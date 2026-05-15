"""Event ORM model — capture les événements observés ou émis par le système."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Event(Base):
    """Événement stocké en LTM.

    Tracé immuable d'une observation (L1) ou d'une action (L5) significative.
    """

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    task_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    agent_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    session_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False, index=True
    )

    __table_args__ = (
        Index("ix_events_type_created", "event_type", "created_at"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Event id={self.id} type={self.event_type} task={self.task_id}>"


__all__ = ["Event"]
