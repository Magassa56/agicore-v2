"""Bus-owned service for durable EventBus delivery progression."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime

from agicore.core.event_delivery_contracts import (
    AnchorRecord,
    ApplyStatus,
    ClaimResult,
    DeliveryRecord,
    EmissionApplyResult,
    HandlerManifestEntry,
    ManifestApplyResult,
    ReplayResult,
    canonical_identity,
    canonical_source_sequence,
    prepare_emission,
    prepare_manifest,
)

from ..adapters.sqlalchemy_engine import SqlAlchemyEngine
from ..repositories.event_delivery_repository import EventDeliveryRepository


class EventDeliveryService:
    """Durable authority bound to one profile and manifest version.

    The emission API deliberately has no handler or manifest argument. Those are
    registered and resolved by this authority using the profile/version fixed at
    construction time.
    """

    def __init__(
        self,
        engine: SqlAlchemyEngine,
        *,
        authority_id: str,
        authority_version: str,
        runtime_profile_id: str,
        manifest_version: str,
    ) -> None:
        if (
            not engine.delivery_authority_enabled
            or engine.engine.dialect.name != "sqlite"
        ):
            raise RuntimeError(
                "EventDeliveryService requires SQLite delivery authority mode"
            )
        self._engine = engine
        self._authority_id = canonical_identity(authority_id, field="authority_id")
        self._authority_version = canonical_identity(
            authority_version, field="authority_version"
        )
        self._runtime_profile_id = canonical_identity(
            runtime_profile_id, field="runtime_profile_id"
        )
        self._manifest_version = canonical_identity(
            manifest_version, field="manifest_version"
        )

    def register_manifest(
        self,
        *,
        event_type: str,
        entries: Sequence[HandlerManifestEntry],
        registered_at: datetime,
    ) -> ManifestApplyResult:
        """Register the exact bus-owned manifest used by this service instance."""
        prepared = prepare_manifest(
            runtime_profile_id=self._runtime_profile_id,
            event_type=event_type,
            manifest_version=self._manifest_version,
            entries=entries,
        )
        with self._engine.delivery_session() as session:
            return self._repository(session).register_manifest(
                prepared, registered_at=registered_at
            )

    def accept_emission(
        self,
        *,
        source_identity: str,
        consumer_id: str,
        outcome_id: str,
        outcome_hash: str,
        receipt_hash: str,
        source_sequence: int,
        event_type: str,
        occurred_at: datetime,
        accepted_at: datetime,
        payload: Mapping[str, object],
    ) -> EmissionApplyResult:
        """Atomically accept one canonical emission and its resolved manifest."""
        source_sequence = canonical_source_sequence(source_sequence)
        with self._engine.delivery_session() as session:
            repository = self._repository(session)
            manifest = repository.resolve_manifest(
                runtime_profile_id=self._runtime_profile_id,
                event_type=event_type,
                manifest_version=self._manifest_version,
            )
            prepared = prepare_emission(
                authority_id=self._authority_id,
                authority_version=self._authority_version,
                runtime_profile_id=self._runtime_profile_id,
                manifest_version=self._manifest_version,
                manifest_hash=manifest.manifest_hash,
                source_identity=source_identity,
                consumer_id=consumer_id,
                outcome_id=outcome_id,
                outcome_hash=outcome_hash,
                receipt_hash=receipt_hash,
                source_sequence=source_sequence,
                event_type=event_type,
                occurred_at=occurred_at,
                accepted_at=accepted_at,
                payload=payload,
            )
            return repository.accept_emission(prepared)

    def pending_deliveries(self) -> tuple[DeliveryRecord, ...]:
        """Read incomplete deliveries in authoritative causal order."""
        with self._engine.delivery_session() as session:
            return self._repository(session).pending_deliveries()

    def claim(
        self,
        *,
        handler_effect_id: str,
        worker_identity: str,
        claimed_at: datetime,
    ) -> ClaimResult:
        """CAS-claim one delivery and obtain its fencing generation."""
        with self._engine.delivery_session() as session:
            return self._repository(session).claim(
                handler_effect_digest=handler_effect_id,
                worker_identity=worker_identity,
                claimed_at=claimed_at,
            )

    def recover_claim(
        self,
        *,
        handler_effect_id: str,
        observed_generation: int,
        worker_identity: str,
        recovered_at: datetime,
    ) -> ClaimResult:
        """Explicitly recover a claim and fence its former worker."""
        with self._engine.delivery_session() as session:
            return self._repository(session).recover_claim(
                handler_effect_digest=handler_effect_id,
                observed_generation=observed_generation,
                worker_identity=worker_identity,
                recovered_at=recovered_at,
            )

    def record_synthetic_handler_result(
        self,
        *,
        handler_effect_id: str,
        fencing_generation: int,
        worker_identity: str,
        status: ApplyStatus,
        payload: Mapping[str, object],
        applied_at: datetime,
    ) -> DeliveryRecord:
        """Record a synthetic B1 result; this does not execute a business handler."""
        with self._engine.delivery_session() as session:
            return self._repository(session).record_handler_result(
                handler_effect_digest=handler_effect_id,
                fencing_generation=fencing_generation,
                worker_identity=worker_identity,
                status=status,
                payload=payload,
                applied_at=applied_at,
            )

    def complete_handler(
        self,
        *,
        handler_effect_id: str,
        fencing_generation: int,
        worker_identity: str,
        completed_at: datetime,
    ) -> DeliveryRecord:
        """Confirm a synthetic applied result under its current fencing token."""
        with self._engine.delivery_session() as session:
            return self._repository(session).complete_handler(
                handler_effect_digest=handler_effect_id,
                fencing_generation=fencing_generation,
                worker_identity=worker_identity,
                completed_at=completed_at,
            )

    def anchor(self) -> AnchorRecord:
        """Return the current immutable final journal anchor."""
        with self._engine.delivery_session() as session:
            return self._repository(session).anchor()

    def replay(self, *, expected_anchor: AnchorRecord | None = None) -> ReplayResult:
        """Verify the journal and rebuild its exact SQL projection."""
        with self._engine.delivery_session() as session:
            return self._repository(session).replay(expected_anchor=expected_anchor)

    def _repository(self, session) -> EventDeliveryRepository:
        return EventDeliveryRepository(
            session,
            authority_id=self._authority_id,
            authority_version=self._authority_version,
        )


__all__ = ["EventDeliveryService"]
