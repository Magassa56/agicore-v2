from __future__ import annotations

from types import SimpleNamespace

from agicore.trading.cognitive_adaptation_models import CognitiveLoadLevel
from agicore.trading.cognitive_governance import (
    assess_autonomy_level,
    build_permission_set,
    compute_governance_score,
    detect_governance_risks,
    enforce_cognitive_policies,
    evaluate_cognitive_governance,
    generate_governance_recommendations,
    render_cognitive_governance_markdown,
)
from agicore.trading.cognitive_governance_models import (
    CognitiveAutonomyLevel,
    CognitiveGovernanceDecision,
    CognitiveGovernanceMode,
    CognitiveGovernanceRecommendation,
    CognitiveGovernanceRisk,
    CognitivePermission,
    CognitivePolicy,
)
from agicore.trading.collective_consensus_models import ConsensusDecision, ConsensusMode
from agicore.trading.global_orchestrator_models import OrchestratorDecision, OrchestratorMode
from agicore.trading.intent_alignment_models import IntentAlignmentMode
from agicore.trading.learning_governance_models import LearningGovernanceDecision, LearningGovernanceMode
from agicore.trading.meta_cognition_models import MetaCognitionMode
from agicore.trading.mission_continuity_models import MissionContinuityMode
from agicore.trading.operational_awareness_models import OperationalHealthStatus
from agicore.trading.recovery_resilience_models import RecoveryMode
from agicore.trading.recursive_world_model_models import WorldModelDecision, WorldModelRisk
from agicore.trading.self_reflection_audit_models import CognitiveAuditRisk, ReflectionState
from agicore.trading.strategic_arbitration_models import ArbitrationDecision, ArbitrationMode
from agicore.trading.system_integrity_models import SystemIntegrityStatus


def _audit(score=82, state=ReflectionState.CLEAR_REFLECTION, risks=()):
    return SimpleNamespace(reflection_quality_score=score, state=state, risks=risks)


def _world(score=82, decision=WorldModelDecision.MAINTAIN_WORLD_MODEL, risks=()):
    return SimpleNamespace(world_model_coherence_score=score, decision=decision, risks=risks)


def _orchestrator(decision=OrchestratorDecision.CONTINUE_COORDINATED_OPERATION, mode=OrchestratorMode.COORDINATED_OPERATION, confidence=82):
    return SimpleNamespace(decision=decision, confidence_score=confidence, system_state=SimpleNamespace(mode=mode))


def _meta(mode=MetaCognitionMode.SELF_AWARE, confidence=82):
    return SimpleNamespace(mode=mode, confidence_score=confidence)


def _cognitive(score=82, load=CognitiveLoadLevel.LOW):
    return SimpleNamespace(global_score=score, load_level=load)


def _integrity(status=SystemIntegrityStatus.HEALTHY, score=82):
    return SimpleNamespace(status=status, integrity_score=score)


def _intent(mode=IntentAlignmentMode.FULLY_ALIGNED, confidence=82):
    return SimpleNamespace(mode=mode, alignment_confidence=confidence)


def _arbitration(decision=ArbitrationDecision.CONTINUE_OPERATION, mode=ArbitrationMode.NORMAL_OPERATION):
    return SimpleNamespace(decision=decision, mode=mode)


def _consensus(decision=ConsensusDecision.APPROVE_COLLECTIVE_DECISION, mode=ConsensusMode.NORMAL_CONSENSUS, score=82):
    return SimpleNamespace(decision=decision, mode=mode, collective_confidence_score=score)


def _learning(decision=LearningGovernanceDecision.ALLOW_LEARNING, mode=LearningGovernanceMode.LEARN):
    return SimpleNamespace(decision=decision, mode=mode)


def _recovery(mode=RecoveryMode.NORMAL, score=82):
    return SimpleNamespace(mode=mode, resilience_score=score)


def _mission(mode=MissionContinuityMode.FULL_OPERATION, score=82):
    return SimpleNamespace(mode=mode, continuity_score=score)


def _awareness(health=OperationalHealthStatus.HEALTHY, score=82):
    return SimpleNamespace(health_status=health, operational_confidence_score=score)


