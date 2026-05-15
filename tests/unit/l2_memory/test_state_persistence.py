"""Tests STM (sqlite_stm) + persistance LTM cross-session."""
from __future__ import annotations

import time

from agicore.l2_memory.adapters.sqlite_stm import SqliteStmAdapter
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
