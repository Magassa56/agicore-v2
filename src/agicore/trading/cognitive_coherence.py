"""Offline Autonomous Cognitive Coherence Engine for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime
from statistics import mean
from typing import Any

from .cognitive_alignment_models import CognitiveAlignmentRisk, CognitiveAlignmentState
from .cognitive_coherence_models import (
    CognitiveCoherenceAction,
    CognitiveCoherenceEvent,
    CognitiveCoherenceInput,
    CognitiveCoherenceMode,
    CognitiveCoherenceRecommendation,
    CognitiveCoherenceResult,
    CognitiveCoherenceRisk,
    CognitiveCoherenceScore,
    CognitiveCoherenceState,
    CoherenceAxis,
    CoherenceMatrix,
    ReasoningChain,
)
from .cognitive_governance_models import CognitiveGovernanceDecision, CognitiveGovernanceMode
from .cognitive_identity_models import CognitiveIdentityState
from .cognitive_policy_models import CognitivePolicyMode, CognitivePolicyRisk
from .cognitive_stability_models import CognitiveStabilityState
from .collective_consensus_models import ConsensusDecision, ConsensusMode, ConsensusRisk
from .global_orchestrator_models import OrchestratorDecision, OrchestratorMode
from .intent_integrity_models import IntentIntegrityRisk, IntentIntegrityState
from .multi_timeline_simulation_models import TimelineDecision, TimelineOutcome, TimelineRisk
from .recursive_world_model_models import WorldModelDecision, WorldModelRisk
from .scenario_forecast_models import ForecastDecision, ForecastScenarioType
from .self_reflection_audit_models import CognitiveAuditRisk, ReflectionState
from .strategic_arbitration_models import ArbitrationDecision, ArbitrationMode, ArbitrationSeverity


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


def detect_cognitive_coherence_risks(
    cognitive_alignment: Any = None,
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
    scenario_forecast: Any = None,
    multi_timeline: Any = None,
    strategic_arbitration: Any = None,
) -> tuple[CognitiveCoherenceRisk, ...]:
    """Detect coherence risks across reasoning, simulations and decisions."""

    risks: list[CognitiveCoherenceRisk] = []

    if (
        _get(self_reflection_audit, "state") in (ReflectionState.CONTRADICTORY_REFLECTION, ReflectionState.CRITICAL_REVIEW)
        or _has(_get(self_reflection_audit, "risks", ()), CognitiveAuditRisk.STRATEGIC_SELF_CONTRADICTION)
        or _has(_get(recursive_world_model, "risks", ()), WorldModelRisk.CAUSAL_CONTRADICTION)
    ):
        risks.append(CognitiveCoherenceRisk.LOGICAL_CONTRADICTION)

    audit_trail = _get(self_reflection_audit, "audit_trail")
    if (
        _get(self_reflection_audit, "reflection_quality_score", 80) < 55
        or _get(self_reflection_audit, "state") in (ReflectionState.AUDIT_REQUIRED, ReflectionState.DEGRADED_REFLECTION)
        or _has(_get(self_reflection_audit, "risks", ()), CognitiveAuditRisk.INCOMPLETE_TRACEABILITY)
        or _get(audit_trail, "trace_complete", True) is False
    ):
        risks.append(CognitiveCoherenceRisk.REASONING_CHAIN_BREAK)

    arbitration_decision = _get(strategic_arbitration, "decision")
    consensus_decision = _get(collective_consensus, "decision")
    orchestrator_decision = _get(global_orchestrator, "decision")
    if (
        arbitration_decision in (ArbitrationDecision.STOP_EXECUTION, ArbitrationDecision.EMERGENCY_LOCKDOWN)
        and consensus_decision == ConsensusDecision.APPROVE_COLLECTIVE_DECISION
        or consensus_decision in (ConsensusDecision.NO_CONSENSUS, ConsensusDecision.EMERGENCY_HALT)
        and orchestrator_decision == OrchestratorDecision.CONTINUE_COORDINATED_OPERATION
        or _get(strategic_arbitration, "severity") == ArbitrationSeverity.CRITICAL
        and orchestrator_decision == OrchestratorDecision.CONTINUE_COORDINATED_OPERATION
    ):
        risks.append(CognitiveCoherenceRisk.DECISION_SEQUENCE_CONFLICT)

    if (
        _get(recursive_world_model, "decision")
        in (
            WorldModelDecision.REBUILD_CAUSAL_GRAPH,
            WorldModelDecision.ENTER_WORLD_MODEL_SAFE_MODE,
            WorldModelDecision.FREEZE_RECURSIVE_UPDATES,
        )
        and orchestrator_decision == OrchestratorDecision.CONTINUE_COORDINATED_OPERATION
        or _has(_get(recursive_world_model, "risks", ()), WorldModelRisk.PLANNING_ACTION_MISMATCH)
        or _has(_get(recursive_world_model, "risks", ()), WorldModelRisk.ORCHESTRATION_DESYNC)
    ):
        risks.append(CognitiveCoherenceRisk.WORLD_MODEL_ACTION_MISMATCH)

    critical_forecasts = _get(scenario_forecast, "critical_scenarios", ())
    timeline_risks = _get(multi_timeline, "risks", ())
    if (
        _get(scenario_forecast, "decision")
        in (ForecastDecision.ENTER_FORECAST_SAFE_MODE, ForecastDecision.REBUILD_FORECAST_MODEL, ForecastDecision.AVOID_HIGH_RISK_SCENARIO)
        and _get(multi_timeline, "decision") == TimelineDecision.SELECT_STABLE_TIMELINE
        or _has(critical_forecasts, ForecastScenarioType.EMERGENCY_LOCKDOWN_PATH)
        and _get(multi_timeline, "overall_survivability_score", 80) > 70
        or _has(timeline_risks, TimelineRisk.DIVERGENCE_RISK)
    ):
        risks.append(CognitiveCoherenceRisk.TIMELINE_FORECAST_CONFLICT)

    if (
        _get(cognitive_policy, "mode") in (CognitivePolicyMode.POLICY_RESTRICTED, CognitivePolicyMode.POLICY_SAFE_MODE, CognitivePolicyMode.POLICY_LOCKED)
        and _get(cognitive_governance, "decision") == CognitiveGovernanceDecision.APPROVE_COGNITIVE_OPERATION
        or _has(_get(cognitive_policy, "risks", ()), CognitivePolicyRisk.POLICY_CONFLICT)
        or _get(cognitive_governance, "mode") == CognitiveGovernanceMode.LOCKED_GOVERNANCE
        and _get(cognitive_policy, "mode") == CognitivePolicyMode.POLICY_NORMAL
    ):
        risks.append(CognitiveCoherenceRisk.POLICY_REASONING_CONFLICT)

    if (
        _get(cognitive_alignment, "state")
        in (
            CognitiveAlignmentState.PARTIAL_MISALIGNMENT,
            CognitiveAlignmentState.STRATEGIC_MISALIGNMENT,
            CognitiveAlignmentState.POLICY_MISALIGNMENT,
            CognitiveAlignmentState.INTENT_MISALIGNMENT,
            CognitiveAlignmentState.SYSTEMIC_MISALIGNMENT,
            CognitiveAlignmentState.ALIGNMENT_LOCKED,
        )
        or _get(cognitive_alignment, "cognitive_alignment_score", 80) < 60
        or _has(_get(cognitive_alignment, "risks", ()), CognitiveAlignmentRisk.SYSTEMIC_ALIGNMENT_COLLAPSE)
        or _get(intent_integrity, "state") in (IntentIntegrityState.INTENT_CORRUPTED, IntentIntegrityState.INTENT_LOCKED)
        or _get(cognitive_identity, "state") in (CognitiveIdentityState.IDENTITY_CONFLICTED, CognitiveIdentityState.IDENTITY_LOCKED)
    ):
        risks.append(CognitiveCoherenceRisk.ALIGNMENT_COHERENCE_BREAK)

    if (
        _get(collective_consensus, "mode") in (ConsensusMode.DEGRADED_CONSENSUS, ConsensusMode.CONSENSUS_COLLAPSE)
        or _get(collective_consensus, "collective_confidence_score", 80) < 60
        or _has(_get(collective_consensus, "risks", ()), ConsensusRisk.CONSENSUS_FRAGMENTATION)
    ):
        risks.append(CognitiveCoherenceRisk.CONSENSUS_COHERENCE_BREAK)

    timeline_states = _get(multi_timeline, "timeline_states", ())
    has_collapsing_timeline = any(_get(state, "outcome") in (TimelineOutcome.COLLAPSING, TimelineOutcome.EMERGENCY_STOP) for state in timeline_states)
    if (
        _get(strategic_arbitration, "mode") in (ArbitrationMode.SURVIVAL_MODE, ArbitrationMode.EMERGENCY_LOCKDOWN)
        or _get(strategic_arbitration, "confidence_score", 80) < 55
        or has_collapsing_timeline
        or _get(scenario_forecast, "forecast_stability_score", 80) < 55
    ):
        risks.append(CognitiveCoherenceRisk.STRATEGIC_CONCLUSION_INSTABILITY)

    if (
        len(risks) >= 6
        or _get(cognitive_stability, "state") in (CognitiveStabilityState.CRITICAL, CognitiveStabilityState.COLLAPSING)
        or _get(global_orchestrator, "mode") in (OrchestratorMode.EMERGENCY_ORCHESTRATION, OrchestratorMode.SURVIVAL_ORCHESTRATION)
        or _has(_get(intent_integrity, "risks", ()), IntentIntegrityRisk.INTENT_COLLAPSE_RISK)
    ):
        risks.append(CognitiveCoherenceRisk.SYSTEMIC_COHERENCE_COLLAPSE)

    return _dedupe(tuple(risks))


def compute_cognitive_coherence_score(
    cognitive_alignment: Any = None,
    intent_integrity: Any = None,
    cognitive_identity: Any = None,
    cognitive_continuity: Any = None,
    cognitive_policy: Any = None,
    cognitive_governance: Any = None,
    self_reflection_audit: Any = None,
    recursive_world_model: Any = None,
    global_orchestrator: Any = None,
    collective_consensus: Any = None,
    scenario_forecast: Any = None,
    multi_timeline: Any = None,
    strategic_arbitration: Any = None,
    risks: tuple[CognitiveCoherenceRisk, ...] = (),
) -> CognitiveCoherenceScore:
    """Compute coherence components normalized to 0..100."""

    values = {
        "logical": _average((_get(self_reflection_audit, "reflection_quality_score", 80), _get(recursive_world_model, "world_model_coherence_score", 80))),
        "reasoning": _average((_get(self_reflection_audit, "reflection_quality_score", 80), _get(cognitive_continuity, "continuity_score", 80))),
        "decision": _average((_get(strategic_arbitration, "confidence_score", 80), _get(global_orchestrator, "confidence_score", 80))),
        "world": _average((_get(recursive_world_model, "world_model_coherence_score", 80), _get(global_orchestrator, "confidence_score", 80))),
        "timeline": _average((_get(scenario_forecast, "forecast_stability_score", 80), _get(multi_timeline, "overall_survivability_score", 80))),
        "policy": _average((_get(cognitive_policy, "cognitive_policy_score", 80), _get(cognitive_governance, "governance_score", 80))),
        "alignment": _average((_get(cognitive_alignment, "cognitive_alignment_score", 80), _get(intent_integrity, "intent_integrity_score", 80), _get(cognitive_identity, "identity_score", 80))),
        "consensus": _clamp(_get(collective_consensus, "collective_confidence_score", 80)),
        "strategic": _average((_get(strategic_arbitration, "confidence_score", 80), _get(scenario_forecast, "forecast_stability_score", 80))),
        "systemic": _average(
            (
                _get(cognitive_alignment, "cognitive_alignment_score", 80),
                _get(cognitive_continuity, "continuity_score", 80),
                _get(cognitive_policy, "cognitive_policy_score", 80),
                _get(collective_consensus, "collective_confidence_score", 80),
            )
        ),
    }
    penalties = {
        CognitiveCoherenceRisk.LOGICAL_CONTRADICTION: ("logical", 30),
        CognitiveCoherenceRisk.REASONING_CHAIN_BREAK: ("reasoning", 30),
        CognitiveCoherenceRisk.DECISION_SEQUENCE_CONFLICT: ("decision", 30),
        CognitiveCoherenceRisk.WORLD_MODEL_ACTION_MISMATCH: ("world", 30),
        CognitiveCoherenceRisk.TIMELINE_FORECAST_CONFLICT: ("timeline", 30),
        CognitiveCoherenceRisk.POLICY_REASONING_CONFLICT: ("policy", 30),
        CognitiveCoherenceRisk.ALIGNMENT_COHERENCE_BREAK: ("alignment", 30),
        CognitiveCoherenceRisk.CONSENSUS_COHERENCE_BREAK: ("consensus", 30),
        CognitiveCoherenceRisk.STRATEGIC_CONCLUSION_INSTABILITY: ("strategic", 30),
        CognitiveCoherenceRisk.SYSTEMIC_COHERENCE_COLLAPSE: ("all", 20),
    }
    for risk in risks:
        target, penalty = penalties[risk]
        if target == "all":
            values = {key: value - penalty for key, value in values.items()}
        else:
            values[target] -= penalty

    return CognitiveCoherenceScore(
        logical_consistency_score=_clamp(values["logical"]),
        reasoning_chain_score=_clamp(values["reasoning"]),
        decision_sequence_score=_clamp(values["decision"]),
        world_model_action_score=_clamp(values["world"]),
        timeline_forecast_score=_clamp(values["timeline"]),
        policy_reasoning_score=_clamp(values["policy"]),
        alignment_coherence_score=_clamp(values["alignment"]),
        consensus_coherence_score=_clamp(values["consensus"]),
        strategic_conclusion_score=_clamp(values["strategic"]),
        systemic_coherence_score=_clamp(values["systemic"]),
    )


def build_reasoning_chains(
    score_breakdown: CognitiveCoherenceScore,
    risks: tuple[CognitiveCoherenceRisk, ...] = (),
) -> tuple[ReasoningChain, ...]:
    """Build explainable reasoning chains."""

    specs = (
        (
            "alignment_intent_identity",
            ("cognitive_alignment", "intent_integrity", "cognitive_identity"),
            score_breakdown.alignment_coherence_score,
            CognitiveCoherenceRisk.ALIGNMENT_COHERENCE_BREAK,
        ),
        (
            "policy_governance_reasoning",
            ("cognitive_policy", "cognitive_governance", "self_reflection_audit"),
            score_breakdown.policy_reasoning_score,
            CognitiveCoherenceRisk.POLICY_REASONING_CONFLICT,
        ),
        (
            "world_model_action",
            ("recursive_world_model", "global_orchestrator", "action_route"),
            score_breakdown.world_model_action_score,
            CognitiveCoherenceRisk.WORLD_MODEL_ACTION_MISMATCH,
        ),
        (
            "forecast_timeline_strategy",
            ("scenario_forecast", "multi_timeline", "strategic_arbitration"),
            score_breakdown.timeline_forecast_score,
            CognitiveCoherenceRisk.TIMELINE_FORECAST_CONFLICT,
        ),
    )
    chains: list[ReasoningChain] = []
    for name, steps, score, risk in specs:
        complete = score >= 60 and risk not in risks and CognitiveCoherenceRisk.REASONING_CHAIN_BREAK not in risks
        broken_step = None if complete else steps[-1]
        chains.append(ReasoningChain(name=name, steps=steps, score=score, complete=complete, broken_step=broken_step))
    return tuple(chains)


def build_coherence_axes(
    score_breakdown: CognitiveCoherenceScore,
    risks: tuple[CognitiveCoherenceRisk, ...] = (),
) -> tuple[CoherenceAxis, ...]:
    """Build coherence axes from component scores and detected risks."""

    specs = (
        ("logical_consistency", score_breakdown.logical_consistency_score, CognitiveCoherenceRisk.LOGICAL_CONTRADICTION),
        ("reasoning_chain", score_breakdown.reasoning_chain_score, CognitiveCoherenceRisk.REASONING_CHAIN_BREAK),
        ("decision_sequence", score_breakdown.decision_sequence_score, CognitiveCoherenceRisk.DECISION_SEQUENCE_CONFLICT),
        ("world_model_action", score_breakdown.world_model_action_score, CognitiveCoherenceRisk.WORLD_MODEL_ACTION_MISMATCH),
        ("timeline_forecast", score_breakdown.timeline_forecast_score, CognitiveCoherenceRisk.TIMELINE_FORECAST_CONFLICT),
        ("policy_reasoning", score_breakdown.policy_reasoning_score, CognitiveCoherenceRisk.POLICY_REASONING_CONFLICT),
        ("alignment", score_breakdown.alignment_coherence_score, CognitiveCoherenceRisk.ALIGNMENT_COHERENCE_BREAK),
        ("consensus", score_breakdown.consensus_coherence_score, CognitiveCoherenceRisk.CONSENSUS_COHERENCE_BREAK),
        ("strategic_conclusion", score_breakdown.strategic_conclusion_score, CognitiveCoherenceRisk.STRATEGIC_CONCLUSION_INSTABILITY),
        ("systemic", score_breakdown.systemic_coherence_score, CognitiveCoherenceRisk.SYSTEMIC_COHERENCE_COLLAPSE),
    )
    axes: list[CoherenceAxis] = []
    for name, score, risk in specs:
        coherent = score >= 60 and risk not in risks
        axes.append(
            CoherenceAxis(
                name=name,
                score=score,
                coherent=coherent,
                risk=risk if not coherent else None,
                evidence="coherent" if coherent else f"{risk.value} requires validation",
            )
        )
    return tuple(axes)


def build_coherence_matrix(
    axes: tuple[CoherenceAxis, ...],
    reasoning_chains: tuple[ReasoningChain, ...],
    risks: tuple[CognitiveCoherenceRisk, ...] = (),
) -> CoherenceMatrix:
    """Build a global coherence matrix."""

    broken_axes = tuple(axis.name for axis in axes if not axis.coherent)
    weakest_axis = min(axes, key=lambda axis: axis.score).name if axes else None
    return CoherenceMatrix(
        axes=axes,
        reasoning_chains=reasoning_chains,
        global_score=_average(tuple(axis.score for axis in axes)),
        weakest_axis=weakest_axis,
        broken_axes=broken_axes,
        locked=CognitiveCoherenceRisk.SYSTEMIC_COHERENCE_COLLAPSE in risks,
        autonomy_reduced=bool(risks),
    )


def generate_cognitive_coherence_recommendations(
    risks: tuple[CognitiveCoherenceRisk, ...] = (),
    state: CognitiveCoherenceState = CognitiveCoherenceState.COHERENT,
) -> tuple[CognitiveCoherenceRecommendation, ...]:
    """Generate ordered cognitive coherence recommendations."""

    recommendations: list[CognitiveCoherenceRecommendation] = [CognitiveCoherenceRecommendation.PRESERVE_LOGICAL_INVARIANTS]
    if CognitiveCoherenceRisk.REASONING_CHAIN_BREAK in risks or CognitiveCoherenceRisk.LOGICAL_CONTRADICTION in risks:
        recommendations.append(CognitiveCoherenceRecommendation.EXTEND_REASONING_TRACE)
    if CognitiveCoherenceRisk.DECISION_SEQUENCE_CONFLICT in risks:
        recommendations.append(CognitiveCoherenceRecommendation.VALIDATE_DECISION_CHAIN)
    if CognitiveCoherenceRisk.WORLD_MODEL_ACTION_MISMATCH in risks:
        recommendations.append(CognitiveCoherenceRecommendation.RECHECK_WORLD_MODEL_ACTION_LINK)
    if CognitiveCoherenceRisk.TIMELINE_FORECAST_CONFLICT in risks:
        recommendations.append(CognitiveCoherenceRecommendation.RECONCILE_FORECAST_TIMELINES)
    if CognitiveCoherenceRisk.STRATEGIC_CONCLUSION_INSTABILITY in risks:
        recommendations.append(CognitiveCoherenceRecommendation.REPAIR_STRATEGIC_CONCLUSIONS)
    if risks:
        recommendations.append(CognitiveCoherenceRecommendation.KEEP_AUTONOMY_REDUCED)
    if state in (
        CognitiveCoherenceState.LOGICAL_CONFLICT,
        CognitiveCoherenceState.STRATEGIC_INCOHERENCE,
        CognitiveCoherenceState.SYSTEMIC_INCOHERENCE,
        CognitiveCoherenceState.COHERENCE_AT_RISK,
        CognitiveCoherenceState.COHERENCE_LOCKED,
    ):
        recommendations.append(CognitiveCoherenceRecommendation.REQUIRE_SUPERVISION)
    recommendations.append(CognitiveCoherenceRecommendation.UPDATE_COHERENCE_SNAPSHOT)
    if not risks:
        recommendations.append(CognitiveCoherenceRecommendation.CONTINUE_COHERENCE_MONITORING)
    return _dedupe(tuple(recommendations))


def _select_state(risks: tuple[CognitiveCoherenceRisk, ...]) -> CognitiveCoherenceState:
    if CognitiveCoherenceRisk.SYSTEMIC_COHERENCE_COLLAPSE in risks:
        return CognitiveCoherenceState.COHERENCE_LOCKED
    if len(risks) >= 5:
        return CognitiveCoherenceState.COHERENCE_AT_RISK
    if CognitiveCoherenceRisk.LOGICAL_CONTRADICTION in risks or CognitiveCoherenceRisk.REASONING_CHAIN_BREAK in risks:
        return CognitiveCoherenceState.LOGICAL_CONFLICT
    if (
        CognitiveCoherenceRisk.TIMELINE_FORECAST_CONFLICT in risks
        or CognitiveCoherenceRisk.STRATEGIC_CONCLUSION_INSTABILITY in risks
    ):
        return CognitiveCoherenceState.STRATEGIC_INCOHERENCE
    if (
        CognitiveCoherenceRisk.ALIGNMENT_COHERENCE_BREAK in risks
        or CognitiveCoherenceRisk.CONSENSUS_COHERENCE_BREAK in risks
        or CognitiveCoherenceRisk.POLICY_REASONING_CONFLICT in risks
    ):
        return CognitiveCoherenceState.SYSTEMIC_INCOHERENCE
    if risks:
        return CognitiveCoherenceState.PARTIAL_INCOHERENCE
    return CognitiveCoherenceState.COHERENT


def _select_mode(state: CognitiveCoherenceState, risks: tuple[CognitiveCoherenceRisk, ...]) -> CognitiveCoherenceMode:
    if state == CognitiveCoherenceState.COHERENCE_LOCKED:
        return CognitiveCoherenceMode.LOCKED_COHERENCE_MODE
    if state in (CognitiveCoherenceState.COHERENCE_AT_RISK, CognitiveCoherenceState.SYSTEMIC_INCOHERENCE):
        return CognitiveCoherenceMode.SAFE_COHERENCE_MODE
    if CognitiveCoherenceRisk.LOGICAL_CONTRADICTION in risks or CognitiveCoherenceRisk.REASONING_CHAIN_BREAK in risks:
        return CognitiveCoherenceMode.LOGICAL_VALIDATION
    if CognitiveCoherenceRisk.WORLD_MODEL_ACTION_MISMATCH in risks:
        return CognitiveCoherenceMode.WORLD_MODEL_VALIDATION
    if CognitiveCoherenceRisk.TIMELINE_FORECAST_CONFLICT in risks:
        return CognitiveCoherenceMode.TIMELINE_VALIDATION
    if CognitiveCoherenceRisk.STRATEGIC_CONCLUSION_INSTABILITY in risks:
        return CognitiveCoherenceMode.STRATEGIC_VALIDATION
    if risks:
        return CognitiveCoherenceMode.COHERENCE_MONITORING
    return CognitiveCoherenceMode.NORMAL_COHERENCE


def _build_actions(risks: tuple[CognitiveCoherenceRisk, ...]) -> tuple[CognitiveCoherenceAction, ...]:
    actions: list[CognitiveCoherenceAction] = [CognitiveCoherenceAction.PRESERVE_COHERENCE_STATE]
    if CognitiveCoherenceRisk.REASONING_CHAIN_BREAK in risks or CognitiveCoherenceRisk.LOGICAL_CONTRADICTION in risks:
        actions.append(CognitiveCoherenceAction.REBUILD_REASONING_CHAIN)
    if CognitiveCoherenceRisk.DECISION_SEQUENCE_CONFLICT in risks:
        actions.append(CognitiveCoherenceAction.RECHECK_DECISION_SEQUENCE)
    if CognitiveCoherenceRisk.WORLD_MODEL_ACTION_MISMATCH in risks:
        actions.append(CognitiveCoherenceAction.ALIGN_WORLD_MODEL_ACTIONS)
    if CognitiveCoherenceRisk.TIMELINE_FORECAST_CONFLICT in risks:
        actions.append(CognitiveCoherenceAction.RECONCILE_TIMELINE_FORECAST)
    if CognitiveCoherenceRisk.POLICY_REASONING_CONFLICT in risks:
        actions.append(CognitiveCoherenceAction.REPAIR_POLICY_REASONING)
    if CognitiveCoherenceRisk.CONSENSUS_COHERENCE_BREAK in risks:
        actions.append(CognitiveCoherenceAction.REBUILD_CONSENSUS_COHERENCE)
    if risks:
        actions.append(CognitiveCoherenceAction.REDUCE_AUTONOMY)
    if CognitiveCoherenceRisk.SYSTEMIC_COHERENCE_COLLAPSE in risks:
        actions.extend((CognitiveCoherenceAction.REQUIRE_HUMAN_REVIEW, CognitiveCoherenceAction.LOCK_COHERENCE_STATE))
    return _dedupe(tuple(actions))


def evaluate_cognitive_coherence(
    cognitive_alignment: Any = None,
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
    scenario_forecast: Any = None,
    multi_timeline: Any = None,
    strategic_arbitration: Any = None,
    input_data: CognitiveCoherenceInput | None = None,
) -> CognitiveCoherenceResult:
    """Evaluate cognitive coherence without external systems."""

    if input_data is not None:
        cognitive_alignment = input_data.cognitive_alignment
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
        scenario_forecast = input_data.scenario_forecast
        multi_timeline = input_data.multi_timeline
        strategic_arbitration = input_data.strategic_arbitration

    risks = detect_cognitive_coherence_risks(
        cognitive_alignment=cognitive_alignment,
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
        scenario_forecast=scenario_forecast,
        multi_timeline=multi_timeline,
        strategic_arbitration=strategic_arbitration,
    )
    score_breakdown = compute_cognitive_coherence_score(
        cognitive_alignment=cognitive_alignment,
        intent_integrity=intent_integrity,
        cognitive_identity=cognitive_identity,
        cognitive_continuity=cognitive_continuity,
        cognitive_policy=cognitive_policy,
        cognitive_governance=cognitive_governance,
        self_reflection_audit=self_reflection_audit,
        recursive_world_model=recursive_world_model,
        global_orchestrator=global_orchestrator,
        collective_consensus=collective_consensus,
        scenario_forecast=scenario_forecast,
        multi_timeline=multi_timeline,
        strategic_arbitration=strategic_arbitration,
        risks=risks,
    )
    reasoning_chains = build_reasoning_chains(score_breakdown=score_breakdown, risks=risks)
    axes = build_coherence_axes(score_breakdown=score_breakdown, risks=risks)
    matrix = build_coherence_matrix(axes=axes, reasoning_chains=reasoning_chains, risks=risks)
    state = _select_state(risks)
    mode = _select_mode(state, risks)
    actions = _build_actions(risks)
    recommendations = generate_cognitive_coherence_recommendations(risks=risks, state=state)
    summary = "Cognitive coherence preserved." if not risks else f"Cognitive coherence requires validation for {len(risks)} risk(s)."
    events = (
        CognitiveCoherenceEvent(
            state=state,
            mode=mode,
            message=summary,
            timestamp=datetime.now(UTC),
        ),
    )
    return CognitiveCoherenceResult(
        state=state,
        mode=mode,
        cognitive_coherence_score=matrix.global_score,
        score_breakdown=score_breakdown,
        reasoning_chains=reasoning_chains,
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


def render_cognitive_coherence_markdown(result: CognitiveCoherenceResult) -> str:
    """Render a Markdown report for cognitive coherence."""

    chain_lines = "\n".join(
        f"- {chain.name}: {chain.score}/100, complete={chain.complete}"
        for chain in result.reasoning_chains
    )
    axis_lines = "\n".join(f"- {axis.name}: {axis.score}/100, coherent={axis.coherent}" for axis in result.axes)
    matrix = result.matrix
    return "\n".join(
        [
            "# Cognitive Coherence State",
            f"- State: {result.state.value}",
            f"- Mode: {result.mode.value}",
            "",
            "## Coherence Score",
            f"- Score: {result.cognitive_coherence_score}/100",
            "",
            "## Reasoning Chains",
            chain_lines or "- None",
            "",
            "## Coherence Axes",
            axis_lines or "- None",
            "",
            "## Coherence Matrix",
            f"- Global score: {matrix.global_score}/100",
            f"- Weakest axis: {matrix.weakest_axis or 'none'}",
            f"- Broken axes: {', '.join(matrix.broken_axes) if matrix.broken_axes else 'none'}",
            f"- Autonomy reduced: {matrix.autonomy_reduced}",
            f"- Locked: {matrix.locked}",
            "",
            "## Coherence Risks",
            _render_items(result.risks),
            "",
            "## Actions",
            _render_items(result.actions),
            "",
            "## Recommendations",
            _render_items(result.recommendations),
            "",
            "## AGIcore Cognitive Coherence Outlook",
            result.summary,
        ]
    )


__all__ = [
    "build_coherence_axes",
    "build_coherence_matrix",
    "build_reasoning_chains",
    "compute_cognitive_coherence_score",
    "detect_cognitive_coherence_risks",
    "evaluate_cognitive_coherence",
    "generate_cognitive_coherence_recommendations",
    "render_cognitive_coherence_markdown",
]
