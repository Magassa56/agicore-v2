"""Models for the AGIcore Paper Broker Read-Only Connection Plan layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerReadOnlyConnectionPlanState(StrEnum):
    NOT_READY = "NOT_READY"
    CONNECTION_PLAN_INPUT_INVALID = "CONNECTION_PLAN_INPUT_INVALID"
    CONNECTION_PLAN_BLOCKED = "CONNECTION_PLAN_BLOCKED"
    CONNECTION_PLAN_COMPLETED_WITH_WARNINGS = "CONNECTION_PLAN_COMPLETED_WITH_WARNINGS"
    CONNECTION_PLAN_COMPLETED = "CONNECTION_PLAN_COMPLETED"
    READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE = (
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE"
    )


class PaperBrokerReadOnlyConnectionPlanDecision(StrEnum):
    BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN = "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN"
    REQUIRE_READ_ONLY_SAFETY_REVIEW_FIXES = "REQUIRE_READ_ONLY_SAFETY_REVIEW_FIXES"
    REQUIRE_SCOPE_FIXES = "REQUIRE_SCOPE_FIXES"
    REQUIRE_BOUNDARY_FIXES = "REQUIRE_BOUNDARY_FIXES"
    REQUIRE_PRECONDITION_FIXES = "REQUIRE_PRECONDITION_FIXES"
    REQUIRE_CREDENTIAL_REFERENCE_POLICY_FIXES = "REQUIRE_CREDENTIAL_REFERENCE_POLICY_FIXES"
    REQUIRE_NETWORK_BLOCK_POLICY_FIXES = "REQUIRE_NETWORK_BLOCK_POLICY_FIXES"
    REQUIRE_ACCOUNT_READ_ONLY_FIXES = "REQUIRE_ACCOUNT_READ_ONLY_FIXES"
    REQUIRE_MARKET_DATA_READ_ONLY_FIXES = "REQUIRE_MARKET_DATA_READ_ONLY_FIXES"
    REQUIRE_ORDER_BLOCKING_FIXES = "REQUIRE_ORDER_BLOCKING_FIXES"
    REQUIRE_POSITION_MUTATION_BLOCK_FIXES = "REQUIRE_POSITION_MUTATION_BLOCK_FIXES"
    REQUIRE_OBSERVABILITY_FIXES = "REQUIRE_OBSERVABILITY_FIXES"
    REQUIRE_JOURNAL_FIXES = "REQUIRE_JOURNAL_FIXES"
    REQUIRE_HUMAN_APPROVAL_FIXES = "REQUIRE_HUMAN_APPROVAL_FIXES"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN = "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN"


class PaperBrokerReadOnlyConnectionPlanRisk(StrEnum):
    READ_ONLY_SAFETY_REVIEW_NOT_APPROVED = "READ_ONLY_SAFETY_REVIEW_NOT_APPROVED"
    READ_ONLY_CONNECTION_SCOPE_UNCLEAR = "READ_ONLY_CONNECTION_SCOPE_UNCLEAR"
    CONNECTION_ENVIRONMENT_BOUNDARY_MISSING = "CONNECTION_ENVIRONMENT_BOUNDARY_MISSING"
    CONNECTION_PRECONDITION_MISSING = "CONNECTION_PRECONDITION_MISSING"
    CREDENTIAL_REFERENCE_POLICY_MISSING = "CREDENTIAL_REFERENCE_POLICY_MISSING"
    SECRET_READ_POLICY_UNSAFE = "SECRET_READ_POLICY_UNSAFE"
    NETWORK_EXECUTION_NOT_BLOCKED = "NETWORK_EXECUTION_NOT_BLOCKED"
    HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED = "HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED"
    ACCOUNT_READ_ONLY_CONNECTION_UNSAFE = "ACCOUNT_READ_ONLY_CONNECTION_UNSAFE"
    MARKET_DATA_READ_ONLY_CONNECTION_UNSAFE = "MARKET_DATA_READ_ONLY_CONNECTION_UNSAFE"
    ORDER_BLOCKING_CONNECTION_UNSAFE = "ORDER_BLOCKING_CONNECTION_UNSAFE"
    POSITION_MUTATION_BLOCK_UNSAFE = "POSITION_MUTATION_BLOCK_UNSAFE"
    OBSERVABILITY_PLAN_MISSING = "OBSERVABILITY_PLAN_MISSING"
    JOURNAL_PLAN_MISSING = "JOURNAL_PLAN_MISSING"
    HUMAN_APPROVAL_PLAN_MISSING = "HUMAN_APPROVAL_PLAN_MISSING"
    STOP_CONDITIONS_PLAN_MISSING = "STOP_CONDITIONS_PLAN_MISSING"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE = (
        "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE"
    )


class PaperBrokerReadOnlyConnectionPlanRecommendation(StrEnum):
    HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE = "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE"
    APPROVE_READ_ONLY_SAFETY_REVIEW_FIRST = "APPROVE_READ_ONLY_SAFETY_REVIEW_FIRST"
    CLARIFY_READ_ONLY_CONNECTION_SCOPE = "CLARIFY_READ_ONLY_CONNECTION_SCOPE"
    DEFINE_CONNECTION_ENVIRONMENT_BOUNDARIES = "DEFINE_CONNECTION_ENVIRONMENT_BOUNDARIES"
    DEFINE_CONNECTION_PRECONDITIONS = "DEFINE_CONNECTION_PRECONDITIONS"
    DEFINE_CREDENTIAL_REFERENCE_POLICY = "DEFINE_CREDENTIAL_REFERENCE_POLICY"
    HARDEN_NO_SECRET_READ_POLICY = "HARDEN_NO_SECRET_READ_POLICY"
    BLOCK_NETWORK_EXECUTION = "BLOCK_NETWORK_EXECUTION"
    BLOCK_HTTP_WEBSOCKET_SOCKET = "BLOCK_HTTP_WEBSOCKET_SOCKET"
    HARDEN_ACCOUNT_READ_ONLY_CONNECTION = "HARDEN_ACCOUNT_READ_ONLY_CONNECTION"
    HARDEN_MARKET_DATA_READ_ONLY_CONNECTION = "HARDEN_MARKET_DATA_READ_ONLY_CONNECTION"
    HARDEN_ORDER_BLOCKING_CONNECTION = "HARDEN_ORDER_BLOCKING_CONNECTION"
    HARDEN_POSITION_MUTATION_BLOCK = "HARDEN_POSITION_MUTATION_BLOCK"
    DEFINE_CONNECTION_OBSERVABILITY_PLAN = "DEFINE_CONNECTION_OBSERVABILITY_PLAN"
    DEFINE_CONNECTION_JOURNAL_PLAN = "DEFINE_CONNECTION_JOURNAL_PLAN"
    REQUIRE_CONNECTION_HUMAN_APPROVAL = "REQUIRE_CONNECTION_HUMAN_APPROVAL"
    DEFINE_CONNECTION_STOP_CONDITIONS = "DEFINE_CONNECTION_STOP_CONDITIONS"
    RESTORE_OFFLINE_BOUNDARIES = "RESTORE_OFFLINE_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE = (
        "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE"
    )
    RUN_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN_SUITE = "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN_SUITE"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE = (
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE"
    )


@dataclass(frozen=True)
class ReadOnlyConnectionScope:
    score: int = 0
    defined: bool = False
    plan_only: bool = True
    allowed_actions: tuple[str, ...] = ()
    prohibited_actions: tuple[str, ...] = ()
    risks: tuple[PaperBrokerReadOnlyConnectionPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConnectionEnvironmentBoundary:
    score: int = 0
    defined: bool = False
    offline_only: bool = True
    sandbox_only: bool = True
    connection_execution_disabled: bool = True
    network_transport_disabled: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConnectionPrecondition:
    score: int = 0
    defined: bool = False
    safety_review_required: bool = True
    human_approval_required: bool = True
    stop_conditions_required: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class CredentialsReferencePolicy:
    score: int = 0
    defined: bool = False
    reference_only: bool = True
    no_secret_material: bool = True
    no_api_key_read: bool = True
    no_env_var_read: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class NetworkExecutionBlockPolicy:
    score: int = 0
    defined: bool = False
    network_execution_blocked: bool = True
    http_blocked: bool = True
    websocket_blocked: bool = True
    socket_blocked: bool = True
    external_api_blocked: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class AccountReadOnlyConnectionPolicy:
    score: int = 0
    defined: bool = False
    active_account_access_blocked: bool = True
    account_mutations_blocked: bool = True
    read_only_future_plan: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class MarketDataReadOnlyConnectionPolicy:
    score: int = 0
    defined: bool = False
    read_only_market_data_plan: bool = True
    live_subscription_blocked: bool = True
    network_request_blocked: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class OrderBlockingConnectionPolicy:
    score: int = 0
    defined: bool = False
    order_execution_blocked: bool = True
    real_order_blocked: bool = True
    cancel_replace_blocked: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConnectionObservabilityPlan:
    score: int = 0
    defined: bool = False
    offline_events_planned: bool = True
    connection_attempt_logging_disabled: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConnectionJournalPlan:
    score: int = 0
    defined: bool = False
    offline_journal_required: bool = True
    sensitive_values_redacted: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConnectionHumanApprovalPlan:
    score: int = 0
    defined: bool = False
    human_approval_required: bool = True
    approval_before_safety_gate: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConnectionStopConditionPlan:
    score: int = 0
    defined: bool = False
    stop_on_secret_read: bool = True
    stop_on_network_request: bool = True
    stop_on_order_or_position_request: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionPlanScore:
    overall_score: int
    safety_review_score: int
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
class PaperBrokerReadOnlyConnectionPlanInput:
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
    read_only_safety_review_approved: bool | None = None
    read_only_connection_scope_defined: bool | None = None
    connection_environment_boundaries_defined: bool | None = None
    connection_preconditions_defined: bool | None = None
    credentials_reference_policy_defined: bool | None = None
    credentials_reference_only: bool | None = None
    no_secret_read_policy_defined: bool | None = None
    secret_read_blocked: bool | None = None
    network_execution_block_policy_defined: bool | None = None
    network_execution_blocked: bool | None = None
    http_websocket_socket_block_policy_defined: bool | None = None
    http_transport_blocked: bool | None = None
    websocket_transport_blocked: bool | None = None
    socket_transport_blocked: bool | None = None
    account_read_only_connection_policy_defined: bool | None = None
    account_active_access_blocked: bool | None = None
    account_mutations_blocked: bool | None = None
    market_data_read_only_connection_policy_defined: bool | None = None
    market_data_live_subscription_blocked: bool | None = None
    order_blocking_connection_policy_defined: bool | None = None
    order_execution_blocked: bool | None = None
    position_mutation_block_policy_defined: bool | None = None
    position_mutation_blocked: bool | None = None
    connection_observability_plan_defined: bool | None = None
    connection_journal_plan_defined: bool | None = None
    connection_human_approval_plan_defined: bool | None = None
    connection_stop_conditions_plan_defined: bool | None = None
    paper_broker_read_only_connection_safety_gate_requested: bool | None = False
    offline_mode_enforced: bool | None = None
    sandbox_mode_enforced: bool | None = None
    plan_only: bool | None = None
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
    safety_review_score: int | None = None
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
class PaperBrokerReadOnlyConnectionPlanResult:
    state: PaperBrokerReadOnlyConnectionPlanState
    decision: PaperBrokerReadOnlyConnectionPlanDecision
    connection_plan_score: int
    score_breakdown: PaperBrokerReadOnlyConnectionPlanScore
    risks: tuple[PaperBrokerReadOnlyConnectionPlanRisk, ...] = ()
    recommendations: tuple[PaperBrokerReadOnlyConnectionPlanRecommendation, ...] = ()
    connection_scope: ReadOnlyConnectionScope = field(default_factory=ReadOnlyConnectionScope)
    environment_boundaries: ConnectionEnvironmentBoundary = field(default_factory=ConnectionEnvironmentBoundary)
    connection_preconditions: ConnectionPrecondition = field(default_factory=ConnectionPrecondition)
    credentials_reference_policy: CredentialsReferencePolicy = field(default_factory=CredentialsReferencePolicy)
    no_secret_read_policy: CredentialsReferencePolicy = field(
        default_factory=lambda: CredentialsReferencePolicy(defined=False, reference_only=False)
    )
    network_execution_block_policy: NetworkExecutionBlockPolicy = field(default_factory=NetworkExecutionBlockPolicy)
    http_websocket_socket_block_policy: NetworkExecutionBlockPolicy = field(
        default_factory=lambda: NetworkExecutionBlockPolicy(defined=False)
    )
    account_read_only_connection_policy: AccountReadOnlyConnectionPolicy = field(
        default_factory=AccountReadOnlyConnectionPolicy
    )
    market_data_read_only_connection_policy: MarketDataReadOnlyConnectionPolicy = field(
        default_factory=MarketDataReadOnlyConnectionPolicy
    )
    order_blocking_connection_policy: OrderBlockingConnectionPolicy = field(default_factory=OrderBlockingConnectionPolicy)
    position_mutation_block_policy: OrderBlockingConnectionPolicy = field(
        default_factory=lambda: OrderBlockingConnectionPolicy(defined=False)
    )
    observability_plan: ConnectionObservabilityPlan = field(default_factory=ConnectionObservabilityPlan)
    journal_plan: ConnectionJournalPlan = field(default_factory=ConnectionJournalPlan)
    human_approval_plan: ConnectionHumanApprovalPlan = field(default_factory=ConnectionHumanApprovalPlan)
    stop_conditions_plan: ConnectionStopConditionPlan = field(default_factory=ConnectionStopConditionPlan)
    offline_only: bool = True
    summary: str = ""
