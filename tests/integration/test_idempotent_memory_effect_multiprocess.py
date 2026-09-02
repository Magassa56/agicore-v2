from __future__ import annotations

import multiprocessing
from datetime import datetime, timezone
from queue import Empty

from sqlalchemy import text

from agicore.l2_memory.adapters.sqlalchemy_engine import SqlAlchemyEngine
from agicore.l2_memory.migrations.init_schema import init_schema
from agicore.l2_memory.services.memory_service import MemoryService


OCCURRED_AT = datetime(2026, 8, 26, 10, 30, tzinfo=timezone.utc)


def _worker(database: str, value: int, start, ready, results) -> None:
    engine = SqlAlchemyEngine(f"sqlite:///{database}")
    try:
        service = MemoryService(engine)
        ready.put("ready")
        if not start.wait(timeout=30):
            results.put(("error", "start timeout"))
            return
        result = service.create_event_idempotent(
            effect_id="effect.multiprocess-001",
            occurred_at=OCCURRED_AT,
            event_type="agent.execution.completed",
            task_id="task-multiprocess",
            agent_id="execution-agent",
            session_id="session-multiprocess",
            payload={"value": value},
        )
        results.put(("ok", result.status.value, result.event.id))
    except BaseException as exc:
        results.put(("error", type(exc).__name__, str(exc)))
    finally:
        engine.dispose()


def _run_workers(database, values: tuple[int, int]):
    context = multiprocessing.get_context("spawn")
    start = context.Event()
    ready = context.Queue()
    results = context.Queue()
    processes = [
        context.Process(
            target=_worker,
            args=(database.as_posix(), value, start, ready, results),
        )
        for value in values
    ]
    for process in processes:
        process.start()
    try:
        assert [ready.get(timeout=30) for _ in processes] == ["ready", "ready"]
        start.set()
        observed = [results.get(timeout=30) for _ in processes]
    except Empty as exc:  # pragma: no cover - failure diagnostic
        raise AssertionError("multiprocess worker did not report") from exc
    finally:
        start.set()
        for process in processes:
            process.join(timeout=30)
            if process.is_alive():
                process.terminate()
                process.join(timeout=10)
    assert all(process.exitcode == 0 for process in processes)
    assert all(item[0] == "ok" for item in observed), observed
    return observed


def _bootstrap(database) -> str:
    url = f"sqlite:///{database.as_posix()}"
    engine = SqlAlchemyEngine(url)
    init_schema(engine)
    engine.dispose()
    return url


def _count(url: str) -> int:
    engine = SqlAlchemyEngine(url)
    try:
        with engine.session() as session:
            return int(session.execute(text(
                "SELECT COUNT(*) FROM events WHERE effect_id = 'effect.multiprocess-001'"
            )).scalar_one())
    finally:
        engine.dispose()


def test_two_spawned_processes_apply_same_effect_once(tmp_path) -> None:
    database = tmp_path / "multiprocess-same.sqlite3"
    url = _bootstrap(database)
    observed = _run_workers(database, (1, 1))
    assert sorted(item[1] for item in observed) == ["ALREADY_APPLIED", "APPLIED_NEW"]
    assert len({item[2] for item in observed}) == 1
    assert _count(url) == 1


def test_two_spawned_processes_conflict_on_different_payload(tmp_path) -> None:
    database = tmp_path / "multiprocess-conflict.sqlite3"
    url = _bootstrap(database)
    observed = _run_workers(database, (1, 2))
    assert sorted(item[1] for item in observed) == ["APPLIED_NEW", "CONFLICT"]
    assert len({item[2] for item in observed}) == 1
    assert _count(url) == 1
