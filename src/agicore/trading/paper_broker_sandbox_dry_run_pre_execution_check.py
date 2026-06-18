"""Offline check before a future AGIcore Paper Broker Sandbox Dry Run execution review."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_broker_sandbox_dry_run_pre_execution_check_models import (
    PaperBrokerSandboxDryRunPreExecutionCheckDecision,
    PaperBrokerSandboxDryRunPreExecutionCheckInput,
    PaperBrokerSandboxDryRunPreExecutionCheckRecommendation,
    PaperBrokerSandboxDryRunPreExecutionCheckResult,
    PaperBrokerSandboxDryRunPreExecutionCheckRisk,
    PaperBrokerSandboxDryRunPreExecutionCheckScore,
    PaperBrokerSandboxDryRunPreExecutionCheckSection,
    PaperBrokerSandboxDryRunPreExecutionCheckState,
)


def _coerce_input(
    data: PaperBrokerSandboxDryRunPreExecutionCheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunPreExecutionCheckInput:
    if isinstance(data, PaperBrokerSandboxDryRunPreExecutionCheckInput):
        return data
    allowed = {field.name for field in fields(PaperBrokerSandboxDryRunPreExecutionCheckInput)}
    payload = {key: value for key, value in dict(data).items() if key in allowed}
    return PaperBrokerSandboxDryRunPreExecutionCheckInput(**payload)


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


def _upstream_items(data: PaperBrokerSandboxDryRunPreExecutionCheckInput) -> tuple[Any, ...]:
    return (
        data.paper_broker_sandbox_dry_run_review,
        data.paper_broker_sandbox_dry_run_plan,
        data.paper_broker_sandbox_session_authorization_gate,
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


def _upstream_risks(data: PaperBrokerSandboxDryRunPreExecutionCheckInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperBrokerSandboxDryRunPreExecutionCheckInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _offline_boundary(data: PaperBrokerSandboxDryRunPreExecutionCheckInput) -> bool:
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
        and data.no_dry_run_execution is True
        and data.no_pre_execution is True
        and data.paper_broker_sandbox_dry_run_execution_requested is not True
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
            "DRY_RUN_EXECUTION",
            "PRE_EXECUTION",
            "API_KEY",
            "CREDENTIAL",
        )
    )


def _section(
    name: str,
    score: int,
    risk: PaperBrokerSandboxDryRunPreExecutionCheckRisk,
    failed: bool,
    evidence: tuple[str, ...] = (),
) -> PaperBrokerSandboxDryRunPreExecutionCheckSection:
    risks = (risk,) if failed or score < 85 else ()
    return PaperBrokerSandboxDryRunPreExecutionCheckSection(name, _clamp(score), not risks and score >= 85, risks, evidence)


def _verification_flag(
    data: PaperBrokerSandboxDryRunPreExecutionCheckInput,
    name: str,
    reviewed: bool | None,
    safe: bool | None,
    score: int | None,
    risk: PaperBrokerSandboxDryRunPreExecutionCheckRisk,
    upstream_needles: tuple[str, ...] = (),
    extra_ok: bool = True,
) -> PaperBrokerSandboxDryRunPreExecutionCheckSection:
    ok = _confirmed(reviewed, safe) and extra_ok
    failed = not ok or _has_upstream_risk(data, *upstream_needles)
    return _section(name, score if score is not None else _bool_score(ok), risk, failed)


def verify_dry_run_review_approval(
    data: PaperBrokerSandboxDryRunPreExecutionCheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunPreExecutionCheckSection:
    data = _coerce_input(data)
    review = data.paper_broker_sandbox_dry_run_review
    review_state_ok = _state_contains(
        review,
        "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION_CHECK",
        "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_REVIEW",
    )
    review_approved = (
        data.dry_run_review_approved is not False
        and data.dry_run_review_reviewed is not False
        and (data.dry_run_review_approved is True or review_state_ok)
    )
    failed = not review_approved or _has_upstream_risk(
        data,
        "DRY_RUN_REVIEW_NOT_APPROVED",
        "DRY_RUN_PLAN_NOT_APPROVED",
        "PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION",
        "BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN",
    )
    score = data.dry_run_review_approval_score if data.dry_run_review_approval_score is not None else _bool_score(review_approved)
    return _section(
        "dry_run_review_approval",
        score,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.DRY_RUN_REVIEW_NOT_APPROVED,
        failed,
        (_value(_get(review, "state")), _value(_get(review, "decision"))),
    )


def verify_pre_execution_scope(
    data: PaperBrokerSandboxDryRunPreExecutionCheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunPreExecutionCheckSection:
    data = _coerce_input(data)
    return _verification_flag(
        data,
        "pre_execution_scope",
        data.pre_execution_scope_reviewed,
        data.pre_execution_scope_clear,
        data.pre_execution_scope_score,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.PRE_EXECUTION_SCOPE_UNCLEAR,
        ("SCOPE",),
    )


def verify_pre_execution_boundaries(
    data: PaperBrokerSandboxDryRunPreExecutionCheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunPreExecutionCheckSection:
    data = _coerce_input(data)
    return _verification_flag(
        data,
        "pre_execution_boundaries",
        data.pre_execution_boundaries_reviewed,
        data.pre_execution_boundaries_complete,
        data.pre_execution_boundaries_score,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.PRE_EXECUTION_BOUNDARY_GAP,
        ("BOUNDARY", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK"),
        _offline_boundary(data),
    )


def verify_connection_pre_execution_safety(
    data: PaperBrokerSandboxDryRunPreExecutionCheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunPreExecutionCheckSection:
    data = _coerce_input(data)
    extra_ok = (
        data.no_http_transport is True
        and data.no_websocket_transport is True
        and data.no_socket_transport is True
        and data.no_external_api is True
    )
    return _verification_flag(
        data,
        "connection_pre_execution_safety",
        data.connection_pre_execution_safety_reviewed,
        data.connection_pre_execution_safe,
        data.connection_pre_execution_safety_score,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.CONNECTION_PRE_EXECUTION_SAFETY_GAP,
        ("CONNECTION", "NETWORK", "HTTP", "WEBSOCKET", "SOCKET", "API_ACCESS"),
        extra_ok,
    )


def verify_order_pre_execution_safety(
    data: PaperBrokerSandboxDryRunPreExecutionCheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunPreExecutionCheckSection:
    data = _coerce_input(data)
    extra_ok = data.no_real_order is True and data.no_live_execution is True
    return _verification_flag(
        data,
        "order_pre_execution_safety",
        data.order_pre_execution_safety_reviewed,
        data.order_pre_execution_safe,
        data.order_pre_execution_safety_score,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.ORDER_PRE_EXECUTION_SAFETY_GAP,
        ("ORDER", "EXECUTION_LEAK", "REAL_ORDER", "LIVE_EXECUTION"),
        extra_ok,
    )


def verify_position_pre_execution_safety(
    data: PaperBrokerSandboxDryRunPreExecutionCheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunPreExecutionCheckSection:
    data = _coerce_input(data)
    return _verification_flag(
        data,
        "position_pre_execution_safety",
        data.position_pre_execution_safety_reviewed,
        data.position_pre_execution_safe,
        data.position_pre_execution_safety_score,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.POSITION_PRE_EXECUTION_SAFETY_GAP,
        ("POSITION", "RECONCILIATION"),
    )


def verify_account_pre_execution_safety(
    data: PaperBrokerSandboxDryRunPreExecutionCheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunPreExecutionCheckSection:
    data = _coerce_input(data)
    extra_ok = data.no_api_key_read is True and data.no_real_account_access is True
    return _verification_flag(
        data,
        "account_pre_execution_safety",
        data.account_pre_execution_safety_reviewed,
        data.account_pre_execution_safe,
        data.account_pre_execution_safety_score,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.ACCOUNT_PRE_EXECUTION_SAFETY_GAP,
        ("ACCOUNT", "REAL_ACCOUNT", "CREDENTIAL", "API_KEY"),
        extra_ok,
    )


def verify_observability_pre_execution_safety(
    data: PaperBrokerSandboxDryRunPreExecutionCheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunPreExecutionCheckSection:
    data = _coerce_input(data)
    return _verification_flag(
        data,
        "observability_pre_execution_safety",
        data.observability_pre_execution_safety_reviewed,
        data.observability_pre_execution_safe,
        data.observability_pre_execution_safety_score,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.OBSERVABILITY_PRE_EXECUTION_GAP,
        ("OBSERVABILITY",),
    )


def verify_rollback_pre_execution_safety(
    data: PaperBrokerSandboxDryRunPreExecutionCheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunPreExecutionCheckSection:
    data = _coerce_input(data)
    return _verification_flag(
        data,
        "rollback_pre_execution_safety",
        data.rollback_pre_execution_safety_reviewed,
        data.rollback_pre_execution_safe,
        data.rollback_pre_execution_safety_score,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.ROLLBACK_PRE_EXECUTION_GAP,
        ("ROLLBACK",),
    )


def verify_kill_switch_pre_execution_safety(
    data: PaperBrokerSandboxDryRunPreExecutionCheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunPreExecutionCheckSection:
    data = _coerce_input(data)
    return _verification_flag(
        data,
        "kill_switch_pre_execution_safety",
        data.kill_switch_pre_execution_safety_reviewed,
        data.kill_switch_pre_execution_safe,
        data.kill_switch_pre_execution_safety_score,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.KILL_SWITCH_PRE_EXECUTION_GAP,
        ("KILL_SWITCH",),
    )


def verify_human_supervision_pre_execution_safety(
    data: PaperBrokerSandboxDryRunPreExecutionCheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunPreExecutionCheckSection:
    data = _coerce_input(data)
    return _verification_flag(
        data,
        "human_supervision_pre_execution_safety",
        data.human_supervision_pre_execution_safety_reviewed,
        data.human_supervision_pre_execution_safe,
        data.human_supervision_pre_execution_safety_score,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.HUMAN_SUPERVISION_PRE_EXECUTION_GAP,
        ("HUMAN", "SUPERVISION", "OPERATOR"),
    )


def verify_journal_pre_execution_safety(
    data: PaperBrokerSandboxDryRunPreExecutionCheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunPreExecutionCheckSection:
    data = _coerce_input(data)
    return _verification_flag(
        data,
        "journal_pre_execution_safety",
        data.journal_pre_execution_safety_reviewed,
        data.journal_pre_execution_safe,
        data.journal_pre_execution_safety_score,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.JOURNAL_PRE_EXECUTION_GAP,
        ("JOURNAL", "AUDIT_TRAIL", "TRACE"),
    )


def verify_stop_conditions_pre_execution_safety(
    data: PaperBrokerSandboxDryRunPreExecutionCheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunPreExecutionCheckSection:
    data = _coerce_input(data)
    return _verification_flag(
        data,
        "stop_conditions_pre_execution_safety",
        data.stop_conditions_pre_execution_safety_reviewed,
        data.stop_conditions_pre_execution_safe,
        data.stop_conditions_pre_execution_safety_score,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.STOP_CONDITIONS_PRE_EXECUTION_GAP,
        ("STOP_CONDITION", "HALT", "EMERGENCY_STOP"),
    )


def verify_success_failure_criteria_pre_execution_safety(
    data: PaperBrokerSandboxDryRunPreExecutionCheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunPreExecutionCheckSection:
    data = _coerce_input(data)
    return _verification_flag(
        data,
        "success_failure_criteria_pre_execution_safety",
        data.success_failure_criteria_pre_execution_safety_reviewed,
        data.success_failure_criteria_pre_execution_safe,
        data.success_failure_criteria_pre_execution_safety_score,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.SUCCESS_FAILURE_CRITERIA_PRE_EXECUTION_GAP,
        ("SUCCESS_CRITERIA", "FAILURE_CRITERIA"),
    )


def _all_sections(
    data: PaperBrokerSandboxDryRunPreExecutionCheckInput,
) -> tuple[PaperBrokerSandboxDryRunPreExecutionCheckSection, ...]:
    return (
        verify_dry_run_review_approval(data),
        verify_pre_execution_scope(data),
        verify_pre_execution_boundaries(data),
        verify_connection_pre_execution_safety(data),
        verify_order_pre_execution_safety(data),
        verify_position_pre_execution_safety(data),
        verify_account_pre_execution_safety(data),
        verify_observability_pre_execution_safety(data),
        verify_rollback_pre_execution_safety(data),
        verify_kill_switch_pre_execution_safety(data),
        verify_human_supervision_pre_execution_safety(data),
        verify_journal_pre_execution_safety(data),
        verify_stop_conditions_pre_execution_safety(data),
        verify_success_failure_criteria_pre_execution_safety(data),
    )


def detect_pre_execution_check_risks(
    data: PaperBrokerSandboxDryRunPreExecutionCheckInput | Mapping[str, Any],
    *sections: PaperBrokerSandboxDryRunPreExecutionCheckSection,
) -> tuple[PaperBrokerSandboxDryRunPreExecutionCheckRisk, ...]:
    data = _coerce_input(data)
    if not sections:
        sections = _all_sections(data)
    risks: list[PaperBrokerSandboxDryRunPreExecutionCheckRisk] = []
    for section in sections:
        risks.extend(section.risks)
    if (
        data.paper_broker_sandbox_dry_run_pre_execution_check_requested is not True
        or data.paper_broker_sandbox_dry_run_execution_requested is True
        or not _offline_boundary(data)
    ):
        risks.append(PaperBrokerSandboxDryRunPreExecutionCheckRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION)
    return _dedupe(risks)


def compute_pre_execution_check_score(
    data: PaperBrokerSandboxDryRunPreExecutionCheckInput | Mapping[str, Any],
    risks: tuple[PaperBrokerSandboxDryRunPreExecutionCheckRisk, ...] = (),
    *sections: PaperBrokerSandboxDryRunPreExecutionCheckSection,
) -> PaperBrokerSandboxDryRunPreExecutionCheckScore:
    data = _coerce_input(data)
    if not sections:
        sections = _all_sections(data)
    scores = tuple(section.score for section in sections)
    overall = _clamp(_average(scores) - min(70, len(set(risks)) * 5))
    for risk, cap in {
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.DRY_RUN_REVIEW_NOT_APPROVED: 50,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.PRE_EXECUTION_SCOPE_UNCLEAR: 60,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.PRE_EXECUTION_BOUNDARY_GAP: 45,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.CONNECTION_PRE_EXECUTION_SAFETY_GAP: 50,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.ORDER_PRE_EXECUTION_SAFETY_GAP: 50,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.POSITION_PRE_EXECUTION_SAFETY_GAP: 60,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.ACCOUNT_PRE_EXECUTION_SAFETY_GAP: 45,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.OBSERVABILITY_PRE_EXECUTION_GAP: 60,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.ROLLBACK_PRE_EXECUTION_GAP: 55,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.KILL_SWITCH_PRE_EXECUTION_GAP: 50,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.HUMAN_SUPERVISION_PRE_EXECUTION_GAP: 45,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.JOURNAL_PRE_EXECUTION_GAP: 60,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.STOP_CONDITIONS_PRE_EXECUTION_GAP: 45,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.SUCCESS_FAILURE_CRITERIA_PRE_EXECUTION_GAP: 50,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION: 40,
    }.items():
        if risk in risks:
            overall = min(overall, cap)
    return PaperBrokerSandboxDryRunPreExecutionCheckScore(overall, *scores)


def _select_decision(
    risks: tuple[PaperBrokerSandboxDryRunPreExecutionCheckRisk, ...],
    score: int,
) -> PaperBrokerSandboxDryRunPreExecutionCheckDecision:
    if PaperBrokerSandboxDryRunPreExecutionCheckRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION in risks or score < 45:
        return PaperBrokerSandboxDryRunPreExecutionCheckDecision.BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN
    if PaperBrokerSandboxDryRunPreExecutionCheckRisk.DRY_RUN_REVIEW_NOT_APPROVED in risks:
        return PaperBrokerSandboxDryRunPreExecutionCheckDecision.REQUIRE_DRY_RUN_REVIEW_FIXES
    if PaperBrokerSandboxDryRunPreExecutionCheckRisk.PRE_EXECUTION_SCOPE_UNCLEAR in risks:
        return PaperBrokerSandboxDryRunPreExecutionCheckDecision.REQUIRE_SCOPE_FIXES
    if PaperBrokerSandboxDryRunPreExecutionCheckRisk.PRE_EXECUTION_BOUNDARY_GAP in risks:
        return PaperBrokerSandboxDryRunPreExecutionCheckDecision.REQUIRE_BOUNDARY_FIXES
    if PaperBrokerSandboxDryRunPreExecutionCheckRisk.CONNECTION_PRE_EXECUTION_SAFETY_GAP in risks:
        return PaperBrokerSandboxDryRunPreExecutionCheckDecision.REQUIRE_CONNECTION_SAFETY_FIXES
    if PaperBrokerSandboxDryRunPreExecutionCheckRisk.ORDER_PRE_EXECUTION_SAFETY_GAP in risks:
        return PaperBrokerSandboxDryRunPreExecutionCheckDecision.REQUIRE_ORDER_SAFETY_FIXES
    if PaperBrokerSandboxDryRunPreExecutionCheckRisk.POSITION_PRE_EXECUTION_SAFETY_GAP in risks:
        return PaperBrokerSandboxDryRunPreExecutionCheckDecision.REQUIRE_POSITION_SAFETY_FIXES
    if PaperBrokerSandboxDryRunPreExecutionCheckRisk.ACCOUNT_PRE_EXECUTION_SAFETY_GAP in risks:
        return PaperBrokerSandboxDryRunPreExecutionCheckDecision.REQUIRE_ACCOUNT_SAFETY_FIXES
    if PaperBrokerSandboxDryRunPreExecutionCheckRisk.OBSERVABILITY_PRE_EXECUTION_GAP in risks:
        return PaperBrokerSandboxDryRunPreExecutionCheckDecision.REQUIRE_OBSERVABILITY_FIXES
    if PaperBrokerSandboxDryRunPreExecutionCheckRisk.ROLLBACK_PRE_EXECUTION_GAP in risks:
        return PaperBrokerSandboxDryRunPreExecutionCheckDecision.REQUIRE_ROLLBACK_FIXES
    if PaperBrokerSandboxDryRunPreExecutionCheckRisk.KILL_SWITCH_PRE_EXECUTION_GAP in risks:
        return PaperBrokerSandboxDryRunPreExecutionCheckDecision.REQUIRE_KILL_SWITCH_FIXES
    if PaperBrokerSandboxDryRunPreExecutionCheckRisk.HUMAN_SUPERVISION_PRE_EXECUTION_GAP in risks:
        return PaperBrokerSandboxDryRunPreExecutionCheckDecision.REQUIRE_SUPERVISION_FIXES
    if PaperBrokerSandboxDryRunPreExecutionCheckRisk.JOURNAL_PRE_EXECUTION_GAP in risks:
        return PaperBrokerSandboxDryRunPreExecutionCheckDecision.REQUIRE_JOURNAL_FIXES
    if (
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.STOP_CONDITIONS_PRE_EXECUTION_GAP in risks
        or PaperBrokerSandboxDryRunPreExecutionCheckRisk.SUCCESS_FAILURE_CRITERIA_PRE_EXECUTION_GAP in risks
    ):
        return PaperBrokerSandboxDryRunPreExecutionCheckDecision.REQUIRE_STOP_CONDITION_FIXES
    if risks:
        return PaperBrokerSandboxDryRunPreExecutionCheckDecision.REQUIRE_BOUNDARY_FIXES
    return PaperBrokerSandboxDryRunPreExecutionCheckDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION_CHECK


def _select_state(
    decision: PaperBrokerSandboxDryRunPreExecutionCheckDecision,
    score: int,
) -> PaperBrokerSandboxDryRunPreExecutionCheckState:
    if decision == PaperBrokerSandboxDryRunPreExecutionCheckDecision.BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN:
        return PaperBrokerSandboxDryRunPreExecutionCheckState.NOT_READY
    if decision != PaperBrokerSandboxDryRunPreExecutionCheckDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION_CHECK:
        return (
            PaperBrokerSandboxDryRunPreExecutionCheckState.PRE_EXECUTION_CHECK_REQUIRED
            if score < 82
            else PaperBrokerSandboxDryRunPreExecutionCheckState.PARTIALLY_READY
        )
    if score >= 95:
        return PaperBrokerSandboxDryRunPreExecutionCheckState.READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_REVIEW
    return PaperBrokerSandboxDryRunPreExecutionCheckState.PRE_EXECUTION_CHECK_READY


def generate_pre_execution_check_recommendations(
    risks: tuple[PaperBrokerSandboxDryRunPreExecutionCheckRisk, ...],
    decision: PaperBrokerSandboxDryRunPreExecutionCheckDecision | None = None,
) -> tuple[PaperBrokerSandboxDryRunPreExecutionCheckRecommendation, ...]:
    recommendations: list[PaperBrokerSandboxDryRunPreExecutionCheckRecommendation] = []
    if risks:
        recommendations.append(PaperBrokerSandboxDryRunPreExecutionCheckRecommendation.HOLD_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION)
    mapping = {
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.DRY_RUN_REVIEW_NOT_APPROVED: PaperBrokerSandboxDryRunPreExecutionCheckRecommendation.APPROVE_DRY_RUN_REVIEW_FIRST,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.PRE_EXECUTION_SCOPE_UNCLEAR: PaperBrokerSandboxDryRunPreExecutionCheckRecommendation.CLARIFY_PRE_EXECUTION_SCOPE,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.PRE_EXECUTION_BOUNDARY_GAP: PaperBrokerSandboxDryRunPreExecutionCheckRecommendation.COMPLETE_PRE_EXECUTION_BOUNDARIES,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.CONNECTION_PRE_EXECUTION_SAFETY_GAP: PaperBrokerSandboxDryRunPreExecutionCheckRecommendation.COMPLETE_CONNECTION_PRE_EXECUTION_SAFETY,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.ORDER_PRE_EXECUTION_SAFETY_GAP: PaperBrokerSandboxDryRunPreExecutionCheckRecommendation.COMPLETE_ORDER_PRE_EXECUTION_SAFETY,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.POSITION_PRE_EXECUTION_SAFETY_GAP: PaperBrokerSandboxDryRunPreExecutionCheckRecommendation.COMPLETE_POSITION_PRE_EXECUTION_SAFETY,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.ACCOUNT_PRE_EXECUTION_SAFETY_GAP: PaperBrokerSandboxDryRunPreExecutionCheckRecommendation.COMPLETE_ACCOUNT_PRE_EXECUTION_SAFETY,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.OBSERVABILITY_PRE_EXECUTION_GAP: PaperBrokerSandboxDryRunPreExecutionCheckRecommendation.COMPLETE_OBSERVABILITY_PRE_EXECUTION_SAFETY,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.ROLLBACK_PRE_EXECUTION_GAP: PaperBrokerSandboxDryRunPreExecutionCheckRecommendation.COMPLETE_ROLLBACK_PRE_EXECUTION_SAFETY,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.KILL_SWITCH_PRE_EXECUTION_GAP: PaperBrokerSandboxDryRunPreExecutionCheckRecommendation.COMPLETE_KILL_SWITCH_PRE_EXECUTION_SAFETY,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.HUMAN_SUPERVISION_PRE_EXECUTION_GAP: PaperBrokerSandboxDryRunPreExecutionCheckRecommendation.COMPLETE_HUMAN_SUPERVISION_PRE_EXECUTION_SAFETY,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.JOURNAL_PRE_EXECUTION_GAP: PaperBrokerSandboxDryRunPreExecutionCheckRecommendation.COMPLETE_JOURNAL_PRE_EXECUTION_SAFETY,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.STOP_CONDITIONS_PRE_EXECUTION_GAP: PaperBrokerSandboxDryRunPreExecutionCheckRecommendation.COMPLETE_STOP_CONDITIONS_PRE_EXECUTION_SAFETY,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.SUCCESS_FAILURE_CRITERIA_PRE_EXECUTION_GAP: PaperBrokerSandboxDryRunPreExecutionCheckRecommendation.COMPLETE_SUCCESS_FAILURE_CRITERIA_PRE_EXECUTION_SAFETY,
        PaperBrokerSandboxDryRunPreExecutionCheckRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION: PaperBrokerSandboxDryRunPreExecutionCheckRecommendation.DELAY_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(PaperBrokerSandboxDryRunPreExecutionCheckRecommendation.RUN_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION_CHECK_SUITE)
    if decision == PaperBrokerSandboxDryRunPreExecutionCheckDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION_CHECK:
        recommendations.append(PaperBrokerSandboxDryRunPreExecutionCheckRecommendation.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_REVIEW)
    return _dedupe(recommendations)


def evaluate_paper_broker_sandbox_dry_run_pre_execution_check(
    data: PaperBrokerSandboxDryRunPreExecutionCheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunPreExecutionCheckResult:
    data = _coerce_input(data)
    sections = _all_sections(data)
    risks = detect_pre_execution_check_risks(data, *sections)
    score = compute_pre_execution_check_score(data, risks, *sections)
    decision = _select_decision(risks, score.overall_score)
    state = _select_state(decision, score.overall_score)
    recommendations = generate_pre_execution_check_recommendations(risks, decision)
    offline_only = _offline_boundary(data)
    summary = f"{state.value}: decision={decision.value}, score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return PaperBrokerSandboxDryRunPreExecutionCheckResult(state, decision, score.overall_score, score, risks, *sections, recommendations, offline_only, summary)


def render_paper_broker_sandbox_dry_run_pre_execution_check_markdown(
    result: PaperBrokerSandboxDryRunPreExecutionCheckResult,
) -> str:
    lines = [
        "# AGIcore Paper Broker Sandbox Dry Run Pre-Execution Check",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Score: {result.check_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Paper Broker Sandbox Dry Run Pre-Execution Check Sections",
    ]
    sections = (
        result.dry_run_review_approval,
        result.pre_execution_scope,
        result.pre_execution_boundaries,
        result.connection_pre_execution_safety,
        result.order_pre_execution_safety,
        result.position_pre_execution_safety,
        result.account_pre_execution_safety,
        result.observability_pre_execution_safety,
        result.rollback_pre_execution_safety,
        result.kill_switch_pre_execution_safety,
        result.human_supervision_pre_execution_safety,
        result.journal_pre_execution_safety,
        result.stop_conditions_pre_execution_safety,
        result.success_failure_criteria_pre_execution_safety,
    )
    for section in sections:
        risks = ", ".join(risk.value for risk in section.risks) or "none"
        lines.append(f"- {section.name}: passed={section.passed}, score={section.score}/100, risks={risks}")
        lines.extend(f"  - {item}" for item in section.evidence if item)
    lines.append("")
    lines.append("# Paper Broker Sandbox Dry Run Pre-Execution Check Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Paper Broker Sandbox Dry Run Pre-Execution Check Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_pre_execution_check_score",
    "detect_pre_execution_check_risks",
    "evaluate_paper_broker_sandbox_dry_run_pre_execution_check",
    "generate_pre_execution_check_recommendations",
    "render_paper_broker_sandbox_dry_run_pre_execution_check_markdown",
    "verify_account_pre_execution_safety",
    "verify_connection_pre_execution_safety",
    "verify_dry_run_review_approval",
    "verify_human_supervision_pre_execution_safety",
    "verify_journal_pre_execution_safety",
    "verify_kill_switch_pre_execution_safety",
    "verify_observability_pre_execution_safety",
    "verify_order_pre_execution_safety",
    "verify_position_pre_execution_safety",
    "verify_pre_execution_boundaries",
    "verify_pre_execution_scope",
    "verify_rollback_pre_execution_safety",
    "verify_stop_conditions_pre_execution_safety",
    "verify_success_failure_criteria_pre_execution_safety",
]
