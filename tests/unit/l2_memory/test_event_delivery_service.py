from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from threading import Barrier

import pytest
from sqlalchemy import event, text

from agicore.core.event_delivery_contracts import (
    ApplyStatus,
    ClaimStatus,
    DispatchClass,
    HandlerManifestEntry,
    JournalEventType,
    canonical_json_text,
    handler_effect_id,
    journal_event_hash,
    prepare_emission,
    sha256_canonical,
)
from agicore.l2_memory.adapters.sqlalchemy_engine import SqlAlchemyEngine
from agicore.l2_memory.migrations.add_event_delivery_authority import (
    add_event_delivery_authority,
)
from agicore.l2_memory.repositories.event_delivery_repository import (
    EventDeliveryRepository,
)
from agicore.l2_memory.services.event_delivery_service import EventDeliveryService


NOW = datetime(2026, 8, 27, 10, 0, tzinfo=timezone.utc)
HASH_A = "a" * 64
HASH_B = "b" * 64
EVENT_TYPE = "agent.execution.order.processed"


def _engine(url: str = "sqlite:///:memory:") -> SqlAlchemyEngine:
    engine = SqlAlchemyEngine(url, delivery_authority=True)
    add_event_delivery_authority(engine)
    return engine


def _service(
    engine: SqlAlchemyEngine,
    *,
    profile: str = "paper-trading-v1",
    manifest_version: str = "v1",
) -> EventDeliveryService:
    return EventDeliveryService(
        engine,
        authority_id="event-delivery",
        authority_version="v1",
        runtime_profile_id=profile,
        manifest_version=manifest_version,
    )


def _handler(
    handler_id: str,
    ordinal: int,
    *,
    required: bool = True,
) -> HandlerManifestEntry:
    return HandlerManifestEntry(
        handler_id=handler_id,
        handler_version="v1",
        required=required,
        ordinal=ordinal,
        dispatch_class=DispatchClass.DIRECT,
    )


def _register(
    service: EventDeliveryService,
    entries: tuple[HandlerManifestEntry, ...] = (),
) -> None:
    result = service.register_manifest(
        event_type=EVENT_TYPE,
        entries=entries,
        registered_at=NOW,
    )
    assert result.status in {ApplyStatus.APPLIED_NEW, ApplyStatus.ALREADY_APPLIED}


def _accept(
    service: EventDeliveryService,
    *,
    source_identity: str = "receipt-1",
    source_sequence: int = 1,
    payload: dict[str, object] | None = None,
    accepted_at: datetime = NOW,
):
    return service.accept_emission(
        source_identity=source_identity,
        consumer_id="execution-agent",
        outcome_id=f"outcome-{source_sequence}",
        outcome_hash=HASH_A,
        receipt_hash=HASH_B,
        source_sequence=source_sequence,
        event_type=EVENT_TYPE,
        occurred_at=NOW + timedelta(seconds=source_sequence),
        accepted_at=accepted_at,
        payload=payload or {"kind": "MARKET_FILLED", "sequence": source_sequence},
    )


def _counts(engine: SqlAlchemyEngine) -> dict[str, int]:
    tables = (
        "event_bus_emissions",
        "event_handler_deliveries",
        "event_delivery_journal",
    )
    with engine.session() as session:
        result = {
            name: int(session.execute(text(f"SELECT COUNT(*) FROM {name}")).scalar_one())
            for name in tables
        }
        result["anchor_sequence"] = int(
            session.execute(
                text(
                    "SELECT last_sequence FROM event_delivery_anchor "
                    "WHERE authority_id = 'event-delivery'"
                )
            ).scalar_one()
        )
    return result


def _emission_delivery_projection_snapshot(
    engine: SqlAlchemyEngine,
) -> tuple[tuple[object, ...], tuple[object, ...]]:
    with engine.engine.connect() as connection:
        emissions = tuple(
            tuple(row)
            for row in connection.execute(
                text("SELECT * FROM event_bus_emissions ORDER BY id")
            ).all()
        )
        deliveries = tuple(
            tuple(row)
            for row in connection.execute(
                text("SELECT * FROM event_handler_deliveries ORDER BY id")
            ).all()
        )
    return emissions, deliveries


def _complete_delivery(
    service: EventDeliveryService,
    handler_effect_digest: str,
    *,
    worker: str,
    offset: int,
) -> None:
    claimed = service.claim(
        handler_effect_id=handler_effect_digest,
        worker_identity=worker,
        claimed_at=NOW + timedelta(seconds=offset),
    )
    assert claimed.status is ClaimStatus.CLAIMED
    service.record_synthetic_handler_result(
        handler_effect_id=handler_effect_digest,
        fencing_generation=claimed.delivery.fencing_generation,
        worker_identity=worker,
        status=ApplyStatus.APPLIED_NEW,
        payload={"applied": True},
        applied_at=NOW + timedelta(seconds=offset + 1),
    )
    service.complete_handler(
        handler_effect_id=handler_effect_digest,
        fencing_generation=claimed.delivery.fencing_generation,
        worker_identity=worker,
        completed_at=NOW + timedelta(seconds=offset + 2),
    )


def _as_aware_datetime(value: object) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=timezone.utc)


def _rehash_journal(engine: SqlAlchemyEngine, mutate) -> None:
    with engine.engine.begin() as connection:
        rows = connection.execute(
            text(
                "SELECT authority_id, authority_version, sequence, event_type, "
                "emission_effect_id, handler_effect_id, fencing_generation, "
                "occurred_at, payload_json FROM event_delivery_journal "
                "ORDER BY sequence"
            )
        ).mappings().all()
        previous_hash = "0" * 64
        for original in rows:
            row = dict(original)
            payload = json.loads(row["payload_json"])
            mutate(row, payload)
            payload_json = canonical_json_text(payload)
            payload_hash = sha256_canonical(payload)
            event_hash = journal_event_hash(
                sequence=row["sequence"],
                authority_id=row["authority_id"],
                authority_version=row["authority_version"],
                event_type=JournalEventType(row["event_type"]),
                emission_effect_id=row["emission_effect_id"],
                handler_effect_digest=row["handler_effect_id"],
                fencing_generation=row["fencing_generation"],
                occurred_at=_as_aware_datetime(row["occurred_at"]),
                payload_hash=payload_hash,
                previous_hash=previous_hash,
            )
            connection.execute(
                text(
                    "UPDATE event_delivery_journal SET emission_effect_id = :emission, "
                    "handler_effect_id = :handler, fencing_generation = :generation, "
                    "payload_json = :payload, payload_hash = :payload_hash, "
                    "previous_hash = :previous_hash, event_hash = :event_hash "
                    "WHERE authority_id = :authority_id AND sequence = :sequence"
                ),
                {
                    "emission": row["emission_effect_id"],
                    "handler": row["handler_effect_id"],
                    "generation": row["fencing_generation"],
                    "payload": payload_json,
                    "payload_hash": payload_hash,
                    "previous_hash": previous_hash,
                    "event_hash": event_hash,
                    "authority_id": original["authority_id"],
                    "sequence": original["sequence"],
                },
            )
            previous_hash = event_hash
        connection.execute(
            text(
                "UPDATE event_delivery_anchor SET last_sequence = :sequence, "
                "last_hash = :last_hash WHERE authority_id = 'event-delivery'"
            ),
            {"sequence": len(rows), "last_hash": previous_hash},
        )


