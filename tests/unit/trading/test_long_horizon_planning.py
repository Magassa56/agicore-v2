"""Unit tests for the offline Autonomous Long-Horizon Planning Engine."""
from __future__ import annotations

from agicore.trading.behavioral_stability_models import BehavioralPressureLevel, BehavioralRecoveryState, BehavioralStabilityResult, BehavioralStabilityScore
from agicore.trading.collective_consensus_models import CollectiveConfidence, ConsensusDecision, ConsensusGraph, ConsensusMode, ConsensusResult, ConsensusState
from agicore.trading.global_orchestrator_models import (
    CoordinationResult,
    CoordinationState,
    GlobalOrchestratorResult,
    GlobalSystemState,
    OrchestrationGraph,
    OrchestratorCycle,
    OrchestratorDecision,
    OrchestratorMode,
    OrchestratorPriority,
    OrchestratorRisk,
    SystemHealthSnapshot,
)
from agicore.trading.intent_alignment_models import IntentAlignmentMode, IntentAlignmentResult, IntentAlignmentState, IntentConfidence, IntentPriority
from agicore.trading.long_horizon_planning import (
    build_future_scenarios,
    build_horizon_plan_graph,
    compute_projection_confidence,
    decide_long_horizon_plan,
    evaluate_long_horizon_risks,
    generate_long_horizon_recommendations,
    plan_long_horizon,
    project_strategic_trajectory,
    render_long_horizon_planning_markdown,
)
from agicore.trading.long_horizon_planning_models import FutureScenarioType, PlanningDecision, PlanningHorizon, PlanningRecommendation, PlanningRisk
from agicore.trading.mission_continuity_models import MissionContinuityMode, MissionContinuityResult, MissionContinuityScore
from agicore.trading.operational_awareness_models import OperationalAwarenessMode, OperationalAwarenessResult, OperationalConfidenceScore, OperationalHealthStatus
from agicore.trading.recovery_resilience_models import RecoveryMode, RecoveryResilienceResult, ResilienceScore
from agicore.trading.reward_models import RewardBreakdown, RewardComponent, RewardEvaluationResult, RewardLabel
from agicore.trading.strategic_arbitration_models import ArbitrationDecision, ArbitrationMode, ArbitrationPriority, ArbitrationResult, ArbitrationSeverity, ArbitrationState, PriorityGraph
from agicore.trading.strategic_memory_models import StrategicCyclePhase, StrategicDriftSignal, StrategicTimelineAnalysis
from agicore.trading.strategic_planning_models import StrategicHorizon, StrategicObjective, StrategicPlan, StrategicPlanningResult, StrategicPlanStatus
from agicore.trading.system_integrity_models import SystemIntegrityResult, SystemIntegrityStatus
from agicore.trading.tactical_execution_models import TacticalExecutionQuality, TacticalExecutionResult, TacticalScoreBreakdown


def _timeline(health: int = 85, degraded: bool = False, improvement: bool = True, drifts: tuple[StrategicDriftSignal, ...] = ()) -> StrategicTimelineAnalysis:
    return StrategicTimelineAnalysis(5, (StrategicCyclePhase.GROWTH,), drifts, None, None, health, health, improvement, degraded, (), "timeline")


def _strategy(status: StrategicPlanStatus = StrategicPlanStatus.ACTIVE, objective: StrategicObjective = StrategicObjective.CAPITAL_PRESERVATION, score: int = 85) -> StrategicPlanningResult:
    plan = StrategicPlan(StrategicHorizon.WEEKLY, objective, status, ("objective",), ("risk",), 3, 1.0, "discipline")
    return StrategicPlanningResult(plan, score, (), (), "strategy")


def _awareness(score: int = 85, health: OperationalHealthStatus = OperationalHealthStatus.HEALTHY) -> OperationalAwarenessResult:
    breakdown = OperationalConfidenceScore(score, score, score, score, score, score, score, score, score)
    return OperationalAwarenessResult(OperationalAwarenessMode.STABLE, health, score, breakdown, (), (), (), (), 20, score, "monitor", (), "awareness")


