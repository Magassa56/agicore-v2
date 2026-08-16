"""Unit tests for SignalLoopOrchestrator."""
from __future__ import annotations

import threading
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from agicore.agents.execution_agent import TASK_TYPE_ORDER
from agicore.core.events import Event, EventBus
from agicore.core.task_queue import TaskQueue
from agicore.l1_perception.market_models import EVT_MARKET_TICK
from agicore.l2_memory.schemas.task import TaskCreate, TaskRead
from agicore.l3_intelligence.signal_loop_orchestrator import (
    EVT_SIGNAL_GENERATED,
    ORCHESTRATOR_ID,
    SignalLoopOrchestrator,
)
from agicore.strategy.signal_models import Action, Signal


# ---------------------------------------------------------------- Helpers
def _stub_orchestrator() -> MagicMock:
    """MagicMock orchestrator for a TaskQueue."""
    o = MagicMock()
    def submit(dto: TaskCreate) -> TaskRead:
        now = datetime.now(timezone.utc)
        return TaskRead(
            id=dto.id, task_type=dto.task_type, status="pending",
            assigned_to=dto.assigned_to, payload=dto.payload, result=None,
            error=None, created_at=now, updated_at=now,
        )
    o.submit_task = submit
    return o


class _ScriptedStrategy:
    """Strategy that emits a predefined sequence of actions."""
    name = "scripted"
    def __init__(self, actions: list[Action]) -> None:
        self._actions = list(actions)
        self._i = 0
    def on_bar(self, bar):
        action = self._actions[self._i] if self._i < len(self._actions) else Action.HOLD
        self._i += 1
        return Signal(timestamp=bar.timestamp, action=action,
                      price=bar.close, reason="scripted")


def _emit_tick(bus: EventBus, *, symbol: str = "ES", price: float = 100.0,
               sequence: int = 0) -> None:
    bus.emit(
        EVT_MARKET_TICK,
        symbol=symbol,
        timestamp=datetime.now(timezone.utc).isoformat(),
        sequence=sequence,
        price=price,
        bid=price - 0.05,
        ask=price + 0.05,
        volume=0.0,
    )


def _build(actions: list[Action], symbol: str = "ES") -> tuple[
    SignalLoopOrchestrator, EventBus, TaskQueue, _ScriptedStrategy
]:
    bus = EventBus()
    queue = TaskQueue(_stub_orchestrator())
    strat = _ScriptedStrategy(actions)
    orch = SignalLoopOrchestrator(bus, queue, strat,
                                  symbol=symbol, order_quantity=2.0)
    return orch, bus, queue, strat


# ---------------------------------------------------------------- Validation
class TestValidation:
    def test_invalid_symbol(self) -> None:
        with pytest.raises(ValueError):
            SignalLoopOrchestrator(EventBus(), TaskQueue(_stub_orchestrator()),
                                    _ScriptedStrategy([]), symbol="",
                                    order_quantity=1.0)

    def test_invalid_quantity(self) -> None:
        with pytest.raises(ValueError):
            SignalLoopOrchestrator(EventBus(), TaskQueue(_stub_orchestrator()),
                                    _ScriptedStrategy([]), symbol="ES",
                                    order_quantity=0)
        with pytest.raises(ValueError):
            SignalLoopOrchestrator(EventBus(), TaskQueue(_stub_orchestrator()),
                                    _ScriptedStrategy([]), symbol="ES",
                                    order_quantity=-1.0)


