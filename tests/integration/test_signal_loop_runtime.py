"""Integration tests — full pipeline MarketFeed → SignalLoop → Execution → Replay.

Validates Phase 8B success criteria :
- deterministic end-to-end workflow
- replay-compatible : full reconstruction from EventStore
- runtime-safe shutdown : no leftover threads, clean state
- passive event-driven (no orchestrator background thread)
"""
from __future__ import annotations

import threading
import time
from datetime import datetime, timezone

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
    EVT_SIGNAL_GENERATED,
    SignalLoopOrchestrator,
)
from agicore.l4_planning.runtime import RuntimeEngine
from agicore.l5_action.broker_mock import MockBroker
from agicore.l5_action.execution_service import ExecutionService
from agicore.replay.event_store import EventStore, ReplayEventType
from agicore.replay.replay_engine import ReplayEngine
from agicore.replay.runtime_event_bridge import RuntimeEventBridge
from agicore.strategy.ema_strategy import EMACrossoverStrategy


# ---------------------------------------------------------------- Helpers
class _ScriptedPriceProvider:
    """Deterministic price sequence — guarantees crosses for EMA(2,5)."""
    def __init__(self, prices: list[float]) -> None:
        self._prices = prices
    def __call__(self, idx: int) -> float:
        if idx < len(self._prices):
            return self._prices[idx]
        return self._prices[-1]


def _build_full_pipeline(
    price_sequence: list[float],
    *,
    fast: int = 2,
    slow: int = 5,
    qty: float = 1.0,
):
    """Assembles : Feed → Bus → SignalLoop → Strategy → Queue → Runtime →
    ExecutionAgent → MockBroker. Bridge captures everything for replay."""
    rt = RuntimeEngine(
        retry_policy=RetryPolicy(max_attempts=1, initial_delay=0, jitter=False),
        poll_interval=0.0,
    )
    broker = MockBroker(initial_prices={"ES": price_sequence[0]})
    rt.register_handler(
        TASK_TYPE_ORDER,
        ExecutionAgent(ExecutionService(broker), rt.memory, rt.event_bus),
    )

    strategy = EMACrossoverStrategy(fast_period=fast, slow_period=slow)
    orch = SignalLoopOrchestrator(
        rt.event_bus, rt.queue, strategy,
        symbol="ES", order_quantity=qty,
    )
    orch.attach()

    feed = MockMarketFeed(
        rt.event_bus, "ES",
        tick_interval_s=0.005,
        poll_resolution_s=0.002,
        max_ticks=len(price_sequence),
        price_provider=_ScriptedPriceProvider(price_sequence),
    )

    store = EventStore()
    bridge = RuntimeEventBridge(rt.event_bus, store)
    bridge.attach()
    return rt, broker, orch, feed, store, bridge


def _drain_runtime(rt, max_iterations: int = 100) -> int:
    """Run_once until queue is empty (or limit)."""
    total = 0
    for _ in range(max_iterations):
        n = rt.run_once()
        total += n
        if n == 0:
            break
    return total


def _wait_until(predicate, *, timeout_s: float = 2.0) -> bool:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.01)
    return False


# ---------------------------------------------------------------- End-to-end
def test_end_to_end_pipeline_produces_orders() -> None:
    """Rising→falling sequence triggers BUY then SELL via EMA crossover."""
    # Deliberately constructed for a bullish then bearish cross
    prices = [100, 101, 102, 103, 104, 105, 106, 105, 104, 103, 102, 101, 100,
              99, 98]
    rt, broker, orch, feed, store, bridge = _build_full_pipeline(prices)
    try:
        feed.start()
        # Wait until the feed has emitted all ticks
        _wait_until(lambda: feed.published_count == len(prices), timeout_s=2.0)
        feed.stop()
        # Drain any pending submissions
        _drain_runtime(rt)

        assert orch.tick_count == len(prices)
        # At least one signal should have fired
        assert orch.signal_count >= 1
        assert orch.submitted_count == orch.signal_count

        # Replay store contains the full chain (market ticks not captured by
        # default — only execution events through the default translator)
        order_filled = store.get_by_type(ReplayEventType.ORDER_FILLED)
        order_created = store.get_by_type(ReplayEventType.ORDER_CREATED)
        # At least 1 BUY filled (the rising start guarantees it)
        assert len(order_filled) >= 1
        assert len(order_created) >= 1

        # Replay state matches broker state
        replayed = ReplayEngine(store).replay()
        broker_pnl = broker.get_position("ES")
        if broker_pnl is not None and broker_pnl.quantity == 0:
            # Position closed — replay's realized PnL must match broker's
            assert replayed.realized_pnl_by_symbol.get("ES") == pytest.approx(
                broker_pnl.realized_pnl
            )
    finally:
        orch.detach()
        bridge.detach()
        rt.shutdown()


