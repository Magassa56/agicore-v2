from types import SimpleNamespace

from agicore.trading.cognitive_alignment_models import CognitiveAlignmentState
from agicore.trading.cognitive_coherence_models import CognitiveCoherenceRisk, CognitiveCoherenceState
from agicore.trading.cognitive_consensus import (
    build_consensus_matrix,
    build_consensus_reasoning,
    build_consensus_votes,
    compute_cognitive_consensus_score,
    detect_cognitive_consensus_risks,
    evaluate_cognitive_consensus,
    reconcile_conflicts,
    render_cognitive_consensus_markdown,
)
from agicore.trading.cognitive_consensus_models import (
    CognitiveConsensusAction,
    CognitiveConsensusInput,
    CognitiveConsensusMode,
    CognitiveConsensusRecommendation,
    CognitiveConsensusRisk,
    CognitiveConsensusState,
)
from agicore.trading.collective_consensus_models import ConsensusDecision, ConsensusMode
from agicore.trading.multi_timeline_simulation_models import TimelineDecision, TimelineRisk
from agicore.trading.recursive_world_model_models import WorldModelDecision, WorldModelRisk
from agicore.trading.scenario_forecast_models import ForecastDecision
from agicore.trading.strategic_arbitration_models import ArbitrationDecision, ArbitrationMode, ArbitrationSeverity


def ns(**kwargs):
    return SimpleNamespace(**kwargs)


def test_evaluate_cognitive_consensus_reaches_consensus_for_stable_inputs():
    result = evaluate_cognitive_consensus(
        CognitiveConsensusInput(
            cognitive_coherence=ns(
                state=CognitiveCoherenceState.COHERENT,
                cognitive_coherence_score=92,
                risks=(),
                reasoning_chains=(ns(name="main", steps=("a", "b"), score=90, complete=True),),
            ),
            cognitive_alignment=ns(state=CognitiveAlignmentState.FULLY_ALIGNED, cognitive_alignment_score=91, risks=()),
            intent_integrity=ns(state="INTENT_INTACT", intent_integrity_score=90, risks=()),
            cognitive_identity=ns(state="IDENTITY_STABLE", cognitive_identity_score=88, risks=()),
            collective_consensus=ns(
                mode=ConsensusMode.NORMAL_CONSENSUS,
                decision=ConsensusDecision.APPROVE_COLLECTIVE_DECISION,
                collective_confidence_score=90,
                risks=(),
            ),
            strategic_arbitration=ns(
                mode=ArbitrationMode.NORMAL_OPERATION,
                decision=ArbitrationDecision.CONTINUE_OPERATION,
                severity=ArbitrationSeverity.LOW,
                confidence_score=88,
            ),
            recursive_world_model=ns(world_model_coherence_score=90, decision=WorldModelDecision.MAINTAIN_WORLD_MODEL, risks=()),
        )
    )

    assert result.state == CognitiveConsensusState.CONSENSUS_REACHED
    assert result.mode == CognitiveConsensusMode.NORMAL_CONSENSUS
    assert result.cognitive_consensus_score >= 80
    assert result.risks == ()
    assert result.matrix.winning_position == "APPROVE"


def test_detects_reasoning_conflict_from_coherence_and_audit():
    data = CognitiveConsensusInput(
        cognitive_coherence=ns(
            state=CognitiveCoherenceState.LOGICAL_CONFLICT,
            cognitive_coherence_score=70,
            risks=(CognitiveCoherenceRisk.REASONING_CHAIN_BREAK,),
        ),
        self_reflection_audit=ns(state="CONTRADICTORY_REFLECTION", reflection_quality_score=45, risks=()),
    )

    risks = detect_cognitive_consensus_risks(data)

    assert CognitiveConsensusRisk.REASONING_CONFLICT in risks


def test_detects_timeline_conflict_from_forecast_and_timeline():
    data = CognitiveConsensusInput(
        scenario_forecast=ns(forecast_stability_score=50, decision=ForecastDecision.ENTER_FORECAST_SAFE_MODE, risks=()),
        multi_timeline_simulation=ns(
            overall_survivability_score=45,
            decision=TimelineDecision.AVOID_UNSTABLE_TIMELINE,
            risks=(TimelineRisk.COLLAPSE_RISK,),
        ),
    )

    risks = detect_cognitive_consensus_risks(data)

    assert CognitiveConsensusRisk.TIMELINE_CONFLICT in risks


