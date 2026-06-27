"""Models for the controlled offline runner implementation safety gate."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateState = StrEnum(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateState",
    {
        "NOT_READY": "NOT_READY",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE_INPUT_INVALID": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE_INPUT_INVALID",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE_BLOCKED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE_BLOCKED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE_COMPLETED_WITH_WARNINGS": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE_COMPLETED_WITH_WARNINGS",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE_COMPLETED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE_COMPLETED",
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION": "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION",
    },
)

PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateDecision = StrEnum(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateDecision",
    {
        "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE": "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_PLAN_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_PLAN_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SCOPE_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SCOPE_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ARCHITECTURE_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ARCHITECTURE_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SEQUENCE_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SEQUENCE_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_RUNTIME_CONTRACT_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_RUNTIME_CONTRACT_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_INPUT_ADAPTER_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_INPUT_ADAPTER_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SYNTHETIC_MARKET_CONTEXT_ADAPTER_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SYNTHETIC_MARKET_CONTEXT_ADAPTER_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SIMULATED_BROKER_ADAPTER_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SIMULATED_BROKER_ADAPTER_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ACCOUNT_SNAPSHOT_ADAPTER_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ACCOUNT_SNAPSHOT_ADAPTER_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_MARKET_DATA_SNAPSHOT_ADAPTER_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_MARKET_DATA_SNAPSHOT_ADAPTER_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_STRATEGY_SIGNAL_PROBE_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_STRATEGY_SIGNAL_PROBE_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_RISK_OBSERVER_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_RISK_OBSERVER_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_PROFITABILITY_OBSERVER_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_PROFITABILITY_OBSERVER_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_CONSISTENCY_OBSERVER_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_CONSISTENCY_OBSERVER_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_JOURNAL_WRITER_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_JOURNAL_WRITER_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_OBSERVABILITY_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_OBSERVABILITY_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_HUMAN_APPROVAL_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_HUMAN_APPROVAL_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_STOP_CONDITION_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_STOP_CONDITION_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SUCCESS_FAILURE_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SUCCESS_FAILURE_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_AUDIT_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_AUDIT_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GO_NO_GO_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GO_NO_GO_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ABORT_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ABORT_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_NO_REAL_BROKER_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_NO_REAL_BROKER_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_NO_SECRET_READ_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_NO_SECRET_READ_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_NETWORK_BLOCK_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_NETWORK_BLOCK_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ORDER_BLOCKING_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ORDER_BLOCKING_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_POSITION_MUTATION_BLOCKING_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_POSITION_MUTATION_BLOCKING_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_DATA_ACCESS_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_DATA_ACCESS_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_TEST_STRATEGY_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_TEST_STRATEGY_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ROLLBACK_STRATEGY_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ROLLBACK_STRATEGY_FIXES",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE": "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE",
    },
)

PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateRisk = StrEnum(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateRisk",
    {
        "OFFLINE_RUNNER_IMPLEMENTATION_PLAN_NOT_APPROVED": "OFFLINE_RUNNER_IMPLEMENTATION_PLAN_NOT_APPROVED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SCOPE_BOUNDARY_FAILED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SCOPE_BOUNDARY_FAILED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ARCHITECTURE_BOUNDARY_FAILED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ARCHITECTURE_BOUNDARY_FAILED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SEQUENCE_BOUNDARY_FAILED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SEQUENCE_BOUNDARY_FAILED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_RUNTIME_CONTRACT_BOUNDARY_FAILED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_RUNTIME_CONTRACT_BOUNDARY_FAILED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_INPUT_ADAPTER_BOUNDARY_FAILED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_INPUT_ADAPTER_BOUNDARY_FAILED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SYNTHETIC_MARKET_CONTEXT_ADAPTER_BOUNDARY_FAILED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SYNTHETIC_MARKET_CONTEXT_ADAPTER_BOUNDARY_FAILED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SIMULATED_BROKER_ADAPTER_BOUNDARY_FAILED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SIMULATED_BROKER_ADAPTER_BOUNDARY_FAILED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ACCOUNT_SNAPSHOT_ADAPTER_BOUNDARY_FAILED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ACCOUNT_SNAPSHOT_ADAPTER_BOUNDARY_FAILED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_MARKET_DATA_SNAPSHOT_ADAPTER_BOUNDARY_FAILED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_MARKET_DATA_SNAPSHOT_ADAPTER_BOUNDARY_FAILED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_STRATEGY_SIGNAL_PROBE_BOUNDARY_FAILED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_STRATEGY_SIGNAL_PROBE_BOUNDARY_FAILED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_RISK_OBSERVER_BOUNDARY_FAILED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_RISK_OBSERVER_BOUNDARY_FAILED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_PROFITABILITY_OBSERVER_BOUNDARY_FAILED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_PROFITABILITY_OBSERVER_BOUNDARY_FAILED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_CONSISTENCY_OBSERVER_BOUNDARY_FAILED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_CONSISTENCY_OBSERVER_BOUNDARY_FAILED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_JOURNAL_WRITER_BOUNDARY_FAILED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_JOURNAL_WRITER_BOUNDARY_FAILED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_OBSERVABILITY_BOUNDARY_FAILED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_OBSERVABILITY_BOUNDARY_FAILED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_HUMAN_APPROVAL_BOUNDARY_FAILED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_HUMAN_APPROVAL_BOUNDARY_FAILED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_STOP_CONDITION_BOUNDARY_FAILED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_STOP_CONDITION_BOUNDARY_FAILED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SUCCESS_FAILURE_BOUNDARY_FAILED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SUCCESS_FAILURE_BOUNDARY_FAILED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_AUDIT_BOUNDARY_FAILED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_AUDIT_BOUNDARY_FAILED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GO_NO_GO_BOUNDARY_FAILED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GO_NO_GO_BOUNDARY_FAILED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ABORT_BOUNDARY_FAILED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ABORT_BOUNDARY_FAILED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_REAL_BROKER_BOUNDARY_FAILED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_REAL_BROKER_BOUNDARY_FAILED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SECRET_READ_BOUNDARY_FAILED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SECRET_READ_BOUNDARY_FAILED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_NETWORK_BLOCK_BOUNDARY_FAILED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_NETWORK_BLOCK_BOUNDARY_FAILED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_HTTP_WEBSOCKET_SOCKET_BLOCK_BOUNDARY_FAILED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_HTTP_WEBSOCKET_SOCKET_BLOCK_BOUNDARY_FAILED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ORDER_BLOCKING_BOUNDARY_FAILED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ORDER_BLOCKING_BOUNDARY_FAILED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_POSITION_MUTATION_BLOCKING_BOUNDARY_FAILED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_POSITION_MUTATION_BLOCKING_BOUNDARY_FAILED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_DATA_ACCESS_BOUNDARY_FAILED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_DATA_ACCESS_BOUNDARY_FAILED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_TEST_STRATEGY_BOUNDARY_FAILED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_TEST_STRATEGY_BOUNDARY_FAILED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ROLLBACK_STRATEGY_BOUNDARY_FAILED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ROLLBACK_STRATEGY_BOUNDARY_FAILED",
        "REAL_EXECUTION_BOUNDARY_VIOLATION": "REAL_EXECUTION_BOUNDARY_VIOLATION",
        "DATA_ACCESS_VIOLATION": "DATA_ACCESS_VIOLATION",
        "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION": "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION",
    },
)

PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateRecommendation = StrEnum(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateRecommendation",
    {
        "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION": "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION",
        "APPROVE_OFFLINE_RUNNER_IMPLEMENTATION_PLAN_FIRST": "APPROVE_OFFLINE_RUNNER_IMPLEMENTATION_PLAN_FIRST",
        "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SCOPE": "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SCOPE",
        "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ARCHITECTURE": "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ARCHITECTURE",
        "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SEQUENCE": "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SEQUENCE",
        "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_RUNTIME_CONTRACT": "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_RUNTIME_CONTRACT",
        "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_INPUT_ADAPTER": "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_INPUT_ADAPTER",
        "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SYNTHETIC_MARKET_CONTEXT_ADAPTER": "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SYNTHETIC_MARKET_CONTEXT_ADAPTER",
        "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SIMULATED_BROKER_ADAPTER": "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SIMULATED_BROKER_ADAPTER",
        "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ACCOUNT_SNAPSHOT_ADAPTER": "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ACCOUNT_SNAPSHOT_ADAPTER",
        "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_MARKET_DATA_SNAPSHOT_ADAPTER": "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_MARKET_DATA_SNAPSHOT_ADAPTER",
        "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_STRATEGY_SIGNAL_PROBE": "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_STRATEGY_SIGNAL_PROBE",
        "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_RISK_OBSERVER": "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_RISK_OBSERVER",
        "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_PROFITABILITY_OBSERVER": "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_PROFITABILITY_OBSERVER",
        "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_CONSISTENCY_OBSERVER": "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_CONSISTENCY_OBSERVER",
        "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_JOURNAL_WRITER": "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_JOURNAL_WRITER",
        "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_OBSERVABILITY": "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_OBSERVABILITY",
        "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_HUMAN_APPROVAL": "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_HUMAN_APPROVAL",
        "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_STOP_CONDITIONS": "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_STOP_CONDITIONS",
        "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SUCCESS_FAILURE": "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SUCCESS_FAILURE",
        "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_AUDIT": "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_AUDIT",
        "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GO_NO_GO": "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GO_NO_GO",
        "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ABORT": "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ABORT",
        "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_NO_REAL_BROKER": "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_NO_REAL_BROKER",
        "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_NO_SECRET_READ": "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_NO_SECRET_READ",
        "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_NETWORK_BLOCK": "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_NETWORK_BLOCK",
        "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_HTTP_WEBSOCKET_SOCKET_BLOCK": "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_HTTP_WEBSOCKET_SOCKET_BLOCK",
        "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ORDER_BLOCKING": "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ORDER_BLOCKING",
        "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_POSITION_MUTATION_BLOCKING": "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_POSITION_MUTATION_BLOCKING",
        "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_DATA_ACCESS": "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_DATA_ACCESS",
        "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_TEST_STRATEGY": "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_TEST_STRATEGY",
        "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ROLLBACK_STRATEGY": "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ROLLBACK_STRATEGY",
        "RESTORE_OFFLINE_BOUNDARIES": "RESTORE_OFFLINE_BOUNDARIES",
        "REMOVE_DATA_ACCESS": "REMOVE_DATA_ACCESS",
        "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION": "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION",
        "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE_SUITE": "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE_SUITE",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION": "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION",
    },
)

Risk = PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateRisk


@dataclass(frozen=True)
class _OfflineRunnerImplementationSafetyBoundary:
    name: str
    score: int = 0
    passed: bool = False
    risks: tuple[Risk, ...] = ()
    details: tuple[str, ...] = ()
    offline_only: bool = False
    sandbox_only: bool = False
    implementation_safety_gate_only: bool = False
    no_runner_created: bool = False
    no_runner_execution: bool = False
    no_dry_run_execution: bool = False
    no_real_broker: bool = False
    no_secret_read: bool = False
    network_blocked: bool = False
    http_blocked: bool = False
    websocket_blocked: bool = False
    socket_blocked: bool = False
    order_blocked: bool = False
    position_mutation_blocked: bool = False
    data_access_blocked: bool = False
    read_only: bool = False
    simulated_only: bool = False
    observation_only: bool = False
    human_approval_required: bool = False
    stop_conditions_validated: bool = False
    audit_validated: bool = False
    test_strategy_validated: bool = False
    rollback_strategy_validated: bool = False


_BOUNDARY_CLASSES = {
    "OfflineRunnerImplementationSafetyScopeBoundary",
    "OfflineRunnerImplementationSafetyArchitectureBoundary",
    "OfflineRunnerImplementationSafetySequenceBoundary",
    "OfflineRunnerImplementationSafetyRuntimeContractBoundary",
    "OfflineRunnerImplementationSafetyInputAdapterBoundary",
    "OfflineRunnerImplementationSafetySyntheticMarketContextAdapterBoundary",
    "OfflineRunnerImplementationSafetySimulatedBrokerAdapterBoundary",
    "OfflineRunnerImplementationSafetyAccountSnapshotAdapterBoundary",
    "OfflineRunnerImplementationSafetyMarketDataSnapshotAdapterBoundary",
    "OfflineRunnerImplementationSafetyStrategySignalProbeBoundary",
    "OfflineRunnerImplementationSafetyRiskObserverBoundary",
    "OfflineRunnerImplementationSafetyProfitabilityObserverBoundary",
    "OfflineRunnerImplementationSafetyConsistencyObserverBoundary",
    "OfflineRunnerImplementationSafetyJournalWriterBoundary",
    "OfflineRunnerImplementationSafetyObservabilityBoundary",
    "OfflineRunnerImplementationSafetyHumanApprovalBoundary",
    "OfflineRunnerImplementationSafetyStopConditionBoundary",
    "OfflineRunnerImplementationSafetySuccessFailureBoundary",
    "OfflineRunnerImplementationSafetyAuditBoundary",
    "OfflineRunnerImplementationSafetyGoNoGoBoundary",
    "OfflineRunnerImplementationSafetyAbortBoundary",
    "OfflineRunnerImplementationSafetyNoRealBrokerBoundary",
    "OfflineRunnerImplementationSafetyNoSecretReadBoundary",
    "OfflineRunnerImplementationSafetyNetworkBlockBoundary",
    "OfflineRunnerImplementationSafetyOrderBlockingBoundary",
    "OfflineRunnerImplementationSafetyPositionMutationBlockingBoundary",
    "OfflineRunnerImplementationSafetyDataAccessBoundary",
    "OfflineRunnerImplementationSafetyTestStrategyBoundary",
    "OfflineRunnerImplementationSafetyRollbackStrategyBoundary",
}

for _name in _BOUNDARY_CLASSES:
    globals()[_name] = dataclass(frozen=True)(type(_name, (_OfflineRunnerImplementationSafetyBoundary,), {}))


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateScore:
    overall_score: int = 0
    implementation_plan_score: int = 0
    scope_boundary_score: int = 0
    architecture_boundary_score: int = 0
    sequence_boundary_score: int = 0
    runtime_contract_boundary_score: int = 0
    input_adapter_boundary_score: int = 0
    synthetic_market_context_adapter_boundary_score: int = 0
    simulated_broker_adapter_boundary_score: int = 0
    account_snapshot_adapter_boundary_score: int = 0
    market_data_snapshot_adapter_boundary_score: int = 0
    strategy_signal_probe_boundary_score: int = 0
    risk_observer_boundary_score: int = 0
    profitability_observer_boundary_score: int = 0
    consistency_observer_boundary_score: int = 0
    journal_writer_boundary_score: int = 0
    observability_boundary_score: int = 0
    human_approval_boundary_score: int = 0
    stop_condition_boundary_score: int = 0
    success_failure_boundary_score: int = 0
    audit_boundary_score: int = 0
    go_no_go_boundary_score: int = 0
    abort_boundary_score: int = 0
    no_real_broker_boundary_score: int = 0
    no_secret_read_boundary_score: int = 0
    network_block_boundary_score: int = 0
    http_websocket_socket_block_boundary_score: int = 0
    order_blocking_boundary_score: int = 0
    position_mutation_blocking_boundary_score: int = 0
    data_access_boundary_score: int = 0
    test_strategy_boundary_score: int = 0
    rollback_strategy_boundary_score: int = 0


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateInput:
    paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_plan: Any | None = None
    paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_safety_gate: Any | None = None
    paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_plan: Any | None = None
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
    offline_runner_implementation_plan_approved: bool | None = None
    offline_mode_enforced: bool = True
    sandbox_mode_enforced: bool = True
    implementation_safety_gate_only: bool = True
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
    test_strategy_required: bool = True
    rollback_strategy_required: bool = True
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
    paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_requested: bool = False
    implementation_plan_score: int | None = None
    scope_boundary_score: int | None = None
    architecture_boundary_score: int | None = None
    sequence_boundary_score: int | None = None
    runtime_contract_boundary_score: int | None = None
    input_adapter_boundary_score: int | None = None
    synthetic_market_context_adapter_boundary_score: int | None = None
    simulated_broker_adapter_boundary_score: int | None = None
    account_snapshot_adapter_boundary_score: int | None = None
    market_data_snapshot_adapter_boundary_score: int | None = None
    strategy_signal_probe_boundary_score: int | None = None
    risk_observer_boundary_score: int | None = None
    profitability_observer_boundary_score: int | None = None
    consistency_observer_boundary_score: int | None = None
    journal_writer_boundary_score: int | None = None
    observability_boundary_score: int | None = None
    human_approval_boundary_score: int | None = None
    stop_condition_boundary_score: int | None = None
    success_failure_boundary_score: int | None = None
    audit_boundary_score: int | None = None
    go_no_go_boundary_score: int | None = None
    abort_boundary_score: int | None = None
    no_real_broker_boundary_score: int | None = None
    no_secret_read_boundary_score: int | None = None
    network_block_boundary_score: int | None = None
    http_websocket_socket_block_boundary_score: int | None = None
    order_blocking_boundary_score: int | None = None
    position_mutation_blocking_boundary_score: int | None = None
    data_access_boundary_score: int | None = None
    test_strategy_boundary_score: int | None = None
    rollback_strategy_boundary_score: int | None = None
    offline_runner_implementation_safety_scope_boundary_valid: bool = True
    offline_runner_implementation_safety_architecture_boundary_valid: bool = True
    offline_runner_implementation_safety_sequence_boundary_valid: bool = True
    offline_runner_implementation_safety_runtime_contract_boundary_valid: bool = True
    offline_runner_implementation_safety_input_adapter_boundary_valid: bool = True
    offline_runner_implementation_safety_synthetic_market_context_adapter_boundary_valid: bool = True
    offline_runner_implementation_safety_simulated_broker_adapter_boundary_valid: bool = True
    offline_runner_implementation_safety_account_snapshot_adapter_boundary_valid: bool = True
    offline_runner_implementation_safety_market_data_snapshot_adapter_boundary_valid: bool = True
    offline_runner_implementation_safety_strategy_signal_probe_boundary_valid: bool = True
    offline_runner_implementation_safety_risk_observer_boundary_valid: bool = True
    offline_runner_implementation_safety_profitability_observer_boundary_valid: bool = True
    offline_runner_implementation_safety_consistency_observer_boundary_valid: bool = True
    offline_runner_implementation_safety_journal_writer_boundary_valid: bool = True
    offline_runner_implementation_safety_observability_boundary_valid: bool = True
    offline_runner_implementation_safety_human_approval_boundary_valid: bool = True
    offline_runner_implementation_safety_stop_condition_boundary_valid: bool = True
    offline_runner_implementation_safety_success_failure_boundary_valid: bool = True
    offline_runner_implementation_safety_audit_boundary_valid: bool = True
    offline_runner_implementation_safety_go_no_go_boundary_valid: bool = True
    offline_runner_implementation_safety_abort_boundary_valid: bool = True
    offline_runner_implementation_safety_no_real_broker_boundary_valid: bool = True
    offline_runner_implementation_safety_no_secret_read_boundary_valid: bool = True
    offline_runner_implementation_safety_network_block_boundary_valid: bool = True
    offline_runner_implementation_safety_http_websocket_socket_block_boundary_valid: bool = True
    offline_runner_implementation_safety_order_blocking_boundary_valid: bool = True
    offline_runner_implementation_safety_position_mutation_blocking_boundary_valid: bool = True
    offline_runner_implementation_safety_data_access_boundary_valid: bool = True
    offline_runner_implementation_safety_test_strategy_boundary_valid: bool = True
    offline_runner_implementation_safety_rollback_strategy_boundary_valid: bool = True


@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateResult:
    state: PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateState
    decision: PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateDecision
    score: PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateScore
    risks: tuple[Risk, ...] = ()
    recommendations: tuple[PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateRecommendation, ...] = ()
    summary: str = ""
    markdown_report: str = ""
    offline_only: bool = True
    sandbox_only: bool = True
    implementation_safety_gate_only: bool = True
    runner_created: bool = False
    runner_executed: bool = False
    dry_run_executed: bool = False
    next_phase: str = "PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION"
    scope_boundary: OfflineRunnerImplementationSafetyScopeBoundary | None = None
    architecture_boundary: OfflineRunnerImplementationSafetyArchitectureBoundary | None = None
    sequence_boundary: OfflineRunnerImplementationSafetySequenceBoundary | None = None
    runtime_contract_boundary: OfflineRunnerImplementationSafetyRuntimeContractBoundary | None = None
    input_adapter_boundary: OfflineRunnerImplementationSafetyInputAdapterBoundary | None = None
    synthetic_market_context_adapter_boundary: OfflineRunnerImplementationSafetySyntheticMarketContextAdapterBoundary | None = None
    simulated_broker_adapter_boundary: OfflineRunnerImplementationSafetySimulatedBrokerAdapterBoundary | None = None
    account_snapshot_adapter_boundary: OfflineRunnerImplementationSafetyAccountSnapshotAdapterBoundary | None = None
    market_data_snapshot_adapter_boundary: OfflineRunnerImplementationSafetyMarketDataSnapshotAdapterBoundary | None = None
    strategy_signal_probe_boundary: OfflineRunnerImplementationSafetyStrategySignalProbeBoundary | None = None
    risk_observer_boundary: OfflineRunnerImplementationSafetyRiskObserverBoundary | None = None
    profitability_observer_boundary: OfflineRunnerImplementationSafetyProfitabilityObserverBoundary | None = None
    consistency_observer_boundary: OfflineRunnerImplementationSafetyConsistencyObserverBoundary | None = None
    journal_writer_boundary: OfflineRunnerImplementationSafetyJournalWriterBoundary | None = None
    observability_boundary: OfflineRunnerImplementationSafetyObservabilityBoundary | None = None
    human_approval_boundary: OfflineRunnerImplementationSafetyHumanApprovalBoundary | None = None
    stop_condition_boundary: OfflineRunnerImplementationSafetyStopConditionBoundary | None = None
    success_failure_boundary: OfflineRunnerImplementationSafetySuccessFailureBoundary | None = None
    audit_boundary: OfflineRunnerImplementationSafetyAuditBoundary | None = None
    go_no_go_boundary: OfflineRunnerImplementationSafetyGoNoGoBoundary | None = None
    abort_boundary: OfflineRunnerImplementationSafetyAbortBoundary | None = None
    no_real_broker_boundary: OfflineRunnerImplementationSafetyNoRealBrokerBoundary | None = None
    no_secret_read_boundary: OfflineRunnerImplementationSafetyNoSecretReadBoundary | None = None
    network_block_boundary: OfflineRunnerImplementationSafetyNetworkBlockBoundary | None = None
    http_websocket_socket_block_boundary: OfflineRunnerImplementationSafetyNetworkBlockBoundary | None = None
    order_blocking_boundary: OfflineRunnerImplementationSafetyOrderBlockingBoundary | None = None
    position_mutation_blocking_boundary: OfflineRunnerImplementationSafetyPositionMutationBlockingBoundary | None = None
    data_access_boundary: OfflineRunnerImplementationSafetyDataAccessBoundary | None = None
    test_strategy_boundary: OfflineRunnerImplementationSafetyTestStrategyBoundary | None = None
    rollback_strategy_boundary: OfflineRunnerImplementationSafetyRollbackStrategyBoundary | None = None
    boundaries: tuple[_OfflineRunnerImplementationSafetyBoundary, ...] = field(default_factory=tuple)
