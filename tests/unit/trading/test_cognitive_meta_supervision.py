from types import SimpleNamespace

from agicore.trading.cognitive_meta_supervision import (
    build_global_cognitive_state,
    build_meta_supervision_graph,
    compute_meta_supervision_score,
    detect_meta_supervision_risks,
    evaluate_cognitive_meta_supervision,
    generate_meta_supervision_directives,
    render_cognitive_meta_supervision_markdown,
)
from agicore.trading.cognitive_meta_supervision_models import (
    CognitiveMetaSupervisionInput,
    MetaSupervisionDirective,
    MetaSupervisionMode,
    MetaSupervisionRecommendation,
    MetaSupervisionRisk,
    MetaSupervisionState,
)


def ns(**kwargs):
    return SimpleNamespace(**kwargs)


def stable_input():
    return CognitiveMetaSupervisionInput(
        cognitive_safety_orchestrator=ns(
            state="SAFETY_ORCHESTRATOR_STABLE",
            mode="NORMAL_SAFETY_MODE",
            safety_orchestrator_score=90,
            directives=(),
            risks=(),
        ),
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
        requested_operation="observe",
    )


def test_evaluate_meta_supervision_stable_state():
    result = evaluate_cognitive_meta_supervision(stable_input())

    assert result.state == MetaSupervisionState.META_SUPERVISION_STABLE
    assert result.mode == MetaSupervisionMode.NORMAL_META_SUPERVISION
    assert result.meta_supervision_score >= 80
    assert result.risks == ()
    assert result.global_state.autonomy_allowed is True


def test_detects_recursive_instability():
    data = CognitiveMetaSupervisionInput(
        cognitive_stability=ns(state="COLLAPSING", cognitive_stability_score=20, risks=("RUNAWAY_RECURSION",)),
        recursive_world_model=ns(decision="FREEZE_RECURSIVE_UPDATES", world_model_coherence_score=40, risks=()),
    )

    risks = detect_meta_supervision_risks(data)

    assert MetaSupervisionRisk.RECURSIVE_INSTABILITY in risks


def test_detects_meta_cognitive_collapse_and_lockdown():
    data = CognitiveMetaSupervisionInput(
        cognitive_safety_orchestrator=ns(state="SAFETY_ORCHESTRATOR_LOCKDOWN", safety_orchestrator_score=10, directives=(), risks=()),
        cognitive_executive_control=ns(state="EXECUTIVE_CONTROL_LOCKED", executive_control_score=10, actions=("LOCK_EXECUTIVE_CONTROL",), risks=()),
    )

    result = evaluate_cognitive_meta_supervision(data)

    assert MetaSupervisionRisk.META_COGNITIVE_COLLAPSE in result.risks
    assert result.state == MetaSupervisionState.META_SUPERVISION_LOCKDOWN
    assert result.mode == MetaSupervisionMode.META_LOCKDOWN_MODE
    assert MetaSupervisionDirective.ENTER_META_LOCKDOWN in result.directives


def test_detects_system_fragmentation_from_many_degraded_engines():
    data = CognitiveMetaSupervisionInput(
        cognitive_consensus=ns(state="CONSENSUS_FRAGMENTED", cognitive_consensus_score=35, risks=()),
        cognitive_coherence=ns(state="LOGICAL_CONFLICT", cognitive_coherence_score=35, risks=()),
        cognitive_alignment=ns(state="SYSTEMIC_MISALIGNMENT", cognitive_alignment_score=35, risks=()),
        cognitive_identity=ns(state="IDENTITY_FRAGMENTED", cognitive_identity_score=35, risks=()),
        cognitive_policy=ns(mode="POLICY_RESTRICTED", cognitive_policy_score=45, risks=()),
    )

    result = evaluate_cognitive_meta_supervision(data)

    assert MetaSupervisionRisk.SYSTEM_FRAGMENTATION in result.risks
    assert result.state == MetaSupervisionState.META_SUPERVISION_FRAGMENTED
    assert MetaSupervisionDirective.REBUILD_GLOBAL_COHERENCE in result.directives


def test_detects_unsafe_autonomy_escalation():
    data = CognitiveMetaSupervisionInput(
        requested_operation="expand_autonomy",
        cognitive_executive_control=ns(state="EXECUTIVE_CONTROL_RESTRICTED", executive_control_score=50, actions=("REDUCE_AUTONOMY",), risks=()),
    )

    risks = detect_meta_supervision_risks(data)

    assert MetaSupervisionRisk.UNSAFE_AUTONOMY_ESCALATION in risks


def test_detects_world_model_drift():
    data = CognitiveMetaSupervisionInput(
        recursive_world_model=ns(
            decision="REBUILD_CAUSAL_GRAPH",
            world_model_coherence_score=35,
            risks=("WORLD_MODEL_INCOHERENCE",),
        )
    )

    risks = detect_meta_supervision_risks(data)

    assert MetaSupervisionRisk.WORLD_MODEL_DRIFT in risks


def test_detects_executive_deadlock():
    data = CognitiveMetaSupervisionInput(
        cognitive_executive_control=ns(state="EXECUTIVE_CONTROL_LOCKED", executive_control_score=20, actions=(), risks=()),
        cognitive_priority_arbitration=ns(state="PRIORITY_ARBITRATION_CRITICAL", priority_arbitration_score=20, risks=()),
    )

    risks = detect_meta_supervision_risks(data)

    assert MetaSupervisionRisk.EXECUTIVE_DEADLOCK in risks


def test_detects_consensus_breakdown():
    data = CognitiveMetaSupervisionInput(
        cognitive_consensus=ns(state="SYSTEMIC_CONFLICT", cognitive_consensus_score=20, risks=())
    )

    risks = detect_meta_supervision_risks(data)

    assert MetaSupervisionRisk.CONSENSUS_BREAKDOWN in risks


