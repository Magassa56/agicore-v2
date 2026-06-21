"""Offline safety gate for AGIcore Paper Broker read-only connection planning."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_broker_read_only_connection_safety_gate_models import (
    AccountReadOnlyConnectionSafetyFinding,
    ConnectionBoundarySafetyFinding,
    ConnectionScopeSafetyFinding,
    CredentialsReferenceSafetyFinding,
    HumanApprovalConnectionSafetyFinding,
    MarketDataReadOnlyConnectionSafetyFinding,
    NetworkBlockSafetyFinding,
    OrderBlockingConnectionSafetyFinding,
    PaperBrokerReadOnlyConnectionSafetyGateDecision,
    PaperBrokerReadOnlyConnectionSafetyGateInput,
    PaperBrokerReadOnlyConnectionSafetyGateRecommendation,
    PaperBrokerReadOnlyConnectionSafetyGateResult,
    PaperBrokerReadOnlyConnectionSafetyGateRisk,
    PaperBrokerReadOnlyConnectionSafetyGateScore,
    PaperBrokerReadOnlyConnectionSafetyGateState,
    PositionMutationBlockSafetyFinding,
    StopConditionConnectionSafetyFinding,
)


def _coerce_input(
    data: PaperBrokerReadOnlyConnectionSafetyGateInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlyConnectionSafetyGateInput:
    if data is None:
        return PaperBrokerReadOnlyConnectionSafetyGateInput()
    if isinstance(data, PaperBrokerReadOnlyConnectionSafetyGateInput):
        return data
    allowed = {field.name for field in fields(PaperBrokerReadOnlyConnectionSafetyGateInput)}
    payload = {key: value for key, value in dict(data).items() if key in allowed}
    return PaperBrokerReadOnlyConnectionSafetyGateInput(**payload)


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


def _plan(data: PaperBrokerReadOnlyConnectionSafetyGateInput) -> Any:
    return data.paper_broker_read_only_connection_plan


def _section(data: PaperBrokerReadOnlyConnectionSafetyGateInput, name: str) -> Any:
    return _get(_plan(data), name)


def _policy_ok(section: Any) -> bool:
    if section is None:
        return False
    return _get(section, "defined", True) is True and not _as_tuple(_get(section, "risks", ()))


def _upstream_items(data: PaperBrokerReadOnlyConnectionSafetyGateInput) -> tuple[Any, ...]:
    return (
        data.paper_broker_read_only_connection_plan,
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


def _upstream_risks(data: PaperBrokerReadOnlyConnectionSafetyGateInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperBrokerReadOnlyConnectionSafetyGateInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _offline_boundary(data: PaperBrokerReadOnlyConnectionSafetyGateInput) -> bool:
    return (
        data.offline_mode_enforced is True
        and data.sandbox_mode_enforced is True
        and data.safety_gate_only is True
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


def _data_boundary(data: PaperBrokerReadOnlyConnectionSafetyGateInput) -> bool:
    return (
        data.data_access_requested is not True
        and not _has_upstream_risk(data, "DATA_ACCESS", "DATA_ACCESS_VIOLATION", "REAL_DATA")
    )


def validate_read_only_connection_plan_approval(
    data: PaperBrokerReadOnlyConnectionSafetyGateInput | Mapping[str, Any] | None,
) -> bool:
    data = _coerce_input(data)
    plan = _plan(data)
    if plan is None or data.read_only_connection_plan_approved is False:
        return False
    approved_state = _state_contains(
        plan,
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN",
    )
    approved = data.read_only_connection_plan_approved is True or approved_state
    return (
        approved
        and not _as_tuple(_get(plan, "risks", ()))
        and _get(plan, "offline_only", True) is True
        and not _has_upstream_risk(data, "CONNECTION_PLAN_BLOCKED", "REAL_EXECUTION", "DATA_ACCESS")
    )


def verify_connection_scope_safety(
    data: PaperBrokerReadOnlyConnectionSafetyGateInput | Mapping[str, Any] | None,
) -> ConnectionScopeSafetyFinding:
    data = _coerce_input(data)
    scope = _section(data, "connection_scope")
    prohibited = _as_tuple(_get(scope, "prohibited_actions", ()))
    prohibited_confirmed = _contains(prohibited, "CONNECT", "SECRET", "SOCKET", "ORDER", "POSITION")
    passed = (
        data.connection_scope_safety_verified is not False
        and _policy_ok(scope)
        and _get(scope, "plan_only") is True
        and prohibited_confirmed
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionSafetyGateRisk.CONNECTION_SCOPE_UNSAFE,)
    score = _metric_score(data.scope_score, _get(scope, "score"), passed)
    return ConnectionScopeSafetyFinding(score, passed, True, prohibited_confirmed, risks, ("plan_only_scope",))


def verify_connection_environment_boundary_safety(
    data: PaperBrokerReadOnlyConnectionSafetyGateInput | Mapping[str, Any] | None,
) -> ConnectionBoundarySafetyFinding:
    data = _coerce_input(data)
    boundary = _section(data, "environment_boundaries")
    offline = _get(boundary, "offline_only") is True and data.offline_mode_enforced is True
    sandbox = _get(boundary, "sandbox_only") is True and data.sandbox_mode_enforced is True
    connection_disabled = (
        _get(boundary, "connection_execution_disabled") is True
        and data.broker_connection_disabled is True
        and data.broker_connection_requested is not True
    )
    network_disabled = (
        _get(boundary, "network_transport_disabled") is True
        and data.no_http_transport is True
        and data.no_websocket_transport is True
        and data.no_socket_transport is True
        and data.network_transport_requested is not True
    )
    passed = (
        data.connection_environment_boundary_safety_verified is not False
        and _policy_ok(boundary)
        and offline
        and sandbox
        and connection_disabled
        and network_disabled
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionSafetyGateRisk.CONNECTION_ENVIRONMENT_BOUNDARY_UNSAFE,)
    score = _metric_score(data.boundary_score, _get(boundary, "score"), passed)
    return ConnectionBoundarySafetyFinding(
        score,
        passed,
        offline,
        sandbox,
        connection_disabled,
        network_disabled,
        risks,
        ("offline_sandbox_no_connection",),
    )


def verify_connection_precondition_safety(
    data: PaperBrokerReadOnlyConnectionSafetyGateInput | Mapping[str, Any] | None,
) -> ConnectionScopeSafetyFinding:
    data = _coerce_input(data)
    preconditions = _section(data, "connection_preconditions")
    passed = (
        data.connection_precondition_safety_verified is not False
        and _policy_ok(preconditions)
        and _get(preconditions, "safety_review_required") is True
        and _get(preconditions, "human_approval_required") is True
        and _get(preconditions, "stop_conditions_required") is True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionSafetyGateRisk.CONNECTION_PRECONDITION_UNSAFE,)
    score = _metric_score(data.precondition_score, _get(preconditions, "score"), passed)
    return ConnectionScopeSafetyFinding(score, passed, True, passed, risks, ("safety_review_human_stop_required",))


def verify_credentials_reference_safety(
    data: PaperBrokerReadOnlyConnectionSafetyGateInput | Mapping[str, Any] | None,
) -> CredentialsReferenceSafetyFinding:
    data = _coerce_input(data)
    policy = _section(data, "credentials_reference_policy")
    reference_only = _get(policy, "reference_only") is True
    no_secret_material = _get(policy, "no_secret_material") is True and data.hardcoded_secret_detected is not True
    no_api_key_read = _get(policy, "no_api_key_read") is True and data.api_key_read_requested is not True
    no_env_var_read = _get(policy, "no_env_var_read") is True and data.env_var_read_requested is not True
    passed = (
        data.credentials_reference_safety_verified is not False
        and _policy_ok(policy)
        and reference_only
        and no_secret_material
        and no_api_key_read
        and no_env_var_read
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionSafetyGateRisk.CREDENTIAL_REFERENCE_UNSAFE,)
    score = _metric_score(data.credential_reference_score, _get(policy, "score"), passed)
    return CredentialsReferenceSafetyFinding(
        score,
        passed,
        reference_only,
        no_secret_material,
        no_api_key_read,
        no_env_var_read,
        risks,
        ("credential_references_without_values",),
    )


def verify_no_secret_read_safety(
    data: PaperBrokerReadOnlyConnectionSafetyGateInput | Mapping[str, Any] | None,
) -> CredentialsReferenceSafetyFinding:
    data = _coerce_input(data)
    policy = _section(data, "no_secret_read_policy")
    no_secret_material = _get(policy, "no_secret_material") is True and data.hardcoded_secret_detected is not True
    no_api_key_read = _get(policy, "no_api_key_read") is True and data.api_key_read_requested is not True
    no_env_var_read = _get(policy, "no_env_var_read") is True and data.env_var_read_requested is not True
    passed = (
        data.no_secret_read_safety_verified is not False
        and _policy_ok(policy)
        and no_secret_material
        and no_api_key_read
        and no_env_var_read
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionSafetyGateRisk.SECRET_READ_POLICY_UNSAFE,)
    score = _metric_score(data.no_secret_read_score, _get(policy, "score"), passed)
    return CredentialsReferenceSafetyFinding(
        score,
        passed,
        True,
        no_secret_material,
        no_api_key_read,
        no_env_var_read,
        risks,
        ("secret_read_paths_blocked",),
    )


def verify_network_execution_block_safety(
    data: PaperBrokerReadOnlyConnectionSafetyGateInput | Mapping[str, Any] | None,
) -> NetworkBlockSafetyFinding:
    data = _coerce_input(data)
    policy = _section(data, "network_execution_block_policy")
    passed = (
        data.network_execution_block_safety_verified is not False
        and _policy_ok(policy)
        and _get(policy, "network_execution_blocked") is True
        and data.broker_connection_requested is not True
        and data.network_transport_requested is not True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionSafetyGateRisk.NETWORK_EXECUTION_NOT_BLOCKED,)
    score = _metric_score(data.network_block_score, _get(policy, "score"), passed)
    return NetworkBlockSafetyFinding(
        score,
        passed,
        _get(policy, "network_execution_blocked") is True,
        _get(policy, "http_blocked") is True,
        _get(policy, "websocket_blocked") is True,
        _get(policy, "socket_blocked") is True,
        _get(policy, "external_api_blocked") is True,
        risks,
        ("network_execution_blocked",),
    )


def verify_http_websocket_socket_block_safety(
    data: PaperBrokerReadOnlyConnectionSafetyGateInput | Mapping[str, Any] | None,
) -> NetworkBlockSafetyFinding:
    data = _coerce_input(data)
    policy = _section(data, "http_websocket_socket_block_policy")
    http = _get(policy, "http_blocked") is True and data.no_http_transport is True
    websocket = _get(policy, "websocket_blocked") is True and data.no_websocket_transport is True
    socket = _get(policy, "socket_blocked") is True and data.no_socket_transport is True
    external = _get(policy, "external_api_blocked") is True and data.no_external_api is True
    passed = (
        data.http_websocket_socket_block_safety_verified is not False
        and _policy_ok(policy)
        and http
        and websocket
        and socket
        and external
        and data.network_transport_requested is not True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionSafetyGateRisk.HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED,)
    score = _metric_score(data.http_websocket_socket_block_score, _get(policy, "score"), passed)
    return NetworkBlockSafetyFinding(score, passed, passed, http, websocket, socket, external, risks, ("transport_blocks",))


def verify_account_read_only_connection_safety(
    data: PaperBrokerReadOnlyConnectionSafetyGateInput | Mapping[str, Any] | None,
) -> AccountReadOnlyConnectionSafetyFinding:
    data = _coerce_input(data)
    policy = _section(data, "account_read_only_connection_policy")
    active_blocked = _get(policy, "active_account_access_blocked") is True and data.account_access_requested is not True
    mutations_blocked = _get(policy, "account_mutations_blocked") is True and data.no_real_account_access is True
    passed = (
        data.account_read_only_connection_safety_verified is not False
        and _policy_ok(policy)
        and active_blocked
        and mutations_blocked
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionSafetyGateRisk.ACCOUNT_READ_ONLY_CONNECTION_UNSAFE,)
    score = _metric_score(data.account_read_only_score, _get(policy, "score"), passed)
    return AccountReadOnlyConnectionSafetyFinding(
        score,
        passed,
        active_blocked,
        mutations_blocked,
        risks,
        ("account_read_only_connection",),
    )


def verify_market_data_read_only_connection_safety(
    data: PaperBrokerReadOnlyConnectionSafetyGateInput | Mapping[str, Any] | None,
) -> MarketDataReadOnlyConnectionSafetyFinding:
    data = _coerce_input(data)
    policy = _section(data, "market_data_read_only_connection_policy")
    read_only = _get(policy, "read_only_market_data_plan") is True
    live_blocked = _get(policy, "live_subscription_blocked") is True
    network_blocked = _get(policy, "network_request_blocked") is True and data.network_transport_requested is not True
    passed = (
        data.market_data_read_only_connection_safety_verified is not False
        and _policy_ok(policy)
        and read_only
        and live_blocked
        and network_blocked
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionSafetyGateRisk.MARKET_DATA_READ_ONLY_CONNECTION_UNSAFE,)
    score = _metric_score(data.market_data_read_only_score, _get(policy, "score"), passed)
    return MarketDataReadOnlyConnectionSafetyFinding(
        score,
        passed,
        read_only,
        live_blocked,
        network_blocked,
        risks,
        ("market_data_read_only_no_live_subscription",),
    )


def verify_order_blocking_connection_safety(
    data: PaperBrokerReadOnlyConnectionSafetyGateInput | Mapping[str, Any] | None,
) -> OrderBlockingConnectionSafetyFinding:
    data = _coerce_input(data)
    policy = _section(data, "order_blocking_connection_policy")
    order_blocked = _get(policy, "order_execution_blocked") is True and data.order_execution_requested is not True
    real_order_blocked = _get(policy, "real_order_blocked") is True and data.no_real_order is True
    cancel_replace_blocked = _get(policy, "cancel_replace_blocked") is True
    passed = (
        data.order_blocking_connection_safety_verified is not False
        and _policy_ok(policy)
        and order_blocked
        and real_order_blocked
        and cancel_replace_blocked
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionSafetyGateRisk.ORDER_BLOCKING_CONNECTION_UNSAFE,)
    score = _metric_score(data.order_blocking_score, _get(policy, "score"), passed)
    return OrderBlockingConnectionSafetyFinding(
        score,
        passed,
        order_blocked,
        real_order_blocked,
        cancel_replace_blocked,
        risks,
        ("orders_cancel_replace_blocked",),
    )


def verify_position_mutation_block_safety(
    data: PaperBrokerReadOnlyConnectionSafetyGateInput | Mapping[str, Any] | None,
) -> PositionMutationBlockSafetyFinding:
    data = _coerce_input(data)
    policy = _section(data, "position_mutation_block_policy")
    position_blocked = _get(policy, "cancel_replace_blocked") is True and data.no_position_mutation is True
    request_absent = data.position_mutation_requested is not True
    passed = (
        data.position_mutation_block_safety_verified is not False
        and _policy_ok(policy)
        and position_blocked
        and request_absent
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionSafetyGateRisk.POSITION_MUTATION_BLOCK_UNSAFE,)
    score = _metric_score(data.position_mutation_block_score, _get(policy, "score"), passed)
    return PositionMutationBlockSafetyFinding(
        score,
        passed,
        position_blocked,
        request_absent,
        risks,
        ("position_mutation_blocked",),
    )


def verify_observability_connection_safety(
    data: PaperBrokerReadOnlyConnectionSafetyGateInput | Mapping[str, Any] | None,
) -> ConnectionScopeSafetyFinding:
    data = _coerce_input(data)
    plan = _section(data, "observability_plan")
    passed = (
        data.observability_connection_safety_verified is not False
        and _policy_ok(plan)
        and _get(plan, "offline_events_planned") is True
        and _get(plan, "connection_attempt_logging_disabled") is True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionSafetyGateRisk.OBSERVABILITY_CONNECTION_INCOMPLETE,)
    score = _metric_score(data.observability_score, _get(plan, "score"), passed)
    return ConnectionScopeSafetyFinding(score, passed, True, passed, risks, ("offline_observability_only",))


def verify_journal_connection_safety(
    data: PaperBrokerReadOnlyConnectionSafetyGateInput | Mapping[str, Any] | None,
) -> ConnectionScopeSafetyFinding:
    data = _coerce_input(data)
    plan = _section(data, "journal_plan")
    passed = (
        data.journal_connection_safety_verified is not False
        and _policy_ok(plan)
        and _get(plan, "offline_journal_required") is True
        and _get(plan, "sensitive_values_redacted") is True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionSafetyGateRisk.JOURNAL_CONNECTION_INCOMPLETE,)
    score = _metric_score(data.journal_score, _get(plan, "score"), passed)
    return ConnectionScopeSafetyFinding(score, passed, True, passed, risks, ("redacted_offline_journal",))


def verify_human_approval_connection_safety(
    data: PaperBrokerReadOnlyConnectionSafetyGateInput | Mapping[str, Any] | None,
) -> HumanApprovalConnectionSafetyFinding:
    data = _coerce_input(data)
    plan = _section(data, "human_approval_plan")
    required = _get(plan, "human_approval_required") is True
    before = _get(plan, "approval_before_safety_gate") is True
    passed = data.human_approval_connection_safety_verified is not False and _policy_ok(plan) and required and before
    risks = () if passed else (PaperBrokerReadOnlyConnectionSafetyGateRisk.HUMAN_APPROVAL_CONNECTION_MISSING,)
    score = _metric_score(data.human_approval_score, _get(plan, "score"), passed)
    return HumanApprovalConnectionSafetyFinding(score, passed, required, before, risks, ("human_approval_before_preparation",))


def verify_stop_conditions_connection_safety(
    data: PaperBrokerReadOnlyConnectionSafetyGateInput | Mapping[str, Any] | None,
) -> StopConditionConnectionSafetyFinding:
    data = _coerce_input(data)
    plan = _section(data, "stop_conditions_plan")
    stop_secret = _get(plan, "stop_on_secret_read") is True
    stop_network = _get(plan, "stop_on_network_request") is True
    stop_order_position = _get(plan, "stop_on_order_or_position_request") is True
    passed = (
        data.stop_conditions_connection_safety_verified is not False
        and _policy_ok(plan)
        and stop_secret
        and stop_network
        and stop_order_position
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionSafetyGateRisk.STOP_CONDITIONS_CONNECTION_MISSING,)
    score = _metric_score(data.stop_conditions_score, _get(plan, "score"), passed)
    return StopConditionConnectionSafetyFinding(
        score,
        passed,
        stop_secret,
        stop_network,
        stop_order_position,
        risks,
        ("stop_on_secret_network_order_position",),
    )


def compute_read_only_connection_safety_gate_score(
    data: PaperBrokerReadOnlyConnectionSafetyGateInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlyConnectionSafetyGateScore:
    data = _coerce_input(data)
    plan_ok = validate_read_only_connection_plan_approval(data)
    plan_score = _metric_score(data.connection_plan_score, _get(_plan(data), "connection_plan_score"), plan_ok)
    scope = verify_connection_scope_safety(data)
    boundary = verify_connection_environment_boundary_safety(data)
    precondition = verify_connection_precondition_safety(data)
    credential = verify_credentials_reference_safety(data)
    secret = verify_no_secret_read_safety(data)
    network = verify_network_execution_block_safety(data)
    transports = verify_http_websocket_socket_block_safety(data)
    account = verify_account_read_only_connection_safety(data)
    market = verify_market_data_read_only_connection_safety(data)
    orders = verify_order_blocking_connection_safety(data)
    positions = verify_position_mutation_block_safety(data)
    observability = verify_observability_connection_safety(data)
    journal = verify_journal_connection_safety(data)
    human = verify_human_approval_connection_safety(data)
    stops = verify_stop_conditions_connection_safety(data)
    scores = (
        plan_score,
        scope.score,
        boundary.score,
        precondition.score,
        credential.score,
        secret.score,
        network.score,
        transports.score,
        account.score,
        market.score,
        orders.score,
        positions.score,
        observability.score,
        journal.score,
        human.score,
        stops.score,
    )
    return PaperBrokerReadOnlyConnectionSafetyGateScore(
        overall_score=_average(scores),
        connection_plan_score=plan_score,
        scope_score=scope.score,
        boundary_score=boundary.score,
        precondition_score=precondition.score,
        credential_reference_score=credential.score,
        no_secret_read_score=secret.score,
        network_block_score=network.score,
        http_websocket_socket_block_score=transports.score,
        account_read_only_score=account.score,
        market_data_read_only_score=market.score,
        order_blocking_score=orders.score,
        position_mutation_block_score=positions.score,
        observability_score=observability.score,
        journal_score=journal.score,
        human_approval_score=human.score,
        stop_conditions_score=stops.score,
    )


def _finding_objects(data: PaperBrokerReadOnlyConnectionSafetyGateInput) -> tuple[Any, ...]:
    return (
        verify_connection_scope_safety(data),
        verify_connection_environment_boundary_safety(data),
        verify_connection_precondition_safety(data),
        verify_credentials_reference_safety(data),
        verify_no_secret_read_safety(data),
        verify_network_execution_block_safety(data),
        verify_http_websocket_socket_block_safety(data),
        verify_account_read_only_connection_safety(data),
        verify_market_data_read_only_connection_safety(data),
        verify_order_blocking_connection_safety(data),
        verify_position_mutation_block_safety(data),
        verify_observability_connection_safety(data),
        verify_journal_connection_safety(data),
        verify_human_approval_connection_safety(data),
        verify_stop_conditions_connection_safety(data),
    )


def detect_read_only_connection_safety_gate_risks(
    data: PaperBrokerReadOnlyConnectionSafetyGateInput | Mapping[str, Any] | None,
) -> tuple[PaperBrokerReadOnlyConnectionSafetyGateRisk, ...]:
    data = _coerce_input(data)
    risks: list[PaperBrokerReadOnlyConnectionSafetyGateRisk] = []
    if not validate_read_only_connection_plan_approval(data):
        risks.append(PaperBrokerReadOnlyConnectionSafetyGateRisk.READ_ONLY_CONNECTION_PLAN_NOT_APPROVED)
    for finding in _finding_objects(data):
        risks.extend(_as_tuple(_get(finding, "risks", ())))
    if not _offline_boundary(data):
        risks.append(PaperBrokerReadOnlyConnectionSafetyGateRisk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(PaperBrokerReadOnlyConnectionSafetyGateRisk.DATA_ACCESS_VIOLATION)
    if data.paper_broker_read_only_connection_preparation_requested is True:
        risks.append(PaperBrokerReadOnlyConnectionSafetyGateRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION)
    return _dedupe(risks)


def generate_read_only_connection_safety_gate_recommendations(
    data: PaperBrokerReadOnlyConnectionSafetyGateInput | Mapping[str, Any] | None,
) -> tuple[PaperBrokerReadOnlyConnectionSafetyGateRecommendation, ...]:
    risks = detect_read_only_connection_safety_gate_risks(data)
    if not risks:
        return (
            PaperBrokerReadOnlyConnectionSafetyGateRecommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE_SUITE,
            PaperBrokerReadOnlyConnectionSafetyGateRecommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION,
        )
    mapping = {
        PaperBrokerReadOnlyConnectionSafetyGateRisk.READ_ONLY_CONNECTION_PLAN_NOT_APPROVED: PaperBrokerReadOnlyConnectionSafetyGateRecommendation.APPROVE_CONNECTION_PLAN_FIRST,
        PaperBrokerReadOnlyConnectionSafetyGateRisk.CONNECTION_SCOPE_UNSAFE: PaperBrokerReadOnlyConnectionSafetyGateRecommendation.HARDEN_CONNECTION_SCOPE,
        PaperBrokerReadOnlyConnectionSafetyGateRisk.CONNECTION_ENVIRONMENT_BOUNDARY_UNSAFE: PaperBrokerReadOnlyConnectionSafetyGateRecommendation.HARDEN_CONNECTION_BOUNDARIES,
        PaperBrokerReadOnlyConnectionSafetyGateRisk.CONNECTION_PRECONDITION_UNSAFE: PaperBrokerReadOnlyConnectionSafetyGateRecommendation.HARDEN_CONNECTION_PRECONDITIONS,
        PaperBrokerReadOnlyConnectionSafetyGateRisk.CREDENTIAL_REFERENCE_UNSAFE: PaperBrokerReadOnlyConnectionSafetyGateRecommendation.HARDEN_CREDENTIAL_REFERENCE,
        PaperBrokerReadOnlyConnectionSafetyGateRisk.SECRET_READ_POLICY_UNSAFE: PaperBrokerReadOnlyConnectionSafetyGateRecommendation.HARDEN_SECRET_READ_BLOCK,
        PaperBrokerReadOnlyConnectionSafetyGateRisk.NETWORK_EXECUTION_NOT_BLOCKED: PaperBrokerReadOnlyConnectionSafetyGateRecommendation.BLOCK_NETWORK_EXECUTION,
        PaperBrokerReadOnlyConnectionSafetyGateRisk.HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED: PaperBrokerReadOnlyConnectionSafetyGateRecommendation.BLOCK_HTTP_WEBSOCKET_SOCKET,
        PaperBrokerReadOnlyConnectionSafetyGateRisk.ACCOUNT_READ_ONLY_CONNECTION_UNSAFE: PaperBrokerReadOnlyConnectionSafetyGateRecommendation.HARDEN_ACCOUNT_READ_ONLY_CONNECTION,
        PaperBrokerReadOnlyConnectionSafetyGateRisk.MARKET_DATA_READ_ONLY_CONNECTION_UNSAFE: PaperBrokerReadOnlyConnectionSafetyGateRecommendation.HARDEN_MARKET_DATA_READ_ONLY_CONNECTION,
        PaperBrokerReadOnlyConnectionSafetyGateRisk.ORDER_BLOCKING_CONNECTION_UNSAFE: PaperBrokerReadOnlyConnectionSafetyGateRecommendation.HARDEN_ORDER_BLOCKING_CONNECTION,
        PaperBrokerReadOnlyConnectionSafetyGateRisk.POSITION_MUTATION_BLOCK_UNSAFE: PaperBrokerReadOnlyConnectionSafetyGateRecommendation.HARDEN_POSITION_MUTATION_BLOCK,
        PaperBrokerReadOnlyConnectionSafetyGateRisk.OBSERVABILITY_CONNECTION_INCOMPLETE: PaperBrokerReadOnlyConnectionSafetyGateRecommendation.COMPLETE_CONNECTION_OBSERVABILITY,
        PaperBrokerReadOnlyConnectionSafetyGateRisk.JOURNAL_CONNECTION_INCOMPLETE: PaperBrokerReadOnlyConnectionSafetyGateRecommendation.COMPLETE_CONNECTION_JOURNAL,
        PaperBrokerReadOnlyConnectionSafetyGateRisk.HUMAN_APPROVAL_CONNECTION_MISSING: PaperBrokerReadOnlyConnectionSafetyGateRecommendation.REQUIRE_CONNECTION_HUMAN_APPROVAL,
        PaperBrokerReadOnlyConnectionSafetyGateRisk.STOP_CONDITIONS_CONNECTION_MISSING: PaperBrokerReadOnlyConnectionSafetyGateRecommendation.DEFINE_CONNECTION_STOP_CONDITIONS,
        PaperBrokerReadOnlyConnectionSafetyGateRisk.REAL_EXECUTION_BOUNDARY_VIOLATION: PaperBrokerReadOnlyConnectionSafetyGateRecommendation.RESTORE_OFFLINE_BOUNDARIES,
        PaperBrokerReadOnlyConnectionSafetyGateRisk.DATA_ACCESS_VIOLATION: PaperBrokerReadOnlyConnectionSafetyGateRecommendation.REMOVE_DATA_ACCESS,
        PaperBrokerReadOnlyConnectionSafetyGateRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION: PaperBrokerReadOnlyConnectionSafetyGateRecommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION,
    }
    recommendations = [PaperBrokerReadOnlyConnectionSafetyGateRecommendation.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION]
    recommendations.extend(mapping[risk] for risk in risks if risk in mapping)
    return _dedupe(recommendations)


def _decision_for_risks(
    risks: tuple[PaperBrokerReadOnlyConnectionSafetyGateRisk, ...],
) -> PaperBrokerReadOnlyConnectionSafetyGateDecision:
    if not risks:
        return PaperBrokerReadOnlyConnectionSafetyGateDecision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE
    if PaperBrokerReadOnlyConnectionSafetyGateRisk.READ_ONLY_CONNECTION_PLAN_NOT_APPROVED in risks:
        return PaperBrokerReadOnlyConnectionSafetyGateDecision.REQUIRE_CONNECTION_PLAN_FIXES
    if PaperBrokerReadOnlyConnectionSafetyGateRisk.CONNECTION_SCOPE_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionSafetyGateDecision.REQUIRE_SCOPE_SAFETY_FIXES
    if PaperBrokerReadOnlyConnectionSafetyGateRisk.CONNECTION_PRECONDITION_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionSafetyGateDecision.REQUIRE_PRECONDITION_SAFETY_FIXES
    if PaperBrokerReadOnlyConnectionSafetyGateRisk.CREDENTIAL_REFERENCE_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionSafetyGateDecision.REQUIRE_CREDENTIAL_REFERENCE_FIXES
    if PaperBrokerReadOnlyConnectionSafetyGateRisk.SECRET_READ_POLICY_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionSafetyGateDecision.REQUIRE_SECRET_READ_BLOCK_FIXES
    if any(
        risk in risks
        for risk in (
            PaperBrokerReadOnlyConnectionSafetyGateRisk.NETWORK_EXECUTION_NOT_BLOCKED,
            PaperBrokerReadOnlyConnectionSafetyGateRisk.HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED,
        )
    ):
        return PaperBrokerReadOnlyConnectionSafetyGateDecision.REQUIRE_NETWORK_BLOCK_FIXES
    if PaperBrokerReadOnlyConnectionSafetyGateRisk.ACCOUNT_READ_ONLY_CONNECTION_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionSafetyGateDecision.REQUIRE_ACCOUNT_READ_ONLY_FIXES
    if PaperBrokerReadOnlyConnectionSafetyGateRisk.MARKET_DATA_READ_ONLY_CONNECTION_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionSafetyGateDecision.REQUIRE_MARKET_DATA_READ_ONLY_FIXES
    if PaperBrokerReadOnlyConnectionSafetyGateRisk.ORDER_BLOCKING_CONNECTION_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionSafetyGateDecision.REQUIRE_ORDER_BLOCKING_FIXES
    if PaperBrokerReadOnlyConnectionSafetyGateRisk.POSITION_MUTATION_BLOCK_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionSafetyGateDecision.REQUIRE_POSITION_MUTATION_BLOCK_FIXES
    if PaperBrokerReadOnlyConnectionSafetyGateRisk.HUMAN_APPROVAL_CONNECTION_MISSING in risks:
        return PaperBrokerReadOnlyConnectionSafetyGateDecision.REQUIRE_HUMAN_APPROVAL_FIXES
    if PaperBrokerReadOnlyConnectionSafetyGateRisk.STOP_CONDITIONS_CONNECTION_MISSING in risks:
        return PaperBrokerReadOnlyConnectionSafetyGateDecision.REQUIRE_STOP_CONDITION_FIXES
    if any(
        risk in risks
        for risk in (
            PaperBrokerReadOnlyConnectionSafetyGateRisk.CONNECTION_ENVIRONMENT_BOUNDARY_UNSAFE,
            PaperBrokerReadOnlyConnectionSafetyGateRisk.REAL_EXECUTION_BOUNDARY_VIOLATION,
            PaperBrokerReadOnlyConnectionSafetyGateRisk.DATA_ACCESS_VIOLATION,
        )
    ):
        return PaperBrokerReadOnlyConnectionSafetyGateDecision.REQUIRE_BOUNDARY_SAFETY_FIXES
    return PaperBrokerReadOnlyConnectionSafetyGateDecision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE


def _state_for_result(
    data: PaperBrokerReadOnlyConnectionSafetyGateInput,
    risks: tuple[PaperBrokerReadOnlyConnectionSafetyGateRisk, ...],
    score: PaperBrokerReadOnlyConnectionSafetyGateScore,
) -> PaperBrokerReadOnlyConnectionSafetyGateState:
    if data.paper_broker_read_only_connection_plan is None:
        return PaperBrokerReadOnlyConnectionSafetyGateState.CONNECTION_SAFETY_INPUT_INVALID
    if not risks and score.overall_score >= 85:
        return PaperBrokerReadOnlyConnectionSafetyGateState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION
    if risks:
        return PaperBrokerReadOnlyConnectionSafetyGateState.CONNECTION_SAFETY_BLOCKED
    if score.overall_score >= 70:
        return PaperBrokerReadOnlyConnectionSafetyGateState.CONNECTION_SAFETY_COMPLETED_WITH_WARNINGS
    return PaperBrokerReadOnlyConnectionSafetyGateState.NOT_READY


def evaluate_paper_broker_read_only_connection_safety_gate(
    data: PaperBrokerReadOnlyConnectionSafetyGateInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlyConnectionSafetyGateResult:
    data = _coerce_input(data)
    score = compute_read_only_connection_safety_gate_score(data)
    risks = detect_read_only_connection_safety_gate_risks(data)
    recommendations = generate_read_only_connection_safety_gate_recommendations(data)
    decision = _decision_for_risks(risks)
    state = _state_for_result(data, risks, score)
    return PaperBrokerReadOnlyConnectionSafetyGateResult(
        state=state,
        decision=decision,
        safety_gate_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        recommendations=recommendations,
        scope_safety=verify_connection_scope_safety(data),
        boundary_safety=verify_connection_environment_boundary_safety(data),
        precondition_safety=verify_connection_precondition_safety(data),
        credential_reference_safety=verify_credentials_reference_safety(data),
        no_secret_read_safety=verify_no_secret_read_safety(data),
        network_block_safety=verify_network_execution_block_safety(data),
        http_websocket_socket_block_safety=verify_http_websocket_socket_block_safety(data),
        account_read_only_safety=verify_account_read_only_connection_safety(data),
        market_data_read_only_safety=verify_market_data_read_only_connection_safety(data),
        order_blocking_safety=verify_order_blocking_connection_safety(data),
        position_mutation_block_safety=verify_position_mutation_block_safety(data),
        observability_safety=verify_observability_connection_safety(data),
        journal_safety=verify_journal_connection_safety(data),
        human_approval_safety=verify_human_approval_connection_safety(data),
        stop_conditions_safety=verify_stop_conditions_connection_safety(data),
        offline_only=True,
        summary=(
            "Paper broker read-only connection safety gate is approved for preparation."
            if not risks
            else "Paper broker read-only connection safety gate is blocked until safety risks are fixed."
        ),
    )


def render_paper_broker_read_only_connection_safety_gate_markdown(
    result: PaperBrokerReadOnlyConnectionSafetyGateResult | Mapping[str, Any],
) -> str:
    if isinstance(result, Mapping):
        result = PaperBrokerReadOnlyConnectionSafetyGateResult(**dict(result))
    risks = ", ".join(risk.value for risk in result.risks) or "none"
    recommendations = ", ".join(recommendation.value for recommendation in result.recommendations) or "none"
    sections = (
        result.scope_safety,
        result.boundary_safety,
        result.precondition_safety,
        result.credential_reference_safety,
        result.no_secret_read_safety,
        result.network_block_safety,
        result.http_websocket_socket_block_safety,
        result.account_read_only_safety,
        result.market_data_read_only_safety,
        result.order_blocking_safety,
        result.position_mutation_block_safety,
        result.observability_safety,
        result.journal_safety,
        result.human_approval_safety,
        result.stop_conditions_safety,
    )
    lines = [
        "# Paper Broker Read-Only Connection Safety Gate",
        "",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Safety gate score: {result.safety_gate_score}",
        f"- Offline only: {result.offline_only}",
        f"- Risks: {risks}",
        f"- Recommendations: {recommendations}",
        "",
        "## Enforced Gate Boundaries",
        "- No broker connection",
        "- No API key or environment variable read",
        "- No hardcoded secret",
        "- No HTTP, websocket, socket or external API",
        "- No order execution",
        "- No position mutation",
        "- No active account access",
        "- No data directory access",
        "",
        "## Findings",
    ]
    lines.extend(
        f"- {section.__class__.__name__}: score={_get(section, 'score', 0)}, "
        f"passed={_get(section, 'passed', False)}, risks="
        f"{', '.join(risk.value for risk in _as_tuple(_get(section, 'risks', ()))) or 'none'}"
        for section in sections
    )
    return "\n".join(lines)


__all__ = [
    "evaluate_paper_broker_read_only_connection_safety_gate",
    "validate_read_only_connection_plan_approval",
    "verify_connection_scope_safety",
    "verify_connection_environment_boundary_safety",
    "verify_connection_precondition_safety",
    "verify_credentials_reference_safety",
    "verify_no_secret_read_safety",
    "verify_network_execution_block_safety",
    "verify_http_websocket_socket_block_safety",
    "verify_account_read_only_connection_safety",
    "verify_market_data_read_only_connection_safety",
    "verify_order_blocking_connection_safety",
    "verify_position_mutation_block_safety",
    "verify_observability_connection_safety",
    "verify_journal_connection_safety",
    "verify_human_approval_connection_safety",
    "verify_stop_conditions_connection_safety",
    "compute_read_only_connection_safety_gate_score",
    "detect_read_only_connection_safety_gate_risks",
    "generate_read_only_connection_safety_gate_recommendations",
    "render_paper_broker_read_only_connection_safety_gate_markdown",
]
