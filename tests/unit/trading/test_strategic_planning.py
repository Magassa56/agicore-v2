"""Unit tests for the offline Strategic Planning Engine."""
from __future__ import annotations

from agicore.trading.adaptive_memory_models import TraderMemoryProfile
from agicore.trading.context_scoring_models import ContextScoreBreakdown, ContextScoringResult, TradeContextDecision
from agicore.trading.executive_brain import update_executive_state
from agicore.trading.executive_brain_models import ExecutiveMode
from agicore.trading.hierarchical_supervisor_models import SupervisorDecision, SupervisorOverride, SupervisorResult
from agicore.trading.offline_dataset_models import DatasetQualityReport
from agicore.trading.reward_models import RewardBreakdown, RewardComponent, RewardEvaluationResult, RewardLabel
from agicore.trading.rl_playground_models import (
    RLExperimentConfig,
    RLPlaygroundResult,
    RLPolicyCandidate,
    RLPolicyScore,
)
from agicore.trading.strategic_planning import (
    build_strategic_plan,
    evaluate_strategic_progress,
    render_strategic_plan_markdown,
    update_strategic_plan,
)
from agicore.trading.strategic_planning_models import (
    StrategicHorizon,
    StrategicObjective,
    StrategicPlanStatus,
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


def _supervisor(decision: SupervisorDecision = SupervisorDecision.APPROVE_SYSTEM_DECISION, executable: bool = True) -> SupervisorResult:
    return SupervisorResult(
        decision=decision,
        final_executable=executable,
        applied_overrides=(SupervisorOverride.NONE,),
        reliability_scores=(),
        trusted_agents=(),
        agents_to_watch=(),
        conflicts_detected=(),
        critical_risks=(),
        events=(),
        recommendation="supervisor",
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


def _dataset(quality: int = 80, transitions: int = 25, dangerous: int = 0) -> DatasetQualityReport:
    return DatasetQualityReport(
        transitions_count=transitions,
        unique_states_count=10,
        unique_actions_count=4,
        average_reward=12,
        dangerous_decision_count=dangerous,
        no_trade_count=1,
        missing_reward_count=0,
        missing_next_state_count=0,
        quality_score=quality,
        warnings=(),
    )


def _playground(score: int = 80) -> RLPlaygroundResult:
    candidate = RLPolicyCandidate("BALANCED", 60, 55, True, True, True)
    policy_score = RLPolicyScore(
        candidate_name="BALANCED",
        total_reward=50,
        average_reward=10,
        dangerous_decision_rate=0,
        no_trade_rate=0.1,
        correct_block_rate=0.8,
        final_score=score,
        transitions_evaluated=10,
        accepted_decisions=5,
        blocked_decisions=3,
        reduced_risk_decisions=2,
        risk_notes=(),
    )
    return RLPlaygroundResult(
        config=RLExperimentConfig(),
        dataset=None,  # type: ignore[arg-type]
        candidates=(candidate,),
        episodes=(),
        ranked_scores=(policy_score,),
        best_policy=policy_score,
        safety_notes=(),
    )


def test_build_plan_pauses_when_executive_brain_is_paused() -> None:
    executive = update_executive_state(context_score=_context(TradeContextDecision.NO_TRADE, 20))

    plan = build_strategic_plan(executive_result=executive)

    assert plan.primary_objective == StrategicObjective.PAUSE_AND_REVIEW
    assert plan.status == StrategicPlanStatus.PAUSED
    assert plan.max_trades_per_session == 0


def test_build_plan_enters_drawdown_recovery_on_negative_reward() -> None:
    plan = build_strategic_plan(
        reward_evaluation=_reward(RewardLabel.BAD_DECISION, normalized=25, total=-30),
        context_score=_context(),
    )

    assert plan.primary_objective == StrategicObjective.DRAWDOWN_RECOVERY
    assert plan.status == StrategicPlanStatus.RECOVERY
    assert plan.max_session_loss_r == 0.25


def test_build_plan_preserves_capital_on_high_risk_context() -> None:
    plan = build_strategic_plan(context_score=_context(TradeContextDecision.HIGH_RISK_CONTEXT, 35))

    assert plan.primary_objective == StrategicObjective.CAPITAL_PRESERVATION
    assert plan.status == StrategicPlanStatus.DEFENSIVE
    assert "CONTEXT_RISK" in plan.long_term_risks


def test_build_plan_uses_learning_phase_for_weak_dataset() -> None:
    plan = build_strategic_plan(dataset_quality=_dataset(quality=45, transitions=4), context_score=_context())

    assert plan.primary_objective == StrategicObjective.LEARNING_PHASE
    assert plan.status == StrategicPlanStatus.REVIEW_REQUIRED
    assert plan.max_trades_per_session == 2


def test_build_plan_favors_policy_validation_in_stable_context() -> None:
    plan = build_strategic_plan(
        context_score=_context(TradeContextDecision.TRADE_ALLOWED, 78),
        dataset_quality=_dataset(quality=82),
        rl_playground=_playground(85),
    )

    assert plan.primary_objective == StrategicObjective.POLICY_VALIDATION
    assert plan.policy_to_test == "BALANCED"


def test_build_plan_supports_controlled_growth_from_opportunity_mode() -> None:
    executive = update_executive_state(
        context_score=_context(TradeContextDecision.STRONG_TRADE_ALLOWED, 90),
        reward_evaluation=_reward(RewardLabel.GOOD_DECISION, 85, 40),
    )

    assert executive.state.mode == ExecutiveMode.OPPORTUNITY
    plan = build_strategic_plan(executive_result=executive, context_score=_context(TradeContextDecision.STRONG_TRADE_ALLOWED, 90))

    assert plan.primary_objective == StrategicObjective.CONTROLLED_GROWTH
    assert plan.max_trades_per_session == 4


def test_evaluate_strategic_progress_penalizes_risks() -> None:
    plan = build_strategic_plan(context_score=_context())

    result = evaluate_strategic_progress(
        plan,
        context_score=_context(TradeContextDecision.HIGH_RISK_CONTEXT, 35),
        reward_evaluation=_reward(RewardLabel.BAD_DECISION, 30, -20),
        dataset_quality=_dataset(quality=45, dangerous=3),
    )

    assert result.progress_score < 70
    assert result.progress_notes
    assert result.events


def test_update_strategic_plan_keeps_previous_plan_when_no_stronger_signal() -> None:
    previous = build_strategic_plan(
        context_score=_context(),
        dataset_quality=_dataset(),
        rl_playground=_playground(),
        horizon=StrategicHorizon.DAILY,
    )

    result = update_strategic_plan(previous_plan=previous, context_score=_context())

    assert result.plan.primary_objective == previous.primary_objective
    assert result.plan.horizon == StrategicHorizon.DAILY


def test_memory_profile_high_emotional_risk_reduces_strategy() -> None:
    plan = build_strategic_plan(
        context_score=_context(),
        trader_memory_profile=TraderMemoryProfile(average_emotional_risk_score=80),
    )

    assert plan.primary_objective == StrategicObjective.CAPITAL_PRESERVATION


def test_render_strategic_plan_markdown_contains_required_sections() -> None:
    plan = build_strategic_plan(context_score=_context(), dataset_quality=_dataset(), rl_playground=_playground())
    result = evaluate_strategic_progress(plan, context_score=_context(), dataset_quality=_dataset())

    markdown = render_strategic_plan_markdown(result)

    assert "# Strategic Planning Engine" in markdown
    assert "## Plan strategique" in markdown
    assert "## Horizon" in markdown
    assert "## Objectif principal" in markdown
    assert "## Objectifs de session" in markdown
    assert "## Contraintes de risque" in markdown
    assert "## Progression" in markdown
    assert "## Risques long terme" in markdown
    assert "## Recommandations AGIcore" in markdown
    assert "no broker" in markdown
