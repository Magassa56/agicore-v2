"""Offline mock connectivity layer for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.mock_connectivity_layer_models import (
    MockConnectivityGraph,
    MockConnectivityInput,
    MockConnectivityRecommendation,
    MockConnectivityResult,
    MockConnectivityRisk,
    MockConnectivityScore,
    MockConnectivitySimulation,
    MockConnectivityState,
)


def _coerce_input(data: MockConnectivityInput | Mapping[str, Any]) -> MockConnectivityInput:
    if isinstance(data, MockConnectivityInput):
        return data
    return MockConnectivityInput(**dict(data))


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


def _clamp(value: int | float, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(round(value))))


def _average(values: Iterable[int | float | None], default: int = 0) -> int:
    usable = [float(value) for value in values if value is not None]
    if not usable:
        return default
    return _clamp(sum(usable) / len(usable))


def _weighted_average(values: Iterable[tuple[int | float | None, float]], default: int = 0) -> int:
    usable = [(float(value), weight) for value, weight in values if value is not None and weight > 0]
    if not usable:
        return default
    total_weight = sum(weight for _, weight in usable)
    return _clamp(sum(value * weight for value, weight in usable) / total_weight)


def _score(obj: Any, *names: str, default: int | None = None) -> int | None:
    for name in names:
        value = _get(obj, name)
        if isinstance(value, (int, float)):
            return _clamp(value)
    return default


def _bool_score(value: bool | None, unknown: int = 45) -> int:
    if value is True:
        return 100
    if value is False:
        return 0
    return unknown


def _dedupe(items: Iterable[Any]) -> tuple[Any, ...]:
    seen: set[Any] = set()
    result: list[Any] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return tuple(result)


def _upstream_items(data: MockConnectivityInput) -> tuple[Any, ...]:
    return (
        data.alpaca_paper_connectivity_readiness,
        data.broker_paper_sandbox,
        data.alpaca_paper_adapter,
        data.paper_broker_adapter,
        data.paper_trading_end_to_end,
        data.paper_dry_run,
        data.supervised_paper_trial,
        data.observability_verification,
        data.kill_switch_verification,
        data.rollback_verification,
    )


def _upstream_risks(data: MockConnectivityInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: MockConnectivityInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _upstream_score(data: MockConnectivityInput, *names: str) -> int | None:
    values: list[int] = []
    for item in _upstream_items(data):
        values.extend(_score(item, name) for name in names)
        breakdown = _get(item, "score_breakdown")
        values.extend(_score(breakdown, name) for name in names)
    values = [value for value in values if value is not None]
    return _average(values) if values else None


def simulate_mock_connection(data: MockConnectivityInput | Mapping[str, Any]) -> MockConnectivitySimulation:
    data = _coerce_input(data)
    score = _clamp(data.mock_connection_score) if data.mock_connection_score is not None else _average(
        (
            _bool_score(data.mock_transport_defined),
            _bool_score(data.mock_connect_successful),
            _bool_score(data.mock_handshake_valid),
            _bool_score(data.mock_connection_idempotent),
            _upstream_score(data, "connectivity_score"),
        ),
        default=45,
    )
    risks: list[MockConnectivityRisk] = []
    if (
        data.mock_transport_defined is not True
        or data.mock_connect_successful is not True
        or data.mock_handshake_valid is not True
        or score < 85
    ):
        risks.append(MockConnectivityRisk.MOCK_CONNECTION_FAILURE)
    if data.mock_connection_idempotent is not True:
        risks.append(MockConnectivityRisk.MOCK_SESSION_CORRUPTION)
    events = (
        f"mock_connection_score={score}/100",
        f"mock_transport_defined={data.mock_transport_defined}",
        f"mock_connect_successful={data.mock_connect_successful}",
        f"mock_handshake_valid={data.mock_handshake_valid}",
        f"mock_connection_idempotent={data.mock_connection_idempotent}",
    )
    return MockConnectivitySimulation("mock_connection", score, not risks and score >= 85, _dedupe(risks), events)


def simulate_mock_disconnect(data: MockConnectivityInput | Mapping[str, Any]) -> MockConnectivitySimulation:
    data = _coerce_input(data)
    score = _clamp(data.mock_disconnect_score) if data.mock_disconnect_score is not None else _average(
        (
            _bool_score(data.disconnect_event_simulated),
            _bool_score(data.disconnect_detected),
            _bool_score(data.disconnect_state_safe),
            _bool_score(data.reconnect_blocked_until_supervised),
        ),
        default=45,
    )
    risks: list[MockConnectivityRisk] = []
    if (
        data.disconnect_event_simulated is not True
        or data.disconnect_detected is not True
        or data.disconnect_state_safe is not True
        or score < 85
    ):
        risks.append(MockConnectivityRisk.MOCK_DISCONNECT_UNHANDLED)
    if data.reconnect_blocked_until_supervised is not True:
        risks.append(MockConnectivityRisk.SAFETY_BOUNDARY_BYPASS)
    events = (
        f"mock_disconnect_score={score}/100",
        f"disconnect_event_simulated={data.disconnect_event_simulated}",
        f"disconnect_detected={data.disconnect_detected}",
        f"disconnect_state_safe={data.disconnect_state_safe}",
        f"reconnect_blocked_until_supervised={data.reconnect_blocked_until_supervised}",
    )
    return MockConnectivitySimulation("mock_disconnect", score, not risks and score >= 85, _dedupe(risks), events)


def simulate_mock_timeout(data: MockConnectivityInput | Mapping[str, Any]) -> MockConnectivitySimulation:
    data = _coerce_input(data)
    score = _clamp(data.mock_timeout_score) if data.mock_timeout_score is not None else _average(
        (
            _bool_score(data.timeout_event_simulated),
            _bool_score(data.timeout_detected),
            _bool_score(data.timeout_fail_closed),
            _bool_score(data.timeout_observed),
        ),
        default=45,
    )
    risks: list[MockConnectivityRisk] = []
    if (
        data.timeout_event_simulated is not True
        or data.timeout_detected is not True
        or data.timeout_observed is not True
        or score < 85
    ):
        risks.append(MockConnectivityRisk.MOCK_TIMEOUT_UNHANDLED)
    if data.timeout_fail_closed is not True:
        risks.append(MockConnectivityRisk.SAFETY_BOUNDARY_BYPASS)
    events = (
        f"mock_timeout_score={score}/100",
        f"timeout_event_simulated={data.timeout_event_simulated}",
        f"timeout_detected={data.timeout_detected}",
        f"timeout_fail_closed={data.timeout_fail_closed}",
        f"timeout_observed={data.timeout_observed}",
    )
    return MockConnectivitySimulation("mock_timeout", score, not risks and score >= 85, _dedupe(risks), events)


def simulate_mock_retry(data: MockConnectivityInput | Mapping[str, Any]) -> MockConnectivitySimulation:
    data = _coerce_input(data)
    score = _clamp(data.mock_retry_score) if data.mock_retry_score is not None else _average(
        (
            _bool_score(data.retry_event_simulated),
            _bool_score(data.retry_policy_applied),
            _bool_score(data.retry_backoff_respected),
            _bool_score(data.retry_stop_condition_respected),
        ),
        default=45,
    )
    risks: list[MockConnectivityRisk] = []
    if (
        data.retry_event_simulated is not True
        or data.retry_policy_applied is not True
        or data.retry_backoff_respected is not True
        or data.retry_stop_condition_respected is not True
        or score < 85
    ):
        risks.append(MockConnectivityRisk.MOCK_RETRY_POLICY_FAILURE)
    events = (
        f"mock_retry_score={score}/100",
        f"retry_event_simulated={data.retry_event_simulated}",
        f"retry_policy_applied={data.retry_policy_applied}",
        f"retry_backoff_respected={data.retry_backoff_respected}",
        f"retry_stop_condition_respected={data.retry_stop_condition_respected}",
    )
    return MockConnectivitySimulation("mock_retry", score, not risks and score >= 85, tuple(risks), events)


def simulate_mock_rate_limit(data: MockConnectivityInput | Mapping[str, Any]) -> MockConnectivitySimulation:
    data = _coerce_input(data)
    score = _clamp(data.mock_rate_limit_score) if data.mock_rate_limit_score is not None else _average(
        (
            _bool_score(data.rate_limit_event_simulated),
            _bool_score(data.rate_limit_detected),
            _bool_score(data.throttle_applied),
            _bool_score(data.rate_limit_metric_recorded),
        ),
        default=45,
    )
    risks: list[MockConnectivityRisk] = []
    if (
        data.rate_limit_event_simulated is not True
        or data.rate_limit_detected is not True
        or data.throttle_applied is not True
        or score < 85
    ):
        risks.append(MockConnectivityRisk.MOCK_RATE_LIMIT_UNHANDLED)
    if data.rate_limit_metric_recorded is not True:
        risks.append(MockConnectivityRisk.OBSERVABILITY_GAP)
    events = (
        f"mock_rate_limit_score={score}/100",
        f"rate_limit_event_simulated={data.rate_limit_event_simulated}",
        f"rate_limit_detected={data.rate_limit_detected}",
        f"throttle_applied={data.throttle_applied}",
        f"rate_limit_metric_recorded={data.rate_limit_metric_recorded}",
    )
    return MockConnectivitySimulation("mock_rate_limit", score, not risks and score >= 85, _dedupe(risks), events)


def simulate_mock_broker_response(data: MockConnectivityInput | Mapping[str, Any]) -> MockConnectivitySimulation:
    data = _coerce_input(data)
    score = _clamp(data.mock_broker_response_score) if data.mock_broker_response_score is not None else _average(
        (
            _bool_score(data.mock_response_generated),
            _bool_score(data.mock_response_schema_valid),
            _bool_score(data.mock_response_traceable),
            _bool_score(data.mock_response_deterministic),
        ),
        default=45,
    )
    risks: list[MockConnectivityRisk] = []
    if (
        data.mock_response_generated is not True
        or data.mock_response_schema_valid is not True
        or data.mock_response_traceable is not True
        or score < 85
    ):
        risks.append(MockConnectivityRisk.MOCK_RESPONSE_INVALID)
    if data.mock_response_deterministic is not True:
        risks.append(MockConnectivityRisk.MOCK_SESSION_CORRUPTION)
    events = (
        f"mock_broker_response_score={score}/100",
        f"mock_response_generated={data.mock_response_generated}",
        f"mock_response_schema_valid={data.mock_response_schema_valid}",
        f"mock_response_traceable={data.mock_response_traceable}",
        f"mock_response_deterministic={data.mock_response_deterministic}",
    )
    return MockConnectivitySimulation("mock_broker_response", score, not risks and score >= 85, _dedupe(risks), events)


def simulate_mock_order_rejection(data: MockConnectivityInput | Mapping[str, Any]) -> MockConnectivitySimulation:
    data = _coerce_input(data)
    score = _clamp(data.mock_order_rejection_score) if data.mock_order_rejection_score is not None else _average(
        (
            _bool_score(data.mock_order_rejection_simulated),
            _bool_score(data.mock_order_rejection_handled),
            _bool_score(data.rejection_reason_recorded),
            _bool_score(data.no_order_routed),
        ),
        default=45,
    )
    risks: list[MockConnectivityRisk] = []
    if (
        data.mock_order_rejection_simulated is not True
        or data.mock_order_rejection_handled is not True
        or data.rejection_reason_recorded is not True
        or score < 85
    ):
        risks.append(MockConnectivityRisk.MOCK_ORDER_REJECTION_UNHANDLED)
    if data.no_order_routed is not True:
        risks.append(MockConnectivityRisk.SAFETY_BOUNDARY_BYPASS)
    events = (
        f"mock_order_rejection_score={score}/100",
        f"mock_order_rejection_simulated={data.mock_order_rejection_simulated}",
        f"mock_order_rejection_handled={data.mock_order_rejection_handled}",
        f"rejection_reason_recorded={data.rejection_reason_recorded}",
        f"no_order_routed={data.no_order_routed}",
    )
    return MockConnectivitySimulation("mock_order_rejection", score, not risks and score >= 85, _dedupe(risks), events)


def verify_mock_session_integrity(data: MockConnectivityInput | Mapping[str, Any]) -> MockConnectivitySimulation:
    data = _coerce_input(data)
    score = _clamp(data.mock_session_integrity_score) if data.mock_session_integrity_score is not None else _average(
        (
            _bool_score(data.session_state_isolated),
            _bool_score(data.session_checkpointed),
            _bool_score(data.session_recovery_verified),
            _bool_score(data.session_integrity_locked),
            _bool_score(data.observability_events_emitted),
            _bool_score(data.metrics_recorded),
            _bool_score(data.traces_recorded),
            _bool_score(data.critical_alerts_recorded),
            _bool_score(data.safety_gate_enforced),
            _bool_score(data.kill_switch_linked),
            _bool_score(data.rollback_linked),
            _upstream_score(data, "observability_score", "kill_switch_score", "rollback_score"),
        ),
        default=45,
    )
    risks: list[MockConnectivityRisk] = []
    if (
        data.session_state_isolated is not True
        or data.session_checkpointed is not True
        or data.session_recovery_verified is not True
        or data.session_integrity_locked is not True
        or score < 85
    ):
        risks.append(MockConnectivityRisk.MOCK_SESSION_CORRUPTION)
    if (
        data.observability_events_emitted is not True
        or data.metrics_recorded is not True
        or data.traces_recorded is not True
        or data.critical_alerts_recorded is not True
        or _has_upstream_risk(data, "OBSERVABILITY")
    ):
        risks.append(MockConnectivityRisk.OBSERVABILITY_GAP)
    if (
        data.safety_gate_enforced is not True
        or data.kill_switch_linked is not True
        or data.rollback_linked is not True
        or _has_upstream_risk(data, "KILL_SWITCH", "ROLLBACK", "SAFETY")
    ):
        risks.append(MockConnectivityRisk.SAFETY_BOUNDARY_BYPASS)
    events = (
        f"mock_session_integrity_score={score}/100",
        f"session_state_isolated={data.session_state_isolated}",
        f"session_checkpointed={data.session_checkpointed}",
        f"session_recovery_verified={data.session_recovery_verified}",
        f"session_integrity_locked={data.session_integrity_locked}",
        f"observability_events_emitted={data.observability_events_emitted}",
        f"safety_gate_enforced={data.safety_gate_enforced}",
        f"kill_switch_linked={data.kill_switch_linked}",
        f"rollback_linked={data.rollback_linked}",
    )
    return MockConnectivitySimulation("mock_session_integrity", score, not risks and score >= 85, _dedupe(risks), events)


def detect_mock_connectivity_risks(
    data: MockConnectivityInput | Mapping[str, Any],
    mock_connection: MockConnectivitySimulation | None = None,
    mock_disconnect: MockConnectivitySimulation | None = None,
    mock_timeout: MockConnectivitySimulation | None = None,
    mock_retry: MockConnectivitySimulation | None = None,
    mock_rate_limit: MockConnectivitySimulation | None = None,
    mock_broker_response: MockConnectivitySimulation | None = None,
    mock_order_rejection: MockConnectivitySimulation | None = None,
    mock_session_integrity: MockConnectivitySimulation | None = None,
) -> tuple[MockConnectivityRisk, ...]:
    data = _coerce_input(data)
    simulations = (
        mock_connection or simulate_mock_connection(data),
        mock_disconnect or simulate_mock_disconnect(data),
        mock_timeout or simulate_mock_timeout(data),
        mock_retry or simulate_mock_retry(data),
        mock_rate_limit or simulate_mock_rate_limit(data),
        mock_broker_response or simulate_mock_broker_response(data),
        mock_order_rejection or simulate_mock_order_rejection(data),
        mock_session_integrity or verify_mock_session_integrity(data),
    )
    risks: list[MockConnectivityRisk] = []
    for simulation in simulations:
        risks.extend(simulation.risks)
    if (
        data.offline_mode_enforced is not True
        or data.no_http_transport is not True
        or data.no_websocket_transport is not True
        or data.no_socket_transport is not True
        or data.no_external_sdk_import is not True
        or _has_upstream_risk(data, "BROKER", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK", "EXTERNAL_DEPENDENCY")
    ):
        risks.append(MockConnectivityRisk.SAFETY_BOUNDARY_BYPASS)
    return _dedupe(risks)


def compute_mock_connectivity_score(
    data: MockConnectivityInput | Mapping[str, Any],
    risks: tuple[MockConnectivityRisk, ...] = (),
    mock_connection: MockConnectivitySimulation | None = None,
    mock_disconnect: MockConnectivitySimulation | None = None,
    mock_timeout: MockConnectivitySimulation | None = None,
    mock_retry: MockConnectivitySimulation | None = None,
    mock_rate_limit: MockConnectivitySimulation | None = None,
    mock_broker_response: MockConnectivitySimulation | None = None,
    mock_order_rejection: MockConnectivitySimulation | None = None,
    mock_session_integrity: MockConnectivitySimulation | None = None,
) -> MockConnectivityScore:
    data = _coerce_input(data)
    connection = mock_connection or simulate_mock_connection(data)
    disconnect = mock_disconnect or simulate_mock_disconnect(data)
    timeout = mock_timeout or simulate_mock_timeout(data)
    retry = mock_retry or simulate_mock_retry(data)
    rate_limit = mock_rate_limit or simulate_mock_rate_limit(data)
    response = mock_broker_response or simulate_mock_broker_response(data)
    rejection = mock_order_rejection or simulate_mock_order_rejection(data)
    integrity = mock_session_integrity or verify_mock_session_integrity(data)
    weighted = _weighted_average(
        (
            (connection.score, 1.2),
            (disconnect.score, 1.0),
            (timeout.score, 1.0),
            (retry.score, 0.95),
            (rate_limit.score, 0.95),
            (response.score, 1.05),
            (rejection.score, 1.05),
            (integrity.score, 1.25),
        )
    )
    penalty = min(75, len(set(risks)) * 6)
    overall = _clamp(weighted - penalty)
    critical_caps = {
        MockConnectivityRisk.MOCK_CONNECTION_FAILURE: 45,
        MockConnectivityRisk.MOCK_RESPONSE_INVALID: 50,
        MockConnectivityRisk.MOCK_SESSION_CORRUPTION: 45,
        MockConnectivityRisk.SAFETY_BOUNDARY_BYPASS: 40,
    }
    for risk, cap in critical_caps.items():
        if risk in risks:
            overall = min(overall, cap)
    return MockConnectivityScore(
        overall_score=overall,
        mock_connection_score=connection.score,
        mock_disconnect_score=disconnect.score,
        mock_timeout_score=timeout.score,
        mock_retry_score=retry.score,
        mock_rate_limit_score=rate_limit.score,
        mock_broker_response_score=response.score,
        mock_order_rejection_score=rejection.score,
        mock_session_integrity_score=integrity.score,
    )


def _build_graph(risks: tuple[MockConnectivityRisk, ...]) -> MockConnectivityGraph:
    nodes = ("connection", "disconnect", "timeout", "retry", "rate_limit", "broker_response", "order_rejection", "session", "mock_alpaca_session")
    edges = (
        ("connection", "broker_response", "opens"),
        ("disconnect", "session", "recovers"),
        ("timeout", "retry", "triggers"),
        ("retry", "broker_response", "replays"),
        ("rate_limit", "retry", "throttles"),
        ("broker_response", "session", "updates"),
        ("order_rejection", "session", "records"),
        ("session", "mock_alpaca_session", "authorizes"),
    )
    blocked: list[tuple[str, str]] = []
    mapping = {
        MockConnectivityRisk.MOCK_CONNECTION_FAILURE: ("connection", "broker_response"),
        MockConnectivityRisk.MOCK_DISCONNECT_UNHANDLED: ("disconnect", "session"),
        MockConnectivityRisk.MOCK_TIMEOUT_UNHANDLED: ("timeout", "retry"),
        MockConnectivityRisk.MOCK_RETRY_POLICY_FAILURE: ("retry", "broker_response"),
        MockConnectivityRisk.MOCK_RATE_LIMIT_UNHANDLED: ("rate_limit", "retry"),
        MockConnectivityRisk.MOCK_RESPONSE_INVALID: ("broker_response", "session"),
        MockConnectivityRisk.MOCK_ORDER_REJECTION_UNHANDLED: ("order_rejection", "session"),
        MockConnectivityRisk.MOCK_SESSION_CORRUPTION: ("session", "mock_alpaca_session"),
        MockConnectivityRisk.OBSERVABILITY_GAP: ("session", "mock_alpaca_session"),
        MockConnectivityRisk.SAFETY_BOUNDARY_BYPASS: ("session", "mock_alpaca_session"),
    }
    for risk, edge in mapping.items():
        if risk in risks:
            blocked.append(edge)
    return MockConnectivityGraph(nodes, edges, tuple((a, b) for a, b, _ in edges), _dedupe(blocked))


def _select_state(score: int, risks: tuple[MockConnectivityRisk, ...], validated: bool | None, ready_for_session: bool | None) -> MockConnectivityState:
    hard = {
        MockConnectivityRisk.MOCK_CONNECTION_FAILURE,
        MockConnectivityRisk.MOCK_RESPONSE_INVALID,
        MockConnectivityRisk.MOCK_SESSION_CORRUPTION,
        MockConnectivityRisk.SAFETY_BOUNDARY_BYPASS,
    }
    count = len(set(risks))
    if hard.intersection(risks) or score < 45 or count >= 6:
        return MockConnectivityState.NOT_READY
    if count >= 3 or score < 72:
        return MockConnectivityState.REVIEW_REQUIRED
    if count:
        return MockConnectivityState.PARTIALLY_READY
    if validated is True and ready_for_session is True and score >= 94:
        return MockConnectivityState.READY_FOR_MOCK_ALPACA_SESSION
    if validated is True and score >= 90:
        return MockConnectivityState.MOCK_CONNECTIVITY_VALIDATED
    if score >= 85:
        return MockConnectivityState.MOCK_CONNECTIVITY_READY
    return MockConnectivityState.PARTIALLY_READY


def generate_mock_connectivity_recommendations(
    risks: tuple[MockConnectivityRisk, ...],
    state: MockConnectivityState | None = None,
) -> tuple[MockConnectivityRecommendation, ...]:
    recommendations: list[MockConnectivityRecommendation] = []
    if risks:
        recommendations.append(MockConnectivityRecommendation.HOLD_MOCK_ALPACA_SESSION_APPROVAL)
    mapping = {
        MockConnectivityRisk.MOCK_CONNECTION_FAILURE: MockConnectivityRecommendation.REPAIR_MOCK_CONNECTION,
        MockConnectivityRisk.MOCK_DISCONNECT_UNHANDLED: MockConnectivityRecommendation.HANDLE_MOCK_DISCONNECT,
        MockConnectivityRisk.MOCK_TIMEOUT_UNHANDLED: MockConnectivityRecommendation.HANDLE_MOCK_TIMEOUT,
        MockConnectivityRisk.MOCK_RETRY_POLICY_FAILURE: MockConnectivityRecommendation.REPAIR_MOCK_RETRY_POLICY,
        MockConnectivityRisk.MOCK_RATE_LIMIT_UNHANDLED: MockConnectivityRecommendation.HANDLE_MOCK_RATE_LIMIT,
        MockConnectivityRisk.MOCK_RESPONSE_INVALID: MockConnectivityRecommendation.VALIDATE_MOCK_RESPONSE,
        MockConnectivityRisk.MOCK_ORDER_REJECTION_UNHANDLED: MockConnectivityRecommendation.HANDLE_MOCK_ORDER_REJECTION,
        MockConnectivityRisk.MOCK_SESSION_CORRUPTION: MockConnectivityRecommendation.REPAIR_MOCK_SESSION_INTEGRITY,
        MockConnectivityRisk.OBSERVABILITY_GAP: MockConnectivityRecommendation.RESTORE_MOCK_OBSERVABILITY,
        MockConnectivityRisk.SAFETY_BOUNDARY_BYPASS: MockConnectivityRecommendation.ENFORCE_MOCK_SAFETY_BOUNDARY,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(MockConnectivityRecommendation.RUN_MOCK_CONNECTIVITY_SUITE)
    if state == MockConnectivityState.READY_FOR_MOCK_ALPACA_SESSION:
        recommendations.append(MockConnectivityRecommendation.APPROVE_MOCK_ALPACA_SESSION_AFTER_MANUAL_REVIEW)
    return _dedupe(recommendations)


def evaluate_mock_connectivity_layer(data: MockConnectivityInput | Mapping[str, Any]) -> MockConnectivityResult:
    data = _coerce_input(data)
    connection = simulate_mock_connection(data)
    disconnect = simulate_mock_disconnect(data)
    timeout = simulate_mock_timeout(data)
    retry = simulate_mock_retry(data)
    rate_limit = simulate_mock_rate_limit(data)
    response = simulate_mock_broker_response(data)
    rejection = simulate_mock_order_rejection(data)
    integrity = verify_mock_session_integrity(data)
    risks = detect_mock_connectivity_risks(data, connection, disconnect, timeout, retry, rate_limit, response, rejection, integrity)
    score = compute_mock_connectivity_score(data, risks, connection, disconnect, timeout, retry, rate_limit, response, rejection, integrity)
    state = _select_state(score.overall_score, risks, data.mock_layer_validated, data.ready_for_mock_alpaca_session)
    graph = _build_graph(risks)
    recommendations = generate_mock_connectivity_recommendations(risks, state)
    offline_only = (
        data.offline_mode_enforced is True
        and data.no_http_transport is True
        and data.no_websocket_transport is True
        and data.no_socket_transport is True
        and data.no_external_sdk_import is True
        and data.no_order_routed is True
        and not _has_upstream_risk(data, "BROKER", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK", "EXTERNAL_DEPENDENCY")
    )
    summary = f"{state.value}: score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return MockConnectivityResult(
        state=state,
        mock_connectivity_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        mock_connection=connection,
        mock_disconnect=disconnect,
        mock_timeout=timeout,
        mock_retry=retry,
        mock_rate_limit=rate_limit,
        mock_broker_response=response,
        mock_order_rejection=rejection,
        mock_session_integrity=integrity,
        mock_connectivity_graph=graph,
        recommendations=recommendations,
        offline_only=offline_only,
        summary=summary,
    )


def render_mock_connectivity_markdown(result: MockConnectivityResult) -> str:
    lines = [
        "# AGIcore Mock Connectivity Layer",
        f"- State: {result.state.value}",
        f"- Score: {result.mock_connectivity_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Score Breakdown",
        f"- Connection: {result.score_breakdown.mock_connection_score}/100",
        f"- Disconnect: {result.score_breakdown.mock_disconnect_score}/100",
        f"- Timeout: {result.score_breakdown.mock_timeout_score}/100",
        f"- Retry: {result.score_breakdown.mock_retry_score}/100",
        f"- Rate limit: {result.score_breakdown.mock_rate_limit_score}/100",
        f"- Broker response: {result.score_breakdown.mock_broker_response_score}/100",
        f"- Order rejection: {result.score_breakdown.mock_order_rejection_score}/100",
        f"- Session integrity: {result.score_breakdown.mock_session_integrity_score}/100",
        "",
        "# Mock Simulations",
    ]
    simulations = (
        result.mock_connection,
        result.mock_disconnect,
        result.mock_timeout,
        result.mock_retry,
        result.mock_rate_limit,
        result.mock_broker_response,
        result.mock_order_rejection,
        result.mock_session_integrity,
    )
    for simulation in simulations:
        lines.append(
            f"- {simulation.name}: passed={simulation.passed}, score={simulation.score}/100, "
            f"risks={', '.join(risk.value for risk in simulation.risks) or 'none'}"
        )
        lines.extend(f"  - {event}" for event in simulation.events)
    lines.append("")
    lines.append("# Mock Connectivity Graph")
    lines.append(f"- Nodes: {', '.join(result.mock_connectivity_graph.nodes)}")
    lines.extend(f"- Edge: {source} -> {target} ({label})" for source, target, label in result.mock_connectivity_graph.edges)
    lines.append(
        "- Blocked edges: "
        + (", ".join(f"{source}->{target}" for source, target in result.mock_connectivity_graph.blocked_edges) or "none")
    )
    lines.append("")
    lines.append("# Mock Connectivity Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Mock Connectivity Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_mock_connectivity_score",
    "detect_mock_connectivity_risks",
    "evaluate_mock_connectivity_layer",
    "generate_mock_connectivity_recommendations",
    "render_mock_connectivity_markdown",
    "simulate_mock_broker_response",
    "simulate_mock_connection",
    "simulate_mock_disconnect",
    "simulate_mock_order_rejection",
    "simulate_mock_rate_limit",
    "simulate_mock_retry",
    "simulate_mock_timeout",
    "verify_mock_session_integrity",
]
