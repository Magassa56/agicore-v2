"""Offline adaptive memory for AGIcore trading behavior."""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .adaptive_memory_models import (
    AdaptiveRecommendation,
    MemoryComparisonResult,
    MemoryComparisonSignal,
    TraderMemoryProfile,
)
from .behavior_models import BehaviorAnalysisResult, BehaviorPattern, SessionBehaviorClass


RISK_CLASSES = {
    SessionBehaviorClass.AGGRESSIVE,
    SessionBehaviorClass.OVERTRADING,
    SessionBehaviorClass.REVENGE_TRADING_PROBABLE,
    SessionBehaviorClass.HIGH_RISK,
    SessionBehaviorClass.UNSTABLE,
}
RISK_PATTERNS = {
    BehaviorPattern.SIZE_INCREASE_AFTER_LOSSES,
    BehaviorPattern.TRADE_FREQUENCY_ACCELERATION,
    BehaviorPattern.CONTINUED_AFTER_LIMIT_BREACH,
    BehaviorPattern.LATE_TRADING_DEGRADATION,
}


def update_trader_memory(
    behavior: BehaviorAnalysisResult,
    memory: TraderMemoryProfile | None = None,
) -> TraderMemoryProfile:
    """Update trader memory with one behavior analysis result."""
    existing = memory or TraderMemoryProfile()
    new_count = existing.sessions_count + 1
    class_counts = dict(existing.behavior_class_counts)
    pattern_counts = dict(existing.pattern_counts)
    dangerous_hour_counts = dict(existing.dangerous_hour_counts)
    favorable_context_counts = dict(existing.favorable_context_counts)
    worst_context_counts = dict(existing.worst_context_counts)

    _increment_all(class_counts, (item.value for item in behavior.classifications))
    _increment_all(pattern_counts, (item.value for item in behavior.patterns))
    _increment_all(dangerous_hour_counts, (str(hour) for hour in behavior.summary.dangerous_hours))
    if behavior.summary.favorable_context:
        _increment_all(favorable_context_counts, (behavior.summary.favorable_context,))
    for weakness in behavior.summary.weaknesses:
        _increment_all(worst_context_counts, (weakness,))

    return TraderMemoryProfile(
        sessions_count=new_count,
        average_discipline_score=_rolling_average(
            existing.average_discipline_score,
            existing.sessions_count,
            behavior.scores.discipline_score,
        ),
        average_emotional_risk_score=_rolling_average(
            existing.average_emotional_risk_score,
            existing.sessions_count,
            behavior.scores.emotional_risk_score,
        ),
        average_consistency_score=_rolling_average(
            existing.average_consistency_score,
            existing.sessions_count,
            behavior.scores.consistency_score,
        ),
        recurring_behavior_classes=_recurring_classes(class_counts, new_count),
        recurring_patterns=_recurring_patterns(pattern_counts, new_count),
        recurring_dangerous_hours=_recurring_hours(dangerous_hour_counts, new_count),
        favorable_contexts=_top_keys(favorable_context_counts),
        worst_contexts=_top_keys(worst_context_counts),
        behavior_class_counts=class_counts,
        pattern_counts=pattern_counts,
        dangerous_hour_counts=dangerous_hour_counts,
        favorable_context_counts=favorable_context_counts,
        worst_context_counts=worst_context_counts,
    )


def compare_session_to_memory(
    behavior: BehaviorAnalysisResult,
    memory: TraderMemoryProfile,
) -> MemoryComparisonResult:
    """Compare a new behavior analysis result to historical memory."""
    discipline_delta = behavior.scores.discipline_score - memory.average_discipline_score
    emotional_delta = behavior.scores.emotional_risk_score - memory.average_emotional_risk_score
    consistency_delta = behavior.scores.consistency_score - memory.average_consistency_score
    repeated_classes = tuple(
        item for item in behavior.classifications if item in memory.recurring_behavior_classes
    )
    repeated_patterns = tuple(item for item in behavior.patterns if item in memory.recurring_patterns)
    repeated_hours = tuple(
        hour for hour in behavior.summary.dangerous_hours if hour in memory.recurring_dangerous_hours
    )
    matched_contexts = tuple(
        context
        for context in memory.favorable_contexts
        if context == behavior.summary.favorable_context
    )

    signals: set[MemoryComparisonSignal] = set()
    if discipline_delta >= 5 and emotional_delta >= 0:
        signals.add(MemoryComparisonSignal.IMPROVEMENT)
    if discipline_delta <= -5 or emotional_delta <= -10 or consistency_delta <= -10:
        signals.add(MemoryComparisonSignal.DEGRADATION)
    if repeated_patterns or repeated_hours:
        signals.add(MemoryComparisonSignal.REPEATED_ERROR)
    if any(item in RISK_CLASSES for item in repeated_classes) or any(
        item in RISK_PATTERNS for item in repeated_patterns
    ):
        signals.add(MemoryComparisonSignal.RECURRING_BEHAVIORAL_RISK)
    if matched_contexts:
        signals.add(MemoryComparisonSignal.RECURRING_FAVORABLE_CONTEXT)

    return MemoryComparisonResult(
        signals=tuple(sorted(signals, key=lambda item: item.value)),
        repeated_classes=repeated_classes,
        repeated_patterns=repeated_patterns,
        repeated_dangerous_hours=repeated_hours,
        matched_favorable_contexts=matched_contexts,
        discipline_delta=discipline_delta,
        emotional_risk_delta=emotional_delta,
        consistency_delta=consistency_delta,
    )


