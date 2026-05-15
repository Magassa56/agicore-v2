"""AgentOrchestrator — task lifecycle owner.

Submits tasks, picks up pending ones, runs them through the dispatcher with
retry policy, persists results in LTM, and emits lifecycle events.

Lifecycle (canonical) :
    pending → running → completed
                     → failed (after retry exhaustion)
                     → cancelled
"""
from __future__ import annotations

from typing import Any

import structlog

from agicore.core.events import (
    EVT_TASK_COMPLETED,
    EVT_TASK_CREATED,
    EVT_TASK_FAILED,
    EVT_TASK_RETRIED,
    EVT_TASK_STARTED,
    EventBus,
)
from agicore.core.retry import RetryError, RetryPolicy
from agicore.l2_memory.adapters.sqlalchemy_engine import SqlAlchemyEngine
from agicore.l2_memory.models.task import (
    TASK_STATUS_COMPLETED,
    TASK_STATUS_FAILED,
    TASK_STATUS_PENDING,
    TASK_STATUS_RUNNING,
)
from agicore.l2_memory.repositories.task_repository import TaskRepository
from agicore.l2_memory.schemas.task import TaskCreate, TaskRead, TaskUpdate
from agicore.l2_memory.services.memory_service import MemoryService

from .dispatcher import Dispatcher

logger = structlog.get_logger(__name__)


class TaskNotFoundError(LookupError):
    """No task with that id."""


class AgentOrchestrator:
    """Owner of the task lifecycle. Composes Memory + Dispatcher + EventBus."""

    def __init__(
        self,
        *,
        memory: MemoryService,
        engine: SqlAlchemyEngine,
        dispatcher: Dispatcher,
        event_bus: EventBus,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        self._memory = memory
        self._engine = engine
        self._dispatcher = dispatcher
        self._bus = event_bus
        self._retry_policy = retry_policy or RetryPolicy(max_attempts=1)

    # ------------------------------------------------------------------ Submit
    def submit_task(self, dto: TaskCreate) -> TaskRead:
        """Persist a new task in pending state and emit task.created."""
        with self._engine.session() as s:
            repo = TaskRepository(s)
            task = repo.create(dto)
        self._memory.create_event(
            EVT_TASK_CREATED,
            task_id=task.id,
            agent_id=task.assigned_to,
            payload={"task_type": task.task_type},
        )
        self._bus.emit(
            EVT_TASK_CREATED,
            task_id=task.id,
            task_type=task.task_type,
            assigned_to=task.assigned_to,
        )
        logger.info("orchestrator.task_submitted", task_id=task.id, task_type=task.task_type)
        return task

    # ----------------------------------------------------------- Execute single
    def execute_one(self, task_id: str) -> TaskRead:
        """Run one task end-to-end through its full lifecycle."""
        with self._engine.session() as s:
            repo = TaskRepository(s)
            current = repo.get(task_id)
            if current is None:
                raise TaskNotFoundError(f"unknown task_id={task_id!r}")
            if current.status not in (TASK_STATUS_PENDING,):
                logger.warning(
                    "orchestrator.skip_non_pending",
                    task_id=task_id,
                    status=current.status,
                )
                return current
            running = repo.update(task_id, TaskUpdate(status=TASK_STATUS_RUNNING))
            assert running is not None
            task = running

        self._memory.create_event(
            EVT_TASK_STARTED, task_id=task.id, payload={"task_type": task.task_type}
        )
        self._bus.emit(EVT_TASK_STARTED, task_id=task.id, task_type=task.task_type)

        # Run the handler with retry, counting attempts via a closure
        attempt_box = {"n": 0}

        def _attempt() -> dict[str, Any]:
            attempt_box["n"] += 1
            n = attempt_box["n"]
            if n > 1:
                self._bus.emit(
                    EVT_TASK_RETRIED, task_id=task.id, attempt=n
                )
                self._memory.create_event(
                    EVT_TASK_RETRIED,
                    task_id=task.id,
                    payload={"attempt": n},
                )
            return self._dispatcher.dispatch(task)

        try:
            result = self._retry_policy.execute(_attempt)
        except RetryError as exc:
            return self._mark_failed(task.id, error=str(exc.__cause__ or exc))
        except Exception as exc:
            # Non-retryable or pre-retry-policy error path
            return self._mark_failed(task.id, error=str(exc))

        return self._mark_completed(task.id, result=result)

    # ------------------------------------------------------------ Execute pending
    def execute_pending(self, *, limit: int = 10) -> list[TaskRead]:
        """Execute up to `limit` pending tasks. Returns the list of finished tasks."""
        with self._engine.session() as s:
            repo = TaskRepository(s)
            pending = repo.list_by_status(TASK_STATUS_PENDING, limit=limit)
        finished: list[TaskRead] = []
        for t in pending:
            finished.append(self.execute_one(t.id))
        return finished

    # ------------------------------------------------------------------ Helpers
    def _mark_completed(self, task_id: str, *, result: dict[str, Any]) -> TaskRead:
        with self._engine.session() as s:
            repo = TaskRepository(s)
            updated = repo.update(
                task_id,
                TaskUpdate(status=TASK_STATUS_COMPLETED, result=result),
            )
        assert updated is not None
        self._memory.create_event(
            EVT_TASK_COMPLETED, task_id=task_id, payload={"result_keys": sorted(result.keys())}
        )
        self._bus.emit(EVT_TASK_COMPLETED, task_id=task_id)
        logger.info("orchestrator.task_completed", task_id=task_id)
        return updated

    def _mark_failed(self, task_id: str, *, error: str) -> TaskRead:
        with self._engine.session() as s:
            repo = TaskRepository(s)
            updated = repo.update(
                task_id,
                TaskUpdate(status=TASK_STATUS_FAILED, error=error[:2048]),
            )
        assert updated is not None
        self._memory.create_event(
            EVT_TASK_FAILED, task_id=task_id, payload={"error": error[:512]}
        )
        self._bus.emit(EVT_TASK_FAILED, task_id=task_id, error=error[:512])
        logger.error("orchestrator.task_failed", task_id=task_id, error=error)
        return updated


__all__ = ["AgentOrchestrator", "TaskNotFoundError"]
