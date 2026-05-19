"""Unit tests for the offline RL playground."""
from __future__ import annotations

from agicore.trading.offline_dataset_models import (
    LearningAction,
    LearningReward,
    LearningState,
    LearningTransition,
    OfflineLearningDataset,
)
from agicore.trading.rl_playground import (
    aggressive_threshold_policy,
    balanced_threshold_policy,
    conservative_threshold_policy,
    evaluate_policy_candidate,
    long_only_safe_policy,
    no_trade_high_risk_policy,
    rank_policy_candidates,
    render_rl_playground_markdown,
    run_rl_playground_experiment,
)
from agicore.trading.rl_playground_models import RLPolicyScore


def _dataset() -> OfflineLearningDataset:
    return OfflineLearningDataset(
        name="rl-test",
        transitions=(
            LearningTransition(
                state=LearningState(
                    context_score=88,
                    market_regime="TRENDING_UP",
                    volatility_regime="NORMAL",
                    behavior_classification=("DISCIPLINED",),
                    strategy_name="EMA20_Pullback_Pro",
                ),
                action=LearningAction(
                    policy_name="BALANCED",
                    semi_auto_decision="APPROVE_TRADE",
                    paper_action="PAPER_ORDER_FILLED",
                    approved=True,
                ),
                reward=LearningReward(
                    total_reward=120,
                    normalized_reward=86,
                    reward_label="EXCELLENT_DECISION",
                    pnl_reward=60,
                    discipline_reward=40,
                    risk_penalties=0,
                ),
                next_state=LearningState(context_score=90),
                source_id="safe-1",
            ),
            LearningTransition(
                state=LearningState(
                    context_score=25,
                    market_regime="NEWS_RISK",
                    volatility_regime="EXTREME",
                    behavior_classification=("REVENGE_TRADING_PROBABLE",),
                    strategy_name="EMA20_Pullback_Pro",
                ),
                action=LearningAction(
                    policy_name="AGGRESSIVE",
                    semi_auto_decision="APPROVE_TRADE",
                    paper_action="PAPER_ORDER_FILLED",
                    approved=True,
                ),
                reward=LearningReward(
                    total_reward=-180,
                    normalized_reward=12,
                    reward_label="DANGEROUS_DECISION",
                    pnl_reward=-70,
                    discipline_reward=-30,
                    risk_penalties=-80,
                ),
                next_state=LearningState(context_score=20),
                source_id="danger-1",
            ),
            LearningTransition(
                state=LearningState(
                    context_score=45,
                    market_regime="CHOPPY",
                    volatility_regime="HIGH",
                    behavior_classification=("OVERTRADING",),
                    strategy_name="EMA20_Pullback_Pro",
                ),
                action=LearningAction(
                    policy_name="CONSERVATIVE",
                    semi_auto_decision="BLOCK_TRADE",
                    blocked=True,
                ),
                reward=LearningReward(
                    total_reward=30,
                    normalized_reward=62,
                    reward_label="ACCEPTABLE",
                    pnl_reward=0,
                    discipline_reward=10,
                    risk_penalties=0,
                ),
                next_state=LearningState(context_score=55),
                source_id="block-1",
            ),
        ),
    )


def test_evaluate_policy_candidate_scores_conservative_safely() -> None:
    score = evaluate_policy_candidate(conservative_threshold_policy(), _dataset())

    assert score.candidate_name == "conservative_threshold_policy"
    assert score.transitions_evaluated == 3
    assert score.blocked_decisions >= 2
    assert score.dangerous_decision_rate == 0.0
    assert score.correct_block_rate > 0.0
    assert 0 <= score.final_score <= 100


def test_aggressive_policy_exposes_dangerous_decision_risk() -> None:
    score = evaluate_policy_candidate(aggressive_threshold_policy(), _dataset())

    assert score.accepted_decisions >= 1
    assert score.dangerous_decision_rate > 0.0
    assert any("dangerous" in note.lower() for note in score.risk_notes)


def test_run_rl_playground_experiment_uses_default_candidates_and_best_policy() -> None:
    result = run_rl_playground_experiment(_dataset())

    assert [candidate.name for candidate in result.candidates] == [
        "conservative_threshold_policy",
        "balanced_threshold_policy",
        "aggressive_threshold_policy",
        "no_trade_high_risk_policy",
        "long_only_safe_policy",
    ]
    assert len(result.episodes) == 5
    assert result.best_policy is not None
    assert result.ranked_scores[0] == result.best_policy
    assert any("No real order" in note for note in result.safety_notes)


def test_rank_policy_candidates_orders_by_final_score() -> None:
    low = RLPolicyScore(
        candidate_name="low",
        total_reward=0,
        average_reward=0.0,
        dangerous_decision_rate=0.0,
        no_trade_rate=0.0,
        correct_block_rate=0.0,
        final_score=40,
        transitions_evaluated=1,
        accepted_decisions=0,
        blocked_decisions=1,
        reduced_risk_decisions=0,
        risk_notes=(),
    )
    high = RLPolicyScore(
        candidate_name="high",
        total_reward=100,
        average_reward=50.0,
        dangerous_decision_rate=0.0,
        no_trade_rate=0.0,
        correct_block_rate=1.0,
        final_score=90,
        transitions_evaluated=1,
        accepted_decisions=1,
        blocked_decisions=0,
        reduced_risk_decisions=0,
        risk_notes=(),
    )

    assert rank_policy_candidates((low, high))[0].candidate_name == "high"


def test_render_rl_playground_markdown_contains_required_sections() -> None:
    result = run_rl_playground_experiment(
        _dataset(),
        candidates=(
            balanced_threshold_policy(),
            no_trade_high_risk_policy(),
            long_only_safe_policy(),
        ),
    )

    markdown = render_rl_playground_markdown(result)

    assert "# RL Training Playground" in markdown
    assert "## Resume experience" in markdown
    assert "## Politiques testees" in markdown
    assert "## Meilleure politique" in markdown
    assert "## Scores" in markdown
    assert "## Risques detectes" in markdown
    assert "## Limites" in markdown
    assert "## Prochaines etapes RL safe" in markdown
    assert "does not train a neural network" in markdown