def _append_forged_claim(
    engine: SqlAlchemyEngine,
    *,
    emission_effect_digest: str,
    handler_effect_digest: str,
    worker_identity: str,
    claimed_at: datetime,
) -> None:
    payload = {"worker_identity": worker_identity}
    payload_json = canonical_json_text(payload)
    payload_hash = sha256_canonical(payload)
    with engine.engine.begin() as connection:
        anchor = connection.execute(
            text(
                "SELECT last_sequence, last_hash FROM event_delivery_anchor "
                "WHERE authority_id = 'event-delivery'"
            )
        ).one()
        sequence = int(anchor.last_sequence) + 1
        event_hash = journal_event_hash(
            sequence=sequence,
            authority_id="event-delivery",
            authority_version="v1",
            event_type=JournalEventType.HANDLER_CLAIMED,
            emission_effect_id=emission_effect_digest,
            handler_effect_digest=handler_effect_digest,
            fencing_generation=1,
            occurred_at=claimed_at,
            payload_hash=payload_hash,
            previous_hash=anchor.last_hash,
        )
        connection.execute(
            text(
                "INSERT INTO event_delivery_journal "
                "(authority_id, sequence, authority_version, event_type, "
                "emission_effect_id, handler_effect_id, fencing_generation, "
                "occurred_at, payload_json, payload_hash, previous_hash, event_hash) "
                "VALUES ('event-delivery', :sequence, 'v1', :event_type, "
                ":emission, :handler, 1, :occurred_at, :payload, :payload_hash, "
                ":previous_hash, :event_hash)"
            ),
            {
                "sequence": sequence,
                "event_type": JournalEventType.HANDLER_CLAIMED.value,
                "emission": emission_effect_digest,
                "handler": handler_effect_digest,
                "occurred_at": claimed_at,
                "payload": payload_json,
                "payload_hash": payload_hash,
                "previous_hash": anchor.last_hash,
                "event_hash": event_hash,
            },
        )
        connection.execute(
            text(
                "UPDATE event_handler_deliveries SET status = 'CLAIMED', "
                "fencing_generation = 1, worker_identity = :worker, "
                "claimed_at = :claimed_at WHERE handler_effect_id = :handler"
            ),
            {
                "worker": worker_identity,
                "claimed_at": claimed_at,
                "handler": handler_effect_digest,
            },
        )
        connection.execute(
            text(
                "UPDATE event_delivery_anchor SET last_sequence = :sequence, "
                "last_hash = :event_hash WHERE authority_id = 'event-delivery'"
            ),
            {"sequence": sequence, "event_hash": event_hash},
        )


def _forge_reversed_acceptance_order(
    engine: SqlAlchemyEngine,
    *,
    first_effect_id: str,
    second_effect_id: str,
) -> None:
    with engine.engine.connect() as connection:
        accepted_rows = connection.execute(
            text(
                "SELECT emission_effect_id, payload_json FROM event_delivery_journal "
                "WHERE event_type = 'EMISSION_ACCEPTED' ORDER BY sequence"
            )
        ).mappings().all()
    assert [row["emission_effect_id"] for row in accepted_rows] == [
        first_effect_id,
        second_effect_id,
    ]
    replacements: dict[str, tuple[str, int]] = {}
    projections: dict[str, dict[str, object]] = {}
    for row, forged_sequence in zip(accepted_rows, (3, 1), strict=True):
        accepted_payload = json.loads(row["payload_json"])
        projection = accepted_payload["emission"]
        prepared = prepare_emission(
            authority_id=projection["authority_id"],
            authority_version=projection["authority_version"],
            runtime_profile_id=projection["runtime_profile_id"],
            manifest_version=projection["manifest_version"],
            manifest_hash=projection["manifest_hash"],
            source_identity=projection["source_identity"],
            consumer_id=projection["consumer_id"],
            outcome_id=projection["outcome_id"],
            outcome_hash=projection["outcome_hash"],
            receipt_hash=projection["receipt_hash"],
            source_sequence=forged_sequence,
            event_type=projection["event_type"],
            occurred_at=_as_aware_datetime(projection["occurred_at"]),
            accepted_at=_as_aware_datetime(projection["accepted_at"]),
            payload=projection["payload"],
        )
        old_effect = str(row["emission_effect_id"])
        replacements[old_effect] = (prepared.emission_effect_id, forged_sequence)
        projection["source_sequence"] = forged_sequence
        projection["emission_effect_id"] = prepared.emission_effect_id
        projections[old_effect] = projection

    with engine.engine.begin() as connection:
        connection.execute(
            text("UPDATE event_bus_emissions SET source_sequence = source_sequence + 1000")
        )
        for old_effect, (new_effect, new_sequence) in replacements.items():
            connection.execute(
                text(
                    "UPDATE event_bus_emissions SET source_sequence = :sequence, "
                    "emission_effect_id = :new_effect WHERE emission_effect_id = :old_effect"
                ),
                {
                    "sequence": new_sequence,
                    "new_effect": new_effect,
                    "old_effect": old_effect,
                },
            )

    def mutate(row, payload):
        old_effect = row["emission_effect_id"]
        replacement = replacements.get(old_effect)
        if replacement is None:
            return
        row["emission_effect_id"] = replacement[0]
        if row["event_type"] == JournalEventType.EMISSION_ACCEPTED.value:
            payload["emission"] = projections[old_effect]

    _rehash_journal(engine, mutate)


def test_same_manifest_is_already_applied_and_different_content_conflicts() -> None:
    engine = _engine()
    try:
        service = _service(engine)
        entries = (_handler("signal-loop", 0),)
        first = service.register_manifest(
            event_type=EVENT_TYPE, entries=entries, registered_at=NOW
        )
        same = service.register_manifest(
            event_type=EVENT_TYPE,
            entries=entries,
            registered_at=NOW + timedelta(seconds=1),
        )
        conflict = service.register_manifest(
            event_type=EVENT_TYPE,
            entries=(_handler("runtime-replay", 0),),
            registered_at=NOW,
        )
        assert first.status is ApplyStatus.APPLIED_NEW
        assert same.status is ApplyStatus.ALREADY_APPLIED
        assert conflict.status is ApplyStatus.CONFLICT
        assert conflict.manifest.manifest_hash == first.manifest.manifest_hash
    finally:
        engine.dispose()


def test_new_manifest_version_is_explicit_and_nonretroactive() -> None:
    engine = _engine()
    try:
        v1 = _service(engine)
        _register(v1, (_handler("signal-loop", 0),))
        accepted = _accept(v1)
        v2 = _service(engine, manifest_version="v2")
        _register(v2, (_handler("runtime-replay", 0),))
        conflict = _accept(v2)
        assert conflict.status is ApplyStatus.CONFLICT
        assert conflict.emission.manifest_hash == accepted.emission.manifest_hash
    finally:
        engine.dispose()


def test_identical_emission_is_already_applied_with_one_sql_state() -> None:
    engine = _engine()
    try:
        service = _service(engine, profile="execution-base-v1")
        _register(service)
        first = _accept(service)
        second = _accept(service)
        assert first.status is ApplyStatus.APPLIED_NEW
        assert second.status is ApplyStatus.ALREADY_APPLIED
        assert second.emission.emission_effect_id == first.emission.emission_effect_id
        assert _counts(engine) == {
            "event_bus_emissions": 1,
            "event_handler_deliveries": 0,
            "event_delivery_journal": 2,
            "anchor_sequence": 2,
        }
    finally:
        engine.dispose()


