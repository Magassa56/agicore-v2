"""Models for AGIcore Paper Broker Read-Only Connection Dry Run Execution Preparation Review."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewState(StrEnum):
    NOT_READY = "NOT_READY"
    DRY_RUN_EXECUTION_PREPARATION_REVIEW_INPUT_INVALID = "DRY_RUN_EXECUTION_PREPARATION_REVIEW_INPUT_INVALID"
    DRY_RUN_EXECUTION_PREPARATION_REVIEW_BLOCKED = "DRY_RUN_EXECUTION_PREPARATION_REVIEW_BLOCKED"
    DRY_RUN_EXECUTION_PREPARATION_REVIEW_COMPLETED_WITH_WARNINGS = "DRY_RUN_EXECUTION_PREPARATION_REVIEW_COMPLETED_WITH_WARNINGS"
    DRY_RUN_EXECUTION_PREPARATION_REVIEW_COMPLETED = "DRY_RUN_EXECUTION_PREPARATION_REVIEW_COMPLETED"
    READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN = (
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN"
    )


class PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewDecision(StrEnum):
    BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW = (
        "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW"
    )
    REQUIRE_DRY_RUN_EXECUTION_PREPARATION_FIXES = "REQUIRE_DRY_RUN_EXECUTION_PREPARATION_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_RUNTIME_CONTRACT_REVIEW_FIXES = "REQUIRE_DRY_RUN_EXECUTION_RUNTIME_CONTRACT_REVIEW_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_SEQUENCE_CONTRACT_REVIEW_FIXES = "REQUIRE_DRY_RUN_EXECUTION_SEQUENCE_CONTRACT_REVIEW_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_PRECONDITION_REVIEW_FIXES = "REQUIRE_DRY_RUN_EXECUTION_PRECONDITION_REVIEW_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_CREDENTIAL_REFERENCE_REVIEW_FIXES = "REQUIRE_DRY_RUN_EXECUTION_CREDENTIAL_REFERENCE_REVIEW_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_NO_SECRET_READ_GUARD_REVIEW_FIXES = (
        "REQUIRE_DRY_RUN_EXECUTION_NO_SECRET_READ_GUARD_REVIEW_FIXES"
    )
    REQUIRE_DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD_REVIEW_FIXES = (
        "REQUIRE_DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD_REVIEW_FIXES"
    )
    REQUIRE_DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_REVIEW_FIXES = "REQUIRE_DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_REVIEW_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_REVIEW_FIXES = (
        "REQUIRE_DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_REVIEW_FIXES"
    )
    REQUIRE_DRY_RUN_EXECUTION_ORDER_BLOCKING_REVIEW_FIXES = "REQUIRE_DRY_RUN_EXECUTION_ORDER_BLOCKING_REVIEW_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_REVIEW_FIXES = (
        "REQUIRE_DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_REVIEW_FIXES"
    )
    REQUIRE_DRY_RUN_EXECUTION_OBSERVABILITY_REVIEW_FIXES = "REQUIRE_DRY_RUN_EXECUTION_OBSERVABILITY_REVIEW_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_JOURNAL_REVIEW_FIXES = "REQUIRE_DRY_RUN_EXECUTION_JOURNAL_REVIEW_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_HUMAN_APPROVAL_REVIEW_FIXES = "REQUIRE_DRY_RUN_EXECUTION_HUMAN_APPROVAL_REVIEW_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_STOP_CONDITION_REVIEW_FIXES = "REQUIRE_DRY_RUN_EXECUTION_STOP_CONDITION_REVIEW_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_SUCCESS_FAILURE_REVIEW_FIXES = "REQUIRE_DRY_RUN_EXECUTION_SUCCESS_FAILURE_REVIEW_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_AUDIT_REVIEW_FIXES = "REQUIRE_DRY_RUN_EXECUTION_AUDIT_REVIEW_FIXES"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW = (
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW"
    )


class PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk(StrEnum):
    DRY_RUN_EXECUTION_PREPARATION_NOT_APPROVED = "DRY_RUN_EXECUTION_PREPARATION_NOT_APPROVED"
    DRY_RUN_EXECUTION_RUNTIME_CONTRACT_REVIEW_FAILED = "DRY_RUN_EXECUTION_RUNTIME_CONTRACT_REVIEW_FAILED"
    DRY_RUN_EXECUTION_SEQUENCE_CONTRACT_REVIEW_FAILED = "DRY_RUN_EXECUTION_SEQUENCE_CONTRACT_REVIEW_FAILED"
    DRY_RUN_EXECUTION_PRECONDITION_REVIEW_FAILED = "DRY_RUN_EXECUTION_PRECONDITION_REVIEW_FAILED"
    DRY_RUN_EXECUTION_CREDENTIAL_REFERENCE_REVIEW_FAILED = "DRY_RUN_EXECUTION_CREDENTIAL_REFERENCE_REVIEW_FAILED"
    DRY_RUN_EXECUTION_SECRET_READ_GUARD_REVIEW_FAILED = "DRY_RUN_EXECUTION_SECRET_READ_GUARD_REVIEW_FAILED"
    DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD_REVIEW_FAILED = "DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD_REVIEW_FAILED"
    DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW_FAILED = (
        "DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW_FAILED"
    )
    DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_REVIEW_FAILED = "DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_REVIEW_FAILED"
    DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_REVIEW_FAILED = "DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_REVIEW_FAILED"
    DRY_RUN_EXECUTION_ORDER_BLOCKING_REVIEW_FAILED = "DRY_RUN_EXECUTION_ORDER_BLOCKING_REVIEW_FAILED"
    DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_REVIEW_FAILED = "DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_REVIEW_FAILED"
    DRY_RUN_EXECUTION_OBSERVABILITY_REVIEW_FAILED = "DRY_RUN_EXECUTION_OBSERVABILITY_REVIEW_FAILED"
    DRY_RUN_EXECUTION_JOURNAL_REVIEW_FAILED = "DRY_RUN_EXECUTION_JOURNAL_REVIEW_FAILED"
    DRY_RUN_EXECUTION_HUMAN_APPROVAL_REVIEW_FAILED = "DRY_RUN_EXECUTION_HUMAN_APPROVAL_REVIEW_FAILED"
    DRY_RUN_EXECUTION_STOP_CONDITION_REVIEW_FAILED = "DRY_RUN_EXECUTION_STOP_CONDITION_REVIEW_FAILED"
    DRY_RUN_EXECUTION_SUCCESS_FAILURE_REVIEW_FAILED = "DRY_RUN_EXECUTION_SUCCESS_FAILURE_REVIEW_FAILED"
    DRY_RUN_EXECUTION_AUDIT_REVIEW_FAILED = "DRY_RUN_EXECUTION_AUDIT_REVIEW_FAILED"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN = (
        "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN"
    )


class PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRecommendation(StrEnum):
    HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN = (
        "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN"
    )
    APPROVE_DRY_RUN_EXECUTION_PREPARATION_FIRST = "APPROVE_DRY_RUN_EXECUTION_PREPARATION_FIRST"
    FIX_DRY_RUN_EXECUTION_RUNTIME_CONTRACT_REVIEW = "FIX_DRY_RUN_EXECUTION_RUNTIME_CONTRACT_REVIEW"
    FIX_DRY_RUN_EXECUTION_SEQUENCE_CONTRACT_REVIEW = "FIX_DRY_RUN_EXECUTION_SEQUENCE_CONTRACT_REVIEW"
    FIX_DRY_RUN_EXECUTION_PRECONDITION_REVIEW = "FIX_DRY_RUN_EXECUTION_PRECONDITION_REVIEW"
    FIX_DRY_RUN_EXECUTION_CREDENTIAL_REFERENCE_REVIEW = "FIX_DRY_RUN_EXECUTION_CREDENTIAL_REFERENCE_REVIEW"
    FIX_DRY_RUN_EXECUTION_NO_SECRET_READ_GUARD_REVIEW = "FIX_DRY_RUN_EXECUTION_NO_SECRET_READ_GUARD_REVIEW"
    FIX_DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD_REVIEW = "FIX_DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD_REVIEW"
    FIX_DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW = (
        "FIX_DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW"
    )
    FIX_DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_REVIEW = "FIX_DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_REVIEW"
    FIX_DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_REVIEW = "FIX_DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_REVIEW"
    FIX_DRY_RUN_EXECUTION_ORDER_BLOCKING_REVIEW = "FIX_DRY_RUN_EXECUTION_ORDER_BLOCKING_REVIEW"
    FIX_DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_REVIEW = "FIX_DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_REVIEW"
    FIX_DRY_RUN_EXECUTION_OBSERVABILITY_REVIEW = "FIX_DRY_RUN_EXECUTION_OBSERVABILITY_REVIEW"
    FIX_DRY_RUN_EXECUTION_JOURNAL_REVIEW = "FIX_DRY_RUN_EXECUTION_JOURNAL_REVIEW"
    FIX_DRY_RUN_EXECUTION_HUMAN_APPROVAL_REVIEW = "FIX_DRY_RUN_EXECUTION_HUMAN_APPROVAL_REVIEW"
    FIX_DRY_RUN_EXECUTION_STOP_CONDITION_REVIEW = "FIX_DRY_RUN_EXECUTION_STOP_CONDITION_REVIEW"
    FIX_DRY_RUN_EXECUTION_SUCCESS_FAILURE_REVIEW = "FIX_DRY_RUN_EXECUTION_SUCCESS_FAILURE_REVIEW"
    FIX_DRY_RUN_EXECUTION_AUDIT_REVIEW = "FIX_DRY_RUN_EXECUTION_AUDIT_REVIEW"
    RESTORE_OFFLINE_BOUNDARIES = "RESTORE_OFFLINE_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN = (
        "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN"
    )
    RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW_SUITE = (
        "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW_SUITE"
    )
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN = (
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN"
    )


@dataclass(frozen=True)
class _ReviewFinding:
    name: str = "review_finding"
    score: int = 0
    passed: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionRuntimeContractReviewFinding(_ReviewFinding):
    name: str = "dry_run_execution_runtime_contract_review"
    preparation_only: bool = True
    read_only_only: bool = True
    dry_run_execution_disabled: bool = True


@dataclass(frozen=True)
class DryRunExecutionSequenceContractReviewFinding(_ReviewFinding):
    name: str = "dry_run_execution_sequence_contract_review"
    dry_run_not_executed: bool = True
    connection_not_executed: bool = True
    sequence_steps_defined: bool = True
    network_transport_blocked: bool = True


@dataclass(frozen=True)
class DryRunExecutionPreconditionContractReviewFinding(_ReviewFinding):
    name: str = "dry_run_execution_precondition_contract_review"
    safety_gate_required: bool = True
    human_approval_required: bool = True
    stop_conditions_required: bool = True
    fail_closed: bool = True


@dataclass(frozen=True)
class DryRunExecutionCredentialsReferenceReviewFinding(_ReviewFinding):
    name: str = "dry_run_execution_credentials_reference_review"
    reference_only: bool = True
    no_secret_values: bool = True
    no_api_key_read: bool = True
    no_env_var_read: bool = True


@dataclass(frozen=True)
class DryRunExecutionNoSecretReadGuardReviewFinding(_ReviewFinding):
    name: str = "dry_run_execution_no_secret_read_guard_review"
    guard_enforced: bool = False
    no_api_key_read: bool = True
    no_env_var_read: bool = True
    no_hardcoded_secret: bool = True


@dataclass(frozen=True)
class DryRunExecutionNetworkBlockGuardReviewFinding(_ReviewFinding):
    name: str = "dry_run_execution_network_block_guard_review"
    network_execution_blocked: bool = True
    http_blocked: bool = True
    websocket_blocked: bool = True
    socket_blocked: bool = True
    external_api_blocked: bool = True


@dataclass(frozen=True)
class DryRunExecutionAccountReadOnlyReviewFinding(_ReviewFinding):
    name: str = "dry_run_execution_account_read_only_review"
    active_account_access_blocked: bool = True
    account_mutations_blocked: bool = True
    schema_only_account_review: bool = True


@dataclass(frozen=True)
class DryRunExecutionMarketDataReadOnlyReviewFinding(_ReviewFinding):
    name: str = "dry_run_execution_market_data_read_only_review"
    read_only_market_data_only: bool = True
    live_subscription_blocked: bool = True
    network_request_blocked: bool = True
    schema_or_synthetic_only: bool = True


@dataclass(frozen=True)
class DryRunExecutionOrderBlockingReviewFinding(_ReviewFinding):
    name: str = "dry_run_execution_order_blocking_review"
    order_execution_blocked: bool = True
    real_order_blocked: bool = True
    cancel_replace_blocked: bool = True


@dataclass(frozen=True)
class DryRunExecutionPositionMutationBlockReviewFinding(_ReviewFinding):
    name: str = "dry_run_execution_position_mutation_block_review"
    position_mutation_blocked: bool = True
    position_request_absent: bool = True
    close_modify_blocked: bool = True


@dataclass(frozen=True)
class DryRunExecutionObservabilityReviewFinding(_ReviewFinding):
    name: str = "dry_run_execution_observability_review"
    offline_events_defined: bool = True
    connection_attempt_logging_disabled: bool = True
    sensitive_values_redacted: bool = True


@dataclass(frozen=True)
class DryRunExecutionJournalReviewFinding(_ReviewFinding):
    name: str = "dry_run_execution_journal_review"
    offline_journal_required: bool = True
    sensitive_values_redacted: bool = True
    no_secret_material_logged: bool = True


@dataclass(frozen=True)
class DryRunExecutionHumanApprovalReviewFinding(_ReviewFinding):
    name: str = "dry_run_execution_human_approval_review"
    human_approval_required: bool = True
    approval_before_review: bool = True
    safety_gate_evidence_required: bool = True


@dataclass(frozen=True)
class DryRunExecutionStopConditionReviewFinding(_ReviewFinding):
    name: str = "dry_run_execution_stop_condition_review"
    stop_on_secret_read: bool = True
    stop_on_network_request: bool = True
    stop_on_order_or_position_request: bool = True
    stop_on_account_access_request: bool = True


@dataclass(frozen=True)
class DryRunExecutionSuccessFailureReviewFinding(_ReviewFinding):
    name: str = "dry_run_execution_success_failure_review"
    success_requires_no_real_connection: bool = True
    success_requires_all_guards_verified: bool = True
    failure_on_secret_network_order_position_or_account: bool = True


@dataclass(frozen=True)
class DryRunExecutionAuditReviewFinding(_ReviewFinding):
    name: str = "dry_run_execution_audit_review"
    audit_events_defined: bool = True
    offline_evidence_required: bool = True
    preparation_review_trace_required: bool = True


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewScore:
    overall_score: int
    dry_run_execution_preparation_score: int
    runtime_contract_score: int
    sequence_contract_score: int
    precondition_contract_score: int
    credentials_reference_score: int
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
    audit_score: int


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewInput:
    paper_broker_read_only_connection_dry_run_execution_preparation: Any = None
    paper_broker_read_only_connection_dry_run_execution_safety_gate: Any = None
    paper_broker_read_only_connection_dry_run_execution_plan: Any = None
    paper_broker_read_only_connection_dry_run_preparation_review: Any = None
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
    dry_run_execution_preparation_approved: bool | None = None
    dry_run_execution_runtime_contract_review_verified: bool | None = None
    dry_run_execution_sequence_contract_review_verified: bool | None = None
    dry_run_execution_precondition_contract_review_verified: bool | None = None
    dry_run_execution_credential_reference_review_verified: bool | None = None
    dry_run_execution_no_secret_read_guard_review_verified: bool | None = None
    dry_run_execution_network_block_guard_review_verified: bool | None = None
    dry_run_execution_http_websocket_socket_block_guard_review_verified: bool | None = None
    dry_run_execution_account_read_only_review_verified: bool | None = None
    dry_run_execution_market_data_read_only_review_verified: bool | None = None
    dry_run_execution_order_blocking_review_verified: bool | None = None
    dry_run_execution_position_mutation_block_review_verified: bool | None = None
    dry_run_execution_observability_review_verified: bool | None = None
    dry_run_execution_journal_review_verified: bool | None = None
    dry_run_execution_human_approval_review_verified: bool | None = None
    dry_run_execution_stop_conditions_review_verified: bool | None = None
    dry_run_execution_success_failure_review_verified: bool | None = None
    dry_run_execution_audit_review_verified: bool | None = None
    paper_broker_read_only_connection_dry_run_execution_final_plan_requested: bool | None = False
    paper_broker_read_only_connection_dry_run_execution_controlled_run_plan_requested: bool | None = False
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
    dry_run_execution_preparation_score: int | None = None
    runtime_contract_score: int | None = None
    sequence_contract_score: int | None = None
    precondition_contract_score: int | None = None
    credentials_reference_score: int | None = None
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
    audit_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewResult:
    state: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewState
    decision: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewDecision
    review_score: int
    score_breakdown: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewScore
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk, ...] = ()
    recommendations: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRecommendation, ...] = ()
    dry_run_execution_runtime_contract_review: DryRunExecutionRuntimeContractReviewFinding = field(
        default_factory=DryRunExecutionRuntimeContractReviewFinding
    )
    dry_run_execution_sequence_contract_review: DryRunExecutionSequenceContractReviewFinding = field(
        default_factory=DryRunExecutionSequenceContractReviewFinding
    )
    dry_run_execution_precondition_contract_review: DryRunExecutionPreconditionContractReviewFinding = field(
        default_factory=DryRunExecutionPreconditionContractReviewFinding
    )
    dry_run_execution_credentials_reference_review: DryRunExecutionCredentialsReferenceReviewFinding = field(
        default_factory=DryRunExecutionCredentialsReferenceReviewFinding
    )
    dry_run_execution_no_secret_read_guard_review: DryRunExecutionNoSecretReadGuardReviewFinding = field(
        default_factory=DryRunExecutionNoSecretReadGuardReviewFinding
    )
    dry_run_execution_network_block_guard_review: DryRunExecutionNetworkBlockGuardReviewFinding = field(
        default_factory=DryRunExecutionNetworkBlockGuardReviewFinding
    )
    dry_run_execution_http_websocket_socket_block_guard_review: DryRunExecutionNetworkBlockGuardReviewFinding = field(
        default_factory=lambda: DryRunExecutionNetworkBlockGuardReviewFinding(
            name="dry_run_execution_http_websocket_socket_block_guard_review"
        )
    )
    dry_run_execution_account_read_only_contract_review: DryRunExecutionAccountReadOnlyReviewFinding = field(
        default_factory=DryRunExecutionAccountReadOnlyReviewFinding
    )
    dry_run_execution_market_data_read_only_contract_review: DryRunExecutionMarketDataReadOnlyReviewFinding = field(
        default_factory=DryRunExecutionMarketDataReadOnlyReviewFinding
    )
    dry_run_execution_order_blocking_contract_review: DryRunExecutionOrderBlockingReviewFinding = field(
        default_factory=DryRunExecutionOrderBlockingReviewFinding
    )
    dry_run_execution_position_mutation_block_contract_review: DryRunExecutionPositionMutationBlockReviewFinding = field(
        default_factory=DryRunExecutionPositionMutationBlockReviewFinding
    )
    dry_run_execution_observability_contract_review: DryRunExecutionObservabilityReviewFinding = field(
        default_factory=DryRunExecutionObservabilityReviewFinding
    )
    dry_run_execution_journal_contract_review: DryRunExecutionJournalReviewFinding = field(
        default_factory=DryRunExecutionJournalReviewFinding
    )
    dry_run_execution_human_approval_contract_review: DryRunExecutionHumanApprovalReviewFinding = field(
        default_factory=DryRunExecutionHumanApprovalReviewFinding
    )
    dry_run_execution_stop_conditions_contract_review: DryRunExecutionStopConditionReviewFinding = field(
        default_factory=DryRunExecutionStopConditionReviewFinding
    )
    dry_run_execution_success_failure_contract_review: DryRunExecutionSuccessFailureReviewFinding = field(
        default_factory=DryRunExecutionSuccessFailureReviewFinding
    )
    dry_run_execution_audit_contract_review: DryRunExecutionAuditReviewFinding = field(
        default_factory=DryRunExecutionAuditReviewFinding
    )
    offline_only: bool = True
    summary: str = ""
