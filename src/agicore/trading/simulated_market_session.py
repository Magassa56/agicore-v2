"""Offline simulated market session for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.simulated_market_session_models import (
    SimulatedMarketSessionFlow,
    SimulatedMarketSessionGraph,
    SimulatedMarketSessionInput,
    SimulatedMarketSessionRecommendation,
    SimulatedMarketSessionResult,
    SimulatedMarketSessionRisk,
    SimulatedMarketSessionScore,
    SimulatedMarketSessionState,
)


def _coerce_input(data: SimulatedMarketSessionInput | Mapping[str, Any]) -> SimulatedMarketSessionInput:
    if isinstance(data, SimulatedMarketSessionInput):
        return data
    return SimulatedMarketSessionInput(**dict(data))


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


def _upstream_items(data: SimulatedMarketSessionInput) -> tuple[Any, ...]:
    return (
        data.mock_alpaca_session,
        data.mock_connectivity_layer,
        data.alpaca_paper_connectivity_readiness,
        data.broker_paper_sandbox,
        data.paper_trading_end_to_end,
        data.paper_dry_run,
        data.supervised_paper_trial,
        data.observability_verification,
        data.kill_switch_verification,
        data.rollback_verification,
    )


def _upstream_risks(data: SimulatedMarketSessionInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: SimulatedMarketSessionInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _upstream_score(data: SimulatedMarketSessionInput, *names: str) -> int | None:
    values: list[int] = []
    for item in _upstream_items(data):
        values.extend(_score(item, name) for name in names)
        breakdown = _get(item, "score_breakdown")
        values.extend(_score(breakdown, name) for name in names)
    values = [value for value in values if value is not None]
    return _average(values) if values else None


def simulate_market_data_flow(data: SimulatedMarketSessionInput | Mapping[str, Any]) -> SimulatedMarketSessionFlow:
    data = _coerce_input(data)
    score = _clamp(data.market_data_score) if data.market_data_score is not None else _average(
        (
            _bool_score(data.fictive_market_data_available),
            _bool_score(data.market_data_schema_valid),
            _bool_score(data.market_data_sequence_ordered),
            _bool_score(data.market_data_replayable),
        ),
        default=45,
    )
    risks: list[SimulatedMarketSessionRisk] = []
    if (
        data.fictive_market_data_available is not True
        or data.market_data_schema_valid is not True
        or data.market_data_sequence_ordered is not True
        or score < 85
    ):
        risks.append(SimulatedMarketSessionRisk.MARKET_DATA_MISSING)
    if data.market_data_replayable is not True:
        risks.append(SimulatedMarketSessionRisk.SESSION_STATE_DRIFT)
    events = (
        f"market_data_score={score}/100",
        f"fictive_market_data_available={data.fictive_market_data_available}",
        f"market_data_schema_valid={data.market_data_schema_valid}",
        f"market_data_sequence_ordered={data.market_data_sequence_ordered}",
        f"market_data_replayable={data.market_data_replayable}",
    )
    return SimulatedMarketSessionFlow("market_data_flow", score, not risks and score >= 85, _dedupe(risks), events)


def simulate_signal_generation_flow(data: SimulatedMarketSessionInput | Mapping[str, Any]) -> SimulatedMarketSessionFlow:
    data = _coerce_input(data)
    score = _clamp(data.signal_generation_score) if data.signal_generation_score is not None else _average(
        (
            _bool_score(data.signal_inputs_available),
            _bool_score(data.signal_generation_deterministic),
            _bool_score(data.signal_schema_valid),
            _bool_score(data.signal_traceable),
        ),
        default=45,
    )
    risks: list[SimulatedMarketSessionRisk] = []
    if (
        data.signal_inputs_available is not True
        or data.signal_generation_deterministic is not True
        or data.signal_schema_valid is not True
        or score < 85
    ):
        risks.append(SimulatedMarketSessionRisk.SIGNAL_GENERATION_FAILURE)
    if data.signal_traceable is not True:
        risks.append(SimulatedMarketSessionRisk.OBSERVABILITY_GAP)
    events = (
        f"signal_generation_score={score}/100",
        f"signal_inputs_available={data.signal_inputs_available}",
        f"signal_generation_deterministic={data.signal_generation_deterministic}",
        f"signal_schema_valid={data.signal_schema_valid}",
        f"signal_traceable={data.signal_traceable}",
    )
    return SimulatedMarketSessionFlow("signal_generation_flow", score, not risks and score >= 85, _dedupe(risks), events)


def simulate_decision_generation_flow(data: SimulatedMarketSessionInput | Mapping[str, Any]) -> SimulatedMarketSessionFlow:
    data = _coerce_input(data)
    score = _clamp(data.decision_generation_score) if data.decision_generation_score is not None else _average(
        (
            _bool_score(data.decision_inputs_available),
            _bool_score(data.decision_generation_deterministic),
            _bool_score(data.decision_schema_valid),
            _bool_score(data.decision_safety_checked),
        ),
        default=45,
    )
    risks: list[SimulatedMarketSessionRisk] = []
    if (
        data.decision_inputs_available is not True
        or data.decision_generation_deterministic is not True
        or data.decision_schema_valid is not True
        or score < 85
    ):
        risks.append(SimulatedMarketSessionRisk.DECISION_GENERATION_FAILURE)
    if data.decision_safety_checked is not True:
        risks.append(SimulatedMarketSessionRisk.SAFETY_BOUNDARY_BYPASS)
    events = (
        f"decision_generation_score={score}/100",
        f"decision_inputs_available={data.decision_inputs_available}",
        f"decision_generation_deterministic={data.decision_generation_deterministic}",
        f"decision_schema_valid={data.decision_schema_valid}",
        f"decision_safety_checked={data.decision_safety_checked}",
    )
    return SimulatedMarketSessionFlow("decision_generation_flow", score, not risks and score >= 85, _dedupe(risks), events)


def simulate_paper_order_lifecycle(data: SimulatedMarketSessionInput | Mapping[str, Any]) -> SimulatedMarketSessionFlow:
    data = _coerce_input(data)
    score = _clamp(data.paper_order_lifecycle_score) if data.paper_order_lifecycle_score is not None else _average(
        (
            _bool_score(data.paper_order_created),
            _bool_score(data.paper_order_validated),
            _bool_score(data.paper_order_status_progressed),
            _bool_score(data.paper_order_not_routed),
            _upstream_score(data, "mock_alpaca_session_score", "end_to_end_score"),
        ),
        default=45,
    )
    risks: list[SimulatedMarketSessionRisk] = []
    if (
        data.paper_order_created is not True
        or data.paper_order_validated is not True
        or data.paper_order_status_progressed is not True
        or score < 85
    ):
        risks.append(SimulatedMarketSessionRisk.ORDER_LIFECYCLE_FAILURE)
    if data.paper_order_not_routed is not True:
        risks.append(SimulatedMarketSessionRisk.SAFETY_BOUNDARY_BYPASS)
    events = (
        f"paper_order_lifecycle_score={score}/100",
        f"paper_order_created={data.paper_order_created}",
        f"paper_order_validated={data.paper_order_validated}",
        f"paper_order_status_progressed={data.paper_order_status_progressed}",
        f"paper_order_not_routed={data.paper_order_not_routed}",
    )
    return SimulatedMarketSessionFlow("paper_order_lifecycle", score, not risks and score >= 85, _dedupe(risks), events)


def simulate_position_lifecycle(data: SimulatedMarketSessionInput | Mapping[str, Any]) -> SimulatedMarketSessionFlow:
    data = _coerce_input(data)
    score = _clamp(data.position_lifecycle_score) if data.position_lifecycle_score is not None else _average(
        (
            _bool_score(data.position_opened),
            _bool_score(data.position_updated),
            _bool_score(data.position_closed_or_carried),
            _bool_score(data.position_reconciled),
        ),
        default=45,
    )
    risks: list[SimulatedMarketSessionRisk] = []
    if (
        data.position_opened is not True
        or data.position_updated is not True
        or data.position_closed_or_carried is not True
        or score < 85
    ):
        risks.append(SimulatedMarketSessionRisk.POSITION_LIFECYCLE_FAILURE)
    if data.position_reconciled is not True:
        risks.append(SimulatedMarketSessionRisk.SESSION_STATE_DRIFT)
    events = (
        f"position_lifecycle_score={score}/100",
        f"position_opened={data.position_opened}",
        f"position_updated={data.position_updated}",
        f"position_closed_or_carried={data.position_closed_or_carried}",
        f"position_reconciled={data.position_reconciled}",
    )
    return SimulatedMarketSessionFlow("position_lifecycle", score, not risks and score >= 85, _dedupe(risks), events)


def simulate_paper_pnl_flow(data: SimulatedMarketSessionInput | Mapping[str, Any]) -> SimulatedMarketSessionFlow:
    data = _coerce_input(data)
    score = _clamp(data.paper_pnl_score) if data.paper_pnl_score is not None else _average(
        (
            _bool_score(data.paper_pnl_calculated),
            _bool_score(data.paper_pnl_reconciled),
            _bool_score(data.paper_pnl_traceable),
            _bool_score(data.paper_pnl_deterministic),
        ),
        default=45,
    )
    risks: list[SimulatedMarketSessionRisk] = []
    if (
        data.paper_pnl_calculated is not True
        or data.paper_pnl_reconciled is not True
        or data.paper_pnl_deterministic is not True
        or score < 85
    ):
        risks.append(SimulatedMarketSessionRisk.PNL_CALCULATION_FAILURE)
    if data.paper_pnl_traceable is not True:
        risks.append(SimulatedMarketSessionRisk.OBSERVABILITY_GAP)
    events = (
        f"paper_pnl_score={score}/100",
        f"paper_pnl_calculated={data.paper_pnl_calculated}",
        f"paper_pnl_reconciled={data.paper_pnl_reconciled}",
        f"paper_pnl_traceable={data.paper_pnl_traceable}",
        f"paper_pnl_deterministic={data.paper_pnl_deterministic}",
    )
    return SimulatedMarketSessionFlow("paper_pnl_flow", score, not risks and score >= 85, _dedupe(risks), events)


def simulate_session_journal_flow(data: SimulatedMarketSessionInput | Mapping[str, Any]) -> SimulatedMarketSessionFlow:
    data = _coerce_input(data)
    score = _clamp(data.session_journal_score) if data.session_journal_score is not None else _average(
        (
            _bool_score(data.session_journal_created),
            _bool_score(data.session_journal_complete),
            _bool_score(data.session_journal_replayable),
            _bool_score(data.session_journal_traceable),
        ),
        default=45,
    )
    risks: list[SimulatedMarketSessionRisk] = []
    if (
        data.session_journal_created is not True
        or data.session_journal_complete is not True
        or score < 85
    ):
        risks.append(SimulatedMarketSessionRisk.JOURNAL_INCOMPLETE)
    if data.session_journal_traceable is not True:
        risks.append(SimulatedMarketSessionRisk.OBSERVABILITY_GAP)
    if data.session_journal_replayable is not True:
        risks.append(SimulatedMarketSessionRisk.SESSION_STATE_DRIFT)
    events = (
        f"session_journal_score={score}/100",
        f"session_journal_created={data.session_journal_created}",
        f"session_journal_complete={data.session_journal_complete}",
        f"session_journal_replayable={data.session_journal_replayable}",
        f"session_journal_traceable={data.session_journal_traceable}",
    )
    return SimulatedMarketSessionFlow("session_journal_flow", score, not risks and score >= 85, _dedupe(risks), events)


def simulate_session_observability_flow(data: SimulatedMarketSessionInput | Mapping[str, Any]) -> SimulatedMarketSessionFlow:
    data = _coerce_input(data)
    score = _clamp(data.session_observability_score) if data.session_observability_score is not None else _average(
        (
            _bool_score(data.observability_events_emitted),
            _bool_score(data.metrics_recorded),
            _bool_score(data.traces_recorded),
            _bool_score(data.alerts_recorded),
            _upstream_score(data, "observability_score"),
        ),
        default=45,
    )
    risks: list[SimulatedMarketSessionRisk] = []
    if (
        data.observability_events_emitted is not True
        or data.metrics_recorded is not True
        or data.traces_recorded is not True
        or data.alerts_recorded is not True
        or _has_upstream_risk(data, "OBSERVABILITY")
        or score < 85
    ):
        risks.append(SimulatedMarketSessionRisk.OBSERVABILITY_GAP)
    events = (
        f"session_observability_score={score}/100",
        f"observability_events_emitted={data.observability_events_emitted}",
        f"metrics_recorded={data.metrics_recorded}",
        f"traces_recorded={data.traces_recorded}",
        f"alerts_recorded={data.alerts_recorded}",
    )
    return SimulatedMarketSessionFlow("session_observability_flow", score, not risks and score >= 85, tuple(risks), events)


def detect_market_session_risks(
    data: SimulatedMarketSessionInput | Mapping[str, Any],
    market_data_flow: SimulatedMarketSessionFlow | None = None,
    signal_generation_flow: SimulatedMarketSessionFlow | None = None,
    decision_generation_flow: SimulatedMarketSessionFlow | None = None,
    paper_order_lifecycle: SimulatedMarketSessionFlow | None = None,
    position_lifecycle: SimulatedMarketSessionFlow | None = None,
    paper_pnl_flow: SimulatedMarketSessionFlow | None = None,
    session_journal_flow: SimulatedMarketSessionFlow | None = None,
    session_observability_flow: SimulatedMarketSessionFlow | None = None,
) -> tuple[SimulatedMarketSessionRisk, ...]:
    data = _coerce_input(data)
    flows = (
        market_data_flow or simulate_market_data_flow(data),
        signal_generation_flow or simulate_signal_generation_flow(data),
        decision_generation_flow or simulate_decision_generation_flow(data),
        paper_order_lifecycle or simulate_paper_order_lifecycle(data),
        position_lifecycle or simulate_position_lifecycle(data),
        paper_pnl_flow or simulate_paper_pnl_flow(data),
        session_journal_flow or simulate_session_journal_flow(data),
        session_observability_flow or simulate_session_observability_flow(data),
    )
    risks: list[SimulatedMarketSessionRisk] = []
    for flow in flows:
        risks.extend(flow.risks)
    if (
        data.session_state_snapshot_consistent is not True
        or data.session_state_replay_consistent is not True
        or data.session_state_recovery_verified is not True
        or data.session_state_isolated is not True
    ):
        risks.append(SimulatedMarketSessionRisk.SESSION_STATE_DRIFT)
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
        risks.append(SimulatedMarketSessionRisk.SAFETY_BOUNDARY_BYPASS)
    return _dedupe(risks)


def compute_market_session_score(
    data: SimulatedMarketSessionInput | Mapping[str, Any],
    risks: tuple[SimulatedMarketSessionRisk, ...] = (),
    market_data_flow: SimulatedMarketSessionFlow | None = None,
    signal_generation_flow: SimulatedMarketSessionFlow | None = None,
    decision_generation_flow: SimulatedMarketSessionFlow | None = None,
    paper_order_lifecycle: SimulatedMarketSessionFlow | None = None,
    position_lifecycle: SimulatedMarketSessionFlow | None = None,
    paper_pnl_flow: SimulatedMarketSessionFlow | None = None,
    session_journal_flow: SimulatedMarketSessionFlow | None = None,
    session_observability_flow: SimulatedMarketSessionFlow | None = None,
) -> SimulatedMarketSessionScore:
    data = _coerce_input(data)
    market = market_data_flow or simulate_market_data_flow(data)
    signal = signal_generation_flow or simulate_signal_generation_flow(data)
    decision = decision_generation_flow or simulate_decision_generation_flow(data)
    order = paper_order_lifecycle or simulate_paper_order_lifecycle(data)
    position = position_lifecycle or simulate_position_lifecycle(data)
    pnl = paper_pnl_flow or simulate_paper_pnl_flow(data)
    journal = session_journal_flow or simulate_session_journal_flow(data)
    observability = session_observability_flow or simulate_session_observability_flow(data)
    weighted = _weighted_average(
        (
            (market.score, 1.1),
            (signal.score, 1.0),
            (decision.score, 1.15),
            (order.score, 1.2),
            (position.score, 1.05),
            (pnl.score, 1.0),
            (journal.score, 1.0),
            (observability.score, 1.1),
        )
    )
    state_score = _average(
        (
            _bool_score(data.session_state_snapshot_consistent),
            _bool_score(data.session_state_replay_consistent),
            _bool_score(data.session_state_recovery_verified),
            _bool_score(data.session_state_isolated),
        ),
        default=45,
    )
    weighted = _weighted_average(((weighted, 1.0), (state_score, 0.35)))
    penalty = min(75, len(set(risks)) * 6)
    overall = _clamp(weighted - penalty)
    critical_caps = {
        SimulatedMarketSessionRisk.MARKET_DATA_MISSING: 45,
        SimulatedMarketSessionRisk.ORDER_LIFECYCLE_FAILURE: 50,
        SimulatedMarketSessionRisk.SESSION_STATE_DRIFT: 45,
        SimulatedMarketSessionRisk.SAFETY_BOUNDARY_BYPASS: 40,
    }
    for risk, cap in critical_caps.items():
        if risk in risks:
            overall = min(overall, cap)
    return SimulatedMarketSessionScore(
        overall_score=overall,
        market_data_score=market.score,
        signal_generation_score=signal.score,
        decision_generation_score=decision.score,
        paper_order_lifecycle_score=order.score,
        position_lifecycle_score=position.score,
        paper_pnl_score=pnl.score,
        session_journal_score=journal.score,
        session_observability_score=observability.score,
    )


def _build_graph(risks: tuple[SimulatedMarketSessionRisk, ...]) -> SimulatedMarketSessionGraph:
    nodes = (
        "market_data",
        "signals",
        "decisions",
        "paper_orders",
        "positions",
        "paper_pnl",
        "journal",
        "observability",
        "full_paper_session",
    )
    edges = (
        ("market_data", "signals", "feeds"),
        ("signals", "decisions", "informs"),
        ("decisions", "paper_orders", "authorizes"),
        ("paper_orders", "positions", "updates"),
        ("positions", "paper_pnl", "marks"),
        ("paper_pnl", "journal", "records"),
        ("journal", "observability", "emits"),
        ("observability", "full_paper_session", "authorizes"),
    )
    mapping = {
        SimulatedMarketSessionRisk.MARKET_DATA_MISSING: ("market_data", "signals"),
        SimulatedMarketSessionRisk.SIGNAL_GENERATION_FAILURE: ("signals", "decisions"),
        SimulatedMarketSessionRisk.DECISION_GENERATION_FAILURE: ("decisions", "paper_orders"),
        SimulatedMarketSessionRisk.ORDER_LIFECYCLE_FAILURE: ("paper_orders", "positions"),
        SimulatedMarketSessionRisk.POSITION_LIFECYCLE_FAILURE: ("positions", "paper_pnl"),
        SimulatedMarketSessionRisk.PNL_CALCULATION_FAILURE: ("paper_pnl", "journal"),
        SimulatedMarketSessionRisk.JOURNAL_INCOMPLETE: ("journal", "observability"),
        SimulatedMarketSessionRisk.OBSERVABILITY_GAP: ("observability", "full_paper_session"),
        SimulatedMarketSessionRisk.SESSION_STATE_DRIFT: ("observability", "full_paper_session"),
        SimulatedMarketSessionRisk.SAFETY_BOUNDARY_BYPASS: ("observability", "full_paper_session"),
    }
    blocked = [edge for risk, edge in mapping.items() if risk in risks]
    return SimulatedMarketSessionGraph(nodes, edges, tuple((source, target) for source, target, _ in edges), _dedupe(blocked))


def _select_state(
    score: int,
    risks: tuple[SimulatedMarketSessionRisk, ...],
    completed: bool | None,
    ready_for_full_paper: bool | None,
) -> SimulatedMarketSessionState:
    hard = {
        SimulatedMarketSessionRisk.MARKET_DATA_MISSING,
        SimulatedMarketSessionRisk.ORDER_LIFECYCLE_FAILURE,
        SimulatedMarketSessionRisk.SESSION_STATE_DRIFT,
        SimulatedMarketSessionRisk.SAFETY_BOUNDARY_BYPASS,
    }
    count = len(set(risks))
    if hard.intersection(risks) or score < 45 or count >= 6:
        return SimulatedMarketSessionState.NOT_READY
    if count >= 3 or score < 72:
        return SimulatedMarketSessionState.REVIEW_REQUIRED
    if count:
        return SimulatedMarketSessionState.PARTIALLY_READY
    if completed is True and ready_for_full_paper is True and score >= 94:
        return SimulatedMarketSessionState.READY_FOR_FULL_PAPER_SESSION
    if completed is True and score >= 90:
        return SimulatedMarketSessionState.SIMULATED_SESSION_COMPLETED
    if score >= 85:
        return SimulatedMarketSessionState.SIMULATED_SESSION_READY
    return SimulatedMarketSessionState.PARTIALLY_READY


def generate_market_session_recommendations(
    risks: tuple[SimulatedMarketSessionRisk, ...],
    state: SimulatedMarketSessionState | None = None,
) -> tuple[SimulatedMarketSessionRecommendation, ...]:
    recommendations: list[SimulatedMarketSessionRecommendation] = []
    if risks:
        recommendations.append(SimulatedMarketSessionRecommendation.HOLD_FULL_PAPER_SESSION_APPROVAL)
    mapping = {
        SimulatedMarketSessionRisk.MARKET_DATA_MISSING: SimulatedMarketSessionRecommendation.RESTORE_MARKET_DATA_FLOW,
        SimulatedMarketSessionRisk.SIGNAL_GENERATION_FAILURE: SimulatedMarketSessionRecommendation.REPAIR_SIGNAL_GENERATION_FLOW,
        SimulatedMarketSessionRisk.DECISION_GENERATION_FAILURE: SimulatedMarketSessionRecommendation.REPAIR_DECISION_GENERATION_FLOW,
        SimulatedMarketSessionRisk.ORDER_LIFECYCLE_FAILURE: SimulatedMarketSessionRecommendation.REPAIR_ORDER_LIFECYCLE,
        SimulatedMarketSessionRisk.POSITION_LIFECYCLE_FAILURE: SimulatedMarketSessionRecommendation.REPAIR_POSITION_LIFECYCLE,
        SimulatedMarketSessionRisk.PNL_CALCULATION_FAILURE: SimulatedMarketSessionRecommendation.REPAIR_PNL_CALCULATION,
        SimulatedMarketSessionRisk.JOURNAL_INCOMPLETE: SimulatedMarketSessionRecommendation.COMPLETE_SESSION_JOURNAL,
        SimulatedMarketSessionRisk.OBSERVABILITY_GAP: SimulatedMarketSessionRecommendation.RESTORE_SESSION_OBSERVABILITY,
        SimulatedMarketSessionRisk.SESSION_STATE_DRIFT: SimulatedMarketSessionRecommendation.RECONCILE_SESSION_STATE,
        SimulatedMarketSessionRisk.SAFETY_BOUNDARY_BYPASS: SimulatedMarketSessionRecommendation.ENFORCE_MARKET_SESSION_SAFETY_BOUNDARY,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(SimulatedMarketSessionRecommendation.RUN_SIMULATED_MARKET_SESSION_SUITE)
    if state == SimulatedMarketSessionState.READY_FOR_FULL_PAPER_SESSION:
        recommendations.append(SimulatedMarketSessionRecommendation.APPROVE_FULL_PAPER_SESSION_AFTER_MANUAL_REVIEW)
    return _dedupe(recommendations)


def evaluate_simulated_market_session(data: SimulatedMarketSessionInput | Mapping[str, Any]) -> SimulatedMarketSessionResult:
    data = _coerce_input(data)
    market = simulate_market_data_flow(data)
    signal = simulate_signal_generation_flow(data)
    decision = simulate_decision_generation_flow(data)
    order = simulate_paper_order_lifecycle(data)
    position = simulate_position_lifecycle(data)
    pnl = simulate_paper_pnl_flow(data)
    journal = simulate_session_journal_flow(data)
    observability = simulate_session_observability_flow(data)
    risks = detect_market_session_risks(data, market, signal, decision, order, position, pnl, journal, observability)
    score = compute_market_session_score(data, risks, market, signal, decision, order, position, pnl, journal, observability)
    state = _select_state(score.overall_score, risks, data.simulated_session_completed, data.ready_for_full_paper_session)
    graph = _build_graph(risks)
    recommendations = generate_market_session_recommendations(risks, state)
    offline_only = (
        data.offline_mode_enforced is True
        and data.no_real_broker is True
        and data.no_api_key_read is True
        and data.no_http_transport is True
        and data.no_websocket_transport is True
        and data.no_socket_transport is True
        and data.no_external_api is True
        and data.no_real_order is True
        and data.paper_order_not_routed is True
        and not _has_upstream_risk(data, "BROKER", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK", "EXTERNAL_DEPENDENCY")
    )
    summary = f"{state.value}: score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return SimulatedMarketSessionResult(
        state=state,
        market_session_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        market_data_flow=market,
        signal_generation_flow=signal,
        decision_generation_flow=decision,
        paper_order_lifecycle=order,
        position_lifecycle=position,
        paper_pnl_flow=pnl,
        session_journal_flow=journal,
        session_observability_flow=observability,
        market_session_graph=graph,
        recommendations=recommendations,
        offline_only=offline_only,
        summary=summary,
    )


def render_simulated_market_session_markdown(result: SimulatedMarketSessionResult) -> str:
    lines = [
        "# AGIcore Simulated Market Session",
        f"- State: {result.state.value}",
        f"- Score: {result.market_session_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Score Breakdown",
        f"- Market data: {result.score_breakdown.market_data_score}/100",
        f"- Signal generation: {result.score_breakdown.signal_generation_score}/100",
        f"- Decision generation: {result.score_breakdown.decision_generation_score}/100",
        f"- Paper order lifecycle: {result.score_breakdown.paper_order_lifecycle_score}/100",
        f"- Position lifecycle: {result.score_breakdown.position_lifecycle_score}/100",
        f"- Paper PnL: {result.score_breakdown.paper_pnl_score}/100",
        f"- Session journal: {result.score_breakdown.session_journal_score}/100",
        f"- Session observability: {result.score_breakdown.session_observability_score}/100",
        "",
        "# Simulated Market Flows",
    ]
    flows = (
        result.market_data_flow,
        result.signal_generation_flow,
        result.decision_generation_flow,
        result.paper_order_lifecycle,
        result.position_lifecycle,
        result.paper_pnl_flow,
        result.session_journal_flow,
        result.session_observability_flow,
    )
    for flow in flows:
        lines.append(
            f"- {flow.name}: passed={flow.passed}, score={flow.score}/100, "
            f"risks={', '.join(risk.value for risk in flow.risks) or 'none'}"
        )
        lines.extend(f"  - {event}" for event in flow.events)
    lines.append("")
    lines.append("# Simulated Market Session Graph")
    lines.append(f"- Nodes: {', '.join(result.market_session_graph.nodes)}")
    lines.extend(f"- Edge: {source} -> {target} ({label})" for source, target, label in result.market_session_graph.edges)
    lines.append(
        "- Blocked edges: "
        + (", ".join(f"{source}->{target}" for source, target in result.market_session_graph.blocked_edges) or "none")
    )
    lines.append("")
    lines.append("# Simulated Market Session Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Simulated Market Session Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_market_session_score",
    "detect_market_session_risks",
    "evaluate_simulated_market_session",
    "generate_market_session_recommendations",
    "render_simulated_market_session_markdown",
    "simulate_decision_generation_flow",
    "simulate_market_data_flow",
    "simulate_paper_order_lifecycle",
    "simulate_paper_pnl_flow",
    "simulate_position_lifecycle",
    "simulate_session_journal_flow",
    "simulate_session_observability_flow",
    "simulate_signal_generation_flow",
]
