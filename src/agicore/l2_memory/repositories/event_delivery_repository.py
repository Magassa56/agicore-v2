"""SQL authority for durable EventBus emission and handler progression."""
from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import datetime, timezone

from sqlalchemy import Select, func, select, update
from sqlalchemy.orm import Session

from agicore.core.event_delivery_contracts import (
    ApplyStatus,
    AnchorRecord,
    ClaimResult,
    ClaimStatus,
    DeliveryRecord,
    DispatchClass,
    EmissionApplyResult,
    EmissionRecord,
    GENESIS_HASH,
    HandlerManifestEntry,
    JournalEventType,
    ManifestApplyResult,
    ManifestRecord,
    PreparedEmission,
    PreparedManifest,
    ReplayResult,
    canonical_identity,
    canonical_json_text,
    canonical_time,
    handler_effect_id,
    journal_event_hash,
    sha256_canonical,
    synthetic_result_hash,
    prepare_emission,
    verify_emission,
    verify_manifest,
)

from ..models.event_delivery import (
    EventBusEmission,
    EventDeliveryAnchor,
    EventDeliveryJournal,
    EventHandlerDelivery,
    EventHandlerManifest,
    EventHandlerManifestEntry,
)
from ..adapters.sqlalchemy_engine import (
    _DeliverySessionCapability,
    _require_delivery_session_capability,
)


def _json_values_equal_exact(left: object, right: object) -> bool:
    """Compare canonical JSON values recursively without Python numeric coercion."""
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(
            _json_values_equal_exact(left[key], right[key]) for key in left
        )
    if isinstance(left, list):
        return len(left) == len(right) and all(
            _json_values_equal_exact(left_item, right_item)
            for left_item, right_item in zip(left, right, strict=True)
        )
    return left == right


