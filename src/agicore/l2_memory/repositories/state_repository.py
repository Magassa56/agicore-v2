"""StateRepository — accès à AgentState et ExecutionContext."""
from __future__ import annotations

from datetime import datetime, timezone

import structlog
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.agent_state import AgentState
from ..models.execution_context import ExecutionContext
from ..schemas.agent_state import AgentStateRead, AgentStateUpsert
from ..schemas.execution_context import ExecutionContextCreate, ExecutionContextRead

logger = structlog.get_logger(__name__)


class StateRepository:
    """Repository combiné pour AgentState et ExecutionContext.

    L'état d'un agent et le contexte d'exécution d'une tâche sont liés
    sémantiquement : on les groupe ici pour limiter les dépendances croisées.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    # ------------------------------------------------------------------ AgentState
    def upsert_agent_state(self, dto: AgentStateUpsert) -> AgentStateRead:
        existing = self._session.get(AgentState, dto.agent_id)
        if existing is None:
            existing = AgentState(
                agent_id=dto.agent_id,
                state=dto.state,
                context=dto.context,
            )
            self._session.add(existing)
            logger.info("agent_state.created", agent_id=dto.agent_id, state=dto.state)
        else:
            existing.state = dto.state
            existing.context = dto.context
            existing.last_heartbeat = datetime.now(timezone.utc)
            logger.info("agent_state.updated", agent_id=dto.agent_id, state=dto.state)
        self._session.flush()
        return AgentStateRead.model_validate(existing)

    def get_agent_state(self, agent_id: str) -> AgentStateRead | None:
        s = self._session.get(AgentState, agent_id)
        return AgentStateRead.model_validate(s) if s else None

    def list_agents_by_state(self, state: str) -> list[AgentStateRead]:
        stmt = select(AgentState).where(AgentState.state == state)
        rows = self._session.execute(stmt).scalars().all()
        return [AgentStateRead.model_validate(r) for r in rows]

    # ----------------------------------------------------------- ExecutionContext
    def create_execution_context(
        self, dto: ExecutionContextCreate
    ) -> ExecutionContextRead:
        ctx = ExecutionContext(
            task_id=dto.task_id,
            session_id=dto.session_id,
            planner_state=dto.planner_state,
            memory_scope=dto.memory_scope,
            status=dto.status,
        )
        self._session.add(ctx)
        self._session.flush()
        logger.info(
            "execution_context.created",
            task_id=ctx.task_id,
            session_id=ctx.session_id,
            status=ctx.status,
        )
        return ExecutionContextRead.model_validate(ctx)

    def get_execution_context(self, task_id: str) -> ExecutionContextRead | None:
        ctx = self._session.get(ExecutionContext, task_id)
        return ExecutionContextRead.model_validate(ctx) if ctx else None

    def update_execution_status(
        self, task_id: str, status: str
    ) -> ExecutionContextRead | None:
        ctx = self._session.get(ExecutionContext, task_id)
        if ctx is None:
            return None
        ctx.status = status
        self._session.flush()
        logger.info("execution_context.updated", task_id=task_id, status=status)
        return ExecutionContextRead.model_validate(ctx)


__all__ = ["StateRepository"]
