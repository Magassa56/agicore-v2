"""Unit tests for offline adaptive policy memory."""
from __future__ import annotations

from pathlib import Path

from agicore.trading.adaptive_policy_memory import (
    compare_policy_performance,
    identify_dangerous_policies,
    load_policy_memory,
    recommend_policy_for_context,
    render_policy_memory_markdown,
    save_policy_memory,
    update_policy_memory,
)
from agicore.trading.adaptive_policy_memory_models import (
    AdaptivePolicyMemory,
    PolicyContextSignature,
    PolicyMemoryRecommendation,
)
from agicore.trading.behavior_models import (
    BehaviorAnalysisResult,
    BehaviorRecommendation,
    BehaviorScores,
    BehaviorSummary,
    SessionBehaviorClass,
)
from agicore.trading.market_regime_models import (
    MarketRegime,
    MarketRegimeAnalysis,
    RegimeStrength,
    SessionCondition,
    VolatilityRegime,
)
from agicore.trading.policy_evaluation_models import (
    PolicyComparisonResult,
    PolicyEvaluationResult,
    PolicyRule,
    TradingPolicy,
)


def _rule(policy: TradingPolicy) -> PolicyRule:
    return PolicyRule(
        policy=policy,
        min_context_score=60,
        reduce_risk_below_score=70,
        block_high_risk_context=True,
        allow_high_risk_override=False,
        reduce_size_on_caution=True,
        block_revenge_trading=True,
        block_overtrading=True,
    )


def _result(
    policy: TradingPolicy,
    *,
    reward: float,
    normalized: int,
    context: float,
    dangerous: int = 0,
    accepted: int = 3,
    blocked: int = 1,
    reduced: int = 0,
    scenarios: int = 4,
) -> PolicyEvaluationResult:
    return PolicyEvaluationResult(
        policy=policy,
        rule=_rule(policy),
        total_reward=int(reward * scenarios),
        normalized_reward=normalized,
        accepted_trades=accepted,
        blocked_trades=blocked,
        reduced_risk_trades=reduced,
        dangerous_decisions=dangerous,
        average_context_score=context,
        average_reward=reward,
        best_policy=False,
        best_policy_reason="test",
        scenario_count=scenarios,
        semi_auto_decisions=(),
        paper_execution_results=(),
        reward_results=(),
        risk_notes=(),
    )


def _market(regime: MarketRegime = MarketRegime.TRENDING_UP) -> MarketRegimeAnalysis:
    return MarketRegimeAnalysis(
        primary_regime=regime,
        confidence=85,
        strength=RegimeStrength.STRONG,
        volatility=VolatilityRegime.NORMAL,
        session_condition=SessionCondition.FAVORABLE,
        context_quality_score=85,
        favorable_for_pullback_strategy=True,
        dangerous_market=False,
        detected_regimes=(regime,),
        warnings=(),
        recommendations=(),
    )


def _behavior(*classes: SessionBehaviorClass) -> BehaviorAnalysisResult:
    return BehaviorAnalysisResult(
        classifications=classes or (SessionBehaviorClass.DISCIPLINED,),
        patterns=(),
        scores=BehaviorScores(
            discipline_score=80,
            emotional_risk_score=30,
            consistency_score=80,
            risk_escalation_score=20,
        ),
        recommendations=(BehaviorRecommendation.KEEP_CURRENT_RULES,),
        summary=BehaviorSummary(
            strengths=(),
            weaknesses=(),
            dangerous_hours=(),
            favorable_context="test",
            probable_trader_profile="test",
        ),
    )


def test_update_policy_memory_aggregates_recommendations_and_disabled_policies() -> None:
    memory = update_policy_memory(
        policy_results=(
            _result(TradingPolicy.BALANCED, reward=35, normalized=85, context=88),
            _result(TradingPolicy.AGGRESSIVE, reward=-30, normalized=20, context=35, dangerous=3, accepted=4, blocked=0),
        ),
        market_regime=_market(),
        behavior_result=_behavior(),
        strategy_name="EMA20",
    )

    assert set(memory.entries) == {"BALANCED", "AGGRESSIVE"}
    assert memory.entries["BALANCED"].recommendation in {
        PolicyMemoryRecommendation.PRIORITIZE_POLICY,
        PolicyMemoryRecommendation.KEEP_POLICY,
    }
    assert memory.entries["AGGRESSIVE"].recommendation == PolicyMemoryRecommendation.DISABLE_POLICY
    assert "AGGRESSIVE" in memory.disabled_policies
    assert memory.entries["BALANCED"].regime_performance["TRENDING_UP"] == 35


