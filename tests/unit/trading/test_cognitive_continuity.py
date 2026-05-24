from __future__ import annotations

from types import SimpleNamespace

from agicore.trading.cognitive_continuity import (
    build_cognitive_continuity_plan,
    build_continuity_anchors,
    compute_cognitive_continuity_score,
    detect_cognitive_continuity_risks,
    evaluate_cognitive_continuity,
    generate_cognitive_continuity_recommendations,
    render_cognitive_continuity_markdown,
)
from agicore.trading.cognitive_continuity_models import (
    CognitiveContinuityAction,
    CognitiveContinuityMode,
    CognitiveContinuityRecommendation,
    CognitiveContinuityRisk,
    CognitiveContinuityState,
)
from agicore.trading.cognitive_governance_models import CognitiveGovernanceDecision, CognitiveGovernanceMode
from agicore.trading.cognitive_policy_models import CognitivePolicyMode
from agicore.trading.cognitive_recovery_models import CognitiveRecoveryState
from agicore.trading.cognitive_stability_models import CognitiveStabilityState
from agicore.trading.collective_consensus_models import ConsensusDecision, ConsensusMode
from agicore.trading.global_orchestrator_models import OrchestratorDecision
from agicore.trading.intent_alignment_models import IntentAlignmentMode, IntentRisk
from agicore.trading.mission_continuity_models import ContinuityAction, ContinuityRisk, MissionContinuityMode
from agicore.trading.recursive_world_model_models import WorldModelDecision, WorldModelRisk
from agicore.trading.recovery_resilience_models import RecoveryMode
from agicore.trading.self_reflection_audit_models import CognitiveAuditRisk, ReflectionState
from agicore.trading.strategic_memory_models import StrategicDriftSignal
from agicore.trading.system_integrity_models import SystemIntegrityStatus


def _recovery(state=CognitiveRecoveryState.RECOVERED, score=82):
    return SimpleNamespace(state=state, recovery_score=score)


def _mission(mode=MissionContinuityMode.FULL_OPERATION, score=82, risks=(), actions=()):
    return SimpleNamespace(mode=mode, continuity_score=score, risks=risks, actions=actions)


def _intent(mode=IntentAlignmentMode.FULLY_ALIGNED, confidence=82, risks=(), priority_score=82):
    return SimpleNamespace(
        mode=mode,
        alignment_confidence=confidence,
        risks=risks,
        strategic_goal_stability_score=confidence,
        confidence_breakdown=SimpleNamespace(priority_stability_score=priority_score),
    )


def _timeline(score=82, drifts=(), degraded=False):
    return SimpleNamespace(strategic_health_score=score, drift_signals=drifts, degradation_detected=degraded)


def _audit(score=82, state=ReflectionState.CLEAR_REFLECTION, risks=()):
    return SimpleNamespace(reflection_quality_score=score, state=state, risks=risks)


def _world(score=82, decision=WorldModelDecision.MAINTAIN_WORLD_MODEL, risks=()):
    return SimpleNamespace(world_model_coherence_score=score, decision=decision, risks=risks)


def _consensus(decision=ConsensusDecision.APPROVE_COLLECTIVE_DECISION, mode=ConsensusMode.NORMAL_CONSENSUS, score=82):
    return SimpleNamespace(decision=decision, mode=mode, collective_confidence_score=score)


def _governance(mode=CognitiveGovernanceMode.NORMAL_GOVERNANCE, decision=CognitiveGovernanceDecision.APPROVE_COGNITIVE_OPERATION, score=82):
    return SimpleNamespace(mode=mode, decision=decision, governance_score=score)


def _policy(mode=CognitivePolicyMode.POLICY_NORMAL):
    return SimpleNamespace(mode=mode)


def _stability(state=CognitiveStabilityState.STABLE):
    return SimpleNamespace(state=state)


def _orchestrator(decision=OrchestratorDecision.CONTINUE_COORDINATED_OPERATION):
    return SimpleNamespace(decision=decision)


def _recovery_resilience(mode=RecoveryMode.NORMAL, score=82):
    return SimpleNamespace(mode=mode, resilience_score=score)


def test_continuous_when_all_anchors_are_protected() -> None:
    result = evaluate_cognitive_continuity(
        cognitive_recovery=_recovery(),
        mission_continuity=_mission(),
        intent_alignment=_intent(),
        strategic_timeline_analysis=_timeline(),
        self_reflection_audit=_audit(),
        recursive_world_model=_world(),
        collective_consensus=_consensus(),
        cognitive_governance=_governance(),
        cognitive_policy=_policy(),
    )

    assert result.state == CognitiveContinuityState.CONTINUOUS
    assert result.mode == CognitiveContinuityMode.NORMAL_CONTINUITY
    assert result.actions == (CognitiveContinuityAction.MARK_CONTINUITY_RESTORED,)
    assert result.continuity_score >= 75


