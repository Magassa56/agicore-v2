"""Models for offline trader behavior intelligence."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class SessionBehaviorClass(StrEnum):
    """Behavior classes inferred from replayed sessions."""

    DISCIPLINED = "DISCIPLINED"
    AGGRESSIVE = "AGGRESSIVE"
    OVERTRADING = "OVERTRADING"
    REVENGE_TRADING_PROBABLE = "REVENGE_TRADING_PROBABLE"
    HIGH_RISK = "HIGH_RISK"
    CONSISTENT = "CONSISTENT"
    UNSTABLE = "UNSTABLE"


class BehaviorPattern(StrEnum):
    """Heuristic psychological or execution patterns."""

    SIZE_INCREASE_AFTER_LOSSES = "SIZE_INCREASE_AFTER_LOSSES"
    TRADE_FREQUENCY_ACCELERATION = "TRADE_FREQUENCY_ACCELERATION"
    LOSS_AFTER_WINNING_STREAK = "LOSS_AFTER_WINNING_STREAK"
    CONTINUED_AFTER_LIMIT_BREACH = "CONTINUED_AFTER_LIMIT_BREACH"
    LATE_TRADING_DEGRADATION = "LATE_TRADING_DEGRADATION"
    DISCIPLINED_RECOVERY_AFTER_LOSS = "DISCIPLINED_RECOVERY_AFTER_LOSS"


class BehaviorRecommendation(StrEnum):
    """Discipline recommendations emitted by the behavior layer."""

    STOP_TRADING = "STOP_TRADING"
    REDUCE_SIZE = "REDUCE_SIZE"
    TAKE_BREAK = "TAKE_BREAK"
    KEEP_CURRENT_RULES = "KEEP_CURRENT_RULES"
    AVOID_SPECIFIC_HOURS = "AVOID_SPECIFIC_HOURS"
    LIMIT_MAX_TRADES = "LIMIT_MAX_TRADES"


@dataclass(frozen=True)
class BehaviorScores:
    """Normalized behavior scores from 0 to 100."""

    discipline_score: int
    emotional_risk_score: int
    consistency_score: int
    risk_escalation_score: int


@dataclass(frozen=True)
class BehaviorSummary:
    """Human-readable behavior synthesis."""

    strengths: tuple[str, ...]
    weaknesses: tuple[str, ...]
    dangerous_hours: tuple[int, ...]
    favorable_context: str
    probable_trader_profile: str


@dataclass(frozen=True)
class BehaviorAnalysisResult:
    """Complete offline behavior analysis result."""

    classifications: tuple[SessionBehaviorClass, ...]
    patterns: tuple[BehaviorPattern, ...]
    scores: BehaviorScores
    recommendations: tuple[BehaviorRecommendation, ...]
    summary: BehaviorSummary
    comparison_notes: tuple[str, ...] = ()


__all__ = [
    "BehaviorAnalysisResult",
    "BehaviorPattern",
    "BehaviorRecommendation",
    "BehaviorScores",
    "BehaviorSummary",
    "SessionBehaviorClass",
]
