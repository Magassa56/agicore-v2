"""Offline review gate for a future AGIcore Paper Broker Sandbox Session."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_broker_sandbox_session_review_models import (
    PaperBrokerSandboxSessionReviewDecision,
    PaperBrokerSandboxSessionReviewInput,
    PaperBrokerSandboxSessionReviewRecommendation,
    PaperBrokerSandboxSessionReviewResult,
    PaperBrokerSandboxSessionReviewRisk,
    PaperBrokerSandboxSessionReviewScore,
    PaperBrokerSandboxSessionReviewSection,
    PaperBrokerSandboxSessionReviewState,
)


def _coerce_input(data: PaperBrokerSandboxSessionReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxSessionReviewInput:
    if isinstance(data, PaperBrokerSandboxSessionReviewInput):
        return data
    allowed = {field.name for field in fields(PaperBrokerSandboxSessionReviewInput)}
    payload = {key: value for key, value in dict(data).items() if key in allowed}
    return PaperBrokerSandboxSessionReviewInput(**payload)


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


def _confirmed(*values: bool | None) -> bool:
    if any(value is False for value in values):
        return False
    return any(value is True for value in values)


def _upstream_items(data: PaperBrokerSandboxSessionReviewInput) -> tuple[Any, ...]:
    return (
        data.paper_broker_sandbox_session_preparation,
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


def _upstream_risks(data: PaperBrokerSandboxSessionReviewInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperBrokerSandboxSessionReviewInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _offline_boundary(data: PaperBrokerSandboxSessionReviewInput) -> bool:
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
            "API_KEY",
            "CREDENTIAL",
        )
    )


def _section(
    name: str,
    score: int,
    risk: PaperBrokerSandboxSessionReviewRisk,
    failed: bool,
    evidence: tuple[str, ...] = (),
) -> PaperBrokerSandboxSessionReviewSection:
    risks = (risk,) if failed or score < 85 else ()
    return PaperBrokerSandboxSessionReviewSection(name, _clamp(score), not risks and score >= 85, risks, evidence)


def review_sandbox_preparation_readiness(
    data: PaperBrokerSandboxSessionReviewInput | Mapping[str, Any],
) -> PaperBrokerSandboxSessionReviewSection:
    data = _coerce_input(data)
    preparation = data.paper_broker_sandbox_session_preparation
    preparation_state_ok = _state_contains(
        preparation,
        "READY_FOR_PAPER_BROKER_SANDBOX_SESSION_REVIEW",
        "APPROVE_PAPER_BROKER_SANDBOX_SESSION_PREPARATION",
    )
    preparation_approved = (
        data.sandbox_preparation_approved is not False
        and data.sandbox_preparation_reviewed is not False
        and (data.sandbox_preparation_approved is True or preparation_state_ok)
    )
    failed = not preparation_approved or _has_upstream_risk(
        data,
        "SANDBOX_PREPARATION_NOT_APPROVED",
        "FORWARD_TEST_PLAN_NOT_APPROVED",
        "PREMATURE_SANDBOX_SESSION",
        "BLOCK_BROKER_SANDBOX_SESSION",
    )
    score = (
        data.sandbox_preparation_readiness_score
        if data.sandbox_preparation_readiness_score is not None
        else _bool_score(preparation_approved)
    )
    return _section(
        "sandbox_preparation_readiness",
        score,
        PaperBrokerSandboxSessionReviewRisk.SANDBOX_PREPARATION_NOT_APPROVED,
        failed,
        (_value(_get(preparation, "state")), _value(_get(preparation, "decision"))),
    )


def review_broker_sandbox_scope(
    data: PaperBrokerSandboxSessionReviewInput | Mapping[str, Any],
) -> PaperBrokerSandboxSessionReviewSection:
    data = _coerce_input(data)
    scope_clear = _confirmed(
        data.broker_sandbox_scope_reviewed,
        data.broker_sandbox_scope_clear,
        data.sandbox_scope_reviewed,
        data.sandbox_scope_clear,
    )
    failed = not scope_clear or _has_upstream_risk(data, "SCOPE")
    score = data.broker_sandbox_scope_score if data.broker_sandbox_scope_score is not None else _bool_score(scope_clear)
    return _section("broker_sandbox_scope", score, PaperBrokerSandboxSessionReviewRisk.SANDBOX_SCOPE_UNCLEAR, failed)


def review_broker_sandbox_boundaries(
    data: PaperBrokerSandboxSessionReviewInput | Mapping[str, Any],
) -> PaperBrokerSandboxSessionReviewSection:
    data = _coerce_input(data)
    boundaries_complete = _confirmed(
        data.broker_sandbox_boundaries_reviewed,
        data.broker_sandbox_boundaries_complete,
        data.sandbox_boundaries_reviewed,
        data.sandbox_boundaries_complete,
    )
    boundary_ok = boundaries_complete and _offline_boundary(data)
    failed = not boundary_ok or _has_upstream_risk(data, "BOUNDARY", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK")
    score = data.broker_sandbox_boundaries_score if data.broker_sandbox_boundaries_score is not None else _bool_score(boundary_ok)
    return _section(
        "broker_sandbox_boundaries",
        score,
        PaperBrokerSandboxSessionReviewRisk.SANDBOX_BOUNDARY_INCOMPLETE,
        failed,
    )


def review_paper_broker_adapter_requirements(
    data: PaperBrokerSandboxSessionReviewInput | Mapping[str, Any],
) -> PaperBrokerSandboxSessionReviewSection:
    data = _coerce_input(data)
    explicit_rejection = (
        data.paper_broker_adapter_requirements_reviewed is False
        or data.paper_broker_adapter_requirements_complete is False
    )
    adapter_ready = not explicit_rejection and (
        _confirmed(
            data.paper_broker_adapter_requirements_reviewed,
            data.paper_broker_adapter_requirements_complete,
        )
        or _state_contains(data.paper_broker_adapter, "READY_FOR_ALPACA_PAPER_ADAPTER", "READY_FOR_END_TO_END_PAPER")
    )
    failed = not adapter_ready or _has_upstream_risk(data, "ADAPTER", "TRANSLATION", "INCOMPATIBILITY")
    score = (
        data.paper_broker_adapter_requirements_score
        if data.paper_broker_adapter_requirements_score is not None
        else _bool_score(adapter_ready)
    )
    return _section(
        "paper_broker_adapter_requirements",
        score,
        PaperBrokerSandboxSessionReviewRisk.PAPER_BROKER_ADAPTER_REQUIREMENT_INCOMPLETE,
        failed,
    )


def review_mock_to_broker_transition_readiness(
    data: PaperBrokerSandboxSessionReviewInput | Mapping[str, Any],
) -> PaperBrokerSandboxSessionReviewSection:
    data = _coerce_input(data)
    transition_ready = _confirmed(data.mock_to_broker_transition_reviewed, data.mock_to_broker_transition_ready)
    failed = not transition_ready or _has_upstream_risk(data, "MOCK_TO_BROKER", "MOCK_TO_PAPER", "TRANSITION", "DRIFT")
    score = (
        data.mock_to_broker_transition_readiness_score
        if data.mock_to_broker_transition_readiness_score is not None
        else _bool_score(transition_ready)
    )
    return _section(
        "mock_to_broker_transition_readiness",
        score,
        PaperBrokerSandboxSessionReviewRisk.MOCK_TO_BROKER_TRANSITION_NOT_READY,
        failed,
    )


def review_sandbox_connection_readiness(
    data: PaperBrokerSandboxSessionReviewInput | Mapping[str, Any],
) -> PaperBrokerSandboxSessionReviewSection:
    data = _coerce_input(data)
    connection_ready = _confirmed(data.sandbox_connection_reviewed, data.sandbox_connection_ready)
    connection_boundary = data.no_http_transport is True and data.no_websocket_transport is True and data.no_socket_transport is True
    failed = not connection_ready or not connection_boundary or _has_upstream_risk(data, "CONNECTION", "NETWORK", "HTTP", "WEBSOCKET", "SOCKET", "API_ACCESS")
    score = (
        data.sandbox_connection_readiness_score
        if data.sandbox_connection_readiness_score is not None
        else _bool_score(connection_ready and connection_boundary)
    )
    return _section(
        "sandbox_connection_readiness",
        score,
        PaperBrokerSandboxSessionReviewRisk.CONNECTION_READINESS_GAP,
        failed,
    )


def review_sandbox_order_readiness(
    data: PaperBrokerSandboxSessionReviewInput | Mapping[str, Any],
) -> PaperBrokerSandboxSessionReviewSection:
    data = _coerce_input(data)
    order_ready = _confirmed(data.sandbox_order_reviewed, data.sandbox_order_ready) and data.no_real_order is True
    failed = not order_ready or _has_upstream_risk(data, "ORDER", "EXECUTION_LEAK", "REAL_ORDER", "LIVE_EXECUTION")
    score = data.sandbox_order_readiness_score if data.sandbox_order_readiness_score is not None else _bool_score(order_ready)
    return _section(
        "sandbox_order_readiness",
        score,
        PaperBrokerSandboxSessionReviewRisk.ORDER_READINESS_GAP,
        failed,
    )


def review_sandbox_position_readiness(
    data: PaperBrokerSandboxSessionReviewInput | Mapping[str, Any],
) -> PaperBrokerSandboxSessionReviewSection:
    data = _coerce_input(data)
    position_ready = _confirmed(data.sandbox_position_reviewed, data.sandbox_position_ready)
    failed = not position_ready or _has_upstream_risk(data, "POSITION", "RECONCILIATION")
    score = (
        data.sandbox_position_readiness_score
        if data.sandbox_position_readiness_score is not None
        else _bool_score(position_ready)
    )
    return _section(
        "sandbox_position_readiness",
        score,
        PaperBrokerSandboxSessionReviewRisk.POSITION_READINESS_GAP,
        failed,
    )


def review_sandbox_account_readiness(
    data: PaperBrokerSandboxSessionReviewInput | Mapping[str, Any],
) -> PaperBrokerSandboxSessionReviewSection:
    data = _coerce_input(data)
    account_ready = _confirmed(data.sandbox_account_reviewed, data.sandbox_account_ready) and data.no_api_key_read is True
    failed = not account_ready or _has_upstream_risk(data, "ACCOUNT", "CREDENTIAL", "API_KEY")
    score = data.sandbox_account_readiness_score if data.sandbox_account_readiness_score is not None else _bool_score(account_ready)
    return _section(
        "sandbox_account_readiness",
        score,
        PaperBrokerSandboxSessionReviewRisk.ACCOUNT_READINESS_GAP,
        failed,
    )


def review_sandbox_observability_readiness(
    data: PaperBrokerSandboxSessionReviewInput | Mapping[str, Any],
) -> PaperBrokerSandboxSessionReviewSection:
    data = _coerce_input(data)
    explicit_rejection = data.sandbox_observability_reviewed is False or data.sandbox_observability_ready is False
    observability_ready = not explicit_rejection and (
        _confirmed(data.sandbox_observability_reviewed, data.sandbox_observability_ready)
        or _state_contains(
            data.observability_verification,
            "READY",
            "APPROVE",
        )
    )
    failed = not observability_ready or _has_upstream_risk(data, "OBSERVABILITY")
    score = (
        data.sandbox_observability_readiness_score
        if data.sandbox_observability_readiness_score is not None
        else _bool_score(observability_ready)
    )
    return _section(
        "sandbox_observability_readiness",
        score,
        PaperBrokerSandboxSessionReviewRisk.OBSERVABILITY_READINESS_GAP,
        failed,
    )


def review_sandbox_rollback_readiness(
    data: PaperBrokerSandboxSessionReviewInput | Mapping[str, Any],
) -> PaperBrokerSandboxSessionReviewSection:
    data = _coerce_input(data)
    explicit_rejection = data.sandbox_rollback_reviewed is False or data.sandbox_rollback_ready is False
    rollback_ready = not explicit_rejection and (
        _confirmed(data.sandbox_rollback_reviewed, data.sandbox_rollback_ready)
        or _state_contains(
            data.rollback_verification,
            "READY",
            "APPROVE",
        )
    )
    failed = not rollback_ready or _has_upstream_risk(data, "ROLLBACK")
    score = (
        data.sandbox_rollback_readiness_score
        if data.sandbox_rollback_readiness_score is not None
        else _bool_score(rollback_ready)
    )
    return _section(
        "sandbox_rollback_readiness",
        score,
        PaperBrokerSandboxSessionReviewRisk.ROLLBACK_READINESS_GAP,
        failed,
    )


def review_sandbox_kill_switch_readiness(
    data: PaperBrokerSandboxSessionReviewInput | Mapping[str, Any],
) -> PaperBrokerSandboxSessionReviewSection:
    data = _coerce_input(data)
    explicit_rejection = data.sandbox_kill_switch_reviewed is False or data.sandbox_kill_switch_ready is False
    kill_switch_ready = not explicit_rejection and (
        _confirmed(data.sandbox_kill_switch_reviewed, data.sandbox_kill_switch_ready)
        or _state_contains(
            data.kill_switch_verification,
            "READY",
            "APPROVE",
        )
    )
    failed = not kill_switch_ready or _has_upstream_risk(data, "KILL_SWITCH")
    score = (
        data.sandbox_kill_switch_readiness_score
        if data.sandbox_kill_switch_readiness_score is not None
        else _bool_score(kill_switch_ready)
    )
    return _section(
        "sandbox_kill_switch_readiness",
        score,
        PaperBrokerSandboxSessionReviewRisk.KILL_SWITCH_READINESS_GAP,
        failed,
    )


def review_sandbox_human_supervision_readiness(
    data: PaperBrokerSandboxSessionReviewInput | Mapping[str, Any],
) -> PaperBrokerSandboxSessionReviewSection:
    data = _coerce_input(data)
    explicit_rejection = data.sandbox_human_supervision_reviewed is False or data.sandbox_human_supervision_ready is False
    supervision_ready = not explicit_rejection and (
        _confirmed(data.sandbox_human_supervision_reviewed, data.sandbox_human_supervision_ready)
        or _state_contains(
            data.human_validated_paper_session,
            "READY",
            "APPROVE",
        )
    )
    failed = not supervision_ready or _has_upstream_risk(data, "HUMAN", "SUPERVISION", "OPERATOR")
    score = (
        data.sandbox_human_supervision_readiness_score
        if data.sandbox_human_supervision_readiness_score is not None
        else _bool_score(supervision_ready)
    )
    return _section(
        "sandbox_human_supervision_readiness",
        score,
        PaperBrokerSandboxSessionReviewRisk.HUMAN_SUPERVISION_READINESS_GAP,
        failed,
    )


def _all_sections(data: PaperBrokerSandboxSessionReviewInput) -> tuple[PaperBrokerSandboxSessionReviewSection, ...]:
    return (
        review_sandbox_preparation_readiness(data),
        review_broker_sandbox_scope(data),
        review_broker_sandbox_boundaries(data),
        review_paper_broker_adapter_requirements(data),
        review_mock_to_broker_transition_readiness(data),
        review_sandbox_connection_readiness(data),
        review_sandbox_order_readiness(data),
        review_sandbox_position_readiness(data),
        review_sandbox_account_readiness(data),
        review_sandbox_observability_readiness(data),
        review_sandbox_rollback_readiness(data),
        review_sandbox_kill_switch_readiness(data),
        review_sandbox_human_supervision_readiness(data),
    )


def detect_broker_sandbox_review_risks(
    data: PaperBrokerSandboxSessionReviewInput | Mapping[str, Any],
    *sections: PaperBrokerSandboxSessionReviewSection,
) -> tuple[PaperBrokerSandboxSessionReviewRisk, ...]:
    data = _coerce_input(data)
    if not sections:
        sections = _all_sections(data)
    risks: list[PaperBrokerSandboxSessionReviewRisk] = []
    for section in sections:
        risks.extend(section.risks)
    requested = _confirmed(data.paper_broker_sandbox_session_requested, data.sandbox_session_review_requested)
    if not requested or not _offline_boundary(data):
        risks.append(PaperBrokerSandboxSessionReviewRisk.PREMATURE_BROKER_SANDBOX_SESSION)
    return _dedupe(risks)


def compute_broker_sandbox_review_score(
    data: PaperBrokerSandboxSessionReviewInput | Mapping[str, Any],
    risks: tuple[PaperBrokerSandboxSessionReviewRisk, ...] = (),
    *sections: PaperBrokerSandboxSessionReviewSection,
) -> PaperBrokerSandboxSessionReviewScore:
    data = _coerce_input(data)
    if not sections:
        sections = _all_sections(data)
    scores = tuple(section.score for section in sections)
    overall = _clamp(_average(scores) - min(85, len(set(risks)) * 5))
    for risk, cap in {
        PaperBrokerSandboxSessionReviewRisk.SANDBOX_PREPARATION_NOT_APPROVED: 50,
        PaperBrokerSandboxSessionReviewRisk.SANDBOX_SCOPE_UNCLEAR: 60,
        PaperBrokerSandboxSessionReviewRisk.SANDBOX_BOUNDARY_INCOMPLETE: 45,
        PaperBrokerSandboxSessionReviewRisk.PAPER_BROKER_ADAPTER_REQUIREMENT_INCOMPLETE: 55,
        PaperBrokerSandboxSessionReviewRisk.MOCK_TO_BROKER_TRANSITION_NOT_READY: 55,
        PaperBrokerSandboxSessionReviewRisk.CONNECTION_READINESS_GAP: 50,
        PaperBrokerSandboxSessionReviewRisk.ORDER_READINESS_GAP: 55,
        PaperBrokerSandboxSessionReviewRisk.POSITION_READINESS_GAP: 60,
        PaperBrokerSandboxSessionReviewRisk.ACCOUNT_READINESS_GAP: 55,
        PaperBrokerSandboxSessionReviewRisk.OBSERVABILITY_READINESS_GAP: 60,
        PaperBrokerSandboxSessionReviewRisk.ROLLBACK_READINESS_GAP: 55,
        PaperBrokerSandboxSessionReviewRisk.KILL_SWITCH_READINESS_GAP: 50,
        PaperBrokerSandboxSessionReviewRisk.HUMAN_SUPERVISION_READINESS_GAP: 45,
        PaperBrokerSandboxSessionReviewRisk.PREMATURE_BROKER_SANDBOX_SESSION: 40,
    }.items():
        if risk in risks:
            overall = min(overall, cap)
    return PaperBrokerSandboxSessionReviewScore(overall, *scores)


def _select_decision(
    risks: tuple[PaperBrokerSandboxSessionReviewRisk, ...],
    score: int,
) -> PaperBrokerSandboxSessionReviewDecision:
    if PaperBrokerSandboxSessionReviewRisk.PREMATURE_BROKER_SANDBOX_SESSION in risks or score < 45:
        return PaperBrokerSandboxSessionReviewDecision.BLOCK_PAPER_BROKER_SANDBOX_SESSION
    if PaperBrokerSandboxSessionReviewRisk.SANDBOX_PREPARATION_NOT_APPROVED in risks:
        return PaperBrokerSandboxSessionReviewDecision.REQUIRE_PREPARATION_FIXES
    if (
        PaperBrokerSandboxSessionReviewRisk.SANDBOX_SCOPE_UNCLEAR in risks
        or PaperBrokerSandboxSessionReviewRisk.SANDBOX_BOUNDARY_INCOMPLETE in risks
    ):
        return PaperBrokerSandboxSessionReviewDecision.REQUIRE_BOUNDARY_FIXES
    if (
        PaperBrokerSandboxSessionReviewRisk.PAPER_BROKER_ADAPTER_REQUIREMENT_INCOMPLETE in risks
        or PaperBrokerSandboxSessionReviewRisk.MOCK_TO_BROKER_TRANSITION_NOT_READY in risks
    ):
        return PaperBrokerSandboxSessionReviewDecision.REQUIRE_ADAPTER_FIXES
    if PaperBrokerSandboxSessionReviewRisk.CONNECTION_READINESS_GAP in risks:
        return PaperBrokerSandboxSessionReviewDecision.REQUIRE_CONNECTION_FIXES
    if PaperBrokerSandboxSessionReviewRisk.ORDER_READINESS_GAP in risks:
        return PaperBrokerSandboxSessionReviewDecision.REQUIRE_ORDER_FIXES
    if PaperBrokerSandboxSessionReviewRisk.POSITION_READINESS_GAP in risks:
        return PaperBrokerSandboxSessionReviewDecision.REQUIRE_POSITION_FIXES
    if PaperBrokerSandboxSessionReviewRisk.ACCOUNT_READINESS_GAP in risks:
        return PaperBrokerSandboxSessionReviewDecision.REQUIRE_ACCOUNT_FIXES
    if PaperBrokerSandboxSessionReviewRisk.OBSERVABILITY_READINESS_GAP in risks:
        return PaperBrokerSandboxSessionReviewDecision.REQUIRE_OBSERVABILITY_FIXES
    if PaperBrokerSandboxSessionReviewRisk.ROLLBACK_READINESS_GAP in risks:
        return PaperBrokerSandboxSessionReviewDecision.REQUIRE_ROLLBACK_FIXES
    if PaperBrokerSandboxSessionReviewRisk.KILL_SWITCH_READINESS_GAP in risks:
        return PaperBrokerSandboxSessionReviewDecision.REQUIRE_KILL_SWITCH_FIXES
    if PaperBrokerSandboxSessionReviewRisk.HUMAN_SUPERVISION_READINESS_GAP in risks:
        return PaperBrokerSandboxSessionReviewDecision.REQUIRE_SUPERVISION_FIXES
    if risks:
        return PaperBrokerSandboxSessionReviewDecision.REQUIRE_BOUNDARY_FIXES
    return PaperBrokerSandboxSessionReviewDecision.APPROVE_PAPER_BROKER_SANDBOX_SESSION


def _select_state(
    decision: PaperBrokerSandboxSessionReviewDecision,
    score: int,
) -> PaperBrokerSandboxSessionReviewState:
    if decision == PaperBrokerSandboxSessionReviewDecision.BLOCK_PAPER_BROKER_SANDBOX_SESSION:
        return PaperBrokerSandboxSessionReviewState.NOT_READY
    if decision != PaperBrokerSandboxSessionReviewDecision.APPROVE_PAPER_BROKER_SANDBOX_SESSION:
        return PaperBrokerSandboxSessionReviewState.REVIEW_REQUIRED if score < 82 else PaperBrokerSandboxSessionReviewState.PARTIALLY_READY
    if score >= 95:
        return PaperBrokerSandboxSessionReviewState.READY_FOR_PAPER_BROKER_SANDBOX_SESSION
    return PaperBrokerSandboxSessionReviewState.SANDBOX_SESSION_REVIEW_READY


def generate_broker_sandbox_review_recommendations(
    risks: tuple[PaperBrokerSandboxSessionReviewRisk, ...],
    decision: PaperBrokerSandboxSessionReviewDecision | None = None,
) -> tuple[PaperBrokerSandboxSessionReviewRecommendation, ...]:
    recommendations: list[PaperBrokerSandboxSessionReviewRecommendation] = []
    if risks:
        recommendations.append(PaperBrokerSandboxSessionReviewRecommendation.HOLD_PAPER_BROKER_SANDBOX_SESSION)
    mapping = {
        PaperBrokerSandboxSessionReviewRisk.SANDBOX_PREPARATION_NOT_APPROVED: PaperBrokerSandboxSessionReviewRecommendation.APPROVE_SANDBOX_PREPARATION_FIRST,
        PaperBrokerSandboxSessionReviewRisk.SANDBOX_SCOPE_UNCLEAR: PaperBrokerSandboxSessionReviewRecommendation.CLARIFY_BROKER_SANDBOX_SCOPE,
        PaperBrokerSandboxSessionReviewRisk.SANDBOX_BOUNDARY_INCOMPLETE: PaperBrokerSandboxSessionReviewRecommendation.COMPLETE_BROKER_SANDBOX_BOUNDARIES,
        PaperBrokerSandboxSessionReviewRisk.PAPER_BROKER_ADAPTER_REQUIREMENT_INCOMPLETE: PaperBrokerSandboxSessionReviewRecommendation.COMPLETE_PAPER_BROKER_ADAPTER_REQUIREMENTS,
        PaperBrokerSandboxSessionReviewRisk.MOCK_TO_BROKER_TRANSITION_NOT_READY: PaperBrokerSandboxSessionReviewRecommendation.COMPLETE_MOCK_TO_BROKER_TRANSITION_REVIEW,
        PaperBrokerSandboxSessionReviewRisk.CONNECTION_READINESS_GAP: PaperBrokerSandboxSessionReviewRecommendation.COMPLETE_SANDBOX_CONNECTION_REVIEW,
        PaperBrokerSandboxSessionReviewRisk.ORDER_READINESS_GAP: PaperBrokerSandboxSessionReviewRecommendation.COMPLETE_SANDBOX_ORDER_REVIEW,
        PaperBrokerSandboxSessionReviewRisk.POSITION_READINESS_GAP: PaperBrokerSandboxSessionReviewRecommendation.COMPLETE_SANDBOX_POSITION_REVIEW,
        PaperBrokerSandboxSessionReviewRisk.ACCOUNT_READINESS_GAP: PaperBrokerSandboxSessionReviewRecommendation.COMPLETE_SANDBOX_ACCOUNT_REVIEW,
        PaperBrokerSandboxSessionReviewRisk.OBSERVABILITY_READINESS_GAP: PaperBrokerSandboxSessionReviewRecommendation.COMPLETE_SANDBOX_OBSERVABILITY_REVIEW,
        PaperBrokerSandboxSessionReviewRisk.ROLLBACK_READINESS_GAP: PaperBrokerSandboxSessionReviewRecommendation.COMPLETE_SANDBOX_ROLLBACK_REVIEW,
        PaperBrokerSandboxSessionReviewRisk.KILL_SWITCH_READINESS_GAP: PaperBrokerSandboxSessionReviewRecommendation.COMPLETE_SANDBOX_KILL_SWITCH_REVIEW,
        PaperBrokerSandboxSessionReviewRisk.HUMAN_SUPERVISION_READINESS_GAP: PaperBrokerSandboxSessionReviewRecommendation.COMPLETE_SANDBOX_HUMAN_SUPERVISION_REVIEW,
        PaperBrokerSandboxSessionReviewRisk.PREMATURE_BROKER_SANDBOX_SESSION: PaperBrokerSandboxSessionReviewRecommendation.DELAY_PAPER_BROKER_SANDBOX_SESSION,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(PaperBrokerSandboxSessionReviewRecommendation.RUN_PAPER_BROKER_SANDBOX_SESSION_REVIEW_SUITE)
    if decision == PaperBrokerSandboxSessionReviewDecision.APPROVE_PAPER_BROKER_SANDBOX_SESSION:
        recommendations.append(PaperBrokerSandboxSessionReviewRecommendation.APPROVE_PAPER_BROKER_SANDBOX_SESSION)
    return _dedupe(recommendations)


def evaluate_paper_broker_sandbox_session_review(
    data: PaperBrokerSandboxSessionReviewInput | Mapping[str, Any],
) -> PaperBrokerSandboxSessionReviewResult:
    data = _coerce_input(data)
    sections = _all_sections(data)
    risks = detect_broker_sandbox_review_risks(data, *sections)
    score = compute_broker_sandbox_review_score(data, risks, *sections)
    decision = _select_decision(risks, score.overall_score)
    state = _select_state(decision, score.overall_score)
    recommendations = generate_broker_sandbox_review_recommendations(risks, decision)
    offline_only = _offline_boundary(data)
    summary = f"{state.value}: decision={decision.value}, score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return PaperBrokerSandboxSessionReviewResult(state, decision, score.overall_score, score, risks, *sections, recommendations, offline_only, summary)


def render_paper_broker_sandbox_session_review_markdown(result: PaperBrokerSandboxSessionReviewResult) -> str:
    lines = [
        "# AGIcore Paper Broker Sandbox Session Review",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Score: {result.review_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Broker Sandbox Session Review Sections",
    ]
    sections = (
        result.sandbox_preparation_readiness,
        result.broker_sandbox_scope,
        result.broker_sandbox_boundaries,
        result.paper_broker_adapter_requirements,
        result.mock_to_broker_transition_readiness,
        result.sandbox_connection_readiness,
        result.sandbox_order_readiness,
        result.sandbox_position_readiness,
        result.sandbox_account_readiness,
        result.sandbox_observability_readiness,
        result.sandbox_rollback_readiness,
        result.sandbox_kill_switch_readiness,
        result.sandbox_human_supervision_readiness,
    )
    for section in sections:
        risks = ", ".join(risk.value for risk in section.risks) or "none"
        lines.append(f"- {section.name}: passed={section.passed}, score={section.score}/100, risks={risks}")
        lines.extend(f"  - {item}" for item in section.evidence if item)
    lines.append("")
    lines.append("# Broker Sandbox Session Review Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Broker Sandbox Session Review Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_broker_sandbox_review_score",
    "detect_broker_sandbox_review_risks",
    "evaluate_paper_broker_sandbox_session_review",
    "generate_broker_sandbox_review_recommendations",
    "render_paper_broker_sandbox_session_review_markdown",
    "review_broker_sandbox_boundaries",
    "review_broker_sandbox_scope",
    "review_mock_to_broker_transition_readiness",
    "review_paper_broker_adapter_requirements",
    "review_sandbox_account_readiness",
    "review_sandbox_connection_readiness",
    "review_sandbox_human_supervision_readiness",
    "review_sandbox_kill_switch_readiness",
    "review_sandbox_observability_readiness",
    "review_sandbox_order_readiness",
    "review_sandbox_position_readiness",
    "review_sandbox_preparation_readiness",
    "review_sandbox_rollback_readiness",
]
