"""Models for offline AGIcore mock connectivity layer simulation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class MockConnectivityState(StrEnum):
    NOT_READY = "NOT_READY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    PARTIALLY_READY = "PARTIALLY_READY"
    MOCK_CONNECTIVITY_READY = "MOCK_CONNECTIVITY_READY"
    MOCK_CONNECTIVITY_VALIDATED = "MOCK_CONNECTIVITY_VALIDATED"
    READY_FOR_MOCK_ALPACA_SESSION = "READY_FOR_MOCK_ALPACA_SESSION"


class MockConnectivityRisk(StrEnum):
    MOCK_CONNECTION_FAILURE = "MOCK_CONNECTION_FAILURE"
    MOCK_DISCONNECT_UNHANDLED = "MOCK_DISCONNECT_UNHANDLED"
    MOCK_TIMEOUT_UNHANDLED = "MOCK_TIMEOUT_UNHANDLED"
    MOCK_RETRY_POLICY_FAILURE = "MOCK_RETRY_POLICY_FAILURE"
    MOCK_RATE_LIMIT_UNHANDLED = "MOCK_RATE_LIMIT_UNHANDLED"
    MOCK_RESPONSE_INVALID = "MOCK_RESPONSE_INVALID"
    MOCK_ORDER_REJECTION_UNHANDLED = "MOCK_ORDER_REJECTION_UNHANDLED"
    MOCK_SESSION_CORRUPTION = "MOCK_SESSION_CORRUPTION"
    OBSERVABILITY_GAP = "OBSERVABILITY_GAP"
    SAFETY_BOUNDARY_BYPASS = "SAFETY_BOUNDARY_BYPASS"


class MockConnectivityRecommendation(StrEnum):
    HOLD_MOCK_ALPACA_SESSION_APPROVAL = "HOLD_MOCK_ALPACA_SESSION_APPROVAL"
    REPAIR_MOCK_CONNECTION = "REPAIR_MOCK_CONNECTION"
    HANDLE_MOCK_DISCONNECT = "HANDLE_MOCK_DISCONNECT"
    HANDLE_MOCK_TIMEOUT = "HANDLE_MOCK_TIMEOUT"
    REPAIR_MOCK_RETRY_POLICY = "REPAIR_MOCK_RETRY_POLICY"
    HANDLE_MOCK_RATE_LIMIT = "HANDLE_MOCK_RATE_LIMIT"
    VALIDATE_MOCK_RESPONSE = "VALIDATE_MOCK_RESPONSE"
    HANDLE_MOCK_ORDER_REJECTION = "HANDLE_MOCK_ORDER_REJECTION"
    REPAIR_MOCK_SESSION_INTEGRITY = "REPAIR_MOCK_SESSION_INTEGRITY"
    RESTORE_MOCK_OBSERVABILITY = "RESTORE_MOCK_OBSERVABILITY"
    ENFORCE_MOCK_SAFETY_BOUNDARY = "ENFORCE_MOCK_SAFETY_BOUNDARY"
    RUN_MOCK_CONNECTIVITY_SUITE = "RUN_MOCK_CONNECTIVITY_SUITE"
    APPROVE_MOCK_ALPACA_SESSION_AFTER_MANUAL_REVIEW = (
        "APPROVE_MOCK_ALPACA_SESSION_AFTER_MANUAL_REVIEW"
    )


@dataclass(frozen=True)
class MockConnectivityInput:
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
    mock_transport_defined: bool | None = None
    mock_connect_successful: bool | None = None
    mock_handshake_valid: bool | None = None
    mock_connection_idempotent: bool | None = None
    disconnect_event_simulated: bool | None = None
    disconnect_detected: bool | None = None
    disconnect_state_safe: bool | None = None
    reconnect_blocked_until_supervised: bool | None = None
    timeout_event_simulated: bool | None = None
    timeout_detected: bool | None = None
    timeout_fail_closed: bool | None = None
    timeout_observed: bool | None = None
    retry_event_simulated: bool | None = None
    retry_policy_applied: bool | None = None
    retry_backoff_respected: bool | None = None
    retry_stop_condition_respected: bool | None = None
    rate_limit_event_simulated: bool | None = None
    rate_limit_detected: bool | None = None
    throttle_applied: bool | None = None
    rate_limit_metric_recorded: bool | None = None
    mock_response_generated: bool | None = None
    mock_response_schema_valid: bool | None = None
    mock_response_traceable: bool | None = None
    mock_response_deterministic: bool | None = None
    mock_order_rejection_simulated: bool | None = None
    mock_order_rejection_handled: bool | None = None
    rejection_reason_recorded: bool | None = None
    no_order_routed: bool | None = None
    session_state_isolated: bool | None = None
    session_checkpointed: bool | None = None
    session_recovery_verified: bool | None = None
    session_integrity_locked: bool | None = None
    observability_events_emitted: bool | None = None
    metrics_recorded: bool | None = None
    traces_recorded: bool | None = None
    critical_alerts_recorded: bool | None = None
    safety_gate_enforced: bool | None = None
    kill_switch_linked: bool | None = None
    rollback_linked: bool | None = None
    offline_mode_enforced: bool | None = None
    no_http_transport: bool | None = None
    no_websocket_transport: bool | None = None
    no_socket_transport: bool | None = None
    no_external_sdk_import: bool | None = None
    mock_layer_validated: bool | None = None
    ready_for_mock_alpaca_session: bool | None = None
    mock_connection_score: int | None = None
    mock_disconnect_score: int | None = None
    mock_timeout_score: int | None = None
    mock_retry_score: int | None = None
    mock_rate_limit_score: int | None = None
    mock_broker_response_score: int | None = None
    mock_order_rejection_score: int | None = None
    mock_session_integrity_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class MockConnectivitySimulation:
    name: str
    score: int
    passed: bool
    risks: tuple[MockConnectivityRisk, ...] = ()
    events: tuple[str, ...] = ()


@dataclass(frozen=True)
class MockConnectivityGraph:
    nodes: tuple[str, ...] = ()
    edges: tuple[tuple[str, str, str], ...] = ()
    ready_edges: tuple[tuple[str, str], ...] = ()
    blocked_edges: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class MockConnectivityScore:
    overall_score: int
    mock_connection_score: int
    mock_disconnect_score: int
    mock_timeout_score: int
    mock_retry_score: int
    mock_rate_limit_score: int
    mock_broker_response_score: int
    mock_order_rejection_score: int
    mock_session_integrity_score: int


@dataclass(frozen=True)
class MockConnectivityResult:
    state: MockConnectivityState
    mock_connectivity_score: int
    score_breakdown: MockConnectivityScore
    risks: tuple[MockConnectivityRisk, ...] = ()
    mock_connection: MockConnectivitySimulation = field(
        default_factory=lambda: MockConnectivitySimulation("mock_connection", 0, False)
    )
    mock_disconnect: MockConnectivitySimulation = field(
        default_factory=lambda: MockConnectivitySimulation("mock_disconnect", 0, False)
    )
    mock_timeout: MockConnectivitySimulation = field(
        default_factory=lambda: MockConnectivitySimulation("mock_timeout", 0, False)
    )
    mock_retry: MockConnectivitySimulation = field(
        default_factory=lambda: MockConnectivitySimulation("mock_retry", 0, False)
    )
    mock_rate_limit: MockConnectivitySimulation = field(
        default_factory=lambda: MockConnectivitySimulation("mock_rate_limit", 0, False)
    )
    mock_broker_response: MockConnectivitySimulation = field(
        default_factory=lambda: MockConnectivitySimulation("mock_broker_response", 0, False)
    )
    mock_order_rejection: MockConnectivitySimulation = field(
        default_factory=lambda: MockConnectivitySimulation("mock_order_rejection", 0, False)
    )
    mock_session_integrity: MockConnectivitySimulation = field(
        default_factory=lambda: MockConnectivitySimulation("mock_session_integrity", 0, False)
    )
    mock_connectivity_graph: MockConnectivityGraph = field(default_factory=MockConnectivityGraph)
    recommendations: tuple[MockConnectivityRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
