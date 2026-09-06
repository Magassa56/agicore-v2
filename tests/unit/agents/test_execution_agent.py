from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from agicore.agents.execution_agent import (
    AGENT_ID,
    EVT_ORDER_PROCESSED,
    TASK_TYPE_ORDER,
    ExecutionAgent,
)
from agicore.core.event_delivery_contracts import ApplyStatus, DispatchClass, HandlerManifestEntry
from agicore.core.events import EventBus
from agicore.l2_memory.adapters.sqlalchemy_engine import SqlAlchemyEngine
from agicore.l2_memory.migrations.add_event_delivery_authority import (
    add_event_delivery_authority,
)
from agicore.l2_memory.migrations.init_schema import init_schema
from agicore.l2_memory.schemas.task import TaskRead
from agicore.l2_memory.services.event_delivery_service import EventDeliveryService
from agicore.l2_memory.services.idempotent_memory_delivery_handler import (
    IdempotentMemoryDeliveryHandler,
)
from agicore.l2_memory.services.memory_service import MemoryService
from agicore.l5_action.execution_outbox import L5ExecutionDeliveryError, L5ExecutionDeliveryEvent
from agicore.l5_action.execution_service import L5CanonicalExecutionError
from agicore.l5_action.execution_transaction import replay_l5_execution_delivery_journal
from tests.l5_secure_helpers import make_execution_service, market_payload


