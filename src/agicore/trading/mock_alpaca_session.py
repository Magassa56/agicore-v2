"""Offline mock Alpaca paper session simulator for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.mock_alpaca_session_models import (
    MockAlpacaSessionGraph,
    MockAlpacaSessionInput,
    MockAlpacaSessionRecommendation,
    MockAlpacaSessionResult,
    MockAlpacaSessionRisk,
    MockAlpacaSessionScore,
    MockAlpacaSessionSimulation,
    MockAlpacaSessionState,
)


def _coerce_input(data: MockAlpacaSessionInput | Mapping[str, Any]) -> MockAlpacaSessionInput:
    if isinstance(data, MockAlpacaSessionInput):
        return data
    return MockAlpacaSessionInput(**dict(data))


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


def _upstream_items(data: MockAlpacaSessionInput) -> tuple[Any, ...]:
    return (
        data.mock_connectivity_layer,
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


def _upstream_risks(data: MockAlpacaSessionInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: MockAlpacaSessionInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _upstream_score(data: MockAlpacaSessionInput, *names: str) -> int | None:
    values: list[int] = []
    for item in _upstream_items(data):
        values.extend(_score(item, name) for name in names)
        breakdown = _get(item, "score_breakdown")
        values.extend(_score(breakdown, name) for name in names)
    values = [value for value in values if value is not None]
    return _average(values) if values else None


def simulate_mock_session_connect(data: MockAlpacaSessionInput | Mapping[str, Any]) -> MockAlpacaSessionSimulation:
    data = _coerce_input(data)
    score = (
        _clamp(data.mock_session_connect_score)
        if data.mock_session_connect_score is not None
        else _average(
            (
                _bool_score(data.mock_session_transport_ready),
                _bool_score(data.mock_session_connect_successful),
                _bool_score(data.mock_session_handshake_valid),
                _bool_score(data.mock_session_idempotent),
                _upstream_score(data, "mock_connectivity_score", "connectivity_score"),
            ),
            default=45,
        )
    )
    risks: list[MockAlpacaSessionRisk] = []
    if (
        data.mock_session_transport_ready is not True
        or data.mock_session_connect_successful is not True
        or data.mock_session_handshake_valid is not True
        or score < 85
    ):
        risks.append(MockAlpacaSessionRisk.MOCK_SESSION_CONNECT_FAILURE)
    if data.mock_session_idempotent is not True:
        risks.append(MockAlpacaSessionRisk.MOCK_SESSION_STATE_DRIFT)
    events = (
        f"mock_session_connect_score={score}/100",
        f"mock_session_transport_ready={data.mock_session_transport_ready}",
        f"mock_session_connect_successful={data.mock_session_connect_successful}",
        f"mock_session_handshake_valid={data.mock_session_handshake_valid}",
        f"mock_session_idempotent={data.mock_session_idempotent}",
    )
    return MockAlpacaSessionSimulation("mock_session_connect", score, not risks and score >= 85, _dedupe(risks), events)


def simulate_mock_account_fetch(data: MockAlpacaSessionInput | Mapping[str, Any]) -> MockAlpacaSessionSimulation:
    data = _coerce_input(data)
    score = (
        _clamp(data.mock_account_fetch_score)
        if data.mock_account_fetch_score is not None
        else _average(
            (
                _bool_score(data.mock_account_fetch_simulated),
                _bool_score(data.mock_account_schema_valid),
                _bool_score(data.mock_account_balances_consistent),
                _bool_score(data.mock_account_fetch_traceable),
            ),
            default=45,
        )
    )
    risks: list[MockAlpacaSessionRisk] = []
    if (
        data.mock_account_fetch_simulated is not True
        or data.mock_account_schema_valid is not True
        or score < 85
    ):
        risks.append(MockAlpacaSessionRisk.MOCK_ACCOUNT_FETCH_FAILURE)
    if data.mock_account_balances_consistent is not True:
        risks.append(MockAlpacaSessionRisk.MOCK_SESSION_STATE_DRIFT)
    if data.mock_account_fetch_traceable is not True:
        risks.append(MockAlpacaSessionRisk.MOCK_OBSERVABILITY_EVENT_MISSING)
    events = (
        f"mock_account_fetch_score={score}/100",
        f"mock_account_fetch_simulated={data.mock_account_fetch_simulated}",
        f"mock_account_schema_valid={data.mock_account_schema_valid}",
        f"mock_account_balances_consistent={data.mock_account_balances_consistent}",
        f"mock_account_fetch_traceable={data.mock_account_fetch_traceable}",
    )
    return MockAlpacaSessionSimulation("mock_account_fetch", score, not risks and score >= 85, _dedupe(risks), events)


def simulate_mock_positions_fetch(data: MockAlpacaSessionInput | Mapping[str, Any]) -> MockAlpacaSessionSimulation:
    data = _coerce_input(data)
    score = (
        _clamp(data.mock_positions_fetch_score)
        if data.mock_positions_fetch_score is not None
        else _average(
            (
                _bool_score(data.mock_positions_fetch_simulated),
                _bool_score(data.mock_positions_schema_valid),
                _bool_score(data.mock_positions_reconciled),
                _bool_score(data.mock_positions_fetch_traceable),
            ),
            default=45,
        )
    )
    risks: list[MockAlpacaSessionRisk] = []
    if (
        data.mock_positions_fetch_simulated is not True
        or data.mock_positions_schema_valid is not True
        or score < 85
    ):
        risks.append(MockAlpacaSessionRisk.MOCK_POSITIONS_FETCH_FAILURE)
    if data.mock_positions_reconciled is not True:
        risks.append(MockAlpacaSessionRisk.MOCK_SESSION_STATE_DRIFT)
    if data.mock_positions_fetch_traceable is not True:
        risks.append(MockAlpacaSessionRisk.MOCK_OBSERVABILITY_EVENT_MISSING)
    events = (
        f"mock_positions_fetch_score={score}/100",
        f"mock_positions_fetch_simulated={data.mock_positions_fetch_simulated}",
        f"mock_positions_schema_valid={data.mock_positions_schema_valid}",
        f"mock_positions_reconciled={data.mock_positions_reconciled}",
        f"mock_positions_fetch_traceable={data.mock_positions_fetch_traceable}",
    )
    return MockAlpacaSessionSimulation("mock_positions_fetch", score, not risks and score >= 85, _dedupe(risks), events)


def simulate_mock_order_submit(data: MockAlpacaSessionInput | Mapping[str, Any]) -> MockAlpacaSessionSimulation:
    data = _coerce_input(data)
    score = (
        _clamp(data.mock_order_submit_score)
        if data.mock_order_submit_score is not None
        else _average(
            (
                _bool_score(data.mock_order_submit_simulated),
                _bool_score(data.mock_order_payload_valid),
                _bool_score(data.mock_order_safety_checked),
                _bool_score(data.mock_order_not_routed),
            ),
            default=45,
        )
    )
    risks: list[MockAlpacaSessionRisk] = []
    if (
        data.mock_order_submit_simulated is not True
        or data.mock_order_payload_valid is not True
        or data.mock_order_safety_checked is not True
        or score < 85
    ):
        risks.append(MockAlpacaSessionRisk.MOCK_ORDER_SUBMIT_FAILURE)
    if data.mock_order_not_routed is not True:
        risks.append(MockAlpacaSessionRisk.SAFETY_BOUNDARY_BYPASS)
    events = (
        f"mock_order_submit_score={score}/100",
        f"mock_order_submit_simulated={data.mock_order_submit_simulated}",
        f"mock_order_payload_valid={data.mock_order_payload_valid}",
        f"mock_order_safety_checked={data.mock_order_safety_checked}",
        f"mock_order_not_routed={data.mock_order_not_routed}",
    )
    return MockAlpacaSessionSimulation("mock_order_submit", score, not risks and score >= 85, _dedupe(risks), events)


def simulate_mock_order_status(data: MockAlpacaSessionInput | Mapping[str, Any]) -> MockAlpacaSessionSimulation:
    data = _coerce_input(data)
    score = (
        _clamp(data.mock_order_status_score)
        if data.mock_order_status_score is not None
        else _average(
            (
                _bool_score(data.mock_order_status_simulated),
                _bool_score(data.mock_order_status_schema_valid),
                _bool_score(data.mock_order_status_reconciled),
                _bool_score(data.mock_order_status_traceable),
            ),
            default=45,
        )
    )
    risks: list[MockAlpacaSessionRisk] = []
    if (
        data.mock_order_status_simulated is not True
        or data.mock_order_status_schema_valid is not True
        or score < 85
    ):
        risks.append(MockAlpacaSessionRisk.MOCK_ORDER_STATUS_FAILURE)
    if data.mock_order_status_reconciled is not True:
        risks.append(MockAlpacaSessionRisk.MOCK_SESSION_STATE_DRIFT)
    if data.mock_order_status_traceable is not True:
        risks.append(MockAlpacaSessionRisk.MOCK_OBSERVABILITY_EVENT_MISSING)
    events = (
        f"mock_order_status_score={score}/100",
        f"mock_order_status_simulated={data.mock_order_status_simulated}",
        f"mock_order_status_schema_valid={data.mock_order_status_schema_valid}",
        f"mock_order_status_reconciled={data.mock_order_status_reconciled}",
        f"mock_order_status_traceable={data.mock_order_status_traceable}",
    )
    return MockAlpacaSessionSimulation("mock_order_status", score, not risks and score >= 85, _dedupe(risks), events)


def simulate_mock_journal_update(data: MockAlpacaSessionInput | Mapping[str, Any]) -> MockAlpacaSessionSimulation:
    data = _coerce_input(data)
    score = (
        _clamp(data.mock_journal_update_score)
        if data.mock_journal_update_score is not None
        else _average(
            (
                _bool_score(data.mock_journal_update_simulated),
                _bool_score(data.mock_journal_entry_complete),
                _bool_score(data.mock_journal_traceable),
                _bool_score(data.mock_journal_replayable),
            ),
            default=45,
        )
    )
    risks: list[MockAlpacaSessionRisk] = []
    if (
        data.mock_journal_update_simulated is not True
        or data.mock_journal_entry_complete is not True
        or score < 85
    ):
        risks.append(MockAlpacaSessionRisk.MOCK_JOURNAL_UPDATE_FAILURE)
    if data.mock_journal_traceable is not True:
        risks.append(MockAlpacaSessionRisk.MOCK_OBSERVABILITY_EVENT_MISSING)
    if data.mock_journal_replayable is not True:
        risks.append(MockAlpacaSessionRisk.MOCK_SESSION_STATE_DRIFT)
    events = (
        f"mock_journal_update_score={score}/100",
        f"mock_journal_update_simulated={data.mock_journal_update_simulated}",
        f"mock_journal_entry_complete={data.mock_journal_entry_complete}",
        f"mock_journal_traceable={data.mock_journal_traceable}",
        f"mock_journal_replayable={data.mock_journal_replayable}",
    )
    return MockAlpacaSessionSimulation("mock_journal_update", score, not risks and score >= 85, _dedupe(risks), events)


def simulate_mock_observability_events(data: MockAlpacaSessionInput | Mapping[str, Any]) -> MockAlpacaSessionSimulation:
    data = _coerce_input(data)
    score = (
        _clamp(data.mock_observability_events_score)
        if data.mock_observability_events_score is not None
        else _average(
            (
                _bool_score(data.mock_observability_events_simulated),
                _bool_score(data.mock_metrics_recorded),
                _bool_score(data.mock_traces_recorded),
                _bool_score(data.mock_alerts_recorded),
                _upstream_score(data, "observability_score"),
            ),
            default=45,
        )
    )
    risks: list[MockAlpacaSessionRisk] = []
    if (
        data.mock_observability_events_simulated is not True
        or data.mock_metrics_recorded is not True
        or data.mock_traces_recorded is not True
        or data.mock_alerts_recorded is not True
        or _has_upstream_risk(data, "OBSERVABILITY")
        or score < 85
    ):
        risks.append(MockAlpacaSessionRisk.MOCK_OBSERVABILITY_EVENT_MISSING)
    events = (
        f"mock_observability_events_score={score}/100",
        f"mock_observability_events_simulated={data.mock_observability_events_simulated}",
        f"mock_metrics_recorded={data.mock_metrics_recorded}",
        f"mock_traces_recorded={data.mock_traces_recorded}",
        f"mock_alerts_recorded={data.mock_alerts_recorded}",
    )
    return MockAlpacaSessionSimulation("mock_observability_events", score, not risks and score >= 85, tuple(risks), events)


def simulate_mock_session_disconnect(data: MockAlpacaSessionInput | Mapping[str, Any]) -> MockAlpacaSessionSimulation:
    data = _coerce_input(data)
    score = (
        _clamp(data.mock_session_disconnect_score)
        if data.mock_session_disconnect_score is not None
        else _average(
            (
                _bool_score(data.mock_session_disconnect_simulated),
                _bool_score(data.mock_session_disconnect_detected),
                _bool_score(data.mock_session_shutdown_safe),
                _bool_score(data.mock_session_reconnect_blocked),
            ),
            default=45,
        )
    )
    risks: list[MockAlpacaSessionRisk] = []
    if (
        data.mock_session_disconnect_simulated is not True
        or data.mock_session_disconnect_detected is not True
        or data.mock_session_shutdown_safe is not True
        or score < 85
    ):
        risks.append(MockAlpacaSessionRisk.MOCK_SESSION_DISCONNECT_FAILURE)
    if data.mock_session_reconnect_blocked is not True:
        risks.append(MockAlpacaSessionRisk.SAFETY_BOUNDARY_BYPASS)
    events = (
        f"mock_session_disconnect_score={score}/100",
        f"mock_session_disconnect_simulated={data.mock_session_disconnect_simulated}",
        f"mock_session_disconnect_detected={data.mock_session_disconnect_detected}",
        f"mock_session_shutdown_safe={data.mock_session_shutdown_safe}",
        f"mock_session_reconnect_blocked={data.mock_session_reconnect_blocked}",
    )
    return MockAlpacaSessionSimulation("mock_session_disconnect", score, not risks and score >= 85, _dedupe(risks), events)


def detect_mock_alpaca_session_risks(
    data: MockAlpacaSessionInput | Mapping[str, Any],
    mock_session_connect: MockAlpacaSessionSimulation | None = None,
    mock_account_fetch: MockAlpacaSessionSimulation | None = None,
    mock_positions_fetch: MockAlpacaSessionSimulation | None = None,
    mock_order_submit: MockAlpacaSessionSimulation | None = None,
    mock_order_status: MockAlpacaSessionSimulation | None = None,
    mock_journal_update: MockAlpacaSessionSimulation | None = None,
    mock_observability_events: MockAlpacaSessionSimulation | None = None,
    mock_session_disconnect: MockAlpacaSessionSimulation | None = None,
) -> tuple[MockAlpacaSessionRisk, ...]:
    data = _coerce_input(data)
    simulations = (
        mock_session_connect or simulate_mock_session_connect(data),
        mock_account_fetch or simulate_mock_account_fetch(data),
        mock_positions_fetch or simulate_mock_positions_fetch(data),
        mock_order_submit or simulate_mock_order_submit(data),
        mock_order_status or simulate_mock_order_status(data),
        mock_journal_update or simulate_mock_journal_update(data),
        mock_observability_events or simulate_mock_observability_events(data),
        mock_session_disconnect or simulate_mock_session_disconnect(data),
    )
    risks: list[MockAlpacaSessionRisk] = []
    for simulation in simulations:
        risks.extend(simulation.risks)
    if (
        data.mock_state_snapshot_consistent is not True
        or data.mock_state_replay_consistent is not True
        or data.mock_state_recovery_verified is not True
        or data.mock_state_isolated is not True
    ):
        risks.append(MockAlpacaSessionRisk.MOCK_SESSION_STATE_DRIFT)
    if (
        data.offline_mode_enforced is not True
        or data.no_real_broker is not True
        or data.no_api_key_read is not True
        or data.no_http_transport is not True
        or data.no_websocket_transport is not True
        or data.no_socket_transport is not True
        or data.no_external_api is not True
        or data.no_real_order is not True
        or data.safety_gate_enforced is not True
        or data.kill_switch_linked is not True
        or data.rollback_linked is not True
        or _has_upstream_risk(data, "BROKER", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK", "EXTERNAL_DEPENDENCY", "KILL_SWITCH", "ROLLBACK", "SAFETY")
    ):
        risks.append(MockAlpacaSessionRisk.SAFETY_BOUNDARY_BYPASS)
    return _dedupe(risks)


def compute_mock_alpaca_session_score(
    data: MockAlpacaSessionInput | Mapping[str, Any],
    risks: tuple[MockAlpacaSessionRisk, ...] = (),
    mock_session_connect: MockAlpacaSessionSimulation | None = None,
    mock_account_fetch: MockAlpacaSessionSimulation | None = None,
    mock_positions_fetch: MockAlpacaSessionSimulation | None = None,
    mock_order_submit: MockAlpacaSessionSimulation | None = None,
    mock_order_status: MockAlpacaSessionSimulation | None = None,
    mock_journal_update: MockAlpacaSessionSimulation | None = None,
    mock_observability_events: MockAlpacaSessionSimulation | None = None,
    mock_session_disconnect: MockAlpacaSessionSimulation | None = None,
) -> MockAlpacaSessionScore:
    data = _coerce_input(data)
    connect = mock_session_connect or simulate_mock_session_connect(data)
    account = mock_account_fetch or simulate_mock_account_fetch(data)
    positions = mock_positions_fetch or simulate_mock_positions_fetch(data)
    submit = mock_order_submit or simulate_mock_order_submit(data)
    status = mock_order_status or simulate_mock_order_status(data)
    journal = mock_journal_update or simulate_mock_journal_update(data)
    observability = mock_observability_events or simulate_mock_observability_events(data)
    disconnect = mock_session_disconnect or simulate_mock_session_disconnect(data)
    weighted = _weighted_average(
        (
            (connect.score, 1.2),
            (account.score, 1.0),
            (positions.score, 1.0),
            (submit.score, 1.25),
            (status.score, 1.05),
            (journal.score, 1.05),
            (observability.score, 1.1),
            (disconnect.score, 1.0),
        )
    )
    state_score = _average(
        (
            _bool_score(data.mock_state_snapshot_consistent),
            _bool_score(data.mock_state_replay_consistent),
            _bool_score(data.mock_state_recovery_verified),
            _bool_score(data.mock_state_isolated),
        ),
        default=45,
    )
    weighted = _weighted_average(((weighted, 1.0), (state_score, 0.35)))
    penalty = min(75, len(set(risks)) * 6)
    overall = _clamp(weighted - penalty)
    critical_caps = {
        MockAlpacaSessionRisk.MOCK_SESSION_CONNECT_FAILURE: 45,
        MockAlpacaSessionRisk.MOCK_ORDER_SUBMIT_FAILURE: 50,
        MockAlpacaSessionRisk.MOCK_SESSION_STATE_DRIFT: 45,
        MockAlpacaSessionRisk.SAFETY_BOUNDARY_BYPASS: 40,
    }
    for risk, cap in critical_caps.items():
        if risk in risks:
            overall = min(overall, cap)
    return MockAlpacaSessionScore(
        overall_score=overall,
        mock_session_connect_score=connect.score,
        mock_account_fetch_score=account.score,
        mock_positions_fetch_score=positions.score,
        mock_order_submit_score=submit.score,
        mock_order_status_score=status.score,
        mock_journal_update_score=journal.score,
        mock_observability_events_score=observability.score,
        mock_session_disconnect_score=disconnect.score,
    )


def _build_graph(risks: tuple[MockAlpacaSessionRisk, ...]) -> MockAlpacaSessionGraph:
    nodes = (
        "connect",
        "account",
        "positions",
        "order_submit",
        "order_status",
        "journal",
        "observability",
        "disconnect",
        "simulated_market_session",
    )
    edges = (
        ("connect", "account", "opens"),
        ("account", "positions", "hydrates"),
        ("positions", "order_submit", "guards"),
        ("order_submit", "order_status", "tracks"),
        ("order_status", "journal", "records"),
        ("journal", "observability", "emits"),
        ("observability", "disconnect", "closes"),
        ("disconnect", "simulated_market_session", "authorizes"),
    )
    mapping = {
        MockAlpacaSessionRisk.MOCK_SESSION_CONNECT_FAILURE: ("connect", "account"),
        MockAlpacaSessionRisk.MOCK_ACCOUNT_FETCH_FAILURE: ("account", "positions"),
        MockAlpacaSessionRisk.MOCK_POSITIONS_FETCH_FAILURE: ("positions", "order_submit"),
        MockAlpacaSessionRisk.MOCK_ORDER_SUBMIT_FAILURE: ("order_submit", "order_status"),
        MockAlpacaSessionRisk.MOCK_ORDER_STATUS_FAILURE: ("order_status", "journal"),
        MockAlpacaSessionRisk.MOCK_JOURNAL_UPDATE_FAILURE: ("journal", "observability"),
        MockAlpacaSessionRisk.MOCK_OBSERVABILITY_EVENT_MISSING: ("observability", "disconnect"),
        MockAlpacaSessionRisk.MOCK_SESSION_DISCONNECT_FAILURE: ("disconnect", "simulated_market_session"),
        MockAlpacaSessionRisk.MOCK_SESSION_STATE_DRIFT: ("disconnect", "simulated_market_session"),
        MockAlpacaSessionRisk.SAFETY_BOUNDARY_BYPASS: ("disconnect", "simulated_market_session"),
    }
    blocked = [edge for risk, edge in mapping.items() if risk in risks]
    return MockAlpacaSessionGraph(nodes, edges, tuple((source, target) for source, target, _ in edges), _dedupe(blocked))


def _select_state(
    score: int,
    risks: tuple[MockAlpacaSessionRisk, ...],
    session_completed: bool | None,
    ready_for_market: bool | None,
) -> MockAlpacaSessionState:
    hard = {
        MockAlpacaSessionRisk.MOCK_SESSION_CONNECT_FAILURE,
        MockAlpacaSessionRisk.MOCK_ORDER_SUBMIT_FAILURE,
        MockAlpacaSessionRisk.MOCK_SESSION_STATE_DRIFT,
        MockAlpacaSessionRisk.SAFETY_BOUNDARY_BYPASS,
    }
    count = len(set(risks))
    if hard.intersection(risks) or score < 45 or count >= 6:
        return MockAlpacaSessionState.NOT_READY
    if count >= 3 or score < 72:
        return MockAlpacaSessionState.REVIEW_REQUIRED
    if count:
        return MockAlpacaSessionState.PARTIALLY_READY
    if session_completed is True and ready_for_market is True and score >= 94:
        return MockAlpacaSessionState.READY_FOR_SIMULATED_MARKET_SESSION
    if session_completed is True and score >= 90:
        return MockAlpacaSessionState.MOCK_SESSION_COMPLETED
    if score >= 85:
        return MockAlpacaSessionState.MOCK_SESSION_READY
    return MockAlpacaSessionState.PARTIALLY_READY


def generate_mock_alpaca_session_recommendations(
    risks: tuple[MockAlpacaSessionRisk, ...],
    state: MockAlpacaSessionState | None = None,
) -> tuple[MockAlpacaSessionRecommendation, ...]:
    recommendations: list[MockAlpacaSessionRecommendation] = []
    if risks:
        recommendations.append(MockAlpacaSessionRecommendation.HOLD_SIMULATED_MARKET_SESSION_APPROVAL)
    mapping = {
        MockAlpacaSessionRisk.MOCK_SESSION_CONNECT_FAILURE: MockAlpacaSessionRecommendation.REPAIR_MOCK_SESSION_CONNECT,
        MockAlpacaSessionRisk.MOCK_ACCOUNT_FETCH_FAILURE: MockAlpacaSessionRecommendation.REPAIR_MOCK_ACCOUNT_FETCH,
        MockAlpacaSessionRisk.MOCK_POSITIONS_FETCH_FAILURE: MockAlpacaSessionRecommendation.REPAIR_MOCK_POSITIONS_FETCH,
        MockAlpacaSessionRisk.MOCK_ORDER_SUBMIT_FAILURE: MockAlpacaSessionRecommendation.REPAIR_MOCK_ORDER_SUBMIT,
        MockAlpacaSessionRisk.MOCK_ORDER_STATUS_FAILURE: MockAlpacaSessionRecommendation.REPAIR_MOCK_ORDER_STATUS,
        MockAlpacaSessionRisk.MOCK_JOURNAL_UPDATE_FAILURE: MockAlpacaSessionRecommendation.REPAIR_MOCK_JOURNAL_UPDATE,
        MockAlpacaSessionRisk.MOCK_OBSERVABILITY_EVENT_MISSING: MockAlpacaSessionRecommendation.RESTORE_MOCK_OBSERVABILITY_EVENTS,
        MockAlpacaSessionRisk.MOCK_SESSION_DISCONNECT_FAILURE: MockAlpacaSessionRecommendation.REPAIR_MOCK_SESSION_DISCONNECT,
        MockAlpacaSessionRisk.MOCK_SESSION_STATE_DRIFT: MockAlpacaSessionRecommendation.RECONCILE_MOCK_SESSION_STATE,
        MockAlpacaSessionRisk.SAFETY_BOUNDARY_BYPASS: MockAlpacaSessionRecommendation.ENFORCE_MOCK_SESSION_SAFETY_BOUNDARY,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(MockAlpacaSessionRecommendation.RUN_MOCK_ALPACA_SESSION_SUITE)
    if state == MockAlpacaSessionState.READY_FOR_SIMULATED_MARKET_SESSION:
        recommendations.append(MockAlpacaSessionRecommendation.APPROVE_SIMULATED_MARKET_SESSION_AFTER_MANUAL_REVIEW)
    return _dedupe(recommendations)


def evaluate_mock_alpaca_session(data: MockAlpacaSessionInput | Mapping[str, Any]) -> MockAlpacaSessionResult:
    data = _coerce_input(data)
    connect = simulate_mock_session_connect(data)
    account = simulate_mock_account_fetch(data)
    positions = simulate_mock_positions_fetch(data)
    submit = simulate_mock_order_submit(data)
    status = simulate_mock_order_status(data)
    journal = simulate_mock_journal_update(data)
    observability = simulate_mock_observability_events(data)
    disconnect = simulate_mock_session_disconnect(data)
    risks = detect_mock_alpaca_session_risks(data, connect, account, positions, submit, status, journal, observability, disconnect)
    score = compute_mock_alpaca_session_score(data, risks, connect, account, positions, submit, status, journal, observability, disconnect)
    state = _select_state(score.overall_score, risks, data.session_completed, data.ready_for_simulated_market_session)
    graph = _build_graph(risks)
    recommendations = generate_mock_alpaca_session_recommendations(risks, state)
    offline_only = (
        data.offline_mode_enforced is True
        and data.no_real_broker is True
        and data.no_api_key_read is True
        and data.no_http_transport is True
        and data.no_websocket_transport is True
        and data.no_socket_transport is True
        and data.no_external_api is True
        and data.no_real_order is True
        and data.mock_order_not_routed is True
        and not _has_upstream_risk(data, "BROKER", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK", "EXTERNAL_DEPENDENCY")
    )
    summary = f"{state.value}: score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return MockAlpacaSessionResult(
        state=state,
        mock_alpaca_session_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        mock_session_connect=connect,
        mock_account_fetch=account,
        mock_positions_fetch=positions,
        mock_order_submit=submit,
        mock_order_status=status,
        mock_journal_update=journal,
        mock_observability_events=observability,
        mock_session_disconnect=disconnect,
        mock_session_graph=graph,
        recommendations=recommendations,
        offline_only=offline_only,
        summary=summary,
    )


def render_mock_alpaca_session_markdown(result: MockAlpacaSessionResult) -> str:
    lines = [
        "# AGIcore Mock Alpaca Session",
        f"- State: {result.state.value}",
        f"- Score: {result.mock_alpaca_session_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Score Breakdown",
        f"- Session connect: {result.score_breakdown.mock_session_connect_score}/100",
        f"- Account fetch: {result.score_breakdown.mock_account_fetch_score}/100",
        f"- Positions fetch: {result.score_breakdown.mock_positions_fetch_score}/100",
        f"- Order submit: {result.score_breakdown.mock_order_submit_score}/100",
        f"- Order status: {result.score_breakdown.mock_order_status_score}/100",
        f"- Journal update: {result.score_breakdown.mock_journal_update_score}/100",
        f"- Observability events: {result.score_breakdown.mock_observability_events_score}/100",
        f"- Session disconnect: {result.score_breakdown.mock_session_disconnect_score}/100",
        "",
        "# Mock Alpaca Session Simulations",
    ]
    simulations = (
        result.mock_session_connect,
        result.mock_account_fetch,
        result.mock_positions_fetch,
        result.mock_order_submit,
        result.mock_order_status,
        result.mock_journal_update,
        result.mock_observability_events,
        result.mock_session_disconnect,
    )
    for simulation in simulations:
        lines.append(
            f"- {simulation.name}: passed={simulation.passed}, score={simulation.score}/100, "
            f"risks={', '.join(risk.value for risk in simulation.risks) or 'none'}"
        )
        lines.extend(f"  - {event}" for event in simulation.events)
    lines.append("")
    lines.append("# Mock Alpaca Session Graph")
    lines.append(f"- Nodes: {', '.join(result.mock_session_graph.nodes)}")
    lines.extend(f"- Edge: {source} -> {target} ({label})" for source, target, label in result.mock_session_graph.edges)
    lines.append(
        "- Blocked edges: "
        + (", ".join(f"{source}->{target}" for source, target in result.mock_session_graph.blocked_edges) or "none")
    )
    lines.append("")
    lines.append("# Mock Alpaca Session Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Mock Alpaca Session Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_mock_alpaca_session_score",
    "detect_mock_alpaca_session_risks",
    "evaluate_mock_alpaca_session",
    "generate_mock_alpaca_session_recommendations",
    "render_mock_alpaca_session_markdown",
    "simulate_mock_account_fetch",
    "simulate_mock_journal_update",
    "simulate_mock_observability_events",
    "simulate_mock_order_status",
    "simulate_mock_order_submit",
    "simulate_mock_positions_fetch",
    "simulate_mock_session_connect",
    "simulate_mock_session_disconnect",
]
