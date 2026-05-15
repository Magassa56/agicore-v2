"""EventRepository — accès aux événements LTM."""
from __future__ import annotations

from datetime import datetime

import structlog
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.event import Event
from ..schemas.event import EventCreate, EventRead

logger = structlog.get_logger(__name__)


class EventRepository:
    """Repository pour la table events.

    Pas d'effet de bord global : la session est fournie par l'appelant.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, dto: EventCreate) -> EventRead:
        ev = Event(
            event_type=dto.event_type,
            task_id=dto.task_id,
            agent_id=dto.agent_id,
            session_id=dto.session_id,
            payload=dto.payload,
        )
        self._session.add(ev)
        self._session.flush()  # populates ev.id
        logger.info(
            "event.created",
            event_id=ev.id,
            event_type=ev.event_type,
            task_id=ev.task_id,
            agent_id=ev.agent_id,
        )
        return EventRead.model_validate(ev)

    def get(self, event_id: int) -> EventRead | None:
        ev = self._session.get(Event, event_id)
        return EventRead.model_validate(ev) if ev else None

    def list_recent(
        self,
        limit: int = 50,
        *,
        event_type: str | None = None,
        task_id: str | None = None,
        agent_id: str | None = None,
        since: datetime | None = None,
    ) -> list[EventRead]:
        stmt = select(Event).order_by(Event.created_at.desc()).limit(limit)
        if event_type:
            stmt = stmt.where(Event.event_type == event_type)
        if task_id:
            stmt = stmt.where(Event.task_id == task_id)
        if agent_id:
            stmt = stmt.where(Event.agent_id == agent_id)
        if since:
            stmt = stmt.where(Event.created_at >= since)
        rows = self._session.execute(stmt).scalars().all()
        return [EventRead.model_validate(r) for r in rows]


__all__ = ["EventRepository"]
