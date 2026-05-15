"""ExecutionService — high-level façade over any ``Broker`` implementation.

Repository-compatible design : the service delegates persistence/state to
the broker and adds a thin layer of structured logging and convenience
methods. Future NinjaTrader and Alpaca adapters plug in via the same
``Broker`` Protocol.
"""
from __future__ import annotations

import structlog

from .broker_models import (
    Broker,
    ExecutionReport,
    Order,
    OrderRequest,
    OrderSide,
    OrderType,
    Position,
)

logger = structlog.get_logger(__name__)


class ExecutionService:
    """Front-end API for any ``Broker`` adapter.

    Parameters
    ----------
    broker : Broker
        Required. Any object satisfying the ``Broker`` Protocol from
        ``broker_models``. In Phase 7C, ``MockBroker``. In future phases,
        a real adapter (NinjaTrader, Alpaca) plugged in here unchanged.
    """

    def __init__(self, broker: Broker) -> None:
        self._broker = broker

    @property
    def broker(self) -> Broker:
        return self._broker

    # ------------------------------------------------------------------ Submit
    def submit_market_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        *,
        client_order_id: str | None = None,
    ) -> ExecutionReport:
        request = OrderRequest(
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=OrderType.MARKET,
            client_order_id=client_order_id,
        )
        logger.info(
            "execution_service.submit_market",
            symbol=symbol, side=side.value, quantity=quantity,
        )
        return self._broker.submit_order(request)

    def submit_limit_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        limit_price: float,
        *,
        client_order_id: str | None = None,
    ) -> ExecutionReport:
        request = OrderRequest(
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=OrderType.LIMIT,
            limit_price=limit_price,
            client_order_id=client_order_id,
        )
        logger.info(
            "execution_service.submit_limit",
            symbol=symbol, side=side.value, quantity=quantity, limit=limit_price,
        )
        return self._broker.submit_order(request)

    def submit(self, request: OrderRequest) -> ExecutionReport:
        """Pass-through for arbitrary order requests."""
        return self._broker.submit_order(request)

    # ------------------------------------------------------------------ Cancel / inspect
    def cancel(self, order_id: str) -> ExecutionReport:
        logger.info("execution_service.cancel", order_id=order_id)
        return self._broker.cancel_order(order_id)

    def get_position(self, symbol: str) -> Position | None:
        return self._broker.get_position(symbol)

    def get_open_orders(self) -> list[Order]:
        return self._broker.get_open_orders()


__all__ = ["ExecutionService"]
