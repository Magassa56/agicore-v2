"""Models for the AGIcore Paper Broker Read-Only Connection Preparation layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerReadOnlyConnectionPreparationState(StrEnum):
    NOT_READY = "NOT_READY"
    CONNECTION_PREPARATION_INPUT_INVALID = "CONNECTION_PREPARATION_INPUT_INVALID"
    CONNECTION_PREPARATION_BLOCKED = "CONNECTION_PREPARATION_BLOCKED"
    CONNECTION_PREPARATION_COMPLETED_WITH_WARNINGS = "CONNECTION_PREPARATION_COMPLETED_WITH_WARNINGS"
    CONNECTION_PREPARATION_COMPLETED = "CONNECTION_PREPARATION_COMPLETED"
    READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW = (
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW"
    )


class PaperBrokerReadOnlyConnectionPreparationDecision(StrEnum):
    BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION = "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION"
    REQUIRE_CONNECTION_SAFETY_GATE_FIXES = "REQUIRE_CONNECTION_SAFETY_GATE_FIXES"
    REQUIRE_CONNECTION_CONTRACT_FIXES = "REQUIRE_CONNECTION_CONTRACT_FIXES"
    REQUIRE_BROKER_ADAPTER_BOUNDARY_FIXES = "REQUIRE_BROKER_ADAPTER_BOUNDARY_FIXES"
    REQUIRE_CONFIGURATION_SCHEMA_FIXES = "REQUIRE_CONFIGURATION_SCHEMA_FIXES"
    REQUIRE_CREDENTIAL_REFERENCE_CONTRACT_FIXES = "REQUIRE_CREDENTIAL_REFERENCE_CONTRACT_FIXES"
    REQUIRE_NO_SECRET_READ_GUARD_FIXES = "REQUIRE_NO_SECRET_READ_GUARD_FIXES"
    REQUIRE_NETWORK_BLOCK_GUARD_FIXES = "REQUIRE_NETWORK_BLOCK_GUARD_FIXES"
    REQUIRE_ACCOUNT_READ_ONLY_CONTRACT_FIXES = "REQUIRE_ACCOUNT_READ_ONLY_CONTRACT_FIXES"
    REQUIRE_MARKET_DATA_READ_ONLY_CONTRACT_FIXES = "REQUIRE_MARKET_DATA_READ_ONLY_CONTRACT_FIXES"
    REQUIRE_ORDER_BLOCKING_CONTRACT_FIXES = "REQUIRE_ORDER_BLOCKING_CONTRACT_FIXES"
    REQUIRE_POSITION_MUTATION_BLOCK_FIXES = "REQUIRE_POSITION_MUTATION_BLOCK_FIXES"
    REQUIRE_OBSERVABILITY_CONTRACT_FIXES = "REQUIRE_OBSERVABILITY_CONTRACT_FIXES"
    REQUIRE_JOURNAL_CONTRACT_FIXES = "REQUIRE_JOURNAL_CONTRACT_FIXES"
    REQUIRE_HUMAN_APPROVAL_CONTRACT_FIXES = "REQUIRE_HUMAN_APPROVAL_CONTRACT_FIXES"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION = (
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION"
    )


class PaperBrokerReadOnlyConnectionPreparationRisk(StrEnum):
    CONNECTION_SAFETY_GATE_NOT_APPROVED = "CONNECTION_SAFETY_GATE_NOT_APPROVED"
    READ_ONLY_CONNECTION_CONTRACT_MISSING = "READ_ONLY_CONNECTION_CONTRACT_MISSING"
    BROKER_ADAPTER_BOUNDARY_UNSAFE = "BROKER_ADAPTER_BOUNDARY_UNSAFE"
    CONNECTION_CONFIGURATION_SCHEMA_UNSAFE = "CONNECTION_CONFIGURATION_SCHEMA_UNSAFE"
    CREDENTIAL_REFERENCE_CONTRACT_UNSAFE = "CREDENTIAL_REFERENCE_CONTRACT_UNSAFE"
    SECRET_READ_GUARD_MISSING = "SECRET_READ_GUARD_MISSING"
    NETWORK_EXECUTION_BLOCK_GUARD_MISSING = "NETWORK_EXECUTION_BLOCK_GUARD_MISSING"
    HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_MISSING = "HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_MISSING"
    ACCOUNT_READ_ONLY_CONTRACT_UNSAFE = "ACCOUNT_READ_ONLY_CONTRACT_UNSAFE"
    MARKET_DATA_READ_ONLY_CONTRACT_UNSAFE = "MARKET_DATA_READ_ONLY_CONTRACT_UNSAFE"
    ORDER_BLOCKING_CONTRACT_UNSAFE = "ORDER_BLOCKING_CONTRACT_UNSAFE"
    POSITION_MUTATION_BLOCK_CONTRACT_UNSAFE = "POSITION_MUTATION_BLOCK_CONTRACT_UNSAFE"
    OBSERVABILITY_CONTRACT_INCOMPLETE = "OBSERVABILITY_CONTRACT_INCOMPLETE"
    JOURNAL_CONTRACT_INCOMPLETE = "JOURNAL_CONTRACT_INCOMPLETE"
    HUMAN_APPROVAL_CONTRACT_MISSING = "HUMAN_APPROVAL_CONTRACT_MISSING"
    STOP_CONDITION_CONTRACT_MISSING = "STOP_CONDITION_CONTRACT_MISSING"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW = (
        "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW"
    )


class PaperBrokerReadOnlyConnectionPreparationRecommendation(StrEnum):
    HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION = "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION"
    APPROVE_CONNECTION_SAFETY_GATE_FIRST = "APPROVE_CONNECTION_SAFETY_GATE_FIRST"
    PREPARE_READ_ONLY_CONNECTION_CONTRACT = "PREPARE_READ_ONLY_CONNECTION_CONTRACT"
    HARDEN_BROKER_ADAPTER_BOUNDARY = "HARDEN_BROKER_ADAPTER_BOUNDARY"
    HARDEN_CONNECTION_CONFIGURATION_SCHEMA = "HARDEN_CONNECTION_CONFIGURATION_SCHEMA"
    HARDEN_CREDENTIAL_REFERENCE_CONTRACT = "HARDEN_CREDENTIAL_REFERENCE_CONTRACT"
    INSTALL_NO_SECRET_READ_GUARD = "INSTALL_NO_SECRET_READ_GUARD"
    INSTALL_NETWORK_EXECUTION_BLOCK_GUARD = "INSTALL_NETWORK_EXECUTION_BLOCK_GUARD"
    INSTALL_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD = "INSTALL_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD"
    HARDEN_ACCOUNT_READ_ONLY_CONTRACT = "HARDEN_ACCOUNT_READ_ONLY_CONTRACT"
    HARDEN_MARKET_DATA_READ_ONLY_CONTRACT = "HARDEN_MARKET_DATA_READ_ONLY_CONTRACT"
    HARDEN_ORDER_BLOCKING_CONTRACT = "HARDEN_ORDER_BLOCKING_CONTRACT"
    HARDEN_POSITION_MUTATION_BLOCK_CONTRACT = "HARDEN_POSITION_MUTATION_BLOCK_CONTRACT"
    COMPLETE_CONNECTION_OBSERVABILITY_CONTRACT = "COMPLETE_CONNECTION_OBSERVABILITY_CONTRACT"
    COMPLETE_CONNECTION_JOURNAL_CONTRACT = "COMPLETE_CONNECTION_JOURNAL_CONTRACT"
    REQUIRE_CONNECTION_HUMAN_APPROVAL = "REQUIRE_CONNECTION_HUMAN_APPROVAL"
    DEFINE_CONNECTION_STOP_CONDITIONS = "DEFINE_CONNECTION_STOP_CONDITIONS"
    RESTORE_OFFLINE_BOUNDARIES = "RESTORE_OFFLINE_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW = (
        "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW"
    )
    RUN_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_SUITE = (
        "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_SUITE"
    )
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW = (
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW"
    )


@dataclass(frozen=True)
class ReadOnlyConnectionContract:
    name: str = "read_only_connection_contract"
    score: int = 0
    defined: bool = False
    preparation_only: bool = True
    read_only_only: bool = True
    no_connection_execution: bool = True
    allowed_actions: tuple[str, ...] = ()
    prohibited_actions: tuple[str, ...] = ()
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class BrokerAdapterBoundary:
    name: str = "broker_adapter_boundary"
    score: int = 0
    defined: bool = False
    no_real_broker: bool = True
    no_alpaca_real: bool = True
    adapter_instantiation_blocked: bool = True
    network_transport_blocked: bool = True
    paper_only_future_reference: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConnectionConfigurationSchema:
    name: str = "connection_configuration_schema"
    score: int = 0
    defined: bool = False
    schema_only: bool = True
    env_var_read_blocked: bool = True
    api_key_value_absent: bool = True
    network_fields_reference_only: bool = True
    required_fields: tuple[str, ...] = ()
    prohibited_fields: tuple[str, ...] = ()
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class CredentialsReferenceContract:
    name: str = "credentials_reference_contract"
    score: int = 0
    defined: bool = False
    reference_only: bool = True
    no_secret_values: bool = True
    no_api_key_read: bool = True
    no_env_var_read: bool = True
    secret_source: str = "none_in_this_phase"
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class NoSecretReadGuard:
    name: str = "no_secret_read_guard"
    score: int = 0
    defined: bool = False
    no_api_key_read: bool = True
    no_env_var_read: bool = True
    no_hardcoded_secret: bool = True
    guard_enforced: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class NetworkExecutionBlockGuard:
    name: str = "network_execution_block_guard"
    score: int = 0
    defined: bool = False
    network_execution_blocked: bool = True
    http_blocked: bool = True
    websocket_blocked: bool = True
    socket_blocked: bool = True
    external_api_blocked: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class AccountReadOnlyContract:
    name: str = "account_read_only_contract"
    score: int = 0
    defined: bool = False
    active_account_access_blocked: bool = True
    account_mutations_blocked: bool = True
    read_only_schema_only: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class MarketDataReadOnlyContract:
    name: str = "market_data_read_only_contract"
    score: int = 0
    defined: bool = False
    read_only_market_data_only: bool = True
    live_subscription_blocked: bool = True
    network_request_blocked: bool = True
    synthetic_or_schema_only: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class OrderBlockingContract:
    name: str = "order_blocking_contract"
    score: int = 0
    defined: bool = False
    order_execution_blocked: bool = True
    real_order_blocked: bool = True
    cancel_replace_blocked: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class PositionMutationBlockContract:
    name: str = "position_mutation_block_contract"
    score: int = 0
    defined: bool = False
    position_mutation_blocked: bool = True
    position_request_absent: bool = True
    close_modify_blocked: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConnectionObservabilityContract:
    name: str = "connection_observability_contract"
    score: int = 0
    defined: bool = False
    offline_events_defined: bool = True
    connection_attempt_logging_disabled: bool = True
    sensitive_values_redacted: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConnectionJournalContract:
    name: str = "connection_journal_contract"
    score: int = 0
    defined: bool = False
    offline_journal_required: bool = True
    sensitive_values_redacted: bool = True
    no_secret_material_logged: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConnectionHumanApprovalContract:
    name: str = "connection_human_approval_contract"
    score: int = 0
    defined: bool = False
    human_approval_required: bool = True
    approval_before_review: bool = True
    safety_gate_evidence_required: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConnectionStopConditionContract:
    name: str = "connection_stop_conditions_contract"
    score: int = 0
    defined: bool = False
    stop_on_secret_read: bool = True
    stop_on_network_request: bool = True
    stop_on_order_or_position_request: bool = True
    stop_on_account_access_request: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionPreparationScore:
    overall_score: int
    connection_safety_gate_score: int
    connection_contract_score: int
    broker_adapter_boundary_score: int
    configuration_schema_score: int
    credential_reference_contract_score: int
    no_secret_read_guard_score: int
    network_block_guard_score: int
    http_websocket_socket_block_guard_score: int
    account_read_only_contract_score: int
    market_data_read_only_contract_score: int
    order_blocking_contract_score: int
    position_mutation_block_score: int
    observability_contract_score: int
    journal_contract_score: int
    human_approval_contract_score: int
    stop_conditions_contract_score: int


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionPreparationInput:
    paper_broker_read_only_connection_safety_gate: Any = None
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
    connection_safety_gate_approved: bool | None = None
    read_only_connection_contract_prepared: bool | None = None
    broker_adapter_boundary_prepared: bool | None = None
    connection_configuration_schema_prepared: bool | None = None
    credentials_reference_contract_prepared: bool | None = None
    credentials_reference_only: bool | None = None
    no_secret_read_guard_prepared: bool | None = None
    secret_read_guard_enforced: bool | None = None
    network_execution_block_guard_prepared: bool | None = None
    network_execution_blocked: bool | None = None
    http_websocket_socket_block_guard_prepared: bool | None = None
    http_transport_blocked: bool | None = None
    websocket_transport_blocked: bool | None = None
    socket_transport_blocked: bool | None = None
    account_read_only_contract_prepared: bool | None = None
    account_active_access_blocked: bool | None = None
    account_mutations_blocked: bool | None = None
    market_data_read_only_contract_prepared: bool | None = None
    market_data_live_subscription_blocked: bool | None = None
    market_data_network_request_blocked: bool | None = None
    order_blocking_contract_prepared: bool | None = None
    order_execution_blocked: bool | None = None
    cancel_replace_blocked: bool | None = None
    position_mutation_block_contract_prepared: bool | None = None
    position_mutation_blocked: bool | None = None
    observability_contract_prepared: bool | None = None
    journal_contract_prepared: bool | None = None
    human_approval_contract_prepared: bool | None = None
    human_approval_required: bool | None = None
    stop_conditions_contract_prepared: bool | None = None
    paper_broker_read_only_connection_preparation_review_requested: bool | None = False
    offline_mode_enforced: bool | None = None
    sandbox_mode_enforced: bool | None = None
    preparation_only: bool | None = None
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
    external_api_requested: bool | None = False
    connection_safety_gate_score: int | None = None
    connection_contract_score: int | None = None
    broker_adapter_boundary_score: int | None = None
    configuration_schema_score: int | None = None
    credential_reference_contract_score: int | None = None
    no_secret_read_guard_score: int | None = None
    network_block_guard_score: int | None = None
    http_websocket_socket_block_guard_score: int | None = None
    account_read_only_contract_score: int | None = None
    market_data_read_only_contract_score: int | None = None
    order_blocking_contract_score: int | None = None
    position_mutation_block_score: int | None = None
    observability_contract_score: int | None = None
    journal_contract_score: int | None = None
    human_approval_contract_score: int | None = None
    stop_conditions_contract_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionPreparationResult:
    state: PaperBrokerReadOnlyConnectionPreparationState
    decision: PaperBrokerReadOnlyConnectionPreparationDecision
    preparation_score: int
    score_breakdown: PaperBrokerReadOnlyConnectionPreparationScore
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationRisk, ...] = ()
    recommendations: tuple[PaperBrokerReadOnlyConnectionPreparationRecommendation, ...] = ()
    read_only_connection_contract: ReadOnlyConnectionContract = field(default_factory=ReadOnlyConnectionContract)
    broker_adapter_boundary: BrokerAdapterBoundary = field(default_factory=BrokerAdapterBoundary)
    connection_configuration_schema: ConnectionConfigurationSchema = field(default_factory=ConnectionConfigurationSchema)
    credentials_reference_contract: CredentialsReferenceContract = field(default_factory=CredentialsReferenceContract)
    no_secret_read_guard: NoSecretReadGuard = field(default_factory=NoSecretReadGuard)
    network_execution_block_guard: NetworkExecutionBlockGuard = field(default_factory=NetworkExecutionBlockGuard)
    http_websocket_socket_block_guard: NetworkExecutionBlockGuard = field(
        default_factory=lambda: NetworkExecutionBlockGuard(name="http_websocket_socket_block_guard")
    )
    account_read_only_contract: AccountReadOnlyContract = field(default_factory=AccountReadOnlyContract)
    market_data_read_only_contract: MarketDataReadOnlyContract = field(default_factory=MarketDataReadOnlyContract)
    order_blocking_contract: OrderBlockingContract = field(default_factory=OrderBlockingContract)
    position_mutation_block_contract: PositionMutationBlockContract = field(default_factory=PositionMutationBlockContract)
    observability_contract: ConnectionObservabilityContract = field(default_factory=ConnectionObservabilityContract)
    journal_contract: ConnectionJournalContract = field(default_factory=ConnectionJournalContract)
    human_approval_contract: ConnectionHumanApprovalContract = field(default_factory=ConnectionHumanApprovalContract)
    stop_conditions_contract: ConnectionStopConditionContract = field(default_factory=ConnectionStopConditionContract)
    offline_only: bool = True
    summary: str = ""
