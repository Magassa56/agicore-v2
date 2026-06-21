"""Models for AGIcore Paper Broker Read-Only Connection Dry Run Preparation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerReadOnlyConnectionDryRunPreparationState(StrEnum):
    NOT_READY = "NOT_READY"
    DRY_RUN_PREPARATION_INPUT_INVALID = "DRY_RUN_PREPARATION_INPUT_INVALID"
    DRY_RUN_PREPARATION_BLOCKED = "DRY_RUN_PREPARATION_BLOCKED"
    DRY_RUN_PREPARATION_COMPLETED_WITH_WARNINGS = "DRY_RUN_PREPARATION_COMPLETED_WITH_WARNINGS"
    DRY_RUN_PREPARATION_COMPLETED = "DRY_RUN_PREPARATION_COMPLETED"
    READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION_REVIEW = (
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION_REVIEW"
    )


class PaperBrokerReadOnlyConnectionDryRunPreparationDecision(StrEnum):
    BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION = (
        "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION"
    )
    REQUIRE_DRY_RUN_SAFETY_GATE_FIXES = "REQUIRE_DRY_RUN_SAFETY_GATE_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_CONTRACT_FIXES = "REQUIRE_DRY_RUN_EXECUTION_CONTRACT_FIXES"
    REQUIRE_DRY_RUN_ADAPTER_BOUNDARY_FIXES = "REQUIRE_DRY_RUN_ADAPTER_BOUNDARY_FIXES"
    REQUIRE_DRY_RUN_CONFIGURATION_SCHEMA_FIXES = "REQUIRE_DRY_RUN_CONFIGURATION_SCHEMA_FIXES"
    REQUIRE_DRY_RUN_CREDENTIAL_REFERENCE_FIXES = "REQUIRE_DRY_RUN_CREDENTIAL_REFERENCE_FIXES"
    REQUIRE_DRY_RUN_NO_SECRET_READ_GUARD_FIXES = "REQUIRE_DRY_RUN_NO_SECRET_READ_GUARD_FIXES"
    REQUIRE_DRY_RUN_NETWORK_BLOCK_GUARD_FIXES = "REQUIRE_DRY_RUN_NETWORK_BLOCK_GUARD_FIXES"
    REQUIRE_DRY_RUN_ACCOUNT_READ_ONLY_FIXES = "REQUIRE_DRY_RUN_ACCOUNT_READ_ONLY_FIXES"
    REQUIRE_DRY_RUN_MARKET_DATA_READ_ONLY_FIXES = "REQUIRE_DRY_RUN_MARKET_DATA_READ_ONLY_FIXES"
    REQUIRE_DRY_RUN_ORDER_BLOCKING_FIXES = "REQUIRE_DRY_RUN_ORDER_BLOCKING_FIXES"
    REQUIRE_DRY_RUN_POSITION_MUTATION_BLOCK_FIXES = "REQUIRE_DRY_RUN_POSITION_MUTATION_BLOCK_FIXES"
    REQUIRE_DRY_RUN_OBSERVABILITY_FIXES = "REQUIRE_DRY_RUN_OBSERVABILITY_FIXES"
    REQUIRE_DRY_RUN_JOURNAL_FIXES = "REQUIRE_DRY_RUN_JOURNAL_FIXES"
    REQUIRE_DRY_RUN_HUMAN_APPROVAL_FIXES = "REQUIRE_DRY_RUN_HUMAN_APPROVAL_FIXES"
    REQUIRE_DRY_RUN_STOP_CONDITION_FIXES = "REQUIRE_DRY_RUN_STOP_CONDITION_FIXES"
    REQUIRE_DRY_RUN_SUCCESS_FAILURE_FIXES = "REQUIRE_DRY_RUN_SUCCESS_FAILURE_FIXES"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION = (
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION"
    )


class PaperBrokerReadOnlyConnectionDryRunPreparationRisk(StrEnum):
    DRY_RUN_SAFETY_GATE_NOT_APPROVED = "DRY_RUN_SAFETY_GATE_NOT_APPROVED"
    DRY_RUN_EXECUTION_CONTRACT_MISSING = "DRY_RUN_EXECUTION_CONTRACT_MISSING"
    DRY_RUN_ADAPTER_BOUNDARY_UNSAFE = "DRY_RUN_ADAPTER_BOUNDARY_UNSAFE"
    DRY_RUN_CONFIGURATION_SCHEMA_UNSAFE = "DRY_RUN_CONFIGURATION_SCHEMA_UNSAFE"
    DRY_RUN_CREDENTIAL_REFERENCE_UNSAFE = "DRY_RUN_CREDENTIAL_REFERENCE_UNSAFE"
    DRY_RUN_SECRET_READ_GUARD_MISSING = "DRY_RUN_SECRET_READ_GUARD_MISSING"
    DRY_RUN_NETWORK_BLOCK_GUARD_MISSING = "DRY_RUN_NETWORK_BLOCK_GUARD_MISSING"
    DRY_RUN_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_MISSING = "DRY_RUN_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_MISSING"
    DRY_RUN_ACCOUNT_READ_ONLY_UNSAFE = "DRY_RUN_ACCOUNT_READ_ONLY_UNSAFE"
    DRY_RUN_MARKET_DATA_READ_ONLY_UNSAFE = "DRY_RUN_MARKET_DATA_READ_ONLY_UNSAFE"
    DRY_RUN_ORDER_BLOCKING_UNSAFE = "DRY_RUN_ORDER_BLOCKING_UNSAFE"
    DRY_RUN_POSITION_MUTATION_BLOCK_UNSAFE = "DRY_RUN_POSITION_MUTATION_BLOCK_UNSAFE"
    DRY_RUN_OBSERVABILITY_INCOMPLETE = "DRY_RUN_OBSERVABILITY_INCOMPLETE"
    DRY_RUN_JOURNAL_INCOMPLETE = "DRY_RUN_JOURNAL_INCOMPLETE"
    DRY_RUN_HUMAN_APPROVAL_MISSING = "DRY_RUN_HUMAN_APPROVAL_MISSING"
    DRY_RUN_STOP_CONDITIONS_MISSING = "DRY_RUN_STOP_CONDITIONS_MISSING"
    DRY_RUN_SUCCESS_FAILURE_CONTRACT_MISSING = "DRY_RUN_SUCCESS_FAILURE_CONTRACT_MISSING"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION_REVIEW = (
        "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION_REVIEW"
    )


class PaperBrokerReadOnlyConnectionDryRunPreparationRecommendation(StrEnum):
    HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION_REVIEW = (
        "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION_REVIEW"
    )
    APPROVE_DRY_RUN_SAFETY_GATE_FIRST = "APPROVE_DRY_RUN_SAFETY_GATE_FIRST"
    PREPARE_DRY_RUN_EXECUTION_CONTRACT = "PREPARE_DRY_RUN_EXECUTION_CONTRACT"
    HARDEN_DRY_RUN_ADAPTER_BOUNDARY = "HARDEN_DRY_RUN_ADAPTER_BOUNDARY"
    HARDEN_DRY_RUN_CONFIGURATION_SCHEMA = "HARDEN_DRY_RUN_CONFIGURATION_SCHEMA"
    HARDEN_DRY_RUN_CREDENTIAL_REFERENCE = "HARDEN_DRY_RUN_CREDENTIAL_REFERENCE"
    INSTALL_DRY_RUN_NO_SECRET_READ_GUARD = "INSTALL_DRY_RUN_NO_SECRET_READ_GUARD"
    INSTALL_DRY_RUN_NETWORK_BLOCK_GUARD = "INSTALL_DRY_RUN_NETWORK_BLOCK_GUARD"
    INSTALL_DRY_RUN_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD = "INSTALL_DRY_RUN_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD"
    HARDEN_DRY_RUN_ACCOUNT_READ_ONLY = "HARDEN_DRY_RUN_ACCOUNT_READ_ONLY"
    HARDEN_DRY_RUN_MARKET_DATA_READ_ONLY = "HARDEN_DRY_RUN_MARKET_DATA_READ_ONLY"
    HARDEN_DRY_RUN_ORDER_BLOCKING = "HARDEN_DRY_RUN_ORDER_BLOCKING"
    HARDEN_DRY_RUN_POSITION_MUTATION_BLOCK = "HARDEN_DRY_RUN_POSITION_MUTATION_BLOCK"
    COMPLETE_DRY_RUN_OBSERVABILITY = "COMPLETE_DRY_RUN_OBSERVABILITY"
    COMPLETE_DRY_RUN_JOURNAL = "COMPLETE_DRY_RUN_JOURNAL"
    REQUIRE_DRY_RUN_HUMAN_APPROVAL = "REQUIRE_DRY_RUN_HUMAN_APPROVAL"
    DEFINE_DRY_RUN_STOP_CONDITIONS = "DEFINE_DRY_RUN_STOP_CONDITIONS"
    PREPARE_DRY_RUN_SUCCESS_FAILURE_CONTRACT = "PREPARE_DRY_RUN_SUCCESS_FAILURE_CONTRACT"
    RESTORE_OFFLINE_BOUNDARIES = "RESTORE_OFFLINE_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION_REVIEW = (
        "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION_REVIEW"
    )
    RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION_SUITE = (
        "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION_SUITE"
    )
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION_REVIEW = (
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION_REVIEW"
    )


@dataclass(frozen=True)
class DryRunExecutionContract:
    name: str = "dry_run_execution_contract"
    score: int = 0
    defined: bool = False
    preparation_only: bool = True
    read_only_only: bool = True
    dry_run_execution_disabled: bool = True
    allowed_actions: tuple[str, ...] = ()
    prohibited_actions: tuple[str, ...] = ()
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunAdapterBoundary:
    name: str = "dry_run_adapter_boundary"
    score: int = 0
    defined: bool = False
    no_real_broker: bool = True
    no_alpaca_real: bool = True
    adapter_instantiation_blocked: bool = True
    network_transport_blocked: bool = True
    paper_only_future_reference: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunConfigurationSchema:
    name: str = "dry_run_configuration_schema"
    score: int = 0
    defined: bool = False
    schema_only: bool = True
    env_var_read_blocked: bool = True
    api_key_value_absent: bool = True
    network_fields_reference_only: bool = True
    required_fields: tuple[str, ...] = ()
    prohibited_fields: tuple[str, ...] = ()
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunCredentialsReferenceContract:
    name: str = "dry_run_credentials_reference_contract"
    score: int = 0
    defined: bool = False
    reference_only: bool = True
    no_secret_values: bool = True
    no_api_key_read: bool = True
    no_env_var_read: bool = True
    secret_source: str = "none_in_this_phase"
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunNoSecretReadGuard:
    name: str = "dry_run_no_secret_read_guard"
    score: int = 0
    defined: bool = False
    guard_enforced: bool = False
    no_api_key_read: bool = True
    no_env_var_read: bool = True
    no_hardcoded_secret: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunNetworkBlockGuard:
    name: str = "dry_run_network_block_guard"
    score: int = 0
    defined: bool = False
    network_execution_blocked: bool = True
    http_blocked: bool = True
    websocket_blocked: bool = True
    socket_blocked: bool = True
    external_api_blocked: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunAccountReadOnlyContract:
    name: str = "dry_run_account_read_only_contract"
    score: int = 0
    defined: bool = False
    active_account_access_blocked: bool = True
    account_mutations_blocked: bool = True
    schema_only_account_review: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunMarketDataReadOnlyContract:
    name: str = "dry_run_market_data_read_only_contract"
    score: int = 0
    defined: bool = False
    read_only_market_data_only: bool = True
    live_subscription_blocked: bool = True
    network_request_blocked: bool = True
    schema_or_synthetic_only: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunOrderBlockingContract:
    name: str = "dry_run_order_blocking_contract"
    score: int = 0
    defined: bool = False
    order_execution_blocked: bool = True
    real_order_blocked: bool = True
    cancel_replace_blocked: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunPositionMutationBlockContract:
    name: str = "dry_run_position_mutation_block_contract"
    score: int = 0
    defined: bool = False
    position_mutation_blocked: bool = True
    position_request_absent: bool = True
    close_modify_blocked: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunObservabilityContract:
    name: str = "dry_run_observability_contract"
    score: int = 0
    defined: bool = False
    offline_events_defined: bool = True
    connection_attempt_logging_disabled: bool = True
    sensitive_values_redacted: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunJournalContract:
    name: str = "dry_run_journal_contract"
    score: int = 0
    defined: bool = False
    offline_journal_required: bool = True
    sensitive_values_redacted: bool = True
    no_secret_material_logged: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunHumanApprovalContract:
    name: str = "dry_run_human_approval_contract"
    score: int = 0
    defined: bool = False
    human_approval_required: bool = True
    approval_before_review: bool = True
    safety_gate_evidence_required: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunStopConditionContract:
    name: str = "dry_run_stop_conditions_contract"
    score: int = 0
    defined: bool = False
    stop_on_secret_read: bool = True
    stop_on_network_request: bool = True
    stop_on_order_or_position_request: bool = True
    stop_on_account_access_request: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunSuccessFailureContract:
    name: str = "dry_run_success_failure_contract"
    score: int = 0
    defined: bool = False
    success_requires_no_real_connection: bool = True
    success_requires_all_guards_verified: bool = True
    failure_on_secret_network_order_position_or_account: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunPreparationScore:
    overall_score: int
    dry_run_safety_gate_score: int
    execution_contract_score: int
    adapter_boundary_score: int
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
    success_failure_score: int


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunPreparationInput:
    paper_broker_read_only_connection_dry_run_safety_gate: Any = None
    paper_broker_read_only_connection_dry_run_plan: Any = None
    paper_broker_read_only_connection_preparation_review: Any = None
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
    dry_run_safety_gate_approved: bool | None = None
    dry_run_execution_contract_prepared: bool | None = None
    dry_run_adapter_boundary_prepared: bool | None = None
    dry_run_configuration_schema_prepared: bool | None = None
    dry_run_credentials_reference_contract_prepared: bool | None = None
    dry_run_credentials_reference_only: bool | None = None
    dry_run_no_secret_read_guard_prepared: bool | None = None
    dry_run_secret_read_guard_enforced: bool | None = None
    dry_run_network_block_guard_prepared: bool | None = None
    dry_run_network_blocked: bool | None = None
    dry_run_http_websocket_socket_block_guard_prepared: bool | None = None
    dry_run_http_transport_blocked: bool | None = None
    dry_run_websocket_transport_blocked: bool | None = None
    dry_run_socket_transport_blocked: bool | None = None
    dry_run_external_api_blocked: bool | None = None
    dry_run_account_read_only_contract_prepared: bool | None = None
    dry_run_account_active_access_blocked: bool | None = None
    dry_run_account_mutations_blocked: bool | None = None
    dry_run_market_data_read_only_contract_prepared: bool | None = None
    dry_run_market_data_live_subscription_blocked: bool | None = None
    dry_run_market_data_network_request_blocked: bool | None = None
    dry_run_order_blocking_contract_prepared: bool | None = None
    dry_run_order_execution_blocked: bool | None = None
    dry_run_cancel_replace_blocked: bool | None = None
    dry_run_position_mutation_block_contract_prepared: bool | None = None
    dry_run_position_mutation_blocked: bool | None = None
    dry_run_observability_contract_prepared: bool | None = None
    dry_run_journal_contract_prepared: bool | None = None
    dry_run_human_approval_contract_prepared: bool | None = None
    dry_run_human_approval_required: bool | None = None
    dry_run_stop_conditions_contract_prepared: bool | None = None
    dry_run_success_failure_contract_prepared: bool | None = None
    paper_broker_read_only_connection_dry_run_preparation_review_requested: bool | None = False
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
    dry_run_requested: bool | None = False
    dry_run_executed: bool | None = False
    dry_run_safety_gate_score: int | None = None
    execution_contract_score: int | None = None
    adapter_boundary_score: int | None = None
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
    success_failure_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunPreparationResult:
    state: PaperBrokerReadOnlyConnectionDryRunPreparationState
    decision: PaperBrokerReadOnlyConnectionDryRunPreparationDecision
    preparation_score: int
    score_breakdown: PaperBrokerReadOnlyConnectionDryRunPreparationScore
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationRisk, ...] = ()
    recommendations: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationRecommendation, ...] = ()
    dry_run_execution_contract: DryRunExecutionContract = field(default_factory=DryRunExecutionContract)
    dry_run_adapter_boundary: DryRunAdapterBoundary = field(default_factory=DryRunAdapterBoundary)
    dry_run_configuration_schema: DryRunConfigurationSchema = field(default_factory=DryRunConfigurationSchema)
    dry_run_credentials_reference_contract: DryRunCredentialsReferenceContract = field(
        default_factory=DryRunCredentialsReferenceContract
    )
    dry_run_no_secret_read_guard: DryRunNoSecretReadGuard = field(default_factory=DryRunNoSecretReadGuard)
    dry_run_network_block_guard: DryRunNetworkBlockGuard = field(default_factory=DryRunNetworkBlockGuard)
    dry_run_http_websocket_socket_block_guard: DryRunNetworkBlockGuard = field(
        default_factory=lambda: DryRunNetworkBlockGuard(name="dry_run_http_websocket_socket_block_guard")
    )
    dry_run_account_read_only_contract: DryRunAccountReadOnlyContract = field(default_factory=DryRunAccountReadOnlyContract)
    dry_run_market_data_read_only_contract: DryRunMarketDataReadOnlyContract = field(
        default_factory=DryRunMarketDataReadOnlyContract
    )
    dry_run_order_blocking_contract: DryRunOrderBlockingContract = field(default_factory=DryRunOrderBlockingContract)
    dry_run_position_mutation_block_contract: DryRunPositionMutationBlockContract = field(
        default_factory=DryRunPositionMutationBlockContract
    )
    dry_run_observability_contract: DryRunObservabilityContract = field(default_factory=DryRunObservabilityContract)
    dry_run_journal_contract: DryRunJournalContract = field(default_factory=DryRunJournalContract)
    dry_run_human_approval_contract: DryRunHumanApprovalContract = field(default_factory=DryRunHumanApprovalContract)
    dry_run_stop_conditions_contract: DryRunStopConditionContract = field(default_factory=DryRunStopConditionContract)
    dry_run_success_failure_contract: DryRunSuccessFailureContract = field(default_factory=DryRunSuccessFailureContract)
    offline_only: bool = True
    summary: str = ""