def test_same_source_with_different_payload_conflicts_without_mutation() -> None:
    engine = _engine()
    try:
        service = _service(engine, profile="execution-base-v1")
        _register(service)
        first = _accept(service, payload={"value": 1})
        before = _counts(engine)
        conflict = _accept(service, payload={"value": 2})
        assert conflict.status is ApplyStatus.CONFLICT
        assert conflict.emission.payload == {"value": 1}
        assert _counts(engine) == before
        assert conflict.emission.emission_effect_id == first.emission.emission_effect_id
    finally:
        engine.dispose()


def test_retry_attempt_time_is_not_part_of_the_economic_identity() -> None:
    engine = _engine()
    try:
        service = _service(engine, profile="execution-base-v1")
        _register(service)
        first = _accept(service, accepted_at=NOW)
        retry = _accept(service, accepted_at=NOW + timedelta(hours=1))
        assert retry.status is ApplyStatus.ALREADY_APPLIED
        assert retry.emission.accepted_at == first.emission.accepted_at
        assert retry.emission.emission_effect_id == first.emission.emission_effect_id
        assert _counts(engine)["event_bus_emissions"] == 1
    finally:
        engine.dispose()


def test_source_sequence_zero_is_rejected_before_sql() -> None:
    engine = _engine()
    try:
        service = _service(engine, profile="execution-base-v1")
        _register(service)
        statements: list[str] = []

        def observe(_connection, _cursor, statement, _parameters, _context, _many):
            statements.append(statement)

        event.listen(engine.engine, "before_cursor_execute", observe)
        try:
            with pytest.raises(ValueError, match="positive integer"):
                _accept(service, source_sequence=0)
        finally:
            event.remove(engine.engine, "before_cursor_execute", observe)
        assert statements == []
        assert _counts(engine)["event_bus_emissions"] == 0
    finally:
        engine.dispose()


def test_regressive_source_sequence_is_rejected_without_mutation() -> None:
    engine = _engine()
    try:
        service = _service(engine, profile="signal-loop-v1")
        _register(service, (_handler("signal-loop", 0),))
        _accept(service, source_identity="receipt-3", source_sequence=3)
        before_counts = _counts(engine)
        before_anchor = service.anchor()
        before_replay = service.replay()
        with pytest.raises(ValueError, match="last accepted sequence"):
            _accept(service, source_identity="receipt-1", source_sequence=1)
        assert _counts(engine) == before_counts
        assert service.anchor() == before_anchor
        assert service.replay() == before_replay
    finally:
        engine.dispose()


def test_completed_higher_sequence_still_rejects_late_lower_sequence() -> None:
    engine = _engine()
    try:
        service = _service(engine, profile="signal-loop-v1")
        _register(service, (_handler("signal-loop", 0),))
        third = _accept(service, source_identity="receipt-3", source_sequence=3)
        _complete_delivery(
            service,
            third.deliveries[0].handler_effect_id,
            worker="worker-3",
            offset=10,
        )
        before = service.replay()
        with pytest.raises(ValueError, match="last accepted sequence"):
            _accept(service, source_identity="receipt-1", source_sequence=1)
        assert service.replay() == before
    finally:
        engine.dispose()


def test_increasing_sequences_retry_and_same_sequence_conflict_are_canonical() -> None:
    engine = _engine()
    try:
        service = _service(engine, profile="signal-loop-v1")
        _register(service, (_handler("signal-loop", 0),))
        tenth = _accept(service, source_identity="receipt-z", source_sequence=10)
        eleventh = _accept(service, source_identity="receipt-a", source_sequence=11)
        twelfth = _accept(service, source_identity="receipt-m", source_sequence=12)
        retry = _accept(service, source_identity="receipt-a", source_sequence=11)
        conflict = _accept(
            service,
            source_identity="receipt-other",
            source_sequence=11,
            payload={"kind": "FORGED", "sequence": 11},
        )
        assert retry.status is ApplyStatus.ALREADY_APPLIED
        assert retry.emission.emission_effect_id == eleventh.emission.emission_effect_id
        assert conflict.status is ApplyStatus.CONFLICT
        assert conflict.emission.emission_effect_id == eleventh.emission.emission_effect_id
        assert [item.source_sequence for item in service.pending_deliveries()] == [
            tenth.emission.source_sequence,
            eleventh.emission.source_sequence,
            twelfth.emission.source_sequence,
        ]
    finally:
        engine.dispose()


def test_zero_required_handlers_completes_immediately_while_best_effort_is_pending() -> None:
    engine = _engine()
    try:
        service = _service(engine, profile="execution-base-v1")
        _register(service, (_handler("runtime-monitor", 0, required=False),))
        result = _accept(service)
        assert result.emission.status == "COMPLETED"
        assert result.emission_accepted_hash != result.emission_completed_hash
        assert len(result.deliveries) == 1
        assert result.deliveries[0].status == "PENDING"
        replay = service.replay()
        assert replay.emissions[0].status == "COMPLETED"
        assert replay.deliveries[0].status == "PENDING"
    finally:
        engine.dispose()


def test_two_required_handlers_block_completion_until_both_complete() -> None:
    engine = _engine()
    try:
        service = _service(engine)
        _register(
            service,
            (_handler("signal-loop", 0), _handler("runtime-replay", 1)),
        )
        accepted = _accept(service)
        first, second = accepted.deliveries
        claim = service.claim(
            handler_effect_id=first.handler_effect_id,
            worker_identity="worker-1",
            claimed_at=NOW + timedelta(seconds=2),
        )
        service.record_synthetic_handler_result(
            handler_effect_id=first.handler_effect_id,
            fencing_generation=claim.delivery.fencing_generation,
            worker_identity="worker-1",
            status=ApplyStatus.APPLIED_NEW,
            payload={"applied": True},
            applied_at=NOW + timedelta(seconds=3),
        )
        service.complete_handler(
            handler_effect_id=first.handler_effect_id,
            fencing_generation=claim.delivery.fencing_generation,
            worker_identity="worker-1",
            completed_at=NOW + timedelta(seconds=4),
        )
        replay = service.replay()
        assert replay.emissions[0].status == "ACCEPTED"

        claim2 = service.claim(
            handler_effect_id=second.handler_effect_id,
            worker_identity="worker-2",
            claimed_at=NOW + timedelta(seconds=5),
        )
        service.record_synthetic_handler_result(
            handler_effect_id=second.handler_effect_id,
            fencing_generation=claim2.delivery.fencing_generation,
            worker_identity="worker-2",
            status=ApplyStatus.ALREADY_APPLIED,
            payload={"applied": True},
            applied_at=NOW + timedelta(seconds=6),
        )
        service.complete_handler(
            handler_effect_id=second.handler_effect_id,
            fencing_generation=claim2.delivery.fencing_generation,
            worker_identity="worker-2",
            completed_at=NOW + timedelta(seconds=7),
        )
        replay = service.replay()
        assert replay.emissions[0].status == "COMPLETED"
        assert [item.status for item in replay.deliveries] == ["COMPLETED", "COMPLETED"]
    finally:
        engine.dispose()


