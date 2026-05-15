"""Unit tests for signal_models DTOs."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from agicore.strategy.signal_models import (
    Action,
    BacktestResult,
    OHLCV,
    Signal,
    StrategyMetrics,
    TradeRecord,
)


def test_action_enum_values() -> None:
    assert Action.BUY.value == "BUY"
    assert Action.SELL.value == "SELL"
    assert Action.HOLD.value == "HOLD"


def test_ohlcv_frozen_and_validated() -> None:
    bar = OHLCV(
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        open=100, high=101, low=99, close=100.5,
    )
    assert bar.close == 100.5
    with pytest.raises(ValidationError):
        OHLCV(
            timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
            open=-1, high=1, low=1, close=1,
        )


def test_signal_construction() -> None:
    sig = Signal(
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        action=Action.BUY,
        price=100.0,
        reason="bullish_cross",
    )
    assert sig.action == Action.BUY


def test_trade_record_fields() -> None:
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    t1 = datetime(2026, 1, 2, tzinfo=timezone.utc)
    tr = TradeRecord(
        entry_time=t0, entry_price=100.0,
        exit_time=t1, exit_price=110.0,
        quantity=10.0, pnl=100.0, pnl_pct=0.1,
    )
    assert tr.pnl == 100.0


def test_strategy_metrics_bounds() -> None:
    StrategyMetrics(
        total_trades=2, wins=1, losses=1,
        win_rate=0.5, total_pnl=10.0, max_drawdown=0.1,
        final_equity=10100.0, initial_equity=10000.0,
    )
    with pytest.raises(ValidationError):
        StrategyMetrics(
            total_trades=2, wins=1, losses=1,
            win_rate=1.5,  # >1 invalide
            total_pnl=0.0, max_drawdown=0.0,
            final_equity=10000.0, initial_equity=10000.0,
        )


def test_backtest_result_assembles() -> None:
    metrics = StrategyMetrics(
        total_trades=0, wins=0, losses=0, win_rate=0.0,
        total_pnl=0.0, max_drawdown=0.0,
        final_equity=10000.0, initial_equity=10000.0,
    )
    result = BacktestResult(
        strategy_name="ema_crossover",
        bars_processed=0,
        signals=[], trades=[], metrics=metrics,
        equity_curve=[10000.0],
    )
    assert result.strategy_name == "ema_crossover"
