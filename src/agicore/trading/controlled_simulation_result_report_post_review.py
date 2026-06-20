"""Offline result report and post-run review for controlled simulations."""

from __future__ import annotations

import math
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.controlled_simulation_result_report_post_review_models import (
    ControlledSimulationResultReportDecision,
    ControlledSimulationResultReportInput,
    ControlledSimulationResultReportRecommendation,
    ControlledSimulationResultReportResult,
    ControlledSimulationResultReportRisk,
    ControlledSimulationResultReportScore,
    ControlledSimulationResultReportState,
    OfflineDrawdownQualityReview,
    OfflineEquityCurveReview,
    OfflinePnLQualityReview,
    OfflinePositionConsistencyReview,
    OfflinePostRunFinding,
    OfflineSimulationMetricSummary,
)


def _coerce_input(data: ControlledSimulationResultReportInput | Mapping[str, Any]) -> ControlledSimulationResultReportInput:
    if isinstance(data, ControlledSimulationResultReportInput):
        return data
    allowed = {field.name for field in fields(ControlledSimulationResultReportInput)}
    payload = {key: value for key, value in dict(data).items() if key in allowed}
    return ControlledSimulationResultReportInput(**payload)


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


def _numeric_or_inf(value: Any) -> bool:
    return isinstance(value, int | float) and not math.isnan(float(value))


def _round(value: float, digits: int = 10) -> float:
    return round(float(value), digits)


def _close(left: float, right: float, tolerance: float) -> bool:
    return abs(float(left) - float(right)) <= max(tolerance, 0.0)


def _runner(data: ControlledSimulationResultReportInput) -> Any:
    return data.controlled_simulation_offline_runner_result


def _metrics(runner_result: Any) -> Any:
    return _get(runner_result, "metrics")


def _equity_curve(runner_result: Any) -> tuple[Any, ...]:
    return _as_tuple(_get(runner_result, "equity_curve", ()))


def _final_position(runner_result: Any) -> Any:
    return _get(runner_result, "final_position")


def _stop_conditions(runner_result: Any) -> Any:
    return _get(runner_result, "stop_conditions")


