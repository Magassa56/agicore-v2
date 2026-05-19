"""Unit tests for offline trading reward function."""
from __future__ import annotations

from datetime import datetime

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
from agicore.trading.paper_execution_models import (
    PaperExecutionDecision,
    PaperExecutionEvent,
    PaperExecutionEventType,
    PaperExecutionResult,
)
from agicore.trading.paper_trading_models import (
    PaperAccountState,
    PaperOrderRequest,
    PaperOrderResult,
    PaperOrderSide,
    PaperOrderStatus,
    PaperPosition,
)
from agicore.trading.reward_function import (
    evaluate_trading_reward,
    render_reward_evaluation_markdown,
)
from agicore.trading.reward_models import RewardEvaluationInput, RewardLabel
from agicore.trading.semi_auto_decision_models import (
    SemiAutoAction,
    SemiAutoDecision,
    SemiAutoDecisionResult,
)
from agicore.trading.session_replay_models import (
    ReplayViolation,
    ReplayViolationType,
    SessionReplayResult,
    SessionReplaySummary,
)
from agicore.trading.strategy_dna_models import StrategyDNA, TradeDirection
from agicore.trading.trade_journal_models import JournalAnalysisResult


def _context(decision: TradeContextDecision, score: int = 85) -> ContextScoringResult:
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
        favorable_factors=("clean context",),
        risk_factors=(),
        recommendations=("continue",),
        strategy_regime_notes=("compatible",),
    )


def _market(*, dangerous: bool = False, favorable: bool = True) -> MarketRegimeAnalysis:
    return MarketRegimeAnalysis(
        primary_regime=MarketRegime.TRENDING_UP if favorable else MarketRegime.NEWS_RISK,
        confidence=85,
        strength=RegimeStrength.STRONG,
        volatility=VolatilityRegime.NORMAL if favorable else VolatilityRegime.EXTREME,
        session_condition=SessionCondition.FAVORABLE if favorable else SessionCondition.DANGEROUS,
        context_quality_score=85 if favorable else 20,
        favorable_for_pullback_strategy=favorable,
        dangerous_market=dangerous,
        detected_regimes=(MarketRegime.TRENDING_UP if favorable else MarketRegime.NEWS_RISK,),
        warnings=(),
        recommendations=(),
    )


def _behavior(
    *,
    disciplined: bool = True,
    overtrading: bool = False,
    revenge: bool = False,
) -> BehaviorAnalysisResult:
    classes = []
    if disciplined:
        classes.extend([SessionBehaviorClass.DISCIPLINED, SessionBehaviorClass.CONSISTENT])
    if overtrading:
        classes.append(SessionBehaviorClass.OVERTRADING)
    if revenge:
        classes.append(SessionBehaviorClass.REVENGE_TRADING_PROBABLE)
    if overtrading or revenge:
        classes.append(SessionBehaviorClass.HIGH_RISK)
    score = 90 if disciplined and not (overtrading or revenge) else 35
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


def _replay(*, discipline: int = 95, violation: bool = False, largest_loss: float = 0.0) -> SessionReplayResult:
    violations = (
        ReplayViolation(
            kind=ReplayViolationType.DAILY_LOSS_EXCEEDED,
            message="loss limit",
            timestamp=datetime(2026, 5, 19, 10, 0),
        ),
    ) if violation else ()
    summary = SessionReplaySummary(
        session_day=datetime(2026, 5, 19).date(),
        total_pnl=100.0,
        trade_count=1,
        win_rate=1.0,
        largest_loss=largest_loss,
        largest_gain=100.0,
        max_loss_streak=1 if largest_loss < 0 else 0,
        start_time=datetime(2026, 5, 19, 10, 0),
        end_time=datetime(2026, 5, 19, 10, 1),
        discipline_score=discipline,
        violations=violations,
    )
    return SessionReplayResult(sessions=(summary,), events=(), discipline_score=discipline)


def _semi(decision: SemiAutoDecision) -> SemiAutoDecisionResult:
    return SemiAutoDecisionResult(
        decision=decision,
        action=SemiAutoAction.PREPARE_ORDER_PREVIEW,
        context_score=85,
        approval_reasons=(),
        blocking_reasons=(),
        detected_risks=(),
        manual_confirmation_conditions=(),
        trader_message="test",
    )


def _paper(*, filled: bool = True, realized_pnl: float = 100.0, quantity: float = 1.0) -> PaperExecutionResult:
    request = PaperOrderRequest(
        symbol="NQ",
        side=PaperOrderSide.BUY,
        quantity=quantity,
        simulated_price=100.0,
    )
    order_result = PaperOrderResult(
        order_id="paper-1",
        request=request,
        status=PaperOrderStatus.FILLED if filled else PaperOrderStatus.REJECTED,
        accepted=filled,
        reason="filled" if filled else "rejected",
        filled_quantity=quantity if filled else 0.0,
        fill_price=100.0 if filled else None,
        position=PaperPosition(
            symbol="NQ",
            quantity=0.0,
            average_price=0.0,
            realized_pnl=realized_pnl,
        ) if filled else None,
        account_state=PaperAccountState(
            cash=100_000.0,
            equity=100_000.0,
            realized_pnl=realized_pnl if filled else 0.0,
            open_positions=0,
            trading_enabled=True,
        ),
    )
    return PaperExecutionResult(
        decision=PaperExecutionDecision.PAPER_ORDER_FILLED if filled else PaperExecutionDecision.PRECHECK_REJECTED,
        accepted=filled,
        precheck_passed=filled,
        precheck_reasons=("ok",),
        order_result=order_result if filled else None,
        events=(
            PaperExecutionEvent(
                event_type=PaperExecutionEventType.LOOP_COMPLETED,
                message="done",
                timestamp=datetime(2026, 5, 19, 10, 0),
            ),
        ),
        safety_message="offline",
    )