def test_best_effort_conflict_never_blocks_required_completion() -> None:
    engine = _engine()
    try:
        service = _service(engine)
        _register(
            service,
            (
                _handler("signal-loop", 0),
                _handler("runtime-monitor", 1, required=False),
            ),
        )
        accepted = _accept(service)
        required, observer = accepted.deliveries
        required_claim = service.claim(
            handler_effect_id=required.handler_effect_id,
            worker_identity="worker-required",
            claimed_at=NOW + timedelta(seconds=2),
        )
        service.record_synthetic_handler_result(
            handler_effect_id=required.handler_effect_id,
            fencing_generation=required_claim.delivery.fencing_generation,
            worker_identity="worker-required",
            status=ApplyStatus.APPLIED_NEW,
            payload={},
            applied_at=NOW + timedelta(seconds=3),
        )
        service.complete_handler(
            handler_effect_id=required.handler_effect_id,
            fencing_generation=required_claim.delivery.fencing_generation,
            worker_identity="worker-required",
            completed_at=NOW + timedelta(seconds=4),
        )
        observer_claim = service.claim(
            handler_effect_id=observer.handler_effect_id,
            worker_identity="worker-observer",
            claimed_at=NOW + timedelta(seconds=5),
        )
        service.record_synthetic_handler_result(
            handler_effect_id=observer.handler_effect_id,
            fencing_generation=observer_claim.delivery.fencing_generation,
            worker_identity="worker-observer",
            status=ApplyStatus.CONFLICT,
            payload={"reason": "synthetic"},
            applied_at=NOW + timedelta(seconds=6),
        )
        replay = service.replay()
        assert replay.emissions[0].status == "COMPLETED"
        assert [item.status for item in replay.deliveries] == ["COMPLETED", "CONFLICT"]
    finally:
        engine.dispose()


def test_explicit_recovery_fences_old_worker() -> None:
    engine = _engine()
    try:
        service = _service(engine, profile="signal-loop-v1")
        _register(service, (_handler("signal-loop", 0),))
        delivery = _accept(service).deliveries[0]
        first = service.claim(
            handler_effect_id=delivery.handler_effect_id,
            worker_identity="worker-old",
            claimed_at=NOW + timedelta(seconds=2),
        )
        recovered = service.recover_claim(
            handler_effect_id=delivery.handler_effect_id,
            observed_generation=first.delivery.fencing_generation,
            worker_identity="worker-new",
            recovered_at=NOW + timedelta(seconds=3),
        )
        assert recovered.status is ClaimStatus.CLAIMED
        assert recovered.delivery.fencing_generation == first.delivery.fencing_generation + 1
        with pytest.raises(RuntimeError, match="stale or foreign"):
            service.record_synthetic_handler_result(
                handler_effect_id=delivery.handler_effect_id,
                fencing_generation=first.delivery.fencing_generation,
                worker_identity="worker-old",
                status=ApplyStatus.APPLIED_NEW,
                payload={},
                applied_at=NOW + timedelta(seconds=4),
            )
        applied = service.record_synthetic_handler_result(
            handler_effect_id=delivery.handler_effect_id,
            fencing_generation=recovered.delivery.fencing_generation,
            worker_identity="worker-new",
            status=ApplyStatus.ALREADY_APPLIED,
            payload={},
            applied_at=NOW + timedelta(seconds=4),
        )
        assert applied.status == "APPLIED"
    finally:
        engine.dispose()


def test_stale_observed_generation_cannot_recover_claim() -> None:
    engine = _engine()
    try:
        service = _service(engine, profile="signal-loop-v1")
        _register(service, (_handler("signal-loop", 0),))
        delivery = _accept(service).deliveries[0]
        service.claim(
            handler_effect_id=delivery.handler_effect_id,
            worker_identity="worker-1",
            claimed_at=NOW,
        )
        result = service.recover_claim(
            handler_effect_id=delivery.handler_effect_id,
            observed_generation=99,
            worker_identity="worker-2",
            recovered_at=NOW + timedelta(seconds=1),
        )
        assert result.status is ClaimStatus.UNAVAILABLE
        assert result.delivery.fencing_generation == 1
    finally:
        engine.dispose()


@pytest.mark.parametrize(
    "statement_fragment",
    (
        "INSERT INTO event_bus_emissions",
        "INSERT INTO event_handler_deliveries",
        "INSERT INTO event_delivery_journal",
        "UPDATE event_delivery_anchor",
    ),
)
def test_acceptance_failure_at_each_sql_stage_leaves_no_partial_state(
    tmp_path, statement_fragment: str
) -> None:
    database = tmp_path / "atomic.sqlite3"
    engine = _engine(f"sqlite:///{database.as_posix()}")
    try:
        service = _service(engine, profile="signal-loop-v1")
        _register(service, (_handler("signal-loop", 0),))
        fired = False

        def fail_once(_connection, _cursor, statement, _parameters, _context, _many):
            nonlocal fired
            if not fired and statement_fragment.lower() in statement.lower():
                fired = True
                raise RuntimeError("injected acceptance failure")

        event.listen(engine.engine, "before_cursor_execute", fail_once)
        try:
            with pytest.raises(RuntimeError, match="injected"):
                _accept(service)
        finally:
            event.remove(engine.engine, "before_cursor_execute", fail_once)
        assert fired
        assert _counts(engine) == {
            "event_bus_emissions": 0,
            "event_handler_deliveries": 0,
            "event_delivery_journal": 0,
            "anchor_sequence": 0,
        }
    finally:
        engine.dispose()


def test_causal_pending_order_survives_retry_and_ignores_lexical_hash_order() -> None:
    engine = _engine()
    try:
        service = _service(engine, profile="signal-loop-v1")
        _register(service, (_handler("signal-loop", 0),))
        first = _accept(service, source_identity="receipt-a", source_sequence=1)
        second = _accept(service, source_identity="receipt-m", source_sequence=2)
        third = _accept(service, source_identity="receipt-z", source_sequence=3)
        assert [item.source_sequence for item in service.pending_deliveries()] == [1, 2, 3]
        blocked = service.claim(
            handler_effect_id=second.deliveries[0].handler_effect_id,
            worker_identity="worker-2",
            claimed_at=NOW + timedelta(seconds=10),
        )
        assert blocked.status is ClaimStatus.UNAVAILABLE
        assert [item.source_sequence for item in service.pending_deliveries()] == [1, 2, 3]
        assert first.emission.accepted_sequence < third.emission.accepted_sequence
    finally:
        engine.dispose()


def test_claim_rejects_later_source_until_predecessor_completed() -> None:
    engine = _engine()
    try:
        service = _service(engine, profile="signal-loop-v1")
        _register(service, (_handler("signal-loop", 0),))
        first = _accept(service, source_identity="receipt-1", source_sequence=1)
        second = _accept(service, source_identity="receipt-2", source_sequence=2)
        blocked = service.claim(
            handler_effect_id=second.deliveries[0].handler_effect_id,
            worker_identity="worker-2",
            claimed_at=NOW + timedelta(seconds=10),
        )
        assert blocked.status is ClaimStatus.UNAVAILABLE
        assert blocked.delivery.status == "PENDING"
        _complete_delivery(
            service,
            first.deliveries[0].handler_effect_id,
            worker="worker-1",
            offset=11,
        )
        claimed = service.claim(
            handler_effect_id=second.deliveries[0].handler_effect_id,
            worker_identity="worker-2",
            claimed_at=NOW + timedelta(seconds=20),
        )
        assert claimed.status is ClaimStatus.CLAIMED
    finally:
        engine.dispose()


