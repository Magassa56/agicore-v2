"""MockBroker — deterministic offline broker for safe execution validation.

Long-only. No networking. No async. No external deps.

Fill rules
----------
- MARKET orders : filled immediately at the symbol's last seen price.
                  If no price has been published, the order is REJECTED.
- LIMIT orders  : filled immediately if the current market price has
                  already crossed the limit ; otherwise the order stays
                  PENDING and is filled the moment ``set_market_price``
                  pushes the symbol across the limit.

Position math (long-only)
-------------------------
- BUY                       : opens or adds to a long position. Average
                              entry price is updated as a weighted mean.
- SELL when no/short        : REJECTED (Phase 7C does not support shorts).
- SELL <= position.quantity : reduces position, realizes PnL.
- SELL >  position.quantity : REJECTED (insufficient position).

This mock uses a single ``threading.RLock`` for thread-safety, mirroring
the conventions of Runtime Core.
"""
from __future__ import annotations

import threading
from collections.abc import Iterable
from typing import Any
from uuid import uuid4

import structlog

from .broker_models import (
    Broker,
    ExecutionReport,
    InsufficientPositionError,
    InvalidOrderError,
    Order,
    OrderNotFoundError,
    OrderRequest,
    OrderSide,
    OrderStatus,
    OrderType,
    Position,
    utcnow,
)

logger = structlog.get_logger(__name__)


