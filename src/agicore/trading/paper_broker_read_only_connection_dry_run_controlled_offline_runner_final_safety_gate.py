"""Offline safety gate for controlled offline runner plans."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Callable, Iterable, Mapping

from agicore.trading import paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_safety_gate_models as m

Risk = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateRisk
Decision = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateDecision
Recommendation = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateRecommendation


def _coerce_input(data: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateInput | Mapping[str, Any] | None) -> m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateInput:
    if data is None:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateInput()
    if isinstance(data, m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateInput):
        return data
    allowed = {field.name for field in fields(m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateInput)}
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateInput(**{key: value for key, value in dict(data).items() if key in allowed})


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


def _plan(data: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateInput) -> Any:
    return data.paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_plan


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _upstream_items(data: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateInput) -> tuple[Any, ...]:
    return (
        data.paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_plan,
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


def _upstream_risks(data: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _section(data: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateInput, attr: str) -> Any:
    return _get(_plan(data), attr)


def _section_ok(section: Any) -> bool:
    return section is not None and _get(section, "defined", True) is True and _get(section, "passed", True) is True and not _as_tuple(_get(section, "risks", ()))


def validate_final_offline_runner_plan_approval(data) -> bool:
    data = _coerce_input(data)
    plan = _plan(data)
    if plan is None or data.final_offline_runner_plan_approved is False:
        return False
    approved_state = _state_contains(
        plan,
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN",
    )
    approved = data.final_offline_runner_plan_approved is True or approved_state
    return approved and not _as_tuple(_get(plan, "risks", ())) and _get(plan, "offline_only", True) is True


def _offline_boundary(data: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateInput) -> bool:
    expected_true = (
        data.offline_mode_enforced, data.sandbox_mode_enforced, data.safety_gate_only,
        data.no_runner_created, data.no_runner_execution, data.no_dry_run_execution,
        data.no_broker_connection, data.no_real_broker, data.no_alpaca_real,
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
        and not _has_upstream_risk(data, "LIVE_EXECUTION", "BROKER_CONNECTION", "API_KEY", "SECRET_READ", "NETWORK", "HTTP", "WEBSOCKET", "SOCKET", "REAL_ORDER", "REAL_ACCOUNT", "REAL_EXECUTION", "POSITION_MUTATION", "ALPACA_REAL", "RUNNER_EXECUT")
    )


def _data_boundary(data: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateInput) -> bool:
    return data.data_access_requested is not True and not _has_upstream_risk(data, "DATA_ACCESS", "DATA/", "REAL_DATA")


def _http_transport_safe(data: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateInput) -> bool:
    return data.no_http_transport is True and data.no_websocket_transport is True and data.no_socket_transport is True and data.network_transport_requested is not True


_Check = tuple[str, Callable[[m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateInput], bool]]


def _boundary(data, *, flag: str, score: str, fallback_attr: str | None, risk: Risk, cls, checks: tuple[_Check, ...]):
    data = _coerce_input(data)
    values = {field: check(data) for field, check in checks}
    fallback = _get(_section(data, fallback_attr), "score") if fallback_attr else None
    passed = _get(data, flag) is True and all(values.values())
    return cls(
        passed=passed,
        score=_metric_score(_get(data, score), fallback, passed),
        risks=() if passed else (risk,),
        details=("offline runner safety boundary validated without creating or executing runner",),
        **values,
    )


def validate_final_offline_runner_safety_scope_boundary(data):
    return _boundary(data, flag="final_offline_runner_safety_scope_boundary_verified", score="scope_score", fallback_attr="scope", risk=Risk.FINAL_OFFLINE_RUNNER_SAFETY_SCOPE_BOUNDARY_FAILED, cls=m.FinalOfflineRunnerSafetyScopeBoundary, checks=(
        ("offline_only", lambda d: d.offline_mode_enforced is True and _get(_section(d, "scope"), "offline_only", True) is True),
        ("sandbox_only", lambda d: d.sandbox_mode_enforced is True and _get(_section(d, "scope"), "sandbox_only", True) is True),
        ("safety_gate_only", lambda d: d.safety_gate_only is True),
        ("runner_not_created", lambda d: d.no_runner_created is True and d.runner_creation_requested is not True),
        ("runner_not_executed", lambda d: d.no_runner_execution is True and d.runner_execution_requested is not True),
    ))


def validate_final_offline_runner_safety_execution_mode_boundary(data):
    return _boundary(data, flag="final_offline_runner_safety_execution_mode_boundary_verified", score="execution_mode_score", fallback_attr="execution_mode", risk=Risk.FINAL_OFFLINE_RUNNER_SAFETY_EXECUTION_MODE_BOUNDARY_FAILED, cls=m.FinalOfflineRunnerSafetyExecutionModeBoundary, checks=(
        ("controlled_offline_mode", lambda d: _section_ok(_section(d, "execution_mode"))),
        ("deterministic_mode", lambda d: _get(_section(d, "execution_mode"), "deterministic_mode", True) is True),
        ("in_memory_only", lambda d: _get(_section(d, "execution_mode"), "in_memory_only", True) is True),
        ("no_dry_run_execution", lambda d: d.no_dry_run_execution is True and d.dry_run_requested is not True and d.dry_run_executed is not True),
    ))


def validate_final_offline_runner_safety_input_contract_boundary(data):
    return _boundary(data, flag="final_offline_runner_safety_input_contract_boundary_verified", score="input_contract_score", fallback_attr="input_contract", risk=Risk.FINAL_OFFLINE_RUNNER_SAFETY_INPUT_CONTRACT_BOUNDARY_FAILED, cls=m.FinalOfflineRunnerSafetyInputContractBoundary, checks=(
        ("input_contract_valid", lambda d: _section_ok(_section(d, "input_contract"))),
        ("synthetic_inputs_only", lambda d: _get(_section(d, "input_contract"), "synthetic_inputs_only", True) is True),
        ("no_real_credentials", lambda d: d.no_api_key_read is True and d.no_env_var_read is True),
    ))


def validate_final_offline_runner_safety_synthetic_market_context_boundary(data):
    return _boundary(data, flag="final_offline_runner_safety_synthetic_market_context_boundary_verified", score="synthetic_market_context_score", fallback_attr="synthetic_market_context", risk=Risk.FINAL_OFFLINE_RUNNER_SAFETY_SYNTHETIC_MARKET_CONTEXT_BOUNDARY_FAILED, cls=m.FinalOfflineRunnerSafetySyntheticMarketContextBoundary, checks=(
        ("synthetic_context_valid", lambda d: _section_ok(_section(d, "synthetic_market_context"))),
        ("in_memory_context", lambda d: _get(_section(d, "synthetic_market_context"), "in_memory_context", True) is True),
        ("no_data_access", lambda d: d.data_access_requested is not True),
    ))


def validate_final_offline_runner_safety_read_only_broker_simulation_boundary(data):
    return _boundary(data, flag="final_offline_runner_safety_read_only_broker_simulation_boundary_verified", score="read_only_broker_simulation_score", fallback_attr="read_only_broker_simulation", risk=Risk.FINAL_OFFLINE_RUNNER_SAFETY_READ_ONLY_BROKER_SIMULATION_BOUNDARY_FAILED, cls=m.FinalOfflineRunnerSafetyReadOnlyBrokerSimulationBoundary, checks=(
        ("simulated_broker_only", lambda d: _get(_section(d, "read_only_broker_simulation"), "simulated_broker_only", True) is True),
        ("read_only_contract", lambda d: _get(_section(d, "read_only_broker_simulation"), "read_only_contract", True) is True),
        ("no_real_broker", lambda d: d.no_real_broker is True and d.broker_connection_requested is not True),
    ))


def validate_final_offline_runner_safety_no_real_broker_boundary(data):
    return _boundary(data, flag="final_offline_runner_safety_no_real_broker_boundary_verified", score="no_real_broker_score", fallback_attr="no_real_broker_policy", risk=Risk.FINAL_OFFLINE_RUNNER_SAFETY_REAL_BROKER_BOUNDARY_FAILED, cls=m.FinalOfflineRunnerSafetyNoRealBrokerBoundary, checks=(
        ("real_broker_blocked", lambda d: d.no_real_broker is True and d.broker_connection_requested is not True),
        ("alpaca_blocked", lambda d: d.no_alpaca_real is True),
        ("broker_connection_disabled", lambda d: d.no_broker_connection is True),
    ))


def validate_final_offline_runner_safety_no_secret_read_boundary(data):
    return _boundary(data, flag="final_offline_runner_safety_no_secret_read_boundary_verified", score="no_secret_read_score", fallback_attr="no_secret_read_policy", risk=Risk.FINAL_OFFLINE_RUNNER_SAFETY_SECRET_READ_BOUNDARY_FAILED, cls=m.FinalOfflineRunnerSafetyNoSecretReadBoundary, checks=(
        ("no_api_key_read", lambda d: d.no_api_key_read is True and d.api_key_read_requested is not True),
        ("no_env_var_read", lambda d: d.no_env_var_read is True and d.env_var_read_requested is not True),
        ("no_hardcoded_secret", lambda d: d.no_hardcoded_secrets is True and d.hardcoded_secret_detected is not True),
    ))


def validate_final_offline_runner_safety_network_block_boundary(data):
    return _boundary(data, flag="final_offline_runner_safety_network_block_boundary_verified", score="network_score", fallback_attr="network_block_policy", risk=Risk.FINAL_OFFLINE_RUNNER_SAFETY_NETWORK_BLOCK_BOUNDARY_FAILED, cls=m.FinalOfflineRunnerSafetyNetworkBlockBoundary, checks=(
        ("network_blocked", lambda d: d.network_transport_requested is not True),
        ("http_blocked", lambda d: d.no_http_transport is True),
        ("websocket_blocked", lambda d: d.no_websocket_transport is True),
        ("socket_blocked", lambda d: d.no_socket_transport is True),
        ("external_api_blocked", lambda d: d.no_external_api is True and d.external_api_requested is not True),
    ))


def validate_final_offline_runner_safety_http_websocket_socket_block_boundary(data):
    return _boundary(data, flag="final_offline_runner_safety_http_websocket_socket_block_boundary_verified", score="http_websocket_socket_score", fallback_attr="http_websocket_socket_block_policy", risk=Risk.FINAL_OFFLINE_RUNNER_SAFETY_HTTP_WEBSOCKET_SOCKET_BLOCK_BOUNDARY_FAILED, cls=m.FinalOfflineRunnerSafetyNetworkBlockBoundary, checks=(
        ("network_blocked", lambda d: d.network_transport_requested is not True),
        ("http_blocked", lambda d: d.no_http_transport is True),
        ("websocket_blocked", lambda d: d.no_websocket_transport is True),
        ("socket_blocked", lambda d: d.no_socket_transport is True),
        ("external_api_blocked", lambda d: d.no_external_api is True),
    ))

def validate_final_offline_runner_safety_account_snapshot_boundary(data):
    return _boundary(data, flag="final_offline_runner_safety_account_snapshot_boundary_verified", score="account_snapshot_score", fallback_attr="account_snapshot_policy", risk=Risk.FINAL_OFFLINE_RUNNER_SAFETY_ACCOUNT_SNAPSHOT_BOUNDARY_FAILED, cls=m.FinalOfflineRunnerSafetyAccountSnapshotBoundary, checks=(
        ("simulated_snapshot_only", lambda d: _get(_section(d, "account_snapshot_policy"), "simulated_snapshot_only", True) is True),
        ("read_only_snapshot", lambda d: _get(_section(d, "account_snapshot_policy"), "read_only_snapshot", True) is True),
        ("active_account_access_blocked", lambda d: d.no_real_account_access is True and d.account_access_requested is not True),
    ))


def validate_final_offline_runner_safety_market_data_snapshot_boundary(data):
    return _boundary(data, flag="final_offline_runner_safety_market_data_snapshot_boundary_verified", score="market_data_snapshot_score", fallback_attr="market_data_snapshot_policy", risk=Risk.FINAL_OFFLINE_RUNNER_SAFETY_MARKET_DATA_SNAPSHOT_BOUNDARY_FAILED, cls=m.FinalOfflineRunnerSafetyMarketDataSnapshotBoundary, checks=(
        ("synthetic_snapshot_only", lambda d: _get(_section(d, "market_data_snapshot_policy"), "synthetic_snapshot_only", True) is True),
        ("read_only_snapshot", lambda d: _get(_section(d, "market_data_snapshot_policy"), "read_only_snapshot", True) is True),
        ("live_subscription_blocked", lambda d: _http_transport_safe(d) and d.data_access_requested is not True),
    ))


def validate_final_offline_runner_safety_order_blocking_boundary(data):
    return _boundary(data, flag="final_offline_runner_safety_order_blocking_boundary_verified", score="order_blocking_score", fallback_attr="order_blocking_policy", risk=Risk.FINAL_OFFLINE_RUNNER_SAFETY_ORDER_BLOCKING_BOUNDARY_FAILED, cls=m.FinalOfflineRunnerSafetyOrderBlockingBoundary, checks=(
        ("order_execution_blocked", lambda d: d.order_execution_requested is not True),
        ("real_order_blocked", lambda d: d.no_real_order is True),
        ("cancel_replace_blocked", lambda d: _get(_section(d, "order_blocking_policy"), "cancel_replace_blocked", True) is True),
    ))


def validate_final_offline_runner_safety_position_mutation_blocking_boundary(data):
    return _boundary(data, flag="final_offline_runner_safety_position_mutation_blocking_boundary_verified", score="position_mutation_score", fallback_attr="position_mutation_blocking_policy", risk=Risk.FINAL_OFFLINE_RUNNER_SAFETY_POSITION_MUTATION_BLOCKING_BOUNDARY_FAILED, cls=m.FinalOfflineRunnerSafetyPositionMutationBlockingBoundary, checks=(
        ("position_mutation_blocked", lambda d: d.no_position_mutation is True and d.position_mutation_requested is not True),
        ("close_modify_blocked", lambda d: _get(_section(d, "position_mutation_blocking_policy"), "close_modify_blocked", True) is True),
        ("simulated_position_read_only", lambda d: _get(_section(d, "position_mutation_blocking_policy"), "simulated_position_read_only", True) is True),
    ))


def validate_final_offline_runner_safety_strategy_signal_observation_boundary(data):
    return _boundary(data, flag="final_offline_runner_safety_strategy_signal_observation_boundary_verified", score="strategy_signal_observation_score", fallback_attr="strategy_signal_observation_plan", risk=Risk.FINAL_OFFLINE_RUNNER_SAFETY_STRATEGY_SIGNAL_OBSERVATION_BOUNDARY_FAILED, cls=m.FinalOfflineRunnerSafetyStrategySignalObservationBoundary, checks=(
        ("observation_only", lambda d: _get(_section(d, "strategy_signal_observation_plan"), "observation_only", True) is True),
        ("no_signal_execution", lambda d: d.order_execution_requested is not True),
        ("signal_trace_required", lambda d: _get(_section(d, "strategy_signal_observation_plan"), "signal_trace_required", True) is True),
    ))


def validate_final_offline_runner_safety_risk_observation_boundary(data):
    return _boundary(data, flag="final_offline_runner_safety_risk_observation_boundary_verified", score="risk_observation_score", fallback_attr="risk_observation_plan", risk=Risk.FINAL_OFFLINE_RUNNER_SAFETY_RISK_OBSERVATION_BOUNDARY_FAILED, cls=m.FinalOfflineRunnerSafetyRiskObservationBoundary, checks=(
        ("observation_only", lambda d: _get(_section(d, "risk_observation_plan"), "observation_only", True) is True),
        ("no_risk_action_execution", lambda d: d.position_mutation_requested is not True and d.order_execution_requested is not True),
        ("risk_trace_required", lambda d: _get(_section(d, "risk_observation_plan"), "risk_trace_required", True) is True),
    ))


def validate_final_offline_runner_safety_profitability_observation_boundary(data):
    return _boundary(data, flag="final_offline_runner_safety_profitability_observation_boundary_verified", score="profitability_observation_score", fallback_attr="profitability_observation_plan", risk=Risk.FINAL_OFFLINE_RUNNER_SAFETY_PROFITABILITY_OBSERVATION_BOUNDARY_FAILED, cls=m.FinalOfflineRunnerSafetyProfitabilityObservationBoundary, checks=(
        ("observation_only", lambda d: _get(_section(d, "profitability_observation_plan"), "observation_only", True) is True),
        ("no_profit_promise", lambda d: _get(_section(d, "profitability_observation_plan"), "no_profit_promise", True) is True),
        ("profitability_trace_required", lambda d: _get(_section(d, "profitability_observation_plan"), "profitability_trace_required", True) is True),
    ))


def validate_final_offline_runner_safety_consistency_observation_boundary(data):
    return _boundary(data, flag="final_offline_runner_safety_consistency_observation_boundary_verified", score="consistency_observation_score", fallback_attr="consistency_observation_plan", risk=Risk.FINAL_OFFLINE_RUNNER_SAFETY_CONSISTENCY_OBSERVATION_BOUNDARY_FAILED, cls=m.FinalOfflineRunnerSafetyConsistencyObservationBoundary, checks=(
        ("observation_only", lambda d: _get(_section(d, "consistency_observation_plan"), "observation_only", True) is True),
        ("deterministic_consistency_checks", lambda d: _get(_section(d, "consistency_observation_plan"), "deterministic_consistency_checks", True) is True),
        ("consistency_trace_required", lambda d: _get(_section(d, "consistency_observation_plan"), "consistency_trace_required", True) is True),
    ))


def validate_final_offline_runner_safety_journal_boundary(data):
    return _boundary(data, flag="final_offline_runner_safety_journal_boundary_verified", score="journal_score", fallback_attr="journal_plan", risk=Risk.FINAL_OFFLINE_RUNNER_SAFETY_JOURNAL_BOUNDARY_FAILED, cls=m.FinalOfflineRunnerSafetyJournalBoundary, checks=(
        ("offline_journal_required", lambda d: _get(_section(d, "journal_plan"), "offline_journal_required", True) is True),
        ("no_secret_material_logged", lambda d: _get(_section(d, "journal_plan"), "no_secret_material_logged", True) is True),
        ("plan_events_recorded", lambda d: _get(_section(d, "journal_plan"), "plan_events_recorded", True) is True),
    ))


def validate_final_offline_runner_safety_observability_boundary(data):
    return _boundary(data, flag="final_offline_runner_safety_observability_boundary_verified", score="observability_score", fallback_attr="observability_plan", risk=Risk.FINAL_OFFLINE_RUNNER_SAFETY_OBSERVABILITY_BOUNDARY_FAILED, cls=m.FinalOfflineRunnerSafetyObservabilityBoundary, checks=(
        ("offline_events_defined", lambda d: _get(_section(d, "observability_plan"), "offline_events_defined", True) is True),
        ("no_connection_attempt_metrics", lambda d: d.broker_connection_requested is not True),
        ("sensitive_values_redacted", lambda d: _get(_section(d, "observability_plan"), "sensitive_values_redacted", True) is True),
    ))


def validate_final_offline_runner_safety_human_approval_boundary(data):
    return _boundary(data, flag="final_offline_runner_safety_human_approval_boundary_verified", score="human_approval_score", fallback_attr="human_approval_plan", risk=Risk.FINAL_OFFLINE_RUNNER_SAFETY_HUMAN_APPROVAL_BOUNDARY_FAILED, cls=m.FinalOfflineRunnerSafetyHumanApprovalBoundary, checks=(
        ("human_approval_required", lambda d: d.human_approval_required is True),
        ("approval_before_preparation", lambda d: d.approval_before_preparation is True),
        ("evidence_required", lambda d: _get(_section(d, "human_approval_plan"), "evidence_required", True) is True),
    ))


def validate_final_offline_runner_safety_stop_conditions_boundary(data):
    return _boundary(data, flag="final_offline_runner_safety_stop_conditions_boundary_verified", score="stop_conditions_score", fallback_attr="stop_conditions_plan", risk=Risk.FINAL_OFFLINE_RUNNER_SAFETY_STOP_CONDITION_BOUNDARY_FAILED, cls=m.FinalOfflineRunnerSafetyStopConditionBoundary, checks=(
        ("stop_on_secret_read", lambda d: _get(_section(d, "stop_conditions_plan"), "stop_on_secret_read", True) is True),
        ("stop_on_network_request", lambda d: _get(_section(d, "stop_conditions_plan"), "stop_on_network_request", True) is True),
        ("stop_on_order_or_position_request", lambda d: _get(_section(d, "stop_conditions_plan"), "stop_on_order_or_position_request", True) is True),
        ("stop_on_account_access_request", lambda d: _get(_section(d, "stop_conditions_plan"), "stop_on_account_access_request", True) is True),
    ))


def validate_final_offline_runner_safety_success_failure_boundary(data):
    return _boundary(data, flag="final_offline_runner_safety_success_failure_boundary_verified", score="success_failure_score", fallback_attr=None, risk=Risk.FINAL_OFFLINE_RUNNER_SAFETY_SUCCESS_FAILURE_BOUNDARY_FAILED, cls=m.FinalOfflineRunnerSafetySuccessFailureBoundary, checks=(
        ("success_criteria_defined", lambda d: _section_ok(_section(d, "success_criteria"))),
        ("failure_criteria_defined", lambda d: _section_ok(_section(d, "failure_criteria"))),
        ("failure_on_boundary_violation", lambda d: d.failure_on_boundary_violation is True),
    ))


def validate_final_offline_runner_safety_audit_boundary(data):
    return _boundary(data, flag="final_offline_runner_safety_audit_boundary_verified", score="audit_score", fallback_attr="audit_plan", risk=Risk.FINAL_OFFLINE_RUNNER_SAFETY_AUDIT_BOUNDARY_FAILED, cls=m.FinalOfflineRunnerSafetyAuditBoundary, checks=(
        ("audit_events_defined", lambda d: _get(_section(d, "audit_plan"), "audit_events_defined", True) is True),
        ("boundary_evidence_required", lambda d: _get(_section(d, "audit_plan"), "boundary_evidence_required", True) is True),
        ("immutable_plan_record_required", lambda d: _get(_section(d, "audit_plan"), "immutable_plan_record_required", True) is True),
    ))


def validate_final_offline_runner_safety_go_no_go_boundary(data):
    return _boundary(data, flag="final_offline_runner_safety_go_no_go_boundary_verified", score="go_no_go_score", fallback_attr="go_no_go_policy", risk=Risk.FINAL_OFFLINE_RUNNER_SAFETY_GO_NO_GO_BOUNDARY_FAILED, cls=m.FinalOfflineRunnerSafetyGoNoGoBoundary, checks=(
        ("go_no_go_required", lambda d: _get(_section(d, "go_no_go_policy"), "go_no_go_required", True) is True),
        ("no_go_on_risk", lambda d: _get(_section(d, "go_no_go_policy"), "no_go_on_risk", True) is True),
        ("next_phase_requires_clean_gate", lambda d: d.next_phase_requires_clean_gate is True),
    ))


def validate_final_offline_runner_safety_abort_boundary(data):
    return _boundary(data, flag="final_offline_runner_safety_abort_boundary_verified", score="abort_score", fallback_attr="abort_policy", risk=Risk.FINAL_OFFLINE_RUNNER_SAFETY_ABORT_BOUNDARY_FAILED, cls=m.FinalOfflineRunnerSafetyAbortBoundary, checks=(
        ("abort_on_secret_read", lambda d: _get(_section(d, "abort_policy"), "abort_on_secret_read", True) is True),
        ("abort_on_network_or_broker_request", lambda d: _get(_section(d, "abort_policy"), "abort_on_network_or_broker_request", True) is True),
        ("abort_on_order_or_position_request", lambda d: _get(_section(d, "abort_policy"), "abort_on_order_or_position_request", True) is True),
    ))


def _boundaries(data: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateInput):
    return {
        "scope_boundary": validate_final_offline_runner_safety_scope_boundary(data),
        "execution_mode_boundary": validate_final_offline_runner_safety_execution_mode_boundary(data),
        "input_contract_boundary": validate_final_offline_runner_safety_input_contract_boundary(data),
        "synthetic_market_context_boundary": validate_final_offline_runner_safety_synthetic_market_context_boundary(data),
        "read_only_broker_simulation_boundary": validate_final_offline_runner_safety_read_only_broker_simulation_boundary(data),
        "no_real_broker_boundary": validate_final_offline_runner_safety_no_real_broker_boundary(data),
        "no_secret_read_boundary": validate_final_offline_runner_safety_no_secret_read_boundary(data),
        "network_block_boundary": validate_final_offline_runner_safety_network_block_boundary(data),
        "http_websocket_socket_block_boundary": validate_final_offline_runner_safety_http_websocket_socket_block_boundary(data),
        "account_snapshot_boundary": validate_final_offline_runner_safety_account_snapshot_boundary(data),
        "market_data_snapshot_boundary": validate_final_offline_runner_safety_market_data_snapshot_boundary(data),
        "order_blocking_boundary": validate_final_offline_runner_safety_order_blocking_boundary(data),
        "position_mutation_blocking_boundary": validate_final_offline_runner_safety_position_mutation_blocking_boundary(data),
        "strategy_signal_observation_boundary": validate_final_offline_runner_safety_strategy_signal_observation_boundary(data),
        "risk_observation_boundary": validate_final_offline_runner_safety_risk_observation_boundary(data),
        "profitability_observation_boundary": validate_final_offline_runner_safety_profitability_observation_boundary(data),
        "consistency_observation_boundary": validate_final_offline_runner_safety_consistency_observation_boundary(data),
        "journal_boundary": validate_final_offline_runner_safety_journal_boundary(data),
        "observability_boundary": validate_final_offline_runner_safety_observability_boundary(data),
        "human_approval_boundary": validate_final_offline_runner_safety_human_approval_boundary(data),
        "stop_conditions_boundary": validate_final_offline_runner_safety_stop_conditions_boundary(data),
        "success_failure_boundary": validate_final_offline_runner_safety_success_failure_boundary(data),
        "audit_boundary": validate_final_offline_runner_safety_audit_boundary(data),
        "go_no_go_boundary": validate_final_offline_runner_safety_go_no_go_boundary(data),
        "abort_boundary": validate_final_offline_runner_safety_abort_boundary(data),
    }

def compute_final_offline_runner_safety_gate_score(data, boundaries: Mapping[str, Any] | None = None) -> m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateScore:
    data = _coerce_input(data)
    boundaries = dict(boundaries or _boundaries(data))
    plan_score = _metric_score(data.final_offline_runner_plan_score, _get(_get(_plan(data), "score"), "overall_score"), validate_final_offline_runner_plan_approval(data))
    scores = {key: _get(value, "score", 0) for key, value in boundaries.items()}
    overall = _average((plan_score, *scores.values()))
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateScore(
        overall_score=overall,
        final_offline_runner_plan_score=plan_score,
        scope_score=scores["scope_boundary"],
        execution_mode_score=scores["execution_mode_boundary"],
        input_contract_score=scores["input_contract_boundary"],
        synthetic_market_context_score=scores["synthetic_market_context_boundary"],
        read_only_broker_simulation_score=scores["read_only_broker_simulation_boundary"],
        no_real_broker_score=scores["no_real_broker_boundary"],
        no_secret_read_score=scores["no_secret_read_boundary"],
        network_score=scores["network_block_boundary"],
        http_websocket_socket_score=scores["http_websocket_socket_block_boundary"],
        account_snapshot_score=scores["account_snapshot_boundary"],
        market_data_snapshot_score=scores["market_data_snapshot_boundary"],
        order_blocking_score=scores["order_blocking_boundary"],
        position_mutation_score=scores["position_mutation_blocking_boundary"],
        strategy_signal_observation_score=scores["strategy_signal_observation_boundary"],
        risk_observation_score=scores["risk_observation_boundary"],
        profitability_observation_score=scores["profitability_observation_boundary"],
        consistency_observation_score=scores["consistency_observation_boundary"],
        journal_score=scores["journal_boundary"],
        observability_score=scores["observability_boundary"],
        human_approval_score=scores["human_approval_boundary"],
        stop_conditions_score=scores["stop_conditions_boundary"],
        success_failure_score=scores["success_failure_boundary"],
        audit_score=scores["audit_boundary"],
        go_no_go_score=scores["go_no_go_boundary"],
        abort_score=scores["abort_boundary"],
    )


def detect_final_offline_runner_safety_gate_risks(data, boundaries: Mapping[str, Any] | None = None) -> tuple[Risk, ...]:
    data = _coerce_input(data)
    boundaries = dict(boundaries or _boundaries(data))
    risks: list[Risk] = []
    if not validate_final_offline_runner_plan_approval(data):
        risks.append(Risk.FINAL_OFFLINE_RUNNER_PLAN_NOT_APPROVED)
    for boundary in boundaries.values():
        risks.extend(_as_tuple(_get(boundary, "risks", ())))
    if not _offline_boundary(data):
        risks.append(Risk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(Risk.DATA_ACCESS_VIOLATION)
    if data.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_plan_requested is True:
        risks.append(Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN)
    return _dedupe(risks)


_RISK_TO_DECISION = {
    Risk.FINAL_OFFLINE_RUNNER_PLAN_NOT_APPROVED: Decision.REQUIRE_FINAL_OFFLINE_RUNNER_PLAN_FIXES,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_SCOPE_BOUNDARY_FAILED: Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_SCOPE_FIXES,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_EXECUTION_MODE_BOUNDARY_FAILED: Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_EXECUTION_MODE_FIXES,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_INPUT_CONTRACT_BOUNDARY_FAILED: Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_INPUT_CONTRACT_FIXES,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_SYNTHETIC_MARKET_CONTEXT_BOUNDARY_FAILED: Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_SYNTHETIC_MARKET_CONTEXT_FIXES,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_READ_ONLY_BROKER_SIMULATION_BOUNDARY_FAILED: Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_READ_ONLY_BROKER_SIMULATION_FIXES,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_REAL_BROKER_BOUNDARY_FAILED: Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_NO_REAL_BROKER_FIXES,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_SECRET_READ_BOUNDARY_FAILED: Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_NO_SECRET_READ_FIXES,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_NETWORK_BLOCK_BOUNDARY_FAILED: Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_NETWORK_BLOCK_FIXES,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_HTTP_WEBSOCKET_SOCKET_BLOCK_BOUNDARY_FAILED: Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_NETWORK_BLOCK_FIXES,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_ACCOUNT_SNAPSHOT_BOUNDARY_FAILED: Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_ACCOUNT_SNAPSHOT_FIXES,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_MARKET_DATA_SNAPSHOT_BOUNDARY_FAILED: Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_MARKET_DATA_SNAPSHOT_FIXES,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_ORDER_BLOCKING_BOUNDARY_FAILED: Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_ORDER_BLOCKING_FIXES,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_POSITION_MUTATION_BLOCKING_BOUNDARY_FAILED: Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_POSITION_MUTATION_BLOCKING_FIXES,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_STRATEGY_SIGNAL_OBSERVATION_BOUNDARY_FAILED: Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_STRATEGY_SIGNAL_OBSERVATION_FIXES,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_RISK_OBSERVATION_BOUNDARY_FAILED: Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_RISK_OBSERVATION_FIXES,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_PROFITABILITY_OBSERVATION_BOUNDARY_FAILED: Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_PROFITABILITY_OBSERVATION_FIXES,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_CONSISTENCY_OBSERVATION_BOUNDARY_FAILED: Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_CONSISTENCY_OBSERVATION_FIXES,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_JOURNAL_BOUNDARY_FAILED: Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_JOURNAL_FIXES,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_OBSERVABILITY_BOUNDARY_FAILED: Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_OBSERVABILITY_FIXES,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_HUMAN_APPROVAL_BOUNDARY_FAILED: Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_HUMAN_APPROVAL_FIXES,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_STOP_CONDITION_BOUNDARY_FAILED: Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_STOP_CONDITION_FIXES,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_SUCCESS_FAILURE_BOUNDARY_FAILED: Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_SUCCESS_FAILURE_FIXES,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_AUDIT_BOUNDARY_FAILED: Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_AUDIT_FIXES,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_GO_NO_GO_BOUNDARY_FAILED: Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_GO_NO_GO_FIXES,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_ABORT_BOUNDARY_FAILED: Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_ABORT_FIXES,
    Risk.REAL_EXECUTION_BOUNDARY_VIOLATION: Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE,
    Risk.DATA_ACCESS_VIOLATION: Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE,
    Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN: Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE,
}

_RISK_TO_RECOMMENDATION = {
    Risk.FINAL_OFFLINE_RUNNER_PLAN_NOT_APPROVED: Recommendation.APPROVE_OFFLINE_RUNNER_PLAN_FIRST,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_SCOPE_BOUNDARY_FAILED: Recommendation.HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_SCOPE,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_EXECUTION_MODE_BOUNDARY_FAILED: Recommendation.HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_EXECUTION_MODE,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_INPUT_CONTRACT_BOUNDARY_FAILED: Recommendation.HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_INPUT_CONTRACT,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_SYNTHETIC_MARKET_CONTEXT_BOUNDARY_FAILED: Recommendation.HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_SYNTHETIC_MARKET_CONTEXT,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_READ_ONLY_BROKER_SIMULATION_BOUNDARY_FAILED: Recommendation.HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_READ_ONLY_BROKER_SIMULATION,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_REAL_BROKER_BOUNDARY_FAILED: Recommendation.RESTORE_OFFLINE_RUNNER_REAL_BROKER_BOUNDARY,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_SECRET_READ_BOUNDARY_FAILED: Recommendation.HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_NO_SECRET_READ,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_NETWORK_BLOCK_BOUNDARY_FAILED: Recommendation.BLOCK_FINAL_OFFLINE_RUNNER_SAFETY_NETWORK,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_HTTP_WEBSOCKET_SOCKET_BLOCK_BOUNDARY_FAILED: Recommendation.BLOCK_FINAL_OFFLINE_RUNNER_SAFETY_HTTP_WEBSOCKET_SOCKET,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_ACCOUNT_SNAPSHOT_BOUNDARY_FAILED: Recommendation.HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_ACCOUNT_SNAPSHOT,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_MARKET_DATA_SNAPSHOT_BOUNDARY_FAILED: Recommendation.HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_MARKET_DATA_SNAPSHOT,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_ORDER_BLOCKING_BOUNDARY_FAILED: Recommendation.HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_ORDER_BLOCKING,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_POSITION_MUTATION_BLOCKING_BOUNDARY_FAILED: Recommendation.HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_POSITION_MUTATION_BLOCKING,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_STRATEGY_SIGNAL_OBSERVATION_BOUNDARY_FAILED: Recommendation.HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_STRATEGY_SIGNAL_OBSERVATION,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_RISK_OBSERVATION_BOUNDARY_FAILED: Recommendation.HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_RISK_OBSERVATION,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_PROFITABILITY_OBSERVATION_BOUNDARY_FAILED: Recommendation.HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_PROFITABILITY_OBSERVATION,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_CONSISTENCY_OBSERVATION_BOUNDARY_FAILED: Recommendation.HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_CONSISTENCY_OBSERVATION,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_JOURNAL_BOUNDARY_FAILED: Recommendation.COMPLETE_FINAL_OFFLINE_RUNNER_SAFETY_JOURNAL,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_OBSERVABILITY_BOUNDARY_FAILED: Recommendation.COMPLETE_FINAL_OFFLINE_RUNNER_SAFETY_OBSERVABILITY,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_HUMAN_APPROVAL_BOUNDARY_FAILED: Recommendation.REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_HUMAN_APPROVAL,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_STOP_CONDITION_BOUNDARY_FAILED: Recommendation.HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_STOP_CONDITIONS,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_SUCCESS_FAILURE_BOUNDARY_FAILED: Recommendation.HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_SUCCESS_FAILURE,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_AUDIT_BOUNDARY_FAILED: Recommendation.COMPLETE_FINAL_OFFLINE_RUNNER_SAFETY_AUDIT,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_GO_NO_GO_BOUNDARY_FAILED: Recommendation.HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_GO_NO_GO,
    Risk.FINAL_OFFLINE_RUNNER_SAFETY_ABORT_BOUNDARY_FAILED: Recommendation.HARDEN_FINAL_OFFLINE_RUNNER_SAFETY_ABORT,
    Risk.REAL_EXECUTION_BOUNDARY_VIOLATION: Recommendation.RESTORE_OFFLINE_BOUNDARIES,
    Risk.DATA_ACCESS_VIOLATION: Recommendation.REMOVE_DATA_ACCESS,
    Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN: Recommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN,
}


def generate_final_offline_runner_safety_gate_recommendations(data, risks: Iterable[Risk] | None = None) -> tuple[Recommendation, ...]:
    risks = tuple(risks if risks is not None else detect_final_offline_runner_safety_gate_risks(data))
    if not risks:
        return (
            Recommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE_SUITE,
            Recommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN,
        )
    recommendations = [Recommendation.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN]
    recommendations.extend(_RISK_TO_RECOMMENDATION.get(risk, Recommendation.RESTORE_OFFLINE_BOUNDARIES) for risk in risks)
    return _dedupe(recommendations)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE
    blocking = {Risk.REAL_EXECUTION_BOUNDARY_VIOLATION, Risk.DATA_ACCESS_VIOLATION, Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN}
    if any(risk in blocking for risk in risks):
        return Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE
    for risk in risks:
        decision = _RISK_TO_DECISION.get(risk)
        if decision is not None:
            return decision
    return Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE


def _state_for(data, risks: tuple[Risk, ...], score: m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateScore) -> m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateState:
    if _plan(data) is None:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateState.FINAL_OFFLINE_RUNNER_SAFETY_GATE_INPUT_INVALID
    if not risks and score.overall_score >= 85:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN
    if risks:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateState.FINAL_OFFLINE_RUNNER_SAFETY_GATE_BLOCKED
    if score.overall_score >= 70:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateState.FINAL_OFFLINE_RUNNER_SAFETY_GATE_COMPLETED_WITH_WARNINGS
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateState.NOT_READY


def render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_safety_gate_markdown(result) -> str:
    risks = ", ".join(_value(risk) for risk in result.risks) or "none"
    recommendations = ", ".join(_value(recommendation) for recommendation in result.recommendations) or "none"
    return "\n".join((
        "# Paper Broker Read-Only Connection Dry Run Controlled Offline Runner Safety Gate",
        f"- State: {_value(result.state)}",
        f"- Decision: {_value(result.decision)}",
        f"- Score: {result.score.overall_score}",
        f"- Risks: {risks}",
        f"- Recommendations: {recommendations}",
        "- Boundary: offline/sandbox safety gate only; no runner creation, no runner execution, no dry-run, no broker connection, no secrets, no network, no orders, no position mutation, no data access.",
        f"- Next phase: {result.next_phase}",
    ))


def evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_safety_gate(data=None):
    data = _coerce_input(data)
    boundaries = _boundaries(data)
    score = compute_final_offline_runner_safety_gate_score(data, boundaries)
    risks = detect_final_offline_runner_safety_gate_risks(data, boundaries)
    recommendations = generate_final_offline_runner_safety_gate_recommendations(data, risks)
    decision = _decision_for(risks)
    state = _state_for(data, risks, score)
    summary = "Offline runner safety gate approved for preparation" if not risks else "Offline runner safety gate blocked"
    result = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateResult(
        state=state,
        decision=decision,
        score=score,
        risks=risks,
        recommendations=recommendations,
        summary=summary,
        offline_only=True,
        sandbox_only=True,
        safety_gate_only=True,
        runner_created=False,
        runner_executed=False,
        dry_run_executed=False,
        findings=tuple(boundaries.values()),
        **boundaries,
    )
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalSafetyGateResult(
        **{**result.__dict__, "markdown_report": render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_safety_gate_markdown(result)}
    )
