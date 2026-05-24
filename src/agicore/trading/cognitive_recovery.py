"""Offline Autonomous Cognitive Recovery Engine for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .cognitive_governance_models import CognitiveAutonomyLevel, CognitiveGovernanceDecision, CognitiveGovernanceMode
from .cognitive_policy_models import CognitivePolicyDecision, CognitivePolicyMode, CognitivePolicyRisk, CognitivePolicyScope
from .cognitive_recovery_models import (
    CognitiveRecoveryAction,
    CognitiveRecoveryCheckpoint,
    CognitiveRecoveryEvent,
    CognitiveRecoveryInput,
    CognitiveRecoveryMode,
    CognitiveRecoveryPlan,
    CognitiveRecoveryRecommendation,
    CognitiveRecoveryResult,
    CognitiveRecoveryRisk,
    CognitiveRecoveryScore,
    CognitiveRecoveryState,
    CognitiveRecoveryStep,
)
from .cognitive_resilience_models import CognitiveResilienceAction, CognitiveResilienceState
from .cognitive_stability_models import CognitiveStabilityMode, CognitiveStabilityRisk, CognitiveStabilityState
from .collective_consensus_models import ConsensusDecision, ConsensusMode
from .global_orchestrator_models import OrchestratorDecision, OrchestratorMode
from .mission_continuity_models import ContinuityAction, ContinuityRisk, MissionContinuityMode
from .recursive_world_model_models import WorldModelDecision, WorldModelRisk
from .recovery_resilience_models import RecoveryMode
from .strategic_arbitration_models import ArbitrationDecision, ArbitrationMode
from .system_integrity_models import SystemIntegrityStatus


def evaluate_cognitive_recovery(
    recovery_input: CognitiveRecoveryInput | None = None,
    **kwargs,
) -> CognitiveRecoveryResult:
    """Run the full offline cognitive recovery pipeline."""
    data = _input(recovery_input, **kwargs)
    risks = detect_cognitive_recovery_risks(data)
    checkpoints = build_recovery_checkpoints(data)
    score_breakdown = compute_cognitive_recovery_score(data, risks=risks)
    score = _overall_score(score_breakdown)
    plan = build_cognitive_recovery_plan(data, risks=risks, checkpoints=checkpoints)
    actions = tuple(dict.fromkeys(step.action for step in plan.steps))
    state = _recovery_state(data, score, risks, plan)
    mode = _recovery_mode(data, state, risks)
    recommendations = generate_cognitive_recovery_recommendations(data, risks=risks, state=state)
    event = CognitiveRecoveryEvent(state, mode, f"cognitive recovery state={state.value}", datetime.now(UTC))
    return CognitiveRecoveryResult(
        state,
        mode,
        score,
        score_breakdown,
        risks,
        actions,
        plan,
        checkpoints,
        recommendations,
        (event,),
        f"{state.value}: {mode.value} with recovery score {score}/100",
    )


def detect_cognitive_recovery_risks(
    recovery_input: CognitiveRecoveryInput | None = None,
    **kwargs,
) -> tuple[CognitiveRecoveryRisk, ...]:
    """Detect risks that can block or corrupt cognitive recovery."""
    data = _input(recovery_input, **kwargs)
    risks: list[CognitiveRecoveryRisk] = []

    if _recovery_loop(data):
        risks.append(CognitiveRecoveryRisk.RECOVERY_LOOP)
    if _recovery_failure(data):
        risks.append(CognitiveRecoveryRisk.RECOVERY_FAILURE)
    if _consensus_rebuild_failure(data):
        risks.append(CognitiveRecoveryRisk.CONSENSUS_REBUILD_FAILURE)
    if _governance_restore_failure(data):
        risks.append(CognitiveRecoveryRisk.GOVERNANCE_RESTORE_FAILURE)
    if _policy_repair_failure(data):
        risks.append(CognitiveRecoveryRisk.POLICY_REPAIR_FAILURE)
    if _world_model_restore_failure(data):
        risks.append(CognitiveRecoveryRisk.WORLD_MODEL_RESTORE_FAILURE)
    if _stability_rebuild_failure(data):
        risks.append(CognitiveRecoveryRisk.STABILITY_REBUILD_FAILURE)
    if _memory_restore_risk(data):
        risks.append(CognitiveRecoveryRisk.MEMORY_RESTORE_RISK)
    if _unsafe_recovery_path(data):
        risks.append(CognitiveRecoveryRisk.UNSAFE_RECOVERY_PATH)
    if _premature_reactivation(data):
        risks.append(CognitiveRecoveryRisk.PREMATURE_REACTIVATION)
    return tuple(dict.fromkeys(risks))


def build_cognitive_recovery_plan(
    recovery_input: CognitiveRecoveryInput | None = None,
    *,
    risks: tuple[CognitiveRecoveryRisk, ...] | None = None,
    checkpoints: tuple[CognitiveRecoveryCheckpoint, ...] | None = None,
    **kwargs,
) -> CognitiveRecoveryPlan:
    """Build an ordered deep recovery plan."""
    data = _input(recovery_input, **kwargs)
    resolved_risks = risks if risks is not None else detect_cognitive_recovery_risks(data)
    resolved_checkpoints = checkpoints if checkpoints is not None else build_recovery_checkpoints(data)
    steps: list[CognitiveRecoveryStep] = []

    if _minimal_core_required(data, resolved_risks):
        steps.append(_step(1, CognitiveRecoveryAction.REBUILD_MINIMAL_CORE, "minimal_core", "resilience is critical or survival mode is active"))
    if CognitiveRecoveryRisk.CONSENSUS_REBUILD_FAILURE in resolved_risks or _consensus_needs_rebuild(data):
        steps.append(_step(2, CognitiveRecoveryAction.RESTORE_CONSENSUS, "collective_consensus", "consensus must be restored before autonomy expansion"))
    if CognitiveRecoveryRisk.GOVERNANCE_RESTORE_FAILURE in resolved_risks or _governance_needs_restore(data):
        steps.append(_step(3, CognitiveRecoveryAction.RESTORE_GOVERNANCE, "cognitive_governance", "governance must be restored before policy repair"))
    if CognitiveRecoveryRisk.POLICY_REPAIR_FAILURE in resolved_risks or _policy_needs_repair(data):
        steps.append(_step(4, CognitiveRecoveryAction.REPAIR_POLICIES, "cognitive_policy", "policy set must be repaired before routing or strategy evolution"))
    if CognitiveRecoveryRisk.WORLD_MODEL_RESTORE_FAILURE in resolved_risks or _world_model_needs_restore(data):
        steps.append(_step(5, CognitiveRecoveryAction.RESTORE_WORLD_MODEL, "recursive_world_model", "world model must be valid before action routing"))
    if CognitiveRecoveryRisk.STABILITY_REBUILD_FAILURE in resolved_risks or _stability_needs_rebuild(data):
        steps.append(_step(6, CognitiveRecoveryAction.REBUILD_STABILITY, "cognitive_stability", "stability must be rebuilt before strategy evolution"))
    if CognitiveRecoveryRisk.MEMORY_RESTORE_RISK in resolved_risks:
        steps.append(_step(7, CognitiveRecoveryAction.PROTECT_MEMORY, "critical_memory", "critical memory must be preserved during recovery"))
    if resolved_risks:
        steps.append(_step(8, CognitiveRecoveryAction.KEEP_AUTONOMY_REDUCED, "autonomy", "autonomy remains reduced during recovery"))
    if _human_review_required(data, resolved_risks):
        steps.append(_step(9, CognitiveRecoveryAction.REQUIRE_HUMAN_REVIEW, "supervision", "human review required for unsafe recovery path"))
    if not steps:
        steps.append(_step(10, CognitiveRecoveryAction.MARK_RECOVERY_COMPLETE, "recovery", "all recovery checks passed", False, True))

    ordered_steps = tuple(sorted(dict.fromkeys(steps), key=lambda item: item.order))
    return CognitiveRecoveryPlan(
        ordered_steps,
        resolved_checkpoints,
        bool(resolved_risks),
        bool(resolved_risks),
        bool(resolved_risks),
        _minimal_core_required(data, resolved_risks),
        not resolved_risks,
    )


def compute_cognitive_recovery_score(
    recovery_input: CognitiveRecoveryInput | None = None,
    *,
    risks: tuple[CognitiveRecoveryRisk, ...] | None = None,
    **kwargs,
) -> CognitiveRecoveryScore:
    """Compute deep cognitive recovery score components."""
    data = _input(recovery_input, **kwargs)
    resolved_risks = risks if risks is not None else detect_cognitive_recovery_risks(data)
    minimal_core = _clamp(_resilience_score(data) - 30 * _has(resolved_risks, CognitiveRecoveryRisk.RECOVERY_FAILURE))
    consensus = _clamp(_consensus_score(data) - 30 * _has(resolved_risks, CognitiveRecoveryRisk.CONSENSUS_REBUILD_FAILURE))
    governance = _clamp(_governance_score(data) - 30 * _has(resolved_risks, CognitiveRecoveryRisk.GOVERNANCE_RESTORE_FAILURE))
    policy = _clamp(_policy_score(data) - 30 * _has(resolved_risks, CognitiveRecoveryRisk.POLICY_REPAIR_FAILURE))
    world = _clamp(_world_score(data) - 30 * _has(resolved_risks, CognitiveRecoveryRisk.WORLD_MODEL_RESTORE_FAILURE))
    stability = _clamp(_stability_score(data) - 30 * _has(resolved_risks, CognitiveRecoveryRisk.STABILITY_REBUILD_FAILURE))
    memory = _clamp(_memory_score(data) - 30 * _has(resolved_risks, CognitiveRecoveryRisk.MEMORY_RESTORE_RISK))
    orchestration = _clamp(_orchestration_score(data) - 25 * _has(resolved_risks, CognitiveRecoveryRisk.UNSAFE_RECOVERY_PATH))
    return CognitiveRecoveryScore(minimal_core, consensus, governance, policy, world, stability, memory, orchestration)


def build_recovery_checkpoints(
    recovery_input: CognitiveRecoveryInput | None = None,
    **kwargs,
) -> tuple[CognitiveRecoveryCheckpoint, ...]:
    """Build ordered checkpoints preserving recovery progress."""
    data = _input(recovery_input, **kwargs)
    checkpoints = [
        _checkpoint("minimal_core", _resilience_score(data), "resilience baseline"),
        _checkpoint("consensus", _consensus_score(data), "minimal consensus layer"),
        _checkpoint("governance", _governance_score(data), "governance restored before policy"),
        _checkpoint("policy", _policy_score(data), "policy repair before routing"),
        _checkpoint("world_model", _world_score(data), "world model before action"),
        _checkpoint("stability", _stability_score(data), "stability before strategy evolution"),
        _checkpoint("memory", _memory_score(data), "critical memory preserved"),
        _checkpoint("orchestration", _orchestration_score(data), "orchestration safe to coordinate"),
    ]
    return tuple(dict.fromkeys(tuple(data.previous_checkpoints) + tuple(checkpoints)))


def generate_cognitive_recovery_recommendations(
    recovery_input: CognitiveRecoveryInput | None = None,
    *,
    risks: tuple[CognitiveRecoveryRisk, ...] | None = None,
    state: CognitiveRecoveryState | None = None,
    **kwargs,
) -> tuple[CognitiveRecoveryRecommendation, ...]:
    """Generate deep cognitive recovery recommendations."""
    data = _input(recovery_input, **kwargs)
    resolved_risks = risks if risks is not None else detect_cognitive_recovery_risks(data)
    resolved_state = state or _recovery_state(data, _overall_score(compute_cognitive_recovery_score(data, risks=resolved_risks)), resolved_risks, build_cognitive_recovery_plan(data, risks=resolved_risks))
    recommendations: list[CognitiveRecoveryRecommendation] = []

    if resolved_risks:
        recommendations.append(CognitiveRecoveryRecommendation.CONTINUE_RECOVERY)
        recommendations.append(CognitiveRecoveryRecommendation.EXTEND_RECOVERY_WINDOW)
    if CognitiveRecoveryRisk.CONSENSUS_REBUILD_FAILURE in resolved_risks:
        recommendations.append(CognitiveRecoveryRecommendation.RESTORE_MINIMAL_CONSENSUS_FIRST)
    if CognitiveRecoveryRisk.GOVERNANCE_RESTORE_FAILURE in resolved_risks or CognitiveRecoveryRisk.POLICY_REPAIR_FAILURE in resolved_risks:
        recommendations.append(CognitiveRecoveryRecommendation.REPAIR_GOVERNANCE_BEFORE_POLICY)
    if CognitiveRecoveryRisk.WORLD_MODEL_RESTORE_FAILURE in resolved_risks:
        recommendations.append(CognitiveRecoveryRecommendation.VALIDATE_WORLD_MODEL_BEFORE_ACTION)
    if resolved_risks:
        recommendations.append(CognitiveRecoveryRecommendation.KEEP_LEARNING_FROZEN)
        recommendations.append(CognitiveRecoveryRecommendation.KEEP_EXECUTION_DISABLED)
        recommendations.append(CognitiveRecoveryRecommendation.RECHECK_STABILITY)
        recommendations.append(CognitiveRecoveryRecommendation.PRESERVE_RECOVERY_CHECKPOINT)
    if resolved_state in {CognitiveRecoveryState.HUMAN_REVIEW_REQUIRED, CognitiveRecoveryState.FAILED_RECOVERY} or _human_review_required(data, resolved_risks):
        recommendations.append(CognitiveRecoveryRecommendation.ESCALATE_TO_HUMAN_REVIEW)
    if not recommendations:
        recommendations.append(CognitiveRecoveryRecommendation.PRESERVE_RECOVERY_CHECKPOINT)
    return tuple(dict.fromkeys(recommendations))


def render_cognitive_recovery_markdown(result: CognitiveRecoveryResult) -> str:
    """Render cognitive recovery result as Markdown."""
    lines = [
        "# Autonomous Cognitive Recovery Engine",
        "",
        "## Cognitive Recovery State",
        "",
        f"- State: {result.state.value}",
        "",
        "## Recovery Score",
        "",
        f"- Overall: {result.recovery_score}/100",
        f"- Consensus: {result.score_breakdown.consensus_recovery_score}/100",
        f"- World Model: {result.score_breakdown.world_model_recovery_score}/100",
        "",
        "## Recovery Mode",
        "",
        f"- {result.mode.value}",
        "",
        "## Recovery Risks",
        "",
        *_bullet_lines(tuple(risk.value for risk in result.risks)),
        "",
        "## Recovery Plan",
        "",
        *_bullet_lines(tuple(f"{step.order}. {step.action.value} -> {step.target_layer}" for step in result.recovery_plan.steps)),
        "",
        "## Checkpoints",
        "",
        *_bullet_lines(tuple(f"{checkpoint.layer}: {checkpoint.score}/100 stable={checkpoint.stable}" for checkpoint in result.checkpoints)),
        "",
        "## Actions",
        "",
        *_bullet_lines(tuple(action.value for action in result.actions)),
        "",
        "## Recommendations",
        "",
        *_bullet_lines(tuple(recommendation.value for recommendation in result.recommendations)),
        "",
        "## AGIcore Recovery Outlook",
        "",
        result.summary,
    ]
    return "\n".join(lines)


def _input(recovery_input: CognitiveRecoveryInput | None = None, **kwargs) -> CognitiveRecoveryInput:
    if recovery_input is not None and kwargs:
        raise ValueError("Pass either CognitiveRecoveryInput or keyword inputs, not both")
    if recovery_input is not None:
        return recovery_input
    return CognitiveRecoveryInput(**kwargs)


def _recovery_loop(data: CognitiveRecoveryInput) -> bool:
    return len(data.previous_checkpoints) >= 4 and _avg([checkpoint.score for checkpoint in data.previous_checkpoints[-4:]], 70) < 55


def _recovery_failure(data: CognitiveRecoveryInput) -> bool:
    return (
        _value(_get(data.cognitive_resilience, "state")) in {CognitiveResilienceState.COGNITIVE_SURVIVAL, CognitiveResilienceState.CRITICAL}
        and _resilience_score(data) < 40
    ) or _value(_get(data.system_integrity, "status")) in {SystemIntegrityStatus.COMPROMISED, SystemIntegrityStatus.ROLLBACK_RECOMMENDED}


def _consensus_rebuild_failure(data: CognitiveRecoveryInput) -> bool:
    return _consensus_needs_rebuild(data)


def _governance_restore_failure(data: CognitiveRecoveryInput) -> bool:
    return _governance_needs_restore(data)


def _policy_repair_failure(data: CognitiveRecoveryInput) -> bool:
    return _policy_needs_repair(data)


def _world_model_restore_failure(data: CognitiveRecoveryInput) -> bool:
    return _world_model_needs_restore(data)


def _stability_rebuild_failure(data: CognitiveRecoveryInput) -> bool:
    return _stability_needs_rebuild(data)


def _memory_restore_risk(data: CognitiveRecoveryInput) -> bool:
    risks = set(_get(data.mission_continuity, "risks", ()) or ())
    actions = set(_get(data.mission_continuity, "actions", ()) or ())
    return (
        ContinuityRisk.MEMORY_RISK in risks
        or ContinuityRisk.STRATEGIC_MEMORY_LOSS in risks
        or ContinuityAction.PRESERVE_MEMORY in actions
        or _value(_get(data.mission_continuity, "mode")) in {MissionContinuityMode.ESSENTIAL_ONLY, MissionContinuityMode.SURVIVAL_CONTINUITY}
    )


def _unsafe_recovery_path(data: CognitiveRecoveryInput) -> bool:
    return (
        _value(_get(data.strategic_arbitration, "decision")) in {ArbitrationDecision.EMERGENCY_LOCKDOWN, ArbitrationDecision.STOP_EXECUTION}
        or _value(_get(data.strategic_arbitration, "mode")) == ArbitrationMode.EMERGENCY_LOCKDOWN
        or _value(_get(data.global_orchestrator, "decision")) in {OrchestratorDecision.EMERGENCY_HALT_ROUTING, OrchestratorDecision.ACTIVATE_SURVIVAL_MODE}
        or _value(_get(data.global_orchestrator, "system_state", object()), "mode") in {OrchestratorMode.EMERGENCY_ORCHESTRATION, OrchestratorMode.SURVIVAL_ORCHESTRATION}
    )


def _premature_reactivation(data: CognitiveRecoveryInput) -> bool:
    return (
        _value(_get(data.cognitive_governance, "autonomy_level")) == CognitiveAutonomyLevel.FULL_AUTONOMY
        and (
            _stability_needs_rebuild(data)
            or _world_model_needs_restore(data)
            or _policy_needs_repair(data)
            or _consensus_needs_rebuild(data)
        )
    )


def _consensus_needs_rebuild(data: CognitiveRecoveryInput) -> bool:
    return (
        _consensus_score(data) < 60
        or _value(_get(data.collective_consensus, "mode")) in {ConsensusMode.CONSENSUS_COLLAPSE, ConsensusMode.DEGRADED_CONSENSUS, ConsensusMode.EMERGENCY_CONSENSUS}
        or _value(_get(data.collective_consensus, "decision")) in {ConsensusDecision.NO_CONSENSUS, ConsensusDecision.BLOCK_COLLECTIVE_ACTION, ConsensusDecision.EMERGENCY_HALT}
    )


def _governance_needs_restore(data: CognitiveRecoveryInput) -> bool:
    return (
        _governance_score(data) < 60
        or _value(_get(data.cognitive_governance, "mode")) in {CognitiveGovernanceMode.LOCKED_GOVERNANCE, CognitiveGovernanceMode.EMERGENCY_GOVERNANCE, CognitiveGovernanceMode.SAFE_GOVERNANCE}
        or _value(_get(data.cognitive_governance, "decision")) in {CognitiveGovernanceDecision.ENTER_LOCKED_GOVERNANCE, CognitiveGovernanceDecision.REQUIRE_HUMAN_REVIEW}
    )


def _policy_needs_repair(data: CognitiveRecoveryInput) -> bool:
    policy_risks = set(_get(data.cognitive_policy, "risks", ()) or ())
    return (
        _policy_score(data) < 60
        or _value(_get(data.cognitive_policy, "mode")) in {CognitivePolicyMode.POLICY_LOCKED, CognitivePolicyMode.POLICY_SAFE_MODE, CognitivePolicyMode.POLICY_RESTRICTED}
        or bool({CognitivePolicyRisk.POLICY_CONFLICT, CognitivePolicyRisk.SAFETY_CRITICAL_BYPASS, CognitivePolicyRisk.GOVERNANCE_POLICY_MISMATCH}.intersection(policy_risks))
    )


def _world_model_needs_restore(data: CognitiveRecoveryInput) -> bool:
    world_risks = set(_get(data.recursive_world_model, "risks", ()) or ())
    return (
        _world_score(data) < 60
        or _value(_get(data.recursive_world_model, "decision")) in {WorldModelDecision.REBUILD_CAUSAL_GRAPH, WorldModelDecision.ENTER_WORLD_MODEL_SAFE_MODE, WorldModelDecision.FREEZE_RECURSIVE_UPDATES}
        or bool({WorldModelRisk.WORLD_MODEL_INCOHERENCE, WorldModelRisk.SAFETY_MODEL_FAILURE, WorldModelRisk.RECURSIVE_FEEDBACK_LOOP}.intersection(world_risks))
    )


def _stability_needs_rebuild(data: CognitiveRecoveryInput) -> bool:
    stability_risks = set(_get(data.cognitive_stability, "risks", ()) or ())
    return (
        _stability_score(data) < 60
        or _value(_get(data.cognitive_stability, "state")) in {CognitiveStabilityState.CRITICAL, CognitiveStabilityState.COLLAPSING, CognitiveStabilityState.UNSTABLE}
        or _value(_get(data.cognitive_stability, "mode")) in {CognitiveStabilityMode.EMERGENCY_STABILIZATION, CognitiveStabilityMode.LOCKED_STABILITY}
        or CognitiveStabilityRisk.SYSTEM_COLLAPSE_RISK in stability_risks
    )


def _minimal_core_required(data: CognitiveRecoveryInput, risks: tuple[CognitiveRecoveryRisk, ...]) -> bool:
    return (
        CognitiveRecoveryRisk.RECOVERY_FAILURE in risks
        or _value(_get(data.cognitive_resilience, "state")) in {CognitiveResilienceState.COGNITIVE_SURVIVAL, CognitiveResilienceState.CRITICAL}
    )


def _human_review_required(data: CognitiveRecoveryInput, risks: tuple[CognitiveRecoveryRisk, ...]) -> bool:
    return (
        CognitiveRecoveryRisk.UNSAFE_RECOVERY_PATH in risks
        or CognitiveRecoveryRisk.PREMATURE_REACTIVATION in risks
        or CognitiveRecoveryRisk.RECOVERY_FAILURE in risks
        or len(risks) >= 6
    )


def _recovery_state(
    data: CognitiveRecoveryInput,
    score: int,
    risks: tuple[CognitiveRecoveryRisk, ...],
    plan: CognitiveRecoveryPlan,
) -> CognitiveRecoveryState:
    if _human_review_required(data, risks):
        return CognitiveRecoveryState.HUMAN_REVIEW_REQUIRED
    if CognitiveRecoveryRisk.RECOVERY_FAILURE in risks or score < 30:
        return CognitiveRecoveryState.FAILED_RECOVERY
    if CognitiveRecoveryRisk.UNSAFE_RECOVERY_PATH in risks:
        return CognitiveRecoveryState.SAFE_RECOVERY
    if not risks and score >= 75:
        return CognitiveRecoveryState.RECOVERED
    if plan.minimal_core_required:
        return CognitiveRecoveryState.RECOVERING
    if len(risks) >= 4 or score < 50:
        return CognitiveRecoveryState.DEGRADED_RECOVERY
    if risks:
        return CognitiveRecoveryState.PARTIAL_RECOVERY
    return CognitiveRecoveryState.RECOVERING


def _recovery_mode(
    data: CognitiveRecoveryInput,
    state: CognitiveRecoveryState,
    risks: tuple[CognitiveRecoveryRisk, ...],
) -> CognitiveRecoveryMode:
    if state == CognitiveRecoveryState.HUMAN_REVIEW_REQUIRED:
        return CognitiveRecoveryMode.LOCKED_RECOVERY
    if CognitiveRecoveryRisk.UNSAFE_RECOVERY_PATH in risks:
        return CognitiveRecoveryMode.SAFE_RECOVERY_MODE
    if CognitiveRecoveryRisk.RECOVERY_FAILURE in risks:
        return CognitiveRecoveryMode.MINIMAL_RECONSTRUCTION
    if CognitiveRecoveryRisk.CONSENSUS_REBUILD_FAILURE in risks:
        return CognitiveRecoveryMode.CONSENSUS_REBUILD
    if CognitiveRecoveryRisk.GOVERNANCE_RESTORE_FAILURE in risks:
        return CognitiveRecoveryMode.GOVERNANCE_RESTORE
    if CognitiveRecoveryRisk.POLICY_REPAIR_FAILURE in risks:
        return CognitiveRecoveryMode.POLICY_REPAIR
    if CognitiveRecoveryRisk.WORLD_MODEL_RESTORE_FAILURE in risks:
        return CognitiveRecoveryMode.WORLD_MODEL_RESTORE
    if CognitiveRecoveryRisk.STABILITY_REBUILD_FAILURE in risks:
        return CognitiveRecoveryMode.STABILITY_REBUILD
    return CognitiveRecoveryMode.NORMAL_RECOVERY


def _step(
    order: int,
    action: CognitiveRecoveryAction,
    target: str,
    reason: str,
    required: bool = True,
    completed: bool = False,
) -> CognitiveRecoveryStep:
    return CognitiveRecoveryStep(order, action, target, reason, required, completed)


def _checkpoint(layer: str, score: int, note: str) -> CognitiveRecoveryCheckpoint:
    return CognitiveRecoveryCheckpoint(f"checkpoint_{layer}", layer, _clamp(score), score >= 65, (note,))


def _resilience_score(data: CognitiveRecoveryInput) -> int:
    return _clamp(_get(data.cognitive_resilience, "resilience_score", _get(data.recovery_resilience, "resilience_score", 70)))


def _consensus_score(data: CognitiveRecoveryInput) -> int:
    return _clamp(_get(data.collective_consensus, "collective_confidence_score", 70))


def _governance_score(data: CognitiveRecoveryInput) -> int:
    return _clamp(_get(data.cognitive_governance, "governance_score", 70))


def _policy_score(data: CognitiveRecoveryInput) -> int:
    return _clamp(_get(data.cognitive_policy, "cognitive_policy_score", 70))


def _world_score(data: CognitiveRecoveryInput) -> int:
    return _clamp(_get(data.recursive_world_model, "world_model_coherence_score", 70))


def _stability_score(data: CognitiveRecoveryInput) -> int:
    return _clamp(_get(data.cognitive_stability, "stability_score", 70))


def _memory_score(data: CognitiveRecoveryInput) -> int:
    return _clamp(_get(data.mission_continuity, "continuity_score", 70))


def _orchestration_score(data: CognitiveRecoveryInput) -> int:
    return _clamp(_get(data.global_orchestrator, "confidence_score", 70))


def _overall_score(score: CognitiveRecoveryScore) -> int:
    return _avg(
        [
            score.minimal_core_score,
            score.consensus_recovery_score,
            score.governance_recovery_score,
            score.policy_recovery_score,
            score.world_model_recovery_score,
            score.stability_recovery_score,
            score.memory_recovery_score,
            score.orchestration_recovery_score,
        ],
        50,
    )


def _has(risks: tuple[CognitiveRecoveryRisk, ...], risk: CognitiveRecoveryRisk) -> int:
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
    "build_recovery_checkpoints",
    "compute_cognitive_recovery_score",
    "detect_cognitive_recovery_risks",
    "evaluate_cognitive_recovery",
    "generate_cognitive_recovery_recommendations",
    "render_cognitive_recovery_markdown",
]
