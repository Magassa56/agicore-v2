"""Integration tests — MockMarketFeed wired to RuntimeEngine + Replay layer.

Validates Phase 8A success criteria :
- ticks flow on the Runtime EventBus
- runtime stays alive
- feed shuts down cleanly
- replay-compatible : ticks captured via custom translator are stored as
  MARKET_TICK ReplayEvents, but do NOT alter order/position state
"""
from __future__ import annotations

import threading
import time

import pytest

from agicore.agents.execution_agent import (
    EVT_ORDER_PROCESSED,
    TASK_TYPE_ORDER,
    ExecutionAgent,
)
from agicore.core.events import Event, EventBus
from agicore.core.retry import RetryPolicy
from agicore.l1_perception.market_models import EVT_MARKET_TICK
from agicore.l1_perception.mock_market_feed import MockMarketFeed
from agicore.l2_memory.schemas.task import TaskCreate
from agicore.l4_planning.runtime import RuntimeEngine
from agicore.l5_action.broker_mock import MockBroker
from agicore.l5_action.execution_service import ExecutionService
from agicore.replay.event_store import EventStore, ReplayEventType
from agicore.replay.replay_engine import ReplayEngine
from agicore.replay.runtime_event_bridge import RuntimeEventBridge


def test_feed_emits_ticks_into_runtime_bus() -> None:
    """Le feed produit des ticks visibles par n'importe quel subscriber bus."""
    rt = RuntimeEngine(poll_interval=0.5)
    received: list = []
    rt.subscribe(EVT_MARKET_TICK, lambda ev: received.append(ev))

    feed = MockMarketFeed(
        rt.event_bus, "ES",
        tick_interval_s=0.02, poll_resolution_s=0.01, max_ticks=5,
    )
    try:
        feed.start()
        time.sleep(0.3)
        feed.stop()
    finally:
        rt.shutdown()

    assert len(received) == 5
    # Ordering monotone
    seqs = [ev.payload["sequence"] for ev in received]
    assert seqs == list(range(5))


def test_feed_does_not_disturb_execution_pipeline() -> None:
    """Le feed et l'ExecutionAgent coexistent sans interférer."""
    rt = RuntimeEngine(
        retry_policy=RetryPolicy(max_attempts=1, initial_delay=0, jitter=False),
        poll_interval=0.0,
    )
    broker = MockBroker(initial_prices={"ES": 100.0})
    rt.register_handler(
        TASK_TYPE_ORDER,
        ExecutionAgent(ExecutionService(broker), rt.memory, rt.event_bus),
    )

    feed = MockMarketFeed(
        rt.event_bus, "ES",
        tick_interval_s=0.02, poll_resolution_s=0.01, max_ticks=5,
    )
    try:
        feed.start()

        rt.submit(TaskCreate(id="ord-1", task_type=TASK_TYPE_ORDER,
                             payload={"symbol": "ES", "side": "BUY",
                                      "quantity": 1.0}))
        time.sleep(0.05)
        rt.run_once()
        feed.stop()

        assert broker.get_position("ES").quantity == 1.0
        # Pipeline d'exécution OK : LTM event présent
        ltm = rt.memory.get_recent_events(event_type=EVT_ORDER_PROCESSED)
        assert len(ltm) == 1
    finally:
        rt.shutdown()


