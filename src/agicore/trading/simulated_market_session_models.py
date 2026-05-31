"""Models for offline AGIcore simulated market session."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class SimulatedMarketSessionState(StrEnum):
    NOT_READY = "NOT_READY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    PARTIALLY_READY = "PARTIALLY_READY"
    SIMULATED_SESSION_READY = "SIMULATED_SESSION_READY"
    SIMULATED_SESSION_COMPLETED = "SIMULATED_SESSION_COMPLETED"
    READY_FOR_FULL_PAPER_SESSION = "READY_FOR_FULL_PAPER_SESSION"


class SimulatedMarketSessionRisk(StrEnum):
    MARKET_DATA_MISSING = "MARKET_DATA_MISSING"
    SIGNAL_GENERATION_FAILURE = "SIGNAL_GENERATION_FAILURE"
    DECISION_GENERATION_FAILURE = "DECISION_GENERATION_FAILURE"
    ORDER_LIFECYCLE_FAILURE = "ORDER_LIFECYCLE_FAILURE"
    POSITION_LIFECYCLE_FAILURE = "POSITION_LIFECYCLE_FAILURE"
    PNL_CALCULATION_FAILURE = "PNL_CALCULATION_FAILURE"
    JOURNAL_INCOMPLETE = "JOURNAL_INCOMPLETE"
    OBSERVABILITY_GAP = "OBSERVABILITY_GAP"
    SESSION_STATE_DRIFT = "SESSION_STATE_DRIFT"
    SAFETY_BOUNDARY_BYPASS = "SAFETY_BOUNDARY_BYPASS"


class SimulatedMarketSessionRecommendation(StrEnum):
    HOLD_FULL_PAPER_SESSION_APPROVAL = "HOLD_FULL_PAPER_SESSION_APPROVAL"
    RESTORE_MARKET_DATA_FLOW = "RESTORE_MARKET_DATA_FLOW"
    REPAIR_SIGNAL_GENERATION_FLOW = "REPAIR_SIGNAL_GENERATION_FLOW"
    REPAIR_DECISION_GENERATION_FLOW = "REPAIR_DECISION_GENERATION_FLOW"
    REPAIR_ORDER_LIFECYCLE = "REPAIR_ORDER_LIFECYCLE"
    REPAIR_POSITION_LIFECYCLE = "REPAIR_POSITION_LIFECYCLE"
    REPAIR_PNL_CALCULATION = "REPAIR_PNL_CALCULATION"
    COMPLETE_SESSION_JOURNAL = "COMPLETE_SESSION_JOURNAL"
    RESTORE_SESSION_OBSERVABILITY = "RESTORE_SESSION_OBSERVABILITY"
    RECONCILE_SESSION_STATE = "RECONCILE_SESSION_STATE"
    ENFORCE_MARKET_SESSION_SAFETY_BOUNDARY = "ENFORCE_MARKET_SESSION_SAFETY_BOUNDARY"
    RUN_SIMULATED_MARKET_SESSION_SUITE = "RUN_SIMULATED_MARKET_SESSION_SUITE"
    APPROVE_FULL_PAPER_SESSION_AFTER_MANUAL_REVIEW = (
        "APPROVE_FULL_PAPER_SESSION_AFTER_MANUAL_REVIEW"
    )


@dataclass(frozen=True)
class SimulatedMarketSessionInput:
    mock_alpaca_session: Any = None
    mock_connectivity_layer: Any = None
    alpaca_paper_connectivity_readiness: Any = None
    broker_paper_sandbox: Any = None
    paper_trading_end_to_end: Any = None
    paper_dry_run: Any = None
    supervised_paper_trial: Any = None
    observability_verification: Any = None
    kill_switch_verification: Any = None
    rollback_verification: Any = None
    fictive_market_data_available: bool | None = None
    market_data_schema_valid: bool | None = None
    market_data_sequence_ordered: bool | None = None
    market_data_replayable: bool | None = None
    signal_inputs_available: bool | None = None
    signal_generation_deterministic: bool | None = None
    signal_schema_valid: bool | None = None
    signal_traceable: bool | None = None
    decision_inputs_available: bool | None = None
    decision_generation_deterministic: bool | None = None
    decision_schema_valid: bool | None = None
    decision_safety_checked: bool | None = None
    paper_order_created: bool | None = None
    paper_order_validated: bool | None = None
    paper_order_status_progressed: bool | None = None
    paper_order_not_routed: bool | None = None
    position_opened: bool | None = None
    position_updated: bool | None = None
    position_closed_or_carried: bool | None = None
    position_reconciled: bool | None = None
    paper_pnl_calculated: bool | None = None
    paper_pnl_reconciled: bool | None = None
    paper_pnl_traceable: bool | None = None
    paper_pnl_deterministic: bool | None = None
    session_journal_created: bool | None = None
    session_journal_complete: bool | None = None
    session_journal_replayable: bool | None = None
    session_journal_traceable: bool | None = None
    observability_events_emitted: bool | None = None
    metrics_recorded: bool | None = None
    traces_recorded: bool | None = None
    alerts_recorded: bool | None = None
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
    safety_gate_enforced: bool | None = None
    kill_switch_linked: bool | None = None
    rollback_linked: bool | None = None
    simulated_session_completed: bool | None = None
    ready_for_full_paper_session: bool | None = None
    market_data_score: int | None = None
    signal_generation_score: int | None = None
    decision_generation_score: int | None = None
    paper_order_lifecycle_score: int | None = None
    position_lifecycle_score: int | None = None
    paper_pnl_score: int | None = None
    session_journal_score: int | None = None
    session_observability_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class SimulatedMarketSessionFlow:
    name: str
    score: int
    passed: bool
    risks: tuple[SimulatedMarketSessionRisk, ...] = ()
    events: tuple[str, ...] = ()


@dataclass(frozen=True)
class SimulatedMarketSessionGraph:
    nodes: tuple[str, ...] = ()
    edges: tuple[tuple[str, str, str], ...] = ()
    ready_edges: tuple[tuple[str, str], ...] = ()
    blocked_edges: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class SimulatedMarketSessionScore:
    overall_score: int
    market_data_score: int
    signal_generation_score: int
    decision_generation_score: int
    paper_order_lifecycle_score: int
    position_lifecycle_score: int
    paper_pnl_score: int
    session_journal_score: int
    session_observability_score: int


@dataclass(frozen=True)
class SimulatedMarketSessionResult:
    state: SimulatedMarketSessionState
    market_session_score: int
    score_breakdown: SimulatedMarketSessionScore
    risks: tuple[SimulatedMarketSessionRisk, ...] = ()
    market_data_flow: SimulatedMarketSessionFlow = field(
        default_factory=lambda: SimulatedMarketSessionFlow("market_data_flow", 0, False)
    )
    signal_generation_flow: SimulatedMarketSessionFlow = field(
        default_factory=lambda: SimulatedMarketSessionFlow("signal_generation_flow", 0, False)
    )
    decision_generation_flow: SimulatedMarketSessionFlow = field(
        default_factory=lambda: SimulatedMarketSessionFlow("decision_generation_flow", 0, False)
    )
    paper_order_lifecycle: SimulatedMarketSessionFlow = field(
        default_factory=lambda: SimulatedMarketSessionFlow("paper_order_lifecycle", 0, False)
    )
    position_lifecycle: SimulatedMarketSessionFlow = field(
        default_factory=lambda: SimulatedMarketSessionFlow("position_lifecycle", 0, False)
    )
    paper_pnl_flow: SimulatedMarketSessionFlow = field(
        default_factory=lambda: SimulatedMarketSessionFlow("paper_pnl_flow", 0, False)
    )
    session_journal_flow: SimulatedMarketSessionFlow = field(
        default_factory=lambda: SimulatedMarketSessionFlow("session_journal_flow", 0, False)
    )
    session_observability_flow: SimulatedMarketSessionFlow = field(
        default_factory=lambda: SimulatedMarketSessionFlow("session_observability_flow", 0, False)
    )
    market_session_graph: SimulatedMarketSessionGraph = field(default_factory=SimulatedMarketSessionGraph)
    recommendations: tuple[SimulatedMarketSessionRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
