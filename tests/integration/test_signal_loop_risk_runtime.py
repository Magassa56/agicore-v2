from __future__ import annotations

import threading
from datetime import datetime, timezone

from agicore.agents.execution_agent import EVT_ORDER_PROCESSED, TASK_TYPE_ORDER, ExecutionAgent
from agicore.core.retry import RetryPolicy
from agicore.l1_perception.market_models import EVT_MARKET_TICK
from agicore.l3_intelligence.signal_loop_orchestrator import EVT_SIGNAL_BLOCKED, SignalLoopOrchestrator
from agicore.l4_planning.runtime import RuntimeEngine
from agicore.strategy.signal_models import Action, Signal
from tests.l5_secure_helpers import make_execution_service


class _BuyStrategy:
    name = "buy-once"

    def __init__(self) -> None:
        self.used = False

    def on_bar(self, bar):
        action = Action.HOLD if self.used else Action.BUY
        self.used = True
        return Signal(timestamp=bar.timestamp, action=action, price=bar.close, reason="test")


def _runtime(*, qty: float, max_position: float):
    runtime = RuntimeEngine(
        retry_policy=RetryPolicy(max_attempts=1, initial_delay=0, jitter=False),
        poll_interval=0.0,
    )
    service = make_execution_service(max_position_size=max_position)
    runtime.register_handler(
        TASK_TYPE_ORDER,
        ExecutionAgent(service, runtime.memory, runtime.event_bus),
    )
    loop = SignalLoopOrchestrator(
        runtime.event_bus, runtime.queue, _BuyStrategy(),
        symbol="ES", order_quantity=qty,
    )
    loop.attach()
    return runtime, service, loop


def _emit(runtime, service, price=100.0):
    stamp = datetime(2026, 8, 15, 10, 0, tzinfo=timezone.utc)
    service.price_provider.set_market_price("ES", price, observed_at=stamp)
    runtime.event_bus.emit(
        EVT_MARKET_TICK, symbol="ES", timestamp=stamp.isoformat(),
        sequence=1, price=price, bid=price, ask=price, volume=1.0,
    )
    runtime.run_once()


def test_blocked_intents_do_not_reach_transaction_store() -> None:
    runtime, service, loop = _runtime(qty=5.0, max_position=1.0)
    try:
        blocked = []
        runtime.event_bus.subscribe(EVT_SIGNAL_BLOCKED, blocked.append)
        _emit(runtime, service)
        assert loop.submitted_count == 1
        assert loop.blocked_count == 1
        assert loop.last_block_codes == ["RISK_MANAGER_BLOCKED", "POSITION_SIZE_EXCEEDED"]
        assert len(blocked) == 1
        assert blocked[0].payload["intent_id"].startswith("sig-intent-")
        assert service.state.orders == {} and service.state.fills == {}
        events = runtime.memory.get_recent_events(event_type=EVT_ORDER_PROCESSED, limit=5)
        assert len(events) == 1 and events[0].payload["order_status"] == "REJECTED"
        assert events[0].payload["consumption_id"] is None
    finally:
        loop.detach()
        runtime.shutdown()


def test_passed_intents_continue_through_single_risk_boundary() -> None:
    runtime, service, loop = _runtime(qty=1.0, max_position=10.0)
    try:
        _emit(runtime, service)
        assert len(service.state.orders) == len(service.state.fills) == 1
        assert len(service.consumptions) == 1
        assert service.state.positions["ES"].quantity == 1.0
    finally:
        loop.detach()
        runtime.shutdown()


def test_signal_loop_has_no_parallel_risk_gate() -> None:
    runtime, service, loop = _runtime(qty=1.0, max_position=10.0)
    try:
        _emit(runtime, service)
        assert loop.blocked_count == 0
        assert len(service.consumptions) == 1
    finally:
        loop.detach()
        runtime.shutdown()


def test_deterministic_pass_block_sequence() -> None:
    outcomes = []
    for _ in range(2):
        runtime, service, loop = _runtime(qty=2.0, max_position=1.0)
        try:
            _emit(runtime, service)
            outcomes.append((loop.submitted_count, len(service.state.orders), len(service.consumptions)))
        finally:
            loop.detach()
            runtime.shutdown()
    assert outcomes == [(1, 0, 0), (1, 0, 0)]


def test_no_threading_explosion_with_canonical_gate() -> None:
    before = {thread.name for thread in threading.enumerate()}
    runtime, service, loop = _runtime(qty=1.0, max_position=10.0)
    try:
        _emit(runtime, service)
        after = {thread.name for thread in threading.enumerate()}
        assert after == before
    finally:
        loop.detach()
        runtime.shutdown()
