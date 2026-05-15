"""Task ORM model — unité de travail orchestrée par L4."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# Statuts canoniques d'une tâche
TASK_STATUS_PENDING = "pending"
TASK_STATUS_RUNNING = "running"
TASK_STATUS_COMPLETED = "completed"
TASK_STATUS_FAILED = "failed"
TASK_STATUS_CANCELLED = "cancelled"


class Task(Base):
    """Tâche orchestrée. ID texte (UUID) pour rester DB-agnostique."""

    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    task_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(32), default=TASK_STATUS_PENDING, nullable=False, index=True
    )
    assigned_to: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    result: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Task id={self.id} type={self.task_type} status={self.status}>"


__all__ = [
    "Task",
    "TASK_STATUS_PENDING",
    "TASK_STATUS_RUNNING",
    "TASK_STATUS_COMPLETED",
    "TASK_STATUS_FAILED",
    "TASK_STATUS_CANCELLED",
]
