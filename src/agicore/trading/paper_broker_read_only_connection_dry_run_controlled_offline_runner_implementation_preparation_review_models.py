"""Models for controlled offline runner implementation preparation review."""

from __future__ import annotations

from dataclasses import field, make_dataclass
from enum import StrEnum
from typing import Any


_ITEMS = (
    ("implementation_scope_contract", "OfflineRunnerImplementationScopePreparationReviewFinding"),
    ("implementation_architecture_contract", "OfflineRunnerImplementationArchitecturePreparationReviewFinding"),
    ("implementation_sequence_contract", "OfflineRunnerImplementationSequencePreparationReviewFinding"),
    ("runtime_contract", "OfflineRunnerRuntimePreparationReviewFinding"),
    ("input_adapter_contract", "OfflineRunnerInputAdapterPreparationReviewFinding"),
    ("synthetic_market_context_adapter_contract", "OfflineRunnerSyntheticMarketContextAdapterPreparationReviewFinding"),
    ("simulated_broker_adapter_contract", "OfflineRunnerSimulatedBrokerAdapterPreparationReviewFinding"),
    ("account_snapshot_adapter_contract", "OfflineRunnerAccountSnapshotAdapterPreparationReviewFinding"),
    ("market_data_snapshot_adapter_contract", "OfflineRunnerMarketDataSnapshotAdapterPreparationReviewFinding"),
    ("strategy_signal_probe_contract", "OfflineRunnerStrategySignalProbePreparationReviewFinding"),
    ("risk_observer_contract", "OfflineRunnerRiskObserverPreparationReviewFinding"),
    ("profitability_observer_contract", "OfflineRunnerProfitabilityObserverPreparationReviewFinding"),
    ("consistency_observer_contract", "OfflineRunnerConsistencyObserverPreparationReviewFinding"),
    ("journal_writer_contract", "OfflineRunnerJournalWriterPreparationReviewFinding"),
    ("observability_contract", "OfflineRunnerObservabilityPreparationReviewFinding"),
    ("human_approval_contract", "OfflineRunnerHumanApprovalPreparationReviewFinding"),
    ("stop_condition_contract", "OfflineRunnerStopConditionPreparationReviewFinding"),
    ("success_criteria_contract", "OfflineRunnerSuccessCriteriaPreparationReviewFinding"),
    ("failure_criteria_contract", "OfflineRunnerFailureCriteriaPreparationReviewFinding"),
    ("audit_contract", "OfflineRunnerAuditPreparationReviewFinding"),
    ("go_no_go_contract", "OfflineRunnerGoNoGoPreparationReviewFinding"),
    ("abort_contract", "OfflineRunnerAbortPreparationReviewFinding"),
    ("no_real_broker_guard", "OfflineRunnerNoRealBrokerGuardReviewFinding"),
    ("no_secret_read_guard", "OfflineRunnerNoSecretReadGuardReviewFinding"),
    ("network_block_guard", "OfflineRunnerNetworkBlockGuardReviewFinding"),
    ("http_websocket_socket_block_guard", "OfflineRunnerNetworkBlockGuardReviewFinding"),
    ("order_blocking_guard", "OfflineRunnerOrderBlockingGuardReviewFinding"),
    ("position_mutation_blocking_guard", "OfflineRunnerPositionMutationBlockingGuardReviewFinding"),
    ("data_access_guard", "OfflineRunnerDataAccessGuardReviewFinding"),
    ("test_strategy_contract", "OfflineRunnerTestStrategyPreparationReviewFinding"),
    ("rollback_strategy_contract", "OfflineRunnerRollbackStrategyPreparationReviewFinding"),
)

