"""Models for the AGIcore Paper Broker Read-Only Connection Dry Run Safety Gate."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerReadOnlyConnectionDryRunSafetyGateState(StrEnum):
    NOT_READY = "NOT_READY"
    DRY_RUN_SAFETY_INPUT_INVALID = "DRY_RUN_SAFETY_INPUT_INVALID"
    DRY_RUN_SAFETY_BLOCKED = "DRY_RUN_SAFETY_BLOCKED"
    DRY_RUN_SAFETY_COMPLETED_WITH_WARNINGS = "DRY_RUN_SAFETY_COMPLETED_WITH_WARNINGS"
    DRY_RUN_SAFETY_COMPLETED = "DRY_RUN_SAFETY_COMPLETED"
    READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION = (
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION"
    )


class PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision(StrEnum):
    BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE = (
        "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE"
    )
    REQUIRE_DRY_RUN_PLAN_FIXES = "REQUIRE_DRY_RUN_PLAN_FIXES"
    REQUIRE_SCOPE_SAFETY_FIXES = "REQUIRE_SCOPE_SAFETY_FIXES"
    REQUIRE_BOUNDARY_SAFETY_FIXES = "REQUIRE_BOUNDARY_SAFETY_FIXES"
    REQUIRE_PRECONDITION_SAFETY_FIXES = "REQUIRE_PRECONDITION_SAFETY_FIXES"
    REQUIRE_CREDENTIAL_SAFETY_FIXES = "REQUIRE_CREDENTIAL_SAFETY_FIXES"
    REQUIRE_NO_SECRET_READ_SAFETY_FIXES = "REQUIRE_NO_SECRET_READ_SAFETY_FIXES"
    REQUIRE_NETWORK_BLOCK_SAFETY_FIXES = "REQUIRE_NETWORK_BLOCK_SAFETY_FIXES"
    REQUIRE_ACCOUNT_READ_ONLY_SAFETY_FIXES = "REQUIRE_ACCOUNT_READ_ONLY_SAFETY_FIXES"
    REQUIRE_MARKET_DATA_READ_ONLY_SAFETY_FIXES = "REQUIRE_MARKET_DATA_READ_ONLY_SAFETY_FIXES"
    REQUIRE_ORDER_BLOCKING_SAFETY_FIXES = "REQUIRE_ORDER_BLOCKING_SAFETY_FIXES"
    REQUIRE_POSITION_MUTATION_BLOCK_SAFETY_FIXES = "REQUIRE_POSITION_MUTATION_BLOCK_SAFETY_FIXES"
    REQUIRE_OBSERVABILITY_SAFETY_FIXES = "REQUIRE_OBSERVABILITY_SAFETY_FIXES"
    REQUIRE_JOURNAL_SAFETY_FIXES = "REQUIRE_JOURNAL_SAFETY_FIXES"
    REQUIRE_HUMAN_APPROVAL_SAFETY_FIXES = "REQUIRE_HUMAN_APPROVAL_SAFETY_FIXES"
    REQUIRE_STOP_CONDITION_SAFETY_FIXES = "REQUIRE_STOP_CONDITION_SAFETY_FIXES"
    REQUIRE_SUCCESS_FAILURE_CRITERIA_SAFETY_FIXES = "REQUIRE_SUCCESS_FAILURE_CRITERIA_SAFETY_FIXES"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE = (
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE"
    )


class PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk(StrEnum):
    DRY_RUN_PLAN_NOT_APPROVED = "DRY_RUN_PLAN_NOT_APPROVED"
    DRY_RUN_SCOPE_UNSAFE = "DRY_RUN_SCOPE_UNSAFE"
    DRY_RUN_BOUNDARY_UNSAFE = "DRY_RUN_BOUNDARY_UNSAFE"
    DRY_RUN_PRECONDITION_UNSAFE = "DRY_RUN_PRECONDITION_UNSAFE"
    DRY_RUN_CREDENTIALS_UNSAFE = "DRY_RUN_CREDENTIALS_UNSAFE"
    DRY_RUN_SECRET_READ_POLICY_UNSAFE = "DRY_RUN_SECRET_READ_POLICY_UNSAFE"
    DRY_RUN_NETWORK_NOT_BLOCKED = "DRY_RUN_NETWORK_NOT_BLOCKED"
    DRY_RUN_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED = "DRY_RUN_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED"
    DRY_RUN_ACCOUNT_READ_ONLY_UNSAFE = "DRY_RUN_ACCOUNT_READ_ONLY_UNSAFE"
    DRY_RUN_MARKET_DATA_READ_ONLY_UNSAFE = "DRY_RUN_MARKET_DATA_READ_ONLY_UNSAFE"
    DRY_RUN_ORDER_BLOCKING_UNSAFE = "DRY_RUN_ORDER_BLOCKING_UNSAFE"
    DRY_RUN_POSITION_MUTATION_BLOCK_UNSAFE = "DRY_RUN_POSITION_MUTATION_BLOCK_UNSAFE"
    DRY_RUN_OBSERVABILITY_INCOMPLETE = "DRY_RUN_OBSERVABILITY_INCOMPLETE"
    DRY_RUN_JOURNAL_INCOMPLETE = "DRY_RUN_JOURNAL_INCOMPLETE"
    DRY_RUN_HUMAN_APPROVAL_MISSING = "DRY_RUN_HUMAN_APPROVAL_MISSING"
    DRY_RUN_STOP_CONDITIONS_MISSING = "DRY_RUN_STOP_CONDITIONS_MISSING"
    DRY_RUN_SUCCESS_FAILURE_CRITERIA_UNSAFE = "DRY_RUN_SUCCESS_FAILURE_CRITERIA_UNSAFE"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION = (
        "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION"
    )


class PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation(StrEnum):
    HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION = (
        "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION"
    )
    APPROVE_DRY_RUN_PLAN_FIRST = "APPROVE_DRY_RUN_PLAN_FIRST"
    HARDEN_DRY_RUN_SCOPE = "HARDEN_DRY_RUN_SCOPE"
    HARDEN_DRY_RUN_BOUNDARIES = "HARDEN_DRY_RUN_BOUNDARIES"
    HARDEN_DRY_RUN_PRECONDITIONS = "HARDEN_DRY_RUN_PRECONDITIONS"
    HARDEN_DRY_RUN_CREDENTIALS = "HARDEN_DRY_RUN_CREDENTIALS"
    HARDEN_DRY_RUN_NO_SECRET_READ = "HARDEN_DRY_RUN_NO_SECRET_READ"
    BLOCK_DRY_RUN_NETWORK = "BLOCK_DRY_RUN_NETWORK"
    BLOCK_DRY_RUN_HTTP_WEBSOCKET_SOCKET = "BLOCK_DRY_RUN_HTTP_WEBSOCKET_SOCKET"
    HARDEN_DRY_RUN_ACCOUNT_READ_ONLY = "HARDEN_DRY_RUN_ACCOUNT_READ_ONLY"
    HARDEN_DRY_RUN_MARKET_DATA_READ_ONLY = "HARDEN_DRY_RUN_MARKET_DATA_READ_ONLY"
    HARDEN_DRY_RUN_ORDER_BLOCKING = "HARDEN_DRY_RUN_ORDER_BLOCKING"
    HARDEN_DRY_RUN_POSITION_MUTATION_BLOCK = "HARDEN_DRY_RUN_POSITION_MUTATION_BLOCK"
    COMPLETE_DRY_RUN_OBSERVABILITY = "COMPLETE_DRY_RUN_OBSERVABILITY"
    COMPLETE_DRY_RUN_JOURNAL = "COMPLETE_DRY_RUN_JOURNAL"
    REQUIRE_DRY_RUN_HUMAN_APPROVAL = "REQUIRE_DRY_RUN_HUMAN_APPROVAL"
    DEFINE_DRY_RUN_STOP_CONDITIONS = "DEFINE_DRY_RUN_STOP_CONDITIONS"
    HARDEN_DRY_RUN_SUCCESS_FAILURE_CRITERIA = "HARDEN_DRY_RUN_SUCCESS_FAILURE_CRITERIA"
    RESTORE_OFFLINE_BOUNDARIES = "RESTORE_OFFLINE_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION = (
        "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION"
    )
    RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE_SUITE = (
        "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE_SUITE"
    )
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION = (
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION"
    )


@dataclass(frozen=True)
class DryRunSafetyFinding:
    score: int = 0
    passed: bool = False
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DryRunScopeSafetyFinding(DryRunSafetyFinding):
    plan_only: bool = True
    read_only_only: bool = True
    dry_run_not_executed: bool = True
    prohibited_actions_confirmed: bool = False


@dataclass(frozen=True)
class DryRunBoundarySafetyFinding(DryRunSafetyFinding):
    offline_only: bool = False
    sandbox_only: bool = False
    broker_connection_disabled: bool = False
    network_transport_blocked: bool = False
    data_access_blocked: bool = False


@dataclass(frozen=True)
class DryRunCredentialsSafetyFinding(DryRunSafetyFinding):
    reference_only: bool = False
    no_secret_material: bool = False
    no_api_key_read: bool = False
    no_env_var_read: bool = False


@dataclass(frozen=True)
class DryRunNetworkBlockSafetyFinding(DryRunSafetyFinding):
    network_execution_blocked: bool = False
    http_blocked: bool = False
    websocket_blocked: bool = False
    socket_blocked: bool = False
    external_api_blocked: bool = False


@dataclass(frozen=True)
class DryRunAccountReadOnlySafetyFinding(DryRunSafetyFinding):
    active_account_access_blocked: bool = False
    account_mutations_blocked: bool = False


@dataclass(frozen=True)
class DryRunMarketDataReadOnlySafetyFinding(DryRunSafetyFinding):
    read_only_market_data_only: bool = False
    live_subscription_blocked: bool = False
    network_request_blocked: bool = False


@dataclass(frozen=True)
class DryRunOrderBlockingSafetyFinding(DryRunSafetyFinding):
    order_execution_blocked: bool = False
    real_order_blocked: bool = False
    cancel_replace_blocked: bool = False


@dataclass(frozen=True)
class DryRunPositionMutationBlockSafetyFinding(DryRunSafetyFinding):
    position_mutation_blocked: bool = False
    position_request_absent: bool = True


@dataclass(frozen=True)
class DryRunHumanApprovalSafetyFinding(DryRunSafetyFinding):
    human_approval_required: bool = False
    approval_before_preparation: bool = False


@dataclass(frozen=True)
class DryRunStopConditionSafetyFinding(DryRunSafetyFinding):
    stop_on_secret_read: bool = False
    stop_on_network_request: bool = False
    stop_on_order_or_position_request: bool = False
    stop_on_account_access_request: bool = False


@dataclass(frozen=True)
class DryRunSuccessFailureCriteriaSafetyFinding(DryRunSafetyFinding):
    success_criteria_defined: bool = False
    failure_criteria_defined: bool = False
    fail_closed_on_boundary_violation: bool = False


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunSafetyGateScore:
    overall_score: int
    dry_run_plan_score: int
    scope_score: int
    boundary_score: int
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


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunSafetyGateInput:
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
    dry_run_plan_approved: bool | None = None
    dry_run_scope_safety_verified: bool | None = None
    dry_run_boundary_safety_verified: bool | None = None
    dry_run_precondition_safety_verified: bool | None = None
    dry_run_credentials_safety_verified: bool | None = None
    dry_run_no_secret_read_safety_verified: bool | None = None
    dry_run_network_block_safety_verified: bool | None = None
    dry_run_http_websocket_socket_block_safety_verified: bool | None = None
    dry_run_account_read_only_safety_verified: bool | None = None
    dry_run_market_data_read_only_safety_verified: bool | None = None
    dry_run_order_blocking_safety_verified: bool | None = None
    dry_run_position_mutation_block_safety_verified: bool | None = None
    dry_run_observability_safety_verified: bool | None = None
    dry_run_journal_safety_verified: bool | None = None
    dry_run_human_approval_safety_verified: bool | None = None
    dry_run_stop_conditions_safety_verified: bool | None = None
    dry_run_success_failure_criteria_safety_verified: bool | None = None
    paper_broker_read_only_connection_dry_run_preparation_requested: bool | None = False
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
    dry_run_plan_score: int | None = None
    scope_score: int | None = None
    boundary_score: int | None = None
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
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunSafetyGateResult:
    state: PaperBrokerReadOnlyConnectionDryRunSafetyGateState
    decision: PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision
    safety_gate_score: int
    score_breakdown: PaperBrokerReadOnlyConnectionDryRunSafetyGateScore
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk, ...] = ()
    recommendations: tuple[PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation, ...] = ()
    scope_safety: DryRunScopeSafetyFinding = field(default_factory=DryRunScopeSafetyFinding)
    boundary_safety: DryRunBoundarySafetyFinding = field(default_factory=DryRunBoundarySafetyFinding)
    precondition_safety: DryRunSafetyFinding = field(default_factory=DryRunSafetyFinding)
    credentials_safety: DryRunCredentialsSafetyFinding = field(default_factory=DryRunCredentialsSafetyFinding)
    no_secret_read_safety: DryRunCredentialsSafetyFinding = field(default_factory=DryRunCredentialsSafetyFinding)
    network_block_safety: DryRunNetworkBlockSafetyFinding = field(default_factory=DryRunNetworkBlockSafetyFinding)
    http_websocket_socket_block_safety: DryRunNetworkBlockSafetyFinding = field(
        default_factory=DryRunNetworkBlockSafetyFinding
    )
    account_read_only_safety: DryRunAccountReadOnlySafetyFinding = field(default_factory=DryRunAccountReadOnlySafetyFinding)
    market_data_read_only_safety: DryRunMarketDataReadOnlySafetyFinding = field(
        default_factory=DryRunMarketDataReadOnlySafetyFinding
    )
    order_blocking_safety: DryRunOrderBlockingSafetyFinding = field(default_factory=DryRunOrderBlockingSafetyFinding)
    position_mutation_block_safety: DryRunPositionMutationBlockSafetyFinding = field(
        default_factory=DryRunPositionMutationBlockSafetyFinding
    )
    observability_safety: DryRunSafetyFinding = field(default_factory=DryRunSafetyFinding)
    journal_safety: DryRunSafetyFinding = field(default_factory=DryRunSafetyFinding)
    human_approval_safety: DryRunHumanApprovalSafetyFinding = field(default_factory=DryRunHumanApprovalSafetyFinding)
    stop_conditions_safety: DryRunStopConditionSafetyFinding = field(default_factory=DryRunStopConditionSafetyFinding)
    success_failure_criteria_safety: DryRunSuccessFailureCriteriaSafetyFinding = field(
        default_factory=DryRunSuccessFailureCriteriaSafetyFinding
    )
    offline_only: bool = True
    summary: str = ""
