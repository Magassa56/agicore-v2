from __future__ import annotations

from types import SimpleNamespace

from agicore.trading.cognitive_alignment import (
    build_alignment_axes,
    build_alignment_matrix,
    compute_cognitive_alignment_score,
    detect_cognitive_alignment_risks,
    evaluate_cognitive_alignment,
    generate_cognitive_alignment_recommendations,
    render_cognitive_alignment_markdown,
)
from agicore.trading.cognitive_alignment_models import (
    CognitiveAlignmentAction,
    CognitiveAlignmentMode,
    CognitiveAlignmentRecommendation,
    CognitiveAlignmentRisk,
    CognitiveAlignmentState,
)
from agicore.trading.cognitive_governance_models import (
    CognitiveAutonomyLevel,
    CognitiveGovernanceDecision,
    CognitiveGovernanceMode,
)
from agicore.trading.cognitive_identity_models import CognitiveIdentityRisk, CognitiveIdentityState
from agicore.trading.cognitive_policy_models import CognitivePolicyMode, CognitivePolicyRisk
from agicore.trading.cognitive_stability_models import CognitiveStabilityState
from agicore.trading.collective_consensus_models import ConsensusDecision, ConsensusMode, ConsensusRisk
from agicore.trading.global_orchestrator_models import OrchestratorDecision, OrchestratorMode
from agicore.trading.intent_alignment_models import IntentAlignmentMode, IntentRisk
from agicore.trading.intent_integrity_models import IntentIntegrityRisk, IntentIntegrityState
from agicore.trading.mission_continuity_models import ContinuityRisk, MissionContinuityMode
from agicore.trading.recursive_world_model_models import WorldModelDecision, WorldModelRisk
from agicore.trading.self_reflection_audit_models import CognitiveAuditRisk, ReflectionState
from agicore.trading.system_integrity_models import SystemIntegrityStatus


def _mission(mode=MissionContinuityMode.FULL_OPERATION, score=84, risks=()):
    return SimpleNamespace(mode=mode, continuity_score=score, risks=risks)


def _intent_alignment(mode=IntentAlignmentMode.FULLY_ALIGNED, confidence=84, risks=()):
    return SimpleNamespace(mode=mode, alignment_confidence=confidence, risks=risks)


def _identity(state=CognitiveIdentityState.IDENTITY_STABLE, score=84, risks=()):
    return SimpleNamespace(state=state, identity_score=score, risks=risks)


def _intent_integrity(state=IntentIntegrityState.INTENT_INTACT, score=84, risks=()):
    return SimpleNamespace(state=state, intent_integrity_score=score, risks=risks)


def _policy(mode=CognitivePolicyMode.POLICY_NORMAL, score=84, risks=()):
    return SimpleNamespace(mode=mode, cognitive_policy_score=score, risks=risks)


def _governance(
    mode=CognitiveGovernanceMode.NORMAL_GOVERNANCE,
    decision=CognitiveGovernanceDecision.APPROVE_COGNITIVE_OPERATION,
    score=84,
    autonomy=CognitiveAutonomyLevel.LIMITED_AUTONOMY,
):
    return SimpleNamespace(mode=mode, decision=decision, governance_score=score, autonomy_level=autonomy)


def _world(score=84, decision=WorldModelDecision.MAINTAIN_WORLD_MODEL, risks=()):
    return SimpleNamespace(world_model_coherence_score=score, decision=decision, risks=risks)


def _consensus(decision=ConsensusDecision.APPROVE_COLLECTIVE_DECISION, mode=ConsensusMode.NORMAL_CONSENSUS, score=84, risks=()):
    return SimpleNamespace(decision=decision, mode=mode, collective_confidence_score=score, risks=risks)


def _audit(state=ReflectionState.CLEAR_REFLECTION, score=84, risks=()):
    return SimpleNamespace(state=state, reflection_quality_score=score, risks=risks)


