"""Pydantic schemas for Task."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    id: str = Field(..., min_length=1, max_length=64)
    task_type: str = Field(..., min_length=1, max_length=64)
    assigned_to: str | None = Field(default=None, max_length=64)
    payload: dict[str, Any] = Field(default_factory=dict)


class TaskUpdate(BaseModel):
    status: str | None = Field(default=None, max_length=32)
    assigned_to: str | None = Field(default=None, max_length=64)
    result: dict[str, Any] | None = None
    error: str | None = Field(default=None, max_length=2048)


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    task_type: str
    status: str
    assigned_to: str | None
    payload: dict[str, Any]
    result: dict[str, Any] | None
    error: str | None
    created_at: datetime
    updated_at: datetime


__all__ = ["TaskCreate", "TaskUpdate", "TaskRead"]