def test_claim_causal_rejection_changes_nothing() -> None:
    engine = _engine()
    try:
        service = _service(engine, profile="signal-loop-v1")
        _register(service, (_handler("signal-loop", 0),))
        _accept(service, source_identity="receipt-1", source_sequence=1)
        second = _accept(service, source_identity="receipt-2", source_sequence=2)
        before_counts = _counts(engine)
        before_anchor = service.anchor()
        before_replay = service.replay()
        blocked = service.claim(
            handler_effect_id=second.deliveries[0].handler_effect_id,
            worker_identity="worker-2",
            claimed_at=NOW + timedelta(seconds=10),
        )
        assert blocked.status is ClaimStatus.UNAVAILABLE
        assert _counts(engine) == before_counts
        assert service.anchor() == before_anchor
        assert service.replay() == before_replay
    finally:
        engine.dispose()


def test_completed_required_handlers_release_head_of_line_despite_best_effort() -> None:
    engine = _engine()
    try:
        service = _service(engine, profile="paper-trading-v1")
        _register(
            service,
            (
                _handler("signal-loop", 0),
                _handler("runtime-monitor", 1, required=False),
            ),
        )
        first = _accept(service, source_identity="receipt-1", source_sequence=1)
        second = _accept(service, source_identity="receipt-2", source_sequence=2)
        _complete_delivery(
            service,
            first.deliveries[0].handler_effect_id,
            worker="worker-1",
            offset=10,
        )
        replay = service.replay()
        assert replay.emissions[0].status == "COMPLETED"
        assert replay.deliveries[1].status == "PENDING"
        claimed = service.claim(
            handler_effect_id=second.deliveries[0].handler_effect_id,
            worker_identity="worker-2",
            claimed_at=NOW + timedelta(seconds=20),
        )
        assert claimed.status is ClaimStatus.CLAIMED
    finally:
        engine.dispose()


def test_required_conflict_keeps_causal_head_of_line_blocked() -> None:
    engine = _engine()
    try:
        service = _service(engine, profile="signal-loop-v1")
        _register(service, (_handler("signal-loop", 0),))
        first = _accept(service, source_identity="receipt-1", source_sequence=1)
        second = _accept(service, source_identity="receipt-2", source_sequence=2)
        claim = service.claim(
            handler_effect_id=first.deliveries[0].handler_effect_id,
            worker_identity="worker-1",
            claimed_at=NOW + timedelta(seconds=10),
        )
        service.record_synthetic_handler_result(
            handler_effect_id=first.deliveries[0].handler_effect_id,
            fencing_generation=claim.delivery.fencing_generation,
            worker_identity="worker-1",
            status=ApplyStatus.CONFLICT,
            payload={"reason": "synthetic-conflict"},
            applied_at=NOW + timedelta(seconds=11),
        )
        blocked = service.claim(
            handler_effect_id=second.deliveries[0].handler_effect_id,
            worker_identity="worker-2",
            claimed_at=NOW + timedelta(seconds=12),
        )
        assert blocked.status is ClaimStatus.UNAVAILABLE
        assert service.replay().emissions[0].status == "ACCEPTED"
    finally:
        engine.dispose()


def test_limit_and_market_delivery_order_is_source_sequence_not_identity() -> None:
    engine = _engine()
    try:
        service = _service(engine, profile="signal-loop-v1")
        _register(service, (_handler("signal-loop", 0),))
        placement = _accept(
            service,
            source_identity="receipt-z-placement",
            source_sequence=10,
            payload={"kind": "LIMIT_PLACEMENT"},
        )
        fill = _accept(
            service,
            source_identity="receipt-a-fill",
            source_sequence=11,
            payload={"kind": "LIMIT_FILL"},
        )
        market = _accept(
            service,
            source_identity="receipt-m-market",
            source_sequence=12,
            payload={"kind": "MARKET_FILLED"},
        )
        pending = service.pending_deliveries()
        assert [item.handler_effect_id for item in pending] == [
            placement.deliveries[0].handler_effect_id,
            fill.deliveries[0].handler_effect_id,
            market.deliveries[0].handler_effect_id,
        ]
    finally:
        engine.dispose()


def test_expected_anchor_rejects_rechained_journal_and_anchor(tmp_path) -> None:
    engine = _engine(f"sqlite:///{(tmp_path / 'rechain.sqlite3').as_posix()}")
    try:
        service = _service(engine, profile="execution-base-v1")
        _register(service)
        _accept(service)
        expected = service.anchor()
        with engine.engine.begin() as connection:
            connection.execute(
                text(
                    "UPDATE event_delivery_journal SET event_hash = :hash "
                    "WHERE sequence = 2"
                ),
                {"hash": "c" * 64},
            )
            connection.execute(
                text(
                    "UPDATE event_delivery_anchor SET last_hash = :hash "
                    "WHERE authority_id = 'event-delivery'"
                ),
                {"hash": "c" * 64},
            )
        with pytest.raises(RuntimeError, match="expected anchor"):
            service.replay(expected_anchor=expected)
    finally:
        engine.dispose()


def test_replay_rejects_semantically_forged_rehashed_manifest_snapshot(tmp_path) -> None:
    engine = _engine(f"sqlite:///{(tmp_path / 'semantic-rehash.sqlite3').as_posix()}")
    try:
        service = _service(engine, profile="signal-loop-v1")
        _register(service, (_handler("signal-loop", 0),))
        _accept(service)
        with engine.engine.begin() as connection:
            row = connection.execute(
                text(
                    "SELECT authority_id, authority_version, sequence, event_type, "
                    "emission_effect_id, handler_effect_id, fencing_generation, "
                    "occurred_at, payload_json, previous_hash "
                    "FROM event_delivery_journal WHERE sequence = 1"
                )
            ).mappings().one()
            payload = json.loads(row["payload_json"])
            payload["manifest_snapshot"][0]["handler_id"] = "runtime-replay"
            payload_json = canonical_json_text(payload)
            payload_hash = sha256_canonical(payload)
            event_hash = journal_event_hash(
                sequence=row["sequence"],
                authority_id=row["authority_id"],
                authority_version=row["authority_version"],
                event_type=JournalEventType(row["event_type"]),
                emission_effect_id=row["emission_effect_id"],
                handler_effect_digest=row["handler_effect_id"],
                fencing_generation=row["fencing_generation"],
                occurred_at=datetime.fromisoformat(row["occurred_at"]).replace(
                    tzinfo=timezone.utc
                ),
                payload_hash=payload_hash,
                previous_hash=row["previous_hash"],
            )
            connection.execute(
                text(
                    "UPDATE event_delivery_journal SET payload_json = :payload_json, "
                    "payload_hash = :payload_hash, event_hash = :event_hash "
                    "WHERE sequence = 1"
                ),
                {
                    "payload_json": payload_json,
                    "payload_hash": payload_hash,
                    "event_hash": event_hash,
                },
            )
            connection.execute(
                text(
                    "UPDATE event_delivery_anchor SET last_hash = :event_hash "
                    "WHERE authority_id = 'event-delivery'"
                ),
                {"event_hash": event_hash},
            )
        with pytest.raises(RuntimeError, match="manifest snapshot"):
            service.replay()
    finally:
        engine.dispose()


