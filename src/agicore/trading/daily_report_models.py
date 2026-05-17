"""Models for offline daily trading reports."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DailyTradingReport:
    """Aggregated daily trading report ready for Markdown rendering."""

    report_date: date
    session_summary: str
    total_pnl: float
    trade_count: int
    win_rate: float
    discipline_score: int
    emotional_risk_score: int
    consistency_score: int
    behavior_classifications: tuple[str, ...]
    rule_violations: tuple[str, ...]
    recommendations: tuple[str, ...]
    memory_comparison: tuple[str, ...]
    playbook_alignment: tuple[str, ...]
    strategy_alignment: tuple[str, ...]
    next_session_action_plan: tuple[str, ...]


__all__ = ["DailyTradingReport"]
