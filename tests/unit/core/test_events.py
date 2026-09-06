"""Tests for EventBus."""
from __future__ import annotations

from datetime import UTC, datetime
from inspect import signature
from types import SimpleNamespace

import pytest

from agicore.core.event_delivery_contracts import (
    ApplyStatus,
    DispatchClass,
    HandlerManifestEntry,
)
from agicore.core.events import (
    EVT_TASK_COMPLETED,
    EVT_TASK_CREATED,
    WILDCARD,
    Event,
    EventBus,
)
from agicore.l2_memory.adapters.sqlalchemy_engine import SqlAlchemyEngine
from agicore.l2_memory.migrations.add_event_delivery_authority import (
    add_event_delivery_authority,
)
from agicore.l2_memory.services.event_delivery_service import EventDeliveryService

NOW = datetime(2026, 9, 3, 12, 0, tzinfo=UTC)


class _CanonicalDelivery:
    def __init__(self, status: ApplyStatus = ApplyStatus.APPLIED_NEW) -> None:
        self.status = status
        self.calls: list[dict[str, object]] = []

    def accept_emission(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            status=self.status,
            emission=SimpleNamespace(emission_effect_id="a" * 64),
        )


def _canonical_payload() -> dict[str, object]:
    return {
        "consumer_id": "execution-agent",
        "outcome_id": "outcome-1",
        "outcome_hash": "b" * 64,
        "receipt_hash": "c" * 64,
        "source_sequence": 1,
        "business": {"required_handler_ids": ["cannot-substitute-manifest"]},
    }


def test_event_immutable_with_payload_returns_new() -> None:
    e1 = Event(event_type="t.x", payload={"a": 1})
    e2 = e1.with_payload(b=2)
    assert e1.payload == {"a": 1}
    assert e2.payload == {"a": 1, "b": 2}
    assert e1.event_id != e2.event_id


def test_event_bus_publish_calls_subscribers() -> None:
    bus = EventBus()
    received: list[Event] = []
    bus.subscribe(EVT_TASK_CREATED, received.append)

    invoked = bus.emit(EVT_TASK_CREATED, task_id="t-1")

    assert invoked == 1
    assert len(received) == 1
    assert received[0].event_type == EVT_TASK_CREATED
    assert received[0].payload == {"task_id": "t-1"}


def test_event_bus_wildcard_subscriber() -> None:
    bus = EventBus()
    seen: list[str] = []
    bus.subscribe(WILDCARD, lambda ev: seen.append(ev.event_type))

    bus.emit(EVT_TASK_CREATED, task_id="t-1")
    bus.emit(EVT_TASK_COMPLETED, task_id="t-1")

    assert seen == [EVT_TASK_CREATED, EVT_TASK_COMPLETED]


def test_event_bus_unsubscribe() -> None:
    bus = EventBus()
    received: list[Event] = []
    unsub = bus.subscribe(EVT_TASK_CREATED, received.append)

    bus.emit(EVT_TASK_CREATED, task_id="t-1")
    unsub()
    bus.emit(EVT_TASK_CREATED, task_id="t-2")

    assert len(received) == 1


def test_event_bus_handler_failure_is_isolated() -> None:
    bus = EventBus()
    received: list[Event] = []

    def boom(ev: Event) -> None:
        raise RuntimeError("handler bug")

    bus.subscribe(EVT_TASK_CREATED, boom)
    bus.subscribe(EVT_TASK_CREATED, received.append)

    invoked = bus.emit(EVT_TASK_CREATED, task_id="t-1")

    assert invoked == 1  # le handler en échec n'est pas compté
    assert len(received) == 1  # l'autre handler a quand même reçu


def test_event_bus_clear_removes_all() -> None:
    bus = EventBus()
    seen: list[Event] = []
    bus.subscribe(EVT_TASK_CREATED, seen.append)
    bus.clear()
    bus.emit(EVT_TASK_CREATED, task_id="t-1")
    assert seen == []


