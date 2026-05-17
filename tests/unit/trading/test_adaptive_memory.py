"""Unit tests for offline adaptive trader memory."""
from __future__ import annotations

import pytest

from agicore.trading.adaptive_memory import (
    compare_session_to_memory,
    generate_adaptive_recommendations,
    load_trader_memory,
    save_trader_memory,
    update_trader_memory,
)
from agicore.trading.adaptive_memory_models import (
    AdaptiveRecommendation,
    MemoryComparisonSignal,
)
from agicore.trading.behavior_models import (
    BehaviorAnalysisResult,
    BehaviorPattern,
    BehaviorRecommendation,
    BehaviorScores,
    BehaviorSummary,
    SessionBehaviorClass,
)


def _behavior(
    *,
    discipline: int = 100,
    emotional: int = 100,
    consistency: int = 100,
    escalation: int = 100,
    classes: tuple[SessionBehaviorClass, ...] = (SessionBehaviorClass.DISCIPLINED,),
    patterns: tuple[BehaviorPattern, ...] = (),
    dangerous_hours: tuple[int, ...] = (),
    favorable_context: str = "Best observed start-hour context: 09:00 with PnL 100.00",
    weaknesses: tuple[str, ...] = ("No major behavioral weakness detected",),
) -> BehaviorAnalysisResult:
    return BehaviorAnalysisResult(
        classifications=classes,
        patterns=patterns,
        scores=BehaviorScores(
            discipline_score=discipline,
            emotional_risk_score=emotional,
            consistency_score=consistency,
            risk_escalation_score=escalation,
        ),
        recommendations=(BehaviorRecommendation.KEEP_CURRENT_RULES,),
        summary=BehaviorSummary(
            strengths=("High replay discipline score",),
            weaknesses=weaknesses,
            dangerous_hours=dangerous_hours,
            favorable_context=favorable_context,
            probable_trader_profile="Rule-following consistent trader",
        ),
    )


def test_update_trader_memory_creates_profile_from_first_behavior() -> None:
    behavior = _behavior(
        classes=(SessionBehaviorClass.DISCIPLINED, SessionBehaviorClass.CONSISTENT),
        patterns=(BehaviorPattern.DISCIPLINED_RECOVERY_AFTER_LOSS,),
    )

    memory = update_trader_memory(behavior)

    assert memory.sessions_count == 1
    assert memory.average_discipline_score == 100
    assert memory.average_emotional_risk_score == 100
    assert memory.average_consistency_score == 100
    assert memory.recurring_behavior_classes == (
        SessionBehaviorClass.CONSISTENT,
        SessionBehaviorClass.DISCIPLINED,
    )
    assert memory.recurring_patterns == (BehaviorPattern.DISCIPLINED_RECOVERY_AFTER_LOSS,)
    assert memory.favorable_contexts == ("Best observed start-hour context: 09:00 with PnL 100.00",)


def test_update_trader_memory_tracks_averages_and_recurring_risks() -> None:
    risky = _behavior(
        discipline=40,
        emotional=55,
        consistency=60,
        classes=(SessionBehaviorClass.OVERTRADING, SessionBehaviorClass.HIGH_RISK),
        patterns=(
            BehaviorPattern.SIZE_INCREASE_AFTER_LOSSES,
            BehaviorPattern.TRADE_FREQUENCY_ACCELERATION,
        ),
        dangerous_hours=(20,),
        weaknesses=("Trade count exceeded declared limits",),
    )

    memory = update_trader_memory(risky)
    memory = update_trader_memory(risky, memory)

    assert memory.sessions_count == 2
    assert memory.average_discipline_score == 40
    assert memory.average_emotional_risk_score == 55
    assert memory.average_consistency_score == 60
    assert SessionBehaviorClass.OVERTRADING in memory.recurring_behavior_classes
    assert SessionBehaviorClass.HIGH_RISK in memory.recurring_behavior_classes
    assert BehaviorPattern.SIZE_INCREASE_AFTER_LOSSES in memory.recurring_patterns
    assert BehaviorPattern.TRADE_FREQUENCY_ACCELERATION in memory.recurring_patterns
    assert memory.recurring_dangerous_hours == (20,)
    assert memory.worst_contexts == ("Trade count exceeded declared limits",)