class EventDeliveryRepository:
    """Repository used inside one already-open authoritative SQL transaction."""

    def __init__(
        self,
        session: Session,
        *,
        authority_id: str,
        authority_version: str,
    ) -> None:
        self._session = session
        self._delivery_capability: _DeliverySessionCapability = (
            _require_delivery_session_capability(session)
        )
        self._delivery_capability_token = self._delivery_capability._token
        self._authority_id = canonical_identity(authority_id, field="authority_id")
        self._authority_version = canonical_identity(
            authority_version, field="authority_version"
        )

    def register_manifest(
        self, prepared: PreparedManifest, *, registered_at: datetime
    ) -> ManifestApplyResult:
        """Register one immutable bus-owned manifest version."""
        self._require_authority()
        prepared = verify_manifest(prepared)
        registered_time, _ = canonical_time(registered_at, field="registered_at")
        anchor = self._ensure_anchor()
        if anchor.authority_version != self._authority_version:
            raise RuntimeError("delivery authority version mismatch")
        existing = self._session.execute(
            select(EventHandlerManifest).where(
                EventHandlerManifest.authority_id == self._authority_id,
                EventHandlerManifest.runtime_profile_id == prepared.runtime_profile_id,
                EventHandlerManifest.event_type == prepared.event_type,
                EventHandlerManifest.manifest_version == prepared.manifest_version,
            )
        ).scalar_one_or_none()
        if existing is not None:
            record = self._manifest_record(existing)
            same = (
                existing.manifest_hash == prepared.manifest_hash
                and existing.canonical_json == prepared.canonical_json
                and record.entries == prepared.entries
            )
            return ManifestApplyResult(
                status=ApplyStatus.ALREADY_APPLIED if same else ApplyStatus.CONFLICT,
                manifest=record,
            )

        row = EventHandlerManifest(
            authority_id=self._authority_id,
            runtime_profile_id=prepared.runtime_profile_id,
            event_type=prepared.event_type,
            manifest_version=prepared.manifest_version,
            manifest_hash=prepared.manifest_hash,
            canonical_json=prepared.canonical_json,
            registered_at=registered_time,
        )
        self._session.add(row)
        self._session.flush()
        for item in prepared.entries:
            self._session.add(
                EventHandlerManifestEntry(
                    manifest_id=row.id,
                    handler_id=item.handler_id,
                    handler_version=item.handler_version,
                    required=item.required,
                    ordinal=item.ordinal,
                    dispatch_class=item.dispatch_class.value,
                )
            )
        self._session.flush()
        return ManifestApplyResult(
            status=ApplyStatus.APPLIED_NEW,
            manifest=self._manifest_record(row),
        )

    def resolve_manifest(
        self, *, runtime_profile_id: str, event_type: str, manifest_version: str
    ) -> PreparedManifest:
        """Resolve an exact manifest from authority-owned configuration."""
        self._require_authority()
        profile = canonical_identity(runtime_profile_id, field="runtime_profile_id")
        event = canonical_identity(event_type, field="event_type")
        version = canonical_identity(manifest_version, field="manifest_version")
        row = self._session.execute(
            select(EventHandlerManifest).where(
                EventHandlerManifest.authority_id == self._authority_id,
                EventHandlerManifest.runtime_profile_id == profile,
                EventHandlerManifest.event_type == event,
                EventHandlerManifest.manifest_version == version,
            )
        ).scalar_one_or_none()
        if row is None:
            raise RuntimeError("no bus-owned manifest registered for this event")
        entries = self._manifest_entries(row.id)
        prepared = PreparedManifest(
            runtime_profile_id=row.runtime_profile_id,
            event_type=row.event_type,
            manifest_version=row.manifest_version,
            entries=entries,
            manifest_hash=row.manifest_hash,
            canonical_json=row.canonical_json,
        )
        from agicore.core.event_delivery_contracts import prepare_manifest

        rebuilt = prepare_manifest(
            runtime_profile_id=prepared.runtime_profile_id,
            event_type=prepared.event_type,
            manifest_version=prepared.manifest_version,
            entries=prepared.entries,
        )
        if rebuilt != prepared:
            raise RuntimeError("persisted manifest is not canonical")
        return prepared

    def accept_emission(self, prepared: PreparedEmission) -> EmissionApplyResult:
        """Atomically accept an emission, deliveries, journal, and anchor."""
        self._require_authority()
        prepared = verify_emission(prepared)
        manifest = self.resolve_manifest(
            runtime_profile_id=prepared.runtime_profile_id,
            event_type=prepared.event_type,
            manifest_version=prepared.manifest_version,
        )
        if (
            prepared.authority_id != self._authority_id
            or prepared.authority_version != self._authority_version
            or prepared.runtime_profile_id != manifest.runtime_profile_id
            or prepared.manifest_version != manifest.manifest_version
            or prepared.event_type != manifest.event_type
            or prepared.manifest_hash != manifest.manifest_hash
        ):
            raise ValueError("emission does not match the resolved bus-owned manifest")
        existing = self._find_emission_identity(prepared)
        if existing is not None:
            return self._existing_emission_result(existing, prepared, manifest)

        greatest_sequence = self._session.execute(
            select(func.max(EventBusEmission.source_sequence)).where(
                EventBusEmission.authority_id == self._authority_id,
                EventBusEmission.consumer_id == prepared.consumer_id,
            )
        ).scalar_one()
        if (
            greatest_sequence is not None
            and prepared.source_sequence <= greatest_sequence
        ):
            raise ValueError(
                "source_sequence must be greater than the consumer's last accepted sequence"
            )

        self._ensure_anchor()

        next_sequence = self._anchor().last_sequence + 1
        emission = EventBusEmission(
            authority_id=self._authority_id,
            authority_version=self._authority_version,
            source_identity=prepared.source_identity,
            consumer_id=prepared.consumer_id,
            outcome_id=prepared.outcome_id,
            outcome_hash=prepared.outcome_hash,
            receipt_hash=prepared.receipt_hash,
            source_sequence=prepared.source_sequence,
            event_type=prepared.event_type,
            occurred_at=prepared.occurred_at,
            accepted_at=prepared.accepted_at,
            payload_json=prepared.payload_json,
            payload_hash=prepared.payload_hash,
            runtime_profile_id=prepared.runtime_profile_id,
            manifest_version=prepared.manifest_version,
            manifest_hash=prepared.manifest_hash,
            emission_effect_id=prepared.emission_effect_id,
            accepted_sequence=next_sequence,
            status="ACCEPTED",
        )
        self._session.add(emission)
        self._session.flush()
        deliveries: list[EventHandlerDelivery] = []
        for entry in manifest.entries:
            delivery = EventHandlerDelivery(
                emission_id=emission.id,
                authority_id=self._authority_id,
                emission_effect_id=emission.emission_effect_id,
                handler_effect_id=handler_effect_id(
                    emission_effect_id=emission.emission_effect_id,
                    handler_id=entry.handler_id,
                    handler_version=entry.handler_version,
                ),
                handler_id=entry.handler_id,
                handler_version=entry.handler_version,
                required=entry.required,
                ordinal=entry.ordinal,
                dispatch_class=entry.dispatch_class.value,
                status="PENDING",
                fencing_generation=0,
                worker_identity=None,
                claimed_at=None,
                result_status=None,
                result_hash=None,
                result_json=None,
            )
            self._session.add(delivery)
            deliveries.append(delivery)
        self._session.flush()
        accepted_payload = self._accepted_payload(emission, deliveries)
        accepted = self._append_journal(
            event_type=JournalEventType.EMISSION_ACCEPTED,
            emission_effect_id=emission.emission_effect_id,
            handler_effect_digest=None,
            fencing_generation=0,
            occurred_at=prepared.accepted_at,
            payload=accepted_payload,
        )
        if accepted.sequence != emission.accepted_sequence:
            raise RuntimeError("accepted journal sequence allocation diverged")

        completed_hash: str | None = None
        if not any(item.required for item in deliveries):
            emission.status = "COMPLETED"
            completed = self._append_journal(
                event_type=JournalEventType.EMISSION_COMPLETED,
                emission_effect_id=emission.emission_effect_id,
                handler_effect_digest=None,
                fencing_generation=0,
                occurred_at=prepared.accepted_at,
                payload={
                    "required_handler_effect_ids": [],
                    "completion_scope": "required_handlers_only",
                },
            )
            completed_hash = completed.event_hash
        self._session.flush()
        return EmissionApplyResult(
            status=ApplyStatus.APPLIED_NEW,
            emission=self._emission_record(emission),
            deliveries=tuple(self._delivery_record(item, emission) for item in deliveries),
            emission_accepted_hash=accepted.event_hash,
            emission_completed_hash=completed_hash,
        )

    def pending_deliveries(self) -> tuple[DeliveryRecord, ...]:
        """Return pending/claimed/applied work in authoritative causal order."""
        self._require_authority()
        rows = self._session.execute(
            select(EventHandlerDelivery, EventBusEmission)
            .join(EventBusEmission, EventBusEmission.id == EventHandlerDelivery.emission_id)
            .where(
                EventHandlerDelivery.authority_id == self._authority_id,
                EventHandlerDelivery.status.in_(("PENDING", "CLAIMED", "APPLIED")),
            )
            .order_by(
                EventBusEmission.consumer_id,
                EventBusEmission.source_sequence,
                EventBusEmission.accepted_sequence,
                EventHandlerDelivery.ordinal,
            )
        ).all()
        return tuple(self._delivery_record(delivery, emission) for delivery, emission in rows)

    def claim(
        self,
        *,
        handler_effect_digest: str,
        worker_identity: str,
        claimed_at: datetime,
    ) -> ClaimResult:
        """Claim one pending delivery with an authoritative fencing generation."""
        self._require_authority()
        worker = canonical_identity(worker_identity, field="worker_identity")
        claim_time, _ = canonical_time(claimed_at, field="claimed_at")
        delivery, emission = self._delivery_and_emission(handler_effect_digest)
        predecessor = self._session.execute(
            select(EventBusEmission.id).where(
                EventBusEmission.authority_id == self._authority_id,
                EventBusEmission.consumer_id == emission.consumer_id,
                EventBusEmission.source_sequence < emission.source_sequence,
                EventBusEmission.status != "COMPLETED",
            ).limit(1)
        ).first()
        if predecessor is not None:
            return ClaimResult(
                status=ClaimStatus.UNAVAILABLE,
                delivery=self._delivery_record(delivery, emission),
            )
        if delivery.status == "CLAIMED" and delivery.worker_identity == worker:
            return ClaimResult(
                status=ClaimStatus.ALREADY_CLAIMED,
                delivery=self._delivery_record(delivery, emission),
            )
        if delivery.status != "PENDING":
            return ClaimResult(
                status=ClaimStatus.UNAVAILABLE,
                delivery=self._delivery_record(delivery, emission),
            )
        previous_generation = delivery.fencing_generation
        generation = previous_generation + 1
        result = self._session.execute(
            update(EventHandlerDelivery)
            .where(
                EventHandlerDelivery.id == delivery.id,
                EventHandlerDelivery.status == "PENDING",
                EventHandlerDelivery.fencing_generation == previous_generation,
            )
            .values(
                status="CLAIMED",
                fencing_generation=generation,
                worker_identity=worker,
                claimed_at=claim_time,
            )
        )
        if result.rowcount != 1:
            raise RuntimeError("handler claim CAS failed")
        self._session.flush()
        self._session.refresh(delivery)
        self._append_journal(
            event_type=JournalEventType.HANDLER_CLAIMED,
            emission_effect_id=emission.emission_effect_id,
            handler_effect_digest=delivery.handler_effect_id,
            fencing_generation=generation,
            occurred_at=claim_time,
            payload={"worker_identity": worker},
        )
        return ClaimResult(
            status=ClaimStatus.CLAIMED,
            delivery=self._delivery_record(delivery, emission),
        )

    def recover_claim(
        self,
        *,
        handler_effect_digest: str,
        observed_generation: int,
        worker_identity: str,
        recovered_at: datetime,
    ) -> ClaimResult:
        """Explicitly recover a claim and fence the former worker."""
        self._require_authority()
        if (
            not isinstance(observed_generation, int)
            or isinstance(observed_generation, bool)
            or observed_generation <= 0
        ):
            raise ValueError("observed_generation must be a positive integer")
        worker = canonical_identity(worker_identity, field="worker_identity")
        recovery_time, _ = canonical_time(recovered_at, field="recovered_at")
        delivery, emission = self._delivery_and_emission(handler_effect_digest)
        if delivery.status not in {"CLAIMED", "APPLIED"}:
            return ClaimResult(
                status=ClaimStatus.UNAVAILABLE,
                delivery=self._delivery_record(delivery, emission),
            )
        if delivery.fencing_generation != observed_generation:
            return ClaimResult(
                status=ClaimStatus.UNAVAILABLE,
                delivery=self._delivery_record(delivery, emission),
            )
        previous_worker = delivery.worker_identity
        generation = observed_generation + 1
        result = self._session.execute(
            update(EventHandlerDelivery)
            .where(
                EventHandlerDelivery.id == delivery.id,
                EventHandlerDelivery.status == delivery.status,
                EventHandlerDelivery.fencing_generation == observed_generation,
            )
            .values(
                fencing_generation=generation,
                worker_identity=worker,
                claimed_at=recovery_time,
            )
        )
        if result.rowcount != 1:
            raise RuntimeError("handler recovery CAS failed")
        self._session.flush()
        self._session.refresh(delivery)
        self._append_journal(
            event_type=JournalEventType.HANDLER_CLAIM_RECOVERED,
            emission_effect_id=emission.emission_effect_id,
            handler_effect_digest=delivery.handler_effect_id,
            fencing_generation=generation,
            occurred_at=recovery_time,
            payload={
                "worker_identity": worker,
                "previous_worker_identity": previous_worker,
                "observed_generation": observed_generation,
                "preserved_status": delivery.status,
            },
        )
        return ClaimResult(
            status=ClaimStatus.CLAIMED,
            delivery=self._delivery_record(delivery, emission),
        )

    def record_handler_result(
        self,
        *,
        handler_effect_digest: str,
        fencing_generation: int,
        worker_identity: str,
        status: ApplyStatus,
        payload: Mapping[str, object],
        applied_at: datetime,
    ) -> DeliveryRecord:
        """Record a synthetic B1 handler result under the current fencing token."""
        self._require_authority()
        worker = canonical_identity(worker_identity, field="worker_identity")
        applied_time, _ = canonical_time(applied_at, field="applied_at")
        result_status = ApplyStatus(status)
        result_hash, result_json, _ = synthetic_result_hash(
            handler_effect_digest=handler_effect_digest,
            status=result_status,
            payload=payload,
        )
        delivery, emission = self._delivery_and_emission(handler_effect_digest)
        self._assert_fencing(delivery, fencing_generation, worker)
        if delivery.status in {"APPLIED", "COMPLETED", "CONFLICT"}:
            if (
                delivery.result_status == result_status.value
                and delivery.result_hash == result_hash
                and delivery.result_json == result_json
            ):
                return self._delivery_record(delivery, emission)
            raise RuntimeError("handler result conflicts with its authoritative record")
        if delivery.status != "CLAIMED":
            raise RuntimeError("handler must be claimed before recording a result")
        delivery.status = (
            "CONFLICT" if result_status is ApplyStatus.CONFLICT else "APPLIED"
        )
        delivery.result_status = result_status.value
        delivery.result_hash = result_hash
        delivery.result_json = result_json
        self._session.flush()
        self._append_journal(
            event_type=JournalEventType.HANDLER_APPLIED,
            emission_effect_id=emission.emission_effect_id,
            handler_effect_digest=delivery.handler_effect_id,
            fencing_generation=fencing_generation,
            occurred_at=applied_time,
            payload={
                "worker_identity": worker,
                "result_status": result_status.value,
                "result_hash": result_hash,
                "result": json.loads(result_json),
            },
        )
        return self._delivery_record(delivery, emission)

    def complete_handler(
        self,
        *,
        handler_effect_digest: str,
        fencing_generation: int,
        worker_identity: str,
        completed_at: datetime,
    ) -> DeliveryRecord:
        """Confirm one applied handler and complete its emission when eligible."""
        self._require_authority()
        worker = canonical_identity(worker_identity, field="worker_identity")
        completion_time, _ = canonical_time(completed_at, field="completed_at")
        delivery, emission = self._delivery_and_emission(handler_effect_digest)
        self._assert_fencing(delivery, fencing_generation, worker)
        if delivery.status == "COMPLETED":
            return self._delivery_record(delivery, emission)
        if delivery.status != "APPLIED":
            raise RuntimeError("only an applied handler can be completed")
        delivery.status = "COMPLETED"
        self._session.flush()
        self._append_journal(
            event_type=JournalEventType.HANDLER_COMPLETED,
            emission_effect_id=emission.emission_effect_id,
            handler_effect_digest=delivery.handler_effect_id,
            fencing_generation=fencing_generation,
            occurred_at=completion_time,
            payload={
                "worker_identity": worker,
                "result_hash": delivery.result_hash,
            },
        )
        incomplete_required = self._session.execute(
            select(EventHandlerDelivery.id).where(
                EventHandlerDelivery.emission_id == emission.id,
                EventHandlerDelivery.required.is_(True),
                EventHandlerDelivery.status != "COMPLETED",
            )
        ).first()
        if incomplete_required is None and emission.status != "COMPLETED":
            required_ids = self._session.execute(
                select(EventHandlerDelivery.handler_effect_id)
                .where(
                    EventHandlerDelivery.emission_id == emission.id,
                    EventHandlerDelivery.required.is_(True),
                )
                .order_by(EventHandlerDelivery.ordinal)
            ).scalars().all()
            emission.status = "COMPLETED"
            self._append_journal(
                event_type=JournalEventType.EMISSION_COMPLETED,
                emission_effect_id=emission.emission_effect_id,
                handler_effect_digest=None,
                fencing_generation=0,
                occurred_at=completion_time,
                payload={
                    "required_handler_effect_ids": list(required_ids),
                    "completion_scope": "required_handlers_only",
                },
            )
        self._session.flush()
        return self._delivery_record(delivery, emission)

    def anchor(self) -> AnchorRecord:
        """Return the current immutable final anchor."""
        self._require_authority()
        anchor = self._anchor()
        return AnchorRecord(
            authority_id=anchor.authority_id,
            authority_version=anchor.authority_version,
            last_sequence=anchor.last_sequence,
            last_hash=anchor.last_hash,
        )

    def replay(self, *, expected_anchor: AnchorRecord | None = None) -> ReplayResult:
        """Verify chain, anchor and complete SQL projection, then replay state."""
        self._require_authority()
        anchor = self._anchor()
        actual_anchor = self.anchor()
        if expected_anchor is not None and actual_anchor != expected_anchor:
            raise RuntimeError("event delivery anchor differs from the expected anchor")
        rows = self._session.execute(
            select(EventDeliveryJournal)
            .where(EventDeliveryJournal.authority_id == self._authority_id)
            .order_by(EventDeliveryJournal.sequence)
        ).scalars().all()
        if len(rows) != anchor.last_sequence:
            raise RuntimeError("event delivery journal is truncated or has a sequence gap")

        emissions: dict[str, dict[str, object]] = {}
        deliveries: dict[str, dict[str, object]] = {}
        previous_hash = GENESIS_HASH
        for expected_sequence, row in enumerate(rows, start=1):
            if (
                row.authority_id != self._authority_id
                or row.authority_version != self._authority_version
            ):
                raise RuntimeError("event delivery journal authority identity is invalid")
            if row.sequence != expected_sequence or row.previous_hash != previous_hash:
                raise RuntimeError("event delivery journal sequence or chain is invalid")
            payload = json.loads(row.payload_json)
            if canonical_json_text(payload) != row.payload_json:
                raise RuntimeError("event delivery journal payload is not canonical")
            if sha256_canonical(payload) != row.payload_hash:
                raise RuntimeError("event delivery journal payload hash is invalid")
            rebuilt_hash = journal_event_hash(
                sequence=row.sequence,
                authority_id=row.authority_id,
                authority_version=row.authority_version,
                event_type=JournalEventType(row.event_type),
                emission_effect_id=row.emission_effect_id,
                handler_effect_digest=row.handler_effect_id,
                fencing_generation=row.fencing_generation,
                occurred_at=self._normalized_time(row.occurred_at),
                payload_hash=row.payload_hash,
                previous_hash=row.previous_hash,
            )
            if row.event_hash != rebuilt_hash:
                raise RuntimeError("event delivery journal event hash is invalid")
            self._replay_transition(row, payload, emissions, deliveries)
            previous_hash = row.event_hash
        if anchor.last_hash != previous_hash:
            raise RuntimeError("event delivery anchor hash is invalid")

        sql_emissions = self._session.execute(
            select(EventBusEmission)
            .where(EventBusEmission.authority_id == self._authority_id)
            .order_by(EventBusEmission.accepted_sequence)
        ).scalars().all()
        sql_deliveries = self._session.execute(
            select(EventHandlerDelivery, EventBusEmission)
            .join(EventBusEmission, EventBusEmission.id == EventHandlerDelivery.emission_id)
            .where(EventHandlerDelivery.authority_id == self._authority_id)
            .order_by(EventBusEmission.accepted_sequence, EventHandlerDelivery.ordinal)
        ).all()
        sql_emission_projection = {
            row.emission_effect_id: self._emission_projection(row)
            for row in sql_emissions
        }
        if not _json_values_equal_exact(sql_emission_projection, emissions):
            raise RuntimeError("event emission projection diverges from the journal")
        sql_delivery_projection = {
            delivery.handler_effect_id: self._delivery_projection(delivery, emission)
            for delivery, emission in sql_deliveries
        }
        if not _json_values_equal_exact(sql_delivery_projection, deliveries):
            raise RuntimeError("handler delivery projection diverges from the journal")
        for emission in sql_emissions:
            manifest = self.resolve_manifest(
                runtime_profile_id=emission.runtime_profile_id,
                event_type=emission.event_type,
                manifest_version=emission.manifest_version,
            )
            if manifest.manifest_hash != emission.manifest_hash:
                raise RuntimeError("emission manifest snapshot is not authoritative")
        return ReplayResult(
            anchor=actual_anchor,
            emissions=tuple(self._emission_record(row) for row in sql_emissions),
            deliveries=tuple(
                self._delivery_record(delivery, emission)
                for delivery, emission in sql_deliveries
            ),
        )

    def _require_authority(self) -> None:
        _require_delivery_session_capability(
            self._session,
            expected=self._delivery_capability,
            expected_token=self._delivery_capability_token,
        )

    def _ensure_anchor(self) -> EventDeliveryAnchor:
        anchor = self._session.get(EventDeliveryAnchor, self._authority_id)
        if anchor is None:
            anchor = EventDeliveryAnchor(
                authority_id=self._authority_id,
                authority_version=self._authority_version,
                last_sequence=0,
                last_hash=GENESIS_HASH,
            )
            self._session.add(anchor)
            self._session.flush()
        elif anchor.authority_version != self._authority_version:
            raise RuntimeError("delivery authority version mismatch")
        return anchor

    def _anchor(self) -> EventDeliveryAnchor:
        anchor = self._session.get(EventDeliveryAnchor, self._authority_id)
        if anchor is None:
            raise RuntimeError("delivery authority has not been initialized")
        if anchor.authority_version != self._authority_version:
            raise RuntimeError("delivery authority version mismatch")
        return anchor

    def _append_journal(
        self,
        *,
        event_type: JournalEventType,
        emission_effect_id: str,
        handler_effect_digest: str | None,
        fencing_generation: int,
        occurred_at: datetime,
        payload: Mapping[str, object],
    ) -> EventDeliveryJournal:
        anchor = self._anchor()
        sequence = anchor.last_sequence + 1
        payload_json = canonical_json_text(payload)
        payload_hash = sha256_canonical(payload)
        event_hash = journal_event_hash(
            sequence=sequence,
            authority_id=self._authority_id,
            authority_version=self._authority_version,
            event_type=event_type,
            emission_effect_id=emission_effect_id,
            handler_effect_digest=handler_effect_digest,
            fencing_generation=fencing_generation,
            occurred_at=occurred_at,
            payload_hash=payload_hash,
            previous_hash=anchor.last_hash,
        )
        row = EventDeliveryJournal(
            authority_id=self._authority_id,
            sequence=sequence,
            authority_version=self._authority_version,
            event_type=event_type.value,
            emission_effect_id=emission_effect_id,
            handler_effect_id=handler_effect_digest,
            fencing_generation=fencing_generation,
            occurred_at=occurred_at,
            payload_json=payload_json,
            payload_hash=payload_hash,
            previous_hash=anchor.last_hash,
            event_hash=event_hash,
        )
        self._session.add(row)
        anchor.last_sequence = sequence
        anchor.last_hash = event_hash
        self._session.flush()
        return row

    def _find_emission_identity(self, dto: PreparedEmission) -> EventBusEmission | None:
        statement: Select[tuple[EventBusEmission]] = select(EventBusEmission).where(
            EventBusEmission.authority_id == self._authority_id,
            (
                (EventBusEmission.source_identity == dto.source_identity)
                | (EventBusEmission.emission_effect_id == dto.emission_effect_id)
                | (
                    (EventBusEmission.consumer_id == dto.consumer_id)
                    & (EventBusEmission.source_sequence == dto.source_sequence)
                )
            ),
        )
        return self._session.execute(statement).scalars().first()

    def _existing_emission_result(
        self,
        row: EventBusEmission,
        dto: PreparedEmission,
        manifest: PreparedManifest,
    ) -> EmissionApplyResult:
        same = self._emission_matches(row, dto)
        deliveries = self._deliveries_for_emission(row.id)
        expected_static = [
            (
                item.handler_id,
                item.handler_version,
                item.required,
                item.ordinal,
                item.dispatch_class.value,
            )
            for item in manifest.entries
        ]
        actual_static = [
            (
                item.handler_id,
                item.handler_version,
                item.required,
                item.ordinal,
                item.dispatch_class,
            )
            for item in deliveries
        ]
        same = same and actual_static == expected_static
        accepted_hash = self._journal_hash(
            row.emission_effect_id, JournalEventType.EMISSION_ACCEPTED
        )
        completed_hash = self._journal_hash(
            row.emission_effect_id, JournalEventType.EMISSION_COMPLETED, required=False
        )
        return EmissionApplyResult(
            status=ApplyStatus.ALREADY_APPLIED if same else ApplyStatus.CONFLICT,
            emission=self._emission_record(row),
            deliveries=tuple(self._delivery_record(item, row) for item in deliveries),
            emission_accepted_hash=accepted_hash,
            emission_completed_hash=completed_hash,
        )

    def _emission_matches(self, row: EventBusEmission, dto: PreparedEmission) -> bool:
        return self._emission_projection(row) == {
            "authority_id": dto.authority_id,
            "authority_version": dto.authority_version,
            "source_identity": dto.source_identity,
            "consumer_id": dto.consumer_id,
            "outcome_id": dto.outcome_id,
            "outcome_hash": dto.outcome_hash,
            "receipt_hash": dto.receipt_hash,
            "source_sequence": dto.source_sequence,
            "event_type": dto.event_type,
            "occurred_at": dto.occurred_at_text,
            "accepted_at": self._emission_projection(row)["accepted_at"],
            "payload": json.loads(dto.payload_json),
            "payload_hash": dto.payload_hash,
            "runtime_profile_id": dto.runtime_profile_id,
            "manifest_version": dto.manifest_version,
            "manifest_hash": dto.manifest_hash,
            "emission_effect_id": dto.emission_effect_id,
            "accepted_sequence": row.accepted_sequence,
            "status": row.status,
        }

    def _manifest_record(self, row: EventHandlerManifest) -> ManifestRecord:
        return ManifestRecord(
            runtime_profile_id=row.runtime_profile_id,
            event_type=row.event_type,
            manifest_version=row.manifest_version,
            entries=self._manifest_entries(row.id),
            manifest_hash=row.manifest_hash,
            registered_at=self._normalized_time(row.registered_at),
        )

    def _manifest_entries(self, manifest_id: int) -> tuple[HandlerManifestEntry, ...]:
        rows = self._session.execute(
            select(EventHandlerManifestEntry)
            .where(EventHandlerManifestEntry.manifest_id == manifest_id)
            .order_by(EventHandlerManifestEntry.ordinal)
        ).scalars().all()
        return tuple(
            HandlerManifestEntry(
                handler_id=row.handler_id,
                handler_version=row.handler_version,
                required=row.required,
                ordinal=row.ordinal,
                dispatch_class=DispatchClass(row.dispatch_class),
            )
            for row in rows
        )

    def _deliveries_for_emission(self, emission_id: int) -> list[EventHandlerDelivery]:
        return list(
            self._session.execute(
                select(EventHandlerDelivery)
                .where(EventHandlerDelivery.emission_id == emission_id)
                .order_by(EventHandlerDelivery.ordinal)
            ).scalars().all()
        )

    def _delivery_and_emission(
        self, handler_effect_digest: str
    ) -> tuple[EventHandlerDelivery, EventBusEmission]:
        from agicore.core.event_delivery_contracts import canonical_hash

        digest = canonical_hash(handler_effect_digest, field="handler_effect_id")
        row = self._session.execute(
            select(EventHandlerDelivery, EventBusEmission)
            .join(EventBusEmission, EventBusEmission.id == EventHandlerDelivery.emission_id)
            .where(
                EventHandlerDelivery.authority_id == self._authority_id,
                EventHandlerDelivery.handler_effect_id == digest,
            )
        ).one_or_none()
        if row is None:
            raise RuntimeError("unknown handler delivery")
        return row[0], row[1]

    @staticmethod
    def _assert_fencing(
        delivery: EventHandlerDelivery, generation: int, worker: str
    ) -> None:
        if (
            not isinstance(generation, int)
            or isinstance(generation, bool)
            or generation <= 0
        ):
            raise ValueError("fencing_generation must be a positive integer")
        if delivery.fencing_generation != generation or delivery.worker_identity != worker:
            raise RuntimeError("stale or foreign handler fencing token")

    def _journal_hash(
        self,
        emission_effect_id: str,
        event_type: JournalEventType,
        *,
        required: bool = True,
    ) -> str | None:
        value = self._session.execute(
            select(EventDeliveryJournal.event_hash).where(
                EventDeliveryJournal.authority_id == self._authority_id,
                EventDeliveryJournal.emission_effect_id == emission_effect_id,
                EventDeliveryJournal.event_type == event_type.value,
            )
        ).scalar_one_or_none()
        if required and value is None:
            raise RuntimeError(f"missing authoritative {event_type.value} proof")
        return value

    def _accepted_payload(
        self, emission: EventBusEmission, deliveries: list[EventHandlerDelivery]
    ) -> Mapping[str, object]:
        return {
            "emission": self._emission_projection(emission),
            "deliveries": [self._delivery_projection(item, emission) for item in deliveries],
            "manifest_snapshot": [
                {
                    "handler_id": item.handler_id,
                    "handler_version": item.handler_version,
                    "required": item.required,
                    "ordinal": item.ordinal,
                    "dispatch_class": item.dispatch_class,
                }
                for item in deliveries
            ],
        }

    def _emission_projection(self, row: EventBusEmission) -> dict[str, object]:
        _, occurred = canonical_time(self._normalized_time(row.occurred_at), field="occurred_at")
        _, accepted = canonical_time(self._normalized_time(row.accepted_at), field="accepted_at")
        return {
            "authority_id": row.authority_id,
            "authority_version": row.authority_version,
            "source_identity": row.source_identity,
            "consumer_id": row.consumer_id,
            "outcome_id": row.outcome_id,
            "outcome_hash": row.outcome_hash,
            "receipt_hash": row.receipt_hash,
            "source_sequence": row.source_sequence,
            "event_type": row.event_type,
            "occurred_at": occurred,
            "accepted_at": accepted,
            "payload": json.loads(row.payload_json),
            "payload_hash": row.payload_hash,
            "runtime_profile_id": row.runtime_profile_id,
            "manifest_version": row.manifest_version,
            "manifest_hash": row.manifest_hash,
            "emission_effect_id": row.emission_effect_id,
            "accepted_sequence": row.accepted_sequence,
            "status": row.status,
        }

    def _delivery_projection(
        self, row: EventHandlerDelivery, emission: EventBusEmission
    ) -> dict[str, object]:
        claimed = None
        if row.claimed_at is not None:
            _, claimed = canonical_time(self._normalized_time(row.claimed_at), field="claimed_at")
        return {
            "emission_effect_id": row.emission_effect_id,
            "handler_effect_id": row.handler_effect_id,
            "consumer_id": emission.consumer_id,
            "source_sequence": emission.source_sequence,
            "accepted_sequence": emission.accepted_sequence,
            "handler_id": row.handler_id,
            "handler_version": row.handler_version,
            "required": row.required,
            "ordinal": row.ordinal,
            "dispatch_class": row.dispatch_class,
            "status": row.status,
            "fencing_generation": row.fencing_generation,
            "worker_identity": row.worker_identity,
            "claimed_at": claimed,
            "result_status": row.result_status,
            "result_hash": row.result_hash,
            "result": json.loads(row.result_json) if row.result_json is not None else None,
        }

    def _emission_record(self, row: EventBusEmission) -> EmissionRecord:
        return EmissionRecord(
            source_identity=row.source_identity,
            consumer_id=row.consumer_id,
            outcome_id=row.outcome_id,
            outcome_hash=row.outcome_hash,
            receipt_hash=row.receipt_hash,
            source_sequence=row.source_sequence,
            event_type=row.event_type,
            occurred_at=self._normalized_time(row.occurred_at),
            accepted_at=self._normalized_time(row.accepted_at),
            payload=json.loads(row.payload_json),
            payload_hash=row.payload_hash,
            runtime_profile_id=row.runtime_profile_id,
            manifest_version=row.manifest_version,
            manifest_hash=row.manifest_hash,
            emission_effect_id=row.emission_effect_id,
            accepted_sequence=row.accepted_sequence,
            status=row.status,
        )

    def _delivery_record(
        self, row: EventHandlerDelivery, emission: EventBusEmission
    ) -> DeliveryRecord:
        return DeliveryRecord(
            emission_effect_id=row.emission_effect_id,
            handler_effect_id=row.handler_effect_id,
            consumer_id=emission.consumer_id,
            source_sequence=emission.source_sequence,
            accepted_sequence=emission.accepted_sequence,
            handler_id=row.handler_id,
            handler_version=row.handler_version,
            required=row.required,
            ordinal=row.ordinal,
            dispatch_class=DispatchClass(row.dispatch_class),
            status=row.status,
            fencing_generation=row.fencing_generation,
            worker_identity=row.worker_identity,
            claimed_at=(
                self._normalized_time(row.claimed_at) if row.claimed_at is not None else None
            ),
            result_status=(ApplyStatus(row.result_status) if row.result_status else None),
            result_hash=row.result_hash,
            result=json.loads(row.result_json) if row.result_json is not None else None,
        )

    def _replay_transition(
        self,
        row: EventDeliveryJournal,
        payload: Mapping[str, object],
        emissions: dict[str, dict[str, object]],
        deliveries: dict[str, dict[str, object]],
    ) -> None:
        event_type = JournalEventType(row.event_type)
        emission_id = row.emission_effect_id
        if event_type is JournalEventType.EMISSION_ACCEPTED:
            if row.handler_effect_id is not None or row.fencing_generation != 0:
                raise RuntimeError("EMISSION_ACCEPTED journal header is not canonical")
            if emission_id in emissions:
                raise RuntimeError("duplicate EMISSION_ACCEPTED transition")
            emission = payload.get("emission")
            initial_deliveries = payload.get("deliveries")
            manifest_snapshot = payload.get("manifest_snapshot")
            if (
                set(payload) != {"emission", "deliveries", "manifest_snapshot"}
                or
                not isinstance(emission, dict)
                or not isinstance(initial_deliveries, list)
                or not isinstance(manifest_snapshot, list)
            ):
                raise RuntimeError("invalid EMISSION_ACCEPTED payload")
            prepared = self._prepare_replayed_emission(emission)
            expected_emission = self._prepared_emission_projection(
                prepared,
                accepted_sequence=row.sequence,
                status="ACCEPTED",
            )
            if (
                not _json_values_equal_exact(emission, expected_emission)
                or emission_id != prepared.emission_effect_id
            ):
                raise RuntimeError("EMISSION_ACCEPTED semantic reconstruction failed")
            if self._render_time(row.occurred_at) != prepared.accepted_at_text:
                raise RuntimeError("EMISSION_ACCEPTED journal time is not canonical")
            manifest = self.resolve_manifest(
                runtime_profile_id=prepared.runtime_profile_id,
                event_type=prepared.event_type,
                manifest_version=prepared.manifest_version,
            )
            if manifest.manifest_hash != prepared.manifest_hash:
                raise RuntimeError("EMISSION_ACCEPTED manifest hash is not authoritative")
            expected_snapshot = self._manifest_snapshot(manifest)
            expected_deliveries = [
                self._initial_delivery_projection(
                    prepared,
                    accepted_sequence=row.sequence,
                    entry=entry,
                )
                for entry in manifest.entries
            ]
            if not _json_values_equal_exact(
                manifest_snapshot, expected_snapshot
            ) or not _json_values_equal_exact(
                initial_deliveries, expected_deliveries
            ):
                raise RuntimeError("EMISSION_ACCEPTED manifest snapshot is not authoritative")
            prior_consumer_sequences = [
                int(item["source_sequence"])
                for item in emissions.values()
                if item["consumer_id"] == prepared.consumer_id
            ]
            if (
                prior_consumer_sequences
                and prepared.source_sequence <= max(prior_consumer_sequences)
            ):
                raise RuntimeError(
                    "EMISSION_ACCEPTED consumer source_sequence is not strictly increasing"
                )
            emissions[emission_id] = expected_emission
            for item in expected_deliveries:
                effect_id = item["handler_effect_id"]
                if effect_id in deliveries:
                    raise RuntimeError("duplicate initial handler delivery")
                deliveries[effect_id] = item
            return
        if emission_id not in emissions:
            raise RuntimeError("journal transition precedes EMISSION_ACCEPTED")
        if event_type is JournalEventType.EMISSION_COMPLETED:
            if row.handler_effect_id is not None or row.fencing_generation != 0:
                raise RuntimeError("EMISSION_COMPLETED journal header is not canonical")
            if emissions[emission_id]["status"] == "COMPLETED":
                raise RuntimeError("duplicate EMISSION_COMPLETED transition")
            required = [
                item
                for item in deliveries.values()
                if item["emission_effect_id"] == emission_id and item["required"]
            ]
            if any(item["status"] != "COMPLETED" for item in required):
                raise RuntimeError("EMISSION_COMPLETED precedes required handlers")
            expected_required_ids = [
                item["handler_effect_id"]
                for item in sorted(required, key=lambda item: int(item["ordinal"]))
            ]
            if payload != {
                "required_handler_effect_ids": expected_required_ids,
                "completion_scope": "required_handlers_only",
            }:
                raise RuntimeError("EMISSION_COMPLETED proof is not canonical")
            emissions[emission_id]["status"] = "COMPLETED"
            return
        effect_id = row.handler_effect_id
        if effect_id is None or effect_id not in deliveries:
            raise RuntimeError("journal transition references an unknown handler")
        delivery = deliveries[effect_id]
        expected_effect_id = handler_effect_id(
            emission_effect_id=emission_id,
            handler_id=str(delivery["handler_id"]),
            handler_version=str(delivery["handler_version"]),
        )
        if (
            delivery["emission_effect_id"] != emission_id
            or effect_id != expected_effect_id
            or row.fencing_generation <= 0
        ):
            raise RuntimeError("handler journal transition cross-link is invalid")
        if event_type is JournalEventType.HANDLER_CLAIMED:
            if set(payload) != {"worker_identity"}:
                raise RuntimeError("HANDLER_CLAIMED proof is not canonical")
            if delivery["status"] != "PENDING":
                raise RuntimeError("handler claim has an invalid predecessor")
            claimed_emission = emissions[emission_id]
            incomplete_predecessor = any(
                item["consumer_id"] == claimed_emission["consumer_id"]
                and int(item["source_sequence"])
                < int(claimed_emission["source_sequence"])
                and item["status"] != "COMPLETED"
                for item in emissions.values()
            )
            if incomplete_predecessor:
                raise RuntimeError(
                    "handler claim violates consumer head-of-line causality"
                )
            if row.fencing_generation != int(delivery["fencing_generation"]) + 1:
                raise RuntimeError("handler claim fencing is not monotonic")
            canonical_identity(payload["worker_identity"], field="worker_identity")
            delivery.update(
                status="CLAIMED",
                fencing_generation=row.fencing_generation,
                worker_identity=payload["worker_identity"],
                claimed_at=self._render_time(row.occurred_at),
            )
        elif event_type is JournalEventType.HANDLER_CLAIM_RECOVERED:
            if set(payload) != {
                "worker_identity",
                "previous_worker_identity",
                "observed_generation",
                "preserved_status",
            }:
                raise RuntimeError("HANDLER_CLAIM_RECOVERED proof is not canonical")
            if delivery["status"] not in {"CLAIMED", "APPLIED"}:
                raise RuntimeError("handler recovery has an invalid predecessor")
            observed_generation = payload["observed_generation"]
            if type(observed_generation) is not int or observed_generation <= 0:
                raise RuntimeError(
                    "handler recovery observed_generation must be a positive integer"
                )
            previous_generation = int(delivery["fencing_generation"])
            if (
                row.fencing_generation != previous_generation + 1
                or observed_generation != previous_generation
                or payload["previous_worker_identity"] != delivery["worker_identity"]
                or payload["preserved_status"] != delivery["status"]
            ):
                raise RuntimeError("handler recovery fencing is not monotonic")
            canonical_identity(payload["worker_identity"], field="worker_identity")
            delivery.update(
                fencing_generation=row.fencing_generation,
                worker_identity=payload["worker_identity"],
                claimed_at=self._render_time(row.occurred_at),
            )
        elif event_type is JournalEventType.HANDLER_APPLIED:
            if set(payload) != {
                "worker_identity",
                "result_status",
                "result_hash",
                "result",
            }:
                raise RuntimeError("HANDLER_APPLIED proof is not canonical")
            if delivery["status"] != "CLAIMED":
                raise RuntimeError("handler result has an invalid predecessor")
            if (
                row.fencing_generation != delivery["fencing_generation"]
                or payload["worker_identity"] != delivery["worker_identity"]
            ):
                raise RuntimeError("HANDLER_APPLIED fencing proof is invalid")
            rebuilt_result_hash, _, _ = synthetic_result_hash(
                handler_effect_digest=effect_id,
                status=ApplyStatus(payload["result_status"]),
                payload=payload["result"],
            )
            if payload["result_hash"] != rebuilt_result_hash:
                raise RuntimeError("HANDLER_APPLIED result hash is invalid")
            delivery.update(
                status=(
                    "CONFLICT"
                    if payload["result_status"] == ApplyStatus.CONFLICT.value
                    else "APPLIED"
                ),
                result_status=payload["result_status"],
                result_hash=payload["result_hash"],
                result=payload["result"],
            )
        elif event_type is JournalEventType.HANDLER_COMPLETED:
            if set(payload) != {"worker_identity", "result_hash"}:
                raise RuntimeError("HANDLER_COMPLETED proof is not canonical")
            if delivery["status"] != "APPLIED":
                raise RuntimeError("handler completion has an invalid predecessor")
            if (
                row.fencing_generation != delivery["fencing_generation"]
                or payload["worker_identity"] != delivery["worker_identity"]
                or payload["result_hash"] != delivery["result_hash"]
            ):
                raise RuntimeError("HANDLER_COMPLETED fencing proof is invalid")
            delivery["status"] = "COMPLETED"

    def _prepare_replayed_emission(
        self, emission: Mapping[str, object]
    ) -> PreparedEmission:
        expected_keys = {
            "authority_id",
            "authority_version",
            "source_identity",
            "consumer_id",
            "outcome_id",
            "outcome_hash",
            "receipt_hash",
            "source_sequence",
            "event_type",
            "occurred_at",
            "accepted_at",
            "payload",
            "payload_hash",
            "runtime_profile_id",
            "manifest_version",
            "manifest_hash",
            "emission_effect_id",
            "accepted_sequence",
            "status",
        }
        if set(emission) != expected_keys:
            raise RuntimeError("EMISSION_ACCEPTED projection schema is not canonical")
        try:
            prepared = prepare_emission(
                authority_id=emission["authority_id"],
                authority_version=emission["authority_version"],
                runtime_profile_id=emission["runtime_profile_id"],
                manifest_version=emission["manifest_version"],
                manifest_hash=emission["manifest_hash"],
                source_identity=emission["source_identity"],
                consumer_id=emission["consumer_id"],
                outcome_id=emission["outcome_id"],
                outcome_hash=emission["outcome_hash"],
                receipt_hash=emission["receipt_hash"],
                source_sequence=emission["source_sequence"],
                event_type=emission["event_type"],
                occurred_at=self._parse_canonical_time(
                    emission["occurred_at"], field="occurred_at"
                ),
                accepted_at=self._parse_canonical_time(
                    emission["accepted_at"], field="accepted_at"
                ),
                payload=emission["payload"],
            )
        except (TypeError, ValueError) as exc:
            raise RuntimeError("EMISSION_ACCEPTED values are not canonical") from exc
        if (
            prepared.authority_id != self._authority_id
            or prepared.authority_version != self._authority_version
        ):
            raise RuntimeError("EMISSION_ACCEPTED authority is not canonical")
        return prepared

    @staticmethod
    def _prepared_emission_projection(
        prepared: PreparedEmission, *, accepted_sequence: int, status: str
    ) -> dict[str, object]:
        return {
            "authority_id": prepared.authority_id,
            "authority_version": prepared.authority_version,
            "source_identity": prepared.source_identity,
            "consumer_id": prepared.consumer_id,
            "outcome_id": prepared.outcome_id,
            "outcome_hash": prepared.outcome_hash,
            "receipt_hash": prepared.receipt_hash,
            "source_sequence": prepared.source_sequence,
            "event_type": prepared.event_type,
            "occurred_at": prepared.occurred_at_text,
            "accepted_at": prepared.accepted_at_text,
            "payload": json.loads(prepared.payload_json),
            "payload_hash": prepared.payload_hash,
            "runtime_profile_id": prepared.runtime_profile_id,
            "manifest_version": prepared.manifest_version,
            "manifest_hash": prepared.manifest_hash,
            "emission_effect_id": prepared.emission_effect_id,
            "accepted_sequence": accepted_sequence,
            "status": status,
        }

    @staticmethod
    def _manifest_snapshot(manifest: PreparedManifest) -> list[dict[str, object]]:
        return [
            {
                "handler_id": entry.handler_id,
                "handler_version": entry.handler_version,
                "required": entry.required,
                "ordinal": entry.ordinal,
                "dispatch_class": entry.dispatch_class.value,
            }
            for entry in manifest.entries
        ]

    @staticmethod
    def _initial_delivery_projection(
        prepared: PreparedEmission,
        *,
        accepted_sequence: int,
        entry: HandlerManifestEntry,
    ) -> dict[str, object]:
        return {
            "emission_effect_id": prepared.emission_effect_id,
            "handler_effect_id": handler_effect_id(
                emission_effect_id=prepared.emission_effect_id,
                handler_id=entry.handler_id,
                handler_version=entry.handler_version,
            ),
            "consumer_id": prepared.consumer_id,
            "source_sequence": prepared.source_sequence,
            "accepted_sequence": accepted_sequence,
            "handler_id": entry.handler_id,
            "handler_version": entry.handler_version,
            "required": entry.required,
            "ordinal": entry.ordinal,
            "dispatch_class": entry.dispatch_class.value,
            "status": "PENDING",
            "fencing_generation": 0,
            "worker_identity": None,
            "claimed_at": None,
            "result_status": None,
            "result_hash": None,
            "result": None,
        }

    @staticmethod
    def _parse_canonical_time(value: object, *, field: str) -> datetime:
        if not isinstance(value, str):
            raise ValueError(f"{field} must be a canonical timestamp")
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"{field} must be a canonical timestamp") from exc
        normalized, rendered = canonical_time(parsed, field=field)
        if rendered != value:
            raise ValueError(f"{field} must be a canonical timestamp")
        return normalized

    @staticmethod
    def _normalized_time(value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @classmethod
    def _render_time(cls, value: datetime) -> str:
        return canonical_time(cls._normalized_time(value), field="journal time")[1]


__all__ = ["EventDeliveryRepository"]
