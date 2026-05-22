"""Offline Autonomous Adaptive Strategy Evolution Engine for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime

from .behavioral_stability_models import BehavioralPressureLevel
from .collective_consensus_models import ConsensusDecision
from .intent_alignment_models import IntentAlignmentMode
from .learning_governance_models import LearningGovernanceDecision, LearningGovernanceMode
from .long_horizon_planning_models import PlanningDecision, PlanningRisk
from .reward_models import RewardLabel
from .scenario_forecast_models import ForecastDecision, ForecastScenarioType
from .strategic_arbitration_models import ArbitrationDecision
from .strategy_evolution_models import (
    StrategyEvolutionDecision,
    StrategyEvolutionEvent,
    StrategyEvolutionInput,
    StrategyEvolutionMode,
    StrategyEvolutionRecommendation,
    StrategyEvolutionResult,
    StrategyEvolutionRisk,
    StrategyFitnessScore,
    StrategyGeneration,
    StrategyLineageGraph,
    StrategyMutation,
)
from .tactical_execution_models import TacticalExecutionQuality, TacticalExecutionSignal


def evaluate_strategy_evolution(
    evolution_input: StrategyEvolutionInput | None = None,
    **kwargs,
) -> StrategyEvolutionResult:
    """Evaluate controlled offline strategy evolution end to end."""
    data = _input(evolution_input, **kwargs)
    fitness_breakdown = compute_strategy_fitness(data)
    risks = detect_strategy_evolution_risks(data, fitness=fitness_breakdown)
    mutations = propose_strategy_mutations(data, risks=risks, fitness=fitness_breakdown)
    lineage = build_strategy_lineage_graph(data, fitness=fitness_breakdown, proposed_mutations=mutations)
    decision = decide_strategy_evolution(data, risks=risks, fitness=fitness_breakdown, proposed_mutations=mutations, lineage_graph=lineage)
    mode = _mode_for_decision(decision, risks, data)
    recommendations = generate_strategy_evolution_recommendations(data, decision=decision, risks=risks, proposed_mutations=mutations)
    current = _current_generation(data, fitness_breakdown, mutations)
    fitness_score = _overall_fitness(fitness_breakdown)
    event = StrategyEvolutionEvent(decision, mode, f"strategy evolution decision={decision.value}", datetime.now(UTC))
    return StrategyEvolutionResult(
        mode=mode,
        decision=decision,
        current_generation=current,
        fitness_score=fitness_score,
        fitness_breakdown=fitness_breakdown,
        proposed_mutations=mutations,
        risks=risks,
        lineage_graph=lineage,
        recommendations=recommendations,
        preserved_core_dna=current.preserved_core_dna and StrategyEvolutionRisk.LOSS_OF_CORE_DNA not in risks,
        events=(event,),
        summary=f"{mode.value}: {decision.value} with fitness {fitness_score}/100",
    )


def detect_strategy_evolution_risks(
    evolution_input: StrategyEvolutionInput | None = None,
    *,
    fitness: StrategyFitnessScore | None = None,
    **kwargs,
) -> tuple[StrategyEvolutionRisk, ...]:
    """Detect risks before any strategy mutation is allowed offline."""
    data = _input(evolution_input, **kwargs)
    resolved_fitness = fitness or compute_strategy_fitness(data)
    risks: list[StrategyEvolutionRisk] = []

    if _strategy_drift(data):
        risks.append(StrategyEvolutionRisk.STRATEGY_DRIFT)
    if _mutation_count(data) >= 4:
        risks.append(StrategyEvolutionRisk.OVER_MUTATION)
    if resolved_fitness.performance_score < 45 or _fitness_degraded(data):
        risks.append(StrategyEvolutionRisk.FITNESS_DEGRADATION)
    if _behavior_unsafe(data):
        risks.append(StrategyEvolutionRisk.BEHAVIORAL_UNSAFE_EVOLUTION)
    if _alignment_weak(data):
        risks.append(StrategyEvolutionRisk.ALIGNMENT_BREAK)
    if resolved_fitness.evidence_score < 45:
        risks.append(StrategyEvolutionRisk.LOW_EVIDENCE_EVOLUTION)
    if _reward_overfit(data):
        risks.append(StrategyEvolutionRisk.REWARD_OVERFIT)
    if _core_dna_at_risk(data):
        risks.append(StrategyEvolutionRisk.LOSS_OF_CORE_DNA)
    if resolved_fitness.lineage_stability_score < 45:
        risks.append(StrategyEvolutionRisk.UNSTABLE_LINEAGE)
    if _unsafe_policy_propagation(data):
        risks.append(StrategyEvolutionRisk.UNSAFE_POLICY_PROPAGATION)
    return tuple(dict.fromkeys(risks))


def compute_strategy_fitness(
    evolution_input: StrategyEvolutionInput | None = None,
    **kwargs,
) -> StrategyFitnessScore:
    """Compute deterministic offline strategy fitness components."""
    data = _input(evolution_input, **kwargs)
    performance = _performance_score(data)
    risk_control = _risk_control_score(data)
    dna = _dna_preservation_score(data)
    behavior = _behavioral_safety_score(data)
    alignment = _alignment_score(data)
    evidence = _evidence_score(data)
    lineage = _lineage_stability_score(data)
    return StrategyFitnessScore(performance, risk_control, dna, behavior, alignment, evidence, lineage)


def propose_strategy_mutations(
    evolution_input: StrategyEvolutionInput | None = None,
    *,
    risks: tuple[StrategyEvolutionRisk, ...] | None = None,
    fitness: StrategyFitnessScore | None = None,
    **kwargs,
) -> tuple[StrategyMutation, ...]:
    """Propose safe offline-only mutation candidates."""
    data = _input(evolution_input, **kwargs)
    resolved_risks = risks or detect_strategy_evolution_risks(data)
    resolved_fitness = fitness or compute_strategy_fitness(data)

    if _freeze_required(data) or StrategyEvolutionRisk.ALIGNMENT_BREAK in resolved_risks:
        return (StrategyMutation.NO_MUTATION,)

    mutations: list[StrategyMutation] = []
    if resolved_fitness.risk_control_score < 65 or StrategyEvolutionRisk.FITNESS_DEGRADATION in resolved_risks:
        mutations.append(StrategyMutation.RISK_REDUCTION_MUTATION)
        mutations.append(StrategyMutation.POSITION_SIZING_MUTATION)
    if _behavior_unsafe(data):
        mutations.append(StrategyMutation.BEHAVIOR_GUARD_MUTATION)
    if resolved_fitness.performance_score < 60 and StrategyEvolutionRisk.LOW_EVIDENCE_EVOLUTION not in resolved_risks:
        mutations.append(StrategyMutation.ENTRY_FILTER_MUTATION)
        mutations.append(StrategyMutation.EXIT_FILTER_MUTATION)
    if _forecast_safe_or_degraded(data):
        mutations.append(StrategyMutation.CONTEXT_FILTER_MUTATION)
        mutations.append(StrategyMutation.VOLATILITY_ADAPTATION_MUTATION)
    if _time_window_needed(data):
        mutations.append(StrategyMutation.TIME_WINDOW_MUTATION)
    if _policy_memory_weak(data):
        mutations.append(StrategyMutation.POLICY_SELECTION_MUTATION)

    if not mutations:
        return (StrategyMutation.NO_MUTATION,)
    return tuple(dict.fromkeys(mutations[:4]))


def build_strategy_lineage_graph(
    evolution_input: StrategyEvolutionInput | None = None,
    *,
    fitness: StrategyFitnessScore | None = None,
    proposed_mutations: tuple[StrategyMutation, ...] | None = None,
    **kwargs,
) -> StrategyLineageGraph:
    """Build an explainable lineage graph for current and previous generations."""
    data = _input(evolution_input, **kwargs)
    resolved_fitness = fitness or compute_strategy_fitness(data)
    current = _current_generation(data, resolved_fitness, proposed_mutations or ())
    generations = data.previous_generations + (current,)
    nodes = tuple(generation.generation_id for generation in generations)
    edges = tuple(
        (generation.parent_generation_id, generation.generation_id, ",".join(m.value for m in generation.mutations) or StrategyMutation.NO_MUTATION.value)
        for generation in generations
        if generation.parent_generation_id
    )
    stable = tuple(g.generation_id for g in generations if g.fitness_score >= 65 and g.preserved_core_dna)
    unstable = tuple(g.generation_id for g in generations if g.fitness_score < 50 or not g.preserved_core_dna)
    recommended_parent = stable[-1] if stable else (generations[0].generation_id if generations else None)
    return StrategyLineageGraph(nodes, edges, stable, unstable, current.generation_id, recommended_parent)


def decide_strategy_evolution(
    evolution_input: StrategyEvolutionInput | None = None,
    *,
    risks: tuple[StrategyEvolutionRisk, ...] | None = None,
    fitness: StrategyFitnessScore | None = None,
    proposed_mutations: tuple[StrategyMutation, ...] | None = None,
    lineage_graph: StrategyLineageGraph | None = None,
    **kwargs,
) -> StrategyEvolutionDecision:
    """Decide whether to preserve, mutate, freeze, rollback or rebuild."""
    data = _input(evolution_input, **kwargs)
    resolved_fitness = fitness or compute_strategy_fitness(data)
    resolved_risks = risks or detect_strategy_evolution_risks(data, fitness=resolved_fitness)
    resolved_mutations = proposed_mutations or propose_strategy_mutations(data, risks=resolved_risks, fitness=resolved_fitness)
    resolved_lineage = lineage_graph or build_strategy_lineage_graph(data, fitness=resolved_fitness, proposed_mutations=resolved_mutations)
    critical = {
        StrategyEvolutionRisk.ALIGNMENT_BREAK,
        StrategyEvolutionRisk.LOSS_OF_CORE_DNA,
        StrategyEvolutionRisk.UNSAFE_POLICY_PROPAGATION,
    }

    if _freeze_required(data):
        return StrategyEvolutionDecision.FREEZE_STRATEGY_EVOLUTION
    if len(critical.intersection(resolved_risks)) >= 2:
        return StrategyEvolutionDecision.REQUIRE_HUMAN_REVIEW
    if StrategyEvolutionRisk.UNSTABLE_LINEAGE in resolved_risks and resolved_lineage.stable_generations:
        return StrategyEvolutionDecision.ROLLBACK_TO_STABLE_GENERATION
    if resolved_fitness.evidence_score < 40:
        return StrategyEvolutionDecision.REQUIRE_MORE_EVIDENCE
    if _critical_risk_count(resolved_risks) >= 4 and not resolved_lineage.stable_generations:
        return StrategyEvolutionDecision.REBUILD_STRATEGY_FAMILY
    if StrategyMutation.NO_MUTATION not in resolved_mutations and resolved_fitness.risk_control_score >= 55:
        return StrategyEvolutionDecision.TEST_MUTATION_OFFLINE
    if resolved_fitness.performance_score < 55 or StrategyEvolutionRisk.FITNESS_DEGRADATION in resolved_risks:
        return StrategyEvolutionDecision.APPLY_CONTROLLED_MUTATION
    return StrategyEvolutionDecision.KEEP_CURRENT_STRATEGY


def generate_strategy_evolution_recommendations(
    evolution_input: StrategyEvolutionInput | None = None,
    *,
    decision: StrategyEvolutionDecision | None = None,
    risks: tuple[StrategyEvolutionRisk, ...] | None = None,
    proposed_mutations: tuple[StrategyMutation, ...] | None = None,
    **kwargs,
) -> tuple[StrategyEvolutionRecommendation, ...]:
    """Generate controls and validation steps for strategy evolution."""
    data = _input(evolution_input, **kwargs)
    resolved_risks = risks or detect_strategy_evolution_risks(data)
    resolved_mutations = proposed_mutations or propose_strategy_mutations(data, risks=resolved_risks)
    resolved_decision = decision or decide_strategy_evolution(data, risks=resolved_risks, proposed_mutations=resolved_mutations)
    recommendations: list[StrategyEvolutionRecommendation] = [StrategyEvolutionRecommendation.PRESERVE_STRATEGY_DNA]

    if resolved_decision in {StrategyEvolutionDecision.TEST_MUTATION_OFFLINE, StrategyEvolutionDecision.APPLY_CONTROLLED_MUTATION}:
        recommendations.append(StrategyEvolutionRecommendation.TEST_IN_REPLAY_ARENA)
        recommendations.append(StrategyEvolutionRecommendation.COMPARE_GENERATIONS)
    if StrategyEvolutionRisk.OVER_MUTATION in resolved_risks or len([m for m in resolved_mutations if m != StrategyMutation.NO_MUTATION]) > 2:
        recommendations.append(StrategyEvolutionRecommendation.REDUCE_MUTATION_SCOPE)
    if StrategyEvolutionRisk.LOW_EVIDENCE_EVOLUTION in resolved_risks:
        recommendations.append(StrategyEvolutionRecommendation.EXTEND_VALIDATION_WINDOW)
    if StrategyEvolutionRisk.UNSAFE_POLICY_PROPAGATION in resolved_risks or _freeze_required(data):
        recommendations.append(StrategyEvolutionRecommendation.FREEZE_POLICY_EXPANSION)
    if StrategyMutation.RISK_REDUCTION_MUTATION in resolved_mutations or StrategyMutation.POSITION_SIZING_MUTATION in resolved_mutations:
        recommendations.append(StrategyEvolutionRecommendation.APPLY_RISK_REDUCTION)
    if resolved_decision == StrategyEvolutionDecision.ROLLBACK_TO_STABLE_GENERATION:
        recommendations.append(StrategyEvolutionRecommendation.ROLLBACK_UNSTABLE_VARIANT)
    if resolved_decision == StrategyEvolutionDecision.KEEP_CURRENT_STRATEGY:
        recommendations.append(StrategyEvolutionRecommendation.CONTINUE_STABLE_STRATEGY)
    recommendations.append(StrategyEvolutionRecommendation.UPDATE_STRATEGY_MEMORY)
    return tuple(dict.fromkeys(recommendations))


def render_strategy_evolution_markdown(result: StrategyEvolutionResult) -> str:
    """Render strategy evolution result as Markdown."""
    lines = [
        "# Autonomous Adaptive Strategy Evolution Engine",
        "",
        "## Strategy Evolution State",
        "",
        f"- Mode: {result.mode.value}",
        f"- Decision: {result.decision.value}",
        f"- Core DNA preserved: {result.preserved_core_dna}",
        "",
        "## Current Generation",
        "",
        f"- ID: {result.current_generation.generation_id}",
        f"- Strategy: {result.current_generation.strategy_name}",
        f"- Version: {result.current_generation.version}",
        "",
        "## Fitness Score",
        "",
        f"- Overall: {result.fitness_score}/100",
        f"- Performance: {result.fitness_breakdown.performance_score}/100",
        f"- Risk control: {result.fitness_breakdown.risk_control_score}/100",
        f"- DNA preservation: {result.fitness_breakdown.dna_preservation_score}/100",
        f"- Behavioral safety: {result.fitness_breakdown.behavioral_safety_score}/100",
        f"- Alignment: {result.fitness_breakdown.alignment_score}/100",
        f"- Evidence: {result.fitness_breakdown.evidence_score}/100",
        f"- Lineage stability: {result.fitness_breakdown.lineage_stability_score}/100",
        "",
        "## Proposed Mutations",
        "",
        *_bullet_lines(tuple(mutation.value for mutation in result.proposed_mutations)),
        "",
        "## Evolution Risks",
        "",
        *_bullet_lines(tuple(risk.value for risk in result.risks)),
        "",
        "## Lineage Graph",
        "",
        *_bullet_lines(result.lineage_graph.nodes),
        *_bullet_lines(tuple(f"{source} -> {target}: {label}" for source, target, label in result.lineage_graph.edges)),
        "",
        "## Decision",
        "",
        f"- {result.decision.value}",
        "",
        "## Recommendations",
        "",
        *_bullet_lines(tuple(recommendation.value for recommendation in result.recommendations)),
        "",
        "## AGIcore Strategy Evolution Outlook",
        "",
        result.summary,
    ]
    return "\n".join(lines)


def _input(evolution_input: StrategyEvolutionInput | None = None, **kwargs) -> StrategyEvolutionInput:
    if evolution_input is not None and kwargs:
        raise ValueError("Pass either StrategyEvolutionInput or keyword inputs, not both")
    if evolution_input is not None:
        return evolution_input
    return StrategyEvolutionInput(**kwargs)


def _overall_fitness(score: StrategyFitnessScore) -> int:
    return _clamp(
        (
            score.performance_score
            + score.risk_control_score
            + score.dna_preservation_score
            + score.behavioral_safety_score
            + score.alignment_score
            + score.evidence_score
            + score.lineage_stability_score
        )
        / 7
    )


def _performance_score(data: StrategyEvolutionInput) -> int:
    scores: list[int] = []
    if data.reward_evaluation is not None:
        scores.append(data.reward_evaluation.normalized_reward)
    if data.tactical_execution is not None:
        scores.append(data.tactical_execution.global_score)
    if data.replay_arena is not None:
        scores.append(data.replay_arena.robustness_score)
    if data.scenario_forecast is not None:
        scores.append(data.scenario_forecast.forecast_stability_score)
    if data.long_horizon_plan is not None:
        scores.append(data.long_horizon_plan.projection.projected_stability_score)
    if data.policy_memory is not None and data.policy_memory.entries:
        scores.append(_clamp(sum(entry.average_reward for entry in data.policy_memory.entries.values()) / len(data.policy_memory.entries)))
    return _avg(scores, 65)


def _risk_control_score(data: StrategyEvolutionInput) -> int:
    score = 75
    if data.scenario_forecast is not None and data.scenario_forecast.decision in {ForecastDecision.ENTER_FORECAST_SAFE_MODE, ForecastDecision.AVOID_HIGH_RISK_SCENARIO}:
        score -= 25
    if data.long_horizon_plan is not None and data.long_horizon_plan.decision in {PlanningDecision.REDUCE_RISK_PLAN, PlanningDecision.ENTER_LONG_HORIZON_SAFE_MODE}:
        score -= 20
    if data.collective_consensus is not None and data.collective_consensus.decision in {ConsensusDecision.BLOCK_COLLECTIVE_ACTION, ConsensusDecision.EMERGENCY_HALT}:
        score -= 25
    if data.strategic_arbitration is not None and data.strategic_arbitration.decision in {ArbitrationDecision.EMERGENCY_LOCKDOWN, ArbitrationDecision.STOP_EXECUTION}:
        score -= 25
    if data.strategy_dna is not None and data.strategy_dna.risk_rules.risk_per_trade is not None and data.strategy_dna.risk_rules.risk_per_trade <= 1.0:
        score += 8
    return _clamp(score)


def _dna_preservation_score(data: StrategyEvolutionInput) -> int:
    score = 80
    if data.strategy_dna is None:
        score -= 20
    else:
        if not data.strategy_dna.entry_conditions:
            score -= 15
        if not data.strategy_dna.exit_conditions:
            score -= 10
        if data.strategy_dna.trend_filter is None and data.strategy_dna.ema_filter is None:
            score -= 10
    for generation in data.previous_generations:
        if not generation.preserved_core_dna:
            score -= 15
    return _clamp(score)


def _behavioral_safety_score(data: StrategyEvolutionInput) -> int:
    if data.behavioral_stability is None:
        return 65
    score = data.behavioral_stability.stability_score
    if data.behavioral_stability.pressure_level in {BehavioralPressureLevel.HIGH, BehavioralPressureLevel.EXTREME}:
        score -= 20
    return _clamp(score)


def _alignment_score(data: StrategyEvolutionInput) -> int:
    score = 75
    if data.intent_alignment is not None:
        score = data.intent_alignment.alignment_confidence
        if data.intent_alignment.mode not in {IntentAlignmentMode.FULLY_ALIGNED, IntentAlignmentMode.STABLE_ALIGNMENT}:
            score -= 20
    if data.learning_governance is not None and data.learning_governance.mode in {LearningGovernanceMode.FREEZE_LEARNING, LearningGovernanceMode.SAFETY_LOCKDOWN}:
        score -= 20
    return _clamp(score)


def _evidence_score(data: StrategyEvolutionInput) -> int:
    evidence = 0
    evidence += 15 if data.reward_evaluation is not None else 0
    evidence += 15 if data.tactical_execution is not None else 0
    evidence += 15 if data.replay_arena is not None else 0
    evidence += 15 if data.policy_memory is not None and data.policy_memory.entries else 0
    evidence += 10 if data.scenario_forecast is not None else 0
    evidence += 10 if data.long_horizon_plan is not None else 0
    evidence += 10 if data.strategy_dna is not None else 0
    evidence += min(10, len(data.previous_generations) * 3)
    return _clamp(evidence)


def _lineage_stability_score(data: StrategyEvolutionInput) -> int:
    if not data.previous_generations:
        return 60
    scores = [generation.fitness_score for generation in data.previous_generations]
    score = sum(scores) / len(scores)
    if any(not generation.preserved_core_dna for generation in data.previous_generations):
        score -= 20
    if len({mutation for generation in data.previous_generations for mutation in generation.mutations if mutation != StrategyMutation.NO_MUTATION}) >= 5:
        score -= 20
    if len(scores) >= 2 and scores[-1] + 12 < scores[0]:
        score -= 15
    return _clamp(score)


def _current_generation(data: StrategyEvolutionInput, fitness: StrategyFitnessScore, mutations: tuple[StrategyMutation, ...]) -> StrategyGeneration:
    parent = data.previous_generations[-1] if data.previous_generations else None
    strategy_name = data.strategy_dna.name if data.strategy_dna is not None else "unbound_strategy"
    version = (parent.version + 1) if parent else 1
    generation_id = f"{strategy_name}:g{version}"
    meaningful_mutations = tuple(m for m in mutations if m != StrategyMutation.NO_MUTATION)
    return StrategyGeneration(
        generation_id=generation_id,
        strategy_name=strategy_name,
        version=version,
        fitness_score=_overall_fitness(fitness),
        mutations=meaningful_mutations or (StrategyMutation.NO_MUTATION,),
        parent_generation_id=parent.generation_id if parent else None,
        preserved_core_dna=fitness.dna_preservation_score >= 60 and StrategyMutation.NO_MUTATION not in meaningful_mutations,
        notes=(f"fitness={_overall_fitness(fitness)}",),
    )


def _strategy_drift(data: StrategyEvolutionInput) -> bool:
    return (
        data.scenario_forecast is not None and ForecastScenarioType.STRATEGIC_DRIFT in data.scenario_forecast.critical_scenarios
    ) or (
        data.long_horizon_plan is not None and PlanningRisk.STRATEGIC_DRIFT_RISK in data.long_horizon_plan.risks
    )


def _mutation_count(data: StrategyEvolutionInput) -> int:
    return sum(1 for generation in data.previous_generations for mutation in generation.mutations if mutation != StrategyMutation.NO_MUTATION)


def _fitness_degraded(data: StrategyEvolutionInput) -> bool:
    if len(data.previous_generations) < 2:
        return False
    return data.previous_generations[-1].fitness_score + 10 < data.previous_generations[-2].fitness_score


def _behavior_unsafe(data: StrategyEvolutionInput) -> bool:
    return (
        data.behavioral_stability is not None
        and (data.behavioral_stability.stability_score < 45 or data.behavioral_stability.pressure_level == BehavioralPressureLevel.EXTREME)
    )


def _alignment_weak(data: StrategyEvolutionInput) -> bool:
    return (
        data.intent_alignment is not None
        and (data.intent_alignment.alignment_confidence < 50 or data.intent_alignment.mode in {IntentAlignmentMode.MISALIGNED, IntentAlignmentMode.CRITICAL_REALIGNMENT})
    )


def _reward_overfit(data: StrategyEvolutionInput) -> bool:
    return (
        data.reward_evaluation is not None
        and data.reward_evaluation.normalized_reward >= 75
        and (
            _risk_control_score(data) < 55
            or (data.tactical_execution is not None and data.tactical_execution.quality in {TacticalExecutionQuality.WEAK, TacticalExecutionQuality.DANGEROUS})
        )
    )


def _core_dna_at_risk(data: StrategyEvolutionInput) -> bool:
    return _dna_preservation_score(data) < 55 or any(not generation.preserved_core_dna for generation in data.previous_generations[-2:])


def _unsafe_policy_propagation(data: StrategyEvolutionInput) -> bool:
    if data.policy_memory is not None and data.policy_memory.disabled_policies:
        return True
    return data.learning_governance is not None and data.learning_governance.decision in {
        LearningGovernanceDecision.LOCK_DANGEROUS_POLICY,
        LearningGovernanceDecision.ENTER_SAFETY_LOCKDOWN,
    }


def _freeze_required(data: StrategyEvolutionInput) -> bool:
    return (
        data.learning_governance is not None
        and (
            data.learning_governance.mode in {LearningGovernanceMode.FREEZE_LEARNING, LearningGovernanceMode.SAFETY_LOCKDOWN}
            or data.learning_governance.decision in {LearningGovernanceDecision.FREEZE_POLICY_UPDATE, LearningGovernanceDecision.ENTER_SAFETY_LOCKDOWN}
        )
    ) or (
        data.scenario_forecast is not None and data.scenario_forecast.decision == ForecastDecision.ENTER_FORECAST_SAFE_MODE
    )


def _forecast_safe_or_degraded(data: StrategyEvolutionInput) -> bool:
    return data.scenario_forecast is not None and data.scenario_forecast.decision in {
        ForecastDecision.PRIORITIZE_SAFE_SCENARIO,
        ForecastDecision.AVOID_HIGH_RISK_SCENARIO,
        ForecastDecision.ENTER_FORECAST_SAFE_MODE,
    }


def _time_window_needed(data: StrategyEvolutionInput) -> bool:
    return (
        data.tactical_execution is not None
        and (
            TacticalExecutionSignal.TIMING_BAD in data.tactical_execution.signals
            or TacticalExecutionSignal.VOLATILITY_MISMATCH in data.tactical_execution.signals
        )
    )


def _policy_memory_weak(data: StrategyEvolutionInput) -> bool:
    return (
        data.policy_memory is not None
        and data.policy_memory.entries
        and any(entry.confidence_score < 45 or entry.dangerous_decision_rate >= 0.25 for entry in data.policy_memory.entries.values())
    )


def _critical_risk_count(risks: tuple[StrategyEvolutionRisk, ...]) -> int:
    critical = {
        StrategyEvolutionRisk.FITNESS_DEGRADATION,
        StrategyEvolutionRisk.BEHAVIORAL_UNSAFE_EVOLUTION,
        StrategyEvolutionRisk.ALIGNMENT_BREAK,
        StrategyEvolutionRisk.LOSS_OF_CORE_DNA,
        StrategyEvolutionRisk.UNSTABLE_LINEAGE,
        StrategyEvolutionRisk.UNSAFE_POLICY_PROPAGATION,
    }
    return len(critical.intersection(risks))


def _mode_for_decision(
    decision: StrategyEvolutionDecision,
    risks: tuple[StrategyEvolutionRisk, ...],
    data: StrategyEvolutionInput,
) -> StrategyEvolutionMode:
    if decision == StrategyEvolutionDecision.FREEZE_STRATEGY_EVOLUTION:
        return StrategyEvolutionMode.FREEZE_EVOLUTION
    if decision == StrategyEvolutionDecision.ROLLBACK_TO_STABLE_GENERATION:
        return StrategyEvolutionMode.SAFE_ROLLBACK
    if decision == StrategyEvolutionDecision.REBUILD_STRATEGY_FAMILY:
        return StrategyEvolutionMode.REBUILD_STRATEGY
    if StrategyEvolutionRisk.BEHAVIORAL_UNSAFE_EVOLUTION in risks or _recovery_context(data):
        return StrategyEvolutionMode.RECOVERY_EVOLUTION
    if decision == StrategyEvolutionDecision.APPLY_CONTROLLED_MUTATION:
        return StrategyEvolutionMode.CONTROLLED_EVOLUTION
    if decision == StrategyEvolutionDecision.TEST_MUTATION_OFFLINE:
        return StrategyEvolutionMode.MUTATION_EXPERIMENT
    if decision == StrategyEvolutionDecision.REQUIRE_MORE_EVIDENCE:
        return StrategyEvolutionMode.CONSERVATIVE_ADAPTATION
    return StrategyEvolutionMode.STABLE_PRESERVATION


def _recovery_context(data: StrategyEvolutionInput) -> bool:
    return data.long_horizon_plan is not None and data.long_horizon_plan.decision == PlanningDecision.PRIORITIZE_RECOVERY


def _avg(values: list[float], default: int) -> int:
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
    "build_strategy_lineage_graph",
    "compute_strategy_fitness",
    "decide_strategy_evolution",
    "detect_strategy_evolution_risks",
    "evaluate_strategy_evolution",
    "generate_strategy_evolution_recommendations",
    "propose_strategy_mutations",
    "render_strategy_evolution_markdown",
]