def _mission(mode: MissionContinuityMode = MissionContinuityMode.FULL_OPERATION, score: int = 85) -> MissionContinuityResult:
    breakdown = MissionContinuityScore(score, score, score, score, score, score, score)
    return MissionContinuityResult(mode, score, breakdown, (), (), (), (), (), (), (), (), "mission")


def _recovery(mode: RecoveryMode = RecoveryMode.NORMAL, score: int = 85) -> RecoveryResilienceResult:
    breakdown = ResilienceScore(score, score, score, score, score, score, score)
    return RecoveryResilienceResult(mode, score, breakdown, (), (), (), (), (), (), (), "recovery")


def _integrity(status: SystemIntegrityStatus = SystemIntegrityStatus.HEALTHY, score: int = 85) -> SystemIntegrityResult:
    return SystemIntegrityResult(status, score, (), (), (), "action", (), (), "integrity")


def _alignment(mode: IntentAlignmentMode = IntentAlignmentMode.FULLY_ALIGNED, score: int = 85) -> IntentAlignmentResult:
    confidence = IntentConfidence(score, score, score, score, score, score, score)
    return IntentAlignmentResult(mode, IntentAlignmentState.ALIGNED, score, confidence, (IntentPriority.SAFETY,), (), (), (), (), "mission", score, (), "alignment")


def _arbitration(decision: ArbitrationDecision = ArbitrationDecision.CONTINUE_OPERATION, mode: ArbitrationMode = ArbitrationMode.NORMAL_OPERATION, score: int = 85) -> ArbitrationResult:
    graph = PriorityGraph((ArbitrationPriority.SURVIVAL,), (), (ArbitrationPriority.PERFORMANCE,), ArbitrationPriority.PERFORMANCE)
    return ArbitrationResult(mode, ArbitrationState.STABLE, decision, ArbitrationSeverity.LOW, score, ArbitrationPriority.PERFORMANCE, (), (), (), graph, (), decision == ArbitrationDecision.EMERGENCY_LOCKDOWN, "arbitration", ())


def _consensus(decision: ConsensusDecision = ConsensusDecision.APPROVE_COLLECTIVE_DECISION, mode: ConsensusMode = ConsensusMode.NORMAL_CONSENSUS, score: int = 85) -> ConsensusResult:
    confidence = CollectiveConfidence(score, score, score, score, score, score)
    graph = ConsensusGraph((), (), None, (), ())
    return ConsensusResult(mode, ConsensusState.STABLE, decision, score, confidence, (), graph, {}, (), (), (), (), "consensus", ())


def _behavior(score: int = 85, pressure: BehavioralPressureLevel = BehavioralPressureLevel.LOW) -> BehavioralStabilityResult:
    return BehavioralStabilityResult(score, pressure, BehavioralRecoveryState.STABLE, BehavioralStabilityScore(score, score, score, score, score, score), (), (), (), ())


def _tactical(quality: TacticalExecutionQuality = TacticalExecutionQuality.GOOD) -> TacticalExecutionResult:
    return TacticalExecutionResult(quality, 85, TacticalScoreBreakdown(85, 85, 85, 85, 85, 85, 85), (), (), (), ())


def _reward(label: RewardLabel = RewardLabel.GOOD_DECISION, normalized: int = 85) -> RewardEvaluationResult:
    component = RewardComponent("x", 0, "reason")
    breakdown = RewardBreakdown(component, component, component, component, component, component, component, component, component, component, component)
    return RewardEvaluationResult(10, normalized, label, breakdown, (), ())


def _orchestrator(confidence: int = 85, decision: OrchestratorDecision = OrchestratorDecision.CONTINUE_COORDINATED_OPERATION) -> GlobalOrchestratorResult:
    health = SystemHealthSnapshot(confidence, confidence, confidence, confidence, confidence, confidence, confidence, confidence, confidence)
    state = GlobalSystemState(OrchestratorMode.COORDINATED_OPERATION, OrchestratorPriority.STRATEGY, health, ("system_integrity",), (), (), (), ())
    graph = OrchestrationGraph(("system_integrity",), (), None, (), ())
    cycle = OrchestratorCycle("c1", OrchestratorMode.COORDINATED_OPERATION, OrchestratorPriority.STRATEGY, (), (), False, False)
    coordination = CoordinationResult(CoordinationState(OrchestratorMode.COORDINATED_OPERATION, OrchestratorPriority.STRATEGY, confidence, (), ()), decision, (), cycle, (), "coordination")
    return GlobalOrchestratorResult(state, graph, coordination, decision, confidence, (), (), "orchestrator")


