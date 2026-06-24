"""Models for AGIcore Paper Broker Read-Only Connection Dry Run Controlled Execution Final Plan."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalPlanState(StrEnum):
    NOT_READY = "NOT_READY"
    FINAL_CONTROLLED_EXECUTION_PLAN_INPUT_INVALID = "FINAL_CONTROLLED_EXECUTION_PLAN_INPUT_INVALID"
    FINAL_CONTROLLED_EXECUTION_PLAN_BLOCKED = "FINAL_CONTROLLED_EXECUTION_PLAN_BLOCKED"
    FINAL_CONTROLLED_EXECUTION_PLAN_COMPLETED_WITH_WARNINGS = "FINAL_CONTROLLED_EXECUTION_PLAN_COMPLETED_WITH_WARNINGS"
    FINAL_CONTROLLED_EXECUTION_PLAN_COMPLETED = "FINAL_CONTROLLED_EXECUTION_PLAN_COMPLETED"
    READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_SAFETY_GATE = "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_SAFETY_GATE"


class PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalPlanDecision(StrEnum):
    BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_PLAN = "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_PLAN"
    REQUIRE_CONTROLLED_PREPARATION_REVIEW_FIXES = "REQUIRE_CONTROLLED_PREPARATION_REVIEW_FIXES"
    REQUIRE_FINAL_CONTROLLED_SCOPE_FIXES = "REQUIRE_FINAL_CONTROLLED_SCOPE_FIXES"
    REQUIRE_FINAL_CONTROLLED_SEQUENCE_FIXES = "REQUIRE_FINAL_CONTROLLED_SEQUENCE_FIXES"
    REQUIRE_FINAL_CONTROLLED_PRECONDITION_FIXES = "REQUIRE_FINAL_CONTROLLED_PRECONDITION_FIXES"
    REQUIRE_FINAL_CONTROLLED_CREDENTIAL_POLICY_FIXES = "REQUIRE_FINAL_CONTROLLED_CREDENTIAL_POLICY_FIXES"
    REQUIRE_FINAL_CONTROLLED_NO_SECRET_READ_FIXES = "REQUIRE_FINAL_CONTROLLED_NO_SECRET_READ_FIXES"
    REQUIRE_FINAL_CONTROLLED_NETWORK_BLOCK_FIXES = "REQUIRE_FINAL_CONTROLLED_NETWORK_BLOCK_FIXES"
    REQUIRE_FINAL_CONTROLLED_ACCOUNT_READ_ONLY_FIXES = "REQUIRE_FINAL_CONTROLLED_ACCOUNT_READ_ONLY_FIXES"
    REQUIRE_FINAL_CONTROLLED_MARKET_DATA_READ_ONLY_FIXES = "REQUIRE_FINAL_CONTROLLED_MARKET_DATA_READ_ONLY_FIXES"
    REQUIRE_FINAL_CONTROLLED_ORDER_BLOCKING_FIXES = "REQUIRE_FINAL_CONTROLLED_ORDER_BLOCKING_FIXES"
    REQUIRE_FINAL_CONTROLLED_POSITION_MUTATION_BLOCK_FIXES = "REQUIRE_FINAL_CONTROLLED_POSITION_MUTATION_BLOCK_FIXES"
    REQUIRE_FINAL_CONTROLLED_OBSERVABILITY_FIXES = "REQUIRE_FINAL_CONTROLLED_OBSERVABILITY_FIXES"
    REQUIRE_FINAL_CONTROLLED_JOURNAL_FIXES = "REQUIRE_FINAL_CONTROLLED_JOURNAL_FIXES"
    REQUIRE_FINAL_CONTROLLED_HUMAN_APPROVAL_FIXES = "REQUIRE_FINAL_CONTROLLED_HUMAN_APPROVAL_FIXES"
    REQUIRE_FINAL_CONTROLLED_STOP_CONDITION_FIXES = "REQUIRE_FINAL_CONTROLLED_STOP_CONDITION_FIXES"
    REQUIRE_FINAL_CONTROLLED_SUCCESS_FAILURE_FIXES = "REQUIRE_FINAL_CONTROLLED_SUCCESS_FAILURE_FIXES"
    REQUIRE_FINAL_CONTROLLED_AUDIT_FIXES = "REQUIRE_FINAL_CONTROLLED_AUDIT_FIXES"
    REQUIRE_FINAL_CONTROLLED_GO_NO_GO_FIXES = "REQUIRE_FINAL_CONTROLLED_GO_NO_GO_FIXES"
    REQUIRE_FINAL_CONTROLLED_ABORT_FIXES = "REQUIRE_FINAL_CONTROLLED_ABORT_FIXES"
    REQUIRE_FINAL_CONTROLLED_PROFITABILITY_OBSERVATION_FIXES = "REQUIRE_FINAL_CONTROLLED_PROFITABILITY_OBSERVATION_FIXES"
    REQUIRE_FINAL_CONTROLLED_CONSISTENCY_OBSERVATION_FIXES = "REQUIRE_FINAL_CONTROLLED_CONSISTENCY_OBSERVATION_FIXES"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_PLAN = "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_PLAN"


class PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalPlanRisk(StrEnum):
    CONTROLLED_EXECUTION_PREPARATION_REVIEW_NOT_APPROVED = "CONTROLLED_EXECUTION_PREPARATION_REVIEW_NOT_APPROVED"
    FINAL_CONTROLLED_SCOPE_UNCLEAR = "FINAL_CONTROLLED_SCOPE_UNCLEAR"
    FINAL_CONTROLLED_SEQUENCE_MISSING = "FINAL_CONTROLLED_SEQUENCE_MISSING"
    FINAL_CONTROLLED_PRECONDITION_MISSING = "FINAL_CONTROLLED_PRECONDITION_MISSING"
    FINAL_CONTROLLED_CREDENTIAL_POLICY_UNSAFE = "FINAL_CONTROLLED_CREDENTIAL_POLICY_UNSAFE"
    FINAL_CONTROLLED_SECRET_READ_POLICY_UNSAFE = "FINAL_CONTROLLED_SECRET_READ_POLICY_UNSAFE"
    FINAL_CONTROLLED_NETWORK_NOT_BLOCKED = "FINAL_CONTROLLED_NETWORK_NOT_BLOCKED"
    FINAL_CONTROLLED_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED = "FINAL_CONTROLLED_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED"
    FINAL_CONTROLLED_ACCOUNT_READ_ONLY_UNSAFE = "FINAL_CONTROLLED_ACCOUNT_READ_ONLY_UNSAFE"
    FINAL_CONTROLLED_MARKET_DATA_READ_ONLY_UNSAFE = "FINAL_CONTROLLED_MARKET_DATA_READ_ONLY_UNSAFE"
    FINAL_CONTROLLED_ORDER_BLOCKING_UNSAFE = "FINAL_CONTROLLED_ORDER_BLOCKING_UNSAFE"
    FINAL_CONTROLLED_POSITION_MUTATION_BLOCK_UNSAFE = "FINAL_CONTROLLED_POSITION_MUTATION_BLOCK_UNSAFE"
    FINAL_CONTROLLED_OBSERVABILITY_MISSING = "FINAL_CONTROLLED_OBSERVABILITY_MISSING"
    FINAL_CONTROLLED_JOURNAL_MISSING = "FINAL_CONTROLLED_JOURNAL_MISSING"
    FINAL_CONTROLLED_HUMAN_APPROVAL_MISSING = "FINAL_CONTROLLED_HUMAN_APPROVAL_MISSING"
    FINAL_CONTROLLED_STOP_CONDITIONS_MISSING = "FINAL_CONTROLLED_STOP_CONDITIONS_MISSING"
    FINAL_CONTROLLED_SUCCESS_CRITERIA_MISSING = "FINAL_CONTROLLED_SUCCESS_CRITERIA_MISSING"
    FINAL_CONTROLLED_FAILURE_CRITERIA_MISSING = "FINAL_CONTROLLED_FAILURE_CRITERIA_MISSING"
    FINAL_CONTROLLED_AUDIT_PLAN_MISSING = "FINAL_CONTROLLED_AUDIT_PLAN_MISSING"
    FINAL_CONTROLLED_GO_NO_GO_POLICY_MISSING = "FINAL_CONTROLLED_GO_NO_GO_POLICY_MISSING"
    FINAL_CONTROLLED_ABORT_POLICY_MISSING = "FINAL_CONTROLLED_ABORT_POLICY_MISSING"
    FINAL_CONTROLLED_PROFITABILITY_OBSERVATION_MISSING = "FINAL_CONTROLLED_PROFITABILITY_OBSERVATION_MISSING"
    FINAL_CONTROLLED_CONSISTENCY_OBSERVATION_MISSING = "FINAL_CONTROLLED_CONSISTENCY_OBSERVATION_MISSING"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_SAFETY_GATE = "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_SAFETY_GATE"


class PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalPlanRecommendation(StrEnum):
    HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_SAFETY_GATE = "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_SAFETY_GATE"
    APPROVE_CONTROLLED_EXECUTION_PREPARATION_REVIEW_FIRST = "APPROVE_CONTROLLED_EXECUTION_PREPARATION_REVIEW_FIRST"
    DEFINE_FINAL_CONTROLLED_SCOPE = "DEFINE_FINAL_CONTROLLED_SCOPE"
    DEFINE_FINAL_CONTROLLED_SEQUENCE = "DEFINE_FINAL_CONTROLLED_SEQUENCE"
    DEFINE_FINAL_CONTROLLED_PRECONDITIONS = "DEFINE_FINAL_CONTROLLED_PRECONDITIONS"
    HARDEN_FINAL_CONTROLLED_CREDENTIAL_POLICY = "HARDEN_FINAL_CONTROLLED_CREDENTIAL_POLICY"
    HARDEN_FINAL_CONTROLLED_NO_SECRET_READ_POLICY = "HARDEN_FINAL_CONTROLLED_NO_SECRET_READ_POLICY"
    BLOCK_FINAL_CONTROLLED_NETWORK_TRANSPORT = "BLOCK_FINAL_CONTROLLED_NETWORK_TRANSPORT"
    BLOCK_FINAL_CONTROLLED_HTTP_WEBSOCKET_SOCKET = "BLOCK_FINAL_CONTROLLED_HTTP_WEBSOCKET_SOCKET"
    HARDEN_FINAL_CONTROLLED_ACCOUNT_READ_ONLY = "HARDEN_FINAL_CONTROLLED_ACCOUNT_READ_ONLY"
    HARDEN_FINAL_CONTROLLED_MARKET_DATA_READ_ONLY = "HARDEN_FINAL_CONTROLLED_MARKET_DATA_READ_ONLY"
    HARDEN_FINAL_CONTROLLED_ORDER_BLOCKING = "HARDEN_FINAL_CONTROLLED_ORDER_BLOCKING"
    HARDEN_FINAL_CONTROLLED_POSITION_MUTATION_BLOCK = "HARDEN_FINAL_CONTROLLED_POSITION_MUTATION_BLOCK"
    COMPLETE_FINAL_CONTROLLED_OBSERVABILITY = "COMPLETE_FINAL_CONTROLLED_OBSERVABILITY"
    COMPLETE_FINAL_CONTROLLED_JOURNAL = "COMPLETE_FINAL_CONTROLLED_JOURNAL"
    REQUIRE_FINAL_CONTROLLED_HUMAN_APPROVAL = "REQUIRE_FINAL_CONTROLLED_HUMAN_APPROVAL"
    DEFINE_FINAL_CONTROLLED_STOP_CONDITIONS = "DEFINE_FINAL_CONTROLLED_STOP_CONDITIONS"
    DEFINE_FINAL_CONTROLLED_SUCCESS_FAILURE_CRITERIA = "DEFINE_FINAL_CONTROLLED_SUCCESS_FAILURE_CRITERIA"
    COMPLETE_FINAL_CONTROLLED_AUDIT_PLAN = "COMPLETE_FINAL_CONTROLLED_AUDIT_PLAN"
    DEFINE_FINAL_CONTROLLED_GO_NO_GO_POLICY = "DEFINE_FINAL_CONTROLLED_GO_NO_GO_POLICY"
    DEFINE_FINAL_CONTROLLED_ABORT_POLICY = "DEFINE_FINAL_CONTROLLED_ABORT_POLICY"
    DEFINE_FINAL_CONTROLLED_PROFITABILITY_OBSERVATION = "DEFINE_FINAL_CONTROLLED_PROFITABILITY_OBSERVATION"
    DEFINE_FINAL_CONTROLLED_CONSISTENCY_OBSERVATION = "DEFINE_FINAL_CONTROLLED_CONSISTENCY_OBSERVATION"
    RESTORE_OFFLINE_BOUNDARIES = "RESTORE_OFFLINE_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_SAFETY_GATE = "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_SAFETY_GATE"
    RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_PLAN_SUITE = "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_PLAN_SUITE"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_SAFETY_GATE = "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_SAFETY_GATE"


Risk = PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalPlanRisk


@dataclass(frozen=True)
class _FinalControlledSection:
    name: str = "final_controlled_section"
    score: int = 0
    defined: bool = False
    risks: tuple[Risk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class FinalControlledExecutionScope(_FinalControlledSection):
    name: str = "final_controlled_execution_scope"
    offline_only: bool = True
    sandbox_only: bool = True
    final_plan_only: bool = True
    dry_run_execution_disabled: bool = True


@dataclass(frozen=True)
class FinalControlledExecutionSequence(_FinalControlledSection):
    name: str = "final_controlled_execution_sequence"
    sequence_steps_defined: bool = True
    dry_run_not_executed: bool = True
    connection_not_executed: bool = True
    fail_closed: bool = True


@dataclass(frozen=True)
class FinalControlledExecutionPrecondition(_FinalControlledSection):
    name: str = "final_controlled_execution_precondition"
    preparation_review_required: bool = True
    safety_gate_required: bool = True
    human_approval_required: bool = True
    stop_conditions_required: bool = True


@dataclass(frozen=True)
class FinalControlledCredentialsReferencePolicy(_FinalControlledSection):
    name: str = "final_controlled_credentials_reference_policy"
    reference_only: bool = True
    no_secret_values: bool = True
    no_api_key_read: bool = True
    no_env_var_read: bool = True


@dataclass(frozen=True)
class FinalControlledNoSecretReadPolicy(_FinalControlledSection):
    name: str = "final_controlled_no_secret_read_policy"
    no_api_key_read: bool = True
    no_env_var_read: bool = True
    no_hardcoded_secret: bool = True
    fail_on_secret_read_request: bool = True


@dataclass(frozen=True)
class FinalControlledNetworkBlockPolicy(_FinalControlledSection):
    name: str = "final_controlled_network_block_policy"
    network_execution_blocked: bool = True
    http_blocked: bool = True
    websocket_blocked: bool = True
    socket_blocked: bool = True
    external_api_blocked: bool = True


@dataclass(frozen=True)
class FinalControlledAccountReadOnlyPolicy(_FinalControlledSection):
    name: str = "final_controlled_account_read_only_policy"
    active_account_access_blocked: bool = True
    account_mutations_blocked: bool = True
    schema_only_account_review: bool = True


@dataclass(frozen=True)
class FinalControlledMarketDataReadOnlyPolicy(_FinalControlledSection):
    name: str = "final_controlled_market_data_read_only_policy"
    read_only_market_data_only: bool = True
    live_subscription_blocked: bool = True
    network_request_blocked: bool = True
    schema_or_synthetic_only: bool = True


@dataclass(frozen=True)
class FinalControlledOrderBlockingPolicy(_FinalControlledSection):
    name: str = "final_controlled_order_blocking_policy"
    order_execution_blocked: bool = True
    real_order_blocked: bool = True
    cancel_replace_blocked: bool = True


@dataclass(frozen=True)
class FinalControlledPositionMutationBlockPolicy(_FinalControlledSection):
    name: str = "final_controlled_position_mutation_block_policy"
    position_mutation_blocked: bool = True
    position_request_absent: bool = True
    close_modify_blocked: bool = True


@dataclass(frozen=True)
class FinalControlledObservabilityPlan(_FinalControlledSection):
    name: str = "final_controlled_observability_plan"
    offline_events_defined: bool = True
    connection_attempt_logging_disabled: bool = True
    sensitive_values_redacted: bool = True


@dataclass(frozen=True)
class FinalControlledJournalPlan(_FinalControlledSection):
    name: str = "final_controlled_journal_plan"
    offline_journal_required: bool = True
    sensitive_values_redacted: bool = True
    no_secret_material_logged: bool = True


@dataclass(frozen=True)
class FinalControlledHumanApprovalPlan(_FinalControlledSection):
    name: str = "final_controlled_human_approval_plan"
    human_approval_required: bool = True
    approval_before_safety_gate: bool = True
    preparation_review_evidence_required: bool = True


@dataclass(frozen=True)
class FinalControlledStopConditionPlan(_FinalControlledSection):
    name: str = "final_controlled_stop_condition_plan"
    stop_on_secret_read: bool = True
    stop_on_network_request: bool = True
    stop_on_order_or_position_request: bool = True
    stop_on_account_access_request: bool = True


@dataclass(frozen=True)
class FinalControlledSuccessCriteria(_FinalControlledSection):
    name: str = "final_controlled_success_criteria"
    success_requires_no_real_connection: bool = True
    success_requires_all_guards_verified: bool = True
    success_requires_go_no_go_approval: bool = True


@dataclass(frozen=True)
class FinalControlledFailureCriteria(_FinalControlledSection):
    name: str = "final_controlled_failure_criteria"
    failure_on_secret_read: bool = True
    failure_on_network_request: bool = True
    failure_on_order_position_or_account: bool = True


@dataclass(frozen=True)
class FinalControlledAuditPlan(_FinalControlledSection):
    name: str = "final_controlled_audit_plan"
    audit_events_defined: bool = True
    offline_evidence_required: bool = True
    final_plan_trace_required: bool = True


@dataclass(frozen=True)
class FinalControlledGoNoGoPolicy(_FinalControlledSection):
    name: str = "final_controlled_go_no_go_policy"
    go_requires_all_sections_ready: bool = True
    no_go_on_any_boundary_violation: bool = True
    human_go_required: bool = True


@dataclass(frozen=True)
class FinalControlledAbortPolicy(_FinalControlledSection):
    name: str = "final_controlled_abort_policy"
    abort_on_boundary_violation: bool = True
    abort_on_secret_read_request: bool = True
    abort_on_network_or_order_request: bool = True


@dataclass(frozen=True)
class FinalControlledProfitabilityObservationPolicy(_FinalControlledSection):
    name: str = "final_controlled_profitability_observation_policy"
    observation_only: bool = True
    no_profit_promise: bool = True
    synthetic_or_paper_metrics_only: bool = True
    no_trading_decision_from_observation: bool = True


@dataclass(frozen=True)
class FinalControlledConsistencyObservationPolicy(_FinalControlledSection):
    name: str = "final_controlled_consistency_observation_policy"
    observation_only: bool = True
    deterministic_checks_required: bool = True
    no_runtime_adaptation: bool = True
    repeated_result_review_required: bool = True


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalPlanScore:
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
    abort_score: int
    profitability_observation_score: int
    consistency_observation_score: int


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalPlanInput:
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
    controlled_execution_preparation_review_approved: bool | None = None
    final_controlled_scope_defined: bool | None = None
    final_controlled_sequence_defined: bool | None = None
    final_controlled_preconditions_defined: bool | None = None
    final_controlled_credentials_reference_policy_defined: bool | None = None
    final_controlled_credentials_reference_only: bool | None = None
    final_controlled_no_secret_read_policy_defined: bool | None = None
    final_controlled_network_block_policy_defined: bool | None = None
    final_controlled_network_blocked: bool | None = None
    final_controlled_http_websocket_socket_block_policy_defined: bool | None = None
    final_controlled_http_blocked: bool | None = None
    final_controlled_websocket_blocked: bool | None = None
    final_controlled_socket_blocked: bool | None = None
    final_controlled_external_api_blocked: bool | None = None
    final_controlled_account_read_only_policy_defined: bool | None = None
    final_controlled_active_account_access_blocked: bool | None = None
    final_controlled_account_mutations_blocked: bool | None = None
    final_controlled_market_data_read_only_policy_defined: bool | None = None
    final_controlled_market_data_live_subscription_blocked: bool | None = None
    final_controlled_market_data_network_request_blocked: bool | None = None
    final_controlled_order_blocking_policy_defined: bool | None = None
    final_controlled_order_execution_blocked: bool | None = None
    final_controlled_cancel_replace_blocked: bool | None = None
    final_controlled_position_mutation_block_policy_defined: bool | None = None
    final_controlled_position_mutation_blocked: bool | None = None
    final_controlled_observability_plan_defined: bool | None = None
    final_controlled_journal_plan_defined: bool | None = None
    final_controlled_human_approval_plan_defined: bool | None = None
    final_controlled_human_approval_required: bool | None = None
    final_controlled_stop_conditions_plan_defined: bool | None = None
    final_controlled_success_criteria_defined: bool | None = None
    final_controlled_failure_criteria_defined: bool | None = None
    final_controlled_audit_plan_defined: bool | None = None
    final_controlled_go_no_go_policy_defined: bool | None = None
    final_controlled_abort_policy_defined: bool | None = None
    final_controlled_profitability_observation_policy_defined: bool | None = None
    final_controlled_consistency_observation_policy_defined: bool | None = None
    paper_broker_read_only_connection_dry_run_controlled_execution_final_safety_gate_requested: bool | None = False
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
    abort_score: int | None = None
    profitability_observation_score: int | None = None
    consistency_observation_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalPlanResult:
    state: PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalPlanState
    decision: PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalPlanDecision
    final_plan_score: int
    score_breakdown: PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalPlanScore
    risks: tuple[Risk, ...] = ()
    recommendations: tuple[PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalPlanRecommendation, ...] = ()
    final_controlled_execution_scope: FinalControlledExecutionScope = field(default_factory=FinalControlledExecutionScope)
    final_controlled_execution_sequence: FinalControlledExecutionSequence = field(default_factory=FinalControlledExecutionSequence)
    final_controlled_execution_precondition: FinalControlledExecutionPrecondition = field(default_factory=FinalControlledExecutionPrecondition)
    final_controlled_credentials_reference_policy: FinalControlledCredentialsReferencePolicy = field(default_factory=FinalControlledCredentialsReferencePolicy)
    final_controlled_no_secret_read_policy: FinalControlledNoSecretReadPolicy = field(default_factory=FinalControlledNoSecretReadPolicy)
    final_controlled_network_block_policy: FinalControlledNetworkBlockPolicy = field(default_factory=FinalControlledNetworkBlockPolicy)
    final_controlled_http_websocket_socket_block_policy: FinalControlledNetworkBlockPolicy = field(default_factory=lambda: FinalControlledNetworkBlockPolicy(name="final_controlled_http_websocket_socket_block_policy"))
    final_controlled_account_read_only_policy: FinalControlledAccountReadOnlyPolicy = field(default_factory=FinalControlledAccountReadOnlyPolicy)
    final_controlled_market_data_read_only_policy: FinalControlledMarketDataReadOnlyPolicy = field(default_factory=FinalControlledMarketDataReadOnlyPolicy)
    final_controlled_order_blocking_policy: FinalControlledOrderBlockingPolicy = field(default_factory=FinalControlledOrderBlockingPolicy)
    final_controlled_position_mutation_block_policy: FinalControlledPositionMutationBlockPolicy = field(default_factory=FinalControlledPositionMutationBlockPolicy)
    final_controlled_observability_plan: FinalControlledObservabilityPlan = field(default_factory=FinalControlledObservabilityPlan)
    final_controlled_journal_plan: FinalControlledJournalPlan = field(default_factory=FinalControlledJournalPlan)
    final_controlled_human_approval_plan: FinalControlledHumanApprovalPlan = field(default_factory=FinalControlledHumanApprovalPlan)
    final_controlled_stop_conditions_plan: FinalControlledStopConditionPlan = field(default_factory=FinalControlledStopConditionPlan)
    final_controlled_success_criteria: FinalControlledSuccessCriteria = field(default_factory=FinalControlledSuccessCriteria)
    final_controlled_failure_criteria: FinalControlledFailureCriteria = field(default_factory=FinalControlledFailureCriteria)
    final_controlled_audit_plan: FinalControlledAuditPlan = field(default_factory=FinalControlledAuditPlan)
    final_controlled_go_no_go_policy: FinalControlledGoNoGoPolicy = field(default_factory=FinalControlledGoNoGoPolicy)
    final_controlled_abort_policy: FinalControlledAbortPolicy = field(default_factory=FinalControlledAbortPolicy)
    final_controlled_profitability_observation_policy: FinalControlledProfitabilityObservationPolicy = field(default_factory=FinalControlledProfitabilityObservationPolicy)
    final_controlled_consistency_observation_policy: FinalControlledConsistencyObservationPolicy = field(default_factory=FinalControlledConsistencyObservationPolicy)
    offline_only: bool = True
    summary: str = ""