"""Tests for AgentOrchestrator full lifecycle."""
from __future__ import annotations

import pytest

from agicore.core.events import (
    EVT_TASK_COMPLETED,
    EVT_TASK_CREATED,
    EVT_TASK_FAILED,
    EVT_TASK_RETRIED,
    EVT_TASK_STARTED,
    EventBus,
)
from agicore.l2_memory.schemas.task import TaskCreate
from agicore.l4_planning.handlers import HandlerRegistry
from agicore.l4_planning.orchestrator import AgentOrchestrator, TaskNotFoundError


def test_submit_task_creates_in_pending(orchestrator: AgentOrchestrator) -> None:
    task = orchestrator.submit_task(TaskCreate(id="t-1", task_type="tx.echo"))
    assert task.id == "t-1"
    assert task.status == "pending"


def test_execute_one_happy_path(
    orchestrator: AgentOrchestrator,
    registry: HandlerRegistry,
) -> None:
    registry.register("tx.echo", lambda t: {"echoed": t.payload})
    orchestrator.submit_task(
        TaskCreate(id="t-1", task_type="tx.echo", payload={"hello": "world"})
    )
    finished = orchestrator.execute_one("t-1")
    assert finished.status == "completed"
    assert finished.result == {"echoed": {"hello": "world"}}


def test_execute_one_unknown_task_raises(orchestrator: AgentOrchestrator) -> None:
    with pytest.raises(TaskNotFoundError):
        orchestrator.execute_one("ghost")


def test_execute_one_failure_after_retry_exhaustion(
    orchestrator: AgentOrchestrator,
    registry: HandlerRegistry,
) -> None:
    def always_fail(t):
        raise RuntimeError("doom")

    registry.register("tx.boom", always_fail)
    orchestrator.submit_task(TaskCreate(id="t-1", task_type="tx.boom"))
    finished = orchestrator.execute_one("t-1")
    assert finished.status == "failed"
    assert finished.error is not None
    assert "doom" in finished.error


def test_execute_one_succeeds_after_one_retry(
    orchestrator: AgentOrchestrator,
    registry: HandlerRegistry,
) -> None:
    state = {"calls": 0}

    def flaky(t):
        state["calls"] += 1
        if state["calls"] < 2:
            raise ValueError("transient")
        return {"ok": True}

    registry.register("tx.flaky", flaky)
    orchestrator.submit_task(TaskCreate(id="t-1", task_type="tx.flaky"))
    finished = orchestrator.execute_one("t-1")
    assert finished.status == "completed"
    assert state["calls"] == 2


def test_execute_pending_processes_batch(
    orchestrator: AgentOrchestrator,
    registry: HandlerRegistry,
) -> None:
    registry.register("tx.echo", lambda t: {"id": t.id})
    for i in range(3):
        orchestrator.submit_task(TaskCreate(id=f"t-{i}", task_type="tx.echo"))
    finished = orchestrator.execute_pending(limit=10)
    assert len(finished) == 3
    assert all(t.status == "completed" for t in finished)


def test_event_propagation_lifecycle(
    orchestrator: AgentOrchestrator,
    registry: HandlerRegistry,
    event_bus: EventBus,
) -> None:
    seen: list[str] = []
    event_bus.subscribe("*", lambda ev: seen.append(ev.event_type))

    registry.register("tx.echo", lambda t: {"ok": True})
    orchestrator.submit_task(TaskCreate(id="t-1", task_type="tx.echo"))
    orchestrator.execute_one("t-1")

    assert EVT_TASK_CREATED in seen
    assert EVT_TASK_STARTED in seen
    assert EVT_TASK_COMPLETED in seen
    assert EVT_TASK_FAILED not in seen


def test_event_propagation_emits_retry_event(
    orchestrator: AgentOrchestrator,
    registry: HandlerRegistry,
    event_bus: EventBus,
) -> None:
    seen: list[str] = []
    event_bus.subscribe("*", lambda ev: seen.append(ev.event_type))

    state = {"calls": 0}

    def flaky(t):
        state["calls"] += 1
        if state["calls"] < 2:
            raise ValueError("transient")
        return {}

    registry.register("tx.flaky", flaky)
    orchestrator.submit_task(TaskCreate(id="t-1", task_type="tx.flaky"))
    orchestrator.execute_one("t-1")

    assert EVT_TASK_RETRIED in seen
