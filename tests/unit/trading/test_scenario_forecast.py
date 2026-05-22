"""Unit tests for the offline Autonomous Scenario Forecast Engine."""
from __future__ import annotations

from agicore.trading.behavioral_stability_models import BehavioralPressureLevel, BehavioralRecoveryState, BehavioralStabilityResult, BehavioralStabilityScore
from agicore.trading.cognitive_adaptation_models import CognitiveAdaptationMode, CognitiveAdaptationResult, CognitiveFlexibilityScore, CognitiveLoadLevel
from agicore.trading.collective_consensus_models import CollectiveConfidence, ConsensusDecision, ConsensusGraph, ConsensusMode, ConsensusResult, ConsensusState
from agicore.trading.global_orchestrator_models import GlobalOrchestratorResult, GlobalSystemState, OrchestrationGraph, OrchestratorDecision, OrchestratorMode, OrchestratorPriority, SystemHealthSnapshot
from agicore.trading.intent_alignment_models import IntentAlignmentMode, IntentAlignmentResult, IntentAlignmentState, IntentConfidence, IntentPriority
from agicore.trading.long_horizon_planning_models import FutureProjection, FutureScenario, FutureScenarioType, HorizonPlanGraph, LongHorizonPlanningResult, PlanningDecision, PlanningHorizon, PlanningRisk, StrategicTrajectory
from agicore.trading.mission_continuity_models import MissionContinuityMode, MissionContinuityResult, MissionContinuityScore
from agicore.trading.operational_awareness_models import OperationalAwarenessMode, OperationalAwarenessResult, OperationalConfidenceScore, OperationalHealthStatus
from agicore.trading.recovery_resilience_models import RecoveryMode, RecoveryResilienceResult, ResilienceScore
from agicore.trading.reward_models import RewardBreakdown, RewardComponent, RewardEvaluationResult, RewardLabel
from agicore.trading.scenario_forecast import (
    build_forecast_risk_map,
    build_forecast_scenarios,
    compute_forecast_stability_score,
    decide_forecast_path,
    detect_forecast_bifurcations,
    estimate_scenario_probability,
    forecast_scenarios,
    generate_forecast_recommendations,
    render_scenario_forecast_markdown,
)
from agicore.trading.scenario_forecast_models import ForecastDecision, ForecastProbabilityBand, ForecastRecommendation, ForecastScenarioType
from agicore.trading.strategic_arbitration_models import ArbitrationDecision, ArbitrationMode, ArbitrationPriority, ArbitrationResult, ArbitrationSeverity, ArbitrationState, PriorityGraph
from agicore.trading.strategic_memory_models import StrategicCyclePhase, StrategicDriftSignal, StrategicTimelineAnalysis
from agicore.trading.system_integrity_models import SystemIntegrityResult, SystemIntegrityStatus


def _timeline(health: int = 85, degraded: bool = False, drifts: tuple[StrategicDriftSignal, ...] = ()) -> StrategicTimelineAnalysis:
    return StrategicTimelineAnalysis(5, (StrategicCyclePhase.GROWTH,), drifts, None, None, health, health, not degraded, degraded, (), "timeline")


def _behavior(score: int = 85, pressure: BehavioralPressureLevel = BehavioralPressureLevel.LOW) -> BehavioralStabilityResult:
    return BehavioralStabilityResult(score, pressure, BehavioralRecoveryState.STABLE, BehavioralStabilityScore(score, score, score, score, score, score), (), (), (), ())


def _cognitive(score: int = 85, load: CognitiveLoadLevel = CognitiveLoadLevel.LOW) -> CognitiveAdaptationResult:
    return CognitiveAdaptationResult(CognitiveAdaptationMode.ADAPT, load, score, CognitiveFlexibilityScore(score, score, score, score, score, score), (), (), (), ())


def _integrity(status: SystemIntegrityStatus = SystemIntegrityStatus.HEALTHY, score: int = 85) -> SystemIntegrityResult:
    return SystemIntegrityResult(status, score, (), (), (), "action", (), (), "integrity")


