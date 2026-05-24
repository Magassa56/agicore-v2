from __future__ import annotations

from types import SimpleNamespace

from agicore.trading.cognitive_continuity_models import CognitiveContinuityRisk, CognitiveContinuityState
from agicore.trading.cognitive_governance_models import (
    CognitiveAutonomyLevel,
    CognitiveGovernanceDecision,
    CognitiveGovernanceMode,
)
from agicore.trading.cognitive_identity_models import CognitiveIdentityRisk, CognitiveIdentityState
from agicore.trading.cognitive_policy_models import CognitivePolicyMode, CognitivePolicyRisk
from agicore.trading.cognitive_recovery_models import CognitiveRecoveryState
from agicore.trading.cognitive_resilience_models import CognitiveResilienceState
from agicore.trading.cognitive_stability_models import CognitiveStabilityState
from agicore.trading.collective_consensus_models import ConsensusDecision
from agicore.trading.global_orchestrator_models import OrchestratorDecision
from agicore.trading.intent_alignment_models import IntentAlignmentMode, IntentRisk
from agicore.trading.intent_integrity import (
    build_intent_chain,
    compute_intent_integrity_score,
    detect_intent_integrity_risks,
    evaluate_intent_integrity,
    generate_intent_integrity_recommendations,
    render_intent_integrity_markdown,
    run_intent_integrity_checks,
)
from agicore.trading.intent_integrity_models import (
    IntentIntegrityAction,
    IntentIntegrityMode,
    IntentIntegrityRecommendation,
    IntentIntegrityRisk,
    IntentIntegrityState,
)
from agicore.trading.mission_continuity_models import MissionContinuityMode
from agicore.trading.recursive_world_model_models import WorldModelDecision, WorldModelRisk
from agicore.trading.self_reflection_audit_models import CognitiveAuditRisk, ReflectionState
from agicore.trading.strategic_memory_models import StrategicDriftSignal
from agicore.trading.system_integrity_models import SystemIntegrityStatus


def _identity(state=CognitiveIdentityState.IDENTITY_STABLE, score=84, risks=()):
    return SimpleNamespace(state=state, identity_score=score, risks=risks)


def _continuity(state=CognitiveContinuityState.CONTINUOUS, score=84, risks=()):
    return SimpleNamespace(state=state, continuity_score=score, risks=risks)


def _intent(mode=IntentAlignmentMode.FULLY_ALIGNED, confidence=84, risks=()):
    return SimpleNamespace(mode=mode, alignment_confidence=confidence, risks=risks)


def _policy(mode=CognitivePolicyMode.POLICY_NORMAL, score=84, risks=()):
    return SimpleNamespace(mode=mode, cognitive_policy_score=score, risks=risks)


def _governance(
    mode=CognitiveGovernanceMode.NORMAL_GOVERNANCE,
    decision=CognitiveGovernanceDecision.APPROVE_COGNITIVE_OPERATION,
    score=84,
    autonomy=CognitiveAutonomyLevel.LIMITED_AUTONOMY,
):
    return SimpleNamespace(mode=mode, decision=decision, governance_score=score, autonomy_level=autonomy)


def _audit(state=ReflectionState.CLEAR_REFLECTION, score=84, risks=()):
    return SimpleNamespace(state=state, reflection_quality_score=score, risks=risks)


def test_intent_intact_when_chain_is_verified() -> None:
    result = evaluate_intent_integrity(
        cognitive_identity=_identity(),
        cognitive_continuity=_continuity(),
        intent_alignment=_intent(),
        cognitive_policy=_policy(),
        cognitive_governance=_governance(),
        self_reflection_audit=_audit(),
    )

    assert result.state == IntentIntegrityState.INTENT_INTACT
    assert result.mode == IntentIntegrityMode.NORMAL_INTENT_INTEGRITY
    assert result.intent_chain.verified is True
    assert IntentIntegrityAction.MARK_INTENT_INTEGRITY_RESTORED in result.actions


def test_detects_mission_identity_policy_and_governance_conflicts() -> None:
    risks = detect_intent_integrity_risks(
        intent_alignment=_intent(IntentAlignmentMode.MISALIGNED, 35, (IntentRisk.MISSION_DIVERGENCE,)),
        cognitive_identity=_identity(CognitiveIdentityState.IDENTITY_CONFLICTED, 35, (CognitiveIdentityRisk.MISSION_IDENTITY_MISMATCH,)),
        cognitive_policy=_policy(CognitivePolicyMode.POLICY_LOCKED, 35, (CognitivePolicyRisk.POLICY_CONFLICT,)),
        cognitive_governance=_governance(
            CognitiveGovernanceMode.LOCKED_GOVERNANCE,
            CognitiveGovernanceDecision.ENTER_LOCKED_GOVERNANCE,
            35,
        ),
    )

    assert IntentIntegrityRisk.MISSION_INTENT_MISMATCH in risks
    assert IntentIntegrityRisk.IDENTITY_INTENT_CONFLICT in risks
    assert IntentIntegrityRisk.POLICY_INTENT_CONFLICT in risks
    assert IntentIntegrityRisk.GOVERNANCE_INTENT_CONFLICT in risks
    assert IntentIntegrityRisk.INTENT_CORRUPTION_RISK in risks


