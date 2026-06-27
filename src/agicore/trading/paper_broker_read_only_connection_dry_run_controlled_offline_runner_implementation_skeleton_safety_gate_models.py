"""Models for controlled offline runner implementation skeleton safety gate."""
from __future__ import annotations

from dataclasses import field, make_dataclass
from enum import StrEnum
from typing import Any

_ITEMS = [
    ("scope_boundary", "OfflineRunnerSkeletonSafetyScopeBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_SCOPE_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_SCOPE_FIXES", "validate_offline_runner_skeleton_safety_scope_boundary"),
    ("module_boundaries", "OfflineRunnerSkeletonSafetyModuleBoundaries", "OFFLINE_RUNNER_SKELETON_SAFETY_MODULE_BOUNDARIES_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_MODULE_BOUNDARY_FIXES", "validate_offline_runner_skeleton_safety_module_boundaries"),
    ("file_layout_boundary", "OfflineRunnerSkeletonSafetyFileLayoutBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_FILE_LAYOUT_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_FILE_LAYOUT_FIXES", "validate_offline_runner_skeleton_safety_file_layout_boundary"),
    ("interface_contract_boundary", "OfflineRunnerSkeletonSafetyInterfaceContractBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_INTERFACE_CONTRACT_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_INTERFACE_CONTRACT_FIXES", "validate_offline_runner_skeleton_safety_interface_contract_boundary"),
    ("runtime_stub_boundary", "OfflineRunnerSkeletonSafetyRuntimeStubBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_RUNTIME_STUB_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_RUNTIME_STUB_FIXES", "validate_offline_runner_skeleton_safety_runtime_stub_boundary"),
    ("input_adapter_stub_boundary", "OfflineRunnerSkeletonSafetyInputAdapterStubBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_INPUT_ADAPTER_STUB_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_INPUT_ADAPTER_STUB_FIXES", "validate_offline_runner_skeleton_safety_input_adapter_stub_boundary"),
    ("synthetic_market_context_stub_boundary", "OfflineRunnerSkeletonSafetySyntheticMarketContextStubBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_SYNTHETIC_MARKET_CONTEXT_STUB_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_SYNTHETIC_MARKET_CONTEXT_STUB_FIXES", "validate_offline_runner_skeleton_safety_synthetic_market_context_stub_boundary"),
    ("simulated_broker_stub_boundary", "OfflineRunnerSkeletonSafetySimulatedBrokerStubBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_SIMULATED_BROKER_STUB_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_SIMULATED_BROKER_STUB_FIXES", "validate_offline_runner_skeleton_safety_simulated_broker_stub_boundary"),
    ("account_snapshot_stub_boundary", "OfflineRunnerSkeletonSafetyAccountSnapshotStubBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_ACCOUNT_SNAPSHOT_STUB_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_ACCOUNT_SNAPSHOT_STUB_FIXES", "validate_offline_runner_skeleton_safety_account_snapshot_stub_boundary"),
    ("market_data_snapshot_stub_boundary", "OfflineRunnerSkeletonSafetyMarketDataSnapshotStubBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_MARKET_DATA_SNAPSHOT_STUB_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_MARKET_DATA_SNAPSHOT_STUB_FIXES", "validate_offline_runner_skeleton_safety_market_data_snapshot_stub_boundary"),
    ("strategy_signal_probe_stub_boundary", "OfflineRunnerSkeletonSafetyStrategySignalProbeStubBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_STRATEGY_SIGNAL_PROBE_STUB_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_STRATEGY_SIGNAL_PROBE_STUB_FIXES", "validate_offline_runner_skeleton_safety_strategy_signal_probe_stub_boundary"),
    ("risk_observer_stub_boundary", "OfflineRunnerSkeletonSafetyRiskObserverStubBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_RISK_OBSERVER_STUB_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_RISK_OBSERVER_STUB_FIXES", "validate_offline_runner_skeleton_safety_risk_observer_stub_boundary"),
    ("profitability_observer_stub_boundary", "OfflineRunnerSkeletonSafetyProfitabilityObserverStubBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_PROFITABILITY_OBSERVER_STUB_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_PROFITABILITY_OBSERVER_STUB_FIXES", "validate_offline_runner_skeleton_safety_profitability_observer_stub_boundary"),
    ("consistency_observer_stub_boundary", "OfflineRunnerSkeletonSafetyConsistencyObserverStubBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_CONSISTENCY_OBSERVER_STUB_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_CONSISTENCY_OBSERVER_STUB_FIXES", "validate_offline_runner_skeleton_safety_consistency_observer_stub_boundary"),
    ("journal_writer_stub_boundary", "OfflineRunnerSkeletonSafetyJournalWriterStubBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_JOURNAL_WRITER_STUB_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_JOURNAL_WRITER_STUB_FIXES", "validate_offline_runner_skeleton_safety_journal_writer_stub_boundary"),
    ("observability_stub_boundary", "OfflineRunnerSkeletonSafetyObservabilityStubBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_OBSERVABILITY_STUB_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_OBSERVABILITY_STUB_FIXES", "validate_offline_runner_skeleton_safety_observability_stub_boundary"),
    ("human_approval_stub_boundary", "OfflineRunnerSkeletonSafetyHumanApprovalStubBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_HUMAN_APPROVAL_STUB_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_HUMAN_APPROVAL_STUB_FIXES", "validate_offline_runner_skeleton_safety_human_approval_stub_boundary"),
    ("stop_condition_stub_boundary", "OfflineRunnerSkeletonSafetyStopConditionStubBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_STOP_CONDITION_STUB_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_STOP_CONDITION_STUB_FIXES", "validate_offline_runner_skeleton_safety_stop_condition_stub_boundary"),
    ("success_failure_stub_boundary", "OfflineRunnerSkeletonSafetySuccessFailureStubBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_SUCCESS_FAILURE_STUB_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_SUCCESS_FAILURE_STUB_FIXES", "validate_offline_runner_skeleton_safety_success_failure_stub_boundary"),
    ("audit_stub_boundary", "OfflineRunnerSkeletonSafetyAuditStubBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_AUDIT_STUB_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_AUDIT_STUB_FIXES", "validate_offline_runner_skeleton_safety_audit_stub_boundary"),
    ("go_no_go_stub_boundary", "OfflineRunnerSkeletonSafetyGoNoGoStubBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_GO_NO_GO_STUB_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_GO_NO_GO_STUB_FIXES", "validate_offline_runner_skeleton_safety_go_no_go_stub_boundary"),
    ("abort_stub_boundary", "OfflineRunnerSkeletonSafetyAbortStubBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_ABORT_STUB_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_ABORT_STUB_FIXES", "validate_offline_runner_skeleton_safety_abort_stub_boundary"),
    ("no_real_broker_boundary", "OfflineRunnerSkeletonSafetyNoRealBrokerBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_REAL_BROKER_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_NO_REAL_BROKER_FIXES", "validate_offline_runner_skeleton_safety_no_real_broker_boundary"),
    ("no_secret_read_boundary", "OfflineRunnerSkeletonSafetyNoSecretReadBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_SECRET_READ_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_NO_SECRET_READ_FIXES", "validate_offline_runner_skeleton_safety_no_secret_read_boundary"),
    ("network_block_boundary", "OfflineRunnerSkeletonSafetyNetworkBlockBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_NETWORK_BLOCK_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_NETWORK_BLOCK_FIXES", "validate_offline_runner_skeleton_safety_network_block_boundary"),
    ("http_websocket_socket_block_boundary", "OfflineRunnerSkeletonSafetyNetworkBlockBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_HTTP_WEBSOCKET_SOCKET_BLOCK_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_NETWORK_BLOCK_FIXES", "validate_offline_runner_skeleton_safety_http_websocket_socket_block_boundary"),
    ("order_blocking_boundary", "OfflineRunnerSkeletonSafetyOrderBlockingBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_ORDER_BLOCKING_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_ORDER_BLOCKING_FIXES", "validate_offline_runner_skeleton_safety_order_blocking_boundary"),
    ("position_mutation_blocking_boundary", "OfflineRunnerSkeletonSafetyPositionMutationBlockingBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_POSITION_MUTATION_BLOCKING_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_POSITION_MUTATION_BLOCKING_FIXES", "validate_offline_runner_skeleton_safety_position_mutation_blocking_boundary"),
    ("data_access_boundary", "OfflineRunnerSkeletonSafetyDataAccessBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_DATA_ACCESS_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_DATA_ACCESS_FIXES", "validate_offline_runner_skeleton_safety_data_access_boundary"),
    ("test_strategy_boundary", "OfflineRunnerSkeletonSafetyTestStrategyBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_TEST_STRATEGY_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_TEST_STRATEGY_FIXES", "validate_offline_runner_skeleton_safety_test_strategy_boundary"),
    ("rollback_strategy_boundary", "OfflineRunnerSkeletonSafetyRollbackStrategyBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_ROLLBACK_STRATEGY_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_ROLLBACK_STRATEGY_FIXES", "validate_offline_runner_skeleton_safety_rollback_strategy_boundary"),
    ("readiness_criteria_boundary", "OfflineRunnerSkeletonSafetyReadinessCriteriaBoundary", "OFFLINE_RUNNER_SKELETON_SAFETY_READINESS_CRITERIA_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_SKELETON_SAFETY_READINESS_CRITERIA_FIXES", "validate_offline_runner_skeleton_safety_readiness_criteria_boundary"),
]
_RISK_BY_KEY = {k: r for k, _c, r, _d, _f in _ITEMS}
_DECISION_BY_KEY = {k: d for k, _c, _r, d, _f in _ITEMS}
_RECOMMENDATION_BY_KEY = {k: f"FIX_{r}" for k, _c, r, _d, _f in _ITEMS}

PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateState = StrEnum(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateState",
    {
        "NOT_READY": "NOT_READY",
        "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE_INPUT_INVALID": "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE_INPUT_INVALID",
        "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE_BLOCKED": "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE_BLOCKED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE_COMPLETED_WITH_WARNINGS": "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE_COMPLETED_WITH_WARNINGS",
        "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE_COMPLETED": "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE_COMPLETED",
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION": "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION",
    },
)
PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateDecision = StrEnum(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateDecision",
    {
        "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE": "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PLAN_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PLAN_FIXES",
        **{d: d for d in _DECISION_BY_KEY.values()},
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE": "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE",
    },
)
PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateRisk = StrEnum(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateRisk",
    {
        "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PLAN_NOT_APPROVED": "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PLAN_NOT_APPROVED",
        **{r: r for r in _RISK_BY_KEY.values()},
        "REAL_EXECUTION_BOUNDARY_VIOLATION": "REAL_EXECUTION_BOUNDARY_VIOLATION",
        "DATA_ACCESS_VIOLATION": "DATA_ACCESS_VIOLATION",
        "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION": "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION",
    },
)
PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateRecommendation = StrEnum(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateRecommendation",
    {
        "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION": "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION",
        "APPROVE_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PLAN_FIRST": "APPROVE_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PLAN_FIRST",
        **{rec: rec for rec in _RECOMMENDATION_BY_KEY.values()},
        "RESTORE_OFFLINE_BOUNDARIES": "RESTORE_OFFLINE_BOUNDARIES",
        "REMOVE_DATA_ACCESS": "REMOVE_DATA_ACCESS",
        "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION": "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION",
        "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE_SUITE": "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE_SUITE",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION": "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION",
    },
)

