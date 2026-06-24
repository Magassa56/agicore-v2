"""Models for Paper Broker Read-Only Connection Dry Run Controlled Execution Preparation Review."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewState(StrEnum):
    NOT_READY = "NOT_READY"
    CONTROLLED_EXECUTION_PREPARATION_REVIEW_INPUT_INVALID = "CONTROLLED_EXECUTION_PREPARATION_REVIEW_INPUT_INVALID"
    CONTROLLED_EXECUTION_PREPARATION_REVIEW_BLOCKED = "CONTROLLED_EXECUTION_PREPARATION_REVIEW_BLOCKED"
    CONTROLLED_EXECUTION_PREPARATION_REVIEW_COMPLETED_WITH_WARNINGS = "CONTROLLED_EXECUTION_PREPARATION_REVIEW_COMPLETED_WITH_WARNINGS"
    CONTROLLED_EXECUTION_PREPARATION_REVIEW_COMPLETED = "CONTROLLED_EXECUTION_PREPARATION_REVIEW_COMPLETED"
    READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_PLAN = "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_PLAN"


class PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewDecision(StrEnum):
    BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW = "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW"
    REQUIRE_CONTROLLED_EXECUTION_PREPARATION_FIXES = "REQUIRE_CONTROLLED_EXECUTION_PREPARATION_FIXES"
    REQUIRE_CONTROLLED_RUNTIME_CONTRACT_REVIEW_FIXES = "REQUIRE_CONTROLLED_RUNTIME_CONTRACT_REVIEW_FIXES"
    REQUIRE_CONTROLLED_SEQUENCE_CONTRACT_REVIEW_FIXES = "REQUIRE_CONTROLLED_SEQUENCE_CONTRACT_REVIEW_FIXES"
    REQUIRE_CONTROLLED_PRECONDITION_REVIEW_FIXES = "REQUIRE_CONTROLLED_PRECONDITION_REVIEW_FIXES"
    REQUIRE_CONTROLLED_CREDENTIAL_REFERENCE_REVIEW_FIXES = "REQUIRE_CONTROLLED_CREDENTIAL_REFERENCE_REVIEW_FIXES"
    REQUIRE_CONTROLLED_NO_SECRET_READ_GUARD_REVIEW_FIXES = "REQUIRE_CONTROLLED_NO_SECRET_READ_GUARD_REVIEW_FIXES"
    REQUIRE_CONTROLLED_NETWORK_BLOCK_GUARD_REVIEW_FIXES = "REQUIRE_CONTROLLED_NETWORK_BLOCK_GUARD_REVIEW_FIXES"
    REQUIRE_CONTROLLED_ACCOUNT_READ_ONLY_REVIEW_FIXES = "REQUIRE_CONTROLLED_ACCOUNT_READ_ONLY_REVIEW_FIXES"
    REQUIRE_CONTROLLED_MARKET_DATA_READ_ONLY_REVIEW_FIXES = "REQUIRE_CONTROLLED_MARKET_DATA_READ_ONLY_REVIEW_FIXES"
    REQUIRE_CONTROLLED_ORDER_BLOCKING_REVIEW_FIXES = "REQUIRE_CONTROLLED_ORDER_BLOCKING_REVIEW_FIXES"
    REQUIRE_CONTROLLED_POSITION_MUTATION_BLOCK_REVIEW_FIXES = "REQUIRE_CONTROLLED_POSITION_MUTATION_BLOCK_REVIEW_FIXES"
    REQUIRE_CONTROLLED_OBSERVABILITY_REVIEW_FIXES = "REQUIRE_CONTROLLED_OBSERVABILITY_REVIEW_FIXES"
    REQUIRE_CONTROLLED_JOURNAL_REVIEW_FIXES = "REQUIRE_CONTROLLED_JOURNAL_REVIEW_FIXES"
    REQUIRE_CONTROLLED_HUMAN_APPROVAL_REVIEW_FIXES = "REQUIRE_CONTROLLED_HUMAN_APPROVAL_REVIEW_FIXES"
    REQUIRE_CONTROLLED_STOP_CONDITION_REVIEW_FIXES = "REQUIRE_CONTROLLED_STOP_CONDITION_REVIEW_FIXES"
    REQUIRE_CONTROLLED_SUCCESS_FAILURE_REVIEW_FIXES = "REQUIRE_CONTROLLED_SUCCESS_FAILURE_REVIEW_FIXES"
    REQUIRE_CONTROLLED_AUDIT_REVIEW_FIXES = "REQUIRE_CONTROLLED_AUDIT_REVIEW_FIXES"
    REQUIRE_CONTROLLED_GO_NO_GO_REVIEW_FIXES = "REQUIRE_CONTROLLED_GO_NO_GO_REVIEW_FIXES"
    REQUIRE_CONTROLLED_ABORT_REVIEW_FIXES = "REQUIRE_CONTROLLED_ABORT_REVIEW_FIXES"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW = "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW"


class PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRisk(StrEnum):
    CONTROLLED_EXECUTION_PREPARATION_NOT_APPROVED = "CONTROLLED_EXECUTION_PREPARATION_NOT_APPROVED"
    CONTROLLED_RUNTIME_CONTRACT_REVIEW_FAILED = "CONTROLLED_RUNTIME_CONTRACT_REVIEW_FAILED"
    CONTROLLED_SEQUENCE_CONTRACT_REVIEW_FAILED = "CONTROLLED_SEQUENCE_CONTRACT_REVIEW_FAILED"
    CONTROLLED_PRECONDITION_REVIEW_FAILED = "CONTROLLED_PRECONDITION_REVIEW_FAILED"
    CONTROLLED_CREDENTIAL_REFERENCE_REVIEW_FAILED = "CONTROLLED_CREDENTIAL_REFERENCE_REVIEW_FAILED"
    CONTROLLED_SECRET_READ_GUARD_REVIEW_FAILED = "CONTROLLED_SECRET_READ_GUARD_REVIEW_FAILED"
    CONTROLLED_NETWORK_BLOCK_GUARD_REVIEW_FAILED = "CONTROLLED_NETWORK_BLOCK_GUARD_REVIEW_FAILED"
    CONTROLLED_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW_FAILED = "CONTROLLED_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW_FAILED"
    CONTROLLED_ACCOUNT_READ_ONLY_REVIEW_FAILED = "CONTROLLED_ACCOUNT_READ_ONLY_REVIEW_FAILED"
    CONTROLLED_MARKET_DATA_READ_ONLY_REVIEW_FAILED = "CONTROLLED_MARKET_DATA_READ_ONLY_REVIEW_FAILED"
    CONTROLLED_ORDER_BLOCKING_REVIEW_FAILED = "CONTROLLED_ORDER_BLOCKING_REVIEW_FAILED"
    CONTROLLED_POSITION_MUTATION_BLOCK_REVIEW_FAILED = "CONTROLLED_POSITION_MUTATION_BLOCK_REVIEW_FAILED"
    CONTROLLED_OBSERVABILITY_REVIEW_FAILED = "CONTROLLED_OBSERVABILITY_REVIEW_FAILED"
    CONTROLLED_JOURNAL_REVIEW_FAILED = "CONTROLLED_JOURNAL_REVIEW_FAILED"
    CONTROLLED_HUMAN_APPROVAL_REVIEW_FAILED = "CONTROLLED_HUMAN_APPROVAL_REVIEW_FAILED"
    CONTROLLED_STOP_CONDITION_REVIEW_FAILED = "CONTROLLED_STOP_CONDITION_REVIEW_FAILED"
    CONTROLLED_SUCCESS_FAILURE_REVIEW_FAILED = "CONTROLLED_SUCCESS_FAILURE_REVIEW_FAILED"
    CONTROLLED_AUDIT_REVIEW_FAILED = "CONTROLLED_AUDIT_REVIEW_FAILED"
    CONTROLLED_GO_NO_GO_REVIEW_FAILED = "CONTROLLED_GO_NO_GO_REVIEW_FAILED"
    CONTROLLED_ABORT_REVIEW_FAILED = "CONTROLLED_ABORT_REVIEW_FAILED"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_PLAN = "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_PLAN"


class PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRecommendation(StrEnum):
    HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_PLAN = "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_PLAN"
    APPROVE_CONTROLLED_EXECUTION_PREPARATION_FIRST = "APPROVE_CONTROLLED_EXECUTION_PREPARATION_FIRST"
    FIX_CONTROLLED_RUNTIME_CONTRACT_REVIEW = "FIX_CONTROLLED_RUNTIME_CONTRACT_REVIEW"
    FIX_CONTROLLED_SEQUENCE_CONTRACT_REVIEW = "FIX_CONTROLLED_SEQUENCE_CONTRACT_REVIEW"
    FIX_CONTROLLED_PRECONDITION_REVIEW = "FIX_CONTROLLED_PRECONDITION_REVIEW"
    FIX_CONTROLLED_CREDENTIAL_REFERENCE_REVIEW = "FIX_CONTROLLED_CREDENTIAL_REFERENCE_REVIEW"
    FIX_CONTROLLED_NO_SECRET_READ_GUARD_REVIEW = "FIX_CONTROLLED_NO_SECRET_READ_GUARD_REVIEW"
    FIX_CONTROLLED_NETWORK_BLOCK_GUARD_REVIEW = "FIX_CONTROLLED_NETWORK_BLOCK_GUARD_REVIEW"
    FIX_CONTROLLED_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW = "FIX_CONTROLLED_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW"
    FIX_CONTROLLED_ACCOUNT_READ_ONLY_REVIEW = "FIX_CONTROLLED_ACCOUNT_READ_ONLY_REVIEW"
    FIX_CONTROLLED_MARKET_DATA_READ_ONLY_REVIEW = "FIX_CONTROLLED_MARKET_DATA_READ_ONLY_REVIEW"
    FIX_CONTROLLED_ORDER_BLOCKING_REVIEW = "FIX_CONTROLLED_ORDER_BLOCKING_REVIEW"
    FIX_CONTROLLED_POSITION_MUTATION_BLOCK_REVIEW = "FIX_CONTROLLED_POSITION_MUTATION_BLOCK_REVIEW"
    FIX_CONTROLLED_OBSERVABILITY_REVIEW = "FIX_CONTROLLED_OBSERVABILITY_REVIEW"
    FIX_CONTROLLED_JOURNAL_REVIEW = "FIX_CONTROLLED_JOURNAL_REVIEW"
    FIX_CONTROLLED_HUMAN_APPROVAL_REVIEW = "FIX_CONTROLLED_HUMAN_APPROVAL_REVIEW"
    FIX_CONTROLLED_STOP_CONDITION_REVIEW = "FIX_CONTROLLED_STOP_CONDITION_REVIEW"
    FIX_CONTROLLED_SUCCESS_FAILURE_REVIEW = "FIX_CONTROLLED_SUCCESS_FAILURE_REVIEW"
    FIX_CONTROLLED_AUDIT_REVIEW = "FIX_CONTROLLED_AUDIT_REVIEW"
    FIX_CONTROLLED_GO_NO_GO_REVIEW = "FIX_CONTROLLED_GO_NO_GO_REVIEW"
    FIX_CONTROLLED_ABORT_REVIEW = "FIX_CONTROLLED_ABORT_REVIEW"
    RESTORE_OFFLINE_BOUNDARIES = "RESTORE_OFFLINE_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_PLAN = "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_PLAN"
    RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW_SUITE = "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW_SUITE"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_PLAN = "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_PLAN"


Risk = PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRisk


@dataclass(frozen=True)
class _ReviewFinding:
    name: str = "controlled_review_finding"
    score: int = 0
    passed: bool = False
    risks: tuple[Risk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ControlledExecutionRuntimeContractReviewFinding(_ReviewFinding):
    name: str = "controlled_execution_runtime_contract_review"
    preparation_only: bool = True
    read_only_only: bool = True
    dry_run_execution_disabled: bool = True


@dataclass(frozen=True)
class ControlledExecutionSequenceContractReviewFinding(_ReviewFinding):
    name: str = "controlled_execution_sequence_contract_review"
    dry_run_not_executed: bool = True
    connection_not_executed: bool = True
    sequence_steps_defined: bool = True
    network_transport_blocked: bool = True


@dataclass(frozen=True)
class ControlledExecutionPreconditionContractReviewFinding(_ReviewFinding):
    name: str = "controlled_execution_precondition_contract_review"
    safety_gate_required: bool = True
    human_approval_required: bool = True
    stop_conditions_required: bool = True
    fail_closed: bool = True


@dataclass(frozen=True)
class ControlledCredentialsReferenceReviewFinding(_ReviewFinding):
    name: str = "controlled_credentials_reference_review"
    reference_only: bool = True
    no_secret_values: bool = True
    no_api_key_read: bool = True
    no_env_var_read: bool = True


@dataclass(frozen=True)
class ControlledNoSecretReadGuardReviewFinding(_ReviewFinding):
    name: str = "controlled_no_secret_read_guard_review"
    guard_enforced: bool = False
    no_api_key_read: bool = True
    no_env_var_read: bool = True
    no_hardcoded_secret: bool = True


@dataclass(frozen=True)
class ControlledNetworkBlockGuardReviewFinding(_ReviewFinding):
    name: str = "controlled_network_block_guard_review"
    network_execution_blocked: bool = True
    http_blocked: bool = True
    websocket_blocked: bool = True
    socket_blocked: bool = True
    external_api_blocked: bool = True


@dataclass(frozen=True)
class ControlledAccountReadOnlyReviewFinding(_ReviewFinding):
    name: str = "controlled_account_read_only_review"
    active_account_access_blocked: bool = True
    account_mutations_blocked: bool = True
    schema_only_account_review: bool = True


@dataclass(frozen=True)
class ControlledMarketDataReadOnlyReviewFinding(_ReviewFinding):
    name: str = "controlled_market_data_read_only_review"
    read_only_market_data_only: bool = True
    live_subscription_blocked: bool = True
    network_request_blocked: bool = True
    schema_or_synthetic_only: bool = True


@dataclass(frozen=True)
class ControlledOrderBlockingReviewFinding(_ReviewFinding):
    name: str = "controlled_order_blocking_review"
    order_execution_blocked: bool = True
    real_order_blocked: bool = True
    cancel_replace_blocked: bool = True


@dataclass(frozen=True)
class ControlledPositionMutationBlockReviewFinding(_ReviewFinding):
    name: str = "controlled_position_mutation_block_review"
    position_mutation_blocked: bool = True
    position_request_absent: bool = True
    close_modify_blocked: bool = True


@dataclass(frozen=True)
class ControlledObservabilityReviewFinding(_ReviewFinding):
    name: str = "controlled_observability_review"
    offline_events_defined: bool = True
    connection_attempt_logging_disabled: bool = True
    sensitive_values_redacted: bool = True


@dataclass(frozen=True)
class ControlledJournalReviewFinding(_ReviewFinding):
    name: str = "controlled_journal_review"
    offline_journal_required: bool = True
    sensitive_values_redacted: bool = True
    no_secret_material_logged: bool = True


@dataclass(frozen=True)
class ControlledHumanApprovalReviewFinding(_ReviewFinding):
    name: str = "controlled_human_approval_review"
    human_approval_required: bool = True
    approval_before_review: bool = True
    safety_gate_evidence_required: bool = True


@dataclass(frozen=True)
class ControlledStopConditionReviewFinding(_ReviewFinding):
    name: str = "controlled_stop_condition_review"
    stop_on_secret_read: bool = True
    stop_on_network_request: bool = True
    stop_on_order_or_position_request: bool = True
    stop_on_account_access_request: bool = True


@dataclass(frozen=True)
class ControlledSuccessFailureReviewFinding(_ReviewFinding):
    name: str = "controlled_success_failure_review"
    success_requires_no_real_connection: bool = True
    success_requires_all_guards_verified: bool = True
    failure_on_secret_network_order_position_or_account: bool = True


@dataclass(frozen=True)
class ControlledAuditReviewFinding(_ReviewFinding):
    name: str = "controlled_audit_review"
    audit_events_defined: bool = True
    offline_evidence_required: bool = True
    preparation_review_trace_required: bool = True


@dataclass(frozen=True)
class ControlledGoNoGoReviewFinding(_ReviewFinding):
    name: str = "controlled_go_no_go_review"
    go_requires_all_contracts_ready: bool = True
    no_go_on_any_boundary_violation: bool = True
    human_go_required: bool = True


@dataclass(frozen=True)
class ControlledAbortReviewFinding(_ReviewFinding):
    name: str = "controlled_abort_review"
    abort_on_secret_read: bool = True
    abort_on_network_request: bool = True
    abort_on_order_position_or_account: bool = True
    abort_on_go_no_go_failure: bool = True


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewScore:
    overall_score: int
    controlled_execution_preparation_score: int
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
    go_no_go_score: int
    abort_score: int


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewInput:
    paper_broker_read_only_connection_dry_run_controlled_execution_preparation: Any = None
    paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate: Any = None
    paper_broker_read_only_connection_dry_run_controlled_execution_plan: Any = None
    paper_broker_read_only_connection_dry_run_execution_final_safety_gate: Any = None
    paper_broker_read_only_connection_dry_run_execution_final_plan: Any = None
    paper_broker_read_only_connection_dry_run_execution_preparation_review: Any = None
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
    controlled_execution_preparation_approved: bool | None = None
    controlled_runtime_contract_review_verified: bool | None = None
    controlled_sequence_contract_review_verified: bool | None = None
    controlled_precondition_contract_review_verified: bool | None = None
    controlled_credential_reference_review_verified: bool | None = None
    controlled_no_secret_read_guard_review_verified: bool | None = None
    controlled_network_block_guard_review_verified: bool | None = None
    controlled_http_websocket_socket_block_guard_review_verified: bool | None = None
    controlled_account_read_only_review_verified: bool | None = None
    controlled_market_data_read_only_review_verified: bool | None = None
    controlled_order_blocking_review_verified: bool | None = None
    controlled_position_mutation_block_review_verified: bool | None = None
    controlled_observability_review_verified: bool | None = None
    controlled_journal_review_verified: bool | None = None
    controlled_human_approval_review_verified: bool | None = None
    controlled_stop_conditions_review_verified: bool | None = None
    controlled_success_failure_review_verified: bool | None = None
    controlled_audit_review_verified: bool | None = None
    controlled_go_no_go_review_verified: bool | None = None
    controlled_abort_review_verified: bool | None = None
    paper_broker_read_only_connection_dry_run_controlled_execution_final_plan_requested: bool | None = False
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
    controlled_execution_preparation_score: int | None = None
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
    go_no_go_score: int | None = None
    abort_score: int | None = None


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewResult:
    state: PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewState
    decision: PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewDecision
    review_score: int
    score_breakdown: PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewScore
    risks: tuple[Risk, ...] = ()
    recommendations: tuple[PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRecommendation, ...] = ()
    controlled_execution_runtime_contract_review: ControlledExecutionRuntimeContractReviewFinding = field(default_factory=ControlledExecutionRuntimeContractReviewFinding)
    controlled_execution_sequence_contract_review: ControlledExecutionSequenceContractReviewFinding = field(default_factory=ControlledExecutionSequenceContractReviewFinding)
    controlled_execution_precondition_contract_review: ControlledExecutionPreconditionContractReviewFinding = field(default_factory=ControlledExecutionPreconditionContractReviewFinding)
    controlled_credentials_reference_review: ControlledCredentialsReferenceReviewFinding = field(default_factory=ControlledCredentialsReferenceReviewFinding)
    controlled_no_secret_read_guard_review: ControlledNoSecretReadGuardReviewFinding = field(default_factory=ControlledNoSecretReadGuardReviewFinding)
    controlled_network_block_guard_review: ControlledNetworkBlockGuardReviewFinding = field(default_factory=ControlledNetworkBlockGuardReviewFinding)
    controlled_http_websocket_socket_block_guard_review: ControlledNetworkBlockGuardReviewFinding = field(default_factory=lambda: ControlledNetworkBlockGuardReviewFinding(name="controlled_http_websocket_socket_block_guard_review"))
    controlled_account_read_only_review: ControlledAccountReadOnlyReviewFinding = field(default_factory=ControlledAccountReadOnlyReviewFinding)
    controlled_market_data_read_only_review: ControlledMarketDataReadOnlyReviewFinding = field(default_factory=ControlledMarketDataReadOnlyReviewFinding)
    controlled_order_blocking_review: ControlledOrderBlockingReviewFinding = field(default_factory=ControlledOrderBlockingReviewFinding)
    controlled_position_mutation_block_review: ControlledPositionMutationBlockReviewFinding = field(default_factory=ControlledPositionMutationBlockReviewFinding)
    controlled_observability_review: ControlledObservabilityReviewFinding = field(default_factory=ControlledObservabilityReviewFinding)
    controlled_journal_review: ControlledJournalReviewFinding = field(default_factory=ControlledJournalReviewFinding)
    controlled_human_approval_review: ControlledHumanApprovalReviewFinding = field(default_factory=ControlledHumanApprovalReviewFinding)
    controlled_stop_conditions_review: ControlledStopConditionReviewFinding = field(default_factory=ControlledStopConditionReviewFinding)
    controlled_success_failure_review: ControlledSuccessFailureReviewFinding = field(default_factory=ControlledSuccessFailureReviewFinding)
    controlled_audit_review: ControlledAuditReviewFinding = field(default_factory=ControlledAuditReviewFinding)
    controlled_go_no_go_review: ControlledGoNoGoReviewFinding = field(default_factory=ControlledGoNoGoReviewFinding)
    controlled_abort_review: ControlledAbortReviewFinding = field(default_factory=ControlledAbortReviewFinding)
    offline_only: bool = True
    summary: str = ""
