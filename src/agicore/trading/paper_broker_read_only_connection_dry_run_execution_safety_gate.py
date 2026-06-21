"""Offline safety gate for AGIcore read-only connection dry-run execution plans."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_broker_read_only_connection_dry_run_execution_safety_gate_models import (
    DryRunExecutionAccountReadOnlySafetyFinding,
    DryRunExecutionAuditSafetyFinding,
    DryRunExecutionCredentialsSafetyFinding,
    DryRunExecutionHumanApprovalSafetyFinding,
    DryRunExecutionJournalSafetyFinding,
    DryRunExecutionMarketDataReadOnlySafetyFinding,
    DryRunExecutionNetworkBlockSafetyFinding,
    DryRunExecutionObservabilitySafetyFinding,
    DryRunExecutionOrderBlockingSafetyFinding,
    DryRunExecutionPositionMutationBlockSafetyFinding,
    DryRunExecutionPreconditionSafetyFinding,
    DryRunExecutionScopeSafetyFinding,
    DryRunExecutionSequenceSafetyFinding,
    DryRunExecutionStopConditionSafetyFinding,
    DryRunExecutionSuccessFailureSafetyFinding,
    PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateDecision,
    PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput,
    PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRecommendation,
    PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateResult,
    PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk,
    PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateScore,
    PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateState,
)


Risk = PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk
Decision = PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateDecision
Recommendation = PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRecommendation


def _coerce_input(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput:
    if data is None:
        return PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput()
    if isinstance(data, PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput):
        return data
    allowed = {field.name for field in fields(PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput)}
    return PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput(
        **{key: value for key, value in dict(data).items() if key in allowed}
    )


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
    values = tuple(_value(item).upper() for item in _as_tuple(items))
    return any(any(needle.upper() in value for value in values) for needle in needles)


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


def _metric_score(explicit: int | None, fallback: Any, passed: bool) -> int:
    if explicit is not None:
        return _clamp(explicit)
    if fallback is not None:
        return _clamp(fallback)
    return 100 if passed else 0


def _plan(data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput) -> Any:
    return data.paper_broker_read_only_connection_dry_run_execution_plan


def _section(data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput, name: str) -> Any:
    return _get(_plan(data), f"dry_run_execution_{name}")


def _section_ok(section: Any) -> bool:
    return (
        section is not None
        and _get(section, "defined", True) is True
        and _get(section, "passed", True) is True
        and not _as_tuple(_get(section, "risks", ()))
    )


def _upstream_items(data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput) -> tuple[Any, ...]:
    return (
        data.paper_broker_read_only_connection_dry_run_execution_plan,
        data.paper_broker_read_only_connection_dry_run_preparation_review,
        data.paper_broker_read_only_connection_dry_run_preparation,
        data.paper_broker_read_only_connection_dry_run_safety_gate,
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


def _upstream_risks(data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _offline_boundary(data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput) -> bool:
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
            "BROKER_CONNECTION",
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


def _data_boundary(data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput) -> bool:
    return data.data_access_requested is not True and not _has_upstream_risk(data, "DATA_ACCESS", "DATA/")


def validate_dry_run_execution_plan_approval(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput | Mapping[str, Any] | None,
) -> bool:
    data = _coerce_input(data)
    plan = _plan(data)
    if plan is None or data.dry_run_execution_plan_approved is False:
        return False
    approved_state = _state_contains(
        plan,
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN",
    )
    approved = data.dry_run_execution_plan_approved is True or approved_state
    return approved and not _as_tuple(_get(plan, "risks", ())) and _get(plan, "offline_only", True) is True


def verify_dry_run_execution_scope_safety(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunExecutionScopeSafetyFinding:
    data = _coerce_input(data)
    section = _section(data, "scope")
    passed = (
        data.dry_run_execution_scope_safety_verified is not False
        and _section_ok(section)
        and _get(section, "plan_only") is True
        and _get(section, "offline_only") is True
        and _get(section, "read_only_only") is True
        and _get(section, "no_real_execution") is True
        and _offline_boundary(data)
        and _data_boundary(data)
    )
    risks = () if passed else (Risk.DRY_RUN_EXECUTION_SCOPE_UNSAFE,)
    return DryRunExecutionScopeSafetyFinding(
        score=_metric_score(data.scope_score, _get(section, "score"), passed),
        passed=passed,
        risks=risks,
        details=("dry_run_execution_scope_safety",),
        plan_only=_get(section, "plan_only") is True,
        offline_only=_get(section, "offline_only") is True and _offline_boundary(data),
        read_only_only=_get(section, "read_only_only") is True,
        dry_run_not_executed=_get(section, "no_real_execution") is True and data.dry_run_executed is not True,
        prohibited_actions_confirmed=_offline_boundary(data) and _data_boundary(data),
    )


def verify_dry_run_execution_sequence_safety(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunExecutionSequenceSafetyFinding:
    data = _coerce_input(data)
    section = _section(data, "sequence")
    steps = _as_tuple(_get(section, "steps", ()))
    passed = (
        data.dry_run_execution_sequence_safety_verified is not False
        and _section_ok(section)
        and _get(section, "dry_run_not_executed") is True
        and _get(section, "connection_not_executed") is True
        and bool(steps)
    )
    risks = () if passed else (Risk.DRY_RUN_EXECUTION_SEQUENCE_UNSAFE,)
    return DryRunExecutionSequenceSafetyFinding(
        _metric_score(data.sequence_score, _get(section, "score"), passed),
        passed,
        risks,
        ("dry_run_execution_sequence_safety",),
        _get(section, "dry_run_not_executed") is True,
        _get(section, "connection_not_executed") is True,
        bool(steps),
    )


def verify_dry_run_execution_precondition_safety(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunExecutionPreconditionSafetyFinding:
    data = _coerce_input(data)
    section = _section(data, "preconditions")
    passed = (
        data.dry_run_execution_precondition_safety_verified is not False
        and _section_ok(section)
        and _get(section, "preparation_review_required") is True
        and _get(section, "safety_gate_required_next") is True
        and _get(section, "fail_closed") is True
    )
    risks = () if passed else (Risk.DRY_RUN_EXECUTION_PRECONDITION_UNSAFE,)
    return DryRunExecutionPreconditionSafetyFinding(
        _metric_score(data.precondition_score, _get(section, "score"), passed),
        passed,
        risks,
        ("dry_run_execution_precondition_safety",),
        _get(section, "preparation_review_required") is True,
        _get(section, "safety_gate_required_next") is True,
        _get(section, "fail_closed") is True,
    )


def verify_dry_run_execution_credentials_reference_safety(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunExecutionCredentialsSafetyFinding:
    data = _coerce_input(data)
    section = _section(data, "credentials_reference_policy")
    passed = (
        data.dry_run_execution_credentials_reference_safety_verified is not False
        and _section_ok(section)
        and _get(section, "reference_only") is True
        and _get(section, "no_secret_values") is True
        and _get(section, "no_api_key_read") is True
        and _get(section, "no_env_var_read") is True
    )
    risks = () if passed else (Risk.DRY_RUN_EXECUTION_CREDENTIAL_POLICY_UNSAFE,)
    return DryRunExecutionCredentialsSafetyFinding(
        _metric_score(data.credentials_score, _get(section, "score"), passed),
        passed,
        risks,
        ("dry_run_execution_credentials_reference_safety",),
        _get(section, "reference_only") is True,
        _get(section, "no_secret_values") is True,
        _get(section, "no_api_key_read") is True,
        _get(section, "no_env_var_read") is True,
    )


def verify_dry_run_execution_no_secret_read_safety(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunExecutionCredentialsSafetyFinding:
    data = _coerce_input(data)
    section = _section(data, "no_secret_read_policy")
    passed = (
        data.dry_run_execution_no_secret_read_safety_verified is not False
        and _section_ok(section)
        and _get(section, "policy_enforced") is True
        and _get(section, "no_api_key_read") is True
        and _get(section, "no_env_var_read") is True
        and _get(section, "no_hardcoded_secret") is True
        and data.api_key_read_requested is not True
        and data.env_var_read_requested is not True
        and data.hardcoded_secret_detected is not True
    )
    risks = () if passed else (Risk.DRY_RUN_EXECUTION_SECRET_READ_POLICY_UNSAFE,)
    return DryRunExecutionCredentialsSafetyFinding(
        _metric_score(data.no_secret_read_score, _get(section, "score"), passed),
        passed,
        risks,
        ("dry_run_execution_no_secret_read_safety",),
        True,
        _get(section, "no_hardcoded_secret") is True and data.hardcoded_secret_detected is not True,
        _get(section, "no_api_key_read") is True and data.api_key_read_requested is not True,
        _get(section, "no_env_var_read") is True and data.env_var_read_requested is not True,
    )


def verify_dry_run_execution_network_block_safety(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunExecutionNetworkBlockSafetyFinding:
    data = _coerce_input(data)
    section = _section(data, "network_block_policy")
    passed = (
        data.dry_run_execution_network_block_safety_verified is not False
        and _section_ok(section)
        and _get(section, "network_execution_blocked") is True
        and _get(section, "external_api_blocked") is True
        and data.network_transport_requested is not True
        and data.external_api_requested is not True
    )
    risks = () if passed else (Risk.DRY_RUN_EXECUTION_NETWORK_NOT_BLOCKED,)
    return DryRunExecutionNetworkBlockSafetyFinding(
        _metric_score(data.network_block_score, _get(section, "score"), passed),
        passed,
        risks,
        ("dry_run_execution_network_block_safety",),
        _get(section, "network_execution_blocked") is True and data.network_transport_requested is not True,
        _get(section, "http_blocked") is True,
        _get(section, "websocket_blocked") is True,
        _get(section, "socket_blocked") is True,
        _get(section, "external_api_blocked") is True and data.external_api_requested is not True,
    )


def verify_dry_run_execution_http_websocket_socket_block_safety(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunExecutionNetworkBlockSafetyFinding:
    data = _coerce_input(data)
    section = _section(data, "http_websocket_socket_block_policy")
    passed = (
        data.dry_run_execution_http_websocket_socket_block_safety_verified is not False
        and _section_ok(section)
        and _get(section, "http_blocked") is True
        and _get(section, "websocket_blocked") is True
        and _get(section, "socket_blocked") is True
        and data.network_transport_requested is not True
    )
    risks = () if passed else (Risk.DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED,)
    return DryRunExecutionNetworkBlockSafetyFinding(
        _metric_score(data.http_websocket_socket_block_score, _get(section, "score"), passed),
        passed,
        risks,
        ("dry_run_execution_http_websocket_socket_block_safety",),
        _get(section, "network_execution_blocked") is True and data.network_transport_requested is not True,
        _get(section, "http_blocked") is True,
        _get(section, "websocket_blocked") is True,
        _get(section, "socket_blocked") is True,
        _get(section, "external_api_blocked") is True,
    )


def verify_dry_run_execution_account_read_only_safety(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunExecutionAccountReadOnlySafetyFinding:
    data = _coerce_input(data)
    section = _section(data, "account_read_only_policy")
    passed = (
        data.dry_run_execution_account_read_only_safety_verified is not False
        and _section_ok(section)
        and _get(section, "active_account_access_blocked") is True
        and _get(section, "account_mutations_blocked") is True
        and data.account_access_requested is not True
    )
    risks = () if passed else (Risk.DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_UNSAFE,)
    return DryRunExecutionAccountReadOnlySafetyFinding(
        _metric_score(data.account_read_only_score, _get(section, "score"), passed),
        passed,
        risks,
        ("dry_run_execution_account_read_only_safety",),
        _get(section, "active_account_access_blocked") is True and data.account_access_requested is not True,
        _get(section, "account_mutations_blocked") is True,
        _get(section, "schema_only_account_review") is True,
    )


def verify_dry_run_execution_market_data_read_only_safety(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunExecutionMarketDataReadOnlySafetyFinding:
    data = _coerce_input(data)
    section = _section(data, "market_data_read_only_policy")
    passed = (
        data.dry_run_execution_market_data_read_only_safety_verified is not False
        and _section_ok(section)
        and _get(section, "read_only_market_data_only") is True
        and _get(section, "live_subscription_blocked") is True
        and _get(section, "network_request_blocked") is True
    )
    risks = () if passed else (Risk.DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_UNSAFE,)
    return DryRunExecutionMarketDataReadOnlySafetyFinding(
        _metric_score(data.market_data_read_only_score, _get(section, "score"), passed),
        passed,
        risks,
        ("dry_run_execution_market_data_read_only_safety",),
        _get(section, "read_only_market_data_only") is True,
        _get(section, "live_subscription_blocked") is True,
        _get(section, "network_request_blocked") is True,
        _get(section, "schema_or_synthetic_only") is True,
    )


def verify_dry_run_execution_order_blocking_safety(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunExecutionOrderBlockingSafetyFinding:
    data = _coerce_input(data)
    section = _section(data, "order_blocking_policy")
    passed = (
        data.dry_run_execution_order_blocking_safety_verified is not False
        and _section_ok(section)
        and _get(section, "order_execution_blocked") is True
        and _get(section, "real_order_blocked") is True
        and _get(section, "cancel_replace_blocked") is True
        and data.order_execution_requested is not True
    )
    risks = () if passed else (Risk.DRY_RUN_EXECUTION_ORDER_BLOCKING_UNSAFE,)
    return DryRunExecutionOrderBlockingSafetyFinding(
        _metric_score(data.order_blocking_score, _get(section, "score"), passed),
        passed,
        risks,
        ("dry_run_execution_order_blocking_safety",),
        _get(section, "order_execution_blocked") is True and data.order_execution_requested is not True,
        _get(section, "real_order_blocked") is True,
        _get(section, "cancel_replace_blocked") is True,
    )


def verify_dry_run_execution_position_mutation_block_safety(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunExecutionPositionMutationBlockSafetyFinding:
    data = _coerce_input(data)
    section = _section(data, "position_mutation_block_policy")
    passed = (
        data.dry_run_execution_position_mutation_block_safety_verified is not False
        and _section_ok(section)
        and _get(section, "position_mutation_blocked") is True
        and _get(section, "position_request_absent") is True
        and _get(section, "close_modify_blocked") is True
        and data.position_mutation_requested is not True
    )
    risks = () if passed else (Risk.DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_UNSAFE,)
    return DryRunExecutionPositionMutationBlockSafetyFinding(
        _metric_score(data.position_mutation_block_score, _get(section, "score"), passed),
        passed,
        risks,
        ("dry_run_execution_position_mutation_block_safety",),
        _get(section, "position_mutation_blocked") is True and data.position_mutation_requested is not True,
        _get(section, "position_request_absent") is True and data.position_mutation_requested is not True,
        _get(section, "close_modify_blocked") is True,
    )


def verify_dry_run_execution_observability_safety(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunExecutionObservabilitySafetyFinding:
    data = _coerce_input(data)
    section = _section(data, "observability_plan")
    passed = (
        data.dry_run_execution_observability_safety_verified is not False
        and _section_ok(section)
        and _get(section, "offline_events_defined") is True
        and _get(section, "connection_attempt_logging_disabled") is True
        and _get(section, "sensitive_values_redacted") is True
    )
    risks = () if passed else (Risk.DRY_RUN_EXECUTION_OBSERVABILITY_INCOMPLETE,)
    return DryRunExecutionObservabilitySafetyFinding(
        _metric_score(data.observability_score, _get(section, "score"), passed),
        passed,
        risks,
        ("dry_run_execution_observability_safety",),
        _get(section, "offline_events_defined") is True,
        _get(section, "connection_attempt_logging_disabled") is True,
        _get(section, "sensitive_values_redacted") is True,
    )


def verify_dry_run_execution_journal_safety(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunExecutionJournalSafetyFinding:
    data = _coerce_input(data)
    section = _section(data, "journal_plan")
    passed = (
        data.dry_run_execution_journal_safety_verified is not False
        and _section_ok(section)
        and _get(section, "offline_journal_required") is True
        and _get(section, "sensitive_values_redacted") is True
        and _get(section, "no_secret_material_logged") is True
    )
    risks = () if passed else (Risk.DRY_RUN_EXECUTION_JOURNAL_INCOMPLETE,)
    return DryRunExecutionJournalSafetyFinding(
        _metric_score(data.journal_score, _get(section, "score"), passed),
        passed,
        risks,
        ("dry_run_execution_journal_safety",),
        _get(section, "offline_journal_required") is True,
        _get(section, "sensitive_values_redacted") is True,
        _get(section, "no_secret_material_logged") is True,
    )


def verify_dry_run_execution_human_approval_safety(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunExecutionHumanApprovalSafetyFinding:
    data = _coerce_input(data)
    section = _section(data, "human_approval_plan")
    passed = (
        data.dry_run_execution_human_approval_safety_verified is not False
        and _section_ok(section)
        and _get(section, "human_approval_required") is True
        and _get(section, "approval_before_safety_gate") is True
        and _get(section, "preparation_review_evidence_required") is True
    )
    risks = () if passed else (Risk.DRY_RUN_EXECUTION_HUMAN_APPROVAL_MISSING,)
    return DryRunExecutionHumanApprovalSafetyFinding(
        _metric_score(data.human_approval_score, _get(section, "score"), passed),
        passed,
        risks,
        ("dry_run_execution_human_approval_safety",),
        _get(section, "human_approval_required") is True,
        _get(section, "approval_before_safety_gate") is True,
        _get(section, "preparation_review_evidence_required") is True,
    )


def verify_dry_run_execution_stop_conditions_safety(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunExecutionStopConditionSafetyFinding:
    data = _coerce_input(data)
    section = _section(data, "stop_conditions_plan")
    passed = (
        data.dry_run_execution_stop_conditions_safety_verified is not False
        and _section_ok(section)
        and _get(section, "stop_on_secret_read") is True
        and _get(section, "stop_on_network_request") is True
        and _get(section, "stop_on_order_or_position_request") is True
        and _get(section, "stop_on_account_access_request") is True
    )
    risks = () if passed else (Risk.DRY_RUN_EXECUTION_STOP_CONDITIONS_MISSING,)
    return DryRunExecutionStopConditionSafetyFinding(
        _metric_score(data.stop_conditions_score, _get(section, "score"), passed),
        passed,
        risks,
        ("dry_run_execution_stop_conditions_safety",),
        _get(section, "stop_on_secret_read") is True,
        _get(section, "stop_on_network_request") is True,
        _get(section, "stop_on_order_or_position_request") is True,
        _get(section, "stop_on_account_access_request") is True,
    )


def verify_dry_run_execution_success_failure_criteria_safety(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunExecutionSuccessFailureSafetyFinding:
    data = _coerce_input(data)
    success = _section(data, "success_criteria")
    failure = _section(data, "failure_criteria")
    success_ok = (
        _section_ok(success)
        and _get(success, "requires_no_real_connection") is True
        and _get(success, "requires_no_secret_read") is True
        and _get(success, "requires_all_guards_verified") is True
    )
    failure_ok = (
        _section_ok(failure)
        and _get(failure, "failure_on_secret_network_order_position_or_account") is True
        and _get(failure, "failure_on_data_access") is True
        and _get(failure, "failure_on_real_execution") is True
    )
    passed = data.dry_run_execution_success_failure_criteria_safety_verified is not False and success_ok and failure_ok
    risks = () if passed else (Risk.DRY_RUN_EXECUTION_SUCCESS_FAILURE_CRITERIA_UNSAFE,)
    fallback = _average((_get(success, "score"), _get(failure, "score"))) if success is not None and failure is not None else None
    return DryRunExecutionSuccessFailureSafetyFinding(
        _metric_score(data.success_failure_criteria_score, fallback, passed),
        passed,
        risks,
        ("dry_run_execution_success_failure_criteria_safety",),
        _get(success, "defined") is True,
        _get(failure, "defined") is True,
        _get(success, "requires_no_real_connection") is True,
        failure_ok,
    )


def verify_dry_run_execution_audit_plan_safety(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput | Mapping[str, Any] | None,
) -> DryRunExecutionAuditSafetyFinding:
    data = _coerce_input(data)
    section = _section(data, "audit_plan")
    passed = (
        data.dry_run_execution_audit_plan_safety_verified is not False
        and _section_ok(section)
        and _get(section, "audit_events_defined") is True
        and _get(section, "offline_evidence_required") is True
        and _get(section, "next_safety_gate_trace_required") is True
    )
    risks = () if passed else (Risk.DRY_RUN_EXECUTION_AUDIT_PLAN_MISSING,)
    return DryRunExecutionAuditSafetyFinding(
        _metric_score(data.audit_plan_score, _get(section, "score"), passed),
        passed,
        risks,
        ("dry_run_execution_audit_plan_safety",),
        _get(section, "audit_events_defined") is True,
        _get(section, "offline_evidence_required") is True,
        _get(section, "next_safety_gate_trace_required") is True,
    )


def _safety_objects(data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput) -> tuple[Any, ...]:
    return (
        verify_dry_run_execution_scope_safety(data),
        verify_dry_run_execution_sequence_safety(data),
        verify_dry_run_execution_precondition_safety(data),
        verify_dry_run_execution_credentials_reference_safety(data),
        verify_dry_run_execution_no_secret_read_safety(data),
        verify_dry_run_execution_network_block_safety(data),
        verify_dry_run_execution_http_websocket_socket_block_safety(data),
        verify_dry_run_execution_account_read_only_safety(data),
        verify_dry_run_execution_market_data_read_only_safety(data),
        verify_dry_run_execution_order_blocking_safety(data),
        verify_dry_run_execution_position_mutation_block_safety(data),
        verify_dry_run_execution_observability_safety(data),
        verify_dry_run_execution_journal_safety(data),
        verify_dry_run_execution_human_approval_safety(data),
        verify_dry_run_execution_stop_conditions_safety(data),
        verify_dry_run_execution_success_failure_criteria_safety(data),
        verify_dry_run_execution_audit_plan_safety(data),
    )


def compute_read_only_connection_dry_run_execution_safety_gate_score(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateScore:
    data = _coerce_input(data)
    plan_score = _metric_score(
        data.dry_run_execution_plan_score,
        _get(_plan(data), "execution_plan_score"),
        validate_dry_run_execution_plan_approval(data),
    )
    findings = _safety_objects(data)
    scores = (plan_score,) + tuple(int(_get(finding, "score", 0)) for finding in findings)
    return PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateScore(
        overall_score=_average(scores),
        dry_run_execution_plan_score=plan_score,
        scope_score=findings[0].score,
        sequence_score=findings[1].score,
        precondition_score=findings[2].score,
        credentials_score=findings[3].score,
        no_secret_read_score=findings[4].score,
        network_block_score=findings[5].score,
        http_websocket_socket_block_score=findings[6].score,
        account_read_only_score=findings[7].score,
        market_data_read_only_score=findings[8].score,
        order_blocking_score=findings[9].score,
        position_mutation_block_score=findings[10].score,
        observability_score=findings[11].score,
        journal_score=findings[12].score,
        human_approval_score=findings[13].score,
        stop_conditions_score=findings[14].score,
        success_failure_criteria_score=findings[15].score,
        audit_plan_score=findings[16].score,
    )


def detect_read_only_connection_dry_run_execution_safety_gate_risks(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput | Mapping[str, Any] | None,
) -> tuple[PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk, ...]:
    data = _coerce_input(data)
    risks: list[PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk] = []
    if not validate_dry_run_execution_plan_approval(data):
        risks.append(Risk.DRY_RUN_EXECUTION_PLAN_NOT_APPROVED)
    for finding in _safety_objects(data):
        risks.extend(_as_tuple(_get(finding, "risks", ())))
    if not _offline_boundary(data):
        risks.append(Risk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(Risk.DATA_ACCESS_VIOLATION)
    if data.paper_broker_read_only_connection_dry_run_execution_preparation_requested is True:
        risks.append(Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION)
    return _dedupe(risks)


def generate_read_only_connection_dry_run_execution_safety_gate_recommendations(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput | Mapping[str, Any] | None,
) -> tuple[PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRecommendation, ...]:
    risks = detect_read_only_connection_dry_run_execution_safety_gate_risks(data)
    if not risks:
        return (
            Recommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE_SUITE,
            Recommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION,
        )
    mapping = {
        Risk.DRY_RUN_EXECUTION_PLAN_NOT_APPROVED: Recommendation.APPROVE_DRY_RUN_EXECUTION_PLAN_FIRST,
        Risk.DRY_RUN_EXECUTION_SCOPE_UNSAFE: Recommendation.HARDEN_DRY_RUN_EXECUTION_SCOPE,
        Risk.DRY_RUN_EXECUTION_SEQUENCE_UNSAFE: Recommendation.HARDEN_DRY_RUN_EXECUTION_SEQUENCE,
        Risk.DRY_RUN_EXECUTION_PRECONDITION_UNSAFE: Recommendation.HARDEN_DRY_RUN_EXECUTION_PRECONDITIONS,
        Risk.DRY_RUN_EXECUTION_CREDENTIAL_POLICY_UNSAFE: Recommendation.HARDEN_DRY_RUN_EXECUTION_CREDENTIALS,
        Risk.DRY_RUN_EXECUTION_SECRET_READ_POLICY_UNSAFE: Recommendation.HARDEN_DRY_RUN_EXECUTION_NO_SECRET_READ,
        Risk.DRY_RUN_EXECUTION_NETWORK_NOT_BLOCKED: Recommendation.BLOCK_DRY_RUN_EXECUTION_NETWORK,
        Risk.DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED: (
            Recommendation.BLOCK_DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET
        ),
        Risk.DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_UNSAFE: Recommendation.HARDEN_DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY,
        Risk.DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_UNSAFE: (
            Recommendation.HARDEN_DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY
        ),
        Risk.DRY_RUN_EXECUTION_ORDER_BLOCKING_UNSAFE: Recommendation.HARDEN_DRY_RUN_EXECUTION_ORDER_BLOCKING,
        Risk.DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_UNSAFE: (
            Recommendation.HARDEN_DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK
        ),
        Risk.DRY_RUN_EXECUTION_OBSERVABILITY_INCOMPLETE: Recommendation.COMPLETE_DRY_RUN_EXECUTION_OBSERVABILITY,
        Risk.DRY_RUN_EXECUTION_JOURNAL_INCOMPLETE: Recommendation.COMPLETE_DRY_RUN_EXECUTION_JOURNAL,
        Risk.DRY_RUN_EXECUTION_HUMAN_APPROVAL_MISSING: Recommendation.REQUIRE_DRY_RUN_EXECUTION_HUMAN_APPROVAL,
        Risk.DRY_RUN_EXECUTION_STOP_CONDITIONS_MISSING: Recommendation.DEFINE_DRY_RUN_EXECUTION_STOP_CONDITIONS,
        Risk.DRY_RUN_EXECUTION_SUCCESS_FAILURE_CRITERIA_UNSAFE: (
            Recommendation.HARDEN_DRY_RUN_EXECUTION_SUCCESS_FAILURE_CRITERIA
        ),
        Risk.DRY_RUN_EXECUTION_AUDIT_PLAN_MISSING: Recommendation.DEFINE_DRY_RUN_EXECUTION_AUDIT_PLAN,
        Risk.REAL_EXECUTION_BOUNDARY_VIOLATION: Recommendation.RESTORE_OFFLINE_BOUNDARIES,
        Risk.DATA_ACCESS_VIOLATION: Recommendation.REMOVE_DATA_ACCESS,
        Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION: (
            Recommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION
        ),
    }
    recommendations = [Recommendation.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION]
    recommendations.extend(mapping[risk] for risk in risks if risk in mapping)
    return _dedupe(recommendations)


def _decision_for_risks(
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk, ...],
) -> PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateDecision:
    if not risks:
        return Decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE
    if Risk.DRY_RUN_EXECUTION_PLAN_NOT_APPROVED in risks:
        return Decision.REQUIRE_DRY_RUN_EXECUTION_PLAN_FIXES
    if any(risk in risks for risk in (Risk.DRY_RUN_EXECUTION_SCOPE_UNSAFE, Risk.REAL_EXECUTION_BOUNDARY_VIOLATION, Risk.DATA_ACCESS_VIOLATION)):
        return Decision.REQUIRE_DRY_RUN_EXECUTION_SCOPE_SAFETY_FIXES
    if Risk.DRY_RUN_EXECUTION_SEQUENCE_UNSAFE in risks:
        return Decision.REQUIRE_DRY_RUN_EXECUTION_SEQUENCE_SAFETY_FIXES
    if Risk.DRY_RUN_EXECUTION_PRECONDITION_UNSAFE in risks:
        return Decision.REQUIRE_DRY_RUN_EXECUTION_PRECONDITION_SAFETY_FIXES
    if Risk.DRY_RUN_EXECUTION_CREDENTIAL_POLICY_UNSAFE in risks:
        return Decision.REQUIRE_DRY_RUN_EXECUTION_CREDENTIAL_SAFETY_FIXES
    if Risk.DRY_RUN_EXECUTION_SECRET_READ_POLICY_UNSAFE in risks:
        return Decision.REQUIRE_DRY_RUN_EXECUTION_NO_SECRET_READ_FIXES
    if any(risk in risks for risk in (Risk.DRY_RUN_EXECUTION_NETWORK_NOT_BLOCKED, Risk.DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED)):
        return Decision.REQUIRE_DRY_RUN_EXECUTION_NETWORK_BLOCK_FIXES
    if Risk.DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_UNSAFE in risks:
        return Decision.REQUIRE_DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_FIXES
    if Risk.DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_UNSAFE in risks:
        return Decision.REQUIRE_DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_FIXES
    if Risk.DRY_RUN_EXECUTION_ORDER_BLOCKING_UNSAFE in risks:
        return Decision.REQUIRE_DRY_RUN_EXECUTION_ORDER_BLOCKING_FIXES
    if Risk.DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_UNSAFE in risks:
        return Decision.REQUIRE_DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_FIXES
    if Risk.DRY_RUN_EXECUTION_HUMAN_APPROVAL_MISSING in risks:
        return Decision.REQUIRE_DRY_RUN_EXECUTION_HUMAN_APPROVAL_FIXES
    if any(risk in risks for risk in (Risk.DRY_RUN_EXECUTION_STOP_CONDITIONS_MISSING, Risk.DRY_RUN_EXECUTION_SUCCESS_FAILURE_CRITERIA_UNSAFE)):
        return Decision.REQUIRE_DRY_RUN_EXECUTION_STOP_CONDITION_FIXES
    if any(risk in risks for risk in (Risk.DRY_RUN_EXECUTION_OBSERVABILITY_INCOMPLETE, Risk.DRY_RUN_EXECUTION_JOURNAL_INCOMPLETE, Risk.DRY_RUN_EXECUTION_AUDIT_PLAN_MISSING)):
        return Decision.REQUIRE_DRY_RUN_EXECUTION_AUDIT_FIXES
    return Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE


def _state_for_result(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput,
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateRisk, ...],
    score: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateScore,
) -> PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateState:
    if data.paper_broker_read_only_connection_dry_run_execution_plan is None:
        return PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateState.DRY_RUN_EXECUTION_SAFETY_GATE_INPUT_INVALID
    if not risks and score.overall_score >= 85:
        return (
            PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION
        )
    if risks:
        return PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateState.DRY_RUN_EXECUTION_SAFETY_GATE_BLOCKED
    if score.overall_score >= 70:
        return PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateState.DRY_RUN_EXECUTION_SAFETY_GATE_COMPLETED_WITH_WARNINGS
    return PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateState.NOT_READY


def evaluate_paper_broker_read_only_connection_dry_run_execution_safety_gate(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateResult:
    data = _coerce_input(data)
    score = compute_read_only_connection_dry_run_execution_safety_gate_score(data)
    risks = detect_read_only_connection_dry_run_execution_safety_gate_risks(data)
    recommendations = generate_read_only_connection_dry_run_execution_safety_gate_recommendations(data)
    return PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateResult(
        state=_state_for_result(data, risks, score),
        decision=_decision_for_risks(risks),
        safety_gate_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        recommendations=recommendations,
        scope_safety=verify_dry_run_execution_scope_safety(data),
        sequence_safety=verify_dry_run_execution_sequence_safety(data),
        precondition_safety=verify_dry_run_execution_precondition_safety(data),
        credentials_reference_safety=verify_dry_run_execution_credentials_reference_safety(data),
        no_secret_read_safety=verify_dry_run_execution_no_secret_read_safety(data),
        network_block_safety=verify_dry_run_execution_network_block_safety(data),
        http_websocket_socket_block_safety=verify_dry_run_execution_http_websocket_socket_block_safety(data),
        account_read_only_safety=verify_dry_run_execution_account_read_only_safety(data),
        market_data_read_only_safety=verify_dry_run_execution_market_data_read_only_safety(data),
        order_blocking_safety=verify_dry_run_execution_order_blocking_safety(data),
        position_mutation_block_safety=verify_dry_run_execution_position_mutation_block_safety(data),
        observability_safety=verify_dry_run_execution_observability_safety(data),
        journal_safety=verify_dry_run_execution_journal_safety(data),
        human_approval_safety=verify_dry_run_execution_human_approval_safety(data),
        stop_conditions_safety=verify_dry_run_execution_stop_conditions_safety(data),
        success_failure_criteria_safety=verify_dry_run_execution_success_failure_criteria_safety(data),
        audit_plan_safety=verify_dry_run_execution_audit_plan_safety(data),
        offline_only=True,
        summary=(
            "Paper broker read-only connection dry-run execution safety gate is approved for execution preparation."
            if not risks
            else "Paper broker read-only connection dry-run execution safety gate is blocked until safety risks are fixed."
        ),
    )


def render_paper_broker_read_only_connection_dry_run_execution_safety_gate_markdown(
    result: PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateResult | Mapping[str, Any],
) -> str:
    if isinstance(result, Mapping):
        result = PaperBrokerReadOnlyConnectionDryRunExecutionSafetyGateResult(**dict(result))
    risks = ", ".join(risk.value for risk in result.risks) or "none"
    recommendations = ", ".join(recommendation.value for recommendation in result.recommendations) or "none"
    sections = (
        "# Paper Broker Read-Only Connection Dry Run Execution Safety Gate",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Safety gate score: {result.safety_gate_score}",
        f"- Risks: {risks}",
        f"- Recommendations: {recommendations}",
        "- Offline only: true",
        "- Sandbox only: true",
        "- Dry-run executed: false",
        "- Broker connection executed: false",
        "- API key read: false",
        "- Environment variable read: false",
        "- HTTP/websocket/socket/API external calls: blocked",
        "- Orders and position mutations: blocked",
        "- Account access: blocked",
        "- data/ access: blocked",
    )
    return "\n".join(sections)
