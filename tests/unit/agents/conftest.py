"""Fixtures for agent unit tests."""
from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timezone

import pytest

from agicore.core.events import EventBus
from agicore.l2_memory.adapters.sqlalchemy_engine import SqlAlchemyEngine
from agicore.l2_memory.migrations.init_schema import init_schema
from agicore.l2_memory.schemas.task import TaskRead
from agicore.l2_memory.services.memory_service import MemoryService


@pytest.fixture()
def engine() -> Iterator[SqlAlchemyEngine]:
    eng = SqlAlchemyEngine("sqlite:///:memory:")
    init_schema(eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def memory(engine: SqlAlchemyEngine) -> MemoryService:
    return MemoryService(engine)


@pytest.fixture()
def event_bus() -> EventBus:
    return EventBus()


@pytest.fixture()
def make_task():
    """Factory to build a TaskRead suitable for direct handler invocation."""
    def _factory(
        task_id: str = "t-1",
        task_type: str = "agent.echo",
        payload: dict | None = None,
    ) -> TaskRead:
        now = datetime.now(timezone.utc)
        return TaskRead(
            id=task_id,
            task_type=task_type,
            status="running",
            assigned_to=None,
            payload=payload or {},
            result=None,
            error=None,
            created_at=now,
            updated_at=now,
        )
    return _factory
