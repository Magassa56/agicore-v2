"""Fixtures pour tests l4_planning."""
from __future__ import annotations

from collections.abc import Iterator

import pytest

from agicore.core.events import EventBus
from agicore.core.retry import RetryPolicy
from agicore.l2_memory.adapters.sqlalchemy_engine import SqlAlchemyEngine
from agicore.l2_memory.migrations.init_schema import init_schema
from agicore.l2_memory.services.memory_service import MemoryService
from agicore.l4_planning.dispatcher import Dispatcher
from agicore.l4_planning.handlers import HandlerRegistry
from agicore.l4_planning.orchestrator import AgentOrchestrator


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
def registry() -> HandlerRegistry:
    return HandlerRegistry()


@pytest.fixture()
def dispatcher(registry: HandlerRegistry, event_bus: EventBus) -> Dispatcher:
    return Dispatcher(registry, event_bus)


@pytest.fixture()
def orchestrator(
    memory: MemoryService,
    engine: SqlAlchemyEngine,
    dispatcher: Dispatcher,
    event_bus: EventBus,
) -> AgentOrchestrator:
    return AgentOrchestrator(
        memory=memory,
        engine=engine,
        dispatcher=dispatcher,
        event_bus=event_bus,
        retry_policy=RetryPolicy(max_attempts=2, initial_delay=0.0, jitter=False),
    )