def test_detects_decision_mismatch_and_chain_break() -> None:
    risks = detect_intent_integrity_risks(
        cognitive_continuity=_continuity(
            CognitiveContinuityState.DEGRADED_CONTINUITY,
            35,
            (CognitiveContinuityRisk.DECISION_CHAIN_BREAK,),
        ),
        self_reflection_audit=_audit(
            ReflectionState.AUDIT_REQUIRED,
            35,
            (CognitiveAuditRisk.UNEXPLAINED_DECISION, CognitiveAuditRisk.INCOMPLETE_TRACEABILITY),
        ),
        global_orchestrator=SimpleNamespace(decision=OrchestratorDecision.REQUIRE_HUMAN_SUPERVISION),
        collective_consensus=SimpleNamespace(decision=ConsensusDecision.NO_CONSENSUS),
    )

    assert IntentIntegrityRisk.DECISION_INTENT_MISMATCH in risks
    assert IntentIntegrityRisk.INTENT_CHAIN_BREAK in risks


def test_locks_intent_on_collapse_risk() -> None:
    result = evaluate_intent_integrity(
        intent_alignment=_intent(IntentAlignmentMode.MISALIGNED, 20, (IntentRisk.MISSION_DIVERGENCE,)),
        cognitive_identity=_identity(CognitiveIdentityState.IDENTITY_LOCKED, 20, (CognitiveIdentityRisk.IDENTITY_COLLAPSE_RISK,)),
        cognitive_policy=_policy(CognitivePolicyMode.POLICY_LOCKED, 20, (CognitivePolicyRisk.POLICY_CONFLICT,)),
        cognitive_governance=_governance(CognitiveGovernanceMode.LOCKED_GOVERNANCE, CognitiveGovernanceDecision.ENTER_LOCKED_GOVERNANCE, 20),
        cognitive_continuity=_continuity(CognitiveContinuityState.CONTINUITY_FAILURE, 20),
        system_integrity=SimpleNamespace(status=SystemIntegrityStatus.COMPROMISED),
        cognitive_stability=SimpleNamespace(state=CognitiveStabilityState.COLLAPSING),
    )

    assert result.state == IntentIntegrityState.INTENT_LOCKED
    assert result.mode == IntentIntegrityMode.LOCKED_INTENT_MODE
    assert IntentIntegrityRisk.INTENT_COLLAPSE_RISK in result.risks
    assert IntentIntegrityAction.LOCK_INTENT_STATE in result.actions


def test_autonomy_intent_expansion_is_detected_when_risky() -> None:
    risks = detect_intent_integrity_risks(
        intent_alignment=_intent(IntentAlignmentMode.AUTONOMY_DRIFT, 60, (IntentRisk.AUTONOMY_EXPANSION,)),
        cognitive_governance=_governance(autonomy=CognitiveAutonomyLevel.FULL_AUTONOMY),
        cognitive_identity=_identity(CognitiveIdentityState.IDENTITY_WATCH, 65),
    )

    assert IntentIntegrityRisk.AUTONOMY_INTENT_EXPANSION in risks


def test_score_penalizes_intent_components() -> None:
    score = compute_intent_integrity_score(
        cognitive_identity=_identity(score=45),
        cognitive_continuity=_continuity(score=45),
        cognitive_policy=_policy(score=45),
        cognitive_governance=_governance(score=45),
        self_reflection_audit=_audit(score=45),
        intent_alignment=_intent(confidence=45),
        risks=(
            IntentIntegrityRisk.MISSION_INTENT_MISMATCH,
            IntentIntegrityRisk.IDENTITY_INTENT_CONFLICT,
            IntentIntegrityRisk.POLICY_INTENT_CONFLICT,
            IntentIntegrityRisk.GOVERNANCE_INTENT_CONFLICT,
            IntentIntegrityRisk.DECISION_INTENT_MISMATCH,
            IntentIntegrityRisk.INTENT_CHAIN_BREAK,
            IntentIntegrityRisk.INTENT_COLLAPSE_RISK,
        ),
    )

    assert score.mission_intent_score == 0
    assert score.identity_intent_score == 0
    assert score.chain_integrity_score == 0
    assert score.decision_link_score == 0


