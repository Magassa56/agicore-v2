from __future__ import annotations

from types import SimpleNamespace

from agicore.trading.cognitive_governance_models import CognitiveAutonomyLevel, CognitiveGovernanceDecision, CognitiveGovernanceMode
from agicore.trading.cognitive_policy_models import CognitivePolicyMode, CognitivePolicyRisk
from agicore.trading.cognitive_recovery import (
    build_cognitive_recovery_plan,
    build_recovery_checkpoints,
    compute_cognitive_recovery_score,
    detect_cognitive_recovery_risks,
    evaluate_cognitive_recovery,
    generate_cognitive_recovery_recommendations,
    render_cognitive_recovery_markdown,
)
from agicore.trading.cognitive_recovery_models import (
    CognitiveRecoveryAction,
    CognitiveRecoveryCheckpoint,
    CognitiveRecoveryMode,
    CognitiveRecoveryRecommendation,
    CognitiveRecoveryRisk,
    CognitiveRecoveryState,
)
from agicore.trading.cognitive_resilience_models import CognitiveResilienceState
from agicore.trading.cognitive_stability_models import CognitiveStabilityMode, CognitiveStabilityRisk, CognitiveStabilityState
from agicore.trading.collective_consensus_models import ConsensusDecision, ConsensusMode
from agicore.trading.global_orchestrator_models import OrchestratorDecision, OrchestratorMode
from agicore.trading.mission_continuity_models import ContinuityAction, ContinuityRisk, MissionContinuityMode
from agicore.trading.recursive_world_model_models import WorldModelDecision, WorldModelRisk
from agicore.trading.recovery_resilience_models import RecoveryMode
from agicore.trading.strategic_arbitration_models import ArbitrationDecision, ArbitrationMode
from agicore.trading.system_integrity_models import SystemIntegrityStatus


def _resilience(state=CognitiveResilienceState.RESILIENT, score=82):
    return SimpleNamespace(state=state, resilience_score=score)


def _stability(state=CognitiveStabilityState.STABLE, mode=CognitiveStabilityMode.NORMAL_STABILITY, score=82, risks=()):
    return SimpleNamespace(state=state, mode=mode, stability_score=score, risks=risks)


def _policy(mode=CognitivePolicyMode.POLICY_NORMAL, score=82, risks=(), violations=()):
    return SimpleNamespace(mode=mode, cognitive_policy_score=score, risks=risks, violations=violations)


def _governance(mode=CognitiveGovernanceMode.NORMAL_GOVERNANCE, decision=CognitiveGovernanceDecision.APPROVE_COGNITIVE_OPERATION, score=82, autonomy=CognitiveAutonomyLevel.LIMITED_AUTONOMY):
    return SimpleNamespace(mode=mode, decision=decision, governance_score=score, autonomy_level=autonomy)


def _world(score=82, decision=WorldModelDecision.MAINTAIN_WORLD_MODEL, risks=()):
    return SimpleNamespace(world_model_coherence_score=score, decision=decision, risks=risks)


def _orchestrator(decision=OrchestratorDecision.CONTINUE_COORDINATED_OPERATION, mode=OrchestratorMode.COORDINATED_OPERATION, score=82):
    return SimpleNamespace(decision=decision, confidence_score=score, system_state=SimpleNamespace(mode=mode))


def _consensus(decision=ConsensusDecision.APPROVE_COLLECTIVE_DECISION, mode=ConsensusMode.NORMAL_CONSENSUS, score=82):
    return SimpleNamespace(decision=decision, mode=mode, collective_confidence_score=score)


def _arbitration(decision=ArbitrationDecision.CONTINUE_OPERATION, mode=ArbitrationMode.NORMAL_OPERATION):
    return SimpleNamespace(decision=decision, mode=mode)


def _integrity(status=SystemIntegrityStatus.HEALTHY):
    return SimpleNamespace(status=status)


def _mission(mode=MissionContinuityMode.FULL_OPERATION, score=82, risks=(), actions=()):
    return SimpleNamespace(mode=mode, continuity_score=score, risks=risks, actions=actions)


def _recovery(mode=RecoveryMode.NORMAL, score=82):
    return SimpleNamespace(mode=mode, resilience_score=score)


def test_recovered_when_all_layers_are_stable() -> None:
    result = evaluate_cognitive_recovery(
        cognitive_resilience=_resilience(),
        cognitive_stability=_stability(),
        cognitive_policy=_policy(),
        cognitive_governance=_governance(),
        recursive_world_model=_world(),
        collective_consensus=_consensus(),
        global_orchestrator=_orchestrator(),
        mission_continuity=_mission(),
    )

    assert result.state == CognitiveRecoveryState.RECOVERED
    assert result.mode == CognitiveRecoveryMode.NORMAL_RECOVERY
    assert result.actions == (CognitiveRecoveryAction.MARK_RECOVERY_COMPLETE,)
    assert result.recovery_plan.complete is True


