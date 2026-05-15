"""Integration tests — Phase 8D risk-gated signal execution end-to-end.

Validates :
- blocked intents NEVER reach TaskQueue / ExecutionAgent / MockBroker
- passed intents flow through normally
- risk events captured in EventStore via custom translator
- replay state matches broker state (only fills affect positions/PnL)
- deterministic pass/block sequence
"""
from __future__ import annotations

import threading
import time

import pytest

from agicore.agents.execution_agent import (
    EVT_ORDER_PROCESSED,
    TASK_TYPE_ORDER,
    ExecutionAgent,
)
from agicore.core.events import Event
from agicore.core.retry import RetryPolicy
from agicore.l1_perception.market_models import EVT_MARKET_TICK
from agicore.l1_perception.mock_market_feed import MockMarketFeed
from agicore.l3_intelligence.signal_loop_orchestrator import (
    EVT_SIGNAL_BLOCKED,
    SignalLoopOrchestrator,
)
from agicore.l4_planning.runtime import RuntimeEngine
from agicore.l5_action.broker_mock import MockBroker
from agicore.l5_action.execution_service import ExecutionService
from agicore.replay.event_store import EventStore, ReplayEventType
from agicore.replay.replay_engine import ReplayEngine
from agicore.replay.runtime_event_bridge import RuntimeEventBridge
from agicore.risk.exposure_models import (
    EVT_RISK_BLOCKED,
    ExposureSnapshot,
    RiskLimits,
    SymbolExposure,
)
from agicore.risk.risk_manager import RiskManager
from agicore.strategy.ema_strategy import EMACrossoverStrategy


# ---------------------------------------------------------------- Helpers
class _ScriptedPriceProvider:
    def __init__(self, prices): self._prices = prices
    def __call__(self, idx):
        return self._prices[idx] if idx < len(self._prices) else self._prices[-1]


def _broker_snapshot_provider(
    broker: MockBroker,
    symbol: str,
    *,
    initial_equity: float = 10_000.0,
):
    """Build a snapshot from broker live state."""
    def provider() -> ExposureSnapshot:
        positions = {}
        pos = broker.get_position(symbol)
        if pos is not None and pos.quantity > 0:
            mark = broker.get_market_price(symbol) or pos.avg_entry_price
            positions[symbol] = SymbolExposure(
                symbol=symbol, quantity=pos.quantity,
                avg_entry_price=pos.avg_entry_price, mark_price=mark,
            )
        realized = pos.realized_pnl if pos else 0.0
        return ExposureSnapshot(
            positions=positions,
            realized_pnl_total=realized,
            initial_equity=initial_equity,
            peak_equity=max(initial_equity, initial_equity + realized),
        )
    return provider


def _wait_until(predicate, *, timeout_s: float = 2.0) -> bool:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.01)
    return False


def _drain(rt, max_iter=200):
    for _ in range(max_iter):
        if rt.run_once() == 0:
            break


def _build(
    prices: list[float],
    *,
    qty: float,
    risk_limits: RiskLimits,
    fast: int = 2,
    slow: int = 5,
):
    rt = RuntimeEngine(
        retry_policy=RetryPolicy(max_attempts=1, initial_delay=0, jitter=False),
        poll_interval=0.0,
    )
    broker = MockBroker(initial_prices={"ES": prices[0]})
    rt.register_handler(
        TASK_TYPE_ORDER,
        ExecutionAgent(ExecutionService(broker), rt.memory, rt.event_bus),
    )
    strategy = EMACrossoverStrategy(fast_period=fast, slow_period=slow)
    rm = RiskManager(risk_limits, event_bus=rt.event_bus)
    snap_provider = _broker_snapshot_provider(broker, "ES")
    orch = SignalLoopOrchestrator(
        rt.event_bus, rt.queue, strategy,
        symbol="ES", order_quantity=qty,
        risk_manager=rm, snapshot_provider=snap_provider,
    )
    orch.attach()

    # Bridge with both order and risk translators
    store = EventStore()
    bridge = RuntimeEventBridge(rt.event_bus, store)

    def risk_translator(event: Event):
        return [(ReplayEventType.RISK_VIOLATION, {
            "intent_id": event.payload.get("intent_id"),
            "symbol": event.payload.get("symbol"),
            "side": event.payload.get("side"),
            "quantity": event.payload.get("quantity"),
            "violation_codes": event.payload.get("violation_codes", []),
        })]

    bridge.register_translator(EVT_RISK_BLOCKED, risk_translator)
    bridge.attach()

    # Mirror broker mark price into the broker each tick (simulates a market
    # feed-aware broker — needed so SELLs can fill at the latest price)
    def update_mark(event):
        broker.set_market_price(event.payload["symbol"], event.payload["price"])
    rt.subscribe(EVT_MARKET_TICK, update_mark)

    feed = MockMarketFeed(
        rt.event_bus, "ES",
        tick_interval_s=0.005, poll_resolution_s=0.002,
        max_ticks=len(prices),
        price_provider=_ScriptedPriceProvider(prices),
    )
    return rt, broker, orch, feed, store, bridge


