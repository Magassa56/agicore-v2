from types import SimpleNamespace

from agicore.trading.cognitive_consensus_models import CognitiveConsensusState, ConsensusReasoningChain
from agicore.trading.cognitive_memory_consolidation import (
    build_memory_clusters,
    build_memory_traces,
    compute_memory_consolidation_score,
    consolidate_memory_snapshot,
    detect_memory_consolidation_risks,
    evaluate_cognitive_memory_consolidation,
    generate_memory_consolidation_recommendations,
    render_cognitive_memory_consolidation_markdown,
)
from agicore.trading.cognitive_memory_consolidation_models import (
    CognitiveMemoryConsolidationInput,
    MemoryConsolidationAction,
    MemoryConsolidationMode,
    MemoryConsolidationRecommendation,
    MemoryConsolidationRisk,
    MemoryConsolidationState,
    MemoryTrace,
)


def ns(**kwargs):
    return SimpleNamespace(**kwargs)


def stable_input():
    return CognitiveMemoryConsolidationInput(
        cognitive_consensus=ns(
            state=CognitiveConsensusState.CONSENSUS_REACHED,
            cognitive_consensus_score=92,
            reasoning_chains=(ConsensusReasoningChain(name="safe_chain", steps=("observe", "align"), score=90),),
            risks=(),
        ),
        cognitive_coherence=ns(state="COHERENT", cognitive_coherence_score=91, reasoning_chains=(), risks=()),
        cognitive_alignment=ns(state="FULLY_ALIGNED", cognitive_alignment_score=90, risks=()),
        intent_integrity=ns(state="INTENT_INTACT", intent_integrity_score=89, risks=()),
        cognitive_identity=ns(state="IDENTITY_STABLE", cognitive_identity_score=90, risks=()),
        cognitive_continuity=ns(state="CONTINUOUS", cognitive_continuity_score=88, risks=()),
        cognitive_resilience=ns(state="RESILIENT", cognitive_resilience_score=87, risks=()),
        cognitive_stability=ns(state="STABLE", cognitive_stability_score=90, risks=()),
        self_reflection_audit=ns(state="CLEAR_REFLECTION", reflection_quality_score=89, risks=()),
        recursive_world_model=ns(decision="MAINTAIN_WORLD_MODEL", world_model_coherence_score=88, risks=()),
        strategic_timeline_analysis=ns(
            snapshots_count=3,
            strategic_health_score=86,
            stability_score=87,
            degradation_detected=False,
        ),
        session_replay=ns(sessions=(ns(),), discipline_score=85),
        trade_journal_result=ns(
            total_trades=4,
            playbook_compliance_rate=0.9,
            risk_rules_compliance_rate=0.9,
            trades_to_review=(),
        ),
        strategy_dna=ns(name="EMA20 Pullback"),
    )


def test_evaluate_memory_consolidation_consolidates_stable_memory():
    result = evaluate_cognitive_memory_consolidation(stable_input())

    assert result.state == MemoryConsolidationState.MEMORY_CONSOLIDATED
    assert result.mode == MemoryConsolidationMode.NORMAL_CONSOLIDATION
    assert result.memory_consolidation_score >= 75
    assert result.risks == ()
    assert result.snapshot.protected is True
    assert "capital_preservation" in result.snapshot.preserved_invariants


def test_build_memory_traces_collects_reasoning_and_strategy_sources():
    traces = build_memory_traces(stable_input())

    assert any(trace.trace_id == "cognitive_consensus" for trace in traces)
    assert any("reasoning" in trace.tags for trace in traces)
    assert any(trace.trace_id == "strategy_dna" for trace in traces)
    assert any("experience" in trace.tags for trace in traces)


def test_build_memory_clusters_groups_traces_by_memory_domain():
    traces = build_memory_traces(stable_input())
    clusters = build_memory_clusters(traces)

    names = {cluster.name for cluster in clusters}
    assert "reasoning_memory" in names
    assert "strategic_experience" in names
    assert "invariant_memory" in names
    assert "continuity_memory" in names


def test_detects_memory_fragmentation_for_sparse_input():
    data = CognitiveMemoryConsolidationInput(
        manual_traces=(MemoryTrace(trace_id="single", source="manual", content="only trace", confidence_score=80),)
    )

    risks = detect_memory_consolidation_risks(data)

    assert MemoryConsolidationRisk.MEMORY_FRAGMENTATION in risks
    assert MemoryConsolidationRisk.REASONING_TRACE_LOSS in risks
    assert MemoryConsolidationRisk.STRATEGIC_EXPERIENCE_LOSS in risks


def test_detects_contradictory_memory_trace():
    data = CognitiveMemoryConsolidationInput(
        cognitive_consensus=ns(state="HIGH_CONFLICT_STATE", cognitive_consensus_score=50, reasoning_chains=(), risks=()),
        self_reflection_audit=ns(state="CONTRADICTORY_REFLECTION", reflection_quality_score=45, risks=()),
        manual_traces=(
            MemoryTrace(
                trace_id="manual_conflict",
                source="manual",
                content="conflicting trace",
                confidence_score=55,
                critical=True,
                contradicted=True,
                tags=("reasoning",),
            ),
        ),
    )

    risks = detect_memory_consolidation_risks(data)

    assert MemoryConsolidationRisk.CONTRADICTORY_MEMORY_TRACE in risks


