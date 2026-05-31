"""Offline/sandbox test run verifier for the AGIcore Paper Trading Runtime."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_runtime_test_run_models import (
    PaperRuntimeTestCheck,
    PaperRuntimeTestRunDecision,
    PaperRuntimeTestRunInput,
    PaperRuntimeTestRunRecommendation,
    PaperRuntimeTestRunResult,
    PaperRuntimeTestRunRisk,
    PaperRuntimeTestRunScore,
    PaperRuntimeTestRunState,
    PaperRuntimeTestScenario,
)
from agicore.trading.paper_trading_runtime import run_paper_trading_runtime
from agicore.trading.paper_trading_runtime_models import PaperTradingRuntimeInput


def _coerce_input(data: PaperRuntimeTestRunInput | Mapping[str, Any]) -> PaperRuntimeTestRunInput:
    if isinstance(data, PaperRuntimeTestRunInput):
        return data
    return PaperRuntimeTestRunInput(**dict(data))


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


def _upstream_items(data: PaperRuntimeTestRunInput) -> tuple[Any, ...]:
    return (
        data.paper_runtime_integration_review,
        data.paper_trading_runtime,
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


def _upstream_risks(data: PaperRuntimeTestRunInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperRuntimeTestRunInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _check(name: str, score: int, risk: PaperRuntimeTestRunRisk, failed: bool, details: tuple[str, ...] = ()) -> PaperRuntimeTestCheck:
    risks = (risk,) if failed or score < 85 else ()
    return PaperRuntimeTestCheck(name, _clamp(score), not risks and score >= 85, risks, details)


def _default_runtime_input(data: PaperRuntimeTestRunInput) -> PaperTradingRuntimeInput:
    return PaperTradingRuntimeInput(
        paper_trading_runtime_design=data.paper_trading_runtime_design,
        paper_runtime_decision_review=data.paper_runtime_decision_review,
        full_paper_session=data.full_paper_session,
        simulated_market_session=data.simulated_market_session,
        mock_alpaca_session=data.mock_alpaca_session,
        mock_connectivity_layer=data.mock_connectivity_layer,
        observability_verification=data.observability_verification,
        rollback_verification=data.rollback_verification,
        kill_switch_verification=data.kill_switch_verification,
        human_validated_paper_session=data.human_validated_paper_session,
        supervised_paper_session=data.supervised_paper_session,
        session_id="paper-runtime-test-run",
        symbol="AGICORE.TEST.PAPER",
        market_price=101.0,
        previous_price=100.0,
        quantity=1.0,
        approved_by_human=True,
        operator_confirmed=True,
        session_authorized=True,
        safety_gate_enabled=True,
        risk_limits_enforced=True,
        paper_order_not_routed=True,
        journal_enabled=True,
        observability_enabled=True,
        rollback_hook_available=True,
        kill_switch_hook_available=True,
        offline_mode_enforced=True,
        sandbox_mode_enforced=True,
        no_real_broker=True,
        no_api_key_read=True,
        no_http_transport=True,
        no_websocket_transport=True,
        no_socket_transport=True,
        no_external_api=True,
        no_real_order=True,
    )


def _runtime_input(data: PaperRuntimeTestRunInput) -> Any:
    if data.runtime_input is not None:
        return data.runtime_input
    return _default_runtime_input(data)


def run_runtime_test_scenario(data: PaperRuntimeTestRunInput | Mapping[str, Any]) -> PaperRuntimeTestScenario:
    data = _coerce_input(data)
    runtime_result = run_paper_trading_runtime(_runtime_input(data))
    checks = (
        verify_runtime_start(data, runtime_result),
        verify_runtime_session_init(data, runtime_result),
        verify_runtime_market_cycle(data, runtime_result),
        verify_runtime_signal_cycle(data, runtime_result),
        verify_runtime_decision_cycle(data, runtime_result),
        verify_runtime_safety_gate(data, runtime_result),
        verify_runtime_paper_order_simulation(data, runtime_result),
        verify_runtime_position_pnl_update(data, runtime_result),
        verify_runtime_journal_output(data, runtime_result),
        verify_runtime_observability_output(data, runtime_result),
        verify_runtime_rollback_hook(data, runtime_result),
        verify_runtime_kill_switch_hook(data, runtime_result),
        verify_runtime_human_supervision_hook(data, runtime_result),
        verify_runtime_stop(data, runtime_result),
    )
    return PaperRuntimeTestScenario(runtime_result, checks, _offline_boundary(data, runtime_result))


def verify_runtime_start(data: PaperRuntimeTestRunInput | Mapping[str, Any], runtime_result: Any | None = None) -> PaperRuntimeTestCheck:
    data = _coerce_input(data)
    runtime_result = runtime_result or run_paper_trading_runtime(_runtime_input(data))
    failed = data.test_run_requested is not True or runtime_result is None or _get(runtime_result, "offline_only") is not True
    score = data.runtime_start_score if data.runtime_start_score is not None else _average((_bool_score(data.test_run_requested), 100 if runtime_result is not None else 0, _bool_score(_get(runtime_result, "offline_only"))))
    return _check("runtime_start", score, PaperRuntimeTestRunRisk.RUNTIME_START_FAILURE, failed, (f"runtime_present={runtime_result is not None}",))


def verify_runtime_session_init(data: PaperRuntimeTestRunInput | Mapping[str, Any], runtime_result: Any | None = None) -> PaperRuntimeTestCheck:
    data = _coerce_input(data)
    runtime_result = runtime_result or run_paper_trading_runtime(_runtime_input(data))
    step = _get(runtime_result, "session")
    failed = _get(step, "passed") is not True
    score = data.session_init_score if data.session_init_score is not None else int(_get(step, "score", 0) or 0)
    return _check("session_init", score, PaperRuntimeTestRunRisk.SESSION_INIT_FAILURE, failed, _as_tuple(_get(step, "events", ())))


def verify_runtime_market_cycle(data: PaperRuntimeTestRunInput | Mapping[str, Any], runtime_result: Any | None = None) -> PaperRuntimeTestCheck:
    data = _coerce_input(data)
    runtime_result = runtime_result or run_paper_trading_runtime(_runtime_input(data))
    step = _get(runtime_result, "market_cycle")
    failed = _get(step, "passed") is not True or _get(runtime_result, "market_snapshot") is None
    score = data.market_cycle_score if data.market_cycle_score is not None else int(_get(step, "score", 0) or 0)
    return _check("market_cycle", score, PaperRuntimeTestRunRisk.MARKET_CYCLE_FAILURE, failed, _as_tuple(_get(step, "events", ())))


def verify_runtime_signal_cycle(data: PaperRuntimeTestRunInput | Mapping[str, Any], runtime_result: Any | None = None) -> PaperRuntimeTestCheck:
    data = _coerce_input(data)
    runtime_result = runtime_result or run_paper_trading_runtime(_runtime_input(data))
    step = _get(runtime_result, "signal_cycle")
    failed = _get(step, "passed") is not True or _get(runtime_result, "signal") is None
    score = data.signal_cycle_score if data.signal_cycle_score is not None else int(_get(step, "score", 0) or 0)
    return _check("signal_cycle", score, PaperRuntimeTestRunRisk.SIGNAL_CYCLE_FAILURE, failed, _as_tuple(_get(step, "events", ())))


def verify_runtime_decision_cycle(data: PaperRuntimeTestRunInput | Mapping[str, Any], runtime_result: Any | None = None) -> PaperRuntimeTestCheck:
    data = _coerce_input(data)
    runtime_result = runtime_result or run_paper_trading_runtime(_runtime_input(data))
    step = _get(runtime_result, "decision_cycle")
    failed = _get(step, "passed") is not True or _get(runtime_result, "decision") is None
    score = data.decision_cycle_score if data.decision_cycle_score is not None else int(_get(step, "score", 0) or 0)
    return _check("decision_cycle", score, PaperRuntimeTestRunRisk.DECISION_CYCLE_FAILURE, failed, _as_tuple(_get(step, "events", ())))


def verify_runtime_safety_gate(data: PaperRuntimeTestRunInput | Mapping[str, Any], runtime_result: Any | None = None) -> PaperRuntimeTestCheck:
    data = _coerce_input(data)
    runtime_result = runtime_result or run_paper_trading_runtime(_runtime_input(data))
    step = _get(runtime_result, "safety_gate")
    failed = _get(step, "passed") is not True or _has_upstream_risk(data, "SAFETY_BYPASS", "UNSAFE_ORDER")
    score = data.safety_gate_score if data.safety_gate_score is not None else int(_get(step, "score", 0) or 0)
    return _check("safety_gate", score, PaperRuntimeTestRunRisk.SAFETY_GATE_FAILURE, failed, _as_tuple(_get(step, "events", ())))


def verify_runtime_paper_order_simulation(data: PaperRuntimeTestRunInput | Mapping[str, Any], runtime_result: Any | None = None) -> PaperRuntimeTestCheck:
    data = _coerce_input(data)
    runtime_result = runtime_result or run_paper_trading_runtime(_runtime_input(data))
    step = _get(runtime_result, "paper_order_simulation")
    order = _get(runtime_result, "order")
    failed = _get(step, "passed") is not True or order is None or _get(order, "routed") is not False or _has_upstream_risk(data, "REAL_ORDER", "BROKER")
    score = data.paper_order_simulation_score if data.paper_order_simulation_score is not None else int(_get(step, "score", 0) or 0)
    return _check("paper_order_simulation", score, PaperRuntimeTestRunRisk.PAPER_ORDER_SIMULATION_FAILURE, failed, _as_tuple(_get(step, "events", ())))


def verify_runtime_position_pnl_update(data: PaperRuntimeTestRunInput | Mapping[str, Any], runtime_result: Any | None = None) -> PaperRuntimeTestCheck:
    data = _coerce_input(data)
    runtime_result = runtime_result or run_paper_trading_runtime(_runtime_input(data))
    step = _get(runtime_result, "position_pnl_update")
    failed = _get(step, "passed") is not True or _get(runtime_result, "position") is None
    score = data.position_pnl_update_score if data.position_pnl_update_score is not None else int(_get(step, "score", 0) or 0)
    return _check("position_pnl_update", score, PaperRuntimeTestRunRisk.POSITION_PNL_UPDATE_FAILURE, failed, _as_tuple(_get(step, "events", ())))


def verify_runtime_journal_output(data: PaperRuntimeTestRunInput | Mapping[str, Any], runtime_result: Any | None = None) -> PaperRuntimeTestCheck:
    data = _coerce_input(data)
    runtime_result = runtime_result or run_paper_trading_runtime(_runtime_input(data))
    step = _get(runtime_result, "journal")
    entries = _as_tuple(_get(runtime_result, "journal_entries", ()))
    failed = _get(step, "passed") is not True or len(entries) <= 0
    score = data.journal_output_score if data.journal_output_score is not None else int(_get(step, "score", 0) or 0)
    return _check("journal_output", score, PaperRuntimeTestRunRisk.JOURNAL_OUTPUT_FAILURE, failed, (f"journal_entries={len(entries)}",))


def verify_runtime_observability_output(data: PaperRuntimeTestRunInput | Mapping[str, Any], runtime_result: Any | None = None) -> PaperRuntimeTestCheck:
    data = _coerce_input(data)
    runtime_result = runtime_result or run_paper_trading_runtime(_runtime_input(data))
    step = _get(runtime_result, "observability")
    events = _as_tuple(_get(runtime_result, "observability_events", ()))
    failed = _get(step, "passed") is not True or len(events) <= 0 or _has_upstream_risk(data, "OBSERVABILITY")
    score = data.observability_output_score if data.observability_output_score is not None else int(_get(step, "score", 0) or 0)
    return _check("observability_output", score, PaperRuntimeTestRunRisk.OBSERVABILITY_OUTPUT_FAILURE, failed, (f"observability_events={len(events)}",))


def verify_runtime_rollback_hook(data: PaperRuntimeTestRunInput | Mapping[str, Any], runtime_result: Any | None = None) -> PaperRuntimeTestCheck:
    data = _coerce_input(data)
    runtime_result = runtime_result or run_paper_trading_runtime(_runtime_input(data))
    step = _get(runtime_result, "rollback_hook")
    failed = _get(step, "passed") is not True or _has_upstream_risk(data, "ROLLBACK")
    score = data.rollback_hook_score if data.rollback_hook_score is not None else int(_get(step, "score", 0) or 0)
    return _check("rollback_hook", score, PaperRuntimeTestRunRisk.ROLLBACK_HOOK_FAILURE, failed, _as_tuple(_get(step, "events", ())))


def verify_runtime_kill_switch_hook(data: PaperRuntimeTestRunInput | Mapping[str, Any], runtime_result: Any | None = None) -> PaperRuntimeTestCheck:
    data = _coerce_input(data)
    runtime_result = runtime_result or run_paper_trading_runtime(_runtime_input(data))
    step = _get(runtime_result, "kill_switch_hook")
    failed = _get(step, "passed") is not True or _has_upstream_risk(data, "KILL_SWITCH")
    score = data.kill_switch_hook_score if data.kill_switch_hook_score is not None else int(_get(step, "score", 0) or 0)
    return _check("kill_switch_hook", score, PaperRuntimeTestRunRisk.KILL_SWITCH_HOOK_FAILURE, failed, _as_tuple(_get(step, "events", ())))


def verify_runtime_human_supervision_hook(data: PaperRuntimeTestRunInput | Mapping[str, Any], runtime_result: Any | None = None) -> PaperRuntimeTestCheck:
    data = _coerce_input(data)
    runtime_result = runtime_result or run_paper_trading_runtime(_runtime_input(data))
    step = _get(runtime_result, "human_supervision_hook")
    failed = _get(step, "passed") is not True or _has_upstream_risk(data, "HUMAN", "SUPERVISION")
    score = data.human_supervision_hook_score if data.human_supervision_hook_score is not None else int(_get(step, "score", 0) or 0)
    return _check("human_supervision_hook", score, PaperRuntimeTestRunRisk.HUMAN_SUPERVISION_HOOK_FAILURE, failed, _as_tuple(_get(step, "events", ())))


def verify_runtime_stop(data: PaperRuntimeTestRunInput | Mapping[str, Any], runtime_result: Any | None = None) -> PaperRuntimeTestCheck:
    data = _coerce_input(data)
    runtime_result = runtime_result or run_paper_trading_runtime(_runtime_input(data))
    step = _get(runtime_result, "stop")
    failed = _get(step, "passed") is not True or not _state_contains(runtime_result, "COMPLETED")
    score = data.runtime_stop_score if data.runtime_stop_score is not None else int(_get(step, "score", 0) or 0)
    return _check("runtime_stop", score, PaperRuntimeTestRunRisk.RUNTIME_STOP_FAILURE, failed, _as_tuple(_get(step, "events", ())))


def _offline_boundary(data: PaperRuntimeTestRunInput, runtime_result: Any | None = None) -> bool:
    runtime_input = _runtime_input(data)
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
        and _get(runtime_input, "offline_mode_enforced", True) is True
        and _get(runtime_input, "sandbox_mode_enforced", True) is True
        and _get(runtime_input, "no_real_broker", True) is True
        and _get(runtime_input, "no_api_key_read", True) is True
        and _get(runtime_input, "no_http_transport", True) is True
        and _get(runtime_input, "no_websocket_transport", True) is True
        and _get(runtime_input, "no_socket_transport", True) is True
        and _get(runtime_input, "no_external_api", True) is True
        and _get(runtime_input, "no_real_order", True) is True
        and _get(runtime_input, "paper_order_not_routed", True) is True
        and _get(runtime_result, "offline_only", True) is True
        and not _has_upstream_risk(data, "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK", "BROKER", "EXTERNAL_DEPENDENCY")
    )


def detect_test_run_risks(data: PaperRuntimeTestRunInput | Mapping[str, Any], *checks: PaperRuntimeTestCheck) -> tuple[PaperRuntimeTestRunRisk, ...]:
    data = _coerce_input(data)
    if not checks:
        scenario = run_runtime_test_scenario(data)
        checks = scenario.checks
        runtime_result = scenario.runtime_result
    else:
        runtime_result = None
    risks: list[PaperRuntimeTestRunRisk] = []
    for check in checks:
        risks.extend(check.risks)
    if not _offline_boundary(data, runtime_result):
        risks.append(PaperRuntimeTestRunRisk.TEST_RUN_STATE_DRIFT)
    if _has_upstream_risk(data, "DRIFT", "STATE_CORRUPTION", "INCONSISTENCY"):
        risks.append(PaperRuntimeTestRunRisk.TEST_RUN_STATE_DRIFT)
    return _dedupe(risks)


def compute_test_run_score(data: PaperRuntimeTestRunInput | Mapping[str, Any], risks: tuple[PaperRuntimeTestRunRisk, ...] = (), *checks: PaperRuntimeTestCheck) -> PaperRuntimeTestRunScore:
    data = _coerce_input(data)
    if not checks:
        checks = run_runtime_test_scenario(data).checks
    scores = tuple(check.score for check in checks)
    overall = _clamp(_average(scores) - min(85, len(set(risks)) * 5))
    for risk, cap in {
        PaperRuntimeTestRunRisk.RUNTIME_START_FAILURE: 35,
        PaperRuntimeTestRunRisk.SESSION_INIT_FAILURE: 35,
        PaperRuntimeTestRunRisk.SAFETY_GATE_FAILURE: 45,
        PaperRuntimeTestRunRisk.PAPER_ORDER_SIMULATION_FAILURE: 45,
        PaperRuntimeTestRunRisk.OBSERVABILITY_OUTPUT_FAILURE: 55,
        PaperRuntimeTestRunRisk.ROLLBACK_HOOK_FAILURE: 55,
        PaperRuntimeTestRunRisk.KILL_SWITCH_HOOK_FAILURE: 50,
        PaperRuntimeTestRunRisk.HUMAN_SUPERVISION_HOOK_FAILURE: 55,
        PaperRuntimeTestRunRisk.RUNTIME_STOP_FAILURE: 50,
        PaperRuntimeTestRunRisk.TEST_RUN_STATE_DRIFT: 40,
    }.items():
        if risk in risks:
            overall = min(overall, cap)
    return PaperRuntimeTestRunScore(overall, *scores)


def _select_decision(score: int, risks: tuple[PaperRuntimeTestRunRisk, ...], ready_for_extended_test: bool | None) -> PaperRuntimeTestRunDecision:
    if PaperRuntimeTestRunRisk.TEST_RUN_STATE_DRIFT in risks or PaperRuntimeTestRunRisk.RUNTIME_START_FAILURE in risks or score < 45:
        return PaperRuntimeTestRunDecision.TEST_RUN_BLOCKED
    hard = {
        PaperRuntimeTestRunRisk.SESSION_INIT_FAILURE,
        PaperRuntimeTestRunRisk.SAFETY_GATE_FAILURE,
        PaperRuntimeTestRunRisk.PAPER_ORDER_SIMULATION_FAILURE,
        PaperRuntimeTestRunRisk.KILL_SWITCH_HOOK_FAILURE,
        PaperRuntimeTestRunRisk.RUNTIME_STOP_FAILURE,
    }
    if hard.intersection(risks) or len(set(risks)) >= 4:
        return PaperRuntimeTestRunDecision.TEST_RUN_REVIEW_REQUIRED
    if risks:
        return PaperRuntimeTestRunDecision.TEST_RUN_PARTIALLY_READY
    if ready_for_extended_test is True and score >= 94:
        return PaperRuntimeTestRunDecision.READY_FOR_EXTENDED_PAPER_RUNTIME_TEST
    if score >= 90:
        return PaperRuntimeTestRunDecision.TEST_RUN_COMPLETED
    if score >= 85:
        return PaperRuntimeTestRunDecision.TEST_RUN_READY
    return PaperRuntimeTestRunDecision.TEST_RUN_PARTIALLY_READY


def _select_state(decision: PaperRuntimeTestRunDecision) -> PaperRuntimeTestRunState:
    mapping = {
        PaperRuntimeTestRunDecision.TEST_RUN_BLOCKED: PaperRuntimeTestRunState.NOT_READY,
        PaperRuntimeTestRunDecision.TEST_RUN_REVIEW_REQUIRED: PaperRuntimeTestRunState.TEST_REVIEW_REQUIRED,
        PaperRuntimeTestRunDecision.TEST_RUN_PARTIALLY_READY: PaperRuntimeTestRunState.TEST_PARTIALLY_READY,
        PaperRuntimeTestRunDecision.TEST_RUN_READY: PaperRuntimeTestRunState.TEST_RUN_READY,
        PaperRuntimeTestRunDecision.TEST_RUN_COMPLETED: PaperRuntimeTestRunState.TEST_RUN_COMPLETED,
        PaperRuntimeTestRunDecision.READY_FOR_EXTENDED_PAPER_RUNTIME_TEST: PaperRuntimeTestRunState.READY_FOR_EXTENDED_PAPER_RUNTIME_TEST,
    }
    return mapping[decision]


def generate_test_run_recommendations(risks: tuple[PaperRuntimeTestRunRisk, ...], decision: PaperRuntimeTestRunDecision | None = None) -> tuple[PaperRuntimeTestRunRecommendation, ...]:
    recommendations: list[PaperRuntimeTestRunRecommendation] = []
    if risks:
        recommendations.append(PaperRuntimeTestRunRecommendation.HOLD_EXTENDED_TEST_APPROVAL)
    mapping = {
        PaperRuntimeTestRunRisk.RUNTIME_START_FAILURE: PaperRuntimeTestRunRecommendation.REPAIR_RUNTIME_START,
        PaperRuntimeTestRunRisk.SESSION_INIT_FAILURE: PaperRuntimeTestRunRecommendation.REPAIR_SESSION_INIT,
        PaperRuntimeTestRunRisk.MARKET_CYCLE_FAILURE: PaperRuntimeTestRunRecommendation.REPAIR_MARKET_CYCLE,
        PaperRuntimeTestRunRisk.SIGNAL_CYCLE_FAILURE: PaperRuntimeTestRunRecommendation.REPAIR_SIGNAL_CYCLE,
        PaperRuntimeTestRunRisk.DECISION_CYCLE_FAILURE: PaperRuntimeTestRunRecommendation.REPAIR_DECISION_CYCLE,
        PaperRuntimeTestRunRisk.SAFETY_GATE_FAILURE: PaperRuntimeTestRunRecommendation.REPAIR_SAFETY_GATE,
        PaperRuntimeTestRunRisk.PAPER_ORDER_SIMULATION_FAILURE: PaperRuntimeTestRunRecommendation.REPAIR_PAPER_ORDER_SIMULATION,
        PaperRuntimeTestRunRisk.POSITION_PNL_UPDATE_FAILURE: PaperRuntimeTestRunRecommendation.REPAIR_POSITION_PNL_UPDATE,
        PaperRuntimeTestRunRisk.JOURNAL_OUTPUT_FAILURE: PaperRuntimeTestRunRecommendation.REPAIR_JOURNAL_OUTPUT,
        PaperRuntimeTestRunRisk.OBSERVABILITY_OUTPUT_FAILURE: PaperRuntimeTestRunRecommendation.REPAIR_OBSERVABILITY_OUTPUT,
        PaperRuntimeTestRunRisk.ROLLBACK_HOOK_FAILURE: PaperRuntimeTestRunRecommendation.REPAIR_ROLLBACK_HOOK,
        PaperRuntimeTestRunRisk.KILL_SWITCH_HOOK_FAILURE: PaperRuntimeTestRunRecommendation.REPAIR_KILL_SWITCH_HOOK,
        PaperRuntimeTestRunRisk.HUMAN_SUPERVISION_HOOK_FAILURE: PaperRuntimeTestRunRecommendation.REPAIR_HUMAN_SUPERVISION_HOOK,
        PaperRuntimeTestRunRisk.RUNTIME_STOP_FAILURE: PaperRuntimeTestRunRecommendation.REPAIR_RUNTIME_STOP,
        PaperRuntimeTestRunRisk.TEST_RUN_STATE_DRIFT: PaperRuntimeTestRunRecommendation.RECONCILE_TEST_RUN_STATE,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(PaperRuntimeTestRunRecommendation.RUN_PAPER_RUNTIME_TEST_RUN_SUITE)
    if decision == PaperRuntimeTestRunDecision.READY_FOR_EXTENDED_PAPER_RUNTIME_TEST:
        recommendations.append(PaperRuntimeTestRunRecommendation.APPROVE_EXTENDED_TEST_AFTER_MANUAL_REVIEW)
    return _dedupe(recommendations)


def evaluate_paper_runtime_test_run(data: PaperRuntimeTestRunInput | Mapping[str, Any]) -> PaperRuntimeTestRunResult:
    data = _coerce_input(data)
    scenario = run_runtime_test_scenario(data)
    checks = scenario.checks
    risks = detect_test_run_risks(data, *checks)
    score = compute_test_run_score(data, risks, *checks)
    decision = _select_decision(score.overall_score, risks, data.ready_for_extended_test)
    state = _select_state(decision)
    recommendations = generate_test_run_recommendations(risks, decision)
    offline_only = _offline_boundary(data, scenario.runtime_result)
    summary = f"{state.value}: decision={decision.value}, score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return PaperRuntimeTestRunResult(state, decision, score.overall_score, score, risks, *checks, scenario.runtime_result, recommendations, offline_only, summary)


def render_paper_runtime_test_run_markdown(result: PaperRuntimeTestRunResult) -> str:
    lines = [
        "# AGIcore Paper Runtime Test Run",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Score: {result.test_run_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Runtime Test Checks",
    ]
    checks = (
        result.runtime_start,
        result.session_init,
        result.market_cycle,
        result.signal_cycle,
        result.decision_cycle,
        result.safety_gate,
        result.paper_order_simulation,
        result.position_pnl_update,
        result.journal_output,
        result.observability_output,
        result.rollback_hook,
        result.kill_switch_hook,
        result.human_supervision_hook,
        result.runtime_stop,
    )
    for check in checks:
        lines.append(f"- {check.name}: passed={check.passed}, score={check.score}/100, risks={', '.join(risk.value for risk in check.risks) or 'none'}")
        lines.extend(f"  - {detail}" for detail in check.details)
    lines.append("")
    lines.append("# Test Run Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Test Run Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_test_run_score",
    "detect_test_run_risks",
    "evaluate_paper_runtime_test_run",
    "generate_test_run_recommendations",
    "render_paper_runtime_test_run_markdown",
    "run_runtime_test_scenario",
    "verify_runtime_decision_cycle",
    "verify_runtime_human_supervision_hook",
    "verify_runtime_journal_output",
    "verify_runtime_kill_switch_hook",
    "verify_runtime_market_cycle",
    "verify_runtime_observability_output",
    "verify_runtime_paper_order_simulation",
    "verify_runtime_position_pnl_update",
    "verify_runtime_rollback_hook",
    "verify_runtime_safety_gate",
    "verify_runtime_session_init",
    "verify_runtime_signal_cycle",
    "verify_runtime_start",
    "verify_runtime_stop",
]
