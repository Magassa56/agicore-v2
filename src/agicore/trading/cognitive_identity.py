"""Offline Autonomous Cognitive Identity Engine for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime
from statistics import mean
from typing import Any

from .cognitive_continuity_models import CognitiveContinuityRisk, CognitiveContinuityState
from .cognitive_governance_models import CognitiveAutonomyLevel, CognitiveGovernanceDecision, CognitiveGovernanceMode
from .cognitive_identity_models import (
    CognitiveIdentityAction,
    CognitiveIdentityEvent,
    CognitiveIdentityInput,
    CognitiveIdentityMode,
    CognitiveIdentityProfile,
    CognitiveIdentityRecommendation,
    CognitiveIdentityResult,
    CognitiveIdentityRisk,
    CognitiveIdentityScore,
    CognitiveIdentityState,
    CognitiveInvariant,
)
from .cognitive_policy_models import CognitivePolicyMode, CognitivePolicyRisk
from .cognitive_recovery_models import CognitiveRecoveryState
from .cognitive_resilience_models import CognitiveResilienceState
from .cognitive_stability_models import CognitiveStabilityState
from .collective_consensus_models import ConsensusDecision, ConsensusMode, ConsensusRisk
from .intent_alignment_models import IntentAlignmentMode, IntentRisk
from .mission_continuity_models import ContinuityRisk, MissionContinuityMode
from .recursive_world_model_models import WorldModelDecision, WorldModelRisk
from .strategic_memory_models import StrategicDriftSignal
from .system_integrity_models import SystemIntegrityStatus


def _value(item: Any) -> str:
    return getattr(item, "value", str(item))


def _has(items: Any, expected: Any) -> bool:
    expected_value = _value(expected)
    return any(_value(item) == expected_value for item in (items or ()))


def _get(obj: Any, attr: str, default: Any = None) -> Any:
    return getattr(obj, attr, default) if obj is not None else default


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


def detect_cognitive_identity_risks(
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
    strategy_dna: Any = None,
) -> tuple[CognitiveIdentityRisk, ...]:
    """Detect identity drift, fragmentation and invariant breaks using offline heuristics."""

    risks: list[CognitiveIdentityRisk] = []

    continuity_state = _get(cognitive_continuity, "state")
    continuity_risks = _get(cognitive_continuity, "risks", ())
    if (
        continuity_state in (CognitiveContinuityState.IDENTITY_DRIFT, CognitiveContinuityState.CONTINUITY_FAILURE)
        or _has(continuity_risks, CognitiveContinuityRisk.STRATEGIC_IDENTITY_DRIFT)
        or _get(strategic_timeline_analysis, "strategic_health_score", 80) < 55
        or _has(_get(strategic_timeline_analysis, "drift_signals", ()), StrategicDriftSignal.STRATEGIC_DEGRADATION)
    ):
        risks.append(CognitiveIdentityRisk.STRATEGIC_IDENTITY_DRIFT)

    intent_mode = _get(intent_alignment, "mode")
    intent_risks = _get(intent_alignment, "risks", ())
    if (
        intent_mode
        in (
            IntentAlignmentMode.MISALIGNED,
            IntentAlignmentMode.CRITICAL_REALIGNMENT,
            IntentAlignmentMode.STRATEGIC_DIVERGENCE,
        )
        or _get(intent_alignment, "alignment_confidence", 80) < 55
        or _has(intent_risks, IntentRisk.MISSION_DIVERGENCE)
        or _has(_get(mission_continuity, "risks", ()), ContinuityRisk.EXECUTIVE_COLLAPSE)
        or _get(mission_continuity, "mode") in (MissionContinuityMode.SURVIVAL_CONTINUITY, MissionContinuityMode.SAFE_PAUSE)
    ):
        risks.append(CognitiveIdentityRisk.MISSION_IDENTITY_MISMATCH)

    priority_score = _get(_get(intent_alignment, "confidence_breakdown"), "priority_stability_score", 80)
    if (
        intent_mode == IntentAlignmentMode.PRIORITY_CONFLICT
        or priority_score < 55
        or _has(continuity_risks, CognitiveContinuityRisk.PRIORITY_ORDER_LOSS)
    ):
        risks.append(CognitiveIdentityRisk.PRIORITY_INVARIANT_BREAK)

    governance_mode = _get(cognitive_governance, "mode")
    governance_decision = _get(cognitive_governance, "decision")
    if (
        governance_mode
        in (
            CognitiveGovernanceMode.RESTRICTED_GOVERNANCE,
            CognitiveGovernanceMode.SAFE_GOVERNANCE,
            CognitiveGovernanceMode.DEGRADED_GOVERNANCE,
            CognitiveGovernanceMode.EMERGENCY_GOVERNANCE,
            CognitiveGovernanceMode.LOCKED_GOVERNANCE,
        )
        or governance_decision
        in (
            CognitiveGovernanceDecision.ENFORCE_SAFE_GOVERNANCE,
            CognitiveGovernanceDecision.DENY_AUTONOMY_EXPANSION,
            CognitiveGovernanceDecision.REQUIRE_HUMAN_REVIEW,
            CognitiveGovernanceDecision.ENTER_LOCKED_GOVERNANCE,
        )
        or _get(cognitive_governance, "governance_score", 80) < 55
    ):
        risks.append(CognitiveIdentityRisk.GOVERNANCE_IDENTITY_CONFLICT)

    if (
        _get(cognitive_policy, "mode")
        in (CognitivePolicyMode.POLICY_RESTRICTED, CognitivePolicyMode.POLICY_SAFE_MODE, CognitivePolicyMode.POLICY_LOCKED)
        or _has(_get(cognitive_policy, "risks", ()), CognitivePolicyRisk.GOVERNANCE_POLICY_MISMATCH)
        or _has(_get(cognitive_policy, "risks", ()), CognitivePolicyRisk.POLICY_CONFLICT)
        or _has(_get(cognitive_policy, "risks", ()), CognitivePolicyRisk.SAFETY_CRITICAL_BYPASS)
    ):
        risks.append(CognitiveIdentityRisk.POLICY_IDENTITY_CONFLICT)

    if (
        _get(recursive_world_model, "world_model_coherence_score", 80) < 60
        or _get(recursive_world_model, "decision")
        in (
            WorldModelDecision.REBUILD_CAUSAL_GRAPH,
            WorldModelDecision.ENTER_WORLD_MODEL_SAFE_MODE,
            WorldModelDecision.FREEZE_RECURSIVE_UPDATES,
        )
        or _has(_get(recursive_world_model, "risks", ()), WorldModelRisk.WORLD_MODEL_INCOHERENCE)
        or _has(_get(recursive_world_model, "risks", ()), WorldModelRisk.STATE_DRIFT)
        or _has(_get(recursive_world_model, "risks", ()), WorldModelRisk.GOVERNANCE_MISALIGNMENT)
    ):
        risks.append(CognitiveIdentityRisk.WORLD_MODEL_IDENTITY_DRIFT)

    if (
        _get(collective_consensus, "collective_confidence_score", 80) < 60
        or _get(collective_consensus, "mode") in (ConsensusMode.DEGRADED_CONSENSUS, ConsensusMode.CONSENSUS_COLLAPSE)
        or _get(collective_consensus, "decision")
        in (
            ConsensusDecision.BLOCK_COLLECTIVE_ACTION,
            ConsensusDecision.EMERGENCY_HALT,
            ConsensusDecision.NO_CONSENSUS,
        )
        or _has(_get(collective_consensus, "risks", ()), ConsensusRisk.CONSENSUS_FRAGMENTATION)
    ):
        risks.append(CognitiveIdentityRisk.CONSENSUS_IDENTITY_FRAGMENTATION)

    if (
        _get(cognitive_recovery, "state")
        in (
            CognitiveRecoveryState.RECOVERING,
            CognitiveRecoveryState.PARTIAL_RECOVERY,
            CognitiveRecoveryState.DEGRADED_RECOVERY,
            CognitiveRecoveryState.SAFE_RECOVERY,
            CognitiveRecoveryState.HUMAN_REVIEW_REQUIRED,
        )
        or _get(cognitive_resilience, "state")
        in (
            CognitiveResilienceState.FRAGILE,
            CognitiveResilienceState.CRITICAL,
            CognitiveResilienceState.RECOVERING,
            CognitiveResilienceState.COGNITIVE_SURVIVAL,
        )
        or continuity_state == CognitiveContinuityState.RECOVERING_CONTINUITY
    ):
        risks.append(CognitiveIdentityRisk.RECOVERY_IDENTITY_DISCONTINUITY)

    if (
        _get(cognitive_governance, "autonomy_level") == CognitiveAutonomyLevel.FULL_AUTONOMY
        and risks
        or intent_mode == IntentAlignmentMode.AUTONOMY_DRIFT
        or _has(intent_risks, IntentRisk.AUTONOMY_EXPANSION)
    ):
        risks.append(CognitiveIdentityRisk.AUTONOMY_IDENTITY_EXPANSION)

    if (
        continuity_state == CognitiveContinuityState.CONTINUITY_FAILURE
        or _get(system_integrity, "status") in (SystemIntegrityStatus.COMPROMISED, SystemIntegrityStatus.ROLLBACK_RECOMMENDED)
        or _get(cognitive_stability, "state") in (CognitiveStabilityState.CRITICAL, CognitiveStabilityState.COLLAPSING)
        or len(risks) >= 5
    ):
        risks.append(CognitiveIdentityRisk.IDENTITY_COLLAPSE_RISK)

    return _dedupe(tuple(risks))


def compute_cognitive_identity_score(
    cognitive_continuity: Any = None,
    cognitive_policy: Any = None,
    cognitive_governance: Any = None,
    recursive_world_model: Any = None,
    collective_consensus: Any = None,
    intent_alignment: Any = None,
    strategic_timeline_analysis: Any = None,
    strategy_dna: Any = None,
    risks: tuple[CognitiveIdentityRisk, ...] = (),
) -> CognitiveIdentityScore:
    """Compute normalized identity component scores."""

    mission_alignment = _clamp(_get(intent_alignment, "alignment_confidence", 80))
    strategic_dna = _clamp(_get(strategic_timeline_analysis, "strategic_health_score", 80))
    if strategy_dna is None:
        strategic_dna = min(strategic_dna, 70)
    priority = _clamp(_get(_get(intent_alignment, "confidence_breakdown"), "priority_stability_score", mission_alignment))
    governance = _clamp(_get(cognitive_governance, "governance_score", 80))
    policy = _clamp(_get(cognitive_policy, "cognitive_policy_score", 80))
    world_model = _clamp(_get(recursive_world_model, "world_model_coherence_score", 80))
    consensus = _clamp(_get(collective_consensus, "collective_confidence_score", 80))
    continuity = _clamp(_get(cognitive_continuity, "continuity_score", 80))
    autonomy = 80
    if _get(cognitive_governance, "autonomy_level") in (
        CognitiveAutonomyLevel.SUPERVISED_AUTONOMY,
        CognitiveAutonomyLevel.OBSERVE_ONLY,
        CognitiveAutonomyLevel.LOCKED_AUTONOMY,
        CognitiveAutonomyLevel.HUMAN_REVIEW_REQUIRED,
    ):
        autonomy = 65

    penalties = {
        CognitiveIdentityRisk.MISSION_IDENTITY_MISMATCH: ("mission", 25),
        CognitiveIdentityRisk.STRATEGIC_IDENTITY_DRIFT: ("strategy", 25),
        CognitiveIdentityRisk.PRIORITY_INVARIANT_BREAK: ("priority", 25),
        CognitiveIdentityRisk.GOVERNANCE_IDENTITY_CONFLICT: ("governance", 25),
        CognitiveIdentityRisk.POLICY_IDENTITY_CONFLICT: ("policy", 25),
        CognitiveIdentityRisk.WORLD_MODEL_IDENTITY_DRIFT: ("world", 25),
        CognitiveIdentityRisk.CONSENSUS_IDENTITY_FRAGMENTATION: ("consensus", 25),
        CognitiveIdentityRisk.RECOVERY_IDENTITY_DISCONTINUITY: ("continuity", 15),
        CognitiveIdentityRisk.AUTONOMY_IDENTITY_EXPANSION: ("autonomy", 30),
        CognitiveIdentityRisk.IDENTITY_COLLAPSE_RISK: ("all", 15),
    }
    values = {
        "mission": mission_alignment,
        "strategy": strategic_dna,
        "priority": priority,
        "governance": governance,
        "policy": policy,
        "world": world_model,
        "consensus": consensus,
        "continuity": continuity,
        "autonomy": autonomy,
    }
    for risk in risks:
        target, penalty = penalties[risk]
        if target == "all":
            values = {key: value - penalty for key, value in values.items()}
        else:
            values[target] -= penalty

    return CognitiveIdentityScore(
        mission_alignment_score=_clamp(values["mission"]),
        strategic_dna_score=_clamp(values["strategy"]),
        priority_invariant_score=_clamp(values["priority"]),
        governance_identity_score=_clamp(values["governance"]),
        policy_identity_score=_clamp(values["policy"]),
        world_model_identity_score=_clamp(values["world"]),
        consensus_identity_score=_clamp(values["consensus"]),
        continuity_identity_score=_clamp(values["continuity"]),
        autonomy_safety_score=_clamp(values["autonomy"]),
    )


def build_cognitive_invariants(
    risks: tuple[CognitiveIdentityRisk, ...] = (),
    strategy_dna: Any = None,
) -> tuple[CognitiveInvariant, ...]:
    """Build core mission, safety and strategy invariants."""

    def invariant(
        name: str,
        description: str,
        priority: int,
        related_risks: tuple[CognitiveIdentityRisk, ...],
    ) -> CognitiveInvariant:
        violated = tuple(risk for risk in related_risks if risk in risks)
        score = _clamp(95 - 25 * len(violated) - (10 if CognitiveIdentityRisk.IDENTITY_COLLAPSE_RISK in risks else 0))
        return CognitiveInvariant(
            name=name,
            description=description,
            priority=priority,
            score=score,
            protected=not violated and CognitiveIdentityRisk.IDENTITY_COLLAPSE_RISK not in risks,
            violated_by=violated,
        )

    strategy_name = _get(strategy_dna, "name", "active strategy DNA")
    return (
        invariant(
            "mission_continuity",
            "Preserve offline mission continuity before performance expansion.",
            100,
            (CognitiveIdentityRisk.MISSION_IDENTITY_MISMATCH, CognitiveIdentityRisk.RECOVERY_IDENTITY_DISCONTINUITY),
        ),
        invariant(
            "safety_boundary",
            "Keep all decisions offline, paper-only and safety-first.",
            95,
            (CognitiveIdentityRisk.GOVERNANCE_IDENTITY_CONFLICT, CognitiveIdentityRisk.AUTONOMY_IDENTITY_EXPANSION),
        ),
        invariant(
            "discipline_and_capital_preservation",
            "Protect discipline, risk controls and capital preservation.",
            90,
            (CognitiveIdentityRisk.PRIORITY_INVARIANT_BREAK, CognitiveIdentityRisk.POLICY_IDENTITY_CONFLICT),
        ),
        invariant(
            "strategic_dna",
            f"Preserve stable strategy DNA for {strategy_name}.",
            85,
            (CognitiveIdentityRisk.STRATEGIC_IDENTITY_DRIFT, CognitiveIdentityRisk.WORLD_MODEL_IDENTITY_DRIFT),
        ),
        invariant(
            "collective_coherence",
            "Maintain consensus, governance and identity coherence across cognitive layers.",
            80,
            (CognitiveIdentityRisk.CONSENSUS_IDENTITY_FRAGMENTATION, CognitiveIdentityRisk.IDENTITY_COLLAPSE_RISK),
        ),
    )


def build_cognitive_identity_profile(
    risks: tuple[CognitiveIdentityRisk, ...] = (),
    identity_score: int = 75,
    strategy_dna: Any = None,
) -> CognitiveIdentityProfile:
    """Build an explainable identity profile from strategy and invariant evidence."""

    invariants = build_cognitive_invariants(risks=risks, strategy_dna=strategy_dna)
    strategy_name = _get(strategy_dna, "name")
    priorities = (
        "SURVIVAL",
        "SYSTEM_INTEGRITY",
        "SAFETY",
        "MISSION",
        "CONTINUITY",
        "DISCIPLINE",
        "STRATEGY_DNA",
        "LEARNING_ONLY_AFTER_STABILITY",
    )
    return CognitiveIdentityProfile(
        profile_name="AGIcore Trading Cognitive Identity",
        mission_statement="Maintain a safe offline trading intelligence stack aligned with mission, discipline and capital preservation.",
        strategy_name=strategy_name,
        core_priorities=priorities,
        invariants=invariants,
        identity_score=_clamp(identity_score),
        autonomy_limited=bool(risks),
        locked=CognitiveIdentityRisk.IDENTITY_COLLAPSE_RISK in risks,
    )


def generate_cognitive_identity_recommendations(
    risks: tuple[CognitiveIdentityRisk, ...] = (),
    state: CognitiveIdentityState = CognitiveIdentityState.IDENTITY_STABLE,
) -> tuple[CognitiveIdentityRecommendation, ...]:
    """Generate ordered identity recommendations."""

    recommendations: list[CognitiveIdentityRecommendation] = [CognitiveIdentityRecommendation.PRESERVE_CORE_IDENTITY]
    if CognitiveIdentityRisk.MISSION_IDENTITY_MISMATCH in risks:
        recommendations.append(CognitiveIdentityRecommendation.VERIFY_MISSION_ALIGNMENT)
    if CognitiveIdentityRisk.STRATEGIC_IDENTITY_DRIFT in risks:
        recommendations.append(CognitiveIdentityRecommendation.PROTECT_STRATEGIC_DNA)
    if CognitiveIdentityRisk.PRIORITY_INVARIANT_BREAK in risks:
        recommendations.append(CognitiveIdentityRecommendation.RECHECK_PRIORITY_ORDER)
    if (
        CognitiveIdentityRisk.CONSENSUS_IDENTITY_FRAGMENTATION in risks
        or CognitiveIdentityRisk.GOVERNANCE_IDENTITY_CONFLICT in risks
        or CognitiveIdentityRisk.POLICY_IDENTITY_CONFLICT in risks
    ):
        recommendations.append(CognitiveIdentityRecommendation.REPAIR_IDENTITY_FRAGMENTATION)
    if CognitiveIdentityRisk.RECOVERY_IDENTITY_DISCONTINUITY in risks:
        recommendations.append(CognitiveIdentityRecommendation.KEEP_RECOVERY_CONTEXT_ACTIVE)
    if CognitiveIdentityRisk.AUTONOMY_IDENTITY_EXPANSION in risks:
        recommendations.append(CognitiveIdentityRecommendation.LIMIT_AUTONOMY_EXPANSION)
    if state in (
        CognitiveIdentityState.IDENTITY_AT_RISK,
        CognitiveIdentityState.IDENTITY_CONFLICTED,
        CognitiveIdentityState.IDENTITY_FRAGMENTED,
        CognitiveIdentityState.IDENTITY_LOCKED,
    ):
        recommendations.append(CognitiveIdentityRecommendation.REQUIRE_SUPERVISION)
    recommendations.append(CognitiveIdentityRecommendation.UPDATE_IDENTITY_SNAPSHOT)
    if not risks:
        recommendations.append(CognitiveIdentityRecommendation.CONTINUE_IDENTITY_MONITORING)
    return _dedupe(tuple(recommendations))


def _select_state(risks: tuple[CognitiveIdentityRisk, ...]) -> CognitiveIdentityState:
    if CognitiveIdentityRisk.IDENTITY_COLLAPSE_RISK in risks:
        return CognitiveIdentityState.IDENTITY_LOCKED
    if CognitiveIdentityRisk.MISSION_IDENTITY_MISMATCH in risks and CognitiveIdentityRisk.AUTONOMY_IDENTITY_EXPANSION in risks:
        return CognitiveIdentityState.IDENTITY_AT_RISK
    if (
        CognitiveIdentityRisk.CONSENSUS_IDENTITY_FRAGMENTATION in risks
        and CognitiveIdentityRisk.GOVERNANCE_IDENTITY_CONFLICT in risks
        and CognitiveIdentityRisk.POLICY_IDENTITY_CONFLICT in risks
    ):
        return CognitiveIdentityState.IDENTITY_FRAGMENTED
    if len(risks) >= 4:
        return CognitiveIdentityState.IDENTITY_CONFLICTED
    if CognitiveIdentityRisk.STRATEGIC_IDENTITY_DRIFT in risks:
        return CognitiveIdentityState.IDENTITY_DRIFT
    if CognitiveIdentityRisk.RECOVERY_IDENTITY_DISCONTINUITY in risks:
        return CognitiveIdentityState.IDENTITY_RESTORING
    if risks:
        return CognitiveIdentityState.IDENTITY_WATCH
    return CognitiveIdentityState.IDENTITY_STABLE


def _select_mode(state: CognitiveIdentityState, risks: tuple[CognitiveIdentityRisk, ...]) -> CognitiveIdentityMode:
    if state == CognitiveIdentityState.IDENTITY_LOCKED:
        return CognitiveIdentityMode.LOCKED_IDENTITY_MODE
    if state in (CognitiveIdentityState.IDENTITY_AT_RISK, CognitiveIdentityState.IDENTITY_CONFLICTED):
        return CognitiveIdentityMode.SAFE_IDENTITY_MODE
    if CognitiveIdentityRisk.MISSION_IDENTITY_MISMATCH in risks:
        return CognitiveIdentityMode.MISSION_ALIGNMENT
    if CognitiveIdentityRisk.PRIORITY_INVARIANT_BREAK in risks:
        return CognitiveIdentityMode.PRIORITY_RESTORATION
    if CognitiveIdentityRisk.STRATEGIC_IDENTITY_DRIFT in risks:
        return CognitiveIdentityMode.INVARIANT_PROTECTION
    if state in (CognitiveIdentityState.IDENTITY_FRAGMENTED, CognitiveIdentityState.IDENTITY_RESTORING):
        return CognitiveIdentityMode.IDENTITY_REPAIR
    if risks:
        return CognitiveIdentityMode.IDENTITY_MONITORING
    return CognitiveIdentityMode.NORMAL_IDENTITY


def _build_actions(risks: tuple[CognitiveIdentityRisk, ...]) -> tuple[CognitiveIdentityAction, ...]:
    actions: list[CognitiveIdentityAction] = [CognitiveIdentityAction.PRESERVE_IDENTITY_PROFILE]
    if risks:
        actions.append(CognitiveIdentityAction.PROTECT_CORE_INVARIANTS)
    if CognitiveIdentityRisk.MISSION_IDENTITY_MISMATCH in risks:
        actions.append(CognitiveIdentityAction.RESTORE_MISSION_ALIGNMENT)
    if CognitiveIdentityRisk.PRIORITY_INVARIANT_BREAK in risks:
        actions.append(CognitiveIdentityAction.RESTORE_PRIORITY_INVARIANTS)
    if CognitiveIdentityRisk.GOVERNANCE_IDENTITY_CONFLICT in risks:
        actions.append(CognitiveIdentityAction.SYNC_GOVERNANCE_WITH_IDENTITY)
    if CognitiveIdentityRisk.POLICY_IDENTITY_CONFLICT in risks:
        actions.append(CognitiveIdentityAction.SYNC_POLICY_WITH_IDENTITY)
    if any(
        risk in risks
        for risk in (
            CognitiveIdentityRisk.STRATEGIC_IDENTITY_DRIFT,
            CognitiveIdentityRisk.WORLD_MODEL_IDENTITY_DRIFT,
            CognitiveIdentityRisk.CONSENSUS_IDENTITY_FRAGMENTATION,
            CognitiveIdentityRisk.RECOVERY_IDENTITY_DISCONTINUITY,
        )
    ):
        actions.append(CognitiveIdentityAction.REPAIR_IDENTITY_CONTEXT)
    if risks:
        actions.append(CognitiveIdentityAction.KEEP_AUTONOMY_REDUCED)
    if CognitiveIdentityRisk.IDENTITY_COLLAPSE_RISK in risks or len(risks) >= 5:
        actions.extend((CognitiveIdentityAction.REQUIRE_HUMAN_REVIEW, CognitiveIdentityAction.LOCK_IDENTITY_STATE))
    return _dedupe(tuple(actions))


def evaluate_cognitive_identity(
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
    strategy_dna: Any = None,
    input_data: CognitiveIdentityInput | None = None,
) -> CognitiveIdentityResult:
    """Evaluate AGIcore cognitive identity using local deterministic heuristics."""

    if input_data is not None:
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
        strategy_dna = input_data.strategy_dna

    risks = detect_cognitive_identity_risks(
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
        strategy_dna=strategy_dna,
    )
    score_breakdown = compute_cognitive_identity_score(
        cognitive_continuity=cognitive_continuity,
        cognitive_policy=cognitive_policy,
        cognitive_governance=cognitive_governance,
        recursive_world_model=recursive_world_model,
        collective_consensus=collective_consensus,
        intent_alignment=intent_alignment,
        strategic_timeline_analysis=strategic_timeline_analysis,
        strategy_dna=strategy_dna,
        risks=risks,
    )
    identity_score = _average(tuple(score_breakdown.__dict__.values()))
    state = _select_state(risks)
    mode = _select_mode(state, risks)
    invariants = build_cognitive_invariants(risks=risks, strategy_dna=strategy_dna)
    profile = build_cognitive_identity_profile(risks=risks, identity_score=identity_score, strategy_dna=strategy_dna)
    actions = _build_actions(risks)
    recommendations = generate_cognitive_identity_recommendations(risks=risks, state=state)
    summary = (
        "Cognitive identity stable and aligned."
        if not risks
        else f"Cognitive identity requires controls for {len(risks)} detected risk(s)."
    )
    events = (
        CognitiveIdentityEvent(
            state=state,
            mode=mode,
            message=summary,
            timestamp=datetime.now(UTC),
        ),
    )

    return CognitiveIdentityResult(
        state=state,
        mode=mode,
        identity_score=identity_score,
        score_breakdown=score_breakdown,
        profile=profile,
        invariants=invariants,
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


def render_cognitive_identity_markdown(result: CognitiveIdentityResult) -> str:
    """Render a concise Markdown report for cognitive identity."""

    invariant_lines = "\n".join(
        f"- {invariant.name}: {invariant.score}/100, protected={invariant.protected}"
        for invariant in result.invariants
    )
    profile = result.profile
    return "\n".join(
        [
            "# Cognitive Identity State",
            f"- State: {result.state.value}",
            f"- Mode: {result.mode.value}",
            "",
            "## Identity Score",
            f"- Score: {result.identity_score}/100",
            "",
            "## Identity Profile",
            f"- Profile: {profile.profile_name}",
            f"- Strategy: {profile.strategy_name or 'unspecified'}",
            f"- Autonomy limited: {profile.autonomy_limited}",
            f"- Locked: {profile.locked}",
            "",
            "## Core Invariants",
            invariant_lines or "- None",
            "",
            "## Identity Risks",
            _render_items(result.risks),
            "",
            "## Actions",
            _render_items(result.actions),
            "",
            "## Recommendations",
            _render_items(result.recommendations),
            "",
            "## AGIcore Cognitive Identity Outlook",
            result.summary,
        ]
    )


__all__ = [
    "build_cognitive_identity_profile",
    "build_cognitive_invariants",
    "compute_cognitive_identity_score",
    "detect_cognitive_identity_risks",
    "evaluate_cognitive_identity",
    "generate_cognitive_identity_recommendations",
    "render_cognitive_identity_markdown",
]