class MockBroker:
    """Long-only deterministic in-memory broker. Implements ``Broker`` Protocol."""

    NAME: str = "mock_broker"

    def __init__(self, *, initial_prices: dict[str, float] | None = None) -> None:
        self._lock = threading.RLock()
        self._prices: dict[str, float] = dict(initial_prices or {})
        self._orders: dict[str, Order] = {}
        self._positions: dict[str, Position] = {}

    # ------------------------------------------------------------------ Market data
    def set_market_price(self, symbol: str, price: float) -> None:
        """Publish a new market price for ``symbol``. Triggers limit-order fills."""
        if price < 0:
            raise InvalidOrderError("price must be >= 0")
        with self._lock:
            self._prices[symbol] = float(price)
            # Try to fill any pending LIMIT orders that just got crossed
            for order_id, order in list(self._orders.items()):
                if (
                    order.status == OrderStatus.PENDING
                    and order.order_type == OrderType.LIMIT
                    and order.symbol == symbol
                    and self._limit_crossed(order, price)
                ):
                    self._fill_order(order_id, fill_price=price)
        logger.debug("mock_broker.market_price", symbol=symbol, price=price)

    def get_market_price(self, symbol: str) -> float | None:
        with self._lock:
            return self._prices.get(symbol)

    # ------------------------------------------------------------------ Broker API
    def submit_order(self, request: OrderRequest) -> ExecutionReport:
        with self._lock:
            order_id = request.client_order_id or f"ord-{uuid4()}"
            now = utcnow()

            order = Order(
                order_id=order_id,
                client_order_id=request.client_order_id,
                symbol=request.symbol,
                side=request.side,
                quantity=request.quantity,
                order_type=request.order_type,
                limit_price=request.limit_price,
                status=OrderStatus.PENDING,
                created_at=now,
            )
            self._orders[order_id] = order
            logger.info(
                "mock_broker.order_submitted",
                order_id=order_id,
                symbol=request.symbol,
                side=request.side.value,
                qty=request.quantity,
                type=request.order_type.value,
                limit=request.limit_price,
            )

            # Validate side against position (long-only)
            if request.side == OrderSide.SELL:
                pos = self._positions.get(request.symbol)
                available = pos.quantity if pos else 0.0
                if available <= 0 or request.quantity > available:
                    return self._reject(
                        order_id,
                        f"insufficient position for SELL: have={available}, want={request.quantity}",
                    )

            # MARKET : fill immediately at last price
            if request.order_type == OrderType.MARKET:
                price = self._prices.get(request.symbol)
                if price is None:
                    return self._reject(
                        order_id,
                        f"no market price for symbol={request.symbol!r}",
                    )
                return self._fill_order(order_id, fill_price=price)

            # LIMIT : fill if already crossed, else stay PENDING
            current = self._prices.get(request.symbol)
            if current is not None and self._limit_crossed(self._orders[order_id], current):
                return self._fill_order(order_id, fill_price=current)

            return ExecutionReport(
                order_id=order_id,
                status=OrderStatus.PENDING,
                timestamp=now,
                message="limit order resting",
            )

    def cancel_order(self, order_id: str) -> ExecutionReport:
        with self._lock:
            order = self._orders.get(order_id)
            if order is None:
                raise OrderNotFoundError(f"unknown order_id={order_id!r}")
            if order.status != OrderStatus.PENDING:
                return ExecutionReport(
                    order_id=order_id,
                    status=order.status,
                    timestamp=utcnow(),
                    message=f"cannot cancel order in status {order.status.value}",
                )
            now = utcnow()
            cancelled = order.model_copy(
                update={"status": OrderStatus.CANCELLED, "cancelled_at": now}
            )
            self._orders[order_id] = cancelled
            logger.info("mock_broker.order_cancelled", order_id=order_id)
            return ExecutionReport(
                order_id=order_id,
                status=OrderStatus.CANCELLED,
                timestamp=now,
                message="cancelled",
            )

    def get_position(self, symbol: str) -> Position | None:
        with self._lock:
            return self._positions.get(symbol)

    def get_open_orders(self) -> list[Order]:
        with self._lock:
            return [
                o for o in self._orders.values()
                if o.status == OrderStatus.PENDING
            ]

    # ------------------------------------------------------------------ Inspection
    def get_order(self, order_id: str) -> Order | None:
        with self._lock:
            return self._orders.get(order_id)

    def get_all_orders(self) -> list[Order]:
        with self._lock:
            return list(self._orders.values())

    def reset(self) -> None:
        """Clear all state. Useful between tests."""
        with self._lock:
            self._prices.clear()
            self._orders.clear()
            self._positions.clear()

    # ------------------------------------------------------------------ Internals
    @staticmethod
    def _limit_crossed(order: Order, current_price: float) -> bool:
        if order.limit_price is None:
            return False
        if order.side == OrderSide.BUY:
            return current_price <= order.limit_price
        return current_price >= order.limit_price

    def _fill_order(self, order_id: str, *, fill_price: float) -> ExecutionReport:
        order = self._orders[order_id]
        # Re-check long-only invariants for SELL just before fill
        if order.side == OrderSide.SELL:
            pos = self._positions.get(order.symbol)
            available = pos.quantity if pos else 0.0
            if available <= 0 or order.quantity > available:
                return self._reject(
                    order_id,
                    f"insufficient position at fill time: have={available}, want={order.quantity}",
                )

        now = utcnow()
        filled = order.model_copy(
            update={
                "status": OrderStatus.FILLED,
                "filled_price": fill_price,
                "filled_quantity": order.quantity,
                "filled_at": now,
            }
        )
        self._orders[order_id] = filled
        self._apply_fill_to_position(filled, fill_price=fill_price, ts=now)

        logger.info(
            "mock_broker.order_filled",
            order_id=order_id,
            symbol=filled.symbol,
            side=filled.side.value,
            qty=filled.quantity,
            price=fill_price,
        )
        return ExecutionReport(
            order_id=order_id,
            status=OrderStatus.FILLED,
            filled_price=fill_price,
            filled_quantity=filled.quantity,
            timestamp=now,
            message="filled",
        )

    def _reject(self, order_id: str, reason: str) -> ExecutionReport:
        order = self._orders[order_id]
        now = utcnow()
        rejected = order.model_copy(
            update={"status": OrderStatus.REJECTED, "rejected_reason": reason}
        )
        self._orders[order_id] = rejected
        logger.warning(
            "mock_broker.order_rejected", order_id=order_id, reason=reason
        )
        return ExecutionReport(
            order_id=order_id,
            status=OrderStatus.REJECTED,
            timestamp=now,
            message=reason,
        )

    def _apply_fill_to_position(
        self, order: Order, *, fill_price: float, ts: Any
    ) -> None:
        sym = order.symbol
        pos = self._positions.get(sym)
        existing_realized = pos.realized_pnl if pos else 0.0

        if order.side == OrderSide.BUY:
            if pos is None or pos.quantity == 0:
                self._positions[sym] = Position(
                    symbol=sym,
                    quantity=order.quantity,
                    avg_entry_price=fill_price,
                    realized_pnl=existing_realized,
                    last_update=ts,
                )
            else:
                total_qty = pos.quantity + order.quantity
                new_avg = (
                    pos.quantity * pos.avg_entry_price
                    + order.quantity * fill_price
                ) / total_qty
                self._positions[sym] = Position(
                    symbol=sym,
                    quantity=total_qty,
                    avg_entry_price=new_avg,
                    realized_pnl=pos.realized_pnl,
                    last_update=ts,
                )
            return

        # SELL — guarded by submit/fill gates above
        assert pos is not None and pos.quantity >= order.quantity
        realized = pos.realized_pnl + (fill_price - pos.avg_entry_price) * order.quantity
        new_qty = pos.quantity - order.quantity
        self._positions[sym] = Position(
            symbol=sym,
            quantity=new_qty,
            avg_entry_price=pos.avg_entry_price if new_qty > 0 else 0.0,
            realized_pnl=realized,
            last_update=ts,
        )


# Sanity check that MockBroker satisfies the Broker Protocol.
_: Broker = MockBroker()


__all__ = ["MockBroker"]
