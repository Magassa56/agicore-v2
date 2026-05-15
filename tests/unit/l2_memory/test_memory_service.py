"""Tests MemoryService — façade haut-niveau."""
from __future__ import annotations

from agicore.l2_memory.services.memory_service import MemoryService


def test_create_and_get_recent_events(memory_service: MemoryService) -> None:
    memory_service.create_event("trade.signal", task_id="t-1", payload={"x": 1})
    memory_service.create_event("trade.signal", task_id="t-2", payload={"x": 2})
    memory_service.create_event("system.heartbeat", agent_id="orch-1")

    all_recent = memory_service.get_recent_events(limit=10)
    assert len(all_recent) == 3

    only_signals = memory_service.get_recent_events(event_type="trade.signal")
    assert len(only_signals) == 2

    only_t1 = memory_service.get_recent_events(task_id="t-1")
    assert len(only_t1) == 1
    assert only_t1[0].payload == {"x": 1}


def test_save_and_load_state(memory_service: MemoryService) -> None:
    memory_service.save_state("trading_agent", "busy", context={"orders": 4})
    loaded = memory_service.load_state("trading_agent")
    assert loaded is not None
    assert loaded.state == "busy"
    assert loaded.context == {"orders": 4}


def test_load_state_returns_none_when_unknown(memory_service: MemoryService) -> None:
    assert memory_service.load_state("ghost-agent") is None


def test_execution_context_roundtrip(memory_service: MemoryService) -> None:
    memory_service.create_execution_context(
        task_id="task-z",
        session_id="sess-7",
        planner_state="planned",
    )
    ctx = memory_service.load_execution_context("task-z")
    assert ctx is not None
    assert ctx.session_id == "sess-7"
    assert ctx.status == "pending"

    updated = memory_service.update_execution_status("task-z", "completed")
    assert updated is not None
    assert updated.status == "completed"
