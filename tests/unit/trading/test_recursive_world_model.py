from __future__ import annotations

from types import SimpleNamespace

from agicore.trading.cognitive_adaptation_models import CognitiveLoadLevel
from agicore.trading.global_orchestrator_models import OrchestratorDecision, OrchestratorMode, OrchestratorRisk
from agicore.trading.intent_alignment_models import IntentAlignmentMode
from agicore.trading.multi_timeline_simulation_models import TimelineDecision, TimelineOutcome, TimelineRisk
from agicore.trading.recursive_world_model import (
    build_world_model_graph,
    compute_world_model_coherence,
    decide_world_model_action,
    detect_world_model_risks,
    evaluate_recursive_world_model,
    evaluate_world_model_state,
    generate_world_model_recommendations,
    render_recursive_world_model_markdown,
    simulate_causal_impacts,
)
from agicore.trading.recursive_world_model_models import (
    WorldModelDecision,
    WorldModelLayer,
    WorldModelRecommendation,
    WorldModelRisk,
)
from agicore.trading.reward_models import RewardLabel
from agicore.trading.scenario_forecast_models import ForecastDecision, ForecastRiskMap, ForecastScenarioType, ForecastStabilityScore, ScenarioForecastResult
from agicore.trading.strategic_arbitration_models import ArbitrationDecision
from agicore.trading.strategic_memory_models import StrategicDriftSignal
from agicore.trading.strategy_evolution_models import StrategyEvolutionDecision, StrategyEvolutionMode
from agicore.trading.system_integrity_models import SystemIntegrityStatus


def _forecast(decision=ForecastDecision.CONTINUE_CURRENT_PATH, score=78, confidence=72, critical=()):
    return ScenarioForecastResult(
        decision=decision,
        forecast_stability_score=score,
        stability_breakdown=ForecastStabilityScore(80, 90, 75, 75, 80, confidence),
        scenarios=(),
        bifurcations=(),
        risk_map=ForecastRiskMap(25, 25, 25, 25, 25, 25, 25),
        recommendations=(),
        survivable_scenarios=(ForecastScenarioType.STABLE_CONTINUATION,),
        critical_scenarios=critical,
        events=(),
        summary="forecast",
    )


def _timeline_result(decision=TimelineDecision.SELECT_STABLE_TIMELINE, survivability=78, risks=(), outcome=TimelineOutcome.STABLE):
    return SimpleNamespace(
        decision=decision,
        overall_survivability_score=survivability,
        risks=risks,
        timeline_states=(SimpleNamespace(outcome=outcome),),
        summary="timeline",
    )


def _plan(decision_value="PROCEED_WITH_PLAN", stability=75):
    return SimpleNamespace(decision=SimpleNamespace(value=decision_value), projection=SimpleNamespace(projected_stability_score=stability))


def _strategy(mode=StrategyEvolutionMode.STABLE_PRESERVATION, decision=StrategyEvolutionDecision.KEEP_CURRENT_STRATEGY, fitness=76, evidence=75):
    return SimpleNamespace(mode=mode, decision=decision, fitness_score=fitness, fitness_breakdown=SimpleNamespace(evidence_score=evidence))


def _orchestrator(decision=OrchestratorDecision.CONTINUE_COORDINATED_OPERATION, mode=OrchestratorMode.COORDINATED_OPERATION, confidence=75, risks=()):
    return SimpleNamespace(
        decision=decision,
        confidence_score=confidence,
        system_state=SimpleNamespace(mode=mode, risks=risks),
    )


def _coordination(confidence=75, risks=()):
    return SimpleNamespace(state=SimpleNamespace(confidence_score=confidence, risks=risks))


def _health(score=75):
    return SimpleNamespace(orchestration_confidence=score)


def _strategic_timeline(score=75, degraded=False, drifts=()):
    return SimpleNamespace(strategic_health_score=score, degradation_detected=degraded, drift_signals=drifts)


def _integrity(status=SystemIntegrityStatus.HEALTHY, score=75):
    return SimpleNamespace(status=status, integrity_score=score)


def _intent(mode=IntentAlignmentMode.FULLY_ALIGNED):
    return SimpleNamespace(mode=mode)


def _arbitration(decision=ArbitrationDecision.CONTINUE_OPERATION):
    return SimpleNamespace(decision=decision)


def _cognitive(score=75, load=CognitiveLoadLevel.LOW):
    return SimpleNamespace(global_score=score, load_level=load)


def _reward(label=RewardLabel.GOOD_DECISION):
    return SimpleNamespace(reward_label=label)


def test_builds_world_model_graph_with_required_layers_and_links() -> None:
    graph = build_world_model_graph(
        multi_timeline=_timeline_result(),
        scenario_forecast=_forecast(),
        long_horizon_plan=_plan(),
        strategy_evolution=_strategy(),
        global_orchestrator=_orchestrator(),
    )

    assert WorldModelLayer.PERCEPTION in graph.layers
    assert WorldModelLayer.ORCHESTRATION in graph.layers
    assert any(link.source == WorldModelLayer.PLANNING and link.target == WorldModelLayer.ACTION for link in graph.links)


