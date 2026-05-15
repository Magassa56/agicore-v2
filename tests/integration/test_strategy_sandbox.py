"""Integration test — full strategy sandbox pipeline on synthetic data.

Validates that AGIcore can run a complete strategy analysis workflow
end-to-end : EMA crossover → signals → backtest → metrics. Fully offline.
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

from agicore.strategy.backtest_runner import BacktestRunner
from agicore.strategy.ema_strategy import EMACrossoverStrategy
from agicore.strategy.signal_models import Action, OHLCV


def _build_oscillating_dataset(n_bars: int = 120) -> list[OHLCV]:
    """Sine-wave around 100 — guarantees several BUY/SELL cycles."""
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    bars: list[OHLCV] = []
    for i in range(n_bars):
        price = 100.0 + 12.0 * math.sin(i * 0.30)
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


def test_strategy_sandbox_full_pipeline() -> None:
    """End-to-end : strategy + runner + metrics produce a coherent result."""
    bars = _build_oscillating_dataset(120)
    strategy = EMACrossoverStrategy(fast_period=5, slow_period=15)
    runner = BacktestRunner(initial_capital=10_000.0)

    result = runner.run(strategy, bars)

    # Structure ----------------------------------------------------------------
    assert result.strategy_name == strategy.name
    assert result.bars_processed == 120
    assert len(result.signals) == 120
    assert len(result.equity_curve) == 121  # initial + N
    assert result.metrics.initial_equity == 10_000.0

    # Activity -----------------------------------------------------------------
    actions = {s.action for s in result.signals}
    assert Action.BUY in actions
    assert Action.SELL in actions
    assert result.metrics.total_trades >= 2

    # Coherence ----------------------------------------------------------------
    # wins + losses == total_trades
    assert result.metrics.wins + result.metrics.losses == result.metrics.total_trades
    # win_rate = wins / total
    if result.metrics.total_trades > 0:
        assert result.metrics.win_rate == result.metrics.wins / result.metrics.total_trades
    # final_equity = initial + total_pnl (long-only, single position)
    assert abs(
        result.metrics.final_equity - (result.metrics.initial_equity + result.metrics.total_pnl)
    ) < 1e-6
    # max_drawdown is bounded
    assert 0.0 <= result.metrics.max_drawdown <= 1.0
    # equity_curve is consistent with last value
    assert result.equity_curve[-1] == result.metrics.final_equity

    # Trades ordering ----------------------------------------------------------
    for trade in result.trades:
        assert trade.exit_time >= trade.entry_time
        assert trade.quantity > 0
        # pnl_pct should match raw pnl / entry_value
        entry_value = trade.entry_price * trade.quantity
        assert abs(trade.pnl_pct - trade.pnl / entry_value) < 1e-9


def test_strategy_sandbox_flat_market_no_trades() -> None:
    """Flat market → no crosses, no trades, equity unchanged."""
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    bars = [
        OHLCV(
            timestamp=t0 + timedelta(minutes=i),
            open=100.0, high=100.0, low=100.0, close=100.0, volume=1.0,
        )
        for i in range(50)
    ]
    strategy = EMACrossoverStrategy(fast_period=5, slow_period=15)
    runner = BacktestRunner(initial_capital=5_000.0)

    result = runner.run(strategy, bars)

    assert result.metrics.total_trades == 0
    assert result.metrics.total_pnl == 0.0
    assert result.metrics.win_rate == 0.0
    assert result.metrics.max_drawdown == 0.0
    assert result.metrics.final_equity == 5_000.0
