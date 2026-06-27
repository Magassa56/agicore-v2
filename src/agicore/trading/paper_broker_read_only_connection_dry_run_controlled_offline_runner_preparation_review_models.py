"""Models for Paper Broker Read-Only Connection Dry Run Controlled Offline Runner Preparation Review."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewState(StrEnum):
    NOT_READY = "NOT_READY"
    OFFLINE_RUNNER_PREPARATION_REVIEW_INPUT_INVALID = "OFFLINE_RUNNER_PREPARATION_REVIEW_INPUT_INVALID"
    OFFLINE_RUNNER_PREPARATION_REVIEW_BLOCKED = "OFFLINE_RUNNER_PREPARATION_REVIEW_BLOCKED"
    OFFLINE_RUNNER_PREPARATION_REVIEW_COMPLETED_WITH_WARNINGS = "OFFLINE_RUNNER_PREPARATION_REVIEW_COMPLETED_WITH_WARNINGS"
    OFFLINE_RUNNER_PREPARATION_REVIEW_COMPLETED = "OFFLINE_RUNNER_PREPARATION_REVIEW_COMPLETED"
    READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN = "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN"


class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewDecision(StrEnum):
    BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW = "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW"
    REQUIRE_OFFLINE_RUNNER_PREPARATION_FIXES = "REQUIRE_OFFLINE_RUNNER_PREPARATION_FIXES"
    REQUIRE_OFFLINE_RUNNER_SCOPE_PREPARATION_REVIEW_FIXES = "REQUIRE_OFFLINE_RUNNER_SCOPE_PREPARATION_REVIEW_FIXES"
    REQUIRE_OFFLINE_RUNNER_EXECUTION_MODE_PREPARATION_REVIEW_FIXES = "REQUIRE_OFFLINE_RUNNER_EXECUTION_MODE_PREPARATION_REVIEW_FIXES"
    REQUIRE_OFFLINE_RUNNER_INPUT_CONTRACT_PREPARATION_REVIEW_FIXES = "REQUIRE_OFFLINE_RUNNER_INPUT_CONTRACT_PREPARATION_REVIEW_FIXES"
    REQUIRE_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_PREPARATION_REVIEW_FIXES = "REQUIRE_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_PREPARATION_REVIEW_FIXES"
    REQUIRE_OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_PREPARATION_REVIEW_FIXES = "REQUIRE_OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_PREPARATION_REVIEW_FIXES"
    REQUIRE_OFFLINE_RUNNER_NO_REAL_BROKER_GUARD_REVIEW_FIXES = "REQUIRE_OFFLINE_RUNNER_NO_REAL_BROKER_GUARD_REVIEW_FIXES"
    REQUIRE_OFFLINE_RUNNER_NO_SECRET_READ_GUARD_REVIEW_FIXES = "REQUIRE_OFFLINE_RUNNER_NO_SECRET_READ_GUARD_REVIEW_FIXES"
    REQUIRE_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_REVIEW_FIXES = "REQUIRE_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_REVIEW_FIXES"
    REQUIRE_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_PREPARATION_REVIEW_FIXES = "REQUIRE_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_PREPARATION_REVIEW_FIXES"
    REQUIRE_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_PREPARATION_REVIEW_FIXES = "REQUIRE_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_PREPARATION_REVIEW_FIXES"
    REQUIRE_OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_REVIEW_FIXES = "REQUIRE_OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_REVIEW_FIXES"
    REQUIRE_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_REVIEW_FIXES = "REQUIRE_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_REVIEW_FIXES"
    REQUIRE_OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_PREPARATION_REVIEW_FIXES = "REQUIRE_OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_PREPARATION_REVIEW_FIXES"
    REQUIRE_OFFLINE_RUNNER_RISK_OBSERVATION_PREPARATION_REVIEW_FIXES = "REQUIRE_OFFLINE_RUNNER_RISK_OBSERVATION_PREPARATION_REVIEW_FIXES"
    REQUIRE_OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_PREPARATION_REVIEW_FIXES = "REQUIRE_OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_PREPARATION_REVIEW_FIXES"
    REQUIRE_OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_PREPARATION_REVIEW_FIXES = "REQUIRE_OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_PREPARATION_REVIEW_FIXES"
    REQUIRE_OFFLINE_RUNNER_JOURNAL_PREPARATION_REVIEW_FIXES = "REQUIRE_OFFLINE_RUNNER_JOURNAL_PREPARATION_REVIEW_FIXES"
    REQUIRE_OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_REVIEW_FIXES = "REQUIRE_OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_REVIEW_FIXES"
    REQUIRE_OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION_REVIEW_FIXES = "REQUIRE_OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION_REVIEW_FIXES"
    REQUIRE_OFFLINE_RUNNER_STOP_CONDITION_PREPARATION_REVIEW_FIXES = "REQUIRE_OFFLINE_RUNNER_STOP_CONDITION_PREPARATION_REVIEW_FIXES"
    REQUIRE_OFFLINE_RUNNER_SUCCESS_FAILURE_PREPARATION_REVIEW_FIXES = "REQUIRE_OFFLINE_RUNNER_SUCCESS_FAILURE_PREPARATION_REVIEW_FIXES"
    REQUIRE_OFFLINE_RUNNER_AUDIT_PREPARATION_REVIEW_FIXES = "REQUIRE_OFFLINE_RUNNER_AUDIT_PREPARATION_REVIEW_FIXES"
    REQUIRE_OFFLINE_RUNNER_GO_NO_GO_PREPARATION_REVIEW_FIXES = "REQUIRE_OFFLINE_RUNNER_GO_NO_GO_PREPARATION_REVIEW_FIXES"
    REQUIRE_OFFLINE_RUNNER_ABORT_PREPARATION_REVIEW_FIXES = "REQUIRE_OFFLINE_RUNNER_ABORT_PREPARATION_REVIEW_FIXES"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW = "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW"


class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewRisk(StrEnum):
    OFFLINE_RUNNER_PREPARATION_NOT_APPROVED = "OFFLINE_RUNNER_PREPARATION_NOT_APPROVED"
    OFFLINE_RUNNER_SCOPE_PREPARATION_REVIEW_FAILED = "OFFLINE_RUNNER_SCOPE_PREPARATION_REVIEW_FAILED"
    OFFLINE_RUNNER_EXECUTION_MODE_PREPARATION_REVIEW_FAILED = "OFFLINE_RUNNER_EXECUTION_MODE_PREPARATION_REVIEW_FAILED"
    OFFLINE_RUNNER_INPUT_CONTRACT_PREPARATION_REVIEW_FAILED = "OFFLINE_RUNNER_INPUT_CONTRACT_PREPARATION_REVIEW_FAILED"
    OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_PREPARATION_REVIEW_FAILED = "OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_PREPARATION_REVIEW_FAILED"
    OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_PREPARATION_REVIEW_FAILED = "OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_PREPARATION_REVIEW_FAILED"
    OFFLINE_RUNNER_REAL_BROKER_GUARD_REVIEW_FAILED = "OFFLINE_RUNNER_REAL_BROKER_GUARD_REVIEW_FAILED"
    OFFLINE_RUNNER_SECRET_READ_GUARD_REVIEW_FAILED = "OFFLINE_RUNNER_SECRET_READ_GUARD_REVIEW_FAILED"
    OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_REVIEW_FAILED = "OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_REVIEW_FAILED"
    OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW_FAILED = "OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW_FAILED"
    OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_PREPARATION_REVIEW_FAILED = "OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_PREPARATION_REVIEW_FAILED"
    OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_PREPARATION_REVIEW_FAILED = "OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_PREPARATION_REVIEW_FAILED"
    OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_REVIEW_FAILED = "OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_REVIEW_FAILED"
    OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_REVIEW_FAILED = "OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_REVIEW_FAILED"
    OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_PREPARATION_REVIEW_FAILED = "OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_PREPARATION_REVIEW_FAILED"
    OFFLINE_RUNNER_RISK_OBSERVATION_PREPARATION_REVIEW_FAILED = "OFFLINE_RUNNER_RISK_OBSERVATION_PREPARATION_REVIEW_FAILED"
    OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_PREPARATION_REVIEW_FAILED = "OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_PREPARATION_REVIEW_FAILED"
    OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_PREPARATION_REVIEW_FAILED = "OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_PREPARATION_REVIEW_FAILED"
    OFFLINE_RUNNER_JOURNAL_PREPARATION_REVIEW_FAILED = "OFFLINE_RUNNER_JOURNAL_PREPARATION_REVIEW_FAILED"
    OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_REVIEW_FAILED = "OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_REVIEW_FAILED"
    OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION_REVIEW_FAILED = "OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION_REVIEW_FAILED"
    OFFLINE_RUNNER_STOP_CONDITIONS_PREPARATION_REVIEW_FAILED = "OFFLINE_RUNNER_STOP_CONDITIONS_PREPARATION_REVIEW_FAILED"
    OFFLINE_RUNNER_SUCCESS_CRITERIA_PREPARATION_REVIEW_FAILED = "OFFLINE_RUNNER_SUCCESS_CRITERIA_PREPARATION_REVIEW_FAILED"
    OFFLINE_RUNNER_FAILURE_CRITERIA_PREPARATION_REVIEW_FAILED = "OFFLINE_RUNNER_FAILURE_CRITERIA_PREPARATION_REVIEW_FAILED"
    OFFLINE_RUNNER_AUDIT_PREPARATION_REVIEW_FAILED = "OFFLINE_RUNNER_AUDIT_PREPARATION_REVIEW_FAILED"
    OFFLINE_RUNNER_GO_NO_GO_PREPARATION_REVIEW_FAILED = "OFFLINE_RUNNER_GO_NO_GO_PREPARATION_REVIEW_FAILED"
    OFFLINE_RUNNER_ABORT_PREPARATION_REVIEW_FAILED = "OFFLINE_RUNNER_ABORT_PREPARATION_REVIEW_FAILED"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN = "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN"


class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewRecommendation(StrEnum):
    HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN = "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN"
    APPROVE_OFFLINE_RUNNER_PREPARATION_FIRST = "APPROVE_OFFLINE_RUNNER_PREPARATION_FIRST"
    FIX_OFFLINE_RUNNER_SCOPE_PREPARATION_REVIEW = "FIX_OFFLINE_RUNNER_SCOPE_PREPARATION_REVIEW"
    FIX_OFFLINE_RUNNER_EXECUTION_MODE_PREPARATION_REVIEW = "FIX_OFFLINE_RUNNER_EXECUTION_MODE_PREPARATION_REVIEW"
    FIX_OFFLINE_RUNNER_INPUT_CONTRACT_PREPARATION_REVIEW = "FIX_OFFLINE_RUNNER_INPUT_CONTRACT_PREPARATION_REVIEW"
    FIX_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_PREPARATION_REVIEW = "FIX_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_PREPARATION_REVIEW"
    FIX_OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_PREPARATION_REVIEW = "FIX_OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_PREPARATION_REVIEW"
    FIX_OFFLINE_RUNNER_NO_REAL_BROKER_GUARD_REVIEW = "FIX_OFFLINE_RUNNER_NO_REAL_BROKER_GUARD_REVIEW"
    FIX_OFFLINE_RUNNER_NO_SECRET_READ_GUARD_REVIEW = "FIX_OFFLINE_RUNNER_NO_SECRET_READ_GUARD_REVIEW"
    FIX_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_REVIEW = "FIX_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_REVIEW"
    FIX_OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW = "FIX_OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW"
    FIX_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_PREPARATION_REVIEW = "FIX_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_PREPARATION_REVIEW"
    FIX_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_PREPARATION_REVIEW = "FIX_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_PREPARATION_REVIEW"
    FIX_OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_REVIEW = "FIX_OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_REVIEW"
    FIX_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_REVIEW = "FIX_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_REVIEW"
    FIX_OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_PREPARATION_REVIEW = "FIX_OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_PREPARATION_REVIEW"
    FIX_OFFLINE_RUNNER_RISK_OBSERVATION_PREPARATION_REVIEW = "FIX_OFFLINE_RUNNER_RISK_OBSERVATION_PREPARATION_REVIEW"
    FIX_OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_PREPARATION_REVIEW = "FIX_OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_PREPARATION_REVIEW"
    FIX_OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_PREPARATION_REVIEW = "FIX_OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_PREPARATION_REVIEW"
    FIX_OFFLINE_RUNNER_JOURNAL_PREPARATION_REVIEW = "FIX_OFFLINE_RUNNER_JOURNAL_PREPARATION_REVIEW"
    FIX_OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_REVIEW = "FIX_OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_REVIEW"
    FIX_OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION_REVIEW = "FIX_OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION_REVIEW"
    FIX_OFFLINE_RUNNER_STOP_CONDITION_PREPARATION_REVIEW = "FIX_OFFLINE_RUNNER_STOP_CONDITION_PREPARATION_REVIEW"
    FIX_OFFLINE_RUNNER_SUCCESS_FAILURE_PREPARATION_REVIEW = "FIX_OFFLINE_RUNNER_SUCCESS_FAILURE_PREPARATION_REVIEW"
    FIX_OFFLINE_RUNNER_AUDIT_PREPARATION_REVIEW = "FIX_OFFLINE_RUNNER_AUDIT_PREPARATION_REVIEW"
    FIX_OFFLINE_RUNNER_GO_NO_GO_PREPARATION_REVIEW = "FIX_OFFLINE_RUNNER_GO_NO_GO_PREPARATION_REVIEW"
    FIX_OFFLINE_RUNNER_ABORT_PREPARATION_REVIEW = "FIX_OFFLINE_RUNNER_ABORT_PREPARATION_REVIEW"
    RESTORE_OFFLINE_BOUNDARIES = "RESTORE_OFFLINE_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN = "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN"
    RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW_SUITE = "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW_SUITE"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN = "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN"


Risk = PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewRisk


@dataclass(frozen=True)
class _OfflineRunnerPreparationReviewFinding:
    name: str = "offline_runner_preparation_review_finding"
    score: int = 0
    passed: bool = False
    risks: tuple[Risk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class OfflineRunnerScopePreparationReviewFinding(_OfflineRunnerPreparationReviewFinding):
    name: str = "offline_runner_scope_preparation_review"
    offline_only: bool = True
    sandbox_only: bool = True
    preparation_only: bool = True
    no_runner_executable_created: bool = True


@dataclass(frozen=True)
class OfflineRunnerExecutionModePreparationReviewFinding(_OfflineRunnerPreparationReviewFinding):
    name: str = "offline_runner_execution_mode_preparation_review"
    controlled_offline_mode: bool = True
    deterministic_mode: bool = True
    in_memory_only: bool = True
    no_dry_run_execution: bool = True


@dataclass(frozen=True)
class OfflineRunnerInputPreparationReviewFinding(_OfflineRunnerPreparationReviewFinding):
    name: str = "offline_runner_input_preparation_review"
    schema_only_inputs: bool = True
    synthetic_inputs_only: bool = True
    no_real_credentials: bool = True


@dataclass(frozen=True)
class OfflineRunnerSyntheticMarketContextPreparationReviewFinding(_OfflineRunnerPreparationReviewFinding):
    name: str = "offline_runner_synthetic_market_context_preparation_review"
    synthetic_context_only: bool = True
    in_memory_context: bool = True
    no_data_access: bool = True


@dataclass(frozen=True)
class OfflineRunnerReadOnlyBrokerSimulationPreparationReviewFinding(_OfflineRunnerPreparationReviewFinding):
    name: str = "offline_runner_read_only_broker_simulation_preparation_review"
    simulated_broker_only: bool = True
    read_only_contract: bool = True
    no_real_broker: bool = True


@dataclass(frozen=True)
class OfflineRunnerNoRealBrokerGuardReviewFinding(_OfflineRunnerPreparationReviewFinding):
    name: str = "offline_runner_no_real_broker_guard_review"
    real_broker_blocked: bool = True
    alpaca_blocked: bool = True
    broker_connection_disabled: bool = True


@dataclass(frozen=True)
class OfflineRunnerNoSecretReadGuardReviewFinding(_OfflineRunnerPreparationReviewFinding):
    name: str = "offline_runner_no_secret_read_guard_review"
    no_api_key_read: bool = True
    no_env_var_read: bool = True
    no_hardcoded_secret: bool = True


@dataclass(frozen=True)
class OfflineRunnerNetworkBlockGuardReviewFinding(_OfflineRunnerPreparationReviewFinding):
    name: str = "offline_runner_network_block_guard_review"
    network_blocked: bool = True
    http_blocked: bool = True
    websocket_blocked: bool = True
    socket_blocked: bool = True
    external_api_blocked: bool = True


@dataclass(frozen=True)
class OfflineRunnerAccountSnapshotPreparationReviewFinding(_OfflineRunnerPreparationReviewFinding):
    name: str = "offline_runner_account_snapshot_preparation_review"
    simulated_snapshot_only: bool = True
    read_only_snapshot: bool = True
    active_account_access_blocked: bool = True


@dataclass(frozen=True)
class OfflineRunnerMarketDataSnapshotPreparationReviewFinding(_OfflineRunnerPreparationReviewFinding):
    name: str = "offline_runner_market_data_snapshot_preparation_review"
    synthetic_snapshot_only: bool = True
    read_only_snapshot: bool = True
    live_subscription_blocked: bool = True


@dataclass(frozen=True)
class OfflineRunnerOrderBlockingGuardReviewFinding(_OfflineRunnerPreparationReviewFinding):
    name: str = "offline_runner_order_blocking_guard_review"
    order_execution_blocked: bool = True
    real_order_blocked: bool = True
    cancel_replace_blocked: bool = True


@dataclass(frozen=True)
class OfflineRunnerPositionMutationBlockingGuardReviewFinding(_OfflineRunnerPreparationReviewFinding):
    name: str = "offline_runner_position_mutation_blocking_guard_review"
    position_mutation_blocked: bool = True
    close_modify_blocked: bool = True
    simulated_position_read_only: bool = True


@dataclass(frozen=True)
class OfflineRunnerStrategySignalObservationPreparationReviewFinding(_OfflineRunnerPreparationReviewFinding):
    name: str = "offline_runner_strategy_signal_observation_preparation_review"
    observation_only: bool = True
    no_signal_execution: bool = True
    signal_trace_required: bool = True


@dataclass(frozen=True)
class OfflineRunnerRiskObservationPreparationReviewFinding(_OfflineRunnerPreparationReviewFinding):
    name: str = "offline_runner_risk_observation_preparation_review"
    observation_only: bool = True
    no_risk_action_execution: bool = True
    risk_trace_required: bool = True


@dataclass(frozen=True)
class OfflineRunnerProfitabilityObservationPreparationReviewFinding(_OfflineRunnerPreparationReviewFinding):
    name: str = "offline_runner_profitability_observation_preparation_review"
    observation_only: bool = True
    no_profit_promise: bool = True
    profitability_trace_required: bool = True


@dataclass(frozen=True)
class OfflineRunnerConsistencyObservationPreparationReviewFinding(_OfflineRunnerPreparationReviewFinding):
    name: str = "offline_runner_consistency_observation_preparation_review"
    observation_only: bool = True
    deterministic_consistency_checks: bool = True
    consistency_trace_required: bool = True


@dataclass(frozen=True)
class OfflineRunnerJournalPreparationReviewFinding(_OfflineRunnerPreparationReviewFinding):
    name: str = "offline_runner_journal_preparation_review"
    offline_journal_required: bool = True
    no_secret_material_logged: bool = True
    plan_events_recorded: bool = True


@dataclass(frozen=True)
class OfflineRunnerObservabilityPreparationReviewFinding(_OfflineRunnerPreparationReviewFinding):
    name: str = "offline_runner_observability_preparation_review"
    offline_events_defined: bool = True
    no_connection_attempt_metrics: bool = True
    sensitive_values_redacted: bool = True


@dataclass(frozen=True)
class OfflineRunnerHumanApprovalPreparationReviewFinding(_OfflineRunnerPreparationReviewFinding):
    name: str = "offline_runner_human_approval_preparation_review"
    human_approval_required: bool = True
    approval_before_review: bool = True
    evidence_required: bool = True


@dataclass(frozen=True)
class OfflineRunnerStopConditionPreparationReviewFinding(_OfflineRunnerPreparationReviewFinding):
    name: str = "offline_runner_stop_condition_preparation_review"
    stop_on_secret_read: bool = True
    stop_on_network_request: bool = True
    stop_on_order_or_position_request: bool = True
    stop_on_account_access_request: bool = True


@dataclass(frozen=True)
class OfflineRunnerSuccessCriteriaPreparationReviewFinding(_OfflineRunnerPreparationReviewFinding):
    name: str = "offline_runner_success_criteria_preparation_review"
    no_boundary_violation_required: bool = True
    all_contracts_prepared: bool = True
    no_runner_execution_required: bool = True


@dataclass(frozen=True)
class OfflineRunnerFailureCriteriaPreparationReviewFinding(_OfflineRunnerPreparationReviewFinding):
    name: str = "offline_runner_failure_criteria_preparation_review"
    fail_on_boundary_violation: bool = True
    fail_on_missing_contract: bool = True
    fail_on_execution_request: bool = True


@dataclass(frozen=True)
class OfflineRunnerAuditPreparationReviewFinding(_OfflineRunnerPreparationReviewFinding):
    name: str = "offline_runner_audit_preparation_review"
    audit_events_defined: bool = True
    boundary_evidence_required: bool = True
    immutable_preparation_record_required: bool = True


@dataclass(frozen=True)
class OfflineRunnerGoNoGoPreparationReviewFinding(_OfflineRunnerPreparationReviewFinding):
    name: str = "offline_runner_go_no_go_preparation_review"
    go_no_go_required: bool = True
    no_go_on_risk: bool = True
    next_phase_requires_clean_preparation: bool = True


@dataclass(frozen=True)
class OfflineRunnerAbortPreparationReviewFinding(_OfflineRunnerPreparationReviewFinding):
    name: str = "offline_runner_abort_preparation_review"
    abort_on_secret_read: bool = True
    abort_on_network_or_broker_request: bool = True
    abort_on_order_or_position_request: bool = True


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewScore:
    overall_score: int = 0
    offline_runner_preparation_score: int = 0
    scope_score: int = 0
    execution_mode_score: int = 0
    input_contract_score: int = 0
    synthetic_market_context_score: int = 0
    read_only_broker_simulation_score: int = 0
    no_real_broker_score: int = 0
    no_secret_read_score: int = 0
    network_score: int = 0
    http_websocket_socket_score: int = 0
    account_snapshot_score: int = 0
    market_data_snapshot_score: int = 0
    order_blocking_score: int = 0
    position_mutation_score: int = 0
    strategy_signal_observation_score: int = 0
    risk_observation_score: int = 0
    profitability_observation_score: int = 0
    consistency_observation_score: int = 0
    journal_score: int = 0
    observability_score: int = 0
    human_approval_score: int = 0
    stop_conditions_score: int = 0
    success_score: int = 0
    failure_score: int = 0
    audit_score: int = 0
    go_no_go_score: int = 0
    abort_score: int = 0


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewInput:
    paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation: Any | None = None
    paper_broker_read_only_connection_dry_run_controlled_offline_runner_safety_gate: Any | None = None
    paper_broker_read_only_connection_dry_run_controlled_offline_runner_plan: Any | None = None
    paper_broker_read_only_connection_dry_run_controlled_execution_final_safety_gate: Any | None = None
    paper_broker_read_only_connection_dry_run_controlled_execution_final_plan: Any | None = None
    paper_broker_read_only_connection_dry_run_controlled_execution_preparation_review: Any | None = None
    paper_broker_read_only_connection_dry_run_controlled_execution_preparation: Any | None = None
    paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate: Any | None = None
    paper_broker_read_only_connection_dry_run_controlled_execution_plan: Any | None = None
    paper_broker_read_only_connection_dry_run_execution_final_safety_gate: Any | None = None
    paper_broker_read_only_connection_dry_run_execution_final_plan: Any | None = None
    paper_broker_read_only_connection_dry_run_execution_preparation_review: Any | None = None
    paper_broker_read_only_connection_dry_run_execution_preparation: Any | None = None
    paper_broker_read_only_connection_dry_run_execution_safety_gate: Any | None = None
    paper_broker_read_only_connection_dry_run_execution_plan: Any | None = None
    paper_broker_read_only_connection_dry_run_preparation_review: Any | None = None
    paper_broker_read_only_connection_dry_run_preparation: Any | None = None
    paper_broker_read_only_connection_dry_run_safety_gate: Any | None = None
    paper_broker_read_only_connection_dry_run_plan: Any | None = None
    paper_broker_read_only_connection_preparation_review: Any | None = None
    paper_broker_read_only_connection_preparation: Any | None = None
    paper_broker_read_only_connection_safety_gate: Any | None = None
    paper_broker_read_only_connection_plan: Any | None = None
    paper_broker_read_only_safety_review: Any | None = None
    paper_broker_read_only_preparation: Any | None = None
    offline_runner_preparation_approved: bool | None = None
    offline_runner_scope_preparation_review_verified: bool | None = None
    offline_runner_execution_mode_preparation_review_verified: bool | None = None
    offline_runner_input_contract_preparation_review_verified: bool | None = None
    offline_runner_synthetic_market_context_preparation_review_verified: bool | None = None
    offline_runner_read_only_broker_simulation_preparation_review_verified: bool | None = None
    offline_runner_no_real_broker_guard_review_verified: bool | None = None
    offline_runner_no_secret_read_guard_review_verified: bool | None = None
    offline_runner_network_block_guard_review_verified: bool | None = None
    offline_runner_http_websocket_socket_block_guard_review_verified: bool | None = None
    offline_runner_account_snapshot_preparation_review_verified: bool | None = None
    offline_runner_market_data_snapshot_preparation_review_verified: bool | None = None
    offline_runner_order_blocking_guard_review_verified: bool | None = None
    offline_runner_position_mutation_blocking_guard_review_verified: bool | None = None
    offline_runner_strategy_signal_observation_preparation_review_verified: bool | None = None
    offline_runner_risk_observation_preparation_review_verified: bool | None = None
    offline_runner_profitability_observation_preparation_review_verified: bool | None = None
    offline_runner_consistency_observation_preparation_review_verified: bool | None = None
    offline_runner_journal_preparation_review_verified: bool | None = None
    offline_runner_observability_preparation_review_verified: bool | None = None
    offline_runner_human_approval_preparation_review_verified: bool | None = None
    offline_runner_stop_conditions_preparation_review_verified: bool | None = None
    offline_runner_success_criteria_preparation_review_verified: bool | None = None
    offline_runner_failure_criteria_preparation_review_verified: bool | None = None
    offline_runner_audit_preparation_review_verified: bool | None = None
    offline_runner_go_no_go_preparation_review_verified: bool | None = None
    offline_runner_abort_preparation_review_verified: bool | None = None
    offline_mode_enforced: bool = True
    sandbox_mode_enforced: bool = True
    review_only: bool = True
    no_runner_executable_created: bool = True
    no_runner_execution: bool = True
    no_dry_run_execution: bool = True
    broker_connection_disabled: bool = True
    no_real_broker: bool = True
    no_alpaca_real: bool = True
    no_api_key_read: bool = True
    no_env_var_read: bool = True
    no_hardcoded_secrets: bool = True
    no_http_transport: bool = True
    no_websocket_transport: bool = True
    no_socket_transport: bool = True
    no_external_api: bool = True
    no_external_ml: bool = True
    no_external_llm: bool = True
    no_live_execution: bool = True
    no_real_account_access: bool = True
    no_real_order: bool = True
    no_position_mutation: bool = True
    real_execution_requested: bool = False
    runner_creation_requested: bool = False
    runner_execution_requested: bool = False
    dry_run_requested: bool = False
    dry_run_executed: bool = False
    broker_connection_requested: bool = False
    api_key_read_requested: bool = False
    env_var_read_requested: bool = False
    hardcoded_secret_detected: bool = False
    network_transport_requested: bool = False
    external_api_requested: bool = False
    order_execution_requested: bool = False
    position_mutation_requested: bool = False
    account_access_requested: bool = False
    data_access_requested: bool = False
    paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_plan_requested: bool = False
    offline_runner_preparation_score: int | None = None
    scope_score: int | None = None
    execution_mode_score: int | None = None
    input_contract_score: int | None = None
    synthetic_market_context_score: int | None = None
    read_only_broker_simulation_score: int | None = None
    no_real_broker_score: int | None = None
    no_secret_read_score: int | None = None
    network_score: int | None = None
    http_websocket_socket_score: int | None = None
    account_snapshot_score: int | None = None
    market_data_snapshot_score: int | None = None
    order_blocking_score: int | None = None
    position_mutation_score: int | None = None
    strategy_signal_observation_score: int | None = None
    risk_observation_score: int | None = None
    profitability_observation_score: int | None = None
    consistency_observation_score: int | None = None
    journal_score: int | None = None
    observability_score: int | None = None
    human_approval_score: int | None = None
    stop_conditions_score: int | None = None
    success_score: int | None = None
    failure_score: int | None = None
    audit_score: int | None = None
    go_no_go_score: int | None = None
    abort_score: int | None = None


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewResult:
    state: PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewState
    decision: PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewDecision
    score: PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewScore
    review_score: int = 0
    risks: tuple[Risk, ...] = ()
    recommendations: tuple[PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewRecommendation, ...] = ()
    summary: str = ""
    markdown_report: str = ""
    offline_only: bool = True
    sandbox_only: bool = True
    review_only: bool = True
    runner_created: bool = False
    runner_executed: bool = False
    dry_run_executed: bool = False
    next_phase: str = "PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN"
    scope_preparation_review: OfflineRunnerScopePreparationReviewFinding = field(default_factory=OfflineRunnerScopePreparationReviewFinding)
    execution_mode_preparation_review: OfflineRunnerExecutionModePreparationReviewFinding = field(default_factory=OfflineRunnerExecutionModePreparationReviewFinding)
    input_preparation_review: OfflineRunnerInputPreparationReviewFinding = field(default_factory=OfflineRunnerInputPreparationReviewFinding)
    synthetic_market_context_preparation_review: OfflineRunnerSyntheticMarketContextPreparationReviewFinding = field(default_factory=OfflineRunnerSyntheticMarketContextPreparationReviewFinding)
    read_only_broker_simulation_preparation_review: OfflineRunnerReadOnlyBrokerSimulationPreparationReviewFinding = field(default_factory=OfflineRunnerReadOnlyBrokerSimulationPreparationReviewFinding)
    no_real_broker_guard_review: OfflineRunnerNoRealBrokerGuardReviewFinding = field(default_factory=OfflineRunnerNoRealBrokerGuardReviewFinding)
    no_secret_read_guard_review: OfflineRunnerNoSecretReadGuardReviewFinding = field(default_factory=OfflineRunnerNoSecretReadGuardReviewFinding)
    network_block_guard_review: OfflineRunnerNetworkBlockGuardReviewFinding = field(default_factory=OfflineRunnerNetworkBlockGuardReviewFinding)
    http_websocket_socket_block_guard_review: OfflineRunnerNetworkBlockGuardReviewFinding = field(default_factory=lambda: OfflineRunnerNetworkBlockGuardReviewFinding(name="offline_runner_http_websocket_socket_block_guard_review"))
    account_snapshot_preparation_review: OfflineRunnerAccountSnapshotPreparationReviewFinding = field(default_factory=OfflineRunnerAccountSnapshotPreparationReviewFinding)
    market_data_snapshot_preparation_review: OfflineRunnerMarketDataSnapshotPreparationReviewFinding = field(default_factory=OfflineRunnerMarketDataSnapshotPreparationReviewFinding)
    order_blocking_guard_review: OfflineRunnerOrderBlockingGuardReviewFinding = field(default_factory=OfflineRunnerOrderBlockingGuardReviewFinding)
    position_mutation_blocking_guard_review: OfflineRunnerPositionMutationBlockingGuardReviewFinding = field(default_factory=OfflineRunnerPositionMutationBlockingGuardReviewFinding)
    strategy_signal_observation_preparation_review: OfflineRunnerStrategySignalObservationPreparationReviewFinding = field(default_factory=OfflineRunnerStrategySignalObservationPreparationReviewFinding)
    risk_observation_preparation_review: OfflineRunnerRiskObservationPreparationReviewFinding = field(default_factory=OfflineRunnerRiskObservationPreparationReviewFinding)
    profitability_observation_preparation_review: OfflineRunnerProfitabilityObservationPreparationReviewFinding = field(default_factory=OfflineRunnerProfitabilityObservationPreparationReviewFinding)
    consistency_observation_preparation_review: OfflineRunnerConsistencyObservationPreparationReviewFinding = field(default_factory=OfflineRunnerConsistencyObservationPreparationReviewFinding)
    journal_preparation_review: OfflineRunnerJournalPreparationReviewFinding = field(default_factory=OfflineRunnerJournalPreparationReviewFinding)
    observability_preparation_review: OfflineRunnerObservabilityPreparationReviewFinding = field(default_factory=OfflineRunnerObservabilityPreparationReviewFinding)
    human_approval_preparation_review: OfflineRunnerHumanApprovalPreparationReviewFinding = field(default_factory=OfflineRunnerHumanApprovalPreparationReviewFinding)
    stop_conditions_preparation_review: OfflineRunnerStopConditionPreparationReviewFinding = field(default_factory=OfflineRunnerStopConditionPreparationReviewFinding)
    success_criteria_preparation_review: OfflineRunnerSuccessCriteriaPreparationReviewFinding = field(default_factory=OfflineRunnerSuccessCriteriaPreparationReviewFinding)
    failure_criteria_preparation_review: OfflineRunnerFailureCriteriaPreparationReviewFinding = field(default_factory=OfflineRunnerFailureCriteriaPreparationReviewFinding)
    audit_preparation_review: OfflineRunnerAuditPreparationReviewFinding = field(default_factory=OfflineRunnerAuditPreparationReviewFinding)
    go_no_go_preparation_review: OfflineRunnerGoNoGoPreparationReviewFinding = field(default_factory=OfflineRunnerGoNoGoPreparationReviewFinding)
    abort_preparation_review: OfflineRunnerAbortPreparationReviewFinding = field(default_factory=OfflineRunnerAbortPreparationReviewFinding)
    findings: tuple[_OfflineRunnerPreparationReviewFinding, ...] = field(default_factory=tuple)
