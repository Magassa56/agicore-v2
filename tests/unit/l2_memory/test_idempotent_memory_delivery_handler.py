from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from threading import Barrier

import pytest
from sqlalchemy import text

from agicore.core.event_delivery_contracts import (
    ApplyStatus,
    DispatchClass,
    HandlerManifestEntry,
)
from agicore.l2_memory.adapters.sqlalchemy_engine import SqlAlchemyEngine
from agicore.l2_memory.migrations.init_schema import init_schema
from agicore.l2_memory.services.event_delivery_service import EventDeliveryService
from agicore.l2_memory.services.idempotent_memory_delivery_handler import (
    IdempotentMemoryDeliveryHandler,
)
from agicore.l2_memory.services.memory_service import MemoryService


NOW = datetime(2026, 9, 2, 18, 0, tzinfo=timezone.utc)


def _service(engine: SqlAlchemyEngine) -> EventDeliveryService:
    return EventDeliveryService(
        engine,
        authority_id="event-delivery",
        authority_version="v1",
        runtime_profile_id=IdempotentMemoryDeliveryHandler.RUNTIME_PROFILE_ID,
        manifest_version="v1",
    )


def _system(url: str = "sqlite:///:memory:") -> tuple[
    SqlAlchemyEngine,
    EventDeliveryService,
    IdempotentMemoryDeliveryHandler,
]:
    engine = SqlAlchemyEngine(url, delivery_authority=True)
    init_schema(engine, include_event_delivery=True)
    delivery = _service(engine)
    delivery.register_manifest(
        event_type="offline.audit.requested",
        entries=(
            HandlerManifestEntry(
                handler_id=IdempotentMemoryDeliveryHandler.HANDLER_ID,
                handler_version=IdempotentMemoryDeliveryHandler.HANDLER_VERSION,
                required=True,
                ordinal=0,
                dispatch_class=DispatchClass.DIRECT,
            ),
        ),
        registered_at=NOW,
    )
    delivery.accept_emission(
        source_identity="offline-source",
        consumer_id="memory-audit",
        outcome_id="audit-1",
        outcome_hash="a" * 64,
        receipt_hash="b" * 64,
        source_sequence=1,
        event_type="offline.audit.requested",
        occurred_at=NOW,
        accepted_at=NOW,
        payload={"sample": True, "count": 1},
    )
    handler = IdempotentMemoryDeliveryHandler(delivery, MemoryService(engine))
    return engine, delivery, handler


def _memory_count(engine: SqlAlchemyEngine) -> int:
    with engine.session() as session:
        return int(
            session.execute(
                text("SELECT COUNT(*) FROM events WHERE effect_id IS NOT NULL")
            ).scalar_one()
        )


def test_one_delivery_is_applied_completed_and_replayable() -> None:
    engine, delivery, handler = _system()
    try:
        result = handler.run_one(worker_identity="memory-worker", observed_at=NOW)

        assert result.status == "COMPLETED"
        assert result.delivery is not None
        assert result.delivery.status == "COMPLETED"
        assert result.delivery.result_status is ApplyStatus.APPLIED_CONFIRMED
        assert _memory_count(engine) == 1
        assert handler.run_one(
            worker_identity="memory-worker", observed_at=NOW
        ).status == "IDLE"
        replayed = delivery.replay()
        assert replayed.deliveries[0].status == "COMPLETED"
        assert replayed.emissions[0].status == "COMPLETED"
    finally:
        engine.dispose()


def test_restart_recovers_effect_without_duplicate_and_replays(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    url = f"sqlite:///{(tmp_path / 'sink-b2-restart.sqlite3').as_posix()}"
    first_engine, first_delivery, first_handler = _system(url)
    try:
        monkeypatch.setattr(
            first_delivery,
            "record_synthetic_handler_result",
            lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("simulated crash")),
        )
        with pytest.raises(RuntimeError, match="simulated crash"):
            first_handler.run_one(worker_identity="worker-before", observed_at=NOW)
        assert _memory_count(first_engine) == 1
    finally:
        first_engine.dispose()

    second_engine = SqlAlchemyEngine(url, delivery_authority=True)
    second_delivery = _service(second_engine)
    second_handler = IdempotentMemoryDeliveryHandler(
        second_delivery, MemoryService(second_engine)
    )
    try:
        recovered = second_handler.run_one(
            worker_identity="worker-after",
            observed_at=NOW,
            recover_stale_claim=True,
        )
        assert recovered.status == "COMPLETED"
        assert _memory_count(second_engine) == 1
        replayed = second_delivery.replay()
        assert replayed.deliveries[0].result_status is ApplyStatus.APPLIED_CONFIRMED
        assert replayed.deliveries[0].status == "COMPLETED"
        assert replayed.emissions[0].status == "COMPLETED"
    finally:
        second_engine.dispose()


def test_two_workers_create_only_one_memory_effect(tmp_path) -> None:
    url = f"sqlite:///{(tmp_path / 'sink-b2-concurrent.sqlite3').as_posix()}"
    bootstrap, _, _ = _system(url)
    bootstrap.dispose()
    barrier = Barrier(2)

    def work(worker_identity: str) -> str:
        engine = SqlAlchemyEngine(url, delivery_authority=True)
        handler = IdempotentMemoryDeliveryHandler(
            _service(engine), MemoryService(engine)
        )
        try:
            barrier.wait(timeout=10)
            return handler.run_one(
                worker_identity=worker_identity, observed_at=NOW
            ).status
        finally:
            engine.dispose()

    with ThreadPoolExecutor(max_workers=2) as pool:
        statuses = tuple(pool.map(work, ("memory-worker-a", "memory-worker-b")))

    verifier = SqlAlchemyEngine(url, delivery_authority=True)
    try:
        assert statuses.count("COMPLETED") == 1
        assert set(statuses).issubset({"COMPLETED", "IDLE", "UNAVAILABLE"})
        assert _memory_count(verifier) == 1
        replayed = _service(verifier).replay()
        assert replayed.deliveries[0].status == "COMPLETED"
        assert replayed.emissions[0].status == "COMPLETED"
    finally:
        verifier.dispose()


def test_retry_after_memory_effect_before_b1_result_has_stable_proof(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, delivery, handler = _system()
    original = delivery.record_synthetic_handler_result
    try:
        monkeypatch.setattr(
            delivery,
            "record_synthetic_handler_result",
            lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("simulated crash")),
        )
        with pytest.raises(RuntimeError, match="simulated crash"):
            handler.run_one(worker_identity="memory-worker", observed_at=NOW)
        assert _memory_count(engine) == 1
        assert delivery.pending_deliveries()[0].status == "CLAIMED"

        monkeypatch.setattr(delivery, "record_synthetic_handler_result", original)
        recovered = handler.run_one(
            worker_identity="memory-worker", observed_at=NOW
        )

        assert recovered.status == "COMPLETED"
        assert recovered.delivery is not None
        assert recovered.delivery.result_status is ApplyStatus.APPLIED_CONFIRMED
        assert _memory_count(engine) == 1
    finally:
        engine.dispose()
