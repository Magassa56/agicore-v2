"""Offline Autonomous Cognitive Intent Integrity Engine for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime
from statistics import mean
from typing import Any

from .cognitive_continuity_models import CognitiveContinuityRisk, CognitiveContinuityState
from .cognitive_governance_models import CognitiveAutonomyLevel, CognitiveGovernanceDecision, CognitiveGovernanceMode
from .cognitive_identity_models import CognitiveIdentityRisk, CognitiveIdentityState
from .cognitive_policy_models import CognitivePolicyMode, CognitivePolicyRisk
from .cognitive_recovery_models import CognitiveRecoveryState
from .cognitive_resilience_models import CognitiveResilienceState
from .cognitive_stability_models import CognitiveStabilityState
from .collective_consensus_models import ConsensusDecision, ConsensusMode
from .global_orchestrator_models import OrchestratorDecision, OrchestratorMode
from .intent_alignment_models import IntentAlignmentMode, IntentRisk
from .intent_integrity_models import (
    IntentChain,
    IntentIntegrityAction,
    IntentIntegrityCheck,
    IntentIntegrityEvent,
    IntentIntegrityInput,
    IntentIntegrityMode,
    IntentIntegrityRecommendation,
    IntentIntegrityResult,
    IntentIntegrityRisk,
    IntentIntegrityScore,
    IntentIntegrityState,
)
from .mission_continuity_models import ContinuityRisk, MissionContinuityMode
from .recursive_world_model_models import WorldModelDecision, WorldModelRisk
from .self_reflection_audit_models import CognitiveAuditRisk, ReflectionState
from .strategic_memory_models import StrategicDriftSignal
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


def detect_intent_integrity_risks(
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
    system_integrity: Any = None,
    mission_continuity: Any = None,
    strategic_timeline_analysis: Any = None,
) -> tuple[IntentIntegrityRisk, ...]:
    """Detect intent integrity risks with deterministic offline heuristics."""

    risks: list[IntentIntegrityRisk] = []

    intent_mode = _get(intent_alignment, "mode")
    intent_risks = _get(intent_alignment, "risks", ())
    if (
        intent_mode
        in (
            IntentAlignmentMode.PARTIAL_DRIFT,
            IntentAlignmentMode.AUTONOMY_DRIFT,
            IntentAlignmentMode.STRATEGIC_DIVERGENCE,
            IntentAlignmentMode.MISALIGNED,
            IntentAlignmentMode.CRITICAL_REALIGNMENT,
        )
        or _has(intent_risks, IntentRisk.STRATEGIC_MISALIGNMENT)
        or _has(_get(strategic_timeline_analysis, "drift_signals", ()), StrategicDriftSignal.STRATEGIC_DEGRADATION)
    ):
        risks.append(IntentIntegrityRisk.INTENT_DRIFT_RISK)

    if (
        intent_mode in (IntentAlignmentMode.MISALIGNED, IntentAlignmentMode.CRITICAL_REALIGNMENT)
        or _get(intent_alignment, "alignment_confidence", 80) < 55
        or _has(intent_risks, IntentRisk.MISSION_DIVERGENCE)
        or _get(mission_continuity, "mode") in (MissionContinuityMode.SURVIVAL_CONTINUITY, MissionContinuityMode.SAFE_PAUSE)
        or _has(_get(mission_continuity, "risks", ()), ContinuityRisk.EXECUTIVE_COLLAPSE)
    ):
        risks.append(IntentIntegrityRisk.MISSION_INTENT_MISMATCH)

    identity_state = _get(cognitive_identity, "state")
    if (
        identity_state
        in (
            CognitiveIdentityState.IDENTITY_DRIFT,
            CognitiveIdentityState.IDENTITY_FRAGMENTED,
            CognitiveIdentityState.IDENTITY_CONFLICTED,
            CognitiveIdentityState.IDENTITY_AT_RISK,
            CognitiveIdentityState.IDENTITY_LOCKED,
        )
        or _get(cognitive_identity, "identity_score", 80) < 60
        or _has(_get(cognitive_identity, "risks", ()), CognitiveIdentityRisk.MISSION_IDENTITY_MISMATCH)
        or _has(_get(cognitive_identity, "risks", ()), CognitiveIdentityRisk.IDENTITY_COLLAPSE_RISK)
    ):
        risks.append(IntentIntegrityRisk.IDENTITY_INTENT_CONFLICT)

    if (
        _get(cognitive_policy, "mode")
        in (CognitivePolicyMode.POLICY_RESTRICTED, CognitivePolicyMode.POLICY_SAFE_MODE, CognitivePolicyMode.POLICY_LOCKED)
        or _has(_get(cognitive_policy, "risks", ()), CognitivePolicyRisk.POLICY_CONFLICT)
        or _has(_get(cognitive_policy, "risks", ()), CognitivePolicyRisk.GOVERNANCE_POLICY_MISMATCH)
        or _get(cognitive_policy, "cognitive_policy_score", 80) < 55
    ):
        risks.append(IntentIntegrityRisk.POLICY_INTENT_CONFLICT)

    if (
        _get(cognitive_governance, "mode")
        in (
            CognitiveGovernanceMode.RESTRICTED_GOVERNANCE,
            CognitiveGovernanceMode.SAFE_GOVERNANCE,
            CognitiveGovernanceMode.DEGRADED_GOVERNANCE,
            CognitiveGovernanceMode.EMERGENCY_GOVERNANCE,
            CognitiveGovernanceMode.LOCKED_GOVERNANCE,
        )
        or _get(cognitive_governance, "decision")
        in (
            CognitiveGovernanceDecision.ENFORCE_SAFE_GOVERNANCE,
            CognitiveGovernanceDecision.DENY_AUTONOMY_EXPANSION,
            CognitiveGovernanceDecision.REQUIRE_HUMAN_REVIEW,
            CognitiveGovernanceDecision.ENTER_LOCKED_GOVERNANCE,
        )
        or _get(cognitive_governance, "governance_score", 80) < 55
    ):
        risks.append(IntentIntegrityRisk.GOVERNANCE_INTENT_CONFLICT)

    if (
        _get(self_reflection_audit, "state")
        in (ReflectionState.DEGRADED_REFLECTION, ReflectionState.CONTRADICTORY_REFLECTION, ReflectionState.AUDIT_REQUIRED)
        or _has(_get(self_reflection_audit, "risks", ()), CognitiveAuditRisk.UNEXPLAINED_DECISION)
        or _has(_get(self_reflection_audit, "risks", ()), CognitiveAuditRisk.STRATEGIC_SELF_CONTRADICTION)
        or _get(global_orchestrator, "decision")
        in (
            OrchestratorDecision.ENTER_SAFE_GLOBAL_MODE,
            OrchestratorDecision.REQUIRE_HUMAN_SUPERVISION,
            OrchestratorDecision.EMERGENCY_HALT_ROUTING,
        )
        or _get(collective_consensus, "decision")
        in (ConsensusDecision.BLOCK_COLLECTIVE_ACTION, ConsensusDecision.EMERGENCY_HALT, ConsensusDecision.NO_CONSENSUS)
    ):
        risks.append(IntentIntegrityRisk.DECISION_INTENT_MISMATCH)

    if (
        _get(cognitive_governance, "autonomy_level") == CognitiveAutonomyLevel.FULL_AUTONOMY
        and risks
        or _has(intent_risks, IntentRisk.AUTONOMY_EXPANSION)
        or intent_mode == IntentAlignmentMode.AUTONOMY_DRIFT
    ):
        risks.append(IntentIntegrityRisk.AUTONOMY_INTENT_EXPANSION)

    if (
        _get(cognitive_continuity, "continuity_score", 80) < 55
        or _get(cognitive_continuity, "state")
        in (CognitiveContinuityState.DEGRADED_CONTINUITY, CognitiveContinuityState.FRAGMENTED_CONTINUITY, CognitiveContinuityState.CONTINUITY_FAILURE)
        or _has(_get(cognitive_continuity, "risks", ()), CognitiveContinuityRisk.DECISION_CHAIN_BREAK)
        or _has(_get(self_reflection_audit, "risks", ()), CognitiveAuditRisk.INCOMPLETE_TRACEABILITY)
    ):
        risks.append(IntentIntegrityRisk.INTENT_CHAIN_BREAK)

    mission_problem = IntentIntegrityRisk.MISSION_INTENT_MISMATCH in risks
    identity_problem = IntentIntegrityRisk.IDENTITY_INTENT_CONFLICT in risks
    policy_problem = IntentIntegrityRisk.POLICY_INTENT_CONFLICT in risks or IntentIntegrityRisk.GOVERNANCE_INTENT_CONFLICT in risks
    if mission_problem and identity_problem and policy_problem:
        risks.append(IntentIntegrityRisk.INTENT_CORRUPTION_RISK)

    if (
        IntentIntegrityRisk.INTENT_CORRUPTION_RISK in risks
        and (IntentIntegrityRisk.INTENT_CHAIN_BREAK in risks or len(risks) >= 6)
        or _get(system_integrity, "status") in (SystemIntegrityStatus.COMPROMISED, SystemIntegrityStatus.ROLLBACK_RECOMMENDED)
        or _get(cognitive_stability, "state") in (CognitiveStabilityState.CRITICAL, CognitiveStabilityState.COLLAPSING)
        or _get(recursive_world_model, "decision") == WorldModelDecision.FREEZE_RECURSIVE_UPDATES
        or _has(_get(recursive_world_model, "risks", ()), WorldModelRisk.RECURSIVE_FEEDBACK_LOOP)
    ):
        risks.append(IntentIntegrityRisk.INTENT_COLLAPSE_RISK)

    if (
        _get(cognitive_recovery, "state")
        in (CognitiveRecoveryState.DEGRADED_RECOVERY, CognitiveRecoveryState.FAILED_RECOVERY)
        or _get(cognitive_resilience, "state") in (CognitiveResilienceState.CRITICAL, CognitiveResilienceState.COGNITIVE_SURVIVAL)
    ):
        risks.append(IntentIntegrityRisk.INTENT_CHAIN_BREAK)

    return _dedupe(tuple(risks))


def compute_intent_integrity_score(
    cognitive_identity: Any = None,
    cognitive_continuity: Any = None,
    cognitive_policy: Any = None,
    cognitive_governance: Any = None,
    self_reflection_audit: Any = None,
    intent_alignment: Any = None,
    risks: tuple[IntentIntegrityRisk, ...] = (),
) -> IntentIntegrityScore:
    """Compute normalized intent integrity component scores."""

    mission = _clamp(_get(intent_alignment, "alignment_confidence", 80))
    identity = _clamp(_get(cognitive_identity, "identity_score", 80))
    policy = _clamp(_get(cognitive_policy, "cognitive_policy_score", 80))
    governance = _clamp(_get(cognitive_governance, "governance_score", 80))
    decision = _clamp(_get(self_reflection_audit, "reflection_quality_score", 80))
    autonomy = 80
    if _get(cognitive_governance, "autonomy_level") in (
        CognitiveAutonomyLevel.SUPERVISED_AUTONOMY,
        CognitiveAutonomyLevel.OBSERVE_ONLY,
        CognitiveAutonomyLevel.LOCKED_AUTONOMY,
        CognitiveAutonomyLevel.HUMAN_REVIEW_REQUIRED,
    ):
        autonomy = 65
    chain = _clamp(_get(cognitive_continuity, "continuity_score", 80))
    corruption = 90

    penalties = {
        IntentIntegrityRisk.MISSION_INTENT_MISMATCH: ("mission", 25),
        IntentIntegrityRisk.IDENTITY_INTENT_CONFLICT: ("identity", 25),
        IntentIntegrityRisk.POLICY_INTENT_CONFLICT: ("policy", 25),
        IntentIntegrityRisk.GOVERNANCE_INTENT_CONFLICT: ("governance", 25),
        IntentIntegrityRisk.DECISION_INTENT_MISMATCH: ("decision", 25),
        IntentIntegrityRisk.AUTONOMY_INTENT_EXPANSION: ("autonomy", 30),
        IntentIntegrityRisk.INTENT_CHAIN_BREAK: ("chain", 30),
        IntentIntegrityRisk.INTENT_DRIFT_RISK: ("chain", 15),
        IntentIntegrityRisk.INTENT_CORRUPTION_RISK: ("corruption", 45),
        IntentIntegrityRisk.INTENT_COLLAPSE_RISK: ("all", 20),
    }
    values = {
        "mission": mission,
        "identity": identity,
        "policy": policy,
        "governance": governance,
        "decision": decision,
        "autonomy": autonomy,
        "chain": chain,
        "corruption": corruption,
    }
    for risk in risks:
        target, penalty = penalties[risk]
        if target == "all":
            values = {key: value - penalty for key, value in values.items()}
        else:
            values[target] -= penalty

    return IntentIntegrityScore(
        mission_intent_score=_clamp(values["mission"]),
        identity_intent_score=_clamp(values["identity"]),
        policy_intent_score=_clamp(values["policy"]),
        governance_intent_score=_clamp(values["governance"]),
        decision_link_score=_clamp(values["decision"]),
        autonomy_intent_score=_clamp(values["autonomy"]),
        chain_integrity_score=_clamp(values["chain"]),
        corruption_resistance_score=_clamp(values["corruption"]),
    )


def run_intent_integrity_checks(
    score_breakdown: IntentIntegrityScore,
    risks: tuple[IntentIntegrityRisk, ...] = (),
) -> tuple[IntentIntegrityCheck, ...]:
    """Build auditable checks for mission, identity, policies and decisions."""

    mapping = (
        ("mission_intent", score_breakdown.mission_intent_score, IntentIntegrityRisk.MISSION_INTENT_MISMATCH),
        ("identity_intent", score_breakdown.identity_intent_score, IntentIntegrityRisk.IDENTITY_INTENT_CONFLICT),
        ("policy_intent", score_breakdown.policy_intent_score, IntentIntegrityRisk.POLICY_INTENT_CONFLICT),
        ("governance_intent", score_breakdown.governance_intent_score, IntentIntegrityRisk.GOVERNANCE_INTENT_CONFLICT),
        ("decision_intent_link", score_breakdown.decision_link_score, IntentIntegrityRisk.DECISION_INTENT_MISMATCH),
        ("autonomy_intent", score_breakdown.autonomy_intent_score, IntentIntegrityRisk.AUTONOMY_INTENT_EXPANSION),
        ("intent_chain", score_breakdown.chain_integrity_score, IntentIntegrityRisk.INTENT_CHAIN_BREAK),
        ("corruption_resistance", score_breakdown.corruption_resistance_score, IntentIntegrityRisk.INTENT_CORRUPTION_RISK),
    )
    checks: list[IntentIntegrityCheck] = []
    for name, score, risk in mapping:
        failed = risk in risks or score < 60
        checks.append(
            IntentIntegrityCheck(
                name=name,
                passed=not failed,
                score=score,
                risk=risk if failed else None,
                message="passed" if not failed else f"{risk.value} requires correction",
            )
        )
    return tuple(checks)


def build_intent_chain(
    score_breakdown: IntentIntegrityScore,
    checks: tuple[IntentIntegrityCheck, ...],
    risks: tuple[IntentIntegrityRisk, ...] = (),
) -> IntentChain:
    """Build an explainable intent chain from mission to decision links."""

    broken_links = tuple(check.name for check in checks if not check.passed)
    return IntentChain(
        mission_intent="Preserve mission and offline safety before performance expansion.",
        identity_intent="Keep cognitive identity aligned with mission, discipline and continuity.",
        policy_intent="Enforce governance and policy limits before any autonomy expansion.",
        governance_intent="Apply supervision, traceability and safety controls to intent changes.",
        decision_intent="Link decisions back to auditable mission, identity and policy evidence.",
        chain_score=score_breakdown.chain_integrity_score,
        broken_links=broken_links,
        verified=not broken_links and not risks,
    )


def generate_intent_integrity_recommendations(
    risks: tuple[IntentIntegrityRisk, ...] = (),
    state: IntentIntegrityState = IntentIntegrityState.INTENT_INTACT,
) -> tuple[IntentIntegrityRecommendation, ...]:
    """Generate ordered intent integrity recommendations."""

    recommendations: list[IntentIntegrityRecommendation] = [IntentIntegrityRecommendation.PRESERVE_CORE_INTENT]
    if IntentIntegrityRisk.MISSION_INTENT_MISMATCH in risks:
        recommendations.append(IntentIntegrityRecommendation.VERIFY_MISSION_OBJECTIVES)
    if IntentIntegrityRisk.INTENT_CHAIN_BREAK in risks:
        recommendations.append(IntentIntegrityRecommendation.REPAIR_INTENT_CHAIN)
    if IntentIntegrityRisk.IDENTITY_INTENT_CONFLICT in risks:
        recommendations.append(IntentIntegrityRecommendation.ALIGN_INTENT_WITH_IDENTITY)
    if IntentIntegrityRisk.POLICY_INTENT_CONFLICT in risks:
        recommendations.append(IntentIntegrityRecommendation.ALIGN_INTENT_WITH_POLICY)
    if IntentIntegrityRisk.GOVERNANCE_INTENT_CONFLICT in risks:
        recommendations.append(IntentIntegrityRecommendation.RECHECK_GOVERNANCE_CONSISTENCY)
    if IntentIntegrityRisk.AUTONOMY_INTENT_EXPANSION in risks:
        recommendations.append(IntentIntegrityRecommendation.REDUCE_AUTONOMY_DURING_INTENT_REPAIR)
    if state in (
        IntentIntegrityState.INTENT_AT_RISK,
        IntentIntegrityState.INTENT_CONFLICT,
        IntentIntegrityState.INTENT_CORRUPTED,
        IntentIntegrityState.INTENT_LOCKED,
    ):
        recommendations.append(IntentIntegrityRecommendation.REQUIRE_SUPERVISION)
    recommendations.append(IntentIntegrityRecommendation.UPDATE_INTENT_SNAPSHOT)
    if not risks:
        recommendations.append(IntentIntegrityRecommendation.CONTINUE_INTENT_MONITORING)
    return _dedupe(tuple(recommendations))


def _select_state(risks: tuple[IntentIntegrityRisk, ...]) -> IntentIntegrityState:
    if IntentIntegrityRisk.INTENT_COLLAPSE_RISK in risks:
        return IntentIntegrityState.INTENT_LOCKED
    if IntentIntegrityRisk.INTENT_CORRUPTION_RISK in risks:
        return IntentIntegrityState.INTENT_CORRUPTED
    if IntentIntegrityRisk.AUTONOMY_INTENT_EXPANSION in risks and IntentIntegrityRisk.MISSION_INTENT_MISMATCH in risks:
        return IntentIntegrityState.INTENT_AT_RISK
    if (
        IntentIntegrityRisk.IDENTITY_INTENT_CONFLICT in risks
        and (IntentIntegrityRisk.POLICY_INTENT_CONFLICT in risks or IntentIntegrityRisk.GOVERNANCE_INTENT_CONFLICT in risks)
    ):
        return IntentIntegrityState.INTENT_CONFLICT
    if IntentIntegrityRisk.INTENT_CHAIN_BREAK in risks:
        return IntentIntegrityState.INTENT_REPAIRING
    if IntentIntegrityRisk.INTENT_DRIFT_RISK in risks:
        return IntentIntegrityState.INTENT_DRIFT
    if risks:
        return IntentIntegrityState.INTENT_WATCH
    return IntentIntegrityState.INTENT_INTACT


def _select_mode(state: IntentIntegrityState, risks: tuple[IntentIntegrityRisk, ...]) -> IntentIntegrityMode:
    if state == IntentIntegrityState.INTENT_LOCKED:
        return IntentIntegrityMode.LOCKED_INTENT_MODE
    if state in (IntentIntegrityState.INTENT_AT_RISK, IntentIntegrityState.INTENT_CORRUPTED):
        return IntentIntegrityMode.SAFE_INTENT_MODE
    if IntentIntegrityRisk.MISSION_INTENT_MISMATCH in risks:
        return IntentIntegrityMode.MISSION_INTENT_PROTECTION
    if IntentIntegrityRisk.IDENTITY_INTENT_CONFLICT in risks:
        return IntentIntegrityMode.IDENTITY_INTENT_SYNC
    if IntentIntegrityRisk.POLICY_INTENT_CONFLICT in risks or IntentIntegrityRisk.GOVERNANCE_INTENT_CONFLICT in risks:
        return IntentIntegrityMode.POLICY_INTENT_ENFORCEMENT
    if IntentIntegrityRisk.INTENT_CHAIN_BREAK in risks:
        return IntentIntegrityMode.INTENT_CHAIN_VERIFICATION
    if risks:
        return IntentIntegrityMode.INTENT_MONITORING
    return IntentIntegrityMode.NORMAL_INTENT_INTEGRITY


def _build_actions(risks: tuple[IntentIntegrityRisk, ...]) -> tuple[IntentIntegrityAction, ...]:
    actions: list[IntentIntegrityAction] = [IntentIntegrityAction.PRESERVE_INTENT_CHAIN]
    if IntentIntegrityRisk.MISSION_INTENT_MISMATCH in risks:
        actions.append(IntentIntegrityAction.VERIFY_MISSION_INTENT)
    if IntentIntegrityRisk.IDENTITY_INTENT_CONFLICT in risks:
        actions.append(IntentIntegrityAction.SYNC_IDENTITY_INTENT)
    if IntentIntegrityRisk.POLICY_INTENT_CONFLICT in risks or IntentIntegrityRisk.GOVERNANCE_INTENT_CONFLICT in risks:
        actions.append(IntentIntegrityAction.ENFORCE_POLICY_INTENT)
    if IntentIntegrityRisk.DECISION_INTENT_MISMATCH in risks or IntentIntegrityRisk.INTENT_CHAIN_BREAK in risks:
        actions.append(IntentIntegrityAction.RESTORE_DECISION_INTENT_LINK)
    if risks:
        actions.extend((IntentIntegrityAction.REDUCE_AUTONOMY, IntentIntegrityAction.REQUIRE_INTENT_AUDIT))
    if IntentIntegrityRisk.INTENT_COLLAPSE_RISK in risks or IntentIntegrityRisk.INTENT_CORRUPTION_RISK in risks:
        actions.extend((IntentIntegrityAction.LOCK_INTENT_STATE, IntentIntegrityAction.REQUIRE_HUMAN_REVIEW))
    if not risks:
        actions.append(IntentIntegrityAction.MARK_INTENT_INTEGRITY_RESTORED)
    return _dedupe(tuple(actions))


def evaluate_intent_integrity(
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
    system_integrity: Any = None,
    mission_continuity: Any = None,
    strategic_timeline_analysis: Any = None,
    input_data: IntentIntegrityInput | None = None,
) -> IntentIntegrityResult:
    """Evaluate internal intent integrity without external calls."""

    if input_data is not None:
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
        system_integrity = input_data.system_integrity
        mission_continuity = input_data.mission_continuity
        strategic_timeline_analysis = input_data.strategic_timeline_analysis

    risks = detect_intent_integrity_risks(
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
        system_integrity=system_integrity,
        mission_continuity=mission_continuity,
        strategic_timeline_analysis=strategic_timeline_analysis,
    )
    score_breakdown = compute_intent_integrity_score(
        cognitive_identity=cognitive_identity,
        cognitive_continuity=cognitive_continuity,
        cognitive_policy=cognitive_policy,
        cognitive_governance=cognitive_governance,
        self_reflection_audit=self_reflection_audit,
        intent_alignment=intent_alignment,
        risks=risks,
    )
    checks = run_intent_integrity_checks(score_breakdown=score_breakdown, risks=risks)
    intent_chain = build_intent_chain(score_breakdown=score_breakdown, checks=checks, risks=risks)
    intent_integrity_score = _average(tuple(score_breakdown.__dict__.values()))
    state = _select_state(risks)
    mode = _select_mode(state, risks)
    actions = _build_actions(risks)
    recommendations = generate_intent_integrity_recommendations(risks=risks, state=state)
    summary = (
        "Intent integrity intact and verified."
        if not risks
        else f"Intent integrity requires controls for {len(risks)} detected risk(s)."
    )
    events = (
        IntentIntegrityEvent(
            state=state,
            mode=mode,
            message=summary,
            timestamp=datetime.now(UTC),
        ),
    )

    return IntentIntegrityResult(
        state=state,
        mode=mode,
        intent_integrity_score=intent_integrity_score,
        score_breakdown=score_breakdown,
        intent_chain=intent_chain,
        checks=checks,
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


def render_intent_integrity_markdown(result: IntentIntegrityResult) -> str:
    """Render a Markdown report for intent integrity."""

    check_lines = "\n".join(
        f"- {check.name}: {check.score}/100, passed={check.passed}"
        for check in result.checks
    )
    chain = result.intent_chain
    return "\n".join(
        [
            "# Intent Integrity State",
            f"- State: {result.state.value}",
            f"- Mode: {result.mode.value}",
            "",
            "## Intent Integrity Score",
            f"- Score: {result.intent_integrity_score}/100",
            "",
            "## Intent Chain",
            f"- Chain score: {chain.chain_score}/100",
            f"- Verified: {chain.verified}",
            f"- Broken links: {', '.join(chain.broken_links) if chain.broken_links else 'none'}",
            "",
            "## Integrity Checks",
            check_lines or "- None",
            "",
            "## Risks",
            _render_items(result.risks),
            "",
            "## Actions",
            _render_items(result.actions),
            "",
            "## Recommendations",
            _render_items(result.recommendations),
            "",
            "## AGIcore Intent Integrity Outlook",
            result.summary,
        ]
    )


__all__ = [
    "build_intent_chain",
    "compute_intent_integrity_score",
    "detect_intent_integrity_risks",
    "evaluate_intent_integrity",
    "generate_intent_integrity_recommendations",
    "render_intent_integrity_markdown",
    "run_intent_integrity_checks",
]
