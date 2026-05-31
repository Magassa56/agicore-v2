"""Models for offline AGIcore full paper session simulation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class FullPaperSessionState(StrEnum):
    NOT_READY = "NOT_READY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    PARTIALLY_READY = "PARTIALLY_READY"
    FULL_SESSION_READY = "FULL_SESSION_READY"
    FULL_SESSION_COMPLETED = "FULL_SESSION_COMPLETED"
    READY_FOR_PAPER_TRADING_RUNTIME = "READY_FOR_PAPER_TRADING_RUNTIME"


class FullPaperSessionRisk(StrEnum):
    MARKET_CYCLE_FAILURE = "MARKET_CYCLE_FAILURE"
    SIGNAL_CYCLE_FAILURE = "SIGNAL_CYCLE_FAILURE"
    DECISION_CYCLE_FAILURE = "DECISION_CYCLE_FAILURE"
    ORDER_CYCLE_FAILURE = "ORDER_CYCLE_FAILURE"
    POSITION_CYCLE_FAILURE = "POSITION_CYCLE_FAILURE"
    PNL_CYCLE_FAILURE = "PNL_CYCLE_FAILURE"
    RISK_MANAGEMENT_FAILURE = "RISK_MANAGEMENT_FAILURE"
    JOURNAL_INCOMPLETE = "JOURNAL_INCOMPLETE"
    OBSERVABILITY_GAP = "OBSERVABILITY_GAP"
    ROLLBACK_FAILURE = "ROLLBACK_FAILURE"
    KILL_SWITCH_FAILURE = "KILL_SWITCH_FAILURE"
    SESSION_STATE_DRIFT = "SESSION_STATE_DRIFT"
    SAFETY_BOUNDARY_BYPASS = "SAFETY_BOUNDARY_BYPASS"


class FullPaperSessionRecommendation(StrEnum):
    HOLD_PAPER_TRADING_RUNTIME_APPROVAL = "HOLD_PAPER_TRADING_RUNTIME_APPROVAL"
    REPAIR_MARKET_CYCLES = "REPAIR_MARKET_CYCLES"
    REPAIR_SIGNAL_CYCLES = "REPAIR_SIGNAL_CYCLES"
    REPAIR_DECISION_CYCLES = "REPAIR_DECISION_CYCLES"
    REPAIR_ORDER_CYCLES = "REPAIR_ORDER_CYCLES"
    REPAIR_POSITION_CYCLES = "REPAIR_POSITION_CYCLES"
    REPAIR_PNL_CYCLES = "REPAIR_PNL_CYCLES"
    REPAIR_RISK_MANAGEMENT = "REPAIR_RISK_MANAGEMENT"
    COMPLETE_FULL_SESSION_JOURNAL = "COMPLETE_FULL_SESSION_JOURNAL"
    RESTORE_FULL_SESSION_OBSERVABILITY = "RESTORE_FULL_SESSION_OBSERVABILITY"
    REPAIR_SESSION_ROLLBACK = "REPAIR_SESSION_ROLLBACK"
    REPAIR_SESSION_KILL_SWITCH = "REPAIR_SESSION_KILL_SWITCH"
    RECONCILE_FULL_SESSION_STATE = "RECONCILE_FULL_SESSION_STATE"
    ENFORCE_FULL_SESSION_SAFETY_BOUNDARY = "ENFORCE_FULL_SESSION_SAFETY_BOUNDARY"
    RUN_FULL_PAPER_SESSION_SUITE = "RUN_FULL_PAPER_SESSION_SUITE"
    APPROVE_PAPER_TRADING_RUNTIME_AFTER_MANUAL_REVIEW = (
        "APPROVE_PAPER_TRADING_RUNTIME_AFTER_MANUAL_REVIEW"
    )


@dataclass(frozen=True)
class FullPaperSessionInput:
    simulated_market_session: Any = None
    mock_alpaca_session: Any = None
    mock_connectivity_layer: Any = None
    paper_trading_end_to_end: Any = None
    paper_dry_run: Any = None
    supervised_paper_trial: Any = None
    observability_verification: Any = None
    kill_switch_verification: Any = None
    rollback_verification: Any = None
    market_cycles_available: bool | None = None
    market_cycles_schema_valid: bool | None = None
    market_cycles_replayable: bool | None = None
    market_cycles_count_valid: bool | None = None
    signal_cycles_generated: bool | None = None
    signal_cycles_deterministic: bool | None = None
    signal_cycles_traceable: bool | None = None
    signal_cycles_count_aligned: bool | None = None
    decision_cycles_generated: bool | None = None
    decision_cycles_deterministic: bool | None = None
    decision_cycles_safety_checked: bool | None = None
    decision_cycles_traceable: bool | None = None
    order_cycles_created: bool | None = None
    order_cycles_validated: bool | None = None
    order_cycles_status_progressed: bool | None = None
    order_cycles_not_routed: bool | None = None
    position_cycles_updated: bool | None = None
    position_cycles_reconciled: bool | None = None
    position_cycles_isolated: bool | None = None
    position_cycles_traceable: bool | None = None
    pnl_cycles_calculated: bool | None = None
    pnl_cycles_reconciled: bool | None = None
    pnl_cycles_deterministic: bool | None = None
    pnl_cycles_traceable: bool | None = None
    risk_limits_defined: bool | None = None
    risk_limits_enforced: bool | None = None
    risk_breaches_blocked: bool | None = None
    risk_state_traceable: bool | None = None
    journal_created: bool | None = None
    journal_complete: bool | None = None
    journal_replayable: bool | None = None
    journal_traceable: bool | None = None
    observability_events_emitted: bool | None = None
    metrics_recorded: bool | None = None
    traces_recorded: bool | None = None
    alerts_recorded: bool | None = None
    rollback_checkpoint_created: bool | None = None
    rollback_restore_verified: bool | None = None
    rollback_state_reconciled: bool | None = None
    rollback_observed: bool | None = None
    kill_switch_available: bool | None = None
    kill_switch_halts_orders: bool | None = None
    kill_switch_halts_session: bool | None = None
    kill_switch_observed: bool | None = None
    session_state_snapshot_consistent: bool | None = None
    session_state_replay_consistent: bool | None = None
    session_state_recovery_verified: bool | None = None
    session_state_isolated: bool | None = None
    offline_mode_enforced: bool | None = None
    no_real_broker: bool | None = None
    no_api_key_read: bool | None = None
    no_http_transport: bool | None = None
    no_websocket_transport: bool | None = None
    no_socket_transport: bool | None = None
    no_external_api: bool | None = None
    no_real_order: bool | None = None
    full_session_completed: bool | None = None
    ready_for_paper_trading_runtime: bool | None = None
    market_cycles_score: int | None = None
    signal_cycles_score: int | None = None
    decision_cycles_score: int | None = None
    order_cycles_score: int | None = None
    position_cycles_score: int | None = None
    pnl_cycles_score: int | None = None
    risk_management_score: int | None = None
    journal_score: int | None = None
    observability_score: int | None = None
    rollback_score: int | None = None
    kill_switch_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class FullPaperSessionCheck:
    name: str
    score: int
    passed: bool
    risks: tuple[FullPaperSessionRisk, ...] = ()
    events: tuple[str, ...] = ()


@dataclass(frozen=True)
class FullPaperSessionGraph:
    nodes: tuple[str, ...] = ()
    edges: tuple[tuple[str, str, str], ...] = ()
    ready_edges: tuple[tuple[str, str], ...] = ()
    blocked_edges: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class FullPaperSessionScore:
    overall_score: int
    market_cycles_score: int
    signal_cycles_score: int
    decision_cycles_score: int
    order_cycles_score: int
    position_cycles_score: int
    pnl_cycles_score: int
    risk_management_score: int
    journal_score: int
    observability_score: int
    rollback_score: int
    kill_switch_score: int


@dataclass(frozen=True)
class FullPaperSessionResult:
    state: FullPaperSessionState
    full_session_score: int
    score_breakdown: FullPaperSessionScore
    risks: tuple[FullPaperSessionRisk, ...] = ()
    market_cycles: FullPaperSessionCheck = field(default_factory=lambda: FullPaperSessionCheck("market_cycles", 0, False))
    signal_cycles: FullPaperSessionCheck = field(default_factory=lambda: FullPaperSessionCheck("signal_cycles", 0, False))
    decision_cycles: FullPaperSessionCheck = field(default_factory=lambda: FullPaperSessionCheck("decision_cycles", 0, False))
    order_cycles: FullPaperSessionCheck = field(default_factory=lambda: FullPaperSessionCheck("order_cycles", 0, False))
    position_cycles: FullPaperSessionCheck = field(default_factory=lambda: FullPaperSessionCheck("position_cycles", 0, False))
    pnl_cycles: FullPaperSessionCheck = field(default_factory=lambda: FullPaperSessionCheck("pnl_cycles", 0, False))
    risk_management: FullPaperSessionCheck = field(default_factory=lambda: FullPaperSessionCheck("risk_management", 0, False))
    journal: FullPaperSessionCheck = field(default_factory=lambda: FullPaperSessionCheck("journal", 0, False))
    observability: FullPaperSessionCheck = field(default_factory=lambda: FullPaperSessionCheck("observability", 0, False))
    rollback: FullPaperSessionCheck = field(default_factory=lambda: FullPaperSessionCheck("rollback", 0, False))
    kill_switch: FullPaperSessionCheck = field(default_factory=lambda: FullPaperSessionCheck("kill_switch", 0, False))
    session_graph: FullPaperSessionGraph = field(default_factory=FullPaperSessionGraph)
    recommendations: tuple[FullPaperSessionRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
