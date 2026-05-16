"""Pure statistics for normalized trading records."""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date

from .import_nt8_csv import NormalizedTrade


@dataclass(frozen=True)
class TradeStats:
    total_pnl: float
    pnl_by_day: dict[date, float]
    pnl_by_hour: dict[int, float]
    trades_by_day: dict[date, int]
    win_rate: float
    average_trade: float
    largest_loss: float
    largest_gain: float
    max_consecutive_losses: int
    average_mae: float | None
    average_mfe: float | None
    total_trades: int


def analyze_trades(trades: Sequence[NormalizedTrade]) -> TradeStats:
    """Compute aggregate performance statistics from normalized trades."""
    pnl_by_day: defaultdict[date, float] = defaultdict(float)
    pnl_by_hour: defaultdict[int, float] = defaultdict(float)
    trades_by_day: defaultdict[date, int] = defaultdict(int)
    total_pnl = 0.0
    wins = 0
    largest_loss = 0.0
    largest_gain = 0.0
    consecutive_losses = 0
    max_consecutive_losses = 0
    mae_values: list[float] = []
    mfe_values: list[float] = []

    ordered_trades = sorted(trades, key=lambda trade: trade.exit_time)
    for trade in ordered_trades:
        trade_day = trade.exit_time.date()
        trade_hour = trade.exit_time.hour
        total_pnl += trade.pnl
        pnl_by_day[trade_day] += trade.pnl
        pnl_by_hour[trade_hour] += trade.pnl
        trades_by_day[trade_day] += 1

        if trade.pnl > 0:
            wins += 1
            consecutive_losses = 0
        else:
            consecutive_losses += 1
            max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)

        largest_loss = min(largest_loss, trade.pnl)
        largest_gain = max(largest_gain, trade.pnl)

        if trade.mae is not None:
            mae_values.append(trade.mae)
        if trade.mfe is not None:
            mfe_values.append(trade.mfe)

    total_trades = len(ordered_trades)
    return TradeStats(
        total_pnl=total_pnl,
        pnl_by_day=dict(pnl_by_day),
        pnl_by_hour=dict(pnl_by_hour),
        trades_by_day=dict(trades_by_day),
        win_rate=(wins / total_trades) if total_trades else 0.0,
        average_trade=(total_pnl / total_trades) if total_trades else 0.0,
        largest_loss=largest_loss,
        largest_gain=largest_gain,
        max_consecutive_losses=max_consecutive_losses,
        average_mae=_average(mae_values),
        average_mfe=_average(mfe_values),
        total_trades=total_trades,
    )


def _average(values: Sequence[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


__all__ = ["TradeStats", "analyze_trades"]