# ---------------------------------------------------------------- Lifecycle
class TestLifecycle:
    def test_initial_state(self) -> None:
        orch, *_ = _build([])
        assert not orch.is_attached
        assert orch.tick_count == 0
        assert orch.signal_count == 0
        assert orch.submitted_count == 0
        assert orch.last_signal_action is None

    def test_attach_detach(self) -> None:
        orch, bus, _, _ = _build([Action.HOLD])
        orch.attach()
        assert orch.is_attached
        _emit_tick(bus)
        assert orch.tick_count == 1
        orch.detach()
        assert not orch.is_attached
        _emit_tick(bus)
        assert orch.tick_count == 1  # plus de capture après detach

    def test_attach_idempotent(self) -> None:
        orch, bus, queue, _ = _build([Action.BUY])
        orch.attach()
        orch.attach()
        _emit_tick(bus)
        # Une seule capture (pas double-subscribed)
        assert orch.submitted_count == 1
        assert queue.enqueued_count == 1

    def test_detach_idempotent(self) -> None:
        orch, *_ = _build([])
        orch.detach()
        orch.detach()  # no error

    def test_context_manager(self) -> None:
        orch, bus, _, _ = _build([Action.HOLD])
        with orch:
            assert orch.is_attached
            _emit_tick(bus)
        assert not orch.is_attached


# ---------------------------------------------------------------- Symbol filter
class TestSymbolFilter:
    def test_other_symbol_ignored(self) -> None:
        orch, bus, _, _ = _build([Action.BUY], symbol="ES")
        orch.attach()
        _emit_tick(bus, symbol="NQ", price=200.0)
        assert orch.tick_count == 0
        assert orch.submitted_count == 0


# ---------------------------------------------------------------- Signal handling
class TestSignalHandling:
    def test_hold_does_not_submit(self) -> None:
        orch, bus, queue, _ = _build([Action.HOLD, Action.HOLD])
        orch.attach()
        _emit_tick(bus)
        _emit_tick(bus, sequence=1)
        assert orch.tick_count == 2
        assert orch.signal_count == 0
        assert orch.submitted_count == 0
        assert queue.enqueued_count == 0

    def test_buy_submits_order_task(self) -> None:
        orch, bus, queue, _ = _build([Action.BUY])
        orch.attach()
        _emit_tick(bus, price=100.0)
        assert orch.submitted_count == 1
        assert queue.enqueued_count == 1

    def test_sell_submits_order_task(self) -> None:
        orch, bus, queue, _ = _build([Action.SELL])
        orch.attach()
        _emit_tick(bus, price=110.0)
        assert orch.submitted_count == 1
        assert queue.enqueued_count == 1

    def test_buy_then_sell_two_submissions(self) -> None:
        orch, bus, queue, _ = _build([Action.BUY, Action.HOLD, Action.SELL])
        orch.attach()
        _emit_tick(bus, price=100.0, sequence=0)
        _emit_tick(bus, price=105.0, sequence=1)
        _emit_tick(bus, price=110.0, sequence=2)
        assert orch.submitted_count == 2
        assert orch.signal_count == 2
        assert orch.tick_count == 3

    def test_last_signal_action_tracked(self) -> None:
        orch, bus, _, _ = _build([Action.BUY, Action.HOLD, Action.SELL])
        orch.attach()
        _emit_tick(bus, sequence=0)
        assert orch.last_signal_action == "BUY"
        _emit_tick(bus, sequence=1)
        assert orch.last_signal_action == "HOLD"
        _emit_tick(bus, sequence=2)
        assert orch.last_signal_action == "SELL"


# ---------------------------------------------------------------- Bus signal emission
class TestBusEmission:
    def test_emits_signal_event_for_buy(self) -> None:
        orch, bus, _, _ = _build([Action.BUY])
        captured = []
        bus.subscribe(EVT_SIGNAL_GENERATED, lambda ev: captured.append(ev))
        orch.attach()
        _emit_tick(bus, price=100.0)
        assert len(captured) == 1
        assert captured[0].payload["action"] == "BUY"
        assert captured[0].payload["price"] == 100.0
        assert captured[0].payload["symbol"] == "ES"

    def test_does_not_emit_for_hold(self) -> None:
        orch, bus, _, _ = _build([Action.HOLD])
        captured = []
        bus.subscribe(EVT_SIGNAL_GENERATED, lambda ev: captured.append(ev))
        orch.attach()
        _emit_tick(bus)
        assert captured == []

    def test_disable_signal_emission(self) -> None:
        bus = EventBus()
        queue = TaskQueue(_stub_orchestrator())
        strat = _ScriptedStrategy([Action.BUY])
        orch = SignalLoopOrchestrator(
            bus, queue, strat, symbol="ES", order_quantity=1.0,
            emit_signals=False,
        )
        captured = []
        bus.subscribe(EVT_SIGNAL_GENERATED, lambda ev: captured.append(ev))
        orch.attach()
        _emit_tick(bus)
        # Pas d'emit signal mais l'order est quand même soumis
        assert captured == []
        assert orch.submitted_count == 1


