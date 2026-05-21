"""Offline Cognitive Adaptation Engine for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .behavioral_stability_models import BehavioralPressureLevel, BehavioralRecoveryState
from .cognitive_adaptation_models import (
    CognitiveAdaptationEvent,
    CognitiveAdaptationInput,
    CognitiveAdaptationMode,
    CognitiveAdaptationResult,
    CognitiveAdaptationSignal,
    CognitiveFlexibilityScore,
    CognitiveLoadLevel,
)
from .context_scoring_models import TradeContextDecision
from .executive_brain_models import ExecutiveMode
from .hierarchical_supervisor_models import SupervisorDecision
from .meta_strategy_models import MetaStrategyDecision
from .reward_models import RewardLabel
from .strategic_memory_models import StrategicDriftSignal
from .strategic_planning_models import StrategicObjective, StrategicPlanStatus
from .tactical_execution_models import TacticalExecutionQuality


def compute_cognitive_flexibility_score(
    adaptation_input: CognitiveAdaptationInput | None = None,
    **kwargs,
) -> CognitiveFlexibilityScore:
    """Compute cognitive flexibility component scores from offline evidence."""
    data = _input(adaptation_input, **kwargs)
    clarity = 70
    flexibility = 65
    load = 75
    context_adaptation = 65
    policy_adaptation = 65
    recovery_learning = 65

    if data.strategic_result is not None:
        if data.strategic_result.progress_score >= 70:
            clarity += 10
        if data.strategic_result.plan.status in {StrategicPlanStatus.PAUSED, StrategicPlanStatus.REVIEW_REQUIRED}:
            clarity -= 15
        if data.strategic_result.plan.primary_objective in {StrategicObjective.LEARNING_PHASE, StrategicObjective.DRAWDOWN_RECOVERY}:
            recovery_learning += 10
    if data.executive_result is not None:
        if data.executive_result.state.mode in {ExecutiveMode.NORMAL, ExecutiveMode.OPPORTUNITY}:
            clarity += 8
        elif data.executive_result.state.mode in {ExecutiveMode.PAUSED, ExecutiveMode.SURVIVAL}:
            clarity -= 20
            load -= 15
    if data.supervisor_result is not None:
        if data.supervisor_result.conflicts_detected:
            clarity -= 15
            load -= min(25, len(data.supervisor_result.conflicts_detected) * 8)
        if data.supervisor_result.decision in {SupervisorDecision.REQUIRE_HUMAN_REVIEW, SupervisorDecision.OVERRIDE_TO_BLOCK, SupervisorDecision.EMERGENCY_HALT}:
            clarity -= 12
            flexibility -= 8
    if data.meta_strategy is not None:
        if data.meta_strategy.required_manual_review or data.meta_strategy.decision in {MetaStrategyDecision.REQUIRE_REVIEW, MetaStrategyDecision.NO_STRATEGY}:
            clarity -= 15
        if data.meta_strategy.decision in {MetaStrategyDecision.SELECT_POLICY, MetaStrategyDecision.SELECT_REDUCED_RISK_POLICY, MetaStrategyDecision.FALLBACK_TO_CONSERVATIVE}:
            policy_adaptation += 8
        if data.meta_strategy.decision == MetaStrategyDecision.BLOCK_ALL_POLICIES:
            policy_adaptation -= 20
    if data.behavioral_stability is not None:
        load += int((data.behavioral_stability.stability_score - 60) * 0.35)
        if data.behavioral_stability.pressure_level in {BehavioralPressureLevel.HIGH, BehavioralPressureLevel.EXTREME}:
            load -= 25
            flexibility -= 10
        if data.behavioral_stability.recovery_state in {BehavioralRecoveryState.RECOVERING, BehavioralRecoveryState.STABLE}:
            recovery_learning += 10
        elif data.behavioral_stability.recovery_state in {BehavioralRecoveryState.DETERIORATING, BehavioralRecoveryState.CRITICAL}:
            recovery_learning -= 20
    if data.strategic_timeline_analysis is not None:
        context_adaptation += int((data.strategic_timeline_analysis.stability_score - 60) * 0.25)
        if data.strategic_timeline_analysis.improvement_detected:
            flexibility += 10
            recovery_learning += 8
        if data.strategic_timeline_analysis.degradation_detected:
            flexibility -= 12
            context_adaptation -= 12
    if data.context_score is not None:
        context_adaptation += int((data.context_score.global_score - 60) * 0.2)
        if data.context_score.decision in {TradeContextDecision.HIGH_RISK_CONTEXT, TradeContextDecision.NO_TRADE}:
            load -= 10
    if data.tactical_execution is not None:
        if data.tactical_execution.quality in {TacticalExecutionQuality.GOOD, TacticalExecutionQuality.EXCELLENT}:
            context_adaptation += 8
        elif data.tactical_execution.quality in {TacticalExecutionQuality.WEAK, TacticalExecutionQuality.DANGEROUS}:
            load -= 12
            context_adaptation -= 10
    if data.reward_evaluation is not None:
        if data.reward_evaluation.reward_label in {RewardLabel.GOOD_DECISION, RewardLabel.EXCELLENT_DECISION}:
            recovery_learning += 8
        elif data.reward_evaluation.reward_label in {RewardLabel.BAD_DECISION, RewardLabel.DANGEROUS_DECISION}:
            recovery_learning -= 15
            policy_adaptation -= 8

    return CognitiveFlexibilityScore(
        strategic_clarity_score=_clamp(clarity),
        decision_flexibility_score=_clamp(flexibility),
        cognitive_load_score=_clamp(load),
        context_adaptation_score=_clamp(context_adaptation),
        policy_adaptation_score=_clamp(policy_adaptation),
        recovery_learning_score=_clamp(recovery_learning),
    )


def detect_cognitive_signals(
    adaptation_input: CognitiveAdaptationInput | None = None,
    **kwargs,
) -> tuple[CognitiveAdaptationSignal, ...]:
    """Detect cognitive adaptation signals with deterministic offline heuristics."""
    data = _input(adaptation_input, **kwargs)
    scores = compute_cognitive_flexibility_score(data)
    signals: list[CognitiveAdaptationSignal] = []

    signals.append(CognitiveAdaptationSignal.STRATEGIC_CLARITY_HIGH if scores.strategic_clarity_score >= 70 else CognitiveAdaptationSignal.STRATEGIC_CLARITY_LOW)
    if _decision_confusion(data):
        signals.append(CognitiveAdaptationSignal.DECISION_CONFUSION)
    if _cognitive_load_level(data, scores) == CognitiveLoadLevel.OVERLOADED:
        signals.append(CognitiveAdaptationSignal.COGNITIVE_OVERLOAD)
    if _rigid_policy_use(data):
        signals.append(CognitiveAdaptationSignal.RIGID_POLICY_USE)
    if scores.decision_flexibility_score >= 70 and scores.context_adaptation_score >= 65:
        signals.append(CognitiveAdaptationSignal.FLEXIBLE_ADAPTATION)
    if _context_shift(data):
        signals.append(CognitiveAdaptationSignal.CONTEXT_SHIFT_DETECTED)
    if _adaptation_success(data, scores):
        signals.append(CognitiveAdaptationSignal.ADAPTATION_SUCCESS)
    if _adaptation_failure(data, scores):
        signals.append(CognitiveAdaptationSignal.ADAPTATION_FAILURE)
    if _overreaction_risk(data):
        signals.append(CognitiveAdaptationSignal.OVER_REACTION_RISK)
    if _underreaction_risk(data):
        signals.append(CognitiveAdaptationSignal.UNDER_REACTION_RISK)
    if _observe_recommended(data, scores):
        signals.append(CognitiveAdaptationSignal.OBSERVATION_MODE_RECOMMENDED)
    if _stable_pattern_exploitable(data, scores):
        signals.append(CognitiveAdaptationSignal.STABLE_PATTERN_EXPLOITABLE)
    return tuple(dict.fromkeys(signals))


def recommend_adaptation_mode(
    adaptation_input: CognitiveAdaptationInput | None = None,
    **kwargs,
) -> CognitiveAdaptationMode:
    """Recommend an offline cognitive adaptation mode."""
    data = _input(adaptation_input, **kwargs)
    scores = compute_cognitive_flexibility_score(data)
    signals = detect_cognitive_signals(data)
    load = _cognitive_load_level(data, scores)

    if load == CognitiveLoadLevel.OVERLOADED or _hard_pause(data):
        return CognitiveAdaptationMode.PAUSE
    if data.behavioral_stability is not None and data.behavioral_stability.stability_score < 45:
        return CognitiveAdaptationMode.RECOVER
    if load == CognitiveLoadLevel.HIGH:
        return CognitiveAdaptationMode.SLOW_DOWN
    if CognitiveAdaptationSignal.STABLE_PATTERN_EXPLOITABLE in signals:
        return CognitiveAdaptationMode.EXPLOIT_STABLE_PATTERN
    if CognitiveAdaptationSignal.OBSERVATION_MODE_RECOMMENDED in signals or CognitiveAdaptationSignal.DECISION_CONFUSION in signals:
        return CognitiveAdaptationMode.OBSERVE
    if CognitiveAdaptationSignal.CONTEXT_SHIFT_DETECTED in signals or CognitiveAdaptationSignal.UNDER_REACTION_RISK in signals:
        return CognitiveAdaptationMode.ADAPT
    return CognitiveAdaptationMode.OBSERVE


def evaluate_cognitive_adaptation(
    adaptation_input: CognitiveAdaptationInput | None = None,
    **kwargs,
) -> CognitiveAdaptationResult:
    """Evaluate cognitive load, flexibility and adaptation mode offline."""
    data = _input(adaptation_input, **kwargs)
    scores = compute_cognitive_flexibility_score(data)
    signals = detect_cognitive_signals(data)
    load = _cognitive_load_level(data, scores)
    mode = recommend_adaptation_mode(data)
    global_score = _global_score(scores, signals, load)
    event = CognitiveAdaptationEvent(
        mode=mode,
        load_level=load,
        message=f"Cognitive adaptation evaluated at {global_score}/100.",
        timestamp=datetime.now(UTC),
    )
    return CognitiveAdaptationResult(
        adaptation_mode=mode,
        load_level=load,
        global_score=global_score,
        flexibility_score=scores,
        signals=signals,
        risks=_risk_notes(signals, load),
        recommendations=_recommendations(mode, signals, load),
        events=(event,),
    )


def render_cognitive_adaptation_markdown(result: CognitiveAdaptationResult) -> str:
    """Render cognitive adaptation result as Markdown."""
    lines = [
        "# Cognitive Adaptation Engine",
        "",
        "## Adaptation cognitive",
        "",
        f"- Score: {result.global_score}/100",
        "",
        "## Charge cognitive",
        "",
        f"- {result.load_level.value}",
        f"- Load score: {result.flexibility_score.cognitive_load_score}/100",
        "",
        "## Flexibilite decisionnelle",
        "",
        f"- Decision flexibility: {result.flexibility_score.decision_flexibility_score}/100",
        f"- Context adaptation: {result.flexibility_score.context_adaptation_score}/100",
        f"- Policy adaptation: {result.flexibility_score.policy_adaptation_score}/100",
        "",
        "## Signaux detectes",
        "",
        *_bullet_lines(tuple(signal.value for signal in result.signals)),
        "",
        "## Risques cognitifs",
        "",
        *_bullet_lines(result.risks),
        "",
        "## Mode recommande",
        "",
        f"- {result.adaptation_mode.value}",
        "",
        "## Recommandations AGIcore",
        "",
        *_bullet_lines(result.recommendations),
        "",
        "- Offline only: no broker, no real order, no external ML, no neural training.",
        "",
    ]
    return "\n".join(lines)


def _decision_confusion(data: CognitiveAdaptationInput) -> bool:
    exec_block = data.executive_result is not None and (
        data.executive_result.decision.stop_session
        or data.executive_result.state.mode in {ExecutiveMode.PAUSED, ExecutiveMode.SURVIVAL}
    )
    supervisor_ok = data.supervisor_result is not None and data.supervisor_result.final_executable
    supervisor_block = data.supervisor_result is not None and not data.supervisor_result.final_executable
    meta_ok = data.meta_strategy is not None and data.meta_strategy.decision in {
        MetaStrategyDecision.SELECT_POLICY,
        MetaStrategyDecision.SELECT_REDUCED_RISK_POLICY,
    }
    meta_block = data.meta_strategy is not None and data.meta_strategy.decision in {
        MetaStrategyDecision.BLOCK_ALL_POLICIES,
        MetaStrategyDecision.NO_STRATEGY,
    }
    contradictions = (exec_block and meta_ok) or (supervisor_block and meta_ok) or (supervisor_ok and meta_block)
    conflicts = data.supervisor_result is not None and bool(data.supervisor_result.conflicts_detected)
    return bool(contradictions or conflicts)


def _rigid_policy_use(data: CognitiveAdaptationInput) -> bool:
    if data.meta_strategy is None:
        return False
    bad_reward = data.reward_evaluation is not None and data.reward_evaluation.reward_label in {RewardLabel.BAD_DECISION, RewardLabel.DANGEROUS_DECISION}
    weak_context = data.context_score is not None and data.context_score.decision in {TradeContextDecision.HIGH_RISK_CONTEXT, TradeContextDecision.NO_TRADE}
    selected_anyway = data.meta_strategy.decision == MetaStrategyDecision.SELECT_POLICY and not data.meta_strategy.required_manual_review
    timeline_shift = _context_shift(data)
    return bool(selected_anyway and (bad_reward or weak_context) and timeline_shift)


def _context_shift(data: CognitiveAdaptationInput) -> bool:
    if data.strategic_timeline_analysis is not None and any(
        signal in data.strategic_timeline_analysis.drift_signals
        for signal in {
            StrategicDriftSignal.STRATEGIC_DEGRADATION,
            StrategicDriftSignal.REWARD_DECLINE,
            StrategicDriftSignal.STABILITY_DECLINE,
            StrategicDriftSignal.PERSISTENT_DRAWDOWN,
        }
    ):
        return True
    return bool(data.context_score is not None and data.context_score.decision in {TradeContextDecision.HIGH_RISK_CONTEXT, TradeContextDecision.NO_TRADE})


def _adaptation_success(data: CognitiveAdaptationInput, scores: CognitiveFlexibilityScore) -> bool:
    timeline_ok = data.strategic_timeline_analysis is not None and data.strategic_timeline_analysis.improvement_detected and not data.strategic_timeline_analysis.degradation_detected
    reward_ok = data.reward_evaluation is not None and data.reward_evaluation.reward_label in {RewardLabel.GOOD_DECISION, RewardLabel.EXCELLENT_DECISION}
    behavior_ok = data.behavioral_stability is None or data.behavioral_stability.stability_score >= 70
    return bool(timeline_ok and reward_ok and behavior_ok and scores.decision_flexibility_score >= 65)


def _adaptation_failure(data: CognitiveAdaptationInput, scores: CognitiveFlexibilityScore) -> bool:
    timeline_bad = data.strategic_timeline_analysis is not None and data.strategic_timeline_analysis.degradation_detected
    reward_bad = data.reward_evaluation is not None and data.reward_evaluation.reward_label in {RewardLabel.BAD_DECISION, RewardLabel.DANGEROUS_DECISION}
    return bool((timeline_bad or reward_bad) and scores.policy_adaptation_score < 55)


def _overreaction_risk(data: CognitiveAdaptationInput) -> bool:
    if data.meta_strategy is None or data.reward_evaluation is None:
        return False
    one_bad_session = data.reward_evaluation.total_reward < 0
    hard_shift = data.meta_strategy.decision in {MetaStrategyDecision.BLOCK_ALL_POLICIES, MetaStrategyDecision.FALLBACK_TO_CONSERVATIVE}
    no_persistent_degradation = data.strategic_timeline_analysis is None or not data.strategic_timeline_analysis.degradation_detected
    return bool(one_bad_session and hard_shift and no_persistent_degradation)


def _underreaction_risk(data: CognitiveAdaptationInput) -> bool:
    persistent_degradation = data.strategic_timeline_analysis is not None and data.strategic_timeline_analysis.degradation_detected
    no_change = data.meta_strategy is not None and data.meta_strategy.decision == MetaStrategyDecision.SELECT_POLICY and not data.meta_strategy.required_manual_review
    bad_reward = data.reward_evaluation is not None and data.reward_evaluation.total_reward < 0
    return bool(persistent_degradation and no_change and bad_reward)


def _observe_recommended(data: CognitiveAdaptationInput, scores: CognitiveFlexibilityScore) -> bool:
    uncertainty = scores.strategic_clarity_score < 55 or _decision_confusion(data)
    low_evidence = data.replay_arena is None and data.strategic_timeline_analysis is None and data.reward_evaluation is None
    return bool(uncertainty or low_evidence)


def _stable_pattern_exploitable(data: CognitiveAdaptationInput, scores: CognitiveFlexibilityScore) -> bool:
    stable_context = data.context_score is not None and data.context_score.decision in {
        TradeContextDecision.TRADE_ALLOWED,
        TradeContextDecision.STRONG_TRADE_ALLOWED,
    } and data.context_score.global_score >= 75
    positive_reward = data.reward_evaluation is not None and data.reward_evaluation.normalized_reward >= 70
    stable_behavior = data.behavioral_stability is None or data.behavioral_stability.stability_score >= 70
    stable_timeline = data.strategic_timeline_analysis is None or (
        data.strategic_timeline_analysis.stability_score >= 70 and not data.strategic_timeline_analysis.degradation_detected
    )
    return bool(stable_context and positive_reward and stable_behavior and stable_timeline and scores.cognitive_load_score >= 65)


def _hard_pause(data: CognitiveAdaptationInput) -> bool:
    if data.executive_result is not None and data.executive_result.decision.stop_session:
        return True
    if data.supervisor_result is not None and data.supervisor_result.decision == SupervisorDecision.EMERGENCY_HALT:
        return True
    if data.behavioral_stability is not None and data.behavioral_stability.pressure_level == BehavioralPressureLevel.EXTREME:
        return True
    return False


def _cognitive_load_level(
    data: CognitiveAdaptationInput,
    scores: CognitiveFlexibilityScore,
) -> CognitiveLoadLevel:
    pressure_extreme = data.behavioral_stability is not None and data.behavioral_stability.pressure_level == BehavioralPressureLevel.EXTREME
    conflicts = data.supervisor_result is not None and len(data.supervisor_result.conflicts_detected) >= 2
    if scores.cognitive_load_score < 35 or (pressure_extreme and conflicts):
        return CognitiveLoadLevel.OVERLOADED
    if scores.cognitive_load_score < 55 or _decision_confusion(data):
        return CognitiveLoadLevel.HIGH
    if scores.cognitive_load_score < 75:
        return CognitiveLoadLevel.MODERATE
    return CognitiveLoadLevel.LOW


def _global_score(
    scores: CognitiveFlexibilityScore,
    signals: tuple[CognitiveAdaptationSignal, ...],
    load: CognitiveLoadLevel,
) -> int:
    score = (
        scores.strategic_clarity_score * 0.18
        + scores.decision_flexibility_score * 0.20
        + scores.cognitive_load_score * 0.18
        + scores.context_adaptation_score * 0.16
        + scores.policy_adaptation_score * 0.14
        + scores.recovery_learning_score * 0.14
    )
    score -= 8 * sum(1 for signal in signals if signal in _negative_signals())
    score += 6 * sum(1 for signal in signals if signal in _positive_signals())
    if load == CognitiveLoadLevel.OVERLOADED:
        score -= 20
    elif load == CognitiveLoadLevel.HIGH:
        score -= 10
    return _clamp(score)


def _risk_notes(
    signals: tuple[CognitiveAdaptationSignal, ...],
    load: CognitiveLoadLevel,
) -> tuple[str, ...]:
    notes: list[str] = []
    if load in {CognitiveLoadLevel.HIGH, CognitiveLoadLevel.OVERLOADED}:
        notes.append("Cognitive load is elevated.")
    mapping = {
        CognitiveAdaptationSignal.STRATEGIC_CLARITY_LOW: "Strategic clarity is low.",
        CognitiveAdaptationSignal.DECISION_CONFUSION: "Decision layers disagree or conflict.",
        CognitiveAdaptationSignal.COGNITIVE_OVERLOAD: "Cognitive overload detected.",
        CognitiveAdaptationSignal.RIGID_POLICY_USE: "Policy use appears rigid despite context/reward deterioration.",
        CognitiveAdaptationSignal.ADAPTATION_FAILURE: "Recent adaptation is not improving reward or stability.",
        CognitiveAdaptationSignal.OVER_REACTION_RISK: "Policy shift may be excessive after limited evidence.",
        CognitiveAdaptationSignal.UNDER_REACTION_RISK: "System is not adapting despite persistent degradation.",
    }
    for signal, note in mapping.items():
        if signal in signals:
            notes.append(note)
    return tuple(dict.fromkeys(notes)) or ("No major cognitive risk detected.",)


def _recommendations(
    mode: CognitiveAdaptationMode,
    signals: tuple[CognitiveAdaptationSignal, ...],
    load: CognitiveLoadLevel,
) -> tuple[str, ...]:
    recommendations: list[str] = []
    if mode == CognitiveAdaptationMode.PAUSE:
        recommendations.append("Pause decision flow and reduce cognitive load.")
    elif mode == CognitiveAdaptationMode.RECOVER:
        recommendations.append("Switch to recovery and learning-only review.")
    elif mode == CognitiveAdaptationMode.SLOW_DOWN:
        recommendations.append("Slow down decisions and require confirmation.")
    elif mode == CognitiveAdaptationMode.ADAPT:
        recommendations.append("Adapt policy selection to the new context.")
    elif mode == CognitiveAdaptationMode.EXPLOIT_STABLE_PATTERN:
        recommendations.append("Use the stable pattern with strict offline controls.")
    else:
        recommendations.append("Observe until clarity improves.")
    if CognitiveAdaptationSignal.RIGID_POLICY_USE in signals or CognitiveAdaptationSignal.UNDER_REACTION_RISK in signals:
        recommendations.append("Review policy rigidity and update selection criteria.")
    if CognitiveAdaptationSignal.OVER_REACTION_RISK in signals:
        recommendations.append("Collect more evidence before hard policy changes.")
    if load == CognitiveLoadLevel.OVERLOADED:
        recommendations.append("Block new experiments until cognitive load normalizes.")
    return tuple(dict.fromkeys(recommendations))


def _negative_signals() -> set[CognitiveAdaptationSignal]:
    return {
        CognitiveAdaptationSignal.STRATEGIC_CLARITY_LOW,
        CognitiveAdaptationSignal.DECISION_CONFUSION,
        CognitiveAdaptationSignal.COGNITIVE_OVERLOAD,
        CognitiveAdaptationSignal.RIGID_POLICY_USE,
        CognitiveAdaptationSignal.ADAPTATION_FAILURE,
        CognitiveAdaptationSignal.OVER_REACTION_RISK,
        CognitiveAdaptationSignal.UNDER_REACTION_RISK,
    }


def _positive_signals() -> set[CognitiveAdaptationSignal]:
    return {
        CognitiveAdaptationSignal.STRATEGIC_CLARITY_HIGH,
        CognitiveAdaptationSignal.FLEXIBLE_ADAPTATION,
        CognitiveAdaptationSignal.ADAPTATION_SUCCESS,
        CognitiveAdaptationSignal.STABLE_PATTERN_EXPLOITABLE,
    }


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _input(adaptation_input: CognitiveAdaptationInput | None = None, **kwargs: Any) -> CognitiveAdaptationInput:
    if adaptation_input is not None:
        return adaptation_input
    return CognitiveAdaptationInput(**kwargs)


def _clamp(value: int | float) -> int:
    return max(0, min(100, int(round(value))))


__all__ = [
    "compute_cognitive_flexibility_score",
    "detect_cognitive_signals",
    "evaluate_cognitive_adaptation",
    "recommend_adaptation_mode",
    "render_cognitive_adaptation_markdown",
]
