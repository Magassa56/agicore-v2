from __future__ import annotations

from types import SimpleNamespace

from agicore.trading.cognitive_alignment_models import CognitiveAlignmentRisk, CognitiveAlignmentState
from agicore.trading.cognitive_coherence import (
    build_coherence_axes,
    build_coherence_matrix,
    build_reasoning_chains,
    compute_cognitive_coherence_score,
    detect_cognitive_coherence_risks,
    evaluate_cognitive_coherence,
    generate_cognitive_coherence_recommendations,
    render_cognitive_coherence_markdown,
)
from agicore.trading.cognitive_coherence_models import (
    CognitiveCoherenceAction,
    CognitiveCoherenceMode,
    CognitiveCoherenceRecommendation,
    CognitiveCoherenceRisk,
    CognitiveCoherenceState,
)
from agicore.trading.cognitive_governance_models import CognitiveGovernanceDecision, CognitiveGovernanceMode
from agicore.trading.cognitive_identity_models import CognitiveIdentityState
from agicore.trading.cognitive_policy_models import CognitivePolicyMode, CognitivePolicyRisk
from agicore.trading.cognitive_stability_models import CognitiveStabilityState
from agicore.trading.collective_consensus_models import ConsensusDecision, ConsensusMode, ConsensusRisk
from agicore.trading.global_orchestrator_models import OrchestratorDecision, OrchestratorMode
from agicore.trading.intent_integrity_models import IntentIntegrityRisk, IntentIntegrityState
from agicore.trading.multi_timeline_simulation_models import TimelineDecision, TimelineOutcome, TimelineRisk
from agicore.trading.recursive_world_model_models import WorldModelDecision, WorldModelRisk
from agicore.trading.scenario_forecast_models import ForecastDecision, ForecastScenarioType
from agicore.trading.self_reflection_audit_models import CognitiveAuditRisk, ReflectionState
from agicore.trading.strategic_arbitration_models import ArbitrationDecision, ArbitrationMode, ArbitrationSeverity


def _alignment(state=CognitiveAlignmentState.FULLY_ALIGNED, score=84, risks=()):
    return SimpleNamespace(state=state, cognitive_alignment_score=score, risks=risks)


def _intent(state=IntentIntegrityState.INTENT_INTACT, score=84, risks=()):
    return SimpleNamespace(state=state, intent_integrity_score=score, risks=risks)


def _identity(state=CognitiveIdentityState.IDENTITY_STABLE, score=84):
    return SimpleNamespace(state=state, identity_score=score)


def _continuity(score=84):
    return SimpleNamespace(continuity_score=score)


def _policy(mode=CognitivePolicyMode.POLICY_NORMAL, score=84, risks=()):
    return SimpleNamespace(mode=mode, cognitive_policy_score=score, risks=risks)


def _governance(mode=CognitiveGovernanceMode.NORMAL_GOVERNANCE, decision=CognitiveGovernanceDecision.APPROVE_COGNITIVE_OPERATION, score=84):
    return SimpleNamespace(mode=mode, decision=decision, governance_score=score)


def _audit(state=ReflectionState.CLEAR_REFLECTION, score=84, risks=(), trace_complete=True):
    return SimpleNamespace(
        state=state,
        reflection_quality_score=score,
        risks=risks,
        audit_trail=SimpleNamespace(trace_complete=trace_complete),
    )


def _world(score=84, decision=WorldModelDecision.MAINTAIN_WORLD_MODEL, risks=()):
    return SimpleNamespace(world_model_coherence_score=score, decision=decision, risks=risks)


def _orchestrator(mode=OrchestratorMode.NORMAL_OPERATION, decision=OrchestratorDecision.CONTINUE_COORDINATED_OPERATION, score=84):
    return SimpleNamespace(mode=mode, decision=decision, confidence_score=score)


def _consensus(decision=ConsensusDecision.APPROVE_COLLECTIVE_DECISION, mode=ConsensusMode.NORMAL_CONSENSUS, score=84, risks=()):
    return SimpleNamespace(decision=decision, mode=mode, collective_confidence_score=score, risks=risks)


