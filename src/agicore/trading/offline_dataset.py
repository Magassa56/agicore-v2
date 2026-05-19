"""Offline learning dataset builder for AGIcore Trading."""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from statistics import mean
from typing import Any, Iterable

from .adaptive_memory_models import TraderMemoryProfile
from .behavior_models import BehaviorAnalysisResult
from .context_scoring_models import ContextScoringResult, TradeContextDecision
from .market_regime_models import MarketRegimeAnalysis
from .offline_dataset_models import (
    DatasetQualityReport,
    LearningAction,
    LearningReward,
    LearningState,
    LearningTransition,
    OfflineLearningDataset,
)
from .paper_execution_models import PaperExecutionDecision, PaperExecutionResult
from .policy_evaluation_models import PolicyEvaluationResult, TradingPolicy
from .reward_models import RewardEvaluationResult, RewardLabel
from .semi_auto_decision_models import SemiAutoDecision, SemiAutoDecisionResult
from .strategy_dna_models import StrategyDNA


def build_learning_transition(
    *,
    state: LearningState | None = None,
    action: LearningAction | None = None,
    reward: LearningReward | None = None,
    next_state: LearningState | None = None,
    context_score: ContextScoringResult | None = None,
    market_regime: MarketRegimeAnalysis | None = None,
    behavior_result: BehaviorAnalysisResult | None = None,
    memory_profile: TraderMemoryProfile | None = None,
    strategy_dna: StrategyDNA | None = None,
    hour_of_day: int | None = None,
    session_trade_count: int | None = None,
    policy_name: str | TradingPolicy | None = None,
    semi_auto_decision: SemiAutoDecisionResult | None = None,
    paper_execution_result: PaperExecutionResult | None = None,
    reward_result: RewardEvaluationResult | None = None,
    next_context_score: ContextScoringResult | None = None,
    next_market_regime: MarketRegimeAnalysis | None = None,
    next_behavior_result: BehaviorAnalysisResult | None = None,
    next_memory_profile: TraderMemoryProfile | None = None,
    next_strategy_dna: StrategyDNA | None = None,
    next_hour_of_day: int | None = None,
    next_session_trade_count: int | None = None,
    source_id: str | None = None,
) -> LearningTransition:
    """Build one deterministic offline transition. No model is trained here."""
    resolved_state = state or _build_state(
        context_score=context_score,
        market_regime=market_regime,
        behavior_result=behavior_result,
        memory_profile=memory_profile,
        strategy_dna=strategy_dna,
        hour_of_day=hour_of_day,
        session_trade_count=session_trade_count,
    )
    resolved_action = action or _build_action(
        policy_name=policy_name,
        semi_auto_decision=semi_auto_decision,
        paper_execution_result=paper_execution_result,
    )
    resolved_reward = reward if reward is not None else _build_reward(reward_result)
    resolved_next_state = next_state
    if resolved_next_state is None and any(
        item is not None
        for item in (
            next_context_score,
            next_market_regime,
            next_behavior_result,
            next_memory_profile,
            next_strategy_dna,
            next_hour_of_day,
            next_session_trade_count,
        )
    ):
        resolved_next_state = _build_state(
            context_score=next_context_score,
            market_regime=next_market_regime,
            behavior_result=next_behavior_result,
            memory_profile=next_memory_profile,
            strategy_dna=next_strategy_dna,
            hour_of_day=next_hour_of_day,
            session_trade_count=next_session_trade_count,
        )
    return LearningTransition(
        state=resolved_state,
        action=resolved_action,
        reward=resolved_reward,
        next_state=resolved_next_state,
        source_id=source_id,
    )


def build_offline_learning_dataset(
    transitions: Iterable[LearningTransition] = (),
    *,
    policy_results: Iterable[PolicyEvaluationResult] = (),
    name: str = "agicore_offline_learning_dataset",
    version: str = "1.0",
    description: str = "Offline dataset for future policy evaluation; no RL training is performed.",
) -> OfflineLearningDataset:
    """Build an offline dataset from explicit transitions and policy results."""
    built = list(transitions)
    for policy_result in policy_results:
        built.extend(_transitions_from_policy_result(policy_result))
    return OfflineLearningDataset(
        transitions=tuple(built),
        name=name,
        version=version,
        description=description,
    )


