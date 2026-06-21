"""Models for the AGIcore Paper Broker Read-Only Connection Safety Gate."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerReadOnlyConnectionSafetyGateState(StrEnum):
    NOT_READY = "NOT_READY"
    CONNECTION_SAFETY_INPUT_INVALID = "CONNECTION_SAFETY_INPUT_INVALID"
    CONNECTION_SAFETY_BLOCKED = "CONNECTION_SAFETY_BLOCKED"
    CONNECTION_SAFETY_COMPLETED_WITH_WARNINGS = "CONNECTION_SAFETY_COMPLETED_WITH_WARNINGS"
    CONNECTION_SAFETY_COMPLETED = "CONNECTION_SAFETY_COMPLETED"
    READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION = (
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION"
    )


class PaperBrokerReadOnlyConnectionSafetyGateDecision(StrEnum):
    BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE = "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE"
    REQUIRE_CONNECTION_PLAN_FIXES = "REQUIRE_CONNECTION_PLAN_FIXES"
    REQUIRE_SCOPE_SAFETY_FIXES = "REQUIRE_SCOPE_SAFETY_FIXES"
    REQUIRE_BOUNDARY_SAFETY_FIXES = "REQUIRE_BOUNDARY_SAFETY_FIXES"
    REQUIRE_PRECONDITION_SAFETY_FIXES = "REQUIRE_PRECONDITION_SAFETY_FIXES"
    REQUIRE_CREDENTIAL_REFERENCE_FIXES = "REQUIRE_CREDENTIAL_REFERENCE_FIXES"
    REQUIRE_SECRET_READ_BLOCK_FIXES = "REQUIRE_SECRET_READ_BLOCK_FIXES"
    REQUIRE_NETWORK_BLOCK_FIXES = "REQUIRE_NETWORK_BLOCK_FIXES"
    REQUIRE_ACCOUNT_READ_ONLY_FIXES = "REQUIRE_ACCOUNT_READ_ONLY_FIXES"
    REQUIRE_MARKET_DATA_READ_ONLY_FIXES = "REQUIRE_MARKET_DATA_READ_ONLY_FIXES"
    REQUIRE_ORDER_BLOCKING_FIXES = "REQUIRE_ORDER_BLOCKING_FIXES"
    REQUIRE_POSITION_MUTATION_BLOCK_FIXES = "REQUIRE_POSITION_MUTATION_BLOCK_FIXES"
    REQUIRE_HUMAN_APPROVAL_FIXES = "REQUIRE_HUMAN_APPROVAL_FIXES"
    REQUIRE_STOP_CONDITION_FIXES = "REQUIRE_STOP_CONDITION_FIXES"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE = (
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE"
    )


class PaperBrokerReadOnlyConnectionSafetyGateRisk(StrEnum):
    READ_ONLY_CONNECTION_PLAN_NOT_APPROVED = "READ_ONLY_CONNECTION_PLAN_NOT_APPROVED"
    CONNECTION_SCOPE_UNSAFE = "CONNECTION_SCOPE_UNSAFE"
    CONNECTION_ENVIRONMENT_BOUNDARY_UNSAFE = "CONNECTION_ENVIRONMENT_BOUNDARY_UNSAFE"
    CONNECTION_PRECONDITION_UNSAFE = "CONNECTION_PRECONDITION_UNSAFE"
    CREDENTIAL_REFERENCE_UNSAFE = "CREDENTIAL_REFERENCE_UNSAFE"
    SECRET_READ_POLICY_UNSAFE = "SECRET_READ_POLICY_UNSAFE"
    NETWORK_EXECUTION_NOT_BLOCKED = "NETWORK_EXECUTION_NOT_BLOCKED"
    HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED = "HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED"
    ACCOUNT_READ_ONLY_CONNECTION_UNSAFE = "ACCOUNT_READ_ONLY_CONNECTION_UNSAFE"
    MARKET_DATA_READ_ONLY_CONNECTION_UNSAFE = "MARKET_DATA_READ_ONLY_CONNECTION_UNSAFE"
    ORDER_BLOCKING_CONNECTION_UNSAFE = "ORDER_BLOCKING_CONNECTION_UNSAFE"
    POSITION_MUTATION_BLOCK_UNSAFE = "POSITION_MUTATION_BLOCK_UNSAFE"
    OBSERVABILITY_CONNECTION_INCOMPLETE = "OBSERVABILITY_CONNECTION_INCOMPLETE"
    JOURNAL_CONNECTION_INCOMPLETE = "JOURNAL_CONNECTION_INCOMPLETE"
    HUMAN_APPROVAL_CONNECTION_MISSING = "HUMAN_APPROVAL_CONNECTION_MISSING"
    STOP_CONDITIONS_CONNECTION_MISSING = "STOP_CONDITIONS_CONNECTION_MISSING"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION = (
        "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION"
    )


class PaperBrokerReadOnlyConnectionSafetyGateRecommendation(StrEnum):
    HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION = "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION"
    APPROVE_CONNECTION_PLAN_FIRST = "APPROVE_CONNECTION_PLAN_FIRST"
    HARDEN_CONNECTION_SCOPE = "HARDEN_CONNECTION_SCOPE"
    HARDEN_CONNECTION_BOUNDARIES = "HARDEN_CONNECTION_BOUNDARIES"
    HARDEN_CONNECTION_PRECONDITIONS = "HARDEN_CONNECTION_PRECONDITIONS"
    HARDEN_CREDENTIAL_REFERENCE = "HARDEN_CREDENTIAL_REFERENCE"
    HARDEN_SECRET_READ_BLOCK = "HARDEN_SECRET_READ_BLOCK"
    BLOCK_NETWORK_EXECUTION = "BLOCK_NETWORK_EXECUTION"
    BLOCK_HTTP_WEBSOCKET_SOCKET = "BLOCK_HTTP_WEBSOCKET_SOCKET"
    HARDEN_ACCOUNT_READ_ONLY_CONNECTION = "HARDEN_ACCOUNT_READ_ONLY_CONNECTION"
    HARDEN_MARKET_DATA_READ_ONLY_CONNECTION = "HARDEN_MARKET_DATA_READ_ONLY_CONNECTION"
    HARDEN_ORDER_BLOCKING_CONNECTION = "HARDEN_ORDER_BLOCKING_CONNECTION"
    HARDEN_POSITION_MUTATION_BLOCK = "HARDEN_POSITION_MUTATION_BLOCK"
    COMPLETE_CONNECTION_OBSERVABILITY = "COMPLETE_CONNECTION_OBSERVABILITY"
    COMPLETE_CONNECTION_JOURNAL = "COMPLETE_CONNECTION_JOURNAL"
    REQUIRE_CONNECTION_HUMAN_APPROVAL = "REQUIRE_CONNECTION_HUMAN_APPROVAL"
    DEFINE_CONNECTION_STOP_CONDITIONS = "DEFINE_CONNECTION_STOP_CONDITIONS"
    RESTORE_OFFLINE_BOUNDARIES = "RESTORE_OFFLINE_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION = (
        "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION"
    )
    RUN_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE_SUITE = (
        "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE_SUITE"
    )
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION = (
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION"
    )


@dataclass(frozen=True)
class ConnectionScopeSafetyFinding:
    score: int = 0
    passed: bool = False
    plan_only: bool = True
    prohibited_actions_confirmed: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionSafetyGateRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConnectionBoundarySafetyFinding:
    score: int = 0
    passed: bool = False
    offline_only: bool = False
    sandbox_only: bool = False
    connection_execution_disabled: bool = False
    network_transport_disabled: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionSafetyGateRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class CredentialsReferenceSafetyFinding:
    score: int = 0
    passed: bool = False
    reference_only: bool = False
    no_secret_material: bool = False
    no_api_key_read: bool = False
    no_env_var_read: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionSafetyGateRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class NetworkBlockSafetyFinding:
    score: int = 0
    passed: bool = False
    network_execution_blocked: bool = False
    http_blocked: bool = False
    websocket_blocked: bool = False
    socket_blocked: bool = False
    external_api_blocked: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionSafetyGateRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class AccountReadOnlyConnectionSafetyFinding:
    score: int = 0
    passed: bool = False
    active_account_access_blocked: bool = False
    account_mutations_blocked: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionSafetyGateRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class MarketDataReadOnlyConnectionSafetyFinding:
    score: int = 0
    passed: bool = False
    read_only_market_data_plan: bool = False
    live_subscription_blocked: bool = False
    network_request_blocked: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionSafetyGateRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class OrderBlockingConnectionSafetyFinding:
    score: int = 0
    passed: bool = False
    order_execution_blocked: bool = False
    real_order_blocked: bool = False
    cancel_replace_blocked: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionSafetyGateRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class PositionMutationBlockSafetyFinding:
    score: int = 0
    passed: bool = False
    position_mutation_blocked: bool = False
    position_request_absent: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionSafetyGateRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class HumanApprovalConnectionSafetyFinding:
    score: int = 0
    passed: bool = False
    human_approval_required: bool = False
    approval_before_preparation: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionSafetyGateRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class StopConditionConnectionSafetyFinding:
    score: int = 0
    passed: bool = False
    stop_on_secret_read: bool = False
    stop_on_network_request: bool = False
    stop_on_order_or_position_request: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionSafetyGateRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionSafetyGateScore:
    overall_score: int
    connection_plan_score: int
    scope_score: int
    boundary_score: int
    precondition_score: int
    credential_reference_score: int
    no_secret_read_score: int
    network_block_score: int
    http_websocket_socket_block_score: int
    account_read_only_score: int
    market_data_read_only_score: int
    order_blocking_score: int
    position_mutation_block_score: int
    observability_score: int
    journal_score: int
    human_approval_score: int
    stop_conditions_score: int


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionSafetyGateInput:
    paper_broker_read_only_connection_plan: Any = None
    paper_broker_read_only_safety_review: Any = None
    paper_broker_read_only_preparation: Any = None
    multi_scenario_result_report: Any = None
    multi_scenario_controlled_simulation_result: Any = None
    performance_risk_validation_gate: Any = None
    performance_metrics_result: Any = None
    risk_metrics_result: Any = None
    controlled_simulation_result_report: Any = None
    controlled_simulation_offline_runner_result: Any = None
    paper_runtime_forward_test_plan: Any = None
    official_paper_validation_report: Any = None
    paper_runtime_validation: Any = None
    paper_trading_runtime: Any = None
    observability_verification: Any = None
    rollback_verification: Any = None
    kill_switch_verification: Any = None
    human_validated_paper_session: Any = None
    supervised_paper_session: Any = None
    read_only_connection_plan_approved: bool | None = None
    connection_scope_safety_verified: bool | None = None
    connection_environment_boundary_safety_verified: bool | None = None
    connection_precondition_safety_verified: bool | None = None
    credentials_reference_safety_verified: bool | None = None
    no_secret_read_safety_verified: bool | None = None
    network_execution_block_safety_verified: bool | None = None
    http_websocket_socket_block_safety_verified: bool | None = None
    account_read_only_connection_safety_verified: bool | None = None
    market_data_read_only_connection_safety_verified: bool | None = None
    order_blocking_connection_safety_verified: bool | None = None
    position_mutation_block_safety_verified: bool | None = None
    observability_connection_safety_verified: bool | None = None
    journal_connection_safety_verified: bool | None = None
    human_approval_connection_safety_verified: bool | None = None
    stop_conditions_connection_safety_verified: bool | None = None
    paper_broker_read_only_connection_preparation_requested: bool | None = False
    offline_mode_enforced: bool | None = None
    sandbox_mode_enforced: bool | None = None
    safety_gate_only: bool | None = None
    broker_connection_disabled: bool | None = None
    no_real_broker: bool | None = None
    no_alpaca_real: bool | None = None
    no_api_key_read: bool | None = None
    no_env_var_read: bool | None = None
    no_hardcoded_secrets: bool | None = None
    no_http_transport: bool | None = None
    no_websocket_transport: bool | None = None
    no_socket_transport: bool | None = None
    no_external_api: bool | None = None
    no_external_ml: bool | None = None
    no_external_llm: bool | None = None
    no_live_execution: bool | None = None
    no_real_order: bool | None = None
    no_position_mutation: bool | None = None
    no_real_account_access: bool | None = None
    data_access_requested: bool | None = False
    real_execution_requested: bool | None = False
    broker_connection_requested: bool | None = False
    api_key_read_requested: bool | None = False
    env_var_read_requested: bool | None = False
    hardcoded_secret_detected: bool | None = False
    order_execution_requested: bool | None = False
    position_mutation_requested: bool | None = False
    account_access_requested: bool | None = False
    network_transport_requested: bool | None = False
    connection_plan_score: int | None = None
    scope_score: int | None = None
    boundary_score: int | None = None
    precondition_score: int | None = None
    credential_reference_score: int | None = None
    no_secret_read_score: int | None = None
    network_block_score: int | None = None
    http_websocket_socket_block_score: int | None = None
    account_read_only_score: int | None = None
    market_data_read_only_score: int | None = None
    order_blocking_score: int | None = None
    position_mutation_block_score: int | None = None
    observability_score: int | None = None
    journal_score: int | None = None
    human_approval_score: int | None = None
    stop_conditions_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionSafetyGateResult:
    state: PaperBrokerReadOnlyConnectionSafetyGateState
    decision: PaperBrokerReadOnlyConnectionSafetyGateDecision
    safety_gate_score: int
    score_breakdown: PaperBrokerReadOnlyConnectionSafetyGateScore
    risks: tuple[PaperBrokerReadOnlyConnectionSafetyGateRisk, ...] = ()
    recommendations: tuple[PaperBrokerReadOnlyConnectionSafetyGateRecommendation, ...] = ()
    scope_safety: ConnectionScopeSafetyFinding = field(default_factory=ConnectionScopeSafetyFinding)
    boundary_safety: ConnectionBoundarySafetyFinding = field(default_factory=ConnectionBoundarySafetyFinding)
    precondition_safety: ConnectionScopeSafetyFinding = field(default_factory=ConnectionScopeSafetyFinding)
    credential_reference_safety: CredentialsReferenceSafetyFinding = field(
        default_factory=CredentialsReferenceSafetyFinding
    )
    no_secret_read_safety: CredentialsReferenceSafetyFinding = field(default_factory=CredentialsReferenceSafetyFinding)
    network_block_safety: NetworkBlockSafetyFinding = field(default_factory=NetworkBlockSafetyFinding)
    http_websocket_socket_block_safety: NetworkBlockSafetyFinding = field(default_factory=NetworkBlockSafetyFinding)
    account_read_only_safety: AccountReadOnlyConnectionSafetyFinding = field(
        default_factory=AccountReadOnlyConnectionSafetyFinding
    )
    market_data_read_only_safety: MarketDataReadOnlyConnectionSafetyFinding = field(
        default_factory=MarketDataReadOnlyConnectionSafetyFinding
    )
    order_blocking_safety: OrderBlockingConnectionSafetyFinding = field(
        default_factory=OrderBlockingConnectionSafetyFinding
    )
    position_mutation_block_safety: PositionMutationBlockSafetyFinding = field(
        default_factory=PositionMutationBlockSafetyFinding
    )
    observability_safety: ConnectionScopeSafetyFinding = field(default_factory=ConnectionScopeSafetyFinding)
    journal_safety: ConnectionScopeSafetyFinding = field(default_factory=ConnectionScopeSafetyFinding)
    human_approval_safety: HumanApprovalConnectionSafetyFinding = field(
        default_factory=HumanApprovalConnectionSafetyFinding
    )
    stop_conditions_safety: StopConditionConnectionSafetyFinding = field(
        default_factory=StopConditionConnectionSafetyFinding
    )
    offline_only: bool = True
    summary: str = ""
