from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import text

from agicore.core.event_delivery_contracts import (
    ApplyStatus,
    DispatchClass,
    HandlerManifestEntry,
)
from agicore.l2_memory.adapters.sqlalchemy_engine import SqlAlchemyEngine
from agicore.l2_memory.migrations.add_event_delivery_authority import (
    add_event_delivery_authority,
)
from agicore.l2_memory.services.event_delivery_service import EventDeliveryService


NOW = datetime(2026, 8, 27, 12, 0, tzinfo=timezone.utc)


def _service(engine: SqlAlchemyEngine) -> EventDeliveryService:
    return EventDeliveryService(
        engine,
        authority_id="event-delivery",
        authority_version="v1",
        runtime_profile_id="signal-loop-v1",
        manifest_version="v1",
    )


def _accept(
    service: EventDeliveryService,
    sequence: int = 1,
    *,
    source_identity: str | None = None,
):
    return service.accept_emission(
        source_identity=source_identity or f"receipt-{sequence}",
        consumer_id="execution-agent",
        outcome_id=f"outcome-{sequence}",
        outcome_hash="a" * 64,
        receipt_hash="b" * 64,
        source_sequence=sequence,
        event_type="agent.execution.order.processed",
        occurred_at=NOW + timedelta(seconds=sequence),
        accepted_at=NOW + timedelta(seconds=sequence),
        payload={"sequence": sequence},
    )


def test_restart_preserves_acceptance_claim_result_and_replay(tmp_path) -> None:
    database = tmp_path / "delivery-restart.sqlite3"
    url = f"sqlite:///{database.as_posix()}"
    first_engine = SqlAlchemyEngine(url, delivery_authority=True)
    add_event_delivery_authority(first_engine)
    first_service = _service(first_engine)
    first_service.register_manifest(
        event_type="agent.execution.order.processed",
        entries=(
            HandlerManifestEntry(
                handler_id="signal-loop",
                handler_version="v1",
                required=True,
                ordinal=0,
                dispatch_class=DispatchClass.DIRECT,
            ),
        ),
        registered_at=NOW,
    )
    accepted = _accept(first_service)
    claimed = first_service.claim(
        handler_effect_id=accepted.deliveries[0].handler_effect_id,
        worker_identity="worker-before-restart",
        claimed_at=NOW + timedelta(seconds=2),
    )
    first_service.record_synthetic_handler_result(
        handler_effect_id=accepted.deliveries[0].handler_effect_id,
        fencing_generation=claimed.delivery.fencing_generation,
        worker_identity="worker-before-restart",
        status=ApplyStatus.APPLIED_NEW,
        payload={"durable": True},
        applied_at=NOW + timedelta(seconds=3),
    )
    anchor_before = first_service.anchor()
    first_engine.dispose()

    second_engine = SqlAlchemyEngine(url, delivery_authority=True)
    try:
        add_event_delivery_authority(second_engine)
        second_service = _service(second_engine)
        retry = _accept(second_service)
        assert retry.status is ApplyStatus.ALREADY_APPLIED
        assert len(second_service.pending_deliveries()) == 1
        recovered = second_service.recover_claim(
            handler_effect_id=accepted.deliveries[0].handler_effect_id,
            observed_generation=claimed.delivery.fencing_generation,
            worker_identity="worker-after-restart",
            recovered_at=NOW + timedelta(seconds=4),
        )
        completed = second_service.complete_handler(
            handler_effect_id=accepted.deliveries[0].handler_effect_id,
            fencing_generation=recovered.delivery.fencing_generation,
            worker_identity="worker-after-restart",
            completed_at=NOW + timedelta(seconds=5),
        )
        assert completed.status == "COMPLETED"
        replay = second_service.replay()
        assert replay.emissions[0].status == "COMPLETED"
        assert replay.deliveries[0].result == {"durable": True}
        assert replay.anchor.last_sequence > anchor_before.last_sequence
        with second_engine.session() as session:
            assert session.execute(text("SELECT COUNT(*) FROM event_bus_emissions")).scalar_one() == 1
    finally:
        second_engine.dispose()


def test_restart_reconstructs_pending_order_from_source_sequence(tmp_path) -> None:
    database = tmp_path / "delivery-order-restart.sqlite3"
    url = f"sqlite:///{database.as_posix()}"
    engine = SqlAlchemyEngine(url, delivery_authority=True)
    add_event_delivery_authority(engine)
    service = _service(engine)
    service.register_manifest(
        event_type="agent.execution.order.processed",
        entries=(
            HandlerManifestEntry(
                handler_id="signal-loop",
                handler_version="v1",
                required=True,
                ordinal=0,
                dispatch_class=DispatchClass.DIRECT,
            ),
        ),
        registered_at=NOW,
    )
    for sequence, source_identity in (
        (1, "receipt-z"),
        (2, "receipt-a"),
        (3, "receipt-m"),
    ):
        _accept(service, sequence, source_identity=source_identity)
    engine.dispose()

    restarted = SqlAlchemyEngine(url, delivery_authority=True)
    try:
        replayed = _service(restarted)
        assert [item.source_sequence for item in replayed.pending_deliveries()] == [1, 2, 3]
        replay = replayed.replay()
        assert [item.source_sequence for item in replay.emissions] == [1, 2, 3]
    finally:
        restarted.dispose()
