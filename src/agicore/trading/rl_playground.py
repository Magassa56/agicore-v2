"""Offline RL playground for deterministic policy candidates."""
from __future__ import annotations

from statistics import mean

from .offline_dataset_models import LearningTransition, OfflineLearningDataset
from .rl_playground_models import (
    RLExperimentConfig,
    RLPlaygroundResult,
    RLPolicyCandidate,
    RLPolicyScore,
    RLTrainingEpisode,
)

_BLOCK = "BLOCK"
_REDUCE_RISK = "REDUCE_RISK"
_APPROVE = "APPROVE"


def conservative_threshold_policy() -> RLPolicyCandidate:
    """Return a conservative deterministic threshold policy."""
    return RLPolicyCandidate(
        name="conservative_threshold_policy",
        min_context_score=75,
        reduce_risk_below_score=90,
        block_high_risk=True,
        block_revenge_trading=True,
        block_overtrading=True,
    )


def balanced_threshold_policy() -> RLPolicyCandidate:
    """Return a balanced deterministic threshold policy."""
    return RLPolicyCandidate(
        name="balanced_threshold_policy",
        min_context_score=65,
        reduce_risk_below_score=78,
        block_high_risk=True,
        block_revenge_trading=True,
        block_overtrading=True,
    )


def aggressive_threshold_policy() -> RLPolicyCandidate:
    """Return an aggressive deterministic threshold policy."""
    return RLPolicyCandidate(
        name="aggressive_threshold_policy",
        min_context_score=50,
        reduce_risk_below_score=62,
        block_high_risk=False,
        block_revenge_trading=False,
        block_overtrading=False,
        aggressive_approval=True,
    )


def no_trade_high_risk_policy() -> RLPolicyCandidate:
    """Return a policy that blocks high-risk contexts."""
    return RLPolicyCandidate(
        name="no_trade_high_risk_policy",
        min_context_score=60,
        reduce_risk_below_score=72,
        block_high_risk=True,
        block_revenge_trading=True,
        block_overtrading=True,
    )


def long_only_safe_policy() -> RLPolicyCandidate:
    """Return a long-only conservative policy candidate."""
    return RLPolicyCandidate(
        name="long_only_safe_policy",
        min_context_score=70,
        reduce_risk_below_score=82,
        block_high_risk=True,
        block_revenge_trading=True,
        block_overtrading=True,
        long_only=True,
    )


def evaluate_policy_candidate(
    candidate: RLPolicyCandidate,
    dataset: OfflineLearningDataset,
    config: RLExperimentConfig | None = None,
) -> RLPolicyScore:
    """Evaluate a deterministic candidate on an OfflineLearningDataset."""
    resolved_config = config or RLExperimentConfig()
    rewards: list[int] = []
    dangerous_count = 0
    no_trade_count = 0
    correct_block_count = 0
    accepted_count = 0
    blocked_count = 0
    reduced_count = 0
    risk_notes: list[str] = []

    for transition in dataset.transitions:
        decision = _candidate_decision(candidate, transition)
        target_reward = _transition_reward(transition)
        dangerous = _dangerous_transition(transition)
        no_trade_target = _target_no_trade(transition)
        correct_block = decision == _BLOCK and (dangerous or no_trade_target)

        reward = target_reward
        if decision == _APPROVE:
            accepted_count += 1
            if dangerous:
                reward -= resolved_config.wrong_approval_penalty
                risk_notes.append(f"{candidate.name}: approved a dangerous transition.")
        elif decision == _REDUCE_RISK:
            reduced_count += 1
            reward -= 2
            if dangerous:
                reward -= resolved_config.wrong_approval_penalty // 2
                risk_notes.append(f"{candidate.name}: reduced risk but still allowed a dangerous transition.")
        else:
            blocked_count += 1
            no_trade_count += 1
            if correct_block:
                correct_block_count += 1
                reward += resolved_config.correct_block_bonus
            else:
                reward -= resolved_config.no_trade_penalty

        if dangerous and decision != _BLOCK:
            dangerous_count += 1
        rewards.append(reward)

    total_reward = sum(rewards)
    average_reward = round(mean(rewards), 2) if rewards else 0.0
    transitions_count = len(dataset.transitions)
    dangerous_rate = _rate(dangerous_count, transitions_count)
    no_trade_rate = _rate(no_trade_count, transitions_count)
    correct_block_rate = _rate(correct_block_count, max(1, sum(1 for transition in dataset.transitions if _dangerous_transition(transition) or _target_no_trade(transition))))
    final_score = _final_score(
        average_reward=average_reward,
        dangerous_rate=dangerous_rate,
        correct_block_rate=correct_block_rate,
        no_trade_rate=no_trade_rate,
        config=resolved_config,
    )
    return RLPolicyScore(
        candidate_name=candidate.name,
        total_reward=total_reward,
        average_reward=average_reward,
        dangerous_decision_rate=dangerous_rate,
        no_trade_rate=no_trade_rate,
        correct_block_rate=correct_block_rate,
        final_score=final_score,
        transitions_evaluated=transitions_count,
        accepted_decisions=accepted_count,
        blocked_decisions=blocked_count,
        reduced_risk_decisions=reduced_count,
        risk_notes=tuple(dict.fromkeys(risk_notes)),
    )


