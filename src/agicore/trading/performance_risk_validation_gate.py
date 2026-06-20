"""Offline gate combining performance and risk metrics validation."""

from __future__ import annotations

import math
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.performance_risk_validation_gate_models import (
    PerformanceRiskValidationFinding,
    PerformanceRiskValidationGateDecision,
    PerformanceRiskValidationGateInput,
    PerformanceRiskValidationGateRecommendation,
    PerformanceRiskValidationGateResult,
    PerformanceRiskValidationGateRisk,
    PerformanceRiskValidationGateScore,
    PerformanceRiskValidationGateState,
    PerformanceRiskValidationSummary,
    PerformanceRiskValidationThresholds,
)


def _coerce_input(
    data: PerformanceRiskValidationGateInput | Mapping[str, Any],
) -> PerformanceRiskValidationGateInput:
    if isinstance(data, PerformanceRiskValidationGateInput):
        return data
    allowed = {field.name for field in fields(PerformanceRiskValidationGateInput)}
    payload = {key: value for key, value in dict(data).items() if key in allowed}
    return PerformanceRiskValidationGateInput(**payload)


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


def _finite(value: Any) -> bool:
    return isinstance(value, int | float) and math.isfinite(float(value))


def _numeric_or_inf(value: Any) -> bool:
    return isinstance(value, int | float) and not math.isnan(float(value))


def _clamp(value: int | float, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(round(value))))


def _thresholds(data: PerformanceRiskValidationGateInput) -> PerformanceRiskValidationThresholds | None:
    if data.thresholds is None:
        return None
    if isinstance(data.thresholds, PerformanceRiskValidationThresholds):
        return data.thresholds
    allowed = {field.name for field in fields(PerformanceRiskValidationThresholds)}
    payload = {key: value for key, value in dict(data.thresholds).items() if key in allowed}
    return PerformanceRiskValidationThresholds(**payload)


def _thresholds_valid(thresholds: PerformanceRiskValidationThresholds | None) -> bool:
    return (
        thresholds is not None
        and thresholds.min_trade_count >= 0
        and thresholds.max_drawdown_fraction >= 0
        and 0 <= thresholds.min_win_rate <= 1
        and thresholds.min_profit_factor >= 0
        and thresholds.max_risk_per_trade_fraction >= 0
        and thresholds.max_exposure_fraction >= 0
        and thresholds.max_loss_limit_usage >= 0
        and 0 <= thresholds.min_performance_stability_score <= 100
        and 0 <= thresholds.min_risk_stability_score <= 100
        and 0 <= thresholds.min_performance_quality_score <= 100
        and 0 <= thresholds.min_risk_quality_score <= 100
        and thresholds.max_rule_violation_count >= 0
        and 0 <= thresholds.min_gate_score <= 100
    )


def _performance_summary(data: PerformanceRiskValidationGateInput) -> Any:
    return data.performance_metric_summary or _get(data.performance_metrics_result, "metric_summary")


def _risk_summary(data: PerformanceRiskValidationGateInput) -> Any:
    return data.risk_metric_summary or _get(data.risk_metrics_result, "metric_summary")


def _upstream_items(data: PerformanceRiskValidationGateInput) -> tuple[Any, ...]:
    return (
        data.performance_metrics_result,
        data.risk_metrics_result,
        data.performance_metric_summary,
        data.risk_metric_summary,
        data.performance_thresholds,
        data.risk_thresholds,
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


def _upstream_risks(data: PerformanceRiskValidationGateInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PerformanceRiskValidationGateInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _offline_boundary(data: PerformanceRiskValidationGateInput) -> bool:
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


def _data_boundary(data: PerformanceRiskValidationGateInput) -> bool:
    return (
        data.synthetic_data_only is True
        and data.in_memory_only is True
        and data.data_access_requested is not True
        and not _has_upstream_risk(data, "DATA_ACCESS", "DATA_ACCESS_VIOLATION", "REAL_DATA")
    )


def validate_performance_metrics_approval(
    data: PerformanceRiskValidationGateInput | Mapping[str, Any],
) -> bool:
    data = _coerce_input(data)
    result = data.performance_metrics_result
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
            "PROFIT_FACTOR_INVALID",
            "EXPECTANCY_INVALID",
            "REAL_EXECUTION_BOUNDARY_VIOLATION",
            "DATA_ACCESS_VIOLATION",
            "PREMATURE_RISK_METRICS_ENGINE",
        )
    )


