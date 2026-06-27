"""Models for controlled offline runner implementation preparation."""

from __future__ import annotations

from dataclasses import field, make_dataclass
from enum import StrEnum
from typing import Any


_ITEMS = (
    ("implementation_scope_contract", "OfflineRunnerImplementationScopePreparationContract"),
    ("implementation_architecture_contract", "OfflineRunnerImplementationArchitecturePreparationContract"),
    ("implementation_sequence_contract", "OfflineRunnerImplementationSequencePreparationContract"),
    ("runtime_contract", "OfflineRunnerRuntimePreparationContract"),
    ("input_adapter_contract", "OfflineRunnerInputAdapterPreparationContract"),
    ("synthetic_market_context_adapter_contract", "OfflineRunnerSyntheticMarketContextAdapterPreparationContract"),
    ("simulated_broker_adapter_contract", "OfflineRunnerSimulatedBrokerAdapterPreparationContract"),
    ("account_snapshot_adapter_contract", "OfflineRunnerAccountSnapshotAdapterPreparationContract"),
    ("market_data_snapshot_adapter_contract", "OfflineRunnerMarketDataSnapshotAdapterPreparationContract"),
    ("strategy_signal_probe_contract", "OfflineRunnerStrategySignalProbePreparationContract"),
    ("risk_observer_contract", "OfflineRunnerRiskObserverPreparationContract"),
    ("profitability_observer_contract", "OfflineRunnerProfitabilityObserverPreparationContract"),
    ("consistency_observer_contract", "OfflineRunnerConsistencyObserverPreparationContract"),
    ("journal_writer_contract", "OfflineRunnerJournalWriterPreparationContract"),
    ("observability_contract", "OfflineRunnerObservabilityPreparationContract"),
    ("human_approval_contract", "OfflineRunnerHumanApprovalPreparationContract"),
    ("stop_condition_contract", "OfflineRunnerStopConditionPreparationContract"),
    ("success_criteria_contract", "OfflineRunnerSuccessCriteriaPreparationContract"),
    ("failure_criteria_contract", "OfflineRunnerFailureCriteriaPreparationContract"),
    ("audit_contract", "OfflineRunnerAuditPreparationContract"),
    ("go_no_go_contract", "OfflineRunnerGoNoGoPreparationContract"),
    ("abort_contract", "OfflineRunnerAbortPreparationContract"),
    ("no_real_broker_guard", "OfflineRunnerNoRealBrokerImplementationGuard"),
    ("no_secret_read_guard", "OfflineRunnerNoSecretReadImplementationGuard"),
    ("network_block_guard", "OfflineRunnerNetworkBlockImplementationGuard"),
    ("http_websocket_socket_block_guard", "OfflineRunnerNetworkBlockImplementationGuard"),
    ("order_blocking_guard", "OfflineRunnerOrderBlockingImplementationGuard"),
    ("position_mutation_blocking_guard", "OfflineRunnerPositionMutationBlockingImplementationGuard"),
    ("data_access_guard", "OfflineRunnerDataAccessImplementationGuard"),
    ("test_strategy_contract", "OfflineRunnerTestStrategyPreparationContract"),
    ("rollback_strategy_contract", "OfflineRunnerRollbackStrategyPreparationContract"),
)