def run_rl_playground_experiment(
    dataset: OfflineLearningDataset,
    candidates: tuple[RLPolicyCandidate, ...] | list[RLPolicyCandidate] | None = None,
    config: RLExperimentConfig | None = None,
) -> RLPlaygroundResult:
    """Run an offline playground experiment with simple policy candidates."""
    resolved_config = config or RLExperimentConfig()
    resolved_candidates = tuple(candidates) if candidates is not None else _default_candidates()
    episodes = tuple(
        RLTrainingEpisode(
            candidate_name=candidate.name,
            dataset_name=dataset.name,
            transitions_count=len(dataset.transitions),
            policy_score=evaluate_policy_candidate(candidate, dataset, resolved_config),
        )
        for candidate in resolved_candidates
    )
    ranked = rank_policy_candidates(tuple(episode.policy_score for episode in episodes))
    best = ranked[0] if ranked else None
    return RLPlaygroundResult(
        config=resolved_config,
        dataset=dataset,
        candidates=resolved_candidates,
        episodes=episodes,
        ranked_scores=ranked,
        best_policy=best,
        safety_notes=(
            "Offline playground only; no neural network training is performed.",
            "No broker, external ML, market API, NinjaTrader, Alpaca, Binance, Rithmic or Tradovate connection is used.",
            "No real order is sent.",
        ),
    )


def rank_policy_candidates(scores: tuple[RLPolicyScore, ...] | list[RLPolicyScore]) -> tuple[RLPolicyScore, ...]:
    """Rank policy candidates by final score, then safety."""
    return tuple(
        sorted(
            scores,
            key=lambda score: (
                score.final_score,
                -score.dangerous_decision_rate,
                score.correct_block_rate,
                score.average_reward,
            ),
            reverse=True,
        )
    )


def render_rl_playground_markdown(result: RLPlaygroundResult) -> str:
    """Render the offline playground result as Markdown."""
    best = result.best_policy
    lines = [
        "# RL Training Playground",
        "",
        "## Resume experience",
        "",
        f"- Experiment: {result.config.experiment_name}",
        f"- Dataset: {result.dataset.name}",
        f"- Transitions: {len(result.dataset.transitions)}",
        "",
        "## Politiques testees",
        "",
        *_candidate_lines(result.candidates),
        "",
        "## Meilleure politique",
        "",
        f"- Policy: {best.candidate_name if best is not None else 'None'}",
        f"- Final score: {best.final_score if best is not None else 0}/100",
        "",
        "## Scores",
        "",
        "| Policy | Final | Total reward | Avg reward | Dangerous rate | No-trade rate | Correct block rate |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        *_score_lines(result.ranked_scores),
        "",
        "## Risques detectes",
        "",
        *_risk_lines(result.ranked_scores),
        "",
        "## Limites",
        "",
        "- This playground evaluates fixed heuristic candidates on an offline dataset only.",
        "- It does not train a neural network, fit a statistical model, call external ML, or execute orders.",
        "",
        "## Prochaines etapes RL safe",
        "",
        "- Increase dataset coverage before any future offline policy learning.",
        "- Keep dangerous decisions labeled and reviewed before using them as policy targets.",
        "- Preserve broker/API isolation until a separate explicit safety phase is approved.",
        "",
    ]
    return "\n".join(lines)


def _default_candidates() -> tuple[RLPolicyCandidate, ...]:
    return (
        conservative_threshold_policy(),
        balanced_threshold_policy(),
        aggressive_threshold_policy(),
        no_trade_high_risk_policy(),
        long_only_safe_policy(),
    )


