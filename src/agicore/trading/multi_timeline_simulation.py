"""Offline Autonomous Multi-Timeline Simulation Engine for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime

from .behavioral_stability_models import BehavioralPressureLevel
from .cognitive_adaptation_models import CognitiveLoadLevel
from .intent_alignment_models import IntentAlignmentMode
from .long_horizon_planning_models import PlanningDecision, PlanningRisk
from .mission_continuity_models import MissionContinuityMode
from .multi_timeline_simulation_models import (
    MultiTimelineSimulationInput,
    MultiTimelineSimulationResult,
    TimelineComparisonGraph,
    TimelineDecision,
    TimelineDivergence,
    TimelineEvent,
    TimelineOutcome,
    TimelineRecommendation,
    TimelineRisk,
    TimelineScenario,
    TimelineState,
    TimelineSurvivabilityScore,
)
from .operational_awareness_models import OperationalHealthStatus
from .recovery_resilience_models import RecoveryMode
from .reward_models import RewardLabel
from .scenario_forecast_models import ForecastDecision, ForecastScenarioType
from .strategic_arbitration_models import ArbitrationDecision, ArbitrationMode
from .strategic_memory_models import StrategicDriftSignal
from .strategy_evolution_models import StrategyEvolutionDecision, StrategyEvolutionMode
from .system_integrity_models import SystemIntegrityStatus


def build_timeline_scenarios(
    simulation_input: MultiTimelineSimulationInput | None = None,
    **kwargs,
) -> tuple[TimelineScenario, ...]:
    """Build plausible parallel timelines from current offline evidence."""
    data = _input(simulation_input, **kwargs)
    if data.requested_timelines:
        return tuple(dict.fromkeys(data.requested_timelines))

    scenarios = [TimelineScenario.BASELINE_TIMELINE]
    if _healthy(data):
        scenarios.append(TimelineScenario.GROWTH_TIMELINE)
    if _safe_mode_needed(data) or _danger_count(data) >= 2:
        scenarios.append(TimelineScenario.SAFE_TIMELINE)
    if _recovery_context(data):
        scenarios.append(TimelineScenario.RECOVERY_TIMELINE)
    if _strategic_drift(data):
        scenarios.append(TimelineScenario.DEGRADED_TIMELINE)
    if _behavior_risk(data):
        scenarios.append(TimelineScenario.BEHAVIORAL_RISK_TIMELINE)
    if _system_risk(data):
        scenarios.append(TimelineScenario.SYSTEM_RISK_TIMELINE)
    if _volatility_risk(data):
        scenarios.append(TimelineScenario.HIGH_VOLATILITY_TIMELINE)
    if _critical_count(data) >= 2:
        scenarios.append(TimelineScenario.EMERGENCY_TIMELINE)
    if _evidence_count(data) < 2:
        scenarios.append(TimelineScenario.UNKNOWN_TIMELINE)
    return tuple(dict.fromkeys(scenarios))


def simulate_timeline_states(
    simulation_input: MultiTimelineSimulationInput | None = None,
    *,
    scenarios: tuple[TimelineScenario, ...] | None = None,
    **kwargs,
) -> tuple[TimelineState, ...]:
    """Simulate deterministic future state for each timeline."""
    data = _input(simulation_input, **kwargs)
    resolved_scenarios = scenarios or build_timeline_scenarios(data)
    return tuple(_simulate_one(data, scenario) for scenario in resolved_scenarios)


def compare_timeline_outcomes(
    simulation_input: MultiTimelineSimulationInput | None = None,
    *,
    states: tuple[TimelineState, ...] | None = None,
    **kwargs,
) -> tuple[TimelineRisk, ...]:
    """Compare outcomes and emit cross-timeline risks."""
    data = _input(simulation_input, **kwargs)
    resolved_states = states or simulate_timeline_states(data)
    divergences = compute_timeline_divergence(data, states=resolved_states)
    survivability = compute_timeline_survivability(data, states=resolved_states)
    risks: list[TimelineRisk] = []

    if any(divergence.divergence_score >= 55 for divergence in divergences):
        risks.append(TimelineRisk.DIVERGENCE_RISK)
    if any(state.outcome in {TimelineOutcome.COLLAPSING, TimelineOutcome.EMERGENCY_STOP} for state in resolved_states):
        risks.append(TimelineRisk.COLLAPSE_RISK)
    if any(state.scenario == TimelineScenario.DEGRADED_TIMELINE for state in resolved_states) or _strategic_drift(data):
        risks.append(TimelineRisk.STRATEGIC_DRIFT_RISK)
    if any(state.scenario == TimelineScenario.BEHAVIORAL_RISK_TIMELINE for state in resolved_states):
        risks.append(TimelineRisk.BEHAVIORAL_REGRESSION_RISK)
    if any(state.scenario == TimelineScenario.SYSTEM_RISK_TIMELINE for state in resolved_states):
        risks.append(TimelineRisk.SYSTEM_FAILURE_RISK)
    if any(state.scenario == TimelineScenario.RECOVERY_TIMELINE and state.recovery_score < 50 for state in resolved_states):
        risks.append(TimelineRisk.RECOVERY_FAILURE_RISK)
    if any(state.outcome == TimelineOutcome.SAFE_MODE for state in resolved_states):
        risks.append(TimelineRisk.SAFE_MODE_DEPENDENCY)
    if any(score.survivability_score < 45 for score in survivability):
        risks.append(TimelineRisk.LOW_SURVIVABILITY)
    if TimelineScenario.UNKNOWN_TIMELINE in {state.scenario for state in resolved_states} or _evidence_count(data) < 2:
        risks.append(TimelineRisk.TIMELINE_UNCERTAINTY)
    if _mission_incompatible(data) or any(state.safety_score < 35 for state in resolved_states):
        risks.append(TimelineRisk.INCOMPATIBLE_FUTURE_PATH)
    return tuple(dict.fromkeys(risks))


def compute_timeline_divergence(
    simulation_input: MultiTimelineSimulationInput | None = None,
    *,
    states: tuple[TimelineState, ...] | None = None,
    **kwargs,
) -> tuple[TimelineDivergence, ...]:
    """Compute divergence between baseline and alternative timelines."""
    data = _input(simulation_input, **kwargs)
    resolved_states = states or simulate_timeline_states(data)
    baseline = next((state for state in resolved_states if state.scenario == TimelineScenario.BASELINE_TIMELINE), resolved_states[0] if resolved_states else None)
    if baseline is None:
        return ()

    divergences: list[TimelineDivergence] = []
    for state in resolved_states:
        if state.scenario == baseline.scenario:
            continue
        score = _clamp(
            abs(state.stability_score - baseline.stability_score) * 0.35
            + abs(state.recovery_score - baseline.recovery_score) * 0.2
            + abs(state.safety_score - baseline.safety_score) * 0.25
            + abs(state.system_health_score - baseline.system_health_score) * 0.2
        )
        drivers = _divergence_drivers(baseline, state)
        divergences.append(TimelineDivergence(baseline.scenario, state.scenario, score, _severity(score), drivers))
    return tuple(divergences)


def compute_timeline_survivability(
    simulation_input: MultiTimelineSimulationInput | None = None,
    *,
    states: tuple[TimelineState, ...] | None = None,
    **kwargs,
) -> tuple[TimelineSurvivabilityScore, ...]:
    """Compute survivability score per timeline."""
    data = _input(simulation_input, **kwargs)
    resolved_states = states or simulate_timeline_states(data)
    confidence = _confidence(data)
    mission = _mission_score(data)
    scores: list[TimelineSurvivabilityScore] = []
    for state in resolved_states:
        survivability = _clamp(
            state.stability_score * 0.25
            + state.safety_score * 0.25
            + state.recovery_score * 0.15
            + state.system_health_score * 0.15
            + mission * 0.1
            + confidence * 0.1
        )
        if state.outcome in {TimelineOutcome.COLLAPSING, TimelineOutcome.EMERGENCY_STOP}:
            survivability = _clamp(survivability - 25)
        scores.append(TimelineSurvivabilityScore(state.scenario, survivability, state.stability_score, state.safety_score, state.recovery_score, mission, confidence))
    return tuple(scores)


def build_timeline_comparison_graph(
    simulation_input: MultiTimelineSimulationInput | None = None,
    *,
    states: tuple[TimelineState, ...] | None = None,
    survivability_scores: tuple[TimelineSurvivabilityScore, ...] | None = None,
    **kwargs,
) -> TimelineComparisonGraph:
    """Build an explainable comparison graph across timelines."""
    data = _input(simulation_input, **kwargs)
    resolved_states = states or simulate_timeline_states(data)
    resolved_scores = survivability_scores or compute_timeline_survivability(data, states=resolved_states)
    score_by_scenario = {score.scenario: score.survivability_score for score in resolved_scores}
    nodes = tuple(state.scenario.value for state in resolved_states)
    edges = tuple(("BASELINE_TIMELINE", state.scenario.value, state.outcome.value) for state in resolved_states if state.scenario != TimelineScenario.BASELINE_TIMELINE)
    stable = tuple(state.scenario for state in resolved_states if state.outcome in {TimelineOutcome.STABLE, TimelineOutcome.IMPROVING, TimelineOutcome.RECOVERING} and score_by_scenario.get(state.scenario, 0) >= 60)
    unstable = tuple(state.scenario for state in resolved_states if state.outcome in {TimelineOutcome.UNSTABLE, TimelineOutcome.COLLAPSING, TimelineOutcome.EMERGENCY_STOP} or score_by_scenario.get(state.scenario, 100) < 45)
    recommended = max(resolved_scores, key=lambda score: score.survivability_score).scenario if resolved_scores else None
    return TimelineComparisonGraph(nodes, edges, stable, unstable, recommended)


def decide_timeline_path(
    simulation_input: MultiTimelineSimulationInput | None = None,
    *,
    states: tuple[TimelineState, ...] | None = None,
    risks: tuple[TimelineRisk, ...] | None = None,
    survivability_scores: tuple[TimelineSurvivabilityScore, ...] | None = None,
    graph: TimelineComparisonGraph | None = None,
    **kwargs,
) -> TimelineDecision:
    """Select the safest explainable path from simulated timelines."""
    data = _input(simulation_input, **kwargs)
    resolved_states = states or simulate_timeline_states(data)
    resolved_scores = survivability_scores or compute_timeline_survivability(data, states=resolved_states)
    resolved_risks = risks or compare_timeline_outcomes(data, states=resolved_states)
    resolved_graph = graph or build_timeline_comparison_graph(data, states=resolved_states, survivability_scores=resolved_scores)
    best = max(resolved_scores, key=lambda score: score.survivability_score, default=None)

    if _evidence_count(data) < 2 or TimelineRisk.TIMELINE_UNCERTAINTY in resolved_risks:
        return TimelineDecision.REQUIRE_MORE_SIMULATION
    if _critical_count(data) >= 3 or any(state.outcome == TimelineOutcome.EMERGENCY_STOP for state in resolved_states):
        return TimelineDecision.ENTER_TIMELINE_SAFE_MODE
    if TimelineRisk.INCOMPATIBLE_FUTURE_PATH in resolved_risks and TimelineRisk.COLLAPSE_RISK in resolved_risks:
        return TimelineDecision.REQUIRE_HUMAN_REVIEW
    if best is not None and best.survivability_score < 40:
        return TimelineDecision.REBUILD_TIMELINE_SET
    if best is not None and best.scenario == TimelineScenario.RECOVERY_TIMELINE and best.survivability_score >= 55:
        return TimelineDecision.SELECT_RECOVERY_TIMELINE
    if best is not None and best.scenario == TimelineScenario.SAFE_TIMELINE:
        return TimelineDecision.SELECT_SAFE_TIMELINE
    if resolved_graph.unstable_paths:
        return TimelineDecision.AVOID_UNSTABLE_TIMELINE
    return TimelineDecision.SELECT_STABLE_TIMELINE


def generate_timeline_recommendations(
    simulation_input: MultiTimelineSimulationInput | None = None,
    *,
    decision: TimelineDecision | None = None,
    risks: tuple[TimelineRisk, ...] | None = None,
    states: tuple[TimelineState, ...] | None = None,
    **kwargs,
) -> tuple[TimelineRecommendation, ...]:
    """Generate recommendations from timeline decision and risks."""
    data = _input(simulation_input, **kwargs)
    resolved_states = states or simulate_timeline_states(data)
    resolved_risks = risks or compare_timeline_outcomes(data, states=resolved_states)
    resolved_decision = decision or decide_timeline_path(data, states=resolved_states, risks=resolved_risks)
    recommendations: list[TimelineRecommendation] = [TimelineRecommendation.PRESERVE_TIMELINE_MEMORY]

    if resolved_decision == TimelineDecision.SELECT_STABLE_TIMELINE:
        recommendations.append(TimelineRecommendation.FOLLOW_BASELINE_IF_STABLE)
    if resolved_decision in {TimelineDecision.SELECT_SAFE_TIMELINE, TimelineDecision.ENTER_TIMELINE_SAFE_MODE} or TimelineRisk.SAFE_MODE_DEPENDENCY in resolved_risks:
        recommendations.append(TimelineRecommendation.PRIORITIZE_SAFE_TIMELINE)
    if resolved_decision == TimelineDecision.SELECT_RECOVERY_TIMELINE or TimelineRisk.RECOVERY_FAILURE_RISK in resolved_risks:
        recommendations.append(TimelineRecommendation.PRIORITIZE_RECOVERY_PATH)
    if TimelineRisk.DIVERGENCE_RISK in resolved_risks:
        recommendations.append(TimelineRecommendation.AVOID_HIGH_DIVERGENCE_PATH)
    if TimelineRisk.TIMELINE_UNCERTAINTY in resolved_risks or resolved_decision == TimelineDecision.REQUIRE_MORE_SIMULATION:
        recommendations.append(TimelineRecommendation.EXTEND_SIMULATION_DEPTH)
    if TimelineRisk.STRATEGIC_DRIFT_RISK in resolved_risks:
        recommendations.append(TimelineRecommendation.REDUCE_STRATEGIC_RISK)
    if TimelineRisk.BEHAVIORAL_REGRESSION_RISK in resolved_risks:
        recommendations.append(TimelineRecommendation.STABILIZE_BEHAVIOR_BEFORE_EXECUTION)
    if TimelineRisk.SYSTEM_FAILURE_RISK in resolved_risks or TimelineRisk.COLLAPSE_RISK in resolved_risks:
        recommendations.append(TimelineRecommendation.CHECK_SYSTEM_INTEGRITY)
    if data.scenario_forecast is not None and data.scenario_forecast.decision in {ForecastDecision.REQUIRE_OBSERVATION_WINDOW, ForecastDecision.REBUILD_FORECAST_MODEL}:
        recommendations.append(TimelineRecommendation.UPDATE_FORECAST_MODEL)
    return tuple(dict.fromkeys(recommendations))


def render_multi_timeline_simulation_markdown(result: MultiTimelineSimulationResult) -> str:
    """Render multi-timeline simulation result as Markdown."""
    lines = [
        "# Autonomous Multi-Timeline Simulation Engine",
        "",
        "## Multi-Timeline Simulation State",
        "",
        f"- Decision: {result.decision.value}",
        f"- Selected timeline: {result.selected_timeline.value if result.selected_timeline else 'None'}",
        f"- Overall survivability: {result.overall_survivability_score}/100",
        "",
        "## Timeline Scenarios",
        "",
        *_bullet_lines(tuple(state.scenario.value for state in result.timeline_states)),
        "",
        "## Timeline Outcomes",
        "",
        *_bullet_lines(tuple(f"{state.scenario.value}: {state.outcome.value}" for state in result.timeline_states)),
        "",
        "## Divergence Analysis",
        "",
        *_bullet_lines(tuple(f"{d.alternative.value}: {d.divergence_score}/100 {d.severity}" for d in result.divergences)),
        "",
        "## Survivability Scores",
        "",
        *_bullet_lines(tuple(f"{score.scenario.value}: {score.survivability_score}/100" for score in result.survivability_scores)),
        "",
        "## Comparison Graph",
        "",
        *_bullet_lines(result.comparison_graph.nodes),
        *_bullet_lines(tuple(f"{source} -> {target}: {label}" for source, target, label in result.comparison_graph.edges)),
        "",
        "## Decision",
        "",
        f"- {result.decision.value}",
        "",
        "## Recommendations",
        "",
        *_bullet_lines(tuple(recommendation.value for recommendation in result.recommendations)),
        "",
        "## AGIcore Timeline Outlook",
        "",
        result.summary,
    ]
    return "\n".join(lines)


def run_multi_timeline_simulation(
    simulation_input: MultiTimelineSimulationInput | None = None,
    **kwargs,
) -> MultiTimelineSimulationResult:
    """Run the full offline multi-timeline simulation pipeline."""
    data = _input(simulation_input, **kwargs)
    scenarios = build_timeline_scenarios(data)
    states = simulate_timeline_states(data, scenarios=scenarios)
    divergences = compute_timeline_divergence(data, states=states)
    survivability = compute_timeline_survivability(data, states=states)
    graph = build_timeline_comparison_graph(data, states=states, survivability_scores=survivability)
    risks = compare_timeline_outcomes(data, states=states)
    decision = decide_timeline_path(data, states=states, risks=risks, survivability_scores=survivability, graph=graph)
    recommendations = generate_timeline_recommendations(data, decision=decision, risks=risks, states=states)
    selected = graph.recommended_path
    overall = _clamp(sum(score.survivability_score for score in survivability) / max(1, len(survivability)))
    event = TimelineEvent(decision, f"multi-timeline decision={decision.value}", datetime.now(UTC))
    return MultiTimelineSimulationResult(
        decision,
        selected,
        states,
        divergences,
        survivability,
        graph,
        risks,
        recommendations,
        overall,
        (event,),
        f"{decision.value} with {len(states)} simulated timelines and survivability {overall}/100",
    )


def _simulate_one(data: MultiTimelineSimulationInput, scenario: TimelineScenario) -> TimelineState:
    base_stability = _stability(data)
    recovery = _recovery_score(data)
    growth = _growth_score(data)
    safety = _safety_score(data)
    health = _system_health(data)
    behavior = _behavior_score(data)
    notes: list[str] = []

    if scenario == TimelineScenario.SAFE_TIMELINE:
        safety += 18
        growth -= 18
        notes.append("risk reduced")
    elif scenario == TimelineScenario.RECOVERY_TIMELINE:
        recovery += 20
        growth -= 8
        notes.append("recovery prioritized")
    elif scenario == TimelineScenario.GROWTH_TIMELINE:
        growth += 20
        safety -= 10
        notes.append("growth bias")
    elif scenario == TimelineScenario.DEGRADED_TIMELINE:
        base_stability -= 25
        growth -= 15
        notes.append("strategic drift")
    elif scenario == TimelineScenario.HIGH_VOLATILITY_TIMELINE:
        safety -= 20
        base_stability -= 10
        notes.append("volatility spike")
    elif scenario == TimelineScenario.BEHAVIORAL_RISK_TIMELINE:
        behavior -= 30
        safety -= 10
        notes.append("behavior regression")
    elif scenario == TimelineScenario.SYSTEM_RISK_TIMELINE:
        health -= 30
        safety -= 15
        notes.append("system failure path")
    elif scenario == TimelineScenario.EMERGENCY_TIMELINE:
        base_stability -= 45
        health -= 40
        safety -= 35
        notes.append("emergency stop path")
    elif scenario == TimelineScenario.UNKNOWN_TIMELINE:
        base_stability -= 15
        recovery -= 10
        growth -= 10
        safety -= 10
        notes.append("low evidence")

    base_stability = _clamp(base_stability)
    recovery = _clamp(recovery)
    growth = _clamp(growth)
    safety = _clamp(safety)
    health = _clamp(health)
    behavior = _clamp(behavior)
    outcome = _outcome_for(scenario, base_stability, recovery, safety, health, behavior)
    return TimelineState(scenario, base_stability, recovery, growth, safety, health, behavior, outcome, tuple(notes))


def _outcome_for(
    scenario: TimelineScenario,
    stability: int,
    recovery: int,
    safety: int,
    health: int,
    behavior: int,
) -> TimelineOutcome:
    if scenario == TimelineScenario.EMERGENCY_TIMELINE or min(stability, safety, health) < 25:
        return TimelineOutcome.EMERGENCY_STOP
    if scenario == TimelineScenario.SAFE_TIMELINE:
        return TimelineOutcome.SAFE_MODE
    if min(stability, safety, health, behavior) < 35:
        return TimelineOutcome.COLLAPSING
    if scenario == TimelineScenario.RECOVERY_TIMELINE and recovery >= 60:
        return TimelineOutcome.RECOVERING
    if stability >= 75 and safety >= 70:
        return TimelineOutcome.IMPROVING
    if stability >= 60 and safety >= 55:
        return TimelineOutcome.STABLE
    if stability >= 45:
        return TimelineOutcome.DEGRADED
    return TimelineOutcome.UNSTABLE


def _input(simulation_input: MultiTimelineSimulationInput | None = None, **kwargs) -> MultiTimelineSimulationInput:
    if simulation_input is not None and kwargs:
        raise ValueError("Pass either MultiTimelineSimulationInput or keyword inputs, not both")
    if simulation_input is not None:
        return simulation_input
    return MultiTimelineSimulationInput(**kwargs)


def _stability(data: MultiTimelineSimulationInput) -> int:
    values: list[int] = []
    if data.scenario_forecast is not None:
        values.append(data.scenario_forecast.forecast_stability_score)
    if data.long_horizon_plan is not None:
        values.append(data.long_horizon_plan.projection.projected_stability_score)
    if data.strategy_evolution is not None:
        values.append(data.strategy_evolution.fitness_score)
    if data.strategic_timeline_analysis is not None:
        values.append(data.strategic_timeline_analysis.strategic_health_score)
    return _avg(values, 68)


def _recovery_score(data: MultiTimelineSimulationInput) -> int:
    values: list[int] = []
    if data.long_horizon_plan is not None:
        values.append(data.long_horizon_plan.projection.projected_recovery_score)
    if data.recovery_resilience is not None:
        values.append(data.recovery_resilience.resilience_score)
    return _avg(values, 60)


def _growth_score(data: MultiTimelineSimulationInput) -> int:
    values: list[int] = []
    if data.long_horizon_plan is not None:
        values.append(100 - data.long_horizon_plan.projection.projected_drawdown_risk_score)
    if data.reward_evaluation is not None:
        values.append(data.reward_evaluation.normalized_reward)
    return _avg(values, 62)


def _safety_score(data: MultiTimelineSimulationInput) -> int:
    score = 75
    if data.scenario_forecast is not None and data.scenario_forecast.decision in {ForecastDecision.ENTER_FORECAST_SAFE_MODE, ForecastDecision.AVOID_HIGH_RISK_SCENARIO}:
        score -= 25
    if data.strategy_evolution is not None and data.strategy_evolution.decision in {StrategyEvolutionDecision.FREEZE_STRATEGY_EVOLUTION, StrategyEvolutionDecision.REQUIRE_HUMAN_REVIEW}:
        score -= 15
    if data.strategic_arbitration is not None and data.strategic_arbitration.decision in {ArbitrationDecision.EMERGENCY_LOCKDOWN, ArbitrationDecision.STOP_EXECUTION}:
        score -= 25
    if _safe_mode_needed(data):
        score += 10
    return _clamp(score)


def _system_health(data: MultiTimelineSimulationInput) -> int:
    if data.health_snapshot is not None:
        return data.health_snapshot.orchestration_confidence
    if data.global_orchestrator is not None:
        return data.global_orchestrator.confidence_score
    if data.system_integrity is not None:
        return data.system_integrity.integrity_score
    if data.operational_awareness is not None:
        return data.operational_awareness.operational_confidence_score
    return 70


def _behavior_score(data: MultiTimelineSimulationInput) -> int:
    if data.behavioral_stability is not None:
        return data.behavioral_stability.stability_score
    if data.long_horizon_plan is not None:
        return data.long_horizon_plan.projection.projected_behavior_score
    return 70


def _mission_score(data: MultiTimelineSimulationInput) -> int:
    score = 75
    if data.mission_continuity is not None and data.mission_continuity.mode != MissionContinuityMode.FULL_OPERATION:
        score -= 25
        score = min(score, data.mission_continuity.continuity_score)
    if data.intent_alignment is not None and data.intent_alignment.mode not in {IntentAlignmentMode.FULLY_ALIGNED, IntentAlignmentMode.STABLE_ALIGNMENT}:
        score -= 25
    return _clamp(score)


def _confidence(data: MultiTimelineSimulationInput) -> int:
    values: list[int] = []
    if data.scenario_forecast is not None:
        values.append(data.scenario_forecast.stability_breakdown.confidence_score)
    if data.long_horizon_plan is not None:
        values.append(data.long_horizon_plan.projection_confidence)
    if data.strategy_evolution is not None:
        values.append(data.strategy_evolution.fitness_breakdown.evidence_score)
    if data.operational_awareness is not None:
        values.append(data.operational_awareness.operational_confidence_score)
    return _avg(values, 45 if _evidence_count(data) < 2 else 65)


def _healthy(data: MultiTimelineSimulationInput) -> bool:
    return _stability(data) >= 70 and _system_health(data) >= 65 and _behavior_score(data) >= 65 and _danger_count(data) == 0


def _safe_mode_needed(data: MultiTimelineSimulationInput) -> bool:
    return (
        data.scenario_forecast is not None and data.scenario_forecast.decision in {ForecastDecision.PRIORITIZE_SAFE_SCENARIO, ForecastDecision.ENTER_FORECAST_SAFE_MODE}
    ) or (
        data.long_horizon_plan is not None and data.long_horizon_plan.decision == PlanningDecision.ENTER_LONG_HORIZON_SAFE_MODE
    ) or (
        data.strategic_arbitration is not None and data.strategic_arbitration.mode == ArbitrationMode.EMERGENCY_LOCKDOWN
    )


def _recovery_context(data: MultiTimelineSimulationInput) -> bool:
    return (
        data.long_horizon_plan is not None and data.long_horizon_plan.decision == PlanningDecision.PRIORITIZE_RECOVERY
    ) or (
        data.recovery_resilience is not None and data.recovery_resilience.mode not in {RecoveryMode.NORMAL, RecoveryMode.REBUILD_CONFIDENCE}
    ) or (
        data.scenario_forecast is not None and ForecastScenarioType.RECOVERY_SUCCESS in data.scenario_forecast.survivable_scenarios
    )


def _strategic_drift(data: MultiTimelineSimulationInput) -> bool:
    return (
        data.long_horizon_plan is not None and PlanningRisk.STRATEGIC_DRIFT_RISK in data.long_horizon_plan.risks
    ) or (
        data.strategic_timeline_analysis is not None and (data.strategic_timeline_analysis.degradation_detected or StrategicDriftSignal.STRATEGIC_DEGRADATION in data.strategic_timeline_analysis.drift_signals)
    ) or (
        data.strategy_evolution is not None and data.strategy_evolution.mode in {StrategyEvolutionMode.SAFE_ROLLBACK, StrategyEvolutionMode.REBUILD_STRATEGY}
    )


def _behavior_risk(data: MultiTimelineSimulationInput) -> bool:
    return data.behavioral_stability is not None and (
        data.behavioral_stability.stability_score < 50 or data.behavioral_stability.pressure_level in {BehavioralPressureLevel.HIGH, BehavioralPressureLevel.EXTREME}
    )


def _system_risk(data: MultiTimelineSimulationInput) -> bool:
    return (
        data.system_integrity is not None and data.system_integrity.status != SystemIntegrityStatus.HEALTHY
    ) or (
        data.operational_awareness is not None and data.operational_awareness.health_status in {OperationalHealthStatus.DEGRADED, OperationalHealthStatus.CRITICAL, OperationalHealthStatus.COLLAPSING}
    )


def _volatility_risk(data: MultiTimelineSimulationInput) -> bool:
    return data.scenario_forecast is not None and ForecastScenarioType.SYSTEM_DEGRADATION in data.scenario_forecast.critical_scenarios


def _critical_count(data: MultiTimelineSimulationInput) -> int:
    count = 0
    if data.system_integrity is not None and data.system_integrity.status in {SystemIntegrityStatus.COMPROMISED, SystemIntegrityStatus.ROLLBACK_RECOMMENDED}:
        count += 1
    if data.operational_awareness is not None and data.operational_awareness.health_status in {OperationalHealthStatus.CRITICAL, OperationalHealthStatus.COLLAPSING}:
        count += 1
    if data.cognitive_adaptation is not None and data.cognitive_adaptation.load_level == CognitiveLoadLevel.OVERLOADED:
        count += 1
    if data.reward_evaluation is not None and data.reward_evaluation.reward_label == RewardLabel.DANGEROUS_DECISION:
        count += 1
    if data.strategic_arbitration is not None and data.strategic_arbitration.decision in {ArbitrationDecision.EMERGENCY_LOCKDOWN, ArbitrationDecision.STOP_EXECUTION}:
        count += 1
    return count


def _danger_count(data: MultiTimelineSimulationInput) -> int:
    count = _critical_count(data)
    count += 1 if _safe_mode_needed(data) else 0
    count += 1 if _strategic_drift(data) else 0
    count += 1 if _behavior_risk(data) else 0
    count += 1 if _system_risk(data) else 0
    return count


def _mission_incompatible(data: MultiTimelineSimulationInput) -> bool:
    return data.intent_alignment is not None and data.intent_alignment.mode in {IntentAlignmentMode.MISALIGNED, IntentAlignmentMode.CRITICAL_REALIGNMENT}


def _divergence_drivers(baseline: TimelineState, state: TimelineState) -> tuple[str, ...]:
    drivers: list[str] = []
    if abs(state.stability_score - baseline.stability_score) >= 20:
        drivers.append("stability")
    if abs(state.safety_score - baseline.safety_score) >= 20:
        drivers.append("safety")
    if abs(state.system_health_score - baseline.system_health_score) >= 20:
        drivers.append("system_health")
    if abs(state.behavior_score - baseline.behavior_score) >= 20:
        drivers.append("behavior")
    return tuple(drivers) or ("minor_variance",)


def _severity(score: int) -> str:
    if score >= 70:
        return "critical"
    if score >= 50:
        return "high"
    if score >= 30:
        return "moderate"
    return "low"


def _evidence_count(data: MultiTimelineSimulationInput) -> int:
    return sum(
        value is not None
        for value in (
            data.scenario_forecast,
            data.long_horizon_plan,
            data.strategy_evolution,
            data.global_orchestrator,
            data.coordination_result,
            data.health_snapshot,
            data.strategic_timeline_analysis,
            data.operational_awareness,
            data.mission_continuity,
            data.recovery_resilience,
            data.system_integrity,
            data.intent_alignment,
            data.strategic_arbitration,
            data.collective_consensus,
            data.behavioral_stability,
            data.cognitive_adaptation,
            data.reward_evaluation,
        )
    )


def _avg(values: list[int], default: int) -> int:
    if not values:
        return default
    return _clamp(sum(values) / len(values))


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _clamp(value: float, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(round(value))))


__all__ = [
    "build_timeline_comparison_graph",
    "build_timeline_scenarios",
    "compare_timeline_outcomes",
    "compute_timeline_divergence",
    "compute_timeline_survivability",
    "decide_timeline_path",
    "generate_timeline_recommendations",
    "render_multi_timeline_simulation_markdown",
    "run_multi_timeline_simulation",
    "simulate_timeline_states",
]
