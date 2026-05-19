"""Models for offline trading reward evaluation."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .adaptive_memory_models import TraderMemoryProfile
from .behavior_models import BehaviorAnalysisResult
from .context_scoring_models import ContextScoringResult
from .market_regime_models import MarketRegimeAnalysis
from .paper_execution_models import PaperExecutionResult
from .semi_auto_decision_models import SemiAutoDecisionResult
from .session_replay_models import SessionReplayResult
from .strategy_dna_models import StrategyDNA
from .trade_journal_models import JournalAnalysisResult, TradeJournalEntry


class RewardLabel(StrEnum):
    """Human-readable reward quality label."""

    EXCELLENT_DECISION = "EXCELLENT_DECISION"
    GOOD_DECISION = "GOOD_DECISION"
    ACCEPTABLE = "ACCEPTABLE"
    BAD_DECISION = "BAD_DECISION"
    DANGEROUS_DECISION = "DANGEROUS_DECISION"


@dataclass(frozen=True)
class RewardComponent:
    """Single signed reward component."""

    name: str
    value: int
    reason: str


@dataclass(frozen=True)
class RewardBreakdown:
    """Reward components normalized to the -100..100 range."""

    pnl_reward: RewardComponent
    risk_adjusted_reward: RewardComponent
    discipline_reward: RewardComponent
    context_alignment_reward: RewardComponent
    behavior_reward: RewardComponent
    drawdown_penalty: RewardComponent
    rule_violation_penalty: RewardComponent
    overtrading_penalty: RewardComponent
    revenge_trading_penalty: RewardComponent
    strategy_compliance_reward: RewardComponent
    memory_improvement_reward: RewardComponent


@dataclass(frozen=True)
class RewardEvaluationInput:
    """Optional inputs for the offline reward function."""

    paper_execution_result: PaperExecutionResult | None = None
    semi_auto_decision: SemiAutoDecisionResult | None = None
    context_score: ContextScoringResult | None = None
    session_replay_result: SessionReplayResult | None = None
    behavior_result: BehaviorAnalysisResult | None = None
    memory_profile: TraderMemoryProfile | None = None
    market_regime: MarketRegimeAnalysis | None = None
    strategy_dna: StrategyDNA | None = None
    journal_entries: tuple[TradeJournalEntry, ...] = ()
    journal_result: JournalAnalysisResult | None = None


@dataclass(frozen=True)
class RewardEvaluationResult:
    """Final offline reward evaluation output."""

    total_reward: int
    normalized_reward: int
    reward_label: RewardLabel
    breakdown: RewardBreakdown
    learning_notes: tuple[str, ...]
    improvement_actions: tuple[str, ...]


__all__ = [
    "RewardBreakdown",
    "RewardComponent",
    "RewardEvaluationInput",
    "RewardEvaluationResult",
    "RewardLabel",
]
