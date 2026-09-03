"""Offline review + pre-execution check for a controlled simulation runner."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_broker_sandbox_controlled_simulation_review_precheck_models import (
    PaperBrokerSandboxControlledSimulationReviewPrecheckDecision,
    PaperBrokerSandboxControlledSimulationReviewPrecheckInput,
    PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation,
    PaperBrokerSandboxControlledSimulationReviewPrecheckResult,
    PaperBrokerSandboxControlledSimulationReviewPrecheckRisk,
    PaperBrokerSandboxControlledSimulationReviewPrecheckScore,
    PaperBrokerSandboxControlledSimulationReviewPrecheckSection,
    PaperBrokerSandboxControlledSimulationReviewPrecheckState,
)


def _coerce_input(
    data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxControlledSimulationReviewPrecheckInput:
    if isinstance(data, PaperBrokerSandboxControlledSimulationReviewPrecheckInput):
        return data
    allowed = {field.name for field in fields(PaperBrokerSandboxControlledSimulationReviewPrecheckInput)}
    payload = {key: value for key, value in dict(data).items() if key in allowed}
    return PaperBrokerSandboxControlledSimulationReviewPrecheckInput(**payload)


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


def _upstream_items(data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput) -> tuple[Any, ...]:
    return (
        data.paper_broker_sandbox_dry_run_controlled_simulation_plan,
        data.paper_broker_sandbox_dry_run_execution_authorization_gate,
        data.paper_broker_sandbox_dry_run_execution_review,
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
        data.observability_verification,
        data.rollback_verification,
        data.kill_switch_verification,
        data.human_validated_paper_session,
        data.supervised_paper_session,
    )


def _upstream_risks(data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(
    data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput,
    *needles: str,
) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _no_real_execution(data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput) -> bool:
    return (
        data.no_live_execution is True
        and data.no_dry_run_execution is True
        and data.no_controlled_simulation_execution is True
        and data.no_real_order is True
        and data.no_real_account_access is True
        and data.controlled_simulation_offline_runner_requested is not True
        and data.controlled_simulation_real_execution_requested is not True
        and data.controlled_simulation_execution_requested is not True
        and not _has_upstream_risk(
            data,
            "LIVE_EXECUTION",
            "DRY_RUN_EXECUTION",
            "REAL_EXECUTION",
            "REAL_ORDER",
            "REAL_ACCOUNT",
            "CONTROLLED_SIMULATION_EXECUTION",
            "SIMULATION_EXECUTION",
        )
    )


def _offline_boundary(data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput) -> bool:
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
        and _no_real_execution(data)
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
            "CONTROLLED_SIMULATION_EXECUTION",
            "OFFLINE_RUNNER",
            "API_KEY",
            "CREDENTIAL",
        )
    )


def _section(
    name: str,
    score: int,
    risk: PaperBrokerSandboxControlledSimulationReviewPrecheckRisk,
    failed: bool,
    evidence: tuple[str, ...] = (),
) -> PaperBrokerSandboxControlledSimulationReviewPrecheckSection:
    risks = (risk,) if failed or score < 85 else ()
    return PaperBrokerSandboxControlledSimulationReviewPrecheckSection(name, _clamp(score), not risks and score >= 85, risks, evidence)


def _review_flag(
    data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput,
    name: str,
    reviewed: bool | None,
    complete: bool | None,
    score: int | None,
    risk: PaperBrokerSandboxControlledSimulationReviewPrecheckRisk,
    upstream_needles: tuple[str, ...] = (),
    extra_ok: bool = True,
) -> PaperBrokerSandboxControlledSimulationReviewPrecheckSection:
    ok = _confirmed(reviewed, complete) and extra_ok
    failed = not ok or _has_upstream_risk(data, *upstream_needles)
    return _section(name, score if score is not None else _bool_score(ok), risk, failed)


def review_controlled_simulation_plan_readiness(
    data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxControlledSimulationReviewPrecheckSection:
    data = _coerce_input(data)
    plan = data.paper_broker_sandbox_dry_run_controlled_simulation_plan
    plan_state_ok = _state_contains(
        plan,
        "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_REVIEW",
        "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_PLAN",
    )
    plan_approved = (
        data.controlled_simulation_plan_approved is not False
        and data.controlled_simulation_plan_reviewed is not False
        and (data.controlled_simulation_plan_approved is True or plan_state_ok)
    )
    failed = not plan_approved or _has_upstream_risk(
        data,
        "EXECUTION_AUTHORIZATION_GATE_NOT_APPROVED",
        "CONTROLLED_SIMULATION_PLAN_NOT_APPROVED",
        "PREMATURE_PAPER_BROKER_SANDBOX_CONTROLLED_SIMULATION_EXECUTION",
        "BLOCK_PAPER_BROKER_SANDBOX_CONTROLLED_SIMULATION",
    )
    score = data.controlled_simulation_plan_readiness_score
    return _section(
        "controlled_simulation_plan_readiness",
        score if score is not None else _bool_score(plan_approved),
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_PLAN_NOT_APPROVED,
        failed,
        (_value(_get(plan, "state")), _value(_get(plan, "decision"))),
    )


def review_controlled_simulation_scope(
    data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxControlledSimulationReviewPrecheckSection:
    data = _coerce_input(data)
    return _review_flag(data, "controlled_simulation_scope", data.controlled_simulation_scope_reviewed, data.controlled_simulation_scope_clear, data.controlled_simulation_scope_score, PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_SCOPE_UNCLEAR, ("SCOPE",))


def review_controlled_simulation_boundaries(
    data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxControlledSimulationReviewPrecheckSection:
    data = _coerce_input(data)
    return _review_flag(data, "controlled_simulation_boundaries", data.controlled_simulation_boundaries_reviewed, data.controlled_simulation_boundaries_complete, data.controlled_simulation_boundaries_score, PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_BOUNDARY_INCOMPLETE, ("BOUNDARY", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK"), _offline_boundary(data))


def review_controlled_simulation_scenario(
    data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxControlledSimulationReviewPrecheckSection:
    data = _coerce_input(data)
    return _review_flag(data, "controlled_simulation_scenario", data.controlled_simulation_scenario_reviewed, data.controlled_simulation_scenario_complete, data.controlled_simulation_scenario_score, PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_SCENARIO_INCOMPLETE, ("SCENARIO",))


def review_controlled_simulation_session_limits(
    data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxControlledSimulationReviewPrecheckSection:
    data = _coerce_input(data)
    return _review_flag(data, "controlled_simulation_session_limits", data.controlled_simulation_session_limits_reviewed, data.controlled_simulation_session_limits_complete, data.controlled_simulation_session_limits_score, PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_SESSION_LIMIT_INCOMPLETE, ("LIMIT", "CAP"))


def review_controlled_simulation_connection_policy(
    data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxControlledSimulationReviewPrecheckSection:
    data = _coerce_input(data)
    extra_ok = data.no_http_transport is True and data.no_websocket_transport is True and data.no_socket_transport is True and data.no_external_api is True
    return _review_flag(data, "controlled_simulation_connection_policy", data.controlled_simulation_connection_policy_reviewed, data.controlled_simulation_connection_policy_complete, data.controlled_simulation_connection_policy_score, PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_CONNECTION_POLICY_INCOMPLETE, ("CONNECTION", "NETWORK", "HTTP", "WEBSOCKET", "SOCKET", "API_ACCESS"), extra_ok)


def review_controlled_simulation_order_policy(
    data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxControlledSimulationReviewPrecheckSection:
    data = _coerce_input(data)
    extra_ok = data.no_real_order is True and data.no_live_execution is True and data.no_dry_run_execution is True
    return _review_flag(data, "controlled_simulation_order_policy", data.controlled_simulation_order_policy_reviewed, data.controlled_simulation_order_policy_complete, data.controlled_simulation_order_policy_score, PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_ORDER_POLICY_INCOMPLETE, ("ORDER", "EXECUTION_LEAK", "REAL_ORDER", "LIVE_EXECUTION"), extra_ok)


def review_controlled_simulation_position_policy(
    data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxControlledSimulationReviewPrecheckSection:
    data = _coerce_input(data)
    return _review_flag(data, "controlled_simulation_position_policy", data.controlled_simulation_position_policy_reviewed, data.controlled_simulation_position_policy_complete, data.controlled_simulation_position_policy_score, PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_POSITION_POLICY_INCOMPLETE, ("POSITION", "RECONCILIATION"))


def review_controlled_simulation_account_policy(
    data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxControlledSimulationReviewPrecheckSection:
    data = _coerce_input(data)
    extra_ok = data.no_api_key_read is True and data.no_real_account_access is True
    return _review_flag(data, "controlled_simulation_account_policy", data.controlled_simulation_account_policy_reviewed, data.controlled_simulation_account_policy_complete, data.controlled_simulation_account_policy_score, PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_ACCOUNT_POLICY_INCOMPLETE, ("ACCOUNT", "REAL_ACCOUNT", "CREDENTIAL", "API_KEY"), extra_ok)


def review_controlled_simulation_observability_policy(
    data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxControlledSimulationReviewPrecheckSection:
    data = _coerce_input(data)
    return _review_flag(data, "controlled_simulation_observability_policy", data.controlled_simulation_observability_policy_reviewed, data.controlled_simulation_observability_policy_complete, data.controlled_simulation_observability_policy_score, PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_OBSERVABILITY_INCOMPLETE, ("OBSERVABILITY",))


def review_controlled_simulation_rollback_policy(
    data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxControlledSimulationReviewPrecheckSection:
    data = _coerce_input(data)
    return _review_flag(data, "controlled_simulation_rollback_policy", data.controlled_simulation_rollback_policy_reviewed, data.controlled_simulation_rollback_policy_complete, data.controlled_simulation_rollback_policy_score, PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_ROLLBACK_INCOMPLETE, ("ROLLBACK",))


def review_controlled_simulation_kill_switch_policy(
    data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxControlledSimulationReviewPrecheckSection:
    data = _coerce_input(data)
    return _review_flag(data, "controlled_simulation_kill_switch_policy", data.controlled_simulation_kill_switch_policy_reviewed, data.controlled_simulation_kill_switch_policy_complete, data.controlled_simulation_kill_switch_policy_score, PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_KILL_SWITCH_INCOMPLETE, ("KILL_SWITCH",))


def review_controlled_simulation_human_supervision_policy(
    data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxControlledSimulationReviewPrecheckSection:
    data = _coerce_input(data)
    return _review_flag(data, "controlled_simulation_human_supervision_policy", data.controlled_simulation_human_supervision_policy_reviewed, data.controlled_simulation_human_supervision_policy_complete, data.controlled_simulation_human_supervision_policy_score, PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_HUMAN_SUPERVISION_INCOMPLETE, ("HUMAN", "SUPERVISION", "OPERATOR"))


def review_controlled_simulation_journal_policy(
    data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxControlledSimulationReviewPrecheckSection:
    data = _coerce_input(data)
    return _review_flag(data, "controlled_simulation_journal_policy", data.controlled_simulation_journal_policy_reviewed, data.controlled_simulation_journal_policy_complete, data.controlled_simulation_journal_policy_score, PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_JOURNAL_INCOMPLETE, ("JOURNAL", "AUDIT_TRAIL", "TRACE"))


def review_controlled_simulation_stop_conditions(
    data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxControlledSimulationReviewPrecheckSection:
    data = _coerce_input(data)
    return _review_flag(data, "controlled_simulation_stop_conditions", data.controlled_simulation_stop_conditions_reviewed, data.controlled_simulation_stop_conditions_complete, data.controlled_simulation_stop_conditions_score, PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_STOP_CONDITION_INCOMPLETE, ("STOP_CONDITION", "HALT", "EMERGENCY_STOP"))


def review_controlled_simulation_abort_conditions(
    data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxControlledSimulationReviewPrecheckSection:
    data = _coerce_input(data)
    return _review_flag(data, "controlled_simulation_abort_conditions", data.controlled_simulation_abort_conditions_reviewed, data.controlled_simulation_abort_conditions_complete, data.controlled_simulation_abort_conditions_score, PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_ABORT_CONDITION_INCOMPLETE, ("ABORT", "CANCEL", "EMERGENCY_ABORT"))


def review_controlled_simulation_success_failure_criteria(
    data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxControlledSimulationReviewPrecheckSection:
    data = _coerce_input(data)
    return _review_flag(data, "controlled_simulation_success_failure_criteria", data.controlled_simulation_success_failure_criteria_reviewed, data.controlled_simulation_success_failure_criteria_complete, data.controlled_simulation_success_failure_criteria_score, PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_SUCCESS_FAILURE_CRITERIA_INCOMPLETE, ("SUCCESS_CRITERIA", "FAILURE_CRITERIA"))


def verify_controlled_simulation_pre_execution_safety(
    data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxControlledSimulationReviewPrecheckSection:
    data = _coerce_input(data)
    safe = (
        _confirmed(data.controlled_simulation_pre_execution_safety_reviewed, data.controlled_simulation_pre_execution_safe)
        and _offline_boundary(data)
        and not _has_upstream_risk(data, "PRE_EXECUTION_GAP", "PRE_EXECUTION_SAFETY_GAP", "REAL_EXECUTION")
    )
    score = data.controlled_simulation_pre_execution_safety_score
    return _section(
        "controlled_simulation_pre_execution_safety",
        score if score is not None else _bool_score(safe),
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.REAL_EXECUTION_BOUNDARY_VIOLATION,
        not safe,
    )


def verify_controlled_simulation_no_real_execution(
    data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxControlledSimulationReviewPrecheckSection:
    data = _coerce_input(data)
    no_real_execution = _no_real_execution(data)
    score = data.controlled_simulation_no_real_execution_score
    return _section(
        "controlled_simulation_no_real_execution",
        score if score is not None else _bool_score(no_real_execution),
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.REAL_EXECUTION_BOUNDARY_VIOLATION,
        not no_real_execution,
    )


def verify_controlled_simulation_offline_boundaries(
    data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxControlledSimulationReviewPrecheckSection:
    data = _coerce_input(data)
    offline_ok = _offline_boundary(data)
    score = data.controlled_simulation_offline_boundaries_score
    return _section(
        "controlled_simulation_offline_boundaries",
        score if score is not None else _bool_score(offline_ok),
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.REAL_EXECUTION_BOUNDARY_VIOLATION,
        not offline_ok,
    )


def verify_controlled_simulation_human_approval_required(
    data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxControlledSimulationReviewPrecheckSection:
    data = _coerce_input(data)
    approved = (
        data.controlled_simulation_human_approval_required is True
        and data.controlled_simulation_human_approval_confirmed is True
        and data.controlled_simulation_human_supervision_policy_complete is True
    )
    score = data.controlled_simulation_human_approval_score
    return _section(
        "controlled_simulation_human_approval",
        score if score is not None else _bool_score(approved),
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_HUMAN_SUPERVISION_INCOMPLETE,
        not approved,
    )


def _all_sections(
    data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput,
) -> tuple[PaperBrokerSandboxControlledSimulationReviewPrecheckSection, ...]:
    return (
        review_controlled_simulation_plan_readiness(data),
        review_controlled_simulation_scope(data),
        review_controlled_simulation_boundaries(data),
        review_controlled_simulation_scenario(data),
        review_controlled_simulation_session_limits(data),
        review_controlled_simulation_connection_policy(data),
        review_controlled_simulation_order_policy(data),
        review_controlled_simulation_position_policy(data),
        review_controlled_simulation_account_policy(data),
        review_controlled_simulation_observability_policy(data),
        review_controlled_simulation_rollback_policy(data),
        review_controlled_simulation_kill_switch_policy(data),
        review_controlled_simulation_human_supervision_policy(data),
        review_controlled_simulation_journal_policy(data),
        review_controlled_simulation_stop_conditions(data),
        review_controlled_simulation_abort_conditions(data),
        review_controlled_simulation_success_failure_criteria(data),
        verify_controlled_simulation_pre_execution_safety(data),
        verify_controlled_simulation_no_real_execution(data),
        verify_controlled_simulation_offline_boundaries(data),
        verify_controlled_simulation_human_approval_required(data),
    )


def detect_controlled_simulation_review_precheck_risks(
    data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput | Mapping[str, Any],
    *sections: PaperBrokerSandboxControlledSimulationReviewPrecheckSection,
) -> tuple[PaperBrokerSandboxControlledSimulationReviewPrecheckRisk, ...]:
    data = _coerce_input(data)
    if not sections:
        sections = _all_sections(data)
    risks: list[PaperBrokerSandboxControlledSimulationReviewPrecheckRisk] = []
    for section in sections:
        risks.extend(section.risks)
    if (
        data.controlled_simulation_review_precheck_requested is not True
        or data.controlled_simulation_offline_runner_requested is True
        or data.controlled_simulation_real_execution_requested is True
        or data.controlled_simulation_execution_requested is True
        or not _offline_boundary(data)
    ):
        risks.append(PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.PREMATURE_CONTROLLED_SIMULATION_OFFLINE_RUNNER)
    return _dedupe(risks)


def compute_controlled_simulation_review_precheck_score(
    data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput | Mapping[str, Any],
    risks: tuple[PaperBrokerSandboxControlledSimulationReviewPrecheckRisk, ...] = (),
    *sections: PaperBrokerSandboxControlledSimulationReviewPrecheckSection,
) -> PaperBrokerSandboxControlledSimulationReviewPrecheckScore:
    data = _coerce_input(data)
    if not sections:
        sections = _all_sections(data)
    scores = tuple(section.score for section in sections)
    overall = _clamp(_average(scores) - min(95, len(set(risks)) * 5))
    for risk, cap in {
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_PLAN_NOT_APPROVED: 50,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_SCOPE_UNCLEAR: 60,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_BOUNDARY_INCOMPLETE: 45,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_SCENARIO_INCOMPLETE: 60,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_SESSION_LIMIT_INCOMPLETE: 55,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_CONNECTION_POLICY_INCOMPLETE: 50,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_ORDER_POLICY_INCOMPLETE: 50,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_POSITION_POLICY_INCOMPLETE: 60,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_ACCOUNT_POLICY_INCOMPLETE: 45,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_OBSERVABILITY_INCOMPLETE: 60,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_ROLLBACK_INCOMPLETE: 55,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_KILL_SWITCH_INCOMPLETE: 50,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_HUMAN_SUPERVISION_INCOMPLETE: 45,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_JOURNAL_INCOMPLETE: 60,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_STOP_CONDITION_INCOMPLETE: 45,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_ABORT_CONDITION_INCOMPLETE: 45,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_SUCCESS_FAILURE_CRITERIA_INCOMPLETE: 50,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.REAL_EXECUTION_BOUNDARY_VIOLATION: 45,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.PREMATURE_CONTROLLED_SIMULATION_OFFLINE_RUNNER: 40,
    }.items():
        if risk in risks:
            overall = min(overall, cap)
    return PaperBrokerSandboxControlledSimulationReviewPrecheckScore(overall, *scores)


def _select_decision(
    risks: tuple[PaperBrokerSandboxControlledSimulationReviewPrecheckRisk, ...],
    score: int,
) -> PaperBrokerSandboxControlledSimulationReviewPrecheckDecision:
    if PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.PREMATURE_CONTROLLED_SIMULATION_OFFLINE_RUNNER in risks or score < 45:
        return PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.BLOCK_CONTROLLED_SIMULATION
    if PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_PLAN_NOT_APPROVED in risks:
        return PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_CONTROLLED_SIMULATION_PLAN_FIXES
    if PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_SCOPE_UNCLEAR in risks:
        return PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_SCOPE_FIXES
    if (
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_BOUNDARY_INCOMPLETE in risks
        or PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in risks
    ):
        return PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_BOUNDARY_FIXES
    if PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_SCENARIO_INCOMPLETE in risks:
        return PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_SCENARIO_FIXES
    if PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_SESSION_LIMIT_INCOMPLETE in risks:
        return PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_SESSION_LIMIT_FIXES
    if PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_CONNECTION_POLICY_INCOMPLETE in risks:
        return PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_CONNECTION_POLICY_FIXES
    if PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_ORDER_POLICY_INCOMPLETE in risks:
        return PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_ORDER_POLICY_FIXES
    if PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_POSITION_POLICY_INCOMPLETE in risks:
        return PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_POSITION_POLICY_FIXES
    if PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_ACCOUNT_POLICY_INCOMPLETE in risks:
        return PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_ACCOUNT_POLICY_FIXES
    if PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_OBSERVABILITY_INCOMPLETE in risks:
        return PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_OBSERVABILITY_FIXES
    if PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_ROLLBACK_INCOMPLETE in risks:
        return PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_ROLLBACK_FIXES
    if PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_KILL_SWITCH_INCOMPLETE in risks:
        return PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_KILL_SWITCH_FIXES
    if PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_HUMAN_SUPERVISION_INCOMPLETE in risks:
        return PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_SUPERVISION_FIXES
    if PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_JOURNAL_INCOMPLETE in risks:
        return PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_JOURNAL_FIXES
    if PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_STOP_CONDITION_INCOMPLETE in risks:
        return PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_STOP_CONDITION_FIXES
    if PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_ABORT_CONDITION_INCOMPLETE in risks:
        return PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_ABORT_CONDITION_FIXES
    if PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_SUCCESS_FAILURE_CRITERIA_INCOMPLETE in risks:
        return PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_SUCCESS_FAILURE_CRITERIA_FIXES
    if risks:
        return PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.REQUIRE_BOUNDARY_FIXES
    return PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.APPROVE_CONTROLLED_SIMULATION_REVIEW_PRECHECK


def _select_state(
    decision: PaperBrokerSandboxControlledSimulationReviewPrecheckDecision,
    score: int,
) -> PaperBrokerSandboxControlledSimulationReviewPrecheckState:
    if decision == PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.BLOCK_CONTROLLED_SIMULATION:
        return PaperBrokerSandboxControlledSimulationReviewPrecheckState.NOT_READY
    if decision != PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.APPROVE_CONTROLLED_SIMULATION_REVIEW_PRECHECK:
        return (
            PaperBrokerSandboxControlledSimulationReviewPrecheckState.REVIEW_PRECHECK_REQUIRED
            if score < 82
            else PaperBrokerSandboxControlledSimulationReviewPrecheckState.PARTIALLY_READY
        )
    if score >= 95:
        return PaperBrokerSandboxControlledSimulationReviewPrecheckState.READY_FOR_CONTROLLED_SIMULATION_OFFLINE_RUNNER
    return PaperBrokerSandboxControlledSimulationReviewPrecheckState.CONTROLLED_SIMULATION_REVIEW_PRECHECK_READY


def generate_controlled_simulation_review_precheck_recommendations(
    risks: tuple[PaperBrokerSandboxControlledSimulationReviewPrecheckRisk, ...],
    decision: PaperBrokerSandboxControlledSimulationReviewPrecheckDecision | None = None,
) -> tuple[PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation, ...]:
    recommendations: list[PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation] = []
    if risks:
        recommendations.append(PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.HOLD_CONTROLLED_SIMULATION_OFFLINE_RUNNER)
    mapping = {
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_PLAN_NOT_APPROVED: PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.APPROVE_CONTROLLED_SIMULATION_PLAN_FIRST,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_SCOPE_UNCLEAR: PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.CLARIFY_CONTROLLED_SIMULATION_SCOPE,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_BOUNDARY_INCOMPLETE: PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.COMPLETE_CONTROLLED_SIMULATION_BOUNDARIES,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_SCENARIO_INCOMPLETE: PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.COMPLETE_CONTROLLED_SIMULATION_SCENARIO,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_SESSION_LIMIT_INCOMPLETE: PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.COMPLETE_CONTROLLED_SIMULATION_SESSION_LIMITS,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_CONNECTION_POLICY_INCOMPLETE: PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.COMPLETE_CONTROLLED_SIMULATION_CONNECTION_POLICY,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_ORDER_POLICY_INCOMPLETE: PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.COMPLETE_CONTROLLED_SIMULATION_ORDER_POLICY,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_POSITION_POLICY_INCOMPLETE: PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.COMPLETE_CONTROLLED_SIMULATION_POSITION_POLICY,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_ACCOUNT_POLICY_INCOMPLETE: PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.COMPLETE_CONTROLLED_SIMULATION_ACCOUNT_POLICY,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_OBSERVABILITY_INCOMPLETE: PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.COMPLETE_CONTROLLED_SIMULATION_OBSERVABILITY_POLICY,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_ROLLBACK_INCOMPLETE: PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.COMPLETE_CONTROLLED_SIMULATION_ROLLBACK_POLICY,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_KILL_SWITCH_INCOMPLETE: PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.COMPLETE_CONTROLLED_SIMULATION_KILL_SWITCH_POLICY,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_HUMAN_SUPERVISION_INCOMPLETE: PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.COMPLETE_CONTROLLED_SIMULATION_HUMAN_SUPERVISION_POLICY,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_JOURNAL_INCOMPLETE: PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.COMPLETE_CONTROLLED_SIMULATION_JOURNAL_POLICY,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_STOP_CONDITION_INCOMPLETE: PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.COMPLETE_CONTROLLED_SIMULATION_STOP_CONDITIONS,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_ABORT_CONDITION_INCOMPLETE: PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.COMPLETE_CONTROLLED_SIMULATION_ABORT_CONDITIONS,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.CONTROLLED_SIMULATION_SUCCESS_FAILURE_CRITERIA_INCOMPLETE: PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.COMPLETE_CONTROLLED_SIMULATION_SUCCESS_FAILURE_CRITERIA,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.REAL_EXECUTION_BOUNDARY_VIOLATION: PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.RESTORE_REAL_EXECUTION_BOUNDARIES,
        PaperBrokerSandboxControlledSimulationReviewPrecheckRisk.PREMATURE_CONTROLLED_SIMULATION_OFFLINE_RUNNER: PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.DELAY_CONTROLLED_SIMULATION_OFFLINE_RUNNER,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.RUN_CONTROLLED_SIMULATION_REVIEW_PRECHECK_SUITE)
    if decision == PaperBrokerSandboxControlledSimulationReviewPrecheckDecision.APPROVE_CONTROLLED_SIMULATION_REVIEW_PRECHECK:
        recommendations.append(PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation.APPROVE_CONTROLLED_SIMULATION_OFFLINE_RUNNER)
    return _dedupe(recommendations)


def evaluate_paper_broker_sandbox_controlled_simulation_review_precheck(
    data: PaperBrokerSandboxControlledSimulationReviewPrecheckInput | Mapping[str, Any],
) -> PaperBrokerSandboxControlledSimulationReviewPrecheckResult:
    data = _coerce_input(data)
    sections = _all_sections(data)
    risks = detect_controlled_simulation_review_precheck_risks(data, *sections)
    score = compute_controlled_simulation_review_precheck_score(data, risks, *sections)
    decision = _select_decision(risks, score.overall_score)
    state = _select_state(decision, score.overall_score)
    recommendations = generate_controlled_simulation_review_precheck_recommendations(risks, decision)
    offline_only = _offline_boundary(data)
    summary = f"{state.value}: decision={decision.value}, score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return PaperBrokerSandboxControlledSimulationReviewPrecheckResult(
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


def render_controlled_simulation_review_precheck_markdown(
    result: PaperBrokerSandboxControlledSimulationReviewPrecheckResult,
) -> str:
    lines = [
        "# AGIcore Controlled Simulation Review + Precheck",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Score: {result.review_precheck_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Controlled Simulation Review + Precheck Sections",
    ]
    sections = (
        result.controlled_simulation_plan_readiness,
        result.controlled_simulation_scope,
        result.controlled_simulation_boundaries,
        result.controlled_simulation_scenario,
        result.controlled_simulation_session_limits,
        result.controlled_simulation_connection_policy,
        result.controlled_simulation_order_policy,
        result.controlled_simulation_position_policy,
        result.controlled_simulation_account_policy,
        result.controlled_simulation_observability_policy,
        result.controlled_simulation_rollback_policy,
        result.controlled_simulation_kill_switch_policy,
        result.controlled_simulation_human_supervision_policy,
        result.controlled_simulation_journal_policy,
        result.controlled_simulation_stop_conditions,
        result.controlled_simulation_abort_conditions,
        result.controlled_simulation_success_failure_criteria,
        result.controlled_simulation_pre_execution_safety,
        result.controlled_simulation_no_real_execution,
        result.controlled_simulation_offline_boundaries,
        result.controlled_simulation_human_approval,
    )
    for section in sections:
        risks = ", ".join(risk.value for risk in section.risks) or "none"
        lines.append(f"- {section.name}: passed={section.passed}, score={section.score}/100, risks={risks}")
        lines.extend(f"  - {item}" for item in section.evidence if item)
    lines.append("")
    lines.append("# Controlled Simulation Review + Precheck Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Controlled Simulation Review + Precheck Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_controlled_simulation_review_precheck_score",
    "detect_controlled_simulation_review_precheck_risks",
    "evaluate_paper_broker_sandbox_controlled_simulation_review_precheck",
    "generate_controlled_simulation_review_precheck_recommendations",
    "render_controlled_simulation_review_precheck_markdown",
    "review_controlled_simulation_abort_conditions",
    "review_controlled_simulation_account_policy",
    "review_controlled_simulation_boundaries",
    "review_controlled_simulation_connection_policy",
    "review_controlled_simulation_human_supervision_policy",
    "review_controlled_simulation_journal_policy",
    "review_controlled_simulation_kill_switch_policy",
    "review_controlled_simulation_observability_policy",
    "review_controlled_simulation_order_policy",
    "review_controlled_simulation_plan_readiness",
    "review_controlled_simulation_position_policy",
    "review_controlled_simulation_rollback_policy",
    "review_controlled_simulation_scenario",
    "review_controlled_simulation_scope",
    "review_controlled_simulation_session_limits",
    "review_controlled_simulation_stop_conditions",
    "review_controlled_simulation_success_failure_criteria",
    "verify_controlled_simulation_human_approval_required",
    "verify_controlled_simulation_no_real_execution",
    "verify_controlled_simulation_offline_boundaries",
    "verify_controlled_simulation_pre_execution_safety",
]
