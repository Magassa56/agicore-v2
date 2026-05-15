"""Unit tests for StrategyAgent."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from agicore.agents.strategy_agent import (
    AGENT_ID,
    DATASET_PATTERNS,
    DEFAULT_DATASET_PATTERN,
    DEFAULT_DATASET_SIZE,
    DEFAULT_FAST_PERIOD,
    DEFAULT_INITIAL_CAPITAL,
    DEFAULT_SLOW_PERIOD,
    EVT_STRATEGY_BACKTEST_COMPLETED,
    TASK_TYPE_BACKTEST,
    StrategyAgent,
    _generate_mock_dataset,
)
from agicore.core.events import EventBus
from agicore.l2_memory.services.memory_service import MemoryService
from agicore.strategy.signal_models import OHLCV


# ---------------------------------------------------------------- Constants
def test_canonical_constants() -> None:
    assert TASK_TYPE_BACKTEST == "strategy.backtest"
    assert EVT_STRATEGY_BACKTEST_COMPLETED == "agent.strategy.backtest.completed"
    assert AGENT_ID == "strategy_agent"
    assert "oscillating" in DATASET_PATTERNS
    assert "rising" in DATASET_PATTERNS
    assert "falling" in DATASET_PATTERNS
    assert "constant" in DATASET_PATTERNS
    assert DEFAULT_FAST_PERIOD == 12
    assert DEFAULT_SLOW_PERIOD == 26
    assert DEFAULT_INITIAL_CAPITAL == 10_000.0


# ---------------------------------------------------------------- Mock dataset
def test_mock_dataset_oscillating_default_size() -> None:
    bars = _generate_mock_dataset(
        n_bars=DEFAULT_DATASET_SIZE,
        pattern="oscillating",
        base_price=100.0,
    )
    assert len(bars) == DEFAULT_DATASET_SIZE
    assert all(isinstance(b, OHLCV) for b in bars)
    closes = [b.close for b in bars]
    # oscillating must reach values both above and below the base
    assert max(closes) > 100.0
    assert min(closes) < 100.0


def test_mock_dataset_rising_monotonic() -> None:
    bars = _generate_mock_dataset(n_bars=20, pattern="rising", base_price=100.0)
    closes = [b.close for b in bars]
    assert closes == sorted(closes)
    assert closes[-1] > closes[0]


def test_mock_dataset_falling_strictly_decreasing() -> None:
    bars = _generate_mock_dataset(n_bars=20, pattern="falling", base_price=100.0)
    closes = [b.close for b in bars]
    assert closes == sorted(closes, reverse=True)


def test_mock_dataset_constant() -> None:
    bars = _generate_mock_dataset(n_bars=10, pattern="constant", base_price=42.0)
    assert all(b.close == 42.0 for b in bars)


def test_mock_dataset_invalid_args() -> None:
    with pytest.raises(ValueError):
        _generate_mock_dataset(n_bars=0, pattern="constant", base_price=100.0)
    with pytest.raises(ValueError):
        _generate_mock_dataset(n_bars=10, pattern="weird", base_price=100.0)
    with pytest.raises(ValueError):
        _generate_mock_dataset(n_bars=10, pattern="constant", base_price=0)


# ---------------------------------------------------------------- StrategyAgent
def test_returns_required_fields(memory: MemoryService, make_task) -> None:
    agent = StrategyAgent(memory)
    task = make_task(task_id="t-1", task_type=TASK_TYPE_BACKTEST)
    result = agent(task)

    # Champs requis par la spec Phase 7B
    for required in (
        "strategy_name", "total_trades", "win_rate", "total_pnl",
        "max_drawdown", "final_equity", "runtime_duration_ms",
    ):
        assert required in result, f"missing required field: {required}"

    # Métadonnées d'exécution
    assert result["task_id"] == "t-1"
    assert result["agent_id"] == AGENT_ID
    assert "started_at" in result
    assert result["completed_count"] == 1


def test_runtime_duration_is_positive(
    memory: MemoryService, make_task
) -> None:
    agent = StrategyAgent(memory)
    result = agent(make_task(task_type=TASK_TYPE_BACKTEST))
    assert result["runtime_duration_ms"] > 0


def test_default_oscillating_dataset_produces_trades(
    memory: MemoryService, make_task
) -> None:
    agent = StrategyAgent(memory)
    result = agent(make_task(task_type=TASK_TYPE_BACKTEST))
    # avec sine-wave 120 bars + EMA(12,26), on doit avoir au moins quelques trades
    assert result["total_trades"] >= 1
    assert 0.0 <= result["win_rate"] <= 1.0


def test_constant_dataset_produces_no_trades(
    memory: MemoryService, make_task
) -> None:
    agent = StrategyAgent(memory)
    result = agent(
        make_task(
            task_type=TASK_TYPE_BACKTEST,
            payload={"dataset_pattern": "constant", "dataset_size": 50},
        )
    )
    assert result["total_trades"] == 0
    assert result["total_pnl"] == 0.0
    assert result["max_drawdown"] == 0.0
    assert result["final_equity"] == DEFAULT_INITIAL_CAPITAL


def test_custom_periods_respected(memory: MemoryService, make_task) -> None:
    agent = StrategyAgent(memory)
    result = agent(
        make_task(
            task_type=TASK_TYPE_BACKTEST,
            payload={"fast_period": 3, "slow_period": 10, "dataset_size": 80},
        )
    )
    assert "(3,10)" in result["strategy_name"]


def test_custom_initial_capital(memory: MemoryService, make_task) -> None:
    agent = StrategyAgent(memory)
    result = agent(
        make_task(
            task_type=TASK_TYPE_BACKTEST,
            payload={"initial_capital": 5_000.0, "dataset_pattern": "constant"},
        )
    )
    assert result["initial_equity"] == 5_000.0
    assert result["final_equity"] == 5_000.0


def test_custom_strategy_name(memory: MemoryService, make_task) -> None:
    agent = StrategyAgent(memory)
    result = agent(
        make_task(
            task_type=TASK_TYPE_BACKTEST,
            payload={"strategy_name": "my_custom_strat"},
        )
    )
    assert result["strategy_name"] == "my_custom_strat"


def test_persists_summary_event(memory: MemoryService, make_task) -> None:
    agent = StrategyAgent(memory)
    agent(make_task(task_id="t-x", task_type=TASK_TYPE_BACKTEST))

    events = memory.get_recent_events(
        event_type=EVT_STRATEGY_BACKTEST_COMPLETED, limit=5
    )
    assert len(events) == 1
    ev = events[0]
    assert ev.task_id == "t-x"
    assert ev.agent_id == AGENT_ID
    # Le payload de l'event contient bien les champs clés
    for required in ("total_trades", "total_pnl", "max_drawdown", "final_equity"):
        assert required in ev.payload


def test_emits_bus_event_when_provided(
    memory: MemoryService, event_bus: EventBus, make_task
) -> None:
    received = []
    event_bus.subscribe(EVT_STRATEGY_BACKTEST_COMPLETED, lambda ev: received.append(ev))

    agent = StrategyAgent(memory, event_bus)
    agent(make_task(task_id="t-bus", task_type=TASK_TYPE_BACKTEST))

    assert len(received) == 1
    assert received[0].payload["task_id"] == "t-bus"
    assert "strategy_name" in received[0].payload


def test_works_without_bus(memory: MemoryService, make_task) -> None:
    agent = StrategyAgent(memory, event_bus=None)
    result = agent(make_task(task_type=TASK_TYPE_BACKTEST))
    assert "strategy_name" in result


def test_custom_dataset_provider(
    memory: MemoryService, make_task
) -> None:
    """Le hook dataset_provider permet d'injecter ses propres données."""
    captured = {}

    def my_provider(payload: dict) -> list[OHLCV]:
        captured["payload"] = payload
        t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
        return [
            OHLCV(timestamp=t0, open=100, high=100, low=100, close=100, volume=0)
        ] * 30

    agent = StrategyAgent(memory, dataset_provider=my_provider)
    result = agent(
        make_task(task_type=TASK_TYPE_BACKTEST, payload={"foo": "bar"})
    )
    assert captured["payload"] == {"foo": "bar"}
    assert result["bars_processed"] == 30


