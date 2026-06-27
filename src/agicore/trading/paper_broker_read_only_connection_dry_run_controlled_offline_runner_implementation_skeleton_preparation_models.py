"""Models for controlled offline runner implementation skeleton preparation."""
from __future__ import annotations

from dataclasses import field, make_dataclass
from enum import StrEnum
from typing import Any

_ITEMS = [
    ("scope_contract", "OfflineRunnerSkeletonScopePreparationContract", "OFFLINE_RUNNER_SKELETON_SCOPE_PREPARATION_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_SCOPE_PREPARATION_FIXES", "prepare_offline_runner_skeleton_scope_contract"),
    ("module_boundaries_contract", "OfflineRunnerSkeletonModuleBoundariesPreparationContract", "OFFLINE_RUNNER_SKELETON_MODULE_BOUNDARIES_PREPARATION_UNSAFE", "REQUIRE_OFFLINE_RUNNER_SKELETON_MODULE_BOUNDARIES_PREPARATION_FIXES", "prepare_offline_runner_skeleton_module_boundaries_contract"),
    ("file_layout_contract", "OfflineRunnerSkeletonFileLayoutPreparationContract", "OFFLINE_RUNNER_SKELETON_FILE_LAYOUT_PREPARATION_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_FILE_LAYOUT_PREPARATION_FIXES", "prepare_offline_runner_skeleton_file_layout_contract"),
    ("interface_contract", "OfflineRunnerSkeletonInterfacePreparationContract", "OFFLINE_RUNNER_SKELETON_INTERFACE_PREPARATION_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_INTERFACE_PREPARATION_FIXES", "prepare_offline_runner_skeleton_interface_contract"),
    ("runtime_stub_contract", "OfflineRunnerSkeletonRuntimeStubPreparationContract", "OFFLINE_RUNNER_SKELETON_RUNTIME_STUB_PREPARATION_UNSAFE", "REQUIRE_OFFLINE_RUNNER_SKELETON_RUNTIME_STUB_PREPARATION_FIXES", "prepare_offline_runner_skeleton_runtime_stub_contract"),
    ("input_adapter_stub_contract", "OfflineRunnerSkeletonInputAdapterStubPreparationContract", "OFFLINE_RUNNER_SKELETON_INPUT_ADAPTER_STUB_PREPARATION_UNSAFE", "REQUIRE_OFFLINE_RUNNER_SKELETON_INPUT_ADAPTER_STUB_PREPARATION_FIXES", "prepare_offline_runner_skeleton_input_adapter_stub_contract"),
    ("synthetic_market_context_stub_contract", "OfflineRunnerSkeletonSyntheticMarketContextStubPreparationContract", "OFFLINE_RUNNER_SKELETON_SYNTHETIC_MARKET_CONTEXT_STUB_PREPARATION_UNSAFE", "REQUIRE_OFFLINE_RUNNER_SKELETON_SYNTHETIC_MARKET_CONTEXT_STUB_PREPARATION_FIXES", "prepare_offline_runner_skeleton_synthetic_market_context_stub_contract"),
    ("simulated_broker_stub_contract", "OfflineRunnerSkeletonSimulatedBrokerStubPreparationContract", "OFFLINE_RUNNER_SKELETON_SIMULATED_BROKER_STUB_PREPARATION_UNSAFE", "REQUIRE_OFFLINE_RUNNER_SKELETON_SIMULATED_BROKER_STUB_PREPARATION_FIXES", "prepare_offline_runner_skeleton_simulated_broker_stub_contract"),
    ("account_snapshot_stub_contract", "OfflineRunnerSkeletonAccountSnapshotStubPreparationContract", "OFFLINE_RUNNER_SKELETON_ACCOUNT_SNAPSHOT_STUB_PREPARATION_UNSAFE", "REQUIRE_OFFLINE_RUNNER_SKELETON_ACCOUNT_SNAPSHOT_STUB_PREPARATION_FIXES", "prepare_offline_runner_skeleton_account_snapshot_stub_contract"),
    ("market_data_snapshot_stub_contract", "OfflineRunnerSkeletonMarketDataSnapshotStubPreparationContract", "OFFLINE_RUNNER_SKELETON_MARKET_DATA_SNAPSHOT_STUB_PREPARATION_UNSAFE", "REQUIRE_OFFLINE_RUNNER_SKELETON_MARKET_DATA_SNAPSHOT_STUB_PREPARATION_FIXES", "prepare_offline_runner_skeleton_market_data_snapshot_stub_contract"),
    ("strategy_signal_probe_stub_contract", "OfflineRunnerSkeletonStrategySignalProbeStubPreparationContract", "OFFLINE_RUNNER_SKELETON_STRATEGY_SIGNAL_PROBE_STUB_PREPARATION_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_STRATEGY_SIGNAL_PROBE_STUB_PREPARATION_FIXES", "prepare_offline_runner_skeleton_strategy_signal_probe_stub_contract"),
    ("risk_observer_stub_contract", "OfflineRunnerSkeletonRiskObserverStubPreparationContract", "OFFLINE_RUNNER_SKELETON_RISK_OBSERVER_STUB_PREPARATION_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_RISK_OBSERVER_STUB_PREPARATION_FIXES", "prepare_offline_runner_skeleton_risk_observer_stub_contract"),
    ("profitability_observer_stub_contract", "OfflineRunnerSkeletonProfitabilityObserverStubPreparationContract", "OFFLINE_RUNNER_SKELETON_PROFITABILITY_OBSERVER_STUB_PREPARATION_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_PROFITABILITY_OBSERVER_STUB_PREPARATION_FIXES", "prepare_offline_runner_skeleton_profitability_observer_stub_contract"),
    ("consistency_observer_stub_contract", "OfflineRunnerSkeletonConsistencyObserverStubPreparationContract", "OFFLINE_RUNNER_SKELETON_CONSISTENCY_OBSERVER_STUB_PREPARATION_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_CONSISTENCY_OBSERVER_STUB_PREPARATION_FIXES", "prepare_offline_runner_skeleton_consistency_observer_stub_contract"),
    ("journal_writer_stub_contract", "OfflineRunnerSkeletonJournalWriterStubPreparationContract", "OFFLINE_RUNNER_SKELETON_JOURNAL_WRITER_STUB_PREPARATION_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_JOURNAL_WRITER_STUB_PREPARATION_FIXES", "prepare_offline_runner_skeleton_journal_writer_stub_contract"),
    ("observability_stub_contract", "OfflineRunnerSkeletonObservabilityStubPreparationContract", "OFFLINE_RUNNER_SKELETON_OBSERVABILITY_STUB_PREPARATION_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_OBSERVABILITY_STUB_PREPARATION_FIXES", "prepare_offline_runner_skeleton_observability_stub_contract"),
    ("human_approval_stub_contract", "OfflineRunnerSkeletonHumanApprovalStubPreparationContract", "OFFLINE_RUNNER_SKELETON_HUMAN_APPROVAL_STUB_PREPARATION_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_HUMAN_APPROVAL_STUB_PREPARATION_FIXES", "prepare_offline_runner_skeleton_human_approval_stub_contract"),
    ("stop_condition_stub_contract", "OfflineRunnerSkeletonStopConditionStubPreparationContract", "OFFLINE_RUNNER_SKELETON_STOP_CONDITIONS_STUB_PREPARATION_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_STOP_CONDITION_STUB_PREPARATION_FIXES", "prepare_offline_runner_skeleton_stop_condition_stub_contract"),
    ("success_failure_stub_contract", "OfflineRunnerSkeletonSuccessFailureStubPreparationContract", "OFFLINE_RUNNER_SKELETON_SUCCESS_FAILURE_STUB_PREPARATION_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_SUCCESS_FAILURE_STUB_PREPARATION_FIXES", "prepare_offline_runner_skeleton_success_failure_stub_contract"),
    ("audit_stub_contract", "OfflineRunnerSkeletonAuditStubPreparationContract", "OFFLINE_RUNNER_SKELETON_AUDIT_STUB_PREPARATION_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_AUDIT_STUB_PREPARATION_FIXES", "prepare_offline_runner_skeleton_audit_stub_contract"),
    ("go_no_go_stub_contract", "OfflineRunnerSkeletonGoNoGoStubPreparationContract", "OFFLINE_RUNNER_SKELETON_GO_NO_GO_STUB_PREPARATION_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_GO_NO_GO_STUB_PREPARATION_FIXES", "prepare_offline_runner_skeleton_go_no_go_stub_contract"),
    ("abort_stub_contract", "OfflineRunnerSkeletonAbortStubPreparationContract", "OFFLINE_RUNNER_SKELETON_ABORT_STUB_PREPARATION_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_ABORT_STUB_PREPARATION_FIXES", "prepare_offline_runner_skeleton_abort_stub_contract"),
    ("no_real_broker_guard", "OfflineRunnerSkeletonNoRealBrokerPreparationGuard", "OFFLINE_RUNNER_SKELETON_REAL_BROKER_GUARD_PREPARATION_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_NO_REAL_BROKER_GUARD_PREPARATION_FIXES", "prepare_offline_runner_skeleton_no_real_broker_guard"),
    ("no_secret_read_guard", "OfflineRunnerSkeletonNoSecretReadPreparationGuard", "OFFLINE_RUNNER_SKELETON_SECRET_READ_GUARD_PREPARATION_UNSAFE", "REQUIRE_OFFLINE_RUNNER_SKELETON_NO_SECRET_READ_GUARD_PREPARATION_FIXES", "prepare_offline_runner_skeleton_no_secret_read_guard"),
    ("network_block_guard", "OfflineRunnerSkeletonNetworkBlockPreparationGuard", "OFFLINE_RUNNER_SKELETON_NETWORK_BLOCK_GUARD_PREPARATION_UNSAFE", "REQUIRE_OFFLINE_RUNNER_SKELETON_NETWORK_BLOCK_GUARD_PREPARATION_FIXES", "prepare_offline_runner_skeleton_network_block_guard"),
    ("http_websocket_socket_block_guard", "OfflineRunnerSkeletonNetworkBlockPreparationGuard", "OFFLINE_RUNNER_SKELETON_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_PREPARATION_UNSAFE", "REQUIRE_OFFLINE_RUNNER_SKELETON_NETWORK_BLOCK_GUARD_PREPARATION_FIXES", "prepare_offline_runner_skeleton_http_websocket_socket_block_guard"),
    ("order_blocking_guard", "OfflineRunnerSkeletonOrderBlockingPreparationGuard", "OFFLINE_RUNNER_SKELETON_ORDER_BLOCKING_GUARD_PREPARATION_UNSAFE", "REQUIRE_OFFLINE_RUNNER_SKELETON_ORDER_BLOCKING_GUARD_PREPARATION_FIXES", "prepare_offline_runner_skeleton_order_blocking_guard"),
    ("position_mutation_blocking_guard", "OfflineRunnerSkeletonPositionMutationBlockingPreparationGuard", "OFFLINE_RUNNER_SKELETON_POSITION_MUTATION_BLOCKING_GUARD_PREPARATION_UNSAFE", "REQUIRE_OFFLINE_RUNNER_SKELETON_POSITION_MUTATION_BLOCKING_GUARD_PREPARATION_FIXES", "prepare_offline_runner_skeleton_position_mutation_blocking_guard"),
    ("data_access_guard", "OfflineRunnerSkeletonDataAccessPreparationGuard", "OFFLINE_RUNNER_SKELETON_DATA_ACCESS_GUARD_PREPARATION_UNSAFE", "REQUIRE_OFFLINE_RUNNER_SKELETON_DATA_ACCESS_GUARD_PREPARATION_FIXES", "prepare_offline_runner_skeleton_data_access_guard"),
    ("test_strategy_contract", "OfflineRunnerSkeletonTestStrategyPreparationContract", "OFFLINE_RUNNER_SKELETON_TEST_STRATEGY_PREPARATION_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_TEST_STRATEGY_PREPARATION_FIXES", "prepare_offline_runner_skeleton_test_strategy_contract"),
    ("rollback_strategy_contract", "OfflineRunnerSkeletonRollbackStrategyPreparationContract", "OFFLINE_RUNNER_SKELETON_ROLLBACK_STRATEGY_PREPARATION_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_ROLLBACK_STRATEGY_PREPARATION_FIXES", "prepare_offline_runner_skeleton_rollback_strategy_contract"),
    ("readiness_criteria_contract", "OfflineRunnerSkeletonReadinessCriteriaPreparationContract", "OFFLINE_RUNNER_SKELETON_READINESS_CRITERIA_PREPARATION_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_READINESS_CRITERIA_PREPARATION_FIXES", "prepare_offline_runner_skeleton_readiness_criteria_contract"),
]
_RISK_BY_KEY = {k: r for k, _c, r, _d, _f in _ITEMS}
_DECISION_BY_KEY = {k: d for k, _c, _r, d, _f in _ITEMS}
_RECOMMENDATION_BY_KEY = {k: f"FIX_{r}" for k, _c, r, _d, _f in _ITEMS}

PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationState = StrEnum(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationState",
    {
        "NOT_READY": "NOT_READY",
        "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_INPUT_INVALID": "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_INPUT_INVALID",
        "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_BLOCKED": "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_BLOCKED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_COMPLETED_WITH_WARNINGS": "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_COMPLETED_WITH_WARNINGS",
        "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_COMPLETED": "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_COMPLETED",
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_REVIEW": "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_REVIEW",
    },
)
PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationDecision = StrEnum(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationDecision",
    {
        "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION": "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE_FIXES",
        **{d: d for d in _DECISION_BY_KEY.values()},
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION": "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION",
    },
)
PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationRisk = StrEnum(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationRisk",
    {
        "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE_NOT_APPROVED": "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE_NOT_APPROVED",
        **{r: r for r in _RISK_BY_KEY.values()},
        "REAL_EXECUTION_BOUNDARY_VIOLATION": "REAL_EXECUTION_BOUNDARY_VIOLATION",
        "DATA_ACCESS_VIOLATION": "DATA_ACCESS_VIOLATION",
        "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_REVIEW": "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_REVIEW",
    },
)
PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationRecommendation = StrEnum(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationRecommendation",
    {
        "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_REVIEW": "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_REVIEW",
        "APPROVE_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE_FIRST": "APPROVE_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE_FIRST",
        **{rec: rec for rec in _RECOMMENDATION_BY_KEY.values()},
        "RESTORE_OFFLINE_BOUNDARIES": "RESTORE_OFFLINE_BOUNDARIES",
        "REMOVE_DATA_ACCESS": "REMOVE_DATA_ACCESS",
        "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_REVIEW": "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_REVIEW",
        "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_SUITE": "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_SUITE",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_REVIEW": "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_REVIEW",
    },
)

