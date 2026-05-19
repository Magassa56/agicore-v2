"""Models for offline trading policy evaluation."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .adaptive_memory_models import TraderMemoryProfile
from .behavior_models import BehaviorAnalysisResult
from .context_scoring_models import ContextScoringResult
from .market_regime_models import MarketRegimeAnalysis
from .paper_execution_models import PaperExecutionResult
from .paper_trading_models import PaperOrderRequest
from .reward_models import RewardEvaluationResult
from .semi_auto_decision_models import SemiAutoDecisionResult
from .session_replay_models import SessionReplayResult
from .strategy_dna_models import StrategyDNA


class TradingPolicy(StrEnum):
    """Supported deterministic offline policy profiles."""

    CONSERVATIVE = "CONSERVATIVE"
    BALANCED = "BALANCED"
    AGGRESSIVE = "AGGRESSIVE"
    LONG_ONLY_STRICT = "LONG_ONLY_STRICT"
    NO_TRADE_ON_HIGH_RISK = "NO_TRADE_ON_HIGH_RISK"


@dataclass(frozen=True)
class PolicyRule:
    """Decision thresholds and safety behavior for one policy."""

    policy: TradingPolicy
    min_context_score: int
    reduce_risk_below_score: int
    block_high_risk_context: bool
    allow_high_risk_override: bool
    reduce_size_on_caution: bool
    block_revenge_trading: bool
    block_overtrading: bool
    long_only: bool = False


@dataclass(frozen=True)
class PolicyEvaluationScenario:
    """One offline scenario evaluated by a deterministic policy."""

    name: str
    context_score: ContextScoringResult
    order_request: PaperOrderRequest
    market_regime: MarketRegimeAnalysis | None = None
    behavior_result: BehaviorAnalysisResult | None = None
    memory_profile: TraderMemoryProfile | None = None
    strategy_dna: StrategyDNA | None = None
    session_replay_result: SessionReplayResult | None = None


@dataclass(frozen=True)
class PolicyEvaluationResult:
    """Aggregated result for one policy across one or more scenarios."""

    policy: TradingPolicy
    rule: PolicyRule
    total_reward: int
    normalized_reward: int
    accepted_trades: int
    blocked_trades: int
    reduced_risk_trades: int
    dangerous_decisions: int
    average_context_score: float
    average_reward: float
    best_policy: bool
    best_policy_reason: str
    scenario_count: int
    semi_auto_decisions: tuple[SemiAutoDecisionResult, ...]
    paper_execution_results: tuple[PaperExecutionResult, ...]
    reward_results: tuple[RewardEvaluationResult, ...]
    risk_notes: tuple[str, ...]


@dataclass(frozen=True)
class PolicyComparisonResult:
    """Comparison output for multiple policy evaluations."""

    results: tuple[PolicyEvaluationResult, ...]
    best_policy: TradingPolicy | None
    best_policy_reason: str
    recommendation: str
    risks_detected: tuple[str, ...]


__all__ = [
    "PolicyComparisonResult",
    "PolicyEvaluationResult",
    "PolicyEvaluationScenario",
    "PolicyRule",
    "TradingPolicy",
]
