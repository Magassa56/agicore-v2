"""Tests MemoryService — façade haut-niveau."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from threading import Barrier

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from agicore.l2_memory.adapters.sqlalchemy_engine import SqlAlchemyEngine
from agicore.l2_memory.migrations.init_schema import init_schema
from agicore.l2_memory.repositories.event_repository import EventRepository
from agicore.l2_memory.schemas.event import (
    IdempotentEventApplyStatus,
    IdempotentEventCreate,
    prepare_idempotent_event,
)
from agicore.l2_memory.services.memory_service import MemoryService


OCCURRED_AT = datetime(2026, 8, 26, 9, 30, tzinfo=timezone.utc)


def _apply(
    memory: MemoryService,
    *,
    effect_id: str = "effect.memory-001",
    occurred_at: datetime = OCCURRED_AT,
    event_type: str = "agent.execution.completed",
    task_id: str | None = "task-001",
    agent_id: str | None = "agent-001",
    session_id: str | None = "session-001",
    payload: dict[str, object] | None = None,
):
    return memory.create_event_idempotent(
        effect_id=effect_id,
        occurred_at=occurred_at,
        event_type=event_type,
        task_id=task_id,
        agent_id=agent_id,
        session_id=session_id,
        payload=payload if payload is not None else {"nested": {"value": 1}, "items": [1, 2]},
    )


def _event_count(engine: SqlAlchemyEngine) -> int:
    with engine.session() as session:
        return int(session.execute(text("SELECT COUNT(*) FROM events")).scalar_one())


def _prepared_event(
    *,
    effect_id: str = "effect.repository-001",
    occurred_at: datetime = OCCURRED_AT,
    event_type: str = "agent.execution.completed",
    task_id: str | None = "task-001",
    agent_id: str | None = "agent-001",
    session_id: str | None = "session-001",
    payload: dict[str, object] | None = None,
) -> IdempotentEventCreate:
    return prepare_idempotent_event(
        effect_id=effect_id,
        occurred_at=occurred_at,
        event_type=event_type,
        task_id=task_id,
        agent_id=agent_id,
        session_id=session_id,
        payload=payload if payload is not None else {"nested": {"value": 1}},
    )


def _repository_rejects_without_row(
    engine: SqlAlchemyEngine,
    dto: IdempotentEventCreate,
    *,
    match: str,
) -> None:
    with pytest.raises(ValueError, match=match):
        with engine.session() as session:
            EventRepository(session).create_idempotent(dto)
    assert _event_count(engine) == 0


def test_create_and_get_recent_events(memory_service: MemoryService) -> None:
    memory_service.create_event("trade.signal", task_id="t-1", payload={"x": 1})
    memory_service.create_event("trade.signal", task_id="t-2", payload={"x": 2})
    memory_service.create_event("system.heartbeat", agent_id="orch-1")

    all_recent = memory_service.get_recent_events(limit=10)
    assert len(all_recent) == 3

    only_signals = memory_service.get_recent_events(event_type="trade.signal")
    assert len(only_signals) == 2

    only_t1 = memory_service.get_recent_events(task_id="t-1")
    assert len(only_t1) == 1
    assert only_t1[0].payload == {"x": 1}


def test_save_and_load_state(memory_service: MemoryService) -> None:
    memory_service.save_state("trading_agent", "busy", context={"orders": 4})
    loaded = memory_service.load_state("trading_agent")
    assert loaded is not None
    assert loaded.state == "busy"
    assert loaded.context == {"orders": 4}


def test_load_state_returns_none_when_unknown(memory_service: MemoryService) -> None:
    assert memory_service.load_state("ghost-agent") is None


def test_execution_context_roundtrip(memory_service: MemoryService) -> None:
    memory_service.create_execution_context(
        task_id="task-z",
        session_id="sess-7",
        planner_state="planned",
    )
    ctx = memory_service.load_execution_context("task-z")
    assert ctx is not None
    assert ctx.session_id == "sess-7"
    assert ctx.status == "pending"

    updated = memory_service.update_execution_status("task-z", "completed")
    assert updated is not None
    assert updated.status == "completed"


def test_idempotent_event_applies_new_then_returns_authoritative_existing(
    memory_service: MemoryService,
    ltm_engine: SqlAlchemyEngine,
) -> None:
    first = _apply(memory_service)
    second = _apply(memory_service)

    assert first.status is IdempotentEventApplyStatus.APPLIED_NEW
    assert second.status is IdempotentEventApplyStatus.ALREADY_APPLIED
    assert second.event == first.event
    assert _event_count(ltm_engine) == 1
    assert first.event.occurred_at == OCCURRED_AT
    assert first.event.effect_id == "effect.memory-001"
    assert len(first.event.payload_hash) == 64
    with pytest.raises(FrozenInstanceError):
        first.status = IdempotentEventApplyStatus.CONFLICT  # type: ignore[misc]
    with pytest.raises(TypeError):
        first.event.payload["new"] = "forbidden"  # type: ignore[index]


def test_canonical_payload_key_order_does_not_change_identity(
    memory_service: MemoryService,
    ltm_engine: SqlAlchemyEngine,
) -> None:
    first = _apply(
        memory_service,
        effect_id="effect.memory-key-order",
        payload={"z": 1, "a": {"right": 2, "left": 1}},
    )
    second = _apply(
        memory_service,
        effect_id="effect.memory-key-order",
        payload={"a": {"left": 1, "right": 2}, "z": 1},
    )
    assert first.status is IdempotentEventApplyStatus.APPLIED_NEW
    assert second.status is IdempotentEventApplyStatus.ALREADY_APPLIED
    assert first.event.payload_hash == second.event.payload_hash
    assert _event_count(ltm_engine) == 1


@pytest.mark.parametrize(
    "changes",
    (
        {"payload": {"nested": {"value": 2}, "items": [1, 2]}},
        {"event_type": "agent.execution.rejected"},
        {"occurred_at": OCCURRED_AT + timedelta(microseconds=1)},
        {"task_id": "task-002"},
        {"agent_id": "agent-002"},
        {"session_id": "session-002"},
    ),
)
def test_idempotent_event_conflicts_on_any_semantic_change_without_mutation(
    memory_service: MemoryService,
    ltm_engine: SqlAlchemyEngine,
    changes: dict[str, object],
) -> None:
    first = _apply(memory_service)
    before = first.event
    conflict = _apply(memory_service, **changes)

    assert conflict.status is IdempotentEventApplyStatus.CONFLICT
    assert conflict.event == before
    assert _event_count(ltm_engine) == 1
    with ltm_engine.session() as session:
        authoritative = session.execute(text(
            "SELECT effect_id, payload_hash FROM events"
        )).one()
    assert authoritative == (before.effect_id, before.payload_hash)


def test_distinct_effect_ids_are_independent(
    memory_service: MemoryService,
    ltm_engine: SqlAlchemyEngine,
) -> None:
    left = _apply(memory_service, effect_id="effect.memory-left")
    right = _apply(memory_service, effect_id="effect.memory-right")
    assert left.status is right.status is IdempotentEventApplyStatus.APPLIED_NEW
    assert left.event.id != right.event.id
    assert _event_count(ltm_engine) == 2


def test_idempotent_event_rejects_naive_time_before_writing(
    memory_service: MemoryService,
    ltm_engine: SqlAlchemyEngine,
) -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        _apply(memory_service, occurred_at=datetime(2026, 8, 26, 9, 30))
    assert _event_count(ltm_engine) == 0


@pytest.mark.parametrize(
    "effect_id",
    ("", " Effect", "UPPERCASE", "effect/invalid", "effect.trailing-", "a" * 129),
)
def test_idempotent_event_rejects_noncanonical_effect_id_before_writing(
    memory_service: MemoryService,
    ltm_engine: SqlAlchemyEngine,
    effect_id: str,
) -> None:
    with pytest.raises(ValueError, match="effect_id"):
        _apply(memory_service, effect_id=effect_id)
    assert _event_count(ltm_engine) == 0


@pytest.mark.parametrize(
    "payload",
    (
        {"not_finite": float("nan")},
        {"set": {1, 2}},
        {"tuple": (1, 2)},
        {1: "non-string-key"},
        {"time": OCCURRED_AT},
    ),
)
def test_idempotent_event_rejects_noncanonical_payload_before_writing(
    memory_service: MemoryService,
    ltm_engine: SqlAlchemyEngine,
    payload: dict[object, object],
) -> None:
    with pytest.raises(ValueError, match="payload"):
        _apply(memory_service, payload=payload)  # type: ignore[arg-type]
    assert _event_count(ltm_engine) == 0


def test_idempotent_event_owns_a_deep_copy_of_input(
    memory_service: MemoryService,
) -> None:
    payload: dict[str, object] = {"nested": {"value": 1}, "items": [1, 2]}
    result = _apply(memory_service, payload=payload)
    nested = payload["nested"]
    items = payload["items"]
    assert isinstance(nested, dict) and isinstance(items, list)
    nested["value"] = 99
    items.append(3)

    stored = memory_service.get_recent_events(limit=1)[0]
    assert stored.payload == {"nested": {"value": 1}, "items": [1, 2]}
    assert dict(result.event.payload)["items"] == (1, 2)


def test_repository_rejects_forged_payload_hash_before_sql_lookup(
    ltm_engine: SqlAlchemyEngine,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    forged = _prepared_event().model_copy(update={"payload_hash": "f" * 64})
    with ltm_engine.session() as session:
        repository = EventRepository(session)

        def unexpected_lookup(effect_id: str):
            pytest.fail(f"unexpected SQL lookup for invalid DTO: {effect_id}")

        monkeypatch.setattr(repository, "_get_by_effect_id", unexpected_lookup)
        with pytest.raises(ValueError, match="payload_hash"):
            repository.create_idempotent(forged)
    assert _event_count(ltm_engine) == 0


def test_repository_rejects_model_construct_forgery_before_mutation(
    ltm_engine: SqlAlchemyEngine,
) -> None:
    forged = IdempotentEventCreate.model_construct(
        effect_id="FORGED",
        payload_hash="not-a-hash",
        occurred_at="not-a-datetime",
        event_type="",
        task_id=object(),
        agent_id=None,
        session_id=None,
        payload={"value": 1},
    )
    _repository_rejects_without_row(ltm_engine, forged, match="effect_id")


def test_repository_rejects_naive_datetime_before_mutation(
    ltm_engine: SqlAlchemyEngine,
) -> None:
    forged = _prepared_event().model_copy(
        update={"occurred_at": datetime(2026, 8, 26, 9, 30)}
    )
    _repository_rejects_without_row(ltm_engine, forged, match="timezone-aware")


def test_repository_rejects_noncanonical_effect_id_before_mutation(
    ltm_engine: SqlAlchemyEngine,
) -> None:
    forged = _prepared_event().model_copy(update={"effect_id": "Effect/Invalid"})
    _repository_rejects_without_row(ltm_engine, forged, match="effect_id")


@pytest.mark.parametrize(
    "invalid_payload",
    (
        {"number": float("nan")},
        {"unsupported": {1, 2}},
    ),
)
def test_repository_rejects_noncanonical_payload_before_mutation(
    ltm_engine: SqlAlchemyEngine,
    invalid_payload: dict[str, object],
) -> None:
    forged = _prepared_event().model_copy(update={"payload": invalid_payload})
    _repository_rejects_without_row(ltm_engine, forged, match="payload")


def test_repository_detects_payload_mutation_after_preparation(
    ltm_engine: SqlAlchemyEngine,
) -> None:
    prepared = _prepared_event()
    nested = prepared.payload["nested"]
    assert isinstance(nested, dict)
    nested["value"] = 999
    _repository_rejects_without_row(ltm_engine, prepared, match="payload_hash")


def test_repository_accepts_exact_reconstruction_and_stores_rebuilt_hash(
    ltm_engine: SqlAlchemyEngine,
) -> None:
    prepared = _prepared_event()
    with ltm_engine.session() as session:
        result = EventRepository(session).create_idempotent(prepared)
    assert result.status is IdempotentEventApplyStatus.APPLIED_NEW
    with ltm_engine.session() as session:
        stored = session.execute(text(
            "SELECT effect_id, payload_hash FROM events"
        )).one()
    assert stored.effect_id == prepared.effect_id
    assert stored.payload_hash == prepared.payload_hash


def test_repository_and_service_share_the_same_canonical_authority(
    memory_service: MemoryService,
    ltm_engine: SqlAlchemyEngine,
) -> None:
    prepared = _prepared_event(effect_id="effect.repository-service-equivalence")
    with ltm_engine.session() as session:
        direct = EventRepository(session).create_idempotent(prepared)
    via_service = memory_service.create_event_idempotent(
        effect_id=prepared.effect_id,
        occurred_at=prepared.occurred_at,
        event_type=prepared.event_type,
        task_id=prepared.task_id,
        agent_id=prepared.agent_id,
        session_id=prepared.session_id,
        payload=prepared.payload,
    )
    assert direct.status is IdempotentEventApplyStatus.APPLIED_NEW
    assert via_service.status is IdempotentEventApplyStatus.ALREADY_APPLIED
    assert via_service.event == direct.event
    assert _event_count(ltm_engine) == 1


def test_legacy_events_remain_non_idempotent_and_nullable(
    memory_service: MemoryService,
    ltm_engine: SqlAlchemyEngine,
) -> None:
    first = memory_service.create_event("legacy.event", payload={"same": True})
    second = memory_service.create_event("legacy.event", payload={"same": True})
    assert first.id != second.id
    assert _event_count(ltm_engine) == 2
    with ltm_engine.session() as session:
        rows = session.execute(text(
            "SELECT effect_id, payload_hash FROM events ORDER BY id"
        )).all()
    assert rows == [(None, None), (None, None)]


def test_lost_result_retry_does_not_insert_a_second_row(
    memory_service: MemoryService,
    ltm_engine: SqlAlchemyEngine,
) -> None:
    _apply(memory_service, effect_id="effect.memory-lost-result")
    recovered = _apply(memory_service, effect_id="effect.memory-lost-result")
    assert recovered.status is IdempotentEventApplyStatus.ALREADY_APPLIED
    assert _event_count(ltm_engine) == 1


def test_unrelated_sql_integrity_error_propagates_and_rolls_back(
    memory_service: MemoryService,
    ltm_engine: SqlAlchemyEngine,
) -> None:
    with ltm_engine.engine.begin() as connection:
        connection.execute(text("""
            CREATE TRIGGER reject_forced_event
            BEFORE INSERT ON events
            WHEN NEW.event_type = 'forced.sql-error'
            BEGIN
                SELECT RAISE(ABORT, 'forced unrelated integrity error');
            END
        """))
    with pytest.raises(IntegrityError, match="forced unrelated"):
        _apply(
            memory_service,
            effect_id="effect.memory-sql-error",
            event_type="forced.sql-error",
        )
    assert _event_count(ltm_engine) == 0
    recovered = _apply(memory_service, effect_id="effect.memory-after-rollback")
    assert recovered.status is IdempotentEventApplyStatus.APPLIED_NEW
    assert _event_count(ltm_engine) == 1


def test_two_threads_with_distinct_engines_insert_same_effect_once(tmp_path) -> None:
    database = tmp_path / "thread-authority.sqlite3"
    url = f"sqlite:///{database.as_posix()}"
    bootstrap = SqlAlchemyEngine(url)
    init_schema(bootstrap)
    bootstrap.dispose()
    barrier = Barrier(2)

    def worker() -> IdempotentEventApplyStatus:
        engine = SqlAlchemyEngine(url)
        try:
            memory = MemoryService(engine)
            barrier.wait(timeout=10)
            return _apply(memory, effect_id="effect.memory-thread-race").status
        finally:
            engine.dispose()

    with ThreadPoolExecutor(max_workers=2) as pool:
        statuses = tuple(pool.map(lambda _: worker(), range(2)))
    assert sorted(item.value for item in statuses) == ["ALREADY_APPLIED", "APPLIED_NEW"]
    verifier = SqlAlchemyEngine(url)
    try:
        assert _event_count(verifier) == 1
    finally:
        verifier.dispose()


def test_concurrent_different_payload_has_one_winner_and_one_conflict(tmp_path) -> None:
    database = tmp_path / "thread-conflict.sqlite3"
    url = f"sqlite:///{database.as_posix()}"
    bootstrap = SqlAlchemyEngine(url)
    init_schema(bootstrap)
    bootstrap.dispose()
    barrier = Barrier(2)

    def worker(value: int) -> IdempotentEventApplyStatus:
        engine = SqlAlchemyEngine(url)
        try:
            memory = MemoryService(engine)
            barrier.wait(timeout=10)
            return _apply(
                memory,
                effect_id="effect.memory-thread-conflict",
                payload={"winner": value},
            ).status
        finally:
            engine.dispose()

    with ThreadPoolExecutor(max_workers=2) as pool:
        statuses = tuple(pool.map(worker, (1, 2)))
    assert sorted(item.value for item in statuses) == ["APPLIED_NEW", "CONFLICT"]
    verifier = SqlAlchemyEngine(url)
    try:
        assert _event_count(verifier) == 1
    finally:
        verifier.dispose()
