"""Offline performance metrics engine for controlled simulation results."""

from __future__ import annotations

import math
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.performance_metrics_engine_models import (
    EquityPerformanceSample,
    PerformanceMetricSummary,
    PerformanceMetricsEngineDecision,
    PerformanceMetricsEngineInput,
    PerformanceMetricsEngineRecommendation,
    PerformanceMetricsEngineResult,
    PerformanceMetricsEngineRisk,
    PerformanceMetricsEngineScore,
    PerformanceMetricsEngineState,
    PerformanceThresholds,
    PerformanceValidationFinding,
    TradePerformanceSample,
)


def _coerce_input(data: PerformanceMetricsEngineInput | Mapping[str, Any]) -> PerformanceMetricsEngineInput:
    if isinstance(data, PerformanceMetricsEngineInput):
        return data
    allowed = {field.name for field in fields(PerformanceMetricsEngineInput)}
    payload = {key: value for key, value in dict(data).items() if key in allowed}
    return PerformanceMetricsEngineInput(**payload)


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


def _report(data: PerformanceMetricsEngineInput) -> Any:
    return data.controlled_simulation_result_report


def _runner(data: PerformanceMetricsEngineInput) -> Any:
    return data.controlled_simulation_offline_runner_result


def _metric_summary(report: Any) -> Any:
    return _get(report, "metric_summary")