def test_replay_compatible_via_custom_bridge_translator() -> None:
    """Un translator personnalisé capture les ticks dans EventStore comme
    MARKET_TICK. La reconstruction d'état n'en est pas affectée."""
    rt = RuntimeEngine(poll_interval=0.5)
    store = EventStore()
    bridge = RuntimeEventBridge(rt.event_bus, store)

    def market_tick_translator(event: Event):
        p = event.payload
        return [(ReplayEventType.MARKET_TICK, {
            "symbol": p["symbol"],
            "price": p["price"],
            "bid": p["bid"],
            "ask": p["ask"],
            "volume": p.get("volume", 0.0),
        })]

    bridge.register_translator(EVT_MARKET_TICK, market_tick_translator)
    bridge.attach()

    feed = MockMarketFeed(
        rt.event_bus, "ES",
        tick_interval_s=0.02, poll_resolution_s=0.01, max_ticks=4,
    )
    try:
        feed.start()
        time.sleep(0.3)
        feed.stop()
    finally:
        bridge.detach()
        rt.shutdown()

    # Ticks bien capturés en MARKET_TICK
    captured = store.get_by_type(ReplayEventType.MARKET_TICK)
    assert len(captured) == 4
    # Sequences monotones côté store
    seqs = [e.sequence for e in captured]
    assert seqs == sorted(seqs)
    # Replay : aucun effet sur les positions / PnL (no-op explicite)
    state = ReplayEngine(store).replay()
    assert state.positions == {}
    assert state.realized_pnl_by_symbol == {}
    assert state.events_processed == 4
    # MARKET_TICK ne doit PAS être dans ignored_events (no-op explicite)
    assert all(e["reason"] != "unknown_event_type"
               for e in state.ignored_events)


def test_replay_combined_market_ticks_and_orders() -> None:
    """Ticks + ordres d'exécution dans le même log : ordres affectent
    le state, ticks sont des observations."""
    rt = RuntimeEngine(
        retry_policy=RetryPolicy(max_attempts=1, initial_delay=0, jitter=False),
        poll_interval=0.0,
    )
    broker = MockBroker(initial_prices={"ES": 100.0})
    rt.register_handler(
        TASK_TYPE_ORDER,
        ExecutionAgent(ExecutionService(broker), rt.memory, rt.event_bus),
    )

    store = EventStore()
    bridge = RuntimeEventBridge(rt.event_bus, store)

    def market_tick_translator(event: Event):
        p = event.payload
        return [(ReplayEventType.MARKET_TICK, {
            "symbol": p["symbol"], "price": p["price"],
            "bid": p["bid"], "ask": p["ask"],
        })]

    bridge.register_translator(EVT_MARKET_TICK, market_tick_translator)
    bridge.attach()

    feed = MockMarketFeed(
        rt.event_bus, "ES",
        tick_interval_s=0.02, poll_resolution_s=0.01, max_ticks=3,
    )
    try:
        feed.start()
        time.sleep(0.05)

        # BUY then SELL pendant que le feed tourne
        rt.submit(TaskCreate(id="b1", task_type=TASK_TYPE_ORDER,
                             payload={"symbol": "ES", "side": "BUY",
                                      "quantity": 2.0}))
        rt.run_once()
        broker.set_market_price("ES", 110.0)
        rt.submit(TaskCreate(id="s1", task_type=TASK_TYPE_ORDER,
                             payload={"symbol": "ES", "side": "SELL",
                                      "quantity": 2.0}))
        rt.run_once()

        feed.stop()
    finally:
        bridge.detach()
        rt.shutdown()

    # EventStore contient ticks + ordres mélangés
    market_ticks = store.get_by_type(ReplayEventType.MARKET_TICK)
    order_filled = store.get_by_type(ReplayEventType.ORDER_FILLED)
    assert len(market_ticks) == 3
    assert len(order_filled) == 2

    # Replay : seuls les ordres affectent le state
    state = ReplayEngine(store).replay()
    assert state.realized_pnl_by_symbol.get("ES") == pytest.approx(20.0)
    assert state.positions == {} or state.positions["ES"].quantity == 0.0


def test_feed_graceful_shutdown_no_leftover_thread() -> None:
    rt = RuntimeEngine(poll_interval=0.5)
    feed = MockMarketFeed(
        rt.event_bus, "ES",
        tick_interval_s=0.02, poll_resolution_s=0.01,
    )
    try:
        feed.start()
        time.sleep(0.05)
        feed.stop()
    finally:
        rt.shutdown()
    alive = [t for t in threading.enumerate()
             if t.name.startswith("mock-market-feed:") and t.is_alive()]
    assert alive == []
