from __future__ import annotations

from types import SimpleNamespace

from agicore.trading.behavioral_stability_models import BehavioralPressureLevel, BehavioralRecoveryState
from agicore.trading.cognitive_adaptation_models import CognitiveLoadLevel
from agicore.trading.cognitive_governance_models import CognitiveGovernanceDecision, CognitiveGovernanceMode, CognitiveGovernanceRisk
from agicore.trading.cognitive_policy_models import CognitivePolicyMode, CognitivePolicyRisk
from agicore.trading.cognitive_stability import (
    analyze_stability_trend,
    build_stability_window,
    compute_cognitive_stability_score,
    detect_decision_oscillation,
    detect_stability_risks,
    evaluate_cognitive_stability,
    generate_stability_recommendations,
    render_cognitive_stability_markdown,
)
from agicore.trading.cognitive_stability_models import (
    CognitiveStabilityMode,
    CognitiveStabilityRecommendation,
    CognitiveStabilityRisk,
    CognitiveStabilitySignal,
    CognitiveStabilityState,
    StabilityTrend,
)
from agicore.trading.collective_consensus_models import ConsensusDecision, ConsensusMode
from agicore.trading.global_orchestrator_models import OrchestratorDecision, OrchestratorMode
from agicore.trading.mission_continuity_models import MissionContinuityMode
from agicore.trading.operational_awareness_models import OperationalHealthStatus
from agicore.trading.recursive_world_model_models import WorldModelDecision, WorldModelRisk
from agicore.trading.recovery_resilience_models import RecoveryMode
from agicore.trading.self_reflection_audit_models import CognitiveAuditRisk, ReflectionState
from agicore.trading.strategic_arbitration_models import ArbitrationDecision, ArbitrationMode
from agicore.trading.system_integrity_models import SystemIntegrityStatus


def _policy(mode=CognitivePolicyMode.POLICY_NORMAL, score=82, risks=(), violations=()):
    return SimpleNamespace(mode=mode, cognitive_policy_score=score, risks=risks, violations=violations)


def _governance(mode=CognitiveGovernanceMode.NORMAL_GOVERNANCE, decision=CognitiveGovernanceDecision.APPROVE_COGNITIVE_OPERATION, score=82, risks=()):
    return SimpleNamespace(mode=mode, decision=decision, governance_score=score, risks=risks)


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


def _awareness(health=OperationalHealthStatus.HEALTHY, score=82):
    return SimpleNamespace(health_status=health, operational_confidence_score=score)


def _behavior(score=82, pressure=BehavioralPressureLevel.LOW, recovery=BehavioralRecoveryState.STABLE):
    return SimpleNamespace(stability_score=score, pressure_level=pressure, recovery_state=recovery)


def _cognitive(score=82, load=CognitiveLoadLevel.LOW):
    return SimpleNamespace(global_score=score, load_level=load)


def _integrity(status=SystemIntegrityStatus.HEALTHY, score=82):
    return SimpleNamespace(status=status, integrity_score=score)


def _mission(mode=MissionContinuityMode.FULL_OPERATION, score=82):
    return SimpleNamespace(mode=mode, continuity_score=score)


def _recovery(mode=RecoveryMode.NORMAL, score=82):
    return SimpleNamespace(mode=mode, resilience_score=score)


def test_stable_inputs_confirm_stability() -> None:
    result = evaluate_cognitive_stability(
        cognitive_policy=_policy(),
        cognitive_governance=_governance(),
        recursive_world_model=_world(),
        global_orchestrator=_orchestrator(),
        collective_consensus=_consensus(),
        behavioral_stability=_behavior(),
    )

    assert result.state == CognitiveStabilityState.STABLE
    assert result.mode == CognitiveStabilityMode.NORMAL_STABILITY
    assert result.stability_score >= 75
    assert CognitiveStabilitySignal.STABILITY_CONFIRMED in result.signals


