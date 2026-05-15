"""Pydantic schemas for ExecutionContext."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ExecutionContextCreate(BaseModel):
    task_id: str = Field(..., min_length=1, max_length=64)
    session_id: str = Field(..., min_length=1, max_length=64)
    planner_state: str = Field(..., min_length=1, max_length=64)
    memory_scope: str = Field(default="task", max_length=32)
    status: str = Field(default="pending", max_length=32)


class ExecutionContextRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: str
    session_id: str
    timestamp: datetime
    planner_state: str
    memory_scope: str
    status: str


__all__ = ["ExecutionContextCreate", "ExecutionContextRead"]
