"""Models for offline-first AGIcore broker paper sandbox readiness."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class BrokerPaperSandboxState(StrEnum):
    NOT_READY = "NOT_READY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    PARTIALLY_READY = "PARTIALLY_READY"
    SANDBOX_READY = "SANDBOX_READY"
    SANDBOX_VALIDATED = "SANDBOX_VALIDATED"
    READY_FOR_ALPACA_PAPER_CONNECTIVITY = "READY_FOR_ALPACA_PAPER_CONNECTIVITY"


class BrokerPaperSandboxRisk(StrEnum):
    ADAPTER_INCOMPATIBILITY = "ADAPTER_INCOMPATIBILITY"
    ORDER_TRANSLATION_FAILURE = "ORDER_TRANSLATION_FAILURE"
    POSITION_TRANSLATION_FAILURE = "POSITION_TRANSLATION_FAILURE"
    ACCOUNT_TRANSLATION_FAILURE = "ACCOUNT_TRANSLATION_FAILURE"
    SAFETY_BOUNDARY_MISSING = "SAFETY_BOUNDARY_MISSING"
    OBSERVABILITY_BOUNDARY_MISSING = "OBSERVABILITY_BOUNDARY_MISSING"
    KILL_SWITCH_BOUNDARY_MISSING = "KILL_SWITCH_BOUNDARY_MISSING"
    ROLLBACK_BOUNDARY_MISSING = "ROLLBACK_BOUNDARY_MISSING"
    SANDBOX_CONFIGURATION_DRIFT = "SANDBOX_CONFIGURATION_DRIFT"
    EXTERNAL_DEPENDENCY_RISK = "EXTERNAL_DEPENDENCY_RISK"


class BrokerPaperSandboxRecommendation(StrEnum):
    HOLD_ALPACA_CONNECTIVITY_APPROVAL = "HOLD_ALPACA_CONNECTIVITY_APPROVAL"
    REPAIR_ADAPTER_COMPATIBILITY = "REPAIR_ADAPTER_COMPATIBILITY"
    REPAIR_ORDER_TRANSLATION = "REPAIR_ORDER_TRANSLATION"
    REPAIR_POSITION_TRANSLATION = "REPAIR_POSITION_TRANSLATION"
    REPAIR_ACCOUNT_TRANSLATION = "REPAIR_ACCOUNT_TRANSLATION"
    DEFINE_SAFETY_BOUNDARY = "DEFINE_SAFETY_BOUNDARY"
    DEFINE_OBSERVABILITY_BOUNDARY = "DEFINE_OBSERVABILITY_BOUNDARY"
    DEFINE_KILL_SWITCH_BOUNDARY = "DEFINE_KILL_SWITCH_BOUNDARY"
    DEFINE_ROLLBACK_BOUNDARY = "DEFINE_ROLLBACK_BOUNDARY"
    LOCK_SANDBOX_CONFIGURATION = "LOCK_SANDBOX_CONFIGURATION"
    REMOVE_EXTERNAL_DEPENDENCY = "REMOVE_EXTERNAL_DEPENDENCY"
    RUN_BROKER_PAPER_SANDBOX_SUITE = "RUN_BROKER_PAPER_SANDBOX_SUITE"
    APPROVE_ALPACA_PAPER_CONNECTIVITY_AFTER_MANUAL_REVIEW = (
        "APPROVE_ALPACA_PAPER_CONNECTIVITY_AFTER_MANUAL_REVIEW"
    )


@dataclass(frozen=True)
class BrokerPaperSandboxInput:
    supervised_paper_trial: Any = None
    paper_dry_run: Any = None
    paper_trading_end_to_end: Any = None
    alpaca_paper_adapter: Any = None
    paper_broker_adapter: Any = None
    supervised_paper_session: Any = None
    human_validated_paper_session: Any = None
    controlled_paper_run: Any = None
    observability_verification: Any = None
    rollback_verification: Any = None
    kill_switch_verification: Any = None
    paper_broker_adapter_ready: bool | None = None
    alpaca_adapter_ready: bool | None = None
    adapter_contract_version_locked: bool | None = None
    sandbox_adapter_mode_enabled: bool | None = None
    order_mapping_defined: bool | None = None
    order_validation_defined: bool | None = None
    order_idempotency_defined: bool | None = None
    order_routing_disabled: bool | None = None
    position_mapping_defined: bool | None = None
    position_reconciliation_defined: bool | None = None
    position_checkpointing_defined: bool | None = None
    position_drift_monitoring_defined: bool | None = None
    account_mapping_defined: bool | None = None
    account_reconciliation_defined: bool | None = None
    buying_power_mapping_defined: bool | None = None
    account_state_checkpointing_defined: bool | None = None
    safety_prechecks_required: bool | None = None
    sandbox_order_limits_defined: bool | None = None
    no_live_order_route: bool | None = None
    no_api_keys_required: bool | None = None
    observability_events_defined: bool | None = None
    sandbox_metrics_defined: bool | None = None
    audit_trail_defined: bool | None = None
    critical_alerts_defined: bool | None = None
    kill_switch_linked: bool | None = None
    emergency_stop_path_defined: bool | None = None
    operator_halt_required: bool | None = None
    post_halt_state_safe: bool | None = None
    rollback_linked: bool | None = None
    recovery_point_required: bool | None = None
    rollback_audit_defined: bool | None = None
    restart_guard_defined: bool | None = None
    offline_mode_enforced: bool | None = None
    no_http_transport: bool | None = None
    no_websocket_transport: bool | None = None
    no_socket_transport: bool | None = None
    external_dependencies_blocked: bool | None = None
    configuration_locked: bool | None = None
    sandbox_validated: bool | None = None
    ready_for_alpaca_paper_connectivity: bool | None = None
    adapter_compatibility_score: int | None = None
    order_translation_score: int | None = None
    position_translation_score: int | None = None
    account_translation_score: int | None = None
    safety_boundary_score: int | None = None
    observability_boundary_score: int | None = None
    kill_switch_boundary_score: int | None = None
    rollback_boundary_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class BrokerPaperSandboxReviewSection:
    name: str
    score: int
    passed: bool
    risks: tuple[BrokerPaperSandboxRisk, ...] = ()
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class BrokerPaperSandboxGraph:
    nodes: tuple[str, ...] = ()
    edges: tuple[tuple[str, str, str], ...] = ()
    ready_edges: tuple[tuple[str, str], ...] = ()
    blocked_edges: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class BrokerPaperSandboxScore:
    overall_score: int
    adapter_compatibility_score: int
    order_translation_score: int
    position_translation_score: int
    account_translation_score: int
    safety_boundary_score: int
    observability_boundary_score: int
    kill_switch_boundary_score: int
    rollback_boundary_score: int


@dataclass(frozen=True)
class BrokerPaperSandboxResult:
    state: BrokerPaperSandboxState
    sandbox_score: int
    score_breakdown: BrokerPaperSandboxScore
    risks: tuple[BrokerPaperSandboxRisk, ...] = ()
    adapter_compatibility_review: BrokerPaperSandboxReviewSection = field(
        default_factory=lambda: BrokerPaperSandboxReviewSection("adapter_compatibility_review", 0, False)
    )
    order_translation_review: BrokerPaperSandboxReviewSection = field(
        default_factory=lambda: BrokerPaperSandboxReviewSection("order_translation_review", 0, False)
    )
    position_translation_review: BrokerPaperSandboxReviewSection = field(
        default_factory=lambda: BrokerPaperSandboxReviewSection("position_translation_review", 0, False)
    )
    account_translation_review: BrokerPaperSandboxReviewSection = field(
        default_factory=lambda: BrokerPaperSandboxReviewSection("account_translation_review", 0, False)
    )
    safety_boundaries_review: BrokerPaperSandboxReviewSection = field(
        default_factory=lambda: BrokerPaperSandboxReviewSection("safety_boundaries_review", 0, False)
    )
    observability_boundaries_review: BrokerPaperSandboxReviewSection = field(
        default_factory=lambda: BrokerPaperSandboxReviewSection("observability_boundaries_review", 0, False)
    )
    kill_switch_boundaries_review: BrokerPaperSandboxReviewSection = field(
        default_factory=lambda: BrokerPaperSandboxReviewSection("kill_switch_boundaries_review", 0, False)
    )
    rollback_boundaries_review: BrokerPaperSandboxReviewSection = field(
        default_factory=lambda: BrokerPaperSandboxReviewSection("rollback_boundaries_review", 0, False)
    )
    sandbox_graph: BrokerPaperSandboxGraph = field(default_factory=BrokerPaperSandboxGraph)
    recommendations: tuple[BrokerPaperSandboxRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
