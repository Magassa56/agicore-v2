from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime

import pytest

from agicore.agents.execution_agent import (
    AGENT_ID,
    EVT_ORDER_PROCESSED,
    TASK_TYPE_ORDER,
    ExecutionAgent,
)
from agicore.core.event_delivery_contracts import DispatchClass, HandlerManifestEntry
from agicore.core.events import EventBus
from agicore.l2_memory.adapters.sqlalchemy_engine import SqlAlchemyEngine
from agicore.l2_memory.migrations.add_event_delivery_authority import (
    add_event_delivery_authority,
)
from agicore.l2_memory.migrations.init_schema import init_schema
from agicore.l2_memory.schemas.task import TaskRead
from agicore.l2_memory.services.event_delivery_service import EventDeliveryService
from agicore.l2_memory.services.memory_service import MemoryService
from agicore.l5_action.execution_service import L5CanonicalExecutionError
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


def test_canonical_retry_links_ack_to_one_durable_emission(monkeypatch) -> None:
    engine = SqlAlchemyEngine("sqlite:///:memory:", delivery_authority=True)
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
    service = make_execution_service()
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
    payload = market_payload("canonical-retry")
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
    engine.dispose()
