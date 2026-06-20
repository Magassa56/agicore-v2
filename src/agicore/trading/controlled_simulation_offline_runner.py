"""Deterministic in-memory controlled simulation offline runner for AGIcore."""

from __future__ import annotations

import math
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.controlled_simulation_offline_runner_models import (
    ControlledSimulationOfflineRunnerDecision,
    ControlledSimulationOfflineRunnerInput,
    ControlledSimulationOfflineRunnerRecommendation,
    ControlledSimulationOfflineRunnerResult,
    ControlledSimulationOfflineRunnerRisk,
    ControlledSimulationOfflineRunnerScore,
    ControlledSimulationOfflineRunnerState,
    OfflineEquityPoint,
    OfflinePositionState,
    OfflineSignalEvent,
    OfflineSimulatedDecision,
    OfflineSimulatedFill,
    OfflineSimulationMetrics,
    OfflineSimulationStepLog,
    OfflineStopConditionResult,
    OfflineSyntheticMarketBar,
)


_ACTIONS = {"BUY", "SELL", "HOLD"}


def _coerce_input(data: ControlledSimulationOfflineRunnerInput | Mapping[str, Any]) -> ControlledSimulationOfflineRunnerInput:
    if isinstance(data, ControlledSimulationOfflineRunnerInput):
        return data
    allowed = {field.name for field in fields(ControlledSimulationOfflineRunnerInput)}
    payload = {key: value for key, value in dict(data).items() if key in allowed}
    return ControlledSimulationOfflineRunnerInput(**payload)


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


def _finite(value: Any) -> bool:
    return isinstance(value, int | float) and math.isfinite(float(value))


def _round(value: float, digits: int = 10) -> float:
    return round(float(value), digits)


def _upstream_items(data: ControlledSimulationOfflineRunnerInput) -> tuple[Any, ...]:
    return (
        data.controlled_simulation_review_precheck,
        data.paper_broker_sandbox_dry_run_controlled_simulation_plan,
        data.paper_broker_sandbox_dry_run_execution_authorization_gate,
        data.paper_broker_sandbox_dry_run_execution_review,
        data.paper_broker_sandbox_dry_run_pre_execution_check,
        data.paper_broker_sandbox_dry_run_review,
        data.paper_broker_sandbox_dry_run_plan,
        data.paper_runtime_forward_test_plan,
        data.supervised_paper_runtime_trial,
        data.official_paper_validation_report,
        data.paper_runtime_validation,
        data.paper_trading_runtime,
        data.observability_verification,
        data.rollback_verification,
        data.kill_switch_verification,
        data.human_validated_paper_session,
        data.supervised_paper_session,
    )


