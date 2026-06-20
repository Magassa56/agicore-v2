"""Offline risk metrics engine for controlled simulation performance results."""

from __future__ import annotations

import math
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.risk_metrics_engine_models import (
    EquityRiskSample,
    PositionRiskSample,
    RiskMetricSummary,
    RiskMetricsEngineDecision,
    RiskMetricsEngineInput,
    RiskMetricsEngineRecommendation,
    RiskMetricsEngineResult,
    RiskMetricsEngineRisk,
    RiskMetricsEngineScore,
    RiskMetricsEngineState,
    RiskThresholds,
    RiskValidationFinding,
    StopConditionRiskSample,
    TradeRiskSample,
)


def _coerce_input(data: RiskMetricsEngineInput | Mapping[str, Any]) -> RiskMetricsEngineInput:
    if isinstance(data, RiskMetricsEngineInput):
        return data
    allowed = {field.name for field in fields(RiskMetricsEngineInput)}
    payload = {key: value for key, value in dict(data).items() if key in allowed}
    return RiskMetricsEngineInput(**payload)


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


def _close(left: float, right: float, tolerance: float) -> bool:
    return abs(float(left) - float(right)) <= max(tolerance, 0.0)


def _performance_result(data: RiskMetricsEngineInput) -> Any:
    return data.performance_metrics_result


def _runner(data: RiskMetricsEngineInput) -> Any:
    return data.controlled_simulation_offline_runner_result


def _report(data: RiskMetricsEngineInput) -> Any:
    return data.controlled_simulation_result_report


def _performance_summary(data: RiskMetricsEngineInput) -> Any:
    return (
        data.performance_metric_summary
        or _get(_performance_result(data), "metric_summary")
        or _get(_report(data), "metric_summary")
        or data.offline_simulation_metrics
        or _get(_runner(data), "metrics")
    )


