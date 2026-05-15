"""Unit tests for the Phase 8D risk gate in SignalLoopOrchestrator."""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from agicore.core.events import EventBus
from agicore.core.task_queue import TaskQueue
from agicore.l1_perception.market_models import EVT_MARKET_TICK
from agicore.l2_memory.schemas.task import TaskCreate, TaskRead
from agicore.l3_intelligence.signal_loop_orchestrator import (
    EVT_SIGNAL_BLOCKED,
    EVT_SIGNAL_GENERATED,
    SignalLoopOrchestrator,
)
from agicore.risk.exposure_models import (
    ExposureSnapshot,
    RiskLimits,
    SymbolExposure,
    empty_snapshot,
)
from agicore.risk.risk_manager import RiskManager
from agicore.strategy.signal_models import Action, Signal


def _stub_orchestrator() -> MagicMock:
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
    name = "scripted"
    def __init__(self, actions): self._actions = list(actions); self._i = 0
    def on_bar(self, bar):
        action = self._actions[self._i] if self._i < len(self._actions) else Action.HOLD
        self._i += 1
        return Signal(timestamp=bar.timestamp, action=action,
                      price=bar.close, reason="scripted")


def _emit_tick(bus, *, symbol="ES", price=100.0, sequence=0):
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


# ---------------------------------------------------------------- Constructor validation
def test_risk_manager_without_snapshot_provider_raises() -> None:
    with pytest.raises(ValueError):
        SignalLoopOrchestrator(
            EventBus(), TaskQueue(_stub_orchestrator()),
            _ScriptedStrategy([]),
            symbol="ES", order_quantity=1.0,
            risk_manager=RiskManager(RiskLimits()),
        )


def test_snapshot_provider_without_risk_manager_raises() -> None:
    with pytest.raises(ValueError):
        SignalLoopOrchestrator(
            EventBus(), TaskQueue(_stub_orchestrator()),
            _ScriptedStrategy([]),
            symbol="ES", order_quantity=1.0,
            snapshot_provider=lambda: empty_snapshot(),
        )


def test_no_risk_gate_by_default() -> None:
    orch = SignalLoopOrchestrator(
        EventBus(), TaskQueue(_stub_orchestrator()),
        _ScriptedStrategy([]),
        symbol="ES", order_quantity=1.0,
    )
    assert not orch.has_risk_gate
    assert orch.blocked_count == 0


# ---------------------------------------------------------------- Backward compatibility
def test_phase_8b_behavior_preserved_when_no_risk() -> None:
    """Without risk_manager, behavior is identical to Phase 8B."""
    bus = EventBus()
    queue = TaskQueue(_stub_orchestrator())
    orch = SignalLoopOrchestrator(
        bus, queue, _ScriptedStrategy([Action.BUY, Action.HOLD, Action.SELL]),
        symbol="ES", order_quantity=1.0,
    )
    orch.attach()
    _emit_tick(bus, sequence=0)
    _emit_tick(bus, sequence=1)
    _emit_tick(bus, sequence=2)

    assert orch.submitted_count == 2
    assert orch.blocked_count == 0
    assert orch.tick_count == 3


# ---------------------------------------------------------------- Risk gate behavior
def test_risk_gate_blocks_invalid_intent() -> None:
    bus = EventBus()
    queue = TaskQueue(_stub_orchestrator())
    rm = RiskManager(RiskLimits(max_position_size=1.0))  # qty 5 > 1
    orch = SignalLoopOrchestrator(
        bus, queue, _ScriptedStrategy([Action.BUY]),
        symbol="ES", order_quantity=5.0,
        risk_manager=rm, snapshot_provider=lambda: empty_snapshot(),
    )
    orch.attach()
    _emit_tick(bus)

    assert orch.signal_count == 1       # signal generated
    assert orch.blocked_count == 1      # blocked by risk
    assert orch.submitted_count == 0    # NOT submitted
    assert queue.enqueued_count == 0    # queue NEVER touched
    assert "POSITION_SIZE_EXCEEDED" in orch.last_block_codes