def _upstream_items(data: PerformanceMetricsEngineInput) -> tuple[Any, ...]:
    return (
        data.controlled_simulation_result_report,
        data.controlled_simulation_offline_runner_result,
        data.controlled_simulation_result_report_input,
        data.controlled_simulation_offline_runner_input,
        data.controlled_simulation_review_precheck,
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


def _upstream_risks(data: PerformanceMetricsEngineInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PerformanceMetricsEngineInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _offline_boundary(data: PerformanceMetricsEngineInput) -> bool:
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


def _data_boundary(data: PerformanceMetricsEngineInput) -> bool:
    return (
        data.synthetic_data_only is True
        and data.in_memory_only is True
        and data.data_access_requested is not True
        and not _has_upstream_risk(data, "DATA_ACCESS", "DATA_ACCESS_VIOLATION", "REAL_DATA")
    )


def _coerce_trade_sample(item: TradePerformanceSample | Mapping[str, Any]) -> TradePerformanceSample:
    if isinstance(item, TradePerformanceSample):
        return item
    payload = dict(item)
    return TradePerformanceSample(
        pnl=float(payload.get("pnl", 0.0)),
        quantity=float(payload.get("quantity", 1.0)),
        entry_price=float(payload.get("entry_price", 0.0)),
        exit_price=float(payload.get("exit_price", 0.0)),
        symbol=str(payload.get("symbol", "")),
        step_open=int(payload.get("step_open", 0)),
        step_close=int(payload.get("step_close", 0)),
    )


def _coerce_equity_sample(item: EquityPerformanceSample | Mapping[str, Any], fallback_step: int) -> EquityPerformanceSample:
    if isinstance(item, EquityPerformanceSample):
        return item
    payload = dict(item)
    return EquityPerformanceSample(
        step=int(payload.get("step", fallback_step)),
        equity=float(payload.get("equity", 0.0)),
        drawdown=float(payload.get("drawdown", 0.0)),
        drawdown_fraction=float(payload.get("drawdown_fraction", 0.0)),
        timestamp=str(payload.get("timestamp", "")),
    )


def _thresholds(data: PerformanceMetricsEngineInput) -> PerformanceThresholds | None:
    if data.thresholds is None:
        return None
    if isinstance(data.thresholds, PerformanceThresholds):
        return data.thresholds
    allowed = {field.name for field in fields(PerformanceThresholds)}
    payload = {key: value for key, value in dict(data.thresholds).items() if key in allowed}
    return PerformanceThresholds(**payload)


def _thresholds_valid(thresholds: PerformanceThresholds | None) -> bool:
    return (
        thresholds is not None
        and thresholds.min_trade_count >= 0
        and thresholds.max_drawdown_fraction >= 0
        and 0 <= thresholds.min_win_rate <= 1
        and thresholds.min_profit_factor >= 0
        and thresholds.min_risk_reward_ratio >= 0
        and 0 <= thresholds.min_stability_score <= 100
        and 0 <= thresholds.min_quality_score <= 100
    )


def validate_controlled_simulation_result_report(
    data: PerformanceMetricsEngineInput | Mapping[str, Any],
) -> bool:
    data = _coerce_input(data)
    report = _report(data)
    if report is None:
        return False
    approved = (
        data.result_report_approved is not False
        and (
            data.result_report_approved is True
            or _state_contains(
                report,
                "READY_FOR_PERFORMANCE_METRICS_ENGINE",
                "APPROVE_CONTROLLED_SIMULATION_RESULT_REPORT",
            )
        )
    )
    return (
        approved
        and _get(report, "offline_only", True) is True
        and not _contains(
            _get(report, "risks", ()),
            "OFFLINE_RUNNER_NOT_APPROVED",
            "OFFLINE_RUNNER_RESULT_MISSING",
            "METRICS_MISSING",
            "PNL_REPORT_INVALID",
            "DRAWDOWN_REPORT_INVALID",
            "WIN_RATE_REPORT_INVALID",
            "PROFIT_FACTOR_REPORT_INVALID",
            "EXPECTANCY_REPORT_INVALID",
            "EQUITY_CURVE_REVIEW_INVALID",
            "POSITION_CONSISTENCY_INVALID",
            "REAL_EXECUTION_BOUNDARY_VIOLATION",
            "DATA_ACCESS_VIOLATION",
            "PREMATURE_PERFORMANCE_METRICS_ENGINE",
        )
    )


def _extract_trade_samples(data: PerformanceMetricsEngineInput) -> tuple[TradePerformanceSample, ...]:
    if data.trade_samples is not None:
        return tuple(_coerce_trade_sample(item) for item in data.trade_samples)
    runner = _runner(data)
    final_position = _get(runner, "final_position")
    closed_trade_pnls = tuple(float(pnl) for pnl in _as_tuple(_get(final_position, "closed_trade_pnls", ())))
    if closed_trade_pnls:
        return tuple(TradePerformanceSample(pnl=pnl, symbol=_value(_get(final_position, "symbol"))) for pnl in closed_trade_pnls)
    summary = _metric_summary(_report(data))
    trade_count = int(_get(summary, "trade_count", 0) or 0)
    if trade_count > 0 and _finite(_get(summary, "expectancy", None)):
        return tuple(TradePerformanceSample(pnl=float(_get(summary, "expectancy")), symbol="summary") for _ in range(trade_count))
    return ()


def _extract_equity_samples(data: PerformanceMetricsEngineInput) -> tuple[EquityPerformanceSample, ...]:
    if data.equity_samples is not None:
        return tuple(_coerce_equity_sample(item, index) for index, item in enumerate(data.equity_samples))
    runner = _runner(data)
    curve = _as_tuple(_get(runner, "equity_curve", ()))
    if curve:
        return tuple(
            EquityPerformanceSample(
                step=int(_get(point, "step", index)),
                equity=float(_get(point, "equity", 0.0)),
                drawdown=float(_get(point, "drawdown", 0.0)),
                drawdown_fraction=float(_get(point, "drawdown_fraction", 0.0)),
                timestamp=_value(_get(point, "timestamp")),
            )
            for index, point in enumerate(curve)
        )
    return ()


def extract_performance_inputs(
    data: PerformanceMetricsEngineInput | Mapping[str, Any],
) -> dict[str, Any]:
    data = _coerce_input(data)
    return {
        "report": _report(data),
        "runner": _runner(data),
        "metric_summary": _metric_summary(_report(data)),
        "trade_samples": _extract_trade_samples(data),
        "equity_samples": _extract_equity_samples(data),
        "thresholds": _thresholds(data),
    }


def compute_total_pnl(
    metric_summary: Any = None,
    trade_samples: tuple[TradePerformanceSample, ...] = (),
    equity_samples: tuple[EquityPerformanceSample, ...] = (),
) -> float:
    if trade_samples:
        return _round(sum(sample.pnl for sample in trade_samples))
    if equity_samples and all(_finite(sample.equity) for sample in equity_samples):
        return _round(equity_samples[-1].equity - equity_samples[0].equity)
    if metric_summary is not None and _finite(_get(metric_summary, "total_pnl")):
        return _round(float(_get(metric_summary, "total_pnl")))
    return 0.0


def compute_return_fraction(
    total_pnl: float,
    metric_summary: Any = None,
    equity_samples: tuple[EquityPerformanceSample, ...] = (),
) -> float:
    if metric_summary is not None and _finite(_get(metric_summary, "return_fraction")):
        return _round(float(_get(metric_summary, "return_fraction")))
    initial = float(_get(metric_summary, "initial_equity", 0.0) or 0.0)
    if not initial and equity_samples:
        initial = equity_samples[0].equity
    return _round(total_pnl / initial) if initial else 0.0


def compute_max_drawdown(
    metric_summary: Any = None,
    equity_samples: tuple[EquityPerformanceSample, ...] = (),
) -> tuple[float, float]:
    if equity_samples and all(_finite(sample.equity) for sample in equity_samples):
        peak = equity_samples[0].equity
        max_drawdown = 0.0
        max_fraction = 0.0
        for sample in equity_samples:
            peak = max(peak, sample.equity)
            drawdown = max(0.0, peak - sample.equity)
            fraction = drawdown / peak if peak else 0.0
            max_drawdown = max(max_drawdown, drawdown)
            max_fraction = max(max_fraction, fraction)
        return _round(max_drawdown), _round(max_fraction)
    if metric_summary is not None and _finite(_get(metric_summary, "max_drawdown")):
        return _round(float(_get(metric_summary, "max_drawdown"))), _round(float(_get(metric_summary, "max_drawdown_fraction", 0.0)))
    return 0.0, 0.0


def compute_win_rate(
    trade_samples: tuple[TradePerformanceSample, ...] = (),
    metric_summary: Any = None,
) -> float:
    if trade_samples:
        return _round(sum(1 for sample in trade_samples if sample.pnl > 0) / len(trade_samples))
    if metric_summary is not None and _finite(_get(metric_summary, "win_rate")):
        return _round(float(_get(metric_summary, "win_rate")))
    return 0.0


def compute_profit_factor(
    trade_samples: tuple[TradePerformanceSample, ...] = (),
    metric_summary: Any = None,
) -> float:
    if trade_samples:
        gross_profit = sum(sample.pnl for sample in trade_samples if sample.pnl > 0)
        gross_loss = abs(sum(sample.pnl for sample in trade_samples if sample.pnl < 0))
        if gross_loss == 0:
            return float("inf") if gross_profit > 0 else 0.0
        return _round(gross_profit / gross_loss)
    if metric_summary is not None and _numeric_or_inf(_get(metric_summary, "profit_factor")):
        return float(_get(metric_summary, "profit_factor"))
    return 0.0


def compute_expectancy(
    trade_samples: tuple[TradePerformanceSample, ...] = (),
    metric_summary: Any = None,
) -> float:
    if trade_samples:
        return _round(sum(sample.pnl for sample in trade_samples) / len(trade_samples))
    if metric_summary is not None and _finite(_get(metric_summary, "expectancy")):
        return _round(float(_get(metric_summary, "expectancy")))
    return 0.0


def compute_trade_count(
    trade_samples: tuple[TradePerformanceSample, ...] = (),
    metric_summary: Any = None,
) -> int:
    if trade_samples:
        return len(trade_samples)
    return int(_get(metric_summary, "trade_count", 0) or 0)


def compute_average_win(trade_samples: tuple[TradePerformanceSample, ...] = ()) -> float:
    winners = [sample.pnl for sample in trade_samples if sample.pnl > 0]
    return _round(sum(winners) / len(winners)) if winners else 0.0


def compute_average_loss(trade_samples: tuple[TradePerformanceSample, ...] = ()) -> float:
    losers = [sample.pnl for sample in trade_samples if sample.pnl < 0]
    return _round(sum(losers) / len(losers)) if losers else 0.0


def compute_risk_reward_ratio(average_win: float, average_loss: float) -> float:
    if average_loss == 0:
        return float("inf") if average_win > 0 else 0.0
    return _round(average_win / abs(average_loss))


def _equity_samples_valid(equity_samples: tuple[EquityPerformanceSample, ...]) -> bool:
    if not equity_samples:
        return False
    steps = tuple(sample.step for sample in equity_samples)
    return (
        len(set(steps)) == len(steps)
        and all(next_step > step for step, next_step in zip(steps, steps[1:]))
        and all(_finite(sample.equity) and sample.equity >= 0 for sample in equity_samples)
    )


def compute_performance_stability_score(
    equity_samples: tuple[EquityPerformanceSample, ...] = (),
) -> int:
    if not _equity_samples_valid(equity_samples):
        return 0
    if len(equity_samples) == 1:
        return 100
    _, max_drawdown_fraction = compute_max_drawdown(equity_samples=equity_samples)
    changes = [abs(right.equity - left.equity) for left, right in zip(equity_samples, equity_samples[1:])]
    baseline = max(equity_samples[0].equity, 1.0)
    volatility_fraction = (sum(changes) / len(changes)) / baseline
    return _clamp(100 - (max_drawdown_fraction * 100) - (volatility_fraction * 100))


def compute_performance_quality_score(
    summary: PerformanceMetricSummary,
    thresholds: PerformanceThresholds | None,
) -> int:
    if thresholds is None:
        return 0
    checks = (
        _finite(summary.total_pnl),
        _finite(summary.return_fraction) and summary.return_fraction >= thresholds.min_return_fraction,
        _finite(summary.max_drawdown_fraction) and summary.max_drawdown_fraction <= thresholds.max_drawdown_fraction,
        _finite(summary.win_rate) and summary.win_rate >= thresholds.min_win_rate,
        _numeric_or_inf(summary.profit_factor) and summary.profit_factor >= thresholds.min_profit_factor,
        _finite(summary.expectancy) and summary.expectancy >= thresholds.min_expectancy,
        summary.trade_count >= thresholds.min_trade_count,
        _numeric_or_inf(summary.risk_reward_ratio) and summary.risk_reward_ratio >= thresholds.min_risk_reward_ratio,
        summary.stability_score >= thresholds.min_stability_score,
    )
    return _clamp(sum(100 for passed in checks if passed) / len(checks))


def _build_metric_summary(inputs: Mapping[str, Any]) -> PerformanceMetricSummary:
    metric_summary = inputs["metric_summary"]
    trade_samples = tuple(inputs["trade_samples"])
    equity_samples = tuple(inputs["equity_samples"])
    thresholds = inputs["thresholds"]
    total_pnl = compute_total_pnl(metric_summary, trade_samples, equity_samples)
    return_fraction = compute_return_fraction(total_pnl, metric_summary, equity_samples)
    max_drawdown, max_drawdown_fraction = compute_max_drawdown(metric_summary, equity_samples)
    win_rate = compute_win_rate(trade_samples, metric_summary)
    profit_factor = compute_profit_factor(trade_samples, metric_summary)
    expectancy = compute_expectancy(trade_samples, metric_summary)
    trade_count = compute_trade_count(trade_samples, metric_summary)
    average_win = compute_average_win(trade_samples)
    average_loss = compute_average_loss(trade_samples)
    risk_reward = compute_risk_reward_ratio(average_win, average_loss)
    stability = compute_performance_stability_score(equity_samples)
    provisional = PerformanceMetricSummary(
        total_pnl,
        return_fraction,
        _round(return_fraction * 100),
        max_drawdown,
        max_drawdown_fraction,
        win_rate,
        profit_factor,
        expectancy,
        trade_count,
        average_win,
        average_loss,
        risk_reward,
        stability,
        0,
    )
    quality = compute_performance_quality_score(provisional, thresholds)
    return PerformanceMetricSummary(
        total_pnl,
        return_fraction,
        _round(return_fraction * 100),
        max_drawdown,
        max_drawdown_fraction,
        win_rate,
        profit_factor,
        expectancy,
        trade_count,
        average_win,
        average_loss,
        risk_reward,
        stability,
        quality,
    )


def _metric_matches_report(value: float, report_value: Any, tolerance: float) -> bool:
    if not _numeric_or_inf(value) or not _numeric_or_inf(report_value):
        return False
    if math.isinf(float(value)) or math.isinf(float(report_value)):
        return math.isinf(float(value)) and math.isinf(float(report_value))
    return _close(float(value), float(report_value), tolerance)


def detect_performance_metric_risks(
    data: PerformanceMetricsEngineInput | Mapping[str, Any],
    performance_summary: PerformanceMetricSummary | None = None,
    inputs: Mapping[str, Any] | None = None,
) -> tuple[PerformanceMetricsEngineRisk, ...]:
    data = _coerce_input(data)
    inputs = extract_performance_inputs(data) if inputs is None else inputs
    performance_summary = _build_metric_summary(inputs) if performance_summary is None else performance_summary
    risks: list[PerformanceMetricsEngineRisk] = []
    report_summary = inputs["metric_summary"]
    trade_samples = tuple(inputs["trade_samples"])
    equity_samples = tuple(inputs["equity_samples"])
    thresholds = inputs["thresholds"]
    if not validate_controlled_simulation_result_report(data):
        risks.append(PerformanceMetricsEngineRisk.RESULT_REPORT_NOT_APPROVED)
    if report_summary is None:
        risks.append(PerformanceMetricsEngineRisk.PERFORMANCE_INPUT_MISSING)
    if not trade_samples:
        risks.append(PerformanceMetricsEngineRisk.TRADE_SAMPLE_EMPTY)
    if not _equity_samples_valid(equity_samples):
        risks.append(PerformanceMetricsEngineRisk.EQUITY_SAMPLE_INVALID)
    if not _thresholds_valid(thresholds):
        risks.append(PerformanceMetricsEngineRisk.PERFORMANCE_THRESHOLD_MISSING)
    tolerance = data.metric_tolerance
    if not _finite(performance_summary.total_pnl) or (
        report_summary is not None and not _metric_matches_report(performance_summary.total_pnl, _get(report_summary, "total_pnl"), tolerance)
    ):
        risks.append(PerformanceMetricsEngineRisk.PNL_INVALID)
    if not _finite(performance_summary.return_fraction) or performance_summary.return_fraction < -1:
        risks.append(PerformanceMetricsEngineRisk.RETURN_INVALID)
    if (
        not _finite(performance_summary.max_drawdown)
        or not _finite(performance_summary.max_drawdown_fraction)
        or performance_summary.max_drawdown < 0
        or performance_summary.max_drawdown_fraction < 0
        or (report_summary is not None and not _metric_matches_report(performance_summary.max_drawdown, _get(report_summary, "max_drawdown"), tolerance))
    ):
        risks.append(PerformanceMetricsEngineRisk.DRAWDOWN_INVALID)
    if (
        not _finite(performance_summary.win_rate)
        or not 0 <= performance_summary.win_rate <= 1
        or (report_summary is not None and not _metric_matches_report(performance_summary.win_rate, _get(report_summary, "win_rate"), tolerance))
    ):
        risks.append(PerformanceMetricsEngineRisk.WIN_RATE_INVALID)
    if (
        not _numeric_or_inf(performance_summary.profit_factor)
        or performance_summary.profit_factor < 0
        or (
            report_summary is not None
            and not _metric_matches_report(performance_summary.profit_factor, _get(report_summary, "profit_factor"), tolerance)
        )
    ):
        risks.append(PerformanceMetricsEngineRisk.PROFIT_FACTOR_INVALID)
    if (
        not _finite(performance_summary.expectancy)
        or (report_summary is not None and not _metric_matches_report(performance_summary.expectancy, _get(report_summary, "expectancy"), tolerance))
    ):
        risks.append(PerformanceMetricsEngineRisk.EXPECTANCY_INVALID)
    if thresholds is not None and performance_summary.trade_count < thresholds.min_trade_count:
        risks.append(PerformanceMetricsEngineRisk.TRADE_COUNT_TOO_LOW)
    if not _numeric_or_inf(performance_summary.risk_reward_ratio) or performance_summary.risk_reward_ratio < 0:
        risks.append(PerformanceMetricsEngineRisk.RISK_REWARD_INVALID)
    if thresholds is not None and (
        performance_summary.stability_score < thresholds.min_stability_score
        or performance_summary.quality_score < thresholds.min_quality_score
        or performance_summary.max_drawdown_fraction > thresholds.max_drawdown_fraction
        or performance_summary.win_rate < thresholds.min_win_rate
        or performance_summary.profit_factor < thresholds.min_profit_factor
        or performance_summary.expectancy < thresholds.min_expectancy
        or performance_summary.return_fraction < thresholds.min_return_fraction
        or performance_summary.risk_reward_ratio < thresholds.min_risk_reward_ratio
    ):
        risks.append(PerformanceMetricsEngineRisk.PERFORMANCE_STABILITY_WEAK)
    if not _offline_boundary(data):
        risks.append(PerformanceMetricsEngineRisk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(PerformanceMetricsEngineRisk.DATA_ACCESS_VIOLATION)
    if data.risk_metrics_engine_requested is True:
        risks.append(PerformanceMetricsEngineRisk.PREMATURE_RISK_METRICS_ENGINE)
    return _dedupe(risks)


def _finding(
    name: str,
    passed: bool,
    risk: PerformanceMetricsEngineRisk,
    details: tuple[str, ...] = (),
    warning_score: int = 60,
) -> PerformanceValidationFinding:
    return PerformanceValidationFinding(name, passed, 100 if passed else warning_score, () if passed else (risk,), details)


def _build_findings(
    data: PerformanceMetricsEngineInput,
    summary: PerformanceMetricSummary,
    inputs: Mapping[str, Any],
) -> tuple[PerformanceValidationFinding, ...]:
    thresholds = inputs["thresholds"]
    report_summary = inputs["metric_summary"]
    trade_samples = tuple(inputs["trade_samples"])
    equity_samples = tuple(inputs["equity_samples"])
    tolerance = data.metric_tolerance
    return (
        _finding("result_report", validate_controlled_simulation_result_report(data), PerformanceMetricsEngineRisk.RESULT_REPORT_NOT_APPROVED),
        _finding("trade_samples", bool(trade_samples), PerformanceMetricsEngineRisk.TRADE_SAMPLE_EMPTY, (f"count={len(trade_samples)}",)),
        _finding("equity_samples", _equity_samples_valid(equity_samples), PerformanceMetricsEngineRisk.EQUITY_SAMPLE_INVALID, (f"count={len(equity_samples)}",)),
        _finding("thresholds", _thresholds_valid(thresholds), PerformanceMetricsEngineRisk.PERFORMANCE_THRESHOLD_MISSING),
        _finding("pnl", report_summary is not None and _metric_matches_report(summary.total_pnl, _get(report_summary, "total_pnl"), tolerance), PerformanceMetricsEngineRisk.PNL_INVALID),
        _finding("return", _finite(summary.return_fraction) and summary.return_fraction >= -1, PerformanceMetricsEngineRisk.RETURN_INVALID),
        _finding("drawdown", _finite(summary.max_drawdown_fraction) and summary.max_drawdown_fraction >= 0, PerformanceMetricsEngineRisk.DRAWDOWN_INVALID),
        _finding("win_rate", _finite(summary.win_rate) and 0 <= summary.win_rate <= 1, PerformanceMetricsEngineRisk.WIN_RATE_INVALID),
        _finding("profit_factor", _numeric_or_inf(summary.profit_factor) and summary.profit_factor >= 0, PerformanceMetricsEngineRisk.PROFIT_FACTOR_INVALID),
        _finding("expectancy", _finite(summary.expectancy), PerformanceMetricsEngineRisk.EXPECTANCY_INVALID),
        _finding("trade_count", thresholds is not None and summary.trade_count >= thresholds.min_trade_count, PerformanceMetricsEngineRisk.TRADE_COUNT_TOO_LOW),
        _finding("risk_reward", _numeric_or_inf(summary.risk_reward_ratio) and summary.risk_reward_ratio >= 0, PerformanceMetricsEngineRisk.RISK_REWARD_INVALID),
        _finding("stability", thresholds is not None and summary.stability_score >= thresholds.min_stability_score and summary.quality_score >= thresholds.min_quality_score, PerformanceMetricsEngineRisk.PERFORMANCE_STABILITY_WEAK),
    )


def _finding_score(findings: tuple[PerformanceValidationFinding, ...], name: str) -> int:
    for finding in findings:
        if finding.name == name:
            return finding.score
    return 0


def _compute_engine_score(
    data: PerformanceMetricsEngineInput,
    risks: tuple[PerformanceMetricsEngineRisk, ...],
    findings: tuple[PerformanceValidationFinding, ...],
) -> PerformanceMetricsEngineScore:
    result_report_score = _finding_score(findings, "result_report")
    trade_sample_score = _finding_score(findings, "trade_samples")
    equity_sample_score = _finding_score(findings, "equity_samples")
    threshold_score = _finding_score(findings, "thresholds")
    pnl_score = _finding_score(findings, "pnl")
    return_score = _finding_score(findings, "return")
    drawdown_score = _finding_score(findings, "drawdown")
    win_rate_score = _finding_score(findings, "win_rate")
    profit_factor_score = _finding_score(findings, "profit_factor")
    expectancy_score = _finding_score(findings, "expectancy")
    trade_count_score = _finding_score(findings, "trade_count")
    risk_reward_score = _finding_score(findings, "risk_reward")
    stability_score = _finding_score(findings, "stability")
    boundary_score = 100 if _offline_boundary(data) and _data_boundary(data) else 0
    values = (
        result_report_score,
        trade_sample_score,
        equity_sample_score,
        threshold_score,
        pnl_score,
        return_score,
        drawdown_score,
        win_rate_score,
        profit_factor_score,
        expectancy_score,
        trade_count_score,
        risk_reward_score,
        stability_score,
        boundary_score,
    )
    overall = _clamp(sum(values) / len(values) - min(80, len(set(risks)) * 4))
    for risk, cap in {
        PerformanceMetricsEngineRisk.RESULT_REPORT_NOT_APPROVED: 50,
        PerformanceMetricsEngineRisk.PERFORMANCE_INPUT_MISSING: 45,
        PerformanceMetricsEngineRisk.TRADE_SAMPLE_EMPTY: 55,
        PerformanceMetricsEngineRisk.EQUITY_SAMPLE_INVALID: 50,
        PerformanceMetricsEngineRisk.PNL_INVALID: 55,
        PerformanceMetricsEngineRisk.RETURN_INVALID: 60,
        PerformanceMetricsEngineRisk.DRAWDOWN_INVALID: 55,
        PerformanceMetricsEngineRisk.WIN_RATE_INVALID: 60,
        PerformanceMetricsEngineRisk.PROFIT_FACTOR_INVALID: 60,
        PerformanceMetricsEngineRisk.EXPECTANCY_INVALID: 60,
        PerformanceMetricsEngineRisk.TRADE_COUNT_TOO_LOW: 70,
        PerformanceMetricsEngineRisk.RISK_REWARD_INVALID: 60,
        PerformanceMetricsEngineRisk.PERFORMANCE_STABILITY_WEAK: 75,
        PerformanceMetricsEngineRisk.PERFORMANCE_THRESHOLD_MISSING: 55,
        PerformanceMetricsEngineRisk.REAL_EXECUTION_BOUNDARY_VIOLATION: 35,
        PerformanceMetricsEngineRisk.DATA_ACCESS_VIOLATION: 35,
        PerformanceMetricsEngineRisk.PREMATURE_RISK_METRICS_ENGINE: 40,
    }.items():
        if risk in risks:
            overall = min(overall, cap)
    return PerformanceMetricsEngineScore(
        overall,
        result_report_score,
        trade_sample_score,
        equity_sample_score,
        threshold_score,
        pnl_score,
        return_score,
        drawdown_score,
        win_rate_score,
        profit_factor_score,
        expectancy_score,
        trade_count_score,
        risk_reward_score,
        stability_score,
        boundary_score,
    )


def _select_decision(
    risks: tuple[PerformanceMetricsEngineRisk, ...],
) -> PerformanceMetricsEngineDecision:
    if (
        PerformanceMetricsEngineRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in risks
        or PerformanceMetricsEngineRisk.DATA_ACCESS_VIOLATION in risks
        or PerformanceMetricsEngineRisk.PREMATURE_RISK_METRICS_ENGINE in risks
    ):
        return PerformanceMetricsEngineDecision.BLOCK_PERFORMANCE_METRICS
    if (
        PerformanceMetricsEngineRisk.RESULT_REPORT_NOT_APPROVED in risks
        or PerformanceMetricsEngineRisk.PERFORMANCE_INPUT_MISSING in risks
    ):
        return PerformanceMetricsEngineDecision.REQUIRE_RESULT_REPORT_FIXES
    if PerformanceMetricsEngineRisk.TRADE_SAMPLE_EMPTY in risks:
        return PerformanceMetricsEngineDecision.REQUIRE_TRADE_SAMPLE_FIXES
    if PerformanceMetricsEngineRisk.EQUITY_SAMPLE_INVALID in risks:
        return PerformanceMetricsEngineDecision.REQUIRE_EQUITY_SAMPLE_FIXES
    if PerformanceMetricsEngineRisk.PERFORMANCE_THRESHOLD_MISSING in risks:
        return PerformanceMetricsEngineDecision.REQUIRE_THRESHOLD_FIXES
    if risks:
        return PerformanceMetricsEngineDecision.REQUIRE_PERFORMANCE_REVIEW
    return PerformanceMetricsEngineDecision.APPROVE_PERFORMANCE_METRICS_ENGINE


def _select_state(
    decision: PerformanceMetricsEngineDecision,
    risks: tuple[PerformanceMetricsEngineRisk, ...],
    score: int,
) -> PerformanceMetricsEngineState:
    if decision == PerformanceMetricsEngineDecision.BLOCK_PERFORMANCE_METRICS:
        return PerformanceMetricsEngineState.METRICS_BLOCKED
    if decision in {
        PerformanceMetricsEngineDecision.REQUIRE_RESULT_REPORT_FIXES,
        PerformanceMetricsEngineDecision.REQUIRE_TRADE_SAMPLE_FIXES,
        PerformanceMetricsEngineDecision.REQUIRE_EQUITY_SAMPLE_FIXES,
        PerformanceMetricsEngineDecision.REQUIRE_THRESHOLD_FIXES,
    }:
        return PerformanceMetricsEngineState.INPUT_INVALID
    if risks:
        return PerformanceMetricsEngineState.METRICS_COMPLETED_WITH_WARNINGS
    if score >= 95:
        return PerformanceMetricsEngineState.READY_FOR_RISK_METRICS_ENGINE
    return PerformanceMetricsEngineState.METRICS_COMPLETED


def generate_performance_metric_recommendations(
    risks: tuple[PerformanceMetricsEngineRisk, ...],
    decision: PerformanceMetricsEngineDecision | None = None,
) -> tuple[PerformanceMetricsEngineRecommendation, ...]:
    recommendations: list[PerformanceMetricsEngineRecommendation] = []
    if risks:
        recommendations.append(PerformanceMetricsEngineRecommendation.HOLD_RISK_METRICS_ENGINE)
    mapping = {
        PerformanceMetricsEngineRisk.RESULT_REPORT_NOT_APPROVED: PerformanceMetricsEngineRecommendation.APPROVE_RESULT_REPORT_FIRST,
        PerformanceMetricsEngineRisk.PERFORMANCE_INPUT_MISSING: PerformanceMetricsEngineRecommendation.PROVIDE_PERFORMANCE_INPUTS,
        PerformanceMetricsEngineRisk.TRADE_SAMPLE_EMPTY: PerformanceMetricsEngineRecommendation.PROVIDE_TRADE_SAMPLES,
        PerformanceMetricsEngineRisk.EQUITY_SAMPLE_INVALID: PerformanceMetricsEngineRecommendation.REBUILD_EQUITY_SAMPLES,
        PerformanceMetricsEngineRisk.PNL_INVALID: PerformanceMetricsEngineRecommendation.RECHECK_PNL,
        PerformanceMetricsEngineRisk.RETURN_INVALID: PerformanceMetricsEngineRecommendation.RECHECK_RETURN,
        PerformanceMetricsEngineRisk.DRAWDOWN_INVALID: PerformanceMetricsEngineRecommendation.RECHECK_DRAWDOWN,
        PerformanceMetricsEngineRisk.WIN_RATE_INVALID: PerformanceMetricsEngineRecommendation.RECHECK_WIN_RATE,
        PerformanceMetricsEngineRisk.PROFIT_FACTOR_INVALID: PerformanceMetricsEngineRecommendation.RECHECK_PROFIT_FACTOR,
        PerformanceMetricsEngineRisk.EXPECTANCY_INVALID: PerformanceMetricsEngineRecommendation.RECHECK_EXPECTANCY,
        PerformanceMetricsEngineRisk.TRADE_COUNT_TOO_LOW: PerformanceMetricsEngineRecommendation.INCREASE_TRADE_SAMPLE_SIZE,
        PerformanceMetricsEngineRisk.RISK_REWARD_INVALID: PerformanceMetricsEngineRecommendation.RECHECK_RISK_REWARD,
        PerformanceMetricsEngineRisk.PERFORMANCE_STABILITY_WEAK: PerformanceMetricsEngineRecommendation.IMPROVE_PERFORMANCE_STABILITY,
        PerformanceMetricsEngineRisk.PERFORMANCE_THRESHOLD_MISSING: PerformanceMetricsEngineRecommendation.DEFINE_PERFORMANCE_THRESHOLDS,
        PerformanceMetricsEngineRisk.REAL_EXECUTION_BOUNDARY_VIOLATION: PerformanceMetricsEngineRecommendation.RESTORE_REAL_EXECUTION_BOUNDARIES,
        PerformanceMetricsEngineRisk.DATA_ACCESS_VIOLATION: PerformanceMetricsEngineRecommendation.REMOVE_DATA_ACCESS,
        PerformanceMetricsEngineRisk.PREMATURE_RISK_METRICS_ENGINE: PerformanceMetricsEngineRecommendation.DELAY_RISK_METRICS_ENGINE,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(PerformanceMetricsEngineRecommendation.RUN_PERFORMANCE_METRICS_ENGINE_SUITE)
    if decision == PerformanceMetricsEngineDecision.APPROVE_PERFORMANCE_METRICS_ENGINE:
        recommendations.append(PerformanceMetricsEngineRecommendation.APPROVE_RISK_METRICS_ENGINE)
    return _dedupe(recommendations)


def evaluate_performance_metrics_engine(
    data: PerformanceMetricsEngineInput | Mapping[str, Any],
) -> PerformanceMetricsEngineResult:
    data = _coerce_input(data)
    inputs = extract_performance_inputs(data)
    thresholds = inputs["thresholds"] or PerformanceThresholds()
    trade_samples = tuple(inputs["trade_samples"])
    equity_samples = tuple(inputs["equity_samples"])
    metric_summary = _build_metric_summary(inputs)
    risks = detect_performance_metric_risks(data, metric_summary, inputs)
    findings = _build_findings(data, metric_summary, inputs)
    score = _compute_engine_score(data, risks, findings)
    decision = _select_decision(risks)
    state = _select_state(decision, risks, score.overall_score)
    recommendations = generate_performance_metric_recommendations(risks, decision)
    offline_only = _offline_boundary(data) and _data_boundary(data)
    summary = f"{state.value}: decision={decision.value}, score={score.overall_score}, risks={len(risks)}, pnl={metric_summary.total_pnl}"
    return PerformanceMetricsEngineResult(
        state,
        decision,
        score.overall_score,
        score,
        risks,
        recommendations,
        metric_summary,
        thresholds,
        trade_samples,
        equity_samples,
        findings,
        offline_only,
        summary,
    )


def render_performance_metrics_engine_markdown(
    result: PerformanceMetricsEngineResult,
) -> str:
    lines = [
        "# AGIcore Performance Metrics Engine",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Score: {result.engine_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Performance Metrics",
        f"- Total PnL: {result.metric_summary.total_pnl}",
        f"- Return fraction: {result.metric_summary.return_fraction}",
        f"- Return percent: {result.metric_summary.return_percent}",
        f"- Max drawdown: {result.metric_summary.max_drawdown}",
        f"- Max drawdown fraction: {result.metric_summary.max_drawdown_fraction}",
        f"- Win rate: {result.metric_summary.win_rate}",
        f"- Profit factor: {result.metric_summary.profit_factor}",
        f"- Expectancy: {result.metric_summary.expectancy}",
        f"- Trade count: {result.metric_summary.trade_count}",
        f"- Average win: {result.metric_summary.average_win}",
        f"- Average loss: {result.metric_summary.average_loss}",
        f"- Risk/reward ratio: {result.metric_summary.risk_reward_ratio}",
        f"- Stability score: {result.metric_summary.stability_score}",
        f"- Quality score: {result.metric_summary.quality_score}",
        "",
        "# Risks",
    ]
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    lines.append("")
    lines.append("# Findings")
    for finding in result.findings:
        risks = ", ".join(risk.value for risk in finding.risks) or "none"
        lines.append(f"- {finding.name}: passed={finding.passed}, score={finding.score}/100, risks={risks}")
    return "\n".join(lines)


__all__ = [
    "compute_average_loss",
    "compute_average_win",
    "compute_expectancy",
    "compute_max_drawdown",
    "compute_performance_quality_score",
    "compute_performance_stability_score",
    "compute_profit_factor",
    "compute_return_fraction",
    "compute_risk_reward_ratio",
    "compute_total_pnl",
    "compute_trade_count",
    "compute_win_rate",
    "detect_performance_metric_risks",
    "evaluate_performance_metrics_engine",
    "extract_performance_inputs",
    "generate_performance_metric_recommendations",
    "render_performance_metrics_engine_markdown",
    "validate_controlled_simulation_result_report",
]
