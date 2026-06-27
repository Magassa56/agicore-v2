"""Models for Paper Broker Read-Only Connection Dry Run Controlled Offline Runner Final Plan."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanState(StrEnum):
    NOT_READY = "NOT_READY"
    FINAL_OFFLINE_RUNNER_PLAN_INPUT_INVALID = "FINAL_OFFLINE_RUNNER_PLAN_INPUT_INVALID"
    FINAL_OFFLINE_RUNNER_PLAN_BLOCKED = "FINAL_OFFLINE_RUNNER_PLAN_BLOCKED"
    FINAL_OFFLINE_RUNNER_PLAN_COMPLETED_WITH_WARNINGS = "FINAL_OFFLINE_RUNNER_PLAN_COMPLETED_WITH_WARNINGS"
    FINAL_OFFLINE_RUNNER_PLAN_COMPLETED = "FINAL_OFFLINE_RUNNER_PLAN_COMPLETED"
    READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE = "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE"


class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanDecision(StrEnum):
    BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN = "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN"
    REQUIRE_OFFLINE_RUNNER_PREPARATION_REVIEW_FIXES = "REQUIRE_OFFLINE_RUNNER_PREPARATION_REVIEW_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_SCOPE_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_SCOPE_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_EXECUTION_MODE_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_EXECUTION_MODE_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_INPUT_CONTRACT_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_INPUT_CONTRACT_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_NO_REAL_BROKER_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_NO_REAL_BROKER_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_NO_SECRET_READ_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_NO_SECRET_READ_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_NETWORK_BLOCK_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_NETWORK_BLOCK_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_ORDER_BLOCKING_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_ORDER_BLOCKING_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_RISK_OBSERVATION_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_RISK_OBSERVATION_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_JOURNAL_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_JOURNAL_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_OBSERVABILITY_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_OBSERVABILITY_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_HUMAN_APPROVAL_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_HUMAN_APPROVAL_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_STOP_CONDITION_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_STOP_CONDITION_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_SUCCESS_FAILURE_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_SUCCESS_FAILURE_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_AUDIT_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_AUDIT_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_GO_NO_GO_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_GO_NO_GO_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_ABORT_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_ABORT_FIXES"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN = "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN"


class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanRisk(StrEnum):
    OFFLINE_RUNNER_PREPARATION_REVIEW_NOT_APPROVED = "OFFLINE_RUNNER_PREPARATION_REVIEW_NOT_APPROVED"
    FINAL_OFFLINE_RUNNER_SCOPE_UNCLEAR = "FINAL_OFFLINE_RUNNER_SCOPE_UNCLEAR"
    FINAL_OFFLINE_RUNNER_EXECUTION_MODE_UNSAFE = "FINAL_OFFLINE_RUNNER_EXECUTION_MODE_UNSAFE"
    FINAL_OFFLINE_RUNNER_INPUT_CONTRACT_MISSING = "FINAL_OFFLINE_RUNNER_INPUT_CONTRACT_MISSING"
    FINAL_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_MISSING = "FINAL_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_MISSING"
    FINAL_OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_UNSAFE = "FINAL_OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_UNSAFE"
    FINAL_OFFLINE_RUNNER_REAL_BROKER_POLICY_UNSAFE = "FINAL_OFFLINE_RUNNER_REAL_BROKER_POLICY_UNSAFE"
    FINAL_OFFLINE_RUNNER_SECRET_READ_POLICY_UNSAFE = "FINAL_OFFLINE_RUNNER_SECRET_READ_POLICY_UNSAFE"
    FINAL_OFFLINE_RUNNER_NETWORK_NOT_BLOCKED = "FINAL_OFFLINE_RUNNER_NETWORK_NOT_BLOCKED"
    FINAL_OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED = "FINAL_OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED"
    FINAL_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_UNSAFE = "FINAL_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_UNSAFE"
    FINAL_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_UNSAFE = "FINAL_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_UNSAFE"
    FINAL_OFFLINE_RUNNER_ORDER_BLOCKING_UNSAFE = "FINAL_OFFLINE_RUNNER_ORDER_BLOCKING_UNSAFE"
    FINAL_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_UNSAFE = "FINAL_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_UNSAFE"
    FINAL_OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_MISSING = "FINAL_OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_MISSING"
    FINAL_OFFLINE_RUNNER_RISK_OBSERVATION_MISSING = "FINAL_OFFLINE_RUNNER_RISK_OBSERVATION_MISSING"
    FINAL_OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_MISSING = "FINAL_OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_MISSING"
    FINAL_OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_MISSING = "FINAL_OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_MISSING"
    FINAL_OFFLINE_RUNNER_JOURNAL_MISSING = "FINAL_OFFLINE_RUNNER_JOURNAL_MISSING"
    FINAL_OFFLINE_RUNNER_OBSERVABILITY_MISSING = "FINAL_OFFLINE_RUNNER_OBSERVABILITY_MISSING"
    FINAL_OFFLINE_RUNNER_HUMAN_APPROVAL_MISSING = "FINAL_OFFLINE_RUNNER_HUMAN_APPROVAL_MISSING"
    FINAL_OFFLINE_RUNNER_STOP_CONDITIONS_MISSING = "FINAL_OFFLINE_RUNNER_STOP_CONDITIONS_MISSING"
    FINAL_OFFLINE_RUNNER_SUCCESS_CRITERIA_MISSING = "FINAL_OFFLINE_RUNNER_SUCCESS_CRITERIA_MISSING"
    FINAL_OFFLINE_RUNNER_FAILURE_CRITERIA_MISSING = "FINAL_OFFLINE_RUNNER_FAILURE_CRITERIA_MISSING"
    FINAL_OFFLINE_RUNNER_AUDIT_PLAN_MISSING = "FINAL_OFFLINE_RUNNER_AUDIT_PLAN_MISSING"
    FINAL_OFFLINE_RUNNER_GO_NO_GO_POLICY_MISSING = "FINAL_OFFLINE_RUNNER_GO_NO_GO_POLICY_MISSING"
    FINAL_OFFLINE_RUNNER_ABORT_POLICY_MISSING = "FINAL_OFFLINE_RUNNER_ABORT_POLICY_MISSING"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE = "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE"


class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanRecommendation(StrEnum):
    HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE = "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE"
    APPROVE_OFFLINE_RUNNER_PREPARATION_REVIEW_FIRST = "APPROVE_OFFLINE_RUNNER_PREPARATION_REVIEW_FIRST"
    FIX_FINAL_OFFLINE_RUNNER_SCOPE = "FIX_FINAL_OFFLINE_RUNNER_SCOPE"
    FIX_FINAL_OFFLINE_RUNNER_EXECUTION_MODE = "FIX_FINAL_OFFLINE_RUNNER_EXECUTION_MODE"
    FIX_FINAL_OFFLINE_RUNNER_INPUT_CONTRACT = "FIX_FINAL_OFFLINE_RUNNER_INPUT_CONTRACT"
    FIX_FINAL_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT = "FIX_FINAL_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT"
    FIX_FINAL_OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION = "FIX_FINAL_OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION"
    FIX_FINAL_OFFLINE_RUNNER_NO_REAL_BROKER_POLICY = "FIX_FINAL_OFFLINE_RUNNER_NO_REAL_BROKER_POLICY"
    FIX_FINAL_OFFLINE_RUNNER_NO_SECRET_READ_POLICY = "FIX_FINAL_OFFLINE_RUNNER_NO_SECRET_READ_POLICY"
    FIX_FINAL_OFFLINE_RUNNER_NETWORK_BLOCK_POLICY = "FIX_FINAL_OFFLINE_RUNNER_NETWORK_BLOCK_POLICY"
    FIX_FINAL_OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_BLOCK_POLICY = "FIX_FINAL_OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_BLOCK_POLICY"
    FIX_FINAL_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT = "FIX_FINAL_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT"
    FIX_FINAL_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT = "FIX_FINAL_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT"
    FIX_FINAL_OFFLINE_RUNNER_ORDER_BLOCKING = "FIX_FINAL_OFFLINE_RUNNER_ORDER_BLOCKING"
    FIX_FINAL_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING = "FIX_FINAL_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING"
    FIX_FINAL_OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION = "FIX_FINAL_OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION"
    FIX_FINAL_OFFLINE_RUNNER_RISK_OBSERVATION = "FIX_FINAL_OFFLINE_RUNNER_RISK_OBSERVATION"
    FIX_FINAL_OFFLINE_RUNNER_PROFITABILITY_OBSERVATION = "FIX_FINAL_OFFLINE_RUNNER_PROFITABILITY_OBSERVATION"
    FIX_FINAL_OFFLINE_RUNNER_CONSISTENCY_OBSERVATION = "FIX_FINAL_OFFLINE_RUNNER_CONSISTENCY_OBSERVATION"
    FIX_FINAL_OFFLINE_RUNNER_JOURNAL = "FIX_FINAL_OFFLINE_RUNNER_JOURNAL"
    FIX_FINAL_OFFLINE_RUNNER_OBSERVABILITY = "FIX_FINAL_OFFLINE_RUNNER_OBSERVABILITY"
    FIX_FINAL_OFFLINE_RUNNER_HUMAN_APPROVAL = "FIX_FINAL_OFFLINE_RUNNER_HUMAN_APPROVAL"
    FIX_FINAL_OFFLINE_RUNNER_STOP_CONDITIONS = "FIX_FINAL_OFFLINE_RUNNER_STOP_CONDITIONS"
    FIX_FINAL_OFFLINE_RUNNER_SUCCESS_FAILURE = "FIX_FINAL_OFFLINE_RUNNER_SUCCESS_FAILURE"
    FIX_FINAL_OFFLINE_RUNNER_AUDIT = "FIX_FINAL_OFFLINE_RUNNER_AUDIT"
    FIX_FINAL_OFFLINE_RUNNER_GO_NO_GO = "FIX_FINAL_OFFLINE_RUNNER_GO_NO_GO"
    FIX_FINAL_OFFLINE_RUNNER_ABORT = "FIX_FINAL_OFFLINE_RUNNER_ABORT"
    RESTORE_OFFLINE_BOUNDARIES = "RESTORE_OFFLINE_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE = "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE"
    RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN_SUITE = "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN_SUITE"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE = "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE"


Risk = PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanRisk

@dataclass(frozen=True)
class _FinalOfflineRunnerPlanArtifact:
    name: str
    score: int = 0
    defined: bool = False
    risks: tuple[Risk, ...] = ()
    details: tuple[str, ...] = ()

@dataclass(frozen=True)
class FinalOfflineRunnerScope(_FinalOfflineRunnerPlanArtifact):
    offline_only: bool = False
    sandbox_only: bool = False
    final_plan_only: bool = False
    no_runner_executable_created: bool = False

@dataclass(frozen=True)
class FinalOfflineRunnerExecutionMode(_FinalOfflineRunnerPlanArtifact):
    controlled_offline_mode: bool = False
    deterministic_mode: bool = False
    in_memory_only: bool = False
    no_dry_run_execution: bool = False

@dataclass(frozen=True)
class FinalOfflineRunnerInputContract(_FinalOfflineRunnerPlanArtifact):
    schema_only_inputs: bool = False
    synthetic_inputs_only: bool = False
    no_real_credentials: bool = False

@dataclass(frozen=True)
class FinalOfflineRunnerSyntheticMarketContext(_FinalOfflineRunnerPlanArtifact):
    synthetic_context_only: bool = False
    in_memory_context: bool = False
    no_data_access: bool = False

@dataclass(frozen=True)
class FinalOfflineRunnerReadOnlyBrokerSimulationContract(_FinalOfflineRunnerPlanArtifact):
    simulated_broker_only: bool = False
    read_only_contract: bool = False
    no_real_broker: bool = False

@dataclass(frozen=True)
class FinalOfflineRunnerNoRealBrokerPolicy(_FinalOfflineRunnerPlanArtifact):
    real_broker_blocked: bool = False
    alpaca_blocked: bool = False
    broker_connection_disabled: bool = False

@dataclass(frozen=True)
class FinalOfflineRunnerNoSecretReadPolicy(_FinalOfflineRunnerPlanArtifact):
    no_api_key_read: bool = False
    no_env_var_read: bool = False
    no_hardcoded_secret: bool = False

@dataclass(frozen=True)
class FinalOfflineRunnerNetworkBlockPolicy(_FinalOfflineRunnerPlanArtifact):
    network_blocked: bool = False
    http_blocked: bool = False
    websocket_blocked: bool = False
    socket_blocked: bool = False
    external_api_blocked: bool = False

@dataclass(frozen=True)
class FinalOfflineRunnerAccountSnapshotPolicy(_FinalOfflineRunnerPlanArtifact):
    simulated_snapshot_only: bool = False
    read_only_snapshot: bool = False
    active_account_access_blocked: bool = False

@dataclass(frozen=True)
class FinalOfflineRunnerMarketDataSnapshotPolicy(_FinalOfflineRunnerPlanArtifact):
    synthetic_snapshot_only: bool = False
    read_only_snapshot: bool = False
    live_subscription_blocked: bool = False

@dataclass(frozen=True)
class FinalOfflineRunnerOrderBlockingPolicy(_FinalOfflineRunnerPlanArtifact):
    order_execution_blocked: bool = False
    real_order_blocked: bool = False
    cancel_replace_blocked: bool = False

@dataclass(frozen=True)
class FinalOfflineRunnerPositionMutationBlockingPolicy(_FinalOfflineRunnerPlanArtifact):
    position_mutation_blocked: bool = False
    close_modify_blocked: bool = False
    simulated_position_read_only: bool = False

@dataclass(frozen=True)
class FinalOfflineRunnerStrategySignalObservationPlan(_FinalOfflineRunnerPlanArtifact):
    observation_only: bool = False
    no_signal_execution: bool = False
    signal_trace_required: bool = False

@dataclass(frozen=True)
class FinalOfflineRunnerRiskObservationPlan(_FinalOfflineRunnerPlanArtifact):
    observation_only: bool = False
    no_risk_action_execution: bool = False
    risk_trace_required: bool = False

@dataclass(frozen=True)
class FinalOfflineRunnerProfitabilityObservationPlan(_FinalOfflineRunnerPlanArtifact):
    observation_only: bool = False
    no_profit_promise: bool = False
    profitability_trace_required: bool = False

@dataclass(frozen=True)
class FinalOfflineRunnerConsistencyObservationPlan(_FinalOfflineRunnerPlanArtifact):
    observation_only: bool = False
    deterministic_consistency_checks: bool = False
    consistency_trace_required: bool = False

@dataclass(frozen=True)
class FinalOfflineRunnerJournalPlan(_FinalOfflineRunnerPlanArtifact):
    offline_journal_required: bool = False
    no_secret_material_logged: bool = False
    plan_events_recorded: bool = False

@dataclass(frozen=True)
class FinalOfflineRunnerObservabilityPlan(_FinalOfflineRunnerPlanArtifact):
    offline_events_defined: bool = False
    no_connection_attempt_metrics: bool = False
    sensitive_values_redacted: bool = False

@dataclass(frozen=True)
class FinalOfflineRunnerHumanApprovalPlan(_FinalOfflineRunnerPlanArtifact):
    human_approval_required: bool = False
    approval_before_final_safety_gate: bool = False
    evidence_required: bool = False

@dataclass(frozen=True)
class FinalOfflineRunnerStopConditionPlan(_FinalOfflineRunnerPlanArtifact):
    stop_on_secret_read: bool = False
    stop_on_network_request: bool = False
    stop_on_order_or_position_request: bool = False
    stop_on_account_access_request: bool = False

@dataclass(frozen=True)
class FinalOfflineRunnerSuccessCriteria(_FinalOfflineRunnerPlanArtifact):
    no_boundary_violation_required: bool = False
    all_plans_defined: bool = False
    no_runner_execution_required: bool = False

@dataclass(frozen=True)
class FinalOfflineRunnerFailureCriteria(_FinalOfflineRunnerPlanArtifact):
    fail_on_boundary_violation: bool = False
    fail_on_missing_plan: bool = False
    fail_on_execution_request: bool = False

@dataclass(frozen=True)
class FinalOfflineRunnerAuditPlan(_FinalOfflineRunnerPlanArtifact):
    audit_events_defined: bool = False
    boundary_evidence_required: bool = False
    immutable_final_plan_record_required: bool = False

@dataclass(frozen=True)
class FinalOfflineRunnerGoNoGoPolicy(_FinalOfflineRunnerPlanArtifact):
    go_no_go_required: bool = False
    no_go_on_risk: bool = False
    next_phase_requires_clean_final_plan: bool = False

@dataclass(frozen=True)
class FinalOfflineRunnerAbortPolicy(_FinalOfflineRunnerPlanArtifact):
    abort_on_secret_read: bool = False
    abort_on_network_or_broker_request: bool = False
    abort_on_order_or_position_request: bool = False

@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanScore:
    overall_score: int = 0
    offline_runner_preparation_review_score: int = 0
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
class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanInput:
    paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review: Any | None = None
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
    offline_runner_preparation_review_approved: bool | None = None
    final_offline_runner_scope_defined: bool = True
    final_offline_runner_execution_mode_defined: bool = True
    final_offline_runner_input_contract_defined: bool = True
    final_offline_runner_synthetic_market_context_defined: bool = True
    final_offline_runner_read_only_broker_simulation_defined: bool = True
    final_offline_runner_no_real_broker_policy_defined: bool = True
    final_offline_runner_no_secret_read_policy_defined: bool = True
    final_offline_runner_network_block_policy_defined: bool = True
    final_offline_runner_http_websocket_socket_block_policy_defined: bool = True
    final_offline_runner_account_snapshot_policy_defined: bool = True
    final_offline_runner_market_data_snapshot_policy_defined: bool = True
    final_offline_runner_order_blocking_policy_defined: bool = True
    final_offline_runner_position_mutation_blocking_policy_defined: bool = True
    final_offline_runner_strategy_signal_observation_plan_defined: bool = True
    final_offline_runner_risk_observation_plan_defined: bool = True
    final_offline_runner_profitability_observation_plan_defined: bool = True
    final_offline_runner_consistency_observation_plan_defined: bool = True
    final_offline_runner_journal_plan_defined: bool = True
    final_offline_runner_observability_plan_defined: bool = True
    final_offline_runner_human_approval_plan_defined: bool = True
    final_offline_runner_stop_conditions_plan_defined: bool = True
    final_offline_runner_success_criteria_defined: bool = True
    final_offline_runner_failure_criteria_defined: bool = True
    final_offline_runner_audit_plan_defined: bool = True
    final_offline_runner_go_no_go_policy_defined: bool = True
    final_offline_runner_abort_policy_defined: bool = True
    offline_mode_enforced: bool = True
    sandbox_mode_enforced: bool = True
    final_plan_only: bool = True
    no_runner_executable_created: bool = True
    no_runner_execution: bool = True
    no_dry_run_execution: bool = True
    deterministic_mode: bool = True
    in_memory_only: bool = True
    synthetic_inputs_only: bool = True
    synthetic_market_in_memory: bool = True
    simulated_broker_only: bool = True
    read_only_broker_simulation: bool = True
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
    account_snapshot_simulated: bool = True
    account_snapshot_read_only: bool = True
    market_data_snapshot_synthetic: bool = True
    market_data_snapshot_read_only: bool = True
    no_real_order: bool = True
    order_blocking_enforced: bool = True
    cancel_replace_blocked: bool = True
    no_position_mutation: bool = True
    position_mutation_blocked: bool = True
    strategy_signal_observation_only: bool = True
    risk_observation_only: bool = True
    profitability_observation_only: bool = True
    no_profit_promise: bool = True
    consistency_observation_only: bool = True
    offline_journal_required: bool = True
    offline_observability_required: bool = True
    human_approval_required: bool = True
    approval_before_final_safety_gate: bool = True
    stop_on_secret_read: bool = True
    stop_on_network_request: bool = True
    stop_on_order_or_position_request: bool = True
    stop_on_account_access_request: bool = True
    success_no_boundary_violation_required: bool = True
    failure_on_boundary_violation: bool = True
    audit_plan_required: bool = True
    go_no_go_required: bool = True
    abort_on_boundary_violation: bool = True
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
    paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_safety_gate_requested: bool = False
    offline_runner_preparation_review_score: int | None = None
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
class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanResult:
    state: PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanState
    decision: PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanDecision
    score: PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanScore
    risks: tuple[Risk, ...] = ()
    recommendations: tuple[PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanRecommendation, ...] = ()
    summary: str = ""
    markdown_report: str = ""
    offline_only: bool = True
    sandbox_only: bool = True
    final_plan_only: bool = True
    runner_created: bool = False
    runner_executed: bool = False
    dry_run_executed: bool = False
    next_phase: str = "PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE"
    scope: FinalOfflineRunnerScope | None = None
    execution_mode: FinalOfflineRunnerExecutionMode | None = None
    input_contract: FinalOfflineRunnerInputContract | None = None
    synthetic_market_context: FinalOfflineRunnerSyntheticMarketContext | None = None
    read_only_broker_simulation: FinalOfflineRunnerReadOnlyBrokerSimulationContract | None = None
    no_real_broker_policy: FinalOfflineRunnerNoRealBrokerPolicy | None = None
    no_secret_read_policy: FinalOfflineRunnerNoSecretReadPolicy | None = None
    network_block_policy: FinalOfflineRunnerNetworkBlockPolicy | None = None
    http_websocket_socket_block_policy: FinalOfflineRunnerNetworkBlockPolicy | None = None
    account_snapshot_policy: FinalOfflineRunnerAccountSnapshotPolicy | None = None
    market_data_snapshot_policy: FinalOfflineRunnerMarketDataSnapshotPolicy | None = None
    order_blocking_policy: FinalOfflineRunnerOrderBlockingPolicy | None = None
    position_mutation_blocking_policy: FinalOfflineRunnerPositionMutationBlockingPolicy | None = None
    strategy_signal_observation_plan: FinalOfflineRunnerStrategySignalObservationPlan | None = None
    risk_observation_plan: FinalOfflineRunnerRiskObservationPlan | None = None
    profitability_observation_plan: FinalOfflineRunnerProfitabilityObservationPlan | None = None
    consistency_observation_plan: FinalOfflineRunnerConsistencyObservationPlan | None = None
    journal_plan: FinalOfflineRunnerJournalPlan | None = None
    observability_plan: FinalOfflineRunnerObservabilityPlan | None = None
    human_approval_plan: FinalOfflineRunnerHumanApprovalPlan | None = None
    stop_conditions_plan: FinalOfflineRunnerStopConditionPlan | None = None
    success_criteria: FinalOfflineRunnerSuccessCriteria | None = None
    failure_criteria: FinalOfflineRunnerFailureCriteria | None = None
    audit_plan: FinalOfflineRunnerAuditPlan | None = None
    go_no_go_policy: FinalOfflineRunnerGoNoGoPolicy | None = None
    abort_policy: FinalOfflineRunnerAbortPolicy | None = None
    artifacts: tuple[_FinalOfflineRunnerPlanArtifact, ...] = field(default_factory=tuple)