def test_detects_memory_decision_mission_identity_risks() -> None:
    risks = detect_cognitive_continuity_risks(
        mission_continuity=_mission(MissionContinuityMode.SURVIVAL_CONTINUITY, 35, (ContinuityRisk.MEMORY_RISK,), (ContinuityAction.PRESERVE_MEMORY,)),
        self_reflection_audit=_audit(35, ReflectionState.AUDIT_REQUIRED, (CognitiveAuditRisk.INCOMPLETE_TRACEABILITY,)),
        intent_alignment=_intent(IntentAlignmentMode.MISALIGNED, 35, (IntentRisk.MISSION_DIVERGENCE,)),
        strategic_timeline_analysis=_timeline(35, (StrategicDriftSignal.STRATEGIC_DEGRADATION, StrategicDriftSignal.DANGEROUS_POLICY), True),
    )

    assert CognitiveContinuityRisk.MEMORY_CONTINUITY_BREAK in risks
    assert CognitiveContinuityRisk.DECISION_CHAIN_BREAK in risks
    assert CognitiveContinuityRisk.MISSION_DRIFT in risks
    assert CognitiveContinuityRisk.STRATEGIC_IDENTITY_DRIFT in risks


def test_detects_priority_world_consensus_and_execution_context_risks() -> None:
    risks = detect_cognitive_continuity_risks(
        intent_alignment=_intent(IntentAlignmentMode.PRIORITY_CONFLICT, 65, priority_score=30),
        recursive_world_model=_world(30, WorldModelDecision.REBUILD_CAUSAL_GRAPH, (WorldModelRisk.WORLD_MODEL_INCOHERENCE,)),
        collective_consensus=_consensus(ConsensusDecision.NO_CONSENSUS, ConsensusMode.CONSENSUS_COLLAPSE, 30),
        system_integrity=SimpleNamespace(status=SystemIntegrityStatus.COMPROMISED),
        cognitive_policy=_policy(CognitivePolicyMode.POLICY_LOCKED),
    )

    assert CognitiveContinuityRisk.PRIORITY_ORDER_LOSS in risks
    assert CognitiveContinuityRisk.WORLD_MODEL_CONTINUITY_RISK in risks
    assert CognitiveContinuityRisk.CONSENSUS_CONTINUITY_RISK in risks
    assert CognitiveContinuityRisk.EXECUTION_CONTEXT_LOSS in risks


def test_detects_recovery_and_governance_discontinuity() -> None:
    risks = detect_cognitive_continuity_risks(
        cognitive_recovery=_recovery(CognitiveRecoveryState.PARTIAL_RECOVERY, 45),
        recovery_resilience=_recovery_resilience(RecoveryMode.REBUILD_CONFIDENCE, 60),
        cognitive_governance=_governance(CognitiveGovernanceMode.LOCKED_GOVERNANCE, CognitiveGovernanceDecision.ENTER_LOCKED_GOVERNANCE, 30),
    )

    assert CognitiveContinuityRisk.RECOVERY_DISCONTINUITY in risks
    assert CognitiveContinuityRisk.GOVERNANCE_CONTINUITY_RISK in risks


def test_continuity_failure_when_memory_mission_and_identity_drift_together() -> None:
    result = evaluate_cognitive_continuity(
        mission_continuity=_mission(MissionContinuityMode.SURVIVAL_CONTINUITY, 25, (ContinuityRisk.MEMORY_RISK,), (ContinuityAction.PRESERVE_MEMORY,)),
        intent_alignment=_intent(IntentAlignmentMode.MISALIGNED, 25, (IntentRisk.MISSION_DIVERGENCE,)),
        strategic_timeline_analysis=_timeline(25, (StrategicDriftSignal.STRATEGIC_DEGRADATION,), True),
    )

    assert result.state == CognitiveContinuityState.CONTINUITY_FAILURE
    assert result.mode == CognitiveContinuityMode.LOCKED_CONTINUITY
    assert CognitiveContinuityAction.REQUIRE_HUMAN_REVIEW in result.actions


def test_build_anchors_marks_risky_anchors_unprotected() -> None:
    anchors = build_continuity_anchors(
        risks=(
            CognitiveContinuityRisk.MEMORY_CONTINUITY_BREAK,
            CognitiveContinuityRisk.WORLD_MODEL_CONTINUITY_RISK,
        ),
        mission_continuity=_mission(score=40),
        recursive_world_model=_world(35),
    )

    memory = next(anchor for anchor in anchors if anchor.name == "strategic_memory")
    world = next(anchor for anchor in anchors if anchor.name == "world_model")
    assert memory.protected is False
    assert world.protected is False
    assert memory.risk == CognitiveContinuityRisk.MEMORY_CONTINUITY_BREAK