def test_evaluates_world_model_state_for_all_layers() -> None:
    states = evaluate_world_model_state(
        multi_timeline=_timeline_result(),
        scenario_forecast=_forecast(),
        cognitive_adaptation=_cognitive(),
        system_integrity=_integrity(),
    )

    assert len(states) == 10
    assert {state.layer for state in states} == set(WorldModelLayer)
    assert all(0 <= state.coherence_score <= 100 for state in states)


def test_detects_forecast_reality_gap_and_planning_action_mismatch() -> None:
    risks = detect_world_model_risks(
        scenario_forecast=_forecast(ForecastDecision.CONTINUE_CURRENT_PATH, 82),
        multi_timeline=_timeline_result(TimelineDecision.ENTER_TIMELINE_SAFE_MODE, 35, (TimelineRisk.COLLAPSE_RISK,), TimelineOutcome.EMERGENCY_STOP),
        long_horizon_plan=_plan("PROCEED_WITH_PLAN", 80),
        system_integrity=_integrity(SystemIntegrityStatus.HEALTHY, 75),
    )

    assert WorldModelRisk.FORECAST_REALITY_GAP in risks
    assert WorldModelRisk.PLANNING_ACTION_MISMATCH in risks


def test_detects_state_drift_and_dynamics_instability() -> None:
    risks = detect_world_model_risks(
        strategic_timeline_analysis=_strategic_timeline(35, True, (StrategicDriftSignal.STRATEGIC_DEGRADATION,)),
        multi_timeline=_timeline_result(TimelineDecision.REBUILD_TIMELINE_SET, 30),
        scenario_forecast=_forecast(ForecastDecision.AVOID_HIGH_RISK_SCENARIO, 35, 40),
    )

    assert WorldModelRisk.STATE_DRIFT in risks
    assert WorldModelRisk.DYNAMICS_INSTABILITY in risks


def test_detects_orchestration_desync_and_safety_failure() -> None:
    risks = detect_world_model_risks(
        global_orchestrator=_orchestrator(OrchestratorDecision.CONTINUE_COORDINATED_OPERATION, confidence=80),
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 25),
        multi_timeline=_timeline_result(TimelineDecision.ENTER_TIMELINE_SAFE_MODE, 25, (TimelineRisk.COLLAPSE_RISK,)),
        strategic_arbitration=_arbitration(ArbitrationDecision.EMERGENCY_LOCKDOWN),
    )

    assert WorldModelRisk.ORCHESTRATION_DESYNC in risks
    assert WorldModelRisk.SAFETY_MODEL_FAILURE in risks


def test_simulates_causal_impacts_with_prediction_risks() -> None:
    states = evaluate_world_model_state(
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 20),
        global_orchestrator=_orchestrator(confidence=80),
        multi_timeline=_timeline_result(TimelineDecision.ENTER_TIMELINE_SAFE_MODE, 25),
    )
    predictions = simulate_causal_impacts(states=states)

    assert predictions
    assert all(0 <= prediction.impact_score <= 100 for prediction in predictions)


def test_decision_requires_more_observation_when_evidence_is_sparse() -> None:
    decision = decide_world_model_action()

    assert decision == WorldModelDecision.REQUIRE_MORE_OBSERVATION


def test_decision_freezes_recursive_updates_on_feedback_loop() -> None:
    decision = decide_world_model_action(
        strategy_evolution=_strategy(StrategyEvolutionMode.REBUILD_STRATEGY, StrategyEvolutionDecision.REBUILD_STRATEGY_FAMILY),
        multi_timeline=_timeline_result(TimelineDecision.REBUILD_TIMELINE_SET, 30),
        scenario_forecast=_forecast(ForecastDecision.ENTER_FORECAST_SAFE_MODE, 30),
    )

    assert decision == WorldModelDecision.FREEZE_RECURSIVE_UPDATES


def test_recommendations_cover_forecast_safety_and_orchestration_risks() -> None:
    recommendations = generate_world_model_recommendations(
        risks=(
            WorldModelRisk.FORECAST_REALITY_GAP,
            WorldModelRisk.SAFETY_MODEL_FAILURE,
            WorldModelRisk.ORCHESTRATION_DESYNC,
            WorldModelRisk.RECURSIVE_FEEDBACK_LOOP,
        )
    )

    assert WorldModelRecommendation.CHECK_FORECAST_ALIGNMENT in recommendations
    assert WorldModelRecommendation.PROTECT_SAFETY_MODEL in recommendations
    assert WorldModelRecommendation.SYNC_ORCHESTRATION_STATE in recommendations
    assert WorldModelRecommendation.REDUCE_RECURSIVE_DEPTH in recommendations


def test_render_recursive_world_model_markdown_contains_required_sections() -> None:
    result = evaluate_recursive_world_model(
        multi_timeline=_timeline_result(),
        scenario_forecast=_forecast(),
        long_horizon_plan=_plan(),
        strategy_evolution=_strategy(),
        global_orchestrator=_orchestrator(),
        cognitive_adaptation=_cognitive(),
    )
    markdown = render_recursive_world_model_markdown(result)

    assert "Recursive World Model State" in markdown
    assert "World Model Layers" in markdown
    assert "Causal Graph" in markdown
    assert "Predicted Impacts" in markdown
    assert "Coherence Score" in markdown
    assert "Risks" in markdown
    assert "Decision" in markdown
    assert "Recommendations" in markdown
    assert "AGIcore World Model Outlook" in markdown
