from types import SimpleNamespace

from agicore.trading.cognitive_executive_control import (
    build_executive_decision_graph,
    build_executive_directives,
    compute_executive_control_score,
    detect_executive_control_risks,
    evaluate_cognitive_executive_control,
    generate_executive_control_recommendations,
    render_cognitive_executive_control_markdown,
)
from agicore.trading.cognitive_executive_control_models import (
    CognitiveExecutiveControlInput,
    ExecutiveControlAction,
    ExecutiveControlMode,
    ExecutiveControlRecommendation,
    ExecutiveControlRisk,
    ExecutiveControlState,
)


def ns(**kwargs):
    return SimpleNamespace(**kwargs)


def stable_input():
    return CognitiveExecutiveControlInput(
        cognitive_memory_consolidation=ns(state="MEMORY_CONSOLIDATED", memory_consolidation_score=91, risks=()),
        cognitive_consensus=ns(state="CONSENSUS_REACHED", cognitive_consensus_score=90, risks=()),
        cognitive_coherence=ns(state="COHERENT", cognitive_coherence_score=90, risks=()),
        cognitive_alignment=ns(state="FULLY_ALIGNED", cognitive_alignment_score=91, risks=()),
        intent_integrity=ns(state="INTENT_INTACT", intent_integrity_score=90, risks=()),
        cognitive_identity=ns(state="IDENTITY_STABLE", cognitive_identity_score=90, risks=()),
        cognitive_continuity=ns(state="CONTINUOUS", cognitive_continuity_score=88, risks=()),
        cognitive_recovery=ns(state="RECOVERED", cognitive_recovery_score=89, risks=()),
        cognitive_resilience=ns(state="RESILIENT", cognitive_resilience_score=88, risks=()),
        cognitive_stability=ns(state="STABLE", cognitive_stability_score=90, risks=()),
        cognitive_policy=ns(mode="POLICY_NORMAL", cognitive_policy_score=90, decisions=("ALLOW",), risks=()),
        cognitive_governance=ns(
            mode="NORMAL_GOVERNANCE",
            autonomy_level="LIMITED_AUTONOMY",
            governance_score=90,
            risks=(),
        ),
        self_reflection_audit=ns(state="CLEAR_REFLECTION", reflection_quality_score=90, risks=()),
        recursive_world_model=ns(decision="MAINTAIN_WORLD_MODEL", world_model_coherence_score=89, risks=()),
        global_orchestrator=ns(mode="NORMAL_OPERATION", confidence_score=88, risks=()),
        system_integrity=ns(status="HEALTHY", integrity_score=90, risks=()),
        mission_continuity=ns(mode="FULL_OPERATION", continuity_score=90, risks=()),
    )


def test_evaluate_cognitive_executive_control_allows_stable_continuation():
    result = evaluate_cognitive_executive_control(stable_input())

    assert result.state == ExecutiveControlState.EXECUTIVE_CONTROL_STABLE
    assert result.mode == ExecutiveControlMode.NORMAL_EXECUTIVE_CONTROL
    assert result.executive_control_score >= 80
    assert result.risks == ()
    assert ExecutiveControlAction.ALLOW_CONTINUE in result.actions
    assert result.decision_graph.safe_mode_required is False


def test_detects_autonomy_too_high_when_core_scores_are_weak():
    data = CognitiveExecutiveControlInput(
        cognitive_governance=ns(autonomy_level="FULL_AUTONOMY", governance_score=80, risks=()),
        cognitive_alignment=ns(cognitive_alignment_score=45, state="PARTIAL_MISALIGNMENT", risks=()),
        cognitive_coherence=ns(cognitive_coherence_score=90, state="COHERENT", risks=()),
        cognitive_consensus=ns(cognitive_consensus_score=90, state="CONSENSUS_REACHED", risks=()),
    )

    risks = detect_executive_control_risks(data)

    assert ExecutiveControlRisk.AUTONOMY_TOO_HIGH in risks