def _forecast(decision=ForecastDecision.CONTINUE_CURRENT_PATH, score=84, critical=()):
    return SimpleNamespace(decision=decision, forecast_stability_score=score, critical_scenarios=critical)


def _timeline(decision=TimelineDecision.SELECT_STABLE_TIMELINE, score=84, risks=(), outcome=TimelineOutcome.STABLE):
    return SimpleNamespace(
        decision=decision,
        overall_survivability_score=score,
        risks=risks,
        timeline_states=(SimpleNamespace(outcome=outcome),),
    )


def _arbitration(decision=ArbitrationDecision.CONTINUE_OPERATION, mode=ArbitrationMode.NORMAL_OPERATION, severity=ArbitrationSeverity.LOW, score=84):
    return SimpleNamespace(decision=decision, mode=mode, severity=severity, confidence_score=score)


def test_coherent_when_all_reasoning_layers_are_consistent() -> None:
    result = evaluate_cognitive_coherence(
        cognitive_alignment=_alignment(),
        intent_integrity=_intent(),
        cognitive_identity=_identity(),
        cognitive_continuity=_continuity(),
        cognitive_policy=_policy(),
        cognitive_governance=_governance(),
        self_reflection_audit=_audit(),
        recursive_world_model=_world(),
        global_orchestrator=_orchestrator(),
        collective_consensus=_consensus(),
        scenario_forecast=_forecast(),
        multi_timeline=_timeline(),
        strategic_arbitration=_arbitration(),
    )

    assert result.state == CognitiveCoherenceState.COHERENT
    assert result.mode == CognitiveCoherenceMode.NORMAL_COHERENCE
    assert result.matrix.locked is False
    assert result.actions == (CognitiveCoherenceAction.PRESERVE_COHERENCE_STATE,)


def test_detects_logical_contradiction_and_reasoning_chain_break() -> None:
    risks = detect_cognitive_coherence_risks(
        self_reflection_audit=_audit(
            ReflectionState.CONTRADICTORY_REFLECTION,
            35,
            (CognitiveAuditRisk.STRATEGIC_SELF_CONTRADICTION, CognitiveAuditRisk.INCOMPLETE_TRACEABILITY),
            trace_complete=False,
        ),
        recursive_world_model=_world(35, risks=(WorldModelRisk.CAUSAL_CONTRADICTION,)),
    )

    assert CognitiveCoherenceRisk.LOGICAL_CONTRADICTION in risks
    assert CognitiveCoherenceRisk.REASONING_CHAIN_BREAK in risks


def test_detects_decision_sequence_conflict() -> None:
    risks = detect_cognitive_coherence_risks(
        strategic_arbitration=_arbitration(ArbitrationDecision.EMERGENCY_LOCKDOWN, severity=ArbitrationSeverity.CRITICAL),
        collective_consensus=_consensus(ConsensusDecision.APPROVE_COLLECTIVE_DECISION),
        global_orchestrator=_orchestrator(decision=OrchestratorDecision.CONTINUE_COORDINATED_OPERATION),
    )

    assert CognitiveCoherenceRisk.DECISION_SEQUENCE_CONFLICT in risks


def test_detects_world_model_action_mismatch() -> None:
    risks = detect_cognitive_coherence_risks(
        recursive_world_model=_world(
            35,
            WorldModelDecision.REBUILD_CAUSAL_GRAPH,
            (WorldModelRisk.PLANNING_ACTION_MISMATCH,),
        ),
        global_orchestrator=_orchestrator(decision=OrchestratorDecision.CONTINUE_COORDINATED_OPERATION),
    )

    assert CognitiveCoherenceRisk.WORLD_MODEL_ACTION_MISMATCH in risks


def test_detects_timeline_forecast_conflict() -> None:
    risks = detect_cognitive_coherence_risks(
        scenario_forecast=_forecast(ForecastDecision.ENTER_FORECAST_SAFE_MODE, 35, (ForecastScenarioType.EMERGENCY_LOCKDOWN_PATH,)),
        multi_timeline=_timeline(TimelineDecision.SELECT_STABLE_TIMELINE, 85, (TimelineRisk.DIVERGENCE_RISK,)),
    )

    assert CognitiveCoherenceRisk.TIMELINE_FORECAST_CONFLICT in risks


