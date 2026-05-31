"""Deterministic offline/sandbox Paper Trading Runtime for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_trading_runtime_models import (
    PaperRuntimeDecision,
    PaperRuntimeMarketSnapshot,
    PaperRuntimeOrder,
    PaperRuntimePosition,
    PaperRuntimeSignal,
    PaperTradingRuntimeInput,
    PaperTradingRuntimeRecommendation,
    PaperTradingRuntimeReport,
    PaperTradingRuntimeResult,
    PaperTradingRuntimeRisk,
    PaperTradingRuntimeState,
    PaperTradingRuntimeStep,
)


def _coerce_input(data: PaperTradingRuntimeInput | Mapping[str, Any]) -> PaperTradingRuntimeInput:
    if isinstance(data, PaperTradingRuntimeInput):
        return data
    return PaperTradingRuntimeInput(**dict(data))


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


def _bool_score(value: bool | None, unknown: int = 45) -> int:
    if value is True:
        return 100
    if value is False:
        return 0
    return unknown


def _average(values: Iterable[int | float | None], default: int = 0) -> int:
    usable = [float(value) for value in values if value is not None]
    if not usable:
        return default
    return _clamp(sum(usable) / len(usable))


def _dedupe(items: Iterable[Any]) -> tuple[Any, ...]:
    seen: set[Any] = set()
    result: list[Any] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return tuple(result)


def _upstream_items(data: PaperTradingRuntimeInput) -> tuple[Any, ...]:
    return (
        data.paper_trading_runtime_design,
        data.paper_runtime_decision_review,
        data.paper_runtime_pre_review,
        data.full_paper_session,
        data.simulated_market_session,
        data.mock_alpaca_session,
        data.mock_connectivity_layer,
        data.alpaca_paper_connectivity_readiness,
        data.broker_paper_sandbox,
        data.paper_trading_end_to_end,
        data.paper_dry_run,
        data.supervised_paper_trial,
        data.observability_verification,
        data.rollback_verification,
        data.kill_switch_verification,
        data.human_validated_paper_session,
        data.supervised_paper_session,
    )


def _upstream_risks(data: PaperTradingRuntimeInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperTradingRuntimeInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _step(
    name: str,
    passed: bool,
    score: int,
    risk: PaperTradingRuntimeRisk | None = None,
    events: tuple[str, ...] = (),
    state: PaperTradingRuntimeState = PaperTradingRuntimeState.RUNNING,
) -> PaperTradingRuntimeStep:
    risks = (risk,) if risk is not None and not passed else ()
    return PaperTradingRuntimeStep(name=name, state=state, passed=passed, score=_clamp(score), risks=risks, events=events)


def _offline_boundary(data: PaperTradingRuntimeInput) -> bool:
    return (
        data.offline_mode_enforced is True
        and data.sandbox_mode_enforced is True
        and data.no_real_broker is True
        and data.no_api_key_read is True
        and data.no_http_transport is True
        and data.no_websocket_transport is True
        and data.no_socket_transport is True
        and data.no_external_api is True
        and data.no_real_order is True
        and data.paper_order_not_routed is True
        and not _has_upstream_risk(data, "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK", "BROKER", "EXTERNAL_DEPENDENCY")
    )


def initialize_paper_runtime_session(data: PaperTradingRuntimeInput | Mapping[str, Any]) -> PaperTradingRuntimeStep:
    data = _coerce_input(data)
    score = _average(
        (
            _bool_score(data.offline_mode_enforced),
            _bool_score(data.sandbox_mode_enforced),
            _bool_score(data.no_real_broker),
            _bool_score(data.no_api_key_read),
            _bool_score(data.no_http_transport),
            _bool_score(data.no_websocket_transport),
            _bool_score(data.no_socket_transport),
            _bool_score(data.no_external_api),
            _bool_score(data.no_real_order),
            _bool_score(data.paper_order_not_routed),
        )
    )
    passed = bool(data.session_id) and _offline_boundary(data) and score >= 85
    events = (
        f"session_id={data.session_id}",
        f"offline_boundary={_offline_boundary(data)}",
        f"sandbox_mode_enforced={data.sandbox_mode_enforced}",
    )
    return _step("runtime_session", passed, score, PaperTradingRuntimeRisk.RUNTIME_INITIALIZATION_FAILURE, events, PaperTradingRuntimeState.READY if passed else PaperTradingRuntimeState.FAILED_SAFE)


def execute_market_cycle(data: PaperTradingRuntimeInput | Mapping[str, Any]) -> tuple[PaperTradingRuntimeStep, PaperRuntimeMarketSnapshot | None]:
    data = _coerce_input(data)
    valid = data.market_price is not None and data.previous_price is not None and data.market_price > 0 and data.previous_price > 0
    passed = valid and not data.force_market_failure
    score = 100 if passed else 0
    snapshot = None
    if valid:
        event = "price_up" if data.market_price >= data.previous_price else "price_down"
        snapshot = PaperRuntimeMarketSnapshot(data.symbol, float(data.market_price), float(data.previous_price), event)
    events = (f"symbol={data.symbol}", f"market_price={data.market_price}", f"previous_price={data.previous_price}")
    return _step("market_cycle", passed, score, PaperTradingRuntimeRisk.MARKET_CYCLE_FAILURE, events), snapshot


def execute_signal_cycle(
    data: PaperTradingRuntimeInput | Mapping[str, Any],
    market_snapshot: PaperRuntimeMarketSnapshot | None = None,
) -> tuple[PaperTradingRuntimeStep, PaperRuntimeSignal | None]:
    data = _coerce_input(data)
    if market_snapshot is None:
        _, market_snapshot = execute_market_cycle(data)
    passed = market_snapshot is not None and not data.force_signal_failure
    signal = None
    if passed:
        action = "BUY" if market_snapshot.price >= market_snapshot.previous_price else "SELL"
        confidence = min(0.99, max(0.51, abs(market_snapshot.price - market_snapshot.previous_price) / market_snapshot.previous_price + 0.55))
        signal = PaperRuntimeSignal(market_snapshot.symbol, action, round(confidence, 4), market_snapshot.event)
    events = (f"signal_available={signal is not None}", f"forced_failure={data.force_signal_failure}")
    return _step("signal_cycle", passed, 100 if passed else 0, PaperTradingRuntimeRisk.SIGNAL_CYCLE_FAILURE, events), signal


def execute_decision_cycle(
    data: PaperTradingRuntimeInput | Mapping[str, Any],
    signal: PaperRuntimeSignal | None = None,
) -> tuple[PaperTradingRuntimeStep, PaperRuntimeDecision | None]:
    data = _coerce_input(data)
    if signal is None:
        _, market = execute_market_cycle(data)
        _, signal = execute_signal_cycle(data, market)
    passed = signal is not None and data.quantity > 0 and not data.force_decision_failure
    decision = None
    if passed:
        decision = PaperRuntimeDecision(signal.symbol, signal.action, float(data.quantity), f"signal:{signal.reason}:{signal.confidence}")
    events = (f"decision_available={decision is not None}", f"quantity={data.quantity}")
    return _step("decision_cycle", passed, 100 if passed else 0, PaperTradingRuntimeRisk.DECISION_CYCLE_FAILURE, events), decision


def execute_safety_gate(
    data: PaperTradingRuntimeInput | Mapping[str, Any],
    decision: PaperRuntimeDecision | None = None,
) -> PaperTradingRuntimeStep:
    data = _coerce_input(data)
    if decision is None:
        _, decision = execute_decision_cycle(data)
    passed = (
        decision is not None
        and data.safety_gate_enabled is True
        and data.risk_limits_enforced is True
        and data.paper_order_not_routed is True
        and _offline_boundary(data)
        and not _has_upstream_risk(data, "SAFETY_BYPASS", "UNSAFE_ORDER", "REAL_ORDER")
    )
    score = _average((_bool_score(data.safety_gate_enabled), _bool_score(data.risk_limits_enforced), _bool_score(data.paper_order_not_routed), _bool_score(_offline_boundary(data))))
    events = (f"safety_gate_enabled={data.safety_gate_enabled}", f"risk_limits_enforced={data.risk_limits_enforced}", "real_order_blocked=True")
    return _step("safety_gate", passed, score, PaperTradingRuntimeRisk.SAFETY_GATE_FAILURE, events)


def execute_paper_order_simulation(
    data: PaperTradingRuntimeInput | Mapping[str, Any],
    decision: PaperRuntimeDecision | None = None,
    safety_gate: PaperTradingRuntimeStep | None = None,
) -> tuple[PaperTradingRuntimeStep, PaperRuntimeOrder | None]:
    data = _coerce_input(data)
    if decision is None:
        _, decision = execute_decision_cycle(data)
    safety_gate = safety_gate or execute_safety_gate(data, decision)
    passed = decision is not None and safety_gate.passed and data.paper_order_not_routed is True and not data.force_order_failure
    order = None
    if passed:
        order = PaperRuntimeOrder(f"{data.session_id}-order-1", decision.symbol, decision.action, decision.quantity, float(data.market_price or 0.0), "FILLED", routed=False)
    events = (f"order_created={order is not None}", "broker_routed=False", f"forced_failure={data.force_order_failure}")
    return _step("paper_order_simulation", passed, 100 if passed else 0, PaperTradingRuntimeRisk.PAPER_ORDER_SIMULATION_FAILURE, events), order


def update_paper_position_and_pnl(
    data: PaperTradingRuntimeInput | Mapping[str, Any],
    order: PaperRuntimeOrder | None = None,
) -> tuple[PaperTradingRuntimeStep, PaperRuntimePosition | None]:
    data = _coerce_input(data)
    if order is None:
        _, decision = execute_decision_cycle(data)
        safety = execute_safety_gate(data, decision)
        _, order = execute_paper_order_simulation(data, decision, safety)
    passed = order is not None and order.status == "FILLED" and not data.force_position_failure
    position = None
    if passed:
        signed_qty = order.quantity if order.side == "BUY" else -order.quantity
        quantity = float(data.initial_position + signed_qty)
        cash_delta = -order.price * order.quantity if order.side == "BUY" else order.price * order.quantity
        cash = float(data.initial_cash + cash_delta)
        unrealized = round((float(data.market_price or order.price) - order.price) * quantity, 6)
        position = PaperRuntimePosition(order.symbol, quantity, order.price, cash, 0.0, unrealized)
    events = (f"position_updated={position is not None}", f"cash={position.cash if position else 'n/a'}")
    return _step("position_pnl_update", passed, 100 if passed else 0, PaperTradingRuntimeRisk.POSITION_PNL_UPDATE_FAILURE, events), position


def write_runtime_journal(
    data: PaperTradingRuntimeInput | Mapping[str, Any],
    order: PaperRuntimeOrder | None = None,
    position: PaperRuntimePosition | None = None,
) -> tuple[PaperTradingRuntimeStep, tuple[str, ...]]:
    data = _coerce_input(data)
    passed = data.journal_enabled is True and order is not None and position is not None and not data.force_journal_failure
    entries = ()
    if passed:
        entries = (
            f"session={data.session_id}",
            f"order={order.order_id}:{order.side}:{order.quantity}@{order.price}:routed={order.routed}",
            f"position={position.symbol}:{position.quantity}:cash={position.cash}:upnl={position.unrealized_pnl}",
        )
    events = (f"journal_enabled={data.journal_enabled}", f"journal_entries={len(entries)}")
    return _step("runtime_journal", passed, 100 if passed else _bool_score(data.journal_enabled), PaperTradingRuntimeRisk.JOURNAL_WRITE_FAILURE, events), entries


def emit_runtime_observability_events(
    data: PaperTradingRuntimeInput | Mapping[str, Any],
    journal_entries: tuple[str, ...] = (),
) -> tuple[PaperTradingRuntimeStep, tuple[str, ...]]:
    data = _coerce_input(data)
    passed = data.observability_enabled is True and bool(journal_entries) and not data.force_observability_failure
    events = ()
    if passed:
        events = (
            f"runtime.started:{data.session_id}",
            "runtime.market_cycle.completed",
            "runtime.order_simulation.completed",
            "runtime.position_pnl.completed",
            "runtime.journal.completed",
        )
    step_events = (f"observability_enabled={data.observability_enabled}", f"events={len(events)}")
    return _step("runtime_observability", passed, 100 if passed else _bool_score(data.observability_enabled), PaperTradingRuntimeRisk.OBSERVABILITY_EMIT_FAILURE, step_events), events


def check_runtime_rollback_hook(data: PaperTradingRuntimeInput | Mapping[str, Any]) -> PaperTradingRuntimeStep:
    data = _coerce_input(data)
    passed = data.rollback_hook_available is True
    if data.rollback_requested and not passed:
        score = 0
    else:
        score = _bool_score(data.rollback_hook_available)
    events = (f"rollback_requested={data.rollback_requested}", f"rollback_hook_available={data.rollback_hook_available}")
    return _step("rollback_hook", passed, score, PaperTradingRuntimeRisk.ROLLBACK_HOOK_FAILURE, events)


def check_runtime_kill_switch_hook(data: PaperTradingRuntimeInput | Mapping[str, Any]) -> PaperTradingRuntimeStep:
    data = _coerce_input(data)
    passed = data.kill_switch_hook_available is True
    if data.kill_switch_triggered and not passed:
        score = 0
    else:
        score = _bool_score(data.kill_switch_hook_available)
    events = (f"kill_switch_triggered={data.kill_switch_triggered}", f"kill_switch_hook_available={data.kill_switch_hook_available}")
    return _step("kill_switch_hook", passed, score, PaperTradingRuntimeRisk.KILL_SWITCH_HOOK_FAILURE, events)


def check_human_supervision_hook(data: PaperTradingRuntimeInput | Mapping[str, Any]) -> PaperTradingRuntimeStep:
    data = _coerce_input(data)
    passed = data.approved_by_human is True and data.operator_confirmed is True and data.session_authorized is True
    score = _average((_bool_score(data.approved_by_human), _bool_score(data.operator_confirmed), _bool_score(data.session_authorized)))
    events = (
        f"approved_by_human={data.approved_by_human}",
        f"operator_confirmed={data.operator_confirmed}",
        f"session_authorized={data.session_authorized}",
        f"supervision_pause_requested={data.supervision_pause_requested}",
    )
    state = PaperTradingRuntimeState.PAUSED_BY_SUPERVISION if data.supervision_pause_requested else PaperTradingRuntimeState.RUNNING
    return _step("human_supervision_hook", passed and not data.supervision_pause_requested, score, PaperTradingRuntimeRisk.HUMAN_SUPERVISION_FAILURE, events, state)


def _collect_risks(steps: tuple[PaperTradingRuntimeStep, ...], data: PaperTradingRuntimeInput) -> tuple[PaperTradingRuntimeRisk, ...]:
    risks: list[PaperTradingRuntimeRisk] = []
    for step in steps:
        risks.extend(step.risks)
    if not _offline_boundary(data):
        risks.append(PaperTradingRuntimeRisk.RUNTIME_STATE_DRIFT)
    if _has_upstream_risk(data, "DRIFT", "STATE_CORRUPTION", "INCONSISTENCY"):
        risks.append(PaperTradingRuntimeRisk.RUNTIME_STATE_DRIFT)
    return _dedupe(risks)


def _runtime_score(steps: tuple[PaperTradingRuntimeStep, ...], risks: tuple[PaperTradingRuntimeRisk, ...]) -> int:
    base = _average(step.score for step in steps)
    score = _clamp(base - min(75, len(set(risks)) * 6))
    caps = {
        PaperTradingRuntimeRisk.RUNTIME_INITIALIZATION_FAILURE: 35,
        PaperTradingRuntimeRisk.SAFETY_GATE_FAILURE: 45,
        PaperTradingRuntimeRisk.PAPER_ORDER_SIMULATION_FAILURE: 45,
        PaperTradingRuntimeRisk.KILL_SWITCH_HOOK_FAILURE: 50,
        PaperTradingRuntimeRisk.ROLLBACK_HOOK_FAILURE: 50,
        PaperTradingRuntimeRisk.HUMAN_SUPERVISION_FAILURE: 50,
        PaperTradingRuntimeRisk.RUNTIME_STATE_DRIFT: 40,
    }
    for risk, cap in caps.items():
        if risk in risks:
            score = min(score, cap)
    return score


def _select_state(data: PaperTradingRuntimeInput, risks: tuple[PaperTradingRuntimeRisk, ...], score: int) -> PaperTradingRuntimeState:
    if data.kill_switch_triggered:
        return PaperTradingRuntimeState.STOPPED_BY_KILL_SWITCH
    if data.rollback_requested:
        return PaperTradingRuntimeState.STOPPED_BY_ROLLBACK
    if data.supervision_pause_requested:
        return PaperTradingRuntimeState.PAUSED_BY_SUPERVISION
    if risks or score < 85:
        return PaperTradingRuntimeState.FAILED_SAFE
    return PaperTradingRuntimeState.COMPLETED


def _recommendations(risks: tuple[PaperTradingRuntimeRisk, ...], state: PaperTradingRuntimeState) -> tuple[PaperTradingRuntimeRecommendation, ...]:
    recommendations: list[PaperTradingRuntimeRecommendation] = []
    if risks:
        recommendations.append(PaperTradingRuntimeRecommendation.HOLD_RUNTIME_APPROVAL)
    mapping = {
        PaperTradingRuntimeRisk.RUNTIME_INITIALIZATION_FAILURE: PaperTradingRuntimeRecommendation.REPAIR_RUNTIME_INITIALIZATION,
        PaperTradingRuntimeRisk.MARKET_CYCLE_FAILURE: PaperTradingRuntimeRecommendation.REPAIR_MARKET_CYCLE,
        PaperTradingRuntimeRisk.SIGNAL_CYCLE_FAILURE: PaperTradingRuntimeRecommendation.REPAIR_SIGNAL_CYCLE,
        PaperTradingRuntimeRisk.DECISION_CYCLE_FAILURE: PaperTradingRuntimeRecommendation.REPAIR_DECISION_CYCLE,
        PaperTradingRuntimeRisk.SAFETY_GATE_FAILURE: PaperTradingRuntimeRecommendation.REPAIR_SAFETY_GATE,
        PaperTradingRuntimeRisk.PAPER_ORDER_SIMULATION_FAILURE: PaperTradingRuntimeRecommendation.REPAIR_PAPER_ORDER_SIMULATION,
        PaperTradingRuntimeRisk.POSITION_PNL_UPDATE_FAILURE: PaperTradingRuntimeRecommendation.REPAIR_POSITION_PNL_UPDATE,
        PaperTradingRuntimeRisk.JOURNAL_WRITE_FAILURE: PaperTradingRuntimeRecommendation.REPAIR_RUNTIME_JOURNAL,
        PaperTradingRuntimeRisk.OBSERVABILITY_EMIT_FAILURE: PaperTradingRuntimeRecommendation.REPAIR_RUNTIME_OBSERVABILITY,
        PaperTradingRuntimeRisk.ROLLBACK_HOOK_FAILURE: PaperTradingRuntimeRecommendation.REPAIR_ROLLBACK_HOOK,
        PaperTradingRuntimeRisk.KILL_SWITCH_HOOK_FAILURE: PaperTradingRuntimeRecommendation.REPAIR_KILL_SWITCH_HOOK,
        PaperTradingRuntimeRisk.HUMAN_SUPERVISION_FAILURE: PaperTradingRuntimeRecommendation.REPAIR_HUMAN_SUPERVISION_HOOK,
        PaperTradingRuntimeRisk.RUNTIME_STATE_DRIFT: PaperTradingRuntimeRecommendation.RECONCILE_RUNTIME_STATE,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(PaperTradingRuntimeRecommendation.RUN_PAPER_RUNTIME_SUITE)
    if state == PaperTradingRuntimeState.COMPLETED:
        recommendations.append(PaperTradingRuntimeRecommendation.APPROVE_RUNTIME_AFTER_MANUAL_REVIEW)
    return _dedupe(recommendations)


def build_runtime_report(
    data: PaperTradingRuntimeInput | Mapping[str, Any],
    state: PaperTradingRuntimeState,
    score: int,
    risks: tuple[PaperTradingRuntimeRisk, ...],
    steps: tuple[PaperTradingRuntimeStep, ...],
    journal_entries: tuple[str, ...] = (),
    observability_events: tuple[str, ...] = (),
) -> PaperTradingRuntimeReport:
    data = _coerce_input(data)
    events: list[str] = []
    for step in steps:
        events.extend(step.events)
    return PaperTradingRuntimeReport(
        session_id=data.session_id,
        state=state,
        score=score,
        risks=risks,
        events=tuple(events),
        order_count=1 if any(step.name == "paper_order_simulation" and step.passed for step in steps) else 0,
        journal_count=len(journal_entries),
        observability_count=len(observability_events),
    )


def stop_paper_trading_runtime(
    data: PaperTradingRuntimeInput | Mapping[str, Any],
    state: PaperTradingRuntimeState = PaperTradingRuntimeState.COMPLETED,
) -> PaperTradingRuntimeStep:
    data = _coerce_input(data)
    passed = state in {
        PaperTradingRuntimeState.COMPLETED,
        PaperTradingRuntimeState.STOPPED_BY_KILL_SWITCH,
        PaperTradingRuntimeState.STOPPED_BY_ROLLBACK,
        PaperTradingRuntimeState.PAUSED_BY_SUPERVISION,
        PaperTradingRuntimeState.FAILED_SAFE,
    }
    events = (f"session_id={data.session_id}", f"final_state={state.value}", "runtime_stopped=True")
    return _step("runtime_stop", passed, 100 if passed else 0, None if passed else PaperTradingRuntimeRisk.RUNTIME_STATE_DRIFT, events, state)


def run_paper_trading_runtime(data: PaperTradingRuntimeInput | Mapping[str, Any]) -> PaperTradingRuntimeResult:
    data = _coerce_input(data)
    session = initialize_paper_runtime_session(data)
    market_step, market = execute_market_cycle(data) if session.passed else (_step("market_cycle", False, 0, PaperTradingRuntimeRisk.MARKET_CYCLE_FAILURE), None)
    signal_step, signal = execute_signal_cycle(data, market) if market_step.passed else (_step("signal_cycle", False, 0, PaperTradingRuntimeRisk.SIGNAL_CYCLE_FAILURE), None)
    decision_step, decision = execute_decision_cycle(data, signal) if signal_step.passed else (_step("decision_cycle", False, 0, PaperTradingRuntimeRisk.DECISION_CYCLE_FAILURE), None)
    safety = execute_safety_gate(data, decision) if decision_step.passed else _step("safety_gate", False, 0, PaperTradingRuntimeRisk.SAFETY_GATE_FAILURE)
    order_step, order = execute_paper_order_simulation(data, decision, safety) if safety.passed else (_step("paper_order_simulation", False, 0, PaperTradingRuntimeRisk.PAPER_ORDER_SIMULATION_FAILURE), None)
    position_step, position = update_paper_position_and_pnl(data, order) if order_step.passed else (_step("position_pnl_update", False, 0, PaperTradingRuntimeRisk.POSITION_PNL_UPDATE_FAILURE), None)
    journal_step, journal_entries = write_runtime_journal(data, order, position) if position_step.passed else (_step("runtime_journal", False, 0, PaperTradingRuntimeRisk.JOURNAL_WRITE_FAILURE), ())
    observability_step, observability_events = emit_runtime_observability_events(data, journal_entries) if journal_step.passed else (_step("runtime_observability", False, 0, PaperTradingRuntimeRisk.OBSERVABILITY_EMIT_FAILURE), ())
    rollback = check_runtime_rollback_hook(data)
    kill_switch = check_runtime_kill_switch_hook(data)
    human = check_human_supervision_hook(data)
    steps = (session, market_step, signal_step, decision_step, safety, order_step, position_step, journal_step, observability_step, rollback, kill_switch, human)
    risks = _collect_risks(steps, data)
    score = _runtime_score(steps, risks)
    state = _select_state(data, risks, score)
    stop = stop_paper_trading_runtime(data, state)
    steps_with_stop = steps + (stop,)
    report = build_runtime_report(data, state, score, risks, steps_with_stop, journal_entries, observability_events)
    recommendations = _recommendations(risks, state)
    offline_only = _offline_boundary(data)
    summary = f"{state.value}: score={score}, risks={len(risks)}, offline_only={offline_only}, orders={report.order_count}"
    return PaperTradingRuntimeResult(
        state=state,
        runtime_score=score,
        risks=risks,
        recommendations=recommendations,
        session=session,
        market_cycle=market_step,
        signal_cycle=signal_step,
        decision_cycle=decision_step,
        safety_gate=safety,
        paper_order_simulation=order_step,
        position_pnl_update=position_step,
        journal=journal_step,
        observability=observability_step,
        rollback_hook=rollback,
        kill_switch_hook=kill_switch,
        human_supervision_hook=human,
        stop=stop,
        market_snapshot=market,
        signal=signal,
        decision=decision,
        order=order,
        position=position,
        journal_entries=journal_entries,
        observability_events=observability_events,
        report=report,
        offline_only=offline_only,
        summary=summary,
    )


def render_paper_trading_runtime_markdown(result: PaperTradingRuntimeResult) -> str:
    lines = [
        "# AGIcore Paper Trading Runtime",
        f"- State: {result.state.value}",
        f"- Score: {result.runtime_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Runtime Steps",
    ]
    steps = (
        result.session,
        result.market_cycle,
        result.signal_cycle,
        result.decision_cycle,
        result.safety_gate,
        result.paper_order_simulation,
        result.position_pnl_update,
        result.journal,
        result.observability,
        result.rollback_hook,
        result.kill_switch_hook,
        result.human_supervision_hook,
        result.stop,
    )
    for step in steps:
        lines.append(f"- {step.name}: passed={step.passed}, state={step.state.value}, score={step.score}/100, risks={', '.join(risk.value for risk in step.risks) or 'none'}")
        lines.extend(f"  - {event}" for event in step.events)
    lines.extend(("", "# Runtime Artifacts"))
    if result.order is not None:
        lines.append(f"- Order: {result.order.order_id}, {result.order.side}, routed={result.order.routed}, status={result.order.status}")
    if result.position is not None:
        lines.append(f"- Position: {result.position.symbol}, qty={result.position.quantity}, cash={result.position.cash}, upnl={result.position.unrealized_pnl}")
    lines.extend((f"- Journal entries: {len(result.journal_entries)}", f"- Observability events: {len(result.observability_events)}", "", "# Runtime Risks"))
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Runtime Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "build_runtime_report",
    "check_human_supervision_hook",
    "check_runtime_kill_switch_hook",
    "check_runtime_rollback_hook",
    "emit_runtime_observability_events",
    "execute_decision_cycle",
    "execute_market_cycle",
    "execute_paper_order_simulation",
    "execute_safety_gate",
    "execute_signal_cycle",
    "initialize_paper_runtime_session",
    "render_paper_trading_runtime_markdown",
    "run_paper_trading_runtime",
    "stop_paper_trading_runtime",
    "update_paper_position_and_pnl",
    "write_runtime_journal",
]
