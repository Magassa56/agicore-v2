"""Unit tests for Markdown report generation."""
from __future__ import annotations

from datetime import datetime

from agicore.trading.analyze_trades import analyze_trades
from agicore.trading.import_nt8_csv import NormalizedTrade
from agicore.trading.report import generate_markdown_report
from agicore.trading.risk_guard import RiskGuardConfig, evaluate_risk


def _trade(day: int, hour: int, pnl: float) -> NormalizedTrade:
    when = datetime(2026, 5, day, hour, 0)
    return NormalizedTrade(entry_time=when, exit_time=when, pnl=pnl)


def test_generate_markdown_report_contains_required_sections() -> None:
    stats = analyze_trades(
        [
            _trade(1, 9, 150.0),
            _trade(2, 10, -350.0),
            _trade(2, 10, -50.0),
        ]
    )
    risk = evaluate_risk(stats, RiskGuardConfig(daily_loss_limit=-300.0))

    report = generate_markdown_report(stats, risk)

    assert "# Trading Report" in report
    assert "## Global Summary" in report
    assert "- Total trades: 3" in report
    assert "- Total PnL: -250.00" in report
    assert "## Best Days" in report
    assert "2026-05-01: 150.00" in report
    assert "## Worst Hours" in report
    assert "10:00: -400.00" in report
    assert "## Risk Guard Alerts" in report
    assert "daily_loss" in report
    assert "## Proposed Apex Rules" in report
    assert "Stop trading after 300.00 daily loss" in report
