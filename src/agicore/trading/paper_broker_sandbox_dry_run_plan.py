"""Offline plan gate for a future AGIcore Paper Broker Sandbox Dry Run Review."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_broker_sandbox_dry_run_plan_models import (
    PaperBrokerSandboxDryRunPlanDecision,
    PaperBrokerSandboxDryRunPlanInput,
    PaperBrokerSandboxDryRunPlanRecommendation,
    PaperBrokerSandboxDryRunPlanResult,
    PaperBrokerSandboxDryRunPlanRisk,
    PaperBrokerSandboxDryRunPlanScore,
    PaperBrokerSandboxDryRunPlanSection,
    PaperBrokerSandboxDryRunPlanState,
)


def _coerce_input(data: PaperBrokerSandboxDryRunPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunPlanInput:
    if isinstance(data, PaperBrokerSandboxDryRunPlanInput):
        return data
    allowed = {field.name for field in fields(PaperBrokerSandboxDryRunPlanInput)}
    payload = {key: value for key, value in dict(data).items() if key in allowed}
    return PaperBrokerSandboxDryRunPlanInput(**payload)


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


def _upstream_items(data: PaperBrokerSandboxDryRunPlanInput) -> tuple[Any, ...]:
    return (
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


def _upstream_risks(data: PaperBrokerSandboxDryRunPlanInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperBrokerSandboxDryRunPlanInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _offline_boundary(data: PaperBrokerSandboxDryRunPlanInput) -> bool:
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
            "API_KEY",
            "CREDENTIAL",
        )
    )


def _section(
    name: str,
    score: int,
    risk: PaperBrokerSandboxDryRunPlanRisk,
    failed: bool,
    details: tuple[str, ...] = (),
) -> PaperBrokerSandboxDryRunPlanSection:
    risks = (risk,) if failed or score < 85 else ()
    return PaperBrokerSandboxDryRunPlanSection(name, _clamp(score), not risks and score >= 85, risks, details)


def _definition_section(
    name: str,
    defined: bool | None,
    score: int | None,
    risk: PaperBrokerSandboxDryRunPlanRisk,
    upstream_needles: tuple[str, ...] = (),
) -> PaperBrokerSandboxDryRunPlanSection:
    failed = defined is not True
    section_score = score if score is not None else _bool_score(defined)
    return _section(name, section_score, risk, failed, upstream_needles)


def verify_authorization_gate_readiness(
    data: PaperBrokerSandboxDryRunPlanInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunPlanSection:
    data = _coerce_input(data)
    gate = data.paper_broker_sandbox_session_authorization_gate
    gate_state_ok = _state_contains(
        gate,
        "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN",
        "APPROVE_PAPER_BROKER_SANDBOX_AUTHORIZATION_GATE",
    )
    gate_approved = (
        data.authorization_gate_approved is not False
        and data.authorization_gate_reviewed is not False
        and (data.authorization_gate_approved is True or gate_state_ok)
    )
    failed = not gate_approved or _has_upstream_risk(
        data,
        "SANDBOX_REVIEW_NOT_APPROVED",
        "AUTHORIZATION_GATE_NOT_APPROVED",
        "BLOCK_PAPER_BROKER_SANDBOX_SESSION",
    )
    score = data.authorization_gate_readiness_score if data.authorization_gate_readiness_score is not None else _bool_score(gate_approved)
    return _section(
        "authorization_gate_readiness",
        score,
        PaperBrokerSandboxDryRunPlanRisk.AUTHORIZATION_GATE_NOT_APPROVED,
        failed,
        (_value(_get(gate, "state")), _value(_get(gate, "decision"))),
    )


def define_dry_run_scope(data: PaperBrokerSandboxDryRunPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunPlanSection:
    data = _coerce_input(data)
    scope_clear = _confirmed(data.dry_run_scope_defined, data.dry_run_scope_clear)
    failed = not scope_clear or _has_upstream_risk(data, "SCOPE")
    score = data.dry_run_scope_score if data.dry_run_scope_score is not None else _bool_score(scope_clear)
    return _section("dry_run_scope", score, PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_SCOPE_UNCLEAR, failed)


def define_dry_run_boundaries(data: PaperBrokerSandboxDryRunPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunPlanSection:
    data = _coerce_input(data)
    boundaries_complete = _confirmed(data.dry_run_boundaries_defined, data.dry_run_boundaries_complete)
    boundary_ok = boundaries_complete and _offline_boundary(data)
    failed = not boundary_ok or _has_upstream_risk(data, "BOUNDARY", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK")
    score = data.dry_run_boundaries_score if data.dry_run_boundaries_score is not None else _bool_score(boundary_ok)
    return _section("dry_run_boundaries", score, PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_BOUNDARY_GAP, failed)


def define_dry_run_scenario(data: PaperBrokerSandboxDryRunPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunPlanSection:
    data = _coerce_input(data)
    failed = data.dry_run_scenario_defined is not True or _has_upstream_risk(data, "SCENARIO")
    score = data.dry_run_scenario_score if data.dry_run_scenario_score is not None else _bool_score(data.dry_run_scenario_defined)
    return _section("dry_run_scenario", score, PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_SCENARIO_UNDEFINED, failed)


def define_dry_run_session_limits(data: PaperBrokerSandboxDryRunPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunPlanSection:
    data = _coerce_input(data)
    failed = data.dry_run_session_limits_defined is not True or _has_upstream_risk(data, "LIMIT", "CAP")
    score = data.dry_run_session_limits_score if data.dry_run_session_limits_score is not None else _bool_score(data.dry_run_session_limits_defined)
    return _section("dry_run_session_limits", score, PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_SESSION_LIMIT_GAP, failed)


def define_dry_run_connection_policy(data: PaperBrokerSandboxDryRunPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunPlanSection:
    data = _coerce_input(data)
    connection_policy_ok = (
        data.dry_run_connection_policy_defined is True
        and data.no_http_transport is True
        and data.no_websocket_transport is True
        and data.no_socket_transport is True
        and data.no_external_api is True
    )
    failed = not connection_policy_ok or _has_upstream_risk(data, "CONNECTION", "NETWORK", "HTTP", "WEBSOCKET", "SOCKET", "API_ACCESS")
    score = data.dry_run_connection_policy_score if data.dry_run_connection_policy_score is not None else _bool_score(connection_policy_ok)
    return _section("dry_run_connection_policy", score, PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_CONNECTION_POLICY_GAP, failed)


def define_dry_run_order_policy(data: PaperBrokerSandboxDryRunPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunPlanSection:
    data = _coerce_input(data)
    order_policy_ok = data.dry_run_order_policy_defined is True and data.no_real_order is True and data.no_live_execution is True
    failed = not order_policy_ok or _has_upstream_risk(data, "ORDER", "EXECUTION_LEAK", "REAL_ORDER", "LIVE_EXECUTION")
    score = data.dry_run_order_policy_score if data.dry_run_order_policy_score is not None else _bool_score(order_policy_ok)
    return _section("dry_run_order_policy", score, PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_ORDER_POLICY_GAP, failed)


def define_dry_run_position_policy(data: PaperBrokerSandboxDryRunPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunPlanSection:
    data = _coerce_input(data)
    failed = data.dry_run_position_policy_defined is not True or _has_upstream_risk(data, "POSITION", "RECONCILIATION")
    score = data.dry_run_position_policy_score if data.dry_run_position_policy_score is not None else _bool_score(data.dry_run_position_policy_defined)
    return _section("dry_run_position_policy", score, PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_POSITION_POLICY_GAP, failed)


def define_dry_run_account_policy(data: PaperBrokerSandboxDryRunPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunPlanSection:
    data = _coerce_input(data)
    account_policy_ok = data.dry_run_account_policy_defined is True and data.no_api_key_read is True and data.no_real_account_access is True
    failed = not account_policy_ok or _has_upstream_risk(data, "ACCOUNT", "REAL_ACCOUNT", "CREDENTIAL", "API_KEY")
    score = data.dry_run_account_policy_score if data.dry_run_account_policy_score is not None else _bool_score(account_policy_ok)
    return _section("dry_run_account_policy", score, PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_ACCOUNT_POLICY_GAP, failed)


def define_dry_run_observability_policy(data: PaperBrokerSandboxDryRunPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunPlanSection:
    data = _coerce_input(data)
    failed = data.dry_run_observability_policy_defined is not True or _has_upstream_risk(data, "OBSERVABILITY")
    score = data.dry_run_observability_policy_score if data.dry_run_observability_policy_score is not None else _bool_score(data.dry_run_observability_policy_defined)
    return _section("dry_run_observability_policy", score, PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_OBSERVABILITY_GAP, failed)


def define_dry_run_rollback_policy(data: PaperBrokerSandboxDryRunPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunPlanSection:
    data = _coerce_input(data)
    failed = data.dry_run_rollback_policy_defined is not True or _has_upstream_risk(data, "ROLLBACK")
    score = data.dry_run_rollback_policy_score if data.dry_run_rollback_policy_score is not None else _bool_score(data.dry_run_rollback_policy_defined)
    return _section("dry_run_rollback_policy", score, PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_ROLLBACK_GAP, failed)


def define_dry_run_kill_switch_policy(data: PaperBrokerSandboxDryRunPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunPlanSection:
    data = _coerce_input(data)
    failed = data.dry_run_kill_switch_policy_defined is not True or _has_upstream_risk(data, "KILL_SWITCH")
    score = data.dry_run_kill_switch_policy_score if data.dry_run_kill_switch_policy_score is not None else _bool_score(data.dry_run_kill_switch_policy_defined)
    return _section("dry_run_kill_switch_policy", score, PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_KILL_SWITCH_GAP, failed)


def define_dry_run_human_supervision_policy(data: PaperBrokerSandboxDryRunPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunPlanSection:
    data = _coerce_input(data)
    failed = data.dry_run_human_supervision_policy_defined is not True or _has_upstream_risk(data, "HUMAN", "SUPERVISION", "OPERATOR")
    score = data.dry_run_human_supervision_policy_score if data.dry_run_human_supervision_policy_score is not None else _bool_score(data.dry_run_human_supervision_policy_defined)
    return _section("dry_run_human_supervision_policy", score, PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_HUMAN_SUPERVISION_GAP, failed)


def define_dry_run_journal_policy(data: PaperBrokerSandboxDryRunPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunPlanSection:
    data = _coerce_input(data)
    failed = data.dry_run_journal_policy_defined is not True or _has_upstream_risk(data, "JOURNAL", "AUDIT_TRAIL", "TRACE")
    score = data.dry_run_journal_policy_score if data.dry_run_journal_policy_score is not None else _bool_score(data.dry_run_journal_policy_defined)
    return _section("dry_run_journal_policy", score, PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_JOURNAL_GAP, failed)


def define_dry_run_stop_conditions(data: PaperBrokerSandboxDryRunPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunPlanSection:
    data = _coerce_input(data)
    failed = data.dry_run_stop_conditions_defined is not True or _has_upstream_risk(data, "STOP_CONDITION", "HALT", "EMERGENCY_STOP")
    score = data.dry_run_stop_conditions_score if data.dry_run_stop_conditions_score is not None else _bool_score(data.dry_run_stop_conditions_defined)
    return _section("dry_run_stop_conditions", score, PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_STOP_CONDITION_GAP, failed)


def define_dry_run_success_criteria(data: PaperBrokerSandboxDryRunPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunPlanSection:
    data = _coerce_input(data)
    failed = data.dry_run_success_criteria_defined is not True or _has_upstream_risk(data, "SUCCESS_CRITERIA")
    score = data.dry_run_success_criteria_score if data.dry_run_success_criteria_score is not None else _bool_score(data.dry_run_success_criteria_defined)
    return _section("dry_run_success_criteria", score, PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_STOP_CONDITION_GAP, failed)


def define_dry_run_failure_criteria(data: PaperBrokerSandboxDryRunPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunPlanSection:
    data = _coerce_input(data)
    failed = data.dry_run_failure_criteria_defined is not True or _has_upstream_risk(data, "FAILURE_CRITERIA")
    score = data.dry_run_failure_criteria_score if data.dry_run_failure_criteria_score is not None else _bool_score(data.dry_run_failure_criteria_defined)
    return _section("dry_run_failure_criteria", score, PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_STOP_CONDITION_GAP, failed)


def _all_sections(data: PaperBrokerSandboxDryRunPlanInput) -> tuple[PaperBrokerSandboxDryRunPlanSection, ...]:
    return (
        verify_authorization_gate_readiness(data),
        define_dry_run_scope(data),
        define_dry_run_boundaries(data),
        define_dry_run_scenario(data),
        define_dry_run_session_limits(data),
        define_dry_run_connection_policy(data),
        define_dry_run_order_policy(data),
        define_dry_run_position_policy(data),
        define_dry_run_account_policy(data),
        define_dry_run_observability_policy(data),
        define_dry_run_rollback_policy(data),
        define_dry_run_kill_switch_policy(data),
        define_dry_run_human_supervision_policy(data),
        define_dry_run_journal_policy(data),
        define_dry_run_stop_conditions(data),
        define_dry_run_success_criteria(data),
        define_dry_run_failure_criteria(data),
    )


def detect_dry_run_plan_risks(
    data: PaperBrokerSandboxDryRunPlanInput | Mapping[str, Any],
    *sections: PaperBrokerSandboxDryRunPlanSection,
) -> tuple[PaperBrokerSandboxDryRunPlanRisk, ...]:
    data = _coerce_input(data)
    if not sections:
        sections = _all_sections(data)
    risks: list[PaperBrokerSandboxDryRunPlanRisk] = []
    for section in sections:
        risks.extend(section.risks)
    if (
        data.paper_broker_sandbox_dry_run_plan_requested is not True
        or data.paper_broker_sandbox_dry_run_execution_requested is True
        or not _offline_boundary(data)
    ):
        risks.append(PaperBrokerSandboxDryRunPlanRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION)
    return _dedupe(risks)


def compute_dry_run_plan_score(
    data: PaperBrokerSandboxDryRunPlanInput | Mapping[str, Any],
    risks: tuple[PaperBrokerSandboxDryRunPlanRisk, ...] = (),
    *sections: PaperBrokerSandboxDryRunPlanSection,
) -> PaperBrokerSandboxDryRunPlanScore:
    data = _coerce_input(data)
    if not sections:
        sections = _all_sections(data)
    scores = tuple(section.score for section in sections)
    overall = _clamp(_average(scores) - min(85, len(set(risks)) * 5))
    for risk, cap in {
        PaperBrokerSandboxDryRunPlanRisk.AUTHORIZATION_GATE_NOT_APPROVED: 50,
        PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_SCOPE_UNCLEAR: 60,
        PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_BOUNDARY_GAP: 45,
        PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_SCENARIO_UNDEFINED: 60,
        PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_SESSION_LIMIT_GAP: 55,
        PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_CONNECTION_POLICY_GAP: 50,
        PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_ORDER_POLICY_GAP: 55,
        PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_POSITION_POLICY_GAP: 60,
        PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_ACCOUNT_POLICY_GAP: 50,
        PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_OBSERVABILITY_GAP: 60,
        PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_ROLLBACK_GAP: 55,
        PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_KILL_SWITCH_GAP: 50,
        PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_HUMAN_SUPERVISION_GAP: 45,
        PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_JOURNAL_GAP: 60,
        PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_STOP_CONDITION_GAP: 45,
        PaperBrokerSandboxDryRunPlanRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION: 40,
    }.items():
        if risk in risks:
            overall = min(overall, cap)
    return PaperBrokerSandboxDryRunPlanScore(overall, *scores)


def _select_decision(
    risks: tuple[PaperBrokerSandboxDryRunPlanRisk, ...],
    score: int,
) -> PaperBrokerSandboxDryRunPlanDecision:
    if PaperBrokerSandboxDryRunPlanRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION in risks or score < 45:
        return PaperBrokerSandboxDryRunPlanDecision.BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN
    if PaperBrokerSandboxDryRunPlanRisk.AUTHORIZATION_GATE_NOT_APPROVED in risks:
        return PaperBrokerSandboxDryRunPlanDecision.REQUIRE_AUTHORIZATION_GATE_FIXES
    if PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_SCOPE_UNCLEAR in risks:
        return PaperBrokerSandboxDryRunPlanDecision.REQUIRE_SCOPE_FIXES
    if PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_BOUNDARY_GAP in risks:
        return PaperBrokerSandboxDryRunPlanDecision.REQUIRE_BOUNDARY_FIXES
    if PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_SCENARIO_UNDEFINED in risks:
        return PaperBrokerSandboxDryRunPlanDecision.REQUIRE_SCENARIO_FIXES
    if PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_SESSION_LIMIT_GAP in risks:
        return PaperBrokerSandboxDryRunPlanDecision.REQUIRE_SESSION_LIMIT_FIXES
    if PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_CONNECTION_POLICY_GAP in risks:
        return PaperBrokerSandboxDryRunPlanDecision.REQUIRE_CONNECTION_POLICY_FIXES
    if PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_ORDER_POLICY_GAP in risks:
        return PaperBrokerSandboxDryRunPlanDecision.REQUIRE_ORDER_POLICY_FIXES
    if PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_POSITION_POLICY_GAP in risks:
        return PaperBrokerSandboxDryRunPlanDecision.REQUIRE_POSITION_POLICY_FIXES
    if PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_ACCOUNT_POLICY_GAP in risks:
        return PaperBrokerSandboxDryRunPlanDecision.REQUIRE_ACCOUNT_POLICY_FIXES
    if PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_OBSERVABILITY_GAP in risks:
        return PaperBrokerSandboxDryRunPlanDecision.REQUIRE_OBSERVABILITY_FIXES
    if PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_ROLLBACK_GAP in risks:
        return PaperBrokerSandboxDryRunPlanDecision.REQUIRE_ROLLBACK_FIXES
    if PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_KILL_SWITCH_GAP in risks:
        return PaperBrokerSandboxDryRunPlanDecision.REQUIRE_KILL_SWITCH_FIXES
    if PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_HUMAN_SUPERVISION_GAP in risks:
        return PaperBrokerSandboxDryRunPlanDecision.REQUIRE_SUPERVISION_FIXES
    if PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_JOURNAL_GAP in risks:
        return PaperBrokerSandboxDryRunPlanDecision.REQUIRE_JOURNAL_FIXES
    if PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_STOP_CONDITION_GAP in risks:
        return PaperBrokerSandboxDryRunPlanDecision.REQUIRE_STOP_CONDITION_FIXES
    if risks:
        return PaperBrokerSandboxDryRunPlanDecision.REQUIRE_BOUNDARY_FIXES
    return PaperBrokerSandboxDryRunPlanDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_PLAN


def _select_state(
    decision: PaperBrokerSandboxDryRunPlanDecision,
    score: int,
) -> PaperBrokerSandboxDryRunPlanState:
    if decision == PaperBrokerSandboxDryRunPlanDecision.BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN:
        return PaperBrokerSandboxDryRunPlanState.NOT_READY
    if decision != PaperBrokerSandboxDryRunPlanDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_PLAN:
        return PaperBrokerSandboxDryRunPlanState.DRY_RUN_PLAN_REVIEW_REQUIRED if score < 82 else PaperBrokerSandboxDryRunPlanState.PARTIALLY_PLANNED
    if score >= 95:
        return PaperBrokerSandboxDryRunPlanState.READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_REVIEW
    return PaperBrokerSandboxDryRunPlanState.DRY_RUN_PLAN_READY


def generate_dry_run_plan_recommendations(
    risks: tuple[PaperBrokerSandboxDryRunPlanRisk, ...],
    decision: PaperBrokerSandboxDryRunPlanDecision | None = None,
) -> tuple[PaperBrokerSandboxDryRunPlanRecommendation, ...]:
    recommendations: list[PaperBrokerSandboxDryRunPlanRecommendation] = []
    if risks:
        recommendations.append(PaperBrokerSandboxDryRunPlanRecommendation.HOLD_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION)
    mapping = {
        PaperBrokerSandboxDryRunPlanRisk.AUTHORIZATION_GATE_NOT_APPROVED: PaperBrokerSandboxDryRunPlanRecommendation.APPROVE_AUTHORIZATION_GATE_FIRST,
        PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_SCOPE_UNCLEAR: PaperBrokerSandboxDryRunPlanRecommendation.CLARIFY_DRY_RUN_SCOPE,
        PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_BOUNDARY_GAP: PaperBrokerSandboxDryRunPlanRecommendation.COMPLETE_DRY_RUN_BOUNDARIES,
        PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_SCENARIO_UNDEFINED: PaperBrokerSandboxDryRunPlanRecommendation.DEFINE_DRY_RUN_SCENARIO,
        PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_SESSION_LIMIT_GAP: PaperBrokerSandboxDryRunPlanRecommendation.DEFINE_DRY_RUN_SESSION_LIMITS,
        PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_CONNECTION_POLICY_GAP: PaperBrokerSandboxDryRunPlanRecommendation.DEFINE_DRY_RUN_CONNECTION_POLICY,
        PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_ORDER_POLICY_GAP: PaperBrokerSandboxDryRunPlanRecommendation.DEFINE_DRY_RUN_ORDER_POLICY,
        PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_POSITION_POLICY_GAP: PaperBrokerSandboxDryRunPlanRecommendation.DEFINE_DRY_RUN_POSITION_POLICY,
        PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_ACCOUNT_POLICY_GAP: PaperBrokerSandboxDryRunPlanRecommendation.DEFINE_DRY_RUN_ACCOUNT_POLICY,
        PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_OBSERVABILITY_GAP: PaperBrokerSandboxDryRunPlanRecommendation.DEFINE_DRY_RUN_OBSERVABILITY_POLICY,
        PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_ROLLBACK_GAP: PaperBrokerSandboxDryRunPlanRecommendation.DEFINE_DRY_RUN_ROLLBACK_POLICY,
        PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_KILL_SWITCH_GAP: PaperBrokerSandboxDryRunPlanRecommendation.DEFINE_DRY_RUN_KILL_SWITCH_POLICY,
        PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_HUMAN_SUPERVISION_GAP: PaperBrokerSandboxDryRunPlanRecommendation.DEFINE_DRY_RUN_HUMAN_SUPERVISION_POLICY,
        PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_JOURNAL_GAP: PaperBrokerSandboxDryRunPlanRecommendation.DEFINE_DRY_RUN_JOURNAL_POLICY,
        PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_STOP_CONDITION_GAP: PaperBrokerSandboxDryRunPlanRecommendation.DEFINE_DRY_RUN_STOP_CONDITIONS,
        PaperBrokerSandboxDryRunPlanRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION: PaperBrokerSandboxDryRunPlanRecommendation.DELAY_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    if PaperBrokerSandboxDryRunPlanRisk.DRY_RUN_STOP_CONDITION_GAP in risks:
        recommendations.append(PaperBrokerSandboxDryRunPlanRecommendation.DEFINE_DRY_RUN_SUCCESS_AND_FAILURE_CRITERIA)
    recommendations.append(PaperBrokerSandboxDryRunPlanRecommendation.RUN_PAPER_BROKER_SANDBOX_DRY_RUN_PLAN_SUITE)
    if decision == PaperBrokerSandboxDryRunPlanDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_PLAN:
        recommendations.append(PaperBrokerSandboxDryRunPlanRecommendation.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_REVIEW)
    return _dedupe(recommendations)


def evaluate_paper_broker_sandbox_dry_run_plan(
    data: PaperBrokerSandboxDryRunPlanInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunPlanResult:
    data = _coerce_input(data)
    sections = _all_sections(data)
    risks = detect_dry_run_plan_risks(data, *sections)
    score = compute_dry_run_plan_score(data, risks, *sections)
    decision = _select_decision(risks, score.overall_score)
    state = _select_state(decision, score.overall_score)
    recommendations = generate_dry_run_plan_recommendations(risks, decision)
    offline_only = _offline_boundary(data)
    summary = f"{state.value}: decision={decision.value}, score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return PaperBrokerSandboxDryRunPlanResult(state, decision, score.overall_score, score, risks, *sections, recommendations, offline_only, summary)


def render_paper_broker_sandbox_dry_run_plan_markdown(result: PaperBrokerSandboxDryRunPlanResult) -> str:
    lines = [
        "# AGIcore Paper Broker Sandbox Dry Run Plan",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Score: {result.plan_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Paper Broker Sandbox Dry Run Plan Sections",
    ]
    sections = (
        result.authorization_gate_readiness,
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
        lines.append(f"- {section.name}: defined={section.defined}, score={section.score}/100, risks={risks}")
        lines.extend(f"  - {detail}" for detail in section.details if detail)
    lines.append("")
    lines.append("# Paper Broker Sandbox Dry Run Plan Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Paper Broker Sandbox Dry Run Plan Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_dry_run_plan_score",
    "define_dry_run_account_policy",
    "define_dry_run_boundaries",
    "define_dry_run_connection_policy",
    "define_dry_run_failure_criteria",
    "define_dry_run_human_supervision_policy",
    "define_dry_run_journal_policy",
    "define_dry_run_kill_switch_policy",
    "define_dry_run_observability_policy",
    "define_dry_run_order_policy",
    "define_dry_run_position_policy",
    "define_dry_run_rollback_policy",
    "define_dry_run_scenario",
    "define_dry_run_scope",
    "define_dry_run_session_limits",
    "define_dry_run_stop_conditions",
    "define_dry_run_success_criteria",
    "detect_dry_run_plan_risks",
    "evaluate_paper_broker_sandbox_dry_run_plan",
    "generate_dry_run_plan_recommendations",
    "render_paper_broker_sandbox_dry_run_plan_markdown",
    "verify_authorization_gate_readiness",
]

