"""StateBuilder — pure, deterministic state reconstruction from events.

Single responsibility : given an iterable of ``ReplayEvent``, return a
``ReplayState`` that is the sole truth at the last event's point in time.

Invariants
----------
- 100 % deterministic : same input events → identical output state.
- Stateless : the builder holds no instance state. ``build`` is a pure
  function in everything but its method-syntax wrapping.
- Long-only : matches the broker-mock semantics (Phase 7C). SELLs require
  a sufficient long position ; oversells are recorded as ``ignored`` and
  do not affect computed PnL.
- Realized PnL is ALWAYS recomputed from the event log. ``PnLUpdated``
  events serve as audit checkpoints — they overwrite the running tally
  for the symbol they reference.
"""
from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Any

import structlog
from pydantic import BaseModel, ConfigDict, Field

from .event_store import ReplayEvent, ReplayEventType

logger = structlog.get_logger(__name__)


# ============================================================================
# Output state model
# ============================================================================
class ReplayPosition(BaseModel):
    model_config = ConfigDict(frozen=True)
    symbol: str
    quantity: float = Field(..., ge=0)
    avg_entry_price: float = Field(..., ge=0)


class ReplayClosedOrder(BaseModel):
    model_config = ConfigDict(frozen=True)
    order_id: str
    status: str           # FILLED | CANCELLED
    symbol: str
    side: str
    quantity: float
    fill_price: float | None = None
    timestamp: datetime
    sequence: int


class ReplayState(BaseModel):
    """Deterministic snapshot rebuilt from the event log."""
    model_config = ConfigDict(frozen=True)

    positions: dict[str, ReplayPosition]
    open_orders: dict[str, dict[str, Any]]
    closed_orders: list[ReplayClosedOrder]
    realized_pnl_by_symbol: dict[str, float]
    total_realized_pnl: float
    events_processed: int
    last_event_sequence: int
    last_event_timestamp: datetime | None
    ignored_events: list[dict[str, Any]] = Field(default_factory=list)