def test_compare_session_to_memory_detects_improvement_and_favorable_context() -> None:
    historical = update_trader_memory(
        _behavior(discipline=70, emotional=70, consistency=70),
    )
    improved = _behavior(discipline=90, emotional=80, consistency=80)

    comparison = compare_session_to_memory(improved, historical)

    assert MemoryComparisonSignal.IMPROVEMENT in comparison.signals
    assert MemoryComparisonSignal.RECURRING_FAVORABLE_CONTEXT in comparison.signals
    assert comparison.discipline_delta == pytest.approx(20)
    assert comparison.emotional_risk_delta == pytest.approx(10)
    assert comparison.matched_favorable_contexts == historical.favorable_contexts


def test_compare_session_to_memory_detects_degradation_and_repeated_errors() -> None:
    risky = _behavior(
        discipline=45,
        emotional=45,
        consistency=60,
        classes=(SessionBehaviorClass.OVERTRADING, SessionBehaviorClass.HIGH_RISK),
        patterns=(BehaviorPattern.SIZE_INCREASE_AFTER_LOSSES,),
        dangerous_hours=(20,),
    )
    memory = update_trader_memory(risky)
    memory = update_trader_memory(risky, memory)
    worse = _behavior(
        discipline=20,
        emotional=20,
        consistency=40,
        classes=(SessionBehaviorClass.OVERTRADING,),
        patterns=(BehaviorPattern.SIZE_INCREASE_AFTER_LOSSES,),
        dangerous_hours=(20,),
    )

    comparison = compare_session_to_memory(worse, memory)

    assert MemoryComparisonSignal.DEGRADATION in comparison.signals
    assert MemoryComparisonSignal.REPEATED_ERROR in comparison.signals
    assert MemoryComparisonSignal.RECURRING_BEHAVIORAL_RISK in comparison.signals
    assert comparison.repeated_classes == (SessionBehaviorClass.OVERTRADING,)
    assert comparison.repeated_patterns == (BehaviorPattern.SIZE_INCREASE_AFTER_LOSSES,)
    assert comparison.repeated_dangerous_hours == (20,)


def test_generate_adaptive_recommendations_uses_memory_and_comparison() -> None:
    risky = _behavior(
        classes=(
            SessionBehaviorClass.OVERTRADING,
            SessionBehaviorClass.REVENGE_TRADING_PROBABLE,
        ),
        patterns=(
            BehaviorPattern.SIZE_INCREASE_AFTER_LOSSES,
            BehaviorPattern.TRADE_FREQUENCY_ACCELERATION,
        ),
        dangerous_hours=(20,),
    )
    memory = update_trader_memory(risky)
    memory = update_trader_memory(risky, memory)
    comparison = compare_session_to_memory(risky, memory)

    recommendations = generate_adaptive_recommendations(memory, comparison)

    assert AdaptiveRecommendation.STRENGTHEN_MAX_TRADES_LIMIT in recommendations
    assert AdaptiveRecommendation.AVOID_RECURRING_TOXIC_HOURS in recommendations
    assert AdaptiveRecommendation.REDUCE_SIZE_FOR_RECURRING_RISK in recommendations
    assert AdaptiveRecommendation.REQUIRE_BREAK_AFTER_LOSS in recommendations


def test_generate_adaptive_recommendations_keeps_rules_when_memory_is_strong() -> None:
    memory = update_trader_memory(
        _behavior(
            discipline=95,
            emotional=95,
            classes=(SessionBehaviorClass.DISCIPLINED, SessionBehaviorClass.CONSISTENT),
        )
    )

    recommendations = generate_adaptive_recommendations(memory)

    assert recommendations == (AdaptiveRecommendation.KEEP_CURRENT_RULES,)


def test_save_and_load_trader_memory_round_trip(tmp_path) -> None:
    path = tmp_path / "trader_memory.json"
    risky = _behavior(
        discipline=40,
        emotional=50,
        classes=(SessionBehaviorClass.OVERTRADING,),
        patterns=(BehaviorPattern.SIZE_INCREASE_AFTER_LOSSES,),
        dangerous_hours=(20,),
    )
    memory = update_trader_memory(risky)

    save_trader_memory(memory, path)
    loaded = load_trader_memory(path)

    assert loaded == memory
