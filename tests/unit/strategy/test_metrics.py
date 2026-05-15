"""Unit tests for the metrics module."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from agicore.strategy.metrics import (
    compute_max_drawdown,
    compute_metrics,
    compute_total_pnl,
    compute_win_rate,
)
from agicore.strategy.signal_models import TradeRecord


def _trade(pnl: float, *, qty: float = 1.0) -> TradeRecord:
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    t1 = datetime(2026, 1, 2, tzinfo=timezone.utc)
    return TradeRecord(
        entry_time=t0, entry_price=100.0,
        exit_time=t1, exit_price=100.0 + pnl,
        quantity=qty,
        pnl=pnl, pnl_pct=pnl / 100.0,
    )


def test_max_drawdown_empty_curve() -> None:
    assert compute_max_drawdown([]) == 0.0


def test_max_drawdown_monotonic_rising() -> None:
    assert compute_max_drawdown([100, 110, 120, 130]) == 0.0


def test_max_drawdown_simple_dip() -> None:
    # Peak 120, dip to 90 → DD = 30/120 = 0.25
    assert compute_max_drawdown([100, 120, 90, 110]) == pytest.approx(0.25)


def test_max_drawdown_zero_peak() -> None:
    """Doit gérer une équité initiale nulle sans diviser par 0."""
    assert compute_max_drawdown([0, 0, 0]) == 0.0


def test_win_rate_empty() -> None:
    assert compute_win_rate([]) == 0.0


def test_win_rate_all_wins() -> None:
    trades = [_trade(10), _trade(20), _trade(5)]
    assert compute_win_rate(trades) == 1.0


def test_win_rate_all_losses() -> None:
    trades = [_trade(-10), _trade(-20)]
    assert compute_win_rate(trades) == 0.0


def test_win_rate_mixed() -> None:
    trades = [_trade(10), _trade(-5), _trade(15), _trade(-20)]
    assert compute_win_rate(trades) == 0.5


def test_total_pnl() -> None:
    trades = [_trade(10), _trade(-3), _trade(7)]
    assert compute_total_pnl(trades) == 14.0


def test_compute_metrics_no_trades() -> None:
    m = compute_metrics([], [10000.0], initial_equity=10000.0)
    assert m.total_trades == 0
    assert m.win_rate == 0.0
    assert m.total_pnl == 0.0
    assert m.max_drawdown == 0.0
    assert m.final_equity == 10000.0


def test_compute_metrics_full() -> None:
    trades = [_trade(50), _trade(-20), _trade(30)]
    curve = [10000, 10050, 10030, 10060]
    m = compute_metrics(trades, curve, initial_equity=10000.0)
    assert m.total_trades == 3
    assert m.wins == 2
    assert m.losses == 1
    assert m.win_rate == pytest.approx(2 / 3)
    assert m.total_pnl == pytest.approx(60.0)
    assert m.final_equity == 10060
    # DD = (10050 - 10030) / 10050
    assert m.max_drawdown == pytest.approx((10050 - 10030) / 10050)


def test_compute_metrics_invalid_initial() -> None:
    with pytest.raises(ValueError):
        compute_metrics([], [], initial_equity=0)
    with pytest.raises(ValueError):
        compute_metrics([], [], initial_equity=-100)
