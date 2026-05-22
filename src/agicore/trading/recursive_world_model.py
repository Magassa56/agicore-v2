"""Offline Autonomous Recursive World Model Engine for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .cognitive_adaptation_models import CognitiveLoadLevel
from .global_orchestrator_models import OrchestratorDecision, OrchestratorMode, OrchestratorRisk
from .intent_alignment_models import IntentAlignmentMode
from .multi_timeline_simulation_models import TimelineDecision, TimelineOutcome, TimelineRisk
from .recursive_world_model_models import (
    RecursiveWorldModelInput,
    RecursiveWorldModelResult,
    WorldModelCausalLink,
    WorldModelCoherenceScore,
    WorldModelDecision,
    WorldModelEvent,
    WorldModelGraph,
    WorldModelLayer,
    WorldModelPrediction,
    WorldModelRecommendation,
    WorldModelRisk,
    WorldModelState,
)
from .reward_models import RewardLabel
from .scenario_forecast_models import ForecastDecision, ForecastScenarioType
from .strategic_arbitration_models import ArbitrationDecision
from .strategic_memory_models import StrategicDriftSignal
from .strategy_evolution_models import StrategyEvolutionDecision, StrategyEvolutionMode
from .system_integrity_models import SystemIntegrityStatus


def build_world_model_graph(
    world_model_input: RecursiveWorldModelInput | None = None,
    **kwargs,
) -> WorldModelGraph:
    """Build the recursive causal graph connecting core world model layers."""
    data = _input(world_model_input, **kwargs)
    states = evaluate_world_model_state(data)
    state_by_layer = {state.layer: state for state in states}
    links = (
        _link(WorldModelLayer.PERCEPTION, WorldModelLayer.STATE_MEMORY, _evidence_count(data), "market/session observations update memory"),
        _link(WorldModelLayer.STATE_MEMORY, WorldModelLayer.DYNAMICS, state_by_layer[WorldModelLayer.STATE_MEMORY].coherence_score, "memory conditions dynamics"),
        _link(WorldModelLayer.DYNAMICS, WorldModelLayer.PLANNING, state_by_layer[WorldModelLayer.DYNAMICS].coherence_score, "dynamics constrain planning"),
        _link(WorldModelLayer.PLANNING, WorldModelLayer.ACTION, state_by_layer[WorldModelLayer.PLANNING].coherence_score, "plans constrain action"),
        _link(WorldModelLayer.GOVERNANCE, WorldModelLayer.PLANNING, state_by_layer[WorldModelLayer.GOVERNANCE].coherence_score, "governance limits planning"),
        _link(WorldModelLayer.SAFETY, WorldModelLayer.ACTION, state_by_layer[WorldModelLayer.SAFETY].coherence_score, "safety gates action"),
        _link(WorldModelLayer.FORECASTING, WorldModelLayer.DYNAMICS, state_by_layer[WorldModelLayer.FORECASTING].coherence_score, "forecast projects dynamics"),
        _link(WorldModelLayer.META_COGNITION, WorldModelLayer.GOVERNANCE, state_by_layer[WorldModelLayer.META_COGNITION].coherence_score, "meta cognition adjusts governance"),
        _link(WorldModelLayer.ORCHESTRATION, WorldModelLayer.SAFETY, state_by_layer[WorldModelLayer.ORCHESTRATION].coherence_score, "orchestration synchronizes safety"),
    )
    critical = tuple(state.layer for state in states if state.coherence_score < 35)
    unstable = tuple(state.layer for state in states if state.coherence_score < 55)
    dominant = min(states, key=lambda state: state.coherence_score).layer if states else None
    return WorldModelGraph(tuple(state.layer for state in states), links, critical, unstable, dominant)


def evaluate_world_model_state(
    world_model_input: RecursiveWorldModelInput | None = None,
    **kwargs,
) -> tuple[WorldModelState, ...]:
    """Evaluate coherence status for every recursive world model layer."""
    data = _input(world_model_input, **kwargs)
    scores = {
        WorldModelLayer.PERCEPTION: _perception_score(data),
        WorldModelLayer.STATE_MEMORY: _state_memory_score(data),
        WorldModelLayer.DYNAMICS: _dynamics_score(data),
        WorldModelLayer.PLANNING: _planning_score(data),
        WorldModelLayer.ACTION: _action_score(data),
        WorldModelLayer.GOVERNANCE: _governance_score(data),
        WorldModelLayer.SAFETY: _safety_score(data),
        WorldModelLayer.META_COGNITION: _meta_cognition_score(data),
        WorldModelLayer.FORECASTING: _forecasting_score(data),
        WorldModelLayer.ORCHESTRATION: _orchestration_score(data),
    }
    return tuple(
        WorldModelState(layer, score, _layer_confidence(data, layer), _status(score), _signals_for_layer(data, layer))
        for layer, score in scores.items()
    )


def detect_world_model_risks(
    world_model_input: RecursiveWorldModelInput | None = None,
    *,
    states: tuple[WorldModelState, ...] | None = None,
    predictions: tuple[WorldModelPrediction, ...] | None = None,
    **kwargs,
) -> tuple[WorldModelRisk, ...]:
    """Detect recursive world model risks from state and causal predictions."""
    data = _input(world_model_input, **kwargs)
    resolved_states = states or evaluate_world_model_state(data)
    resolved_predictions = predictions or simulate_causal_impacts(data, states=resolved_states)
    by_layer = {state.layer: state.coherence_score for state in resolved_states}
    risks: list[WorldModelRisk] = []

    if _avg(list(by_layer.values()), 50) < 55:
        risks.append(WorldModelRisk.WORLD_MODEL_INCOHERENCE)
    if any(prediction.impact_score >= 70 and prediction.confidence_score < 45 for prediction in resolved_predictions):
        risks.append(WorldModelRisk.CAUSAL_CONTRADICTION)
    if by_layer.get(WorldModelLayer.STATE_MEMORY, 100) < 55 or _state_drift(data):
        risks.append(WorldModelRisk.STATE_DRIFT)
    if by_layer.get(WorldModelLayer.DYNAMICS, 100) < 50:
        risks.append(WorldModelRisk.DYNAMICS_INSTABILITY)
    if _planning_action_mismatch(data):
        risks.append(WorldModelRisk.PLANNING_ACTION_MISMATCH)
    if _forecast_reality_gap(data):
        risks.append(WorldModelRisk.FORECAST_REALITY_GAP)
    if _orchestration_desync(data):
        risks.append(WorldModelRisk.ORCHESTRATION_DESYNC)
    if by_layer.get(WorldModelLayer.GOVERNANCE, 100) < 55 or _governance_misaligned(data):
        risks.append(WorldModelRisk.GOVERNANCE_MISALIGNMENT)
    if by_layer.get(WorldModelLayer.SAFETY, 100) < 50 or _safety_failure(data):
        risks.append(WorldModelRisk.SAFETY_MODEL_FAILURE)
    if _recursive_feedback_loop(data):
        risks.append(WorldModelRisk.RECURSIVE_FEEDBACK_LOOP)
    return tuple(dict.fromkeys(risks))


def simulate_causal_impacts(
    world_model_input: RecursiveWorldModelInput | None = None,
    *,
    states: tuple[WorldModelState, ...] | None = None,
    graph: WorldModelGraph | None = None,
    **kwargs,
) -> tuple[WorldModelPrediction, ...]:
    """Simulate deterministic causal impacts between recursive layers."""
    data = _input(world_model_input, **kwargs)
    resolved_states = states or evaluate_world_model_state(data)
    resolved_graph = graph or build_world_model_graph(data)
    state_by_layer = {state.layer: state for state in resolved_states}
    predictions: list[WorldModelPrediction] = []
    for link in resolved_graph.links:
        source = state_by_layer[link.source]
        target = state_by_layer[link.target]
        impact = _clamp(abs(source.coherence_score - target.coherence_score) + max(0, 70 - source.coherence_score) // 2)
        confidence = _clamp((source.confidence_score + target.confidence_score + link.strength_score) / 3)
        risks = _prediction_risks(link, impact, confidence)
        predictions.append(WorldModelPrediction(link.source, link.target, impact, confidence, f"{link.source.value} impacts {link.target.value}", risks))
    return tuple(predictions)


def compute_world_model_coherence(
    world_model_input: RecursiveWorldModelInput | None = None,
    *,
    states: tuple[WorldModelState, ...] | None = None,
    predictions: tuple[WorldModelPrediction, ...] | None = None,
    **kwargs,
) -> WorldModelCoherenceScore:
    """Compute component coherence scores for the recursive world model."""
    data = _input(world_model_input, **kwargs)
    resolved_states = states or evaluate_world_model_state(data)
    resolved_predictions = predictions or simulate_causal_impacts(data, states=resolved_states)
    by_layer = {state.layer: state.coherence_score for state in resolved_states}
    causal = _clamp(100 - sum(prediction.impact_score for prediction in resolved_predictions) / max(1, len(resolved_predictions)) + _confidence(data) // 10)
    return WorldModelCoherenceScore(
        by_layer.get(WorldModelLayer.PERCEPTION, 50),
        by_layer.get(WorldModelLayer.STATE_MEMORY, 50),
        by_layer.get(WorldModelLayer.DYNAMICS, 50),
        by_layer.get(WorldModelLayer.PLANNING, 50),
        by_layer.get(WorldModelLayer.ACTION, 50),
        by_layer.get(WorldModelLayer.GOVERNANCE, 50),
        by_layer.get(WorldModelLayer.SAFETY, 50),
        by_layer.get(WorldModelLayer.META_COGNITION, 50),
        by_layer.get(WorldModelLayer.FORECASTING, 50),
        by_layer.get(WorldModelLayer.ORCHESTRATION, 50),
        causal,
    )


def decide_world_model_action(
    world_model_input: RecursiveWorldModelInput | None = None,
    *,
    coherence: WorldModelCoherenceScore | None = None,
    risks: tuple[WorldModelRisk, ...] | None = None,
    graph: WorldModelGraph | None = None,
    **kwargs,
) -> WorldModelDecision:
    """Decide how the recursive world model should update itself."""
    data = _input(world_model_input, **kwargs)
    resolved_coherence = coherence or compute_world_model_coherence(data)
    resolved_graph = graph or build_world_model_graph(data)
    resolved_risks = risks or detect_world_model_risks(data)
    overall = _overall_coherence(resolved_coherence)
    critical = {
        WorldModelRisk.SAFETY_MODEL_FAILURE,
        WorldModelRisk.ORCHESTRATION_DESYNC,
        WorldModelRisk.RECURSIVE_FEEDBACK_LOOP,
        WorldModelRisk.GOVERNANCE_MISALIGNMENT,
    }

    if WorldModelRisk.RECURSIVE_FEEDBACK_LOOP in resolved_risks:
        return WorldModelDecision.FREEZE_RECURSIVE_UPDATES
    if len(critical.intersection(resolved_risks)) >= 3:
        return WorldModelDecision.ENTER_WORLD_MODEL_SAFE_MODE
    if WorldModelRisk.SAFETY_MODEL_FAILURE in resolved_risks:
        return WorldModelDecision.PRIORITIZE_SAFETY_MODEL
    if _evidence_count(data) < 2 or overall < 45:
        return WorldModelDecision.REQUIRE_MORE_OBSERVATION
    if len(resolved_graph.unstable_layers) >= 4 or WorldModelRisk.CAUSAL_CONTRADICTION in resolved_risks:
        return WorldModelDecision.REBUILD_CAUSAL_GRAPH
    if WorldModelRisk.PLANNING_ACTION_MISMATCH in resolved_risks or WorldModelRisk.STATE_DRIFT in resolved_risks:
        return WorldModelDecision.UPDATE_INTERNAL_STATE
    if WorldModelRisk.ORCHESTRATION_DESYNC in resolved_risks:
        return WorldModelDecision.REQUIRE_HUMAN_REVIEW
    return WorldModelDecision.MAINTAIN_WORLD_MODEL


def generate_world_model_recommendations(
    world_model_input: RecursiveWorldModelInput | None = None,
    *,
    decision: WorldModelDecision | None = None,
    risks: tuple[WorldModelRisk, ...] | None = None,
    **kwargs,
) -> tuple[WorldModelRecommendation, ...]:
    """Generate world model recommendations from decision and risk set."""
    data = _input(world_model_input, **kwargs)
    resolved_risks = risks or detect_world_model_risks(data)
    resolved_decision = decision or decide_world_model_action(data, risks=resolved_risks)
    recommendations: list[WorldModelRecommendation] = [WorldModelRecommendation.PRESERVE_WORLD_MODEL_SNAPSHOT]

    if WorldModelRisk.STATE_DRIFT in resolved_risks or resolved_decision == WorldModelDecision.UPDATE_INTERNAL_STATE:
        recommendations.append(WorldModelRecommendation.UPDATE_STATE_MEMORY)
    if WorldModelRisk.CAUSAL_CONTRADICTION in resolved_risks or resolved_decision == WorldModelDecision.REBUILD_CAUSAL_GRAPH:
        recommendations.append(WorldModelRecommendation.REBALANCE_CAUSAL_LINKS)
    if WorldModelRisk.FORECAST_REALITY_GAP in resolved_risks:
        recommendations.append(WorldModelRecommendation.CHECK_FORECAST_ALIGNMENT)
    if WorldModelRisk.DYNAMICS_INSTABILITY in resolved_risks:
        recommendations.append(WorldModelRecommendation.STABILIZE_DYNAMICS)
    if WorldModelRisk.PLANNING_ACTION_MISMATCH in resolved_risks:
        recommendations.append(WorldModelRecommendation.ALIGN_PLANNING_ACTION)
    if WorldModelRisk.RECURSIVE_FEEDBACK_LOOP in resolved_risks:
        recommendations.append(WorldModelRecommendation.REDUCE_RECURSIVE_DEPTH)
    if WorldModelRisk.SAFETY_MODEL_FAILURE in resolved_risks or resolved_decision == WorldModelDecision.PRIORITIZE_SAFETY_MODEL:
        recommendations.append(WorldModelRecommendation.PROTECT_SAFETY_MODEL)
    if WorldModelRisk.ORCHESTRATION_DESYNC in resolved_risks:
        recommendations.append(WorldModelRecommendation.SYNC_ORCHESTRATION_STATE)
    if resolved_decision == WorldModelDecision.REQUIRE_MORE_OBSERVATION:
        recommendations.append(WorldModelRecommendation.EXTEND_OBSERVATION_WINDOW)
    return tuple(dict.fromkeys(recommendations))


def render_recursive_world_model_markdown(result: RecursiveWorldModelResult) -> str:
    """Render recursive world model result as Markdown."""
    lines = [
        "# Autonomous Recursive World Model Engine",
        "",
        "## Recursive World Model State",
        "",
        f"- Decision: {result.decision.value}",
        f"- Coherence: {result.world_model_coherence_score}/100",
        "",
        "## World Model Layers",
        "",
        *_bullet_lines(tuple(f"{state.layer.value}: {state.coherence_score}/100 {state.status}" for state in result.states)),
        "",
        "## Causal Graph",
        "",
        *_bullet_lines(tuple(f"{link.source.value} -> {link.target.value}: {link.strength_score}/100" for link in result.graph.links)),
        "",
        "## Predicted Impacts",
        "",
        *_bullet_lines(tuple(f"{prediction.source_layer.value} -> {prediction.target_layer.value}: impact={prediction.impact_score}/100" for prediction in result.predictions)),
        "",
        "## Coherence Score",
        "",
        f"- Overall: {result.world_model_coherence_score}/100",
        f"- Causal consistency: {result.coherence_breakdown.causal_consistency_score}/100",
        "",
        "## Risks",
        "",
        *_bullet_lines(tuple(risk.value for risk in result.risks)),
        "",
        "## Decision",
        "",
        f"- {result.decision.value}",
        "",
        "## Recommendations",
        "",
        *_bullet_lines(tuple(recommendation.value for recommendation in result.recommendations)),
        "",
        "## AGIcore World Model Outlook",
        "",
        result.summary,
    ]
    return "\n".join(lines)


def evaluate_recursive_world_model(
    world_model_input: RecursiveWorldModelInput | None = None,
    **kwargs,
) -> RecursiveWorldModelResult:
    """Run the full offline recursive world model pipeline."""
    data = _input(world_model_input, **kwargs)
    states = evaluate_world_model_state(data)
    graph = build_world_model_graph(data)
    predictions = simulate_causal_impacts(data, states=states, graph=graph)
    coherence = compute_world_model_coherence(data, states=states, predictions=predictions)
    risks = detect_world_model_risks(data, states=states, predictions=predictions)
    decision = decide_world_model_action(data, coherence=coherence, risks=risks, graph=graph)
    recommendations = generate_world_model_recommendations(data, decision=decision, risks=risks)
    overall = _overall_coherence(coherence)
    event = WorldModelEvent(decision, f"recursive world model decision={decision.value}", datetime.now(UTC))
    return RecursiveWorldModelResult(decision, overall, coherence, states, graph, predictions, risks, recommendations, (event,), f"{decision.value} with coherence {overall}/100")


def _input(world_model_input: RecursiveWorldModelInput | None = None, **kwargs) -> RecursiveWorldModelInput:
    if world_model_input is not None and kwargs:
        raise ValueError("Pass either RecursiveWorldModelInput or keyword inputs, not both")
    if world_model_input is not None:
        return world_model_input
    return RecursiveWorldModelInput(**kwargs)


def _link(source: WorldModelLayer, target: WorldModelLayer, strength: int, evidence: str) -> WorldModelCausalLink:
    return WorldModelCausalLink(source, target, _clamp(strength), "positive", evidence)


def _perception_score(data: RecursiveWorldModelInput) -> int:
    return _clamp(50 + min(40, _evidence_count(data) * 5))


def _state_memory_score(data: RecursiveWorldModelInput) -> int:
    values = []
    if data.strategic_timeline_analysis is not None:
        values.append(_get(data.strategic_timeline_analysis, "strategic_health_score", 65))
    if data.multi_timeline is not None:
        values.append(data.multi_timeline.overall_survivability_score)
    return _avg(values, 65)


def _dynamics_score(data: RecursiveWorldModelInput) -> int:
    values = []
    if data.multi_timeline is not None:
        values.append(data.multi_timeline.overall_survivability_score)
    if data.scenario_forecast is not None:
        values.append(data.scenario_forecast.forecast_stability_score)
    if data.recovery_resilience is not None:
        values.append(_get(data.recovery_resilience, "resilience_score", 60))
    return _avg(values, 65)


def _planning_score(data: RecursiveWorldModelInput) -> int:
    values = []
    if data.long_horizon_plan is not None:
        projection = _get(data.long_horizon_plan, "projection", None)
        values.append(_get(projection, "projected_stability_score", 60))
    if data.strategy_evolution is not None:
        values.append(data.strategy_evolution.fitness_score)
    return _avg(values, 65)


def _action_score(data: RecursiveWorldModelInput) -> int:
    score = 70
    if data.reward_evaluation is not None and _get(data.reward_evaluation, "reward_label", None) in {RewardLabel.BAD_DECISION, RewardLabel.DANGEROUS_DECISION}:
        score -= 20
    if data.multi_timeline is not None and data.multi_timeline.decision in {TimelineDecision.ENTER_TIMELINE_SAFE_MODE, TimelineDecision.REQUIRE_HUMAN_REVIEW}:
        score -= 20
    return _clamp(score)


def _governance_score(data: RecursiveWorldModelInput) -> int:
    score = 75
    if data.intent_alignment is not None and data.intent_alignment.mode not in {IntentAlignmentMode.FULLY_ALIGNED, IntentAlignmentMode.STABLE_ALIGNMENT}:
        score -= 25
    if data.strategic_arbitration is not None and data.strategic_arbitration.decision in {ArbitrationDecision.EMERGENCY_LOCKDOWN, ArbitrationDecision.STOP_EXECUTION}:
        score -= 25
    return _clamp(score)


def _safety_score(data: RecursiveWorldModelInput) -> int:
    score = 80
    if data.system_integrity is not None and data.system_integrity.status in {SystemIntegrityStatus.COMPROMISED, SystemIntegrityStatus.ROLLBACK_RECOMMENDED}:
        score -= 35
    if data.multi_timeline is not None and TimelineRisk.COLLAPSE_RISK in data.multi_timeline.risks:
        score -= 25
    if data.scenario_forecast is not None and data.scenario_forecast.decision == ForecastDecision.ENTER_FORECAST_SAFE_MODE:
        score -= 15
    return _clamp(score)


def _meta_cognition_score(data: RecursiveWorldModelInput) -> int:
    if data.cognitive_adaptation is None:
        return 65
    score = _get(data.cognitive_adaptation, "global_score", 65)
    if _get(data.cognitive_adaptation, "load_level", None) == CognitiveLoadLevel.OVERLOADED:
        score -= 25
    return _clamp(score)


def _forecasting_score(data: RecursiveWorldModelInput) -> int:
    values = []
    if data.scenario_forecast is not None:
        values.append(data.scenario_forecast.forecast_stability_score)
        values.append(data.scenario_forecast.stability_breakdown.confidence_score)
    if data.multi_timeline is not None:
        values.append(data.multi_timeline.overall_survivability_score)
    return _avg(values, 60)


def _orchestration_score(data: RecursiveWorldModelInput) -> int:
    if data.health_snapshot is not None:
        return _get(data.health_snapshot, "orchestration_confidence", 65)
    if data.global_orchestrator is not None:
        return data.global_orchestrator.confidence_score
    if data.coordination_result is not None:
        return _get(data.coordination_result.state, "confidence_score", 65)
    return 65


def _layer_confidence(data: RecursiveWorldModelInput, layer: WorldModelLayer) -> int:
    if layer in {WorldModelLayer.PERCEPTION, WorldModelLayer.STATE_MEMORY}:
        return _clamp(40 + _evidence_count(data) * 6)
    if layer == WorldModelLayer.FORECASTING and data.scenario_forecast is not None:
        return data.scenario_forecast.stability_breakdown.confidence_score
    if layer == WorldModelLayer.ORCHESTRATION:
        return _orchestration_score(data)
    return _confidence(data)


def _signals_for_layer(data: RecursiveWorldModelInput, layer: WorldModelLayer) -> tuple[str, ...]:
    signals: list[str] = []
    if layer == WorldModelLayer.FORECASTING and data.scenario_forecast is not None:
        signals.append(data.scenario_forecast.decision.value)
    if layer == WorldModelLayer.DYNAMICS and data.multi_timeline is not None:
        signals.append(data.multi_timeline.decision.value)
    if layer == WorldModelLayer.ORCHESTRATION and data.global_orchestrator is not None:
        signals.append(data.global_orchestrator.decision.value)
    if layer == WorldModelLayer.META_COGNITION and data.cognitive_adaptation is not None:
        signals.append(_get(data.cognitive_adaptation, "load_level", "UNKNOWN").value)
    return tuple(signals)


def _prediction_risks(link: WorldModelCausalLink, impact: int, confidence: int) -> tuple[WorldModelRisk, ...]:
    risks: list[WorldModelRisk] = []
    if impact >= 65 and confidence < 50:
        risks.append(WorldModelRisk.CAUSAL_CONTRADICTION)
    if link.target == WorldModelLayer.ACTION and impact >= 55:
        risks.append(WorldModelRisk.PLANNING_ACTION_MISMATCH)
    if link.target == WorldModelLayer.SAFETY and impact >= 55:
        risks.append(WorldModelRisk.ORCHESTRATION_DESYNC)
    return tuple(risks)


def _state_drift(data: RecursiveWorldModelInput) -> bool:
    return data.strategic_timeline_analysis is not None and (
        _get(data.strategic_timeline_analysis, "degradation_detected", False)
        or StrategicDriftSignal.STRATEGIC_DEGRADATION in _get(data.strategic_timeline_analysis, "drift_signals", ())
    )


def _planning_action_mismatch(data: RecursiveWorldModelInput) -> bool:
    if data.long_horizon_plan is None or data.multi_timeline is None:
        return False
    planning_decision = _get(data.long_horizon_plan, "decision", None)
    return planning_decision is not None and "PROCEED" in planning_decision.value and data.multi_timeline.decision in {
        TimelineDecision.ENTER_TIMELINE_SAFE_MODE,
        TimelineDecision.REQUIRE_HUMAN_REVIEW,
    }


def _forecast_reality_gap(data: RecursiveWorldModelInput) -> bool:
    return (
        data.scenario_forecast is not None
        and data.multi_timeline is not None
        and data.scenario_forecast.decision == ForecastDecision.CONTINUE_CURRENT_PATH
        and data.multi_timeline.decision in {TimelineDecision.ENTER_TIMELINE_SAFE_MODE, TimelineDecision.REQUIRE_HUMAN_REVIEW}
    )


def _orchestration_desync(data: RecursiveWorldModelInput) -> bool:
    if data.global_orchestrator is not None:
        if data.global_orchestrator.decision == OrchestratorDecision.CONTINUE_COORDINATED_OPERATION and _safety_score(data) < 45:
            return True
        if data.global_orchestrator.system_state.mode in {OrchestratorMode.EMERGENCY_ORCHESTRATION, OrchestratorMode.SURVIVAL_ORCHESTRATION} and _forecasting_score(data) > 65:
            return True
    if data.coordination_result is not None and OrchestratorRisk.EXECUTION_DESYNCHRONIZATION in _get(data.coordination_result.state, "risks", ()):
        return True
    return False


def _governance_misaligned(data: RecursiveWorldModelInput) -> bool:
    return data.intent_alignment is not None and data.intent_alignment.mode in {IntentAlignmentMode.MISALIGNED, IntentAlignmentMode.CRITICAL_REALIGNMENT}


def _safety_failure(data: RecursiveWorldModelInput) -> bool:
    return (
        data.system_integrity is not None and data.system_integrity.status == SystemIntegrityStatus.COMPROMISED
    ) or (
        data.strategic_arbitration is not None and data.strategic_arbitration.decision == ArbitrationDecision.EMERGENCY_LOCKDOWN
    )


def _recursive_feedback_loop(data: RecursiveWorldModelInput) -> bool:
    return (
        data.strategy_evolution is not None
        and data.strategy_evolution.mode in {StrategyEvolutionMode.REBUILD_STRATEGY, StrategyEvolutionMode.SAFE_ROLLBACK}
        and data.multi_timeline is not None
        and data.multi_timeline.decision in {TimelineDecision.REBUILD_TIMELINE_SET, TimelineDecision.ENTER_TIMELINE_SAFE_MODE}
    )


def _overall_coherence(score: WorldModelCoherenceScore) -> int:
    values = [
        score.perception_score,
        score.state_memory_score,
        score.dynamics_score,
        score.planning_score,
        score.action_score,
        score.governance_score,
        score.safety_score,
        score.meta_cognition_score,
        score.forecasting_score,
        score.orchestration_score,
        score.causal_consistency_score,
    ]
    return _avg(values, 50)


def _evidence_count(data: RecursiveWorldModelInput) -> int:
    return sum(
        value is not None
        for value in (
            data.multi_timeline,
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


def _confidence(data: RecursiveWorldModelInput) -> int:
    values = []
    if data.scenario_forecast is not None:
        values.append(data.scenario_forecast.stability_breakdown.confidence_score)
    if data.multi_timeline is not None:
        values.append(data.multi_timeline.overall_survivability_score)
    if data.global_orchestrator is not None:
        values.append(data.global_orchestrator.confidence_score)
    if data.cognitive_adaptation is not None:
        values.append(_get(data.cognitive_adaptation, "global_score", 65))
    return _avg(values, 45 if _evidence_count(data) < 2 else 65)


def _status(score: int) -> str:
    if score >= 75:
        return "stable"
    if score >= 55:
        return "monitored"
    if score >= 35:
        return "unstable"
    return "critical"


def _avg(values: list[int], default: int) -> int:
    if not values:
        return default
    return _clamp(sum(values) / len(values))


def _get(obj: Any, name: str, default: Any = None) -> Any:
    return getattr(obj, name, default) if obj is not None else default


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _clamp(value: float, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(round(value))))


__all__ = [
    "build_world_model_graph",
    "compute_world_model_coherence",
    "decide_world_model_action",
    "detect_world_model_risks",
    "evaluate_recursive_world_model",
    "evaluate_world_model_state",
    "generate_world_model_recommendations",
    "render_recursive_world_model_markdown",
    "simulate_causal_impacts",
]
