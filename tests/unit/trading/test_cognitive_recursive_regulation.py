from types import SimpleNamespace

from agicore.trading.cognitive_recursive_regulation import (
    build_recursive_regulation_graph,
    build_recursive_stabilization_plan,
    compute_recursive_regulation_score,
    detect_recursive_regulation_risks,
    evaluate_cognitive_recursive_regulation,
    generate_recursive_regulation_directives,
    render_cognitive_recursive_regulation_markdown,
)
from agicore.trading.cognitive_recursive_regulation_models import (
    CognitiveRecursiveRegulationInput,
    RecursiveRegulationDirective,
    RecursiveRegulationMode,
    RecursiveRegulationRecommendation,
    RecursiveRegulationRisk,
    RecursiveRegulationState,
)


def ns(**kwargs):
    return SimpleNamespace(**kwargs)


def stable_input():
    return CognitiveRecursiveRegulationInput(
        cognitive_meta_supervision=ns(state="META_SUPERVISION_STABLE", meta_supervision_score=90, directives=(), risks=()),
        cognitive_safety_orchestrator=ns(state="SAFETY_ORCHESTRATOR_STABLE", safety_orchestrator_score=90, directives=(), risks=()),
        cognitive_consensus=ns(state="CONSENSUS_REACHED", cognitive_consensus_score=90, risks=()),
        cognitive_coherence=ns(state="COHERENT", cognitive_coherence_score=90, risks=()),
        cognitive_alignment=ns(state="FULLY_ALIGNED", cognitive_alignment_score=90, risks=()),
        cognitive_executive_control=ns(state="EXECUTIVE_CONTROL_STABLE", executive_control_score=90, actions=(), risks=()),
        recursive_world_model=ns(decision="MAINTAIN_WORLD_MODEL", world_model_coherence_score=90, risks=()),
        intent_integrity=ns(state="INTENT_INTACT", intent_integrity_score=90, risks=()),
        cognitive_memory_consolidation=ns(state="MEMORY_CONSOLIDATED", memory_consolidation_score=90, risks=()),
        self_reflection_audit=ns(state="CLEAR_REFLECTION", reflection_quality_score=90, risks=()),
        requested_recursive_depth=2,
        max_allowed_depth=3,
        recursive_cycle_count=1,
        signal_amplification_factor=1.0,
    )


def test_evaluate_recursive_regulation_stable_state():
    result = evaluate_cognitive_recursive_regulation(stable_input())

    assert result.state == RecursiveRegulationState.RECURSION_STABLE
    assert result.mode == RecursiveRegulationMode.NORMAL_RECURSIVE_REGULATION
    assert result.recursive_regulation_score >= 80
    assert result.risks == ()
    assert result.stabilization_plan.throttle_active is False


def test_detects_runaway_recursion_and_depth_limit():
    data = CognitiveRecursiveRegulationInput(requested_recursive_depth=6, max_allowed_depth=3, recursive_cycle_count=9)

    result = evaluate_cognitive_recursive_regulation(data)

    assert RecursiveRegulationRisk.RUNAWAY_RECURSION in result.risks
    assert RecursiveRegulationDirective.LIMIT_RECURSIVE_DEPTH in result.directives
    assert result.stabilization_plan.throttle_active is True


def test_detects_recursive_feedback_loop():
    data = CognitiveRecursiveRegulationInput(
        recursive_world_model=ns(decision="FREEZE_RECURSIVE_UPDATES", world_model_coherence_score=60, risks=("RECURSIVE_FEEDBACK_LOOP",)),
    )

    risks = detect_recursive_regulation_risks(data)

    assert RecursiveRegulationRisk.RECURSIVE_FEEDBACK_LOOP in risks


