from types import SimpleNamespace

from agicore.trading.cognitive_priority_arbitration import (
    build_arbitration_decision_matrix,
    build_priority_hierarchy,
    compute_priority_arbitration_score,
    detect_priority_arbitration_risks,
    detect_priority_conflicts,
    evaluate_cognitive_priority_arbitration,
    generate_priority_arbitration_recommendations,
    render_cognitive_priority_arbitration_markdown,
    resolve_priority_conflicts,
)
from agicore.trading.cognitive_priority_arbitration_models import (
    CognitivePriorityArbitrationInput,
    PriorityArbitrationAction,
    PriorityArbitrationMode,
    PriorityArbitrationRecommendation,
    PriorityArbitrationRisk,
    PriorityArbitrationState,
)


def ns(**kwargs):
    return SimpleNamespace(**kwargs)


def stable_input():
    return CognitivePriorityArbitrationInput(
        cognitive_executive_control=ns(state="EXECUTIVE_CONTROL_STABLE", executive_control_score=90, risks=()),
        cognitive_memory_consolidation=ns(state="MEMORY_CONSOLIDATED", memory_consolidation_score=90, risks=()),
        cognitive_consensus=ns(state="CONSENSUS_REACHED", cognitive_consensus_score=90, risks=()),
        cognitive_coherence=ns(state="COHERENT", cognitive_coherence_score=90, risks=()),
        cognitive_alignment=ns(state="FULLY_ALIGNED", cognitive_alignment_score=90, risks=()),
        intent_integrity=ns(state="INTENT_INTACT", intent_integrity_score=90, risks=()),
        cognitive_identity=ns(state="IDENTITY_STABLE", cognitive_identity_score=90, risks=()),
        cognitive_continuity=ns(state="CONTINUOUS", cognitive_continuity_score=90, risks=()),
        cognitive_recovery=ns(state="RECOVERED", cognitive_recovery_score=90, risks=()),
        cognitive_resilience=ns(state="RESILIENT", cognitive_resilience_score=90, risks=()),
        cognitive_stability=ns(state="STABLE", cognitive_stability_score=90, risks=()),
        cognitive_policy=ns(mode="POLICY_NORMAL", cognitive_policy_score=90, risks=()),
        cognitive_governance=ns(mode="NORMAL_GOVERNANCE", autonomy_level="LIMITED_AUTONOMY", governance_score=90, risks=()),
        self_reflection_audit=ns(state="CLEAR_REFLECTION", reflection_quality_score=90, risks=()),
        recursive_world_model=ns(decision="MAINTAIN_WORLD_MODEL", world_model_coherence_score=90, risks=()),
        system_integrity=ns(status="HEALTHY", integrity_score=90, risks=()),
        mission_continuity=ns(mode="FULL_OPERATION", continuity_score=90, risks=()),
        requested_priority="performance",
    )


def test_evaluate_priority_arbitration_stable_safety_first():
    result = evaluate_cognitive_priority_arbitration(stable_input())

    assert result.state == PriorityArbitrationState.PRIORITY_ARBITRATION_STABLE
    assert result.mode == PriorityArbitrationMode.NORMAL_ARBITRATION
    assert result.priority_arbitration_score >= 80
    assert result.hierarchy.dominant_priority == "safety"
    assert result.risks == ()
    assert PriorityArbitrationAction.PRESERVE_SAFETY_PRIORITY in result.actions


def test_build_priority_hierarchy_keeps_safety_and_capital_dominant():
    hierarchy = build_priority_hierarchy(stable_input())
    names = [priority.name for priority in hierarchy.priorities]

    assert names.index("safety") < names.index("performance")
    assert names.index("capital_preservation") < names.index("autonomy_expansion")
    assert hierarchy.safety_dominant is True
    assert hierarchy.capital_protection_dominant is True


def test_detects_safety_priority_loss_when_performance_requested_under_degradation():
    data = CognitivePriorityArbitrationInput(
        system_integrity=ns(status="COMPROMISED", integrity_score=25, risks=()),
        cognitive_stability=ns(state="CRITICAL", cognitive_stability_score=25, risks=()),
        requested_priority="performance",
    )

    conflicts = detect_priority_conflicts(data)
    risks = detect_priority_arbitration_risks(data, conflicts)

    assert any(conflict.risk == PriorityArbitrationRisk.SAFETY_PRIORITY_LOSS for conflict in conflicts)
    assert PriorityArbitrationRisk.SAFETY_PRIORITY_LOSS in risks


