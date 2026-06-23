"""Models for AGIcore Paper Broker Read-Only Connection Dry Run Execution Final Safety Gate."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerReadOnlyConnectionDryRunExecutionFinalSafetyGateState(StrEnum):
    NOT_READY = "NOT_READY"
    FINAL_SAFETY_GATE_INPUT_INVALID = "FINAL_SAFETY_GATE_INPUT_INVALID"
    FINAL_SAFETY_GATE_BLOCKED = "FINAL_SAFETY_GATE_BLOCKED"
    FINAL_SAFETY_GATE_COMPLETED_WITH_WARNINGS = "FINAL_SAFETY_GATE_COMPLETED_WITH_WARNINGS"
    FINAL_SAFETY_GATE_COMPLETED = "FINAL_SAFETY_GATE_COMPLETED"
    READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PLAN = "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PLAN"


class PaperBrokerReadOnlyConnectionDryRunExecutionFinalSafetyGateDecision(StrEnum):
    BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_SAFETY_GATE = "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_SAFETY_GATE"
    REQUIRE_FINAL_PLAN_FIXES = "REQUIRE_FINAL_PLAN_FIXES"
    REQUIRE_FINAL_SCOPE_SAFETY_FIXES = "REQUIRE_FINAL_SCOPE_SAFETY_FIXES"
    REQUIRE_FINAL_SEQUENCE_SAFETY_FIXES = "REQUIRE_FINAL_SEQUENCE_SAFETY_FIXES"
    REQUIRE_FINAL_PRECONDITION_SAFETY_FIXES = "REQUIRE_FINAL_PRECONDITION_SAFETY_FIXES"
    REQUIRE_FINAL_CREDENTIAL_SAFETY_FIXES = "REQUIRE_FINAL_CREDENTIAL_SAFETY_FIXES"
    REQUIRE_FINAL_NETWORK_BLOCK_FIXES = "REQUIRE_FINAL_NETWORK_BLOCK_FIXES"
    REQUIRE_FINAL_ACCOUNT_READ_ONLY_FIXES = "REQUIRE_FINAL_ACCOUNT_READ_ONLY_FIXES"
    REQUIRE_FINAL_MARKET_DATA_READ_ONLY_FIXES = "REQUIRE_FINAL_MARKET_DATA_READ_ONLY_FIXES"
    REQUIRE_FINAL_ORDER_BLOCKING_FIXES = "REQUIRE_FINAL_ORDER_BLOCKING_FIXES"
    REQUIRE_FINAL_POSITION_MUTATION_BLOCK_FIXES = "REQUIRE_FINAL_POSITION_MUTATION_BLOCK_FIXES"
    REQUIRE_FINAL_HUMAN_APPROVAL_FIXES = "REQUIRE_FINAL_HUMAN_APPROVAL_FIXES"
    REQUIRE_FINAL_STOP_CONDITION_FIXES = "REQUIRE_FINAL_STOP_CONDITION_FIXES"
    REQUIRE_FINAL_AUDIT_FIXES = "REQUIRE_FINAL_AUDIT_FIXES"
    REQUIRE_FINAL_GO_NO_GO_FIXES = "REQUIRE_FINAL_GO_NO_GO_FIXES"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_SAFETY_GATE = "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_SAFETY_GATE"


class PaperBrokerReadOnlyConnectionDryRunExecutionFinalSafetyGateRisk(StrEnum):
    DRY_RUN_EXECUTION_FINAL_PLAN_NOT_APPROVED = "DRY_RUN_EXECUTION_FINAL_PLAN_NOT_APPROVED"
    FINAL_EXECUTION_SCOPE_UNSAFE = "FINAL_EXECUTION_SCOPE_UNSAFE"
    FINAL_EXECUTION_SEQUENCE_UNSAFE = "FINAL_EXECUTION_SEQUENCE_UNSAFE"
    FINAL_EXECUTION_PRECONDITION_UNSAFE = "FINAL_EXECUTION_PRECONDITION_UNSAFE"
    FINAL_CREDENTIAL_POLICY_UNSAFE = "FINAL_CREDENTIAL_POLICY_UNSAFE"
    FINAL_SECRET_READ_POLICY_UNSAFE = "FINAL_SECRET_READ_POLICY_UNSAFE"
    FINAL_NETWORK_NOT_BLOCKED = "FINAL_NETWORK_NOT_BLOCKED"
    FINAL_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED = "FINAL_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED"
    FINAL_ACCOUNT_READ_ONLY_UNSAFE = "FINAL_ACCOUNT_READ_ONLY_UNSAFE"
    FINAL_MARKET_DATA_READ_ONLY_UNSAFE = "FINAL_MARKET_DATA_READ_ONLY_UNSAFE"
    FINAL_ORDER_BLOCKING_UNSAFE = "FINAL_ORDER_BLOCKING_UNSAFE"
    FINAL_POSITION_MUTATION_BLOCK_UNSAFE = "FINAL_POSITION_MUTATION_BLOCK_UNSAFE"
    FINAL_OBSERVABILITY_INCOMPLETE = "FINAL_OBSERVABILITY_INCOMPLETE"
    FINAL_JOURNAL_INCOMPLETE = "FINAL_JOURNAL_INCOMPLETE"
    FINAL_HUMAN_APPROVAL_MISSING = "FINAL_HUMAN_APPROVAL_MISSING"
    FINAL_STOP_CONDITIONS_MISSING = "FINAL_STOP_CONDITIONS_MISSING"
    FINAL_SUCCESS_FAILURE_CRITERIA_UNSAFE = "FINAL_SUCCESS_FAILURE_CRITERIA_UNSAFE"
    FINAL_AUDIT_PLAN_MISSING = "FINAL_AUDIT_PLAN_MISSING"
    FINAL_GO_NO_GO_POLICY_MISSING = "FINAL_GO_NO_GO_POLICY_MISSING"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PLAN = "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PLAN"


class PaperBrokerReadOnlyConnectionDryRunExecutionFinalSafetyGateRecommendation(StrEnum):
    HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PLAN = "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PLAN"
    APPROVE_DRY_RUN_EXECUTION_FINAL_PLAN_FIRST = "APPROVE_DRY_RUN_EXECUTION_FINAL_PLAN_FIRST"
    HARDEN_FINAL_EXECUTION_SCOPE = "HARDEN_FINAL_EXECUTION_SCOPE"
    HARDEN_FINAL_EXECUTION_SEQUENCE = "HARDEN_FINAL_EXECUTION_SEQUENCE"
    HARDEN_FINAL_EXECUTION_PRECONDITIONS = "HARDEN_FINAL_EXECUTION_PRECONDITIONS"
    HARDEN_FINAL_CREDENTIALS = "HARDEN_FINAL_CREDENTIALS"
    HARDEN_FINAL_NO_SECRET_READ = "HARDEN_FINAL_NO_SECRET_READ"
    BLOCK_FINAL_NETWORK = "BLOCK_FINAL_NETWORK"
    BLOCK_FINAL_HTTP_WEBSOCKET_SOCKET = "BLOCK_FINAL_HTTP_WEBSOCKET_SOCKET"
    HARDEN_FINAL_ACCOUNT_READ_ONLY = "HARDEN_FINAL_ACCOUNT_READ_ONLY"
    HARDEN_FINAL_MARKET_DATA_READ_ONLY = "HARDEN_FINAL_MARKET_DATA_READ_ONLY"
    HARDEN_FINAL_ORDER_BLOCKING = "HARDEN_FINAL_ORDER_BLOCKING"
    HARDEN_FINAL_POSITION_MUTATION_BLOCK = "HARDEN_FINAL_POSITION_MUTATION_BLOCK"
    COMPLETE_FINAL_OBSERVABILITY = "COMPLETE_FINAL_OBSERVABILITY"
    COMPLETE_FINAL_JOURNAL = "COMPLETE_FINAL_JOURNAL"
    REQUIRE_FINAL_HUMAN_APPROVAL = "REQUIRE_FINAL_HUMAN_APPROVAL"
    DEFINE_FINAL_STOP_CONDITIONS = "DEFINE_FINAL_STOP_CONDITIONS"
    HARDEN_FINAL_SUCCESS_FAILURE_CRITERIA = "HARDEN_FINAL_SUCCESS_FAILURE_CRITERIA"
    DEFINE_FINAL_AUDIT_PLAN = "DEFINE_FINAL_AUDIT_PLAN"
    DEFINE_FINAL_GO_NO_GO_POLICY = "DEFINE_FINAL_GO_NO_GO_POLICY"
    RESTORE_OFFLINE_BOUNDARIES = "RESTORE_OFFLINE_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PLAN = "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PLAN"
    RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_SAFETY_GATE_SUITE = "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_SAFETY_GATE_SUITE"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PLAN = "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PLAN"


@dataclass(frozen=True)
class FinalSafetyFinding:
    score: int = 0
    passed: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionFinalSafetyGateRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class FinalExecutionScopeSafetyFinding(FinalSafetyFinding):
    offline_only: bool = False
    sandbox_only: bool = False
    safety_gate_only: bool = False
    no_dry_run_executed: bool = False
    prohibited_actions_confirmed: bool = False


@dataclass(frozen=True)
class FinalExecutionSequenceSafetyFinding(FinalSafetyFinding):
    sequence_steps_defined: bool = False
    dry_run_not_executed: bool = False
    connection_not_executed: bool = False
    fail_closed: bool = False


@dataclass(frozen=True)
class FinalExecutionPreconditionSafetyFinding(FinalSafetyFinding):
    final_plan_required: bool = False
    safety_gate_required: bool = False
    human_approval_required: bool = False
    stop_conditions_required: bool = False


@dataclass(frozen=True)
class FinalCredentialsReferenceSafetyFinding(FinalSafetyFinding):
    reference_only: bool = False
    no_secret_values: bool = False
    no_api_key_read: bool = False
    no_env_var_read: bool = False


@dataclass(frozen=True)
class FinalNetworkBlockSafetyFinding(FinalSafetyFinding):
    network_execution_blocked: bool = False
    http_blocked: bool = False
    websocket_blocked: bool = False
    socket_blocked: bool = False
    external_api_blocked: bool = False


@dataclass(frozen=True)
class FinalAccountReadOnlySafetyFinding(FinalSafetyFinding):
    active_account_access_blocked: bool = False
    account_mutations_blocked: bool = False
    schema_only_account_review: bool = False


@dataclass(frozen=True)
class FinalMarketDataReadOnlySafetyFinding(FinalSafetyFinding):
    read_only_market_data_only: bool = False
    live_subscription_blocked: bool = False
    network_request_blocked: bool = False
    schema_or_synthetic_only: bool = False


@dataclass(frozen=True)
class FinalOrderBlockingSafetyFinding(FinalSafetyFinding):
    order_execution_blocked: bool = False
    real_order_blocked: bool = False
    cancel_replace_blocked: bool = False


@dataclass(frozen=True)
class FinalPositionMutationBlockSafetyFinding(FinalSafetyFinding):
    position_mutation_blocked: bool = False
    position_request_absent: bool = False
    close_modify_blocked: bool = False


@dataclass(frozen=True)
class FinalObservabilitySafetyFinding(FinalSafetyFinding):
    offline_events_defined: bool = False
    connection_attempt_logging_disabled: bool = False
    sensitive_values_redacted: bool = False


@dataclass(frozen=True)
class FinalJournalSafetyFinding(FinalSafetyFinding):
    offline_journal_required: bool = False
    sensitive_values_redacted: bool = False
    no_secret_material_logged: bool = False


@dataclass(frozen=True)
class FinalHumanApprovalSafetyFinding(FinalSafetyFinding):
    human_approval_required: bool = False
    approval_before_safety_gate: bool = False
    final_plan_evidence_required: bool = False


@dataclass(frozen=True)
class FinalStopConditionSafetyFinding(FinalSafetyFinding):
    stop_on_secret_read: bool = False
    stop_on_network_request: bool = False
    stop_on_order_or_position_request: bool = False
    stop_on_account_access_request: bool = False


@dataclass(frozen=True)
class FinalSuccessFailureSafetyFinding(FinalSafetyFinding):
    success_criteria_defined: bool = False
    failure_criteria_defined: bool = False
    requires_no_real_connection: bool = False
    failure_on_boundary_violation: bool = False


@dataclass(frozen=True)
class FinalAuditSafetyFinding(FinalSafetyFinding):
    audit_events_defined: bool = False
    offline_evidence_required: bool = False
    final_safety_gate_trace_required: bool = False


@dataclass(frozen=True)
class FinalGoNoGoSafetyFinding(FinalSafetyFinding):
    go_requires_all_sections_ready: bool = False
    no_go_on_any_boundary_violation: bool = False
    human_go_required: bool = False


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunExecutionFinalSafetyGateScore:
    overall_score: int
    final_plan_score: int
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


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunExecutionFinalSafetyGateInput:
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
    dry_run_execution_final_plan_approved: bool | None = None
    final_execution_scope_safety_verified: bool | None = None
    final_execution_sequence_safety_verified: bool | None = None
    final_execution_precondition_safety_verified: bool | None = None
    final_credentials_reference_safety_verified: bool | None = None
    final_no_secret_read_safety_verified: bool | None = None
    final_network_block_safety_verified: bool | None = None
    final_http_websocket_socket_block_safety_verified: bool | None = None
    final_account_read_only_safety_verified: bool | None = None
    final_market_data_read_only_safety_verified: bool | None = None
    final_order_blocking_safety_verified: bool | None = None
    final_position_mutation_block_safety_verified: bool | None = None
    final_observability_safety_verified: bool | None = None
    final_journal_safety_verified: bool | None = None
    final_human_approval_safety_verified: bool | None = None
    final_stop_conditions_safety_verified: bool | None = None
    final_success_failure_criteria_safety_verified: bool | None = None
    final_audit_plan_safety_verified: bool | None = None
    final_go_no_go_policy_safety_verified: bool | None = None
    paper_broker_read_only_connection_dry_run_controlled_execution_plan_requested: bool | None = False
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
    final_plan_score: int | None = None
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
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunExecutionFinalSafetyGateResult:
    state: PaperBrokerReadOnlyConnectionDryRunExecutionFinalSafetyGateState
    decision: PaperBrokerReadOnlyConnectionDryRunExecutionFinalSafetyGateDecision
    safety_gate_score: int
    score_breakdown: PaperBrokerReadOnlyConnectionDryRunExecutionFinalSafetyGateScore
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionFinalSafetyGateRisk, ...] = ()
    recommendations: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionFinalSafetyGateRecommendation, ...] = ()
    scope_safety: FinalExecutionScopeSafetyFinding = field(default_factory=FinalExecutionScopeSafetyFinding)
    sequence_safety: FinalExecutionSequenceSafetyFinding = field(default_factory=FinalExecutionSequenceSafetyFinding)
    precondition_safety: FinalExecutionPreconditionSafetyFinding = field(default_factory=FinalExecutionPreconditionSafetyFinding)
    credentials_reference_safety: FinalCredentialsReferenceSafetyFinding = field(default_factory=FinalCredentialsReferenceSafetyFinding)
    no_secret_read_safety: FinalCredentialsReferenceSafetyFinding = field(default_factory=FinalCredentialsReferenceSafetyFinding)
    network_block_safety: FinalNetworkBlockSafetyFinding = field(default_factory=FinalNetworkBlockSafetyFinding)
    http_websocket_socket_block_safety: FinalNetworkBlockSafetyFinding = field(default_factory=FinalNetworkBlockSafetyFinding)
    account_read_only_safety: FinalAccountReadOnlySafetyFinding = field(default_factory=FinalAccountReadOnlySafetyFinding)
    market_data_read_only_safety: FinalMarketDataReadOnlySafetyFinding = field(default_factory=FinalMarketDataReadOnlySafetyFinding)
    order_blocking_safety: FinalOrderBlockingSafetyFinding = field(default_factory=FinalOrderBlockingSafetyFinding)
    position_mutation_block_safety: FinalPositionMutationBlockSafetyFinding = field(default_factory=FinalPositionMutationBlockSafetyFinding)
    observability_safety: FinalObservabilitySafetyFinding = field(default_factory=FinalObservabilitySafetyFinding)
    journal_safety: FinalJournalSafetyFinding = field(default_factory=FinalJournalSafetyFinding)
    human_approval_safety: FinalHumanApprovalSafetyFinding = field(default_factory=FinalHumanApprovalSafetyFinding)
    stop_conditions_safety: FinalStopConditionSafetyFinding = field(default_factory=FinalStopConditionSafetyFinding)
    success_failure_criteria_safety: FinalSuccessFailureSafetyFinding = field(default_factory=FinalSuccessFailureSafetyFinding)
    audit_plan_safety: FinalAuditSafetyFinding = field(default_factory=FinalAuditSafetyFinding)
    go_no_go_policy_safety: FinalGoNoGoSafetyFinding = field(default_factory=FinalGoNoGoSafetyFinding)
    offline_only: bool = True
    summary: str = ""