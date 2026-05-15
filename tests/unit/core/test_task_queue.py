"""Tests for TaskQueue."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from agicore.core.task_queue import TaskQueue
from agicore.l2_memory.schemas.task import TaskCreate, TaskRead


def _stub_orchestrator() -> MagicMock:
    """Minimal mock of AgentOrchestrator for unit-testing TaskQueue."""
    from datetime import datetime, timezone
    orch = MagicMock()

    def submit(dto: TaskCreate) -> TaskRead:
        now = datetime.now(timezone.utc)
        return TaskRead(
            id=dto.id,
            task_type=dto.task_type,
            status="pending",
            assigned_to=dto.assigned_to,
            payload=dto.payload,
            result=None,
            error=None,
            created_at=now,
            updated_at=now,
        )

    orch.submit_task = submit
    return orch


def test_enqueue_pulses_wakeup() -> None:
    orch = _stub_orchestrator()
    q = TaskQueue(orch)
    assert not q.wakeup_event.is_set()

    persisted = q.enqueue(TaskCreate(id="t-1", task_type="tx.echo"))
    assert persisted.id == "t-1"
    assert q.wakeup_event.is_set()


def test_enqueue_increments_count() -> None:
    orch = _stub_orchestrator()
    q = TaskQueue(orch)
    assert q.enqueued_count == 0
    q.enqueue(TaskCreate(id="t-1", task_type="x"))
    q.enqueue(TaskCreate(id="t-2", task_type="x"))
    assert q.enqueued_count == 2


def test_external_wakeup_event_is_used() -> None:
    """Loop and queue must share the same event for the wakeup pattern to work."""
    from threading import Event as ThreadEvent

    shared = ThreadEvent()
    orch = _stub_orchestrator()
    q = TaskQueue(orch, wakeup=shared)
    assert q.wakeup_event is shared
    q.enqueue(TaskCreate(id="t-1", task_type="x"))
    assert shared.is_set()
