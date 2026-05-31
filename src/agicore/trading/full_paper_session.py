"""Offline full paper session orchestration for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.full_paper_session_models import (
    FullPaperSessionCheck,
    FullPaperSessionGraph,
    FullPaperSessionInput,
    FullPaperSessionRecommendation,
    FullPaperSessionResult,
    FullPaperSessionRisk,
    FullPaperSessionScore,
    FullPaperSessionState,
)


def _coerce_input(data: FullPaperSessionInput | Mapping[str, Any]) -> FullPaperSessionInput:
    if isinstance(data, FullPaperSessionInput):
        return data
    return FullPaperSessionInput(**dict(data))


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


def _upstream_items(data: FullPaperSessionInput) -> tuple[Any, ...]:
    return (
        data.simulated_market_session,
        data.mock_alpaca_session,
        data.mock_connectivity_layer,
        data.paper_trading_end_to_end,
        data.paper_dry_run,
        data.supervised_paper_trial,
        data.observability_verification,
        data.kill_switch_verification,
        data.rollback_verification,
    )


def _upstream_risks(data: FullPaperSessionInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: FullPaperSessionInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _make_check(name: str, score: int, risk: FullPaperSessionRisk, required: tuple[bool | None, ...], events: tuple[str, ...], extra_risks: tuple[FullPaperSessionRisk, ...] = ()) -> FullPaperSessionCheck:
    risks: list[FullPaperSessionRisk] = []
    if any(value is not True for value in required) or score < 85:
        risks.append(risk)
    risks.extend(extra_risks)
    return FullPaperSessionCheck(name, score, not risks and score >= 85, _dedupe(risks), events)


def simulate_session_market_cycles(data: FullPaperSessionInput | Mapping[str, Any]) -> FullPaperSessionCheck:
    data = _coerce_input(data)
    score = _clamp(data.market_cycles_score) if data.market_cycles_score is not None else _average((
        _bool_score(data.market_cycles_available),
        _bool_score(data.market_cycles_schema_valid),
        _bool_score(data.market_cycles_replayable),
        _bool_score(data.market_cycles_count_valid),
    ), default=45)
    extra = (FullPaperSessionRisk.SESSION_STATE_DRIFT,) if data.market_cycles_replayable is not True else ()
    events = (
        f"market_cycles_score={score}/100",
        f"market_cycles_available={data.market_cycles_available}",
        f"market_cycles_schema_valid={data.market_cycles_schema_valid}",
        f"market_cycles_replayable={data.market_cycles_replayable}",
        f"market_cycles_count_valid={data.market_cycles_count_valid}",
    )
    return _make_check("market_cycles", score, FullPaperSessionRisk.MARKET_CYCLE_FAILURE, (data.market_cycles_available, data.market_cycles_schema_valid, data.market_cycles_count_valid), events, extra)


def simulate_session_signal_cycles(data: FullPaperSessionInput | Mapping[str, Any]) -> FullPaperSessionCheck:
    data = _coerce_input(data)
    score = _clamp(data.signal_cycles_score) if data.signal_cycles_score is not None else _average((
        _bool_score(data.signal_cycles_generated),
        _bool_score(data.signal_cycles_deterministic),
        _bool_score(data.signal_cycles_traceable),
        _bool_score(data.signal_cycles_count_aligned),
    ), default=45)
    extra = (FullPaperSessionRisk.OBSERVABILITY_GAP,) if data.signal_cycles_traceable is not True else ()
    events = (
        f"signal_cycles_score={score}/100",
        f"signal_cycles_generated={data.signal_cycles_generated}",
        f"signal_cycles_deterministic={data.signal_cycles_deterministic}",
        f"signal_cycles_traceable={data.signal_cycles_traceable}",
        f"signal_cycles_count_aligned={data.signal_cycles_count_aligned}",
    )
    return _make_check("signal_cycles", score, FullPaperSessionRisk.SIGNAL_CYCLE_FAILURE, (data.signal_cycles_generated, data.signal_cycles_deterministic, data.signal_cycles_count_aligned), events, extra)


def simulate_session_decision_cycles(data: FullPaperSessionInput | Mapping[str, Any]) -> FullPaperSessionCheck:
    data = _coerce_input(data)
    score = _clamp(data.decision_cycles_score) if data.decision_cycles_score is not None else _average((
        _bool_score(data.decision_cycles_generated),
        _bool_score(data.decision_cycles_deterministic),
        _bool_score(data.decision_cycles_safety_checked),
        _bool_score(data.decision_cycles_traceable),
    ), default=45)
    extra: list[FullPaperSessionRisk] = []
    if data.decision_cycles_safety_checked is not True:
        extra.append(FullPaperSessionRisk.SAFETY_BOUNDARY_BYPASS)
    if data.decision_cycles_traceable is not True:
        extra.append(FullPaperSessionRisk.OBSERVABILITY_GAP)
    events = (
        f"decision_cycles_score={score}/100",
        f"decision_cycles_generated={data.decision_cycles_generated}",
        f"decision_cycles_deterministic={data.decision_cycles_deterministic}",
        f"decision_cycles_safety_checked={data.decision_cycles_safety_checked}",
        f"decision_cycles_traceable={data.decision_cycles_traceable}",
    )
    return _make_check("decision_cycles", score, FullPaperSessionRisk.DECISION_CYCLE_FAILURE, (data.decision_cycles_generated, data.decision_cycles_deterministic), events, tuple(extra))


def simulate_session_order_cycles(data: FullPaperSessionInput | Mapping[str, Any]) -> FullPaperSessionCheck:
    data = _coerce_input(data)
    score = _clamp(data.order_cycles_score) if data.order_cycles_score is not None else _average((
        _bool_score(data.order_cycles_created),
        _bool_score(data.order_cycles_validated),
        _bool_score(data.order_cycles_status_progressed),
        _bool_score(data.order_cycles_not_routed),
    ), default=45)
    extra = (FullPaperSessionRisk.SAFETY_BOUNDARY_BYPASS,) if data.order_cycles_not_routed is not True else ()
    events = (
        f"order_cycles_score={score}/100",
        f"order_cycles_created={data.order_cycles_created}",
        f"order_cycles_validated={data.order_cycles_validated}",
        f"order_cycles_status_progressed={data.order_cycles_status_progressed}",
        f"order_cycles_not_routed={data.order_cycles_not_routed}",
    )
    return _make_check("order_cycles", score, FullPaperSessionRisk.ORDER_CYCLE_FAILURE, (data.order_cycles_created, data.order_cycles_validated, data.order_cycles_status_progressed), events, extra)


def simulate_session_position_cycles(data: FullPaperSessionInput | Mapping[str, Any]) -> FullPaperSessionCheck:
    data = _coerce_input(data)
    score = _clamp(data.position_cycles_score) if data.position_cycles_score is not None else _average((
        _bool_score(data.position_cycles_updated),
        _bool_score(data.position_cycles_reconciled),
        _bool_score(data.position_cycles_isolated),
        _bool_score(data.position_cycles_traceable),
    ), default=45)
    extra: list[FullPaperSessionRisk] = []
    if data.position_cycles_reconciled is not True or data.position_cycles_isolated is not True:
        extra.append(FullPaperSessionRisk.SESSION_STATE_DRIFT)
    if data.position_cycles_traceable is not True:
        extra.append(FullPaperSessionRisk.OBSERVABILITY_GAP)
    events = (
        f"position_cycles_score={score}/100",
        f"position_cycles_updated={data.position_cycles_updated}",
        f"position_cycles_reconciled={data.position_cycles_reconciled}",
        f"position_cycles_isolated={data.position_cycles_isolated}",
        f"position_cycles_traceable={data.position_cycles_traceable}",
    )
    return _make_check("position_cycles", score, FullPaperSessionRisk.POSITION_CYCLE_FAILURE, (data.position_cycles_updated,), events, tuple(extra))


def simulate_session_pnl_cycles(data: FullPaperSessionInput | Mapping[str, Any]) -> FullPaperSessionCheck:
    data = _coerce_input(data)
    score = _clamp(data.pnl_cycles_score) if data.pnl_cycles_score is not None else _average((
        _bool_score(data.pnl_cycles_calculated),
        _bool_score(data.pnl_cycles_reconciled),
        _bool_score(data.pnl_cycles_deterministic),
        _bool_score(data.pnl_cycles_traceable),
    ), default=45)
    extra = (FullPaperSessionRisk.OBSERVABILITY_GAP,) if data.pnl_cycles_traceable is not True else ()
    events = (
        f"pnl_cycles_score={score}/100",
        f"pnl_cycles_calculated={data.pnl_cycles_calculated}",
        f"pnl_cycles_reconciled={data.pnl_cycles_reconciled}",
        f"pnl_cycles_deterministic={data.pnl_cycles_deterministic}",
        f"pnl_cycles_traceable={data.pnl_cycles_traceable}",
    )
    return _make_check("pnl_cycles", score, FullPaperSessionRisk.PNL_CYCLE_FAILURE, (data.pnl_cycles_calculated, data.pnl_cycles_reconciled, data.pnl_cycles_deterministic), events, extra)


def simulate_session_risk_management(data: FullPaperSessionInput | Mapping[str, Any]) -> FullPaperSessionCheck:
    data = _coerce_input(data)
    score = _clamp(data.risk_management_score) if data.risk_management_score is not None else _average((
        _bool_score(data.risk_limits_defined),
        _bool_score(data.risk_limits_enforced),
        _bool_score(data.risk_breaches_blocked),
        _bool_score(data.risk_state_traceable),
    ), default=45)
    extra: list[FullPaperSessionRisk] = []
    if data.risk_limits_enforced is not True or data.risk_breaches_blocked is not True:
        extra.append(FullPaperSessionRisk.SAFETY_BOUNDARY_BYPASS)
    if data.risk_state_traceable is not True:
        extra.append(FullPaperSessionRisk.OBSERVABILITY_GAP)
    events = (
        f"risk_management_score={score}/100",
        f"risk_limits_defined={data.risk_limits_defined}",
        f"risk_limits_enforced={data.risk_limits_enforced}",
        f"risk_breaches_blocked={data.risk_breaches_blocked}",
        f"risk_state_traceable={data.risk_state_traceable}",
    )
    return _make_check("risk_management", score, FullPaperSessionRisk.RISK_MANAGEMENT_FAILURE, (data.risk_limits_defined,), events, tuple(extra))


def simulate_session_journal(data: FullPaperSessionInput | Mapping[str, Any]) -> FullPaperSessionCheck:
    data = _coerce_input(data)
    score = _clamp(data.journal_score) if data.journal_score is not None else _average((
        _bool_score(data.journal_created),
        _bool_score(data.journal_complete),
        _bool_score(data.journal_replayable),
        _bool_score(data.journal_traceable),
    ), default=45)
    extra: list[FullPaperSessionRisk] = []
    if data.journal_replayable is not True:
        extra.append(FullPaperSessionRisk.SESSION_STATE_DRIFT)
    if data.journal_traceable is not True:
        extra.append(FullPaperSessionRisk.OBSERVABILITY_GAP)
    events = (
        f"journal_score={score}/100",
        f"journal_created={data.journal_created}",
        f"journal_complete={data.journal_complete}",
        f"journal_replayable={data.journal_replayable}",
        f"journal_traceable={data.journal_traceable}",
    )
    return _make_check("journal", score, FullPaperSessionRisk.JOURNAL_INCOMPLETE, (data.journal_created, data.journal_complete), events, tuple(extra))


def simulate_session_observability(data: FullPaperSessionInput | Mapping[str, Any]) -> FullPaperSessionCheck:
    data = _coerce_input(data)
    score = _clamp(data.observability_score) if data.observability_score is not None else _average((
        _bool_score(data.observability_events_emitted),
        _bool_score(data.metrics_recorded),
        _bool_score(data.traces_recorded),
        _bool_score(data.alerts_recorded),
    ), default=45)
    upstream_gap = _has_upstream_risk(data, "OBSERVABILITY")
    events = (
        f"observability_score={score}/100",
        f"observability_events_emitted={data.observability_events_emitted}",
        f"metrics_recorded={data.metrics_recorded}",
        f"traces_recorded={data.traces_recorded}",
        f"alerts_recorded={data.alerts_recorded}",
    )
    extra = (FullPaperSessionRisk.OBSERVABILITY_GAP,) if upstream_gap else ()
    return _make_check("observability", score, FullPaperSessionRisk.OBSERVABILITY_GAP, (data.observability_events_emitted, data.metrics_recorded, data.traces_recorded, data.alerts_recorded), events, extra)


def verify_session_rollback(data: FullPaperSessionInput | Mapping[str, Any]) -> FullPaperSessionCheck:
    data = _coerce_input(data)
    score = _clamp(data.rollback_score) if data.rollback_score is not None else _average((
        _bool_score(data.rollback_checkpoint_created),
        _bool_score(data.rollback_restore_verified),
        _bool_score(data.rollback_state_reconciled),
        _bool_score(data.rollback_observed),
    ), default=45)
    extra: list[FullPaperSessionRisk] = []
    if data.rollback_state_reconciled is not True:
        extra.append(FullPaperSessionRisk.SESSION_STATE_DRIFT)
    if data.rollback_observed is not True:
        extra.append(FullPaperSessionRisk.OBSERVABILITY_GAP)
    events = (
        f"rollback_score={score}/100",
        f"rollback_checkpoint_created={data.rollback_checkpoint_created}",
        f"rollback_restore_verified={data.rollback_restore_verified}",
        f"rollback_state_reconciled={data.rollback_state_reconciled}",
        f"rollback_observed={data.rollback_observed}",
    )
    return _make_check("rollback", score, FullPaperSessionRisk.ROLLBACK_FAILURE, (data.rollback_checkpoint_created, data.rollback_restore_verified), events, tuple(extra))


def verify_session_kill_switch(data: FullPaperSessionInput | Mapping[str, Any]) -> FullPaperSessionCheck:
    data = _coerce_input(data)
    score = _clamp(data.kill_switch_score) if data.kill_switch_score is not None else _average((
        _bool_score(data.kill_switch_available),
        _bool_score(data.kill_switch_halts_orders),
        _bool_score(data.kill_switch_halts_session),
        _bool_score(data.kill_switch_observed),
    ), default=45)
    extra: list[FullPaperSessionRisk] = []
    if data.kill_switch_halts_orders is not True or data.kill_switch_halts_session is not True:
        extra.append(FullPaperSessionRisk.SAFETY_BOUNDARY_BYPASS)
    if data.kill_switch_observed is not True:
        extra.append(FullPaperSessionRisk.OBSERVABILITY_GAP)
    events = (
        f"kill_switch_score={score}/100",
        f"kill_switch_available={data.kill_switch_available}",
        f"kill_switch_halts_orders={data.kill_switch_halts_orders}",
        f"kill_switch_halts_session={data.kill_switch_halts_session}",
        f"kill_switch_observed={data.kill_switch_observed}",
    )
    return _make_check("kill_switch", score, FullPaperSessionRisk.KILL_SWITCH_FAILURE, (data.kill_switch_available,), events, tuple(extra))


def detect_full_session_risks(data: FullPaperSessionInput | Mapping[str, Any], *checks: FullPaperSessionCheck) -> tuple[FullPaperSessionRisk, ...]:
    data = _coerce_input(data)
    if not checks:
        checks = (
            simulate_session_market_cycles(data),
            simulate_session_signal_cycles(data),
            simulate_session_decision_cycles(data),
            simulate_session_order_cycles(data),
            simulate_session_position_cycles(data),
            simulate_session_pnl_cycles(data),
            simulate_session_risk_management(data),
            simulate_session_journal(data),
            simulate_session_observability(data),
            verify_session_rollback(data),
            verify_session_kill_switch(data),
        )
    risks: list[FullPaperSessionRisk] = []
    for check in checks:
        risks.extend(check.risks)
    if (
        data.session_state_snapshot_consistent is not True
        or data.session_state_replay_consistent is not True
        or data.session_state_recovery_verified is not True
        or data.session_state_isolated is not True
    ):
        risks.append(FullPaperSessionRisk.SESSION_STATE_DRIFT)
    if (
        data.offline_mode_enforced is not True
        or data.no_real_broker is not True
        or data.no_api_key_read is not True
        or data.no_http_transport is not True
        or data.no_websocket_transport is not True
        or data.no_socket_transport is not True
        or data.no_external_api is not True
        or data.no_real_order is not True
        or _has_upstream_risk(data, "BROKER", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK", "EXTERNAL_DEPENDENCY", "KILL_SWITCH", "ROLLBACK", "SAFETY")
    ):
        risks.append(FullPaperSessionRisk.SAFETY_BOUNDARY_BYPASS)
    return _dedupe(risks)


def compute_full_session_score(data: FullPaperSessionInput | Mapping[str, Any], risks: tuple[FullPaperSessionRisk, ...] = (), *checks: FullPaperSessionCheck) -> FullPaperSessionScore:
    data = _coerce_input(data)
    if not checks:
        checks = (
            simulate_session_market_cycles(data),
            simulate_session_signal_cycles(data),
            simulate_session_decision_cycles(data),
            simulate_session_order_cycles(data),
            simulate_session_position_cycles(data),
            simulate_session_pnl_cycles(data),
            simulate_session_risk_management(data),
            simulate_session_journal(data),
            simulate_session_observability(data),
            verify_session_rollback(data),
            verify_session_kill_switch(data),
        )
    weighted = _weighted_average((
        (checks[0].score, 1.1),
        (checks[1].score, 1.0),
        (checks[2].score, 1.15),
        (checks[3].score, 1.2),
        (checks[4].score, 1.05),
        (checks[5].score, 1.0),
        (checks[6].score, 1.2),
        (checks[7].score, 1.0),
        (checks[8].score, 1.1),
        (checks[9].score, 1.15),
        (checks[10].score, 1.2),
    ))
    state_score = _average((
        _bool_score(data.session_state_snapshot_consistent),
        _bool_score(data.session_state_replay_consistent),
        _bool_score(data.session_state_recovery_verified),
        _bool_score(data.session_state_isolated),
    ), default=45)
    overall = _clamp(_weighted_average(((weighted, 1.0), (state_score, 0.35))) - min(80, len(set(risks)) * 5))
    for risk, cap in {
        FullPaperSessionRisk.MARKET_CYCLE_FAILURE: 45,
        FullPaperSessionRisk.ORDER_CYCLE_FAILURE: 50,
        FullPaperSessionRisk.RISK_MANAGEMENT_FAILURE: 45,
        FullPaperSessionRisk.ROLLBACK_FAILURE: 45,
        FullPaperSessionRisk.KILL_SWITCH_FAILURE: 40,
        FullPaperSessionRisk.SESSION_STATE_DRIFT: 45,
        FullPaperSessionRisk.SAFETY_BOUNDARY_BYPASS: 40,
    }.items():
        if risk in risks:
            overall = min(overall, cap)
    return FullPaperSessionScore(
        overall, checks[0].score, checks[1].score, checks[2].score, checks[3].score,
        checks[4].score, checks[5].score, checks[6].score, checks[7].score,
        checks[8].score, checks[9].score, checks[10].score,
    )


def _build_graph(risks: tuple[FullPaperSessionRisk, ...]) -> FullPaperSessionGraph:
    nodes = ("market", "signals", "decisions", "orders", "positions", "pnl", "risk", "journal", "observability", "rollback", "kill_switch", "paper_runtime")
    edges = (
        ("market", "signals", "feeds"),
        ("signals", "decisions", "informs"),
        ("decisions", "orders", "authorizes"),
        ("orders", "positions", "updates"),
        ("positions", "pnl", "marks"),
        ("pnl", "risk", "checks"),
        ("risk", "journal", "records"),
        ("journal", "observability", "emits"),
        ("observability", "rollback", "verifies"),
        ("rollback", "kill_switch", "guards"),
        ("kill_switch", "paper_runtime", "authorizes"),
    )
    mapping = {
        FullPaperSessionRisk.MARKET_CYCLE_FAILURE: ("market", "signals"),
        FullPaperSessionRisk.SIGNAL_CYCLE_FAILURE: ("signals", "decisions"),
        FullPaperSessionRisk.DECISION_CYCLE_FAILURE: ("decisions", "orders"),
        FullPaperSessionRisk.ORDER_CYCLE_FAILURE: ("orders", "positions"),
        FullPaperSessionRisk.POSITION_CYCLE_FAILURE: ("positions", "pnl"),
        FullPaperSessionRisk.PNL_CYCLE_FAILURE: ("pnl", "risk"),
        FullPaperSessionRisk.RISK_MANAGEMENT_FAILURE: ("risk", "journal"),
        FullPaperSessionRisk.JOURNAL_INCOMPLETE: ("journal", "observability"),
        FullPaperSessionRisk.OBSERVABILITY_GAP: ("observability", "rollback"),
        FullPaperSessionRisk.ROLLBACK_FAILURE: ("rollback", "kill_switch"),
        FullPaperSessionRisk.KILL_SWITCH_FAILURE: ("kill_switch", "paper_runtime"),
        FullPaperSessionRisk.SESSION_STATE_DRIFT: ("kill_switch", "paper_runtime"),
        FullPaperSessionRisk.SAFETY_BOUNDARY_BYPASS: ("kill_switch", "paper_runtime"),
    }
    blocked = [edge for risk, edge in mapping.items() if risk in risks]
    return FullPaperSessionGraph(nodes, edges, tuple((source, target) for source, target, _ in edges), _dedupe(blocked))


def _select_state(score: int, risks: tuple[FullPaperSessionRisk, ...], completed: bool | None, ready_for_runtime: bool | None) -> FullPaperSessionState:
    hard = {
        FullPaperSessionRisk.MARKET_CYCLE_FAILURE,
        FullPaperSessionRisk.ORDER_CYCLE_FAILURE,
        FullPaperSessionRisk.RISK_MANAGEMENT_FAILURE,
        FullPaperSessionRisk.ROLLBACK_FAILURE,
        FullPaperSessionRisk.KILL_SWITCH_FAILURE,
        FullPaperSessionRisk.SESSION_STATE_DRIFT,
        FullPaperSessionRisk.SAFETY_BOUNDARY_BYPASS,
    }
    count = len(set(risks))
    if hard.intersection(risks) or score < 45 or count >= 7:
        return FullPaperSessionState.NOT_READY
    if count >= 3 or score < 72:
        return FullPaperSessionState.REVIEW_REQUIRED
    if count:
        return FullPaperSessionState.PARTIALLY_READY
    if completed is True and ready_for_runtime is True and score >= 94:
        return FullPaperSessionState.READY_FOR_PAPER_TRADING_RUNTIME
    if completed is True and score >= 90:
        return FullPaperSessionState.FULL_SESSION_COMPLETED
    if score >= 85:
        return FullPaperSessionState.FULL_SESSION_READY
    return FullPaperSessionState.PARTIALLY_READY


def generate_full_session_recommendations(risks: tuple[FullPaperSessionRisk, ...], state: FullPaperSessionState | None = None) -> tuple[FullPaperSessionRecommendation, ...]:
    recommendations: list[FullPaperSessionRecommendation] = []
    if risks:
        recommendations.append(FullPaperSessionRecommendation.HOLD_PAPER_TRADING_RUNTIME_APPROVAL)
    mapping = {
        FullPaperSessionRisk.MARKET_CYCLE_FAILURE: FullPaperSessionRecommendation.REPAIR_MARKET_CYCLES,
        FullPaperSessionRisk.SIGNAL_CYCLE_FAILURE: FullPaperSessionRecommendation.REPAIR_SIGNAL_CYCLES,
        FullPaperSessionRisk.DECISION_CYCLE_FAILURE: FullPaperSessionRecommendation.REPAIR_DECISION_CYCLES,
        FullPaperSessionRisk.ORDER_CYCLE_FAILURE: FullPaperSessionRecommendation.REPAIR_ORDER_CYCLES,
        FullPaperSessionRisk.POSITION_CYCLE_FAILURE: FullPaperSessionRecommendation.REPAIR_POSITION_CYCLES,
        FullPaperSessionRisk.PNL_CYCLE_FAILURE: FullPaperSessionRecommendation.REPAIR_PNL_CYCLES,
        FullPaperSessionRisk.RISK_MANAGEMENT_FAILURE: FullPaperSessionRecommendation.REPAIR_RISK_MANAGEMENT,
        FullPaperSessionRisk.JOURNAL_INCOMPLETE: FullPaperSessionRecommendation.COMPLETE_FULL_SESSION_JOURNAL,
        FullPaperSessionRisk.OBSERVABILITY_GAP: FullPaperSessionRecommendation.RESTORE_FULL_SESSION_OBSERVABILITY,
        FullPaperSessionRisk.ROLLBACK_FAILURE: FullPaperSessionRecommendation.REPAIR_SESSION_ROLLBACK,
        FullPaperSessionRisk.KILL_SWITCH_FAILURE: FullPaperSessionRecommendation.REPAIR_SESSION_KILL_SWITCH,
        FullPaperSessionRisk.SESSION_STATE_DRIFT: FullPaperSessionRecommendation.RECONCILE_FULL_SESSION_STATE,
        FullPaperSessionRisk.SAFETY_BOUNDARY_BYPASS: FullPaperSessionRecommendation.ENFORCE_FULL_SESSION_SAFETY_BOUNDARY,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(FullPaperSessionRecommendation.RUN_FULL_PAPER_SESSION_SUITE)
    if state == FullPaperSessionState.READY_FOR_PAPER_TRADING_RUNTIME:
        recommendations.append(FullPaperSessionRecommendation.APPROVE_PAPER_TRADING_RUNTIME_AFTER_MANUAL_REVIEW)
    return _dedupe(recommendations)


def evaluate_full_paper_session(data: FullPaperSessionInput | Mapping[str, Any]) -> FullPaperSessionResult:
    data = _coerce_input(data)
    checks = (
        simulate_session_market_cycles(data),
        simulate_session_signal_cycles(data),
        simulate_session_decision_cycles(data),
        simulate_session_order_cycles(data),
        simulate_session_position_cycles(data),
        simulate_session_pnl_cycles(data),
        simulate_session_risk_management(data),
        simulate_session_journal(data),
        simulate_session_observability(data),
        verify_session_rollback(data),
        verify_session_kill_switch(data),
    )
    risks = detect_full_session_risks(data, *checks)
    score = compute_full_session_score(data, risks, *checks)
    state = _select_state(score.overall_score, risks, data.full_session_completed, data.ready_for_paper_trading_runtime)
    graph = _build_graph(risks)
    recommendations = generate_full_session_recommendations(risks, state)
    offline_only = (
        data.offline_mode_enforced is True
        and data.no_real_broker is True
        and data.no_api_key_read is True
        and data.no_http_transport is True
        and data.no_websocket_transport is True
        and data.no_socket_transport is True
        and data.no_external_api is True
        and data.no_real_order is True
        and data.order_cycles_not_routed is True
        and not _has_upstream_risk(data, "BROKER", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK", "EXTERNAL_DEPENDENCY")
    )
    summary = f"{state.value}: score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return FullPaperSessionResult(
        state, score.overall_score, score, risks,
        checks[0], checks[1], checks[2], checks[3], checks[4], checks[5],
        checks[6], checks[7], checks[8], checks[9], checks[10],
        graph, recommendations, offline_only, summary,
    )


def render_full_paper_session_markdown(result: FullPaperSessionResult) -> str:
    lines = [
        "# AGIcore Full Paper Session",
        f"- State: {result.state.value}",
        f"- Score: {result.full_session_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Score Breakdown",
        f"- Market cycles: {result.score_breakdown.market_cycles_score}/100",
        f"- Signal cycles: {result.score_breakdown.signal_cycles_score}/100",
        f"- Decision cycles: {result.score_breakdown.decision_cycles_score}/100",
        f"- Order cycles: {result.score_breakdown.order_cycles_score}/100",
        f"- Position cycles: {result.score_breakdown.position_cycles_score}/100",
        f"- PnL cycles: {result.score_breakdown.pnl_cycles_score}/100",
        f"- Risk management: {result.score_breakdown.risk_management_score}/100",
        f"- Journal: {result.score_breakdown.journal_score}/100",
        f"- Observability: {result.score_breakdown.observability_score}/100",
        f"- Rollback: {result.score_breakdown.rollback_score}/100",
        f"- Kill switch: {result.score_breakdown.kill_switch_score}/100",
        "",
        "# Full Paper Session Checks",
    ]
    checks = (
        result.market_cycles, result.signal_cycles, result.decision_cycles, result.order_cycles,
        result.position_cycles, result.pnl_cycles, result.risk_management, result.journal,
        result.observability, result.rollback, result.kill_switch,
    )
    for check in checks:
        lines.append(f"- {check.name}: passed={check.passed}, score={check.score}/100, risks={', '.join(risk.value for risk in check.risks) or 'none'}")
        lines.extend(f"  - {event}" for event in check.events)
    lines.append("")
    lines.append("# Full Paper Session Graph")
    lines.append(f"- Nodes: {', '.join(result.session_graph.nodes)}")
    lines.extend(f"- Edge: {source} -> {target} ({label})" for source, target, label in result.session_graph.edges)
    lines.append("- Blocked edges: " + (", ".join(f"{source}->{target}" for source, target in result.session_graph.blocked_edges) or "none"))
    lines.append("")
    lines.append("# Full Paper Session Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Full Paper Session Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_full_session_score",
    "detect_full_session_risks",
    "evaluate_full_paper_session",
    "generate_full_session_recommendations",
    "render_full_paper_session_markdown",
    "simulate_session_decision_cycles",
    "simulate_session_journal",
    "simulate_session_market_cycles",
    "simulate_session_observability",
    "simulate_session_order_cycles",
    "simulate_session_pnl_cycles",
    "simulate_session_position_cycles",
    "simulate_session_risk_management",
    "simulate_session_signal_cycles",
    "verify_session_kill_switch",
    "verify_session_rollback",
]
