from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from sqlalchemy import event, text

from agicore.core.event_delivery_contracts import (
    DispatchClass,
    HandlerManifestEntry,
    prepare_emission,
    prepare_manifest,
)
from agicore.l2_memory.adapters.sqlalchemy_engine import SqlAlchemyEngine
from agicore.l2_memory.migrations.add_event_delivery_authority import (
    add_event_delivery_authority,
)
from agicore.l2_memory.repositories.event_delivery_repository import (
    EventDeliveryRepository,
)
from agicore.l2_memory.services.event_delivery_service import EventDeliveryService


NOW = datetime(2026, 8, 27, 11, 0, tzinfo=timezone.utc)
HASH_A = "a" * 64
HASH_B = "b" * 64


def _repo(session) -> EventDeliveryRepository:
    return EventDeliveryRepository(
        session,
        authority_id="event-delivery",
        authority_version="v1",
    )


def _manifest(
    *,
    profile: str = "signal-loop-v1",
    event_type: str = "agent.execution.order.processed",
    version: str = "v1",
    handler_id: str = "signal-loop",
):
    return prepare_manifest(
        runtime_profile_id=profile,
        event_type=event_type,
        manifest_version=version,
        entries=(
            HandlerManifestEntry(
                handler_id=handler_id,
                handler_version="v1",
                required=True,
                ordinal=0,
                dispatch_class=DispatchClass.DIRECT,
            ),
        ),
    )


def _emission(
    manifest_hash: str,
    *,
    profile: str = "signal-loop-v1",
    event_type: str = "agent.execution.order.processed",
    version: str = "v1",
):
    return prepare_emission(
        authority_id="event-delivery",
        authority_version="v1",
        runtime_profile_id=profile,
        manifest_version=version,
        manifest_hash=manifest_hash,
        source_identity="receipt-direct",
        consumer_id="execution-agent",
        outcome_id="outcome-direct",
        outcome_hash=HASH_A,
        receipt_hash=HASH_B,
        source_sequence=1,
        event_type=event_type,
        occurred_at=NOW,
        accepted_at=NOW,
        payload={"value": 1},
    )


def _count(engine: SqlAlchemyEngine, table: str) -> int:
    with engine.session() as session:
        return int(session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one())


def _authority_snapshot(engine: SqlAlchemyEngine) -> tuple[object, ...]:
    tables = (
        "event_handler_manifests",
        "event_handler_manifest_entries",
        "event_bus_emissions",
        "event_handler_deliveries",
        "event_delivery_journal",
        "event_delivery_anchor",
    )
    with engine.session() as session:
        return tuple(
            (
                table,
                tuple(
                    tuple(row)
                    for row in session.execute(
                        text(f"SELECT * FROM {table} ORDER BY 1")
                    ).all()
                ),
            )
            for table in tables
        )


def test_repository_reconstructs_manifest_before_sql() -> None:
    engine = SqlAlchemyEngine("sqlite:///:memory:", delivery_authority=True)
    add_event_delivery_authority(engine)
    try:
        manifest = _manifest()
        forged = replace(manifest, manifest_hash="f" * 64)
        with pytest.raises(ValueError, match="canonical reconstruction"):
            with engine.delivery_session() as session:
                _repo(session).register_manifest(forged, registered_at=NOW)
        assert _count(engine, "event_handler_manifests") == 0
        assert _count(engine, "event_delivery_anchor") == 0
    finally:
        engine.dispose()


def test_repository_reconstructs_emission_before_lookup_or_mutation() -> None:
    engine = SqlAlchemyEngine("sqlite:///:memory:", delivery_authority=True)
    add_event_delivery_authority(engine)
    try:
        manifest = _manifest()
        with engine.delivery_session() as session:
            _repo(session).register_manifest(manifest, registered_at=NOW)
        forged = replace(_emission(manifest.manifest_hash), payload_hash="f" * 64)
        with pytest.raises(ValueError, match="canonical reconstruction"):
            with engine.delivery_session() as session:
                _repo(session).accept_emission(forged)
        assert _count(engine, "event_bus_emissions") == 0
        assert _count(engine, "event_handler_deliveries") == 0
        assert _count(engine, "event_delivery_journal") == 0
    finally:
        engine.dispose()


