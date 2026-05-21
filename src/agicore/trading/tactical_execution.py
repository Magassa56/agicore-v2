"""Offline Tactical Execution Intelligence for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .context_scoring_models import TradeContextDecision
from .executive_brain_models import ExecutiveMode
from .market_regime_models import MarketRegime, SessionCondition, VolatilityRegime
from .paper_execution_models import PaperExecutionDecision
from .reward_models import RewardLabel
from .semi_auto_decision_models import SemiAutoDecision
from .strategic_planning_models import StrategicObjective
from .tactical_execution_models import (
    TacticalExecutionEvent,
    TacticalExecutionInput,
    TacticalExecutionQuality,
    TacticalExecutionResult,
    TacticalExecutionSignal,
    TacticalScoreBreakdown,
)
from .trade_journal_models import JournalMistakeType


def score_entry_quality(tactical_input: TacticalExecutionInput | None = None, **kwargs) -> int:
    """Score tactical entry quality from context, decision and journal evidence."""
    data = _input(tactical_input, **kwargs)
    score = 55
    if data.context_score is not None:
        score += int((data.context_score.global_score - 50) * 0.45)
        if data.context_score.decision == TradeContextDecision.NO_TRADE:
            score -= 45
        elif data.context_score.decision == TradeContextDecision.HIGH_RISK_CONTEXT:
            score -= 25
        elif data.context_score.decision == TradeContextDecision.STRONG_TRADE_ALLOWED:
            score += 12
    if data.market_regime is not None:
        if data.market_regime.dangerous_market:
            score -= 30
        elif data.market_regime.context_quality_score >= 75:
            score += 10
        if data.market_regime.favorable_for_pullback_strategy:
            score += 6
    if data.semi_auto_decision is not None:
        if data.semi_auto_decision.decision == SemiAutoDecision.APPROVE_TRADE:
            score += 8
        elif data.semi_auto_decision.decision == SemiAutoDecision.APPROVE_REDUCED_RISK:
            score += 2
        elif data.semi_auto_decision.decision in {SemiAutoDecision.BLOCK_TRADE, SemiAutoDecision.STOP_SESSION, SemiAutoDecision.REVIEW_ONLY}:
            score -= 15
    if data.trade_journal_entry is not None:
        if not data.trade_journal_entry.followed_playbook:
            score -= 25
        if not data.trade_journal_entry.followed_risk_rules:
            score -= 30
        if any(mistake in data.trade_journal_entry.mistake_types for mistake in (JournalMistakeType.FOMO, JournalMistakeType.LATE_ENTRY, JournalMistakeType.CHASED_PRICE)):
            score -= 25
    return _clamp(score)


def score_exit_quality(tactical_input: TacticalExecutionInput | None = None, **kwargs) -> int:
    """Score tactical exit quality from execution, reward and journal evidence."""
    data = _input(tactical_input, **kwargs)
    score = 55
    if data.paper_execution is not None:
        if data.paper_execution.decision == PaperExecutionDecision.PAPER_ORDER_FILLED and data.paper_execution.accepted:
            score += 10
        elif data.paper_execution.decision == PaperExecutionDecision.PRECHECK_REJECTED:
            score += 2
        else:
            score -= 12
    if data.reward_evaluation is not None:
        score += int((data.reward_evaluation.normalized_reward - 50) * 0.35)
        if data.reward_evaluation.reward_label == RewardLabel.DANGEROUS_DECISION:
            score -= 30
        elif data.reward_evaluation.reward_label == RewardLabel.BAD_DECISION:
            score -= 18
        elif data.reward_evaluation.reward_label in {RewardLabel.GOOD_DECISION, RewardLabel.EXCELLENT_DECISION}:
            score += 10
    if data.trade_journal_entry is not None:
        if any(mistake in data.trade_journal_entry.mistake_types for mistake in (JournalMistakeType.EARLY_EXIT, JournalMistakeType.LATE_EXIT, JournalMistakeType.MOVED_STOP)):
            score -= 20
        if "target" in data.trade_journal_entry.exit_reason.casefold() or "plan" in data.trade_journal_entry.exit_reason.casefold():
            score += 8
    return _clamp(score)


def detect_tactical_risks(tactical_input: TacticalExecutionInput | None = None, **kwargs) -> tuple[TacticalExecutionSignal, ...]:
    """Detect tactical execution risks and strengths with deterministic heuristics."""
    data = _input(tactical_input, **kwargs)
    signals: list[TacticalExecutionSignal] = []
    entry = score_entry_quality(data)
    exit_score = score_exit_quality(data)
    signals.append(TacticalExecutionSignal.ENTRY_QUALITY_HIGH if entry >= 70 else TacticalExecutionSignal.ENTRY_QUALITY_LOW)
    signals.append(TacticalExecutionSignal.EXIT_QUALITY_HIGH if exit_score >= 70 else TacticalExecutionSignal.EXIT_QUALITY_LOW)

    timing_score = _timing_score(data)
    signals.append(TacticalExecutionSignal.TIMING_GOOD if timing_score >= 65 else TacticalExecutionSignal.TIMING_BAD)
    vol_score = _volatility_score(data)
    signals.append(TacticalExecutionSignal.VOLATILITY_ALIGNED if vol_score >= 65 else TacticalExecutionSignal.VOLATILITY_MISMATCH)
    discipline_score = _discipline_score(data)
    signals.append(TacticalExecutionSignal.TACTICAL_DISCIPLINE_STRONG if discipline_score >= 70 else TacticalExecutionSignal.TACTICAL_DISCIPLINE_WEAK)
    alignment_score = _strategy_alignment_score(data)
    signals.append(TacticalExecutionSignal.STRATEGY_ALIGNMENT_STRONG if alignment_score >= 70 else TacticalExecutionSignal.STRATEGY_ALIGNMENT_WEAK)

    if _aggressive_decision(data) and _weak_context(data):
        signals.append(TacticalExecutionSignal.FOMO_RISK)
        signals.append(TacticalExecutionSignal.CHASE_RISK)
    if _hesitation_risk(data):
        signals.append(TacticalExecutionSignal.HESITATION_RISK)
    if _overconfidence_risk(data):
        signals.append(TacticalExecutionSignal.OVERCONFIDENCE_RISK)
    if data.trade_journal_entry is not None:
        mistakes = set(data.trade_journal_entry.mistake_types)
        if JournalMistakeType.FOMO in mistakes:
            signals.append(TacticalExecutionSignal.FOMO_RISK)
        if JournalMistakeType.CHASED_PRICE in mistakes:
            signals.append(TacticalExecutionSignal.CHASE_RISK)
    return tuple(dict.fromkeys(signals))


def evaluate_tactical_execution(
    tactical_input: TacticalExecutionInput | None = None,
    **kwargs,
) -> TacticalExecutionResult:
    """Evaluate micro execution quality. This is offline analysis only."""
    data = _input(tactical_input, **kwargs)
    entry = score_entry_quality(data)
    exit_score = score_exit_quality(data)
    timing = _timing_score(data)
    volatility = _volatility_score(data)
    discipline = _discipline_score(data)
    alignment = _strategy_alignment_score(data)
    risk_control = _risk_control_score(data)
    breakdown = TacticalScoreBreakdown(
        entry_score=entry,
        exit_score=exit_score,
        timing_score=timing,
        volatility_score=volatility,
        discipline_score=discipline,
        strategy_alignment_score=alignment,
        risk_control_score=risk_control,
    )
    signals = detect_tactical_risks(data)
    global_score = _clamp(
        entry * 0.22
        + exit_score * 0.16
        + timing * 0.14
        + volatility * 0.12
        + discipline * 0.16
        + alignment * 0.12
        + risk_control * 0.08
    )
    quality = _quality(global_score, signals, data)
    risks = _risk_notes(signals, data)
    event = TacticalExecutionEvent(
        quality=quality,
        message=f"Tactical execution evaluated at {global_score}/100.",
        timestamp=datetime.now(UTC),
    )
    return TacticalExecutionResult(
        quality=quality,
        global_score=global_score,
        breakdown=breakdown,
        signals=signals,
        risks=risks,
        recommendations=_recommendations(quality, signals),
        events=(event,),
    )


def render_tactical_execution_markdown(result: TacticalExecutionResult) -> str:
    """Render a tactical execution result as Markdown."""
    lines = [
        "# Tactical Execution Intelligence",
        "",
        "## Qualite tactique",
        "",
        f"- {result.quality.value}",
        "",
        "## Score global",
        "",
        f"- {result.global_score}/100",
        "",
        "## Score entree",
        "",
        f"- {result.breakdown.entry_score}/100",
        "",
        "## Score sortie",
        "",
        f"- {result.breakdown.exit_score}/100",
        "",
        "## Timing",
        "",
        f"- {result.breakdown.timing_score}/100",
        "",
        "## Volatilite",
        "",
        f"- {result.breakdown.volatility_score}/100",
        "",
        "## Risques tactiques",
        "",
        *_bullet_lines(result.risks),
        "",
        "## Alignement strategie",
        "",
        f"- {result.breakdown.strategy_alignment_score}/100",
        *_bullet_lines(tuple(signal.value for signal in result.signals if "STRATEGY_ALIGNMENT" in signal.value)),
        "",
        "## Recommandations AGIcore",
        "",
        *_bullet_lines(result.recommendations),
        "",
        "- Offline only: no broker, no real order, no external ML, no neural training.",
        "",
    ]
    return "\n".join(lines)


def _timing_score(data: TacticalExecutionInput) -> int:
    score = 55
    if data.context_score is not None:
        if data.context_score.decision in {TradeContextDecision.TRADE_ALLOWED, TradeContextDecision.STRONG_TRADE_ALLOWED}:
            score += 15
        elif data.context_score.decision in {TradeContextDecision.HIGH_RISK_CONTEXT, TradeContextDecision.NO_TRADE}:
            score -= 25
    if data.market_regime is not None:
        if data.market_regime.session_condition == SessionCondition.FAVORABLE:
            score += 12
        elif data.market_regime.session_condition == SessionCondition.DANGEROUS:
            score -= 25
    if data.executive_result is not None:
        if data.executive_result.state.mode == ExecutiveMode.OPPORTUNITY:
            score += 8
        elif data.executive_result.state.mode in {ExecutiveMode.DEFENSIVE, ExecutiveMode.SURVIVAL, ExecutiveMode.PAUSED}:
            score -= 12
    return _clamp(score)


def _volatility_score(data: TacticalExecutionInput) -> int:
    if data.market_regime is None:
        return 60
    score = 65
    volatility = data.market_regime.volatility
    if data.market_regime.dangerous_market:
        score -= 35
    elif volatility == VolatilityRegime.NORMAL:
        score += 15
    elif volatility == VolatilityRegime.LOW:
        score -= 8 if data.market_regime.primary_regime == MarketRegime.DEAD_MARKET else 0
    elif volatility == VolatilityRegime.HIGH:
        score += 4 if data.market_regime.context_quality_score >= 70 else -15
    elif volatility == VolatilityRegime.EXTREME:
        score -= 25
    return _clamp(score)


def _discipline_score(data: TacticalExecutionInput) -> int:
    score = 65
    if data.trade_journal_entry is not None:
        if data.trade_journal_entry.followed_playbook:
            score += 10
        else:
            score -= 25
        if data.trade_journal_entry.followed_risk_rules:
            score += 10
        else:
            score -= 30
        score -= min(30, len(data.trade_journal_entry.mistake_types) * 8)
    if data.journal_result is not None:
        score += int((data.journal_result.playbook_compliance_rate - 0.75) * 30)
        score += int((data.journal_result.risk_rules_compliance_rate - 0.75) * 30)
    if data.reward_evaluation is not None and data.reward_evaluation.reward_label == RewardLabel.DANGEROUS_DECISION:
        score -= 25
    return _clamp(score)


def _strategy_alignment_score(data: TacticalExecutionInput) -> int:
    score = 60
    if data.strategic_result is not None:
        objective = data.strategic_result.plan.primary_objective
        if objective in {StrategicObjective.CONTROLLED_GROWTH, StrategicObjective.POLICY_VALIDATION, StrategicObjective.CONSISTENCY_BUILDING}:
            score += 10
        elif objective in {StrategicObjective.CAPITAL_PRESERVATION, StrategicObjective.DRAWDOWN_RECOVERY, StrategicObjective.PAUSE_AND_REVIEW}:
            score -= 12 if _aggressive_decision(data) else 0
    if data.strategy_dna is not None and data.trade_journal_entry is not None:
        text = f"{data.trade_journal_entry.setup_name} {data.trade_journal_entry.entry_reason}".casefold()
        strategy_terms = (data.strategy_dna.name, *data.strategy_dna.entry_conditions)
        if any(str(term).casefold() in text for term in strategy_terms if term):
            score += 15
        elif data.trade_journal_entry.setup_name:
            score -= 10
    if data.context_score is not None and data.context_score.strategy_regime_notes:
        score += 5
    return _clamp(score)


def _risk_control_score(data: TacticalExecutionInput) -> int:
    score = 70
    if data.context_score is not None:
        if data.context_score.decision == TradeContextDecision.NO_TRADE:
            score -= 40
        elif data.context_score.decision == TradeContextDecision.HIGH_RISK_CONTEXT:
            score -= 25
    if data.semi_auto_decision is not None and data.semi_auto_decision.decision == SemiAutoDecision.APPROVE_REDUCED_RISK:
        score += 8
    if data.paper_execution is not None and not data.paper_execution.precheck_passed:
        score += 6
    if _aggressive_decision(data) and _weak_context(data):
        score -= 30
    if data.trade_journal_entry is not None and not data.trade_journal_entry.followed_risk_rules:
        score -= 35
    return _clamp(score)


def _quality(
    score: int,
    signals: tuple[TacticalExecutionSignal, ...],
    data: TacticalExecutionInput,
) -> TacticalExecutionQuality:
    if data.semi_auto_decision is not None and data.semi_auto_decision.decision in {SemiAutoDecision.BLOCK_TRADE, SemiAutoDecision.STOP_SESSION, SemiAutoDecision.REVIEW_ONLY}:
        if data.paper_execution is None or not data.paper_execution.accepted:
            return TacticalExecutionQuality.BLOCKED
    if any(signal in signals for signal in (TacticalExecutionSignal.FOMO_RISK, TacticalExecutionSignal.CHASE_RISK, TacticalExecutionSignal.OVERCONFIDENCE_RISK)) and score < 45:
        return TacticalExecutionQuality.DANGEROUS
    if score >= 85:
        return TacticalExecutionQuality.EXCELLENT
    if score >= 72:
        return TacticalExecutionQuality.GOOD
    if score >= 58:
        return TacticalExecutionQuality.ACCEPTABLE
    if score >= 40:
        return TacticalExecutionQuality.WEAK
    return TacticalExecutionQuality.DANGEROUS


def _risk_notes(signals: tuple[TacticalExecutionSignal, ...], data: TacticalExecutionInput) -> tuple[str, ...]:
    risks: list[str] = []
    if TacticalExecutionSignal.FOMO_RISK in signals:
        risks.append("FOMO risk: aggressive action with weak context or journal evidence.")
    if TacticalExecutionSignal.CHASE_RISK in signals:
        risks.append("Chase risk: entry may be late or price may have been chased.")
    if TacticalExecutionSignal.HESITATION_RISK in signals:
        risks.append("Hesitation risk: strong context was blocked without a clear safety reason.")
    if TacticalExecutionSignal.OVERCONFIDENCE_RISK in signals:
        risks.append("Overconfidence risk: aggressive action despite negative reward/high risk.")
    if TacticalExecutionSignal.VOLATILITY_MISMATCH in signals:
        risks.append("Volatility mismatch: regime volatility is not aligned with tactical action.")
    if TacticalExecutionSignal.TACTICAL_DISCIPLINE_WEAK in signals:
        risks.append("Tactical discipline weak: playbook, risk rules or journal mistakes need review.")
    if data.market_regime is not None and data.market_regime.dangerous_market:
        risks.append("Dangerous market regime detected.")
    return tuple(dict.fromkeys(risks)) or ("No major tactical risk detected.",)


def _recommendations(
    quality: TacticalExecutionQuality,
    signals: tuple[TacticalExecutionSignal, ...],
) -> tuple[str, ...]:
    recommendations: list[str] = []
    if quality in {TacticalExecutionQuality.DANGEROUS, TacticalExecutionQuality.BLOCKED}:
        recommendations.append("Do not increase exposure; review the tactical decision offline.")
    if TacticalExecutionSignal.FOMO_RISK in signals or TacticalExecutionSignal.CHASE_RISK in signals:
        recommendations.append("Require a pre-entry pause and compare entry price to planned level.")
    if TacticalExecutionSignal.HESITATION_RISK in signals:
        recommendations.append("Review whether valid setups are being blocked without safety justification.")
    if TacticalExecutionSignal.OVERCONFIDENCE_RISK in signals:
        recommendations.append("Reduce risk and require confirmation after negative reward.")
    if TacticalExecutionSignal.STRATEGY_ALIGNMENT_WEAK in signals:
        recommendations.append("Re-check setup against Strategy DNA and strategic objective.")
    if quality in {TacticalExecutionQuality.EXCELLENT, TacticalExecutionQuality.GOOD}:
        recommendations.append("Keep the same tactical checklist and continue offline tracking.")
    return tuple(dict.fromkeys(recommendations or ["Maintain tactical review and journal evidence."]))


def _aggressive_decision(data: TacticalExecutionInput) -> bool:
    return bool(data.semi_auto_decision is not None and data.semi_auto_decision.decision == SemiAutoDecision.APPROVE_TRADE)


def _weak_context(data: TacticalExecutionInput) -> bool:
    return bool(
        data.context_score is not None
        and (
            data.context_score.global_score < 55
            or data.context_score.decision in {TradeContextDecision.HIGH_RISK_CONTEXT, TradeContextDecision.NO_TRADE}
        )
    )


def _hesitation_risk(data: TacticalExecutionInput) -> bool:
    if data.context_score is None or data.semi_auto_decision is None:
        return False
    strong_context = data.context_score.global_score >= 80 and data.context_score.decision == TradeContextDecision.STRONG_TRADE_ALLOWED
    blocked = data.semi_auto_decision.decision in {SemiAutoDecision.BLOCK_TRADE, SemiAutoDecision.REVIEW_ONLY, SemiAutoDecision.REQUIRE_CONFIRMATION}
    safety_reasons = data.semi_auto_decision.blocking_reasons or data.semi_auto_decision.detected_risks
    return bool(strong_context and blocked and not safety_reasons)


def _overconfidence_risk(data: TacticalExecutionInput) -> bool:
    if not _aggressive_decision(data) or data.reward_evaluation is None:
        return False
    negative_reward = data.reward_evaluation.total_reward < 0 or data.reward_evaluation.reward_label in {RewardLabel.BAD_DECISION, RewardLabel.DANGEROUS_DECISION}
    high_risk = data.context_score is not None and data.context_score.decision in {TradeContextDecision.HIGH_RISK_CONTEXT, TradeContextDecision.REDUCE_RISK}
    return bool(negative_reward and high_risk)


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _input(tactical_input: TacticalExecutionInput | None = None, **kwargs: Any) -> TacticalExecutionInput:
    if tactical_input is not None:
        return tactical_input
    return TacticalExecutionInput(**kwargs)


def _clamp(value: int | float) -> int:
    return max(0, min(100, int(round(value))))


__all__ = [
    "detect_tactical_risks",
    "evaluate_tactical_execution",
    "render_tactical_execution_markdown",
    "score_entry_quality",
    "score_exit_quality",
]
