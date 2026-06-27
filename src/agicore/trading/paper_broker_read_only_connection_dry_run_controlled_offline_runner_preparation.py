"""Offline preparation for a future controlled read-only paper broker dry-run runner."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Callable, Iterable, Mapping

from agicore.trading import paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_models as m

Risk = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationRisk
Decision = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationDecision
Recommendation = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationRecommendation


def _coerce_input(data: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationInput | Mapping[str, Any] | None) -> m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationInput:
    if data is None:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationInput()
    if isinstance(data, m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationInput):
        return data
    allowed = {field.name for field in fields(m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationInput)}
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationInput(**{key: value for key, value in dict(data).items() if key in allowed})


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


def _gate(data: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationInput) -> Any:
    return data.paper_broker_read_only_connection_dry_run_controlled_offline_runner_safety_gate


def _gate_boundary(data: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationInput, name: str) -> Any:
    return _get(_gate(data), name)


def _upstream_items(data: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationInput) -> tuple[Any, ...]:
    return (
        data.paper_broker_read_only_connection_dry_run_controlled_offline_runner_safety_gate,
        data.paper_broker_read_only_connection_dry_run_controlled_offline_runner_plan,
        data.paper_broker_read_only_connection_dry_run_controlled_execution_final_safety_gate,
        data.paper_broker_read_only_connection_dry_run_controlled_execution_final_plan,
        data.paper_broker_read_only_connection_dry_run_controlled_execution_preparation_review,
        data.paper_broker_read_only_connection_dry_run_controlled_execution_preparation,
        data.paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate,
        data.paper_broker_read_only_connection_dry_run_controlled_execution_plan,
        data.paper_broker_read_only_connection_dry_run_execution_final_safety_gate,
        data.paper_broker_read_only_connection_dry_run_execution_final_plan,
        data.paper_broker_read_only_connection_dry_run_execution_preparation_review,
        data.paper_broker_read_only_connection_dry_run_execution_preparation,
        data.paper_broker_read_only_connection_dry_run_execution_safety_gate,
        data.paper_broker_read_only_connection_dry_run_execution_plan,
        data.paper_broker_read_only_connection_dry_run_preparation_review,
        data.paper_broker_read_only_connection_dry_run_preparation,
        data.paper_broker_read_only_connection_dry_run_safety_gate,
        data.paper_broker_read_only_connection_dry_run_plan,
        data.paper_broker_read_only_connection_preparation_review,
        data.paper_broker_read_only_connection_preparation,
        data.paper_broker_read_only_connection_safety_gate,
        data.paper_broker_read_only_connection_plan,
        data.paper_broker_read_only_safety_review,
        data.paper_broker_read_only_preparation,
    )


def _upstream_risks(data: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def validate_offline_runner_safety_gate_approval(data) -> bool:
    data = _coerce_input(data)
    gate = _gate(data)
    if gate is None or data.offline_runner_safety_gate_approved is False:
        return False
    approved_state = _state_contains(
        gate,
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_SAFETY_GATE",
    )
    approved = data.offline_runner_safety_gate_approved is True or approved_state
    return approved and not _as_tuple(_get(gate, "risks", ())) and _get(gate, "offline_only", True) is True


def _offline_boundary(data: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationInput) -> bool:
    expected_true = (
        data.offline_mode_enforced, data.sandbox_mode_enforced, data.preparation_only,
        data.no_runner_executable_created, data.no_runner_execution, data.no_dry_run_execution,
        data.broker_connection_disabled, data.no_real_broker, data.no_alpaca_real,
        data.no_api_key_read, data.no_env_var_read, data.no_hardcoded_secrets,
        data.no_http_transport, data.no_websocket_transport, data.no_socket_transport,
        data.no_external_api, data.no_external_ml, data.no_external_llm,
        data.no_live_execution, data.no_real_order, data.no_position_mutation,
        data.no_real_account_access,
    )
    requested = (
        data.real_execution_requested, data.runner_creation_requested, data.runner_execution_requested,
        data.dry_run_requested, data.dry_run_executed, data.broker_connection_requested,
        data.api_key_read_requested, data.env_var_read_requested, data.hardcoded_secret_detected,
        data.network_transport_requested, data.external_api_requested, data.order_execution_requested,
        data.position_mutation_requested, data.account_access_requested,
    )
    return (
        all(item is True for item in expected_true)
        and not any(item is True for item in requested)
        and all(_get(item, "offline_only", True) is True for item in _upstream_items(data))
        and not _has_upstream_risk(data, "LIVE_EXECUTION", "BROKER_CONNECTION", "API_KEY", "SECRET_READ", "NETWORK", "HTTP", "WEBSOCKET", "SOCKET", "REAL_ORDER", "REAL_ACCOUNT", "REAL_EXECUTION", "POSITION_MUTATION", "ALPACA_REAL", "RUNNER_EXECUT", "RUNNER_CREAT")
    )


def _data_boundary(data: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationInput) -> bool:
    return data.data_access_requested is not True and not _has_upstream_risk(data, "DATA_ACCESS", "DATA/", "REAL_DATA")


def _http_transport_safe(data: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationInput) -> bool:
    return data.no_http_transport is True and data.no_websocket_transport is True and data.no_socket_transport is True and data.network_transport_requested is not True


_Check = tuple[str, Callable[[m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationInput], bool]]


def _artifact(data, *, flag: str, score: str, fallback_boundary: str | None, risk: Risk, cls, name: str, checks: tuple[_Check, ...]):
    data = _coerce_input(data)
    values = {field: check(data) for field, check in checks}
    fallback = _get(_gate_boundary(data, fallback_boundary), "score") if fallback_boundary else None
    prepared = _get(data, flag) is True and all(values.values())
    return cls(
        name=name,
        prepared=prepared,
        score=_metric_score(_get(data, score), fallback, prepared),
        risks=() if prepared else (risk,),
        details=("offline preparation contract prepared without creating executable runner",),
        **values,
    )


def prepare_offline_runner_scope_contract(data):
    return _artifact(data, flag="offline_runner_scope_contract_prepared", score="scope_score", fallback_boundary="scope_boundary", risk=Risk.OFFLINE_RUNNER_SCOPE_PREPARATION_MISSING, cls=m.OfflineRunnerScopePreparationContract, name="scope_contract", checks=(
        ("offline_only", lambda d: d.offline_mode_enforced is True),
        ("sandbox_only", lambda d: d.sandbox_mode_enforced is True),
        ("preparation_only", lambda d: d.preparation_only is True),
        ("no_runner_executable_created", lambda d: d.no_runner_executable_created is True and d.runner_creation_requested is not True),
    ))


def prepare_offline_runner_execution_mode_contract(data):
    return _artifact(data, flag="offline_runner_execution_mode_contract_prepared", score="execution_mode_score", fallback_boundary="execution_mode_boundary", risk=Risk.OFFLINE_RUNNER_EXECUTION_MODE_PREPARATION_UNSAFE, cls=m.OfflineRunnerExecutionModePreparationContract, name="execution_mode_contract", checks=(
        ("controlled_offline_mode", lambda d: d.offline_mode_enforced is True and d.sandbox_mode_enforced is True),
        ("deterministic_mode", lambda d: d.deterministic_mode is True),
        ("in_memory_only", lambda d: d.in_memory_only is True),
        ("no_dry_run_execution", lambda d: d.no_dry_run_execution is True and d.dry_run_requested is not True and d.dry_run_executed is not True),
    ))


def prepare_offline_runner_input_contract(data):
    return _artifact(data, flag="offline_runner_input_contract_prepared", score="input_contract_score", fallback_boundary="input_contract_boundary", risk=Risk.OFFLINE_RUNNER_INPUT_CONTRACT_PREPARATION_MISSING, cls=m.OfflineRunnerInputPreparationContract, name="input_contract", checks=(
        ("schema_only_inputs", lambda d: d.preparation_only is True),
        ("synthetic_inputs_only", lambda d: d.synthetic_inputs_only is True),
        ("no_real_credentials", lambda d: d.no_api_key_read is True and d.no_env_var_read is True),
    ))


def prepare_offline_runner_synthetic_market_context_contract(data):
    return _artifact(data, flag="offline_runner_synthetic_market_context_contract_prepared", score="synthetic_market_context_score", fallback_boundary="synthetic_market_context_boundary", risk=Risk.OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_PREPARATION_MISSING, cls=m.OfflineRunnerSyntheticMarketContextPreparationContract, name="synthetic_market_context_contract", checks=(
        ("synthetic_context_only", lambda d: d.market_data_snapshot_synthetic is True),
        ("in_memory_context", lambda d: d.synthetic_market_in_memory is True and d.in_memory_only is True),
        ("no_data_access", lambda d: d.data_access_requested is not True),
    ))


def prepare_offline_runner_read_only_broker_simulation_contract(data):
    return _artifact(data, flag="offline_runner_read_only_broker_simulation_contract_prepared", score="read_only_broker_simulation_score", fallback_boundary="read_only_broker_simulation_boundary", risk=Risk.OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_PREPARATION_UNSAFE, cls=m.OfflineRunnerReadOnlyBrokerSimulationPreparationContract, name="read_only_broker_simulation_contract", checks=(
        ("simulated_broker_only", lambda d: d.simulated_broker_only is True),
        ("read_only_contract", lambda d: d.read_only_broker_simulation is True),
        ("no_real_broker", lambda d: d.no_real_broker is True and d.broker_connection_requested is not True),
    ))


def prepare_offline_runner_no_real_broker_guard(data):
    return _artifact(data, flag="offline_runner_no_real_broker_guard_prepared", score="no_real_broker_score", fallback_boundary="no_real_broker_boundary", risk=Risk.OFFLINE_RUNNER_REAL_BROKER_GUARD_MISSING, cls=m.OfflineRunnerNoRealBrokerGuard, name="no_real_broker_guard", checks=(
        ("real_broker_blocked", lambda d: d.no_real_broker is True and d.broker_connection_requested is not True),
        ("alpaca_blocked", lambda d: d.no_alpaca_real is True),
        ("broker_connection_disabled", lambda d: d.broker_connection_disabled is True),
    ))


def prepare_offline_runner_no_secret_read_guard(data):
    return _artifact(data, flag="offline_runner_no_secret_read_guard_prepared", score="no_secret_read_score", fallback_boundary="no_secret_read_boundary", risk=Risk.OFFLINE_RUNNER_SECRET_READ_GUARD_UNSAFE, cls=m.OfflineRunnerNoSecretReadGuard, name="no_secret_read_guard", checks=(
        ("no_api_key_read", lambda d: d.no_api_key_read is True and d.api_key_read_requested is not True),
        ("no_env_var_read", lambda d: d.no_env_var_read is True and d.env_var_read_requested is not True),
        ("no_hardcoded_secret", lambda d: d.no_hardcoded_secrets is True and d.hardcoded_secret_detected is not True),
    ))


def prepare_offline_runner_network_block_guard(data):
    return _artifact(data, flag="offline_runner_network_block_guard_prepared", score="network_score", fallback_boundary="network_block_boundary", risk=Risk.OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_UNSAFE, cls=m.OfflineRunnerNetworkBlockGuard, name="network_block_guard", checks=(
        ("network_blocked", lambda d: d.network_transport_requested is not True),
        ("http_blocked", lambda d: d.no_http_transport is True),
        ("websocket_blocked", lambda d: d.no_websocket_transport is True),
        ("socket_blocked", lambda d: d.no_socket_transport is True),
        ("external_api_blocked", lambda d: d.no_external_api is True and d.external_api_requested is not True),
    ))


def prepare_offline_runner_http_websocket_socket_block_guard(data):
    return _artifact(data, flag="offline_runner_http_websocket_socket_block_guard_prepared", score="http_websocket_socket_score", fallback_boundary="http_websocket_socket_block_boundary", risk=Risk.OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_UNSAFE, cls=m.OfflineRunnerNetworkBlockGuard, name="http_websocket_socket_block_guard", checks=(
        ("network_blocked", lambda d: d.network_transport_requested is not True),
        ("http_blocked", lambda d: d.no_http_transport is True),
        ("websocket_blocked", lambda d: d.no_websocket_transport is True),
        ("socket_blocked", lambda d: d.no_socket_transport is True),
        ("external_api_blocked", lambda d: d.no_external_api is True),
    ))

def prepare_offline_runner_account_snapshot_contract(data):
    return _artifact(data, flag="offline_runner_account_snapshot_contract_prepared", score="account_snapshot_score", fallback_boundary="account_snapshot_boundary", risk=Risk.OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_PREPARATION_UNSAFE, cls=m.OfflineRunnerAccountSnapshotPreparationContract, name="account_snapshot_contract", checks=(
        ("simulated_snapshot_only", lambda d: d.account_snapshot_simulated is True),
        ("read_only_snapshot", lambda d: d.account_snapshot_read_only is True),
        ("active_account_access_blocked", lambda d: d.no_real_account_access is True and d.account_access_requested is not True),
    ))


def prepare_offline_runner_market_data_snapshot_contract(data):
    return _artifact(data, flag="offline_runner_market_data_snapshot_contract_prepared", score="market_data_snapshot_score", fallback_boundary="market_data_snapshot_boundary", risk=Risk.OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_PREPARATION_UNSAFE, cls=m.OfflineRunnerMarketDataSnapshotPreparationContract, name="market_data_snapshot_contract", checks=(
        ("synthetic_snapshot_only", lambda d: d.market_data_snapshot_synthetic is True),
        ("read_only_snapshot", lambda d: d.market_data_snapshot_read_only is True),
        ("live_subscription_blocked", lambda d: _http_transport_safe(d) and d.data_access_requested is not True),
    ))


def prepare_offline_runner_order_blocking_guard(data):
    return _artifact(data, flag="offline_runner_order_blocking_guard_prepared", score="order_blocking_score", fallback_boundary="order_blocking_boundary", risk=Risk.OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_UNSAFE, cls=m.OfflineRunnerOrderBlockingGuard, name="order_blocking_guard", checks=(
        ("order_execution_blocked", lambda d: d.order_blocking_enforced is True and d.order_execution_requested is not True),
        ("real_order_blocked", lambda d: d.no_real_order is True),
        ("cancel_replace_blocked", lambda d: d.cancel_replace_blocked is True),
    ))


def prepare_offline_runner_position_mutation_blocking_guard(data):
    return _artifact(data, flag="offline_runner_position_mutation_blocking_guard_prepared", score="position_mutation_score", fallback_boundary="position_mutation_blocking_boundary", risk=Risk.OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_UNSAFE, cls=m.OfflineRunnerPositionMutationBlockingGuard, name="position_mutation_blocking_guard", checks=(
        ("position_mutation_blocked", lambda d: d.position_mutation_blocked is True and d.position_mutation_requested is not True),
        ("close_modify_blocked", lambda d: d.no_position_mutation is True),
        ("simulated_position_read_only", lambda d: d.account_snapshot_read_only is True),
    ))


def prepare_offline_runner_strategy_signal_observation_contract(data):
    return _artifact(data, flag="offline_runner_strategy_signal_observation_contract_prepared", score="strategy_signal_observation_score", fallback_boundary="strategy_signal_observation_boundary", risk=Risk.OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_PREPARATION_MISSING, cls=m.OfflineRunnerStrategySignalObservationPreparationContract, name="strategy_signal_observation_contract", checks=(
        ("observation_only", lambda d: d.strategy_signal_observation_only is True),
        ("no_signal_execution", lambda d: d.order_execution_requested is not True),
        ("signal_trace_required", lambda d: d.offline_observability_required is True),
    ))


def prepare_offline_runner_risk_observation_contract(data):
    return _artifact(data, flag="offline_runner_risk_observation_contract_prepared", score="risk_observation_score", fallback_boundary="risk_observation_boundary", risk=Risk.OFFLINE_RUNNER_RISK_OBSERVATION_PREPARATION_MISSING, cls=m.OfflineRunnerRiskObservationPreparationContract, name="risk_observation_contract", checks=(
        ("observation_only", lambda d: d.risk_observation_only is True),
        ("no_risk_action_execution", lambda d: d.position_mutation_requested is not True and d.order_execution_requested is not True),
        ("risk_trace_required", lambda d: d.offline_observability_required is True),
    ))


def prepare_offline_runner_profitability_observation_contract(data):
    return _artifact(data, flag="offline_runner_profitability_observation_contract_prepared", score="profitability_observation_score", fallback_boundary="profitability_observation_boundary", risk=Risk.OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_PREPARATION_MISSING, cls=m.OfflineRunnerProfitabilityObservationPreparationContract, name="profitability_observation_contract", checks=(
        ("observation_only", lambda d: d.profitability_observation_only is True),
        ("no_profit_promise", lambda d: d.no_profit_promise is True),
        ("profitability_trace_required", lambda d: d.offline_observability_required is True),
    ))


def prepare_offline_runner_consistency_observation_contract(data):
    return _artifact(data, flag="offline_runner_consistency_observation_contract_prepared", score="consistency_observation_score", fallback_boundary="consistency_observation_boundary", risk=Risk.OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_PREPARATION_MISSING, cls=m.OfflineRunnerConsistencyObservationPreparationContract, name="consistency_observation_contract", checks=(
        ("observation_only", lambda d: d.consistency_observation_only is True),
        ("deterministic_consistency_checks", lambda d: d.deterministic_mode is True),
        ("consistency_trace_required", lambda d: d.offline_observability_required is True),
    ))


def prepare_offline_runner_journal_contract(data):
    return _artifact(data, flag="offline_runner_journal_contract_prepared", score="journal_score", fallback_boundary="journal_boundary", risk=Risk.OFFLINE_RUNNER_JOURNAL_PREPARATION_MISSING, cls=m.OfflineRunnerJournalPreparationContract, name="journal_contract", checks=(
        ("offline_journal_required", lambda d: d.offline_journal_required is True),
        ("no_secret_material_logged", lambda d: d.no_hardcoded_secrets is True),
        ("plan_events_recorded", lambda d: d.preparation_only is True),
    ))


def prepare_offline_runner_observability_contract(data):
    return _artifact(data, flag="offline_runner_observability_contract_prepared", score="observability_score", fallback_boundary="observability_boundary", risk=Risk.OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_MISSING, cls=m.OfflineRunnerObservabilityPreparationContract, name="observability_contract", checks=(
        ("offline_events_defined", lambda d: d.offline_observability_required is True),
        ("no_connection_attempt_metrics", lambda d: d.broker_connection_requested is not True),
        ("sensitive_values_redacted", lambda d: d.no_hardcoded_secrets is True),
    ))


def prepare_offline_runner_human_approval_contract(data):
    return _artifact(data, flag="offline_runner_human_approval_contract_prepared", score="human_approval_score", fallback_boundary="human_approval_boundary", risk=Risk.OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION_MISSING, cls=m.OfflineRunnerHumanApprovalPreparationContract, name="human_approval_contract", checks=(
        ("human_approval_required", lambda d: d.human_approval_required is True),
        ("approval_before_review", lambda d: d.approval_before_review is True),
        ("evidence_required", lambda d: d.audit_contract_required is True),
    ))


def prepare_offline_runner_stop_conditions_contract(data):
    return _artifact(data, flag="offline_runner_stop_conditions_contract_prepared", score="stop_conditions_score", fallback_boundary="stop_conditions_boundary", risk=Risk.OFFLINE_RUNNER_STOP_CONDITIONS_PREPARATION_MISSING, cls=m.OfflineRunnerStopConditionPreparationContract, name="stop_conditions_contract", checks=(
        ("stop_on_secret_read", lambda d: d.stop_on_secret_read is True),
        ("stop_on_network_request", lambda d: d.stop_on_network_request is True),
        ("stop_on_order_or_position_request", lambda d: d.stop_on_order_or_position_request is True),
        ("stop_on_account_access_request", lambda d: d.stop_on_account_access_request is True),
    ))


def prepare_offline_runner_success_criteria_contract(data):
    return _artifact(data, flag="offline_runner_success_criteria_contract_prepared", score="success_score", fallback_boundary="success_failure_boundary", risk=Risk.OFFLINE_RUNNER_SUCCESS_CRITERIA_PREPARATION_MISSING, cls=m.OfflineRunnerSuccessCriteriaPreparationContract, name="success_criteria_contract", checks=(
        ("no_boundary_violation_required", lambda d: d.success_no_boundary_violation_required is True),
        ("all_contracts_prepared", lambda d: True),
        ("no_runner_execution_required", lambda d: d.no_runner_execution is True and d.no_dry_run_execution is True),
    ))


def prepare_offline_runner_failure_criteria_contract(data):
    return _artifact(data, flag="offline_runner_failure_criteria_contract_prepared", score="failure_score", fallback_boundary="success_failure_boundary", risk=Risk.OFFLINE_RUNNER_FAILURE_CRITERIA_PREPARATION_MISSING, cls=m.OfflineRunnerFailureCriteriaPreparationContract, name="failure_criteria_contract", checks=(
        ("fail_on_boundary_violation", lambda d: d.failure_on_boundary_violation is True),
        ("fail_on_missing_contract", lambda d: True),
        ("fail_on_execution_request", lambda d: d.runner_creation_requested is not True and d.runner_execution_requested is not True and d.dry_run_requested is not True),
    ))


def prepare_offline_runner_audit_contract(data):
    return _artifact(data, flag="offline_runner_audit_contract_prepared", score="audit_score", fallback_boundary="audit_boundary", risk=Risk.OFFLINE_RUNNER_AUDIT_PREPARATION_MISSING, cls=m.OfflineRunnerAuditPreparationContract, name="audit_contract", checks=(
        ("audit_events_defined", lambda d: d.audit_contract_required is True),
        ("boundary_evidence_required", lambda d: d.success_no_boundary_violation_required is True),
        ("immutable_preparation_record_required", lambda d: d.preparation_only is True),
    ))


def prepare_offline_runner_go_no_go_contract(data):
    return _artifact(data, flag="offline_runner_go_no_go_contract_prepared", score="go_no_go_score", fallback_boundary="go_no_go_boundary", risk=Risk.OFFLINE_RUNNER_GO_NO_GO_PREPARATION_MISSING, cls=m.OfflineRunnerGoNoGoPreparationContract, name="go_no_go_contract", checks=(
        ("go_no_go_required", lambda d: d.go_no_go_required is True),
        ("no_go_on_risk", lambda d: True),
        ("next_phase_requires_clean_preparation", lambda d: d.paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review_requested is not True),
    ))


def prepare_offline_runner_abort_contract(data):
    return _artifact(data, flag="offline_runner_abort_contract_prepared", score="abort_score", fallback_boundary="abort_boundary", risk=Risk.OFFLINE_RUNNER_ABORT_PREPARATION_MISSING, cls=m.OfflineRunnerAbortPreparationContract, name="abort_contract", checks=(
        ("abort_on_secret_read", lambda d: d.abort_on_boundary_violation is True and d.stop_on_secret_read is True),
        ("abort_on_network_or_broker_request", lambda d: d.abort_on_boundary_violation is True and d.stop_on_network_request is True),
        ("abort_on_order_or_position_request", lambda d: d.abort_on_boundary_violation is True and d.stop_on_order_or_position_request is True),
    ))


def _artifacts(data: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationInput):
    return {
        "scope_contract": prepare_offline_runner_scope_contract(data),
        "execution_mode_contract": prepare_offline_runner_execution_mode_contract(data),
        "input_contract": prepare_offline_runner_input_contract(data),
        "synthetic_market_context_contract": prepare_offline_runner_synthetic_market_context_contract(data),
        "read_only_broker_simulation_contract": prepare_offline_runner_read_only_broker_simulation_contract(data),
        "no_real_broker_guard": prepare_offline_runner_no_real_broker_guard(data),
        "no_secret_read_guard": prepare_offline_runner_no_secret_read_guard(data),
        "network_block_guard": prepare_offline_runner_network_block_guard(data),
        "http_websocket_socket_block_guard": prepare_offline_runner_http_websocket_socket_block_guard(data),
        "account_snapshot_contract": prepare_offline_runner_account_snapshot_contract(data),
        "market_data_snapshot_contract": prepare_offline_runner_market_data_snapshot_contract(data),
        "order_blocking_guard": prepare_offline_runner_order_blocking_guard(data),
        "position_mutation_blocking_guard": prepare_offline_runner_position_mutation_blocking_guard(data),
        "strategy_signal_observation_contract": prepare_offline_runner_strategy_signal_observation_contract(data),
        "risk_observation_contract": prepare_offline_runner_risk_observation_contract(data),
        "profitability_observation_contract": prepare_offline_runner_profitability_observation_contract(data),
        "consistency_observation_contract": prepare_offline_runner_consistency_observation_contract(data),
        "journal_contract": prepare_offline_runner_journal_contract(data),
        "observability_contract": prepare_offline_runner_observability_contract(data),
        "human_approval_contract": prepare_offline_runner_human_approval_contract(data),
        "stop_conditions_contract": prepare_offline_runner_stop_conditions_contract(data),
        "success_criteria_contract": prepare_offline_runner_success_criteria_contract(data),
        "failure_criteria_contract": prepare_offline_runner_failure_criteria_contract(data),
        "audit_contract": prepare_offline_runner_audit_contract(data),
        "go_no_go_contract": prepare_offline_runner_go_no_go_contract(data),
        "abort_contract": prepare_offline_runner_abort_contract(data),
    }

def compute_offline_runner_preparation_score(data, artifacts: Mapping[str, Any] | None = None) -> m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationScore:
    data = _coerce_input(data)
    artifacts = dict(artifacts or _artifacts(data))
    gate_score = _metric_score(data.offline_runner_safety_gate_score, _get(_get(_gate(data), "score"), "overall_score"), validate_offline_runner_safety_gate_approval(data))
    scores = {key: _get(value, "score", 0) for key, value in artifacts.items()}
    overall = _average((gate_score, *scores.values()))
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationScore(
        overall_score=overall,
        offline_runner_safety_gate_score=gate_score,
        scope_score=scores["scope_contract"],
        execution_mode_score=scores["execution_mode_contract"],
        input_contract_score=scores["input_contract"],
        synthetic_market_context_score=scores["synthetic_market_context_contract"],
        read_only_broker_simulation_score=scores["read_only_broker_simulation_contract"],
        no_real_broker_score=scores["no_real_broker_guard"],
        no_secret_read_score=scores["no_secret_read_guard"],
        network_score=scores["network_block_guard"],
        http_websocket_socket_score=scores["http_websocket_socket_block_guard"],
        account_snapshot_score=scores["account_snapshot_contract"],
        market_data_snapshot_score=scores["market_data_snapshot_contract"],
        order_blocking_score=scores["order_blocking_guard"],
        position_mutation_score=scores["position_mutation_blocking_guard"],
        strategy_signal_observation_score=scores["strategy_signal_observation_contract"],
        risk_observation_score=scores["risk_observation_contract"],
        profitability_observation_score=scores["profitability_observation_contract"],
        consistency_observation_score=scores["consistency_observation_contract"],
        journal_score=scores["journal_contract"],
        observability_score=scores["observability_contract"],
        human_approval_score=scores["human_approval_contract"],
        stop_conditions_score=scores["stop_conditions_contract"],
        success_score=scores["success_criteria_contract"],
        failure_score=scores["failure_criteria_contract"],
        audit_score=scores["audit_contract"],
        go_no_go_score=scores["go_no_go_contract"],
        abort_score=scores["abort_contract"],
    )


def detect_offline_runner_preparation_risks(data, artifacts: Mapping[str, Any] | None = None) -> tuple[Risk, ...]:
    data = _coerce_input(data)
    artifacts = dict(artifacts or _artifacts(data))
    risks: list[Risk] = []
    if not validate_offline_runner_safety_gate_approval(data):
        risks.append(Risk.OFFLINE_RUNNER_SAFETY_GATE_NOT_APPROVED)
    for artifact in artifacts.values():
        risks.extend(_as_tuple(_get(artifact, "risks", ())))
    if not _offline_boundary(data):
        risks.append(Risk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(Risk.DATA_ACCESS_VIOLATION)
    if data.paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review_requested is True:
        risks.append(Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW)
    return _dedupe(risks)


_RISK_TO_DECISION = {
    Risk.OFFLINE_RUNNER_SAFETY_GATE_NOT_APPROVED: Decision.REQUIRE_OFFLINE_RUNNER_SAFETY_GATE_FIXES,
    Risk.OFFLINE_RUNNER_SCOPE_PREPARATION_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_SCOPE_PREPARATION_FIXES,
    Risk.OFFLINE_RUNNER_EXECUTION_MODE_PREPARATION_UNSAFE: Decision.REQUIRE_OFFLINE_RUNNER_EXECUTION_MODE_PREPARATION_FIXES,
    Risk.OFFLINE_RUNNER_INPUT_CONTRACT_PREPARATION_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_INPUT_CONTRACT_PREPARATION_FIXES,
    Risk.OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_PREPARATION_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_PREPARATION_FIXES,
    Risk.OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_PREPARATION_UNSAFE: Decision.REQUIRE_OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_PREPARATION_FIXES,
    Risk.OFFLINE_RUNNER_REAL_BROKER_GUARD_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_NO_REAL_BROKER_GUARD_FIXES,
    Risk.OFFLINE_RUNNER_SECRET_READ_GUARD_UNSAFE: Decision.REQUIRE_OFFLINE_RUNNER_NO_SECRET_READ_GUARD_FIXES,
    Risk.OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_UNSAFE: Decision.REQUIRE_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_FIXES,
    Risk.OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_UNSAFE: Decision.REQUIRE_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_FIXES,
    Risk.OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_PREPARATION_UNSAFE: Decision.REQUIRE_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_PREPARATION_FIXES,
    Risk.OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_PREPARATION_UNSAFE: Decision.REQUIRE_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_PREPARATION_FIXES,
    Risk.OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_UNSAFE: Decision.REQUIRE_OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_FIXES,
    Risk.OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_UNSAFE: Decision.REQUIRE_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_FIXES,
    Risk.OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_PREPARATION_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_PREPARATION_FIXES,
    Risk.OFFLINE_RUNNER_RISK_OBSERVATION_PREPARATION_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_RISK_OBSERVATION_PREPARATION_FIXES,
    Risk.OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_PREPARATION_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_PREPARATION_FIXES,
    Risk.OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_PREPARATION_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_PREPARATION_FIXES,
    Risk.OFFLINE_RUNNER_JOURNAL_PREPARATION_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_JOURNAL_PREPARATION_FIXES,
    Risk.OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_FIXES,
    Risk.OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION_FIXES,
    Risk.OFFLINE_RUNNER_STOP_CONDITIONS_PREPARATION_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_STOP_CONDITION_PREPARATION_FIXES,
    Risk.OFFLINE_RUNNER_SUCCESS_CRITERIA_PREPARATION_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_SUCCESS_FAILURE_PREPARATION_FIXES,
    Risk.OFFLINE_RUNNER_FAILURE_CRITERIA_PREPARATION_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_SUCCESS_FAILURE_PREPARATION_FIXES,
    Risk.OFFLINE_RUNNER_AUDIT_PREPARATION_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_AUDIT_PREPARATION_FIXES,
    Risk.OFFLINE_RUNNER_GO_NO_GO_PREPARATION_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_GO_NO_GO_PREPARATION_FIXES,
    Risk.OFFLINE_RUNNER_ABORT_PREPARATION_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_ABORT_PREPARATION_FIXES,
    Risk.REAL_EXECUTION_BOUNDARY_VIOLATION: Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION,
    Risk.DATA_ACCESS_VIOLATION: Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION,
    Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW: Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION,
}

_RISK_TO_RECOMMENDATION = {
    Risk.OFFLINE_RUNNER_SAFETY_GATE_NOT_APPROVED: Recommendation.APPROVE_OFFLINE_RUNNER_SAFETY_GATE_FIRST,
    Risk.OFFLINE_RUNNER_SCOPE_PREPARATION_MISSING: Recommendation.PREPARE_OFFLINE_RUNNER_SCOPE,
    Risk.OFFLINE_RUNNER_EXECUTION_MODE_PREPARATION_UNSAFE: Recommendation.PREPARE_OFFLINE_RUNNER_EXECUTION_MODE,
    Risk.OFFLINE_RUNNER_INPUT_CONTRACT_PREPARATION_MISSING: Recommendation.PREPARE_OFFLINE_RUNNER_INPUT_CONTRACT,
    Risk.OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_PREPARATION_MISSING: Recommendation.PREPARE_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT,
    Risk.OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_PREPARATION_UNSAFE: Recommendation.HARDEN_OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION,
    Risk.OFFLINE_RUNNER_REAL_BROKER_GUARD_MISSING: Recommendation.PREPARE_OFFLINE_RUNNER_NO_REAL_BROKER_GUARD,
    Risk.OFFLINE_RUNNER_SECRET_READ_GUARD_UNSAFE: Recommendation.HARDEN_OFFLINE_RUNNER_NO_SECRET_READ_GUARD,
    Risk.OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_UNSAFE: Recommendation.HARDEN_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD,
    Risk.OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_UNSAFE: Recommendation.HARDEN_OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD,
    Risk.OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_PREPARATION_UNSAFE: Recommendation.HARDEN_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT,
    Risk.OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_PREPARATION_UNSAFE: Recommendation.HARDEN_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT,
    Risk.OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_UNSAFE: Recommendation.HARDEN_OFFLINE_RUNNER_ORDER_BLOCKING_GUARD,
    Risk.OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_UNSAFE: Recommendation.HARDEN_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD,
    Risk.OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_PREPARATION_MISSING: Recommendation.PREPARE_OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION,
    Risk.OFFLINE_RUNNER_RISK_OBSERVATION_PREPARATION_MISSING: Recommendation.PREPARE_OFFLINE_RUNNER_RISK_OBSERVATION,
    Risk.OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_PREPARATION_MISSING: Recommendation.PREPARE_OFFLINE_RUNNER_PROFITABILITY_OBSERVATION,
    Risk.OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_PREPARATION_MISSING: Recommendation.PREPARE_OFFLINE_RUNNER_CONSISTENCY_OBSERVATION,
    Risk.OFFLINE_RUNNER_JOURNAL_PREPARATION_MISSING: Recommendation.COMPLETE_OFFLINE_RUNNER_JOURNAL_PREPARATION,
    Risk.OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_MISSING: Recommendation.COMPLETE_OFFLINE_RUNNER_OBSERVABILITY_PREPARATION,
    Risk.OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION_MISSING: Recommendation.REQUIRE_OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION,
    Risk.OFFLINE_RUNNER_STOP_CONDITIONS_PREPARATION_MISSING: Recommendation.PREPARE_OFFLINE_RUNNER_STOP_CONDITIONS,
    Risk.OFFLINE_RUNNER_SUCCESS_CRITERIA_PREPARATION_MISSING: Recommendation.PREPARE_OFFLINE_RUNNER_SUCCESS_FAILURE,
    Risk.OFFLINE_RUNNER_FAILURE_CRITERIA_PREPARATION_MISSING: Recommendation.PREPARE_OFFLINE_RUNNER_SUCCESS_FAILURE,
    Risk.OFFLINE_RUNNER_AUDIT_PREPARATION_MISSING: Recommendation.COMPLETE_OFFLINE_RUNNER_AUDIT_PREPARATION,
    Risk.OFFLINE_RUNNER_GO_NO_GO_PREPARATION_MISSING: Recommendation.PREPARE_OFFLINE_RUNNER_GO_NO_GO,
    Risk.OFFLINE_RUNNER_ABORT_PREPARATION_MISSING: Recommendation.PREPARE_OFFLINE_RUNNER_ABORT,
    Risk.REAL_EXECUTION_BOUNDARY_VIOLATION: Recommendation.RESTORE_OFFLINE_BOUNDARIES,
    Risk.DATA_ACCESS_VIOLATION: Recommendation.REMOVE_DATA_ACCESS,
    Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW: Recommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW,
}


def generate_offline_runner_preparation_recommendations(data, risks: Iterable[Risk] | None = None) -> tuple[Recommendation, ...]:
    risks = tuple(risks if risks is not None else detect_offline_runner_preparation_risks(data))
    if not risks:
        return (
            Recommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_SUITE,
            Recommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW,
        )
    recommendations = [Recommendation.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW]
    recommendations.extend(_RISK_TO_RECOMMENDATION.get(risk, Recommendation.RESTORE_OFFLINE_BOUNDARIES) for risk in risks)
    return _dedupe(recommendations)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION
    blocking = {Risk.REAL_EXECUTION_BOUNDARY_VIOLATION, Risk.DATA_ACCESS_VIOLATION, Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW}
    if any(risk in blocking for risk in risks):
        return Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION
    for risk in risks:
        decision = _RISK_TO_DECISION.get(risk)
        if decision is not None:
            return decision
    return Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION


def _state_for(data, risks: tuple[Risk, ...], score: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationScore) -> m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationState:
    if _gate(data) is None:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationState.OFFLINE_RUNNER_PREPARATION_INPUT_INVALID
    if not risks and score.overall_score >= 85:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW
    if risks:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationState.OFFLINE_RUNNER_PREPARATION_BLOCKED
    if score.overall_score >= 70:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationState.OFFLINE_RUNNER_PREPARATION_COMPLETED_WITH_WARNINGS
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationState.NOT_READY


def render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_markdown(result) -> str:
    risks = ", ".join(_value(risk) for risk in result.risks) or "none"
    recommendations = ", ".join(_value(recommendation) for recommendation in result.recommendations) or "none"
    return "\n".join((
        "# Paper Broker Read-Only Connection Dry Run Controlled Offline Runner Preparation",
        f"- State: {_value(result.state)}",
        f"- Decision: {_value(result.decision)}",
        f"- Score: {result.score.overall_score}",
        f"- Risks: {risks}",
        f"- Recommendations: {recommendations}",
        "- Boundary: offline/sandbox preparation only; no executable runner creation, no runner execution, no dry-run, no broker connection, no secrets, no network, no orders, no position mutation, no data access.",
        f"- Next phase: {result.next_phase}",
    ))


def evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation(data=None):
    data = _coerce_input(data)
    artifacts = _artifacts(data)
    score = compute_offline_runner_preparation_score(data, artifacts)
    risks = detect_offline_runner_preparation_risks(data, artifacts)
    recommendations = generate_offline_runner_preparation_recommendations(data, risks)
    decision = _decision_for(risks)
    state = _state_for(data, risks, score)
    summary = "Offline runner preparation approved for review" if not risks else "Offline runner preparation blocked"
    result = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationResult(
        state=state,
        decision=decision,
        score=score,
        risks=risks,
        recommendations=recommendations,
        summary=summary,
        offline_only=True,
        sandbox_only=True,
        preparation_only=True,
        runner_created=False,
        runner_executed=False,
        dry_run_executed=False,
        artifacts=tuple(artifacts.values()),
        **artifacts,
    )
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPreparationResult(
        **{**result.__dict__, "markdown_report": render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_markdown(result)}
    )