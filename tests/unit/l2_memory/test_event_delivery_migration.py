from __future__ import annotations

from types import SimpleNamespace

from sqlalchemy import inspect, text

import pytest

from agicore.l2_memory.adapters.sqlalchemy_engine import SqlAlchemyEngine
from agicore.l2_memory.migrations.add_event_delivery_authority import (
    add_event_delivery_authority,
)
from agicore.l2_memory.migrations.init_schema import init_schema
from agicore.l2_memory.services.event_delivery_service import EventDeliveryService


TABLES = {
    "event_handler_manifests",
    "event_handler_manifest_entries",
    "event_bus_emissions",
    "event_handler_deliveries",
    "event_delivery_journal",
    "event_delivery_anchor",
}


def _engine(tmp_path, name: str = "delivery.sqlite3") -> SqlAlchemyEngine:
    return SqlAlchemyEngine(
        f"sqlite:///{(tmp_path / name).as_posix()}",
        delivery_authority=True,
        sqlite_busy_timeout_ms=7_000,
    )


def _schema(engine: SqlAlchemyEngine):
    with engine.engine.connect() as connection:
        return tuple(
            tuple(row)
            for row in connection.execute(
                text(
                    "SELECT type, name, tbl_name, sql FROM sqlite_master "
                    "WHERE tbl_name LIKE 'event_%' ORDER BY type, name"
                )
            ).all()
        )


def test_migration_creates_exact_tables_and_is_idempotent(tmp_path) -> None:
    engine = _engine(tmp_path)
    try:
        init_schema(engine)
        add_event_delivery_authority(engine)
        first = _schema(engine)
        add_event_delivery_authority(engine)
        assert _schema(engine) == first
        assert TABLES.issubset(set(inspect(engine.engine).get_table_names()))
        with engine.engine.connect() as connection:
            assert connection.exec_driver_sql("PRAGMA foreign_keys").scalar_one() == 1
            assert connection.exec_driver_sql("PRAGMA journal_mode").scalar_one() == "wal"
            assert connection.exec_driver_sql("PRAGMA busy_timeout").scalar_one() == 7000
    finally:
        engine.dispose()


def test_init_schema_can_opt_in_without_changing_default_contract(tmp_path) -> None:
    default = SqlAlchemyEngine(f"sqlite:///{(tmp_path / 'legacy.sqlite3').as_posix()}")
    try:
        tables = init_schema(default)
        assert TABLES.isdisjoint(tables)
        assert TABLES.isdisjoint(inspect(default.engine).get_table_names())
        with pytest.raises(RuntimeError, match="delivery authority mode"):
            add_event_delivery_authority(default)
    finally:
        default.dispose()

    enabled = _engine(tmp_path, "enabled.sqlite3")
    try:
        tables = init_schema(enabled, include_event_delivery=True)
        assert TABLES.issubset(tables)
    finally:
        enabled.dispose()


def test_partial_schema_is_rejected_before_additional_mutation(tmp_path) -> None:
    engine = _engine(tmp_path)
    try:
        with engine.engine.begin() as connection:
            connection.execute(text("CREATE TABLE event_delivery_anchor (x INTEGER)"))
        before = _schema(engine)
        with pytest.raises(RuntimeError, match="partial"):
            add_event_delivery_authority(engine)
        assert _schema(engine) == before
    finally:
        engine.dispose()


@pytest.mark.parametrize(
    "replacement",
    (
        "CREATE UNIQUE INDEX ux_event_emission_source "
        "ON event_bus_emissions(authority_id, source_identity) WHERE 0",
        "CREATE INDEX ux_event_emission_source "
        "ON event_bus_emissions(authority_id, source_identity)",
        "CREATE UNIQUE INDEX ux_event_emission_source "
        "ON event_bus_emissions(authority_id, outcome_id)",
    ),
    ids=("partial", "non-unique", "wrong-column"),
)
def test_deceptive_homonymous_index_is_rejected_without_mutation(
    tmp_path, replacement: str
) -> None:
    engine = _engine(tmp_path)
    try:
        add_event_delivery_authority(engine)
        with engine.engine.begin() as connection:
            connection.execute(text("DROP INDEX ux_event_emission_source"))
            connection.execute(text(replacement))
        before = _schema(engine)
        with pytest.raises(RuntimeError, match="incompatible SQLite delivery index"):
            add_event_delivery_authority(engine)
        assert _schema(engine) == before
    finally:
        engine.dispose()


def test_unknown_trigger_on_authority_table_is_rejected_without_mutation(tmp_path) -> None:
    engine = _engine(tmp_path)
    try:
        add_event_delivery_authority(engine)
        with engine.engine.begin() as connection:
            connection.execute(
                text(
                    "CREATE TRIGGER trg_event_delivery_journal_deceptive "
                    "BEFORE INSERT ON event_delivery_journal WHEN 0 "
                    "BEGIN SELECT RAISE(ABORT, 'never'); END"
                )
            )
        before = _schema(engine)
        with pytest.raises(RuntimeError, match="unexpected SQLite trigger"):
            add_event_delivery_authority(engine)
        assert _schema(engine) == before
    finally:
        engine.dispose()


def test_incompatible_complete_table_definition_is_rejected(tmp_path) -> None:
    engine = _engine(tmp_path)
    try:
        add_event_delivery_authority(engine)
        with engine.engine.begin() as connection:
            connection.execute(text("ALTER TABLE event_delivery_anchor RENAME TO old_anchor"))
            connection.execute(
                text(
                    "CREATE TABLE event_delivery_anchor ("
                    "authority_id VARCHAR(128) PRIMARY KEY, "
                    "authority_version VARCHAR(128) NOT NULL, "
                    "last_sequence INTEGER NOT NULL, last_hash VARCHAR(64) NOT NULL)"
                )
            )
            connection.execute(text("DROP TABLE old_anchor"))
        before = _schema(engine)
        with pytest.raises(RuntimeError, match="incompatible SQLite delivery table"):
            add_event_delivery_authority(engine)
        assert _schema(engine) == before
    finally:
        engine.dispose()


class _NonSqliteEngineBoundary:
    def __init__(self) -> None:
        self.dialect = SimpleNamespace(name="postgresql")
        self.begin_calls = 0

    def begin(self):
        self.begin_calls += 1
        raise AssertionError("non-SQLite authority must fail before opening a transaction")


class _NonSqliteAuthority:
    delivery_authority_enabled = True

    def __init__(self) -> None:
        self.engine = _NonSqliteEngineBoundary()


def test_non_sqlite_delivery_engine_is_rejected_before_engine_creation() -> None:
    with pytest.raises(RuntimeError, match="SQLite backends only"):
        SqlAlchemyEngine(
            "postgresql+psycopg://unused.invalid/agicore",
            delivery_authority=True,
        )


def test_non_sqlite_migration_is_rejected_before_transaction_or_table_creation() -> None:
    engine = _NonSqliteAuthority()
    with pytest.raises(RuntimeError, match="SQLite backends only"):
        add_event_delivery_authority(engine)  # type: ignore[arg-type]
    assert engine.engine.begin_calls == 0


def test_event_delivery_service_rejects_non_sqlite_authority_before_session() -> None:
    engine = _NonSqliteAuthority()
    with pytest.raises(RuntimeError, match="SQLite delivery authority mode"):
        EventDeliveryService(
            engine,  # type: ignore[arg-type]
            authority_id="event-delivery",
            authority_version="v1",
            runtime_profile_id="signal-loop-v1",
            manifest_version="v1",
        )
    assert engine.engine.begin_calls == 0