def test_evaluate_trading_reward_labels_excellent_controlled_winner() -> None:
    result = evaluate_trading_reward(
        RewardEvaluationInput(
            paper_execution_result=_paper(realized_pnl=120.0),
            semi_auto_decision=_semi(SemiAutoDecision.APPROVE_TRADE),
            context_score=_context(TradeContextDecision.STRONG_TRADE_ALLOWED, 90),
            session_replay_result=_replay(),
            behavior_result=_behavior(),
            memory_profile=TraderMemoryProfile(
                sessions_count=10,
                average_discipline_score=78.0,
                average_emotional_risk_score=76.0,
                average_consistency_score=80.0,
                favorable_contexts=("EMA20 trend day",),
            ),
            market_regime=_market(),
            strategy_dna=StrategyDNA(
                name="EMA20_Pullback_Pro",
                description="offline",
                allowed_direction=TradeDirection.BOTH,
            ),
            journal_result=JournalAnalysisResult(
                total_trades=1,
                total_sessions=1,
                dominant_emotions=(("CALM", 1),),
                recurring_mistakes=(),
                most_noted_setups=(("EMA20", 1),),
                frequent_tags=(),
                playbook_compliance_rate=1.0,
                risk_rules_compliance_rate=1.0,
                missing_screenshot_trade_ids=(),
                keyword_flags=(),
                trades_to_review=(),
                improvement_plan=(),
            ),
        )
    )

    assert result.reward_label == RewardLabel.EXCELLENT_DECISION
    assert result.normalized_reward >= 85
    assert result.breakdown.pnl_reward.value > 0
    assert result.breakdown.strategy_compliance_reward.value > 0
    assert any("Positive simulated PnL" in note for note in result.learning_notes)


def test_evaluate_trading_reward_penalizes_dangerous_execution() -> None:
    result = evaluate_trading_reward(
        paper_execution_result=_paper(realized_pnl=-120.0, quantity=3.0),
        semi_auto_decision=_semi(SemiAutoDecision.APPROVE_TRADE),
        context_score=_context(TradeContextDecision.NO_TRADE, 20),
        session_replay_result=_replay(discipline=35, violation=True, largest_loss=-400.0),
        behavior_result=_behavior(disciplined=False, overtrading=True, revenge=True),
        memory_profile=TraderMemoryProfile(
            sessions_count=5,
            average_discipline_score=60.0,
            average_emotional_risk_score=60.0,
            average_consistency_score=55.0,
            recurring_patterns=(),
        ),
        market_regime=_market(dangerous=True, favorable=False),
        strategy_dna=StrategyDNA(
            name="EMA20_Pullback_Pro",
            description="offline",
            allowed_direction=TradeDirection.BOTH,
        ),
    )

    assert result.reward_label == RewardLabel.DANGEROUS_DECISION
    assert result.normalized_reward < 30
    assert result.breakdown.revenge_trading_penalty.value < 0
    assert result.breakdown.overtrading_penalty.value < 0
    assert result.breakdown.rule_violation_penalty.value < 0
    assert any("NO_TRADE" in action for action in result.improvement_actions)


def test_evaluate_trading_reward_rewards_correct_block_in_dangerous_context() -> None:
    result = evaluate_trading_reward(
        paper_execution_result=_paper(filled=False),
        semi_auto_decision=_semi(SemiAutoDecision.BLOCK_TRADE),
        context_score=_context(TradeContextDecision.NO_TRADE, 25),
        market_regime=_market(dangerous=True, favorable=False),
        behavior_result=_behavior(disciplined=False),
    )

    assert result.breakdown.risk_adjusted_reward.value > 0
    assert result.breakdown.context_alignment_reward.value > -20
    assert any("avoided execution" in note.lower() for note in result.learning_notes)


def test_render_reward_evaluation_markdown_contains_required_sections() -> None:
    result = evaluate_trading_reward(
        paper_execution_result=_paper(realized_pnl=50.0),
        semi_auto_decision=_semi(SemiAutoDecision.APPROVE_TRADE),
        context_score=_context(TradeContextDecision.TRADE_ALLOWED, 75),
        market_regime=_market(),
        behavior_result=_behavior(),
    )

    markdown = render_reward_evaluation_markdown(result)

    assert "# Trading Reward Evaluation" in markdown
    assert "## Reward total" in markdown
    assert "## Label" in markdown
    assert "## Detail composants" in markdown
    assert "## Penalites" in markdown
    assert "## Ce qui a ete bien fait" in markdown
    assert "## Ce qui doit etre ameliore" in markdown
    assert "## Utilisation future pour RL offline" in markdown
