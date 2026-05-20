"""Unit tests for offline meta strategy selector."""
from __future__ import annotations

from agicore.trading.adaptive_policy_memory_models import (
    AdaptivePolicyMemory,
    PolicyMemoryEntry,
    PolicyMemoryRecommendation,
)
from agicore.trading.behavior_models import (
    BehaviorAnalysisResult,
    BehaviorRecommendation,
    BehaviorScores,
    BehaviorSummary,
    SessionBehaviorClass,
)
from agicore.trading.context_scoring_models import (
    ContextScoreBreakdown,
    ContextScoringResult,
    TradeContextDecision,
)
from agicore.trading.market_regime_models import (
    MarketRegime,
    MarketRegimeAnalysis,
    RegimeStrength,
    SessionCondition,
    VolatilityRegime,
)
from agicore.trading.meta_strategy_models import (
    MetaStrategyCandidate,
    MetaStrategyDecision,
    MetaStrategyReason,
    MetaStrategySelectionInput,
)
from agicore.trading.meta_strategy_selector import (
    rank_strategy_candidates,
    render_meta_strategy_markdown,
    select_meta_strategy,
)
from agicore.trading.policy_evaluation_models import PolicyEvaluationResult, PolicyRule, TradingPolicy
from agicore.trading.safe_rl_models import SafeRLExperimentResult, SafeRLStatus
from agicore.trading.semi_auto_decision_models import SemiAutoAction, SemiAutoDecision, SemiAutoDecisionResult
from agicore.trading.strategy_dna_models import StrategyDNA, TradeDirection


def _entry(
    policy_name: str,
    *,
    reward: float = 25.0,
    confidence: int = 80,
    dangerous: float = 0.0,
    recommendation: PolicyMemoryRecommendation = PolicyMemoryRecommendation.KEEP_POLICY,
) -> PolicyMemoryEntry:
    return PolicyMemoryEntry(
        policy_name=policy_name,
        total_evaluations=5,
        average_reward=reward,
        average_context_score=82.0,
        dangerous_decision_rate=dangerous,
        blocked_trade_rate=0.2,
        accepted_trade_rate=0.7,
        reduced_risk_rate=0.1,
        confidence_score=confidence,
        recommendation=recommendation,
        best_contexts=("regime=TRENDING_UP; behavior=DISCIPLINED; score=HIGH; strategy=EMA20",),
        worst_contexts=(),
        regime_performance={"TRENDING_UP": reward},
        behavior_context_performance={"DISCIPLINED": reward},
        last_updated="2026-05-20T00:00:00+00:00",
    )


def _memory() -> AdaptivePolicyMemory:
    return AdaptivePolicyMemory(
        entries={
            "BALANCED": _entry("BALANCED", reward=30, confidence=85),
            "AGGRESSIVE": _entry(
                "AGGRESSIVE",
                reward=-20,
                confidence=25,
                dangerous=0.5,
                recommendation=PolicyMemoryRecommendation.DISABLE_POLICY,
            ),
        },
        disabled_policies=("AGGRESSIVE",),
    )


def _context(decision: TradeContextDecision = TradeContextDecision.TRADE_ALLOWED, score: int = 82) -> ContextScoringResult:
    return ContextScoringResult(
        global_score=score,
        decision=decision,
        breakdown=ContextScoreBreakdown(
            market_score=score,
            behavior_score=score,
            discipline_score=score,
            memory_score=score,
            emotional_score=score,
            volatility_score=score,
            strategy_regime_compatibility_score=score,
        ),
        favorable_factors=(),
        risk_factors=(),
        recommendations=(),
        strategy_regime_notes=(),
    )


