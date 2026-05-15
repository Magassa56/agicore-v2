"""ExecutionContext ORM model — contexte d'exécution d'une tâche L4."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# Memory scope canoniques
MEMORY_SCOPE_SESSION = "session"
MEMORY_SCOPE_TASK = "task"
MEMORY_SCOPE_GLOBAL = "global"

# Exec status canoniques
EXEC_STATUS_PENDING = "pending"
EXEC_STATUS_RUNNING = "running"
EXEC_STATUS_COMPLETED = "completed"
EXEC_STATUS_FAILED = "failed"


class ExecutionContext(Base):
    """Contexte d'exécution propagé à travers L3 → L4 → L5."""

    __tablename__ = "execution_context"

    task_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False, index=True
    )
    planner_state: Mapped[str] = mapped_column(String(64), nullable=False)
    memory_scope: Mapped[str] = mapped_column(
        String(32), default=MEMORY_SCOPE_TASK, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(32), default=EXEC_STATUS_PENDING, nullable=False, index=True
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ExecCtx task={self.task_id} session={self.session_id} status={self.status}>"


__all__ = [
    "ExecutionContext",
    "MEMORY_SCOPE_SESSION",
    "MEMORY_SCOPE_TASK",
    "MEMORY_SCOPE_GLOBAL",
    "EXEC_STATUS_PENDING",
    "EXEC_STATUS_RUNNING",
    "EXEC_STATUS_COMPLETED",
    "EXEC_STATUS_FAILED",
]