def validate_risk_metrics_approval(
    data: PerformanceRiskValidationGateInput | Mapping[str, Any],
) -> bool:
    data = _coerce_input(data)
    result = data.risk_metrics_result
    if result is None:
        return False
    approved = (
        data.risk_metrics_approved is not False
        and (
            data.risk_metrics_approved is True
            or _state_contains(
                result,
                "READY_FOR_PERFORMANCE_RISK_VALIDATION_GATE",
                "APPROVE_RISK_METRICS_ENGINE",
            )
        )
    )
    return (
        approved
        and _get(result, "offline_only", True) is True
        and not _contains(
            _get(result, "risks", ()),
            "PERFORMANCE_METRICS_NOT_APPROVED",
            "RISK_INPUT_MISSING",
            "TRADE_RISK_SAMPLE_EMPTY",
            "EQUITY_RISK_SAMPLE_INVALID",
            "POSITION_RISK_SAMPLE_INVALID",
            "STOP_CONDITION_SAMPLE_INVALID",
            "MAX_LOSS_INVALID",
            "MAX_DRAWDOWN_INVALID",
            "REAL_EXECUTION_BOUNDARY_VIOLATION",
            "DATA_ACCESS_VIOLATION",
            "PREMATURE_PERFORMANCE_RISK_VALIDATION_GATE",
        )
    )


def _make_finding(
    name: str,
    passed: bool,
    risk: PerformanceRiskValidationGateRisk,
    details: tuple[str, ...] = (),
    warning_score: int = 60,
) -> PerformanceRiskValidationFinding:
    return PerformanceRiskValidationFinding(name, passed, 100 if passed else warning_score, () if passed else (risk,), details)


def evaluate_pnl_validation(
    performance_summary: Any,
    thresholds: PerformanceRiskValidationThresholds | None,
) -> PerformanceRiskValidationFinding:
    value = _get(performance_summary, "total_pnl")
    passed = thresholds is not None and _finite(value) and float(value) >= thresholds.min_total_pnl
    return _make_finding("pnl", passed, PerformanceRiskValidationGateRisk.PNL_VALIDATION_FAILED, (f"total_pnl={value}",))


def evaluate_return_validation(
    performance_summary: Any,
    thresholds: PerformanceRiskValidationThresholds | None,
) -> PerformanceRiskValidationFinding:
    value = _get(performance_summary, "return_fraction")
    passed = thresholds is not None and _finite(value) and float(value) >= thresholds.min_return_fraction
    return _make_finding("return", passed, PerformanceRiskValidationGateRisk.RETURN_VALIDATION_FAILED, (f"return_fraction={value}",))


def evaluate_drawdown_validation(
    performance_summary: Any,
    risk_summary: Any,
    thresholds: PerformanceRiskValidationThresholds | None,
) -> PerformanceRiskValidationFinding:
    values = [
        float(value)
        for value in (
            _get(performance_summary, "max_drawdown_fraction"),
            _get(risk_summary, "max_drawdown_fraction"),
        )
        if _finite(value)
    ]
    drawdown = max(values) if values else math.inf
    passed = thresholds is not None and math.isfinite(drawdown) and drawdown <= thresholds.max_drawdown_fraction
    return _make_finding(
        "drawdown",
        passed,
        PerformanceRiskValidationGateRisk.DRAWDOWN_VALIDATION_FAILED,
        (f"max_drawdown_fraction={drawdown}",),
    )


def evaluate_profit_factor_validation(
    performance_summary: Any,
    thresholds: PerformanceRiskValidationThresholds | None,
) -> PerformanceRiskValidationFinding:
    value = _get(performance_summary, "profit_factor")
    passed = thresholds is not None and _numeric_or_inf(value) and float(value) >= thresholds.min_profit_factor
    return _make_finding(
        "profit_factor",
        passed,
        PerformanceRiskValidationGateRisk.PROFIT_FACTOR_VALIDATION_FAILED,
        (f"profit_factor={value}",),
    )


def evaluate_expectancy_validation(
    performance_summary: Any,
    thresholds: PerformanceRiskValidationThresholds | None,
) -> PerformanceRiskValidationFinding:
    value = _get(performance_summary, "expectancy")
    passed = thresholds is not None and _finite(value) and float(value) >= thresholds.min_expectancy
    return _make_finding("expectancy", passed, PerformanceRiskValidationGateRisk.EXPECTANCY_VALIDATION_FAILED, (f"expectancy={value}",))