def test_dataset_provider_empty_list_raises(
    memory: MemoryService, make_task
) -> None:
    agent = StrategyAgent(memory, dataset_provider=lambda p: [])
    with pytest.raises(ValueError):
        agent(make_task(task_type=TASK_TYPE_BACKTEST))


def test_invalid_dataset_pattern_propagates(
    memory: MemoryService, make_task
) -> None:
    agent = StrategyAgent(memory)
    with pytest.raises(ValueError):
        agent(
            make_task(
                task_type=TASK_TYPE_BACKTEST,
                payload={"dataset_pattern": "absurd"},
            )
        )


def test_completed_count_increments(memory: MemoryService, make_task) -> None:
    agent = StrategyAgent(memory)
    assert agent.completed_count == 0
    agent(make_task(task_id="a", task_type=TASK_TYPE_BACKTEST,
                    payload={"dataset_pattern": "constant"}))
    agent(make_task(task_id="b", task_type=TASK_TYPE_BACKTEST,
                    payload={"dataset_pattern": "constant"}))
    assert agent.completed_count == 2


def test_metric_consistency(memory: MemoryService, make_task) -> None:
    """final_equity = initial + total_pnl ; wins+losses = total_trades."""
    agent = StrategyAgent(memory)
    result = agent(make_task(task_type=TASK_TYPE_BACKTEST))
    assert result["wins"] + result["losses"] == result["total_trades"]
    assert abs(
        result["final_equity"] - (result["initial_equity"] + result["total_pnl"])
    ) < 1e-6
