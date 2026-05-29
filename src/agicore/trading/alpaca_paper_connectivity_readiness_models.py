"""Models for offline AGIcore Alpaca Paper connectivity readiness."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class AlpacaPaperConnectivityState(StrEnum):
    NOT_READY = "NOT_READY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    PARTIALLY_READY = "PARTIALLY_READY"
    CONNECTIVITY_READY = "CONNECTIVITY_READY"
    CONNECTIVITY_VALIDATED = "CONNECTIVITY_VALIDATED"
    READY_FOR_MOCK_CONNECTIVITY = "READY_FOR_MOCK_CONNECTIVITY"


class AlpacaPaperConnectivityRisk(StrEnum):
    MISSING_CREDENTIALS = "MISSING_CREDENTIALS"
    INVALID_ENDPOINT_CONFIGURATION = "INVALID_ENDPOINT_CONFIGURATION"
    RATE_LIMIT_EXPOSURE = "RATE_LIMIT_EXPOSURE"
    TIMEOUT_EXPOSURE = "TIMEOUT_EXPOSURE"
    RETRY_POLICY_MISSING = "RETRY_POLICY_MISSING"
    SESSION_RECOVERY_FAILURE = "SESSION_RECOVERY_FAILURE"
    OBSERVABILITY_GAP = "OBSERVABILITY_GAP"
    KILL_SWITCH_INCOMPATIBILITY = "KILL_SWITCH_INCOMPATIBILITY"
    ROLLBACK_INCOMPATIBILITY = "ROLLBACK_INCOMPATIBILITY"
    UNSAFE_CONNECTIVITY_CONFIGURATION = "UNSAFE_CONNECTIVITY_CONFIGURATION"


class AlpacaPaperConnectivityRecommendation(StrEnum):
    HOLD_MOCK_CONNECTIVITY_APPROVAL = "HOLD_MOCK_CONNECTIVITY_APPROVAL"
    DEFINE_CREDENTIAL_REQUIREMENTS = "DEFINE_CREDENTIAL_REQUIREMENTS"
    FIX_ENDPOINT_CONFIGURATION = "FIX_ENDPOINT_CONFIGURATION"
    DEFINE_RATE_LIMIT_GUARDS = "DEFINE_RATE_LIMIT_GUARDS"
    DEFINE_TIMEOUT_POLICY = "DEFINE_TIMEOUT_POLICY"
    DEFINE_RETRY_POLICY = "DEFINE_RETRY_POLICY"
    VERIFY_SESSION_RECOVERY = "VERIFY_SESSION_RECOVERY"
    RESTORE_CONNECTIVITY_OBSERVABILITY = "RESTORE_CONNECTIVITY_OBSERVABILITY"
    LINK_KILL_SWITCH_COMPATIBILITY = "LINK_KILL_SWITCH_COMPATIBILITY"
    LINK_ROLLBACK_COMPATIBILITY = "LINK_ROLLBACK_COMPATIBILITY"
    LOCK_SAFE_CONNECTIVITY_CONFIGURATION = "LOCK_SAFE_CONNECTIVITY_CONFIGURATION"
    RUN_CONNECTIVITY_READINESS_SUITE = "RUN_CONNECTIVITY_READINESS_SUITE"
    APPROVE_MOCK_CONNECTIVITY_AFTER_MANUAL_REVIEW = "APPROVE_MOCK_CONNECTIVITY_AFTER_MANUAL_REVIEW"


@dataclass(frozen=True)
class AlpacaPaperConnectivityInput:
    broker_paper_sandbox: Any = None
    alpaca_paper_adapter: Any = None
    paper_trading_end_to_end: Any = None
    paper_dry_run: Any = None
    supervised_paper_trial: Any = None
    observability_verification: Any = None
    kill_switch_verification: Any = None
    rollback_verification: Any = None
    credential_schema_defined: bool | None = None
    credential_storage_externalized: bool | None = None
    no_real_credentials_loaded: bool | None = None
    paper_account_scope_defined: bool | None = None
    paper_endpoint_config_defined: bool | None = None
    endpoint_environment_locked: bool | None = None
    endpoint_allowlist_defined: bool | None = None
    live_endpoint_blocked: bool | None = None
    rate_limit_budget_defined: bool | None = None
    request_throttle_defined: bool | None = None
    burst_guard_defined: bool | None = None
    rate_limit_observability_defined: bool | None = None
    retry_policy_defined: bool | None = None
    retry_backoff_defined: bool | None = None
    retry_idempotency_defined: bool | None = None
    retry_stop_condition_defined: bool | None = None
    timeout_policy_defined: bool | None = None
    connect_timeout_defined: bool | None = None
    read_timeout_defined: bool | None = None
    timeout_fail_closed: bool | None = None
    disconnect_detection_defined: bool | None = None
    reconnect_policy_defined: bool | None = None
    session_recovery_checkpointed: bool | None = None
    stale_session_guard_defined: bool | None = None
    session_state_isolated: bool | None = None
    session_idempotency_defined: bool | None = None
    session_audit_defined: bool | None = None
    session_integrity_locked: bool | None = None
    observability_events_defined: bool | None = None
    metrics_defined: bool | None = None
    traces_defined: bool | None = None
    critical_alerts_defined: bool | None = None
    kill_switch_linked: bool | None = None
    kill_switch_fail_closed: bool | None = None
    emergency_disconnect_defined: bool | None = None
    operator_halt_required: bool | None = None
    rollback_linked: bool | None = None
    recovery_point_required: bool | None = None
    rollback_after_disconnect_defined: bool | None = None
    restart_guard_defined: bool | None = None
    offline_mode_enforced: bool | None = None
    no_http_transport: bool | None = None
    no_websocket_transport: bool | None = None
    no_socket_transport: bool | None = None
    no_external_sdk_import: bool | None = None
    configuration_locked: bool | None = None
    connectivity_validated: bool | None = None
    ready_for_mock_connectivity: bool | None = None
    credentials_score: int | None = None
    endpoint_score: int | None = None
    rate_limit_score: int | None = None
    retry_score: int | None = None
    timeout_score: int | None = None
    disconnect_recovery_score: int | None = None
    session_integrity_score: int | None = None
    observability_score: int | None = None
    kill_switch_compatibility_score: int | None = None
    rollback_compatibility_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class AlpacaPaperConnectivityReviewSection:
    name: str
    score: int
    passed: bool
    risks: tuple[AlpacaPaperConnectivityRisk, ...] = ()
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class AlpacaPaperConnectivityGraph:
    nodes: tuple[str, ...] = ()
    edges: tuple[tuple[str, str, str], ...] = ()
    ready_edges: tuple[tuple[str, str], ...] = ()
    blocked_edges: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class AlpacaPaperConnectivityScore:
    overall_score: int
    credentials_score: int
    endpoint_score: int
    rate_limit_score: int
    retry_score: int
    timeout_score: int
    disconnect_recovery_score: int
    session_integrity_score: int
    observability_score: int
    kill_switch_compatibility_score: int
    rollback_compatibility_score: int


@dataclass(frozen=True)
class AlpacaPaperConnectivityResult:
    state: AlpacaPaperConnectivityState
    connectivity_score: int
    score_breakdown: AlpacaPaperConnectivityScore
    risks: tuple[AlpacaPaperConnectivityRisk, ...] = ()
    credentials_review: AlpacaPaperConnectivityReviewSection = field(
        default_factory=lambda: AlpacaPaperConnectivityReviewSection("credentials_review", 0, False)
    )
    endpoint_review: AlpacaPaperConnectivityReviewSection = field(
        default_factory=lambda: AlpacaPaperConnectivityReviewSection("endpoint_review", 0, False)
    )
    rate_limit_review: AlpacaPaperConnectivityReviewSection = field(
        default_factory=lambda: AlpacaPaperConnectivityReviewSection("rate_limit_review", 0, False)
    )
    retry_review: AlpacaPaperConnectivityReviewSection = field(
        default_factory=lambda: AlpacaPaperConnectivityReviewSection("retry_review", 0, False)
    )
    timeout_review: AlpacaPaperConnectivityReviewSection = field(
        default_factory=lambda: AlpacaPaperConnectivityReviewSection("timeout_review", 0, False)
    )
    disconnect_recovery_review: AlpacaPaperConnectivityReviewSection = field(
        default_factory=lambda: AlpacaPaperConnectivityReviewSection("disconnect_recovery_review", 0, False)
    )
    session_integrity_review: AlpacaPaperConnectivityReviewSection = field(
        default_factory=lambda: AlpacaPaperConnectivityReviewSection("session_integrity_review", 0, False)
    )
    observability_review: AlpacaPaperConnectivityReviewSection = field(
        default_factory=lambda: AlpacaPaperConnectivityReviewSection("observability_review", 0, False)
    )
    kill_switch_compatibility_review: AlpacaPaperConnectivityReviewSection = field(
        default_factory=lambda: AlpacaPaperConnectivityReviewSection("kill_switch_compatibility_review", 0, False)
    )
    rollback_compatibility_review: AlpacaPaperConnectivityReviewSection = field(
        default_factory=lambda: AlpacaPaperConnectivityReviewSection("rollback_compatibility_review", 0, False)
    )
    connectivity_graph: AlpacaPaperConnectivityGraph = field(default_factory=AlpacaPaperConnectivityGraph)
    recommendations: tuple[AlpacaPaperConnectivityRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
