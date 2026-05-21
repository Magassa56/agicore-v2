"""Unit tests for the offline Cognitive Adaptation Engine."""
from __future__ import annotations

from agicore.trading.behavioral_stability_models import (
    BehavioralPressureLevel,
    BehavioralRecoveryState,
    BehavioralStabilityResult,
    BehavioralStabilityScore,
)
from agicore.trading.cognitive_adaptation import (
    compute_cognitive_flexibility_score,
    detect_cognitive_signals,
    evaluate_cognitive_adaptation,
    recommend_adaptation_mode,
    render_cognitive_adaptation_markdown,
)
from agicore.trading.cognitive_adaptation_models import (
    CognitiveAdaptationMode,
    CognitiveAdaptationSignal,
    CognitiveLoadLevel,
)
from agicore.trading.context_scoring_models import ContextScoreBreakdown, ContextScoringResult, TradeContextDecision
from agicore.trading.executive_brain_models import (
    ExecutiveBrainResult,
    ExecutiveDecision,
    ExecutiveIntent,
    ExecutiveMode,
    ExecutiveRiskAppetite,
    ExecutiveState,
)
from agicore.trading.hierarchical_supervisor_models import SupervisorDecision, SupervisorOverride, SupervisorResult
from agicore.trading.meta_strategy_models import MetaStrategyDecision, MetaStrategySelectionResult
from agicore.trading.reward_models import RewardBreakdown, RewardComponent, RewardEvaluationResult, RewardLabel
from agicore.trading.strategic_memory_models import StrategicDriftSignal, StrategicTimelineAnalysis
from agicore.trading.strategic_planning_models import (
    StrategicHorizon,
    StrategicObjective,
    StrategicPlan,
    StrategicPlanningResult,
    StrategicPlanStatus,
)
from agicore.trading.tactical_execution_models import (
    TacticalExecutionEvent,
    TacticalExecutionQuality,
    TacticalExecutionResult,
    TacticalExecutionSignal,
    TacticalScoreBreakdown,
)


def _context(decision: TradeContextDecision = TradeContextDecision.TRADE_ALLOWED, score: int = 75) -> ContextScoringResult:
    return ContextScoringResult(
        global_score=score,
        decision=decision,
        breakdown=ContextScoreBreakdown(score, score, score, score, score, score, score),
        favorable_factors=(),
        risk_factors=(),
        recommendations=(),
        strategy_regime_notes=(),
    )


def _reward(label: RewardLabel = RewardLabel.GOOD_DECISION, normalized: int = 75, total: int = 20) -> RewardEvaluationResult:
    component = RewardComponent("x", 0, "x")
    return RewardEvaluationResult(
        total_reward=total,
        normalized_reward=normalized,
        reward_label=label,
        breakdown=RewardBreakdown(component, component, component, component, component, component, component, component, component, component, component),
        learning_notes=(),
        improvement_actions=(),
    )


def _behavior(score: int = 80, pressure: BehavioralPressureLevel = BehavioralPressureLevel.LOW) -> BehavioralStabilityResult:
    return BehavioralStabilityResult(
        stability_score=score,
        pressure_level=pressure,
        recovery_state=BehavioralRecoveryState.STABLE,
        score_breakdown=BehavioralStabilityScore(score, score, score, score, score, score),
        signals=(),
        risks=(),
        recommendations=(),
        events=(),
    )


def _timeline(
    stability: int = 80,
    health: int = 80,
    improvement: bool = False,
    degradation: bool = False,
    drifts: tuple[StrategicDriftSignal, ...] = (),
) -> StrategicTimelineAnalysis:
    return StrategicTimelineAnalysis(
        snapshots_count=4,
        cycle_phases=(),
        drift_signals=drifts,
        best_period=None,
        worst_period=None,
        stability_score=stability,
        strategic_health_score=health,
        improvement_detected=improvement,
        degradation_detected=degradation,
        recommendations=(),
        summary="timeline",
    )


