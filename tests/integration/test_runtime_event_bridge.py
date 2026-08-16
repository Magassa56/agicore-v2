"""Integration test — RuntimeEventBridge wired to a real RuntimeEngine.

End-to-end demonstration : ExecutionAgent runs through the runtime ;
the bridge passively captures the lifecycle events into the EventStore ;
ReplayEngine reconstructs state from the captured log.
"""
from __future__ import annotations

from datetime import timedelta

import pytest

from agicore.agents.execution_agent import (
    EVT_ORDER_PROCESSED,
    TASK_TYPE_ORDER,
    ExecutionAgent,
)
from agicore.core.retry import RetryPolicy
from agicore.l2_memory.schemas.task import TaskCreate
from agicore.l4_planning.runtime import RuntimeEngine
from agicore.l5_action.execution_service import ExecutionService
from tests.l5_secure_helpers import TEST_TIME, make_execution_service, market_payload
from agicore.replay.event_store import EventStore, ReplayEventType
from agicore.replay.replay_engine import ReplayEngine
from agicore.replay.runtime_event_bridge import RuntimeEventBridge


def _build_runtime_with_bridge() -> tuple[
    RuntimeEngine, ExecutionService, EventStore, RuntimeEventBridge
]:
    rt = RuntimeEngine(
        retry_policy=RetryPolicy(max_attempts=1, initial_delay=0, jitter=False),
        poll_interval=0.0,
    )
    svc = make_execution_service()
    rt.register_handler(TASK_TYPE_ORDER, ExecutionAgent(svc, rt.memory, rt.event_bus))

    store = EventStore()
    bridge = RuntimeEventBridge(rt.event_bus, store)
    bridge.attach()
    return rt, svc, store, bridge


def test_bridge_captures_executed_orders_in_order() -> None:
    rt, broker, store, bridge = _build_runtime_with_bridge()
    try:
        rt.submit(TaskCreate(id="ord-1", task_type=TASK_TYPE_ORDER,
                             payload=market_payload("bridge-buy", side="BUY", quantity=4.0, price=100.0)))
        rt.run_once()

        broker.price_provider.set_market_price(
            "ES", 110.0, observed_at=TEST_TIME
        )
        rt.submit(TaskCreate(id="ord-2", task_type=TASK_TYPE_ORDER,
                             payload=market_payload("bridge-sell", side="SELL", quantity=4.0, price=110.0)))
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
                             payload=market_payload("replay-buy", side="BUY", quantity=5.0, price=100.0)))
        rt.run_once()
        broker.price_provider.set_market_price(
            "ES", 120.0, observed_at=TEST_TIME
        )
        rt.submit(TaskCreate(id="ord-2", task_type=TASK_TYPE_ORDER,
                             payload=market_payload("replay-sell", side="SELL", quantity=5.0, price=120.0)))
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


def test_rejected_risk_is_audited_without_phantom_order() -> None:
    rt, broker, store, bridge = _build_runtime_with_bridge()
    try:
        rt.submit(TaskCreate(id="ord-rej", task_type=TASK_TYPE_ORDER,
                             payload=market_payload("bridge-rejected", side="SELL", quantity=5.0)))
        rt.run_once()

        events = store.get_all()
        assert len(events) == 1
        assert events[0].event_type == ReplayEventType.RISK_VIOLATION
        payload = events[0].payload
        assert payload["intent_id"] == "intent-bridge-rejected"
        assert payload["authorization_id"].startswith("risk-auth-")
        assert payload["decision_hash"] and payload["risk_limits_hash"]
        assert payload["provider_id"] == "test-canonical-l5"
        assert payload["context_state_version"] == 0
        assert payload["context_state_hash"]
        assert "INSUFFICIENT_POSITION" in payload["violation_codes"]
        state = ReplayEngine(store).replay()
        assert state.positions == {} and state.total_realized_pnl == 0.0
    finally:
        bridge.detach()
        rt.shutdown()


def test_bridge_does_not_modify_runtime_or_agents() -> None:
    """Bridge attaches as a passive subscriber : the rest of the system
    behaves identically with or without it."""
    rt, broker, store, bridge = _build_runtime_with_bridge()
    try:
        rt.submit(TaskCreate(id="ord-1", task_type=TASK_TYPE_ORDER,
                             payload=market_payload("bridge-passive", side="BUY", quantity=1.0)))
        rt.run_once()
        # The runtime task is still completed normally, MemoryService still
        # has the LTM event, MockBroker still has the position
        assert broker.get_position("ES").quantity == 1.0
        ltm_events = rt.memory.get_recent_events(event_type=EVT_ORDER_PROCESSED)
        assert len(ltm_events) == 1
    finally:
        bridge.detach()
        rt.shutdown()


def test_committed_cancellation_still_has_order_lifecycle_events() -> None:
    rt, _service, store, bridge = _build_runtime_with_bridge()
    try:
        rt.event_bus.emit(
            EVT_ORDER_PROCESSED,
            order_id="order-cancelled",
            symbol="ES",
            side="BUY",
            quantity=1.0,
            order_status="CANCELLED",
            committed=True,
            broker_message="cancelled by explicit transaction",
        )
        events = store.get_all()
        assert [event.event_type for event in events] == [
            ReplayEventType.ORDER_CREATED,
            ReplayEventType.ORDER_CANCELLED,
        ]
    finally:
        bridge.detach()
        rt.shutdown()
