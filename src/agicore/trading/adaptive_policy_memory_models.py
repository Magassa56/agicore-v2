"""Models for offline adaptive policy memory."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class PolicyMemoryRecommendation(StrEnum):
    """Recommendation emitted for a policy based on offline memory."""

    PRIORITIZE_POLICY = "PRIORITIZE_POLICY"
    KEEP_POLICY = "KEEP_POLICY"
    REDUCE_POLICY_USAGE = "REDUCE_POLICY_USAGE"
    DISABLE_POLICY = "DISABLE_POLICY"
    REQUIRE_REVIEW = "REQUIRE_REVIEW"


@dataclass(frozen=True)
class PolicyContextSignature:
    """Compact market/behavior context used to compare policies."""

    market_regime: str | None = None
    behavior_classification: tuple[str, ...] = ()
    context_score_bucket: str | None = None
    strategy_name: str | None = None


@dataclass(frozen=True)
class PolicyPerformanceSnapshot:
    """One immutable performance snapshot for a policy."""

    policy_name: str
    reward: float
    normalized_reward: int
    average_context_score: float
    dangerous_decision_rate: float
    blocked_trade_rate: float
    accepted_trade_rate: float
    reduced_risk_rate: float
    context_signature: PolicyContextSignature
    source: str = "policy_evaluation"


@dataclass(frozen=True)
class PolicyMemoryEntry:
    """Aggregated offline memory for one policy."""

    policy_name: str
    total_evaluations: int
    average_reward: float
    average_context_score: float
    dangerous_decision_rate: float
    blocked_trade_rate: float
    accepted_trade_rate: float
    reduced_risk_rate: float
    confidence_score: int
    recommendation: PolicyMemoryRecommendation
    best_contexts: tuple[str, ...]
    worst_contexts: tuple[str, ...]
    regime_performance: dict[str, float] = field(default_factory=dict)
    behavior_context_performance: dict[str, float] = field(default_factory=dict)
    last_updated: str = ""


@dataclass(frozen=True)
class AdaptivePolicyMemory:
    """Offline adaptive memory across policy candidates."""

    entries: dict[str, PolicyMemoryEntry] = field(default_factory=dict)
    snapshots: tuple[PolicyPerformanceSnapshot, ...] = ()
    disabled_policies: tuple[str, ...] = ()
    last_updated: str = ""


__all__ = [
    "AdaptivePolicyMemory",
    "PolicyContextSignature",
    "PolicyMemoryEntry",
    "PolicyMemoryRecommendation",
    "PolicyPerformanceSnapshot",
]
