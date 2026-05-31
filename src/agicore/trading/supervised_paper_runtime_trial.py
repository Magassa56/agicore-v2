"""Offline supervised trial for the AGIcore Paper Trading Runtime."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.supervised_paper_runtime_trial_models import (
    SupervisedPaperRuntimeTrialCheck,
    SupervisedPaperRuntimeTrialDecision,
    SupervisedPaperRuntimeTrialInput,
    SupervisedPaperRuntimeTrialRecommendation,
    SupervisedPaperRuntimeTrialResult,
    SupervisedPaperRuntimeTrialRisk,
    SupervisedPaperRuntimeTrialScore,
    SupervisedPaperRuntimeTrialState,
)


def _coerce_input(data: SupervisedPaperRuntimeTrialInput | Mapping[str, Any]) -> SupervisedPaperRuntimeTrialInput:
    if isinstance(data, SupervisedPaperRuntimeTrialInput):
        return data
    return SupervisedPaperRuntimeTrialInput(**dict(data))


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


def _upstream_items(data: SupervisedPaperRuntimeTrialInput) -> tuple[Any, ...]:
    return (
        data.official_paper_validation_report,
        data.paper_runtime_validation,
        data.paper_runtime_release_candidate,
        data.paper_runtime_stabilization_review,
        data.extended_paper_runtime_test,
        data.paper_runtime_test_run,
        data.paper_trading_runtime,
        data.paper_runtime_integration_review,
        data.paper_trading_runtime_design,
        data.paper_runtime_decision_review,
        data.full_paper_session,
        data.observability_verification,
        data.rollback_verification,
        data.kill_switch_verification,
        data.human_validated_paper_session,
        data.supervised_paper_session,
    )


def _upstream_risks(data: SupervisedPaperRuntimeTrialInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: SupervisedPaperRuntimeTrialInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _check(name: str, score: int, risk: SupervisedPaperRuntimeTrialRisk, failed: bool, details: tuple[str, ...] = ()) -> SupervisedPaperRuntimeTrialCheck:
    risks = (risk,) if failed or score < 85 else ()
    return SupervisedPaperRuntimeTrialCheck(name, _clamp(score), not risks and score >= 85, risks, details)


def verify_trial_authorization(data: SupervisedPaperRuntimeTrialInput | Mapping[str, Any]) -> SupervisedPaperRuntimeTrialCheck:
    data = _coerce_input(data)
    report = data.official_paper_validation_report
    failed = data.trial_authorized is not True or not _state_contains(report, "READY_FOR_SUPERVISED_PAPER_RUNTIME_TRIAL", "APPROVE_SUPERVISED_PAPER_RUNTIME_TRIAL")
    score = data.trial_authorization_score if data.trial_authorization_score is not None else _bool_score(data.trial_authorized)
    return _check("trial_authorization", score, SupervisedPaperRuntimeTrialRisk.TRIAL_AUTHORIZATION_MISSING, failed, (_value(_get(report, "state")),))


def verify_human_supervision_active(data: SupervisedPaperRuntimeTrialInput | Mapping[str, Any]) -> SupervisedPaperRuntimeTrialCheck:
    data = _coerce_input(data)
    failed = data.human_supervision_active is not True or _has_upstream_risk(data, "HUMAN", "SUPERVISION")
    score = data.human_supervision_score if data.human_supervision_score is not None else _bool_score(data.human_supervision_active)
    return _check("human_supervision_active", score, SupervisedPaperRuntimeTrialRisk.HUMAN_SUPERVISION_INACTIVE, failed)


def verify_runtime_trial_start(data: SupervisedPaperRuntimeTrialInput | Mapping[str, Any]) -> SupervisedPaperRuntimeTrialCheck:
    data = _coerce_input(data)
    failed = data.runtime_trial_started is not True or _has_upstream_risk(data, "RUNTIME_START", "START_FAILURE")
    score = data.runtime_trial_start_score if data.runtime_trial_start_score is not None else _bool_score(data.runtime_trial_started)
    return _check("runtime_trial_start", score, SupervisedPaperRuntimeTrialRisk.RUNTIME_TRIAL_START_FAILURE, failed)


def verify_runtime_trial_session_init(data: SupervisedPaperRuntimeTrialInput | Mapping[str, Any]) -> SupervisedPaperRuntimeTrialCheck:
    data = _coerce_input(data)
    failed = data.session_initialized is not True or _has_upstream_risk(data, "SESSION_INIT")
    score = data.session_init_score if data.session_init_score is not None else _bool_score(data.session_initialized)
    return _check("runtime_trial_session_init", score, SupervisedPaperRuntimeTrialRisk.SESSION_INIT_FAILURE, failed)


def verify_runtime_trial_cycles(data: SupervisedPaperRuntimeTrialInput | Mapping[str, Any]) -> SupervisedPaperRuntimeTrialCheck:
    data = _coerce_input(data)
    failed = data.runtime_cycles_completed is not True or _has_upstream_risk(data, "RUNTIME_CYCLE", "MARKET_CYCLE", "SIGNAL_CYCLE", "DECISION_CYCLE")
    score = data.runtime_cycles_score if data.runtime_cycles_score is not None else _bool_score(data.runtime_cycles_completed)
    return _check("runtime_trial_cycles", score, SupervisedPaperRuntimeTrialRisk.RUNTIME_CYCLE_FAILURE, failed)


def verify_runtime_trial_safety_gate(data: SupervisedPaperRuntimeTrialInput | Mapping[str, Any]) -> SupervisedPaperRuntimeTrialCheck:
    data = _coerce_input(data)
    failed = data.safety_gate_passed is not True or _has_upstream_risk(data, "SAFETY_GATE", "SAFETY")
    score = data.safety_gate_score if data.safety_gate_score is not None else _bool_score(data.safety_gate_passed)
    return _check("runtime_trial_safety_gate", score, SupervisedPaperRuntimeTrialRisk.SAFETY_GATE_FAILURE, failed)


def verify_runtime_trial_paper_order_simulation(data: SupervisedPaperRuntimeTrialInput | Mapping[str, Any]) -> SupervisedPaperRuntimeTrialCheck:
    data = _coerce_input(data)
    failed = data.paper_order_simulated is not True or _has_upstream_risk(data, "PAPER_ORDER", "ORDER_SIMULATION")
    score = data.paper_order_simulation_score if data.paper_order_simulation_score is not None else _bool_score(data.paper_order_simulated)
    return _check("runtime_trial_paper_order_simulation", score, SupervisedPaperRuntimeTrialRisk.PAPER_ORDER_SIMULATION_FAILURE, failed)


def verify_runtime_trial_position_pnl(data: SupervisedPaperRuntimeTrialInput | Mapping[str, Any]) -> SupervisedPaperRuntimeTrialCheck:
    data = _coerce_input(data)
    failed = data.position_pnl_updated is not True or _has_upstream_risk(data, "POSITION", "PNL")
    score = data.position_pnl_score if data.position_pnl_score is not None else _bool_score(data.position_pnl_updated)
    return _check("runtime_trial_position_pnl", score, SupervisedPaperRuntimeTrialRisk.POSITION_PNL_FAILURE, failed)


def verify_runtime_trial_journal(data: SupervisedPaperRuntimeTrialInput | Mapping[str, Any]) -> SupervisedPaperRuntimeTrialCheck:
    data = _coerce_input(data)
    failed = data.journal_written is not True or _has_upstream_risk(data, "JOURNAL")
    score = data.journal_score if data.journal_score is not None else _bool_score(data.journal_written)
    return _check("runtime_trial_journal", score, SupervisedPaperRuntimeTrialRisk.JOURNAL_FAILURE, failed)


def verify_runtime_trial_observability(data: SupervisedPaperRuntimeTrialInput | Mapping[str, Any]) -> SupervisedPaperRuntimeTrialCheck:
    data = _coerce_input(data)
    failed = data.observability_emitted is not True or _has_upstream_risk(data, "OBSERVABILITY")
    score = data.observability_score if data.observability_score is not None else _bool_score(data.observability_emitted)
    return _check("runtime_trial_observability", score, SupervisedPaperRuntimeTrialRisk.OBSERVABILITY_FAILURE, failed)


def verify_runtime_trial_rollback(data: SupervisedPaperRuntimeTrialInput | Mapping[str, Any]) -> SupervisedPaperRuntimeTrialCheck:
    data = _coerce_input(data)
    failed = data.rollback_verified is not True or _has_upstream_risk(data, "ROLLBACK")
    score = data.rollback_score if data.rollback_score is not None else _bool_score(data.rollback_verified)
    return _check("runtime_trial_rollback", score, SupervisedPaperRuntimeTrialRisk.ROLLBACK_FAILURE, failed)


def verify_runtime_trial_kill_switch(data: SupervisedPaperRuntimeTrialInput | Mapping[str, Any]) -> SupervisedPaperRuntimeTrialCheck:
    data = _coerce_input(data)
    failed = data.kill_switch_verified is not True or _has_upstream_risk(data, "KILL_SWITCH")
    score = data.kill_switch_score if data.kill_switch_score is not None else _bool_score(data.kill_switch_verified)
    return _check("runtime_trial_kill_switch", score, SupervisedPaperRuntimeTrialRisk.KILL_SWITCH_FAILURE, failed)


def verify_runtime_trial_human_intervention(data: SupervisedPaperRuntimeTrialInput | Mapping[str, Any]) -> SupervisedPaperRuntimeTrialCheck:
    data = _coerce_input(data)
    failed = data.human_intervention_verified is not True or _has_upstream_risk(data, "HUMAN_INTERVENTION", "HUMAN_OVERRIDE")
    score = data.human_intervention_score if data.human_intervention_score is not None else _bool_score(data.human_intervention_verified)
    return _check("runtime_trial_human_intervention", score, SupervisedPaperRuntimeTrialRisk.HUMAN_INTERVENTION_FAILURE, failed)


def verify_runtime_trial_stop(data: SupervisedPaperRuntimeTrialInput | Mapping[str, Any]) -> SupervisedPaperRuntimeTrialCheck:
    data = _coerce_input(data)
    failed = data.runtime_trial_stopped is not True or _has_upstream_risk(data, "TRIAL_STOP", "RUNTIME_STOP")
    score = data.trial_stop_score if data.trial_stop_score is not None else _bool_score(data.runtime_trial_stopped)
    return _check("runtime_trial_stop", score, SupervisedPaperRuntimeTrialRisk.TRIAL_STOP_FAILURE, failed)


def _offline_boundary(data: SupervisedPaperRuntimeTrialInput) -> bool:
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
        and _get(data.official_paper_validation_report, "offline_only", True) is True
        and not _has_upstream_risk(data, "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK", "BROKER", "EXTERNAL_DEPENDENCY")
    )


def _all_checks(data: SupervisedPaperRuntimeTrialInput) -> tuple[SupervisedPaperRuntimeTrialCheck, ...]:
    return (
        verify_trial_authorization(data),
        verify_human_supervision_active(data),
        verify_runtime_trial_start(data),
        verify_runtime_trial_session_init(data),
        verify_runtime_trial_cycles(data),
        verify_runtime_trial_safety_gate(data),
        verify_runtime_trial_paper_order_simulation(data),
        verify_runtime_trial_position_pnl(data),
        verify_runtime_trial_journal(data),
        verify_runtime_trial_observability(data),
        verify_runtime_trial_rollback(data),
        verify_runtime_trial_kill_switch(data),
        verify_runtime_trial_human_intervention(data),
        verify_runtime_trial_stop(data),
    )


def detect_supervised_trial_risks(data: SupervisedPaperRuntimeTrialInput | Mapping[str, Any], *checks: SupervisedPaperRuntimeTrialCheck) -> tuple[SupervisedPaperRuntimeTrialRisk, ...]:
    data = _coerce_input(data)
    if not checks:
        checks = _all_checks(data)
    risks: list[SupervisedPaperRuntimeTrialRisk] = []
    for check in checks:
        risks.extend(check.risks)
    if data.forward_test_plan_requested is not True or not _offline_boundary(data):
        risks.append(SupervisedPaperRuntimeTrialRisk.PREMATURE_FORWARD_TEST_PLAN)
    return _dedupe(risks)


def compute_supervised_trial_score(data: SupervisedPaperRuntimeTrialInput | Mapping[str, Any], risks: tuple[SupervisedPaperRuntimeTrialRisk, ...] = (), *checks: SupervisedPaperRuntimeTrialCheck) -> SupervisedPaperRuntimeTrialScore:
    data = _coerce_input(data)
    if not checks:
        checks = _all_checks(data)
    scores = tuple(check.score for check in checks)
    overall = _clamp(_average(scores) - min(80, len(set(risks)) * 5))
    for risk, cap in {
        SupervisedPaperRuntimeTrialRisk.TRIAL_AUTHORIZATION_MISSING: 45,
        SupervisedPaperRuntimeTrialRisk.HUMAN_SUPERVISION_INACTIVE: 45,
        SupervisedPaperRuntimeTrialRisk.RUNTIME_TRIAL_START_FAILURE: 55,
        SupervisedPaperRuntimeTrialRisk.SAFETY_GATE_FAILURE: 50,
        SupervisedPaperRuntimeTrialRisk.OBSERVABILITY_FAILURE: 60,
        SupervisedPaperRuntimeTrialRisk.ROLLBACK_FAILURE: 55,
        SupervisedPaperRuntimeTrialRisk.KILL_SWITCH_FAILURE: 50,
        SupervisedPaperRuntimeTrialRisk.PREMATURE_FORWARD_TEST_PLAN: 40,
    }.items():
        if risk in risks:
            overall = min(overall, cap)
    return SupervisedPaperRuntimeTrialScore(overall, *scores)


def _select_decision(risks: tuple[SupervisedPaperRuntimeTrialRisk, ...], score: int) -> SupervisedPaperRuntimeTrialDecision:
    if SupervisedPaperRuntimeTrialRisk.PREMATURE_FORWARD_TEST_PLAN in risks or score < 45:
        return SupervisedPaperRuntimeTrialDecision.BLOCK_SUPERVISED_TRIAL
    if SupervisedPaperRuntimeTrialRisk.TRIAL_AUTHORIZATION_MISSING in risks:
        return SupervisedPaperRuntimeTrialDecision.REQUIRE_AUTHORIZATION_FIXES
    if SupervisedPaperRuntimeTrialRisk.HUMAN_SUPERVISION_INACTIVE in risks or SupervisedPaperRuntimeTrialRisk.HUMAN_INTERVENTION_FAILURE in risks:
        return SupervisedPaperRuntimeTrialDecision.REQUIRE_SUPERVISION_FIXES
    if SupervisedPaperRuntimeTrialRisk.SAFETY_GATE_FAILURE in risks:
        return SupervisedPaperRuntimeTrialDecision.REQUIRE_SAFETY_FIXES
    if SupervisedPaperRuntimeTrialRisk.OBSERVABILITY_FAILURE in risks or SupervisedPaperRuntimeTrialRisk.JOURNAL_FAILURE in risks:
        return SupervisedPaperRuntimeTrialDecision.REQUIRE_OBSERVABILITY_FIXES
    if SupervisedPaperRuntimeTrialRisk.ROLLBACK_FAILURE in risks:
        return SupervisedPaperRuntimeTrialDecision.REQUIRE_ROLLBACK_FIXES
    if SupervisedPaperRuntimeTrialRisk.KILL_SWITCH_FAILURE in risks:
        return SupervisedPaperRuntimeTrialDecision.REQUIRE_KILL_SWITCH_FIXES
    if risks:
        return SupervisedPaperRuntimeTrialDecision.REQUIRE_RUNTIME_TRIAL_FIXES
    return SupervisedPaperRuntimeTrialDecision.APPROVE_SUPERVISED_PAPER_RUNTIME_TRIAL


def _select_state(decision: SupervisedPaperRuntimeTrialDecision, score: int) -> SupervisedPaperRuntimeTrialState:
    if decision == SupervisedPaperRuntimeTrialDecision.BLOCK_SUPERVISED_TRIAL:
        return SupervisedPaperRuntimeTrialState.NOT_READY
    if decision != SupervisedPaperRuntimeTrialDecision.APPROVE_SUPERVISED_PAPER_RUNTIME_TRIAL:
        return SupervisedPaperRuntimeTrialState.TRIAL_REVIEW_REQUIRED if score < 82 else SupervisedPaperRuntimeTrialState.TRIAL_PARTIALLY_READY
    if score >= 95:
        return SupervisedPaperRuntimeTrialState.READY_FOR_PAPER_RUNTIME_FORWARD_TEST_PLAN
    return SupervisedPaperRuntimeTrialState.SUPERVISED_TRIAL_COMPLETED


def generate_supervised_trial_recommendations(risks: tuple[SupervisedPaperRuntimeTrialRisk, ...], decision: SupervisedPaperRuntimeTrialDecision | None = None) -> tuple[SupervisedPaperRuntimeTrialRecommendation, ...]:
    recommendations: list[SupervisedPaperRuntimeTrialRecommendation] = []
    if risks:
        recommendations.append(SupervisedPaperRuntimeTrialRecommendation.HOLD_FORWARD_TEST_PLAN)
    mapping = {
        SupervisedPaperRuntimeTrialRisk.TRIAL_AUTHORIZATION_MISSING: SupervisedPaperRuntimeTrialRecommendation.COMPLETE_TRIAL_AUTHORIZATION,
        SupervisedPaperRuntimeTrialRisk.HUMAN_SUPERVISION_INACTIVE: SupervisedPaperRuntimeTrialRecommendation.ACTIVATE_HUMAN_SUPERVISION,
        SupervisedPaperRuntimeTrialRisk.RUNTIME_TRIAL_START_FAILURE: SupervisedPaperRuntimeTrialRecommendation.REPAIR_RUNTIME_TRIAL_START,
        SupervisedPaperRuntimeTrialRisk.SESSION_INIT_FAILURE: SupervisedPaperRuntimeTrialRecommendation.REPAIR_SESSION_INIT,
        SupervisedPaperRuntimeTrialRisk.RUNTIME_CYCLE_FAILURE: SupervisedPaperRuntimeTrialRecommendation.REPAIR_RUNTIME_CYCLES,
        SupervisedPaperRuntimeTrialRisk.SAFETY_GATE_FAILURE: SupervisedPaperRuntimeTrialRecommendation.REPAIR_SAFETY_GATE,
        SupervisedPaperRuntimeTrialRisk.PAPER_ORDER_SIMULATION_FAILURE: SupervisedPaperRuntimeTrialRecommendation.REPAIR_PAPER_ORDER_SIMULATION,
        SupervisedPaperRuntimeTrialRisk.POSITION_PNL_FAILURE: SupervisedPaperRuntimeTrialRecommendation.REPAIR_POSITION_PNL,
        SupervisedPaperRuntimeTrialRisk.JOURNAL_FAILURE: SupervisedPaperRuntimeTrialRecommendation.REPAIR_JOURNAL,
        SupervisedPaperRuntimeTrialRisk.OBSERVABILITY_FAILURE: SupervisedPaperRuntimeTrialRecommendation.REPAIR_OBSERVABILITY,
        SupervisedPaperRuntimeTrialRisk.ROLLBACK_FAILURE: SupervisedPaperRuntimeTrialRecommendation.REPAIR_ROLLBACK,
        SupervisedPaperRuntimeTrialRisk.KILL_SWITCH_FAILURE: SupervisedPaperRuntimeTrialRecommendation.REPAIR_KILL_SWITCH,
        SupervisedPaperRuntimeTrialRisk.HUMAN_INTERVENTION_FAILURE: SupervisedPaperRuntimeTrialRecommendation.REPAIR_HUMAN_INTERVENTION,
        SupervisedPaperRuntimeTrialRisk.TRIAL_STOP_FAILURE: SupervisedPaperRuntimeTrialRecommendation.REPAIR_TRIAL_STOP,
        SupervisedPaperRuntimeTrialRisk.PREMATURE_FORWARD_TEST_PLAN: SupervisedPaperRuntimeTrialRecommendation.DELAY_FORWARD_TEST_PLAN,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(SupervisedPaperRuntimeTrialRecommendation.RUN_SUPERVISED_RUNTIME_TRIAL_SUITE)
    if decision == SupervisedPaperRuntimeTrialDecision.APPROVE_SUPERVISED_PAPER_RUNTIME_TRIAL:
        recommendations.append(SupervisedPaperRuntimeTrialRecommendation.APPROVE_FORWARD_TEST_PLAN_PREPARATION)
    return _dedupe(recommendations)


def run_supervised_runtime_trial(data: SupervisedPaperRuntimeTrialInput | Mapping[str, Any]) -> SupervisedPaperRuntimeTrialResult:
    return evaluate_supervised_paper_runtime_trial(data)


def evaluate_supervised_paper_runtime_trial(data: SupervisedPaperRuntimeTrialInput | Mapping[str, Any]) -> SupervisedPaperRuntimeTrialResult:
    data = _coerce_input(data)
    checks = _all_checks(data)
    risks = detect_supervised_trial_risks(data, *checks)
    score = compute_supervised_trial_score(data, risks, *checks)
    decision = _select_decision(risks, score.overall_score)
    state = _select_state(decision, score.overall_score)
    recommendations = generate_supervised_trial_recommendations(risks, decision)
    offline_only = _offline_boundary(data)
    summary = f"{state.value}: decision={decision.value}, score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return SupervisedPaperRuntimeTrialResult(state, decision, score.overall_score, score, risks, *checks, recommendations, offline_only, summary)


def render_supervised_paper_runtime_trial_markdown(result: SupervisedPaperRuntimeTrialResult) -> str:
    lines = [
        "# AGIcore Supervised Paper Runtime Trial",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Score: {result.supervised_trial_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Trial Checks",
    ]
    checks = (
        result.trial_authorization,
        result.human_supervision_active,
        result.runtime_trial_start,
        result.runtime_trial_session_init,
        result.runtime_trial_cycles,
        result.runtime_trial_safety_gate,
        result.runtime_trial_paper_order_simulation,
        result.runtime_trial_position_pnl,
        result.runtime_trial_journal,
        result.runtime_trial_observability,
        result.runtime_trial_rollback,
        result.runtime_trial_kill_switch,
        result.runtime_trial_human_intervention,
        result.runtime_trial_stop,
    )
    for check in checks:
        lines.append(f"- {check.name}: passed={check.passed}, score={check.score}/100, risks={', '.join(risk.value for risk in check.risks) or 'none'}")
    lines.append("")
    lines.append("# Trial Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Trial Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_supervised_trial_score",
    "detect_supervised_trial_risks",
    "evaluate_supervised_paper_runtime_trial",
    "generate_supervised_trial_recommendations",
    "render_supervised_paper_runtime_trial_markdown",
    "run_supervised_runtime_trial",
    "verify_human_supervision_active",
    "verify_runtime_trial_cycles",
    "verify_runtime_trial_human_intervention",
    "verify_runtime_trial_journal",
    "verify_runtime_trial_kill_switch",
    "verify_runtime_trial_observability",
    "verify_runtime_trial_paper_order_simulation",
    "verify_runtime_trial_position_pnl",
    "verify_runtime_trial_rollback",
    "verify_runtime_trial_safety_gate",
    "verify_runtime_trial_session_init",
    "verify_runtime_trial_start",
    "verify_runtime_trial_stop",
    "verify_trial_authorization",
]
