"""Strategy sandbox — minimal performance metrics.

All functions are pure : input → output, no I/O. The backtest runner
calls ``compute_metrics`` once at the end of a run.
"""
from __future__ import annotations

from collections.abc import Sequence

from .signal_models import StrategyMetrics, TradeRecord


def compute_max_drawdown(equity_curve: Sequence[float]) -> float:
    """Maximum drawdown over an equity curve. Returns a fraction in [0, 1].

    Drawdown at point i = (peak_so_far - equity_i) / peak_so_far.
    """
    if not equity_curve:
        return 0.0
    peak = equity_curve[0]
    max_dd = 0.0
    for value in equity_curve:
        if value > peak:
            peak = value
        if peak > 0:
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd
    return max_dd


def compute_win_rate(trades: Sequence[TradeRecord]) -> float:
    """Fraction of trades with strictly positive PnL. Zero when no trades."""
    if not trades:
        return 0.0
    wins = sum(1 for t in trades if t.pnl > 0)
    return wins / len(trades)


def compute_total_pnl(trades: Sequence[TradeRecord]) -> float:
    return sum(t.pnl for t in trades)


def compute_metrics(
    trades: Sequence[TradeRecord],
    equity_curve: Sequence[float],
    *,
    initial_equity: float,
) -> StrategyMetrics:
    """Aggregate metrics for a backtest run."""
    if initial_equity <= 0:
        raise ValueError("initial_equity must be > 0")
    total = len(trades)
    wins = sum(1 for t in trades if t.pnl > 0)
    losses = sum(1 for t in trades if t.pnl <= 0)
    return StrategyMetrics(
        total_trades=total,
        wins=wins,
        losses=losses,
        win_rate=(wins / total) if total > 0 else 0.0,
        total_pnl=compute_total_pnl(trades),
        max_drawdown=compute_max_drawdown(equity_curve),
        final_equity=equity_curve[-1] if equity_curve else initial_equity,
        initial_equity=initial_equity,
    )


__all__ = [
    "compute_metrics",
    "compute_max_drawdown",
    "compute_win_rate",
    "compute_total_pnl",
]
