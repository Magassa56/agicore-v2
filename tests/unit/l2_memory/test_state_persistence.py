"""Tests STM (sqlite_stm) + persistance LTM cross-session."""
from __future__ import annotations

import time

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError

from agicore.l2_memory.adapters.sqlalchemy_engine import SqlAlchemyEngine
from agicore.l2_memory.adapters.sqlite_stm import SqliteStmAdapter
from agicore.l2_memory.migrations.add_idempotent_memory_effect import (
    _EFFECT_INDEX_DDL,
    _SQLITE_INSERT_TRIGGER_DDL,
    _SQLITE_UPDATE_TRIGGER_DDL,
    _postgresql_pair_expression_is_exact,
    add_idempotent_memory_effect,
)
from agicore.l2_memory.services.memory_service import MemoryService


def test_stm_put_get_default(stm: SqliteStmAdapter) -> None:
    stm.put("k1", {"a": 1})
    assert stm.get("k1") == {"a": 1}
    assert stm.get("missing") is None
    assert stm.get("missing", default={"x": 1}) == {"x": 1}


def test_stm_scoped_by_task(stm: SqliteStmAdapter) -> None:
    stm.put("plan", {"step": 1}, task_id="t-1")
    stm.put("plan", {"step": 2}, task_id="t-2")
    assert stm.get("plan", task_id="t-1") == {"step": 1}
    assert stm.get("plan", task_id="t-2") == {"step": 2}

    keys_t1 = stm.list_keys_by_task("t-1")
    assert "plan" in keys_t1


def test_stm_ttl_expires(stm: SqliteStmAdapter) -> None:
    stm.put("temp", "v", ttl_seconds=0.05)
    assert stm.get("temp") == "v"
    time.sleep(0.1)
    assert stm.get("temp") is None  # expiré, supprimé en lecture


def test_stm_clear_expired(stm: SqliteStmAdapter) -> None:
    stm.put("a", 1, ttl_seconds=0.05)
    stm.put("b", 2)  # pas de TTL, jamais expiré
    time.sleep(0.1)
    removed = stm.clear_expired()
    assert removed == 1
    assert stm.get("b") == 2


def test_ltm_state_persists_across_sessions(memory_service: MemoryService) -> None:
    saved = memory_service.save_state(
        "orch-1", "active", context={"running_tasks": 3}
    )
    assert saved.agent_id == "orch-1"

    loaded = memory_service.load_state("orch-1")
    assert loaded is not None
    assert loaded.state == "active"
    assert loaded.context == {"running_tasks": 3}


