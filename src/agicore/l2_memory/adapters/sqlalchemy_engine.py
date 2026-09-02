"""SQLAlchemy engine and session factory for LTM.

Provides a clean abstraction over engine/session management. Tests use
in-memory SQLite. Production swaps to PostgreSQL by changing the URL.
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from threading import RLock
from typing import Iterator
from weakref import ReferenceType, WeakKeyDictionary, ref

import structlog
from sqlalchemy import Connection, Engine, create_engine, event
from sqlalchemy.exc import ResourceClosedError
from sqlalchemy.orm import Session, SessionTransaction, sessionmaker
from sqlalchemy.pool import StaticPool

logger = structlog.get_logger(__name__)


DEFAULT_LTM_URL = "sqlite:///./logs/agicore_ltm.sqlite3"


class _DeliverySessionCapability:
    """Opaque proof that a Session is inside one active delivery transaction."""

    __slots__ = (
        "_connection",
        "_driver_connection",
        "_root_transaction",
        "_revoked",
        "_session_ref",
        "_token",
        "_transaction_end_guards",
    )

    def __init__(
        self,
        *,
        session: Session,
        root_transaction: SessionTransaction,
        connection: Connection,
    ) -> None:
        self._session_ref: ReferenceType[Session] = ref(session)
        self._root_transaction = root_transaction
        self._connection = connection
        self._driver_connection = connection.connection.driver_connection
        self._token = object()
        self._revoked = False
        self._transaction_end_guards: tuple[tuple[str, object], ...] = ()


_DELIVERY_SESSION_CAPABILITIES: WeakKeyDictionary[
    Session, _DeliverySessionCapability
] = WeakKeyDictionary()
_DELIVERY_SESSION_CAPABILITIES_LOCK = RLock()


def _delivery_sqlite_authorizer(
    driver_connection,
    action_code: int,
    argument_one: str | None,
    _argument_two: str | None,
    _database_name: str | None,
    _trigger_name: str | None,
) -> int:
    """Revoke capabilities when SQLite itself observes a transaction end.

    This covers raw ``sqlite3.Connection.commit()`` / ``rollback()`` and raw
    transaction-control SQL. Replacing the engine-owned SQLite authorizer is
    outside the supported delivery-authority contract.
    """
    if action_code == sqlite3.SQLITE_TRANSACTION and argument_one in {
        "COMMIT",
        "ROLLBACK",
    }:
        with _DELIVERY_SESSION_CAPABILITIES_LOCK:
            matches = [
                (session, capability)
                for session, capability in _DELIVERY_SESSION_CAPABILITIES.items()
                if capability._driver_connection is driver_connection
            ]
        for session, capability in matches:
            _revoke_delivery_session_capability(session, capability)
    return sqlite3.SQLITE_OK


def _revoke_delivery_session_capability(
    session: Session, capability: _DeliverySessionCapability
) -> None:
    with _DELIVERY_SESSION_CAPABILITIES_LOCK:
        if capability._revoked:
            return
        if _DELIVERY_SESSION_CAPABILITIES.get(session) is capability:
            del _DELIVERY_SESSION_CAPABILITIES[session]
        capability._token = object()
        capability._revoked = True


def _remove_delivery_session_guards(
    capability: _DeliverySessionCapability,
) -> None:
    first_error: BaseException | None = None
    guards = capability._transaction_end_guards
    capability._transaction_end_guards = ()
    for event_name, guard in guards:
        try:
            if event.contains(capability._connection, event_name, guard):
                event.remove(capability._connection, event_name, guard)
        except BaseException as exc:
            if first_error is None:
                first_error = exc
    if first_error is not None:
        raise first_error


def _activate_delivery_session_capability(
    session: Session,
    *,
    root_transaction: SessionTransaction,
    connection: Connection,
) -> _DeliverySessionCapability:
    if (
        session.get_transaction() is not root_transaction
        or not root_transaction.is_active
        or connection.closed
        or connection.invalidated
        or not connection.in_transaction()
        or connection.dialect.name != "sqlite"
    ):
        raise RuntimeError("delivery transaction is not active")
    try:
        driver_connection = connection.connection.driver_connection
    except (AttributeError, TypeError) as exc:
        raise RuntimeError("delivery transaction is not active") from exc
    if getattr(driver_connection, "in_transaction", False) is not True:
        raise RuntimeError("delivery transaction is not active")
    capability = _DeliverySessionCapability(
        session=session,
        root_transaction=root_transaction,
        connection=connection,
    )
    with _DELIVERY_SESSION_CAPABILITIES_LOCK:
        if session in _DELIVERY_SESSION_CAPABILITIES:
            raise RuntimeError("delivery session capability is already active")
        _DELIVERY_SESSION_CAPABILITIES[session] = capability

    def revoke_after_transaction_end(
        _connection,
        _cursor,
        _statement,
        _parameters,
        _context,
        _many,
    ) -> None:
        if getattr(capability._driver_connection, "in_transaction", False) is not True:
            _revoke_delivery_session_capability(session, capability)

    def revoke_on_connection_end(_connection) -> None:
        _revoke_delivery_session_capability(session, capability)

    guards: tuple[tuple[str, object], ...] = (
        ("after_cursor_execute", revoke_after_transaction_end),
        ("commit", revoke_on_connection_end),
        ("rollback", revoke_on_connection_end),
    )
    installed: list[tuple[str, object]] = []
    try:
        for event_name, guard in guards:
            event.listen(connection, event_name, guard)
            installed.append((event_name, guard))
        capability._transaction_end_guards = tuple(installed)
    except BaseException:
        capability._transaction_end_guards = tuple(installed)
        try:
            _remove_delivery_session_guards(capability)
        finally:
            _revoke_delivery_session_capability(session, capability)
        raise
    return capability


def _deactivate_delivery_session_capability(
    session: Session, capability: _DeliverySessionCapability
) -> None:
    try:
        _remove_delivery_session_guards(capability)
    finally:
        _revoke_delivery_session_capability(session, capability)


def _require_delivery_session_capability(
    session: Session,
    *,
    expected: _DeliverySessionCapability | None = None,
    expected_token: object | None = None,
) -> _DeliverySessionCapability:
    """Fail closed unless ``session`` owns the current private SQLite capability."""
    try:
        dialect_name = session.get_bind().dialect.name
    except (AttributeError, TypeError) as exc:
        raise RuntimeError(
            "EventDeliveryRepository requires an active SQLite delivery_session"
        ) from exc
    if dialect_name != "sqlite":
        raise RuntimeError(
            "EventDeliveryRepository requires an active SQLite delivery_session"
        )
    with _DELIVERY_SESSION_CAPABILITIES_LOCK:
        capability = _DELIVERY_SESSION_CAPABILITIES.get(session)
    if capability is None or (
        expected is not None
        and (
            capability is not expected
            or expected_token is None
            or capability._token is not expected_token
        )
    ):
        raise RuntimeError(
            "EventDeliveryRepository requires an active SQLite delivery_session"
        )
    try:
        root_transaction = session.get_transaction()
        connection = capability._connection
    except (AttributeError, TypeError) as exc:
        raise RuntimeError(
            "EventDeliveryRepository requires an active SQLite delivery_session"
        ) from exc
    if (
        capability._session_ref() is not session
        or root_transaction is not capability._root_transaction
        or not capability._root_transaction.is_active
        or connection.closed
        or connection.invalidated
        or connection.dialect.name != "sqlite"
        or not connection.in_transaction()
    ):
        raise RuntimeError(
            "EventDeliveryRepository requires an active SQLite delivery_session"
        )
    try:
        driver_connection = connection.connection.driver_connection
    except (AttributeError, ResourceClosedError, TypeError) as exc:
        raise RuntimeError(
            "EventDeliveryRepository requires an active SQLite delivery_session"
        ) from exc
    if (
        driver_connection is not capability._driver_connection
        or getattr(driver_connection, "in_transaction", False) is not True
    ):
        raise RuntimeError(
            "EventDeliveryRepository requires an active SQLite delivery_session"
        )
    return capability


class SqlAlchemyEngine:
    """Wrapper sur engine SQLAlchemy + sessionmaker.

    Usage::

        from agicore.l2_memory.models import Base
        eng = SqlAlchemyEngine("sqlite:///:memory:")
        eng.create_all(Base.metadata)
        with eng.session() as s:
            ...
    """

    def __init__(
        self,
        url: str = DEFAULT_LTM_URL,
        *,
        echo: bool = False,
        future: bool = True,
        delivery_authority: bool = False,
        sqlite_busy_timeout_ms: int = 5_000,
    ) -> None:
        if not isinstance(delivery_authority, bool):
            raise ValueError("delivery_authority must be a boolean")
        if delivery_authority and not url.startswith("sqlite"):
            raise RuntimeError(
                "EventDelivery B1 authority supports SQLite backends only"
            )
        if (
            not isinstance(sqlite_busy_timeout_ms, int)
            or isinstance(sqlite_busy_timeout_ms, bool)
            or sqlite_busy_timeout_ms <= 0
        ):
            raise ValueError("sqlite_busy_timeout_ms must be a positive integer")
        connect_args: dict[str, object] = {}
        engine_kwargs: dict[str, object] = {}
        self._serialize_sessions = False
        self._delivery_authority = delivery_authority
        self._sqlite_delivery_authority = delivery_authority and url.startswith("sqlite")
        self._sqlite_memory = url.startswith("sqlite") and ":memory:" in url
        if url.startswith("sqlite"):
            connect_args["check_same_thread"] = False
            if delivery_authority:
                connect_args["timeout"] = sqlite_busy_timeout_ms / 1_000
            if self._sqlite_memory:
                engine_kwargs["poolclass"] = StaticPool
                self._serialize_sessions = True
        self._session_lock = RLock()
        self._engine: Engine = create_engine(
            url, echo=echo, future=future, connect_args=connect_args, **engine_kwargs
        )
        if self._sqlite_delivery_authority:
            busy_timeout = sqlite_busy_timeout_ms
            use_wal = not self._sqlite_memory

            @event.listens_for(self._engine, "connect")
            def _configure_delivery_connection(dbapi_connection, _record) -> None:
                dbapi_connection.set_authorizer(
                    lambda action, argument_one, argument_two, database, trigger: (
                        _delivery_sqlite_authorizer(
                            dbapi_connection,
                            action,
                            argument_one,
                            argument_two,
                            database,
                            trigger,
                        )
                    )
                )
                cursor = dbapi_connection.cursor()
                try:
                    cursor.execute("PRAGMA foreign_keys=ON")
                    cursor.execute(f"PRAGMA busy_timeout={busy_timeout}")
                    if use_wal:
                        mode = cursor.execute("PRAGMA journal_mode=WAL").fetchone()
                        if mode is None or str(mode[0]).lower() != "wal":
                            raise RuntimeError("SQLite WAL could not be enabled")
                finally:
                    cursor.close()
        self._sessionmaker = sessionmaker(
            bind=self._engine, autoflush=False, expire_on_commit=False, future=future
        )
        logger.info("ltm.engine.initialized", url=url)

    @property
    def engine(self) -> Engine:
        return self._engine

    @property
    def delivery_authority_enabled(self) -> bool:
        """Whether durable delivery transaction semantics were explicitly enabled."""
        return self._delivery_authority

    def create_all(self, metadata) -> None:
        """Crée toutes les tables déclarées dans le metadata fourni."""
        metadata.create_all(self._engine)
        logger.info("ltm.engine.create_all", tables=list(metadata.tables.keys()))

    def drop_all(self, metadata) -> None:
        """Supprime toutes les tables. Réservé aux tests / reset complet."""
        metadata.drop_all(self._engine)
        logger.warning("ltm.engine.drop_all", tables=list(metadata.tables.keys()))

    @contextmanager
    def session(self) -> Iterator[Session]:
        """Context manager: commit on success, rollback on exception."""
        if self._serialize_sessions:
            with self._session_lock:
                with self._session_context() as s:
                    yield s
            return

        with self._session_context() as s:
            yield s

    @contextmanager
    def delivery_session(self) -> Iterator[Session]:
        """Open one authoritative delivery transaction.

        SQLite uses ``BEGIN IMMEDIATE`` to serialize journal sequence, consumer
        ordering and anchor allocation across processes. Other L2 sessions retain
        their historical behavior; B1 rejects non-SQLite delivery authorities.
        """
        if not self._delivery_authority:
            raise RuntimeError("delivery authority mode was not enabled")
        if self._serialize_sessions:
            with self._session_lock:
                with self._delivery_session_context() as session:
                    yield session
            return
        with self._delivery_session_context() as session:
            yield session

    @contextmanager
    def _delivery_session_context(self) -> Iterator[Session]:
        session = self._sessionmaker()
        capability: _DeliverySessionCapability | None = None
        capability_token: object | None = None
        try:
            if not self._sqlite_delivery_authority:
                raise RuntimeError(
                    "EventDelivery B1 authority supports SQLite backends only"
                )
            connection = session.connection()
            connection.exec_driver_sql("BEGIN IMMEDIATE")
            root_transaction = session.get_transaction()
            if root_transaction is None:
                raise RuntimeError("delivery transaction did not start")
            capability = _activate_delivery_session_capability(
                session,
                root_transaction=root_transaction,
                connection=connection,
            )
            capability_token = capability._token
            yield session
            _require_delivery_session_capability(
                session,
                expected=capability,
                expected_token=capability_token,
            )
            session.commit()
        except BaseException:
            if capability is None or not capability._revoked:
                session.rollback()
            elif (
                not capability._connection.closed
                and capability._connection.in_transaction()
            ):
                capability._connection.rollback()
            raise
        finally:
            try:
                if capability is not None:
                    _deactivate_delivery_session_capability(session, capability)
            finally:
                session.close()

    @contextmanager
    def _session_context(self) -> Iterator[Session]:
        """Create one isolated SQLAlchemy Session for a single unit of work."""
        s = self._sessionmaker()
        try:
            yield s
            s.commit()
        except Exception:
            s.rollback()
            raise
        finally:
            s.close()

    def dispose(self) -> None:
        self._engine.dispose()
        logger.info("ltm.engine.disposed")


__all__ = ["SqlAlchemyEngine", "DEFAULT_LTM_URL"]
