"""Models for offline AGIcore paper runtime preparation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperRuntimePreparationState(StrEnum):
    NOT_READY = "NOT_READY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    PARTIALLY_READY = "PARTIALLY_READY"
    PAPER_RUNTIME_READY = "PAPER_RUNTIME_READY"
    READY_FOR_PAPER_EXECUTION_LOOP = "READY_FOR_PAPER_EXECUTION_LOOP"


class PaperRuntimeRisk(StrEnum):
    VIRTUAL_PORTFOLIO_MISSING = "VIRTUAL_PORTFOLIO_MISSING"
    SIMULATED_ORDER_ENGINE_MISSING = "SIMULATED_ORDER_ENGINE_MISSING"
    SIMULATED_POSITION_TRACKING_MISSING = "SIMULATED_POSITION_TRACKING_MISSING"
    PAPER_RISK_ENGINE_MISSING = "PAPER_RISK_ENGINE_MISSING"
    SESSION_RUNTIME_UNVERIFIED = "SESSION_RUNTIME_UNVERIFIED"
    PAPER_PNL_UNVERIFIED = "PAPER_PNL_UNVERIFIED"
    PAPER_STATE_CORRUPTION_RISK = "PAPER_STATE_CORRUPTION_RISK"
    PAPER_EXECUTION_LEAK_RISK = "PAPER_EXECUTION_LEAK_RISK"
    PAPER_OBSERVABILITY_GAP = "PAPER_OBSERVABILITY_GAP"
    PAPER_RUNTIME_NOT_ISOLATED = "PAPER_RUNTIME_NOT_ISOLATED"


class PaperRuntimeRecommendation(StrEnum):
    HOLD_PAPER_RUNTIME_APPROVAL = "HOLD_PAPER_RUNTIME_APPROVAL"
    CREATE_VIRTUAL_PORTFOLIO = "CREATE_VIRTUAL_PORTFOLIO"
    ENABLE_SIMULATED_ORDER_ENGINE = "ENABLE_SIMULATED_ORDER_ENGINE"
    ENABLE_SIMULATED_POSITION_TRACKING = "ENABLE_SIMULATED_POSITION_TRACKING"
    ENABLE_PAPER_RISK_ENGINE = "ENABLE_PAPER_RISK_ENGINE"
    VERIFY_SESSION_RUNTIME = "VERIFY_SESSION_RUNTIME"
    VERIFY_PAPER_PNL = "VERIFY_PAPER_PNL"
    PROTECT_PAPER_STATE = "PROTECT_PAPER_STATE"
    SEAL_PAPER_EXECUTION_BOUNDARY = "SEAL_PAPER_EXECUTION_BOUNDARY"
    ADD_PAPER_OBSERVABILITY = "ADD_PAPER_OBSERVABILITY"
    ISOLATE_PAPER_RUNTIME = "ISOLATE_PAPER_RUNTIME"
    RUN_PAPER_RUNTIME_PREPARATION_SUITE = "RUN_PAPER_RUNTIME_PREPARATION_SUITE"
    APPROVE_PAPER_EXECUTION_LOOP_AFTER_MANUAL_REVIEW = (
        "APPROVE_PAPER_EXECUTION_LOOP_AFTER_MANUAL_REVIEW"
    )


@dataclass(frozen=True)
class PaperRuntimePreparationInput:
    observability_verification: Any = None
    rollback_verification: Any = None
    kill_switch_verification: Any = None
    runtime_isolation_review: Any = None
    sandbox_readiness_audit: Any = None
    stable_review: Any = None
    virtual_portfolio_available: bool | None = None
    virtual_cash_configured: bool | None = None
    virtual_equity_consistent: bool | None = None
    portfolio_reset_supported: bool | None = None
    simulated_order_engine_available: bool | None = None
    market_order_simulation_supported: bool | None = None
    order_rejection_simulation_supported: bool | None = None
    broker_connection_absent: bool | None = None
    simulated_position_tracking_available: bool | None = None
    position_average_price_supported: bool | None = None
    realized_pnl_supported: bool | None = None
    position_state_consistent: bool | None = None
    paper_risk_engine_available: bool | None = None
    max_order_limits_configured: bool | None = None
    risk_gate_enforced: bool | None = None
    kill_switch_connected: bool | None = None
    session_runtime_configured: bool | None = None
    session_prechecks_defined: bool | None = None
    session_event_stream_available: bool | None = None
    paper_runtime_isolated: bool | None = None
    paper_observability_available: bool | None = None
    paper_state_checkpoint_supported: bool | None = None
    ready_for_paper_execution_loop: bool | None = None
    virtual_portfolio_score: int | None = None
    simulated_order_score: int | None = None
    simulated_position_score: int | None = None
    paper_risk_score: int | None = None
    session_runtime_score: int | None = None
    paper_observability_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperRuntimeReviewSection:
    name: str
    score: int
    passed: bool
    risks: tuple[PaperRuntimeRisk, ...] = ()
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperRuntimeGraph:
    nodes: tuple[str, ...] = ()
    edges: tuple[tuple[str, str, str], ...] = ()
    ready_edges: tuple[tuple[str, str], ...] = ()
    blocked_edges: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class PaperRuntimeScore:
    overall_score: int
    virtual_portfolio_score: int
    simulated_order_score: int
    simulated_position_score: int
    paper_risk_score: int
    session_runtime_score: int
    paper_observability_score: int


@dataclass(frozen=True)
class PaperRuntimePreparationResult:
    state: PaperRuntimePreparationState
    paper_runtime_score: int
    score_breakdown: PaperRuntimeScore
    blockers: tuple[PaperRuntimeRisk, ...] = ()
    virtual_portfolio_review: PaperRuntimeReviewSection = field(
        default_factory=lambda: PaperRuntimeReviewSection("virtual_portfolio_review", 0, False)
    )
    simulated_order_review: PaperRuntimeReviewSection = field(
        default_factory=lambda: PaperRuntimeReviewSection("simulated_order_review", 0, False)
    )
    simulated_position_review: PaperRuntimeReviewSection = field(
        default_factory=lambda: PaperRuntimeReviewSection("simulated_position_review", 0, False)
    )
    paper_risk_review: PaperRuntimeReviewSection = field(
        default_factory=lambda: PaperRuntimeReviewSection("paper_risk_review", 0, False)
    )
    session_runtime_review: PaperRuntimeReviewSection = field(
        default_factory=lambda: PaperRuntimeReviewSection("session_runtime_review", 0, False)
    )
    paper_runtime_graph: PaperRuntimeGraph = field(default_factory=PaperRuntimeGraph)
    recommendations: tuple[PaperRuntimeRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