def test_direct_repository_acceptance_matches_service_authority_contract() -> None:
    engine = SqlAlchemyEngine("sqlite:///:memory:", delivery_authority=True)
    add_event_delivery_authority(engine)
    try:
        manifest = _manifest()
        with engine.delivery_session() as session:
            repository = _repo(session)
            repository.register_manifest(manifest, registered_at=NOW)
            resolved = repository.resolve_manifest(
                runtime_profile_id="signal-loop-v1",
                event_type="agent.execution.order.processed",
                manifest_version="v1",
            )
            result = repository.accept_emission(_emission(resolved.manifest_hash))
        assert result.emission.manifest_hash == manifest.manifest_hash
        assert len(result.deliveries) == 1
        assert _count(engine, "event_bus_emissions") == 1
        assert _count(engine, "event_handler_deliveries") == 1
        assert _count(engine, "event_delivery_journal") == 1
    finally:
        engine.dispose()


def test_direct_repository_rejects_canonical_unregistered_manifest_without_mutation() -> None:
    engine = SqlAlchemyEngine("sqlite:///:memory:", delivery_authority=True)
    add_event_delivery_authority(engine)
    try:
        manifest = _manifest()
        before = _authority_snapshot(engine)
        with pytest.raises(RuntimeError, match="no bus-owned manifest"):
            with engine.delivery_session() as session:
                _repo(session).accept_emission(_emission(manifest.manifest_hash))
        assert _authority_snapshot(engine) == before
    finally:
        engine.dispose()


def test_direct_repository_rejects_conflicting_canonical_manifest_hash_without_mutation() -> None:
    engine = SqlAlchemyEngine("sqlite:///:memory:", delivery_authority=True)
    add_event_delivery_authority(engine)
    try:
        registered = _manifest()
        conflicting = _manifest(handler_id="runtime-replay")
        with engine.delivery_session() as session:
            _repo(session).register_manifest(registered, registered_at=NOW)
        before = _authority_snapshot(engine)
        with pytest.raises(ValueError, match="bus-owned manifest"):
            with engine.delivery_session() as session:
                _repo(session).accept_emission(_emission(conflicting.manifest_hash))
        assert _authority_snapshot(engine) == before
    finally:
        engine.dispose()


@pytest.mark.parametrize(
    "substitute",
    (
        _manifest(handler_id="runtime-replay"),
        _manifest(version="v2"),
        _manifest(profile="replay-audit-v1"),
        _manifest(event_type="agent.execution.order.replayed"),
    ),
    ids=("same-identity", "other-version", "other-profile", "other-event"),
)
def test_repository_accept_emission_has_no_caller_manifest_substitution_boundary(
    substitute,
) -> None:
    engine = SqlAlchemyEngine("sqlite:///:memory:", delivery_authority=True)
    add_event_delivery_authority(engine)
    try:
        registered = _manifest()
        with engine.delivery_session() as session:
            repository = _repo(session)
            repository.register_manifest(registered, registered_at=NOW)
            if (
                substitute.runtime_profile_id,
                substitute.event_type,
                substitute.manifest_version,
            ) != (
                registered.runtime_profile_id,
                registered.event_type,
                registered.manifest_version,
            ):
                repository.register_manifest(
                    substitute, registered_at=NOW
                )
        before = _authority_snapshot(engine)
        with pytest.raises(TypeError, match="unexpected keyword argument 'manifest'"):
            with engine.delivery_session() as session:
                _repo(session).accept_emission(
                    _emission(registered.manifest_hash), manifest=substitute
                )
        assert _authority_snapshot(engine) == before
    finally:
        engine.dispose()