@pytest.fixture()
def engine() -> Iterator[SqlAlchemyEngine]:
    engine = SqlAlchemyEngine("sqlite:///:memory:")
    init_schema(engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def memory(engine) -> MemoryService:
    return MemoryService(engine)


def _task(task_id: str, payload: dict[str, object]) -> TaskRead:
    now = datetime.now(UTC)
    return TaskRead(
        id=task_id, task_type=TASK_TYPE_ORDER, status="running",
        assigned_to=None, payload=payload, result=None, error=None,
        created_at=now, updated_at=now,
    )


def test_canonical_constants() -> None:
    assert (TASK_TYPE_ORDER, EVT_ORDER_PROCESSED, AGENT_ID) == (
        "execution.order", "agent.execution.order.processed", "execution_agent"
    )


def test_canonical_conflict_does_not_acknowledge_outcome(memory) -> None:
    class ConflictingDelivery:
        def accept_emission(self, **kwargs):
            return SimpleNamespace(
                status=ApplyStatus.CONFLICT,
                emission_accepted_hash="e" * 64,
            )

    service = make_execution_service(max_position_size=2.0)
    service.price_provider.set_market_price(
        "MNQ", 100.0, observed_at=datetime(2026, 8, 15, 10, 0, tzinfo=UTC)
    )
    bus = EventBus(canonical_delivery=ConflictingDelivery())
    agent = ExecutionAgent(service, memory, bus)
    with pytest.raises(L5CanonicalExecutionError, match="EMISSION_NOT_ACCEPTED"):
        agent(_task("conflicting-emission", market_payload("conflicting-emission", symbol="MNQ")))
    assert len(service.pending_outcomes(AGENT_ID)) == 1
    inbox = service.outcome_inbox(AGENT_ID)
    assert all(
        "event_bus" not in effects
        for effects in inbox.state.effect_event_hashes.values()
    )


def test_market_buy_filled_with_audit_identity(memory) -> None:
    agent = ExecutionAgent(make_execution_service(), memory)
    result = agent(_task("task-one", market_payload("one", quantity=2.0)))
    assert result["order_status"] == "FILLED"
    assert result["position_quantity"] == 2.0
    assert result["authorization_id"] and result["consumption_id"]
    assert result["aggregate_state_hash"] and result["context_state_hash"]


def test_market_sell_without_position_is_controlled_rejection(memory) -> None:
    agent = ExecutionAgent(make_execution_service(), memory)
    result = agent(_task("task-sell", market_payload("sell", side="SELL")))
    assert result["order_status"] == "REJECTED"
    assert result["committed"] is False
    assert "INSUFFICIENT_POSITION" in result["violation_codes"]


def test_limit_placement_is_pending_without_fill(memory) -> None:
    service = make_execution_service()
    payload = market_payload("limit", price=90.0)
    payload.update({"order_type": "LIMIT", "limit_price": 90.0})
    payload.pop("fill_id")
    payload.pop("filled_at")
    result = ExecutionAgent(service, memory)(_task("task-limit", payload))
    assert result["order_status"] == "PENDING"
    assert service.state.fills == {} and service.state.positions == {}


@pytest.mark.parametrize("missing", [
    "intent_id", "estimated_price", "timestamp", "operation_id", "order_id",
    "fill_id", "report_id", "submitted_at", "filled_at",
])
def test_incomplete_payload_is_rejected_before_execution(memory, missing) -> None:
    payload = market_payload(f"missing-{missing}")
    payload.pop(missing)
    with pytest.raises(L5CanonicalExecutionError) as exc:
        ExecutionAgent(make_execution_service(), memory)(_task(f"task-{missing}", payload))
    assert exc.value.code == "INVALID_TASK_PAYLOAD"


def test_naive_timestamp_is_rejected(memory) -> None:
    payload = market_payload("naive")
    payload["timestamp"] = "2026-08-15T10:00:00"
    with pytest.raises(L5CanonicalExecutionError):
        ExecutionAgent(make_execution_service(), memory)(_task("task-naive", payload))


def test_persists_and_emits_committed_result(memory) -> None:
    bus = EventBus()
    received = []
    bus.subscribe(EVT_ORDER_PROCESSED, received.append)
    agent = ExecutionAgent(make_execution_service(), memory, bus)
    result = agent(_task("task-event", market_payload("event")))
    events = memory.get_recent_events(event_type=EVT_ORDER_PROCESSED, limit=5)
    assert len(events) == len(received) == 1
    assert events[0].payload["aggregate_state_hash"] == result["aggregate_state_hash"]


def test_processed_count_increments_only_after_completed_result(memory) -> None:
    agent = ExecutionAgent(make_execution_service(), memory)
    agent(_task("task-a", market_payload("a")))
    agent(_task("task-b", market_payload("b")))
    assert agent.processed_count == 2


def test_execution_without_event_bus_persists_and_has_positive_runtime(memory) -> None:
    agent = ExecutionAgent(make_execution_service(), memory, event_bus=None)
    result = agent(_task("task-no-bus", market_payload("no-bus")))
    assert result["runtime_duration_ms"] > 0
    assert result["order_status"] == "FILLED"
    events = memory.get_recent_events(event_type=EVT_ORDER_PROCESSED, limit=5)
    assert len(events) == 1 and events[0].payload["intent_id"] == "intent-no-bus"


@pytest.mark.parametrize("restart", [False, True])
def test_canonical_retry_links_ack_to_one_durable_emission(monkeypatch, tmp_path, restart) -> None:
    database_url = f"sqlite:///{tmp_path / 'cross-replay.sqlite3'}"
    engine = SqlAlchemyEngine(database_url, delivery_authority=True)
    init_schema(engine)
    add_event_delivery_authority(engine)
    memory = MemoryService(engine)
    delivery = EventDeliveryService(
        engine,
        authority_id="event-delivery",
        authority_version="v1",
        runtime_profile_id="execution-base-v1",
        manifest_version="v1",
    )
    delivery.register_manifest(
        event_type=EVT_ORDER_PROCESSED,
        entries=(
            HandlerManifestEntry(
                handler_id="idempotent-memory-delivery",
                handler_version="v1",
                required=True,
                ordinal=0,
                dispatch_class=DispatchClass.DIRECT,
            ),
        ),
        registered_at=datetime(2026, 8, 15, 10, 0, tzinfo=UTC),
    )
    bus = EventBus(
        canonical_delivery=delivery,
        acceptance_clock=lambda: datetime(2026, 8, 15, 10, 1, tzinfo=UTC),
    )
    service = make_execution_service(max_position_size=2.0)
    service.price_provider.set_market_price(
        "MNQ", 100.0, observed_at=datetime(2026, 8, 15, 10, 0, tzinfo=UTC)
    )
    agent = ExecutionAgent(service, memory, bus)
    original_acknowledge = service.acknowledge_outcome
    calls = 0

    def lose_once(receipt, inbox, *, emission_accepted_hash=None):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise L5CanonicalExecutionError("ACK_LOST", "simulated acknowledgement loss")
        return original_acknowledge(
            receipt,
            inbox,
            emission_accepted_hash=emission_accepted_hash,
        )

    monkeypatch.setattr(service, "acknowledge_outcome", lose_once)
    payload = market_payload("canonical-retry", symbol="MNQ", quantity=1.0)
    with pytest.raises(L5CanonicalExecutionError, match="ACK_LOST"):
        agent(_task("task-canonical-first", payload))

    feedback = agent(_task("task-canonical-retry", payload))
    replay = delivery.replay()

    assert feedback["redelivered"] is True
    assert feedback["emission_accepted_hash"] == replay.anchor.last_hash
    assert len(replay.emissions) == len(replay.deliveries) == 1
    assert replay.deliveries[0].status == "PENDING"
    assert replay.emissions[0].payload["outcome"]["outcome_id"] == replay.emissions[0].outcome_id
    assert replay.emissions[0].payload["outcome"]["outcome_hash"] == replay.emissions[0].outcome_hash
    assert service.pending_outcomes(AGENT_ID) == ()
    if restart:
        engine.dispose()
        engine = SqlAlchemyEngine(database_url, delivery_authority=True)
        delivery = EventDeliveryService(
            engine, authority_id="event-delivery", authority_version="v1",
            runtime_profile_id="execution-base-v1", manifest_version="v1",
        )
        assert delivery.replay(expected_anchor=replay.anchor) == replay
        bus = EventBus(canonical_delivery=delivery)
    store = service._store
    inbox = service.outcome_inbox(AGENT_ID)
    replay_arguments = {
        "execution_events": store.state.execution_journal,
        "inbox_events": inbox.state.journal,
        "expected_inbox_hash": inbox.state.journal[-1].event_hash,
    }
    events = store.delivery_state.journal
    with pytest.raises(L5ExecutionDeliveryError, match="UNVERIFIED_BUS_ACCEPTANCE"):
        replay_l5_execution_delivery_journal(
            events, expected_final_hash=events[-1].event_hash, **replay_arguments
        )
    replayed, _ = replay_l5_execution_delivery_journal(
        events,
        expected_final_hash=events[-1].event_hash,
        bus_authority=delivery,
        expected_bus_anchor=replay.anchor,
        **replay_arguments,
    )
    assert replayed == store.delivery_state
    assert replay.acceptance_hashes[replay.emissions[0].emission_effect_id] == feedback["emission_accepted_hash"]
    with pytest.raises(TypeError):
        replay.acceptance_hashes[replay.emissions[0].emission_effect_id] = "0" * 64

    handler = IdempotentMemoryDeliveryHandler(delivery, MemoryService(engine))
    completed = handler.run_one(
        worker_identity="cross-replay-worker",
        observed_at=datetime(2026, 8, 15, 10, 2, tzinfo=UTC),
    )
    assert completed.status == "COMPLETED"
    completed_bus = delivery.replay()
    assert completed_bus.acceptance_hashes == replay.acceptance_hashes
    assert completed_bus.deliveries[0].status == "COMPLETED"
    completed_replay, _ = replay_l5_execution_delivery_journal(
        events, expected_final_hash=events[-1].event_hash,
        bus_authority=delivery, expected_bus_anchor=completed_bus.anchor,
        **replay_arguments,
    )
    assert completed_replay == replayed
    assert handler.run_one(
        worker_identity="cross-replay-worker",
        observed_at=datetime(2026, 8, 15, 10, 3, tzinfo=UTC),
    ).status == "IDLE"
    assert len(MemoryService(engine).get_recent_events(
        event_type="delivery.memory.applied", limit=10,
    )) == 1

    other_payload = dict(replay.emissions[0].payload)
    other_payload["outcome_id"] = "other-outcome"
    other_payload["source_sequence"] += 1
    other = bus.accept_idempotent(
        source_identity="other-receipt",
        event_type=EVT_ORDER_PROCESSED,
        occurred_at=replay.emissions[0].occurred_at,
        payload=other_payload,
    )
    with pytest.raises(RuntimeError, match="anchor"):
        replay_l5_execution_delivery_journal(
            events, expected_final_hash=events[-1].event_hash,
            bus_authority=delivery, expected_bus_anchor=replay.anchor,
            **replay_arguments,
        )
    for false_hash in ("0" * 64, other.emission_accepted_hash, None):
        forged_ack = inbox.acknowledgement_for(
            inbox.receipts[0], emission_accepted_hash=false_hash,
        )
        last = events[-1]
        forged_event = L5ExecutionDeliveryEvent.create(
            sequence_number=last.sequence_number,
            event_type=last.event_type,
            delivery_version_before=last.delivery_version_before,
            delivery_hash_before=last.delivery_hash_before,
            payload={"acknowledgement": forged_ack.canonical()},
            previous_event_hash=last.previous_event_hash,
        )
        with pytest.raises(L5ExecutionDeliveryError, match="UNVERIFIED_BUS_ACCEPTANCE"):
            replay_l5_execution_delivery_journal(
                (*events[:-1], forged_event),
                expected_final_hash=forged_event.event_hash,
                bus_authority=delivery, expected_bus_anchor=delivery.anchor(),
                **replay_arguments,
            )
    assert store.delivery_state == replayed
    engine.dispose()
