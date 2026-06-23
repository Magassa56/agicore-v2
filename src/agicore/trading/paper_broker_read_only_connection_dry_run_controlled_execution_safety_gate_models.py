"""Models for AGIcore Paper Broker Read-Only Connection Dry Run Controlled Execution Safety Gate."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateState(StrEnum):
    NOT_READY = "NOT_READY"
    CONTROLLED_EXECUTION_SAFETY_GATE_INPUT_INVALID = "CONTROLLED_EXECUTION_SAFETY_GATE_INPUT_INVALID"
    CONTROLLED_EXECUTION_SAFETY_GATE_BLOCKED = "CONTROLLED_EXECUTION_SAFETY_GATE_BLOCKED"
    CONTROLLED_EXECUTION_SAFETY_GATE_COMPLETED_WITH_WARNINGS = "CONTROLLED_EXECUTION_SAFETY_GATE_COMPLETED_WITH_WARNINGS"
    CONTROLLED_EXECUTION_SAFETY_GATE_COMPLETED = "CONTROLLED_EXECUTION_SAFETY_GATE_COMPLETED"
    READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION = "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION"


class PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateDecision(StrEnum):
    BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE = "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE"
    REQUIRE_CONTROLLED_EXECUTION_PLAN_FIXES = "REQUIRE_CONTROLLED_EXECUTION_PLAN_FIXES"
    REQUIRE_CONTROLLED_SCOPE_SAFETY_FIXES = "REQUIRE_CONTROLLED_SCOPE_SAFETY_FIXES"
    REQUIRE_CONTROLLED_SEQUENCE_SAFETY_FIXES = "REQUIRE_CONTROLLED_SEQUENCE_SAFETY_FIXES"
    REQUIRE_CONTROLLED_PRECONDITION_SAFETY_FIXES = "REQUIRE_CONTROLLED_PRECONDITION_SAFETY_FIXES"
    REQUIRE_CONTROLLED_CREDENTIAL_SAFETY_FIXES = "REQUIRE_CONTROLLED_CREDENTIAL_SAFETY_FIXES"
    REQUIRE_CONTROLLED_NO_SECRET_READ_FIXES = "REQUIRE_CONTROLLED_NO_SECRET_READ_FIXES"
    REQUIRE_CONTROLLED_NETWORK_BLOCK_FIXES = "REQUIRE_CONTROLLED_NETWORK_BLOCK_FIXES"
    REQUIRE_CONTROLLED_ACCOUNT_READ_ONLY_FIXES = "REQUIRE_CONTROLLED_ACCOUNT_READ_ONLY_FIXES"
    REQUIRE_CONTROLLED_MARKET_DATA_READ_ONLY_FIXES = "REQUIRE_CONTROLLED_MARKET_DATA_READ_ONLY_FIXES"
    REQUIRE_CONTROLLED_ORDER_BLOCKING_FIXES = "REQUIRE_CONTROLLED_ORDER_BLOCKING_FIXES"
    REQUIRE_CONTROLLED_POSITION_MUTATION_BLOCK_FIXES = "REQUIRE_CONTROLLED_POSITION_MUTATION_BLOCK_FIXES"
    REQUIRE_CONTROLLED_HUMAN_APPROVAL_FIXES = "REQUIRE_CONTROLLED_HUMAN_APPROVAL_FIXES"
    REQUIRE_CONTROLLED_STOP_CONDITION_FIXES = "REQUIRE_CONTROLLED_STOP_CONDITION_FIXES"
    REQUIRE_CONTROLLED_AUDIT_FIXES = "REQUIRE_CONTROLLED_AUDIT_FIXES"
    REQUIRE_CONTROLLED_GO_NO_GO_FIXES = "REQUIRE_CONTROLLED_GO_NO_GO_FIXES"
    REQUIRE_CONTROLLED_ABORT_POLICY_FIXES = "REQUIRE_CONTROLLED_ABORT_POLICY_FIXES"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE = "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE"


class PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRisk(StrEnum):
    CONTROLLED_EXECUTION_PLAN_NOT_APPROVED = "CONTROLLED_EXECUTION_PLAN_NOT_APPROVED"
    CONTROLLED_EXECUTION_SCOPE_UNSAFE = "CONTROLLED_EXECUTION_SCOPE_UNSAFE"
    CONTROLLED_EXECUTION_SEQUENCE_UNSAFE = "CONTROLLED_EXECUTION_SEQUENCE_UNSAFE"
    CONTROLLED_EXECUTION_PRECONDITION_UNSAFE = "CONTROLLED_EXECUTION_PRECONDITION_UNSAFE"
    CONTROLLED_CREDENTIAL_POLICY_UNSAFE = "CONTROLLED_CREDENTIAL_POLICY_UNSAFE"
    CONTROLLED_SECRET_READ_POLICY_UNSAFE = "CONTROLLED_SECRET_READ_POLICY_UNSAFE"
    CONTROLLED_NETWORK_NOT_BLOCKED = "CONTROLLED_NETWORK_NOT_BLOCKED"
    CONTROLLED_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED = "CONTROLLED_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED"
    CONTROLLED_ACCOUNT_READ_ONLY_UNSAFE = "CONTROLLED_ACCOUNT_READ_ONLY_UNSAFE"
    CONTROLLED_MARKET_DATA_READ_ONLY_UNSAFE = "CONTROLLED_MARKET_DATA_READ_ONLY_UNSAFE"
    CONTROLLED_ORDER_BLOCKING_UNSAFE = "CONTROLLED_ORDER_BLOCKING_UNSAFE"
    CONTROLLED_POSITION_MUTATION_BLOCK_UNSAFE = "CONTROLLED_POSITION_MUTATION_BLOCK_UNSAFE"
    CONTROLLED_OBSERVABILITY_INCOMPLETE = "CONTROLLED_OBSERVABILITY_INCOMPLETE"
    CONTROLLED_JOURNAL_INCOMPLETE = "CONTROLLED_JOURNAL_INCOMPLETE"
    CONTROLLED_HUMAN_APPROVAL_MISSING = "CONTROLLED_HUMAN_APPROVAL_MISSING"
    CONTROLLED_STOP_CONDITIONS_MISSING = "CONTROLLED_STOP_CONDITIONS_MISSING"
    CONTROLLED_SUCCESS_FAILURE_CRITERIA_UNSAFE = "CONTROLLED_SUCCESS_FAILURE_CRITERIA_UNSAFE"
    CONTROLLED_AUDIT_PLAN_MISSING = "CONTROLLED_AUDIT_PLAN_MISSING"
    CONTROLLED_GO_NO_GO_POLICY_MISSING = "CONTROLLED_GO_NO_GO_POLICY_MISSING"
    CONTROLLED_ABORT_POLICY_MISSING = "CONTROLLED_ABORT_POLICY_MISSING"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION = "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION"


class PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRecommendation(StrEnum):
    HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION = "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION"
    APPROVE_CONTROLLED_EXECUTION_PLAN_FIRST = "APPROVE_CONTROLLED_EXECUTION_PLAN_FIRST"
    HARDEN_CONTROLLED_EXECUTION_SCOPE = "HARDEN_CONTROLLED_EXECUTION_SCOPE"
    HARDEN_CONTROLLED_EXECUTION_SEQUENCE = "HARDEN_CONTROLLED_EXECUTION_SEQUENCE"
    HARDEN_CONTROLLED_EXECUTION_PRECONDITIONS = "HARDEN_CONTROLLED_EXECUTION_PRECONDITIONS"
    HARDEN_CONTROLLED_CREDENTIALS = "HARDEN_CONTROLLED_CREDENTIALS"
    HARDEN_CONTROLLED_NO_SECRET_READ = "HARDEN_CONTROLLED_NO_SECRET_READ"
    BLOCK_CONTROLLED_NETWORK = "BLOCK_CONTROLLED_NETWORK"
    BLOCK_CONTROLLED_HTTP_WEBSOCKET_SOCKET = "BLOCK_CONTROLLED_HTTP_WEBSOCKET_SOCKET"
    HARDEN_CONTROLLED_ACCOUNT_READ_ONLY = "HARDEN_CONTROLLED_ACCOUNT_READ_ONLY"
    HARDEN_CONTROLLED_MARKET_DATA_READ_ONLY = "HARDEN_CONTROLLED_MARKET_DATA_READ_ONLY"
    HARDEN_CONTROLLED_ORDER_BLOCKING = "HARDEN_CONTROLLED_ORDER_BLOCKING"
    HARDEN_CONTROLLED_POSITION_MUTATION_BLOCK = "HARDEN_CONTROLLED_POSITION_MUTATION_BLOCK"
    COMPLETE_CONTROLLED_OBSERVABILITY = "COMPLETE_CONTROLLED_OBSERVABILITY"
    COMPLETE_CONTROLLED_JOURNAL = "COMPLETE_CONTROLLED_JOURNAL"
    REQUIRE_CONTROLLED_HUMAN_APPROVAL = "REQUIRE_CONTROLLED_HUMAN_APPROVAL"
    DEFINE_CONTROLLED_STOP_CONDITIONS = "DEFINE_CONTROLLED_STOP_CONDITIONS"
    HARDEN_CONTROLLED_SUCCESS_FAILURE_CRITERIA = "HARDEN_CONTROLLED_SUCCESS_FAILURE_CRITERIA"
    DEFINE_CONTROLLED_AUDIT_PLAN = "DEFINE_CONTROLLED_AUDIT_PLAN"
    DEFINE_CONTROLLED_GO_NO_GO_POLICY = "DEFINE_CONTROLLED_GO_NO_GO_POLICY"
    DEFINE_CONTROLLED_ABORT_POLICY = "DEFINE_CONTROLLED_ABORT_POLICY"
    RESTORE_OFFLINE_BOUNDARIES = "RESTORE_OFFLINE_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION = "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION"
    RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE_SUITE = "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE_SUITE"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION = "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION"


@dataclass(frozen=True)
class ControlledSafetyFinding:
    score: int = 0
    passed: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ControlledExecutionScopeSafetyFinding(ControlledSafetyFinding):
    offline_only: bool = False
    sandbox_only: bool = False
    safety_gate_only: bool = False
    no_dry_run_executed: bool = False
    prohibited_actions_confirmed: bool = False


@dataclass(frozen=True)
class ControlledExecutionSequenceSafetyFinding(ControlledSafetyFinding):
    sequence_steps_defined: bool = False
    dry_run_not_executed: bool = False
    connection_not_executed: bool = False
    fail_closed: bool = False


@dataclass(frozen=True)
class ControlledExecutionPreconditionSafetyFinding(ControlledSafetyFinding):
    controlled_plan_required: bool = False
    safety_gate_required: bool = False
    human_approval_required: bool = False
    stop_conditions_required: bool = False


@dataclass(frozen=True)
class ControlledCredentialsSafetyFinding(ControlledSafetyFinding):
    reference_only: bool = False
    no_secret_values: bool = False
    no_api_key_read: bool = False
    no_env_var_read: bool = False


@dataclass(frozen=True)
class ControlledNetworkBlockSafetyFinding(ControlledSafetyFinding):
    network_execution_blocked: bool = False
    http_blocked: bool = False
    websocket_blocked: bool = False
    socket_blocked: bool = False
    external_api_blocked: bool = False


@dataclass(frozen=True)
class ControlledAccountReadOnlySafetyFinding(ControlledSafetyFinding):
    active_account_access_blocked: bool = False
    account_mutations_blocked: bool = False
    schema_only_account_review: bool = False


@dataclass(frozen=True)
class ControlledMarketDataReadOnlySafetyFinding(ControlledSafetyFinding):
    read_only_market_data_only: bool = False
    live_subscription_blocked: bool = False
    network_request_blocked: bool = False
    schema_or_synthetic_only: bool = False


@dataclass(frozen=True)
class ControlledOrderBlockingSafetyFinding(ControlledSafetyFinding):
    order_execution_blocked: bool = False
    real_order_blocked: bool = False
    cancel_replace_blocked: bool = False


@dataclass(frozen=True)
class ControlledPositionMutationBlockSafetyFinding(ControlledSafetyFinding):
    position_mutation_blocked: bool = False
    position_request_absent: bool = False
    close_modify_blocked: bool = False


@dataclass(frozen=True)
class ControlledObservabilitySafetyFinding(ControlledSafetyFinding):
    offline_events_defined: bool = False
    connection_attempt_logging_disabled: bool = False
    sensitive_values_redacted: bool = False


@dataclass(frozen=True)
class ControlledJournalSafetyFinding(ControlledSafetyFinding):
    offline_journal_required: bool = False
    sensitive_values_redacted: bool = False
    no_secret_material_logged: bool = False


@dataclass(frozen=True)
class ControlledHumanApprovalSafetyFinding(ControlledSafetyFinding):
    human_approval_required: bool = False
    approval_before_safety_gate: bool = False
    controlled_plan_evidence_required: bool = False


@dataclass(frozen=True)
class ControlledStopConditionSafetyFinding(ControlledSafetyFinding):
    stop_on_secret_read: bool = False
    stop_on_network_request: bool = False
    stop_on_order_or_position_request: bool = False
    stop_on_account_access_request: bool = False


@dataclass(frozen=True)
class ControlledSuccessFailureSafetyFinding(ControlledSafetyFinding):
    success_criteria_defined: bool = False
    failure_criteria_defined: bool = False
    requires_no_real_connection: bool = False
    failure_on_boundary_violation: bool = False


@dataclass(frozen=True)
class ControlledAuditSafetyFinding(ControlledSafetyFinding):
    audit_events_defined: bool = False
    offline_evidence_required: bool = False
    controlled_safety_gate_trace_required: bool = False


@dataclass(frozen=True)
class ControlledGoNoGoSafetyFinding(ControlledSafetyFinding):
    go_requires_all_sections_ready: bool = False
    no_go_on_any_boundary_violation: bool = False
    human_go_required: bool = False


@dataclass(frozen=True)
class ControlledAbortPolicySafetyFinding(ControlledSafetyFinding):
    abort_on_secret_read: bool = False
    abort_on_network_request: bool = False
    abort_on_order_position_or_account: bool = False
    abort_on_go_no_go_failure: bool = False


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateScore:
    overall_score: int
    controlled_plan_score: int
    scope_score: int
    sequence_score: int
    precondition_score: int
    credentials_score: int
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
    success_failure_criteria_score: int
    audit_plan_score: int
    go_no_go_score: int
    abort_policy_score: int


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateInput:
    paper_broker_read_only_connection_dry_run_controlled_execution_plan: Any = None
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
    controlled_execution_plan_approved: bool | None = None
    controlled_execution_scope_safety_verified: bool | None = None
    controlled_execution_sequence_safety_verified: bool | None = None
    controlled_execution_precondition_safety_verified: bool | None = None
    controlled_credentials_reference_safety_verified: bool | None = None
    controlled_no_secret_read_safety_verified: bool | None = None
    controlled_network_block_safety_verified: bool | None = None
    controlled_http_websocket_socket_block_safety_verified: bool | None = None
    controlled_account_read_only_safety_verified: bool | None = None
    controlled_market_data_read_only_safety_verified: bool | None = None
    controlled_order_blocking_safety_verified: bool | None = None
    controlled_position_mutation_block_safety_verified: bool | None = None
    controlled_observability_safety_verified: bool | None = None
    controlled_journal_safety_verified: bool | None = None
    controlled_human_approval_safety_verified: bool | None = None
    controlled_stop_conditions_safety_verified: bool | None = None
    controlled_success_failure_criteria_safety_verified: bool | None = None
    controlled_audit_plan_safety_verified: bool | None = None
    controlled_go_no_go_policy_safety_verified: bool | None = None
    controlled_abort_policy_safety_verified: bool | None = None
    paper_broker_read_only_connection_dry_run_controlled_execution_preparation_requested: bool | None = False
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
    external_api_requested: bool | None = False
    dry_run_requested: bool | None = False
    dry_run_executed: bool | None = False
    controlled_plan_score: int | None = None
    scope_score: int | None = None
    sequence_score: int | None = None
    precondition_score: int | None = None
    credentials_score: int | None = None
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
    success_failure_criteria_score: int | None = None
    audit_plan_score: int | None = None
    go_no_go_score: int | None = None
    abort_policy_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateResult:
    state: PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateState
    decision: PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateDecision
    safety_gate_score: int
    score_breakdown: PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateScore
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRisk, ...] = ()
    recommendations: tuple[PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRecommendation, ...] = ()
    scope_safety: ControlledExecutionScopeSafetyFinding = field(default_factory=ControlledExecutionScopeSafetyFinding)
    sequence_safety: ControlledExecutionSequenceSafetyFinding = field(default_factory=ControlledExecutionSequenceSafetyFinding)
    precondition_safety: ControlledExecutionPreconditionSafetyFinding = field(default_factory=ControlledExecutionPreconditionSafetyFinding)
    credentials_reference_safety: ControlledCredentialsSafetyFinding = field(default_factory=ControlledCredentialsSafetyFinding)
    no_secret_read_safety: ControlledCredentialsSafetyFinding = field(default_factory=ControlledCredentialsSafetyFinding)
    network_block_safety: ControlledNetworkBlockSafetyFinding = field(default_factory=ControlledNetworkBlockSafetyFinding)
    http_websocket_socket_block_safety: ControlledNetworkBlockSafetyFinding = field(default_factory=ControlledNetworkBlockSafetyFinding)
    account_read_only_safety: ControlledAccountReadOnlySafetyFinding = field(default_factory=ControlledAccountReadOnlySafetyFinding)
    market_data_read_only_safety: ControlledMarketDataReadOnlySafetyFinding = field(default_factory=ControlledMarketDataReadOnlySafetyFinding)
    order_blocking_safety: ControlledOrderBlockingSafetyFinding = field(default_factory=ControlledOrderBlockingSafetyFinding)
    position_mutation_block_safety: ControlledPositionMutationBlockSafetyFinding = field(default_factory=ControlledPositionMutationBlockSafetyFinding)
    observability_safety: ControlledObservabilitySafetyFinding = field(default_factory=ControlledObservabilitySafetyFinding)
    journal_safety: ControlledJournalSafetyFinding = field(default_factory=ControlledJournalSafetyFinding)
    human_approval_safety: ControlledHumanApprovalSafetyFinding = field(default_factory=ControlledHumanApprovalSafetyFinding)
    stop_conditions_safety: ControlledStopConditionSafetyFinding = field(default_factory=ControlledStopConditionSafetyFinding)
    success_failure_criteria_safety: ControlledSuccessFailureSafetyFinding = field(default_factory=ControlledSuccessFailureSafetyFinding)
    audit_plan_safety: ControlledAuditSafetyFinding = field(default_factory=ControlledAuditSafetyFinding)
    go_no_go_policy_safety: ControlledGoNoGoSafetyFinding = field(default_factory=ControlledGoNoGoSafetyFinding)
    abort_policy_safety: ControlledAbortPolicySafetyFinding = field(default_factory=ControlledAbortPolicySafetyFinding)
    offline_only: bool = True
    summary: str = ""
