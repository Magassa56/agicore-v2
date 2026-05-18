"""Models for offline semi-auto decision assistance."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from .adaptive_memory_models import TraderMemoryProfile
from .behavior_models import BehaviorAnalysisResult
from .context_scoring_models import ContextScoringResult
from .daily_report_models import DailyTradingReport
from .market_regime_models import MarketRegimeAnalysis
from .playbook_models import TraderProfile
from .session_coach_models import SessionCoachDecision
from .strategy_dna_models import StrategyDNA


class SemiAutoDecision(StrEnum):
    """Offline semi-auto decision; never executes real orders."""

    APPROVE_TRADE = "APPROVE_TRADE"
    APPROVE_REDUCED_RISK = "APPROVE_REDUCED_RISK"
    REQUIRE_CONFIRMATION = "REQUIRE_CONFIRMATION"
    BLOCK_TRADE = "BLOCK_TRADE"
    STOP_SESSION = "STOP_SESSION"
    REVIEW_ONLY = "REVIEW_ONLY"


class SemiAutoAction(StrEnum):
    """Recommended offline action for the operator UI."""

    PREPARE_ORDER_PREVIEW = "prepare_order_preview"
    REDUCE_SIZE = "reduce_size"
    REQUEST_MANUAL_CONFIRMATION = "request_manual_confirmation"
    BLOCK_TRADE = "block_trade"
    RECOMMEND_STOP_SESSION = "recommend_stop_session"
    REQUIRE_REVIEW = "require_review"
    NO_ACTION = "no_action"


@dataclass(frozen=True)
class SemiAutoDecisionInput:
    """Inputs consumed by the offline semi-auto decision assistant."""

    context_score: ContextScoringResult
    coach_decision: SessionCoachDecision | None = None
    coach_output: Any | None = None
    market_regime: MarketRegimeAnalysis | None = None
    behavior_result: BehaviorAnalysisResult | None = None
    memory_profile: TraderMemoryProfile | None = None
    trader_profile: TraderProfile | None = None
    strategy_dna: StrategyDNA | None = None
    daily_report: DailyTradingReport | None = None


@dataclass(frozen=True)
class SemiAutoDecisionResult:
    """Final assisted decision, action and operator-facing explanation."""

    decision: SemiAutoDecision
    action: SemiAutoAction
    context_score: int
    approval_reasons: tuple[str, ...]
    blocking_reasons: tuple[str, ...]
    detected_risks: tuple[str, ...]
    manual_confirmation_conditions: tuple[str, ...]
    trader_message: str


__all__ = [
    "SemiAutoAction",
    "SemiAutoDecision",
    "SemiAutoDecisionInput",
    "SemiAutoDecisionResult",
]