@pytest.mark.parametrize(
    "case,mutate_accepted_payload",
    (
        (
            "accepted-sequence-bool",
            lambda payload: payload["emission"].__setitem__(
                "accepted_sequence", True
            ),
        ),
        (
            "accepted-sequence-float",
            lambda payload: payload["emission"].__setitem__(
                "accepted_sequence", 1.0
            ),
        ),
        (
            "manifest-ordinal-bool",
            lambda payload: payload["manifest_snapshot"][0].__setitem__(
                "ordinal", False
            ),
        ),
        (
            "manifest-required-int",
            lambda payload: payload["manifest_snapshot"][0].__setitem__(
                "required", 1
            ),
        ),
        (
            "delivery-fencing-bool",
            lambda payload: payload["deliveries"][0].__setitem__(
                "fencing_generation", False
            ),
        ),
        (
            "delivery-accepted-sequence-float",
            lambda payload: payload["deliveries"][0].__setitem__(
                "accepted_sequence", 1.0
            ),
        ),
    ),
    ids=(
        "accepted-sequence-bool",
        "accepted-sequence-float",
        "manifest-ordinal-bool",
        "manifest-required-int",
        "delivery-fencing-bool",
        "delivery-accepted-sequence-float",
    ),
)
def test_replay_rejects_rehashed_accepted_payload_numeric_type_substitution(
    tmp_path, case, mutate_accepted_payload
) -> None:
    engine = _engine(f"sqlite:///{(tmp_path / f'{case}.sqlite3').as_posix()}")
    try:
        service = _service(engine, profile="signal-loop-v1")
        _register(service, (_handler("signal-loop", 0),))
        _accept(service, payload={"bool": True, "int": 1, "float": 1.0})
        projection_before = _emission_delivery_projection_snapshot(engine)

        def mutate(row, payload):
            if row["event_type"] == JournalEventType.EMISSION_ACCEPTED.value:
                mutate_accepted_payload(payload)

        _rehash_journal(engine, mutate)
        assert _emission_delivery_projection_snapshot(engine) == projection_before
        with pytest.raises(RuntimeError, match="semantic reconstruction|manifest snapshot"):
            service.replay()
        assert _emission_delivery_projection_snapshot(engine) == projection_before
    finally:
        engine.dispose()


def test_replay_accepts_canonical_bool_int_and_float_as_distinct_values() -> None:
    engine = _engine()
    try:
        service = _service(engine, profile="signal-loop-v1")
        _register(service, (_handler("signal-loop", 0),))
        _accept(service, payload={"bool": True, "int": 1, "float": 1.0})
        replayed = service.replay()
        payload = replayed.emissions[0].payload
        assert type(payload["bool"]) is bool
        assert type(payload["int"]) is int
        assert type(payload["float"]) is float
    finally:
        engine.dispose()


def test_replay_rejects_rehashed_payload_and_projection_with_stale_effect_id(
    tmp_path,
) -> None:
    engine = _engine(f"sqlite:///{(tmp_path / 'stale-effect.sqlite3').as_posix()}")
    try:
        service = _service(engine, profile="signal-loop-v1")
        _register(service, (_handler("signal-loop", 0),))
        _accept(service)
        forged_payload = {"kind": "FORGED", "sequence": 1}
        forged_json = canonical_json_text(forged_payload)
        forged_hash = sha256_canonical(forged_payload)
        with engine.engine.begin() as connection:
            connection.execute(
                text(
                    "UPDATE event_bus_emissions SET payload_json = :payload, "
                    "payload_hash = :payload_hash"
                ),
                {"payload": forged_json, "payload_hash": forged_hash},
            )

        def mutate(row, payload):
            if row["event_type"] == JournalEventType.EMISSION_ACCEPTED.value:
                payload["emission"]["payload"] = forged_payload
                payload["emission"]["payload_hash"] = forged_hash

        _rehash_journal(engine, mutate)
        with pytest.raises(RuntimeError, match="semantic reconstruction"):
            service.replay()
    finally:
        engine.dispose()


def test_replay_rejects_rehashed_handler_substitution_against_bus_manifest(
    tmp_path,
) -> None:
    engine = _engine(f"sqlite:///{(tmp_path / 'handler-substitute.sqlite3').as_posix()}")
    try:
        service = _service(engine, profile="signal-loop-v1")
        _register(service, (_handler("signal-loop", 0),))
        accepted = _accept(service)
        emission_id = accepted.emission.emission_effect_id
        substituted_effect = handler_effect_id(
            emission_effect_id=emission_id,
            handler_id="runtime-replay",
            handler_version="v1",
        )
        with engine.engine.begin() as connection:
            connection.execute(
                text(
                    "UPDATE event_handler_deliveries SET handler_id = 'runtime-replay', "
                    "handler_effect_id = :effect"
                ),
                {"effect": substituted_effect},
            )

        def mutate(row, payload):
            if row["event_type"] == JournalEventType.EMISSION_ACCEPTED.value:
                payload["manifest_snapshot"][0]["handler_id"] = "runtime-replay"
                payload["deliveries"][0]["handler_id"] = "runtime-replay"
                payload["deliveries"][0]["handler_effect_id"] = substituted_effect

        _rehash_journal(engine, mutate)
        with pytest.raises(RuntimeError, match="manifest snapshot"):
            service.replay()
    finally:
        engine.dispose()


def test_replay_rejects_rehashed_handler_effect_id_substitution(tmp_path) -> None:
    engine = _engine(f"sqlite:///{(tmp_path / 'handler-effect.sqlite3').as_posix()}")
    try:
        service = _service(engine, profile="signal-loop-v1")
        _register(service, (_handler("signal-loop", 0),))
        _accept(service)
        forged_effect = "c" * 64
        with engine.engine.begin() as connection:
            connection.execute(
                text(
                    "UPDATE event_handler_deliveries SET handler_effect_id = :effect"
                ),
                {"effect": forged_effect},
            )

        def mutate(row, payload):
            if row["event_type"] == JournalEventType.EMISSION_ACCEPTED.value:
                payload["deliveries"][0]["handler_effect_id"] = forged_effect

        _rehash_journal(engine, mutate)
        with pytest.raises(RuntimeError, match="manifest snapshot"):
            service.replay()
    finally:
        engine.dispose()


def test_replay_rejects_handler_transition_cross_linked_to_other_emission(
    tmp_path,
) -> None:
    engine = _engine(f"sqlite:///{(tmp_path / 'cross-link.sqlite3').as_posix()}")
    try:
        service = _service(engine, profile="signal-loop-v1")
        _register(service, (_handler("signal-loop", 0),))
        first = _accept(service, source_identity="receipt-1", source_sequence=1)
        _complete_delivery(
            service,
            first.deliveries[0].handler_effect_id,
            worker="worker-1",
            offset=10,
        )
        second = _accept(service, source_identity="receipt-2", source_sequence=2)
        service.claim(
            handler_effect_id=second.deliveries[0].handler_effect_id,
            worker_identity="worker-2",
            claimed_at=NOW + timedelta(seconds=20),
        )

        def mutate(row, _payload):
            if (
                row["event_type"] == JournalEventType.HANDLER_CLAIMED.value
                and row["handler_effect_id"] == second.deliveries[0].handler_effect_id
            ):
                row["emission_effect_id"] = first.emission.emission_effect_id

        _rehash_journal(engine, mutate)
        with pytest.raises(RuntimeError, match="cross-link"):
            service.replay()
    finally:
        engine.dispose()


