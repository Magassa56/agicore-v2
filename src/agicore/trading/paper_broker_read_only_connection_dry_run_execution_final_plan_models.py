"""Models for AGIcore Paper Broker Read-Only Connection Dry Run Execution Final Plan."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanState(StrEnum):
    NOT_READY = "NOT_READY"
    DRY_RUN_EXECUTION_FINAL_PLAN_INPUT_INVALID = "DRY_RUN_EXECUTION_FINAL_PLAN_INPUT_INVALID"
    DRY_RUN_EXECUTION_FINAL_PLAN_BLOCKED = "DRY_RUN_EXECUTION_FINAL_PLAN_BLOCKED"
    DRY_RUN_EXECUTION_FINAL_PLAN_COMPLETED_WITH_WARNINGS = "DRY_RUN_EXECUTION_FINAL_PLAN_COMPLETED_WITH_WARNINGS"
    DRY_RUN_EXECUTION_FINAL_PLAN_COMPLETED = "DRY_RUN_EXECUTION_FINAL_PLAN_COMPLETED"
    READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_SAFETY_GATE = "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_SAFETY_GATE"


class PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanDecision(StrEnum):
    BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN = "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN"
    REQUIRE_DRY_RUN_EXECUTION_PREPARATION_REVIEW_FIXES = "REQUIRE_DRY_RUN_EXECUTION_PREPARATION_REVIEW_FIXES"
    REQUIRE_FINAL_EXECUTION_SCOPE_FIXES = "REQUIRE_FINAL_EXECUTION_SCOPE_FIXES"
    REQUIRE_FINAL_EXECUTION_SEQUENCE_FIXES = "REQUIRE_FINAL_EXECUTION_SEQUENCE_FIXES"
    REQUIRE_FINAL_EXECUTION_PRECONDITION_FIXES = "REQUIRE_FINAL_EXECUTION_PRECONDITION_FIXES"
    REQUIRE_FINAL_CREDENTIAL_POLICY_FIXES = "REQUIRE_FINAL_CREDENTIAL_POLICY_FIXES"
    REQUIRE_FINAL_NO_SECRET_READ_FIXES = "REQUIRE_FINAL_NO_SECRET_READ_FIXES"
    REQUIRE_FINAL_NETWORK_BLOCK_FIXES = "REQUIRE_FINAL_NETWORK_BLOCK_FIXES"
    REQUIRE_FINAL_ACCOUNT_READ_ONLY_FIXES = "REQUIRE_FINAL_ACCOUNT_READ_ONLY_FIXES"
    REQUIRE_FINAL_MARKET_DATA_READ_ONLY_FIXES = "REQUIRE_FINAL_MARKET_DATA_READ_ONLY_FIXES"
    REQUIRE_FINAL_ORDER_BLOCKING_FIXES = "REQUIRE_FINAL_ORDER_BLOCKING_FIXES"
    REQUIRE_FINAL_POSITION_MUTATION_BLOCK_FIXES = "REQUIRE_FINAL_POSITION_MUTATION_BLOCK_FIXES"
    REQUIRE_FINAL_OBSERVABILITY_FIXES = "REQUIRE_FINAL_OBSERVABILITY_FIXES"
    REQUIRE_FINAL_JOURNAL_FIXES = "REQUIRE_FINAL_JOURNAL_FIXES"
    REQUIRE_FINAL_HUMAN_APPROVAL_FIXES = "REQUIRE_FINAL_HUMAN_APPROVAL_FIXES"
    REQUIRE_FINAL_STOP_CONDITION_FIXES = "REQUIRE_FINAL_STOP_CONDITION_FIXES"
    REQUIRE_FINAL_SUCCESS_FAILURE_FIXES = "REQUIRE_FINAL_SUCCESS_FAILURE_FIXES"
    REQUIRE_FINAL_AUDIT_FIXES = "REQUIRE_FINAL_AUDIT_FIXES"
    REQUIRE_FINAL_GO_NO_GO_FIXES = "REQUIRE_FINAL_GO_NO_GO_FIXES"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN = "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN"


class PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk(StrEnum):
    DRY_RUN_EXECUTION_PREPARATION_REVIEW_NOT_APPROVED = "DRY_RUN_EXECUTION_PREPARATION_REVIEW_NOT_APPROVED"
    FINAL_EXECUTION_SCOPE_UNCLEAR = "FINAL_EXECUTION_SCOPE_UNCLEAR"
    FINAL_EXECUTION_SEQUENCE_MISSING = "FINAL_EXECUTION_SEQUENCE_MISSING"
    FINAL_EXECUTION_PRECONDITION_MISSING = "FINAL_EXECUTION_PRECONDITION_MISSING"
    FINAL_CREDENTIAL_POLICY_UNSAFE = "FINAL_CREDENTIAL_POLICY_UNSAFE"
    FINAL_SECRET_READ_POLICY_UNSAFE = "FINAL_SECRET_READ_POLICY_UNSAFE"
    FINAL_NETWORK_NOT_BLOCKED = "FINAL_NETWORK_NOT_BLOCKED"
    FINAL_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED = "FINAL_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED"
    FINAL_ACCOUNT_READ_ONLY_UNSAFE = "FINAL_ACCOUNT_READ_ONLY_UNSAFE"
    FINAL_MARKET_DATA_READ_ONLY_UNSAFE = "FINAL_MARKET_DATA_READ_ONLY_UNSAFE"
    FINAL_ORDER_BLOCKING_UNSAFE = "FINAL_ORDER_BLOCKING_UNSAFE"
    FINAL_POSITION_MUTATION_BLOCK_UNSAFE = "FINAL_POSITION_MUTATION_BLOCK_UNSAFE"
    FINAL_OBSERVABILITY_MISSING = "FINAL_OBSERVABILITY_MISSING"
    FINAL_JOURNAL_MISSING = "FINAL_JOURNAL_MISSING"
    FINAL_HUMAN_APPROVAL_MISSING = "FINAL_HUMAN_APPROVAL_MISSING"
    FINAL_STOP_CONDITIONS_MISSING = "FINAL_STOP_CONDITIONS_MISSING"
    FINAL_SUCCESS_CRITERIA_MISSING = "FINAL_SUCCESS_CRITERIA_MISSING"
    FINAL_FAILURE_CRITERIA_MISSING = "FINAL_FAILURE_CRITERIA_MISSING"
    FINAL_AUDIT_PLAN_MISSING = "FINAL_AUDIT_PLAN_MISSING"
    FINAL_GO_NO_GO_POLICY_MISSING = "FINAL_GO_NO_GO_POLICY_MISSING"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_SAFETY_GATE = "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_SAFETY_GATE"


class PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRecommendation(StrEnum):
    HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_SAFETY_GATE = "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_SAFETY_GATE"
    APPROVE_DRY_RUN_EXECUTION_PREPARATION_REVIEW_FIRST = "APPROVE_DRY_RUN_EXECUTION_PREPARATION_REVIEW_FIRST"
    DEFINE_FINAL_EXECUTION_SCOPE = "DEFINE_FINAL_EXECUTION_SCOPE"
    DEFINE_FINAL_EXECUTION_SEQUENCE = "DEFINE_FINAL_EXECUTION_SEQUENCE"
    DEFINE_FINAL_EXECUTION_PRECONDITIONS = "DEFINE_FINAL_EXECUTION_PRECONDITIONS"
    HARDEN_FINAL_CREDENTIAL_POLICY = "HARDEN_FINAL_CREDENTIAL_POLICY"
    HARDEN_FINAL_NO_SECRET_READ_POLICY = "HARDEN_FINAL_NO_SECRET_READ_POLICY"
    BLOCK_FINAL_NETWORK_TRANSPORT = "BLOCK_FINAL_NETWORK_TRANSPORT"
    BLOCK_FINAL_HTTP_WEBSOCKET_SOCKET = "BLOCK_FINAL_HTTP_WEBSOCKET_SOCKET"
    HARDEN_FINAL_ACCOUNT_READ_ONLY = "HARDEN_FINAL_ACCOUNT_READ_ONLY"
    HARDEN_FINAL_MARKET_DATA_READ_ONLY = "HARDEN_FINAL_MARKET_DATA_READ_ONLY"
    HARDEN_FINAL_ORDER_BLOCKING = "HARDEN_FINAL_ORDER_BLOCKING"
    HARDEN_FINAL_POSITION_MUTATION_BLOCK = "HARDEN_FINAL_POSITION_MUTATION_BLOCK"
    COMPLETE_FINAL_OBSERVABILITY = "COMPLETE_FINAL_OBSERVABILITY"
    COMPLETE_FINAL_JOURNAL = "COMPLETE_FINAL_JOURNAL"
    REQUIRE_FINAL_HUMAN_APPROVAL = "REQUIRE_FINAL_HUMAN_APPROVAL"
    DEFINE_FINAL_STOP_CONDITIONS = "DEFINE_FINAL_STOP_CONDITIONS"
    DEFINE_FINAL_SUCCESS_FAILURE_CRITERIA = "DEFINE_FINAL_SUCCESS_FAILURE_CRITERIA"
    COMPLETE_FINAL_AUDIT_PLAN = "COMPLETE_FINAL_AUDIT_PLAN"
    DEFINE_FINAL_GO_NO_GO_POLICY = "DEFINE_FINAL_GO_NO_GO_POLICY"
    RESTORE_OFFLINE_BOUNDARIES = "RESTORE_OFFLINE_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_SAFETY_GATE = "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_SAFETY_GATE"
    RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN_SUITE = "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN_SUITE"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_SAFETY_GATE = "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_SAFETY_GATE"


@dataclass(frozen=True)
class _FinalPlanSection:
    name: str = "final_plan_section"
    score: int = 0
    defined: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class FinalDryRunExecutionScope(_FinalPlanSection):
    name: str = "final_dry_run_execution_scope"
    offline_only: bool = True
    sandbox_only: bool = True
    final_plan_only: bool = True
    dry_run_execution_disabled: bool = True


@dataclass(frozen=True)
class FinalDryRunExecutionSequence(_FinalPlanSection):
    name: str = "final_dry_run_execution_sequence"
    sequence_steps_defined: bool = True
    dry_run_not_executed: bool = True
    connection_not_executed: bool = True
    fail_closed: bool = True


@dataclass(frozen=True)
class FinalDryRunExecutionPrecondition(_FinalPlanSection):
    name: str = "final_dry_run_execution_precondition"
    preparation_review_required: bool = True
    safety_gate_required: bool = True
    human_approval_required: bool = True
    stop_conditions_required: bool = True


@dataclass(frozen=True)
class FinalCredentialsReferencePolicy(_FinalPlanSection):
    name: str = "final_credentials_reference_policy"
    reference_only: bool = True
    no_secret_values: bool = True
    no_api_key_read: bool = True
    no_env_var_read: bool = True


@dataclass(frozen=True)
class FinalNoSecretReadPolicy(_FinalPlanSection):
    name: str = "final_no_secret_read_policy"
    no_api_key_read: bool = True
    no_env_var_read: bool = True
    no_hardcoded_secret: bool = True
    fail_on_secret_read_request: bool = True


@dataclass(frozen=True)
class FinalNetworkBlockPolicy(_FinalPlanSection):
    name: str = "final_network_block_policy"
    network_execution_blocked: bool = True
    http_blocked: bool = True
    websocket_blocked: bool = True
    socket_blocked: bool = True
    external_api_blocked: bool = True


@dataclass(frozen=True)
class FinalAccountReadOnlyPolicy(_FinalPlanSection):
    name: str = "final_account_read_only_policy"
    active_account_access_blocked: bool = True
    account_mutations_blocked: bool = True
    schema_only_account_review: bool = True


@dataclass(frozen=True)
class FinalMarketDataReadOnlyPolicy(_FinalPlanSection):
    name: str = "final_market_data_read_only_policy"
    read_only_market_data_only: bool = True
    live_subscription_blocked: bool = True
    network_request_blocked: bool = True
    schema_or_synthetic_only: bool = True


@dataclass(frozen=True)
class FinalOrderBlockingPolicy(_FinalPlanSection):
    name: str = "final_order_blocking_policy"
    order_execution_blocked: bool = True
    real_order_blocked: bool = True
    cancel_replace_blocked: bool = True


@dataclass(frozen=True)
class FinalPositionMutationBlockPolicy(_FinalPlanSection):
    name: str = "final_position_mutation_block_policy"
    position_mutation_blocked: bool = True
    position_request_absent: bool = True
    close_modify_blocked: bool = True


@dataclass(frozen=True)
class FinalObservabilityPlan(_FinalPlanSection):
    name: str = "final_observability_plan"
    offline_events_defined: bool = True
    connection_attempt_logging_disabled: bool = True
    sensitive_values_redacted: bool = True


@dataclass(frozen=True)
class FinalJournalPlan(_FinalPlanSection):
    name: str = "final_journal_plan"
    offline_journal_required: bool = True
    sensitive_values_redacted: bool = True
    no_secret_material_logged: bool = True


@dataclass(frozen=True)
class FinalHumanApprovalPlan(_FinalPlanSection):
    name: str = "final_human_approval_plan"
    human_approval_required: bool = True
    approval_before_safety_gate: bool = True
    preparation_review_evidence_required: bool = True


@dataclass(frozen=True)
class FinalStopConditionPlan(_FinalPlanSection):
    name: str = "final_stop_condition_plan"
    stop_on_secret_read: bool = True
    stop_on_network_request: bool = True
    stop_on_order_or_position_request: bool = True
    stop_on_account_access_request: bool = True


@dataclass(frozen=True)
class FinalSuccessCriteria(_FinalPlanSection):
    name: str = "final_success_criteria"
    success_requires_no_real_connection: bool = True
    success_requires_all_guards_verified: bool = True
    success_requires_go_no_go_approval: bool = True


@dataclass(frozen=True)
class FinalFailureCriteria(_FinalPlanSection):
    name: str = "final_failure_criteria"
    failure_on_secret_read: bool = True
    failure_on_network_request: bool = True
    failure_on_order_position_or_account: bool = True


@dataclass(frozen=True)
class FinalAuditPlan(_FinalPlanSection):
    name: str = "final_audit_plan"
    audit_events_defined: bool = True
    offline_evidence_required: bool = True
    final_plan_trace_required: bool = True


@dataclass(frozen=True)
class FinalGoNoGoPolicy(_FinalPlanSection):
    name: str = "final_go_no_go_policy"
    go_requires_all_sections_ready: bool = True
    no_go_on_any_boundary_violation: bool = True
    human_go_required: bool = True


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanScore:
    overall_score: int
    preparation_review_score: int
    scope_score: int
    sequence_score: int
    precondition_score: int
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
    success_score: int
    failure_score: int
    audit_score: int
    go_no_go_score: int


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanInput:
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
    dry_run_execution_preparation_review_approved: bool | None = None
    final_execution_scope_defined: bool | None = None
    final_execution_sequence_defined: bool | None = None
    final_execution_preconditions_defined: bool | None = None
    final_credentials_reference_policy_defined: bool | None = None
    final_credentials_reference_only: bool | None = None
    final_no_secret_read_policy_defined: bool | None = None
    final_network_block_policy_defined: bool | None = None
    final_network_blocked: bool | None = None
    final_http_websocket_socket_block_policy_defined: bool | None = None
    final_http_blocked: bool | None = None
    final_websocket_blocked: bool | None = None
    final_socket_blocked: bool | None = None
    final_external_api_blocked: bool | None = None
    final_account_read_only_policy_defined: bool | None = None
    final_active_account_access_blocked: bool | None = None
    final_account_mutations_blocked: bool | None = None
    final_market_data_read_only_policy_defined: bool | None = None
    final_market_data_live_subscription_blocked: bool | None = None
    final_market_data_network_request_blocked: bool | None = None
    final_order_blocking_policy_defined: bool | None = None
    final_order_execution_blocked: bool | None = None
    final_cancel_replace_blocked: bool | None = None
    final_position_mutation_block_policy_defined: bool | None = None
    final_position_mutation_blocked: bool | None = None
    final_observability_plan_defined: bool | None = None
    final_journal_plan_defined: bool | None = None
    final_human_approval_plan_defined: bool | None = None
    final_human_approval_required: bool | None = None
    final_stop_conditions_plan_defined: bool | None = None
    final_success_criteria_defined: bool | None = None
    final_failure_criteria_defined: bool | None = None
    final_audit_plan_defined: bool | None = None
    final_go_no_go_policy_defined: bool | None = None
    paper_broker_read_only_connection_dry_run_execution_final_safety_gate_requested: bool | None = False
    offline_mode_enforced: bool | None = None
    sandbox_mode_enforced: bool | None = None
    final_plan_only: bool | None = None
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
    preparation_review_score: int | None = None
    scope_score: int | None = None
    sequence_score: int | None = None
    precondition_score: int | None = None
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
    success_score: int | None = None
    failure_score: int | None = None
    audit_score: int | None = None
    go_no_go_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanResult:
    state: PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanState
    decision: PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanDecision
    final_plan_score: int
    score_breakdown: PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanScore
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk, ...] = ()
    recommendations: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRecommendation, ...] = ()
    final_dry_run_execution_scope: FinalDryRunExecutionScope = field(default_factory=FinalDryRunExecutionScope)
    final_dry_run_execution_sequence: FinalDryRunExecutionSequence = field(default_factory=FinalDryRunExecutionSequence)
    final_dry_run_execution_precondition: FinalDryRunExecutionPrecondition = field(default_factory=FinalDryRunExecutionPrecondition)
    final_credentials_reference_policy: FinalCredentialsReferencePolicy = field(default_factory=FinalCredentialsReferencePolicy)
    final_no_secret_read_policy: FinalNoSecretReadPolicy = field(default_factory=FinalNoSecretReadPolicy)
    final_network_block_policy: FinalNetworkBlockPolicy = field(default_factory=FinalNetworkBlockPolicy)
    final_http_websocket_socket_block_policy: FinalNetworkBlockPolicy = field(default_factory=lambda: FinalNetworkBlockPolicy(name="final_http_websocket_socket_block_policy"))
    final_account_read_only_policy: FinalAccountReadOnlyPolicy = field(default_factory=FinalAccountReadOnlyPolicy)
    final_market_data_read_only_policy: FinalMarketDataReadOnlyPolicy = field(default_factory=FinalMarketDataReadOnlyPolicy)
    final_order_blocking_policy: FinalOrderBlockingPolicy = field(default_factory=FinalOrderBlockingPolicy)
    final_position_mutation_block_policy: FinalPositionMutationBlockPolicy = field(default_factory=FinalPositionMutationBlockPolicy)
    final_observability_plan: FinalObservabilityPlan = field(default_factory=FinalObservabilityPlan)
    final_journal_plan: FinalJournalPlan = field(default_factory=FinalJournalPlan)
    final_human_approval_plan: FinalHumanApprovalPlan = field(default_factory=FinalHumanApprovalPlan)
    final_stop_conditions_plan: FinalStopConditionPlan = field(default_factory=FinalStopConditionPlan)
    final_success_criteria: FinalSuccessCriteria = field(default_factory=FinalSuccessCriteria)
    final_failure_criteria: FinalFailureCriteria = field(default_factory=FinalFailureCriteria)
    final_audit_plan: FinalAuditPlan = field(default_factory=FinalAuditPlan)
    final_go_no_go_policy: FinalGoNoGoPolicy = field(default_factory=FinalGoNoGoPolicy)
    offline_only: bool = True
    summary: str = ""
