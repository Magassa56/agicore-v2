"""Offline forward test plan for the AGIcore Paper Trading Runtime."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_runtime_forward_test_plan_models import (
    PaperRuntimeForwardTestPlanDecision,
    PaperRuntimeForwardTestPlanInput,
    PaperRuntimeForwardTestPlanRecommendation,
    PaperRuntimeForwardTestPlanResult,
    PaperRuntimeForwardTestPlanRisk,
    PaperRuntimeForwardTestPlanScore,
    PaperRuntimeForwardTestPlanSection,
    PaperRuntimeForwardTestPlanState,
)


def _coerce_input(data: PaperRuntimeForwardTestPlanInput | Mapping[str, Any]) -> PaperRuntimeForwardTestPlanInput:
    if isinstance(data, PaperRuntimeForwardTestPlanInput):
        return data
    return PaperRuntimeForwardTestPlanInput(**dict(data))


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


def _upstream_items(data: PaperRuntimeForwardTestPlanInput) -> tuple[Any, ...]:
    return (
        data.supervised_paper_runtime_trial,
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
        data.observability_verification,
        data.rollback_verification,
        data.kill_switch_verification,
        data.human_validated_paper_session,
        data.supervised_paper_session,
    )


def _upstream_risks(data: PaperRuntimeForwardTestPlanInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperRuntimeForwardTestPlanInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _section(name: str, score: int, risk: PaperRuntimeForwardTestPlanRisk, failed: bool, details: tuple[str, ...] = ()) -> PaperRuntimeForwardTestPlanSection:
    risks = (risk,) if failed or score < 85 else ()
    return PaperRuntimeForwardTestPlanSection(name, _clamp(score), not risks and score >= 85, risks, details)


def define_forward_test_scope(data: PaperRuntimeForwardTestPlanInput | Mapping[str, Any]) -> PaperRuntimeForwardTestPlanSection:
    data = _coerce_input(data)
    trial = data.supervised_paper_runtime_trial
    failed = data.forward_test_scope_defined is not True or not _state_contains(trial, "READY_FOR_PAPER_RUNTIME_FORWARD_TEST_PLAN", "APPROVE_SUPERVISED_PAPER_RUNTIME_TRIAL") or _has_upstream_risk(data, "SCOPE")
    score = data.forward_test_scope_score if data.forward_test_scope_score is not None else _bool_score(data.forward_test_scope_defined)
    return _section("forward_test_scope", score, PaperRuntimeForwardTestPlanRisk.FORWARD_TEST_SCOPE_UNCLEAR, failed, (_value(_get(trial, "state")),))


def define_forward_test_duration(data: PaperRuntimeForwardTestPlanInput | Mapping[str, Any]) -> PaperRuntimeForwardTestPlanSection:
    data = _coerce_input(data)
    failed = data.duration_defined is not True or data.duration_days is None or data.duration_days <= 0
    score = data.forward_test_duration_score if data.forward_test_duration_score is not None else _bool_score(data.duration_defined and data.duration_days is not None and data.duration_days > 0)
    return _section("forward_test_duration", score, PaperRuntimeForwardTestPlanRisk.DURATION_UNDEFINED, failed, (f"duration_days={data.duration_days}",))


def define_allowed_session_limits(data: PaperRuntimeForwardTestPlanInput | Mapping[str, Any]) -> PaperRuntimeForwardTestPlanSection:
    data = _coerce_input(data)
    failed = data.session_limits_defined is not True or data.max_sessions is None or data.max_sessions <= 0
    score = data.allowed_session_limits_score if data.allowed_session_limits_score is not None else _bool_score(data.session_limits_defined and data.max_sessions is not None and data.max_sessions > 0)
    return _section("allowed_session_limits", score, PaperRuntimeForwardTestPlanRisk.SESSION_LIMITS_MISSING, failed, (f"max_sessions={data.max_sessions}",))


def define_simulated_loss_limits(data: PaperRuntimeForwardTestPlanInput | Mapping[str, Any]) -> PaperRuntimeForwardTestPlanSection:
    data = _coerce_input(data)
    failed = data.simulated_loss_limits_defined is not True or data.max_simulated_loss_pct is None or data.max_simulated_loss_pct <= 0
    score = data.simulated_loss_limits_score if data.simulated_loss_limits_score is not None else _bool_score(data.simulated_loss_limits_defined and data.max_simulated_loss_pct is not None and data.max_simulated_loss_pct > 0)
    return _section("simulated_loss_limits", score, PaperRuntimeForwardTestPlanRisk.SIMULATED_LOSS_LIMITS_MISSING, failed, (f"max_simulated_loss_pct={data.max_simulated_loss_pct}",))


def define_human_supervision_rules(data: PaperRuntimeForwardTestPlanInput | Mapping[str, Any]) -> PaperRuntimeForwardTestPlanSection:
    data = _coerce_input(data)
    failed = data.human_supervision_rules_defined is not True or _has_upstream_risk(data, "HUMAN", "SUPERVISION")
    score = data.human_supervision_rules_score if data.human_supervision_rules_score is not None else _bool_score(data.human_supervision_rules_defined)
    return _section("human_supervision_rules", score, PaperRuntimeForwardTestPlanRisk.HUMAN_SUPERVISION_RULES_MISSING, failed)


def define_journal_requirements(data: PaperRuntimeForwardTestPlanInput | Mapping[str, Any]) -> PaperRuntimeForwardTestPlanSection:
    data = _coerce_input(data)
    failed = data.journal_requirements_defined is not True or _has_upstream_risk(data, "JOURNAL")
    score = data.journal_requirements_score if data.journal_requirements_score is not None else _bool_score(data.journal_requirements_defined)
    return _section("journal_requirements", score, PaperRuntimeForwardTestPlanRisk.JOURNAL_REQUIREMENTS_MISSING, failed)


def define_observability_requirements(data: PaperRuntimeForwardTestPlanInput | Mapping[str, Any]) -> PaperRuntimeForwardTestPlanSection:
    data = _coerce_input(data)
    failed = data.observability_requirements_defined is not True or _has_upstream_risk(data, "OBSERVABILITY")
    score = data.observability_requirements_score if data.observability_requirements_score is not None else _bool_score(data.observability_requirements_defined)
    return _section("observability_requirements", score, PaperRuntimeForwardTestPlanRisk.OBSERVABILITY_REQUIREMENTS_MISSING, failed)


def define_rollback_rules(data: PaperRuntimeForwardTestPlanInput | Mapping[str, Any]) -> PaperRuntimeForwardTestPlanSection:
    data = _coerce_input(data)
    failed = data.rollback_rules_defined is not True or _has_upstream_risk(data, "ROLLBACK")
    score = data.rollback_rules_score if data.rollback_rules_score is not None else _bool_score(data.rollback_rules_defined)
    return _section("rollback_rules", score, PaperRuntimeForwardTestPlanRisk.ROLLBACK_RULES_MISSING, failed)


def define_kill_switch_rules(data: PaperRuntimeForwardTestPlanInput | Mapping[str, Any]) -> PaperRuntimeForwardTestPlanSection:
    data = _coerce_input(data)
    failed = data.kill_switch_rules_defined is not True or _has_upstream_risk(data, "KILL_SWITCH")
    score = data.kill_switch_rules_score if data.kill_switch_rules_score is not None else _bool_score(data.kill_switch_rules_defined)
    return _section("kill_switch_rules", score, PaperRuntimeForwardTestPlanRisk.KILL_SWITCH_RULES_MISSING, failed)


def define_success_criteria(data: PaperRuntimeForwardTestPlanInput | Mapping[str, Any]) -> PaperRuntimeForwardTestPlanSection:
    data = _coerce_input(data)
    failed = data.success_criteria_defined is not True
    score = data.success_criteria_score if data.success_criteria_score is not None else _bool_score(data.success_criteria_defined)
    return _section("success_criteria", score, PaperRuntimeForwardTestPlanRisk.SUCCESS_CRITERIA_UNCLEAR, failed)


def define_failure_criteria(data: PaperRuntimeForwardTestPlanInput | Mapping[str, Any]) -> PaperRuntimeForwardTestPlanSection:
    data = _coerce_input(data)
    failed = data.failure_criteria_defined is not True
    score = data.failure_criteria_score if data.failure_criteria_score is not None else _bool_score(data.failure_criteria_defined)
    return _section("failure_criteria", score, PaperRuntimeForwardTestPlanRisk.FAILURE_CRITERIA_UNCLEAR, failed)


def define_stop_conditions(data: PaperRuntimeForwardTestPlanInput | Mapping[str, Any]) -> PaperRuntimeForwardTestPlanSection:
    data = _coerce_input(data)
    failed = data.stop_conditions_defined is not True
    score = data.stop_conditions_score if data.stop_conditions_score is not None else _bool_score(data.stop_conditions_defined)
    return _section("stop_conditions", score, PaperRuntimeForwardTestPlanRisk.STOP_CONDITIONS_MISSING, failed)


def _offline_boundary(data: PaperRuntimeForwardTestPlanInput) -> bool:
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
        and _get(data.supervised_paper_runtime_trial, "offline_only", True) is True
        and not _has_upstream_risk(data, "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK", "BROKER", "EXTERNAL_DEPENDENCY")
    )


def _all_sections(data: PaperRuntimeForwardTestPlanInput) -> tuple[PaperRuntimeForwardTestPlanSection, ...]:
    return (
        define_forward_test_scope(data),
        define_forward_test_duration(data),
        define_allowed_session_limits(data),
        define_simulated_loss_limits(data),
        define_human_supervision_rules(data),
        define_journal_requirements(data),
        define_observability_requirements(data),
        define_rollback_rules(data),
        define_kill_switch_rules(data),
        define_success_criteria(data),
        define_failure_criteria(data),
        define_stop_conditions(data),
    )


def detect_forward_test_plan_risks(data: PaperRuntimeForwardTestPlanInput | Mapping[str, Any], *sections: PaperRuntimeForwardTestPlanSection) -> tuple[PaperRuntimeForwardTestPlanRisk, ...]:
    data = _coerce_input(data)
    if not sections:
        sections = _all_sections(data)
    risks: list[PaperRuntimeForwardTestPlanRisk] = []
    for section in sections:
        risks.extend(section.risks)
    if data.broker_sandbox_session_requested is not True or not _offline_boundary(data):
        risks.append(PaperRuntimeForwardTestPlanRisk.PREMATURE_BROKER_SANDBOX_SESSION)
    return _dedupe(risks)


def compute_forward_test_plan_score(data: PaperRuntimeForwardTestPlanInput | Mapping[str, Any], risks: tuple[PaperRuntimeForwardTestPlanRisk, ...] = (), *sections: PaperRuntimeForwardTestPlanSection) -> PaperRuntimeForwardTestPlanScore:
    data = _coerce_input(data)
    if not sections:
        sections = _all_sections(data)
    scores = tuple(section.score for section in sections)
    overall = _clamp(_average(scores) - min(80, len(set(risks)) * 5))
    for risk, cap in {
        PaperRuntimeForwardTestPlanRisk.FORWARD_TEST_SCOPE_UNCLEAR: 45,
        PaperRuntimeForwardTestPlanRisk.DURATION_UNDEFINED: 60,
        PaperRuntimeForwardTestPlanRisk.SESSION_LIMITS_MISSING: 55,
        PaperRuntimeForwardTestPlanRisk.SIMULATED_LOSS_LIMITS_MISSING: 50,
        PaperRuntimeForwardTestPlanRisk.HUMAN_SUPERVISION_RULES_MISSING: 45,
        PaperRuntimeForwardTestPlanRisk.OBSERVABILITY_REQUIREMENTS_MISSING: 60,
        PaperRuntimeForwardTestPlanRisk.ROLLBACK_RULES_MISSING: 55,
        PaperRuntimeForwardTestPlanRisk.KILL_SWITCH_RULES_MISSING: 50,
        PaperRuntimeForwardTestPlanRisk.PREMATURE_BROKER_SANDBOX_SESSION: 40,
    }.items():
        if risk in risks:
            overall = min(overall, cap)
    return PaperRuntimeForwardTestPlanScore(overall, *scores)


def _select_decision(risks: tuple[PaperRuntimeForwardTestPlanRisk, ...], score: int) -> PaperRuntimeForwardTestPlanDecision:
    if PaperRuntimeForwardTestPlanRisk.PREMATURE_BROKER_SANDBOX_SESSION in risks or score < 45:
        return PaperRuntimeForwardTestPlanDecision.BLOCK_FORWARD_TEST
    if PaperRuntimeForwardTestPlanRisk.FORWARD_TEST_SCOPE_UNCLEAR in risks or PaperRuntimeForwardTestPlanRisk.DURATION_UNDEFINED in risks:
        return PaperRuntimeForwardTestPlanDecision.REQUIRE_SCOPE_FIXES
    if PaperRuntimeForwardTestPlanRisk.HUMAN_SUPERVISION_RULES_MISSING in risks:
        return PaperRuntimeForwardTestPlanDecision.REQUIRE_SUPERVISION_FIXES
    if PaperRuntimeForwardTestPlanRisk.SESSION_LIMITS_MISSING in risks or PaperRuntimeForwardTestPlanRisk.SIMULATED_LOSS_LIMITS_MISSING in risks:
        return PaperRuntimeForwardTestPlanDecision.REQUIRE_LIMIT_FIXES
    if PaperRuntimeForwardTestPlanRisk.OBSERVABILITY_REQUIREMENTS_MISSING in risks or PaperRuntimeForwardTestPlanRisk.JOURNAL_REQUIREMENTS_MISSING in risks:
        return PaperRuntimeForwardTestPlanDecision.REQUIRE_OBSERVABILITY_FIXES
    if PaperRuntimeForwardTestPlanRisk.ROLLBACK_RULES_MISSING in risks:
        return PaperRuntimeForwardTestPlanDecision.REQUIRE_ROLLBACK_FIXES
    if PaperRuntimeForwardTestPlanRisk.KILL_SWITCH_RULES_MISSING in risks:
        return PaperRuntimeForwardTestPlanDecision.REQUIRE_KILL_SWITCH_FIXES
    if risks:
        return PaperRuntimeForwardTestPlanDecision.REQUIRE_SCOPE_FIXES
    return PaperRuntimeForwardTestPlanDecision.APPROVE_PAPER_RUNTIME_FORWARD_TEST_PLAN


def _select_state(decision: PaperRuntimeForwardTestPlanDecision, score: int) -> PaperRuntimeForwardTestPlanState:
    if decision == PaperRuntimeForwardTestPlanDecision.BLOCK_FORWARD_TEST:
        return PaperRuntimeForwardTestPlanState.PLAN_NOT_READY
    if decision != PaperRuntimeForwardTestPlanDecision.APPROVE_PAPER_RUNTIME_FORWARD_TEST_PLAN:
        return PaperRuntimeForwardTestPlanState.PLAN_REVIEW_REQUIRED if score < 82 else PaperRuntimeForwardTestPlanState.PLAN_PARTIALLY_READY
    if score >= 95:
        return PaperRuntimeForwardTestPlanState.READY_FOR_PAPER_BROKER_SANDBOX_SESSION
    return PaperRuntimeForwardTestPlanState.PLAN_READY


def generate_forward_test_plan_recommendations(risks: tuple[PaperRuntimeForwardTestPlanRisk, ...], decision: PaperRuntimeForwardTestPlanDecision | None = None) -> tuple[PaperRuntimeForwardTestPlanRecommendation, ...]:
    recommendations: list[PaperRuntimeForwardTestPlanRecommendation] = []
    if risks:
        recommendations.append(PaperRuntimeForwardTestPlanRecommendation.HOLD_BROKER_SANDBOX_SESSION)
    mapping = {
        PaperRuntimeForwardTestPlanRisk.FORWARD_TEST_SCOPE_UNCLEAR: PaperRuntimeForwardTestPlanRecommendation.CLARIFY_FORWARD_TEST_SCOPE,
        PaperRuntimeForwardTestPlanRisk.DURATION_UNDEFINED: PaperRuntimeForwardTestPlanRecommendation.DEFINE_FORWARD_TEST_DURATION,
        PaperRuntimeForwardTestPlanRisk.SESSION_LIMITS_MISSING: PaperRuntimeForwardTestPlanRecommendation.DEFINE_ALLOWED_SESSION_LIMITS,
        PaperRuntimeForwardTestPlanRisk.SIMULATED_LOSS_LIMITS_MISSING: PaperRuntimeForwardTestPlanRecommendation.DEFINE_SIMULATED_LOSS_LIMITS,
        PaperRuntimeForwardTestPlanRisk.HUMAN_SUPERVISION_RULES_MISSING: PaperRuntimeForwardTestPlanRecommendation.DEFINE_HUMAN_SUPERVISION_RULES,
        PaperRuntimeForwardTestPlanRisk.JOURNAL_REQUIREMENTS_MISSING: PaperRuntimeForwardTestPlanRecommendation.DEFINE_JOURNAL_REQUIREMENTS,
        PaperRuntimeForwardTestPlanRisk.OBSERVABILITY_REQUIREMENTS_MISSING: PaperRuntimeForwardTestPlanRecommendation.DEFINE_OBSERVABILITY_REQUIREMENTS,
        PaperRuntimeForwardTestPlanRisk.ROLLBACK_RULES_MISSING: PaperRuntimeForwardTestPlanRecommendation.DEFINE_ROLLBACK_RULES,
        PaperRuntimeForwardTestPlanRisk.KILL_SWITCH_RULES_MISSING: PaperRuntimeForwardTestPlanRecommendation.DEFINE_KILL_SWITCH_RULES,
        PaperRuntimeForwardTestPlanRisk.SUCCESS_CRITERIA_UNCLEAR: PaperRuntimeForwardTestPlanRecommendation.DEFINE_SUCCESS_CRITERIA,
        PaperRuntimeForwardTestPlanRisk.FAILURE_CRITERIA_UNCLEAR: PaperRuntimeForwardTestPlanRecommendation.DEFINE_FAILURE_CRITERIA,
        PaperRuntimeForwardTestPlanRisk.STOP_CONDITIONS_MISSING: PaperRuntimeForwardTestPlanRecommendation.DEFINE_STOP_CONDITIONS,
        PaperRuntimeForwardTestPlanRisk.PREMATURE_BROKER_SANDBOX_SESSION: PaperRuntimeForwardTestPlanRecommendation.DELAY_BROKER_SANDBOX_SESSION,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(PaperRuntimeForwardTestPlanRecommendation.RUN_FORWARD_TEST_PLAN_REVIEW_SUITE)
    if decision == PaperRuntimeForwardTestPlanDecision.APPROVE_PAPER_RUNTIME_FORWARD_TEST_PLAN:
        recommendations.append(PaperRuntimeForwardTestPlanRecommendation.APPROVE_PAPER_BROKER_SANDBOX_SESSION_PREP)
    return _dedupe(recommendations)


def evaluate_paper_runtime_forward_test_plan(data: PaperRuntimeForwardTestPlanInput | Mapping[str, Any]) -> PaperRuntimeForwardTestPlanResult:
    data = _coerce_input(data)
    sections = _all_sections(data)
    risks = detect_forward_test_plan_risks(data, *sections)
    score = compute_forward_test_plan_score(data, risks, *sections)
    decision = _select_decision(risks, score.overall_score)
    state = _select_state(decision, score.overall_score)
    recommendations = generate_forward_test_plan_recommendations(risks, decision)
    offline_only = _offline_boundary(data)
    summary = f"{state.value}: decision={decision.value}, score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return PaperRuntimeForwardTestPlanResult(state, decision, score.overall_score, score, risks, *sections, recommendations, offline_only, summary)


def render_paper_runtime_forward_test_plan_markdown(result: PaperRuntimeForwardTestPlanResult) -> str:
    lines = [
        "# AGIcore Paper Runtime Forward Test Plan",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Score: {result.forward_test_plan_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Forward Test Plan Sections",
    ]
    sections = (
        result.forward_test_scope,
        result.forward_test_duration,
        result.allowed_session_limits,
        result.simulated_loss_limits,
        result.human_supervision_rules,
        result.journal_requirements,
        result.observability_requirements,
        result.rollback_rules,
        result.kill_switch_rules,
        result.success_criteria,
        result.failure_criteria,
        result.stop_conditions,
    )
    for section in sections:
        lines.append(f"- {section.name}: defined={section.defined}, score={section.score}/100, risks={', '.join(risk.value for risk in section.risks) or 'none'}")
        lines.extend(f"  - {detail}" for detail in section.details if detail)
    lines.append("")
    lines.append("# Forward Test Plan Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Forward Test Plan Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_forward_test_plan_score",
    "define_allowed_session_limits",
    "define_failure_criteria",
    "define_forward_test_duration",
    "define_forward_test_scope",
    "define_human_supervision_rules",
    "define_journal_requirements",
    "define_kill_switch_rules",
    "define_observability_requirements",
    "define_rollback_rules",
    "define_simulated_loss_limits",
    "define_stop_conditions",
    "define_success_criteria",
    "detect_forward_test_plan_risks",
    "evaluate_paper_runtime_forward_test_plan",
    "generate_forward_test_plan_recommendations",
    "render_paper_runtime_forward_test_plan_markdown",
]
