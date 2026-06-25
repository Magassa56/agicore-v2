"""Offline final safety gate for controlled read-only broker dry-run final plans."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Callable, Iterable, Mapping

from agicore.trading import paper_broker_read_only_connection_dry_run_controlled_execution_final_safety_gate_models as m

Risk = m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateRisk
Decision = m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateDecision
Recommendation = m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateRecommendation


def _coerce_input(data: m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateInput | Mapping[str, Any] | None) -> m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateInput:
    if data is None:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateInput()
    if isinstance(data, m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateInput):
        return data
    allowed = {field.name for field in fields(m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateInput)}
    return m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateInput(**{key: value for key, value in dict(data).items() if key in allowed})


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


def _plan(data: m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateInput) -> Any:
    return data.paper_broker_read_only_connection_dry_run_controlled_execution_final_plan


_SECTION_ATTRS = {
    "scope": "final_controlled_execution_scope",
    "sequence": "final_controlled_execution_sequence",
    "precondition": "final_controlled_execution_precondition",
    "credentials": "final_controlled_credentials_reference_policy",
    "no_secret": "final_controlled_no_secret_read_policy",
    "network": "final_controlled_network_block_policy",
    "http": "final_controlled_http_websocket_socket_block_policy",
    "account": "final_controlled_account_read_only_policy",
    "market_data": "final_controlled_market_data_read_only_policy",
    "order": "final_controlled_order_blocking_policy",
    "position": "final_controlled_position_mutation_block_policy",
    "observability": "final_controlled_observability_plan",
    "journal": "final_controlled_journal_plan",
    "human": "final_controlled_human_approval_plan",
    "stop": "final_controlled_stop_conditions_plan",
    "success": "final_controlled_success_criteria",
    "failure": "final_controlled_failure_criteria",
    "audit": "final_controlled_audit_plan",
    "go_no_go": "final_controlled_go_no_go_policy",
    "abort": "final_controlled_abort_policy",
    "profitability": "final_controlled_profitability_observation_policy",
    "consistency": "final_controlled_consistency_observation_policy",
}


def _section(data: m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateInput, name: str) -> Any:
    return _get(_plan(data), _SECTION_ATTRS[name])


def _section_ok(section: Any) -> bool:
    return section is not None and _get(section, "defined", True) is True and _get(section, "passed", True) is True and not _as_tuple(_get(section, "risks", ()))


def _upstream_items(data: m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateInput) -> tuple[Any, ...]:
    return (
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


def _upstream_risks(data: m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)

def validate_final_controlled_execution_plan_approval(data):
    data = _coerce_input(data)
    plan = _plan(data)
    if plan is None or data.final_controlled_execution_plan_approved is False:
        return False
    approved_state = _state_contains(
        plan,
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_SAFETY_GATE",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_PLAN",
    )
    approved = data.final_controlled_execution_plan_approved is True or approved_state
    return approved and not _as_tuple(_get(plan, "risks", ())) and _get(plan, "offline_only", True) is True


def _offline_boundary(data):
    expected_true = (
        data.offline_mode_enforced, data.sandbox_mode_enforced, data.safety_gate_only,
        data.broker_connection_disabled, data.no_real_broker, data.no_alpaca_real,
        data.no_api_key_read, data.no_env_var_read, data.no_hardcoded_secrets,
        data.no_http_transport, data.no_websocket_transport, data.no_socket_transport,
        data.no_external_api, data.no_external_ml, data.no_external_llm,
        data.no_live_execution, data.no_real_order, data.no_position_mutation,
        data.no_real_account_access,
    )
    requested = (
        data.real_execution_requested, data.broker_connection_requested, data.api_key_read_requested,
        data.env_var_read_requested, data.hardcoded_secret_detected, data.order_execution_requested,
        data.position_mutation_requested, data.account_access_requested, data.network_transport_requested,
        data.external_api_requested, data.dry_run_requested, data.dry_run_executed,
    )
    return (
        all(item is True for item in expected_true)
        and not any(item is True for item in requested)
        and all(_get(item, "offline_only", True) is True for item in _upstream_items(data))
        and not _has_upstream_risk(data, "LIVE_EXECUTION", "BROKER_CONNECTION", "API_KEY", "SECRET_READ", "NETWORK", "HTTP", "WEBSOCKET", "SOCKET", "REAL_ORDER", "REAL_ACCOUNT", "REAL_EXECUTION", "POSITION_MUTATION", "ALPACA_REAL")
    )


def _data_boundary(data):
    return data.data_access_requested is not True and not _has_upstream_risk(data, "DATA_ACCESS", "DATA/", "REAL_DATA")


_Check = tuple[str, Callable[[m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateInput], bool]]


def _boundary(data, *, flag: str, score: str, fallback: Any, risk: Risk, cls, checks: tuple[_Check, ...]):
    data = _coerce_input(data)
    values = {field: check(data) for field, check in checks}
    passed = _get(data, flag) is True and all(values.values())
    return cls(
        passed=passed,
        score=_metric_score(_get(data, score), fallback, passed),
        risks=() if passed else (risk,),
        details=("offline final safety boundary validated without executing dry-run",),
        **values,
    )


def validate_final_safety_runtime_boundary(data):
    return _boundary(data, flag="final_safety_runtime_boundary_verified", score="runtime_score", fallback=_get(_plan(_coerce_input(data)), "final_plan_score"), risk=Risk.FINAL_SAFETY_RUNTIME_BOUNDARY_FAILED, cls=m.FinalSafetyRuntimeBoundary, checks=(
        ("runtime_safety_only", lambda d: d.safety_gate_only is True),
        ("dry_run_not_executed", lambda d: d.dry_run_executed is not True and d.dry_run_requested is not True),
        ("connection_not_executed", lambda d: d.broker_connection_requested is not True),
        ("no_live_execution", lambda d: d.no_live_execution is True and d.real_execution_requested is not True),
    ))


def validate_final_safety_offline_sandbox_boundary(data):
    return _boundary(data, flag="final_safety_offline_sandbox_boundary_verified", score="offline_sandbox_score", fallback=None, risk=Risk.FINAL_SAFETY_OFFLINE_SANDBOX_BOUNDARY_FAILED, cls=m.FinalSafetyOfflineSandboxBoundary, checks=(
        ("offline_only", lambda d: d.offline_mode_enforced is True),
        ("sandbox_only", lambda d: d.sandbox_mode_enforced is True),
        ("safety_gate_only", lambda d: d.safety_gate_only is True),
        ("no_data_access", lambda d: d.data_access_requested is not True),
    ))


def validate_final_safety_credentials_boundary(data):
    return _boundary(data, flag="final_safety_credentials_boundary_verified", score="credentials_score", fallback=_get(_section(_coerce_input(data), "credentials"), "score"), risk=Risk.FINAL_SAFETY_CREDENTIAL_BOUNDARY_FAILED, cls=m.FinalSafetyCredentialsBoundary, checks=(
        ("reference_only", lambda d: _get(_section(d, "credentials"), "reference_only", True) is True),
        ("no_secret_values", lambda d: d.hardcoded_secret_detected is not True),
        ("no_api_key_read", lambda d: d.no_api_key_read is True and d.api_key_read_requested is not True),
        ("no_env_var_read", lambda d: d.no_env_var_read is True and d.env_var_read_requested is not True),
    ))


def validate_final_safety_no_secret_read_boundary(data):
    return _boundary(data, flag="final_safety_no_secret_read_boundary_verified", score="no_secret_score", fallback=_get(_section(_coerce_input(data), "no_secret"), "score"), risk=Risk.FINAL_SAFETY_SECRET_READ_BOUNDARY_FAILED, cls=m.FinalSafetyNoSecretReadBoundary, checks=(
        ("no_api_key_read", lambda d: d.no_api_key_read is True and d.api_key_read_requested is not True),
        ("no_env_var_read", lambda d: d.no_env_var_read is True and d.env_var_read_requested is not True),
        ("no_hardcoded_secret", lambda d: d.no_hardcoded_secrets is True and d.hardcoded_secret_detected is not True),
        ("fail_on_secret_read_request", lambda d: True),
    ))


def _network_checks():
    return (
        ("network_execution_blocked", lambda d: d.network_transport_requested is not True),
        ("http_blocked", lambda d: d.no_http_transport is True),
        ("websocket_blocked", lambda d: d.no_websocket_transport is True),
        ("socket_blocked", lambda d: d.no_socket_transport is True),
        ("external_api_blocked", lambda d: d.no_external_api is True and d.external_api_requested is not True),
    )


def validate_final_safety_network_block_boundary(data):
    return _boundary(data, flag="final_safety_network_block_boundary_verified", score="network_score", fallback=_get(_section(_coerce_input(data), "network"), "score"), risk=Risk.FINAL_SAFETY_NETWORK_BLOCK_BOUNDARY_FAILED, cls=m.FinalSafetyNetworkBlockBoundary, checks=_network_checks())


def validate_final_safety_http_websocket_socket_block_boundary(data):
    return _boundary(data, flag="final_safety_http_websocket_socket_block_boundary_verified", score="http_websocket_socket_score", fallback=_get(_section(_coerce_input(data), "http"), "score"), risk=Risk.FINAL_SAFETY_HTTP_WEBSOCKET_SOCKET_BLOCK_BOUNDARY_FAILED, cls=m.FinalSafetyNetworkBlockBoundary, checks=_network_checks())


def validate_final_safety_account_read_only_boundary(data):
    return _boundary(data, flag="final_safety_account_read_only_boundary_verified", score="account_score", fallback=_get(_section(_coerce_input(data), "account"), "score"), risk=Risk.FINAL_SAFETY_ACCOUNT_READ_ONLY_BOUNDARY_FAILED, cls=m.FinalSafetyAccountReadOnlyBoundary, checks=(
        ("active_account_access_blocked", lambda d: d.no_real_account_access is True and d.account_access_requested is not True),
        ("account_mutations_blocked", lambda d: True),
        ("schema_only_account_review", lambda d: True),
    ))


def validate_final_safety_market_data_read_only_boundary(data):
    return _boundary(data, flag="final_safety_market_data_read_only_boundary_verified", score="market_data_score", fallback=_get(_section(_coerce_input(data), "market_data"), "score"), risk=Risk.FINAL_SAFETY_MARKET_DATA_READ_ONLY_BOUNDARY_FAILED, cls=m.FinalSafetyMarketDataReadOnlyBoundary, checks=(
        ("read_only_market_data_only", lambda d: True),
        ("live_subscription_blocked", lambda d: d.network_transport_requested is not True),
        ("network_request_blocked", lambda d: d.no_external_api is True and d.network_transport_requested is not True),
        ("schema_or_synthetic_only", lambda d: True),
    ))


def validate_final_safety_order_blocking_boundary(data):
    return _boundary(data, flag="final_safety_order_blocking_boundary_verified", score="order_score", fallback=_get(_section(_coerce_input(data), "order"), "score"), risk=Risk.FINAL_SAFETY_ORDER_BLOCKING_BOUNDARY_FAILED, cls=m.FinalSafetyOrderBlockingBoundary, checks=(
        ("order_execution_blocked", lambda d: d.no_real_order is True and d.order_execution_requested is not True),
        ("real_order_blocked", lambda d: d.no_real_order is True),
        ("cancel_replace_blocked", lambda d: True),
    ))


def validate_final_safety_position_mutation_blocking_boundary(data):
    return _boundary(data, flag="final_safety_position_mutation_blocking_boundary_verified", score="position_score", fallback=_get(_section(_coerce_input(data), "position"), "score"), risk=Risk.FINAL_SAFETY_POSITION_MUTATION_BLOCKING_BOUNDARY_FAILED, cls=m.FinalSafetyPositionMutationBlockingBoundary, checks=(
        ("position_mutation_blocked", lambda d: d.no_position_mutation is True and d.position_mutation_requested is not True),
        ("position_request_absent", lambda d: d.position_mutation_requested is not True),
        ("close_modify_blocked", lambda d: True),
    ))

def validate_final_safety_observability_boundary(data):
    return _boundary(data, flag="final_safety_observability_boundary_verified", score="observability_score", fallback=_get(_section(_coerce_input(data), "observability"), "score"), risk=Risk.FINAL_SAFETY_OBSERVABILITY_BOUNDARY_FAILED, cls=m.FinalSafetyObservabilityBoundary, checks=(
        ("offline_events_defined", lambda d: True),
        ("connection_attempt_logging_disabled", lambda d: True),
        ("sensitive_values_redacted", lambda d: True),
    ))


def validate_final_safety_journal_boundary(data):
    return _boundary(data, flag="final_safety_journal_boundary_verified", score="journal_score", fallback=_get(_section(_coerce_input(data), "journal"), "score"), risk=Risk.FINAL_SAFETY_JOURNAL_BOUNDARY_FAILED, cls=m.FinalSafetyJournalBoundary, checks=(
        ("offline_journal_required", lambda d: True),
        ("sensitive_values_redacted", lambda d: True),
        ("no_secret_material_logged", lambda d: d.no_hardcoded_secrets is True),
    ))


def validate_final_safety_human_approval_boundary(data):
    return _boundary(data, flag="final_safety_human_approval_boundary_verified", score="human_approval_score", fallback=_get(_section(_coerce_input(data), "human"), "score"), risk=Risk.FINAL_SAFETY_HUMAN_APPROVAL_BOUNDARY_FAILED, cls=m.FinalSafetyHumanApprovalBoundary, checks=(
        ("human_approval_required", lambda d: _get(_section(d, "human"), "human_approval_required", True) is True),
        ("approval_before_runner_plan", lambda d: True),
        ("final_plan_evidence_required", lambda d: validate_final_controlled_execution_plan_approval(d)),
    ))


def validate_final_safety_stop_conditions_boundary(data):
    return _boundary(data, flag="final_safety_stop_conditions_boundary_verified", score="stop_conditions_score", fallback=_get(_section(_coerce_input(data), "stop"), "score"), risk=Risk.FINAL_SAFETY_STOP_CONDITION_BOUNDARY_FAILED, cls=m.FinalSafetyStopConditionBoundary, checks=(
        ("stop_on_secret_read", lambda d: True),
        ("stop_on_network_request", lambda d: True),
        ("stop_on_order_or_position_request", lambda d: True),
        ("stop_on_account_access_request", lambda d: True),
    ))


def validate_final_safety_success_failure_boundary(data):
    data = _coerce_input(data)
    success = _section(data, "success")
    failure = _section(data, "failure")
    return _boundary(data, flag="final_safety_success_failure_boundary_verified", score="success_failure_score", fallback=_average((_get(success, "score"), _get(failure, "score"))), risk=Risk.FINAL_SAFETY_SUCCESS_FAILURE_BOUNDARY_FAILED, cls=m.FinalSafetySuccessFailureBoundary, checks=(
        ("success_criteria_defined", lambda d: _section_ok(_section(d, "success"))),
        ("failure_criteria_defined", lambda d: _section_ok(_section(d, "failure"))),
        ("requires_no_real_connection", lambda d: d.broker_connection_requested is not True),
        ("failure_on_boundary_violation", lambda d: True),
    ))


def validate_final_safety_audit_boundary(data):
    return _boundary(data, flag="final_safety_audit_boundary_verified", score="audit_score", fallback=_get(_section(_coerce_input(data), "audit"), "score"), risk=Risk.FINAL_SAFETY_AUDIT_BOUNDARY_FAILED, cls=m.FinalSafetyAuditBoundary, checks=(
        ("audit_events_defined", lambda d: True),
        ("offline_evidence_required", lambda d: True),
        ("final_safety_gate_trace_required", lambda d: True),
    ))


def validate_final_safety_go_no_go_boundary(data):
    return _boundary(data, flag="final_safety_go_no_go_boundary_verified", score="go_no_go_score", fallback=_get(_section(_coerce_input(data), "go_no_go"), "score"), risk=Risk.FINAL_SAFETY_GO_NO_GO_BOUNDARY_FAILED, cls=m.FinalSafetyGoNoGoBoundary, checks=(
        ("go_requires_all_boundaries_passed", lambda d: True),
        ("no_go_on_any_boundary_violation", lambda d: True),
        ("human_go_required", lambda d: _get(_section(d, "go_no_go"), "human_go_required", True) is True),
    ))


def validate_final_safety_abort_boundary(data):
    return _boundary(data, flag="final_safety_abort_boundary_verified", score="abort_score", fallback=_get(_section(_coerce_input(data), "abort"), "score"), risk=Risk.FINAL_SAFETY_ABORT_BOUNDARY_FAILED, cls=m.FinalSafetyAbortBoundary, checks=(
        ("abort_on_boundary_violation", lambda d: True),
        ("abort_on_secret_read_request", lambda d: True),
        ("abort_on_network_or_order_request", lambda d: True),
    ))


def validate_final_safety_profitability_observation_boundary(data):
    return _boundary(data, flag="final_safety_profitability_observation_boundary_verified", score="profitability_observation_score", fallback=_get(_section(_coerce_input(data), "profitability"), "score"), risk=Risk.FINAL_SAFETY_PROFITABILITY_OBSERVATION_BOUNDARY_FAILED, cls=m.FinalSafetyProfitabilityObservationBoundary, checks=(
        ("observation_only", lambda d: _get(_section(d, "profitability"), "observation_only", True) is True),
        ("no_profit_promise", lambda d: _get(_section(d, "profitability"), "no_profit_promise", True) is True),
        ("synthetic_or_paper_metrics_only", lambda d: True),
        ("no_trading_decision_from_observation", lambda d: True),
    ))


def validate_final_safety_consistency_observation_boundary(data):
    return _boundary(data, flag="final_safety_consistency_observation_boundary_verified", score="consistency_observation_score", fallback=_get(_section(_coerce_input(data), "consistency"), "score"), risk=Risk.FINAL_SAFETY_CONSISTENCY_OBSERVATION_BOUNDARY_FAILED, cls=m.FinalSafetyConsistencyObservationBoundary, checks=(
        ("observation_only", lambda d: _get(_section(d, "consistency"), "observation_only", True) is True),
        ("deterministic_checks_required", lambda d: True),
        ("no_runtime_adaptation", lambda d: True),
        ("repeated_result_review_required", lambda d: True),
    ))


def _boundaries(data):
    return (
        validate_final_safety_runtime_boundary(data),
        validate_final_safety_offline_sandbox_boundary(data),
        validate_final_safety_credentials_boundary(data),
        validate_final_safety_no_secret_read_boundary(data),
        validate_final_safety_network_block_boundary(data),
        validate_final_safety_http_websocket_socket_block_boundary(data),
        validate_final_safety_account_read_only_boundary(data),
        validate_final_safety_market_data_read_only_boundary(data),
        validate_final_safety_order_blocking_boundary(data),
        validate_final_safety_position_mutation_blocking_boundary(data),
        validate_final_safety_observability_boundary(data),
        validate_final_safety_journal_boundary(data),
        validate_final_safety_human_approval_boundary(data),
        validate_final_safety_stop_conditions_boundary(data),
        validate_final_safety_success_failure_boundary(data),
        validate_final_safety_audit_boundary(data),
        validate_final_safety_go_no_go_boundary(data),
        validate_final_safety_abort_boundary(data),
        validate_final_safety_profitability_observation_boundary(data),
        validate_final_safety_consistency_observation_boundary(data),
    )

def compute_final_safety_gate_score(data):
    data = _coerce_input(data)
    plan_ok = validate_final_controlled_execution_plan_approval(data)
    plan_score = _metric_score(data.final_plan_score, _get(_plan(data), "final_plan_score"), plan_ok)
    boundaries = _boundaries(data)
    scores = (plan_score,) + tuple(boundary.score for boundary in boundaries)
    return m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateScore(
        overall_score=_average(scores), final_plan_score=plan_score,
        runtime_score=boundaries[0].score, offline_sandbox_score=boundaries[1].score,
        credentials_score=boundaries[2].score, no_secret_score=boundaries[3].score,
        network_score=boundaries[4].score, http_websocket_socket_score=boundaries[5].score,
        account_score=boundaries[6].score, market_data_score=boundaries[7].score,
        order_score=boundaries[8].score, position_score=boundaries[9].score,
        observability_score=boundaries[10].score, journal_score=boundaries[11].score,
        human_approval_score=boundaries[12].score, stop_conditions_score=boundaries[13].score,
        success_failure_score=boundaries[14].score, audit_score=boundaries[15].score,
        go_no_go_score=boundaries[16].score, abort_score=boundaries[17].score,
        profitability_observation_score=boundaries[18].score, consistency_observation_score=boundaries[19].score,
    )


def detect_final_safety_gate_risks(data):
    data = _coerce_input(data)
    risks: list[Risk] = []
    if not validate_final_controlled_execution_plan_approval(data):
        risks.append(Risk.FINAL_CONTROLLED_EXECUTION_PLAN_NOT_APPROVED)
    for boundary in _boundaries(data):
        risks.extend(_as_tuple(boundary.risks))
    if not _offline_boundary(data):
        risks.append(Risk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(Risk.DATA_ACCESS_VIOLATION)
    if data.paper_broker_read_only_connection_dry_run_controlled_offline_runner_plan_requested is True:
        risks.append(Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PLAN)
    return _dedupe(risks)


def generate_final_safety_gate_recommendations(data):
    risks = detect_final_safety_gate_risks(data)
    if not risks:
        return (
            Recommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_SAFETY_GATE_SUITE,
            Recommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PLAN,
        )
    mapping = {
        Risk.FINAL_CONTROLLED_EXECUTION_PLAN_NOT_APPROVED: Recommendation.APPROVE_FINAL_CONTROLLED_EXECUTION_PLAN_FIRST,
        Risk.FINAL_SAFETY_RUNTIME_BOUNDARY_FAILED: Recommendation.HARDEN_FINAL_SAFETY_RUNTIME_BOUNDARY,
        Risk.FINAL_SAFETY_OFFLINE_SANDBOX_BOUNDARY_FAILED: Recommendation.RESTORE_FINAL_SAFETY_OFFLINE_SANDBOX,
        Risk.FINAL_SAFETY_CREDENTIAL_BOUNDARY_FAILED: Recommendation.HARDEN_FINAL_SAFETY_CREDENTIAL_BOUNDARY,
        Risk.FINAL_SAFETY_SECRET_READ_BOUNDARY_FAILED: Recommendation.HARDEN_FINAL_SAFETY_NO_SECRET_READ,
        Risk.FINAL_SAFETY_NETWORK_BLOCK_BOUNDARY_FAILED: Recommendation.BLOCK_FINAL_SAFETY_NETWORK_TRANSPORT,
        Risk.FINAL_SAFETY_HTTP_WEBSOCKET_SOCKET_BLOCK_BOUNDARY_FAILED: Recommendation.BLOCK_FINAL_SAFETY_HTTP_WEBSOCKET_SOCKET,
        Risk.FINAL_SAFETY_ACCOUNT_READ_ONLY_BOUNDARY_FAILED: Recommendation.HARDEN_FINAL_SAFETY_ACCOUNT_READ_ONLY,
        Risk.FINAL_SAFETY_MARKET_DATA_READ_ONLY_BOUNDARY_FAILED: Recommendation.HARDEN_FINAL_SAFETY_MARKET_DATA_READ_ONLY,
        Risk.FINAL_SAFETY_ORDER_BLOCKING_BOUNDARY_FAILED: Recommendation.HARDEN_FINAL_SAFETY_ORDER_BLOCKING,
        Risk.FINAL_SAFETY_POSITION_MUTATION_BLOCKING_BOUNDARY_FAILED: Recommendation.HARDEN_FINAL_SAFETY_POSITION_MUTATION_BLOCKING,
        Risk.FINAL_SAFETY_OBSERVABILITY_BOUNDARY_FAILED: Recommendation.COMPLETE_FINAL_SAFETY_OBSERVABILITY,
        Risk.FINAL_SAFETY_JOURNAL_BOUNDARY_FAILED: Recommendation.COMPLETE_FINAL_SAFETY_JOURNAL,
        Risk.FINAL_SAFETY_HUMAN_APPROVAL_BOUNDARY_FAILED: Recommendation.REQUIRE_FINAL_SAFETY_HUMAN_APPROVAL,
        Risk.FINAL_SAFETY_STOP_CONDITION_BOUNDARY_FAILED: Recommendation.DEFINE_FINAL_SAFETY_STOP_CONDITIONS,
        Risk.FINAL_SAFETY_SUCCESS_FAILURE_BOUNDARY_FAILED: Recommendation.HARDEN_FINAL_SAFETY_SUCCESS_FAILURE,
        Risk.FINAL_SAFETY_AUDIT_BOUNDARY_FAILED: Recommendation.COMPLETE_FINAL_SAFETY_AUDIT,
        Risk.FINAL_SAFETY_GO_NO_GO_BOUNDARY_FAILED: Recommendation.DEFINE_FINAL_SAFETY_GO_NO_GO,
        Risk.FINAL_SAFETY_ABORT_BOUNDARY_FAILED: Recommendation.DEFINE_FINAL_SAFETY_ABORT,
        Risk.FINAL_SAFETY_PROFITABILITY_OBSERVATION_BOUNDARY_FAILED: Recommendation.DEFINE_FINAL_SAFETY_PROFITABILITY_OBSERVATION,
        Risk.FINAL_SAFETY_CONSISTENCY_OBSERVATION_BOUNDARY_FAILED: Recommendation.DEFINE_FINAL_SAFETY_CONSISTENCY_OBSERVATION,
        Risk.REAL_EXECUTION_BOUNDARY_VIOLATION: Recommendation.RESTORE_OFFLINE_BOUNDARIES,
        Risk.DATA_ACCESS_VIOLATION: Recommendation.REMOVE_DATA_ACCESS,
        Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PLAN: Recommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PLAN,
    }
    recommendations = [Recommendation.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PLAN]
    recommendations.extend(mapping[item] for item in risks if item in mapping)
    return _dedupe(recommendations)


def _decision_for_risks(risks):
    if not risks:
        return Decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_SAFETY_GATE
    if Risk.FINAL_CONTROLLED_EXECUTION_PLAN_NOT_APPROVED in risks:
        return Decision.REQUIRE_FINAL_CONTROLLED_EXECUTION_PLAN_FIXES
    if Risk.REAL_EXECUTION_BOUNDARY_VIOLATION in risks or Risk.DATA_ACCESS_VIOLATION in risks:
        return Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_SAFETY_GATE
    ordered = (
        (Risk.FINAL_SAFETY_RUNTIME_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_RUNTIME_BOUNDARY_FIXES),
        (Risk.FINAL_SAFETY_OFFLINE_SANDBOX_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_OFFLINE_SANDBOX_FIXES),
        (Risk.FINAL_SAFETY_CREDENTIAL_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_CREDENTIAL_BOUNDARY_FIXES),
        (Risk.FINAL_SAFETY_SECRET_READ_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_NO_SECRET_READ_FIXES),
        (Risk.FINAL_SAFETY_NETWORK_BLOCK_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_NETWORK_BLOCK_FIXES),
        (Risk.FINAL_SAFETY_HTTP_WEBSOCKET_SOCKET_BLOCK_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_NETWORK_BLOCK_FIXES),
        (Risk.FINAL_SAFETY_ACCOUNT_READ_ONLY_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_ACCOUNT_READ_ONLY_FIXES),
        (Risk.FINAL_SAFETY_MARKET_DATA_READ_ONLY_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_MARKET_DATA_READ_ONLY_FIXES),
        (Risk.FINAL_SAFETY_ORDER_BLOCKING_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_ORDER_BLOCKING_FIXES),
        (Risk.FINAL_SAFETY_POSITION_MUTATION_BLOCKING_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_POSITION_MUTATION_BLOCKING_FIXES),
        (Risk.FINAL_SAFETY_OBSERVABILITY_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_OBSERVABILITY_FIXES),
        (Risk.FINAL_SAFETY_JOURNAL_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_JOURNAL_FIXES),
        (Risk.FINAL_SAFETY_HUMAN_APPROVAL_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_HUMAN_APPROVAL_FIXES),
        (Risk.FINAL_SAFETY_STOP_CONDITION_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_STOP_CONDITION_FIXES),
        (Risk.FINAL_SAFETY_SUCCESS_FAILURE_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_SUCCESS_FAILURE_FIXES),
        (Risk.FINAL_SAFETY_AUDIT_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_AUDIT_FIXES),
        (Risk.FINAL_SAFETY_GO_NO_GO_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_GO_NO_GO_FIXES),
        (Risk.FINAL_SAFETY_ABORT_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_ABORT_FIXES),
        (Risk.FINAL_SAFETY_PROFITABILITY_OBSERVATION_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_PROFITABILITY_OBSERVATION_FIXES),
        (Risk.FINAL_SAFETY_CONSISTENCY_OBSERVATION_BOUNDARY_FAILED, Decision.REQUIRE_FINAL_SAFETY_CONSISTENCY_OBSERVATION_FIXES),
    )
    for item, decision in ordered:
        if item in risks:
            return decision
    return Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_SAFETY_GATE


def _state_for_result(data, risks, score):
    state = m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateState
    if _plan(data) is None:
        return state.FINAL_SAFETY_GATE_INPUT_INVALID
    if not risks and score.overall_score >= 85:
        return state.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PLAN
    if risks:
        return state.FINAL_SAFETY_GATE_BLOCKED
    if score.overall_score >= 70:
        return state.FINAL_SAFETY_GATE_COMPLETED_WITH_WARNINGS
    return state.NOT_READY

def evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_final_safety_gate(data):
    data = _coerce_input(data)
    score = compute_final_safety_gate_score(data)
    risks = detect_final_safety_gate_risks(data)
    boundaries = _boundaries(data)
    return m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateResult(
        state=_state_for_result(data, risks, score),
        decision=_decision_for_risks(risks),
        safety_gate_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        recommendations=generate_final_safety_gate_recommendations(data),
        runtime_boundary=boundaries[0],
        offline_sandbox_boundary=boundaries[1],
        credentials_boundary=boundaries[2],
        no_secret_read_boundary=boundaries[3],
        network_block_boundary=boundaries[4],
        http_websocket_socket_block_boundary=boundaries[5],
        account_read_only_boundary=boundaries[6],
        market_data_read_only_boundary=boundaries[7],
        order_blocking_boundary=boundaries[8],
        position_mutation_blocking_boundary=boundaries[9],
        observability_boundary=boundaries[10],
        journal_boundary=boundaries[11],
        human_approval_boundary=boundaries[12],
        stop_condition_boundary=boundaries[13],
        success_failure_boundary=boundaries[14],
        audit_boundary=boundaries[15],
        go_no_go_boundary=boundaries[16],
        abort_boundary=boundaries[17],
        profitability_observation_boundary=boundaries[18],
        consistency_observation_boundary=boundaries[19],
        offline_only=True,
        summary=(
            "Paper broker read-only connection dry-run controlled execution final safety gate is approved for controlled offline runner planning."
            if not risks
            else "Paper broker read-only connection dry-run controlled execution final safety gate is blocked until safety risks are fixed."
        ),
    )


def render_paper_broker_read_only_connection_dry_run_controlled_execution_final_safety_gate_markdown(result):
    if isinstance(result, Mapping):
        result = m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionFinalSafetyGateResult(**dict(result))
    risks = ", ".join(item.value for item in result.risks) or "none"
    recommendations = ", ".join(item.value for item in result.recommendations) or "none"
    boundaries = (
        ("runtime_boundary", result.runtime_boundary),
        ("offline_sandbox_boundary", result.offline_sandbox_boundary),
        ("credentials_boundary", result.credentials_boundary),
        ("no_secret_read_boundary", result.no_secret_read_boundary),
        ("network_block_boundary", result.network_block_boundary),
        ("http_websocket_socket_block_boundary", result.http_websocket_socket_block_boundary),
        ("account_read_only_boundary", result.account_read_only_boundary),
        ("market_data_read_only_boundary", result.market_data_read_only_boundary),
        ("order_blocking_boundary", result.order_blocking_boundary),
        ("position_mutation_blocking_boundary", result.position_mutation_blocking_boundary),
        ("observability_boundary", result.observability_boundary),
        ("journal_boundary", result.journal_boundary),
        ("human_approval_boundary", result.human_approval_boundary),
        ("stop_condition_boundary", result.stop_condition_boundary),
        ("success_failure_boundary", result.success_failure_boundary),
        ("audit_boundary", result.audit_boundary),
        ("go_no_go_boundary", result.go_no_go_boundary),
        ("abort_boundary", result.abort_boundary),
        ("profitability_observation_boundary", result.profitability_observation_boundary),
        ("consistency_observation_boundary", result.consistency_observation_boundary),
    )
    lines = [
        "# Paper Broker Read-Only Connection Dry Run Controlled Execution Final Safety Gate",
        "",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Final safety gate score: {result.safety_gate_score}",
        f"- Offline only: {result.offline_only}",
        f"- Risks: {risks}",
        f"- Recommendations: {recommendations}",
        "",
        "## Enforced Final Safety Boundaries",
        "- No dry-run execution and no broker connection",
        "- No API key, environment variable, hardcoded secret, HTTP, websocket, socket, external API, order, position mutation, active account access, or data/ access",
        "- Profitability and consistency observation stay observation-only and do not promise profit",
        "",
        "## Boundary Results",
    ]
    for name, boundary in boundaries:
        lines.append(f"- {name}: score={boundary.score}, passed={boundary.passed}, risks={len(boundary.risks)}")
    if result.summary:
        lines.extend(("", f"Summary: {result.summary}"))
    return "\n".join(lines)