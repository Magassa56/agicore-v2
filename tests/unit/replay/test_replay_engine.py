"""Unit tests for ReplayEngine — determinism + time-bounded replay."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from agicore.replay.event_store import EventStore, ReplayEventType
from agicore.replay.replay_engine import ReplayEngine


def _populate(s: EventStore) -> None:
    base = datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)
    s.append(ReplayEventType.ORDER_CREATED,
             {"order_id": "buy", "symbol": "ES", "side": "BUY", "quantity": 5.0},
             timestamp=base)
    s.append(ReplayEventType.ORDER_FILLED,
             {"order_id": "buy", "symbol": "ES", "side": "BUY",
              "quantity": 5.0, "fill_price": 100.0},
             timestamp=base + timedelta(seconds=1))
    s.append(ReplayEventType.ORDER_CREATED,
             {"order_id": "sell", "symbol": "ES", "side": "SELL", "quantity": 5.0},
             timestamp=base + timedelta(seconds=2))
    s.append(ReplayEventType.ORDER_FILLED,
             {"order_id": "sell", "symbol": "ES", "side": "SELL",
              "quantity": 5.0, "fill_price": 110.0},
             timestamp=base + timedelta(seconds=3))


def test_replay_returns_consistent_state() -> None:
    s = EventStore()
    _populate(s)
    engine = ReplayEngine(s)
    state = engine.replay()
    assert state.events_processed == 4
    assert state.realized_pnl_by_symbol["ES"] == pytest.approx(50.0)


def test_replay_until_yields_intermediate_state() -> None:
    s = EventStore()
    _populate(s)
    engine = ReplayEngine(s)

    base = datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)
    # After only the first BUY fill : position open, no PnL yet
    state_mid = engine.replay_until(base + timedelta(seconds=1))
    assert state_mid.events_processed == 2
    assert state_mid.positions["ES"].quantity == 5.0
    assert state_mid.total_realized_pnl == 0.0


def test_replay_in_range() -> None:
    s = EventStore()
    _populate(s)
    engine = ReplayEngine(s)

    base = datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)
    # Only the SELL leg
    state = engine.replay_in_range(start=base + timedelta(seconds=2))
    assert state.events_processed == 2
    # Only SELL events → no prior BUY fill → SELL is ignored
    assert state.positions == {}


def test_is_deterministic_true_for_consistent_log() -> None:
    s = EventStore()
    _populate(s)
    engine = ReplayEngine(s)
    assert engine.is_deterministic(n_runs=5) is True


def test_is_deterministic_requires_at_least_two_runs() -> None:
    s = EventStore()
    engine = ReplayEngine(s)
    with pytest.raises(ValueError):
        engine.is_deterministic(n_runs=1)


def test_replay_after_clear_returns_empty_state() -> None:
    s = EventStore()
    _populate(s)
    engine = ReplayEngine(s)
    s.clear()
    state = engine.replay()
    assert state.events_processed == 0
    assert state.positions == {}


def test_engine_exposes_components() -> None:
    s = EventStore()
    engine = ReplayEngine(s)
    assert engine.store is s
    assert engine.builder is not None