# ============================================================================
# StateBuilder
# ============================================================================
class StateBuilder:
    """Pure stateless reconstructor."""

    def build(self, events: Iterable[ReplayEvent]) -> ReplayState:
        # Mutable working dicts — never exposed
        positions: dict[str, dict[str, float]] = {}
        open_orders: dict[str, dict[str, Any]] = {}
        closed_orders: list[ReplayClosedOrder] = []
        realized: dict[str, float] = {}
        ignored: list[dict[str, Any]] = []

        # Sort by sequence to guarantee deterministic order even if the
        # caller passes events out of order
        sorted_events = sorted(events, key=lambda e: e.sequence)

        last_seq = -1
        last_ts: datetime | None = None
        n = 0

        for event in sorted_events:
            self._apply(
                event,
                positions=positions,
                open_orders=open_orders,
                closed_orders=closed_orders,
                realized=realized,
                ignored=ignored,
            )
            last_seq = event.sequence
            last_ts = event.timestamp
            n += 1

        return ReplayState(
            positions={
                s: ReplayPosition(
                    symbol=s,
                    quantity=p["quantity"],
                    avg_entry_price=p["avg_entry_price"] if p["quantity"] > 0 else 0.0,
                )
                for s, p in positions.items()
                if p["quantity"] >= 0  # long-only invariant
            },
            open_orders=dict(open_orders),
            closed_orders=closed_orders,
            realized_pnl_by_symbol=dict(realized),
            total_realized_pnl=sum(realized.values()),
            events_processed=n,
            last_event_sequence=last_seq,
            last_event_timestamp=last_ts,
            ignored_events=ignored,
        )

    # ------------------------------------------------------------------ Apply
    def _apply(
        self,
        event: ReplayEvent,
        *,
        positions: dict[str, dict[str, float]],
        open_orders: dict[str, dict[str, Any]],
        closed_orders: list[ReplayClosedOrder],
        realized: dict[str, float],
        ignored: list[dict[str, Any]],
    ) -> None:
        et = event.event_type
        p = event.payload

        if et == ReplayEventType.ORDER_CREATED:
            order_id = str(p["order_id"])
            open_orders[order_id] = {
                "order_id": order_id,
                "symbol": p["symbol"],
                "side": p["side"],
                "quantity": float(p["quantity"]),
                "order_type": p.get("order_type", "MARKET"),
                "limit_price": p.get("limit_price"),
                "created_sequence": event.sequence,
            }
            return

        if et == ReplayEventType.ORDER_CANCELLED:
            order_id = str(p["order_id"])
            order = open_orders.pop(order_id, None)
            if order is None:
                ignored.append({
                    "reason": "cancel_unknown_order",
                    "event_id": event.event_id,
                    "order_id": order_id,
                })
                return
            closed_orders.append(ReplayClosedOrder(
                order_id=order_id,
                status="CANCELLED",
                symbol=order["symbol"],
                side=order["side"],
                quantity=order["quantity"],
                fill_price=None,
                timestamp=event.timestamp,
                sequence=event.sequence,
            ))
            return

        if et == ReplayEventType.ORDER_FILLED:
            order_id = str(p["order_id"])
            order = open_orders.pop(order_id, None)
            symbol = p.get("symbol") or (order["symbol"] if order else None)
            side = p.get("side") or (order["side"] if order else None)
            qty = float(p.get("quantity") or p.get("fill_quantity") or
                        (order["quantity"] if order else 0.0))
            fill_price = float(p["fill_price"])
            if not symbol or side not in ("BUY", "SELL") or qty <= 0:
                ignored.append({
                    "reason": "fill_invalid_payload",
                    "event_id": event.event_id,
                })
                return
            applied = self._apply_fill(positions, realized, symbol, side, qty, fill_price)
            if not applied:
                ignored.append({
                    "reason": "insufficient_position",
                    "event_id": event.event_id,
                    "order_id": order_id,
                })
                # Nevertheless track the closed order for audit
            closed_orders.append(ReplayClosedOrder(
                order_id=order_id,
                status="FILLED" if applied else "REJECTED",
                symbol=symbol,
                side=side,
                quantity=qty,
                fill_price=fill_price,
                timestamp=event.timestamp,
                sequence=event.sequence,
            ))
            return

        if et == ReplayEventType.POSITION_OPENED:
            symbol = p["symbol"]
            side = p.get("side", "BUY")
            qty = float(p["quantity"])
            price = float(p["price"])
            if side != "BUY" or qty <= 0:
                ignored.append({
                    "reason": "position_opened_invalid",
                    "event_id": event.event_id,
                })
                return
            self._apply_fill(positions, realized, symbol, "BUY", qty, price)
            return

        if et == ReplayEventType.POSITION_CLOSED:
            symbol = p["symbol"]
            qty = float(p["quantity"])
            price = float(p["price"])
            if qty <= 0:
                ignored.append({
                    "reason": "position_closed_invalid_qty",
                    "event_id": event.event_id,
                })
                return
            applied = self._apply_fill(positions, realized, symbol, "SELL", qty, price)
            if not applied:
                ignored.append({
                    "reason": "position_closed_insufficient",
                    "event_id": event.event_id,
                })
            return

        if et == ReplayEventType.MARKET_TICK:
            # Observation event — does not affect order/position state.
            # Recorded in the log but explicitly a no-op for state.
            return

        if et == ReplayEventType.RISK_VIOLATION:
            # Observation event — risk gate decisions do not alter state.
            return

        if et == ReplayEventType.PNL_UPDATED:
            symbol = p["symbol"]
            realized[symbol] = float(p["realized_pnl"])
            return

        # Unknown — should never hit because Pydantic restricts the enum
        ignored.append({
            "reason": "unknown_event_type",
            "event_id": event.event_id,
            "event_type": str(et),
        })

    # ------------------------------------------------------------------ Long-only fill
    @staticmethod
    def _apply_fill(
        positions: dict[str, dict[str, float]],
        realized: dict[str, float],
        symbol: str,
        side: str,
        quantity: float,
        price: float,
    ) -> bool:
        """Apply a long-only fill. Returns True if applied, False if ignored."""
        pos = positions.get(symbol, {"quantity": 0.0, "avg_entry_price": 0.0})

        if side == "BUY":
            if pos["quantity"] == 0.0:
                positions[symbol] = {"quantity": quantity, "avg_entry_price": price}
            else:
                total = pos["quantity"] + quantity
                new_avg = (
                    pos["quantity"] * pos["avg_entry_price"]
                    + quantity * price
                ) / total
                positions[symbol] = {"quantity": total, "avg_entry_price": new_avg}
            return True

        # SELL — long-only
        if pos["quantity"] <= 0 or quantity > pos["quantity"]:
            return False

        # Realize PnL on the qty being closed
        delta = (price - pos["avg_entry_price"]) * quantity
        realized[symbol] = realized.get(symbol, 0.0) + delta

        new_qty = pos["quantity"] - quantity
        positions[symbol] = {
            "quantity": new_qty,
            "avg_entry_price": pos["avg_entry_price"] if new_qty > 0 else 0.0,
        }
        return True


__all__ = ["StateBuilder", "ReplayState", "ReplayPosition", "ReplayClosedOrder"]