Risk = PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationRisk
_BASE_FIELDS = [
    ("name", str),
    ("score", int, 0),
    ("prepared", bool, False),
    ("risks", tuple[Risk, ...], ()),
    ("details", tuple[str, ...], ()),
    ("offline_only", bool, False),
    ("sandbox_only", bool, False),
    ("skeleton_preparation_only", bool, False),
    ("no_runner_created", bool, False),
    ("no_runner_execution", bool, False),
    ("no_dry_run_execution", bool, False),
    ("no_real_broker", bool, False),
    ("no_secret_read", bool, False),
    ("network_blocked", bool, False),
    ("http_blocked", bool, False),
    ("websocket_blocked", bool, False),
    ("socket_blocked", bool, False),
    ("order_blocked", bool, False),
    ("position_mutation_blocked", bool, False),
    ("data_access_blocked", bool, False),
    ("read_only", bool, False),
    ("simulated_only", bool, False),
    ("stub_only", bool, False),
    ("observation_only", bool, False),
    ("human_approval_required", bool, False),
    ("stop_conditions_prepared", bool, False),
    ("audit_prepared", bool, False),
    ("test_strategy_prepared", bool, False),
    ("rollback_strategy_prepared", bool, False),
    ("readiness_criteria_prepared", bool, False),
]
for _k, _c, _r, _d, _f in _ITEMS:
    globals()[_c] = make_dataclass(_c, _BASE_FIELDS, frozen=True)

PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationScore = make_dataclass(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationScore",
    [("overall_score", int, 0), ("implementation_skeleton_safety_gate_score", int, 0)]
    + [(f"{k}_score", int, 0) for k, _c, _r, _d, _f in _ITEMS],
    frozen=True,
)
_COMPAT_FIELDS = [
    "paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_safety_gate",
    "paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_plan",
    "paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_final_safety_gate",
    "paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_final_plan",
    "paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_review",
    "paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation",
    "paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate",
    "paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_plan",
    "paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_safety_gate",
    "paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_plan",
    "paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review",
    "paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation",
    "paper_broker_read_only_connection_dry_run_controlled_offline_runner_safety_gate",
    "paper_broker_read_only_connection_dry_run_controlled_offline_runner_plan",
    "paper_broker_read_only_connection_dry_run_controlled_execution_final_safety_gate",
    "paper_broker_read_only_connection_dry_run_controlled_execution_final_plan",
    "paper_broker_read_only_connection_dry_run_controlled_execution_preparation_review",
    "paper_broker_read_only_connection_dry_run_controlled_execution_preparation",
    "paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate",
    "paper_broker_read_only_connection_dry_run_controlled_execution_plan",
    "paper_broker_read_only_connection_dry_run_execution_final_safety_gate",
    "paper_broker_read_only_connection_dry_run_execution_final_plan",
    "paper_broker_read_only_connection_dry_run_execution_preparation_review",
    "paper_broker_read_only_connection_dry_run_execution_preparation",
    "paper_broker_read_only_connection_dry_run_execution_safety_gate",
    "paper_broker_read_only_connection_dry_run_execution_plan",
    "paper_broker_read_only_connection_dry_run_preparation_review",
    "paper_broker_read_only_connection_dry_run_preparation",
    "paper_broker_read_only_connection_dry_run_safety_gate",
    "paper_broker_read_only_connection_dry_run_plan",
    "paper_broker_read_only_connection_preparation_review",
    "paper_broker_read_only_connection_preparation",
    "paper_broker_read_only_connection_safety_gate",
    "paper_broker_read_only_connection_plan",
    "paper_broker_read_only_safety_review",
    "paper_broker_read_only_preparation",
]
PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationInput = make_dataclass(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationInput",
    [(n, Any | None, None) for n in _COMPAT_FIELDS]
    + [("offline_runner_implementation_skeleton_safety_gate_approved", bool | None, None)]
    + [(f"offline_runner_{k}_prepared", bool, True) for k, _c, _r, _d, _f in _ITEMS]
    + [
        ("offline_mode_enforced", bool, True),
        ("sandbox_mode_enforced", bool, True),
        ("skeleton_preparation_only", bool, True),
        ("no_runner_created", bool, True),
        ("no_runner_execution", bool, True),
        ("no_dry_run_execution", bool, True),
        ("no_broker_connection", bool, True),
        ("no_real_broker", bool, True),
        ("no_alpaca_real", bool, True),
        ("no_api_key_read", bool, True),
        ("no_env_var_read", bool, True),
        ("no_hardcoded_secrets", bool, True),
        ("no_http_transport", bool, True),
        ("no_websocket_transport", bool, True),
        ("no_socket_transport", bool, True),
        ("no_external_api", bool, True),
        ("no_external_ml", bool, True),
        ("no_external_llm", bool, True),
        ("no_live_execution", bool, True),
        ("no_real_order", bool, True),
        ("no_position_mutation", bool, True),
        ("no_real_account_access", bool, True),
        ("stubs_only", bool, True),
        ("human_approval_required", bool, True),
        ("test_strategy_required", bool, True),
        ("rollback_strategy_required", bool, True),
        ("readiness_criteria_required", bool, True),
        ("real_execution_requested", bool, False),
        ("runner_creation_requested", bool, False),
        ("runner_execution_requested", bool, False),
        ("dry_run_requested", bool, False),
        ("dry_run_executed", bool, False),
        ("broker_connection_requested", bool, False),
        ("api_key_read_requested", bool, False),
        ("env_var_read_requested", bool, False),
        ("hardcoded_secret_detected", bool, False),
        ("network_transport_requested", bool, False),
        ("external_api_requested", bool, False),
        ("order_execution_requested", bool, False),
        ("position_mutation_requested", bool, False),
        ("account_access_requested", bool, False),
        ("data_access_requested", bool, False),
        ("paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_preparation_review_requested", bool, False),
        ("implementation_skeleton_safety_gate_score", int | None, None),
    ]
    + [(f"{k}_score", int | None, None) for k, _c, _r, _d, _f in _ITEMS],
    frozen=True,
)
PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationResult = make_dataclass(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationResult",
    [
        ("state", PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationState),
        ("decision", PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationDecision),
        ("score", PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationScore),
        ("risks", tuple[Risk, ...], ()),
        ("recommendations", tuple[PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationRecommendation, ...], ()),
        ("summary", str, ""),
        ("markdown_report", str, ""),
        ("offline_only", bool, True),
        ("sandbox_only", bool, True),
        ("skeleton_preparation_only", bool, True),
        ("runner_created", bool, False),
        ("runner_executed", bool, False),
        ("dry_run_executed", bool, False),
        ("next_phase", str, "PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_REVIEW"),
    ]
    + [(k, globals()[c] | None, None) for k, c, _r, _d, _f in _ITEMS]
    + [("contracts", dict[str, Any], field(default_factory=dict))],
    frozen=True,
)
__all__ = [
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationInput",
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationResult",
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationState",
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationDecision",
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationRisk",
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationRecommendation",
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationScore",
] + [c for _k, c, _r, _d, _f in _ITEMS]