Risk = PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateRisk
_BASE_FIELDS = [
    ("name", str),
    ("score", int, 0),
    ("safe", bool, False),
    ("risks", tuple[Risk, ...], ()),
    ("details", tuple[str, ...], ()),
    ("offline_only", bool, False),
    ("sandbox_only", bool, False),
    ("skeleton_safety_gate_only", bool, False),
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
    ("stop_conditions_safe", bool, False),
    ("audit_safe", bool, False),
    ("test_strategy_safe", bool, False),
    ("rollback_strategy_safe", bool, False),
    ("readiness_criteria_safe", bool, False),
]
for _k, _c, _r, _d, _f in _ITEMS:
    globals()[_c] = make_dataclass(_c, _BASE_FIELDS, frozen=True)

PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateScore = make_dataclass(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateScore",
    [("overall_score", int, 0), ("implementation_skeleton_plan_score", int, 0)]
    + [(f"{k}_score", int, 0) for k, _c, _r, _d, _f in _ITEMS],
    frozen=True,
)
_COMPAT_FIELDS = [
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
PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateInput = make_dataclass(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateInput",
    [(n, Any | None, None) for n in _COMPAT_FIELDS]
    + [("offline_runner_implementation_skeleton_plan_approved", bool | None, None)]
    + [(f"offline_runner_{k}_safe", bool, True) for k, _c, _r, _d, _f in _ITEMS]
    + [
        ("offline_mode_enforced", bool, True),
        ("sandbox_mode_enforced", bool, True),
        ("skeleton_safety_gate_only", bool, True),
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
        ("paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_preparation_requested", bool, False),
        ("implementation_skeleton_plan_score", int | None, None),
    ]
    + [(f"{k}_score", int | None, None) for k, _c, _r, _d, _f in _ITEMS],
    frozen=True,
)
PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateResult = make_dataclass(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateResult",
    [
        ("state", PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateState),
        ("decision", PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateDecision),
        ("score", PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateScore),
        ("risks", tuple[Risk, ...], ()),
        ("recommendations", tuple[PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateRecommendation, ...], ()),
        ("summary", str, ""),
        ("markdown_report", str, ""),
        ("offline_only", bool, True),
        ("sandbox_only", bool, True),
        ("skeleton_safety_gate_only", bool, True),
        ("runner_created", bool, False),
        ("runner_executed", bool, False),
        ("dry_run_executed", bool, False),
        ("next_phase", str, "PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION"),
    ]
    + [(k, globals()[c] | None, None) for k, c, _r, _d, _f in _ITEMS]
    + [("boundaries", dict[str, Any], field(default_factory=dict))],
    frozen=True,
)
__all__ = [
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateInput",
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateResult",
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateState",
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateDecision",
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateRisk",
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateRecommendation",
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateScore",
] + [c for _k, c, _r, _d, _f in _ITEMS]
