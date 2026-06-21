"""Offline safety review for AGIcore Paper Broker read-only preparation."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_broker_read_only_safety_review_models import (
    AccountReadOnlySafetyReview,
    BrokerBoundarySafetyReview,
    CredentialSafetyReview,
    MarketDataReadOnlySafetyReview,
    OrderBlockingSafetyReview,
    PaperBrokerReadOnlySafetyReviewDecision,
    PaperBrokerReadOnlySafetyReviewInput,
    PaperBrokerReadOnlySafetyReviewRecommendation,
    PaperBrokerReadOnlySafetyReviewResult,
    PaperBrokerReadOnlySafetyReviewRisk,
    PaperBrokerReadOnlySafetyReviewScore,
    PaperBrokerReadOnlySafetyReviewState,
    PositionMutationSafetyReview,
    ReadOnlySafetyFinding,
)


def _coerce_input(data: PaperBrokerReadOnlySafetyReviewInput | Mapping[str, Any] | None) -> PaperBrokerReadOnlySafetyReviewInput:
    if data is None:
        return PaperBrokerReadOnlySafetyReviewInput()
    if isinstance(data, PaperBrokerReadOnlySafetyReviewInput):
        return data
    allowed = {field.name for field in fields(PaperBrokerReadOnlySafetyReviewInput)}
    payload = {key: value for key, value in dict(data).items() if key in allowed}
    return PaperBrokerReadOnlySafetyReviewInput(**payload)


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


def _safe_flag(explicit: bool | None, fallback: Any = None, default: bool = False) -> bool:
    if explicit is not None:
        return explicit is True
    if fallback is not None:
        return fallback is True
    return default


def _metric_score(explicit: int | None, fallback: Any, passed: bool) -> int:
    if explicit is not None:
        return _clamp(explicit)
    if fallback is not None:
        return _clamp(fallback)
    return _bool_score(passed)


def _preparation(data: PaperBrokerReadOnlySafetyReviewInput) -> Any:
    return data.paper_broker_read_only_preparation


def _prep_policy(data: PaperBrokerReadOnlySafetyReviewInput, name: str) -> Any:
    return _get(_preparation(data), name)


def _policy_risks(policy: Any) -> tuple[Any, ...]:
    return _as_tuple(_get(policy, "risks", ()))


def _policy_ok(policy: Any) -> bool:
    if policy is None:
        return False
    if _get(policy, "passed") is not None:
        return _get(policy, "passed") is True and not _policy_risks(policy)
    if _get(policy, "defined") is not None:
        return _get(policy, "defined") is True and not _policy_risks(policy)
    return not _policy_risks(policy)


def _upstream_items(data: PaperBrokerReadOnlySafetyReviewInput) -> tuple[Any, ...]:
    return (
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


def _upstream_risks(data: PaperBrokerReadOnlySafetyReviewInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperBrokerReadOnlySafetyReviewInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _credential_policy(data: PaperBrokerReadOnlySafetyReviewInput) -> Any:
    return _prep_policy(data, "credentials_handling_policy")


def _boundary_policy(data: PaperBrokerReadOnlySafetyReviewInput) -> Any:
    return _prep_policy(data, "broker_environment_boundaries")


def _order_policy(data: PaperBrokerReadOnlySafetyReviewInput) -> Any:
    return _prep_policy(data, "no_order_execution_policy")


def _position_policy(data: PaperBrokerReadOnlySafetyReviewInput) -> Any:
    return _prep_policy(data, "no_position_mutation_policy")


def _account_policy(data: PaperBrokerReadOnlySafetyReviewInput) -> Any:
    return _prep_policy(data, "account_read_only_policy")


def _market_data_policy(data: PaperBrokerReadOnlySafetyReviewInput) -> Any:
    return _prep_policy(data, "market_data_read_only_policy")


def _offline_boundary(data: PaperBrokerReadOnlySafetyReviewInput) -> bool:
    boundary = _boundary_policy(data)
    credentials = _credential_policy(data)
    orders = _order_policy(data)
    positions = _position_policy(data)
    account = _account_policy(data)
    network_disabled = _safe_flag(
        data.no_http_transport,
        _get(boundary, "network_transport_disabled"),
        default=True,
    )
    return (
        _safe_flag(data.offline_mode_enforced, _get(boundary, "offline_only")) is True
        and _safe_flag(data.sandbox_mode_enforced, _get(boundary, "sandbox_only")) is True
        and _safe_flag(data.safety_review_only, True, default=False) is True
        and _safe_flag(data.broker_connection_disabled, _get(boundary, "broker_connection_disabled")) is True
        and _safe_flag(data.no_real_broker, True, default=True) is True
        and _safe_flag(data.no_alpaca_real, True, default=True) is True
        and _safe_flag(data.no_api_key_read, _get(credentials, "no_api_key_read"), default=True) is True
        and _safe_flag(data.no_env_var_read, _get(credentials, "no_env_var_read"), default=True) is True
        and network_disabled is True
        and _safe_flag(data.no_websocket_transport, _get(boundary, "network_transport_disabled"), default=True) is True
        and _safe_flag(data.no_socket_transport, _get(boundary, "network_transport_disabled"), default=True) is True
        and _safe_flag(data.no_external_api, _get(boundary, "network_transport_disabled"), default=True) is True
        and _safe_flag(data.no_external_ml, True, default=True) is True
        and _safe_flag(data.no_external_llm, True, default=True) is True
        and _safe_flag(data.no_live_execution, True, default=True) is True
        and _safe_flag(data.no_real_order, _get(orders, "real_order_blocked"), default=True) is True
        and _safe_flag(data.no_position_mutation, _get(positions, "position_mutation_blocked"), default=True) is True
        and _safe_flag(data.no_real_account_access, _get(account, "active_account_access_blocked"), default=True) is True
        and data.real_execution_requested is not True
        and data.broker_connection_requested is not True
        and data.api_key_read_requested is not True
        and data.env_var_read_requested is not True
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


def _data_boundary(data: PaperBrokerReadOnlySafetyReviewInput) -> bool:
    return (
        data.data_access_requested is not True
        and not _has_upstream_risk(data, "DATA_ACCESS", "DATA_ACCESS_VIOLATION", "REAL_DATA")
    )


def validate_read_only_preparation_approval(
    data: PaperBrokerReadOnlySafetyReviewInput | Mapping[str, Any] | None,
) -> bool:
    data = _coerce_input(data)
    preparation = _preparation(data)
    if preparation is None or data.read_only_preparation_approved is False:
        return False
    approved_state = _state_contains(
        preparation,
        "READY_FOR_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW",
        "APPROVE_PAPER_BROKER_READ_ONLY_PREPARATION",
    )
    approved = data.read_only_preparation_approved is True or approved_state
    return (
        approved
        and not _as_tuple(_get(preparation, "risks", ()))
        and _get(preparation, "offline_only", True) is True
        and not _has_upstream_risk(data, "READ_ONLY_PREPARATION_BLOCKED", "REAL_EXECUTION", "DATA_ACCESS")
    )


def review_read_only_scope(data: PaperBrokerReadOnlySafetyReviewInput | Mapping[str, Any] | None) -> ReadOnlySafetyFinding:
    data = _coerce_input(data)
    scope = _prep_policy(data, "scope")
    preparation_only = _safe_flag(None, _get(scope, "preparation_only"), default=False)
    reviewed = data.read_only_scope_reviewed is not False
    passed = reviewed and _policy_ok(scope) and preparation_only
    risks = () if passed else (PaperBrokerReadOnlySafetyReviewRisk.READ_ONLY_SCOPE_UNCLEAR,)
    score = _metric_score(data.scope_score, _get(scope, "score"), passed)
    return ReadOnlySafetyFinding("read_only_scope", score, passed, risks, ("scope_is_read_only_preparation_only",))


def review_broker_environment_boundaries(
    data: PaperBrokerReadOnlySafetyReviewInput | Mapping[str, Any] | None,
) -> BrokerBoundarySafetyReview:
    data = _coerce_input(data)
    boundary = _boundary_policy(data)
    offline_only = _safe_flag(data.offline_mode_enforced, _get(boundary, "offline_only"))
    sandbox_only = _safe_flag(data.sandbox_mode_enforced, _get(boundary, "sandbox_only"))
    broker_disabled = _safe_flag(data.broker_connection_disabled, _get(boundary, "broker_connection_disabled"))
    network_disabled = (
        _safe_flag(data.no_http_transport, _get(boundary, "network_transport_disabled"), default=True)
        and _safe_flag(data.no_websocket_transport, _get(boundary, "network_transport_disabled"), default=True)
        and _safe_flag(data.no_socket_transport, _get(boundary, "network_transport_disabled"), default=True)
        and data.network_transport_requested is not True
    )
    reviewed = data.broker_environment_boundaries_reviewed is not False
    passed = reviewed and _policy_ok(boundary) and offline_only and sandbox_only and broker_disabled and network_disabled
    risks = () if passed else (PaperBrokerReadOnlySafetyReviewRisk.BROKER_ENVIRONMENT_BOUNDARY_UNSAFE,)
    score = _metric_score(data.boundary_score, _get(boundary, "score"), passed)
    return BrokerBoundarySafetyReview(
        score=score,
        passed=passed,
        offline_only=offline_only,
        sandbox_only=sandbox_only,
        broker_connection_disabled=broker_disabled,
        network_transport_disabled=network_disabled,
        risks=risks,
        details=("no_broker_connection", "no_http_websocket_socket"),
    )


def review_read_only_permission_policy(
    data: PaperBrokerReadOnlySafetyReviewInput | Mapping[str, Any] | None,
) -> ReadOnlySafetyFinding:
    data = _coerce_input(data)
    policy = _prep_policy(data, "read_only_permission_policy")
    write_blocked = (
        data.order_execution_requested is not True
        and data.position_mutation_requested is not True
        and data.account_access_requested is not True
    )
    reviewed = data.read_only_permission_policy_reviewed is not False
    passed = reviewed and _policy_ok(policy) and write_blocked
    risks = () if passed else (PaperBrokerReadOnlySafetyReviewRisk.READ_ONLY_PERMISSION_POLICY_UNSAFE,)
    score = _metric_score(data.permission_policy_score, _get(policy, "score"), passed)
    return ReadOnlySafetyFinding("read_only_permission_policy", score, passed, risks, ("write_permissions_denied",))


def review_credentials_handling_policy(
    data: PaperBrokerReadOnlySafetyReviewInput | Mapping[str, Any] | None,
) -> CredentialSafetyReview:
    data = _coerce_input(data)
    policy = _credential_policy(data)
    no_api_key = _safe_flag(data.no_api_key_read, _get(policy, "no_api_key_read"), default=True)
    no_env = _safe_flag(data.no_env_var_read, _get(policy, "no_env_var_read"), default=True)
    no_hardcoded = _safe_flag(data.no_hardcoded_secrets, _get(policy, "no_hardcoded_secrets"), default=True)
    risks: list[PaperBrokerReadOnlySafetyReviewRisk] = []
    reviewed = data.credentials_handling_policy_reviewed is not False
    if not reviewed or not _policy_ok(policy) or data.api_key_read_requested is True or not no_api_key:
        risks.append(PaperBrokerReadOnlySafetyReviewRisk.CREDENTIAL_HANDLING_UNSAFE)
    if data.env_var_read_requested is True or not no_env:
        risks.append(PaperBrokerReadOnlySafetyReviewRisk.ENVIRONMENT_VARIABLE_READ_RISK)
    if data.hardcoded_secret_detected is True or not no_hardcoded:
        risks.append(PaperBrokerReadOnlySafetyReviewRisk.HARDCODED_SECRET_RISK)
    if _has_upstream_risk(data, "API_KEY", "SECRET", "CREDENTIAL"):
        risks.append(PaperBrokerReadOnlySafetyReviewRisk.CREDENTIAL_HANDLING_UNSAFE)
    passed = not risks
    score = _metric_score(data.credential_policy_score, _get(policy, "score"), passed)
    return CredentialSafetyReview(
        score=score,
        passed=passed,
        no_api_key_read=no_api_key and data.api_key_read_requested is not True,
        no_env_var_read=no_env and data.env_var_read_requested is not True,
        no_hardcoded_secret=no_hardcoded and data.hardcoded_secret_detected is not True,
        secret_source=_value(_get(policy, "secret_source", "none_in_this_phase")) or "none_in_this_phase",
        risks=_dedupe(risks),
        details=("no_api_key_read", "no_env_var_read", "no_hardcoded_secret"),
    )


def review_no_order_execution_policy(
    data: PaperBrokerReadOnlySafetyReviewInput | Mapping[str, Any] | None,
) -> OrderBlockingSafetyReview:
    data = _coerce_input(data)
    policy = _order_policy(data)
    order_blocked = _safe_flag(data.order_execution_blocked, _get(policy, "order_execution_blocked"))
    real_order_blocked = _safe_flag(data.no_real_order, _get(policy, "real_order_blocked"), default=True)
    request_absent = data.order_execution_requested is not True
    reviewed = data.no_order_execution_policy_reviewed is not False
    passed = reviewed and _policy_ok(policy) and order_blocked and real_order_blocked and request_absent
    risks = () if passed else (PaperBrokerReadOnlySafetyReviewRisk.ORDER_EXECUTION_NOT_BLOCKED,)
    score = _metric_score(data.order_blocking_score, _get(policy, "score"), passed)
    return OrderBlockingSafetyReview(
        score=score,
        passed=passed,
        order_execution_blocked=order_blocked,
        real_order_blocked=real_order_blocked,
        order_request_absent=request_absent,
        risks=risks,
        details=("submit_cancel_replace_order_paths_blocked",),
    )


def review_no_position_mutation_policy(
    data: PaperBrokerReadOnlySafetyReviewInput | Mapping[str, Any] | None,
) -> PositionMutationSafetyReview:
    data = _coerce_input(data)
    policy = _position_policy(data)
    mutation_blocked = _safe_flag(data.position_mutation_blocked, _get(policy, "position_mutation_blocked"))
    request_absent = data.position_mutation_requested is not True
    reviewed = data.no_position_mutation_policy_reviewed is not False
    passed = reviewed and _policy_ok(policy) and mutation_blocked and request_absent
    risks = () if passed else (PaperBrokerReadOnlySafetyReviewRisk.POSITION_MUTATION_NOT_BLOCKED,)
    score = _metric_score(data.position_mutation_score, _get(policy, "score"), passed)
    return PositionMutationSafetyReview(
        score=score,
        passed=passed,
        position_mutation_blocked=mutation_blocked,
        mutation_request_absent=request_absent,
        risks=risks,
        details=("position_create_update_close_paths_blocked",),
    )


def review_account_read_only_policy(
    data: PaperBrokerReadOnlySafetyReviewInput | Mapping[str, Any] | None,
) -> AccountReadOnlySafetyReview:
    data = _coerce_input(data)
    policy = _account_policy(data)
    active_access_blocked = _safe_flag(
        data.account_active_access_blocked,
        _get(policy, "active_account_access_blocked"),
        default=True,
    )
    mutations_blocked = _safe_flag(data.account_mutations_blocked, _get(policy, "mutations_blocked"), default=True)
    reviewed = data.account_read_only_policy_reviewed is not False
    request_absent = data.account_access_requested is not True
    passed = reviewed and _policy_ok(policy) and active_access_blocked and mutations_blocked and request_absent
    risks = () if passed else (PaperBrokerReadOnlySafetyReviewRisk.ACCOUNT_READ_ONLY_POLICY_UNSAFE,)
    score = _metric_score(data.account_read_only_score, _get(policy, "score"), passed)
    return AccountReadOnlySafetyReview(
        score=score,
        passed=passed,
        account_read_only=passed,
        active_account_access_blocked=active_access_blocked and request_absent,
        mutations_blocked=mutations_blocked,
        risks=risks,
        details=("active_account_access_blocked", "account_mutations_blocked"),
    )


def review_market_data_read_only_policy(
    data: PaperBrokerReadOnlySafetyReviewInput | Mapping[str, Any] | None,
) -> MarketDataReadOnlySafetyReview:
    data = _coerce_input(data)
    policy = _market_data_policy(data)
    live_disabled = _safe_flag(
        data.market_data_live_subscription_blocked,
        _get(policy, "live_subscription_disabled"),
        default=True,
    )
    network_absent = data.network_transport_requested is not True
    reviewed = data.market_data_read_only_policy_reviewed is not False
    passed = reviewed and _policy_ok(policy) and live_disabled and network_absent
    risks = () if passed else (PaperBrokerReadOnlySafetyReviewRisk.MARKET_DATA_READ_ONLY_POLICY_UNSAFE,)
    score = _metric_score(data.market_data_read_only_score, _get(policy, "score"), passed)
    return MarketDataReadOnlySafetyReview(
        score=score,
        passed=passed,
        market_data_read_only=passed,
        live_subscription_disabled=live_disabled,
        network_request_absent=network_absent,
        risks=risks,
        details=("future_market_data_read_only_plan_only", "no_live_subscription_test"),
    )


def review_mock_to_paper_boundary_policy(
    data: PaperBrokerReadOnlySafetyReviewInput | Mapping[str, Any] | None,
) -> ReadOnlySafetyFinding:
    data = _coerce_input(data)
    policy = _prep_policy(data, "mock_to_paper_boundary_policy")
    reviewed = data.mock_to_paper_boundary_reviewed is not False
    mock_defined = _safe_flag(None, _get(policy, "mock_boundary_defined"))
    passed = reviewed and _policy_ok(policy) and mock_defined
    risks = () if passed else (PaperBrokerReadOnlySafetyReviewRisk.MOCK_TO_PAPER_BOUNDARY_UNSAFE,)
    score = _metric_score(data.mock_to_paper_boundary_score, _get(policy, "score"), passed)
    return ReadOnlySafetyFinding("mock_to_paper_boundary", score, passed, risks, ("mock_outputs_are_review_inputs_only",))


def review_paper_vs_real_boundary_policy(
    data: PaperBrokerReadOnlySafetyReviewInput | Mapping[str, Any] | None,
) -> ReadOnlySafetyFinding:
    data = _coerce_input(data)
    policy = _prep_policy(data, "paper_vs_real_boundary_policy")
    reviewed = data.paper_vs_real_boundary_reviewed is not False
    paper_defined = _safe_flag(None, _get(policy, "paper_boundary_defined"))
    real_blocked = _safe_flag(data.no_real_broker, _get(policy, "real_boundary_blocked"), default=True)
    passed = reviewed and _policy_ok(policy) and paper_defined and real_blocked and data.real_execution_requested is not True
    risks = () if passed else (PaperBrokerReadOnlySafetyReviewRisk.PAPER_REAL_BOUNDARY_UNSAFE,)
    score = _metric_score(data.paper_vs_real_boundary_score, _get(policy, "score"), passed)
    return ReadOnlySafetyFinding("paper_vs_real_boundary", score, passed, risks, ("paper_future_read_only_only", "real_blocked"))


def review_observability_policy(
    data: PaperBrokerReadOnlySafetyReviewInput | Mapping[str, Any] | None,
) -> ReadOnlySafetyFinding:
    data = _coerce_input(data)
    policy = _prep_policy(data, "observability_preparation_policy")
    reviewed = data.observability_policy_reviewed is not False
    passed = reviewed and _policy_ok(policy)
    risks = () if passed else (PaperBrokerReadOnlySafetyReviewRisk.OBSERVABILITY_POLICY_INCOMPLETE,)
    score = _metric_score(data.observability_score, _get(policy, "score"), passed)
    return ReadOnlySafetyFinding("observability_policy", score, passed, risks, ("offline_audit_events_required",))


def review_journal_policy(data: PaperBrokerReadOnlySafetyReviewInput | Mapping[str, Any] | None) -> ReadOnlySafetyFinding:
    data = _coerce_input(data)
    policy = _prep_policy(data, "journal_preparation_policy")
    reviewed = data.journal_policy_reviewed is not False
    passed = reviewed and _policy_ok(policy)
    risks = () if passed else (PaperBrokerReadOnlySafetyReviewRisk.JOURNAL_POLICY_INCOMPLETE,)
    score = _metric_score(data.journal_score, _get(policy, "score"), passed)
    return ReadOnlySafetyFinding("journal_policy", score, passed, risks, ("safety_review_decisions_journaled_offline",))


def review_human_approval_policy(
    data: PaperBrokerReadOnlySafetyReviewInput | Mapping[str, Any] | None,
) -> ReadOnlySafetyFinding:
    data = _coerce_input(data)
    policy = _prep_policy(data, "human_approval_policy")
    reviewed = data.human_approval_policy_reviewed is not False
    passed = reviewed and _policy_ok(policy)
    risks = () if passed else (PaperBrokerReadOnlySafetyReviewRisk.HUMAN_APPROVAL_POLICY_INCOMPLETE,)
    score = _metric_score(data.human_approval_score, _get(policy, "score"), passed)
    return ReadOnlySafetyFinding("human_approval_policy", score, passed, risks, ("explicit_human_approval_required",))


def review_stop_conditions_policy(
    data: PaperBrokerReadOnlySafetyReviewInput | Mapping[str, Any] | None,
) -> ReadOnlySafetyFinding:
    data = _coerce_input(data)
    policy = _prep_policy(data, "stop_conditions_policy")
    reviewed = data.stop_conditions_policy_reviewed is not False
    passed = reviewed and _policy_ok(policy)
    risks = () if passed else (PaperBrokerReadOnlySafetyReviewRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN,)
    score = _metric_score(data.stop_conditions_score, _get(policy, "score"), passed)
    return ReadOnlySafetyFinding(
        "stop_conditions_policy",
        score,
        passed,
        risks,
        ("stop_if_connection_secret_order_position_account_or_network_requested",),
    )


def compute_read_only_safety_score(
    data: PaperBrokerReadOnlySafetyReviewInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlySafetyReviewScore:
    data = _coerce_input(data)
    preparation_approved = validate_read_only_preparation_approval(data)
    prep_score = _metric_score(
        data.preparation_approval_score,
        _get(_preparation(data), "preparation_score"),
        preparation_approved,
    )
    scope = review_read_only_scope(data)
    boundary = review_broker_environment_boundaries(data)
    permission = review_read_only_permission_policy(data)
    credentials = review_credentials_handling_policy(data)
    orders = review_no_order_execution_policy(data)
    positions = review_no_position_mutation_policy(data)
    account = review_account_read_only_policy(data)
    market = review_market_data_read_only_policy(data)
    mock_boundary = review_mock_to_paper_boundary_policy(data)
    paper_real = review_paper_vs_real_boundary_policy(data)
    observability = review_observability_policy(data)
    journal = review_journal_policy(data)
    human = review_human_approval_policy(data)
    stops = review_stop_conditions_policy(data)
    component_scores = (
        prep_score,
        scope.score,
        boundary.score,
        permission.score,
        credentials.score,
        orders.score,
        positions.score,
        account.score,
        market.score,
        mock_boundary.score,
        paper_real.score,
        observability.score,
        journal.score,
        human.score,
        stops.score,
    )
    return PaperBrokerReadOnlySafetyReviewScore(
        overall_score=_average(component_scores),
        preparation_approval_score=prep_score,
        scope_score=scope.score,
        boundary_score=boundary.score,
        permission_policy_score=permission.score,
        credential_policy_score=credentials.score,
        order_blocking_score=orders.score,
        position_mutation_score=positions.score,
        account_read_only_score=account.score,
        market_data_read_only_score=market.score,
        mock_to_paper_boundary_score=mock_boundary.score,
        paper_vs_real_boundary_score=paper_real.score,
        observability_score=observability.score,
        journal_score=journal.score,
        human_approval_score=human.score,
        stop_conditions_score=stops.score,
    )


def _review_objects(data: PaperBrokerReadOnlySafetyReviewInput) -> tuple[Any, ...]:
    return (
        review_read_only_scope(data),
        review_broker_environment_boundaries(data),
        review_read_only_permission_policy(data),
        review_credentials_handling_policy(data),
        review_no_order_execution_policy(data),
        review_no_position_mutation_policy(data),
        review_account_read_only_policy(data),
        review_market_data_read_only_policy(data),
        review_mock_to_paper_boundary_policy(data),
        review_paper_vs_real_boundary_policy(data),
        review_observability_policy(data),
        review_journal_policy(data),
        review_human_approval_policy(data),
        review_stop_conditions_policy(data),
    )


def detect_read_only_safety_risks(
    data: PaperBrokerReadOnlySafetyReviewInput | Mapping[str, Any] | None,
) -> tuple[PaperBrokerReadOnlySafetyReviewRisk, ...]:
    data = _coerce_input(data)
    risks: list[PaperBrokerReadOnlySafetyReviewRisk] = []
    if not validate_read_only_preparation_approval(data):
        risks.append(PaperBrokerReadOnlySafetyReviewRisk.READ_ONLY_PREPARATION_NOT_APPROVED)
    for review in _review_objects(data):
        risks.extend(_as_tuple(_get(review, "risks", ())))
    if not _offline_boundary(data):
        risks.append(PaperBrokerReadOnlySafetyReviewRisk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(PaperBrokerReadOnlySafetyReviewRisk.DATA_ACCESS_VIOLATION)
    if data.paper_broker_read_only_connection_plan_requested is True:
        risks.append(PaperBrokerReadOnlySafetyReviewRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN)
    return _dedupe(risks)


def generate_read_only_safety_recommendations(
    data: PaperBrokerReadOnlySafetyReviewInput | Mapping[str, Any] | None,
) -> tuple[PaperBrokerReadOnlySafetyReviewRecommendation, ...]:
    risks = detect_read_only_safety_risks(data)
    if not risks:
        return (
            PaperBrokerReadOnlySafetyReviewRecommendation.RUN_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW_SUITE,
            PaperBrokerReadOnlySafetyReviewRecommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN,
        )
    mapping = {
        PaperBrokerReadOnlySafetyReviewRisk.READ_ONLY_PREPARATION_NOT_APPROVED: PaperBrokerReadOnlySafetyReviewRecommendation.APPROVE_READ_ONLY_PREPARATION_FIRST,
        PaperBrokerReadOnlySafetyReviewRisk.READ_ONLY_SCOPE_UNCLEAR: PaperBrokerReadOnlySafetyReviewRecommendation.CLARIFY_READ_ONLY_SCOPE,
        PaperBrokerReadOnlySafetyReviewRisk.BROKER_ENVIRONMENT_BOUNDARY_UNSAFE: PaperBrokerReadOnlySafetyReviewRecommendation.HARDEN_BROKER_ENVIRONMENT_BOUNDARIES,
        PaperBrokerReadOnlySafetyReviewRisk.READ_ONLY_PERMISSION_POLICY_UNSAFE: PaperBrokerReadOnlySafetyReviewRecommendation.HARDEN_READ_ONLY_PERMISSION_POLICY,
        PaperBrokerReadOnlySafetyReviewRisk.CREDENTIAL_HANDLING_UNSAFE: PaperBrokerReadOnlySafetyReviewRecommendation.HARDEN_CREDENTIAL_HANDLING,
        PaperBrokerReadOnlySafetyReviewRisk.HARDCODED_SECRET_RISK: PaperBrokerReadOnlySafetyReviewRecommendation.REMOVE_HARDCODED_SECRET,
        PaperBrokerReadOnlySafetyReviewRisk.ENVIRONMENT_VARIABLE_READ_RISK: PaperBrokerReadOnlySafetyReviewRecommendation.BLOCK_ENVIRONMENT_VARIABLE_READ,
        PaperBrokerReadOnlySafetyReviewRisk.ORDER_EXECUTION_NOT_BLOCKED: PaperBrokerReadOnlySafetyReviewRecommendation.BLOCK_ORDER_EXECUTION,
        PaperBrokerReadOnlySafetyReviewRisk.POSITION_MUTATION_NOT_BLOCKED: PaperBrokerReadOnlySafetyReviewRecommendation.BLOCK_POSITION_MUTATION,
        PaperBrokerReadOnlySafetyReviewRisk.ACCOUNT_READ_ONLY_POLICY_UNSAFE: PaperBrokerReadOnlySafetyReviewRecommendation.HARDEN_ACCOUNT_READ_ONLY_POLICY,
        PaperBrokerReadOnlySafetyReviewRisk.MARKET_DATA_READ_ONLY_POLICY_UNSAFE: PaperBrokerReadOnlySafetyReviewRecommendation.HARDEN_MARKET_DATA_READ_ONLY_POLICY,
        PaperBrokerReadOnlySafetyReviewRisk.MOCK_TO_PAPER_BOUNDARY_UNSAFE: PaperBrokerReadOnlySafetyReviewRecommendation.CLARIFY_MOCK_TO_PAPER_BOUNDARY,
        PaperBrokerReadOnlySafetyReviewRisk.PAPER_REAL_BOUNDARY_UNSAFE: PaperBrokerReadOnlySafetyReviewRecommendation.CLARIFY_PAPER_REAL_BOUNDARY,
        PaperBrokerReadOnlySafetyReviewRisk.OBSERVABILITY_POLICY_INCOMPLETE: PaperBrokerReadOnlySafetyReviewRecommendation.COMPLETE_OBSERVABILITY_POLICY,
        PaperBrokerReadOnlySafetyReviewRisk.JOURNAL_POLICY_INCOMPLETE: PaperBrokerReadOnlySafetyReviewRecommendation.COMPLETE_JOURNAL_POLICY,
        PaperBrokerReadOnlySafetyReviewRisk.HUMAN_APPROVAL_POLICY_INCOMPLETE: PaperBrokerReadOnlySafetyReviewRecommendation.REQUIRE_HUMAN_APPROVAL,
        PaperBrokerReadOnlySafetyReviewRisk.REAL_EXECUTION_BOUNDARY_VIOLATION: PaperBrokerReadOnlySafetyReviewRecommendation.RESTORE_OFFLINE_BOUNDARIES,
        PaperBrokerReadOnlySafetyReviewRisk.DATA_ACCESS_VIOLATION: PaperBrokerReadOnlySafetyReviewRecommendation.REMOVE_DATA_ACCESS,
        PaperBrokerReadOnlySafetyReviewRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN: PaperBrokerReadOnlySafetyReviewRecommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN,
    }
    recommendations = [PaperBrokerReadOnlySafetyReviewRecommendation.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN]
    recommendations.extend(mapping[risk] for risk in risks if risk in mapping)
    return _dedupe(recommendations)


def _decision_for_risks(
    risks: tuple[PaperBrokerReadOnlySafetyReviewRisk, ...],
) -> PaperBrokerReadOnlySafetyReviewDecision:
    if not risks:
        return PaperBrokerReadOnlySafetyReviewDecision.APPROVE_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW
    if PaperBrokerReadOnlySafetyReviewRisk.READ_ONLY_PREPARATION_NOT_APPROVED in risks:
        return PaperBrokerReadOnlySafetyReviewDecision.REQUIRE_READ_ONLY_PREPARATION_FIXES
    if PaperBrokerReadOnlySafetyReviewRisk.READ_ONLY_SCOPE_UNCLEAR in risks:
        return PaperBrokerReadOnlySafetyReviewDecision.REQUIRE_SCOPE_FIXES
    if any(
        risk in risks
        for risk in (
            PaperBrokerReadOnlySafetyReviewRisk.CREDENTIAL_HANDLING_UNSAFE,
            PaperBrokerReadOnlySafetyReviewRisk.HARDCODED_SECRET_RISK,
            PaperBrokerReadOnlySafetyReviewRisk.ENVIRONMENT_VARIABLE_READ_RISK,
        )
    ):
        return PaperBrokerReadOnlySafetyReviewDecision.REQUIRE_CREDENTIAL_POLICY_FIXES
    if PaperBrokerReadOnlySafetyReviewRisk.ORDER_EXECUTION_NOT_BLOCKED in risks:
        return PaperBrokerReadOnlySafetyReviewDecision.REQUIRE_NO_ORDER_POLICY_FIXES
    if PaperBrokerReadOnlySafetyReviewRisk.POSITION_MUTATION_NOT_BLOCKED in risks:
        return PaperBrokerReadOnlySafetyReviewDecision.REQUIRE_POSITION_MUTATION_FIXES
    if PaperBrokerReadOnlySafetyReviewRisk.ACCOUNT_READ_ONLY_POLICY_UNSAFE in risks:
        return PaperBrokerReadOnlySafetyReviewDecision.REQUIRE_ACCOUNT_READ_ONLY_FIXES
    if PaperBrokerReadOnlySafetyReviewRisk.MARKET_DATA_READ_ONLY_POLICY_UNSAFE in risks:
        return PaperBrokerReadOnlySafetyReviewDecision.REQUIRE_MARKET_DATA_READ_ONLY_FIXES
    if PaperBrokerReadOnlySafetyReviewRisk.MOCK_TO_PAPER_BOUNDARY_UNSAFE in risks:
        return PaperBrokerReadOnlySafetyReviewDecision.REQUIRE_MOCK_PAPER_BOUNDARY_FIXES
    if PaperBrokerReadOnlySafetyReviewRisk.PAPER_REAL_BOUNDARY_UNSAFE in risks:
        return PaperBrokerReadOnlySafetyReviewDecision.REQUIRE_PAPER_REAL_BOUNDARY_FIXES
    if PaperBrokerReadOnlySafetyReviewRisk.READ_ONLY_PERMISSION_POLICY_UNSAFE in risks:
        return PaperBrokerReadOnlySafetyReviewDecision.REQUIRE_PERMISSION_POLICY_FIXES
    if PaperBrokerReadOnlySafetyReviewRisk.HUMAN_APPROVAL_POLICY_INCOMPLETE in risks:
        return PaperBrokerReadOnlySafetyReviewDecision.REQUIRE_HUMAN_APPROVAL_FIXES
    if any(
        risk in risks
        for risk in (
            PaperBrokerReadOnlySafetyReviewRisk.BROKER_ENVIRONMENT_BOUNDARY_UNSAFE,
            PaperBrokerReadOnlySafetyReviewRisk.REAL_EXECUTION_BOUNDARY_VIOLATION,
            PaperBrokerReadOnlySafetyReviewRisk.DATA_ACCESS_VIOLATION,
        )
    ):
        return PaperBrokerReadOnlySafetyReviewDecision.REQUIRE_BOUNDARY_FIXES
    return PaperBrokerReadOnlySafetyReviewDecision.BLOCK_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW


def _state_for_result(
    data: PaperBrokerReadOnlySafetyReviewInput,
    risks: tuple[PaperBrokerReadOnlySafetyReviewRisk, ...],
    score: PaperBrokerReadOnlySafetyReviewScore,
) -> PaperBrokerReadOnlySafetyReviewState:
    if data.paper_broker_read_only_preparation is None:
        return PaperBrokerReadOnlySafetyReviewState.SAFETY_REVIEW_INPUT_INVALID
    if not risks and score.overall_score >= 85:
        return PaperBrokerReadOnlySafetyReviewState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN
    if risks:
        return PaperBrokerReadOnlySafetyReviewState.SAFETY_REVIEW_BLOCKED
    if score.overall_score >= 70:
        return PaperBrokerReadOnlySafetyReviewState.SAFETY_REVIEW_COMPLETED_WITH_WARNINGS
    return PaperBrokerReadOnlySafetyReviewState.NOT_READY


def _finding_from_review(name: str, review: Any) -> ReadOnlySafetyFinding:
    return ReadOnlySafetyFinding(
        name=name,
        score=_get(review, "score", 0),
        passed=_get(review, "passed", False),
        risks=_as_tuple(_get(review, "risks", ())),
        details=_as_tuple(_get(review, "details", ())),
    )


def _build_findings(data: PaperBrokerReadOnlySafetyReviewInput) -> tuple[ReadOnlySafetyFinding, ...]:
    return (
        review_read_only_scope(data),
        _finding_from_review("broker_environment_boundaries", review_broker_environment_boundaries(data)),
        review_read_only_permission_policy(data),
        _finding_from_review("credentials_handling_policy", review_credentials_handling_policy(data)),
        _finding_from_review("no_order_execution_policy", review_no_order_execution_policy(data)),
        _finding_from_review("no_position_mutation_policy", review_no_position_mutation_policy(data)),
        _finding_from_review("account_read_only_policy", review_account_read_only_policy(data)),
        _finding_from_review("market_data_read_only_policy", review_market_data_read_only_policy(data)),
        review_mock_to_paper_boundary_policy(data),
        review_paper_vs_real_boundary_policy(data),
        review_observability_policy(data),
        review_journal_policy(data),
        review_human_approval_policy(data),
        review_stop_conditions_policy(data),
    )


def evaluate_paper_broker_read_only_safety_review(
    data: PaperBrokerReadOnlySafetyReviewInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlySafetyReviewResult:
    data = _coerce_input(data)
    score = compute_read_only_safety_score(data)
    risks = detect_read_only_safety_risks(data)
    recommendations = generate_read_only_safety_recommendations(data)
    decision = _decision_for_risks(risks)
    state = _state_for_result(data, risks, score)
    return PaperBrokerReadOnlySafetyReviewResult(
        state=state,
        decision=decision,
        safety_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        recommendations=recommendations,
        read_only_scope_review=review_read_only_scope(data),
        broker_environment_boundary_review=review_broker_environment_boundaries(data),
        read_only_permission_policy_review=review_read_only_permission_policy(data),
        credentials_handling_review=review_credentials_handling_policy(data),
        order_blocking_review=review_no_order_execution_policy(data),
        position_mutation_review=review_no_position_mutation_policy(data),
        account_read_only_review=review_account_read_only_policy(data),
        market_data_read_only_review=review_market_data_read_only_policy(data),
        mock_to_paper_boundary_review=review_mock_to_paper_boundary_policy(data),
        paper_vs_real_boundary_review=review_paper_vs_real_boundary_policy(data),
        observability_review=review_observability_policy(data),
        journal_review=review_journal_policy(data),
        human_approval_review=review_human_approval_policy(data),
        stop_conditions_review=review_stop_conditions_policy(data),
        findings=_build_findings(data),
        offline_only=True,
        summary=(
            "Paper broker read-only safety review is approved for a future connection plan."
            if not risks
            else "Paper broker read-only safety review is blocked until safety gaps are fixed."
        ),
    )


def render_paper_broker_read_only_safety_review_markdown(
    result: PaperBrokerReadOnlySafetyReviewResult | Mapping[str, Any],
) -> str:
    if isinstance(result, Mapping):
        result = PaperBrokerReadOnlySafetyReviewResult(**dict(result))
    risks = ", ".join(risk.value for risk in result.risks) or "none"
    recommendations = ", ".join(recommendation.value for recommendation in result.recommendations) or "none"
    findings = "\n".join(
        f"- {finding.name}: score={finding.score}, passed={finding.passed}, risks="
        f"{', '.join(risk.value for risk in finding.risks) or 'none'}"
        for finding in result.findings
    )
    return "\n".join(
        (
            "# Paper Broker Read-Only Safety Review",
            "",
            f"- State: {result.state.value}",
            f"- Decision: {result.decision.value}",
            f"- Safety score: {result.safety_score}",
            f"- Offline only: {result.offline_only}",
            f"- Risks: {risks}",
            f"- Recommendations: {recommendations}",
            "",
            "## Enforced Boundaries",
            "- No broker connection",
            "- No Alpaca real access",
            "- No API key or environment variable read",
            "- No hardcoded secret",
            "- No HTTP, websocket, socket or external API",
            "- No order execution",
            "- No position mutation",
            "- No active account access",
            "- No data directory access",
            "",
            "## Findings",
            findings,
        )
    )


__all__ = [
    "evaluate_paper_broker_read_only_safety_review",
    "validate_read_only_preparation_approval",
    "review_read_only_scope",
    "review_broker_environment_boundaries",
    "review_read_only_permission_policy",
    "review_credentials_handling_policy",
    "review_no_order_execution_policy",
    "review_no_position_mutation_policy",
    "review_account_read_only_policy",
    "review_market_data_read_only_policy",
    "review_mock_to_paper_boundary_policy",
    "review_paper_vs_real_boundary_policy",
    "review_observability_policy",
    "review_journal_policy",
    "review_human_approval_policy",
    "review_stop_conditions_policy",
    "compute_read_only_safety_score",
    "detect_read_only_safety_risks",
    "generate_read_only_safety_recommendations",
    "render_paper_broker_read_only_safety_review_markdown",
]
