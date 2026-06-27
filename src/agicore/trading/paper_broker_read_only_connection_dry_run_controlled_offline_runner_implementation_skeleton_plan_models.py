"""Models for controlled offline runner implementation skeleton plan."""
from __future__ import annotations

from dataclasses import field, make_dataclass
from enum import StrEnum
from typing import Any

_ITEMS = [
    ("scope", "OfflineRunnerSkeletonScope", "OFFLINE_RUNNER_SKELETON_SCOPE_UNCLEAR", "REQUIRE_OFFLINE_RUNNER_SKELETON_SCOPE_FIXES", "define_offline_runner_skeleton_scope"),
    ("module_boundaries", "OfflineRunnerSkeletonModuleBoundaries", "OFFLINE_RUNNER_SKELETON_MODULE_BOUNDARIES_UNSAFE", "REQUIRE_OFFLINE_RUNNER_SKELETON_MODULE_BOUNDARY_FIXES", "define_offline_runner_skeleton_module_boundaries"),
    ("file_layout", "OfflineRunnerSkeletonFileLayout", "OFFLINE_RUNNER_SKELETON_FILE_LAYOUT_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_FILE_LAYOUT_FIXES", "define_offline_runner_skeleton_file_layout"),
    ("interface_contract", "OfflineRunnerSkeletonInterfaceContract", "OFFLINE_RUNNER_SKELETON_INTERFACE_CONTRACT_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_INTERFACE_CONTRACT_FIXES", "define_offline_runner_skeleton_interface_contract"),
    ("runtime_stub_contract", "OfflineRunnerSkeletonRuntimeStubContract", "OFFLINE_RUNNER_SKELETON_RUNTIME_STUB_UNSAFE", "REQUIRE_OFFLINE_RUNNER_SKELETON_RUNTIME_STUB_FIXES", "define_offline_runner_skeleton_runtime_stub_contract"),
    ("input_adapter_stub_contract", "OfflineRunnerSkeletonInputAdapterStubContract", "OFFLINE_RUNNER_SKELETON_INPUT_ADAPTER_STUB_UNSAFE", "REQUIRE_OFFLINE_RUNNER_SKELETON_INPUT_ADAPTER_STUB_FIXES", "define_offline_runner_skeleton_input_adapter_stub_contract"),
    ("synthetic_market_context_stub_contract", "OfflineRunnerSkeletonSyntheticMarketContextStubContract", "OFFLINE_RUNNER_SKELETON_SYNTHETIC_MARKET_CONTEXT_STUB_UNSAFE", "REQUIRE_OFFLINE_RUNNER_SKELETON_SYNTHETIC_MARKET_CONTEXT_STUB_FIXES", "define_offline_runner_skeleton_synthetic_market_context_stub_contract"),
    ("simulated_broker_stub_contract", "OfflineRunnerSkeletonSimulatedBrokerStubContract", "OFFLINE_RUNNER_SKELETON_SIMULATED_BROKER_STUB_UNSAFE", "REQUIRE_OFFLINE_RUNNER_SKELETON_SIMULATED_BROKER_STUB_FIXES", "define_offline_runner_skeleton_simulated_broker_stub_contract"),
    ("account_snapshot_stub_contract", "OfflineRunnerSkeletonAccountSnapshotStubContract", "OFFLINE_RUNNER_SKELETON_ACCOUNT_SNAPSHOT_STUB_UNSAFE", "REQUIRE_OFFLINE_RUNNER_SKELETON_ACCOUNT_SNAPSHOT_STUB_FIXES", "define_offline_runner_skeleton_account_snapshot_stub_contract"),
    ("market_data_snapshot_stub_contract", "OfflineRunnerSkeletonMarketDataSnapshotStubContract", "OFFLINE_RUNNER_SKELETON_MARKET_DATA_SNAPSHOT_STUB_UNSAFE", "REQUIRE_OFFLINE_RUNNER_SKELETON_MARKET_DATA_SNAPSHOT_STUB_FIXES", "define_offline_runner_skeleton_market_data_snapshot_stub_contract"),
    ("strategy_signal_probe_stub_contract", "OfflineRunnerSkeletonStrategySignalProbeStubContract", "OFFLINE_RUNNER_SKELETON_STRATEGY_SIGNAL_PROBE_STUB_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_STRATEGY_SIGNAL_PROBE_STUB_FIXES", "define_offline_runner_skeleton_strategy_signal_probe_stub_contract"),
    ("risk_observer_stub_contract", "OfflineRunnerSkeletonRiskObserverStubContract", "OFFLINE_RUNNER_SKELETON_RISK_OBSERVER_STUB_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_RISK_OBSERVER_STUB_FIXES", "define_offline_runner_skeleton_risk_observer_stub_contract"),
    ("profitability_observer_stub_contract", "OfflineRunnerSkeletonProfitabilityObserverStubContract", "OFFLINE_RUNNER_SKELETON_PROFITABILITY_OBSERVER_STUB_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_PROFITABILITY_OBSERVER_STUB_FIXES", "define_offline_runner_skeleton_profitability_observer_stub_contract"),
    ("consistency_observer_stub_contract", "OfflineRunnerSkeletonConsistencyObserverStubContract", "OFFLINE_RUNNER_SKELETON_CONSISTENCY_OBSERVER_STUB_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_CONSISTENCY_OBSERVER_STUB_FIXES", "define_offline_runner_skeleton_consistency_observer_stub_contract"),
    ("journal_writer_stub_contract", "OfflineRunnerSkeletonJournalWriterStubContract", "OFFLINE_RUNNER_SKELETON_JOURNAL_WRITER_STUB_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_JOURNAL_WRITER_STUB_FIXES", "define_offline_runner_skeleton_journal_writer_stub_contract"),
    ("observability_stub_contract", "OfflineRunnerSkeletonObservabilityStubContract", "OFFLINE_RUNNER_SKELETON_OBSERVABILITY_STUB_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_OBSERVABILITY_STUB_FIXES", "define_offline_runner_skeleton_observability_stub_contract"),
    ("human_approval_stub_contract", "OfflineRunnerSkeletonHumanApprovalStubContract", "OFFLINE_RUNNER_SKELETON_HUMAN_APPROVAL_STUB_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_HUMAN_APPROVAL_STUB_FIXES", "define_offline_runner_skeleton_human_approval_stub_contract"),
    ("stop_condition_stub_contract", "OfflineRunnerSkeletonStopConditionStubContract", "OFFLINE_RUNNER_SKELETON_STOP_CONDITION_STUB_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_STOP_CONDITION_STUB_FIXES", "define_offline_runner_skeleton_stop_condition_stub_contract"),
    ("success_failure_stub_contract", "OfflineRunnerSkeletonSuccessFailureStubContract", "OFFLINE_RUNNER_SKELETON_SUCCESS_FAILURE_STUB_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_SUCCESS_FAILURE_STUB_FIXES", "define_offline_runner_skeleton_success_failure_stub_contract"),
    ("audit_stub_contract", "OfflineRunnerSkeletonAuditStubContract", "OFFLINE_RUNNER_SKELETON_AUDIT_STUB_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_AUDIT_STUB_FIXES", "define_offline_runner_skeleton_audit_stub_contract"),
    ("go_no_go_stub_contract", "OfflineRunnerSkeletonGoNoGoStubContract", "OFFLINE_RUNNER_SKELETON_GO_NO_GO_STUB_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_GO_NO_GO_STUB_FIXES", "define_offline_runner_skeleton_go_no_go_stub_contract"),
    ("abort_stub_contract", "OfflineRunnerSkeletonAbortStubContract", "OFFLINE_RUNNER_SKELETON_ABORT_STUB_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_ABORT_STUB_FIXES", "define_offline_runner_skeleton_abort_stub_contract"),
    ("no_real_broker_guard", "OfflineRunnerSkeletonNoRealBrokerGuard", "OFFLINE_RUNNER_SKELETON_REAL_BROKER_GUARD_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_NO_REAL_BROKER_GUARD_FIXES", "define_offline_runner_skeleton_no_real_broker_guard"),
    ("no_secret_read_guard", "OfflineRunnerSkeletonNoSecretReadGuard", "OFFLINE_RUNNER_SKELETON_SECRET_READ_GUARD_UNSAFE", "REQUIRE_OFFLINE_RUNNER_SKELETON_NO_SECRET_READ_GUARD_FIXES", "define_offline_runner_skeleton_no_secret_read_guard"),
    ("network_block_guard", "OfflineRunnerSkeletonNetworkBlockGuard", "OFFLINE_RUNNER_SKELETON_NETWORK_BLOCK_GUARD_UNSAFE", "REQUIRE_OFFLINE_RUNNER_SKELETON_NETWORK_BLOCK_GUARD_FIXES", "define_offline_runner_skeleton_network_block_guard"),
    ("http_websocket_socket_block_guard", "OfflineRunnerSkeletonNetworkBlockGuard", "OFFLINE_RUNNER_SKELETON_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_UNSAFE", "REQUIRE_OFFLINE_RUNNER_SKELETON_NETWORK_BLOCK_GUARD_FIXES", "define_offline_runner_skeleton_http_websocket_socket_block_guard"),
    ("order_blocking_guard", "OfflineRunnerSkeletonOrderBlockingGuard", "OFFLINE_RUNNER_SKELETON_ORDER_BLOCKING_GUARD_UNSAFE", "REQUIRE_OFFLINE_RUNNER_SKELETON_ORDER_BLOCKING_GUARD_FIXES", "define_offline_runner_skeleton_order_blocking_guard"),
    ("position_mutation_blocking_guard", "OfflineRunnerSkeletonPositionMutationBlockingGuard", "OFFLINE_RUNNER_SKELETON_POSITION_MUTATION_BLOCKING_GUARD_UNSAFE", "REQUIRE_OFFLINE_RUNNER_SKELETON_POSITION_MUTATION_BLOCKING_GUARD_FIXES", "define_offline_runner_skeleton_position_mutation_blocking_guard"),
    ("data_access_guard", "OfflineRunnerSkeletonDataAccessGuard", "OFFLINE_RUNNER_SKELETON_DATA_ACCESS_GUARD_UNSAFE", "REQUIRE_OFFLINE_RUNNER_SKELETON_DATA_ACCESS_GUARD_FIXES", "define_offline_runner_skeleton_data_access_guard"),
    ("test_strategy", "OfflineRunnerSkeletonTestStrategy", "OFFLINE_RUNNER_SKELETON_TEST_STRATEGY_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_TEST_STRATEGY_FIXES", "define_offline_runner_skeleton_test_strategy"),
    ("rollback_strategy", "OfflineRunnerSkeletonRollbackStrategy", "OFFLINE_RUNNER_SKELETON_ROLLBACK_STRATEGY_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_ROLLBACK_STRATEGY_FIXES", "define_offline_runner_skeleton_rollback_strategy"),
    ("readiness_criteria", "OfflineRunnerSkeletonReadinessCriteria", "OFFLINE_RUNNER_SKELETON_READINESS_CRITERIA_MISSING", "REQUIRE_OFFLINE_RUNNER_SKELETON_READINESS_CRITERIA_FIXES", "define_offline_runner_skeleton_readiness_criteria"),
]
_RISK_BY_KEY = {k: r for k, _c, r, _d, _f in _ITEMS}
_DECISION_BY_KEY = {k: d for k, _c, _r, d, _f in _ITEMS}
_RECOMMENDATION_BY_KEY = {k: f"FIX_{r}" for k, _c, r, _d, _f in _ITEMS}

PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPlanState = StrEnum(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPlanState",
    {
        "NOT_READY": "NOT_READY",
        "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PLAN_INPUT_INVALID": "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PLAN_INPUT_INVALID",
        "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PLAN_BLOCKED": "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PLAN_BLOCKED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PLAN_COMPLETED_WITH_WARNINGS": "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PLAN_COMPLETED_WITH_WARNINGS",
        "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PLAN_COMPLETED": "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PLAN_COMPLETED",
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE": "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE",
    },
)
PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPlanDecision = StrEnum(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPlanDecision",
    {
        "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PLAN": "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PLAN",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_FINAL_SAFETY_GATE_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_FINAL_SAFETY_GATE_FIXES",
        **{d: d for d in _DECISION_BY_KEY.values()},
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PLAN": "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PLAN",
    },
)
PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPlanRisk = StrEnum(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPlanRisk",
    {
        "OFFLINE_RUNNER_IMPLEMENTATION_FINAL_SAFETY_GATE_NOT_APPROVED": "OFFLINE_RUNNER_IMPLEMENTATION_FINAL_SAFETY_GATE_NOT_APPROVED",
        **{r: r for r in _RISK_BY_KEY.values()},
        "REAL_EXECUTION_BOUNDARY_VIOLATION": "REAL_EXECUTION_BOUNDARY_VIOLATION",
        "DATA_ACCESS_VIOLATION": "DATA_ACCESS_VIOLATION",
        "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE": "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE",
    },
)
PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPlanRecommendation = StrEnum(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPlanRecommendation",
    {
        "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE": "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE",
        "APPROVE_OFFLINE_RUNNER_IMPLEMENTATION_FINAL_SAFETY_GATE_FIRST": "APPROVE_OFFLINE_RUNNER_IMPLEMENTATION_FINAL_SAFETY_GATE_FIRST",
        **{rec: rec for rec in _RECOMMENDATION_BY_KEY.values()},
        "RESTORE_OFFLINE_BOUNDARIES": "RESTORE_OFFLINE_BOUNDARIES",
        "REMOVE_DATA_ACCESS": "REMOVE_DATA_ACCESS",
        "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE": "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE",
        "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PLAN_SUITE": "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PLAN_SUITE",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE": "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE",
    },
)

