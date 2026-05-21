"""Offline Behavioral Stability Engine for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .context_scoring_models import TradeContextDecision
from .executive_brain_models import ExecutiveMode
from .reward_models import RewardLabel
from .session_coach_models import SessionCoachDecision
from .strategic_memory_models import StrategicDriftSignal
from .strategic_planning_models import StrategicObjective, StrategicPlanStatus
from .tactical_execution_models import TacticalExecutionQuality, TacticalExecutionSignal
from .behavioral_stability_models import (
    BehavioralPressureLevel,
    BehavioralRecoveryState,
    BehavioralRiskSignal,
    BehavioralStabilityEvent,
    BehavioralStabilityInput,
    BehavioralStabilityResult,
    BehavioralStabilityScore,
)


def detect_behavioral_risks(
    stability_input: BehavioralStabilityInput | None = None,
    **kwargs,
) -> tuple[BehavioralRiskSignal, ...]:
    """Detect behavioral risks using deterministic offline heuristics."""
    data = _input(stability_input, **kwargs)
    signals: list[BehavioralRiskSignal] = []

    if _tilt_risk(data):
        signals.append(BehavioralRiskSignal.TILT_RISK)
    if _revenge_risk(data):
        signals.append(BehavioralRiskSignal.REVENGE_RISK)
    if _discipline_decay(data):
        signals.append(BehavioralRiskSignal.DISCIPLINE_DECAY)
    if _fatigue_risk(data):
        signals.append(BehavioralRiskSignal.FATIGUE_RISK)
    if _overconfidence_risk(data):
        signals.append(BehavioralRiskSignal.OVERCONFIDENCE_RISK)
    if _fear_block(data):
        signals.append(BehavioralRiskSignal.FEAR_BLOCK)
    if _hesitation_spiral(data):
        signals.append(BehavioralRiskSignal.HESITATION_SPIRAL)
    if _emotional_instability(data):
        signals.append(BehavioralRiskSignal.EMOTIONAL_INSTABILITY)
    if evaluate_recovery_state(data) == BehavioralRecoveryState.RECOVERING:
        signals.append(BehavioralRiskSignal.RECOVERY_IN_PROGRESS)
    if _pressure_level(data) in {BehavioralPressureLevel.HIGH, BehavioralPressureLevel.EXTREME}:
        signals.append(BehavioralRiskSignal.PSYCHOLOGICAL_PRESSURE_HIGH)
    if _session_overload(data):
        signals.append(BehavioralRiskSignal.SESSION_OVERLOAD)
    if _consistent_discipline(data):
        signals.append(BehavioralRiskSignal.CONSISTENT_DISCIPLINE)
    if not any(signal in signals for signal in _negative_signals()):
        signals.append(BehavioralRiskSignal.STABLE_BEHAVIOR)
    return tuple(dict.fromkeys(signals))


def evaluate_recovery_state(
    stability_input: BehavioralStabilityInput | None = None,
    **kwargs,
) -> BehavioralRecoveryState:
    """Evaluate current behavioral recovery state."""
    data = _input(stability_input, **kwargs)
    if data.session_coach_result is not None and data.session_coach_result.decision == SessionCoachDecision.STOP_TRADING:
        return BehavioralRecoveryState.CRITICAL
    if data.executive_result is not None and data.executive_result.state.mode in {ExecutiveMode.SURVIVAL, ExecutiveMode.PAUSED}:
        return BehavioralRecoveryState.CRITICAL
    if _tilt_risk(data) or _revenge_risk(data) or _extreme_drawdown_pressure(data):
        return BehavioralRecoveryState.DETERIORATING
    if _discipline_decay(data) or _fatigue_risk(data) or _pressure_level(data) == BehavioralPressureLevel.HIGH:
        return BehavioralRecoveryState.FRAGILE
    if data.strategic_result is not None and (
        data.strategic_result.plan.status == StrategicPlanStatus.RECOVERY
        or data.strategic_result.plan.primary_objective == StrategicObjective.DRAWDOWN_RECOVERY
    ):
        return BehavioralRecoveryState.RECOVERING
    if data.strategic_timeline_analysis is not None and data.strategic_timeline_analysis.improvement_detected and not data.strategic_timeline_analysis.degradation_detected:
        return BehavioralRecoveryState.RECOVERING
    return BehavioralRecoveryState.STABLE


def compute_behavioral_stability_score(
    stability_input: BehavioralStabilityInput | None = None,
    **kwargs,
) -> BehavioralStabilityScore:
    """Compute component stability scores from 0 to 100."""
    data = _input(stability_input, **kwargs)
    discipline = 75
    emotional = 75
    fatigue = 80
    pressure = 75
    recovery = 70
    consistency = 70

    if data.tactical_execution is not None:
        discipline = int((discipline + data.tactical_execution.breakdown.discipline_score) / 2)
        if data.tactical_execution.quality in {TacticalExecutionQuality.WEAK, TacticalExecutionQuality.DANGEROUS}:
            discipline -= 18
            emotional -= 12
        if TacticalExecutionSignal.HESITATION_RISK in data.tactical_execution.signals:
            emotional -= 10
        if TacticalExecutionSignal.OVERCONFIDENCE_RISK in data.tactical_execution.signals:
            emotional -= 18
    if data.journal_result is not None:
        discipline += int((data.journal_result.playbook_compliance_rate - 0.75) * 35)
        discipline += int((data.journal_result.risk_rules_compliance_rate - 0.75) * 35)
        emotional -= min(35, len(data.journal_result.keyword_flags) * 8)
        if _journal_has_keyword(data, "fatigue"):
            fatigue -= 25
    if data.reward_evaluation is not None:
        if data.reward_evaluation.total_reward < 0:
            emotional -= 15
            recovery -= 10
        if data.reward_evaluation.reward_label == RewardLabel.DANGEROUS_DECISION:
            discipline -= 20
            emotional -= 20
        elif data.reward_evaluation.reward_label == RewardLabel.EXCELLENT_DECISION:
            recovery += 10
    if data.strategic_timeline_analysis is not None:
        consistency = data.strategic_timeline_analysis.stability_score
        pressure += int((data.strategic_timeline_analysis.strategic_health_score - 60) * 0.25)
        if data.strategic_timeline_analysis.degradation_detected:
            recovery -= 15
            pressure -= 15
    if data.session_coach_result is not None:
        if data.session_coach_result.break_recommended:
            fatigue -= 20
        if data.session_coach_result.stop_recommended:
            discipline -= 25
            pressure -= 25
        if data.session_coach_result.reduce_size:
            pressure -= 8
    if data.context_score is not None and data.context_score.decision in {TradeContextDecision.HIGH_RISK_CONTEXT, TradeContextDecision.NO_TRADE}:
        pressure -= 15
    if data.replay_arena is not None and data.replay_arena.dangerous_decisions:
        discipline -= min(25, data.replay_arena.dangerous_decisions * 5)
    return BehavioralStabilityScore(
        discipline_score=_clamp(discipline),
        emotional_control_score=_clamp(emotional),
        fatigue_score=_clamp(fatigue),
        pressure_resilience_score=_clamp(pressure),
        recovery_score=_clamp(recovery),
        consistency_score=_clamp(consistency),
    )


def evaluate_behavioral_stability(
    stability_input: BehavioralStabilityInput | None = None,
    **kwargs,
) -> BehavioralStabilityResult:
    """Evaluate offline behavioral stability and recommendations."""
    data = _input(stability_input, **kwargs)
    breakdown = compute_behavioral_stability_score(data)
    signals = detect_behavioral_risks(data)
    pressure = _pressure_level(data, breakdown)
    recovery = evaluate_recovery_state(data)
    score = _global_score(breakdown, signals, pressure, recovery)
    event = BehavioralStabilityEvent(
        pressure_level=pressure,
        recovery_state=recovery,
        message=f"Behavioral stability evaluated at {score}/100.",
        timestamp=datetime.now(UTC),
    )
    return BehavioralStabilityResult(
        stability_score=score,
        pressure_level=pressure,
        recovery_state=recovery,
        score_breakdown=breakdown,
        signals=signals,
        risks=_risk_notes(signals),
        recommendations=_recommendations(score, pressure, recovery, signals),
        events=(event,),
    )


def render_behavioral_stability_markdown(result: BehavioralStabilityResult) -> str:
    """Render behavioral stability analysis as Markdown."""
    lines = [
        "# Behavioral Stability Engine",
        "",
        "## Stabilite comportementale",
        "",
        f"- Recovery state: {result.recovery_state.value}",
        "",
        "## Score global",
        "",
        f"- {result.stability_score}/100",
        "",
        "## Pression psychologique",
        "",
        f"- {result.pressure_level.value}",
        f"- Pressure resilience: {result.score_breakdown.pressure_resilience_score}/100",
        "",
        "## Risques detectes",
        "",
        *_bullet_lines(result.risks),
        "",
        "## Etat recuperation",
        "",
        f"- {result.recovery_state.value}",
        f"- Recovery score: {result.score_breakdown.recovery_score}/100",
        "",
        "## Discipline",
        "",
        f"- {result.score_breakdown.discipline_score}/100",
        *_bullet_lines(tuple(signal.value for signal in result.signals if "DISCIPLINE" in signal.value)),
        "",
        "## Fatigue",
        "",
        f"- {result.score_breakdown.fatigue_score}/100",
        *_bullet_lines(tuple(signal.value for signal in result.signals if "FATIGUE" in signal.value)),
        "",
        "## Tilt/Revenge",
        "",
        *_bullet_lines(tuple(signal.value for signal in result.signals if signal in {BehavioralRiskSignal.TILT_RISK, BehavioralRiskSignal.REVENGE_RISK})),
        "",
        "## Recommandations AGIcore",
        "",
        *_bullet_lines(result.recommendations),
        "",
        "- Offline only: no broker, no real order, no external ML, no neural training.",
        "",
    ]
    return "\n".join(lines)


def _tilt_risk(data: BehavioralStabilityInput) -> bool:
    negative = data.reward_evaluation is not None and data.reward_evaluation.total_reward < 0
    frustration = any(keyword in _journal_keywords(data) for keyword in {"tilt", "peur", "fear", "frustration"})
    tactical = data.tactical_execution is not None and data.tactical_execution.quality in {TacticalExecutionQuality.WEAK, TacticalExecutionQuality.DANGEROUS}
    return bool(negative and (frustration or tactical))


def _revenge_risk(data: BehavioralStabilityInput) -> bool:
    journal_revenge = "revenge" in _journal_keywords(data)
    replay_revenge = data.replay_arena is not None and data.replay_arena.dangerous_decisions > 0 and data.replay_arena.executed_orders > data.replay_arena.blocked_orders + 2
    tactical_chase = data.tactical_execution is not None and TacticalExecutionSignal.CHASE_RISK in data.tactical_execution.signals
    negative = data.reward_evaluation is not None and data.reward_evaluation.total_reward < 0
    return bool(journal_revenge or (negative and (replay_revenge or tactical_chase)))


def _discipline_decay(data: BehavioralStabilityInput) -> bool:
    if data.journal_result is not None and (data.journal_result.playbook_compliance_rate < 0.7 or data.journal_result.risk_rules_compliance_rate < 0.7):
        return True
    if data.strategic_timeline_analysis is not None and any(signal in data.strategic_timeline_analysis.drift_signals for signal in (StrategicDriftSignal.STABILITY_DECLINE, StrategicDriftSignal.VIOLATIONS_INCREASE)):
        return True
    if data.tactical_execution is not None and TacticalExecutionSignal.TACTICAL_DISCIPLINE_WEAK in data.tactical_execution.signals:
        return True
    return False


def _fatigue_risk(data: BehavioralStabilityInput) -> bool:
    if _journal_has_keyword(data, "fatigue"):
        return True
    if data.session_coach_result is not None and data.session_coach_result.break_recommended:
        return True
    return bool(data.tactical_execution is not None and data.tactical_execution.global_score < 55 and TacticalExecutionSignal.HESITATION_RISK in data.tactical_execution.signals)


def _overconfidence_risk(data: BehavioralStabilityInput) -> bool:
    if data.tactical_execution is not None and TacticalExecutionSignal.OVERCONFIDENCE_RISK in data.tactical_execution.signals:
        return True
    excessive_gain = data.reward_evaluation is not None and data.reward_evaluation.total_reward > 60 and data.reward_evaluation.normalized_reward > 85
    risky_context = data.context_score is not None and data.context_score.decision in {TradeContextDecision.HIGH_RISK_CONTEXT, TradeContextDecision.REDUCE_RISK}
    return bool(excessive_gain and risky_context)


def _fear_block(data: BehavioralStabilityInput) -> bool:
    fear = any(keyword in _journal_keywords(data) for keyword in {"peur", "fear"})
    context_strong = data.context_score is not None and data.context_score.global_score >= 80
    return bool(fear and context_strong)


def _hesitation_spiral(data: BehavioralStabilityInput) -> bool:
    return bool(data.tactical_execution is not None and TacticalExecutionSignal.HESITATION_RISK in data.tactical_execution.signals and _fear_block(data))


def _emotional_instability(data: BehavioralStabilityInput) -> bool:
    keywords = _journal_keywords(data)
    return bool(len(keywords.intersection({"tilt", "revenge", "fatigue", "peur", "fear", "euphorie"})) >= 2)


def _session_overload(data: BehavioralStabilityInput) -> bool:
    if data.session_coach_result is not None and (data.session_coach_result.stop_recommended or data.session_coach_result.break_recommended):
        return True
    return bool(data.replay_arena is not None and data.replay_arena.executed_orders >= 6)


def _consistent_discipline(data: BehavioralStabilityInput) -> bool:
    journal_ok = data.journal_result is None or (data.journal_result.playbook_compliance_rate >= 0.85 and data.journal_result.risk_rules_compliance_rate >= 0.85)
    tactical_ok = data.tactical_execution is None or data.tactical_execution.quality in {TacticalExecutionQuality.GOOD, TacticalExecutionQuality.EXCELLENT}
    timeline_ok = data.strategic_timeline_analysis is None or data.strategic_timeline_analysis.stability_score >= 70
    return bool(journal_ok and tactical_ok and timeline_ok)


def _extreme_drawdown_pressure(data: BehavioralStabilityInput) -> bool:
    return bool(
        data.strategic_timeline_analysis is not None
        and any(signal == StrategicDriftSignal.PERSISTENT_DRAWDOWN for signal in data.strategic_timeline_analysis.drift_signals)
        and data.strategic_timeline_analysis.strategic_health_score < 45
    )


def _pressure_level(
    data: BehavioralStabilityInput,
    breakdown: BehavioralStabilityScore | None = None,
) -> BehavioralPressureLevel:
    score = 0
    if data.strategic_timeline_analysis is not None:
        if data.strategic_timeline_analysis.strategic_health_score < 40:
            score += 35
        if any(signal == StrategicDriftSignal.PERSISTENT_DRAWDOWN for signal in data.strategic_timeline_analysis.drift_signals):
            score += 25
        if data.strategic_timeline_analysis.degradation_detected:
            score += 15
    if data.reward_evaluation is not None and data.reward_evaluation.total_reward < 0:
        score += 15
    if data.context_score is not None and data.context_score.decision == TradeContextDecision.NO_TRADE:
        score += 15
    if data.session_coach_result is not None and data.session_coach_result.stop_recommended:
        score += 25
    if breakdown is not None:
        score += max(0, 60 - breakdown.pressure_resilience_score)
    if score >= 70:
        return BehavioralPressureLevel.EXTREME
    if score >= 45:
        return BehavioralPressureLevel.HIGH
    if score >= 20:
        return BehavioralPressureLevel.MODERATE
    return BehavioralPressureLevel.LOW


def _global_score(
    breakdown: BehavioralStabilityScore,
    signals: tuple[BehavioralRiskSignal, ...],
    pressure: BehavioralPressureLevel,
    recovery: BehavioralRecoveryState,
) -> int:
    score = (
        breakdown.discipline_score * 0.22
        + breakdown.emotional_control_score * 0.22
        + breakdown.fatigue_score * 0.14
        + breakdown.pressure_resilience_score * 0.16
        + breakdown.recovery_score * 0.12
        + breakdown.consistency_score * 0.14
    )
    score -= 7 * sum(1 for signal in signals if signal in _negative_signals())
    if pressure == BehavioralPressureLevel.EXTREME:
        score -= 25
    elif pressure == BehavioralPressureLevel.HIGH:
        score -= 12
    if recovery == BehavioralRecoveryState.CRITICAL:
        score -= 25
    elif recovery == BehavioralRecoveryState.DETERIORATING:
        score -= 18
    elif recovery == BehavioralRecoveryState.RECOVERING:
        score += 6
    if BehavioralRiskSignal.CONSISTENT_DISCIPLINE in signals:
        score += 6
    return _clamp(score)


def _risk_notes(signals: tuple[BehavioralRiskSignal, ...]) -> tuple[str, ...]:
    notes: list[str] = []
    mapping = {
        BehavioralRiskSignal.TILT_RISK: "Tilt risk detected from losses, frustration or weak tactical quality.",
        BehavioralRiskSignal.REVENGE_RISK: "Revenge risk detected from losses, frequency or journal signals.",
        BehavioralRiskSignal.DISCIPLINE_DECAY: "Discipline decay detected across tactical/journal/timeline evidence.",
        BehavioralRiskSignal.FATIGUE_RISK: "Fatigue risk detected; break or reduced load recommended.",
        BehavioralRiskSignal.OVERCONFIDENCE_RISK: "Overconfidence risk detected after gains or risky approval.",
        BehavioralRiskSignal.FEAR_BLOCK: "Fear block detected in strong context.",
        BehavioralRiskSignal.HESITATION_SPIRAL: "Hesitation spiral detected from fear plus blocked execution.",
        BehavioralRiskSignal.EMOTIONAL_INSTABILITY: "Multiple emotional instability keywords detected.",
        BehavioralRiskSignal.PSYCHOLOGICAL_PRESSURE_HIGH: "Psychological pressure is high.",
        BehavioralRiskSignal.SESSION_OVERLOAD: "Session overload detected.",
    }
    for signal, message in mapping.items():
        if signal in signals:
            notes.append(message)
    return tuple(notes) or ("No major behavioral risk detected.",)


def _recommendations(
    score: int,
    pressure: BehavioralPressureLevel,
    recovery: BehavioralRecoveryState,
    signals: tuple[BehavioralRiskSignal, ...],
) -> tuple[str, ...]:
    recommendations: list[str] = []
    if pressure == BehavioralPressureLevel.EXTREME or recovery == BehavioralRecoveryState.CRITICAL or score < 35:
        recommendations.append("Pause the session and protect capital.")
    if BehavioralRiskSignal.REVENGE_RISK in signals or BehavioralRiskSignal.TILT_RISK in signals:
        recommendations.append("Switch to learning/recovery mode before any new paper decision.")
    if BehavioralRiskSignal.FATIGUE_RISK in signals or BehavioralRiskSignal.SESSION_OVERLOAD in signals:
        recommendations.append("Take a break and reduce session load.")
    if BehavioralRiskSignal.OVERCONFIDENCE_RISK in signals:
        recommendations.append("Reduce aggressiveness and require manual confirmation.")
    if BehavioralRiskSignal.DISCIPLINE_DECAY in signals:
        recommendations.append("Reinforce playbook and risk rules before continuing.")
    if BehavioralRiskSignal.CONSISTENT_DISCIPLINE in signals and pressure == BehavioralPressureLevel.LOW:
        recommendations.append("Maintain the current discipline process.")
    return tuple(dict.fromkeys(recommendations or ("Continue monitoring behavioral stability offline.",)))


def _journal_keywords(data: BehavioralStabilityInput) -> set[str]:
    if data.journal_result is None:
        return set()
    return {keyword.casefold() for _, keyword in data.journal_result.keyword_flags}


def _journal_has_keyword(data: BehavioralStabilityInput, keyword: str) -> bool:
    return keyword.casefold() in _journal_keywords(data)


def _negative_signals() -> set[BehavioralRiskSignal]:
    return {
        BehavioralRiskSignal.TILT_RISK,
        BehavioralRiskSignal.REVENGE_RISK,
        BehavioralRiskSignal.DISCIPLINE_DECAY,
        BehavioralRiskSignal.FATIGUE_RISK,
        BehavioralRiskSignal.OVERCONFIDENCE_RISK,
        BehavioralRiskSignal.FEAR_BLOCK,
        BehavioralRiskSignal.HESITATION_SPIRAL,
        BehavioralRiskSignal.EMOTIONAL_INSTABILITY,
        BehavioralRiskSignal.PSYCHOLOGICAL_PRESSURE_HIGH,
        BehavioralRiskSignal.SESSION_OVERLOAD,
    }


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _input(stability_input: BehavioralStabilityInput | None = None, **kwargs: Any) -> BehavioralStabilityInput:
    if stability_input is not None:
        return stability_input
    return BehavioralStabilityInput(**kwargs)


def _clamp(value: int | float) -> int:
    return max(0, min(100, int(round(value))))


__all__ = [
    "compute_behavioral_stability_score",
    "detect_behavioral_risks",
    "evaluate_behavioral_stability",
    "evaluate_recovery_state",
    "render_behavioral_stability_markdown",
]
