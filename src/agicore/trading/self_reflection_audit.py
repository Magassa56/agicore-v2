"""Offline Autonomous Self-Reflection & Cognitive Audit Engine."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .behavioral_stability_models import BehavioralPressureLevel
from .cognitive_adaptation_models import CognitiveLoadLevel
from .global_orchestrator_models import OrchestratorDecision
from .intent_alignment_models import IntentAlignmentMode
from .learning_governance_models import LearningGovernanceDecision, LearningGovernanceMode
from .meta_cognition_models import CognitiveBias, MetaCognitionMode, MetaCognitiveRisk
from .multi_timeline_simulation_models import TimelineDecision
from .recursive_self_evaluation_models import SelfEvaluationStatus, SystemAutonomyRecommendation
from .recursive_world_model_models import WorldModelDecision, WorldModelRisk
from .scenario_forecast_models import ForecastDecision
from .self_reflection_audit_models import (
    CognitiveAuditEvent,
    CognitiveAuditFinding,
    CognitiveAuditRecommendation,
    CognitiveAuditRisk,
    CognitiveAuditSignal,
    CognitiveAuditTrail,
    ReflectionDepth,
    ReflectionQualityScore,
    ReflectionState,
    SelfReflectionAuditInput,
    SelfReflectionAuditResult,
)
from .strategic_arbitration_models import ArbitrationDecision, ArbitrationMode
from .strategic_memory_models import StrategicDriftSignal


def evaluate_self_reflection_audit(
    audit_input: SelfReflectionAuditInput | None = None,
    **kwargs,
) -> SelfReflectionAuditResult:
    """Run the full offline self-reflection and cognitive audit pipeline."""
    data = _input(audit_input, **kwargs)
    trail = build_cognitive_audit_trail(data)
    signals = detect_cognitive_audit_signals(data, audit_trail=trail)
    risks = detect_cognitive_audit_risks(data, signals=signals, audit_trail=trail)
    quality = compute_reflection_quality(data, signals=signals, risks=risks, audit_trail=trail)
    findings = generate_cognitive_audit_findings(data, signals=signals, risks=risks)
    recommendations = generate_cognitive_audit_recommendations(data, risks=risks, findings=findings, quality=quality)
    state = _reflection_state(quality, risks, signals)
    depth = _reflection_depth(quality, risks, findings)
    score = _overall_quality(quality)
    event = CognitiveAuditEvent(state, depth, f"self-reflection audit state={state.value}", datetime.now(UTC))
    return SelfReflectionAuditResult(
        state,
        depth,
        score,
        quality,
        signals,
        risks,
        findings,
        trail,
        recommendations,
        (event,),
        f"{state.value} with reflection quality {score}/100",
    )


def detect_cognitive_audit_signals(
    audit_input: SelfReflectionAuditInput | None = None,
    *,
    audit_trail: CognitiveAuditTrail | None = None,
    **kwargs,
) -> tuple[CognitiveAuditSignal, ...]:
    """Detect audit signals from compatible offline engines."""
    data = _input(audit_input, **kwargs)
    trail = audit_trail or build_cognitive_audit_trail(data)
    signals: list[CognitiveAuditSignal] = []

    if trail.trace_complete:
        signals.append(CognitiveAuditSignal.DECISION_TRACE_AVAILABLE)
    else:
        signals.append(CognitiveAuditSignal.AUDIT_TRAIL_INCOMPLETE)
    if _reasoning_gap(data):
        signals.append(CognitiveAuditSignal.REASONING_GAP)
    if _strategic_contradiction(data):
        signals.append(CognitiveAuditSignal.STRATEGIC_CONTRADICTION)
    if _behavioral_drift(data):
        signals.append(CognitiveAuditSignal.BEHAVIORAL_DRIFT_DETECTED)
    if _cognitive_bias(data):
        signals.append(CognitiveAuditSignal.COGNITIVE_BIAS_DETECTED)
    if _world_model_inconsistent(data):
        signals.append(CognitiveAuditSignal.WORLD_MODEL_INCONSISTENCY)
    if _orchestration_mismatch(data):
        signals.append(CognitiveAuditSignal.ORCHESTRATION_MISMATCH)
    if _forecast_mismatch(data):
        signals.append(CognitiveAuditSignal.FORECAST_MISMATCH)
    if _self_correction_possible(data):
        signals.append(CognitiveAuditSignal.SELF_CORRECTION_OPPORTUNITY)
    return tuple(dict.fromkeys(signals))


def detect_cognitive_audit_risks(
    audit_input: SelfReflectionAuditInput | None = None,
    *,
    signals: tuple[CognitiveAuditSignal, ...] | None = None,
    audit_trail: CognitiveAuditTrail | None = None,
    **kwargs,
) -> tuple[CognitiveAuditRisk, ...]:
    """Detect cognitive audit risks from signals and trace quality."""
    data = _input(audit_input, **kwargs)
    trail = audit_trail or build_cognitive_audit_trail(data)
    resolved_signals = signals or detect_cognitive_audit_signals(data, audit_trail=trail)
    risks: list[CognitiveAuditRisk] = []

    if CognitiveAuditSignal.REASONING_GAP in resolved_signals:
        risks.append(CognitiveAuditRisk.UNEXPLAINED_DECISION)
    if _repeated_cognitive_error(data):
        risks.append(CognitiveAuditRisk.REPEATED_COGNITIVE_ERROR)
    if CognitiveAuditSignal.STRATEGIC_CONTRADICTION in resolved_signals:
        risks.append(CognitiveAuditRisk.STRATEGIC_SELF_CONTRADICTION)
    if CognitiveAuditSignal.BEHAVIORAL_DRIFT_DETECTED in resolved_signals:
        risks.append(CognitiveAuditRisk.BEHAVIORAL_DECAY)
    if _reflection_failure(data):
        risks.append(CognitiveAuditRisk.REFLECTION_FAILURE)
    if trail.confidence_score < 50 or _audit_confidence(data) < 50:
        risks.append(CognitiveAuditRisk.LOW_AUDIT_CONFIDENCE)
    if CognitiveAuditSignal.WORLD_MODEL_INCONSISTENCY in resolved_signals:
        risks.append(CognitiveAuditRisk.WORLD_MODEL_DRIFT)
    if _meta_cognitive_drift(data):
        risks.append(CognitiveAuditRisk.META_COGNITIVE_DRIFT)
    if not trail.trace_complete:
        risks.append(CognitiveAuditRisk.INCOMPLETE_TRACEABILITY)
    if _self_correction_failure(data):
        risks.append(CognitiveAuditRisk.SELF_CORRECTION_FAILURE)
    return tuple(dict.fromkeys(risks))


def compute_reflection_quality(
    audit_input: SelfReflectionAuditInput | None = None,
    *,
    signals: tuple[CognitiveAuditSignal, ...] | None = None,
    risks: tuple[CognitiveAuditRisk, ...] | None = None,
    audit_trail: CognitiveAuditTrail | None = None,
    **kwargs,
) -> ReflectionQualityScore:
    """Compute reflection quality component scores."""
    data = _input(audit_input, **kwargs)
    trail = audit_trail or build_cognitive_audit_trail(data)
    resolved_signals = signals or detect_cognitive_audit_signals(data, audit_trail=trail)
    resolved_risks = risks or detect_cognitive_audit_risks(data, signals=resolved_signals, audit_trail=trail)
    traceability = trail.confidence_score
    reasoning = _clamp(_meta_score(data) - 12 * _risk_count(resolved_risks, {CognitiveAuditRisk.UNEXPLAINED_DECISION, CognitiveAuditRisk.REPEATED_COGNITIVE_ERROR}))
    strategic = _clamp(_strategy_score(data) - (25 if CognitiveAuditRisk.STRATEGIC_SELF_CONTRADICTION in resolved_risks else 0))
    behavior = _behavior_score(data)
    meta = _meta_score(data)
    world_model = _world_model_score(data)
    correction = _clamp(70 + (10 if CognitiveAuditSignal.SELF_CORRECTION_OPPORTUNITY in resolved_signals else 0) - 25 * _risk_count(resolved_risks, {CognitiveAuditRisk.SELF_CORRECTION_FAILURE, CognitiveAuditRisk.REFLECTION_FAILURE}))
    return ReflectionQualityScore(traceability, reasoning, strategic, behavior, meta, world_model, correction)


def build_cognitive_audit_trail(
    audit_input: SelfReflectionAuditInput | None = None,
    **kwargs,
) -> CognitiveAuditTrail:
    """Build an explainable audit trail across decision layers."""
    data = _input(audit_input, **kwargs)
    expected = (
        ("self_evaluation", data.self_evaluation),
        ("meta_cognition", data.meta_cognition),
        ("world_model", data.recursive_world_model),
        ("forecast", data.scenario_forecast),
        ("multi_timeline", data.multi_timeline),
        ("orchestrator", data.global_orchestrator),
        ("governance", data.learning_governance),
    )
    steps = tuple(name for name, value in expected if value is not None)
    missing = tuple(name for name, value in expected if value is None)
    linked = steps
    confidence = _clamp(100 * len(steps) / len(expected))
    trace_complete = len(missing) <= 2 and "world_model" in steps and "orchestrator" in steps
    return CognitiveAuditTrail(steps, missing, linked, trace_complete, confidence)


def generate_cognitive_audit_findings(
    audit_input: SelfReflectionAuditInput | None = None,
    *,
    signals: tuple[CognitiveAuditSignal, ...] | None = None,
    risks: tuple[CognitiveAuditRisk, ...] | None = None,
    **kwargs,
) -> tuple[CognitiveAuditFinding, ...]:
    """Generate ordered cognitive audit findings."""
    data = _input(audit_input, **kwargs)
    resolved_signals = signals or detect_cognitive_audit_signals(data)
    resolved_risks = risks or detect_cognitive_audit_risks(data, signals=resolved_signals)
    findings: list[CognitiveAuditFinding] = []

    if CognitiveAuditRisk.INCOMPLETE_TRACEABILITY in resolved_risks:
        findings.append(_finding("Incomplete decision trace", 70, (CognitiveAuditSignal.AUDIT_TRAIL_INCOMPLETE,), (CognitiveAuditRisk.INCOMPLETE_TRACEABILITY,), "Audit trail is missing one or more core reasoning layers.", CognitiveAuditRecommendation.REBUILD_DECISION_TRACE))
    if CognitiveAuditRisk.STRATEGIC_SELF_CONTRADICTION in resolved_risks:
        findings.append(_finding("Strategic contradiction", 78, (CognitiveAuditSignal.STRATEGIC_CONTRADICTION,), (CognitiveAuditRisk.STRATEGIC_SELF_CONTRADICTION,), "Strategy, intent, arbitration, or timeline decisions diverge.", CognitiveAuditRecommendation.CORRECT_STRATEGIC_CONFLICT))
    if CognitiveAuditRisk.BEHAVIORAL_DECAY in resolved_risks:
        findings.append(_finding("Behavioral decay", 68, (CognitiveAuditSignal.BEHAVIORAL_DRIFT_DETECTED,), (CognitiveAuditRisk.BEHAVIORAL_DECAY,), "Behavioral stability or strategic memory shows drift.", CognitiveAuditRecommendation.STABILIZE_BEHAVIORAL_BASELINE))
    if CognitiveAuditRisk.WORLD_MODEL_DRIFT in resolved_risks:
        findings.append(_finding("World model drift", 74, (CognitiveAuditSignal.WORLD_MODEL_INCONSISTENCY,), (CognitiveAuditRisk.WORLD_MODEL_DRIFT,), "Recursive world model is inconsistent with downstream decisions.", CognitiveAuditRecommendation.UPDATE_WORLD_MODEL))
    if CognitiveAuditRisk.META_COGNITIVE_DRIFT in resolved_risks:
        findings.append(_finding("Meta-cognitive drift", 72, (CognitiveAuditSignal.COGNITIVE_BIAS_DETECTED,), (CognitiveAuditRisk.META_COGNITIVE_DRIFT,), "Meta-cognition reports bias, contradiction, or degraded reasoning.", CognitiveAuditRecommendation.RECALIBRATE_META_COGNITION))
    if not findings:
        findings.append(_finding("Reflection stable", 15, (CognitiveAuditSignal.DECISION_TRACE_AVAILABLE,), (), "Decision trace is sufficiently coherent for monitoring.", CognitiveAuditRecommendation.CONTINUE_REFLECTION_MONITORING))
    return tuple(sorted(findings, key=lambda finding: finding.severity_score, reverse=True))


def generate_cognitive_audit_recommendations(
    audit_input: SelfReflectionAuditInput | None = None,
    *,
    risks: tuple[CognitiveAuditRisk, ...] | None = None,
    findings: tuple[CognitiveAuditFinding, ...] | None = None,
    quality: ReflectionQualityScore | None = None,
    **kwargs,
) -> tuple[CognitiveAuditRecommendation, ...]:
    """Generate corrective recommendations for the audit result."""
    data = _input(audit_input, **kwargs)
    resolved_risks = risks or detect_cognitive_audit_risks(data)
    resolved_findings = findings or generate_cognitive_audit_findings(data, risks=resolved_risks)
    resolved_quality = quality or compute_reflection_quality(data, risks=resolved_risks)
    recommendations: list[CognitiveAuditRecommendation] = [finding.corrective_action for finding in resolved_findings]

    if len(resolved_risks) >= 3 or _overall_quality(resolved_quality) < 55:
        recommendations.append(CognitiveAuditRecommendation.REQUIRE_DEEP_AUDIT)
    if CognitiveAuditRisk.INCOMPLETE_TRACEABILITY in resolved_risks:
        recommendations.append(CognitiveAuditRecommendation.EXTEND_AUDIT_TRAIL)
    if _overall_quality(resolved_quality) < 50 or CognitiveAuditRisk.REFLECTION_FAILURE in resolved_risks:
        recommendations.append(CognitiveAuditRecommendation.REDUCE_AUTONOMY_DURING_AUDIT)
    if len(resolved_risks) >= 5 or CognitiveAuditRisk.SELF_CORRECTION_FAILURE in resolved_risks:
        recommendations.append(CognitiveAuditRecommendation.REQUIRE_HUMAN_REVIEW)
    recommendations.append(CognitiveAuditRecommendation.CONTINUE_REFLECTION_MONITORING)
    return tuple(dict.fromkeys(recommendations))


def render_self_reflection_audit_markdown(result: SelfReflectionAuditResult) -> str:
    """Render self-reflection audit result as Markdown."""
    lines = [
        "# Autonomous Self-Reflection & Cognitive Audit Engine",
        "",
        "## Self-Reflection State",
        "",
        f"- State: {result.state.value}",
        f"- Depth: {result.depth.value}",
        "",
        "## Reflection Quality",
        "",
        f"- Overall: {result.reflection_quality_score}/100",
        f"- Traceability: {result.quality_breakdown.traceability_score}/100",
        f"- Reasoning coherence: {result.quality_breakdown.reasoning_coherence_score}/100",
        f"- Strategic consistency: {result.quality_breakdown.strategic_consistency_score}/100",
        "",
        "## Audit Signals",
        "",
        *_bullet_lines(tuple(signal.value for signal in result.signals)),
        "",
        "## Audit Risks",
        "",
        *_bullet_lines(tuple(risk.value for risk in result.risks)),
        "",
        "## Cognitive Findings",
        "",
        *_bullet_lines(tuple(f"{finding.title}: {finding.severity_score}/100" for finding in result.findings)),
        "",
        "## Audit Trail",
        "",
        *_bullet_lines(result.audit_trail.steps),
        *_bullet_lines(tuple(f"missing: {step}" for step in result.audit_trail.missing_steps)),
        "",
        "## Recommendations",
        "",
        *_bullet_lines(tuple(recommendation.value for recommendation in result.recommendations)),
        "",
        "## AGIcore Self-Reflection Outlook",
        "",
        result.summary,
    ]
    return "\n".join(lines)


def _input(audit_input: SelfReflectionAuditInput | None = None, **kwargs) -> SelfReflectionAuditInput:
    if audit_input is not None and kwargs:
        raise ValueError("Pass either SelfReflectionAuditInput or keyword inputs, not both")
    if audit_input is not None:
        return audit_input
    return SelfReflectionAuditInput(**kwargs)


def _finding(
    title: str,
    severity: int,
    signals: tuple[CognitiveAuditSignal, ...],
    risks: tuple[CognitiveAuditRisk, ...],
    explanation: str,
    action: CognitiveAuditRecommendation,
) -> CognitiveAuditFinding:
    return CognitiveAuditFinding(title, _clamp(severity), signals, risks, explanation, action)


def _reasoning_gap(data: SelfReflectionAuditInput) -> bool:
    return (
        data.self_evaluation is not None and data.self_evaluation.status in {SelfEvaluationStatus.CONTRADICTORY, SelfEvaluationStatus.REVIEW_REQUIRED}
    ) or (
        data.meta_cognition is not None and data.meta_cognition.mode in {MetaCognitionMode.CONTRADICTORY, MetaCognitionMode.DEGRADED_REASONING}
    )


def _strategic_contradiction(data: SelfReflectionAuditInput) -> bool:
    return (
        data.intent_alignment is not None and data.intent_alignment.mode in {IntentAlignmentMode.PRIORITY_CONFLICT, IntentAlignmentMode.STRATEGIC_DIVERGENCE, IntentAlignmentMode.MISALIGNED, IntentAlignmentMode.CRITICAL_REALIGNMENT}
    ) or (
        data.strategic_arbitration is not None and data.strategic_arbitration.decision in {ArbitrationDecision.EMERGENCY_LOCKDOWN, ArbitrationDecision.STOP_EXECUTION}
        and data.global_orchestrator is not None and data.global_orchestrator.decision == OrchestratorDecision.CONTINUE_COORDINATED_OPERATION
    )


def _behavioral_drift(data: SelfReflectionAuditInput) -> bool:
    return (
        data.behavioral_stability is not None and (_get(data.behavioral_stability, "stability_score", 70) < 50 or _get(data.behavioral_stability, "pressure_level", None) in {BehavioralPressureLevel.HIGH, BehavioralPressureLevel.EXTREME})
    ) or (
        data.strategic_timeline_analysis is not None and StrategicDriftSignal.BEHAVIORAL_DRIFT in _get(data.strategic_timeline_analysis, "drift_signals", ())
    )


def _cognitive_bias(data: SelfReflectionAuditInput) -> bool:
    return data.meta_cognition is not None and (
        bool(data.meta_cognition.biases)
        or CognitiveBias.DECISION_INCONSISTENCY in data.meta_cognition.biases
        or MetaCognitiveRisk.REASONING_DEGRADATION in data.meta_cognition.risks
    )


def _world_model_inconsistent(data: SelfReflectionAuditInput) -> bool:
    return data.recursive_world_model is not None and (
        data.recursive_world_model.world_model_coherence_score < 55
        or WorldModelRisk.WORLD_MODEL_INCOHERENCE in data.recursive_world_model.risks
        or data.recursive_world_model.decision in {WorldModelDecision.REBUILD_CAUSAL_GRAPH, WorldModelDecision.ENTER_WORLD_MODEL_SAFE_MODE}
    )


def _orchestration_mismatch(data: SelfReflectionAuditInput) -> bool:
    return (
        data.global_orchestrator is not None
        and data.strategic_arbitration is not None
        and data.global_orchestrator.decision == OrchestratorDecision.CONTINUE_COORDINATED_OPERATION
        and data.strategic_arbitration.mode == ArbitrationMode.EMERGENCY_LOCKDOWN
    )


def _forecast_mismatch(data: SelfReflectionAuditInput) -> bool:
    return (
        data.scenario_forecast is not None
        and data.multi_timeline is not None
        and data.scenario_forecast.decision == ForecastDecision.CONTINUE_CURRENT_PATH
        and data.multi_timeline.decision in {TimelineDecision.ENTER_TIMELINE_SAFE_MODE, TimelineDecision.REQUIRE_HUMAN_REVIEW}
    )


def _self_correction_possible(data: SelfReflectionAuditInput) -> bool:
    return (
        data.learning_governance is not None and data.learning_governance.decision in {LearningGovernanceDecision.PAUSE_LEARNING, LearningGovernanceDecision.FREEZE_POLICY_UPDATE, LearningGovernanceDecision.REQUIRE_HUMAN_REVIEW}
    ) or (
        data.self_evaluation is not None and data.self_evaluation.autonomy_recommendation in {SystemAutonomyRecommendation.REDUCE_AUTONOMY, SystemAutonomyRecommendation.RECALIBRATE_SYSTEM}
    )


def _repeated_cognitive_error(data: SelfReflectionAuditInput) -> bool:
    return data.meta_cognition is not None and len(data.meta_cognition.biases) >= 1 and (
        len(data.meta_cognition.risks) >= 1
        or data.meta_cognition.mode in {MetaCognitionMode.RECALIBRATION_REQUIRED, MetaCognitionMode.DEGRADED_REASONING}
    )


def _reflection_failure(data: SelfReflectionAuditInput) -> bool:
    return data.self_evaluation is not None and data.self_evaluation.status in {SelfEvaluationStatus.UNSTABLE, SelfEvaluationStatus.CONTRADICTORY}


def _meta_cognitive_drift(data: SelfReflectionAuditInput) -> bool:
    return data.meta_cognition is not None and (
        data.meta_cognition.confidence_score < 50
        or data.meta_cognition.mode in {MetaCognitionMode.RECALIBRATION_REQUIRED, MetaCognitionMode.DEGRADED_REASONING}
    )


def _self_correction_failure(data: SelfReflectionAuditInput) -> bool:
    return (
        data.learning_governance is not None and data.learning_governance.mode == LearningGovernanceMode.SAFETY_LOCKDOWN
    ) and (
        data.self_evaluation is not None and data.self_evaluation.autonomy_recommendation == SystemAutonomyRecommendation.FREEZE_AUTONOMY
    )


def _audit_confidence(data: SelfReflectionAuditInput) -> int:
    values = []
    if data.self_evaluation is not None:
        values.append(data.self_evaluation.confidence_score)
    if data.meta_cognition is not None:
        values.append(data.meta_cognition.confidence_score)
    if data.recursive_world_model is not None:
        values.append(data.recursive_world_model.world_model_coherence_score)
    return _avg(values, 45 if _evidence_count(data) < 3 else 65)


def _meta_score(data: SelfReflectionAuditInput) -> int:
    if data.meta_cognition is not None:
        score = data.meta_cognition.reasoning_stability_score
        if data.meta_cognition.mode in {MetaCognitionMode.CONTRADICTORY, MetaCognitionMode.DEGRADED_REASONING, MetaCognitionMode.RECALIBRATION_REQUIRED}:
            score -= 20
        return _clamp(score)
    if data.cognitive_adaptation is not None:
        score = data.cognitive_adaptation.global_score
        if data.cognitive_adaptation.load_level == CognitiveLoadLevel.OVERLOADED:
            score -= 25
        return _clamp(score)
    return 65


def _strategy_score(data: SelfReflectionAuditInput) -> int:
    values = []
    if data.intent_alignment is not None:
        values.append(_get(data.intent_alignment, "alignment_confidence", 65))
    if data.strategic_timeline_analysis is not None:
        values.append(_get(data.strategic_timeline_analysis, "strategic_health_score", 65))
    if data.collective_consensus is not None:
        values.append(_get(data.collective_consensus, "collective_confidence_score", 65))
    return _avg(values, 65)


def _behavior_score(data: SelfReflectionAuditInput) -> int:
    if data.behavioral_stability is None:
        return 65
    score = _get(data.behavioral_stability, "stability_score", 65)
    if _get(data.behavioral_stability, "pressure_level", None) in {BehavioralPressureLevel.HIGH, BehavioralPressureLevel.EXTREME}:
        score -= 20
    return _clamp(score)


def _world_model_score(data: SelfReflectionAuditInput) -> int:
    if data.recursive_world_model is None:
        return 60
    score = data.recursive_world_model.world_model_coherence_score
    if data.recursive_world_model.decision in {WorldModelDecision.ENTER_WORLD_MODEL_SAFE_MODE, WorldModelDecision.FREEZE_RECURSIVE_UPDATES}:
        score -= 20
    return _clamp(score)


def _reflection_state(
    quality: ReflectionQualityScore,
    risks: tuple[CognitiveAuditRisk, ...],
    signals: tuple[CognitiveAuditSignal, ...],
) -> ReflectionState:
    score = _overall_quality(quality)
    if CognitiveAuditRisk.SELF_CORRECTION_FAILURE in risks or len(risks) >= 6:
        return ReflectionState.CRITICAL_REVIEW
    if CognitiveAuditSignal.SELF_CORRECTION_OPPORTUNITY in signals and risks:
        return ReflectionState.SELF_CORRECTION_NEEDED
    if CognitiveAuditRisk.STRATEGIC_SELF_CONTRADICTION in risks:
        return ReflectionState.CONTRADICTORY_REFLECTION
    if score < 45:
        return ReflectionState.AUDIT_REQUIRED
    if score < 60:
        return ReflectionState.DEGRADED_REFLECTION
    if score < 75:
        return ReflectionState.PARTIAL_REFLECTION
    return ReflectionState.CLEAR_REFLECTION


def _reflection_depth(
    quality: ReflectionQualityScore,
    risks: tuple[CognitiveAuditRisk, ...],
    findings: tuple[CognitiveAuditFinding, ...],
) -> ReflectionDepth:
    score = _overall_quality(quality)
    max_severity = max((finding.severity_score for finding in findings), default=0)
    if len(risks) >= 5 or max_severity >= 85:
        return ReflectionDepth.CRITICAL
    if CognitiveAuditRisk.WORLD_MODEL_DRIFT in risks or CognitiveAuditRisk.META_COGNITIVE_DRIFT in risks:
        return ReflectionDepth.RECURSIVE
    if len(risks) >= 3 or score < 60:
        return ReflectionDepth.DEEP
    if risks:
        return ReflectionDepth.STANDARD
    return ReflectionDepth.SHALLOW


def _overall_quality(score: ReflectionQualityScore) -> int:
    return _avg(
        [
            score.traceability_score,
            score.reasoning_coherence_score,
            score.strategic_consistency_score,
            score.behavioral_awareness_score,
            score.meta_cognitive_score,
            score.world_model_alignment_score,
            score.self_correction_readiness_score,
        ],
        50,
    )


def _risk_count(risks: tuple[CognitiveAuditRisk, ...], selected: set[CognitiveAuditRisk]) -> int:
    return len(selected.intersection(risks))


def _evidence_count(data: SelfReflectionAuditInput) -> int:
    return sum(
        value is not None
        for value in (
            data.recursive_world_model,
            data.global_orchestrator,
            data.meta_cognition,
            data.cognitive_adaptation,
            data.behavioral_stability,
            data.strategic_timeline_analysis,
            data.scenario_forecast,
            data.multi_timeline,
            data.intent_alignment,
            data.strategic_arbitration,
            data.collective_consensus,
            data.learning_governance,
            data.self_evaluation,
        )
    )


def _avg(values: list[int], default: int) -> int:
    if not values:
        return default
    return _clamp(sum(values) / len(values))


def _get(obj: Any, name: str, default: Any = None) -> Any:
    return getattr(obj, name, default) if obj is not None else default


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _clamp(value: float, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(round(value))))


__all__ = [
    "build_cognitive_audit_trail",
    "compute_reflection_quality",
    "detect_cognitive_audit_risks",
    "detect_cognitive_audit_signals",
    "evaluate_self_reflection_audit",
    "generate_cognitive_audit_findings",
    "generate_cognitive_audit_recommendations",
    "render_self_reflection_audit_markdown",
]
