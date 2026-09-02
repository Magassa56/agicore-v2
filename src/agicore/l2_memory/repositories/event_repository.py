"""EventRepository — accès aux événements LTM."""
from __future__ import annotations

from datetime import datetime

import structlog
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models.event import Event
from ..schemas.event import (
    EventCreate,
    EventRead,
    IdempotentEventApplyResult,
    IdempotentEventApplyStatus,
    IdempotentEventCreate,
    IdempotentEventRecord,
    verify_idempotent_event,
)

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

    def create_idempotent(
        self, dto: IdempotentEventCreate
    ) -> IdempotentEventApplyResult:
        """Insert once by effect_id, resolving only its unique-key collision."""
        prepared = verify_idempotent_event(dto)
        existing = self._get_by_effect_id(prepared.effect_id)
        if existing is not None:
            return self._existing_result(existing, prepared)

        event = Event(
            event_type=prepared.event_type,
            task_id=prepared.task_id,
            agent_id=prepared.agent_id,
            session_id=prepared.session_id,
            payload=dict(prepared.payload),
            effect_id=prepared.effect_id,
            payload_hash=prepared.payload_hash,
            created_at=prepared.occurred_at,
        )
        self._session.add(event)
        try:
            self._session.flush()
        except IntegrityError as exc:
            self._session.rollback()
            if not self._is_effect_id_collision(exc):
                raise
            existing = self._get_by_effect_id(prepared.effect_id)
            if existing is None:
                raise
            return self._existing_result(existing, prepared)

        logger.info(
            "event.idempotent_applied",
            event_id=event.id,
            effect_id=event.effect_id,
            event_type=event.event_type,
        )
        return IdempotentEventApplyResult(
            status=IdempotentEventApplyStatus.APPLIED_NEW,
            event=self._record(event),
        )

    def _get_by_effect_id(self, effect_id: str) -> Event | None:
        return self._session.execute(
            select(Event).where(Event.effect_id == effect_id)
        ).scalar_one_or_none()

    def _existing_result(
        self, event: Event, dto: IdempotentEventCreate
    ) -> IdempotentEventApplyResult:
        same_content = (
            event.effect_id == dto.effect_id
            and event.payload_hash == dto.payload_hash
            and event.event_type == dto.event_type
            and event.task_id == dto.task_id
            and event.agent_id == dto.agent_id
            and event.session_id == dto.session_id
            and self._normalized_time(event.created_at) == dto.occurred_at
            and event.payload == dto.payload
        )
        return IdempotentEventApplyResult(
            status=(
                IdempotentEventApplyStatus.ALREADY_APPLIED
                if same_content
                else IdempotentEventApplyStatus.CONFLICT
            ),
            event=self._record(event),
        )

    @staticmethod
    def _normalized_time(value: datetime) -> datetime:
        from datetime import timezone

        if value.tzinfo is None or value.utcoffset() is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @classmethod
    def _record(cls, event: Event) -> IdempotentEventRecord:
        if event.effect_id is None or event.payload_hash is None:
            raise RuntimeError("idempotent event row lacks its authoritative identity")
        return IdempotentEventRecord(
            id=event.id,
            effect_id=event.effect_id,
            payload_hash=event.payload_hash,
            event_type=event.event_type,
            occurred_at=cls._normalized_time(event.created_at),
            task_id=event.task_id,
            agent_id=event.agent_id,
            session_id=event.session_id,
            payload=event.payload,
        )

    @staticmethod
    def _is_effect_id_collision(exc: IntegrityError) -> bool:
        original = exc.orig
        diagnostic = getattr(original, "diag", None)
        if getattr(diagnostic, "constraint_name", None) == "ux_events_effect_id":
            return True
        message = str(original).lower()
        return (
            "ux_events_effect_id" in message
            or "unique constraint failed: events.effect_id" in message
        )

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
