"""Short-term memory adapter — stdlib sqlite3 (no SQLAlchemy).

STM is session/task scoped, lightweight, and ephemeral. Perfect for runtime
state, locks, and short-lived context. Use a path of ":memory:" for fully
in-process volatile storage.
"""
from __future__ import annotations

import json
import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Iterator

import structlog

logger = structlog.get_logger(__name__)


_SCHEMA = """
CREATE TABLE IF NOT EXISTS stm_kv (
    key          TEXT NOT NULL,
    value        TEXT NOT NULL,
    session_id   TEXT,
    task_id      TEXT,
    expires_at   REAL,
    created_at   REAL NOT NULL,
    PRIMARY KEY (key, session_id, task_id)
);
CREATE INDEX IF NOT EXISTS ix_stm_kv_session ON stm_kv(session_id);
CREATE INDEX IF NOT EXISTS ix_stm_kv_task    ON stm_kv(task_id);
CREATE INDEX IF NOT EXISTS ix_stm_kv_expires ON stm_kv(expires_at);
"""


class SqliteStmAdapter:
    """Adaptateur STM stdlib-only, sécurisé pour usage thread-local.

    Usage::

        stm = SqliteStmAdapter(":memory:")
        stm.put("plan", {"step": 1}, task_id="t-42")
        stm.get("plan", task_id="t-42")
    """

    def __init__(self, path: str = ":memory:") -> None:
        self._path = path
        self._conn = sqlite3.connect(path, isolation_level=None, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._conn.executescript(_SCHEMA)
        logger.info("stm.adapter.initialized", path=path)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def close(self) -> None:
        try:
            self._conn.close()
            logger.info("stm.adapter.closed", path=self._path)
        except Exception as exc:  # pragma: no cover
            logger.error("stm.adapter.close_failed", error=str(exc))

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        """Context manager pour transactions explicites."""
        try:
            self._conn.execute("BEGIN")
            yield self._conn
            self._conn.execute("COMMIT")
        except Exception:
            self._conn.execute("ROLLBACK")
            raise

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    def put(
        self,
        key: str,
        value: Any,
        *,
        session_id: str | None = None,
        task_id: str | None = None,
        ttl_seconds: float | None = None,
    ) -> None:
        """Stocke une paire clé/valeur. value est JSON-sérialisé."""
        encoded = json.dumps(value, default=str)
        now = time.time()
        expires_at = (now + ttl_seconds) if ttl_seconds is not None else None
        self._conn.execute(
            "INSERT OR REPLACE INTO stm_kv "
            "(key, value, session_id, task_id, expires_at, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (key, encoded, session_id, task_id, expires_at, now),
        )
        logger.debug(
            "stm.put",
            key=key,
            session_id=session_id,
            task_id=task_id,
            ttl_seconds=ttl_seconds,
        )

    def get(
        self,
        key: str,
        *,
        session_id: str | None = None,
        task_id: str | None = None,
        default: Any = None,
    ) -> Any:
        """Récupère une valeur. Renvoie default si absente ou expirée."""
        row = self._conn.execute(
            "SELECT value, expires_at FROM stm_kv "
            "WHERE key = ? AND IFNULL(session_id,'') = IFNULL(?, '') "
            "AND IFNULL(task_id,'') = IFNULL(?, '')",
            (key, session_id, task_id),
        ).fetchone()
        if row is None:
            return default
        if row["expires_at"] is not None and row["expires_at"] < time.time():
            self.delete(key, session_id=session_id, task_id=task_id)
            return default
        return json.loads(row["value"])

    def delete(
        self,
        key: str,
        *,
        session_id: str | None = None,
        task_id: str | None = None,
    ) -> None:
        self._conn.execute(
            "DELETE FROM stm_kv "
            "WHERE key = ? AND IFNULL(session_id,'') = IFNULL(?, '') "
            "AND IFNULL(task_id,'') = IFNULL(?, '')",
            (key, session_id, task_id),
        )
        logger.debug("stm.delete", key=key, session_id=session_id, task_id=task_id)

    def list_keys_by_task(self, task_id: str) -> list[str]:
        rows = self._conn.execute(
            "SELECT key FROM stm_kv WHERE task_id = ?", (task_id,)
        ).fetchall()
        return [r["key"] for r in rows]

    def list_keys_by_session(self, session_id: str) -> list[str]:
        rows = self._conn.execute(
            "SELECT key FROM stm_kv WHERE session_id = ?", (session_id,)
        ).fetchall()
        return [r["key"] for r in rows]

    def clear_expired(self) -> int:
        now = time.time()
        cur = self._conn.execute(
            "DELETE FROM stm_kv WHERE expires_at IS NOT NULL AND expires_at < ?",
            (now,),
        )
        removed = cur.rowcount or 0
        if removed:
            logger.info("stm.clear_expired", removed=removed)
        return removed

    def clear_all(self) -> None:
        """Vide toute la STM. À n'utiliser que dans les tests ou les resets contrôlés."""
        self._conn.execute("DELETE FROM stm_kv")
        logger.info("stm.clear_all")


__all__ = ["SqliteStmAdapter"]