def test_checks_and_chain_mark_failed_links() -> None:
    score = compute_intent_integrity_score(
        intent_alignment=_intent(confidence=45),
        cognitive_continuity=_continuity(score=45),
        risks=(IntentIntegrityRisk.MISSION_INTENT_MISMATCH, IntentIntegrityRisk.INTENT_CHAIN_BREAK),
    )
    checks = run_intent_integrity_checks(score, (IntentIntegrityRisk.MISSION_INTENT_MISMATCH, IntentIntegrityRisk.INTENT_CHAIN_BREAK))
    chain = build_intent_chain(score, checks, (IntentIntegrityRisk.MISSION_INTENT_MISMATCH,))

    assert any(check.name == "mission_intent" and check.passed is False for check in checks)
    assert "mission_intent" in chain.broken_links
    assert chain.verified is False


def test_repairing_state_when_only_chain_breaks() -> None:
    result = evaluate_intent_integrity(
        cognitive_continuity=_continuity(
            CognitiveContinuityState.DEGRADED_CONTINUITY,
            40,
            (CognitiveContinuityRisk.DECISION_CHAIN_BREAK,),
        ),
        self_reflection_audit=_audit(risks=(CognitiveAuditRisk.INCOMPLETE_TRACEABILITY,)),
    )

    assert result.state == IntentIntegrityState.INTENT_REPAIRING
    assert result.mode == IntentIntegrityMode.INTENT_CHAIN_VERIFICATION


def test_recovery_and_resilience_failures_break_chain() -> None:
    risks = detect_intent_integrity_risks(
        cognitive_recovery=SimpleNamespace(state=CognitiveRecoveryState.FAILED_RECOVERY),
        cognitive_resilience=SimpleNamespace(state=CognitiveResilienceState.COGNITIVE_SURVIVAL),
    )

    assert IntentIntegrityRisk.INTENT_CHAIN_BREAK in risks


def test_world_model_recursive_freeze_can_collapse_intent() -> None:
    risks = detect_intent_integrity_risks(
        recursive_world_model=SimpleNamespace(
            decision=WorldModelDecision.FREEZE_RECURSIVE_UPDATES,
            risks=(WorldModelRisk.RECURSIVE_FEEDBACK_LOOP,),
        ),
        strategic_timeline_analysis=SimpleNamespace(drift_signals=(StrategicDriftSignal.STRATEGIC_DEGRADATION,)),
    )

    assert IntentIntegrityRisk.INTENT_DRIFT_RISK in risks
    assert IntentIntegrityRisk.INTENT_COLLAPSE_RISK in risks


def test_recommendations_cover_intent_controls() -> None:
    recommendations = generate_intent_integrity_recommendations(
        risks=(
            IntentIntegrityRisk.MISSION_INTENT_MISMATCH,
            IntentIntegrityRisk.INTENT_CHAIN_BREAK,
            IntentIntegrityRisk.IDENTITY_INTENT_CONFLICT,
            IntentIntegrityRisk.POLICY_INTENT_CONFLICT,
            IntentIntegrityRisk.GOVERNANCE_INTENT_CONFLICT,
            IntentIntegrityRisk.AUTONOMY_INTENT_EXPANSION,
        ),
        state=IntentIntegrityState.INTENT_AT_RISK,
    )

    assert IntentIntegrityRecommendation.VERIFY_MISSION_OBJECTIVES in recommendations
    assert IntentIntegrityRecommendation.REPAIR_INTENT_CHAIN in recommendations
    assert IntentIntegrityRecommendation.ALIGN_INTENT_WITH_IDENTITY in recommendations
    assert IntentIntegrityRecommendation.ALIGN_INTENT_WITH_POLICY in recommendations
    assert IntentIntegrityRecommendation.RECHECK_GOVERNANCE_CONSISTENCY in recommendations
    assert IntentIntegrityRecommendation.REQUIRE_SUPERVISION in recommendations


def test_render_intent_integrity_markdown_contains_required_sections() -> None:
    result = evaluate_intent_integrity(
        cognitive_identity=_identity(),
        cognitive_continuity=_continuity(),
        intent_alignment=_intent(),
        cognitive_policy=_policy(),
        cognitive_governance=_governance(),
        self_reflection_audit=_audit(),
    )
    markdown = render_intent_integrity_markdown(result)

    assert "Intent Integrity State" in markdown
    assert "Intent Integrity Score" in markdown
    assert "Intent Chain" in markdown
    assert "Integrity Checks" in markdown
    assert "Risks" in markdown
    assert "Actions" in markdown
    assert "Recommendations" in markdown
    assert "AGIcore Intent Integrity Outlook" in markdown