_RISK_BY_KEY = {
    "implementation_scope_contract": "OFFLINE_RUNNER_IMPLEMENTATION_SCOPE_PREPARATION_MISSING",
    "implementation_architecture_contract": "OFFLINE_RUNNER_IMPLEMENTATION_ARCHITECTURE_PREPARATION_UNSAFE",
    "implementation_sequence_contract": "OFFLINE_RUNNER_IMPLEMENTATION_SEQUENCE_PREPARATION_MISSING",
    "runtime_contract": "OFFLINE_RUNNER_RUNTIME_PREPARATION_UNSAFE",
    "input_adapter_contract": "OFFLINE_RUNNER_INPUT_ADAPTER_PREPARATION_UNSAFE",
    "synthetic_market_context_adapter_contract": "OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_ADAPTER_PREPARATION_UNSAFE",
    "simulated_broker_adapter_contract": "OFFLINE_RUNNER_SIMULATED_BROKER_ADAPTER_PREPARATION_UNSAFE",
    "account_snapshot_adapter_contract": "OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_ADAPTER_PREPARATION_UNSAFE",
    "market_data_snapshot_adapter_contract": "OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_ADAPTER_PREPARATION_UNSAFE",
    "strategy_signal_probe_contract": "OFFLINE_RUNNER_STRATEGY_SIGNAL_PROBE_PREPARATION_MISSING",
    "risk_observer_contract": "OFFLINE_RUNNER_RISK_OBSERVER_PREPARATION_MISSING",
    "profitability_observer_contract": "OFFLINE_RUNNER_PROFITABILITY_OBSERVER_PREPARATION_MISSING",
    "consistency_observer_contract": "OFFLINE_RUNNER_CONSISTENCY_OBSERVER_PREPARATION_MISSING",
    "journal_writer_contract": "OFFLINE_RUNNER_JOURNAL_WRITER_PREPARATION_MISSING",
    "observability_contract": "OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_MISSING",
    "human_approval_contract": "OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION_MISSING",
    "stop_condition_contract": "OFFLINE_RUNNER_STOP_CONDITIONS_PREPARATION_MISSING",
    "success_criteria_contract": "OFFLINE_RUNNER_SUCCESS_CRITERIA_PREPARATION_MISSING",
    "failure_criteria_contract": "OFFLINE_RUNNER_FAILURE_CRITERIA_PREPARATION_MISSING",
    "audit_contract": "OFFLINE_RUNNER_AUDIT_PREPARATION_MISSING",
    "go_no_go_contract": "OFFLINE_RUNNER_GO_NO_GO_PREPARATION_MISSING",
    "abort_contract": "OFFLINE_RUNNER_ABORT_PREPARATION_MISSING",
    "no_real_broker_guard": "OFFLINE_RUNNER_REAL_BROKER_GUARD_PREPARATION_MISSING",
    "no_secret_read_guard": "OFFLINE_RUNNER_SECRET_READ_GUARD_PREPARATION_UNSAFE",
    "network_block_guard": "OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_PREPARATION_UNSAFE",
    "http_websocket_socket_block_guard": "OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_PREPARATION_UNSAFE",
    "order_blocking_guard": "OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_PREPARATION_UNSAFE",
    "position_mutation_blocking_guard": "OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_PREPARATION_UNSAFE",
    "data_access_guard": "OFFLINE_RUNNER_DATA_ACCESS_GUARD_PREPARATION_UNSAFE",
    "test_strategy_contract": "OFFLINE_RUNNER_TEST_STRATEGY_PREPARATION_MISSING",
    "rollback_strategy_contract": "OFFLINE_RUNNER_ROLLBACK_STRATEGY_PREPARATION_MISSING",
}

PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationState = StrEnum(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationState",
    {
        "NOT_READY": "NOT_READY",
        "OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_INPUT_INVALID": "OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_INPUT_INVALID",
        "OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_BLOCKED": "OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_BLOCKED",
        "OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_COMPLETED_WITH_WARNINGS": "OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_COMPLETED_WITH_WARNINGS",
        "OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_COMPLETED": "OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_COMPLETED",
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW": "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW",
    },
)

_DECISIONS = {
    "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION": "BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION",
    "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE_FIXES",
    "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION": "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION",
}
for _key in _RISK_BY_KEY:
    _name = "REQUIRE_OFFLINE_RUNNER_" + _key.upper().replace("_CONTRACT", "").replace("_GUARD", "_GUARD").replace("IMPLEMENTATION_", "IMPLEMENTATION_") + "_PREPARATION_FIXES"
    _name = _name.replace("SUCCESS_CRITERIA_PREPARATION_FIXES", "SUCCESS_FAILURE_PREPARATION_FIXES")
    _name = _name.replace("FAILURE_CRITERIA_PREPARATION_FIXES", "SUCCESS_FAILURE_PREPARATION_FIXES")
    _DECISIONS[_name] = _name