def _candidate_decision(candidate: RLPolicyCandidate, transition: LearningTransition) -> str:
    state = transition.state
    context_score = state.context_score if state.context_score is not None else 0
    behavior = set(state.behavior_classification)
    high_risk_state = (
        context_score < candidate.min_context_score
        or state.market_regime in {"NEWS_RISK", "DEAD_MARKET"}
        or state.volatility_regime == "EXTREME"
        or (candidate.block_high_risk and context_score < 60)
    )
    if candidate.block_revenge_trading and "REVENGE_TRADING_PROBABLE" in behavior:
        return _BLOCK
    if candidate.block_overtrading and "OVERTRADING" in behavior:
        return _BLOCK
    if candidate.long_only and _looks_short_or_sell(transition):
        return _BLOCK
    if high_risk_state and not candidate.aggressive_approval:
        return _BLOCK
    if context_score < candidate.reduce_risk_below_score:
        return _REDUCE_RISK
    return _APPROVE


def _transition_reward(transition: LearningTransition) -> int:
    reward = transition.reward
    if reward is None:
        return 0
    if reward.normalized_reward is not None:
        return reward.normalized_reward - 50
    if reward.total_reward is not None:
        return reward.total_reward
    return 0


def _dangerous_transition(transition: LearningTransition) -> bool:
    state = transition.state
    reward = transition.reward
    action = transition.action
    return bool(
        (reward is not None and reward.reward_label == "DANGEROUS_DECISION")
        or (state.context_score is not None and state.context_score < 40)
        or state.market_regime in {"NEWS_RISK", "DEAD_MARKET"}
        or state.volatility_regime == "EXTREME"
        or "REVENGE_TRADING_PROBABLE" in state.behavior_classification
        or (action.approved and action.semi_auto_decision == "APPROVE_TRADE" and state.context_score is not None and state.context_score < 60)
    )


def _target_no_trade(transition: LearningTransition) -> bool:
    action = transition.action
    return bool(action.blocked or action.stop_session or action.semi_auto_decision in {"BLOCK_TRADE", "STOP_SESSION", "REVIEW_ONLY"})


def _looks_short_or_sell(transition: LearningTransition) -> bool:
    action_text = " ".join(
        value or ""
        for value in (
            transition.action.policy_name,
            transition.action.semi_auto_decision,
            transition.action.paper_action,
            transition.state.strategy_name,
        )
    ).upper()
    return "SHORT" in action_text or "SELL" in action_text


def _final_score(
    *,
    average_reward: float,
    dangerous_rate: float,
    correct_block_rate: float,
    no_trade_rate: float,
    config: RLExperimentConfig,
) -> int:
    score = 50 + average_reward
    score += correct_block_rate * 20
    score -= dangerous_rate * config.dangerous_decision_penalty
    if no_trade_rate > 0.75:
        score -= 8
    return _clamp(score)


def _candidate_lines(candidates: tuple[RLPolicyCandidate, ...]) -> list[str]:
    if not candidates:
        return ["- None"]
    return [
        (
            f"- {candidate.name}: min_context={candidate.min_context_score}, "
            f"reduce_below={candidate.reduce_risk_below_score}, long_only={candidate.long_only}"
        )
        for candidate in candidates
    ]


def _score_lines(scores: tuple[RLPolicyScore, ...]) -> list[str]:
    if not scores:
        return ["| None | 0 | 0 | 0.00 | 0.00 | 0.00 | 0.00 |"]
    return [
        (
            f"| {score.candidate_name} | {score.final_score} | {score.total_reward} | "
            f"{score.average_reward:.2f} | {score.dangerous_decision_rate:.2f} | "
            f"{score.no_trade_rate:.2f} | {score.correct_block_rate:.2f} |"
        )
        for score in scores
    ]


def _risk_lines(scores: tuple[RLPolicyScore, ...]) -> list[str]:
    risks = tuple(dict.fromkeys(note for score in scores for note in score.risk_notes))
    if not risks:
        return ["- None"]
    return [f"- {risk}" for risk in risks]


def _rate(count: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round(count / total, 4)


def _clamp(value: int | float) -> int:
    return max(0, min(100, int(round(value))))


__all__ = [
    "aggressive_threshold_policy",
    "balanced_threshold_policy",
    "conservative_threshold_policy",
    "evaluate_policy_candidate",
    "long_only_safe_policy",
    "no_trade_high_risk_policy",
    "rank_policy_candidates",
    "render_rl_playground_markdown",
    "run_rl_playground_experiment",
]
