from types import SimpleNamespace

from agicore.trading.cognitive_constitutional import (
    build_constitutional_constraints,
    build_constitutional_hierarchy,
    compute_constitutional_score,
    detect_constitutional_risks,
    evaluate_cognitive_constitutional,
    generate_constitutional_directives,
    render_cognitive_constitutional_markdown,
)
from agicore.trading.cognitive_constitutional_models import (
    CognitiveConstitutionalInput,
    ConstitutionalDirective,
    ConstitutionalMode,
    ConstitutionalRecommendation,
    ConstitutionalRisk,
    ConstitutionalState,
)


def ns(**kwargs):
    return SimpleNamespace(**kwargs)


def stable_input():
    return CognitiveConstitutionalInput(
        cognitive_meta_supervision=ns(state="META_SUPERVISION_STABLE", meta_supervision_score=90, directives=(), risks=()),
        cognitive_recursive_regulation=ns(state="RECURSION_STABLE", recursive_regulation_score=90, risks=()),
        cognitive_safety_orchestrator=ns(state="SAFETY_ORCHESTRATOR_STABLE", mode="NORMAL_SAFETY_MODE", safety_orchestrator_score=90, directives=(), risks=()),
        cognitive_executive_control=ns(state="EXECUTIVE_CONTROL_STABLE", executive_control_score=90, actions=(), risks=()),
        cognitive_priority_arbitration=ns(state="PRIORITY_ARBITRATION_STABLE", priority_arbitration_score=90, risks=()),
        cognitive_consensus=ns(state="CONSENSUS_REACHED", cognitive_consensus_score=90, risks=()),
        cognitive_coherence=ns(state="COHERENT", cognitive_coherence_score=90, risks=()),
        cognitive_alignment=ns(state="FULLY_ALIGNED", cognitive_alignment_score=90, risks=()),
        intent_integrity=ns(state="INTENT_INTACT", intent_integrity_score=90, risks=()),
        cognitive_identity=ns(state="IDENTITY_STABLE", cognitive_identity_score=90, risks=()),
        recursive_world_model=ns(decision="MAINTAIN_WORLD_MODEL", world_model_coherence_score=90, risks=()),
        self_reflection_audit=ns(state="CLEAR_REFLECTION", reflection_quality_score=90, risks=()),
        cognitive_governance=ns(mode="NORMAL_GOVERNANCE", governance_score=90, risks=()),
        cognitive_policy=ns(mode="POLICY_NORMAL", cognitive_policy_score=90, risks=()),
        requested_operation="observe",
        requested_authority="ACTIONS",
    )


def test_evaluate_constitutional_stable_state():
    result = evaluate_cognitive_constitutional(stable_input())

    assert result.state == ConstitutionalState.CONSTITUTION_INTACT
    assert result.mode == ConstitutionalMode.NORMAL_CONSTITUTIONAL_MODE
    assert result.constitutional_score >= 85
    assert result.risks == ()
    assert result.constitutional_veto_active is False


def test_detects_constitutional_violation_and_veto():
    data = CognitiveConstitutionalInput(requested_operation="override_safety")

    result = evaluate_cognitive_constitutional(data)

    assert ConstitutionalRisk.CONSTITUTIONAL_VIOLATION in result.risks
    assert result.state == ConstitutionalState.CONSTITUTIONAL_VETO_ACTIVE
    assert result.mode == ConstitutionalMode.SAFETY_VETO_MODE
    assert ConstitutionalDirective.ACTIVATE_CONSTITUTIONAL_VETO in result.directives
    assert result.constitutional_veto_active is True


def test_blocks_safety_override_attempt():
    data = CognitiveConstitutionalInput(
        requested_operation="execute",
        cognitive_safety_orchestrator=ns(
            state="SAFETY_ORCHESTRATOR_PROTECTING",
            mode="SAFE_MODE_COORDINATION",
            safety_orchestrator_score=60,
            directives=("BLOCK_HIGH_RISK_DECISIONS",),
            risks=(),
        ),
    )

    result = evaluate_cognitive_constitutional(data)

    assert ConstitutionalRisk.SAFETY_OVERRIDE_ATTEMPT in result.risks
    assert ConstitutionalDirective.BLOCK_SAFETY_OVERRIDE in result.directives
    assert "autonomous_action" in result.constraints.blocked_operations


