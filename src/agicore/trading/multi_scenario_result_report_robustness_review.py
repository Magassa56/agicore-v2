"""Offline multi-scenario result report and robustness review for AGIcore."""

from __future__ import annotations

import math
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.multi_scenario_controlled_simulation_models import (
    ControlledSimulationScenarioType,
)
from agicore.trading.multi_scenario_result_report_robustness_review_models import (
    MultiScenarioAggregateMetricReview,
    MultiScenarioBehaviorReview,
    MultiScenarioPostRunFinding,
    MultiScenarioReadinessFinding,
    MultiScenarioResultReportDecision,
    MultiScenarioResultReportInput,
    MultiScenarioResultReportRecommendation,
    MultiScenarioResultReportResult,
    MultiScenarioResultReportRisk,
    MultiScenarioResultReportScore,
    MultiScenarioResultReportState,
    MultiScenarioRobustnessReview,
    MultiScenarioStabilityReview,
)


def _coerce_input(data: MultiScenarioResultReportInput | Mapping[str, Any]) -> MultiScenarioResultReportInput:
    if isinstance(data, MultiScenarioResultReportInput):
        return data
    allowed = {field.name for field in fields(MultiScenarioResultReportInput)}
    payload = {key: value for key, value in dict(data).items() if key in allowed}
    return MultiScenarioResultReportInput(**payload)


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


def _simulation_result(data: MultiScenarioResultReportInput) -> Any:
    return data.multi_scenario_controlled_simulation_result


def _aggregate_report(data: MultiScenarioResultReportInput) -> Any:
    return data.multi_scenario_aggregate_report or _get(_simulation_result(data), "aggregate_report")


def _metric_summary(data: MultiScenarioResultReportInput) -> Any:
    return (
        data.multi_scenario_metric_summary
        or _get(_simulation_result(data), "metric_summary")
        or _get(_aggregate_report(data), "metric_summary")
    )


def _scenario_results(data: MultiScenarioResultReportInput) -> tuple[Any, ...]:
    if data.controlled_simulation_scenario_results is not None:
        return _as_tuple(data.controlled_simulation_scenario_results)
    report = _aggregate_report(data)
    if report is not None:
        results = _as_tuple(_get(report, "scenario_results", ()))
        if results:
            return results
    return _as_tuple(_get(_simulation_result(data), "scenario_results", ()))


