"""Models for AGIcore Paper Broker Read-Only Connection Dry Run Controlled Execution Preparation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationState(StrEnum):
    NOT_READY = "NOT_READY"
    CONTROLLED_EXECUTION_PREPARATION_INPUT_INVALID = "CONTROLLED_EXECUTION_PREPARATION_INPUT_INVALID"
    CONTROLLED_EXECUTION_PREPARATION_BLOCKED = "CONTROLLED_EXECUTION_PREPARATION_BLOCKED"
    CONTROLLED_EXECUTION_PREPARATION_COMPLETED_WITH_WARNINGS = "CONTROLLED_EXECUTION_PREPARATION_COMPLETED_WITH_WARNINGS"
    CONTROLLED_EXECUTION_PREPARATION_COMPLETED = "CONTROLLED_EXECUTION_PREPARATION_COMPLETED"
    READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW = "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW"


class PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationDecision(StrEnum):
    BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION = "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION"
    REQUIRE_CONTROLLED_EXECUTION_SAFETY_GATE_FIXES = "REQUIRE_CONTROLLED_EXECUTION_SAFETY_GATE_FIXES"
    REQUIRE_CONTROLLED_RUNTIME_CONTRACT_FIXES = "REQUIRE_CONTROLLED_RUNTIME_CONTRACT_FIXES"
    REQUIRE_CONTROLLED_SEQUENCE_CONTRACT_FIXES = "REQUIRE_CONTROLLED_SEQUENCE_CONTRACT_FIXES"
    REQUIRE_CONTROLLED_PRECONDITION_CONTRACT_FIXES = "REQUIRE_CONTROLLED_PRECONDITION_CONTRACT_FIXES"
    REQUIRE_CONTROLLED_CREDENTIAL_REFERENCE_FIXES = "REQUIRE_CONTROLLED_CREDENTIAL_REFERENCE_FIXES"
    REQUIRE_CONTROLLED_NO_SECRET_READ_GUARD_FIXES = "REQUIRE_CONTROLLED_NO_SECRET_READ_GUARD_FIXES"
    REQUIRE_CONTROLLED_NETWORK_BLOCK_GUARD_FIXES = "REQUIRE_CONTROLLED_NETWORK_BLOCK_GUARD_FIXES"
    REQUIRE_CONTROLLED_ACCOUNT_READ_ONLY_FIXES = "REQUIRE_CONTROLLED_ACCOUNT_READ_ONLY_FIXES"
    REQUIRE_CONTROLLED_MARKET_DATA_READ_ONLY_FIXES = "REQUIRE_CONTROLLED_MARKET_DATA_READ_ONLY_FIXES"
    REQUIRE_CONTROLLED_ORDER_BLOCKING_FIXES = "REQUIRE_CONTROLLED_ORDER_BLOCKING_FIXES"
    REQUIRE_CONTROLLED_POSITION_MUTATION_BLOCK_FIXES = "REQUIRE_CONTROLLED_POSITION_MUTATION_BLOCK_FIXES"
    REQUIRE_CONTROLLED_OBSERVABILITY_FIXES = "REQUIRE_CONTROLLED_OBSERVABILITY_FIXES"
    REQUIRE_CONTROLLED_JOURNAL_FIXES = "REQUIRE_CONTROLLED_JOURNAL_FIXES"
    REQUIRE_CONTROLLED_HUMAN_APPROVAL_FIXES = "REQUIRE_CONTROLLED_HUMAN_APPROVAL_FIXES"
    REQUIRE_CONTROLLED_STOP_CONDITION_FIXES = "REQUIRE_CONTROLLED_STOP_CONDITION_FIXES"
    REQUIRE_CONTROLLED_SUCCESS_FAILURE_FIXES = "REQUIRE_CONTROLLED_SUCCESS_FAILURE_FIXES"
    REQUIRE_CONTROLLED_AUDIT_FIXES = "REQUIRE_CONTROLLED_AUDIT_FIXES"
    REQUIRE_CONTROLLED_GO_NO_GO_FIXES = "REQUIRE_CONTROLLED_GO_NO_GO_FIXES"
    REQUIRE_CONTROLLED_ABORT_FIXES = "REQUIRE_CONTROLLED_ABORT_FIXES"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION = "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION"


class PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRisk(StrEnum):
    CONTROLLED_EXECUTION_SAFETY_GATE_NOT_APPROVED = "CONTROLLED_EXECUTION_SAFETY_GATE_NOT_APPROVED"
    CONTROLLED_RUNTIME_CONTRACT_MISSING = "CONTROLLED_RUNTIME_CONTRACT_MISSING"
    CONTROLLED_SEQUENCE_CONTRACT_MISSING = "CONTROLLED_SEQUENCE_CONTRACT_MISSING"
    CONTROLLED_PRECONDITION_CONTRACT_MISSING = "CONTROLLED_PRECONDITION_CONTRACT_MISSING"
    CONTROLLED_CREDENTIAL_REFERENCE_UNSAFE = "CONTROLLED_CREDENTIAL_REFERENCE_UNSAFE"
    CONTROLLED_SECRET_READ_GUARD_MISSING = "CONTROLLED_SECRET_READ_GUARD_MISSING"
    CONTROLLED_NETWORK_BLOCK_GUARD_MISSING = "CONTROLLED_NETWORK_BLOCK_GUARD_MISSING"
    CONTROLLED_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_MISSING = "CONTROLLED_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_MISSING"
    CONTROLLED_ACCOUNT_READ_ONLY_UNSAFE = "CONTROLLED_ACCOUNT_READ_ONLY_UNSAFE"
    CONTROLLED_MARKET_DATA_READ_ONLY_UNSAFE = "CONTROLLED_MARKET_DATA_READ_ONLY_UNSAFE"
    CONTROLLED_ORDER_BLOCKING_UNSAFE = "CONTROLLED_ORDER_BLOCKING_UNSAFE"
    CONTROLLED_POSITION_MUTATION_BLOCK_UNSAFE = "CONTROLLED_POSITION_MUTATION_BLOCK_UNSAFE"
    CONTROLLED_OBSERVABILITY_INCOMPLETE = "CONTROLLED_OBSERVABILITY_INCOMPLETE"
    CONTROLLED_JOURNAL_INCOMPLETE = "CONTROLLED_JOURNAL_INCOMPLETE"
    CONTROLLED_HUMAN_APPROVAL_MISSING = "CONTROLLED_HUMAN_APPROVAL_MISSING"
    CONTROLLED_STOP_CONDITIONS_MISSING = "CONTROLLED_STOP_CONDITIONS_MISSING"
    CONTROLLED_SUCCESS_FAILURE_CONTRACT_MISSING = "CONTROLLED_SUCCESS_FAILURE_CONTRACT_MISSING"
    CONTROLLED_AUDIT_CONTRACT_MISSING = "CONTROLLED_AUDIT_CONTRACT_MISSING"
    CONTROLLED_GO_NO_GO_CONTRACT_MISSING = "CONTROLLED_GO_NO_GO_CONTRACT_MISSING"
    CONTROLLED_ABORT_CONTRACT_MISSING = "CONTROLLED_ABORT_CONTRACT_MISSING"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW = "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW"


class PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRecommendation(StrEnum):
    HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW = "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW"
    APPROVE_CONTROLLED_EXECUTION_SAFETY_GATE_FIRST = "APPROVE_CONTROLLED_EXECUTION_SAFETY_GATE_FIRST"
    PREPARE_CONTROLLED_RUNTIME_CONTRACT = "PREPARE_CONTROLLED_RUNTIME_CONTRACT"
    PREPARE_CONTROLLED_SEQUENCE_CONTRACT = "PREPARE_CONTROLLED_SEQUENCE_CONTRACT"
    PREPARE_CONTROLLED_PRECONDITION_CONTRACT = "PREPARE_CONTROLLED_PRECONDITION_CONTRACT"
    HARDEN_CONTROLLED_CREDENTIAL_REFERENCE = "HARDEN_CONTROLLED_CREDENTIAL_REFERENCE"
    INSTALL_CONTROLLED_NO_SECRET_READ_GUARD = "INSTALL_CONTROLLED_NO_SECRET_READ_GUARD"
    INSTALL_CONTROLLED_NETWORK_BLOCK_GUARD = "INSTALL_CONTROLLED_NETWORK_BLOCK_GUARD"
    INSTALL_CONTROLLED_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD = "INSTALL_CONTROLLED_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD"
    HARDEN_CONTROLLED_ACCOUNT_READ_ONLY = "HARDEN_CONTROLLED_ACCOUNT_READ_ONLY"
    HARDEN_CONTROLLED_MARKET_DATA_READ_ONLY = "HARDEN_CONTROLLED_MARKET_DATA_READ_ONLY"
    HARDEN_CONTROLLED_ORDER_BLOCKING = "HARDEN_CONTROLLED_ORDER_BLOCKING"
    HARDEN_CONTROLLED_POSITION_MUTATION_BLOCK = "HARDEN_CONTROLLED_POSITION_MUTATION_BLOCK"
    COMPLETE_CONTROLLED_OBSERVABILITY = "COMPLETE_CONTROLLED_OBSERVABILITY"
    COMPLETE_CONTROLLED_JOURNAL = "COMPLETE_CONTROLLED_JOURNAL"
    REQUIRE_CONTROLLED_HUMAN_APPROVAL = "REQUIRE_CONTROLLED_HUMAN_APPROVAL"
    DEFINE_CONTROLLED_STOP_CONDITIONS = "DEFINE_CONTROLLED_STOP_CONDITIONS"
    PREPARE_CONTROLLED_SUCCESS_FAILURE_CONTRACT = "PREPARE_CONTROLLED_SUCCESS_FAILURE_CONTRACT"
    PREPARE_CONTROLLED_AUDIT_CONTRACT = "PREPARE_CONTROLLED_AUDIT_CONTRACT"
    PREPARE_CONTROLLED_GO_NO_GO_CONTRACT = "PREPARE_CONTROLLED_GO_NO_GO_CONTRACT"
    PREPARE_CONTROLLED_ABORT_CONTRACT = "PREPARE_CONTROLLED_ABORT_CONTRACT"
    RESTORE_OFFLINE_BOUNDARIES = "RESTORE_OFFLINE_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW = "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW"
    RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_SUITE = "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_SUITE"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW = "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW"


Risk = PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRisk


@dataclass(frozen=True)
class ControlledExecutionRuntimeContract:
    name: str = "controlled_execution_runtime_contract"
    score: int = 0
    defined: bool = False
    preparation_only: bool = True
    read_only_only: bool = True
    dry_run_execution_disabled: bool = True
    allowed_actions: tuple[str, ...] = ()
    prohibited_actions: tuple[str, ...] = ()
    risks: tuple[Risk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ControlledExecutionSequenceContract:
    name: str = "controlled_execution_sequence_contract"
    score: int = 0
    defined: bool = False
    dry_run_not_executed: bool = True
    connection_not_executed: bool = True
    sequence_steps_defined: bool = True
    network_transport_blocked: bool = True
    risks: tuple[Risk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ControlledExecutionPreconditionContract:
    name: str = "controlled_execution_precondition_contract"
    score: int = 0
    defined: bool = False
    safety_gate_required: bool = True
    human_approval_required: bool = True
    stop_conditions_required: bool = True
    fail_closed: bool = True
    risks: tuple[Risk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ControlledCredentialsReferenceContract:
    name: str = "controlled_credentials_reference_contract"
    score: int = 0
    defined: bool = False
    reference_only: bool = True
    no_secret_values: bool = True
    no_api_key_read: bool = True
    no_env_var_read: bool = True
    secret_source: str = "none_in_this_phase"
    risks: tuple[Risk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ControlledNoSecretReadGuard:
    name: str = "controlled_no_secret_read_guard"
    score: int = 0
    defined: bool = False
    guard_enforced: bool = False
    no_api_key_read: bool = True
    no_env_var_read: bool = True
    no_hardcoded_secret: bool = True
    risks: tuple[Risk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ControlledNetworkBlockGuard:
    name: str = "controlled_network_block_guard"
    score: int = 0
    defined: bool = False
    network_execution_blocked: bool = True
    http_blocked: bool = True
    websocket_blocked: bool = True
    socket_blocked: bool = True
    external_api_blocked: bool = True
    risks: tuple[Risk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ControlledAccountReadOnlyContract:
    name: str = "controlled_account_read_only_contract"
    score: int = 0
    defined: bool = False
    active_account_access_blocked: bool = True
    account_mutations_blocked: bool = True
    schema_only_account_review: bool = True
    risks: tuple[Risk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ControlledMarketDataReadOnlyContract:
    name: str = "controlled_market_data_read_only_contract"
    score: int = 0
    defined: bool = False
    read_only_market_data_only: bool = True
    live_subscription_blocked: bool = True
    network_request_blocked: bool = True
    schema_or_synthetic_only: bool = True
    risks: tuple[Risk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ControlledOrderBlockingContract:
    name: str = "controlled_order_blocking_contract"
    score: int = 0
    defined: bool = False
    order_execution_blocked: bool = True
    real_order_blocked: bool = True
    cancel_replace_blocked: bool = True
    risks: tuple[Risk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ControlledPositionMutationBlockContract:
    name: str = "controlled_position_mutation_block_contract"
    score: int = 0
    defined: bool = False
    position_mutation_blocked: bool = True
    position_request_absent: bool = True
    close_modify_blocked: bool = True
    risks: tuple[Risk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ControlledObservabilityContract:
    name: str = "controlled_observability_contract"
    score: int = 0
    defined: bool = False
    offline_events_defined: bool = True
    connection_attempt_logging_disabled: bool = True
    sensitive_values_redacted: bool = True
    risks: tuple[Risk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ControlledJournalContract:
    name: str = "controlled_journal_contract"
    score: int = 0
    defined: bool = False
    offline_journal_required: bool = True
    sensitive_values_redacted: bool = True
    no_secret_material_logged: bool = True
    risks: tuple[Risk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ControlledHumanApprovalContract:
    name: str = "controlled_human_approval_contract"
    score: int = 0
    defined: bool = False
    human_approval_required: bool = True
    approval_before_review: bool = True
    safety_gate_evidence_required: bool = True
    risks: tuple[Risk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ControlledStopConditionContract:
    name: str = "controlled_stop_conditions_contract"
    score: int = 0
    defined: bool = False
    stop_on_secret_read: bool = True
    stop_on_network_request: bool = True
    stop_on_order_or_position_request: bool = True
    stop_on_account_access_request: bool = True
    risks: tuple[Risk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ControlledSuccessFailureContract:
    name: str = "controlled_success_failure_contract"
    score: int = 0
    defined: bool = False
    success_requires_no_real_connection: bool = True
    success_requires_all_guards_verified: bool = True
    failure_on_secret_network_order_position_or_account: bool = True
    risks: tuple[Risk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ControlledAuditContract:
    name: str = "controlled_audit_contract"
    score: int = 0
    defined: bool = False
    audit_events_defined: bool = True
    offline_evidence_required: bool = True
    preparation_review_trace_required: bool = True
    risks: tuple[Risk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ControlledGoNoGoContract:
    name: str = "controlled_go_no_go_contract"
    score: int = 0
    defined: bool = False
    go_requires_all_contracts_ready: bool = True
    no_go_on_any_boundary_violation: bool = True
    human_go_required: bool = True
    risks: tuple[Risk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ControlledAbortContract:
    name: str = "controlled_abort_contract"
    score: int = 0
    defined: bool = False
    abort_on_secret_read: bool = True
    abort_on_network_request: bool = True
    abort_on_order_position_or_account: bool = True
    abort_on_go_no_go_failure: bool = True
    risks: tuple[Risk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationScore:
    overall_score: int
    controlled_execution_safety_gate_score: int
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
class PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationInput:
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
    controlled_execution_safety_gate_approved: bool | None = None
    controlled_runtime_contract_prepared: bool | None = None
    controlled_execution_runtime_contract_prepared: bool | None = None
    controlled_sequence_contract_prepared: bool | None = None
    controlled_execution_sequence_contract_prepared: bool | None = None
    controlled_precondition_contract_prepared: bool | None = None
    controlled_execution_precondition_contract_prepared: bool | None = None
    controlled_credentials_reference_contract_prepared: bool | None = None
    controlled_credentials_reference_only: bool | None = None
    controlled_no_secret_read_guard_prepared: bool | None = None
    controlled_secret_read_guard_enforced: bool | None = None
    controlled_network_block_guard_prepared: bool | None = None
    controlled_network_blocked: bool | None = None
    controlled_http_websocket_socket_block_guard_prepared: bool | None = None
    controlled_http_transport_blocked: bool | None = None
    controlled_websocket_transport_blocked: bool | None = None
    controlled_socket_transport_blocked: bool | None = None
    controlled_external_api_blocked: bool | None = None
    controlled_account_read_only_contract_prepared: bool | None = None
    controlled_account_active_access_blocked: bool | None = None
    controlled_account_mutations_blocked: bool | None = None
    controlled_market_data_read_only_contract_prepared: bool | None = None
    controlled_market_data_live_subscription_blocked: bool | None = None
    controlled_market_data_network_request_blocked: bool | None = None
    controlled_order_blocking_contract_prepared: bool | None = None
    controlled_order_execution_blocked: bool | None = None
    controlled_cancel_replace_blocked: bool | None = None
    controlled_position_mutation_block_contract_prepared: bool | None = None
    controlled_position_mutation_blocked: bool | None = None
    controlled_observability_contract_prepared: bool | None = None
    controlled_journal_contract_prepared: bool | None = None
    controlled_human_approval_contract_prepared: bool | None = None
    controlled_human_approval_required: bool | None = None
    controlled_stop_conditions_contract_prepared: bool | None = None
    controlled_success_failure_contract_prepared: bool | None = None
    controlled_audit_contract_prepared: bool | None = None
    controlled_go_no_go_contract_prepared: bool | None = None
    controlled_abort_contract_prepared: bool | None = None
    paper_broker_read_only_connection_dry_run_controlled_execution_preparation_review_requested: bool | None = False
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
    controlled_execution_safety_gate_score: int | None = None
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
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationResult:
    state: PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationState
    decision: PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationDecision
    preparation_score: int
    score_breakdown: PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationScore
    risks: tuple[Risk, ...] = ()
    recommendations: tuple[PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRecommendation, ...] = ()
    controlled_execution_runtime_contract: ControlledExecutionRuntimeContract = field(default_factory=ControlledExecutionRuntimeContract)
    controlled_execution_sequence_contract: ControlledExecutionSequenceContract = field(default_factory=ControlledExecutionSequenceContract)
    controlled_execution_precondition_contract: ControlledExecutionPreconditionContract = field(default_factory=ControlledExecutionPreconditionContract)
    controlled_credentials_reference_contract: ControlledCredentialsReferenceContract = field(default_factory=ControlledCredentialsReferenceContract)
    controlled_no_secret_read_guard: ControlledNoSecretReadGuard = field(default_factory=ControlledNoSecretReadGuard)
    controlled_network_block_guard: ControlledNetworkBlockGuard = field(default_factory=ControlledNetworkBlockGuard)
    controlled_http_websocket_socket_block_guard: ControlledNetworkBlockGuard = field(default_factory=lambda: ControlledNetworkBlockGuard(name="controlled_http_websocket_socket_block_guard"))
    controlled_account_read_only_contract: ControlledAccountReadOnlyContract = field(default_factory=ControlledAccountReadOnlyContract)
    controlled_market_data_read_only_contract: ControlledMarketDataReadOnlyContract = field(default_factory=ControlledMarketDataReadOnlyContract)
    controlled_order_blocking_contract: ControlledOrderBlockingContract = field(default_factory=ControlledOrderBlockingContract)
    controlled_position_mutation_block_contract: ControlledPositionMutationBlockContract = field(default_factory=ControlledPositionMutationBlockContract)
    controlled_observability_contract: ControlledObservabilityContract = field(default_factory=ControlledObservabilityContract)
    controlled_journal_contract: ControlledJournalContract = field(default_factory=ControlledJournalContract)
    controlled_human_approval_contract: ControlledHumanApprovalContract = field(default_factory=ControlledHumanApprovalContract)
    controlled_stop_conditions_contract: ControlledStopConditionContract = field(default_factory=ControlledStopConditionContract)
    controlled_success_failure_contract: ControlledSuccessFailureContract = field(default_factory=ControlledSuccessFailureContract)
    controlled_audit_contract: ControlledAuditContract = field(default_factory=ControlledAuditContract)
    controlled_go_no_go_contract: ControlledGoNoGoContract = field(default_factory=ControlledGoNoGoContract)
    controlled_abort_contract: ControlledAbortContract = field(default_factory=ControlledAbortContract)
    offline_only: bool = True
    summary: str = ""