def evaluate_dataset_quality(dataset: OfflineLearningDataset) -> DatasetQualityReport:
    """Evaluate basic dataset quality using deterministic offline checks."""
    transitions = dataset.transitions
    rewards = [transition.reward.normalized_reward for transition in transitions if transition.reward is not None and transition.reward.normalized_reward is not None]
    missing_reward = sum(1 for transition in transitions if transition.reward is None or transition.reward.normalized_reward is None)
    missing_next = sum(1 for transition in transitions if transition.next_state is None)
    dangerous = sum(1 for transition in transitions if _is_dangerous_transition(transition))
    no_trade = sum(1 for transition in transitions if _is_no_trade_transition(transition))
    unique_states = {json.dumps(_state_payload(transition.state), sort_keys=True) for transition in transitions}
    unique_actions = {json.dumps(asdict(transition.action), sort_keys=True) for transition in transitions}
    average_reward = round(mean(rewards), 2) if rewards else 0.0

    score = 100
    if not transitions:
        score = 0
    score -= min(35, missing_reward * 10)
    score -= min(25, missing_next * 5)
    score -= min(25, dangerous * 8)
    if transitions and len(unique_states) < max(1, len(transitions) // 2):
        score -= 10
    if transitions and len(unique_actions) < 2:
        score -= 5
    score = _clamp(score)
    warnings = _quality_warnings(
        transitions_count=len(transitions),
        missing_reward=missing_reward,
        missing_next=missing_next,
        dangerous=dangerous,
        unique_states_count=len(unique_states),
        unique_actions_count=len(unique_actions),
    )
    return DatasetQualityReport(
        transitions_count=len(transitions),
        unique_states_count=len(unique_states),
        unique_actions_count=len(unique_actions),
        average_reward=average_reward,
        dangerous_decision_count=dangerous,
        no_trade_count=no_trade,
        missing_reward_count=missing_reward,
        missing_next_state_count=missing_next,
        quality_score=score,
        warnings=warnings,
    )


def render_offline_dataset_markdown(
    dataset: OfflineLearningDataset,
    quality_report: DatasetQualityReport | None = None,
) -> str:
    """Render an offline learning dataset summary as Markdown."""
    report = quality_report or evaluate_dataset_quality(dataset)
    lines = [
        "# Offline Learning Dataset",
        "",
        "## Resume dataset",
        "",
        f"- Name: {dataset.name}",
        f"- Version: {dataset.version}",
        f"- Transitions: {report.transitions_count}",
        "",
        "## Qualite dataset",
        "",
        f"- Quality score: {report.quality_score}/100",
        f"- Unique states: {report.unique_states_count}",
        f"- Unique actions: {report.unique_actions_count}",
        f"- Average reward: {report.average_reward:.2f}",
        "",
        "## Couverture transitions",
        "",
        f"- Dangerous decisions: {report.dangerous_decision_count}",
        f"- No-trade actions: {report.no_trade_count}",
        f"- Missing rewards: {report.missing_reward_count}",
        f"- Missing next states: {report.missing_next_state_count}",
        "",
        "## Avertissements",
        "",
        *_bullet_lines(report.warnings),
        "",
        "## Utilisation future pour Offline RL",
        "",
        "- This dataset stores offline state-action-reward-next_state transitions only.",
        "- No model training, external ML, broker/API connection, or real order execution is performed.",
        "",
    ]
    return "\n".join(lines)


def save_offline_learning_dataset(path: str | Path, dataset: OfflineLearningDataset) -> None:
    """Save an offline learning dataset as simple JSON."""
    Path(path).write_text(json.dumps(_dataset_to_payload(dataset), indent=2, sort_keys=True), encoding="utf-8")


def load_offline_learning_dataset(path: str | Path) -> OfflineLearningDataset:
    """Load an offline learning dataset saved by save_offline_learning_dataset."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return OfflineLearningDataset(
        name=str(payload.get("name", "agicore_offline_learning_dataset")),
        version=str(payload.get("version", "1.0")),
        description=str(payload.get("description", "")),
        transitions=tuple(_transition_from_payload(item) for item in payload.get("transitions", ())),
    )


def _build_state(
    *,
    context_score: ContextScoringResult | None,
    market_regime: MarketRegimeAnalysis | None,
    behavior_result: BehaviorAnalysisResult | None,
    memory_profile: TraderMemoryProfile | None,
    strategy_dna: StrategyDNA | None,
    hour_of_day: int | None,
    session_trade_count: int | None,
) -> LearningState:
    return LearningState(
        context_score=context_score.global_score if context_score is not None else None,
        market_regime=_enum_value(market_regime.primary_regime) if market_regime is not None else None,
        volatility_regime=_enum_value(market_regime.volatility) if market_regime is not None else None,
        behavior_classification=tuple(_enum_value(item) for item in behavior_result.classifications) if behavior_result is not None else (),
        discipline_score=behavior_result.scores.discipline_score if behavior_result is not None else None,
        emotional_risk_score=behavior_result.scores.emotional_risk_score if behavior_result is not None else None,
        memory_risk_flags=_memory_flags(memory_profile),
        strategy_name=strategy_dna.name if strategy_dna is not None else None,
        hour_of_day=hour_of_day,
        session_trade_count=session_trade_count,
    )


def _build_action(
    *,
    policy_name: str | TradingPolicy | None,
    semi_auto_decision: SemiAutoDecisionResult | None,
    paper_execution_result: PaperExecutionResult | None,
) -> LearningAction:
    decision = semi_auto_decision.decision if semi_auto_decision is not None else None
    paper_action = paper_execution_result.decision if paper_execution_result is not None else None
    return LearningAction(
        policy_name=_enum_value(policy_name) if policy_name is not None else None,
        semi_auto_decision=_enum_value(decision) if decision is not None else None,
        paper_action=_enum_value(paper_action) if paper_action is not None else None,
        approved=decision in {SemiAutoDecision.APPROVE_TRADE, SemiAutoDecision.APPROVE_REDUCED_RISK},
        reduced_risk=decision == SemiAutoDecision.APPROVE_REDUCED_RISK,
        blocked=decision in {SemiAutoDecision.BLOCK_TRADE, SemiAutoDecision.REVIEW_ONLY},
        stop_session=decision == SemiAutoDecision.STOP_SESSION,
    )


def _build_reward(reward_result: RewardEvaluationResult | None) -> LearningReward | None:
    if reward_result is None:
        return None
    breakdown = reward_result.breakdown
    risk_penalties = sum(
        component.value
        for component in (
            breakdown.drawdown_penalty,
            breakdown.rule_violation_penalty,
            breakdown.overtrading_penalty,
            breakdown.revenge_trading_penalty,
        )
        if component.value < 0
    )
    return LearningReward(
        total_reward=reward_result.total_reward,
        normalized_reward=reward_result.normalized_reward,
        reward_label=reward_result.reward_label.value,
        pnl_reward=breakdown.pnl_reward.value,
        discipline_reward=breakdown.discipline_reward.value,
        risk_penalties=risk_penalties,
    )


def _transitions_from_policy_result(policy_result: PolicyEvaluationResult) -> tuple[LearningTransition, ...]:
    transitions: list[LearningTransition] = []
    for index, (semi, paper, reward) in enumerate(
        zip(
            policy_result.semi_auto_decisions,
            policy_result.paper_execution_results,
            policy_result.reward_results,
            strict=True,
        )
    ):
        transition = build_learning_transition(
            state=LearningState(context_score=semi.context_score),
            action=_build_action(
                policy_name=policy_result.policy,
                semi_auto_decision=semi,
                paper_execution_result=paper,
            ),
            reward=_build_reward(reward),
            next_state=LearningState(context_score=semi.context_score, session_trade_count=index + 1),
            source_id=f"{policy_result.policy.value}:{index}",
        )
        transitions.append(transition)
    return tuple(transitions)


def _memory_flags(memory_profile: TraderMemoryProfile | None) -> tuple[str, ...]:
    if memory_profile is None:
        return ()
    flags: list[str] = []
    flags.extend(_enum_value(item) for item in memory_profile.recurring_behavior_classes)
    flags.extend(_enum_value(item) for item in memory_profile.recurring_patterns)
    flags.extend(f"dangerous_hour:{hour}" for hour in memory_profile.recurring_dangerous_hours)
    flags.extend(f"worst_context:{context}" for context in memory_profile.worst_contexts)
    return tuple(dict.fromkeys(flags))


def _is_dangerous_transition(transition: LearningTransition) -> bool:
    reward = transition.reward
    action = transition.action
    state = transition.state
    return bool(
        (reward is not None and reward.reward_label == RewardLabel.DANGEROUS_DECISION.value)
        or (action.approved and state.context_score is not None and state.context_score < 40)
        or (action.approved and state.market_regime in {"NEWS_RISK", "DEAD_MARKET"})
        or (action.approved and "REVENGE_TRADING_PROBABLE" in state.behavior_classification)
    )


def _is_no_trade_transition(transition: LearningTransition) -> bool:
    action = transition.action
    return bool(action.blocked or action.stop_session or action.semi_auto_decision == SemiAutoDecision.BLOCK_TRADE.value)


def _quality_warnings(
    *,
    transitions_count: int,
    missing_reward: int,
    missing_next: int,
    dangerous: int,
    unique_states_count: int,
    unique_actions_count: int,
) -> tuple[str, ...]:
    warnings: list[str] = []
    if transitions_count == 0:
        warnings.append("Dataset is empty.")
    if missing_reward:
        warnings.append("Some transitions have no reward target.")
    if missing_next:
        warnings.append("Some transitions have no next_state.")
    if dangerous:
        warnings.append("Dangerous decisions are present and should be reviewed before policy learning.")
    if transitions_count and unique_states_count < max(1, transitions_count // 2):
        warnings.append("State diversity is low.")
    if transitions_count and unique_actions_count < 2:
        warnings.append("Action diversity is low.")
    return tuple(warnings or ("Dataset is suitable for offline analysis only.",))


def _dataset_to_payload(dataset: OfflineLearningDataset) -> dict[str, Any]:
    return {
        "name": dataset.name,
        "version": dataset.version,
        "description": dataset.description,
        "transitions": [_transition_to_payload(transition) for transition in dataset.transitions],
    }


def _transition_to_payload(transition: LearningTransition) -> dict[str, Any]:
    return {
        "state": asdict(transition.state),
        "action": asdict(transition.action),
        "reward": asdict(transition.reward) if transition.reward is not None else None,
        "next_state": asdict(transition.next_state) if transition.next_state is not None else None,
        "source_id": transition.source_id,
    }


def _transition_from_payload(payload: dict[str, Any]) -> LearningTransition:
    return LearningTransition(
        state=_state_from_payload(payload["state"]),
        action=_action_from_payload(payload["action"]),
        reward=_reward_from_payload(payload.get("reward")),
        next_state=_state_from_payload(payload["next_state"]) if payload.get("next_state") is not None else None,
        source_id=payload.get("source_id"),
    )


def _state_from_payload(payload: dict[str, Any]) -> LearningState:
    return LearningState(
        context_score=_optional_int(payload.get("context_score")),
        market_regime=payload.get("market_regime"),
        volatility_regime=payload.get("volatility_regime"),
        behavior_classification=tuple(str(item) for item in payload.get("behavior_classification", ())),
        discipline_score=_optional_int(payload.get("discipline_score")),
        emotional_risk_score=_optional_int(payload.get("emotional_risk_score")),
        memory_risk_flags=tuple(str(item) for item in payload.get("memory_risk_flags", ())),
        strategy_name=payload.get("strategy_name"),
        hour_of_day=_optional_int(payload.get("hour_of_day")),
        session_trade_count=_optional_int(payload.get("session_trade_count")),
    )


def _action_from_payload(payload: dict[str, Any]) -> LearningAction:
    return LearningAction(
        policy_name=payload.get("policy_name"),
        semi_auto_decision=payload.get("semi_auto_decision"),
        paper_action=payload.get("paper_action"),
        approved=bool(payload.get("approved", False)),
        reduced_risk=bool(payload.get("reduced_risk", False)),
        blocked=bool(payload.get("blocked", False)),
        stop_session=bool(payload.get("stop_session", False)),
    )


def _reward_from_payload(payload: dict[str, Any] | None) -> LearningReward | None:
    if payload is None:
        return None
    return LearningReward(
        total_reward=_optional_int(payload.get("total_reward")),
        normalized_reward=_optional_int(payload.get("normalized_reward")),
        reward_label=payload.get("reward_label"),
        pnl_reward=_optional_int(payload.get("pnl_reward")),
        discipline_reward=_optional_int(payload.get("discipline_reward")),
        risk_penalties=_optional_int(payload.get("risk_penalties")),
    )


def _state_payload(state: LearningState) -> dict[str, Any]:
    return asdict(state)


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    return int(value)


def _enum_value(value: Any) -> str:
    return value.value if hasattr(value, "value") else str(value)


def _clamp(value: int | float) -> int:
    return max(0, min(100, int(round(value))))


__all__ = [
    "build_learning_transition",
    "build_offline_learning_dataset",
    "evaluate_dataset_quality",
    "load_offline_learning_dataset",
    "render_offline_dataset_markdown",
    "save_offline_learning_dataset",
]