def test_full_autonomy_when_governance_inputs_are_healthy() -> None:
    result = evaluate_cognitive_governance(
        self_reflection_audit=_audit(),
        recursive_world_model=_world(),
        global_orchestrator=_orchestrator(),
        meta_cognition=_meta(),
        system_integrity=_integrity(),
        intent_alignment=_intent(),
        learning_governance=_learning(),
        mission_continuity=_mission(),
        operational_awareness=_awareness(),
    )

    assert result.autonomy_level == CognitiveAutonomyLevel.FULL_AUTONOMY
    assert result.decision == CognitiveGovernanceDecision.APPROVE_COGNITIVE_OPERATION
    assert CognitivePermission.ALLOW_AUTONOMY_EXPANSION in result.permissions


def test_locks_governance_when_integrity_is_compromised() -> None:
    result = evaluate_cognitive_governance(
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 20),
        strategic_arbitration=_arbitration(ArbitrationDecision.EMERGENCY_LOCKDOWN, ArbitrationMode.EMERGENCY_LOCKDOWN),
        self_reflection_audit=_audit(40, ReflectionState.CRITICAL_REVIEW),
    )

    assert result.mode == CognitiveGovernanceMode.LOCKED_GOVERNANCE
    assert result.autonomy_level == CognitiveAutonomyLevel.LOCKED_AUTONOMY
    assert result.decision == CognitiveGovernanceDecision.ENTER_LOCKED_GOVERNANCE
    assert CognitiveGovernanceRisk.EMERGENCY_LOCK_REQUIRED in result.risks


def test_assess_autonomy_requires_human_review_for_critical_audit() -> None:
    level = assess_autonomy_level(self_reflection_audit=_audit(35, ReflectionState.CRITICAL_REVIEW))

    assert level == CognitiveAutonomyLevel.HUMAN_REVIEW_REQUIRED


def test_build_permission_set_restricts_recursive_and_execution_permissions() -> None:
    permissions = build_permission_set(
        recursive_world_model=_world(35, WorldModelDecision.REBUILD_CAUSAL_GRAPH, (WorldModelRisk.WORLD_MODEL_INCOHERENCE,)),
        global_orchestrator=_orchestrator(OrchestratorDecision.ENTER_SAFE_GLOBAL_MODE),
        intent_alignment=_intent(IntentAlignmentMode.MISALIGNED, 35),
    )

    assert CognitivePermission.ALLOW_RECURSIVE_UPDATES not in permissions
    assert CognitivePermission.ALLOW_EXECUTION_ROUTING not in permissions
    assert CognitivePermission.DENY_HIGH_RISK_ACTIONS in permissions


def test_policy_enforcement_denies_unsafe_permissions_when_forced() -> None:
    permissions = (
        CognitivePermission.ALLOW_ANALYSIS,
        CognitivePermission.ALLOW_RECURSIVE_UPDATES,
        CognitivePermission.ALLOW_AUTONOMY_EXPANSION,
        CognitivePermission.ALLOW_EXECUTION_ROUTING,
    )
    enforcements = enforce_cognitive_policies(
        recursive_world_model=_world(30, WorldModelDecision.FREEZE_RECURSIVE_UPDATES, (WorldModelRisk.RECURSIVE_FEEDBACK_LOOP,)),
        intent_alignment=_intent(IntentAlignmentMode.MISALIGNED, 30),
        strategic_arbitration=_arbitration(ArbitrationDecision.ENABLE_SAFE_MODE, ArbitrationMode.SAFE_COORDINATION),
        permissions=permissions,
    )

    denied = {permission for enforcement in enforcements for permission in enforcement.denied_permissions}
    assert CognitivePermission.ALLOW_RECURSIVE_UPDATES in denied
    assert CognitivePermission.ALLOW_AUTONOMY_EXPANSION in denied


