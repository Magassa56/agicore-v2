"""Integration tests — RiskManager wired with EventBus + replay capture.

Validates Phase 8C success criteria :
- replay-compatible : risk events captured via custom translator into
  EventStore as RISK_VIOLATION records
- deterministic rejection scenarios : identical inputs always block
- thread-safety : concurrent validations don't corrupt the bus / store
- runtime integration : RuntimeEngine + RiskManager + bridge coexist
"""
from __future__ import annotations

import threading
from datetime import datetime, timezone

import pytest

from agicore.core.events import Event
from agicore.l4_planning.runtime import RuntimeEngine
from agicore.replay.event_store import EventStore, ReplayEventType
from agicore.replay.replay_engine import ReplayEngine
from agicore.replay.runtime_event_bridge import RuntimeEventBridge
from agicore.risk.exposure_models import (
    EVT_RISK_BLOCKED,
    EVT_RISK_PASSED,
    ExecutionIntent,
    ExposureSnapshot,
    IntentSide,
    RiskCheckCode,
    RiskLimits,
    SymbolExposure,
    empty_snapshot,
)
from agicore.risk.risk_manager import RiskManager


def _intent(intent_id: str, *, side: IntentSide = IntentSide.BUY,
            quantity: float = 1.0, price: float = 100.0,
            symbol: str = "ES") -> ExecutionIntent:
    return ExecutionIntent(
        intent_id=intent_id, symbol=symbol, side=side,
        quantity=quantity, estimated_price=price,
        timestamp=datetime.now(timezone.utc),
    )


def _build_with_bridge() -> tuple[RuntimeEngine, RiskManager, EventStore, RuntimeEventBridge]:
    rt = RuntimeEngine(poll_interval=0.5)
    rm = RiskManager(
        RiskLimits(max_position_size=10.0, max_exposure_value=1500.0,
                   max_drawdown_pct=0.10, daily_loss_limit=300.0),
        event_bus=rt.event_bus,
    )
    store = EventStore()
    bridge = RuntimeEventBridge(rt.event_bus, store)

    def translate_blocked(event: Event):
        return [(ReplayEventType.RISK_VIOLATION, {
            "intent_id": event.payload.get("intent_id"),
            "symbol": event.payload.get("symbol"),
            "side": event.payload.get("side"),
            "quantity": event.payload.get("quantity"),
            "violation_codes": event.payload.get("violation_codes", []),
        })]

    bridge.register_translator(EVT_RISK_BLOCKED, translate_blocked)
    bridge.attach()
    return rt, rm, store, bridge


# ---------------------------------------------------------------- Bus events
def test_bus_emits_passed_for_valid_intent() -> None:
    rt = RuntimeEngine(poll_interval=0.5)
    captured = []
    rt.subscribe(EVT_RISK_PASSED, lambda ev: captured.append(ev))
    rm = RiskManager(RiskLimits(max_position_size=10.0), event_bus=rt.event_bus)
    try:
        rm.validate(_intent("i-1", quantity=5.0), empty_snapshot())
        assert len(captured) == 1
        assert captured[0].payload["intent_id"] == "i-1"
    finally:
        rt.shutdown()


def test_bus_emits_blocked_for_invalid_intent() -> None:
    rt = RuntimeEngine(poll_interval=0.5)
    captured = []
    rt.subscribe(EVT_RISK_BLOCKED, lambda ev: captured.append(ev))
    rm = RiskManager(RiskLimits(max_position_size=2.0), event_bus=rt.event_bus)
    try:
        rm.validate(_intent("i-2", quantity=5.0), empty_snapshot())
        assert len(captured) == 1
        codes = captured[0].payload["violation_codes"]
        assert RiskCheckCode.POSITION_SIZE_EXCEEDED.value in codes
    finally:
        rt.shutdown()


# ---------------------------------------------------------------- Replay capture
def test_blocked_events_captured_as_risk_violations() -> None:
    rt, rm, store, bridge = _build_with_bridge()
    try:
        # 1 passed (no capture by translator), 2 blocked (captured)
        rm.validate(_intent("ok", quantity=2.0), empty_snapshot())
        rm.validate(_intent("bad-size", quantity=20.0), empty_snapshot())
        rm.validate(_intent("bad-exp", quantity=8.0, price=300.0),
                    empty_snapshot())

        violations = store.get_by_type(ReplayEventType.RISK_VIOLATION)
        assert len(violations) == 2
        ids = {ev.payload["intent_id"] for ev in violations}
        assert ids == {"bad-size", "bad-exp"}
    finally:
        bridge.detach()
        rt.shutdown()


