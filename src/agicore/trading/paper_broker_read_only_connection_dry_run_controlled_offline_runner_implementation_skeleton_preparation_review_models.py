"""Models for controlled offline runner implementation skeleton preparation review."""
from __future__ import annotations

from dataclasses import field, make_dataclass
from enum import StrEnum
from typing import Any

_ITEMS = [('scope_preparation_contract', 'OfflineRunnerSkeletonScopePreparationReviewFinding', 'OFFLINE_RUNNER_SKELETON_SCOPE_PREPARATION_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_SCOPE_PREPARATION_REVIEW_FIXES', 'review_offline_runner_skeleton_scope_preparation_contract'), ('module_boundaries_preparation_contract', 'OfflineRunnerSkeletonModuleBoundariesPreparationReviewFinding', 'OFFLINE_RUNNER_SKELETON_MODULE_BOUNDARIES_PREPARATION_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_MODULE_BOUNDARIES_PREPARATION_REVIEW_FIXES', 'review_offline_runner_skeleton_module_boundaries_preparation_contract'), ('file_layout_preparation_contract', 'OfflineRunnerSkeletonFileLayoutPreparationReviewFinding', 'OFFLINE_RUNNER_SKELETON_FILE_LAYOUT_PREPARATION_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_FILE_LAYOUT_PREPARATION_REVIEW_FIXES', 'review_offline_runner_skeleton_file_layout_preparation_contract'), ('interface_preparation_contract', 'OfflineRunnerSkeletonInterfacePreparationReviewFinding', 'OFFLINE_RUNNER_SKELETON_INTERFACE_PREPARATION_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_INTERFACE_PREPARATION_REVIEW_FIXES', 'review_offline_runner_skeleton_interface_preparation_contract'), ('runtime_stub_preparation_contract', 'OfflineRunnerSkeletonRuntimeStubPreparationReviewFinding', 'OFFLINE_RUNNER_SKELETON_RUNTIME_STUB_PREPARATION_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_RUNTIME_STUB_PREPARATION_REVIEW_FIXES', 'review_offline_runner_skeleton_runtime_stub_preparation_contract'), ('input_adapter_stub_preparation_contract', 'OfflineRunnerSkeletonInputAdapterStubPreparationReviewFinding', 'OFFLINE_RUNNER_SKELETON_INPUT_ADAPTER_STUB_PREPARATION_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_INPUT_ADAPTER_STUB_PREPARATION_REVIEW_FIXES', 'review_offline_runner_skeleton_input_adapter_stub_preparation_contract'), ('synthetic_market_context_stub_preparation_contract', 'OfflineRunnerSkeletonSyntheticMarketContextStubPreparationReviewFinding', 'OFFLINE_RUNNER_SKELETON_SYNTHETIC_MARKET_CONTEXT_STUB_PREPARATION_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_SYNTHETIC_MARKET_CONTEXT_STUB_PREPARATION_REVIEW_FIXES', 'review_offline_runner_skeleton_synthetic_market_context_stub_preparation_contract'), ('simulated_broker_stub_preparation_contract', 'OfflineRunnerSkeletonSimulatedBrokerStubPreparationReviewFinding', 'OFFLINE_RUNNER_SKELETON_SIMULATED_BROKER_STUB_PREPARATION_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_SIMULATED_BROKER_STUB_PREPARATION_REVIEW_FIXES', 'review_offline_runner_skeleton_simulated_broker_stub_preparation_contract'), ('account_snapshot_stub_preparation_contract', 'OfflineRunnerSkeletonAccountSnapshotStubPreparationReviewFinding', 'OFFLINE_RUNNER_SKELETON_ACCOUNT_SNAPSHOT_STUB_PREPARATION_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_ACCOUNT_SNAPSHOT_STUB_PREPARATION_REVIEW_FIXES', 'review_offline_runner_skeleton_account_snapshot_stub_preparation_contract'), ('market_data_snapshot_stub_preparation_contract', 'OfflineRunnerSkeletonMarketDataSnapshotStubPreparationReviewFinding', 'OFFLINE_RUNNER_SKELETON_MARKET_DATA_SNAPSHOT_STUB_PREPARATION_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_MARKET_DATA_SNAPSHOT_STUB_PREPARATION_REVIEW_FIXES', 'review_offline_runner_skeleton_market_data_snapshot_stub_preparation_contract'), ('strategy_signal_probe_stub_preparation_contract', 'OfflineRunnerSkeletonStrategySignalProbeStubPreparationReviewFinding', 'OFFLINE_RUNNER_SKELETON_STRATEGY_SIGNAL_PROBE_STUB_PREPARATION_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_STRATEGY_SIGNAL_PROBE_STUB_PREPARATION_REVIEW_FIXES', 'review_offline_runner_skeleton_strategy_signal_probe_stub_preparation_contract'), ('risk_observer_stub_preparation_contract', 'OfflineRunnerSkeletonRiskObserverStubPreparationReviewFinding', 'OFFLINE_RUNNER_SKELETON_RISK_OBSERVER_STUB_PREPARATION_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_RISK_OBSERVER_STUB_PREPARATION_REVIEW_FIXES', 'review_offline_runner_skeleton_risk_observer_stub_preparation_contract'), ('profitability_observer_stub_preparation_contract', 'OfflineRunnerSkeletonProfitabilityObserverStubPreparationReviewFinding', 'OFFLINE_RUNNER_SKELETON_PROFITABILITY_OBSERVER_STUB_PREPARATION_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_PROFITABILITY_OBSERVER_STUB_PREPARATION_REVIEW_FIXES', 'review_offline_runner_skeleton_profitability_observer_stub_preparation_contract'), ('consistency_observer_stub_preparation_contract', 'OfflineRunnerSkeletonConsistencyObserverStubPreparationReviewFinding', 'OFFLINE_RUNNER_SKELETON_CONSISTENCY_OBSERVER_STUB_PREPARATION_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_CONSISTENCY_OBSERVER_STUB_PREPARATION_REVIEW_FIXES', 'review_offline_runner_skeleton_consistency_observer_stub_preparation_contract'), ('journal_writer_stub_preparation_contract', 'OfflineRunnerSkeletonJournalWriterStubPreparationReviewFinding', 'OFFLINE_RUNNER_SKELETON_JOURNAL_WRITER_STUB_PREPARATION_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_JOURNAL_WRITER_STUB_PREPARATION_REVIEW_FIXES', 'review_offline_runner_skeleton_journal_writer_stub_preparation_contract'), ('observability_stub_preparation_contract', 'OfflineRunnerSkeletonObservabilityStubPreparationReviewFinding', 'OFFLINE_RUNNER_SKELETON_OBSERVABILITY_STUB_PREPARATION_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_OBSERVABILITY_STUB_PREPARATION_REVIEW_FIXES', 'review_offline_runner_skeleton_observability_stub_preparation_contract'), ('human_approval_stub_preparation_contract', 'OfflineRunnerSkeletonHumanApprovalStubPreparationReviewFinding', 'OFFLINE_RUNNER_SKELETON_HUMAN_APPROVAL_STUB_PREPARATION_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_HUMAN_APPROVAL_STUB_PREPARATION_REVIEW_FIXES', 'review_offline_runner_skeleton_human_approval_stub_preparation_contract'), ('stop_condition_stub_preparation_contract', 'OfflineRunnerSkeletonStopConditionStubPreparationReviewFinding', 'OFFLINE_RUNNER_SKELETON_STOP_CONDITIONS_STUB_PREPARATION_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_STOP_CONDITION_STUB_PREPARATION_REVIEW_FIXES', 'review_offline_runner_skeleton_stop_condition_stub_preparation_contract'), ('success_failure_stub_preparation_contract', 'OfflineRunnerSkeletonSuccessFailureStubPreparationReviewFinding', 'OFFLINE_RUNNER_SKELETON_SUCCESS_FAILURE_STUB_PREPARATION_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_SUCCESS_FAILURE_STUB_PREPARATION_REVIEW_FIXES', 'review_offline_runner_skeleton_success_failure_stub_preparation_contract'), ('audit_stub_preparation_contract', 'OfflineRunnerSkeletonAuditStubPreparationReviewFinding', 'OFFLINE_RUNNER_SKELETON_AUDIT_STUB_PREPARATION_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_AUDIT_STUB_PREPARATION_REVIEW_FIXES', 'review_offline_runner_skeleton_audit_stub_preparation_contract'), ('go_no_go_stub_preparation_contract', 'OfflineRunnerSkeletonGoNoGoStubPreparationReviewFinding', 'OFFLINE_RUNNER_SKELETON_GO_NO_GO_STUB_PREPARATION_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_GO_NO_GO_STUB_PREPARATION_REVIEW_FIXES', 'review_offline_runner_skeleton_go_no_go_stub_preparation_contract'), ('abort_stub_preparation_contract', 'OfflineRunnerSkeletonAbortStubPreparationReviewFinding', 'OFFLINE_RUNNER_SKELETON_ABORT_STUB_PREPARATION_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_ABORT_STUB_PREPARATION_REVIEW_FIXES', 'review_offline_runner_skeleton_abort_stub_preparation_contract'), ('no_real_broker_guard', 'OfflineRunnerSkeletonNoRealBrokerGuardReviewFinding', 'OFFLINE_RUNNER_SKELETON_REAL_BROKER_GUARD_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_NO_REAL_BROKER_GUARD_REVIEW_FIXES', 'review_offline_runner_skeleton_no_real_broker_guard'), ('no_secret_read_guard', 'OfflineRunnerSkeletonNoSecretReadGuardReviewFinding', 'OFFLINE_RUNNER_SKELETON_SECRET_READ_GUARD_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_NO_SECRET_READ_GUARD_REVIEW_FIXES', 'review_offline_runner_skeleton_no_secret_read_guard'), ('network_block_guard', 'OfflineRunnerSkeletonNetworkBlockGuardReviewFinding', 'OFFLINE_RUNNER_SKELETON_NETWORK_BLOCK_GUARD_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_NETWORK_BLOCK_GUARD_REVIEW_FIXES', 'review_offline_runner_skeleton_network_block_guard'), ('http_websocket_socket_block_guard', 'OfflineRunnerSkeletonNetworkBlockGuardReviewFinding', 'OFFLINE_RUNNER_SKELETON_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_NETWORK_BLOCK_GUARD_REVIEW_FIXES', 'review_offline_runner_skeleton_http_websocket_socket_block_guard'), ('order_blocking_guard', 'OfflineRunnerSkeletonOrderBlockingGuardReviewFinding', 'OFFLINE_RUNNER_SKELETON_ORDER_BLOCKING_GUARD_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_ORDER_BLOCKING_GUARD_REVIEW_FIXES', 'review_offline_runner_skeleton_order_blocking_guard'), ('position_mutation_blocking_guard', 'OfflineRunnerSkeletonPositionMutationBlockingGuardReviewFinding', 'OFFLINE_RUNNER_SKELETON_POSITION_MUTATION_BLOCKING_GUARD_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_POSITION_MUTATION_BLOCKING_GUARD_REVIEW_FIXES', 'review_offline_runner_skeleton_position_mutation_blocking_guard'), ('data_access_guard', 'OfflineRunnerSkeletonDataAccessGuardReviewFinding', 'OFFLINE_RUNNER_SKELETON_DATA_ACCESS_GUARD_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_DATA_ACCESS_GUARD_REVIEW_FIXES', 'review_offline_runner_skeleton_data_access_guard'), ('test_strategy_preparation_contract', 'OfflineRunnerSkeletonTestStrategyPreparationReviewFinding', 'OFFLINE_RUNNER_SKELETON_TEST_STRATEGY_PREPARATION_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_TEST_STRATEGY_PREPARATION_REVIEW_FIXES', 'review_offline_runner_skeleton_test_strategy_preparation_contract'), ('rollback_strategy_preparation_contract', 'OfflineRunnerSkeletonRollbackStrategyPreparationReviewFinding', 'OFFLINE_RUNNER_SKELETON_ROLLBACK_STRATEGY_PREPARATION_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_ROLLBACK_STRATEGY_PREPARATION_REVIEW_FIXES', 'review_offline_runner_skeleton_rollback_strategy_preparation_contract'), ('readiness_criteria_preparation_contract', 'OfflineRunnerSkeletonReadinessCriteriaPreparationReviewFinding', 'OFFLINE_RUNNER_SKELETON_READINESS_CRITERIA_PREPARATION_REVIEW_FAILED', 'REQUIRE_OFFLINE_RUNNER_SKELETON_READINESS_CRITERIA_PREPARATION_REVIEW_FIXES', 'review_offline_runner_skeleton_readiness_criteria_preparation_contract')]
_RISK_BY_KEY = {k: r for k, _c, r, _d, _f in _ITEMS}
_DECISION_BY_KEY = {k: d for k, _c, _r, d, _f in _ITEMS}
_RECOMMENDATION_BY_KEY = {k: f"FIX_{r}" for k, _c, r, _d, _f in _ITEMS}

PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationReviewState = StrEnum(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationReviewState",
    {
        "NOT_READY": "NOT_READY",
        "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_REVIEW_INPUT_INVALID": "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_REVIEW_INPUT_INVALID",
        "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_REVIEW_BLOCKED": "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_REVIEW_BLOCKED",
        "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_REVIEW_COMPLETED_WITH_WARNINGS": "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_REVIEW_COMPLETED_WITH_WARNINGS",
        "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_REVIEW_COMPLETED": "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_REVIEW_COMPLETED",
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_FINAL_PLAN": "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_FINAL_PLAN",
    },
)
PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationReviewDecision = StrEnum(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationReviewDecision",
    {
        "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_REVIEW": "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_REVIEW",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_FIXES",
        **{d: d for d in _DECISION_BY_KEY.values()},
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_REVIEW": "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_REVIEW",
    },
)
PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationReviewRisk = StrEnum(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationReviewRisk",
    {
        "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_NOT_APPROVED": "OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_NOT_APPROVED",
        **{r: r for r in _RISK_BY_KEY.values()},
        "REAL_EXECUTION_BOUNDARY_VIOLATION": "REAL_EXECUTION_BOUNDARY_VIOLATION",
        "DATA_ACCESS_VIOLATION": "DATA_ACCESS_VIOLATION",
        "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_FINAL_PLAN": "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_FINAL_PLAN",
    },
)
PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationReviewRecommendation = StrEnum(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationReviewRecommendation",
    {
        "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_FINAL_PLAN": "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_FINAL_PLAN",
        "APPROVE_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_FIRST": "APPROVE_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_FIRST",
        **{rec: rec for rec in _RECOMMENDATION_BY_KEY.values()},
        "RESTORE_OFFLINE_BOUNDARIES": "RESTORE_OFFLINE_BOUNDARIES",
        "REMOVE_DATA_ACCESS": "REMOVE_DATA_ACCESS",
        "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_FINAL_PLAN": "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_FINAL_PLAN",
        "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_REVIEW_SUITE": "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION_REVIEW_SUITE",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_FINAL_PLAN": "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_FINAL_PLAN",
    },
)

