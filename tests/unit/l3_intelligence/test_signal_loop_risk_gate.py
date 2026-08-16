from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from agicore.agents.execution_agent import EVT_ORDER_PROCESSED, ExecutionAgent
from agicore.core.events import EventBus
from agicore.core.task_queue import TaskQueue
from agicore.l1_perception.market_models import EVT_MARKET_TICK
from agicore.l2_memory.schemas.task import TaskCreate, TaskRead
from agicore.l3_intelligence.signal_loop_orchestrator import (
    EVT_SIGNAL_BLOCKED,
    EVT_SIGNAL_GENERATED,
    RISK_RESULT_CONTRACT_VERSION,
    SignalLoopOrchestrator,
)
from agicore.risk.exposure_models import RiskLimits
from agicore.risk.risk_manager import RiskManager
from agicore.strategy.signal_models import Action, Signal


def _stub_orchestrator(captured: list[TaskCreate] | None = None) -> MagicMock:
    orchestrator = MagicMock()

    def submit(dto: TaskCreate) -> TaskRead:
        if captured is not None:
            captured.append(dto)
        now = datetime.now(timezone.utc)
        return TaskRead(
            id=dto.id, task_type=dto.task_type, status="pending",
            assigned_to=dto.assigned_to, payload=dto.payload, result=None,
            error=None, created_at=now, updated_at=now,
        )

    orchestrator.submit_task = submit
    return orchestrator


class _Strategy:
    name = "scripted"

    def __init__(self, actions):
        self.actions = iter(actions)

    def on_bar(self, bar):
        return Signal(timestamp=bar.timestamp, action=next(self.actions), price=bar.close, reason="test")


def _emit(bus: EventBus, price: float = 100.0) -> None:
    bus.emit(
        EVT_MARKET_TICK, symbol="ES", timestamp="2026-08-15T10:00:00+00:00",
        sequence=1, price=price, bid=price, ask=price, volume=1.0,
    )


def test_signal_loop_refuses_parallel_risk_manager() -> None:
    with pytest.raises(ValueError, match="canonical ExecutionService"):
        SignalLoopOrchestrator(
            EventBus(), TaskQueue(_stub_orchestrator()), _Strategy([]),
            symbol="ES", order_quantity=1.0,
            risk_manager=RiskManager(RiskLimits()), snapshot_provider=lambda: None,
        )


def test_signal_loop_is_proposal_only() -> None:
    loop = SignalLoopOrchestrator(
        EventBus(), TaskQueue(_stub_orchestrator()), _Strategy([]),
        symbol="ES", order_quantity=1.0,
    )
    assert loop.risk_result_contract_version == RISK_RESULT_CONTRACT_VERSION
    assert loop.blocked_count == 0


def test_non_hold_proposal_contains_complete_explicit_identity() -> None:
    captured: list[TaskCreate] = []
    bus = EventBus()
    loop = SignalLoopOrchestrator(
        bus, TaskQueue(_stub_orchestrator(captured)), _Strategy([Action.BUY]),
        symbol="ES", order_quantity=2.0,
    )
    loop.attach()
    _emit(bus)
    assert loop.submitted_count == 1 and len(captured) == 1
    payload = dict(captured[0].payload)
    required = {
        "intent_id", "symbol", "side", "quantity", "estimated_price", "timestamp",
        "order_type", "operation_id", "order_id", "fill_id", "report_id",
        "submitted_at", "filled_at",
    }
    assert required == set(payload)
    request = ExecutionAgent._build_execution_request(payload)
    assert request.intent.estimated_price == 100.0


def test_same_signal_input_produces_same_task_and_payload() -> None:
    captures = []
    for _ in range(2):
        recorded: list[TaskCreate] = []
        bus = EventBus()
        loop = SignalLoopOrchestrator(
            bus, TaskQueue(_stub_orchestrator(recorded)), _Strategy([Action.BUY]),
            symbol="ES", order_quantity=1.0,
        )
        loop.attach()
        _emit(bus)
        captures.append((recorded[0].id, dict(recorded[0].payload)))
    assert captures[0] == captures[1]