def test_detects_recursive_audit_meta_and_safe_mode_risks() -> None:
    risks = detect_governance_risks(
        self_reflection_audit=_audit(35, ReflectionState.AUDIT_REQUIRED, (CognitiveAuditRisk.INCOMPLETE_TRACEABILITY,)),
        recursive_world_model=_world(35, WorldModelDecision.FREEZE_RECURSIVE_UPDATES, (WorldModelRisk.WORLD_MODEL_INCOHERENCE,)),
        meta_cognition=_meta(MetaCognitionMode.DEGRADED_REASONING, 35),
        cognitive_adaptation=_cognitive(40, CognitiveLoadLevel.OVERLOADED),
        global_orchestrator=_orchestrator(OrchestratorDecision.ENTER_SAFE_GLOBAL_MODE),
    )

    assert CognitiveGovernanceRisk.RECURSIVE_DRIFT_RISK in risks
    assert CognitiveGovernanceRisk.LOW_AUDITABILITY in risks
    assert CognitiveGovernanceRisk.META_COGNITIVE_INSTABILITY in risks
    assert CognitiveGovernanceRisk.SYSTEM_SAFE_MODE_REQUIRED in risks


def test_compute_governance_score_penalizes_policy_violations() -> None:
    enforcements = (
        SimpleNamespace(allowed=True),
        SimpleNamespace(allowed=False),
        SimpleNamespace(allowed=False),
    )
    score = compute_governance_score(
        self_reflection_audit=_audit(40),
        recursive_world_model=_world(35),
        system_integrity=_integrity(SystemIntegrityStatus.DEGRADED, 45),
        policy_enforcements=enforcements,
        risks=(CognitiveGovernanceRisk.UNSAFE_PERMISSION_SET, CognitiveGovernanceRisk.RECURSIVE_DRIFT_RISK),
    )

    assert score.policy_compliance_score < 70
    assert score.recursive_safety_score < 60
    assert score.auditability_score == 40


def test_recommendations_cover_emergency_and_world_model_controls() -> None:
    recommendations = generate_governance_recommendations(
        decision=CognitiveGovernanceDecision.ENTER_LOCKED_GOVERNANCE,
        risks=(
            CognitiveGovernanceRisk.EMERGENCY_LOCK_REQUIRED,
            CognitiveGovernanceRisk.WORLD_MODEL_INCOHERENCE,
            CognitiveGovernanceRisk.LOW_AUDITABILITY,
            CognitiveGovernanceRisk.POLICY_VIOLATION_RISK,
        ),
    )

    assert CognitiveGovernanceRecommendation.ENTER_EMERGENCY_LOCK in recommendations
    assert CognitiveGovernanceRecommendation.PROTECT_WORLD_MODEL in recommendations
    assert CognitiveGovernanceRecommendation.ENFORCE_AUDIT_TRACE in recommendations
    assert CognitiveGovernanceRecommendation.REBUILD_GOVERNANCE_POLICY in recommendations


def test_strategy_and_learning_are_limited_when_learning_governance_is_frozen() -> None:
    result = evaluate_cognitive_governance(
        self_reflection_audit=_audit(70),
        recursive_world_model=_world(70),
        learning_governance=_learning(LearningGovernanceDecision.FREEZE_POLICY_UPDATE, LearningGovernanceMode.FREEZE_LEARNING),
    )

    assert CognitivePermission.ALLOW_STRATEGY_EVOLUTION not in result.permissions
    assert CognitivePermission.ALLOW_LEARNING_UPDATE not in result.permissions
    assert CognitiveGovernanceRecommendation.LIMIT_STRATEGY_EVOLUTION in result.recommendations


def test_render_cognitive_governance_markdown_contains_required_sections() -> None:
    result = evaluate_cognitive_governance(
        self_reflection_audit=_audit(),
        recursive_world_model=_world(),
        global_orchestrator=_orchestrator(),
        meta_cognition=_meta(),
        system_integrity=_integrity(),
        intent_alignment=_intent(),
    )
    markdown = render_cognitive_governance_markdown(result)

    assert "Cognitive Governance State" in markdown
    assert "Autonomy Level" in markdown
    assert "Permission Set" in markdown
    assert "Policy Enforcement" in markdown
    assert "Governance Risks" in markdown
    assert "Governance Score" in markdown
    assert "Decisions" in markdown
    assert "Recommendations" in markdown
    assert "AGIcore Cognitive Governance Outlook" in markdown
