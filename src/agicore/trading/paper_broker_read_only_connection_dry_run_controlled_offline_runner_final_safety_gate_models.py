"""Models for Paper Broker Read-Only Connection Dry Run Controlled Offline Runner Safety Gate."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateState(StrEnum):
    NOT_READY = "NOT_READY"
    FINAL_OFFLINE_RUNNER_SAFETY_GATE_INPUT_INVALID = "FINAL_OFFLINE_RUNNER_SAFETY_GATE_INPUT_INVALID"
    FINAL_OFFLINE_RUNNER_SAFETY_GATE_BLOCKED = "FINAL_OFFLINE_RUNNER_SAFETY_GATE_BLOCKED"
    FINAL_OFFLINE_RUNNER_SAFETY_GATE_COMPLETED_WITH_WARNINGS = "FINAL_OFFLINE_RUNNER_SAFETY_GATE_COMPLETED_WITH_WARNINGS"
    FINAL_OFFLINE_RUNNER_SAFETY_GATE_COMPLETED = "FINAL_OFFLINE_RUNNER_SAFETY_GATE_COMPLETED"
    READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN = "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN"


class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateDecision(StrEnum):
    BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE = "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE"
    REQUIRE_FINAL_OFFLINE_RUNNER_PLAN_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_PLAN_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_SCOPE_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_SCOPE_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_EXECUTION_MODE_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_EXECUTION_MODE_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_INPUT_CONTRACT_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_INPUT_CONTRACT_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_SYNTHETIC_MARKET_CONTEXT_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_SYNTHETIC_MARKET_CONTEXT_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_READ_ONLY_BROKER_SIMULATION_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_READ_ONLY_BROKER_SIMULATION_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_NO_REAL_BROKER_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_NO_REAL_BROKER_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_NO_SECRET_READ_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_NO_SECRET_READ_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_NETWORK_BLOCK_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_NETWORK_BLOCK_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_ACCOUNT_SNAPSHOT_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_ACCOUNT_SNAPSHOT_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_MARKET_DATA_SNAPSHOT_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_MARKET_DATA_SNAPSHOT_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_ORDER_BLOCKING_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_ORDER_BLOCKING_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_POSITION_MUTATION_BLOCKING_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_POSITION_MUTATION_BLOCKING_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_STRATEGY_SIGNAL_OBSERVATION_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_STRATEGY_SIGNAL_OBSERVATION_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_RISK_OBSERVATION_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_RISK_OBSERVATION_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_PROFITABILITY_OBSERVATION_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_PROFITABILITY_OBSERVATION_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_CONSISTENCY_OBSERVATION_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_CONSISTENCY_OBSERVATION_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_JOURNAL_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_JOURNAL_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_OBSERVABILITY_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_OBSERVABILITY_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_HUMAN_APPROVAL_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_HUMAN_APPROVAL_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_STOP_CONDITION_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_STOP_CONDITION_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_SUCCESS_FAILURE_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_SUCCESS_FAILURE_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_AUDIT_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_AUDIT_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_GO_NO_GO_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_GO_NO_GO_FIXES"
    REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_ABORT_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_ABORT_FIXES"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE = "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE"


class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateRisk(StrEnum):
    FINAL_OFFLINE_RUNNER_PLAN_NOT_APPROVED = "FINAL_OFFLINE_RUNNER_PLAN_NOT_APPROVED"
    FINAL_OFFLINE_RUNNER_SAFETY_SCOPE_BOUNDARY_FAILED = "FINAL_OFFLINE_RUNNER_SAFETY_SCOPE_BOUNDARY_FAILED"
    FINAL_OFFLINE_RUNNER_SAFETY_EXECUTION_MODE_BOUNDARY_FAILED = "FINAL_OFFLINE_RUNNER_SAFETY_EXECUTION_MODE_BOUNDARY_FAILED"
    FINAL_OFFLINE_RUNNER_SAFETY_INPUT_CONTRACT_BOUNDARY_FAILED = "FINAL_OFFLINE_RUNNER_SAFETY_INPUT_CONTRACT_BOUNDARY_FAILED"
    FINAL_OFFLINE_RUNNER_SAFETY_SYNTHETIC_MARKET_CONTEXT_BOUNDARY_FAILED = "FINAL_OFFLINE_RUNNER_SAFETY_SYNTHETIC_MARKET_CONTEXT_BOUNDARY_FAILED"
    FINAL_OFFLINE_RUNNER_SAFETY_READ_ONLY_BROKER_SIMULATION_BOUNDARY_FAILED = "FINAL_OFFLINE_RUNNER_SAFETY_READ_ONLY_BROKER_SIMULATION_BOUNDARY_FAILED"
    FINAL_OFFLINE_RUNNER_SAFETY_REAL_BROKER_BOUNDARY_FAILED = "FINAL_OFFLINE_RUNNER_SAFETY_REAL_BROKER_BOUNDARY_FAILED"
    FINAL_OFFLINE_RUNNER_SAFETY_SECRET_READ_BOUNDARY_FAILED = "FINAL_OFFLINE_RUNNER_SAFETY_SECRET_READ_BOUNDARY_FAILED"
    FINAL_OFFLINE_RUNNER_SAFETY_NETWORK_BLOCK_BOUNDARY_FAILED = "FINAL_OFFLINE_RUNNER_SAFETY_NETWORK_BLOCK_BOUNDARY_FAILED"
    FINAL_OFFLINE_RUNNER_SAFETY_HTTP_WEBSOCKET_SOCKET_BLOCK_BOUNDARY_FAILED = "FINAL_OFFLINE_RUNNER_SAFETY_HTTP_WEBSOCKET_SOCKET_BLOCK_BOUNDARY_FAILED"
    FINAL_OFFLINE_RUNNER_SAFETY_ACCOUNT_SNAPSHOT_BOUNDARY_FAILED = "FINAL_OFFLINE_RUNNER_SAFETY_ACCOUNT_SNAPSHOT_BOUNDARY_FAILED"
    FINAL_OFFLINE_RUNNER_SAFETY_MARKET_DATA_SNAPSHOT_BOUNDARY_FAILED = "FINAL_OFFLINE_RUNNER_SAFETY_MARKET_DATA_SNAPSHOT_BOUNDARY_FAILED"
    FINAL_OFFLINE_RUNNER_SAFETY_ORDER_BLOCKING_BOUNDARY_FAILED = "FINAL_OFFLINE_RUNNER_SAFETY_ORDER_BLOCKING_BOUNDARY_FAILED"
    FINAL_OFFLINE_RUNNER_SAFETY_POSITION_MUTATION_BLOCKING_BOUNDARY_FAILED = "FINAL_OFFLINE_RUNNER_SAFETY_POSITION_MUTATION_BLOCKING_BOUNDARY_FAILED"
    FINAL_OFFLINE_RUNNER_SAFETY_STRATEGY_SIGNAL_OBSERVATION_BOUNDARY_FAILED = "FINAL_OFFLINE_RUNNER_SAFETY_STRATEGY_SIGNAL_OBSERVATION_BOUNDARY_FAILED"
    FINAL_OFFLINE_RUNNER_SAFETY_RISK_OBSERVATION_BOUNDARY_FAILED = "FINAL_OFFLINE_RUNNER_SAFETY_RISK_OBSERVATION_BOUNDARY_FAILED"
    FINAL_OFFLINE_RUNNER_SAFETY_PROFITABILITY_OBSERVATION_BOUNDARY_FAILED = "FINAL_OFFLINE_RUNNER_SAFETY_PROFITABILITY_OBSERVATION_BOUNDARY_FAILED"
    FINAL_OFFLINE_RUNNER_SAFETY_CONSISTENCY_OBSERVATION_BOUNDARY_FAILED = "FINAL_OFFLINE_RUNNER_SAFETY_CONSISTENCY_OBSERVATION_BOUNDARY_FAILED"
    FINAL_OFFLINE_RUNNER_SAFETY_JOURNAL_BOUNDARY_FAILED = "FINAL_OFFLINE_RUNNER_SAFETY_JOURNAL_BOUNDARY_FAILED"
    FINAL_OFFLINE_RUNNER_SAFETY_OBSERVABILITY_BOUNDARY_FAILED = "FINAL_OFFLINE_RUNNER_SAFETY_OBSERVABILITY_BOUNDARY_FAILED"
    FINAL_OFFLINE_RUNNER_SAFETY_HUMAN_APPROVAL_BOUNDARY_FAILED = "FINAL_OFFLINE_RUNNER_SAFETY_HUMAN_APPROVAL_BOUNDARY_FAILED"
    FINAL_OFFLINE_RUNNER_SAFETY_STOP_CONDITION_BOUNDARY_FAILED = "FINAL_OFFLINE_RUNNER_SAFETY_STOP_CONDITION_BOUNDARY_FAILED"
    FINAL_OFFLINE_RUNNER_SAFETY_SUCCESS_FAILURE_BOUNDARY_FAILED = "FINAL_OFFLINE_RUNNER_SAFETY_SUCCESS_FAILURE_BOUNDARY_FAILED"
    FINAL_OFFLINE_RUNNER_SAFETY_AUDIT_BOUNDARY_FAILED = "FINAL_OFFLINE_RUNNER_SAFETY_AUDIT_BOUNDARY_FAILED"
    FINAL_OFFLINE_RUNNER_SAFETY_GO_NO_GO_BOUNDARY_FAILED = "FINAL_OFFLINE_RUNNER_SAFETY_GO_NO_GO_BOUNDARY_FAILED"
    FINAL_OFFLINE_RUNNER_SAFETY_ABORT_BOUNDARY_FAILED = "FINAL_OFFLINE_RUNNER_SAFETY_ABORT_BOUNDARY_FAILED"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN = "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN"


class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateRecommendation(StrEnum):
    HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN = "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN"
    APPROVE_OFFLINE_RUNNER_PLAN_FIRST = "APPROVE_OFFLINE_RUNNER_PLAN_FIRST"
    HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_SCOPE = "HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_SCOPE"
    HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_EXECUTION_MODE = "HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_EXECUTION_MODE"
    HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_INPUT_CONTRACT = "HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_INPUT_CONTRACT"
    HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_SYNTHETIC_MARKET_CONTEXT = "HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_SYNTHETIC_MARKET_CONTEXT"
    HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_READ_ONLY_BROKER_SIMULATION = "HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_READ_ONLY_BROKER_SIMULATION"
    RESTORE_OFFLINE_RUNNER_REAL_BROKER_BOUNDARY = "RESTORE_OFFLINE_RUNNER_REAL_BROKER_BOUNDARY"
    HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_NO_SECRET_READ = "HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_NO_SECRET_READ"
    BLOCK_FINAL_OFFLINE_RUNNER_SAFETY_NETWORK = "BLOCK_FINAL_OFFLINE_RUNNER_SAFETY_NETWORK"
    BLOCK_FINAL_OFFLINE_RUNNER_SAFETY_HTTP_WEBSOCKET_SOCKET = "BLOCK_FINAL_OFFLINE_RUNNER_SAFETY_HTTP_WEBSOCKET_SOCKET"
    HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_ACCOUNT_SNAPSHOT = "HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_ACCOUNT_SNAPSHOT"
    HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_MARKET_DATA_SNAPSHOT = "HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_MARKET_DATA_SNAPSHOT"
    HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_ORDER_BLOCKING = "HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_ORDER_BLOCKING"
    HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_POSITION_MUTATION_BLOCKING = "HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_POSITION_MUTATION_BLOCKING"
    HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_STRATEGY_SIGNAL_OBSERVATION = "HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_STRATEGY_SIGNAL_OBSERVATION"
    HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_RISK_OBSERVATION = "HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_RISK_OBSERVATION"
    HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_PROFITABILITY_OBSERVATION = "HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_PROFITABILITY_OBSERVATION"
    HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_CONSISTENCY_OBSERVATION = "HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_CONSISTENCY_OBSERVATION"
    COMPLETE_FINAL_OFFLINE_RUNNER_SAFETY_JOURNAL = "COMPLETE_FINAL_OFFLINE_RUNNER_SAFETY_JOURNAL"
    COMPLETE_FINAL_OFFLINE_RUNNER_SAFETY_OBSERVABILITY = "COMPLETE_FINAL_OFFLINE_RUNNER_SAFETY_OBSERVABILITY"
    REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_HUMAN_APPROVAL = "REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_HUMAN_APPROVAL"
    HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_STOP_CONDITIONS = "HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_STOP_CONDITIONS"
    HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_SUCCESS_FAILURE = "HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_SUCCESS_FAILURE"
    COMPLETE_FINAL_OFFLINE_RUNNER_SAFETY_AUDIT = "COMPLETE_FINAL_OFFLINE_RUNNER_SAFETY_AUDIT"
    HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_GO_NO_GO = "HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_GO_NO_GO"
    HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_ABORT = "HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_ABORT"
    RESTORE_OFFLINE_BOUNDARIES = "RESTORE_OFFLINE_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN = "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN"
    RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE_SUITE = "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE_SUITE"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN = "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN"


Risk = PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateRisk


@dataclass(frozen=True)
class _FinalOfflineRunnerSafetyBoundary:
    score: int = 0
    passed: bool = False
    risks: tuple[Risk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class FinalOfflineRunnerSafetyScopeBoundary(_FinalOfflineRunnerSafetyBoundary):
    offline_only: bool = False
    sandbox_only: bool = False
    safety_gate_only: bool = False
    runner_not_created: bool = False
    runner_not_executed: bool = False


@dataclass(frozen=True)
class FinalOfflineRunnerSafetyExecutionModeBoundary(_FinalOfflineRunnerSafetyBoundary):
    controlled_offline_mode: bool = False
    deterministic_mode: bool = False
    in_memory_only: bool = False
    no_dry_run_execution: bool = False


@dataclass(frozen=True)
class FinalOfflineRunnerSafetyInputContractBoundary(_FinalOfflineRunnerSafetyBoundary):
    input_contract_valid: bool = False
    synthetic_inputs_only: bool = False
    no_real_credentials: bool = False


@dataclass(frozen=True)
class FinalOfflineRunnerSafetySyntheticMarketContextBoundary(_FinalOfflineRunnerSafetyBoundary):
    synthetic_context_valid: bool = False
    in_memory_context: bool = False
    no_data_access: bool = False


@dataclass(frozen=True)
class FinalOfflineRunnerSafetyReadOnlyBrokerSimulationBoundary(_FinalOfflineRunnerSafetyBoundary):
    simulated_broker_only: bool = False
    read_only_contract: bool = False
    no_real_broker: bool = False


@dataclass(frozen=True)
class FinalOfflineRunnerSafetyNoRealBrokerBoundary(_FinalOfflineRunnerSafetyBoundary):
    real_broker_blocked: bool = False
    alpaca_blocked: bool = False
    broker_connection_disabled: bool = False


@dataclass(frozen=True)
class FinalOfflineRunnerSafetyNoSecretReadBoundary(_FinalOfflineRunnerSafetyBoundary):
    no_api_key_read: bool = False
    no_env_var_read: bool = False
    no_hardcoded_secret: bool = False


@dataclass(frozen=True)
class FinalOfflineRunnerSafetyNetworkBlockBoundary(_FinalOfflineRunnerSafetyBoundary):
    network_blocked: bool = False
    http_blocked: bool = False
    websocket_blocked: bool = False
    socket_blocked: bool = False
    external_api_blocked: bool = False


@dataclass(frozen=True)
class FinalOfflineRunnerSafetyAccountSnapshotBoundary(_FinalOfflineRunnerSafetyBoundary):
    simulated_snapshot_only: bool = False
    read_only_snapshot: bool = False
    active_account_access_blocked: bool = False


@dataclass(frozen=True)
class FinalOfflineRunnerSafetyMarketDataSnapshotBoundary(_FinalOfflineRunnerSafetyBoundary):
    synthetic_snapshot_only: bool = False
    read_only_snapshot: bool = False
    live_subscription_blocked: bool = False


@dataclass(frozen=True)
class FinalOfflineRunnerSafetyOrderBlockingBoundary(_FinalOfflineRunnerSafetyBoundary):
    order_execution_blocked: bool = False
    real_order_blocked: bool = False
    cancel_replace_blocked: bool = False


@dataclass(frozen=True)
class FinalOfflineRunnerSafetyPositionMutationBlockingBoundary(_FinalOfflineRunnerSafetyBoundary):
    position_mutation_blocked: bool = False
    close_modify_blocked: bool = False
    simulated_position_read_only: bool = False


@dataclass(frozen=True)
class FinalOfflineRunnerSafetyStrategySignalObservationBoundary(_FinalOfflineRunnerSafetyBoundary):
    observation_only: bool = False
    no_signal_execution: bool = False
    signal_trace_required: bool = False


@dataclass(frozen=True)
class FinalOfflineRunnerSafetyRiskObservationBoundary(_FinalOfflineRunnerSafetyBoundary):
    observation_only: bool = False
    no_risk_action_execution: bool = False
    risk_trace_required: bool = False


@dataclass(frozen=True)
class FinalOfflineRunnerSafetyProfitabilityObservationBoundary(_FinalOfflineRunnerSafetyBoundary):
    observation_only: bool = False
    no_profit_promise: bool = False
    profitability_trace_required: bool = False


@dataclass(frozen=True)
class FinalOfflineRunnerSafetyConsistencyObservationBoundary(_FinalOfflineRunnerSafetyBoundary):
    observation_only: bool = False
    deterministic_consistency_checks: bool = False
    consistency_trace_required: bool = False


@dataclass(frozen=True)
class FinalOfflineRunnerSafetyJournalBoundary(_FinalOfflineRunnerSafetyBoundary):
    offline_journal_required: bool = False
    no_secret_material_logged: bool = False
    plan_events_recorded: bool = False


@dataclass(frozen=True)
class FinalOfflineRunnerSafetyObservabilityBoundary(_FinalOfflineRunnerSafetyBoundary):
    offline_events_defined: bool = False
    no_connection_attempt_metrics: bool = False
    sensitive_values_redacted: bool = False


@dataclass(frozen=True)
class FinalOfflineRunnerSafetyHumanApprovalBoundary(_FinalOfflineRunnerSafetyBoundary):
    human_approval_required: bool = False
    approval_before_preparation: bool = False
    evidence_required: bool = False


@dataclass(frozen=True)
class FinalOfflineRunnerSafetyStopConditionBoundary(_FinalOfflineRunnerSafetyBoundary):
    stop_on_secret_read: bool = False
    stop_on_network_request: bool = False
    stop_on_order_or_position_request: bool = False
    stop_on_account_access_request: bool = False


@dataclass(frozen=True)
class FinalOfflineRunnerSafetySuccessFailureBoundary(_FinalOfflineRunnerSafetyBoundary):
    success_criteria_defined: bool = False
    failure_criteria_defined: bool = False
    failure_on_boundary_violation: bool = False


@dataclass(frozen=True)
class FinalOfflineRunnerSafetyAuditBoundary(_FinalOfflineRunnerSafetyBoundary):
    audit_events_defined: bool = False
    boundary_evidence_required: bool = False
    immutable_plan_record_required: bool = False


@dataclass(frozen=True)
class FinalOfflineRunnerSafetyGoNoGoBoundary(_FinalOfflineRunnerSafetyBoundary):
    go_no_go_required: bool = False
    no_go_on_risk: bool = False
    next_phase_requires_clean_gate: bool = False


@dataclass(frozen=True)
class FinalOfflineRunnerSafetyAbortBoundary(_FinalOfflineRunnerSafetyBoundary):
    abort_on_secret_read: bool = False
    abort_on_network_or_broker_request: bool = False
    abort_on_order_or_position_request: bool = False


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateScore:
    overall_score: int = 0
    final_offline_runner_plan_score: int = 0
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
    success_failure_score: int = 0
    audit_score: int = 0
    go_no_go_score: int = 0
    abort_score: int = 0


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateInput:
    paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_plan: Any | None = None
    paper_broker_read_only_connection_dry_run_controlled_offline_runner_plan: Any | None = None
    final_offline_runner_plan_approved: bool | None = None
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

    final_offline_runner_safety_scope_boundary_verified: bool = True
    final_offline_runner_safety_execution_mode_boundary_verified: bool = True
    final_offline_runner_safety_input_contract_boundary_verified: bool = True
    final_offline_runner_safety_synthetic_market_context_boundary_verified: bool = True
    final_offline_runner_safety_read_only_broker_simulation_boundary_verified: bool = True
    final_offline_runner_safety_no_real_broker_boundary_verified: bool = True
    final_offline_runner_safety_no_secret_read_boundary_verified: bool = True
    final_offline_runner_safety_network_block_boundary_verified: bool = True
    final_offline_runner_safety_http_websocket_socket_block_boundary_verified: bool = True
    final_offline_runner_safety_account_snapshot_boundary_verified: bool = True
    final_offline_runner_safety_market_data_snapshot_boundary_verified: bool = True
    final_offline_runner_safety_order_blocking_boundary_verified: bool = True
    final_offline_runner_safety_position_mutation_blocking_boundary_verified: bool = True
    final_offline_runner_safety_strategy_signal_observation_boundary_verified: bool = True
    final_offline_runner_safety_risk_observation_boundary_verified: bool = True
    final_offline_runner_safety_profitability_observation_boundary_verified: bool = True
    final_offline_runner_safety_consistency_observation_boundary_verified: bool = True
    final_offline_runner_safety_journal_boundary_verified: bool = True
    final_offline_runner_safety_observability_boundary_verified: bool = True
    final_offline_runner_safety_human_approval_boundary_verified: bool = True
    final_offline_runner_safety_stop_conditions_boundary_verified: bool = True
    final_offline_runner_safety_success_failure_boundary_verified: bool = True
    final_offline_runner_safety_audit_boundary_verified: bool = True
    final_offline_runner_safety_go_no_go_boundary_verified: bool = True
    final_offline_runner_safety_abort_boundary_verified: bool = True

    offline_mode_enforced: bool = True
    sandbox_mode_enforced: bool = True
    safety_gate_only: bool = True
    no_runner_created: bool = True
    no_runner_execution: bool = True
    no_dry_run_execution: bool = True
    no_broker_connection: bool = True
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
    no_real_order: bool = True
    no_position_mutation: bool = True
    no_real_account_access: bool = True
    human_approval_required: bool = True
    approval_before_preparation: bool = True
    failure_on_boundary_violation: bool = True
    next_phase_requires_clean_gate: bool = True

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
    paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_plan_requested: bool = False

    final_offline_runner_plan_score: int | None = None
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
    success_failure_score: int | None = None
    audit_score: int | None = None
    go_no_go_score: int | None = None
    abort_score: int | None = None


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateResult:
    state: PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateState
    decision: PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateDecision
    score: PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateScore
    risks: tuple[Risk, ...] = ()
    recommendations: tuple[PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateRecommendation, ...] = ()
    summary: str = ""
    markdown_report: str = ""
    offline_only: bool = True
    sandbox_only: bool = True
    safety_gate_only: bool = True
    runner_created: bool = False
    runner_executed: bool = False
    dry_run_executed: bool = False
    next_phase: str = "PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN"
    scope_boundary: FinalOfflineRunnerSafetyScopeBoundary | None = None
    execution_mode_boundary: FinalOfflineRunnerSafetyExecutionModeBoundary | None = None
    input_contract_boundary: FinalOfflineRunnerSafetyInputContractBoundary | None = None
    synthetic_market_context_boundary: FinalOfflineRunnerSafetySyntheticMarketContextBoundary | None = None
    read_only_broker_simulation_boundary: FinalOfflineRunnerSafetyReadOnlyBrokerSimulationBoundary | None = None
    no_real_broker_boundary: FinalOfflineRunnerSafetyNoRealBrokerBoundary | None = None
    no_secret_read_boundary: FinalOfflineRunnerSafetyNoSecretReadBoundary | None = None
    network_block_boundary: FinalOfflineRunnerSafetyNetworkBlockBoundary | None = None
    http_websocket_socket_block_boundary: FinalOfflineRunnerSafetyNetworkBlockBoundary | None = None
    account_snapshot_boundary: FinalOfflineRunnerSafetyAccountSnapshotBoundary | None = None
    market_data_snapshot_boundary: FinalOfflineRunnerSafetyMarketDataSnapshotBoundary | None = None
    order_blocking_boundary: FinalOfflineRunnerSafetyOrderBlockingBoundary | None = None
    position_mutation_blocking_boundary: FinalOfflineRunnerSafetyPositionMutationBlockingBoundary | None = None
    strategy_signal_observation_boundary: FinalOfflineRunnerSafetyStrategySignalObservationBoundary | None = None
    risk_observation_boundary: FinalOfflineRunnerSafetyRiskObservationBoundary | None = None
    profitability_observation_boundary: FinalOfflineRunnerSafetyProfitabilityObservationBoundary | None = None
    consistency_observation_boundary: FinalOfflineRunnerSafetyConsistencyObservationBoundary | None = None
    journal_boundary: FinalOfflineRunnerSafetyJournalBoundary | None = None
    observability_boundary: FinalOfflineRunnerSafetyObservabilityBoundary | None = None
    human_approval_boundary: FinalOfflineRunnerSafetyHumanApprovalBoundary | None = None
    stop_conditions_boundary: FinalOfflineRunnerSafetyStopConditionBoundary | None = None
    success_failure_boundary: FinalOfflineRunnerSafetySuccessFailureBoundary | None = None
    audit_boundary: FinalOfflineRunnerSafetyAuditBoundary | None = None
    go_no_go_boundary: FinalOfflineRunnerSafetyGoNoGoBoundary | None = None
    abort_boundary: FinalOfflineRunnerSafetyAbortBoundary | None = None
    findings: tuple[_FinalOfflineRunnerSafetyBoundary, ...] = field(default_factory=tuple)