def test_builds_stable_growth_scenario_when_inputs_are_healthy() -> None:
    scenarios = build_future_scenarios(
        strategic_timeline_analysis=_timeline(),
        system_integrity=_integrity(),
        behavioral_stability=_behavior(),
        reward_evaluation=_reward(),
    )

    assert FutureScenarioType.STABLE_GROWTH in {scenario.scenario_type for scenario in scenarios}


def test_projects_controlled_recovery_when_drawdown_persists() -> None:
    scenarios = build_future_scenarios(
        strategic_timeline_analysis=_timeline(45, True, False, (StrategicDriftSignal.PERSISTENT_DRAWDOWN, StrategicDriftSignal.STRATEGIC_DEGRADATION)),
        recovery_resilience=_recovery(RecoveryMode.STABILIZE, 45),
        reward_evaluation=_reward(RewardLabel.BAD_DECISION, 35),
    )
    trajectory = project_strategic_trajectory(strategic_timeline_analysis=_timeline(45, True, False, (StrategicDriftSignal.PERSISTENT_DRAWDOWN,)), scenarios=scenarios)

    assert FutureScenarioType.CONTROLLED_RECOVERY in {scenario.scenario_type for scenario in scenarios}
    assert trajectory.trajectory_label == "multi_phase_recovery"


def test_detects_future_risks_from_degraded_evidence() -> None:
    scenarios = build_future_scenarios(
        strategic_timeline_analysis=_timeline(35, True, False, (StrategicDriftSignal.PERSISTENT_DRAWDOWN, StrategicDriftSignal.BEHAVIORAL_DRIFT)),
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 25),
        behavioral_stability=_behavior(30, BehavioralPressureLevel.HIGH),
        tactical_execution=_tactical(TacticalExecutionQuality.WEAK),
        mission_continuity=_mission(MissionContinuityMode.SURVIVAL_CONTINUITY, 30),
    )
    risks = evaluate_long_horizon_risks(
        strategic_timeline_analysis=_timeline(35, True, False, (StrategicDriftSignal.PERSISTENT_DRAWDOWN,)),
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 25),
        behavioral_stability=_behavior(30, BehavioralPressureLevel.HIGH),
        tactical_execution=_tactical(TacticalExecutionQuality.WEAK),
        mission_continuity=_mission(MissionContinuityMode.SURVIVAL_CONTINUITY, 30),
        scenarios=scenarios,
    )

    assert PlanningRisk.FUTURE_DRAWDOWN_RISK in risks
    assert PlanningRisk.SYSTEM_INSTABILITY_RISK in risks
    assert PlanningRisk.EXECUTION_QUALITY_DECAY in risks
    assert PlanningRisk.CONTINUITY_BREAKDOWN_RISK in risks


def test_safe_mode_decision_when_multiple_future_paths_are_dangerous() -> None:
    result = plan_long_horizon(
        global_orchestrator=_orchestrator(25, OrchestratorDecision.ENTER_SAFE_GLOBAL_MODE),
        strategic_arbitration=_arbitration(ArbitrationDecision.ENABLE_SAFE_MODE, ArbitrationMode.PROTECTIVE_ARBITRATION, 25),
        collective_consensus=_consensus(ConsensusDecision.ENTER_SAFE_MODE, ConsensusMode.SAFETY_FIRST, 25),
        intent_alignment=_alignment(IntentAlignmentMode.CRITICAL_REALIGNMENT, 20),
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 20),
        mission_continuity=_mission(MissionContinuityMode.SURVIVAL_CONTINUITY, 20),
        strategic_timeline_analysis=_timeline(25, True, False, (StrategicDriftSignal.PERSISTENT_DRAWDOWN, StrategicDriftSignal.STRATEGIC_DEGRADATION)),
    )

    assert result.decision == PlanningDecision.ENTER_LONG_HORIZON_SAFE_MODE
    assert PlanningRecommendation.PRIORITIZE_CAPITAL_PRESERVATION in result.recommendations


