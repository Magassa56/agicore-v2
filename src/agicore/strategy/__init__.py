"""AGIcore-v2 — offline strategy sandbox (Phase 7A).

Self-contained module : EMA crossover strategy, mock-data backtest runner,
basic metrics. Fully offline. No broker, no live feed, no trading
integration. The L5 action layer remains untouched.
"""
from .backtest_runner import BacktestRunner
from .ema_strategy import EMACrossoverStrategy
from .metrics import (
    compute_max_drawdown,
    compute_metrics,
    compute_total_pnl,
    compute_win_rate,
)
from .signal_models import (
    Action,
    BacktestResult,
    OHLCV,
    Signal,
    StrategyMetrics,
    TradeRecord,
)

__all__ = [
    # models
    "Action",
    "OHLCV",
    "Signal",
    "TradeRecord",
    "StrategyMetrics",
    "BacktestResult",
    # strategy
    "EMACrossoverStrategy",
    # backtest
    "BacktestRunner",
    # metrics
    "compute_metrics",
    "compute_max_drawdown",
    "compute_win_rate",
    "compute_total_pnl",
]