def _awareness(score: int = 85, health: OperationalHealthStatus = OperationalHealthStatus.HEALTHY) -> OperationalAwarenessResult:
    breakdown = OperationalConfidenceScore(score, score, score, score, score, score, score, score, score)
    return OperationalAwarenessResult(OperationalAwarenessMode.CRITICAL if health == OperationalHealthStatus.CRITICAL else OperationalAwarenessMode.STABLE, health, score, breakdown, (), (), (), (), 20, score, "monitor", (), "awareness")


def _mission(mode: MissionContinuityMode = MissionContinuityMode.FULL_OPERATION, score: int = 85) -> MissionContinuityResult:
    breakdown = MissionContinuityScore(score, score, score, score, score, score, score)
    return MissionContinuityResult(mode, score, breakdown, (), (), (), (), (), (), (), (), "mission")


def _recovery(mode: RecoveryMode = RecoveryMode.NORMAL, score: int = 85) -> RecoveryResilienceResult:
    breakdown = ResilienceScore(score, score, score, score, score, score, score)
    return RecoveryResilienceResult(mode, score, breakdown, (), (), (), (), (), (), (), "recovery")


def _alignment(mode: IntentAlignmentMode = IntentAlignmentMode.FULLY_ALIGNED, score: int = 85) -> IntentAlignmentResult:
    confidence = IntentConfidence(score, score, score, score, score, score, score)
    return IntentAlignmentResult(mode, IntentAlignmentState.ALIGNED, score, confidence, (IntentPriority.SAFETY,), (), (), (), (), "mission", score, (), "alignment")


def _arbitration(decision: ArbitrationDecision = ArbitrationDecision.CONTINUE_OPERATION, mode: ArbitrationMode = ArbitrationMode.NORMAL_OPERATION, score: int = 85) -> ArbitrationResult:
    graph = PriorityGraph((ArbitrationPriority.SURVIVAL,), (), (ArbitrationPriority.PERFORMANCE,), ArbitrationPriority.PERFORMANCE)
    return ArbitrationResult(mode, ArbitrationState.STABLE, decision, ArbitrationSeverity.CRITICAL if decision == ArbitrationDecision.EMERGENCY_LOCKDOWN else ArbitrationSeverity.LOW, score, ArbitrationPriority.PERFORMANCE, (), (), (), graph, (), decision == ArbitrationDecision.EMERGENCY_LOCKDOWN, "arbitration", ())


def _consensus(decision: ConsensusDecision = ConsensusDecision.APPROVE_COLLECTIVE_DECISION, mode: ConsensusMode = ConsensusMode.NORMAL_CONSENSUS, score: int = 85) -> ConsensusResult:
    confidence = CollectiveConfidence(score, score, score, score, score, score)
    graph = ConsensusGraph((), (), None, (), ())
    return ConsensusResult(mode, ConsensusState.STABLE, decision, score, confidence, (), graph, {}, (), (), (), (), "consensus", ())


def _reward(label: RewardLabel = RewardLabel.GOOD_DECISION, normalized: int = 85) -> RewardEvaluationResult:
    component = RewardComponent("x", 0, "reason")
    breakdown = RewardBreakdown(component, component, component, component, component, component, component, component, component, component, component)
    return RewardEvaluationResult(10, normalized, label, breakdown, (), ())


def _long_plan(decision: PlanningDecision = PlanningDecision.PROCEED_WITH_PLAN, confidence: int = 85, risks: tuple[PlanningRisk, ...] = ()) -> LongHorizonPlanningResult:
    scenario = FutureScenario(FutureScenarioType.STABLE_GROWTH, 70, 40, PlanningHorizon.WEEKLY, "stable", "growth")
    projection = FutureProjection(PlanningHorizon.WEEKLY, confidence, 30, confidence, confidence, confidence, confidence)
    trajectory = StrategicTrajectory("controlled_growth", "current", "target", ("observe", "grow"), "stable", 5, ())
    graph = HorizonPlanGraph(PlanningHorizon.WEEKLY, ("current",), (), ("current",), ())
    return LongHorizonPlanningResult(PlanningHorizon.WEEKLY, decision, confidence, (scenario,), projection, trajectory, risks, graph, (), (), "plan")