def generate_adaptive_recommendations(
    memory: TraderMemoryProfile,
    comparison: MemoryComparisonResult | None = None,
) -> tuple[AdaptiveRecommendation, ...]:
    """Generate recommendations from historical memory and optional comparison."""
    recommendations: set[AdaptiveRecommendation] = set()
    recurring_classes = set(memory.recurring_behavior_classes)
    recurring_patterns = set(memory.recurring_patterns)
    signals = set(comparison.signals) if comparison is not None else set()

    if SessionBehaviorClass.OVERTRADING in recurring_classes:
        recommendations.add(AdaptiveRecommendation.STRENGTHEN_MAX_TRADES_LIMIT)
    if memory.recurring_dangerous_hours:
        recommendations.add(AdaptiveRecommendation.AVOID_RECURRING_TOXIC_HOURS)
    if BehaviorPattern.SIZE_INCREASE_AFTER_LOSSES in recurring_patterns:
        recommendations.add(AdaptiveRecommendation.REDUCE_SIZE_FOR_RECURRING_RISK)
    if (
        BehaviorPattern.TRADE_FREQUENCY_ACCELERATION in recurring_patterns
        or SessionBehaviorClass.REVENGE_TRADING_PROBABLE in recurring_classes
    ):
        recommendations.add(AdaptiveRecommendation.REQUIRE_BREAK_AFTER_LOSS)
    if (
        MemoryComparisonSignal.IMPROVEMENT in signals
        and not recommendations
    ) or (
        not recommendations
        and memory.average_discipline_score >= 85
        and memory.average_emotional_risk_score >= 85
    ):
        recommendations.add(AdaptiveRecommendation.KEEP_CURRENT_RULES)
    if MemoryComparisonSignal.DEGRADATION in signals and not recommendations:
        recommendations.add(AdaptiveRecommendation.REQUIRE_BREAK_AFTER_LOSS)

    return tuple(sorted(recommendations, key=lambda item: item.value))


def save_trader_memory(memory: TraderMemoryProfile, path: str | Path) -> None:
    """Save trader memory as simple JSON."""
    json_path = Path(path)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(asdict(memory), indent=2, sort_keys=True),
        encoding="utf-8",
    )


def load_trader_memory(path: str | Path) -> TraderMemoryProfile:
    """Load trader memory from simple JSON."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return TraderMemoryProfile(
        sessions_count=payload.get("sessions_count", 0),
        average_discipline_score=payload.get("average_discipline_score", 0.0),
        average_emotional_risk_score=payload.get("average_emotional_risk_score", 0.0),
        average_consistency_score=payload.get("average_consistency_score", 0.0),
        recurring_behavior_classes=tuple(
            SessionBehaviorClass(item) for item in payload.get("recurring_behavior_classes", ())
        ),
        recurring_patterns=tuple(
            BehaviorPattern(item) for item in payload.get("recurring_patterns", ())
        ),
        recurring_dangerous_hours=tuple(payload.get("recurring_dangerous_hours", ())),
        favorable_contexts=tuple(payload.get("favorable_contexts", ())),
        worst_contexts=tuple(payload.get("worst_contexts", ())),
        behavior_class_counts=dict(payload.get("behavior_class_counts", {})),
        pattern_counts=dict(payload.get("pattern_counts", {})),
        dangerous_hour_counts=dict(payload.get("dangerous_hour_counts", {})),
        favorable_context_counts=dict(payload.get("favorable_context_counts", {})),
        worst_context_counts=dict(payload.get("worst_context_counts", {})),
    )


def _increment_all(counts: dict[str, int], values) -> None:
    for value in values:
        counts[str(value)] = counts.get(str(value), 0) + 1


def _rolling_average(current_average: float, current_count: int, new_value: float) -> float:
    if current_count <= 0:
        return float(new_value)
    return ((current_average * current_count) + new_value) / (current_count + 1)


def _recurring_classes(counts: dict[str, int], sessions_count: int) -> tuple[SessionBehaviorClass, ...]:
    return tuple(
        SessionBehaviorClass(item)
        for item in _recurring_keys(counts, sessions_count)
    )


def _recurring_patterns(counts: dict[str, int], sessions_count: int) -> tuple[BehaviorPattern, ...]:
    return tuple(
        BehaviorPattern(item)
        for item in _recurring_keys(counts, sessions_count)
    )


def _recurring_hours(counts: dict[str, int], sessions_count: int) -> tuple[int, ...]:
    return tuple(int(item) for item in _recurring_keys(counts, sessions_count))


def _recurring_keys(counts: dict[str, int], sessions_count: int) -> tuple[str, ...]:
    threshold = 2 if sessions_count >= 2 else 1
    return tuple(
        key
        for key, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        if counts[key] >= threshold
    )


def _top_keys(counts: dict[str, int], limit: int = 5) -> tuple[str, ...]:
    return tuple(
        key for key, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]
    )


__all__ = [
    "compare_session_to_memory",
    "generate_adaptive_recommendations",
    "load_trader_memory",
    "save_trader_memory",
    "update_trader_memory",
]