Risk = PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPlanRisk
_BASE_FIELDS = [
    ("name", str),
    ("score", int, 0),
    ("defined", bool, False),
    ("risks", tuple[Risk, ...], ()),
    ("details", tuple[str, ...], ()),
    ("offline_only", bool, False),
    ("sandbox_only", bool, False),
    ("skeleton_plan_only", bool, False),
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
    ("stop_conditions_defined", bool, False),
    ("audit_defined", bool, False),
    ("test_strategy_defined", bool, False),
    ("rollback_strategy_defined", bool, False),
    ("readiness_criteria_defined", bool, False),
]
for _k, _c, _r, _d, _f in _ITEMS:
    globals()[_c] = make_dataclass(_c, _BASE_FIELDS, frozen=True)

PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPlanScore = make_dataclass(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPlanScore",
    [("overall_score", int, 0), ("implementation_final_safety_gate_score", int, 0)]
    + [(f"{k}_score", int, 0) for k, _c, _r, _d, _f in _ITEMS],
    frozen=True,
)
_COMPAT_FIELDS = [
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
PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPlanInput = make_dataclass(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPlanInput",
    [(n, Any | None, None) for n in _COMPAT_FIELDS]
    + [("offline_runner_implementation_final_safety_gate_approved", bool | None, None)]
    + [(f"offline_runner_{k}_defined", bool, True) for k, _c, _r, _d, _f in _ITEMS]
    + [
        ("offline_mode_enforced", bool, True),
        ("sandbox_mode_enforced", bool, True),
        ("implementation_skeleton_plan_only", bool, True),
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
        ("paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_safety_gate_requested", bool, False),
        ("implementation_final_safety_gate_score", int | None, None),
    ]
    + [(f"{k}_score", int | None, None) for k, _c, _r, _d, _f in _ITEMS],
    frozen=True,
)
PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPlanResult = make_dataclass(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPlanResult",
    [
        ("state", PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPlanState),
        ("decision", PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPlanDecision),
        ("score", PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPlanScore),
        ("risks", tuple[Risk, ...], ()),
        ("recommendations", tuple[PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPlanRecommendation, ...], ()),
        ("summary", str, ""),
        ("markdown_report", str, ""),
        ("offline_only", bool, True),
        ("sandbox_only", bool, True),
        ("skeleton_plan_only", bool, True),
        ("runner_created", bool, False),
        ("runner_executed", bool, False),
        ("dry_run_executed", bool, False),
        ("next_phase", str, "PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE"),
    ]
    + [(k, globals()[c] | None, None) for k, c, _r, _d, _f in _ITEMS]
    + [("components", dict[str, Any], field(default_factory=dict))],
    frozen=True,
)
__all__ = [
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPlanInput",
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPlanResult",
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPlanState",
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPlanDecision",
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPlanRisk",
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPlanRecommendation",
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPlanScore",
] + [c for _k, c, _r, _d, _f in _ITEMS]