def test_detects_recovery_failure_and_minimal_core_rebuild() -> None:
    result = evaluate_cognitive_recovery(
        cognitive_resilience=_resilience(CognitiveResilienceState.COGNITIVE_SURVIVAL, 25),
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED),
        cognitive_stability=_stability(CognitiveStabilityState.COLLAPSING, CognitiveStabilityMode.LOCKED_STABILITY, 20),
    )

    assert CognitiveRecoveryRisk.RECOVERY_FAILURE in result.risks
    assert result.recovery_plan.minimal_core_required is True
    assert CognitiveRecoveryAction.REBUILD_MINIMAL_CORE in result.actions


def test_detects_consensus_governance_policy_world_and_stability_failures() -> None:
    risks = detect_cognitive_recovery_risks(
        collective_consensus=_consensus(ConsensusDecision.NO_CONSENSUS, ConsensusMode.CONSENSUS_COLLAPSE, 20),
        cognitive_governance=_governance(CognitiveGovernanceMode.LOCKED_GOVERNANCE, CognitiveGovernanceDecision.ENTER_LOCKED_GOVERNANCE, 20),
        cognitive_policy=_policy(CognitivePolicyMode.POLICY_LOCKED, 20, (CognitivePolicyRisk.POLICY_CONFLICT,)),
        recursive_world_model=_world(20, WorldModelDecision.REBUILD_CAUSAL_GRAPH, (WorldModelRisk.WORLD_MODEL_INCOHERENCE,)),
        cognitive_stability=_stability(CognitiveStabilityState.CRITICAL, CognitiveStabilityMode.EMERGENCY_STABILIZATION, 20, (CognitiveStabilityRisk.SYSTEM_COLLAPSE_RISK,)),
    )

    assert CognitiveRecoveryRisk.CONSENSUS_REBUILD_FAILURE in risks
    assert CognitiveRecoveryRisk.GOVERNANCE_RESTORE_FAILURE in risks
    assert CognitiveRecoveryRisk.POLICY_REPAIR_FAILURE in risks
    assert CognitiveRecoveryRisk.WORLD_MODEL_RESTORE_FAILURE in risks
    assert CognitiveRecoveryRisk.STABILITY_REBUILD_FAILURE in risks


def test_detects_memory_unsafe_path_and_premature_reactivation() -> None:
    risks = detect_cognitive_recovery_risks(
        mission_continuity=_mission(MissionContinuityMode.SURVIVAL_CONTINUITY, 30, (ContinuityRisk.MEMORY_RISK,), (ContinuityAction.PRESERVE_MEMORY,)),
        strategic_arbitration=_arbitration(ArbitrationDecision.EMERGENCY_LOCKDOWN, ArbitrationMode.EMERGENCY_LOCKDOWN),
        global_orchestrator=_orchestrator(OrchestratorDecision.EMERGENCY_HALT_ROUTING, OrchestratorMode.EMERGENCY_ORCHESTRATION, 20),
        cognitive_governance=_governance(autonomy=CognitiveAutonomyLevel.FULL_AUTONOMY),
        cognitive_stability=_stability(CognitiveStabilityState.UNSTABLE, score=40),
        recursive_world_model=_world(40),
    )

    assert CognitiveRecoveryRisk.MEMORY_RESTORE_RISK in risks
    assert CognitiveRecoveryRisk.UNSAFE_RECOVERY_PATH in risks
    assert CognitiveRecoveryRisk.PREMATURE_REACTIVATION in risks


def test_detects_recovery_loop_from_stagnating_checkpoints() -> None:
    checkpoints = tuple(
        CognitiveRecoveryCheckpoint(f"c{i}", "stability", 40 + i, False)
        for i in range(4)
    )
    risks = detect_cognitive_recovery_risks(previous_checkpoints=checkpoints)

    assert CognitiveRecoveryRisk.RECOVERY_LOOP in risks


def test_plan_orders_consensus_before_governance_before_policy() -> None:
    plan = build_cognitive_recovery_plan(
        risks=(
            CognitiveRecoveryRisk.CONSENSUS_REBUILD_FAILURE,
            CognitiveRecoveryRisk.GOVERNANCE_RESTORE_FAILURE,
            CognitiveRecoveryRisk.POLICY_REPAIR_FAILURE,
            CognitiveRecoveryRisk.WORLD_MODEL_RESTORE_FAILURE,
            CognitiveRecoveryRisk.STABILITY_REBUILD_FAILURE,
            CognitiveRecoveryRisk.MEMORY_RESTORE_RISK,
        )
    )
    actions = [step.action for step in plan.steps]

    assert actions.index(CognitiveRecoveryAction.RESTORE_CONSENSUS) < actions.index(CognitiveRecoveryAction.RESTORE_GOVERNANCE)
    assert actions.index(CognitiveRecoveryAction.RESTORE_GOVERNANCE) < actions.index(CognitiveRecoveryAction.REPAIR_POLICIES)
    assert actions.index(CognitiveRecoveryAction.RESTORE_WORLD_MODEL) < actions.index(CognitiveRecoveryAction.REBUILD_STABILITY)
    assert plan.learning_frozen is True
    assert plan.execution_disabled is True


