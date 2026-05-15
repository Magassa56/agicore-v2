"""TaskRepository — accès aux tâches LTM."""
from __future__ import annotations

import structlog
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.task import Task
from ..schemas.task import TaskCreate, TaskRead, TaskUpdate

logger = structlog.get_logger(__name__)


class TaskRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, dto: TaskCreate) -> TaskRead:
        t = Task(
            id=dto.id,
            task_type=dto.task_type,
            assigned_to=dto.assigned_to,
            payload=dto.payload,
        )
        self._session.add(t)
        self._session.flush()
        logger.info("task.created", task_id=t.id, task_type=t.task_type)
        return TaskRead.model_validate(t)

    def get(self, task_id: str) -> TaskRead | None:
        t = self._session.get(Task, task_id)
        return TaskRead.model_validate(t) if t else None

    def update(self, task_id: str, dto: TaskUpdate) -> TaskRead | None:
        t = self._session.get(Task, task_id)
        if t is None:
            return None
        if dto.status is not None:
            t.status = dto.status
        if dto.assigned_to is not None:
            t.assigned_to = dto.assigned_to
        if dto.result is not None:
            t.result = dto.result
        if dto.error is not None:
            t.error = dto.error
        self._session.flush()
        logger.info("task.updated", task_id=t.id, status=t.status)
        return TaskRead.model_validate(t)

    def list_by_status(self, status: str, *, limit: int = 100) -> list[TaskRead]:
        stmt = (
            select(Task)
            .where(Task.status == status)
            .order_by(Task.created_at.asc())
            .limit(limit)
        )
        rows = self._session.execute(stmt).scalars().all()
        return [TaskRead.model_validate(r) for r in rows]


__all__ = ["TaskRepository"]
