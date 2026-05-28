from dataclasses import replace
from types import SimpleNamespace

from agicore.trading.freeze_candidate_review import (
    build_architecture_review,
    build_observability_review,
    build_paper_runtime_review,
    build_runtime_review,
    build_safety_review,
    compute_freeze_candidate_score,
    detect_freeze_candidate_blockers,
    evaluate_freeze_candidate,
    generate_freeze_candidate_recommendations,
    render_freeze_candidate_markdown,
)
from agicore.trading.freeze_candidate_review_models import (
    FreezeCandidateBlocker,
    FreezeCandidateRecommendation,
    FreezeCandidateReviewInput,
    FreezeCandidateState,
)


def ns(**kwargs):
    return SimpleNamespace(**kwargs)


def stable_freeze_readiness_audit():
    snapshot = ns(
        cognitive_fragmentation_score=96,
        engine_conflict_score=96,
        global_stability_score=96,
        runtime_coherence_score=95,
        observability_score=95,
        replay_safety_score=96,
        rollback_score=95,
        sandbox_score=96,
        paper_trading_score=95,
    )
    score = ns(paper_runtime_score=95)
    return ns(
        state="READY_TO_TRY",
        freeze_readiness_score=96,
        score_breakdown=score,
        snapshot=snapshot,
        blockers=(),
        offline_only=True,
    )


def stable_input():
    return FreezeCandidateReviewInput(
        freeze_readiness_audit=stable_freeze_readiness_audit(),
        cognitive_constitutional=ns(state="CONSTITUTION_INTACT", constitutional_score=96, risks=()),
        cognitive_meta_supervision=ns(state="META_SUPERVISION_STABLE", meta_supervision_score=95, risks=()),
        cognitive_recursive_regulation=ns(state="RECURSION_STABLE", recursive_regulation_score=96, risks=()),
        cognitive_safety_orchestrator=ns(state="SAFETY_ORCHESTRATOR_STABLE", safety_orchestrator_score=96, risks=()),
        cognitive_executive_control=ns(state="EXECUTIVE_CONTROL_STABLE", executive_control_score=95, risks=()),
        cognitive_priority_arbitration=ns(state="PRIORITY_ARBITRATION_STABLE", priority_arbitration_score=95, risks=()),
        cognitive_consensus=ns(state="CONSENSUS_REACHED", cognitive_consensus_score=96, risks=()),
        cognitive_coherence=ns(state="COHERENT", cognitive_coherence_score=96, risks=()),
        cognitive_alignment=ns(state="FULLY_ALIGNED", cognitive_alignment_score=95, risks=()),
        cognitive_memory_consolidation=ns(state="MEMORY_CONSOLIDATED", memory_consolidation_score=95, risks=()),
        intent_integrity=ns(state="INTENT_INTACT", intent_integrity_score=96, risks=()),
        cognitive_identity=ns(state="IDENTITY_STABLE", cognitive_identity_score=96, risks=()),
        cognitive_continuity=ns(state="CONTINUITY_STABLE", cognitive_continuity_score=95, risks=()),
        recursive_world_model=ns(decision="MAINTAIN_WORLD_MODEL", world_model_coherence_score=96, risks=()),
        self_reflection_audit=ns(state="CLEAR_REFLECTION", reflection_quality_score=95, risks=()),
        architecture_stable=True,
        module_fragmentation_count=0,
        import_coherence_score=96,
        runtime_stable=True,
        runtime_recoverable=True,
        runtime_observable=True,
        logging_consistent=True,
        replay_safe=True,
        rollback_ready=True,
        rollback_tested=True,
        kill_switch_ready=True,
        sandbox_ready=True,
        paper_runtime_ready=True,
        execution_isolated=True,
        broker_disabled=True,
        external_api_disabled=True,
        live_execution_disabled=True,
        notes=("offline freeze candidate fixture",),
    )


def test_evaluate_freeze_candidate_ready_for_sandbox_when_all_reviews_green():
    result = evaluate_freeze_candidate(stable_input())

    assert result.state == FreezeCandidateState.READY_FOR_SANDBOX
    assert result.freeze_candidate_score >= 94
    assert result.blockers == ()
    assert result.offline_only is True
    assert result.architecture_review.passed is True
    assert result.paper_runtime_review.passed is True


