"""Models for offline adaptive trader memory."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from .behavior_models import BehaviorPattern, SessionBehaviorClass


class MemoryComparisonSignal(StrEnum):
    """Signals detected when comparing a new behavior sample to memory."""

    IMPROVEMENT = "IMPROVEMENT"
    DEGRADATION = "DEGRADATION"
    REPEATED_ERROR = "REPEATED_ERROR"
    RECURRING_BEHAVIORAL_RISK = "RECURRING_BEHAVIORAL_RISK"
    RECURRING_FAVORABLE_CONTEXT = "RECURRING_FAVORABLE_CONTEXT"


class AdaptiveRecommendation(StrEnum):
    """Recommendations based on historical behavior memory."""

    STRENGTHEN_MAX_TRADES_LIMIT = "STRENGTHEN_MAX_TRADES_LIMIT"
    AVOID_RECURRING_TOXIC_HOURS = "AVOID_RECURRING_TOXIC_HOURS"
    KEEP_CURRENT_RULES = "KEEP_CURRENT_RULES"
    REDUCE_SIZE_FOR_RECURRING_RISK = "REDUCE_SIZE_FOR_RECURRING_RISK"
    REQUIRE_BREAK_AFTER_LOSS = "REQUIRE_BREAK_AFTER_LOSS"


@dataclass(frozen=True)
class TraderMemoryProfile:
    """Aggregated adaptive memory for one trader."""

    sessions_count: int = 0
    average_discipline_score: float = 0.0
    average_emotional_risk_score: float = 0.0
    average_consistency_score: float = 0.0
    recurring_behavior_classes: tuple[SessionBehaviorClass, ...] = ()
    recurring_patterns: tuple[BehaviorPattern, ...] = ()
    recurring_dangerous_hours: tuple[int, ...] = ()
    favorable_contexts: tuple[str, ...] = ()
    worst_contexts: tuple[str, ...] = ()
    behavior_class_counts: dict[str, int] = field(default_factory=dict)
    pattern_counts: dict[str, int] = field(default_factory=dict)
    dangerous_hour_counts: dict[str, int] = field(default_factory=dict)
    favorable_context_counts: dict[str, int] = field(default_factory=dict)
    worst_context_counts: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class MemoryComparisonResult:
    """Comparison of new behavior against historical trader memory."""

    signals: tuple[MemoryComparisonSignal, ...]
    repeated_classes: tuple[SessionBehaviorClass, ...] = ()
    repeated_patterns: tuple[BehaviorPattern, ...] = ()
    repeated_dangerous_hours: tuple[int, ...] = ()
    matched_favorable_contexts: tuple[str, ...] = ()
    discipline_delta: float = 0.0
    emotional_risk_delta: float = 0.0
    consistency_delta: float = 0.0


__all__ = [
    "AdaptiveRecommendation",
    "MemoryComparisonResult",
    "MemoryComparisonSignal",
    "TraderMemoryProfile",
]
