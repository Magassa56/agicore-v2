"""MemoryService — façade haut-niveau pour la couche L2.

Compose les repositories et expose une API simple aux couches L3/L4/L5.
Toutes les opérations sont structlog-ready : aucun print, niveau approprié.
"""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any

import structlog

from ..adapters.sqlalchemy_engine import SqlAlchemyEngine
from ..repositories.event_repository import EventRepository
from ..repositories.state_repository import StateRepository
from ..repositories.task_repository import TaskRepository
from ..schemas.agent_state import AgentStateRead, AgentStateUpsert
from ..schemas.event import (
    EventCreate,
    EventRead,
    IdempotentEventApplyResult,
    prepare_idempotent_event,
)
from ..schemas.execution_context import ExecutionContextCreate, ExecutionContextRead

logger = structlog.get_logger(__name__)

class MemoryService:
    """Façade L2. Toujours instanciée avec un SqlAlchemyEngine.

    Les méthodes ouvrent et ferment leur propre session — pas d'état partagé.
    """

    def __init__(self, engine: SqlAlchemyEngine) -> None:
        self._engine = engine

    # ------------------------------------------------------------------ Events
    def create_event(
        self,
        event_type: str,
        *,
        task_id: str | None = None,
        agent_id: str | None = None,
        session_id: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> EventRead:
        """Crée un event en LTM. Retourne le DTO en lecture (avec id, timestamp)."""
        dto = EventCreate(
            event_type=event_type,
            task_id=task_id,
            agent_id=agent_id,
            session_id=session_id,
            payload=payload or {},
        )
        with self._engine.session() as s:
            repo = EventRepository(s)
            return repo.create(dto)

    def create_event_idempotent(
        self,
        *,
        effect_id: str,
        occurred_at: datetime,
        event_type: str,
        task_id: str | None = None,
        agent_id: str | None = None,
        session_id: str | None = None,
        payload: Mapping[str, object],
    ) -> IdempotentEventApplyResult:
        """Apply one canonical event exactly once in the local SQL authority."""
        dto = prepare_idempotent_event(
            effect_id=effect_id,
            occurred_at=occurred_at,
            event_type=event_type,
            task_id=task_id,
            agent_id=agent_id,
            session_id=session_id,
            payload=payload,
        )
        with self._engine.session() as session:
            return EventRepository(session).create_idempotent(dto)

    def get_recent_events(
        self,
        limit: int = 50,
        *,
        event_type: str | None = None,
        task_id: str | None = None,
        agent_id: str | None = None,
        since: datetime | None = None,
    ) -> list[EventRead]:
        """Récupère les events récents avec filtrage optionnel."""
        with self._engine.session() as s:
            repo = EventRepository(s)
            return repo.list_recent(
                limit,
                event_type=event_type,
                task_id=task_id,
                agent_id=agent_id,
                since=since,
            )

    # ------------------------------------------------------------------ State
    def save_state(
        self,
        agent_id: str,
        state: str,
        *,
        context: dict[str, Any] | None = None,
    ) -> AgentStateRead:
        """Crée ou met à jour l'état d'un agent."""
        dto = AgentStateUpsert(agent_id=agent_id, state=state, context=context or {})
        with self._engine.session() as s:
            repo = StateRepository(s)
            return repo.upsert_agent_state(dto)

    def load_state(self, agent_id: str) -> AgentStateRead | None:
        """Charge l'état d'un agent ou None si absent."""
        with self._engine.session() as s:
            repo = StateRepository(s)
            return repo.get_agent_state(agent_id)

    # ----------------------------------------------------------- ExecutionContext
    def create_execution_context(
        self,
        task_id: str,
        session_id: str,
        planner_state: str,
        *,
        memory_scope: str = "task",
        status: str = "pending",
    ) -> ExecutionContextRead:
        """Crée un ExecutionContext propagé à travers L3/L4/L5."""
        dto = ExecutionContextCreate(
            task_id=task_id,
            session_id=session_id,
            planner_state=planner_state,
            memory_scope=memory_scope,
            status=status,
        )
        with self._engine.session() as s:
            repo = StateRepository(s)
            return repo.create_execution_context(dto)

    def load_execution_context(self, task_id: str) -> ExecutionContextRead | None:
        with self._engine.session() as s:
            repo = StateRepository(s)
            return repo.get_execution_context(task_id)

    def update_execution_status(
        self, task_id: str, status: str
    ) -> ExecutionContextRead | None:
        with self._engine.session() as s:
            repo = StateRepository(s)
            return repo.update_execution_status(task_id, status)

    # ------------------------------------------------------------------ Tasks (mince)
    def task_repository(self) -> TaskRepository:
        """Renvoie un TaskRepository scoped sur une session — usage avancé."""
        # NOTE: pour rester cohérent avec le pattern session-scoped,
        # les opérations Task passent par le repository directement avec une session
        # ouverte par l'appelant. Cette méthode est volontairement minimaliste pour
        # ne pas pré-baker une session sans gestion de cycle de vie.
        raise NotImplementedError(
            "Use engine.session() and instantiate TaskRepository inside the with-block."
        )


__all__ = ["MemoryService"]