def test_low_confidence_projection_observes_before_action() -> None:
    decision = decide_long_horizon_plan()

    assert decision == PlanningDecision.OBSERVE_BEFORE_ACTION


def test_horizon_plan_graph_contains_scenarios_and_phases() -> None:
    scenarios = build_future_scenarios(strategic_timeline_analysis=_timeline(), reward_evaluation=_reward())
    trajectory = project_strategic_trajectory(strategic_timeline_analysis=_timeline(), reward_evaluation=_reward(), scenarios=scenarios)
    graph = build_horizon_plan_graph(strategic_timeline_analysis=_timeline(), reward_evaluation=_reward(), scenarios=scenarios, trajectory=trajectory)

    assert "current_state" in graph.nodes
    assert graph.critical_path
    assert graph.edges


def test_projection_confidence_uses_available_scores() -> None:
    confidence = compute_projection_confidence(
        global_orchestrator=_orchestrator(90),
        strategic_timeline_analysis=_timeline(90),
        system_integrity=_integrity(SystemIntegrityStatus.HEALTHY, 90),
        reward_evaluation=_reward(RewardLabel.EXCELLENT_DECISION, 95),
    )

    assert confidence >= 75


def test_recommendations_for_recovery_and_behavioral_guardrails() -> None:
    recommendations = generate_long_horizon_recommendations(
        strategic_timeline_analysis=_timeline(35, True, False, (StrategicDriftSignal.PERSISTENT_DRAWDOWN,)),
        behavioral_stability=_behavior(35, BehavioralPressureLevel.EXTREME),
        recovery_resilience=_recovery(RecoveryMode.STABILIZE, 40),
        reward_evaluation=_reward(RewardLabel.BAD_DECISION, 30),
    )

    assert PlanningRecommendation.PREPARE_RECOVERY_SEQUENCE in recommendations
    assert PlanningRecommendation.STRENGTHEN_BEHAVIORAL_GUARDS in recommendations
    assert PlanningRecommendation.UPDATE_STRATEGIC_MEMORY in recommendations


def test_learning_overadaptation_freezes_policy_expansion() -> None:
    risks = evaluate_long_horizon_risks(
        strategic_result=_strategy(StrategicPlanStatus.ACTIVE, StrategicObjective.POLICY_VALIDATION, 40),
        system_integrity=_integrity(SystemIntegrityStatus.UNSTABLE, 40),
    )
    recommendations = generate_long_horizon_recommendations(
        strategic_result=_strategy(StrategicPlanStatus.ACTIVE, StrategicObjective.POLICY_VALIDATION, 40),
        system_integrity=_integrity(SystemIntegrityStatus.UNSTABLE, 40),
    )

    assert PlanningRisk.LEARNING_OVERADAPTATION_RISK in risks
    assert PlanningRecommendation.FREEZE_POLICY_EXPANSION in recommendations


def test_render_long_horizon_markdown_contains_required_sections() -> None:
    result = plan_long_horizon(
        horizon=PlanningHorizon.WEEKLY,
        global_orchestrator=_orchestrator(),
        strategic_timeline_analysis=_timeline(),
        strategic_result=_strategy(),
        operational_awareness=_awareness(),
        system_integrity=_integrity(),
        reward_evaluation=_reward(),
    )
    markdown = render_long_horizon_planning_markdown(result)

    assert "# Autonomous Long-Horizon Planning Engine" in markdown
    assert "## Long-Horizon Planning State" in markdown
    assert "## Planning Horizon" in markdown
    assert "## Future Scenarios" in markdown
    assert "## Strategic Trajectory" in markdown
    assert "## Risks" in markdown
    assert "## Plan Graph" in markdown
    assert "## Decision" in markdown
    assert "## Recommendations" in markdown
    assert "## AGIcore Future Outlook" in markdown
    assert "no broker" in markdown