def test_detects_strategic_conflict_and_decision_deadlock():
    data = CognitiveConsensusInput(
        strategic_arbitration=ns(
            mode=ArbitrationMode.EMERGENCY_LOCKDOWN,
            decision=ArbitrationDecision.EMERGENCY_LOCKDOWN,
            severity=ArbitrationSeverity.CRITICAL,
            confidence_score=70,
        ),
        global_orchestrator=ns(mode="NORMAL_OPERATION", decision="CONTINUE_COORDINATED_OPERATION", confidence_score=80),
        collective_consensus=ns(
            mode=ConsensusMode.NORMAL_CONSENSUS,
            decision=ConsensusDecision.APPROVE_COLLECTIVE_DECISION,
            collective_confidence_score=80,
            risks=(),
        ),
    )

    risks = detect_cognitive_consensus_risks(data)

    assert CognitiveConsensusRisk.STRATEGIC_CONFLICT in risks
    assert CognitiveConsensusRisk.DECISION_DEADLOCK in risks


def test_detects_world_model_policy_and_alignment_conflicts():
    data = CognitiveConsensusInput(
        recursive_world_model=ns(
            world_model_coherence_score=40,
            decision=WorldModelDecision.REBUILD_CAUSAL_GRAPH,
            risks=(WorldModelRisk.WORLD_MODEL_INCOHERENCE,),
        ),
        cognitive_policy=ns(mode="POLICY_SAFE_MODE", cognitive_policy_score=45, risks=("POLICY_CONFLICT",)),
        cognitive_governance=ns(mode="SAFE_GOVERNANCE", governance_score=50, risks=()),
        cognitive_alignment=ns(state=CognitiveAlignmentState.SYSTEMIC_MISALIGNMENT, cognitive_alignment_score=35, risks=()),
        intent_integrity=ns(state="INTENT_CONFLICT", intent_integrity_score=40, risks=()),
    )

    risks = detect_cognitive_consensus_risks(data)

    assert CognitiveConsensusRisk.WORLD_MODEL_CONFLICT in risks
    assert CognitiveConsensusRisk.POLICY_CONFLICT in risks
    assert CognitiveConsensusRisk.ALIGNMENT_CONFLICT in risks


def test_locks_consensus_on_systemic_collapse():
    data = CognitiveConsensusInput(
        cognitive_stability=ns(state="COLLAPSING"),
        cognitive_coherence=ns(state="COHERENCE_LOCKED", cognitive_coherence_score=20, risks=(CognitiveCoherenceRisk.LOGICAL_CONTRADICTION,)),
        cognitive_alignment=ns(state=CognitiveAlignmentState.ALIGNMENT_LOCKED, cognitive_alignment_score=20, risks=()),
        collective_consensus=ns(mode=ConsensusMode.CONSENSUS_COLLAPSE, decision=ConsensusDecision.NO_CONSENSUS, collective_confidence_score=15, risks=()),
        strategic_arbitration=ns(mode=ArbitrationMode.EMERGENCY_LOCKDOWN, decision=ArbitrationDecision.EMERGENCY_LOCKDOWN, severity=ArbitrationSeverity.CRITICAL, confidence_score=20),
        global_orchestrator=ns(mode="EMERGENCY_ORCHESTRATION", decision="EMERGENCY_HALT_ROUTING", confidence_score=20),
        recursive_world_model=ns(world_model_coherence_score=20, decision=WorldModelDecision.ENTER_WORLD_MODEL_SAFE_MODE, risks=(WorldModelRisk.SAFETY_MODEL_FAILURE,)),
        cognitive_policy=ns(mode="POLICY_LOCKED", cognitive_policy_score=20, risks=("GOVERNANCE_POLICY_MISMATCH",)),
        intent_integrity=ns(state="INTENT_LOCKED", intent_integrity_score=20, risks=("AUTONOMY_INTENT_EXPANSION",)),
    )

    result = evaluate_cognitive_consensus(data)

    assert result.state == CognitiveConsensusState.CONSENSUS_LOCKED
    assert result.mode == CognitiveConsensusMode.LOCKED_CONSENSUS_MODE
    assert CognitiveConsensusRisk.SYSTEMIC_CONSENSUS_COLLAPSE in result.risks
    assert CognitiveConsensusAction.LOCK_CONSENSUS_STATE in result.actions
    assert result.matrix.locked is True


