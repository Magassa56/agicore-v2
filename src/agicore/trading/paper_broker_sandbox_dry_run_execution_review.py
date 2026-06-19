"""Offline review before a future AGIcore Paper Broker Sandbox Dry Run execution authorization gate."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_broker_sandbox_dry_run_execution_review_models import (
    PaperBrokerSandboxDryRunExecutionReviewDecision,
    PaperBrokerSandboxDryRunExecutionReviewInput,
    PaperBrokerSandboxDryRunExecutionReviewRecommendation,
    PaperBrokerSandboxDryRunExecutionReviewResult,
    PaperBrokerSandboxDryRunExecutionReviewRisk,
    PaperBrokerSandboxDryRunExecutionReviewScore,
    PaperBrokerSandboxDryRunExecutionReviewSection,
    PaperBrokerSandboxDryRunExecutionReviewState,
)


def _coerce_input(
    data: PaperBrokerSandboxDryRunExecutionReviewInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunExecutionReviewInput:
    if isinstance(data, PaperBrokerSandboxDryRunExecutionReviewInput):
        return data
    allowed = {field.name for field in fields(PaperBrokerSandboxDryRunExecutionReviewInput)}
    payload = {key: value for key, value in dict(data).items() if key in allowed}
    return PaperBrokerSandboxDryRunExecutionReviewInput(**payload)


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


def _upstream_items(data: PaperBrokerSandboxDryRunExecutionReviewInput) -> tuple[Any, ...]:
    return (
        data.paper_broker_sandbox_dry_run_pre_execution_check,
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


def _upstream_risks(data: PaperBrokerSandboxDryRunExecutionReviewInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperBrokerSandboxDryRunExecutionReviewInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _offline_boundary(data: PaperBrokerSandboxDryRunExecutionReviewInput) -> bool:
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
        and data.no_dry_run_execution is True
        and data.no_real_execution is True
        and data.no_real_order is True
        and data.no_real_account_access is True
        and data.paper_broker_sandbox_dry_run_execution_requested is not True
        and data.paper_broker_sandbox_dry_run_real_execution_requested is not True
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
            "REAL_EXECUTION",
            "API_KEY",
            "CREDENTIAL",
        )
    )


def _section(
    name: str,
    score: int,
    risk: PaperBrokerSandboxDryRunExecutionReviewRisk,
    failed: bool,
    evidence: tuple[str, ...] = (),
) -> PaperBrokerSandboxDryRunExecutionReviewSection:
    risks = (risk,) if failed or score < 85 else ()
    return PaperBrokerSandboxDryRunExecutionReviewSection(name, _clamp(score), not risks and score >= 85, risks, evidence)


def _review_flag(
    data: PaperBrokerSandboxDryRunExecutionReviewInput,
    name: str,
    reviewed: bool | None,
    complete: bool | None,
    score: int | None,
    risk: PaperBrokerSandboxDryRunExecutionReviewRisk,
    upstream_needles: tuple[str, ...] = (),
    extra_ok: bool = True,
) -> PaperBrokerSandboxDryRunExecutionReviewSection:
    ok = _confirmed(reviewed, complete) and extra_ok
    failed = not ok or _has_upstream_risk(data, *upstream_needles)
    return _section(name, score if score is not None else _bool_score(ok), risk, failed)


def review_pre_execution_check_approval(
    data: PaperBrokerSandboxDryRunExecutionReviewInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunExecutionReviewSection:
    data = _coerce_input(data)
    check = data.paper_broker_sandbox_dry_run_pre_execution_check
    check_state_ok = _state_contains(
        check,
        "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_REVIEW",
        "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION_CHECK",
    )
    check_approved = (
        data.pre_execution_check_approved is not False
        and data.pre_execution_check_reviewed is not False
        and (data.pre_execution_check_approved is True or check_state_ok)
    )
    failed = not check_approved or _has_upstream_risk(
        data,
        "PRE_EXECUTION_CHECK_NOT_APPROVED",
        "DRY_RUN_REVIEW_NOT_APPROVED",
        "PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION",
        "BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN",
    )
    score = data.pre_execution_check_approval_score if data.pre_execution_check_approval_score is not None else _bool_score(check_approved)
    return _section(
        "pre_execution_check_approval",
        score,
        PaperBrokerSandboxDryRunExecutionReviewRisk.PRE_EXECUTION_CHECK_NOT_APPROVED,
        failed,
        (_value(_get(check, "state")), _value(_get(check, "decision"))),
    )


def review_execution_scope(data: PaperBrokerSandboxDryRunExecutionReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunExecutionReviewSection:
    data = _coerce_input(data)
    return _review_flag(data, "execution_scope", data.execution_scope_reviewed, data.execution_scope_clear, data.execution_scope_score, PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_SCOPE_UNCLEAR, ("SCOPE",))


def review_execution_boundaries(data: PaperBrokerSandboxDryRunExecutionReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunExecutionReviewSection:
    data = _coerce_input(data)
    return _review_flag(data, "execution_boundaries", data.execution_boundaries_reviewed, data.execution_boundaries_complete, data.execution_boundaries_score, PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_BOUNDARY_GAP, ("BOUNDARY", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK"), _offline_boundary(data))


def review_execution_scenario(data: PaperBrokerSandboxDryRunExecutionReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunExecutionReviewSection:
    data = _coerce_input(data)
    return _review_flag(data, "execution_scenario", data.execution_scenario_reviewed, data.execution_scenario_complete, data.execution_scenario_score, PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_SCENARIO_GAP, ("SCENARIO",))


def review_execution_session_limits(data: PaperBrokerSandboxDryRunExecutionReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunExecutionReviewSection:
    data = _coerce_input(data)
    return _review_flag(data, "execution_session_limits", data.execution_session_limits_reviewed, data.execution_session_limits_complete, data.execution_session_limits_score, PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_SESSION_LIMIT_GAP, ("LIMIT", "CAP"))


def review_execution_connection_control(data: PaperBrokerSandboxDryRunExecutionReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunExecutionReviewSection:
    data = _coerce_input(data)
    extra_ok = data.no_http_transport is True and data.no_websocket_transport is True and data.no_socket_transport is True and data.no_external_api is True
    return _review_flag(data, "execution_connection_control", data.execution_connection_control_reviewed, data.execution_connection_control_complete, data.execution_connection_control_score, PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_CONNECTION_CONTROL_GAP, ("CONNECTION", "NETWORK", "HTTP", "WEBSOCKET", "SOCKET", "API_ACCESS"), extra_ok)


def review_execution_order_control(data: PaperBrokerSandboxDryRunExecutionReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunExecutionReviewSection:
    data = _coerce_input(data)
    extra_ok = data.no_real_order is True and data.no_live_execution is True and data.no_real_execution is True
    return _review_flag(data, "execution_order_control", data.execution_order_control_reviewed, data.execution_order_control_complete, data.execution_order_control_score, PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_ORDER_CONTROL_GAP, ("ORDER", "EXECUTION_LEAK", "REAL_ORDER", "LIVE_EXECUTION"), extra_ok)


def review_execution_position_control(data: PaperBrokerSandboxDryRunExecutionReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunExecutionReviewSection:
    data = _coerce_input(data)
    return _review_flag(data, "execution_position_control", data.execution_position_control_reviewed, data.execution_position_control_complete, data.execution_position_control_score, PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_POSITION_CONTROL_GAP, ("POSITION", "RECONCILIATION"))


def review_execution_account_control(data: PaperBrokerSandboxDryRunExecutionReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunExecutionReviewSection:
    data = _coerce_input(data)
    extra_ok = data.no_api_key_read is True and data.no_real_account_access is True
    return _review_flag(data, "execution_account_control", data.execution_account_control_reviewed, data.execution_account_control_complete, data.execution_account_control_score, PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_ACCOUNT_CONTROL_GAP, ("ACCOUNT", "REAL_ACCOUNT", "CREDENTIAL", "API_KEY"), extra_ok)


def review_execution_observability_control(data: PaperBrokerSandboxDryRunExecutionReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunExecutionReviewSection:
    data = _coerce_input(data)
    return _review_flag(data, "execution_observability_control", data.execution_observability_control_reviewed, data.execution_observability_control_complete, data.execution_observability_control_score, PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_OBSERVABILITY_GAP, ("OBSERVABILITY",))


def review_execution_rollback_control(data: PaperBrokerSandboxDryRunExecutionReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunExecutionReviewSection:
    data = _coerce_input(data)
    return _review_flag(data, "execution_rollback_control", data.execution_rollback_control_reviewed, data.execution_rollback_control_complete, data.execution_rollback_control_score, PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_ROLLBACK_GAP, ("ROLLBACK",))


def review_execution_kill_switch_control(data: PaperBrokerSandboxDryRunExecutionReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunExecutionReviewSection:
    data = _coerce_input(data)
    return _review_flag(data, "execution_kill_switch_control", data.execution_kill_switch_control_reviewed, data.execution_kill_switch_control_complete, data.execution_kill_switch_control_score, PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_KILL_SWITCH_GAP, ("KILL_SWITCH",))


def review_execution_human_supervision_control(data: PaperBrokerSandboxDryRunExecutionReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunExecutionReviewSection:
    data = _coerce_input(data)
    return _review_flag(data, "execution_human_supervision_control", data.execution_human_supervision_control_reviewed, data.execution_human_supervision_control_complete, data.execution_human_supervision_control_score, PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_HUMAN_SUPERVISION_GAP, ("HUMAN", "SUPERVISION", "OPERATOR"))


def review_execution_journal_control(data: PaperBrokerSandboxDryRunExecutionReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunExecutionReviewSection:
    data = _coerce_input(data)
    return _review_flag(data, "execution_journal_control", data.execution_journal_control_reviewed, data.execution_journal_control_complete, data.execution_journal_control_score, PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_JOURNAL_GAP, ("JOURNAL", "AUDIT_TRAIL", "TRACE"))


def review_execution_stop_conditions(data: PaperBrokerSandboxDryRunExecutionReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunExecutionReviewSection:
    data = _coerce_input(data)
    return _review_flag(data, "execution_stop_conditions", data.execution_stop_conditions_reviewed, data.execution_stop_conditions_complete, data.execution_stop_conditions_score, PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_STOP_CONDITION_GAP, ("STOP_CONDITION", "HALT", "EMERGENCY_STOP"))


def review_execution_success_failure_criteria(data: PaperBrokerSandboxDryRunExecutionReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunExecutionReviewSection:
    data = _coerce_input(data)
    return _review_flag(data, "execution_success_failure_criteria", data.execution_success_failure_criteria_reviewed, data.execution_success_failure_criteria_complete, data.execution_success_failure_criteria_score, PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_SUCCESS_FAILURE_CRITERIA_GAP, ("SUCCESS_CRITERIA", "FAILURE_CRITERIA"))


def review_execution_abort_conditions(data: PaperBrokerSandboxDryRunExecutionReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunExecutionReviewSection:
    data = _coerce_input(data)
    return _review_flag(data, "execution_abort_conditions", data.execution_abort_conditions_reviewed, data.execution_abort_conditions_complete, data.execution_abort_conditions_score, PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_ABORT_CONDITION_GAP, ("ABORT", "CANCEL", "EMERGENCY_ABORT"))


def _all_sections(data: PaperBrokerSandboxDryRunExecutionReviewInput) -> tuple[PaperBrokerSandboxDryRunExecutionReviewSection, ...]:
    return (
        review_pre_execution_check_approval(data),
        review_execution_scope(data),
        review_execution_boundaries(data),
        review_execution_scenario(data),
        review_execution_session_limits(data),
        review_execution_connection_control(data),
        review_execution_order_control(data),
        review_execution_position_control(data),
        review_execution_account_control(data),
        review_execution_observability_control(data),
        review_execution_rollback_control(data),
        review_execution_kill_switch_control(data),
        review_execution_human_supervision_control(data),
        review_execution_journal_control(data),
        review_execution_stop_conditions(data),
        review_execution_success_failure_criteria(data),
        review_execution_abort_conditions(data),
    )


def detect_execution_review_risks(
    data: PaperBrokerSandboxDryRunExecutionReviewInput | Mapping[str, Any],
    *sections: PaperBrokerSandboxDryRunExecutionReviewSection,
) -> tuple[PaperBrokerSandboxDryRunExecutionReviewRisk, ...]:
    data = _coerce_input(data)
    if not sections:
        sections = _all_sections(data)
    risks: list[PaperBrokerSandboxDryRunExecutionReviewRisk] = []
    for section in sections:
        risks.extend(section.risks)
    if (
        data.paper_broker_sandbox_dry_run_execution_review_requested is not True
        or data.paper_broker_sandbox_dry_run_execution_requested is True
        or data.paper_broker_sandbox_dry_run_real_execution_requested is True
        or not _offline_boundary(data)
    ):
        risks.append(PaperBrokerSandboxDryRunExecutionReviewRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_REAL_EXECUTION)
    return _dedupe(risks)


def compute_execution_review_score(
    data: PaperBrokerSandboxDryRunExecutionReviewInput | Mapping[str, Any],
    risks: tuple[PaperBrokerSandboxDryRunExecutionReviewRisk, ...] = (),
    *sections: PaperBrokerSandboxDryRunExecutionReviewSection,
) -> PaperBrokerSandboxDryRunExecutionReviewScore:
    data = _coerce_input(data)
    if not sections:
        sections = _all_sections(data)
    scores = tuple(section.score for section in sections)
    overall = _clamp(_average(scores) - min(85, len(set(risks)) * 5))
    for risk, cap in {
        PaperBrokerSandboxDryRunExecutionReviewRisk.PRE_EXECUTION_CHECK_NOT_APPROVED: 50,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_SCOPE_UNCLEAR: 60,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_BOUNDARY_GAP: 45,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_SCENARIO_GAP: 60,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_SESSION_LIMIT_GAP: 55,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_CONNECTION_CONTROL_GAP: 50,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_ORDER_CONTROL_GAP: 50,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_POSITION_CONTROL_GAP: 60,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_ACCOUNT_CONTROL_GAP: 45,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_OBSERVABILITY_GAP: 60,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_ROLLBACK_GAP: 55,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_KILL_SWITCH_GAP: 50,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_HUMAN_SUPERVISION_GAP: 45,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_JOURNAL_GAP: 60,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_STOP_CONDITION_GAP: 45,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_SUCCESS_FAILURE_CRITERIA_GAP: 50,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_ABORT_CONDITION_GAP: 45,
        PaperBrokerSandboxDryRunExecutionReviewRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_REAL_EXECUTION: 40,
    }.items():
        if risk in risks:
            overall = min(overall, cap)
    return PaperBrokerSandboxDryRunExecutionReviewScore(overall, *scores)


def _select_decision(
    risks: tuple[PaperBrokerSandboxDryRunExecutionReviewRisk, ...],
    score: int,
) -> PaperBrokerSandboxDryRunExecutionReviewDecision:
    if PaperBrokerSandboxDryRunExecutionReviewRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_REAL_EXECUTION in risks or score < 45:
        return PaperBrokerSandboxDryRunExecutionReviewDecision.BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION
    if PaperBrokerSandboxDryRunExecutionReviewRisk.PRE_EXECUTION_CHECK_NOT_APPROVED in risks:
        return PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_PRE_EXECUTION_CHECK_FIXES
    if PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_SCOPE_UNCLEAR in risks:
        return PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_SCOPE_FIXES
    if PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_BOUNDARY_GAP in risks:
        return PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_BOUNDARY_FIXES
    if PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_SCENARIO_GAP in risks:
        return PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_SCENARIO_FIXES
    if PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_SESSION_LIMIT_GAP in risks:
        return PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_SESSION_LIMIT_FIXES
    if PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_CONNECTION_CONTROL_GAP in risks:
        return PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_CONNECTION_CONTROL_FIXES
    if PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_ORDER_CONTROL_GAP in risks:
        return PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_ORDER_CONTROL_FIXES
    if PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_POSITION_CONTROL_GAP in risks:
        return PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_POSITION_CONTROL_FIXES
    if PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_ACCOUNT_CONTROL_GAP in risks:
        return PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_ACCOUNT_CONTROL_FIXES
    if PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_OBSERVABILITY_GAP in risks:
        return PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_OBSERVABILITY_FIXES
    if PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_ROLLBACK_GAP in risks:
        return PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_ROLLBACK_FIXES
    if PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_KILL_SWITCH_GAP in risks:
        return PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_KILL_SWITCH_FIXES
    if PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_HUMAN_SUPERVISION_GAP in risks:
        return PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_SUPERVISION_FIXES
    if PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_JOURNAL_GAP in risks:
        return PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_JOURNAL_FIXES
    if (
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_STOP_CONDITION_GAP in risks
        or PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_SUCCESS_FAILURE_CRITERIA_GAP in risks
    ):
        return PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_STOP_CONDITION_FIXES
    if PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_ABORT_CONDITION_GAP in risks:
        return PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_ABORT_CONDITION_FIXES
    if risks:
        return PaperBrokerSandboxDryRunExecutionReviewDecision.REQUIRE_BOUNDARY_FIXES
    return PaperBrokerSandboxDryRunExecutionReviewDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_REVIEW


def _select_state(
    decision: PaperBrokerSandboxDryRunExecutionReviewDecision,
    score: int,
) -> PaperBrokerSandboxDryRunExecutionReviewState:
    if decision == PaperBrokerSandboxDryRunExecutionReviewDecision.BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION:
        return PaperBrokerSandboxDryRunExecutionReviewState.NOT_READY
    if decision != PaperBrokerSandboxDryRunExecutionReviewDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_REVIEW:
        return PaperBrokerSandboxDryRunExecutionReviewState.EXECUTION_REVIEW_REQUIRED if score < 82 else PaperBrokerSandboxDryRunExecutionReviewState.PARTIALLY_READY
    if score >= 95:
        return PaperBrokerSandboxDryRunExecutionReviewState.READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION_GATE
    return PaperBrokerSandboxDryRunExecutionReviewState.DRY_RUN_EXECUTION_REVIEW_READY


def generate_execution_review_recommendations(
    risks: tuple[PaperBrokerSandboxDryRunExecutionReviewRisk, ...],
    decision: PaperBrokerSandboxDryRunExecutionReviewDecision | None = None,
) -> tuple[PaperBrokerSandboxDryRunExecutionReviewRecommendation, ...]:
    recommendations: list[PaperBrokerSandboxDryRunExecutionReviewRecommendation] = []
    if risks:
        recommendations.append(PaperBrokerSandboxDryRunExecutionReviewRecommendation.HOLD_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION)
    mapping = {
        PaperBrokerSandboxDryRunExecutionReviewRisk.PRE_EXECUTION_CHECK_NOT_APPROVED: PaperBrokerSandboxDryRunExecutionReviewRecommendation.APPROVE_PRE_EXECUTION_CHECK_FIRST,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_SCOPE_UNCLEAR: PaperBrokerSandboxDryRunExecutionReviewRecommendation.CLARIFY_EXECUTION_SCOPE,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_BOUNDARY_GAP: PaperBrokerSandboxDryRunExecutionReviewRecommendation.COMPLETE_EXECUTION_BOUNDARIES,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_SCENARIO_GAP: PaperBrokerSandboxDryRunExecutionReviewRecommendation.COMPLETE_EXECUTION_SCENARIO,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_SESSION_LIMIT_GAP: PaperBrokerSandboxDryRunExecutionReviewRecommendation.COMPLETE_EXECUTION_SESSION_LIMITS,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_CONNECTION_CONTROL_GAP: PaperBrokerSandboxDryRunExecutionReviewRecommendation.COMPLETE_EXECUTION_CONNECTION_CONTROL,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_ORDER_CONTROL_GAP: PaperBrokerSandboxDryRunExecutionReviewRecommendation.COMPLETE_EXECUTION_ORDER_CONTROL,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_POSITION_CONTROL_GAP: PaperBrokerSandboxDryRunExecutionReviewRecommendation.COMPLETE_EXECUTION_POSITION_CONTROL,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_ACCOUNT_CONTROL_GAP: PaperBrokerSandboxDryRunExecutionReviewRecommendation.COMPLETE_EXECUTION_ACCOUNT_CONTROL,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_OBSERVABILITY_GAP: PaperBrokerSandboxDryRunExecutionReviewRecommendation.COMPLETE_EXECUTION_OBSERVABILITY_CONTROL,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_ROLLBACK_GAP: PaperBrokerSandboxDryRunExecutionReviewRecommendation.COMPLETE_EXECUTION_ROLLBACK_CONTROL,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_KILL_SWITCH_GAP: PaperBrokerSandboxDryRunExecutionReviewRecommendation.COMPLETE_EXECUTION_KILL_SWITCH_CONTROL,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_HUMAN_SUPERVISION_GAP: PaperBrokerSandboxDryRunExecutionReviewRecommendation.COMPLETE_EXECUTION_HUMAN_SUPERVISION_CONTROL,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_JOURNAL_GAP: PaperBrokerSandboxDryRunExecutionReviewRecommendation.COMPLETE_EXECUTION_JOURNAL_CONTROL,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_STOP_CONDITION_GAP: PaperBrokerSandboxDryRunExecutionReviewRecommendation.COMPLETE_EXECUTION_STOP_CONDITIONS,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_SUCCESS_FAILURE_CRITERIA_GAP: PaperBrokerSandboxDryRunExecutionReviewRecommendation.COMPLETE_EXECUTION_SUCCESS_FAILURE_CRITERIA,
        PaperBrokerSandboxDryRunExecutionReviewRisk.EXECUTION_ABORT_CONDITION_GAP: PaperBrokerSandboxDryRunExecutionReviewRecommendation.COMPLETE_EXECUTION_ABORT_CONDITIONS,
        PaperBrokerSandboxDryRunExecutionReviewRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_REAL_EXECUTION: PaperBrokerSandboxDryRunExecutionReviewRecommendation.DELAY_PAPER_BROKER_SANDBOX_DRY_RUN_REAL_EXECUTION,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(PaperBrokerSandboxDryRunExecutionReviewRecommendation.RUN_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_REVIEW_SUITE)
    if decision == PaperBrokerSandboxDryRunExecutionReviewDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_REVIEW:
        recommendations.append(PaperBrokerSandboxDryRunExecutionReviewRecommendation.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION_GATE)
    return _dedupe(recommendations)


def evaluate_paper_broker_sandbox_dry_run_execution_review(
    data: PaperBrokerSandboxDryRunExecutionReviewInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunExecutionReviewResult:
    data = _coerce_input(data)
    sections = _all_sections(data)
    risks = detect_execution_review_risks(data, *sections)
    score = compute_execution_review_score(data, risks, *sections)
    decision = _select_decision(risks, score.overall_score)
    state = _select_state(decision, score.overall_score)
    recommendations = generate_execution_review_recommendations(risks, decision)
    offline_only = _offline_boundary(data)
    summary = f"{state.value}: decision={decision.value}, score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return PaperBrokerSandboxDryRunExecutionReviewResult(state, decision, score.overall_score, score, risks, *sections, recommendations, offline_only, summary)


def render_paper_broker_sandbox_dry_run_execution_review_markdown(result: PaperBrokerSandboxDryRunExecutionReviewResult) -> str:
    lines = [
        "# AGIcore Paper Broker Sandbox Dry Run Execution Review",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Score: {result.review_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Paper Broker Sandbox Dry Run Execution Review Sections",
    ]
    sections = (
        result.pre_execution_check_approval,
        result.execution_scope,
        result.execution_boundaries,
        result.execution_scenario,
        result.execution_session_limits,
        result.execution_connection_control,
        result.execution_order_control,
        result.execution_position_control,
        result.execution_account_control,
        result.execution_observability_control,
        result.execution_rollback_control,
        result.execution_kill_switch_control,
        result.execution_human_supervision_control,
        result.execution_journal_control,
        result.execution_stop_conditions,
        result.execution_success_failure_criteria,
        result.execution_abort_conditions,
    )
    for section in sections:
        risks = ", ".join(risk.value for risk in section.risks) or "none"
        lines.append(f"- {section.name}: passed={section.passed}, score={section.score}/100, risks={risks}")
        lines.extend(f"  - {item}" for item in section.evidence if item)
    lines.append("")
    lines.append("# Paper Broker Sandbox Dry Run Execution Review Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Paper Broker Sandbox Dry Run Execution Review Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_execution_review_score",
    "detect_execution_review_risks",
    "evaluate_paper_broker_sandbox_dry_run_execution_review",
    "generate_execution_review_recommendations",
    "render_paper_broker_sandbox_dry_run_execution_review_markdown",
    "review_execution_abort_conditions",
    "review_execution_account_control",
    "review_execution_boundaries",
    "review_execution_connection_control",
    "review_execution_human_supervision_control",
    "review_execution_journal_control",
    "review_execution_kill_switch_control",
    "review_execution_observability_control",
    "review_execution_order_control",
    "review_execution_position_control",
    "review_execution_rollback_control",
    "review_execution_scenario",
    "review_execution_scope",
    "review_execution_session_limits",
    "review_execution_stop_conditions",
    "review_execution_success_failure_criteria",
    "review_pre_execution_check_approval",
]
