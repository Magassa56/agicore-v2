"""Models for the AGIcore Paper Broker Read-Only Connection Dry Run Plan layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerReadOnlyConnectionDryRunPlanState(StrEnum):
    NOT_READY = "NOT_READY"
    DRY_RUN_PLAN_INPUT_INVALID = "DRY_RUN_PLAN_INPUT_INVALID"
    DRY_RUN_PLAN_BLOCKED = "DRY_RUN_PLAN_BLOCKED"
    DRY_RUN_PLAN_COMPLETED_WITH_WARNINGS = "DRY_RUN_PLAN_COMPLETED_WITH_WARNINGS"
    DRY_RUN_PLAN_COMPLETED = "DRY_RUN_PLAN_COMPLETED"
    READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE = (
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE"
    )


class PaperBrokerReadOnlyConnectionDryRunPlanDecision(StrEnum):
    BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN = "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN"
    REQUIRE_CONNECTION_PREPARATION_REVIEW_FIXES = "REQUIRE_CONNECTION_PREPARATION_REVIEW_FIXES"
    REQUIRE_DRY_RUN_SCOPE_FIXES = "REQUIRE_DRY_RUN_SCOPE_FIXES"
    REQUIRE_DRY_RUN_BOUNDARY_FIXES = "REQUIRE_DRY_RUN_BOUNDARY_FIXES"
    REQUIRE_DRY_RUN_PRECONDITION_FIXES = "REQUIRE_DRY_RUN_PRECONDITION_FIXES"
    REQUIRE_DRY_RUN_CREDENTIAL_POLICY_FIXES = "REQUIRE_DRY_RUN_CREDENTIAL_POLICY_FIXES"
    REQUIRE_DRY_RUN_NO_SECRET_READ_FIXES = "REQUIRE_DRY_RUN_NO_SECRET_READ_FIXES"
    REQUIRE_DRY_RUN_NETWORK_BLOCK_FIXES = "REQUIRE_DRY_RUN_NETWORK_BLOCK_FIXES"
    REQUIRE_DRY_RUN_ACCOUNT_READ_ONLY_FIXES = "REQUIRE_DRY_RUN_ACCOUNT_READ_ONLY_FIXES"
    REQUIRE_DRY_RUN_MARKET_DATA_READ_ONLY_FIXES = "REQUIRE_DRY_RUN_MARKET_DATA_READ_ONLY_FIXES"
    REQUIRE_DRY_RUN_ORDER_BLOCKING_FIXES = "REQUIRE_DRY_RUN_ORDER_BLOCKING_FIXES"
    REQUIRE_DRY_RUN_POSITION_MUTATION_BLOCK_FIXES = "REQUIRE_DRY_RUN_POSITION_MUTATION_BLOCK_FIXES"
    REQUIRE_DRY_RUN_OBSERVABILITY_FIXES = "REQUIRE_DRY_RUN_OBSERVABILITY_FIXES"
    REQUIRE_DRY_RUN_JOURNAL_FIXES = "REQUIRE_DRY_RUN_JOURNAL_FIXES"
    REQUIRE_DRY_RUN_HUMAN_APPROVAL_FIXES = "REQUIRE_DRY_RUN_HUMAN_APPROVAL_FIXES"
    REQUIRE_DRY_RUN_STOP_CONDITION_FIXES = "REQUIRE_DRY_RUN_STOP_CONDITION_FIXES"
    REQUIRE_DRY_RUN_SUCCESS_FAILURE_CRITERIA_FIXES = "REQUIRE_DRY_RUN_SUCCESS_FAILURE_CRITERIA_FIXES"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN = (
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN"
    )


class PaperBrokerReadOnlyConnectionDryRunPlanRisk(StrEnum):
    CONNECTION_PREPARATION_REVIEW_NOT_APPROVED = "CONNECTION_PREPARATION_REVIEW_NOT_APPROVED"
    DRY_RUN_SCOPE_UNCLEAR = "DRY_RUN_SCOPE_UNCLEAR"
    DRY_RUN_ENVIRONMENT_BOUNDARY_MISSING = "DRY_RUN_ENVIRONMENT_BOUNDARY_MISSING"
    DRY_RUN_PRECONDITION_MISSING = "DRY_RUN_PRECONDITION_MISSING"
    DRY_RUN_CREDENTIAL_POLICY_UNSAFE = "DRY_RUN_CREDENTIAL_POLICY_UNSAFE"
    DRY_RUN_SECRET_READ_POLICY_UNSAFE = "DRY_RUN_SECRET_READ_POLICY_UNSAFE"
    DRY_RUN_NETWORK_NOT_BLOCKED = "DRY_RUN_NETWORK_NOT_BLOCKED"
    DRY_RUN_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED = "DRY_RUN_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED"
    DRY_RUN_ACCOUNT_READ_ONLY_UNSAFE = "DRY_RUN_ACCOUNT_READ_ONLY_UNSAFE"
    DRY_RUN_MARKET_DATA_READ_ONLY_UNSAFE = "DRY_RUN_MARKET_DATA_READ_ONLY_UNSAFE"
    DRY_RUN_ORDER_BLOCKING_UNSAFE = "DRY_RUN_ORDER_BLOCKING_UNSAFE"
    DRY_RUN_POSITION_MUTATION_BLOCK_UNSAFE = "DRY_RUN_POSITION_MUTATION_BLOCK_UNSAFE"
    DRY_RUN_OBSERVABILITY_PLAN_MISSING = "DRY_RUN_OBSERVABILITY_PLAN_MISSING"
    DRY_RUN_JOURNAL_PLAN_MISSING = "DRY_RUN_JOURNAL_PLAN_MISSING"
    DRY_RUN_HUMAN_APPROVAL_MISSING = "DRY_RUN_HUMAN_APPROVAL_MISSING"
    DRY_RUN_STOP_CONDITIONS_MISSING = "DRY_RUN_STOP_CONDITIONS_MISSING"
    DRY_RUN_SUCCESS_CRITERIA_MISSING = "DRY_RUN_SUCCESS_CRITERIA_MISSING"
    DRY_RUN_FAILURE_CRITERIA_MISSING = "DRY_RUN_FAILURE_CRITERIA_MISSING"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE = (
        "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE"
    )


class PaperBrokerReadOnlyConnectionDryRunPlanRecommendation(StrEnum):
    HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE = (
        "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE"
    )
    APPROVE_CONNECTION_PREPARATION_REVIEW_FIRST = "APPROVE_CONNECTION_PREPARATION_REVIEW_FIRST"
    DEFINE_DRY_RUN_SCOPE = "DEFINE_DRY_RUN_SCOPE"
    DEFINE_DRY_RUN_ENVIRONMENT_BOUNDARIES = "DEFINE_DRY_RUN_ENVIRONMENT_BOUNDARIES"
    DEFINE_DRY_RUN_PRECONDITIONS = "DEFINE_DRY_RUN_PRECONDITIONS"
    HARDEN_DRY_RUN_CREDENTIAL_POLICY = "HARDEN_DRY_RUN_CREDENTIAL_POLICY"
    HARDEN_DRY_RUN_NO_SECRET_READ_POLICY = "HARDEN_DRY_RUN_NO_SECRET_READ_POLICY"
    BLOCK_DRY_RUN_NETWORK = "BLOCK_DRY_RUN_NETWORK"
    BLOCK_DRY_RUN_HTTP_WEBSOCKET_SOCKET = "BLOCK_DRY_RUN_HTTP_WEBSOCKET_SOCKET"
    HARDEN_DRY_RUN_ACCOUNT_READ_ONLY = "HARDEN_DRY_RUN_ACCOUNT_READ_ONLY"
    HARDEN_DRY_RUN_MARKET_DATA_READ_ONLY = "HARDEN_DRY_RUN_MARKET_DATA_READ_ONLY"
    HARDEN_DRY_RUN_ORDER_BLOCKING = "HARDEN_DRY_RUN_ORDER_BLOCKING"
    HARDEN_DRY_RUN_POSITION_MUTATION_BLOCK = "HARDEN_DRY_RUN_POSITION_MUTATION_BLOCK"
    DEFINE_DRY_RUN_OBSERVABILITY = "DEFINE_DRY_RUN_OBSERVABILITY"
    DEFINE_DRY_RUN_JOURNAL = "DEFINE_DRY_RUN_JOURNAL"
    REQUIRE_DRY_RUN_HUMAN_APPROVAL = "REQUIRE_DRY_RUN_HUMAN_APPROVAL"
    DEFINE_DRY_RUN_STOP_CONDITIONS = "DEFINE_DRY_RUN_STOP_CONDITIONS"
    DEFINE_DRY_RUN_SUCCESS_FAILURE_CRITERIA = "DEFINE_DRY_RUN_SUCCESS_FAILURE_CRITERIA"
    RESTORE_OFFLINE_BOUNDARIES = "RESTORE_OFFLINE_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE = (
        "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE"
    )
    RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN_SUITE = (
        "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN_SUITE"
    )
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE = (
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE"
    )


@dataclass(frozen=True)
class DryRunScope:
    name: str = "dry_run_scope"
    score: int = 0
    defined: bool = False
    plan_only: bool = True
    read_only_only: bool = True
    dry_run_not_executed: bool = True
    allowed_actions: tuple[str, ...] = ()
    prohibited_actions: tuple[str, ...] = ()
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunEnvironmentBoundary:
    name: str = "dry_run_environment_boundaries"
    score: int = 0
    defined: bool = False
    offline_only: bool = True
    sandbox_only: bool = True
    broker_connection_disabled: bool = True
    network_transport_blocked: bool = True
    data_access_blocked: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunPrecondition:
    name: str = "dry_run_preconditions"
    score: int = 0
    defined: bool = False
    preparation_review_required: bool = True
    human_approval_required: bool = True
    safety_gate_required: bool = True
    stop_conditions_required: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunCredentialsReferencePolicy:
    name: str = "dry_run_credentials_reference_policy"
    score: int = 0
    defined: bool = False
    reference_only: bool = True
    no_secret_values: bool = True
    no_api_key_read: bool = True
    no_env_var_read: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunNoSecretReadPolicy:
    name: str = "dry_run_no_secret_read_policy"
    score: int = 0
    defined: bool = False
    no_api_key_read: bool = True
    no_env_var_read: bool = True
    no_hardcoded_secret: bool = True
    policy_enforced: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunNetworkBlockPolicy:
    name: str = "dry_run_network_block_policy"
    score: int = 0
    defined: bool = False
    network_execution_blocked: bool = True
    http_blocked: bool = True
    websocket_blocked: bool = True
    socket_blocked: bool = True
    external_api_blocked: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunAccountReadOnlyPolicy:
    name: str = "dry_run_account_read_only_policy"
    score: int = 0
    defined: bool = False
    active_account_access_blocked: bool = True
    account_mutations_blocked: bool = True
    schema_only_account_review: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunMarketDataReadOnlyPolicy:
    name: str = "dry_run_market_data_read_only_policy"
    score: int = 0
    defined: bool = False
    read_only_market_data_only: bool = True
    live_subscription_blocked: bool = True
    network_request_blocked: bool = True
    synthetic_or_schema_only: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunOrderBlockingPolicy:
    name: str = "dry_run_order_blocking_policy"
    score: int = 0
    defined: bool = False
    order_execution_blocked: bool = True
    real_order_blocked: bool = True
    cancel_replace_blocked: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunPositionMutationBlockPolicy:
    name: str = "dry_run_position_mutation_block_policy"
    score: int = 0
    defined: bool = False
    position_mutation_blocked: bool = True
    position_request_absent: bool = True
    close_modify_blocked: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunObservabilityPlan:
    name: str = "dry_run_observability_plan"
    score: int = 0
    defined: bool = False
    offline_events_defined: bool = True
    connection_attempt_logging_disabled: bool = True
    sensitive_values_redacted: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunJournalPlan:
    name: str = "dry_run_journal_plan"
    score: int = 0
    defined: bool = False
    offline_journal_required: bool = True
    sensitive_values_redacted: bool = True
    no_secret_material_logged: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunHumanApprovalPlan:
    name: str = "dry_run_human_approval_plan"
    score: int = 0
    defined: bool = False
    human_approval_required: bool = True
    approval_before_safety_gate: bool = True
    dry_run_plan_evidence_required: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunStopConditionPlan:
    name: str = "dry_run_stop_conditions_plan"
    score: int = 0
    defined: bool = False
    stop_on_secret_read: bool = True
    stop_on_network_request: bool = True
    stop_on_order_or_position_request: bool = True
    stop_on_account_access_request: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunSuccessCriteria:
    name: str = "dry_run_success_criteria"
    score: int = 0
    defined: bool = False
    no_real_connection_attempted: bool = True
    all_guards_verified: bool = True
    read_only_boundaries_preserved: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunFailureCriteria:
    name: str = "dry_run_failure_criteria"
    score: int = 0
    defined: bool = False
    fail_on_secret_read: bool = True
    fail_on_network_attempt: bool = True
    fail_on_order_or_position_request: bool = True
    fail_on_account_access_request: bool = True
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPlanRisk, ...] = ()
    details: tuple[str, ...] = ()

@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunPlanScore:
    overall_score: int
    connection_preparation_review_score: int
    scope_score: int
    boundary_score: int
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


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunPlanInput:
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
    connection_preparation_review_approved: bool | None = None
    dry_run_scope_defined: bool | None = None
    dry_run_environment_boundaries_defined: bool | None = None
    dry_run_preconditions_defined: bool | None = None
    dry_run_credentials_reference_policy_defined: bool | None = None
    dry_run_credentials_reference_only: bool | None = None
    dry_run_no_secret_read_policy_defined: bool | None = None
    dry_run_secret_read_blocked: bool | None = None
    dry_run_network_block_policy_defined: bool | None = None
    dry_run_network_blocked: bool | None = None
    dry_run_http_websocket_socket_block_policy_defined: bool | None = None
    dry_run_http_blocked: bool | None = None
    dry_run_websocket_blocked: bool | None = None
    dry_run_socket_blocked: bool | None = None
    dry_run_external_api_blocked: bool | None = None
    dry_run_account_read_only_policy_defined: bool | None = None
    dry_run_account_access_blocked: bool | None = None
    dry_run_account_mutations_blocked: bool | None = None
    dry_run_market_data_read_only_policy_defined: bool | None = None
    dry_run_market_data_live_subscription_blocked: bool | None = None
    dry_run_market_data_network_request_blocked: bool | None = None
    dry_run_order_blocking_policy_defined: bool | None = None
    dry_run_order_execution_blocked: bool | None = None
    dry_run_cancel_replace_blocked: bool | None = None
    dry_run_position_mutation_block_policy_defined: bool | None = None
    dry_run_position_mutation_blocked: bool | None = None
    dry_run_observability_plan_defined: bool | None = None
    dry_run_journal_plan_defined: bool | None = None
    dry_run_human_approval_plan_defined: bool | None = None
    dry_run_human_approval_required: bool | None = None
    dry_run_stop_conditions_plan_defined: bool | None = None
    dry_run_success_criteria_defined: bool | None = None
    dry_run_failure_criteria_defined: bool | None = None
    paper_broker_read_only_connection_dry_run_safety_gate_requested: bool | None = False
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
    connection_preparation_review_score: int | None = None
    dry_run_scope_score: int | None = None
    dry_run_boundary_score: int | None = None
    dry_run_precondition_score: int | None = None
    dry_run_credential_policy_score: int | None = None
    dry_run_no_secret_read_score: int | None = None
    dry_run_network_block_score: int | None = None
    dry_run_http_websocket_socket_block_score: int | None = None
    dry_run_account_read_only_score: int | None = None
    dry_run_market_data_read_only_score: int | None = None
    dry_run_order_blocking_score: int | None = None
    dry_run_position_mutation_block_score: int | None = None
    dry_run_observability_score: int | None = None
    dry_run_journal_score: int | None = None
    dry_run_human_approval_score: int | None = None
    dry_run_stop_conditions_score: int | None = None
    dry_run_success_criteria_score: int | None = None
    dry_run_failure_criteria_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunPlanResult:
    state: PaperBrokerReadOnlyConnectionDryRunPlanState
    decision: PaperBrokerReadOnlyConnectionDryRunPlanDecision
    dry_run_plan_score: int
    score_breakdown: PaperBrokerReadOnlyConnectionDryRunPlanScore
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPlanRisk, ...] = ()
    recommendations: tuple[PaperBrokerReadOnlyConnectionDryRunPlanRecommendation, ...] = ()
    dry_run_scope: DryRunScope = field(default_factory=DryRunScope)
    environment_boundaries: DryRunEnvironmentBoundary = field(default_factory=DryRunEnvironmentBoundary)
    preconditions: DryRunPrecondition = field(default_factory=DryRunPrecondition)
    credentials_reference_policy: DryRunCredentialsReferencePolicy = field(default_factory=DryRunCredentialsReferencePolicy)
    no_secret_read_policy: DryRunNoSecretReadPolicy = field(default_factory=DryRunNoSecretReadPolicy)
    network_block_policy: DryRunNetworkBlockPolicy = field(default_factory=DryRunNetworkBlockPolicy)
    http_websocket_socket_block_policy: DryRunNetworkBlockPolicy = field(default_factory=DryRunNetworkBlockPolicy)
    account_read_only_policy: DryRunAccountReadOnlyPolicy = field(default_factory=DryRunAccountReadOnlyPolicy)
    market_data_read_only_policy: DryRunMarketDataReadOnlyPolicy = field(default_factory=DryRunMarketDataReadOnlyPolicy)
    order_blocking_policy: DryRunOrderBlockingPolicy = field(default_factory=DryRunOrderBlockingPolicy)
    position_mutation_block_policy: DryRunPositionMutationBlockPolicy = field(default_factory=DryRunPositionMutationBlockPolicy)
    observability_plan: DryRunObservabilityPlan = field(default_factory=DryRunObservabilityPlan)
    journal_plan: DryRunJournalPlan = field(default_factory=DryRunJournalPlan)
    human_approval_plan: DryRunHumanApprovalPlan = field(default_factory=DryRunHumanApprovalPlan)
    stop_conditions_plan: DryRunStopConditionPlan = field(default_factory=DryRunStopConditionPlan)
    success_criteria: DryRunSuccessCriteria = field(default_factory=DryRunSuccessCriteria)
    failure_criteria: DryRunFailureCriteria = field(default_factory=DryRunFailureCriteria)
    offline_only: bool = True
    summary: str = ""
