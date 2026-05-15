"""AGIcore-v2 L4 — Planning / Orchestration / Runtime.

Public API :
- TaskHandler / HandlerRegistry  : routing table
- Dispatcher                     : stateless router
- AgentOrchestrator              : task lifecycle owner
- ExecutionLoop                  : polling driver (wakeup-aware)
- RuntimeEngine                  : full Phase 3 façade — Runtime Engine v1
"""
from .dispatcher import Dispatcher
from .execution_loop import ExecutionLoop
from .handlers import (
    HandlerAlreadyRegisteredError,
    HandlerNotFoundError,
    HandlerRegistry,
    TaskHandler,
)
from .orchestrator import AgentOrchestrator, TaskNotFoundError
from .runtime import RuntimeEngine

__all__ = [
    "TaskHandler",
    "HandlerRegistry",
    "HandlerNotFoundError",
    "HandlerAlreadyRegisteredError",
    "Dispatcher",
    "AgentOrchestrator",
    "TaskNotFoundError",
    "ExecutionLoop",
    "RuntimeEngine",
]
