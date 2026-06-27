"""Offline review for controlled paper broker read-only offline runner preparation."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading import paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review_models as m

Risk = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewRisk
Decision = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewDecision
Recommendation = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewRecommendation


def _coerce_input(data):
    if data is None:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewInput()
    if isinstance(data, m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewInput):
        return data
    allowed = {field.name for field in fields(m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewInput)}
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewInput(
        **{key: value for key, value in dict(data).items() if key in allowed}
    )


def _value(item: Any) -> str:
    if item is None:
        return ""
    if isinstance(item, Enum):
        return str(item.value)
    return str(item)


def _get(obj: Any, name: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, Mapping):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _as_tuple(items: Any) -> tuple[Any, ...]:
    if items is None:
        return ()
    if isinstance(items, tuple):
        return items
    if isinstance(items, list):
        return tuple(items)
    if isinstance(items, set):
        return tuple(items)
    return (items,)


def _contains(items: Any, *needles: str) -> bool:
    values = tuple(_value(item).upper() for item in _as_tuple(items))
    return any(any(needle.upper() in value for value in values) for needle in needles)


def _dedupe(items: Iterable[Any]) -> tuple[Any, ...]:
    seen: set[Any] = set()
    result: list[Any] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return tuple(result)


def _clamp(value: int | float, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(round(value))))


def _average(values: Iterable[int | float | None], default: int = 0) -> int:
    usable = [float(value) for value in values if value is not None]
    return default if not usable else _clamp(sum(usable) / len(usable))


def _metric_score(explicit: int | None, fallback: Any, passed: bool) -> int:
    if explicit is not None:
        return _clamp(explicit)
    if fallback is not None:
        return _clamp(fallback)
    return 100 if passed else 0


def _preparation(data):
    return data.paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation


def _contract(data, name: str):
    return _get(_preparation(data), name)


def _contract_ok(contract: Any) -> bool:
    return contract is not None and _get(contract, "prepared", True) is True and not _as_tuple(_get(contract, "risks", ()))


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def validate_offline_runner_preparation_approval(data) -> bool:
    data = _coerce_input(data)
    preparation = _preparation(data)
    if preparation is None or data.offline_runner_preparation_approved is False:
        return False
    approved = data.offline_runner_preparation_approved is True or _state_contains(
        preparation,
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION",
    )
    return approved and not _as_tuple(_get(preparation, "risks", ())) and _get(preparation, "offline_only", True) is True


def _offline_boundary(data) -> bool:
    expected_true = (
        data.offline_mode_enforced, data.sandbox_mode_enforced, data.review_only,
        data.no_runner_executable_created, data.no_runner_execution, data.no_dry_run_execution,
        data.broker_connection_disabled, data.no_real_broker, data.no_alpaca_real,
        data.no_api_key_read, data.no_env_var_read, data.no_hardcoded_secrets,
        data.no_http_transport, data.no_websocket_transport, data.no_socket_transport,
        data.no_external_api, data.no_external_ml, data.no_external_llm, data.no_live_execution,
        data.no_real_account_access, data.no_real_order, data.no_position_mutation,
    )
    requested = (
        data.real_execution_requested, data.runner_creation_requested, data.runner_execution_requested,
        data.dry_run_requested, data.dry_run_executed, data.broker_connection_requested,
        data.api_key_read_requested, data.env_var_read_requested, data.hardcoded_secret_detected,
        data.network_transport_requested, data.external_api_requested, data.order_execution_requested,
        data.position_mutation_requested, data.account_access_requested,
    )
    return all(item is True for item in expected_true) and not any(item is True for item in requested)


def _data_boundary(data) -> bool:
    return data.data_access_requested is not True and not _contains(_get(_preparation(data), "risks", ()), "DATA_ACCESS", "DATA/")


_SPECS = {
    "scope_preparation_review": ("review_offline_runner_scope_preparation_contract", "scope_contract", "offline_runner_scope_preparation_review_verified", "scope_score", Risk.OFFLINE_RUNNER_SCOPE_PREPARATION_REVIEW_FAILED, m.OfflineRunnerScopePreparationReviewFinding, ("offline_only", "sandbox_only", "preparation_only", "no_runner_executable_created")),
    "execution_mode_preparation_review": ("review_offline_runner_execution_mode_preparation_contract", "execution_mode_contract", "offline_runner_execution_mode_preparation_review_verified", "execution_mode_score", Risk.OFFLINE_RUNNER_EXECUTION_MODE_PREPARATION_REVIEW_FAILED, m.OfflineRunnerExecutionModePreparationReviewFinding, ("controlled_offline_mode", "deterministic_mode", "in_memory_only", "no_dry_run_execution")),
    "input_preparation_review": ("review_offline_runner_input_preparation_contract", "input_contract", "offline_runner_input_contract_preparation_review_verified", "input_contract_score", Risk.OFFLINE_RUNNER_INPUT_CONTRACT_PREPARATION_REVIEW_FAILED, m.OfflineRunnerInputPreparationReviewFinding, ("schema_only_inputs", "synthetic_inputs_only", "no_real_credentials")),
    "synthetic_market_context_preparation_review": ("review_offline_runner_synthetic_market_context_preparation_contract", "synthetic_market_context_contract", "offline_runner_synthetic_market_context_preparation_review_verified", "synthetic_market_context_score", Risk.OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_PREPARATION_REVIEW_FAILED, m.OfflineRunnerSyntheticMarketContextPreparationReviewFinding, ("synthetic_context_only", "in_memory_context", "no_data_access")),
    "read_only_broker_simulation_preparation_review": ("review_offline_runner_read_only_broker_simulation_preparation_contract", "read_only_broker_simulation_contract", "offline_runner_read_only_broker_simulation_preparation_review_verified", "read_only_broker_simulation_score", Risk.OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_PREPARATION_REVIEW_FAILED, m.OfflineRunnerReadOnlyBrokerSimulationPreparationReviewFinding, ("simulated_broker_only", "read_only_contract", "no_real_broker")),
    "no_real_broker_guard_review": ("review_offline_runner_no_real_broker_guard", "no_real_broker_guard", "offline_runner_no_real_broker_guard_review_verified", "no_real_broker_score", Risk.OFFLINE_RUNNER_REAL_BROKER_GUARD_REVIEW_FAILED, m.OfflineRunnerNoRealBrokerGuardReviewFinding, ("real_broker_blocked", "alpaca_blocked", "broker_connection_disabled")),
    "no_secret_read_guard_review": ("review_offline_runner_no_secret_read_guard", "no_secret_read_guard", "offline_runner_no_secret_read_guard_review_verified", "no_secret_read_score", Risk.OFFLINE_RUNNER_SECRET_READ_GUARD_REVIEW_FAILED, m.OfflineRunnerNoSecretReadGuardReviewFinding, ("no_api_key_read", "no_env_var_read", "no_hardcoded_secret")),
    "network_block_guard_review": ("review_offline_runner_network_block_guard", "network_block_guard", "offline_runner_network_block_guard_review_verified", "network_score", Risk.OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_REVIEW_FAILED, m.OfflineRunnerNetworkBlockGuardReviewFinding, ("network_blocked", "http_blocked", "websocket_blocked", "socket_blocked", "external_api_blocked")),
    "http_websocket_socket_block_guard_review": ("review_offline_runner_http_websocket_socket_block_guard", "http_websocket_socket_block_guard", "offline_runner_http_websocket_socket_block_guard_review_verified", "http_websocket_socket_score", Risk.OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW_FAILED, m.OfflineRunnerNetworkBlockGuardReviewFinding, ("network_blocked", "http_blocked", "websocket_blocked", "socket_blocked", "external_api_blocked")),
    "account_snapshot_preparation_review": ("review_offline_runner_account_snapshot_preparation_contract", "account_snapshot_contract", "offline_runner_account_snapshot_preparation_review_verified", "account_snapshot_score", Risk.OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_PREPARATION_REVIEW_FAILED, m.OfflineRunnerAccountSnapshotPreparationReviewFinding, ("simulated_snapshot_only", "read_only_snapshot", "active_account_access_blocked")),
    "market_data_snapshot_preparation_review": ("review_offline_runner_market_data_snapshot_preparation_contract", "market_data_snapshot_contract", "offline_runner_market_data_snapshot_preparation_review_verified", "market_data_snapshot_score", Risk.OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_PREPARATION_REVIEW_FAILED, m.OfflineRunnerMarketDataSnapshotPreparationReviewFinding, ("synthetic_snapshot_only", "read_only_snapshot", "live_subscription_blocked")),
    "order_blocking_guard_review": ("review_offline_runner_order_blocking_guard", "order_blocking_guard", "offline_runner_order_blocking_guard_review_verified", "order_blocking_score", Risk.OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_REVIEW_FAILED, m.OfflineRunnerOrderBlockingGuardReviewFinding, ("order_execution_blocked", "real_order_blocked", "cancel_replace_blocked")),
    "position_mutation_blocking_guard_review": ("review_offline_runner_position_mutation_blocking_guard", "position_mutation_blocking_guard", "offline_runner_position_mutation_blocking_guard_review_verified", "position_mutation_score", Risk.OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_REVIEW_FAILED, m.OfflineRunnerPositionMutationBlockingGuardReviewFinding, ("position_mutation_blocked", "close_modify_blocked", "simulated_position_read_only")),
    "strategy_signal_observation_preparation_review": ("review_offline_runner_strategy_signal_observation_preparation_contract", "strategy_signal_observation_contract", "offline_runner_strategy_signal_observation_preparation_review_verified", "strategy_signal_observation_score", Risk.OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_PREPARATION_REVIEW_FAILED, m.OfflineRunnerStrategySignalObservationPreparationReviewFinding, ("observation_only", "no_signal_execution", "signal_trace_required")),
    "risk_observation_preparation_review": ("review_offline_runner_risk_observation_preparation_contract", "risk_observation_contract", "offline_runner_risk_observation_preparation_review_verified", "risk_observation_score", Risk.OFFLINE_RUNNER_RISK_OBSERVATION_PREPARATION_REVIEW_FAILED, m.OfflineRunnerRiskObservationPreparationReviewFinding, ("observation_only", "no_risk_action_execution", "risk_trace_required")),
    "profitability_observation_preparation_review": ("review_offline_runner_profitability_observation_preparation_contract", "profitability_observation_contract", "offline_runner_profitability_observation_preparation_review_verified", "profitability_observation_score", Risk.OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_PREPARATION_REVIEW_FAILED, m.OfflineRunnerProfitabilityObservationPreparationReviewFinding, ("observation_only", "no_profit_promise", "profitability_trace_required")),
    "consistency_observation_preparation_review": ("review_offline_runner_consistency_observation_preparation_contract", "consistency_observation_contract", "offline_runner_consistency_observation_preparation_review_verified", "consistency_observation_score", Risk.OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_PREPARATION_REVIEW_FAILED, m.OfflineRunnerConsistencyObservationPreparationReviewFinding, ("observation_only", "deterministic_consistency_checks", "consistency_trace_required")),
    "journal_preparation_review": ("review_offline_runner_journal_preparation_contract", "journal_contract", "offline_runner_journal_preparation_review_verified", "journal_score", Risk.OFFLINE_RUNNER_JOURNAL_PREPARATION_REVIEW_FAILED, m.OfflineRunnerJournalPreparationReviewFinding, ("offline_journal_required", "no_secret_material_logged", "plan_events_recorded")),
    "observability_preparation_review": ("review_offline_runner_observability_preparation_contract", "observability_contract", "offline_runner_observability_preparation_review_verified", "observability_score", Risk.OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_REVIEW_FAILED, m.OfflineRunnerObservabilityPreparationReviewFinding, ("offline_events_defined", "no_connection_attempt_metrics", "sensitive_values_redacted")),
    "human_approval_preparation_review": ("review_offline_runner_human_approval_preparation_contract", "human_approval_contract", "offline_runner_human_approval_preparation_review_verified", "human_approval_score", Risk.OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION_REVIEW_FAILED, m.OfflineRunnerHumanApprovalPreparationReviewFinding, ("human_approval_required", "approval_before_review", "evidence_required")),
    "stop_conditions_preparation_review": ("review_offline_runner_stop_conditions_preparation_contract", "stop_conditions_contract", "offline_runner_stop_conditions_preparation_review_verified", "stop_conditions_score", Risk.OFFLINE_RUNNER_STOP_CONDITIONS_PREPARATION_REVIEW_FAILED, m.OfflineRunnerStopConditionPreparationReviewFinding, ("stop_on_secret_read", "stop_on_network_request", "stop_on_order_or_position_request", "stop_on_account_access_request")),
    "success_criteria_preparation_review": ("review_offline_runner_success_criteria_preparation_contract", "success_criteria_contract", "offline_runner_success_criteria_preparation_review_verified", "success_score", Risk.OFFLINE_RUNNER_SUCCESS_CRITERIA_PREPARATION_REVIEW_FAILED, m.OfflineRunnerSuccessCriteriaPreparationReviewFinding, ("no_boundary_violation_required", "all_contracts_prepared", "no_runner_execution_required")),
    "failure_criteria_preparation_review": ("review_offline_runner_failure_criteria_preparation_contract", "failure_criteria_contract", "offline_runner_failure_criteria_preparation_review_verified", "failure_score", Risk.OFFLINE_RUNNER_FAILURE_CRITERIA_PREPARATION_REVIEW_FAILED, m.OfflineRunnerFailureCriteriaPreparationReviewFinding, ("fail_on_boundary_violation", "fail_on_missing_contract", "fail_on_execution_request")),
    "audit_preparation_review": ("review_offline_runner_audit_preparation_contract", "audit_contract", "offline_runner_audit_preparation_review_verified", "audit_score", Risk.OFFLINE_RUNNER_AUDIT_PREPARATION_REVIEW_FAILED, m.OfflineRunnerAuditPreparationReviewFinding, ("audit_events_defined", "boundary_evidence_required", "immutable_preparation_record_required")),
    "go_no_go_preparation_review": ("review_offline_runner_go_no_go_preparation_contract", "go_no_go_contract", "offline_runner_go_no_go_preparation_review_verified", "go_no_go_score", Risk.OFFLINE_RUNNER_GO_NO_GO_PREPARATION_REVIEW_FAILED, m.OfflineRunnerGoNoGoPreparationReviewFinding, ("go_no_go_required", "no_go_on_risk", "next_phase_requires_clean_preparation")),
    "abort_preparation_review": ("review_offline_runner_abort_preparation_contract", "abort_contract", "offline_runner_abort_preparation_review_verified", "abort_score", Risk.OFFLINE_RUNNER_ABORT_PREPARATION_REVIEW_FAILED, m.OfflineRunnerAbortPreparationReviewFinding, ("abort_on_secret_read", "abort_on_network_or_broker_request", "abort_on_order_or_position_request")),
}


_RISK_TO_DECISION = {
    Risk.OFFLINE_RUNNER_PREPARATION_NOT_APPROVED: Decision.REQUIRE_OFFLINE_RUNNER_PREPARATION_FIXES,
    Risk.OFFLINE_RUNNER_SCOPE_PREPARATION_REVIEW_FAILED: Decision.REQUIRE_OFFLINE_RUNNER_SCOPE_PREPARATION_REVIEW_FIXES,
    Risk.OFFLINE_RUNNER_EXECUTION_MODE_PREPARATION_REVIEW_FAILED: Decision.REQUIRE_OFFLINE_RUNNER_EXECUTION_MODE_PREPARATION_REVIEW_FIXES,
    Risk.OFFLINE_RUNNER_INPUT_CONTRACT_PREPARATION_REVIEW_FAILED: Decision.REQUIRE_OFFLINE_RUNNER_INPUT_CONTRACT_PREPARATION_REVIEW_FIXES,
    Risk.OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_PREPARATION_REVIEW_FAILED: Decision.REQUIRE_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_PREPARATION_REVIEW_FIXES,
    Risk.OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_PREPARATION_REVIEW_FAILED: Decision.REQUIRE_OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_PREPARATION_REVIEW_FIXES,
    Risk.OFFLINE_RUNNER_REAL_BROKER_GUARD_REVIEW_FAILED: Decision.REQUIRE_OFFLINE_RUNNER_NO_REAL_BROKER_GUARD_REVIEW_FIXES,
    Risk.OFFLINE_RUNNER_SECRET_READ_GUARD_REVIEW_FAILED: Decision.REQUIRE_OFFLINE_RUNNER_NO_SECRET_READ_GUARD_REVIEW_FIXES,
    Risk.OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_REVIEW_FAILED: Decision.REQUIRE_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_REVIEW_FIXES,
    Risk.OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW_FAILED: Decision.REQUIRE_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_REVIEW_FIXES,
    Risk.OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_PREPARATION_REVIEW_FAILED: Decision.REQUIRE_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_PREPARATION_REVIEW_FIXES,
    Risk.OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_PREPARATION_REVIEW_FAILED: Decision.REQUIRE_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_PREPARATION_REVIEW_FIXES,
    Risk.OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_REVIEW_FAILED: Decision.REQUIRE_OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_REVIEW_FIXES,
    Risk.OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_REVIEW_FAILED: Decision.REQUIRE_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_REVIEW_FIXES,
    Risk.OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_PREPARATION_REVIEW_FAILED: Decision.REQUIRE_OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_PREPARATION_REVIEW_FIXES,
    Risk.OFFLINE_RUNNER_RISK_OBSERVATION_PREPARATION_REVIEW_FAILED: Decision.REQUIRE_OFFLINE_RUNNER_RISK_OBSERVATION_PREPARATION_REVIEW_FIXES,
    Risk.OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_PREPARATION_REVIEW_FAILED: Decision.REQUIRE_OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_PREPARATION_REVIEW_FIXES,
    Risk.OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_PREPARATION_REVIEW_FAILED: Decision.REQUIRE_OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_PREPARATION_REVIEW_FIXES,
    Risk.OFFLINE_RUNNER_JOURNAL_PREPARATION_REVIEW_FAILED: Decision.REQUIRE_OFFLINE_RUNNER_JOURNAL_PREPARATION_REVIEW_FIXES,
    Risk.OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_REVIEW_FAILED: Decision.REQUIRE_OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_REVIEW_FIXES,
    Risk.OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION_REVIEW_FAILED: Decision.REQUIRE_OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION_REVIEW_FIXES,
    Risk.OFFLINE_RUNNER_STOP_CONDITIONS_PREPARATION_REVIEW_FAILED: Decision.REQUIRE_OFFLINE_RUNNER_STOP_CONDITION_PREPARATION_REVIEW_FIXES,
    Risk.OFFLINE_RUNNER_SUCCESS_CRITERIA_PREPARATION_REVIEW_FAILED: Decision.REQUIRE_OFFLINE_RUNNER_SUCCESS_FAILURE_PREPARATION_REVIEW_FIXES,
    Risk.OFFLINE_RUNNER_FAILURE_CRITERIA_PREPARATION_REVIEW_FAILED: Decision.REQUIRE_OFFLINE_RUNNER_SUCCESS_FAILURE_PREPARATION_REVIEW_FIXES,
    Risk.OFFLINE_RUNNER_AUDIT_PREPARATION_REVIEW_FAILED: Decision.REQUIRE_OFFLINE_RUNNER_AUDIT_PREPARATION_REVIEW_FIXES,
    Risk.OFFLINE_RUNNER_GO_NO_GO_PREPARATION_REVIEW_FAILED: Decision.REQUIRE_OFFLINE_RUNNER_GO_NO_GO_PREPARATION_REVIEW_FIXES,
    Risk.OFFLINE_RUNNER_ABORT_PREPARATION_REVIEW_FAILED: Decision.REQUIRE_OFFLINE_RUNNER_ABORT_PREPARATION_REVIEW_FIXES,
}

_RISK_TO_RECOMMENDATION = {
    Risk.OFFLINE_RUNNER_PREPARATION_NOT_APPROVED: Recommendation.APPROVE_OFFLINE_RUNNER_PREPARATION_FIRST,
    Risk.OFFLINE_RUNNER_SCOPE_PREPARATION_REVIEW_FAILED: Recommendation.FIX_OFFLINE_RUNNER_SCOPE_PREPARATION_REVIEW,
    Risk.OFFLINE_RUNNER_EXECUTION_MODE_PREPARATION_REVIEW_FAILED: Recommendation.FIX_OFFLINE_RUNNER_EXECUTION_MODE_PREPARATION_REVIEW,
    Risk.OFFLINE_RUNNER_INPUT_CONTRACT_PREPARATION_REVIEW_FAILED: Recommendation.FIX_OFFLINE_RUNNER_INPUT_CONTRACT_PREPARATION_REVIEW,
    Risk.OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_PREPARATION_REVIEW_FAILED: Recommendation.FIX_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_PREPARATION_REVIEW,
    Risk.OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_PREPARATION_REVIEW_FAILED: Recommendation.FIX_OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_PREPARATION_REVIEW,
    Risk.OFFLINE_RUNNER_REAL_BROKER_GUARD_REVIEW_FAILED: Recommendation.FIX_OFFLINE_RUNNER_NO_REAL_BROKER_GUARD_REVIEW,
    Risk.OFFLINE_RUNNER_SECRET_READ_GUARD_REVIEW_FAILED: Recommendation.FIX_OFFLINE_RUNNER_NO_SECRET_READ_GUARD_REVIEW,
    Risk.OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_REVIEW_FAILED: Recommendation.FIX_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_REVIEW,
    Risk.OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW_FAILED: Recommendation.FIX_OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW,
    Risk.OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_PREPARATION_REVIEW_FAILED: Recommendation.FIX_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_PREPARATION_REVIEW,
    Risk.OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_PREPARATION_REVIEW_FAILED: Recommendation.FIX_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_PREPARATION_REVIEW,
    Risk.OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_REVIEW_FAILED: Recommendation.FIX_OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_REVIEW,
    Risk.OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_REVIEW_FAILED: Recommendation.FIX_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_REVIEW,
    Risk.OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_PREPARATION_REVIEW_FAILED: Recommendation.FIX_OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_PREPARATION_REVIEW,
    Risk.OFFLINE_RUNNER_RISK_OBSERVATION_PREPARATION_REVIEW_FAILED: Recommendation.FIX_OFFLINE_RUNNER_RISK_OBSERVATION_PREPARATION_REVIEW,
    Risk.OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_PREPARATION_REVIEW_FAILED: Recommendation.FIX_OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_PREPARATION_REVIEW,
    Risk.OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_PREPARATION_REVIEW_FAILED: Recommendation.FIX_OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_PREPARATION_REVIEW,
    Risk.OFFLINE_RUNNER_JOURNAL_PREPARATION_REVIEW_FAILED: Recommendation.FIX_OFFLINE_RUNNER_JOURNAL_PREPARATION_REVIEW,
    Risk.OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_REVIEW_FAILED: Recommendation.FIX_OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_REVIEW,
    Risk.OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION_REVIEW_FAILED: Recommendation.FIX_OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION_REVIEW,
    Risk.OFFLINE_RUNNER_STOP_CONDITIONS_PREPARATION_REVIEW_FAILED: Recommendation.FIX_OFFLINE_RUNNER_STOP_CONDITION_PREPARATION_REVIEW,
    Risk.OFFLINE_RUNNER_SUCCESS_CRITERIA_PREPARATION_REVIEW_FAILED: Recommendation.FIX_OFFLINE_RUNNER_SUCCESS_FAILURE_PREPARATION_REVIEW,
    Risk.OFFLINE_RUNNER_FAILURE_CRITERIA_PREPARATION_REVIEW_FAILED: Recommendation.FIX_OFFLINE_RUNNER_SUCCESS_FAILURE_PREPARATION_REVIEW,
    Risk.OFFLINE_RUNNER_AUDIT_PREPARATION_REVIEW_FAILED: Recommendation.FIX_OFFLINE_RUNNER_AUDIT_PREPARATION_REVIEW,
    Risk.OFFLINE_RUNNER_GO_NO_GO_PREPARATION_REVIEW_FAILED: Recommendation.FIX_OFFLINE_RUNNER_GO_NO_GO_PREPARATION_REVIEW,
    Risk.OFFLINE_RUNNER_ABORT_PREPARATION_REVIEW_FAILED: Recommendation.FIX_OFFLINE_RUNNER_ABORT_PREPARATION_REVIEW,
    Risk.REAL_EXECUTION_BOUNDARY_VIOLATION: Recommendation.RESTORE_OFFLINE_BOUNDARIES,
    Risk.DATA_ACCESS_VIOLATION: Recommendation.REMOVE_DATA_ACCESS,
    Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN: Recommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN,
}


def _guarded_fields(data, attrs: tuple[str, ...]) -> dict[str, bool]:
    blocked = {
        "no_runner_executable_created": data.runner_creation_requested is not True,
        "no_dry_run_execution": data.dry_run_executed is not True and data.dry_run_requested is not True,
        "no_real_broker": data.broker_connection_requested is not True and data.no_real_broker is True,
        "real_broker_blocked": data.broker_connection_requested is not True and data.no_real_broker is True,
        "alpaca_blocked": data.no_alpaca_real is True,
        "broker_connection_disabled": data.broker_connection_disabled is True and data.broker_connection_requested is not True,
        "no_api_key_read": data.api_key_read_requested is not True and data.no_api_key_read is True,
        "no_env_var_read": data.env_var_read_requested is not True and data.no_env_var_read is True,
        "no_hardcoded_secret": data.hardcoded_secret_detected is not True and data.no_hardcoded_secrets is True,
        "network_blocked": data.network_transport_requested is not True,
        "http_blocked": data.no_http_transport is True,
        "websocket_blocked": data.no_websocket_transport is True,
        "socket_blocked": data.no_socket_transport is True,
        "external_api_blocked": data.external_api_requested is not True and data.no_external_api is True,
        "active_account_access_blocked": data.account_access_requested is not True,
        "order_execution_blocked": data.order_execution_requested is not True,
        "real_order_blocked": data.order_execution_requested is not True and data.no_real_order is True,
        "position_mutation_blocked": data.position_mutation_requested is not True and data.no_position_mutation is True,
        "no_data_access": data.data_access_requested is not True,
        "no_runner_execution_required": data.runner_execution_requested is not True and data.no_runner_execution is True,
        "fail_on_execution_request": data.runner_execution_requested is not True and data.dry_run_requested is not True,
        "next_phase_requires_clean_preparation": data.paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_plan_requested is not True,
        "no_connection_attempt_metrics": data.broker_connection_requested is not True,
    }
    return {attr: blocked.get(attr, True) for attr in attrs}


def _review(data, result_key: str):
    data = _coerce_input(data)
    _fn, contract_name, flag_name, score_name, risk, cls, attrs = _SPECS[result_key]
    contract = _contract(data, contract_name)
    values = {attr: _get(contract, attr) is True and ok for attr, ok in _guarded_fields(data, attrs).items()}
    passed = _get(data, flag_name) is not False and _contract_ok(contract) and all(values.values())
    payload = {
        "score": _metric_score(_get(data, score_name), _get(contract, "score"), passed),
        "passed": passed,
        "risks": () if passed else (risk,),
        "details": (f"{contract_name} reviewed offline without creating or executing a runner",),
        **values,
    }
    if result_key == "http_websocket_socket_block_guard_review":
        payload["name"] = "offline_runner_http_websocket_socket_block_guard_review"
    return cls(**payload)


def _make_review(result_key: str):
    def review(data):
        return _review(data, result_key)
    review.__name__ = _SPECS[result_key][0]
    return review


for _result_key, _spec in _SPECS.items():
    globals()[_spec[0]] = _make_review(_result_key)


def _findings(data):
    return {key: _review(data, key) for key in _SPECS}


_SCORE_MAP = {
    "scope_score": "scope_preparation_review",
    "execution_mode_score": "execution_mode_preparation_review",
    "input_contract_score": "input_preparation_review",
    "synthetic_market_context_score": "synthetic_market_context_preparation_review",
    "read_only_broker_simulation_score": "read_only_broker_simulation_preparation_review",
    "no_real_broker_score": "no_real_broker_guard_review",
    "no_secret_read_score": "no_secret_read_guard_review",
    "network_score": "network_block_guard_review",
    "http_websocket_socket_score": "http_websocket_socket_block_guard_review",
    "account_snapshot_score": "account_snapshot_preparation_review",
    "market_data_snapshot_score": "market_data_snapshot_preparation_review",
    "order_blocking_score": "order_blocking_guard_review",
    "position_mutation_score": "position_mutation_blocking_guard_review",
    "strategy_signal_observation_score": "strategy_signal_observation_preparation_review",
    "risk_observation_score": "risk_observation_preparation_review",
    "profitability_observation_score": "profitability_observation_preparation_review",
    "consistency_observation_score": "consistency_observation_preparation_review",
    "journal_score": "journal_preparation_review",
    "observability_score": "observability_preparation_review",
    "human_approval_score": "human_approval_preparation_review",
    "stop_conditions_score": "stop_conditions_preparation_review",
    "success_score": "success_criteria_preparation_review",
    "failure_score": "failure_criteria_preparation_review",
    "audit_score": "audit_preparation_review",
    "go_no_go_score": "go_no_go_preparation_review",
    "abort_score": "abort_preparation_review",
}


def compute_offline_runner_preparation_review_score(data, findings: Mapping[str, Any] | None = None) -> m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewScore:
    data = _coerce_input(data)
    findings = dict(findings or _findings(data))
    prep_score = _metric_score(data.offline_runner_preparation_score, _get(_get(_preparation(data), "score"), "overall_score"), validate_offline_runner_preparation_approval(data))
    scores = {key: _get(value, "score", 0) for key, value in findings.items()}
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewScore(
        overall_score=_average((prep_score, *scores.values())),
        offline_runner_preparation_score=prep_score,
        **{score_field: scores[result_key] for score_field, result_key in _SCORE_MAP.items()},
    )


def detect_offline_runner_preparation_review_risks(data, findings: Mapping[str, Any] | None = None) -> tuple[Risk, ...]:
    data = _coerce_input(data)
    findings = dict(findings or _findings(data))
    risks: list[Risk] = []
    if not validate_offline_runner_preparation_approval(data):
        risks.append(Risk.OFFLINE_RUNNER_PREPARATION_NOT_APPROVED)
    for finding in findings.values():
        risks.extend(_as_tuple(_get(finding, "risks", ())))
    if not _offline_boundary(data):
        risks.append(Risk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(Risk.DATA_ACCESS_VIOLATION)
    if data.paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_plan_requested is True:
        risks.append(Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN)
    return _dedupe(risks)


def generate_offline_runner_preparation_review_recommendations(data, risks: Iterable[Risk] | None = None) -> tuple[Recommendation, ...]:
    risks = tuple(risks if risks is not None else detect_offline_runner_preparation_review_risks(data))
    if not risks:
        return (
            Recommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW_SUITE,
            Recommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN,
        )
    recommendations = [Recommendation.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN]
    recommendations.extend(_RISK_TO_RECOMMENDATION.get(risk, Recommendation.RESTORE_OFFLINE_BOUNDARIES) for risk in risks)
    return _dedupe(recommendations)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW
    blocking = {
        Risk.REAL_EXECUTION_BOUNDARY_VIOLATION,
        Risk.DATA_ACCESS_VIOLATION,
        Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN,
    }
    if any(risk in blocking for risk in risks):
        return Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW
    for risk in risks:
        decision = _RISK_TO_DECISION.get(risk)
        if decision is not None:
            return decision
    return Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW


def _state_for(data, risks: tuple[Risk, ...], score: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewScore):
    if _preparation(data) is None:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewState.OFFLINE_RUNNER_PREPARATION_REVIEW_INPUT_INVALID
    if not risks and score.overall_score >= 85:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN
    if risks:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewState.OFFLINE_RUNNER_PREPARATION_REVIEW_BLOCKED
    if score.overall_score >= 70:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewState.OFFLINE_RUNNER_PREPARATION_REVIEW_COMPLETED_WITH_WARNINGS
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewState.NOT_READY


def render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review_markdown(result) -> str:
    risks = ", ".join(_value(risk) for risk in result.risks) or "none"
    recommendations = ", ".join(_value(recommendation) for recommendation in result.recommendations) or "none"
    return "\n".join((
        "# Paper Broker Read-Only Connection Dry Run Controlled Offline Runner Preparation Review",
        f"- State: {_value(result.state)}",
        f"- Decision: {_value(result.decision)}",
        f"- Score: {result.score.overall_score}",
        f"- Risks: {risks}",
        f"- Recommendations: {recommendations}",
        "- Boundary: offline/sandbox review only; no executable runner creation, no runner execution, no dry-run, no broker connection, no secrets, no network, no orders, no position mutation, no data access.",
        f"- Next phase: {result.next_phase}",
    ))


def evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review(data=None):
    data = _coerce_input(data)
    findings = _findings(data)
    score = compute_offline_runner_preparation_review_score(data, findings)
    risks = detect_offline_runner_preparation_review_risks(data, findings)
    recommendations = generate_offline_runner_preparation_review_recommendations(data, risks)
    result = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewResult(
        state=_state_for(data, risks, score),
        decision=_decision_for(risks),
        score=score,
        review_score=score.overall_score,
        risks=risks,
        recommendations=recommendations,
        summary="Offline runner preparation review approved for final plan" if not risks else "Offline runner preparation review blocked",
        offline_only=True,
        sandbox_only=True,
        review_only=True,
        runner_created=False,
        runner_executed=False,
        dry_run_executed=False,
        findings=tuple(findings.values()),
        **findings,
    )
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationReviewResult(
        **{**result.__dict__, "markdown_report": render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review_markdown(result)}
    )
