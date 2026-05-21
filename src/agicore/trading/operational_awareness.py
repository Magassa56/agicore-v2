"""Offline Autonomous Operational Awareness Engine for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .behavioral_stability_models import BehavioralPressureLevel, BehavioralRecoveryState
from .cognitive_adaptation_models import CognitiveLoadLevel
from .executive_brain_models import ExecutiveMode
from .hierarchical_supervisor_models import SupervisorDecision
from .mission_continuity_models import MissionContinuityMode
from .multi_agent_models import AgentConsensusStatus, AgentVote
from .operational_awareness_models import (
    OperationalAwarenessInput,
    OperationalAwarenessMode,
    OperationalAwarenessResult,
    OperationalConfidenceScore,
    OperationalEvent,
    OperationalHealthStatus,
    OperationalMetric,
    OperationalRecommendation,
    OperationalRisk,
    OperationalSignal,
)
from .recursive_self_evaluation_models import SelfEvaluationStatus, SystemAutonomyRecommendation
from .recovery_resilience_models import RecoveryMode
from .strategic_memory_models import StrategicDriftSignal
from .system_integrity_models import SystemIntegrityStatus


def evaluate_operational_awareness(
    awareness_input: OperationalAwarenessInput | None = None,
    **kwargs,
) -> OperationalAwarenessResult:
    """Evaluate global operational state and dynamic offline recommendations."""
    data = _input(awareness_input, **kwargs)
    confidence = compute_operational_confidence(data)
    signals = analyze_operational_signals(data, confidence=confidence)
    risks = detect_operational_risks(data, confidence=confidence, signals=signals)
    score = _global_confidence(confidence, risks)
    mode = _mode(data, confidence, risks, signals, score)
    health = _health(score, risks)
    if mode == OperationalAwarenessMode.CRITICAL and health not in {
        OperationalHealthStatus.CRITICAL,
        OperationalHealthStatus.COLLAPSING,
    }:
        health = OperationalHealthStatus.CRITICAL
    recommendations = build_operational_recommendations(data, risks=risks, mode=mode)
    metrics = _metrics(data, confidence)
    event = OperationalEvent(
        mode=mode,
        health_status=health,
        message=f"Operational awareness {mode.value}; confidence {score}/100.",
        timestamp=datetime.now(UTC),
    )
    return OperationalAwarenessResult(
        mode=mode,
        health_status=health,
        operational_confidence_score=score,
        confidence_breakdown=confidence,
        signals=signals,
        risks=risks,
        metrics=metrics,
        recommendations=recommendations,
        system_load_score=_system_load(data, risks),
        coordination_quality_score=confidence.coordination_score,
        monitoring_state=_monitoring_state(mode, health),
        events=(event,),
        summary=f"Operational mode {mode.value} with confidence {score}/100 and {len(risks)} risk(s).",
    )


def detect_operational_risks(
    awareness_input: OperationalAwarenessInput | None = None,
    *,
    confidence: OperationalConfidenceScore | None = None,
    signals: tuple[OperationalSignal, ...] | None = None,
    **kwargs,
) -> tuple[OperationalRisk, ...]:
    """Detect operational risks, including silent degradation."""
    data = _input(awareness_input, **kwargs)
    resolved_confidence = confidence or compute_operational_confidence(data)
    resolved_signals = signals or analyze_operational_signals(data, confidence=resolved_confidence)
    risks: list[OperationalRisk] = []

    weak_count = sum(
        1
        for value in (
            resolved_confidence.system_health_score,
            resolved_confidence.continuity_score,
            resolved_confidence.recovery_score,
            resolved_confidence.coordination_score,
            resolved_confidence.executive_score,
            resolved_confidence.memory_score,
            resolved_confidence.autonomy_score,
        )
        if 45 <= value < 70
    )
    if weak_count >= 3 and not any(value < 35 for value in _score_values(resolved_confidence)):
        risks.append(OperationalRisk.SILENT_DEGRADATION)

    if data.agent_coordination is not None and (
        data.agent_coordination.consensus_status == AgentConsensusStatus.NO_CONSENSUS
        or data.agent_coordination.consensus_score < 55
        or len(data.agent_coordination.disagreements) >= 2
    ):
        risks.append(OperationalRisk.AGENT_COORDINATION_DRIFT)

    if data.executive_result is not None and (
        data.executive_result.state.mode in {ExecutiveMode.SURVIVAL, ExecutiveMode.PAUSED}
        or data.executive_result.decision.stop_session
    ):
        risks.append(OperationalRisk.EXECUTIVE_INSTABILITY)

    if data.strategic_timeline_analysis is not None and (
        data.strategic_timeline_analysis.snapshots_count == 0
        or data.strategic_timeline_analysis.stability_score < 50
        or StrategicDriftSignal.STABILITY_DECLINE in data.strategic_timeline_analysis.drift_signals
    ):
        risks.append(OperationalRisk.MEMORY_FRAGMENTATION)

    if data.cognitive_adaptation is not None and data.cognitive_adaptation.load_level in {CognitiveLoadLevel.HIGH, CognitiveLoadLevel.OVERLOADED}:
        risks.append(OperationalRisk.COGNITIVE_SATURATION)

    if data.strategic_timeline_analysis is not None and (
        data.strategic_timeline_analysis.degradation_detected
        or StrategicDriftSignal.STRATEGIC_DEGRADATION in data.strategic_timeline_analysis.drift_signals
    ):
        risks.append(OperationalRisk.STRATEGIC_INCONSISTENCY)

    if data.recovery_resilience is not None and data.recovery_resilience.mode in {RecoveryMode.PAUSED_RECOVERY, RecoveryMode.STABILIZE, RecoveryMode.REDUCE_COMPLEXITY}:
        if data.recovery_resilience.resilience_score < 55 or len(data.recovery_resilience.risks) >= 3:
            risks.append(OperationalRisk.RECOVERY_STAGNATION)

    if data.self_evaluation is not None and (
        data.self_evaluation.status in {SelfEvaluationStatus.AUTONOMY_REDUCED, SelfEvaluationStatus.UNSTABLE, SelfEvaluationStatus.CONTRADICTORY}
        or data.self_evaluation.autonomy_recommendation != SystemAutonomyRecommendation.MAINTAIN_AUTONOMY
    ):
        risks.append(OperationalRisk.AUTONOMY_DRIFT)

    if data.supervisor_result is not None and (
        data.supervisor_result.decision in {SupervisorDecision.REQUIRE_HUMAN_REVIEW, SupervisorDecision.EMERGENCY_HALT}
        or len(data.supervisor_result.conflicts_detected) >= 2
    ):
        risks.append(OperationalRisk.DECISION_LATENCY)

    if data.behavioral_stability is not None and (
        data.behavioral_stability.pressure_level in {BehavioralPressureLevel.HIGH, BehavioralPressureLevel.EXTREME}
        or data.behavioral_stability.recovery_state in {BehavioralRecoveryState.DETERIORATING, BehavioralRecoveryState.CRITICAL}
    ):
        risks.append(OperationalRisk.SYSTEM_FATIGUE)

    if OperationalSignal.LOAD_CRITICAL in resolved_signals and OperationalRisk.COGNITIVE_SATURATION not in risks:
        risks.append(OperationalRisk.COGNITIVE_SATURATION)

    return tuple(dict.fromkeys(risks))


def compute_operational_confidence(
    awareness_input: OperationalAwarenessInput | None = None,
    **kwargs,
) -> OperationalConfidenceScore:
    """Compute operational confidence components from 0..100."""
    data = _input(awareness_input, **kwargs)
    system = 80
    continuity = 80
    recovery = 80
    coordination = 80
    executive = 80
    memory = 80
    cognitive = 80
    behavioral = 80
    autonomy = 80

    if data.system_integrity is not None:
        system = data.system_integrity.integrity_score
        if data.system_integrity.status in {SystemIntegrityStatus.COMPROMISED, SystemIntegrityStatus.PROTECTION_MODE}:
            system -= 25
        elif data.system_integrity.status == SystemIntegrityStatus.UNSTABLE:
            system -= 12

    if data.mission_continuity is not None:
        continuity = data.mission_continuity.continuity_score
        if data.mission_continuity.mode in {MissionContinuityMode.SURVIVAL_CONTINUITY, MissionContinuityMode.SAFE_PAUSE}:
            continuity -= 20
        elif data.mission_continuity.mode in {MissionContinuityMode.ESSENTIAL_ONLY, MissionContinuityMode.ISOLATED_OPERATION}:
            continuity -= 10

    if data.recovery_resilience is not None:
        recovery = data.recovery_resilience.resilience_score
        if data.recovery_resilience.mode == RecoveryMode.PAUSED_RECOVERY:
            recovery -= 20
        elif data.recovery_resilience.mode == RecoveryMode.REBUILD_CONFIDENCE:
            recovery += 5

    if data.agent_coordination is not None:
        coordination = data.agent_coordination.consensus_score
        coordination -= min(25, len(data.agent_coordination.disagreements) * 5)
        if data.agent_coordination.final_vote in {AgentVote.BLOCK, AgentVote.STOP_SESSION}:
            coordination -= 10

    if data.supervisor_result is not None:
        if not data.supervisor_result.final_executable:
            coordination -= 15
        if data.supervisor_result.critical_risks:
            coordination -= min(20, len(data.supervisor_result.critical_risks) * 5)

    if data.executive_result is not None:
        if data.executive_result.state.mode in {ExecutiveMode.SURVIVAL, ExecutiveMode.PAUSED}:
            executive = 35
        elif data.executive_result.state.mode in {ExecutiveMode.DEFENSIVE, ExecutiveMode.RECOVERY}:
            executive = 62
        if data.executive_result.decision.stop_session:
            executive -= 20

    if data.strategic_timeline_analysis is not None:
        memory = data.strategic_timeline_analysis.stability_score
        if data.strategic_timeline_analysis.snapshots_count == 0:
            memory -= 35
        if data.strategic_timeline_analysis.degradation_detected:
            memory -= 15

    if data.cognitive_adaptation is not None:
        cognitive = data.cognitive_adaptation.global_score
        if data.cognitive_adaptation.load_level == CognitiveLoadLevel.OVERLOADED:
            cognitive -= 25
        elif data.cognitive_adaptation.load_level == CognitiveLoadLevel.HIGH:
            cognitive -= 10

    if data.behavioral_stability is not None:
        behavioral = data.behavioral_stability.stability_score
        if data.behavioral_stability.pressure_level == BehavioralPressureLevel.EXTREME:
            behavioral -= 20
        elif data.behavioral_stability.pressure_level == BehavioralPressureLevel.HIGH:
            behavioral -= 10

    if data.self_evaluation is not None:
        autonomy = data.self_evaluation.confidence_score
        if data.self_evaluation.autonomy_recommendation != SystemAutonomyRecommendation.MAINTAIN_AUTONOMY:
            autonomy -= 15

    return OperationalConfidenceScore(
        system_health_score=_clamp(system),
        continuity_score=_clamp(continuity),
        recovery_score=_clamp(recovery),
        coordination_score=_clamp(coordination),
        executive_score=_clamp(executive),
        memory_score=_clamp(memory),
        cognitive_load_score=_clamp(cognitive),
        behavioral_stability_score=_clamp(behavioral),
        autonomy_score=_clamp(autonomy),
    )


def build_operational_recommendations(
    awareness_input: OperationalAwarenessInput | None = None,
    *,
    risks: tuple[OperationalRisk, ...] | None = None,
    mode: OperationalAwarenessMode | None = None,
    **kwargs,
) -> tuple[OperationalRecommendation, ...]:
    """Build ordered operational recommendations."""
    data = _input(awareness_input, **kwargs)
    confidence = compute_operational_confidence(data)
    resolved_risks = risks or detect_operational_risks(data, confidence=confidence)
    resolved_mode = mode or _mode(data, confidence, resolved_risks, analyze_operational_signals(data, confidence=confidence), _global_confidence(confidence, resolved_risks))
    recommendations: list[OperationalRecommendation] = []

    if resolved_mode in {OperationalAwarenessMode.CRITICAL, OperationalAwarenessMode.UNSTABLE}:
        recommendations.append(OperationalRecommendation.PRIORITIZE_CRITICAL_SYSTEMS)
        recommendations.append(OperationalRecommendation.REQUIRE_SUPERVISION)
    if resolved_mode in {OperationalAwarenessMode.HIGH_LOAD, OperationalAwarenessMode.FRAGMENTED, OperationalAwarenessMode.DEGRADED}:
        recommendations.append(OperationalRecommendation.REDUCE_COMPLEXITY)
    if OperationalRisk.AUTONOMY_DRIFT in resolved_risks or OperationalRisk.EXECUTIVE_INSTABILITY in resolved_risks:
        recommendations.append(OperationalRecommendation.REDUCE_AUTONOMY)
    if OperationalRisk.AGENT_COORDINATION_DRIFT in resolved_risks:
        recommendations.append(OperationalRecommendation.STABILIZE_COORDINATION)
    if OperationalRisk.COGNITIVE_SATURATION in resolved_risks:
        recommendations.append(OperationalRecommendation.FREEZE_LEARNING)
    if OperationalRisk.RECOVERY_STAGNATION in resolved_risks:
        recommendations.append(OperationalRecommendation.INITIATE_RECOVERY)
    if OperationalRisk.SILENT_DEGRADATION in resolved_risks or OperationalRisk.MEMORY_FRAGMENTATION in resolved_risks:
        recommendations.append(OperationalRecommendation.REBUILD_STABILITY)
    if not recommendations and resolved_mode in {OperationalAwarenessMode.OPTIMAL, OperationalAwarenessMode.STABLE}:
        recommendations.append(OperationalRecommendation.MAINTAIN_OPERATION)
    recommendations.append(OperationalRecommendation.CONTINUE_MONITORING)
    return tuple(dict.fromkeys(recommendations))


def analyze_operational_signals(
    awareness_input: OperationalAwarenessInput | None = None,
    *,
    confidence: OperationalConfidenceScore | None = None,
    **kwargs,
) -> tuple[OperationalSignal, ...]:
    """Analyze active operational signals from scores and layer states."""
    data = _input(awareness_input, **kwargs)
    scores = confidence or compute_operational_confidence(data)
    signals: list[OperationalSignal] = []
    avg = _avg(_score_values(scores))
    signals.append(OperationalSignal.SYSTEM_HEALTH_STRONG if avg >= 75 else OperationalSignal.SYSTEM_HEALTH_WEAK)
    load = _system_load(data, ())
    if load >= 75:
        signals.append(OperationalSignal.LOAD_CRITICAL)
    elif load >= 55:
        signals.append(OperationalSignal.LOAD_ELEVATED)
    else:
        signals.append(OperationalSignal.LOAD_NORMAL)
    signals.append(OperationalSignal.COORDINATION_ALIGNED if scores.coordination_score >= 65 else OperationalSignal.COORDINATION_DRIFTING)
    signals.append(OperationalSignal.EXECUTIVE_STABLE if scores.executive_score >= 65 else OperationalSignal.EXECUTIVE_UNSTABLE)
    signals.append(OperationalSignal.MEMORY_STABLE if scores.memory_score >= 65 else OperationalSignal.MEMORY_FRAGMENTED)
    signals.append(OperationalSignal.AUTONOMY_STABLE if scores.autonomy_score >= 65 else OperationalSignal.AUTONOMY_DRIFTING)
    if data.recovery_resilience is not None and data.recovery_resilience.mode == RecoveryMode.REBUILD_CONFIDENCE:
        signals.append(OperationalSignal.RECOVERY_PROGRESSING)
    elif data.recovery_resilience is not None and data.recovery_resilience.mode in {RecoveryMode.PAUSED_RECOVERY, RecoveryMode.STABILIZE, RecoveryMode.REDUCE_COMPLEXITY}:
        signals.append(OperationalSignal.RECOVERY_STALLED)
    return tuple(dict.fromkeys(signals))


def render_operational_awareness_markdown(result: OperationalAwarenessResult) -> str:
    """Render operational awareness result as Markdown."""
    lines = [
        "# Autonomous Operational Awareness Engine",
        "",
        "## Operational Status",
        "",
        f"- {result.health_status.value}",
        f"- {result.summary}",
        "",
        "## Operational Confidence",
        "",
        f"- {result.operational_confidence_score}/100",
        "",
        "## Active Signals",
        "",
        *_bullet_lines(tuple(signal.value for signal in result.signals)),
        "",
        "## Detected Risks",
        "",
        *_bullet_lines(tuple(risk.value for risk in result.risks)),
        "",
        "## System Load",
        "",
        f"- {result.system_load_score}/100",
        "",
        "## Coordination Quality",
        "",
        f"- {result.coordination_quality_score}/100",
        "",
        "## Operational Recommendations",
        "",
        *_bullet_lines(tuple(recommendation.value for recommendation in result.recommendations)),
        "",
        "## AGIcore Monitoring State",
        "",
        f"- {result.monitoring_state}",
        "",
        "- Offline only: no broker, no real order, no external ML, no neural training.",
        "",
    ]
    return "\n".join(lines)


def _metrics(data: OperationalAwarenessInput, confidence: OperationalConfidenceScore) -> tuple[OperationalMetric, ...]:
    return (
        OperationalMetric("system_health", confidence.system_health_score, _metric_status(confidence.system_health_score), "Integrity-derived health."),
        OperationalMetric("continuity", confidence.continuity_score, _metric_status(confidence.continuity_score), "Mission continuity capacity."),
        OperationalMetric("recovery", confidence.recovery_score, _metric_status(confidence.recovery_score), "Recovery readiness."),
        OperationalMetric("coordination", confidence.coordination_score, _metric_status(confidence.coordination_score), "Agent and supervisor coordination."),
        OperationalMetric("memory", confidence.memory_score, _metric_status(confidence.memory_score), "Strategic memory stability."),
        OperationalMetric("system_load", _system_load(data, ()), _metric_status(100 - _system_load(data, ())), "Estimated operational load."),
    )


def _mode(
    data: OperationalAwarenessInput,
    confidence: OperationalConfidenceScore,
    risks: tuple[OperationalRisk, ...],
    signals: tuple[OperationalSignal, ...],
    score: int,
) -> OperationalAwarenessMode:
    if score < 30 or data.system_integrity is not None and data.system_integrity.status in {SystemIntegrityStatus.COMPROMISED, SystemIntegrityStatus.PROTECTION_MODE}:
        return OperationalAwarenessMode.CRITICAL
    if len(risks) >= 5:
        return OperationalAwarenessMode.UNSTABLE
    if data.recovery_resilience is not None and data.recovery_resilience.mode == RecoveryMode.REBUILD_CONFIDENCE:
        return OperationalAwarenessMode.RECOVERY_OBSERVATION
    if OperationalRisk.MEMORY_FRAGMENTATION in risks or OperationalRisk.AGENT_COORDINATION_DRIFT in risks:
        return OperationalAwarenessMode.FRAGMENTED
    if OperationalSignal.LOAD_CRITICAL in signals or OperationalSignal.LOAD_ELEVATED in signals:
        return OperationalAwarenessMode.HIGH_LOAD
    if score < 60 or risks:
        return OperationalAwarenessMode.DEGRADED
    if score >= 80 and not risks:
        return OperationalAwarenessMode.OPTIMAL
    return OperationalAwarenessMode.STABLE


def _health(score: int, risks: tuple[OperationalRisk, ...]) -> OperationalHealthStatus:
    if score < 25 or len(risks) >= 6:
        return OperationalHealthStatus.COLLAPSING
    if score < 40 or len(risks) >= 4:
        return OperationalHealthStatus.CRITICAL
    if score < 60 or len(risks) >= 2:
        return OperationalHealthStatus.DEGRADED
    if score < 75 or risks:
        return OperationalHealthStatus.WARNING
    return OperationalHealthStatus.HEALTHY


def _system_load(data: OperationalAwarenessInput, risks: tuple[OperationalRisk, ...]) -> int:
    load = 25
    if data.cognitive_adaptation is not None:
        if data.cognitive_adaptation.load_level == CognitiveLoadLevel.OVERLOADED:
            load += 45
        elif data.cognitive_adaptation.load_level == CognitiveLoadLevel.HIGH:
            load += 30
        elif data.cognitive_adaptation.load_level == CognitiveLoadLevel.MODERATE:
            load += 15
    if data.mission_continuity is not None:
        load += min(25, len(data.mission_continuity.risks) * 5)
    if data.recovery_resilience is not None:
        load += min(25, len(data.recovery_resilience.risks) * 5)
    if data.agent_coordination is not None:
        load += min(20, len(data.agent_coordination.disagreements) * 5)
    load += min(20, len(risks) * 3)
    return _clamp(load)


def _global_confidence(scores: OperationalConfidenceScore, risks: tuple[OperationalRisk, ...]) -> int:
    score = _avg(_score_values(scores))
    score -= 4 * len(risks)
    score -= 5 * sum(1 for risk in risks if risk in _critical_risks())
    return _clamp(score)


def _critical_risks() -> set[OperationalRisk]:
    return {
        OperationalRisk.EXECUTIVE_INSTABILITY,
        OperationalRisk.COGNITIVE_SATURATION,
        OperationalRisk.RECOVERY_STAGNATION,
        OperationalRisk.AUTONOMY_DRIFT,
    }


def _monitoring_state(mode: OperationalAwarenessMode, health: OperationalHealthStatus) -> str:
    if health in {OperationalHealthStatus.CRITICAL, OperationalHealthStatus.COLLAPSING}:
        return "intensive_monitoring_required"
    if mode == OperationalAwarenessMode.RECOVERY_OBSERVATION:
        return "recovery_observation"
    if mode in {OperationalAwarenessMode.DEGRADED, OperationalAwarenessMode.HIGH_LOAD, OperationalAwarenessMode.FRAGMENTED}:
        return "heightened_monitoring"
    return "normal_monitoring"


def _metric_status(value: float) -> OperationalHealthStatus:
    if value < 25:
        return OperationalHealthStatus.COLLAPSING
    if value < 40:
        return OperationalHealthStatus.CRITICAL
    if value < 60:
        return OperationalHealthStatus.DEGRADED
    if value < 75:
        return OperationalHealthStatus.WARNING
    return OperationalHealthStatus.HEALTHY


def _score_values(scores: OperationalConfidenceScore) -> tuple[int, ...]:
    return (
        scores.system_health_score,
        scores.continuity_score,
        scores.recovery_score,
        scores.coordination_score,
        scores.executive_score,
        scores.memory_score,
        scores.cognitive_load_score,
        scores.behavioral_stability_score,
        scores.autonomy_score,
    )


def _avg(values: tuple[int, ...]) -> int:
    return int(round(sum(values) / len(values)))


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _input(awareness_input: OperationalAwarenessInput | None = None, **kwargs: Any) -> OperationalAwarenessInput:
    if awareness_input is not None:
        return awareness_input
    return OperationalAwarenessInput(**kwargs)


def _clamp(value: int | float) -> int:
    return max(0, min(100, int(round(value))))


__all__ = [
    "analyze_operational_signals",
    "build_operational_recommendations",
    "compute_operational_confidence",
    "detect_operational_risks",
    "evaluate_operational_awareness",
    "render_operational_awareness_markdown",
]
