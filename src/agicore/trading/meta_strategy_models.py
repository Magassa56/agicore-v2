"""Models for offline meta strategy selection."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .adaptive_policy_memory_models import AdaptivePolicyMemory
from .behavior_models import BehaviorAnalysisResult
from .context_scoring_models import ContextScoringResult
from .market_regime_models import MarketRegimeAnalysis
from .playbook_models import TraderProfile
from .policy_evaluation_models import PolicyEvaluationResult
from .safe_rl_models import SafeRLExperimentResult
from .semi_auto_decision_models import SemiAutoDecisionResult
from .strategy_dna_models import StrategyDNA


class MetaStrategyDecision(StrEnum):
    """Final offline meta-strategy selector decision."""

    SELECT_POLICY = "SELECT_POLICY"
    SELECT_REDUCED_RISK_POLICY = "SELECT_REDUCED_RISK_POLICY"
    REQUIRE_REVIEW = "REQUIRE_REVIEW"
    BLOCK_ALL_POLICIES = "BLOCK_ALL_POLICIES"
    FALLBACK_TO_CONSERVATIVE = "FALLBACK_TO_CONSERVATIVE"
    NO_STRATEGY = "NO_STRATEGY"


class MetaStrategyReason(StrEnum):
    """Reason codes emitted by the selector."""

    MEMORY_MATCH = "MEMORY_MATCH"
    HIGH_AVERAGE_REWARD = "HIGH_AVERAGE_REWARD"
    HIGH_CONFIDENCE = "HIGH_CONFIDENCE"
    DANGEROUS_POLICY = "DANGEROUS_POLICY"
    REGIME_INCOMPATIBLE = "REGIME_INCOMPATIBLE"
    SAFE_RL_BLOCKED = "SAFE_RL_BLOCKED"
    BEHAVIOR_RISK_HIGH = "BEHAVIOR_RISK_HIGH"
    STRATEGY_DNA_COMPATIBLE = "STRATEGY_DNA_COMPATIBLE"
    FALLBACK_CONSERVATIVE = "FALLBACK_CONSERVATIVE"
    NO_TRADE_CONTEXT = "NO_TRADE_CONTEXT"
    STOP_SESSION = "STOP_SESSION"
    DANGEROUS_MARKET = "DANGEROUS_MARKET"


@dataclass(frozen=True)
class MetaStrategyCandidate:
    """Rankable policy/strategy candidate."""

    policy_name: str
    score: int
    confidence_score: int
    average_reward: float
    dangerous_decision_rate: float
    compatible_with_strategy: bool
    disabled: bool = False
    reasons: tuple[MetaStrategyReason, ...] = ()
    risk_notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class MetaStrategySelectionInput:
    """Inputs consumed by the offline meta-strategy selector."""

    adaptive_policy_memory: AdaptivePolicyMemory | None = None
    policy_results: tuple[PolicyEvaluationResult, ...] = ()
    safe_rl_result: SafeRLExperimentResult | None = None
    context_score: ContextScoringResult | None = None
    market_regime: MarketRegimeAnalysis | None = None
    behavior_result: BehaviorAnalysisResult | None = None
    semi_auto_decision: SemiAutoDecisionResult | None = None
    strategy_dna: StrategyDNA | None = None
    trader_profile: TraderProfile | None = None


@dataclass(frozen=True)
class MetaStrategySelectionResult:
    """Final selector output."""

    selected_policy_name: str | None
    decision: MetaStrategyDecision
    confidence_score: int
    ranked_candidates: tuple[MetaStrategyCandidate, ...]
    reasons: tuple[MetaStrategyReason, ...]
    risk_notes: tuple[str, ...]
    required_manual_review: bool
    recommendation: str


__all__ = [
    "MetaStrategyCandidate",
    "MetaStrategyDecision",
    "MetaStrategyReason",
    "MetaStrategySelectionInput",
    "MetaStrategySelectionResult",
]