def test_hold_preserves_task_queue() -> None:
    captured = []
    bus = EventBus()
    loop = SignalLoopOrchestrator(
        bus, TaskQueue(_stub_orchestrator(captured)), _Strategy([Action.HOLD]),
        symbol="ES", order_quantity=1.0,
    )
    loop.attach()
    _emit(bus)
    assert captured == [] and loop.signal_count == 0 and loop.submitted_count == 0


def test_signal_event_is_emitted_before_proposal() -> None:
    bus = EventBus()
    events = []
    bus.subscribe(EVT_SIGNAL_GENERATED, events.append)
    loop = SignalLoopOrchestrator(
        bus, TaskQueue(_stub_orchestrator([])), _Strategy([Action.SELL]),
        symbol="ES", order_quantity=1.0,
    )
    loop.attach()
    _emit(bus)
    assert len(events) == 1 and events[0].payload["action"] == "SELL"


def test_payload_validation_precedes_any_future_risk_call() -> None:
    with pytest.raises(Exception):
        ExecutionAgent._build_execution_request({"symbol": "ES", "side": "BUY"})


def test_canonical_rejection_is_correlated_once_and_audited() -> None:
    captured: list[TaskCreate] = []
    blocked_events = []
    bus = EventBus()
    bus.subscribe(EVT_SIGNAL_BLOCKED, blocked_events.append)
    loop = SignalLoopOrchestrator(
        bus, TaskQueue(_stub_orchestrator(captured)), _Strategy([Action.BUY]),
        symbol="ES", order_quantity=1.0,
    )
    loop.attach()
    _emit(bus)
    intent_id = captured[0].payload["intent_id"]
    result = {
        "intent_id": intent_id,
        "committed": False,
        "order_status": "REJECTED",
        "violation_codes": ["EXPOSURE_EXCEEDED"],
        "authorization_id": "risk-auth-test",
        "decision_hash": "a" * 64,
    }
    bus.emit(EVT_ORDER_PROCESSED, **result)
    bus.emit(EVT_ORDER_PROCESSED, **result)
    assert loop.blocked_count == 1
    assert loop.last_block_codes == ["EXPOSURE_EXCEEDED"]
    assert len(blocked_events) == 1
    assert blocked_events[0].payload["intent_id"] == intent_id
    loop.detach()


def test_emit_signals_false_keeps_truthful_block_count_without_event() -> None:
    captured: list[TaskCreate] = []
    events = []
    bus = EventBus()
    bus.subscribe(EVT_SIGNAL_BLOCKED, events.append)
    loop = SignalLoopOrchestrator(
        bus, TaskQueue(_stub_orchestrator(captured)), _Strategy([Action.BUY]),
        symbol="ES", order_quantity=1.0, emit_signals=False,
    )
    loop.attach()
    _emit(bus)
    bus.emit(
        EVT_ORDER_PROCESSED,
        intent_id=captured[0].payload["intent_id"],
        committed=False,
        order_status="REJECTED",
        violation_codes=["POSITION_SIZE_EXCEEDED"],
    )
    assert loop.blocked_count == 1
    assert loop.last_block_codes == ["POSITION_SIZE_EXCEEDED"]
    assert events == []
    loop.detach()


def test_committed_fill_never_emits_signal_blocked() -> None:
    captured: list[TaskCreate] = []
    events = []
    bus = EventBus()
    bus.subscribe(EVT_SIGNAL_BLOCKED, events.append)
    loop = SignalLoopOrchestrator(
        bus, TaskQueue(_stub_orchestrator(captured)), _Strategy([Action.BUY]),
        symbol="ES", order_quantity=1.0,
    )
    loop.attach()
    _emit(bus)
    bus.emit(
        EVT_ORDER_PROCESSED,
        intent_id=captured[0].payload["intent_id"],
        committed=True,
        order_status="FILLED",
        violation_codes=[],
    )
    assert loop.blocked_count == 0 and loop.last_block_codes == [] and events == []
    loop.detach()