def test_canonical_api_does_not_accept_handler_or_manifest_selection() -> None:
    parameters = signature(EventBus.accept_idempotent).parameters
    assert tuple(parameters) == (
        "self",
        "source_identity",
        "event_type",
        "occurred_at",
        "payload",
    )


def test_canonical_acceptance_is_durable_before_legacy_propagation() -> None:
    authority = _CanonicalDelivery()
    bus = EventBus(canonical_delivery=authority, acceptance_clock=lambda: NOW)
    observed: list[Event] = []
    bus.subscribe("agent.execution.order.processed", observed.append)

    result = bus.accept_idempotent(
        source_identity="execution-agent",
        event_type="agent.execution.order.processed",
        occurred_at=NOW,
        payload=_canonical_payload(),
    )

    assert result.status == ApplyStatus.APPLIED_NEW
    assert authority.calls[0]["accepted_at"] is NOW
    assert "required_handler_ids" not in authority.calls[0]
    assert len(observed) == 1
    assert observed[0].event_id == "a" * 64


def test_canonical_retry_does_not_repeat_legacy_best_effort_delivery() -> None:
    authority = _CanonicalDelivery(ApplyStatus.ALREADY_APPLIED)
    bus = EventBus(canonical_delivery=authority, acceptance_clock=lambda: NOW)
    observed: list[Event] = []
    bus.subscribe("agent.execution.order.processed", observed.append)

    result = bus.accept_idempotent(
        source_identity="execution-agent",
        event_type="agent.execution.order.processed",
        occurred_at=NOW,
        payload=_canonical_payload(),
    )

    assert result.status == ApplyStatus.ALREADY_APPLIED
    assert observed == []


def test_canonical_path_rejects_missing_authority_or_linkage_before_delivery() -> None:
    with pytest.raises(RuntimeError, match="not configured"):
        EventBus().accept_idempotent(
            source_identity="execution-agent",
            event_type="agent.execution.order.processed",
            occurred_at=NOW,
            payload=_canonical_payload(),
        )
    authority = _CanonicalDelivery()
    with pytest.raises(ValueError, match="linkage fields"):
        EventBus(canonical_delivery=authority).accept_idempotent(
            source_identity="execution-agent",
            event_type="agent.execution.order.processed",
            occurred_at=NOW,
            payload={"outcome_id": "outcome-1"},
        )
    assert authority.calls == []


def test_canonical_bus_uses_registered_manifest_and_retries_one_sql_emission() -> None:
    engine = SqlAlchemyEngine("sqlite:///:memory:", delivery_authority=True)
    add_event_delivery_authority(engine)
    delivery = EventDeliveryService(
        engine,
        authority_id="event-delivery",
        authority_version="v1",
        runtime_profile_id="execution-base-v1",
        manifest_version="v1",
    )
    delivery.register_manifest(
        event_type="agent.execution.order.processed",
        entries=(
            HandlerManifestEntry(
                handler_id="idempotent-memory-delivery",
                handler_version="v1",
                required=True,
                ordinal=0,
                dispatch_class=DispatchClass.DIRECT,
            ),
        ),
        registered_at=NOW,
    )
    bus = EventBus(canonical_delivery=delivery, acceptance_clock=lambda: NOW)
    payload = _canonical_payload()

    first = bus.accept_idempotent(
        source_identity="execution-agent-receipt-1",
        event_type="agent.execution.order.processed",
        occurred_at=NOW,
        payload=payload,
    )
    repeated = bus.accept_idempotent(
        source_identity="execution-agent-receipt-1",
        event_type="agent.execution.order.processed",
        occurred_at=NOW,
        payload=payload,
    )

    assert first.status == ApplyStatus.APPLIED_NEW
    assert repeated.status == ApplyStatus.ALREADY_APPLIED
    assert len(delivery.replay().emissions) == 1
    assert [item.handler_id for item in first.deliveries] == [
        "idempotent-memory-delivery"
    ]
    engine.dispose()
