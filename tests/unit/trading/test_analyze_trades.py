"""Unit tests for trade analysis."""
from __future__ import annotations

from datetime import datetime

import pytest

from agicore.trading.analyze_trades import analyze_trades
from agicore.trading.import_nt8_csv import NormalizedTrade


def _trade(day: int, hour: int, pnl: float, *, mae: float | None = None, mfe: float | None = None):
    when = datetime(2026, 5, day, hour, 0)
    return NormalizedTrade(entry_time=when, exit_time=when, pnl=pnl, mae=mae, mfe=mfe)


def test_analyze_trades_computes_expected_statistics() -> None:
    trades = [
        _trade(1, 9, 100.0, mae=-20.0, mfe=140.0),
        _trade(1, 10, -50.0, mae=-80.0, mfe=10.0),
        _trade(2, 10, -25.0),
        _trade(2, 11, 75.0, mae=-15.0, mfe=90.0),
    ]

    stats = analyze_trades(trades)

    assert stats.total_trades == 4
    assert stats.total_pnl == 100.0
    assert stats.pnl_by_day[datetime(2026, 5, 1).date()] == 50.0
    assert stats.pnl_by_day[datetime(2026, 5, 2).date()] == 50.0
    assert stats.pnl_by_hour[10] == -75.0
    assert stats.trades_by_day[datetime(2026, 5, 1).date()] == 2
    assert stats.win_rate == pytest.approx(0.5)
    assert stats.average_trade == pytest.approx(25.0)
    assert stats.largest_loss == -50.0
    assert stats.largest_gain == 100.0
    assert stats.max_consecutive_losses == 2
    assert stats.average_mae == pytest.approx((-20.0 - 80.0 - 15.0) / 3)
    assert stats.average_mfe == pytest.approx((140.0 + 10.0 + 90.0) / 3)


def test_analyze_trades_empty_input_returns_zero_stats() -> None:
    stats = analyze_trades([])

    assert stats.total_trades == 0
    assert stats.total_pnl == 0.0
    assert stats.win_rate == 0.0
    assert stats.average_trade == 0.0
    assert stats.largest_loss == 0.0
    assert stats.largest_gain == 0.0
    assert stats.max_consecutive_losses == 0
    assert stats.average_mae is None
    assert stats.average_mfe is None
