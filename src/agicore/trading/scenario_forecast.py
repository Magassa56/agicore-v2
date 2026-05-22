"""Offline Autonomous Scenario Forecast Engine for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .behavioral_stability_models import BehavioralPressureLevel, BehavioralRecoveryState
from .cognitive_adaptation_models import CognitiveAdaptationMode, CognitiveLoadLevel
from .collective_consensus_models import ConsensusDecision, ConsensusMode
from .global_orchestrator_models import OrchestratorDecision, OrchestratorMode, OrchestratorRisk
from .intent_alignment_models import IntentAlignmentMode
from .long_horizon_planning_models import FutureScenarioType, PlanningDecision, PlanningRisk
from .mission_continuity_models import MissionContinuityMode
from .operational_awareness_models import OperationalHealthStatus
from .recovery_resilience_models import RecoveryMode
from .reward_models import RewardLabel
from .scenario_forecast_models import (
    ForecastBifurcation,
    ForecastDecision,
    ForecastEvent,
    ForecastProbabilityBand,
    ForecastRecommendation,
    ForecastRiskMap,
    ForecastScenario,
    ForecastScenarioType,
    ForecastStabilityScore,
    ScenarioForecastInput,
    ScenarioForecastResult,
)
from .strategic_arbitration_models import ArbitrationDecision, ArbitrationMode
from .strategic_memory_models import StrategicDriftSignal
from .system_integrity_models import SystemIntegrityStatus


def build_forecast_scenarios(
    forecast_input: ScenarioForecastInput | None = None,
    **kwargs,
) -> tuple[ForecastScenario, ...]:
    """Build forecast scenarios and estimate probability bands."""
    data = _input(forecast_input, **kwargs)
    candidates = _candidate_types(data)
    scenarios: list[ForecastScenario] = []
    for scenario_type in candidates:
        probability = estimate_scenario_probability(scenario_type, data)
        scenarios.append(
            ForecastScenario(
                scenario_type=scenario_type,
                probability_band=_band(probability),
                probability_score=probability,
                survivable=_survivable(scenario_type, data),
                stability_impact_score=_impact(scenario_type),
                description=_description(scenario_type),
                risk_notes=_risk_notes(scenario_type, data),
            )
        )
    return tuple(scenarios)


def estimate_scenario_probability(
    scenario_type: ForecastScenarioType,
    forecast_input: ScenarioForecastInput | None = None,
    **kwargs,
) -> int:
    """Estimate relative scenario probability using deterministic offline heuristics."""
    data = _input(forecast_input, **kwargs)
    base = 25
    health = _system_health(data)
    behavior = _behavior_score(data)
    strategy = _strategy_score(data)
    recovery = _recovery_score(data)

    if scenario_type == ForecastScenarioType.STABLE_CONTINUATION:
        base = 35 + (health + behavior + strategy) // 12
        if _safe_mode_needed(data):
            base -= 25
    elif scenario_type == ForecastScenarioType.CONTROLLED_GROWTH:
        base = 30 + (health + strategy) // 10
        if _danger_count(data) > 0:
            base -= 20
    elif scenario_type == ForecastScenarioType.RECOVERY_SUCCESS:
        base = 25 + recovery // 2
        if _drawdown_pressure(data):
            base += 10
    elif scenario_type == ForecastScenarioType.RECOVERY_FAILURE:
        base = 25 + max(0, 70 - recovery) // 2
        if _drawdown_pressure(data):
            base += 15
    elif scenario_type == ForecastScenarioType.STRATEGIC_DRIFT:
        base = 25 + max(0, 75 - strategy) // 2
        if data.strategic_timeline_analysis is not None and data.strategic_timeline_analysis.degradation_detected:
            base += 20
    elif scenario_type == ForecastScenarioType.BEHAVIORAL_REGRESSION:
        base = 25 + max(0, 75 - behavior) // 2
        if data.behavioral_stability is not None and data.behavioral_stability.pressure_level in {BehavioralPressureLevel.HIGH, BehavioralPressureLevel.EXTREME}:
            base += 20
    elif scenario_type == ForecastScenarioType.SYSTEM_DEGRADATION:
        base = 25 + max(0, 80 - health) // 2
        if data.system_integrity is not None and data.system_integrity.status != SystemIntegrityStatus.HEALTHY:
            base += 20
    elif scenario_type == ForecastScenarioType.SAFE_MODE_TRANSITION:
        base = 20 + _danger_count(data) * 15
        if _safe_mode_needed(data):
            base += 25
    elif scenario_type == ForecastScenarioType.MISSION_CONTINUITY_BREAK:
        base = 20 + _mission_risk(data) // 2
    elif scenario_type == ForecastScenarioType.EMERGENCY_LOCKDOWN_PATH:
        base = 10 + _critical_count(data) * 18
    return _clamp(base)


def detect_forecast_bifurcations(
    forecast_input: ScenarioForecastInput | None = None,
    *,
    scenarios: tuple[ForecastScenario, ...] | None = None,
    **kwargs,
) -> tuple[ForecastBifurcation, ...]:
    """Detect critical forks where opposing future paths are both plausible."""
    data = _input(forecast_input, **kwargs)
    resolved = scenarios or build_forecast_scenarios(data)
    by_type = {scenario.scenario_type: scenario for scenario in resolved}
    bifurcations: list[ForecastBifurcation] = []
    pairs = (
        (ForecastScenarioType.STABLE_CONTINUATION, ForecastScenarioType.SYSTEM_DEGRADATION, "stability_vs_degradation"),
        (ForecastScenarioType.RECOVERY_SUCCESS, ForecastScenarioType.RECOVERY_FAILURE, "recovery_fork"),
        (ForecastScenarioType.CONTROLLED_GROWTH, ForecastScenarioType.STRATEGIC_DRIFT, "growth_vs_drift"),
        (ForecastScenarioType.SAFE_MODE_TRANSITION, ForecastScenarioType.EMERGENCY_LOCKDOWN_PATH, "safe_mode_vs_lockdown"),
    )
    for positive, negative, trigger in pairs:
        if positive in by_type and negative in by_type:
            low = min(by_type[positive].probability_score, by_type[negative].probability_score)
            high = max(by_type[positive].probability_score, by_type[negative].probability_score)
            if low >= 45 and high - low <= 30:
                bifurcations.append(ForecastBifurcation(positive, negative, _clamp(low + (100 - abs(high - low)) // 3), trigger, "increase_observation_and_prioritize_safety"))
    return tuple(bifurcations)


def build_forecast_risk_map(
    forecast_input: ScenarioForecastInput | None = None,
    **kwargs,
) -> ForecastRiskMap:
    """Build future risk map by category."""
    data = _input(forecast_input, **kwargs)
    strategy = _risk_from_score(_strategy_score(data))
    behavior = _risk_from_score(_behavior_score(data))
    cognition = _risk_from_score(_cognitive_score(data))
    integrity = _risk_from_score(_system_health(data))
    continuity = _mission_risk(data)
    recovery = _risk_from_score(_recovery_score(data))
    mission = _mission_risk(data)
    if _safe_mode_needed(data):
        integrity += 15
        mission += 10
    if _drawdown_pressure(data):
        strategy += 10
        recovery += 15
    return ForecastRiskMap(_clamp(strategy), _clamp(behavior), _clamp(cognition), _clamp(integrity), _clamp(continuity), _clamp(recovery), _clamp(mission))


def compute_forecast_stability_score(
    forecast_input: ScenarioForecastInput | None = None,
    *,
    scenarios: tuple[ForecastScenario, ...] | None = None,
    risk_map: ForecastRiskMap | None = None,
    bifurcations: tuple[ForecastBifurcation, ...] | None = None,
    **kwargs,
) -> ForecastStabilityScore:
    """Compute forecast stability component scores."""
    data = _input(forecast_input, **kwargs)
    resolved_scenarios = scenarios or build_forecast_scenarios(data)
    resolved_risk_map = risk_map or build_forecast_risk_map(data)
    resolved_bifurcations = bifurcations or detect_forecast_bifurcations(data, scenarios=resolved_scenarios)
    dangerous = _dangerous_scenarios(resolved_scenarios)
    survivable_count = sum(1 for scenario in resolved_scenarios if scenario.survivable)
    scenario_balance = _clamp(85 - len(dangerous) * 8 - len(resolved_bifurcations) * 6)
    survivability = _clamp(100 * survivable_count / max(1, len(resolved_scenarios)))
    system_health = _clamp(100 - resolved_risk_map.integrity)
    behavior = _clamp(100 - resolved_risk_map.behavior)
    continuity = _clamp(100 - resolved_risk_map.continuity)
    confidence = _clamp((_available_confidence(data) + scenario_balance + survivability) / 3 - len(resolved_bifurcations) * 4)
    return ForecastStabilityScore(scenario_balance, survivability, system_health, behavior, continuity, confidence)


def decide_forecast_path(
    forecast_input: ScenarioForecastInput | None = None,
    *,
    scenarios: tuple[ForecastScenario, ...] | None = None,
    risk_map: ForecastRiskMap | None = None,
    stability: ForecastStabilityScore | None = None,
    bifurcations: tuple[ForecastBifurcation, ...] | None = None,
    **kwargs,
) -> ForecastDecision:
    """Decide which forecast path AGIcore should prioritize."""
    data = _input(forecast_input, **kwargs)
    resolved_scenarios = scenarios or build_forecast_scenarios(data)
    resolved_risk_map = risk_map or build_forecast_risk_map(data)
    resolved_bifurcations = bifurcations or detect_forecast_bifurcations(data, scenarios=resolved_scenarios)
    resolved_stability = stability or compute_forecast_stability_score(data, scenarios=resolved_scenarios, risk_map=resolved_risk_map, bifurcations=resolved_bifurcations)
    scenario_types = {scenario.scenario_type for scenario in resolved_scenarios if scenario.probability_score >= 55}
    critical_count = len({ForecastScenarioType.SYSTEM_DEGRADATION, ForecastScenarioType.SAFE_MODE_TRANSITION, ForecastScenarioType.MISSION_CONTINUITY_BREAK, ForecastScenarioType.EMERGENCY_LOCKDOWN_PATH}.intersection(scenario_types))

    if _evidence_count(data) < 2:
        return ForecastDecision.REQUIRE_OBSERVATION_WINDOW
    if critical_count >= 3 or any(s.scenario_type == ForecastScenarioType.EMERGENCY_LOCKDOWN_PATH and s.probability_score >= 55 for s in resolved_scenarios):
        return ForecastDecision.ENTER_FORECAST_SAFE_MODE
    if resolved_stability.confidence_score < 45:
        return ForecastDecision.REQUIRE_OBSERVATION_WINDOW
    if resolved_bifurcations and resolved_stability.scenario_balance_score < 60:
        return ForecastDecision.REQUIRE_HUMAN_REVIEW
    if ForecastScenarioType.RECOVERY_SUCCESS in scenario_types and ForecastScenarioType.RECOVERY_FAILURE in scenario_types:
        return ForecastDecision.PREPARE_RECOVERY_PATH
    if _max_risk(resolved_risk_map) >= 75:
        return ForecastDecision.AVOID_HIGH_RISK_SCENARIO
    if ForecastScenarioType.SAFE_MODE_TRANSITION in scenario_types:
        return ForecastDecision.PRIORITIZE_SAFE_SCENARIO
    if ForecastScenarioType.STABLE_CONTINUATION in scenario_types or ForecastScenarioType.CONTROLLED_GROWTH in scenario_types:
        return ForecastDecision.CONTINUE_CURRENT_PATH
    return ForecastDecision.REBUILD_FORECAST_MODEL


def generate_forecast_recommendations(
    forecast_input: ScenarioForecastInput | None = None,
    *,
    decision: ForecastDecision | None = None,
    risk_map: ForecastRiskMap | None = None,
    scenarios: tuple[ForecastScenario, ...] | None = None,
    **kwargs,
) -> tuple[ForecastRecommendation, ...]:
    """Generate recommendations from the forecast decision and risk map."""
    data = _input(forecast_input, **kwargs)
    resolved_scenarios = scenarios or build_forecast_scenarios(data)
    resolved_risk_map = risk_map or build_forecast_risk_map(data)
    resolved_decision = decision or decide_forecast_path(data, scenarios=resolved_scenarios, risk_map=resolved_risk_map)
    recommendations: list[ForecastRecommendation] = []

    if resolved_decision in {ForecastDecision.ENTER_FORECAST_SAFE_MODE, ForecastDecision.AVOID_HIGH_RISK_SCENARIO, ForecastDecision.PRIORITIZE_SAFE_SCENARIO}:
        recommendations.append(ForecastRecommendation.REDUCE_RISK_EXPOSURE)
        recommendations.append(ForecastRecommendation.INCREASE_MONITORING)
    if resolved_decision == ForecastDecision.PREPARE_RECOVERY_PATH or any(s.scenario_type in {ForecastScenarioType.RECOVERY_SUCCESS, ForecastScenarioType.RECOVERY_FAILURE} for s in resolved_scenarios):
        recommendations.append(ForecastRecommendation.PRIORITIZE_RECOVERY_SCENARIO)
    if resolved_risk_map.strategy >= 65 or resolved_risk_map.mission >= 65 or _strategy_drift(data):
        recommendations.append(ForecastRecommendation.PROTECT_STRATEGIC_MEMORY)
        recommendations.append(ForecastRecommendation.UPDATE_LONG_HORIZON_PLAN)
    if resolved_risk_map.integrity >= 65:
        recommendations.append(ForecastRecommendation.CHECK_SYSTEM_INTEGRITY)
    if resolved_risk_map.behavior >= 65:
        recommendations.append(ForecastRecommendation.STABILIZE_BEHAVIOR)
    if resolved_risk_map.cognition >= 65 or resolved_decision == ForecastDecision.REQUIRE_OBSERVATION_WINDOW:
        recommendations.append(ForecastRecommendation.EXTEND_OBSERVATION_PERIOD)
    if _policy_expansion_unsafe(data):
        recommendations.append(ForecastRecommendation.FREEZE_POLICY_EXPANSION)
    if not recommendations:
        recommendations.append(ForecastRecommendation.MAINTAIN_CURRENT_TRAJECTORY)
    return tuple(dict.fromkeys(recommendations))


def render_scenario_forecast_markdown(result: ScenarioForecastResult) -> str:
    """Render scenario forecast as Markdown."""
    lines = [
        "# Autonomous Scenario Forecast Engine",
        "",
        "## Scenario Forecast State",
        "",
        f"- Decision: {result.decision.value}",
        f"- Stability: {result.forecast_stability_score}/100",
        "",
        "## Forecast Scenarios",
        "",
        *_bullet_lines(tuple(f"{scenario.scenario_type.value}: {scenario.probability_score}/100, survivable={scenario.survivable}" for scenario in result.scenarios)),
        "",
        "## Probability Bands",
        "",
        *_bullet_lines(tuple(f"{scenario.scenario_type.value}: {scenario.probability_band.value}" for scenario in result.scenarios)),
        "",
        "## Bifurcations",
        "",
        *_bullet_lines(tuple(f"{b.positive_scenario.value} vs {b.negative_scenario.value}: {b.severity_score}/100" for b in result.bifurcations)),
        "",
        "## Risk Map",
        "",
        f"- strategy: {result.risk_map.strategy}/100",
        f"- behavior: {result.risk_map.behavior}/100",
        f"- cognition: {result.risk_map.cognition}/100",
        f"- integrity: {result.risk_map.integrity}/100",
        f"- continuity: {result.risk_map.continuity}/100",
        f"- recovery: {result.risk_map.recovery}/100",
        f"- mission: {result.risk_map.mission}/100",
        "",
        "## Stability Score",
        "",
        f"- {result.forecast_stability_score}/100",
        "",
        "## Forecast Decision",
        "",
        f"- {result.decision.value}",
        "",
        "## Recommendations",
        "",
        *_bullet_lines(tuple(recommendation.value for recommendation in result.recommendations)),
        "",
        "## AGIcore Forecast Outlook",
        "",
        f"- {result.summary}",
        "- Offline only: no broker, no real order, no external API, no external ML, no external LLM, no neural training, no live execution.",
        "",
    ]
    return "\n".join(lines)


def forecast_scenarios(
    forecast_input: ScenarioForecastInput | None = None,
    **kwargs,
) -> ScenarioForecastResult:
    """Run the full offline scenario forecast pipeline."""
    data = _input(forecast_input, **kwargs)
    scenarios = build_forecast_scenarios(data)
    bifurcations = detect_forecast_bifurcations(data, scenarios=scenarios)
    risk_map = build_forecast_risk_map(data)
    stability = compute_forecast_stability_score(data, scenarios=scenarios, risk_map=risk_map, bifurcations=bifurcations)
    decision = decide_forecast_path(data, scenarios=scenarios, risk_map=risk_map, stability=stability, bifurcations=bifurcations)
    recommendations = generate_forecast_recommendations(data, decision=decision, risk_map=risk_map, scenarios=scenarios)
    score = _overall_stability(stability, risk_map)
    event = ForecastEvent(decision, f"Scenario forecast selected {decision.value}.", datetime.now(UTC))
    return ScenarioForecastResult(
        decision,
        score,
        stability,
        scenarios,
        bifurcations,
        risk_map,
        recommendations,
        tuple(s.scenario_type for s in scenarios if s.survivable),
        tuple(s.scenario_type for s in scenarios if not s.survivable or s.stability_impact_score >= 80),
        (event,),
        f"{len(scenarios)} scenario(s), {len(bifurcations)} bifurcation(s), decision {decision.value}.",
    )


def _candidate_types(data: ScenarioForecastInput) -> tuple[ForecastScenarioType, ...]:
    types = {ForecastScenarioType.STABLE_CONTINUATION}
    if _system_health(data) >= 70 and _strategy_score(data) >= 70:
        types.add(ForecastScenarioType.CONTROLLED_GROWTH)
    if _recovery_context(data):
        types.add(ForecastScenarioType.RECOVERY_SUCCESS)
        types.add(ForecastScenarioType.RECOVERY_FAILURE)
    if _strategy_drift(data):
        types.add(ForecastScenarioType.STRATEGIC_DRIFT)
    if _behavior_score(data) < 65:
        types.add(ForecastScenarioType.BEHAVIORAL_REGRESSION)
    if _system_health(data) < 65 or (data.system_integrity is not None and data.system_integrity.status != SystemIntegrityStatus.HEALTHY):
        types.add(ForecastScenarioType.SYSTEM_DEGRADATION)
    if _safe_mode_needed(data):
        types.add(ForecastScenarioType.SAFE_MODE_TRANSITION)
    if _mission_risk(data) >= 60:
        types.add(ForecastScenarioType.MISSION_CONTINUITY_BREAK)
    if _critical_count(data) >= 2:
        types.add(ForecastScenarioType.EMERGENCY_LOCKDOWN_PATH)
    return tuple(sorted(types, key=lambda item: item.value))


def _band(score: int) -> ForecastProbabilityBand:
    if score < 0:
        return ForecastProbabilityBand.UNKNOWN
    if score < 20:
        return ForecastProbabilityBand.VERY_LOW
    if score < 40:
        return ForecastProbabilityBand.LOW
    if score < 60:
        return ForecastProbabilityBand.MODERATE
    if score < 80:
        return ForecastProbabilityBand.HIGH
    return ForecastProbabilityBand.VERY_HIGH


def _survivable(scenario_type: ForecastScenarioType, data: ScenarioForecastInput) -> bool:
    if scenario_type == ForecastScenarioType.EMERGENCY_LOCKDOWN_PATH:
        return False
    if scenario_type == ForecastScenarioType.MISSION_CONTINUITY_BREAK and _mission_risk(data) >= 80:
        return False
    if scenario_type == ForecastScenarioType.SYSTEM_DEGRADATION and _system_health(data) < 25:
        return False
    return True


def _impact(scenario_type: ForecastScenarioType) -> int:
    return {
        ForecastScenarioType.STABLE_CONTINUATION: 30,
        ForecastScenarioType.CONTROLLED_GROWTH: 35,
        ForecastScenarioType.RECOVERY_SUCCESS: 45,
        ForecastScenarioType.RECOVERY_FAILURE: 75,
        ForecastScenarioType.STRATEGIC_DRIFT: 70,
        ForecastScenarioType.BEHAVIORAL_REGRESSION: 70,
        ForecastScenarioType.SYSTEM_DEGRADATION: 85,
        ForecastScenarioType.SAFE_MODE_TRANSITION: 65,
        ForecastScenarioType.MISSION_CONTINUITY_BREAK: 90,
        ForecastScenarioType.EMERGENCY_LOCKDOWN_PATH: 100,
    }[scenario_type]


def _description(scenario_type: ForecastScenarioType) -> str:
    return scenario_type.value.lower().replace("_", " ")


def _risk_notes(scenario_type: ForecastScenarioType, data: ScenarioForecastInput) -> tuple[str, ...]:
    notes: list[str] = []
    if scenario_type in {ForecastScenarioType.SYSTEM_DEGRADATION, ForecastScenarioType.EMERGENCY_LOCKDOWN_PATH} and data.system_integrity is not None:
        notes.append(f"integrity={data.system_integrity.status.value}")
    if scenario_type == ForecastScenarioType.BEHAVIORAL_REGRESSION and data.behavioral_stability is not None:
        notes.append(f"pressure={data.behavioral_stability.pressure_level.value}")
    if scenario_type == ForecastScenarioType.STRATEGIC_DRIFT and data.strategic_timeline_analysis is not None:
        notes.append("strategic timeline degradation")
    return tuple(notes)


def _system_health(data: ScenarioForecastInput) -> int:
    if data.health_snapshot is not None:
        return data.health_snapshot.orchestration_confidence
    if data.global_orchestrator is not None:
        return data.global_orchestrator.confidence_score
    if data.system_integrity is not None:
        return data.system_integrity.integrity_score
    return 70


def _strategy_score(data: ScenarioForecastInput) -> int:
    if data.long_horizon_plan is not None:
        return data.long_horizon_plan.projection.projected_stability_score
    if data.strategic_timeline_analysis is not None:
        return data.strategic_timeline_analysis.strategic_health_score
    return 70


def _behavior_score(data: ScenarioForecastInput) -> int:
    if data.behavioral_stability is not None:
        return data.behavioral_stability.stability_score
    return 70


def _cognitive_score(data: ScenarioForecastInput) -> int:
    if data.cognitive_adaptation is not None:
        return data.cognitive_adaptation.global_score
    return 70


def _recovery_score(data: ScenarioForecastInput) -> int:
    if data.recovery_resilience is not None:
        return data.recovery_resilience.resilience_score
    if data.long_horizon_plan is not None:
        return data.long_horizon_plan.projection.projected_recovery_score
    return 65


def _mission_risk(data: ScenarioForecastInput) -> int:
    risk = 30
    if data.mission_continuity is not None and data.mission_continuity.mode != MissionContinuityMode.FULL_OPERATION:
        risk += 30
        risk += max(0, 70 - data.mission_continuity.continuity_score) // 2
    if data.intent_alignment is not None and data.intent_alignment.mode not in {IntentAlignmentMode.FULLY_ALIGNED, IntentAlignmentMode.STABLE_ALIGNMENT}:
        risk += 25
    return _clamp(risk)


def _risk_from_score(score: int) -> int:
    return _clamp(100 - score)


def _drawdown_pressure(data: ScenarioForecastInput) -> bool:
    return (
        data.long_horizon_plan is not None and PlanningRisk.FUTURE_DRAWDOWN_RISK in data.long_horizon_plan.risks
    ) or (
        data.strategic_timeline_analysis is not None and StrategicDriftSignal.PERSISTENT_DRAWDOWN in data.strategic_timeline_analysis.drift_signals
    ) or (
        data.reward_evaluation is not None and data.reward_evaluation.reward_label in {RewardLabel.BAD_DECISION, RewardLabel.DANGEROUS_DECISION}
    )


def _strategy_drift(data: ScenarioForecastInput) -> bool:
    return (
        data.long_horizon_plan is not None and PlanningRisk.STRATEGIC_DRIFT_RISK in data.long_horizon_plan.risks
    ) or (
        data.strategic_timeline_analysis is not None and (data.strategic_timeline_analysis.degradation_detected or StrategicDriftSignal.STRATEGIC_DEGRADATION in data.strategic_timeline_analysis.drift_signals)
    )


def _recovery_context(data: ScenarioForecastInput) -> bool:
    return (
        data.recovery_resilience is not None and data.recovery_resilience.mode != RecoveryMode.NORMAL
    ) or (
        data.long_horizon_plan is not None and data.long_horizon_plan.decision in {PlanningDecision.PRIORITIZE_RECOVERY, PlanningDecision.ENTER_LONG_HORIZON_SAFE_MODE}
    ) or _drawdown_pressure(data)


def _safe_mode_needed(data: ScenarioForecastInput) -> bool:
    return (
        (data.long_horizon_plan is not None and data.long_horizon_plan.decision == PlanningDecision.ENTER_LONG_HORIZON_SAFE_MODE)
        or (data.global_orchestrator is not None and data.global_orchestrator.decision in {OrchestratorDecision.ENTER_SAFE_GLOBAL_MODE, OrchestratorDecision.ACTIVATE_SURVIVAL_MODE, OrchestratorDecision.EMERGENCY_HALT_ROUTING})
        or (data.coordination_result is not None and OrchestratorRisk.GLOBAL_SAFE_MODE_REQUIRED in data.coordination_result.state.risks)
        or (data.strategic_arbitration is not None and data.strategic_arbitration.decision in {ArbitrationDecision.EMERGENCY_LOCKDOWN, ArbitrationDecision.ENABLE_SAFE_MODE, ArbitrationDecision.STOP_EXECUTION})
        or (data.collective_consensus is not None and data.collective_consensus.decision in {ConsensusDecision.EMERGENCY_HALT, ConsensusDecision.ENTER_SAFE_MODE, ConsensusDecision.BLOCK_COLLECTIVE_ACTION})
    )


def _critical_count(data: ScenarioForecastInput) -> int:
    count = 0
    if data.system_integrity is not None and data.system_integrity.status in {SystemIntegrityStatus.COMPROMISED, SystemIntegrityStatus.ROLLBACK_RECOMMENDED}:
        count += 1
    if data.operational_awareness is not None and data.operational_awareness.health_status in {OperationalHealthStatus.CRITICAL, OperationalHealthStatus.COLLAPSING}:
        count += 1
    if data.global_orchestrator is not None and data.global_orchestrator.system_state.mode in {OrchestratorMode.EMERGENCY_ORCHESTRATION, OrchestratorMode.SURVIVAL_ORCHESTRATION}:
        count += 1
    if data.strategic_arbitration is not None and data.strategic_arbitration.mode == ArbitrationMode.EMERGENCY_LOCKDOWN:
        count += 1
    if data.collective_consensus is not None and data.collective_consensus.mode == ConsensusMode.EMERGENCY_CONSENSUS:
        count += 1
    if data.cognitive_adaptation is not None and data.cognitive_adaptation.load_level == CognitiveLoadLevel.OVERLOADED:
        count += 1
    return count


def _danger_count(data: ScenarioForecastInput) -> int:
    count = _critical_count(data)
    if _safe_mode_needed(data):
        count += 1
    if _strategy_drift(data):
        count += 1
    if data.behavioral_stability is not None and data.behavioral_stability.pressure_level in {BehavioralPressureLevel.HIGH, BehavioralPressureLevel.EXTREME}:
        count += 1
    return count


def _dangerous_scenarios(scenarios: tuple[ForecastScenario, ...]) -> tuple[ForecastScenario, ...]:
    dangerous_types = {
        ForecastScenarioType.RECOVERY_FAILURE,
        ForecastScenarioType.STRATEGIC_DRIFT,
        ForecastScenarioType.BEHAVIORAL_REGRESSION,
        ForecastScenarioType.SYSTEM_DEGRADATION,
        ForecastScenarioType.SAFE_MODE_TRANSITION,
        ForecastScenarioType.MISSION_CONTINUITY_BREAK,
        ForecastScenarioType.EMERGENCY_LOCKDOWN_PATH,
    }
    return tuple(scenario for scenario in scenarios if scenario.scenario_type in dangerous_types and scenario.probability_score >= 50)


def _max_risk(risk_map: ForecastRiskMap) -> int:
    return max(risk_map.strategy, risk_map.behavior, risk_map.cognition, risk_map.integrity, risk_map.continuity, risk_map.recovery, risk_map.mission)


def _available_confidence(data: ScenarioForecastInput) -> int:
    scores: list[int] = []
    for value in (
        data.long_horizon_plan.projection_confidence if data.long_horizon_plan is not None else None,
        data.global_orchestrator.confidence_score if data.global_orchestrator is not None else None,
        data.health_snapshot.orchestration_confidence if data.health_snapshot is not None else None,
        data.strategic_timeline_analysis.strategic_health_score if data.strategic_timeline_analysis is not None else None,
        data.system_integrity.integrity_score if data.system_integrity is not None else None,
        data.collective_consensus.collective_confidence_score if data.collective_consensus is not None else None,
        data.reward_evaluation.normalized_reward if data.reward_evaluation is not None else None,
    ):
        if value is not None:
            scores.append(value)
    if not scores:
        return 45
    return _clamp(sum(scores) / len(scores))


def _evidence_count(data: ScenarioForecastInput) -> int:
    return sum(
        value is not None
        for value in (
            data.long_horizon_plan,
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


def _policy_expansion_unsafe(data: ScenarioForecastInput) -> bool:
    return (
        data.long_horizon_plan is not None
        and PlanningRisk.LEARNING_OVERADAPTATION_RISK in data.long_horizon_plan.risks
    ) or _system_health(data) < 55


def _overall_stability(stability: ForecastStabilityScore, risk_map: ForecastRiskMap) -> int:
    risk_penalty = _max_risk(risk_map) // 5
    score = (
        stability.scenario_balance_score
        + stability.survivability_score
        + stability.system_health_score
        + stability.behavioral_stability_score
        + stability.continuity_score
        + stability.confidence_score
    ) / 6
    return _clamp(score - risk_penalty)


def _input(forecast_input: ScenarioForecastInput | None = None, **kwargs: Any) -> ScenarioForecastInput:
    if forecast_input is not None:
        return forecast_input
    return ScenarioForecastInput(**kwargs)


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _clamp(value: int | float) -> int:
    return max(0, min(100, int(round(value))))


__all__ = [
    "build_forecast_risk_map",
    "build_forecast_scenarios",
    "compute_forecast_stability_score",
    "decide_forecast_path",
    "detect_forecast_bifurcations",
    "estimate_scenario_probability",
    "forecast_scenarios",
    "generate_forecast_recommendations",
    "render_scenario_forecast_markdown",
]