@pytest.mark.parametrize(
    "substitute",
    (
        _manifest(handler_id="runtime-replay"),
        _manifest(version="v2"),
        _manifest(profile="replay-audit-v1"),
        _manifest(event_type="agent.execution.order.replayed"),
    ),
    ids=("same-identity", "other-version", "other-profile", "other-event"),
)
def test_repository_rejects_foreign_manifest_hash_against_persisted_authority(
    substitute,
) -> None:
    engine = SqlAlchemyEngine("sqlite:///:memory:", delivery_authority=True)
    add_event_delivery_authority(engine)
    try:
        registered = _manifest()
        with engine.delivery_session() as session:
            repository = _repo(session)
            repository.register_manifest(registered, registered_at=NOW)
            if (
                substitute.runtime_profile_id,
                substitute.event_type,
                substitute.manifest_version,
            ) != (
                registered.runtime_profile_id,
                registered.event_type,
                registered.manifest_version,
            ):
                repository.register_manifest(substitute, registered_at=NOW)
        before = _authority_snapshot(engine)
        prepared_for_registered_identity = _emission(substitute.manifest_hash)
        with pytest.raises(ValueError, match="bus-owned manifest"):
            with engine.delivery_session() as session:
                _repo(session).accept_emission(prepared_for_registered_identity)
        assert _authority_snapshot(engine) == before
    finally:
        engine.dispose()


def test_repository_construction_with_ordinary_session_is_rejected_before_sql() -> None:
    engine = SqlAlchemyEngine("sqlite:///:memory:", delivery_authority=True)
    add_event_delivery_authority(engine)
    try:
        statements: list[str] = []

        @event.listens_for(engine.engine, "before_cursor_execute")
        def capture(_connection, _cursor, statement, _parameters, _context, _many):
            statements.append(statement)

        with engine.session() as session:
            with pytest.raises(RuntimeError, match="active SQLite delivery_session"):
                _repo(session)
        assert statements == []
    finally:
        engine.dispose()


def test_register_manifest_via_ordinary_session_is_rejected_without_mutation() -> None:
    engine = SqlAlchemyEngine("sqlite:///:memory:", delivery_authority=True)
    add_event_delivery_authority(engine)
    try:
        before = _authority_snapshot(engine)
        with engine.session() as session:
            with pytest.raises(RuntimeError, match="active SQLite delivery_session"):
                repository = _repo(session)
                repository.register_manifest(_manifest(), registered_at=NOW)
        assert _authority_snapshot(engine) == before
    finally:
        engine.dispose()


def test_accept_emission_via_ordinary_session_is_rejected_without_mutation() -> None:
    engine = SqlAlchemyEngine("sqlite:///:memory:", delivery_authority=True)
    add_event_delivery_authority(engine)
    try:
        manifest = _manifest()
        with engine.delivery_session() as session:
            _repo(session).register_manifest(manifest, registered_at=NOW)
        before = _authority_snapshot(engine)
        with engine.session() as session:
            with pytest.raises(RuntimeError, match="active SQLite delivery_session"):
                repository = _repo(session)
                repository.accept_emission(_emission(manifest.manifest_hash))
        assert _authority_snapshot(engine) == before
    finally:
        engine.dispose()


def test_repository_is_rejected_after_manual_commit_without_autobegin() -> None:
    engine = SqlAlchemyEngine("sqlite:///:memory:", delivery_authority=True)
    add_event_delivery_authority(engine)
    try:
        before = _authority_snapshot(engine)
        statements: list[str] = []

        @event.listens_for(engine.engine, "before_cursor_execute")
        def capture(_connection, _cursor, statement, _parameters, _context, _many):
            statements.append(statement)

        with pytest.raises(RuntimeError, match="active SQLite delivery_session"):
            with engine.delivery_session() as session:
                repository = _repo(session)
                root_transaction = session.get_transaction()
                assert root_transaction is not None
                session.commit()
                assert session.get_transaction() is None
                statement_count = len(statements)
                with pytest.raises(
                    RuntimeError, match="active SQLite delivery_session"
                ):
                    repository.pending_deliveries()
                assert len(statements) == statement_count
                assert session.get_transaction() is None
        assert _authority_snapshot(engine) == before
    finally:
        engine.dispose()