def evaluate_trade_count_validation(
    performance_summary: Any,
    thresholds: PerformanceRiskValidationThresholds | None,
) -> PerformanceRiskValidationFinding:
    value = int(_get(performance_summary, "trade_count", 0) or 0)
    passed = thresholds is not None and value >= thresholds.min_trade_count
    return _make_finding("trade_count", passed, PerformanceRiskValidationGateRisk.TRADE_COUNT_TOO_LOW, (f"trade_count={value}",))


def evaluate_win_rate_validation(
    performance_summary: Any,
    thresholds: PerformanceRiskValidationThresholds | None,
) -> PerformanceRiskValidationFinding:
    value = _get(performance_summary, "win_rate")
    passed = thresholds is not None and _finite(value) and float(value) >= thresholds.min_win_rate
    return _make_finding(
        "win_rate",
        passed,
        PerformanceRiskValidationGateRisk.WIN_RATE_VALIDATION_WARNING,
        (f"win_rate={value}",),
        warning_score=75,
    )


def evaluate_risk_per_trade_validation(
    risk_summary: Any,
    thresholds: PerformanceRiskValidationThresholds | None,
) -> PerformanceRiskValidationFinding:
    value = _get(risk_summary, "risk_per_trade_fraction")
    passed = thresholds is not None and _finite(value) and float(value) <= thresholds.max_risk_per_trade_fraction
    return _make_finding(
        "risk_per_trade",
        passed,
        PerformanceRiskValidationGateRisk.RISK_PER_TRADE_TOO_HIGH,
        (f"risk_per_trade_fraction={value}",),
    )


def evaluate_exposure_validation(
    risk_summary: Any,
    thresholds: PerformanceRiskValidationThresholds | None,
) -> PerformanceRiskValidationFinding:
    value = _get(risk_summary, "exposure_fraction")
    passed = thresholds is not None and _finite(value) and float(value) <= thresholds.max_exposure_fraction
    return _make_finding("exposure", passed, PerformanceRiskValidationGateRisk.EXPOSURE_TOO_HIGH, (f"exposure_fraction={value}",))


def evaluate_loss_limit_validation(
    risk_summary: Any,
    thresholds: PerformanceRiskValidationThresholds | None,
) -> PerformanceRiskValidationFinding:
    value = _get(risk_summary, "loss_limit_usage")
    passed = thresholds is not None and _numeric_or_inf(value) and float(value) <= thresholds.max_loss_limit_usage
    return _make_finding(
        "loss_limit",
        passed,
        PerformanceRiskValidationGateRisk.LOSS_LIMIT_USAGE_TOO_HIGH,
        (f"loss_limit_usage={value}",),
    )


def evaluate_stability_validation(
    performance_summary: Any,
    risk_summary: Any,
    thresholds: PerformanceRiskValidationThresholds | None,
) -> PerformanceRiskValidationFinding:
    performance_stability = int(_get(performance_summary, "stability_score", 0) or 0)
    performance_quality = int(_get(performance_summary, "quality_score", 0) or 0)
    risk_stability = int(_get(risk_summary, "loss_stability_score", 0) or 0)
    risk_quality = int(_get(risk_summary, "risk_quality_score", 0) or 0)
    passed = (
        thresholds is not None
        and performance_stability >= thresholds.min_performance_stability_score
        and performance_quality >= thresholds.min_performance_quality_score
        and risk_stability >= thresholds.min_risk_stability_score
        and risk_quality >= thresholds.min_risk_quality_score
    )
    return _make_finding(
        "stability",
        passed,
        PerformanceRiskValidationGateRisk.STABILITY_VALIDATION_FAILED,
        (
            f"performance_stability={performance_stability}",
            f"performance_quality={performance_quality}",
            f"risk_stability={risk_stability}",
            f"risk_quality={risk_quality}",
        ),
    )


def evaluate_rule_violation_validation(
    risk_metrics_result: Any,
    thresholds: PerformanceRiskValidationThresholds | None,
) -> PerformanceRiskValidationFinding:
    violations = tuple(_as_tuple(_get(risk_metrics_result, "violations", ())))
    risk_items = tuple(_as_tuple(_get(risk_metrics_result, "risks", ())))
    violation_count = len(violations) + sum(
        1
        for risk in risk_items
        if _contains(
            (risk,),
            "LOSS_LIMIT_BREACHED",
            "DRAWDOWN_LIMIT_BREACHED",
            "RISK_PER_TRADE_TOO_HIGH",
            "EXPOSURE_TOO_HIGH",
            "CONSECUTIVE_LOSS_LIMIT_BREACHED",
            "RULE",
        )
    )
    passed = thresholds is not None and violation_count <= thresholds.max_rule_violation_count
    return _make_finding(
        "rule_violations",
        passed,
        PerformanceRiskValidationGateRisk.RULE_VIOLATION_DETECTED,
        (f"rule_violation_count={violation_count}",),
    )


