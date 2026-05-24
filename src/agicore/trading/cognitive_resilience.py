"""Offline Autonomous Cognitive Resilience Engine for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .behavioral_stability_models import BehavioralPressureLevel, BehavioralRecoveryState
from .cognitive_governance_models import CognitiveGovernanceDecision, CognitiveGovernanceMode
from .cognitive_policy_models import CognitivePolicyMode, CognitivePolicyRisk
from .cognitive_resilience_models import (
    CognitiveFailureDomain,
    CognitiveRecoveryPlan,
    CognitiveResilienceAction,
    CognitiveResilienceEvent,
    CognitiveResilienceInput,
    CognitiveResilienceMode,
    CognitiveResilienceRecommendation,
    CognitiveResilienceResult,
    CognitiveResilienceRisk,
    CognitiveResilienceScore,
    CognitiveResilienceState,
)
from .cognitive_stability_models import CognitiveStabilityMode, CognitiveStabilityRisk, CognitiveStabilityState
from .collective_consensus_models import ConsensusDecision, ConsensusMode
from .global_orchestrator_models import OrchestratorDecision, OrchestratorMode
from .mission_continuity_models import ContinuityAction, ContinuityRisk, MissionContinuityMode
from .operational_awareness_models import OperationalHealthStatus
from .recursive_world_model_models import WorldModelDecision, WorldModelRisk
from .recovery_resilience_models import RecoveryMode
from .self_reflection_audit_models import CognitiveAuditRisk, ReflectionState
from .strategic_arbitration_models import ArbitrationDecision, ArbitrationMode
from .system_integrity_models import SystemIntegrityStatus


def evaluate_cognitive_resilience(
    resilience_input: CognitiveResilienceInput | None = None,
    **kwargs,
) -> CognitiveResilienceResult:
    """Run the full offline cognitive resilience pipeline."""
    data = _input(resilience_input, **kwargs)
    risks = detect_cognitive_resilience_risks(data)
    failure_domains = identify_failure_domains(data, risks=risks)
    score_breakdown = compute_cognitive_resilience_score(data, risks=risks)
    score = _overall_score(score_breakdown)
    actions = _actions_from_risks(risks)
    recovery_plan = build_cognitive_recovery_plan(data, risks=risks, failure_domains=failure_domains, actions=actions)
    state = _resilience_state(data, risks, score)
    mode = _resilience_mode(data, state, risks, recovery_plan)
    recommendations = generate_cognitive_resilience_recommendations(data, risks=risks, state=state)
    event = CognitiveResilienceEvent(state, mode, f"cognitive resilience state={state.value}", datetime.now(UTC))
    return CognitiveResilienceResult(
        state,
        mode,
        score,
        score_breakdown,
        risks,
        actions,
        failure_domains,
        recovery_plan,
        recommendations,
        (event,),
        f"{state.value}: {mode.value} with resilience score {score}/100",
    )


def detect_cognitive_resilience_risks(
    resilience_input: CognitiveResilienceInput | None = None,
    **kwargs,
) -> tuple[CognitiveResilienceRisk, ...]:
    """Detect risks that can break cognitive resilience."""
    data = _input(resilience_input, **kwargs)
    risks: list[CognitiveResilienceRisk] = []

    if _collapse_risk(data):
        risks.append(CognitiveResilienceRisk.COGNITIVE_COLLAPSE_RISK)
    if _consensus_breakdown(data):
        risks.append(CognitiveResilienceRisk.CONSENSUS_BREAKDOWN)
    if _governance_failure(data):
        risks.append(CognitiveResilienceRisk.GOVERNANCE_FAILURE)
    if _policy_failure(data):
        risks.append(CognitiveResilienceRisk.POLICY_FAILURE)
    if _world_model_failure(data):
        risks.append(CognitiveResilienceRisk.WORLD_MODEL_FAILURE)
    if _orchestration_failure(data):
        risks.append(CognitiveResilienceRisk.ORCHESTRATION_FAILURE)
    if _memory_risk(data):
        risks.append(CognitiveResilienceRisk.MEMORY_RISK)
    if _recursive_failure(data):
        risks.append(CognitiveResilienceRisk.RECURSIVE_FAILURE)
    if _strategic_drift_surge(data):
        risks.append(CognitiveResilienceRisk.STRATEGIC_DRIFT_SURGE)
    if _behavioral_destabilization(data):
        risks.append(CognitiveResilienceRisk.BEHAVIORAL_DESTABILIZATION)
    return tuple(dict.fromkeys(risks))


def compute_cognitive_resilience_score(
    resilience_input: CognitiveResilienceInput | None = None,
    *,
    risks: tuple[CognitiveResilienceRisk, ...] | None = None,
    **kwargs,
) -> CognitiveResilienceScore:
    """Compute cognitive resilience component score."""
    data = _input(resilience_input, **kwargs)
    resolved_risks = risks if risks is not None else detect_cognitive_resilience_risks(data)
    stability = _clamp(_get(data.cognitive_stability, "stability_score", 70) - 30 * _has(resolved_risks, CognitiveResilienceRisk.COGNITIVE_COLLAPSE_RISK))
    governance = _clamp(_get(data.cognitive_governance, "governance_score", 70) - 25 * _has(resolved_risks, CognitiveResilienceRisk.GOVERNANCE_FAILURE))
    policy = _clamp(_get(data.cognitive_policy, "cognitive_policy_score", 70) - 25 * _has(resolved_risks, CognitiveResilienceRisk.POLICY_FAILURE))
    consensus = _clamp(_get(data.collective_consensus, "collective_confidence_score", 70) - 30 * _has(resolved_risks, CognitiveResilienceRisk.CONSENSUS_BREAKDOWN))
    world = _clamp(_get(data.recursive_world_model, "world_model_coherence_score", 70) - 30 * _has(resolved_risks, CognitiveResilienceRisk.WORLD_MODEL_FAILURE))
    orchestration = _clamp(_get(data.global_orchestrator, "confidence_score", _get(data.operational_awareness, "operational_confidence_score", 70)) - 30 * _has(resolved_risks, CognitiveResilienceRisk.ORCHESTRATION_FAILURE))
    memory = _clamp(_get(data.mission_continuity, "continuity_score", 70) - 30 * _has(resolved_risks, CognitiveResilienceRisk.MEMORY_RISK))
    behavioral = _clamp(_get(data.behavioral_stability, "stability_score", 70) - 30 * _has(resolved_risks, CognitiveResilienceRisk.BEHAVIORAL_DESTABILIZATION))
    return CognitiveResilienceScore(stability, governance, policy, consensus, world, orchestration, memory, behavioral)


def identify_failure_domains(
    resilience_input: CognitiveResilienceInput | None = None,
    *,
    risks: tuple[CognitiveResilienceRisk, ...] | None = None,
    **kwargs,
) -> tuple[CognitiveFailureDomain, ...]:
    """Identify failure domains to isolate or monitor."""
    data = _input(resilience_input, **kwargs)
    resolved_risks = risks if risks is not None else detect_cognitive_resilience_risks(data)
    domains: list[CognitiveFailureDomain] = []
    mapping = {
        CognitiveResilienceRisk.CONSENSUS_BREAKDOWN: ("collective_consensus", 85, CognitiveResilienceAction.REBUILD_MINIMAL_CONSENSUS, "minimal consensus must be rebuilt"),
        CognitiveResilienceRisk.GOVERNANCE_FAILURE: ("cognitive_governance", 90, CognitiveResilienceAction.REDUCE_AUTONOMY, "governance failed or entered emergency mode"),
        CognitiveResilienceRisk.POLICY_FAILURE: ("cognitive_policy", 80, CognitiveResilienceAction.FREEZE_STRATEGY_EVOLUTION, "policy set is fragmented or locked"),
        CognitiveResilienceRisk.WORLD_MODEL_FAILURE: ("recursive_world_model", 85, CognitiveResilienceAction.FREEZE_RECURSIVE_UPDATES, "world model coherence is unsafe"),
        CognitiveResilienceRisk.ORCHESTRATION_FAILURE: ("global_orchestrator", 90, CognitiveResilienceAction.ISOLATE_FAILURE_DOMAIN, "orchestration entered emergency or survival mode"),
        CognitiveResilienceRisk.MEMORY_RISK: ("mission_memory", 80, CognitiveResilienceAction.PROTECT_CRITICAL_MEMORY, "mission continuity reports memory risk"),
        CognitiveResilienceRisk.RECURSIVE_FAILURE: ("recursive_feedback", 95, CognitiveResilienceAction.FREEZE_RECURSIVE_UPDATES, "recursive loop risk threatens stability"),
        CognitiveResilienceRisk.STRATEGIC_DRIFT_SURGE: ("intent_alignment", 70, CognitiveResilienceAction.RESTORE_STABLE_BASELINE, "strategic alignment is drifting"),
        CognitiveResilienceRisk.BEHAVIORAL_DESTABILIZATION: ("behavioral_stability", 75, CognitiveResilienceAction.REDUCE_AUTONOMY, "behavioral pressure destabilizes decisions"),
        CognitiveResilienceRisk.COGNITIVE_COLLAPSE_RISK: ("cognitive_stability", 100, CognitiveResilienceAction.ENTER_COGNITIVE_SURVIVAL_MODE, "cognitive stability is critical or collapsing"),
    }
    for risk in resolved_risks:
        name, severity, action, reason = mapping[risk]
        domains.append(CognitiveFailureDomain(name, risk, severity, severity >= 80, action, reason))
    return tuple(sorted(domains, key=lambda domain: domain.severity_score, reverse=True))


def build_cognitive_recovery_plan(
    resilience_input: CognitiveResilienceInput | None = None,
    *,
    risks: tuple[CognitiveResilienceRisk, ...] | None = None,
    failure_domains: tuple[CognitiveFailureDomain, ...] | None = None,
    actions: tuple[CognitiveResilienceAction, ...] | None = None,
    **kwargs,
) -> CognitiveRecoveryPlan:
    """Build an ordered recovery plan for cognitive continuity."""
    data = _input(resilience_input, **kwargs)
    resolved_risks = risks if risks is not None else detect_cognitive_resilience_risks(data)
    domains = failure_domains if failure_domains is not None else identify_failure_domains(data, risks=resolved_risks)
    resolved_actions = actions if actions is not None else _actions_from_risks(resolved_risks)
    ordered = _ordered_actions(resolved_actions)
    return CognitiveRecoveryPlan(
        ordered,
        domains,
        CognitiveResilienceRisk.MEMORY_RISK in resolved_risks,
        CognitiveResilienceRisk.CONSENSUS_BREAKDOWN in resolved_risks,
        CognitiveResilienceRisk.RECURSIVE_FAILURE in resolved_risks or CognitiveResilienceRisk.WORLD_MODEL_FAILURE in resolved_risks,
        CognitiveResilienceRisk.COGNITIVE_COLLAPSE_RISK in resolved_risks or len(resolved_risks) >= 5,
    )


def generate_cognitive_resilience_recommendations(
    resilience_input: CognitiveResilienceInput | None = None,
    *,
    risks: tuple[CognitiveResilienceRisk, ...] | None = None,
    state: CognitiveResilienceState | None = None,
    **kwargs,
) -> tuple[CognitiveResilienceRecommendation, ...]:
    """Generate cognitive resilience recommendations."""
    data = _input(resilience_input, **kwargs)
    resolved_risks = risks if risks is not None else detect_cognitive_resilience_risks(data)
    resolved_state = state or _resilience_state(data, resolved_risks, _overall_score(compute_cognitive_resilience_score(data, risks=resolved_risks)))
    recommendations: list[CognitiveResilienceRecommendation] = []
    if CognitiveResilienceRisk.GOVERNANCE_FAILURE in resolved_risks:
        recommendations.append(CognitiveResilienceRecommendation.STABILIZE_GOVERNANCE)
    if CognitiveResilienceRisk.CONSENSUS_BREAKDOWN in resolved_risks:
        recommendations.append(CognitiveResilienceRecommendation.REBUILD_CONSENSUS_LAYER)
    if CognitiveResilienceRisk.WORLD_MODEL_FAILURE in resolved_risks or CognitiveResilienceRisk.RECURSIVE_FAILURE in resolved_risks:
        recommendations.append(CognitiveResilienceRecommendation.PROTECT_WORLD_MODEL)
        recommendations.append(CognitiveResilienceRecommendation.REDUCE_RECURSIVE_DEPTH)
    if CognitiveResilienceRisk.POLICY_FAILURE in resolved_risks:
        recommendations.append(CognitiveResilienceRecommendation.LOCK_HIGH_RISK_POLICIES)
    if CognitiveResilienceRisk.MEMORY_RISK in resolved_risks:
        recommendations.append(CognitiveResilienceRecommendation.PRESERVE_STRATEGIC_MEMORY)
    if resolved_state in {CognitiveResilienceState.CRITICAL, CognitiveResilienceState.COGNITIVE_SURVIVAL, CognitiveResilienceState.RECOVERING}:
        recommendations.append(CognitiveResilienceRecommendation.INITIATE_COGNITIVE_RECOVERY)
    if resolved_state in {CognitiveResilienceState.CRITICAL, CognitiveResilienceState.COGNITIVE_SURVIVAL}:
        recommendations.append(CognitiveResilienceRecommendation.REQUIRE_SUPERVISION)
    recommendations.append(CognitiveResilienceRecommendation.RECHECK_SYSTEM_STABILITY)
    recommendations.append(CognitiveResilienceRecommendation.CONTINUE_RESILIENCE_MONITORING)
    return tuple(dict.fromkeys(recommendations))


def render_cognitive_resilience_markdown(result: CognitiveResilienceResult) -> str:
    """Render cognitive resilience result as Markdown."""
    lines = [
        "# Autonomous Cognitive Resilience Engine",
        "",
        "## Cognitive Resilience State",
        "",
        f"- State: {result.state.value}",
        f"- Mode: {result.mode.value}",
        "",
        "## Resilience Score",
        "",
        f"- Overall: {result.resilience_score}/100",
        f"- Stability: {result.score_breakdown.stability_resilience_score}/100",
        f"- Memory: {result.score_breakdown.memory_resilience_score}/100",
        "",
        "## Failure Domains",
        "",
        *_bullet_lines(tuple(f"{domain.name}: {domain.risk.value} severity={domain.severity_score}" for domain in result.failure_domains)),
        "",
        "## Risks",
        "",
        *_bullet_lines(tuple(risk.value for risk in result.risks)),
        "",
        "## Recovery Plan",
        "",
        *_bullet_lines(tuple(action.value for action in result.recovery_plan.steps)),
        "",
        "## Actions",
        "",
        *_bullet_lines(tuple(action.value for action in result.actions)),
        "",
        "## Recommendations",
        "",
        *_bullet_lines(tuple(recommendation.value for recommendation in result.recommendations)),
        "",
        "## AGIcore Cognitive Resilience Outlook",
        "",
        result.summary,
    ]
    return "\n".join(lines)


def _input(resilience_input: CognitiveResilienceInput | None = None, **kwargs) -> CognitiveResilienceInput:
    if resilience_input is not None and kwargs:
        raise ValueError("Pass either CognitiveResilienceInput or keyword inputs, not both")
    if resilience_input is not None:
        return resilience_input
    return CognitiveResilienceInput(**kwargs)


def _collapse_risk(data: CognitiveResilienceInput) -> bool:
    return (
        _value(_get(data.cognitive_stability, "state")) in {CognitiveStabilityState.CRITICAL, CognitiveStabilityState.COLLAPSING}
        or _value(_get(data.cognitive_stability, "mode")) in {CognitiveStabilityMode.EMERGENCY_STABILIZATION, CognitiveStabilityMode.LOCKED_STABILITY}
        or _get(data.cognitive_stability, "stability_score", 70) < 35
        or _value(_get(data.system_integrity, "status")) in {SystemIntegrityStatus.COMPROMISED, SystemIntegrityStatus.ROLLBACK_RECOMMENDED}
    )


def _consensus_breakdown(data: CognitiveResilienceInput) -> bool:
    return (
        _get(data.collective_consensus, "collective_confidence_score", 70) < 50
        or _value(_get(data.collective_consensus, "mode")) in {ConsensusMode.CONSENSUS_COLLAPSE, ConsensusMode.EMERGENCY_CONSENSUS, ConsensusMode.DEGRADED_CONSENSUS}
        or _value(_get(data.collective_consensus, "decision")) in {ConsensusDecision.NO_CONSENSUS, ConsensusDecision.BLOCK_COLLECTIVE_ACTION, ConsensusDecision.EMERGENCY_HALT}
    )


def _governance_failure(data: CognitiveResilienceInput) -> bool:
    return (
        _value(_get(data.cognitive_governance, "mode")) in {CognitiveGovernanceMode.EMERGENCY_GOVERNANCE, CognitiveGovernanceMode.LOCKED_GOVERNANCE}
        or _value(_get(data.cognitive_governance, "decision")) in {CognitiveGovernanceDecision.ENTER_LOCKED_GOVERNANCE, CognitiveGovernanceDecision.REQUIRE_HUMAN_REVIEW}
        or _get(data.cognitive_governance, "governance_score", 70) < 40
    )


def _policy_failure(data: CognitiveResilienceInput) -> bool:
    policy_risks = set(_get(data.cognitive_policy, "risks", ()) or ())
    violations = tuple(_get(data.cognitive_policy, "violations", ()) or ())
    return (
        _value(_get(data.cognitive_policy, "mode")) in {CognitivePolicyMode.POLICY_LOCKED, CognitivePolicyMode.POLICY_SAFE_MODE}
        or len(violations) >= 2
        or bool({CognitivePolicyRisk.POLICY_CONFLICT, CognitivePolicyRisk.SAFETY_CRITICAL_BYPASS, CognitivePolicyRisk.GOVERNANCE_POLICY_MISMATCH}.intersection(policy_risks))
    )


def _world_model_failure(data: CognitiveResilienceInput) -> bool:
    risks = set(_get(data.recursive_world_model, "risks", ()) or ())
    return (
        _get(data.recursive_world_model, "world_model_coherence_score", 70) < 45
        or _value(_get(data.recursive_world_model, "decision")) in {WorldModelDecision.ENTER_WORLD_MODEL_SAFE_MODE, WorldModelDecision.REBUILD_CAUSAL_GRAPH}
        or bool({WorldModelRisk.WORLD_MODEL_INCOHERENCE, WorldModelRisk.SAFETY_MODEL_FAILURE}.intersection(risks))
    )


def _orchestration_failure(data: CognitiveResilienceInput) -> bool:
    return (
        _get(data.global_orchestrator, "confidence_score", 70) < 45
        or _value(_get(data.global_orchestrator, "decision")) in {OrchestratorDecision.ACTIVATE_SURVIVAL_MODE, OrchestratorDecision.EMERGENCY_HALT_ROUTING}
        or _value(_get(data.global_orchestrator, "system_state", object()), "mode") in {OrchestratorMode.EMERGENCY_ORCHESTRATION, OrchestratorMode.SURVIVAL_ORCHESTRATION}
        or _value(_get(data.strategic_arbitration, "mode")) == ArbitrationMode.EMERGENCY_LOCKDOWN
        or _value(_get(data.strategic_arbitration, "decision")) == ArbitrationDecision.EMERGENCY_LOCKDOWN
    )


def _memory_risk(data: CognitiveResilienceInput) -> bool:
    risks = set(_get(data.mission_continuity, "risks", ()) or ())
    actions = set(_get(data.mission_continuity, "actions", ()) or ())
    return (
        ContinuityRisk.MEMORY_RISK in risks
        or ContinuityRisk.STRATEGIC_MEMORY_LOSS in risks
        or ContinuityAction.PRESERVE_MEMORY in actions
        or _value(_get(data.mission_continuity, "mode")) in {MissionContinuityMode.ESSENTIAL_ONLY, MissionContinuityMode.SURVIVAL_CONTINUITY}
    )


def _recursive_failure(data: CognitiveResilienceInput) -> bool:
    stability_risks = set(_get(data.cognitive_stability, "risks", ()) or ())
    world_risks = set(_get(data.recursive_world_model, "risks", ()) or ())
    audit_risks = set(_get(data.self_reflection_audit, "risks", ()) or ())
    return (
        CognitiveStabilityRisk.RUNAWAY_RECURSION in stability_risks
        or CognitiveStabilityRisk.RECURSIVE_INSTABILITY in stability_risks
        or WorldModelRisk.RECURSIVE_FEEDBACK_LOOP in world_risks
        or CognitiveAuditRisk.WORLD_MODEL_DRIFT in audit_risks
        or _value(_get(data.recursive_world_model, "decision")) == WorldModelDecision.FREEZE_RECURSIVE_UPDATES
    )


def _strategic_drift_surge(data: CognitiveResilienceInput) -> bool:
    return (
        _get(data.intent_alignment, "alignment_confidence", 70) < 45
        or "DRIFT" in str(_value(_get(data.intent_alignment, "mode")))
        or _value(_get(data.self_reflection_audit, "state")) in {ReflectionState.CONTRADICTORY_REFLECTION, ReflectionState.SELF_CORRECTION_NEEDED}
    )


def _behavioral_destabilization(data: CognitiveResilienceInput) -> bool:
    return (
        _get(data.behavioral_stability, "stability_score", 70) < 45
        or _value(_get(data.behavioral_stability, "pressure_level")) in {BehavioralPressureLevel.HIGH, BehavioralPressureLevel.EXTREME}
        or _value(_get(data.behavioral_stability, "recovery_state")) in {BehavioralRecoveryState.DETERIORATING, BehavioralRecoveryState.CRITICAL}
    )


def _actions_from_risks(risks: tuple[CognitiveResilienceRisk, ...]) -> tuple[CognitiveResilienceAction, ...]:
    actions: list[CognitiveResilienceAction] = []
    if not risks:
        actions.append(CognitiveResilienceAction.KEEP_RUNNING)
    if CognitiveResilienceRisk.COGNITIVE_COLLAPSE_RISK in risks:
        actions.append(CognitiveResilienceAction.ENTER_COGNITIVE_SURVIVAL_MODE)
        actions.append(CognitiveResilienceAction.REQUIRE_HUMAN_REVIEW)
    if any(risk in risks for risk in (CognitiveResilienceRisk.GOVERNANCE_FAILURE, CognitiveResilienceRisk.BEHAVIORAL_DESTABILIZATION, CognitiveResilienceRisk.STRATEGIC_DRIFT_SURGE)):
        actions.append(CognitiveResilienceAction.REDUCE_AUTONOMY)
    if any(risk in risks for risk in (CognitiveResilienceRisk.POLICY_FAILURE, CognitiveResilienceRisk.ORCHESTRATION_FAILURE, CognitiveResilienceRisk.WORLD_MODEL_FAILURE)):
        actions.append(CognitiveResilienceAction.ISOLATE_FAILURE_DOMAIN)
    if CognitiveResilienceRisk.MEMORY_RISK in risks:
        actions.append(CognitiveResilienceAction.PROTECT_CRITICAL_MEMORY)
    if CognitiveResilienceRisk.CONSENSUS_BREAKDOWN in risks:
        actions.append(CognitiveResilienceAction.REBUILD_MINIMAL_CONSENSUS)
    if CognitiveResilienceRisk.RECURSIVE_FAILURE in risks or CognitiveResilienceRisk.WORLD_MODEL_FAILURE in risks:
        actions.append(CognitiveResilienceAction.FREEZE_RECURSIVE_UPDATES)
    if CognitiveResilienceRisk.POLICY_FAILURE in risks:
        actions.append(CognitiveResilienceAction.FREEZE_STRATEGY_EVOLUTION)
    if risks:
        actions.append(CognitiveResilienceAction.RESTORE_STABLE_BASELINE)
    return tuple(dict.fromkeys(actions))


def _ordered_actions(actions: tuple[CognitiveResilienceAction, ...]) -> tuple[CognitiveResilienceAction, ...]:
    order = (
        CognitiveResilienceAction.ENTER_COGNITIVE_SURVIVAL_MODE,
        CognitiveResilienceAction.REQUIRE_HUMAN_REVIEW,
        CognitiveResilienceAction.PROTECT_CRITICAL_MEMORY,
        CognitiveResilienceAction.FREEZE_RECURSIVE_UPDATES,
        CognitiveResilienceAction.REBUILD_MINIMAL_CONSENSUS,
        CognitiveResilienceAction.ISOLATE_FAILURE_DOMAIN,
        CognitiveResilienceAction.FREEZE_STRATEGY_EVOLUTION,
        CognitiveResilienceAction.REDUCE_AUTONOMY,
        CognitiveResilienceAction.RESTORE_STABLE_BASELINE,
        CognitiveResilienceAction.KEEP_RUNNING,
    )
    selected = set(actions)
    return tuple(action for action in order if action in selected)


def _resilience_state(data: CognitiveResilienceInput, risks: tuple[CognitiveResilienceRisk, ...], score: int) -> CognitiveResilienceState:
    if CognitiveResilienceRisk.COGNITIVE_COLLAPSE_RISK in risks and len(risks) >= 3:
        return CognitiveResilienceState.COGNITIVE_SURVIVAL
    if CognitiveResilienceRisk.COGNITIVE_COLLAPSE_RISK in risks or score < 35:
        return CognitiveResilienceState.CRITICAL
    if _value(_get(data.recovery_resilience, "mode")) in {RecoveryMode.STABILIZE, RecoveryMode.REBUILD_CONFIDENCE}:
        return CognitiveResilienceState.RECOVERING
    if len(risks) >= 4 or score < 50:
        return CognitiveResilienceState.FRAGILE
    if len(risks) >= 2 or score < 65:
        return CognitiveResilienceState.DEGRADED
    if risks:
        return CognitiveResilienceState.WATCH
    return CognitiveResilienceState.RESILIENT


def _resilience_mode(
    data: CognitiveResilienceInput,
    state: CognitiveResilienceState,
    risks: tuple[CognitiveResilienceRisk, ...],
    plan: CognitiveRecoveryPlan,
) -> CognitiveResilienceMode:
    if state == CognitiveResilienceState.COGNITIVE_SURVIVAL:
        return CognitiveResilienceMode.SURVIVAL_COGNITION
    if state == CognitiveResilienceState.CRITICAL:
        return CognitiveResilienceMode.LOCKED_RESILIENCE
    if plan.protected_memory:
        return CognitiveResilienceMode.PROTECT_MEMORY
    if CognitiveResilienceRisk.CONSENSUS_BREAKDOWN in risks:
        return CognitiveResilienceMode.REBUILD_CONSENSUS
    if any(domain.isolate for domain in plan.failure_domains):
        return CognitiveResilienceMode.ISOLATE_FAILURES
    if state == CognitiveResilienceState.RECOVERING:
        return CognitiveResilienceMode.STABILIZE_COGNITION
    if state in {CognitiveResilienceState.DEGRADED, CognitiveResilienceState.FRAGILE}:
        return CognitiveResilienceMode.STABILIZE_COGNITION
    if state == CognitiveResilienceState.WATCH:
        return CognitiveResilienceMode.MONITORING_RESILIENCE
    return CognitiveResilienceMode.NORMAL_RESILIENCE


def _overall_score(score: CognitiveResilienceScore) -> int:
    return _avg(
        [
            score.stability_resilience_score,
            score.governance_resilience_score,
            score.policy_resilience_score,
            score.consensus_resilience_score,
            score.world_model_resilience_score,
            score.orchestration_resilience_score,
            score.memory_resilience_score,
            score.behavioral_resilience_score,
        ],
        50,
    )


def _has(risks: tuple[CognitiveResilienceRisk, ...], risk: CognitiveResilienceRisk) -> int:
    return 1 if risk in risks else 0


def _get(obj: Any, name: str, default: Any = None) -> Any:
    return getattr(obj, name, default) if obj is not None else default


def _value(value: Any, nested: str | None = None) -> Any:
    if nested is not None:
        value = _get(value, nested)
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


def _clamp(value: float | int | None, low: int = 0, high: int = 100) -> int:
    if value is None:
        value = low
    return max(low, min(high, int(round(float(value)))))


__all__ = [
    "build_cognitive_recovery_plan",
    "compute_cognitive_resilience_score",
    "detect_cognitive_resilience_risks",
    "evaluate_cognitive_resilience",
    "generate_cognitive_resilience_recommendations",
    "identify_failure_domains",
    "render_cognitive_resilience_markdown",
]
