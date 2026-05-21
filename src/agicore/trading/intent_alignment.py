"""Offline Autonomous Intent Alignment Engine for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .executive_brain_models import ExecutiveIntent, ExecutiveMode, ExecutiveRiskAppetite
from .hierarchical_supervisor_models import SupervisorDecision
from .intent_alignment_models import (
    IntentAlignmentInput,
    IntentAlignmentMode,
    IntentAlignmentResult,
    IntentAlignmentState,
    IntentAlignmentEvent,
    IntentConfidence,
    IntentConflict,
    IntentDrift,
    IntentPriority,
    IntentRecommendation,
    IntentRisk,
)
from .learning_governance_models import LearningGovernanceDecision, LearningGovernanceMode
from .meta_cognition_models import MetaCognitionMode, MetaCognitiveRisk
from .mission_continuity_models import MissionContinuityMode
from .operational_awareness_models import OperationalAwarenessMode, OperationalHealthStatus, OperationalRisk
from .recursive_self_evaluation_models import SelfEvaluationStatus, SystemAutonomyRecommendation
from .strategic_planning_models import StrategicObjective, StrategicPlanStatus
from .system_integrity_models import SystemIntegrityStatus


def evaluate_intent_alignment(
    alignment_input: IntentAlignmentInput | None = None,
    **kwargs,
) -> IntentAlignmentResult:
    """Evaluate mission, safety, priority and autonomy alignment offline."""
    data = _input(alignment_input, **kwargs)
    confidence = compute_alignment_confidence(data)
    drifts = detect_alignment_drifts(data, confidence=confidence)
    conflicts = detect_intent_conflicts(data, confidence=confidence, drifts=drifts)
    priority_stability = analyze_priority_stability(data, conflicts=conflicts, drifts=drifts)
    risks = _risks(data, confidence, conflicts, drifts, priority_stability)
    score = _global_confidence(confidence, conflicts, drifts, risks)
    mode = _mode(score, conflicts, drifts, risks)
    state = _state(mode, score, conflicts, risks)
    recommendations = build_alignment_recommendations(
        data,
        confidence=confidence,
        conflicts=conflicts,
        drifts=drifts,
        risks=risks,
        mode=mode,
    )
    event = IntentAlignmentEvent(
        mode=mode,
        state=state,
        message=f"Intent alignment {mode.value}; confidence {score}/100.",
        timestamp=datetime.now(UTC),
    )
    return IntentAlignmentResult(
        mode=mode,
        state=state,
        alignment_confidence=score,
        confidence_breakdown=confidence,
        priority_order=_priority_order(data, risks),
        conflicts=conflicts,
        drifts=drifts,
        risks=risks,
        recommendations=recommendations,
        mission_status=_mission_status(mode, risks),
        strategic_goal_stability_score=priority_stability,
        events=(event,),
        summary=f"Intent alignment mode {mode.value} with confidence {score}/100 and {len(risks)} risk(s).",
    )


def detect_alignment_drifts(
    alignment_input: IntentAlignmentInput | None = None,
    *,
    confidence: IntentConfidence | None = None,
    **kwargs,
) -> tuple[IntentDrift, ...]:
    """Detect early intent drift signals across autonomous layers."""
    data = _input(alignment_input, **kwargs)
    resolved_confidence = confidence or compute_alignment_confidence(data)
    drifts: list[IntentDrift] = []

    if _autonomy_pressure(data, resolved_confidence):
        drifts.append(IntentDrift.AUTONOMY_EXPANDING)
    if _mission_pressure(data):
        drifts.append(IntentDrift.MISSION_DIVERGING)
    if _strategy_pressure(data):
        drifts.append(IntentDrift.STRATEGY_DIVERGING)
    if _safety_pressure(data) and _allows_expansion(data):
        drifts.append(IntentDrift.SAFETY_BOUNDARY_WEAKENING)
    if data.learning_governance is not None and data.learning_governance.decision == LearningGovernanceDecision.ALLOW_LEARNING and _system_unsafe(data):
        drifts.append(IntentDrift.GOVERNANCE_DRIFTING)
    if _goal_count(data) >= 7:
        drifts.append(IntentDrift.PRIORITY_FRAGMENTING)
    if data.self_evaluation is not None and data.self_evaluation.status in {SelfEvaluationStatus.CONTRADICTORY, SelfEvaluationStatus.UNSTABLE}:
        drifts.append(IntentDrift.RECURSIVE_GOAL_DRIFT)
    if data.meta_cognition is not None and data.meta_cognition.mode in {MetaCognitionMode.CONTRADICTORY, MetaCognitionMode.RECALIBRATION_REQUIRED}:
        drifts.append(IntentDrift.RECURSIVE_GOAL_DRIFT)

    return tuple(dict.fromkeys(drifts))


def detect_intent_conflicts(
    alignment_input: IntentAlignmentInput | None = None,
    *,
    confidence: IntentConfidence | None = None,
    drifts: tuple[IntentDrift, ...] | None = None,
    **kwargs,
) -> tuple[IntentConflict, ...]:
    """Detect hard intent conflicts between executive, safety and governance layers."""
    data = _input(alignment_input, **kwargs)
    resolved_confidence = confidence or compute_alignment_confidence(data)
    resolved_drifts = drifts or detect_alignment_drifts(data, confidence=resolved_confidence)
    conflicts: list[IntentConflict] = []

    if (
        data.executive_result is not None
        and data.executive_result.decision.allow_execution
        and data.learning_governance is not None
        and data.learning_governance.mode in {LearningGovernanceMode.FREEZE_LEARNING, LearningGovernanceMode.SAFETY_LOCKDOWN}
    ):
        conflicts.append(IntentConflict.EXECUTIVE_GOVERNANCE_CONFLICT)
    if (
        data.executive_result is not None
        and data.executive_result.decision.allow_execution
        and data.supervisor_result is not None
        and not data.supervisor_result.final_executable
    ):
        conflicts.append(IntentConflict.EXECUTIVE_SUPERVISOR_CONFLICT)
    if (
        data.strategic_result is not None
        and data.strategic_result.plan.primary_objective in {StrategicObjective.LEARNING_PHASE, StrategicObjective.POLICY_VALIDATION}
        and data.learning_governance is not None
        and data.learning_governance.mode in {LearningGovernanceMode.FREEZE_LEARNING, LearningGovernanceMode.SAFETY_LOCKDOWN}
    ):
        conflicts.append(IntentConflict.STRATEGY_GOVERNANCE_CONFLICT)
    if _safety_pressure(data) and _growth_or_execution_intent(data):
        conflicts.append(IntentConflict.SAFETY_MISSION_CONFLICT)
    if (
        data.self_evaluation is not None
        and data.self_evaluation.autonomy_recommendation == SystemAutonomyRecommendation.MAINTAIN_AUTONOMY
        and data.supervisor_result is not None
        and data.supervisor_result.decision in {SupervisorDecision.OVERRIDE_TO_BLOCK, SupervisorDecision.OVERRIDE_TO_STOP_SESSION, SupervisorDecision.EMERGENCY_HALT}
    ):
        conflicts.append(IntentConflict.AUTONOMY_SUPERVISION_CONFLICT)
    if _priority_collision(data):
        conflicts.append(IntentConflict.PRIORITY_COLLISION)
    if resolved_confidence.offline_boundary_score < 60:
        conflicts.append(IntentConflict.OFFLINE_BOUNDARY_CONFLICT)
    if IntentDrift.SAFETY_BOUNDARY_WEAKENING in resolved_drifts and IntentDrift.MISSION_DIVERGING in resolved_drifts:
        conflicts.append(IntentConflict.SAFETY_MISSION_CONFLICT)

    return tuple(dict.fromkeys(conflicts))


def compute_alignment_confidence(
    alignment_input: IntentAlignmentInput | None = None,
    **kwargs,
) -> IntentConfidence:
    """Compute intent alignment confidence component scores from 0..100."""
    data = _input(alignment_input, **kwargs)
    mission = 85
    safety = 90
    governance = 85
    strategic = 85
    priority = 85
    autonomy = 85
    offline = 100

    if data.meta_cognition is not None:
        strategic = min(strategic, data.meta_cognition.confidence_breakdown.strategic_alignment_score)
        autonomy = min(autonomy, data.meta_cognition.confidence_breakdown.autonomy_calibration_score)
        if data.meta_cognition.mode in {MetaCognitionMode.CONTRADICTORY, MetaCognitionMode.RECALIBRATION_REQUIRED}:
            mission -= 15
            strategic -= 15
            priority -= 15
        if MetaCognitiveRisk.AUTONOMY_OVEREXPANSION in data.meta_cognition.risks:
            autonomy -= 25

    if data.operational_awareness is not None:
        safety = min(safety, data.operational_awareness.operational_confidence_score)
        if data.operational_awareness.health_status in {OperationalHealthStatus.CRITICAL, OperationalHealthStatus.COLLAPSING}:
            safety -= 25
            autonomy -= 15
        if OperationalRisk.AUTONOMY_DRIFT in data.operational_awareness.risks:
            autonomy -= 20
        if OperationalRisk.STRATEGIC_INCONSISTENCY in data.operational_awareness.risks:
            strategic -= 15

    if data.mission_continuity is not None:
        mission = min(mission, data.mission_continuity.continuity_score)
        if data.mission_continuity.mode in {MissionContinuityMode.SURVIVAL_CONTINUITY, MissionContinuityMode.SAFE_PAUSE}:
            mission -= 15
            autonomy -= 15

    if data.system_integrity is not None:
        safety = min(safety, data.system_integrity.integrity_score)
        if data.system_integrity.status in {SystemIntegrityStatus.COMPROMISED, SystemIntegrityStatus.PROTECTION_MODE, SystemIntegrityStatus.ROLLBACK_RECOMMENDED}:
            safety -= 25
            governance -= 20
            autonomy -= 20

    if data.learning_governance is not None:
        if data.learning_governance.mode in {LearningGovernanceMode.FREEZE_LEARNING, LearningGovernanceMode.SAFETY_LOCKDOWN}:
            governance -= 10
            autonomy -= 20
        if data.learning_governance.decision == LearningGovernanceDecision.ALLOW_LEARNING and _system_unsafe(data):
            governance -= 25
            safety -= 15

    if data.self_evaluation is not None:
        autonomy = min(autonomy, data.self_evaluation.score_breakdown.autonomy_readiness_score)
        if data.self_evaluation.status in {SelfEvaluationStatus.CONTRADICTORY, SelfEvaluationStatus.UNSTABLE}:
            mission -= 15
            priority -= 20
            autonomy -= 15

    if data.executive_result is not None:
        if data.executive_result.state.risk_appetite == ExecutiveRiskAppetite.ELEVATED and _safety_pressure(data):
            safety -= 15
            priority -= 15
        if data.executive_result.decision.allow_execution and data.supervisor_result is not None and not data.supervisor_result.final_executable:
            priority -= 30
            governance -= 20
        if data.executive_result.state.mode in {ExecutiveMode.SURVIVAL, ExecutiveMode.PAUSED}:
            mission -= 5

    if data.strategic_result is not None:
        strategic = min(strategic, data.strategic_result.progress_score)
        if data.strategic_result.plan.status in {StrategicPlanStatus.PAUSED, StrategicPlanStatus.REVIEW_REQUIRED}:
            strategic -= 15
            priority -= 10
        if _goal_count(data) >= 7:
            priority -= 25

    return IntentConfidence(
        mission_alignment_score=_clamp(mission),
        safety_alignment_score=_clamp(safety),
        governance_alignment_score=_clamp(governance),
        strategic_alignment_score=_clamp(strategic),
        priority_stability_score=_clamp(priority),
        autonomy_alignment_score=_clamp(autonomy),
        offline_boundary_score=_clamp(offline),
    )


def analyze_priority_stability(
    alignment_input: IntentAlignmentInput | None = None,
    *,
    conflicts: tuple[IntentConflict, ...] | None = None,
    drifts: tuple[IntentDrift, ...] | None = None,
    **kwargs,
) -> int:
    """Analyze stability of the mission priority order."""
    data = _input(alignment_input, **kwargs)
    resolved_conflicts = conflicts or detect_intent_conflicts(data)
    resolved_drifts = drifts or detect_alignment_drifts(data)
    confidence = compute_alignment_confidence(data)
    score = _avg(
        (
            confidence.mission_alignment_score,
            confidence.governance_alignment_score,
            confidence.strategic_alignment_score,
            confidence.priority_stability_score,
        )
    )
    score -= min(35, len(resolved_conflicts) * 8)
    score -= min(25, len(resolved_drifts) * 4)
    if _priority_collision(data):
        score -= 15
    if _goal_count(data) >= 7:
        score -= 15
    return _clamp(score)


def build_alignment_recommendations(
    alignment_input: IntentAlignmentInput | None = None,
    *,
    confidence: IntentConfidence | None = None,
    conflicts: tuple[IntentConflict, ...] | None = None,
    drifts: tuple[IntentDrift, ...] | None = None,
    risks: tuple[IntentRisk, ...] | None = None,
    mode: IntentAlignmentMode | None = None,
    **kwargs,
) -> tuple[IntentRecommendation, ...]:
    """Build ordered recommendations to restore or preserve intent alignment."""
    data = _input(alignment_input, **kwargs)
    resolved_confidence = confidence or compute_alignment_confidence(data)
    resolved_drifts = drifts or detect_alignment_drifts(data, confidence=resolved_confidence)
    resolved_conflicts = conflicts or detect_intent_conflicts(data, confidence=resolved_confidence, drifts=resolved_drifts)
    priority_stability = analyze_priority_stability(data, conflicts=resolved_conflicts, drifts=resolved_drifts)
    resolved_risks = risks or _risks(data, resolved_confidence, resolved_conflicts, resolved_drifts, priority_stability)
    resolved_mode = mode or _mode(_global_confidence(resolved_confidence, resolved_conflicts, resolved_drifts, resolved_risks), resolved_conflicts, resolved_drifts, resolved_risks)
    recommendations: list[IntentRecommendation] = []

    if resolved_mode in {IntentAlignmentMode.CRITICAL_REALIGNMENT, IntentAlignmentMode.MISALIGNED}:
        recommendations.append(IntentRecommendation.ENTER_ALIGNMENT_SAFE_MODE)
        recommendations.append(IntentRecommendation.REQUIRE_ALIGNMENT_REVIEW)
    if IntentRisk.SAFETY_BOUNDARY_DRIFT in resolved_risks or IntentConflict.SAFETY_MISSION_CONFLICT in resolved_conflicts:
        recommendations.append(IntentRecommendation.REINFORCE_SAFETY_CONSTRAINTS)
    if IntentRisk.AUTONOMY_EXPANSION in resolved_risks or IntentDrift.AUTONOMY_EXPANDING in resolved_drifts:
        recommendations.append(IntentRecommendation.REDUCE_AUTONOMY)
        recommendations.append(IntentRecommendation.FREEZE_OBJECTIVE_EXPANSION)
    if IntentRisk.PRIORITY_COLLISION in resolved_risks or IntentConflict.PRIORITY_COLLISION in resolved_conflicts:
        recommendations.append(IntentRecommendation.RESTORE_PRIORITY_ORDER)
    if IntentRisk.STRATEGIC_MISALIGNMENT in resolved_risks or IntentRisk.MISSION_DIVERGENCE in resolved_risks:
        recommendations.append(IntentRecommendation.RECALIBRATE_STRATEGIC_GOALS)
    if resolved_conflicts:
        recommendations.append(IntentRecommendation.REQUIRE_SUPERVISION)
    if not recommendations:
        recommendations.append(IntentRecommendation.MAINTAIN_ALIGNMENT)
    recommendations.append(IntentRecommendation.CONTINUE_MONITORING)
    return tuple(dict.fromkeys(recommendations))


def render_intent_alignment_markdown(result: IntentAlignmentResult) -> str:
    """Render intent alignment assessment as Markdown."""
    lines = [
        "# Autonomous Intent Alignment Engine",
        "",
        "## Intent Alignment State",
        "",
        f"- Mode: {result.mode.value}",
        f"- State: {result.state.value}",
        f"- {result.summary}",
        "",
        "## Strategic Goal Stability",
        "",
        f"- {result.strategic_goal_stability_score}/100",
        f"- Mission status: {result.mission_status}",
        "",
        "## Priority Analysis",
        "",
        *_bullet_lines(tuple(priority.value for priority in result.priority_order)),
        "",
        "## Intent Conflicts",
        "",
        *_bullet_lines(tuple(conflict.value for conflict in result.conflicts)),
        "",
        "## Alignment Risks",
        "",
        *_bullet_lines(tuple(risk.value for risk in result.risks)),
        "",
        "## Alignment Confidence",
        "",
        f"- {result.alignment_confidence}/100",
        "",
        "## Recommendations",
        "",
        *_bullet_lines(tuple(recommendation.value for recommendation in result.recommendations)),
        "",
        "## AGIcore Alignment Status",
        "",
        "- Offline only: no broker, no real order, no external API, no external ML, no neural training.",
        "",
    ]
    return "\n".join(lines)


def _risks(
    data: IntentAlignmentInput,
    confidence: IntentConfidence,
    conflicts: tuple[IntentConflict, ...],
    drifts: tuple[IntentDrift, ...],
    priority_stability: int,
) -> tuple[IntentRisk, ...]:
    risks: list[IntentRisk] = []
    if IntentDrift.PRIORITY_FRAGMENTING in drifts or _goal_count(data) >= 7:
        risks.append(IntentRisk.GOAL_FRAGMENTATION)
    if IntentDrift.AUTONOMY_EXPANDING in drifts:
        risks.append(IntentRisk.AUTONOMY_EXPANSION)
    if IntentConflict.PRIORITY_COLLISION in conflicts or priority_stability < 55:
        risks.append(IntentRisk.PRIORITY_COLLISION)
    if IntentDrift.STRATEGY_DIVERGING in drifts or IntentConflict.STRATEGY_GOVERNANCE_CONFLICT in conflicts:
        risks.append(IntentRisk.STRATEGIC_MISALIGNMENT)
    if IntentDrift.SAFETY_BOUNDARY_WEAKENING in drifts or confidence.safety_alignment_score < 55:
        risks.append(IntentRisk.SAFETY_BOUNDARY_DRIFT)
    if data.meta_cognition is not None and data.meta_cognition.mode in {MetaCognitionMode.CONTRADICTORY, MetaCognitionMode.RECALIBRATION_REQUIRED}:
        risks.append(IntentRisk.REASONING_OBJECTIVE_CONFLICT)
    if _priority_collision(data):
        risks.append(IntentRisk.EXECUTIVE_PRIORITY_DRIFT)
    if IntentDrift.RECURSIVE_GOAL_DRIFT in drifts:
        risks.append(IntentRisk.RECURSIVE_GOAL_INSTABILITY)
    if IntentDrift.MISSION_DIVERGING in drifts or IntentConflict.SAFETY_MISSION_CONFLICT in conflicts:
        risks.append(IntentRisk.MISSION_DIVERGENCE)
    if len(conflicts) >= 3 or (IntentRisk.SAFETY_BOUNDARY_DRIFT in risks and IntentRisk.MISSION_DIVERGENCE in risks):
        risks.append(IntentRisk.ALIGNMENT_COLLAPSE)
    return tuple(dict.fromkeys(risks))


def _mode(
    score: int,
    conflicts: tuple[IntentConflict, ...],
    drifts: tuple[IntentDrift, ...],
    risks: tuple[IntentRisk, ...],
) -> IntentAlignmentMode:
    if IntentRisk.ALIGNMENT_COLLAPSE in risks or (IntentRisk.SAFETY_BOUNDARY_DRIFT in risks and IntentRisk.MISSION_DIVERGENCE in risks):
        return IntentAlignmentMode.CRITICAL_REALIGNMENT
    if score < 35 or len(conflicts) >= 3:
        return IntentAlignmentMode.MISALIGNED
    if IntentConflict.PRIORITY_COLLISION in conflicts:
        return IntentAlignmentMode.PRIORITY_CONFLICT
    if IntentDrift.AUTONOMY_EXPANDING in drifts:
        return IntentAlignmentMode.AUTONOMY_DRIFT
    if IntentDrift.STRATEGY_DIVERGING in drifts or IntentRisk.STRATEGIC_MISALIGNMENT in risks:
        return IntentAlignmentMode.STRATEGIC_DIVERGENCE
    if drifts or risks:
        return IntentAlignmentMode.PARTIAL_DRIFT
    if score >= 85:
        return IntentAlignmentMode.FULLY_ALIGNED
    return IntentAlignmentMode.STABLE_ALIGNMENT


def _state(
    mode: IntentAlignmentMode,
    score: int,
    conflicts: tuple[IntentConflict, ...],
    risks: tuple[IntentRisk, ...],
) -> IntentAlignmentState:
    if mode == IntentAlignmentMode.CRITICAL_REALIGNMENT:
        return IntentAlignmentState.CRITICAL
    if mode == IntentAlignmentMode.MISALIGNED or IntentRisk.ALIGNMENT_COLLAPSE in risks:
        return IntentAlignmentState.MISALIGNED
    if conflicts or mode == IntentAlignmentMode.PRIORITY_CONFLICT:
        return IntentAlignmentState.CONFLICTED
    if mode in {IntentAlignmentMode.PARTIAL_DRIFT, IntentAlignmentMode.AUTONOMY_DRIFT, IntentAlignmentMode.STRATEGIC_DIVERGENCE}:
        return IntentAlignmentState.DRIFTING
    if score < 85:
        return IntentAlignmentState.MONITORED
    return IntentAlignmentState.ALIGNED


def _global_confidence(
    confidence: IntentConfidence,
    conflicts: tuple[IntentConflict, ...],
    drifts: tuple[IntentDrift, ...],
    risks: tuple[IntentRisk, ...],
) -> int:
    score = _avg(
        (
            confidence.mission_alignment_score,
            confidence.safety_alignment_score,
            confidence.governance_alignment_score,
            confidence.strategic_alignment_score,
            confidence.priority_stability_score,
            confidence.autonomy_alignment_score,
            confidence.offline_boundary_score,
        )
    )
    score -= min(35, len(conflicts) * 8)
    score -= min(25, len(drifts) * 4)
    score -= min(35, len(risks) * 5)
    return _clamp(score)


def _priority_order(data: IntentAlignmentInput, risks: tuple[IntentRisk, ...]) -> tuple[IntentPriority, ...]:
    order = [
        IntentPriority.SAFETY,
        IntentPriority.OFFLINE_ONLY,
        IntentPriority.CAPITAL_PRESERVATION,
        IntentPriority.GOVERNANCE,
        IntentPriority.STRATEGIC_CONSISTENCY,
        IntentPriority.LEARNING,
        IntentPriority.AUTONOMY,
        IntentPriority.EXECUTION,
    ]
    if data.executive_result is not None and data.executive_result.state.intent == ExecutiveIntent.SESSION_STOP:
        order.insert(0, order.pop(order.index(IntentPriority.GOVERNANCE)))
    if IntentRisk.SAFETY_BOUNDARY_DRIFT in risks:
        order.insert(0, order.pop(order.index(IntentPriority.SAFETY)))
    return tuple(dict.fromkeys(order))


def _mission_status(mode: IntentAlignmentMode, risks: tuple[IntentRisk, ...]) -> str:
    if mode == IntentAlignmentMode.CRITICAL_REALIGNMENT:
        return "critical_realignment_required"
    if IntentRisk.MISSION_DIVERGENCE in risks:
        return "mission_drift_detected"
    if risks:
        return "aligned_with_monitoring"
    return "mission_aligned"


def _autonomy_pressure(data: IntentAlignmentInput, confidence: IntentConfidence) -> bool:
    if data.meta_cognition is not None and MetaCognitiveRisk.AUTONOMY_OVEREXPANSION in data.meta_cognition.risks:
        return True
    if data.operational_awareness is not None and OperationalRisk.AUTONOMY_DRIFT in data.operational_awareness.risks:
        return True
    if (
        data.self_evaluation is not None
        and data.self_evaluation.autonomy_recommendation == SystemAutonomyRecommendation.MAINTAIN_AUTONOMY
        and (_safety_pressure(data) or confidence.autonomy_alignment_score < 55)
    ):
        return True
    if data.executive_result is not None and data.executive_result.decision.allow_execution and _safety_pressure(data):
        return True
    return False


def _mission_pressure(data: IntentAlignmentInput) -> bool:
    if data.mission_continuity is not None and data.mission_continuity.mode in {MissionContinuityMode.SURVIVAL_CONTINUITY, MissionContinuityMode.SAFE_PAUSE} and _growth_or_execution_intent(data):
        return True
    if data.system_integrity is not None and data.system_integrity.status in {SystemIntegrityStatus.COMPROMISED, SystemIntegrityStatus.PROTECTION_MODE} and _allows_expansion(data):
        return True
    return False


def _strategy_pressure(data: IntentAlignmentInput) -> bool:
    if data.strategic_result is None:
        return False
    plan = data.strategic_result.plan
    if plan.status in {StrategicPlanStatus.PAUSED, StrategicPlanStatus.REVIEW_REQUIRED} and _growth_or_execution_intent(data):
        return True
    if plan.primary_objective in {StrategicObjective.POLICY_VALIDATION, StrategicObjective.LEARNING_PHASE} and data.learning_governance is not None and data.learning_governance.mode in {LearningGovernanceMode.FREEZE_LEARNING, LearningGovernanceMode.SAFETY_LOCKDOWN}:
        return True
    return False


def _safety_pressure(data: IntentAlignmentInput) -> bool:
    if data.system_integrity is not None and data.system_integrity.status in {SystemIntegrityStatus.COMPROMISED, SystemIntegrityStatus.PROTECTION_MODE, SystemIntegrityStatus.ROLLBACK_RECOMMENDED}:
        return True
    if data.operational_awareness is not None and data.operational_awareness.health_status in {OperationalHealthStatus.CRITICAL, OperationalHealthStatus.COLLAPSING}:
        return True
    if data.mission_continuity is not None and data.mission_continuity.mode in {MissionContinuityMode.SURVIVAL_CONTINUITY, MissionContinuityMode.SAFE_PAUSE}:
        return True
    if data.supervisor_result is not None and data.supervisor_result.decision in {SupervisorDecision.OVERRIDE_TO_BLOCK, SupervisorDecision.OVERRIDE_TO_STOP_SESSION, SupervisorDecision.EMERGENCY_HALT}:
        return True
    return False


def _allows_expansion(data: IntentAlignmentInput) -> bool:
    if data.learning_governance is not None and data.learning_governance.decision in {LearningGovernanceDecision.ALLOW_LEARNING, LearningGovernanceDecision.ALLOW_LIMITED_LEARNING}:
        return True
    if data.executive_result is not None and data.executive_result.state.intent in {ExecutiveIntent.CONTROLLED_GROWTH, ExecutiveIntent.POLICY_TESTING, ExecutiveIntent.LEARNING_ONLY}:
        return True
    if data.self_evaluation is not None and data.self_evaluation.autonomy_recommendation == SystemAutonomyRecommendation.MAINTAIN_AUTONOMY:
        return True
    return False


def _growth_or_execution_intent(data: IntentAlignmentInput) -> bool:
    if data.executive_result is None:
        return False
    return (
        data.executive_result.decision.allow_execution
        or data.executive_result.state.intent in {ExecutiveIntent.CONTROLLED_GROWTH, ExecutiveIntent.POLICY_TESTING}
        or data.executive_result.state.risk_appetite == ExecutiveRiskAppetite.ELEVATED
    )


def _priority_collision(data: IntentAlignmentInput) -> bool:
    if data.executive_result is None or data.strategic_result is None:
        return False
    executive_intent = data.executive_result.state.intent
    strategic_objective = data.strategic_result.plan.primary_objective
    protective_objectives = {StrategicObjective.CAPITAL_PRESERVATION, StrategicObjective.RISK_REDUCTION, StrategicObjective.PAUSE_AND_REVIEW, StrategicObjective.DRAWDOWN_RECOVERY}
    expansion_intents = {ExecutiveIntent.CONTROLLED_GROWTH, ExecutiveIntent.POLICY_TESTING}
    return executive_intent in expansion_intents and strategic_objective in protective_objectives


def _system_unsafe(data: IntentAlignmentInput) -> bool:
    return _safety_pressure(data) or (
        data.operational_awareness is not None
        and data.operational_awareness.mode in {OperationalAwarenessMode.CRITICAL, OperationalAwarenessMode.UNSTABLE}
    )


def _goal_count(data: IntentAlignmentInput) -> int:
    if data.strategic_result is None:
        return 0
    plan = data.strategic_result.plan
    return len(plan.session_objectives) + len(plan.risk_constraints) + len(plan.long_term_risks) + len(plan.recommendations)


def _avg(values: tuple[int, ...]) -> int:
    return int(round(sum(values) / len(values)))


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _input(alignment_input: IntentAlignmentInput | None = None, **kwargs: Any) -> IntentAlignmentInput:
    if alignment_input is not None:
        return alignment_input
    return IntentAlignmentInput(**kwargs)


def _clamp(value: int | float) -> int:
    return max(0, min(100, int(round(value))))


__all__ = [
    "analyze_priority_stability",
    "build_alignment_recommendations",
    "compute_alignment_confidence",
    "detect_alignment_drifts",
    "detect_intent_conflicts",
    "evaluate_intent_alignment",
    "render_intent_alignment_markdown",
]