def test_fully_aligned_when_all_axes_are_healthy() -> None:
    result = evaluate_cognitive_alignment(
        mission_continuity=_mission(),
        intent_alignment=_intent_alignment(),
        cognitive_identity=_identity(),
        intent_integrity=_intent_integrity(),
        cognitive_policy=_policy(),
        cognitive_governance=_governance(),
        recursive_world_model=_world(),
        collective_consensus=_consensus(),
        self_reflection_audit=_audit(),
    )

    assert result.state == CognitiveAlignmentState.FULLY_ALIGNED
    assert result.mode == CognitiveAlignmentMode.NORMAL_ALIGNMENT
    assert result.matrix.locked is False
    assert result.actions == (CognitiveAlignmentAction.PRESERVE_ALIGNMENT_STATE,)


def test_detects_mission_identity_and_intent_breaks() -> None:
    risks = detect_cognitive_alignment_risks(
        mission_continuity=_mission(MissionContinuityMode.SURVIVAL_CONTINUITY, 35, (ContinuityRisk.EXECUTIVE_COLLAPSE,)),
        intent_alignment=_intent_alignment(IntentAlignmentMode.MISALIGNED, 35, (IntentRisk.MISSION_DIVERGENCE,)),
        cognitive_identity=_identity(CognitiveIdentityState.IDENTITY_CONFLICTED, 35, (CognitiveIdentityRisk.IDENTITY_COLLAPSE_RISK,)),
        intent_integrity=_intent_integrity(IntentIntegrityState.INTENT_CONFLICT, 35, (IntentIntegrityRisk.INTENT_COLLAPSE_RISK,)),
    )

    assert CognitiveAlignmentRisk.MISSION_ALIGNMENT_BREAK in risks
    assert CognitiveAlignmentRisk.IDENTITY_ALIGNMENT_BREAK in risks
    assert CognitiveAlignmentRisk.INTENT_ALIGNMENT_BREAK in risks


def test_detects_policy_governance_world_consensus_and_decision_breaks() -> None:
    risks = detect_cognitive_alignment_risks(
        cognitive_policy=_policy(CognitivePolicyMode.POLICY_LOCKED, 35, (CognitivePolicyRisk.POLICY_CONFLICT,)),
        cognitive_governance=_governance(CognitiveGovernanceMode.LOCKED_GOVERNANCE, CognitiveGovernanceDecision.ENTER_LOCKED_GOVERNANCE, 35),
        recursive_world_model=_world(35, WorldModelDecision.REBUILD_CAUSAL_GRAPH, (WorldModelRisk.WORLD_MODEL_INCOHERENCE,)),
        collective_consensus=_consensus(
            ConsensusDecision.NO_CONSENSUS,
            ConsensusMode.CONSENSUS_COLLAPSE,
            35,
            (ConsensusRisk.CONSENSUS_FRAGMENTATION,),
        ),
        self_reflection_audit=_audit(ReflectionState.AUDIT_REQUIRED, 35, (CognitiveAuditRisk.UNEXPLAINED_DECISION,)),
        global_orchestrator=SimpleNamespace(
            mode=OrchestratorMode.EMERGENCY_ORCHESTRATION,
            decision=OrchestratorDecision.EMERGENCY_HALT_ROUTING,
        ),
    )

    assert CognitiveAlignmentRisk.POLICY_ALIGNMENT_BREAK in risks
    assert CognitiveAlignmentRisk.GOVERNANCE_ALIGNMENT_BREAK in risks
    assert CognitiveAlignmentRisk.WORLD_MODEL_ALIGNMENT_BREAK in risks
    assert CognitiveAlignmentRisk.CONSENSUS_ALIGNMENT_BREAK in risks
    assert CognitiveAlignmentRisk.DECISION_ACTION_MISALIGNMENT in risks