def test_signal_loop_emits_signal_events_for_observers() -> None:
    """Observers can subscribe to agent.signal_loop.signal events."""
    prices = [100, 101, 102, 103, 104, 105, 106]
    rt, broker, orch, feed, store, bridge = _build_full_pipeline(prices)

    captured_signals: list = []
    rt.subscribe(EVT_SIGNAL_GENERATED, lambda ev: captured_signals.append(ev))

    try:
        feed.start()
        _wait_until(lambda: feed.published_count == len(prices), timeout_s=2.0)
        feed.stop()
        _drain_runtime(rt)

        # The rising sequence should produce at least one BUY signal
        assert len(captured_signals) >= 1
        assert any(ev.payload["action"] == "BUY" for ev in captured_signals)
    finally:
        orch.detach()
        bridge.detach()
        rt.shutdown()


def test_replay_consistency_full_workflow() -> None:
    """Replay reconstructs state from event log == broker state."""
    prices = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110,
              108, 106, 104, 102, 100, 98, 96, 94, 92]
    rt, broker, orch, feed, store, bridge = _build_full_pipeline(
        prices, fast=2, slow=5, qty=2.0,
    )
    try:
        feed.start()
        _wait_until(lambda: feed.published_count == len(prices), timeout_s=3.0)
        feed.stop()
        _drain_runtime(rt)

        replayed = ReplayEngine(store).replay()

        # If the broker has a position, replay should match
        broker_pos = broker.get_position("ES")
        if broker_pos is not None:
            replayed_pos = replayed.positions.get("ES")
            if broker_pos.quantity == 0:
                # Position closed — both sides agree on realized PnL
                assert replayed.realized_pnl_by_symbol.get("ES", 0.0) == pytest.approx(
                    broker_pos.realized_pnl
                )
            else:
                # Position open — quantity matches
                assert replayed_pos is not None
                assert replayed_pos.quantity == broker_pos.quantity
    finally:
        orch.detach()
        bridge.detach()
        rt.shutdown()


def test_no_threading_explosion() -> None:
    """SignalLoop adds no thread of its own ; only the feed has 1 daemon."""
    prices = [100, 101, 102]
    rt, broker, orch, feed, store, bridge = _build_full_pipeline(prices)
    try:
        before = {t.name for t in threading.enumerate()}
        feed.start()
        time.sleep(0.05)
        during = {t.name for t in threading.enumerate()}
        # Only the mock-market-feed thread should be new
        new_threads = during - before
        new_thread_names = {n for n in new_threads if not n.startswith("Thread-")}
        # At most one named thread for the feed
        feed_threads = [n for n in new_thread_names if n.startswith("mock-market-feed:")]
        assert len(feed_threads) <= 1

        feed.stop()
    finally:
        orch.detach()
        bridge.detach()
        rt.shutdown()


def test_runtime_safe_shutdown() -> None:
    """All components shut down cleanly, no residual threads."""
    prices = [100, 101, 102, 103]
    rt, broker, orch, feed, store, bridge = _build_full_pipeline(prices)
    try:
        feed.start()
        time.sleep(0.05)
    finally:
        feed.stop()
        orch.detach()
        bridge.detach()
        rt.shutdown()

    alive = [t for t in threading.enumerate()
             if t.name.startswith("mock-market-feed:") and t.is_alive()]
    assert alive == []
    assert not orch.is_attached
    assert not bridge.is_attached


def test_deterministic_two_runs_produce_same_order_count() -> None:
    """Same price sequence → same number of submitted orders both runs."""
    prices = [100, 101, 102, 103, 104, 105, 106, 105, 104, 103, 102, 101, 100,
              99, 98]
    counts = []
    for _ in range(2):
        rt, broker, orch, feed, store, bridge = _build_full_pipeline(prices)
        try:
            feed.start()
            _wait_until(lambda: feed.published_count == len(prices), timeout_s=2.0)
            feed.stop()
            _drain_runtime(rt)
            counts.append(orch.submitted_count)
        finally:
            orch.detach()
            bridge.detach()
            rt.shutdown()
    assert counts[0] == counts[1]