def test_risk_gate_allows_valid_intent() -> None:
    bus = EventBus()
    queue = TaskQueue(_stub_orchestrator())
    rm = RiskManager(RiskLimits(max_position_size=10.0))
    orch = SignalLoopOrchestrator(
        bus, queue, _ScriptedStrategy([Action.BUY]),
        symbol="ES", order_quantity=2.0,
        risk_manager=rm, snapshot_provider=lambda: empty_snapshot(),
    )
    orch.attach()
    _emit_tick(bus)

    assert orch.submitted_count == 1
    assert orch.blocked_count == 0


def test_blocked_event_emitted_on_block() -> None:
    bus = EventBus()
    captured = []
    bus.subscribe(EVT_SIGNAL_BLOCKED, lambda ev: captured.append(ev))

    queue = TaskQueue(_stub_orchestrator())
    rm = RiskManager(RiskLimits(max_position_size=1.0))
    orch = SignalLoopOrchestrator(
        bus, queue, _ScriptedStrategy([Action.BUY]),
        symbol="ES", order_quantity=10.0,
        risk_manager=rm, snapshot_provider=lambda: empty_snapshot(),
    )
    orch.attach()
    _emit_tick(bus)

    assert len(captured) == 1
    assert "POSITION_SIZE_EXCEEDED" in captured[0].payload["violation_codes"]
    assert captured[0].payload["symbol"] == "ES"


def test_signal_event_emitted_even_when_blocked() -> None:
    """The orchestrator emits signal first, then evaluates risk."""
    bus = EventBus()
    signals_seen = []
    bus.subscribe(EVT_SIGNAL_GENERATED, lambda ev: signals_seen.append(ev))

    queue = TaskQueue(_stub_orchestrator())
    rm = RiskManager(RiskLimits(max_position_size=1.0))
    orch = SignalLoopOrchestrator(
        bus, queue, _ScriptedStrategy([Action.BUY]),
        symbol="ES", order_quantity=99.0,
        risk_manager=rm, snapshot_provider=lambda: empty_snapshot(),
    )
    orch.attach()
    _emit_tick(bus)

    assert len(signals_seen) == 1


def test_emit_signals_disabled_no_blocked_event() -> None:
    bus = EventBus()
    captured = []
    bus.subscribe(EVT_SIGNAL_BLOCKED, lambda ev: captured.append(ev))

    queue = TaskQueue(_stub_orchestrator())
    rm = RiskManager(RiskLimits(max_position_size=1.0))
    orch = SignalLoopOrchestrator(
        bus, queue, _ScriptedStrategy([Action.BUY]),
        symbol="ES", order_quantity=99.0,
        risk_manager=rm, snapshot_provider=lambda: empty_snapshot(),
        emit_signals=False,
    )
    orch.attach()
    _emit_tick(bus)

    # Signal blocked, but no event because emit_signals=False
    assert captured == []
    assert orch.blocked_count == 1


# ---------------------------------------------------------------- Snapshot provider interaction
def test_snapshot_provider_called_each_signal() -> None:
    calls = {"n": 0}

    def provider():
        calls["n"] += 1
        return empty_snapshot()

    bus = EventBus()
    queue = TaskQueue(_stub_orchestrator())
    rm = RiskManager(RiskLimits())  # no limits → all pass
    orch = SignalLoopOrchestrator(
        bus, queue, _ScriptedStrategy([Action.BUY, Action.HOLD, Action.SELL]),
        symbol="ES", order_quantity=1.0,
        risk_manager=rm, snapshot_provider=provider,
    )
    orch.attach()

    # First emit: BUY → 1 call
    _emit_tick(bus, sequence=0)
    # Second emit: HOLD → 0 calls
    _emit_tick(bus, sequence=1)
    # Third emit: SELL → but no position so blocked → 1 call
    _emit_tick(bus, sequence=2)

    # 2 non-HOLD signals → 2 provider calls
    assert calls["n"] == 2


