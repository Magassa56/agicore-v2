from types import SimpleNamespace

from agicore.trading.cognitive_safety_orchestrator import (
    build_safety_coordination_graph,
    build_safety_directives,
    build_safety_stabilization_plan,
    compute_safety_orchestrator_score,
    detect_cascade_risks,
    detect_safety_orchestrator_risks,
    evaluate_cognitive_safety_orchestrator,
    generate_safety_orchestrator_recommendations,
    render_cognitive_safety_orchestrator_markdown,
)
from agicore.trading.cognitive_safety_orchestrator_models import (
    CognitiveSafetyOrchestratorInput,
    SafetyOrchestratorAction,
    SafetyOrchestratorMode,
    SafetyOrchestratorRecommendation,
    SafetyOrchestratorRisk,
    SafetyOrchestratorState,
)


def ns(**kwargs):
    return SimpleNamespace(**kwargs)


def stable_input():
    return CognitiveSafetyOrchestratorInput(
        cognitive_executive_control=ns(state="EXECUTIVE_CONTROL_STABLE", executive_control_score=90, actions=(), risks=()),
        cognitive_priority_arbitration=ns(state="PRIORITY_ARBITRATION_STABLE", priority_arbitration_score=90, risks=()),
        cognitive_consensus=ns(state="CONSENSUS_REACHED", cognitive_consensus_score=90, risks=()),
        cognitive_coherence=ns(state="COHERENT", cognitive_coherence_score=90, risks=()),
        cognitive_alignment=ns(state="FULLY_ALIGNED", cognitive_alignment_score=90, risks=()),
        cognitive_memory_consolidation=ns(state="MEMORY_CONSOLIDATED", memory_consolidation_score=90, risks=()),
        intent_integrity=ns(state="INTENT_INTACT", intent_integrity_score=90, risks=()),
        cognitive_identity=ns(state="IDENTITY_STABLE", cognitive_identity_score=90, risks=()),
        cognitive_continuity=ns(state="CONTINUOUS", cognitive_continuity_score=90, risks=()),
        cognitive_recovery=ns(state="RECOVERED", cognitive_recovery_score=90, risks=()),
        cognitive_resilience=ns(state="RESILIENT", cognitive_resilience_score=90, risks=()),
        cognitive_stability=ns(state="STABLE", cognitive_stability_score=90, risks=()),
        cognitive_policy=ns(mode="POLICY_NORMAL", cognitive_policy_score=90, risks=()),
        cognitive_governance=ns(mode="NORMAL_GOVERNANCE", governance_score=90, risks=()),
        self_reflection_audit=ns(state="CLEAR_REFLECTION", reflection_quality_score=90, risks=()),
        recursive_world_model=ns(decision="MAINTAIN_WORLD_MODEL", world_model_coherence_score=90, risks=()),
        system_integrity=ns(status="HEALTHY", integrity_score=90, risks=()),
        mission_continuity=ns(mode="FULL_OPERATION", continuity_score=90, risks=()),
        requested_operation="monitor",
    )


def test_evaluate_safety_orchestrator_stable_state():
    result = evaluate_cognitive_safety_orchestrator(stable_input())

    assert result.state == SafetyOrchestratorState.SAFETY_ORCHESTRATOR_STABLE
    assert result.mode == SafetyOrchestratorMode.NORMAL_SAFETY_MODE
    assert result.safety_orchestrator_score >= 80
    assert result.risks == ()
    assert result.coordination_graph.safe_mode_active is False


def test_detects_executive_and_priority_failures():
    data = CognitiveSafetyOrchestratorInput(
        cognitive_executive_control=ns(state="EXECUTIVE_CONTROL_LOCKED", executive_control_score=20, actions=("LOCK_EXECUTIVE_CONTROL",), risks=()),
        cognitive_priority_arbitration=ns(state="PRIORITY_ARBITRATION_DEGRADED", priority_arbitration_score=35, risks=()),
    )

    risks = detect_safety_orchestrator_risks(data)

    assert SafetyOrchestratorRisk.EXECUTIVE_CONTROL_FAILURE in risks
    assert SafetyOrchestratorRisk.PRIORITY_ARBITRATION_FAILURE in risks


def test_alignment_and_coherence_breakdown_activate_protection():
    data = CognitiveSafetyOrchestratorInput(
        cognitive_alignment=ns(state="SYSTEMIC_MISALIGNMENT", cognitive_alignment_score=30, risks=()),
        cognitive_coherence=ns(state="LOGICAL_CONFLICT", cognitive_coherence_score=30, risks=()),
        cognitive_stability=ns(state="UNSTABLE", cognitive_stability_score=35, risks=()),
    )

    result = evaluate_cognitive_safety_orchestrator(data)

    assert SafetyOrchestratorRisk.ALIGNMENT_BREAKDOWN in result.risks
    assert SafetyOrchestratorRisk.COHERENCE_COLLAPSE in result.risks
    assert SafetyOrchestratorAction.ACTIVATE_GLOBAL_SAFE_MODE in result.actions
    assert SafetyOrchestratorAction.BLOCK_HIGH_RISK_DECISIONS in result.actions


