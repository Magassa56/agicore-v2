"""Integration test — ExecutionAgent through the full Runtime Engine pipeline.

Validates that AGIcore can orchestrate a complete simulated execution
workflow safely. Fully offline — uses MockBroker.
"""
from __future__ import annotations

import pytest

from agicore.agents.execution_agent import (
    AGENT_ID,
    EVT_ORDER_PROCESSED,
    TASK_TYPE_ORDER,
    ExecutionAgent,
)
from agicore.core.events import (
    EVT_TASK_COMPLETED,
    EVT_TASK_CREATED,
    EVT_TASK_FAILED,
    EVT_TASK_STARTED,
)
from agicore.core.retry import RetryPolicy
from agicore.l2_memory.repositories.task_repository import TaskRepository
from agicore.l2_memory.schemas.task import TaskCreate
from agicore.l4_planning.runtime import RuntimeEngine
from agicore.l5_action.broker_mock import MockBroker
from agicore.l5_action.execution_service import ExecutionService


def test_execution_agent_full_runtime_pipeline() -> None:
    """receive → enqueue → dispatch → execute → log → persist → feedback."""
    rt = RuntimeEngine(
        retry_policy=RetryPolicy(max_attempts=1, initial_delay=0, jitter=False),
        poll_interval=0.0,
    )
    broker = MockBroker(initial_prices={"ES": 100.0})
    svc = ExecutionService(broker)
    agent = ExecutionAgent(svc, rt.memory, rt.event_bus)
    rt.register_handler(TASK_TYPE_ORDER, agent)

    seen: list[str] = []
    rt.subscribe("*", lambda ev: seen.append(ev.event_type))

    try:
        # 1. Submit BUY 5 @ market
        rt.submit(TaskCreate(
            id="ord-buy-1",
            task_type=TASK_TYPE_ORDER,
            payload={"symbol": "ES", "side": "BUY", "quantity": 5.0},
        ))
        executed = rt.run_once()
        assert executed == 1

        with rt.orchestrator._engine.session() as s:  # type: ignore[attr-defined]
            t = TaskRepository(s).get("ord-buy-1")
        assert t is not None
        assert t.status == "completed"
        assert t.result is not None
        assert t.result["order_status"] == "FILLED"
        assert t.result["fill_price"] == 100.0
        assert t.result["agent_id"] == AGENT_ID

        # 2. Move price → submit SELL 5 → realized PnL
        broker.set_market_price("ES", 115.0)
        rt.submit(TaskCreate(
            id="ord-sell-1",
            task_type=TASK_TYPE_ORDER,
            payload={"symbol": "ES", "side": "SELL", "quantity": 5.0},
        ))
        rt.run_once()

        with rt.orchestrator._engine.session() as s:  # type: ignore[attr-defined]
            t = TaskRepository(s).get("ord-sell-1")
        assert t is not None
        assert t.status == "completed"
        assert t.result["order_status"] == "FILLED"
        assert t.result["fill_price"] == 115.0
        assert t.result["realized_pnl"] == pytest.approx(75.0)  # (115-100)*5
        assert t.result["position_quantity"] == 0.0

        # 3. Lifecycle + domain events propagated
        assert EVT_TASK_CREATED in seen
        assert EVT_TASK_STARTED in seen
        assert EVT_TASK_COMPLETED in seen
        assert EVT_ORDER_PROCESSED in seen

        # 4. Two domain events persisted in LTM
        events = rt.memory.get_recent_events(
            event_type=EVT_ORDER_PROCESSED, limit=10
        )
        assert len(events) == 2
        # Counter
        assert agent.processed_count == 2
    finally:
        rt.shutdown()


def test_execution_agent_invalid_payload_marks_task_failed() -> None:
    """Validation error → task FAILED (not silently swallowed)."""
    rt = RuntimeEngine(
        retry_policy=RetryPolicy(max_attempts=1, initial_delay=0, jitter=False),
        poll_interval=0.0,
    )
    broker = MockBroker(initial_prices={"ES": 100.0})
    svc = ExecutionService(broker)
    rt.register_handler(TASK_TYPE_ORDER, ExecutionAgent(svc, rt.memory, rt.event_bus))

    seen: list[str] = []
    rt.subscribe("*", lambda ev: seen.append(ev.event_type))

    try:
        rt.submit(TaskCreate(
            id="ord-bad",
            task_type=TASK_TYPE_ORDER,
            payload={"side": "BUY", "quantity": 1.0},  # symbol missing
        ))
        rt.run_once()

        with rt.orchestrator._engine.session() as s:  # type: ignore[attr-defined]
            t = TaskRepository(s).get("ord-bad")
        assert t is not None
        assert t.status == "failed"
        assert t.error is not None
        assert "symbol" in t.error.lower()
        assert EVT_TASK_FAILED in seen
    finally:
        rt.shutdown()


def test_execution_agent_rejected_order_marks_task_completed() -> None:
    """REJECTED is a valid execution outcome — task COMPLETED, not failed."""
    rt = RuntimeEngine(
        retry_policy=RetryPolicy(max_attempts=1, initial_delay=0, jitter=False),
        poll_interval=0.0,
    )
    broker = MockBroker(initial_prices={"ES": 100.0})
    svc = ExecutionService(broker)
    rt.register_handler(TASK_TYPE_ORDER, ExecutionAgent(svc, rt.memory, rt.event_bus))

    try:
        rt.submit(TaskCreate(
            id="ord-rej",
            task_type=TASK_TYPE_ORDER,
            payload={"symbol": "ES", "side": "SELL", "quantity": 10.0},  # no position
        ))
        rt.run_once()

        with rt.orchestrator._engine.session() as s:  # type: ignore[attr-defined]
            t = TaskRepository(s).get("ord-rej")
        assert t is not None
        assert t.status == "completed"  # not failed — REJECTED is a result
        assert t.result["order_status"] == "REJECTED"
        assert "insufficient" in t.result["broker_message"].lower()
    finally:
        rt.shutdown()
