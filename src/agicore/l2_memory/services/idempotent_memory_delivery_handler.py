"""Bounded offline worker for one durable idempotent memory delivery."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime

from agicore.core.event_delivery_contracts import (
    ApplyStatus,
    ClaimStatus,
    DeliveryRecord,
    EmissionRecord,
    canonical_json_text,
    canonical_identity,
)

from ..schemas.event import IdempotentEventApplyStatus
from .event_delivery_service import EventDeliveryService
from .memory_service import MemoryService


@dataclass(frozen=True)
class MemoryDeliveryRunResult:
    """Outcome of one bounded worker iteration."""

    status: str
    delivery: DeliveryRecord | None


class IdempotentMemoryDeliveryHandler:
    """Apply one explicitly registered memory handler without using EventBus legacy."""

    HANDLER_ID = "idempotent-memory-delivery"
    HANDLER_VERSION = "v1"
    RUNTIME_PROFILE_ID = "offline-memory-audit-v1"

    def __init__(
        self,
        delivery: EventDeliveryService,
        memory: MemoryService,
    ) -> None:
        self._delivery = delivery
        self._memory = memory

    def run_one(
        self,
        *,
        worker_identity: str,
        observed_at: datetime,
        recover_stale_claim: bool = False,
    ) -> MemoryDeliveryRunResult:
        """Process at most one causal delivery and return without polling."""
        worker = canonical_identity(worker_identity, field="worker_identity")
        pending = self._delivery.pending_deliveries()
        candidate = next(
            (
                item
                for item in pending
                if item.handler_id == self.HANDLER_ID
                and item.handler_version == self.HANDLER_VERSION
            ),
            None,
        )
        if candidate is None:
            return MemoryDeliveryRunResult(status="IDLE", delivery=None)

        claimed = self._obtain_claim(
            candidate,
            worker_identity=worker,
            observed_at=observed_at,
            recover_stale_claim=recover_stale_claim,
        )
        if claimed is None:
            return MemoryDeliveryRunResult(status="UNAVAILABLE", delivery=candidate)
        if claimed.status == "APPLIED":
            completed = self._delivery.complete_handler(
                handler_effect_id=claimed.handler_effect_id,
                fencing_generation=claimed.fencing_generation,
                worker_identity=worker,
                completed_at=observed_at,
            )
            return MemoryDeliveryRunResult(status="COMPLETED", delivery=completed)

        emission = self._resolve_emission(claimed.emission_effect_id)
        memory_payload = {
            "schema": "agicore.offline-memory-audit.v1",
            "emission_effect_id": emission.emission_effect_id,
            "source_identity": emission.source_identity,
            "consumer_id": emission.consumer_id,
            "outcome_id": emission.outcome_id,
            "outcome_hash": emission.outcome_hash,
            "receipt_hash": emission.receipt_hash,
            "source_sequence": emission.source_sequence,
            "event_type": emission.event_type,
            "payload": json.loads(canonical_json_text(emission.payload)),
        }
        applied = self._memory.create_event_idempotent(
            effect_id=claimed.handler_effect_id,
            occurred_at=emission.occurred_at,
            event_type="delivery.memory.applied",
            payload=memory_payload,
        )
        stable_status = (
            ApplyStatus.CONFLICT
            if applied.status is IdempotentEventApplyStatus.CONFLICT
            else ApplyStatus.APPLIED_CONFIRMED
        )
        recorded = self._delivery.record_synthetic_handler_result(
            handler_effect_id=claimed.handler_effect_id,
            fencing_generation=claimed.fencing_generation,
            worker_identity=worker,
            status=stable_status,
            payload={
                "effect_id": applied.event.effect_id,
                "payload_hash": applied.event.payload_hash,
            },
            applied_at=observed_at,
        )
        if stable_status is ApplyStatus.CONFLICT:
            return MemoryDeliveryRunResult(status="CONFLICT", delivery=recorded)
        completed = self._delivery.complete_handler(
            handler_effect_id=recorded.handler_effect_id,
            fencing_generation=recorded.fencing_generation,
            worker_identity=worker,
            completed_at=observed_at,
        )
        return MemoryDeliveryRunResult(status="COMPLETED", delivery=completed)

    def _obtain_claim(
        self,
        delivery: DeliveryRecord,
        *,
        worker_identity: str,
        observed_at: datetime,
        recover_stale_claim: bool,
    ) -> DeliveryRecord | None:
        if delivery.status in {"CLAIMED", "APPLIED"}:
            if delivery.worker_identity == worker_identity:
                return delivery
            if not recover_stale_claim:
                return None
            recovered = self._delivery.recover_claim(
                handler_effect_id=delivery.handler_effect_id,
                observed_generation=delivery.fencing_generation,
                worker_identity=worker_identity,
                recovered_at=observed_at,
            )
            return (
                recovered.delivery
                if recovered.status is ClaimStatus.CLAIMED
                else None
            )
        claimed = self._delivery.claim(
            handler_effect_id=delivery.handler_effect_id,
            worker_identity=worker_identity,
            claimed_at=observed_at,
        )
        if claimed.status not in {ClaimStatus.CLAIMED, ClaimStatus.ALREADY_CLAIMED}:
            return None
        return claimed.delivery

    def _resolve_emission(self, emission_effect_id: str) -> EmissionRecord:
        replay = self._delivery.replay()
        for emission in replay.emissions:
            if emission.emission_effect_id == emission_effect_id:
                return emission
        raise RuntimeError("delivery emission is absent from authoritative replay")


__all__ = ["IdempotentMemoryDeliveryHandler", "MemoryDeliveryRunResult"]
