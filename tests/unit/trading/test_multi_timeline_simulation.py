from __future__ import annotations

from types import SimpleNamespace

from agicore.trading.behavioral_stability_models import BehavioralPressureLevel
from agicore.trading.cognitive_adaptation_models import CognitiveLoadLevel
from agicore.trading.intent_alignment_models import IntentAlignmentMode
from agicore.trading.long_horizon_planning_models import PlanningDecision, PlanningRisk
from agicore.trading.mission_continuity_models import MissionContinuityMode
from agicore.trading.multi_timeline_simulation import (
    build_timeline_comparison_graph,
    build_timeline_scenarios,
    compare_timeline_outcomes,
    compute_timeline_divergence,
    compute_timeline_survivability,
    decide_timeline_path,
    generate_timeline_recommendations,
    render_multi_timeline_simulation_markdown,
    run_multi_timeline_simulation,
    simulate_timeline_states,
)
from agicore.trading.multi_timeline_simulation_models import (
    TimelineDecision,
    TimelineOutcome,
    TimelineRecommendation,
    TimelineRisk,
    TimelineScenario,
)
from agicore.trading.operational_awareness_models import OperationalHealthStatus
from agicore.trading.recovery_resilience_models import RecoveryMode
from agicore.trading.reward_models import RewardLabel
from agicore.trading.scenario_forecast_models import ForecastDecision, ForecastRiskMap, ForecastScenarioType, ForecastStabilityScore, ScenarioForecastResult
from agicore.trading.strategic_arbitration_models import ArbitrationDecision, ArbitrationMode
from agicore.trading.strategic_memory_models import StrategicDriftSignal
from agicore.trading.strategy_evolution_models import StrategyEvolutionDecision, StrategyEvolutionMode
from agicore.trading.system_integrity_models import SystemIntegrityStatus


def _forecast(decision=ForecastDecision.CONTINUE_CURRENT_PATH, score=78, critical=(), survivable=(ForecastScenarioType.STABLE_CONTINUATION,)):
    return ScenarioForecastResult(
        decision=decision,
        forecast_stability_score=score,
        stability_breakdown=ForecastStabilityScore(80, 90, 75, 75, 80, 70),
        scenarios=(),
        bifurcations=(),
        risk_map=ForecastRiskMap(25, 25, 25, 25, 25, 25, 25),
        recommendations=(),
        survivable_scenarios=survivable,
        critical_scenarios=critical,
        events=(),
        summary="forecast",
    )


def _plan(decision=PlanningDecision.PROCEED_WITH_PLAN, stability=78, recovery=70, drawdown=20, behavior=75, risks=()):
    projection = SimpleNamespace(
        projected_stability_score=stability,
        projected_recovery_score=recovery,
        projected_drawdown_risk_score=drawdown,
        projected_behavior_score=behavior,
    )
    return SimpleNamespace(decision=decision, projection=projection, projection_confidence=75, risks=risks)


def _strategy_evolution(score=76, decision=StrategyEvolutionDecision.KEEP_CURRENT_STRATEGY, mode=StrategyEvolutionMode.STABLE_PRESERVATION, evidence=75):
    breakdown = SimpleNamespace(evidence_score=evidence)
    return SimpleNamespace(fitness_score=score, decision=decision, mode=mode, fitness_breakdown=breakdown)


def _behavior(score=80, pressure=BehavioralPressureLevel.LOW):
    return SimpleNamespace(stability_score=score, pressure_level=pressure)


def _integrity(status=SystemIntegrityStatus.HEALTHY, score=82):
    return SimpleNamespace(status=status, integrity_score=score)


def _awareness(health=OperationalHealthStatus.HEALTHY, score=82):
    return SimpleNamespace(health_status=health, operational_confidence_score=score)


def _recovery(mode=RecoveryMode.NORMAL, score=75):
    return SimpleNamespace(mode=mode, resilience_score=score)


def _mission(mode=MissionContinuityMode.FULL_OPERATION, score=80):
    return SimpleNamespace(mode=mode, continuity_score=score)


def _intent(mode=IntentAlignmentMode.FULLY_ALIGNED):
    return SimpleNamespace(mode=mode)


