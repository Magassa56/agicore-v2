"""Models for AGIcore Paper Broker Read-Only Connection Dry Run Execution Preparation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerReadOnlyConnectionDryRunExecutionPreparationState(StrEnum):
    NOT_READY = "NOT_READY"
    DRY_RUN_EXECUTION_PREPARATION_INPUT_INVALID = "DRY_RUN_EXECUTION_PREPARATION_INPUT_INVALID"
    DRY_RUN_EXECUTION_PREPARATION_BLOCKED = "DRY_RUN_EXECUTION_PREPARATION_BLOCKED"
    DRY_RUN_EXECUTION_PREPARATION_COMPLETED_WITH_WARNINGS = "DRY_RUN_EXECUTION_PREPARATION_COMPLETED_WITH_WARNINGS"
    DRY_RUN_EXECUTION_PREPARATION_COMPLETED = "DRY_RUN_EXECUTION_PREPARATION_COMPLETED"
    READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW = (
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW"
    )


class PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision(StrEnum):
    BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION = (
        "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION"
    )
    REQUIRE_DRY_RUN_EXECUTION_SAFETY_GATE_FIXES = "REQUIRE_DRY_RUN_EXECUTION_SAFETY_GATE_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_RUNTIME_CONTRACT_FIXES = "REQUIRE_DRY_RUN_EXECUTION_RUNTIME_CONTRACT_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_SEQUENCE_CONTRACT_FIXES = "REQUIRE_DRY_RUN_EXECUTION_SEQUENCE_CONTRACT_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_PRECONDITION_CONTRACT_FIXES = "REQUIRE_DRY_RUN_EXECUTION_PRECONDITION_CONTRACT_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_CREDENTIAL_REFERENCE_FIXES = "REQUIRE_DRY_RUN_EXECUTION_CREDENTIAL_REFERENCE_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_NO_SECRET_READ_GUARD_FIXES = "REQUIRE_DRY_RUN_EXECUTION_NO_SECRET_READ_GUARD_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD_FIXES = "REQUIRE_DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_FIXES = "REQUIRE_DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_FIXES = "REQUIRE_DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_ORDER_BLOCKING_FIXES = "REQUIRE_DRY_RUN_EXECUTION_ORDER_BLOCKING_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_FIXES = "REQUIRE_DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_OBSERVABILITY_FIXES = "REQUIRE_DRY_RUN_EXECUTION_OBSERVABILITY_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_JOURNAL_FIXES = "REQUIRE_DRY_RUN_EXECUTION_JOURNAL_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_HUMAN_APPROVAL_FIXES = "REQUIRE_DRY_RUN_EXECUTION_HUMAN_APPROVAL_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_STOP_CONDITION_FIXES = "REQUIRE_DRY_RUN_EXECUTION_STOP_CONDITION_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_SUCCESS_FAILURE_FIXES = "REQUIRE_DRY_RUN_EXECUTION_SUCCESS_FAILURE_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_AUDIT_FIXES = "REQUIRE_DRY_RUN_EXECUTION_AUDIT_FIXES"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION = (
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION"
    )


class PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk(StrEnum):
    DRY_RUN_EXECUTION_SAFETY_GATE_NOT_APPROVED = "DRY_RUN_EXECUTION_SAFETY_GATE_NOT_APPROVED"
    DRY_RUN_EXECUTION_RUNTIME_CONTRACT_MISSING = "DRY_RUN_EXECUTION_RUNTIME_CONTRACT_MISSING"
    DRY_RUN_EXECUTION_SEQUENCE_CONTRACT_MISSING = "DRY_RUN_EXECUTION_SEQUENCE_CONTRACT_MISSING"
    DRY_RUN_EXECUTION_PRECONDITION_CONTRACT_MISSING = "DRY_RUN_EXECUTION_PRECONDITION_CONTRACT_MISSING"
    DRY_RUN_EXECUTION_CREDENTIAL_REFERENCE_UNSAFE = "DRY_RUN_EXECUTION_CREDENTIAL_REFERENCE_UNSAFE"
    DRY_RUN_EXECUTION_SECRET_READ_GUARD_MISSING = "DRY_RUN_EXECUTION_SECRET_READ_GUARD_MISSING"
    DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD_MISSING = "DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD_MISSING"
    DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_MISSING = "DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_MISSING"
    DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_UNSAFE = "DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_UNSAFE"
    DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_UNSAFE = "DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_UNSAFE"
    DRY_RUN_EXECUTION_ORDER_BLOCKING_UNSAFE = "DRY_RUN_EXECUTION_ORDER_BLOCKING_UNSAFE"
    DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_UNSAFE = "DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_UNSAFE"
    DRY_RUN_EXECUTION_OBSERVABILITY_INCOMPLETE = "DRY_RUN_EXECUTION_OBSERVABILITY_INCOMPLETE"
    DRY_RUN_EXECUTION_JOURNAL_INCOMPLETE = "DRY_RUN_EXECUTION_JOURNAL_INCOMPLETE"
    DRY_RUN_EXECUTION_HUMAN_APPROVAL_MISSING = "DRY_RUN_EXECUTION_HUMAN_APPROVAL_MISSING"
    DRY_RUN_EXECUTION_STOP_CONDITIONS_MISSING = "DRY_RUN_EXECUTION_STOP_CONDITIONS_MISSING"
    DRY_RUN_EXECUTION_SUCCESS_FAILURE_CONTRACT_MISSING = "DRY_RUN_EXECUTION_SUCCESS_FAILURE_CONTRACT_MISSING"
    DRY_RUN_EXECUTION_AUDIT_CONTRACT_MISSING = "DRY_RUN_EXECUTION_AUDIT_CONTRACT_MISSING"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW = (
        "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW"
    )


class PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation(StrEnum):
    HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW = (
        "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW"
    )
    APPROVE_DRY_RUN_EXECUTION_SAFETY_GATE_FIRST = "APPROVE_DRY_RUN_EXECUTION_SAFETY_GATE_FIRST"
    PREPARE_DRY_RUN_EXECUTION_RUNTIME_CONTRACT = "PREPARE_DRY_RUN_EXECUTION_RUNTIME_CONTRACT"
    PREPARE_DRY_RUN_EXECUTION_SEQUENCE_CONTRACT = "PREPARE_DRY_RUN_EXECUTION_SEQUENCE_CONTRACT"
    PREPARE_DRY_RUN_EXECUTION_PRECONDITION_CONTRACT = "PREPARE_DRY_RUN_EXECUTION_PRECONDITION_CONTRACT"
    HARDEN_DRY_RUN_EXECUTION_CREDENTIAL_REFERENCE = "HARDEN_DRY_RUN_EXECUTION_CREDENTIAL_REFERENCE"
    INSTALL_DRY_RUN_EXECUTION_NO_SECRET_READ_GUARD = "INSTALL_DRY_RUN_EXECUTION_NO_SECRET_READ_GUARD"
    INSTALL_DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD = "INSTALL_DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD"
    INSTALL_DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD = "INSTALL_DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD"
    HARDEN_DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY = "HARDEN_DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY"
    HARDEN_DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY = "HARDEN_DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY"
    HARDEN_DRY_RUN_EXECUTION_ORDER_BLOCKING = "HARDEN_DRY_RUN_EXECUTION_ORDER_BLOCKING"
    HARDEN_DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK = "HARDEN_DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK"
    COMPLETE_DRY_RUN_EXECUTION_OBSERVABILITY = "COMPLETE_DRY_RUN_EXECUTION_OBSERVABILITY"
    COMPLETE_DRY_RUN_EXECUTION_JOURNAL = "COMPLETE_DRY_RUN_EXECUTION_JOURNAL"
    REQUIRE_DRY_RUN_EXECUTION_HUMAN_APPROVAL = "REQUIRE_DRY_RUN_EXECUTION_HUMAN_APPROVAL"
    DEFINE_DRY_RUN_EXECUTION_STOP_CONDITIONS = "DEFINE_DRY_RUN_EXECUTION_STOP_CONDITIONS"
    PREPARE_DRY_RUN_EXECUTION_SUCCESS_FAILURE_CONTRACT = "PREPARE_DRY_RUN_EXECUTION_SUCCESS_FAILURE_CONTRACT"
    PREPARE_DRY_RUN_EXECUTION_AUDIT_CONTRACT = "PREPARE_DRY_RUN_EXECUTION_AUDIT_CONTRACT"
    RESTORE_OFFLINE_BOUNDARIES = "RESTORE_OFFLINE_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW = (
        "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW"
    )
    RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_SUITE = (
        "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_SUITE"
    )
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW = (
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW"
    )


@dataclass(frozen=True)
class DryRunExecutionRuntimeContract:
    name: str = "dry_run_execution_runtime_contract"
    score: int = 0
    defined: bool = False
    preparation_only: bool = True
    read_only_only: bool = True
    dry_run_execution_disabled: bool = True
    allowed_actions: tuple[str, ...] = ()
    prohibited_actions: tuple[str, ...] = ()
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionSequenceContract:
    name: str = "dry_run_execution_sequence_contract"
    score: int = 0
    defined: bool = False
    dry_run_not_executed: bool = True
    connection_not_executed: bool = True
    sequence_steps_defined: bool = True
    network_transport_blocked: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionPreconditionContract:
    name: str = "dry_run_execution_precondition_contract"
    score: int = 0
    defined: bool = False
    safety_gate_required: bool = True
    human_approval_required: bool = True
    stop_conditions_required: bool = True
    fail_closed: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionCredentialsReferenceContract:
    name: str = "dry_run_execution_credentials_reference_contract"
    score: int = 0
    defined: bool = False
    reference_only: bool = True
    no_secret_values: bool = True
    no_api_key_read: bool = True
    no_env_var_read: bool = True
    secret_source: str = "none_in_this_phase"
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionNoSecretReadGuard:
    name: str = "dry_run_execution_no_secret_read_guard"
    score: int = 0
    defined: bool = False
    guard_enforced: bool = False
    no_api_key_read: bool = True
    no_env_var_read: bool = True
    no_hardcoded_secret: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionNetworkBlockGuard:
    name: str = "dry_run_execution_network_block_guard"
    score: int = 0
    defined: bool = False
    network_execution_blocked: bool = True
    http_blocked: bool = True
    websocket_blocked: bool = True
    socket_blocked: bool = True
    external_api_blocked: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionAccountReadOnlyContract:
    name: str = "dry_run_execution_account_read_only_contract"
    score: int = 0
    defined: bool = False
    active_account_access_blocked: bool = True
    account_mutations_blocked: bool = True
    schema_only_account_review: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionMarketDataReadOnlyContract:
    name: str = "dry_run_execution_market_data_read_only_contract"
    score: int = 0
    defined: bool = False
    read_only_market_data_only: bool = True
    live_subscription_blocked: bool = True
    network_request_blocked: bool = True
    schema_or_synthetic_only: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionOrderBlockingContract:
    name: str = "dry_run_execution_order_blocking_contract"
    score: int = 0
    defined: bool = False
    order_execution_blocked: bool = True
    real_order_blocked: bool = True
    cancel_replace_blocked: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionPositionMutationBlockContract:
    name: str = "dry_run_execution_position_mutation_block_contract"
    score: int = 0
    defined: bool = False
    position_mutation_blocked: bool = True
    position_request_absent: bool = True
    close_modify_blocked: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionObservabilityContract:
    name: str = "dry_run_execution_observability_contract"
    score: int = 0
    defined: bool = False
    offline_events_defined: bool = True
    connection_attempt_logging_disabled: bool = True
    sensitive_values_redacted: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionJournalContract:
    name: str = "dry_run_execution_journal_contract"
    score: int = 0
    defined: bool = False
    offline_journal_required: bool = True
    sensitive_values_redacted: bool = True
    no_secret_material_logged: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionHumanApprovalContract:
    name: str = "dry_run_execution_human_approval_contract"
    score: int = 0
    defined: bool = False
    human_approval_required: bool = True
    approval_before_review: bool = True
    safety_gate_evidence_required: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionStopConditionContract:
    name: str = "dry_run_execution_stop_conditions_contract"
    score: int = 0
    defined: bool = False
    stop_on_secret_read: bool = True
    stop_on_network_request: bool = True
    stop_on_order_or_position_request: bool = True
    stop_on_account_access_request: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionSuccessFailureContract:
    name: str = "dry_run_execution_success_failure_contract"
    score: int = 0
    defined: bool = False
    success_requires_no_real_connection: bool = True
    success_requires_all_guards_verified: bool = True
    failure_on_secret_network_order_position_or_account: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionAuditContract:
    name: str = "dry_run_execution_audit_contract"
    score: int = 0
    defined: bool = False
    audit_events_defined: bool = True
    offline_evidence_required: bool = True
    preparation_review_trace_required: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunExecutionPreparationScore:
    overall_score: int
    dry_run_execution_safety_gate_score: int
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
class PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput:
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
    dry_run_execution_safety_gate_approved: bool | None = None
    dry_run_execution_runtime_contract_prepared: bool | None = None
    dry_run_execution_sequence_contract_prepared: bool | None = None
    dry_run_execution_precondition_contract_prepared: bool | None = None
    dry_run_execution_credentials_reference_contract_prepared: bool | None = None
    dry_run_execution_credentials_reference_only: bool | None = None
    dry_run_execution_no_secret_read_guard_prepared: bool | None = None
    dry_run_execution_secret_read_guard_enforced: bool | None = None
    dry_run_execution_network_block_guard_prepared: bool | None = None
    dry_run_execution_network_blocked: bool | None = None
    dry_run_execution_http_websocket_socket_block_guard_prepared: bool | None = None
    dry_run_execution_http_transport_blocked: bool | None = None
    dry_run_execution_websocket_transport_blocked: bool | None = None
    dry_run_execution_socket_transport_blocked: bool | None = None
    dry_run_execution_external_api_blocked: bool | None = None
    dry_run_execution_account_read_only_contract_prepared: bool | None = None
    dry_run_execution_account_active_access_blocked: bool | None = None
    dry_run_execution_account_mutations_blocked: bool | None = None
    dry_run_execution_market_data_read_only_contract_prepared: bool | None = None
    dry_run_execution_market_data_live_subscription_blocked: bool | None = None
    dry_run_execution_market_data_network_request_blocked: bool | None = None
    dry_run_execution_order_blocking_contract_prepared: bool | None = None
    dry_run_execution_order_execution_blocked: bool | None = None
    dry_run_execution_cancel_replace_blocked: bool | None = None
    dry_run_execution_position_mutation_block_contract_prepared: bool | None = None
    dry_run_execution_position_mutation_blocked: bool | None = None
    dry_run_execution_observability_contract_prepared: bool | None = None
    dry_run_execution_journal_contract_prepared: bool | None = None
    dry_run_execution_human_approval_contract_prepared: bool | None = None
    dry_run_execution_human_approval_required: bool | None = None
    dry_run_execution_stop_conditions_contract_prepared: bool | None = None
    dry_run_execution_success_failure_contract_prepared: bool | None = None
    dry_run_execution_audit_contract_prepared: bool | None = None
    paper_broker_read_only_connection_dry_run_execution_preparation_review_requested: bool | None = False
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
    dry_run_execution_safety_gate_score: int | None = None
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
class PaperBrokerReadOnlyConnectionDryRunExecutionPreparationResult:
    state: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationState
    decision: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision
    preparation_score: int
    score_breakdown: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationScore
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk, ...] = ()
    recommendations: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation, ...] = ()
    dry_run_execution_runtime_contract: DryRunExecutionRuntimeContract = field(default_factory=DryRunExecutionRuntimeContract)
    dry_run_execution_sequence_contract: DryRunExecutionSequenceContract = field(default_factory=DryRunExecutionSequenceContract)
    dry_run_execution_precondition_contract: DryRunExecutionPreconditionContract = field(default_factory=DryRunExecutionPreconditionContract)
    dry_run_execution_credentials_reference_contract: DryRunExecutionCredentialsReferenceContract = field(
        default_factory=DryRunExecutionCredentialsReferenceContract
    )
    dry_run_execution_no_secret_read_guard: DryRunExecutionNoSecretReadGuard = field(default_factory=DryRunExecutionNoSecretReadGuard)
    dry_run_execution_network_block_guard: DryRunExecutionNetworkBlockGuard = field(default_factory=DryRunExecutionNetworkBlockGuard)
    dry_run_execution_http_websocket_socket_block_guard: DryRunExecutionNetworkBlockGuard = field(
        default_factory=lambda: DryRunExecutionNetworkBlockGuard(name="dry_run_execution_http_websocket_socket_block_guard")
    )
    dry_run_execution_account_read_only_contract: DryRunExecutionAccountReadOnlyContract = field(default_factory=DryRunExecutionAccountReadOnlyContract)
    dry_run_execution_market_data_read_only_contract: DryRunExecutionMarketDataReadOnlyContract = field(
        default_factory=DryRunExecutionMarketDataReadOnlyContract
    )
    dry_run_execution_order_blocking_contract: DryRunExecutionOrderBlockingContract = field(default_factory=DryRunExecutionOrderBlockingContract)
    dry_run_execution_position_mutation_block_contract: DryRunExecutionPositionMutationBlockContract = field(
        default_factory=DryRunExecutionPositionMutationBlockContract
    )
    dry_run_execution_observability_contract: DryRunExecutionObservabilityContract = field(default_factory=DryRunExecutionObservabilityContract)
    dry_run_execution_journal_contract: DryRunExecutionJournalContract = field(default_factory=DryRunExecutionJournalContract)
    dry_run_execution_human_approval_contract: DryRunExecutionHumanApprovalContract = field(default_factory=DryRunExecutionHumanApprovalContract)
    dry_run_execution_stop_conditions_contract: DryRunExecutionStopConditionContract = field(default_factory=DryRunExecutionStopConditionContract)
    dry_run_execution_success_failure_contract: DryRunExecutionSuccessFailureContract = field(default_factory=DryRunExecutionSuccessFailureContract)
    dry_run_execution_audit_contract: DryRunExecutionAuditContract = field(default_factory=DryRunExecutionAuditContract)
    offline_only: bool = True
    summary: str = ""