def test_compare_policy_performance_orders_safe_policy_first() -> None:
    memory = update_policy_memory(
        policy_results=(
            _result(TradingPolicy.AGGRESSIVE, reward=-20, normalized=20, context=40, dangerous=3),
            _result(TradingPolicy.CONSERVATIVE, reward=20, normalized=75, context=82, dangerous=0),
        ),
        market_regime=_market(),
        behavior_result=_behavior(),
    )

    ranked = compare_policy_performance(memory)

    assert ranked[0].policy_name == "CONSERVATIVE"
    assert ranked[-1].policy_name == "AGGRESSIVE"


def test_recommend_policy_for_context_uses_regime_and_behavior_memory() -> None:
    memory = update_policy_memory(
        policy_results=(
            _result(TradingPolicy.BALANCED, reward=28, normalized=82, context=85),
            _result(TradingPolicy.NO_TRADE_ON_HIGH_RISK, reward=10, normalized=68, context=70, accepted=1, blocked=3),
        ),
        market_regime=_market(MarketRegime.TRENDING_UP),
        behavior_result=_behavior(SessionBehaviorClass.DISCIPLINED),
        strategy_name="EMA20",
    )

    recommended = recommend_policy_for_context(
        memory,
        PolicyContextSignature(
            market_regime="TRENDING_UP",
            behavior_classification=("DISCIPLINED",),
            context_score_bucket="HIGH",
            strategy_name="EMA20",
        ),
    )

    assert recommended is not None
    assert recommended.policy_name == "BALANCED"


def test_identify_dangerous_policies_flags_low_confidence_and_high_danger() -> None:
    memory = update_policy_memory(
        policy_results=(
            _result(TradingPolicy.BALANCED, reward=25, normalized=80, context=85),
            _result(TradingPolicy.AGGRESSIVE, reward=-10, normalized=35, context=45, dangerous=2),
        ),
        market_regime=_market(),
        behavior_result=_behavior(SessionBehaviorClass.OVERTRADING),
    )

    assert identify_dangerous_policies(memory) == ("AGGRESSIVE",)


def test_update_policy_memory_accepts_policy_comparison_result() -> None:
    comparison = PolicyComparisonResult(
        results=(
            _result(TradingPolicy.CONSERVATIVE, reward=12, normalized=70, context=75),
            _result(TradingPolicy.BALANCED, reward=18, normalized=78, context=80),
        ),
        best_policy=TradingPolicy.BALANCED,
        best_policy_reason="best",
        recommendation="use balanced",
        risks_detected=(),
    )

    memory = update_policy_memory(comparison_result=comparison, market_regime=_market())

    assert set(memory.entries) == {"CONSERVATIVE", "BALANCED"}
    assert len(memory.snapshots) == 2


def test_save_and_load_policy_memory_roundtrip(tmp_path: Path) -> None:
    memory = update_policy_memory(
        policy_results=(_result(TradingPolicy.BALANCED, reward=15, normalized=72, context=76),),
        market_regime=_market(),
        behavior_result=_behavior(),
    )
    path = tmp_path / "policy_memory.json"

    save_policy_memory(path, memory)
    loaded = load_policy_memory(path)

    assert loaded == memory


def test_render_policy_memory_markdown_contains_required_sections() -> None:
    memory = update_policy_memory(
        policy_results=(_result(TradingPolicy.BALANCED, reward=20, normalized=75, context=80),),
        market_regime=_market(),
        behavior_result=_behavior(),
    )

    markdown = render_policy_memory_markdown(memory)

    assert "# Adaptive Policy Memory" in markdown
    assert "## Resume memoire" in markdown
    assert "## Classement politiques" in markdown
    assert "## Politiques dangereuses" in markdown
    assert "## Meilleurs contextes" in markdown
    assert "## Pires contextes" in markdown
    assert "## Recommandations AGIcore" in markdown
    assert "no broker" in markdown


def test_update_empty_memory_keeps_empty_state() -> None:
    memory = update_policy_memory(AdaptivePolicyMemory())

    assert memory.entries == {}
    assert memory.snapshots == ()
    assert memory.disabled_policies == ()
