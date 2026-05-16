"""Markdown reporting for offline trade analysis."""
from __future__ import annotations

from datetime import date

from .analyze_trades import TradeStats
from .risk_guard import RiskGuardResult


def generate_markdown_report(stats: TradeStats, risk: RiskGuardResult) -> str:
    """Generate a compact Markdown trading report."""
    best_days = _rank_dates(stats.pnl_by_day, reverse=True)
    worst_days = _rank_dates(stats.pnl_by_day, reverse=False)
    best_hours = _rank_hours(stats.pnl_by_hour, reverse=True)
    worst_hours = _rank_hours(stats.pnl_by_hour, reverse=False)

    lines = [
        "# Trading Report",
        "",
        "## Global Summary",
        "",
        f"- Total trades: {stats.total_trades}",
        f"- Total PnL: {_money(stats.total_pnl)}",
        f"- Win rate: {stats.win_rate:.2%}",
        f"- Average trade: {_money(stats.average_trade)}",
        f"- Largest gain: {_money(stats.largest_gain)}",
        f"- Largest loss: {_money(stats.largest_loss)}",
        f"- Max consecutive losses: {stats.max_consecutive_losses}",
        f"- Average MAE: {_optional_money(stats.average_mae)}",
        f"- Average MFE: {_optional_money(stats.average_mfe)}",
        "",
        "## Best Days",
        "",
        *_format_date_rows(best_days),
        "",
        "## Worst Days",
        "",
        *_format_date_rows(worst_days),
        "",
        "## Best Hours",
        "",
        *_format_hour_rows(best_hours),
        "",
        "## Worst Hours",
        "",
        *_format_hour_rows(worst_hours),
        "",
        "## Risk Guard Alerts",
        "",
        *_format_alerts(risk),
        "",
        "## Proposed Apex Rules",
        "",
        *_format_rules(risk),
        "",
    ]
    return "\n".join(lines)


def _rank_dates(values: dict[date, float], *, reverse: bool) -> list[tuple[date, float]]:
    return sorted(values.items(), key=lambda item: item[1], reverse=reverse)[:3]


def _rank_hours(values: dict[int, float], *, reverse: bool) -> list[tuple[int, float]]:
    return sorted(values.items(), key=lambda item: item[1], reverse=reverse)[:3]


def _format_date_rows(rows: list[tuple[date, float]]) -> list[str]:
    if not rows:
        return ["- No data"]
    return [f"- {day.isoformat()}: {_money(pnl)}" for day, pnl in rows]


def _format_hour_rows(rows: list[tuple[int, float]]) -> list[str]:
    if not rows:
        return ["- No data"]
    return [f"- {hour:02d}:00: {_money(pnl)}" for hour, pnl in rows]


def _format_alerts(risk: RiskGuardResult) -> list[str]:
    if not risk.alerts:
        return ["- No alerts"]
    return [f"- [{alert.severity}] {alert.kind}: {alert.message}" for alert in risk.alerts]


def _format_rules(risk: RiskGuardResult) -> list[str]:
    if not risk.apex_rules:
        return ["- No rules proposed"]
    return [f"- {rule}" for rule in risk.apex_rules]


def _money(value: float) -> str:
    return f"{value:.2f}"


def _optional_money(value: float | None) -> str:
    return "n/a" if value is None else _money(value)


__all__ = ["generate_markdown_report"]