def test_policy_or_intent_failure_blocks_action():
    data = CognitiveExecutiveControlInput(
        cognitive_policy=ns(
            mode="POLICY_LOCKED",
            cognitive_policy_score=30,
            decisions=("LOCKDOWN",),
            risks=("EXECUTION_ROUTING_UNSAFE",),
        ),
        intent_integrity=ns(state="INTENT_CORRUPTED", intent_integrity_score=25, risks=("INTENT_COLLAPSE_RISK",)),
    )

    result = evaluate_cognitive_executive_control(data)

    assert ExecutiveControlRisk.POLICY_BLOCK_REQUIRED in result.risks
    assert ExecutiveControlRisk.INTENT_FAILURE in result.risks
    assert ExecutiveControlAction.BLOCK_ACTION in result.actions
    assert any(directive.blocks_execution for directive in result.directives)


def test_alignment_coherence_consensus_failures_reduce_autonomy():
    data = CognitiveExecutiveControlInput(
        cognitive_alignment=ns(state="SYSTEMIC_MISALIGNMENT", cognitive_alignment_score=30, risks=()),
        cognitive_coherence=ns(state="LOGICAL_CONFLICT", cognitive_coherence_score=30, risks=()),
        cognitive_consensus=ns(state="CONSENSUS_FRAGMENTED", cognitive_consensus_score=30, risks=()),
    )

    result = evaluate_cognitive_executive_control(data)

    assert ExecutiveControlRisk.ALIGNMENT_FAILURE in result.risks
    assert ExecutiveControlRisk.COHERENCE_FAILURE in result.risks
    assert ExecutiveControlRisk.CONSENSUS_FAILURE in result.risks
    assert ExecutiveControlAction.REDUCE_AUTONOMY in result.actions


def test_memory_failure_protects_memory_and_requires_supervision():
    data = CognitiveExecutiveControlInput(
        cognitive_memory_consolidation=ns(
            state="MEMORY_LOCKED",
            memory_consolidation_score=20,
            risks=("MEMORY_CORRUPTION_RISK",),
        )
    )

    result = evaluate_cognitive_executive_control(data)

    assert ExecutiveControlRisk.MEMORY_FAILURE in result.risks
    assert ExecutiveControlAction.REQUIRE_SUPERVISION in result.actions
    assert ExecutiveControlRecommendation.PROTECT_MEMORY in result.recommendations


def test_recovery_incomplete_enters_recovery_control_when_isolated():
    data = CognitiveExecutiveControlInput(
        cognitive_recovery=ns(state="RECOVERING", cognitive_recovery_score=65, risks=()),
        cognitive_resilience=ns(state="RECOVERING", cognitive_resilience_score=65, risks=()),
    )

    result = evaluate_cognitive_executive_control(data)

    assert result.state == ExecutiveControlState.EXECUTIVE_CONTROL_RECOVERING
    assert result.mode == ExecutiveControlMode.RECOVERY_CONTROL
    assert ExecutiveControlRisk.RECOVERY_INCOMPLETE in result.risks
    assert ExecutiveControlRecommendation.KEEP_RECOVERY_ACTIVE in result.recommendations


def test_systemic_control_collapse_locks_executive_control():
    data = CognitiveExecutiveControlInput(
        system_integrity=ns(status="COMPROMISED", integrity_score=10, risks=("SAFETY_LOCKDOWN_REQUIRED",)),
        cognitive_stability=ns(state="COLLAPSING", cognitive_stability_score=10, risks=()),
        cognitive_consensus=ns(state="CONSENSUS_LOCKED", cognitive_consensus_score=10, risks=("SYSTEMIC_CONSENSUS_COLLAPSE",)),
        cognitive_memory_consolidation=ns(state="MEMORY_LOCKED", memory_consolidation_score=10, risks=("MEMORY_CORRUPTION_RISK",)),
        cognitive_governance=ns(mode="LOCKED_GOVERNANCE", autonomy_level="LOCKED_AUTONOMY", governance_score=10, risks=()),
        cognitive_policy=ns(mode="POLICY_LOCKED", cognitive_policy_score=10, decisions=("LOCKDOWN",), risks=()),
        intent_integrity=ns(state="INTENT_LOCKED", intent_integrity_score=10, risks=()),
    )

    result = evaluate_cognitive_executive_control(data)

    assert result.state == ExecutiveControlState.EXECUTIVE_CONTROL_LOCKED
    assert result.mode == ExecutiveControlMode.LOCKED_CONTROL
    assert ExecutiveControlRisk.SYSTEMIC_CONTROL_COLLAPSE in result.risks
    assert ExecutiveControlAction.LOCK_EXECUTIVE_CONTROL in result.actions
    assert result.decision_graph.locked is True


