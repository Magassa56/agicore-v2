"""Unit tests for StateBuilder — pure deterministic reconstruction."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from agicore.replay.event_store import EventStore, ReplayEventType
from agicore.replay.state_builder import StateBuilder


def _seeded_store() -> EventStore:
    """Returns a store with deterministic timestamps (no datetime.now)."""
    s = EventStore()
    return s


def test_empty_events_returns_empty_state() -> None:
    state = StateBuilder().build([])
    assert state.events_processed == 0
    assert state.positions == {}
    assert state.open_orders == {}
    assert state.closed_orders == []
    assert state.total_realized_pnl == 0.0
    assert state.last_event_sequence == -1
    assert state.last_event_timestamp is None


def test_order_created_only_tracks_open() -> None:
    s = _seeded_store()
    s.append(ReplayEventType.ORDER_CREATED, {
        "order_id": "o-1", "symbol": "ES", "side": "BUY", "quantity": 2.0,
    })
    state = StateBuilder().build(s)
    assert "o-1" in state.open_orders
    assert state.positions == {}


def test_buy_then_fill_opens_position() -> None:
    s = _seeded_store()
    s.append(ReplayEventType.ORDER_CREATED, {
        "order_id": "o-1", "symbol": "ES", "side": "BUY", "quantity": 5.0,
    })
    s.append(ReplayEventType.ORDER_FILLED, {
        "order_id": "o-1", "symbol": "ES", "side": "BUY",
        "quantity": 5.0, "fill_price": 100.0,
    })
    state = StateBuilder().build(s)
    assert "o-1" not in state.open_orders
    assert len(state.closed_orders) == 1
    assert state.closed_orders[0].status == "FILLED"
    pos = state.positions["ES"]
    assert pos.quantity == 5.0
    assert pos.avg_entry_price == 100.0
    assert state.total_realized_pnl == 0.0


def test_buy_then_sell_realizes_pnl() -> None:
    s = _seeded_store()
    s.append(ReplayEventType.ORDER_CREATED,
             {"order_id": "buy", "symbol": "ES", "side": "BUY", "quantity": 4.0})
    s.append(ReplayEventType.ORDER_FILLED,
             {"order_id": "buy", "symbol": "ES", "side": "BUY",
              "quantity": 4.0, "fill_price": 100.0})
    s.append(ReplayEventType.ORDER_CREATED,
             {"order_id": "sell", "symbol": "ES", "side": "SELL", "quantity": 4.0})
    s.append(ReplayEventType.ORDER_FILLED,
             {"order_id": "sell", "symbol": "ES", "side": "SELL",
              "quantity": 4.0, "fill_price": 120.0})
    state = StateBuilder().build(s)
    assert state.positions["ES"].quantity == 0.0
    assert state.realized_pnl_by_symbol["ES"] == pytest.approx(80.0)
    assert state.total_realized_pnl == pytest.approx(80.0)


def test_partial_close_realizes_partial_pnl() -> None:
    s = _seeded_store()
    s.append(ReplayEventType.ORDER_CREATED,
             {"order_id": "buy", "symbol": "ES", "side": "BUY", "quantity": 10.0})
    s.append(ReplayEventType.ORDER_FILLED,
             {"order_id": "buy", "symbol": "ES", "side": "BUY",
              "quantity": 10.0, "fill_price": 100.0})
    s.append(ReplayEventType.ORDER_CREATED,
             {"order_id": "sell", "symbol": "ES", "side": "SELL", "quantity": 4.0})
    s.append(ReplayEventType.ORDER_FILLED,
             {"order_id": "sell", "symbol": "ES", "side": "SELL",
              "quantity": 4.0, "fill_price": 110.0})
    state = StateBuilder().build(s)
    assert state.positions["ES"].quantity == 6.0
    assert state.positions["ES"].avg_entry_price == 100.0  # unchanged on residual
    assert state.realized_pnl_by_symbol["ES"] == pytest.approx(40.0)


def test_two_buys_weighted_average() -> None:
    s = _seeded_store()
    s.append(ReplayEventType.ORDER_CREATED,
             {"order_id": "b1", "symbol": "ES", "side": "BUY", "quantity": 10.0})
    s.append(ReplayEventType.ORDER_FILLED,
             {"order_id": "b1", "symbol": "ES", "side": "BUY",
              "quantity": 10.0, "fill_price": 100.0})
    s.append(ReplayEventType.ORDER_CREATED,
             {"order_id": "b2", "symbol": "ES", "side": "BUY", "quantity": 10.0})
    s.append(ReplayEventType.ORDER_FILLED,
             {"order_id": "b2", "symbol": "ES", "side": "BUY",
              "quantity": 10.0, "fill_price": 110.0})
    state = StateBuilder().build(s)
    assert state.positions["ES"].quantity == 20.0
    assert state.positions["ES"].avg_entry_price == pytest.approx(105.0)


def test_cancel_removes_from_open_orders() -> None:
    s = _seeded_store()
    s.append(ReplayEventType.ORDER_CREATED,
             {"order_id": "o-1", "symbol": "ES", "side": "BUY", "quantity": 1.0})
    s.append(ReplayEventType.ORDER_CANCELLED,
             {"order_id": "o-1", "reason": "user_cancel"})
    state = StateBuilder().build(s)
    assert "o-1" not in state.open_orders
    assert state.closed_orders[0].status == "CANCELLED"


def test_oversell_is_ignored() -> None:
    s = _seeded_store()
    # Fill SELL without prior position
    s.append(ReplayEventType.ORDER_FILLED,
             {"order_id": "x", "symbol": "ES", "side": "SELL",
              "quantity": 1.0, "fill_price": 100.0})
    state = StateBuilder().build(s)
    assert state.positions == {}
    assert state.realized_pnl_by_symbol == {}
    assert any(e["reason"] == "insufficient_position" for e in state.ignored_events)


def test_position_opened_event_alternative() -> None:
    s = _seeded_store()
    s.append(ReplayEventType.POSITION_OPENED,
             {"symbol": "ES", "side": "BUY", "quantity": 3.0, "price": 50.0})
    state = StateBuilder().build(s)
    assert state.positions["ES"].quantity == 3.0
    assert state.positions["ES"].avg_entry_price == 50.0


def test_position_closed_event_alternative() -> None:
    s = _seeded_store()
    s.append(ReplayEventType.POSITION_OPENED,
             {"symbol": "ES", "side": "BUY", "quantity": 3.0, "price": 50.0})
    s.append(ReplayEventType.POSITION_CLOSED,
             {"symbol": "ES", "quantity": 3.0, "price": 60.0})
    state = StateBuilder().build(s)
    assert state.positions["ES"].quantity == 0.0
    assert state.realized_pnl_by_symbol["ES"] == pytest.approx(30.0)


def test_pnl_updated_overwrites() -> None:
    s = _seeded_store()
    s.append(ReplayEventType.PNL_UPDATED, {"symbol": "ES", "realized_pnl": 999.0})
    state = StateBuilder().build(s)
    assert state.realized_pnl_by_symbol["ES"] == 999.0


def test_events_sorted_by_sequence_even_if_passed_unsorted() -> None:
    """Builder must sort events by sequence, not by iteration order."""
    s = _seeded_store()
    s.append(ReplayEventType.ORDER_CREATED,
             {"order_id": "a", "symbol": "ES", "side": "BUY", "quantity": 1.0})
    s.append(ReplayEventType.ORDER_FILLED,
             {"order_id": "a", "symbol": "ES", "side": "BUY",
              "quantity": 1.0, "fill_price": 100.0})

    events = s.get_all()
    reversed_events = list(reversed(events))

    state_normal = StateBuilder().build(events)
    state_reversed = StateBuilder().build(reversed_events)

    assert state_normal == state_reversed


def test_last_event_sequence_and_timestamp_recorded() -> None:
    s = _seeded_store()
    t1 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    t2 = t1 + timedelta(minutes=1)
    s.append(ReplayEventType.PNL_UPDATED, {"symbol": "ES", "realized_pnl": 1.0},
             timestamp=t1)
    s.append(ReplayEventType.PNL_UPDATED, {"symbol": "NQ", "realized_pnl": 2.0},
             timestamp=t2)
    state = StateBuilder().build(s)
    assert state.last_event_sequence == 1
    assert state.last_event_timestamp == t2
    assert state.events_processed == 2
