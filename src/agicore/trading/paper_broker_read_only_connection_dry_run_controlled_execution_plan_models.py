"""Models for AGIcore Paper Broker Read-Only Connection Dry Run Controlled Execution Plan."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanState(StrEnum):
    NOT_READY = "NOT_READY"
    CONTROLLED_EXECUTION_PLAN_INPUT_INVALID = "CONTROLLED_EXECUTION_PLAN_INPUT_INVALID"
    CONTROLLED_EXECUTION_PLAN_BLOCKED = "CONTROLLED_EXECUTION_PLAN_BLOCKED"
    CONTROLLED_EXECUTION_PLAN_COMPLETED_WITH_WARNINGS = "CONTROLLED_EXECUTION_PLAN_COMPLETED_WITH_WARNINGS"
    CONTROLLED_EXECUTION_PLAN_COMPLETED = "CONTROLLED_EXECUTION_PLAN_COMPLETED"
    READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE = "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE"


class PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanDecision(StrEnum):
    BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PLAN = "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PLAN"
    REQUIRE_FINAL_SAFETY_GATE_FIXES = "REQUIRE_FINAL_SAFETY_GATE_FIXES"
    REQUIRE_CONTROLLED_SCOPE_FIXES = "REQUIRE_CONTROLLED_SCOPE_FIXES"
    REQUIRE_CONTROLLED_SEQUENCE_FIXES = "REQUIRE_CONTROLLED_SEQUENCE_FIXES"
    REQUIRE_CONTROLLED_PRECONDITION_FIXES = "REQUIRE_CONTROLLED_PRECONDITION_FIXES"
    REQUIRE_CONTROLLED_CREDENTIAL_POLICY_FIXES = "REQUIRE_CONTROLLED_CREDENTIAL_POLICY_FIXES"
    REQUIRE_CONTROLLED_NO_SECRET_READ_FIXES = "REQUIRE_CONTROLLED_NO_SECRET_READ_FIXES"
    REQUIRE_CONTROLLED_NETWORK_BLOCK_FIXES = "REQUIRE_CONTROLLED_NETWORK_BLOCK_FIXES"
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
    REQUIRE_CONTROLLED_ABORT_POLICY_FIXES = "REQUIRE_CONTROLLED_ABORT_POLICY_FIXES"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PLAN = "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PLAN"


class PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk(StrEnum):
    DRY_RUN_EXECUTION_FINAL_SAFETY_GATE_NOT_APPROVED = "DRY_RUN_EXECUTION_FINAL_SAFETY_GATE_NOT_APPROVED"
    CONTROLLED_EXECUTION_SCOPE_UNCLEAR = "CONTROLLED_EXECUTION_SCOPE_UNCLEAR"
    CONTROLLED_EXECUTION_SEQUENCE_MISSING = "CONTROLLED_EXECUTION_SEQUENCE_MISSING"
    CONTROLLED_EXECUTION_PRECONDITION_MISSING = "CONTROLLED_EXECUTION_PRECONDITION_MISSING"
    CONTROLLED_CREDENTIAL_POLICY_UNSAFE = "CONTROLLED_CREDENTIAL_POLICY_UNSAFE"
    CONTROLLED_SECRET_READ_POLICY_UNSAFE = "CONTROLLED_SECRET_READ_POLICY_UNSAFE"
    CONTROLLED_NETWORK_NOT_BLOCKED = "CONTROLLED_NETWORK_NOT_BLOCKED"
    CONTROLLED_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED = "CONTROLLED_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED"
    CONTROLLED_ACCOUNT_READ_ONLY_UNSAFE = "CONTROLLED_ACCOUNT_READ_ONLY_UNSAFE"
    CONTROLLED_MARKET_DATA_READ_ONLY_UNSAFE = "CONTROLLED_MARKET_DATA_READ_ONLY_UNSAFE"
    CONTROLLED_ORDER_BLOCKING_UNSAFE = "CONTROLLED_ORDER_BLOCKING_UNSAFE"
    CONTROLLED_POSITION_MUTATION_BLOCK_UNSAFE = "CONTROLLED_POSITION_MUTATION_BLOCK_UNSAFE"
    CONTROLLED_OBSERVABILITY_MISSING = "CONTROLLED_OBSERVABILITY_MISSING"
    CONTROLLED_JOURNAL_MISSING = "CONTROLLED_JOURNAL_MISSING"
    CONTROLLED_HUMAN_APPROVAL_MISSING = "CONTROLLED_HUMAN_APPROVAL_MISSING"
    CONTROLLED_STOP_CONDITIONS_MISSING = "CONTROLLED_STOP_CONDITIONS_MISSING"
    CONTROLLED_SUCCESS_CRITERIA_MISSING = "CONTROLLED_SUCCESS_CRITERIA_MISSING"
    CONTROLLED_FAILURE_CRITERIA_MISSING = "CONTROLLED_FAILURE_CRITERIA_MISSING"
    CONTROLLED_AUDIT_PLAN_MISSING = "CONTROLLED_AUDIT_PLAN_MISSING"
    CONTROLLED_GO_NO_GO_POLICY_MISSING = "CONTROLLED_GO_NO_GO_POLICY_MISSING"
    CONTROLLED_ABORT_POLICY_MISSING = "CONTROLLED_ABORT_POLICY_MISSING"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE = "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE"


class PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRecommendation(StrEnum):
    HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE = "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE"
    APPROVE_DRY_RUN_EXECUTION_FINAL_SAFETY_GATE_FIRST = "APPROVE_DRY_RUN_EXECUTION_FINAL_SAFETY_GATE_FIRST"
    DEFINE_CONTROLLED_EXECUTION_SCOPE = "DEFINE_CONTROLLED_EXECUTION_SCOPE"
    DEFINE_CONTROLLED_EXECUTION_SEQUENCE = "DEFINE_CONTROLLED_EXECUTION_SEQUENCE"
    DEFINE_CONTROLLED_EXECUTION_PRECONDITIONS = "DEFINE_CONTROLLED_EXECUTION_PRECONDITIONS"
    HARDEN_CONTROLLED_CREDENTIAL_POLICY = "HARDEN_CONTROLLED_CREDENTIAL_POLICY"
    HARDEN_CONTROLLED_NO_SECRET_READ_POLICY = "HARDEN_CONTROLLED_NO_SECRET_READ_POLICY"
    BLOCK_CONTROLLED_NETWORK_TRANSPORT = "BLOCK_CONTROLLED_NETWORK_TRANSPORT"
    BLOCK_CONTROLLED_HTTP_WEBSOCKET_SOCKET = "BLOCK_CONTROLLED_HTTP_WEBSOCKET_SOCKET"
    HARDEN_CONTROLLED_ACCOUNT_READ_ONLY = "HARDEN_CONTROLLED_ACCOUNT_READ_ONLY"
    HARDEN_CONTROLLED_MARKET_DATA_READ_ONLY = "HARDEN_CONTROLLED_MARKET_DATA_READ_ONLY"
    HARDEN_CONTROLLED_ORDER_BLOCKING = "HARDEN_CONTROLLED_ORDER_BLOCKING"
    HARDEN_CONTROLLED_POSITION_MUTATION_BLOCK = "HARDEN_CONTROLLED_POSITION_MUTATION_BLOCK"
    COMPLETE_CONTROLLED_OBSERVABILITY = "COMPLETE_CONTROLLED_OBSERVABILITY"
    COMPLETE_CONTROLLED_JOURNAL = "COMPLETE_CONTROLLED_JOURNAL"
    REQUIRE_CONTROLLED_HUMAN_APPROVAL = "REQUIRE_CONTROLLED_HUMAN_APPROVAL"
    DEFINE_CONTROLLED_STOP_CONDITIONS = "DEFINE_CONTROLLED_STOP_CONDITIONS"
    DEFINE_CONTROLLED_SUCCESS_FAILURE_CRITERIA = "DEFINE_CONTROLLED_SUCCESS_FAILURE_CRITERIA"
    COMPLETE_CONTROLLED_AUDIT_PLAN = "COMPLETE_CONTROLLED_AUDIT_PLAN"
    DEFINE_CONTROLLED_GO_NO_GO_POLICY = "DEFINE_CONTROLLED_GO_NO_GO_POLICY"
    DEFINE_CONTROLLED_ABORT_POLICY = "DEFINE_CONTROLLED_ABORT_POLICY"
    RESTORE_OFFLINE_BOUNDARIES = "RESTORE_OFFLINE_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE = "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE"
    RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PLAN_SUITE = "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PLAN_SUITE"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE = "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE"


@dataclass(frozen=True)
class _ControlledPlanSection:
    name: str = "controlled_plan_section"
    score: int = 0
    defined: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ControlledExecutionScope(_ControlledPlanSection):
    name: str = "controlled_dry_run_execution_scope"
    offline_only: bool = True
    sandbox_only: bool = True
    controlled_plan_only: bool = True
    dry_run_execution_disabled: bool = True


@dataclass(frozen=True)
class ControlledExecutionSequence(_ControlledPlanSection):
    name: str = "controlled_dry_run_execution_sequence"
    sequence_steps_defined: bool = True
    dry_run_not_executed: bool = True
    connection_not_executed: bool = True
    fail_closed: bool = True


@dataclass(frozen=True)
class ControlledExecutionPrecondition(_ControlledPlanSection):
    name: str = "controlled_dry_run_execution_precondition"
    final_safety_gate_required: bool = True
    safety_gate_required: bool = True
    human_approval_required: bool = True
    stop_conditions_required: bool = True


@dataclass(frozen=True)
class ControlledCredentialsReferencePolicy(_ControlledPlanSection):
    name: str = "controlled_credentials_reference_policy"
    reference_only: bool = True
    no_secret_values: bool = True
    no_api_key_read: bool = True
    no_env_var_read: bool = True


@dataclass(frozen=True)
class ControlledNoSecretReadPolicy(_ControlledPlanSection):
    name: str = "controlled_no_secret_read_policy"
    no_api_key_read: bool = True
    no_env_var_read: bool = True
    no_hardcoded_secret: bool = True
    fail_on_secret_read_request: bool = True


@dataclass(frozen=True)
class ControlledNetworkBlockPolicy(_ControlledPlanSection):
    name: str = "controlled_network_block_policy"
    network_execution_blocked: bool = True
    http_blocked: bool = True
    websocket_blocked: bool = True
    socket_blocked: bool = True
    external_api_blocked: bool = True


@dataclass(frozen=True)
class ControlledAccountReadOnlyPolicy(_ControlledPlanSection):
    name: str = "controlled_account_read_only_policy"
    active_account_access_blocked: bool = True
    account_mutations_blocked: bool = True
    schema_only_account_review: bool = True


@dataclass(frozen=True)
class ControlledMarketDataReadOnlyPolicy(_ControlledPlanSection):
    name: str = "controlled_market_data_read_only_policy"
    read_only_market_data_only: bool = True
    live_subscription_blocked: bool = True
    network_request_blocked: bool = True
    schema_or_synthetic_only: bool = True


@dataclass(frozen=True)
class ControlledOrderBlockingPolicy(_ControlledPlanSection):
    name: str = "controlled_order_blocking_policy"
    order_execution_blocked: bool = True
    real_order_blocked: bool = True
    cancel_replace_blocked: bool = True


@dataclass(frozen=True)
class ControlledPositionMutationBlockPolicy(_ControlledPlanSection):
    name: str = "controlled_position_mutation_block_policy"
    position_mutation_blocked: bool = True
    position_request_absent: bool = True
    close_modify_blocked: bool = True


@dataclass(frozen=True)
class ControlledObservabilityPlan(_ControlledPlanSection):
    name: str = "controlled_observability_plan"
    offline_events_defined: bool = True
    connection_attempt_logging_disabled: bool = True
    sensitive_values_redacted: bool = True


@dataclass(frozen=True)
class ControlledJournalPlan(_ControlledPlanSection):
    name: str = "controlled_journal_plan"
    offline_journal_required: bool = True
    sensitive_values_redacted: bool = True
    no_secret_material_logged: bool = True


@dataclass(frozen=True)
class ControlledHumanApprovalPlan(_ControlledPlanSection):
    name: str = "controlled_human_approval_plan"
    human_approval_required: bool = True
    approval_before_safety_gate: bool = True
    final_safety_gate_evidence_required: bool = True


@dataclass(frozen=True)
class ControlledStopConditionPlan(_ControlledPlanSection):
    name: str = "controlled_stop_condition_plan"
    stop_on_secret_read: bool = True
    stop_on_network_request: bool = True
    stop_on_order_or_position_request: bool = True
    stop_on_account_access_request: bool = True


@dataclass(frozen=True)
class ControlledSuccessCriteria(_ControlledPlanSection):
    name: str = "controlled_success_criteria"
    success_requires_no_real_connection: bool = True
    success_requires_all_guards_verified: bool = True
    success_requires_go_no_go_approval: bool = True


@dataclass(frozen=True)
class ControlledFailureCriteria(_ControlledPlanSection):
    name: str = "controlled_failure_criteria"
    failure_on_secret_read: bool = True
    failure_on_network_request: bool = True
    failure_on_order_position_or_account: bool = True


@dataclass(frozen=True)
class ControlledAuditPlan(_ControlledPlanSection):
    name: str = "controlled_audit_plan"
    audit_events_defined: bool = True
    offline_evidence_required: bool = True
    controlled_plan_trace_required: bool = True


@dataclass(frozen=True)
class ControlledGoNoGoPolicy(_ControlledPlanSection):
    name: str = "controlled_go_no_go_policy"
    go_requires_all_sections_ready: bool = True
    no_go_on_any_boundary_violation: bool = True
    human_go_required: bool = True


@dataclass(frozen=True)
class ControlledAbortPolicy(_ControlledPlanSection):
    name: str = "controlled_abort_policy"
    abort_on_secret_read: bool = True
    abort_on_network_request: bool = True
    abort_on_order_position_or_account: bool = True
    abort_on_go_no_go_failure: bool = True


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanScore:
    overall_score: int
    final_safety_gate_score: int
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
    abort_score: int


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanInput:
    paper_broker_read_only_connection_dry_run_execution_final_safety_gate: Any = None
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
    dry_run_execution_final_safety_gate_approved: bool | None = None
    controlled_execution_scope_defined: bool | None = None
    controlled_execution_sequence_defined: bool | None = None
    controlled_execution_preconditions_defined: bool | None = None
    controlled_credentials_reference_policy_defined: bool | None = None
    controlled_credentials_reference_only: bool | None = None
    controlled_no_secret_read_policy_defined: bool | None = None
    controlled_network_block_policy_defined: bool | None = None
    controlled_network_blocked: bool | None = None
    controlled_http_websocket_socket_block_policy_defined: bool | None = None
    controlled_http_blocked: bool | None = None
    controlled_websocket_blocked: bool | None = None
    controlled_socket_blocked: bool | None = None
    controlled_external_api_blocked: bool | None = None
    controlled_account_read_only_policy_defined: bool | None = None
    controlled_active_account_access_blocked: bool | None = None
    controlled_account_mutations_blocked: bool | None = None
    controlled_market_data_read_only_policy_defined: bool | None = None
    controlled_market_data_live_subscription_blocked: bool | None = None
    controlled_market_data_network_request_blocked: bool | None = None
    controlled_order_blocking_policy_defined: bool | None = None
    controlled_order_execution_blocked: bool | None = None
    controlled_cancel_replace_blocked: bool | None = None
    controlled_position_mutation_block_policy_defined: bool | None = None
    controlled_position_mutation_blocked: bool | None = None
    controlled_observability_plan_defined: bool | None = None
    controlled_journal_plan_defined: bool | None = None
    controlled_human_approval_plan_defined: bool | None = None
    controlled_human_approval_required: bool | None = None
    controlled_stop_conditions_plan_defined: bool | None = None
    controlled_success_criteria_defined: bool | None = None
    controlled_failure_criteria_defined: bool | None = None
    controlled_audit_plan_defined: bool | None = None
    controlled_go_no_go_policy_defined: bool | None = None
    controlled_abort_policy_defined: bool | None = None
    paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate_requested: bool | None = False
    offline_mode_enforced: bool | None = None
    sandbox_mode_enforced: bool | None = None
    controlled_plan_only: bool | None = None
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
    final_safety_gate_score: int | None = None
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
    abort_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanResult:
    state: PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanState
    decision: PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanDecision
    controlled_plan_score: int
    score_breakdown: PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanScore
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk, ...] = ()
    recommendations: tuple[PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRecommendation, ...] = ()
    controlled_dry_run_execution_scope: ControlledExecutionScope = field(default_factory=ControlledExecutionScope)
    controlled_dry_run_execution_sequence: ControlledExecutionSequence = field(default_factory=ControlledExecutionSequence)
    controlled_dry_run_execution_precondition: ControlledExecutionPrecondition = field(default_factory=ControlledExecutionPrecondition)
    controlled_credentials_reference_policy: ControlledCredentialsReferencePolicy = field(default_factory=ControlledCredentialsReferencePolicy)
    controlled_no_secret_read_policy: ControlledNoSecretReadPolicy = field(default_factory=ControlledNoSecretReadPolicy)
    controlled_network_block_policy: ControlledNetworkBlockPolicy = field(default_factory=ControlledNetworkBlockPolicy)
    controlled_http_websocket_socket_block_policy: ControlledNetworkBlockPolicy = field(default_factory=lambda: ControlledNetworkBlockPolicy(name="controlled_http_websocket_socket_block_policy"))
    controlled_account_read_only_policy: ControlledAccountReadOnlyPolicy = field(default_factory=ControlledAccountReadOnlyPolicy)
    controlled_market_data_read_only_policy: ControlledMarketDataReadOnlyPolicy = field(default_factory=ControlledMarketDataReadOnlyPolicy)
    controlled_order_blocking_policy: ControlledOrderBlockingPolicy = field(default_factory=ControlledOrderBlockingPolicy)
    controlled_position_mutation_block_policy: ControlledPositionMutationBlockPolicy = field(default_factory=ControlledPositionMutationBlockPolicy)
    controlled_observability_plan: ControlledObservabilityPlan = field(default_factory=ControlledObservabilityPlan)
    controlled_journal_plan: ControlledJournalPlan = field(default_factory=ControlledJournalPlan)
    controlled_human_approval_plan: ControlledHumanApprovalPlan = field(default_factory=ControlledHumanApprovalPlan)
    controlled_stop_conditions_plan: ControlledStopConditionPlan = field(default_factory=ControlledStopConditionPlan)
    controlled_success_criteria: ControlledSuccessCriteria = field(default_factory=ControlledSuccessCriteria)
    controlled_failure_criteria: ControlledFailureCriteria = field(default_factory=ControlledFailureCriteria)
    controlled_audit_plan: ControlledAuditPlan = field(default_factory=ControlledAuditPlan)
    controlled_go_no_go_policy: ControlledGoNoGoPolicy = field(default_factory=ControlledGoNoGoPolicy)
    controlled_abort_policy: ControlledAbortPolicy = field(default_factory=ControlledAbortPolicy)
    offline_only: bool = True
    summary: str = ""