def _market(*, dangerous: bool = False, regime: MarketRegime = MarketRegime.TRENDING_UP) -> MarketRegimeAnalysis:
    return MarketRegimeAnalysis(
        primary_regime=MarketRegime.NEWS_RISK if dangerous else regime,
        confidence=80,
        strength=RegimeStrength.STRONG,
        volatility=VolatilityRegime.EXTREME if dangerous else VolatilityRegime.NORMAL,
        session_condition=SessionCondition.DANGEROUS if dangerous else SessionCondition.FAVORABLE,
        context_quality_score=20 if dangerous else 85,
        favorable_for_pullback_strategy=not dangerous,
        dangerous_market=dangerous,
        detected_regimes=(MarketRegime.NEWS_RISK if dangerous else regime,),
        warnings=(),
        recommendations=(),
    )


def _behavior(*, high_risk: bool = False) -> BehaviorAnalysisResult:
    classes = (SessionBehaviorClass.HIGH_RISK,) if high_risk else (SessionBehaviorClass.DISCIPLINED,)
    return BehaviorAnalysisResult(
        classifications=classes,
        patterns=(),
        scores=BehaviorScores(
            discipline_score=80,
            emotional_risk_score=80 if high_risk else 25,
            consistency_score=80,
            risk_escalation_score=80 if high_risk else 20,
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


def _strategy(direction: TradeDirection = TradeDirection.BOTH) -> StrategyDNA:
    return StrategyDNA(name="EMA20", description="offline", allowed_direction=direction)


def _safe(status: SafeRLStatus = SafeRLStatus.SAFE) -> SafeRLExperimentResult:
    return SafeRLExperimentResult(
        status=status,
        validations=(),
        active_guardrails=(),
        risks_detected=("safe rl blocked",) if status == SafeRLStatus.BLOCKED else (),
        allowed_experiments=("offline",) if status == SafeRLStatus.SAFE else (),
        blocked_experiments=("blocked",) if status == SafeRLStatus.BLOCKED else (),
        recommendations=(),
        safety_summary="test",
    )


def _semi(decision: SemiAutoDecision) -> SemiAutoDecisionResult:
    return SemiAutoDecisionResult(
        decision=decision,
        action=SemiAutoAction.RECOMMEND_STOP_SESSION if decision == SemiAutoDecision.STOP_SESSION else SemiAutoAction.NO_ACTION,
        context_score=80,
        approval_reasons=(),
        blocking_reasons=(),
        detected_risks=(),
        manual_confirmation_conditions=(),
        trader_message="test",
    )


def test_select_meta_strategy_uses_adaptive_policy_memory() -> None:
    result = select_meta_strategy(
        adaptive_policy_memory=_memory(),
        safe_rl_result=_safe(),
        context_score=_context(),
        market_regime=_market(),
        behavior_result=_behavior(),
        strategy_dna=_strategy(),
    )

    assert result.decision == MetaStrategyDecision.SELECT_POLICY
    assert result.selected_policy_name == "BALANCED"
    assert result.confidence_score > 60
    assert MetaStrategyReason.MEMORY_MATCH in result.reasons
    assert result.required_manual_review is False


def test_select_meta_strategy_blocks_all_on_no_trade_dangerous_or_stop_session() -> None:
    no_trade = select_meta_strategy(
        adaptive_policy_memory=_memory(),
        context_score=_context(TradeContextDecision.NO_TRADE),
        market_regime=_market(),
    )
    dangerous = select_meta_strategy(
        adaptive_policy_memory=_memory(),
        context_score=_context(),
        market_regime=_market(dangerous=True),
    )
    stop = select_meta_strategy(
        adaptive_policy_memory=_memory(),
        context_score=_context(),
        market_regime=_market(),
        semi_auto_decision=_semi(SemiAutoDecision.STOP_SESSION),
    )

    assert no_trade.decision == MetaStrategyDecision.BLOCK_ALL_POLICIES
    assert dangerous.decision == MetaStrategyDecision.BLOCK_ALL_POLICIES
    assert stop.decision == MetaStrategyDecision.BLOCK_ALL_POLICIES


def test_select_meta_strategy_requires_review_when_safe_rl_blocked() -> None:
    result = select_meta_strategy(
        adaptive_policy_memory=_memory(),
        safe_rl_result=_safe(SafeRLStatus.BLOCKED),
        context_score=_context(),
        market_regime=_market(),
        behavior_result=_behavior(),
    )

    assert result.decision == MetaStrategyDecision.REQUIRE_REVIEW
    assert result.required_manual_review is True
    assert MetaStrategyReason.SAFE_RL_BLOCKED in result.reasons


def test_select_meta_strategy_reduced_risk_when_behavior_high_risk() -> None:
    result = select_meta_strategy(
        adaptive_policy_memory=_memory(),
        safe_rl_result=_safe(),
        context_score=_context(),
        market_regime=_market(),
        behavior_result=_behavior(high_risk=True),
    )

    assert result.decision == MetaStrategyDecision.SELECT_REDUCED_RISK_POLICY
    assert result.selected_policy_name == "BALANCED"
    assert result.required_manual_review is True


def test_select_meta_strategy_fallback_conservative_when_no_candidates_and_uncertain_context() -> None:
    result = select_meta_strategy(context_score=_context(score=50), safe_rl_result=_safe())

    assert result.decision == MetaStrategyDecision.FALLBACK_TO_CONSERVATIVE
    assert result.selected_policy_name == "CONSERVATIVE"
    assert result.required_manual_review is True


def test_select_meta_strategy_can_use_policy_results_without_memory() -> None:
    policy_result = PolicyEvaluationResult(
        policy=TradingPolicy.CONSERVATIVE,
        rule=PolicyRule(
            policy=TradingPolicy.CONSERVATIVE,
            min_context_score=70,
            reduce_risk_below_score=80,
            block_high_risk_context=True,
            allow_high_risk_override=False,
            reduce_size_on_caution=True,
            block_revenge_trading=True,
            block_overtrading=True,
        ),
        total_reward=100,
        normalized_reward=78,
        accepted_trades=2,
        blocked_trades=1,
        reduced_risk_trades=0,
        dangerous_decisions=0,
        average_context_score=80,
        average_reward=20,
        best_policy=False,
        best_policy_reason="test",
        scenario_count=3,
        semi_auto_decisions=(),
        paper_execution_results=(),
        reward_results=(),
        risk_notes=(),
    )

    result = select_meta_strategy(
        policy_results=(policy_result,),
        context_score=_context(),
        market_regime=_market(),
        behavior_result=_behavior(),
    )

    assert result.selected_policy_name == "CONSERVATIVE"
    assert result.decision == MetaStrategyDecision.SELECT_POLICY


def test_rank_strategy_candidates_orders_disabled_last() -> None:
    ranked = rank_strategy_candidates(
        (
            MetaStrategyCandidate("bad", score=100, confidence_score=100, average_reward=50, dangerous_decision_rate=0.5, compatible_with_strategy=True, disabled=True),
            MetaStrategyCandidate("good", score=70, confidence_score=70, average_reward=20, dangerous_decision_rate=0.0, compatible_with_strategy=True),
        )
    )

    assert ranked[0].policy_name == "good"
    assert ranked[-1].policy_name == "bad"


def test_render_meta_strategy_markdown_contains_required_sections() -> None:
    result = select_meta_strategy(
        MetaStrategySelectionInput(
            adaptive_policy_memory=_memory(),
            safe_rl_result=_safe(),
            context_score=_context(),
            market_regime=_market(),
            behavior_result=_behavior(),
            strategy_dna=_strategy(),
        )
    )

    markdown = render_meta_strategy_markdown(result)

    assert "# Meta Strategy Selector" in markdown
    assert "## Decision meta-strategie" in markdown
    assert "## Politique selectionnee" in markdown
    assert "## Classement des politiques" in markdown
    assert "## Raisons" in markdown
    assert "## Risques detectes" in markdown
    assert "## Fallback/Review" in markdown
    assert "## Recommandation AGIcore" in markdown
    assert "no broker" in markdown
