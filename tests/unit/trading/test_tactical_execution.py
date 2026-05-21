"""Unit tests for offline Tactical Execution Intelligence."""
from __future__ import annotations

from datetime import date

from agicore.trading.context_scoring_models import ContextScoreBreakdown, ContextScoringResult, TradeContextDecision
from agicore.trading.market_regime_models import (
    MarketRegime,
    MarketRegimeAnalysis,
    RegimeStrength,
    SessionCondition,
    VolatilityRegime,
)
from agicore.trading.reward_models import RewardBreakdown, RewardComponent, RewardEvaluationResult, RewardLabel
from agicore.trading.semi_auto_decision_models import SemiAutoAction, SemiAutoDecision, SemiAutoDecisionResult
from agicore.trading.tactical_execution import (
    detect_tactical_risks,
    evaluate_tactical_execution,
    render_tactical_execution_markdown,
    score_entry_quality,
    score_exit_quality,
)
from agicore.trading.tactical_execution_models import TacticalExecutionQuality, TacticalExecutionSignal
from agicore.trading.trade_journal_models import JournalMistakeType, TradeJournalEntry


def _context(decision: TradeContextDecision = TradeContextDecision.TRADE_ALLOWED, score: int = 75) -> ContextScoringResult:
    return ContextScoringResult(
        global_score=score,
        decision=decision,
        breakdown=ContextScoreBreakdown(score, score, score, score, score, score, score),
        favorable_factors=(),
        risk_factors=(),
        recommendations=(),
        strategy_regime_notes=("strategy aligned",),
    )


def _market(
    volatility: VolatilityRegime = VolatilityRegime.NORMAL,
    dangerous: bool = False,
    quality: int = 75,
) -> MarketRegimeAnalysis:
    return MarketRegimeAnalysis(
        primary_regime=MarketRegime.TRENDING_UP,
        confidence=80,
        strength=RegimeStrength.STRONG,
        volatility=volatility,
        session_condition=SessionCondition.DANGEROUS if dangerous else SessionCondition.FAVORABLE,
        context_quality_score=quality,
        favorable_for_pullback_strategy=not dangerous,
        dangerous_market=dangerous,
        detected_regimes=(MarketRegime.TRENDING_UP,),
        warnings=(),
        recommendations=(),
    )


def _semi(decision: SemiAutoDecision = SemiAutoDecision.APPROVE_TRADE, risks: tuple[str, ...] = ()) -> SemiAutoDecisionResult:
    return SemiAutoDecisionResult(
        decision=decision,
        action=SemiAutoAction.PREPARE_ORDER_PREVIEW,
        context_score=80,
        approval_reasons=("ok",),
        blocking_reasons=(),
        detected_risks=risks,
        manual_confirmation_conditions=(),
        trader_message="message",
    )


def _reward(label: RewardLabel = RewardLabel.GOOD_DECISION, normalized: int = 75, total: int = 20) -> RewardEvaluationResult:
    component = RewardComponent("x", 0, "x")
    return RewardEvaluationResult(
        total_reward=total,
        normalized_reward=normalized,
        reward_label=label,
        breakdown=RewardBreakdown(component, component, component, component, component, component, component, component, component, component, component),
        learning_notes=(),
        improvement_actions=(),
    )


def _journal(
    mistakes: tuple[JournalMistakeType, ...] = (),
    playbook: bool = True,
    risk_rules: bool = True,
) -> TradeJournalEntry:
    return TradeJournalEntry(
        trade_id="t1",
        session_date=date(2026, 5, 21),
        instrument="ES",
        direction="LONG",
        setup_name="EMA20 Pullback",
        entry_reason="EMA20 Pullback plan",
        exit_reason="target hit by plan",
        mistake_types=mistakes,
        followed_playbook=playbook,
        followed_risk_rules=risk_rules,
    )


def test_score_entry_quality_rewards_strong_context_and_playbook() -> None:
    score = score_entry_quality(
        context_score=_context(TradeContextDecision.STRONG_TRADE_ALLOWED, 90),
        market_regime=_market(),
        semi_auto_decision=_semi(),
        trade_journal_entry=_journal(),
    )

    assert score >= 85


def test_score_entry_quality_penalizes_no_trade_and_journal_mistakes() -> None:
    score = score_entry_quality(
        context_score=_context(TradeContextDecision.NO_TRADE, 25),
        semi_auto_decision=_semi(),
        trade_journal_entry=_journal((JournalMistakeType.FOMO, JournalMistakeType.CHASED_PRICE), playbook=False, risk_rules=False),
    )

    assert score <= 20


