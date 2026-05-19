"""Models for offline learning dataset construction."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LearningState:
    """Compact offline state vector for future policy learning."""

    context_score: int | None = None
    market_regime: str | None = None
    volatility_regime: str | None = None
    behavior_classification: tuple[str, ...] = ()
    discipline_score: int | None = None
    emotional_risk_score: int | None = None
    memory_risk_flags: tuple[str, ...] = ()
    strategy_name: str | None = None
    hour_of_day: int | None = None
    session_trade_count: int | None = None


@dataclass(frozen=True)
class LearningAction:
    """Offline action representation produced by policy/decision layers."""

    policy_name: str | None = None
    semi_auto_decision: str | None = None
    paper_action: str | None = None
    approved: bool = False
    reduced_risk: bool = False
    blocked: bool = False
    stop_session: bool = False


@dataclass(frozen=True)
class LearningReward:
    """Reward target extracted from the reward function engine."""

    total_reward: int | None = None
    normalized_reward: int | None = None
    reward_label: str | None = None
    pnl_reward: int | None = None
    discipline_reward: int | None = None
    risk_penalties: int | None = None


@dataclass(frozen=True)
class LearningTransition:
    """One state-action-reward-next_state transition."""

    state: LearningState
    action: LearningAction
    reward: LearningReward | None = None
    next_state: LearningState | None = None
    source_id: str | None = None


@dataclass(frozen=True)
class OfflineLearningDataset:
    """Offline-only learning dataset. It does not train any model."""

    transitions: tuple[LearningTransition, ...]
    name: str = "agicore_offline_learning_dataset"
    version: str = "1.0"
    description: str = "Offline dataset for future policy evaluation; no RL training is performed."


@dataclass(frozen=True)
class DatasetQualityReport:
    """Quality metrics for an offline learning dataset."""

    transitions_count: int
    unique_states_count: int
    unique_actions_count: int
    average_reward: float
    dangerous_decision_count: int
    no_trade_count: int
    missing_reward_count: int
    missing_next_state_count: int
    quality_score: int
    warnings: tuple[str, ...]


__all__ = [
    "DatasetQualityReport",
    "LearningAction",
    "LearningReward",
    "LearningState",
    "LearningTransition",
    "OfflineLearningDataset",
]