def test_score_penalizes_targeted_risks():
    stable = compute_executive_control_score(stable_input(), ())
    degraded = compute_executive_control_score(
        stable_input(),
        (
            ExecutiveControlRisk.POLICY_BLOCK_REQUIRED,
            ExecutiveControlRisk.ALIGNMENT_FAILURE,
            ExecutiveControlRisk.MEMORY_FAILURE,
        ),
    )

    assert degraded.policy_control_score < stable.policy_control_score
    assert degraded.alignment_control_score < stable.alignment_control_score
    assert degraded.memory_control_score < stable.memory_control_score


def test_directives_include_safe_mode_freezes_for_multiple_risks():
    score = compute_executive_control_score(stable_input(), ())
    directives = build_executive_directives(
        (
            ExecutiveControlRisk.ALIGNMENT_FAILURE,
            ExecutiveControlRisk.COHERENCE_FAILURE,
            ExecutiveControlRisk.CONSENSUS_FAILURE,
            ExecutiveControlRisk.MEMORY_FAILURE,
        ),
        score,
    )
    actions = {directive.action for directive in directives}

    assert ExecutiveControlAction.ENTER_SAFE_MODE in actions
    assert ExecutiveControlAction.FREEZE_LEARNING in actions
    assert ExecutiveControlAction.FREEZE_RECURSIVE_UPDATES in actions


def test_decision_graph_marks_blocked_nodes_and_safe_mode():
    directives = build_executive_directives(
        (ExecutiveControlRisk.POLICY_BLOCK_REQUIRED, ExecutiveControlRisk.CONSENSUS_FAILURE),
        compute_executive_control_score(stable_input(), ()),
    )
    graph = build_executive_decision_graph(
        directives,
        (ExecutiveControlRisk.POLICY_BLOCK_REQUIRED, ExecutiveControlRisk.CONSENSUS_FAILURE),
    )

    assert "policy" in graph.blocked_nodes
    assert "consensus" in graph.blocked_nodes
    assert graph.nodes
    assert graph.edges


def test_recommendations_map_to_risks():
    recommendations = generate_executive_control_recommendations(
        (
            ExecutiveControlRisk.POLICY_BLOCK_REQUIRED,
            ExecutiveControlRisk.ALIGNMENT_FAILURE,
            ExecutiveControlRisk.COHERENCE_FAILURE,
            ExecutiveControlRisk.CONSENSUS_FAILURE,
            ExecutiveControlRisk.INTENT_FAILURE,
            ExecutiveControlRisk.SYSTEMIC_CONTROL_COLLAPSE,
        )
    )

    assert ExecutiveControlRecommendation.ENFORCE_POLICY_BLOCKS in recommendations
    assert ExecutiveControlRecommendation.RECHECK_ALIGNMENT in recommendations
    assert ExecutiveControlRecommendation.RECHECK_COHERENCE in recommendations
    assert ExecutiveControlRecommendation.REBUILD_CONSENSUS in recommendations
    assert ExecutiveControlRecommendation.RESTORE_INTENT_INTEGRITY in recommendations
    assert ExecutiveControlRecommendation.MAINTAIN_EXECUTIVE_LOCK in recommendations


def test_markdown_contains_required_sections():
    result = evaluate_cognitive_executive_control(stable_input())

    markdown = render_cognitive_executive_control_markdown(result)

    assert "# Cognitive Executive Control State" in markdown
    assert "# Executive Control Score" in markdown
    assert "# Directives" in markdown
    assert "# Decision Graph" in markdown
    assert "# Risks" in markdown
    assert "# Actions" in markdown
    assert "# Recommendations" in markdown
    assert "# AGIcore Executive Control Outlook" in markdown