def test_snapshot_provider_failure_fails_closed() -> None:
    """If the snapshot provider raises, the intent is BLOCKED (fail-closed)."""
    def boom():
        raise RuntimeError("snapshot broken")

    bus = EventBus()
    queue = TaskQueue(_stub_orchestrator())
    rm = RiskManager(RiskLimits())
    orch = SignalLoopOrchestrator(
        bus, queue, _ScriptedStrategy([Action.BUY]),
        symbol="ES", order_quantity=1.0,
        risk_manager=rm, snapshot_provider=boom,
    )
    orch.attach()
    _emit_tick(bus)

    assert orch.submitted_count == 0
    assert orch.blocked_count == 1
    assert "SNAPSHOT_PROVIDER_FAILED" in orch.last_block_codes


def test_risk_manager_failure_fails_closed() -> None:
    """If the RiskManager itself raises, the intent is BLOCKED."""
    rm = MagicMock()
    rm.validate.side_effect = RuntimeError("risk broken")

    bus = EventBus()
    queue = TaskQueue(_stub_orchestrator())
    orch = SignalLoopOrchestrator(
        bus, queue, _ScriptedStrategy([Action.BUY]),
        symbol="ES", order_quantity=1.0,
        risk_manager=rm, snapshot_provider=lambda: empty_snapshot(),
    )
    orch.attach()
    _emit_tick(bus)

    assert orch.submitted_count == 0
    assert orch.blocked_count == 1
    assert "RISK_MANAGER_ERROR" in orch.last_block_codes


# ---------------------------------------------------------------- Mixed scenarios
def test_mixed_pass_and_block_sequence() -> None:
    bus = EventBus()
    queue = TaskQueue(_stub_orchestrator())
    rm = RiskManager(RiskLimits(max_position_size=2.0))

    # Provider tracks "current quantity" — increments with each accepted BUY
    state = {"qty": 0.0}
    def provider():
        positions = {}
        if state["qty"] > 0:
            positions["ES"] = SymbolExposure(
                symbol="ES", quantity=state["qty"],
                avg_entry_price=100.0, mark_price=100.0,
            )
        return ExposureSnapshot(
            positions=positions,
            initial_equity=10_000.0, peak_equity=10_000.0,
        )

    actions = [Action.BUY, Action.BUY, Action.BUY]
    orch = SignalLoopOrchestrator(
        bus, queue, _ScriptedStrategy(actions),
        symbol="ES", order_quantity=1.0,
        risk_manager=rm, snapshot_provider=provider,
    )
    orch.attach()

    for i in range(3):
        _emit_tick(bus, sequence=i)
        # Simulate broker filling the just-submitted order
        if orch.submitted_count > state["qty"]:
            state["qty"] = orch.submitted_count

    # First 2 BUYs accepted (cumul qty 1, 2), 3rd blocked (would be 3 > 2)
    assert orch.submitted_count == 2
    assert orch.blocked_count == 1


# ---------------------------------------------------------------- Integration with bus
def test_underlying_risk_events_fire_on_bus() -> None:
    """RiskManager itself emits its own events when configured with the bus."""
    bus = EventBus()
    risk_passed_seen = []
    risk_blocked_seen = []
    bus.subscribe("risk.check.passed", lambda ev: risk_passed_seen.append(ev))
    bus.subscribe("risk.check.blocked", lambda ev: risk_blocked_seen.append(ev))

    queue = TaskQueue(_stub_orchestrator())
    rm = RiskManager(RiskLimits(max_position_size=1.0), event_bus=bus)
    orch = SignalLoopOrchestrator(
        bus, queue, _ScriptedStrategy([Action.BUY, Action.BUY]),
        symbol="ES", order_quantity=5.0,
        risk_manager=rm, snapshot_provider=lambda: empty_snapshot(),
    )
    orch.attach()
    _emit_tick(bus, sequence=0)
    _emit_tick(bus, sequence=1)

    # Both blocked (qty 5 > limit 1)
    assert len(risk_blocked_seen) == 2
    assert len(risk_passed_seen) == 0
