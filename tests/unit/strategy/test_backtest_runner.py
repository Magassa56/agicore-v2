"""Unit tests for BacktestRunner."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from agicore.strategy.backtest_runner import BacktestRunner
from agicore.strategy.ema_strategy import EMACrossoverStrategy
from agicore.strategy.signal_models import Action, OHLCV, Signal


class _ScriptedStrategy:
    """Strategy that emits a predefined sequence of actions per bar."""
    name = "scripted"

    def __init__(self, actions: list[Action]) -> None:
        self._actions = list(actions)
        self._i = 0

    def on_bar(self, bar: OHLCV) -> Signal:
        action = self._actions[self._i] if self._i < len(self._actions) else Action.HOLD
        self._i += 1
        return Signal(timestamp=bar.timestamp, action=action, price=bar.close)


def _bars(prices: list[float]) -> list[OHLCV]:
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return [
        OHLCV(timestamp=t0.replace(minute=i % 60, hour=(i // 60)),
              open=p, high=p, low=p, close=p, volume=0)
        for i, p in enumerate(prices)
    ]


def test_invalid_initial_capital() -> None:
    with pytest.raises(ValueError):
        BacktestRunner(initial_capital=0)
    with pytest.raises(ValueError):
        BacktestRunner(initial_capital=-1)


def test_no_signals_no_trades(make_bars, constant_series) -> None:
    runner = BacktestRunner(initial_capital=10_000)
    strategy = EMACrossoverStrategy(fast_period=3, slow_period=10)
    result = runner.run(strategy, make_bars(constant_series))
    assert result.trades == []
    assert result.metrics.total_trades == 0
    assert result.metrics.final_equity == pytest.approx(10_000)
    assert result.bars_processed == len(constant_series)


def test_single_round_trip_profit() -> None:
    runner = BacktestRunner(initial_capital=1000.0)
    actions = [Action.HOLD, Action.BUY, Action.HOLD, Action.SELL, Action.HOLD]
    prices = [100.0, 100.0, 105.0, 110.0, 115.0]
    result = runner.run(_ScriptedStrategy(actions), _bars(prices))
    assert len(result.trades) == 1
    trade = result.trades[0]
    assert trade.entry_price == 100.0
    assert trade.exit_price == 110.0
    # 10 units, +10/unit = +100
    assert trade.quantity == pytest.approx(10.0)
    assert trade.pnl == pytest.approx(100.0)
    assert result.metrics.total_pnl == pytest.approx(100.0)
    assert result.metrics.win_rate == 1.0


def test_single_round_trip_loss() -> None:
    runner = BacktestRunner(initial_capital=1000.0)
    actions = [Action.BUY, Action.SELL]
    prices = [100.0, 80.0]
    result = runner.run(_ScriptedStrategy(actions), _bars(prices))
    assert len(result.trades) == 1
    assert result.trades[0].pnl == pytest.approx(-200.0)
    assert result.metrics.win_rate == 0.0


def test_open_position_force_closed_at_last_bar() -> None:
    runner = BacktestRunner(initial_capital=1000.0)
    actions = [Action.BUY, Action.HOLD, Action.HOLD]  # jamais de SELL
    prices = [100.0, 105.0, 110.0]
    result = runner.run(_ScriptedStrategy(actions), _bars(prices))
    assert len(result.trades) == 1
    assert result.trades[0].entry_price == 100.0
    assert result.trades[0].exit_price == 110.0


def test_buy_when_already_long_is_ignored() -> None:
    runner = BacktestRunner(initial_capital=1000.0)
    actions = [Action.BUY, Action.BUY, Action.SELL]
    prices = [100.0, 105.0, 110.0]
    result = runner.run(_ScriptedStrategy(actions), _bars(prices))
    # une seule paire BUY → SELL
    assert len(result.trades) == 1
    assert result.trades[0].entry_price == 100.0
    assert result.trades[0].exit_price == 110.0


def test_sell_without_position_is_noop() -> None:
    runner = BacktestRunner(initial_capital=1000.0)
    actions = [Action.SELL, Action.HOLD]
    prices = [100.0, 100.0]
    result = runner.run(_ScriptedStrategy(actions), _bars(prices))
    assert result.trades == []
    assert result.metrics.final_equity == pytest.approx(1000.0)


def test_equity_curve_length_matches_bars() -> None:
    runner = BacktestRunner(initial_capital=1000.0)
    actions = [Action.HOLD, Action.HOLD, Action.HOLD]
    prices = [100.0, 100.0, 100.0]
    result = runner.run(_ScriptedStrategy(actions), _bars(prices))
    # initial + N bars
    assert len(result.equity_curve) == len(prices) + 1


def test_backtest_result_signals_match_bar_count() -> None:
    runner = BacktestRunner(initial_capital=1000.0)
    actions = [Action.HOLD] * 4
    prices = [100.0, 100.0, 100.0, 100.0]
    result = runner.run(_ScriptedStrategy(actions), _bars(prices))
    assert len(result.signals) == len(prices)
