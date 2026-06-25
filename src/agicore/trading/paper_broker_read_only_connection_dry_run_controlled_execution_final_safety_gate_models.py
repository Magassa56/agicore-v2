"""Models for Paper Broker Read-Only Connection Dry Run Controlled Execution Final Safety Gate."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateState(StrEnum):
    NOT_READY = "NOT_READY"
    FINAL_SAFETY_GATE_INPUT_INVALID = "FINAL_SAFETY_GATE_INPUT_INVALID"
    FINAL_SAFETY_GATE_BLOCKED = "FINAL_SAFETY_GATE_BLOCKED"
    FINAL_SAFETY_GATE_COMPLETED_WITH_WARNINGS = "FINAL_SAFETY_GATE_COMPLETED_WITH_WARNINGS"
    FINAL_SAFETY_GATE_COMPLETED = "FINAL_SAFETY_GATE_COMPLETED"
    READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PLAN = "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PLAN"


class PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateDecision(StrEnum):
    BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_SAFETY_GATE = "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_SAFETY_GATE"
    REQUIRE_FINAL_CONTROLLED_EXECUTION_PLAN_FIXES = "REQUIRE_FINAL_CONTROLLED_EXECUTION_PLAN_FIXES"
    REQUIRE_FINAL_SAFETY_RUNTIME_BOUNDARY_FIXES = "REQUIRE_FINAL_SAFETY_RUNTIME_BOUNDARY_FIXES"
    REQUIRE_FINAL_SAFETY_OFFLINE_SANDBOX_FIXES = "REQUIRE_FINAL_SAFETY_OFFLINE_SANDBOX_FIXES"
    REQUIRE_FINAL_SAFETY_CREDENTIAL_BOUNDARY_FIXES = "REQUIRE_FINAL_SAFETY_CREDENTIAL_BOUNDARY_FIXES"
    REQUIRE_FINAL_SAFETY_NO_SECRET_READ_FIXES = "REQUIRE_FINAL_SAFETY_NO_SECRET_READ_FIXES"
    REQUIRE_FINAL_SAFETY_NETWORK_BLOCK_FIXES = "REQUIRE_FINAL_SAFETY_NETWORK_BLOCK_FIXES"
    REQUIRE_FINAL_SAFETY_ACCOUNT_READ_ONLY_FIXES = "REQUIRE_FINAL_SAFETY_ACCOUNT_READ_ONLY_FIXES"
    REQUIRE_FINAL_SAFETY_MARKET_DATA_READ_ONLY_FIXES = "REQUIRE_FINAL_SAFETY_MARKET_DATA_READ_ONLY_FIXES"
    REQUIRE_FINAL_SAFETY_ORDER_BLOCKING_FIXES = "REQUIRE_FINAL_SAFETY_ORDER_BLOCKING_FIXES"
    REQUIRE_FINAL_SAFETY_POSITION_MUTATION_BLOCKING_FIXES = "REQUIRE_FINAL_SAFETY_POSITION_MUTATION_BLOCKING_FIXES"
    REQUIRE_FINAL_SAFETY_OBSERVABILITY_FIXES = "REQUIRE_FINAL_SAFETY_OBSERVABILITY_FIXES"
    REQUIRE_FINAL_SAFETY_JOURNAL_FIXES = "REQUIRE_FINAL_SAFETY_JOURNAL_FIXES"
    REQUIRE_FINAL_SAFETY_HUMAN_APPROVAL_FIXES = "REQUIRE_FINAL_SAFETY_HUMAN_APPROVAL_FIXES"
    REQUIRE_FINAL_SAFETY_STOP_CONDITION_FIXES = "REQUIRE_FINAL_SAFETY_STOP_CONDITION_FIXES"
    REQUIRE_FINAL_SAFETY_SUCCESS_FAILURE_FIXES = "REQUIRE_FINAL_SAFETY_SUCCESS_FAILURE_FIXES"
    REQUIRE_FINAL_SAFETY_AUDIT_FIXES = "REQUIRE_FINAL_SAFETY_AUDIT_FIXES"
    REQUIRE_FINAL_SAFETY_GO_NO_GO_FIXES = "REQUIRE_FINAL_SAFETY_GO_NO_GO_FIXES"
    REQUIRE_FINAL_SAFETY_ABORT_FIXES = "REQUIRE_FINAL_SAFETY_ABORT_FIXES"
    REQUIRE_FINAL_SAFETY_PROFITABILITY_OBSERVATION_FIXES = "REQUIRE_FINAL_SAFETY_PROFITABILITY_OBSERVATION_FIXES"
    REQUIRE_FINAL_SAFETY_CONSISTENCY_OBSERVATION_FIXES = "REQUIRE_FINAL_SAFETY_CONSISTENCY_OBSERVATION_FIXES"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_SAFETY_GATE = "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_SAFETY_GATE"


class PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateRisk(StrEnum):
    FINAL_CONTROLLED_EXECUTION_PLAN_NOT_APPROVED = "FINAL_CONTROLLED_EXECUTION_PLAN_NOT_APPROVED"
    FINAL_SAFETY_RUNTIME_BOUNDARY_FAILED = "FINAL_SAFETY_RUNTIME_BOUNDARY_FAILED"
    FINAL_SAFETY_OFFLINE_SANDBOX_BOUNDARY_FAILED = "FINAL_SAFETY_OFFLINE_SANDBOX_BOUNDARY_FAILED"
    FINAL_SAFETY_CREDENTIAL_BOUNDARY_FAILED = "FINAL_SAFETY_CREDENTIAL_BOUNDARY_FAILED"
    FINAL_SAFETY_SECRET_READ_BOUNDARY_FAILED = "FINAL_SAFETY_SECRET_READ_BOUNDARY_FAILED"
    FINAL_SAFETY_NETWORK_BLOCK_BOUNDARY_FAILED = "FINAL_SAFETY_NETWORK_BLOCK_BOUNDARY_FAILED"
    FINAL_SAFETY_HTTP_WEBSOCKET_SOCKET_BLOCK_BOUNDARY_FAILED = "FINAL_SAFETY_HTTP_WEBSOCKET_SOCKET_BLOCK_BOUNDARY_FAILED"
    FINAL_SAFETY_ACCOUNT_READ_ONLY_BOUNDARY_FAILED = "FINAL_SAFETY_ACCOUNT_READ_ONLY_BOUNDARY_FAILED"
    FINAL_SAFETY_MARKET_DATA_READ_ONLY_BOUNDARY_FAILED = "FINAL_SAFETY_MARKET_DATA_READ_ONLY_BOUNDARY_FAILED"
    FINAL_SAFETY_ORDER_BLOCKING_BOUNDARY_FAILED = "FINAL_SAFETY_ORDER_BLOCKING_BOUNDARY_FAILED"
    FINAL_SAFETY_POSITION_MUTATION_BLOCKING_BOUNDARY_FAILED = "FINAL_SAFETY_POSITION_MUTATION_BLOCKING_BOUNDARY_FAILED"
    FINAL_SAFETY_OBSERVABILITY_BOUNDARY_FAILED = "FINAL_SAFETY_OBSERVABILITY_BOUNDARY_FAILED"
    FINAL_SAFETY_JOURNAL_BOUNDARY_FAILED = "FINAL_SAFETY_JOURNAL_BOUNDARY_FAILED"
    FINAL_SAFETY_HUMAN_APPROVAL_BOUNDARY_FAILED = "FINAL_SAFETY_HUMAN_APPROVAL_BOUNDARY_FAILED"
    FINAL_SAFETY_STOP_CONDITION_BOUNDARY_FAILED = "FINAL_SAFETY_STOP_CONDITION_BOUNDARY_FAILED"
    FINAL_SAFETY_SUCCESS_FAILURE_BOUNDARY_FAILED = "FINAL_SAFETY_SUCCESS_FAILURE_BOUNDARY_FAILED"
    FINAL_SAFETY_AUDIT_BOUNDARY_FAILED = "FINAL_SAFETY_AUDIT_BOUNDARY_FAILED"
    FINAL_SAFETY_GO_NO_GO_BOUNDARY_FAILED = "FINAL_SAFETY_GO_NO_GO_BOUNDARY_FAILED"
    FINAL_SAFETY_ABORT_BOUNDARY_FAILED = "FINAL_SAFETY_ABORT_BOUNDARY_FAILED"
    FINAL_SAFETY_PROFITABILITY_OBSERVATION_BOUNDARY_FAILED = "FINAL_SAFETY_PROFITABILITY_OBSERVATION_BOUNDARY_FAILED"
    FINAL_SAFETY_CONSISTENCY_OBSERVATION_BOUNDARY_FAILED = "FINAL_SAFETY_CONSISTENCY_OBSERVATION_BOUNDARY_FAILED"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PLAN = "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PLAN"


class PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateRecommendation(StrEnum):
    HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PLAN = "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PLAN"
    APPROVE_FINAL_CONTROLLED_EXECUTION_PLAN_FIRST = "APPROVE_FINAL_CONTROLLED_EXECUTION_PLAN_FIRST"
    HARDEN_FINAL_SAFETY_RUNTIME_BOUNDARY = "HARDEN_FINAL_SAFETY_RUNTIME_BOUNDARY"
    RESTORE_FINAL_SAFETY_OFFLINE_SANDBOX = "RESTORE_FINAL_SAFETY_OFFLINE_SANDBOX"
    HARDEN_FINAL_SAFETY_CREDENTIAL_BOUNDARY = "HARDEN_FINAL_SAFETY_CREDENTIAL_BOUNDARY"
    HARDEN_FINAL_SAFETY_NO_SECRET_READ = "HARDEN_FINAL_SAFETY_NO_SECRET_READ"
    BLOCK_FINAL_SAFETY_NETWORK_TRANSPORT = "BLOCK_FINAL_SAFETY_NETWORK_TRANSPORT"
    BLOCK_FINAL_SAFETY_HTTP_WEBSOCKET_SOCKET = "BLOCK_FINAL_SAFETY_HTTP_WEBSOCKET_SOCKET"
    HARDEN_FINAL_SAFETY_ACCOUNT_READ_ONLY = "HARDEN_FINAL_SAFETY_ACCOUNT_READ_ONLY"
    HARDEN_FINAL_SAFETY_MARKET_DATA_READ_ONLY = "HARDEN_FINAL_SAFETY_MARKET_DATA_READ_ONLY"
    HARDEN_FINAL_SAFETY_ORDER_BLOCKING = "HARDEN_FINAL_SAFETY_ORDER_BLOCKING"
    HARDEN_FINAL_SAFETY_POSITION_MUTATION_BLOCKING = "HARDEN_FINAL_SAFETY_POSITION_MUTATION_BLOCKING"
    COMPLETE_FINAL_SAFETY_OBSERVABILITY = "COMPLETE_FINAL_SAFETY_OBSERVABILITY"
    COMPLETE_FINAL_SAFETY_JOURNAL = "COMPLETE_FINAL_SAFETY_JOURNAL"
    REQUIRE_FINAL_SAFETY_HUMAN_APPROVAL = "REQUIRE_FINAL_SAFETY_HUMAN_APPROVAL"
    DEFINE_FINAL_SAFETY_STOP_CONDITIONS = "DEFINE_FINAL_SAFETY_STOP_CONDITIONS"
    HARDEN_FINAL_SAFETY_SUCCESS_FAILURE = "HARDEN_FINAL_SAFETY_SUCCESS_FAILURE"
    COMPLETE_FINAL_SAFETY_AUDIT = "COMPLETE_FINAL_SAFETY_AUDIT"
    DEFINE_FINAL_SAFETY_GO_NO_GO = "DEFINE_FINAL_SAFETY_GO_NO_GO"
    DEFINE_FINAL_SAFETY_ABORT = "DEFINE_FINAL_SAFETY_ABORT"
    DEFINE_FINAL_SAFETY_PROFITABILITY_OBSERVATION = "DEFINE_FINAL_SAFETY_PROFITABILITY_OBSERVATION"
    DEFINE_FINAL_SAFETY_CONSISTENCY_OBSERVATION = "DEFINE_FINAL_SAFETY_CONSISTENCY_OBSERVATION"
    RESTORE_OFFLINE_BOUNDARIES = "RESTORE_OFFLINE_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PLAN = "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PLAN"
    RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_SAFETY_GATE_SUITE = "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_SAFETY_GATE_SUITE"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PLAN = "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PLAN"


Risk = PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateRisk


@dataclass(frozen=True)
class _FinalSafetyBoundary:
    score: int = 0
    passed: bool = False
    risks: tuple[Risk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class FinalSafetyRuntimeBoundary(_FinalSafetyBoundary):
    runtime_safety_only: bool = False
    dry_run_not_executed: bool = False
    connection_not_executed: bool = False
    no_live_execution: bool = False


@dataclass(frozen=True)
class FinalSafetyOfflineSandboxBoundary(_FinalSafetyBoundary):
    offline_only: bool = False
    sandbox_only: bool = False
    safety_gate_only: bool = False
    no_data_access: bool = False


@dataclass(frozen=True)
class FinalSafetyCredentialsBoundary(_FinalSafetyBoundary):
    reference_only: bool = False
    no_secret_values: bool = False
    no_api_key_read: bool = False
    no_env_var_read: bool = False


@dataclass(frozen=True)
class FinalSafetyNoSecretReadBoundary(_FinalSafetyBoundary):
    no_api_key_read: bool = False
    no_env_var_read: bool = False
    no_hardcoded_secret: bool = False
    fail_on_secret_read_request: bool = False


@dataclass(frozen=True)
class FinalSafetyNetworkBlockBoundary(_FinalSafetyBoundary):
    network_execution_blocked: bool = False
    http_blocked: bool = False
    websocket_blocked: bool = False
    socket_blocked: bool = False
    external_api_blocked: bool = False


@dataclass(frozen=True)
class FinalSafetyAccountReadOnlyBoundary(_FinalSafetyBoundary):
    active_account_access_blocked: bool = False
    account_mutations_blocked: bool = False
    schema_only_account_review: bool = False


@dataclass(frozen=True)
class FinalSafetyMarketDataReadOnlyBoundary(_FinalSafetyBoundary):
    read_only_market_data_only: bool = False
    live_subscription_blocked: bool = False
    network_request_blocked: bool = False
    schema_or_synthetic_only: bool = False


@dataclass(frozen=True)
class FinalSafetyOrderBlockingBoundary(_FinalSafetyBoundary):
    order_execution_blocked: bool = False
    real_order_blocked: bool = False
    cancel_replace_blocked: bool = False


@dataclass(frozen=True)
class FinalSafetyPositionMutationBlockingBoundary(_FinalSafetyBoundary):
    position_mutation_blocked: bool = False
    position_request_absent: bool = False
    close_modify_blocked: bool = False

@dataclass(frozen=True)
class FinalSafetyObservabilityBoundary(_FinalSafetyBoundary):
    offline_events_defined: bool = False
    connection_attempt_logging_disabled: bool = False
    sensitive_values_redacted: bool = False


@dataclass(frozen=True)
class FinalSafetyJournalBoundary(_FinalSafetyBoundary):
    offline_journal_required: bool = False
    sensitive_values_redacted: bool = False
    no_secret_material_logged: bool = False


@dataclass(frozen=True)
class FinalSafetyHumanApprovalBoundary(_FinalSafetyBoundary):
    human_approval_required: bool = False
    approval_before_runner_plan: bool = False
    final_plan_evidence_required: bool = False


@dataclass(frozen=True)
class FinalSafetyStopConditionBoundary(_FinalSafetyBoundary):
    stop_on_secret_read: bool = False
    stop_on_network_request: bool = False
    stop_on_order_or_position_request: bool = False
    stop_on_account_access_request: bool = False


@dataclass(frozen=True)
class FinalSafetySuccessFailureBoundary(_FinalSafetyBoundary):
    success_criteria_defined: bool = False
    failure_criteria_defined: bool = False
    requires_no_real_connection: bool = False
    failure_on_boundary_violation: bool = False


@dataclass(frozen=True)
class FinalSafetyAuditBoundary(_FinalSafetyBoundary):
    audit_events_defined: bool = False
    offline_evidence_required: bool = False
    final_safety_gate_trace_required: bool = False


@dataclass(frozen=True)
class FinalSafetyGoNoGoBoundary(_FinalSafetyBoundary):
    go_requires_all_boundaries_passed: bool = False
    no_go_on_any_boundary_violation: bool = False
    human_go_required: bool = False


@dataclass(frozen=True)
class FinalSafetyAbortBoundary(_FinalSafetyBoundary):
    abort_on_boundary_violation: bool = False
    abort_on_secret_read_request: bool = False
    abort_on_network_or_order_request: bool = False


@dataclass(frozen=True)
class FinalSafetyProfitabilityObservationBoundary(_FinalSafetyBoundary):
    observation_only: bool = False
    no_profit_promise: bool = False
    synthetic_or_paper_metrics_only: bool = False
    no_trading_decision_from_observation: bool = False


@dataclass(frozen=True)
class FinalSafetyConsistencyObservationBoundary(_FinalSafetyBoundary):
    observation_only: bool = False
    deterministic_checks_required: bool = False
    no_runtime_adaptation: bool = False
    repeated_result_review_required: bool = False


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateScore:
    overall_score: int
    final_plan_score: int
    runtime_score: int
    offline_sandbox_score: int
    credentials_score: int
    no_secret_score: int
    network_score: int
    http_websocket_socket_score: int
    account_score: int
    market_data_score: int
    order_score: int
    position_score: int
    observability_score: int
    journal_score: int
    human_approval_score: int
    stop_conditions_score: int
    success_failure_score: int
    audit_score: int
    go_no_go_score: int
    abort_score: int
    profitability_observation_score: int
    consistency_observation_score: int


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateInput:
    paper_broker_read_only_connection_dry_run_controlled_execution_final_plan: Any = None
    paper_broker_read_only_connection_dry_run_controlled_execution_preparation_review: Any = None
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
    final_controlled_execution_plan_approved: bool | None = None
    final_safety_runtime_boundary_verified: bool | None = None
    final_safety_offline_sandbox_boundary_verified: bool | None = None
    final_safety_credentials_boundary_verified: bool | None = None
    final_safety_no_secret_read_boundary_verified: bool | None = None
    final_safety_network_block_boundary_verified: bool | None = None
    final_safety_http_websocket_socket_block_boundary_verified: bool | None = None
    final_safety_account_read_only_boundary_verified: bool | None = None
    final_safety_market_data_read_only_boundary_verified: bool | None = None
    final_safety_order_blocking_boundary_verified: bool | None = None
    final_safety_position_mutation_blocking_boundary_verified: bool | None = None
    final_safety_observability_boundary_verified: bool | None = None
    final_safety_journal_boundary_verified: bool | None = None
    final_safety_human_approval_boundary_verified: bool | None = None
    final_safety_stop_conditions_boundary_verified: bool | None = None
    final_safety_success_failure_boundary_verified: bool | None = None
    final_safety_audit_boundary_verified: bool | None = None
    final_safety_go_no_go_boundary_verified: bool | None = None
    final_safety_abort_boundary_verified: bool | None = None
    final_safety_profitability_observation_boundary_verified: bool | None = None
    final_safety_consistency_observation_boundary_verified: bool | None = None
    paper_broker_read_only_connection_dry_run_controlled_offline_runner_plan_requested: bool | None = False
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
    runtime_score: int | None = None
    offline_sandbox_score: int | None = None
    credentials_score: int | None = None
    no_secret_score: int | None = None
    network_score: int | None = None
    http_websocket_socket_score: int | None = None
    account_score: int | None = None
    market_data_score: int | None = None
    order_score: int | None = None
    position_score: int | None = None
    observability_score: int | None = None
    journal_score: int | None = None
    human_approval_score: int | None = None
    stop_conditions_score: int | None = None
    success_failure_score: int | None = None
    audit_score: int | None = None
    go_no_go_score: int | None = None
    abort_score: int | None = None
    profitability_observation_score: int | None = None
    consistency_observation_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateResult:
    state: PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateState
    decision: PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateDecision
    safety_gate_score: int
    score_breakdown: PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateScore
    risks: tuple[Risk, ...] = ()
    recommendations: tuple[PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateRecommendation, ...] = ()
    runtime_boundary: FinalSafetyRuntimeBoundary = field(default_factory=FinalSafetyRuntimeBoundary)
    offline_sandbox_boundary: FinalSafetyOfflineSandboxBoundary = field(default_factory=FinalSafetyOfflineSandboxBoundary)
    credentials_boundary: FinalSafetyCredentialsBoundary = field(default_factory=FinalSafetyCredentialsBoundary)
    no_secret_read_boundary: FinalSafetyNoSecretReadBoundary = field(default_factory=FinalSafetyNoSecretReadBoundary)
    network_block_boundary: FinalSafetyNetworkBlockBoundary = field(default_factory=FinalSafetyNetworkBlockBoundary)
    http_websocket_socket_block_boundary: FinalSafetyNetworkBlockBoundary = field(default_factory=FinalSafetyNetworkBlockBoundary)
    account_read_only_boundary: FinalSafetyAccountReadOnlyBoundary = field(default_factory=FinalSafetyAccountReadOnlyBoundary)
    market_data_read_only_boundary: FinalSafetyMarketDataReadOnlyBoundary = field(default_factory=FinalSafetyMarketDataReadOnlyBoundary)
    order_blocking_boundary: FinalSafetyOrderBlockingBoundary = field(default_factory=FinalSafetyOrderBlockingBoundary)
    position_mutation_blocking_boundary: FinalSafetyPositionMutationBlockingBoundary = field(default_factory=FinalSafetyPositionMutationBlockingBoundary)
    observability_boundary: FinalSafetyObservabilityBoundary = field(default_factory=FinalSafetyObservabilityBoundary)
    journal_boundary: FinalSafetyJournalBoundary = field(default_factory=FinalSafetyJournalBoundary)
    human_approval_boundary: FinalSafetyHumanApprovalBoundary = field(default_factory=FinalSafetyHumanApprovalBoundary)
    stop_condition_boundary: FinalSafetyStopConditionBoundary = field(default_factory=FinalSafetyStopConditionBoundary)
    success_failure_boundary: FinalSafetySuccessFailureBoundary = field(default_factory=FinalSafetySuccessFailureBoundary)
    audit_boundary: FinalSafetyAuditBoundary = field(default_factory=FinalSafetyAuditBoundary)
    go_no_go_boundary: FinalSafetyGoNoGoBoundary = field(default_factory=FinalSafetyGoNoGoBoundary)
    abort_boundary: FinalSafetyAbortBoundary = field(default_factory=FinalSafetyAbortBoundary)
    profitability_observation_boundary: FinalSafetyProfitabilityObservationBoundary = field(default_factory=FinalSafetyProfitabilityObservationBoundary)
    consistency_observation_boundary: FinalSafetyConsistencyObservationBoundary = field(default_factory=FinalSafetyConsistencyObservationBoundary)
    offline_only: bool = True
    summary: str = ""