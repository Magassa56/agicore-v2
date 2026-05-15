"""Tests d'initialisation des bases STM et LTM."""
from __future__ import annotations

from sqlalchemy import inspect

from agicore.l2_memory.adapters.sqlalchemy_engine import SqlAlchemyEngine
from agicore.l2_memory.adapters.sqlite_stm import SqliteStmAdapter
from agicore.l2_memory.migrations.init_schema import init_schema


def test_stm_initializes_in_memory() -> None:
    stm = SqliteStmAdapter(":memory:")
    try:
        # Une opération simple doit fonctionner immédiatement
        stm.put("smoke", {"ok": True})
        assert stm.get("smoke") == {"ok": True}
    finally:
        stm.close()


def test_ltm_init_schema_creates_all_tables() -> None:
    engine = SqlAlchemyEngine("sqlite:///:memory:")
    try:
        tables = init_schema(engine)
        assert "events" in tables
        assert "tasks" in tables
        assert "agent_state" in tables
        assert "execution_context" in tables

        inspector = inspect(engine.engine)
        present = set(inspector.get_table_names())
        assert {"events", "tasks", "agent_state", "execution_context"}.issubset(present)
    finally:
        engine.dispose()


def test_ltm_init_schema_is_idempotent() -> None:
    engine = SqlAlchemyEngine("sqlite:///:memory:")
    try:
        init_schema(engine)
        # Doit pouvoir être rappelée sans erreur
        init_schema(engine)
    finally:
        engine.dispose()