def test_locks_alignment_on_systemic_collapse() -> None:
    result = evaluate_cognitive_alignment(
        mission_continuity=_mission(MissionContinuityMode.SURVIVAL_CONTINUITY, 20),
        intent_alignment=_intent_alignment(IntentAlignmentMode.MISALIGNED, 20),
        cognitive_identity=_identity(CognitiveIdentityState.IDENTITY_LOCKED, 20, (CognitiveIdentityRisk.IDENTITY_COLLAPSE_RISK,)),
        intent_integrity=_intent_integrity(IntentIntegrityState.INTENT_LOCKED, 20, (IntentIntegrityRisk.INTENT_COLLAPSE_RISK,)),
        cognitive_policy=_policy(CognitivePolicyMode.POLICY_LOCKED, 20, (CognitivePolicyRisk.POLICY_CONFLICT,)),
        cognitive_governance=_governance(CognitiveGovernanceMode.LOCKED_GOVERNANCE, CognitiveGovernanceDecision.ENTER_LOCKED_GOVERNANCE, 20),
        system_integrity=SimpleNamespace(status=SystemIntegrityStatus.COMPROMISED),
        cognitive_stability=SimpleNamespace(state=CognitiveStabilityState.COLLAPSING),
    )

    assert result.state == CognitiveAlignmentState.ALIGNMENT_LOCKED
    assert result.mode == CognitiveAlignmentMode.LOCKED_ALIGNMENT_MODE
    assert CognitiveAlignmentRisk.SYSTEMIC_ALIGNMENT_COLLAPSE in result.risks
    assert CognitiveAlignmentAction.LOCK_ALIGNMENT_STATE in result.actions


def test_autonomy_alignment_risk_when_full_autonomy_with_breaks() -> None:
    risks = detect_cognitive_alignment_risks(
        intent_alignment=_intent_alignment(IntentAlignmentMode.AUTONOMY_DRIFT, 65, (IntentRisk.AUTONOMY_EXPANSION,)),
        cognitive_governance=_governance(autonomy=CognitiveAutonomyLevel.FULL_AUTONOMY),
        cognitive_identity=_identity(CognitiveIdentityState.IDENTITY_WATCH, 65),
    )

    assert CognitiveAlignmentRisk.AUTONOMY_ALIGNMENT_RISK in risks


def test_score_penalizes_all_alignment_axes() -> None:
    score = compute_cognitive_alignment_score(
        mission_continuity=_mission(score=45),
        intent_alignment=_intent_alignment(confidence=45),
        cognitive_identity=_identity(score=45),
        intent_integrity=_intent_integrity(score=45),
        cognitive_policy=_policy(score=45),
        cognitive_governance=_governance(score=45),
        recursive_world_model=_world(score=45),
        collective_consensus=_consensus(score=45),
        self_reflection_audit=_audit(score=45),
        risks=(
            CognitiveAlignmentRisk.MISSION_ALIGNMENT_BREAK,
            CognitiveAlignmentRisk.IDENTITY_ALIGNMENT_BREAK,
            CognitiveAlignmentRisk.INTENT_ALIGNMENT_BREAK,
            CognitiveAlignmentRisk.POLICY_ALIGNMENT_BREAK,
            CognitiveAlignmentRisk.GOVERNANCE_ALIGNMENT_BREAK,
            CognitiveAlignmentRisk.WORLD_MODEL_ALIGNMENT_BREAK,
            CognitiveAlignmentRisk.CONSENSUS_ALIGNMENT_BREAK,
            CognitiveAlignmentRisk.DECISION_ACTION_MISALIGNMENT,
            CognitiveAlignmentRisk.SYSTEMIC_ALIGNMENT_COLLAPSE,
        ),
    )

    assert score.mission_alignment_score == 0
    assert score.identity_alignment_score == 0
    assert score.intent_alignment_score == 0
    assert score.consensus_alignment_score == 0