def test_detects_drift_when_governance_policy_and_world_model_degrade() -> None:
    risks = detect_stability_risks(
        cognitive_policy=_policy(CognitivePolicyMode.POLICY_RESTRICTED, 45),
        cognitive_governance=_governance(CognitiveGovernanceMode.DEGRADED_GOVERNANCE, score=45),
        recursive_world_model=_world(45),
    )

    assert CognitiveStabilityRisk.COGNITIVE_DRIFT in risks


def test_detects_decision_oscillation_from_historical_window() -> None:
    window = build_stability_window(
        historical_snapshots=(
            {"decision": "APPROVE_COLLECTIVE_DECISION", "score": 82, "risks": ()},
            {"decision": "EMERGENCY_HALT", "score": 30, "risks": ("SYSTEM_COLLAPSE_RISK",)},
            {"decision": "CONTINUE_COORDINATED_OPERATION", "score": 78, "risks": ()},
        ),
        cognitive_policy=_policy(),
    )

    assert window.oscillation_count >= 2
    assert detect_decision_oscillation(stability_window=window) is True


def test_detects_policy_fragmentation_consensus_and_orchestrator_stress() -> None:
    risks = detect_stability_risks(
        cognitive_policy=_policy(
            CognitivePolicyMode.POLICY_SAFE_MODE,
            45,
            (CognitivePolicyRisk.POLICY_CONFLICT, CognitivePolicyRisk.SAFETY_CRITICAL_BYPASS),
            (SimpleNamespace(), SimpleNamespace()),
        ),
        collective_consensus=_consensus(ConsensusDecision.NO_CONSENSUS, ConsensusMode.CONSENSUS_COLLAPSE, 25),
        global_orchestrator=_orchestrator(OrchestratorDecision.EMERGENCY_HALT_ROUTING, OrchestratorMode.EMERGENCY_ORCHESTRATION, 30),
    )

    assert CognitiveStabilityRisk.POLICY_FRAGMENTATION in risks
    assert CognitiveStabilityRisk.CONSENSUS_CONFLICT in risks
    assert CognitiveStabilityRisk.ORCHESTRATOR_OVERLOAD in risks


def test_detects_world_model_and_recursive_runaway_risks() -> None:
    risks = detect_stability_risks(
        cognitive_policy=_policy(CognitivePolicyMode.POLICY_LOCKED, 30, (CognitivePolicyRisk.WORLD_MODEL_UNPROTECTED,), (SimpleNamespace(), SimpleNamespace())),
        self_reflection_audit=_audit(25, ReflectionState.CRITICAL_REVIEW, (CognitiveAuditRisk.WORLD_MODEL_DRIFT,)),
        recursive_world_model=_world(25, WorldModelDecision.FREEZE_RECURSIVE_UPDATES, (WorldModelRisk.WORLD_MODEL_INCOHERENCE, WorldModelRisk.RECURSIVE_FEEDBACK_LOOP)),
    )

    assert CognitiveStabilityRisk.WORLD_MODEL_INCOHERENCE in risks
    assert CognitiveStabilityRisk.RECURSIVE_INSTABILITY in risks
    assert CognitiveStabilityRisk.RUNAWAY_RECURSION in risks


def test_detects_behavioral_instability_and_collapse_risk() -> None:
    result = evaluate_cognitive_stability(
        behavioral_stability=_behavior(25, BehavioralPressureLevel.EXTREME, BehavioralRecoveryState.CRITICAL),
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 20),
        mission_continuity=_mission(MissionContinuityMode.SURVIVAL_CONTINUITY, 25),
    )

    assert result.state == CognitiveStabilityState.COLLAPSING
    assert result.mode == CognitiveStabilityMode.LOCKED_STABILITY
    assert CognitiveStabilityRisk.BEHAVIORAL_INSTABILITY in result.risks
    assert CognitiveStabilityRisk.SYSTEM_COLLAPSE_RISK in result.risks


