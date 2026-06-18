"""Offline review gate for a future AGIcore Paper Broker Sandbox Dry Run Pre-Execution Check."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_broker_sandbox_dry_run_review_models import (
    PaperBrokerSandboxDryRunReviewDecision,
    PaperBrokerSandboxDryRunReviewInput,
    PaperBrokerSandboxDryRunReviewRecommendation,
    PaperBrokerSandboxDryRunReviewResult,
    PaperBrokerSandboxDryRunReviewRisk,
    PaperBrokerSandboxDryRunReviewScore,
    PaperBrokerSandboxDryRunReviewSection,
    PaperBrokerSandboxDryRunReviewState,
)


def _coerce_input(data: PaperBrokerSandboxDryRunReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunReviewInput:
    if isinstance(data, PaperBrokerSandboxDryRunReviewInput):
        return data
    allowed = {field.name for field in fields(PaperBrokerSandboxDryRunReviewInput)}
    payload = {key: value for key, value in dict(data).items() if key in allowed}
    return PaperBrokerSandboxDryRunReviewInput(**payload)


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


def _upstream_items(data: PaperBrokerSandboxDryRunReviewInput) -> tuple[Any, ...]:
    return (
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


def _upstream_risks(data: PaperBrokerSandboxDryRunReviewInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperBrokerSandboxDryRunReviewInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _offline_boundary(data: PaperBrokerSandboxDryRunReviewInput) -> bool:
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
        and data.paper_broker_sandbox_dry_run_pre_execution_requested is not True
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
    risk: PaperBrokerSandboxDryRunReviewRisk,
    failed: bool,
    evidence: tuple[str, ...] = (),
) -> PaperBrokerSandboxDryRunReviewSection:
    risks = (risk,) if failed or score < 85 else ()
    return PaperBrokerSandboxDryRunReviewSection(name, _clamp(score), not risks and score >= 85, risks, evidence)


def _review_flag(
    data: PaperBrokerSandboxDryRunReviewInput,
    name: str,
    reviewed: bool | None,
    complete: bool | None,
    score: int | None,
    risk: PaperBrokerSandboxDryRunReviewRisk,
    upstream_needles: tuple[str, ...] = (),
    extra_ok: bool = True,
) -> PaperBrokerSandboxDryRunReviewSection:
    ok = _confirmed(reviewed, complete) and extra_ok
    failed = not ok or _has_upstream_risk(data, *upstream_needles)
    return _section(name, score if score is not None else _bool_score(ok), risk, failed)


def review_dry_run_plan_readiness(
    data: PaperBrokerSandboxDryRunReviewInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunReviewSection:
    data = _coerce_input(data)
    plan = data.paper_broker_sandbox_dry_run_plan
    plan_state_ok = _state_contains(
        plan,
        "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_REVIEW",
        "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_PLAN",
    )
    plan_approved = (
        data.dry_run_plan_approved is not False
        and data.dry_run_plan_reviewed is not False
        and (data.dry_run_plan_approved is True or plan_state_ok)
    )
    failed = not plan_approved or _has_upstream_risk(
        data,
        "DRY_RUN_PLAN_NOT_APPROVED",
        "AUTHORIZATION_GATE_NOT_APPROVED",
        "PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION",
        "BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN",
    )
    score = data.dry_run_plan_readiness_score if data.dry_run_plan_readiness_score is not None else _bool_score(plan_approved)
    return _section(
        "dry_run_plan_readiness",
        score,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_PLAN_NOT_APPROVED,
        failed,
        (_value(_get(plan, "state")), _value(_get(plan, "decision"))),
    )


def review_dry_run_scope(data: PaperBrokerSandboxDryRunReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunReviewSection:
    data = _coerce_input(data)
    return _review_flag(data, "dry_run_scope", data.dry_run_scope_reviewed, data.dry_run_scope_clear, data.dry_run_scope_score, PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_SCOPE_UNCLEAR, ("SCOPE",))


def review_dry_run_boundaries(data: PaperBrokerSandboxDryRunReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunReviewSection:
    data = _coerce_input(data)
    return _review_flag(data, "dry_run_boundaries", data.dry_run_boundaries_reviewed, data.dry_run_boundaries_complete, data.dry_run_boundaries_score, PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_BOUNDARY_INCOMPLETE, ("BOUNDARY", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK"), _offline_boundary(data))


def review_dry_run_scenario(data: PaperBrokerSandboxDryRunReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunReviewSection:
    data = _coerce_input(data)
    return _review_flag(data, "dry_run_scenario", data.dry_run_scenario_reviewed, data.dry_run_scenario_complete, data.dry_run_scenario_score, PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_SCENARIO_INCOMPLETE, ("SCENARIO",))


def review_dry_run_session_limits(data: PaperBrokerSandboxDryRunReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunReviewSection:
    data = _coerce_input(data)
    return _review_flag(data, "dry_run_session_limits", data.dry_run_session_limits_reviewed, data.dry_run_session_limits_complete, data.dry_run_session_limits_score, PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_SESSION_LIMIT_INCOMPLETE, ("LIMIT", "CAP"))


def review_dry_run_connection_policy(data: PaperBrokerSandboxDryRunReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunReviewSection:
    data = _coerce_input(data)
    extra_ok = data.no_http_transport is True and data.no_websocket_transport is True and data.no_socket_transport is True and data.no_external_api is True
    return _review_flag(data, "dry_run_connection_policy", data.dry_run_connection_policy_reviewed, data.dry_run_connection_policy_complete, data.dry_run_connection_policy_score, PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_CONNECTION_POLICY_INCOMPLETE, ("CONNECTION", "NETWORK", "HTTP", "WEBSOCKET", "SOCKET", "API_ACCESS"), extra_ok)


def review_dry_run_order_policy(data: PaperBrokerSandboxDryRunReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunReviewSection:
    data = _coerce_input(data)
    extra_ok = data.no_real_order is True and data.no_live_execution is True
    return _review_flag(data, "dry_run_order_policy", data.dry_run_order_policy_reviewed, data.dry_run_order_policy_complete, data.dry_run_order_policy_score, PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_ORDER_POLICY_INCOMPLETE, ("ORDER", "EXECUTION_LEAK", "REAL_ORDER", "LIVE_EXECUTION"), extra_ok)


def review_dry_run_position_policy(data: PaperBrokerSandboxDryRunReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunReviewSection:
    data = _coerce_input(data)
    return _review_flag(data, "dry_run_position_policy", data.dry_run_position_policy_reviewed, data.dry_run_position_policy_complete, data.dry_run_position_policy_score, PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_POSITION_POLICY_INCOMPLETE, ("POSITION", "RECONCILIATION"))


def review_dry_run_account_policy(data: PaperBrokerSandboxDryRunReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunReviewSection:
    data = _coerce_input(data)
    extra_ok = data.no_api_key_read is True and data.no_real_account_access is True
    return _review_flag(data, "dry_run_account_policy", data.dry_run_account_policy_reviewed, data.dry_run_account_policy_complete, data.dry_run_account_policy_score, PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_ACCOUNT_POLICY_INCOMPLETE, ("ACCOUNT", "REAL_ACCOUNT", "CREDENTIAL", "API_KEY"), extra_ok)


def review_dry_run_observability_policy(data: PaperBrokerSandboxDryRunReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunReviewSection:
    data = _coerce_input(data)
    return _review_flag(data, "dry_run_observability_policy", data.dry_run_observability_policy_reviewed, data.dry_run_observability_policy_complete, data.dry_run_observability_policy_score, PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_OBSERVABILITY_INCOMPLETE, ("OBSERVABILITY",))


def review_dry_run_rollback_policy(data: PaperBrokerSandboxDryRunReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunReviewSection:
    data = _coerce_input(data)
    return _review_flag(data, "dry_run_rollback_policy", data.dry_run_rollback_policy_reviewed, data.dry_run_rollback_policy_complete, data.dry_run_rollback_policy_score, PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_ROLLBACK_INCOMPLETE, ("ROLLBACK",))


def review_dry_run_kill_switch_policy(data: PaperBrokerSandboxDryRunReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunReviewSection:
    data = _coerce_input(data)
    return _review_flag(data, "dry_run_kill_switch_policy", data.dry_run_kill_switch_policy_reviewed, data.dry_run_kill_switch_policy_complete, data.dry_run_kill_switch_policy_score, PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_KILL_SWITCH_INCOMPLETE, ("KILL_SWITCH",))


def review_dry_run_human_supervision_policy(data: PaperBrokerSandboxDryRunReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunReviewSection:
    data = _coerce_input(data)
    return _review_flag(data, "dry_run_human_supervision_policy", data.dry_run_human_supervision_policy_reviewed, data.dry_run_human_supervision_policy_complete, data.dry_run_human_supervision_policy_score, PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_HUMAN_SUPERVISION_INCOMPLETE, ("HUMAN", "SUPERVISION", "OPERATOR"))


def review_dry_run_journal_policy(data: PaperBrokerSandboxDryRunReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunReviewSection:
    data = _coerce_input(data)
    return _review_flag(data, "dry_run_journal_policy", data.dry_run_journal_policy_reviewed, data.dry_run_journal_policy_complete, data.dry_run_journal_policy_score, PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_JOURNAL_INCOMPLETE, ("JOURNAL", "AUDIT_TRAIL", "TRACE"))


def review_dry_run_stop_conditions(data: PaperBrokerSandboxDryRunReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunReviewSection:
    data = _coerce_input(data)
    return _review_flag(data, "dry_run_stop_conditions", data.dry_run_stop_conditions_reviewed, data.dry_run_stop_conditions_complete, data.dry_run_stop_conditions_score, PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_STOP_CONDITION_INCOMPLETE, ("STOP_CONDITION", "HALT", "EMERGENCY_STOP"))


def review_dry_run_success_criteria(data: PaperBrokerSandboxDryRunReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunReviewSection:
    data = _coerce_input(data)
    return _review_flag(data, "dry_run_success_criteria", data.dry_run_success_criteria_reviewed, data.dry_run_success_criteria_complete, data.dry_run_success_criteria_score, PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_SUCCESS_CRITERIA_INCOMPLETE, ("SUCCESS_CRITERIA",))


def review_dry_run_failure_criteria(data: PaperBrokerSandboxDryRunReviewInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunReviewSection:
    data = _coerce_input(data)
    return _review_flag(data, "dry_run_failure_criteria", data.dry_run_failure_criteria_reviewed, data.dry_run_failure_criteria_complete, data.dry_run_failure_criteria_score, PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_FAILURE_CRITERIA_INCOMPLETE, ("FAILURE_CRITERIA",))


def _all_sections(data: PaperBrokerSandboxDryRunReviewInput) -> tuple[PaperBrokerSandboxDryRunReviewSection, ...]:
    return (
        review_dry_run_plan_readiness(data),
        review_dry_run_scope(data),
        review_dry_run_boundaries(data),
        review_dry_run_scenario(data),
        review_dry_run_session_limits(data),
        review_dry_run_connection_policy(data),
        review_dry_run_order_policy(data),
        review_dry_run_position_policy(data),
        review_dry_run_account_policy(data),
        review_dry_run_observability_policy(data),
        review_dry_run_rollback_policy(data),
        review_dry_run_kill_switch_policy(data),
        review_dry_run_human_supervision_policy(data),
        review_dry_run_journal_policy(data),
        review_dry_run_stop_conditions(data),
        review_dry_run_success_criteria(data),
        review_dry_run_failure_criteria(data),
    )


def detect_dry_run_review_risks(
    data: PaperBrokerSandboxDryRunReviewInput | Mapping[str, Any],
    *sections: PaperBrokerSandboxDryRunReviewSection,
) -> tuple[PaperBrokerSandboxDryRunReviewRisk, ...]:
    data = _coerce_input(data)
    if not sections:
        sections = _all_sections(data)
    risks: list[PaperBrokerSandboxDryRunReviewRisk] = []
    for section in sections:
        risks.extend(section.risks)
    if (
        data.paper_broker_sandbox_dry_run_review_requested is not True
        or data.paper_broker_sandbox_dry_run_pre_execution_requested is True
        or not _offline_boundary(data)
    ):
        risks.append(PaperBrokerSandboxDryRunReviewRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION)
    return _dedupe(risks)


def compute_dry_run_review_score(
    data: PaperBrokerSandboxDryRunReviewInput | Mapping[str, Any],
    risks: tuple[PaperBrokerSandboxDryRunReviewRisk, ...] = (),
    *sections: PaperBrokerSandboxDryRunReviewSection,
) -> PaperBrokerSandboxDryRunReviewScore:
    data = _coerce_input(data)
    if not sections:
        sections = _all_sections(data)
    scores = tuple(section.score for section in sections)
    overall = _clamp(_average(scores) - min(85, len(set(risks)) * 5))
    for risk, cap in {
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_PLAN_NOT_APPROVED: 50,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_SCOPE_UNCLEAR: 60,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_BOUNDARY_INCOMPLETE: 45,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_SCENARIO_INCOMPLETE: 60,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_SESSION_LIMIT_INCOMPLETE: 55,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_CONNECTION_POLICY_INCOMPLETE: 50,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_ORDER_POLICY_INCOMPLETE: 55,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_POSITION_POLICY_INCOMPLETE: 60,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_ACCOUNT_POLICY_INCOMPLETE: 50,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_OBSERVABILITY_INCOMPLETE: 60,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_ROLLBACK_INCOMPLETE: 55,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_KILL_SWITCH_INCOMPLETE: 50,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_HUMAN_SUPERVISION_INCOMPLETE: 45,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_JOURNAL_INCOMPLETE: 60,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_STOP_CONDITION_INCOMPLETE: 45,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_SUCCESS_CRITERIA_INCOMPLETE: 50,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_FAILURE_CRITERIA_INCOMPLETE: 50,
        PaperBrokerSandboxDryRunReviewRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION: 40,
    }.items():
        if risk in risks:
            overall = min(overall, cap)
    return PaperBrokerSandboxDryRunReviewScore(overall, *scores)


def _select_decision(
    risks: tuple[PaperBrokerSandboxDryRunReviewRisk, ...],
    score: int,
) -> PaperBrokerSandboxDryRunReviewDecision:
    if PaperBrokerSandboxDryRunReviewRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION in risks or score < 45:
        return PaperBrokerSandboxDryRunReviewDecision.BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN
    if PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_PLAN_NOT_APPROVED in risks:
        return PaperBrokerSandboxDryRunReviewDecision.REQUIRE_DRY_RUN_PLAN_FIXES
    if PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_SCOPE_UNCLEAR in risks:
        return PaperBrokerSandboxDryRunReviewDecision.REQUIRE_SCOPE_FIXES
    if PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_BOUNDARY_INCOMPLETE in risks:
        return PaperBrokerSandboxDryRunReviewDecision.REQUIRE_BOUNDARY_FIXES
    if PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_SCENARIO_INCOMPLETE in risks:
        return PaperBrokerSandboxDryRunReviewDecision.REQUIRE_SCENARIO_FIXES
    if PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_SESSION_LIMIT_INCOMPLETE in risks:
        return PaperBrokerSandboxDryRunReviewDecision.REQUIRE_SESSION_LIMIT_FIXES
    if PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_CONNECTION_POLICY_INCOMPLETE in risks:
        return PaperBrokerSandboxDryRunReviewDecision.REQUIRE_CONNECTION_POLICY_FIXES
    if PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_ORDER_POLICY_INCOMPLETE in risks:
        return PaperBrokerSandboxDryRunReviewDecision.REQUIRE_ORDER_POLICY_FIXES
    if PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_POSITION_POLICY_INCOMPLETE in risks:
        return PaperBrokerSandboxDryRunReviewDecision.REQUIRE_POSITION_POLICY_FIXES
    if PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_ACCOUNT_POLICY_INCOMPLETE in risks:
        return PaperBrokerSandboxDryRunReviewDecision.REQUIRE_ACCOUNT_POLICY_FIXES
    if PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_OBSERVABILITY_INCOMPLETE in risks:
        return PaperBrokerSandboxDryRunReviewDecision.REQUIRE_OBSERVABILITY_FIXES
    if PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_ROLLBACK_INCOMPLETE in risks:
        return PaperBrokerSandboxDryRunReviewDecision.REQUIRE_ROLLBACK_FIXES
    if PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_KILL_SWITCH_INCOMPLETE in risks:
        return PaperBrokerSandboxDryRunReviewDecision.REQUIRE_KILL_SWITCH_FIXES
    if PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_HUMAN_SUPERVISION_INCOMPLETE in risks:
        return PaperBrokerSandboxDryRunReviewDecision.REQUIRE_SUPERVISION_FIXES
    if PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_JOURNAL_INCOMPLETE in risks:
        return PaperBrokerSandboxDryRunReviewDecision.REQUIRE_JOURNAL_FIXES
    if (
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_STOP_CONDITION_INCOMPLETE in risks
        or PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_SUCCESS_CRITERIA_INCOMPLETE in risks
        or PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_FAILURE_CRITERIA_INCOMPLETE in risks
    ):
        return PaperBrokerSandboxDryRunReviewDecision.REQUIRE_STOP_CONDITION_FIXES
    if risks:
        return PaperBrokerSandboxDryRunReviewDecision.REQUIRE_BOUNDARY_FIXES
    return PaperBrokerSandboxDryRunReviewDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_REVIEW


def _select_state(
    decision: PaperBrokerSandboxDryRunReviewDecision,
    score: int,
) -> PaperBrokerSandboxDryRunReviewState:
    if decision == PaperBrokerSandboxDryRunReviewDecision.BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN:
        return PaperBrokerSandboxDryRunReviewState.NOT_READY
    if decision != PaperBrokerSandboxDryRunReviewDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_REVIEW:
        return PaperBrokerSandboxDryRunReviewState.DRY_RUN_REVIEW_REQUIRED if score < 82 else PaperBrokerSandboxDryRunReviewState.PARTIALLY_READY
    if score >= 95:
        return PaperBrokerSandboxDryRunReviewState.READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION_CHECK
    return PaperBrokerSandboxDryRunReviewState.DRY_RUN_REVIEW_READY


def generate_dry_run_review_recommendations(
    risks: tuple[PaperBrokerSandboxDryRunReviewRisk, ...],
    decision: PaperBrokerSandboxDryRunReviewDecision | None = None,
) -> tuple[PaperBrokerSandboxDryRunReviewRecommendation, ...]:
    recommendations: list[PaperBrokerSandboxDryRunReviewRecommendation] = []
    if risks:
        recommendations.append(PaperBrokerSandboxDryRunReviewRecommendation.HOLD_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION)
    mapping = {
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_PLAN_NOT_APPROVED: PaperBrokerSandboxDryRunReviewRecommendation.APPROVE_DRY_RUN_PLAN_FIRST,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_SCOPE_UNCLEAR: PaperBrokerSandboxDryRunReviewRecommendation.CLARIFY_DRY_RUN_SCOPE,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_BOUNDARY_INCOMPLETE: PaperBrokerSandboxDryRunReviewRecommendation.COMPLETE_DRY_RUN_BOUNDARIES,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_SCENARIO_INCOMPLETE: PaperBrokerSandboxDryRunReviewRecommendation.COMPLETE_DRY_RUN_SCENARIO,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_SESSION_LIMIT_INCOMPLETE: PaperBrokerSandboxDryRunReviewRecommendation.COMPLETE_DRY_RUN_SESSION_LIMITS,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_CONNECTION_POLICY_INCOMPLETE: PaperBrokerSandboxDryRunReviewRecommendation.COMPLETE_DRY_RUN_CONNECTION_POLICY,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_ORDER_POLICY_INCOMPLETE: PaperBrokerSandboxDryRunReviewRecommendation.COMPLETE_DRY_RUN_ORDER_POLICY,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_POSITION_POLICY_INCOMPLETE: PaperBrokerSandboxDryRunReviewRecommendation.COMPLETE_DRY_RUN_POSITION_POLICY,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_ACCOUNT_POLICY_INCOMPLETE: PaperBrokerSandboxDryRunReviewRecommendation.COMPLETE_DRY_RUN_ACCOUNT_POLICY,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_OBSERVABILITY_INCOMPLETE: PaperBrokerSandboxDryRunReviewRecommendation.COMPLETE_DRY_RUN_OBSERVABILITY_POLICY,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_ROLLBACK_INCOMPLETE: PaperBrokerSandboxDryRunReviewRecommendation.COMPLETE_DRY_RUN_ROLLBACK_POLICY,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_KILL_SWITCH_INCOMPLETE: PaperBrokerSandboxDryRunReviewRecommendation.COMPLETE_DRY_RUN_KILL_SWITCH_POLICY,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_HUMAN_SUPERVISION_INCOMPLETE: PaperBrokerSandboxDryRunReviewRecommendation.COMPLETE_DRY_RUN_HUMAN_SUPERVISION_POLICY,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_JOURNAL_INCOMPLETE: PaperBrokerSandboxDryRunReviewRecommendation.COMPLETE_DRY_RUN_JOURNAL_POLICY,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_STOP_CONDITION_INCOMPLETE: PaperBrokerSandboxDryRunReviewRecommendation.COMPLETE_DRY_RUN_STOP_CONDITIONS,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_SUCCESS_CRITERIA_INCOMPLETE: PaperBrokerSandboxDryRunReviewRecommendation.COMPLETE_DRY_RUN_SUCCESS_CRITERIA,
        PaperBrokerSandboxDryRunReviewRisk.DRY_RUN_FAILURE_CRITERIA_INCOMPLETE: PaperBrokerSandboxDryRunReviewRecommendation.COMPLETE_DRY_RUN_FAILURE_CRITERIA,
        PaperBrokerSandboxDryRunReviewRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION: PaperBrokerSandboxDryRunReviewRecommendation.DELAY_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(PaperBrokerSandboxDryRunReviewRecommendation.RUN_PAPER_BROKER_SANDBOX_DRY_RUN_REVIEW_SUITE)
    if decision == PaperBrokerSandboxDryRunReviewDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_REVIEW:
        recommendations.append(PaperBrokerSandboxDryRunReviewRecommendation.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION_CHECK)
    return _dedupe(recommendations)


def evaluate_paper_broker_sandbox_dry_run_review(
    data: PaperBrokerSandboxDryRunReviewInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunReviewResult:
    data = _coerce_input(data)
    sections = _all_sections(data)
    risks = detect_dry_run_review_risks(data, *sections)
    score = compute_dry_run_review_score(data, risks, *sections)
    decision = _select_decision(risks, score.overall_score)
    state = _select_state(decision, score.overall_score)
    recommendations = generate_dry_run_review_recommendations(risks, decision)
    offline_only = _offline_boundary(data)
    summary = f"{state.value}: decision={decision.value}, score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return PaperBrokerSandboxDryRunReviewResult(state, decision, score.overall_score, score, risks, *sections, recommendations, offline_only, summary)


def render_paper_broker_sandbox_dry_run_review_markdown(result: PaperBrokerSandboxDryRunReviewResult) -> str:
    lines = [
        "# AGIcore Paper Broker Sandbox Dry Run Review",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Score: {result.review_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Paper Broker Sandbox Dry Run Review Sections",
    ]
    sections = (
        result.dry_run_plan_readiness,
        result.dry_run_scope,
        result.dry_run_boundaries,
        result.dry_run_scenario,
        result.dry_run_session_limits,
        result.dry_run_connection_policy,
        result.dry_run_order_policy,
        result.dry_run_position_policy,
        result.dry_run_account_policy,
        result.dry_run_observability_policy,
        result.dry_run_rollback_policy,
        result.dry_run_kill_switch_policy,
        result.dry_run_human_supervision_policy,
        result.dry_run_journal_policy,
        result.dry_run_stop_conditions,
        result.dry_run_success_criteria,
        result.dry_run_failure_criteria,
    )
    for section in sections:
        risks = ", ".join(risk.value for risk in section.risks) or "none"
        lines.append(f"- {section.name}: passed={section.passed}, score={section.score}/100, risks={risks}")
        lines.extend(f"  - {item}" for item in section.evidence if item)
    lines.append("")
    lines.append("# Paper Broker Sandbox Dry Run Review Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Paper Broker Sandbox Dry Run Review Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_dry_run_review_score",
    "detect_dry_run_review_risks",
    "evaluate_paper_broker_sandbox_dry_run_review",
    "generate_dry_run_review_recommendations",
    "render_paper_broker_sandbox_dry_run_review_markdown",
    "review_dry_run_account_policy",
    "review_dry_run_boundaries",
    "review_dry_run_connection_policy",
    "review_dry_run_failure_criteria",
    "review_dry_run_human_supervision_policy",
    "review_dry_run_journal_policy",
    "review_dry_run_kill_switch_policy",
    "review_dry_run_observability_policy",
    "review_dry_run_order_policy",
    "review_dry_run_plan_readiness",
    "review_dry_run_position_policy",
    "review_dry_run_rollback_policy",
    "review_dry_run_scenario",
    "review_dry_run_scope",
    "review_dry_run_session_limits",
    "review_dry_run_stop_conditions",
    "review_dry_run_success_criteria",
]

