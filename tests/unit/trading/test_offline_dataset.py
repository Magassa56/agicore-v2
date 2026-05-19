"""Unit tests for offline learning dataset builder."""
from __future__ import annotations

from pathlib import Path

from agicore.trading.adaptive_memory_models import TraderMemoryProfile
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
from agicore.trading.offline_dataset import (
    build_learning_transition,
    build_offline_learning_dataset,
    evaluate_dataset_quality,
    load_offline_learning_dataset,
    render_offline_dataset_markdown,
    save_offline_learning_dataset,
)
from agicore.trading.offline_dataset_models import LearningAction, LearningState
from agicore.trading.paper_execution_loop import run_paper_execution_loop
from agicore.trading.paper_execution_models import PaperExecutionRequest
from agicore.trading.paper_trading_adapter import MockPaperTradingAdapter
from agicore.trading.paper_trading_models import PaperOrderRequest, PaperOrderSide
from agicore.trading.reward_function import evaluate_trading_reward
from agicore.trading.reward_models import RewardLabel
from agicore.trading.semi_auto_decision_models import (
    SemiAutoAction,
    SemiAutoDecision,
    SemiAutoDecisionResult,
)
from agicore.trading.strategy_dna_models import StrategyDNA, TradeDirection


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
        favorable_factors=("trend",),
        risk_factors=(),
        recommendations=("offline",),
        strategy_regime_notes=("compatible",),
    )


def _market(*, dangerous: bool = False) -> MarketRegimeAnalysis:
    return MarketRegimeAnalysis(
        primary_regime=MarketRegime.NEWS_RISK if dangerous else MarketRegime.TRENDING_UP,
        confidence=80,
        strength=RegimeStrength.STRONG,
        volatility=VolatilityRegime.EXTREME if dangerous else VolatilityRegime.NORMAL,
        session_condition=SessionCondition.DANGEROUS if dangerous else SessionCondition.FAVORABLE,
        context_quality_score=20 if dangerous else 85,
        favorable_for_pullback_strategy=not dangerous,
        dangerous_market=dangerous,
        detected_regimes=(MarketRegime.NEWS_RISK if dangerous else MarketRegime.TRENDING_UP,),
        warnings=(),
        recommendations=(),
    )


def _behavior(*, revenge: bool = False) -> BehaviorAnalysisResult:
    classes = [SessionBehaviorClass.DISCIPLINED]
    if revenge:
        classes.extend([SessionBehaviorClass.REVENGE_TRADING_PROBABLE, SessionBehaviorClass.HIGH_RISK])
    score = 35 if revenge else 88
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


def _strategy() -> StrategyDNA:
    return StrategyDNA(
        name="EMA20_Pullback_Pro",
        description="offline",
        allowed_direction=TradeDirection.BOTH,
    )


def _semi(decision: SemiAutoDecision = SemiAutoDecision.APPROVE_TRADE) -> SemiAutoDecisionResult:
    return SemiAutoDecisionResult(
        decision=decision,
        action=SemiAutoAction.PREPARE_ORDER_PREVIEW if decision == SemiAutoDecision.APPROVE_TRADE else SemiAutoAction.BLOCK_TRADE,
        context_score=82,
        approval_reasons=("ok",) if decision == SemiAutoDecision.APPROVE_TRADE else (),
        blocking_reasons=("blocked",) if decision == SemiAutoDecision.BLOCK_TRADE else (),
        detected_risks=(),
        manual_confirmation_conditions=(),
        trader_message="offline",
    )


def _paper_and_reward(
    context: ContextScoringResult,
    semi: SemiAutoDecisionResult,
    market: MarketRegimeAnalysis,
    behavior: BehaviorAnalysisResult,
) -> tuple[object, object]:
    paper = run_paper_execution_loop(
        PaperExecutionRequest(
            semi_auto_decision=semi,
            context_score=context,
            order_request=PaperOrderRequest(
                symbol="NQ",
                side=PaperOrderSide.BUY,
                quantity=1.0,
                simulated_price=100.0,
            ),
            strategy_dna=_strategy(),
        ),
        adapter=MockPaperTradingAdapter(),
    )
    reward = evaluate_trading_reward(
        paper_execution_result=paper,
        semi_auto_decision=semi,
        context_score=context,
        behavior_result=behavior,
        market_regime=market,
        strategy_dna=_strategy(),
    )
    return paper, reward


