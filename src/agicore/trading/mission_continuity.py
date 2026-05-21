"""Offline Autonomous Mission Continuity Engine for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .executive_brain_models import ExecutiveMode
from .hierarchical_supervisor_models import SupervisorDecision, SupervisorOverride
from .learning_governance_models import LearningGovernanceDecision, LearningGovernanceMode
from .mission_continuity_models import (
    ContinuityAction,
    ContinuityEvent,
    ContinuityModuleState,
    ContinuityRisk,
    MissionContinuityInput,
    MissionContinuityMode,
    MissionContinuityResult,
    MissionContinuityScore,
    MissionCriticality,
)
from .multi_agent_models import AgentConsensusStatus, AgentVote
from .recursive_self_evaluation_models import (
    SelfEvaluationStatus,
    SystemAutonomyRecommendation,
)
from .recovery_resilience_models import RecoveryAction, RecoveryMode, RecoveryRisk
from .strategic_memory_models import StrategicDriftSignal
from .system_integrity_models import ModuleHealthStatus, SystemIntegrityStatus


def evaluate_mission_continuity(
    continuity_input: MissionContinuityInput | None = None,
    **kwargs,
) -> MissionContinuityResult:
    """Evaluate mission continuity under normal or degraded offline operation."""
    data = _input(continuity_input, **kwargs)
    module_states = prioritize_critical_modules(data)
    score_breakdown = compute_continuity_score(data, module_states=module_states)
    risks = detect_continuity_risks(data, score_breakdown=score_breakdown, module_states=module_states)
    actions = build_continuity_plan(data, risks=risks, module_states=module_states)
    mode = _mode(data, risks, score_breakdown, module_states)
    continuity_score = _global_score(score_breakdown, risks)
    event_action = actions[0] if actions else ContinuityAction.KEEP_CORE_RUNNING
    event = ContinuityEvent(
        mode=mode,
        action=event_action,
        message=f"Mission continuity {mode.value}; score {continuity_score}/100.",
        timestamp=datetime.now(UTC),
    )
    critical_modules = tuple(state.module_name for state in module_states if state.criticality in {MissionCriticality.CRITICAL, MissionCriticality.HIGH})
    disabled_modules = tuple(state.module_name for state in module_states if not state.enabled)
    return MissionContinuityResult(
        mode=mode,
        continuity_score=continuity_score,
        score_breakdown=score_breakdown,
        risks=risks,
        actions=actions,
        module_states=module_states,
        critical_modules=critical_modules,
        disabled_modules=disabled_modules,
        recovery_preparation=_recovery_preparation(mode, risks, actions),
        recommendations=_recommendations(mode, risks, actions),
        events=(event,),
        summary=f"Mission continuity {mode.value} with score {continuity_score}/100 and {len(disabled_modules)} disabled module(s).",
    )


def detect_continuity_risks(
    continuity_input: MissionContinuityInput | None = None,
    *,
    score_breakdown: MissionContinuityScore | None = None,
    module_states: tuple[ContinuityModuleState, ...] | None = None,
    **kwargs,
) -> tuple[ContinuityRisk, ...]:
    """Detect risks that threaten essential mission continuity."""
    data = _input(continuity_input, **kwargs)
    states = module_states or prioritize_critical_modules(data)
    scores = score_breakdown or compute_continuity_score(data, module_states=states)
    risks: list[ContinuityRisk] = []

    if data.system_integrity is not None:
        if data.system_integrity.status in {SystemIntegrityStatus.COMPROMISED, SystemIntegrityStatus.PROTECTION_MODE}:
            risks.extend((ContinuityRisk.CORE_FAILURE, ContinuityRisk.CASCADING_FAILURE))
        if data.system_integrity.status == SystemIntegrityStatus.ROLLBACK_RECOMMENDED:
            risks.append(ContinuityRisk.CONTINUITY_BREAKDOWN)
        if len(data.system_integrity.modules_to_isolate) >= 2:
            risks.append(ContinuityRisk.CASCADING_FAILURE)

    if data.recovery_resilience is not None:
        if data.recovery_resilience.mode in {RecoveryMode.SURVIVAL_MODE, RecoveryMode.PAUSED_RECOVERY}:
            risks.append(ContinuityRisk.RECOVERY_LOOP)
        if RecoveryRisk.RECOVERY_FAILURE in data.recovery_resilience.risks:
            risks.append(ContinuityRisk.CONTINUITY_BREAKDOWN)

    if data.executive_result is not None and (
        data.executive_result.state.mode in {ExecutiveMode.SURVIVAL, ExecutiveMode.PAUSED}
        or data.executive_result.decision.stop_session
    ):
        risks.append(ContinuityRisk.EXECUTIVE_COLLAPSE)

    if data.supervisor_result is not None and (
        data.supervisor_result.decision in {SupervisorDecision.EMERGENCY_HALT, SupervisorDecision.OVERRIDE_TO_STOP_SESSION}
        or not data.supervisor_result.final_executable
        or any(override in {SupervisorOverride.EMERGENCY_HALT, SupervisorOverride.STOP_SESSION} for override in data.supervisor_result.applied_overrides)
    ):
        risks.append(ContinuityRisk.SUPERVISION_FAILURE)

    if data.self_evaluation is not None and (
        data.self_evaluation.status in {SelfEvaluationStatus.UNSTABLE, SelfEvaluationStatus.CONTRADICTORY, SelfEvaluationStatus.AUTONOMY_REDUCED}
        or data.self_evaluation.autonomy_recommendation in {
            SystemAutonomyRecommendation.REDUCE_AUTONOMY,
            SystemAutonomyRecommendation.OBSERVE_ONLY,
            SystemAutonomyRecommendation.FREEZE_AUTONOMY,
            SystemAutonomyRecommendation.REQUIRE_HUMAN_REVIEW,
            SystemAutonomyRecommendation.RECALIBRATE_SYSTEM,
        }
    ):
        risks.append(ContinuityRisk.AUTONOMY_UNSTABLE)

    if data.learning_governance is not None and data.learning_governance.mode in {
        LearningGovernanceMode.SAFETY_LOCKDOWN,
        LearningGovernanceMode.FREEZE_LEARNING,
    }:
        risks.append(ContinuityRisk.AUTONOMY_UNSTABLE)

    if data.strategic_timeline_analysis is not None:
        if data.strategic_timeline_analysis.snapshots_count == 0:
            risks.append(ContinuityRisk.STRATEGIC_MEMORY_LOSS)
        if data.strategic_timeline_analysis.degradation_detected or StrategicDriftSignal.PERSISTENT_DRAWDOWN in data.strategic_timeline_analysis.drift_signals:
            risks.append(ContinuityRisk.MEMORY_RISK)

    disabled_critical = [
        state for state in states if not state.enabled and state.criticality in {MissionCriticality.CRITICAL, MissionCriticality.HIGH}
    ]
    if disabled_critical:
        risks.append(ContinuityRisk.CORE_FAILURE)
    if scores.service_availability_score < 45:
        risks.append(ContinuityRisk.RESOURCE_EXHAUSTION)
    if scores.cascading_failure_resistance_score < 45:
        risks.append(ContinuityRisk.CASCADING_FAILURE)

    return tuple(dict.fromkeys(risks))


def compute_continuity_score(
    continuity_input: MissionContinuityInput | None = None,
    *,
    module_states: tuple[ContinuityModuleState, ...] | None = None,
    **kwargs,
) -> MissionContinuityScore:
    """Compute mission continuity component scores from 0..100."""
    data = _input(continuity_input, **kwargs)
    states = module_states or prioritize_critical_modules(data)
    core = 80
    memory = 80
    supervision = 80
    autonomy = 80
    recovery = 75
    service = 80
    cascading = 80

    if data.system_integrity is not None:
        core = min(core, data.system_integrity.integrity_score)
        service -= min(35, len(data.system_integrity.modules_to_isolate) * 8)
        if data.system_integrity.status in {SystemIntegrityStatus.COMPROMISED, SystemIntegrityStatus.PROTECTION_MODE}:
            core -= 30
            cascading -= 25
        elif data.system_integrity.status == SystemIntegrityStatus.UNSTABLE:
            core -= 15
            cascading -= 10

    if data.recovery_resilience is not None:
        recovery = data.recovery_resilience.resilience_score
        if data.recovery_resilience.mode in {RecoveryMode.SURVIVAL_MODE, RecoveryMode.PAUSED_RECOVERY}:
            recovery -= 20
            service -= 15
        elif data.recovery_resilience.mode == RecoveryMode.REBUILD_CONFIDENCE:
            recovery += 8

    if data.self_evaluation is not None:
        autonomy = min(autonomy, data.self_evaluation.confidence_score)
        if data.self_evaluation.autonomy_recommendation != SystemAutonomyRecommendation.MAINTAIN_AUTONOMY:
            autonomy -= 15

    if data.supervisor_result is not None:
        if not data.supervisor_result.final_executable:
            supervision -= 25
        if data.supervisor_result.critical_risks:
            supervision -= min(25, len(data.supervisor_result.critical_risks) * 7)

    if data.agent_coordination is not None:
        supervision = min(supervision, data.agent_coordination.consensus_score + 10)
        if data.agent_coordination.consensus_status == AgentConsensusStatus.NO_CONSENSUS:
            supervision -= 15

    if data.executive_result is not None:
        if data.executive_result.state.mode in {ExecutiveMode.SURVIVAL, ExecutiveMode.PAUSED}:
            core -= 20
            autonomy -= 15
        if data.executive_result.decision.stop_session:
            core -= 20

    if data.learning_governance is not None:
        if data.learning_governance.mode == LearningGovernanceMode.SAFETY_LOCKDOWN:
            autonomy -= 30
        elif data.learning_governance.mode == LearningGovernanceMode.FREEZE_LEARNING:
            autonomy -= 15

    if data.strategic_timeline_analysis is not None:
        memory = data.strategic_timeline_analysis.strategic_health_score
        if data.strategic_timeline_analysis.snapshots_count == 0:
            memory -= 35
        if data.strategic_timeline_analysis.degradation_detected:
            memory -= 15

    if data.policy_memory is not None:
        if data.policy_memory.disabled_policies:
            service -= min(20, len(data.policy_memory.disabled_policies) * 5)

    disabled_non_critical = [state for state in states if not state.enabled and state.criticality in {MissionCriticality.LOW, MissionCriticality.OPTIONAL}]
    disabled_critical = [state for state in states if not state.enabled and state.criticality in {MissionCriticality.CRITICAL, MissionCriticality.HIGH}]
    service -= min(20, len(disabled_non_critical) * 4)
    service -= min(45, len(disabled_critical) * 15)
    cascading -= min(25, len([state for state in states if state.isolated]) * 5)

    return MissionContinuityScore(
        core_continuity_score=_clamp(core),
        memory_preservation_score=_clamp(memory),
        supervision_score=_clamp(supervision),
        autonomy_stability_score=_clamp(autonomy),
        recovery_readiness_score=_clamp(recovery),
        service_availability_score=_clamp(service),
        cascading_failure_resistance_score=_clamp(cascading),
    )


def build_continuity_plan(
    continuity_input: MissionContinuityInput | None = None,
    *,
    risks: tuple[ContinuityRisk, ...] | None = None,
    module_states: tuple[ContinuityModuleState, ...] | None = None,
    **kwargs,
) -> tuple[ContinuityAction, ...]:
    """Build an ordered continuity action plan."""
    data = _input(continuity_input, **kwargs)
    states = module_states or prioritize_critical_modules(data)
    resolved_risks = risks or detect_continuity_risks(data, module_states=states)
    actions: list[ContinuityAction] = [ContinuityAction.KEEP_CORE_RUNNING, ContinuityAction.PRESERVE_MEMORY]

    if any(not state.enabled for state in states if state.criticality in {MissionCriticality.LOW, MissionCriticality.OPTIONAL}):
        actions.append(ContinuityAction.DISABLE_NON_CRITICAL)
    if data.learning_governance is not None and (
        data.learning_governance.mode in {LearningGovernanceMode.SAFETY_LOCKDOWN, LearningGovernanceMode.FREEZE_LEARNING}
        or data.learning_governance.decision in {LearningGovernanceDecision.FREEZE_POLICY_UPDATE, LearningGovernanceDecision.ENTER_SAFETY_LOCKDOWN}
    ):
        actions.append(ContinuityAction.FREEZE_LEARNING)
    if ContinuityRisk.AUTONOMY_UNSTABLE in resolved_risks or ContinuityRisk.SUPERVISION_FAILURE in resolved_risks:
        actions.append(ContinuityAction.REDUCE_AUTONOMY)
    if ContinuityRisk.CORE_FAILURE in resolved_risks or ContinuityRisk.CASCADING_FAILURE in resolved_risks:
        actions.append(ContinuityAction.ACTIVATE_SAFE_MODE)
    if any(state.isolated for state in states):
        actions.append(ContinuityAction.ISOLATE_FAILURE_DOMAIN)
    if any(not state.enabled and state.criticality in {MissionCriticality.CRITICAL, MissionCriticality.HIGH} for state in states):
        actions.append(ContinuityAction.RESTORE_ESSENTIAL_SERVICES)
    if _critical_risk_count(resolved_risks) >= 3 or ContinuityRisk.CONTINUITY_BREAKDOWN in resolved_risks:
        actions.append(ContinuityAction.REQUIRE_HUMAN_REVIEW)
    if _recovery_ready(data, resolved_risks):
        actions.append(ContinuityAction.PREPARE_RECOVERY_PHASE)

    return tuple(dict.fromkeys(actions))


def prioritize_critical_modules(
    continuity_input: MissionContinuityInput | None = None,
    **kwargs,
) -> tuple[ContinuityModuleState, ...]:
    """Prioritize vital modules and disable low-priority domains when degraded."""
    data = _input(continuity_input, **kwargs)
    degraded = _degraded(data)
    isolated = set(data.system_integrity.modules_to_isolate if data.system_integrity is not None else ())
    if data.recovery_resilience is not None:
        isolated.update(data.recovery_resilience.isolated_modules)
    module_specs = (
        ("executive_brain", MissionCriticality.CRITICAL),
        ("hierarchical_supervisor", MissionCriticality.CRITICAL),
        ("system_integrity", MissionCriticality.CRITICAL),
        ("strategic_memory_timeline", MissionCriticality.CRITICAL),
        ("recursive_self_evaluation", MissionCriticality.HIGH),
        ("learning_governance", MissionCriticality.HIGH),
        ("multi_agent_coordination", MissionCriticality.NORMAL),
        ("adaptive_policy_memory", MissionCriticality.NORMAL),
        ("policy_experimentation", MissionCriticality.LOW),
        ("paper_execution_loop", MissionCriticality.LOW),
        ("rl_playground", MissionCriticality.OPTIONAL),
        ("scenario_replay_arena", MissionCriticality.OPTIONAL),
    )
    states: list[ContinuityModuleState] = []
    for module_name, criticality in module_specs:
        is_isolated = module_name in isolated
        enabled = True
        reason = "Available for continuity operation."
        if degraded and criticality in {MissionCriticality.LOW, MissionCriticality.OPTIONAL}:
            enabled = False
            reason = "Disabled because system is degraded and module is non-critical."
        if is_isolated:
            enabled = False
            reason = "Isolated by integrity or recovery layer."
        preserved = criticality in {MissionCriticality.CRITICAL, MissionCriticality.HIGH}
        states.append(ContinuityModuleState(module_name, criticality, enabled, is_isolated, preserved, reason))
    return tuple(states)


def render_mission_continuity_markdown(result: MissionContinuityResult) -> str:
    """Render mission continuity result as Markdown."""
    lines = [
        "# Autonomous Mission Continuity Engine",
        "",
        "## Mission Continuity Status",
        "",
        f"- {result.summary}",
        "",
        "## Continuity Score",
        "",
        f"- {result.continuity_score}/100",
        "",
        "## Operating Mode",
        "",
        f"- {result.mode.value}",
        "",
        "## Critical Modules",
        "",
        *_bullet_lines(result.critical_modules),
        "",
        "## Disabled Modules",
        "",
        *_bullet_lines(result.disabled_modules),
        "",
        "## Risks Detected",
        "",
        *_bullet_lines(tuple(risk.value for risk in result.risks)),
        "",
        "## Continuity Actions",
        "",
        *_bullet_lines(tuple(action.value for action in result.actions)),
        "",
        "## Recovery Preparation",
        "",
        *_bullet_lines(result.recovery_preparation),
        "",
        "## AGIcore Recommendations",
        "",
        *_bullet_lines(result.recommendations),
        "",
        "- Offline only: no broker, no real order, no external ML, no neural training.",
        "",
    ]
    return "\n".join(lines)


def _mode(
    data: MissionContinuityInput,
    risks: tuple[ContinuityRisk, ...],
    scores: MissionContinuityScore,
    states: tuple[ContinuityModuleState, ...],
) -> MissionContinuityMode:
    critical_count = _critical_risk_count(risks)
    if ContinuityRisk.CONTINUITY_BREAKDOWN in risks or critical_count >= 5:
        return MissionContinuityMode.SAFE_PAUSE
    if critical_count >= 3 or ContinuityRisk.CORE_FAILURE in risks:
        return MissionContinuityMode.SURVIVAL_CONTINUITY
    if any(state.isolated for state in states):
        return MissionContinuityMode.ISOLATED_OPERATION
    if scores.core_continuity_score < 55 or scores.service_availability_score < 55:
        return MissionContinuityMode.ESSENTIAL_ONLY
    if _recovery_ready(data, risks):
        return MissionContinuityMode.RECOVERY_TRANSITION
    if risks or _degraded(data):
        return MissionContinuityMode.DEGRADED_OPERATION
    return MissionContinuityMode.FULL_OPERATION


def _global_score(scores: MissionContinuityScore, risks: tuple[ContinuityRisk, ...]) -> int:
    values = (
        scores.core_continuity_score,
        scores.memory_preservation_score,
        scores.supervision_score,
        scores.autonomy_stability_score,
        scores.recovery_readiness_score,
        scores.service_availability_score,
        scores.cascading_failure_resistance_score,
    )
    score = int(round(sum(values) / len(values)))
    score -= 4 * len(risks)
    score -= 5 * _critical_risk_count(risks)
    return _clamp(score)


def _degraded(data: MissionContinuityInput) -> bool:
    return bool(
        (data.system_integrity is not None and data.system_integrity.status != SystemIntegrityStatus.HEALTHY)
        or (data.recovery_resilience is not None and data.recovery_resilience.mode != RecoveryMode.NORMAL)
        or (data.self_evaluation is not None and data.self_evaluation.status != SelfEvaluationStatus.STABLE)
    )


def _recovery_ready(data: MissionContinuityInput, risks: tuple[ContinuityRisk, ...]) -> bool:
    return bool(
        data.recovery_resilience is not None
        and data.recovery_resilience.mode in {RecoveryMode.REBUILD_CONFIDENCE, RecoveryMode.STABILIZE}
        and ContinuityRisk.CORE_FAILURE not in risks
        and ContinuityRisk.CONTINUITY_BREAKDOWN not in risks
    )


def _recovery_preparation(
    mode: MissionContinuityMode,
    risks: tuple[ContinuityRisk, ...],
    actions: tuple[ContinuityAction, ...],
) -> tuple[str, ...]:
    notes: list[str] = []
    if mode == MissionContinuityMode.RECOVERY_TRANSITION:
        notes.append("Prepare transition from degraded continuity to recovery phase.")
    if ContinuityAction.PRESERVE_MEMORY in actions:
        notes.append("Preserve strategic memory and critical decision state before changes.")
    if ContinuityAction.RESTORE_ESSENTIAL_SERVICES in actions:
        notes.append("Restore critical services before optional workflows.")
    if ContinuityRisk.RECOVERY_LOOP in risks:
        notes.append("Avoid repeated recovery loops; require review before next escalation.")
    return tuple(dict.fromkeys(notes or ["No recovery transition needed."]))


def _recommendations(
    mode: MissionContinuityMode,
    risks: tuple[ContinuityRisk, ...],
    actions: tuple[ContinuityAction, ...],
) -> tuple[str, ...]:
    recommendations: list[str] = []
    if mode == MissionContinuityMode.FULL_OPERATION:
        recommendations.append("Keep full offline mission operation active.")
    elif mode == MissionContinuityMode.SAFE_PAUSE:
        recommendations.append("Pause non-essential mission activity and require human review.")
    elif mode == MissionContinuityMode.SURVIVAL_CONTINUITY:
        recommendations.append("Run only vital safety, memory and supervision functions.")
    elif mode == MissionContinuityMode.ESSENTIAL_ONLY:
        recommendations.append("Disable optional workflows and preserve essential services.")
    elif mode == MissionContinuityMode.ISOLATED_OPERATION:
        recommendations.append("Operate with isolated failure domains until module health recovers.")
    elif mode == MissionContinuityMode.RECOVERY_TRANSITION:
        recommendations.append("Prepare controlled transition into recovery phase.")
    else:
        recommendations.append("Continue degraded operation with reduced autonomy.")
    if ContinuityRisk.STRATEGIC_MEMORY_LOSS in risks or ContinuityRisk.MEMORY_RISK in risks:
        recommendations.append("Protect strategic memory snapshots before any adaptation.")
    if ContinuityAction.FREEZE_LEARNING in actions:
        recommendations.append("Keep learning frozen while continuity is degraded.")
    return tuple(dict.fromkeys(recommendations))


def _critical_risk_count(risks: tuple[ContinuityRisk, ...]) -> int:
    return sum(1 for risk in risks if risk in _critical_risks())


def _critical_risks() -> set[ContinuityRisk]:
    return {
        ContinuityRisk.CORE_FAILURE,
        ContinuityRisk.CASCADING_FAILURE,
        ContinuityRisk.EXECUTIVE_COLLAPSE,
        ContinuityRisk.STRATEGIC_MEMORY_LOSS,
        ContinuityRisk.RECOVERY_LOOP,
        ContinuityRisk.SUPERVISION_FAILURE,
        ContinuityRisk.CONTINUITY_BREAKDOWN,
    }


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _input(continuity_input: MissionContinuityInput | None = None, **kwargs: Any) -> MissionContinuityInput:
    if continuity_input is not None:
        return continuity_input
    return MissionContinuityInput(**kwargs)


def _clamp(value: int | float) -> int:
    return max(0, min(100, int(round(value))))


__all__ = [
    "build_continuity_plan",
    "compute_continuity_score",
    "detect_continuity_risks",
    "evaluate_mission_continuity",
    "prioritize_critical_modules",
    "render_mission_continuity_markdown",
]
