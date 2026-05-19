"""Models for the offline RL training playground."""
from __future__ import annotations

from dataclasses import dataclass

from .offline_dataset_models import OfflineLearningDataset


@dataclass(frozen=True)
class RLExperimentConfig:
    """Configuration for an offline playground run. No model is trained."""

    experiment_name: str = "agicore_rl_playground"
    minimum_context_score: int = 60
    correct_block_bonus: int = 12
    wrong_approval_penalty: int = 25
    no_trade_penalty: int = 4
    dangerous_decision_penalty: int = 30


@dataclass(frozen=True)
class RLPolicyCandidate:
    """Simple deterministic policy candidate for offline evaluation."""

    name: str
    min_context_score: int
    reduce_risk_below_score: int
    block_high_risk: bool
    block_revenge_trading: bool
    block_overtrading: bool
    long_only: bool = False
    aggressive_approval: bool = False


@dataclass(frozen=True)
class RLPolicyScore:
    """Aggregated score for one policy candidate."""

    candidate_name: str
    total_reward: int
    average_reward: float
    dangerous_decision_rate: float
    no_trade_rate: float
    correct_block_rate: float
    final_score: int
    transitions_evaluated: int
    accepted_decisions: int
    blocked_decisions: int
    reduced_risk_decisions: int
    risk_notes: tuple[str, ...]


@dataclass(frozen=True)
class RLTrainingEpisode:
    """One offline episode over a static dataset."""

    candidate_name: str
    dataset_name: str
    transitions_count: int
    policy_score: RLPolicyScore


@dataclass(frozen=True)
class RLPlaygroundResult:
    """Final playground result across policy candidates."""

    config: RLExperimentConfig
    dataset: OfflineLearningDataset
    candidates: tuple[RLPolicyCandidate, ...]
    episodes: tuple[RLTrainingEpisode, ...]
    ranked_scores: tuple[RLPolicyScore, ...]
    best_policy: RLPolicyScore | None
    safety_notes: tuple[str, ...]


__all__ = [
    "RLExperimentConfig",
    "RLPlaygroundResult",
    "RLPolicyCandidate",
    "RLPolicyScore",
    "RLTrainingEpisode",
]
