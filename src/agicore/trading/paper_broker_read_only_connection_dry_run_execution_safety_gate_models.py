"""Models for AGIcore Paper Broker Read-Only Connection Dry Run Execution Safety Gate."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateState(StrEnum):
    NOT_READY = "NOT_READY"
    DRY_RUN_EXECUTION_SAFETY_GATE_INPUT_INVALID = "DRY_RUN_EXECUTION_SAFETY_GATE_INPUT_INVALID"
    DRY_RUN_EXECUTION_SAFETY_GATE_BLOCKED = "DRY_RUN_EXECUTION_SAFETY_GATE_BLOCKED"
    DRY_RUN_EXECUTION_SAFETY_GATE_COMPLETED_WITH_WARNINGS = (
        "DRY_RUN_EXECUTION_SAFETY_GATE_COMPLETED_WITH_WARNINGS"
    )
    DRY_RUN_EXECUTION_SAFETY_GATE_COMPLETED = "DRY_RUN_EXECUTION_SAFETY_GATE_COMPLETED"
    READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION = (
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION"
    )


class PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateDecision(StrEnum):
    BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE = (
        "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE"
    )
    REQUIRE_DRY_RUN_EXECUTION_PLAN_FIXES = "REQUIRE_DRY_RUN_EXECUTION_PLAN_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_SCOPE_SAFETY_FIXES = "REQUIRE_DRY_RUN_EXECUTION_SCOPE_SAFETY_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_SEQUENCE_SAFETY_FIXES = "REQUIRE_DRY_RUN_EXECUTION_SEQUENCE_SAFETY_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_PRECONDITION_SAFETY_FIXES = (
        "REQUIRE_DRY_RUN_EXECUTION_PRECONDITION_SAFETY_FIXES"
    )
    REQUIRE_DRY_RUN_EXECUTION_CREDENTIAL_SAFETY_FIXES = "REQUIRE_DRY_RUN_EXECUTION_CREDENTIAL_SAFETY_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_NO_SECRET_READ_FIXES = "REQUIRE_DRY_RUN_EXECUTION_NO_SECRET_READ_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_NETWORK_BLOCK_FIXES = "REQUIRE_DRY_RUN_EXECUTION_NETWORK_BLOCK_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_FIXES = "REQUIRE_DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_FIXES = (
        "REQUIRE_DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_FIXES"
    )
    REQUIRE_DRY_RUN_EXECUTION_ORDER_BLOCKING_FIXES = "REQUIRE_DRY_RUN_EXECUTION_ORDER_BLOCKING_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_FIXES = (
        "REQUIRE_DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_FIXES"
    )
    REQUIRE_DRY_RUN_EXECUTION_HUMAN_APPROVAL_FIXES = "REQUIRE_DRY_RUN_EXECUTION_HUMAN_APPROVAL_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_STOP_CONDITION_FIXES = "REQUIRE_DRY_RUN_EXECUTION_STOP_CONDITION_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_AUDIT_FIXES = "REQUIRE_DRY_RUN_EXECUTION_AUDIT_FIXES"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE = (
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE"
    )


class PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk(StrEnum):
    DRY_RUN_EXECUTION_PLAN_NOT_APPROVED = "DRY_RUN_EXECUTION_PLAN_NOT_APPROVED"
    DRY_RUN_EXECUTION_SCOPE_UNSAFE = "DRY_RUN_EXECUTION_SCOPE_UNSAFE"
    DRY_RUN_EXECUTION_SEQUENCE_UNSAFE = "DRY_RUN_EXECUTION_SEQUENCE_UNSAFE"
    DRY_RUN_EXECUTION_PRECONDITION_UNSAFE = "DRY_RUN_EXECUTION_PRECONDITION_UNSAFE"
    DRY_RUN_EXECUTION_CREDENTIAL_POLICY_UNSAFE = "DRY_RUN_EXECUTION_CREDENTIAL_POLICY_UNSAFE"
    DRY_RUN_EXECUTION_SECRET_READ_POLICY_UNSAFE = "DRY_RUN_EXECUTION_SECRET_READ_POLICY_UNSAFE"
    DRY_RUN_EXECUTION_NETWORK_NOT_BLOCKED = "DRY_RUN_EXECUTION_NETWORK_NOT_BLOCKED"
    DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED = (
        "DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED"
    )
    DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_UNSAFE = "DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_UNSAFE"
    DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_UNSAFE = "DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_UNSAFE"
    DRY_RUN_EXECUTION_ORDER_BLOCKING_UNSAFE = "DRY_RUN_EXECUTION_ORDER_BLOCKING_UNSAFE"
    DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_UNSAFE = "DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_UNSAFE"
    DRY_RUN_EXECUTION_OBSERVABILITY_INCOMPLETE = "DRY_RUN_EXECUTION_OBSERVABILITY_INCOMPLETE"
    DRY_RUN_EXECUTION_JOURNAL_INCOMPLETE = "DRY_RUN_EXECUTION_JOURNAL_INCOMPLETE"
    DRY_RUN_EXECUTION_HUMAN_APPROVAL_MISSING = "DRY_RUN_EXECUTION_HUMAN_APPROVAL_MISSING"
    DRY_RUN_EXECUTION_STOP_CONDITIONS_MISSING = "DRY_RUN_EXECUTION_STOP_CONDITIONS_MISSING"
    DRY_RUN_EXECUTION_SUCCESS_FAILURE_CRITERIA_UNSAFE = (
        "DRY_RUN_EXECUTION_SUCCESS_FAILURE_CRITERIA_UNSAFE"
    )
    DRY_RUN_EXECUTION_AUDIT_PLAN_MISSING = "DRY_RUN_EXECUTION_AUDIT_PLAN_MISSING"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION = (
        "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION"
    )


class PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRecommendation(StrEnum):
    HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION = (
        "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION"
    )
    APPROVE_DRY_RUN_EXECUTION_PLAN_FIRST = "APPROVE_DRY_RUN_EXECUTION_PLAN_FIRST"
    HARDEN_DRY_RUN_EXECUTION_SCOPE = "HARDEN_DRY_RUN_EXECUTION_SCOPE"
    HARDEN_DRY_RUN_EXECUTION_SEQUENCE = "HARDEN_DRY_RUN_EXECUTION_SEQUENCE"
    HARDEN_DRY_RUN_EXECUTION_PRECONDITIONS = "HARDEN_DRY_RUN_EXECUTION_PRECONDITIONS"
    HARDEN_DRY_RUN_EXECUTION_CREDENTIALS = "HARDEN_DRY_RUN_EXECUTION_CREDENTIALS"
    HARDEN_DRY_RUN_EXECUTION_NO_SECRET_READ = "HARDEN_DRY_RUN_EXECUTION_NO_SECRET_READ"
    BLOCK_DRY_RUN_EXECUTION_NETWORK = "BLOCK_DRY_RUN_EXECUTION_NETWORK"
    BLOCK_DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET = "BLOCK_DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET"
    HARDEN_DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY = "HARDEN_DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY"
    HARDEN_DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY = "HARDEN_DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY"
    HARDEN_DRY_RUN_EXECUTION_ORDER_BLOCKING = "HARDEN_DRY_RUN_EXECUTION_ORDER_BLOCKING"
    HARDEN_DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK = "HARDEN_DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK"
    COMPLETE_DRY_RUN_EXECUTION_OBSERVABILITY = "COMPLETE_DRY_RUN_EXECUTION_OBSERVABILITY"
    COMPLETE_DRY_RUN_EXECUTION_JOURNAL = "COMPLETE_DRY_RUN_EXECUTION_JOURNAL"
    REQUIRE_DRY_RUN_EXECUTION_HUMAN_APPROVAL = "REQUIRE_DRY_RUN_EXECUTION_HUMAN_APPROVAL"
    DEFINE_DRY_RUN_EXECUTION_STOP_CONDITIONS = "DEFINE_DRY_RUN_EXECUTION_STOP_CONDITIONS"
    HARDEN_DRY_RUN_EXECUTION_SUCCESS_FAILURE_CRITERIA = (
        "HARDEN_DRY_RUN_EXECUTION_SUCCESS_FAILURE_CRITERIA"
    )
    DEFINE_DRY_RUN_EXECUTION_AUDIT_PLAN = "DEFINE_DRY_RUN_EXECUTION_AUDIT_PLAN"
    RESTORE_OFFLINE_BOUNDARIES = "RESTORE_OFFLINE_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION = (
        "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION"
    )
    RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE_SUITE = (
        "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE_SUITE"
    )
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION = (
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION"
    )


@dataclass(frozen=True)
class DryRunExecutionSafetyFinding:
    score: int = 0
    passed: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionScopeSafetyFinding(DryRunExecutionSafetyFinding):
    plan_only: bool = False
    offline_only: bool = False
    read_only_only: bool = False
    dry_run_not_executed: bool = False
    prohibited_actions_confirmed: bool = False


@dataclass(frozen=True)
class DryRunExecutionSequenceSafetyFinding(DryRunExecutionSafetyFinding):
    dry_run_not_executed: bool = False
    connection_not_executed: bool = False
    steps_defined: bool = False


@dataclass(frozen=True)
class DryRunExecutionPreconditionSafetyFinding(DryRunExecutionSafetyFinding):
    preparation_review_required: bool = False
    safety_gate_required_next: bool = False
    fail_closed: bool = False


@dataclass(frozen=True)
class DryRunExecutionCredentialsSafetyFinding(DryRunExecutionSafetyFinding):
    reference_only: bool = False
    no_secret_material: bool = False
    no_api_key_read: bool = False
    no_env_var_read: bool = False


@dataclass(frozen=True)
class DryRunExecutionNetworkBlockSafetyFinding(DryRunExecutionSafetyFinding):
    network_execution_blocked: bool = False
    http_blocked: bool = False
    websocket_blocked: bool = False
    socket_blocked: bool = False
    external_api_blocked: bool = False


@dataclass(frozen=True)
class DryRunExecutionAccountReadOnlySafetyFinding(DryRunExecutionSafetyFinding):
    active_account_access_blocked: bool = False
    account_mutations_blocked: bool = False
    schema_only_account_review: bool = False


@dataclass(frozen=True)
class DryRunExecutionMarketDataReadOnlySafetyFinding(DryRunExecutionSafetyFinding):
    read_only_market_data_only: bool = False
    live_subscription_blocked: bool = False
    network_request_blocked: bool = False
    schema_or_synthetic_only: bool = False


@dataclass(frozen=True)
class DryRunExecutionOrderBlockingSafetyFinding(DryRunExecutionSafetyFinding):
    order_execution_blocked: bool = False
    real_order_blocked: bool = False
    cancel_replace_blocked: bool = False


@dataclass(frozen=True)
class DryRunExecutionPositionMutationBlockSafetyFinding(DryRunExecutionSafetyFinding):
    position_mutation_blocked: bool = False
    position_request_absent: bool = False
    close_modify_blocked: bool = False


@dataclass(frozen=True)
class DryRunExecutionObservabilitySafetyFinding(DryRunExecutionSafetyFinding):
    offline_events_defined: bool = False
    connection_attempt_logging_disabled: bool = False
    sensitive_values_redacted: bool = False


@dataclass(frozen=True)
class DryRunExecutionJournalSafetyFinding(DryRunExecutionSafetyFinding):
    offline_journal_required: bool = False
    sensitive_values_redacted: bool = False
    no_secret_material_logged: bool = False


@dataclass(frozen=True)
class DryRunExecutionHumanApprovalSafetyFinding(DryRunExecutionSafetyFinding):
    human_approval_required: bool = False
    approval_before_safety_gate: bool = False
    preparation_review_evidence_required: bool = False


@dataclass(frozen=True)
class DryRunExecutionStopConditionSafetyFinding(DryRunExecutionSafetyFinding):
    stop_on_secret_read: bool = False
    stop_on_network_request: bool = False
    stop_on_order_or_position_request: bool = False
    stop_on_account_access_request: bool = False


@dataclass(frozen=True)
class DryRunExecutionSuccessFailureSafetyFinding(DryRunExecutionSafetyFinding):
    success_criteria_defined: bool = False
    failure_criteria_defined: bool = False
    requires_no_real_connection: bool = False
    failure_on_boundary_violation: bool = False


@dataclass(frozen=True)
class DryRunExecutionAuditSafetyFinding(DryRunExecutionSafetyFinding):
    audit_events_defined: bool = False
    offline_evidence_required: bool = False
    next_preparation_trace_required: bool = False


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateScore:
    overall_score: int
    dry_run_execution_plan_score: int
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


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput:
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
    dry_run_execution_plan_approved: bool | None = None
    dry_run_execution_scope_safety_verified: bool | None = None
    dry_run_execution_sequence_safety_verified: bool | None = None
    dry_run_execution_precondition_safety_verified: bool | None = None
    dry_run_execution_credentials_reference_safety_verified: bool | None = None
    dry_run_execution_no_secret_read_safety_verified: bool | None = None
    dry_run_execution_network_block_safety_verified: bool | None = None
    dry_run_execution_http_websocket_socket_block_safety_verified: bool | None = None
    dry_run_execution_account_read_only_safety_verified: bool | None = None
    dry_run_execution_market_data_read_only_safety_verified: bool | None = None
    dry_run_execution_order_blocking_safety_verified: bool | None = None
    dry_run_execution_position_mutation_block_safety_verified: bool | None = None
    dry_run_execution_observability_safety_verified: bool | None = None
    dry_run_execution_journal_safety_verified: bool | None = None
    dry_run_execution_human_approval_safety_verified: bool | None = None
    dry_run_execution_stop_conditions_safety_verified: bool | None = None
    dry_run_execution_success_failure_criteria_safety_verified: bool | None = None
    dry_run_execution_audit_plan_safety_verified: bool | None = None
    paper_broker_read_only_connection_dry_run_execution_preparation_requested: bool | None = False
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
    dry_run_execution_plan_score: int | None = None
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
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateResult:
    state: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateState
    decision: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateDecision
    safety_gate_score: int
    score_breakdown: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateScore
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk, ...] = ()
    recommendations: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRecommendation, ...] = ()
    scope_safety: DryRunExecutionScopeSafetyFinding = field(default_factory=DryRunExecutionScopeSafetyFinding)
    sequence_safety: DryRunExecutionSequenceSafetyFinding = field(default_factory=DryRunExecutionSequenceSafetyFinding)
    precondition_safety: DryRunExecutionPreconditionSafetyFinding = field(
        default_factory=DryRunExecutionPreconditionSafetyFinding
    )
    credentials_reference_safety: DryRunExecutionCredentialsSafetyFinding = field(
        default_factory=DryRunExecutionCredentialsSafetyFinding
    )
    no_secret_read_safety: DryRunExecutionCredentialsSafetyFinding = field(
        default_factory=DryRunExecutionCredentialsSafetyFinding
    )
    network_block_safety: DryRunExecutionNetworkBlockSafetyFinding = field(
        default_factory=DryRunExecutionNetworkBlockSafetyFinding
    )
    http_websocket_socket_block_safety: DryRunExecutionNetworkBlockSafetyFinding = field(
        default_factory=DryRunExecutionNetworkBlockSafetyFinding
    )
    account_read_only_safety: DryRunExecutionAccountReadOnlySafetyFinding = field(
        default_factory=DryRunExecutionAccountReadOnlySafetyFinding
    )
    market_data_read_only_safety: DryRunExecutionMarketDataReadOnlySafetyFinding = field(
        default_factory=DryRunExecutionMarketDataReadOnlySafetyFinding
    )
    order_blocking_safety: DryRunExecutionOrderBlockingSafetyFinding = field(
        default_factory=DryRunExecutionOrderBlockingSafetyFinding
    )
    position_mutation_block_safety: DryRunExecutionPositionMutationBlockSafetyFinding = field(
        default_factory=DryRunExecutionPositionMutationBlockSafetyFinding
    )
    observability_safety: DryRunExecutionObservabilitySafetyFinding = field(
        default_factory=DryRunExecutionObservabilitySafetyFinding
    )
    journal_safety: DryRunExecutionJournalSafetyFinding = field(default_factory=DryRunExecutionJournalSafetyFinding)
    human_approval_safety: DryRunExecutionHumanApprovalSafetyFinding = field(
        default_factory=DryRunExecutionHumanApprovalSafetyFinding
    )
    stop_conditions_safety: DryRunExecutionStopConditionSafetyFinding = field(
        default_factory=DryRunExecutionStopConditionSafetyFinding
    )
    success_failure_criteria_safety: DryRunExecutionSuccessFailureSafetyFinding = field(
        default_factory=DryRunExecutionSuccessFailureSafetyFinding
    )
    audit_plan_safety: DryRunExecutionAuditSafetyFinding = field(default_factory=DryRunExecutionAuditSafetyFinding)
    offline_only: bool = True
    summary: str = ""