def _strategic(progress: int = 75, status: StrategicPlanStatus = StrategicPlanStatus.ACTIVE) -> StrategicPlanningResult:
    plan = StrategicPlan(
        horizon=StrategicHorizon.WEEKLY,
        primary_objective=StrategicObjective.CONSISTENCY_BUILDING,
        status=status,
        session_objectives=(),
        risk_constraints=(),
        max_trades_per_session=2,
        max_session_loss_r=0.5,
        focus_behavior="clarity",
    )
    return StrategicPlanningResult(plan=plan, progress_score=progress, progress_notes=(), events=(), recommendation="ok")


def _executive(mode: ExecutiveMode = ExecutiveMode.NORMAL, stop: bool = False) -> ExecutiveBrainResult:
    state = ExecutiveState(mode, ExecutiveIntent.CONTROLLED_GROWTH, ExecutiveRiskAppetite.MODERATE, "objective", (), ())
    decision = ExecutiveDecision(not stop, False, False, stop, "LABEL", "action")
    return ExecutiveBrainResult(state=state, decision=decision, events=(), recommendation="ok")


def _supervisor(decision: SupervisorDecision = SupervisorDecision.APPROVE_SYSTEM_DECISION, executable: bool = True, conflicts: tuple[str, ...] = ()) -> SupervisorResult:
    return SupervisorResult(
        decision=decision,
        final_executable=executable,
        applied_overrides=(SupervisorOverride.NONE,),
        reliability_scores=(),
        trusted_agents=(),
        agents_to_watch=(),
        conflicts_detected=conflicts,
        critical_risks=(),
        events=(),
        recommendation="ok",
    )


def _meta(decision: MetaStrategyDecision = MetaStrategyDecision.SELECT_POLICY, review: bool = False) -> MetaStrategySelectionResult:
    return MetaStrategySelectionResult(
        selected_policy_name="BALANCED",
        decision=decision,
        confidence_score=75,
        ranked_candidates=(),
        reasons=(),
        risk_notes=(),
        required_manual_review=review,
        recommendation="ok",
    )


def _tactical(quality: TacticalExecutionQuality = TacticalExecutionQuality.GOOD) -> TacticalExecutionResult:
    return TacticalExecutionResult(
        quality=quality,
        global_score=80,
        breakdown=TacticalScoreBreakdown(80, 75, 75, 75, 80, 80, 75),
        signals=(TacticalExecutionSignal.TACTICAL_DISCIPLINE_STRONG,),
        risks=(),
        recommendations=(),
        events=(TacticalExecutionEvent(quality, "ok", __import__("datetime").datetime.now(__import__("datetime").UTC)),),
    )


def test_compute_cognitive_flexibility_score_rewards_clear_stable_context() -> None:
    score = compute_cognitive_flexibility_score(
        behavioral_stability=_behavior(),
        strategic_timeline_analysis=_timeline(improvement=True),
        strategic_result=_strategic(),
        executive_result=_executive(ExecutiveMode.OPPORTUNITY),
        meta_strategy=_meta(),
        context_score=_context(TradeContextDecision.STRONG_TRADE_ALLOWED, 90),
        reward_evaluation=_reward(RewardLabel.EXCELLENT_DECISION, 90, 50),
        tactical_execution=_tactical(),
    )

    assert score.strategic_clarity_score >= 80
    assert score.decision_flexibility_score >= 70
    assert score.recovery_learning_score >= 80


def test_detects_cognitive_overload_from_pressure_and_conflicts() -> None:
    signals = detect_cognitive_signals(
        behavioral_stability=_behavior(30, BehavioralPressureLevel.EXTREME),
        supervisor_result=_supervisor(SupervisorDecision.REQUIRE_HUMAN_REVIEW, False, ("risk", "policy")),
        executive_result=_executive(ExecutiveMode.SURVIVAL, stop=True),
    )

    assert CognitiveAdaptationSignal.COGNITIVE_OVERLOAD in signals
    assert CognitiveAdaptationSignal.DECISION_CONFUSION in signals


def test_detects_rigid_policy_use_and_underreaction() -> None:
    signals = detect_cognitive_signals(
        meta_strategy=_meta(MetaStrategyDecision.SELECT_POLICY, review=False),
        reward_evaluation=_reward(RewardLabel.BAD_DECISION, 25, -20),
        context_score=_context(TradeContextDecision.HIGH_RISK_CONTEXT, 35),
        strategic_timeline_analysis=_timeline(degradation=True, drifts=(StrategicDriftSignal.REWARD_DECLINE,)),
    )

    assert CognitiveAdaptationSignal.RIGID_POLICY_USE in signals
    assert CognitiveAdaptationSignal.UNDER_REACTION_RISK in signals