def test_detects_identity_and_continuity_memory_breaks():
    data = stable_input()
    data = CognitiveMemoryConsolidationInput(
        cognitive_alignment=ns(state="SYSTEMIC_MISALIGNMENT", cognitive_alignment_score=30, risks=("MISSION_ALIGNMENT_BREAK",)),
        intent_integrity=ns(state="INTENT_CONFLICT", intent_integrity_score=35, risks=()),
        cognitive_identity=ns(state="IDENTITY_AT_RISK", cognitive_identity_score=35, risks=("IDENTITY_DRIFT",)),
        cognitive_continuity=ns(state="CONTINUITY_FAILURE", cognitive_continuity_score=30, risks=("DECISION_CHAIN_BREAK",)),
        cognitive_coherence=ns(state="COHERENT", cognitive_coherence_score=70, reasoning_chains=(), risks=()),
        strategy_dna=ns(name="EMA20 Pullback"),
    )

    risks = detect_memory_consolidation_risks(data)

    assert MemoryConsolidationRisk.INVARIANT_MEMORY_DRIFT in risks
    assert MemoryConsolidationRisk.IDENTITY_MEMORY_MISMATCH in risks
    assert MemoryConsolidationRisk.CONTINUITY_MEMORY_BREAK in risks


def test_locks_memory_on_corruption_risk():
    data = CognitiveMemoryConsolidationInput(
        cognitive_consensus=ns(state="CONSENSUS_LOCKED", cognitive_consensus_score=15, reasoning_chains=(), risks=()),
        cognitive_coherence=ns(state="COHERENCE_LOCKED", cognitive_coherence_score=15, reasoning_chains=(), risks=("REASONING_CHAIN_BREAK",)),
        cognitive_alignment=ns(state="ALIGNMENT_LOCKED", cognitive_alignment_score=15, risks=("MISSION_ALIGNMENT_BREAK",)),
        intent_integrity=ns(state="INTENT_LOCKED", intent_integrity_score=15, risks=()),
        cognitive_identity=ns(state="IDENTITY_LOCKED", cognitive_identity_score=15, risks=("IDENTITY_DRIFT",)),
        cognitive_continuity=ns(state="CONTINUITY_FAILURE", cognitive_continuity_score=15, risks=("DECISION_CHAIN_BREAK",)),
        cognitive_resilience=ns(state="CRITICAL", cognitive_resilience_score=15, risks=()),
        cognitive_stability=ns(state="COLLAPSING", cognitive_stability_score=15, risks=()),
        self_reflection_audit=ns(state="CRITICAL_REVIEW", reflection_quality_score=15, risks=()),
    )

    result = evaluate_cognitive_memory_consolidation(data)

    assert result.state == MemoryConsolidationState.MEMORY_LOCKED
    assert result.mode == MemoryConsolidationMode.LOCKED_MEMORY_MODE
    assert MemoryConsolidationRisk.MEMORY_CORRUPTION_RISK in result.risks
    assert MemoryConsolidationAction.LOCK_MEMORY_STATE in result.actions
    assert result.snapshot.locked is True


def test_score_penalizes_contradictions_and_identity_breaks():
    traces = build_memory_traces(stable_input())
    clusters = build_memory_clusters(traces)
    stable_score = compute_memory_consolidation_score(stable_input(), traces, clusters, ())
    degraded_score = compute_memory_consolidation_score(
        stable_input(),
        traces,
        clusters,
        (
            MemoryConsolidationRisk.CONTRADICTORY_MEMORY_TRACE,
            MemoryConsolidationRisk.IDENTITY_MEMORY_MISMATCH,
            MemoryConsolidationRisk.CONTINUITY_MEMORY_BREAK,
        ),
    )

    assert degraded_score.contradiction_cleanup_score < stable_score.contradiction_cleanup_score
    assert degraded_score.identity_memory_score < stable_score.identity_memory_score
    assert degraded_score.continuity_score < stable_score.continuity_score


def test_consolidated_snapshot_preserves_invariants_and_critical_traces():
    traces = build_memory_traces(stable_input())
    clusters = build_memory_clusters(traces)
    score = compute_memory_consolidation_score(stable_input(), traces, clusters, ())

    snapshot = consolidate_memory_snapshot(traces, clusters, score, ())

    assert snapshot.memory_confidence_score == score.overall_memory_score
    assert "mission_offline_only" in snapshot.preserved_invariants
    assert "cognitive_consensus" in snapshot.critical_trace_ids
    assert snapshot.protected is True


def test_recommendations_include_safe_trace_merge_and_overwrite_avoidance():
    recommendations = generate_memory_consolidation_recommendations(
        (
            MemoryConsolidationRisk.CONTRADICTORY_MEMORY_TRACE,
            MemoryConsolidationRisk.CONSOLIDATION_OVERWRITE_RISK,
            MemoryConsolidationRisk.IDENTITY_MEMORY_MISMATCH,
        )
    )

    assert MemoryConsolidationRecommendation.MERGE_SAFE_TRACES_ONLY in recommendations
    assert MemoryConsolidationRecommendation.AVOID_OVERWRITE in recommendations
    assert MemoryConsolidationRecommendation.KEEP_AUTONOMY_REDUCED in recommendations


def test_markdown_contains_required_sections():
    result = evaluate_cognitive_memory_consolidation(stable_input())

    markdown = render_cognitive_memory_consolidation_markdown(result)

    assert "# Cognitive Memory Consolidation State" in markdown
    assert "# Memory Score" in markdown
    assert "# Memory Traces" in markdown
    assert "# Memory Clusters" in markdown
    assert "# Consolidated Snapshot" in markdown
    assert "# Memory Risks" in markdown
    assert "# Actions" in markdown
    assert "# Recommendations" in markdown
    assert "# AGIcore Memory Consolidation Outlook" in markdown
