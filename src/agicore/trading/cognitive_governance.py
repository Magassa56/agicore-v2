"""Offline Autonomous Cognitive Governance Engine for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .cognitive_adaptation_models import CognitiveLoadLevel
from .cognitive_governance_models import (
    CognitiveAutonomyLevel,
    CognitiveGovernanceDecision,
    CognitiveGovernanceEvent,
    CognitiveGovernanceInput,
    CognitiveGovernanceMode,
    CognitiveGovernanceRecommendation,
    CognitiveGovernanceResult,
    CognitiveGovernanceRisk,
    CognitiveGovernanceScore,
    CognitivePermission,
    CognitivePolicy,
    CognitivePolicyEnforcement,
)
from .collective_consensus_models import ConsensusDecision, ConsensusMode
from .global_orchestrator_models import OrchestratorDecision, OrchestratorMode
from .intent_alignment_models import IntentAlignmentMode
from .learning_governance_models import LearningGovernanceDecision, LearningGovernanceMode
from .meta_cognition_models import MetaCognitionMode
from .mission_continuity_models import MissionContinuityMode
from .operational_awareness_models import OperationalHealthStatus
from .recovery_resilience_models import RecoveryMode
from .recursive_world_model_models import WorldModelDecision, WorldModelRisk
from .self_reflection_audit_models import CognitiveAuditRisk, ReflectionState
from .strategic_arbitration_models import ArbitrationDecision, ArbitrationMode
from .system_integrity_models import SystemIntegrityStatus


def evaluate_cognitive_governance(
    governance_input: CognitiveGovernanceInput | None = None,
    **kwargs,
) -> CognitiveGovernanceResult:
    """Run the full offline cognitive governance pipeline."""
    data = _input(governance_input, **kwargs)
    autonomy = assess_autonomy_level(data)
    permissions = build_permission_set(data, autonomy_level=autonomy)
    enforcements = enforce_cognitive_policies(data, autonomy_level=autonomy, permissions=permissions)
    risks = detect_governance_risks(data, autonomy_level=autonomy, permissions=permissions, policy_enforcements=enforcements)
    score_breakdown = compute_governance_score(data, risks=risks, policy_enforcements=enforcements)
    decision = _governance_decision(data, autonomy, risks)
    mode = _governance_mode(data, decision, autonomy, risks)
    recommendations = generate_governance_recommendations(data, decision=decision, risks=risks)
    denied = tuple(dict.fromkeys(permission for enforcement in enforcements for permission in enforcement.denied_permissions))
    score = _overall_score(score_breakdown)
    event = CognitiveGovernanceEvent(mode, decision, f"cognitive governance decision={decision.value}", datetime.now(UTC))
    return CognitiveGovernanceResult(
        mode,
        autonomy,
        decision,
        permissions,
        denied,
        enforcements,
        risks,
        score,
        score_breakdown,
        recommendations,
        (event,),
        f"{mode.value}: {decision.value} with governance score {score}/100",
    )


def assess_autonomy_level(
    governance_input: CognitiveGovernanceInput | None = None,
    **kwargs,
) -> CognitiveAutonomyLevel:
    """Assess the allowed autonomy level from audit, safety and governance evidence."""
    data = _input(governance_input, **kwargs)
    if _emergency_lock(data):
        return CognitiveAutonomyLevel.LOCKED_AUTONOMY
    if _human_review_required(data):
        return CognitiveAutonomyLevel.HUMAN_REVIEW_REQUIRED
    if _observe_only(data):
        return CognitiveAutonomyLevel.OBSERVE_ONLY
    if _supervised_required(data):
        return CognitiveAutonomyLevel.SUPERVISED_AUTONOMY
    if _limited_required(data):
        return CognitiveAutonomyLevel.LIMITED_AUTONOMY
    return CognitiveAutonomyLevel.FULL_AUTONOMY


def build_permission_set(
    governance_input: CognitiveGovernanceInput | None = None,
    *,
    autonomy_level: CognitiveAutonomyLevel | None = None,
    **kwargs,
) -> tuple[CognitivePermission, ...]:
    """Build an explainable permission set for the current autonomy level."""
    data = _input(governance_input, **kwargs)
    level = autonomy_level or assess_autonomy_level(data)
    permissions: list[CognitivePermission] = [CognitivePermission.ALLOW_ANALYSIS, CognitivePermission.REQUIRE_AUDIT_TRACE]

    if level in {CognitiveAutonomyLevel.FULL_AUTONOMY, CognitiveAutonomyLevel.LIMITED_AUTONOMY, CognitiveAutonomyLevel.SUPERVISED_AUTONOMY}:
        permissions.extend([CognitivePermission.ALLOW_PLANNING, CognitivePermission.ALLOW_FORECASTING])
    if level in {CognitiveAutonomyLevel.FULL_AUTONOMY, CognitiveAutonomyLevel.LIMITED_AUTONOMY} and not _strategy_evolution_limited(data):
        permissions.append(CognitivePermission.ALLOW_STRATEGY_EVOLUTION)
    if level == CognitiveAutonomyLevel.FULL_AUTONOMY and not _recursive_freeze_required(data):
        permissions.append(CognitivePermission.ALLOW_RECURSIVE_UPDATES)
    if level == CognitiveAutonomyLevel.FULL_AUTONOMY and not _autonomy_expansion_blocked(data):
        permissions.append(CognitivePermission.ALLOW_AUTONOMY_EXPANSION)
    if level in {CognitiveAutonomyLevel.FULL_AUTONOMY, CognitiveAutonomyLevel.LIMITED_AUTONOMY} and not _safe_mode_required(data):
        permissions.append(CognitivePermission.ALLOW_EXECUTION_ROUTING)
    if level == CognitiveAutonomyLevel.FULL_AUTONOMY and not _learning_unstable(data):
        permissions.append(CognitivePermission.ALLOW_LEARNING_UPDATE)
    if level != CognitiveAutonomyLevel.FULL_AUTONOMY or _safe_mode_required(data):
        permissions.append(CognitivePermission.DENY_HIGH_RISK_ACTIONS)
    return tuple(dict.fromkeys(permissions))


def enforce_cognitive_policies(
    governance_input: CognitiveGovernanceInput | None = None,
    *,
    autonomy_level: CognitiveAutonomyLevel | None = None,
    permissions: tuple[CognitivePermission, ...] | None = None,
    **kwargs,
) -> tuple[CognitivePolicyEnforcement, ...]:
    """Apply governance policies against the permission set."""
    data = _input(governance_input, **kwargs)
    level = autonomy_level or assess_autonomy_level(data)
    allowed_permissions = permissions or build_permission_set(data, autonomy_level=level)
    enforcements: list[CognitivePolicyEnforcement] = []

    enforcements.append(_enforcement(CognitivePolicy.OFFLINE_ONLY_POLICY, True, allowed_permissions, (), "offline cognitive operation only"))
    enforcements.append(_enforcement(CognitivePolicy.AUDIT_TRACE_POLICY, CognitivePermission.REQUIRE_AUDIT_TRACE in allowed_permissions, allowed_permissions, _deny_if_missing(allowed_permissions, CognitivePermission.REQUIRE_AUDIT_TRACE), "audit trace required"))
    enforcements.append(_enforcement(CognitivePolicy.SAFETY_FIRST_POLICY, CognitivePermission.DENY_HIGH_RISK_ACTIONS in allowed_permissions or not _safe_mode_required(data), allowed_permissions, () if CognitivePermission.DENY_HIGH_RISK_ACTIONS in allowed_permissions else (CognitivePermission.ALLOW_EXECUTION_ROUTING,), "safety must dominate high risk routing"))
    enforcements.append(_enforcement(CognitivePolicy.AUTONOMY_LIMIT_POLICY, not _autonomy_expansion_blocked(data) or CognitivePermission.ALLOW_AUTONOMY_EXPANSION not in allowed_permissions, allowed_permissions, (CognitivePermission.ALLOW_AUTONOMY_EXPANSION,) if _autonomy_expansion_blocked(data) else (), "autonomy expansion gated by alignment and audit"))
    enforcements.append(_enforcement(CognitivePolicy.RECURSIVE_UPDATE_POLICY, not _recursive_freeze_required(data) or CognitivePermission.ALLOW_RECURSIVE_UPDATES not in allowed_permissions, allowed_permissions, (CognitivePermission.ALLOW_RECURSIVE_UPDATES,) if _recursive_freeze_required(data) else (), "recursive updates gated by world model coherence"))
    enforcements.append(_enforcement(CognitivePolicy.LEARNING_UPDATE_POLICY, not _learning_unstable(data) or CognitivePermission.ALLOW_LEARNING_UPDATE not in allowed_permissions, allowed_permissions, (CognitivePermission.ALLOW_LEARNING_UPDATE,) if _learning_unstable(data) else (), "learning update gated by governance"))
    enforcements.append(_enforcement(CognitivePolicy.STRATEGY_EVOLUTION_POLICY, not _strategy_evolution_limited(data) or CognitivePermission.ALLOW_STRATEGY_EVOLUTION not in allowed_permissions, allowed_permissions, (CognitivePermission.ALLOW_STRATEGY_EVOLUTION,) if _strategy_evolution_limited(data) else (), "strategy evolution gated by stability"))
    enforcements.append(_enforcement(CognitivePolicy.EXECUTION_ROUTING_POLICY, not _safe_mode_required(data) or CognitivePermission.ALLOW_EXECUTION_ROUTING not in allowed_permissions, allowed_permissions, (CognitivePermission.ALLOW_EXECUTION_ROUTING,) if _safe_mode_required(data) else (), "execution routing blocked under safe mode"))
    return tuple(enforcements)


def detect_governance_risks(
    governance_input: CognitiveGovernanceInput | None = None,
    *,
    autonomy_level: CognitiveAutonomyLevel | None = None,
    permissions: tuple[CognitivePermission, ...] | None = None,
    policy_enforcements: tuple[CognitivePolicyEnforcement, ...] | None = None,
    **kwargs,
) -> tuple[CognitiveGovernanceRisk, ...]:
    """Detect cognitive governance risks."""
    data = _input(governance_input, **kwargs)
    level = autonomy_level or assess_autonomy_level(data)
    allowed_permissions = permissions or build_permission_set(data, autonomy_level=level)
    enforcements = policy_enforcements or enforce_cognitive_policies(data, autonomy_level=level, permissions=allowed_permissions)
    risks: list[CognitiveGovernanceRisk] = []

    if _autonomy_expansion_blocked(data) and CognitivePermission.ALLOW_AUTONOMY_EXPANSION in allowed_permissions:
        risks.append(CognitiveGovernanceRisk.AUTONOMY_ESCALATION_RISK)
    if _recursive_freeze_required(data):
        risks.append(CognitiveGovernanceRisk.RECURSIVE_DRIFT_RISK)
    if any(not enforcement.allowed for enforcement in enforcements):
        risks.append(CognitiveGovernanceRisk.POLICY_VIOLATION_RISK)
    if _unsafe_permission_set(data, allowed_permissions):
        risks.append(CognitiveGovernanceRisk.UNSAFE_PERMISSION_SET)
    if _governance_fragmented(data):
        risks.append(CognitiveGovernanceRisk.GOVERNANCE_FRAGMENTATION)
    if _audit_quality(data) < 55 or CognitivePermission.REQUIRE_AUDIT_TRACE not in allowed_permissions:
        risks.append(CognitiveGovernanceRisk.LOW_AUDITABILITY)
    if _meta_instability(data):
        risks.append(CognitiveGovernanceRisk.META_COGNITIVE_INSTABILITY)
    if _world_model_incoherent(data):
        risks.append(CognitiveGovernanceRisk.WORLD_MODEL_INCOHERENCE)
    if _safe_mode_required(data):
        risks.append(CognitiveGovernanceRisk.SYSTEM_SAFE_MODE_REQUIRED)
    if _emergency_lock(data):
        risks.append(CognitiveGovernanceRisk.EMERGENCY_LOCK_REQUIRED)
    return tuple(dict.fromkeys(risks))


def compute_governance_score(
    governance_input: CognitiveGovernanceInput | None = None,
    *,
    risks: tuple[CognitiveGovernanceRisk, ...] | None = None,
    policy_enforcements: tuple[CognitivePolicyEnforcement, ...] | None = None,
    **kwargs,
) -> CognitiveGovernanceScore:
    """Compute cognitive governance component score."""
    data = _input(governance_input, **kwargs)
    resolved_risks = risks or detect_governance_risks(data)
    enforcements = policy_enforcements or enforce_cognitive_policies(data)
    policy_pass_rate = _clamp(100 * sum(1 for enforcement in enforcements if enforcement.allowed) / max(1, len(enforcements)))
    autonomy = _clamp(85 - 15 * _risk_count(resolved_risks, {CognitiveGovernanceRisk.AUTONOMY_ESCALATION_RISK, CognitiveGovernanceRisk.UNSAFE_PERMISSION_SET}))
    audit = _audit_quality(data)
    recursive = _clamp(_world_model_score(data) - 20 * _risk_count(resolved_risks, {CognitiveGovernanceRisk.RECURSIVE_DRIFT_RISK}))
    world = _world_model_score(data)
    meta = _meta_score(data)
    safety = _system_safety_score(data)
    return CognitiveGovernanceScore(autonomy, audit, policy_pass_rate, recursive, world, meta, safety)


def generate_governance_recommendations(
    governance_input: CognitiveGovernanceInput | None = None,
    *,
    decision: CognitiveGovernanceDecision | None = None,
    risks: tuple[CognitiveGovernanceRisk, ...] | None = None,
    **kwargs,
) -> tuple[CognitiveGovernanceRecommendation, ...]:
    """Generate cognitive governance recommendations."""
    data = _input(governance_input, **kwargs)
    resolved_risks = risks or detect_governance_risks(data)
    resolved_decision = decision or _governance_decision(data, assess_autonomy_level(data), resolved_risks)
    recommendations: list[CognitiveGovernanceRecommendation] = []

    if resolved_decision in {CognitiveGovernanceDecision.REDUCE_AUTONOMY_LEVEL, CognitiveGovernanceDecision.DENY_AUTONOMY_EXPANSION} or CognitiveGovernanceRisk.AUTONOMY_ESCALATION_RISK in resolved_risks:
        recommendations.append(CognitiveGovernanceRecommendation.REDUCE_AUTONOMY)
    if CognitiveGovernanceRisk.LOW_AUDITABILITY in resolved_risks:
        recommendations.append(CognitiveGovernanceRecommendation.ENFORCE_AUDIT_TRACE)
    if CognitiveGovernanceRisk.RECURSIVE_DRIFT_RISK in resolved_risks or resolved_decision == CognitiveGovernanceDecision.FREEZE_RECURSIVE_UPDATES:
        recommendations.append(CognitiveGovernanceRecommendation.FREEZE_RECURSIVE_SYSTEMS)
    if _strategy_evolution_limited(data):
        recommendations.append(CognitiveGovernanceRecommendation.LIMIT_STRATEGY_EVOLUTION)
    if resolved_decision in {CognitiveGovernanceDecision.REQUIRE_HUMAN_REVIEW, CognitiveGovernanceDecision.APPROVE_WITH_RESTRICTIONS}:
        recommendations.append(CognitiveGovernanceRecommendation.REQUIRE_SUPERVISION)
    if CognitiveGovernanceRisk.POLICY_VIOLATION_RISK in resolved_risks or CognitiveGovernanceRisk.GOVERNANCE_FRAGMENTATION in resolved_risks:
        recommendations.append(CognitiveGovernanceRecommendation.REBUILD_GOVERNANCE_POLICY)
    if CognitiveGovernanceRisk.WORLD_MODEL_INCOHERENCE in resolved_risks:
        recommendations.append(CognitiveGovernanceRecommendation.PROTECT_WORLD_MODEL)
    if resolved_decision in {CognitiveGovernanceDecision.ENFORCE_SAFE_GOVERNANCE, CognitiveGovernanceDecision.APPROVE_WITH_RESTRICTIONS}:
        recommendations.append(CognitiveGovernanceRecommendation.MAINTAIN_SAFE_GOVERNANCE)
    if CognitiveGovernanceRisk.EMERGENCY_LOCK_REQUIRED in resolved_risks or resolved_decision == CognitiveGovernanceDecision.ENTER_LOCKED_GOVERNANCE:
        recommendations.append(CognitiveGovernanceRecommendation.ENTER_EMERGENCY_LOCK)
    recommendations.append(CognitiveGovernanceRecommendation.CONTINUE_MONITORING)
    return tuple(dict.fromkeys(recommendations))


def render_cognitive_governance_markdown(result: CognitiveGovernanceResult) -> str:
    """Render cognitive governance result as Markdown."""
    lines = [
        "# Autonomous Cognitive Governance Engine",
        "",
        "## Cognitive Governance State",
        "",
        f"- Mode: {result.mode.value}",
        f"- Decision: {result.decision.value}",
        "",
        "## Autonomy Level",
        "",
        f"- {result.autonomy_level.value}",
        "",
        "## Permission Set",
        "",
        *_bullet_lines(tuple(permission.value for permission in result.permissions)),
        "",
        "## Policy Enforcement",
        "",
        *_bullet_lines(tuple(f"{enforcement.policy.value}: allowed={enforcement.allowed}" for enforcement in result.policy_enforcements)),
        "",
        "## Governance Risks",
        "",
        *_bullet_lines(tuple(risk.value for risk in result.risks)),
        "",
        "## Governance Score",
        "",
        f"- Overall: {result.governance_score}/100",
        f"- Auditability: {result.score_breakdown.auditability_score}/100",
        f"- System safety: {result.score_breakdown.system_safety_score}/100",
        "",
        "## Decisions",
        "",
        f"- {result.decision.value}",
        "",
        "## Recommendations",
        "",
        *_bullet_lines(tuple(recommendation.value for recommendation in result.recommendations)),
        "",
        "## AGIcore Cognitive Governance Outlook",
        "",
        result.summary,
    ]
    return "\n".join(lines)


def _input(governance_input: CognitiveGovernanceInput | None = None, **kwargs) -> CognitiveGovernanceInput:
    if governance_input is not None and kwargs:
        raise ValueError("Pass either CognitiveGovernanceInput or keyword inputs, not both")
    if governance_input is not None:
        return governance_input
    return CognitiveGovernanceInput(**kwargs)


def _governance_decision(
    data: CognitiveGovernanceInput,
    autonomy: CognitiveAutonomyLevel,
    risks: tuple[CognitiveGovernanceRisk, ...],
) -> CognitiveGovernanceDecision:
    if CognitiveGovernanceRisk.EMERGENCY_LOCK_REQUIRED in risks or autonomy == CognitiveAutonomyLevel.LOCKED_AUTONOMY:
        return CognitiveGovernanceDecision.ENTER_LOCKED_GOVERNANCE
    if CognitiveGovernanceRisk.RECURSIVE_DRIFT_RISK in risks:
        return CognitiveGovernanceDecision.FREEZE_RECURSIVE_UPDATES
    if CognitiveGovernanceRisk.SYSTEM_SAFE_MODE_REQUIRED in risks:
        return CognitiveGovernanceDecision.ENFORCE_SAFE_GOVERNANCE
    if autonomy == CognitiveAutonomyLevel.HUMAN_REVIEW_REQUIRED or len(risks) >= 5:
        return CognitiveGovernanceDecision.REQUIRE_HUMAN_REVIEW
    if CognitiveGovernanceRisk.AUTONOMY_ESCALATION_RISK in risks or _autonomy_expansion_blocked(data):
        return CognitiveGovernanceDecision.DENY_AUTONOMY_EXPANSION
    if autonomy in {CognitiveAutonomyLevel.LIMITED_AUTONOMY, CognitiveAutonomyLevel.SUPERVISED_AUTONOMY, CognitiveAutonomyLevel.OBSERVE_ONLY}:
        return CognitiveGovernanceDecision.REDUCE_AUTONOMY_LEVEL
    if risks:
        return CognitiveGovernanceDecision.APPROVE_WITH_RESTRICTIONS
    return CognitiveGovernanceDecision.APPROVE_COGNITIVE_OPERATION


def _governance_mode(
    data: CognitiveGovernanceInput,
    decision: CognitiveGovernanceDecision,
    autonomy: CognitiveAutonomyLevel,
    risks: tuple[CognitiveGovernanceRisk, ...],
) -> CognitiveGovernanceMode:
    if decision == CognitiveGovernanceDecision.ENTER_LOCKED_GOVERNANCE:
        return CognitiveGovernanceMode.LOCKED_GOVERNANCE
    if CognitiveGovernanceRisk.EMERGENCY_LOCK_REQUIRED in risks:
        return CognitiveGovernanceMode.EMERGENCY_GOVERNANCE
    if decision == CognitiveGovernanceDecision.ENFORCE_SAFE_GOVERNANCE:
        return CognitiveGovernanceMode.SAFE_GOVERNANCE
    if autonomy in {CognitiveAutonomyLevel.OBSERVE_ONLY, CognitiveAutonomyLevel.LOCKED_AUTONOMY}:
        return CognitiveGovernanceMode.RESTRICTED_GOVERNANCE
    if autonomy == CognitiveAutonomyLevel.SUPERVISED_AUTONOMY or decision == CognitiveGovernanceDecision.REQUIRE_HUMAN_REVIEW:
        return CognitiveGovernanceMode.SUPERVISED_GOVERNANCE
    if risks:
        return CognitiveGovernanceMode.DEGRADED_GOVERNANCE
    return CognitiveGovernanceMode.NORMAL_GOVERNANCE


def _enforcement(
    policy: CognitivePolicy,
    allowed: bool,
    permissions: tuple[CognitivePermission, ...],
    denied: tuple[CognitivePermission, ...],
    reason: str,
) -> CognitivePolicyEnforcement:
    return CognitivePolicyEnforcement(policy, bool(allowed), permissions, tuple(dict.fromkeys(denied)), reason)


def _deny_if_missing(permissions: tuple[CognitivePermission, ...], permission: CognitivePermission) -> tuple[CognitivePermission, ...]:
    return () if permission in permissions else (permission,)


def _emergency_lock(data: CognitiveGovernanceInput) -> bool:
    return (
        data.system_integrity is not None and data.system_integrity.status in {SystemIntegrityStatus.COMPROMISED, SystemIntegrityStatus.ROLLBACK_RECOMMENDED}
    ) or (
        data.strategic_arbitration is not None and data.strategic_arbitration.decision == ArbitrationDecision.EMERGENCY_LOCKDOWN
    ) or (
        data.collective_consensus is not None and data.collective_consensus.decision == ConsensusDecision.EMERGENCY_HALT
    )


def _human_review_required(data: CognitiveGovernanceInput) -> bool:
    return (
        data.self_reflection_audit is not None and data.self_reflection_audit.state in {ReflectionState.CRITICAL_REVIEW, ReflectionState.CONTRADICTORY_REFLECTION}
    ) or (
        data.intent_alignment is not None and data.intent_alignment.mode == IntentAlignmentMode.CRITICAL_REALIGNMENT
    )


def _observe_only(data: CognitiveGovernanceInput) -> bool:
    return (
        data.learning_governance is not None and data.learning_governance.mode in {LearningGovernanceMode.OBSERVE_ONLY, LearningGovernanceMode.SAFETY_LOCKDOWN}
    ) or (
        data.mission_continuity is not None and data.mission_continuity.mode == MissionContinuityMode.SAFE_PAUSE
    )


def _supervised_required(data: CognitiveGovernanceInput) -> bool:
    return (
        data.collective_consensus is not None and data.collective_consensus.decision in {ConsensusDecision.REQUIRE_SUPERVISION, ConsensusDecision.NO_CONSENSUS}
    ) or (
        data.strategic_arbitration is not None and data.strategic_arbitration.decision == ArbitrationDecision.REQUIRE_SUPERVISION
    )


def _limited_required(data: CognitiveGovernanceInput) -> bool:
    return (
        data.self_reflection_audit is not None and data.self_reflection_audit.reflection_quality_score < 70
    ) or (
        data.operational_awareness is not None and data.operational_awareness.health_status in {OperationalHealthStatus.WARNING, OperationalHealthStatus.DEGRADED}
    ) or _world_model_incoherent(data)


def _recursive_freeze_required(data: CognitiveGovernanceInput) -> bool:
    return data.recursive_world_model is not None and (
        data.recursive_world_model.decision in {WorldModelDecision.FREEZE_RECURSIVE_UPDATES, WorldModelDecision.ENTER_WORLD_MODEL_SAFE_MODE, WorldModelDecision.REBUILD_CAUSAL_GRAPH}
        or WorldModelRisk.RECURSIVE_FEEDBACK_LOOP in data.recursive_world_model.risks
        or WorldModelRisk.WORLD_MODEL_INCOHERENCE in data.recursive_world_model.risks
    )


def _autonomy_expansion_blocked(data: CognitiveGovernanceInput) -> bool:
    return (
        data.intent_alignment is not None and (_get(data.intent_alignment, "alignment_confidence", 70) < 60 or data.intent_alignment.mode not in {IntentAlignmentMode.FULLY_ALIGNED, IntentAlignmentMode.STABLE_ALIGNMENT})
    ) or (
        data.self_reflection_audit is not None and data.self_reflection_audit.reflection_quality_score < 65
    ) or _safe_mode_required(data)


def _strategy_evolution_limited(data: CognitiveGovernanceInput) -> bool:
    return (
        data.learning_governance is not None and data.learning_governance.decision in {LearningGovernanceDecision.FREEZE_POLICY_UPDATE, LearningGovernanceDecision.LOCK_DANGEROUS_POLICY, LearningGovernanceDecision.ENTER_SAFETY_LOCKDOWN}
    ) or _safe_mode_required(data)


def _learning_unstable(data: CognitiveGovernanceInput) -> bool:
    return data.learning_governance is not None and data.learning_governance.mode in {
        LearningGovernanceMode.FREEZE_LEARNING,
        LearningGovernanceMode.SAFETY_LOCKDOWN,
        LearningGovernanceMode.RECOVERY_MODE,
    }


def _safe_mode_required(data: CognitiveGovernanceInput) -> bool:
    return (
        data.global_orchestrator is not None and data.global_orchestrator.decision in {OrchestratorDecision.ENTER_SAFE_GLOBAL_MODE, OrchestratorDecision.ACTIVATE_SURVIVAL_MODE, OrchestratorDecision.EMERGENCY_HALT_ROUTING}
    ) or (
        data.strategic_arbitration is not None and data.strategic_arbitration.mode == ArbitrationMode.EMERGENCY_LOCKDOWN
    ) or (
        data.collective_consensus is not None and data.collective_consensus.mode in {ConsensusMode.SAFETY_FIRST, ConsensusMode.EMERGENCY_CONSENSUS, ConsensusMode.CONSENSUS_COLLAPSE}
    ) or (
        data.recovery_resilience is not None and data.recovery_resilience.mode in {RecoveryMode.SURVIVAL_MODE, RecoveryMode.PAUSED_RECOVERY}
    )


def _unsafe_permission_set(data: CognitiveGovernanceInput, permissions: tuple[CognitivePermission, ...]) -> bool:
    return (
        CognitivePermission.ALLOW_AUTONOMY_EXPANSION in permissions and _autonomy_expansion_blocked(data)
    ) or (
        CognitivePermission.ALLOW_RECURSIVE_UPDATES in permissions and _recursive_freeze_required(data)
    ) or (
        CognitivePermission.ALLOW_EXECUTION_ROUTING in permissions and _safe_mode_required(data)
    )


def _governance_fragmented(data: CognitiveGovernanceInput) -> bool:
    return (
        data.collective_consensus is not None and data.collective_consensus.mode in {ConsensusMode.DEGRADED_CONSENSUS, ConsensusMode.CONSENSUS_COLLAPSE}
    ) or (
        data.global_orchestrator is not None and data.global_orchestrator.system_state.mode in {OrchestratorMode.DEGRADED_OPERATION, OrchestratorMode.EMERGENCY_ORCHESTRATION}
    )


def _meta_instability(data: CognitiveGovernanceInput) -> bool:
    return (
        data.meta_cognition is not None and (data.meta_cognition.confidence_score < 50 or data.meta_cognition.mode in {MetaCognitionMode.CONTRADICTORY, MetaCognitionMode.DEGRADED_REASONING, MetaCognitionMode.RECALIBRATION_REQUIRED})
    ) or (
        data.cognitive_adaptation is not None and data.cognitive_adaptation.load_level == CognitiveLoadLevel.OVERLOADED
    )


def _world_model_incoherent(data: CognitiveGovernanceInput) -> bool:
    return data.recursive_world_model is not None and (
        data.recursive_world_model.world_model_coherence_score < 55 or WorldModelRisk.WORLD_MODEL_INCOHERENCE in data.recursive_world_model.risks
    )


def _audit_quality(data: CognitiveGovernanceInput) -> int:
    if data.self_reflection_audit is None:
        return 45
    score = data.self_reflection_audit.reflection_quality_score
    if CognitiveAuditRisk.INCOMPLETE_TRACEABILITY in data.self_reflection_audit.risks:
        score -= 15
    return _clamp(score)


def _world_model_score(data: CognitiveGovernanceInput) -> int:
    if data.recursive_world_model is None:
        return 60
    return data.recursive_world_model.world_model_coherence_score


def _meta_score(data: CognitiveGovernanceInput) -> int:
    if data.meta_cognition is not None:
        return data.meta_cognition.confidence_score
    if data.cognitive_adaptation is not None:
        return data.cognitive_adaptation.global_score
    return 65


def _system_safety_score(data: CognitiveGovernanceInput) -> int:
    values: list[int] = []
    if data.system_integrity is not None:
        values.append(data.system_integrity.integrity_score)
    if data.mission_continuity is not None:
        values.append(data.mission_continuity.continuity_score)
    if data.recovery_resilience is not None:
        values.append(data.recovery_resilience.resilience_score)
    if data.operational_awareness is not None:
        values.append(data.operational_awareness.operational_confidence_score)
    base = _avg(values, 70)
    if _emergency_lock(data):
        base -= 35
    elif _safe_mode_required(data):
        base -= 20
    return _clamp(base)


def _overall_score(score: CognitiveGovernanceScore) -> int:
    return _avg(
        [
            score.autonomy_control_score,
            score.auditability_score,
            score.policy_compliance_score,
            score.recursive_safety_score,
            score.world_model_protection_score,
            score.meta_cognitive_stability_score,
            score.system_safety_score,
        ],
        50,
    )


def _risk_count(risks: tuple[CognitiveGovernanceRisk, ...], selected: set[CognitiveGovernanceRisk]) -> int:
    return len(selected.intersection(risks))


def _get(obj: Any, name: str, default: Any = None) -> Any:
    return getattr(obj, name, default) if obj is not None else default


def _avg(values: list[int], default: int) -> int:
    if not values:
        return default
    return _clamp(sum(values) / len(values))


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _clamp(value: float, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(round(value))))


__all__ = [
    "assess_autonomy_level",
    "build_permission_set",
    "compute_governance_score",
    "detect_governance_risks",
    "enforce_cognitive_policies",
    "evaluate_cognitive_governance",
    "generate_governance_recommendations",
    "render_cognitive_governance_markdown",
]