def _arbitration(decision=ArbitrationDecision.CONTINUE_OPERATION, mode=ArbitrationMode.NORMAL_OPERATION):
    return SimpleNamespace(decision=decision, mode=mode)


def _timeline(health=80, degraded=False, drifts=()):
    return SimpleNamespace(strategic_health_score=health, degradation_detected=degraded, drift_signals=drifts)


def _cognitive(load=CognitiveLoadLevel.LOW):
    return SimpleNamespace(load_level=load)


def _reward(label=RewardLabel.GOOD_DECISION, normalized=75):
    return SimpleNamespace(reward_label=label, normalized_reward=normalized)


def test_builds_baseline_and_growth_timeline_when_inputs_are_healthy() -> None:
    scenarios = build_timeline_scenarios(
        scenario_forecast=_forecast(),
        long_horizon_plan=_plan(),
        strategy_evolution=_strategy_evolution(),
        system_integrity=_integrity(),
        behavioral_stability=_behavior(),
    )

    assert TimelineScenario.BASELINE_TIMELINE in scenarios
    assert TimelineScenario.GROWTH_TIMELINE in scenarios


def test_builds_safe_recovery_and_risk_timelines_from_degraded_inputs() -> None:
    scenarios = build_timeline_scenarios(
        scenario_forecast=_forecast(ForecastDecision.ENTER_FORECAST_SAFE_MODE, 35, critical=(ForecastScenarioType.SYSTEM_DEGRADATION,), survivable=(ForecastScenarioType.RECOVERY_SUCCESS,)),
        long_horizon_plan=_plan(PlanningDecision.PRIORITIZE_RECOVERY, risks=(PlanningRisk.STRATEGIC_DRIFT_RISK,)),
        recovery_resilience=_recovery(RecoveryMode.STABILIZE, 42),
        system_integrity=_integrity(SystemIntegrityStatus.DEGRADED, 45),
        behavioral_stability=_behavior(35, BehavioralPressureLevel.HIGH),
    )

    assert TimelineScenario.SAFE_TIMELINE in scenarios
    assert TimelineScenario.RECOVERY_TIMELINE in scenarios
    assert TimelineScenario.BEHAVIORAL_RISK_TIMELINE in scenarios
    assert TimelineScenario.SYSTEM_RISK_TIMELINE in scenarios


def test_simulates_outcomes_for_safe_recovery_and_emergency_timelines() -> None:
    states = simulate_timeline_states(
        requested_timelines=(TimelineScenario.SAFE_TIMELINE, TimelineScenario.RECOVERY_TIMELINE, TimelineScenario.EMERGENCY_TIMELINE),
        scenario_forecast=_forecast(ForecastDecision.ENTER_FORECAST_SAFE_MODE, 45),
        long_horizon_plan=_plan(PlanningDecision.PRIORITIZE_RECOVERY, stability=45, recovery=60),
        system_integrity=_integrity(SystemIntegrityStatus.DEGRADED, 40),
    )
    by_scenario = {state.scenario: state.outcome for state in states}

    assert by_scenario[TimelineScenario.SAFE_TIMELINE] == TimelineOutcome.SAFE_MODE
    assert by_scenario[TimelineScenario.RECOVERY_TIMELINE] in {TimelineOutcome.RECOVERING, TimelineOutcome.DEGRADED, TimelineOutcome.STABLE}
    assert by_scenario[TimelineScenario.EMERGENCY_TIMELINE] == TimelineOutcome.EMERGENCY_STOP


def test_computes_divergence_against_baseline() -> None:
    states = simulate_timeline_states(
        requested_timelines=(TimelineScenario.BASELINE_TIMELINE, TimelineScenario.SYSTEM_RISK_TIMELINE),
        scenario_forecast=_forecast(),
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 30),
        operational_awareness=_awareness(OperationalHealthStatus.CRITICAL, 35),
    )
    divergences = compute_timeline_divergence(states=states)

    assert len(divergences) == 1
    assert divergences[0].alternative == TimelineScenario.SYSTEM_RISK_TIMELINE
    assert divergences[0].divergence_score > 0


