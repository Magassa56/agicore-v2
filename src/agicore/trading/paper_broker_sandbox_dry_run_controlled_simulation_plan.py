"""Offline plan for a future AGIcore Paper Broker Sandbox Dry Run controlled simulation review."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_broker_sandbox_dry_run_controlled_simulation_plan_models import (
    PaperBrokerSandboxDryRunControlledSimulationPlanDecision,
    PaperBrokerSandboxDryRunControlledSimulationPlanInput,
    PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation,
    PaperBrokerSandboxDryRunControlledSimulationPlanResult,
    PaperBrokerSandboxDryRunControlledSimulationPlanRisk,
    PaperBrokerSandboxDryRunControlledSimulationPlanScore,
    PaperBrokerSandboxDryRunControlledSimulationPlanSection,
    PaperBrokerSandboxDryRunControlledSimulationPlanState,
)


def _coerce_input(
    data: PaperBrokerSandboxDryRunControlledSimulationPlanInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunControlledSimulationPlanInput:
    if isinstance(data, PaperBrokerSandboxDryRunControlledSimulationPlanInput):
        return data
    allowed = {field.name for field in fields(PaperBrokerSandboxDryRunControlledSimulationPlanInput)}
    payload = {key: value for key, value in dict(data).items() if key in allowed}
    return PaperBrokerSandboxDryRunControlledSimulationPlanInput(**payload)


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


def _upstream_items(data: PaperBrokerSandboxDryRunControlledSimulationPlanInput) -> tuple[Any, ...]:
    return (
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


def _upstream_risks(data: PaperBrokerSandboxDryRunControlledSimulationPlanInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperBrokerSandboxDryRunControlledSimulationPlanInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _offline_boundary(data: PaperBrokerSandboxDryRunControlledSimulationPlanInput) -> bool:
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
        and data.no_controlled_simulation_execution is True
        and data.no_real_order is True
        and data.no_real_account_access is True
        and data.paper_broker_sandbox_dry_run_controlled_simulation_requested is not True
        and data.paper_broker_sandbox_dry_run_controlled_simulation_execution_requested is not True
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
            "CONTROLLED_SIMULATION",
            "SIMULATION_EXECUTION",
            "API_KEY",
            "CREDENTIAL",
        )
    )


def _section(
    name: str,
    score: int,
    risk: PaperBrokerSandboxDryRunControlledSimulationPlanRisk,
    failed: bool,
    evidence: tuple[str, ...] = (),
) -> PaperBrokerSandboxDryRunControlledSimulationPlanSection:
    risks = (risk,) if failed or score < 85 else ()
    return PaperBrokerSandboxDryRunControlledSimulationPlanSection(name, _clamp(score), not risks and score >= 85, risks, evidence)


def _define_flag(
    data: PaperBrokerSandboxDryRunControlledSimulationPlanInput,
    name: str,
    defined: bool | None,
    complete: bool | None,
    score: int | None,
    risk: PaperBrokerSandboxDryRunControlledSimulationPlanRisk,
    upstream_needles: tuple[str, ...] = (),
    extra_ok: bool = True,
) -> PaperBrokerSandboxDryRunControlledSimulationPlanSection:
    ok = _confirmed(defined, complete) and extra_ok
    failed = not ok or _has_upstream_risk(data, *upstream_needles)
    return _section(name, score if score is not None else _bool_score(ok), risk, failed)


def verify_execution_authorization_gate_readiness(
    data: PaperBrokerSandboxDryRunControlledSimulationPlanInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunControlledSimulationPlanSection:
    data = _coerce_input(data)
    gate = data.paper_broker_sandbox_dry_run_execution_authorization_gate
    gate_state_ok = _state_contains(
        gate,
        "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_PLAN",
        "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION_GATE",
    )
    gate_approved = (
        data.execution_authorization_gate_approved is not False
        and data.execution_authorization_gate_reviewed is not False
        and (data.execution_authorization_gate_approved is True or gate_state_ok)
    )
    failed = not gate_approved or _has_upstream_risk(
        data,
        "EXECUTION_AUTHORIZATION_GATE_NOT_APPROVED",
        "EXECUTION_REVIEW_NOT_APPROVED",
        "PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION",
        "BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION",
    )
    score = data.execution_authorization_gate_readiness_score if data.execution_authorization_gate_readiness_score is not None else _bool_score(gate_approved)
    return _section(
        "execution_authorization_gate_readiness",
        score,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.EXECUTION_AUTHORIZATION_GATE_NOT_APPROVED,
        failed,
        (_value(_get(gate, "state")), _value(_get(gate, "decision"))),
    )


def define_controlled_simulation_scope(data: PaperBrokerSandboxDryRunControlledSimulationPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunControlledSimulationPlanSection:
    data = _coerce_input(data)
    return _define_flag(data, "controlled_simulation_scope", data.controlled_simulation_scope_defined, data.controlled_simulation_scope_clear, data.controlled_simulation_scope_score, PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_SCOPE_UNCLEAR, ("SCOPE",))


def define_controlled_simulation_boundaries(data: PaperBrokerSandboxDryRunControlledSimulationPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunControlledSimulationPlanSection:
    data = _coerce_input(data)
    return _define_flag(data, "controlled_simulation_boundaries", data.controlled_simulation_boundaries_defined, data.controlled_simulation_boundaries_complete, data.controlled_simulation_boundaries_score, PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_BOUNDARY_GAP, ("BOUNDARY", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK"), _offline_boundary(data))


def define_controlled_simulation_scenario(data: PaperBrokerSandboxDryRunControlledSimulationPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunControlledSimulationPlanSection:
    data = _coerce_input(data)
    return _define_flag(data, "controlled_simulation_scenario", data.controlled_simulation_scenario_defined, data.controlled_simulation_scenario_complete, data.controlled_simulation_scenario_score, PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_SCENARIO_UNDEFINED, ("SCENARIO",))


def define_controlled_simulation_session_limits(data: PaperBrokerSandboxDryRunControlledSimulationPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunControlledSimulationPlanSection:
    data = _coerce_input(data)
    return _define_flag(data, "controlled_simulation_session_limits", data.controlled_simulation_session_limits_defined, data.controlled_simulation_session_limits_complete, data.controlled_simulation_session_limits_score, PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_SESSION_LIMIT_GAP, ("LIMIT", "CAP"))


def define_controlled_simulation_connection_policy(data: PaperBrokerSandboxDryRunControlledSimulationPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunControlledSimulationPlanSection:
    data = _coerce_input(data)
    extra_ok = data.no_http_transport is True and data.no_websocket_transport is True and data.no_socket_transport is True and data.no_external_api is True
    return _define_flag(data, "controlled_simulation_connection_policy", data.controlled_simulation_connection_policy_defined, data.controlled_simulation_connection_policy_complete, data.controlled_simulation_connection_policy_score, PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_CONNECTION_POLICY_GAP, ("CONNECTION", "NETWORK", "HTTP", "WEBSOCKET", "SOCKET", "API_ACCESS"), extra_ok)


def define_controlled_simulation_order_policy(data: PaperBrokerSandboxDryRunControlledSimulationPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunControlledSimulationPlanSection:
    data = _coerce_input(data)
    extra_ok = data.no_real_order is True and data.no_live_execution is True and data.no_dry_run_execution is True
    return _define_flag(data, "controlled_simulation_order_policy", data.controlled_simulation_order_policy_defined, data.controlled_simulation_order_policy_complete, data.controlled_simulation_order_policy_score, PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_ORDER_POLICY_GAP, ("ORDER", "EXECUTION_LEAK", "REAL_ORDER", "LIVE_EXECUTION"), extra_ok)


def define_controlled_simulation_position_policy(data: PaperBrokerSandboxDryRunControlledSimulationPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunControlledSimulationPlanSection:
    data = _coerce_input(data)
    return _define_flag(data, "controlled_simulation_position_policy", data.controlled_simulation_position_policy_defined, data.controlled_simulation_position_policy_complete, data.controlled_simulation_position_policy_score, PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_POSITION_POLICY_GAP, ("POSITION", "RECONCILIATION"))


def define_controlled_simulation_account_policy(data: PaperBrokerSandboxDryRunControlledSimulationPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunControlledSimulationPlanSection:
    data = _coerce_input(data)
    extra_ok = data.no_api_key_read is True and data.no_real_account_access is True
    return _define_flag(data, "controlled_simulation_account_policy", data.controlled_simulation_account_policy_defined, data.controlled_simulation_account_policy_complete, data.controlled_simulation_account_policy_score, PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_ACCOUNT_POLICY_GAP, ("ACCOUNT", "REAL_ACCOUNT", "CREDENTIAL", "API_KEY"), extra_ok)


def define_controlled_simulation_observability_policy(data: PaperBrokerSandboxDryRunControlledSimulationPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunControlledSimulationPlanSection:
    data = _coerce_input(data)
    return _define_flag(data, "controlled_simulation_observability_policy", data.controlled_simulation_observability_policy_defined, data.controlled_simulation_observability_policy_complete, data.controlled_simulation_observability_policy_score, PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_OBSERVABILITY_GAP, ("OBSERVABILITY",))


def define_controlled_simulation_rollback_policy(data: PaperBrokerSandboxDryRunControlledSimulationPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunControlledSimulationPlanSection:
    data = _coerce_input(data)
    return _define_flag(data, "controlled_simulation_rollback_policy", data.controlled_simulation_rollback_policy_defined, data.controlled_simulation_rollback_policy_complete, data.controlled_simulation_rollback_policy_score, PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_ROLLBACK_GAP, ("ROLLBACK",))


def define_controlled_simulation_kill_switch_policy(data: PaperBrokerSandboxDryRunControlledSimulationPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunControlledSimulationPlanSection:
    data = _coerce_input(data)
    return _define_flag(data, "controlled_simulation_kill_switch_policy", data.controlled_simulation_kill_switch_policy_defined, data.controlled_simulation_kill_switch_policy_complete, data.controlled_simulation_kill_switch_policy_score, PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_KILL_SWITCH_GAP, ("KILL_SWITCH",))


def define_controlled_simulation_human_supervision_policy(data: PaperBrokerSandboxDryRunControlledSimulationPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunControlledSimulationPlanSection:
    data = _coerce_input(data)
    return _define_flag(data, "controlled_simulation_human_supervision_policy", data.controlled_simulation_human_supervision_policy_defined, data.controlled_simulation_human_supervision_policy_complete, data.controlled_simulation_human_supervision_policy_score, PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_HUMAN_SUPERVISION_GAP, ("HUMAN", "SUPERVISION", "OPERATOR"))


def define_controlled_simulation_journal_policy(data: PaperBrokerSandboxDryRunControlledSimulationPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunControlledSimulationPlanSection:
    data = _coerce_input(data)
    return _define_flag(data, "controlled_simulation_journal_policy", data.controlled_simulation_journal_policy_defined, data.controlled_simulation_journal_policy_complete, data.controlled_simulation_journal_policy_score, PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_JOURNAL_GAP, ("JOURNAL", "AUDIT_TRAIL", "TRACE"))


def define_controlled_simulation_stop_conditions(data: PaperBrokerSandboxDryRunControlledSimulationPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunControlledSimulationPlanSection:
    data = _coerce_input(data)
    return _define_flag(data, "controlled_simulation_stop_conditions", data.controlled_simulation_stop_conditions_defined, data.controlled_simulation_stop_conditions_complete, data.controlled_simulation_stop_conditions_score, PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_STOP_CONDITION_GAP, ("STOP_CONDITION", "HALT", "EMERGENCY_STOP"))


def define_controlled_simulation_abort_conditions(data: PaperBrokerSandboxDryRunControlledSimulationPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunControlledSimulationPlanSection:
    data = _coerce_input(data)
    return _define_flag(data, "controlled_simulation_abort_conditions", data.controlled_simulation_abort_conditions_defined, data.controlled_simulation_abort_conditions_complete, data.controlled_simulation_abort_conditions_score, PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_ABORT_CONDITION_GAP, ("ABORT", "CANCEL", "EMERGENCY_ABORT"))


def define_controlled_simulation_success_criteria(data: PaperBrokerSandboxDryRunControlledSimulationPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunControlledSimulationPlanSection:
    data = _coerce_input(data)
    return _define_flag(data, "controlled_simulation_success_criteria", data.controlled_simulation_success_criteria_defined, data.controlled_simulation_success_criteria_complete, data.controlled_simulation_success_criteria_score, PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_SUCCESS_FAILURE_CRITERIA_GAP, ("SUCCESS_CRITERIA",))


def define_controlled_simulation_failure_criteria(data: PaperBrokerSandboxDryRunControlledSimulationPlanInput | Mapping[str, Any]) -> PaperBrokerSandboxDryRunControlledSimulationPlanSection:
    data = _coerce_input(data)
    return _define_flag(data, "controlled_simulation_failure_criteria", data.controlled_simulation_failure_criteria_defined, data.controlled_simulation_failure_criteria_complete, data.controlled_simulation_failure_criteria_score, PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_SUCCESS_FAILURE_CRITERIA_GAP, ("FAILURE_CRITERIA",))


def _all_sections(data: PaperBrokerSandboxDryRunControlledSimulationPlanInput) -> tuple[PaperBrokerSandboxDryRunControlledSimulationPlanSection, ...]:
    return (
        verify_execution_authorization_gate_readiness(data),
        define_controlled_simulation_scope(data),
        define_controlled_simulation_boundaries(data),
        define_controlled_simulation_scenario(data),
        define_controlled_simulation_session_limits(data),
        define_controlled_simulation_connection_policy(data),
        define_controlled_simulation_order_policy(data),
        define_controlled_simulation_position_policy(data),
        define_controlled_simulation_account_policy(data),
        define_controlled_simulation_observability_policy(data),
        define_controlled_simulation_rollback_policy(data),
        define_controlled_simulation_kill_switch_policy(data),
        define_controlled_simulation_human_supervision_policy(data),
        define_controlled_simulation_journal_policy(data),
        define_controlled_simulation_stop_conditions(data),
        define_controlled_simulation_abort_conditions(data),
        define_controlled_simulation_success_criteria(data),
        define_controlled_simulation_failure_criteria(data),
    )


def detect_controlled_simulation_plan_risks(
    data: PaperBrokerSandboxDryRunControlledSimulationPlanInput | Mapping[str, Any],
    *sections: PaperBrokerSandboxDryRunControlledSimulationPlanSection,
) -> tuple[PaperBrokerSandboxDryRunControlledSimulationPlanRisk, ...]:
    data = _coerce_input(data)
    if not sections:
        sections = _all_sections(data)
    risks: list[PaperBrokerSandboxDryRunControlledSimulationPlanRisk] = []
    for section in sections:
        risks.extend(section.risks)
    if (
        data.paper_broker_sandbox_dry_run_controlled_simulation_plan_requested is not True
        or data.paper_broker_sandbox_dry_run_controlled_simulation_requested is True
        or data.paper_broker_sandbox_dry_run_controlled_simulation_execution_requested is True
        or not _offline_boundary(data)
    ):
        risks.append(PaperBrokerSandboxDryRunControlledSimulationPlanRisk.PREMATURE_PAPER_BROKER_SANDBOX_CONTROLLED_SIMULATION_EXECUTION)
    return _dedupe(risks)


def compute_controlled_simulation_plan_score(
    data: PaperBrokerSandboxDryRunControlledSimulationPlanInput | Mapping[str, Any],
    risks: tuple[PaperBrokerSandboxDryRunControlledSimulationPlanRisk, ...] = (),
    *sections: PaperBrokerSandboxDryRunControlledSimulationPlanSection,
) -> PaperBrokerSandboxDryRunControlledSimulationPlanScore:
    data = _coerce_input(data)
    if not sections:
        sections = _all_sections(data)
    scores = tuple(section.score for section in sections)
    overall = _clamp(_average(scores) - min(90, len(set(risks)) * 5))
    for risk, cap in {
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.EXECUTION_AUTHORIZATION_GATE_NOT_APPROVED: 50,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_SCOPE_UNCLEAR: 60,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_BOUNDARY_GAP: 45,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_SCENARIO_UNDEFINED: 60,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_SESSION_LIMIT_GAP: 55,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_CONNECTION_POLICY_GAP: 50,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_ORDER_POLICY_GAP: 50,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_POSITION_POLICY_GAP: 60,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_ACCOUNT_POLICY_GAP: 45,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_OBSERVABILITY_GAP: 60,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_ROLLBACK_GAP: 55,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_KILL_SWITCH_GAP: 50,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_HUMAN_SUPERVISION_GAP: 45,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_JOURNAL_GAP: 60,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_STOP_CONDITION_GAP: 45,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_ABORT_CONDITION_GAP: 45,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_SUCCESS_FAILURE_CRITERIA_GAP: 50,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.PREMATURE_PAPER_BROKER_SANDBOX_CONTROLLED_SIMULATION_EXECUTION: 40,
    }.items():
        if risk in risks:
            overall = min(overall, cap)
    return PaperBrokerSandboxDryRunControlledSimulationPlanScore(overall, *scores)


def _select_decision(
    risks: tuple[PaperBrokerSandboxDryRunControlledSimulationPlanRisk, ...],
    score: int,
) -> PaperBrokerSandboxDryRunControlledSimulationPlanDecision:
    if PaperBrokerSandboxDryRunControlledSimulationPlanRisk.PREMATURE_PAPER_BROKER_SANDBOX_CONTROLLED_SIMULATION_EXECUTION in risks or score < 45:
        return PaperBrokerSandboxDryRunControlledSimulationPlanDecision.BLOCK_PAPER_BROKER_SANDBOX_CONTROLLED_SIMULATION
    if PaperBrokerSandboxDryRunControlledSimulationPlanRisk.EXECUTION_AUTHORIZATION_GATE_NOT_APPROVED in risks:
        return PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_EXECUTION_AUTHORIZATION_GATE_FIXES
    if PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_SCOPE_UNCLEAR in risks:
        return PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_SCOPE_FIXES
    if PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_BOUNDARY_GAP in risks:
        return PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_BOUNDARY_FIXES
    if PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_SCENARIO_UNDEFINED in risks:
        return PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_SCENARIO_FIXES
    if PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_SESSION_LIMIT_GAP in risks:
        return PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_SESSION_LIMIT_FIXES
    if PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_CONNECTION_POLICY_GAP in risks:
        return PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_CONNECTION_POLICY_FIXES
    if PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_ORDER_POLICY_GAP in risks:
        return PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_ORDER_POLICY_FIXES
    if PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_POSITION_POLICY_GAP in risks:
        return PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_POSITION_POLICY_FIXES
    if PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_ACCOUNT_POLICY_GAP in risks:
        return PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_ACCOUNT_POLICY_FIXES
    if PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_OBSERVABILITY_GAP in risks:
        return PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_OBSERVABILITY_FIXES
    if PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_ROLLBACK_GAP in risks:
        return PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_ROLLBACK_FIXES
    if PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_KILL_SWITCH_GAP in risks:
        return PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_KILL_SWITCH_FIXES
    if PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_HUMAN_SUPERVISION_GAP in risks:
        return PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_SUPERVISION_FIXES
    if PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_JOURNAL_GAP in risks:
        return PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_JOURNAL_FIXES
    if (
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_STOP_CONDITION_GAP in risks
        or PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_SUCCESS_FAILURE_CRITERIA_GAP in risks
    ):
        return PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_STOP_CONDITION_FIXES
    if PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_ABORT_CONDITION_GAP in risks:
        return PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_ABORT_CONDITION_FIXES
    if risks:
        return PaperBrokerSandboxDryRunControlledSimulationPlanDecision.REQUIRE_BOUNDARY_FIXES
    return PaperBrokerSandboxDryRunControlledSimulationPlanDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_PLAN


def _select_state(
    decision: PaperBrokerSandboxDryRunControlledSimulationPlanDecision,
    score: int,
) -> PaperBrokerSandboxDryRunControlledSimulationPlanState:
    if decision == PaperBrokerSandboxDryRunControlledSimulationPlanDecision.BLOCK_PAPER_BROKER_SANDBOX_CONTROLLED_SIMULATION:
        return PaperBrokerSandboxDryRunControlledSimulationPlanState.NOT_READY
    if decision != PaperBrokerSandboxDryRunControlledSimulationPlanDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_PLAN:
        return (
            PaperBrokerSandboxDryRunControlledSimulationPlanState.CONTROLLED_SIMULATION_PLAN_REVIEW_REQUIRED
            if score < 82
            else PaperBrokerSandboxDryRunControlledSimulationPlanState.PARTIALLY_PLANNED
        )
    if score >= 95:
        return PaperBrokerSandboxDryRunControlledSimulationPlanState.READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_REVIEW
    return PaperBrokerSandboxDryRunControlledSimulationPlanState.CONTROLLED_SIMULATION_PLAN_READY


def generate_controlled_simulation_plan_recommendations(
    risks: tuple[PaperBrokerSandboxDryRunControlledSimulationPlanRisk, ...],
    decision: PaperBrokerSandboxDryRunControlledSimulationPlanDecision | None = None,
) -> tuple[PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation, ...]:
    recommendations: list[PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation] = []
    if risks:
        recommendations.append(PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.HOLD_PAPER_BROKER_SANDBOX_CONTROLLED_SIMULATION_REVIEW)
    mapping = {
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.EXECUTION_AUTHORIZATION_GATE_NOT_APPROVED: PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.APPROVE_EXECUTION_AUTHORIZATION_GATE_FIRST,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_SCOPE_UNCLEAR: PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.CLARIFY_CONTROLLED_SIMULATION_SCOPE,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_BOUNDARY_GAP: PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.COMPLETE_CONTROLLED_SIMULATION_BOUNDARIES,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_SCENARIO_UNDEFINED: PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.COMPLETE_CONTROLLED_SIMULATION_SCENARIO,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_SESSION_LIMIT_GAP: PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.COMPLETE_CONTROLLED_SIMULATION_SESSION_LIMITS,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_CONNECTION_POLICY_GAP: PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.COMPLETE_CONTROLLED_SIMULATION_CONNECTION_POLICY,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_ORDER_POLICY_GAP: PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.COMPLETE_CONTROLLED_SIMULATION_ORDER_POLICY,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_POSITION_POLICY_GAP: PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.COMPLETE_CONTROLLED_SIMULATION_POSITION_POLICY,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_ACCOUNT_POLICY_GAP: PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.COMPLETE_CONTROLLED_SIMULATION_ACCOUNT_POLICY,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_OBSERVABILITY_GAP: PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.COMPLETE_CONTROLLED_SIMULATION_OBSERVABILITY_POLICY,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_ROLLBACK_GAP: PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.COMPLETE_CONTROLLED_SIMULATION_ROLLBACK_POLICY,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_KILL_SWITCH_GAP: PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.COMPLETE_CONTROLLED_SIMULATION_KILL_SWITCH_POLICY,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_HUMAN_SUPERVISION_GAP: PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.COMPLETE_CONTROLLED_SIMULATION_HUMAN_SUPERVISION_POLICY,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_JOURNAL_GAP: PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.COMPLETE_CONTROLLED_SIMULATION_JOURNAL_POLICY,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_STOP_CONDITION_GAP: PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.COMPLETE_CONTROLLED_SIMULATION_STOP_CONDITIONS,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_ABORT_CONDITION_GAP: PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.COMPLETE_CONTROLLED_SIMULATION_ABORT_CONDITIONS,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.CONTROLLED_SIMULATION_SUCCESS_FAILURE_CRITERIA_GAP: PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.COMPLETE_CONTROLLED_SIMULATION_SUCCESS_FAILURE_CRITERIA,
        PaperBrokerSandboxDryRunControlledSimulationPlanRisk.PREMATURE_PAPER_BROKER_SANDBOX_CONTROLLED_SIMULATION_EXECUTION: PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.DELAY_PAPER_BROKER_SANDBOX_CONTROLLED_SIMULATION_EXECUTION,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.RUN_PAPER_BROKER_SANDBOX_CONTROLLED_SIMULATION_PLAN_SUITE)
    if decision == PaperBrokerSandboxDryRunControlledSimulationPlanDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_PLAN:
        recommendations.append(PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_REVIEW)
    return _dedupe(recommendations)


def evaluate_paper_broker_sandbox_dry_run_controlled_simulation_plan(
    data: PaperBrokerSandboxDryRunControlledSimulationPlanInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunControlledSimulationPlanResult:
    data = _coerce_input(data)
    sections = _all_sections(data)
    risks = detect_controlled_simulation_plan_risks(data, *sections)
    score = compute_controlled_simulation_plan_score(data, risks, *sections)
    decision = _select_decision(risks, score.overall_score)
    state = _select_state(decision, score.overall_score)
    recommendations = generate_controlled_simulation_plan_recommendations(risks, decision)
    offline_only = _offline_boundary(data)
    summary = f"{state.value}: decision={decision.value}, score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return PaperBrokerSandboxDryRunControlledSimulationPlanResult(state, decision, score.overall_score, score, risks, *sections, recommendations, offline_only, summary)


def render_paper_broker_sandbox_dry_run_controlled_simulation_plan_markdown(
    result: PaperBrokerSandboxDryRunControlledSimulationPlanResult,
) -> str:
    lines = [
        "# AGIcore Paper Broker Sandbox Dry Run Controlled Simulation Plan",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Score: {result.plan_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Paper Broker Sandbox Dry Run Controlled Simulation Plan Sections",
    ]
    sections = (
        result.execution_authorization_gate_readiness,
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
        result.controlled_simulation_success_criteria,
        result.controlled_simulation_failure_criteria,
    )
    for section in sections:
        risks = ", ".join(risk.value for risk in section.risks) or "none"
        lines.append(f"- {section.name}: passed={section.passed}, score={section.score}/100, risks={risks}")
        lines.extend(f"  - {item}" for item in section.evidence if item)
    lines.append("")
    lines.append("# Paper Broker Sandbox Dry Run Controlled Simulation Plan Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Paper Broker Sandbox Dry Run Controlled Simulation Plan Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_controlled_simulation_plan_score",
    "define_controlled_simulation_abort_conditions",
    "define_controlled_simulation_account_policy",
    "define_controlled_simulation_boundaries",
    "define_controlled_simulation_connection_policy",
    "define_controlled_simulation_failure_criteria",
    "define_controlled_simulation_human_supervision_policy",
    "define_controlled_simulation_journal_policy",
    "define_controlled_simulation_kill_switch_policy",
    "define_controlled_simulation_observability_policy",
    "define_controlled_simulation_order_policy",
    "define_controlled_simulation_position_policy",
    "define_controlled_simulation_rollback_policy",
    "define_controlled_simulation_scenario",
    "define_controlled_simulation_scope",
    "define_controlled_simulation_session_limits",
    "define_controlled_simulation_stop_conditions",
    "define_controlled_simulation_success_criteria",
    "detect_controlled_simulation_plan_risks",
    "evaluate_paper_broker_sandbox_dry_run_controlled_simulation_plan",
    "generate_controlled_simulation_plan_recommendations",
    "render_paper_broker_sandbox_dry_run_controlled_simulation_plan_markdown",
    "verify_execution_authorization_gate_readiness",
]
