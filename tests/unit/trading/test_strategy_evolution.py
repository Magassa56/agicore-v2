from __future__ import annotations

from datetime import UTC, datetime

from agicore.trading.adaptive_policy_memory_models import AdaptivePolicyMemory, PolicyMemoryEntry, PolicyMemoryRecommendation
from agicore.trading.behavioral_stability_models import BehavioralPressureLevel, BehavioralRecoveryState, BehavioralStabilityResult, BehavioralStabilityScore
from agicore.trading.intent_alignment_models import IntentAlignmentMode, IntentAlignmentResult, IntentAlignmentState, IntentConfidence
from agicore.trading.learning_governance_models import LearningCycleStatus, LearningGovernanceDecision, LearningGovernanceMode
from agicore.trading.long_horizon_planning_models import PlanningDecision, PlanningRisk
from agicore.trading.reward_models import RewardBreakdown, RewardComponent, RewardEvaluationResult, RewardLabel
from agicore.trading.scenario_forecast_models import (
    ForecastDecision,
    ForecastRiskMap,
    ForecastScenarioType,
    ForecastStabilityScore,
    ScenarioForecastResult,
)
from agicore.trading.strategy_dna import define_strategy
from agicore.trading.strategy_dna_models import StrategyRiskRules, TradeDirection
from agicore.trading.strategy_evolution import (
    build_strategy_lineage_graph,
    compute_strategy_fitness,
    decide_strategy_evolution,
    detect_strategy_evolution_risks,
    evaluate_strategy_evolution,
    generate_strategy_evolution_recommendations,
    propose_strategy_mutations,
    render_strategy_evolution_markdown,
)
from agicore.trading.strategy_evolution_models import (
    StrategyEvolutionDecision,
    StrategyEvolutionMode,
    StrategyEvolutionRecommendation,
    StrategyEvolutionRisk,
    StrategyGeneration,
    StrategyMutation,
)
from agicore.trading.tactical_execution_models import TacticalExecutionEvent, TacticalExecutionQuality, TacticalExecutionResult, TacticalExecutionSignal, TacticalScoreBreakdown


def _strategy():
    return define_strategy(
        name="EMA20 Pullback",
        description="Controlled EMA20 pullback continuation strategy",
        allowed_direction=TradeDirection.LONG_ONLY,
        allowed_hours=(9, 10, 11),
        trend_filter="trend up",
        ema_filter="ema20 aligned",
        entry_conditions=("pullback into ema20", "higher low"),
        exit_conditions=("target reached", "invalidated pullback"),
        risk_rules=StrategyRiskRules(max_daily_loss=500, max_trades_per_day=3, risk_per_trade=0.5),
    )


def _reward(label=RewardLabel.GOOD_DECISION, normalized=75, total=20):
    component = RewardComponent("x", 0, "x")
    breakdown = RewardBreakdown(component, component, component, component, component, component, component, component, component, component, component)
    return RewardEvaluationResult(total, normalized, label, breakdown, (), ())


def _behavior(score=80, pressure=BehavioralPressureLevel.LOW):
    return BehavioralStabilityResult(
        score,
        pressure,
        BehavioralRecoveryState.STABLE if score >= 60 else BehavioralRecoveryState.DETERIORATING,
        BehavioralStabilityScore(score, score, score, score, score, score),
        (),
        (),
        (),
        (),
    )


def _intent(mode=IntentAlignmentMode.FULLY_ALIGNED, confidence=85):
    return IntentAlignmentResult(
        mode,
        IntentAlignmentState.ALIGNED if confidence >= 70 else IntentAlignmentState.DRIFTING,
        confidence,
        IntentConfidence(confidence, confidence, confidence, confidence, confidence, confidence, 100),
        (),
        (),
        (),
        (),
        (),
        "aligned",
        confidence,
        (),
        "intent",
    )


def _learning_governance(decision, mode, status):
    from agicore.trading.learning_governance_models import LearningGovernanceResult

    return LearningGovernanceResult(decision, mode, status, (), (), (), (), (), "governance")


def _tactical(quality=TacticalExecutionQuality.GOOD, score=75, signals=(TacticalExecutionSignal.TACTICAL_DISCIPLINE_STRONG,)):
    return TacticalExecutionResult(
        quality,
        score,
        TacticalScoreBreakdown(score, score, score, score, score, score, score),
        signals,
        (),
        (),
        (TacticalExecutionEvent(quality, "ok", datetime.now(UTC)),),
    )


