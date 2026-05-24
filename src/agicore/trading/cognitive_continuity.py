"""Offline Autonomous Cognitive Continuity Engine for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .cognitive_continuity_models import (
    CognitiveContinuityAction,
    CognitiveContinuityAnchor,
    CognitiveContinuityEvent,
    CognitiveContinuityInput,
    CognitiveContinuityMode,
    CognitiveContinuityPlan,
    CognitiveContinuityRecommendation,
    CognitiveContinuityResult,
    CognitiveContinuityRisk,
    CognitiveContinuityScore,
    CognitiveContinuityState,
)
from .cognitive_governance_models import CognitiveAutonomyLevel, CognitiveGovernanceDecision, CognitiveGovernanceMode
from .cognitive_policy_models import CognitivePolicyMode
from .cognitive_recovery_models import CognitiveRecoveryAction, CognitiveRecoveryState
from .cognitive_resilience_models import CognitiveResilienceState
from .cognitive_stability_models import CognitiveStabilityState
from .collective_consensus_models import ConsensusDecision, ConsensusMode
from .intent_alignment_models import IntentAlignmentMode, IntentRisk
from .mission_continuity_models import ContinuityAction, ContinuityRisk, MissionContinuityMode
from .recursive_world_model_models import WorldModelDecision, WorldModelRisk
from .recovery_resilience_models import RecoveryMode
from .self_reflection_audit_models import CognitiveAuditRisk, ReflectionState
from .strategic_memory_models import StrategicDriftSignal
from .system_integrity_models import SystemIntegrityStatus


def evaluate_cognitive_continuity(
    continuity_input: CognitiveContinuityInput | None = None,
    **kwargs,
) -> CognitiveContinuityResult:
    """Run the full offline cognitive continuity pipeline."""
    data = _input(continuity_input, **kwargs)
    risks = detect_cognitive_continuity_risks(data)
    anchors = build_continuity_anchors(data, risks=risks)
    score_breakdown = compute_cognitive_continuity_score(data, risks=risks)
    score = _overall_score(score_breakdown)
    plan = build_cognitive_continuity_plan(data, anchors=anchors, risks=risks)
    actions = plan.actions
    state = _continuity_state(data, score, risks)
    mode = _continuity_mode(state, risks)
    recommendations = generate_cognitive_continuity_recommendations(data, risks=risks, state=state)
    event = CognitiveContinuityEvent(state, mode, f"cognitive continuity state={state.value}", datetime.now(UTC))
    return CognitiveContinuityResult(
        state,
        mode,
        score,
        score_breakdown,
        anchors,
        risks,
        actions,
        plan,
        recommendations,
        (event,),
        f"{state.value}: {mode.value} with continuity score {score}/100",
    )


def detect_cognitive_continuity_risks(
    continuity_input: CognitiveContinuityInput | None = None,
    **kwargs,
) -> tuple[CognitiveContinuityRisk, ...]:
    """Detect risks that break decision, memory, mission or identity continuity."""
    data = _input(continuity_input, **kwargs)
    risks: list[CognitiveContinuityRisk] = []
    if _memory_break(data):
        risks.append(CognitiveContinuityRisk.MEMORY_CONTINUITY_BREAK)
    if _decision_chain_break(data):
        risks.append(CognitiveContinuityRisk.DECISION_CHAIN_BREAK)
    if _mission_drift(data):
        risks.append(CognitiveContinuityRisk.MISSION_DRIFT)
    if _identity_drift(data):
        risks.append(CognitiveContinuityRisk.STRATEGIC_IDENTITY_DRIFT)
    if _priority_order_loss(data):
        risks.append(CognitiveContinuityRisk.PRIORITY_ORDER_LOSS)
    if _recovery_discontinuity(data):
        risks.append(CognitiveContinuityRisk.RECOVERY_DISCONTINUITY)
    if _governance_continuity_risk(data):
        risks.append(CognitiveContinuityRisk.GOVERNANCE_CONTINUITY_RISK)
    if _world_model_context_risk(data):
        risks.append(CognitiveContinuityRisk.WORLD_MODEL_CONTINUITY_RISK)
    if _consensus_context_risk(data):
        risks.append(CognitiveContinuityRisk.CONSENSUS_CONTINUITY_RISK)
    if _execution_context_loss(data):
        risks.append(CognitiveContinuityRisk.EXECUTION_CONTEXT_LOSS)
    return tuple(dict.fromkeys(risks))


def compute_cognitive_continuity_score(
    continuity_input: CognitiveContinuityInput | None = None,
    *,
    risks: tuple[CognitiveContinuityRisk, ...] | None = None,
    **kwargs,
) -> CognitiveContinuityScore:
    """Compute cognitive continuity score components."""
    data = _input(continuity_input, **kwargs)
    resolved = risks if risks is not None else detect_cognitive_continuity_risks(data)
    memory = _clamp(_memory_score(data) - 30 * _has(resolved, CognitiveContinuityRisk.MEMORY_CONTINUITY_BREAK))
    decision = _clamp(_audit_score(data) - 30 * _has(resolved, CognitiveContinuityRisk.DECISION_CHAIN_BREAK))
    mission = _clamp(_mission_score(data) - 30 * _has(resolved, CognitiveContinuityRisk.MISSION_DRIFT))
    identity = _clamp(_identity_score(data) - 30 * _has(resolved, CognitiveContinuityRisk.STRATEGIC_IDENTITY_DRIFT))
    priority = _clamp(_priority_score(data) - 30 * _has(resolved, CognitiveContinuityRisk.PRIORITY_ORDER_LOSS))
    recovery = _clamp(_recovery_score(data) - 25 * _has(resolved, CognitiveContinuityRisk.RECOVERY_DISCONTINUITY))
    governance = _clamp(_governance_score(data) - 25 * _has(resolved, CognitiveContinuityRisk.GOVERNANCE_CONTINUITY_RISK))
    world = _clamp(_world_score(data) - 30 * _has(resolved, CognitiveContinuityRisk.WORLD_MODEL_CONTINUITY_RISK))
    consensus = _clamp(_consensus_score(data) - 30 * _has(resolved, CognitiveContinuityRisk.CONSENSUS_CONTINUITY_RISK))
    return CognitiveContinuityScore(memory, decision, mission, identity, priority, recovery, governance, world, consensus)


def build_continuity_anchors(
    continuity_input: CognitiveContinuityInput | None = None,
    *,
    risks: tuple[CognitiveContinuityRisk, ...] | None = None,
    **kwargs,
) -> tuple[CognitiveContinuityAnchor, ...]:
    """Build continuity anchors for memory, mission, identity and context."""
    data = _input(continuity_input, **kwargs)
    resolved = risks if risks is not None else detect_cognitive_continuity_risks(data)
    return (
        _anchor("strategic_memory", _memory_score(data), CognitiveContinuityRisk.MEMORY_CONTINUITY_BREAK, resolved, "strategic memory continuity"),
        _anchor("decision_chain", _audit_score(data), CognitiveContinuityRisk.DECISION_CHAIN_BREAK, resolved, "decision trace and audit continuity"),
        _anchor("mission", _mission_score(data), CognitiveContinuityRisk.MISSION_DRIFT, resolved, "mission anchor continuity"),
        _anchor("strategic_identity", _identity_score(data), CognitiveContinuityRisk.STRATEGIC_IDENTITY_DRIFT, resolved, "strategy DNA and identity continuity"),
        _anchor("priority_order", _priority_score(data), CognitiveContinuityRisk.PRIORITY_ORDER_LOSS, resolved, "priority hierarchy continuity"),
        _anchor("recovery", _recovery_score(data), CognitiveContinuityRisk.RECOVERY_DISCONTINUITY, resolved, "post recovery continuity"),
        _anchor("governance", _governance_score(data), CognitiveContinuityRisk.GOVERNANCE_CONTINUITY_RISK, resolved, "governance context continuity"),
        _anchor("world_model", _world_score(data), CognitiveContinuityRisk.WORLD_MODEL_CONTINUITY_RISK, resolved, "world model context continuity"),
        _anchor("consensus", _consensus_score(data), CognitiveContinuityRisk.CONSENSUS_CONTINUITY_RISK, resolved, "consensus context continuity"),
    )


def build_cognitive_continuity_plan(
    continuity_input: CognitiveContinuityInput | None = None,
    *,
    anchors: tuple[CognitiveContinuityAnchor, ...] | None = None,
    risks: tuple[CognitiveContinuityRisk, ...] | None = None,
    **kwargs,
) -> CognitiveContinuityPlan:
    """Build a continuity preservation plan."""
    data = _input(continuity_input, **kwargs)
    resolved = risks if risks is not None else detect_cognitive_continuity_risks(data)
    resolved_anchors = anchors if anchors is not None else build_continuity_anchors(data, risks=resolved)
    actions: list[CognitiveContinuityAction] = []
    if CognitiveContinuityRisk.MEMORY_CONTINUITY_BREAK in resolved:
        actions.append(CognitiveContinuityAction.PRESERVE_STRATEGIC_MEMORY)
    if CognitiveContinuityRisk.DECISION_CHAIN_BREAK in resolved:
        actions.append(CognitiveContinuityAction.REPAIR_DECISION_CHAIN)
    if CognitiveContinuityRisk.MISSION_DRIFT in resolved:
        actions.append(CognitiveContinuityAction.RESTORE_MISSION_ANCHOR)
    if CognitiveContinuityRisk.PRIORITY_ORDER_LOSS in resolved:
        actions.append(CognitiveContinuityAction.RESTORE_PRIORITY_ORDER)
    if CognitiveContinuityRisk.STRATEGIC_IDENTITY_DRIFT in resolved:
        actions.append(CognitiveContinuityAction.PROTECT_IDENTITY_ANCHOR)
    if CognitiveContinuityRisk.WORLD_MODEL_CONTINUITY_RISK in resolved:
        actions.append(CognitiveContinuityAction.SYNC_WORLD_MODEL_CONTEXT)
    if CognitiveContinuityRisk.CONSENSUS_CONTINUITY_RISK in resolved:
        actions.append(CognitiveContinuityAction.REBUILD_CONSENSUS_CONTEXT)
    if resolved:
        actions.append(CognitiveContinuityAction.KEEP_AUTONOMY_REDUCED)
    if _human_review_required(resolved):
        actions.append(CognitiveContinuityAction.REQUIRE_HUMAN_REVIEW)
    if not actions:
        actions.append(CognitiveContinuityAction.MARK_CONTINUITY_RESTORED)
    actions_tuple = tuple(dict.fromkeys(actions))
    return CognitiveContinuityPlan(
        resolved_anchors,
        actions_tuple,
        CognitiveContinuityAction.PRESERVE_STRATEGIC_MEMORY in actions_tuple or CognitiveContinuityRisk.MEMORY_CONTINUITY_BREAK not in resolved,
        CognitiveContinuityAction.RESTORE_MISSION_ANCHOR in actions_tuple or CognitiveContinuityRisk.MISSION_DRIFT not in resolved,
        CognitiveContinuityAction.PROTECT_IDENTITY_ANCHOR in actions_tuple or CognitiveContinuityRisk.STRATEGIC_IDENTITY_DRIFT not in resolved,
        bool(resolved),
        CognitiveContinuityAction.REQUIRE_HUMAN_REVIEW in actions_tuple,
    )


def generate_cognitive_continuity_recommendations(
    continuity_input: CognitiveContinuityInput | None = None,
    *,
    risks: tuple[CognitiveContinuityRisk, ...] | None = None,
    state: CognitiveContinuityState | None = None,
    **kwargs,
) -> tuple[CognitiveContinuityRecommendation, ...]:
    """Generate continuity recommendations."""
    data = _input(continuity_input, **kwargs)
    resolved = risks if risks is not None else detect_cognitive_continuity_risks(data)
    resolved_state = state or _continuity_state(data, _overall_score(compute_cognitive_continuity_score(data, risks=resolved)), resolved)
    recommendations: list[CognitiveContinuityRecommendation] = []
    if CognitiveContinuityRisk.MEMORY_CONTINUITY_BREAK in resolved:
        recommendations.append(CognitiveContinuityRecommendation.EXTEND_MEMORY_CHECKPOINTS)
    if CognitiveContinuityRisk.MISSION_DRIFT in resolved:
        recommendations.append(CognitiveContinuityRecommendation.RESTORE_MISSION_BEFORE_ACTION)
    if CognitiveContinuityRisk.STRATEGIC_IDENTITY_DRIFT in resolved:
        recommendations.append(CognitiveContinuityRecommendation.VERIFY_IDENTITY_ANCHORS)
    if CognitiveContinuityRisk.DECISION_CHAIN_BREAK in resolved:
        recommendations.append(CognitiveContinuityRecommendation.REPAIR_DECISION_TRACE)
    if CognitiveContinuityRisk.RECOVERY_DISCONTINUITY in resolved or resolved_state == CognitiveContinuityState.RECOVERING_CONTINUITY:
        recommendations.append(CognitiveContinuityRecommendation.KEEP_RECOVERY_MODE_ACTIVE)
    if CognitiveContinuityRisk.GOVERNANCE_CONTINUITY_RISK in resolved:
        recommendations.append(CognitiveContinuityRecommendation.PROTECT_GOVERNANCE_CONTEXT)
    if CognitiveContinuityRisk.WORLD_MODEL_CONTINUITY_RISK in resolved:
        recommendations.append(CognitiveContinuityRecommendation.RECHECK_WORLD_MODEL_ALIGNMENT)
    if _human_review_required(resolved):
        recommendations.append(CognitiveContinuityRecommendation.REQUIRE_SUPERVISION)
    recommendations.append(CognitiveContinuityRecommendation.UPDATE_CONTINUITY_SNAPSHOT)
    recommendations.append(CognitiveContinuityRecommendation.CONTINUE_CONTINUITY_MONITORING)
    return tuple(dict.fromkeys(recommendations))


def render_cognitive_continuity_markdown(result: CognitiveContinuityResult) -> str:
    """Render cognitive continuity result as Markdown."""
    lines = [
        "# Autonomous Cognitive Continuity Engine",
        "",
        "## Cognitive Continuity State",
        "",
        f"- State: {result.state.value}",
        f"- Mode: {result.mode.value}",
        "",
        "## Continuity Score",
        "",
        f"- Overall: {result.continuity_score}/100",
        f"- Memory: {result.score_breakdown.memory_continuity_score}/100",
        f"- Mission: {result.score_breakdown.mission_anchor_score}/100",
        "",
        "## Continuity Anchors",
        "",
        *_bullet_lines(tuple(f"{anchor.name}: {anchor.score}/100 protected={anchor.protected}" for anchor in result.anchors)),
        "",
        "## Continuity Risks",
        "",
        *_bullet_lines(tuple(risk.value for risk in result.risks)),
        "",
        "## Continuity Plan",
        "",
        *_bullet_lines(tuple(action.value for action in result.continuity_plan.actions)),
        "",
        "## Actions",
        "",
        *_bullet_lines(tuple(action.value for action in result.actions)),
        "",
        "## Recommendations",
        "",
        *_bullet_lines(tuple(recommendation.value for recommendation in result.recommendations)),
        "",
        "## AGIcore Cognitive Continuity Outlook",
        "",
        result.summary,
    ]
    return "\n".join(lines)


def _input(continuity_input: CognitiveContinuityInput | None = None, **kwargs) -> CognitiveContinuityInput:
    if continuity_input is not None and kwargs:
        raise ValueError("Pass either CognitiveContinuityInput or keyword inputs, not both")
    if continuity_input is not None:
        return continuity_input
    return CognitiveContinuityInput(**kwargs)


def _memory_break(data: CognitiveContinuityInput) -> bool:
    risks = set(_get(data.mission_continuity, "risks", ()) or ())
    actions = set(_get(data.mission_continuity, "actions", ()) or ())
    drifts = set(_get(data.strategic_timeline_analysis, "drift_signals", ()) or ())
    return (
        ContinuityRisk.MEMORY_RISK in risks
        or ContinuityRisk.STRATEGIC_MEMORY_LOSS in risks
        or ContinuityAction.PRESERVE_MEMORY in actions
        or StrategicDriftSignal.STRATEGIC_DEGRADATION in drifts
        or _memory_score(data) < 55
    )


def _decision_chain_break(data: CognitiveContinuityInput) -> bool:
    audit_risks = set(_get(data.self_reflection_audit, "risks", ()) or ())
    return (
        CognitiveAuditRisk.INCOMPLETE_TRACEABILITY in audit_risks
        or _get(data.self_reflection_audit, "reflection_quality_score", 75) < 55
        or _value(_get(data.self_reflection_audit, "state")) in {ReflectionState.AUDIT_REQUIRED, ReflectionState.CONTRADICTORY_REFLECTION, ReflectionState.CRITICAL_REVIEW}
        or _value(_get(data.cognitive_recovery, "state")) in {CognitiveRecoveryState.PARTIAL_RECOVERY, CognitiveRecoveryState.DEGRADED_RECOVERY, CognitiveRecoveryState.FAILED_RECOVERY}
    )


def _mission_drift(data: CognitiveContinuityInput) -> bool:
    intent_risks = set(_get(data.intent_alignment, "risks", ()) or ())
    return (
        _get(data.intent_alignment, "alignment_confidence", 75) < 60
        or _value(_get(data.intent_alignment, "mode")) in {IntentAlignmentMode.PARTIAL_DRIFT, IntentAlignmentMode.STRATEGIC_DIVERGENCE, IntentAlignmentMode.MISALIGNED, IntentAlignmentMode.CRITICAL_REALIGNMENT}
        or IntentRisk.MISSION_DIVERGENCE in intent_risks
        or _value(_get(data.mission_continuity, "mode")) in {MissionContinuityMode.SURVIVAL_CONTINUITY, MissionContinuityMode.SAFE_PAUSE}
    )


def _identity_drift(data: CognitiveContinuityInput) -> bool:
    drifts = set(_get(data.strategic_timeline_analysis, "drift_signals", ()) or ())
    return (
        StrategicDriftSignal.STRATEGIC_DEGRADATION in drifts
        or StrategicDriftSignal.DANGEROUS_POLICY in drifts
        or _get(data.strategic_timeline_analysis, "strategic_health_score", 75) < 55
        or _value(_get(data.intent_alignment, "mode")) in {IntentAlignmentMode.STRATEGIC_DIVERGENCE, IntentAlignmentMode.MISALIGNED}
    )


def _priority_order_loss(data: CognitiveContinuityInput) -> bool:
    consensus_decision = _value(_get(data.collective_consensus, "decision"))
    orchestrator_decision = _value(_get(data.global_orchestrator, "decision"))
    return (
        _value(_get(data.intent_alignment, "mode")) == IntentAlignmentMode.PRIORITY_CONFLICT
        or (consensus_decision == ConsensusDecision.APPROVE_COLLECTIVE_DECISION and "SAFE" in str(orchestrator_decision))
        or (consensus_decision == ConsensusDecision.EMERGENCY_HALT and "CONTINUE" in str(orchestrator_decision))
    )


def _recovery_discontinuity(data: CognitiveContinuityInput) -> bool:
    return (
        _value(_get(data.cognitive_recovery, "state")) in {
            CognitiveRecoveryState.RECOVERING,
            CognitiveRecoveryState.PARTIAL_RECOVERY,
            CognitiveRecoveryState.DEGRADED_RECOVERY,
            CognitiveRecoveryState.SAFE_RECOVERY,
            CognitiveRecoveryState.HUMAN_REVIEW_REQUIRED,
        }
        or _value(_get(data.recovery_resilience, "mode")) in {RecoveryMode.STABILIZE, RecoveryMode.REBUILD_CONFIDENCE, RecoveryMode.SURVIVAL_MODE}
    )


def _governance_continuity_risk(data: CognitiveContinuityInput) -> bool:
    return (
        _governance_score(data) < 60
        or _value(_get(data.cognitive_governance, "mode")) in {CognitiveGovernanceMode.LOCKED_GOVERNANCE, CognitiveGovernanceMode.EMERGENCY_GOVERNANCE, CognitiveGovernanceMode.SAFE_GOVERNANCE}
        or _value(_get(data.cognitive_governance, "decision")) in {CognitiveGovernanceDecision.ENTER_LOCKED_GOVERNANCE, CognitiveGovernanceDecision.REQUIRE_HUMAN_REVIEW}
    )


def _world_model_context_risk(data: CognitiveContinuityInput) -> bool:
    world_risks = set(_get(data.recursive_world_model, "risks", ()) or ())
    return (
        _world_score(data) < 60
        or _value(_get(data.recursive_world_model, "decision")) in {WorldModelDecision.REBUILD_CAUSAL_GRAPH, WorldModelDecision.ENTER_WORLD_MODEL_SAFE_MODE, WorldModelDecision.FREEZE_RECURSIVE_UPDATES}
        or bool({WorldModelRisk.WORLD_MODEL_INCOHERENCE, WorldModelRisk.STATE_DRIFT, WorldModelRisk.ORCHESTRATION_DESYNC}.intersection(world_risks))
    )


def _consensus_context_risk(data: CognitiveContinuityInput) -> bool:
    return (
        _consensus_score(data) < 60
        or _value(_get(data.collective_consensus, "mode")) in {ConsensusMode.DEGRADED_CONSENSUS, ConsensusMode.CONSENSUS_COLLAPSE, ConsensusMode.EMERGENCY_CONSENSUS}
        or _value(_get(data.collective_consensus, "decision")) in {ConsensusDecision.NO_CONSENSUS, ConsensusDecision.BLOCK_COLLECTIVE_ACTION, ConsensusDecision.EMERGENCY_HALT}
    )


def _execution_context_loss(data: CognitiveContinuityInput) -> bool:
    return (
        _value(_get(data.system_integrity, "status")) in {SystemIntegrityStatus.COMPROMISED, SystemIntegrityStatus.ROLLBACK_RECOMMENDED}
        or _value(_get(data.cognitive_policy, "mode")) in {CognitivePolicyMode.POLICY_LOCKED, CognitivePolicyMode.POLICY_SAFE_MODE}
        or _value(_get(data.cognitive_stability, "state")) in {CognitiveStabilityState.CRITICAL, CognitiveStabilityState.COLLAPSING}
    )


def _continuity_state(
    data: CognitiveContinuityInput,
    score: int,
    risks: tuple[CognitiveContinuityRisk, ...],
) -> CognitiveContinuityState:
    if all(risk in risks for risk in (CognitiveContinuityRisk.MEMORY_CONTINUITY_BREAK, CognitiveContinuityRisk.MISSION_DRIFT, CognitiveContinuityRisk.STRATEGIC_IDENTITY_DRIFT)):
        return CognitiveContinuityState.CONTINUITY_FAILURE
    if CognitiveContinuityRisk.MISSION_DRIFT in risks:
        return CognitiveContinuityState.MISSION_AT_RISK
    if CognitiveContinuityRisk.STRATEGIC_IDENTITY_DRIFT in risks:
        return CognitiveContinuityState.IDENTITY_DRIFT
    if _value(_get(data.cognitive_recovery, "state")) in {CognitiveRecoveryState.RECOVERING, CognitiveRecoveryState.PARTIAL_RECOVERY, CognitiveRecoveryState.SAFE_RECOVERY}:
        return CognitiveContinuityState.RECOVERING_CONTINUITY
    if len(risks) >= 5 or score < 45:
        return CognitiveContinuityState.FRAGMENTED_CONTINUITY
    if len(risks) >= 2 or score < 60:
        return CognitiveContinuityState.DEGRADED_CONTINUITY
    if risks:
        return CognitiveContinuityState.WATCH
    return CognitiveContinuityState.CONTINUOUS


def _continuity_mode(
    state: CognitiveContinuityState,
    risks: tuple[CognitiveContinuityRisk, ...],
) -> CognitiveContinuityMode:
    if state == CognitiveContinuityState.CONTINUITY_FAILURE:
        return CognitiveContinuityMode.LOCKED_CONTINUITY
    if CognitiveContinuityRisk.MEMORY_CONTINUITY_BREAK in risks:
        return CognitiveContinuityMode.MEMORY_PRESERVATION
    if CognitiveContinuityRisk.MISSION_DRIFT in risks:
        return CognitiveContinuityMode.MISSION_PRESERVATION
    if CognitiveContinuityRisk.STRATEGIC_IDENTITY_DRIFT in risks:
        return CognitiveContinuityMode.IDENTITY_PRESERVATION
    if CognitiveContinuityRisk.DECISION_CHAIN_BREAK in risks:
        return CognitiveContinuityMode.DECISION_CHAIN_REPAIR
    if CognitiveContinuityRisk.RECOVERY_DISCONTINUITY in risks:
        return CognitiveContinuityMode.RECOVERY_CONTINUITY
    if risks:
        return CognitiveContinuityMode.SAFE_CONTINUITY_MODE
    return CognitiveContinuityMode.NORMAL_CONTINUITY


def _anchor(
    name: str,
    score: int,
    risk: CognitiveContinuityRisk,
    risks: tuple[CognitiveContinuityRisk, ...],
    note: str,
) -> CognitiveContinuityAnchor:
    active = risk in risks
    return CognitiveContinuityAnchor(name, _clamp(score), not active and score >= 60, risk if active else None, note)


def _human_review_required(risks: tuple[CognitiveContinuityRisk, ...]) -> bool:
    return len(risks) >= 6 or all(risk in risks for risk in (CognitiveContinuityRisk.MEMORY_CONTINUITY_BREAK, CognitiveContinuityRisk.MISSION_DRIFT, CognitiveContinuityRisk.STRATEGIC_IDENTITY_DRIFT))


def _memory_score(data: CognitiveContinuityInput) -> int:
    return _clamp(_get(data.mission_continuity, "continuity_score", _get(data.strategic_timeline_analysis, "strategic_health_score", 70)))


def _audit_score(data: CognitiveContinuityInput) -> int:
    return _clamp(_get(data.self_reflection_audit, "reflection_quality_score", _get(data.cognitive_recovery, "recovery_score", 70)))


def _mission_score(data: CognitiveContinuityInput) -> int:
    return _clamp(_get(data.intent_alignment, "alignment_confidence", _get(data.mission_continuity, "continuity_score", 70)))


def _identity_score(data: CognitiveContinuityInput) -> int:
    return _clamp(_get(data.strategic_timeline_analysis, "strategic_health_score", _get(data.intent_alignment, "strategic_goal_stability_score", 70)))


def _priority_score(data: CognitiveContinuityInput) -> int:
    return _clamp(_get(data.intent_alignment, "confidence_breakdown", object()), "priority_stability_score") if _get(data.intent_alignment, "confidence_breakdown") is not None else _mission_score(data)


def _recovery_score(data: CognitiveContinuityInput) -> int:
    return _clamp(_get(data.cognitive_recovery, "recovery_score", _get(data.recovery_resilience, "resilience_score", 70)))


def _governance_score(data: CognitiveContinuityInput) -> int:
    return _clamp(_get(data.cognitive_governance, "governance_score", 70))


def _world_score(data: CognitiveContinuityInput) -> int:
    return _clamp(_get(data.recursive_world_model, "world_model_coherence_score", 70))


def _consensus_score(data: CognitiveContinuityInput) -> int:
    return _clamp(_get(data.collective_consensus, "collective_confidence_score", 70))


def _overall_score(score: CognitiveContinuityScore) -> int:
    return _avg(
        [
            score.memory_continuity_score,
            score.decision_chain_score,
            score.mission_anchor_score,
            score.strategic_identity_score,
            score.priority_order_score,
            score.recovery_continuity_score,
            score.governance_context_score,
            score.world_model_context_score,
            score.consensus_context_score,
        ],
        50,
    )


def _has(risks: tuple[CognitiveContinuityRisk, ...], risk: CognitiveContinuityRisk) -> int:
    return 1 if risk in risks else 0


def _get(obj: Any, name: str, default: Any = None) -> Any:
    return getattr(obj, name, default) if obj is not None else default


def _value(value: Any) -> Any:
    return getattr(value, "value", value)


def _avg(values: list[int], default: int) -> int:
    values = [int(value) for value in values if value is not None]
    if not values:
        return default
    return _clamp(sum(values) / len(values))


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _clamp(value: Any, name: str | None = None, low: int = 0, high: int = 100) -> int:
    if name is not None:
        value = _get(value, name, low)
    if value is None:
        value = low
    return max(low, min(high, int(round(float(value)))))


__all__ = [
    "build_cognitive_continuity_plan",
    "build_continuity_anchors",
    "compute_cognitive_continuity_score",
    "detect_cognitive_continuity_risks",
    "evaluate_cognitive_continuity",
    "generate_cognitive_continuity_recommendations",
    "render_cognitive_continuity_markdown",
]