def _create_legacy_events_table(engine: SqlAlchemyEngine) -> None:
    with engine.engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type VARCHAR(64) NOT NULL,
                task_id VARCHAR(64) NULL,
                agent_id VARCHAR(64) NULL,
                session_id VARCHAR(64) NULL,
                payload JSON NOT NULL,
                created_at DATETIME NOT NULL
            )
        """))


def _add_identity_columns(engine: SqlAlchemyEngine) -> None:
    with engine.engine.begin() as connection:
        connection.execute(text(
            "ALTER TABLE events ADD COLUMN effect_id VARCHAR(128) NULL"
        ))
        connection.execute(text(
            "ALTER TABLE events ADD COLUMN payload_hash VARCHAR(64) NULL"
        ))


def _sqlite_schema(engine: SqlAlchemyEngine) -> tuple[tuple[object, ...], ...]:
    with engine.engine.connect() as connection:
        rows = connection.execute(text(
            "SELECT type, name, tbl_name, sql FROM sqlite_master "
            "WHERE tbl_name = 'events' ORDER BY type, name"
        )).all()
    return tuple(tuple(row) for row in rows)


def test_additive_migration_preserves_legacy_rows_and_is_idempotent(tmp_path) -> None:
    database = tmp_path / "legacy-events.sqlite3"
    engine = SqlAlchemyEngine(f"sqlite:///{database.as_posix()}")
    try:
        _create_legacy_events_table(engine)
        with engine.engine.begin() as connection:
            connection.execute(text("""
                INSERT INTO events (
                    event_type, task_id, agent_id, session_id, payload, created_at
                ) VALUES (
                    'legacy.event', 'task-old', NULL, NULL, '{"old": true}',
                    '2026-08-26 09:00:00'
                )
            """))

        add_idempotent_memory_effect(engine)
        add_idempotent_memory_effect(engine)

        inspector = inspect(engine.engine)
        columns = {item["name"] for item in inspector.get_columns("events")}
        indexes = {item["name"]: item for item in inspector.get_indexes("events")}
        assert {"effect_id", "payload_hash"}.issubset(columns)
        assert indexes["ux_events_effect_id"]["unique"]
        with engine.engine.connect() as connection:
            row = connection.execute(text(
                "SELECT event_type, task_id, effect_id, payload_hash FROM events"
            )).one()
        assert tuple(row) == ("legacy.event", "task-old", None, None)
        with pytest.raises(IntegrityError, match="effect identity pair mismatch"):
            with engine.engine.begin() as connection:
                connection.execute(text("""
                    INSERT INTO events (
                        event_type, payload, created_at, effect_id, payload_hash
                    ) VALUES (
                        'invalid.event', '{}', '2026-08-26 09:00:00',
                        'effect.invalid-pair', NULL
                    )
                """))
    finally:
        engine.dispose()


def test_migration_rejects_partial_incompatible_schema_without_further_change(
    tmp_path,
) -> None:
    database = tmp_path / "partial-events.sqlite3"
    engine = SqlAlchemyEngine(f"sqlite:///{database.as_posix()}")
    try:
        _create_legacy_events_table(engine)
        with engine.engine.begin() as connection:
            connection.execute(text(
                "ALTER TABLE events ADD COLUMN effect_id VARCHAR(128) NULL"
            ))
        with pytest.raises(RuntimeError, match="partial"):
            add_idempotent_memory_effect(engine)
        columns = {item["name"] for item in inspect(engine.engine).get_columns("events")}
        assert "effect_id" in columns and "payload_hash" not in columns
        assert "ux_events_effect_id" not in {
            item["name"] for item in inspect(engine.engine).get_indexes("events")
        }
    finally:
        engine.dispose()


@pytest.mark.parametrize(
    "index_ddl",
    (
        "CREATE UNIQUE INDEX ux_events_effect_id ON events(effect_id) WHERE 0",
        "CREATE UNIQUE INDEX ux_events_effect_id ON events(effect_id) "
        "WHERE effect_id IS NULL",
        "CREATE INDEX ux_events_effect_id ON events(effect_id)",
        "CREATE UNIQUE INDEX ux_events_effect_id ON events(event_type)",
    ),
    ids=("where-zero", "null-filter", "non-unique", "wrong-column"),
)
def test_migration_rejects_deceptive_homonymous_sqlite_index_without_mutation(
    tmp_path,
    index_ddl: str,
) -> None:
    database = tmp_path / "deceptive-index.sqlite3"
    engine = SqlAlchemyEngine(f"sqlite:///{database.as_posix()}")
    try:
        _create_legacy_events_table(engine)
        _add_identity_columns(engine)
        with engine.engine.begin() as connection:
            connection.execute(text(index_ddl))
        before = _sqlite_schema(engine)

        with pytest.raises(RuntimeError, match="incompatible SQLite index"):
            add_idempotent_memory_effect(engine)

        assert _sqlite_schema(engine) == before
    finally:
        engine.dispose()


@pytest.mark.parametrize(
    "trigger_ddl",
    (
        """
            CREATE TRIGGER trg_events_effect_identity_insert
            BEFORE INSERT ON events
            WHEN 0
            BEGIN
                SELECT RAISE(ABORT, 'events effect identity pair mismatch');
            END
        """,
        """
            CREATE TRIGGER trg_events_effect_identity_insert
            BEFORE INSERT ON events
            WHEN (NEW.effect_id IS NULL AND NEW.payload_hash IS NULL)
              OR (NEW.effect_id IS NOT NULL AND NEW.payload_hash IS NOT NULL)
            BEGIN
                SELECT RAISE(ABORT, 'events effect identity pair mismatch');
            END
        """,
        """
            CREATE TRIGGER trg_events_effect_identity_update
            BEFORE UPDATE OF effect_id ON events
            WHEN NEW.effect_id IS NULL AND NEW.payload_hash IS NOT NULL
            BEGIN
                SELECT RAISE(ABORT, 'events effect identity pair mismatch');
            END
        """,
    ),
    ids=("ineffective-insert", "inverted-insert", "incomplete-update"),
)
def test_migration_rejects_deceptive_homonymous_sqlite_trigger_without_mutation(
    tmp_path,
    trigger_ddl: str,
) -> None:
    database = tmp_path / "deceptive-trigger.sqlite3"
    engine = SqlAlchemyEngine(f"sqlite:///{database.as_posix()}")
    try:
        _create_legacy_events_table(engine)
        _add_identity_columns(engine)
        with engine.engine.begin() as connection:
            connection.execute(text(trigger_ddl))
        before = _sqlite_schema(engine)

        with pytest.raises(RuntimeError, match="incompatible SQLite trigger"):
            add_idempotent_memory_effect(engine)

        assert _sqlite_schema(engine) == before
        assert "ux_events_effect_id" not in {
            item["name"] for item in inspect(engine.engine).get_indexes("events")
        }
    finally:
        engine.dispose()


def test_migration_accepts_canonical_existing_sqlite_authorities_and_replays(
    tmp_path,
) -> None:
    database = tmp_path / "canonical-authorities.sqlite3"
    engine = SqlAlchemyEngine(f"sqlite:///{database.as_posix()}")
    try:
        _create_legacy_events_table(engine)
        _add_identity_columns(engine)
        with engine.engine.begin() as connection:
            connection.execute(text(_EFFECT_INDEX_DDL))
            connection.execute(text(_SQLITE_INSERT_TRIGGER_DDL))
            connection.execute(text(_SQLITE_UPDATE_TRIGGER_DDL))

        add_idempotent_memory_effect(engine)
        first_schema = _sqlite_schema(engine)
        add_idempotent_memory_effect(engine)
        assert _sqlite_schema(engine) == first_schema

        with engine.engine.begin() as connection:
            connection.execute(text("""
                INSERT INTO events (
                    event_type, payload, created_at, effect_id, payload_hash
                ) VALUES (
                    'canonical.event', '{}', '2026-08-26 09:00:00',
                    'effect.duplicate-proof',
                    'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
                )
            """))
        with pytest.raises(IntegrityError, match="events.effect_id"):
            with engine.engine.begin() as connection:
                connection.execute(text("""
                    INSERT INTO events (
                        event_type, payload, created_at, effect_id, payload_hash
                    ) VALUES (
                        'canonical.event', '{}', '2026-08-26 09:00:01',
                        'effect.duplicate-proof',
                        'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
                    )
                """))
    finally:
        engine.dispose()


@pytest.mark.parametrize(
    "expression",
    (
        "effect_id IS NULL OR payload_hash IS NULL",
        "effect_id IS NULL AND payload_hash IS NULL",
        "(effect_id IS NULL AND payload_hash IS NOT NULL) OR "
        "(effect_id IS NOT NULL AND payload_hash IS NULL)",
        "effect_id IS NOT NULL OR payload_hash IS NOT NULL",
    ),
)
def test_postgresql_pair_constraint_rejects_non_equivalent_definitions(
    expression: str,
) -> None:
    assert not _postgresql_pair_expression_is_exact(expression)


def test_postgresql_pair_constraint_accepts_exact_logical_equivalence() -> None:
    assert _postgresql_pair_expression_is_exact(
        "CHECK ((effect_id IS NULL AND payload_hash IS NULL) OR "
        "(effect_id IS NOT NULL AND payload_hash IS NOT NULL))"
    )
