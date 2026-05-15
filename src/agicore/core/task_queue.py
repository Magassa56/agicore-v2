"""TaskQueue — minimal in-process FIFO façade with persistence + wakeup.

Decouples the producer of tasks (any caller) from the consumer (the
orchestrator's execution loop). Each enqueue call:

1. persists the task in LTM (via orchestrator.submit_task) so it survives crashes;
2. pulses a wakeup signal so any blocking execution loop polls immediately
   instead of waiting out the full poll interval.

Stays intentionally minimal — Phase 3 does NOT introduce a distributed broker.
That can be swapped in behind this same interface in a later phase.
"""
from __future__ import annotations

from threading import Event as ThreadEvent
from typing import TYPE_CHECKING

import structlog

from agicore.l2_memory.schemas.task import TaskCreate, TaskRead

if TYPE_CHECKING:
    from agicore.l4_planning.orchestrator import AgentOrchestrator

logger = structlog.get_logger(__name__)


class TaskQueue:
    """Producer-side façade. Persists the task and wakes the consumer."""

    def __init__(
        self,
        orchestrator: "AgentOrchestrator",
        *,
        wakeup: ThreadEvent | None = None,
    ) -> None:
        self._orch = orchestrator
        self._wakeup = wakeup or ThreadEvent()
        self._enqueued = 0

    @property
    def wakeup_event(self) -> ThreadEvent:
        """The shared wakeup event consumed by the ExecutionLoop."""
        return self._wakeup

    @property
    def enqueued_count(self) -> int:
        """Total number of tasks enqueued since this queue was created."""
        return self._enqueued

    def enqueue(self, task: TaskCreate) -> TaskRead:
        """Persist + signal. Returns the persisted TaskRead."""
        persisted = self._orch.submit_task(task)
        self._enqueued += 1
        self._wakeup.set()
        logger.info(
            "task_queue.enqueued",
            task_id=persisted.id,
            task_type=persisted.task_type,
            total_enqueued=self._enqueued,
        )
        return persisted


__all__ = ["TaskQueue"]