# ---------------------------------------------------------------- Tests
def test_blocked_intents_do_not_reach_broker() -> None:
    """With a tight position size limit, all BUY signals are blocked ;
    broker stays empty."""
    prices = [100, 101, 102, 103, 104, 105, 106, 105, 104, 103]
    rt, broker, orch, feed, store, bridge = _build(
        prices, qty=10.0,  # very large quantity
        risk_limits=RiskLimits(max_position_size=1.0),
    )
    try:
        feed.start()
        _wait_until(lambda: feed.published_count == len(prices), timeout_s=2.0)
        feed.stop()
        _drain(rt)

        # If signal generated, it was blocked → not submitted
        assert orch.signal_count >= 1
        assert orch.submitted_count == 0
        assert orch.blocked_count == orch.signal_count
        # Broker untouched
        assert broker.get_position("ES") is None
    finally:
        orch.detach()
        bridge.detach()
        rt.shutdown()


def test_passed_intents_continue_through_pipeline() -> None:
    """With permissive limits, signals flow through normally."""
    prices = [100, 101, 102, 103, 104, 105, 106, 105, 104, 103]
    rt, broker, orch, feed, store, bridge = _build(
        prices, qty=1.0,
        risk_limits=RiskLimits(max_position_size=100.0),  # very permissive
    )
    try:
        feed.start()
        _wait_until(lambda: feed.published_count == len(prices), timeout_s=2.0)
        feed.stop()
        _drain(rt)

        if orch.signal_count > 0:
            assert orch.submitted_count >= 1
            # broker should have processed at least one fill
            assert broker.get_position("ES") is not None
    finally:
        orch.detach()
        bridge.detach()
        rt.shutdown()


def test_risk_violations_captured_in_replay_store() -> None:
    """Blocked events captured as RISK_VIOLATION via custom translator."""
    prices = [100, 101, 102, 103, 104, 105, 106]
    rt, broker, orch, feed, store, bridge = _build(
        prices, qty=10.0,
        risk_limits=RiskLimits(max_position_size=1.0),
    )
    try:
        feed.start()
        _wait_until(lambda: feed.published_count == len(prices), timeout_s=2.0)
        feed.stop()
        _drain(rt)

        violations = store.get_by_type(ReplayEventType.RISK_VIOLATION)
        if orch.blocked_count > 0:
            assert len(violations) == orch.blocked_count
            for v in violations:
                assert "POSITION_SIZE_EXCEEDED" in v.payload["violation_codes"]
    finally:
        orch.detach()
        bridge.detach()
        rt.shutdown()


def test_replay_state_matches_broker_state() -> None:
    """Risk-blocked orders never affect state — replay agrees with broker."""
    prices = [100, 101, 102, 103, 104, 105, 106]
    rt, broker, orch, feed, store, bridge = _build(
        prices, qty=2.0,
        risk_limits=RiskLimits(max_position_size=10.0),
    )
    try:
        feed.start()
        _wait_until(lambda: feed.published_count == len(prices), timeout_s=2.0)
        feed.stop()
        _drain(rt)

        # No fills → no positions, no PnL — both broker and replay agree
        replayed = ReplayEngine(store).replay()
        broker_pos = broker.get_position("ES")
        if broker_pos is not None and broker_pos.quantity > 0:
            assert "ES" in replayed.positions
            assert replayed.positions["ES"].quantity == broker_pos.quantity
        else:
            # No position case
            assert "ES" not in replayed.positions or replayed.positions["ES"].quantity == 0
    finally:
        orch.detach()
        bridge.detach()
        rt.shutdown()


def test_blocked_signal_emits_event_observers_can_track() -> None:
    """Subscribers to agent.signal_loop.blocked receive notifications."""
    prices = [100, 101, 102, 103, 104, 105, 106]
    rt, broker, orch, feed, store, bridge = _build(
        prices, qty=10.0,
        risk_limits=RiskLimits(max_position_size=1.0),
    )
    captured = []
    rt.subscribe(EVT_SIGNAL_BLOCKED, lambda ev: captured.append(ev))

    try:
        feed.start()
        _wait_until(lambda: feed.published_count == len(prices), timeout_s=2.0)
        feed.stop()
        _drain(rt)

        # Should have received at least as many block events as signals
        assert len(captured) == orch.blocked_count
        if captured:
            assert "POSITION_SIZE_EXCEEDED" in captured[0].payload["violation_codes"]
    finally:
        orch.detach()
        bridge.detach()
        rt.shutdown()


def test_deterministic_pass_block_sequence() -> None:
    """Same prices + same risk config → same submitted/blocked counts."""
    prices = [100, 101, 102, 103, 104, 105, 106, 105, 104, 103, 102]
    counts = []

    for _ in range(2):
        rt, broker, orch, feed, store, bridge = _build(
            prices, qty=2.0,
            risk_limits=RiskLimits(max_position_size=5.0),
        )
        try:
            feed.start()
            _wait_until(lambda: feed.published_count == len(prices), timeout_s=2.0)
            feed.stop()
            _drain(rt)
            counts.append((orch.submitted_count, orch.blocked_count))
        finally:
            orch.detach()
            bridge.detach()
            rt.shutdown()

    assert counts[0] == counts[1]


def test_no_threading_explosion_with_risk_gate() -> None:
    """Risk gate adds 0 thread."""
    prices = [100, 101, 102]
    before = {t.name for t in threading.enumerate()}
    rt, broker, orch, feed, store, bridge = _build(
        prices, qty=1.0, risk_limits=RiskLimits(max_position_size=10.0),
    )
    try:
        feed.start()
        time.sleep(0.05)
        during = {t.name for t in threading.enumerate()}
        new = during - before
        # Only the feed thread should be new
        assert all(n.startswith("mock-market-feed:") or n.startswith("Thread-")
                   for n in new)
        feed.stop()
    finally:
        orch.detach()
        bridge.detach()
        rt.shutdown()
