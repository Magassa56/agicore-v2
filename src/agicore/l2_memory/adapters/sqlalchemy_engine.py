"""SQLAlchemy engine and session factory for LTM.

Provides a clean abstraction over engine/session management. Tests use
in-memory SQLite. Production swaps to PostgreSQL by changing the URL.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import structlog
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

logger = structlog.get_logger(__name__)


DEFAULT_LTM_URL = "sqlite:///./logs/agicore_ltm.sqlite3"


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
    ) -> None:
        connect_args: dict[str, object] = {}
        engine_kwargs: dict[str, object] = {}
        if url.startswith("sqlite"):
            connect_args["check_same_thread"] = False
            if ":memory:" in url:
                engine_kwargs["poolclass"] = StaticPool
        self._engine: Engine = create_engine(
            url, echo=echo, future=future, connect_args=connect_args, **engine_kwargs
        )
        self._sessionmaker = sessionmaker(
            bind=self._engine, autoflush=False, expire_on_commit=False, future=future
        )
        logger.info("ltm.engine.initialized", url=url)

    @property
    def engine(self) -> Engine:
        return self._engine

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
        """Context manager — commit auto si pas d'exception, rollback sinon."""
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
