"""Models for offline AGIcore mock Alpaca paper session simulation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class MockAlpacaSessionState(StrEnum):
    NOT_READY = "NOT_READY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    PARTIALLY_READY = "PARTIALLY_READY"
    MOCK_SESSION_READY = "MOCK_SESSION_READY"
    MOCK_SESSION_COMPLETED = "MOCK_SESSION_COMPLETED"
    READY_FOR_SIMULATED_MARKET_SESSION = "READY_FOR_SIMULATED_MARKET_SESSION"


class MockAlpacaSessionRisk(StrEnum):
    MOCK_SESSION_CONNECT_FAILURE = "MOCK_SESSION_CONNECT_FAILURE"
    MOCK_ACCOUNT_FETCH_FAILURE = "MOCK_ACCOUNT_FETCH_FAILURE"
    MOCK_POSITIONS_FETCH_FAILURE = "MOCK_POSITIONS_FETCH_FAILURE"
    MOCK_ORDER_SUBMIT_FAILURE = "MOCK_ORDER_SUBMIT_FAILURE"
    MOCK_ORDER_STATUS_FAILURE = "MOCK_ORDER_STATUS_FAILURE"
    MOCK_JOURNAL_UPDATE_FAILURE = "MOCK_JOURNAL_UPDATE_FAILURE"
    MOCK_OBSERVABILITY_EVENT_MISSING = "MOCK_OBSERVABILITY_EVENT_MISSING"
    MOCK_SESSION_DISCONNECT_FAILURE = "MOCK_SESSION_DISCONNECT_FAILURE"
    MOCK_SESSION_STATE_DRIFT = "MOCK_SESSION_STATE_DRIFT"
    SAFETY_BOUNDARY_BYPASS = "SAFETY_BOUNDARY_BYPASS"


class MockAlpacaSessionRecommendation(StrEnum):
    HOLD_SIMULATED_MARKET_SESSION_APPROVAL = "HOLD_SIMULATED_MARKET_SESSION_APPROVAL"
    REPAIR_MOCK_SESSION_CONNECT = "REPAIR_MOCK_SESSION_CONNECT"
    REPAIR_MOCK_ACCOUNT_FETCH = "REPAIR_MOCK_ACCOUNT_FETCH"
    REPAIR_MOCK_POSITIONS_FETCH = "REPAIR_MOCK_POSITIONS_FETCH"
    REPAIR_MOCK_ORDER_SUBMIT = "REPAIR_MOCK_ORDER_SUBMIT"
    REPAIR_MOCK_ORDER_STATUS = "REPAIR_MOCK_ORDER_STATUS"
    REPAIR_MOCK_JOURNAL_UPDATE = "REPAIR_MOCK_JOURNAL_UPDATE"
    RESTORE_MOCK_OBSERVABILITY_EVENTS = "RESTORE_MOCK_OBSERVABILITY_EVENTS"
    REPAIR_MOCK_SESSION_DISCONNECT = "REPAIR_MOCK_SESSION_DISCONNECT"
    RECONCILE_MOCK_SESSION_STATE = "RECONCILE_MOCK_SESSION_STATE"
    ENFORCE_MOCK_SESSION_SAFETY_BOUNDARY = "ENFORCE_MOCK_SESSION_SAFETY_BOUNDARY"
    RUN_MOCK_ALPACA_SESSION_SUITE = "RUN_MOCK_ALPACA_SESSION_SUITE"
    APPROVE_SIMULATED_MARKET_SESSION_AFTER_MANUAL_REVIEW = (
        "APPROVE_SIMULATED_MARKET_SESSION_AFTER_MANUAL_REVIEW"
    )


@dataclass(frozen=True)
class MockAlpacaSessionInput:
    mock_connectivity_layer: Any = None
    alpaca_paper_connectivity_readiness: Any = None
    broker_paper_sandbox: Any = None
    alpaca_paper_adapter: Any = None
    paper_broker_adapter: Any = None
    paper_trading_end_to_end: Any = None
    paper_dry_run: Any = None
    supervised_paper_trial: Any = None
    observability_verification: Any = None
    kill_switch_verification: Any = None
    rollback_verification: Any = None
    mock_session_transport_ready: bool | None = None
    mock_session_connect_successful: bool | None = None
    mock_session_handshake_valid: bool | None = None
    mock_session_idempotent: bool | None = None
    mock_account_fetch_simulated: bool | None = None
    mock_account_schema_valid: bool | None = None
    mock_account_balances_consistent: bool | None = None
    mock_account_fetch_traceable: bool | None = None
    mock_positions_fetch_simulated: bool | None = None
    mock_positions_schema_valid: bool | None = None
    mock_positions_reconciled: bool | None = None
    mock_positions_fetch_traceable: bool | None = None
    mock_order_submit_simulated: bool | None = None
    mock_order_payload_valid: bool | None = None
    mock_order_safety_checked: bool | None = None
    mock_order_not_routed: bool | None = None
    mock_order_status_simulated: bool | None = None
    mock_order_status_schema_valid: bool | None = None
    mock_order_status_reconciled: bool | None = None
    mock_order_status_traceable: bool | None = None
    mock_journal_update_simulated: bool | None = None
    mock_journal_entry_complete: bool | None = None
    mock_journal_traceable: bool | None = None
    mock_journal_replayable: bool | None = None
    mock_observability_events_simulated: bool | None = None
    mock_metrics_recorded: bool | None = None
    mock_traces_recorded: bool | None = None
    mock_alerts_recorded: bool | None = None
    mock_session_disconnect_simulated: bool | None = None
    mock_session_disconnect_detected: bool | None = None
    mock_session_shutdown_safe: bool | None = None
    mock_session_reconnect_blocked: bool | None = None
    mock_state_snapshot_consistent: bool | None = None
    mock_state_replay_consistent: bool | None = None
    mock_state_recovery_verified: bool | None = None
    mock_state_isolated: bool | None = None
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
    session_completed: bool | None = None
    ready_for_simulated_market_session: bool | None = None
    mock_session_connect_score: int | None = None
    mock_account_fetch_score: int | None = None
    mock_positions_fetch_score: int | None = None
    mock_order_submit_score: int | None = None
    mock_order_status_score: int | None = None
    mock_journal_update_score: int | None = None
    mock_observability_events_score: int | None = None
    mock_session_disconnect_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class MockAlpacaSessionSimulation:
    name: str
    score: int
    passed: bool
    risks: tuple[MockAlpacaSessionRisk, ...] = ()
    events: tuple[str, ...] = ()


@dataclass(frozen=True)
class MockAlpacaSessionGraph:
    nodes: tuple[str, ...] = ()
    edges: tuple[tuple[str, str, str], ...] = ()
    ready_edges: tuple[tuple[str, str], ...] = ()
    blocked_edges: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class MockAlpacaSessionScore:
    overall_score: int
    mock_session_connect_score: int
    mock_account_fetch_score: int
    mock_positions_fetch_score: int
    mock_order_submit_score: int
    mock_order_status_score: int
    mock_journal_update_score: int
    mock_observability_events_score: int
    mock_session_disconnect_score: int


@dataclass(frozen=True)
class MockAlpacaSessionResult:
    state: MockAlpacaSessionState
    mock_alpaca_session_score: int
    score_breakdown: MockAlpacaSessionScore
    risks: tuple[MockAlpacaSessionRisk, ...] = ()
    mock_session_connect: MockAlpacaSessionSimulation = field(
        default_factory=lambda: MockAlpacaSessionSimulation("mock_session_connect", 0, False)
    )
    mock_account_fetch: MockAlpacaSessionSimulation = field(
        default_factory=lambda: MockAlpacaSessionSimulation("mock_account_fetch", 0, False)
    )
    mock_positions_fetch: MockAlpacaSessionSimulation = field(
        default_factory=lambda: MockAlpacaSessionSimulation("mock_positions_fetch", 0, False)
    )
    mock_order_submit: MockAlpacaSessionSimulation = field(
        default_factory=lambda: MockAlpacaSessionSimulation("mock_order_submit", 0, False)
    )
    mock_order_status: MockAlpacaSessionSimulation = field(
        default_factory=lambda: MockAlpacaSessionSimulation("mock_order_status", 0, False)
    )
    mock_journal_update: MockAlpacaSessionSimulation = field(
        default_factory=lambda: MockAlpacaSessionSimulation("mock_journal_update", 0, False)
    )
    mock_observability_events: MockAlpacaSessionSimulation = field(
        default_factory=lambda: MockAlpacaSessionSimulation("mock_observability_events", 0, False)
    )
    mock_session_disconnect: MockAlpacaSessionSimulation = field(
        default_factory=lambda: MockAlpacaSessionSimulation("mock_session_disconnect", 0, False)
    )
    mock_session_graph: MockAlpacaSessionGraph = field(default_factory=MockAlpacaSessionGraph)
    recommendations: tuple[MockAlpacaSessionRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
