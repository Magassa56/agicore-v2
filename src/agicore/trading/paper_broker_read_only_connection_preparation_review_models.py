"""Models for the AGIcore Paper Broker Read-Only Connection Preparation Review layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerReadOnlyConnectionPreparationReviewState(StrEnum):
    NOT_READY = "NOT_READY"
    CONNECTION_PREPARATION_REVIEW_INPUT_INVALID = "CONNECTION_PREPARATION_REVIEW_INPUT_INVALID"
    CONNECTION_PREPARATION_REVIEW_BLOCKED = "CONNECTION_PREPARATION_REVIEW_BLOCKED"
    CONNECTION_PREPARATION_REVIEW_COMPLETED_WITH_WARNINGS = "CONNECTION_PREPARATION_REVIEW_COMPLETED_WITH_WARNINGS"
    CONNECTION_PREPARATION_REVIEW_COMPLETED = "CONNECTION_PREPARATION_REVIEW_COMPLETED"
    READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN = (
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN"
    )


class PaperBrokerReadOnlyConnectionPreparationReviewDecision(StrEnum):
    BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW = (
        "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW"
    )
    REQUIRE_CONNECTION_PREPARATION_FIXES = "REQUIRE_CONNECTION_PREPARATION_FIXES"
    REQUIRE_CONNECTION_CONTRACT_REVIEW_FIXES = "REQUIRE_CONNECTION_CONTRACT_REVIEW_FIXES"
    REQUIRE_BROKER_ADAPTER_BOUNDARY_REVIEW_FIXES = "REQUIRE_BROKER_ADAPTER_BOUNDARY_REVIEW_FIXES"
    REQUIRE_CONFIGURATION_SCHEMA_REVIEW_FIXES = "REQUIRE_CONFIGURATION_SCHEMA_REVIEW_FIXES"
    REQUIRE_CREDENTIAL_REFERENCE_REVIEW_FIXES = "REQUIRE_CREDENTIAL_REFERENCE_REVIEW_FIXES"
    REQUIRE_NO_SECRET_READ_GUARD_REVIEW_FIXES = "REQUIRE_NO_SECRET_READ_GUARD_REVIEW_FIXES"
    REQUIRE_NETWORK_BLOCK_GUARD_REVIEW_FIXES = "REQUIRE_NETWORK_BLOCK_GUARD_REVIEW_FIXES"
    REQUIRE_ACCOUNT_READ_ONLY_CONTRACT_REVIEW_FIXES = "REQUIRE_ACCOUNT_READ_ONLY_CONTRACT_REVIEW_FIXES"
    REQUIRE_MARKET_DATA_READ_ONLY_CONTRACT_REVIEW_FIXES = "REQUIRE_MARKET_DATA_READ_ONLY_CONTRACT_REVIEW_FIXES"
    REQUIRE_ORDER_BLOCKING_CONTRACT_REVIEW_FIXES = "REQUIRE_ORDER_BLOCKING_CONTRACT_REVIEW_FIXES"
    REQUIRE_POSITION_MUTATION_BLOCK_REVIEW_FIXES = "REQUIRE_POSITION_MUTATION_BLOCK_REVIEW_FIXES"
    REQUIRE_OBSERVABILITY_CONTRACT_REVIEW_FIXES = "REQUIRE_OBSERVABILITY_CONTRACT_REVIEW_FIXES"
    REQUIRE_JOURNAL_CONTRACT_REVIEW_FIXES = "REQUIRE_JOURNAL_CONTRACT_REVIEW_FIXES"
    REQUIRE_HUMAN_APPROVAL_CONTRACT_REVIEW_FIXES = "REQUIRE_HUMAN_APPROVAL_CONTRACT_REVIEW_FIXES"
    REQUIRE_STOP_CONDITION_CONTRACT_REVIEW_FIXES = "REQUIRE_STOP_CONDITION_CONTRACT_REVIEW_FIXES"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW = (
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW"
    )


class PaperBrokerReadOnlyConnectionPreparationReviewRisk(StrEnum):
    CONNECTION_PREPARATION_NOT_APPROVED = "CONNECTION_PREPARATION_NOT_APPROVED"
    READ_ONLY_CONNECTION_CONTRACT_REVIEW_FAILED = "READ_ONLY_CONNECTION_CONTRACT_REVIEW_FAILED"
    BROKER_ADAPTER_BOUNDARY_REVIEW_FAILED = "BROKER_ADAPTER_BOUNDARY_REVIEW_FAILED"
    CONNECTION_CONFIGURATION_SCHEMA_REVIEW_FAILED = "CONNECTION_CONFIGURATION_SCHEMA_REVIEW_FAILED"
    CREDENTIAL_REFERENCE_CONTRACT_REVIEW_FAILED = "CREDENTIAL_REFERENCE_CONTRACT_REVIEW_FAILED"
    SECRET_READ_GUARD_REVIEW_FAILED = "SECRET_READ_GUARD_REVIEW_FAILED"
    NETWORK_EXECUTION_BLOCK_GUARD_REVIEW_FAILED = "NETWORK_EXECUTION_BLOCK_GUARD_REVIEW_FAILED"
    HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW_FAILED = "HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW_FAILED"
    ACCOUNT_READ_ONLY_CONTRACT_REVIEW_FAILED = "ACCOUNT_READ_ONLY_CONTRACT_REVIEW_FAILED"
    MARKET_DATA_READ_ONLY_CONTRACT_REVIEW_FAILED = "MARKET_DATA_READ_ONLY_CONTRACT_REVIEW_FAILED"
    ORDER_BLOCKING_CONTRACT_REVIEW_FAILED = "ORDER_BLOCKING_CONTRACT_REVIEW_FAILED"
    POSITION_MUTATION_BLOCK_CONTRACT_REVIEW_FAILED = "POSITION_MUTATION_BLOCK_CONTRACT_REVIEW_FAILED"
    OBSERVABILITY_CONTRACT_REVIEW_FAILED = "OBSERVABILITY_CONTRACT_REVIEW_FAILED"
    JOURNAL_CONTRACT_REVIEW_FAILED = "JOURNAL_CONTRACT_REVIEW_FAILED"
    HUMAN_APPROVAL_CONTRACT_REVIEW_FAILED = "HUMAN_APPROVAL_CONTRACT_REVIEW_FAILED"
    STOP_CONDITION_CONTRACT_REVIEW_FAILED = "STOP_CONDITION_CONTRACT_REVIEW_FAILED"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN = (
        "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN"
    )


class PaperBrokerReadOnlyConnectionPreparationReviewRecommendation(StrEnum):
    HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN = "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN"
    APPROVE_CONNECTION_PREPARATION_FIRST = "APPROVE_CONNECTION_PREPARATION_FIRST"
    FIX_READ_ONLY_CONNECTION_CONTRACT = "FIX_READ_ONLY_CONNECTION_CONTRACT"
    FIX_BROKER_ADAPTER_BOUNDARY = "FIX_BROKER_ADAPTER_BOUNDARY"
    FIX_CONNECTION_CONFIGURATION_SCHEMA = "FIX_CONNECTION_CONFIGURATION_SCHEMA"
    FIX_CREDENTIAL_REFERENCE_CONTRACT = "FIX_CREDENTIAL_REFERENCE_CONTRACT"
    FIX_NO_SECRET_READ_GUARD = "FIX_NO_SECRET_READ_GUARD"
    FIX_NETWORK_EXECUTION_BLOCK_GUARD = "FIX_NETWORK_EXECUTION_BLOCK_GUARD"
    FIX_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD = "FIX_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD"
    FIX_ACCOUNT_READ_ONLY_CONTRACT = "FIX_ACCOUNT_READ_ONLY_CONTRACT"
    FIX_MARKET_DATA_READ_ONLY_CONTRACT = "FIX_MARKET_DATA_READ_ONLY_CONTRACT"
    FIX_ORDER_BLOCKING_CONTRACT = "FIX_ORDER_BLOCKING_CONTRACT"
    FIX_POSITION_MUTATION_BLOCK_CONTRACT = "FIX_POSITION_MUTATION_BLOCK_CONTRACT"
    FIX_OBSERVABILITY_CONTRACT = "FIX_OBSERVABILITY_CONTRACT"
    FIX_JOURNAL_CONTRACT = "FIX_JOURNAL_CONTRACT"
    FIX_HUMAN_APPROVAL_CONTRACT = "FIX_HUMAN_APPROVAL_CONTRACT"
    FIX_STOP_CONDITION_CONTRACT = "FIX_STOP_CONDITION_CONTRACT"
    RESTORE_OFFLINE_BOUNDARIES = "RESTORE_OFFLINE_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN = (
        "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN"
    )
    RUN_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW_SUITE = (
        "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW_SUITE"
    )
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN = (
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN"
    )


@dataclass(frozen=True)
class ConnectionContractReviewFinding:
    score: int = 0
    passed: bool = False
    reviewed: bool = False
    read_only_only: bool = False
    no_connection_execution: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class BrokerAdapterBoundaryReviewFinding:
    score: int = 0
    passed: bool = False
    reviewed: bool = False
    no_real_broker: bool = False
    no_alpaca_real: bool = False
    adapter_instantiation_blocked: bool = False
    network_transport_blocked: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConfigurationSchemaReviewFinding:
    score: int = 0
    passed: bool = False
    reviewed: bool = False
    schema_only: bool = False
    env_var_read_blocked: bool = False
    api_key_value_absent: bool = False
    network_fields_reference_only: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class CredentialsReferenceReviewFinding:
    score: int = 0
    passed: bool = False
    reviewed: bool = False
    reference_only: bool = False
    no_secret_values: bool = False
    no_api_key_read: bool = False
    no_env_var_read: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class NoSecretReadGuardReviewFinding:
    score: int = 0
    passed: bool = False
    reviewed: bool = False
    guard_enforced: bool = False
    no_api_key_read: bool = False
    no_env_var_read: bool = False
    no_hardcoded_secret: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class NetworkExecutionBlockGuardReviewFinding:
    score: int = 0
    passed: bool = False
    reviewed: bool = False
    network_execution_blocked: bool = False
    http_blocked: bool = False
    websocket_blocked: bool = False
    socket_blocked: bool = False
    external_api_blocked: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class AccountReadOnlyContractReviewFinding:
    score: int = 0
    passed: bool = False
    reviewed: bool = False
    active_account_access_blocked: bool = False
    account_mutations_blocked: bool = False
    read_only_schema_only: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class MarketDataReadOnlyContractReviewFinding:
    score: int = 0
    passed: bool = False
    reviewed: bool = False
    read_only_market_data_only: bool = False
    live_subscription_blocked: bool = False
    network_request_blocked: bool = False
    synthetic_or_schema_only: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class OrderBlockingContractReviewFinding:
    score: int = 0
    passed: bool = False
    reviewed: bool = False
    order_execution_blocked: bool = False
    real_order_blocked: bool = False
    cancel_replace_blocked: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class PositionMutationBlockContractReviewFinding:
    score: int = 0
    passed: bool = False
    reviewed: bool = False
    position_mutation_blocked: bool = False
    position_request_absent: bool = False
    close_modify_blocked: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ObservabilityContractReviewFinding:
    score: int = 0
    passed: bool = False
    reviewed: bool = False
    offline_events_defined: bool = False
    connection_attempt_logging_disabled: bool = False
    sensitive_values_redacted: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class JournalContractReviewFinding:
    score: int = 0
    passed: bool = False
    reviewed: bool = False
    offline_journal_required: bool = False
    sensitive_values_redacted: bool = False
    no_secret_material_logged: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class HumanApprovalContractReviewFinding:
    score: int = 0
    passed: bool = False
    reviewed: bool = False
    human_approval_required: bool = False
    approval_before_review: bool = False
    safety_gate_evidence_required: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class StopConditionContractReviewFinding:
    score: int = 0
    passed: bool = False
    reviewed: bool = False
    stop_on_secret_read: bool = False
    stop_on_network_request: bool = False
    stop_on_order_or_position_request: bool = False
    stop_on_account_access_request: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionPreparationReviewScore:
    overall_score: int
    connection_preparation_score: int
    connection_contract_score: int
    broker_adapter_boundary_score: int
    configuration_schema_score: int
    credential_reference_score: int
    no_secret_read_guard_score: int
    network_block_guard_score: int
    http_websocket_socket_block_guard_score: int
    account_read_only_score: int
    market_data_read_only_score: int
    order_blocking_score: int
    position_mutation_block_score: int
    observability_score: int
    journal_score: int
    human_approval_score: int
    stop_conditions_score: int


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionPreparationReviewInput:
    paper_broker_read_only_connection_preparation: Any = None
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
    connection_preparation_approved: bool | None = None
    connection_contract_review_verified: bool | None = None
    broker_adapter_boundary_review_verified: bool | None = None
    configuration_schema_review_verified: bool | None = None
    credential_reference_review_verified: bool | None = None
    no_secret_read_guard_review_verified: bool | None = None
    network_block_guard_review_verified: bool | None = None
    http_websocket_socket_block_guard_review_verified: bool | None = None
    account_read_only_contract_review_verified: bool | None = None
    market_data_read_only_contract_review_verified: bool | None = None
    order_blocking_contract_review_verified: bool | None = None
    position_mutation_block_review_verified: bool | None = None
    observability_contract_review_verified: bool | None = None
    journal_contract_review_verified: bool | None = None
    human_approval_contract_review_verified: bool | None = None
    stop_conditions_contract_review_verified: bool | None = None
    paper_broker_read_only_connection_dry_run_plan_requested: bool | None = False
    offline_mode_enforced: bool | None = None
    sandbox_mode_enforced: bool | None = None
    review_only: bool | None = None
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
    connection_preparation_score: int | None = None
    connection_contract_score: int | None = None
    broker_adapter_boundary_score: int | None = None
    configuration_schema_score: int | None = None
    credential_reference_score: int | None = None
    no_secret_read_guard_score: int | None = None
    network_block_guard_score: int | None = None
    http_websocket_socket_block_guard_score: int | None = None
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
class PaperBrokerReadOnlyConnectionPreparationReviewResult:
    state: PaperBrokerReadOnlyConnectionPreparationReviewState
    decision: PaperBrokerReadOnlyConnectionPreparationReviewDecision
    review_score: int
    score_breakdown: PaperBrokerReadOnlyConnectionPreparationReviewScore
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationReviewRisk, ...] = ()
    recommendations: tuple[PaperBrokerReadOnlyConnectionPreparationReviewRecommendation, ...] = ()
    connection_contract_review: ConnectionContractReviewFinding = field(default_factory=ConnectionContractReviewFinding)
    broker_adapter_boundary_review: BrokerAdapterBoundaryReviewFinding = field(
        default_factory=BrokerAdapterBoundaryReviewFinding
    )
    configuration_schema_review: ConfigurationSchemaReviewFinding = field(default_factory=ConfigurationSchemaReviewFinding)
    credentials_reference_review: CredentialsReferenceReviewFinding = field(
        default_factory=CredentialsReferenceReviewFinding
    )
    no_secret_read_guard_review: NoSecretReadGuardReviewFinding = field(default_factory=NoSecretReadGuardReviewFinding)
    network_execution_block_guard_review: NetworkExecutionBlockGuardReviewFinding = field(
        default_factory=NetworkExecutionBlockGuardReviewFinding
    )
    http_websocket_socket_block_guard_review: NetworkExecutionBlockGuardReviewFinding = field(
        default_factory=lambda: NetworkExecutionBlockGuardReviewFinding()
    )
    account_read_only_contract_review: AccountReadOnlyContractReviewFinding = field(
        default_factory=AccountReadOnlyContractReviewFinding
    )
    market_data_read_only_contract_review: MarketDataReadOnlyContractReviewFinding = field(
        default_factory=MarketDataReadOnlyContractReviewFinding
    )
    order_blocking_contract_review: OrderBlockingContractReviewFinding = field(
        default_factory=OrderBlockingContractReviewFinding
    )
    position_mutation_block_contract_review: PositionMutationBlockContractReviewFinding = field(
        default_factory=PositionMutationBlockContractReviewFinding
    )
    observability_contract_review: ObservabilityContractReviewFinding = field(
        default_factory=ObservabilityContractReviewFinding
    )
    journal_contract_review: JournalContractReviewFinding = field(default_factory=JournalContractReviewFinding)
    human_approval_contract_review: HumanApprovalContractReviewFinding = field(
        default_factory=HumanApprovalContractReviewFinding
    )
    stop_conditions_contract_review: StopConditionContractReviewFinding = field(
        default_factory=StopConditionContractReviewFinding
    )
    offline_only: bool = True
    summary: str = ""
