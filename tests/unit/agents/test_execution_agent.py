"""Unit tests for ExecutionAgent."""
from __future__ import annotations

from collections.abc import Iterator

import pytest

from agicore.agents.execution_agent import (
    AGENT_ID,
    EVT_ORDER_PROCESSED,
    TASK_TYPE_ORDER,
    ExecutionAgent,
)
from agicore.core.events import EventBus
from agicore.l2_memory.adapters.sqlalchemy_engine import SqlAlchemyEngine
from agicore.l2_memory.migrations.init_schema import init_schema
from agicore.l2_memory.services.memory_service import MemoryService
from agicore.l5_action.broker_mock import MockBroker
from agicore.l5_action.broker_models import InvalidOrderError
from agicore.l5_action.execution_service import ExecutionService


# ---------------------------------------------------------------- Fixtures
@pytest.fixture()
def engine() -> Iterator[SqlAlchemyEngine]:
    eng = SqlAlchemyEngine("sqlite:///:memory:")
    init_schema(eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def memory(engine: SqlAlchemyEngine) -> MemoryService:
    return MemoryService(engine)


@pytest.fixture()
def event_bus() -> EventBus:
    return EventBus()


@pytest.fixture()
def broker() -> MockBroker:
    return MockBroker(initial_prices={"ES": 100.0})


@pytest.fixture()
def execution_service(broker: MockBroker) -> ExecutionService:
    return ExecutionService(broker)


@pytest.fixture()
def make_task():
    from datetime import datetime, timezone
    from agicore.l2_memory.schemas.task import TaskRead

    def _factory(task_id="t-1", payload=None):
        now = datetime.now(timezone.utc)
        return TaskRead(
            id=task_id,
            task_type=TASK_TYPE_ORDER,
            status="running",
            assigned_to=None,
            payload=payload or {},
            result=None, error=None,
            created_at=now, updated_at=now,
        )
    return _factory


# ---------------------------------------------------------------- Constants
def test_canonical_constants() -> None:
    assert TASK_TYPE_ORDER == "execution.order"
    assert EVT_ORDER_PROCESSED == "agent.execution.order.processed"
    assert AGENT_ID == "execution_agent"


# ---------------------------------------------------------------- Required output
def test_returns_required_fields(execution_service, memory, make_task) -> None:
    agent = ExecutionAgent(execution_service, memory)
    task = make_task(payload={"symbol": "ES", "side": "BUY", "quantity": 1.0})

    result = agent(task)

    for required in (
        "order_id", "symbol", "side", "quantity", "order_status",
        "fill_price", "realized_pnl", "runtime_duration_ms",
    ):
        assert required in result, f"missing required field: {required}"

    assert result["task_id"] == "t-1"
    assert result["agent_id"] == AGENT_ID
    assert result["processed_count"] == 1


# ---------------------------------------------------------------- Happy paths
def test_market_buy_filled(execution_service, memory, make_task) -> None:
    agent = ExecutionAgent(execution_service, memory)
    result = agent(make_task(payload={"symbol": "ES", "side": "BUY", "quantity": 2.0}))
    assert result["order_status"] == "FILLED"
    assert result["fill_price"] == 100.0
    assert result["filled_quantity"] == 2.0
    assert result["position_quantity"] == 2.0


def test_market_sell_no_position_rejected(execution_service, memory, make_task) -> None:
    agent = ExecutionAgent(execution_service, memory)
    result = agent(make_task(payload={"symbol": "ES", "side": "SELL", "quantity": 1.0}))
    assert result["order_status"] == "REJECTED"
    assert result["fill_price"] is None
    assert "insufficient" in result["broker_message"].lower()


def test_round_trip_realized_pnl(
    broker, execution_service, memory, make_task
) -> None:
    agent = ExecutionAgent(execution_service, memory)

    # Open position
    agent(make_task(task_id="t-buy", payload={
        "symbol": "ES", "side": "BUY", "quantity": 4.0,
    }))
    # Move price up
    broker.set_market_price("ES", 110.0)
    # Close position
    result = agent(make_task(task_id="t-sell", payload={
        "symbol": "ES", "side": "SELL", "quantity": 4.0,
    }))
    assert result["order_status"] == "FILLED"
    assert result["realized_pnl"] == pytest.approx(40.0)  # (110-100)*4
    assert result["position_quantity"] == 0.0


def test_limit_order_resting(execution_service, memory, make_task) -> None:
    agent = ExecutionAgent(execution_service, memory)
    result = agent(make_task(payload={
        "symbol": "ES", "side": "BUY", "quantity": 1.0,
        "order_type": "LIMIT", "limit_price": 90.0,
    }))
    assert result["order_status"] == "PENDING"
    assert result["fill_price"] is None
    assert result["limit_price"] == 90.0


def test_runtime_duration_positive(execution_service, memory, make_task) -> None:
    agent = ExecutionAgent(execution_service, memory)
    result = agent(make_task(payload={"symbol": "ES", "side": "BUY", "quantity": 1.0}))
    assert result["runtime_duration_ms"] > 0


# ---------------------------------------------------------------- Validation
def test_missing_symbol_raises(execution_service, memory, make_task) -> None:
    agent = ExecutionAgent(execution_service, memory)
    with pytest.raises(InvalidOrderError):
        agent(make_task(payload={"side": "BUY", "quantity": 1.0}))


def test_missing_side_raises(execution_service, memory, make_task) -> None:
    agent = ExecutionAgent(execution_service, memory)
    with pytest.raises(InvalidOrderError):
        agent(make_task(payload={"symbol": "ES", "quantity": 1.0}))


def test_missing_quantity_raises(execution_service, memory, make_task) -> None:
    agent = ExecutionAgent(execution_service, memory)
    with pytest.raises(InvalidOrderError):
        agent(make_task(payload={"symbol": "ES", "side": "BUY"}))


def test_invalid_side_raises(execution_service, memory, make_task) -> None:
    agent = ExecutionAgent(execution_service, memory)
    with pytest.raises(InvalidOrderError):
        agent(make_task(payload={"symbol": "ES", "side": "MAYBE", "quantity": 1.0}))


def test_invalid_order_type_raises(execution_service, memory, make_task) -> None:
    agent = ExecutionAgent(execution_service, memory)
    with pytest.raises(InvalidOrderError):
        agent(make_task(payload={
            "symbol": "ES", "side": "BUY", "quantity": 1.0,
            "order_type": "STOP",
        }))


def test_limit_without_price_raises(execution_service, memory, make_task) -> None:
    agent = ExecutionAgent(execution_service, memory)
    with pytest.raises(InvalidOrderError):
        agent(make_task(payload={
            "symbol": "ES", "side": "BUY", "quantity": 1.0,
            "order_type": "LIMIT",
        }))


def test_market_with_price_raises(execution_service, memory, make_task) -> None:
    agent = ExecutionAgent(execution_service, memory)
    with pytest.raises(InvalidOrderError):
        agent(make_task(payload={
            "symbol": "ES", "side": "BUY", "quantity": 1.0,
            "order_type": "MARKET", "limit_price": 100.0,
        }))


def test_negative_quantity_rejected_at_pydantic(
    execution_service, memory, make_task
) -> None:
    """Negative quantity is rejected by OrderRequest validation."""
    agent = ExecutionAgent(execution_service, memory)
    with pytest.raises(Exception):  # ValidationError ou InvalidOrderError
        agent(make_task(payload={"symbol": "ES", "side": "BUY", "quantity": -1.0}))


# ---------------------------------------------------------------- Persistence + Bus
def test_persists_event_in_memory(
    execution_service, memory, make_task
) -> None:
    agent = ExecutionAgent(execution_service, memory)
    agent(make_task(task_id="t-x", payload={
        "symbol": "ES", "side": "BUY", "quantity": 1.0,
    }))
    events = memory.get_recent_events(event_type=EVT_ORDER_PROCESSED, limit=5)
    assert len(events) == 1
    ev = events[0]
    assert ev.task_id == "t-x"
    assert ev.agent_id == AGENT_ID
    for k in ("symbol", "side", "order_status", "fill_price"):
        assert k in ev.payload


def test_emits_bus_event(
    execution_service, memory, event_bus, make_task
) -> None:
    received = []
    event_bus.subscribe(EVT_ORDER_PROCESSED, lambda ev: received.append(ev))

    agent = ExecutionAgent(execution_service, memory, event_bus)
    agent(make_task(payload={"symbol": "ES", "side": "BUY", "quantity": 1.0}))

    assert len(received) == 1
    assert received[0].payload["order_status"] == "FILLED"


def test_works_without_bus(
    execution_service, memory, make_task
) -> None:
    agent = ExecutionAgent(execution_service, memory, event_bus=None)
    result = agent(make_task(payload={"symbol": "ES", "side": "BUY", "quantity": 1.0}))
    assert result["order_status"] == "FILLED"


# ---------------------------------------------------------------- Misc
def test_processed_count_increments(
    execution_service, memory, make_task
) -> None:
    agent = ExecutionAgent(execution_service, memory)
    assert agent.processed_count == 0
    agent(make_task(task_id="a", payload={"symbol": "ES", "side": "BUY", "quantity": 1.0}))
    agent(make_task(task_id="b", payload={"symbol": "ES", "side": "BUY", "quantity": 1.0}))
    assert agent.processed_count == 2


def test_client_order_id_propagated(
    execution_service, memory, make_task
) -> None:
    agent = ExecutionAgent(execution_service, memory)
    result = agent(make_task(payload={
        "symbol": "ES", "side": "BUY", "quantity": 1.0,
        "client_order_id": "my-coid",
    }))
    assert result["order_id"] == "my-coid"


def test_rejected_status_does_not_raise(
    execution_service, memory, make_task
) -> None:
    """REJECTED is a valid outcome — no exception, returns the report."""
    agent = ExecutionAgent(execution_service, memory)
    result = agent(make_task(payload={"symbol": "ES", "side": "SELL", "quantity": 5.0}))
    assert result["order_status"] == "REJECTED"
