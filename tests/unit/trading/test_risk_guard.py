"""Unit tests for risk guard rules."""
from __future__ import annotations

from datetime import datetime

from agicore.trading.analyze_trades import analyze_trades
from agicore.trading.import_nt8_csv import NormalizedTrade
from agicore.trading.risk_guard import RiskGuardConfig, evaluate_risk


def _trade(day: int, hour: int, pnl: float) -> NormalizedTrade:
    when = datetime(2026, 5, day, hour, 0)
    return NormalizedTrade(entry_time=when, exit_time=when, pnl=pnl)


def test_evaluate_risk_detects_destructive_patterns() -> None:
    trades = [
        _trade(1, 9, -200.0),
        _trade(1, 10, -250.0),
        _trade(1, 10, -100.0),
        _trade(1, 11, 50.0),
        _trade(2, 9, 10.0),
        _trade(2, 9, 10.0),
        _trade(2, 9, 10.0),
        _trade(2, 9, 10.0),
    ]
    stats = analyze_trades(trades)

    result = evaluate_risk(
        stats,
        RiskGuardConfig(
            destructive_day_loss=-500.0,
            daily_loss_limit=-300.0,
            max_trades_per_day=3,
            dangerous_hour_loss=-200.0,
            max_consecutive_losses=3,
        ),
    )

    kinds = {alert.kind for alert in result.alerts}
    assert "destructive_day" in kinds
    assert "daily_loss" in kinds
    assert "overtrading" in kinds
    assert "dangerous_hour" in kinds
    assert "loss_streak" in kinds
    assert "2026-05-01" in result.worst_days
    assert 10 in result.worst_hours
    assert "Stop trading after 300.00 daily loss" in result.apex_rules
    assert "Stop trading after 3 consecutive losses" in result.apex_rules
    assert "Max 3 trades per day" in result.apex_rules
    assert "Avoid worst trading hours: 10:00" in result.apex_rules
