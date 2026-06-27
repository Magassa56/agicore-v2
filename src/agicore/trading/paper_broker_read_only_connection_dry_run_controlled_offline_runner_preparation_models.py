"""Models for Paper Broker Read-Only Connection Dry Run Controlled Offline Runner Preparation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationState(StrEnum):
    NOT_READY = "NOT_READY"
    OFFLINE_RUNNER_PREPARATION_INPUT_INVALID = "OFFLINE_RUNNER_PREPARATION_INPUT_INVALID"
    OFFLINE_RUNNER_PREPARATION_BLOCKED = "OFFLINE_RUNNER_PREPARATION_BLOCKED"
    OFFLINE_RUNNER_PREPARATION_COMPLETED_WITH_WARNINGS = "OFFLINE_RUNNER_PREPARATION_COMPLETED_WITH_WARNINGS"
    OFFLINE_RUNNER_PREPARATION_COMPLETED = "OFFLINE_RUNNER_PREPARATION_COMPLETED"
    READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW = "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW"


class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationDecision(StrEnum):
    BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION = "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION"
    REQUIRE_OFFLINE_RUNNER_SAFETY_GATE_FIXES = "REQUIRE_OFFLINE_RUNNER_SAFETY_GATE_FIXES"
    REQUIRE_OFFLINE_RUNNER_SCOPE_PREPARATION_FIXES = "REQUIRE_OFFLINE_RUNNER_SCOPE_PREPARATION_FIXES"
    REQUIRE_OFFLINE_RUNNER_EXECUTION_MODE_PREPARATION_FIXES = "REQUIRE_OFFLINE_RUNNER_EXECUTION_MODE_PREPARATION_FIXES"
    REQUIRE_OFFLINE_RUNNER_INPUT_CONTRACT_PREPARATION_FIXES = "REQUIRE_OFFLINE_RUNNER_INPUT_CONTRACT_PREPARATION_FIXES"
    REQUIRE_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_PREPARATION_FIXES = "REQUIRE_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_PREPARATION_FIXES"
    REQUIRE_OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_PREPARATION_FIXES = "REQUIRE_OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_PREPARATION_FIXES"
    REQUIRE_OFFLINE_RUNNER_NO_REAL_BROKER_GUARD_FIXES = "REQUIRE_OFFLINE_RUNNER_NO_REAL_BROKER_GUARD_FIXES"
    REQUIRE_OFFLINE_RUNNER_NO_SECRET_READ_GUARD_FIXES = "REQUIRE_OFFLINE_RUNNER_NO_SECRET_READ_GUARD_FIXES"
    REQUIRE_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_FIXES = "REQUIRE_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_FIXES"
    REQUIRE_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_PREPARATION_FIXES = "REQUIRE_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_PREPARATION_FIXES"
    REQUIRE_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_PREPARATION_FIXES = "REQUIRE_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_PREPARATION_FIXES"
    REQUIRE_OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_FIXES = "REQUIRE_OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_FIXES"
    REQUIRE_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_FIXES = "REQUIRE_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_FIXES"
    REQUIRE_OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_PREPARATION_FIXES = "REQUIRE_OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_PREPARATION_FIXES"
    REQUIRE_OFFLINE_RUNNER_RISK_OBSERVATION_PREPARATION_FIXES = "REQUIRE_OFFLINE_RUNNER_RISK_OBSERVATION_PREPARATION_FIXES"
    REQUIRE_OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_PREPARATION_FIXES = "REQUIRE_OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_PREPARATION_FIXES"
    REQUIRE_OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_PREPARATION_FIXES = "REQUIRE_OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_PREPARATION_FIXES"
    REQUIRE_OFFLINE_RUNNER_JOURNAL_PREPARATION_FIXES = "REQUIRE_OFFLINE_RUNNER_JOURNAL_PREPARATION_FIXES"
    REQUIRE_OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_FIXES = "REQUIRE_OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_FIXES"
    REQUIRE_OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION_FIXES = "REQUIRE_OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION_FIXES"
    REQUIRE_OFFLINE_RUNNER_STOP_CONDITION_PREPARATION_FIXES = "REQUIRE_OFFLINE_RUNNER_STOP_CONDITION_PREPARATION_FIXES"
    REQUIRE_OFFLINE_RUNNER_SUCCESS_FAILURE_PREPARATION_FIXES = "REQUIRE_OFFLINE_RUNNER_SUCCESS_FAILURE_PREPARATION_FIXES"
    REQUIRE_OFFLINE_RUNNER_AUDIT_PREPARATION_FIXES = "REQUIRE_OFFLINE_RUNNER_AUDIT_PREPARATION_FIXES"
    REQUIRE_OFFLINE_RUNNER_GO_NO_GO_PREPARATION_FIXES = "REQUIRE_OFFLINE_RUNNER_GO_NO_GO_PREPARATION_FIXES"
    REQUIRE_OFFLINE_RUNNER_ABORT_PREPARATION_FIXES = "REQUIRE_OFFLINE_RUNNER_ABORT_PREPARATION_FIXES"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION = "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION"


class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationRisk(StrEnum):
    OFFLINE_RUNNER_SAFETY_GATE_NOT_APPROVED = "OFFLINE_RUNNER_SAFETY_GATE_NOT_APPROVED"
    OFFLINE_RUNNER_SCOPE_PREPARATION_MISSING = "OFFLINE_RUNNER_SCOPE_PREPARATION_MISSING"
    OFFLINE_RUNNER_EXECUTION_MODE_PREPARATION_UNSAFE = "OFFLINE_RUNNER_EXECUTION_MODE_PREPARATION_UNSAFE"
    OFFLINE_RUNNER_INPUT_CONTRACT_PREPARATION_MISSING = "OFFLINE_RUNNER_INPUT_CONTRACT_PREPARATION_MISSING"
    OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_PREPARATION_MISSING = "OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_PREPARATION_MISSING"
    OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_PREPARATION_UNSAFE = "OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_PREPARATION_UNSAFE"
    OFFLINE_RUNNER_REAL_BROKER_GUARD_MISSING = "OFFLINE_RUNNER_REAL_BROKER_GUARD_MISSING"
    OFFLINE_RUNNER_SECRET_READ_GUARD_UNSAFE = "OFFLINE_RUNNER_SECRET_READ_GUARD_UNSAFE"
    OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_UNSAFE = "OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_UNSAFE"
    OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_UNSAFE = "OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_UNSAFE"
    OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_PREPARATION_UNSAFE = "OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_PREPARATION_UNSAFE"
    OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_PREPARATION_UNSAFE = "OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_PREPARATION_UNSAFE"
    OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_UNSAFE = "OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_UNSAFE"
    OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_UNSAFE = "OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_UNSAFE"
    OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_PREPARATION_MISSING = "OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_PREPARATION_MISSING"
    OFFLINE_RUNNER_RISK_OBSERVATION_PREPARATION_MISSING = "OFFLINE_RUNNER_RISK_OBSERVATION_PREPARATION_MISSING"
    OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_PREPARATION_MISSING = "OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_PREPARATION_MISSING"
    OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_PREPARATION_MISSING = "OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_PREPARATION_MISSING"
    OFFLINE_RUNNER_JOURNAL_PREPARATION_MISSING = "OFFLINE_RUNNER_JOURNAL_PREPARATION_MISSING"
    OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_MISSING = "OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_MISSING"
    OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION_MISSING = "OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION_MISSING"
    OFFLINE_RUNNER_STOP_CONDITIONS_PREPARATION_MISSING = "OFFLINE_RUNNER_STOP_CONDITIONS_PREPARATION_MISSING"
    OFFLINE_RUNNER_SUCCESS_CRITERIA_PREPARATION_MISSING = "OFFLINE_RUNNER_SUCCESS_CRITERIA_PREPARATION_MISSING"
    OFFLINE_RUNNER_FAILURE_CRITERIA_PREPARATION_MISSING = "OFFLINE_RUNNER_FAILURE_CRITERIA_PREPARATION_MISSING"
    OFFLINE_RUNNER_AUDIT_PREPARATION_MISSING = "OFFLINE_RUNNER_AUDIT_PREPARATION_MISSING"
    OFFLINE_RUNNER_GO_NO_GO_PREPARATION_MISSING = "OFFLINE_RUNNER_GO_NO_GO_PREPARATION_MISSING"
    OFFLINE_RUNNER_ABORT_PREPARATION_MISSING = "OFFLINE_RUNNER_ABORT_PREPARATION_MISSING"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW = "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW"


class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationRecommendation(StrEnum):
    HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW = "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW"
    APPROVE_OFFLINE_RUNNER_SAFETY_GATE_FIRST = "APPROVE_OFFLINE_RUNNER_SAFETY_GATE_FIRST"
    PREPARE_OFFLINE_RUNNER_SCOPE = "PREPARE_OFFLINE_RUNNER_SCOPE"
    PREPARE_OFFLINE_RUNNER_EXECUTION_MODE = "PREPARE_OFFLINE_RUNNER_EXECUTION_MODE"
    PREPARE_OFFLINE_RUNNER_INPUT_CONTRACT = "PREPARE_OFFLINE_RUNNER_INPUT_CONTRACT"
    PREPARE_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT = "PREPARE_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT"
    HARDEN_OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION = "HARDEN_OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION"
    PREPARE_OFFLINE_RUNNER_NO_REAL_BROKER_GUARD = "PREPARE_OFFLINE_RUNNER_NO_REAL_BROKER_GUARD"
    HARDEN_OFFLINE_RUNNER_NO_SECRET_READ_GUARD = "HARDEN_OFFLINE_RUNNER_NO_SECRET_READ_GUARD"
    HARDEN_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD = "HARDEN_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD"
    HARDEN_OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD = "HARDEN_OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD"
    HARDEN_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT = "HARDEN_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT"
    HARDEN_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT = "HARDEN_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT"
    HARDEN_OFFLINE_RUNNER_ORDER_BLOCKING_GUARD = "HARDEN_OFFLINE_RUNNER_ORDER_BLOCKING_GUARD"
    HARDEN_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD = "HARDEN_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD"
    PREPARE_OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION = "PREPARE_OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION"
    PREPARE_OFFLINE_RUNNER_RISK_OBSERVATION = "PREPARE_OFFLINE_RUNNER_RISK_OBSERVATION"
    PREPARE_OFFLINE_RUNNER_PROFITABILITY_OBSERVATION = "PREPARE_OFFLINE_RUNNER_PROFITABILITY_OBSERVATION"
    PREPARE_OFFLINE_RUNNER_CONSISTENCY_OBSERVATION = "PREPARE_OFFLINE_RUNNER_CONSISTENCY_OBSERVATION"
    COMPLETE_OFFLINE_RUNNER_JOURNAL_PREPARATION = "COMPLETE_OFFLINE_RUNNER_JOURNAL_PREPARATION"
    COMPLETE_OFFLINE_RUNNER_OBSERVABILITY_PREPARATION = "COMPLETE_OFFLINE_RUNNER_OBSERVABILITY_PREPARATION"
    REQUIRE_OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION = "REQUIRE_OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION"
    PREPARE_OFFLINE_RUNNER_STOP_CONDITIONS = "PREPARE_OFFLINE_RUNNER_STOP_CONDITIONS"
    PREPARE_OFFLINE_RUNNER_SUCCESS_FAILURE = "PREPARE_OFFLINE_RUNNER_SUCCESS_FAILURE"
    COMPLETE_OFFLINE_RUNNER_AUDIT_PREPARATION = "COMPLETE_OFFLINE_RUNNER_AUDIT_PREPARATION"
    PREPARE_OFFLINE_RUNNER_GO_NO_GO = "PREPARE_OFFLINE_RUNNER_GO_NO_GO"
    PREPARE_OFFLINE_RUNNER_ABORT = "PREPARE_OFFLINE_RUNNER_ABORT"
    RESTORE_OFFLINE_BOUNDARIES = "RESTORE_OFFLINE_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW = "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW"
    RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_SUITE = "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_SUITE"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW = "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW"


Risk = PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationRisk


@dataclass(frozen=True)
class _OfflineRunnerPreparationArtifact:
    name: str
    score: int = 0
    prepared: bool = False
    risks: tuple[Risk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class OfflineRunnerScopePreparationContract(_OfflineRunnerPreparationArtifact):
    offline_only: bool = False
    sandbox_only: bool = False
    preparation_only: bool = False
    no_runner_executable_created: bool = False


@dataclass(frozen=True)
class OfflineRunnerExecutionModePreparationContract(_OfflineRunnerPreparationArtifact):
    controlled_offline_mode: bool = False
    deterministic_mode: bool = False
    in_memory_only: bool = False
    no_dry_run_execution: bool = False


@dataclass(frozen=True)
class OfflineRunnerInputPreparationContract(_OfflineRunnerPreparationArtifact):
    schema_only_inputs: bool = False
    synthetic_inputs_only: bool = False
    no_real_credentials: bool = False


@dataclass(frozen=True)
class OfflineRunnerSyntheticMarketContextPreparationContract(_OfflineRunnerPreparationArtifact):
    synthetic_context_only: bool = False
    in_memory_context: bool = False
    no_data_access: bool = False


@dataclass(frozen=True)
class OfflineRunnerReadOnlyBrokerSimulationPreparationContract(_OfflineRunnerPreparationArtifact):
    simulated_broker_only: bool = False
    read_only_contract: bool = False
    no_real_broker: bool = False


@dataclass(frozen=True)
class OfflineRunnerNoRealBrokerGuard(_OfflineRunnerPreparationArtifact):
    real_broker_blocked: bool = False
    alpaca_blocked: bool = False
    broker_connection_disabled: bool = False


@dataclass(frozen=True)
class OfflineRunnerNoSecretReadGuard(_OfflineRunnerPreparationArtifact):
    no_api_key_read: bool = False
    no_env_var_read: bool = False
    no_hardcoded_secret: bool = False


@dataclass(frozen=True)
class OfflineRunnerNetworkBlockGuard(_OfflineRunnerPreparationArtifact):
    network_blocked: bool = False
    http_blocked: bool = False
    websocket_blocked: bool = False
    socket_blocked: bool = False
    external_api_blocked: bool = False


@dataclass(frozen=True)
class OfflineRunnerAccountSnapshotPreparationContract(_OfflineRunnerPreparationArtifact):
    simulated_snapshot_only: bool = False
    read_only_snapshot: bool = False
    active_account_access_blocked: bool = False


@dataclass(frozen=True)
class OfflineRunnerMarketDataSnapshotPreparationContract(_OfflineRunnerPreparationArtifact):
    synthetic_snapshot_only: bool = False
    read_only_snapshot: bool = False
    live_subscription_blocked: bool = False


@dataclass(frozen=True)
class OfflineRunnerOrderBlockingGuard(_OfflineRunnerPreparationArtifact):
    order_execution_blocked: bool = False
    real_order_blocked: bool = False
    cancel_replace_blocked: bool = False


@dataclass(frozen=True)
class OfflineRunnerPositionMutationBlockingGuard(_OfflineRunnerPreparationArtifact):
    position_mutation_blocked: bool = False
    close_modify_blocked: bool = False
    simulated_position_read_only: bool = False


@dataclass(frozen=True)
class OfflineRunnerStrategySignalObservationPreparationContract(_OfflineRunnerPreparationArtifact):
    observation_only: bool = False
    no_signal_execution: bool = False
    signal_trace_required: bool = False


@dataclass(frozen=True)
class OfflineRunnerRiskObservationPreparationContract(_OfflineRunnerPreparationArtifact):
    observation_only: bool = False
    no_risk_action_execution: bool = False
    risk_trace_required: bool = False


@dataclass(frozen=True)
class OfflineRunnerProfitabilityObservationPreparationContract(_OfflineRunnerPreparationArtifact):
    observation_only: bool = False
    no_profit_promise: bool = False
    profitability_trace_required: bool = False


@dataclass(frozen=True)
class OfflineRunnerConsistencyObservationPreparationContract(_OfflineRunnerPreparationArtifact):
    observation_only: bool = False
    deterministic_consistency_checks: bool = False
    consistency_trace_required: bool = False

@dataclass(frozen=True)
class OfflineRunnerJournalPreparationContract(_OfflineRunnerPreparationArtifact):
    offline_journal_required: bool = False
    no_secret_material_logged: bool = False
    plan_events_recorded: bool = False


@dataclass(frozen=True)
class OfflineRunnerObservabilityPreparationContract(_OfflineRunnerPreparationArtifact):
    offline_events_defined: bool = False
    no_connection_attempt_metrics: bool = False
    sensitive_values_redacted: bool = False


@dataclass(frozen=True)
class OfflineRunnerHumanApprovalPreparationContract(_OfflineRunnerPreparationArtifact):
    human_approval_required: bool = False
    approval_before_review: bool = False
    evidence_required: bool = False


@dataclass(frozen=True)
class OfflineRunnerStopConditionPreparationContract(_OfflineRunnerPreparationArtifact):
    stop_on_secret_read: bool = False
    stop_on_network_request: bool = False
    stop_on_order_or_position_request: bool = False
    stop_on_account_access_request: bool = False


@dataclass(frozen=True)
class OfflineRunnerSuccessCriteriaPreparationContract(_OfflineRunnerPreparationArtifact):
    no_boundary_violation_required: bool = False
    all_contracts_prepared: bool = False
    no_runner_execution_required: bool = False


@dataclass(frozen=True)
class OfflineRunnerFailureCriteriaPreparationContract(_OfflineRunnerPreparationArtifact):
    fail_on_boundary_violation: bool = False
    fail_on_missing_contract: bool = False
    fail_on_execution_request: bool = False


@dataclass(frozen=True)
class OfflineRunnerAuditPreparationContract(_OfflineRunnerPreparationArtifact):
    audit_events_defined: bool = False
    boundary_evidence_required: bool = False
    immutable_preparation_record_required: bool = False


@dataclass(frozen=True)
class OfflineRunnerGoNoGoPreparationContract(_OfflineRunnerPreparationArtifact):
    go_no_go_required: bool = False
    no_go_on_risk: bool = False
    next_phase_requires_clean_preparation: bool = False


@dataclass(frozen=True)
class OfflineRunnerAbortPreparationContract(_OfflineRunnerPreparationArtifact):
    abort_on_secret_read: bool = False
    abort_on_network_or_broker_request: bool = False
    abort_on_order_or_position_request: bool = False


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationScore:
    overall_score: int = 0
    offline_runner_safety_gate_score: int = 0
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
class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationInput:
    paper_broker_read_only_connection_dry_run_controlled_offline_runner_safety_gate: Any | None = None
    offline_runner_safety_gate_approved: bool | None = None
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

    offline_runner_scope_contract_prepared: bool = True
    offline_runner_execution_mode_contract_prepared: bool = True
    offline_runner_input_contract_prepared: bool = True
    offline_runner_synthetic_market_context_contract_prepared: bool = True
    offline_runner_read_only_broker_simulation_contract_prepared: bool = True
    offline_runner_no_real_broker_guard_prepared: bool = True
    offline_runner_no_secret_read_guard_prepared: bool = True
    offline_runner_network_block_guard_prepared: bool = True
    offline_runner_http_websocket_socket_block_guard_prepared: bool = True
    offline_runner_account_snapshot_contract_prepared: bool = True
    offline_runner_market_data_snapshot_contract_prepared: bool = True
    offline_runner_order_blocking_guard_prepared: bool = True
    offline_runner_position_mutation_blocking_guard_prepared: bool = True
    offline_runner_strategy_signal_observation_contract_prepared: bool = True
    offline_runner_risk_observation_contract_prepared: bool = True
    offline_runner_profitability_observation_contract_prepared: bool = True
    offline_runner_consistency_observation_contract_prepared: bool = True
    offline_runner_journal_contract_prepared: bool = True
    offline_runner_observability_contract_prepared: bool = True
    offline_runner_human_approval_contract_prepared: bool = True
    offline_runner_stop_conditions_contract_prepared: bool = True
    offline_runner_success_criteria_contract_prepared: bool = True
    offline_runner_failure_criteria_contract_prepared: bool = True
    offline_runner_audit_contract_prepared: bool = True
    offline_runner_go_no_go_contract_prepared: bool = True
    offline_runner_abort_contract_prepared: bool = True

    offline_mode_enforced: bool = True
    sandbox_mode_enforced: bool = True
    preparation_only: bool = True
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
    approval_before_review: bool = True
    stop_on_secret_read: bool = True
    stop_on_network_request: bool = True
    stop_on_order_or_position_request: bool = True
    stop_on_account_access_request: bool = True
    success_no_boundary_violation_required: bool = True
    failure_on_boundary_violation: bool = True
    audit_contract_required: bool = True
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
    paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review_requested: bool = False

    offline_runner_safety_gate_score: int | None = None
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
class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationResult:
    state: PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationState
    decision: PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationDecision
    score: PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationScore
    risks: tuple[Risk, ...] = ()
    recommendations: tuple[PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationRecommendation, ...] = ()
    summary: str = ""
    markdown_report: str = ""
    offline_only: bool = True
    sandbox_only: bool = True
    preparation_only: bool = True
    runner_created: bool = False
    runner_executed: bool = False
    dry_run_executed: bool = False
    next_phase: str = "PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW"
    scope_contract: OfflineRunnerScopePreparationContract | None = None
    execution_mode_contract: OfflineRunnerExecutionModePreparationContract | None = None
    input_contract: OfflineRunnerInputPreparationContract | None = None
    synthetic_market_context_contract: OfflineRunnerSyntheticMarketContextPreparationContract | None = None
    read_only_broker_simulation_contract: OfflineRunnerReadOnlyBrokerSimulationPreparationContract | None = None
    no_real_broker_guard: OfflineRunnerNoRealBrokerGuard | None = None
    no_secret_read_guard: OfflineRunnerNoSecretReadGuard | None = None
    network_block_guard: OfflineRunnerNetworkBlockGuard | None = None
    http_websocket_socket_block_guard: OfflineRunnerNetworkBlockGuard | None = None
    account_snapshot_contract: OfflineRunnerAccountSnapshotPreparationContract | None = None
    market_data_snapshot_contract: OfflineRunnerMarketDataSnapshotPreparationContract | None = None
    order_blocking_guard: OfflineRunnerOrderBlockingGuard | None = None
    position_mutation_blocking_guard: OfflineRunnerPositionMutationBlockingGuard | None = None
    strategy_signal_observation_contract: OfflineRunnerStrategySignalObservationPreparationContract | None = None
    risk_observation_contract: OfflineRunnerRiskObservationPreparationContract | None = None
    profitability_observation_contract: OfflineRunnerProfitabilityObservationPreparationContract | None = None
    consistency_observation_contract: OfflineRunnerConsistencyObservationPreparationContract | None = None
    journal_contract: OfflineRunnerJournalPreparationContract | None = None
    observability_contract: OfflineRunnerObservabilityPreparationContract | None = None
    human_approval_contract: OfflineRunnerHumanApprovalPreparationContract | None = None
    stop_conditions_contract: OfflineRunnerStopConditionPreparationContract | None = None
    success_criteria_contract: OfflineRunnerSuccessCriteriaPreparationContract | None = None
    failure_criteria_contract: OfflineRunnerFailureCriteriaPreparationContract | None = None
    audit_contract: OfflineRunnerAuditPreparationContract | None = None
    go_no_go_contract: OfflineRunnerGoNoGoPreparationContract | None = None
    abort_contract: OfflineRunnerAbortPreparationContract | None = None
    artifacts: tuple[_OfflineRunnerPreparationArtifact, ...] = field(default_factory=tuple)