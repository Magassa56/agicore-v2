from __future__ import annotations

from types import SimpleNamespace

from agicore.trading.cognitive_governance_models import (
    CognitiveAutonomyLevel,
    CognitiveGovernanceDecision,
    CognitiveGovernanceMode,
    CognitiveGovernanceRisk,
    CognitivePermission,
)
from agicore.trading.cognitive_policy import (
    build_cognitive_policy_set,
    compute_policy_score,
    detect_policy_violations,
    enforce_policy_decisions,
    evaluate_cognitive_policies,
    generate_policy_actions,
    render_cognitive_policy_markdown,
)
from agicore.trading.cognitive_policy_models import (
    CognitivePolicyAction,
    CognitivePolicyDecision,
    CognitivePolicyMode,
    CognitivePolicyRisk,
    CognitivePolicyScope,
)
from agicore.trading.collective_consensus_models import ConsensusDecision, ConsensusMode
from agicore.trading.global_orchestrator_models import OrchestratorDecision, OrchestratorMode
from agicore.trading.intent_alignment_models import IntentAlignmentMode
from agicore.trading.learning_governance_models import LearningGovernanceDecision, LearningGovernanceMode
from agicore.trading.operational_awareness_models import OperationalHealthStatus
from agicore.trading.recursive_world_model_models import WorldModelDecision, WorldModelRisk
from agicore.trading.self_reflection_audit_models import CognitiveAuditRisk, ReflectionState
from agicore.trading.strategic_arbitration_models import ArbitrationDecision, ArbitrationMode
from agicore.trading.system_integrity_models import SystemIntegrityStatus


def _governance(
    mode=CognitiveGovernanceMode.NORMAL_GOVERNANCE,
    level=CognitiveAutonomyLevel.FULL_AUTONOMY,
    decision=CognitiveGovernanceDecision.APPROVE_COGNITIVE_OPERATION,
    permissions=(
        CognitivePermission.ALLOW_ANALYSIS,
        CognitivePermission.ALLOW_PLANNING,
        CognitivePermission.ALLOW_FORECASTING,
        CognitivePermission.ALLOW_STRATEGY_EVOLUTION,
        CognitivePermission.ALLOW_RECURSIVE_UPDATES,
        CognitivePermission.ALLOW_AUTONOMY_EXPANSION,
        CognitivePermission.ALLOW_EXECUTION_ROUTING,
        CognitivePermission.ALLOW_LEARNING_UPDATE,
        CognitivePermission.REQUIRE_AUDIT_TRACE,
    ),
    risks=(),
    score=82,
):
    return SimpleNamespace(
        mode=mode,
        autonomy_level=level,
        decision=decision,
        permissions=permissions,
        risks=risks,
        governance_score=score,
    )


def _audit(score=82, state=ReflectionState.CLEAR_REFLECTION, risks=()):
    return SimpleNamespace(reflection_quality_score=score, state=state, risks=risks)


def _world(score=82, decision=WorldModelDecision.MAINTAIN_WORLD_MODEL, risks=()):
    return SimpleNamespace(world_model_coherence_score=score, decision=decision, risks=risks)


def _orchestrator(decision=OrchestratorDecision.CONTINUE_COORDINATED_OPERATION, mode=OrchestratorMode.COORDINATED_OPERATION):
    return SimpleNamespace(decision=decision, system_state=SimpleNamespace(mode=mode))


def _arbitration(decision=ArbitrationDecision.CONTINUE_OPERATION, mode=ArbitrationMode.NORMAL_OPERATION):
    return SimpleNamespace(decision=decision, mode=mode)


def _consensus(decision=ConsensusDecision.APPROVE_COLLECTIVE_DECISION, mode=ConsensusMode.NORMAL_CONSENSUS):
    return SimpleNamespace(decision=decision, mode=mode)


def _intent(mode=IntentAlignmentMode.FULLY_ALIGNED, confidence=82):
    return SimpleNamespace(mode=mode, alignment_confidence=confidence)


def _learning(decision=LearningGovernanceDecision.ALLOW_LEARNING, mode=LearningGovernanceMode.LEARN):
    return SimpleNamespace(decision=decision, mode=mode)


def _integrity(status=SystemIntegrityStatus.HEALTHY, score=82):
    return SimpleNamespace(status=status, integrity_score=score)


def _awareness(health=OperationalHealthStatus.HEALTHY):
    return SimpleNamespace(health_status=health)