def test_blocks_unsafe_autonomy_expansion():
    data = CognitiveConstitutionalInput(
        requested_operation="expand_autonomy",
        cognitive_meta_supervision=ns(state="META_SUPERVISION_CRITICAL", meta_supervision_score=35, risks=(), directives=()),
    )

    result = evaluate_cognitive_constitutional(data)

    assert ConstitutionalRisk.UNSAFE_AUTONOMY_EXPANSION in result.risks
    assert ConstitutionalDirective.FREEZE_AUTONOMY_EXPANSION in result.directives
    assert result.constraints.autonomy_expansion_allowed is False


def test_detects_identity_corruption():
    data = CognitiveConstitutionalInput(
        cognitive_identity=ns(state="IDENTITY_FRAGMENTED", cognitive_identity_score=30, risks=())
    )

    risks = detect_constitutional_risks(data)

    assert ConstitutionalRisk.IDENTITY_CORRUPTION in risks


def test_detects_mission_drift():
    data = CognitiveConstitutionalInput(
        intent_integrity=ns(state="INTENT_DRIFT", intent_integrity_score=30, risks=()),
        cognitive_alignment=ns(state="STRATEGIC_MISALIGNMENT", cognitive_alignment_score=35, risks=()),
    )

    risks = detect_constitutional_risks(data)

    assert ConstitutionalRisk.MISSION_DRIFT in risks


def test_detects_rule_hierarchy_breakdown():
    data = CognitiveConstitutionalInput(
        cognitive_priority_arbitration=ns(
            state="PRIORITY_ARBITRATION_CONFLICTED",
            priority_arbitration_score=30,
            risks=("SAFETY_PRIORITY_LOSS",),
        )
    )

    risks = detect_constitutional_risks(data)

    assert ConstitutionalRisk.RULE_HIERARCHY_BREAKDOWN in risks


def test_detects_executive_power_escalation():
    data = CognitiveConstitutionalInput(
        requested_authority="EXECUTIVE",
        cognitive_safety_orchestrator=ns(mode="FULL_SAFETY_LOCK_MODE", state="SAFETY_ORCHESTRATOR_LOCKDOWN", safety_orchestrator_score=20, directives=(), risks=()),
        cognitive_executive_control=ns(state="EXECUTIVE_CONTROL_LOCKED", executive_control_score=20, actions=("ESCALATE_TO_HUMAN",), risks=()),
    )

    risks = detect_constitutional_risks(data)

    assert ConstitutionalRisk.EXECUTIVE_POWER_ESCALATION in risks


def test_detects_consensus_constitution_conflict():
    data = CognitiveConstitutionalInput(
        cognitive_consensus=ns(state="SYSTEMIC_CONFLICT", cognitive_consensus_score=25, risks=()),
        cognitive_alignment=ns(state="SYSTEMIC_MISALIGNMENT", cognitive_alignment_score=25, risks=()),
    )

    risks = detect_constitutional_risks(data)

    assert ConstitutionalRisk.CONSENSUS_CONSTITUTION_CONFLICT in risks


def test_detects_recursive_constitutional_instability():
    data = CognitiveConstitutionalInput(
        cognitive_recursive_regulation=ns(state="RECURSION_LOCKED", recursive_regulation_score=20, risks=("UNBOUNDED_REASONING_EXPANSION",)),
    )

    risks = detect_constitutional_risks(data)

    assert ConstitutionalRisk.RECURSIVE_CONSTITUTIONAL_INSTABILITY in risks


def test_detects_global_system_invariant_break_and_locks():
    data = CognitiveConstitutionalInput(
        requested_operation="execute",
        cognitive_safety_orchestrator=ns(state="SAFETY_ORCHESTRATOR_LOCKDOWN", mode="FULL_SAFETY_LOCK_MODE", safety_orchestrator_score=10, directives=("BLOCK_HIGH_RISK_DECISIONS",), risks=()),
        cognitive_identity=ns(state="IDENTITY_AT_RISK", cognitive_identity_score=10, risks=()),
        intent_integrity=ns(state="INTENT_CORRUPTED", intent_integrity_score=10, risks=()),
        cognitive_priority_arbitration=ns(state="PRIORITY_ARBITRATION_LOCKED", priority_arbitration_score=10, risks=("SAFETY_PRIORITY_LOSS",)),
        cognitive_recursive_regulation=ns(state="RECURSION_LOCKED", recursive_regulation_score=10, risks=("UNBOUNDED_REASONING_EXPANSION",)),
    )

    result = evaluate_cognitive_constitutional(data)

    assert ConstitutionalRisk.GLOBAL_SYSTEM_INVARIANT_BREAK in result.risks
    assert result.state == ConstitutionalState.CONSTITUTION_LOCKED
    assert result.mode == ConstitutionalMode.CONSTITUTIONAL_LOCKDOWN
    assert ConstitutionalDirective.LOCK_CONSTITUTIONAL_STATE in result.directives