def test_replay_rejects_noncanonical_emission_journal_headers(tmp_path) -> None:
    engine = _engine(f"sqlite:///{(tmp_path / 'header.sqlite3').as_posix()}")
    try:
        service = _service(engine, profile="execution-base-v1")
        _register(service)
        _accept(service)

        def mutate(row, _payload):
            if row["event_type"] == JournalEventType.EMISSION_ACCEPTED.value:
                row["handler_effect_id"] = "c" * 64
                row["fencing_generation"] = 1

        _rehash_journal(engine, mutate)
        with pytest.raises(RuntimeError, match="journal header"):
            service.replay()
    finally:
        engine.dispose()


def test_replay_rejects_rehashed_claim_before_predecessor_completion(tmp_path) -> None:
    engine = _engine(f"sqlite:///{(tmp_path / 'causal-claim.sqlite3').as_posix()}")
    try:
        service = _service(engine, profile="signal-loop-v1")
        _register(service, (_handler("signal-loop", 0),))
        _accept(service, source_identity="receipt-1", source_sequence=1)
        second = _accept(service, source_identity="receipt-2", source_sequence=2)
        _append_forged_claim(
            engine,
            emission_effect_digest=second.emission.emission_effect_id,
            handler_effect_digest=second.deliveries[0].handler_effect_id,
            worker_identity="worker-2",
            claimed_at=NOW + timedelta(seconds=20),
        )
        with pytest.raises(RuntimeError, match="head-of-line causality"):
            service.replay()
    finally:
        engine.dispose()


def test_replay_rejects_projection_matching_causally_invalid_claim(tmp_path) -> None:
    engine = _engine(
        f"sqlite:///{(tmp_path / 'causal-projection.sqlite3').as_posix()}"
    )
    try:
        service = _service(engine, profile="signal-loop-v1")
        _register(service, (_handler("signal-loop", 0),))
        _accept(service, source_identity="receipt-1", source_sequence=1)
        second = _accept(service, source_identity="receipt-2", source_sequence=2)
        _append_forged_claim(
            engine,
            emission_effect_digest=second.emission.emission_effect_id,
            handler_effect_digest=second.deliveries[0].handler_effect_id,
            worker_identity="worker-2",
            claimed_at=NOW + timedelta(seconds=20),
        )
        with engine.session() as session:
            projection = session.execute(
                text(
                    "SELECT status, fencing_generation, worker_identity "
                    "FROM event_handler_deliveries WHERE handler_effect_id = :handler"
                ),
                {"handler": second.deliveries[0].handler_effect_id},
            ).one()
        assert tuple(projection) == ("CLAIMED", 1, "worker-2")
        with pytest.raises(RuntimeError, match="head-of-line causality"):
            service.replay()
    finally:
        engine.dispose()


def test_replay_rejects_rehashed_regressive_acceptance_order(tmp_path) -> None:
    engine = _engine(
        f"sqlite:///{(tmp_path / 'regressive-acceptance.sqlite3').as_posix()}"
    )
    try:
        service = _service(engine, profile="execution-base-v1")
        _register(service)
        first = _accept(service, source_identity="receipt-1", source_sequence=1)
        second = _accept(service, source_identity="receipt-3", source_sequence=3)
        _forge_reversed_acceptance_order(
            engine,
            first_effect_id=first.emission.emission_effect_id,
            second_effect_id=second.emission.emission_effect_id,
        )
        with pytest.raises(RuntimeError, match="strictly increasing"):
            service.replay()
    finally:
        engine.dispose()


@pytest.mark.parametrize(
    "forged_generation",
    (True, 1.0),
    ids=("boolean", "float"),
)
def test_replay_rejects_noninteger_observed_generation(
    tmp_path, forged_generation: object
) -> None:
    engine = _engine(
        f"sqlite:///{(tmp_path / f'observed-{type(forged_generation).__name__}.sqlite3').as_posix()}"
    )
    try:
        service = _service(engine, profile="signal-loop-v1")
        _register(service, (_handler("signal-loop", 0),))
        delivery = _accept(service).deliveries[0]
        claimed = service.claim(
            handler_effect_id=delivery.handler_effect_id,
            worker_identity="worker-1",
            claimed_at=NOW + timedelta(seconds=2),
        )
        service.recover_claim(
            handler_effect_id=delivery.handler_effect_id,
            observed_generation=claimed.delivery.fencing_generation,
            worker_identity="worker-2",
            recovered_at=NOW + timedelta(seconds=3),
        )

        def mutate(row, payload):
            if row["event_type"] == JournalEventType.HANDLER_CLAIM_RECOVERED.value:
                payload["observed_generation"] = forged_generation

        _rehash_journal(engine, mutate)
        with pytest.raises(RuntimeError, match="observed_generation"):
            service.replay()
    finally:
        engine.dispose()


@pytest.mark.parametrize("stage", ("CLAIMED", "APPLIED", "COMPLETED"))
def test_handler_progression_failure_before_journal_rolls_back_atomically(
    tmp_path, stage: str
) -> None:
    engine = _engine(f"sqlite:///{(tmp_path / f'rollback-{stage}.sqlite3').as_posix()}")
    try:
        service = _service(engine, profile="signal-loop-v1")
        _register(service, (_handler("signal-loop", 0),))
        delivery = _accept(service).deliveries[0]
        generation = 1
        if stage in {"APPLIED", "COMPLETED"}:
            claim = service.claim(
                handler_effect_id=delivery.handler_effect_id,
                worker_identity="worker-1",
                claimed_at=NOW + timedelta(seconds=2),
            )
            generation = claim.delivery.fencing_generation
        if stage == "COMPLETED":
            service.record_synthetic_handler_result(
                handler_effect_id=delivery.handler_effect_id,
                fencing_generation=generation,
                worker_identity="worker-1",
                status=ApplyStatus.APPLIED_NEW,
                payload={"applied": True},
                applied_at=NOW + timedelta(seconds=3),
            )
        before_counts = _counts(engine)
        before_anchor = service.anchor()
        before_replay = service.replay()
        fired = False

        def fail_journal(_connection, _cursor, statement, _parameters, _context, _many):
            nonlocal fired
            if not fired and "INSERT INTO event_delivery_journal" in statement:
                fired = True
                raise RuntimeError("injected progression failure")

        event.listen(engine.engine, "before_cursor_execute", fail_journal)
        try:
            with pytest.raises(RuntimeError, match="injected progression"):
                if stage == "CLAIMED":
                    service.claim(
                        handler_effect_id=delivery.handler_effect_id,
                        worker_identity="worker-1",
                        claimed_at=NOW + timedelta(seconds=4),
                    )
                elif stage == "APPLIED":
                    service.record_synthetic_handler_result(
                        handler_effect_id=delivery.handler_effect_id,
                        fencing_generation=generation,
                        worker_identity="worker-1",
                        status=ApplyStatus.APPLIED_NEW,
                        payload={"applied": True},
                        applied_at=NOW + timedelta(seconds=4),
                    )
                else:
                    service.complete_handler(
                        handler_effect_id=delivery.handler_effect_id,
                        fencing_generation=generation,
                        worker_identity="worker-1",
                        completed_at=NOW + timedelta(seconds=4),
                    )
        finally:
            event.remove(engine.engine, "before_cursor_execute", fail_journal)
        assert fired
        assert _counts(engine) == before_counts
        assert service.anchor() == before_anchor
        assert service.replay() == before_replay
    finally:
        engine.dispose()