def _forecast(decision=ForecastDecision.CONTINUE_CURRENT_PATH, score=78, critical=()):
    return ScenarioForecastResult(
        decision=decision,
        forecast_stability_score=score,
        stability_breakdown=ForecastStabilityScore(80, 90, 75, 75, 80, 70),
        scenarios=(),
        bifurcations=(),
        risk_map=ForecastRiskMap(25, 25, 25, 25, 25, 25, 25),
        recommendations=(),
        survivable_scenarios=(ForecastScenarioType.STABLE_CONTINUATION,),
        critical_scenarios=critical,
        events=(),
        summary="forecast",
    )


def _policy_memory(dangerous=False):
    entry = PolicyMemoryEntry(
        policy_name="balanced",
        total_evaluations=8,
        average_reward=72 if not dangerous else 35,
        average_context_score=70,
        dangerous_decision_rate=0.05 if not dangerous else 0.35,
        blocked_trade_rate=0.1,
        accepted_trade_rate=0.7,
        reduced_risk_rate=0.2,
        confidence_score=75 if not dangerous else 35,
        recommendation=PolicyMemoryRecommendation.KEEP_POLICY,
        best_contexts=("trend",),
        worst_contexts=("news",),
    )
    return AdaptivePolicyMemory(entries={"balanced": entry}, disabled_policies=("aggressive",) if dangerous else ())


def _generation(version: int, fitness: int, mutations=(), preserved=True):
    return StrategyGeneration(
        generation_id=f"EMA20 Pullback:g{version}",
        strategy_name="EMA20 Pullback",
        version=version,
        fitness_score=fitness,
        mutations=mutations,
        parent_generation_id=f"EMA20 Pullback:g{version - 1}" if version > 1 else None,
        preserved_core_dna=preserved,
    )


def test_preserves_stable_strategy_dna_when_fitness_is_strong() -> None:
    result = evaluate_strategy_evolution(
        scenario_forecast=_forecast(),
        strategy_dna=_strategy(),
        reward_evaluation=_reward(RewardLabel.GOOD_DECISION, 82),
        tactical_execution=_tactical(TacticalExecutionQuality.GOOD, 80),
        behavioral_stability=_behavior(82, BehavioralPressureLevel.LOW),
        intent_alignment=_intent(IntentAlignmentMode.FULLY_ALIGNED, 88),
        policy_memory=_policy_memory(),
        previous_generations=(_generation(1, 75),),
    )

    assert result.decision == StrategyEvolutionDecision.KEEP_CURRENT_STRATEGY
    assert result.mode == StrategyEvolutionMode.STABLE_PRESERVATION
    assert StrategyEvolutionRecommendation.PRESERVE_STRATEGY_DNA in result.recommendations


def test_detects_strategy_drift_from_forecast_and_long_horizon_risks() -> None:
    risks = detect_strategy_evolution_risks(
        scenario_forecast=_forecast(critical=(ForecastScenarioType.STRATEGIC_DRIFT,)),
        long_horizon_plan=type("Plan", (), {"risks": (PlanningRisk.STRATEGIC_DRIFT_RISK,), "decision": PlanningDecision.REDUCE_RISK_PLAN, "projection": type("Projection", (), {"projected_stability_score": 45})()})(),
        strategy_dna=_strategy(),
    )

    assert StrategyEvolutionRisk.STRATEGY_DRIFT in risks


def test_freezes_evolution_when_learning_governance_blocks() -> None:
    result = evaluate_strategy_evolution(
        strategy_dna=_strategy(),
        learning_governance=_learning_governance(
            LearningGovernanceDecision.FREEZE_POLICY_UPDATE,
            LearningGovernanceMode.FREEZE_LEARNING,
            LearningCycleStatus.FROZEN,
        ),
        reward_evaluation=_reward(RewardLabel.ACCEPTABLE, 60),
    )

    assert result.decision == StrategyEvolutionDecision.FREEZE_STRATEGY_EVOLUTION
    assert result.proposed_mutations == (StrategyMutation.NO_MUTATION,)


