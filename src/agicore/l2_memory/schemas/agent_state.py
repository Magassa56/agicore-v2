"""Pydantic schemas for AgentState."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AgentStateUpsert(BaseModel):
    agent_id: str = Field(..., min_length=1, max_length=64)
    state: str = Field(default="idle", max_length=32)
    context: dict[str, Any] = Field(default_factory=dict)


class AgentStateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    agent_id: str
    state: str
    context: dict[str, Any]
    last_heartbeat: datetime
    updated_at: datetime


__all__ = ["AgentStateUpsert", "AgentStateRead"]