def _upstream_items(data: MultiScenarioResultReportInput) -> tuple[Any, ...]:
    return (
        data.multi_scenario_controlled_simulation_result,
        data.multi_scenario_metric_summary,
        data.multi_scenario_aggregate_report,
        data.controlled_simulation_scenario_results,
        data.performance_risk_validation_gate,
        data.performance_metrics_result,
        data.risk_metrics_result,
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


def _upstream_risks(data: MultiScenarioResultReportInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: MultiScenarioResultReportInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _offline_boundary(data: MultiScenarioResultReportInput) -> bool:
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


def _data_boundary(data: MultiScenarioResultReportInput) -> bool:
    return (
        data.synthetic_data_only is True
        and data.in_memory_only is True
        and data.data_access_requested is not True
        and not _has_upstream_risk(data, "DATA_ACCESS", "DATA_ACCESS_VIOLATION", "REAL_DATA")
    )


def validate_multi_scenario_controlled_simulation_result(
    data: MultiScenarioResultReportInput | Mapping[str, Any],
) -> bool:
    data = _coerce_input(data)
    result = _simulation_result(data)
    if result is None:
        return False
    approved = (
        data.multi_scenario_simulation_approved is not False
        and (
            data.multi_scenario_simulation_approved is True
            or _state_contains(
                result,
                "READY_FOR_MULTI_SCENARIO_RESULT_REPORT",
                "APPROVE_MULTI_SCENARIO_CONTROLLED_SIMULATION",
            )
        )
    )
    return (
        approved
        and _get(result, "offline_only", True) is True
        and not _contains(
            _get(result, "risks", ()),
            "PERFORMANCE_RISK_VALIDATION_NOT_APPROVED",
            "SCENARIO_SUITE_EMPTY",
            "SCENARIO_DEFINITION_INVALID",
            "SCENARIO_EXECUTION_FAILED",
            "METRIC_AGGREGATION_INVALID",
            "REAL_EXECUTION_BOUNDARY_VIOLATION",
            "DATA_ACCESS_VIOLATION",
            "PREMATURE_MULTI_SCENARIO_RESULT_REPORT",
        )
    )


def summarize_multi_scenario_aggregate_metrics(
    data: MultiScenarioResultReportInput | Mapping[str, Any],
) -> MultiScenarioAggregateMetricReview:
    data = _coerce_input(data)
    metrics = _metric_summary(data)
    if metrics is None:
        return MultiScenarioAggregateMetricReview(passed=False, risks=(MultiScenarioResultReportRisk.AGGREGATE_METRICS_MISSING,))
    scenario_count = int(_get(metrics, "scenario_count", 0) or 0)
    passed_count = int(_get(metrics, "passed_scenario_count", 0) or 0)
    failed_count = int(_get(metrics, "failed_scenario_count", 0) or 0)
    total_pnl = float(_get(metrics, "total_pnl", 0.0) or 0.0)
    average_pnl = float(_get(metrics, "average_pnl", 0.0) or 0.0)
    max_drawdown_fraction = float(_get(metrics, "max_drawdown_fraction", 0.0) or 0.0)
    win_rate = float(_get(metrics, "win_rate", 0.0) or 0.0)
    profit_factor = float(_get(metrics, "profit_factor", 0.0) or 0.0)
    expectancy = float(_get(metrics, "expectancy", 0.0) or 0.0)
    trade_count = int(_get(metrics, "trade_count", 0) or 0)
    passed = (
        scenario_count > 0
        and passed_count + failed_count == scenario_count
        and all(_finite(value) for value in (total_pnl, average_pnl, max_drawdown_fraction, win_rate, expectancy))
        and _numeric_or_inf(profit_factor)
        and trade_count >= 0
    )
    risks = () if passed else (MultiScenarioResultReportRisk.AGGREGATE_METRICS_MISSING,)
    return MultiScenarioAggregateMetricReview(
        scenario_count,
        passed_count,
        failed_count,
        total_pnl,
        average_pnl,
        max_drawdown_fraction,
        win_rate,
        profit_factor,
        expectancy,
        trade_count,
        passed,
        risks,
        (f"scenario_count={scenario_count}", f"trade_count={trade_count}"),
    )


def review_scenario_pass_fail_distribution(
    data: MultiScenarioResultReportInput | Mapping[str, Any],
) -> MultiScenarioPostRunFinding:
    data = _coerce_input(data)
    review = summarize_multi_scenario_aggregate_metrics(data)
    scenario_results = _scenario_results(data)
    required_types = {
        ControlledSimulationScenarioType.WINNING_SCENARIO,
        ControlledSimulationScenarioType.LOSING_SCENARIO,
        ControlledSimulationScenarioType.FLAT_SCENARIO,
        ControlledSimulationScenarioType.DRAWDOWN_SCENARIO,
        ControlledSimulationScenarioType.VOLATILE_SCENARIO,
        ControlledSimulationScenarioType.STOP_CONDITION_SCENARIO,
        ControlledSimulationScenarioType.RISK_VIOLATION_SCENARIO,
        ControlledSimulationScenarioType.POSITION_INCONSISTENCY_SCENARIO,
    }
    present = {_scenario_type(result) for result in scenario_results}
    passed = review.passed and bool(scenario_results) and required_types.issubset(present) and review.failed_scenario_count <= data.max_failed_scenarios
    return MultiScenarioPostRunFinding(
        "pass_fail_distribution",
        passed,
        100 if passed else 50,
        () if passed else (MultiScenarioResultReportRisk.SCENARIO_PASS_FAIL_REVIEW_INVALID,),
        (f"passed={review.passed_scenario_count}", f"failed={review.failed_scenario_count}", f"present={len(present)}"),
    )


def review_multi_scenario_pnl_quality(
    data: MultiScenarioResultReportInput | Mapping[str, Any],
) -> MultiScenarioPostRunFinding:
    data = _coerce_input(data)
    review = summarize_multi_scenario_aggregate_metrics(data)
    passed = review.passed and review.total_pnl >= data.min_total_pnl
    return MultiScenarioPostRunFinding(
        "pnl_quality",
        passed,
        100 if passed else 60,
        () if passed else (MultiScenarioResultReportRisk.MULTI_SCENARIO_PNL_REVIEW_INVALID,),
        (f"total_pnl={review.total_pnl}", f"minimum={data.min_total_pnl}"),
    )


def review_multi_scenario_drawdown_quality(
    data: MultiScenarioResultReportInput | Mapping[str, Any],
) -> MultiScenarioPostRunFinding:
    data = _coerce_input(data)
    review = summarize_multi_scenario_aggregate_metrics(data)
    passed = review.passed and review.max_drawdown_fraction <= data.max_drawdown_fraction
    return MultiScenarioPostRunFinding(
        "drawdown_quality",
        passed,
        _clamp(100 - review.max_drawdown_fraction * 100) if review.passed else 0,
        () if passed else (MultiScenarioResultReportRisk.MULTI_SCENARIO_DRAWDOWN_REVIEW_INVALID,),
        (f"max_drawdown_fraction={review.max_drawdown_fraction}", f"limit={data.max_drawdown_fraction}"),
    )


def review_multi_scenario_profit_factor_quality(
    data: MultiScenarioResultReportInput | Mapping[str, Any],
) -> MultiScenarioPostRunFinding:
    data = _coerce_input(data)
    review = summarize_multi_scenario_aggregate_metrics(data)
    passed = review.passed and _numeric_or_inf(review.profit_factor) and review.profit_factor >= data.min_profit_factor
    return MultiScenarioPostRunFinding(
        "profit_factor_quality",
        passed,
        100 if passed else 60,
        () if passed else (MultiScenarioResultReportRisk.MULTI_SCENARIO_PROFIT_FACTOR_REVIEW_INVALID,),
        (f"profit_factor={review.profit_factor}", f"minimum={data.min_profit_factor}"),
    )


def review_multi_scenario_expectancy_quality(
    data: MultiScenarioResultReportInput | Mapping[str, Any],
) -> MultiScenarioPostRunFinding:
    data = _coerce_input(data)
    review = summarize_multi_scenario_aggregate_metrics(data)
    passed = review.passed and review.expectancy >= data.min_expectancy
    return MultiScenarioPostRunFinding(
        "expectancy_quality",
        passed,
        100 if passed else 60,
        () if passed else (MultiScenarioResultReportRisk.MULTI_SCENARIO_EXPECTANCY_REVIEW_INVALID,),
        (f"expectancy={review.expectancy}", f"minimum={data.min_expectancy}"),
    )


def review_multi_scenario_stability_quality(
    data: MultiScenarioResultReportInput | Mapping[str, Any],
) -> MultiScenarioStabilityReview:
    data = _coerce_input(data)
    metrics = _metric_summary(data)
    score = int(_get(metrics, "stability_score", 0) or 0)
    passed = score >= data.min_stability_score
    return MultiScenarioStabilityReview(
        score,
        data.min_stability_score,
        passed,
        () if passed else (MultiScenarioResultReportRisk.MULTI_SCENARIO_STABILITY_WEAK,),
        (f"stability_score={score}", f"minimum={data.min_stability_score}"),
    )


def review_multi_scenario_robustness_quality(
    data: MultiScenarioResultReportInput | Mapping[str, Any],
) -> MultiScenarioRobustnessReview:
    data = _coerce_input(data)
    metrics = _metric_summary(data)
    score = int(_get(metrics, "robustness_score", 0) or 0)
    passed = score >= data.min_robustness_score
    return MultiScenarioRobustnessReview(
        score,
        data.min_robustness_score,
        passed,
        () if passed else (MultiScenarioResultReportRisk.MULTI_SCENARIO_ROBUSTNESS_WEAK,),
        (f"robustness_score={score}", f"minimum={data.min_robustness_score}"),
    )


def _scenario_type(result: Any) -> ControlledSimulationScenarioType:
    raw = _get(result, "scenario_type")
    if isinstance(raw, ControlledSimulationScenarioType):
        return raw
    return ControlledSimulationScenarioType(str(raw))


def _review_behavior(
    data: MultiScenarioResultReportInput,
    scenario_type: ControlledSimulationScenarioType,
    risk: MultiScenarioResultReportRisk,
    predicate,
) -> MultiScenarioBehaviorReview:
    results = tuple(result for result in _scenario_results(data) if _scenario_type(result) == scenario_type)
    present = bool(results)
    passed = present and all(bool(_get(result, "passed", False)) for result in results) and all(predicate(result) for result in results)
    pnl = sum(float(_get(result, "pnl", 0.0) or 0.0) for result in results)
    drawdown = max((float(_get(result, "max_drawdown_fraction", 0.0) or 0.0) for result in results), default=0.0)
    return MultiScenarioBehaviorReview(
        scenario_type,
        present,
        passed,
        len(results),
        pnl,
        drawdown,
        () if passed else (risk,),
        (f"present={present}", f"count={len(results)}", f"pnl={pnl}", f"drawdown={drawdown}"),
    )


def review_losing_scenario_behavior(
    data: MultiScenarioResultReportInput | Mapping[str, Any],
) -> MultiScenarioBehaviorReview:
    data = _coerce_input(data)
    return _review_behavior(
        data,
        ControlledSimulationScenarioType.LOSING_SCENARIO,
        MultiScenarioResultReportRisk.LOSING_SCENARIO_BEHAVIOR_INVALID,
        lambda result: float(_get(result, "pnl", 0.0) or 0.0) < 0 and int(_get(result, "trade_count", 0) or 0) > 0,
    )


def review_drawdown_scenario_behavior(
    data: MultiScenarioResultReportInput | Mapping[str, Any],
) -> MultiScenarioBehaviorReview:
    data = _coerce_input(data)
    return _review_behavior(
        data,
        ControlledSimulationScenarioType.DRAWDOWN_SCENARIO,
        MultiScenarioResultReportRisk.DRAWDOWN_SCENARIO_BEHAVIOR_INVALID,
        lambda result: float(_get(result, "max_drawdown_fraction", 0.0) or 0.0) > 0,
    )


def review_risk_violation_scenario_behavior(
    data: MultiScenarioResultReportInput | Mapping[str, Any],
) -> MultiScenarioBehaviorReview:
    data = _coerce_input(data)
    return _review_behavior(
        data,
        ControlledSimulationScenarioType.RISK_VIOLATION_SCENARIO,
        MultiScenarioResultReportRisk.RISK_VIOLATION_SCENARIO_BEHAVIOR_INVALID,
        lambda result: not _as_tuple(_get(result, "failures", ())) and not _contains(_get(result, "risks", ()), "REAL_EXECUTION", "DATA_ACCESS"),
    )


def review_position_inconsistency_scenario_behavior(
    data: MultiScenarioResultReportInput | Mapping[str, Any],
) -> MultiScenarioBehaviorReview:
    data = _coerce_input(data)
    return _review_behavior(
        data,
        ControlledSimulationScenarioType.POSITION_INCONSISTENCY_SCENARIO,
        MultiScenarioResultReportRisk.POSITION_INCONSISTENCY_SCENARIO_BEHAVIOR_INVALID,
        lambda result: not _as_tuple(_get(result, "failures", ())),
    )


def review_stop_condition_scenario_behavior(
    data: MultiScenarioResultReportInput | Mapping[str, Any],
) -> MultiScenarioBehaviorReview:
    data = _coerce_input(data)
    return _review_behavior(
        data,
        ControlledSimulationScenarioType.STOP_CONDITION_SCENARIO,
        MultiScenarioResultReportRisk.STOP_CONDITION_SCENARIO_BEHAVIOR_INVALID,
        lambda result: not _contains(_get(result, "risks", ()), "STOP_CONDITIONS_MISSING", "REAL_EXECUTION", "DATA_ACCESS"),
    )


def _all_behavior_reviews(data: MultiScenarioResultReportInput) -> tuple[MultiScenarioBehaviorReview, ...]:
    return (
        review_losing_scenario_behavior(data),
        review_drawdown_scenario_behavior(data),
        review_risk_violation_scenario_behavior(data),
        review_position_inconsistency_scenario_behavior(data),
        review_stop_condition_scenario_behavior(data),
    )


def review_multi_scenario_readiness_for_paper_broker_read_only(
    data: MultiScenarioResultReportInput | Mapping[str, Any],
) -> MultiScenarioReadinessFinding:
    data = _coerce_input(data)
    blocked = data.paper_broker_read_only_preparation_requested is True
    base_findings = _build_findings(data)
    passed = not blocked and all(finding.passed for finding in base_findings)
    risks = () if passed else ((MultiScenarioResultReportRisk.PAPER_BROKER_READ_ONLY_PREPARATION_PREMATURE,) if blocked else ())
    return MultiScenarioReadinessFinding(
        "paper_broker_read_only_readiness",
        passed,
        100 if passed else 40,
        risks,
        (f"requested={bool(data.paper_broker_read_only_preparation_requested)}", f"findings={len(base_findings)}"),
    )


def _build_findings(data: MultiScenarioResultReportInput) -> tuple[MultiScenarioPostRunFinding, ...]:
    aggregate = summarize_multi_scenario_aggregate_metrics(data)
    robustness = review_multi_scenario_robustness_quality(data)
    stability = review_multi_scenario_stability_quality(data)
    behavior_reviews = _all_behavior_reviews(data)
    findings = [
        MultiScenarioPostRunFinding(
            "simulation_approval",
            validate_multi_scenario_controlled_simulation_result(data),
            100 if validate_multi_scenario_controlled_simulation_result(data) else 0,
            () if validate_multi_scenario_controlled_simulation_result(data) else (MultiScenarioResultReportRisk.MULTI_SCENARIO_SIMULATION_NOT_APPROVED,),
        ),
        MultiScenarioPostRunFinding(
            "aggregate_metrics",
            aggregate.passed,
            100 if aggregate.passed else 0,
            aggregate.risks,
        ),
        review_scenario_pass_fail_distribution(data),
        review_multi_scenario_pnl_quality(data),
        review_multi_scenario_drawdown_quality(data),
        review_multi_scenario_profit_factor_quality(data),
        review_multi_scenario_expectancy_quality(data),
        MultiScenarioPostRunFinding("stability", stability.passed, stability.stability_score, stability.risks, stability.details),
        MultiScenarioPostRunFinding("robustness", robustness.passed, robustness.robustness_score, robustness.risks, robustness.details),
    ]
    findings.extend(
        MultiScenarioPostRunFinding(
            f"{review.scenario_type.value.lower()}_behavior",
            review.passed,
            100 if review.passed else 50,
            review.risks,
            review.details,
        )
        for review in behavior_reviews
    )
    return tuple(findings)


def detect_multi_scenario_result_report_risks(
    data: MultiScenarioResultReportInput | Mapping[str, Any],
    findings: tuple[MultiScenarioPostRunFinding, ...] | None = None,
) -> tuple[MultiScenarioResultReportRisk, ...]:
    data = _coerce_input(data)
    findings = _build_findings(data) if findings is None else findings
    risks: list[MultiScenarioResultReportRisk] = []
    if _simulation_result(data) is None:
        risks.append(MultiScenarioResultReportRisk.MULTI_SCENARIO_RESULT_MISSING)
    if _metric_summary(data) is None:
        risks.append(MultiScenarioResultReportRisk.AGGREGATE_METRICS_MISSING)
    for finding in findings:
        if not finding.passed:
            risks.extend(finding.risks)
    if data.paper_broker_read_only_preparation_requested is True:
        risks.append(MultiScenarioResultReportRisk.PAPER_BROKER_READ_ONLY_PREPARATION_PREMATURE)
    if not _offline_boundary(data):
        risks.append(MultiScenarioResultReportRisk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(MultiScenarioResultReportRisk.DATA_ACCESS_VIOLATION)
    return _dedupe(risks)


def _finding_score(findings: tuple[MultiScenarioPostRunFinding, ...], name: str) -> int:
    for finding in findings:
        if finding.name == name:
            return finding.score
    return 0


def compute_multi_scenario_result_report_score(
    data: MultiScenarioResultReportInput | Mapping[str, Any],
    findings: tuple[MultiScenarioPostRunFinding, ...] | None = None,
    risks: tuple[MultiScenarioResultReportRisk, ...] | None = None,
) -> MultiScenarioResultReportScore:
    data = _coerce_input(data)
    findings = _build_findings(data) if findings is None else findings
    risks = detect_multi_scenario_result_report_risks(data, findings) if risks is None else risks
    simulation_approval_score = _finding_score(findings, "simulation_approval")
    aggregate_metric_score = _finding_score(findings, "aggregate_metrics")
    pass_fail_score = _finding_score(findings, "pass_fail_distribution")
    pnl_score = _finding_score(findings, "pnl_quality")
    drawdown_score = _finding_score(findings, "drawdown_quality")
    profit_factor_score = _finding_score(findings, "profit_factor_quality")
    expectancy_score = _finding_score(findings, "expectancy_quality")
    stability_score = _finding_score(findings, "stability")
    robustness_score = _finding_score(findings, "robustness")
    behavior_scores = [finding.score for finding in findings if finding.name.endswith("_behavior")]
    behavior_score = _clamp(sum(behavior_scores) / len(behavior_scores)) if behavior_scores else 0
    readiness_finding = review_multi_scenario_readiness_for_paper_broker_read_only(data)
    readiness_score = readiness_finding.score
    boundary_score = 100 if _offline_boundary(data) and _data_boundary(data) else 0
    values = (
        simulation_approval_score,
        aggregate_metric_score,
        pass_fail_score,
        pnl_score,
        drawdown_score,
        profit_factor_score,
        expectancy_score,
        stability_score,
        robustness_score,
        behavior_score,
        readiness_score,
        boundary_score,
    )
    overall = _clamp(sum(values) / len(values) - min(80, len(set(risks)) * 4))
    for risk, cap in {
        MultiScenarioResultReportRisk.MULTI_SCENARIO_SIMULATION_NOT_APPROVED: 50,
        MultiScenarioResultReportRisk.MULTI_SCENARIO_RESULT_MISSING: 45,
        MultiScenarioResultReportRisk.AGGREGATE_METRICS_MISSING: 50,
        MultiScenarioResultReportRisk.SCENARIO_PASS_FAIL_REVIEW_INVALID: 65,
        MultiScenarioResultReportRisk.MULTI_SCENARIO_PNL_REVIEW_INVALID: 70,
        MultiScenarioResultReportRisk.MULTI_SCENARIO_DRAWDOWN_REVIEW_INVALID: 70,
        MultiScenarioResultReportRisk.MULTI_SCENARIO_PROFIT_FACTOR_REVIEW_INVALID: 75,
        MultiScenarioResultReportRisk.MULTI_SCENARIO_EXPECTANCY_REVIEW_INVALID: 75,
        MultiScenarioResultReportRisk.MULTI_SCENARIO_STABILITY_WEAK: 75,
        MultiScenarioResultReportRisk.MULTI_SCENARIO_ROBUSTNESS_WEAK: 75,
        MultiScenarioResultReportRisk.POSITION_INCONSISTENCY_SCENARIO_BEHAVIOR_INVALID: 70,
        MultiScenarioResultReportRisk.STOP_CONDITION_SCENARIO_BEHAVIOR_INVALID: 70,
        MultiScenarioResultReportRisk.PAPER_BROKER_READ_ONLY_PREPARATION_PREMATURE: 40,
        MultiScenarioResultReportRisk.REAL_EXECUTION_BOUNDARY_VIOLATION: 35,
        MultiScenarioResultReportRisk.DATA_ACCESS_VIOLATION: 35,
    }.items():
        if risk in risks:
            overall = min(overall, cap)
    return MultiScenarioResultReportScore(
        overall,
        simulation_approval_score,
        aggregate_metric_score,
        pass_fail_score,
        pnl_score,
        drawdown_score,
        profit_factor_score,
        expectancy_score,
        stability_score,
        robustness_score,
        behavior_score,
        readiness_score,
        boundary_score,
    )


def _select_decision(risks: tuple[MultiScenarioResultReportRisk, ...]) -> MultiScenarioResultReportDecision:
    if (
        MultiScenarioResultReportRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in risks
        or MultiScenarioResultReportRisk.DATA_ACCESS_VIOLATION in risks
        or MultiScenarioResultReportRisk.PAPER_BROKER_READ_ONLY_PREPARATION_PREMATURE in risks
    ):
        return MultiScenarioResultReportDecision.BLOCK_MULTI_SCENARIO_RESULT_REPORT
    if (
        MultiScenarioResultReportRisk.MULTI_SCENARIO_SIMULATION_NOT_APPROVED in risks
        or MultiScenarioResultReportRisk.MULTI_SCENARIO_RESULT_MISSING in risks
    ):
        return MultiScenarioResultReportDecision.REQUIRE_MULTI_SCENARIO_FIXES
    if (
        MultiScenarioResultReportRisk.AGGREGATE_METRICS_MISSING in risks
        or MultiScenarioResultReportRisk.SCENARIO_PASS_FAIL_REVIEW_INVALID in risks
    ):
        return MultiScenarioResultReportDecision.REQUIRE_AGGREGATE_METRIC_FIXES
    if MultiScenarioResultReportRisk.MULTI_SCENARIO_ROBUSTNESS_WEAK in risks:
        return MultiScenarioResultReportDecision.REQUIRE_ROBUSTNESS_FIXES
    if MultiScenarioResultReportRisk.MULTI_SCENARIO_STABILITY_WEAK in risks:
        return MultiScenarioResultReportDecision.REQUIRE_STABILITY_FIXES
    if (
        MultiScenarioResultReportRisk.MULTI_SCENARIO_DRAWDOWN_REVIEW_INVALID in risks
        or MultiScenarioResultReportRisk.MULTI_SCENARIO_PNL_REVIEW_INVALID in risks
        or MultiScenarioResultReportRisk.RISK_VIOLATION_SCENARIO_BEHAVIOR_INVALID in risks
    ):
        return MultiScenarioResultReportDecision.REQUIRE_RISK_REDUCTION
    if MultiScenarioResultReportRisk.POSITION_INCONSISTENCY_SCENARIO_BEHAVIOR_INVALID in risks:
        return MultiScenarioResultReportDecision.REQUIRE_POSITION_CONSISTENCY_FIXES
    if MultiScenarioResultReportRisk.STOP_CONDITION_SCENARIO_BEHAVIOR_INVALID in risks:
        return MultiScenarioResultReportDecision.REQUIRE_STOP_CONDITION_FIXES
    if risks:
        return MultiScenarioResultReportDecision.REQUIRE_ADDITIONAL_SCENARIOS
    return MultiScenarioResultReportDecision.APPROVE_MULTI_SCENARIO_RESULT_REPORT_ROBUSTNESS_REVIEW


def _select_state(
    decision: MultiScenarioResultReportDecision,
    risks: tuple[MultiScenarioResultReportRisk, ...],
    score: int,
) -> MultiScenarioResultReportState:
    if decision == MultiScenarioResultReportDecision.BLOCK_MULTI_SCENARIO_RESULT_REPORT:
        return MultiScenarioResultReportState.REPORT_BLOCKED
    if decision in {
        MultiScenarioResultReportDecision.REQUIRE_MULTI_SCENARIO_FIXES,
        MultiScenarioResultReportDecision.REQUIRE_AGGREGATE_METRIC_FIXES,
    }:
        return MultiScenarioResultReportState.REPORT_INPUT_INVALID
    if risks:
        return MultiScenarioResultReportState.REPORT_COMPLETED_WITH_WARNINGS
    if score >= 80:
        return MultiScenarioResultReportState.READY_FOR_PAPER_BROKER_READ_ONLY_PREPARATION
    return MultiScenarioResultReportState.REPORT_COMPLETED


def generate_multi_scenario_result_report_recommendations(
    risks: tuple[MultiScenarioResultReportRisk, ...],
    decision: MultiScenarioResultReportDecision | None = None,
) -> tuple[MultiScenarioResultReportRecommendation, ...]:
    recommendations: list[MultiScenarioResultReportRecommendation] = []
    if risks:
        recommendations.append(MultiScenarioResultReportRecommendation.HOLD_PAPER_BROKER_READ_ONLY_PREPARATION)
    mapping = {
        MultiScenarioResultReportRisk.MULTI_SCENARIO_SIMULATION_NOT_APPROVED: MultiScenarioResultReportRecommendation.APPROVE_MULTI_SCENARIO_SIMULATION_FIRST,
        MultiScenarioResultReportRisk.MULTI_SCENARIO_RESULT_MISSING: MultiScenarioResultReportRecommendation.PROVIDE_MULTI_SCENARIO_RESULT,
        MultiScenarioResultReportRisk.AGGREGATE_METRICS_MISSING: MultiScenarioResultReportRecommendation.REBUILD_AGGREGATE_METRICS,
        MultiScenarioResultReportRisk.SCENARIO_PASS_FAIL_REVIEW_INVALID: MultiScenarioResultReportRecommendation.RECHECK_SCENARIO_PASS_FAIL_DISTRIBUTION,
        MultiScenarioResultReportRisk.MULTI_SCENARIO_PNL_REVIEW_INVALID: MultiScenarioResultReportRecommendation.RECHECK_MULTI_SCENARIO_PNL,
        MultiScenarioResultReportRisk.MULTI_SCENARIO_DRAWDOWN_REVIEW_INVALID: MultiScenarioResultReportRecommendation.REDUCE_MULTI_SCENARIO_DRAWDOWN,
        MultiScenarioResultReportRisk.MULTI_SCENARIO_PROFIT_FACTOR_REVIEW_INVALID: MultiScenarioResultReportRecommendation.IMPROVE_MULTI_SCENARIO_PROFIT_FACTOR,
        MultiScenarioResultReportRisk.MULTI_SCENARIO_EXPECTANCY_REVIEW_INVALID: MultiScenarioResultReportRecommendation.IMPROVE_MULTI_SCENARIO_EXPECTANCY,
        MultiScenarioResultReportRisk.MULTI_SCENARIO_STABILITY_WEAK: MultiScenarioResultReportRecommendation.IMPROVE_MULTI_SCENARIO_STABILITY,
        MultiScenarioResultReportRisk.MULTI_SCENARIO_ROBUSTNESS_WEAK: MultiScenarioResultReportRecommendation.IMPROVE_MULTI_SCENARIO_ROBUSTNESS,
        MultiScenarioResultReportRisk.LOSING_SCENARIO_BEHAVIOR_INVALID: MultiScenarioResultReportRecommendation.RECHECK_LOSING_SCENARIO,
        MultiScenarioResultReportRisk.DRAWDOWN_SCENARIO_BEHAVIOR_INVALID: MultiScenarioResultReportRecommendation.RECHECK_DRAWDOWN_SCENARIO,
        MultiScenarioResultReportRisk.RISK_VIOLATION_SCENARIO_BEHAVIOR_INVALID: MultiScenarioResultReportRecommendation.RECHECK_RISK_VIOLATION_SCENARIO,
        MultiScenarioResultReportRisk.POSITION_INCONSISTENCY_SCENARIO_BEHAVIOR_INVALID: MultiScenarioResultReportRecommendation.RECHECK_POSITION_INCONSISTENCY_SCENARIO,
        MultiScenarioResultReportRisk.STOP_CONDITION_SCENARIO_BEHAVIOR_INVALID: MultiScenarioResultReportRecommendation.RECHECK_STOP_CONDITION_SCENARIO,
        MultiScenarioResultReportRisk.PAPER_BROKER_READ_ONLY_PREPARATION_PREMATURE: MultiScenarioResultReportRecommendation.DELAY_PAPER_BROKER_READ_ONLY_PREPARATION,
        MultiScenarioResultReportRisk.REAL_EXECUTION_BOUNDARY_VIOLATION: MultiScenarioResultReportRecommendation.RESTORE_REAL_EXECUTION_BOUNDARIES,
        MultiScenarioResultReportRisk.DATA_ACCESS_VIOLATION: MultiScenarioResultReportRecommendation.REMOVE_DATA_ACCESS,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(MultiScenarioResultReportRecommendation.RUN_MULTI_SCENARIO_RESULT_REPORT_SUITE)
    if decision == MultiScenarioResultReportDecision.APPROVE_MULTI_SCENARIO_RESULT_REPORT_ROBUSTNESS_REVIEW:
        recommendations.append(MultiScenarioResultReportRecommendation.APPROVE_PAPER_BROKER_READ_ONLY_PREPARATION)
    return _dedupe(recommendations)


def evaluate_multi_scenario_result_report_robustness_review(
    data: MultiScenarioResultReportInput | Mapping[str, Any],
) -> MultiScenarioResultReportResult:
    data = _coerce_input(data)
    aggregate_review = summarize_multi_scenario_aggregate_metrics(data)
    robustness_review = review_multi_scenario_robustness_quality(data)
    stability_review = review_multi_scenario_stability_quality(data)
    behavior_reviews = _all_behavior_reviews(data)
    findings = _build_findings(data)
    risks = detect_multi_scenario_result_report_risks(data, findings)
    readiness = review_multi_scenario_readiness_for_paper_broker_read_only(data)
    if not readiness.passed:
        risks = _dedupe(risks + readiness.risks)
    score = compute_multi_scenario_result_report_score(data, findings, risks)
    decision = _select_decision(risks)
    state = _select_state(decision, risks, score.overall_score)
    recommendations = generate_multi_scenario_result_report_recommendations(risks, decision)
    offline_only = _offline_boundary(data) and _data_boundary(data)
    summary = (
        f"{state.value}: decision={decision.value}, score={score.overall_score}, "
        f"risks={len(risks)}, robustness={robustness_review.robustness_score}"
    )
    return MultiScenarioResultReportResult(
        state,
        decision,
        score.overall_score,
        score,
        risks,
        recommendations,
        aggregate_review,
        robustness_review,
        stability_review,
        behavior_reviews,
        readiness,
        findings,
        offline_only,
        summary,
    )


def render_multi_scenario_result_report_robustness_review_markdown(result: MultiScenarioResultReportResult) -> str:
    risks = "\n".join(f"- {risk.value}" for risk in result.risks) or "- None"
    recommendations = "\n".join(f"- {item.value}" for item in result.recommendations) or "- None"
    findings = "\n".join(f"- {finding.name}: {'PASS' if finding.passed else 'FAIL'} ({finding.score})" for finding in result.findings)
    behaviors = "\n".join(
        f"- {review.scenario_type.value}: {'PASS' if review.passed else 'FAIL'}, pnl={review.pnl}, dd={review.max_drawdown_fraction}"
        for review in result.behavior_reviews
    )
    aggregate = result.aggregate_metric_review
    return "\n".join(
        (
            "# AGIcore Multi-Scenario Result Report + Robustness Review",
            "",
            f"State: {result.state.value}",
            f"Decision: {result.decision.value}",
            f"Score: {result.report_score}",
            f"Offline only: {result.offline_only}",
            "",
            "## Aggregate Metrics",
            f"Scenario count: {aggregate.scenario_count}",
            f"Passed scenarios: {aggregate.passed_scenario_count}",
            f"Failed scenarios: {aggregate.failed_scenario_count}",
            f"Total PnL: {aggregate.total_pnl}",
            f"Average PnL: {aggregate.average_pnl}",
            f"Max drawdown fraction: {aggregate.max_drawdown_fraction}",
            f"Win rate: {aggregate.win_rate}",
            f"Profit factor: {aggregate.profit_factor}",
            f"Expectancy: {aggregate.expectancy}",
            f"Trade count: {aggregate.trade_count}",
            f"Stability score: {result.stability_review.stability_score}",
            f"Robustness score: {result.robustness_review.robustness_score}",
            "",
            "## Behavior Reviews",
            behaviors,
            "",
            "## Readiness",
            f"{result.readiness_finding.name}: {'PASS' if result.readiness_finding.passed else 'FAIL'}",
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
    "evaluate_multi_scenario_result_report_robustness_review",
    "validate_multi_scenario_controlled_simulation_result",
    "summarize_multi_scenario_aggregate_metrics",
    "review_scenario_pass_fail_distribution",
    "review_multi_scenario_pnl_quality",
    "review_multi_scenario_drawdown_quality",
    "review_multi_scenario_profit_factor_quality",
    "review_multi_scenario_expectancy_quality",
    "review_multi_scenario_stability_quality",
    "review_multi_scenario_robustness_quality",
    "review_losing_scenario_behavior",
    "review_drawdown_scenario_behavior",
    "review_risk_violation_scenario_behavior",
    "review_position_inconsistency_scenario_behavior",
    "review_stop_condition_scenario_behavior",
    "review_multi_scenario_readiness_for_paper_broker_read_only",
    "compute_multi_scenario_result_report_score",
    "detect_multi_scenario_result_report_risks",
    "generate_multi_scenario_result_report_recommendations",
    "render_multi_scenario_result_report_robustness_review_markdown",
]
