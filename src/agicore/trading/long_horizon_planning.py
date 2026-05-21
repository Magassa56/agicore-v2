"""Offline Autonomous Long-Horizon Planning Engine for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .behavioral_stability_models import BehavioralPressureLevel, BehavioralRecoveryState
from .collective_consensus_models import ConsensusDecision, ConsensusMode
from .global_orchestrator_models import OrchestratorDecision, OrchestratorMode, OrchestratorRisk
from .intent_alignment_models import IntentAlignmentMode
from .long_horizon_planning_models import (
    FutureProjection,
    FutureScenario,
    FutureScenarioType,
    HorizonPlanGraph,
    LongHorizonPlanningInput,
    LongHorizonPlanningResult,
    PlanningDecision,
    PlanningEvent,
    PlanningHorizon,
    PlanningRecommendation,
    PlanningRisk,
    StrategicTrajectory,
)
from .mission_continuity_models import MissionContinuityMode
from .operational_awareness_models import OperationalHealthStatus
from .recovery_resilience_models import RecoveryMode
from .reward_models import RewardLabel
from .strategic_arbitration_models import ArbitrationDecision, ArbitrationMode
from .strategic_memory_models import StrategicDriftSignal
from .strategic_planning_models import StrategicObjective, StrategicPlanStatus
from .system_integrity_models import SystemIntegrityStatus
from .tactical_execution_models import TacticalExecutionQuality


def build_future_scenarios(
    planning_input: LongHorizonPlanningInput | None = None,
    **kwargs,
) -> tuple[FutureScenario, ...]:
    """Generate plausible future scenarios from current offline evidence."""
    data = _input(planning_input, **kwargs)
    horizon = data.horizon
    scenarios: list[FutureScenario] = []
    health = _system_health(data)
    stability = _strategic_stability(data)
    behavior = _behavior_score(data)

    if health >= 70 and stability >= 70 and behavior >= 70:
        scenarios.append(FutureScenario(FutureScenarioType.STABLE_GROWTH, 70, 55, horizon, "Stable operating context supports controlled growth.", "controlled_growth"))
    if _recovery_needed(data):
        scenarios.append(FutureScenario(FutureScenarioType.CONTROLLED_RECOVERY, 75, 70, horizon, "Recovery path is plausible if risk is reduced.", "recovery"))
    if _drawdown_risk(data) >= 65:
        scenarios.append(FutureScenario(FutureScenarioType.DRAWDOWN_CONTINUATION, 70, 80, horizon, "Current evidence points to continued drawdown pressure.", "capital_preservation"))
    if data.operational_awareness is not None and data.operational_awareness.health_status in {OperationalHealthStatus.CRITICAL, OperationalHealthStatus.COLLAPSING}:
        scenarios.append(FutureScenario(FutureScenarioType.VOLATILITY_SPIKE, 60, 75, horizon, "Operational stress can amplify volatility-sensitive decisions.", "reduce_risk"))
    if data.behavioral_stability is not None and data.behavioral_stability.pressure_level in {BehavioralPressureLevel.HIGH, BehavioralPressureLevel.EXTREME}:
        scenarios.append(FutureScenario(FutureScenarioType.BEHAVIORAL_DEGRADATION, 75, 80, horizon, "Behavioral pressure can degrade future execution quality.", "behavior_guards"))
    if data.strategic_timeline_analysis is not None and data.strategic_timeline_analysis.degradation_detected:
        scenarios.append(FutureScenario(FutureScenarioType.STRATEGIC_DRIFT, 70, 75, horizon, "Strategic timeline already shows degradation.", "recalibrate_strategy"))
    if data.system_integrity is not None and data.system_integrity.status != SystemIntegrityStatus.HEALTHY:
        scenarios.append(FutureScenario(FutureScenarioType.SYSTEM_INSTABILITY, 70, 85, horizon, "System integrity is below healthy state.", "safe_mode"))
    if _safe_mode_needed(data):
        scenarios.append(FutureScenario(FutureScenarioType.SAFE_MODE_REQUIRED, 80, 90, horizon, "Multiple layers indicate safe mode or execution limits.", "safe_mode"))
    if _learning_improving(data):
        scenarios.append(FutureScenario(FutureScenarioType.LEARNING_IMPROVEMENT, 60, 50, horizon, "Learning conditions may improve if evidence remains stable.", "observe_and_learn"))
    if data.mission_continuity is not None and data.mission_continuity.mode != MissionContinuityMode.FULL_OPERATION:
        scenarios.append(FutureScenario(FutureScenarioType.MISSION_CONTINUITY_RISK, 65, 80, horizon, "Mission continuity is constrained.", "continuity_first"))

    if not scenarios:
        scenarios.append(FutureScenario(FutureScenarioType.STABLE_GROWTH, 55, 45, horizon, "Neutral baseline projection with limited evidence.", "observe"))
    return tuple(dict.fromkeys(scenarios))


def project_strategic_trajectory(
    planning_input: LongHorizonPlanningInput | None = None,
    *,
    scenarios: tuple[FutureScenario, ...] | None = None,
    **kwargs,
) -> StrategicTrajectory:
    """Project the strategic phase sequence across the selected horizon."""
    data = _input(planning_input, **kwargs)
    resolved_scenarios = scenarios or build_future_scenarios(data)
    scenario_types = {scenario.scenario_type for scenario in resolved_scenarios}
    if FutureScenarioType.SAFE_MODE_REQUIRED in scenario_types or FutureScenarioType.SYSTEM_INSTABILITY in scenario_types:
        label = "defensive_stabilization"
        phases = ("safe_mode", "integrity_check", "reduced_risk", "review")
    elif FutureScenarioType.CONTROLLED_RECOVERY in scenario_types or FutureScenarioType.DRAWDOWN_CONTINUATION in scenario_types:
        label = "multi_phase_recovery"
        phases = ("capital_preservation", "recovery", "consistency_building", "controlled_reentry")
    elif FutureScenarioType.STABLE_GROWTH in scenario_types:
        label = "controlled_growth"
        phases = ("observe", "controlled_growth", "policy_validation", "scale_slowly")
    else:
        label = "observation_path"
        phases = ("observe", "collect_evidence", "review", "decide")
    current = _current_phase(data)
    target = phases[-1]
    trend = "improving" if _learning_improving(data) and _system_health(data) >= 65 else "degrading" if _future_danger_count(resolved_scenarios) >= 2 else "stable"
    return StrategicTrajectory(label, current, target, phases, trend, _expected_sessions(data.horizon, label), _trajectory_notes(data, resolved_scenarios))


def evaluate_long_horizon_risks(
    planning_input: LongHorizonPlanningInput | None = None,
    *,
    scenarios: tuple[FutureScenario, ...] | None = None,
    projection: FutureProjection | None = None,
    **kwargs,
) -> tuple[PlanningRisk, ...]:
    """Evaluate risks projected over the selected horizon."""
    data = _input(planning_input, **kwargs)
    resolved_scenarios = scenarios or build_future_scenarios(data)
    resolved_projection = projection or _projection(data, resolved_scenarios)
    scenario_types = {scenario.scenario_type for scenario in resolved_scenarios}
    risks: list[PlanningRisk] = []

    if FutureScenarioType.DRAWDOWN_CONTINUATION in scenario_types or resolved_projection.projected_drawdown_risk_score >= 65:
        risks.append(PlanningRisk.FUTURE_DRAWDOWN_RISK)
    if FutureScenarioType.STRATEGIC_DRIFT in scenario_types:
        risks.append(PlanningRisk.STRATEGIC_DRIFT_RISK)
    if FutureScenarioType.BEHAVIORAL_DEGRADATION in scenario_types or resolved_projection.projected_behavior_score < 55:
        risks.append(PlanningRisk.BEHAVIORAL_REGRESSION_RISK)
    if FutureScenarioType.SYSTEM_INSTABILITY in scenario_types or resolved_projection.projected_system_health_score < 55:
        risks.append(PlanningRisk.SYSTEM_INSTABILITY_RISK)
    if _learning_overadapting(data):
        risks.append(PlanningRisk.LEARNING_OVERADAPTATION_RISK)
    if resolved_projection.projection_confidence < 55:
        risks.append(PlanningRisk.LOW_CONFIDENCE_PROJECTION)
    if data.intent_alignment is not None and data.intent_alignment.mode not in {IntentAlignmentMode.FULLY_ALIGNED, IntentAlignmentMode.STABLE_ALIGNMENT}:
        risks.append(PlanningRisk.MISSION_DEVIATION_RISK)
    if FutureScenarioType.CONTROLLED_RECOVERY in scenario_types and resolved_projection.projected_recovery_score < 55:
        risks.append(PlanningRisk.RECOVERY_FAILURE_RISK)
    if data.tactical_execution is not None and data.tactical_execution.quality in {TacticalExecutionQuality.WEAK, TacticalExecutionQuality.DANGEROUS, TacticalExecutionQuality.BLOCKED}:
        risks.append(PlanningRisk.EXECUTION_QUALITY_DECAY)
    if FutureScenarioType.MISSION_CONTINUITY_RISK in scenario_types:
        risks.append(PlanningRisk.CONTINUITY_BREAKDOWN_RISK)
    return tuple(dict.fromkeys(risks))


def build_horizon_plan_graph(
    planning_input: LongHorizonPlanningInput | None = None,
    *,
    scenarios: tuple[FutureScenario, ...] | None = None,
    trajectory: StrategicTrajectory | None = None,
    risks: tuple[PlanningRisk, ...] | None = None,
    **kwargs,
) -> HorizonPlanGraph:
    """Build an explainable graph linking scenarios, phases and controls."""
    data = _input(planning_input, **kwargs)
    resolved_scenarios = scenarios or build_future_scenarios(data)
    resolved_trajectory = trajectory or project_strategic_trajectory(data, scenarios=resolved_scenarios)
    resolved_risks = risks or evaluate_long_horizon_risks(data, scenarios=resolved_scenarios)
    scenario_nodes = tuple(f"scenario:{scenario.scenario_type.value}" for scenario in resolved_scenarios)
    phase_nodes = tuple(f"phase:{phase}" for phase in resolved_trajectory.phase_sequence)
    risk_nodes = tuple(f"risk:{risk.value}" for risk in resolved_risks)
    nodes = scenario_nodes + phase_nodes + risk_nodes
    edges: list[tuple[str, str, str]] = []
    for scenario in scenario_nodes:
        edges.append(("current_state", scenario, "projects"))
    for left, right in zip(phase_nodes, phase_nodes[1:]):
        edges.append((left, right, "then"))
    for risk in risk_nodes:
        edges.append((risk, phase_nodes[0] if phase_nodes else "current_state", "constrains"))
    blocked = tuple(node for node in scenario_nodes if any(word in node for word in ("DRAWDOWN", "INSTABILITY", "SAFE_MODE", "DEGRADATION")))
    return HorizonPlanGraph(data.horizon, ("current_state",) + nodes, tuple(edges), phase_nodes or ("current_state",), blocked)


def decide_long_horizon_plan(
    planning_input: LongHorizonPlanningInput | None = None,
    *,
    risks: tuple[PlanningRisk, ...] | None = None,
    projection: FutureProjection | None = None,
    scenarios: tuple[FutureScenario, ...] | None = None,
    **kwargs,
) -> PlanningDecision:
    """Decide the long-horizon plan from projected risks and confidence."""
    data = _input(planning_input, **kwargs)
    resolved_scenarios = scenarios or build_future_scenarios(data)
    resolved_projection = projection or _projection(data, resolved_scenarios)
    resolved_risks = risks or evaluate_long_horizon_risks(data, scenarios=resolved_scenarios, projection=resolved_projection)
    dangerous_count = len({PlanningRisk.FUTURE_DRAWDOWN_RISK, PlanningRisk.SYSTEM_INSTABILITY_RISK, PlanningRisk.MISSION_DEVIATION_RISK, PlanningRisk.CONTINUITY_BREAKDOWN_RISK}.intersection(resolved_risks))
    if dangerous_count >= 3 or FutureScenarioType.SAFE_MODE_REQUIRED in {scenario.scenario_type for scenario in resolved_scenarios} and dangerous_count >= 2:
        return PlanningDecision.ENTER_LONG_HORIZON_SAFE_MODE
    if PlanningRisk.LOW_CONFIDENCE_PROJECTION in resolved_risks:
        return PlanningDecision.OBSERVE_BEFORE_ACTION
    if PlanningRisk.RECOVERY_FAILURE_RISK in resolved_risks or PlanningRisk.FUTURE_DRAWDOWN_RISK in resolved_risks:
        return PlanningDecision.PRIORITIZE_RECOVERY
    if PlanningRisk.SYSTEM_INSTABILITY_RISK in resolved_risks or PlanningRisk.BEHAVIORAL_REGRESSION_RISK in resolved_risks:
        return PlanningDecision.PRIORITIZE_STABILITY
    if PlanningRisk.STRATEGIC_DRIFT_RISK in resolved_risks or PlanningRisk.MISSION_DEVIATION_RISK in resolved_risks:
        return PlanningDecision.REBUILD_PLAN
    if resolved_projection.projection_confidence < 65:
        return PlanningDecision.REDUCE_RISK_PLAN
    return PlanningDecision.PROCEED_WITH_PLAN


def compute_projection_confidence(
    planning_input: LongHorizonPlanningInput | None = None,
    *,
    scenarios: tuple[FutureScenario, ...] | None = None,
    **kwargs,
) -> int:
    """Compute projection confidence from 0..100."""
    data = _input(planning_input, **kwargs)
    resolved_scenarios = scenarios or build_future_scenarios(data)
    scores = _available_scores(data)
    confidence = int(round(sum(scores) / len(scores))) if scores else 60
    confidence -= min(25, _future_danger_count(resolved_scenarios) * 4)
    if data.strategic_timeline_analysis is None:
        confidence -= 8
    if data.reward_evaluation is None:
        confidence -= 4
    return _clamp(confidence)


def generate_long_horizon_recommendations(
    planning_input: LongHorizonPlanningInput | None = None,
    *,
    decision: PlanningDecision | None = None,
    risks: tuple[PlanningRisk, ...] | None = None,
    scenarios: tuple[FutureScenario, ...] | None = None,
    **kwargs,
) -> tuple[PlanningRecommendation, ...]:
    """Generate ordered long-horizon recommendations."""
    data = _input(planning_input, **kwargs)
    resolved_scenarios = scenarios or build_future_scenarios(data)
    projection = _projection(data, resolved_scenarios)
    resolved_risks = risks or evaluate_long_horizon_risks(data, scenarios=resolved_scenarios, projection=projection)
    resolved_decision = decision or decide_long_horizon_plan(data, risks=resolved_risks, projection=projection, scenarios=resolved_scenarios)
    recommendations: list[PlanningRecommendation] = []

    if resolved_decision in {PlanningDecision.ENTER_LONG_HORIZON_SAFE_MODE, PlanningDecision.PRIORITIZE_STABILITY}:
        recommendations.append(PlanningRecommendation.PRIORITIZE_CAPITAL_PRESERVATION)
        recommendations.append(PlanningRecommendation.RECHECK_SYSTEM_INTEGRITY)
    scenario_types = {scenario.scenario_type for scenario in resolved_scenarios}
    if resolved_decision == PlanningDecision.PRIORITIZE_RECOVERY or FutureScenarioType.CONTROLLED_RECOVERY in scenario_types or FutureScenarioType.DRAWDOWN_CONTINUATION in scenario_types:
        recommendations.append(PlanningRecommendation.PREPARE_RECOVERY_SEQUENCE)
        recommendations.append(PlanningRecommendation.LIMIT_TRADES_NEXT_SESSION)
    if PlanningRisk.BEHAVIORAL_REGRESSION_RISK in resolved_risks:
        recommendations.append(PlanningRecommendation.STRENGTHEN_BEHAVIORAL_GUARDS)
    if PlanningRisk.LEARNING_OVERADAPTATION_RISK in resolved_risks or PlanningRisk.STRATEGIC_DRIFT_RISK in resolved_risks:
        recommendations.append(PlanningRecommendation.FREEZE_POLICY_EXPANSION)
    if PlanningRisk.LOW_CONFIDENCE_PROJECTION in resolved_risks or resolved_decision == PlanningDecision.OBSERVE_BEFORE_ACTION:
        recommendations.append(PlanningRecommendation.INCREASE_OBSERVATION_WINDOW)
    if resolved_decision == PlanningDecision.PROCEED_WITH_PLAN:
        recommendations.append(PlanningRecommendation.CONTINUE_CONTROLLED_GROWTH)
        recommendations.append(PlanningRecommendation.MAINTAIN_CURRENT_TRAJECTORY)
    recommendations.append(PlanningRecommendation.UPDATE_STRATEGIC_MEMORY)
    return tuple(dict.fromkeys(recommendations))


def render_long_horizon_planning_markdown(result: LongHorizonPlanningResult) -> str:
    """Render long-horizon planning result as Markdown."""
    lines = [
        "# Autonomous Long-Horizon Planning Engine",
        "",
        "## Long-Horizon Planning State",
        "",
        f"- Decision: {result.decision.value}",
        f"- Confidence: {result.projection_confidence}/100",
        "",
        "## Planning Horizon",
        "",
        f"- {result.horizon.value}",
        "",
        "## Future Scenarios",
        "",
        *_bullet_lines(tuple(f"{scenario.scenario_type.value}: p={scenario.probability_score}, impact={scenario.impact_score}" for scenario in result.scenarios)),
        "",
        "## Strategic Trajectory",
        "",
        f"- {result.trajectory.trajectory_label}",
        *_bullet_lines(result.trajectory.phase_sequence),
        "",
        "## Risks",
        "",
        *_bullet_lines(tuple(risk.value for risk in result.risks)),
        "",
        "## Plan Graph",
        "",
        *_bullet_lines(tuple(f"{source} -> {target} [{relation}]" for source, target, relation in result.plan_graph.edges)),
        "",
        "## Decision",
        "",
        f"- {result.decision.value}",
        "",
        "## Recommendations",
        "",
        *_bullet_lines(tuple(recommendation.value for recommendation in result.recommendations)),
        "",
        "## AGIcore Future Outlook",
        "",
        f"- {result.summary}",
        "- Offline only: no broker, no real order, no external API, no external ML, no external LLM, no neural training, no live execution.",
        "",
    ]
    return "\n".join(lines)


def plan_long_horizon(
    planning_input: LongHorizonPlanningInput | None = None,
    **kwargs,
) -> LongHorizonPlanningResult:
    """Run the full offline long-horizon planning pipeline."""
    data = _input(planning_input, **kwargs)
    scenarios = build_future_scenarios(data)
    projection = _projection(data, scenarios)
    trajectory = project_strategic_trajectory(data, scenarios=scenarios)
    risks = evaluate_long_horizon_risks(data, scenarios=scenarios, projection=projection)
    graph = build_horizon_plan_graph(data, scenarios=scenarios, trajectory=trajectory, risks=risks)
    decision = decide_long_horizon_plan(data, risks=risks, projection=projection, scenarios=scenarios)
    recommendations = generate_long_horizon_recommendations(data, decision=decision, risks=risks, scenarios=scenarios)
    event = PlanningEvent(decision, data.horizon, f"Long-horizon plan selected {decision.value}.", datetime.now(UTC))
    return LongHorizonPlanningResult(
        data.horizon,
        decision,
        projection.projection_confidence,
        scenarios,
        projection,
        trajectory,
        risks,
        graph,
        recommendations,
        (event,),
        f"{trajectory.trajectory_label} over {data.horizon.value} with {len(risks)} projected risk(s).",
    )


def _projection(data: LongHorizonPlanningInput, scenarios: tuple[FutureScenario, ...]) -> FutureProjection:
    stability = _strategic_stability(data)
    drawdown = _drawdown_risk(data)
    recovery = _recovery_score(data)
    behavior = _behavior_score(data)
    health = _system_health(data)
    danger = _future_danger_count(scenarios)
    return FutureProjection(
        data.horizon,
        _clamp(stability - danger * 3),
        _clamp(drawdown + danger * 4),
        _clamp(recovery - max(0, drawdown - 60) // 4),
        _clamp(behavior - danger * 3),
        _clamp(health - danger * 4),
        compute_projection_confidence(data, scenarios=scenarios),
    )


def _system_health(data: LongHorizonPlanningInput) -> int:
    if data.health_snapshot is not None:
        return data.health_snapshot.orchestration_confidence
    if data.global_orchestrator is not None:
        return data.global_orchestrator.confidence_score
    if data.system_integrity is not None:
        return data.system_integrity.integrity_score
    return 70


def _strategic_stability(data: LongHorizonPlanningInput) -> int:
    if data.strategic_timeline_analysis is not None:
        return data.strategic_timeline_analysis.strategic_health_score
    if data.strategic_result is not None:
        return data.strategic_result.progress_score
    return 70


def _behavior_score(data: LongHorizonPlanningInput) -> int:
    if data.behavioral_stability is not None:
        return data.behavioral_stability.stability_score
    return 70


def _recovery_score(data: LongHorizonPlanningInput) -> int:
    if data.recovery_resilience is not None:
        return data.recovery_resilience.resilience_score
    if data.strategic_timeline_analysis is not None and data.strategic_timeline_analysis.improvement_detected:
        return 75
    return 65


def _drawdown_risk(data: LongHorizonPlanningInput) -> int:
    risk = 35
    if data.strategic_timeline_analysis is not None:
        if StrategicDriftSignal.PERSISTENT_DRAWDOWN in data.strategic_timeline_analysis.drift_signals:
            risk += 35
        if data.strategic_timeline_analysis.degradation_detected:
            risk += 15
    if data.reward_evaluation is not None and data.reward_evaluation.reward_label in {RewardLabel.BAD_DECISION, RewardLabel.DANGEROUS_DECISION}:
        risk += 20
    return _clamp(risk)


def _recovery_needed(data: LongHorizonPlanningInput) -> bool:
    return (
        (data.recovery_resilience is not None and data.recovery_resilience.mode != RecoveryMode.NORMAL)
        or (data.strategic_result is not None and data.strategic_result.plan.status in {StrategicPlanStatus.RECOVERY, StrategicPlanStatus.DEFENSIVE})
        or _drawdown_risk(data) >= 65
    )


def _safe_mode_needed(data: LongHorizonPlanningInput) -> bool:
    return (
        (data.global_orchestrator is not None and data.global_orchestrator.decision in {OrchestratorDecision.ENTER_SAFE_GLOBAL_MODE, OrchestratorDecision.ACTIVATE_SURVIVAL_MODE, OrchestratorDecision.EMERGENCY_HALT_ROUTING})
        or (data.coordination_result is not None and OrchestratorRisk.GLOBAL_SAFE_MODE_REQUIRED in data.coordination_result.state.risks)
        or (data.strategic_arbitration is not None and data.strategic_arbitration.decision in {ArbitrationDecision.EMERGENCY_LOCKDOWN, ArbitrationDecision.ENABLE_SAFE_MODE, ArbitrationDecision.STOP_EXECUTION})
        or (data.collective_consensus is not None and data.collective_consensus.decision in {ConsensusDecision.EMERGENCY_HALT, ConsensusDecision.ENTER_SAFE_MODE, ConsensusDecision.BLOCK_COLLECTIVE_ACTION})
    )


def _learning_improving(data: LongHorizonPlanningInput) -> bool:
    return (
        data.strategic_timeline_analysis is not None
        and data.strategic_timeline_analysis.improvement_detected
        and data.reward_evaluation is not None
        and data.reward_evaluation.reward_label in {RewardLabel.EXCELLENT_DECISION, RewardLabel.GOOD_DECISION}
    )


def _learning_overadapting(data: LongHorizonPlanningInput) -> bool:
    return data.strategic_result is not None and data.strategic_result.plan.primary_objective in {StrategicObjective.POLICY_VALIDATION, StrategicObjective.LEARNING_PHASE} and _system_health(data) < 60


def _current_phase(data: LongHorizonPlanningInput) -> str:
    if data.global_orchestrator is not None:
        return data.global_orchestrator.system_state.mode.value.lower()
    if data.recovery_resilience is not None:
        return data.recovery_resilience.mode.value.lower()
    return "current_state"


def _expected_sessions(horizon: PlanningHorizon, label: str) -> int:
    base = {
        PlanningHorizon.NEXT_SESSION: 1,
        PlanningHorizon.DAILY: 2,
        PlanningHorizon.WEEKLY: 5,
        PlanningHorizon.EVALUATION_CHALLENGE: 20,
        PlanningHorizon.MULTI_PHASE_RECOVERY: 10,
        PlanningHorizon.LONG_TERM_GROWTH: 30,
    }[horizon]
    return base + (3 if label == "multi_phase_recovery" else 0)


def _trajectory_notes(data: LongHorizonPlanningInput, scenarios: tuple[FutureScenario, ...]) -> tuple[str, ...]:
    notes = [f"{len(scenarios)} future scenario(s) projected"]
    if data.strategic_timeline_analysis is None:
        notes.append("strategic timeline absent; confidence reduced")
    if _safe_mode_needed(data):
        notes.append("safe mode constraints active")
    return tuple(notes)


def _future_danger_count(scenarios: tuple[FutureScenario, ...]) -> int:
    dangerous = {
        FutureScenarioType.DRAWDOWN_CONTINUATION,
        FutureScenarioType.BEHAVIORAL_DEGRADATION,
        FutureScenarioType.STRATEGIC_DRIFT,
        FutureScenarioType.SYSTEM_INSTABILITY,
        FutureScenarioType.SAFE_MODE_REQUIRED,
        FutureScenarioType.MISSION_CONTINUITY_RISK,
    }
    return sum(1 for scenario in scenarios if scenario.scenario_type in dangerous)


def _available_scores(data: LongHorizonPlanningInput) -> tuple[int, ...]:
    scores: list[int] = []
    for value in (
        data.global_orchestrator.confidence_score if data.global_orchestrator is not None else None,
        data.health_snapshot.orchestration_confidence if data.health_snapshot is not None else None,
        data.strategic_result.progress_score if data.strategic_result is not None else None,
        data.strategic_timeline_analysis.strategic_health_score if data.strategic_timeline_analysis is not None else None,
        data.operational_awareness.operational_confidence_score if data.operational_awareness is not None else None,
        data.mission_continuity.continuity_score if data.mission_continuity is not None else None,
        data.recovery_resilience.resilience_score if data.recovery_resilience is not None else None,
        data.system_integrity.integrity_score if data.system_integrity is not None else None,
        data.intent_alignment.alignment_confidence if data.intent_alignment is not None else None,
        data.collective_consensus.collective_confidence_score if data.collective_consensus is not None else None,
        data.behavioral_stability.stability_score if data.behavioral_stability is not None else None,
        data.reward_evaluation.normalized_reward if data.reward_evaluation is not None else None,
    ):
        if value is not None:
            scores.append(value)
    return tuple(scores)


def _input(planning_input: LongHorizonPlanningInput | None = None, **kwargs: Any) -> LongHorizonPlanningInput:
    if planning_input is not None:
        return planning_input
    return LongHorizonPlanningInput(**kwargs)


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _clamp(value: int | float) -> int:
    return max(0, min(100, int(round(value))))


__all__ = [
    "build_future_scenarios",
    "build_horizon_plan_graph",
    "compute_projection_confidence",
    "decide_long_horizon_plan",
    "evaluate_long_horizon_risks",
    "generate_long_horizon_recommendations",
    "plan_long_horizon",
    "project_strategic_trajectory",
    "render_long_horizon_planning_markdown",
]
