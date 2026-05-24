from __future__ import annotations

from types import SimpleNamespace

from agicore.trading.behavioral_stability_models import BehavioralPressureLevel, BehavioralRecoveryState
from agicore.trading.cognitive_governance_models import CognitiveGovernanceDecision, CognitiveGovernanceMode
from agicore.trading.cognitive_policy_models import CognitivePolicyMode, CognitivePolicyRisk
from agicore.trading.cognitive_resilience import (
    build_cognitive_recovery_plan,
    compute_cognitive_resilience_score,
    detect_cognitive_resilience_risks,
    evaluate_cognitive_resilience,
    generate_cognitive_resilience_recommendations,
    identify_failure_domains,
    render_cognitive_resilience_markdown,
)
from agicore.trading.cognitive_resilience_models import (
    CognitiveResilienceAction,
    CognitiveResilienceMode,
    CognitiveResilienceRecommendation,
    CognitiveResilienceRisk,
    CognitiveResilienceState,
)
from agicore.trading.cognitive_stability_models import CognitiveStabilityMode, CognitiveStabilityRisk, CognitiveStabilityState
from agicore.trading.collective_consensus_models import ConsensusDecision, ConsensusMode
from agicore.trading.global_orchestrator_models import OrchestratorDecision, OrchestratorMode
from agicore.trading.intent_alignment_models import IntentAlignmentMode
from agicore.trading.mission_continuity_models import ContinuityAction, ContinuityRisk, MissionContinuityMode
from agicore.trading.operational_awareness_models import OperationalHealthStatus
from agicore.trading.recursive_world_model_models import WorldModelDecision, WorldModelRisk
from agicore.trading.recovery_resilience_models import RecoveryMode
from agicore.trading.self_reflection_audit_models import CognitiveAuditRisk, ReflectionState
from agicore.trading.strategic_arbitration_models import ArbitrationDecision, ArbitrationMode
from agicore.trading.system_integrity_models import SystemIntegrityStatus


def _stability(state=CognitiveStabilityState.STABLE, mode=CognitiveStabilityMode.NORMAL_STABILITY, score=82, risks=()):
    return SimpleNamespace(state=state, mode=mode, stability_score=score, risks=risks)


def _policy(mode=CognitivePolicyMode.POLICY_NORMAL, score=82, risks=(), violations=()):
    return SimpleNamespace(mode=mode, cognitive_policy_score=score, risks=risks, violations=violations)


def _governance(mode=CognitiveGovernanceMode.NORMAL_GOVERNANCE, decision=CognitiveGovernanceDecision.APPROVE_COGNITIVE_OPERATION, score=82):
    return SimpleNamespace(mode=mode, decision=decision, governance_score=score)


def _audit(score=82, state=ReflectionState.CLEAR_REFLECTION, risks=()):
    return SimpleNamespace(reflection_quality_score=score, state=state, risks=risks)


def _world(score=82, decision=WorldModelDecision.MAINTAIN_WORLD_MODEL, risks=()):
    return SimpleNamespace(world_model_coherence_score=score, decision=decision, risks=risks)


def _orchestrator(decision=OrchestratorDecision.CONTINUE_COORDINATED_OPERATION, mode=OrchestratorMode.COORDINATED_OPERATION, score=82):
    return SimpleNamespace(decision=decision, confidence_score=score, system_state=SimpleNamespace(mode=mode))


def _consensus(decision=ConsensusDecision.APPROVE_COLLECTIVE_DECISION, mode=ConsensusMode.NORMAL_CONSENSUS, score=82):
    return SimpleNamespace(decision=decision, mode=mode, collective_confidence_score=score)


def _arbitration(decision=ArbitrationDecision.CONTINUE_OPERATION, mode=ArbitrationMode.NORMAL_OPERATION):
    return SimpleNamespace(decision=decision, mode=mode)


def _intent(mode=IntentAlignmentMode.FULLY_ALIGNED, confidence=82):
    return SimpleNamespace(mode=mode, alignment_confidence=confidence)


def _awareness(health=OperationalHealthStatus.HEALTHY, score=82):
    return SimpleNamespace(health_status=health, operational_confidence_score=score)


def _integrity(status=SystemIntegrityStatus.HEALTHY):
    return SimpleNamespace(status=status)


def _mission(mode=MissionContinuityMode.FULL_OPERATION, score=82, risks=(), actions=()):
    return SimpleNamespace(mode=mode, continuity_score=score, risks=risks, actions=actions)


def _recovery(mode=RecoveryMode.NORMAL, score=82):
    return SimpleNamespace(mode=mode, resilience_score=score)


def _behavior(score=82, pressure=BehavioralPressureLevel.LOW, recovery=BehavioralRecoveryState.STABLE):
    return SimpleNamespace(stability_score=score, pressure_level=pressure, recovery_state=recovery)


