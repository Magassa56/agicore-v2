"""StrategyAgent — bridge between the offline Strategy Sandbox and the Runtime.

A ``TaskHandler`` for ``strategy.backtest`` tasks. Loads a mock OHLCV
dataset, runs the EMA crossover strategy through the BacktestRunner,
persists a summary event in LTM, emits a domain event on the EventBus,
and returns a structured feedback dict.

Fully offline. No broker, no live feed, no external API. The agent uses
only the Phase 7A strategy sandbox and existing Runtime/Memory primitives.

Task payload (all optional)
---------------------------
- ``fast_period``       : int  (default 12)
- ``slow_period``       : int  (default 26)
- ``initial_capital``   : float (default 10_000)
- ``dataset_size``      : int  (default 120)
- ``dataset_pattern``   : str  ("oscillating" | "rising" | "falling" | "constant")
- ``base_price``        : float (default 100)
- ``strategy_name``     : str  (override default name)
"""
from __future__ import annotations

import math
import time
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from typing import Any

import structlog

from agicore.core.events import EventBus
from agicore.l2_memory.schemas.task import TaskRead
from agicore.l2_memory.services.memory_service import MemoryService
from agicore.strategy.backtest_runner import BacktestRunner
from agicore.strategy.ema_strategy import EMACrossoverStrategy
from agicore.strategy.signal_models import OHLCV

logger = structlog.get_logger(__name__)


# Canonical identifiers
TASK_TYPE_BACKTEST: str = "strategy.backtest"
EVT_STRATEGY_BACKTEST_COMPLETED: str = "agent.strategy.backtest.completed"
AGENT_ID: str = "strategy_agent"

# Defaults applied when payload omits a field
DEFAULT_FAST_PERIOD: int = 12
DEFAULT_SLOW_PERIOD: int = 26
DEFAULT_INITIAL_CAPITAL: float = 10_000.0
DEFAULT_DATASET_SIZE: int = 120
DEFAULT_DATASET_PATTERN: str = "oscillating"
DEFAULT_BASE_PRICE: float = 100.0

# Allowed values for ``dataset_pattern``
DATASET_PATTERNS: tuple[str, ...] = (
    "oscillating", "rising", "falling", "constant",
)


# Type alias kept inline (no new abstraction module)
DatasetProvider = Callable[[dict[str, Any]], list[OHLCV]]


def _generate_mock_dataset(
    *,
    n_bars: int,
    pattern: str,
    base_price: float,
) -> list[OHLCV]:
    """Deterministic mock OHLCV. Pure function, no external data."""
    if n_bars < 1:
        raise ValueError("n_bars must be >= 1")
    if pattern not in DATASET_PATTERNS:
        raise ValueError(
            f"unknown dataset_pattern={pattern!r}, allowed: {DATASET_PATTERNS}"
        )
    if base_price <= 0:
        raise ValueError("base_price must be > 0")

    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    bars: list[OHLCV] = []
    for i in range(n_bars):
        if pattern == "oscillating":
            price = base_price + 12.0 * math.sin(i * 0.30)
        elif pattern == "rising":
            price = base_price + 0.5 * i
        elif pattern == "falling":
            price = max(0.01, base_price - 0.5 * i)
        else:  # constant
            price = base_price
        bars.append(
            OHLCV(
                timestamp=t0 + timedelta(minutes=i),
                open=price,
                high=price * 1.001,
                low=price * 0.999,
                close=price,
                volume=1000.0,
            )
        )
    return bars