Risk = PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationReviewRisk
_BASE_FIELDS = [
    ("name", str),
    ("score", int, 0),
    ("passed", bool, False),
    ("risks", tuple[Risk, ...], ()),
    ("details", tuple[str, ...], ()),
    ("offline_only", bool, False),
    ("sandbox_only", bool, False),
    ("skeleton_preparation_review_only", bool, False),
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
    ("stop_conditions_passed", bool, False),
    ("audit_passed", bool, False),
    ("test_strategy_passed", bool, False),
    ("rollback_strategy_passed", bool, False),
    ("readiness_criteria_passed", bool, False),
]
for _k, _c, _r, _d, _f in _ITEMS:
    globals()[_c] = make_dataclass(_c, _BASE_FIELDS, frozen=True)

PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationReviewScore = make_dataclass(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationReviewScore",
    [("overall_score", int, 0), ("implementation_skeleton_preparation_score", int, 0)]
    + [(f"{k}_score", int, 0) for k, _c, _r, _d, _f in _ITEMS],
    frozen=True,
)
_COMPAT_FIELDS = [
    "paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_preparation",
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
PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationReviewInput = make_dataclass(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationReviewInput",
    [(n, Any | None, None) for n in _COMPAT_FIELDS]
    + [("offline_runner_implementation_skeleton_preparation_approved", bool | None, None)]
    + [(f"offline_runner_{k}_passed", bool, True) for k, _c, _r, _d, _f in _ITEMS]
    + [
        ("offline_mode_enforced", bool, True),
        ("sandbox_mode_enforced", bool, True),
        ("skeleton_preparation_review_only", bool, True),
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
        ("paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_final_plan_requested", bool, False),
        ("implementation_skeleton_preparation_score", int | None, None),
    ]
    + [(f"{k}_score", int | None, None) for k, _c, _r, _d, _f in _ITEMS],
    frozen=True,
)
PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationReviewResult = make_dataclass(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationReviewResult",
    [
        ("state", PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationReviewState),
        ("decision", PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationReviewDecision),
        ("score", PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationReviewScore),
        ("risks", tuple[Risk, ...], ()),
        ("recommendations", tuple[PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationReviewRecommendation, ...], ()),
        ("summary", str, ""),
        ("markdown_report", str, ""),
        ("offline_only", bool, True),
        ("sandbox_only", bool, True),
        ("skeleton_preparation_review_only", bool, True),
        ("runner_created", bool, False),
        ("runner_executed", bool, False),
        ("dry_run_executed", bool, False),
        ("next_phase", str, "PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_FINAL_PLAN"),
    ]
    + [(k, globals()[c] | None, None) for k, c, _r, _d, _f in _ITEMS]
    + [("findings", dict[str, Any], field(default_factory=dict))],
    frozen=True,
)
__all__ = [
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationReviewInput",
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationReviewResult",
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationReviewState",
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationReviewDecision",
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationReviewRisk",
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationReviewRecommendation",
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPreparationReviewScore",
] + [c for _k, c, _r, _d, _f in _ITEMS]