def _build_summary(
    performance_summary: Any,
    risk_summary: Any,
    risk_metrics_result: Any,
) -> PerformanceRiskValidationSummary:
    rule_violation_finding = evaluate_rule_violation_validation(risk_metrics_result, PerformanceRiskValidationThresholds())
    count_text = rule_violation_finding.details[0].split("=")[-1] if rule_violation_finding.details else "0"
    return PerformanceRiskValidationSummary(
        total_pnl=float(_get(performance_summary, "total_pnl", 0.0) or 0.0),
        return_fraction=float(_get(performance_summary, "return_fraction", 0.0) or 0.0),
        max_drawdown_fraction=max(
            float(_get(performance_summary, "max_drawdown_fraction", 0.0) or 0.0),
            float(_get(risk_summary, "max_drawdown_fraction", 0.0) or 0.0),
        ),
        profit_factor=float(_get(performance_summary, "profit_factor", 0.0) or 0.0),
        expectancy=float(_get(performance_summary, "expectancy", 0.0) or 0.0),
        trade_count=int(_get(performance_summary, "trade_count", 0) or 0),
        win_rate=float(_get(performance_summary, "win_rate", 0.0) or 0.0),
        risk_per_trade_fraction=float(_get(risk_summary, "risk_per_trade_fraction", 0.0) or 0.0),
        exposure_fraction=float(_get(risk_summary, "exposure_fraction", 0.0) or 0.0),
        loss_limit_usage=float(_get(risk_summary, "loss_limit_usage", 0.0) or 0.0),
        performance_stability_score=int(_get(performance_summary, "stability_score", 0) or 0),
        risk_stability_score=int(_get(risk_summary, "loss_stability_score", 0) or 0),
        performance_quality_score=int(_get(performance_summary, "quality_score", 0) or 0),
        risk_quality_score=int(_get(risk_summary, "risk_quality_score", 0) or 0),
        rule_violation_count=int(count_text),
    )


def _approval_findings(
    data: PerformanceRiskValidationGateInput,
    thresholds: PerformanceRiskValidationThresholds | None,
) -> tuple[PerformanceRiskValidationFinding, ...]:
    return (
        _make_finding(
            "performance_approval",
            validate_performance_metrics_approval(data),
            PerformanceRiskValidationGateRisk.PERFORMANCE_METRICS_NOT_APPROVED,
        ),
        _make_finding(
            "risk_approval",
            validate_risk_metrics_approval(data),
            PerformanceRiskValidationGateRisk.RISK_METRICS_NOT_APPROVED,
        ),
        _make_finding(
            "thresholds",
            _thresholds_valid(thresholds),
            PerformanceRiskValidationGateRisk.VALIDATION_THRESHOLD_MISSING,
        ),
    )


def _build_findings(
    data: PerformanceRiskValidationGateInput,
    thresholds: PerformanceRiskValidationThresholds | None,
) -> tuple[PerformanceRiskValidationFinding, ...]:
    performance_summary = _performance_summary(data)
    risk_summary = _risk_summary(data)
    return _approval_findings(data, thresholds) + (
        evaluate_pnl_validation(performance_summary, thresholds),
        evaluate_return_validation(performance_summary, thresholds),
        evaluate_drawdown_validation(performance_summary, risk_summary, thresholds),
        evaluate_profit_factor_validation(performance_summary, thresholds),
        evaluate_expectancy_validation(performance_summary, thresholds),
        evaluate_trade_count_validation(performance_summary, thresholds),
        evaluate_win_rate_validation(performance_summary, thresholds),
        evaluate_risk_per_trade_validation(risk_summary, thresholds),
        evaluate_exposure_validation(risk_summary, thresholds),
        evaluate_loss_limit_validation(risk_summary, thresholds),
        evaluate_stability_validation(performance_summary, risk_summary, thresholds),
        evaluate_rule_violation_validation(data.risk_metrics_result, thresholds),
    )