class StrategyAgent:
    """``TaskHandler`` for ``strategy.backtest`` tasks.

    Parameters
    ----------
    memory : MemoryService
        Required. Used to persist the summary event in LTM.
    event_bus : EventBus | None
        Optional. When provided, also publishes ``EVT_STRATEGY_BACKTEST_COMPLETED``.
    dataset_provider : Callable | None
        Optional override. Receives the task payload, returns ``list[OHLCV]``.
        Default: deterministic mock data from ``_generate_mock_dataset``.
    """

    def __init__(
        self,
        memory: MemoryService,
        event_bus: EventBus | None = None,
        *,
        dataset_provider: DatasetProvider | None = None,
    ) -> None:
        self._memory = memory
        self._bus = event_bus
        self._dataset_provider: DatasetProvider = (
            dataset_provider if dataset_provider is not None
            else self._default_dataset_provider
        )
        self._completed_count = 0

    @property
    def completed_count(self) -> int:
        """Number of backtests this instance has handled."""
        return self._completed_count

    @property
    def agent_id(self) -> str:
        return AGENT_ID

    def __call__(self, task: TaskRead) -> dict[str, Any]:
        """Execute a single ``strategy.backtest`` task."""
        started_at = datetime.now(timezone.utc)
        t0 = time.monotonic()
        payload: dict[str, Any] = dict(task.payload or {})

        fast_period = int(payload.get("fast_period", DEFAULT_FAST_PERIOD))
        slow_period = int(payload.get("slow_period", DEFAULT_SLOW_PERIOD))
        initial_capital = float(
            payload.get("initial_capital", DEFAULT_INITIAL_CAPITAL)
        )
        strategy_name_override = payload.get("strategy_name")

        # 1. Load dataset
        ohlcv = self._dataset_provider(payload)
        if not isinstance(ohlcv, list) or not ohlcv:
            raise ValueError("dataset_provider returned an empty or invalid dataset")

        # 2. Build strategy + runner
        strategy = EMACrossoverStrategy(
            fast_period=fast_period,
            slow_period=slow_period,
            name=strategy_name_override,
        )
        runner = BacktestRunner(initial_capital=initial_capital)

        logger.info(
            "strategy_agent.backtest_starting",
            task_id=task.id,
            strategy_name=strategy.name,
            bars=len(ohlcv),
            initial_capital=initial_capital,
            fast_period=fast_period,
            slow_period=slow_period,
        )

        # 3. Run backtest
        result = runner.run(strategy, ohlcv)

        runtime_duration_ms = max(round((time.monotonic() - t0) * 1000.0, 3), 0.001)

        # 4. Build summary
        summary: dict[str, Any] = {
            "strategy_name": result.strategy_name,
            "total_trades": result.metrics.total_trades,
            "win_rate": result.metrics.win_rate,
            "total_pnl": result.metrics.total_pnl,
            "max_drawdown": result.metrics.max_drawdown,
            "final_equity": result.metrics.final_equity,
            "runtime_duration_ms": runtime_duration_ms,
            # Useful context — not in the contract list but harmless extras
            "initial_equity": result.metrics.initial_equity,
            "wins": result.metrics.wins,
            "losses": result.metrics.losses,
            "bars_processed": result.bars_processed,
        }

        # 5. Persist summary event in LTM
        self._memory.create_event(
            EVT_STRATEGY_BACKTEST_COMPLETED,
            task_id=task.id,
            agent_id=AGENT_ID,
            payload=dict(summary),
        )

        # 6. Emit on event bus
        if self._bus is not None:
            self._bus.emit(
                EVT_STRATEGY_BACKTEST_COMPLETED,
                task_id=task.id,
                strategy_name=summary["strategy_name"],
                total_trades=summary["total_trades"],
                total_pnl=summary["total_pnl"],
                final_equity=summary["final_equity"],
            )

        self._completed_count += 1

        logger.info(
            "strategy_agent.backtest_completed",
            task_id=task.id,
            strategy_name=summary["strategy_name"],
            trades=summary["total_trades"],
            pnl=summary["total_pnl"],
            duration_ms=runtime_duration_ms,
        )

        # 7. Return structured feedback
        return {
            **summary,
            "task_id": task.id,
            "agent_id": AGENT_ID,
            "started_at": started_at.isoformat(),
            "completed_count": self._completed_count,
        }

    # ------------------------------------------------------------------ Default loader
    @staticmethod
    def _default_dataset_provider(payload: dict[str, Any]) -> list[OHLCV]:
        """Generate a deterministic mock dataset based on payload params."""
        n_bars = int(payload.get("dataset_size", DEFAULT_DATASET_SIZE))
        pattern = str(payload.get("dataset_pattern", DEFAULT_DATASET_PATTERN))
        base_price = float(payload.get("base_price", DEFAULT_BASE_PRICE))
        return _generate_mock_dataset(
            n_bars=n_bars, pattern=pattern, base_price=base_price,
        )


__all__ = [
    "StrategyAgent",
    "TASK_TYPE_BACKTEST",
    "EVT_STRATEGY_BACKTEST_COMPLETED",
    "AGENT_ID",
    "DATASET_PATTERNS",
    "DEFAULT_FAST_PERIOD",
    "DEFAULT_SLOW_PERIOD",
    "DEFAULT_INITIAL_CAPITAL",
    "DEFAULT_DATASET_SIZE",
    "DEFAULT_DATASET_PATTERN",
    "DEFAULT_BASE_PRICE",
]
