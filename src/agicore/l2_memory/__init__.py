"""AGIcore-v2 — L2 Memory layer.

Public API (stable) :
- SqliteStmAdapter        : short-term memory (stdlib sqlite3)
- SqlAlchemyEngine        : long-term memory engine
- MemoryService           : high-level service facade
- init_schema/drop_schema : migrations
"""
from .adapters import DEFAULT_LTM_URL, SqlAlchemyEngine, SqliteStmAdapter
from .migrations import drop_schema, init_schema
from .repositories import EventRepository, StateRepository, TaskRepository
from .services import MemoryService

__all__ = [
    # Adapters
    "SqliteStmAdapter",
    "SqlAlchemyEngine",
    "DEFAULT_LTM_URL",
    # Repositories
    "EventRepository",
    "TaskRepository",
    "StateRepository",
    # Service
    "MemoryService",
    # Migrations
    "init_schema",
    "drop_schema",
]