# ---------------------------------------------------------------- Submitted payload
class TestSubmittedPayload:
    def test_task_payload_correct(self) -> None:
        captured_dto = []
        orch_obj = MagicMock()

        def submit(dto):
            captured_dto.append(dto)
            now = datetime.now(timezone.utc)
            return TaskRead(
                id=dto.id, task_type=dto.task_type, status="pending",
                assigned_to=dto.assigned_to, payload=dto.payload,
                result=None, error=None,
                created_at=now, updated_at=now,
            )
        orch_obj.submit_task = submit

        bus = EventBus()
        queue = TaskQueue(orch_obj)
        strat = _ScriptedStrategy([Action.BUY])
        orch = SignalLoopOrchestrator(bus, queue, strat,
                                       symbol="ES", order_quantity=3.0)
        orch.attach()
        _emit_tick(bus, price=100.0)

        assert len(captured_dto) == 1
        dto = captured_dto[0]
        assert dto.task_type == TASK_TYPE_ORDER
        assert dto.assigned_to == ORCHESTRATOR_ID
        assert dto.payload["symbol"] == "ES"
        assert dto.payload["side"] == "BUY"
        assert dto.payload["quantity"] == 3.0
        assert dto.payload["intent_id"].startswith("sig-intent-")
        assert dto.payload["order_id"].startswith("order-")
        assert dto.payload["operation_id"].startswith("operation-")
        assert dto.payload["estimated_price"] == 100.0
        assert dto.payload["timestamp"] == dto.payload["submitted_at"]


# ---------------------------------------------------------------- Robustness
class TestRobustness:
    def test_malformed_tick_does_not_crash(self) -> None:
        orch, bus, _, _ = _build([Action.BUY])
        orch.attach()
        # Tick sans price
        bus.emit(EVT_MARKET_TICK, symbol="ES",
                 timestamp=datetime.now(timezone.utc).isoformat())
        assert orch.tick_count == 0
        assert orch.submitted_count == 0

    def test_strategy_exception_isolated(self) -> None:
        bus = EventBus()
        queue = TaskQueue(_stub_orchestrator())
        class _BadStrat:
            name = "bad"
            def on_bar(self, bar):
                raise RuntimeError("strat broken")
        orch = SignalLoopOrchestrator(bus, queue, _BadStrat(),
                                       symbol="ES", order_quantity=1.0)
        orch.attach()
        _emit_tick(bus)
        # Pas de crash, pas d'order soumis
        assert orch.submitted_count == 0

    def test_concurrent_ticks_are_processed(self) -> None:
        orch, bus, queue, _ = _build([Action.BUY] * 50)
        orch.attach()

        def emit_loop():
            for i in range(10):
                _emit_tick(bus, sequence=i)

        threads = [threading.Thread(target=emit_loop) for _ in range(5)]
        for t in threads: t.start()
        for t in threads: t.join()

        # 50 ticks émis, 50 BUY → 50 enqueues
        assert orch.tick_count == 50
        assert orch.submitted_count == 50
        assert queue.enqueued_count == 50


# ---------------------------------------------------------------- Constants
def test_canonical_constants() -> None:
    assert ORCHESTRATOR_ID == "signal_loop_orchestrator"
    assert EVT_SIGNAL_GENERATED == "agent.signal_loop.signal"
