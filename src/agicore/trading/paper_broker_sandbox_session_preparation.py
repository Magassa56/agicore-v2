"""Offline preparation for a future AGIcore Paper Broker Sandbox Session."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_broker_sandbox_session_preparation_models import (
    PaperBrokerSandboxSessionPreparationDecision,
    PaperBrokerSandboxSessionPreparationInput,
    PaperBrokerSandboxSessionPreparationRecommendation,
    PaperBrokerSandboxSessionPreparationResult,
    PaperBrokerSandboxSessionPreparationRisk,
    PaperBrokerSandboxSessionPreparationScore,
    PaperBrokerSandboxSessionPreparationSection,
    PaperBrokerSandboxSessionPreparationState,
)


def _coerce_input(data: PaperBrokerSandboxSessionPreparationInput | Mapping[str, Any]) -> PaperBrokerSandboxSessionPreparationInput:
    if isinstance(data, PaperBrokerSandboxSessionPreparationInput):
        return data
    return PaperBrokerSandboxSessionPreparationInput(**dict(data))


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


def _upstream_items(data: PaperBrokerSandboxSessionPreparationInput) -> tuple[Any, ...]:
    return (
        data.paper_runtime_forward_test_plan,
        data.supervised_paper_runtime_trial,
        data.official_paper_validation_report,
        data.paper_runtime_validation,
        data.paper_runtime_release_candidate,
        data.paper_trading_runtime,
        data.paper_broker_adapter,
        data.alpaca_paper_adapter,
        data.broker_paper_sandbox,
        data.mock_alpaca_session,
        data.mock_connectivity_layer,
        data.observability_verification,
        data.rollback_verification,
        data.kill_switch_verification,
        data.human_validated_paper_session,
        data.supervised_paper_session,
    )


def _upstream_risks(data: PaperBrokerSandboxSessionPreparationInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperBrokerSandboxSessionPreparationInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _section(
    name: str,
    score: int,
    risk: PaperBrokerSandboxSessionPreparationRisk,
    failed: bool,
    details: tuple[str, ...] = (),
) -> PaperBrokerSandboxSessionPreparationSection:
    risks = (risk,) if failed or score < 85 else ()
    return PaperBrokerSandboxSessionPreparationSection(name, _clamp(score), not risks and score >= 85, risks, details)


def review_forward_test_plan_readiness(data: PaperBrokerSandboxSessionPreparationInput | Mapping[str, Any]) -> PaperBrokerSandboxSessionPreparationSection:
    data = _coerce_input(data)
    plan = data.paper_runtime_forward_test_plan
    approved = data.forward_test_plan_approved is True and _state_contains(
        plan,
        "READY_FOR_PAPER_BROKER_SANDBOX_SESSION",
        "APPROVE_PAPER_RUNTIME_FORWARD_TEST_PLAN",
        "APPROVE_PAPER_BROKER_SANDBOX_SESSION_PREP",
    )
    failed = not approved or _has_upstream_risk(data, "FORWARD_TEST", "PREMATURE_BROKER_SANDBOX_SESSION")
    score = data.forward_test_plan_readiness_score if data.forward_test_plan_readiness_score is not None else _bool_score(approved)
    return _section("forward_test_plan_readiness", score, PaperBrokerSandboxSessionPreparationRisk.FORWARD_TEST_PLAN_NOT_APPROVED, failed, (_value(_get(plan, "state")), _value(_get(plan, "decision"))))


def define_broker_sandbox_session_scope(data: PaperBrokerSandboxSessionPreparationInput | Mapping[str, Any]) -> PaperBrokerSandboxSessionPreparationSection:
    data = _coerce_input(data)
    failed = data.sandbox_session_scope_defined is not True or _has_upstream_risk(data, "SCOPE")
    score = data.sandbox_session_scope_score if data.sandbox_session_scope_score is not None else _bool_score(data.sandbox_session_scope_defined)
    return _section("sandbox_session_scope", score, PaperBrokerSandboxSessionPreparationRisk.SANDBOX_SCOPE_UNCLEAR, failed)


def define_broker_sandbox_session_boundaries(data: PaperBrokerSandboxSessionPreparationInput | Mapping[str, Any]) -> PaperBrokerSandboxSessionPreparationSection:
    data = _coerce_input(data)
    failed = data.sandbox_session_boundaries_defined is not True or not _offline_boundary(data)
    score = data.sandbox_session_boundaries_score if data.sandbox_session_boundaries_score is not None else _bool_score(data.sandbox_session_boundaries_defined and _offline_boundary(data))
    return _section("sandbox_session_boundaries", score, PaperBrokerSandboxSessionPreparationRisk.SANDBOX_BOUNDARY_GAP, failed)


def define_paper_broker_adapter_requirements(data: PaperBrokerSandboxSessionPreparationInput | Mapping[str, Any]) -> PaperBrokerSandboxSessionPreparationSection:
    data = _coerce_input(data)
    failed = data.paper_broker_adapter_requirements_defined is not True or _has_upstream_risk(data, "ADAPTER", "TRANSLATION")
    score = data.paper_broker_adapter_requirements_score if data.paper_broker_adapter_requirements_score is not None else _bool_score(data.paper_broker_adapter_requirements_defined)
    return _section("paper_broker_adapter_requirements", score, PaperBrokerSandboxSessionPreparationRisk.PAPER_BROKER_ADAPTER_REQUIREMENT_GAP, failed)


def define_mock_to_broker_transition_requirements(data: PaperBrokerSandboxSessionPreparationInput | Mapping[str, Any]) -> PaperBrokerSandboxSessionPreparationSection:
    data = _coerce_input(data)
    failed = data.mock_to_broker_transition_requirements_defined is not True or _has_upstream_risk(data, "MOCK_TO_PAPER", "TRANSITION", "DRIFT")
    score = data.mock_to_broker_transition_requirements_score if data.mock_to_broker_transition_requirements_score is not None else _bool_score(data.mock_to_broker_transition_requirements_defined)
    return _section("mock_to_broker_transition_requirements", score, PaperBrokerSandboxSessionPreparationRisk.MOCK_TO_BROKER_TRANSITION_GAP, failed)


def define_sandbox_connection_preconditions(data: PaperBrokerSandboxSessionPreparationInput | Mapping[str, Any]) -> PaperBrokerSandboxSessionPreparationSection:
    data = _coerce_input(data)
    failed = data.sandbox_connection_preconditions_defined is not True or _has_upstream_risk(data, "CONNECTION", "NETWORK", "HTTP", "SOCKET", "API_ACCESS")
    score = data.sandbox_connection_preconditions_score if data.sandbox_connection_preconditions_score is not None else _bool_score(data.sandbox_connection_preconditions_defined)
    return _section("sandbox_connection_preconditions", score, PaperBrokerSandboxSessionPreparationRisk.CONNECTION_PRECONDITION_GAP, failed)


def define_sandbox_order_preconditions(data: PaperBrokerSandboxSessionPreparationInput | Mapping[str, Any]) -> PaperBrokerSandboxSessionPreparationSection:
    data = _coerce_input(data)
    failed = data.sandbox_order_preconditions_defined is not True or _has_upstream_risk(data, "ORDER", "EXECUTION_LEAK")
    score = data.sandbox_order_preconditions_score if data.sandbox_order_preconditions_score is not None else _bool_score(data.sandbox_order_preconditions_defined)
    return _section("sandbox_order_preconditions", score, PaperBrokerSandboxSessionPreparationRisk.ORDER_PRECONDITION_GAP, failed)


def define_sandbox_position_preconditions(data: PaperBrokerSandboxSessionPreparationInput | Mapping[str, Any]) -> PaperBrokerSandboxSessionPreparationSection:
    data = _coerce_input(data)
    failed = data.sandbox_position_preconditions_defined is not True or _has_upstream_risk(data, "POSITION")
    score = data.sandbox_position_preconditions_score if data.sandbox_position_preconditions_score is not None else _bool_score(data.sandbox_position_preconditions_defined)
    return _section("sandbox_position_preconditions", score, PaperBrokerSandboxSessionPreparationRisk.POSITION_PRECONDITION_GAP, failed)


def define_sandbox_account_preconditions(data: PaperBrokerSandboxSessionPreparationInput | Mapping[str, Any]) -> PaperBrokerSandboxSessionPreparationSection:
    data = _coerce_input(data)
    failed = data.sandbox_account_preconditions_defined is not True or _has_upstream_risk(data, "ACCOUNT", "CREDENTIAL")
    score = data.sandbox_account_preconditions_score if data.sandbox_account_preconditions_score is not None else _bool_score(data.sandbox_account_preconditions_defined)
    return _section("sandbox_account_preconditions", score, PaperBrokerSandboxSessionPreparationRisk.ACCOUNT_PRECONDITION_GAP, failed)


def define_sandbox_observability_requirements(data: PaperBrokerSandboxSessionPreparationInput | Mapping[str, Any]) -> PaperBrokerSandboxSessionPreparationSection:
    data = _coerce_input(data)
    failed = data.sandbox_observability_requirements_defined is not True or _has_upstream_risk(data, "OBSERVABILITY")
    score = data.sandbox_observability_requirements_score if data.sandbox_observability_requirements_score is not None else _bool_score(data.sandbox_observability_requirements_defined)
    return _section("sandbox_observability_requirements", score, PaperBrokerSandboxSessionPreparationRisk.OBSERVABILITY_REQUIREMENT_GAP, failed)


def define_sandbox_rollback_requirements(data: PaperBrokerSandboxSessionPreparationInput | Mapping[str, Any]) -> PaperBrokerSandboxSessionPreparationSection:
    data = _coerce_input(data)
    failed = data.sandbox_rollback_requirements_defined is not True or _has_upstream_risk(data, "ROLLBACK")
    score = data.sandbox_rollback_requirements_score if data.sandbox_rollback_requirements_score is not None else _bool_score(data.sandbox_rollback_requirements_defined)
    return _section("sandbox_rollback_requirements", score, PaperBrokerSandboxSessionPreparationRisk.ROLLBACK_REQUIREMENT_GAP, failed)


def define_sandbox_kill_switch_requirements(data: PaperBrokerSandboxSessionPreparationInput | Mapping[str, Any]) -> PaperBrokerSandboxSessionPreparationSection:
    data = _coerce_input(data)
    failed = data.sandbox_kill_switch_requirements_defined is not True or _has_upstream_risk(data, "KILL_SWITCH")
    score = data.sandbox_kill_switch_requirements_score if data.sandbox_kill_switch_requirements_score is not None else _bool_score(data.sandbox_kill_switch_requirements_defined)
    return _section("sandbox_kill_switch_requirements", score, PaperBrokerSandboxSessionPreparationRisk.KILL_SWITCH_REQUIREMENT_GAP, failed)


def define_sandbox_human_supervision_requirements(data: PaperBrokerSandboxSessionPreparationInput | Mapping[str, Any]) -> PaperBrokerSandboxSessionPreparationSection:
    data = _coerce_input(data)
    failed = data.sandbox_human_supervision_requirements_defined is not True or _has_upstream_risk(data, "HUMAN", "SUPERVISION")
    score = data.sandbox_human_supervision_requirements_score if data.sandbox_human_supervision_requirements_score is not None else _bool_score(data.sandbox_human_supervision_requirements_defined)
    return _section("sandbox_human_supervision_requirements", score, PaperBrokerSandboxSessionPreparationRisk.HUMAN_SUPERVISION_REQUIREMENT_GAP, failed)


def _offline_boundary(data: PaperBrokerSandboxSessionPreparationInput) -> bool:
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
        and data.no_real_order is True
        and _get(data.paper_runtime_forward_test_plan, "offline_only", True) is True
        and not _has_upstream_risk(data, "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK", "BROKER_CONNECTIVITY", "EXTERNAL_DEPENDENCY")
    )


def _all_sections(data: PaperBrokerSandboxSessionPreparationInput) -> tuple[PaperBrokerSandboxSessionPreparationSection, ...]:
    return (
        review_forward_test_plan_readiness(data),
        define_broker_sandbox_session_scope(data),
        define_broker_sandbox_session_boundaries(data),
        define_paper_broker_adapter_requirements(data),
        define_mock_to_broker_transition_requirements(data),
        define_sandbox_connection_preconditions(data),
        define_sandbox_order_preconditions(data),
        define_sandbox_position_preconditions(data),
        define_sandbox_account_preconditions(data),
        define_sandbox_observability_requirements(data),
        define_sandbox_rollback_requirements(data),
        define_sandbox_kill_switch_requirements(data),
        define_sandbox_human_supervision_requirements(data),
    )


def detect_broker_sandbox_preparation_risks(
    data: PaperBrokerSandboxSessionPreparationInput | Mapping[str, Any],
    *sections: PaperBrokerSandboxSessionPreparationSection,
) -> tuple[PaperBrokerSandboxSessionPreparationRisk, ...]:
    data = _coerce_input(data)
    if not sections:
        sections = _all_sections(data)
    risks: list[PaperBrokerSandboxSessionPreparationRisk] = []
    for section in sections:
        risks.extend(section.risks)
    if data.sandbox_session_requested is not True or not _offline_boundary(data):
        risks.append(PaperBrokerSandboxSessionPreparationRisk.PREMATURE_SANDBOX_SESSION)
    return _dedupe(risks)


def compute_broker_sandbox_preparation_score(
    data: PaperBrokerSandboxSessionPreparationInput | Mapping[str, Any],
    risks: tuple[PaperBrokerSandboxSessionPreparationRisk, ...] = (),
    *sections: PaperBrokerSandboxSessionPreparationSection,
) -> PaperBrokerSandboxSessionPreparationScore:
    data = _coerce_input(data)
    if not sections:
        sections = _all_sections(data)
    scores = tuple(section.score for section in sections)
    overall = _clamp(_average(scores) - min(85, len(set(risks)) * 5))
    for risk, cap in {
        PaperBrokerSandboxSessionPreparationRisk.FORWARD_TEST_PLAN_NOT_APPROVED: 50,
        PaperBrokerSandboxSessionPreparationRisk.SANDBOX_BOUNDARY_GAP: 45,
        PaperBrokerSandboxSessionPreparationRisk.PAPER_BROKER_ADAPTER_REQUIREMENT_GAP: 55,
        PaperBrokerSandboxSessionPreparationRisk.CONNECTION_PRECONDITION_GAP: 50,
        PaperBrokerSandboxSessionPreparationRisk.ORDER_PRECONDITION_GAP: 55,
        PaperBrokerSandboxSessionPreparationRisk.OBSERVABILITY_REQUIREMENT_GAP: 60,
        PaperBrokerSandboxSessionPreparationRisk.ROLLBACK_REQUIREMENT_GAP: 55,
        PaperBrokerSandboxSessionPreparationRisk.KILL_SWITCH_REQUIREMENT_GAP: 50,
        PaperBrokerSandboxSessionPreparationRisk.HUMAN_SUPERVISION_REQUIREMENT_GAP: 45,
        PaperBrokerSandboxSessionPreparationRisk.PREMATURE_SANDBOX_SESSION: 40,
    }.items():
        if risk in risks:
            overall = min(overall, cap)
    return PaperBrokerSandboxSessionPreparationScore(overall, *scores)


def _select_decision(
    risks: tuple[PaperBrokerSandboxSessionPreparationRisk, ...],
    score: int,
) -> PaperBrokerSandboxSessionPreparationDecision:
    if PaperBrokerSandboxSessionPreparationRisk.PREMATURE_SANDBOX_SESSION in risks or score < 45:
        return PaperBrokerSandboxSessionPreparationDecision.BLOCK_BROKER_SANDBOX_SESSION
    if PaperBrokerSandboxSessionPreparationRisk.FORWARD_TEST_PLAN_NOT_APPROVED in risks:
        return PaperBrokerSandboxSessionPreparationDecision.REQUIRE_FORWARD_TEST_PLAN_FIXES
    if PaperBrokerSandboxSessionPreparationRisk.SANDBOX_BOUNDARY_GAP in risks or PaperBrokerSandboxSessionPreparationRisk.SANDBOX_SCOPE_UNCLEAR in risks:
        return PaperBrokerSandboxSessionPreparationDecision.REQUIRE_BOUNDARY_FIXES
    if (
        PaperBrokerSandboxSessionPreparationRisk.PAPER_BROKER_ADAPTER_REQUIREMENT_GAP in risks
        or PaperBrokerSandboxSessionPreparationRisk.MOCK_TO_BROKER_TRANSITION_GAP in risks
        or PaperBrokerSandboxSessionPreparationRisk.CONNECTION_PRECONDITION_GAP in risks
        or PaperBrokerSandboxSessionPreparationRisk.ORDER_PRECONDITION_GAP in risks
        or PaperBrokerSandboxSessionPreparationRisk.POSITION_PRECONDITION_GAP in risks
        or PaperBrokerSandboxSessionPreparationRisk.ACCOUNT_PRECONDITION_GAP in risks
    ):
        return PaperBrokerSandboxSessionPreparationDecision.REQUIRE_ADAPTER_REQUIREMENT_FIXES
    if PaperBrokerSandboxSessionPreparationRisk.OBSERVABILITY_REQUIREMENT_GAP in risks:
        return PaperBrokerSandboxSessionPreparationDecision.REQUIRE_OBSERVABILITY_FIXES
    if PaperBrokerSandboxSessionPreparationRisk.ROLLBACK_REQUIREMENT_GAP in risks:
        return PaperBrokerSandboxSessionPreparationDecision.REQUIRE_ROLLBACK_FIXES
    if PaperBrokerSandboxSessionPreparationRisk.KILL_SWITCH_REQUIREMENT_GAP in risks:
        return PaperBrokerSandboxSessionPreparationDecision.REQUIRE_KILL_SWITCH_FIXES
    if PaperBrokerSandboxSessionPreparationRisk.HUMAN_SUPERVISION_REQUIREMENT_GAP in risks:
        return PaperBrokerSandboxSessionPreparationDecision.REQUIRE_SUPERVISION_FIXES
    if risks:
        return PaperBrokerSandboxSessionPreparationDecision.REQUIRE_BOUNDARY_FIXES
    return PaperBrokerSandboxSessionPreparationDecision.APPROVE_PAPER_BROKER_SANDBOX_SESSION_PREPARATION


def _select_state(
    decision: PaperBrokerSandboxSessionPreparationDecision,
    score: int,
) -> PaperBrokerSandboxSessionPreparationState:
    if decision == PaperBrokerSandboxSessionPreparationDecision.BLOCK_BROKER_SANDBOX_SESSION:
        return PaperBrokerSandboxSessionPreparationState.NOT_READY
    if decision != PaperBrokerSandboxSessionPreparationDecision.APPROVE_PAPER_BROKER_SANDBOX_SESSION_PREPARATION:
        return PaperBrokerSandboxSessionPreparationState.PREPARATION_REVIEW_REQUIRED if score < 82 else PaperBrokerSandboxSessionPreparationState.PARTIALLY_PREPARED
    if score >= 95:
        return PaperBrokerSandboxSessionPreparationState.READY_FOR_PAPER_BROKER_SANDBOX_SESSION_REVIEW
    return PaperBrokerSandboxSessionPreparationState.SANDBOX_SESSION_PREPARED


def generate_broker_sandbox_preparation_recommendations(
    risks: tuple[PaperBrokerSandboxSessionPreparationRisk, ...],
    decision: PaperBrokerSandboxSessionPreparationDecision | None = None,
) -> tuple[PaperBrokerSandboxSessionPreparationRecommendation, ...]:
    recommendations: list[PaperBrokerSandboxSessionPreparationRecommendation] = []
    if risks:
        recommendations.append(PaperBrokerSandboxSessionPreparationRecommendation.HOLD_PAPER_BROKER_SANDBOX_SESSION)
    mapping = {
        PaperBrokerSandboxSessionPreparationRisk.FORWARD_TEST_PLAN_NOT_APPROVED: PaperBrokerSandboxSessionPreparationRecommendation.APPROVE_FORWARD_TEST_PLAN_FIRST,
        PaperBrokerSandboxSessionPreparationRisk.SANDBOX_SCOPE_UNCLEAR: PaperBrokerSandboxSessionPreparationRecommendation.CLARIFY_SANDBOX_SESSION_SCOPE,
        PaperBrokerSandboxSessionPreparationRisk.SANDBOX_BOUNDARY_GAP: PaperBrokerSandboxSessionPreparationRecommendation.DEFINE_SANDBOX_BOUNDARIES,
        PaperBrokerSandboxSessionPreparationRisk.PAPER_BROKER_ADAPTER_REQUIREMENT_GAP: PaperBrokerSandboxSessionPreparationRecommendation.DEFINE_PAPER_BROKER_ADAPTER_REQUIREMENTS,
        PaperBrokerSandboxSessionPreparationRisk.MOCK_TO_BROKER_TRANSITION_GAP: PaperBrokerSandboxSessionPreparationRecommendation.DEFINE_MOCK_TO_BROKER_TRANSITION_REQUIREMENTS,
        PaperBrokerSandboxSessionPreparationRisk.CONNECTION_PRECONDITION_GAP: PaperBrokerSandboxSessionPreparationRecommendation.DEFINE_SANDBOX_CONNECTION_PRECONDITIONS,
        PaperBrokerSandboxSessionPreparationRisk.ORDER_PRECONDITION_GAP: PaperBrokerSandboxSessionPreparationRecommendation.DEFINE_SANDBOX_ORDER_PRECONDITIONS,
        PaperBrokerSandboxSessionPreparationRisk.POSITION_PRECONDITION_GAP: PaperBrokerSandboxSessionPreparationRecommendation.DEFINE_SANDBOX_POSITION_PRECONDITIONS,
        PaperBrokerSandboxSessionPreparationRisk.ACCOUNT_PRECONDITION_GAP: PaperBrokerSandboxSessionPreparationRecommendation.DEFINE_SANDBOX_ACCOUNT_PRECONDITIONS,
        PaperBrokerSandboxSessionPreparationRisk.OBSERVABILITY_REQUIREMENT_GAP: PaperBrokerSandboxSessionPreparationRecommendation.DEFINE_SANDBOX_OBSERVABILITY_REQUIREMENTS,
        PaperBrokerSandboxSessionPreparationRisk.ROLLBACK_REQUIREMENT_GAP: PaperBrokerSandboxSessionPreparationRecommendation.DEFINE_SANDBOX_ROLLBACK_REQUIREMENTS,
        PaperBrokerSandboxSessionPreparationRisk.KILL_SWITCH_REQUIREMENT_GAP: PaperBrokerSandboxSessionPreparationRecommendation.DEFINE_SANDBOX_KILL_SWITCH_REQUIREMENTS,
        PaperBrokerSandboxSessionPreparationRisk.HUMAN_SUPERVISION_REQUIREMENT_GAP: PaperBrokerSandboxSessionPreparationRecommendation.DEFINE_SANDBOX_HUMAN_SUPERVISION_REQUIREMENTS,
        PaperBrokerSandboxSessionPreparationRisk.PREMATURE_SANDBOX_SESSION: PaperBrokerSandboxSessionPreparationRecommendation.DELAY_SANDBOX_SESSION,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(PaperBrokerSandboxSessionPreparationRecommendation.RUN_BROKER_SANDBOX_PREPARATION_REVIEW_SUITE)
    if decision == PaperBrokerSandboxSessionPreparationDecision.APPROVE_PAPER_BROKER_SANDBOX_SESSION_PREPARATION:
        recommendations.append(PaperBrokerSandboxSessionPreparationRecommendation.APPROVE_PAPER_BROKER_SANDBOX_SESSION_REVIEW)
    return _dedupe(recommendations)


def evaluate_paper_broker_sandbox_session_preparation(
    data: PaperBrokerSandboxSessionPreparationInput | Mapping[str, Any],
) -> PaperBrokerSandboxSessionPreparationResult:
    data = _coerce_input(data)
    sections = _all_sections(data)
    risks = detect_broker_sandbox_preparation_risks(data, *sections)
    score = compute_broker_sandbox_preparation_score(data, risks, *sections)
    decision = _select_decision(risks, score.overall_score)
    state = _select_state(decision, score.overall_score)
    recommendations = generate_broker_sandbox_preparation_recommendations(risks, decision)
    offline_only = _offline_boundary(data)
    summary = f"{state.value}: decision={decision.value}, score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return PaperBrokerSandboxSessionPreparationResult(state, decision, score.overall_score, score, risks, *sections, recommendations, offline_only, summary)


def render_paper_broker_sandbox_session_preparation_markdown(result: PaperBrokerSandboxSessionPreparationResult) -> str:
    lines = [
        "# AGIcore Paper Broker Sandbox Session Preparation",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Score: {result.preparation_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Broker Sandbox Preparation Sections",
    ]
    sections = (
        result.forward_test_plan_readiness,
        result.sandbox_session_scope,
        result.sandbox_session_boundaries,
        result.paper_broker_adapter_requirements,
        result.mock_to_broker_transition_requirements,
        result.sandbox_connection_preconditions,
        result.sandbox_order_preconditions,
        result.sandbox_position_preconditions,
        result.sandbox_account_preconditions,
        result.sandbox_observability_requirements,
        result.sandbox_rollback_requirements,
        result.sandbox_kill_switch_requirements,
        result.sandbox_human_supervision_requirements,
    )
    for section in sections:
        risks = ", ".join(risk.value for risk in section.risks) or "none"
        lines.append(f"- {section.name}: defined={section.defined}, score={section.score}/100, risks={risks}")
        lines.extend(f"  - {detail}" for detail in section.details if detail)
    lines.append("")
    lines.append("# Broker Sandbox Preparation Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Broker Sandbox Preparation Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_broker_sandbox_preparation_score",
    "define_broker_sandbox_session_boundaries",
    "define_broker_sandbox_session_scope",
    "define_mock_to_broker_transition_requirements",
    "define_paper_broker_adapter_requirements",
    "define_sandbox_account_preconditions",
    "define_sandbox_connection_preconditions",
    "define_sandbox_human_supervision_requirements",
    "define_sandbox_kill_switch_requirements",
    "define_sandbox_observability_requirements",
    "define_sandbox_order_preconditions",
    "define_sandbox_position_preconditions",
    "define_sandbox_rollback_requirements",
    "detect_broker_sandbox_preparation_risks",
    "evaluate_paper_broker_sandbox_session_preparation",
    "generate_broker_sandbox_preparation_recommendations",
    "render_paper_broker_sandbox_session_preparation_markdown",
    "review_forward_test_plan_readiness",
]
