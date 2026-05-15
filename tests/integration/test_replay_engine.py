"""Integration tests — full replay scenarios.

Validates the Phase 7E core invariant : State_t = f(Events_0..t).
Same input events → identical output state across multiple runs and
across modes of construction.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from agicore.replay.event_store import EventStore, ReplayEventType
from agicore.replay.replay_engine import ReplayEngine
from agicore.replay.state_builder import StateBuilder


def _scenario_buy_sell_replay() -> EventStore:
    s = EventStore()
    base = datetime(2026, 1, 1, 9, 30, tzinfo=timezone.utc)

    # Buy 10 @ 100
    s.append(ReplayEventType.ORDER_CREATED,
             {"order_id": "ord-1", "symbol": "ES", "side": "BUY", "quantity": 10.0},
             timestamp=base)
    s.append(ReplayEventType.ORDER_FILLED,
             {"order_id": "ord-1", "symbol": "ES", "side": "BUY",
              "quantity": 10.0, "fill_price": 100.0},
             timestamp=base + timedelta(seconds=1))

    # Partial close 4 @ 105
    s.append(ReplayEventType.ORDER_CREATED,
             {"order_id": "ord-2", "symbol": "ES", "side": "SELL", "quantity": 4.0},
             timestamp=base + timedelta(seconds=10))
    s.append(ReplayEventType.ORDER_FILLED,
             {"order_id": "ord-2", "symbol": "ES", "side": "SELL",
              "quantity": 4.0, "fill_price": 105.0},
             timestamp=base + timedelta(seconds=11))

    # Final close 6 @ 120
    s.append(ReplayEventType.ORDER_CREATED,
             {"order_id": "ord-3", "symbol": "ES", "side": "SELL", "quantity": 6.0},
             timestamp=base + timedelta(seconds=20))
    s.append(ReplayEventType.ORDER_FILLED,
             {"order_id": "ord-3", "symbol": "ES", "side": "SELL",
              "quantity": 6.0, "fill_price": 120.0},
             timestamp=base + timedelta(seconds=21))

    return s


def test_full_buy_sell_scenario_pnl() -> None:
    """Replay reproduit le PnL exact attendu par calcul direct."""
    store = _scenario_buy_sell_replay()
    engine = ReplayEngine(store)
    state = engine.replay()

    # PnL attendu = (105-100)*4 + (120-100)*6 = 20 + 120 = 140
    assert state.realized_pnl_by_symbol["ES"] == pytest.approx(140.0)
    assert state.total_realized_pnl == pytest.approx(140.0)
    assert state.positions["ES"].quantity == 0.0
    assert state.events_processed == 6


def test_replay_is_idempotent_across_n_runs() -> None:
    """Réexécuter replay() N fois produit exactement le même état."""
    store = _scenario_buy_sell_replay()
    engine = ReplayEngine(store)

    states = [engine.replay() for _ in range(10)]
    first = states[0]
    for s in states[1:]:
        assert s == first

    # is_deterministic doit confirmer
    assert engine.is_deterministic(n_runs=5) is True


def test_replay_state_does_not_mutate_store() -> None:
    """La reconstruction ne doit jamais modifier le journal."""
    store = _scenario_buy_sell_replay()
    initial_count = store.count()
    initial_snapshot = [e.event_id for e in store.get_all()]

    engine = ReplayEngine(store)
    engine.replay()
    engine.replay()
    engine.replay()

    assert store.count() == initial_count
    assert [e.event_id for e in store.get_all()] == initial_snapshot


def test_replay_until_each_step_matches_progression() -> None:
    """Chaque cutoff temporel doit donner un état cohérent du sous-log."""
    store = _scenario_buy_sell_replay()
    engine = ReplayEngine(store)

    base = datetime(2026, 1, 1, 9, 30, tzinfo=timezone.utc)

    # Après le premier BUY fill : pos 10, PnL 0
    s1 = engine.replay_until(base + timedelta(seconds=1))
    assert s1.positions["ES"].quantity == 10.0
    assert s1.total_realized_pnl == 0.0

    # Après la partial close : pos 6, PnL 20
    s2 = engine.replay_until(base + timedelta(seconds=11))
    assert s2.positions["ES"].quantity == 6.0
    assert s2.realized_pnl_by_symbol["ES"] == pytest.approx(20.0)

    # Final : pos 0, PnL 140
    s3 = engine.replay_until(base + timedelta(seconds=21))
    assert s3.positions["ES"].quantity == 0.0
    assert s3.realized_pnl_by_symbol["ES"] == pytest.approx(140.0)


def test_replay_independent_of_builder_instance() -> None:
    """Deux builders différents produisent le même état pour le même log."""
    store = _scenario_buy_sell_replay()
    s_a = ReplayEngine(store, StateBuilder()).replay()
    s_b = ReplayEngine(store, StateBuilder()).replay()
    assert s_a == s_b


def test_replay_full_chain_with_pnl_audit_event() -> None:
    """Un PnLUpdated audit event écrase le PnL recalculé pour audit."""
    store = _scenario_buy_sell_replay()
    # Audit override
    store.append(ReplayEventType.PNL_UPDATED,
                 {"symbol": "ES", "realized_pnl": 999.0})
    engine = ReplayEngine(store)
    state = engine.replay()
    assert state.realized_pnl_by_symbol["ES"] == 999.0
    # Mais la position reconstruite reste cohérente (PnL audit n'altère pas
    # la position)
    assert state.positions["ES"].quantity == 0.0