def test_builds_normal_policy_set_when_governance_is_healthy() -> None:
    policy_set = build_cognitive_policy_set(
        cognitive_governance=_governance(),
        self_reflection_audit=_audit(),
        recursive_world_model=_world(),
        learning_governance=_learning(),
        system_integrity=_integrity(),
    )

    assert policy_set.mode == CognitivePolicyMode.POLICY_NORMAL
    assert CognitivePolicyScope.ANALYSIS in policy_set.allowed_scopes
    assert CognitivePolicyScope.AUTONOMY_EXPANSION in policy_set.allowed_scopes
    assert CognitivePolicyScope.EXECUTION_ROUTING in policy_set.allowed_scopes


def test_restricts_autonomy_expansion_when_governance_is_restrictive() -> None:
    result = evaluate_cognitive_policies(
        cognitive_governance=_governance(
            CognitiveGovernanceMode.RESTRICTED_GOVERNANCE,
            CognitiveAutonomyLevel.SUPERVISED_AUTONOMY,
            CognitiveGovernanceDecision.DENY_AUTONOMY_EXPANSION,
            permissions=(CognitivePermission.ALLOW_ANALYSIS, CognitivePermission.REQUIRE_AUDIT_TRACE),
        ),
        intent_alignment=_intent(IntentAlignmentMode.AUTONOMY_DRIFT, 45),
    )

    assert result.mode == CognitivePolicyMode.POLICY_RESTRICTED
    assert CognitivePolicyScope.AUTONOMY_EXPANSION in result.policy_set.denied_scopes
    assert CognitivePolicyAction.REDUCE_AUTONOMY in result.enforced_actions


def test_requires_audit_trace_when_self_reflection_is_weak() -> None:
    result = evaluate_cognitive_policies(
        cognitive_governance=_governance(),
        self_reflection_audit=_audit(35, ReflectionState.AUDIT_REQUIRED, (CognitiveAuditRisk.INCOMPLETE_TRACEABILITY,)),
    )

    assert result.mode == CognitivePolicyMode.POLICY_AUDIT_REQUIRED
    assert CognitivePolicyScope.SELF_REFLECTION in result.policy_set.audit_required_scopes
    assert CognitivePolicyAction.REQUIRE_TRACEABILITY in result.enforced_actions


def test_protects_world_model_when_coherence_is_low() -> None:
    result = evaluate_cognitive_policies(
        cognitive_governance=_governance(),
        recursive_world_model=_world(35, WorldModelDecision.ENTER_WORLD_MODEL_SAFE_MODE, (WorldModelRisk.WORLD_MODEL_INCOHERENCE,)),
    )

    assert result.mode == CognitivePolicyMode.POLICY_WORLD_MODEL_PROTECTED
    assert CognitivePolicyScope.RECURSIVE_WORLD_MODEL in result.policy_set.frozen_scopes
    assert CognitivePolicyAction.PROTECT_WORLD_MODEL in result.enforced_actions


def test_freezes_learning_when_learning_governance_blocks_updates() -> None:
    result = evaluate_cognitive_policies(
        cognitive_governance=_governance(),
        learning_governance=_learning(LearningGovernanceDecision.FREEZE_POLICY_UPDATE, LearningGovernanceMode.FREEZE_LEARNING),
    )

    assert result.mode == CognitivePolicyMode.POLICY_LEARNING_FROZEN
    assert CognitivePolicyScope.LEARNING in result.policy_set.frozen_scopes
    assert CognitivePolicyAction.FREEZE_LEARNING in result.enforced_actions


def test_denies_execution_routing_when_integrity_is_critical() -> None:
    result = evaluate_cognitive_policies(
        cognitive_governance=_governance(),
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 20),
        operational_awareness=_awareness(OperationalHealthStatus.CRITICAL),
    )

    assert result.mode == CognitivePolicyMode.POLICY_LOCKED
    assert CognitivePolicyScope.EXECUTION_ROUTING in result.policy_set.denied_scopes
    assert CognitivePolicyAction.DENY_HIGH_RISK_ACTION in result.enforced_actions
    assert CognitivePolicyAction.REQUIRE_HUMAN_REVIEW in result.enforced_actions