def test_score_penalizes_constitutional_risks():
    stable = compute_constitutional_score(stable_input(), ())
    degraded = compute_constitutional_score(
        stable_input(),
        (
            ConstitutionalRisk.SAFETY_OVERRIDE_ATTEMPT,
            ConstitutionalRisk.IDENTITY_CORRUPTION,
            ConstitutionalRisk.MISSION_DRIFT,
        ),
    )

    assert degraded.safety_boundary_score < stable.safety_boundary_score
    assert degraded.identity_invariant_score < stable.identity_invariant_score
    assert degraded.mission_invariant_score < stable.mission_invariant_score
    assert degraded.overall_score < stable.overall_score


def test_hierarchy_enforces_constitution_over_safety_over_actions():
    hierarchy = build_constitutional_hierarchy()

    assert hierarchy.authority_order == ("CONSTITUTION", "SAFETY", "EXECUTIVE", "CONSENSUS", "ACTIONS")
    assert hierarchy.constitution_supreme is True
    assert hierarchy.veto_authority == "CONSTITUTION"
    assert hierarchy.rules[0].authority == "CONSTITUTION"


def test_constraints_protect_core_invariants_and_block_operations():
    risks = (
        ConstitutionalRisk.SAFETY_OVERRIDE_ATTEMPT,
        ConstitutionalRisk.UNSAFE_AUTONOMY_EXPANSION,
    )
    constraints = build_constitutional_constraints(
        CognitiveConstitutionalInput(requested_operation="expand_autonomy"),
        risks,
    )

    assert constraints.veto_active is True
    assert "safety_bypass" in constraints.blocked_operations
    assert "autonomy_expansion" in constraints.blocked_operations
    assert "capital_preservation" in constraints.protected_invariants


def test_directives_and_recommendations_cover_risks():
    result = evaluate_cognitive_constitutional(
        CognitiveConstitutionalInput(
            requested_operation="expand_autonomy",
            cognitive_meta_supervision=ns(state="META_SUPERVISION_CRITICAL", meta_supervision_score=20, risks=(), directives=()),
            cognitive_identity=ns(state="IDENTITY_AT_RISK", cognitive_identity_score=20, risks=()),
            intent_integrity=ns(state="INTENT_DRIFT", intent_integrity_score=20, risks=()),
            cognitive_consensus=ns(state="SYSTEMIC_CONFLICT", cognitive_consensus_score=20, risks=()),
            cognitive_priority_arbitration=ns(state="PRIORITY_ARBITRATION_CONFLICTED", priority_arbitration_score=20, risks=("SAFETY_PRIORITY_LOSS",)),
        )
    )

    assert ConstitutionalDirective.FREEZE_AUTONOMY_EXPANSION in result.directives
    assert ConstitutionalDirective.PROTECT_IDENTITY_INVARIANTS in result.directives
    assert ConstitutionalDirective.RESTORE_MISSION_ALIGNMENT in result.directives
    assert ConstitutionalDirective.REBUILD_RULE_HIERARCHY in result.directives
    assert ConstitutionalRecommendation.LIMIT_AUTONOMY_SCOPE in result.recommendations
    assert ConstitutionalRecommendation.PRESERVE_CORE_IDENTITY in result.recommendations


def test_markdown_contains_required_sections():
    result = evaluate_cognitive_constitutional(stable_input())

    markdown = render_cognitive_constitutional_markdown(result)

    assert "# Cognitive Constitutional State" in markdown
    assert "# Constitutional Score" in markdown
    assert "# Constitutional Hierarchy" in markdown
    assert "# Constitutional Constraints" in markdown
    assert "# Constitutional Risks" in markdown
    assert "# Constitutional Directives" in markdown
    assert "# Recommendations" in markdown
    assert "# AGIcore Constitutional Outlook" in markdown