def test_detects_policy_alignment_consensus_and_strategy_instability() -> None:
    risks = detect_cognitive_coherence_risks(
        cognitive_policy=_policy(CognitivePolicyMode.POLICY_LOCKED, 35, (CognitivePolicyRisk.POLICY_CONFLICT,)),
        cognitive_governance=_governance(CognitiveGovernanceMode.NORMAL_GOVERNANCE, CognitiveGovernanceDecision.APPROVE_COGNITIVE_OPERATION, 35),
        cognitive_alignment=_alignment(CognitiveAlignmentState.SYSTEMIC_MISALIGNMENT, 35, (CognitiveAlignmentRisk.SYSTEMIC_ALIGNMENT_COLLAPSE,)),
        collective_consensus=_consensus(ConsensusDecision.NO_CONSENSUS, ConsensusMode.CONSENSUS_COLLAPSE, 35, (ConsensusRisk.CONSENSUS_FRAGMENTATION,)),
        strategic_arbitration=_arbitration(mode=ArbitrationMode.SURVIVAL_MODE, score=35),
        scenario_forecast=_forecast(score=35),
    )

    assert CognitiveCoherenceRisk.POLICY_REASONING_CONFLICT in risks
    assert CognitiveCoherenceRisk.ALIGNMENT_COHERENCE_BREAK in risks
    assert CognitiveCoherenceRisk.CONSENSUS_COHERENCE_BREAK in risks
    assert CognitiveCoherenceRisk.STRATEGIC_CONCLUSION_INSTABILITY in risks


def test_locks_coherence_on_systemic_collapse() -> None:
    result = evaluate_cognitive_coherence(
        self_reflection_audit=_audit(ReflectionState.CONTRADICTORY_REFLECTION, 20, (CognitiveAuditRisk.INCOMPLETE_TRACEABILITY,), False),
        recursive_world_model=_world(20, WorldModelDecision.FREEZE_RECURSIVE_UPDATES, (WorldModelRisk.CAUSAL_CONTRADICTION,)),
        strategic_arbitration=_arbitration(ArbitrationDecision.EMERGENCY_LOCKDOWN, ArbitrationMode.EMERGENCY_LOCKDOWN, ArbitrationSeverity.CRITICAL, 20),
        collective_consensus=_consensus(ConsensusDecision.NO_CONSENSUS, ConsensusMode.CONSENSUS_COLLAPSE, 20),
        global_orchestrator=_orchestrator(OrchestratorMode.EMERGENCY_ORCHESTRATION, OrchestratorDecision.EMERGENCY_HALT_ROUTING, 20),
        cognitive_alignment=_alignment(CognitiveAlignmentState.ALIGNMENT_LOCKED, 20),
        cognitive_stability=SimpleNamespace(state=CognitiveStabilityState.COLLAPSING),
    )

    assert result.state == CognitiveCoherenceState.COHERENCE_LOCKED
    assert result.mode == CognitiveCoherenceMode.LOCKED_COHERENCE_MODE
    assert CognitiveCoherenceRisk.SYSTEMIC_COHERENCE_COLLAPSE in result.risks
    assert CognitiveCoherenceAction.LOCK_COHERENCE_STATE in result.actions


def test_score_penalizes_all_coherence_axes() -> None:
    score = compute_cognitive_coherence_score(
        self_reflection_audit=_audit(score=45),
        recursive_world_model=_world(score=45),
        strategic_arbitration=_arbitration(score=45),
        global_orchestrator=_orchestrator(score=45),
        scenario_forecast=_forecast(score=45),
        multi_timeline=_timeline(score=45),
        cognitive_policy=_policy(score=45),
        cognitive_governance=_governance(score=45),
        cognitive_alignment=_alignment(score=45),
        cognitive_continuity=_continuity(score=45),
        collective_consensus=_consensus(score=45),
        risks=(
            CognitiveCoherenceRisk.LOGICAL_CONTRADICTION,
            CognitiveCoherenceRisk.REASONING_CHAIN_BREAK,
            CognitiveCoherenceRisk.DECISION_SEQUENCE_CONFLICT,
            CognitiveCoherenceRisk.WORLD_MODEL_ACTION_MISMATCH,
            CognitiveCoherenceRisk.TIMELINE_FORECAST_CONFLICT,
            CognitiveCoherenceRisk.POLICY_REASONING_CONFLICT,
            CognitiveCoherenceRisk.ALIGNMENT_COHERENCE_BREAK,
            CognitiveCoherenceRisk.CONSENSUS_COHERENCE_BREAK,
            CognitiveCoherenceRisk.STRATEGIC_CONCLUSION_INSTABILITY,
            CognitiveCoherenceRisk.SYSTEMIC_COHERENCE_COLLAPSE,
        ),
    )

    assert score.logical_consistency_score == 0
    assert score.reasoning_chain_score == 0
    assert score.decision_sequence_score == 0
    assert score.consensus_coherence_score == 0