def _orchestrator(confidence: int = 85, mode: OrchestratorMode = OrchestratorMode.COORDINATED_OPERATION, decision: OrchestratorDecision = OrchestratorDecision.CONTINUE_COORDINATED_OPERATION) -> GlobalOrchestratorResult:
    health = SystemHealthSnapshot(confidence, confidence, confidence, confidence, confidence, confidence, confidence, confidence, confidence)
    state = GlobalSystemState(mode, OrchestratorPriority.STRATEGY, health, ("system_integrity",), (), (), (), ())
    graph = OrchestrationGraph(("system_integrity",), (), None, (), ())
    return GlobalOrchestratorResult(state, graph, None, decision, confidence, (), (), "orchestrator")


def test_builds_stable_forecast_when_inputs_are_healthy() -> None:
    scenarios = build_forecast_scenarios(
        long_horizon_plan=_long_plan(),
        strategic_timeline_analysis=_timeline(),
        system_integrity=_integrity(),
        behavioral_stability=_behavior(),
    )

    assert ForecastScenarioType.STABLE_CONTINUATION in {scenario.scenario_type for scenario in scenarios}
    assert ForecastScenarioType.CONTROLLED_GROWTH in {scenario.scenario_type for scenario in scenarios}


def test_probability_band_tracks_probability_score() -> None:
    probability = estimate_scenario_probability(
        ForecastScenarioType.SYSTEM_DEGRADATION,
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 25),
        global_orchestrator=_orchestrator(25),
    )
    scenarios = build_forecast_scenarios(system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 25), global_orchestrator=_orchestrator(25))
    degradation = next(s for s in scenarios if s.scenario_type == ForecastScenarioType.SYSTEM_DEGRADATION)

    assert probability >= 60
    assert degradation.probability_band in {ForecastProbabilityBand.HIGH, ForecastProbabilityBand.VERY_HIGH}


def test_detects_recovery_bifurcation_when_recovery_outcomes_are_plausible() -> None:
    scenarios = build_forecast_scenarios(
        recovery_resilience=_recovery(RecoveryMode.STABILIZE, 50),
        strategic_timeline_analysis=_timeline(45, True, (StrategicDriftSignal.PERSISTENT_DRAWDOWN,)),
        reward_evaluation=_reward(RewardLabel.BAD_DECISION, 40),
    )
    bifurcations = detect_forecast_bifurcations(scenarios=scenarios)

    assert any(b.positive_scenario == ForecastScenarioType.RECOVERY_SUCCESS and b.negative_scenario == ForecastScenarioType.RECOVERY_FAILURE for b in bifurcations)


def test_risk_map_covers_all_categories() -> None:
    risk_map = build_forecast_risk_map(
        strategic_timeline_analysis=_timeline(40, True, (StrategicDriftSignal.STRATEGIC_DEGRADATION,)),
        behavioral_stability=_behavior(35, BehavioralPressureLevel.HIGH),
        cognitive_adaptation=_cognitive(35, CognitiveLoadLevel.HIGH),
        system_integrity=_integrity(SystemIntegrityStatus.UNSTABLE, 35),
        mission_continuity=_mission(MissionContinuityMode.SURVIVAL_CONTINUITY, 35),
    )

    assert risk_map.strategy >= 60
    assert risk_map.behavior >= 60
    assert risk_map.cognition >= 60
    assert risk_map.integrity >= 60
    assert risk_map.continuity >= 60
    assert risk_map.mission >= 60


