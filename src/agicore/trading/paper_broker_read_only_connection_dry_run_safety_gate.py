"""Offline safety gate for AGIcore Paper Broker read-only connection dry-run planning."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_broker_read_only_connection_dry_run_safety_gate_models import (
    DryRunAccountReadOnlySafetyFinding,
    DryRunBoundarySafetyFinding,
    DryRunCredentialsSafetyFinding,
    DryRunHumanApprovalSafetyFinding,
    DryRunMarketDataReadOnlySafetyFinding,
    DryRunNetworkBlockSafetyFinding,
    DryRunOrderBlockingSafetyFinding,
    DryRunPositionMutationBlockSafetyFinding,
    DryRunSafetyFinding,
    DryRunScopeSafetyFinding,
    DryRunStopConditionSafetyFinding,
    DryRunSuccessFailureCriteriaSafetyFinding,
    PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision,
    PaperBrokerReadOnlyConnectionDryRunSafetyGateInput,
    PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation,
    PaperBrokerReadOnlyConnectionDryRunSafetyGateResult,
    PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk,
    PaperBrokerReadOnlyConnectionDryRunSafetyGateScore,
    PaperBrokerReadOnlyConnectionDryRunSafetyGateState,
)


def _coerce_input(
    data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlyConnectionDryRunSafetyGateInput:
    if data is None:
        return PaperBrokerReadOnlyConnectionDryRunSafetyGateInput()
    if isinstance(data, PaperBrokerReadOnlyConnectionDryRunSafetyGateInput):
        return data
    allowed = {field.name for field in fields(PaperBrokerReadOnlyConnectionDryRunSafetyGateInput)}
    payload = {key: value for key, value in dict(data).items() if key in allowed}
    return PaperBrokerReadOnlyConnectionDryRunSafetyGateInput(**payload)


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


def _dedupe(items: Iterable[Any]) -> tuple[Any, ...]:
    seen: set[Any] = set()
    result: list[Any] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return tuple(result)


def _clamp(value: int | float, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(round(value))))


def _average(values: Iterable[int | float | None], default: int = 0) -> int:
    usable = [float(value) for value in values if value is not None]
    if not usable:
        return default
    return _clamp(sum(usable) / len(usable))


def _bool_score(value: bool | None, unknown: int = 35) -> int:
    if value is True:
        return 100
    if value is False:
        return 0
    return unknown


def _metric_score(explicit: int | None, fallback: Any, passed: bool) -> int:
    if explicit is not None:
        return _clamp(explicit)
    if fallback is not None:
        return _clamp(fallback)
    return _bool_score(passed)


def _plan(data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput) -> Any:
    return data.paper_broker_read_only_connection_dry_run_plan


def _section(data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput, name: str) -> Any:
    return _get(_plan(data), name)


def _section_ok(section: Any) -> bool:
    if section is None:
        return False
    defined = _get(section, "defined", True) is True
    passed = _get(section, "passed", True) is True
    return defined and passed and not _as_tuple(_get(section, "risks", ()))


def _upstream_items(data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput) -> tuple[Any, ...]:
    return (
        data.paper_broker_read_only_connection_dry_run_plan,
        data.paper_broker_read_only_connection_preparation_review,
        data.paper_broker_read_only_connection_preparation,
        data.paper_broker_read_only_connection_safety_gate,
        data.paper_broker_read_only_connection_plan,
        data.paper_broker_read_only_safety_review,
        data.paper_broker_read_only_preparation,
        data.multi_scenario_result_report,
        data.multi_scenario_controlled_simulation_result,
        data.performance_risk_validation_gate,
        data.performance_metrics_result,
        data.risk_metrics_result,
        data.controlled_simulation_result_report,
        data.controlled_simulation_offline_runner_result,
        data.paper_runtime_forward_test_plan,
        data.official_paper_validation_report,
        data.paper_runtime_validation,
        data.paper_trading_runtime,
        data.observability_verification,
        data.rollback_verification,
        data.kill_switch_verification,
        data.human_validated_paper_session,
        data.supervised_paper_session,
    )


def _upstream_risks(data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _offline_boundary(data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput) -> bool:
    return (
        data.offline_mode_enforced is True
        and data.sandbox_mode_enforced is True
        and data.safety_gate_only is True
        and data.broker_connection_disabled is True
        and data.no_real_broker is True
        and data.no_alpaca_real is True
        and data.no_api_key_read is True
        and data.no_env_var_read is True
        and data.no_hardcoded_secrets is True
        and data.no_http_transport is True
        and data.no_websocket_transport is True
        and data.no_socket_transport is True
        and data.no_external_api is True
        and data.no_external_ml is True
        and data.no_external_llm is True
        and data.no_live_execution is True
        and data.no_real_order is True
        and data.no_position_mutation is True
        and data.no_real_account_access is True
        and data.real_execution_requested is not True
        and data.broker_connection_requested is not True
        and data.api_key_read_requested is not True
        and data.env_var_read_requested is not True
        and data.hardcoded_secret_detected is not True
        and data.order_execution_requested is not True
        and data.position_mutation_requested is not True
        and data.account_access_requested is not True
        and data.network_transport_requested is not True
        and data.external_api_requested is not True
        and data.dry_run_requested is not True
        and data.dry_run_executed is not True
        and all(_get(item, "offline_only", True) is True for item in _upstream_items(data))
        and not _has_upstream_risk(
            data,
            "LIVE_EXECUTION",
            "BROKER_CONNECTIVITY",
            "BROKER_CONNECTION",
            "API_ACCESS",
            "API_KEY",
            "ENVIRONMENT_VARIABLE_READ",
            "SECRET_READ",
            "NETWORK",
            "HTTP",
            "WEBSOCKET",
            "SOCKET",
            "REAL_ORDER",
            "REAL_ACCOUNT",
            "REAL_EXECUTION",
            "POSITION_MUTATION",
            "ALPACA_REAL",
        )
    )


def _data_boundary(data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput) -> bool:
    return data.data_access_requested is not True and not _has_upstream_risk(data, "DATA_ACCESS", "DATA/")


def validate_dry_run_plan_approval(
    data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput | Mapping[str, Any] | None,
) -> bool:
    data = _coerce_input(data)
    plan = _plan(data)
    if plan is None or data.dry_run_plan_approved is False:
        return False
    approved_state = _state_contains(
        plan,
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN",
    )
    approved = data.dry_run_plan_approved is True or approved_state
    return approved and not _as_tuple(_get(plan, "risks", ())) and _get(plan, "offline_only", True) is True


def verify_dry_run_scope_safety(
    data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunScopeSafetyFinding:
    data = _coerce_input(data)
    scope = _section(data, "dry_run_scope")
    prohibited = _as_tuple(_get(scope, "prohibited_actions", ()))
    prohibited_confirmed = _contains(prohibited, "CONNECT", "SECRET", "NETWORK", "ORDER", "POSITION")
    passed = (
        data.dry_run_scope_safety_verified is not False
        and _section_ok(scope)
        and _get(scope, "plan_only") is True
        and _get(scope, "read_only_only") is True
        and _get(scope, "dry_run_not_executed") is True
        and prohibited_confirmed
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_SCOPE_UNSAFE,)
    score = _metric_score(data.scope_score, _get(scope, "score"), passed)
    return DryRunScopeSafetyFinding(
        score=score,
        passed=passed,
        risks=risks,
        details=("dry_run_scope_safety",),
        plan_only=_get(scope, "plan_only") is True,
        read_only_only=_get(scope, "read_only_only") is True,
        dry_run_not_executed=_get(scope, "dry_run_not_executed") is True,
        prohibited_actions_confirmed=prohibited_confirmed,
    )


def verify_dry_run_boundary_safety(
    data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunBoundarySafetyFinding:
    data = _coerce_input(data)
    boundary = _section(data, "environment_boundaries")
    passed = (
        data.dry_run_boundary_safety_verified is not False
        and _section_ok(boundary)
        and _get(boundary, "offline_only") is True
        and _get(boundary, "sandbox_only") is True
        and _get(boundary, "broker_connection_disabled") is True
        and _get(boundary, "network_transport_blocked") is True
        and _get(boundary, "data_access_blocked") is True
        and _offline_boundary(data)
        and _data_boundary(data)
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_BOUNDARY_UNSAFE,)
    score = _metric_score(data.boundary_score, _get(boundary, "score"), passed)
    return DryRunBoundarySafetyFinding(
        score=score,
        passed=passed,
        risks=risks,
        details=("offline_sandbox_boundary_safety",),
        offline_only=_get(boundary, "offline_only") is True,
        sandbox_only=_get(boundary, "sandbox_only") is True,
        broker_connection_disabled=_get(boundary, "broker_connection_disabled") is True,
        network_transport_blocked=_get(boundary, "network_transport_blocked") is True,
        data_access_blocked=_get(boundary, "data_access_blocked") is True and _data_boundary(data),
    )


def verify_dry_run_precondition_safety(
    data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunSafetyFinding:
    data = _coerce_input(data)
    section = _section(data, "preconditions")
    passed = (
        data.dry_run_precondition_safety_verified is not False
        and _section_ok(section)
        and _get(section, "preparation_review_required") is True
        and _get(section, "human_approval_required") is True
        and _get(section, "safety_gate_required") is True
        and _get(section, "stop_conditions_required") is True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_PRECONDITION_UNSAFE,)
    return DryRunSafetyFinding(_metric_score(data.precondition_score, _get(section, "score"), passed), passed, risks, ("precondition_safety",))


def verify_dry_run_credentials_safety(
    data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunCredentialsSafetyFinding:
    data = _coerce_input(data)
    section = _section(data, "credentials_reference_policy")
    passed = (
        data.dry_run_credentials_safety_verified is not False
        and _section_ok(section)
        and _get(section, "reference_only") is True
        and _get(section, "no_secret_values") is True
        and _get(section, "no_api_key_read") is True
        and _get(section, "no_env_var_read") is True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_CREDENTIALS_UNSAFE,)
    return DryRunCredentialsSafetyFinding(
        score=_metric_score(data.credentials_score, _get(section, "score"), passed),
        passed=passed,
        risks=risks,
        details=("credentials_reference_safety",),
        reference_only=_get(section, "reference_only") is True,
        no_secret_material=_get(section, "no_secret_values") is True,
        no_api_key_read=_get(section, "no_api_key_read") is True,
        no_env_var_read=_get(section, "no_env_var_read") is True,
    )


def verify_dry_run_no_secret_read_safety(
    data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunCredentialsSafetyFinding:
    data = _coerce_input(data)
    section = _section(data, "no_secret_read_policy")
    passed = (
        data.dry_run_no_secret_read_safety_verified is not False
        and _section_ok(section)
        and _get(section, "no_api_key_read") is True
        and _get(section, "no_env_var_read") is True
        and _get(section, "no_hardcoded_secret") is True
        and _get(section, "policy_enforced") is True
        and data.api_key_read_requested is not True
        and data.env_var_read_requested is not True
        and data.hardcoded_secret_detected is not True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_SECRET_READ_POLICY_UNSAFE,)
    return DryRunCredentialsSafetyFinding(
        score=_metric_score(data.no_secret_read_score, _get(section, "score"), passed),
        passed=passed,
        risks=risks,
        details=("no_secret_read_safety",),
        reference_only=True,
        no_secret_material=_get(section, "no_hardcoded_secret") is True and data.hardcoded_secret_detected is not True,
        no_api_key_read=_get(section, "no_api_key_read") is True and data.api_key_read_requested is not True,
        no_env_var_read=_get(section, "no_env_var_read") is True and data.env_var_read_requested is not True,
    )


def verify_dry_run_network_block_safety(
    data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunNetworkBlockSafetyFinding:
    data = _coerce_input(data)
    section = _section(data, "network_block_policy")
    passed = (
        data.dry_run_network_block_safety_verified is not False
        and _section_ok(section)
        and _get(section, "network_execution_blocked") is True
        and _get(section, "external_api_blocked") is True
        and data.network_transport_requested is not True
        and data.external_api_requested is not True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_NETWORK_NOT_BLOCKED,)
    return DryRunNetworkBlockSafetyFinding(
        score=_metric_score(data.network_block_score, _get(section, "score"), passed),
        passed=passed,
        risks=risks,
        details=("network_block_safety",),
        network_execution_blocked=_get(section, "network_execution_blocked") is True and data.network_transport_requested is not True,
        http_blocked=_get(section, "http_blocked") is True,
        websocket_blocked=_get(section, "websocket_blocked") is True,
        socket_blocked=_get(section, "socket_blocked") is True,
        external_api_blocked=_get(section, "external_api_blocked") is True and data.external_api_requested is not True,
    )


def verify_dry_run_http_websocket_socket_block_safety(
    data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunNetworkBlockSafetyFinding:
    data = _coerce_input(data)
    section = _section(data, "http_websocket_socket_block_policy")
    passed = (
        data.dry_run_http_websocket_socket_block_safety_verified is not False
        and _section_ok(section)
        and _get(section, "http_blocked") is True
        and _get(section, "websocket_blocked") is True
        and _get(section, "socket_blocked") is True
        and data.network_transport_requested is not True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED,)
    return DryRunNetworkBlockSafetyFinding(
        score=_metric_score(data.http_websocket_socket_block_score, _get(section, "score"), passed),
        passed=passed,
        risks=risks,
        details=("http_websocket_socket_block_safety",),
        network_execution_blocked=_get(section, "network_execution_blocked") is True and data.network_transport_requested is not True,
        http_blocked=_get(section, "http_blocked") is True,
        websocket_blocked=_get(section, "websocket_blocked") is True,
        socket_blocked=_get(section, "socket_blocked") is True,
        external_api_blocked=_get(section, "external_api_blocked") is True,
    )


def verify_dry_run_account_read_only_safety(
    data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunAccountReadOnlySafetyFinding:
    data = _coerce_input(data)
    section = _section(data, "account_read_only_policy")
    passed = (
        data.dry_run_account_read_only_safety_verified is not False
        and _section_ok(section)
        and _get(section, "active_account_access_blocked") is True
        and _get(section, "account_mutations_blocked") is True
        and data.account_access_requested is not True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_ACCOUNT_READ_ONLY_UNSAFE,)
    return DryRunAccountReadOnlySafetyFinding(
        score=_metric_score(data.account_read_only_score, _get(section, "score"), passed),
        passed=passed,
        risks=risks,
        details=("account_read_only_safety",),
        active_account_access_blocked=_get(section, "active_account_access_blocked") is True and data.account_access_requested is not True,
        account_mutations_blocked=_get(section, "account_mutations_blocked") is True,
    )


def verify_dry_run_market_data_read_only_safety(
    data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunMarketDataReadOnlySafetyFinding:
    data = _coerce_input(data)
    section = _section(data, "market_data_read_only_policy")
    passed = (
        data.dry_run_market_data_read_only_safety_verified is not False
        and _section_ok(section)
        and _get(section, "read_only_market_data_only") is True
        and _get(section, "live_subscription_blocked") is True
        and _get(section, "network_request_blocked") is True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_MARKET_DATA_READ_ONLY_UNSAFE,)
    return DryRunMarketDataReadOnlySafetyFinding(
        score=_metric_score(data.market_data_read_only_score, _get(section, "score"), passed),
        passed=passed,
        risks=risks,
        details=("market_data_read_only_safety",),
        read_only_market_data_only=_get(section, "read_only_market_data_only") is True,
        live_subscription_blocked=_get(section, "live_subscription_blocked") is True,
        network_request_blocked=_get(section, "network_request_blocked") is True,
    )


def verify_dry_run_order_blocking_safety(
    data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunOrderBlockingSafetyFinding:
    data = _coerce_input(data)
    section = _section(data, "order_blocking_policy")
    passed = (
        data.dry_run_order_blocking_safety_verified is not False
        and _section_ok(section)
        and _get(section, "order_execution_blocked") is True
        and _get(section, "real_order_blocked") is True
        and _get(section, "cancel_replace_blocked") is True
        and data.order_execution_requested is not True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_ORDER_BLOCKING_UNSAFE,)
    return DryRunOrderBlockingSafetyFinding(
        score=_metric_score(data.order_blocking_score, _get(section, "score"), passed),
        passed=passed,
        risks=risks,
        details=("order_blocking_safety",),
        order_execution_blocked=_get(section, "order_execution_blocked") is True and data.order_execution_requested is not True,
        real_order_blocked=_get(section, "real_order_blocked") is True,
        cancel_replace_blocked=_get(section, "cancel_replace_blocked") is True,
    )


def verify_dry_run_position_mutation_block_safety(
    data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunPositionMutationBlockSafetyFinding:
    data = _coerce_input(data)
    section = _section(data, "position_mutation_block_policy")
    passed = (
        data.dry_run_position_mutation_block_safety_verified is not False
        and _section_ok(section)
        and _get(section, "position_mutation_blocked") is True
        and _get(section, "position_request_absent") is True
        and data.position_mutation_requested is not True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_POSITION_MUTATION_BLOCK_UNSAFE,)
    return DryRunPositionMutationBlockSafetyFinding(
        score=_metric_score(data.position_mutation_block_score, _get(section, "score"), passed),
        passed=passed,
        risks=risks,
        details=("position_mutation_block_safety",),
        position_mutation_blocked=_get(section, "position_mutation_blocked") is True and data.position_mutation_requested is not True,
        position_request_absent=_get(section, "position_request_absent") is True and data.position_mutation_requested is not True,
    )


def verify_dry_run_observability_safety(
    data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunSafetyFinding:
    data = _coerce_input(data)
    section = _section(data, "observability_plan")
    passed = (
        data.dry_run_observability_safety_verified is not False
        and _section_ok(section)
        and _get(section, "offline_events_defined") is True
        and _get(section, "connection_attempt_logging_disabled") is True
        and _get(section, "sensitive_values_redacted") is True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_OBSERVABILITY_INCOMPLETE,)
    return DryRunSafetyFinding(_metric_score(data.observability_score, _get(section, "score"), passed), passed, risks, ("observability_safety",))


def verify_dry_run_journal_safety(
    data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunSafetyFinding:
    data = _coerce_input(data)
    section = _section(data, "journal_plan")
    passed = (
        data.dry_run_journal_safety_verified is not False
        and _section_ok(section)
        and _get(section, "offline_journal_required") is True
        and _get(section, "sensitive_values_redacted") is True
        and _get(section, "no_secret_material_logged") is True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_JOURNAL_INCOMPLETE,)
    return DryRunSafetyFinding(_metric_score(data.journal_score, _get(section, "score"), passed), passed, risks, ("journal_safety",))


def verify_dry_run_human_approval_safety(
    data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunHumanApprovalSafetyFinding:
    data = _coerce_input(data)
    section = _section(data, "human_approval_plan")
    passed = (
        data.dry_run_human_approval_safety_verified is not False
        and _section_ok(section)
        and _get(section, "human_approval_required") is True
        and _get(section, "approval_before_safety_gate") is True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_HUMAN_APPROVAL_MISSING,)
    return DryRunHumanApprovalSafetyFinding(
        score=_metric_score(data.human_approval_score, _get(section, "score"), passed),
        passed=passed,
        risks=risks,
        details=("human_approval_safety",),
        human_approval_required=_get(section, "human_approval_required") is True,
        approval_before_preparation=_get(section, "approval_before_safety_gate") is True,
    )


def verify_dry_run_stop_conditions_safety(
    data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunStopConditionSafetyFinding:
    data = _coerce_input(data)
    section = _section(data, "stop_conditions_plan")
    passed = (
        data.dry_run_stop_conditions_safety_verified is not False
        and _section_ok(section)
        and _get(section, "stop_on_secret_read") is True
        and _get(section, "stop_on_network_request") is True
        and _get(section, "stop_on_order_or_position_request") is True
        and _get(section, "stop_on_account_access_request") is True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_STOP_CONDITIONS_MISSING,)
    return DryRunStopConditionSafetyFinding(
        score=_metric_score(data.stop_conditions_score, _get(section, "score"), passed),
        passed=passed,
        risks=risks,
        details=("stop_conditions_safety",),
        stop_on_secret_read=_get(section, "stop_on_secret_read") is True,
        stop_on_network_request=_get(section, "stop_on_network_request") is True,
        stop_on_order_or_position_request=_get(section, "stop_on_order_or_position_request") is True,
        stop_on_account_access_request=_get(section, "stop_on_account_access_request") is True,
    )


def verify_dry_run_success_failure_criteria_safety(
    data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunSuccessFailureCriteriaSafetyFinding:
    data = _coerce_input(data)
    success = _section(data, "success_criteria")
    failure = _section(data, "failure_criteria")
    success_ok = (
        _section_ok(success)
        and _get(success, "no_real_connection_attempted") is True
        and _get(success, "all_guards_verified") is True
        and _get(success, "read_only_boundaries_preserved") is True
    )
    failure_ok = (
        _section_ok(failure)
        and _get(failure, "fail_on_secret_read") is True
        and _get(failure, "fail_on_network_attempt") is True
        and _get(failure, "fail_on_order_or_position_request") is True
        and _get(failure, "fail_on_account_access_request") is True
    )
    passed = data.dry_run_success_failure_criteria_safety_verified is not False and success_ok and failure_ok
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_SUCCESS_FAILURE_CRITERIA_UNSAFE,)
    fallback = _average((_get(success, "score"), _get(failure, "score"))) if success is not None and failure is not None else None
    return DryRunSuccessFailureCriteriaSafetyFinding(
        score=_metric_score(data.success_failure_criteria_score, fallback, passed),
        passed=passed,
        risks=risks,
        details=("success_failure_criteria_safety",),
        success_criteria_defined=_get(success, "defined") is True,
        failure_criteria_defined=_get(failure, "defined") is True,
        fail_closed_on_boundary_violation=failure_ok,
    )


def _safety_objects(data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput) -> tuple[Any, ...]:
    return (
        verify_dry_run_scope_safety(data),
        verify_dry_run_boundary_safety(data),
        verify_dry_run_precondition_safety(data),
        verify_dry_run_credentials_safety(data),
        verify_dry_run_no_secret_read_safety(data),
        verify_dry_run_network_block_safety(data),
        verify_dry_run_http_websocket_socket_block_safety(data),
        verify_dry_run_account_read_only_safety(data),
        verify_dry_run_market_data_read_only_safety(data),
        verify_dry_run_order_blocking_safety(data),
        verify_dry_run_position_mutation_block_safety(data),
        verify_dry_run_observability_safety(data),
        verify_dry_run_journal_safety(data),
        verify_dry_run_human_approval_safety(data),
        verify_dry_run_stop_conditions_safety(data),
        verify_dry_run_success_failure_criteria_safety(data),
    )


def compute_dry_run_safety_gate_score(
    data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlyConnectionDryRunSafetyGateScore:
    data = _coerce_input(data)
    plan_score = _metric_score(data.dry_run_plan_score, _get(_plan(data), "dry_run_plan_score"), validate_dry_run_plan_approval(data))
    scope = verify_dry_run_scope_safety(data)
    boundary = verify_dry_run_boundary_safety(data)
    precondition = verify_dry_run_precondition_safety(data)
    credentials = verify_dry_run_credentials_safety(data)
    no_secret = verify_dry_run_no_secret_read_safety(data)
    network = verify_dry_run_network_block_safety(data)
    http_ws_socket = verify_dry_run_http_websocket_socket_block_safety(data)
    account = verify_dry_run_account_read_only_safety(data)
    market_data = verify_dry_run_market_data_read_only_safety(data)
    order = verify_dry_run_order_blocking_safety(data)
    position = verify_dry_run_position_mutation_block_safety(data)
    observability = verify_dry_run_observability_safety(data)
    journal = verify_dry_run_journal_safety(data)
    human = verify_dry_run_human_approval_safety(data)
    stop = verify_dry_run_stop_conditions_safety(data)
    criteria = verify_dry_run_success_failure_criteria_safety(data)
    values = (
        plan_score,
        scope.score,
        boundary.score,
        precondition.score,
        credentials.score,
        no_secret.score,
        network.score,
        http_ws_socket.score,
        account.score,
        market_data.score,
        order.score,
        position.score,
        observability.score,
        journal.score,
        human.score,
        stop.score,
        criteria.score,
    )
    return PaperBrokerReadOnlyConnectionDryRunSafetyGateScore(
        overall_score=_average(values),
        dry_run_plan_score=plan_score,
        scope_score=scope.score,
        boundary_score=boundary.score,
        precondition_score=precondition.score,
        credentials_score=credentials.score,
        no_secret_read_score=no_secret.score,
        network_block_score=network.score,
        http_websocket_socket_block_score=http_ws_socket.score,
        account_read_only_score=account.score,
        market_data_read_only_score=market_data.score,
        order_blocking_score=order.score,
        position_mutation_block_score=position.score,
        observability_score=observability.score,
        journal_score=journal.score,
        human_approval_score=human.score,
        stop_conditions_score=stop.score,
        success_failure_criteria_score=criteria.score,
    )


def detect_dry_run_safety_gate_risks(
    data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput | Mapping[str, Any] | None,
) -> tuple[PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk, ...]:
    data = _coerce_input(data)
    risks: list[PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk] = []
    if not validate_dry_run_plan_approval(data):
        risks.append(PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_PLAN_NOT_APPROVED)
    for item in _safety_objects(data):
        risks.extend(_as_tuple(_get(item, "risks", ())))
    if not _offline_boundary(data):
        risks.append(PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DATA_ACCESS_VIOLATION)
    if data.paper_broker_read_only_connection_dry_run_preparation_requested is True:
        risks.append(PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION)
    return _dedupe(risks)


def generate_dry_run_safety_gate_recommendations(
    data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput | Mapping[str, Any] | None,
) -> tuple[PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation, ...]:
    risks = detect_dry_run_safety_gate_risks(data)
    if not risks:
        return (
            PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE_SUITE,
            PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION,
        )
    mapping = {
        PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_PLAN_NOT_APPROVED: PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation.APPROVE_DRY_RUN_PLAN_FIRST,
        PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_SCOPE_UNSAFE: PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation.HARDEN_DRY_RUN_SCOPE,
        PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_BOUNDARY_UNSAFE: PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation.HARDEN_DRY_RUN_BOUNDARIES,
        PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_PRECONDITION_UNSAFE: PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation.HARDEN_DRY_RUN_PRECONDITIONS,
        PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_CREDENTIALS_UNSAFE: PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation.HARDEN_DRY_RUN_CREDENTIALS,
        PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_SECRET_READ_POLICY_UNSAFE: PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation.HARDEN_DRY_RUN_NO_SECRET_READ,
        PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_NETWORK_NOT_BLOCKED: PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation.BLOCK_DRY_RUN_NETWORK,
        PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED: PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation.BLOCK_DRY_RUN_HTTP_WEBSOCKET_SOCKET,
        PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_ACCOUNT_READ_ONLY_UNSAFE: PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation.HARDEN_DRY_RUN_ACCOUNT_READ_ONLY,
        PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_MARKET_DATA_READ_ONLY_UNSAFE: PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation.HARDEN_DRY_RUN_MARKET_DATA_READ_ONLY,
        PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_ORDER_BLOCKING_UNSAFE: PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation.HARDEN_DRY_RUN_ORDER_BLOCKING,
        PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_POSITION_MUTATION_BLOCK_UNSAFE: PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation.HARDEN_DRY_RUN_POSITION_MUTATION_BLOCK,
        PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_OBSERVABILITY_INCOMPLETE: PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation.COMPLETE_DRY_RUN_OBSERVABILITY,
        PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_JOURNAL_INCOMPLETE: PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation.COMPLETE_DRY_RUN_JOURNAL,
        PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_HUMAN_APPROVAL_MISSING: PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation.REQUIRE_DRY_RUN_HUMAN_APPROVAL,
        PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_STOP_CONDITIONS_MISSING: PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation.DEFINE_DRY_RUN_STOP_CONDITIONS,
        PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_SUCCESS_FAILURE_CRITERIA_UNSAFE: PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation.HARDEN_DRY_RUN_SUCCESS_FAILURE_CRITERIA,
        PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.REAL_EXECUTION_BOUNDARY_VIOLATION: PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation.RESTORE_OFFLINE_BOUNDARIES,
        PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DATA_ACCESS_VIOLATION: PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation.REMOVE_DATA_ACCESS,
        PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION: PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION,
    }
    recommendations = [
        PaperBrokerReadOnlyConnectionDryRunSafetyGateRecommendation.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION
    ]
    recommendations.extend(mapping[risk] for risk in risks if risk in mapping)
    return _dedupe(recommendations)


def _decision_for_risks(
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk, ...],
) -> PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision:
    if not risks:
        return PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE
    if PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_PLAN_NOT_APPROVED in risks:
        return PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_DRY_RUN_PLAN_FIXES
    if any(
        risk in risks
        for risk in (
            PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_BOUNDARY_UNSAFE,
            PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.REAL_EXECUTION_BOUNDARY_VIOLATION,
            PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DATA_ACCESS_VIOLATION,
        )
    ):
        return PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_BOUNDARY_SAFETY_FIXES
    if PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_SCOPE_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_SCOPE_SAFETY_FIXES
    if PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_PRECONDITION_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_PRECONDITION_SAFETY_FIXES
    if PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_CREDENTIALS_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_CREDENTIAL_SAFETY_FIXES
    if PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_SECRET_READ_POLICY_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_NO_SECRET_READ_SAFETY_FIXES
    if any(
        risk in risks
        for risk in (
            PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_NETWORK_NOT_BLOCKED,
            PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED,
        )
    ):
        return PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_NETWORK_BLOCK_SAFETY_FIXES
    if PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_ACCOUNT_READ_ONLY_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_ACCOUNT_READ_ONLY_SAFETY_FIXES
    if PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_MARKET_DATA_READ_ONLY_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_MARKET_DATA_READ_ONLY_SAFETY_FIXES
    if PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_ORDER_BLOCKING_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_ORDER_BLOCKING_SAFETY_FIXES
    if PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_POSITION_MUTATION_BLOCK_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_POSITION_MUTATION_BLOCK_SAFETY_FIXES
    if PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_OBSERVABILITY_INCOMPLETE in risks:
        return PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_OBSERVABILITY_SAFETY_FIXES
    if PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_JOURNAL_INCOMPLETE in risks:
        return PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_JOURNAL_SAFETY_FIXES
    if PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_HUMAN_APPROVAL_MISSING in risks:
        return PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_HUMAN_APPROVAL_SAFETY_FIXES
    if PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_STOP_CONDITIONS_MISSING in risks:
        return PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_STOP_CONDITION_SAFETY_FIXES
    if PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk.DRY_RUN_SUCCESS_FAILURE_CRITERIA_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.REQUIRE_SUCCESS_FAILURE_CRITERIA_SAFETY_FIXES
    return PaperBrokerReadOnlyConnectionDryRunSafetyGateDecision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE


def _state_for_result(
    data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput,
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunSafetyGateRisk, ...],
    score: PaperBrokerReadOnlyConnectionDryRunSafetyGateScore,
) -> PaperBrokerReadOnlyConnectionDryRunSafetyGateState:
    if data.paper_broker_read_only_connection_dry_run_plan is None:
        return PaperBrokerReadOnlyConnectionDryRunSafetyGateState.DRY_RUN_SAFETY_INPUT_INVALID
    if not risks and score.overall_score >= 85:
        return PaperBrokerReadOnlyConnectionDryRunSafetyGateState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION
    if risks:
        return PaperBrokerReadOnlyConnectionDryRunSafetyGateState.DRY_RUN_SAFETY_BLOCKED
    if score.overall_score >= 70:
        return PaperBrokerReadOnlyConnectionDryRunSafetyGateState.DRY_RUN_SAFETY_COMPLETED_WITH_WARNINGS
    return PaperBrokerReadOnlyConnectionDryRunSafetyGateState.NOT_READY


def evaluate_paper_broker_read_only_connection_dry_run_safety_gate(
    data: PaperBrokerReadOnlyConnectionDryRunSafetyGateInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlyConnectionDryRunSafetyGateResult:
    data = _coerce_input(data)
    score = compute_dry_run_safety_gate_score(data)
    risks = detect_dry_run_safety_gate_risks(data)
    recommendations = generate_dry_run_safety_gate_recommendations(data)
    decision = _decision_for_risks(risks)
    state = _state_for_result(data, risks, score)
    return PaperBrokerReadOnlyConnectionDryRunSafetyGateResult(
        state=state,
        decision=decision,
        safety_gate_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        recommendations=recommendations,
        scope_safety=verify_dry_run_scope_safety(data),
        boundary_safety=verify_dry_run_boundary_safety(data),
        precondition_safety=verify_dry_run_precondition_safety(data),
        credentials_safety=verify_dry_run_credentials_safety(data),
        no_secret_read_safety=verify_dry_run_no_secret_read_safety(data),
        network_block_safety=verify_dry_run_network_block_safety(data),
        http_websocket_socket_block_safety=verify_dry_run_http_websocket_socket_block_safety(data),
        account_read_only_safety=verify_dry_run_account_read_only_safety(data),
        market_data_read_only_safety=verify_dry_run_market_data_read_only_safety(data),
        order_blocking_safety=verify_dry_run_order_blocking_safety(data),
        position_mutation_block_safety=verify_dry_run_position_mutation_block_safety(data),
        observability_safety=verify_dry_run_observability_safety(data),
        journal_safety=verify_dry_run_journal_safety(data),
        human_approval_safety=verify_dry_run_human_approval_safety(data),
        stop_conditions_safety=verify_dry_run_stop_conditions_safety(data),
        success_failure_criteria_safety=verify_dry_run_success_failure_criteria_safety(data),
        offline_only=True,
        summary=(
            "Paper broker read-only connection dry-run safety gate is approved for dry-run preparation."
            if not risks
            else "Paper broker read-only connection dry-run safety gate is blocked until safety risks are fixed."
        ),
    )


def render_paper_broker_read_only_connection_dry_run_safety_gate_markdown(
    result: PaperBrokerReadOnlyConnectionDryRunSafetyGateResult | Mapping[str, Any],
) -> str:
    if isinstance(result, Mapping):
        result = PaperBrokerReadOnlyConnectionDryRunSafetyGateResult(**dict(result))
    risks = ", ".join(risk.value for risk in result.risks) or "none"
    recommendations = ", ".join(recommendation.value for recommendation in result.recommendations) or "none"
    sections = (
        ("scope_safety", result.scope_safety),
        ("boundary_safety", result.boundary_safety),
        ("precondition_safety", result.precondition_safety),
        ("credentials_safety", result.credentials_safety),
        ("no_secret_read_safety", result.no_secret_read_safety),
        ("network_block_safety", result.network_block_safety),
        ("http_websocket_socket_block_safety", result.http_websocket_socket_block_safety),
        ("account_read_only_safety", result.account_read_only_safety),
        ("market_data_read_only_safety", result.market_data_read_only_safety),
        ("order_blocking_safety", result.order_blocking_safety),
        ("position_mutation_block_safety", result.position_mutation_block_safety),
        ("observability_safety", result.observability_safety),
        ("journal_safety", result.journal_safety),
        ("human_approval_safety", result.human_approval_safety),
        ("stop_conditions_safety", result.stop_conditions_safety),
        ("success_failure_criteria_safety", result.success_failure_criteria_safety),
    )
    lines = [
        "# Paper Broker Read-Only Connection Dry Run Safety Gate",
        "",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Safety gate score: {result.safety_gate_score}",
        f"- Offline only: {result.offline_only}",
        f"- Risks: {risks}",
        f"- Recommendations: {recommendations}",
        "",
        "## Enforced Safety Gate Boundaries",
        "- Safety gate only: no dry-run preparation execution and no connection test",
        "- No broker, Alpaca, API key, environment variable, or hardcoded secret read",
        "- No HTTP, websocket, socket, network transport, or external API",
        "- No order execution, position mutation, trading, or active account access",
        "- No data/ access",
        "",
        "## Safety Findings",
    ]
    for name, section in sections:
        lines.append(f"- {name}: score={section.score}, passed={section.passed}, risks={len(section.risks)}")
    if result.summary:
        lines.extend(("", f"Summary: {result.summary}"))
    return "\n".join(lines)
