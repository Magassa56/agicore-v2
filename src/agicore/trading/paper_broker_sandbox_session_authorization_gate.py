"""Offline authorization gate for a future AGIcore Paper Broker Sandbox Dry Run."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_broker_sandbox_session_authorization_gate_models import (
    PaperBrokerSandboxSessionAuthorizationGateDecision,
    PaperBrokerSandboxSessionAuthorizationGateInput,
    PaperBrokerSandboxSessionAuthorizationGateRecommendation,
    PaperBrokerSandboxSessionAuthorizationGateResult,
    PaperBrokerSandboxSessionAuthorizationGateRisk,
    PaperBrokerSandboxSessionAuthorizationGateScore,
    PaperBrokerSandboxSessionAuthorizationGateSection,
    PaperBrokerSandboxSessionAuthorizationGateState,
)


def _coerce_input(
    data: PaperBrokerSandboxSessionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxSessionAuthorizationGateInput:
    if isinstance(data, PaperBrokerSandboxSessionAuthorizationGateInput):
        return data
    allowed = {field.name for field in fields(PaperBrokerSandboxSessionAuthorizationGateInput)}
    payload = {key: value for key, value in dict(data).items() if key in allowed}
    return PaperBrokerSandboxSessionAuthorizationGateInput(**payload)


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


def _upstream_items(data: PaperBrokerSandboxSessionAuthorizationGateInput) -> tuple[Any, ...]:
    return (
        data.paper_broker_sandbox_session_review,
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


def _upstream_risks(data: PaperBrokerSandboxSessionAuthorizationGateInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperBrokerSandboxSessionAuthorizationGateInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _offline_boundary(data: PaperBrokerSandboxSessionAuthorizationGateInput) -> bool:
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
            "API_KEY",
            "CREDENTIAL",
        )
    )


def _section(
    name: str,
    score: int,
    risk: PaperBrokerSandboxSessionAuthorizationGateRisk,
    failed: bool,
    evidence: tuple[str, ...] = (),
) -> PaperBrokerSandboxSessionAuthorizationGateSection:
    risks = (risk,) if failed or score < 85 else ()
    return PaperBrokerSandboxSessionAuthorizationGateSection(name, _clamp(score), not risks and score >= 85, risks, evidence)


def verify_sandbox_review_approval(
    data: PaperBrokerSandboxSessionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxSessionAuthorizationGateSection:
    data = _coerce_input(data)
    review = data.paper_broker_sandbox_session_review
    review_state_ok = _state_contains(
        review,
        "READY_FOR_PAPER_BROKER_SANDBOX_SESSION",
        "APPROVE_PAPER_BROKER_SANDBOX_SESSION",
    )
    review_approved = (
        data.sandbox_review_approved is not False
        and data.sandbox_reviewed is not False
        and (data.sandbox_review_approved is True or review_state_ok)
    )
    failed = not review_approved or _has_upstream_risk(
        data,
        "SANDBOX_REVIEW_NOT_APPROVED",
        "PREMATURE_BROKER_SANDBOX_SESSION",
        "BLOCK_PAPER_BROKER_SANDBOX_SESSION",
    )
    score = data.sandbox_review_approval_score if data.sandbox_review_approval_score is not None else _bool_score(review_approved)
    return _section(
        "sandbox_review_approval",
        score,
        PaperBrokerSandboxSessionAuthorizationGateRisk.SANDBOX_REVIEW_NOT_APPROVED,
        failed,
        (_value(_get(review, "state")), _value(_get(review, "decision"))),
    )


def verify_authorization_scope(
    data: PaperBrokerSandboxSessionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxSessionAuthorizationGateSection:
    data = _coerce_input(data)
    scope_clear = _confirmed(data.authorization_scope_reviewed, data.authorization_scope_clear)
    failed = not scope_clear or _has_upstream_risk(data, "SCOPE")
    score = data.authorization_scope_score if data.authorization_scope_score is not None else _bool_score(scope_clear)
    return _section("authorization_scope", score, PaperBrokerSandboxSessionAuthorizationGateRisk.AUTHORIZATION_SCOPE_UNCLEAR, failed)


def verify_authorization_boundaries(
    data: PaperBrokerSandboxSessionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxSessionAuthorizationGateSection:
    data = _coerce_input(data)
    boundaries_complete = _confirmed(data.authorization_boundaries_reviewed, data.authorization_boundaries_complete)
    boundary_ok = boundaries_complete and _offline_boundary(data)
    failed = not boundary_ok or _has_upstream_risk(data, "BOUNDARY", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK")
    score = data.authorization_boundaries_score if data.authorization_boundaries_score is not None else _bool_score(boundary_ok)
    return _section("authorization_boundaries", score, PaperBrokerSandboxSessionAuthorizationGateRisk.AUTHORIZATION_BOUNDARY_GAP, failed)


def verify_broker_connection_authorization(
    data: PaperBrokerSandboxSessionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxSessionAuthorizationGateSection:
    data = _coerce_input(data)
    connection_authorized = _confirmed(data.broker_connection_authorization_reviewed, data.broker_connection_authorized)
    connection_boundary = (
        data.no_real_broker is True
        and data.no_alpaca_real is True
        and data.no_http_transport is True
        and data.no_websocket_transport is True
        and data.no_socket_transport is True
        and data.no_external_api is True
    )
    failed = not connection_authorized or not connection_boundary or _has_upstream_risk(
        data,
        "CONNECTION",
        "NETWORK",
        "HTTP",
        "WEBSOCKET",
        "SOCKET",
        "BROKER_CONNECTIVITY",
        "API_ACCESS",
    )
    score = (
        data.broker_connection_authorization_score
        if data.broker_connection_authorization_score is not None
        else _bool_score(connection_authorized and connection_boundary)
    )
    return _section(
        "broker_connection_authorization",
        score,
        PaperBrokerSandboxSessionAuthorizationGateRisk.BROKER_CONNECTION_AUTHORIZATION_GAP,
        failed,
    )


def verify_order_execution_authorization(
    data: PaperBrokerSandboxSessionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxSessionAuthorizationGateSection:
    data = _coerce_input(data)
    order_authorized = (
        _confirmed(data.order_execution_authorization_reviewed, data.order_execution_authorized)
        and data.no_real_order is True
        and data.no_live_execution is True
    )
    failed = not order_authorized or _has_upstream_risk(data, "ORDER", "EXECUTION_LEAK", "REAL_ORDER", "LIVE_EXECUTION")
    score = (
        data.order_execution_authorization_score
        if data.order_execution_authorization_score is not None
        else _bool_score(order_authorized)
    )
    return _section(
        "order_execution_authorization",
        score,
        PaperBrokerSandboxSessionAuthorizationGateRisk.ORDER_EXECUTION_AUTHORIZATION_GAP,
        failed,
    )


def verify_position_management_authorization(
    data: PaperBrokerSandboxSessionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxSessionAuthorizationGateSection:
    data = _coerce_input(data)
    position_authorized = _confirmed(data.position_management_authorization_reviewed, data.position_management_authorized)
    failed = not position_authorized or _has_upstream_risk(data, "POSITION", "RECONCILIATION")
    score = (
        data.position_management_authorization_score
        if data.position_management_authorization_score is not None
        else _bool_score(position_authorized)
    )
    return _section(
        "position_management_authorization",
        score,
        PaperBrokerSandboxSessionAuthorizationGateRisk.POSITION_MANAGEMENT_AUTHORIZATION_GAP,
        failed,
    )


def verify_account_access_authorization(
    data: PaperBrokerSandboxSessionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxSessionAuthorizationGateSection:
    data = _coerce_input(data)
    account_authorized = (
        _confirmed(data.account_access_authorization_reviewed, data.account_access_authorized)
        and data.no_api_key_read is True
        and data.no_real_account_access is True
    )
    failed = not account_authorized or _has_upstream_risk(data, "ACCOUNT", "REAL_ACCOUNT", "CREDENTIAL", "API_KEY")
    score = (
        data.account_access_authorization_score
        if data.account_access_authorization_score is not None
        else _bool_score(account_authorized)
    )
    return _section(
        "account_access_authorization",
        score,
        PaperBrokerSandboxSessionAuthorizationGateRisk.ACCOUNT_ACCESS_AUTHORIZATION_GAP,
        failed,
    )


def verify_observability_authorization(
    data: PaperBrokerSandboxSessionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxSessionAuthorizationGateSection:
    data = _coerce_input(data)
    explicit_rejection = data.observability_authorization_reviewed is False or data.observability_authorized is False
    observability_authorized = not explicit_rejection and (
        _confirmed(data.observability_authorization_reviewed, data.observability_authorized)
        or _state_contains(data.observability_verification, "READY", "APPROVE")
    )
    failed = not observability_authorized or _has_upstream_risk(data, "OBSERVABILITY")
    score = (
        data.observability_authorization_score
        if data.observability_authorization_score is not None
        else _bool_score(observability_authorized)
    )
    return _section(
        "observability_authorization",
        score,
        PaperBrokerSandboxSessionAuthorizationGateRisk.OBSERVABILITY_AUTHORIZATION_GAP,
        failed,
    )


def verify_rollback_authorization(
    data: PaperBrokerSandboxSessionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxSessionAuthorizationGateSection:
    data = _coerce_input(data)
    explicit_rejection = data.rollback_authorization_reviewed is False or data.rollback_authorized is False
    rollback_authorized = not explicit_rejection and (
        _confirmed(data.rollback_authorization_reviewed, data.rollback_authorized)
        or _state_contains(data.rollback_verification, "READY", "APPROVE")
    )
    failed = not rollback_authorized or _has_upstream_risk(data, "ROLLBACK")
    score = data.rollback_authorization_score if data.rollback_authorization_score is not None else _bool_score(rollback_authorized)
    return _section(
        "rollback_authorization",
        score,
        PaperBrokerSandboxSessionAuthorizationGateRisk.ROLLBACK_AUTHORIZATION_GAP,
        failed,
    )


def verify_kill_switch_authorization(
    data: PaperBrokerSandboxSessionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxSessionAuthorizationGateSection:
    data = _coerce_input(data)
    explicit_rejection = data.kill_switch_authorization_reviewed is False or data.kill_switch_authorized is False
    kill_switch_authorized = not explicit_rejection and (
        _confirmed(data.kill_switch_authorization_reviewed, data.kill_switch_authorized)
        or _state_contains(data.kill_switch_verification, "READY", "APPROVE")
    )
    failed = not kill_switch_authorized or _has_upstream_risk(data, "KILL_SWITCH")
    score = (
        data.kill_switch_authorization_score
        if data.kill_switch_authorization_score is not None
        else _bool_score(kill_switch_authorized)
    )
    return _section(
        "kill_switch_authorization",
        score,
        PaperBrokerSandboxSessionAuthorizationGateRisk.KILL_SWITCH_AUTHORIZATION_GAP,
        failed,
    )


def verify_human_supervision_authorization(
    data: PaperBrokerSandboxSessionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxSessionAuthorizationGateSection:
    data = _coerce_input(data)
    explicit_rejection = data.human_supervision_authorization_reviewed is False or data.human_supervision_authorized is False
    supervision_authorized = not explicit_rejection and (
        _confirmed(data.human_supervision_authorization_reviewed, data.human_supervision_authorized)
        or _state_contains(data.human_validated_paper_session, "READY", "APPROVE")
    )
    failed = not supervision_authorized or _has_upstream_risk(data, "HUMAN", "SUPERVISION", "OPERATOR")
    score = (
        data.human_supervision_authorization_score
        if data.human_supervision_authorization_score is not None
        else _bool_score(supervision_authorized)
    )
    return _section(
        "human_supervision_authorization",
        score,
        PaperBrokerSandboxSessionAuthorizationGateRisk.HUMAN_SUPERVISION_AUTHORIZATION_GAP,
        failed,
    )


def verify_journal_authorization(
    data: PaperBrokerSandboxSessionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxSessionAuthorizationGateSection:
    data = _coerce_input(data)
    journal_authorized = _confirmed(data.journal_authorization_reviewed, data.journal_authorized)
    failed = not journal_authorized or _has_upstream_risk(data, "JOURNAL", "AUDIT_TRAIL", "TRACE")
    score = data.journal_authorization_score if data.journal_authorization_score is not None else _bool_score(journal_authorized)
    return _section(
        "journal_authorization",
        score,
        PaperBrokerSandboxSessionAuthorizationGateRisk.JOURNAL_AUTHORIZATION_GAP,
        failed,
    )


def verify_stop_conditions_authorization(
    data: PaperBrokerSandboxSessionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxSessionAuthorizationGateSection:
    data = _coerce_input(data)
    stop_conditions_authorized = _confirmed(
        data.stop_conditions_authorization_reviewed,
        data.stop_conditions_authorized,
    )
    failed = not stop_conditions_authorized or _has_upstream_risk(data, "STOP_CONDITION", "HALT", "EMERGENCY_STOP")
    score = (
        data.stop_conditions_authorization_score
        if data.stop_conditions_authorization_score is not None
        else _bool_score(stop_conditions_authorized)
    )
    return _section(
        "stop_conditions_authorization",
        score,
        PaperBrokerSandboxSessionAuthorizationGateRisk.STOP_CONDITIONS_AUTHORIZATION_GAP,
        failed,
    )


def _all_sections(
    data: PaperBrokerSandboxSessionAuthorizationGateInput,
) -> tuple[PaperBrokerSandboxSessionAuthorizationGateSection, ...]:
    return (
        verify_sandbox_review_approval(data),
        verify_authorization_scope(data),
        verify_authorization_boundaries(data),
        verify_broker_connection_authorization(data),
        verify_order_execution_authorization(data),
        verify_position_management_authorization(data),
        verify_account_access_authorization(data),
        verify_observability_authorization(data),
        verify_rollback_authorization(data),
        verify_kill_switch_authorization(data),
        verify_human_supervision_authorization(data),
        verify_journal_authorization(data),
        verify_stop_conditions_authorization(data),
    )


def detect_authorization_gate_risks(
    data: PaperBrokerSandboxSessionAuthorizationGateInput | Mapping[str, Any],
    *sections: PaperBrokerSandboxSessionAuthorizationGateSection,
) -> tuple[PaperBrokerSandboxSessionAuthorizationGateRisk, ...]:
    data = _coerce_input(data)
    if not sections:
        sections = _all_sections(data)
    risks: list[PaperBrokerSandboxSessionAuthorizationGateRisk] = []
    for section in sections:
        risks.extend(section.risks)
    requested = _confirmed(data.paper_broker_sandbox_dry_run_requested, data.sandbox_authorization_gate_requested)
    if not requested or not _offline_boundary(data):
        risks.append(PaperBrokerSandboxSessionAuthorizationGateRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN)
    return _dedupe(risks)


def compute_authorization_gate_score(
    data: PaperBrokerSandboxSessionAuthorizationGateInput | Mapping[str, Any],
    risks: tuple[PaperBrokerSandboxSessionAuthorizationGateRisk, ...] = (),
    *sections: PaperBrokerSandboxSessionAuthorizationGateSection,
) -> PaperBrokerSandboxSessionAuthorizationGateScore:
    data = _coerce_input(data)
    if not sections:
        sections = _all_sections(data)
    scores = tuple(section.score for section in sections)
    overall = _clamp(_average(scores) - min(85, len(set(risks)) * 5))
    for risk, cap in {
        PaperBrokerSandboxSessionAuthorizationGateRisk.SANDBOX_REVIEW_NOT_APPROVED: 50,
        PaperBrokerSandboxSessionAuthorizationGateRisk.AUTHORIZATION_SCOPE_UNCLEAR: 60,
        PaperBrokerSandboxSessionAuthorizationGateRisk.AUTHORIZATION_BOUNDARY_GAP: 45,
        PaperBrokerSandboxSessionAuthorizationGateRisk.BROKER_CONNECTION_AUTHORIZATION_GAP: 50,
        PaperBrokerSandboxSessionAuthorizationGateRisk.ORDER_EXECUTION_AUTHORIZATION_GAP: 55,
        PaperBrokerSandboxSessionAuthorizationGateRisk.POSITION_MANAGEMENT_AUTHORIZATION_GAP: 60,
        PaperBrokerSandboxSessionAuthorizationGateRisk.ACCOUNT_ACCESS_AUTHORIZATION_GAP: 50,
        PaperBrokerSandboxSessionAuthorizationGateRisk.OBSERVABILITY_AUTHORIZATION_GAP: 60,
        PaperBrokerSandboxSessionAuthorizationGateRisk.ROLLBACK_AUTHORIZATION_GAP: 55,
        PaperBrokerSandboxSessionAuthorizationGateRisk.KILL_SWITCH_AUTHORIZATION_GAP: 50,
        PaperBrokerSandboxSessionAuthorizationGateRisk.HUMAN_SUPERVISION_AUTHORIZATION_GAP: 45,
        PaperBrokerSandboxSessionAuthorizationGateRisk.JOURNAL_AUTHORIZATION_GAP: 60,
        PaperBrokerSandboxSessionAuthorizationGateRisk.STOP_CONDITIONS_AUTHORIZATION_GAP: 45,
        PaperBrokerSandboxSessionAuthorizationGateRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN: 40,
    }.items():
        if risk in risks:
            overall = min(overall, cap)
    return PaperBrokerSandboxSessionAuthorizationGateScore(overall, *scores)


def _select_decision(
    risks: tuple[PaperBrokerSandboxSessionAuthorizationGateRisk, ...],
    score: int,
) -> PaperBrokerSandboxSessionAuthorizationGateDecision:
    if PaperBrokerSandboxSessionAuthorizationGateRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN in risks or score < 45:
        return PaperBrokerSandboxSessionAuthorizationGateDecision.BLOCK_PAPER_BROKER_SANDBOX_SESSION
    if PaperBrokerSandboxSessionAuthorizationGateRisk.SANDBOX_REVIEW_NOT_APPROVED in risks:
        return PaperBrokerSandboxSessionAuthorizationGateDecision.REQUIRE_SANDBOX_REVIEW_FIXES
    if PaperBrokerSandboxSessionAuthorizationGateRisk.AUTHORIZATION_SCOPE_UNCLEAR in risks:
        return PaperBrokerSandboxSessionAuthorizationGateDecision.REQUIRE_SCOPE_FIXES
    if (
        PaperBrokerSandboxSessionAuthorizationGateRisk.AUTHORIZATION_BOUNDARY_GAP in risks
        or PaperBrokerSandboxSessionAuthorizationGateRisk.STOP_CONDITIONS_AUTHORIZATION_GAP in risks
    ):
        return PaperBrokerSandboxSessionAuthorizationGateDecision.REQUIRE_BOUNDARY_FIXES
    if PaperBrokerSandboxSessionAuthorizationGateRisk.BROKER_CONNECTION_AUTHORIZATION_GAP in risks:
        return PaperBrokerSandboxSessionAuthorizationGateDecision.REQUIRE_CONNECTION_AUTHORIZATION_FIXES
    if PaperBrokerSandboxSessionAuthorizationGateRisk.ORDER_EXECUTION_AUTHORIZATION_GAP in risks:
        return PaperBrokerSandboxSessionAuthorizationGateDecision.REQUIRE_ORDER_AUTHORIZATION_FIXES
    if PaperBrokerSandboxSessionAuthorizationGateRisk.POSITION_MANAGEMENT_AUTHORIZATION_GAP in risks:
        return PaperBrokerSandboxSessionAuthorizationGateDecision.REQUIRE_POSITION_AUTHORIZATION_FIXES
    if PaperBrokerSandboxSessionAuthorizationGateRisk.ACCOUNT_ACCESS_AUTHORIZATION_GAP in risks:
        return PaperBrokerSandboxSessionAuthorizationGateDecision.REQUIRE_ACCOUNT_AUTHORIZATION_FIXES
    if PaperBrokerSandboxSessionAuthorizationGateRisk.OBSERVABILITY_AUTHORIZATION_GAP in risks:
        return PaperBrokerSandboxSessionAuthorizationGateDecision.REQUIRE_OBSERVABILITY_AUTHORIZATION_FIXES
    if PaperBrokerSandboxSessionAuthorizationGateRisk.ROLLBACK_AUTHORIZATION_GAP in risks:
        return PaperBrokerSandboxSessionAuthorizationGateDecision.REQUIRE_ROLLBACK_AUTHORIZATION_FIXES
    if PaperBrokerSandboxSessionAuthorizationGateRisk.KILL_SWITCH_AUTHORIZATION_GAP in risks:
        return PaperBrokerSandboxSessionAuthorizationGateDecision.REQUIRE_KILL_SWITCH_AUTHORIZATION_FIXES
    if (
        PaperBrokerSandboxSessionAuthorizationGateRisk.HUMAN_SUPERVISION_AUTHORIZATION_GAP in risks
        or PaperBrokerSandboxSessionAuthorizationGateRisk.JOURNAL_AUTHORIZATION_GAP in risks
    ):
        return PaperBrokerSandboxSessionAuthorizationGateDecision.REQUIRE_SUPERVISION_AUTHORIZATION_FIXES
    if risks:
        return PaperBrokerSandboxSessionAuthorizationGateDecision.REQUIRE_BOUNDARY_FIXES
    return PaperBrokerSandboxSessionAuthorizationGateDecision.APPROVE_PAPER_BROKER_SANDBOX_AUTHORIZATION_GATE


def _select_state(
    decision: PaperBrokerSandboxSessionAuthorizationGateDecision,
    score: int,
) -> PaperBrokerSandboxSessionAuthorizationGateState:
    if decision == PaperBrokerSandboxSessionAuthorizationGateDecision.BLOCK_PAPER_BROKER_SANDBOX_SESSION:
        return PaperBrokerSandboxSessionAuthorizationGateState.NOT_AUTHORIZED
    if decision != PaperBrokerSandboxSessionAuthorizationGateDecision.APPROVE_PAPER_BROKER_SANDBOX_AUTHORIZATION_GATE:
        return (
            PaperBrokerSandboxSessionAuthorizationGateState.AUTHORIZATION_REVIEW_REQUIRED
            if score < 82
            else PaperBrokerSandboxSessionAuthorizationGateState.PARTIALLY_AUTHORIZED
        )
    if score >= 95:
        return PaperBrokerSandboxSessionAuthorizationGateState.READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN
    return PaperBrokerSandboxSessionAuthorizationGateState.SANDBOX_SESSION_AUTHORIZATION_READY


def generate_authorization_gate_recommendations(
    risks: tuple[PaperBrokerSandboxSessionAuthorizationGateRisk, ...],
    decision: PaperBrokerSandboxSessionAuthorizationGateDecision | None = None,
) -> tuple[PaperBrokerSandboxSessionAuthorizationGateRecommendation, ...]:
    recommendations: list[PaperBrokerSandboxSessionAuthorizationGateRecommendation] = []
    if risks:
        recommendations.append(PaperBrokerSandboxSessionAuthorizationGateRecommendation.HOLD_PAPER_BROKER_SANDBOX_DRY_RUN)
    mapping = {
        PaperBrokerSandboxSessionAuthorizationGateRisk.SANDBOX_REVIEW_NOT_APPROVED: PaperBrokerSandboxSessionAuthorizationGateRecommendation.APPROVE_SANDBOX_SESSION_REVIEW_FIRST,
        PaperBrokerSandboxSessionAuthorizationGateRisk.AUTHORIZATION_SCOPE_UNCLEAR: PaperBrokerSandboxSessionAuthorizationGateRecommendation.CLARIFY_AUTHORIZATION_SCOPE,
        PaperBrokerSandboxSessionAuthorizationGateRisk.AUTHORIZATION_BOUNDARY_GAP: PaperBrokerSandboxSessionAuthorizationGateRecommendation.COMPLETE_AUTHORIZATION_BOUNDARIES,
        PaperBrokerSandboxSessionAuthorizationGateRisk.BROKER_CONNECTION_AUTHORIZATION_GAP: PaperBrokerSandboxSessionAuthorizationGateRecommendation.COMPLETE_BROKER_CONNECTION_AUTHORIZATION,
        PaperBrokerSandboxSessionAuthorizationGateRisk.ORDER_EXECUTION_AUTHORIZATION_GAP: PaperBrokerSandboxSessionAuthorizationGateRecommendation.COMPLETE_ORDER_EXECUTION_AUTHORIZATION,
        PaperBrokerSandboxSessionAuthorizationGateRisk.POSITION_MANAGEMENT_AUTHORIZATION_GAP: PaperBrokerSandboxSessionAuthorizationGateRecommendation.COMPLETE_POSITION_MANAGEMENT_AUTHORIZATION,
        PaperBrokerSandboxSessionAuthorizationGateRisk.ACCOUNT_ACCESS_AUTHORIZATION_GAP: PaperBrokerSandboxSessionAuthorizationGateRecommendation.COMPLETE_ACCOUNT_ACCESS_AUTHORIZATION,
        PaperBrokerSandboxSessionAuthorizationGateRisk.OBSERVABILITY_AUTHORIZATION_GAP: PaperBrokerSandboxSessionAuthorizationGateRecommendation.COMPLETE_OBSERVABILITY_AUTHORIZATION,
        PaperBrokerSandboxSessionAuthorizationGateRisk.ROLLBACK_AUTHORIZATION_GAP: PaperBrokerSandboxSessionAuthorizationGateRecommendation.COMPLETE_ROLLBACK_AUTHORIZATION,
        PaperBrokerSandboxSessionAuthorizationGateRisk.KILL_SWITCH_AUTHORIZATION_GAP: PaperBrokerSandboxSessionAuthorizationGateRecommendation.COMPLETE_KILL_SWITCH_AUTHORIZATION,
        PaperBrokerSandboxSessionAuthorizationGateRisk.HUMAN_SUPERVISION_AUTHORIZATION_GAP: PaperBrokerSandboxSessionAuthorizationGateRecommendation.COMPLETE_HUMAN_SUPERVISION_AUTHORIZATION,
        PaperBrokerSandboxSessionAuthorizationGateRisk.JOURNAL_AUTHORIZATION_GAP: PaperBrokerSandboxSessionAuthorizationGateRecommendation.COMPLETE_JOURNAL_AUTHORIZATION,
        PaperBrokerSandboxSessionAuthorizationGateRisk.STOP_CONDITIONS_AUTHORIZATION_GAP: PaperBrokerSandboxSessionAuthorizationGateRecommendation.COMPLETE_STOP_CONDITIONS_AUTHORIZATION,
        PaperBrokerSandboxSessionAuthorizationGateRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN: PaperBrokerSandboxSessionAuthorizationGateRecommendation.DELAY_PAPER_BROKER_SANDBOX_DRY_RUN,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(PaperBrokerSandboxSessionAuthorizationGateRecommendation.RUN_PAPER_BROKER_SANDBOX_AUTHORIZATION_GATE_SUITE)
    if decision == PaperBrokerSandboxSessionAuthorizationGateDecision.APPROVE_PAPER_BROKER_SANDBOX_AUTHORIZATION_GATE:
        recommendations.append(PaperBrokerSandboxSessionAuthorizationGateRecommendation.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN)
    return _dedupe(recommendations)


def evaluate_paper_broker_sandbox_session_authorization_gate(
    data: PaperBrokerSandboxSessionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxSessionAuthorizationGateResult:
    data = _coerce_input(data)
    sections = _all_sections(data)
    risks = detect_authorization_gate_risks(data, *sections)
    score = compute_authorization_gate_score(data, risks, *sections)
    decision = _select_decision(risks, score.overall_score)
    state = _select_state(decision, score.overall_score)
    recommendations = generate_authorization_gate_recommendations(risks, decision)
    offline_only = _offline_boundary(data)
    summary = f"{state.value}: decision={decision.value}, score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return PaperBrokerSandboxSessionAuthorizationGateResult(
        state,
        decision,
        score.overall_score,
        score,
        risks,
        *sections,
        recommendations,
        offline_only,
        summary,
    )


def render_paper_broker_sandbox_session_authorization_gate_markdown(
    result: PaperBrokerSandboxSessionAuthorizationGateResult,
) -> str:
    lines = [
        "# AGIcore Paper Broker Sandbox Session Authorization Gate",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Score: {result.authorization_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Paper Broker Sandbox Authorization Sections",
    ]
    sections = (
        result.sandbox_review_approval,
        result.authorization_scope,
        result.authorization_boundaries,
        result.broker_connection_authorization,
        result.order_execution_authorization,
        result.position_management_authorization,
        result.account_access_authorization,
        result.observability_authorization,
        result.rollback_authorization,
        result.kill_switch_authorization,
        result.human_supervision_authorization,
        result.journal_authorization,
        result.stop_conditions_authorization,
    )
    for section in sections:
        risks = ", ".join(risk.value for risk in section.risks) or "none"
        lines.append(f"- {section.name}: authorized={section.authorized}, score={section.score}/100, risks={risks}")
        lines.extend(f"  - {item}" for item in section.evidence if item)
    lines.append("")
    lines.append("# Paper Broker Sandbox Authorization Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Paper Broker Sandbox Authorization Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_authorization_gate_score",
    "detect_authorization_gate_risks",
    "evaluate_paper_broker_sandbox_session_authorization_gate",
    "generate_authorization_gate_recommendations",
    "render_paper_broker_sandbox_session_authorization_gate_markdown",
    "verify_account_access_authorization",
    "verify_authorization_boundaries",
    "verify_authorization_scope",
    "verify_broker_connection_authorization",
    "verify_human_supervision_authorization",
    "verify_journal_authorization",
    "verify_kill_switch_authorization",
    "verify_observability_authorization",
    "verify_order_execution_authorization",
    "verify_position_management_authorization",
    "verify_rollback_authorization",
    "verify_sandbox_review_approval",
    "verify_stop_conditions_authorization",
]