def test_repository_is_rejected_after_manual_rollback_without_autobegin() -> None:
    engine = SqlAlchemyEngine("sqlite:///:memory:", delivery_authority=True)
    add_event_delivery_authority(engine)
    try:
        before = _authority_snapshot(engine)
        statements: list[str] = []

        @event.listens_for(engine.engine, "before_cursor_execute")
        def capture(_connection, _cursor, statement, _parameters, _context, _many):
            statements.append(statement)

        with pytest.raises(RuntimeError, match="active SQLite delivery_session"):
            with engine.delivery_session() as session:
                repository = _repo(session)
                root_transaction = session.get_transaction()
                assert root_transaction is not None
                session.rollback()
                assert session.get_transaction() is None
                statement_count = len(statements)
                with pytest.raises(
                    RuntimeError, match="active SQLite delivery_session"
                ):
                    repository.pending_deliveries()
                assert len(statements) == statement_count
                assert session.get_transaction() is None
        assert _authority_snapshot(engine) == before
    finally:
        engine.dispose()


def test_repository_is_rejected_after_connection_commit_and_new_transaction() -> None:
    engine = SqlAlchemyEngine("sqlite:///:memory:", delivery_authority=True)
    add_event_delivery_authority(engine)
    try:
        before = _authority_snapshot(engine)
        statements: list[str] = []

        @event.listens_for(engine.engine, "before_cursor_execute")
        def capture(_connection, _cursor, statement, _parameters, _context, _many):
            statements.append(statement)

        with pytest.raises(RuntimeError, match="active SQLite delivery_session"):
            with engine.delivery_session() as session:
                repository = _repo(session)
                root_transaction = session.get_transaction()
                connection = session.connection()
                connection_transaction = connection.get_transaction()
                driver_connection = connection.connection.driver_connection
                assert root_transaction is not None
                assert connection_transaction is not None
                assert root_transaction.is_active
                assert connection.in_transaction()
                assert driver_connection.in_transaction is True

                connection.commit()
                assert session.get_transaction() is root_transaction
                assert root_transaction.is_active
                assert not connection.in_transaction()
                assert driver_connection.in_transaction is False

                replacement_transaction = connection.begin()
                assert replacement_transaction is not connection_transaction
                assert session.get_transaction() is root_transaction
                assert connection.in_transaction()
                assert driver_connection.in_transaction is False
                statement_count = len(statements)
                with pytest.raises(
                    RuntimeError, match="active SQLite delivery_session"
                ):
                    repository.pending_deliveries()
                assert len(statements) == statement_count
                assert session.get_transaction() is root_transaction
                assert connection.get_transaction() is replacement_transaction
                replacement_transaction.rollback()
        assert _authority_snapshot(engine) == before
    finally:
        engine.dispose()


