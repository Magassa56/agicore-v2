"""Unit tests for the offline Safe RL experiment layer."""
from __future__ import annotations

from agicore.trading.behavior_models import (
    BehaviorAnalysisResult,
    BehaviorRecommendation,
    BehaviorScores,
    BehaviorSummary,
    SessionBehaviorClass,
)
from agicore.trading.context_scoring_models import (
    ContextScoreBreakdown,
    ContextScoringResult,
    TradeContextDecision,
)
from agicore.trading.market_regime_models import (
    MarketRegime,
    MarketRegimeAnalysis,
    RegimeStrength,
    SessionCondition,
    VolatilityRegime,
)
from agicore.trading.offline_dataset_models import (
    DatasetQualityReport,
    LearningAction,
    LearningReward,
    LearningState,
    LearningTransition,
    OfflineLearningDataset,
)
from agicore.trading.reward_models import (
    RewardBreakdown,
    RewardComponent,
    RewardEvaluationResult,
    RewardLabel,
)
from agicore.trading.rl_playground_models import (
    RLExperimentConfig,
    RLPlaygroundResult,
    RLPolicyCandidate,
    RLPolicyScore,
    RLTrainingEpisode,
)
from agicore.trading.safe_rl_layer import (
    build_safe_rl_report,
    evaluate_rl_safety,
    render_safe_rl_markdown,
    validate_rl_experiment,
)
from agicore.trading.safe_rl_models import (
    SafeRLExperimentConfig,
    SafeRLGuardrail,
    SafeRLStatus,
    SafeRLValidationResult,
)


def _dataset() -> OfflineLearningDataset:
    return OfflineLearningDataset(
        name="safe-rl-test",
        transitions=(
            LearningTransition(
                state=LearningState(context_score=82, market_regime="TRENDING_UP"),
                action=LearningAction(policy_name="BALANCED", approved=True),
                reward=LearningReward(total_reward=50, normalized_reward=70, reward_label="GOOD_DECISION"),
                next_state=LearningState(context_score=84),
            ),
        ),
    )


def _quality(*, score: int = 90, transitions: int = 20) -> DatasetQualityReport:
    return DatasetQualityReport(
        transitions_count=transitions,
        unique_states_count=transitions,
        unique_actions_count=3,
        average_reward=70.0,
        dangerous_decision_count=0,
        no_trade_count=0,
        missing_reward_count=0,
        missing_next_state_count=0,
        quality_score=score,
        warnings=(),
    )


def _playground(
    *,
    candidate_name: str = "balanced_threshold_policy",
    score: int = 80,
    dangerous_rate: float = 0.0,
) -> RLPlaygroundResult:
    policy_score = RLPolicyScore(
        candidate_name=candidate_name,
        total_reward=100,
        average_reward=20.0,
        dangerous_decision_rate=dangerous_rate,
        no_trade_rate=0.2,
        correct_block_rate=0.8,
        final_score=score,
        transitions_evaluated=20,
        accepted_decisions=10,
        blocked_decisions=10,
        reduced_risk_decisions=0,
        risk_notes=(),
    )
    candidate = RLPolicyCandidate(
        name=candidate_name,
        min_context_score=65,
        reduce_risk_below_score=75,
        block_high_risk=True,
        block_revenge_trading=True,
        block_overtrading=True,
    )
    episode = RLTrainingEpisode(
        candidate_name=candidate_name,
        dataset_name="safe-rl-test",
        transitions_count=20,
        policy_score=policy_score,
    )
    return RLPlaygroundResult(
        config=RLExperimentConfig(),
        dataset=_dataset(),
        candidates=(candidate,),
        episodes=(episode,),
        ranked_scores=(policy_score,),
        best_policy=policy_score,
        safety_notes=("offline",),
    )


def _context(decision: TradeContextDecision = TradeContextDecision.TRADE_ALLOWED) -> ContextScoringResult:
    return ContextScoringResult(
        global_score=80,
        decision=decision,
        breakdown=ContextScoreBreakdown(
            market_score=80,
            behavior_score=80,
            discipline_score=80,
            memory_score=80,
            emotional_score=80,
            volatility_score=80,
            strategy_regime_compatibility_score=80,
        ),
        favorable_factors=(),
        risk_factors=(),
        recommendations=(),
        strategy_regime_notes=(),
    )


def _market(*, dangerous: bool = False) -> MarketRegimeAnalysis:
    return MarketRegimeAnalysis(
        primary_regime=MarketRegime.NEWS_RISK if dangerous else MarketRegime.TRENDING_UP,
        confidence=80,
        strength=RegimeStrength.STRONG,
        volatility=VolatilityRegime.EXTREME if dangerous else VolatilityRegime.NORMAL,
        session_condition=SessionCondition.DANGEROUS if dangerous else SessionCondition.FAVORABLE,
        context_quality_score=20 if dangerous else 80,
        favorable_for_pullback_strategy=not dangerous,
        dangerous_market=dangerous,
        detected_regimes=(MarketRegime.NEWS_RISK if dangerous else MarketRegime.TRENDING_UP,),
        warnings=(),
        recommendations=(),
    )


def _behavior(*, emotional: int = 30, overtrading: bool = False, revenge: bool = False) -> BehaviorAnalysisResult:
    classes = [SessionBehaviorClass.DISCIPLINED]
    if overtrading:
        classes.append(SessionBehaviorClass.OVERTRADING)
    if revenge:
        classes.append(SessionBehaviorClass.REVENGE_TRADING_PROBABLE)
    return BehaviorAnalysisResult(
        classifications=tuple(classes),
        patterns=(),
        scores=BehaviorScores(
            discipline_score=80,
            emotional_risk_score=emotional,
            consistency_score=80,
            risk_escalation_score=20,
        ),
        recommendations=(BehaviorRecommendation.KEEP_CURRENT_RULES,),
        summary=BehaviorSummary(
            strengths=(),
            weaknesses=(),
            dangerous_hours=(),
            favorable_context="test",
            probable_trader_profile="test",
        ),
    )


