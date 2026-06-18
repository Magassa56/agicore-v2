"""Models for the offline AGIcore Paper Broker Sandbox Session Authorization Gate."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerSandboxSessionAuthorizationGateState(StrEnum):
    NOT_AUTHORIZED = "NOT_AUTHORIZED"
    AUTHORIZATION_REVIEW_REQUIRED = "AUTHORIZATION_REVIEW_REQUIRED"
    PARTIALLY_AUTHORIZED = "PARTIALLY_AUTHORIZED"
    SANDBOX_SESSION_AUTHORIZATION_READY = "SANDBOX_SESSION_AUTHORIZATION_READY"
    READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN = "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN"


class PaperBrokerSandboxSessionAuthorizationGateDecision(StrEnum):
    BLOCK_PAPER_BROKER_SANDBOX_SESSION = "BLOCK_PAPER_BROKER_SANDBOX_SESSION"
    REQUIRE_SANDBOX_REVIEW_FIXES = "REQUIRE_SANDBOX_REVIEW_FIXES"
    REQUIRE_SCOPE_FIXES = "REQUIRE_SCOPE_FIXES"
    REQUIRE_BOUNDARY_FIXES = "REQUIRE_BOUNDARY_FIXES"
    REQUIRE_CONNECTION_AUTHORIZATION_FIXES = "REQUIRE_CONNECTION_AUTHORIZATION_FIXES"
    REQUIRE_ORDER_AUTHORIZATION_FIXES = "REQUIRE_ORDER_AUTHORIZATION_FIXES"
    REQUIRE_POSITION_AUTHORIZATION_FIXES = "REQUIRE_POSITION_AUTHORIZATION_FIXES"
    REQUIRE_ACCOUNT_AUTHORIZATION_FIXES = "REQUIRE_ACCOUNT_AUTHORIZATION_FIXES"
    REQUIRE_OBSERVABILITY_AUTHORIZATION_FIXES = "REQUIRE_OBSERVABILITY_AUTHORIZATION_FIXES"
    REQUIRE_ROLLBACK_AUTHORIZATION_FIXES = "REQUIRE_ROLLBACK_AUTHORIZATION_FIXES"
    REQUIRE_KILL_SWITCH_AUTHORIZATION_FIXES = "REQUIRE_KILL_SWITCH_AUTHORIZATION_FIXES"
    REQUIRE_SUPERVISION_AUTHORIZATION_FIXES = "REQUIRE_SUPERVISION_AUTHORIZATION_FIXES"
    APPROVE_PAPER_BROKER_SANDBOX_AUTHORIZATION_GATE = "APPROVE_PAPER_BROKER_SANDBOX_AUTHORIZATION_GATE"


class PaperBrokerSandboxSessionAuthorizationGateRisk(StrEnum):
    SANDBOX_REVIEW_NOT_APPROVED = "SANDBOX_REVIEW_NOT_APPROVED"
    AUTHORIZATION_SCOPE_UNCLEAR = "AUTHORIZATION_SCOPE_UNCLEAR"
    AUTHORIZATION_BOUNDARY_GAP = "AUTHORIZATION_BOUNDARY_GAP"
    BROKER_CONNECTION_AUTHORIZATION_GAP = "BROKER_CONNECTION_AUTHORIZATION_GAP"
    ORDER_EXECUTION_AUTHORIZATION_GAP = "ORDER_EXECUTION_AUTHORIZATION_GAP"
    POSITION_MANAGEMENT_AUTHORIZATION_GAP = "POSITION_MANAGEMENT_AUTHORIZATION_GAP"
    ACCOUNT_ACCESS_AUTHORIZATION_GAP = "ACCOUNT_ACCESS_AUTHORIZATION_GAP"
    OBSERVABILITY_AUTHORIZATION_GAP = "OBSERVABILITY_AUTHORIZATION_GAP"
    ROLLBACK_AUTHORIZATION_GAP = "ROLLBACK_AUTHORIZATION_GAP"
    KILL_SWITCH_AUTHORIZATION_GAP = "KILL_SWITCH_AUTHORIZATION_GAP"
    HUMAN_SUPERVISION_AUTHORIZATION_GAP = "HUMAN_SUPERVISION_AUTHORIZATION_GAP"
    JOURNAL_AUTHORIZATION_GAP = "JOURNAL_AUTHORIZATION_GAP"
    STOP_CONDITIONS_AUTHORIZATION_GAP = "STOP_CONDITIONS_AUTHORIZATION_GAP"
    PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN = "PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN"


class PaperBrokerSandboxSessionAuthorizationGateRecommendation(StrEnum):
    HOLD_PAPER_BROKER_SANDBOX_DRY_RUN = "HOLD_PAPER_BROKER_SANDBOX_DRY_RUN"
    APPROVE_SANDBOX_SESSION_REVIEW_FIRST = "APPROVE_SANDBOX_SESSION_REVIEW_FIRST"
    CLARIFY_AUTHORIZATION_SCOPE = "CLARIFY_AUTHORIZATION_SCOPE"
    COMPLETE_AUTHORIZATION_BOUNDARIES = "COMPLETE_AUTHORIZATION_BOUNDARIES"
    COMPLETE_BROKER_CONNECTION_AUTHORIZATION = "COMPLETE_BROKER_CONNECTION_AUTHORIZATION"
    COMPLETE_ORDER_EXECUTION_AUTHORIZATION = "COMPLETE_ORDER_EXECUTION_AUTHORIZATION"
    COMPLETE_POSITION_MANAGEMENT_AUTHORIZATION = "COMPLETE_POSITION_MANAGEMENT_AUTHORIZATION"
    COMPLETE_ACCOUNT_ACCESS_AUTHORIZATION = "COMPLETE_ACCOUNT_ACCESS_AUTHORIZATION"
    COMPLETE_OBSERVABILITY_AUTHORIZATION = "COMPLETE_OBSERVABILITY_AUTHORIZATION"
    COMPLETE_ROLLBACK_AUTHORIZATION = "COMPLETE_ROLLBACK_AUTHORIZATION"
    COMPLETE_KILL_SWITCH_AUTHORIZATION = "COMPLETE_KILL_SWITCH_AUTHORIZATION"
    COMPLETE_HUMAN_SUPERVISION_AUTHORIZATION = "COMPLETE_HUMAN_SUPERVISION_AUTHORIZATION"
    COMPLETE_JOURNAL_AUTHORIZATION = "COMPLETE_JOURNAL_AUTHORIZATION"
    COMPLETE_STOP_CONDITIONS_AUTHORIZATION = "COMPLETE_STOP_CONDITIONS_AUTHORIZATION"
    DELAY_PAPER_BROKER_SANDBOX_DRY_RUN = "DELAY_PAPER_BROKER_SANDBOX_DRY_RUN"
    RUN_PAPER_BROKER_SANDBOX_AUTHORIZATION_GATE_SUITE = "RUN_PAPER_BROKER_SANDBOX_AUTHORIZATION_GATE_SUITE"
    APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN = "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN"


@dataclass(frozen=True)
class PaperBrokerSandboxSessionAuthorizationGateInput:
    paper_broker_sandbox_session_review: Any = None
    paper_broker_sandbox_session_preparation: Any = None
    paper_runtime_forward_test_plan: Any = None
    supervised_paper_runtime_trial: Any = None
    official_paper_validation_report: Any = None
    paper_runtime_validation: Any = None
    paper_runtime_release_candidate: Any = None
    paper_trading_runtime: Any = None
    paper_broker_adapter: Any = None
    alpaca_paper_adapter: Any = None
    broker_paper_sandbox: Any = None
    mock_alpaca_session: Any = None
    mock_connectivity_layer: Any = None
    observability_verification: Any = None
    rollback_verification: Any = None
    kill_switch_verification: Any = None
    human_validated_paper_session: Any = None
    supervised_paper_session: Any = None
    sandbox_review_approved: bool | None = None
    sandbox_reviewed: bool | None = None
    authorization_scope_reviewed: bool | None = None
    authorization_scope_clear: bool | None = None
    authorization_boundaries_reviewed: bool | None = None
    authorization_boundaries_complete: bool | None = None
    broker_connection_authorization_reviewed: bool | None = None
    broker_connection_authorized: bool | None = None
    order_execution_authorization_reviewed: bool | None = None
    order_execution_authorized: bool | None = None
    position_management_authorization_reviewed: bool | None = None
    position_management_authorized: bool | None = None
    account_access_authorization_reviewed: bool | None = None
    account_access_authorized: bool | None = None
    observability_authorization_reviewed: bool | None = None
    observability_authorized: bool | None = None
    rollback_authorization_reviewed: bool | None = None
    rollback_authorized: bool | None = None
    kill_switch_authorization_reviewed: bool | None = None
    kill_switch_authorized: bool | None = None
    human_supervision_authorization_reviewed: bool | None = None
    human_supervision_authorized: bool | None = None
    journal_authorization_reviewed: bool | None = None
    journal_authorized: bool | None = None
    stop_conditions_authorization_reviewed: bool | None = None
    stop_conditions_authorized: bool | None = None
    paper_broker_sandbox_dry_run_requested: bool | None = None
    sandbox_authorization_gate_requested: bool | None = None
    offline_mode_enforced: bool | None = None
    sandbox_mode_enforced: bool | None = None
    no_real_broker: bool | None = None
    no_alpaca_real: bool | None = None
    no_api_key_read: bool | None = None
    no_http_transport: bool | None = None
    no_websocket_transport: bool | None = None
    no_socket_transport: bool | None = None
    no_external_api: bool | None = None
    no_external_ml: bool | None = None
    no_external_llm: bool | None = None
    no_live_execution: bool | None = None
    no_real_order: bool | None = None
    no_real_account_access: bool | None = None
    sandbox_review_approval_score: int | None = None
    authorization_scope_score: int | None = None
    authorization_boundaries_score: int | None = None
    broker_connection_authorization_score: int | None = None
    order_execution_authorization_score: int | None = None
    position_management_authorization_score: int | None = None
    account_access_authorization_score: int | None = None
    observability_authorization_score: int | None = None
    rollback_authorization_score: int | None = None
    kill_switch_authorization_score: int | None = None
    human_supervision_authorization_score: int | None = None
    journal_authorization_score: int | None = None
    stop_conditions_authorization_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerSandboxSessionAuthorizationGateSection:
    name: str
    score: int
    authorized: bool
    risks: tuple[PaperBrokerSandboxSessionAuthorizationGateRisk, ...] = ()
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerSandboxSessionAuthorizationGateScore:
    overall_score: int
    sandbox_review_approval_score: int
    authorization_scope_score: int
    authorization_boundaries_score: int
    broker_connection_authorization_score: int
    order_execution_authorization_score: int
    position_management_authorization_score: int
    account_access_authorization_score: int
    observability_authorization_score: int
    rollback_authorization_score: int
    kill_switch_authorization_score: int
    human_supervision_authorization_score: int
    journal_authorization_score: int
    stop_conditions_authorization_score: int


@dataclass(frozen=True)
class PaperBrokerSandboxSessionAuthorizationGateResult:
    state: PaperBrokerSandboxSessionAuthorizationGateState
    decision: PaperBrokerSandboxSessionAuthorizationGateDecision
    authorization_score: int
    score_breakdown: PaperBrokerSandboxSessionAuthorizationGateScore
    risks: tuple[PaperBrokerSandboxSessionAuthorizationGateRisk, ...] = ()
    sandbox_review_approval: PaperBrokerSandboxSessionAuthorizationGateSection = field(
        default_factory=lambda: PaperBrokerSandboxSessionAuthorizationGateSection("sandbox_review_approval", 0, False)
    )
    authorization_scope: PaperBrokerSandboxSessionAuthorizationGateSection = field(
        default_factory=lambda: PaperBrokerSandboxSessionAuthorizationGateSection("authorization_scope", 0, False)
    )
    authorization_boundaries: PaperBrokerSandboxSessionAuthorizationGateSection = field(
        default_factory=lambda: PaperBrokerSandboxSessionAuthorizationGateSection("authorization_boundaries", 0, False)
    )
    broker_connection_authorization: PaperBrokerSandboxSessionAuthorizationGateSection = field(
        default_factory=lambda: PaperBrokerSandboxSessionAuthorizationGateSection("broker_connection_authorization", 0, False)
    )
    order_execution_authorization: PaperBrokerSandboxSessionAuthorizationGateSection = field(
        default_factory=lambda: PaperBrokerSandboxSessionAuthorizationGateSection("order_execution_authorization", 0, False)
    )
    position_management_authorization: PaperBrokerSandboxSessionAuthorizationGateSection = field(
        default_factory=lambda: PaperBrokerSandboxSessionAuthorizationGateSection("position_management_authorization", 0, False)
    )
    account_access_authorization: PaperBrokerSandboxSessionAuthorizationGateSection = field(
        default_factory=lambda: PaperBrokerSandboxSessionAuthorizationGateSection("account_access_authorization", 0, False)
    )
    observability_authorization: PaperBrokerSandboxSessionAuthorizationGateSection = field(
        default_factory=lambda: PaperBrokerSandboxSessionAuthorizationGateSection("observability_authorization", 0, False)
    )
    rollback_authorization: PaperBrokerSandboxSessionAuthorizationGateSection = field(
        default_factory=lambda: PaperBrokerSandboxSessionAuthorizationGateSection("rollback_authorization", 0, False)
    )
    kill_switch_authorization: PaperBrokerSandboxSessionAuthorizationGateSection = field(
        default_factory=lambda: PaperBrokerSandboxSessionAuthorizationGateSection("kill_switch_authorization", 0, False)
    )
    human_supervision_authorization: PaperBrokerSandboxSessionAuthorizationGateSection = field(
        default_factory=lambda: PaperBrokerSandboxSessionAuthorizationGateSection("human_supervision_authorization", 0, False)
    )
    journal_authorization: PaperBrokerSandboxSessionAuthorizationGateSection = field(
        default_factory=lambda: PaperBrokerSandboxSessionAuthorizationGateSection("journal_authorization", 0, False)
    )
    stop_conditions_authorization: PaperBrokerSandboxSessionAuthorizationGateSection = field(
        default_factory=lambda: PaperBrokerSandboxSessionAuthorizationGateSection("stop_conditions_authorization", 0, False)
    )
    recommendations: tuple[PaperBrokerSandboxSessionAuthorizationGateRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""

