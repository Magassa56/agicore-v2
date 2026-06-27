"""Models for Paper Broker Read-Only Connection Dry Run Controlled Offline Runner Implementation Plan."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanState(StrEnum):
    NOT_READY = "NOT_READY"
    OFFLINE_RUNNER_IMPLEMENTATION_PLAN_INPUT_INVALID = "OFFLINE_RUNNER_IMPLEMENTATION_PLAN_INPUT_INVALID"
    OFFLINE_RUNNER_IMPLEMENTATION_PLAN_BLOCKED = "OFFLINE_RUNNER_IMPLEMENTATION_PLAN_BLOCKED"
    OFFLINE_RUNNER_IMPLEMENTATION_PLAN_COMPLETED_WITH_WARNINGS = "OFFLINE_RUNNER_IMPLEMENTATION_PLAN_COMPLETED_WITH_WARNINGS"
    OFFLINE_RUNNER_IMPLEMENTATION_PLAN_COMPLETED = "OFFLINE_RUNNER_IMPLEMENTATION_PLAN_COMPLETED"
    READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE = "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE"

class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanDecision(StrEnum):
    BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN = "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN"
    REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_GATE_FIXES = "REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_GATE_FIXES"
    REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SCOPE_FIXES = "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SCOPE_FIXES"
    REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_ARCHITECTURE_FIXES = "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_ARCHITECTURE_FIXES"
    REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SEQUENCE_FIXES = "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SEQUENCE_FIXES"
    REQUIRE_OFFLINE_RUNNER_RUNTIME_CONTRACT_FIXES = "REQUIRE_OFFLINE_RUNNER_RUNTIME_CONTRACT_FIXES"
    REQUIRE_OFFLINE_RUNNER_INPUT_ADAPTER_FIXES = "REQUIRE_OFFLINE_RUNNER_INPUT_ADAPTER_FIXES"
    REQUIRE_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_ADAPTER_FIXES = "REQUIRE_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_ADAPTER_FIXES"
    REQUIRE_OFFLINE_RUNNER_SIMULATED_BROKER_ADAPTER_FIXES = "REQUIRE_OFFLINE_RUNNER_SIMULATED_BROKER_ADAPTER_FIXES"
    REQUIRE_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_ADAPTER_FIXES = "REQUIRE_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_ADAPTER_FIXES"
    REQUIRE_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_ADAPTER_FIXES = "REQUIRE_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_ADAPTER_FIXES"
    REQUIRE_OFFLINE_RUNNER_STRATEGY_SIGNAL_PROBE_FIXES = "REQUIRE_OFFLINE_RUNNER_STRATEGY_SIGNAL_PROBE_FIXES"
    REQUIRE_OFFLINE_RUNNER_RISK_OBSERVER_FIXES = "REQUIRE_OFFLINE_RUNNER_RISK_OBSERVER_FIXES"
    REQUIRE_OFFLINE_RUNNER_PROFITABILITY_OBSERVER_FIXES = "REQUIRE_OFFLINE_RUNNER_PROFITABILITY_OBSERVER_FIXES"
    REQUIRE_OFFLINE_RUNNER_CONSISTENCY_OBSERVER_FIXES = "REQUIRE_OFFLINE_RUNNER_CONSISTENCY_OBSERVER_FIXES"
    REQUIRE_OFFLINE_RUNNER_JOURNAL_WRITER_FIXES = "REQUIRE_OFFLINE_RUNNER_JOURNAL_WRITER_FIXES"
    REQUIRE_OFFLINE_RUNNER_OBSERVABILITY_FIXES = "REQUIRE_OFFLINE_RUNNER_OBSERVABILITY_FIXES"
    REQUIRE_OFFLINE_RUNNER_HUMAN_APPROVAL_FIXES = "REQUIRE_OFFLINE_RUNNER_HUMAN_APPROVAL_FIXES"
    REQUIRE_OFFLINE_RUNNER_STOP_CONDITION_FIXES = "REQUIRE_OFFLINE_RUNNER_STOP_CONDITION_FIXES"
    REQUIRE_OFFLINE_RUNNER_SUCCESS_FAILURE_FIXES = "REQUIRE_OFFLINE_RUNNER_SUCCESS_FAILURE_FIXES"
    REQUIRE_OFFLINE_RUNNER_AUDIT_FIXES = "REQUIRE_OFFLINE_RUNNER_AUDIT_FIXES"
    REQUIRE_OFFLINE_RUNNER_GO_NO_GO_FIXES = "REQUIRE_OFFLINE_RUNNER_GO_NO_GO_FIXES"
    REQUIRE_OFFLINE_RUNNER_ABORT_FIXES = "REQUIRE_OFFLINE_RUNNER_ABORT_FIXES"
    REQUIRE_OFFLINE_RUNNER_NO_REAL_BROKER_GUARD_FIXES = "REQUIRE_OFFLINE_RUNNER_NO_REAL_BROKER_GUARD_FIXES"
    REQUIRE_OFFLINE_RUNNER_NO_SECRET_READ_GUARD_FIXES = "REQUIRE_OFFLINE_RUNNER_NO_SECRET_READ_GUARD_FIXES"
    REQUIRE_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_FIXES = "REQUIRE_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_FIXES"
    REQUIRE_OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_FIXES = "REQUIRE_OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_FIXES"
    REQUIRE_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_FIXES = "REQUIRE_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_FIXES"
    REQUIRE_OFFLINE_RUNNER_DATA_ACCESS_GUARD_FIXES = "REQUIRE_OFFLINE_RUNNER_DATA_ACCESS_GUARD_FIXES"
    REQUIRE_OFFLINE_RUNNER_TEST_STRATEGY_FIXES = "REQUIRE_OFFLINE_RUNNER_TEST_STRATEGY_FIXES"
    REQUIRE_OFFLINE_RUNNER_ROLLBACK_STRATEGY_FIXES = "REQUIRE_OFFLINE_RUNNER_ROLLBACK_STRATEGY_FIXES"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN = "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN"

class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanRisk(StrEnum):
    FINAL_OFFLINE_RUNNER_SAFETY_GATE_NOT_APPROVED = "FINAL_OFFLINE_RUNNER_SAFETY_GATE_NOT_APPROVED"
    OFFLINE_RUNNER_IMPLEMENTATION_SCOPE_UNCLEAR = "OFFLINE_RUNNER_IMPLEMENTATION_SCOPE_UNCLEAR"
    OFFLINE_RUNNER_IMPLEMENTATION_ARCHITECTURE_UNSAFE = "OFFLINE_RUNNER_IMPLEMENTATION_ARCHITECTURE_UNSAFE"
    OFFLINE_RUNNER_IMPLEMENTATION_SEQUENCE_MISSING = "OFFLINE_RUNNER_IMPLEMENTATION_SEQUENCE_MISSING"
    OFFLINE_RUNNER_RUNTIME_CONTRACT_UNSAFE = "OFFLINE_RUNNER_RUNTIME_CONTRACT_UNSAFE"
    OFFLINE_RUNNER_INPUT_ADAPTER_UNSAFE = "OFFLINE_RUNNER_INPUT_ADAPTER_UNSAFE"
    OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_ADAPTER_UNSAFE = "OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_ADAPTER_UNSAFE"
    OFFLINE_RUNNER_SIMULATED_BROKER_ADAPTER_UNSAFE = "OFFLINE_RUNNER_SIMULATED_BROKER_ADAPTER_UNSAFE"
    OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_ADAPTER_UNSAFE = "OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_ADAPTER_UNSAFE"
    OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_ADAPTER_UNSAFE = "OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_ADAPTER_UNSAFE"
    OFFLINE_RUNNER_STRATEGY_SIGNAL_PROBE_MISSING = "OFFLINE_RUNNER_STRATEGY_SIGNAL_PROBE_MISSING"
    OFFLINE_RUNNER_RISK_OBSERVER_MISSING = "OFFLINE_RUNNER_RISK_OBSERVER_MISSING"
    OFFLINE_RUNNER_PROFITABILITY_OBSERVER_MISSING = "OFFLINE_RUNNER_PROFITABILITY_OBSERVER_MISSING"
    OFFLINE_RUNNER_CONSISTENCY_OBSERVER_MISSING = "OFFLINE_RUNNER_CONSISTENCY_OBSERVER_MISSING"
    OFFLINE_RUNNER_JOURNAL_WRITER_MISSING = "OFFLINE_RUNNER_JOURNAL_WRITER_MISSING"
    OFFLINE_RUNNER_OBSERVABILITY_MISSING = "OFFLINE_RUNNER_OBSERVABILITY_MISSING"
    OFFLINE_RUNNER_HUMAN_APPROVAL_MISSING = "OFFLINE_RUNNER_HUMAN_APPROVAL_MISSING"
    OFFLINE_RUNNER_STOP_CONDITIONS_MISSING = "OFFLINE_RUNNER_STOP_CONDITIONS_MISSING"
    OFFLINE_RUNNER_SUCCESS_CRITERIA_MISSING = "OFFLINE_RUNNER_SUCCESS_CRITERIA_MISSING"
    OFFLINE_RUNNER_FAILURE_CRITERIA_MISSING = "OFFLINE_RUNNER_FAILURE_CRITERIA_MISSING"
    OFFLINE_RUNNER_AUDIT_MISSING = "OFFLINE_RUNNER_AUDIT_MISSING"
    OFFLINE_RUNNER_GO_NO_GO_MISSING = "OFFLINE_RUNNER_GO_NO_GO_MISSING"
    OFFLINE_RUNNER_ABORT_MISSING = "OFFLINE_RUNNER_ABORT_MISSING"
    OFFLINE_RUNNER_REAL_BROKER_GUARD_MISSING = "OFFLINE_RUNNER_REAL_BROKER_GUARD_MISSING"
    OFFLINE_RUNNER_SECRET_READ_GUARD_UNSAFE = "OFFLINE_RUNNER_SECRET_READ_GUARD_UNSAFE"
    OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_UNSAFE = "OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_UNSAFE"
    OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_UNSAFE = "OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_UNSAFE"
    OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_UNSAFE = "OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_UNSAFE"
    OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_UNSAFE = "OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_UNSAFE"
    OFFLINE_RUNNER_DATA_ACCESS_GUARD_UNSAFE = "OFFLINE_RUNNER_DATA_ACCESS_GUARD_UNSAFE"
    OFFLINE_RUNNER_TEST_STRATEGY_MISSING = "OFFLINE_RUNNER_TEST_STRATEGY_MISSING"
    OFFLINE_RUNNER_ROLLBACK_STRATEGY_MISSING = "OFFLINE_RUNNER_ROLLBACK_STRATEGY_MISSING"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE = "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE"

class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanRecommendation(StrEnum):
    HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE = "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE"
    APPROVE_FINAL_OFFLINE_RUNNER_SAFETY_GATE_FIRST = "APPROVE_FINAL_OFFLINE_RUNNER_SAFETY_GATE_FIRST"
    FIX_OFFLINE_RUNNER_IMPLEMENTATION_SCOPE = "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SCOPE"
    FIX_OFFLINE_RUNNER_IMPLEMENTATION_ARCHITECTURE = "FIX_OFFLINE_RUNNER_IMPLEMENTATION_ARCHITECTURE"
    FIX_OFFLINE_RUNNER_IMPLEMENTATION_SEQUENCE = "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SEQUENCE"
    FIX_OFFLINE_RUNNER_RUNTIME_CONTRACT = "FIX_OFFLINE_RUNNER_RUNTIME_CONTRACT"
    FIX_OFFLINE_RUNNER_INPUT_ADAPTER = "FIX_OFFLINE_RUNNER_INPUT_ADAPTER"
    FIX_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_ADAPTER = "FIX_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_ADAPTER"
    FIX_OFFLINE_RUNNER_SIMULATED_BROKER_ADAPTER = "FIX_OFFLINE_RUNNER_SIMULATED_BROKER_ADAPTER"
    FIX_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_ADAPTER = "FIX_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_ADAPTER"
    FIX_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_ADAPTER = "FIX_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_ADAPTER"
    FIX_OFFLINE_RUNNER_STRATEGY_SIGNAL_PROBE = "FIX_OFFLINE_RUNNER_STRATEGY_SIGNAL_PROBE"
    FIX_OFFLINE_RUNNER_RISK_OBSERVER = "FIX_OFFLINE_RUNNER_RISK_OBSERVER"
    FIX_OFFLINE_RUNNER_PROFITABILITY_OBSERVER = "FIX_OFFLINE_RUNNER_PROFITABILITY_OBSERVER"
    FIX_OFFLINE_RUNNER_CONSISTENCY_OBSERVER = "FIX_OFFLINE_RUNNER_CONSISTENCY_OBSERVER"
    FIX_OFFLINE_RUNNER_JOURNAL_WRITER = "FIX_OFFLINE_RUNNER_JOURNAL_WRITER"
    FIX_OFFLINE_RUNNER_OBSERVABILITY = "FIX_OFFLINE_RUNNER_OBSERVABILITY"
    FIX_OFFLINE_RUNNER_HUMAN_APPROVAL = "FIX_OFFLINE_RUNNER_HUMAN_APPROVAL"
    FIX_OFFLINE_RUNNER_STOP_CONDITIONS = "FIX_OFFLINE_RUNNER_STOP_CONDITIONS"
    FIX_OFFLINE_RUNNER_SUCCESS_FAILURE = "FIX_OFFLINE_RUNNER_SUCCESS_FAILURE"
    FIX_OFFLINE_RUNNER_AUDIT = "FIX_OFFLINE_RUNNER_AUDIT"
    FIX_OFFLINE_RUNNER_GO_NO_GO = "FIX_OFFLINE_RUNNER_GO_NO_GO"
    FIX_OFFLINE_RUNNER_ABORT = "FIX_OFFLINE_RUNNER_ABORT"
    FIX_OFFLINE_RUNNER_NO_REAL_BROKER_GUARD = "FIX_OFFLINE_RUNNER_NO_REAL_BROKER_GUARD"
    FIX_OFFLINE_RUNNER_NO_SECRET_READ_GUARD = "FIX_OFFLINE_RUNNER_NO_SECRET_READ_GUARD"
    FIX_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD = "FIX_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD"
    FIX_OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD = "FIX_OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD"
    FIX_OFFLINE_RUNNER_ORDER_BLOCKING_GUARD = "FIX_OFFLINE_RUNNER_ORDER_BLOCKING_GUARD"
    FIX_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD = "FIX_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD"
    FIX_OFFLINE_RUNNER_DATA_ACCESS_GUARD = "FIX_OFFLINE_RUNNER_DATA_ACCESS_GUARD"
    FIX_OFFLINE_RUNNER_TEST_STRATEGY = "FIX_OFFLINE_RUNNER_TEST_STRATEGY"
    FIX_OFFLINE_RUNNER_ROLLBACK_STRATEGY = "FIX_OFFLINE_RUNNER_ROLLBACK_STRATEGY"
    RESTORE_OFFLINE_BOUNDARIES = "RESTORE_OFFLINE_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE = "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE"
    RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN_SUITE = "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN_SUITE"
    APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE = "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE"

Risk = PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanRisk

@dataclass(frozen=True)
class _OfflineRunnerImplementationArtifact:
    name: str
    score: int = 0
    defined: bool = False
    risks: tuple[Risk, ...] = ()
    details: tuple[str, ...] = ()
    offline_only: bool = False
    sandbox_only: bool = False
    implementation_plan_only: bool = False
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
    stop_conditions_defined: bool = False
    audit_defined: bool = False

@dataclass(frozen=True)
class OfflineRunnerImplementationScope(_OfflineRunnerImplementationArtifact):
    pass

@dataclass(frozen=True)
class OfflineRunnerImplementationArchitecture(_OfflineRunnerImplementationArtifact):
    pass

@dataclass(frozen=True)
class OfflineRunnerImplementationSequence(_OfflineRunnerImplementationArtifact):
    pass

@dataclass(frozen=True)
class OfflineRunnerRuntimeContract(_OfflineRunnerImplementationArtifact):
    pass

@dataclass(frozen=True)
class OfflineRunnerInputAdapterContract(_OfflineRunnerImplementationArtifact):
    pass

@dataclass(frozen=True)
class OfflineRunnerSyntheticMarketContextAdapter(_OfflineRunnerImplementationArtifact):
    pass

@dataclass(frozen=True)
class OfflineRunnerSimulatedBrokerAdapterContract(_OfflineRunnerImplementationArtifact):
    pass

@dataclass(frozen=True)
class OfflineRunnerAccountSnapshotAdapterContract(_OfflineRunnerImplementationArtifact):
    pass

@dataclass(frozen=True)
class OfflineRunnerMarketDataSnapshotAdapterContract(_OfflineRunnerImplementationArtifact):
    pass

@dataclass(frozen=True)
class OfflineRunnerStrategySignalProbeContract(_OfflineRunnerImplementationArtifact):
    pass

@dataclass(frozen=True)
class OfflineRunnerRiskObserverContract(_OfflineRunnerImplementationArtifact):
    pass

@dataclass(frozen=True)
class OfflineRunnerProfitabilityObserverContract(_OfflineRunnerImplementationArtifact):
    pass

@dataclass(frozen=True)
class OfflineRunnerConsistencyObserverContract(_OfflineRunnerImplementationArtifact):
    pass

@dataclass(frozen=True)
class OfflineRunnerJournalWriterContract(_OfflineRunnerImplementationArtifact):
    pass

@dataclass(frozen=True)
class OfflineRunnerObservabilityContract(_OfflineRunnerImplementationArtifact):
    pass

@dataclass(frozen=True)
class OfflineRunnerHumanApprovalContract(_OfflineRunnerImplementationArtifact):
    pass

@dataclass(frozen=True)
class OfflineRunnerStopConditionContract(_OfflineRunnerImplementationArtifact):
    pass

@dataclass(frozen=True)
class OfflineRunnerSuccessCriteriaContract(_OfflineRunnerImplementationArtifact):
    pass

@dataclass(frozen=True)
class OfflineRunnerFailureCriteriaContract(_OfflineRunnerImplementationArtifact):
    pass

@dataclass(frozen=True)
class OfflineRunnerAuditContract(_OfflineRunnerImplementationArtifact):
    pass

@dataclass(frozen=True)
class OfflineRunnerGoNoGoContract(_OfflineRunnerImplementationArtifact):
    pass

@dataclass(frozen=True)
class OfflineRunnerAbortContract(_OfflineRunnerImplementationArtifact):
    pass

@dataclass(frozen=True)
class OfflineRunnerNoRealBrokerGuard(_OfflineRunnerImplementationArtifact):
    pass

@dataclass(frozen=True)
class OfflineRunnerNoSecretReadGuard(_OfflineRunnerImplementationArtifact):
    pass

@dataclass(frozen=True)
class OfflineRunnerNetworkBlockGuard(_OfflineRunnerImplementationArtifact):
    pass

@dataclass(frozen=True)
class OfflineRunnerOrderBlockingGuard(_OfflineRunnerImplementationArtifact):
    pass

@dataclass(frozen=True)
class OfflineRunnerPositionMutationBlockingGuard(_OfflineRunnerImplementationArtifact):
    pass

@dataclass(frozen=True)
class OfflineRunnerDataAccessGuard(_OfflineRunnerImplementationArtifact):
    pass

@dataclass(frozen=True)
class OfflineRunnerTestStrategy(_OfflineRunnerImplementationArtifact):
    pass

@dataclass(frozen=True)
class OfflineRunnerRollbackStrategy(_OfflineRunnerImplementationArtifact):
    pass

@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanScore:
    overall_score: int = 0
    final_safety_gate_score: int = 0
    implementation_scope_score: int = 0
    implementation_architecture_score: int = 0
    implementation_sequence_score: int = 0
    runtime_contract_score: int = 0
    input_adapter_contract_score: int = 0
    synthetic_market_context_adapter_score: int = 0
    simulated_broker_adapter_contract_score: int = 0
    account_snapshot_adapter_contract_score: int = 0
    market_data_snapshot_adapter_contract_score: int = 0
    strategy_signal_probe_contract_score: int = 0
    risk_observer_contract_score: int = 0
    profitability_observer_contract_score: int = 0
    consistency_observer_contract_score: int = 0
    journal_writer_contract_score: int = 0
    observability_contract_score: int = 0
    human_approval_contract_score: int = 0
    stop_condition_contract_score: int = 0
    success_criteria_contract_score: int = 0
    failure_criteria_contract_score: int = 0
    audit_contract_score: int = 0
    go_no_go_contract_score: int = 0
    abort_contract_score: int = 0
    no_real_broker_guard_score: int = 0
    no_secret_read_guard_score: int = 0
    network_block_guard_score: int = 0
    http_websocket_socket_block_guard_score: int = 0
    order_blocking_guard_score: int = 0
    position_mutation_blocking_guard_score: int = 0
    data_access_guard_score: int = 0
    test_strategy_score: int = 0
    rollback_strategy_score: int = 0

@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanInput:
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
    final_offline_runner_safety_gate_approved: bool | None = None
    offline_runner_implementation_scope_defined: bool = True
    offline_runner_implementation_architecture_defined: bool = True
    offline_runner_implementation_sequence_defined: bool = True
    offline_runner_runtime_contract_defined: bool = True
    offline_runner_input_adapter_contract_defined: bool = True
    offline_runner_synthetic_market_context_adapter_defined: bool = True
    offline_runner_simulated_broker_adapter_contract_defined: bool = True
    offline_runner_account_snapshot_adapter_contract_defined: bool = True
    offline_runner_market_data_snapshot_adapter_contract_defined: bool = True
    offline_runner_strategy_signal_probe_contract_defined: bool = True
    offline_runner_risk_observer_contract_defined: bool = True
    offline_runner_profitability_observer_contract_defined: bool = True
    offline_runner_consistency_observer_contract_defined: bool = True
    offline_runner_journal_writer_contract_defined: bool = True
    offline_runner_observability_contract_defined: bool = True
    offline_runner_human_approval_contract_defined: bool = True
    offline_runner_stop_condition_contract_defined: bool = True
    offline_runner_success_criteria_contract_defined: bool = True
    offline_runner_failure_criteria_contract_defined: bool = True
    offline_runner_audit_contract_defined: bool = True
    offline_runner_go_no_go_contract_defined: bool = True
    offline_runner_abort_contract_defined: bool = True
    offline_runner_no_real_broker_guard_defined: bool = True
    offline_runner_no_secret_read_guard_defined: bool = True
    offline_runner_network_block_guard_defined: bool = True
    offline_runner_http_websocket_socket_block_guard_defined: bool = True
    offline_runner_order_blocking_guard_defined: bool = True
    offline_runner_position_mutation_blocking_guard_defined: bool = True
    offline_runner_data_access_guard_defined: bool = True
    offline_runner_test_strategy_defined: bool = True
    offline_runner_rollback_strategy_defined: bool = True
    offline_mode_enforced: bool = True
    sandbox_mode_enforced: bool = True
    implementation_plan_only: bool = True
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
    paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate_requested: bool = False
    final_safety_gate_score: int | None = None
    implementation_scope_score: int | None = None
    implementation_architecture_score: int | None = None
    implementation_sequence_score: int | None = None
    runtime_contract_score: int | None = None
    input_adapter_contract_score: int | None = None
    synthetic_market_context_adapter_score: int | None = None
    simulated_broker_adapter_contract_score: int | None = None
    account_snapshot_adapter_contract_score: int | None = None
    market_data_snapshot_adapter_contract_score: int | None = None
    strategy_signal_probe_contract_score: int | None = None
    risk_observer_contract_score: int | None = None
    profitability_observer_contract_score: int | None = None
    consistency_observer_contract_score: int | None = None
    journal_writer_contract_score: int | None = None
    observability_contract_score: int | None = None
    human_approval_contract_score: int | None = None
    stop_condition_contract_score: int | None = None
    success_criteria_contract_score: int | None = None
    failure_criteria_contract_score: int | None = None
    audit_contract_score: int | None = None
    go_no_go_contract_score: int | None = None
    abort_contract_score: int | None = None
    no_real_broker_guard_score: int | None = None
    no_secret_read_guard_score: int | None = None
    network_block_guard_score: int | None = None
    http_websocket_socket_block_guard_score: int | None = None
    order_blocking_guard_score: int | None = None
    position_mutation_blocking_guard_score: int | None = None
    data_access_guard_score: int | None = None
    test_strategy_score: int | None = None
    rollback_strategy_score: int | None = None

@dataclass(frozen=True)
class PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanResult:
    state: PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanState
    decision: PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanDecision
    score: PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanScore
    risks: tuple[Risk, ...] = ()
    recommendations: tuple[PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanRecommendation, ...] = ()
    summary: str = ""
    markdown_report: str = ""
    offline_only: bool = True
    sandbox_only: bool = True
    implementation_plan_only: bool = True
    runner_created: bool = False
    runner_executed: bool = False
    dry_run_executed: bool = False
    next_phase: str = "PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE"
    implementation_scope: OfflineRunnerImplementationScope | None = None
    implementation_architecture: OfflineRunnerImplementationArchitecture | None = None
    implementation_sequence: OfflineRunnerImplementationSequence | None = None
    runtime_contract: OfflineRunnerRuntimeContract | None = None
    input_adapter_contract: OfflineRunnerInputAdapterContract | None = None
    synthetic_market_context_adapter: OfflineRunnerSyntheticMarketContextAdapter | None = None
    simulated_broker_adapter_contract: OfflineRunnerSimulatedBrokerAdapterContract | None = None
    account_snapshot_adapter_contract: OfflineRunnerAccountSnapshotAdapterContract | None = None
    market_data_snapshot_adapter_contract: OfflineRunnerMarketDataSnapshotAdapterContract | None = None
    strategy_signal_probe_contract: OfflineRunnerStrategySignalProbeContract | None = None
    risk_observer_contract: OfflineRunnerRiskObserverContract | None = None
    profitability_observer_contract: OfflineRunnerProfitabilityObserverContract | None = None
    consistency_observer_contract: OfflineRunnerConsistencyObserverContract | None = None
    journal_writer_contract: OfflineRunnerJournalWriterContract | None = None
    observability_contract: OfflineRunnerObservabilityContract | None = None
    human_approval_contract: OfflineRunnerHumanApprovalContract | None = None
    stop_condition_contract: OfflineRunnerStopConditionContract | None = None
    success_criteria_contract: OfflineRunnerSuccessCriteriaContract | None = None
    failure_criteria_contract: OfflineRunnerFailureCriteriaContract | None = None
    audit_contract: OfflineRunnerAuditContract | None = None
    go_no_go_contract: OfflineRunnerGoNoGoContract | None = None
    abort_contract: OfflineRunnerAbortContract | None = None
    no_real_broker_guard: OfflineRunnerNoRealBrokerGuard | None = None
    no_secret_read_guard: OfflineRunnerNoSecretReadGuard | None = None
    network_block_guard: OfflineRunnerNetworkBlockGuard | None = None
    http_websocket_socket_block_guard: OfflineRunnerNetworkBlockGuard | None = None
    order_blocking_guard: OfflineRunnerOrderBlockingGuard | None = None
    position_mutation_blocking_guard: OfflineRunnerPositionMutationBlockingGuard | None = None
    data_access_guard: OfflineRunnerDataAccessGuard | None = None
    test_strategy: OfflineRunnerTestStrategy | None = None
    rollback_strategy: OfflineRunnerRollbackStrategy | None = None
    artifacts: tuple[_OfflineRunnerImplementationArtifact, ...] = field(default_factory=tuple)