def test_detects_signal_amplification():
    data = CognitiveRecursiveRegulationInput(signal_amplification_factor=2.5)

    result = evaluate_cognitive_recursive_regulation(data)

    assert RecursiveRegulationRisk.COGNITIVE_SIGNAL_AMPLIFICATION in result.risks
    assert result.mode == RecursiveRegulationMode.RECURSIVE_THROTTLING
    assert RecursiveRegulationDirective.THROTTLE_RECURSIVE_SIGNALS in result.directives


def test_detects_world_model_recursive_drift():
    data = CognitiveRecursiveRegulationInput(
        recursive_world_model=ns(decision="REBUILD_CAUSAL_GRAPH", world_model_coherence_score=30, risks=("WORLD_MODEL_INCOHERENCE",)),
    )

    risks = detect_recursive_regulation_risks(data)

    assert RecursiveRegulationRisk.WORLD_MODEL_RECURSIVE_DRIFT in risks


def test_detects_self_reference_collapse():
    data = CognitiveRecursiveRegulationInput(
        self_reflection_audit=ns(state="CONTRADICTORY_REFLECTION", reflection_quality_score=30, risks=("REFLECTION_FAILURE",)),
    )

    risks = detect_recursive_regulation_risks(data)

    assert RecursiveRegulationRisk.SELF_REFERENCE_COLLAPSE in risks


def test_detects_meta_loop_instability():
    data = CognitiveRecursiveRegulationInput(
        cognitive_meta_supervision=ns(state="META_SUPERVISION_CRITICAL", meta_supervision_score=25, directives=(), risks=("RECURSIVE_INSTABILITY",)),
    )

    result = evaluate_cognitive_recursive_regulation(data)

    assert RecursiveRegulationRisk.META_LOOP_INSTABILITY in result.risks
    assert result.state == RecursiveRegulationState.RECURSION_RECOVERING


def test_detects_cross_engine_recursive_propagation():
    data = CognitiveRecursiveRegulationInput(
        cognitive_consensus=ns(state="CONSENSUS_REACHED", cognitive_consensus_score=90, risks=()),
        cognitive_coherence=ns(state="LOGICAL_CONFLICT", cognitive_coherence_score=30, risks=()),
        cognitive_alignment=ns(state="ALIGNMENT_DRIFT", cognitive_alignment_score=30, risks=()),
        intent_integrity=ns(state="INTENT_CONFLICT", intent_integrity_score=30, risks=()),
        cognitive_memory_consolidation=ns(state="MEMORY_CONSOLIDATED", memory_consolidation_score=90, risks=()),
    )

    result = evaluate_cognitive_recursive_regulation(data)

    assert RecursiveRegulationRisk.CROSS_ENGINE_RECURSIVE_PROPAGATION in result.risks
    assert result.mode == RecursiveRegulationMode.PROPAGATION_CONTROL
    assert result.stabilization_plan.propagation_contained is True


def test_detects_executive_recursion_lock():
    data = CognitiveRecursiveRegulationInput(
        cognitive_executive_control=ns(state="EXECUTIVE_CONTROL_LOCKED", executive_control_score=20, actions=("LOCK_EXECUTIVE_CONTROL",), risks=()),
    )

    risks = detect_recursive_regulation_risks(data)

    assert RecursiveRegulationRisk.EXECUTIVE_RECURSION_LOCK in risks


def test_detects_recursive_consensus_cascade():
    data = CognitiveRecursiveRegulationInput(
        cognitive_consensus=ns(state="CONSENSUS_FRAGMENTED", cognitive_consensus_score=20, risks=()),
    )

    risks = detect_recursive_regulation_risks(data)

    assert RecursiveRegulationRisk.RECURSIVE_CONSENSUS_CASCADE in risks


def test_detects_unbounded_reasoning_expansion_and_locks():
    data = CognitiveRecursiveRegulationInput(
        requested_recursive_depth=7,
        max_allowed_depth=3,
        recursive_cycle_count=13,
    )

    result = evaluate_cognitive_recursive_regulation(data)

    assert RecursiveRegulationRisk.UNBOUNDED_REASONING_EXPANSION in result.risks
    assert result.state == RecursiveRegulationState.RECURSION_LOCKED
    assert result.mode == RecursiveRegulationMode.RECURSIVE_LOCKDOWN
    assert RecursiveRegulationDirective.LOCK_RECURSIVE_EXPANSION in result.directives


