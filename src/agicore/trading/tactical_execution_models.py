"""Models for offline Tactical Execution Intelligence."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .context_scoring_models import ContextScoringResult
from .executive_brain_models import ExecutiveBrainResult
from .market_regime_models import MarketRegimeAnalysis
from .paper_execution_models import PaperExecutionResult
from .reward_models import RewardEvaluationResult
from .semi_auto_decision_models import SemiAutoDecisionResult
from .strategic_planning_models import StrategicPlanningResult
from .strategy_dna_models import StrategyDNA
from .trade_journal_models import JournalAnalysisResult, TradeJournalEntry


class TacticalExecutionQuality(StrEnum):
    """Overall tactical execution quality."""

    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    ACCEPTABLE = "ACCEPTABLE"
    WEAK = "WEAK"
    DANGEROUS = "DANGEROUS"
    BLOCKED = "BLOCKED"


class TacticalExecutionSignal(StrEnum):
    """Signals emitted by the tactical execution layer."""

    ENTRY_QUALITY_HIGH = "ENTRY_QUALITY_HIGH"
    ENTRY_QUALITY_LOW = "ENTRY_QUALITY_LOW"
    EXIT_QUALITY_HIGH = "EXIT_QUALITY_HIGH"
    EXIT_QUALITY_LOW = "EXIT_QUALITY_LOW"
    TIMING_GOOD = "TIMING_GOOD"
    TIMING_BAD = "TIMING_BAD"
    VOLATILITY_ALIGNED = "VOLATILITY_ALIGNED"
    VOLATILITY_MISMATCH = "VOLATILITY_MISMATCH"
    FOMO_RISK = "FOMO_RISK"
    CHASE_RISK = "CHASE_RISK"
    HESITATION_RISK = "HESITATION_RISK"
    OVERCONFIDENCE_RISK = "OVERCONFIDENCE_RISK"
    TACTICAL_DISCIPLINE_STRONG = "TACTICAL_DISCIPLINE_STRONG"
    TACTICAL_DISCIPLINE_WEAK = "TACTICAL_DISCIPLINE_WEAK"
    STRATEGY_ALIGNMENT_STRONG = "STRATEGY_ALIGNMENT_STRONG"
    STRATEGY_ALIGNMENT_WEAK = "STRATEGY_ALIGNMENT_WEAK"


@dataclass(frozen=True)
class TacticalScoreBreakdown:
    """Component tactical scores normalized to 0..100."""

    entry_score: int
    exit_score: int
    timing_score: int
    volatility_score: int
    discipline_score: int
    strategy_alignment_score: int
    risk_control_score: int


@dataclass(frozen=True)
class TacticalExecutionInput:
    """Inputs consumed by the offline tactical execution evaluator."""

    context_score: ContextScoringResult | None = None
    market_regime: MarketRegimeAnalysis | None = None
    semi_auto_decision: SemiAutoDecisionResult | None = None
    paper_execution: PaperExecutionResult | None = None
    reward_evaluation: RewardEvaluationResult | None = None
    executive_result: ExecutiveBrainResult | None = None
    strategic_result: StrategicPlanningResult | None = None
    trade_journal_entry: TradeJournalEntry | None = None
    journal_result: JournalAnalysisResult | None = None
    strategy_dna: StrategyDNA | None = None


@dataclass(frozen=True)
class TacticalExecutionEvent:
    """Auditable tactical execution event."""

    quality: TacticalExecutionQuality
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class TacticalExecutionResult:
    """Final tactical execution intelligence result."""

    quality: TacticalExecutionQuality
    global_score: int
    breakdown: TacticalScoreBreakdown
    signals: tuple[TacticalExecutionSignal, ...]
    risks: tuple[str, ...]
    recommendations: tuple[str, ...]
    events: tuple[TacticalExecutionEvent, ...]


__all__ = [
    "TacticalExecutionEvent",
    "TacticalExecutionInput",
    "TacticalExecutionQuality",
    "TacticalExecutionResult",
    "TacticalExecutionSignal",
    "TacticalScoreBreakdown",
]
