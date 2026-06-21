"""Models for AGIcore Paper Broker Read-Only Connection Dry Run Preparation Review."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerReadOnlyConnectionDryRunPreparationReviewState(StrEnum):
    NOT_READY = "NOT_READY"
    DRY_RUN_PREPARATION_REVIEW_INPUT_INVALID = "DRY_RUN_PREPARATION_REVIEW_INPUT_INVALID"
    DRY_RUN_PREPARATION_REVIEW_BLOCKED = "DRY_RUN_PREPARATION_REVIEW_BLOCKED"
    DRY_RUN_PREPARATION_REVIEW_COMPLETED_WITH_WARNINGS = "DRY_RUN_PREPARATION_REVIEW_COMPLETED_WITH_WARNINGS"
    DRY_RUN_PREPARATION_REVIEW_COMPLETED = "DRY_RUN_PREPARATION_REVIEW_COMPLETED"
    READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN = (
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN"
    )


class PaperBrokerReadOnlyConnectionDryRunPreparationReviewDecision(StrEnum):
    BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION_REVIEW = (
        "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION_REVIEW"
    )
    REQUIRE_DRY_RUN_PREPARATION_FIXES = "REQUIRE_DRY_RUN_PREPARATION_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_CONTRACT_REVIEW_FIXES = "REQUIRE_DRY_RUN_EXECUTION_CONTRACT_REVIEW_FIXES"
    REQUIRE_DRY_RUN_ADAPTER_BOUNDARY_REVIEW_FIXES = "REQUIRE_DRY_RUN_ADAPTER_BOUNDARY_REVIEW_FIXES"
    REQUIRE_DRY_RUN_CONFIGURATION_SCHEMA_REVIEW_FIXES = "REQUIRE_DRY_RUN_CONFIGURATION_SCHEMA_REVIEW_FIXES"
    REQUIRE_DRY_RUN_CREDENTIAL_REFERENCE_REVIEW_FIXES = "REQUIRE_DRY_RUN_CREDENTIAL_REFERENCE_REVIEW_FIXES"
    REQUIRE_DRY_RUN_NO_SECRET_READ_GUARD_REVIEW_FIXES = "REQUIRE_DRY_RUN_NO_SECRET_READ_GUARD_REVIEW_FIXES"
    REQUIRE_DRY_RUN_NETWORK_BLOCK_GUARD_REVIEW_FIXES = "REQUIRE_DRY_RUN_NETWORK_BLOCK_GUARD_REVIEW_FIXES"
    REQUIRE_DRY_RUN_ACCOUNT_READ_ONLY_REVIEW_FIXES = "REQUIRE_DRY_RUN_ACCOUNT_READ_ONLY_REVIEW_FIXES"
    REQUIRE_DRY_RUN_MARKET_DATA_READ_ONLY_REVIEW_FIXES = "REQUIRE_DRY_RUN_MARKET_DATA_READ_ONLY_REVIEW_FIXES"
    REQUIRE_DRY_RUN_ORDER_BLOCKING_REVIEW_FIXES = "REQUIRE_DRY_RUN_ORDER_BLOCKING_REVIEW_FIXES"
    REQUIRE_DRY_RUN_POSITION_MUTATION_BLOCK_REVIEW_FIXES = "REQUIRE_DRY_RUN_POSITION_MUTATION_BLOCK_REVIEW_FIXES"
    REQUIRE_DRY_RUN_OBSERVABILITY_REVIEW_FIXES = "REQUIRE_DRY_RUN_OBSERVABILITY_REVIEW_FIXES"
    REQUIRE_DRY_RUN_JOURNAL_REVIEW_FIXES = "REQUIRE_DRY_RUN_JOURNAL_REVIEW_FIXES"
    REQUIRE_DRY_RUN_HUMAN_APPROVAL_REVIEW_FIXES = "REQUIRE_DRY_RUN_HUMAN_APPROVAL_REVIEW_FIXES"
    REQUIRE_DRY_RUN_STOP_CONDITION_REVIEW_FIXES = "REQUIRE_DRY_RUN_STOP_CONDITION_REVIEW_FIXES"
    REQUIRE_DRY_RUN_SUCCESS_FAILURE_REVIEW_FIXES = "REQUIRE_DRY_RUN_SUCCESS_FAILURE_REVIEW_FIXES"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION_REVIEW = (
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION_REVIEW"
    )


class PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk(StrEnum):
    DRY_RUN_PREPARATION_NOT_APPROVED = "DRY_RUN_PREPARATION_NOT_APPROVED"
    DRY_RUN_EXECUTION_CONTRACT_REVIEW_FAILED = "DRY_RUN_EXECUTION_CONTRACT_REVIEW_FAILED"
    DRY_RUN_ADAPTER_BOUNDARY_REVIEW_FAILED = "DRY_RUN_ADAPTER_BOUNDARY_REVIEW_FAILED"
    DRY_RUN_CONFIGURATION_SCHEMA_REVIEW_FAILED = "DRY_RUN_CONFIGURATION_SCHEMA_REVIEW_FAILED"
    DRY_RUN_CREDENTIAL_REFERENCE_REVIEW_FAILED = "DRY_RUN_CREDENTIAL_REFERENCE_REVIEW_FAILED"
    DRY_RUN_SECRET_READ_GUARD_REVIEW_FAILED = "DRY_RUN_SECRET_READ_GUARD_REVIEW_FAILED"
    DRY_RUN_NETWORK_BLOCK_GUARD_REVIEW_FAILED = "DRY_RUN_NETWORK_BLOCK_GUARD_REVIEW_FAILED"
    DRY_RUN_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW_FAILED = "DRY_RUN_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW_FAILED"
    DRY_RUN_ACCOUNT_READ_ONLY_REVIEW_FAILED = "DRY_RUN_ACCOUNT_READ_ONLY_REVIEW_FAILED"
    DRY_RUN_MARKET_DATA_READ_ONLY_REVIEW_FAILED = "DRY_RUN_MARKET_DATA_READ_ONLY_REVIEW_FAILED"
    DRY_RUN_ORDER_BLOCKING_REVIEW_FAILED = "DRY_RUN_ORDER_BLOCKING_REVIEW_FAILED"
    DRY_RUN_POSITION_MUTATION_BLOCK_REVIEW_FAILED = "DRY_RUN_POSITION_MUTATION_BLOCK_REVIEW_FAILED"
    DRY_RUN_OBSERVABILITY_REVIEW_FAILED = "DRY_RUN_OBSERVABILITY_REVIEW_FAILED"
    DRY_RUN_JOURNAL_REVIEW_FAILED = "DRY_RUN_JOURNAL_REVIEW_FAILED"
    DRY_RUN_HUMAN_APPROVAL_REVIEW_FAILED = "DRY_RUN_HUMAN_APPROVAL_REVIEW_FAILED"
    DRY_RUN_STOP_CONDITIONS_REVIEW_FAILED = "DRY_RUN_STOP_CONDITIONS_REVIEW_FAILED"
    DRY_RUN_SUCCESS_FAILURE_REVIEW_FAILED = "DRY_RUN_SUCCESS_FAILURE_REVIEW_FAILED"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN = (
        "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN"
    )


class PaperBrokerReadOnlyConnectionDryRunPreparationReviewRecommendation(StrEnum):
    HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN = (
        "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN"
    )
    APPROVE_DRY_RUN_PREPARATION_FIRST = "APPROVE_DRY_RUN_PREPARATION_FIRST"
    FIX_DRY_RUN_EXECUTION_CONTRACT_REVIEW = "FIX_DRY_RUN_EXECUTION_CONTRACT_REVIEW"
    FIX_DRY_RUN_ADAPTER_BOUNDARY_REVIEW = "FIX_DRY_RUN_ADAPTER_BOUNDARY_REVIEW"
    FIX_DRY_RUN_CONFIGURATION_SCHEMA_REVIEW = "FIX_DRY_RUN_CONFIGURATION_SCHEMA_REVIEW"
    FIX_DRY_RUN_CREDENTIAL_REFERENCE_REVIEW = "FIX_DRY_RUN_CREDENTIAL_REFERENCE_REVIEW"
    FIX_DRY_RUN_NO_SECRET_READ_GUARD_REVIEW = "FIX_DRY_RUN_NO_SECRET_READ_GUARD_REVIEW"
    FIX_DRY_RUN_NETWORK_BLOCK_GUARD_REVIEW = "FIX_DRY_RUN_NETWORK_BLOCK_GUARD_REVIEW"
    FIX_DRY_RUN_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW = "FIX_DRY_RUN_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW"
    FIX_DRY_RUN_ACCOUNT_READ_ONLY_REVIEW = "FIX_DRY_RUN_ACCOUNT_READ_ONLY_REVIEW"
    FIX_DRY_RUN_MARKET_DATA_READ_ONLY_REVIEW = "FIX_DRY_RUN_MARKET_DATA_READ_ONLY_REVIEW"
    FIX_DRY_RUN_ORDER_BLOCKING_REVIEW = "FIX_DRY_RUN_ORDER_BLOCKING_REVIEW"
    FIX_DRY_RUN_POSITION_MUTATION_BLOCK_REVIEW = "FIX_DRY_RUN_POSITION_MUTATION_BLOCK_REVIEW"
    FIX_DRY_RUN_OBSERVABILITY_REVIEW = "FIX_DRY_RUN_OBSERVABILITY_REVIEW"
    FIX_DRY_RUN_JOURNAL_REVIEW = "FIX_DRY_RUN_JOURNAL_REVIEW"
    FIX_DRY_RUN_HUMAN_APPROVAL_REVIEW = "FIX_DRY_RUN_HUMAN_APPROVAL_REVIEW"
    FIX_DRY_RUN_STOP_CONDITION_REVIEW = "FIX_DRY_RUN_STOP_CONDITION_REVIEW"
    FIX_DRY_RUN_SUCCESS_FAILURE_REVIEW = "FIX_DRY_RUN_SUCCESS_FAILURE_REVIEW"
    RESTORE_OFFLINE_BOUNDARIES = "RESTORE_OFFLINE_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN = (
        "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN"
    )
    RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION_REVIEW_SUITE = (
        "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION_REVIEW_SUITE"
    )
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN = (
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN"
    )


@dataclass(frozen=True)
class DryRunExecutionContractReviewFinding:
    score: int = 0
    passed: bool = False
    reviewed: bool = False
    preparation_only: bool = False
    read_only_only: bool = False
    dry_run_execution_disabled: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunAdapterBoundaryReviewFinding:
    score: int = 0
    passed: bool = False
    reviewed: bool = False
    no_real_broker: bool = False
    no_alpaca_real: bool = False
    adapter_instantiation_blocked: bool = False
    network_transport_blocked: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunConfigurationSchemaReviewFinding:
    score: int = 0
    passed: bool = False
    reviewed: bool = False
    schema_only: bool = False
    env_var_read_blocked: bool = False
    api_key_value_absent: bool = False
    network_fields_reference_only: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunCredentialsReferenceReviewFinding:
    score: int = 0
    passed: bool = False
    reviewed: bool = False
    reference_only: bool = False
    no_secret_values: bool = False
    no_api_key_read: bool = False
    no_env_var_read: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunNoSecretReadGuardReviewFinding:
    score: int = 0
    passed: bool = False
    reviewed: bool = False
    guard_enforced: bool = False
    no_api_key_read: bool = False
    no_env_var_read: bool = False
    no_hardcoded_secret: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunNetworkBlockGuardReviewFinding:
    score: int = 0
    passed: bool = False
    reviewed: bool = False
    network_execution_blocked: bool = False
    http_blocked: bool = False
    websocket_blocked: bool = False
    socket_blocked: bool = False
    external_api_blocked: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunAccountReadOnlyContractReviewFinding:
    score: int = 0
    passed: bool = False
    reviewed: bool = False
    active_account_access_blocked: bool = False
    account_mutations_blocked: bool = False
    schema_only_account_review: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunMarketDataReadOnlyContractReviewFinding:
    score: int = 0
    passed: bool = False
    reviewed: bool = False
    read_only_market_data_only: bool = False
    live_subscription_blocked: bool = False
    network_request_blocked: bool = False
    schema_or_synthetic_only: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunOrderBlockingContractReviewFinding:
    score: int = 0
    passed: bool = False
    reviewed: bool = False
    order_execution_blocked: bool = False
    real_order_blocked: bool = False
    cancel_replace_blocked: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunPositionMutationBlockReviewFinding:
    score: int = 0
    passed: bool = False
    reviewed: bool = False
    position_mutation_blocked: bool = False
    position_request_absent: bool = False
    close_modify_blocked: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunObservabilityContractReviewFinding:
    score: int = 0
    passed: bool = False
    reviewed: bool = False
    offline_events_defined: bool = False
    connection_attempt_logging_disabled: bool = False
    sensitive_values_redacted: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunJournalContractReviewFinding:
    score: int = 0
    passed: bool = False
    reviewed: bool = False
    offline_journal_required: bool = False
    sensitive_values_redacted: bool = False
    no_secret_material_logged: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunHumanApprovalContractReviewFinding:
    score: int = 0
    passed: bool = False
    reviewed: bool = False
    human_approval_required: bool = False
    approval_before_review: bool = False
    safety_gate_evidence_required: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunStopConditionContractReviewFinding:
    score: int = 0
    passed: bool = False
    reviewed: bool = False
    stop_on_secret_read: bool = False
    stop_on_network_request: bool = False
    stop_on_order_or_position_request: bool = False
    stop_on_account_access_request: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunSuccessFailureContractReviewFinding:
    score: int = 0
    passed: bool = False
    reviewed: bool = False
    success_requires_no_real_connection: bool = False
    success_requires_all_guards_verified: bool = False
    failure_on_secret_network_order_position_or_account: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunPreparationReviewScore:
    overall_score: int
    dry_run_preparation_score: int
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
class PaperBrokerReadOnlyConnectionDryRunPreparationReviewInput:
    paper_broker_read_only_connection_dry_run_preparation: Any = None
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
    dry_run_preparation_approved: bool | None = None
    dry_run_execution_contract_review_verified: bool | None = None
    dry_run_adapter_boundary_review_verified: bool | None = None
    dry_run_configuration_schema_review_verified: bool | None = None
    dry_run_credential_reference_review_verified: bool | None = None
    dry_run_no_secret_read_guard_review_verified: bool | None = None
    dry_run_network_block_guard_review_verified: bool | None = None
    dry_run_http_websocket_socket_block_guard_review_verified: bool | None = None
    dry_run_account_read_only_review_verified: bool | None = None
    dry_run_market_data_read_only_review_verified: bool | None = None
    dry_run_order_blocking_review_verified: bool | None = None
    dry_run_position_mutation_block_review_verified: bool | None = None
    dry_run_observability_review_verified: bool | None = None
    dry_run_journal_review_verified: bool | None = None
    dry_run_human_approval_review_verified: bool | None = None
    dry_run_stop_conditions_review_verified: bool | None = None
    dry_run_success_failure_review_verified: bool | None = None
    paper_broker_read_only_connection_dry_run_execution_plan_requested: bool | None = False
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
    dry_run_requested: bool | None = False
    dry_run_executed: bool | None = False
    dry_run_preparation_score: int | None = None
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
class PaperBrokerReadOnlyConnectionDryRunPreparationReviewResult:
    state: PaperBrokerReadOnlyConnectionDryRunPreparationReviewState
    decision: PaperBrokerReadOnlyConnectionDryRunPreparationReviewDecision
    review_score: int
    score_breakdown: PaperBrokerReadOnlyConnectionDryRunPreparationReviewScore
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk, ...] = ()
    recommendations: tuple[PaperBrokerReadOnlyConnectionDryRunPreparationReviewRecommendation, ...] = ()
    dry_run_execution_contract_review: DryRunExecutionContractReviewFinding = field(default_factory=DryRunExecutionContractReviewFinding)
    dry_run_adapter_boundary_review: DryRunAdapterBoundaryReviewFinding = field(default_factory=DryRunAdapterBoundaryReviewFinding)
    dry_run_configuration_schema_review: DryRunConfigurationSchemaReviewFinding = field(default_factory=DryRunConfigurationSchemaReviewFinding)
    dry_run_credentials_reference_review: DryRunCredentialsReferenceReviewFinding = field(default_factory=DryRunCredentialsReferenceReviewFinding)
    dry_run_no_secret_read_guard_review: DryRunNoSecretReadGuardReviewFinding = field(default_factory=DryRunNoSecretReadGuardReviewFinding)
    dry_run_network_block_guard_review: DryRunNetworkBlockGuardReviewFinding = field(default_factory=DryRunNetworkBlockGuardReviewFinding)
    dry_run_http_websocket_socket_block_guard_review: DryRunNetworkBlockGuardReviewFinding = field(default_factory=DryRunNetworkBlockGuardReviewFinding)
    dry_run_account_read_only_contract_review: DryRunAccountReadOnlyContractReviewFinding = field(default_factory=DryRunAccountReadOnlyContractReviewFinding)
    dry_run_market_data_read_only_contract_review: DryRunMarketDataReadOnlyContractReviewFinding = field(default_factory=DryRunMarketDataReadOnlyContractReviewFinding)
    dry_run_order_blocking_contract_review: DryRunOrderBlockingContractReviewFinding = field(default_factory=DryRunOrderBlockingContractReviewFinding)
    dry_run_position_mutation_block_contract_review: DryRunPositionMutationBlockReviewFinding = field(default_factory=DryRunPositionMutationBlockReviewFinding)
    dry_run_observability_contract_review: DryRunObservabilityContractReviewFinding = field(default_factory=DryRunObservabilityContractReviewFinding)
    dry_run_journal_contract_review: DryRunJournalContractReviewFinding = field(default_factory=DryRunJournalContractReviewFinding)
    dry_run_human_approval_contract_review: DryRunHumanApprovalContractReviewFinding = field(default_factory=DryRunHumanApprovalContractReviewFinding)
    dry_run_stop_conditions_contract_review: DryRunStopConditionContractReviewFinding = field(default_factory=DryRunStopConditionContractReviewFinding)
    dry_run_success_failure_contract_review: DryRunSuccessFailureContractReviewFinding = field(default_factory=DryRunSuccessFailureContractReviewFinding)
    offline_only: bool = True
    summary: str = ""