def test_reasoning_chains_axes_and_matrix_mark_breaks() -> None:
    score = compute_cognitive_coherence_score(
        cognitive_alignment=_alignment(score=45),
        risks=(CognitiveCoherenceRisk.ALIGNMENT_COHERENCE_BREAK,),
    )
    chains = build_reasoning_chains(score, (CognitiveCoherenceRisk.ALIGNMENT_COHERENCE_BREAK,))
    axes = build_coherence_axes(score, (CognitiveCoherenceRisk.ALIGNMENT_COHERENCE_BREAK,))
    matrix = build_coherence_matrix(axes, chains, (CognitiveCoherenceRisk.ALIGNMENT_COHERENCE_BREAK,))

    assert any(chain.name == "alignment_intent_identity" and chain.complete is False for chain in chains)
    assert "alignment" in matrix.broken_axes
    assert matrix.autonomy_reduced is True


def test_recommendations_cover_coherence_controls() -> None:
    recommendations = generate_cognitive_coherence_recommendations(
        risks=(
            CognitiveCoherenceRisk.LOGICAL_CONTRADICTION,
            CognitiveCoherenceRisk.REASONING_CHAIN_BREAK,
            CognitiveCoherenceRisk.DECISION_SEQUENCE_CONFLICT,
            CognitiveCoherenceRisk.WORLD_MODEL_ACTION_MISMATCH,
            CognitiveCoherenceRisk.TIMELINE_FORECAST_CONFLICT,
            CognitiveCoherenceRisk.STRATEGIC_CONCLUSION_INSTABILITY,
        ),
        state=CognitiveCoherenceState.COHERENCE_AT_RISK,
    )

    assert CognitiveCoherenceRecommendation.EXTEND_REASONING_TRACE in recommendations
    assert CognitiveCoherenceRecommendation.VALIDATE_DECISION_CHAIN in recommendations
    assert CognitiveCoherenceRecommendation.RECHECK_WORLD_MODEL_ACTION_LINK in recommendations
    assert CognitiveCoherenceRecommendation.RECONCILE_FORECAST_TIMELINES in recommendations
    assert CognitiveCoherenceRecommendation.REPAIR_STRATEGIC_CONCLUSIONS in recommendations
    assert CognitiveCoherenceRecommendation.REQUIRE_SUPERVISION in recommendations


def test_render_cognitive_coherence_markdown_contains_required_sections() -> None:
    result = evaluate_cognitive_coherence(
        cognitive_alignment=_alignment(),
        intent_integrity=_intent(),
        cognitive_identity=_identity(),
        cognitive_continuity=_continuity(),
        cognitive_policy=_policy(),
        cognitive_governance=_governance(),
        self_reflection_audit=_audit(),
        recursive_world_model=_world(),
        global_orchestrator=_orchestrator(),
        collective_consensus=_consensus(),
        scenario_forecast=_forecast(),
        multi_timeline=_timeline(),
        strategic_arbitration=_arbitration(),
    )
    markdown = render_cognitive_coherence_markdown(result)

    assert "Cognitive Coherence State" in markdown
    assert "Coherence Score" in markdown
    assert "Reasoning Chains" in markdown
    assert "Coherence Axes" in markdown
    assert "Coherence Matrix" in markdown
    assert "Coherence Risks" in markdown
    assert "Actions" in markdown
    assert "Recommendations" in markdown
    assert "AGIcore Cognitive Coherence Outlook" in markdown