_RISK_BY_KEY = {
    "implementation_scope_contract": "OFFLINE_RUNNER_IMPLEMENTATION_SCOPE_PREPARATION_REVIEW_FAILED",
    "implementation_architecture_contract": "OFFLINE_RUNNER_IMPLEMENTATION_ARCHITECTURE_PREPARATION_REVIEW_FAILED",
    "implementation_sequence_contract": "OFFLINE_RUNNER_IMPLEMENTATION_SEQUENCE_PREPARATION_REVIEW_FAILED",
    "runtime_contract": "OFFLINE_RUNNER_RUNTIME_PREPARATION_REVIEW_FAILED",
    "input_adapter_contract": "OFFLINE_RUNNER_INPUT_ADAPTER_PREPARATION_REVIEW_FAILED",
    "synthetic_market_context_adapter_contract": "OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_ADAPTER_PREPARATION_REVIEW_FAILED",
    "simulated_broker_adapter_contract": "OFFLINE_RUNNER_SIMULATED_BROKER_ADAPTER_PREPARATION_REVIEW_FAILED",
    "account_snapshot_adapter_contract": "OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_ADAPTER_PREPARATION_REVIEW_FAILED",
    "market_data_snapshot_adapter_contract": "OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_ADAPTER_PREPARATION_REVIEW_FAILED",
    "strategy_signal_probe_contract": "OFFLINE_RUNNER_STRATEGY_SIGNAL_PROBE_PREPARATION_REVIEW_FAILED",
    "risk_observer_contract": "OFFLINE_RUNNER_RISK_OBSERVER_PREPARATION_REVIEW_FAILED",
    "profitability_observer_contract": "OFFLINE_RUNNER_PROFITABILITY_OBSERVER_PREPARATION_REVIEW_FAILED",
    "consistency_observer_contract": "OFFLINE_RUNNER_CONSISTENCY_OBSERVER_PREPARATION_REVIEW_FAILED",
    "journal_writer_contract": "OFFLINE_RUNNER_JOURNAL_WRITER_PREPARATION_REVIEW_FAILED",
    "observability_contract": "OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_REVIEW_FAILED",
    "human_approval_contract": "OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION_REVIEW_FAILED",
    "stop_condition_contract": "OFFLINE_RUNNER_STOP_CONDITIONS_PREPARATION_REVIEW_FAILED",
    "success_criteria_contract": "OFFLINE_RUNNER_SUCCESS_CRITERIA_PREPARATION_REVIEW_FAILED",
    "failure_criteria_contract": "OFFLINE_RUNNER_FAILURE_CRITERIA_PREPARATION_REVIEW_FAILED",
    "audit_contract": "OFFLINE_RUNNER_AUDIT_PREPARATION_REVIEW_FAILED",
    "go_no_go_contract": "OFFLINE_RUNNER_GO_NO_GO_PREPARATION_REVIEW_FAILED",
    "abort_contract": "OFFLINE_RUNNER_ABORT_PREPARATION_REVIEW_FAILED",
    "no_real_broker_guard": "OFFLINE_RUNNER_REAL_BROKER_GUARD_REVIEW_FAILED",
    "no_secret_read_guard": "OFFLINE_RUNNER_SECRET_READ_GUARD_REVIEW_FAILED",
    "network_block_guard": "OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_REVIEW_FAILED",
    "http_websocket_socket_block_guard": "OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW_FAILED",
    "order_blocking_guard": "OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_REVIEW_FAILED",
    "position_mutation_blocking_guard": "OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_REVIEW_FAILED",
    "data_access_guard": "OFFLINE_RUNNER_DATA_ACCESS_GUARD_REVIEW_FAILED",
    "test_strategy_contract": "OFFLINE_RUNNER_TEST_STRATEGY_PREPARATION_REVIEW_FAILED",
    "rollback_strategy_contract": "OFFLINE_RUNNER_ROLLBACK_STRATEGY_PREPARATION_REVIEW_FAILED",
}

PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewState = StrEnum(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewState",
    {
        "NOT_READY": "NOT_READY",
        "OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW_INPUT_INVALID": "OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW_INPUT_INVALID",
        "OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW_BLOCKED": "OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW_BLOCKED",
        "OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW_COMPLETED_WITH_WARNINGS": "OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW_COMPLETED_WITH_WARNINGS",
        "OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW_COMPLETED": "OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW_COMPLETED",
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_FINAL_PLAN": "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_FINAL_PLAN",
    },
)

_DECISIONS = {
    "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW": "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW",
    "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_FIXES",
    "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW": "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW",
}
for _key in _RISK_BY_KEY:
    _name = "REQUIRE_OFFLINE_RUNNER_" + _key.upper().replace("_CONTRACT", "").replace("_GUARD", "_GUARD").replace("IMPLEMENTATION_", "IMPLEMENTATION_") + "_PREPARATION_REVIEW_FIXES"
    _name = _name.replace("SUCCESS_CRITERIA_PREPARATION_REVIEW_FIXES", "SUCCESS_FAILURE_PREPARATION_REVIEW_FIXES")
    _name = _name.replace("FAILURE_CRITERIA_PREPARATION_REVIEW_FIXES", "SUCCESS_FAILURE_PREPARATION_REVIEW_FIXES")
    _DECISIONS[_name] = _name