def test_safe_mode_decision_for_critical_forecast_paths() -> None:
    result = forecast_scenarios(
        long_horizon_plan=_long_plan(PlanningDecision.ENTER_LONG_HORIZON_SAFE_MODE, 20, (PlanningRisk.SYSTEM_INSTABILITY_RISK, PlanningRisk.CONTINUITY_BREAKDOWN_RISK)),
        global_orchestrator=_orchestrator(20, OrchestratorMode.EMERGENCY_ORCHESTRATION, OrchestratorDecision.EMERGENCY_HALT_ROUTING),
        strategic_arbitration=_arbitration(ArbitrationDecision.EMERGENCY_LOCKDOWN, ArbitrationMode.EMERGENCY_LOCKDOWN, 20),
        collective_consensus=_consensus(ConsensusDecision.EMERGENCY_HALT, ConsensusMode.EMERGENCY_CONSENSUS, 20),
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 20),
        operational_awareness=_awareness(20, OperationalHealthStatus.CRITICAL),
        mission_continuity=_mission(MissionContinuityMode.SURVIVAL_CONTINUITY, 20),
        cognitive_adaptation=_cognitive(20, CognitiveLoadLevel.OVERLOADED),
    )

    assert result.decision == ForecastDecision.ENTER_FORECAST_SAFE_MODE
    assert ForecastScenarioType.EMERGENCY_LOCKDOWN_PATH in result.critical_scenarios
    assert ForecastRecommendation.REDUCE_RISK_EXPOSURE in result.recommendations


def test_observation_when_forecast_confidence_is_unknown_low() -> None:
    decision = decide_forecast_path()

    assert decision == ForecastDecision.REQUIRE_OBSERVATION_WINDOW


def test_stability_score_penalizes_dangerous_scenarios() -> None:
    scenarios = build_forecast_scenarios(
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 20),
        behavioral_stability=_behavior(20, BehavioralPressureLevel.EXTREME),
        cognitive_adaptation=_cognitive(20, CognitiveLoadLevel.OVERLOADED),
    )
    stability = compute_forecast_stability_score(scenarios=scenarios, system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 20), behavioral_stability=_behavior(20, BehavioralPressureLevel.EXTREME))

    assert stability.scenario_balance_score < 70
    assert stability.system_health_score < 50


def test_recommendations_for_strategy_integrity_and_behavior_risks() -> None:
    recommendations = generate_forecast_recommendations(
        strategic_timeline_analysis=_timeline(35, True, (StrategicDriftSignal.STRATEGIC_DEGRADATION,)),
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 25),
        behavioral_stability=_behavior(30, BehavioralPressureLevel.EXTREME),
        long_horizon_plan=_long_plan(PlanningDecision.REDUCE_RISK_PLAN, 40, (PlanningRisk.LEARNING_OVERADAPTATION_RISK,)),
    )

    assert ForecastRecommendation.PROTECT_STRATEGIC_MEMORY in recommendations
    assert ForecastRecommendation.CHECK_SYSTEM_INTEGRITY in recommendations
    assert ForecastRecommendation.STABILIZE_BEHAVIOR in recommendations
    assert ForecastRecommendation.FREEZE_POLICY_EXPANSION in recommendations


def test_survivable_scenarios_exclude_emergency_lockdown_path() -> None:
    result = forecast_scenarios(
        strategic_arbitration=_arbitration(ArbitrationDecision.EMERGENCY_LOCKDOWN, ArbitrationMode.EMERGENCY_LOCKDOWN, 15),
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 15),
        operational_awareness=_awareness(15, OperationalHealthStatus.CRITICAL),
    )

    assert ForecastScenarioType.EMERGENCY_LOCKDOWN_PATH not in result.survivable_scenarios


def test_render_scenario_forecast_markdown_contains_required_sections() -> None:
    result = forecast_scenarios(
        long_horizon_plan=_long_plan(),
        global_orchestrator=_orchestrator(),
        strategic_timeline_analysis=_timeline(),
        system_integrity=_integrity(),
        behavioral_stability=_behavior(),
        reward_evaluation=_reward(),
    )
    markdown = render_scenario_forecast_markdown(result)

    assert "# Autonomous Scenario Forecast Engine" in markdown
    assert "## Scenario Forecast State" in markdown
    assert "## Forecast Scenarios" in markdown
    assert "## Probability Bands" in markdown
    assert "## Bifurcations" in markdown
    assert "## Risk Map" in markdown
    assert "## Stability Score" in markdown
    assert "## Forecast Decision" in markdown
    assert "## Recommendations" in markdown
    assert "## AGIcore Forecast Outlook" in markdown
    assert "no broker" in markdown