def test_detects_safety_bypass_attempt():
    data = CognitiveMetaSupervisionInput(
        requested_operation="execute",
        cognitive_safety_orchestrator=ns(
            state="SAFETY_ORCHESTRATOR_PROTECTING",
            mode="SAFE_MODE_COORDINATION",
            safety_orchestrator_score=60,
            directives=("BLOCK_HIGH_RISK_DECISIONS",),
            risks=(),
        ),
    )

    result = evaluate_cognitive_meta_supervision(data)

    assert MetaSupervisionRisk.SAFETY_BYPASS_ATTEMPT in result.risks
    assert result.mode == MetaSupervisionMode.SAFETY_OVERRIDE_MONITORING
    assert MetaSupervisionDirective.ENFORCE_SAFETY_ORCHESTRATOR in result.directives


def test_detects_identity_dissolution():
    data = CognitiveMetaSupervisionInput(
        cognitive_identity=ns(state="IDENTITY_AT_RISK", cognitive_identity_score=30, risks=()),
        intent_integrity=ns(state="INTENT_CORRUPTED", intent_integrity_score=30, risks=()),
    )

    risks = detect_meta_supervision_risks(data)

    assert MetaSupervisionRisk.IDENTITY_DISSOLUTION in risks


def test_detects_emergent_behavior_risk_from_multiple_macro_risks():
    data = CognitiveMetaSupervisionInput(
        cognitive_safety_orchestrator=ns(state="SAFETY_ORCHESTRATOR_CRITICAL", safety_orchestrator_score=25, directives=(), risks=()),
        cognitive_stability=ns(state="COLLAPSING", cognitive_stability_score=20, risks=("RUNAWAY_RECURSION",)),
        cognitive_consensus=ns(state="CONSENSUS_FRAGMENTED", cognitive_consensus_score=20, risks=()),
        cognitive_identity=ns(state="IDENTITY_AT_RISK", cognitive_identity_score=20, risks=()),
    )

    risks = detect_meta_supervision_risks(data)

    assert MetaSupervisionRisk.EMERGENT_BEHAVIOR_RISK in risks


def test_score_penalizes_risks():
    stable = compute_meta_supervision_score(stable_input(), ())
    degraded = compute_meta_supervision_score(
        stable_input(),
        (
            MetaSupervisionRisk.RECURSIVE_INSTABILITY,
            MetaSupervisionRisk.CONSENSUS_BREAKDOWN,
            MetaSupervisionRisk.IDENTITY_DISSOLUTION,
        ),
    )

    assert degraded.stability_score < stable.stability_score
    assert degraded.consensus_score < stable.consensus_score
    assert degraded.identity_score < stable.identity_score
    assert degraded.global_score < stable.global_score


def test_graph_and_global_state_report_critical_engines():
    risks = (MetaSupervisionRisk.SYSTEM_FRAGMENTATION,)
    graph = build_meta_supervision_graph(
        CognitiveMetaSupervisionInput(
            cognitive_consensus=ns(state="CONSENSUS_FRAGMENTED", cognitive_consensus_score=30, risks=()),
            cognitive_coherence=ns(state="LOGICAL_CONFLICT", cognitive_coherence_score=30, risks=()),
        ),
        risks,
    )
    global_state = build_global_cognitive_state(stable_input(), risks, graph)

    assert "consensus" in graph.critical_nodes
    assert "coherence" in graph.critical_nodes
    assert global_state.macro_state == "FRAGMENTED_COGNITIVE_SYSTEM"
    assert global_state.safety_enforced is True


def test_directives_and_recommendations_cover_all_required_risks():
    result = evaluate_cognitive_meta_supervision(
        CognitiveMetaSupervisionInput(
            requested_operation="execute",
            cognitive_safety_orchestrator=ns(
                state="SAFETY_ORCHESTRATOR_PROTECTING",
                mode="SAFE_MODE_COORDINATION",
                safety_orchestrator_score=55,
                directives=("BLOCK_HIGH_RISK_DECISIONS",),
                risks=(),
            ),
            cognitive_stability=ns(state="COLLAPSING", cognitive_stability_score=20, risks=("RUNAWAY_RECURSION",)),
            cognitive_consensus=ns(state="CONSENSUS_FRAGMENTED", cognitive_consensus_score=20, risks=()),
            recursive_world_model=ns(decision="REBUILD_CAUSAL_GRAPH", world_model_coherence_score=20, risks=("WORLD_MODEL_DRIFT",)),
            cognitive_identity=ns(state="IDENTITY_AT_RISK", cognitive_identity_score=20, risks=()),
        )
    )

    assert MetaSupervisionDirective.REDUCE_RECURSIVE_DEPTH in result.directives
    assert MetaSupervisionDirective.REBUILD_CONSENSUS_LAYER in result.directives
    assert MetaSupervisionDirective.RECHECK_WORLD_MODEL in result.directives
    assert MetaSupervisionDirective.ENFORCE_SAFETY_ORCHESTRATOR in result.directives
    assert MetaSupervisionRecommendation.REVIEW_EMERGENT_BEHAVIOR in result.recommendations


def test_markdown_contains_required_sections():
    result = evaluate_cognitive_meta_supervision(stable_input())

    markdown = render_cognitive_meta_supervision_markdown(result)

    assert "# Cognitive Meta-Supervision State" in markdown
    assert "# Meta-Supervision Score" in markdown
    assert "# Global Cognitive State" in markdown
    assert "# Meta-Supervision Graph" in markdown
    assert "# Risks" in markdown
    assert "# Directives" in markdown
    assert "# Recommendations" in markdown
    assert "# AGIcore Meta-Supervision Outlook" in markdown