def test_memory_corruption_spread_protects_memory_system():
    data = CognitiveSafetyOrchestratorInput(
        cognitive_memory_consolidation=ns(
            state="MEMORY_LOCKED",
            memory_consolidation_score=20,
            risks=("MEMORY_CORRUPTION_RISK",),
        )
    )

    result = evaluate_cognitive_safety_orchestrator(data)

    assert SafetyOrchestratorRisk.MEMORY_CORRUPTION_SPREAD in result.risks
    assert SafetyOrchestratorAction.PROTECT_MEMORY_SYSTEM in result.actions
    assert result.stabilization_plan.protected_memory is True


def test_recovery_failure_maintains_recovery_pipeline():
    data = CognitiveSafetyOrchestratorInput(
        cognitive_recovery=ns(state="FAILED_RECOVERY", cognitive_recovery_score=20, risks=()),
        cognitive_resilience=ns(state="CRITICAL", cognitive_resilience_score=30, risks=()),
    )

    result = evaluate_cognitive_safety_orchestrator(data)

    assert result.state == SafetyOrchestratorState.SAFETY_ORCHESTRATOR_RECOVERING
    assert result.mode == SafetyOrchestratorMode.RECOVERY_PROTECTION_MODE
    assert SafetyOrchestratorRisk.RECOVERY_FAILURE in result.risks
    assert SafetyOrchestratorAction.MAINTAIN_RECOVERY_PIPELINE in result.actions


def test_policy_governance_drift_is_detected():
    data = CognitiveSafetyOrchestratorInput(
        cognitive_policy=ns(mode="POLICY_SAFE_MODE", cognitive_policy_score=45, risks=("GOVERNANCE_POLICY_MISMATCH",)),
        cognitive_governance=ns(mode="DEGRADED_GOVERNANCE", governance_score=45, risks=()),
    )

    risks = detect_safety_orchestrator_risks(data)

    assert SafetyOrchestratorRisk.POLICY_GOVERNANCE_DRIFT in risks


def test_unsafe_autonomous_action_is_blocked():
    data = CognitiveSafetyOrchestratorInput(
        requested_operation="execute",
        intent_integrity=ns(state="INTENT_CONFLICT", intent_integrity_score=30, risks=()),
    )

    result = evaluate_cognitive_safety_orchestrator(data)

    assert SafetyOrchestratorRisk.UNSAFE_AUTONOMOUS_ACTION in result.risks
    assert SafetyOrchestratorAction.REQUIRE_HUMAN_SUPERVISION in result.actions
    assert "autonomous_operations" in result.coordination_graph.blocked_components


def test_global_safety_collapse_locks_down_system():
    data = CognitiveSafetyOrchestratorInput(
        cognitive_executive_control=ns(state="EXECUTIVE_CONTROL_LOCKED", executive_control_score=10, actions=("LOCK_EXECUTIVE_CONTROL",), risks=()),
        cognitive_priority_arbitration=ns(state="PRIORITY_ARBITRATION_LOCKED", priority_arbitration_score=10, risks=()),
        cognitive_consensus=ns(state="CONSENSUS_LOCKED", cognitive_consensus_score=10, risks=()),
        cognitive_coherence=ns(state="COHERENCE_LOCKED", cognitive_coherence_score=10, risks=()),
        cognitive_alignment=ns(state="ALIGNMENT_LOCKED", cognitive_alignment_score=10, risks=()),
        cognitive_memory_consolidation=ns(state="MEMORY_LOCKED", memory_consolidation_score=10, risks=("MEMORY_CORRUPTION_RISK",)),
        intent_integrity=ns(state="INTENT_CORRUPTED", intent_integrity_score=10, risks=()),
        cognitive_recovery=ns(state="FAILED_RECOVERY", cognitive_recovery_score=10, risks=()),
        cognitive_resilience=ns(state="CRITICAL", cognitive_resilience_score=10, risks=()),
        cognitive_stability=ns(state="COLLAPSING", cognitive_stability_score=10, risks=()),
        cognitive_policy=ns(mode="POLICY_LOCKED", cognitive_policy_score=10, risks=("GOVERNANCE_POLICY_MISMATCH",)),
        cognitive_governance=ns(mode="LOCKED_GOVERNANCE", governance_score=10, risks=()),
        recursive_world_model=ns(decision="ENTER_WORLD_MODEL_SAFE_MODE", world_model_coherence_score=10, risks=()),
        system_integrity=ns(status="COMPROMISED", integrity_score=10, risks=()),
        requested_operation="execute",
    )

    result = evaluate_cognitive_safety_orchestrator(data)

    assert result.state == SafetyOrchestratorState.SAFETY_ORCHESTRATOR_LOCKDOWN
    assert result.mode == SafetyOrchestratorMode.FULL_SAFETY_LOCK_MODE
    assert SafetyOrchestratorRisk.GLOBAL_SAFETY_COLLAPSE in result.risks
    assert SafetyOrchestratorAction.LOCKDOWN_SYSTEM in result.actions
    assert result.coordination_graph.lockdown_active is True