def _upstream_items(data: ControlledSimulationResultReportInput) -> tuple[Any, ...]:
    return (
        data.controlled_simulation_offline_runner_result,
        data.controlled_simulation_offline_runner_input,
        data.controlled_simulation_review_precheck,
        data.paper_broker_sandbox_dry_run_controlled_simulation_plan,
        data.paper_broker_sandbox_dry_run_execution_authorization_gate,
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


def _upstream_risks(data: ControlledSimulationResultReportInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: ControlledSimulationResultReportInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _offline_boundary(data: ControlledSimulationResultReportInput) -> bool:
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


def _data_boundary(data: ControlledSimulationResultReportInput) -> bool:
    return (
        data.synthetic_data_only is True
        and data.in_memory_only is True
        and data.data_access_requested is not True
        and not _has_upstream_risk(data, "DATA_ACCESS", "DATA_ACCESS_VIOLATION", "REAL_DATA")
    )


def _metrics_valid(metrics: Any) -> bool:
    if metrics is None:
        return False
    values = (
        _get(metrics, "initial_equity"),
        _get(metrics, "final_equity"),
        _get(metrics, "total_pnl"),
        _get(metrics, "realized_pnl"),
        _get(metrics, "unrealized_pnl"),
        _get(metrics, "max_drawdown"),
        _get(metrics, "max_drawdown_fraction"),
        _get(metrics, "win_rate"),
        _get(metrics, "expectancy"),
    )
    return all(_finite(value) for value in values) and _numeric_or_inf(_get(metrics, "profit_factor"))


def _empty_summary() -> OfflineSimulationMetricSummary:
    return OfflineSimulationMetricSummary(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0)


def validate_offline_runner_result(
    data: ControlledSimulationResultReportInput | Mapping[str, Any],
) -> bool:
    data = _coerce_input(data)
    runner_result = _runner(data)
    if runner_result is None:
        return False
    runner_approved = (
        data.offline_runner_approved is not False
        and (
            data.offline_runner_approved is True
            or _state_contains(
                runner_result,
                "READY_FOR_CONTROLLED_SIMULATION_RESULT_REPORT",
                "APPROVE_CONTROLLED_SIMULATION_OFFLINE_RUNNER",
            )
        )
    )
    return (
        runner_approved
        and _get(runner_result, "offline_only", True) is True
        and not _contains(
            _get(runner_result, "risks", ()),
            "REVIEW_PRECHECK_NOT_APPROVED",
            "OFFLINE_SCENARIO_EMPTY",
            "SYNTHETIC_MARKET_PATH_INVALID",
            "SIGNAL_SEQUENCE_INVALID",
            "RISK_LIMITS_MISSING",
            "STOP_CONDITIONS_MISSING",
            "REAL_EXECUTION_BOUNDARY_VIOLATION",
            "DATA_ACCESS_VIOLATION",
            "PREMATURE_RESULT_REPORT",
        )
    )


def summarize_offline_simulation_metrics(
    runner_result: Any,
) -> OfflineSimulationMetricSummary:
    metrics = _metrics(runner_result)
    if metrics is None:
        return _empty_summary()
    try:
        initial = float(_get(metrics, "initial_equity"))
        final = float(_get(metrics, "final_equity"))
        total_pnl = float(_get(metrics, "total_pnl"))
        realized = float(_get(metrics, "realized_pnl"))
        unrealized = float(_get(metrics, "unrealized_pnl"))
        max_drawdown = float(_get(metrics, "max_drawdown"))
        max_drawdown_fraction = float(_get(metrics, "max_drawdown_fraction"))
        win_rate = float(_get(metrics, "win_rate"))
        profit_factor = float(_get(metrics, "profit_factor"))
        expectancy = float(_get(metrics, "expectancy"))
    except (TypeError, ValueError):
        return _empty_summary()
    return_fraction = total_pnl / initial if initial else 0.0
    return OfflineSimulationMetricSummary(
        _round(initial),
        _round(final),
        _round(total_pnl),
        _round(realized),
        _round(unrealized),
        _round(max_drawdown),
        _round(max_drawdown_fraction),
        int(_get(metrics, "trade_count", 0)),
        int(_get(metrics, "winning_trade_count", 0)),
        int(_get(metrics, "losing_trade_count", 0)),
        _round(win_rate),
        profit_factor,
        _round(expectancy),
        _round(return_fraction),
    )


def review_offline_equity_curve(
    runner_result: Any,
    metric_summary: OfflineSimulationMetricSummary,
    tolerance: float = 1e-6,
) -> OfflineEquityCurveReview:
    curve = _equity_curve(runner_result)
    if not curve:
        risk = ControlledSimulationResultReportRisk.EQUITY_CURVE_REVIEW_INVALID
        return OfflineEquityCurveReview(0, 0.0, 0.0, 0.0, 0.0, False, False, False, (risk,))
    equities = tuple(float(_get(point, "equity", math.nan)) for point in curve)
    steps = tuple(int(_get(point, "step", index)) for index, point in enumerate(curve))
    valid_equities = all(_finite(equity) and equity >= 0 for equity in equities)
    monotonic_steps = all(next_step > step for step, next_step in zip(steps, steps[1:]))
    final_matches = valid_equities and _close(equities[-1], metric_summary.final_equity, tolerance)
    passed = valid_equities and monotonic_steps and final_matches
    risks = () if passed else (ControlledSimulationResultReportRisk.EQUITY_CURVE_REVIEW_INVALID,)
    return OfflineEquityCurveReview(
        len(curve),
        _round(equities[0]) if valid_equities else 0.0,
        _round(equities[-1]) if valid_equities else 0.0,
        _round(min(equities)) if valid_equities else 0.0,
        _round(max(equities)) if valid_equities else 0.0,
        monotonic_steps,
        final_matches,
        passed,
        risks,
    )


def review_offline_pnl_quality(
    runner_result: Any,
    metric_summary: OfflineSimulationMetricSummary,
    tolerance: float = 1e-6,
) -> OfflinePnLQualityReview:
    curve = _equity_curve(runner_result)
    if not curve:
        risk = ControlledSimulationResultReportRisk.PNL_REPORT_INVALID
        return OfflinePnLQualityReview(metric_summary.total_pnl, 0.0, 0.0, False, False, False, (risk,))
    recomputed = float(_get(curve[-1], "equity")) - metric_summary.initial_equity
    component_total = metric_summary.realized_pnl + metric_summary.unrealized_pnl
    matches_equity = _close(metric_summary.total_pnl, recomputed, tolerance)
    matches_components = _close(metric_summary.total_pnl, component_total, tolerance)
    passed = matches_equity and matches_components and _finite(metric_summary.total_pnl)
    risks = () if passed else (ControlledSimulationResultReportRisk.PNL_REPORT_INVALID,)
    return OfflinePnLQualityReview(
        _round(metric_summary.total_pnl),
        _round(recomputed),
        _round(component_total),
        matches_equity,
        matches_components,
        passed,
        risks,
    )


def _recompute_drawdown(curve: tuple[Any, ...]) -> tuple[float, float]:
    peak = 0.0
    max_drawdown = 0.0
    max_fraction = 0.0
    for point in curve:
        equity = float(_get(point, "equity", 0.0))
        peak = max(peak, equity)
        drawdown = max(0.0, peak - equity)
        fraction = drawdown / peak if peak else 0.0
        max_drawdown = max(max_drawdown, drawdown)
        max_fraction = max(max_fraction, fraction)
    return _round(max_drawdown), _round(max_fraction)


def review_offline_drawdown_quality(
    runner_result: Any,
    metric_summary: OfflineSimulationMetricSummary,
    max_allowed_drawdown_fraction: float | None = None,
    tolerance: float = 1e-6,
) -> OfflineDrawdownQualityReview:
    curve = _equity_curve(runner_result)
    if not curve:
        risk = ControlledSimulationResultReportRisk.DRAWDOWN_REPORT_INVALID
        return OfflineDrawdownQualityReview(metric_summary.max_drawdown, 0.0, metric_summary.max_drawdown_fraction, 0.0, False, False, (risk,))
    recomputed, recomputed_fraction = _recompute_drawdown(curve)
    amount_ok = _close(metric_summary.max_drawdown, recomputed, tolerance)
    fraction_ok = _close(metric_summary.max_drawdown_fraction, recomputed_fraction, tolerance)
    limit_ok = max_allowed_drawdown_fraction is None or metric_summary.max_drawdown_fraction <= max_allowed_drawdown_fraction + tolerance
    passed = amount_ok and fraction_ok and limit_ok and metric_summary.max_drawdown >= 0 and metric_summary.max_drawdown_fraction >= 0
    risks = () if passed else (ControlledSimulationResultReportRisk.DRAWDOWN_REPORT_INVALID,)
    return OfflineDrawdownQualityReview(
        _round(metric_summary.max_drawdown),
        recomputed,
        _round(metric_summary.max_drawdown_fraction),
        recomputed_fraction,
        limit_ok,
        passed,
        risks,
    )


def review_offline_win_rate_quality(
    metric_summary: OfflineSimulationMetricSummary,
) -> OfflinePostRunFinding:
    count_ok = metric_summary.trade_count >= 0 and metric_summary.winning_trade_count >= 0 and metric_summary.losing_trade_count >= 0
    aggregate_ok = metric_summary.winning_trade_count + metric_summary.losing_trade_count <= metric_summary.trade_count
    rate_ok = 0.0 <= metric_summary.win_rate <= 1.0
    if metric_summary.trade_count:
        expected = metric_summary.winning_trade_count / metric_summary.trade_count
        rate_ok = rate_ok and _close(metric_summary.win_rate, expected, 1e-6)
    else:
        rate_ok = rate_ok and metric_summary.win_rate == 0.0
    passed = count_ok and aggregate_ok and rate_ok
    risks = () if passed else (ControlledSimulationResultReportRisk.WIN_RATE_REPORT_INVALID,)
    return OfflinePostRunFinding("win_rate_quality", passed, 100 if passed else 0, risks)


def review_offline_profit_factor_quality(
    metric_summary: OfflineSimulationMetricSummary,
) -> OfflinePostRunFinding:
    profit_factor = metric_summary.profit_factor
    passed = _numeric_or_inf(profit_factor) and profit_factor >= 0.0
    risks = () if passed else (ControlledSimulationResultReportRisk.PROFIT_FACTOR_REPORT_INVALID,)
    return OfflinePostRunFinding("profit_factor_quality", passed, 100 if passed else 0, risks)


def review_offline_expectancy_quality(
    metric_summary: OfflineSimulationMetricSummary,
) -> OfflinePostRunFinding:
    passed = _finite(metric_summary.expectancy) and (metric_summary.trade_count > 0 or metric_summary.expectancy == 0.0)
    risks = () if passed else (ControlledSimulationResultReportRisk.EXPECTANCY_REPORT_INVALID,)
    return OfflinePostRunFinding("expectancy_quality", passed, 100 if passed else 0, risks)


def review_offline_position_consistency(
    runner_result: Any,
    require_flat_final_position: bool = True,
    tolerance: float = 1e-6,
) -> OfflinePositionConsistencyReview:
    position = _final_position(runner_result)
    curve = _equity_curve(runner_result)
    if position is None:
        risk = ControlledSimulationResultReportRisk.POSITION_CONSISTENCY_INVALID
        return OfflinePositionConsistencyReview("", 0.0, 0.0, 0.0, 0.0, require_flat_final_position, False, False, False, (risk,))
    quantity = float(_get(position, "quantity", math.nan))
    equity = float(_get(position, "equity", math.nan))
    flat = _finite(quantity) and abs(quantity) <= tolerance
    equity_matches = bool(curve) and _finite(equity) and _close(equity, float(_get(curve[-1], "equity")), tolerance)
    expected_flat_ok = not require_flat_final_position or flat
    passed = expected_flat_ok and equity_matches
    risks = () if passed else (ControlledSimulationResultReportRisk.POSITION_CONSISTENCY_INVALID,)
    return OfflinePositionConsistencyReview(
        _value(_get(position, "symbol")),
        _round(quantity) if _finite(quantity) else 0.0,
        _round(float(_get(position, "average_price", 0.0))) if _finite(_get(position, "average_price", 0.0)) else 0.0,
        _round(float(_get(position, "cash", 0.0))) if _finite(_get(position, "cash", 0.0)) else 0.0,
        _round(equity) if _finite(equity) else 0.0,
        require_flat_final_position,
        flat,
        equity_matches,
        passed,
        risks,
    )


def review_offline_stop_conditions(
    runner_result: Any,
) -> OfflinePostRunFinding:
    stop = _stop_conditions(runner_result)
    if stop is None:
        risk = ControlledSimulationResultReportRisk.STOP_CONDITION_REVIEW_INVALID
        return OfflinePostRunFinding("stop_condition_review", False, 0, (risk,), ("missing_stop_condition_result",))
    stop_risks = _as_tuple(_get(stop, "risks", ()))
    triggered = bool(_get(stop, "triggered", False))
    passed = not triggered and not stop_risks
    risks = () if passed else (ControlledSimulationResultReportRisk.STOP_CONDITION_REVIEW_INVALID,)
    details = tuple(_value(item) for item in stop_risks) or tuple(_value(item) for item in _as_tuple(_get(stop, "reasons", ())))
    return OfflinePostRunFinding("stop_condition_review", passed, 100 if passed else 60, risks, details)


def review_offline_runner_risks(
    runner_result: Any,
) -> OfflinePostRunFinding:
    runner_risks = _as_tuple(_get(runner_result, "risks", ()))
    blocking = _contains(
        runner_risks,
        "REVIEW_PRECHECK_NOT_APPROVED",
        "OFFLINE_SCENARIO_EMPTY",
        "SYNTHETIC_MARKET_PATH_INVALID",
        "SIGNAL_SEQUENCE_INVALID",
        "RISK_LIMITS_MISSING",
        "STOP_CONDITIONS_MISSING",
        "REAL_EXECUTION_BOUNDARY_VIOLATION",
        "DATA_ACCESS_VIOLATION",
        "PREMATURE_RESULT_REPORT",
    )
    passed = not runner_risks and not blocking
    risks = () if passed else (ControlledSimulationResultReportRisk.RISK_REVIEW_INCOMPLETE,)
    details = tuple(_value(item) for item in runner_risks)
    return OfflinePostRunFinding("runner_risk_review", passed, 100 if passed else 60, risks, details)


def detect_result_report_risks(
    data: ControlledSimulationResultReportInput | Mapping[str, Any],
    metric_summary: OfflineSimulationMetricSummary | None = None,
    equity_curve_review: OfflineEquityCurveReview | None = None,
    pnl_quality: OfflinePnLQualityReview | None = None,
    drawdown_quality: OfflineDrawdownQualityReview | None = None,
    win_rate_quality: OfflinePostRunFinding | None = None,
    profit_factor_quality: OfflinePostRunFinding | None = None,
    expectancy_quality: OfflinePostRunFinding | None = None,
    position_consistency: OfflinePositionConsistencyReview | None = None,
    stop_condition_review: OfflinePostRunFinding | None = None,
    runner_risk_review: OfflinePostRunFinding | None = None,
) -> tuple[ControlledSimulationResultReportRisk, ...]:
    data = _coerce_input(data)
    runner_result = _runner(data)
    risks: list[ControlledSimulationResultReportRisk] = []
    if runner_result is None:
        risks.append(ControlledSimulationResultReportRisk.OFFLINE_RUNNER_RESULT_MISSING)
    elif not validate_offline_runner_result(data):
        risks.append(ControlledSimulationResultReportRisk.OFFLINE_RUNNER_NOT_APPROVED)
    if runner_result is None or not _metrics_valid(_metrics(runner_result)):
        risks.append(ControlledSimulationResultReportRisk.METRICS_MISSING)
    for review in (
        equity_curve_review,
        pnl_quality,
        drawdown_quality,
        win_rate_quality,
        profit_factor_quality,
        expectancy_quality,
        position_consistency,
        stop_condition_review,
        runner_risk_review,
    ):
        if review is not None:
            risks.extend(_as_tuple(_get(review, "risks", ())))
    if not _offline_boundary(data):
        risks.append(ControlledSimulationResultReportRisk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(ControlledSimulationResultReportRisk.DATA_ACCESS_VIOLATION)
    if data.performance_metrics_engine_requested is True:
        risks.append(ControlledSimulationResultReportRisk.PREMATURE_PERFORMANCE_METRICS_ENGINE)
    return _dedupe(risks)


def _finding_score(passed: bool, warning_score: int = 60) -> int:
    return 100 if passed else warning_score


def compute_result_report_score(
    data: ControlledSimulationResultReportInput | Mapping[str, Any],
    risks: tuple[ControlledSimulationResultReportRisk, ...] = (),
    metric_summary: OfflineSimulationMetricSummary | None = None,
    equity_curve_review: OfflineEquityCurveReview | None = None,
    pnl_quality: OfflinePnLQualityReview | None = None,
    drawdown_quality: OfflineDrawdownQualityReview | None = None,
    win_rate_quality: OfflinePostRunFinding | None = None,
    profit_factor_quality: OfflinePostRunFinding | None = None,
    expectancy_quality: OfflinePostRunFinding | None = None,
    position_consistency: OfflinePositionConsistencyReview | None = None,
    stop_condition_review: OfflinePostRunFinding | None = None,
    runner_risk_review: OfflinePostRunFinding | None = None,
) -> ControlledSimulationResultReportScore:
    data = _coerce_input(data)
    runner_score = 100 if validate_offline_runner_result(data) else 0
    metric_score = 100 if metric_summary is not None and _metrics_valid(_metrics(_runner(data))) else 0
    equity_score = _finding_score(bool(equity_curve_review and equity_curve_review.passed), 0)
    pnl_score = _finding_score(bool(pnl_quality and pnl_quality.passed), 0)
    drawdown_score = _finding_score(bool(drawdown_quality and drawdown_quality.passed), 0)
    win_rate_score = win_rate_quality.score if win_rate_quality is not None else 0
    profit_factor_score = profit_factor_quality.score if profit_factor_quality is not None else 0
    expectancy_score = expectancy_quality.score if expectancy_quality is not None else 0
    position_score = _finding_score(bool(position_consistency and position_consistency.passed), 0)
    stop_score = stop_condition_review.score if stop_condition_review is not None else 0
    risk_review_score = runner_risk_review.score if runner_risk_review is not None else 0
    boundary_score = 100 if _offline_boundary(data) and _data_boundary(data) else 0
    values = (
        runner_score,
        metric_score,
        equity_score,
        pnl_score,
        drawdown_score,
        win_rate_score,
        profit_factor_score,
        expectancy_score,
        position_score,
        stop_score,
        risk_review_score,
        boundary_score,
    )
    overall = _clamp(sum(values) / len(values) - min(80, len(set(risks)) * 4))
    for risk, cap in {
        ControlledSimulationResultReportRisk.OFFLINE_RUNNER_NOT_APPROVED: 50,
        ControlledSimulationResultReportRisk.OFFLINE_RUNNER_RESULT_MISSING: 35,
        ControlledSimulationResultReportRisk.METRICS_MISSING: 45,
        ControlledSimulationResultReportRisk.PNL_REPORT_INVALID: 55,
        ControlledSimulationResultReportRisk.DRAWDOWN_REPORT_INVALID: 55,
        ControlledSimulationResultReportRisk.WIN_RATE_REPORT_INVALID: 60,
        ControlledSimulationResultReportRisk.PROFIT_FACTOR_REPORT_INVALID: 60,
        ControlledSimulationResultReportRisk.EXPECTANCY_REPORT_INVALID: 60,
        ControlledSimulationResultReportRisk.EQUITY_CURVE_REVIEW_INVALID: 50,
        ControlledSimulationResultReportRisk.POSITION_CONSISTENCY_INVALID: 50,
        ControlledSimulationResultReportRisk.STOP_CONDITION_REVIEW_INVALID: 65,
        ControlledSimulationResultReportRisk.RISK_REVIEW_INCOMPLETE: 65,
        ControlledSimulationResultReportRisk.REAL_EXECUTION_BOUNDARY_VIOLATION: 35,
        ControlledSimulationResultReportRisk.DATA_ACCESS_VIOLATION: 35,
        ControlledSimulationResultReportRisk.PREMATURE_PERFORMANCE_METRICS_ENGINE: 40,
    }.items():
        if risk in risks:
            overall = min(overall, cap)
    return ControlledSimulationResultReportScore(
        overall,
        runner_score,
        metric_score,
        equity_score,
        pnl_score,
        drawdown_score,
        win_rate_score,
        profit_factor_score,
        expectancy_score,
        position_score,
        stop_score,
        risk_review_score,
        boundary_score,
    )


def _select_decision(
    risks: tuple[ControlledSimulationResultReportRisk, ...],
) -> ControlledSimulationResultReportDecision:
    if (
        ControlledSimulationResultReportRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in risks
        or ControlledSimulationResultReportRisk.DATA_ACCESS_VIOLATION in risks
        or ControlledSimulationResultReportRisk.PREMATURE_PERFORMANCE_METRICS_ENGINE in risks
    ):
        return ControlledSimulationResultReportDecision.BLOCK_RESULT_REPORT
    if (
        ControlledSimulationResultReportRisk.OFFLINE_RUNNER_NOT_APPROVED in risks
        or ControlledSimulationResultReportRisk.OFFLINE_RUNNER_RESULT_MISSING in risks
    ):
        return ControlledSimulationResultReportDecision.REQUIRE_OFFLINE_RUNNER_FIXES
    if (
        ControlledSimulationResultReportRisk.METRICS_MISSING in risks
        or ControlledSimulationResultReportRisk.PNL_REPORT_INVALID in risks
        or ControlledSimulationResultReportRisk.DRAWDOWN_REPORT_INVALID in risks
        or ControlledSimulationResultReportRisk.WIN_RATE_REPORT_INVALID in risks
        or ControlledSimulationResultReportRisk.PROFIT_FACTOR_REPORT_INVALID in risks
        or ControlledSimulationResultReportRisk.EXPECTANCY_REPORT_INVALID in risks
    ):
        return ControlledSimulationResultReportDecision.REQUIRE_METRIC_FIXES
    if ControlledSimulationResultReportRisk.EQUITY_CURVE_REVIEW_INVALID in risks:
        return ControlledSimulationResultReportDecision.REQUIRE_EQUITY_CURVE_FIXES
    if ControlledSimulationResultReportRisk.POSITION_CONSISTENCY_INVALID in risks:
        return ControlledSimulationResultReportDecision.REQUIRE_POSITION_FIXES
    if ControlledSimulationResultReportRisk.STOP_CONDITION_REVIEW_INVALID in risks:
        return ControlledSimulationResultReportDecision.REQUIRE_STOP_CONDITION_FIXES
    if ControlledSimulationResultReportRisk.RISK_REVIEW_INCOMPLETE in risks:
        return ControlledSimulationResultReportDecision.REQUIRE_RISK_REVIEW_FIXES
    return ControlledSimulationResultReportDecision.APPROVE_CONTROLLED_SIMULATION_RESULT_REPORT


def _select_state(
    decision: ControlledSimulationResultReportDecision,
    risks: tuple[ControlledSimulationResultReportRisk, ...],
    score: int,
) -> ControlledSimulationResultReportState:
    if decision == ControlledSimulationResultReportDecision.BLOCK_RESULT_REPORT:
        return ControlledSimulationResultReportState.REPORT_BLOCKED
    if decision == ControlledSimulationResultReportDecision.REQUIRE_OFFLINE_RUNNER_FIXES:
        return ControlledSimulationResultReportState.REPORT_INPUT_INVALID
    if decision == ControlledSimulationResultReportDecision.REQUIRE_METRIC_FIXES and (
        ControlledSimulationResultReportRisk.METRICS_MISSING in risks
        or ControlledSimulationResultReportRisk.PNL_REPORT_INVALID in risks
    ):
        return ControlledSimulationResultReportState.REPORT_BLOCKED
    if risks:
        return ControlledSimulationResultReportState.REPORT_COMPLETED_WITH_WARNINGS
    if score >= 95:
        return ControlledSimulationResultReportState.READY_FOR_PERFORMANCE_METRICS_ENGINE
    return ControlledSimulationResultReportState.REPORT_COMPLETED


def generate_result_report_recommendations(
    risks: tuple[ControlledSimulationResultReportRisk, ...],
    decision: ControlledSimulationResultReportDecision | None = None,
) -> tuple[ControlledSimulationResultReportRecommendation, ...]:
    recommendations: list[ControlledSimulationResultReportRecommendation] = []
    if risks:
        recommendations.append(ControlledSimulationResultReportRecommendation.HOLD_PERFORMANCE_METRICS_ENGINE)
    mapping = {
        ControlledSimulationResultReportRisk.OFFLINE_RUNNER_NOT_APPROVED: ControlledSimulationResultReportRecommendation.APPROVE_OFFLINE_RUNNER_FIRST,
        ControlledSimulationResultReportRisk.OFFLINE_RUNNER_RESULT_MISSING: ControlledSimulationResultReportRecommendation.PROVIDE_OFFLINE_RUNNER_RESULT,
        ControlledSimulationResultReportRisk.METRICS_MISSING: ControlledSimulationResultReportRecommendation.REBUILD_METRIC_SUMMARY,
        ControlledSimulationResultReportRisk.PNL_REPORT_INVALID: ControlledSimulationResultReportRecommendation.RECHECK_PNL_REPORT,
        ControlledSimulationResultReportRisk.DRAWDOWN_REPORT_INVALID: ControlledSimulationResultReportRecommendation.RECHECK_DRAWDOWN_REPORT,
        ControlledSimulationResultReportRisk.WIN_RATE_REPORT_INVALID: ControlledSimulationResultReportRecommendation.RECHECK_WIN_RATE_REPORT,
        ControlledSimulationResultReportRisk.PROFIT_FACTOR_REPORT_INVALID: ControlledSimulationResultReportRecommendation.RECHECK_PROFIT_FACTOR_REPORT,
        ControlledSimulationResultReportRisk.EXPECTANCY_REPORT_INVALID: ControlledSimulationResultReportRecommendation.RECHECK_EXPECTANCY_REPORT,
        ControlledSimulationResultReportRisk.EQUITY_CURVE_REVIEW_INVALID: ControlledSimulationResultReportRecommendation.REBUILD_EQUITY_CURVE_REVIEW,
        ControlledSimulationResultReportRisk.POSITION_CONSISTENCY_INVALID: ControlledSimulationResultReportRecommendation.RECONCILE_FINAL_POSITION,
        ControlledSimulationResultReportRisk.STOP_CONDITION_REVIEW_INVALID: ControlledSimulationResultReportRecommendation.REVIEW_STOP_CONDITIONS,
        ControlledSimulationResultReportRisk.RISK_REVIEW_INCOMPLETE: ControlledSimulationResultReportRecommendation.COMPLETE_RISK_REVIEW,
        ControlledSimulationResultReportRisk.REAL_EXECUTION_BOUNDARY_VIOLATION: ControlledSimulationResultReportRecommendation.RESTORE_REAL_EXECUTION_BOUNDARIES,
        ControlledSimulationResultReportRisk.DATA_ACCESS_VIOLATION: ControlledSimulationResultReportRecommendation.REMOVE_DATA_ACCESS,
        ControlledSimulationResultReportRisk.PREMATURE_PERFORMANCE_METRICS_ENGINE: ControlledSimulationResultReportRecommendation.DELAY_PERFORMANCE_METRICS_ENGINE,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(ControlledSimulationResultReportRecommendation.RUN_RESULT_REPORT_POST_REVIEW_SUITE)
    if decision == ControlledSimulationResultReportDecision.APPROVE_CONTROLLED_SIMULATION_RESULT_REPORT:
        recommendations.append(ControlledSimulationResultReportRecommendation.APPROVE_PERFORMANCE_METRICS_ENGINE)
    return _dedupe(recommendations)


def evaluate_controlled_simulation_result_report_post_review(
    data: ControlledSimulationResultReportInput | Mapping[str, Any],
) -> ControlledSimulationResultReportResult:
    data = _coerce_input(data)
    runner_result = _runner(data)
    metric_summary = summarize_offline_simulation_metrics(runner_result)
    equity_curve_review = review_offline_equity_curve(runner_result, metric_summary, data.metric_tolerance)
    pnl_quality = review_offline_pnl_quality(runner_result, metric_summary, data.metric_tolerance)
    drawdown_quality = review_offline_drawdown_quality(
        runner_result,
        metric_summary,
        data.max_allowed_drawdown_fraction,
        data.metric_tolerance,
    )
    win_rate_quality = review_offline_win_rate_quality(metric_summary)
    profit_factor_quality = review_offline_profit_factor_quality(metric_summary)
    expectancy_quality = review_offline_expectancy_quality(metric_summary)
    position_consistency = review_offline_position_consistency(
        runner_result,
        data.require_flat_final_position,
        data.metric_tolerance,
    )
    stop_condition_review = review_offline_stop_conditions(runner_result)
    runner_risk_review = review_offline_runner_risks(runner_result)
    risks = detect_result_report_risks(
        data,
        metric_summary,
        equity_curve_review,
        pnl_quality,
        drawdown_quality,
        win_rate_quality,
        profit_factor_quality,
        expectancy_quality,
        position_consistency,
        stop_condition_review,
        runner_risk_review,
    )
    score = compute_result_report_score(
        data,
        risks,
        metric_summary,
        equity_curve_review,
        pnl_quality,
        drawdown_quality,
        win_rate_quality,
        profit_factor_quality,
        expectancy_quality,
        position_consistency,
        stop_condition_review,
        runner_risk_review,
    )
    decision = _select_decision(risks)
    state = _select_state(decision, risks, score.overall_score)
    recommendations = generate_result_report_recommendations(risks, decision)
    findings = (
        win_rate_quality,
        profit_factor_quality,
        expectancy_quality,
        stop_condition_review,
        runner_risk_review,
    )
    offline_only = _offline_boundary(data) and _data_boundary(data)
    summary = f"{state.value}: decision={decision.value}, score={score.overall_score}, risks={len(risks)}, pnl={metric_summary.total_pnl}"
    return ControlledSimulationResultReportResult(
        state,
        decision,
        score.overall_score,
        score,
        risks,
        recommendations,
        metric_summary,
        equity_curve_review,
        pnl_quality,
        drawdown_quality,
        win_rate_quality,
        profit_factor_quality,
        expectancy_quality,
        position_consistency,
        stop_condition_review,
        runner_risk_review,
        findings,
        offline_only,
        summary,
    )


def render_controlled_simulation_result_report_markdown(
    result: ControlledSimulationResultReportResult,
) -> str:
    lines = [
        "# AGIcore Controlled Simulation Result Report + Post-Run Review",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Score: {result.report_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Metrics",
        f"- Initial equity: {result.metric_summary.initial_equity}",
        f"- Final equity: {result.metric_summary.final_equity}",
        f"- Total PnL: {result.metric_summary.total_pnl}",
        f"- Realized PnL: {result.metric_summary.realized_pnl}",
        f"- Unrealized PnL: {result.metric_summary.unrealized_pnl}",
        f"- Max drawdown: {result.metric_summary.max_drawdown}",
        f"- Max drawdown fraction: {result.metric_summary.max_drawdown_fraction}",
        f"- Win rate: {result.metric_summary.win_rate}",
        f"- Profit factor: {result.metric_summary.profit_factor}",
        f"- Expectancy: {result.metric_summary.expectancy}",
        f"- Return fraction: {result.metric_summary.return_fraction}",
        "",
        "# Reviews",
        f"- Equity curve: passed={result.equity_curve_review.passed}, points={result.equity_curve_review.point_count}",
        f"- PnL quality: passed={result.pnl_quality.passed}, recomputed={result.pnl_quality.recomputed_total_pnl}",
        f"- Drawdown quality: passed={result.drawdown_quality.passed}, recomputed={result.drawdown_quality.recomputed_max_drawdown}",
        f"- Position consistency: passed={result.position_consistency.passed}, quantity={result.position_consistency.quantity}",
        f"- Stop conditions: passed={result.stop_condition_review.passed}",
        f"- Runner risk review: passed={result.runner_risk_review.passed}",
        "",
        "# Risks",
    ]
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_result_report_score",
    "detect_result_report_risks",
    "evaluate_controlled_simulation_result_report_post_review",
    "generate_result_report_recommendations",
    "render_controlled_simulation_result_report_markdown",
    "review_offline_drawdown_quality",
    "review_offline_equity_curve",
    "review_offline_expectancy_quality",
    "review_offline_pnl_quality",
    "review_offline_position_consistency",
    "review_offline_profit_factor_quality",
    "review_offline_runner_risks",
    "review_offline_stop_conditions",
    "review_offline_win_rate_quality",
    "summarize_offline_simulation_metrics",
    "validate_offline_runner_result",
]
