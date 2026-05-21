"""Offline Autonomous Strategic Arbitration Engine for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .behavioral_stability_models import BehavioralPressureLevel, BehavioralRecoveryState, BehavioralRiskSignal
from .executive_brain_models import ExecutiveIntent, ExecutiveMode, ExecutiveRiskAppetite
from .hierarchical_supervisor_models import SupervisorDecision
from .intent_alignment_models import IntentAlignmentMode, IntentRisk
from .learning_governance_models import LearningGovernanceDecision, LearningGovernanceMode
from .meta_cognition_models import MetaCognitionMode, MetaCognitiveRisk
from .mission_continuity_models import MissionContinuityMode
from .operational_awareness_models import OperationalAwarenessMode, OperationalHealthStatus, OperationalRisk
from .recovery_resilience_models import RecoveryMode, RecoveryRisk
from .recursive_self_evaluation_models import SelfEvaluationStatus, SystemAutonomyRecommendation
from .strategic_arbitration_models import (
    ArbitrationAuthority,
    ArbitrationConflictType,
    ArbitrationDecision,
    ArbitrationEvent,
    ArbitrationInput,
    ArbitrationMode,
    ArbitrationPriority,
    ArbitrationRecommendation,
    ArbitrationResolution,
    ArbitrationResult,
    ArbitrationSeverity,
    ArbitrationState,
    PriorityGraph,
    StrategicConflict,
)
from .strategic_planning_models import StrategicObjective, StrategicPlanStatus
from .system_integrity_models import SystemIntegrityStatus
from .tactical_execution_models import TacticalExecutionQuality, TacticalExecutionSignal


PRIORITY_ORDER: tuple[ArbitrationPriority, ...] = (
    ArbitrationPriority.SURVIVAL,
    ArbitrationPriority.INTEGRITY,
    ArbitrationPriority.SAFETY,
    ArbitrationPriority.MISSION,
    ArbitrationPriority.CONTINUITY,
    ArbitrationPriority.SUPERVISION,
    ArbitrationPriority.STRATEGY,
    ArbitrationPriority.PERFORMANCE,
    ArbitrationPriority.LEARNING,
)


def detect_strategic_conflicts(
    arbitration_input: ArbitrationInput | None = None,
    **kwargs,
) -> tuple[StrategicConflict, ...]:
    """Detect strategic conflicts between profit, safety, mission and control layers."""
    data = _input(arbitration_input, **kwargs)
    conflicts: list[StrategicConflict] = []

    if _profit_intent(data) and _safety_danger(data):
        conflicts.append(
            StrategicConflict(
                ArbitrationConflictType.PROFIT_VS_SAFETY,
                _critical_if(_critical_safety(data), ArbitrationSeverity.HIGH),
                (ArbitrationPriority.PERFORMANCE, ArbitrationPriority.SAFETY),
                "Profit or execution pressure conflicts with elevated safety danger.",
            )
        )
    if _learning_enabled(data) and _stability_weak(data):
        conflicts.append(
            StrategicConflict(
                ArbitrationConflictType.LEARNING_VS_STABILITY,
                ArbitrationSeverity.HIGH if _system_critical(data) else ArbitrationSeverity.MEDIUM,
                (ArbitrationPriority.LEARNING, ArbitrationPriority.INTEGRITY),
                "Learning expansion conflicts with weak stability or governance.",
            )
        )
    if _mission_protective(data) and _execution_allowed(data):
        conflicts.append(
            StrategicConflict(
                ArbitrationConflictType.MISSION_VS_EXECUTION,
                ArbitrationSeverity.HIGH,
                (ArbitrationPriority.MISSION, ArbitrationPriority.PERFORMANCE),
                "Mission protection conflicts with execution permission.",
            )
        )
    if _autonomy_risky(data) and _supervision_blocks(data):
        conflicts.append(
            StrategicConflict(
                ArbitrationConflictType.AUTONOMY_VS_SUPERVISION,
                ArbitrationSeverity.HIGH,
                (ArbitrationPriority.SUPERVISION, ArbitrationPriority.PERFORMANCE),
                "Autonomy attempts to continue while supervision blocks or requires review.",
            )
        )
    if _execution_allowed(data) and _integrity_degraded(data):
        conflicts.append(
            StrategicConflict(
                ArbitrationConflictType.SPEED_VS_INTEGRITY,
                _critical_if(_system_critical(data), ArbitrationSeverity.HIGH),
                (ArbitrationPriority.INTEGRITY, ArbitrationPriority.PERFORMANCE),
                "Execution speed conflicts with degraded system integrity.",
            )
        )
    if _recovery_active(data) and _continuity_constrained(data):
        conflicts.append(
            StrategicConflict(
                ArbitrationConflictType.RECOVERY_VS_CONTINUITY,
                ArbitrationSeverity.MEDIUM,
                (ArbitrationPriority.CONTINUITY, ArbitrationPriority.SURVIVAL),
                "Recovery actions must be balanced against continuity preservation.",
            )
        )
    if _cognition_degraded(data) and _safety_danger(data):
        conflicts.append(
            StrategicConflict(
                ArbitrationConflictType.COGNITION_VS_RISK,
                _critical_if(_critical_safety(data), ArbitrationSeverity.HIGH),
                (ArbitrationPriority.SAFETY, ArbitrationPriority.STRATEGY),
                "Cognitive degradation conflicts with risk-bearing decisions.",
            )
        )
    if _strategy_expands(data) and _discipline_weak(data):
        conflicts.append(
            StrategicConflict(
                ArbitrationConflictType.STRATEGY_VS_DISCIPLINE,
                ArbitrationSeverity.MEDIUM,
                (ArbitrationPriority.STRATEGY, ArbitrationPriority.SAFETY),
                "Strategy expansion conflicts with tactical or behavioral discipline weakness.",
            )
        )
    if _execution_allowed(data) and _alignment_unsafe(data):
        conflicts.append(
            StrategicConflict(
                ArbitrationConflictType.EXECUTION_VS_ALIGNMENT,
                ArbitrationSeverity.HIGH,
                (ArbitrationPriority.MISSION, ArbitrationPriority.PERFORMANCE),
                "Execution conflicts with intent alignment or mission boundaries.",
            )
        )
    if _survival_required(data) and _profit_intent(data):
        conflicts.append(
            StrategicConflict(
                ArbitrationConflictType.SURVIVAL_VS_PERFORMANCE,
                ArbitrationSeverity.CRITICAL,
                (ArbitrationPriority.SURVIVAL, ArbitrationPriority.PERFORMANCE),
                "Survival controls override performance pressure.",
            )
        )

    return tuple(dict.fromkeys(conflicts))


def compute_arbitration_priority(
    conflicts: tuple[StrategicConflict, ...] | None = None,
    arbitration_input: ArbitrationInput | None = None,
    **kwargs,
) -> ArbitrationPriority:
    """Return the highest active priority according to the fixed hierarchy."""
    data = _input(arbitration_input, **kwargs)
    resolved_conflicts = conflicts if conflicts is not None else detect_strategic_conflicts(data)
    active = _active_priorities(data, resolved_conflicts)
    for priority in PRIORITY_ORDER:
        if priority in active:
            return priority
    return ArbitrationPriority.PERFORMANCE


def evaluate_survival_priority(
    arbitration_input: ArbitrationInput | None = None,
    **kwargs,
) -> bool:
    """Evaluate whether survival outranks all other active concerns."""
    return _survival_required(_input(arbitration_input, **kwargs))


def resolve_conflicts(
    conflicts: tuple[StrategicConflict, ...],
    arbitration_input: ArbitrationInput | None = None,
    **kwargs,
) -> tuple[ArbitrationResolution, ...]:
    """Resolve each conflict by selecting the highest-ranking priority."""
    data = _input(arbitration_input, **kwargs)
    resolutions: list[ArbitrationResolution] = []
    for conflict in conflicts:
        winning_priority = _highest(conflict.priorities)
        authority = _authority(winning_priority)
        decision = _decision_for_priority(winning_priority, conflict.severity, data)
        resolutions.append(
            ArbitrationResolution(
                conflict.conflict_type,
                winning_priority,
                authority,
                decision,
                f"{winning_priority.value} outranks lower priorities by fixed arbitration hierarchy.",
            )
        )
    return tuple(resolutions)


def apply_emergency_arbitration(
    arbitration_input: ArbitrationInput | None = None,
    *,
    conflicts: tuple[StrategicConflict, ...] | None = None,
    **kwargs,
) -> bool:
    """Return True when critical risks require emergency lockdown."""
    data = _input(arbitration_input, **kwargs)
    resolved_conflicts = conflicts if conflicts is not None else detect_strategic_conflicts(data)
    critical_conflicts = sum(1 for conflict in resolved_conflicts if conflict.severity == ArbitrationSeverity.CRITICAL)
    high_conflicts = sum(1 for conflict in resolved_conflicts if conflict.severity == ArbitrationSeverity.HIGH)
    return (
        critical_conflicts >= 2
        or (critical_conflicts >= 1 and high_conflicts >= 2)
        or (_survival_required(data) and _system_critical(data) and _alignment_unsafe(data))
    )


def build_priority_graph(
    arbitration_input: ArbitrationInput | None = None,
    *,
    conflicts: tuple[StrategicConflict, ...] | None = None,
    **kwargs,
) -> PriorityGraph:
    """Build the static priority graph with currently active priorities."""
    data = _input(arbitration_input, **kwargs)
    resolved_conflicts = conflicts if conflicts is not None else detect_strategic_conflicts(data)
    edges = tuple((PRIORITY_ORDER[index], PRIORITY_ORDER[index + 1]) for index in range(len(PRIORITY_ORDER) - 1))
    active = tuple(priority for priority in PRIORITY_ORDER if priority in _active_priorities(data, resolved_conflicts))
    dominant = compute_arbitration_priority(resolved_conflicts, data)
    return PriorityGraph(PRIORITY_ORDER, edges, active, dominant)


def compute_arbitration_confidence(
    arbitration_input: ArbitrationInput | None = None,
    *,
    conflicts: tuple[StrategicConflict, ...] | None = None,
    emergency_lockdown: bool | None = None,
    **kwargs,
) -> int:
    """Compute confidence in the arbitration decision from 0..100."""
    data = _input(arbitration_input, **kwargs)
    resolved_conflicts = conflicts if conflicts is not None else detect_strategic_conflicts(data)
    lockdown = apply_emergency_arbitration(data, conflicts=resolved_conflicts) if emergency_lockdown is None else emergency_lockdown
    score = 88
    score -= min(35, len(resolved_conflicts) * 4)
    score -= sum(8 for conflict in resolved_conflicts if conflict.severity == ArbitrationSeverity.CRITICAL)
    score -= sum(4 for conflict in resolved_conflicts if conflict.severity == ArbitrationSeverity.HIGH)
    if data.intent_alignment is not None:
        score = min(score, data.intent_alignment.alignment_confidence)
    if data.system_integrity is not None:
        score = min(score, data.system_integrity.integrity_score)
    if data.operational_awareness is not None:
        score = min(score, data.operational_awareness.operational_confidence_score)
    if lockdown:
        score -= 10
    return _clamp(score)


def generate_arbitration_recommendations(
    arbitration_input: ArbitrationInput | None = None,
    *,
    conflicts: tuple[StrategicConflict, ...] | None = None,
    emergency_lockdown: bool | None = None,
    **kwargs,
) -> tuple[ArbitrationRecommendation, ...]:
    """Generate ordered recommendations from conflicts and active authorities."""
    data = _input(arbitration_input, **kwargs)
    resolved_conflicts = conflicts if conflicts is not None else detect_strategic_conflicts(data)
    lockdown = apply_emergency_arbitration(data, conflicts=resolved_conflicts) if emergency_lockdown is None else emergency_lockdown
    conflict_types = {conflict.conflict_type for conflict in resolved_conflicts}
    recommendations: list[ArbitrationRecommendation] = []

    if lockdown:
        recommendations.append(ArbitrationRecommendation.LOCK_HIGH_RISK_ACTIONS)
        recommendations.append(ArbitrationRecommendation.ENABLE_SAFE_MODE)
        recommendations.append(ArbitrationRecommendation.REQUIRE_HUMAN_SUPERVISION)
    if ArbitrationConflictType.AUTONOMY_VS_SUPERVISION in conflict_types or _autonomy_risky(data):
        recommendations.append(ArbitrationRecommendation.REDUCE_AUTONOMY)
        recommendations.append(ArbitrationRecommendation.REQUIRE_HUMAN_SUPERVISION)
    if ArbitrationConflictType.LEARNING_VS_STABILITY in conflict_types or _governance_unstable(data):
        recommendations.append(ArbitrationRecommendation.FREEZE_LEARNING)
    if _integrity_degraded(data):
        recommendations.append(ArbitrationRecommendation.ISOLATE_MODULE)
        recommendations.append(ArbitrationRecommendation.ROLLBACK_STRATEGY)
    if _continuity_constrained(data) or _survival_required(data):
        recommendations.append(ArbitrationRecommendation.PROTECT_MEMORY)
        recommendations.append(ArbitrationRecommendation.ENABLE_SAFE_MODE)
    if _execution_allowed(data) and (resolved_conflicts or _safety_danger(data)):
        recommendations.append(ArbitrationRecommendation.SLOW_EXECUTION)
        recommendations.append(ArbitrationRecommendation.LOCK_HIGH_RISK_ACTIONS)
    if not recommendations:
        recommendations.append(ArbitrationRecommendation.CONTINUE_OPERATION)
    return tuple(dict.fromkeys(recommendations))


def render_strategic_arbitration_markdown(result: ArbitrationResult) -> str:
    """Render strategic arbitration as Markdown."""
    lines = [
        "# Autonomous Strategic Arbitration Engine",
        "",
        "## Strategic Arbitration State",
        "",
        f"- Mode: {result.mode.value}",
        f"- State: {result.state.value}",
        f"- Confidence: {result.confidence_score}/100",
        "",
        "## Detected Conflicts",
        "",
        *_bullet_lines(tuple(f"{conflict.conflict_type.value} ({conflict.severity.value})" for conflict in result.conflicts)),
        "",
        "## Priority Graph",
        "",
        f"- Dominant priority: {result.priority_graph.dominant_priority.value}",
        *_bullet_lines(tuple(f"{upper.value} > {lower.value}" for upper, lower in result.priority_graph.edges)),
        "",
        "## Arbitration Decision",
        "",
        f"- {result.decision.value}",
        f"- {result.final_message}",
        "",
        "## Severity",
        "",
        f"- {result.severity.value}",
        "",
        "## Active Authorities",
        "",
        *_bullet_lines(tuple(authority.value for authority in result.active_authorities)),
        "",
        "## Recommendations",
        "",
        *_bullet_lines(tuple(recommendation.value for recommendation in result.recommendations)),
        "",
        "## AGIcore Final Arbitration",
        "",
        "- Offline only: no broker, no real order, no external API, no external ML, no external LLM, no neural training, no live execution.",
        "",
    ]
    return "\n".join(lines)


def arbitrate_strategic_decision(
    arbitration_input: ArbitrationInput | None = None,
    **kwargs,
) -> ArbitrationResult:
    """Run the full offline strategic arbitration pipeline."""
    data = _input(arbitration_input, **kwargs)
    conflicts = detect_strategic_conflicts(data)
    priority_graph = build_priority_graph(data, conflicts=conflicts)
    resolutions = resolve_conflicts(conflicts, data)
    lockdown = apply_emergency_arbitration(data, conflicts=conflicts)
    severity = _overall_severity(conflicts, lockdown)
    decision = ArbitrationDecision.EMERGENCY_LOCKDOWN if lockdown else _final_decision(priority_graph.dominant_priority, severity, data, conflicts)
    mode = _mode(priority_graph.dominant_priority, severity, lockdown, data)
    state = _state(decision, severity, conflicts)
    recommendations = generate_arbitration_recommendations(data, conflicts=conflicts, emergency_lockdown=lockdown)
    confidence = compute_arbitration_confidence(data, conflicts=conflicts, emergency_lockdown=lockdown)
    authorities = tuple(dict.fromkeys(_authority(resolution.winning_priority) for resolution in resolutions)) or (_authority(priority_graph.dominant_priority),)
    event = ArbitrationEvent(
        mode,
        decision,
        severity,
        f"Strategic arbitration selected {decision.value} under {priority_graph.dominant_priority.value}.",
        datetime.now(UTC),
    )
    return ArbitrationResult(
        mode,
        state,
        decision,
        severity,
        confidence,
        priority_graph.dominant_priority,
        authorities,
        conflicts,
        resolutions,
        priority_graph,
        recommendations,
        lockdown,
        _final_message(decision, priority_graph.dominant_priority, conflicts),
        (event,),
    )


def _active_priorities(data: ArbitrationInput, conflicts: tuple[StrategicConflict, ...]) -> set[ArbitrationPriority]:
    active = {priority for conflict in conflicts for priority in conflict.priorities}
    if _survival_required(data):
        active.add(ArbitrationPriority.SURVIVAL)
    if _integrity_degraded(data):
        active.add(ArbitrationPriority.INTEGRITY)
    if _safety_danger(data):
        active.add(ArbitrationPriority.SAFETY)
    if _alignment_unsafe(data) or _mission_protective(data):
        active.add(ArbitrationPriority.MISSION)
    if _continuity_constrained(data):
        active.add(ArbitrationPriority.CONTINUITY)
    if _supervision_blocks(data):
        active.add(ArbitrationPriority.SUPERVISION)
    if _strategy_expands(data):
        active.add(ArbitrationPriority.STRATEGY)
    if _profit_intent(data):
        active.add(ArbitrationPriority.PERFORMANCE)
    if _learning_enabled(data):
        active.add(ArbitrationPriority.LEARNING)
    return active or {ArbitrationPriority.PERFORMANCE}


def _highest(priorities: tuple[ArbitrationPriority, ...]) -> ArbitrationPriority:
    for priority in PRIORITY_ORDER:
        if priority in priorities:
            return priority
    return ArbitrationPriority.PERFORMANCE


def _authority(priority: ArbitrationPriority) -> ArbitrationAuthority:
    return {
        ArbitrationPriority.SURVIVAL: ArbitrationAuthority.SURVIVAL_CONTROLLER,
        ArbitrationPriority.INTEGRITY: ArbitrationAuthority.INTEGRITY_CONTROLLER,
        ArbitrationPriority.SAFETY: ArbitrationAuthority.SAFETY_GUARDIAN,
        ArbitrationPriority.MISSION: ArbitrationAuthority.MISSION_GUARDIAN,
        ArbitrationPriority.CONTINUITY: ArbitrationAuthority.CONTINUITY_MANAGER,
        ArbitrationPriority.SUPERVISION: ArbitrationAuthority.SUPERVISION_CONTROLLER,
        ArbitrationPriority.STRATEGY: ArbitrationAuthority.STRATEGY_DIRECTOR,
        ArbitrationPriority.PERFORMANCE: ArbitrationAuthority.PERFORMANCE_MANAGER,
        ArbitrationPriority.LEARNING: ArbitrationAuthority.LEARNING_GOVERNOR,
    }[priority]


def _decision_for_priority(priority: ArbitrationPriority, severity: ArbitrationSeverity, data: ArbitrationInput) -> ArbitrationDecision:
    if severity == ArbitrationSeverity.CRITICAL and priority in {ArbitrationPriority.SURVIVAL, ArbitrationPriority.INTEGRITY, ArbitrationPriority.SAFETY}:
        return ArbitrationDecision.EMERGENCY_LOCKDOWN
    if priority == ArbitrationPriority.SURVIVAL:
        return ArbitrationDecision.STOP_EXECUTION
    if priority == ArbitrationPriority.INTEGRITY:
        return ArbitrationDecision.ROLLBACK_STRATEGY if _system_critical(data) else ArbitrationDecision.ENABLE_SAFE_MODE
    if priority == ArbitrationPriority.SAFETY:
        return ArbitrationDecision.ENABLE_SAFE_MODE
    if priority == ArbitrationPriority.MISSION:
        return ArbitrationDecision.STOP_EXECUTION if _alignment_unsafe(data) else ArbitrationDecision.REDUCE_RISK
    if priority in {ArbitrationPriority.CONTINUITY, ArbitrationPriority.SUPERVISION}:
        return ArbitrationDecision.REQUIRE_SUPERVISION
    if priority == ArbitrationPriority.LEARNING:
        return ArbitrationDecision.FREEZE_LEARNING if _stability_weak(data) else ArbitrationDecision.CONTINUE_OPERATION
    return ArbitrationDecision.REDUCE_RISK if severity in {ArbitrationSeverity.HIGH, ArbitrationSeverity.CRITICAL} else ArbitrationDecision.CONTINUE_OPERATION


def _final_decision(
    priority: ArbitrationPriority,
    severity: ArbitrationSeverity,
    data: ArbitrationInput,
    conflicts: tuple[StrategicConflict, ...],
) -> ArbitrationDecision:
    if not conflicts and not _safety_danger(data):
        return ArbitrationDecision.CONTINUE_OPERATION
    return _decision_for_priority(priority, severity, data)


def _mode(priority: ArbitrationPriority, severity: ArbitrationSeverity, lockdown: bool, data: ArbitrationInput) -> ArbitrationMode:
    if lockdown:
        return ArbitrationMode.EMERGENCY_LOCKDOWN
    if priority == ArbitrationPriority.SURVIVAL:
        return ArbitrationMode.SURVIVAL_MODE
    if priority == ArbitrationPriority.INTEGRITY:
        return ArbitrationMode.INTEGRITY_PRIORITY
    if priority == ArbitrationPriority.MISSION:
        return ArbitrationMode.MISSION_PRIORITY
    if priority == ArbitrationPriority.SUPERVISION or _supervision_blocks(data):
        return ArbitrationMode.SUPERVISED_MODE
    if severity == ArbitrationSeverity.HIGH:
        return ArbitrationMode.PROTECTIVE_ARBITRATION
    if severity == ArbitrationSeverity.MEDIUM:
        return ArbitrationMode.SAFE_COORDINATION
    return ArbitrationMode.NORMAL_OPERATION


def _state(decision: ArbitrationDecision, severity: ArbitrationSeverity, conflicts: tuple[StrategicConflict, ...]) -> ArbitrationState:
    if decision == ArbitrationDecision.EMERGENCY_LOCKDOWN:
        return ArbitrationState.LOCKDOWN_REQUIRED
    if decision == ArbitrationDecision.ENABLE_SAFE_MODE:
        return ArbitrationState.SAFE_MODE_REQUIRED
    if decision == ArbitrationDecision.REQUIRE_SUPERVISION:
        return ArbitrationState.SUPERVISION_REQUIRED
    if conflicts or severity in {ArbitrationSeverity.MEDIUM, ArbitrationSeverity.HIGH, ArbitrationSeverity.CRITICAL}:
        return ArbitrationState.CONFLICT_DETECTED
    return ArbitrationState.STABLE


def _overall_severity(conflicts: tuple[StrategicConflict, ...], lockdown: bool) -> ArbitrationSeverity:
    if lockdown:
        return ArbitrationSeverity.CRITICAL
    if any(conflict.severity == ArbitrationSeverity.CRITICAL for conflict in conflicts):
        return ArbitrationSeverity.CRITICAL
    if any(conflict.severity == ArbitrationSeverity.HIGH for conflict in conflicts):
        return ArbitrationSeverity.HIGH
    if any(conflict.severity == ArbitrationSeverity.MEDIUM for conflict in conflicts):
        return ArbitrationSeverity.MEDIUM
    return ArbitrationSeverity.LOW


def _final_message(decision: ArbitrationDecision, priority: ArbitrationPriority, conflicts: tuple[StrategicConflict, ...]) -> str:
    return f"{priority.value} authority selected {decision.value} after {len(conflicts)} conflict(s)."


def _profit_intent(data: ArbitrationInput) -> bool:
    if data.executive_result is None:
        return False
    return (
        data.executive_result.decision.allow_execution
        or data.executive_result.state.intent in {ExecutiveIntent.CONTROLLED_GROWTH, ExecutiveIntent.POLICY_TESTING}
        or data.executive_result.state.mode == ExecutiveMode.OPPORTUNITY
        or data.executive_result.state.risk_appetite == ExecutiveRiskAppetite.ELEVATED
    )


def _execution_allowed(data: ArbitrationInput) -> bool:
    return data.executive_result is not None and data.executive_result.decision.allow_execution


def _learning_enabled(data: ArbitrationInput) -> bool:
    return data.learning_governance is not None and data.learning_governance.decision in {
        LearningGovernanceDecision.ALLOW_LEARNING,
        LearningGovernanceDecision.ALLOW_LIMITED_LEARNING,
    }


def _governance_unstable(data: ArbitrationInput) -> bool:
    return data.learning_governance is not None and data.learning_governance.mode in {
        LearningGovernanceMode.FREEZE_LEARNING,
        LearningGovernanceMode.SAFETY_LOCKDOWN,
        LearningGovernanceMode.RECOVERY_MODE,
    }


def _stability_weak(data: ArbitrationInput) -> bool:
    return (
        _integrity_degraded(data)
        or _governance_unstable(data)
        or (data.operational_awareness is not None and data.operational_awareness.health_status in {OperationalHealthStatus.DEGRADED, OperationalHealthStatus.CRITICAL, OperationalHealthStatus.COLLAPSING})
        or (data.self_evaluation is not None and data.self_evaluation.status in {SelfEvaluationStatus.DEGRADED, SelfEvaluationStatus.UNSTABLE, SelfEvaluationStatus.CONTRADICTORY})
    )


def _mission_protective(data: ArbitrationInput) -> bool:
    if data.executive_result is not None and data.executive_result.state.intent in {ExecutiveIntent.CAPITAL_PRESERVATION, ExecutiveIntent.RISK_REDUCTION, ExecutiveIntent.SESSION_STOP}:
        return True
    if data.strategic_result is not None and data.strategic_result.plan.primary_objective in {StrategicObjective.CAPITAL_PRESERVATION, StrategicObjective.RISK_REDUCTION, StrategicObjective.PAUSE_AND_REVIEW, StrategicObjective.DRAWDOWN_RECOVERY}:
        return True
    return False


def _autonomy_risky(data: ArbitrationInput) -> bool:
    if data.self_evaluation is not None and data.self_evaluation.autonomy_recommendation == SystemAutonomyRecommendation.MAINTAIN_AUTONOMY and _safety_danger(data):
        return True
    if data.meta_cognition is not None and MetaCognitiveRisk.AUTONOMY_OVEREXPANSION in data.meta_cognition.risks:
        return True
    if data.intent_alignment is not None and IntentRisk.AUTONOMY_EXPANSION in data.intent_alignment.risks:
        return True
    return False


def _supervision_blocks(data: ArbitrationInput) -> bool:
    return data.supervisor_result is not None and (
        not data.supervisor_result.final_executable
        or data.supervisor_result.decision in {
            SupervisorDecision.REQUIRE_HUMAN_REVIEW,
            SupervisorDecision.OVERRIDE_TO_BLOCK,
            SupervisorDecision.OVERRIDE_TO_STOP_SESSION,
            SupervisorDecision.EMERGENCY_HALT,
        }
    )


def _integrity_degraded(data: ArbitrationInput) -> bool:
    return data.system_integrity is not None and data.system_integrity.status in {
        SystemIntegrityStatus.DEGRADED,
        SystemIntegrityStatus.UNSTABLE,
        SystemIntegrityStatus.COMPROMISED,
        SystemIntegrityStatus.PROTECTION_MODE,
        SystemIntegrityStatus.ROLLBACK_RECOMMENDED,
    }


def _system_critical(data: ArbitrationInput) -> bool:
    return data.system_integrity is not None and data.system_integrity.status in {
        SystemIntegrityStatus.COMPROMISED,
        SystemIntegrityStatus.PROTECTION_MODE,
        SystemIntegrityStatus.ROLLBACK_RECOMMENDED,
    }


def _safety_danger(data: ArbitrationInput) -> bool:
    return (
        _system_critical(data)
        or (data.operational_awareness is not None and data.operational_awareness.health_status in {OperationalHealthStatus.CRITICAL, OperationalHealthStatus.COLLAPSING})
        or (data.intent_alignment is not None and data.intent_alignment.mode in {IntentAlignmentMode.MISALIGNED, IntentAlignmentMode.CRITICAL_REALIGNMENT})
        or _supervision_blocks(data)
    )


def _critical_safety(data: ArbitrationInput) -> bool:
    return (
        _system_critical(data)
        or (data.operational_awareness is not None and data.operational_awareness.health_status == OperationalHealthStatus.COLLAPSING)
        or (data.intent_alignment is not None and data.intent_alignment.mode == IntentAlignmentMode.CRITICAL_REALIGNMENT)
    )


def _recovery_active(data: ArbitrationInput) -> bool:
    return data.recovery_resilience is not None and data.recovery_resilience.mode in {
        RecoveryMode.STABILIZE,
        RecoveryMode.REDUCE_COMPLEXITY,
        RecoveryMode.ISOLATE_MODULES,
        RecoveryMode.STRATEGIC_ROLLBACK,
        RecoveryMode.REBUILD_CONFIDENCE,
        RecoveryMode.PAUSED_RECOVERY,
    }


def _continuity_constrained(data: ArbitrationInput) -> bool:
    return data.mission_continuity is not None and data.mission_continuity.mode in {
        MissionContinuityMode.DEGRADED_OPERATION,
        MissionContinuityMode.ESSENTIAL_ONLY,
        MissionContinuityMode.SURVIVAL_CONTINUITY,
        MissionContinuityMode.ISOLATED_OPERATION,
        MissionContinuityMode.SAFE_PAUSE,
    }


def _survival_required(data: ArbitrationInput) -> bool:
    return (
        (data.recovery_resilience is not None and (data.recovery_resilience.mode == RecoveryMode.SURVIVAL_MODE or RecoveryRisk.SYSTEM_COMPROMISED in data.recovery_resilience.risks))
        or (data.mission_continuity is not None and data.mission_continuity.mode == MissionContinuityMode.SURVIVAL_CONTINUITY)
        or (data.executive_result is not None and data.executive_result.state.mode == ExecutiveMode.SURVIVAL)
    )


def _cognition_degraded(data: ArbitrationInput) -> bool:
    return data.meta_cognition is not None and (
        data.meta_cognition.mode in {MetaCognitionMode.CONTRADICTORY, MetaCognitionMode.DEGRADED_REASONING, MetaCognitionMode.RECALIBRATION_REQUIRED}
        or MetaCognitiveRisk.COGNITIVE_COLLAPSE in data.meta_cognition.risks
        or MetaCognitiveRisk.REASONING_DEGRADATION in data.meta_cognition.risks
    )


def _strategy_expands(data: ArbitrationInput) -> bool:
    if data.strategic_result is not None and data.strategic_result.plan.primary_objective in {StrategicObjective.CONTROLLED_GROWTH, StrategicObjective.POLICY_VALIDATION, StrategicObjective.LEARNING_PHASE}:
        return True
    return data.executive_result is not None and data.executive_result.state.intent in {ExecutiveIntent.CONTROLLED_GROWTH, ExecutiveIntent.POLICY_TESTING, ExecutiveIntent.LEARNING_ONLY}


def _discipline_weak(data: ArbitrationInput) -> bool:
    return (
        (data.tactical_execution is not None and (data.tactical_execution.quality in {TacticalExecutionQuality.WEAK, TacticalExecutionQuality.DANGEROUS} or TacticalExecutionSignal.TACTICAL_DISCIPLINE_WEAK in data.tactical_execution.signals))
        or (data.behavioral_stability is not None and (data.behavioral_stability.pressure_level in {BehavioralPressureLevel.HIGH, BehavioralPressureLevel.EXTREME} or data.behavioral_stability.recovery_state in {BehavioralRecoveryState.DETERIORATING, BehavioralRecoveryState.CRITICAL} or BehavioralRiskSignal.DISCIPLINE_DECAY in data.behavioral_stability.signals))
    )


def _alignment_unsafe(data: ArbitrationInput) -> bool:
    return data.intent_alignment is not None and (
        data.intent_alignment.mode in {IntentAlignmentMode.MISALIGNED, IntentAlignmentMode.CRITICAL_REALIGNMENT}
        or IntentRisk.ALIGNMENT_COLLAPSE in data.intent_alignment.risks
        or IntentRisk.SAFETY_BOUNDARY_DRIFT in data.intent_alignment.risks
    )


def _critical_if(condition: bool, fallback: ArbitrationSeverity) -> ArbitrationSeverity:
    return ArbitrationSeverity.CRITICAL if condition else fallback


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _input(arbitration_input: ArbitrationInput | None = None, **kwargs: Any) -> ArbitrationInput:
    if arbitration_input is not None:
        return arbitration_input
    return ArbitrationInput(**kwargs)


def _clamp(value: int | float) -> int:
    return max(0, min(100, int(round(value))))


__all__ = [
    "apply_emergency_arbitration",
    "arbitrate_strategic_decision",
    "build_priority_graph",
    "compute_arbitration_confidence",
    "compute_arbitration_priority",
    "detect_strategic_conflicts",
    "evaluate_survival_priority",
    "generate_arbitration_recommendations",
    "render_strategic_arbitration_markdown",
    "resolve_conflicts",
]