def test_score_penalizes_targeted_risks():
    stable = compute_safety_orchestrator_score(stable_input(), ())
    degraded = compute_safety_orchestrator_score(
        stable_input(),
        (
            SafetyOrchestratorRisk.EXECUTIVE_CONTROL_FAILURE,
            SafetyOrchestratorRisk.MEMORY_CORRUPTION_SPREAD,
            SafetyOrchestratorRisk.RECOVERY_FAILURE,
        ),
    )

    assert degraded.executive_safety_score < stable.executive_safety_score
    assert degraded.memory_safety_score < stable.memory_safety_score
    assert degraded.recovery_resilience_score < stable.recovery_resilience_score


def test_cascade_risks_explain_cross_layer_propagation():
    risks = (
        SafetyOrchestratorRisk.MEMORY_CORRUPTION_SPREAD,
        SafetyOrchestratorRisk.COHERENCE_COLLAPSE,
        SafetyOrchestratorRisk.SYSTEMIC_CASCADE_RISK,
    )

    cascades = detect_cascade_risks(stable_input(), risks)

    assert any(cascade.cascade_id == "memory_to_continuity" for cascade in cascades)
    assert any(cascade.cascade_id == "reasoning_to_decision" for cascade in cascades)
    assert any(cascade.cascade_id == "systemic_cascade" for cascade in cascades)


def test_directives_graph_and_plan_coordinate_safe_mode():
    risks = (
        SafetyOrchestratorRisk.SYSTEMIC_CASCADE_RISK,
        SafetyOrchestratorRisk.MEMORY_CORRUPTION_SPREAD,
        SafetyOrchestratorRisk.UNSAFE_AUTONOMOUS_ACTION,
    )
    score = compute_safety_orchestrator_score(stable_input(), risks)
    directives = build_safety_directives(risks, score)
    cascades = detect_cascade_risks(stable_input(), risks)
    graph = build_safety_coordination_graph(stable_input(), directives, risks)
    plan = build_safety_stabilization_plan(directives, cascades, risks)

    assert SafetyOrchestratorAction.ACTIVATE_GLOBAL_SAFE_MODE in {directive.action for directive in directives}
    assert graph.safe_mode_active is True
    assert "autonomous_operations" in graph.blocked_components
    assert plan.human_supervision_required is True
    assert plan.protected_memory is True


def test_recommendations_map_to_risks():
    recommendations = generate_safety_orchestrator_recommendations(
        (
            SafetyOrchestratorRisk.EXECUTIVE_CONTROL_FAILURE,
            SafetyOrchestratorRisk.ALIGNMENT_BREAKDOWN,
            SafetyOrchestratorRisk.COHERENCE_COLLAPSE,
            SafetyOrchestratorRisk.POLICY_GOVERNANCE_DRIFT,
            SafetyOrchestratorRisk.MEMORY_CORRUPTION_SPREAD,
            SafetyOrchestratorRisk.RECOVERY_FAILURE,
            SafetyOrchestratorRisk.GLOBAL_SAFETY_COLLAPSE,
        )
    )

    assert SafetyOrchestratorRecommendation.RECHECK_EXECUTIVE_CONTROL in recommendations
    assert SafetyOrchestratorRecommendation.REBUILD_ALIGNMENT in recommendations
    assert SafetyOrchestratorRecommendation.STABILIZE_COGNITIVE_STATE in recommendations
    assert SafetyOrchestratorRecommendation.ENFORCE_POLICY_CONSISTENCY in recommendations
    assert SafetyOrchestratorRecommendation.PRESERVE_MEMORY_INTEGRITY in recommendations
    assert SafetyOrchestratorRecommendation.MAINTAIN_RECOVERY_OPERATIONS in recommendations
    assert SafetyOrchestratorRecommendation.KEEP_LOCKDOWN_ACTIVE in recommendations


def test_markdown_contains_required_sections():
    result = evaluate_cognitive_safety_orchestrator(stable_input())

    markdown = render_cognitive_safety_orchestrator_markdown(result)

    assert "# Cognitive Safety Orchestrator State" in markdown
    assert "# Safety Orchestrator Score" in markdown
    assert "# Safety Directives" in markdown
    assert "# Safety Coordination Graph" in markdown
    assert "# Cascade Risks" in markdown
    assert "# Stabilization Plan" in markdown
    assert "# Risks" in markdown
    assert "# Actions" in markdown
    assert "# Recommendations" in markdown
    assert "# AGIcore Safety Outlook" in markdown
