"""ORM models for AGIcore-v2 long-term memory (LTM)."""
from .agent_state import (
    AGENT_STATE_ACTIVE,
    AGENT_STATE_BUSY,
    AGENT_STATE_IDLE,
    AGENT_STATE_OFFLINE,
    AGENT_STATE_QUARANTINED,
    AgentState,
)
from .base import Base
from .event import Event
from .execution_context import (
    EXEC_STATUS_COMPLETED,
    EXEC_STATUS_FAILED,
    EXEC_STATUS_PENDING,
    EXEC_STATUS_RUNNING,
    MEMORY_SCOPE_GLOBAL,
    MEMORY_SCOPE_SESSION,
    MEMORY_SCOPE_TASK,
    ExecutionContext,
)
from .task import (
    TASK_STATUS_CANCELLED,
    TASK_STATUS_COMPLETED,
    TASK_STATUS_FAILED,
    TASK_STATUS_PENDING,
    TASK_STATUS_RUNNING,
    Task,
)

__all__ = [
    "Base",
    "Event",
    "Task",
    "AgentState",
    "ExecutionContext",
    # Task statuses
    "TASK_STATUS_PENDING",
    "TASK_STATUS_RUNNING",
    "TASK_STATUS_COMPLETED",
    "TASK_STATUS_FAILED",
    "TASK_STATUS_CANCELLED",
    # Agent states
    "AGENT_STATE_IDLE",
    "AGENT_STATE_ACTIVE",
    "AGENT_STATE_BUSY",
    "AGENT_STATE_QUARANTINED",
    "AGENT_STATE_OFFLINE",
    # Memory scopes
    "MEMORY_SCOPE_SESSION",
    "MEMORY_SCOPE_TASK",
    "MEMORY_SCOPE_GLOBAL",
    # Exec statuses
    "EXEC_STATUS_PENDING",
    "EXEC_STATUS_RUNNING",
    "EXEC_STATUS_COMPLETED",
    "EXEC_STATUS_FAILED",
]
