"""Offline Paper Broker read-only connection plan for AGIcore."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_broker_read_only_connection_plan_models import (
    AccountReadOnlyConnectionPolicy,
    ConnectionEnvironmentBoundary,
    ConnectionHumanApprovalPlan,
    ConnectionJournalPlan,
    ConnectionObservabilityPlan,
    ConnectionPrecondition,
    ConnectionStopConditionPlan,
    CredentialsReferencePolicy,
    MarketDataReadOnlyConnectionPolicy,
    NetworkExecutionBlockPolicy,
    OrderBlockingConnectionPolicy,
    PaperBrokerReadOnlyConnectionPlanDecision,
    PaperBrokerReadOnlyConnectionPlanInput,
    PaperBrokerReadOnlyConnectionPlanRecommendation,
    PaperBrokerReadOnlyConnectionPlanResult,
    PaperBrokerReadOnlyConnectionPlanRisk,
    PaperBrokerReadOnlyConnectionPlanScore,
    PaperBrokerReadOnlyConnectionPlanState,
    ReadOnlyConnectionScope,
)


def _coerce_input(
    data: PaperBrokerReadOnlyConnectionPlanInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlyConnectionPlanInput:
    if data is None:
        return PaperBrokerReadOnlyConnectionPlanInput()
    if isinstance(data, PaperBrokerReadOnlyConnectionPlanInput):
        return data
    allowed = {field.name for field in fields(PaperBrokerReadOnlyConnectionPlanInput)}
    payload = {key: value for key, value in dict(data).items() if key in allowed}
    return PaperBrokerReadOnlyConnectionPlanInput(**payload)


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
    text_items = tuple(_value(item).upper() for item in _as_tuple(items))
    return any(any(needle.upper() in item for item in text_items) for needle in needles)


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
    if not usable:
        return default
    return _clamp(sum(usable) / len(usable))


def _bool_score(value: bool | None, unknown: int = 35) -> int:
    if value is True:
        return 100
    if value is False:
        return 0
    return unknown


def _metric_score(explicit: int | None, fallback: Any, passed: bool) -> int:
    if explicit is not None:
        return _clamp(explicit)
    if fallback is not None:
        return _clamp(fallback)
    return _bool_score(passed)


def _safe_flag(explicit: bool | None, fallback: Any = None, default: bool = False) -> bool:
    if explicit is not None:
        return explicit is True
    if fallback is not None:
        return fallback is True
    return default


def _safety_review(data: PaperBrokerReadOnlyConnectionPlanInput) -> Any:
    return data.paper_broker_read_only_safety_review


def _review_item(data: PaperBrokerReadOnlyConnectionPlanInput, name: str) -> Any:
    return _get(_safety_review(data), name)


def _upstream_items(data: PaperBrokerReadOnlyConnectionPlanInput) -> tuple[Any, ...]:
    return (
        data.paper_broker_read_only_safety_review,
        data.paper_broker_read_only_preparation,
        data.multi_scenario_result_report,
        data.multi_scenario_controlled_simulation_result,
        data.performance_risk_validation_gate,
        data.performance_metrics_result,
        data.risk_metrics_result,
        data.controlled_simulation_result_report,
        data.controlled_simulation_offline_runner_result,
        data.paper_runtime_forward_test_plan,
        data.official_paper_validation_report,
        data.paper_runtime_validation,
        data.paper_trading_runtime,
        data.observability_verification,
        data.rollback_verification,
        data.kill_switch_verification,
        data.human_validated_paper_session,
        data.supervised_paper_session,
    )


def _upstream_risks(data: PaperBrokerReadOnlyConnectionPlanInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperBrokerReadOnlyConnectionPlanInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _policy_ok(obj: Any) -> bool:
    if obj is None:
        return False
    if _get(obj, "passed") is not None:
        return _get(obj, "passed") is True and not _as_tuple(_get(obj, "risks", ()))
    if _get(obj, "defined") is not None:
        return _get(obj, "defined") is True and not _as_tuple(_get(obj, "risks", ()))
    return not _as_tuple(_get(obj, "risks", ()))


def _offline_boundary(data: PaperBrokerReadOnlyConnectionPlanInput) -> bool:
    return (
        data.offline_mode_enforced is True
        and data.sandbox_mode_enforced is True
        and data.plan_only is True
        and data.broker_connection_disabled is True
        and data.no_real_broker is True
        and data.no_alpaca_real is True
        and data.no_api_key_read is True
        and data.no_env_var_read is True
        and data.no_hardcoded_secrets is True
        and data.no_http_transport is True
        and data.no_websocket_transport is True
        and data.no_socket_transport is True
        and data.no_external_api is True
        and data.no_external_ml is True
        and data.no_external_llm is True
        and data.no_live_execution is True
        and data.no_real_order is True
        and data.no_position_mutation is True
        and data.no_real_account_access is True
        and data.real_execution_requested is not True
        and data.broker_connection_requested is not True
        and data.api_key_read_requested is not True
        and data.env_var_read_requested is not True
        and data.hardcoded_secret_detected is not True
        and data.order_execution_requested is not True
        and data.position_mutation_requested is not True
        and data.account_access_requested is not True
        and data.network_transport_requested is not True
        and all(_get(item, "offline_only", True) is True for item in _upstream_items(data))
        and not _has_upstream_risk(
            data,
            "LIVE_EXECUTION",
            "BROKER_CONNECTIVITY",
            "BROKER_CONNECTION",
            "API_ACCESS",
            "NETWORK",
            "HTTP",
            "WEBSOCKET",
            "SOCKET",
            "REAL_ORDER",
            "REAL_ACCOUNT",
            "REAL_EXECUTION",
            "POSITION_MUTATION",
            "ALPACA_REAL",
        )
    )


def _data_boundary(data: PaperBrokerReadOnlyConnectionPlanInput) -> bool:
    return (
        data.data_access_requested is not True
        and not _has_upstream_risk(data, "DATA_ACCESS", "DATA_ACCESS_VIOLATION", "REAL_DATA")
    )


def validate_read_only_safety_review_approval(
    data: PaperBrokerReadOnlyConnectionPlanInput | Mapping[str, Any] | None,
) -> bool:
    data = _coerce_input(data)
    review = _safety_review(data)
    if review is None or data.read_only_safety_review_approved is False:
        return False
    approved_state = _state_contains(
        review,
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN",
        "APPROVE_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW",
    )
    approved = data.read_only_safety_review_approved is True or approved_state
    return (
        approved
        and not _as_tuple(_get(review, "risks", ()))
        and _get(review, "offline_only", True) is True
        and not _has_upstream_risk(data, "SAFETY_REVIEW_BLOCKED", "REAL_EXECUTION", "DATA_ACCESS")
    )


def define_read_only_connection_scope(
    data: PaperBrokerReadOnlyConnectionPlanInput | Mapping[str, Any] | None,
) -> ReadOnlyConnectionScope:
    data = _coerce_input(data)
    passed = data.read_only_connection_scope_defined is True and data.plan_only is True
    risks = () if passed else (PaperBrokerReadOnlyConnectionPlanRisk.READ_ONLY_CONNECTION_SCOPE_UNCLEAR,)
    score = _metric_score(data.scope_score, None, passed)
    return ReadOnlyConnectionScope(
        score=score,
        defined=data.read_only_connection_scope_defined is True,
        plan_only=data.plan_only is True,
        allowed_actions=("define_future_read_only_connection_plan", "prepare_safety_gate_inputs"),
        prohibited_actions=("connect_broker", "read_secret", "open_socket", "send_order", "mutate_position"),
        risks=risks,
        details=("offline_plan_only", "future_connection_safety_gate_only"),
    )


def define_connection_environment_boundaries(
    data: PaperBrokerReadOnlyConnectionPlanInput | Mapping[str, Any] | None,
) -> ConnectionEnvironmentBoundary:
    data = _coerce_input(data)
    boundary_ok = _offline_boundary(data)
    risks: list[PaperBrokerReadOnlyConnectionPlanRisk] = []
    if data.connection_environment_boundaries_defined is not True:
        risks.append(PaperBrokerReadOnlyConnectionPlanRisk.CONNECTION_ENVIRONMENT_BOUNDARY_MISSING)
    if not boundary_ok:
        risks.append(PaperBrokerReadOnlyConnectionPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    passed = not risks
    score = _metric_score(data.boundary_score, _get(_review_item(data, "broker_environment_boundary_review"), "score"), passed)
    return ConnectionEnvironmentBoundary(
        score=score,
        defined=data.connection_environment_boundaries_defined is True,
        offline_only=data.offline_mode_enforced is True,
        sandbox_only=data.sandbox_mode_enforced is True,
        connection_execution_disabled=data.broker_connection_disabled is True,
        network_transport_disabled=(
            data.no_http_transport is True
            and data.no_websocket_transport is True
            and data.no_socket_transport is True
            and data.network_transport_requested is not True
        ),
        risks=_dedupe(risks),
        details=("no_connection_execution", "offline_sandbox_plan"),
    )


def define_connection_preconditions(
    data: PaperBrokerReadOnlyConnectionPlanInput | Mapping[str, Any] | None,
) -> ConnectionPrecondition:
    data = _coerce_input(data)
    safety_ok = validate_read_only_safety_review_approval(data)
    passed = data.connection_preconditions_defined is True and safety_ok
    risks = () if passed else (PaperBrokerReadOnlyConnectionPlanRisk.CONNECTION_PRECONDITION_MISSING,)
    score = _metric_score(data.precondition_score, None, passed)
    return ConnectionPrecondition(
        score=score,
        defined=data.connection_preconditions_defined is True,
        safety_review_required=True,
        human_approval_required=True,
        stop_conditions_required=True,
        risks=risks,
        details=("approved_safety_review_required", "no_runtime_execution_allowed"),
    )


def define_credentials_reference_policy(
    data: PaperBrokerReadOnlyConnectionPlanInput | Mapping[str, Any] | None,
) -> CredentialsReferencePolicy:
    data = _coerce_input(data)
    reviewed = _review_item(data, "credentials_handling_review")
    safe = (
        data.credentials_reference_policy_defined is True
        and data.credentials_reference_only is True
        and data.no_api_key_read is True
        and data.no_env_var_read is True
        and data.no_hardcoded_secrets is True
        and data.api_key_read_requested is not True
        and data.env_var_read_requested is not True
        and data.hardcoded_secret_detected is not True
        and _policy_ok(reviewed)
    )
    risks = () if safe else (PaperBrokerReadOnlyConnectionPlanRisk.CREDENTIAL_REFERENCE_POLICY_MISSING,)
    score = _metric_score(data.credential_reference_score, _get(reviewed, "score"), safe)
    return CredentialsReferencePolicy(
        score=score,
        defined=data.credentials_reference_policy_defined is True,
        reference_only=data.credentials_reference_only is True,
        no_secret_material=data.no_hardcoded_secrets is True and data.hardcoded_secret_detected is not True,
        no_api_key_read=data.no_api_key_read is True and data.api_key_read_requested is not True,
        no_env_var_read=data.no_env_var_read is True and data.env_var_read_requested is not True,
        risks=risks,
        details=("credential_ids_are_documented_references_only", "no_secret_value_read"),
    )


def define_no_secret_read_policy(
    data: PaperBrokerReadOnlyConnectionPlanInput | Mapping[str, Any] | None,
) -> CredentialsReferencePolicy:
    data = _coerce_input(data)
    secret_blocked = (
        data.no_secret_read_policy_defined is True
        and data.secret_read_blocked is True
        and data.no_api_key_read is True
        and data.no_env_var_read is True
        and data.api_key_read_requested is not True
        and data.env_var_read_requested is not True
        and data.hardcoded_secret_detected is not True
    )
    risks = () if secret_blocked else (PaperBrokerReadOnlyConnectionPlanRisk.SECRET_READ_POLICY_UNSAFE,)
    score = _metric_score(data.no_secret_read_score, _get(_review_item(data, "credentials_handling_review"), "score"), secret_blocked)
    return CredentialsReferencePolicy(
        score=score,
        defined=data.no_secret_read_policy_defined is True,
        reference_only=True,
        no_secret_material=data.hardcoded_secret_detected is not True,
        no_api_key_read=data.no_api_key_read is True and data.api_key_read_requested is not True,
        no_env_var_read=data.no_env_var_read is True and data.env_var_read_requested is not True,
        risks=risks,
        details=("no_api_key_read", "no_environment_variable_read", "no_secret_material"),
    )


def define_network_execution_block_policy(
    data: PaperBrokerReadOnlyConnectionPlanInput | Mapping[str, Any] | None,
) -> NetworkExecutionBlockPolicy:
    data = _coerce_input(data)
    safe = (
        data.network_execution_block_policy_defined is True
        and data.network_execution_blocked is True
        and data.broker_connection_disabled is True
        and data.network_transport_requested is not True
        and data.broker_connection_requested is not True
    )
    risks = () if safe else (PaperBrokerReadOnlyConnectionPlanRisk.NETWORK_EXECUTION_NOT_BLOCKED,)
    score = _metric_score(data.network_block_score, _get(_review_item(data, "broker_environment_boundary_review"), "score"), safe)
    return NetworkExecutionBlockPolicy(
        score=score,
        defined=data.network_execution_block_policy_defined is True,
        network_execution_blocked=data.network_execution_blocked is True,
        http_blocked=data.no_http_transport is True,
        websocket_blocked=data.no_websocket_transport is True,
        socket_blocked=data.no_socket_transport is True,
        external_api_blocked=data.no_external_api is True,
        risks=risks,
        details=("no_network_execution_in_plan_phase",),
    )


def define_http_websocket_socket_block_policy(
    data: PaperBrokerReadOnlyConnectionPlanInput | Mapping[str, Any] | None,
) -> NetworkExecutionBlockPolicy:
    data = _coerce_input(data)
    safe = (
        data.http_websocket_socket_block_policy_defined is True
        and data.http_transport_blocked is True
        and data.websocket_transport_blocked is True
        and data.socket_transport_blocked is True
        and data.no_http_transport is True
        and data.no_websocket_transport is True
        and data.no_socket_transport is True
        and data.network_transport_requested is not True
    )
    risks = () if safe else (PaperBrokerReadOnlyConnectionPlanRisk.HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED,)
    score = _metric_score(
        data.http_websocket_socket_block_score,
        _get(_review_item(data, "broker_environment_boundary_review"), "score"),
        safe,
    )
    return NetworkExecutionBlockPolicy(
        score=score,
        defined=data.http_websocket_socket_block_policy_defined is True,
        network_execution_blocked=True,
        http_blocked=data.http_transport_blocked is True and data.no_http_transport is True,
        websocket_blocked=data.websocket_transport_blocked is True and data.no_websocket_transport is True,
        socket_blocked=data.socket_transport_blocked is True and data.no_socket_transport is True,
        external_api_blocked=data.no_external_api is True,
        risks=risks,
        details=("http_blocked", "websocket_blocked", "socket_blocked"),
    )


def define_account_read_only_connection_policy(
    data: PaperBrokerReadOnlyConnectionPlanInput | Mapping[str, Any] | None,
) -> AccountReadOnlyConnectionPolicy:
    data = _coerce_input(data)
    safe = (
        data.account_read_only_connection_policy_defined is True
        and data.account_active_access_blocked is True
        and data.account_mutations_blocked is True
        and data.no_real_account_access is True
        and data.account_access_requested is not True
        and _policy_ok(_review_item(data, "account_read_only_review"))
    )
    risks = () if safe else (PaperBrokerReadOnlyConnectionPlanRisk.ACCOUNT_READ_ONLY_CONNECTION_UNSAFE,)
    score = _metric_score(data.account_read_only_score, _get(_review_item(data, "account_read_only_review"), "score"), safe)
    return AccountReadOnlyConnectionPolicy(
        score=score,
        defined=data.account_read_only_connection_policy_defined is True,
        active_account_access_blocked=data.account_active_access_blocked is True and data.account_access_requested is not True,
        account_mutations_blocked=data.account_mutations_blocked is True,
        read_only_future_plan=True,
        risks=risks,
        details=("account_access_not_executed", "future_read_only_contract_only"),
    )


def define_market_data_read_only_connection_policy(
    data: PaperBrokerReadOnlyConnectionPlanInput | Mapping[str, Any] | None,
) -> MarketDataReadOnlyConnectionPolicy:
    data = _coerce_input(data)
    safe = (
        data.market_data_read_only_connection_policy_defined is True
        and data.market_data_live_subscription_blocked is True
        and data.network_transport_requested is not True
        and _policy_ok(_review_item(data, "market_data_read_only_review"))
    )
    risks = () if safe else (PaperBrokerReadOnlyConnectionPlanRisk.MARKET_DATA_READ_ONLY_CONNECTION_UNSAFE,)
    score = _metric_score(
        data.market_data_read_only_score,
        _get(_review_item(data, "market_data_read_only_review"), "score"),
        safe,
    )
    return MarketDataReadOnlyConnectionPolicy(
        score=score,
        defined=data.market_data_read_only_connection_policy_defined is True,
        read_only_market_data_plan=True,
        live_subscription_blocked=data.market_data_live_subscription_blocked is True,
        network_request_blocked=data.network_transport_requested is not True,
        risks=risks,
        details=("market_data_read_only_future_plan", "no_live_subscription_test"),
    )


def define_order_blocking_connection_policy(
    data: PaperBrokerReadOnlyConnectionPlanInput | Mapping[str, Any] | None,
) -> OrderBlockingConnectionPolicy:
    data = _coerce_input(data)
    safe = (
        data.order_blocking_connection_policy_defined is True
        and data.order_execution_blocked is True
        and data.no_real_order is True
        and data.order_execution_requested is not True
        and _policy_ok(_review_item(data, "order_blocking_review"))
    )
    risks = () if safe else (PaperBrokerReadOnlyConnectionPlanRisk.ORDER_BLOCKING_CONNECTION_UNSAFE,)
    score = _metric_score(data.order_blocking_score, _get(_review_item(data, "order_blocking_review"), "score"), safe)
    return OrderBlockingConnectionPolicy(
        score=score,
        defined=data.order_blocking_connection_policy_defined is True,
        order_execution_blocked=data.order_execution_blocked is True,
        real_order_blocked=data.no_real_order is True,
        cancel_replace_blocked=True,
        risks=risks,
        details=("submit_cancel_replace_order_paths_blocked",),
    )


def define_position_mutation_block_policy(
    data: PaperBrokerReadOnlyConnectionPlanInput | Mapping[str, Any] | None,
) -> OrderBlockingConnectionPolicy:
    data = _coerce_input(data)
    safe = (
        data.position_mutation_block_policy_defined is True
        and data.position_mutation_blocked is True
        and data.no_position_mutation is True
        and data.position_mutation_requested is not True
        and _policy_ok(_review_item(data, "position_mutation_review"))
    )
    risks = () if safe else (PaperBrokerReadOnlyConnectionPlanRisk.POSITION_MUTATION_BLOCK_UNSAFE,)
    score = _metric_score(
        data.position_mutation_block_score,
        _get(_review_item(data, "position_mutation_review"), "score"),
        safe,
    )
    return OrderBlockingConnectionPolicy(
        score=score,
        defined=data.position_mutation_block_policy_defined is True,
        order_execution_blocked=data.order_execution_blocked is True,
        real_order_blocked=data.no_real_order is True,
        cancel_replace_blocked=data.position_mutation_blocked is True,
        risks=risks,
        details=("position_create_update_close_paths_blocked",),
    )


def define_connection_observability_plan(
    data: PaperBrokerReadOnlyConnectionPlanInput | Mapping[str, Any] | None,
) -> ConnectionObservabilityPlan:
    data = _coerce_input(data)
    safe = data.connection_observability_plan_defined is True and _policy_ok(_review_item(data, "observability_review"))
    risks = () if safe else (PaperBrokerReadOnlyConnectionPlanRisk.OBSERVABILITY_PLAN_MISSING,)
    score = _metric_score(data.observability_score, _get(_review_item(data, "observability_review"), "score"), safe)
    return ConnectionObservabilityPlan(score, data.connection_observability_plan_defined is True, True, True, risks, ("offline_plan_events",))


def define_connection_journal_plan(
    data: PaperBrokerReadOnlyConnectionPlanInput | Mapping[str, Any] | None,
) -> ConnectionJournalPlan:
    data = _coerce_input(data)
    safe = data.connection_journal_plan_defined is True and _policy_ok(_review_item(data, "journal_review"))
    risks = () if safe else (PaperBrokerReadOnlyConnectionPlanRisk.JOURNAL_PLAN_MISSING,)
    score = _metric_score(data.journal_score, _get(_review_item(data, "journal_review"), "score"), safe)
    return ConnectionJournalPlan(score, data.connection_journal_plan_defined is True, True, True, risks, ("redacted_offline_journal",))


def define_connection_human_approval_plan(
    data: PaperBrokerReadOnlyConnectionPlanInput | Mapping[str, Any] | None,
) -> ConnectionHumanApprovalPlan:
    data = _coerce_input(data)
    safe = data.connection_human_approval_plan_defined is True and _policy_ok(_review_item(data, "human_approval_review"))
    risks = () if safe else (PaperBrokerReadOnlyConnectionPlanRisk.HUMAN_APPROVAL_PLAN_MISSING,)
    score = _metric_score(data.human_approval_score, _get(_review_item(data, "human_approval_review"), "score"), safe)
    return ConnectionHumanApprovalPlan(score, data.connection_human_approval_plan_defined is True, True, True, risks, ("approval_before_safety_gate",))


def define_connection_stop_conditions_plan(
    data: PaperBrokerReadOnlyConnectionPlanInput | Mapping[str, Any] | None,
) -> ConnectionStopConditionPlan:
    data = _coerce_input(data)
    safe = data.connection_stop_conditions_plan_defined is True and _policy_ok(_review_item(data, "stop_conditions_review"))
    risks = () if safe else (PaperBrokerReadOnlyConnectionPlanRisk.STOP_CONDITIONS_PLAN_MISSING,)
    score = _metric_score(data.stop_conditions_score, _get(_review_item(data, "stop_conditions_review"), "score"), safe)
    return ConnectionStopConditionPlan(
        score,
        data.connection_stop_conditions_plan_defined is True,
        True,
        True,
        True,
        risks,
        ("stop_on_secret_network_order_position_account_request",),
    )


def compute_read_only_connection_plan_score(
    data: PaperBrokerReadOnlyConnectionPlanInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlyConnectionPlanScore:
    data = _coerce_input(data)
    safety_ok = validate_read_only_safety_review_approval(data)
    safety_score = _metric_score(data.safety_review_score, _get(_safety_review(data), "safety_score"), safety_ok)
    scope = define_read_only_connection_scope(data)
    boundary = define_connection_environment_boundaries(data)
    preconditions = define_connection_preconditions(data)
    credential_reference = define_credentials_reference_policy(data)
    no_secret = define_no_secret_read_policy(data)
    network = define_network_execution_block_policy(data)
    transports = define_http_websocket_socket_block_policy(data)
    account = define_account_read_only_connection_policy(data)
    market_data = define_market_data_read_only_connection_policy(data)
    orders = define_order_blocking_connection_policy(data)
    positions = define_position_mutation_block_policy(data)
    observability = define_connection_observability_plan(data)
    journal = define_connection_journal_plan(data)
    human = define_connection_human_approval_plan(data)
    stops = define_connection_stop_conditions_plan(data)
    scores = (
        safety_score,
        scope.score,
        boundary.score,
        preconditions.score,
        credential_reference.score,
        no_secret.score,
        network.score,
        transports.score,
        account.score,
        market_data.score,
        orders.score,
        positions.score,
        observability.score,
        journal.score,
        human.score,
        stops.score,
    )
    return PaperBrokerReadOnlyConnectionPlanScore(
        overall_score=_average(scores),
        safety_review_score=safety_score,
        scope_score=scope.score,
        boundary_score=boundary.score,
        precondition_score=preconditions.score,
        credential_reference_score=credential_reference.score,
        no_secret_read_score=no_secret.score,
        network_block_score=network.score,
        http_websocket_socket_block_score=transports.score,
        account_read_only_score=account.score,
        market_data_read_only_score=market_data.score,
        order_blocking_score=orders.score,
        position_mutation_block_score=positions.score,
        observability_score=observability.score,
        journal_score=journal.score,
        human_approval_score=human.score,
        stop_conditions_score=stops.score,
    )


def _policy_objects(data: PaperBrokerReadOnlyConnectionPlanInput) -> tuple[Any, ...]:
    return (
        define_read_only_connection_scope(data),
        define_connection_environment_boundaries(data),
        define_connection_preconditions(data),
        define_credentials_reference_policy(data),
        define_no_secret_read_policy(data),
        define_network_execution_block_policy(data),
        define_http_websocket_socket_block_policy(data),
        define_account_read_only_connection_policy(data),
        define_market_data_read_only_connection_policy(data),
        define_order_blocking_connection_policy(data),
        define_position_mutation_block_policy(data),
        define_connection_observability_plan(data),
        define_connection_journal_plan(data),
        define_connection_human_approval_plan(data),
        define_connection_stop_conditions_plan(data),
    )


def detect_read_only_connection_plan_risks(
    data: PaperBrokerReadOnlyConnectionPlanInput | Mapping[str, Any] | None,
) -> tuple[PaperBrokerReadOnlyConnectionPlanRisk, ...]:
    data = _coerce_input(data)
    risks: list[PaperBrokerReadOnlyConnectionPlanRisk] = []
    if not validate_read_only_safety_review_approval(data):
        risks.append(PaperBrokerReadOnlyConnectionPlanRisk.READ_ONLY_SAFETY_REVIEW_NOT_APPROVED)
    for policy in _policy_objects(data):
        risks.extend(_as_tuple(_get(policy, "risks", ())))
    if not _offline_boundary(data):
        risks.append(PaperBrokerReadOnlyConnectionPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(PaperBrokerReadOnlyConnectionPlanRisk.DATA_ACCESS_VIOLATION)
    if data.paper_broker_read_only_connection_safety_gate_requested is True:
        risks.append(PaperBrokerReadOnlyConnectionPlanRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE)
    return _dedupe(risks)


def generate_read_only_connection_plan_recommendations(
    data: PaperBrokerReadOnlyConnectionPlanInput | Mapping[str, Any] | None,
) -> tuple[PaperBrokerReadOnlyConnectionPlanRecommendation, ...]:
    risks = detect_read_only_connection_plan_risks(data)
    if not risks:
        return (
            PaperBrokerReadOnlyConnectionPlanRecommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN_SUITE,
            PaperBrokerReadOnlyConnectionPlanRecommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE,
        )
    mapping = {
        PaperBrokerReadOnlyConnectionPlanRisk.READ_ONLY_SAFETY_REVIEW_NOT_APPROVED: PaperBrokerReadOnlyConnectionPlanRecommendation.APPROVE_READ_ONLY_SAFETY_REVIEW_FIRST,
        PaperBrokerReadOnlyConnectionPlanRisk.READ_ONLY_CONNECTION_SCOPE_UNCLEAR: PaperBrokerReadOnlyConnectionPlanRecommendation.CLARIFY_READ_ONLY_CONNECTION_SCOPE,
        PaperBrokerReadOnlyConnectionPlanRisk.CONNECTION_ENVIRONMENT_BOUNDARY_MISSING: PaperBrokerReadOnlyConnectionPlanRecommendation.DEFINE_CONNECTION_ENVIRONMENT_BOUNDARIES,
        PaperBrokerReadOnlyConnectionPlanRisk.CONNECTION_PRECONDITION_MISSING: PaperBrokerReadOnlyConnectionPlanRecommendation.DEFINE_CONNECTION_PRECONDITIONS,
        PaperBrokerReadOnlyConnectionPlanRisk.CREDENTIAL_REFERENCE_POLICY_MISSING: PaperBrokerReadOnlyConnectionPlanRecommendation.DEFINE_CREDENTIAL_REFERENCE_POLICY,
        PaperBrokerReadOnlyConnectionPlanRisk.SECRET_READ_POLICY_UNSAFE: PaperBrokerReadOnlyConnectionPlanRecommendation.HARDEN_NO_SECRET_READ_POLICY,
        PaperBrokerReadOnlyConnectionPlanRisk.NETWORK_EXECUTION_NOT_BLOCKED: PaperBrokerReadOnlyConnectionPlanRecommendation.BLOCK_NETWORK_EXECUTION,
        PaperBrokerReadOnlyConnectionPlanRisk.HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED: PaperBrokerReadOnlyConnectionPlanRecommendation.BLOCK_HTTP_WEBSOCKET_SOCKET,
        PaperBrokerReadOnlyConnectionPlanRisk.ACCOUNT_READ_ONLY_CONNECTION_UNSAFE: PaperBrokerReadOnlyConnectionPlanRecommendation.HARDEN_ACCOUNT_READ_ONLY_CONNECTION,
        PaperBrokerReadOnlyConnectionPlanRisk.MARKET_DATA_READ_ONLY_CONNECTION_UNSAFE: PaperBrokerReadOnlyConnectionPlanRecommendation.HARDEN_MARKET_DATA_READ_ONLY_CONNECTION,
        PaperBrokerReadOnlyConnectionPlanRisk.ORDER_BLOCKING_CONNECTION_UNSAFE: PaperBrokerReadOnlyConnectionPlanRecommendation.HARDEN_ORDER_BLOCKING_CONNECTION,
        PaperBrokerReadOnlyConnectionPlanRisk.POSITION_MUTATION_BLOCK_UNSAFE: PaperBrokerReadOnlyConnectionPlanRecommendation.HARDEN_POSITION_MUTATION_BLOCK,
        PaperBrokerReadOnlyConnectionPlanRisk.OBSERVABILITY_PLAN_MISSING: PaperBrokerReadOnlyConnectionPlanRecommendation.DEFINE_CONNECTION_OBSERVABILITY_PLAN,
        PaperBrokerReadOnlyConnectionPlanRisk.JOURNAL_PLAN_MISSING: PaperBrokerReadOnlyConnectionPlanRecommendation.DEFINE_CONNECTION_JOURNAL_PLAN,
        PaperBrokerReadOnlyConnectionPlanRisk.HUMAN_APPROVAL_PLAN_MISSING: PaperBrokerReadOnlyConnectionPlanRecommendation.REQUIRE_CONNECTION_HUMAN_APPROVAL,
        PaperBrokerReadOnlyConnectionPlanRisk.STOP_CONDITIONS_PLAN_MISSING: PaperBrokerReadOnlyConnectionPlanRecommendation.DEFINE_CONNECTION_STOP_CONDITIONS,
        PaperBrokerReadOnlyConnectionPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION: PaperBrokerReadOnlyConnectionPlanRecommendation.RESTORE_OFFLINE_BOUNDARIES,
        PaperBrokerReadOnlyConnectionPlanRisk.DATA_ACCESS_VIOLATION: PaperBrokerReadOnlyConnectionPlanRecommendation.REMOVE_DATA_ACCESS,
        PaperBrokerReadOnlyConnectionPlanRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE: PaperBrokerReadOnlyConnectionPlanRecommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE,
    }
    recommendations = [PaperBrokerReadOnlyConnectionPlanRecommendation.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE]
    recommendations.extend(mapping[risk] for risk in risks if risk in mapping)
    return _dedupe(recommendations)


def _decision_for_risks(
    risks: tuple[PaperBrokerReadOnlyConnectionPlanRisk, ...],
) -> PaperBrokerReadOnlyConnectionPlanDecision:
    if not risks:
        return PaperBrokerReadOnlyConnectionPlanDecision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN
    if PaperBrokerReadOnlyConnectionPlanRisk.READ_ONLY_SAFETY_REVIEW_NOT_APPROVED in risks:
        return PaperBrokerReadOnlyConnectionPlanDecision.REQUIRE_READ_ONLY_SAFETY_REVIEW_FIXES
    if PaperBrokerReadOnlyConnectionPlanRisk.READ_ONLY_CONNECTION_SCOPE_UNCLEAR in risks:
        return PaperBrokerReadOnlyConnectionPlanDecision.REQUIRE_SCOPE_FIXES
    if PaperBrokerReadOnlyConnectionPlanRisk.CONNECTION_PRECONDITION_MISSING in risks:
        return PaperBrokerReadOnlyConnectionPlanDecision.REQUIRE_PRECONDITION_FIXES
    if any(risk in risks for risk in (PaperBrokerReadOnlyConnectionPlanRisk.CREDENTIAL_REFERENCE_POLICY_MISSING, PaperBrokerReadOnlyConnectionPlanRisk.SECRET_READ_POLICY_UNSAFE)):
        return PaperBrokerReadOnlyConnectionPlanDecision.REQUIRE_CREDENTIAL_REFERENCE_POLICY_FIXES
    if any(risk in risks for risk in (PaperBrokerReadOnlyConnectionPlanRisk.NETWORK_EXECUTION_NOT_BLOCKED, PaperBrokerReadOnlyConnectionPlanRisk.HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED)):
        return PaperBrokerReadOnlyConnectionPlanDecision.REQUIRE_NETWORK_BLOCK_POLICY_FIXES
    if PaperBrokerReadOnlyConnectionPlanRisk.ACCOUNT_READ_ONLY_CONNECTION_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionPlanDecision.REQUIRE_ACCOUNT_READ_ONLY_FIXES
    if PaperBrokerReadOnlyConnectionPlanRisk.MARKET_DATA_READ_ONLY_CONNECTION_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionPlanDecision.REQUIRE_MARKET_DATA_READ_ONLY_FIXES
    if PaperBrokerReadOnlyConnectionPlanRisk.ORDER_BLOCKING_CONNECTION_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionPlanDecision.REQUIRE_ORDER_BLOCKING_FIXES
    if PaperBrokerReadOnlyConnectionPlanRisk.POSITION_MUTATION_BLOCK_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionPlanDecision.REQUIRE_POSITION_MUTATION_BLOCK_FIXES
    if PaperBrokerReadOnlyConnectionPlanRisk.OBSERVABILITY_PLAN_MISSING in risks:
        return PaperBrokerReadOnlyConnectionPlanDecision.REQUIRE_OBSERVABILITY_FIXES
    if PaperBrokerReadOnlyConnectionPlanRisk.JOURNAL_PLAN_MISSING in risks:
        return PaperBrokerReadOnlyConnectionPlanDecision.REQUIRE_JOURNAL_FIXES
    if PaperBrokerReadOnlyConnectionPlanRisk.HUMAN_APPROVAL_PLAN_MISSING in risks:
        return PaperBrokerReadOnlyConnectionPlanDecision.REQUIRE_HUMAN_APPROVAL_FIXES
    if any(
        risk in risks
        for risk in (
            PaperBrokerReadOnlyConnectionPlanRisk.CONNECTION_ENVIRONMENT_BOUNDARY_MISSING,
            PaperBrokerReadOnlyConnectionPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION,
            PaperBrokerReadOnlyConnectionPlanRisk.DATA_ACCESS_VIOLATION,
        )
    ):
        return PaperBrokerReadOnlyConnectionPlanDecision.REQUIRE_BOUNDARY_FIXES
    return PaperBrokerReadOnlyConnectionPlanDecision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN


def _state_for_result(
    data: PaperBrokerReadOnlyConnectionPlanInput,
    risks: tuple[PaperBrokerReadOnlyConnectionPlanRisk, ...],
    score: PaperBrokerReadOnlyConnectionPlanScore,
) -> PaperBrokerReadOnlyConnectionPlanState:
    if data.paper_broker_read_only_safety_review is None:
        return PaperBrokerReadOnlyConnectionPlanState.CONNECTION_PLAN_INPUT_INVALID
    if not risks and score.overall_score >= 85:
        return PaperBrokerReadOnlyConnectionPlanState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE
    if risks:
        return PaperBrokerReadOnlyConnectionPlanState.CONNECTION_PLAN_BLOCKED
    if score.overall_score >= 70:
        return PaperBrokerReadOnlyConnectionPlanState.CONNECTION_PLAN_COMPLETED_WITH_WARNINGS
    return PaperBrokerReadOnlyConnectionPlanState.NOT_READY


def evaluate_paper_broker_read_only_connection_plan(
    data: PaperBrokerReadOnlyConnectionPlanInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlyConnectionPlanResult:
    data = _coerce_input(data)
    score = compute_read_only_connection_plan_score(data)
    risks = detect_read_only_connection_plan_risks(data)
    recommendations = generate_read_only_connection_plan_recommendations(data)
    decision = _decision_for_risks(risks)
    state = _state_for_result(data, risks, score)
    return PaperBrokerReadOnlyConnectionPlanResult(
        state=state,
        decision=decision,
        connection_plan_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        recommendations=recommendations,
        connection_scope=define_read_only_connection_scope(data),
        environment_boundaries=define_connection_environment_boundaries(data),
        connection_preconditions=define_connection_preconditions(data),
        credentials_reference_policy=define_credentials_reference_policy(data),
        no_secret_read_policy=define_no_secret_read_policy(data),
        network_execution_block_policy=define_network_execution_block_policy(data),
        http_websocket_socket_block_policy=define_http_websocket_socket_block_policy(data),
        account_read_only_connection_policy=define_account_read_only_connection_policy(data),
        market_data_read_only_connection_policy=define_market_data_read_only_connection_policy(data),
        order_blocking_connection_policy=define_order_blocking_connection_policy(data),
        position_mutation_block_policy=define_position_mutation_block_policy(data),
        observability_plan=define_connection_observability_plan(data),
        journal_plan=define_connection_journal_plan(data),
        human_approval_plan=define_connection_human_approval_plan(data),
        stop_conditions_plan=define_connection_stop_conditions_plan(data),
        offline_only=True,
        summary=(
            "Paper broker read-only connection plan is approved for a future safety gate."
            if not risks
            else "Paper broker read-only connection plan is blocked until plan risks are fixed."
        ),
    )


def render_paper_broker_read_only_connection_plan_markdown(
    result: PaperBrokerReadOnlyConnectionPlanResult | Mapping[str, Any],
) -> str:
    if isinstance(result, Mapping):
        result = PaperBrokerReadOnlyConnectionPlanResult(**dict(result))
    risks = ", ".join(risk.value for risk in result.risks) or "none"
    recommendations = ", ".join(recommendation.value for recommendation in result.recommendations) or "none"
    sections = (
        result.connection_scope,
        result.environment_boundaries,
        result.connection_preconditions,
        result.credentials_reference_policy,
        result.no_secret_read_policy,
        result.network_execution_block_policy,
        result.http_websocket_socket_block_policy,
        result.account_read_only_connection_policy,
        result.market_data_read_only_connection_policy,
        result.order_blocking_connection_policy,
        result.position_mutation_block_policy,
        result.observability_plan,
        result.journal_plan,
        result.human_approval_plan,
        result.stop_conditions_plan,
    )
    lines = [
        "# Paper Broker Read-Only Connection Plan",
        "",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Connection plan score: {result.connection_plan_score}",
        f"- Offline only: {result.offline_only}",
        f"- Risks: {risks}",
        f"- Recommendations: {recommendations}",
        "",
        "## Enforced Non-Execution Boundaries",
        "- No broker connection execution",
        "- No API key or environment variable read",
        "- No HTTP, websocket, socket or external API",
        "- No order execution",
        "- No position mutation",
        "- No active account access",
        "- No data directory access",
        "",
        "## Plan Sections",
    ]
    lines.extend(
        f"- {section.__class__.__name__}: score={_get(section, 'score', 0)}, defined={_get(section, 'defined', False)}, risks="
        f"{', '.join(risk.value for risk in _as_tuple(_get(section, 'risks', ()))) or 'none'}"
        for section in sections
    )
    return "\n".join(lines)


__all__ = [
    "evaluate_paper_broker_read_only_connection_plan",
    "validate_read_only_safety_review_approval",
    "define_read_only_connection_scope",
    "define_connection_environment_boundaries",
    "define_connection_preconditions",
    "define_credentials_reference_policy",
    "define_no_secret_read_policy",
    "define_network_execution_block_policy",
    "define_http_websocket_socket_block_policy",
    "define_account_read_only_connection_policy",
    "define_market_data_read_only_connection_policy",
    "define_order_blocking_connection_policy",
    "define_position_mutation_block_policy",
    "define_connection_observability_plan",
    "define_connection_journal_plan",
    "define_connection_human_approval_plan",
    "define_connection_stop_conditions_plan",
    "compute_read_only_connection_plan_score",
    "detect_read_only_connection_plan_risks",
    "generate_read_only_connection_plan_recommendations",
    "render_paper_broker_read_only_connection_plan_markdown",
]
