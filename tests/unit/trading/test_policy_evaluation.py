"""Unit tests for offline policy evaluation sandbox."""
from __future__ import annotations

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
from agicore.trading.paper_execution_models import PaperExecutionDecision
from agicore.trading.paper_trading_models import PaperOrderRequest, PaperOrderSide
from agicore.trading.policy_evaluation import (
    compare_policies,
    evaluate_policy,
    render_policy_comparison_markdown,
)
from agicore.trading.policy_evaluation_models import PolicyEvaluationScenario, TradingPolicy
from agicore.trading.semi_auto_decision_models import SemiAutoDecision
from agicore.trading.strategy_dna_models import StrategyDNA, TradeDirection


def _context(decision: TradeContextDecision, score: int) -> ContextScoringResult:
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
        favorable_factors=("trend aligned",) if score >= 70 else (),
        risk_factors=("risk",) if score < 70 else (),
        recommendations=("offline only",),
        strategy_regime_notes=("compatible",),
    )


def _market(*, dangerous: bool = False, favorable: bool = True) -> MarketRegimeAnalysis:
    return MarketRegimeAnalysis(
        primary_regime=MarketRegime.TRENDING_UP if favorable else MarketRegime.NEWS_RISK,
        confidence=85,
        strength=RegimeStrength.STRONG if favorable else RegimeStrength.EXTREME,
        volatility=VolatilityRegime.NORMAL if favorable else VolatilityRegime.EXTREME,
        session_condition=SessionCondition.FAVORABLE if favorable else SessionCondition.DANGEROUS,
        context_quality_score=85 if favorable else 20,
        favorable_for_pullback_strategy=favorable,
        dangerous_market=dangerous,
        detected_regimes=(MarketRegime.TRENDING_UP if favorable else MarketRegime.NEWS_RISK,),
        warnings=(),
        recommendations=(),
    )


def _behavior(*, overtrading: bool = False, revenge: bool = False) -> BehaviorAnalysisResult:
    classes = [SessionBehaviorClass.DISCIPLINED, SessionBehaviorClass.CONSISTENT]
    if overtrading:
        classes.append(SessionBehaviorClass.OVERTRADING)
    if revenge:
        classes.append(SessionBehaviorClass.REVENGE_TRADING_PROBABLE)
    if overtrading or revenge:
        classes.append(SessionBehaviorClass.HIGH_RISK)
    score = 35 if overtrading or revenge else 90
    return BehaviorAnalysisResult(
        classifications=tuple(classes),
        patterns=(),
        scores=BehaviorScores(
            discipline_score=score,
            emotional_risk_score=score,
            consistency_score=score,
            risk_escalation_score=score,
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


def _order(side: PaperOrderSide = PaperOrderSide.BUY, quantity: float = 2.0) -> PaperOrderRequest:
    return PaperOrderRequest(
        symbol="NQ",
        side=side,
        quantity=quantity,
        simulated_price=100.0,
    )


def _strategy(direction: TradeDirection = TradeDirection.BOTH) -> StrategyDNA:
    return StrategyDNA(
        name="EMA20_Pullback_Pro",
        description="offline",
        allowed_direction=direction,
    )


def _scenario(
    name: str,
    *,
    decision: TradeContextDecision = TradeContextDecision.TRADE_ALLOWED,
    score: int = 85,
    side: PaperOrderSide = PaperOrderSide.BUY,
    dangerous: bool = False,
    favorable: bool = True,
    overtrading: bool = False,
    revenge: bool = False,
    strategy_direction: TradeDirection = TradeDirection.BOTH,
) -> PolicyEvaluationScenario:
    return PolicyEvaluationScenario(
        name=name,
        context_score=_context(decision, score),
        order_request=_order(side),
        market_regime=_market(dangerous=dangerous, favorable=favorable),
        behavior_result=_behavior(overtrading=overtrading, revenge=revenge),
        strategy_dna=_strategy(strategy_direction),
    )


def test_evaluate_policy_accepts_clean_balanced_scenario() -> None:
    result = evaluate_policy(
        TradingPolicy.BALANCED,
        (_scenario("clean", score=85),),
    )

    assert result.policy == TradingPolicy.BALANCED
    assert result.accepted_trades == 1
    assert result.blocked_trades == 0
    assert result.dangerous_decisions == 0
    assert result.normalized_reward >= 60
    assert result.paper_execution_results[0].decision == PaperExecutionDecision.PAPER_ORDER_FILLED


def test_conservative_policy_blocks_revenge_and_overtrading() -> None:
    result = evaluate_policy(
        TradingPolicy.CONSERVATIVE,
        (
            _scenario(
                "revenge",
                decision=TradeContextDecision.HIGH_RISK_CONTEXT,
                score=55,
                dangerous=True,
                favorable=False,
                overtrading=True,
                revenge=True,
            ),
        ),
    )

    assert result.accepted_trades == 0
    assert result.blocked_trades == 1
    assert result.semi_auto_decisions[0].decision == SemiAutoDecision.BLOCK_TRADE
    assert any("revenge" in note.lower() for note in result.risk_notes)


def test_aggressive_policy_can_reduce_risk_and_override_high_risk_context() -> None:
    result = evaluate_policy(
        TradingPolicy.AGGRESSIVE,
        (
            _scenario(
                "high-risk",
                decision=TradeContextDecision.HIGH_RISK_CONTEXT,
                score=58,
                dangerous=True,
                favorable=False,
                overtrading=True,
            ),
        ),
    )

    assert result.accepted_trades == 1
    assert result.reduced_risk_trades == 1
    assert result.dangerous_decisions >= 1
    assert result.paper_execution_results[0].order_result is not None
    assert result.paper_execution_results[0].order_result.request.quantity == 1.0


def test_long_only_strict_blocks_sell_side() -> None:
    result = evaluate_policy(
        TradingPolicy.LONG_ONLY_STRICT,
        (_scenario("short", side=PaperOrderSide.SELL, strategy_direction=TradeDirection.BOTH),),
    )

    assert result.accepted_trades == 0
    assert result.blocked_trades == 1
    assert any("direction" in reason.lower() for reason in result.semi_auto_decisions[0].blocking_reasons)


def test_compare_policies_marks_best_and_renders_required_markdown_sections() -> None:
    comparison = compare_policies(
        (
            _scenario("clean", score=88),
            _scenario(
                "high-risk",
                decision=TradeContextDecision.HIGH_RISK_CONTEXT,
                score=55,
                dangerous=True,
                favorable=False,
                overtrading=True,
            ),
        ),
        policies=(TradingPolicy.CONSERVATIVE, TradingPolicy.BALANCED, TradingPolicy.AGGRESSIVE),
    )
    markdown = render_policy_comparison_markdown(comparison)

    assert comparison.best_policy is not None
    assert sum(1 for result in comparison.results if result.best_policy) == 1
    assert "## Resume des politiques" in markdown
    assert "## Meilleure politique" in markdown
    assert "## Tableau comparatif" in markdown
    assert "## Risques detectes" in markdown
    assert "## Recommandation AGIcore" in markdown
    assert "## Utilisation future pour Offline RL" in markdown
    assert "No real" in markdown