_DECISIONS.update(
    {
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SCOPE_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SCOPE_PREPARATION_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_ARCHITECTURE_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_ARCHITECTURE_PREPARATION_FIXES",
        "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SEQUENCE_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SEQUENCE_PREPARATION_FIXES",
        "REQUIRE_OFFLINE_RUNNER_RUNTIME_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_RUNTIME_PREPARATION_FIXES",
        "REQUIRE_OFFLINE_RUNNER_INPUT_ADAPTER_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_INPUT_ADAPTER_PREPARATION_FIXES",
        "REQUIRE_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_ADAPTER_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_ADAPTER_PREPARATION_FIXES",
        "REQUIRE_OFFLINE_RUNNER_SIMULATED_BROKER_ADAPTER_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_SIMULATED_BROKER_ADAPTER_PREPARATION_FIXES",
        "REQUIRE_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_ADAPTER_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_ADAPTER_PREPARATION_FIXES",
        "REQUIRE_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_ADAPTER_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_ADAPTER_PREPARATION_FIXES",
        "REQUIRE_OFFLINE_RUNNER_STRATEGY_SIGNAL_PROBE_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_STRATEGY_SIGNAL_PROBE_PREPARATION_FIXES",
        "REQUIRE_OFFLINE_RUNNER_RISK_OBSERVER_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_RISK_OBSERVER_PREPARATION_FIXES",
        "REQUIRE_OFFLINE_RUNNER_PROFITABILITY_OBSERVER_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_PROFITABILITY_OBSERVER_PREPARATION_FIXES",
        "REQUIRE_OFFLINE_RUNNER_CONSISTENCY_OBSERVER_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_CONSISTENCY_OBSERVER_PREPARATION_FIXES",
        "REQUIRE_OFFLINE_RUNNER_JOURNAL_WRITER_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_JOURNAL_WRITER_PREPARATION_FIXES",
        "REQUIRE_OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_FIXES",
        "REQUIRE_OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION_FIXES",
        "REQUIRE_OFFLINE_RUNNER_STOP_CONDITION_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_STOP_CONDITION_PREPARATION_FIXES",
        "REQUIRE_OFFLINE_RUNNER_SUCCESS_FAILURE_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_SUCCESS_FAILURE_PREPARATION_FIXES",
        "REQUIRE_OFFLINE_RUNNER_AUDIT_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_AUDIT_PREPARATION_FIXES",
        "REQUIRE_OFFLINE_RUNNER_GO_NO_GO_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_GO_NO_GO_PREPARATION_FIXES",
        "REQUIRE_OFFLINE_RUNNER_ABORT_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_ABORT_PREPARATION_FIXES",
        "REQUIRE_OFFLINE_RUNNER_NO_REAL_BROKER_GUARD_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_NO_REAL_BROKER_GUARD_PREPARATION_FIXES",
        "REQUIRE_OFFLINE_RUNNER_NO_SECRET_READ_GUARD_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_NO_SECRET_READ_GUARD_PREPARATION_FIXES",
        "REQUIRE_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_PREPARATION_FIXES",
        "REQUIRE_OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_PREPARATION_FIXES",
        "REQUIRE_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_PREPARATION_FIXES",
        "REQUIRE_OFFLINE_RUNNER_DATA_ACCESS_GUARD_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_DATA_ACCESS_GUARD_PREPARATION_FIXES",
        "REQUIRE_OFFLINE_RUNNER_TEST_STRATEGY_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_TEST_STRATEGY_PREPARATION_FIXES",
        "REQUIRE_OFFLINE_RUNNER_ROLLBACK_STRATEGY_PREPARATION_FIXES": "REQUIRE_OFFLINE_RUNNER_ROLLBACK_STRATEGY_PREPARATION_FIXES",
    }
)
PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationDecision = StrEnum(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationDecision",
    _DECISIONS,
)

PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationRisk = StrEnum(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationRisk",
    {
        "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE_NOT_APPROVED": "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE_NOT_APPROVED",
        **{value: value for value in _RISK_BY_KEY.values()},
        "REAL_EXECUTION_BOUNDARY_VIOLATION": "REAL_EXECUTION_BOUNDARY_VIOLATION",
        "DATA_ACCESS_VIOLATION": "DATA_ACCESS_VIOLATION",
        "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW": "PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW",
    },
)

PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationRecommendation = StrEnum(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationRecommendation",
    {
        "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW": "HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW",
        "APPROVE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE_FIRST": "APPROVE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE_FIRST",
        **{f"FIX_{value}": f"FIX_{value}" for value in _RISK_BY_KEY.values()},
        "RESTORE_OFFLINE_BOUNDARIES": "RESTORE_OFFLINE_BOUNDARIES",
        "REMOVE_DATA_ACCESS": "REMOVE_DATA_ACCESS",
        "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW": "DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW",
        "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_SUITE": "RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_SUITE",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW": "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW",
    },
)

Risk = PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationRisk

_BASE_FIELDS = [
    ("name", str),
    ("score", int, 0),
    ("prepared", bool, False),
    ("risks", tuple[Risk, ...], ()),
    ("details", tuple[str, ...], ()),
    ("offline_only", bool, False),
    ("sandbox_only", bool, False),
    ("implementation_preparation_only", bool, False),
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
    ("stop_conditions_prepared", bool, False),
    ("audit_prepared", bool, False),
    ("test_strategy_prepared", bool, False),
    ("rollback_strategy_prepared", bool, False),
]

for _key, _class_name in dict(_ITEMS).items():
    globals()[_class_name] = make_dataclass(_class_name, _BASE_FIELDS, frozen=True)

PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationScore = make_dataclass(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationScore",
    [("overall_score", int, 0), ("implementation_safety_gate_score", int, 0)]
    + [(f"{key}_score", int, 0) for key, _class_name in _ITEMS],
    frozen=True,
)

_COMPAT_FIELDS = [
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

PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationInput = make_dataclass(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationInput",
    [(name, Any | None, None) for name in _COMPAT_FIELDS]
    + [("offline_runner_implementation_safety_gate_approved", bool | None, None)]
    + [(f"offline_runner_{key}_prepared", bool, True) for key, _class_name in _ITEMS]
    + [
        ("offline_mode_enforced", bool, True),
        ("sandbox_mode_enforced", bool, True),
        ("implementation_preparation_only", bool, True),
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
        ("paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_review_requested", bool, False),
        ("implementation_safety_gate_score", int | None, None),
    ]
    + [(f"{key}_score", int | None, None) for key, _class_name in _ITEMS],
    frozen=True,
)

PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationResult = make_dataclass(
    "PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationResult",
    [
        ("state", PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationState),
        ("decision", PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationDecision),
        ("score", PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationScore),
        ("risks", tuple[Risk, ...], ()),
        ("recommendations", tuple[PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationRecommendation, ...], ()),
        ("summary", str, ""),
        ("markdown_report", str, ""),
        ("offline_only", bool, True),
        ("sandbox_only", bool, True),
        ("implementation_preparation_only", bool, True),
        ("runner_created", bool, False),
        ("runner_executed", bool, False),
        ("dry_run_executed", bool, False),
        ("next_phase", str, "PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW"),
    ]
    + [(key, globals()[class_name] | None, None) for key, class_name in _ITEMS]
    + [("contracts", tuple[Any, ...], field(default_factory=tuple))],
    frozen=True,
)
