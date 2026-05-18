"""Models for offline trade context scoring."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .adaptive_memory_models import TraderMemoryProfile
from .behavior_models import BehaviorAnalysisResult
from .daily_report_models import DailyTradingReport
from .market_regime_models import MarketRegimeAnalysis
from .playbook_models import TraderProfile
from .session_replay_models import SessionReplayResult
from .strategy_dna_models import StrategyDNA
from .trade_journal_models import JournalAnalysisResult


class TradeContextDecision(StrEnum):
    """Offline trading decision derived from context score and hard risks."""

    STRONG_TRADE_ALLOWED = "STRONG_TRADE_ALLOWED"
    TRADE_ALLOWED = "TRADE_ALLOWED"
    REDUCE_RISK = "REDUCE_RISK"
    HIGH_RISK_CONTEXT = "HIGH_RISK_CONTEXT"
    NO_TRADE = "NO_TRADE"


@dataclass(frozen=True)
class ContextScoreBreakdown:
    """Component scores normalized from 0 to 100."""

    market_score: int
    behavior_score: int
    discipline_score: int
    memory_score: int
    emotional_score: int
    volatility_score: int
    strategy_regime_compatibility_score: int


@dataclass(frozen=True)
class ContextScoringInput:
    """Optional inputs used by the offline context scoring engine."""

    market_regime: MarketRegimeAnalysis | None = None
    behavior_result: BehaviorAnalysisResult | None = None
    session_replay_result: SessionReplayResult | None = None
    memory_profile: TraderMemoryProfile | None = None
    trader_profile: TraderProfile | None = None
    strategy_dna: StrategyDNA | None = None
    daily_report: DailyTradingReport | None = None
    journal_result: JournalAnalysisResult | None = None


@dataclass(frozen=True)
class ContextScoringResult:
    """Final context score, decision and explanatory factors."""

    global_score: int
    decision: TradeContextDecision
    breakdown: ContextScoreBreakdown
    favorable_factors: tuple[str, ...]
    risk_factors: tuple[str, ...]
    recommendations: tuple[str, ...]
    strategy_regime_notes: tuple[str, ...]
    no_trade_reasons: tuple[str, ...] = ()


__all__ = [
    "ContextScoreBreakdown",
    "ContextScoringInput",
    "ContextScoringResult",
    "TradeContextDecision",
]