def test_replay_state_unaffected_by_risk_violations() -> None:
    """Risk events are observation-only — replay state must not change."""
    rt, rm, store, bridge = _build_with_bridge()
    try:
        rm.validate(_intent("blk-1", quantity=20.0), empty_snapshot())
        rm.validate(_intent("blk-2", quantity=30.0), empty_snapshot())

        state = ReplayEngine(store).replay()
        # Aucun ordre, aucune position, PnL vide
        assert state.positions == {}
        assert state.realized_pnl_by_symbol == {}
        assert state.events_processed >= 2  # les violations sont bien comptées
        # Et NON marquées comme unknown_event_type dans ignored_events
        assert all(e["reason"] != "unknown_event_type"
                   for e in state.ignored_events)
    finally:
        bridge.detach()
        rt.shutdown()


# ---------------------------------------------------------------- Determinism
def test_deterministic_rejection() -> None:
    rt = RuntimeEngine(poll_interval=0.5)
    rm = RiskManager(
        RiskLimits(max_position_size=3.0, max_exposure_value=500.0,
                   max_drawdown_pct=0.05, daily_loss_limit=100.0),
        event_bus=rt.event_bus,
    )
    snap = ExposureSnapshot(
        positions={"ES": SymbolExposure(symbol="ES", quantity=2.0,
                                         avg_entry_price=100, mark_price=100)},
        realized_pnl_total=-700.0, daily_pnl=-150.0,
        initial_equity=10_000.0, peak_equity=10_000.0,
    )
    intent = _intent("rej", quantity=5.0, price=200.0)

    try:
        results = [rm.validate(intent, snap) for _ in range(5)]
        # All blocked, identical violation codes
        for r in results:
            assert not r.passed
        first_codes = {v.code for v in results[0].violations}
        for r in results[1:]:
            codes = {v.code for v in r.violations}
            assert codes == first_codes
    finally:
        rt.shutdown()


# ---------------------------------------------------------------- Thread safety
def test_concurrent_validations_consistent() -> None:
    rt = RuntimeEngine(poll_interval=0.5)
    captured_passed: list = []
    captured_blocked: list = []
    rt.subscribe(EVT_RISK_PASSED, lambda ev: captured_passed.append(ev))
    rt.subscribe(EVT_RISK_BLOCKED, lambda ev: captured_blocked.append(ev))
    rm = RiskManager(RiskLimits(max_position_size=2.0),
                     event_bus=rt.event_bus)

    N = 50

    try:
        def worker(i: int) -> None:
            qty = 5.0 if i % 2 == 0 else 1.0
            rm.validate(_intent(f"i-{i}", quantity=qty), empty_snapshot())

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(N)]
        for t in threads: t.start()
        for t in threads: t.join()

        # 25 passed (qty=1.0 OK) + 25 blocked (qty=5.0 over limit)
        assert len(captured_passed) == 25
        assert len(captured_blocked) == 25
    finally:
        rt.shutdown()


# ---------------------------------------------------------------- Pipeline gating
def test_pre_execution_gate_pattern() -> None:
    """Demonstrate using RiskManager as a gate before submitting to the
    runtime queue."""
    rt = RuntimeEngine(poll_interval=0.5)
    rm = RiskManager(RiskLimits(max_position_size=3.0),
                     event_bus=rt.event_bus)
    submitted: list[str] = []
    rejected: list[str] = []

    try:
        snap = empty_snapshot()
        for i, qty in enumerate([1.0, 2.0, 5.0, 1.0, 10.0]):
            intent = _intent(f"i-{i}", quantity=qty)
            result = rm.validate(intent, snap)
            if result.passed:
                submitted.append(intent.intent_id)
                # Simulate adding to position to keep snapshot accurate
                cur = snap.positions.get("ES")
                cur_qty = cur.quantity if cur else 0.0
                snap = ExposureSnapshot(
                    positions={"ES": SymbolExposure(
                        symbol="ES", quantity=cur_qty + qty,
                        avg_entry_price=100.0, mark_price=100.0,
                    )},
                    realized_pnl_total=snap.realized_pnl_total,
                    daily_pnl=snap.daily_pnl,
                    initial_equity=snap.initial_equity,
                    peak_equity=snap.peak_equity,
                )
            else:
                rejected.append(intent.intent_id)

        # Premier 2 acceptés (cumul 3), reste rejeté (≥4 vs limite 3)
        assert "i-0" in submitted and "i-1" in submitted
        assert "i-2" in rejected and "i-3" in rejected and "i-4" in rejected
    finally:
        rt.shutdown()