def test_detects_overreaction_after_single_bad_session() -> None:
    signals = detect_cognitive_signals(
        meta_strategy=_meta(MetaStrategyDecision.BLOCK_ALL_POLICIES),
        reward_evaluation=_reward(RewardLabel.BAD_DECISION, 35, -5),
        strategic_timeline_analysis=_timeline(degradation=False),
    )

    assert CognitiveAdaptationSignal.OVER_REACTION_RISK in signals


def test_detects_adaptation_success_and_stable_pattern() -> None:
    signals = detect_cognitive_signals(
        behavioral_stability=_behavior(85),
        strategic_timeline_analysis=_timeline(stability=85, health=85, improvement=True),
        context_score=_context(TradeContextDecision.STRONG_TRADE_ALLOWED, 88),
        reward_evaluation=_reward(RewardLabel.GOOD_DECISION, 82, 30),
        tactical_execution=_tactical(TacticalExecutionQuality.EXCELLENT),
    )

    assert CognitiveAdaptationSignal.ADAPTATION_SUCCESS in signals
    assert CognitiveAdaptationSignal.STABLE_PATTERN_EXPLOITABLE in signals


def test_recommend_pause_when_overloaded() -> None:
    mode = recommend_adaptation_mode(
        behavioral_stability=_behavior(20, BehavioralPressureLevel.EXTREME),
        supervisor_result=_supervisor(SupervisorDecision.EMERGENCY_HALT, False, ("risk", "safe_rl")),
    )

    assert mode == CognitiveAdaptationMode.PAUSE


def test_recommend_recover_when_behavioral_stability_low() -> None:
    mode = recommend_adaptation_mode(behavioral_stability=_behavior(35, BehavioralPressureLevel.HIGH))

    assert mode == CognitiveAdaptationMode.RECOVER


def test_recommend_exploit_stable_pattern() -> None:
    mode = recommend_adaptation_mode(
        behavioral_stability=_behavior(85),
        strategic_timeline_analysis=_timeline(stability=85, health=85),
        context_score=_context(TradeContextDecision.TRADE_ALLOWED, 82),
        reward_evaluation=_reward(RewardLabel.GOOD_DECISION, 80, 25),
    )

    assert mode == CognitiveAdaptationMode.EXPLOIT_STABLE_PATTERN


def test_evaluate_cognitive_adaptation_returns_result_and_events() -> None:
    result = evaluate_cognitive_adaptation(
        behavioral_stability=_behavior(),
        strategic_result=_strategic(),
        executive_result=_executive(),
        context_score=_context(),
        reward_evaluation=_reward(),
    )

    assert result.global_score >= 0
    assert result.load_level in set(CognitiveLoadLevel)
    assert result.events
    assert result.recommendations


def test_observation_mode_recommended_for_low_evidence() -> None:
    result = evaluate_cognitive_adaptation()

    assert CognitiveAdaptationSignal.OBSERVATION_MODE_RECOMMENDED in result.signals
    assert result.adaptation_mode == CognitiveAdaptationMode.OBSERVE


def test_render_cognitive_adaptation_markdown_contains_required_sections() -> None:
    result = evaluate_cognitive_adaptation(
        behavioral_stability=_behavior(),
        strategic_timeline_analysis=_timeline(),
        context_score=_context(),
        reward_evaluation=_reward(),
    )

    markdown = render_cognitive_adaptation_markdown(result)

    assert "# Cognitive Adaptation Engine" in markdown
    assert "## Adaptation cognitive" in markdown
    assert "## Charge cognitive" in markdown
    assert "## Flexibilite decisionnelle" in markdown
    assert "## Signaux detectes" in markdown
    assert "## Risques cognitifs" in markdown
    assert "## Mode recommande" in markdown
    assert "## Recommandations AGIcore" in markdown
    assert "no broker" in markdown
