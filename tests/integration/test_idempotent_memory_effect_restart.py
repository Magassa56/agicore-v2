from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import text

from agicore.l2_memory.adapters.sqlalchemy_engine import SqlAlchemyEngine
from agicore.l2_memory.migrations.init_schema import init_schema
from agicore.l2_memory.schemas.event import IdempotentEventApplyStatus
from agicore.l2_memory.services.memory_service import MemoryService


OCCURRED_AT = datetime(2026, 8, 26, 10, 0, tzinfo=timezone.utc)


def _apply(memory: MemoryService):
    return memory.create_event_idempotent(
        effect_id="effect.restart-001",
        occurred_at=OCCURRED_AT,
        event_type="agent.execution.completed",
        task_id="task-restart",
        agent_id="execution-agent",
        session_id="session-restart",
        payload={"outcome_id": "outcome-restart", "committed": True},
    )


def test_file_sqlite_restart_preserves_idempotent_effect(tmp_path) -> None:
    database = tmp_path / "restart-authority.sqlite3"
    url = f"sqlite:///{database.as_posix()}"

    first_engine = SqlAlchemyEngine(url)
    init_schema(first_engine)
    first = _apply(MemoryService(first_engine))
    first_engine.dispose()

    second_engine = SqlAlchemyEngine(url)
    try:
        init_schema(second_engine)
        second = _apply(MemoryService(second_engine))
        with second_engine.session() as session:
            count = session.execute(text(
                "SELECT COUNT(*) FROM events WHERE effect_id = 'effect.restart-001'"
            )).scalar_one()
        assert first.status is IdempotentEventApplyStatus.APPLIED_NEW
        assert second.status is IdempotentEventApplyStatus.ALREADY_APPLIED
        assert second.event.id == first.event.id
        assert count == 1
    finally:
        second_engine.dispose()
