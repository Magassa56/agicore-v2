"""Models for AGIcore Paper Broker Read-Only Connection Dry Run Execution Plan."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerReadOnlyConnectionDryRunExecutionPlanState(StrEnum):
    NOT_READY = "NOT_READY"
    DRY_RUN_EXECUTION_PLAN_INPUT_INVALID = "DRY_RUN_EXECUTION_PLAN_INPUT_INVALID"
    DRY_RUN_EXECUTION_PLAN_BLOCKED = "DRY_RUN_EXECUTION_PLAN_BLOCKED"
    DRY_RUN_EXECUTION_PLAN_COMPLETED_WITH_WARNINGS = "DRY_RUN_EXECUTION_PLAN_COMPLETED_WITH_WARNINGS"
    DRY_RUN_EXECUTION_PLAN_COMPLETED = "DRY_RUN_EXECUTION_PLAN_COMPLETED"
    READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE = (
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE"
    )


class PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision(StrEnum):
    BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN = (
        "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN"
    )
    REQUIRE_DRY_RUN_PREPARATION_REVIEW_FIXES = "REQUIRE_DRY_RUN_PREPARATION_REVIEW_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_SCOPE_FIXES = "REQUIRE_DRY_RUN_EXECUTION_SCOPE_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_SEQUENCE_FIXES = "REQUIRE_DRY_RUN_EXECUTION_SEQUENCE_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_PRECONDITION_FIXES = "REQUIRE_DRY_RUN_EXECUTION_PRECONDITION_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_CREDENTIAL_POLICY_FIXES = "REQUIRE_DRY_RUN_EXECUTION_CREDENTIAL_POLICY_FIXES"
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
    REQUIRE_DRY_RUN_EXECUTION_OBSERVABILITY_FIXES = "REQUIRE_DRY_RUN_EXECUTION_OBSERVABILITY_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_JOURNAL_FIXES = "REQUIRE_DRY_RUN_EXECUTION_JOURNAL_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_HUMAN_APPROVAL_FIXES = "REQUIRE_DRY_RUN_EXECUTION_HUMAN_APPROVAL_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_STOP_CONDITION_FIXES = "REQUIRE_DRY_RUN_EXECUTION_STOP_CONDITION_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_SUCCESS_FAILURE_FIXES = "REQUIRE_DRY_RUN_EXECUTION_SUCCESS_FAILURE_FIXES"
    REQUIRE_DRY_RUN_EXECUTION_AUDIT_FIXES = "REQUIRE_DRY_RUN_EXECUTION_AUDIT_FIXES"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN = (
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN"
    )


class PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk(StrEnum):
    DRY_RUN_PREPARATION_REVIEW_NOT_APPROVED = "DRY_RUN_PREPARATION_REVIEW_NOT_APPROVED"
    DRY_RUN_EXECUTION_SCOPE_UNCLEAR = "DRY_RUN_EXECUTION_SCOPE_UNCLEAR"
    DRY_RUN_EXECUTION_SEQUENCE_MISSING = "DRY_RUN_EXECUTION_SEQUENCE_MISSING"
    DRY_RUN_EXECUTION_PRECONDITION_MISSING = "DRY_RUN_EXECUTION_PRECONDITION_MISSING"
    DRY_RUN_EXECUTION_CREDENTIAL_POLICY_UNSAFE = "DRY_RUN_EXECUTION_CREDENTIAL_POLICY_UNSAFE"
    DRY_RUN_EXECUTION_SECRET_READ_POLICY_UNSAFE = "DRY_RUN_EXECUTION_SECRET_READ_POLICY_UNSAFE"
    DRY_RUN_EXECUTION_NETWORK_NOT_BLOCKED = "DRY_RUN_EXECUTION_NETWORK_NOT_BLOCKED"
    DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED = "DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED"
    DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_UNSAFE = "DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_UNSAFE"
    DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_UNSAFE = "DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_UNSAFE"
    DRY_RUN_EXECUTION_ORDER_BLOCKING_UNSAFE = "DRY_RUN_EXECUTION_ORDER_BLOCKING_UNSAFE"
    DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_UNSAFE = "DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_UNSAFE"
    DRY_RUN_EXECUTION_OBSERVABILITY_MISSING = "DRY_RUN_EXECUTION_OBSERVABILITY_MISSING"
    DRY_RUN_EXECUTION_JOURNAL_MISSING = "DRY_RUN_EXECUTION_JOURNAL_MISSING"
    DRY_RUN_EXECUTION_HUMAN_APPROVAL_MISSING = "DRY_RUN_EXECUTION_HUMAN_APPROVAL_MISSING"
    DRY_RUN_EXECUTION_STOP_CONDITIONS_MISSING = "DRY_RUN_EXECUTION_STOP_CONDITIONS_MISSING"
    DRY_RUN_EXECUTION_SUCCESS_CRITERIA_MISSING = "DRY_RUN_EXECUTION_SUCCESS_CRITERIA_MISSING"
    DRY_RUN_EXECUTION_FAILURE_CRITERIA_MISSING = "DRY_RUN_EXECUTION_FAILURE_CRITERIA_MISSING"
    DRY_RUN_EXECUTION_AUDIT_PLAN_MISSING = "DRY_RUN_EXECUTION_AUDIT_PLAN_MISSING"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE = (
        "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE"
    )


class PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation(StrEnum):
    HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE = (
        "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE"
    )
    APPROVE_DRY_RUN_PREPARATION_REVIEW_FIRST = "APPROVE_DRY_RUN_PREPARATION_REVIEW_FIRST"
    DEFINE_DRY_RUN_EXECUTION_SCOPE = "DEFINE_DRY_RUN_EXECUTION_SCOPE"
    DEFINE_DRY_RUN_EXECUTION_SEQUENCE = "DEFINE_DRY_RUN_EXECUTION_SEQUENCE"
    DEFINE_DRY_RUN_EXECUTION_PRECONDITIONS = "DEFINE_DRY_RUN_EXECUTION_PRECONDITIONS"
    HARDEN_DRY_RUN_EXECUTION_CREDENTIAL_POLICY = "HARDEN_DRY_RUN_EXECUTION_CREDENTIAL_POLICY"
    HARDEN_DRY_RUN_EXECUTION_NO_SECRET_READ_POLICY = "HARDEN_DRY_RUN_EXECUTION_NO_SECRET_READ_POLICY"
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
    DEFINE_DRY_RUN_EXECUTION_SUCCESS_FAILURE_CRITERIA = "DEFINE_DRY_RUN_EXECUTION_SUCCESS_FAILURE_CRITERIA"
    DEFINE_DRY_RUN_EXECUTION_AUDIT_PLAN = "DEFINE_DRY_RUN_EXECUTION_AUDIT_PLAN"
    RESTORE_OFFLINE_BOUNDARIES = "RESTORE_OFFLINE_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE = (
        "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE"
    )
    RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN_SUITE = (
        "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN_SUITE"
    )
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE = (
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE"
    )


@dataclass(frozen=True)
class DryRunExecutionScope:
    name: str = "dry_run_execution_scope"
    score: int = 0
    defined: bool = False
    plan_only: bool = True
    offline_only: bool = True
    read_only_only: bool = True
    no_real_execution: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionSequence:
    name: str = "dry_run_execution_sequence"
    score: int = 0
    defined: bool = False
    dry_run_not_executed: bool = True
    connection_not_executed: bool = True
    steps: tuple[str, ...] = ()
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionPrecondition:
    name: str = "dry_run_execution_preconditions"
    score: int = 0
    defined: bool = False
    preparation_review_required: bool = True
    safety_gate_required_next: bool = True
    fail_closed: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionCredentialsReferencePolicy:
    name: str = "dry_run_execution_credentials_reference_policy"
    score: int = 0
    defined: bool = False
    reference_only: bool = True
    no_secret_values: bool = True
    no_api_key_read: bool = True
    no_env_var_read: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionNoSecretReadPolicy:
    name: str = "dry_run_execution_no_secret_read_policy"
    score: int = 0
    defined: bool = False
    policy_enforced: bool = False
    no_api_key_read: bool = True
    no_env_var_read: bool = True
    no_hardcoded_secret: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionNetworkBlockPolicy:
    name: str = "dry_run_execution_network_block_policy"
    score: int = 0
    defined: bool = False
    network_execution_blocked: bool = True
    http_blocked: bool = True
    websocket_blocked: bool = True
    socket_blocked: bool = True
    external_api_blocked: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionAccountReadOnlyPolicy:
    name: str = "dry_run_execution_account_read_only_policy"
    score: int = 0
    defined: bool = False
    active_account_access_blocked: bool = True
    account_mutations_blocked: bool = True
    schema_only_account_review: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionMarketDataReadOnlyPolicy:
    name: str = "dry_run_execution_market_data_read_only_policy"
    score: int = 0
    defined: bool = False
    read_only_market_data_only: bool = True
    live_subscription_blocked: bool = True
    network_request_blocked: bool = True
    schema_or_synthetic_only: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionOrderBlockingPolicy:
    name: str = "dry_run_execution_order_blocking_policy"
    score: int = 0
    defined: bool = False
    order_execution_blocked: bool = True
    real_order_blocked: bool = True
    cancel_replace_blocked: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionPositionMutationBlockPolicy:
    name: str = "dry_run_execution_position_mutation_block_policy"
    score: int = 0
    defined: bool = False
    position_mutation_blocked: bool = True
    position_request_absent: bool = True
    close_modify_blocked: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionObservabilityPlan:
    name: str = "dry_run_execution_observability_plan"
    score: int = 0
    defined: bool = False
    offline_events_defined: bool = True
    connection_attempt_logging_disabled: bool = True
    sensitive_values_redacted: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionJournalPlan:
    name: str = "dry_run_execution_journal_plan"
    score: int = 0
    defined: bool = False
    offline_journal_required: bool = True
    sensitive_values_redacted: bool = True
    no_secret_material_logged: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionHumanApprovalPlan:
    name: str = "dry_run_execution_human_approval_plan"
    score: int = 0
    defined: bool = False
    human_approval_required: bool = True
    approval_before_safety_gate: bool = True
    preparation_review_evidence_required: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionStopConditionPlan:
    name: str = "dry_run_execution_stop_conditions_plan"
    score: int = 0
    defined: bool = False
    stop_on_secret_read: bool = True
    stop_on_network_request: bool = True
    stop_on_order_or_position_request: bool = True
    stop_on_account_access_request: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionSuccessCriteria:
    name: str = "dry_run_execution_success_criteria"
    score: int = 0
    defined: bool = False
    requires_no_real_connection: bool = True
    requires_no_secret_read: bool = True
    requires_all_guards_verified: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionFailureCriteria:
    name: str = "dry_run_execution_failure_criteria"
    score: int = 0
    defined: bool = False
    failure_on_secret_network_order_position_or_account: bool = True
    failure_on_data_access: bool = True
    failure_on_real_execution: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunExecutionAuditPlan:
    name: str = "dry_run_execution_audit_plan"
    score: int = 0
    defined: bool = False
    audit_events_defined: bool = True
    offline_evidence_required: bool = True
    next_safety_gate_trace_required: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunExecutionPlanScore:
    overall_score: int
    preparation_review_score: int
    scope_score: int
    sequence_score: int
    precondition_score: int
    credential_policy_score: int
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
    success_criteria_score: int
    failure_criteria_score: int
    audit_plan_score: int


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput:
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
    dry_run_preparation_review_approved: bool | None = None
    dry_run_execution_scope_defined: bool | None = None
    dry_run_execution_sequence_defined: bool | None = None
    dry_run_execution_preconditions_defined: bool | None = None
    dry_run_execution_credentials_policy_defined: bool | None = None
    dry_run_execution_credentials_reference_only: bool | None = None
    dry_run_execution_no_secret_read_policy_defined: bool | None = None
    dry_run_execution_no_secret_read_enforced: bool | None = None
    dry_run_execution_network_block_policy_defined: bool | None = None
    dry_run_execution_network_blocked: bool | None = None
    dry_run_execution_http_websocket_socket_block_policy_defined: bool | None = None
    dry_run_execution_http_blocked: bool | None = None
    dry_run_execution_websocket_blocked: bool | None = None
    dry_run_execution_socket_blocked: bool | None = None
    dry_run_execution_external_api_blocked: bool | None = None
    dry_run_execution_account_read_only_policy_defined: bool | None = None
    dry_run_execution_account_access_blocked: bool | None = None
    dry_run_execution_account_mutations_blocked: bool | None = None
    dry_run_execution_market_data_read_only_policy_defined: bool | None = None
    dry_run_execution_market_data_live_subscription_blocked: bool | None = None
    dry_run_execution_market_data_network_request_blocked: bool | None = None
    dry_run_execution_order_blocking_policy_defined: bool | None = None
    dry_run_execution_order_execution_blocked: bool | None = None
    dry_run_execution_cancel_replace_blocked: bool | None = None
    dry_run_execution_position_mutation_block_policy_defined: bool | None = None
    dry_run_execution_position_mutation_blocked: bool | None = None
    dry_run_execution_observability_plan_defined: bool | None = None
    dry_run_execution_journal_plan_defined: bool | None = None
    dry_run_execution_human_approval_plan_defined: bool | None = None
    dry_run_execution_human_approval_required: bool | None = None
    dry_run_execution_stop_conditions_plan_defined: bool | None = None
    dry_run_execution_success_criteria_defined: bool | None = None
    dry_run_execution_failure_criteria_defined: bool | None = None
    dry_run_execution_audit_plan_defined: bool | None = None
    paper_broker_read_only_connection_dry_run_execution_safety_gate_requested: bool | None = False
    offline_mode_enforced: bool | None = None
    sandbox_mode_enforced: bool | None = None
    plan_only: bool | None = None
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
    credential_policy_score: int | None = None
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
    success_criteria_score: int | None = None
    failure_criteria_score: int | None = None
    audit_plan_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunExecutionPlanResult:
    state: PaperBrokerReadOnlyConnectionDryRunExecutionPlanState
    decision: PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision
    execution_plan_score: int
    score_breakdown: PaperBrokerReadOnlyConnectionDryRunExecutionPlanScore
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk, ...] = ()
    recommendations: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation, ...] = ()
    dry_run_execution_scope: DryRunExecutionScope = field(default_factory=DryRunExecutionScope)
    dry_run_execution_sequence: DryRunExecutionSequence = field(default_factory=DryRunExecutionSequence)
    dry_run_execution_preconditions: DryRunExecutionPrecondition = field(default_factory=DryRunExecutionPrecondition)
    dry_run_execution_credentials_reference_policy: DryRunExecutionCredentialsReferencePolicy = field(
        default_factory=DryRunExecutionCredentialsReferencePolicy
    )
    dry_run_execution_no_secret_read_policy: DryRunExecutionNoSecretReadPolicy = field(
        default_factory=DryRunExecutionNoSecretReadPolicy
    )
    dry_run_execution_network_block_policy: DryRunExecutionNetworkBlockPolicy = field(
        default_factory=DryRunExecutionNetworkBlockPolicy
    )
    dry_run_execution_http_websocket_socket_block_policy: DryRunExecutionNetworkBlockPolicy = field(
        default_factory=lambda: DryRunExecutionNetworkBlockPolicy(
            name="dry_run_execution_http_websocket_socket_block_policy"
        )
    )
    dry_run_execution_account_read_only_policy: DryRunExecutionAccountReadOnlyPolicy = field(
        default_factory=DryRunExecutionAccountReadOnlyPolicy
    )
    dry_run_execution_market_data_read_only_policy: DryRunExecutionMarketDataReadOnlyPolicy = field(
        default_factory=DryRunExecutionMarketDataReadOnlyPolicy
    )
    dry_run_execution_order_blocking_policy: DryRunExecutionOrderBlockingPolicy = field(
        default_factory=DryRunExecutionOrderBlockingPolicy
    )
    dry_run_execution_position_mutation_block_policy: DryRunExecutionPositionMutationBlockPolicy = field(
        default_factory=DryRunExecutionPositionMutationBlockPolicy
    )
    dry_run_execution_observability_plan: DryRunExecutionObservabilityPlan = field(
        default_factory=DryRunExecutionObservabilityPlan
    )
    dry_run_execution_journal_plan: DryRunExecutionJournalPlan = field(default_factory=DryRunExecutionJournalPlan)
    dry_run_execution_human_approval_plan: DryRunExecutionHumanApprovalPlan = field(
        default_factory=DryRunExecutionHumanApprovalPlan
    )
    dry_run_execution_stop_conditions_plan: DryRunExecutionStopConditionPlan = field(
        default_factory=DryRunExecutionStopConditionPlan
    )
    dry_run_execution_success_criteria: DryRunExecutionSuccessCriteria = field(
        default_factory=DryRunExecutionSuccessCriteria
    )
    dry_run_execution_failure_criteria: DryRunExecutionFailureCriteria = field(
        default_factory=DryRunExecutionFailureCriteria
    )
    dry_run_execution_audit_plan: DryRunExecutionAuditPlan = field(default_factory=DryRunExecutionAuditPlan)
    offline_only: bool = True
    summary: str = ""