def test_axes_and_matrix_expose_broken_axes() -> None:
    score = compute_cognitive_alignment_score(
        mission_continuity=_mission(score=45),
        intent_alignment=_intent_alignment(confidence=45),
        risks=(CognitiveAlignmentRisk.MISSION_ALIGNMENT_BREAK,),
    )
    axes = build_alignment_axes(score, (CognitiveAlignmentRisk.MISSION_ALIGNMENT_BREAK,))
    matrix = build_alignment_matrix(axes, (CognitiveAlignmentRisk.MISSION_ALIGNMENT_BREAK,))

    assert any(axis.name == "mission" and axis.aligned is False for axis in axes)
    assert "mission" in matrix.broken_axes
    assert matrix.autonomy_reduced is True


def test_intent_misalignment_state_takes_priority() -> None:
    result = evaluate_cognitive_alignment(intent_integrity=_intent_integrity(IntentIntegrityState.INTENT_CONFLICT, 35))

    assert result.state == CognitiveAlignmentState.INTENT_MISALIGNMENT
    assert result.mode == CognitiveAlignmentMode.INTENT_ALIGNMENT_REPAIR


def test_policy_misalignment_state_for_policy_or_governance_break() -> None:
    result = evaluate_cognitive_alignment(cognitive_policy=_policy(CognitivePolicyMode.POLICY_LOCKED, 35))

    assert result.state == CognitiveAlignmentState.POLICY_MISALIGNMENT
    assert result.mode == CognitiveAlignmentMode.POLICY_ALIGNMENT_REPAIR


def test_recommendations_cover_alignment_controls() -> None:
    recommendations = generate_cognitive_alignment_recommendations(
        risks=(
            CognitiveAlignmentRisk.MISSION_ALIGNMENT_BREAK,
            CognitiveAlignmentRisk.IDENTITY_ALIGNMENT_BREAK,
            CognitiveAlignmentRisk.INTENT_ALIGNMENT_BREAK,
            CognitiveAlignmentRisk.POLICY_ALIGNMENT_BREAK,
            CognitiveAlignmentRisk.GOVERNANCE_ALIGNMENT_BREAK,
            CognitiveAlignmentRisk.CONSENSUS_ALIGNMENT_BREAK,
            CognitiveAlignmentRisk.AUTONOMY_ALIGNMENT_RISK,
        ),
        state=CognitiveAlignmentState.SYSTEMIC_MISALIGNMENT,
    )

    assert CognitiveAlignmentRecommendation.VERIFY_MISSION_ALIGNMENT in recommendations
    assert CognitiveAlignmentRecommendation.REPAIR_IDENTITY_ALIGNMENT in recommendations
    assert CognitiveAlignmentRecommendation.REPAIR_INTENT_ALIGNMENT in recommendations
    assert CognitiveAlignmentRecommendation.REPAIR_POLICY_ALIGNMENT in recommendations
    assert CognitiveAlignmentRecommendation.RECHECK_GOVERNANCE_ALIGNMENT in recommendations
    assert CognitiveAlignmentRecommendation.REBUILD_CONSENSUS_CONTEXT in recommendations
    assert CognitiveAlignmentRecommendation.REQUIRE_SUPERVISION in recommendations


def test_render_cognitive_alignment_markdown_contains_required_sections() -> None:
    result = evaluate_cognitive_alignment(
        mission_continuity=_mission(),
        intent_alignment=_intent_alignment(),
        cognitive_identity=_identity(),
        intent_integrity=_intent_integrity(),
        cognitive_policy=_policy(),
        cognitive_governance=_governance(),
        recursive_world_model=_world(),
        collective_consensus=_consensus(),
        self_reflection_audit=_audit(),
    )
    markdown = render_cognitive_alignment_markdown(result)

    assert "Cognitive Alignment State" in markdown
    assert "Alignment Score" in markdown
    assert "Alignment Axes" in markdown
    assert "Alignment Matrix" in markdown
    assert "Alignment Risks" in markdown
    assert "Actions" in markdown
    assert "Recommendations" in markdown
    assert "AGIcore Cognitive Alignment Outlook" in markdown
