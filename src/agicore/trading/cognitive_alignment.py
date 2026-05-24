"""Offline Autonomous Cognitive Alignment Engine for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime
from statistics import mean
from typing import Any

from .cognitive_alignment_models import (
    AlignmentAxis,
    AlignmentMatrix,
    CognitiveAlignmentAction,
    CognitiveAlignmentEvent,
    CognitiveAlignmentInput,
    CognitiveAlignmentMode,
    CognitiveAlignmentRecommendation,
    CognitiveAlignmentResult,
    CognitiveAlignmentRisk,
    CognitiveAlignmentScore,
    CognitiveAlignmentState,
)
from .cognitive_governance_models import CognitiveAutonomyLevel, CognitiveGovernanceDecision, CognitiveGovernanceMode
from .cognitive_identity_models import CognitiveIdentityRisk, CognitiveIdentityState
from .cognitive_policy_models import CognitivePolicyMode, CognitivePolicyRisk
from .cognitive_stability_models import CognitiveStabilityState
from .collective_consensus_models import ConsensusDecision, ConsensusMode, ConsensusRisk
from .global_orchestrator_models import OrchestratorDecision, OrchestratorMode
from .intent_alignment_models import IntentAlignmentMode, IntentRisk
from .intent_integrity_models import IntentIntegrityRisk, IntentIntegrityState
from .mission_continuity_models import ContinuityRisk, MissionContinuityMode
from .recursive_world_model_models import WorldModelDecision, WorldModelRisk
from .self_reflection_audit_models import CognitiveAuditRisk, ReflectionState
from .system_integrity_models import SystemIntegrityStatus


def _value(item: Any) -> str:
    return getattr(item, "value", str(item))


def _get(obj: Any, attr: str, default: Any = None) -> Any:
    return getattr(obj, attr, default) if obj is not None else default


def _has(items: Any, expected: Any) -> bool:
    expected_value = _value(expected)
    return any(_value(item) == expected_value for item in (items or ()))


def _clamp(value: int | float, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(round(value))))


def _average(values: tuple[int, ...]) -> int:
    return _clamp(mean(values)) if values else 75


def _dedupe(items: tuple[Any, ...]) -> tuple[Any, ...]:
    seen: set[str] = set()
    output: list[Any] = []
    for item in items:
        key = _value(item)
        if key not in seen:
            seen.add(key)
            output.append(item)
    return tuple(output)


def detect_cognitive_alignment_risks(
    intent_integrity: Any = None,
    cognitive_identity: Any = None,
    cognitive_continuity: Any = None,
    cognitive_recovery: Any = None,
    cognitive_resilience: Any = None,
    cognitive_stability: Any = None,
    cognitive_policy: Any = None,
    cognitive_governance: Any = None,
    self_reflection_audit: Any = None,
    recursive_world_model: Any = None,
    global_orchestrator: Any = None,
    collective_consensus: Any = None,
    intent_alignment: Any = None,
    mission_continuity: Any = None,
    system_integrity: Any = None,
) -> tuple[CognitiveAlignmentRisk, ...]:
    """Detect global cognitive alignment risks using local heuristics."""

    risks: list[CognitiveAlignmentRisk] = []

    if (
        _get(mission_continuity, "mode") in (MissionContinuityMode.SURVIVAL_CONTINUITY, MissionContinuityMode.SAFE_PAUSE)
        or _get(mission_continuity, "continuity_score", 80) < 55
        or _has(_get(mission_continuity, "risks", ()), ContinuityRisk.EXECUTIVE_COLLAPSE)
        or _get(intent_alignment, "mode") in (IntentAlignmentMode.MISALIGNED, IntentAlignmentMode.CRITICAL_REALIGNMENT)
        or _has(_get(intent_alignment, "risks", ()), IntentRisk.MISSION_DIVERGENCE)
    ):
        risks.append(CognitiveAlignmentRisk.MISSION_ALIGNMENT_BREAK)

    if (
        _get(cognitive_identity, "state")
        in (
            CognitiveIdentityState.IDENTITY_DRIFT,
            CognitiveIdentityState.IDENTITY_FRAGMENTED,
            CognitiveIdentityState.IDENTITY_CONFLICTED,
            CognitiveIdentityState.IDENTITY_AT_RISK,
            CognitiveIdentityState.IDENTITY_LOCKED,
        )
        or _get(cognitive_identity, "identity_score", 80) < 60
        or _has(_get(cognitive_identity, "risks", ()), CognitiveIdentityRisk.IDENTITY_COLLAPSE_RISK)
    ):
        risks.append(CognitiveAlignmentRisk.IDENTITY_ALIGNMENT_BREAK)

    if (
        _get(intent_integrity, "state")
        in (
            IntentIntegrityState.INTENT_DRIFT,
            IntentIntegrityState.INTENT_CONFLICT,
            IntentIntegrityState.INTENT_CORRUPTED,
            IntentIntegrityState.INTENT_AT_RISK,
            IntentIntegrityState.INTENT_LOCKED,
        )
        or _get(intent_integrity, "intent_integrity_score", 80) < 60
        or _has(_get(intent_integrity, "risks", ()), IntentIntegrityRisk.INTENT_COLLAPSE_RISK)
    ):
        risks.append(CognitiveAlignmentRisk.INTENT_ALIGNMENT_BREAK)

    if (
        _get(cognitive_policy, "mode")
        in (CognitivePolicyMode.POLICY_RESTRICTED, CognitivePolicyMode.POLICY_SAFE_MODE, CognitivePolicyMode.POLICY_LOCKED)
        or _get(cognitive_policy, "cognitive_policy_score", 80) < 55
        or _has(_get(cognitive_policy, "risks", ()), CognitivePolicyRisk.POLICY_CONFLICT)
        or _has(_get(cognitive_policy, "risks", ()), CognitivePolicyRisk.SAFETY_CRITICAL_BYPASS)
    ):
        risks.append(CognitiveAlignmentRisk.POLICY_ALIGNMENT_BREAK)

    if (
        _get(cognitive_governance, "mode")
        in (
            CognitiveGovernanceMode.RESTRICTED_GOVERNANCE,
            CognitiveGovernanceMode.SAFE_GOVERNANCE,
            CognitiveGovernanceMode.DEGRADED_GOVERNANCE,
            CognitiveGovernanceMode.EMERGENCY_GOVERNANCE,
            CognitiveGovernanceMode.LOCKED_GOVERNANCE,
        )
        or _get(cognitive_governance, "governance_score", 80) < 55
        or _get(cognitive_governance, "decision")
        in (
            CognitiveGovernanceDecision.ENFORCE_SAFE_GOVERNANCE,
            CognitiveGovernanceDecision.REQUIRE_HUMAN_REVIEW,
            CognitiveGovernanceDecision.ENTER_LOCKED_GOVERNANCE,
        )
    ):
        risks.append(CognitiveAlignmentRisk.GOVERNANCE_ALIGNMENT_BREAK)

    if (
        _get(recursive_world_model, "world_model_coherence_score", 80) < 60
        or _get(recursive_world_model, "decision")
        in (
            WorldModelDecision.REBUILD_CAUSAL_GRAPH,
            WorldModelDecision.ENTER_WORLD_MODEL_SAFE_MODE,
            WorldModelDecision.FREEZE_RECURSIVE_UPDATES,
        )
        or _has(_get(recursive_world_model, "risks", ()), WorldModelRisk.WORLD_MODEL_INCOHERENCE)
        or _has(_get(recursive_world_model, "risks", ()), WorldModelRisk.GOVERNANCE_MISALIGNMENT)
    ):
        risks.append(CognitiveAlignmentRisk.WORLD_MODEL_ALIGNMENT_BREAK)

    if (
        _get(collective_consensus, "mode") in (ConsensusMode.DEGRADED_CONSENSUS, ConsensusMode.CONSENSUS_COLLAPSE)
        or _get(collective_consensus, "collective_confidence_score", 80) < 60
        or _get(collective_consensus, "decision")
        in (ConsensusDecision.BLOCK_COLLECTIVE_ACTION, ConsensusDecision.EMERGENCY_HALT, ConsensusDecision.NO_CONSENSUS)
        or _has(_get(collective_consensus, "risks", ()), ConsensusRisk.CONSENSUS_FRAGMENTATION)
    ):
        risks.append(CognitiveAlignmentRisk.CONSENSUS_ALIGNMENT_BREAK)

    if (
        _get(self_reflection_audit, "state")
        in (ReflectionState.DEGRADED_REFLECTION, ReflectionState.CONTRADICTORY_REFLECTION, ReflectionState.AUDIT_REQUIRED)
        or _has(_get(self_reflection_audit, "risks", ()), CognitiveAuditRisk.UNEXPLAINED_DECISION)
        or _has(_get(self_reflection_audit, "risks", ()), CognitiveAuditRisk.STRATEGIC_SELF_CONTRADICTION)
        or _get(global_orchestrator, "mode") in (OrchestratorMode.DEGRADED_OPERATION, OrchestratorMode.EMERGENCY_ORCHESTRATION)
        or _get(global_orchestrator, "decision")
        in (OrchestratorDecision.ENTER_SAFE_GLOBAL_MODE, OrchestratorDecision.EMERGENCY_HALT_ROUTING)
    ):
        risks.append(CognitiveAlignmentRisk.DECISION_ACTION_MISALIGNMENT)

    if (
        _get(cognitive_governance, "autonomy_level") == CognitiveAutonomyLevel.FULL_AUTONOMY
        and risks
        or _get(intent_alignment, "mode") == IntentAlignmentMode.AUTONOMY_DRIFT
        or _has(_get(intent_alignment, "risks", ()), IntentRisk.AUTONOMY_EXPANSION)
    ):
        risks.append(CognitiveAlignmentRisk.AUTONOMY_ALIGNMENT_RISK)

    if (
        len(risks) >= 6
        or _get(system_integrity, "status") in (SystemIntegrityStatus.COMPROMISED, SystemIntegrityStatus.ROLLBACK_RECOMMENDED)
        or _get(cognitive_stability, "state") in (CognitiveStabilityState.CRITICAL, CognitiveStabilityState.COLLAPSING)
        or _has(_get(intent_integrity, "risks", ()), IntentIntegrityRisk.INTENT_COLLAPSE_RISK)
        or _has(_get(cognitive_identity, "risks", ()), CognitiveIdentityRisk.IDENTITY_COLLAPSE_RISK)
    ):
        risks.append(CognitiveAlignmentRisk.SYSTEMIC_ALIGNMENT_COLLAPSE)

    return _dedupe(tuple(risks))


def compute_cognitive_alignment_score(
    intent_integrity: Any = None,
    cognitive_identity: Any = None,
    cognitive_continuity: Any = None,
    cognitive_policy: Any = None,
    cognitive_governance: Any = None,
    self_reflection_audit: Any = None,
    recursive_world_model: Any = None,
    collective_consensus: Any = None,
    intent_alignment: Any = None,
    mission_continuity: Any = None,
    risks: tuple[CognitiveAlignmentRisk, ...] = (),
) -> CognitiveAlignmentScore:
    """Compute global alignment component scores."""

    values = {
        "mission": _average((_get(mission_continuity, "continuity_score", 80), _get(intent_alignment, "alignment_confidence", 80))),
        "identity": _clamp(_get(cognitive_identity, "identity_score", 80)),
        "intent": _clamp(_get(intent_integrity, "intent_integrity_score", 80)),
        "policy": _clamp(_get(cognitive_policy, "cognitive_policy_score", 80)),
        "governance": _clamp(_get(cognitive_governance, "governance_score", 80)),
        "world": _clamp(_get(recursive_world_model, "world_model_coherence_score", 80)),
        "consensus": _clamp(_get(collective_consensus, "collective_confidence_score", 80)),
        "decision": _clamp(_get(self_reflection_audit, "reflection_quality_score", 80)),
        "autonomy": 80,
        "systemic": _average(
            (
                _get(cognitive_continuity, "continuity_score", 80),
                _get(cognitive_identity, "identity_score", 80),
                _get(intent_integrity, "intent_integrity_score", 80),
                _get(cognitive_governance, "governance_score", 80),
            )
        ),
    }
    if _get(cognitive_governance, "autonomy_level") in (
        CognitiveAutonomyLevel.SUPERVISED_AUTONOMY,
        CognitiveAutonomyLevel.OBSERVE_ONLY,
        CognitiveAutonomyLevel.LOCKED_AUTONOMY,
        CognitiveAutonomyLevel.HUMAN_REVIEW_REQUIRED,
    ):
        values["autonomy"] = 65

    penalties = {
        CognitiveAlignmentRisk.MISSION_ALIGNMENT_BREAK: ("mission", 25),
        CognitiveAlignmentRisk.IDENTITY_ALIGNMENT_BREAK: ("identity", 25),
        CognitiveAlignmentRisk.INTENT_ALIGNMENT_BREAK: ("intent", 25),
        CognitiveAlignmentRisk.POLICY_ALIGNMENT_BREAK: ("policy", 25),
        CognitiveAlignmentRisk.GOVERNANCE_ALIGNMENT_BREAK: ("governance", 25),
        CognitiveAlignmentRisk.WORLD_MODEL_ALIGNMENT_BREAK: ("world", 25),
        CognitiveAlignmentRisk.CONSENSUS_ALIGNMENT_BREAK: ("consensus", 25),
        CognitiveAlignmentRisk.DECISION_ACTION_MISALIGNMENT: ("decision", 25),
        CognitiveAlignmentRisk.AUTONOMY_ALIGNMENT_RISK: ("autonomy", 30),
        CognitiveAlignmentRisk.SYSTEMIC_ALIGNMENT_COLLAPSE: ("all", 20),
    }
    for risk in risks:
        target, penalty = penalties[risk]
        if target == "all":
            values = {key: value - penalty for key, value in values.items()}
        else:
            values[target] -= penalty

    return CognitiveAlignmentScore(
        mission_alignment_score=_clamp(values["mission"]),
        identity_alignment_score=_clamp(values["identity"]),
        intent_alignment_score=_clamp(values["intent"]),
        policy_alignment_score=_clamp(values["policy"]),
        governance_alignment_score=_clamp(values["governance"]),
        world_model_alignment_score=_clamp(values["world"]),
        consensus_alignment_score=_clamp(values["consensus"]),
        decision_action_alignment_score=_clamp(values["decision"]),
        autonomy_alignment_score=_clamp(values["autonomy"]),
        systemic_alignment_score=_clamp(values["systemic"]),
    )


def build_alignment_axes(
    score_breakdown: CognitiveAlignmentScore,
    risks: tuple[CognitiveAlignmentRisk, ...] = (),
) -> tuple[AlignmentAxis, ...]:
    """Build explainable alignment axes from score components and risks."""

    specs = (
        ("mission", score_breakdown.mission_alignment_score, CognitiveAlignmentRisk.MISSION_ALIGNMENT_BREAK),
        ("identity", score_breakdown.identity_alignment_score, CognitiveAlignmentRisk.IDENTITY_ALIGNMENT_BREAK),
        ("intent", score_breakdown.intent_alignment_score, CognitiveAlignmentRisk.INTENT_ALIGNMENT_BREAK),
        ("policy", score_breakdown.policy_alignment_score, CognitiveAlignmentRisk.POLICY_ALIGNMENT_BREAK),
        ("governance", score_breakdown.governance_alignment_score, CognitiveAlignmentRisk.GOVERNANCE_ALIGNMENT_BREAK),
        ("world_model", score_breakdown.world_model_alignment_score, CognitiveAlignmentRisk.WORLD_MODEL_ALIGNMENT_BREAK),
        ("consensus", score_breakdown.consensus_alignment_score, CognitiveAlignmentRisk.CONSENSUS_ALIGNMENT_BREAK),
        ("decision_action", score_breakdown.decision_action_alignment_score, CognitiveAlignmentRisk.DECISION_ACTION_MISALIGNMENT),
        ("autonomy", score_breakdown.autonomy_alignment_score, CognitiveAlignmentRisk.AUTONOMY_ALIGNMENT_RISK),
        ("systemic", score_breakdown.systemic_alignment_score, CognitiveAlignmentRisk.SYSTEMIC_ALIGNMENT_COLLAPSE),
    )
    axes: list[AlignmentAxis] = []
    for name, score, risk in specs:
        aligned = score >= 60 and risk not in risks
        axes.append(
            AlignmentAxis(
                name=name,
                score=score,
                aligned=aligned,
                risk=risk if not aligned else None,
                evidence="aligned" if aligned else f"{risk.value} requires repair",
            )
        )
    return tuple(axes)


def build_alignment_matrix(
    axes: tuple[AlignmentAxis, ...],
    risks: tuple[CognitiveAlignmentRisk, ...] = (),
) -> AlignmentMatrix:
    """Build an alignment matrix across all cognitive axes."""

    broken_axes = tuple(axis.name for axis in axes if not axis.aligned)
    weakest = min(axes, key=lambda axis: axis.score).name if axes else None
    return AlignmentMatrix(
        axes=axes,
        global_score=_average(tuple(axis.score for axis in axes)),
        weakest_axis=weakest,
        broken_axes=broken_axes,
        autonomy_reduced=bool(risks),
        locked=CognitiveAlignmentRisk.SYSTEMIC_ALIGNMENT_COLLAPSE in risks,
    )


def generate_cognitive_alignment_recommendations(
    risks: tuple[CognitiveAlignmentRisk, ...] = (),
    state: CognitiveAlignmentState = CognitiveAlignmentState.FULLY_ALIGNED,
) -> tuple[CognitiveAlignmentRecommendation, ...]:
    """Generate ordered alignment recommendations."""

    recommendations: list[CognitiveAlignmentRecommendation] = []
    if CognitiveAlignmentRisk.MISSION_ALIGNMENT_BREAK in risks:
        recommendations.append(CognitiveAlignmentRecommendation.VERIFY_MISSION_ALIGNMENT)
    if CognitiveAlignmentRisk.IDENTITY_ALIGNMENT_BREAK in risks:
        recommendations.append(CognitiveAlignmentRecommendation.REPAIR_IDENTITY_ALIGNMENT)
    if CognitiveAlignmentRisk.INTENT_ALIGNMENT_BREAK in risks:
        recommendations.append(CognitiveAlignmentRecommendation.REPAIR_INTENT_ALIGNMENT)
    if CognitiveAlignmentRisk.POLICY_ALIGNMENT_BREAK in risks:
        recommendations.append(CognitiveAlignmentRecommendation.REPAIR_POLICY_ALIGNMENT)
    if CognitiveAlignmentRisk.GOVERNANCE_ALIGNMENT_BREAK in risks:
        recommendations.append(CognitiveAlignmentRecommendation.RECHECK_GOVERNANCE_ALIGNMENT)
    if CognitiveAlignmentRisk.CONSENSUS_ALIGNMENT_BREAK in risks:
        recommendations.append(CognitiveAlignmentRecommendation.REBUILD_CONSENSUS_CONTEXT)
    if CognitiveAlignmentRisk.AUTONOMY_ALIGNMENT_RISK in risks or risks:
        recommendations.append(CognitiveAlignmentRecommendation.KEEP_AUTONOMY_REDUCED)
    if state in (
        CognitiveAlignmentState.SYSTEMIC_MISALIGNMENT,
        CognitiveAlignmentState.ALIGNMENT_LOCKED,
        CognitiveAlignmentState.POLICY_MISALIGNMENT,
        CognitiveAlignmentState.INTENT_MISALIGNMENT,
    ):
        recommendations.append(CognitiveAlignmentRecommendation.REQUIRE_SUPERVISION)
    recommendations.append(CognitiveAlignmentRecommendation.UPDATE_ALIGNMENT_SNAPSHOT)
    if not risks:
        recommendations.append(CognitiveAlignmentRecommendation.CONTINUE_ALIGNMENT_MONITORING)
    return _dedupe(tuple(recommendations))


def _select_state(risks: tuple[CognitiveAlignmentRisk, ...]) -> CognitiveAlignmentState:
    if CognitiveAlignmentRisk.SYSTEMIC_ALIGNMENT_COLLAPSE in risks:
        return CognitiveAlignmentState.ALIGNMENT_LOCKED
    if len(risks) >= 5:
        return CognitiveAlignmentState.SYSTEMIC_MISALIGNMENT
    if CognitiveAlignmentRisk.INTENT_ALIGNMENT_BREAK in risks:
        return CognitiveAlignmentState.INTENT_MISALIGNMENT
    if CognitiveAlignmentRisk.POLICY_ALIGNMENT_BREAK in risks or CognitiveAlignmentRisk.GOVERNANCE_ALIGNMENT_BREAK in risks:
        return CognitiveAlignmentState.POLICY_MISALIGNMENT
    if CognitiveAlignmentRisk.IDENTITY_ALIGNMENT_BREAK in risks or CognitiveAlignmentRisk.MISSION_ALIGNMENT_BREAK in risks:
        return CognitiveAlignmentState.STRATEGIC_MISALIGNMENT
    if risks:
        return CognitiveAlignmentState.PARTIAL_MISALIGNMENT
    return CognitiveAlignmentState.FULLY_ALIGNED


def _select_mode(state: CognitiveAlignmentState, risks: tuple[CognitiveAlignmentRisk, ...]) -> CognitiveAlignmentMode:
    if state == CognitiveAlignmentState.ALIGNMENT_LOCKED:
        return CognitiveAlignmentMode.LOCKED_ALIGNMENT_MODE
    if state == CognitiveAlignmentState.SYSTEMIC_MISALIGNMENT:
        return CognitiveAlignmentMode.SAFE_ALIGNMENT_MODE
    if CognitiveAlignmentRisk.MISSION_ALIGNMENT_BREAK in risks:
        return CognitiveAlignmentMode.MISSION_ALIGNMENT
    if CognitiveAlignmentRisk.IDENTITY_ALIGNMENT_BREAK in risks:
        return CognitiveAlignmentMode.IDENTITY_ALIGNMENT
    if CognitiveAlignmentRisk.INTENT_ALIGNMENT_BREAK in risks:
        return CognitiveAlignmentMode.INTENT_ALIGNMENT_REPAIR
    if CognitiveAlignmentRisk.POLICY_ALIGNMENT_BREAK in risks or CognitiveAlignmentRisk.GOVERNANCE_ALIGNMENT_BREAK in risks:
        return CognitiveAlignmentMode.POLICY_ALIGNMENT_REPAIR
    if risks:
        return CognitiveAlignmentMode.ALIGNMENT_MONITORING
    return CognitiveAlignmentMode.NORMAL_ALIGNMENT


def _build_actions(risks: tuple[CognitiveAlignmentRisk, ...]) -> tuple[CognitiveAlignmentAction, ...]:
    actions: list[CognitiveAlignmentAction] = [CognitiveAlignmentAction.PRESERVE_ALIGNMENT_STATE]
    if CognitiveAlignmentRisk.MISSION_ALIGNMENT_BREAK in risks:
        actions.append(CognitiveAlignmentAction.REALIGN_MISSION)
    if CognitiveAlignmentRisk.IDENTITY_ALIGNMENT_BREAK in risks:
        actions.append(CognitiveAlignmentAction.REALIGN_IDENTITY)
    if CognitiveAlignmentRisk.INTENT_ALIGNMENT_BREAK in risks:
        actions.append(CognitiveAlignmentAction.REALIGN_INTENT)
    if CognitiveAlignmentRisk.POLICY_ALIGNMENT_BREAK in risks:
        actions.append(CognitiveAlignmentAction.REALIGN_POLICY)
    if CognitiveAlignmentRisk.GOVERNANCE_ALIGNMENT_BREAK in risks:
        actions.append(CognitiveAlignmentAction.REALIGN_GOVERNANCE)
    if CognitiveAlignmentRisk.WORLD_MODEL_ALIGNMENT_BREAK in risks:
        actions.append(CognitiveAlignmentAction.REALIGN_WORLD_MODEL)
    if CognitiveAlignmentRisk.CONSENSUS_ALIGNMENT_BREAK in risks:
        actions.append(CognitiveAlignmentAction.REBUILD_CONSENSUS_ALIGNMENT)
    if risks:
        actions.append(CognitiveAlignmentAction.REDUCE_AUTONOMY)
    if CognitiveAlignmentRisk.SYSTEMIC_ALIGNMENT_COLLAPSE in risks:
        actions.append(CognitiveAlignmentAction.LOCK_ALIGNMENT_STATE)
    return _dedupe(tuple(actions))


def evaluate_cognitive_alignment(
    intent_integrity: Any = None,
    cognitive_identity: Any = None,
    cognitive_continuity: Any = None,
    cognitive_recovery: Any = None,
    cognitive_resilience: Any = None,
    cognitive_stability: Any = None,
    cognitive_policy: Any = None,
    cognitive_governance: Any = None,
    self_reflection_audit: Any = None,
    recursive_world_model: Any = None,
    global_orchestrator: Any = None,
    collective_consensus: Any = None,
    intent_alignment: Any = None,
    mission_continuity: Any = None,
    system_integrity: Any = None,
    input_data: CognitiveAlignmentInput | None = None,
) -> CognitiveAlignmentResult:
    """Evaluate global cognitive alignment without external systems."""

    if input_data is not None:
        intent_integrity = input_data.intent_integrity
        cognitive_identity = input_data.cognitive_identity
        cognitive_continuity = input_data.cognitive_continuity
        cognitive_recovery = input_data.cognitive_recovery
        cognitive_resilience = input_data.cognitive_resilience
        cognitive_stability = input_data.cognitive_stability
        cognitive_policy = input_data.cognitive_policy
        cognitive_governance = input_data.cognitive_governance
        self_reflection_audit = input_data.self_reflection_audit
        recursive_world_model = input_data.recursive_world_model
        global_orchestrator = input_data.global_orchestrator
        collective_consensus = input_data.collective_consensus
        intent_alignment = input_data.intent_alignment
        mission_continuity = input_data.mission_continuity
        system_integrity = input_data.system_integrity

    risks = detect_cognitive_alignment_risks(
        intent_integrity=intent_integrity,
        cognitive_identity=cognitive_identity,
        cognitive_continuity=cognitive_continuity,
        cognitive_recovery=cognitive_recovery,
        cognitive_resilience=cognitive_resilience,
        cognitive_stability=cognitive_stability,
        cognitive_policy=cognitive_policy,
        cognitive_governance=cognitive_governance,
        self_reflection_audit=self_reflection_audit,
        recursive_world_model=recursive_world_model,
        global_orchestrator=global_orchestrator,
        collective_consensus=collective_consensus,
        intent_alignment=intent_alignment,
        mission_continuity=mission_continuity,
        system_integrity=system_integrity,
    )
    score_breakdown = compute_cognitive_alignment_score(
        intent_integrity=intent_integrity,
        cognitive_identity=cognitive_identity,
        cognitive_continuity=cognitive_continuity,
        cognitive_policy=cognitive_policy,
        cognitive_governance=cognitive_governance,
        self_reflection_audit=self_reflection_audit,
        recursive_world_model=recursive_world_model,
        collective_consensus=collective_consensus,
        intent_alignment=intent_alignment,
        mission_continuity=mission_continuity,
        risks=risks,
    )
    axes = build_alignment_axes(score_breakdown=score_breakdown, risks=risks)
    matrix = build_alignment_matrix(axes=axes, risks=risks)
    score = matrix.global_score
    state = _select_state(risks)
    mode = _select_mode(state, risks)
    actions = _build_actions(risks)
    recommendations = generate_cognitive_alignment_recommendations(risks=risks, state=state)
    summary = "Cognitive alignment fully preserved." if not risks else f"Cognitive alignment requires repair for {len(risks)} risk(s)."
    events = (
        CognitiveAlignmentEvent(
            state=state,
            mode=mode,
            message=summary,
            timestamp=datetime.now(UTC),
        ),
    )
    return CognitiveAlignmentResult(
        state=state,
        mode=mode,
        cognitive_alignment_score=score,
        score_breakdown=score_breakdown,
        axes=axes,
        matrix=matrix,
        risks=risks,
        actions=actions,
        recommendations=recommendations,
        events=events,
        summary=summary,
    )


def _render_items(items: tuple[Any, ...]) -> str:
    if not items:
        return "- None"
    return "\n".join(f"- {_value(item)}" for item in items)


def render_cognitive_alignment_markdown(result: CognitiveAlignmentResult) -> str:
    """Render a Markdown report for cognitive alignment."""

    axis_lines = "\n".join(f"- {axis.name}: {axis.score}/100, aligned={axis.aligned}" for axis in result.axes)
    matrix = result.matrix
    return "\n".join(
        [
            "# Cognitive Alignment State",
            f"- State: {result.state.value}",
            f"- Mode: {result.mode.value}",
            "",
            "## Alignment Score",
            f"- Score: {result.cognitive_alignment_score}/100",
            "",
            "## Alignment Axes",
            axis_lines or "- None",
            "",
            "## Alignment Matrix",
            f"- Global score: {matrix.global_score}/100",
            f"- Weakest axis: {matrix.weakest_axis or 'none'}",
            f"- Broken axes: {', '.join(matrix.broken_axes) if matrix.broken_axes else 'none'}",
            f"- Autonomy reduced: {matrix.autonomy_reduced}",
            f"- Locked: {matrix.locked}",
            "",
            "## Alignment Risks",
            _render_items(result.risks),
            "",
            "## Actions",
            _render_items(result.actions),
            "",
            "## Recommendations",
            _render_items(result.recommendations),
            "",
            "## AGIcore Cognitive Alignment Outlook",
            result.summary,
        ]
    )


__all__ = [
    "build_alignment_axes",
    "build_alignment_matrix",
    "compute_cognitive_alignment_score",
    "detect_cognitive_alignment_risks",
    "evaluate_cognitive_alignment",
    "generate_cognitive_alignment_recommendations",
    "render_cognitive_alignment_markdown",
]