def test_repository_is_rejected_after_connection_rollback_and_new_transaction() -> None:
    engine = SqlAlchemyEngine("sqlite:///:memory:", delivery_authority=True)
    add_event_delivery_authority(engine)
    try:
        before = _authority_snapshot(engine)
        statements: list[str] = []

        @event.listens_for(engine.engine, "before_cursor_execute")
        def capture(_connection, _cursor, statement, _parameters, _context, _many):
            statements.append(statement)

        with pytest.raises(RuntimeError, match="active SQLite delivery_session"):
            with engine.delivery_session() as session:
                repository = _repo(session)
                root_transaction = session.get_transaction()
                connection = session.connection()
                connection_transaction = connection.get_transaction()
                driver_connection = connection.connection.driver_connection
                assert root_transaction is not None
                assert connection_transaction is not None
                assert root_transaction.is_active
                assert connection.in_transaction()
                assert driver_connection.in_transaction is True

                connection.rollback()
                assert session.get_transaction() is root_transaction
                assert root_transaction.is_active
                assert not connection.in_transaction()
                assert driver_connection.in_transaction is False

                replacement_transaction = connection.begin()
                assert replacement_transaction is not connection_transaction
                assert session.get_transaction() is root_transaction
                assert connection.in_transaction()
                assert driver_connection.in_transaction is False
                statement_count = len(statements)
                with pytest.raises(
                    RuntimeError, match="active SQLite delivery_session"
                ):
                    repository.pending_deliveries()
                assert len(statements) == statement_count
                assert session.get_transaction() is root_transaction
                assert connection.get_transaction() is replacement_transaction
                replacement_transaction.rollback()
        assert _authority_snapshot(engine) == before
    finally:
        engine.dispose()


def test_repository_is_rejected_after_replacing_root_transaction() -> None:
    engine = SqlAlchemyEngine("sqlite:///:memory:", delivery_authority=True)
    add_event_delivery_authority(engine)
    try:
        before = _authority_snapshot(engine)
        statements: list[str] = []

        @event.listens_for(engine.engine, "before_cursor_execute")
        def capture(_connection, _cursor, statement, _parameters, _context, _many):
            statements.append(statement)

        with pytest.raises(RuntimeError, match="active SQLite delivery_session"):
            with engine.delivery_session() as session:
                repository = _repo(session)
                original_transaction = session.get_transaction()
                assert original_transaction is not None
                session.commit()
                replacement_transaction = session.begin()
                assert replacement_transaction is not original_transaction
                assert session.get_transaction() is replacement_transaction
                statement_count = len(statements)
                with pytest.raises(
                    RuntimeError, match="active SQLite delivery_session"
                ):
                    repository.pending_deliveries()
                assert len(statements) == statement_count
                assert session.get_transaction() is replacement_transaction
                replacement_transaction.rollback()
        assert _authority_snapshot(engine) == before
    finally:
        engine.dispose()


@pytest.mark.parametrize(
    "commit_statement",
    ("COMMIT", "/* explicit transaction end */ COMMIT"),
    ids=("plain", "comment-prefixed"),
)
def test_repository_is_rejected_after_direct_sql_commit(
    commit_statement: str,
) -> None:
    engine = SqlAlchemyEngine("sqlite:///:memory:", delivery_authority=True)
    add_event_delivery_authority(engine)
    try:
        before = _authority_snapshot(engine)
        statements: list[str] = []

        @event.listens_for(engine.engine, "before_cursor_execute")
        def capture(_connection, _cursor, statement, _parameters, _context, _many):
            statements.append(statement)

        with pytest.raises(RuntimeError, match="active SQLite delivery_session"):
            with engine.delivery_session() as session:
                repository = _repo(session)
                root_transaction = session.get_transaction()
                connection = session.connection()
                driver_connection = connection.connection.driver_connection
                assert root_transaction is not None
                assert driver_connection.in_transaction is True
                connection.exec_driver_sql(commit_statement)

                # SQLAlchemy retains a stale active wrapper here, while pysqlite
                # exposes that BEGIN IMMEDIATE has ended. Native state is authoritative.
                assert session.get_transaction() is root_transaction
                assert root_transaction.is_active
                assert connection.in_transaction()
                assert driver_connection.in_transaction is False
                statement_count = len(statements)
                with pytest.raises(
                    RuntimeError, match="active SQLite delivery_session"
                ):
                    repository.pending_deliveries()
                assert len(statements) == statement_count

                connection.exec_driver_sql("BEGIN IMMEDIATE")
                assert driver_connection.in_transaction is True
                statement_count = len(statements)
                with pytest.raises(
                    RuntimeError, match="active SQLite delivery_session"
                ):
                    repository.pending_deliveries()
                assert len(statements) == statement_count
        assert _authority_snapshot(engine) == before
    finally:
        engine.dispose()


