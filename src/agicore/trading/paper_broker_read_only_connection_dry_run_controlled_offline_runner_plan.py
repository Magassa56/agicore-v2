"""Offline plan for a future controlled read-only paper broker dry-run runner."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Callable, Iterable, Mapping

from agicore.trading import paper_broker_read_only_connection_dry_run_controlled_offline_runner_plan_models as m

Risk = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPlanRisk
Decision = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPlanDecision
Recommendation = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPlanRecommendation


def _coerce_input(data: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPlanInput | Mapping[str, Any] | None) -> m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPlanInput:
    if data is None:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPlanInput()
    if isinstance(data, m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPlanInput):
        return data
    allowed = {field.name for field in fields(m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPlanInput)}
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPlanInput(**{key: value for key, value in dict(data).items() if key in allowed})


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


def _gate(data: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPlanInput) -> Any:
    return data.paper_broker_read_only_connection_dry_run_controlled_execution_final_safety_gate


def _upstream_items(data: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPlanInput) -> tuple[Any, ...]:
    return (
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


def _upstream_risks(data: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPlanInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPlanInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def validate_final_safety_gate_approval(data: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPlanInput | Mapping[str, Any] | None) -> bool:
    data = _coerce_input(data)
    gate = _gate(data)
    if gate is None or data.final_safety_gate_approved is False:
        return False
    approved_state = _state_contains(
        gate,
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PLAN",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_SAFETY_GATE",
    )
    approved = data.final_safety_gate_approved is True or approved_state
    return approved and not _as_tuple(_get(gate, "risks", ())) and _get(gate, "offline_only", True) is True


def _offline_boundary(data: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPlanInput) -> bool:
    expected_true = (
        data.offline_mode_enforced, data.sandbox_mode_enforced, data.plan_only,
        data.runner_plan_only, data.no_runner_execution, data.no_dry_run_execution,
        data.broker_connection_disabled, data.no_real_broker, data.no_alpaca_real,
        data.no_api_key_read, data.no_env_var_read, data.no_hardcoded_secrets,
        data.no_http_transport, data.no_websocket_transport, data.no_socket_transport,
        data.no_external_api, data.no_external_ml, data.no_external_llm,
        data.no_live_execution, data.no_real_order, data.no_position_mutation,
    )
    requested = (
        data.real_execution_requested, data.broker_connection_requested, data.api_key_read_requested,
        data.env_var_read_requested, data.hardcoded_secret_detected, data.order_execution_requested,
        data.position_mutation_requested, data.account_access_requested, data.network_transport_requested,
        data.external_api_requested, data.dry_run_requested, data.dry_run_executed,
        data.runner_requested, data.runner_executed,
    )
    return (
        all(item is True for item in expected_true)
        and not any(item is True for item in requested)
        and all(_get(item, "offline_only", True) is True for item in _upstream_items(data))
        and not _has_upstream_risk(data, "LIVE_EXECUTION", "BROKER_CONNECTION", "API_KEY", "SECRET_READ", "NETWORK", "HTTP", "WEBSOCKET", "SOCKET", "REAL_ORDER", "REAL_ACCOUNT", "REAL_EXECUTION", "POSITION_MUTATION", "ALPACA_REAL")
    )


def _data_boundary(data: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPlanInput) -> bool:
    return data.data_access_requested is not True and not _has_upstream_risk(data, "DATA_ACCESS", "DATA/", "REAL_DATA")


def _http_transport_safe(data: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPlanInput) -> bool:
    return data.no_http_transport is True and data.no_websocket_transport is True and data.no_socket_transport is True and data.network_transport_requested is not True


_Check = tuple[str, Callable[[m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPlanInput], bool]]


def _section(data, *, flag: str, score: str, risk: Risk, cls, checks: tuple[_Check, ...], name: str, fallback: Any = None):
    data = _coerce_input(data)
    values = {field: check(data) for field, check in checks}
    passed = _get(data, flag) is True and all(values.values())
    return cls(
        name=name,
        defined=passed,
        score=_metric_score(_get(data, score), fallback, passed),
        risks=() if passed else (risk,),
        details=("offline runner plan section validated without executing runner",),
        **values,
    )


def define_offline_runner_scope(data):
    return _section(data, flag="offline_runner_scope_defined", score="scope_score", risk=Risk.OFFLINE_RUNNER_SCOPE_UNCLEAR, cls=m.OfflineRunnerScope, name="offline_runner_scope", checks=(
        ("offline_only", lambda d: d.offline_mode_enforced is True),
        ("sandbox_only", lambda d: d.sandbox_mode_enforced is True),
        ("plan_only", lambda d: d.plan_only is True and d.runner_plan_only is True),
        ("no_runner_execution", lambda d: d.no_runner_execution is True and d.runner_executed is not True and d.runner_requested is not True),
    ))


def define_offline_runner_execution_mode(data):
    return _section(data, flag="offline_runner_execution_mode_defined", score="execution_mode_score", risk=Risk.OFFLINE_RUNNER_EXECUTION_MODE_UNSAFE, cls=m.OfflineRunnerExecutionMode, name="offline_runner_execution_mode", checks=(
        ("controlled_offline_mode", lambda d: d.offline_mode_enforced is True and d.sandbox_mode_enforced is True),
        ("deterministic_mode", lambda d: d.deterministic_mode is True),
        ("in_memory_only", lambda d: d.in_memory_only is True),
        ("no_dry_run_execution", lambda d: d.no_dry_run_execution is True and d.dry_run_executed is not True and d.dry_run_requested is not True),
    ))


def define_offline_runner_input_contract(data):
    return _section(data, flag="offline_runner_input_contract_defined", score="input_contract_score", risk=Risk.OFFLINE_RUNNER_INPUT_CONTRACT_MISSING, cls=m.OfflineRunnerInputContract, name="offline_runner_input_contract", checks=(
        ("schema_only_inputs", lambda d: d.plan_only is True),
        ("synthetic_inputs_only", lambda d: d.synthetic_inputs_only is True),
        ("no_real_credentials", lambda d: d.no_api_key_read is True and d.no_env_var_read is True),
    ))


def define_offline_runner_synthetic_market_context(data):
    return _section(data, flag="offline_runner_synthetic_market_context_defined", score="synthetic_market_context_score", risk=Risk.OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_MISSING, cls=m.OfflineRunnerSyntheticMarketContext, name="offline_runner_synthetic_market_context", checks=(
        ("synthetic_context_only", lambda d: d.market_data_snapshot_synthetic is True),
        ("in_memory_context", lambda d: d.synthetic_market_in_memory is True and d.in_memory_only is True),
        ("no_data_directory_access", lambda d: d.data_access_requested is not True),
    ))


def define_offline_runner_read_only_broker_simulation_contract(data):
    return _section(data, flag="offline_runner_read_only_broker_simulation_contract_defined", score="read_only_broker_simulation_score", risk=Risk.OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_UNSAFE, cls=m.OfflineRunnerReadOnlyBrokerSimulationContract, name="offline_runner_read_only_broker_simulation_contract", checks=(
        ("simulated_broker_only", lambda d: d.simulated_broker_only is True),
        ("read_only_contract", lambda d: d.read_only_broker_simulation is True),
        ("no_real_broker", lambda d: d.no_real_broker is True and d.broker_connection_requested is not True),
    ))


def define_offline_runner_no_real_broker_policy(data):
    return _section(data, flag="offline_runner_no_real_broker_policy_defined", score="no_real_broker_score", risk=Risk.OFFLINE_RUNNER_REAL_BROKER_BOUNDARY_VIOLATION, cls=m.OfflineRunnerNoRealBrokerPolicy, name="offline_runner_no_real_broker_policy", checks=(
        ("real_broker_blocked", lambda d: d.no_real_broker is True and d.broker_connection_requested is not True),
        ("alpaca_blocked", lambda d: d.no_alpaca_real is True),
        ("broker_connection_disabled", lambda d: d.broker_connection_disabled is True),
    ))


def define_offline_runner_no_secret_read_policy(data):
    return _section(data, flag="offline_runner_no_secret_read_policy_defined", score="no_secret_read_score", risk=Risk.OFFLINE_RUNNER_SECRET_READ_POLICY_UNSAFE, cls=m.OfflineRunnerNoSecretReadPolicy, name="offline_runner_no_secret_read_policy", checks=(
        ("no_api_key_read", lambda d: d.no_api_key_read is True and d.api_key_read_requested is not True),
        ("no_env_var_read", lambda d: d.no_env_var_read is True and d.env_var_read_requested is not True),
        ("no_hardcoded_secret", lambda d: d.no_hardcoded_secrets is True and d.hardcoded_secret_detected is not True),
    ))


def define_offline_runner_network_block_policy(data):
    return _section(data, flag="offline_runner_network_block_policy_defined", score="network_score", risk=Risk.OFFLINE_RUNNER_NETWORK_NOT_BLOCKED, cls=m.OfflineRunnerNetworkBlockPolicy, name="offline_runner_network_block_policy", checks=(
        ("network_blocked", lambda d: d.network_transport_requested is not True),
        ("http_blocked", lambda d: d.no_http_transport is True),
        ("websocket_blocked", lambda d: d.no_websocket_transport is True),
        ("socket_blocked", lambda d: d.no_socket_transport is True),
        ("external_api_blocked", lambda d: d.no_external_api is True and d.external_api_requested is not True),
    ))


def define_offline_runner_http_websocket_socket_block_policy(data):
    return _section(data, flag="offline_runner_http_websocket_socket_block_policy_defined", score="http_websocket_socket_score", risk=Risk.OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED, cls=m.OfflineRunnerNetworkBlockPolicy, name="offline_runner_http_websocket_socket_block_policy", checks=(
        ("network_blocked", lambda d: d.network_transport_requested is not True),
        ("http_blocked", lambda d: d.no_http_transport is True),
        ("websocket_blocked", lambda d: d.no_websocket_transport is True),
        ("socket_blocked", lambda d: d.no_socket_transport is True),
        ("external_api_blocked", lambda d: d.no_external_api is True),
    ))


def define_offline_runner_account_snapshot_contract(data):
    return _section(data, flag="offline_runner_account_snapshot_contract_defined", score="account_snapshot_score", risk=Risk.OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_UNSAFE, cls=m.OfflineRunnerAccountSnapshotContract, name="offline_runner_account_snapshot_contract", checks=(
        ("simulated_snapshot_only", lambda d: d.account_snapshot_simulated is True),
        ("read_only_snapshot", lambda d: d.account_snapshot_read_only is True),
        ("active_account_access_blocked", lambda d: d.no_real_account_access is True and d.account_access_requested is not True),
    ))


def define_offline_runner_market_data_snapshot_contract(data):
    return _section(data, flag="offline_runner_market_data_snapshot_contract_defined", score="market_data_snapshot_score", risk=Risk.OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_UNSAFE, cls=m.OfflineRunnerMarketDataSnapshotContract, name="offline_runner_market_data_snapshot_contract", checks=(
        ("synthetic_snapshot_only", lambda d: d.market_data_snapshot_synthetic is True),
        ("read_only_snapshot", lambda d: d.market_data_snapshot_read_only is True),
        ("live_subscription_blocked", lambda d: _http_transport_safe(d) and d.data_access_requested is not True),
    ))


def define_offline_runner_order_blocking_contract(data):
    return _section(data, flag="offline_runner_order_blocking_contract_defined", score="order_blocking_score", risk=Risk.OFFLINE_RUNNER_ORDER_BLOCKING_UNSAFE, cls=m.OfflineRunnerOrderBlockingContract, name="offline_runner_order_blocking_contract", checks=(
        ("order_execution_blocked", lambda d: d.order_blocking_enforced is True and d.order_execution_requested is not True),
        ("real_order_blocked", lambda d: d.no_real_order is True),
        ("cancel_replace_blocked", lambda d: d.cancel_replace_blocked is True),
    ))


def define_offline_runner_position_mutation_blocking_contract(data):
    return _section(data, flag="offline_runner_position_mutation_blocking_contract_defined", score="position_mutation_score", risk=Risk.OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_UNSAFE, cls=m.OfflineRunnerPositionMutationBlockingContract, name="offline_runner_position_mutation_blocking_contract", checks=(
        ("position_mutation_blocked", lambda d: d.position_mutation_blocked is True and d.position_mutation_requested is not True),
        ("close_modify_blocked", lambda d: d.no_position_mutation is True),
        ("simulated_position_read_only", lambda d: d.account_snapshot_read_only is True),
    ))


def define_offline_runner_strategy_signal_observation_contract(data):
    return _section(data, flag="offline_runner_strategy_signal_observation_contract_defined", score="strategy_signal_observation_score", risk=Risk.OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_MISSING, cls=m.OfflineRunnerStrategySignalObservationContract, name="offline_runner_strategy_signal_observation_contract", checks=(
        ("observation_only", lambda d: d.strategy_signal_observation_only is True),
        ("no_signal_execution", lambda d: d.order_execution_requested is not True),
        ("signal_trace_required", lambda d: d.offline_observability_required is True),
    ))


def define_offline_runner_risk_observation_contract(data):
    return _section(data, flag="offline_runner_risk_observation_contract_defined", score="risk_observation_score", risk=Risk.OFFLINE_RUNNER_RISK_OBSERVATION_MISSING, cls=m.OfflineRunnerRiskObservationContract, name="offline_runner_risk_observation_contract", checks=(
        ("observation_only", lambda d: d.risk_observation_only is True),
        ("no_risk_action_execution", lambda d: d.position_mutation_requested is not True and d.order_execution_requested is not True),
        ("risk_trace_required", lambda d: d.offline_observability_required is True),
    ))


def define_offline_runner_profitability_observation_contract(data):
    return _section(data, flag="offline_runner_profitability_observation_contract_defined", score="profitability_observation_score", risk=Risk.OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_MISSING, cls=m.OfflineRunnerProfitabilityObservationContract, name="offline_runner_profitability_observation_contract", checks=(
        ("observation_only", lambda d: d.profitability_observation_only is True),
        ("no_profit_promise", lambda d: d.no_profit_promise is True),
        ("profitability_trace_required", lambda d: d.offline_observability_required is True),
    ))


def define_offline_runner_consistency_observation_contract(data):
    return _section(data, flag="offline_runner_consistency_observation_contract_defined", score="consistency_observation_score", risk=Risk.OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_MISSING, cls=m.OfflineRunnerConsistencyObservationContract, name="offline_runner_consistency_observation_contract", checks=(
        ("observation_only", lambda d: d.consistency_observation_only is True),
        ("deterministic_consistency_checks", lambda d: d.deterministic_mode is True),
        ("consistency_trace_required", lambda d: d.offline_observability_required is True),
    ))


def define_offline_runner_journal_contract(data):
    return _section(data, flag="offline_runner_journal_contract_defined", score="journal_score", risk=Risk.OFFLINE_RUNNER_JOURNAL_MISSING, cls=m.OfflineRunnerJournalContract, name="offline_runner_journal_contract", checks=(
        ("offline_journal_required", lambda d: d.offline_journal_required is True),
        ("no_secret_material_logged", lambda d: d.no_hardcoded_secrets is True),
        ("plan_events_recorded", lambda d: d.plan_only is True),
    ))


def define_offline_runner_observability_contract(data):
    return _section(data, flag="offline_runner_observability_contract_defined", score="observability_score", risk=Risk.OFFLINE_RUNNER_OBSERVABILITY_MISSING, cls=m.OfflineRunnerObservabilityContract, name="offline_runner_observability_contract", checks=(
        ("offline_events_defined", lambda d: d.offline_observability_required is True),
        ("no_connection_attempt_metrics", lambda d: d.broker_connection_requested is not True),
        ("sensitive_values_redacted", lambda d: d.no_hardcoded_secrets is True),
    ))


def define_offline_runner_human_approval_contract(data):
    return _section(data, flag="offline_runner_human_approval_contract_defined", score="human_approval_score", risk=Risk.OFFLINE_RUNNER_HUMAN_APPROVAL_MISSING, cls=m.OfflineRunnerHumanApprovalContract, name="offline_runner_human_approval_contract", checks=(
        ("human_approval_required", lambda d: d.human_approval_required is True),
        ("approval_before_safety_gate", lambda d: d.approval_before_safety_gate is True),
        ("evidence_required", lambda d: d.audit_contract_required is True),
    ))


def define_offline_runner_stop_conditions(data):
    return _section(data, flag="offline_runner_stop_conditions_defined", score="stop_conditions_score", risk=Risk.OFFLINE_RUNNER_STOP_CONDITIONS_MISSING, cls=m.OfflineRunnerStopCondition, name="offline_runner_stop_conditions", checks=(
        ("stop_on_secret_read", lambda d: d.stop_on_secret_read is True),
        ("stop_on_network_request", lambda d: d.stop_on_network_request is True),
        ("stop_on_order_or_position_request", lambda d: d.stop_on_order_or_position_request is True),
        ("stop_on_account_access_request", lambda d: d.stop_on_account_access_request is True),
    ))


def define_offline_runner_success_criteria(data):
    return _section(data, flag="offline_runner_success_criteria_defined", score="success_score", risk=Risk.OFFLINE_RUNNER_SUCCESS_CRITERIA_MISSING, cls=m.OfflineRunnerSuccessCriteria, name="offline_runner_success_criteria", checks=(
        ("no_boundary_violation_required", lambda d: d.success_no_boundary_violation_required is True),
        ("all_contracts_defined", lambda d: True),
        ("no_runner_execution_required", lambda d: d.no_runner_execution is True and d.no_dry_run_execution is True),
    ))


def define_offline_runner_failure_criteria(data):
    return _section(data, flag="offline_runner_failure_criteria_defined", score="failure_score", risk=Risk.OFFLINE_RUNNER_FAILURE_CRITERIA_MISSING, cls=m.OfflineRunnerFailureCriteria, name="offline_runner_failure_criteria", checks=(
        ("fail_on_boundary_violation", lambda d: d.failure_on_boundary_violation is True),
        ("fail_on_missing_contract", lambda d: True),
        ("fail_on_execution_request", lambda d: d.runner_requested is not True and d.dry_run_requested is not True),
    ))


def define_offline_runner_audit_contract(data):
    return _section(data, flag="offline_runner_audit_contract_defined", score="audit_score", risk=Risk.OFFLINE_RUNNER_AUDIT_CONTRACT_MISSING, cls=m.OfflineRunnerAuditContract, name="offline_runner_audit_contract", checks=(
        ("audit_events_defined", lambda d: d.audit_contract_required is True),
        ("boundary_evidence_required", lambda d: d.success_no_boundary_violation_required is True),
        ("immutable_plan_record_required", lambda d: d.plan_only is True),
    ))


def define_offline_runner_go_no_go_contract(data):
    return _section(data, flag="offline_runner_go_no_go_contract_defined", score="go_no_go_score", risk=Risk.OFFLINE_RUNNER_GO_NO_GO_CONTRACT_MISSING, cls=m.OfflineRunnerGoNoGoContract, name="offline_runner_go_no_go_contract", checks=(
        ("go_no_go_required", lambda d: d.go_no_go_required is True),
        ("no_go_on_risk", lambda d: True),
        ("next_phase_requires_clean_plan", lambda d: d.paper_broker_read_only_connection_dry_run_controlled_offline_runner_safety_gate_requested is not True),
    ))


def define_offline_runner_abort_contract(data):
    return _section(data, flag="offline_runner_abort_contract_defined", score="abort_score", risk=Risk.OFFLINE_RUNNER_ABORT_CONTRACT_MISSING, cls=m.OfflineRunnerAbortContract, name="offline_runner_abort_contract", checks=(
        ("abort_on_secret_read", lambda d: d.abort_on_boundary_violation is True and d.stop_on_secret_read is True),
        ("abort_on_network_or_broker_request", lambda d: d.abort_on_boundary_violation is True and d.stop_on_network_request is True),
        ("abort_on_order_or_position_request", lambda d: d.abort_on_boundary_violation is True and d.stop_on_order_or_position_request is True),
    ))


def _sections(data: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPlanInput):
    return {
        "offline_runner_scope": define_offline_runner_scope(data),
        "offline_runner_execution_mode": define_offline_runner_execution_mode(data),
        "offline_runner_input_contract": define_offline_runner_input_contract(data),
        "offline_runner_synthetic_market_context": define_offline_runner_synthetic_market_context(data),
        "offline_runner_read_only_broker_simulation_contract": define_offline_runner_read_only_broker_simulation_contract(data),
        "offline_runner_no_real_broker_policy": define_offline_runner_no_real_broker_policy(data),
        "offline_runner_no_secret_read_policy": define_offline_runner_no_secret_read_policy(data),
        "offline_runner_network_block_policy": define_offline_runner_network_block_policy(data),
        "offline_runner_http_websocket_socket_block_policy": define_offline_runner_http_websocket_socket_block_policy(data),
        "offline_runner_account_snapshot_contract": define_offline_runner_account_snapshot_contract(data),
        "offline_runner_market_data_snapshot_contract": define_offline_runner_market_data_snapshot_contract(data),
        "offline_runner_order_blocking_contract": define_offline_runner_order_blocking_contract(data),
        "offline_runner_position_mutation_blocking_contract": define_offline_runner_position_mutation_blocking_contract(data),
        "offline_runner_strategy_signal_observation_contract": define_offline_runner_strategy_signal_observation_contract(data),
        "offline_runner_risk_observation_contract": define_offline_runner_risk_observation_contract(data),
        "offline_runner_profitability_observation_contract": define_offline_runner_profitability_observation_contract(data),
        "offline_runner_consistency_observation_contract": define_offline_runner_consistency_observation_contract(data),
        "offline_runner_journal_contract": define_offline_runner_journal_contract(data),
        "offline_runner_observability_contract": define_offline_runner_observability_contract(data),
        "offline_runner_human_approval_contract": define_offline_runner_human_approval_contract(data),
        "offline_runner_stop_conditions": define_offline_runner_stop_conditions(data),
        "offline_runner_success_criteria": define_offline_runner_success_criteria(data),
        "offline_runner_failure_criteria": define_offline_runner_failure_criteria(data),
        "offline_runner_audit_contract": define_offline_runner_audit_contract(data),
        "offline_runner_go_no_go_contract": define_offline_runner_go_no_go_contract(data),
        "offline_runner_abort_contract": define_offline_runner_abort_contract(data),
    }


def compute_offline_runner_plan_score(data, sections: Mapping[str, Any] | None = None) -> m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPlanScore:
    data = _coerce_input(data)
    sections = dict(sections or _sections(data))
    gate_score = _metric_score(data.final_safety_gate_score, _get(_get(_gate(data), "score"), "overall_score"), validate_final_safety_gate_approval(data))
    section_scores = {key: _get(value, "score", 0) for key, value in sections.items()}
    overall = _average((gate_score, *section_scores.values()))
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPlanScore(
        overall_score=overall,
        final_safety_gate_score=gate_score,
        scope_score=section_scores["offline_runner_scope"],
        execution_mode_score=section_scores["offline_runner_execution_mode"],
        input_contract_score=section_scores["offline_runner_input_contract"],
        synthetic_market_context_score=section_scores["offline_runner_synthetic_market_context"],
        read_only_broker_simulation_score=section_scores["offline_runner_read_only_broker_simulation_contract"],
        no_real_broker_score=section_scores["offline_runner_no_real_broker_policy"],
        no_secret_read_score=section_scores["offline_runner_no_secret_read_policy"],
        network_score=section_scores["offline_runner_network_block_policy"],
        http_websocket_socket_score=section_scores["offline_runner_http_websocket_socket_block_policy"],
        account_snapshot_score=section_scores["offline_runner_account_snapshot_contract"],
        market_data_snapshot_score=section_scores["offline_runner_market_data_snapshot_contract"],
        order_blocking_score=section_scores["offline_runner_order_blocking_contract"],
        position_mutation_score=section_scores["offline_runner_position_mutation_blocking_contract"],
        strategy_signal_observation_score=section_scores["offline_runner_strategy_signal_observation_contract"],
        risk_observation_score=section_scores["offline_runner_risk_observation_contract"],
        profitability_observation_score=section_scores["offline_runner_profitability_observation_contract"],
        consistency_observation_score=section_scores["offline_runner_consistency_observation_contract"],
        journal_score=section_scores["offline_runner_journal_contract"],
        observability_score=section_scores["offline_runner_observability_contract"],
        human_approval_score=section_scores["offline_runner_human_approval_contract"],
        stop_conditions_score=section_scores["offline_runner_stop_conditions"],
        success_score=section_scores["offline_runner_success_criteria"],
        failure_score=section_scores["offline_runner_failure_criteria"],
        audit_score=section_scores["offline_runner_audit_contract"],
        go_no_go_score=section_scores["offline_runner_go_no_go_contract"],
        abort_score=section_scores["offline_runner_abort_contract"],
    )


def detect_offline_runner_plan_risks(data, sections: Mapping[str, Any] | None = None) -> tuple[Risk, ...]:
    data = _coerce_input(data)
    sections = dict(sections or _sections(data))
    risks: list[Risk] = []
    if not validate_final_safety_gate_approval(data):
        risks.append(Risk.FINAL_SAFETY_GATE_NOT_APPROVED)
    for section in sections.values():
        risks.extend(_as_tuple(_get(section, "risks", ())))
    if not _offline_boundary(data):
        risks.append(Risk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(Risk.DATA_ACCESS_VIOLATION)
    if data.paper_broker_read_only_connection_dry_run_controlled_offline_runner_safety_gate_requested is True:
        risks.append(Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_SAFETY_GATE)
    return _dedupe(risks)


_RISK_TO_DECISION = {
    Risk.FINAL_SAFETY_GATE_NOT_APPROVED: Decision.REQUIRE_FINAL_SAFETY_GATE_FIXES,
    Risk.OFFLINE_RUNNER_SCOPE_UNCLEAR: Decision.REQUIRE_OFFLINE_RUNNER_SCOPE_FIXES,
    Risk.OFFLINE_RUNNER_EXECUTION_MODE_UNSAFE: Decision.REQUIRE_OFFLINE_RUNNER_EXECUTION_MODE_FIXES,
    Risk.OFFLINE_RUNNER_INPUT_CONTRACT_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_INPUT_CONTRACT_FIXES,
    Risk.OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_FIXES,
    Risk.OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_UNSAFE: Decision.REQUIRE_OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_FIXES,
    Risk.OFFLINE_RUNNER_REAL_BROKER_BOUNDARY_VIOLATION: Decision.REQUIRE_OFFLINE_RUNNER_NO_REAL_BROKER_FIXES,
    Risk.OFFLINE_RUNNER_SECRET_READ_POLICY_UNSAFE: Decision.REQUIRE_OFFLINE_RUNNER_NO_SECRET_READ_FIXES,
    Risk.OFFLINE_RUNNER_NETWORK_NOT_BLOCKED: Decision.REQUIRE_OFFLINE_RUNNER_NETWORK_BLOCK_FIXES,
    Risk.OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED: Decision.REQUIRE_OFFLINE_RUNNER_NETWORK_BLOCK_FIXES,
    Risk.OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_UNSAFE: Decision.REQUIRE_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_FIXES,
    Risk.OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_UNSAFE: Decision.REQUIRE_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_FIXES,
    Risk.OFFLINE_RUNNER_ORDER_BLOCKING_UNSAFE: Decision.REQUIRE_OFFLINE_RUNNER_ORDER_BLOCKING_FIXES,
    Risk.OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_UNSAFE: Decision.REQUIRE_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_FIXES,
    Risk.OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_FIXES,
    Risk.OFFLINE_RUNNER_RISK_OBSERVATION_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_RISK_OBSERVATION_FIXES,
    Risk.OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_FIXES,
    Risk.OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_FIXES,
    Risk.OFFLINE_RUNNER_JOURNAL_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_JOURNAL_FIXES,
    Risk.OFFLINE_RUNNER_OBSERVABILITY_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_OBSERVABILITY_FIXES,
    Risk.OFFLINE_RUNNER_HUMAN_APPROVAL_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_HUMAN_APPROVAL_FIXES,
    Risk.OFFLINE_RUNNER_STOP_CONDITIONS_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_STOP_CONDITION_FIXES,
    Risk.OFFLINE_RUNNER_SUCCESS_CRITERIA_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_SUCCESS_FAILURE_FIXES,
    Risk.OFFLINE_RUNNER_FAILURE_CRITERIA_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_SUCCESS_FAILURE_FIXES,
    Risk.OFFLINE_RUNNER_AUDIT_CONTRACT_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_AUDIT_FIXES,
    Risk.OFFLINE_RUNNER_GO_NO_GO_CONTRACT_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_GO_NO_GO_FIXES,
    Risk.OFFLINE_RUNNER_ABORT_CONTRACT_MISSING: Decision.REQUIRE_OFFLINE_RUNNER_ABORT_FIXES,
    Risk.REAL_EXECUTION_BOUNDARY_VIOLATION: Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PLAN,
    Risk.DATA_ACCESS_VIOLATION: Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PLAN,
    Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_SAFETY_GATE: Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PLAN,
}

_RISK_TO_RECOMMENDATION = {
    Risk.FINAL_SAFETY_GATE_NOT_APPROVED: Recommendation.APPROVE_FINAL_SAFETY_GATE_FIRST,
    Risk.OFFLINE_RUNNER_SCOPE_UNCLEAR: Recommendation.DEFINE_OFFLINE_RUNNER_SCOPE,
    Risk.OFFLINE_RUNNER_EXECUTION_MODE_UNSAFE: Recommendation.DEFINE_OFFLINE_RUNNER_EXECUTION_MODE,
    Risk.OFFLINE_RUNNER_INPUT_CONTRACT_MISSING: Recommendation.DEFINE_OFFLINE_RUNNER_INPUT_CONTRACT,
    Risk.OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_MISSING: Recommendation.DEFINE_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT,
    Risk.OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_UNSAFE: Recommendation.HARDEN_OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION,
    Risk.OFFLINE_RUNNER_REAL_BROKER_BOUNDARY_VIOLATION: Recommendation.RESTORE_OFFLINE_RUNNER_NO_REAL_BROKER,
    Risk.OFFLINE_RUNNER_SECRET_READ_POLICY_UNSAFE: Recommendation.HARDEN_OFFLINE_RUNNER_NO_SECRET_READ,
    Risk.OFFLINE_RUNNER_NETWORK_NOT_BLOCKED: Recommendation.BLOCK_OFFLINE_RUNNER_NETWORK,
    Risk.OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED: Recommendation.BLOCK_OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET,
    Risk.OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_UNSAFE: Recommendation.HARDEN_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT,
    Risk.OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_UNSAFE: Recommendation.HARDEN_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT,
    Risk.OFFLINE_RUNNER_ORDER_BLOCKING_UNSAFE: Recommendation.HARDEN_OFFLINE_RUNNER_ORDER_BLOCKING,
    Risk.OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_UNSAFE: Recommendation.HARDEN_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING,
    Risk.OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_MISSING: Recommendation.DEFINE_OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION,
    Risk.OFFLINE_RUNNER_RISK_OBSERVATION_MISSING: Recommendation.DEFINE_OFFLINE_RUNNER_RISK_OBSERVATION,
    Risk.OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_MISSING: Recommendation.DEFINE_OFFLINE_RUNNER_PROFITABILITY_OBSERVATION,
    Risk.OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_MISSING: Recommendation.DEFINE_OFFLINE_RUNNER_CONSISTENCY_OBSERVATION,
    Risk.OFFLINE_RUNNER_JOURNAL_MISSING: Recommendation.COMPLETE_OFFLINE_RUNNER_JOURNAL,
    Risk.OFFLINE_RUNNER_OBSERVABILITY_MISSING: Recommendation.COMPLETE_OFFLINE_RUNNER_OBSERVABILITY,
    Risk.OFFLINE_RUNNER_HUMAN_APPROVAL_MISSING: Recommendation.REQUIRE_OFFLINE_RUNNER_HUMAN_APPROVAL,
    Risk.OFFLINE_RUNNER_STOP_CONDITIONS_MISSING: Recommendation.DEFINE_OFFLINE_RUNNER_STOP_CONDITIONS,
    Risk.OFFLINE_RUNNER_SUCCESS_CRITERIA_MISSING: Recommendation.DEFINE_OFFLINE_RUNNER_SUCCESS_FAILURE,
    Risk.OFFLINE_RUNNER_FAILURE_CRITERIA_MISSING: Recommendation.DEFINE_OFFLINE_RUNNER_SUCCESS_FAILURE,
    Risk.OFFLINE_RUNNER_AUDIT_CONTRACT_MISSING: Recommendation.COMPLETE_OFFLINE_RUNNER_AUDIT,
    Risk.OFFLINE_RUNNER_GO_NO_GO_CONTRACT_MISSING: Recommendation.DEFINE_OFFLINE_RUNNER_GO_NO_GO,
    Risk.OFFLINE_RUNNER_ABORT_CONTRACT_MISSING: Recommendation.DEFINE_OFFLINE_RUNNER_ABORT,
    Risk.REAL_EXECUTION_BOUNDARY_VIOLATION: Recommendation.RESTORE_OFFLINE_BOUNDARIES,
    Risk.DATA_ACCESS_VIOLATION: Recommendation.REMOVE_DATA_ACCESS,
    Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_SAFETY_GATE: Recommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_SAFETY_GATE,
}


def generate_offline_runner_plan_recommendations(data, risks: Iterable[Risk] | None = None) -> tuple[Recommendation, ...]:
    risks = tuple(risks if risks is not None else detect_offline_runner_plan_risks(data))
    if not risks:
        return (
            Recommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PLAN_SUITE,
            Recommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_SAFETY_GATE,
        )
    recommendations = [Recommendation.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_SAFETY_GATE]
    recommendations.extend(_RISK_TO_RECOMMENDATION.get(risk, Recommendation.RESTORE_OFFLINE_BOUNDARIES) for risk in risks)
    return _dedupe(recommendations)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PLAN
    blocking_risks = {
        Risk.REAL_EXECUTION_BOUNDARY_VIOLATION,
        Risk.DATA_ACCESS_VIOLATION,
        Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_SAFETY_GATE,
    }
    if any(risk in blocking_risks for risk in risks):
        return Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PLAN
    for risk in risks:
        decision = _RISK_TO_DECISION.get(risk)
        if decision is not None:
            return decision
    return Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PLAN


def _state_for(data, risks: tuple[Risk, ...], score: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPlanScore) -> m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPlanState:
    if _gate(data) is None:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPlanState.OFFLINE_RUNNER_PLAN_INPUT_INVALID
    if not risks and score.overall_score >= 85:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPlanState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_SAFETY_GATE
    if risks:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPlanState.OFFLINE_RUNNER_PLAN_BLOCKED
    if score.overall_score >= 70:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPlanState.OFFLINE_RUNNER_PLAN_COMPLETED_WITH_WARNINGS
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPlanState.NOT_READY


def render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_plan_markdown(result) -> str:
    risks = ", ".join(_value(risk) for risk in result.risks) or "none"
    recommendations = ", ".join(_value(recommendation) for recommendation in result.recommendations) or "none"
    return "\n".join((
        "# Paper Broker Read-Only Connection Dry Run Controlled Offline Runner Plan",
        f"- State: {_value(result.state)}",
        f"- Decision: {_value(result.decision)}",
        f"- Score: {result.score.overall_score}",
        f"- Risks: {risks}",
        f"- Recommendations: {recommendations}",
        "- Boundary: offline/sandbox plan only; no runner execution, no dry-run execution, no broker connection, no secrets, no network, no orders, no position mutation, no data access.",
        f"- Next phase: {result.next_phase}",
    ))


def evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_plan(data=None):
    data = _coerce_input(data)
    sections = _sections(data)
    score = compute_offline_runner_plan_score(data, sections)
    risks = detect_offline_runner_plan_risks(data, sections)
    recommendations = generate_offline_runner_plan_recommendations(data, risks)
    decision = _decision_for(risks)
    state = _state_for(data, risks, score)
    summary = "Offline controlled runner plan approved for safety gate" if not risks else "Offline controlled runner plan blocked"
    result = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPlanResult(
        state=state,
        decision=decision,
        score=score,
        risks=risks,
        recommendations=recommendations,
        summary=summary,
        offline_only=True,
        sandbox_only=True,
        plan_only=True,
        runner_executed=False,
        dry_run_executed=False,
        findings=tuple(sections.values()),
        **sections,
    )
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerPlanResult(
        **{**result.__dict__, "markdown_report": render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_plan_markdown(result)}
    )