def test_proposes_controlled_mutations_for_weak_performance() -> None:
    mutations = propose_strategy_mutations(
        scenario_forecast=_forecast(ForecastDecision.AVOID_HIGH_RISK_SCENARIO, 45),
        strategy_dna=_strategy(),
        reward_evaluation=_reward(RewardLabel.BAD_DECISION, 35),
        tactical_execution=_tactical(TacticalExecutionQuality.WEAK, 42, (TacticalExecutionSignal.TIMING_BAD,)),
        behavioral_stability=_behavior(40, BehavioralPressureLevel.HIGH),
        intent_alignment=_intent(IntentAlignmentMode.STABLE_ALIGNMENT, 70),
    )

    assert StrategyMutation.RISK_REDUCTION_MUTATION in mutations
    assert StrategyMutation.BEHAVIOR_GUARD_MUTATION in mutations
    assert StrategyMutation.NO_MUTATION not in mutations


def test_rolls_back_when_lineage_is_unstable_but_stable_parent_exists() -> None:
    previous = (
        _generation(1, 76),
        _generation(2, 42, (StrategyMutation.ENTRY_FILTER_MUTATION,), preserved=True),
    )
    decision = decide_strategy_evolution(
        strategy_dna=_strategy(),
        reward_evaluation=_reward(RewardLabel.BAD_DECISION, 35),
        previous_generations=previous,
        intent_alignment=_intent(IntentAlignmentMode.STABLE_ALIGNMENT, 80),
    )

    assert decision == StrategyEvolutionDecision.ROLLBACK_TO_STABLE_GENERATION


def test_requires_more_evidence_when_inputs_are_sparse() -> None:
    decision = decide_strategy_evolution(strategy_dna=_strategy())

    assert decision == StrategyEvolutionDecision.REQUIRE_MORE_EVIDENCE


def test_detects_reward_overfit_when_reward_is_high_but_tactical_quality_is_dangerous() -> None:
    risks = detect_strategy_evolution_risks(
        strategy_dna=_strategy(),
        reward_evaluation=_reward(RewardLabel.EXCELLENT_DECISION, 88),
        tactical_execution=_tactical(TacticalExecutionQuality.DANGEROUS, 30),
        intent_alignment=_intent(IntentAlignmentMode.STABLE_ALIGNMENT, 80),
    )

    assert StrategyEvolutionRisk.REWARD_OVERFIT in risks


def test_builds_lineage_graph_with_stable_and_unstable_generations() -> None:
    graph = build_strategy_lineage_graph(
        strategy_dna=_strategy(),
        previous_generations=(
            _generation(1, 80),
            _generation(2, 35, (StrategyMutation.ENTRY_FILTER_MUTATION,), preserved=False),
        ),
    )

    assert "EMA20 Pullback:g1" in graph.stable_generations
    assert "EMA20 Pullback:g2" in graph.unstable_generations
    assert graph.current_generation_id == "EMA20 Pullback:g3"


def test_recommendations_include_replay_arena_and_mutation_scope_controls() -> None:
    recommendations = generate_strategy_evolution_recommendations(
        decision=StrategyEvolutionDecision.TEST_MUTATION_OFFLINE,
        risks=(StrategyEvolutionRisk.OVER_MUTATION, StrategyEvolutionRisk.LOW_EVIDENCE_EVOLUTION),
        proposed_mutations=(
            StrategyMutation.RISK_REDUCTION_MUTATION,
            StrategyMutation.ENTRY_FILTER_MUTATION,
            StrategyMutation.EXIT_FILTER_MUTATION,
        ),
        strategy_dna=_strategy(),
    )

    assert StrategyEvolutionRecommendation.TEST_IN_REPLAY_ARENA in recommendations
    assert StrategyEvolutionRecommendation.REDUCE_MUTATION_SCOPE in recommendations
    assert StrategyEvolutionRecommendation.EXTEND_VALIDATION_WINDOW in recommendations


def test_render_strategy_evolution_markdown_contains_required_sections() -> None:
    result = evaluate_strategy_evolution(
        strategy_dna=_strategy(),
        reward_evaluation=_reward(RewardLabel.GOOD_DECISION, 76),
        tactical_execution=_tactical(TacticalExecutionQuality.GOOD, 74),
        behavioral_stability=_behavior(80, BehavioralPressureLevel.LOW),
        intent_alignment=_intent(IntentAlignmentMode.FULLY_ALIGNED, 84),
    )
    markdown = render_strategy_evolution_markdown(result)

    assert "Strategy Evolution State" in markdown
    assert "Current Generation" in markdown
    assert "Fitness Score" in markdown
    assert "Proposed Mutations" in markdown
    assert "Evolution Risks" in markdown
    assert "Lineage Graph" in markdown
    assert "Decision" in markdown
    assert "Recommendations" in markdown
    assert "AGIcore Strategy Evolution Outlook" in markdown