def test_score_penalizes_conflicted_components():
    data = CognitiveConsensusInput(
        cognitive_coherence=ns(cognitive_coherence_score=90, risks=()),
        recursive_world_model=ns(world_model_coherence_score=90, risks=()),
    )

    stable = compute_cognitive_consensus_score(data, ())
    conflicted = compute_cognitive_consensus_score(
        data,
        (
            CognitiveConsensusRisk.REASONING_CONFLICT,
            CognitiveConsensusRisk.WORLD_MODEL_CONFLICT,
            CognitiveConsensusRisk.AUTONOMY_CONFLICT,
        ),
    )

    assert conflicted.reasoning_consensus_score < stable.reasoning_consensus_score
    assert conflicted.world_model_consensus_score < stable.world_model_consensus_score
    assert conflicted.autonomy_consensus_score < stable.autonomy_consensus_score


def test_votes_and_matrix_expose_safe_or_block_positions():
    data = CognitiveConsensusInput(
        collective_consensus=ns(mode=ConsensusMode.DEGRADED_CONSENSUS, decision=ConsensusDecision.NO_CONSENSUS, collective_confidence_score=35, risks=()),
    )
    risks = detect_cognitive_consensus_risks(data)
    votes = build_consensus_votes(data, risks=risks)
    matrix = build_consensus_matrix(data, risks=risks)

    assert any(vote.vote in {"SAFE_MODE", "BLOCK"} for vote in votes)
    assert matrix.winning_position in {"SAFE_MODE", "BLOCK", "REVIEW"}
    assert matrix.conflict_count > 0


def test_build_consensus_reasoning_uses_existing_chains():
    data = CognitiveConsensusInput(
        cognitive_coherence=ns(
            cognitive_coherence_score=80,
            reasoning_chains=(ns(name="chain_a", steps=("collect", "verify"), score=77, complete=False, broken_step="verify"),),
        )
    )

    chains = build_consensus_reasoning(data)

    assert any(chain.name == "chain_a" for chain in chains)
    assert any(chain.conflict == "verify" for chain in chains)


def test_reconcile_conflicts_returns_operational_notes():
    notes = reconcile_conflicts(
        (
            CognitiveConsensusRisk.REASONING_CONFLICT,
            CognitiveConsensusRisk.TIMELINE_CONFLICT,
            CognitiveConsensusRisk.SYSTEMIC_CONSENSUS_COLLAPSE,
        )
    )

    assert any("reasoning" in note.lower() for note in notes)
    assert any("timeline" in note.lower() for note in notes)
    assert any("Lock consensus" in note for note in notes)


def test_recommendations_cover_safe_consensus_and_manual_validation():
    result = evaluate_cognitive_consensus(
        CognitiveConsensusInput(
            collective_consensus=ns(mode=ConsensusMode.CONSENSUS_COLLAPSE, decision=ConsensusDecision.NO_CONSENSUS, collective_confidence_score=10, risks=()),
            cognitive_stability=ns(state="CRITICAL"),
            cognitive_alignment=ns(state=CognitiveAlignmentState.ALIGNMENT_LOCKED, cognitive_alignment_score=10, risks=()),
            strategic_arbitration=ns(mode=ArbitrationMode.EMERGENCY_LOCKDOWN, decision=ArbitrationDecision.EMERGENCY_LOCKDOWN, severity=ArbitrationSeverity.CRITICAL, confidence_score=10),
        )
    )

    assert CognitiveConsensusRecommendation.ENABLE_SAFE_CONSENSUS in result.recommendations
    assert CognitiveConsensusRecommendation.REQUIRE_MANUAL_VALIDATION in result.recommendations


def test_markdown_contains_required_sections():
    result = evaluate_cognitive_consensus(CognitiveConsensusInput())

    markdown = render_cognitive_consensus_markdown(result)

    assert "# Cognitive Consensus State" in markdown
    assert "# Consensus Score" in markdown
    assert "# Consensus Votes" in markdown
    assert "# Reasoning Debate" in markdown
    assert "# Consensus Matrix" in markdown
    assert "# Consensus Risks" in markdown
    assert "# Actions" in markdown
    assert "# Recommendations" in markdown
    assert "# AGIcore Cognitive Consensus Outlook" in markdown