def test_resilient_state_when_all_inputs_are_healthy() -> None:
    result = evaluate_cognitive_resilience(
        cognitive_stability=_stability(),
        cognitive_policy=_policy(),
        cognitive_governance=_governance(),
        recursive_world_model=_world(),
        collective_consensus=_consensus(),
        global_orchestrator=_orchestrator(),
        mission_continuity=_mission(),
        behavioral_stability=_behavior(),
    )

    assert result.state == CognitiveResilienceState.RESILIENT
    assert result.mode == CognitiveResilienceMode.NORMAL_RESILIENCE
    assert result.actions == (CognitiveResilienceAction.KEEP_RUNNING,)
    assert result.resilience_score >= 75


def test_detects_cognitive_collapse_and_survival_mode() -> None:
    result = evaluate_cognitive_resilience(
        cognitive_stability=_stability(CognitiveStabilityState.COLLAPSING, CognitiveStabilityMode.LOCKED_STABILITY, 20, (CognitiveStabilityRisk.SYSTEM_COLLAPSE_RISK,)),
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED),
        collective_consensus=_consensus(ConsensusDecision.EMERGENCY_HALT, ConsensusMode.CONSENSUS_COLLAPSE, 20),
        global_orchestrator=_orchestrator(OrchestratorDecision.EMERGENCY_HALT_ROUTING, OrchestratorMode.EMERGENCY_ORCHESTRATION, 20),
    )

    assert result.state == CognitiveResilienceState.COGNITIVE_SURVIVAL
    assert result.mode == CognitiveResilienceMode.SURVIVAL_COGNITION
    assert CognitiveResilienceRisk.COGNITIVE_COLLAPSE_RISK in result.risks
    assert CognitiveResilienceAction.ENTER_COGNITIVE_SURVIVAL_MODE in result.actions


def test_detects_consensus_governance_and_policy_failures() -> None:
    risks = detect_cognitive_resilience_risks(
        collective_consensus=_consensus(ConsensusDecision.NO_CONSENSUS, ConsensusMode.CONSENSUS_COLLAPSE, 25),
        cognitive_governance=_governance(CognitiveGovernanceMode.LOCKED_GOVERNANCE, CognitiveGovernanceDecision.ENTER_LOCKED_GOVERNANCE, 25),
        cognitive_policy=_policy(CognitivePolicyMode.POLICY_LOCKED, 25, (CognitivePolicyRisk.POLICY_CONFLICT,), (SimpleNamespace(), SimpleNamespace())),
    )

    assert CognitiveResilienceRisk.CONSENSUS_BREAKDOWN in risks
    assert CognitiveResilienceRisk.GOVERNANCE_FAILURE in risks
    assert CognitiveResilienceRisk.POLICY_FAILURE in risks


def test_detects_world_model_orchestration_memory_and_recursive_failures() -> None:
    risks = detect_cognitive_resilience_risks(
        recursive_world_model=_world(25, WorldModelDecision.FREEZE_RECURSIVE_UPDATES, (WorldModelRisk.WORLD_MODEL_INCOHERENCE, WorldModelRisk.RECURSIVE_FEEDBACK_LOOP)),
        self_reflection_audit=_audit(30, ReflectionState.CRITICAL_REVIEW, (CognitiveAuditRisk.WORLD_MODEL_DRIFT,)),
        global_orchestrator=_orchestrator(OrchestratorDecision.ACTIVATE_SURVIVAL_MODE, OrchestratorMode.SURVIVAL_ORCHESTRATION, 30),
        strategic_arbitration=_arbitration(ArbitrationDecision.EMERGENCY_LOCKDOWN, ArbitrationMode.EMERGENCY_LOCKDOWN),
        mission_continuity=_mission(MissionContinuityMode.SURVIVAL_CONTINUITY, 30, (ContinuityRisk.MEMORY_RISK,), (ContinuityAction.PRESERVE_MEMORY,)),
    )

    assert CognitiveResilienceRisk.WORLD_MODEL_FAILURE in risks
    assert CognitiveResilienceRisk.ORCHESTRATION_FAILURE in risks
    assert CognitiveResilienceRisk.MEMORY_RISK in risks
    assert CognitiveResilienceRisk.RECURSIVE_FAILURE in risks


def test_detects_strategic_drift_and_behavioral_destabilization() -> None:
    risks = detect_cognitive_resilience_risks(
        intent_alignment=_intent(IntentAlignmentMode.STRATEGIC_DIVERGENCE, 30),
        self_reflection_audit=_audit(45, ReflectionState.SELF_CORRECTION_NEEDED),
        behavioral_stability=_behavior(30, BehavioralPressureLevel.EXTREME, BehavioralRecoveryState.CRITICAL),
    )

    assert CognitiveResilienceRisk.STRATEGIC_DRIFT_SURGE in risks
    assert CognitiveResilienceRisk.BEHAVIORAL_DESTABILIZATION in risks


