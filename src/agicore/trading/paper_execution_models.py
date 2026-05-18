"""Models for the offline controlled paper execution loop."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .context_scoring_models import ContextScoringResult
from .paper_trading_models import PaperOrderRequest, PaperOrderResult
from .playbook_models import TraderProfile
from .semi_auto_decision_models import SemiAutoDecisionResult
from .strategy_dna_models import StrategyDNA


class PaperExecutionDecision(StrEnum):
    """Final decision emitted by the controlled paper execution loop."""

    PAPER_ORDER_FILLED = "PAPER_ORDER_FILLED"
    PAPER_ORDER_REJECTED = "PAPER_ORDER_REJECTED"
    PRECHECK_REJECTED = "PRECHECK_REJECTED"


class PaperExecutionEventType(StrEnum):
    """Auditable loop event types."""

    LOOP_STARTED = "LOOP_STARTED"
    PRECHECK_PASSED = "PRECHECK_PASSED"
    PRECHECK_FAILED = "PRECHECK_FAILED"
    PAPER_ORDER_SUBMITTED = "PAPER_ORDER_SUBMITTED"
    PAPER_ORDER_REJECTED = "PAPER_ORDER_REJECTED"
    PAPER_ORDER_FILLED = "PAPER_ORDER_FILLED"
    LOOP_COMPLETED = "LOOP_COMPLETED"


@dataclass(frozen=True)
class PaperExecutionLoopConfig:
    """Configuration for offline controlled paper execution."""

    trading_enabled: bool = True
    risk_allowed: bool = True
    allow_high_risk_override: bool = False
    max_orders_per_session: int = 1
    submitted_orders_count: int = 0


@dataclass(frozen=True)
class PaperExecutionRequest:
    """Request passed to the controlled paper execution loop."""

    semi_auto_decision: SemiAutoDecisionResult
    context_score: ContextScoringResult
    order_request: PaperOrderRequest
    strategy_dna: StrategyDNA | None = None
    trader_profile: TraderProfile | None = None
    config: PaperExecutionLoopConfig = PaperExecutionLoopConfig()


@dataclass(frozen=True)
class PaperExecutionEvent:
    """One auditable event emitted by the offline execution loop."""

    event_type: PaperExecutionEventType
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class PaperExecutionResult:
    """Complete output from the controlled paper execution loop."""

    decision: PaperExecutionDecision
    accepted: bool
    precheck_passed: bool
    precheck_reasons: tuple[str, ...]
    order_result: PaperOrderResult | None
    events: tuple[PaperExecutionEvent, ...]
    safety_message: str


__all__ = [
    "PaperExecutionDecision",
    "PaperExecutionEvent",
    "PaperExecutionEventType",
    "PaperExecutionLoopConfig",
    "PaperExecutionRequest",
    "PaperExecutionResult",
]
