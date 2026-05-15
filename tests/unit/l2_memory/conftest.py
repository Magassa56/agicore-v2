"""Fixtures pytest pour les tests L2 — bases isolées."""
from __future__ import annotations

from collections.abc import Iterator

import pytest

from agicore.l2_memory.adapters.sqlalchemy_engine import SqlAlchemyEngine
from agicore.l2_memory.adapters.sqlite_stm import SqliteStmAdapter
from agicore.l2_memory.migrations.init_schema import init_schema
from agicore.l2_memory.services.memory_service import MemoryService


@pytest.fixture()
def stm() -> Iterator[SqliteStmAdapter]:
    """STM en mémoire — isolation totale par test."""
    adapter = SqliteStmAdapter(":memory:")
    yield adapter
    adapter.close()


@pytest.fixture()
def ltm_engine() -> Iterator[SqlAlchemyEngine]:
    """LTM SQLite en mémoire — isolation totale par test."""
    engine = SqlAlchemyEngine("sqlite:///:memory:")
    init_schema(engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def memory_service(ltm_engine: SqlAlchemyEngine) -> MemoryService:
    return MemoryService(ltm_engine)