def test_build_checkpoints_preserves_previous_and_current_layers() -> None:
    previous = (CognitiveRecoveryCheckpoint("previous", "old", 70, True),)
    checkpoints = build_recovery_checkpoints(
        previous_checkpoints=previous,
        cognitive_resilience=_resilience(score=65),
        collective_consensus=_consensus(score=66),
    )

    assert previous[0] in checkpoints
    assert {checkpoint.layer for checkpoint in checkpoints} >= {"minimal_core", "consensus", "governance", "policy", "world_model", "stability", "memory", "orchestration"}


def test_score_penalizes_failed_layers() -> None:
    score = compute_cognitive_recovery_score(
        cognitive_resilience=_resilience(score=45),
        collective_consensus=_consensus(score=45),
        cognitive_governance=_governance(score=45),
        cognitive_policy=_policy(score=45),
        recursive_world_model=_world(45),
        cognitive_stability=_stability(score=45),
        mission_continuity=_mission(score=45),
        global_orchestrator=_orchestrator(score=45),
        risks=(
            CognitiveRecoveryRisk.RECOVERY_FAILURE,
            CognitiveRecoveryRisk.CONSENSUS_REBUILD_FAILURE,
            CognitiveRecoveryRisk.GOVERNANCE_RESTORE_FAILURE,
            CognitiveRecoveryRisk.POLICY_REPAIR_FAILURE,
            CognitiveRecoveryRisk.WORLD_MODEL_RESTORE_FAILURE,
            CognitiveRecoveryRisk.STABILITY_REBUILD_FAILURE,
            CognitiveRecoveryRisk.MEMORY_RESTORE_RISK,
            CognitiveRecoveryRisk.UNSAFE_RECOVERY_PATH,
        ),
    )

    assert score.minimal_core_score < 20
    assert score.consensus_recovery_score < 20
    assert score.world_model_recovery_score < 20
    assert score.orchestration_recovery_score < 25


def test_recommendations_cover_recovery_controls() -> None:
    recommendations = generate_cognitive_recovery_recommendations(
        risks=(
            CognitiveRecoveryRisk.CONSENSUS_REBUILD_FAILURE,
            CognitiveRecoveryRisk.GOVERNANCE_RESTORE_FAILURE,
            CognitiveRecoveryRisk.POLICY_REPAIR_FAILURE,
            CognitiveRecoveryRisk.WORLD_MODEL_RESTORE_FAILURE,
            CognitiveRecoveryRisk.UNSAFE_RECOVERY_PATH,
        ),
        state=CognitiveRecoveryState.HUMAN_REVIEW_REQUIRED,
    )

    assert CognitiveRecoveryRecommendation.RESTORE_MINIMAL_CONSENSUS_FIRST in recommendations
    assert CognitiveRecoveryRecommendation.REPAIR_GOVERNANCE_BEFORE_POLICY in recommendations
    assert CognitiveRecoveryRecommendation.VALIDATE_WORLD_MODEL_BEFORE_ACTION in recommendations
    assert CognitiveRecoveryRecommendation.KEEP_LEARNING_FROZEN in recommendations
    assert CognitiveRecoveryRecommendation.KEEP_EXECUTION_DISABLED in recommendations
    assert CognitiveRecoveryRecommendation.ESCALATE_TO_HUMAN_REVIEW in recommendations


def test_safe_recovery_mode_on_unsafe_path_without_human_review() -> None:
    result = evaluate_cognitive_recovery(
        strategic_arbitration=_arbitration(ArbitrationDecision.STOP_EXECUTION, ArbitrationMode.SAFE_COORDINATION),
        global_orchestrator=_orchestrator(score=65),
    )

    assert result.mode in {CognitiveRecoveryMode.SAFE_RECOVERY_MODE, CognitiveRecoveryMode.LOCKED_RECOVERY}
    assert CognitiveRecoveryRisk.UNSAFE_RECOVERY_PATH in result.risks


def test_render_cognitive_recovery_markdown_contains_required_sections() -> None:
    result = evaluate_cognitive_recovery(
        cognitive_resilience=_resilience(),
        cognitive_stability=_stability(),
        cognitive_policy=_policy(),
        cognitive_governance=_governance(),
        recursive_world_model=_world(),
        collective_consensus=_consensus(),
    )
    markdown = render_cognitive_recovery_markdown(result)

    assert "Cognitive Recovery State" in markdown
    assert "Recovery Score" in markdown
    assert "Recovery Mode" in markdown
    assert "Recovery Risks" in markdown
    assert "Recovery Plan" in markdown
    assert "Checkpoints" in markdown
    assert "Actions" in markdown
    assert "Recommendations" in markdown
    assert "AGIcore Recovery Outlook" in markdown