def test_failure_between_handler_and_emission_completion_rolls_back_both(
    tmp_path,
) -> None:
    engine = _engine(f"sqlite:///{(tmp_path / 'completion-gap.sqlite3').as_posix()}")
    try:
        service = _service(engine, profile="signal-loop-v1")
        _register(service, (_handler("signal-loop", 0),))
        delivery = _accept(service).deliveries[0]
        claim = service.claim(
            handler_effect_id=delivery.handler_effect_id,
            worker_identity="worker-1",
            claimed_at=NOW + timedelta(seconds=2),
        )
        service.record_synthetic_handler_result(
            handler_effect_id=delivery.handler_effect_id,
            fencing_generation=claim.delivery.fencing_generation,
            worker_identity="worker-1",
            status=ApplyStatus.APPLIED_NEW,
            payload={"applied": True},
            applied_at=NOW + timedelta(seconds=3),
        )
        before_counts = _counts(engine)
        before_anchor = service.anchor()
        before_replay = service.replay()
        journal_inserts = 0

        def fail_second_journal(
            _connection, _cursor, statement, _parameters, _context, _many
        ):
            nonlocal journal_inserts
            if "INSERT INTO event_delivery_journal" in statement:
                journal_inserts += 1
                if journal_inserts == 2:
                    raise RuntimeError("injected emission completion failure")

        event.listen(engine.engine, "before_cursor_execute", fail_second_journal)
        try:
            with pytest.raises(RuntimeError, match="injected emission completion"):
                service.complete_handler(
                    handler_effect_id=delivery.handler_effect_id,
                    fencing_generation=claim.delivery.fencing_generation,
                    worker_identity="worker-1",
                    completed_at=NOW + timedelta(seconds=4),
                )
        finally:
            event.remove(engine.engine, "before_cursor_execute", fail_second_journal)
        assert journal_inserts == 2
        assert _counts(engine) == before_counts
        assert service.anchor() == before_anchor
        assert service.replay() == before_replay
    finally:
        engine.dispose()


def test_replay_rejects_projection_payload_chain_reorder_and_truncation(tmp_path) -> None:
    scenarios = ("projection", "payload", "reorder", "truncation")
    for scenario in scenarios:
        engine = _engine(f"sqlite:///{(tmp_path / f'{scenario}.sqlite3').as_posix()}")
        try:
            service = _service(engine, profile="signal-loop-v1")
            _register(service, (_handler("signal-loop", 0),))
            delivery = _accept(service).deliveries[0]
            service.claim(
                handler_effect_id=delivery.handler_effect_id,
                worker_identity="worker-1",
                claimed_at=NOW + timedelta(seconds=2),
            )
            expected_anchor = service.anchor()
            with engine.engine.begin() as connection:
                if scenario == "projection":
                    connection.execute(
                        text(
                            "UPDATE event_handler_deliveries SET status = 'PENDING', "
                            "fencing_generation = 0, worker_identity = NULL, claimed_at = NULL "
                            "WHERE handler_effect_id = :effect_id"
                        ),
                        {"effect_id": delivery.handler_effect_id},
                    )
                elif scenario == "payload":
                    connection.execute(
                        text(
                            "UPDATE event_delivery_journal SET payload_json = '{}' "
                            "WHERE sequence = 2"
                        )
                    )
                elif scenario == "reorder":
                    connection.execute(
                        text(
                            "UPDATE event_delivery_journal SET sequence = 100 WHERE sequence = 1"
                        )
                    )
                    connection.execute(
                        text(
                            "UPDATE event_delivery_journal SET sequence = 1 WHERE sequence = 2"
                        )
                    )
                    connection.execute(
                        text(
                            "UPDATE event_delivery_journal SET sequence = 2 WHERE sequence = 100"
                        )
                    )
                else:
                    connection.execute(
                        text("DELETE FROM event_delivery_journal WHERE sequence = 2")
                    )
            with pytest.raises(RuntimeError):
                service.replay(expected_anchor=expected_anchor)
        finally:
            engine.dispose()


def test_thread_concurrent_claim_has_one_authoritative_winner(tmp_path) -> None:
    database = tmp_path / "claim.sqlite3"
    url = f"sqlite:///{database.as_posix()}"
    bootstrap = _engine(url)
    service = _service(bootstrap, profile="signal-loop-v1")
    _register(service, (_handler("signal-loop", 0),))
    effect_id = _accept(service).deliveries[0].handler_effect_id
    bootstrap.dispose()
    barrier = Barrier(2)

    def worker(identity: str):
        engine = SqlAlchemyEngine(url, delivery_authority=True)
        try:
            local = _service(engine, profile="signal-loop-v1")
            barrier.wait(timeout=10)
            return local.claim(
                handler_effect_id=effect_id,
                worker_identity=identity,
                claimed_at=NOW + timedelta(seconds=2),
            ).status
        finally:
            engine.dispose()

    with ThreadPoolExecutor(max_workers=2) as pool:
        statuses = tuple(pool.map(worker, ("worker-a", "worker-b")))
    assert sorted(item.value for item in statuses) == ["CLAIMED", "UNAVAILABLE"]


def test_thread_concurrent_acceptance_never_commits_regressive_order(tmp_path) -> None:
    database = tmp_path / "accept-order.sqlite3"
    url = f"sqlite:///{database.as_posix()}"
    bootstrap = _engine(url)
    service = _service(bootstrap, profile="signal-loop-v1")
    _register(service, (_handler("signal-loop", 0),))
    bootstrap.dispose()
    barrier = Barrier(2)

    def worker(sequence: int) -> tuple[str, int]:
        engine = SqlAlchemyEngine(url, delivery_authority=True)
        try:
            local = _service(engine, profile="signal-loop-v1")
            barrier.wait(timeout=10)
            try:
                _accept(
                    local,
                    source_identity=f"receipt-{sequence}",
                    source_sequence=sequence,
                )
                return ("accepted", sequence)
            except ValueError:
                return ("rejected", sequence)
        finally:
            engine.dispose()

    with ThreadPoolExecutor(max_workers=2) as pool:
        observed = tuple(pool.map(worker, (10, 11)))
    assert any(status == "accepted" for status, _ in observed)
    verifier = SqlAlchemyEngine(url, delivery_authority=True)
    try:
        with verifier.session() as session:
            committed = list(
                session.execute(
                    text(
                        "SELECT source_sequence FROM event_bus_emissions "
                        "ORDER BY accepted_sequence"
                    )
                ).scalars()
            )
        assert committed == sorted(set(committed))
    finally:
        verifier.dispose()


def test_repository_and_result_projections_are_deeply_immutable() -> None:
    engine = _engine()
    try:
        service = _service(engine, profile="execution-base-v1")
        _register(service)
        result = _accept(service, payload={"nested": {"items": [1, 2]}})
        with pytest.raises(TypeError):
            result.emission.payload["nested"]["items"] = ()
        with engine.delivery_session() as session:
            replay = EventDeliveryRepository(
                session,
                authority_id="event-delivery",
                authority_version="v1",
            ).replay()
        assert replay.emissions[0].payload["nested"]["items"] == (1, 2)
    finally:
        engine.dispose()