def test_detects_policy_conflict_between_arbitration_and_consensus() -> None:
    result = evaluate_cognitive_policies(
        cognitive_governance=_governance(),
        strategic_arbitration=_arbitration(ArbitrationDecision.ENABLE_SAFE_MODE, ArbitrationMode.SAFE_COORDINATION),
        collective_consensus=_consensus(ConsensusDecision.APPROVE_COLLECTIVE_DECISION, ConsensusMode.NORMAL_CONSENSUS),
    )

    assert CognitivePolicyRisk.POLICY_CONFLICT in result.risks
    assert CognitivePolicyAction.ENTER_SAFE_MODE in result.enforced_actions


def test_detect_policy_violations_catches_forced_unsafe_policy_set() -> None:
    policy_set = build_cognitive_policy_set(cognitive_governance=_governance())
    forced_rules = tuple(
        rule
        if rule.scope != CognitivePolicyScope.AUTONOMY_EXPANSION
        else type(rule)(rule.rule_id, rule.scope, CognitivePolicyDecision.ALLOW, rule.actions, rule.restrictions, rule.reason, rule.priority)
        for rule in policy_set.rules
    )
    forced_set = type(policy_set)(
        CognitivePolicyMode.POLICY_NORMAL,
        forced_rules,
        (CognitivePolicyScope.AUTONOMY_EXPANSION,),
        (),
        (),
        (),
        (),
    )
    violations = detect_policy_violations(
        cognitive_governance=_governance(
            CognitiveGovernanceMode.RESTRICTED_GOVERNANCE,
            CognitiveAutonomyLevel.LIMITED_AUTONOMY,
            CognitiveGovernanceDecision.DENY_AUTONOMY_EXPANSION,
        ),
        policy_set=forced_set,
    )

    assert any(violation.risk == CognitivePolicyRisk.AUTONOMY_POLICY_DRIFT for violation in violations)


def test_compute_policy_score_penalizes_high_severity_violations() -> None:
    violations = (
        SimpleNamespace(risk=CognitivePolicyRisk.EXECUTION_ROUTING_UNSAFE, severity_score=90),
        SimpleNamespace(risk=CognitivePolicyRisk.MISSING_AUDIT_TRACE, severity_score=75),
    )
    score = compute_policy_score(
        cognitive_governance=_governance(score=55),
        self_reflection_audit=_audit(40),
        recursive_world_model=_world(80),
        violations=violations,
    )

    assert score.governance_alignment_score == 55
    assert score.audit_trace_score < 40
    assert score.execution_safety_score < 60
    assert score.policy_consistency_score < 50


def test_generate_policy_actions_combines_controls() -> None:
    actions = generate_policy_actions(
        cognitive_governance=_governance(
            CognitiveGovernanceMode.SAFE_GOVERNANCE,
            CognitiveAutonomyLevel.OBSERVE_ONLY,
            CognitiveGovernanceDecision.ENFORCE_SAFE_GOVERNANCE,
            permissions=(CognitivePermission.ALLOW_ANALYSIS, CognitivePermission.REQUIRE_AUDIT_TRACE),
        ),
        self_reflection_audit=_audit(30, ReflectionState.CRITICAL_REVIEW),
        recursive_world_model=_world(30, WorldModelDecision.FREEZE_RECURSIVE_UPDATES, (WorldModelRisk.RECURSIVE_FEEDBACK_LOOP,)),
        learning_governance=_learning(LearningGovernanceDecision.ENTER_SAFETY_LOCKDOWN, LearningGovernanceMode.SAFETY_LOCKDOWN),
        global_orchestrator=_orchestrator(OrchestratorDecision.ENTER_SAFE_GLOBAL_MODE, OrchestratorMode.SAFE_GLOBAL_MODE),
    )

    assert CognitivePolicyAction.REQUIRE_TRACEABILITY in actions
    assert CognitivePolicyAction.PROTECT_WORLD_MODEL in actions
    assert CognitivePolicyAction.FREEZE_LEARNING in actions
    assert CognitivePolicyAction.ENTER_SAFE_MODE in actions


def test_render_cognitive_policy_markdown_contains_required_sections() -> None:
    result = evaluate_cognitive_policies(
        cognitive_governance=_governance(),
        self_reflection_audit=_audit(),
        recursive_world_model=_world(),
        learning_governance=_learning(),
    )
    markdown = render_cognitive_policy_markdown(result)

    assert "Cognitive Policy State" in markdown
    assert "Policy Mode" in markdown
    assert "Policy Rules" in markdown
    assert "Violations" in markdown
    assert "Decisions" in markdown
    assert "Enforced Actions" in markdown
    assert "Policy Score" in markdown
    assert "Recommendations" in markdown
    assert "AGIcore Policy Outlook" in markdown