def test_survivability_penalizes_emergency_timeline() -> None:
    states = simulate_timeline_states(
        requested_timelines=(TimelineScenario.BASELINE_TIMELINE, TimelineScenario.EMERGENCY_TIMELINE),
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 25),
        cognitive_adaptation=_cognitive(CognitiveLoadLevel.OVERLOADED),
        reward_evaluation=_reward(RewardLabel.DANGEROUS_DECISION, 20),
    )
    scores = compute_timeline_survivability(states=states)
    by_scenario = {score.scenario: score.survivability_score for score in scores}

    assert by_scenario[TimelineScenario.EMERGENCY_TIMELINE] < by_scenario[TimelineScenario.BASELINE_TIMELINE]


def test_compare_outcomes_detects_core_risks() -> None:
    risks = compare_timeline_outcomes(
        requested_timelines=(TimelineScenario.BASELINE_TIMELINE, TimelineScenario.EMERGENCY_TIMELINE, TimelineScenario.BEHAVIORAL_RISK_TIMELINE),
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 25),
        behavioral_stability=_behavior(30, BehavioralPressureLevel.EXTREME),
        intent_alignment=_intent(IntentAlignmentMode.MISALIGNED),
    )

    assert TimelineRisk.COLLAPSE_RISK in risks
    assert TimelineRisk.BEHAVIORAL_REGRESSION_RISK in risks
    assert TimelineRisk.INCOMPATIBLE_FUTURE_PATH in risks


def test_decision_requires_more_simulation_when_evidence_is_sparse() -> None:
    decision = decide_timeline_path()

    assert decision == TimelineDecision.REQUIRE_MORE_SIMULATION


def test_decision_enters_safe_mode_for_critical_timelines() -> None:
    decision = decide_timeline_path(
        scenario_forecast=_forecast(ForecastDecision.ENTER_FORECAST_SAFE_MODE, 25),
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 20),
        operational_awareness=_awareness(OperationalHealthStatus.CRITICAL, 20),
        cognitive_adaptation=_cognitive(CognitiveLoadLevel.OVERLOADED),
        strategic_arbitration=_arbitration(ArbitrationDecision.EMERGENCY_LOCKDOWN, ArbitrationMode.EMERGENCY_LOCKDOWN),
    )

    assert decision == TimelineDecision.ENTER_TIMELINE_SAFE_MODE


def test_graph_and_recommendations_prioritize_safe_and_recovery_paths() -> None:
    result = run_multi_timeline_simulation(
        scenario_forecast=_forecast(ForecastDecision.PRIORITIZE_SAFE_SCENARIO, 55, survivable=(ForecastScenarioType.RECOVERY_SUCCESS,)),
        long_horizon_plan=_plan(PlanningDecision.PRIORITIZE_RECOVERY, stability=50, recovery=70),
        recovery_resilience=_recovery(RecoveryMode.STABILIZE, 55),
        system_integrity=_integrity(SystemIntegrityStatus.DEGRADED, 45),
        behavioral_stability=_behavior(45, BehavioralPressureLevel.HIGH),
    )

    assert result.comparison_graph.recommended_path is not None
    assert TimelineRecommendation.PRESERVE_TIMELINE_MEMORY in result.recommendations
    assert any(
        recommendation in result.recommendations
        for recommendation in (TimelineRecommendation.PRIORITIZE_SAFE_TIMELINE, TimelineRecommendation.PRIORITIZE_RECOVERY_PATH)
    )


def test_render_multi_timeline_markdown_contains_required_sections() -> None:
    result = run_multi_timeline_simulation(
        scenario_forecast=_forecast(),
        long_horizon_plan=_plan(),
        strategy_evolution=_strategy_evolution(),
        behavioral_stability=_behavior(),
        system_integrity=_integrity(),
    )
    markdown = render_multi_timeline_simulation_markdown(result)

    assert "Multi-Timeline Simulation State" in markdown
    assert "Timeline Scenarios" in markdown
    assert "Timeline Outcomes" in markdown
    assert "Divergence Analysis" in markdown
    assert "Survivability Scores" in markdown
    assert "Comparison Graph" in markdown
    assert "Decision" in markdown
    assert "Recommendations" in markdown
    assert "AGIcore Timeline Outlook" in markdown