@pytest.mark.parametrize("transaction_end", ("commit", "rollback"))
def test_repository_is_rejected_after_raw_dbapi_transaction_replacement(
    transaction_end: str,
) -> None:
    engine = SqlAlchemyEngine("sqlite:///:memory:", delivery_authority=True)
    add_event_delivery_authority(engine)
    try:
        before = _authority_snapshot(engine)
        statements: list[str] = []

        @event.listens_for(engine.engine, "before_cursor_execute")
        def capture(_connection, _cursor, statement, _parameters, _context, _many):
            statements.append(statement)

        with pytest.raises(RuntimeError, match="active SQLite delivery_session"):
            with engine.delivery_session() as session:
                repository = _repo(session)
                root_transaction = session.get_transaction()
                connection = session.connection()
                connection_transaction = connection.get_transaction()
                driver_connection = connection.connection.driver_connection
                assert root_transaction is not None
                assert connection_transaction is not None
                assert driver_connection.in_transaction is True

                getattr(driver_connection, transaction_end)()
                assert session.get_transaction() is root_transaction
                assert root_transaction.is_active
                assert connection.get_transaction() is connection_transaction
                assert connection.in_transaction()
                assert driver_connection.in_transaction is False

                # Raw DBAPI control is invisible to SQLAlchemy's transaction object.
                # The engine-owned SQLite authorizer makes the revocation durable.
                driver_connection.execute("BEGIN IMMEDIATE")
                assert session.get_transaction() is root_transaction
                assert connection.get_transaction() is connection_transaction
                assert connection.in_transaction()
                assert driver_connection.in_transaction is True
                statement_count = len(statements)
                with pytest.raises(
                    RuntimeError, match="active SQLite delivery_session"
                ):
                    repository.pending_deliveries()
                assert len(statements) == statement_count
                assert session.get_transaction() is root_transaction
                assert connection.get_transaction() is connection_transaction
        assert _authority_snapshot(engine) == before
    finally:
        engine.dispose()


def test_repository_remains_valid_during_original_delivery_transaction() -> None:
    engine = SqlAlchemyEngine("sqlite:///:memory:", delivery_authority=True)
    add_event_delivery_authority(engine)
    try:
        with engine.delivery_session() as session:
            repository = _repo(session)
            root_transaction = session.get_transaction()
            assert root_transaction is not None
            assert repository.pending_deliveries() == ()
            assert session.get_transaction() is root_transaction
            assert root_transaction.is_active
    finally:
        engine.dispose()


def test_repository_retained_after_delivery_session_exit_is_rejected() -> None:
    engine = SqlAlchemyEngine("sqlite:///:memory:", delivery_authority=True)
    add_event_delivery_authority(engine)
    try:
        with engine.delivery_session() as session:
            repository = _repo(session)
            repository.register_manifest(_manifest(), registered_at=NOW)
        before = _authority_snapshot(engine)
        with pytest.raises(RuntimeError, match="active SQLite delivery_session"):
            repository.pending_deliveries()
        assert _authority_snapshot(engine) == before
    finally:
        engine.dispose()


@pytest.mark.parametrize("failure", (RuntimeError, KeyboardInterrupt, SystemExit))
def test_delivery_session_capability_is_removed_after_every_base_exception(
    failure,
) -> None:
    engine = SqlAlchemyEngine("sqlite:///:memory:", delivery_authority=True)
    add_event_delivery_authority(engine)
    try:
        before = _authority_snapshot(engine)
        with pytest.raises(failure):
            with engine.delivery_session() as session:
                repository = _repo(session)
                repository.register_manifest(_manifest(), registered_at=NOW)
                raise failure("injected failure")
        with pytest.raises(RuntimeError, match="active SQLite delivery_session"):
            repository.pending_deliveries()
        assert _authority_snapshot(engine) == before
    finally:
        engine.dispose()


