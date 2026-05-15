"""AgentState ORM model — état runtime persistant d'un agent."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# États canoniques
AGENT_STATE_IDLE = "idle"
AGENT_STATE_ACTIVE = "active"
AGENT_STATE_BUSY = "busy"
AGENT_STATE_QUARANTINED = "quarantined"
AGENT_STATE_OFFLINE = "offline"


class AgentState(Base):
    """État courant d'un agent. Une ligne par agent_id (key)."""

    __tablename__ = "agent_state"

    agent_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    state: Mapped[str] = mapped_column(
        String(32), default=AGENT_STATE_IDLE, nullable=False, index=True
    )
    context: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    last_heartbeat: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AgentState agent={self.agent_id} state={self.state}>"


__all__ = [
    "AgentState",
    "AGENT_STATE_IDLE",
    "AGENT_STATE_ACTIVE",
    "AGENT_STATE_BUSY",
    "AGENT_STATE_QUARANTINED",
    "AGENT_STATE_OFFLINE",
]