def test_capital_preservation_dominates_autonomy_expansion():
    data = CognitivePriorityArbitrationInput(
        cognitive_policy=ns(mode="POLICY_RESTRICTED", cognitive_policy_score=45, risks=()),
        intent_integrity=ns(state="INTENT_CONFLICT", intent_integrity_score=35, risks=()),
        requested_priority="autonomy_expansion",
    )

    result = evaluate_cognitive_priority_arbitration(data)

    assert PriorityArbitrationRisk.CAPITAL_PROTECTION_FAILURE in result.risks
    assert PriorityArbitrationAction.PRIORITIZE_CAPITAL_PROTECTION in result.actions
    assert result.mode == PriorityArbitrationMode.CAPITAL_PRESERVATION_MODE


def test_executive_control_overrides_lower_priorities():
    data = CognitivePriorityArbitrationInput(
        cognitive_executive_control=ns(state="EXECUTIVE_CONTROL_RESTRICTED", executive_control_score=45, risks=()),
        requested_priority="performance",
    )

    result = evaluate_cognitive_priority_arbitration(data)

    assert result.state == PriorityArbitrationState.PRIORITY_ARBITRATION_ESCALATED
    assert result.mode == PriorityArbitrationMode.EXECUTIVE_OVERRIDE_MODE
    assert PriorityArbitrationRisk.EXECUTIVE_PRIORITY_CONFLICT in result.risks
    assert result.decision_matrix.executive_override_active is True


def test_recovery_priority_suppression_enters_recovery_mode_when_isolated():
    data = CognitivePriorityArbitrationInput(
        cognitive_recovery=ns(state="RECOVERING", cognitive_recovery_score=60, risks=()),
        requested_priority="performance",
    )

    result = evaluate_cognitive_priority_arbitration(data)

    assert result.state == PriorityArbitrationState.PRIORITY_ARBITRATION_RECOVERING
    assert result.mode == PriorityArbitrationMode.RECOVERY_PRIORITY_MODE
    assert PriorityArbitrationRisk.RECOVERY_PRIORITY_SUPPRESSION in result.risks
    assert PriorityArbitrationRecommendation.PRESERVE_RECOVERY_FLOW in result.recommendations


def test_policy_alignment_conflict_is_detected():
    data = CognitivePriorityArbitrationInput(
        cognitive_policy=ns(mode="POLICY_SAFE_MODE", cognitive_policy_score=45, risks=()),
        cognitive_alignment=ns(state="SYSTEMIC_MISALIGNMENT", cognitive_alignment_score=35, risks=()),
        requested_priority="performance",
    )

    risks = detect_priority_arbitration_risks(data)

    assert PriorityArbitrationRisk.POLICY_ALIGNMENT_CONFLICT in risks


def test_coherence_and_consensus_failures_block_lower_priority():
    data = CognitivePriorityArbitrationInput(
        cognitive_coherence=ns(state="LOGICAL_CONFLICT", cognitive_coherence_score=30, risks=()),
        cognitive_consensus=ns(state="CONSENSUS_FRAGMENTED", cognitive_consensus_score=30, risks=()),
        requested_priority="performance",
    )

    result = evaluate_cognitive_priority_arbitration(data)

    assert PriorityArbitrationRisk.COHERENCE_PRIORITY_DRIFT in result.risks
    assert PriorityArbitrationRisk.CONSENSUS_PRIORITY_FAILURE in result.risks
    assert PriorityArbitrationAction.BLOCK_NON_CRITICAL_ACTIONS in result.actions