def test_delivery_session_capability_is_removed_after_commit_failure(
    monkeypatch,
) -> None:
    engine = SqlAlchemyEngine("sqlite:///:memory:", delivery_authority=True)
    add_event_delivery_authority(engine)
    try:
        before = _authority_snapshot(engine)

        def fail_commit() -> None:
            raise RuntimeError("injected commit failure")

        with pytest.raises(RuntimeError, match="injected commit failure"):
            with engine.delivery_session() as session:
                repository = _repo(session)
                monkeypatch.setattr(session, "commit", fail_commit)
        with pytest.raises(RuntimeError, match="active SQLite delivery_session"):
            repository.pending_deliveries()
        assert _authority_snapshot(engine) == before
    finally:
        engine.dispose()


def test_delivery_session_capability_is_removed_after_rollback_failure(
    monkeypatch,
) -> None:
    engine = SqlAlchemyEngine("sqlite:///:memory:", delivery_authority=True)
    add_event_delivery_authority(engine)
    try:
        before = _authority_snapshot(engine)

        def fail_rollback() -> None:
            raise RuntimeError("injected rollback failure")

        with pytest.raises(RuntimeError, match="injected rollback failure"):
            with engine.delivery_session() as session:
                repository = _repo(session)
                monkeypatch.setattr(session, "rollback", fail_rollback)
                raise ValueError("trigger rollback")
        with pytest.raises(RuntimeError, match="active SQLite delivery_session"):
            repository.pending_deliveries()
        assert _authority_snapshot(engine) == before
    finally:
        engine.dispose()


def test_fake_postgresql_session_is_rejected_before_any_operation() -> None:
    class ForbiddenPostgresqlSession:
        def __init__(self) -> None:
            self.calls: list[str] = []

        def get_bind(self):
            return SimpleNamespace(dialect=SimpleNamespace(name="postgresql"))

        def execute(self, *_args, **_kwargs):
            self.calls.append("execute")
            raise AssertionError("execute must not be called")

        def flush(self, *_args, **_kwargs):
            self.calls.append("flush")
            raise AssertionError("flush must not be called")

        def begin(self, *_args, **_kwargs):
            self.calls.append("begin")
            raise AssertionError("begin must not be called")

    session = ForbiddenPostgresqlSession()
    with pytest.raises(RuntimeError, match="active SQLite delivery_session"):
        EventDeliveryRepository(
            session,
            authority_id="event-delivery",
            authority_version="v1",
        )
    assert session.calls == []


def test_service_and_delivery_session_authority_path_remains_valid() -> None:
    engine = SqlAlchemyEngine("sqlite:///:memory:", delivery_authority=True)
    add_event_delivery_authority(engine)
    try:
        service = EventDeliveryService(
            engine,
            authority_id="event-delivery",
            authority_version="v1",
            runtime_profile_id="signal-loop-v1",
            manifest_version="v1",
        )
        registered = service.register_manifest(
            event_type="agent.execution.order.processed",
            entries=_manifest().entries,
            registered_at=NOW,
        )
        accepted = service.accept_emission(
            source_identity="receipt-direct",
            consumer_id="execution-agent",
            outcome_id="outcome-direct",
            outcome_hash=HASH_A,
            receipt_hash=HASH_B,
            source_sequence=1,
            event_type="agent.execution.order.processed",
            occurred_at=NOW,
            accepted_at=NOW,
            payload={"value": 1},
        )
        assert registered.manifest.manifest_hash == accepted.emission.manifest_hash
        assert _count(engine, "event_bus_emissions") == 1
    finally:
        engine.dispose()