def _upstream_risks(data: ControlledSimulationOfflineRunnerInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: ControlledSimulationOfflineRunnerInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _offline_boundary(data: ControlledSimulationOfflineRunnerInput) -> bool:
    return (
        data.offline_mode_enforced is True
        and data.sandbox_mode_enforced is True
        and data.no_real_broker is True
        and data.no_alpaca_real is True
        and data.no_api_key_read is True
        and data.no_http_transport is True
        and data.no_websocket_transport is True
        and data.no_socket_transport is True
        and data.no_external_api is True
        and data.no_external_ml is True
        and data.no_external_llm is True
        and data.no_live_execution is True
        and data.no_real_order is True
        and data.no_real_account_access is True
        and data.real_execution_requested is not True
        and all(_get(item, "offline_only", True) is True for item in _upstream_items(data))
        and not _has_upstream_risk(
            data,
            "LIVE_EXECUTION",
            "API_ACCESS",
            "NETWORK_LEAK",
            "BROKER_CONNECTIVITY",
            "EXTERNAL_DEPENDENCY",
            "HTTP",
            "WEBSOCKET",
            "SOCKET",
            "REAL_ORDER",
            "REAL_ACCOUNT",
            "REAL_EXECUTION",
            "API_KEY",
            "CREDENTIAL",
        )
    )


def _data_boundary(data: ControlledSimulationOfflineRunnerInput) -> bool:
    return (
        data.synthetic_data_only is True
        and data.in_memory_only is True
        and data.data_access_requested is not True
        and not _has_upstream_risk(data, "DATA_ACCESS", "DATA_ACCESS_VIOLATION", "REAL_DATA")
    )


def validate_controlled_simulation_review_precheck(
    data: ControlledSimulationOfflineRunnerInput | Mapping[str, Any],
) -> bool:
    data = _coerce_input(data)
    precheck = data.controlled_simulation_review_precheck
    precheck_state_ok = _state_contains(
        precheck,
        "READY_FOR_CONTROLLED_SIMULATION_OFFLINE_RUNNER",
        "APPROVE_CONTROLLED_SIMULATION_REVIEW_PRECHECK",
    )
    explicit_ok = data.review_precheck_approved is True
    explicit_rejected = data.review_precheck_approved is False
    return (
        not explicit_rejected
        and (explicit_ok or precheck_state_ok)
        and not _has_upstream_risk(
            data,
            "REVIEW_PRECHECK_NOT_APPROVED",
            "REAL_EXECUTION_BOUNDARY_VIOLATION",
            "PREMATURE_CONTROLLED_SIMULATION_OFFLINE_RUNNER",
            "BLOCK_CONTROLLED_SIMULATION",
        )
    )


def _default_market_path(symbol: str) -> tuple[OfflineSyntheticMarketBar, ...]:
    closes = (100.0, 103.0, 101.0, 106.0, 108.0)
    bars: list[OfflineSyntheticMarketBar] = []
    previous = closes[0]
    for step, close in enumerate(closes):
        open_price = previous if step else close
        high = max(open_price, close) + 0.5
        low = min(open_price, close) - 0.5
        bars.append(OfflineSyntheticMarketBar(step, symbol, open_price, high, low, close, 1_000.0, f"T{step}"))
        previous = close
    return tuple(bars)


def _coerce_bar(item: OfflineSyntheticMarketBar | Mapping[str, Any], fallback_step: int, fallback_symbol: str) -> OfflineSyntheticMarketBar:
    if isinstance(item, OfflineSyntheticMarketBar):
        return item
    payload = dict(item)
    close = float(payload.get("close", payload.get("price", 0.0)))
    open_price = float(payload.get("open", close))
    high = float(payload.get("high", max(open_price, close)))
    low = float(payload.get("low", min(open_price, close)))
    return OfflineSyntheticMarketBar(
        step=int(payload.get("step", fallback_step)),
        symbol=str(payload.get("symbol", fallback_symbol)),
        open=open_price,
        high=high,
        low=low,
        close=close,
        volume=float(payload.get("volume", 0.0)),
        timestamp=str(payload.get("timestamp", f"T{fallback_step}")),
    )


def build_offline_synthetic_market_path(
    data: ControlledSimulationOfflineRunnerInput | Mapping[str, Any],
) -> tuple[OfflineSyntheticMarketBar, ...]:
    data = _coerce_input(data)
    if data.synthetic_market_path is None:
        path = _default_market_path(data.symbol)
    else:
        path = tuple(_coerce_bar(item, index, data.symbol) for index, item in enumerate(data.synthetic_market_path))
    if data.max_steps is not None and data.max_steps >= 0:
        path = path[: data.max_steps]
    return tuple(sorted(path, key=lambda bar: bar.step))


def _coerce_signal(item: OfflineSignalEvent | Mapping[str, Any], fallback_symbol: str) -> OfflineSignalEvent:
    if isinstance(item, OfflineSignalEvent):
        return item
    payload = dict(item)
    return OfflineSignalEvent(
        step=int(payload.get("step", 0)),
        symbol=str(payload.get("symbol", fallback_symbol)),
        action=str(payload.get("action", "HOLD")).upper(),
        quantity=float(payload.get("quantity", 1.0)),
        confidence=float(payload.get("confidence", 1.0)),
        reason=str(payload.get("reason", "")),
    )


def build_offline_signal_sequence(
    data: ControlledSimulationOfflineRunnerInput | Mapping[str, Any],
    market_path: tuple[OfflineSyntheticMarketBar, ...] | None = None,
) -> tuple[OfflineSignalEvent, ...]:
    data = _coerce_input(data)
    market_path = build_offline_synthetic_market_path(data) if market_path is None else market_path
    if data.signal_sequence is None:
        if len(market_path) < 2:
            return ()
        return (
            OfflineSignalEvent(market_path[0].step, market_path[0].symbol, "BUY", 1.0, 1.0, "default_entry"),
            OfflineSignalEvent(market_path[-1].step, market_path[-1].symbol, "SELL", 1.0, 1.0, "default_exit"),
        )
    return tuple(sorted((_coerce_signal(item, data.symbol) for item in data.signal_sequence), key=lambda signal: signal.step))


def build_offline_simulation_context(
    data: ControlledSimulationOfflineRunnerInput | Mapping[str, Any],
) -> dict[str, Any]:
    data = _coerce_input(data)
    market_path = build_offline_synthetic_market_path(data)
    signal_sequence = build_offline_signal_sequence(data, market_path)
    return {
        "input": data,
        "market_path": market_path,
        "signal_sequence": signal_sequence,
    }


def _market_path_valid(market_path: tuple[OfflineSyntheticMarketBar, ...]) -> bool:
    if not market_path:
        return False
    steps = [bar.step for bar in market_path]
    if len(set(steps)) != len(steps):
        return False
    for bar in market_path:
        prices = (bar.open, bar.high, bar.low, bar.close)
        if not bar.symbol or any(not _finite(price) or price <= 0 for price in prices):
            return False
        if bar.high < max(bar.open, bar.close, bar.low) or bar.low > min(bar.open, bar.close, bar.high):
            return False
    return True


def _signal_sequence_valid(
    signal_sequence: tuple[OfflineSignalEvent, ...],
    market_path: tuple[OfflineSyntheticMarketBar, ...],
) -> bool:
    if not signal_sequence:
        return False
    valid_steps = {bar.step for bar in market_path}
    valid_symbols = {bar.symbol for bar in market_path}
    for signal in signal_sequence:
        if signal.step not in valid_steps:
            return False
        if signal.symbol not in valid_symbols:
            return False
        if signal.action.upper() not in _ACTIONS:
            return False
        if not _finite(signal.quantity) or signal.quantity < 0:
            return False
        if not _finite(signal.confidence) or not 0 <= signal.confidence <= 1:
            return False
    return True


def _risk_limits_present(data: ControlledSimulationOfflineRunnerInput) -> bool:
    return (
        data.max_steps is not None
        and data.max_order_quantity is not None
        and data.max_position_quantity is not None
        and data.max_drawdown_fraction is not None
        and data.max_loss_amount is not None
        and data.max_steps > 0
        and data.max_order_quantity > 0
        and data.max_position_quantity > 0
        and data.max_drawdown_fraction >= 0
        and data.max_loss_amount >= 0
    )


def execute_offline_simulated_decision(
    signal: OfflineSignalEvent,
    market_bar: OfflineSyntheticMarketBar,
    position: OfflinePositionState,
    data: ControlledSimulationOfflineRunnerInput | Mapping[str, Any],
) -> OfflineSimulatedDecision:
    data = _coerce_input(data)
    action = signal.action.upper()
    quantity = _round(signal.quantity)
    accepted = True
    reason = signal.reason
    if action not in _ACTIONS:
        accepted = False
        reason = "invalid_signal_action"
    elif action == "HOLD":
        quantity = 0.0
        reason = reason or "hold"
    elif quantity <= 0:
        accepted = False
        reason = "non_positive_quantity"
    elif data.max_order_quantity is not None and quantity > data.max_order_quantity:
        accepted = False
        reason = "max_order_quantity_exceeded"
    elif not _offline_boundary(data) or not _data_boundary(data):
        accepted = False
        reason = "offline_boundary_failed"
    elif action == "BUY" and data.max_position_quantity is not None and abs(position.quantity + quantity) > data.max_position_quantity:
        accepted = False
        reason = "max_position_quantity_exceeded"
    elif action == "SELL" and position.quantity <= 0:
        accepted = False
        reason = "no_position_to_sell"
    elif action == "SELL":
        quantity = min(quantity, position.quantity)
    return OfflineSimulatedDecision(signal.step, signal.symbol, action, quantity, market_bar.close, accepted, reason)


def apply_offline_simulated_fill(
    decision: OfflineSimulatedDecision,
    market_bar: OfflineSyntheticMarketBar,
    position: OfflinePositionState | None = None,
    commission_per_fill: float = 0.0,
    slippage_per_unit: float = 0.0,
) -> OfflineSimulatedFill:
    if not decision.accepted:
        return OfflineSimulatedFill(
            decision.step,
            decision.symbol,
            decision.action,
            0.0,
            market_bar.close,
            0.0,
            0.0,
            0.0,
            0.0,
            "REJECTED",
            decision.reason,
        )
    if decision.action == "HOLD" or decision.quantity == 0:
        return OfflineSimulatedFill(
            decision.step,
            decision.symbol,
            decision.action,
            0.0,
            market_bar.close,
            0.0,
            0.0,
            0.0,
            0.0,
            "SKIPPED",
            decision.reason,
        )
    slippage = abs(slippage_per_unit) * decision.quantity
    price = market_bar.close + abs(slippage_per_unit) if decision.action == "BUY" else market_bar.close - abs(slippage_per_unit)
    gross_value = price * decision.quantity
    realized_pnl = 0.0
    if decision.action == "SELL" and position is not None:
        realized_pnl = (price - position.average_price) * decision.quantity - commission_per_fill
    return OfflineSimulatedFill(
        decision.step,
        decision.symbol,
        decision.action,
        _round(decision.quantity),
        _round(price),
        _round(gross_value),
        _round(commission_per_fill),
        _round(slippage),
        _round(realized_pnl),
        "FILLED",
        decision.reason,
    )


def _mark_to_market(position: OfflinePositionState, market_bar: OfflineSyntheticMarketBar) -> OfflinePositionState:
    position_value = position.quantity * market_bar.close
    unrealized = (market_bar.close - position.average_price) * position.quantity if position.quantity else 0.0
    equity = position.cash + position_value
    return OfflinePositionState(
        position.symbol or market_bar.symbol,
        _round(position.quantity),
        _round(position.average_price if position.quantity else 0.0),
        _round(position.cash),
        _round(position.realized_pnl),
        _round(unrealized),
        _round(equity),
        position.closed_trade_pnls,
    )


def update_offline_position_state(
    position: OfflinePositionState,
    fill: OfflineSimulatedFill,
    market_bar: OfflineSyntheticMarketBar,
) -> OfflinePositionState:
    if fill.status != "FILLED":
        return _mark_to_market(position, market_bar)
    if fill.side == "BUY":
        new_quantity = position.quantity + fill.quantity
        new_average = ((position.average_price * position.quantity) + fill.gross_value) / new_quantity if new_quantity else 0.0
        cash = position.cash - fill.gross_value - fill.commission
        updated = OfflinePositionState(
            fill.symbol,
            _round(new_quantity),
            _round(new_average),
            _round(cash),
            _round(position.realized_pnl),
            0.0,
            0.0,
            position.closed_trade_pnls,
        )
        return _mark_to_market(updated, market_bar)
    if fill.side == "SELL":
        sold_quantity = min(fill.quantity, position.quantity)
        remaining_quantity = position.quantity - sold_quantity
        cash = position.cash + fill.price * sold_quantity - fill.commission
        trade_pnl = (fill.price - position.average_price) * sold_quantity - fill.commission
        realized = position.realized_pnl + trade_pnl
        updated = OfflinePositionState(
            fill.symbol,
            _round(remaining_quantity),
            _round(position.average_price if remaining_quantity else 0.0),
            _round(cash),
            _round(realized),
            0.0,
            0.0,
            position.closed_trade_pnls + (_round(trade_pnl),),
        )
        return _mark_to_market(updated, market_bar)
    return _mark_to_market(position, market_bar)


def update_offline_equity_curve(
    equity_curve: tuple[OfflineEquityPoint, ...],
    position: OfflinePositionState,
    market_bar: OfflineSyntheticMarketBar,
) -> tuple[OfflineEquityPoint, ...]:
    peak = max((point.equity for point in equity_curve), default=position.equity)
    peak = max(peak, position.equity)
    drawdown = max(0.0, peak - position.equity)
    drawdown_fraction = drawdown / peak if peak else 0.0
    point = OfflineEquityPoint(
        market_bar.step,
        market_bar.timestamp,
        _round(position.cash),
        _round(position.quantity * market_bar.close),
        _round(position.equity),
        _round(position.realized_pnl),
        _round(position.unrealized_pnl),
        _round(drawdown),
        _round(drawdown_fraction),
    )
    return equity_curve + (point,)


def execute_offline_simulation_steps(context: Mapping[str, Any]) -> dict[str, Any]:
    data = _coerce_input(context["input"])
    market_path = tuple(context["market_path"])
    signal_sequence = tuple(context["signal_sequence"])
    signal_by_step: dict[int, list[OfflineSignalEvent]] = {}
    for signal in signal_sequence:
        signal_by_step.setdefault(signal.step, []).append(signal)
    position = OfflinePositionState(data.symbol, 0.0, 0.0, data.initial_equity, 0.0, 0.0, data.initial_equity)
    decisions: list[OfflineSimulatedDecision] = []
    fills: list[OfflineSimulatedFill] = []
    equity_curve: tuple[OfflineEquityPoint, ...] = ()
    logs: list[OfflineSimulationStepLog] = []
    for bar in market_path:
        step_signals = signal_by_step.get(bar.step, (OfflineSignalEvent(bar.step, bar.symbol, "HOLD", 0.0, 1.0, "no_signal"),))
        last_decision_action = "HOLD"
        last_fill_status = "SKIPPED"
        for signal in step_signals:
            decision = execute_offline_simulated_decision(signal, bar, position, data)
            fill = apply_offline_simulated_fill(decision, bar, position, data.commission_per_fill, data.slippage_per_unit)
            position = update_offline_position_state(position, fill, bar)
            decisions.append(decision)
            fills.append(fill)
            last_decision_action = decision.action
            last_fill_status = fill.status
        position = _mark_to_market(position, bar)
        equity_curve = update_offline_equity_curve(equity_curve, position, bar)
        logs.append(
            OfflineSimulationStepLog(
                bar.step,
                bar.symbol,
                _round(bar.close),
                ",".join(signal.action for signal in step_signals),
                last_decision_action,
                last_fill_status,
                _round(position.quantity),
                _round(position.equity),
                (),
                "offline_step_completed",
            )
        )
        interim_loss = data.initial_equity - position.equity
        current_drawdown = equity_curve[-1].drawdown_fraction
        if data.max_loss_amount is not None and interim_loss >= data.max_loss_amount:
            break
        if data.max_drawdown_fraction is not None and current_drawdown >= data.max_drawdown_fraction:
            break
    return {
        "decisions": tuple(decisions),
        "fills": tuple(fills),
        "final_position": position,
        "equity_curve": equity_curve,
        "step_logs": tuple(logs),
    }


def compute_offline_simulated_pnl(
    equity_curve: tuple[OfflineEquityPoint, ...] | Iterable[OfflineEquityPoint],
    initial_equity: float,
) -> float:
    points = tuple(equity_curve)
    if not points:
        return 0.0
    return _round(points[-1].equity - initial_equity)


def compute_offline_simulated_drawdown(
    equity_curve: tuple[OfflineEquityPoint, ...] | Iterable[OfflineEquityPoint],
) -> float:
    points = tuple(equity_curve)
    if not points:
        return 0.0
    return _round(max(point.drawdown for point in points))


def _compute_offline_simulated_drawdown_fraction(
    equity_curve: tuple[OfflineEquityPoint, ...] | Iterable[OfflineEquityPoint],
) -> float:
    points = tuple(equity_curve)
    if not points:
        return 0.0
    return _round(max(point.drawdown_fraction for point in points))


def compute_offline_win_rate(trade_pnls: tuple[float, ...] | Iterable[float]) -> float:
    pnls = tuple(float(pnl) for pnl in trade_pnls)
    if not pnls:
        return 0.0
    return _round(sum(1 for pnl in pnls if pnl > 0) / len(pnls))


def compute_offline_profit_factor(trade_pnls: tuple[float, ...] | Iterable[float]) -> float:
    pnls = tuple(float(pnl) for pnl in trade_pnls)
    gross_profit = sum(pnl for pnl in pnls if pnl > 0)
    gross_loss = abs(sum(pnl for pnl in pnls if pnl < 0))
    if gross_loss == 0:
        return float("inf") if gross_profit > 0 else 0.0
    return _round(gross_profit / gross_loss)


def compute_offline_expectancy(trade_pnls: tuple[float, ...] | Iterable[float]) -> float:
    pnls = tuple(float(pnl) for pnl in trade_pnls)
    if not pnls:
        return 0.0
    return _round(sum(pnls) / len(pnls))


def _build_metrics(
    data: ControlledSimulationOfflineRunnerInput,
    final_position: OfflinePositionState,
    equity_curve: tuple[OfflineEquityPoint, ...],
) -> OfflineSimulationMetrics:
    trade_pnls = final_position.closed_trade_pnls
    pnl = compute_offline_simulated_pnl(equity_curve, data.initial_equity)
    max_drawdown = compute_offline_simulated_drawdown(equity_curve)
    max_drawdown_fraction = _compute_offline_simulated_drawdown_fraction(equity_curve)
    return OfflineSimulationMetrics(
        _round(data.initial_equity),
        _round(equity_curve[-1].equity if equity_curve else data.initial_equity),
        pnl,
        _round(final_position.realized_pnl),
        _round(final_position.unrealized_pnl),
        max_drawdown,
        max_drawdown_fraction,
        len(trade_pnls),
        sum(1 for pnl_item in trade_pnls if pnl_item > 0),
        sum(1 for pnl_item in trade_pnls if pnl_item < 0),
        compute_offline_win_rate(trade_pnls),
        compute_offline_profit_factor(trade_pnls),
        compute_offline_expectancy(trade_pnls),
    )


def detect_offline_stop_conditions(
    data: ControlledSimulationOfflineRunnerInput | Mapping[str, Any],
    metrics: OfflineSimulationMetrics,
    final_position: OfflinePositionState,
) -> OfflineStopConditionResult:
    data = _coerce_input(data)
    risks: list[ControlledSimulationOfflineRunnerRisk] = []
    reasons: list[str] = []
    if data.max_drawdown_fraction is not None and metrics.max_drawdown_fraction >= data.max_drawdown_fraction:
        risks.append(ControlledSimulationOfflineRunnerRisk.DRAWDOWN_LIMIT_BREACHED)
        reasons.append("max_drawdown_fraction_breached")
    if data.max_loss_amount is not None and metrics.total_pnl <= -abs(data.max_loss_amount):
        risks.append(ControlledSimulationOfflineRunnerRisk.LOSS_LIMIT_BREACHED)
        reasons.append("max_loss_amount_breached")
    if data.require_flat_final_position and abs(final_position.quantity) > 1e-9:
        risks.append(ControlledSimulationOfflineRunnerRisk.UNEXPECTED_OPEN_POSITION)
        reasons.append("final_position_not_flat")
    return OfflineStopConditionResult(bool(risks), _dedupe(risks), tuple(reasons))


def _metrics_valid(metrics: OfflineSimulationMetrics | None, equity_curve: tuple[OfflineEquityPoint, ...]) -> bool:
    if metrics is None or not equity_curve:
        return False
    numeric_values = (
        metrics.initial_equity,
        metrics.final_equity,
        metrics.total_pnl,
        metrics.realized_pnl,
        metrics.unrealized_pnl,
        metrics.max_drawdown,
        metrics.max_drawdown_fraction,
        metrics.win_rate,
        metrics.expectancy,
    )
    return all(_finite(value) for value in numeric_values)


def _input_risks(
    data: ControlledSimulationOfflineRunnerInput,
    market_path: tuple[OfflineSyntheticMarketBar, ...],
    signal_sequence: tuple[OfflineSignalEvent, ...],
) -> tuple[ControlledSimulationOfflineRunnerRisk, ...]:
    risks: list[ControlledSimulationOfflineRunnerRisk] = []
    if not validate_controlled_simulation_review_precheck(data):
        risks.append(ControlledSimulationOfflineRunnerRisk.REVIEW_PRECHECK_NOT_APPROVED)
    if not market_path:
        risks.append(ControlledSimulationOfflineRunnerRisk.OFFLINE_SCENARIO_EMPTY)
    if market_path and not _market_path_valid(market_path):
        risks.append(ControlledSimulationOfflineRunnerRisk.SYNTHETIC_MARKET_PATH_INVALID)
    if not _signal_sequence_valid(signal_sequence, market_path):
        risks.append(ControlledSimulationOfflineRunnerRisk.SIGNAL_SEQUENCE_INVALID)
    if not _risk_limits_present(data):
        risks.append(ControlledSimulationOfflineRunnerRisk.RISK_LIMITS_MISSING)
    if data.stop_conditions_required is not True or data.max_drawdown_fraction is None or data.max_loss_amount is None:
        risks.append(ControlledSimulationOfflineRunnerRisk.STOP_CONDITIONS_MISSING)
    if not _offline_boundary(data):
        risks.append(ControlledSimulationOfflineRunnerRisk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(ControlledSimulationOfflineRunnerRisk.DATA_ACCESS_VIOLATION)
    if data.result_report_requested is True:
        risks.append(ControlledSimulationOfflineRunnerRisk.PREMATURE_RESULT_REPORT)
    return _dedupe(risks)


def detect_offline_runner_risks(
    data: ControlledSimulationOfflineRunnerInput | Mapping[str, Any],
    market_path: tuple[OfflineSyntheticMarketBar, ...] = (),
    signal_sequence: tuple[OfflineSignalEvent, ...] = (),
    equity_curve: tuple[OfflineEquityPoint, ...] = (),
    metrics: OfflineSimulationMetrics | None = None,
    stop_conditions: OfflineStopConditionResult | None = None,
) -> tuple[ControlledSimulationOfflineRunnerRisk, ...]:
    data = _coerce_input(data)
    risks = list(_input_risks(data, market_path, signal_sequence))
    if equity_curve and any(not _finite(point.equity) or point.equity < 0 for point in equity_curve):
        risks.append(ControlledSimulationOfflineRunnerRisk.EQUITY_CURVE_INVALID)
    if metrics is not None and not _metrics_valid(metrics, equity_curve):
        risks.append(ControlledSimulationOfflineRunnerRisk.PNL_COMPUTATION_INVALID)
    if metrics is not None and not _finite(metrics.total_pnl):
        risks.append(ControlledSimulationOfflineRunnerRisk.PNL_COMPUTATION_INVALID)
    if stop_conditions is not None:
        risks.extend(stop_conditions.risks)
    return _dedupe(risks)


def _compute_runner_score(
    data: ControlledSimulationOfflineRunnerInput,
    risks: tuple[ControlledSimulationOfflineRunnerRisk, ...],
    market_path: tuple[OfflineSyntheticMarketBar, ...],
    signal_sequence: tuple[OfflineSignalEvent, ...],
    equity_curve: tuple[OfflineEquityPoint, ...],
    metrics: OfflineSimulationMetrics | None,
) -> ControlledSimulationOfflineRunnerScore:
    review_score = 100 if validate_controlled_simulation_review_precheck(data) else 0
    scenario_score = 100 if market_path and _market_path_valid(market_path) else 0
    signal_score = 100 if _signal_sequence_valid(signal_sequence, market_path) else 0
    risk_limit_score = 100 if _risk_limits_present(data) and data.stop_conditions_required is True else 0
    metric_score = 100 if _metrics_valid(metrics, equity_curve) else 0
    boundary_score = 100 if _offline_boundary(data) and _data_boundary(data) else 0
    overall = _clamp((review_score + scenario_score + signal_score + risk_limit_score + metric_score + boundary_score) / 6)
    overall = _clamp(overall - min(80, len(set(risks)) * 4))
    for risk, cap in {
        ControlledSimulationOfflineRunnerRisk.REVIEW_PRECHECK_NOT_APPROVED: 50,
        ControlledSimulationOfflineRunnerRisk.OFFLINE_SCENARIO_EMPTY: 45,
        ControlledSimulationOfflineRunnerRisk.SYNTHETIC_MARKET_PATH_INVALID: 45,
        ControlledSimulationOfflineRunnerRisk.SIGNAL_SEQUENCE_INVALID: 50,
        ControlledSimulationOfflineRunnerRisk.RISK_LIMITS_MISSING: 55,
        ControlledSimulationOfflineRunnerRisk.STOP_CONDITIONS_MISSING: 55,
        ControlledSimulationOfflineRunnerRisk.EQUITY_CURVE_INVALID: 50,
        ControlledSimulationOfflineRunnerRisk.PNL_COMPUTATION_INVALID: 50,
        ControlledSimulationOfflineRunnerRisk.DRAWDOWN_LIMIT_BREACHED: 70,
        ControlledSimulationOfflineRunnerRisk.LOSS_LIMIT_BREACHED: 70,
        ControlledSimulationOfflineRunnerRisk.UNEXPECTED_OPEN_POSITION: 75,
        ControlledSimulationOfflineRunnerRisk.REAL_EXECUTION_BOUNDARY_VIOLATION: 35,
        ControlledSimulationOfflineRunnerRisk.DATA_ACCESS_VIOLATION: 35,
        ControlledSimulationOfflineRunnerRisk.PREMATURE_RESULT_REPORT: 40,
    }.items():
        if risk in risks:
            overall = min(overall, cap)
    return ControlledSimulationOfflineRunnerScore(overall, review_score, scenario_score, signal_score, risk_limit_score, metric_score, boundary_score)


def _select_decision(
    risks: tuple[ControlledSimulationOfflineRunnerRisk, ...],
) -> ControlledSimulationOfflineRunnerDecision:
    if (
        ControlledSimulationOfflineRunnerRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in risks
        or ControlledSimulationOfflineRunnerRisk.DATA_ACCESS_VIOLATION in risks
        or ControlledSimulationOfflineRunnerRisk.PREMATURE_RESULT_REPORT in risks
    ):
        return ControlledSimulationOfflineRunnerDecision.BLOCK_CONTROLLED_SIMULATION_RUNNER
    if ControlledSimulationOfflineRunnerRisk.REVIEW_PRECHECK_NOT_APPROVED in risks:
        return ControlledSimulationOfflineRunnerDecision.REQUIRE_REVIEW_PRECHECK_FIXES
    if (
        ControlledSimulationOfflineRunnerRisk.OFFLINE_SCENARIO_EMPTY in risks
        or ControlledSimulationOfflineRunnerRisk.SYNTHETIC_MARKET_PATH_INVALID in risks
    ):
        return ControlledSimulationOfflineRunnerDecision.REQUIRE_SCENARIO_FIXES
    if ControlledSimulationOfflineRunnerRisk.SIGNAL_SEQUENCE_INVALID in risks:
        return ControlledSimulationOfflineRunnerDecision.REQUIRE_SIGNAL_FIXES
    if (
        ControlledSimulationOfflineRunnerRisk.RISK_LIMITS_MISSING in risks
        or ControlledSimulationOfflineRunnerRisk.STOP_CONDITIONS_MISSING in risks
        or ControlledSimulationOfflineRunnerRisk.DRAWDOWN_LIMIT_BREACHED in risks
        or ControlledSimulationOfflineRunnerRisk.LOSS_LIMIT_BREACHED in risks
        or ControlledSimulationOfflineRunnerRisk.UNEXPECTED_OPEN_POSITION in risks
    ):
        return ControlledSimulationOfflineRunnerDecision.REQUIRE_RISK_LIMIT_FIXES
    if (
        ControlledSimulationOfflineRunnerRisk.EQUITY_CURVE_INVALID in risks
        or ControlledSimulationOfflineRunnerRisk.PNL_COMPUTATION_INVALID in risks
    ):
        return ControlledSimulationOfflineRunnerDecision.REQUIRE_METRIC_FIXES
    return ControlledSimulationOfflineRunnerDecision.APPROVE_CONTROLLED_SIMULATION_OFFLINE_RUNNER


def _select_state(
    decision: ControlledSimulationOfflineRunnerDecision,
    risks: tuple[ControlledSimulationOfflineRunnerRisk, ...],
    score: int,
) -> ControlledSimulationOfflineRunnerState:
    if decision == ControlledSimulationOfflineRunnerDecision.BLOCK_CONTROLLED_SIMULATION_RUNNER:
        return ControlledSimulationOfflineRunnerState.RUNNER_BLOCKED
    if decision in {
        ControlledSimulationOfflineRunnerDecision.REQUIRE_REVIEW_PRECHECK_FIXES,
        ControlledSimulationOfflineRunnerDecision.REQUIRE_SCENARIO_FIXES,
        ControlledSimulationOfflineRunnerDecision.REQUIRE_SIGNAL_FIXES,
        ControlledSimulationOfflineRunnerDecision.REQUIRE_RISK_LIMIT_FIXES,
    } and (
        ControlledSimulationOfflineRunnerRisk.DRAWDOWN_LIMIT_BREACHED not in risks
        and ControlledSimulationOfflineRunnerRisk.LOSS_LIMIT_BREACHED not in risks
        and ControlledSimulationOfflineRunnerRisk.UNEXPECTED_OPEN_POSITION not in risks
    ):
        return ControlledSimulationOfflineRunnerState.RUNNER_INPUT_INVALID
    if decision == ControlledSimulationOfflineRunnerDecision.REQUIRE_METRIC_FIXES:
        return ControlledSimulationOfflineRunnerState.RUNNER_BLOCKED
    if risks:
        return ControlledSimulationOfflineRunnerState.RUNNER_COMPLETED_WITH_WARNINGS
    if score >= 95:
        return ControlledSimulationOfflineRunnerState.READY_FOR_CONTROLLED_SIMULATION_RESULT_REPORT
    return ControlledSimulationOfflineRunnerState.RUNNER_COMPLETED


def generate_offline_runner_recommendations(
    risks: tuple[ControlledSimulationOfflineRunnerRisk, ...],
    decision: ControlledSimulationOfflineRunnerDecision | None = None,
) -> tuple[ControlledSimulationOfflineRunnerRecommendation, ...]:
    recommendations: list[ControlledSimulationOfflineRunnerRecommendation] = []
    if risks:
        recommendations.append(ControlledSimulationOfflineRunnerRecommendation.HOLD_CONTROLLED_SIMULATION_RESULT_REPORT)
    mapping = {
        ControlledSimulationOfflineRunnerRisk.REVIEW_PRECHECK_NOT_APPROVED: ControlledSimulationOfflineRunnerRecommendation.APPROVE_REVIEW_PRECHECK_FIRST,
        ControlledSimulationOfflineRunnerRisk.OFFLINE_SCENARIO_EMPTY: ControlledSimulationOfflineRunnerRecommendation.PROVIDE_SYNTHETIC_SCENARIO,
        ControlledSimulationOfflineRunnerRisk.SYNTHETIC_MARKET_PATH_INVALID: ControlledSimulationOfflineRunnerRecommendation.FIX_SYNTHETIC_MARKET_PATH,
        ControlledSimulationOfflineRunnerRisk.SIGNAL_SEQUENCE_INVALID: ControlledSimulationOfflineRunnerRecommendation.FIX_SIGNAL_SEQUENCE,
        ControlledSimulationOfflineRunnerRisk.RISK_LIMITS_MISSING: ControlledSimulationOfflineRunnerRecommendation.DEFINE_RISK_LIMITS,
        ControlledSimulationOfflineRunnerRisk.STOP_CONDITIONS_MISSING: ControlledSimulationOfflineRunnerRecommendation.DEFINE_STOP_CONDITIONS,
        ControlledSimulationOfflineRunnerRisk.EQUITY_CURVE_INVALID: ControlledSimulationOfflineRunnerRecommendation.REBUILD_EQUITY_CURVE,
        ControlledSimulationOfflineRunnerRisk.PNL_COMPUTATION_INVALID: ControlledSimulationOfflineRunnerRecommendation.RECHECK_PNL_COMPUTATION,
        ControlledSimulationOfflineRunnerRisk.DRAWDOWN_LIMIT_BREACHED: ControlledSimulationOfflineRunnerRecommendation.REDUCE_DRAWDOWN_EXPOSURE,
        ControlledSimulationOfflineRunnerRisk.LOSS_LIMIT_BREACHED: ControlledSimulationOfflineRunnerRecommendation.REDUCE_LOSS_EXPOSURE,
        ControlledSimulationOfflineRunnerRisk.UNEXPECTED_OPEN_POSITION: ControlledSimulationOfflineRunnerRecommendation.CLOSE_FINAL_POSITION,
        ControlledSimulationOfflineRunnerRisk.REAL_EXECUTION_BOUNDARY_VIOLATION: ControlledSimulationOfflineRunnerRecommendation.RESTORE_OFFLINE_REAL_EXECUTION_BOUNDARIES,
        ControlledSimulationOfflineRunnerRisk.DATA_ACCESS_VIOLATION: ControlledSimulationOfflineRunnerRecommendation.REMOVE_DATA_ACCESS,
        ControlledSimulationOfflineRunnerRisk.PREMATURE_RESULT_REPORT: ControlledSimulationOfflineRunnerRecommendation.DELAY_CONTROLLED_SIMULATION_RESULT_REPORT,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(ControlledSimulationOfflineRunnerRecommendation.RUN_CONTROLLED_SIMULATION_OFFLINE_RUNNER_SUITE)
    if decision == ControlledSimulationOfflineRunnerDecision.APPROVE_CONTROLLED_SIMULATION_OFFLINE_RUNNER:
        recommendations.append(ControlledSimulationOfflineRunnerRecommendation.APPROVE_CONTROLLED_SIMULATION_RESULT_REPORT)
    return _dedupe(recommendations)


def run_controlled_simulation_offline_runner(
    data: ControlledSimulationOfflineRunnerInput | Mapping[str, Any],
) -> ControlledSimulationOfflineRunnerResult:
    data = _coerce_input(data)
    context = build_offline_simulation_context(data)
    market_path = tuple(context["market_path"])
    signal_sequence = tuple(context["signal_sequence"])
    input_risks = _input_risks(data, market_path, signal_sequence)
    blocking_input_risks = {
        ControlledSimulationOfflineRunnerRisk.REVIEW_PRECHECK_NOT_APPROVED,
        ControlledSimulationOfflineRunnerRisk.OFFLINE_SCENARIO_EMPTY,
        ControlledSimulationOfflineRunnerRisk.SYNTHETIC_MARKET_PATH_INVALID,
        ControlledSimulationOfflineRunnerRisk.SIGNAL_SEQUENCE_INVALID,
        ControlledSimulationOfflineRunnerRisk.RISK_LIMITS_MISSING,
        ControlledSimulationOfflineRunnerRisk.STOP_CONDITIONS_MISSING,
        ControlledSimulationOfflineRunnerRisk.REAL_EXECUTION_BOUNDARY_VIOLATION,
        ControlledSimulationOfflineRunnerRisk.DATA_ACCESS_VIOLATION,
        ControlledSimulationOfflineRunnerRisk.PREMATURE_RESULT_REPORT,
    }
    if any(risk in input_risks for risk in blocking_input_risks):
        metrics = OfflineSimulationMetrics(data.initial_equity, data.initial_equity, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0, 0.0, 0.0, 0.0)
        final_position = OfflinePositionState(data.symbol, 0.0, 0.0, data.initial_equity, 0.0, 0.0, data.initial_equity)
        stop_conditions = OfflineStopConditionResult(False)
        risks = input_risks
        score = _compute_runner_score(data, risks, market_path, signal_sequence, (), metrics)
        decision = _select_decision(risks)
        state = _select_state(decision, risks, score.overall_score)
        recommendations = generate_offline_runner_recommendations(risks, decision)
        summary = f"{state.value}: decision={decision.value}, score={score.overall_score}, risks={len(risks)}, pnl=0.0"
        return ControlledSimulationOfflineRunnerResult(
            state,
            decision,
            score.overall_score,
            score,
            risks,
            recommendations,
            market_path,
            signal_sequence,
            (),
            (),
            final_position,
            (),
            (),
            metrics,
            stop_conditions,
            _offline_boundary(data) and _data_boundary(data),
            summary,
        )
    execution = execute_offline_simulation_steps(context)
    decisions = tuple(execution["decisions"])
    fills = tuple(execution["fills"])
    final_position = execution["final_position"]
    equity_curve = tuple(execution["equity_curve"])
    step_logs = tuple(execution["step_logs"])
    metrics = _build_metrics(data, final_position, equity_curve)
    stop_conditions = detect_offline_stop_conditions(data, metrics, final_position)
    risks = detect_offline_runner_risks(data, market_path, signal_sequence, equity_curve, metrics, stop_conditions)
    score = _compute_runner_score(data, risks, market_path, signal_sequence, equity_curve, metrics)
    decision = _select_decision(risks)
    state = _select_state(decision, risks, score.overall_score)
    recommendations = generate_offline_runner_recommendations(risks, decision)
    summary = f"{state.value}: decision={decision.value}, score={score.overall_score}, risks={len(risks)}, pnl={metrics.total_pnl}"
    return ControlledSimulationOfflineRunnerResult(
        state,
        decision,
        score.overall_score,
        score,
        risks,
        recommendations,
        market_path,
        signal_sequence,
        decisions,
        fills,
        final_position,
        equity_curve,
        step_logs,
        metrics,
        stop_conditions,
        _offline_boundary(data) and _data_boundary(data),
        summary,
    )


def render_controlled_simulation_offline_runner_markdown(
    result: ControlledSimulationOfflineRunnerResult,
) -> str:
    lines = [
        "# AGIcore Controlled Simulation Offline Runner",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Score: {result.runner_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Metrics",
        f"- Initial equity: {result.metrics.initial_equity}",
        f"- Final equity: {result.metrics.final_equity}",
        f"- Total PnL: {result.metrics.total_pnl}",
        f"- Realized PnL: {result.metrics.realized_pnl}",
        f"- Unrealized PnL: {result.metrics.unrealized_pnl}",
        f"- Max drawdown: {result.metrics.max_drawdown}",
        f"- Max drawdown fraction: {result.metrics.max_drawdown_fraction}",
        f"- Win rate: {result.metrics.win_rate}",
        f"- Profit factor: {result.metrics.profit_factor}",
        f"- Expectancy: {result.metrics.expectancy}",
        "",
        "# Final Position",
        f"- Symbol: {result.final_position.symbol}",
        f"- Quantity: {result.final_position.quantity}",
        f"- Average price: {result.final_position.average_price}",
        f"- Equity: {result.final_position.equity}",
        "",
        "# Stop Conditions",
    ]
    if result.stop_conditions.risks:
        lines.extend(f"- {risk.value}" for risk in result.stop_conditions.risks)
    else:
        lines.append("- none")
    lines.append("")
    lines.append("# Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    lines.append("")
    lines.append("# Step Logs")
    for log in result.step_logs:
        lines.append(
            f"- step={log.step}, symbol={log.symbol}, price={log.price}, signal={log.signal_action}, "
            f"decision={log.decision_action}, fill={log.fill_status}, equity={log.equity}"
        )
    return "\n".join(lines)


__all__ = [
    "apply_offline_simulated_fill",
    "build_offline_signal_sequence",
    "build_offline_simulation_context",
    "build_offline_synthetic_market_path",
    "compute_offline_expectancy",
    "compute_offline_profit_factor",
    "compute_offline_simulated_drawdown",
    "compute_offline_simulated_pnl",
    "compute_offline_win_rate",
    "detect_offline_runner_risks",
    "detect_offline_stop_conditions",
    "execute_offline_simulated_decision",
    "execute_offline_simulation_steps",
    "generate_offline_runner_recommendations",
    "render_controlled_simulation_offline_runner_markdown",
    "run_controlled_simulation_offline_runner",
    "update_offline_equity_curve",
    "update_offline_position_state",
    "validate_controlled_simulation_review_precheck",
]
