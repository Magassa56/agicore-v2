"""Integration test — RuntimeEventBridge wired to a real RuntimeEngine.

End-to-end demonstration : ExecutionAgent runs through the runtime ;
the bridge passively captures the lifecycle events into the EventStore ;
ReplayEngine reconstructs state from the captured log.
"""
from __future__ import annotations

import pytest

from agicore.agents.execution_agent import (
    EVT_ORDER_PROCESSED,
    TASK_TYPE_ORDER,
    ExecutionAgent,
)
from agicore.core.retry import RetryPolicy
from agicore.l2_memory.schemas.task import TaskCreate
from agicore.l4_planning.runtime import RuntimeEngine
from agicore.l5_action.broker_mock import MockBroker
from agicore.l5_action.execution_service import ExecutionService
from agicore.replay.event_store import EventStore, ReplayEventType
from agicore.replay.replay_engine import ReplayEngine
from agicore.replay.runtime_event_bridge import RuntimeEventBridge


def _build_runtime_with_bridge() -> tuple[
    RuntimeEngine, MockBroker, EventStore, RuntimeEventBridge
]:
    rt = RuntimeEngine(
        retry_policy=RetryPolicy(max_attempts=1, initial_delay=0, jitter=False),
        poll_interval=0.0,
    )
    broker = MockBroker(initial_prices={"ES": 100.0})
    svc = ExecutionService(broker)
    rt.register_handler(TASK_TYPE_ORDER, ExecutionAgent(svc, rt.memory, rt.event_bus))

    store = EventStore()
    bridge = RuntimeEventBridge(rt.event_bus, store)
    bridge.attach()
    return rt, broker, store, bridge


def test_bridge_captures_executed_orders_in_order() -> None:
    rt, broker, store, bridge = _build_runtime_with_bridge()
    try:
        rt.submit(TaskCreate(id="ord-1", task_type=TASK_TYPE_ORDER,
                             payload={"symbol": "ES", "side": "BUY",
                                      "quantity": 4.0}))
        rt.run_once()

        broker.set_market_price("ES", 110.0)
        rt.submit(TaskCreate(id="ord-2", task_type=TASK_TYPE_ORDER,
                             payload={"symbol": "ES", "side": "SELL",
                                      "quantity": 4.0}))
        rt.run_once()

        events = store.get_all()
        # Each FILLED order produces 2 ReplayEvents (Created + Filled)
        assert len(events) == 4
        types = [e.event_type for e in events]
        assert types == [
            ReplayEventType.ORDER_CREATED, ReplayEventType.ORDER_FILLED,
            ReplayEventType.ORDER_CREATED, ReplayEventType.ORDER_FILLED,
        ]
        # Sequences monotone
        seqs = [e.sequence for e in events]
        assert seqs == sorted(seqs)

        # Captured count tracks total replay records
        assert bridge.captured_count == 4
    finally:
        bridge.detach()
        rt.shutdown()


def test_replay_from_bridge_captures_yields_consistent_state() -> None:
    rt, broker, store, bridge = _build_runtime_with_bridge()
    try:
        rt.submit(TaskCreate(id="ord-1", task_type=TASK_TYPE_ORDER,
                             payload={"symbol": "ES", "side": "BUY",
                                      "quantity": 5.0}))
        rt.run_once()
        broker.set_market_price("ES", 120.0)
        rt.submit(TaskCreate(id="ord-2", task_type=TASK_TYPE_ORDER,
                             payload={"symbol": "ES", "side": "SELL",
                                      "quantity": 5.0}))
        rt.run_once()

        engine = ReplayEngine(store)
        state = engine.replay()

        # Long-only round-trip with quantity 5, entry 100, exit 120
        assert state.events_processed == 4
        assert state.positions == {} or state.positions["ES"].quantity == 0.0
        assert state.realized_pnl_by_symbol.get("ES") == pytest.approx(100.0)
        assert state.total_realized_pnl == pytest.approx(100.0)
    finally:
        bridge.detach()
        rt.shutdown()


def test_rejected_order_recorded_as_cancelled_in_replay() -> None:
    rt, broker, store, bridge = _build_runtime_with_bridge()
    try:
        rt.submit(TaskCreate(id="ord-rej", task_type=TASK_TYPE_ORDER,
                             payload={"symbol": "ES", "side": "SELL",
                                      "quantity": 5.0}))  # no position
        rt.run_once()

        events = store.get_all()
        assert len(events) == 2
        assert events[0].event_type == ReplayEventType.ORDER_CREATED
        assert events[1].event_type == ReplayEventType.ORDER_CANCELLED
        assert "insufficient" in events[1].payload["reason"].lower()
    finally:
        bridge.detach()
        rt.shutdown()


def test_bridge_does_not_modify_runtime_or_agents() -> None:
    """Bridge attaches as a passive subscriber : the rest of the system
    behaves identically with or without it."""
    rt, broker, store, bridge = _build_runtime_with_bridge()
    try:
        rt.submit(TaskCreate(id="ord-1", task_type=TASK_TYPE_ORDER,
                             payload={"symbol": "ES", "side": "BUY",
                                      "quantity": 1.0}))
        rt.run_once()
        # The runtime task is still completed normally, MemoryService still
        # has the LTM event, MockBroker still has the position
        assert broker.get_position("ES").quantity == 1.0
        ltm_events = rt.memory.get_recent_events(event_type=EVT_ORDER_PROCESSED)
        assert len(ltm_events) == 1
    finally:
        bridge.detach()
        rt.shutdown()