def test_build_learning_transition_extracts_state_action_reward() -> None:
    context = _context()
    market = _market()
    behavior = _behavior()
    semi = _semi()
    paper, reward = _paper_and_reward(context, semi, market, behavior)

    transition = build_learning_transition(
        context_score=context,
        market_regime=market,
        behavior_result=behavior,
        memory_profile=TraderMemoryProfile(worst_contexts=("late news",)),
        strategy_dna=_strategy(),
        hour_of_day=10,
        session_trade_count=2,
        policy_name="BALANCED",
        semi_auto_decision=semi,
        paper_execution_result=paper,
        reward_result=reward,
        next_context_score=_context(score=86),
        next_market_regime=market,
        next_behavior_result=behavior,
        next_strategy_dna=_strategy(),
        next_hour_of_day=11,
        next_session_trade_count=3,
        source_id="s1",
    )

    assert transition.state.context_score == 82
    assert transition.state.market_regime == "TRENDING_UP"
    assert transition.state.volatility_regime == "NORMAL"
    assert transition.state.behavior_classification == ("DISCIPLINED",)
    assert "worst_context:late news" in transition.state.memory_risk_flags
    assert transition.action.policy_name == "BALANCED"
    assert transition.action.approved is True
    assert transition.reward is not None
    assert transition.reward.reward_label in {label.value for label in RewardLabel}
    assert transition.reward.pnl_reward is not None
    assert transition.next_state is not None
    assert transition.next_state.session_trade_count == 3


def test_evaluate_dataset_quality_counts_missing_and_dangerous_transitions() -> None:
    safe_context = _context(score=82)
    safe_market = _market()
    safe_behavior = _behavior()
    safe_semi = _semi()
    safe_paper, safe_reward = _paper_and_reward(safe_context, safe_semi, safe_market, safe_behavior)
    safe = build_learning_transition(
        context_score=safe_context,
        market_regime=safe_market,
        behavior_result=safe_behavior,
        strategy_dna=_strategy(),
        policy_name="BALANCED",
        semi_auto_decision=safe_semi,
        paper_execution_result=safe_paper,
        reward_result=safe_reward,
        next_state=LearningState(context_score=85),
    )
    dangerous = build_learning_transition(
        state=LearningState(
            context_score=20,
            market_regime="NEWS_RISK",
            behavior_classification=("REVENGE_TRADING_PROBABLE",),
        ),
        action=LearningAction(policy_name="AGGRESSIVE", semi_auto_decision="APPROVE_TRADE", approved=True),
        reward=None,
        next_state=None,
    )
    dataset = build_offline_learning_dataset((safe, dangerous), name="test")

    report = evaluate_dataset_quality(dataset)

    assert report.transitions_count == 2
    assert report.unique_states_count == 2
    assert report.unique_actions_count == 2
    assert report.dangerous_decision_count == 1
    assert report.missing_reward_count == 1
    assert report.missing_next_state_count == 1
    assert report.quality_score < 100


def test_save_and_load_offline_learning_dataset_roundtrip(tmp_path: Path) -> None:
    transition = build_learning_transition(
        state=LearningState(context_score=70, strategy_name="EMA20"),
        action=LearningAction(policy_name="CONSERVATIVE", blocked=True, semi_auto_decision="BLOCK_TRADE"),
        next_state=LearningState(context_score=72),
        source_id="roundtrip",
    )
    dataset = build_offline_learning_dataset((transition,), name="roundtrip")
    path = tmp_path / "offline_dataset.json"

    save_offline_learning_dataset(path, dataset)
    loaded = load_offline_learning_dataset(path)

    assert loaded == dataset


def test_render_offline_dataset_markdown_contains_required_sections() -> None:
    dataset = build_offline_learning_dataset(
        (
            build_learning_transition(
                state=LearningState(context_score=75),
                action=LearningAction(policy_name="NO_TRADE_ON_HIGH_RISK", blocked=True),
                next_state=LearningState(context_score=76),
            ),
        )
    )

    markdown = render_offline_dataset_markdown(dataset)

    assert "# Offline Learning Dataset" in markdown
    assert "## Resume dataset" in markdown
    assert "## Qualite dataset" in markdown
    assert "## Couverture transitions" in markdown
    assert "## Avertissements" in markdown
    assert "## Utilisation future pour Offline RL" in markdown
    assert "No model training" in markdown