def test_detects_all_required_freeze_candidate_blockers():
    data = FreezeCandidateReviewInput(
        freeze_readiness_audit=ns(blockers=("ENGINE_FRAGMENTATION", "REPLAY_UNSAFE")),
        architecture_stable=False,
        module_fragmentation_count=3,
        import_coherence_score=30,
        runtime_stable=False,
        runtime_recoverable=False,
        runtime_observable=False,
        logging_consistent=False,
        replay_safe=False,
        rollback_ready=False,
        rollback_tested=False,
        kill_switch_ready=False,
        sandbox_ready=False,
        paper_runtime_ready=False,
        execution_isolated=False,
        broker_disabled=False,
        external_api_disabled=False,
        live_execution_disabled=False,
        cognitive_meta_supervision=ns(state="META_SUPERVISION_FRAGMENTED", meta_supervision_score=30, risks=("WORLD_MODEL_DRIFT",)),
        cognitive_recursive_regulation=ns(state="RECURSION_LOCKED", recursive_regulation_score=25, risks=("UNBOUNDED_REASONING_EXPANSION",)),
        recursive_world_model=ns(decision="REBUILD_CAUSAL_GRAPH", world_model_coherence_score=25, risks=()),
        intent_integrity=ns(state="INTENT_DRIFT", intent_integrity_score=35, risks=()),
        cognitive_identity=ns(state="IDENTITY_AT_RISK", cognitive_identity_score=35, risks=()),
        cognitive_consensus=ns(state="CONSENSUS_FRAGMENTED", cognitive_consensus_score=35, risks=("CONFLICT",)),
    )

    blockers = detect_freeze_candidate_blockers(data)

    assert blockers == (
        FreezeCandidateBlocker.ARCHITECTURE_FRAGMENTATION,
        FreezeCandidateBlocker.RUNTIME_INSTABILITY,
        FreezeCandidateBlocker.REPLAY_UNSAFE,
        FreezeCandidateBlocker.ROLLBACK_FAILURE_RISK,
        FreezeCandidateBlocker.KILL_SWITCH_ABSENT,
        FreezeCandidateBlocker.EXECUTION_LEAK_RISK,
        FreezeCandidateBlocker.COGNITIVE_DRIFT,
        FreezeCandidateBlocker.RECURSIVE_OVERFLOW_RISK,
        FreezeCandidateBlocker.OBSERVABILITY_GAP,
        FreezeCandidateBlocker.SANDBOX_NOT_READY,
    )


def test_execution_leak_forces_not_ready_and_offline_false():
    data = replace(
        stable_input(),
        execution_isolated=False,
        broker_disabled=False,
        external_api_disabled=False,
        live_execution_disabled=False,
    )

    result = evaluate_freeze_candidate(data)

    assert FreezeCandidateBlocker.EXECUTION_LEAK_RISK in result.blockers
    assert result.state == FreezeCandidateState.NOT_READY
    assert result.offline_only is False


def test_review_required_when_multiple_non_execution_blockers_remain():
    data = replace(
        stable_input(),
        runtime_stable=False,
        replay_safe=False,
        rollback_ready=False,
        rollback_tested=False,
    )

    result = evaluate_freeze_candidate(data)

    assert result.state == FreezeCandidateState.REVIEW_REQUIRED
    assert FreezeCandidateBlocker.RUNTIME_INSTABILITY in result.blockers
    assert FreezeCandidateBlocker.REPLAY_UNSAFE in result.blockers
    assert FreezeCandidateBlocker.ROLLBACK_FAILURE_RISK in result.blockers


def test_freeze_candidate_when_single_blocker_remains():
    data = replace(stable_input(), paper_runtime_ready=False)

    result = evaluate_freeze_candidate(data)

    assert result.state == FreezeCandidateState.FREEZE_CANDIDATE
    assert result.blockers == (FreezeCandidateBlocker.SANDBOX_NOT_READY,)