def test_score_penalizes_recursive_risks():
    stable = compute_recursive_regulation_score(stable_input(), ())
    degraded = compute_recursive_regulation_score(
        stable_input(),
        (
            RecursiveRegulationRisk.RUNAWAY_RECURSION,
            RecursiveRegulationRisk.RECURSIVE_FEEDBACK_LOOP,
            RecursiveRegulationRisk.RECURSIVE_CONSENSUS_CASCADE,
        ),
    )

    assert degraded.recursion_depth_score < stable.recursion_depth_score
    assert degraded.feedback_loop_score < stable.feedback_loop_score
    assert degraded.consensus_recursion_score < stable.consensus_recursion_score
    assert degraded.overall_score < stable.overall_score


def test_graph_and_plan_capture_throttling_and_propagation():
    risks = (
        RecursiveRegulationRisk.RECURSIVE_FEEDBACK_LOOP,
        RecursiveRegulationRisk.CROSS_ENGINE_RECURSIVE_PROPAGATION,
        RecursiveRegulationRisk.EXECUTIVE_RECURSION_LOCK,
        RecursiveRegulationRisk.RECURSIVE_CONSENSUS_CASCADE,
    )
    directives = generate_recursive_regulation_directives(risks)
    graph = build_recursive_regulation_graph(stable_input(), risks)
    plan = build_recursive_stabilization_plan(stable_input(), directives, risks)

    assert graph.feedback_loops
    assert graph.propagation_paths
    assert "executive_control" in graph.throttled_nodes
    assert plan.propagation_contained is True
    assert plan.executive_protected is True
    assert plan.consensus_protected is True


def test_directives_and_recommendations_cover_required_risks():
    result = evaluate_cognitive_recursive_regulation(
        CognitiveRecursiveRegulationInput(
            requested_recursive_depth=8,
            max_allowed_depth=3,
            recursive_cycle_count=14,
            signal_amplification_factor=2.5,
            cognitive_meta_supervision=ns(state="META_SUPERVISION_CRITICAL", meta_supervision_score=20, directives=(), risks=("RECURSIVE_INSTABILITY",)),
            cognitive_consensus=ns(state="CONSENSUS_FRAGMENTED", cognitive_consensus_score=20, risks=()),
            recursive_world_model=ns(decision="REBUILD_CAUSAL_GRAPH", world_model_coherence_score=20, risks=("RECURSIVE_FEEDBACK_LOOP",)),
            self_reflection_audit=ns(state="CONTRADICTORY_REFLECTION", reflection_quality_score=20, risks=()),
        )
    )

    assert RecursiveRegulationDirective.LIMIT_RECURSIVE_DEPTH in result.directives
    assert RecursiveRegulationDirective.THROTTLE_RECURSIVE_SIGNALS in result.directives
    assert RecursiveRegulationDirective.BREAK_FEEDBACK_LOOP in result.directives
    assert RecursiveRegulationDirective.LOCK_RECURSIVE_EXPANSION in result.directives
    assert RecursiveRegulationRecommendation.REQUIRE_MANUAL_RECURSION_REVIEW in result.recommendations


def test_markdown_contains_required_sections():
    result = evaluate_cognitive_recursive_regulation(stable_input())

    markdown = render_cognitive_recursive_regulation_markdown(result)

    assert "# Cognitive Recursive Regulation State" in markdown
    assert "# Recursive Safety Score" in markdown
    assert "# Recursive Regulation Graph" in markdown
    assert "# Recursive Stabilization Plan" in markdown
    assert "# Recursive Risks" in markdown
    assert "# Directives" in markdown
    assert "# Recommendations" in markdown
    assert "# AGIcore Recursive Regulation Outlook" in markdown
