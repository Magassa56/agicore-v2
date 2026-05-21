"""Offline Autonomous Meta-Cognition Engine for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .behavioral_stability_models import BehavioralPressureLevel
from .cognitive_adaptation_models import CognitiveAdaptationMode, CognitiveLoadLevel
from .executive_brain_models import ExecutiveMode
from .hierarchical_supervisor_models import SupervisorDecision, SupervisorOverride
from .learning_governance_models import LearningGovernanceDecision, LearningGovernanceMode
from .meta_cognition_models import (
    CognitiveBias,
    CognitiveContradiction,
    CognitiveRigidity,
    MetaCognitionInput,
    MetaCognitionMode,
    MetaCognitionResult,
    MetaCognitiveConfidence,
    MetaCognitiveEvent,
    MetaCognitiveRecommendation,
    MetaCognitiveRisk,
    MetaCognitiveSignal,
)
from .multi_agent_models import AgentConsensusStatus, AgentVote
from .operational_awareness_models import OperationalAwarenessMode, OperationalHealthStatus, OperationalRisk
from .recursive_self_evaluation_models import SelfEvaluationStatus, SystemAutonomyRecommendation
from .strategic_memory_models import StrategicDriftSignal
from .system_integrity_models import SystemIntegrityStatus


def evaluate_meta_cognition(
    meta_input: MetaCognitionInput | None = None,
    **kwargs,
) -> MetaCognitionResult:
    """Evaluate reasoning quality, bias, contradiction and recalibration needs."""
    data = _input(meta_input, **kwargs)
    confidence = compute_meta_cognitive_confidence(data)
    rigidity = _rigidity(data, confidence)
    biases = detect_cognitive_biases(data, confidence=confidence, rigidity=rigidity)
    contradictions = _contradictions(data, confidence)
    stability = analyze_reasoning_stability(data, confidence=confidence, biases=biases, contradictions=contradictions)
    risks = detect_meta_cognitive_risks(data, confidence=confidence, biases=biases, contradictions=contradictions, stability_score=stability)
    signals = _signals(confidence, rigidity, biases, contradictions, risks, stability)
    score = _global_confidence(confidence, risks, biases, contradictions)
    mode = _mode(score, rigidity, biases, contradictions, risks)
    recommendations = build_meta_cognitive_recommendations(data, risks=risks, biases=biases, contradictions=contradictions, mode=mode)
    event = MetaCognitiveEvent(
        mode=mode,
        message=f"Meta-cognition {mode.value}; confidence {score}/100.",
        timestamp=datetime.now(UTC),
    )
    return MetaCognitionResult(
        mode=mode,
        confidence_score=score,
        confidence_breakdown=confidence,
        rigidity=rigidity,
        biases=biases,
        contradictions=contradictions,
        signals=signals,
        risks=risks,
        recommendations=recommendations,
        reasoning_stability_score=stability,
        reflective_state=_reflective_state(mode, risks),
        events=(event,),
        summary=f"Meta-cognitive mode {mode.value} with confidence {score}/100 and {len(biases)} bias(es).",
    )


def detect_cognitive_biases(
    meta_input: MetaCognitionInput | None = None,
    *,
    confidence: MetaCognitiveConfidence | None = None,
    rigidity: CognitiveRigidity | None = None,
    **kwargs,
) -> tuple[CognitiveBias, ...]:
    """Detect cognitive biases from cross-layer evidence."""
    data = _input(meta_input, **kwargs)
    resolved_confidence = confidence or compute_meta_cognitive_confidence(data)
    resolved_rigidity = rigidity or _rigidity(data, resolved_confidence)
    biases: list[CognitiveBias] = []

    if (
        data.operational_awareness is not None
        and data.operational_awareness.operational_confidence_score >= 75
        and (
            data.operational_awareness.health_status in {OperationalHealthStatus.CRITICAL, OperationalHealthStatus.COLLAPSING}
            or len(data.operational_awareness.risks) >= 3
        )
    ):
        biases.append(CognitiveBias.OVERCONFIDENCE)
    if (
        data.self_evaluation is not None
        and data.self_evaluation.confidence_score >= 75
        and data.supervisor_result is not None
        and not data.supervisor_result.final_executable
    ):
        biases.append(CognitiveBias.OVERCONFIDENCE)
    if data.agent_coordination is not None and data.agent_coordination.consensus_status == AgentConsensusStatus.NO_CONSENSUS:
        biases.append(CognitiveBias.CONFIRMATION_BIAS)
        biases.append(CognitiveBias.DECISION_INCONSISTENCY)
    if data.executive_result is not None and data.executive_result.state.mode in {ExecutiveMode.SURVIVAL, ExecutiveMode.PAUSED}:
        biases.append(CognitiveBias.REACTIONARY_DECISION)
    if resolved_rigidity in {CognitiveRigidity.RIGID, CognitiveRigidity.LOCKED}:
        biases.append(CognitiveBias.STRATEGIC_RIGIDITY)
    if data.strategic_timeline_analysis is not None and data.strategic_timeline_analysis.snapshots_count <= 1:
        biases.append(CognitiveBias.RECENCY_BIAS)
    if data.learning_governance is not None and data.learning_governance.mode == LearningGovernanceMode.EXPLOIT_ONLY and data.strategic_timeline_analysis is not None and data.strategic_timeline_analysis.degradation_detected:
        biases.append(CognitiveBias.FEEDBACK_IGNORANCE)
    if data.operational_awareness is not None and (
        data.operational_awareness.mode == OperationalAwarenessMode.FRAGMENTED
        or OperationalRisk.MEMORY_FRAGMENTATION in data.operational_awareness.risks
    ):
        biases.append(CognitiveBias.COGNITIVE_FRAGMENTATION)
    if data.self_evaluation is not None and data.self_evaluation.autonomy_recommendation == SystemAutonomyRecommendation.MAINTAIN_AUTONOMY and resolved_confidence.autonomy_calibration_score < 55:
        biases.append(CognitiveBias.EXCESSIVE_AUTONOMY)
    if data.strategic_timeline_analysis is not None and (
        data.strategic_timeline_analysis.degradation_detected
        or StrategicDriftSignal.STRATEGIC_DEGRADATION in data.strategic_timeline_analysis.drift_signals
    ):
        biases.append(CognitiveBias.REASONING_DRIFT)

    return tuple(dict.fromkeys(biases))


def detect_meta_cognitive_risks(
    meta_input: MetaCognitionInput | None = None,
    *,
    confidence: MetaCognitiveConfidence | None = None,
    biases: tuple[CognitiveBias, ...] | None = None,
    contradictions: tuple[CognitiveContradiction, ...] | None = None,
    stability_score: int | None = None,
    **kwargs,
) -> tuple[MetaCognitiveRisk, ...]:
    """Detect risks that degrade meta-cognitive reasoning."""
    data = _input(meta_input, **kwargs)
    resolved_confidence = confidence or compute_meta_cognitive_confidence(data)
    resolved_biases = biases or detect_cognitive_biases(data, confidence=resolved_confidence)
    resolved_contradictions = contradictions or _contradictions(data, resolved_confidence)
    stability = stability_score if stability_score is not None else analyze_reasoning_stability(data, confidence=resolved_confidence, biases=resolved_biases, contradictions=resolved_contradictions)
    risks: list[MetaCognitiveRisk] = []

    if resolved_contradictions:
        risks.append(MetaCognitiveRisk.LOGICAL_INSTABILITY)
    if CognitiveContradiction.EXECUTIVE_SUPERVISOR_DIVERGENCE in resolved_contradictions or CognitiveContradiction.STRATEGY_GOVERNANCE_MISMATCH in resolved_contradictions:
        risks.append(MetaCognitiveRisk.STRATEGIC_CONTRADICTION)
    if data.cognitive_adaptation is not None and data.cognitive_adaptation.load_level == CognitiveLoadLevel.OVERLOADED:
        risks.append(MetaCognitiveRisk.COGNITIVE_COLLAPSE)
    if resolved_confidence.self_awareness_score < 45 or resolved_confidence.reasoning_stability_score < 45:
        risks.append(MetaCognitiveRisk.META_CONFIDENCE_FAILURE)
    if stability < 50 or len(resolved_biases) >= 4:
        risks.append(MetaCognitiveRisk.REASONING_DEGRADATION)
    if CognitiveBias.EXCESSIVE_AUTONOMY in resolved_biases or (
        data.self_evaluation is not None and data.self_evaluation.autonomy_recommendation == SystemAutonomyRecommendation.MAINTAIN_AUTONOMY and resolved_contradictions
    ):
        risks.append(MetaCognitiveRisk.AUTONOMY_OVEREXPANSION)
    if CognitiveBias.FEEDBACK_IGNORANCE in resolved_biases:
        risks.append(MetaCognitiveRisk.FEEDBACK_DISCONNECTION)
    if len(resolved_contradictions) >= 3 or CognitiveBias.DECISION_INCONSISTENCY in resolved_biases:
        risks.append(MetaCognitiveRisk.DECISION_CHAOS)
    if data.self_evaluation is not None and data.self_evaluation.status in {SelfEvaluationStatus.CONTRADICTORY, SelfEvaluationStatus.UNSTABLE}:
        risks.append(MetaCognitiveRisk.SELF_EVALUATION_DRIFT)
    if len(resolved_contradictions) >= 2 and data.system_integrity is not None and data.system_integrity.status in {SystemIntegrityStatus.COMPROMISED, SystemIntegrityStatus.PROTECTION_MODE}:
        risks.append(MetaCognitiveRisk.RECALIBRATION_FAILURE)

    return tuple(dict.fromkeys(risks))


def compute_meta_cognitive_confidence(
    meta_input: MetaCognitionInput | None = None,
    **kwargs,
) -> MetaCognitiveConfidence:
    """Compute meta-cognitive confidence component scores from 0..100."""
    data = _input(meta_input, **kwargs)
    reasoning = 80
    self_awareness = 80
    contradiction = 80
    bias = 80
    strategic = 80
    feedback = 80
    autonomy = 80

    if data.self_evaluation is not None:
        self_awareness = data.self_evaluation.confidence_score
        autonomy = data.self_evaluation.score_breakdown.autonomy_readiness_score
        if data.self_evaluation.status == SelfEvaluationStatus.CONTRADICTORY:
            reasoning -= 25
            contradiction -= 30
            self_awareness -= 20
        elif data.self_evaluation.status in {SelfEvaluationStatus.UNSTABLE, SelfEvaluationStatus.DEGRADED}:
            reasoning -= 12
            self_awareness -= 10

    if data.operational_awareness is not None:
        reasoning = min(reasoning, data.operational_awareness.operational_confidence_score)
        if data.operational_awareness.mode in {OperationalAwarenessMode.CRITICAL, OperationalAwarenessMode.UNSTABLE, OperationalAwarenessMode.FRAGMENTED}:
            reasoning -= 15
            bias -= 10

    if data.cognitive_adaptation is not None:
        reasoning = min(reasoning, data.cognitive_adaptation.global_score)
        if data.cognitive_adaptation.load_level == CognitiveLoadLevel.OVERLOADED:
            reasoning -= 25
            bias -= 15
        elif data.cognitive_adaptation.load_level == CognitiveLoadLevel.HIGH:
            reasoning -= 10

        flexibility = data.cognitive_adaptation.flexibility_score
        strategic = min(strategic, flexibility.strategic_clarity_score)
        feedback = min(feedback, flexibility.recovery_learning_score)
        bias = min(bias, flexibility.decision_flexibility_score)

    if data.strategic_timeline_analysis is not None:
        strategic = min(strategic, data.strategic_timeline_analysis.strategic_health_score)
        if data.strategic_timeline_analysis.degradation_detected:
            strategic -= 20
            feedback -= 10

    if data.agent_coordination is not None:
        contradiction = min(contradiction, data.agent_coordination.consensus_score)
        contradiction -= min(20, len(data.agent_coordination.disagreements) * 5)
        if data.agent_coordination.consensus_status == AgentConsensusStatus.NO_CONSENSUS:
            contradiction -= 15

    if data.supervisor_result is not None:
        if not data.supervisor_result.final_executable:
            contradiction -= 20
        if data.supervisor_result.conflicts_detected:
            contradiction -= min(25, len(data.supervisor_result.conflicts_detected) * 6)

    if data.learning_governance is not None:
        if data.learning_governance.mode in {LearningGovernanceMode.SAFETY_LOCKDOWN, LearningGovernanceMode.FREEZE_LEARNING}:
            autonomy -= 20
            feedback -= 10
        if data.learning_governance.decision == LearningGovernanceDecision.ALLOW_LEARNING and data.system_integrity is not None and data.system_integrity.status in {SystemIntegrityStatus.COMPROMISED, SystemIntegrityStatus.PROTECTION_MODE}:
            contradiction -= 20

    if data.behavioral_stability is not None and data.behavioral_stability.pressure_level == BehavioralPressureLevel.EXTREME:
        reasoning -= 10

    return MetaCognitiveConfidence(
        reasoning_stability_score=_clamp(reasoning),
        self_awareness_score=_clamp(self_awareness),
        contradiction_resistance_score=_clamp(contradiction),
        bias_resistance_score=_clamp(bias),
        strategic_alignment_score=_clamp(strategic),
        feedback_integration_score=_clamp(feedback),
        autonomy_calibration_score=_clamp(autonomy),
    )


def analyze_reasoning_stability(
    meta_input: MetaCognitionInput | None = None,
    *,
    confidence: MetaCognitiveConfidence | None = None,
    biases: tuple[CognitiveBias, ...] | None = None,
    contradictions: tuple[CognitiveContradiction, ...] | None = None,
    **kwargs,
) -> int:
    """Analyze reasoning stability as a normalized score."""
    data = _input(meta_input, **kwargs)
    resolved_confidence = confidence or compute_meta_cognitive_confidence(data)
    resolved_biases = biases or detect_cognitive_biases(data, confidence=resolved_confidence)
    resolved_contradictions = contradictions or _contradictions(data, resolved_confidence)
    score = _avg(
        (
            resolved_confidence.reasoning_stability_score,
            resolved_confidence.contradiction_resistance_score,
            resolved_confidence.bias_resistance_score,
            resolved_confidence.strategic_alignment_score,
        )
    )
    score -= min(30, len(resolved_biases) * 4)
    score -= min(35, len(resolved_contradictions) * 8)
    if data.system_integrity is not None and data.system_integrity.status in {SystemIntegrityStatus.COMPROMISED, SystemIntegrityStatus.PROTECTION_MODE}:
        score -= 10
    return _clamp(score)


def build_meta_cognitive_recommendations(
    meta_input: MetaCognitionInput | None = None,
    *,
    risks: tuple[MetaCognitiveRisk, ...] | None = None,
    biases: tuple[CognitiveBias, ...] | None = None,
    contradictions: tuple[CognitiveContradiction, ...] | None = None,
    mode: MetaCognitionMode | None = None,
    **kwargs,
) -> tuple[MetaCognitiveRecommendation, ...]:
    """Build ordered recommendations for reasoning quality controls."""
    data = _input(meta_input, **kwargs)
    confidence = compute_meta_cognitive_confidence(data)
    resolved_biases = biases or detect_cognitive_biases(data, confidence=confidence)
    resolved_contradictions = contradictions or _contradictions(data, confidence)
    resolved_risks = risks or detect_meta_cognitive_risks(data, confidence=confidence, biases=resolved_biases, contradictions=resolved_contradictions)
    resolved_mode = mode or _mode(_global_confidence(confidence, resolved_risks, resolved_biases, resolved_contradictions), _rigidity(data, confidence), resolved_biases, resolved_contradictions, resolved_risks)
    recommendations: list[MetaCognitiveRecommendation] = []

    if resolved_mode in {MetaCognitionMode.RECALIBRATION_REQUIRED, MetaCognitionMode.CONTRADICTORY}:
        recommendations.append(MetaCognitiveRecommendation.RECALIBRATE_REASONING)
        recommendations.append(MetaCognitiveRecommendation.ENTER_SAFE_REASONING_MODE)
    if resolved_contradictions:
        recommendations.append(MetaCognitiveRecommendation.REBUILD_LOGICAL_STABILITY)
        recommendations.append(MetaCognitiveRecommendation.REQUIRE_SUPERVISION)
    if CognitiveBias.OVERCONFIDENCE in resolved_biases or CognitiveBias.EXCESSIVE_AUTONOMY in resolved_biases:
        recommendations.append(MetaCognitiveRecommendation.REDUCE_AUTONOMY)
        recommendations.append(MetaCognitiveRecommendation.FREEZE_DECISION_EXPANSION)
    if CognitiveBias.STRATEGIC_RIGIDITY in resolved_biases or CognitiveBias.REASONING_DRIFT in resolved_biases:
        recommendations.append(MetaCognitiveRecommendation.REVIEW_STRATEGIC_ALIGNMENT)
    if resolved_risks:
        recommendations.append(MetaCognitiveRecommendation.INCREASE_REFLECTION)
        recommendations.append(MetaCognitiveRecommendation.STABILIZE_REASONING)
    if not recommendations:
        recommendations.append(MetaCognitiveRecommendation.CONTINUE_MONITORING)
    else:
        recommendations.append(MetaCognitiveRecommendation.CONTINUE_MONITORING)
    return tuple(dict.fromkeys(recommendations))


def render_meta_cognition_markdown(result: MetaCognitionResult) -> str:
    """Render meta-cognitive assessment as Markdown."""
    lines = [
        "# Autonomous Meta-Cognition Engine",
        "",
        "## Meta-Cognitive State",
        "",
        f"- {result.mode.value}",
        f"- {result.summary}",
        "",
        "## Reasoning Stability",
        "",
        f"- {result.reasoning_stability_score}/100",
        "",
        "## Detected Biases",
        "",
        *_bullet_lines(tuple(bias.value for bias in result.biases)),
        "",
        "## Cognitive Contradictions",
        "",
        *_bullet_lines(tuple(contradiction.value for contradiction in result.contradictions)),
        "",
        "## Meta-Cognitive Risks",
        "",
        *_bullet_lines(tuple(risk.value for risk in result.risks)),
        "",
        "## Confidence Score",
        "",
        f"- {result.confidence_score}/100",
        "",
        "## Recommendations",
        "",
        *_bullet_lines(tuple(recommendation.value for recommendation in result.recommendations)),
        "",
        "## AGIcore Reflective State",
        "",
        f"- {result.reflective_state}",
        "",
        "- Offline only: no broker, no real order, no external ML, no neural training.",
        "",
    ]
    return "\n".join(lines)


def _contradictions(
    data: MetaCognitionInput,
    confidence: MetaCognitiveConfidence,
) -> tuple[CognitiveContradiction, ...]:
    contradictions: list[CognitiveContradiction] = []
    if (
        data.executive_result is not None
        and data.executive_result.decision.allow_execution
        and data.supervisor_result is not None
        and not data.supervisor_result.final_executable
    ):
        contradictions.append(CognitiveContradiction.EXECUTIVE_SUPERVISOR_DIVERGENCE)
    if data.self_evaluation is not None and data.self_evaluation.status == SelfEvaluationStatus.CONTRADICTORY:
        contradictions.append(CognitiveContradiction.SELF_EVALUATION_CONTRADICTION)
    if (
        data.operational_awareness is not None
        and data.operational_awareness.operational_confidence_score >= 75
        and data.operational_awareness.health_status in {OperationalHealthStatus.CRITICAL, OperationalHealthStatus.COLLAPSING}
    ):
        contradictions.append(CognitiveContradiction.AWARENESS_CONFIDENCE_MISMATCH)
    if (
        data.learning_governance is not None
        and data.learning_governance.decision == LearningGovernanceDecision.ALLOW_LEARNING
        and data.system_integrity is not None
        and data.system_integrity.status in {SystemIntegrityStatus.COMPROMISED, SystemIntegrityStatus.PROTECTION_MODE}
    ):
        contradictions.append(CognitiveContradiction.STRATEGY_GOVERNANCE_MISMATCH)
    if (
        data.agent_coordination is not None
        and data.agent_coordination.final_vote in {AgentVote.BLOCK, AgentVote.STOP_SESSION}
        and data.supervisor_result is not None
        and data.supervisor_result.final_executable
    ):
        contradictions.append(CognitiveContradiction.AGENT_SUPERVISOR_MISMATCH)
    if (
        data.strategic_timeline_analysis is not None
        and data.strategic_timeline_analysis.degradation_detected
        and confidence.strategic_alignment_score >= 70
    ):
        contradictions.append(CognitiveContradiction.MEMORY_REASONING_MISMATCH)
    return tuple(dict.fromkeys(contradictions))


def _rigidity(data: MetaCognitionInput, confidence: MetaCognitiveConfidence) -> CognitiveRigidity:
    score = confidence.bias_resistance_score
    if data.cognitive_adaptation is not None:
        flex = data.cognitive_adaptation.flexibility_score
        score = min(score, flex.decision_flexibility_score, flex.context_adaptation_score, flex.policy_adaptation_score)
        if data.cognitive_adaptation.adaptation_mode in {CognitiveAdaptationMode.PAUSE, CognitiveAdaptationMode.RECOVER}:
            score -= 10
    if score < 25:
        return CognitiveRigidity.LOCKED
    if score < 45:
        return CognitiveRigidity.RIGID
    if score < 65:
        return CognitiveRigidity.SOMEWHAT_RIGID
    return CognitiveRigidity.FLEXIBLE


def _signals(
    confidence: MetaCognitiveConfidence,
    rigidity: CognitiveRigidity,
    biases: tuple[CognitiveBias, ...],
    contradictions: tuple[CognitiveContradiction, ...],
    risks: tuple[MetaCognitiveRisk, ...],
    stability: int,
) -> tuple[MetaCognitiveSignal, ...]:
    signals: list[MetaCognitiveSignal] = []
    signals.append(MetaCognitiveSignal.REASONING_STABLE if stability >= 70 and not contradictions else MetaCognitiveSignal.REASONING_UNSTABLE)
    signals.append(MetaCognitiveSignal.SELF_AWARENESS_STRONG if confidence.self_awareness_score >= 70 else MetaCognitiveSignal.SELF_AWARENESS_WEAK)
    if contradictions:
        signals.append(MetaCognitiveSignal.CONTRADICTION_DETECTED)
    if biases:
        signals.append(MetaCognitiveSignal.BIAS_DETECTED)
    if rigidity in {CognitiveRigidity.RIGID, CognitiveRigidity.LOCKED}:
        signals.append(MetaCognitiveSignal.RIGIDITY_DETECTED)
    signals.append(MetaCognitiveSignal.FEEDBACK_CONNECTED if confidence.feedback_integration_score >= 60 else MetaCognitiveSignal.FEEDBACK_DISCONNECTED)
    if risks:
        signals.append(MetaCognitiveSignal.REFLECTION_NEEDED)
    if MetaCognitiveRisk.RECALIBRATION_FAILURE in risks or len(risks) >= 4:
        signals.append(MetaCognitiveSignal.RECALIBRATION_NEEDED)
    return tuple(dict.fromkeys(signals))


def _mode(
    score: int,
    rigidity: CognitiveRigidity,
    biases: tuple[CognitiveBias, ...],
    contradictions: tuple[CognitiveContradiction, ...],
    risks: tuple[MetaCognitiveRisk, ...],
) -> MetaCognitionMode:
    if MetaCognitiveRisk.RECALIBRATION_FAILURE in risks or len(risks) >= 5:
        return MetaCognitionMode.RECALIBRATION_REQUIRED
    if contradictions:
        return MetaCognitionMode.CONTRADICTORY
    if score < 40 or MetaCognitiveRisk.COGNITIVE_COLLAPSE in risks:
        return MetaCognitionMode.DEGRADED_REASONING
    if rigidity in {CognitiveRigidity.RIGID, CognitiveRigidity.LOCKED}:
        return MetaCognitionMode.RIGID
    if CognitiveBias.OVERCONFIDENCE in biases:
        return MetaCognitionMode.OVERCONFIDENT
    if score < 60 or risks:
        return MetaCognitionMode.UNCERTAIN
    if biases:
        return MetaCognitionMode.REFLECTIVE
    return MetaCognitionMode.SELF_AWARE


def _global_confidence(
    confidence: MetaCognitiveConfidence,
    risks: tuple[MetaCognitiveRisk, ...],
    biases: tuple[CognitiveBias, ...],
    contradictions: tuple[CognitiveContradiction, ...],
) -> int:
    score = _avg(
        (
            confidence.reasoning_stability_score,
            confidence.self_awareness_score,
            confidence.contradiction_resistance_score,
            confidence.bias_resistance_score,
            confidence.strategic_alignment_score,
            confidence.feedback_integration_score,
            confidence.autonomy_calibration_score,
        )
    )
    score -= min(25, len(biases) * 3)
    score -= min(35, len(contradictions) * 8)
    score -= min(35, len(risks) * 5)
    return _clamp(score)


def _reflective_state(mode: MetaCognitionMode, risks: tuple[MetaCognitiveRisk, ...]) -> str:
    if mode == MetaCognitionMode.SELF_AWARE:
        return "self_aware_monitoring"
    if mode == MetaCognitionMode.RECALIBRATION_REQUIRED:
        return "recalibration_required"
    if risks:
        return "reflection_required"
    return "reflective_monitoring"


def _avg(values: tuple[int, ...]) -> int:
    return int(round(sum(values) / len(values)))


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _input(meta_input: MetaCognitionInput | None = None, **kwargs: Any) -> MetaCognitionInput:
    if meta_input is not None:
        return meta_input
    return MetaCognitionInput(**kwargs)


def _clamp(value: int | float) -> int:
    return max(0, min(100, int(round(value))))


__all__ = [
    "analyze_reasoning_stability",
    "build_meta_cognitive_recommendations",
    "compute_meta_cognitive_confidence",
    "detect_cognitive_biases",
    "detect_meta_cognitive_risks",
    "evaluate_meta_cognition",
    "render_meta_cognition_markdown",
]