def test_systemic_priority_collapse_locks_arbitration():
    data = CognitivePriorityArbitrationInput(
        cognitive_executive_control=ns(state="EXECUTIVE_CONTROL_LOCKED", executive_control_score=10, risks=()),
        system_integrity=ns(status="COMPROMISED", integrity_score=10, risks=()),
        cognitive_consensus=ns(state="CONSENSUS_LOCKED", cognitive_consensus_score=10, risks=()),
        cognitive_memory_consolidation=ns(state="MEMORY_LOCKED", memory_consolidation_score=10, risks=()),
        cognitive_stability=ns(state="COLLAPSING", cognitive_stability_score=10, risks=()),
        intent_integrity=ns(state="INTENT_CORRUPTED", intent_integrity_score=10, risks=()),
        requested_priority="performance",
    )

    result = evaluate_cognitive_priority_arbitration(data)

    assert result.state == PriorityArbitrationState.PRIORITY_ARBITRATION_LOCKED
    assert result.mode == PriorityArbitrationMode.LOCKED_ARBITRATION_MODE
    assert PriorityArbitrationRisk.SYSTEMIC_PRIORITY_COLLAPSE in result.risks
    assert PriorityArbitrationAction.LOCK_PRIORITY_SYSTEM in result.actions
    assert result.decision_matrix.locked is True


def test_score_penalizes_targeted_priority_risks():
    stable = compute_priority_arbitration_score(stable_input(), ())
    degraded = compute_priority_arbitration_score(
        stable_input(),
        (
            PriorityArbitrationRisk.SAFETY_PRIORITY_LOSS,
            PriorityArbitrationRisk.CAPITAL_PROTECTION_FAILURE,
            PriorityArbitrationRisk.POLICY_ALIGNMENT_CONFLICT,
        ),
    )

    assert degraded.safety_priority_score < stable.safety_priority_score
    assert degraded.capital_preservation_score < stable.capital_preservation_score
    assert degraded.policy_priority_score < stable.policy_priority_score


def test_resolutions_and_matrix_explain_conflict_outcome():
    data = CognitivePriorityArbitrationInput(
        system_integrity=ns(status="COMPROMISED", integrity_score=25, risks=()),
        requested_priority="performance",
    )
    hierarchy = build_priority_hierarchy(data)
    conflicts = detect_priority_conflicts(data, hierarchy)
    risks = detect_priority_arbitration_risks(data, conflicts)
    resolutions = resolve_priority_conflicts(conflicts)
    matrix = build_arbitration_decision_matrix(hierarchy, conflicts, resolutions, risks)

    assert resolutions
    assert any(resolution.winning_priority == "safety" for resolution in resolutions)
    assert matrix.safe_mode_required is True
    assert "high_risk_operations" in matrix.blocked_actions


def test_recommendations_map_to_risks():
    recommendations = generate_priority_arbitration_recommendations(
        (
            PriorityArbitrationRisk.EXECUTIVE_PRIORITY_CONFLICT,
            PriorityArbitrationRisk.PRIORITY_COLLISION,
            PriorityArbitrationRisk.RECOVERY_PRIORITY_SUPPRESSION,
            PriorityArbitrationRisk.POLICY_ALIGNMENT_CONFLICT,
            PriorityArbitrationRisk.COHERENCE_PRIORITY_DRIFT,
            PriorityArbitrationRisk.SYSTEMIC_PRIORITY_COLLAPSE,
        )
    )

    assert PriorityArbitrationRecommendation.RECHECK_EXECUTIVE_CONTROL in recommendations
    assert PriorityArbitrationRecommendation.REBUILD_PRIORITY_HIERARCHY in recommendations
    assert PriorityArbitrationRecommendation.PRESERVE_RECOVERY_FLOW in recommendations
    assert PriorityArbitrationRecommendation.ENFORCE_POLICY_ALIGNMENT in recommendations
    assert PriorityArbitrationRecommendation.STABILIZE_COGNITIVE_STATE in recommendations
    assert PriorityArbitrationRecommendation.MAINTAIN_SAFE_MODE in recommendations


def test_markdown_contains_required_sections():
    result = evaluate_cognitive_priority_arbitration(stable_input())

    markdown = render_cognitive_priority_arbitration_markdown(result)

    assert "# Cognitive Priority Arbitration State" in markdown
    assert "# Arbitration Score" in markdown
    assert "# Priority Hierarchy" in markdown
    assert "# Priority Conflicts" in markdown
    assert "# Priority Resolutions" in markdown
    assert "# Decision Matrix" in markdown
    assert "# Risks" in markdown
    assert "# Actions" in markdown
    assert "# Recommendations" in markdown
    assert "# AGIcore Priority Arbitration Outlook" in markdown