def test_stable_state_when_green_but_below_sandbox_threshold():
    snapshot = ns(
        cognitive_fragmentation_score=89,
        engine_conflict_score=89,
        global_stability_score=89,
        runtime_coherence_score=89,
        observability_score=89,
        replay_safety_score=89,
        rollback_score=89,
        sandbox_score=89,
        paper_trading_score=89,
    )
    data = replace(
        stable_input(),
        freeze_readiness_audit=ns(
            state="STABLE",
            freeze_readiness_score=89,
            score_breakdown=ns(paper_runtime_score=89),
            snapshot=snapshot,
            blockers=(),
            offline_only=True,
        ),
        cognitive_constitutional=ns(state="CONSTITUTION_INTACT", constitutional_score=89, risks=()),
        cognitive_meta_supervision=ns(state="META_SUPERVISION_STABLE", meta_supervision_score=89, risks=()),
        cognitive_recursive_regulation=ns(state="RECURSION_STABLE", recursive_regulation_score=89, risks=()),
        cognitive_safety_orchestrator=ns(state="SAFETY_ORCHESTRATOR_STABLE", safety_orchestrator_score=89, risks=()),
        cognitive_executive_control=ns(state="EXECUTIVE_CONTROL_STABLE", executive_control_score=89, risks=()),
        cognitive_priority_arbitration=ns(state="PRIORITY_ARBITRATION_STABLE", priority_arbitration_score=89, risks=()),
        cognitive_consensus=ns(state="CONSENSUS_REACHED", cognitive_consensus_score=89, risks=()),
        cognitive_coherence=ns(state="COHERENT", cognitive_coherence_score=89, risks=()),
        intent_integrity=ns(state="INTENT_INTACT", intent_integrity_score=89, risks=()),
        cognitive_identity=ns(state="IDENTITY_STABLE", cognitive_identity_score=89, risks=()),
        cognitive_continuity=ns(state="CONTINUITY_STABLE", cognitive_continuity_score=89, risks=()),
        recursive_world_model=ns(decision="MAINTAIN_WORLD_MODEL", world_model_coherence_score=89, risks=()),
        architecture_score=89,
        runtime_score=89,
        safety_score=89,
        observability_score=89,
        paper_runtime_score=89,
    )

    result = evaluate_freeze_candidate(data)

    assert result.state == FreezeCandidateState.STABLE
    assert result.blockers == ()


def test_architecture_review_uses_imports_and_consensus_evidence():
    data = replace(
        stable_input(),
        architecture_stable=False,
        module_fragmentation_count=1,
        import_coherence_score=65,
        cognitive_consensus=ns(state="CONSENSUS_FRAGMENTED", cognitive_consensus_score=55, risks=("CONFLICT",)),
    )

    review = build_architecture_review(data)

    assert review.passed is False
    assert FreezeCandidateBlocker.ARCHITECTURE_FRAGMENTATION in review.blockers
    assert any("import_coherence_score=65/100" == item for item in review.evidence)


def test_runtime_safety_observability_and_paper_reviews_are_independent():
    data = replace(stable_input(), logging_consistent=False, kill_switch_ready=False, sandbox_ready=False)

    runtime = build_runtime_review(data)
    safety = build_safety_review(data)
    observability = build_observability_review(data)
    paper = build_paper_runtime_review(data)

    assert runtime.passed is True
    assert FreezeCandidateBlocker.KILL_SWITCH_ABSENT in safety.blockers
    assert FreezeCandidateBlocker.OBSERVABILITY_GAP in observability.blockers
    assert FreezeCandidateBlocker.SANDBOX_NOT_READY in paper.blockers


def test_score_penalizes_blockers_and_caps_execution_leak():
    data = stable_input()
    clean_score = compute_freeze_candidate_score(data, ())
    blocked_score = compute_freeze_candidate_score(data, (FreezeCandidateBlocker.EXECUTION_LEAK_RISK,))

    assert blocked_score.overall_score < clean_score.overall_score
    assert blocked_score.overall_score <= 45


def test_recommendations_cover_blockers_and_manual_review_gate():
    recommendations = generate_freeze_candidate_recommendations(
        (
            FreezeCandidateBlocker.ARCHITECTURE_FRAGMENTATION,
            FreezeCandidateBlocker.KILL_SWITCH_ABSENT,
        ),
        FreezeCandidateState.REVIEW_REQUIRED,
    )

    assert FreezeCandidateRecommendation.HOLD_FREEZE_APPROVAL in recommendations
    assert FreezeCandidateRecommendation.REDUCE_ARCHITECTURE_FRAGMENTATION in recommendations
    assert FreezeCandidateRecommendation.INSTALL_KILL_SWITCH in recommendations
    assert FreezeCandidateRecommendation.RUN_FREEZE_CANDIDATE_REVIEW_SUITE in recommendations


def test_markdown_contains_required_sections_and_blockers():
    result = evaluate_freeze_candidate(replace(stable_input(), kill_switch_ready=False))

    markdown = render_freeze_candidate_markdown(result)

    assert "# AGIcore Freeze Candidate Review" in markdown
    assert "# Score Breakdown" in markdown
    assert "# Review Sections" in markdown
    assert "# Freeze Candidate Blockers" in markdown
    assert "# Recommendations" in markdown
    assert "# Freeze Candidate Outlook" in markdown
    assert "KILL_SWITCH_ABSENT" in markdown
