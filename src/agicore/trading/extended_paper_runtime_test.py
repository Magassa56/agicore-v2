"""Offline extended multi-scenario tests for the AGIcore Paper Trading Runtime."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.extended_paper_runtime_test_models import (
    ExtendedPaperRuntimeTestDecision,
    ExtendedPaperRuntimeTestInput,
    ExtendedPaperRuntimeTestRecommendation,
    ExtendedPaperRuntimeTestResult,
    ExtendedPaperRuntimeTestRisk,
    ExtendedPaperRuntimeTestScore,
    ExtendedPaperRuntimeTestState,
    ExtendedRuntimeConsistencyReview,
    ExtendedRuntimeScenarioResult,
)
from agicore.trading.paper_trading_runtime import run_paper_trading_runtime
from agicore.trading.paper_trading_runtime_models import PaperTradingRuntimeInput


def _coerce_input(data: ExtendedPaperRuntimeTestInput | Mapping[str, Any]) -> ExtendedPaperRuntimeTestInput:
    if isinstance(data, ExtendedPaperRuntimeTestInput):
        return data
    return ExtendedPaperRuntimeTestInput(**dict(data))


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


def _upstream_items(data: ExtendedPaperRuntimeTestInput) -> tuple[Any, ...]:
    return (
        data.paper_runtime_test_run,
        data.paper_trading_runtime,
        data.paper_runtime_integration_review,
        data.paper_trading_runtime_design,
        data.paper_runtime_decision_review,
        data.full_paper_session,
        data.simulated_market_session,
        data.mock_alpaca_session,
        data.mock_connectivity_layer,
        data.observability_verification,
        data.rollback_verification,
        data.kill_switch_verification,
        data.human_validated_paper_session,
        data.supervised_paper_session,
    )


def _upstream_risks(data: ExtendedPaperRuntimeTestInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: ExtendedPaperRuntimeTestInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _runtime_input(data: ExtendedPaperRuntimeTestInput, suffix: str, **overrides: Any) -> PaperTradingRuntimeInput:
    payload = {
        "paper_trading_runtime_design": data.paper_trading_runtime_design,
        "paper_runtime_decision_review": data.paper_runtime_decision_review,
        "full_paper_session": data.full_paper_session,
        "simulated_market_session": data.simulated_market_session,
        "mock_alpaca_session": data.mock_alpaca_session,
        "mock_connectivity_layer": data.mock_connectivity_layer,
        "observability_verification": data.observability_verification,
        "rollback_verification": data.rollback_verification,
        "kill_switch_verification": data.kill_switch_verification,
        "human_validated_paper_session": data.human_validated_paper_session,
        "supervised_paper_session": data.supervised_paper_session,
        "session_id": f"extended-paper-runtime-{suffix}",
        "symbol": "AGICORE.EXT.PAPER",
        "market_price": 101.0,
        "previous_price": 100.0,
        "quantity": 1.0,
        "approved_by_human": True,
        "operator_confirmed": True,
        "session_authorized": True,
        "safety_gate_enabled": True,
        "risk_limits_enforced": True,
        "paper_order_not_routed": True,
        "journal_enabled": True,
        "observability_enabled": True,
        "rollback_hook_available": True,
        "kill_switch_hook_available": True,
        "offline_mode_enforced": True,
        "sandbox_mode_enforced": True,
        "no_real_broker": True,
        "no_api_key_read": True,
        "no_http_transport": True,
        "no_websocket_transport": True,
        "no_socket_transport": True,
        "no_external_api": True,
        "no_real_order": True,
    }
    payload.update(overrides)
    return PaperTradingRuntimeInput(**payload)


def _scenario(
    name: str,
    runtime_result: Any,
    expected_state: str,
    risk: ExtendedPaperRuntimeTestRisk,
    handled: bool,
    score_override: int | None = None,
    details: tuple[str, ...] = (),
) -> ExtendedRuntimeScenarioResult:
    actual_state = _value(_get(runtime_result, "state"))
    score = _clamp(score_override if score_override is not None else (100 if handled else 0))
    risks = () if handled and score >= 85 else (risk,)
    return ExtendedRuntimeScenarioResult(name, score, not risks, expected_state, actual_state, handled, risks, runtime_result, details)


def run_nominal_runtime_scenario(data: ExtendedPaperRuntimeTestInput | Mapping[str, Any]) -> ExtendedRuntimeScenarioResult:
    data = _coerce_input(data)
    result = run_paper_trading_runtime(_runtime_input(data, "nominal"))
    handled = _value(_get(result, "state")) == "COMPLETED" and _get(result, "offline_only") is True and not _as_tuple(_get(result, "risks", ()))
    return _scenario("nominal", result, "COMPLETED", ExtendedPaperRuntimeTestRisk.NOMINAL_SCENARIO_FAILURE, handled, data.nominal_score)


def run_safety_gate_block_scenario(data: ExtendedPaperRuntimeTestInput | Mapping[str, Any]) -> ExtendedRuntimeScenarioResult:
    data = _coerce_input(data)
    result = run_paper_trading_runtime(_runtime_input(data, "safety-gate-block", risk_limits_enforced=False))
    handled = _value(_get(result, "state")) == "FAILED_SAFE" and _contains(_get(result, "risks", ()), "SAFETY_GATE_FAILURE")
    return _scenario("safety_gate_block", result, "FAILED_SAFE", ExtendedPaperRuntimeTestRisk.SAFETY_GATE_BLOCK_FAILURE, handled, data.safety_gate_block_score)


def run_rollback_scenario(data: ExtendedPaperRuntimeTestInput | Mapping[str, Any]) -> ExtendedRuntimeScenarioResult:
    data = _coerce_input(data)
    result = run_paper_trading_runtime(_runtime_input(data, "rollback", rollback_requested=True))
    handled = _value(_get(result, "state")) == "STOPPED_BY_ROLLBACK" and _get(_get(result, "rollback_hook"), "passed") is True
    return _scenario("rollback", result, "STOPPED_BY_ROLLBACK", ExtendedPaperRuntimeTestRisk.ROLLBACK_SCENARIO_FAILURE, handled, data.rollback_score)


def run_kill_switch_scenario(data: ExtendedPaperRuntimeTestInput | Mapping[str, Any]) -> ExtendedRuntimeScenarioResult:
    data = _coerce_input(data)
    result = run_paper_trading_runtime(_runtime_input(data, "kill-switch", kill_switch_triggered=True))
    handled = _value(_get(result, "state")) == "STOPPED_BY_KILL_SWITCH" and _get(_get(result, "kill_switch_hook"), "passed") is True
    return _scenario("kill_switch", result, "STOPPED_BY_KILL_SWITCH", ExtendedPaperRuntimeTestRisk.KILL_SWITCH_SCENARIO_FAILURE, handled, data.kill_switch_score)


def run_human_supervision_pause_scenario(data: ExtendedPaperRuntimeTestInput | Mapping[str, Any]) -> ExtendedRuntimeScenarioResult:
    data = _coerce_input(data)
    result = run_paper_trading_runtime(_runtime_input(data, "human-pause", supervision_pause_requested=True))
    handled = _value(_get(result, "state")) == "PAUSED_BY_SUPERVISION" and _contains(_get(result, "risks", ()), "HUMAN_SUPERVISION_FAILURE")
    return _scenario("human_supervision_pause", result, "PAUSED_BY_SUPERVISION", ExtendedPaperRuntimeTestRisk.HUMAN_SUPERVISION_PAUSE_FAILURE, handled, data.human_supervision_pause_score)


def run_journal_failure_scenario(data: ExtendedPaperRuntimeTestInput | Mapping[str, Any]) -> ExtendedRuntimeScenarioResult:
    data = _coerce_input(data)
    result = run_paper_trading_runtime(_runtime_input(data, "journal-failure", force_journal_failure=True))
    handled = _value(_get(result, "state")) == "FAILED_SAFE" and _contains(_get(result, "risks", ()), "JOURNAL_WRITE_FAILURE")
    return _scenario("journal_failure", result, "FAILED_SAFE", ExtendedPaperRuntimeTestRisk.JOURNAL_FAILURE_UNHANDLED, handled, data.journal_failure_score)


def run_observability_gap_scenario(data: ExtendedPaperRuntimeTestInput | Mapping[str, Any]) -> ExtendedRuntimeScenarioResult:
    data = _coerce_input(data)
    result = run_paper_trading_runtime(_runtime_input(data, "observability-gap", force_observability_failure=True))
    handled = _value(_get(result, "state")) == "FAILED_SAFE" and _contains(_get(result, "risks", ()), "OBSERVABILITY_EMIT_FAILURE")
    return _scenario("observability_gap", result, "FAILED_SAFE", ExtendedPaperRuntimeTestRisk.OBSERVABILITY_GAP_UNHANDLED, handled, data.observability_gap_score)


def run_runtime_state_drift_scenario(data: ExtendedPaperRuntimeTestInput | Mapping[str, Any]) -> ExtendedRuntimeScenarioResult:
    data = _coerce_input(data)
    result = run_paper_trading_runtime(_runtime_input(data, "state-drift", no_http_transport=False))
    handled = _value(_get(result, "state")) == "FAILED_SAFE" and _contains(_get(result, "risks", ()), "RUNTIME_STATE_DRIFT", "RUNTIME_INITIALIZATION_FAILURE")
    return _scenario("runtime_state_drift", result, "FAILED_SAFE", ExtendedPaperRuntimeTestRisk.RUNTIME_STATE_DRIFT_UNHANDLED, handled, data.runtime_state_drift_score)


def run_extended_runtime_scenarios(data: ExtendedPaperRuntimeTestInput | Mapping[str, Any]) -> tuple[ExtendedRuntimeScenarioResult, ...]:
    data = _coerce_input(data)
    return (
        run_nominal_runtime_scenario(data),
        run_safety_gate_block_scenario(data),
        run_rollback_scenario(data),
        run_kill_switch_scenario(data),
        run_human_supervision_pause_scenario(data),
        run_journal_failure_scenario(data),
        run_observability_gap_scenario(data),
        run_runtime_state_drift_scenario(data),
    )


def verify_multi_scenario_consistency(data: ExtendedPaperRuntimeTestInput | Mapping[str, Any], scenarios: tuple[ExtendedRuntimeScenarioResult, ...] = ()) -> ExtendedRuntimeConsistencyReview:
    data = _coerce_input(data)
    if not scenarios:
        scenarios = run_extended_runtime_scenarios(data)
    names = tuple(scenario.name for scenario in scenarios)
    unique_names = len(set(names)) == len(names)
    offline = all(_get(scenario.runtime_result, "offline_only") is True or scenario.name == "runtime_state_drift" for scenario in scenarios)
    reports = all(_get(scenario.runtime_result, "report") is not None for scenario in scenarios)
    repeatable = data.scenarios_repeatable is True
    passed = unique_names and offline and reports and repeatable and all(scenario.handled for scenario in scenarios)
    score = data.multi_scenario_consistency_score if data.multi_scenario_consistency_score is not None else _average(
        (_bool_score(unique_names), _bool_score(offline), _bool_score(reports), _bool_score(repeatable), _bool_score(all(scenario.handled for scenario in scenarios)))
    )
    risks: list[ExtendedPaperRuntimeTestRisk] = []
    if not (unique_names and offline and reports and all(scenario.handled for scenario in scenarios)):
        risks.append(ExtendedPaperRuntimeTestRisk.MULTI_SCENARIO_INCONSISTENCY)
    if not repeatable:
        risks.append(ExtendedPaperRuntimeTestRisk.EXTENDED_TEST_NOT_REPEATABLE)
    details = (f"scenario_count={len(scenarios)}", f"unique_names={unique_names}", f"offline={offline}", f"reports={reports}", f"repeatable={repeatable}")
    return ExtendedRuntimeConsistencyReview(_clamp(score), not risks and score >= 85, _dedupe(risks), details)


def _offline_boundary(data: ExtendedPaperRuntimeTestInput) -> bool:
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
        and not _has_upstream_risk(data, "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK", "BROKER", "EXTERNAL_DEPENDENCY")
    )


def detect_extended_runtime_risks(
    data: ExtendedPaperRuntimeTestInput | Mapping[str, Any],
    scenarios: tuple[ExtendedRuntimeScenarioResult, ...] = (),
    consistency: ExtendedRuntimeConsistencyReview | None = None,
) -> tuple[ExtendedPaperRuntimeTestRisk, ...]:
    data = _coerce_input(data)
    if not scenarios:
        scenarios = run_extended_runtime_scenarios(data)
    consistency = consistency or verify_multi_scenario_consistency(data, scenarios)
    risks: list[ExtendedPaperRuntimeTestRisk] = []
    for scenario in scenarios:
        risks.extend(scenario.risks)
    risks.extend(consistency.risks)
    if data.extended_test_requested is not True or not _offline_boundary(data):
        risks.append(ExtendedPaperRuntimeTestRisk.RUNTIME_STABILITY_RISK)
    if _has_upstream_risk(data, "DRIFT", "STATE_CORRUPTION", "RUNTIME_STABILITY", "INCONSISTENCY"):
        risks.append(ExtendedPaperRuntimeTestRisk.RUNTIME_STABILITY_RISK)
    return _dedupe(risks)


def compute_extended_runtime_score(
    data: ExtendedPaperRuntimeTestInput | Mapping[str, Any],
    risks: tuple[ExtendedPaperRuntimeTestRisk, ...] = (),
    scenarios: tuple[ExtendedRuntimeScenarioResult, ...] = (),
    consistency: ExtendedRuntimeConsistencyReview | None = None,
) -> ExtendedPaperRuntimeTestScore:
    data = _coerce_input(data)
    if not scenarios:
        scenarios = run_extended_runtime_scenarios(data)
    consistency = consistency or verify_multi_scenario_consistency(data, scenarios)
    scores = tuple(scenario.score for scenario in scenarios) + (consistency.score,)
    overall = _clamp(_average(scores) - min(80, len(set(risks)) * 5))
    for risk, cap in {
        ExtendedPaperRuntimeTestRisk.NOMINAL_SCENARIO_FAILURE: 45,
        ExtendedPaperRuntimeTestRisk.ROLLBACK_SCENARIO_FAILURE: 55,
        ExtendedPaperRuntimeTestRisk.KILL_SWITCH_SCENARIO_FAILURE: 50,
        ExtendedPaperRuntimeTestRisk.RUNTIME_STATE_DRIFT_UNHANDLED: 45,
        ExtendedPaperRuntimeTestRisk.MULTI_SCENARIO_INCONSISTENCY: 60,
        ExtendedPaperRuntimeTestRisk.EXTENDED_TEST_NOT_REPEATABLE: 65,
        ExtendedPaperRuntimeTestRisk.RUNTIME_STABILITY_RISK: 40,
    }.items():
        if risk in risks:
            overall = min(overall, cap)
    return ExtendedPaperRuntimeTestScore(overall, *(scenario.score for scenario in scenarios), consistency.score)


def _select_decision(score: int, risks: tuple[ExtendedPaperRuntimeTestRisk, ...], ready_for_stabilization: bool | None) -> ExtendedPaperRuntimeTestDecision:
    if ExtendedPaperRuntimeTestRisk.RUNTIME_STABILITY_RISK in risks or ExtendedPaperRuntimeTestRisk.NOMINAL_SCENARIO_FAILURE in risks or score < 45:
        return ExtendedPaperRuntimeTestDecision.EXTENDED_TEST_BLOCKED
    hard = {
        ExtendedPaperRuntimeTestRisk.ROLLBACK_SCENARIO_FAILURE,
        ExtendedPaperRuntimeTestRisk.KILL_SWITCH_SCENARIO_FAILURE,
        ExtendedPaperRuntimeTestRisk.RUNTIME_STATE_DRIFT_UNHANDLED,
        ExtendedPaperRuntimeTestRisk.MULTI_SCENARIO_INCONSISTENCY,
    }
    if hard.intersection(risks) or len(set(risks)) >= 4:
        return ExtendedPaperRuntimeTestDecision.EXTENDED_TEST_REVIEW_REQUIRED
    if risks:
        return ExtendedPaperRuntimeTestDecision.EXTENDED_TEST_PARTIALLY_READY
    if ready_for_stabilization is True and score >= 94:
        return ExtendedPaperRuntimeTestDecision.READY_FOR_PAPER_RUNTIME_STABILIZATION_REVIEW
    if score >= 90:
        return ExtendedPaperRuntimeTestDecision.EXTENDED_TEST_COMPLETED
    if score >= 85:
        return ExtendedPaperRuntimeTestDecision.EXTENDED_TEST_READY
    return ExtendedPaperRuntimeTestDecision.EXTENDED_TEST_PARTIALLY_READY


def _select_state(decision: ExtendedPaperRuntimeTestDecision) -> ExtendedPaperRuntimeTestState:
    mapping = {
        ExtendedPaperRuntimeTestDecision.EXTENDED_TEST_BLOCKED: ExtendedPaperRuntimeTestState.NOT_READY,
        ExtendedPaperRuntimeTestDecision.EXTENDED_TEST_REVIEW_REQUIRED: ExtendedPaperRuntimeTestState.EXTENDED_TEST_REVIEW_REQUIRED,
        ExtendedPaperRuntimeTestDecision.EXTENDED_TEST_PARTIALLY_READY: ExtendedPaperRuntimeTestState.EXTENDED_TEST_PARTIALLY_READY,
        ExtendedPaperRuntimeTestDecision.EXTENDED_TEST_READY: ExtendedPaperRuntimeTestState.EXTENDED_TEST_READY,
        ExtendedPaperRuntimeTestDecision.EXTENDED_TEST_COMPLETED: ExtendedPaperRuntimeTestState.EXTENDED_TEST_COMPLETED,
        ExtendedPaperRuntimeTestDecision.READY_FOR_PAPER_RUNTIME_STABILIZATION_REVIEW: ExtendedPaperRuntimeTestState.READY_FOR_PAPER_RUNTIME_STABILIZATION_REVIEW,
    }
    return mapping[decision]


def generate_extended_runtime_recommendations(
    risks: tuple[ExtendedPaperRuntimeTestRisk, ...],
    decision: ExtendedPaperRuntimeTestDecision | None = None,
) -> tuple[ExtendedPaperRuntimeTestRecommendation, ...]:
    recommendations: list[ExtendedPaperRuntimeTestRecommendation] = []
    if risks:
        recommendations.append(ExtendedPaperRuntimeTestRecommendation.HOLD_STABILIZATION_REVIEW_APPROVAL)
    mapping = {
        ExtendedPaperRuntimeTestRisk.NOMINAL_SCENARIO_FAILURE: ExtendedPaperRuntimeTestRecommendation.REPAIR_NOMINAL_SCENARIO,
        ExtendedPaperRuntimeTestRisk.SAFETY_GATE_BLOCK_FAILURE: ExtendedPaperRuntimeTestRecommendation.REPAIR_SAFETY_GATE_BLOCK_HANDLING,
        ExtendedPaperRuntimeTestRisk.ROLLBACK_SCENARIO_FAILURE: ExtendedPaperRuntimeTestRecommendation.REPAIR_ROLLBACK_SCENARIO,
        ExtendedPaperRuntimeTestRisk.KILL_SWITCH_SCENARIO_FAILURE: ExtendedPaperRuntimeTestRecommendation.REPAIR_KILL_SWITCH_SCENARIO,
        ExtendedPaperRuntimeTestRisk.HUMAN_SUPERVISION_PAUSE_FAILURE: ExtendedPaperRuntimeTestRecommendation.REPAIR_HUMAN_SUPERVISION_PAUSE,
        ExtendedPaperRuntimeTestRisk.JOURNAL_FAILURE_UNHANDLED: ExtendedPaperRuntimeTestRecommendation.HANDLE_JOURNAL_FAILURE,
        ExtendedPaperRuntimeTestRisk.OBSERVABILITY_GAP_UNHANDLED: ExtendedPaperRuntimeTestRecommendation.HANDLE_OBSERVABILITY_GAP,
        ExtendedPaperRuntimeTestRisk.RUNTIME_STATE_DRIFT_UNHANDLED: ExtendedPaperRuntimeTestRecommendation.HANDLE_RUNTIME_STATE_DRIFT,
        ExtendedPaperRuntimeTestRisk.MULTI_SCENARIO_INCONSISTENCY: ExtendedPaperRuntimeTestRecommendation.RECONCILE_MULTI_SCENARIO_CONSISTENCY,
        ExtendedPaperRuntimeTestRisk.EXTENDED_TEST_NOT_REPEATABLE: ExtendedPaperRuntimeTestRecommendation.STABILIZE_REPEATABILITY,
        ExtendedPaperRuntimeTestRisk.RUNTIME_STABILITY_RISK: ExtendedPaperRuntimeTestRecommendation.REPAIR_RUNTIME_STABILITY,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(ExtendedPaperRuntimeTestRecommendation.RUN_EXTENDED_PAPER_RUNTIME_TEST_SUITE)
    if decision == ExtendedPaperRuntimeTestDecision.READY_FOR_PAPER_RUNTIME_STABILIZATION_REVIEW:
        recommendations.append(ExtendedPaperRuntimeTestRecommendation.APPROVE_STABILIZATION_REVIEW_AFTER_MANUAL_REVIEW)
    return _dedupe(recommendations)


def evaluate_extended_paper_runtime_test(data: ExtendedPaperRuntimeTestInput | Mapping[str, Any]) -> ExtendedPaperRuntimeTestResult:
    data = _coerce_input(data)
    scenarios = run_extended_runtime_scenarios(data)
    consistency = verify_multi_scenario_consistency(data, scenarios)
    risks = detect_extended_runtime_risks(data, scenarios, consistency)
    score = compute_extended_runtime_score(data, risks, scenarios, consistency)
    decision = _select_decision(score.overall_score, risks, data.ready_for_stabilization_review)
    state = _select_state(decision)
    recommendations = generate_extended_runtime_recommendations(risks, decision)
    offline_only = _offline_boundary(data)
    summary = f"{state.value}: decision={decision.value}, score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return ExtendedPaperRuntimeTestResult(state, decision, score.overall_score, score, risks, *scenarios, consistency, recommendations, offline_only, summary)


def render_extended_paper_runtime_test_markdown(result: ExtendedPaperRuntimeTestResult) -> str:
    lines = [
        "# AGIcore Extended Paper Runtime Test",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Score: {result.extended_runtime_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Runtime Scenarios",
    ]
    scenarios = (
        result.nominal_scenario,
        result.safety_gate_block_scenario,
        result.rollback_scenario,
        result.kill_switch_scenario,
        result.human_supervision_pause_scenario,
        result.journal_failure_scenario,
        result.observability_gap_scenario,
        result.runtime_state_drift_scenario,
    )
    for scenario in scenarios:
        lines.append(
            f"- {scenario.name}: passed={scenario.passed}, score={scenario.score}/100, "
            f"expected={scenario.expected_state}, actual={scenario.actual_state}, risks={', '.join(risk.value for risk in scenario.risks) or 'none'}"
        )
        lines.extend(f"  - {detail}" for detail in scenario.details)
    lines.extend(("", "# Multi Scenario Consistency", f"- passed={result.consistency_review.passed}, score={result.consistency_review.score}/100"))
    lines.extend(f"  - {detail}" for detail in result.consistency_review.details)
    lines.append("")
    lines.append("# Extended Runtime Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Extended Runtime Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_extended_runtime_score",
    "detect_extended_runtime_risks",
    "evaluate_extended_paper_runtime_test",
    "generate_extended_runtime_recommendations",
    "render_extended_paper_runtime_test_markdown",
    "run_extended_runtime_scenarios",
    "run_human_supervision_pause_scenario",
    "run_journal_failure_scenario",
    "run_kill_switch_scenario",
    "run_nominal_runtime_scenario",
    "run_observability_gap_scenario",
    "run_rollback_scenario",
    "run_runtime_state_drift_scenario",
    "run_safety_gate_block_scenario",
    "verify_multi_scenario_consistency",
]
