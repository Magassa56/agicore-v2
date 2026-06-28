"""Short offline review for the minimal controlled offline runner."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.controlled_offline_runner_minimal import (
    assert_controlled_offline_runner_no_real_execution_boundaries,
    render_controlled_offline_runner_json_report,
    run_controlled_offline_runner_minimal,
)
from agicore.trading.controlled_offline_runner_minimal_models import (
    ControlledOfflineRunnerMinimalDecision,
    ControlledOfflineRunnerMinimalResult,
    ControlledOfflineRunnerMinimalState,
)
from agicore.trading.controlled_offline_runner_minimal_review_models import (
    ControlledOfflineRunnerMinimalReviewDecision,
    ControlledOfflineRunnerMinimalReviewFinding,
    ControlledOfflineRunnerMinimalReviewInput,
    ControlledOfflineRunnerMinimalReviewRecommendation,
    ControlledOfflineRunnerMinimalReviewResult,
    ControlledOfflineRunnerMinimalReviewRisk,
    ControlledOfflineRunnerMinimalReviewScore,
    ControlledOfflineRunnerMinimalReviewState,
)


Decision = ControlledOfflineRunnerMinimalReviewDecision
Finding = ControlledOfflineRunnerMinimalReviewFinding
Recommendation = ControlledOfflineRunnerMinimalReviewRecommendation
Risk = ControlledOfflineRunnerMinimalReviewRisk
State = ControlledOfflineRunnerMinimalReviewState


def _value(item: Any) -> str:
    return item.value if isinstance(item, Enum) else str(item)


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
    return (items,)


def _dedupe(items: Iterable[Any]) -> tuple[Any, ...]:
    seen: set[Any] = set()
    out: list[Any] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return tuple(out)


def _coerce_input(data: ControlledOfflineRunnerMinimalReviewInput | Mapping[str, Any] | Any) -> ControlledOfflineRunnerMinimalReviewInput:
    if isinstance(data, ControlledOfflineRunnerMinimalReviewInput):
        return data
    if isinstance(data, Mapping):
        allowed = {field.name for field in fields(ControlledOfflineRunnerMinimalReviewInput)}
        return ControlledOfflineRunnerMinimalReviewInput(**{key: value for key, value in dict(data).items() if key in allowed})
    return ControlledOfflineRunnerMinimalReviewInput(minimal_result=data)


def _finding(name: str, passed: bool, risk: Risk, detail: str) -> Finding:
    return Finding(name=name, passed=passed, score=100 if passed else 0, risks=() if passed else (risk,), details=(detail,))


def validate_controlled_offline_runner_minimal_result_for_review(data: ControlledOfflineRunnerMinimalReviewInput | Mapping[str, Any] | Any) -> bool:
    data = _coerce_input(data)
    result = data.minimal_result
    explicit = data.controlled_offline_runner_minimal_approved
    return (
        result is not None
        and explicit is not False
        and (explicit is True or _get(result, "decision") is ControlledOfflineRunnerMinimalDecision.APPROVE_CONTROLLED_OFFLINE_RUNNER_MINIMAL)
        and _get(result, "state") is ControlledOfflineRunnerMinimalState.READY_FOR_CONTROLLED_OFFLINE_RUNNER_MINIMAL_REVIEW
        and _get(_get(result, "score"), "overall_score", 0) == 100
        and not _as_tuple(_get(result, "risks", ()))
    )


def review_controlled_offline_runner_determinism(data: ControlledOfflineRunnerMinimalReviewInput | Mapping[str, Any] | Any) -> Finding:
    data = _coerce_input(data)
    if data.minimal_input is None:
        passed = data.minimal_result is not None and _get(_get(data.minimal_result, "report"), "json")
    else:
        first = run_controlled_offline_runner_minimal(data.minimal_input)
        second = run_controlled_offline_runner_minimal(data.minimal_input)
        passed = (
            first.decision == second.decision
            and first.state == second.state
            and first.score == second.score
            and first.risks == second.risks
            and _get(_get(first, "report"), "json") == _get(_get(second, "report"), "json")
            and render_controlled_offline_runner_json_report(first) == render_controlled_offline_runner_json_report(second)
        )
    return _finding("determinism", bool(passed), Risk.CONTROLLED_OFFLINE_RUNNER_NOT_DETERMINISTIC, "runner must replay identically in memory")


def review_controlled_offline_runner_market_scenario(result: ControlledOfflineRunnerMinimalResult | Any) -> Finding:
    scenario = _get(result, "scenario")
    bars = _as_tuple(_get(scenario, "bars", ()))
    passed = bool(scenario) and bool(bars) and all(_get(bar, "high", 0) >= max(_get(bar, "open", 0), _get(bar, "close", 0)) and _get(bar, "low", 0) <= min(_get(bar, "open", 0), _get(bar, "close", 0)) for bar in bars)
    return _finding("market_scenario", passed, Risk.CONTROLLED_OFFLINE_RUNNER_MARKET_SCENARIO_REVIEW_FAILED, "synthetic scenario must be non-empty and valid")


def review_controlled_offline_runner_account_snapshot(result: ControlledOfflineRunnerMinimalResult | Any) -> Finding:
    account = _get(result, "account_snapshot")
    passed = bool(account) and _get(account, "simulated") is True and _get(account, "read_only") is True and _get(account, "cash", -1) >= 0 and _get(account, "equity", -1) >= 0
    return _finding("account_snapshot", passed, Risk.CONTROLLED_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_REVIEW_FAILED, "account snapshot must be simulated read-only")


def review_controlled_offline_runner_broker_snapshot(result: ControlledOfflineRunnerMinimalResult | Any) -> Finding:
    broker = _get(result, "broker_snapshot")
    passed = bool(broker) and _get(broker, "connected") is False and _get(broker, "simulated") is True and _get(broker, "read_only") is True and _get(broker, "orders_supported") is False and _get(broker, "real_broker") is False
    return _finding("broker_snapshot", passed, Risk.CONTROLLED_OFFLINE_RUNNER_BROKER_SNAPSHOT_REVIEW_FAILED, "broker snapshot must be simulated, disconnected and read-only")


def review_controlled_offline_runner_strategy_signal(result: ControlledOfflineRunnerMinimalResult | Any) -> Finding:
    signal = _get(result, "strategy_signal")
    passed = bool(signal) and _get(signal, "action") in {"BUY", "SELL", "HOLD"} and 0 <= _get(signal, "confidence", -1) <= 1 and _get(signal, "observation_only") is True
    return _finding("strategy_signal", passed, Risk.CONTROLLED_OFFLINE_RUNNER_STRATEGY_SIGNAL_REVIEW_FAILED, "signal must be observation-only")


def review_controlled_offline_runner_risk_guards(result: ControlledOfflineRunnerMinimalResult | Any) -> Finding:
    guard = _get(result, "risk_guard")
    passed = bool(guard) and _get(guard, "passed") is True and not _as_tuple(_get(guard, "risks", ()))
    return _finding("risk_guard", passed, Risk.CONTROLLED_OFFLINE_RUNNER_RISK_GUARD_REVIEW_FAILED, "risk guards must pass")


def review_controlled_offline_runner_read_only_decision(result: ControlledOfflineRunnerMinimalResult | Any) -> Finding:
    decision = _get(result, "read_only_decision")
    passed = bool(decision) and _get(decision, "read_only") is True and _get(decision, "order_submitted") is False and _get(decision, "position_mutated") is False
    return _finding("read_only_decision", passed, Risk.CONTROLLED_OFFLINE_RUNNER_READ_ONLY_DECISION_REVIEW_FAILED, "decision must remain read-only")


def review_controlled_offline_runner_journal(result: ControlledOfflineRunnerMinimalResult | Any) -> Finding:
    entries = _as_tuple(_get(result, "journal_entries", ()))
    passed = bool(entries) and all(_get(entry, "message") for entry in entries)
    return _finding("journal", passed, Risk.CONTROLLED_OFFLINE_RUNNER_JOURNAL_REVIEW_FAILED, "journal must be present in memory")


def review_controlled_offline_runner_metrics(result: ControlledOfflineRunnerMinimalResult | Any) -> Finding:
    metrics = _get(result, "metrics")
    passed = bool(metrics) and _get(metrics, "bar_count", 0) > 0 and _get(metrics, "real_order_count", 1) == 0 and _get(metrics, "account_access_count", 1) == 0 and _get(metrics, "data_access_count", 1) == 0
    return _finding("metrics", passed, Risk.CONTROLLED_OFFLINE_RUNNER_METRICS_REVIEW_FAILED, "metrics must exist and show no real actions")


def review_controlled_offline_runner_markdown_report(result: ControlledOfflineRunnerMinimalResult | Any) -> Finding:
    markdown = _get(_get(result, "report"), "markdown", "")
    passed = "Controlled Offline Runner Minimal Report" in markdown and "Boundary:" in markdown
    return _finding("markdown_report", passed, Risk.CONTROLLED_OFFLINE_RUNNER_REPORT_REVIEW_FAILED, "markdown report must describe decision and boundaries")


def review_controlled_offline_runner_json_report(result: ControlledOfflineRunnerMinimalResult | Any) -> Finding:
    json_report = _get(_get(result, "report"), "json", "")
    passed = '"decision"' in json_report and '"real_order_count":0' in json_report and '"offline_only":true' in json_report
    return _finding("json_report", passed, Risk.CONTROLLED_OFFLINE_RUNNER_REPORT_REVIEW_FAILED, "json report must include decision and no real orders")


def review_controlled_offline_runner_no_real_execution_boundaries(data: ControlledOfflineRunnerMinimalReviewInput | Mapping[str, Any] | Any) -> Finding:
    data = _coerce_input(data)
    result = data.minimal_result
    if result is None:
        return _finding("no_real_execution_boundaries", False, Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION, "offline boundaries must remain closed")
    if not validate_controlled_offline_runner_minimal_result_for_review(data):
        return Finding("no_real_execution_boundaries", True, 100, (), ("boundary review deferred until minimal result is approved",))
    input_ok = True if data.minimal_input is None else assert_controlled_offline_runner_no_real_execution_boundaries(data.minimal_input)
    passed = (
        input_ok
        and _get(result, "offline_only") is True
        and _get(result, "sandbox_only") is True
        and _get(result, "in_memory_only") is True
        and _get(result, "real_order_submitted") is False
        and _get(result, "real_account_accessed") is False
        and _get(result, "data_accessed") is False
    )
    return _finding("no_real_execution_boundaries", passed, Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION, "offline boundaries must remain closed")


def _all_findings(data: ControlledOfflineRunnerMinimalReviewInput) -> tuple[Finding, ...]:
    result = data.minimal_result
    return (
        review_controlled_offline_runner_determinism(data),
        review_controlled_offline_runner_market_scenario(result),
        review_controlled_offline_runner_account_snapshot(result),
        review_controlled_offline_runner_broker_snapshot(result),
        review_controlled_offline_runner_strategy_signal(result),
        review_controlled_offline_runner_risk_guards(result),
        review_controlled_offline_runner_read_only_decision(result),
        review_controlled_offline_runner_journal(result),
        review_controlled_offline_runner_metrics(result),
        review_controlled_offline_runner_markdown_report(result),
        review_controlled_offline_runner_json_report(result),
        review_controlled_offline_runner_no_real_execution_boundaries(data),
    )


def _map_minimal_boundary_risks(result: Any) -> tuple[Risk, ...]:
    mapped = []
    for risk in _as_tuple(_get(result, "risks", ())):
        name = _value(risk)
        if hasattr(Risk, name):
            mapped.append(getattr(Risk, name))
    return tuple(mapped)


def detect_controlled_offline_runner_minimal_review_risks(data: ControlledOfflineRunnerMinimalReviewInput | Mapping[str, Any] | Any) -> tuple[Risk, ...]:
    data = _coerce_input(data)
    risks: list[Risk] = []
    if not validate_controlled_offline_runner_minimal_result_for_review(data):
        risks.append(Risk.CONTROLLED_OFFLINE_RUNNER_MINIMAL_NOT_APPROVED)
    for finding in _all_findings(data):
        risks.extend(finding.risks)
    risks.extend(_map_minimal_boundary_risks(data.minimal_result))
    if data.synthetic_market_scenario_v1_requested:
        risks.append(Risk.PREMATURE_SYNTHETIC_MARKET_SCENARIO_V1)
    return _dedupe(risks)


def compute_controlled_offline_runner_minimal_review_score(data: ControlledOfflineRunnerMinimalReviewInput | Mapping[str, Any] | Any) -> ControlledOfflineRunnerMinimalReviewScore:
    data = _coerce_input(data)
    findings = _all_findings(data)
    minimal_result_score = 100 if validate_controlled_offline_runner_minimal_result_for_review(data) else 0
    scores = {finding.name: finding.score for finding in findings}
    parts = (
        minimal_result_score,
        scores["determinism"],
        scores["market_scenario"],
        scores["account_snapshot"],
        scores["broker_snapshot"],
        scores["strategy_signal"],
        scores["risk_guard"],
        scores["read_only_decision"],
        scores["journal"],
        scores["metrics"],
        scores["markdown_report"],
        scores["json_report"],
        scores["no_real_execution_boundaries"],
    )
    overall = round(sum(parts) / len(parts))
    return ControlledOfflineRunnerMinimalReviewScore(
        overall_score=overall,
        minimal_result_score=minimal_result_score,
        determinism_score=scores["determinism"],
        market_scenario_score=scores["market_scenario"],
        account_snapshot_score=scores["account_snapshot"],
        broker_snapshot_score=scores["broker_snapshot"],
        strategy_signal_score=scores["strategy_signal"],
        risk_guard_score=scores["risk_guard"],
        read_only_decision_score=scores["read_only_decision"],
        journal_score=scores["journal"],
        metrics_score=scores["metrics"],
        markdown_report_score=scores["markdown_report"],
        json_report_score=scores["json_report"],
        boundary_score=scores["no_real_execution_boundaries"],
    )


def generate_controlled_offline_runner_minimal_review_recommendations(risks: Iterable[Risk] | None = None) -> tuple[Recommendation, ...]:
    risks = tuple(risks or ())
    if not risks:
        return (
            Recommendation.RUN_CONTROLLED_OFFLINE_RUNNER_MINIMAL_REVIEW_TEST_SUITE,
            Recommendation.APPROVE_SYNTHETIC_MARKET_SCENARIO_V1,
        )
    mapping = {
        Risk.CONTROLLED_OFFLINE_RUNNER_MINIMAL_NOT_APPROVED: Recommendation.APPROVE_CONTROLLED_OFFLINE_RUNNER_MINIMAL_FIRST,
        Risk.CONTROLLED_OFFLINE_RUNNER_NOT_DETERMINISTIC: Recommendation.FIX_CONTROLLED_OFFLINE_RUNNER_DETERMINISM,
        Risk.CONTROLLED_OFFLINE_RUNNER_MARKET_SCENARIO_REVIEW_FAILED: Recommendation.FIX_CONTROLLED_OFFLINE_MARKET_SCENARIO,
        Risk.CONTROLLED_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_REVIEW_FAILED: Recommendation.FIX_CONTROLLED_OFFLINE_ACCOUNT_SNAPSHOT,
        Risk.CONTROLLED_OFFLINE_RUNNER_BROKER_SNAPSHOT_REVIEW_FAILED: Recommendation.FIX_CONTROLLED_OFFLINE_BROKER_SNAPSHOT,
        Risk.CONTROLLED_OFFLINE_RUNNER_STRATEGY_SIGNAL_REVIEW_FAILED: Recommendation.FIX_CONTROLLED_OFFLINE_STRATEGY_SIGNAL,
        Risk.CONTROLLED_OFFLINE_RUNNER_RISK_GUARD_REVIEW_FAILED: Recommendation.FIX_CONTROLLED_OFFLINE_RISK_GUARD,
        Risk.CONTROLLED_OFFLINE_RUNNER_READ_ONLY_DECISION_REVIEW_FAILED: Recommendation.FIX_CONTROLLED_OFFLINE_READ_ONLY_DECISION,
        Risk.CONTROLLED_OFFLINE_RUNNER_JOURNAL_REVIEW_FAILED: Recommendation.FIX_CONTROLLED_OFFLINE_JOURNAL,
        Risk.CONTROLLED_OFFLINE_RUNNER_METRICS_REVIEW_FAILED: Recommendation.FIX_CONTROLLED_OFFLINE_METRICS,
        Risk.CONTROLLED_OFFLINE_RUNNER_REPORT_REVIEW_FAILED: Recommendation.FIX_CONTROLLED_OFFLINE_REPORT,
        Risk.REAL_BROKER_BOUNDARY_VIOLATION: Recommendation.RESTORE_OFFLINE_REAL_BROKER_BOUNDARY,
        Risk.REAL_SECRET_BOUNDARY_VIOLATION: Recommendation.RESTORE_OFFLINE_SECRET_BOUNDARY,
        Risk.NETWORK_BOUNDARY_VIOLATION: Recommendation.RESTORE_OFFLINE_NETWORK_BOUNDARY,
        Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION: Recommendation.KEEP_READ_ONLY_NO_ORDER_DECISION,
        Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION: Recommendation.RESTORE_OFFLINE_ACCOUNT_BOUNDARY,
        Risk.DATA_ACCESS_BOUNDARY_VIOLATION: Recommendation.RESTORE_OFFLINE_DATA_BOUNDARY,
        Risk.PREMATURE_SYNTHETIC_MARKET_SCENARIO_V1: Recommendation.DELAY_SYNTHETIC_MARKET_SCENARIO_V1,
    }
    return _dedupe(mapping[risk] for risk in risks if risk in mapping)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_CONTROLLED_OFFLINE_RUNNER_MINIMAL_REVIEW
    boundary = {
        Risk.REAL_BROKER_BOUNDARY_VIOLATION,
        Risk.REAL_SECRET_BOUNDARY_VIOLATION,
        Risk.NETWORK_BOUNDARY_VIOLATION,
        Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION,
        Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION,
        Risk.DATA_ACCESS_BOUNDARY_VIOLATION,
        Risk.PREMATURE_SYNTHETIC_MARKET_SCENARIO_V1,
    }
    if any(risk in boundary for risk in risks):
        return Decision.BLOCK_CONTROLLED_OFFLINE_RUNNER_MINIMAL_REVIEW
    if Risk.CONTROLLED_OFFLINE_RUNNER_MINIMAL_NOT_APPROVED in risks:
        return Decision.REQUIRE_CONTROLLED_OFFLINE_RUNNER_MINIMAL_FIXES
    if Risk.CONTROLLED_OFFLINE_RUNNER_NOT_DETERMINISTIC in risks:
        return Decision.REQUIRE_CONTROLLED_OFFLINE_RUNNER_DETERMINISM_FIXES
    if Risk.CONTROLLED_OFFLINE_RUNNER_MARKET_SCENARIO_REVIEW_FAILED in risks:
        return Decision.REQUIRE_CONTROLLED_OFFLINE_RUNNER_MARKET_SCENARIO_FIXES
    if Risk.CONTROLLED_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_REVIEW_FAILED in risks:
        return Decision.REQUIRE_CONTROLLED_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_FIXES
    if Risk.CONTROLLED_OFFLINE_RUNNER_BROKER_SNAPSHOT_REVIEW_FAILED in risks:
        return Decision.REQUIRE_CONTROLLED_OFFLINE_RUNNER_BROKER_SNAPSHOT_FIXES
    if Risk.CONTROLLED_OFFLINE_RUNNER_STRATEGY_SIGNAL_REVIEW_FAILED in risks:
        return Decision.REQUIRE_CONTROLLED_OFFLINE_RUNNER_STRATEGY_SIGNAL_FIXES
    if Risk.CONTROLLED_OFFLINE_RUNNER_RISK_GUARD_REVIEW_FAILED in risks:
        return Decision.REQUIRE_CONTROLLED_OFFLINE_RUNNER_RISK_GUARD_FIXES
    if Risk.CONTROLLED_OFFLINE_RUNNER_READ_ONLY_DECISION_REVIEW_FAILED in risks:
        return Decision.REQUIRE_CONTROLLED_OFFLINE_RUNNER_READ_ONLY_DECISION_FIXES
    if Risk.CONTROLLED_OFFLINE_RUNNER_JOURNAL_REVIEW_FAILED in risks:
        return Decision.REQUIRE_CONTROLLED_OFFLINE_RUNNER_JOURNAL_FIXES
    if Risk.CONTROLLED_OFFLINE_RUNNER_METRICS_REVIEW_FAILED in risks:
        return Decision.REQUIRE_CONTROLLED_OFFLINE_RUNNER_METRICS_FIXES
    if Risk.CONTROLLED_OFFLINE_RUNNER_REPORT_REVIEW_FAILED in risks:
        return Decision.REQUIRE_CONTROLLED_OFFLINE_RUNNER_REPORT_FIXES
    return Decision.BLOCK_CONTROLLED_OFFLINE_RUNNER_MINIMAL_REVIEW


def _state_for(risks: tuple[Risk, ...], score: ControlledOfflineRunnerMinimalReviewScore) -> State:
    if Risk.CONTROLLED_OFFLINE_RUNNER_MINIMAL_NOT_APPROVED in risks:
        return State.CONTROLLED_OFFLINE_RUNNER_MINIMAL_REVIEW_INPUT_INVALID
    if risks:
        return State.CONTROLLED_OFFLINE_RUNNER_MINIMAL_REVIEW_BLOCKED
    if score.overall_score == 100:
        return State.READY_FOR_SYNTHETIC_MARKET_SCENARIO_V1
    if score.overall_score >= 70:
        return State.CONTROLLED_OFFLINE_RUNNER_MINIMAL_REVIEW_COMPLETED_WITH_WARNINGS
    return State.NOT_READY


def render_controlled_offline_runner_minimal_review_markdown(result: ControlledOfflineRunnerMinimalReviewResult) -> str:
    risks = ", ".join(_value(risk) for risk in result.risks) or "none"
    recs = ", ".join(_value(rec) for rec in result.recommendations) or "none"
    return "\n".join(
        (
            "# Controlled Offline Runner Minimal Review",
            f"- State: {result.state.value}",
            f"- Decision: {result.decision.value}",
            f"- Score: {result.score.overall_score}",
            f"- Risks: {risks}",
            f"- Recommendations: {recs}",
            "- Boundary: review only; no broker, no secret, no network, no order, no account access, no data access.",
            f"- Next phase: {result.next_phase}",
        )
    )


def review_controlled_offline_runner_minimal(data: ControlledOfflineRunnerMinimalReviewInput | Mapping[str, Any] | Any) -> ControlledOfflineRunnerMinimalReviewResult:
    data = _coerce_input(data)
    findings = _all_findings(data)
    score = compute_controlled_offline_runner_minimal_review_score(data)
    risks = detect_controlled_offline_runner_minimal_review_risks(data)
    recommendations = generate_controlled_offline_runner_minimal_review_recommendations(risks)
    result = ControlledOfflineRunnerMinimalReviewResult(
        state=_state_for(risks, score),
        decision=_decision_for(risks),
        score=score,
        risks=risks,
        recommendations=recommendations,
        findings=findings,
        markdown_report="",
        offline_only=True,
        review_only=True,
    )
    return ControlledOfflineRunnerMinimalReviewResult(
        **{**result.__dict__, "markdown_report": render_controlled_offline_runner_minimal_review_markdown(result)}
    )


__all__ = [
    "review_controlled_offline_runner_minimal",
    "validate_controlled_offline_runner_minimal_result_for_review",
    "review_controlled_offline_runner_determinism",
    "review_controlled_offline_runner_market_scenario",
    "review_controlled_offline_runner_account_snapshot",
    "review_controlled_offline_runner_broker_snapshot",
    "review_controlled_offline_runner_strategy_signal",
    "review_controlled_offline_runner_risk_guards",
    "review_controlled_offline_runner_read_only_decision",
    "review_controlled_offline_runner_journal",
    "review_controlled_offline_runner_metrics",
    "review_controlled_offline_runner_markdown_report",
    "review_controlled_offline_runner_json_report",
    "review_controlled_offline_runner_no_real_execution_boundaries",
    "compute_controlled_offline_runner_minimal_review_score",
    "detect_controlled_offline_runner_minimal_review_risks",
    "generate_controlled_offline_runner_minimal_review_recommendations",
    "render_controlled_offline_runner_minimal_review_markdown",
]