def test_score_exit_quality_rewards_good_reward_and_planned_exit() -> None:
    score = score_exit_quality(
        reward_evaluation=_reward(RewardLabel.EXCELLENT_DECISION, 90, 45),
        trade_journal_entry=_journal(),
    )

    assert score >= 80


def test_score_exit_quality_penalizes_exit_mistakes_and_bad_reward() -> None:
    score = score_exit_quality(
        reward_evaluation=_reward(RewardLabel.BAD_DECISION, 25, -20),
        trade_journal_entry=_journal((JournalMistakeType.EARLY_EXIT, JournalMistakeType.MOVED_STOP)),
    )

    assert score < 45


def test_detect_tactical_risks_detects_fomo_and_chase() -> None:
    signals = detect_tactical_risks(
        context_score=_context(TradeContextDecision.HIGH_RISK_CONTEXT, 35),
        semi_auto_decision=_semi(SemiAutoDecision.APPROVE_TRADE),
        trade_journal_entry=_journal((JournalMistakeType.FOMO, JournalMistakeType.CHASED_PRICE)),
    )

    assert TacticalExecutionSignal.FOMO_RISK in signals
    assert TacticalExecutionSignal.CHASE_RISK in signals
    assert TacticalExecutionSignal.ENTRY_QUALITY_LOW in signals


def test_detect_tactical_risks_detects_hesitation() -> None:
    signals = detect_tactical_risks(
        context_score=_context(TradeContextDecision.STRONG_TRADE_ALLOWED, 88),
        semi_auto_decision=_semi(SemiAutoDecision.REQUIRE_CONFIRMATION),
    )

    assert TacticalExecutionSignal.HESITATION_RISK in signals


def test_detect_tactical_risks_detects_overconfidence() -> None:
    signals = detect_tactical_risks(
        context_score=_context(TradeContextDecision.HIGH_RISK_CONTEXT, 45),
        semi_auto_decision=_semi(SemiAutoDecision.APPROVE_TRADE),
        reward_evaluation=_reward(RewardLabel.BAD_DECISION, 30, -10),
    )

    assert TacticalExecutionSignal.OVERCONFIDENCE_RISK in signals


def test_evaluate_tactical_execution_blocks_when_trade_blocked() -> None:
    result = evaluate_tactical_execution(
        context_score=_context(TradeContextDecision.NO_TRADE, 20),
        semi_auto_decision=_semi(SemiAutoDecision.BLOCK_TRADE),
    )

    assert result.quality == TacticalExecutionQuality.BLOCKED
    assert result.events


def test_evaluate_tactical_execution_can_be_excellent() -> None:
    result = evaluate_tactical_execution(
        context_score=_context(TradeContextDecision.STRONG_TRADE_ALLOWED, 95),
        market_regime=_market(),
        semi_auto_decision=_semi(),
        reward_evaluation=_reward(RewardLabel.EXCELLENT_DECISION, 90, 50),
        trade_journal_entry=_journal(),
    )

    assert result.quality in {TacticalExecutionQuality.EXCELLENT, TacticalExecutionQuality.GOOD}
    assert result.global_score >= 72


def test_evaluate_tactical_execution_penalizes_dangerous_volatility() -> None:
    result = evaluate_tactical_execution(
        context_score=_context(TradeContextDecision.HIGH_RISK_CONTEXT, 35),
        market_regime=_market(VolatilityRegime.EXTREME, dangerous=True, quality=20),
        semi_auto_decision=_semi(SemiAutoDecision.APPROVE_TRADE),
        reward_evaluation=_reward(RewardLabel.DANGEROUS_DECISION, 20, -40),
    )

    assert result.quality in {TacticalExecutionQuality.DANGEROUS, TacticalExecutionQuality.WEAK}
    assert TacticalExecutionSignal.VOLATILITY_MISMATCH in result.signals


def test_render_tactical_execution_markdown_contains_required_sections() -> None:
    result = evaluate_tactical_execution(
        context_score=_context(),
        market_regime=_market(),
        semi_auto_decision=_semi(),
        reward_evaluation=_reward(),
        trade_journal_entry=_journal(),
    )

    markdown = render_tactical_execution_markdown(result)

    assert "# Tactical Execution Intelligence" in markdown
    assert "## Qualite tactique" in markdown
    assert "## Score global" in markdown
    assert "## Score entree" in markdown
    assert "## Score sortie" in markdown
    assert "## Timing" in markdown
    assert "## Volatilite" in markdown
    assert "## Risques tactiques" in markdown
    assert "## Alignement strategie" in markdown
    assert "## Recommandations AGIcore" in markdown
    assert "no broker" in markdown