def test_identify_failure_domains_orders_by_severity() -> None:
    domains = identify_failure_domains(
        risks=(
            CognitiveResilienceRisk.POLICY_FAILURE,
            CognitiveResilienceRisk.COGNITIVE_COLLAPSE_RISK,
            CognitiveResilienceRisk.MEMORY_RISK,
        )
    )

    assert domains[0].risk == CognitiveResilienceRisk.COGNITIVE_COLLAPSE_RISK
    assert all(domain.isolate for domain in domains)
    assert {domain.recovery_action for domain in domains} >= {
        CognitiveResilienceAction.ENTER_COGNITIVE_SURVIVAL_MODE,
        CognitiveResilienceAction.PROTECT_CRITICAL_MEMORY,
    }


def test_build_recovery_plan_sets_flags_and_ordered_steps() -> None:
    plan = build_cognitive_recovery_plan(
        risks=(
            CognitiveResilienceRisk.MEMORY_RISK,
            CognitiveResilienceRisk.CONSENSUS_BREAKDOWN,
            CognitiveResilienceRisk.RECURSIVE_FAILURE,
            CognitiveResilienceRisk.COGNITIVE_COLLAPSE_RISK,
        )
    )

    assert plan.protected_memory is True
    assert plan.minimal_consensus_required is True
    assert plan.recursive_updates_frozen is True
    assert plan.survival_mode_required is True
    assert plan.steps[0] == CognitiveResilienceAction.ENTER_COGNITIVE_SURVIVAL_MODE


def test_compute_score_penalizes_failed_domains() -> None:
    score = compute_cognitive_resilience_score(
        cognitive_stability=_stability(score=45),
        cognitive_governance=_governance(score=45),
        cognitive_policy=_policy(score=45),
        collective_consensus=_consensus(score=45),
        recursive_world_model=_world(45),
        global_orchestrator=_orchestrator(score=45),
        mission_continuity=_mission(score=45),
        behavioral_stability=_behavior(45),
        risks=(
            CognitiveResilienceRisk.COGNITIVE_COLLAPSE_RISK,
            CognitiveResilienceRisk.GOVERNANCE_FAILURE,
            CognitiveResilienceRisk.POLICY_FAILURE,
            CognitiveResilienceRisk.CONSENSUS_BREAKDOWN,
            CognitiveResilienceRisk.WORLD_MODEL_FAILURE,
            CognitiveResilienceRisk.ORCHESTRATION_FAILURE,
            CognitiveResilienceRisk.MEMORY_RISK,
            CognitiveResilienceRisk.BEHAVIORAL_DESTABILIZATION,
        ),
    )

    assert score.stability_resilience_score < 30
    assert score.governance_resilience_score < 30
    assert score.policy_resilience_score < 30
    assert score.memory_resilience_score < 30


def test_recommendations_cover_resilience_controls() -> None:
    recommendations = generate_cognitive_resilience_recommendations(
        risks=(
            CognitiveResilienceRisk.GOVERNANCE_FAILURE,
            CognitiveResilienceRisk.CONSENSUS_BREAKDOWN,
            CognitiveResilienceRisk.WORLD_MODEL_FAILURE,
            CognitiveResilienceRisk.POLICY_FAILURE,
            CognitiveResilienceRisk.MEMORY_RISK,
            CognitiveResilienceRisk.RECURSIVE_FAILURE,
        ),
        state=CognitiveResilienceState.CRITICAL,
    )

    assert CognitiveResilienceRecommendation.STABILIZE_GOVERNANCE in recommendations
    assert CognitiveResilienceRecommendation.REBUILD_CONSENSUS_LAYER in recommendations
    assert CognitiveResilienceRecommendation.PROTECT_WORLD_MODEL in recommendations
    assert CognitiveResilienceRecommendation.LOCK_HIGH_RISK_POLICIES in recommendations
    assert CognitiveResilienceRecommendation.PRESERVE_STRATEGIC_MEMORY in recommendations
    assert CognitiveResilienceRecommendation.REQUIRE_SUPERVISION in recommendations


def test_recovering_state_when_recovery_resilience_is_rebuilding() -> None:
    result = evaluate_cognitive_resilience(
        recovery_resilience=_recovery(RecoveryMode.REBUILD_CONFIDENCE, 70),
        cognitive_stability=_stability(score=68),
        cognitive_policy=_policy(score=68),
    )

    assert result.state == CognitiveResilienceState.RECOVERING
    assert result.mode == CognitiveResilienceMode.STABILIZE_COGNITION


def test_render_cognitive_resilience_markdown_contains_required_sections() -> None:
    result = evaluate_cognitive_resilience(
        cognitive_stability=_stability(),
        cognitive_policy=_policy(),
        cognitive_governance=_governance(),
        recursive_world_model=_world(),
        collective_consensus=_consensus(),
    )
    markdown = render_cognitive_resilience_markdown(result)

    assert "Cognitive Resilience State" in markdown
    assert "Resilience Score" in markdown
    assert "Failure Domains" in markdown
    assert "Risks" in markdown
    assert "Recovery Plan" in markdown
    assert "Actions" in markdown
    assert "Recommendations" in markdown
    assert "AGIcore Cognitive Resilience Outlook" in markdown