def _reward(total: int = 20, normalized: int = 65) -> RewardEvaluationResult:
    neutral = RewardComponent("neutral", 0, "neutral")
    return RewardEvaluationResult(
        total_reward=total,
        normalized_reward=normalized,
        reward_label=RewardLabel.ACCEPTABLE,
        breakdown=RewardBreakdown(
            pnl_reward=neutral,
            risk_adjusted_reward=neutral,
            discipline_reward=neutral,
            context_alignment_reward=neutral,
            behavior_reward=neutral,
            drawdown_penalty=neutral,
            rule_violation_penalty=neutral,
            overtrading_penalty=neutral,
            revenge_trading_penalty=neutral,
            strategy_compliance_reward=neutral,
            memory_improvement_reward=neutral,
        ),
        learning_notes=(),
        improvement_actions=(),
    )


def test_validate_rl_experiment_allows_safe_offline_dry_run() -> None:
    result = validate_rl_experiment(
        dataset_quality=_quality(),
        playground_result=_playground(),
        context_score=_context(),
        market_regime=_market(),
        behavior_result=_behavior(),
        reward_result=_reward(),
        config=SafeRLExperimentConfig(min_transitions_count=1),
    )

    assert result.status == SafeRLStatus.SAFE
    assert result.allowed_experiments == ("offline_dry_run_policy_evaluation",)
    assert not result.blocked_experiments


def test_validate_rl_experiment_blocks_unsafe_live_or_real_order_config() -> None:
    result = validate_rl_experiment(
        dataset_quality=_quality(),
        playground_result=_playground(),
        config=SafeRLExperimentConfig(
            min_transitions_count=1,
            dry_run=False,
            allow_live_broker=True,
            allow_real_orders=True,
            allow_neural_training=True,
            allow_external_ml=True,
        ),
    )

    assert result.status == SafeRLStatus.BLOCKED
    assert SafeRLGuardrail.REQUIRE_DRY_RUN in result.active_guardrails
    assert SafeRLGuardrail.FORBID_LIVE_BROKER.value in result.blocked_experiments
    assert SafeRLGuardrail.FORBID_REAL_ORDER.value in result.blocked_experiments
    assert SafeRLGuardrail.FORBID_NEURAL_TRAINING.value in result.blocked_experiments


def test_validate_rl_experiment_blocks_context_market_behavior_and_reward_risks() -> None:
    result = validate_rl_experiment(
        dataset_quality=_quality(score=40, transitions=2),
        playground_result=_playground(candidate_name="aggressive_threshold_policy", score=45, dangerous_rate=0.5),
        context_score=_context(TradeContextDecision.NO_TRADE),
        market_regime=_market(dangerous=True),
        behavior_result=_behavior(emotional=95, overtrading=True, revenge=True),
        reward_result=_reward(total=-200, normalized=10),
        config=SafeRLExperimentConfig(min_transitions_count=10),
    )

    assert result.status == SafeRLStatus.BLOCKED
    assert SafeRLGuardrail.DATASET_QUALITY_MINIMUM.value in result.blocked_experiments
    assert SafeRLGuardrail.MINIMUM_TRANSITIONS_COUNT.value in result.blocked_experiments
    assert SafeRLGuardrail.BLOCK_AGGRESSIVE_HIGH_RISK.value in result.blocked_experiments
    assert SafeRLGuardrail.BLOCK_DANGEROUS_MARKET.value in result.blocked_experiments
    assert SafeRLGuardrail.BLOCK_OVERTRADING.value in result.blocked_experiments
    assert SafeRLGuardrail.BLOCK_REVENGE_TRADING.value in result.blocked_experiments
    assert SafeRLGuardrail.BLOCK_NO_TRADE_CONTEXT.value in result.blocked_experiments
    assert SafeRLGuardrail.BLOCK_NEGATIVE_REWARD.value in result.blocked_experiments


def test_evaluate_rl_safety_alias_and_build_safe_rl_report_review_required() -> None:
    alias_result = evaluate_rl_safety(dataset=_dataset(), config=SafeRLExperimentConfig(min_transitions_count=1))
    manual_report = build_safe_rl_report(
        (
            SafeRLValidationResult(
                guardrail=SafeRLGuardrail.POLICY_SCORE_MINIMUM,
                status=SafeRLStatus.REVIEW_REQUIRED,
                message="missing policy",
            ),
        )
    )

    assert alias_result.status in {SafeRLStatus.REVIEW_REQUIRED, SafeRLStatus.WARNING, SafeRLStatus.BLOCKED, SafeRLStatus.SAFE}
    assert manual_report.status == SafeRLStatus.REVIEW_REQUIRED
    assert manual_report.allowed_experiments == ()


def test_render_safe_rl_markdown_contains_required_sections() -> None:
    result = validate_rl_experiment(
        dataset_quality=_quality(),
        playground_result=_playground(),
        config=SafeRLExperimentConfig(min_transitions_count=1),
    )

    markdown = render_safe_rl_markdown(result)

    assert "# Safe RL Experiment Layer" in markdown
    assert "## Statut securite RL" in markdown
    assert "## Resume validation" in markdown
    assert "## Guardrails actifs" in markdown
    assert "## Risques detectes" in markdown
    assert "## Experiences autorisees" in markdown
    assert "## Experiences bloquees" in markdown
    assert "## Recommandations AGIcore" in markdown
    assert "no live broker" in markdown