def test_plan_generates_ordered_actions_and_reduced_autonomy() -> None:
    plan = build_cognitive_continuity_plan(
        risks=(
            CognitiveContinuityRisk.MEMORY_CONTINUITY_BREAK,
            CognitiveContinuityRisk.DECISION_CHAIN_BREAK,
            CognitiveContinuityRisk.MISSION_DRIFT,
            CognitiveContinuityRisk.PRIORITY_ORDER_LOSS,
            CognitiveContinuityRisk.STRATEGIC_IDENTITY_DRIFT,
            CognitiveContinuityRisk.WORLD_MODEL_CONTINUITY_RISK,
            CognitiveContinuityRisk.CONSENSUS_CONTINUITY_RISK,
        )
    )

    assert CognitiveContinuityAction.PRESERVE_STRATEGIC_MEMORY in plan.actions
    assert CognitiveContinuityAction.REPAIR_DECISION_CHAIN in plan.actions
    assert CognitiveContinuityAction.RESTORE_MISSION_ANCHOR in plan.actions
    assert CognitiveContinuityAction.REQUIRE_HUMAN_REVIEW in plan.actions
    assert plan.autonomy_reduced is True


def test_score_penalizes_all_risky_components() -> None:
    score = compute_cognitive_continuity_score(
        mission_continuity=_mission(score=45),
        self_reflection_audit=_audit(45),
        intent_alignment=_intent(confidence=45, priority_score=45),
        strategic_timeline_analysis=_timeline(45),
        cognitive_recovery=_recovery(score=45),
        cognitive_governance=_governance(score=45),
        recursive_world_model=_world(45),
        collective_consensus=_consensus(score=45),
        risks=(
            CognitiveContinuityRisk.MEMORY_CONTINUITY_BREAK,
            CognitiveContinuityRisk.DECISION_CHAIN_BREAK,
            CognitiveContinuityRisk.MISSION_DRIFT,
            CognitiveContinuityRisk.STRATEGIC_IDENTITY_DRIFT,
            CognitiveContinuityRisk.PRIORITY_ORDER_LOSS,
            CognitiveContinuityRisk.RECOVERY_DISCONTINUITY,
            CognitiveContinuityRisk.GOVERNANCE_CONTINUITY_RISK,
            CognitiveContinuityRisk.WORLD_MODEL_CONTINUITY_RISK,
            CognitiveContinuityRisk.CONSENSUS_CONTINUITY_RISK,
        ),
    )

    assert score.memory_continuity_score < 20
    assert score.decision_chain_score < 20
    assert score.mission_anchor_score < 20
    assert score.consensus_context_score < 20


def test_recommendations_cover_continuity_controls() -> None:
    recommendations = generate_cognitive_continuity_recommendations(
        risks=(
            CognitiveContinuityRisk.MEMORY_CONTINUITY_BREAK,
            CognitiveContinuityRisk.MISSION_DRIFT,
            CognitiveContinuityRisk.STRATEGIC_IDENTITY_DRIFT,
            CognitiveContinuityRisk.DECISION_CHAIN_BREAK,
            CognitiveContinuityRisk.RECOVERY_DISCONTINUITY,
            CognitiveContinuityRisk.GOVERNANCE_CONTINUITY_RISK,
            CognitiveContinuityRisk.WORLD_MODEL_CONTINUITY_RISK,
        ),
        state=CognitiveContinuityState.CONTINUITY_FAILURE,
    )

    assert CognitiveContinuityRecommendation.EXTEND_MEMORY_CHECKPOINTS in recommendations
    assert CognitiveContinuityRecommendation.RESTORE_MISSION_BEFORE_ACTION in recommendations
    assert CognitiveContinuityRecommendation.VERIFY_IDENTITY_ANCHORS in recommendations
    assert CognitiveContinuityRecommendation.REPAIR_DECISION_TRACE in recommendations
    assert CognitiveContinuityRecommendation.REQUIRE_SUPERVISION in recommendations


def test_recovering_continuity_state_when_recovery_is_active() -> None:
    result = evaluate_cognitive_continuity(
        cognitive_recovery=_recovery(CognitiveRecoveryState.RECOVERING, 68),
        recovery_resilience=_recovery_resilience(RecoveryMode.REBUILD_CONFIDENCE, 70),
    )

    assert result.state == CognitiveContinuityState.RECOVERING_CONTINUITY
    assert result.mode == CognitiveContinuityMode.RECOVERY_CONTINUITY


def test_render_cognitive_continuity_markdown_contains_required_sections() -> None:
    result = evaluate_cognitive_continuity(
        cognitive_recovery=_recovery(),
        mission_continuity=_mission(),
        intent_alignment=_intent(),
        strategic_timeline_analysis=_timeline(),
        self_reflection_audit=_audit(),
    )
    markdown = render_cognitive_continuity_markdown(result)

    assert "Cognitive Continuity State" in markdown
    assert "Continuity Score" in markdown
    assert "Continuity Anchors" in markdown
    assert "Continuity Risks" in markdown
    assert "Continuity Plan" in markdown
    assert "Actions" in markdown
    assert "Recommendations" in markdown
    assert "AGIcore Cognitive Continuity Outlook" in markdown