_DECISIONS.update(
    {
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SCOPE_PREPARATION_REVIEW_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SCOPE_PREPARATION_REVIEW_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_ARCHITECTURE_PREPARATION_REVIEW_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_ARCHITECTURE_PREPARATION_REVIEW_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SEQUENCE_PREPARATION_REVIEW_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SEQUENCE_PREPARATION_REVIEW_FIXES",
        "REQUIRE_OFFLINE_RUNNER_RUNTIME_PREPARATION_REVIEW_FIXES": "REQUIRE_OFFLINE_RUNNER_RUNTIME_PREPARATION_REVIEW_FIXES",
        "REQUIRE_OFFLINE_RUNNER_INPUT_ADAPTER_PREPARATION_REVIEW_FIXES": "REQUIRE_OFFLINE_RUNNER_INPUT_ADAPTER_PREPARATION_REVIEW_FIXES",
        "REQUIRE_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_ADAPTER_PREPARATION_REVIEW_FIXES": "REQUIRE_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_ADAPTER_PREPARATION_REVIEW_FIXES",
        "REQUIRE_OFFLINE_RUNNER_SIMULATED_BROKER_ADAPTER_PREPARATION_REVIEW_FIXES": "REQUIRE_OFFLINE_RUNNER_SIMULATED_BROKER_ADAPTER_PREPARATION_REVIEW_FIXES",
        "REQUIRE_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_ADAPTER_PREPARATION_REVIEW_FIXES": "REQUIRE_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_ADAPTER_PREPARATION_REVIEW_FIXES",
        "REQUIRE_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_ADAPTER_PREPARATION_REVIEW_FIXES": "REQUIRE_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_ADAPTER_PREPARATION_REVIEW_FIXES",
        "REQUIRE_OFFLINE_RUNNER_STRATEGY_SIGNAL_PROBE_PREPARATION_REVIEW_FIXES": "REQUIRE_OFFLINE_RUNNER_STRATEGY_SIGNAL_PROBE_PREPARATION_REVIEW_FIXES",
        "REQUIRE_OFFLINE_RUNNER_RISK_OBSERVER_PREPARATION_REVIEW_FIXES": "REQUIRE_OFFLINE_RUNNER_RISK_OBSERVER_PREPARATION_REVIEW_FIXES",
        "REQUIRE_OFFLINE_RUNNER_PROFITABILITY_OBSERVER_PREPARATION_REVIEW_FIXES": "REQUIRE_OFFLINE_RUNNER_PROFITABILITY_OBSERVER_PREPARATION_REVIEW_FIXES",
        "REQUIRE_OFFLINE_RUNNER_CONSISTENCY_OBSERVER_PREPARATION_REVIEW_FIXES": "REQUIRE_OFFLINE_RUNNER_CONSISTENCY_OBSERVER_PREPARATION_REVIEW_FIXES",
        "REQUIRE_OFFLINE_RUNNER_JOURNAL_WRITER_PREPARATION_REVIEW_FIXES": "REQUIRE_OFFLINE_RUNNER_JOURNAL_WRITER_PREPARATION_REVIEW_FIXES",
        "REQUIRE_OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_REVIEW_FIXES": "REQUIRE_OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_REVIEW_FIXES",
        "REQUIRE_OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION_REVIEW_FIXES": "REQUIRE_OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION_REVIEW_FIXES",
        "REQUIRE_OFFLINE_RUNNER_STOP_CONDITION_PREPARATION_REVIEW_FIXES": "REQUIRE_OFFLINE_RUNNER_STOP_CONDITION_PREPARATION_REVIEW_FIXES",
        "REQUIRE_OFFLINE_RUNNER_SUCCESS_FAILURE_PREPARATION_REVIEW_FIXES": "REQUIRE_OFFLINE_RUNNER_SUCCESS_FAILURE_PREPARATION_REVIEW_FIXES",
        "REQUIRE_OFFLINE_RUNNER_AUDIT_PREPARATION_REVIEW_FIXES": "REQUIRE_OFFLINE_RUNNER_AUDIT_PREPARATION_REVIEW_FIXES",
        "REQUIRE_OFFLINE_RUNNER_GO_NO_GO_PREPARATION_REVIEW_FIXES": "REQUIRE_OFFLINE_RUNNER_GO_NO_GO_PREPARATION_REVIEW_FIXES",
        "REQUIRE_OFFLINE_RUNNER_ABORT_PREPARATION_REVIEW_FIXES": "REQUIRE_OFFLINE_RUNNER_ABORT_PREPARATION_REVIEW_FIXES",
        "REQUIRE_OFFLINE_RUNNER_NO_REAL_BROKER_GUARD_REVIEW_FIXES": "REQUIRE_OFFLINE_RUNNER_NO_REAL_BROKER_GUARD_REVIEW_FIXES",
        "REQUIRE_OFFLINE_RUNNER_NO_SECRET_READ_GUARD_REVIEW_FIXES": "REQUIRE_OFFLINE_RUNNER_NO_SECRET_READ_GUARD_REVIEW_FIXES",
        "REQUIRE_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_REVIEW_FIXES": "REQUIRE_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_REVIEW_FIXES",
        "REQUIRE_OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_REVIEW_FIXES": "REQUIRE_OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_REVIEW_FIXES",
        "REQUIRE_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_REVIEW_FIXES": "REQUIRE_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_REVIEW_FIXES",
        "REQUIRE_OFFLINE_RUNNER_DATA_ACCESS_GUARD_REVIEW_FIXES": "REQUIRE_OFFLINE_RUNNER_DATA_ACCESS_GUARD_REVIEW_FIXES",
        "REQUIRE_OFFLINE_RUNNER_TEST_STRATEGY_PREPARATION_REVIEW_FIXES": "REQUIRE_OFFLINE_RUNNER_TEST_STRATEGY_PREPARATION_REVIEW_FIXES",
        "REQUIRE_OFFLINE_RUNNER_ROLLBACK_STRATEGY_PREPARATION_REVIEW_FIXES": "REQUIRE_OFFLINE_RUNNER_ROLLBACK_STRATEGY_PREPARATION_REVIEW_FIXES",
    }
)
PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewDecision = StrEnum(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewDecision",
    _DECISIONS,
)

PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewRisk = StrEnum(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewRisk",
    {
        "OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_NOT_APPROVED": "OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_NOT_APPROVED",
        **{value: value for value in _RISK_BY_KEY.values()},
        "REAL_EXECUTION_BOUNDARY_VIOLATION": "REAL_EXECUTION_BOUNDARY_VIOLATION",
        "DATA_ACCESS_VIOLATION": "DATA_ACCESS_VIOLATION",
        "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_FINAL_PLAN": "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_FINAL_PLAN",
    },
)

PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewRecommendation = StrEnum(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewRecommendation",
    {
        "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_FINAL_PLAN": "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_FINAL_PLAN",
        "APPROVE_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_FIRST": "APPROVE_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_FIRST",
        **{f"FIX_{value}": f"FIX_{value}" for value in _RISK_BY_KEY.values()},
        "RESTORE_OFFLINE_BOUNDARIES": "RESTORE_OFFLINE_BOUNDARIES",
        "REMOVE_DATA_ACCESS": "REMOVE_DATA_ACCESS",
        "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_FINAL_PLAN": "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_FINAL_PLAN",
        "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW_SUITE": "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW_SUITE",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_FINAL_PLAN": "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_FINAL_PLAN",
    },
)

Risk = PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewRisk

_BASE_FIELDS = [
    ("name", str),
    ("score", int, 0),
    ("reviewed", bool, False),
    ("risks", tuple[Risk, ...], ()),
    ("details", tuple[str, ...], ()),
    ("offline_only", bool, False),
    ("sandbox_only", bool, False),
    ("implementation_preparation_review_only", bool, False),
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
    ("observation_only", bool, False),
    ("human_approval_required", bool, False),
    ("stop_conditions_reviewed", bool, False),
    ("audit_reviewed", bool, False),
    ("test_strategy_reviewed", bool, False),
    ("rollback_strategy_reviewed", bool, False),
]

for _key, _class_name in dict(_ITEMS).items():
    globals()[_class_name] = make_dataclass(_class_name, _BASE_FIELDS, frozen=True)

PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewScore = make_dataclass(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewScore",
    [("overall_score", int, 0), ("implementation_safety_gate_score", int, 0)]
    + [(f"{key}_score", int, 0) for key, _class_name in _ITEMS],
    frozen=True,
)

_COMPAT_FIELDS = [
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

PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewInput = make_dataclass(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewInput",
    [(name, Any | None, None) for name in _COMPAT_FIELDS]
    + [("offline_runner_implementation_preparation_approved", bool | None, None)]
    + [(f"offline_runner_{key}_reviewed", bool, True) for key, _class_name in _ITEMS]
    + [
        ("offline_mode_enforced", bool, True),
        ("sandbox_mode_enforced", bool, True),
        ("implementation_preparation_review_only", bool, True),
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
        ("human_approval_required", bool, True),
        ("test_strategy_required", bool, True),
        ("rollback_strategy_required", bool, True),
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
        ("paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_final_plan_requested", bool, False),
        ("implementation_safety_gate_score", int | None, None),
    ]
    + [(f"{key}_score", int | None, None) for key, _class_name in _ITEMS],
    frozen=True,
)

PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewResult = make_dataclass(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewResult",
    [
        ("state", PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewState),
        ("decision", PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewDecision),
        ("score", PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewScore),
        ("risks", tuple[Risk, ...], ()),
        ("recommendations", tuple[PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewRecommendation, ...], ()),
        ("summary", str, ""),
        ("markdown_report", str, ""),
        ("offline_only", bool, True),
        ("sandbox_only", bool, True),
        ("implementation_preparation_review_only", bool, True),
        ("runner_created", bool, False),
        ("runner_executed", bool, False),
        ("dry_run_executed", bool, False),
        ("next_phase", str, "PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_FINAL_PLAN"),
    ]
    + [(key, globals()[class_name] | None, None) for key, class_name in _ITEMS]
    + [("findings", tuple[Any, ...], field(default_factory=tuple))],
    frozen=True,
)
