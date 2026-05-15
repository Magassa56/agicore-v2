"""Pydantic schemas for Event."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EventCreate(BaseModel):
    """DTO d'entrée pour créer un event."""
    event_type: str = Field(..., min_length=1, max_length=64)
    task_id: str | None = Field(default=None, max_length=64)
    agent_id: str | None = Field(default=None, max_length=64)
    session_id: str | None = Field(default=None, max_length=64)
    payload: dict[str, Any] = Field(default_factory=dict)


class EventRead(BaseModel):
    """DTO de sortie pour lire un event."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    task_id: str | None
    agent_id: str | None
    session_id: str | None
    payload: dict[str, Any]
    created_at: datetime


__all__ = ["EventCreate", "EventRead"]