def _upstream_items(data: RiskMetricsEngineInput) -> tuple[Any, ...]:
    return (
        data.performance_metrics_result,
        data.performance_metrics_input,
        data.performance_metric_summary,
        data.performance_thresholds,
        data.controlled_simulation_result_report,
        data.controlled_simulation_offline_runner_result,
        data.offline_simulation_metrics,
        data.offline_equity_curve,
        data.offline_position_state,
        data.offline_stop_conditions,
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


def _upstream_risks(data: RiskMetricsEngineInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: RiskMetricsEngineInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _offline_boundary(data: RiskMetricsEngineInput) -> bool:
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


def _data_boundary(data: RiskMetricsEngineInput) -> bool:
    return (
        data.synthetic_data_only is True
        and data.in_memory_only is True
        and data.data_access_requested is not True
        and not _has_upstream_risk(data, "DATA_ACCESS", "DATA_ACCESS_VIOLATION", "REAL_DATA")
    )


def _thresholds(data: RiskMetricsEngineInput) -> RiskThresholds | None:
    if data.thresholds is None:
        return None
    if isinstance(data.thresholds, RiskThresholds):
        return data.thresholds
    allowed = {field.name for field in fields(RiskThresholds)}
    payload = {key: value for key, value in dict(data.thresholds).items() if key in allowed}
    return RiskThresholds(**payload)


def _thresholds_valid(thresholds: RiskThresholds | None) -> bool:
    return (
        thresholds is not None
        and thresholds.max_loss_amount >= 0
        and thresholds.max_drawdown_fraction >= 0
        and 0 <= thresholds.max_risk_per_trade_fraction
        and thresholds.max_exposure_fraction >= 0
        and thresholds.max_position_risk_amount >= 0
        and thresholds.max_consecutive_losses >= 0
        and 0 <= thresholds.min_loss_stability_score <= 100
        and 0 <= thresholds.min_stop_condition_quality_score <= 100
        and 0 <= thresholds.min_quality_score <= 100
    )


def validate_performance_metrics_result(data: RiskMetricsEngineInput | Mapping[str, Any]) -> bool:
    data = _coerce_input(data)
    result = _performance_result(data)
    if result is None:
        return False
    approved = (
        data.performance_metrics_approved is not False
        and (
            data.performance_metrics_approved is True
            or _state_contains(
                result,
                "READY_FOR_RISK_METRICS_ENGINE",
                "APPROVE_PERFORMANCE_METRICS_ENGINE",
            )
        )
    )
    return (
        approved
        and _get(result, "offline_only", True) is True
        and not _contains(
            _get(result, "risks", ()),
            "RESULT_REPORT_NOT_APPROVED",
            "PERFORMANCE_INPUT_MISSING",
            "TRADE_SAMPLE_EMPTY",
            "EQUITY_SAMPLE_INVALID",
            "PNL_INVALID",
            "RETURN_INVALID",
            "DRAWDOWN_INVALID",
            "WIN_RATE_INVALID",
            "PROFIT_FACTOR_INVALID",
            "EXPECTANCY_INVALID",
            "RISK_REWARD_INVALID",
            "REAL_EXECUTION_BOUNDARY_VIOLATION",
            "DATA_ACCESS_VIOLATION",
            "PREMATURE_RISK_METRICS_ENGINE",
        )
    )


def _coerce_trade_sample(item: Any) -> TradeRiskSample:
    return TradeRiskSample(
        pnl=float(_get(item, "pnl", 0.0)),
        quantity=float(_get(item, "quantity", 1.0)),
        entry_price=float(_get(item, "entry_price", 0.0)),
        exit_price=float(_get(item, "exit_price", 0.0)),
        risk_amount=float(_get(item, "risk_amount", 0.0)),
        symbol=_value(_get(item, "symbol")),
        step_open=int(_get(item, "step_open", 0) or 0),
        step_close=int(_get(item, "step_close", 0) or 0),
    )


def _coerce_equity_sample(item: Any, fallback_step: int) -> EquityRiskSample:
    return EquityRiskSample(
        step=int(_get(item, "step", fallback_step)),
        equity=float(_get(item, "equity", 0.0)),
        drawdown=float(_get(item, "drawdown", 0.0)),
        drawdown_fraction=float(_get(item, "drawdown_fraction", 0.0)),
        timestamp=_value(_get(item, "timestamp")),
    )


def _coerce_position_sample(item: Any, fallback_step: int) -> PositionRiskSample:
    return PositionRiskSample(
        step=int(_get(item, "step", fallback_step)),
        symbol=_value(_get(item, "symbol")),
        quantity=float(_get(item, "quantity", _get(item, "position_quantity", 0.0))),
        price=float(_get(item, "price", _get(item, "average_price", 0.0))),
        equity=float(_get(item, "equity", 0.0)),
        realized_pnl=float(_get(item, "realized_pnl", 0.0)),
        unrealized_pnl=float(_get(item, "unrealized_pnl", 0.0)),
    )


def _coerce_stop_condition_sample(item: Any, fallback_name: str = "stop_conditions") -> StopConditionRiskSample:
    reasons = tuple(_value(reason) for reason in _as_tuple(_get(item, "reasons", ())))
    risks = tuple(_as_tuple(_get(item, "risks", ())))
    return StopConditionRiskSample(
        name=_value(_get(item, "name", fallback_name)) or fallback_name,
        configured=bool(_get(item, "configured", True)),
        triggered=bool(_get(item, "triggered", False)),
        reasons=reasons,
        risks=risks,
    )


def _extract_trade_risk_samples(data: RiskMetricsEngineInput) -> tuple[TradeRiskSample, ...]:
    if data.trade_risk_samples is not None:
        return tuple(_coerce_trade_sample(item) for item in data.trade_risk_samples)
    performance_samples = _as_tuple(_get(_performance_result(data), "trade_samples", ()))
    if performance_samples:
        return tuple(_coerce_trade_sample(item) for item in performance_samples)
    final_position = _get(_runner(data), "final_position")
    closed_trade_pnls = tuple(float(pnl) for pnl in _as_tuple(_get(final_position, "closed_trade_pnls", ())))
    if closed_trade_pnls:
        return tuple(TradeRiskSample(pnl=pnl, symbol=_value(_get(final_position, "symbol"))) for pnl in closed_trade_pnls)
    summary = _performance_summary(data)
    trade_count = int(_get(summary, "trade_count", 0) or 0)
    expectancy = _get(summary, "expectancy")
    if trade_count > 0 and _finite(expectancy):
        return tuple(TradeRiskSample(pnl=float(expectancy), symbol="summary") for _ in range(trade_count))
    return ()


def _extract_equity_risk_samples(data: RiskMetricsEngineInput) -> tuple[EquityRiskSample, ...]:
    if data.equity_risk_samples is not None:
        return tuple(_coerce_equity_sample(item, index) for index, item in enumerate(data.equity_risk_samples))
    performance_samples = _as_tuple(_get(_performance_result(data), "equity_samples", ()))
    if performance_samples:
        return tuple(_coerce_equity_sample(item, index) for index, item in enumerate(performance_samples))
    if data.offline_equity_curve is not None:
        return tuple(_coerce_equity_sample(item, index) for index, item in enumerate(_as_tuple(data.offline_equity_curve)))
    runner_curve = _as_tuple(_get(_runner(data), "equity_curve", ()))
    if runner_curve:
        return tuple(_coerce_equity_sample(item, index) for index, item in enumerate(runner_curve))
    return ()


def _extract_position_risk_samples(data: RiskMetricsEngineInput) -> tuple[PositionRiskSample, ...]:
    if data.position_risk_samples is not None:
        return tuple(_coerce_position_sample(item, index) for index, item in enumerate(data.position_risk_samples))
    step_logs = _as_tuple(_get(_runner(data), "step_logs", ()))
    if step_logs:
        return tuple(_coerce_position_sample(item, index) for index, item in enumerate(step_logs))
    if data.offline_position_state is not None:
        return (_coerce_position_sample(data.offline_position_state, 0),)
    final_position = _get(_runner(data), "final_position")
    if final_position is not None:
        return (_coerce_position_sample(final_position, 0),)
    return ()


def _extract_stop_condition_samples(data: RiskMetricsEngineInput) -> tuple[StopConditionRiskSample, ...]:
    if data.stop_condition_samples is not None:
        return tuple(_coerce_stop_condition_sample(item) for item in data.stop_condition_samples)
    if data.offline_stop_conditions is not None:
        return (_coerce_stop_condition_sample(data.offline_stop_conditions),)
    runner_stop_conditions = _get(_runner(data), "stop_conditions")
    if runner_stop_conditions is not None:
        return (_coerce_stop_condition_sample(runner_stop_conditions),)
    report_stop_review = _get(_report(data), "stop_condition_review")
    if report_stop_review is not None:
        return (
            StopConditionRiskSample(
                "report_stop_condition_review",
                configured=True,
                triggered=False,
                reasons=tuple(_as_tuple(_get(report_stop_review, "details", ()))),
                risks=tuple(_as_tuple(_get(report_stop_review, "risks", ()))),
            ),
        )
    return ()


def _extract_initial_equity(data: RiskMetricsEngineInput, equity_samples: tuple[EquityRiskSample, ...]) -> float:
    for item in (
        _get(_runner(data), "metrics"),
        _get(_report(data), "metric_summary"),
        data.offline_simulation_metrics,
        _performance_summary(data),
    ):
        value = _get(item, "initial_equity")
        if _finite(value) and float(value) > 0:
            return float(value)
    if equity_samples:
        return equity_samples[0].equity
    return 0.0


def extract_risk_inputs(data: RiskMetricsEngineInput | Mapping[str, Any]) -> dict[str, Any]:
    data = _coerce_input(data)
    trade_samples = _extract_trade_risk_samples(data)
    equity_samples = _extract_equity_risk_samples(data)
    return {
        "performance_result": _performance_result(data),
        "performance_summary": _performance_summary(data),
        "runner": _runner(data),
        "report": _report(data),
        "trade_risk_samples": trade_samples,
        "equity_risk_samples": equity_samples,
        "position_risk_samples": _extract_position_risk_samples(data),
        "stop_condition_samples": _extract_stop_condition_samples(data),
        "thresholds": _thresholds(data),
        "initial_equity": _extract_initial_equity(data, equity_samples),
    }


def _equity_samples_valid(equity_samples: tuple[EquityRiskSample, ...]) -> bool:
    if not equity_samples:
        return False
    steps = tuple(sample.step for sample in equity_samples)
    return (
        len(set(steps)) == len(steps)
        and all(next_step > step for step, next_step in zip(steps, steps[1:]))
        and all(_finite(sample.equity) and sample.equity >= 0 for sample in equity_samples)
    )


def _position_samples_valid(position_samples: tuple[PositionRiskSample, ...]) -> bool:
    if not position_samples:
        return False
    return all(
        _finite(sample.quantity)
        and _finite(sample.price)
        and sample.price >= 0
        and _finite(sample.equity)
        and sample.equity >= 0
        for sample in position_samples
    )


def _stop_condition_samples_valid(stop_condition_samples: tuple[StopConditionRiskSample, ...]) -> bool:
    return bool(stop_condition_samples) and all(sample.configured for sample in stop_condition_samples)


def compute_max_loss(
    trade_risk_samples: tuple[TradeRiskSample, ...] = (),
    equity_risk_samples: tuple[EquityRiskSample, ...] = (),
    initial_equity: float = 0.0,
    performance_summary: Any = None,
) -> float:
    baseline = float(initial_equity or 0.0)
    if not baseline and equity_risk_samples:
        baseline = equity_risk_samples[0].equity
    equity_loss = 0.0
    if baseline and equity_risk_samples and all(_finite(sample.equity) for sample in equity_risk_samples):
        equity_loss = max(0.0, baseline - min(sample.equity for sample in equity_risk_samples))
    trade_loss = max((abs(sample.pnl) for sample in trade_risk_samples if sample.pnl < 0), default=0.0)
    summary_pnl = _get(performance_summary, "total_pnl")
    summary_loss = abs(float(summary_pnl)) if _finite(summary_pnl) and float(summary_pnl) < 0 else 0.0
    return _round(max(equity_loss, trade_loss, summary_loss))


def _compute_max_drawdown_amount_and_fraction(
    equity_risk_samples: tuple[EquityRiskSample, ...] = (),
    performance_summary: Any = None,
) -> tuple[float, float]:
    if equity_risk_samples and all(_finite(sample.equity) for sample in equity_risk_samples):
        peak = equity_risk_samples[0].equity
        max_drawdown = 0.0
        max_fraction = 0.0
        for sample in equity_risk_samples:
            peak = max(peak, sample.equity)
            drawdown = max(0.0, peak - sample.equity)
            fraction = drawdown / peak if peak else 0.0
            max_drawdown = max(max_drawdown, drawdown)
            max_fraction = max(max_fraction, fraction)
        return _round(max_drawdown), _round(max_fraction)
    if _finite(_get(performance_summary, "max_drawdown_fraction")):
        return _round(float(_get(performance_summary, "max_drawdown", 0.0) or 0.0)), _round(
            float(_get(performance_summary, "max_drawdown_fraction"))
        )
    return 0.0, 0.0


def compute_max_drawdown_fraction(
    equity_risk_samples: tuple[EquityRiskSample, ...] = (),
    performance_summary: Any = None,
) -> float:
    return _compute_max_drawdown_amount_and_fraction(equity_risk_samples, performance_summary)[1]


def compute_loss_limit_usage(
    max_loss: float,
    thresholds: RiskThresholds | None = None,
    max_loss_amount: float | None = None,
) -> float:
    limit = max_loss_amount if max_loss_amount is not None else _get(thresholds, "max_loss_amount", 0.0)
    if not _finite(max_loss) or max_loss < 0:
        return float("inf")
    if not _finite(limit) or float(limit) <= 0:
        return float("inf") if max_loss > 0 else 0.0
    return _round(max_loss / float(limit))


def compute_risk_per_trade(
    trade_risk_samples: tuple[TradeRiskSample, ...] = (),
    initial_equity: float = 0.0,
) -> float:
    if not trade_risk_samples or not _finite(initial_equity) or initial_equity <= 0:
        return 0.0
    per_trade_risks = []
    for sample in trade_risk_samples:
        explicit_risk = sample.risk_amount if _finite(sample.risk_amount) and sample.risk_amount > 0 else 0.0
        loss_risk = abs(sample.pnl) if sample.pnl < 0 else 0.0
        price_risk = abs(sample.entry_price - sample.exit_price) * abs(sample.quantity) if sample.entry_price and sample.exit_price else 0.0
        per_trade_risks.append(max(explicit_risk, loss_risk, price_risk))
    return _round(max(per_trade_risks, default=0.0) / float(initial_equity))


def compute_exposure_fraction(position_risk_samples: tuple[PositionRiskSample, ...] = ()) -> float:
    if not position_risk_samples:
        return 0.0
    exposures = []
    for sample in position_risk_samples:
        if _finite(sample.quantity) and _finite(sample.price) and _finite(sample.equity) and sample.equity > 0:
            exposures.append(abs(sample.quantity * sample.price) / sample.equity)
    return _round(max(exposures, default=0.0))


def compute_position_risk(position_risk_samples: tuple[PositionRiskSample, ...] = ()) -> float:
    if not position_risk_samples:
        return 0.0
    notionals = [
        abs(sample.quantity * sample.price)
        for sample in position_risk_samples
        if _finite(sample.quantity) and _finite(sample.price)
    ]
    return _round(max(notionals, default=0.0))


def compute_consecutive_loss_count(trade_risk_samples: tuple[TradeRiskSample, ...] = ()) -> int:
    max_count = 0
    current = 0
    for sample in trade_risk_samples:
        if sample.pnl < 0:
            current += 1
            max_count = max(max_count, current)
        else:
            current = 0
    return max_count


def compute_loss_stability_score(
    trade_risk_samples: tuple[TradeRiskSample, ...] = (),
    consecutive_loss_count: int | None = None,
) -> int:
    if not trade_risk_samples:
        return 0
    losses = [abs(sample.pnl) for sample in trade_risk_samples if sample.pnl < 0]
    if not losses:
        return 100
    consecutive = compute_consecutive_loss_count(trade_risk_samples) if consecutive_loss_count is None else consecutive_loss_count
    loss_rate = len(losses) / len(trade_risk_samples)
    consecutive_ratio = consecutive / len(trade_risk_samples)
    return _clamp(100 - (loss_rate * 45) - (consecutive_ratio * 45))


def compute_stop_condition_quality_score(
    stop_condition_samples: tuple[StopConditionRiskSample, ...] = (),
) -> int:
    if not stop_condition_samples:
        return 0
    scores = []
    for sample in stop_condition_samples:
        score = 100
        if not sample.configured:
            score -= 80
        if sample.triggered:
            score -= 25
        if sample.risks:
            score -= 25
        scores.append(_clamp(score))
    return _clamp(sum(scores) / len(scores))


def compute_risk_quality_score(
    summary: RiskMetricSummary,
    thresholds: RiskThresholds | None,
) -> int:
    if thresholds is None:
        return 0
    checks = (
        _finite(summary.max_loss) and summary.max_loss <= thresholds.max_loss_amount,
        _finite(summary.max_drawdown_fraction) and summary.max_drawdown_fraction <= thresholds.max_drawdown_fraction,
        _finite(summary.risk_per_trade_fraction) and summary.risk_per_trade_fraction <= thresholds.max_risk_per_trade_fraction,
        _finite(summary.exposure_fraction) and summary.exposure_fraction <= thresholds.max_exposure_fraction,
        _finite(summary.position_risk) and summary.position_risk <= thresholds.max_position_risk_amount,
        summary.consecutive_loss_count <= thresholds.max_consecutive_losses,
        summary.loss_stability_score >= thresholds.min_loss_stability_score,
        summary.stop_condition_quality_score >= thresholds.min_stop_condition_quality_score,
    )
    return _clamp(sum(100 for passed in checks if passed) / len(checks))


def _build_metric_summary(inputs: Mapping[str, Any]) -> RiskMetricSummary:
    trade_samples = tuple(inputs["trade_risk_samples"])
    equity_samples = tuple(inputs["equity_risk_samples"])
    position_samples = tuple(inputs["position_risk_samples"])
    stop_samples = tuple(inputs["stop_condition_samples"])
    thresholds = inputs["thresholds"]
    performance_summary = inputs["performance_summary"]
    initial_equity = float(inputs["initial_equity"] or 0.0)
    max_loss = compute_max_loss(trade_samples, equity_samples, initial_equity, performance_summary)
    max_drawdown_amount, max_drawdown_fraction = _compute_max_drawdown_amount_and_fraction(equity_samples, performance_summary)
    loss_limit_usage = compute_loss_limit_usage(max_loss, thresholds)
    risk_per_trade = compute_risk_per_trade(trade_samples, initial_equity)
    exposure_fraction = compute_exposure_fraction(position_samples)
    position_risk = compute_position_risk(position_samples)
    consecutive_losses = compute_consecutive_loss_count(trade_samples)
    loss_stability = compute_loss_stability_score(trade_samples, consecutive_losses)
    stop_quality = compute_stop_condition_quality_score(stop_samples)
    provisional = RiskMetricSummary(
        max_loss,
        max_drawdown_fraction,
        loss_limit_usage,
        risk_per_trade,
        exposure_fraction,
        position_risk,
        consecutive_losses,
        loss_stability,
        stop_quality,
        0,
        max_drawdown_amount,
    )
    quality = compute_risk_quality_score(provisional, thresholds)
    return RiskMetricSummary(
        max_loss,
        max_drawdown_fraction,
        loss_limit_usage,
        risk_per_trade,
        exposure_fraction,
        position_risk,
        consecutive_losses,
        loss_stability,
        stop_quality,
        quality,
        max_drawdown_amount,
    )


def _violation(
    name: str,
    passed: bool,
    risk: RiskMetricsEngineRisk,
    details: tuple[str, ...] = (),
    warning_score: int = 60,
) -> RiskValidationFinding:
    return RiskValidationFinding(name, passed, 100 if passed else warning_score, () if passed else (risk,), details)


def _all_threshold_findings(
    summary: RiskMetricSummary,
    thresholds: RiskThresholds | None,
) -> tuple[RiskValidationFinding, ...]:
    if not _thresholds_valid(thresholds):
        return (
            RiskValidationFinding(
                "thresholds",
                False,
                0,
                (RiskMetricsEngineRisk.RISK_THRESHOLD_MISSING,),
                ("risk thresholds are missing or invalid",),
            ),
        )
    assert thresholds is not None
    return (
        _violation(
            "max_loss",
            _finite(summary.max_loss) and summary.max_loss <= thresholds.max_loss_amount,
            RiskMetricsEngineRisk.LOSS_LIMIT_BREACHED,
            (f"max_loss={summary.max_loss}", f"limit={thresholds.max_loss_amount}"),
        ),
        _violation(
            "max_drawdown_fraction",
            _finite(summary.max_drawdown_fraction) and summary.max_drawdown_fraction <= thresholds.max_drawdown_fraction,
            RiskMetricsEngineRisk.DRAWDOWN_LIMIT_BREACHED,
            (f"drawdown={summary.max_drawdown_fraction}", f"limit={thresholds.max_drawdown_fraction}"),
        ),
        _violation(
            "risk_per_trade",
            _finite(summary.risk_per_trade_fraction)
            and summary.risk_per_trade_fraction <= thresholds.max_risk_per_trade_fraction,
            RiskMetricsEngineRisk.RISK_PER_TRADE_TOO_HIGH,
            (f"risk_per_trade={summary.risk_per_trade_fraction}", f"limit={thresholds.max_risk_per_trade_fraction}"),
        ),
        _violation(
            "exposure",
            _finite(summary.exposure_fraction) and summary.exposure_fraction <= thresholds.max_exposure_fraction,
            RiskMetricsEngineRisk.EXPOSURE_TOO_HIGH,
            (f"exposure={summary.exposure_fraction}", f"limit={thresholds.max_exposure_fraction}"),
        ),
        _violation(
            "position_risk",
            _finite(summary.position_risk) and summary.position_risk <= thresholds.max_position_risk_amount,
            RiskMetricsEngineRisk.EXPOSURE_TOO_HIGH,
            (f"position_risk={summary.position_risk}", f"limit={thresholds.max_position_risk_amount}"),
        ),
        _violation(
            "consecutive_losses",
            summary.consecutive_loss_count <= thresholds.max_consecutive_losses,
            RiskMetricsEngineRisk.CONSECUTIVE_LOSS_LIMIT_BREACHED,
            (f"consecutive_losses={summary.consecutive_loss_count}", f"limit={thresholds.max_consecutive_losses}"),
        ),
        _violation(
            "loss_stability",
            summary.loss_stability_score >= thresholds.min_loss_stability_score,
            RiskMetricsEngineRisk.LOSS_STABILITY_WEAK,
            (f"loss_stability={summary.loss_stability_score}", f"minimum={thresholds.min_loss_stability_score}"),
        ),
        _violation(
            "stop_condition_quality",
            summary.stop_condition_quality_score >= thresholds.min_stop_condition_quality_score,
            RiskMetricsEngineRisk.STOP_CONDITION_QUALITY_WEAK,
            (f"stop_condition_quality={summary.stop_condition_quality_score}", f"minimum={thresholds.min_stop_condition_quality_score}"),
        ),
        _violation(
            "risk_quality",
            summary.risk_quality_score >= thresholds.min_quality_score,
            RiskMetricsEngineRisk.LOSS_STABILITY_WEAK,
            (f"risk_quality={summary.risk_quality_score}", f"minimum={thresholds.min_quality_score}"),
        ),
    )


def detect_risk_metric_violations(
    summary: RiskMetricSummary,
    thresholds: RiskThresholds | None,
) -> tuple[RiskValidationFinding, ...]:
    return tuple(finding for finding in _all_threshold_findings(summary, thresholds) if not finding.passed)


def _metric_matches(value: float, expected: Any, tolerance: float) -> bool:
    if not _finite(value) or not _finite(expected):
        return False
    return _close(value, float(expected), tolerance)


def detect_risk_metric_risks(
    data: RiskMetricsEngineInput | Mapping[str, Any],
    risk_summary: RiskMetricSummary | None = None,
    inputs: Mapping[str, Any] | None = None,
) -> tuple[RiskMetricsEngineRisk, ...]:
    data = _coerce_input(data)
    inputs = extract_risk_inputs(data) if inputs is None else inputs
    risk_summary = _build_metric_summary(inputs) if risk_summary is None else risk_summary
    risks: list[RiskMetricsEngineRisk] = []
    performance_summary = inputs["performance_summary"]
    trade_samples = tuple(inputs["trade_risk_samples"])
    equity_samples = tuple(inputs["equity_risk_samples"])
    position_samples = tuple(inputs["position_risk_samples"])
    stop_samples = tuple(inputs["stop_condition_samples"])
    thresholds = inputs["thresholds"]
    if not validate_performance_metrics_result(data):
        risks.append(RiskMetricsEngineRisk.PERFORMANCE_METRICS_NOT_APPROVED)
    if performance_summary is None:
        risks.append(RiskMetricsEngineRisk.RISK_INPUT_MISSING)
    if not trade_samples:
        risks.append(RiskMetricsEngineRisk.TRADE_RISK_SAMPLE_EMPTY)
    if not _equity_samples_valid(equity_samples):
        risks.append(RiskMetricsEngineRisk.EQUITY_RISK_SAMPLE_INVALID)
    if not _position_samples_valid(position_samples):
        risks.append(RiskMetricsEngineRisk.POSITION_RISK_SAMPLE_INVALID)
    if not _stop_condition_samples_valid(stop_samples):
        risks.append(RiskMetricsEngineRisk.STOP_CONDITION_SAMPLE_INVALID)
    if not _thresholds_valid(thresholds):
        risks.append(RiskMetricsEngineRisk.RISK_THRESHOLD_MISSING)
    if not _finite(risk_summary.max_loss) or risk_summary.max_loss < 0:
        risks.append(RiskMetricsEngineRisk.MAX_LOSS_INVALID)
    if (
        not _finite(risk_summary.max_drawdown_fraction)
        or risk_summary.max_drawdown_fraction < 0
        or (
            performance_summary is not None
            and _finite(_get(performance_summary, "max_drawdown_fraction"))
            and not _metric_matches(
                risk_summary.max_drawdown_fraction,
                _get(performance_summary, "max_drawdown_fraction"),
                data.metric_tolerance,
            )
        )
    ):
        risks.append(RiskMetricsEngineRisk.MAX_DRAWDOWN_INVALID)
    for violation in detect_risk_metric_violations(risk_summary, thresholds):
        risks.extend(violation.risks)
    if not _offline_boundary(data):
        risks.append(RiskMetricsEngineRisk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(RiskMetricsEngineRisk.DATA_ACCESS_VIOLATION)
    if data.performance_risk_validation_gate_requested is True:
        risks.append(RiskMetricsEngineRisk.PREMATURE_PERFORMANCE_RISK_VALIDATION_GATE)
    return _dedupe(risks)


def _finding(
    name: str,
    passed: bool,
    risk: RiskMetricsEngineRisk,
    details: tuple[str, ...] = (),
    warning_score: int = 60,
) -> RiskValidationFinding:
    return RiskValidationFinding(name, passed, 100 if passed else warning_score, () if passed else (risk,), details)


def _build_findings(
    data: RiskMetricsEngineInput,
    summary: RiskMetricSummary,
    inputs: Mapping[str, Any],
) -> tuple[RiskValidationFinding, ...]:
    trade_samples = tuple(inputs["trade_risk_samples"])
    equity_samples = tuple(inputs["equity_risk_samples"])
    position_samples = tuple(inputs["position_risk_samples"])
    stop_samples = tuple(inputs["stop_condition_samples"])
    thresholds = inputs["thresholds"]
    base_findings = (
        _finding(
            "performance_metrics",
            validate_performance_metrics_result(data),
            RiskMetricsEngineRisk.PERFORMANCE_METRICS_NOT_APPROVED,
        ),
        _finding(
            "trade_risk_samples",
            bool(trade_samples),
            RiskMetricsEngineRisk.TRADE_RISK_SAMPLE_EMPTY,
            (f"count={len(trade_samples)}",),
        ),
        _finding(
            "equity_risk_samples",
            _equity_samples_valid(equity_samples),
            RiskMetricsEngineRisk.EQUITY_RISK_SAMPLE_INVALID,
            (f"count={len(equity_samples)}",),
        ),
        _finding(
            "position_risk_samples",
            _position_samples_valid(position_samples),
            RiskMetricsEngineRisk.POSITION_RISK_SAMPLE_INVALID,
            (f"count={len(position_samples)}",),
        ),
        _finding(
            "stop_condition_samples",
            _stop_condition_samples_valid(stop_samples),
            RiskMetricsEngineRisk.STOP_CONDITION_SAMPLE_INVALID,
            (f"count={len(stop_samples)}",),
        ),
        _finding("thresholds", _thresholds_valid(thresholds), RiskMetricsEngineRisk.RISK_THRESHOLD_MISSING),
        _finding("max_loss_valid", _finite(summary.max_loss) and summary.max_loss >= 0, RiskMetricsEngineRisk.MAX_LOSS_INVALID),
        _finding(
            "max_drawdown_valid",
            _finite(summary.max_drawdown_fraction) and summary.max_drawdown_fraction >= 0,
            RiskMetricsEngineRisk.MAX_DRAWDOWN_INVALID,
        ),
    )
    return base_findings + _all_threshold_findings(summary, thresholds)


def _finding_score(findings: tuple[RiskValidationFinding, ...], name: str) -> int:
    for finding in findings:
        if finding.name == name:
            return finding.score
    return 0


def _compute_engine_score(
    data: RiskMetricsEngineInput,
    risks: tuple[RiskMetricsEngineRisk, ...],
    findings: tuple[RiskValidationFinding, ...],
) -> RiskMetricsEngineScore:
    performance_metrics_score = _finding_score(findings, "performance_metrics")
    risk_sample_score = _finding_score(findings, "trade_risk_samples")
    equity_sample_score = _finding_score(findings, "equity_risk_samples")
    position_sample_score = _finding_score(findings, "position_risk_samples")
    stop_condition_score = _finding_score(findings, "stop_condition_samples")
    threshold_score = _finding_score(findings, "thresholds")
    max_loss_score = min(_finding_score(findings, "max_loss_valid"), _finding_score(findings, "max_loss"))
    drawdown_score = min(_finding_score(findings, "max_drawdown_valid"), _finding_score(findings, "max_drawdown_fraction"))
    risk_per_trade_score = _finding_score(findings, "risk_per_trade")
    exposure_score = min(_finding_score(findings, "exposure"), _finding_score(findings, "position_risk"))
    consecutive_loss_score = _finding_score(findings, "consecutive_losses")
    loss_stability_score = min(_finding_score(findings, "loss_stability"), _finding_score(findings, "risk_quality"))
    boundary_score = 100 if _offline_boundary(data) and _data_boundary(data) else 0
    values = (
        performance_metrics_score,
        risk_sample_score,
        equity_sample_score,
        position_sample_score,
        stop_condition_score,
        threshold_score,
        max_loss_score,
        drawdown_score,
        risk_per_trade_score,
        exposure_score,
        consecutive_loss_score,
        loss_stability_score,
        boundary_score,
    )
    overall = _clamp(sum(values) / len(values) - min(80, len(set(risks)) * 4))
    for risk, cap in {
        RiskMetricsEngineRisk.PERFORMANCE_METRICS_NOT_APPROVED: 50,
        RiskMetricsEngineRisk.RISK_INPUT_MISSING: 45,
        RiskMetricsEngineRisk.TRADE_RISK_SAMPLE_EMPTY: 55,
        RiskMetricsEngineRisk.EQUITY_RISK_SAMPLE_INVALID: 50,
        RiskMetricsEngineRisk.POSITION_RISK_SAMPLE_INVALID: 50,
        RiskMetricsEngineRisk.STOP_CONDITION_SAMPLE_INVALID: 55,
        RiskMetricsEngineRisk.MAX_LOSS_INVALID: 55,
        RiskMetricsEngineRisk.MAX_DRAWDOWN_INVALID: 55,
        RiskMetricsEngineRisk.LOSS_LIMIT_BREACHED: 70,
        RiskMetricsEngineRisk.DRAWDOWN_LIMIT_BREACHED: 70,
        RiskMetricsEngineRisk.RISK_PER_TRADE_TOO_HIGH: 70,
        RiskMetricsEngineRisk.EXPOSURE_TOO_HIGH: 70,
        RiskMetricsEngineRisk.CONSECUTIVE_LOSS_LIMIT_BREACHED: 70,
        RiskMetricsEngineRisk.LOSS_STABILITY_WEAK: 75,
        RiskMetricsEngineRisk.STOP_CONDITION_QUALITY_WEAK: 75,
        RiskMetricsEngineRisk.RISK_THRESHOLD_MISSING: 55,
        RiskMetricsEngineRisk.REAL_EXECUTION_BOUNDARY_VIOLATION: 35,
        RiskMetricsEngineRisk.DATA_ACCESS_VIOLATION: 35,
        RiskMetricsEngineRisk.PREMATURE_PERFORMANCE_RISK_VALIDATION_GATE: 40,
    }.items():
        if risk in risks:
            overall = min(overall, cap)
    return RiskMetricsEngineScore(
        overall,
        performance_metrics_score,
        risk_sample_score,
        equity_sample_score,
        position_sample_score,
        stop_condition_score,
        threshold_score,
        max_loss_score,
        drawdown_score,
        risk_per_trade_score,
        exposure_score,
        consecutive_loss_score,
        loss_stability_score,
        boundary_score,
    )


def _select_decision(risks: tuple[RiskMetricsEngineRisk, ...]) -> RiskMetricsEngineDecision:
    if (
        RiskMetricsEngineRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in risks
        or RiskMetricsEngineRisk.DATA_ACCESS_VIOLATION in risks
        or RiskMetricsEngineRisk.PREMATURE_PERFORMANCE_RISK_VALIDATION_GATE in risks
    ):
        return RiskMetricsEngineDecision.BLOCK_RISK_METRICS
    if (
        RiskMetricsEngineRisk.PERFORMANCE_METRICS_NOT_APPROVED in risks
        or RiskMetricsEngineRisk.RISK_INPUT_MISSING in risks
    ):
        return RiskMetricsEngineDecision.REQUIRE_PERFORMANCE_METRICS_FIXES
    if RiskMetricsEngineRisk.TRADE_RISK_SAMPLE_EMPTY in risks or RiskMetricsEngineRisk.STOP_CONDITION_SAMPLE_INVALID in risks:
        return RiskMetricsEngineDecision.REQUIRE_RISK_SAMPLE_FIXES
    if RiskMetricsEngineRisk.EQUITY_RISK_SAMPLE_INVALID in risks:
        return RiskMetricsEngineDecision.REQUIRE_EQUITY_SAMPLE_FIXES
    if RiskMetricsEngineRisk.POSITION_RISK_SAMPLE_INVALID in risks:
        return RiskMetricsEngineDecision.REQUIRE_POSITION_SAMPLE_FIXES
    if RiskMetricsEngineRisk.RISK_THRESHOLD_MISSING in risks:
        return RiskMetricsEngineDecision.REQUIRE_THRESHOLD_FIXES
    if risks:
        return RiskMetricsEngineDecision.REQUIRE_RISK_REVIEW
    return RiskMetricsEngineDecision.APPROVE_RISK_METRICS_ENGINE


def _select_state(
    decision: RiskMetricsEngineDecision,
    risks: tuple[RiskMetricsEngineRisk, ...],
    score: int,
) -> RiskMetricsEngineState:
    if decision == RiskMetricsEngineDecision.BLOCK_RISK_METRICS:
        return RiskMetricsEngineState.RISK_METRICS_BLOCKED
    if decision in {
        RiskMetricsEngineDecision.REQUIRE_PERFORMANCE_METRICS_FIXES,
        RiskMetricsEngineDecision.REQUIRE_RISK_SAMPLE_FIXES,
        RiskMetricsEngineDecision.REQUIRE_EQUITY_SAMPLE_FIXES,
        RiskMetricsEngineDecision.REQUIRE_POSITION_SAMPLE_FIXES,
        RiskMetricsEngineDecision.REQUIRE_THRESHOLD_FIXES,
    }:
        return RiskMetricsEngineState.INPUT_INVALID
    if risks:
        return RiskMetricsEngineState.RISK_METRICS_COMPLETED_WITH_WARNINGS
    if score >= 95:
        return RiskMetricsEngineState.READY_FOR_PERFORMANCE_RISK_VALIDATION_GATE
    return RiskMetricsEngineState.RISK_METRICS_COMPLETED


def generate_risk_metric_recommendations(
    risks: tuple[RiskMetricsEngineRisk, ...],
    decision: RiskMetricsEngineDecision | None = None,
) -> tuple[RiskMetricsEngineRecommendation, ...]:
    recommendations: list[RiskMetricsEngineRecommendation] = []
    if risks:
        recommendations.append(RiskMetricsEngineRecommendation.HOLD_PERFORMANCE_RISK_VALIDATION_GATE)
    mapping = {
        RiskMetricsEngineRisk.PERFORMANCE_METRICS_NOT_APPROVED: RiskMetricsEngineRecommendation.APPROVE_PERFORMANCE_METRICS_FIRST,
        RiskMetricsEngineRisk.RISK_INPUT_MISSING: RiskMetricsEngineRecommendation.PROVIDE_RISK_INPUTS,
        RiskMetricsEngineRisk.TRADE_RISK_SAMPLE_EMPTY: RiskMetricsEngineRecommendation.PROVIDE_TRADE_RISK_SAMPLES,
        RiskMetricsEngineRisk.EQUITY_RISK_SAMPLE_INVALID: RiskMetricsEngineRecommendation.REBUILD_EQUITY_RISK_SAMPLES,
        RiskMetricsEngineRisk.POSITION_RISK_SAMPLE_INVALID: RiskMetricsEngineRecommendation.REBUILD_POSITION_RISK_SAMPLES,
        RiskMetricsEngineRisk.STOP_CONDITION_SAMPLE_INVALID: RiskMetricsEngineRecommendation.REBUILD_STOP_CONDITION_SAMPLES,
        RiskMetricsEngineRisk.MAX_LOSS_INVALID: RiskMetricsEngineRecommendation.RECHECK_MAX_LOSS,
        RiskMetricsEngineRisk.MAX_DRAWDOWN_INVALID: RiskMetricsEngineRecommendation.RECHECK_MAX_DRAWDOWN,
        RiskMetricsEngineRisk.LOSS_LIMIT_BREACHED: RiskMetricsEngineRecommendation.REDUCE_LOSS_LIMIT_USAGE,
        RiskMetricsEngineRisk.DRAWDOWN_LIMIT_BREACHED: RiskMetricsEngineRecommendation.REDUCE_DRAWDOWN,
        RiskMetricsEngineRisk.RISK_PER_TRADE_TOO_HIGH: RiskMetricsEngineRecommendation.REDUCE_RISK_PER_TRADE,
        RiskMetricsEngineRisk.EXPOSURE_TOO_HIGH: RiskMetricsEngineRecommendation.REDUCE_EXPOSURE,
        RiskMetricsEngineRisk.CONSECUTIVE_LOSS_LIMIT_BREACHED: RiskMetricsEngineRecommendation.REDUCE_CONSECUTIVE_LOSSES,
        RiskMetricsEngineRisk.LOSS_STABILITY_WEAK: RiskMetricsEngineRecommendation.IMPROVE_LOSS_STABILITY,
        RiskMetricsEngineRisk.STOP_CONDITION_QUALITY_WEAK: RiskMetricsEngineRecommendation.IMPROVE_STOP_CONDITION_QUALITY,
        RiskMetricsEngineRisk.RISK_THRESHOLD_MISSING: RiskMetricsEngineRecommendation.DEFINE_RISK_THRESHOLDS,
        RiskMetricsEngineRisk.REAL_EXECUTION_BOUNDARY_VIOLATION: RiskMetricsEngineRecommendation.RESTORE_REAL_EXECUTION_BOUNDARIES,
        RiskMetricsEngineRisk.DATA_ACCESS_VIOLATION: RiskMetricsEngineRecommendation.REMOVE_DATA_ACCESS,
        RiskMetricsEngineRisk.PREMATURE_PERFORMANCE_RISK_VALIDATION_GATE: RiskMetricsEngineRecommendation.DELAY_PERFORMANCE_RISK_VALIDATION_GATE,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(RiskMetricsEngineRecommendation.RUN_RISK_METRICS_ENGINE_SUITE)
    if decision == RiskMetricsEngineDecision.APPROVE_RISK_METRICS_ENGINE:
        recommendations.append(RiskMetricsEngineRecommendation.APPROVE_PERFORMANCE_RISK_VALIDATION_GATE)
    return _dedupe(recommendations)


def evaluate_risk_metrics_engine(data: RiskMetricsEngineInput | Mapping[str, Any]) -> RiskMetricsEngineResult:
    data = _coerce_input(data)
    inputs = extract_risk_inputs(data)
    thresholds = inputs["thresholds"] or RiskThresholds()
    trade_samples = tuple(inputs["trade_risk_samples"])
    equity_samples = tuple(inputs["equity_risk_samples"])
    position_samples = tuple(inputs["position_risk_samples"])
    stop_samples = tuple(inputs["stop_condition_samples"])
    metric_summary = _build_metric_summary(inputs)
    risks = detect_risk_metric_risks(data, metric_summary, inputs)
    violations = detect_risk_metric_violations(metric_summary, inputs["thresholds"])
    findings = _build_findings(data, metric_summary, inputs)
    score = _compute_engine_score(data, risks, findings)
    decision = _select_decision(risks)
    state = _select_state(decision, risks, score.overall_score)
    recommendations = generate_risk_metric_recommendations(risks, decision)
    offline_only = _offline_boundary(data) and _data_boundary(data)
    summary = (
        f"{state.value}: decision={decision.value}, score={score.overall_score}, "
        f"risks={len(risks)}, max_loss={metric_summary.max_loss}, drawdown={metric_summary.max_drawdown_fraction}"
    )
    return RiskMetricsEngineResult(
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
        position_samples,
        stop_samples,
        violations,
        findings,
        offline_only,
        summary,
    )


def render_risk_metrics_engine_markdown(result: RiskMetricsEngineResult) -> str:
    risks = "\n".join(f"- {risk.value}" for risk in result.risks) or "- None"
    violations = "\n".join(f"- {finding.name}: {', '.join(risk.value for risk in finding.risks)}" for finding in result.violations) or "- None"
    recommendations = "\n".join(f"- {item.value}" for item in result.recommendations) or "- None"
    findings = "\n".join(f"- {finding.name}: {'PASS' if finding.passed else 'FAIL'} ({finding.score})" for finding in result.findings)
    summary = result.metric_summary
    return "\n".join(
        (
            "# AGIcore Risk Metrics Engine",
            "",
            f"State: {result.state.value}",
            f"Decision: {result.decision.value}",
            f"Score: {result.engine_score}",
            f"Offline only: {result.offline_only}",
            "",
            "## Risk Metrics",
            f"Max loss: {summary.max_loss}",
            f"Max drawdown fraction: {summary.max_drawdown_fraction}",
            f"Loss limit usage: {summary.loss_limit_usage}",
            f"Risk per trade fraction: {summary.risk_per_trade_fraction}",
            f"Exposure fraction: {summary.exposure_fraction}",
            f"Position risk: {summary.position_risk}",
            f"Consecutive loss count: {summary.consecutive_loss_count}",
            f"Loss stability score: {summary.loss_stability_score}",
            f"Stop condition quality score: {summary.stop_condition_quality_score}",
            f"Risk quality score: {summary.risk_quality_score}",
            "",
            "## Violations",
            violations,
            "",
            "## Risks",
            risks,
            "",
            "## Recommendations",
            recommendations,
            "",
            "## Findings",
            findings,
        )
    )


__all__ = [
    "evaluate_risk_metrics_engine",
    "validate_performance_metrics_result",
    "extract_risk_inputs",
    "compute_max_loss",
    "compute_max_drawdown_fraction",
    "compute_loss_limit_usage",
    "compute_risk_per_trade",
    "compute_exposure_fraction",
    "compute_position_risk",
    "compute_consecutive_loss_count",
    "compute_loss_stability_score",
    "compute_stop_condition_quality_score",
    "compute_risk_quality_score",
    "detect_risk_metric_violations",
    "detect_risk_metric_risks",
    "generate_risk_metric_recommendations",
    "render_risk_metrics_engine_markdown",
]
