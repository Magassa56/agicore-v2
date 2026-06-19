"""Offline authorization gate before a future AGIcore Paper Broker Sandbox Dry Run controlled simulation plan."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_broker_sandbox_dry_run_execution_authorization_gate_models import (
    PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision,
    PaperBrokerSandboxDryRunExecutionAuthorizationGateInput,
    PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation,
    PaperBrokerSandboxDryRunExecutionAuthorizationGateResult,
    PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk,
    PaperBrokerSandboxDryRunExecutionAuthorizationGateScore,
    PaperBrokerSandboxDryRunExecutionAuthorizationGateSection,
    PaperBrokerSandboxDryRunExecutionAuthorizationGateState,
)


def _coerce_input(
    data: PaperBrokerSandboxDryRunExecutionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunExecutionAuthorizationGateInput:
    if isinstance(data, PaperBrokerSandboxDryRunExecutionAuthorizationGateInput):
        return data
    allowed = {field.name for field in fields(PaperBrokerSandboxDryRunExecutionAuthorizationGateInput)}
    payload = {key: value for key, value in dict(data).items() if key in allowed}
    return PaperBrokerSandboxDryRunExecutionAuthorizationGateInput(**payload)


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


def _upstream_items(data: PaperBrokerSandboxDryRunExecutionAuthorizationGateInput) -> tuple[Any, ...]:
    return (
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


def _upstream_risks(data: PaperBrokerSandboxDryRunExecutionAuthorizationGateInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperBrokerSandboxDryRunExecutionAuthorizationGateInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _offline_boundary(data: PaperBrokerSandboxDryRunExecutionAuthorizationGateInput) -> bool:
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
        and data.paper_broker_sandbox_dry_run_execution_requested is not True
        and data.paper_broker_sandbox_dry_run_controlled_simulation_requested is not True
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
    risk: PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk,
    failed: bool,
    evidence: tuple[str, ...] = (),
) -> PaperBrokerSandboxDryRunExecutionAuthorizationGateSection:
    risks = (risk,) if failed or score < 85 else ()
    return PaperBrokerSandboxDryRunExecutionAuthorizationGateSection(name, _clamp(score), not risks and score >= 85, risks, evidence)


def _authorization_flag(
    data: PaperBrokerSandboxDryRunExecutionAuthorizationGateInput,
    name: str,
    reviewed: bool | None,
    authorized: bool | None,
    score: int | None,
    risk: PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk,
    upstream_needles: tuple[str, ...] = (),
    extra_ok: bool = True,
) -> PaperBrokerSandboxDryRunExecutionAuthorizationGateSection:
    ok = _confirmed(reviewed, authorized) and extra_ok
    failed = not ok or _has_upstream_risk(data, *upstream_needles)
    return _section(name, score if score is not None else _bool_score(ok), risk, failed)


def verify_execution_review_approval(
    data: PaperBrokerSandboxDryRunExecutionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunExecutionAuthorizationGateSection:
    data = _coerce_input(data)
    review = data.paper_broker_sandbox_dry_run_execution_review
    review_state_ok = _state_contains(
        review,
        "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION_GATE",
        "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_REVIEW",
    )
    review_approved = (
        data.execution_review_approved is not False
        and data.execution_review_reviewed is not False
        and (data.execution_review_approved is True or review_state_ok)
    )
    failed = not review_approved or _has_upstream_risk(
        data,
        "EXECUTION_REVIEW_NOT_APPROVED",
        "PRE_EXECUTION_CHECK_NOT_APPROVED",
        "PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_REAL_EXECUTION",
        "BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION",
    )
    score = data.execution_review_approval_score if data.execution_review_approval_score is not None else _bool_score(review_approved)
    return _section(
        "execution_review_approval",
        score,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_REVIEW_NOT_APPROVED,
        failed,
        (_value(_get(review, "state")), _value(_get(review, "decision"))),
    )


def verify_execution_authorization_scope(
    data: PaperBrokerSandboxDryRunExecutionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunExecutionAuthorizationGateSection:
    data = _coerce_input(data)
    return _authorization_flag(
        data,
        "execution_authorization_scope",
        data.execution_authorization_scope_reviewed,
        data.execution_authorization_scope_clear,
        data.execution_authorization_scope_score,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_AUTHORIZATION_SCOPE_UNCLEAR,
        ("SCOPE",),
    )


def verify_execution_authorization_boundaries(
    data: PaperBrokerSandboxDryRunExecutionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunExecutionAuthorizationGateSection:
    data = _coerce_input(data)
    return _authorization_flag(
        data,
        "execution_authorization_boundaries",
        data.execution_authorization_boundaries_reviewed,
        data.execution_authorization_boundaries_complete,
        data.execution_authorization_boundaries_score,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_AUTHORIZATION_BOUNDARY_GAP,
        ("BOUNDARY", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK"),
        _offline_boundary(data),
    )


def verify_execution_scenario_authorization(
    data: PaperBrokerSandboxDryRunExecutionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunExecutionAuthorizationGateSection:
    data = _coerce_input(data)
    return _authorization_flag(
        data,
        "execution_scenario_authorization",
        data.execution_scenario_authorization_reviewed,
        data.execution_scenario_authorization_complete,
        data.execution_scenario_authorization_score,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_SCENARIO_AUTHORIZATION_GAP,
        ("SCENARIO",),
    )


def verify_execution_session_limit_authorization(
    data: PaperBrokerSandboxDryRunExecutionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunExecutionAuthorizationGateSection:
    data = _coerce_input(data)
    return _authorization_flag(
        data,
        "execution_session_limit_authorization",
        data.execution_session_limit_authorization_reviewed,
        data.execution_session_limit_authorization_complete,
        data.execution_session_limit_authorization_score,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_SESSION_LIMIT_AUTHORIZATION_GAP,
        ("LIMIT", "CAP"),
    )


def verify_execution_connection_authorization(
    data: PaperBrokerSandboxDryRunExecutionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunExecutionAuthorizationGateSection:
    data = _coerce_input(data)
    extra_ok = data.no_http_transport is True and data.no_websocket_transport is True and data.no_socket_transport is True and data.no_external_api is True
    return _authorization_flag(
        data,
        "execution_connection_authorization",
        data.execution_connection_authorization_reviewed,
        data.execution_connection_authorization_complete,
        data.execution_connection_authorization_score,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_CONNECTION_AUTHORIZATION_GAP,
        ("CONNECTION", "NETWORK", "HTTP", "WEBSOCKET", "SOCKET", "API_ACCESS"),
        extra_ok,
    )


def verify_execution_order_authorization(
    data: PaperBrokerSandboxDryRunExecutionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunExecutionAuthorizationGateSection:
    data = _coerce_input(data)
    extra_ok = data.no_real_order is True and data.no_live_execution is True and data.no_dry_run_execution is True
    return _authorization_flag(
        data,
        "execution_order_authorization",
        data.execution_order_authorization_reviewed,
        data.execution_order_authorization_complete,
        data.execution_order_authorization_score,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_ORDER_AUTHORIZATION_GAP,
        ("ORDER", "EXECUTION_LEAK", "REAL_ORDER", "LIVE_EXECUTION"),
        extra_ok,
    )


def verify_execution_position_authorization(
    data: PaperBrokerSandboxDryRunExecutionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunExecutionAuthorizationGateSection:
    data = _coerce_input(data)
    return _authorization_flag(
        data,
        "execution_position_authorization",
        data.execution_position_authorization_reviewed,
        data.execution_position_authorization_complete,
        data.execution_position_authorization_score,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_POSITION_AUTHORIZATION_GAP,
        ("POSITION", "RECONCILIATION"),
    )


def verify_execution_account_authorization(
    data: PaperBrokerSandboxDryRunExecutionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunExecutionAuthorizationGateSection:
    data = _coerce_input(data)
    extra_ok = data.no_api_key_read is True and data.no_real_account_access is True
    return _authorization_flag(
        data,
        "execution_account_authorization",
        data.execution_account_authorization_reviewed,
        data.execution_account_authorization_complete,
        data.execution_account_authorization_score,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_ACCOUNT_AUTHORIZATION_GAP,
        ("ACCOUNT", "REAL_ACCOUNT", "CREDENTIAL", "API_KEY"),
        extra_ok,
    )


def verify_execution_observability_authorization(
    data: PaperBrokerSandboxDryRunExecutionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunExecutionAuthorizationGateSection:
    data = _coerce_input(data)
    return _authorization_flag(
        data,
        "execution_observability_authorization",
        data.execution_observability_authorization_reviewed,
        data.execution_observability_authorization_complete,
        data.execution_observability_authorization_score,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_OBSERVABILITY_AUTHORIZATION_GAP,
        ("OBSERVABILITY",),
    )


def verify_execution_rollback_authorization(
    data: PaperBrokerSandboxDryRunExecutionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunExecutionAuthorizationGateSection:
    data = _coerce_input(data)
    return _authorization_flag(
        data,
        "execution_rollback_authorization",
        data.execution_rollback_authorization_reviewed,
        data.execution_rollback_authorization_complete,
        data.execution_rollback_authorization_score,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_ROLLBACK_AUTHORIZATION_GAP,
        ("ROLLBACK",),
    )


def verify_execution_kill_switch_authorization(
    data: PaperBrokerSandboxDryRunExecutionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunExecutionAuthorizationGateSection:
    data = _coerce_input(data)
    return _authorization_flag(
        data,
        "execution_kill_switch_authorization",
        data.execution_kill_switch_authorization_reviewed,
        data.execution_kill_switch_authorization_complete,
        data.execution_kill_switch_authorization_score,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_KILL_SWITCH_AUTHORIZATION_GAP,
        ("KILL_SWITCH",),
    )


def verify_execution_human_supervision_authorization(
    data: PaperBrokerSandboxDryRunExecutionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunExecutionAuthorizationGateSection:
    data = _coerce_input(data)
    return _authorization_flag(
        data,
        "execution_human_supervision_authorization",
        data.execution_human_supervision_authorization_reviewed,
        data.execution_human_supervision_authorization_complete,
        data.execution_human_supervision_authorization_score,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_HUMAN_SUPERVISION_AUTHORIZATION_GAP,
        ("HUMAN", "SUPERVISION", "OPERATOR"),
    )


def verify_execution_journal_authorization(
    data: PaperBrokerSandboxDryRunExecutionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunExecutionAuthorizationGateSection:
    data = _coerce_input(data)
    return _authorization_flag(
        data,
        "execution_journal_authorization",
        data.execution_journal_authorization_reviewed,
        data.execution_journal_authorization_complete,
        data.execution_journal_authorization_score,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_JOURNAL_AUTHORIZATION_GAP,
        ("JOURNAL", "AUDIT_TRAIL", "TRACE"),
    )


def verify_execution_stop_condition_authorization(
    data: PaperBrokerSandboxDryRunExecutionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunExecutionAuthorizationGateSection:
    data = _coerce_input(data)
    return _authorization_flag(
        data,
        "execution_stop_condition_authorization",
        data.execution_stop_condition_authorization_reviewed,
        data.execution_stop_condition_authorization_complete,
        data.execution_stop_condition_authorization_score,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_STOP_CONDITION_AUTHORIZATION_GAP,
        ("STOP_CONDITION", "HALT", "EMERGENCY_STOP"),
    )


def verify_execution_abort_condition_authorization(
    data: PaperBrokerSandboxDryRunExecutionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunExecutionAuthorizationGateSection:
    data = _coerce_input(data)
    return _authorization_flag(
        data,
        "execution_abort_condition_authorization",
        data.execution_abort_condition_authorization_reviewed,
        data.execution_abort_condition_authorization_complete,
        data.execution_abort_condition_authorization_score,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_ABORT_CONDITION_AUTHORIZATION_GAP,
        ("ABORT", "CANCEL", "EMERGENCY_ABORT"),
    )


def verify_execution_success_failure_authorization(
    data: PaperBrokerSandboxDryRunExecutionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunExecutionAuthorizationGateSection:
    data = _coerce_input(data)
    return _authorization_flag(
        data,
        "execution_success_failure_authorization",
        data.execution_success_failure_authorization_reviewed,
        data.execution_success_failure_authorization_complete,
        data.execution_success_failure_authorization_score,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_SUCCESS_FAILURE_AUTHORIZATION_GAP,
        ("SUCCESS_CRITERIA", "FAILURE_CRITERIA"),
    )


def _all_sections(
    data: PaperBrokerSandboxDryRunExecutionAuthorizationGateInput,
) -> tuple[PaperBrokerSandboxDryRunExecutionAuthorizationGateSection, ...]:
    return (
        verify_execution_review_approval(data),
        verify_execution_authorization_scope(data),
        verify_execution_authorization_boundaries(data),
        verify_execution_scenario_authorization(data),
        verify_execution_session_limit_authorization(data),
        verify_execution_connection_authorization(data),
        verify_execution_order_authorization(data),
        verify_execution_position_authorization(data),
        verify_execution_account_authorization(data),
        verify_execution_observability_authorization(data),
        verify_execution_rollback_authorization(data),
        verify_execution_kill_switch_authorization(data),
        verify_execution_human_supervision_authorization(data),
        verify_execution_journal_authorization(data),
        verify_execution_stop_condition_authorization(data),
        verify_execution_abort_condition_authorization(data),
        verify_execution_success_failure_authorization(data),
    )


def detect_execution_authorization_gate_risks(
    data: PaperBrokerSandboxDryRunExecutionAuthorizationGateInput | Mapping[str, Any],
    *sections: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection,
) -> tuple[PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk, ...]:
    data = _coerce_input(data)
    if not sections:
        sections = _all_sections(data)
    risks: list[PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk] = []
    for section in sections:
        risks.extend(section.risks)
    if (
        data.paper_broker_sandbox_dry_run_execution_authorization_gate_requested is not True
        or data.paper_broker_sandbox_dry_run_execution_requested is True
        or data.paper_broker_sandbox_dry_run_controlled_simulation_requested is True
        or not _offline_boundary(data)
    ):
        risks.append(PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION)
    return _dedupe(risks)


def compute_execution_authorization_gate_score(
    data: PaperBrokerSandboxDryRunExecutionAuthorizationGateInput | Mapping[str, Any],
    risks: tuple[PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk, ...] = (),
    *sections: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection,
) -> PaperBrokerSandboxDryRunExecutionAuthorizationGateScore:
    data = _coerce_input(data)
    if not sections:
        sections = _all_sections(data)
    scores = tuple(section.score for section in sections)
    overall = _clamp(_average(scores) - min(85, len(set(risks)) * 5))
    for risk, cap in {
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_REVIEW_NOT_APPROVED: 50,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_AUTHORIZATION_SCOPE_UNCLEAR: 60,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_AUTHORIZATION_BOUNDARY_GAP: 45,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_SCENARIO_AUTHORIZATION_GAP: 60,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_SESSION_LIMIT_AUTHORIZATION_GAP: 55,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_CONNECTION_AUTHORIZATION_GAP: 50,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_ORDER_AUTHORIZATION_GAP: 50,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_POSITION_AUTHORIZATION_GAP: 60,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_ACCOUNT_AUTHORIZATION_GAP: 45,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_OBSERVABILITY_AUTHORIZATION_GAP: 60,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_ROLLBACK_AUTHORIZATION_GAP: 55,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_KILL_SWITCH_AUTHORIZATION_GAP: 50,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_HUMAN_SUPERVISION_AUTHORIZATION_GAP: 45,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_JOURNAL_AUTHORIZATION_GAP: 60,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_STOP_CONDITION_AUTHORIZATION_GAP: 45,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_ABORT_CONDITION_AUTHORIZATION_GAP: 45,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_SUCCESS_FAILURE_AUTHORIZATION_GAP: 50,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION: 40,
    }.items():
        if risk in risks:
            overall = min(overall, cap)
    return PaperBrokerSandboxDryRunExecutionAuthorizationGateScore(overall, *scores)


def _select_decision(
    risks: tuple[PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk, ...],
    score: int,
) -> PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision:
    if PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION in risks or score < 45:
        return PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION
    if PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_REVIEW_NOT_APPROVED in risks:
        return PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_EXECUTION_REVIEW_FIXES
    if PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_AUTHORIZATION_SCOPE_UNCLEAR in risks:
        return PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_SCOPE_FIXES
    if PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_AUTHORIZATION_BOUNDARY_GAP in risks:
        return PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_BOUNDARY_FIXES
    if PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_SCENARIO_AUTHORIZATION_GAP in risks:
        return PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_SCENARIO_FIXES
    if PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_SESSION_LIMIT_AUTHORIZATION_GAP in risks:
        return PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_SESSION_LIMIT_FIXES
    if PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_CONNECTION_AUTHORIZATION_GAP in risks:
        return PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_CONNECTION_AUTHORIZATION_FIXES
    if PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_ORDER_AUTHORIZATION_GAP in risks:
        return PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_ORDER_AUTHORIZATION_FIXES
    if PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_POSITION_AUTHORIZATION_GAP in risks:
        return PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_POSITION_AUTHORIZATION_FIXES
    if PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_ACCOUNT_AUTHORIZATION_GAP in risks:
        return PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_ACCOUNT_AUTHORIZATION_FIXES
    if PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_OBSERVABILITY_AUTHORIZATION_GAP in risks:
        return PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_OBSERVABILITY_FIXES
    if PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_ROLLBACK_AUTHORIZATION_GAP in risks:
        return PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_ROLLBACK_FIXES
    if PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_KILL_SWITCH_AUTHORIZATION_GAP in risks:
        return PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_KILL_SWITCH_FIXES
    if PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_HUMAN_SUPERVISION_AUTHORIZATION_GAP in risks:
        return PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_SUPERVISION_FIXES
    if PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_JOURNAL_AUTHORIZATION_GAP in risks:
        return PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_JOURNAL_FIXES
    if (
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_STOP_CONDITION_AUTHORIZATION_GAP in risks
        or PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_SUCCESS_FAILURE_AUTHORIZATION_GAP in risks
    ):
        return PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_STOP_CONDITION_FIXES
    if PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_ABORT_CONDITION_AUTHORIZATION_GAP in risks:
        return PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_ABORT_CONDITION_FIXES
    if risks:
        return PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.REQUIRE_BOUNDARY_FIXES
    return PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION_GATE


def _select_state(
    decision: PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision,
    score: int,
) -> PaperBrokerSandboxDryRunExecutionAuthorizationGateState:
    if decision == PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION:
        return PaperBrokerSandboxDryRunExecutionAuthorizationGateState.NOT_AUTHORIZED
    if decision != PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION_GATE:
        return (
            PaperBrokerSandboxDryRunExecutionAuthorizationGateState.EXECUTION_AUTHORIZATION_REVIEW_REQUIRED
            if score < 82
            else PaperBrokerSandboxDryRunExecutionAuthorizationGateState.PARTIALLY_AUTHORIZED
        )
    if score >= 95:
        return PaperBrokerSandboxDryRunExecutionAuthorizationGateState.READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_PLAN
    return PaperBrokerSandboxDryRunExecutionAuthorizationGateState.EXECUTION_AUTHORIZATION_GATE_READY


def generate_execution_authorization_gate_recommendations(
    risks: tuple[PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk, ...],
    decision: PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision | None = None,
) -> tuple[PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation, ...]:
    recommendations: list[PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation] = []
    if risks:
        recommendations.append(PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.HOLD_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_PLAN)
    mapping = {
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_REVIEW_NOT_APPROVED: PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.APPROVE_EXECUTION_REVIEW_FIRST,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_AUTHORIZATION_SCOPE_UNCLEAR: PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.CLARIFY_EXECUTION_AUTHORIZATION_SCOPE,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_AUTHORIZATION_BOUNDARY_GAP: PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.COMPLETE_EXECUTION_AUTHORIZATION_BOUNDARIES,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_SCENARIO_AUTHORIZATION_GAP: PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.COMPLETE_EXECUTION_SCENARIO_AUTHORIZATION,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_SESSION_LIMIT_AUTHORIZATION_GAP: PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.COMPLETE_EXECUTION_SESSION_LIMIT_AUTHORIZATION,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_CONNECTION_AUTHORIZATION_GAP: PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.COMPLETE_EXECUTION_CONNECTION_AUTHORIZATION,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_ORDER_AUTHORIZATION_GAP: PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.COMPLETE_EXECUTION_ORDER_AUTHORIZATION,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_POSITION_AUTHORIZATION_GAP: PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.COMPLETE_EXECUTION_POSITION_AUTHORIZATION,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_ACCOUNT_AUTHORIZATION_GAP: PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.COMPLETE_EXECUTION_ACCOUNT_AUTHORIZATION,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_OBSERVABILITY_AUTHORIZATION_GAP: PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.COMPLETE_EXECUTION_OBSERVABILITY_AUTHORIZATION,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_ROLLBACK_AUTHORIZATION_GAP: PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.COMPLETE_EXECUTION_ROLLBACK_AUTHORIZATION,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_KILL_SWITCH_AUTHORIZATION_GAP: PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.COMPLETE_EXECUTION_KILL_SWITCH_AUTHORIZATION,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_HUMAN_SUPERVISION_AUTHORIZATION_GAP: PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.COMPLETE_EXECUTION_HUMAN_SUPERVISION_AUTHORIZATION,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_JOURNAL_AUTHORIZATION_GAP: PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.COMPLETE_EXECUTION_JOURNAL_AUTHORIZATION,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_STOP_CONDITION_AUTHORIZATION_GAP: PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.COMPLETE_EXECUTION_STOP_CONDITION_AUTHORIZATION,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_ABORT_CONDITION_AUTHORIZATION_GAP: PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.COMPLETE_EXECUTION_ABORT_CONDITION_AUTHORIZATION,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.EXECUTION_SUCCESS_FAILURE_AUTHORIZATION_GAP: PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.COMPLETE_EXECUTION_SUCCESS_FAILURE_AUTHORIZATION,
        PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk.PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION: PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.DELAY_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.RUN_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION_GATE_SUITE)
    if decision == PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION_GATE:
        recommendations.append(PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation.APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_PLAN)
    return _dedupe(recommendations)


def evaluate_paper_broker_sandbox_dry_run_execution_authorization_gate(
    data: PaperBrokerSandboxDryRunExecutionAuthorizationGateInput | Mapping[str, Any],
) -> PaperBrokerSandboxDryRunExecutionAuthorizationGateResult:
    data = _coerce_input(data)
    sections = _all_sections(data)
    risks = detect_execution_authorization_gate_risks(data, *sections)
    score = compute_execution_authorization_gate_score(data, risks, *sections)
    decision = _select_decision(risks, score.overall_score)
    state = _select_state(decision, score.overall_score)
    recommendations = generate_execution_authorization_gate_recommendations(risks, decision)
    offline_only = _offline_boundary(data)
    summary = f"{state.value}: decision={decision.value}, score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return PaperBrokerSandboxDryRunExecutionAuthorizationGateResult(state, decision, score.overall_score, score, risks, *sections, recommendations, offline_only, summary)


def render_paper_broker_sandbox_dry_run_execution_authorization_gate_markdown(
    result: PaperBrokerSandboxDryRunExecutionAuthorizationGateResult,
) -> str:
    lines = [
        "# AGIcore Paper Broker Sandbox Dry Run Execution Authorization Gate",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Score: {result.authorization_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Paper Broker Sandbox Dry Run Execution Authorization Gate Sections",
    ]
    sections = (
        result.execution_review_approval,
        result.execution_authorization_scope,
        result.execution_authorization_boundaries,
        result.execution_scenario_authorization,
        result.execution_session_limit_authorization,
        result.execution_connection_authorization,
        result.execution_order_authorization,
        result.execution_position_authorization,
        result.execution_account_authorization,
        result.execution_observability_authorization,
        result.execution_rollback_authorization,
        result.execution_kill_switch_authorization,
        result.execution_human_supervision_authorization,
        result.execution_journal_authorization,
        result.execution_stop_condition_authorization,
        result.execution_abort_condition_authorization,
        result.execution_success_failure_authorization,
    )
    for section in sections:
        risks = ", ".join(risk.value for risk in section.risks) or "none"
        lines.append(f"- {section.name}: passed={section.passed}, score={section.score}/100, risks={risks}")
        lines.extend(f"  - {item}" for item in section.evidence if item)
    lines.append("")
    lines.append("# Paper Broker Sandbox Dry Run Execution Authorization Gate Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Paper Broker Sandbox Dry Run Execution Authorization Gate Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_execution_authorization_gate_score",
    "detect_execution_authorization_gate_risks",
    "evaluate_paper_broker_sandbox_dry_run_execution_authorization_gate",
    "generate_execution_authorization_gate_recommendations",
    "render_paper_broker_sandbox_dry_run_execution_authorization_gate_markdown",
    "verify_execution_abort_condition_authorization",
    "verify_execution_account_authorization",
    "verify_execution_authorization_boundaries",
    "verify_execution_authorization_scope",
    "verify_execution_connection_authorization",
    "verify_execution_human_supervision_authorization",
    "verify_execution_journal_authorization",
    "verify_execution_kill_switch_authorization",
    "verify_execution_observability_authorization",
    "verify_execution_order_authorization",
    "verify_execution_position_authorization",
    "verify_execution_review_approval",
    "verify_execution_rollback_authorization",
    "verify_execution_scenario_authorization",
    "verify_execution_session_limit_authorization",
    "verify_execution_stop_condition_authorization",
    "verify_execution_success_failure_authorization",
]
