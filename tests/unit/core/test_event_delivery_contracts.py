from __future__ import annotations

import inspect
from datetime import datetime, timezone

import pytest

from agicore.core.event_delivery_contracts import (
    ApplyStatus,
    DispatchClass,
    HandlerManifestEntry,
    JournalEventType,
    journal_event_hash,
    prepare_emission,
    prepare_manifest,
    synthetic_result_hash,
)
from agicore.l2_memory.services.event_delivery_service import EventDeliveryService


NOW = datetime(2026, 8, 27, 9, 0, tzinfo=timezone.utc)
HASH_A = "a" * 64
HASH_B = "b" * 64


def _entry(**changes) -> HandlerManifestEntry:
    values = {
        "handler_id": "signal-loop",
        "handler_version": "v1",
        "required": True,
        "ordinal": 0,
        "dispatch_class": DispatchClass.DIRECT,
    }
    values.update(changes)
    return HandlerManifestEntry(**values)


def test_manifest_is_canonical_ordered_and_deeply_immutable() -> None:
    prepared = prepare_manifest(
        runtime_profile_id="paper-trading-v1",
        event_type="agent.execution.order.processed",
        manifest_version="v1",
        entries=(
            _entry(handler_id="runtime-replay", ordinal=2),
            _entry(ordinal=1),
        ),
    )
    assert [entry.ordinal for entry in prepared.entries] == [1, 2]
    assert len(prepared.manifest_hash) == 64
    with pytest.raises((AttributeError, TypeError)):
        prepared.entries[0].canonical()["required"] = False


@pytest.mark.parametrize(
    "change",
    (
        {"handler_id": "UPPER"},
        {"handler_version": ""},
        {"ordinal": -1},
        {"dispatch_class": "unknown"},
        {"handler_id": "anonymous-handler", "required": True},
        {"handler_id": "python-lambda", "required": True},
    ),
)
def test_invalid_handler_identity_version_ordinal_or_class_is_rejected(change) -> None:
    with pytest.raises(ValueError):
        _entry(**change)


def test_duplicate_handler_identity_is_rejected() -> None:
    with pytest.raises(ValueError, match="unique"):
        prepare_manifest(
            runtime_profile_id="paper-trading-v1",
            event_type="agent.execution.order.processed",
            manifest_version="v1",
            entries=(_entry(ordinal=0), _entry(ordinal=1)),
        )


def test_duplicate_handler_ordinal_is_rejected() -> None:
    with pytest.raises(ValueError, match="ordinals"):
        prepare_manifest(
            runtime_profile_id="paper-trading-v1",
            event_type="agent.execution.order.processed",
            manifest_version="v1",
            entries=(_entry(), _entry(handler_id="runtime-replay")),
        )


def test_emission_hashes_all_semantic_fields_and_copies_payload() -> None:
    payload = {"nested": {"items": [1, 2]}, "committed": True}
    first = prepare_emission(
        authority_id="event-delivery",
        authority_version="v1",
        runtime_profile_id="paper-trading-v1",
        manifest_version="v1",
        manifest_hash=HASH_A,
        source_identity="receipt-1",
        consumer_id="execution-agent",
        outcome_id="outcome-1",
        outcome_hash=HASH_A,
        receipt_hash=HASH_B,
        source_sequence=1,
        event_type="agent.execution.order.processed",
        occurred_at=NOW,
        accepted_at=NOW,
        payload=payload,
    )
    payload["nested"]["items"].append(3)
    second = prepare_emission(
        authority_id="event-delivery",
        authority_version="v1",
        runtime_profile_id="paper-trading-v1",
        manifest_version="v1",
        manifest_hash=HASH_A,
        source_identity="receipt-1",
        consumer_id="execution-agent",
        outcome_id="outcome-1",
        outcome_hash=HASH_A,
        receipt_hash=HASH_B,
        source_sequence=1,
        event_type="agent.execution.order.processed",
        occurred_at=NOW,
        accepted_at=NOW,
        payload=payload,
    )
    assert first.emission_effect_id != second.emission_effect_id
    assert first.payload["nested"]["items"] == (1, 2)
    with pytest.raises(TypeError):
        first.payload["extra"] = True


@pytest.mark.parametrize(
    "field,value",
    (
        ("occurred_at", datetime(2026, 8, 27, 9, 0)),
        ("accepted_at", datetime(2026, 8, 27, 9, 0)),
        ("outcome_hash", "not-a-hash"),
        ("receipt_hash", "A" * 64),
        ("source_sequence", -1),
        ("payload", {"bad": float("nan")}),
        ("payload", {"bad": object()}),
    ),
)
def test_emission_rejects_noncanonical_input(field, value) -> None:
    values = {
        "authority_id": "event-delivery",
        "authority_version": "v1",
        "runtime_profile_id": "execution-base-v1",
        "manifest_version": "v1",
        "manifest_hash": HASH_A,
        "source_identity": "receipt-1",
        "consumer_id": "execution-agent",
        "outcome_id": "outcome-1",
        "outcome_hash": HASH_A,
        "receipt_hash": HASH_B,
        "source_sequence": 1,
        "event_type": "agent.execution.order.processed",
        "occurred_at": NOW,
        "accepted_at": NOW,
        "payload": {},
    }
    values[field] = value
    with pytest.raises(ValueError):
        prepare_emission(**values)


def test_synthetic_result_is_deterministic_and_rejects_nonfinite_payload() -> None:
    first = synthetic_result_hash(
        handler_effect_digest=HASH_A,
        status=ApplyStatus.APPLIED_NEW,
        payload={"b": 2, "a": 1},
    )
    second = synthetic_result_hash(
        handler_effect_digest=HASH_A,
        status=ApplyStatus.APPLIED_NEW,
        payload={"a": 1, "b": 2},
    )
    assert first[:2] == second[:2]
    with pytest.raises(ValueError):
        synthetic_result_hash(
            handler_effect_digest=HASH_A,
            status=ApplyStatus.APPLIED_NEW,
            payload={"bad": float("inf")},
        )


def test_emission_api_cannot_receive_handlers_or_manifest() -> None:
    parameters = inspect.signature(EventDeliveryService.accept_emission).parameters
    forbidden = {
        "handlers",
        "handler_ids",
        "required_handler_ids",
        "manifest",
        "manifest_hash",
        "runtime_profile_id",
        "manifest_version",
    }
    assert forbidden.isdisjoint(parameters)
    assert "accepted_at" in parameters
    assert all(parameter.default is inspect.Parameter.empty for name, parameter in parameters.items() if name not in {"self"})


def test_journal_event_hash_rejects_boolean_fencing_generation() -> None:
    with pytest.raises(ValueError, match="fencing_generation"):
        journal_event_hash(
            sequence=1,
            authority_id="event-delivery",
            authority_version="v1",
            event_type=JournalEventType.EMISSION_ACCEPTED,
            emission_effect_id=HASH_A,
            handler_effect_digest=None,
            fencing_generation=True,
            occurred_at=NOW,
            payload_hash=HASH_B,
            previous_hash="0" * 64,
        )