def detect_performance_risk_validation_risks(
    data: PerformanceRiskValidationGateInput | Mapping[str, Any],
    findings: tuple[PerformanceRiskValidationFinding, ...] | None = None,
) -> tuple[PerformanceRiskValidationGateRisk, ...]:
    data = _coerce_input(data)
    thresholds = _thresholds(data)
    findings = _build_findings(data, thresholds) if findings is None else findings
    risks: list[PerformanceRiskValidationGateRisk] = []
    if _performance_summary(data) is None or _risk_summary(data) is None:
        risks.append(PerformanceRiskValidationGateRisk.PERFORMANCE_RISK_INPUT_MISSING)
    for finding in findings:
        if not finding.passed:
            risks.extend(finding.risks)
    if not _offline_boundary(data):
        risks.append(PerformanceRiskValidationGateRisk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(PerformanceRiskValidationGateRisk.DATA_ACCESS_VIOLATION)
    if data.multi_scenario_controlled_simulation_requested is True:
        risks.append(PerformanceRiskValidationGateRisk.PREMATURE_MULTI_SCENARIO_CONTROLLED_SIMULATION)
    return _dedupe(risks)


def _finding_score(findings: tuple[PerformanceRiskValidationFinding, ...], name: str) -> int:
    for finding in findings:
        if finding.name == name:
            return finding.score
    return 0


def compute_performance_risk_validation_score(
    data: PerformanceRiskValidationGateInput | Mapping[str, Any],
    findings: tuple[PerformanceRiskValidationFinding, ...] | None = None,
    risks: tuple[PerformanceRiskValidationGateRisk, ...] | None = None,
) -> PerformanceRiskValidationGateScore:
    data = _coerce_input(data)
    thresholds = _thresholds(data)
    findings = _build_findings(data, thresholds) if findings is None else findings
    risks = detect_performance_risk_validation_risks(data, findings) if risks is None else risks
    performance_approval_score = _finding_score(findings, "performance_approval")
    risk_approval_score = _finding_score(findings, "risk_approval")
    pnl_score = _finding_score(findings, "pnl")
    return_score = _finding_score(findings, "return")
    drawdown_score = _finding_score(findings, "drawdown")
    profit_factor_score = _finding_score(findings, "profit_factor")
    expectancy_score = _finding_score(findings, "expectancy")
    trade_count_score = _finding_score(findings, "trade_count")
    win_rate_score = _finding_score(findings, "win_rate")
    risk_per_trade_score = _finding_score(findings, "risk_per_trade")
    exposure_score = _finding_score(findings, "exposure")
    loss_limit_score = _finding_score(findings, "loss_limit")
    stability_score = _finding_score(findings, "stability")
    rule_violation_score = _finding_score(findings, "rule_violations")
    threshold_score = _finding_score(findings, "thresholds")
    boundary_score = 100 if _offline_boundary(data) and _data_boundary(data) else 0
    values = (
        performance_approval_score,
        risk_approval_score,
        pnl_score,
        return_score,
        drawdown_score,
        profit_factor_score,
        expectancy_score,
        trade_count_score,
        win_rate_score,
        risk_per_trade_score,
        exposure_score,
        loss_limit_score,
        stability_score,
        rule_violation_score,
        threshold_score,
        boundary_score,
    )
    overall = _clamp(sum(values) / len(values) - min(80, len(set(risks)) * 4))
    for risk, cap in {
        PerformanceRiskValidationGateRisk.PERFORMANCE_METRICS_NOT_APPROVED: 50,
        PerformanceRiskValidationGateRisk.RISK_METRICS_NOT_APPROVED: 50,
        PerformanceRiskValidationGateRisk.PERFORMANCE_RISK_INPUT_MISSING: 45,
        PerformanceRiskValidationGateRisk.PNL_VALIDATION_FAILED: 70,
        PerformanceRiskValidationGateRisk.RETURN_VALIDATION_FAILED: 70,
        PerformanceRiskValidationGateRisk.DRAWDOWN_VALIDATION_FAILED: 70,
        PerformanceRiskValidationGateRisk.PROFIT_FACTOR_VALIDATION_FAILED: 75,
        PerformanceRiskValidationGateRisk.EXPECTANCY_VALIDATION_FAILED: 75,
        PerformanceRiskValidationGateRisk.TRADE_COUNT_TOO_LOW: 70,
        PerformanceRiskValidationGateRisk.RISK_PER_TRADE_TOO_HIGH: 70,
        PerformanceRiskValidationGateRisk.EXPOSURE_TOO_HIGH: 70,
        PerformanceRiskValidationGateRisk.LOSS_LIMIT_USAGE_TOO_HIGH: 70,
        PerformanceRiskValidationGateRisk.STABILITY_VALIDATION_FAILED: 75,
        PerformanceRiskValidationGateRisk.RULE_VIOLATION_DETECTED: 70,
        PerformanceRiskValidationGateRisk.VALIDATION_THRESHOLD_MISSING: 55,
        PerformanceRiskValidationGateRisk.REAL_EXECUTION_BOUNDARY_VIOLATION: 35,
        PerformanceRiskValidationGateRisk.DATA_ACCESS_VIOLATION: 35,
        PerformanceRiskValidationGateRisk.PREMATURE_MULTI_SCENARIO_CONTROLLED_SIMULATION: 40,
    }.items():
        if risk in risks:
            overall = min(overall, cap)
    return PerformanceRiskValidationGateScore(
        overall,
        performance_approval_score,
        risk_approval_score,
        pnl_score,
        return_score,
        drawdown_score,
        profit_factor_score,
        expectancy_score,
        trade_count_score,
        win_rate_score,
        risk_per_trade_score,
        exposure_score,
        loss_limit_score,
        stability_score,
        rule_violation_score,
        threshold_score,
        boundary_score,
    )


def _select_decision(
    risks: tuple[PerformanceRiskValidationGateRisk, ...],
) -> PerformanceRiskValidationGateDecision:
    if (
        PerformanceRiskValidationGateRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in risks
        or PerformanceRiskValidationGateRisk.DATA_ACCESS_VIOLATION in risks
        or PerformanceRiskValidationGateRisk.PREMATURE_MULTI_SCENARIO_CONTROLLED_SIMULATION in risks
    ):
        return PerformanceRiskValidationGateDecision.BLOCK_PERFORMANCE_RISK_VALIDATION
    if (
        PerformanceRiskValidationGateRisk.PERFORMANCE_METRICS_NOT_APPROVED in risks
        or PerformanceRiskValidationGateRisk.PERFORMANCE_RISK_INPUT_MISSING in risks
    ):
        return PerformanceRiskValidationGateDecision.REQUIRE_PERFORMANCE_METRICS_FIXES
    if PerformanceRiskValidationGateRisk.RISK_METRICS_NOT_APPROVED in risks:
        return PerformanceRiskValidationGateDecision.REQUIRE_RISK_METRICS_FIXES
    if PerformanceRiskValidationGateRisk.VALIDATION_THRESHOLD_MISSING in risks:
        return PerformanceRiskValidationGateDecision.REQUIRE_ADDITIONAL_SCENARIOS
    if PerformanceRiskValidationGateRisk.TRADE_COUNT_TOO_LOW in risks:
        return PerformanceRiskValidationGateDecision.REQUIRE_MORE_TRADES
    if PerformanceRiskValidationGateRisk.DRAWDOWN_VALIDATION_FAILED in risks:
        return PerformanceRiskValidationGateDecision.REQUIRE_DRAWDOWN_REDUCTION
    if (
        PerformanceRiskValidationGateRisk.RISK_PER_TRADE_TOO_HIGH in risks
        or PerformanceRiskValidationGateRisk.EXPOSURE_TOO_HIGH in risks
        or PerformanceRiskValidationGateRisk.LOSS_LIMIT_USAGE_TOO_HIGH in risks
        or PerformanceRiskValidationGateRisk.RULE_VIOLATION_DETECTED in risks
    ):
        return PerformanceRiskValidationGateDecision.REQUIRE_RISK_REDUCTION
    if PerformanceRiskValidationGateRisk.STABILITY_VALIDATION_FAILED in risks:
        return PerformanceRiskValidationGateDecision.REQUIRE_STABILITY_IMPROVEMENT
    if risks:
        return PerformanceRiskValidationGateDecision.REQUIRE_ADDITIONAL_SCENARIOS
    return PerformanceRiskValidationGateDecision.APPROVE_PERFORMANCE_RISK_VALIDATION_GATE


def _select_state(
    decision: PerformanceRiskValidationGateDecision,
    risks: tuple[PerformanceRiskValidationGateRisk, ...],
    score: int,
    thresholds: PerformanceRiskValidationThresholds | None,
) -> PerformanceRiskValidationGateState:
    if decision == PerformanceRiskValidationGateDecision.BLOCK_PERFORMANCE_RISK_VALIDATION:
        return PerformanceRiskValidationGateState.VALIDATION_BLOCKED
    if decision in {
        PerformanceRiskValidationGateDecision.REQUIRE_PERFORMANCE_METRICS_FIXES,
        PerformanceRiskValidationGateDecision.REQUIRE_RISK_METRICS_FIXES,
    }:
        return PerformanceRiskValidationGateState.VALIDATION_INPUT_INVALID
    if risks:
        return PerformanceRiskValidationGateState.VALIDATION_COMPLETED_WITH_WARNINGS
    if thresholds is not None and score >= thresholds.min_gate_score:
        return PerformanceRiskValidationGateState.READY_FOR_MULTI_SCENARIO_CONTROLLED_SIMULATION
    return PerformanceRiskValidationGateState.VALIDATION_COMPLETED


def generate_performance_risk_validation_recommendations(
    risks: tuple[PerformanceRiskValidationGateRisk, ...],
    decision: PerformanceRiskValidationGateDecision | None = None,
) -> tuple[PerformanceRiskValidationGateRecommendation, ...]:
    recommendations: list[PerformanceRiskValidationGateRecommendation] = []
    if risks:
        recommendations.append(PerformanceRiskValidationGateRecommendation.HOLD_MULTI_SCENARIO_CONTROLLED_SIMULATION)
    mapping = {
        PerformanceRiskValidationGateRisk.PERFORMANCE_METRICS_NOT_APPROVED: PerformanceRiskValidationGateRecommendation.APPROVE_PERFORMANCE_METRICS_FIRST,
        PerformanceRiskValidationGateRisk.RISK_METRICS_NOT_APPROVED: PerformanceRiskValidationGateRecommendation.APPROVE_RISK_METRICS_FIRST,
        PerformanceRiskValidationGateRisk.PERFORMANCE_RISK_INPUT_MISSING: PerformanceRiskValidationGateRecommendation.PROVIDE_PERFORMANCE_RISK_INPUTS,
        PerformanceRiskValidationGateRisk.PNL_VALIDATION_FAILED: PerformanceRiskValidationGateRecommendation.RECHECK_PNL,
        PerformanceRiskValidationGateRisk.RETURN_VALIDATION_FAILED: PerformanceRiskValidationGateRecommendation.RECHECK_RETURN,
        PerformanceRiskValidationGateRisk.DRAWDOWN_VALIDATION_FAILED: PerformanceRiskValidationGateRecommendation.REDUCE_DRAWDOWN,
        PerformanceRiskValidationGateRisk.PROFIT_FACTOR_VALIDATION_FAILED: PerformanceRiskValidationGateRecommendation.IMPROVE_PROFIT_FACTOR,
        PerformanceRiskValidationGateRisk.EXPECTANCY_VALIDATION_FAILED: PerformanceRiskValidationGateRecommendation.IMPROVE_EXPECTANCY,
        PerformanceRiskValidationGateRisk.TRADE_COUNT_TOO_LOW: PerformanceRiskValidationGateRecommendation.ADD_MORE_TRADES,
        PerformanceRiskValidationGateRisk.WIN_RATE_VALIDATION_WARNING: PerformanceRiskValidationGateRecommendation.IMPROVE_WIN_RATE_SAMPLE,
        PerformanceRiskValidationGateRisk.RISK_PER_TRADE_TOO_HIGH: PerformanceRiskValidationGateRecommendation.REDUCE_RISK_PER_TRADE,
        PerformanceRiskValidationGateRisk.EXPOSURE_TOO_HIGH: PerformanceRiskValidationGateRecommendation.REDUCE_EXPOSURE,
        PerformanceRiskValidationGateRisk.LOSS_LIMIT_USAGE_TOO_HIGH: PerformanceRiskValidationGateRecommendation.REDUCE_LOSS_LIMIT_USAGE,
        PerformanceRiskValidationGateRisk.STABILITY_VALIDATION_FAILED: PerformanceRiskValidationGateRecommendation.IMPROVE_STABILITY,
        PerformanceRiskValidationGateRisk.RULE_VIOLATION_DETECTED: PerformanceRiskValidationGateRecommendation.RESOLVE_RULE_VIOLATIONS,
        PerformanceRiskValidationGateRisk.VALIDATION_THRESHOLD_MISSING: PerformanceRiskValidationGateRecommendation.DEFINE_VALIDATION_THRESHOLDS,
        PerformanceRiskValidationGateRisk.REAL_EXECUTION_BOUNDARY_VIOLATION: PerformanceRiskValidationGateRecommendation.RESTORE_REAL_EXECUTION_BOUNDARIES,
        PerformanceRiskValidationGateRisk.DATA_ACCESS_VIOLATION: PerformanceRiskValidationGateRecommendation.REMOVE_DATA_ACCESS,
        PerformanceRiskValidationGateRisk.PREMATURE_MULTI_SCENARIO_CONTROLLED_SIMULATION: PerformanceRiskValidationGateRecommendation.DELAY_MULTI_SCENARIO_CONTROLLED_SIMULATION,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    if PerformanceRiskValidationGateRisk.TRADE_COUNT_TOO_LOW in risks:
        recommendations.append(PerformanceRiskValidationGateRecommendation.HOLD_MULTI_SCENARIO_CONTROLLED_SIMULATION)
        recommendations.append(PerformanceRiskValidationGateRecommendation.ADD_MORE_TRADES)
    recommendations.append(PerformanceRiskValidationGateRecommendation.RUN_PERFORMANCE_RISK_VALIDATION_GATE_SUITE)
    if decision == PerformanceRiskValidationGateDecision.APPROVE_PERFORMANCE_RISK_VALIDATION_GATE:
        recommendations.append(PerformanceRiskValidationGateRecommendation.APPROVE_MULTI_SCENARIO_CONTROLLED_SIMULATION)
    return _dedupe(recommendations)


def evaluate_performance_risk_validation_gate(
    data: PerformanceRiskValidationGateInput | Mapping[str, Any],
) -> PerformanceRiskValidationGateResult:
    data = _coerce_input(data)
    thresholds = _thresholds(data)
    findings = _build_findings(data, thresholds)
    risks = detect_performance_risk_validation_risks(data, findings)
    score = compute_performance_risk_validation_score(data, findings, risks)
    decision = _select_decision(risks)
    state = _select_state(decision, risks, score.overall_score, thresholds)
    recommendations = generate_performance_risk_validation_recommendations(risks, decision)
    validation_summary = _build_summary(_performance_summary(data), _risk_summary(data), data.risk_metrics_result)
    offline_only = _offline_boundary(data) and _data_boundary(data)
    summary = (
        f"{state.value}: decision={decision.value}, score={score.overall_score}, "
        f"risks={len(risks)}, pnl={validation_summary.total_pnl}, risk_quality={validation_summary.risk_quality_score}"
    )
    return PerformanceRiskValidationGateResult(
        state,
        decision,
        score.overall_score,
        score,
        risks,
        recommendations,
        validation_summary,
        thresholds or PerformanceRiskValidationThresholds(),
        findings,
        offline_only,
        summary,
    )


def render_performance_risk_validation_gate_markdown(result: PerformanceRiskValidationGateResult) -> str:
    risks = "\n".join(f"- {risk.value}" for risk in result.risks) or "- None"
    recommendations = "\n".join(f"- {item.value}" for item in result.recommendations) or "- None"
    findings = "\n".join(f"- {finding.name}: {'PASS' if finding.passed else 'FAIL'} ({finding.score})" for finding in result.findings)
    summary = result.validation_summary
    return "\n".join(
        (
            "# AGIcore Performance Risk Validation Gate",
            "",
            f"State: {result.state.value}",
            f"Decision: {result.decision.value}",
            f"Score: {result.gate_score}",
            f"Offline only: {result.offline_only}",
            "",
            "## Combined Metrics",
            f"Total PnL: {summary.total_pnl}",
            f"Return fraction: {summary.return_fraction}",
            f"Max drawdown fraction: {summary.max_drawdown_fraction}",
            f"Profit factor: {summary.profit_factor}",
            f"Expectancy: {summary.expectancy}",
            f"Trade count: {summary.trade_count}",
            f"Win rate: {summary.win_rate}",
            f"Risk per trade fraction: {summary.risk_per_trade_fraction}",
            f"Exposure fraction: {summary.exposure_fraction}",
            f"Loss limit usage: {summary.loss_limit_usage}",
            f"Performance quality score: {summary.performance_quality_score}",
            f"Risk quality score: {summary.risk_quality_score}",
            f"Rule violation count: {summary.rule_violation_count}",
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
    "evaluate_performance_risk_validation_gate",
    "validate_performance_metrics_approval",
    "validate_risk_metrics_approval",
    "evaluate_pnl_validation",
    "evaluate_return_validation",
    "evaluate_drawdown_validation",
    "evaluate_profit_factor_validation",
    "evaluate_expectancy_validation",
    "evaluate_trade_count_validation",
    "evaluate_win_rate_validation",
    "evaluate_risk_per_trade_validation",
    "evaluate_exposure_validation",
    "evaluate_loss_limit_validation",
    "evaluate_stability_validation",
    "evaluate_rule_violation_validation",
    "compute_performance_risk_validation_score",
    "detect_performance_risk_validation_risks",
    "generate_performance_risk_validation_recommendations",
    "render_performance_risk_validation_gate_markdown",
]