def test_recovery_stabilizing_state_is_detected() -> None:
    result = evaluate_cognitive_stability(
        recovery_resilience=_recovery(RecoveryMode.REBUILD_CONFIDENCE, 70),
        cognitive_policy=_policy(score=68),
        cognitive_governance=_governance(score=68),
    )

    assert result.state == CognitiveStabilityState.RECOVERY_STABILIZING
    assert result.mode == CognitiveStabilityMode.RECOVERY_STABILITY_MODE
    assert CognitiveStabilitySignal.RECOVERY_STABILIZATION_DETECTED in result.signals


def test_analyze_trend_reports_improving_degrading_and_collapsing() -> None:
    improving = analyze_stability_trend(stability_window=build_stability_window(historical_snapshots=({"decision": "WATCH", "score": 40},), cognitive_policy=_policy(score=75)))
    degrading = analyze_stability_trend(stability_window=build_stability_window(historical_snapshots=({"decision": "STABLE", "score": 90},), cognitive_policy=_policy(score=35)))
    collapsing = analyze_stability_trend(risks=(CognitiveStabilityRisk.SYSTEM_COLLAPSE_RISK,))

    assert improving == StabilityTrend.IMPROVING
    assert degrading == StabilityTrend.DEGRADING
    assert collapsing == StabilityTrend.COLLAPSING


def test_compute_score_penalizes_risks() -> None:
    score = compute_cognitive_stability_score(
        cognitive_policy=_policy(score=45),
        cognitive_governance=_governance(score=45),
        collective_consensus=_consensus(score=45),
        global_orchestrator=_orchestrator(score=45),
        recursive_world_model=_world(45),
        behavioral_stability=_behavior(45),
        risks=(
            CognitiveStabilityRisk.POLICY_FRAGMENTATION,
            CognitiveStabilityRisk.CONSENSUS_CONFLICT,
            CognitiveStabilityRisk.ORCHESTRATOR_OVERLOAD,
            CognitiveStabilityRisk.WORLD_MODEL_INCOHERENCE,
        ),
    )

    assert score.policy_stability_score < 45
    assert score.consensus_stability_score < 45
    assert score.orchestration_stability_score < 45
    assert score.world_model_stability_score < 45


def test_recommendations_cover_all_major_controls() -> None:
    recommendations = generate_stability_recommendations(
        risks=(
            CognitiveStabilityRisk.COGNITIVE_DRIFT,
            CognitiveStabilityRisk.RECURSIVE_INSTABILITY,
            CognitiveStabilityRisk.POLICY_FRAGMENTATION,
            CognitiveStabilityRisk.CONSENSUS_CONFLICT,
            CognitiveStabilityRisk.WORLD_MODEL_INCOHERENCE,
            CognitiveStabilityRisk.SYSTEM_COLLAPSE_RISK,
        ),
        state=CognitiveStabilityState.COLLAPSING,
    )

    assert CognitiveStabilityRecommendation.REDUCE_AUTONOMY in recommendations
    assert CognitiveStabilityRecommendation.FREEZE_RECURSIVE_UPDATES in recommendations
    assert CognitiveStabilityRecommendation.STABILIZE_POLICY_SET in recommendations
    assert CognitiveStabilityRecommendation.REBUILD_CONSENSUS in recommendations
    assert CognitiveStabilityRecommendation.PROTECT_WORLD_MODEL in recommendations
    assert CognitiveStabilityRecommendation.LOCK_SYSTEM_STABILITY in recommendations


def test_render_cognitive_stability_markdown_contains_required_sections() -> None:
    result = evaluate_cognitive_stability(
        cognitive_policy=_policy(),
        cognitive_governance=_governance(),
        recursive_world_model=_world(),
        global_orchestrator=_orchestrator(),
        collective_consensus=_consensus(),
    )
    markdown = render_cognitive_stability_markdown(result)

    assert "Cognitive Stability State" in markdown
    assert "Stability Score" in markdown
    assert "Stability Trend" in markdown
    assert "Stability Window" in markdown
    assert "Detected Signals" in markdown
    assert "Stability Risks" in markdown
    assert "Recommendations" in markdown
    assert "AGIcore Stability Outlook" in markdown
