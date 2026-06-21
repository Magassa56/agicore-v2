"""Offline execution planning for AGIcore Paper Broker read-only connection dry-runs."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_broker_read_only_connection_dry_run_execution_plan_models import (
    DryRunExecutionAccountReadOnlyPolicy,
    DryRunExecutionAuditPlan,
    DryRunExecutionCredentialsReferencePolicy,
    DryRunExecutionFailureCriteria,
    DryRunExecutionHumanApprovalPlan,
    DryRunExecutionJournalPlan,
    DryRunExecutionMarketDataReadOnlyPolicy,
    DryRunExecutionNetworkBlockPolicy,
    DryRunExecutionNoSecretReadPolicy,
    DryRunExecutionObservabilityPlan,
    DryRunExecutionOrderBlockingPolicy,
    DryRunExecutionPositionMutationBlockPolicy,
    DryRunExecutionPrecondition,
    DryRunExecutionScope,
    DryRunExecutionSequence,
    DryRunExecutionStopConditionPlan,
    DryRunExecutionSuccessCriteria,
    PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision,
    PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput,
    PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation,
    PaperBrokerReadOnlyConnectionDryRunExecutionPlanResult,
    PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk,
    PaperBrokerReadOnlyConnectionDryRunExecutionPlanScore,
    PaperBrokerReadOnlyConnectionDryRunExecutionPlanState,
)


def _coerce_input(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput:
    if data is None:
        return PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput()
    if isinstance(data, PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput):
        return data
    allowed = {field.name for field in fields(PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput)}
    payload = {key: value for key, value in dict(data).items() if key in allowed}
    return PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput(**payload)


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


def _review(data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput) -> Any:
    return data.paper_broker_read_only_connection_dry_run_preparation_review


def _upstream_items(data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput) -> tuple[Any, ...]:
    return (
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


def _upstream_risks(data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _offline_boundary(data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput) -> bool:
    return (
        data.offline_mode_enforced is True
        and data.sandbox_mode_enforced is True
        and data.plan_only is True
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


def _data_boundary(data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput) -> bool:
    return data.data_access_requested is not True and not _has_upstream_risk(data, "DATA_ACCESS", "DATA/", "REAL_DATA")


def validate_dry_run_preparation_review_approval(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput | Mapping[str, Any] | None,
) -> bool:
    data = _coerce_input(data)
    review = _review(data)
    if review is None or data.dry_run_preparation_review_approved is False:
        return False
    approved_state = _state_contains(
        review,
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION_REVIEW",
    )
    approved = data.dry_run_preparation_review_approved is True or approved_state
    return approved and not _as_tuple(_get(review, "risks", ())) and _get(review, "offline_only", True) is True


def define_dry_run_execution_scope(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput | Mapping[str, Any] | None,
) -> DryRunExecutionScope:
    data = _coerce_input(data)
    passed = (
        data.dry_run_execution_scope_defined is True
        and data.plan_only is True
        and data.offline_mode_enforced is True
        and data.sandbox_mode_enforced is True
        and data.dry_run_executed is not True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_SCOPE_UNCLEAR,)
    return DryRunExecutionScope(
        score=_metric_score(data.scope_score, None, passed),
        defined=data.dry_run_execution_scope_defined is True,
        plan_only=data.plan_only is True,
        offline_only=data.offline_mode_enforced is True,
        read_only_only=True,
        no_real_execution=data.dry_run_executed is not True and data.real_execution_requested is not True,
        risks=risks,
        details=("plan_only", "future_execution_safety_gate_only"),
    )


def define_dry_run_execution_sequence(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput | Mapping[str, Any] | None,
) -> DryRunExecutionSequence:
    data = _coerce_input(data)
    passed = data.dry_run_execution_sequence_defined is True and data.dry_run_requested is not True and data.broker_connection_requested is not True
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_SEQUENCE_MISSING,)
    return DryRunExecutionSequence(
        score=_metric_score(data.sequence_score, None, passed),
        defined=data.dry_run_execution_sequence_defined is True,
        dry_run_not_executed=data.dry_run_requested is not True and data.dry_run_executed is not True,
        connection_not_executed=data.broker_connection_requested is not True,
        steps=(
            "load_offline_plan_evidence",
            "verify_read_only_boundaries",
            "verify_no_secret_no_network_guards",
            "prepare_execution_safety_gate_packet",
        ),
        risks=risks,
        details=("sequence_documented_without_execution",),
    )


def define_dry_run_execution_preconditions(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput | Mapping[str, Any] | None,
) -> DryRunExecutionPrecondition:
    data = _coerce_input(data)
    passed = data.dry_run_execution_preconditions_defined is True and validate_dry_run_preparation_review_approval(data)
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_PRECONDITION_MISSING,)
    return DryRunExecutionPrecondition(
        score=_metric_score(data.precondition_score, None, passed),
        defined=data.dry_run_execution_preconditions_defined is True,
        preparation_review_required=True,
        safety_gate_required_next=True,
        fail_closed=True,
        risks=risks,
        details=("preparation_review_approval_required", "safety_gate_before_any_dry_run"),
    )


def define_dry_run_execution_credentials_reference_policy(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput | Mapping[str, Any] | None,
) -> DryRunExecutionCredentialsReferencePolicy:
    data = _coerce_input(data)
    secret_ok = (
        data.no_api_key_read is True
        and data.no_env_var_read is True
        and data.no_hardcoded_secrets is True
        and data.api_key_read_requested is not True
        and data.env_var_read_requested is not True
        and data.hardcoded_secret_detected is not True
    )
    passed = (
        data.dry_run_execution_credentials_policy_defined is True
        and data.dry_run_execution_credentials_reference_only is True
        and secret_ok
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_CREDENTIAL_POLICY_UNSAFE,)
    return DryRunExecutionCredentialsReferencePolicy(
        score=_metric_score(data.credential_policy_score, None, passed),
        defined=data.dry_run_execution_credentials_policy_defined is True,
        reference_only=data.dry_run_execution_credentials_reference_only is True,
        no_secret_values=secret_ok,
        no_api_key_read=data.no_api_key_read is True and data.api_key_read_requested is not True,
        no_env_var_read=data.no_env_var_read is True and data.env_var_read_requested is not True,
        risks=risks,
        details=("credential_references_only", "no_secret_material_loaded"),
    )


def define_dry_run_execution_no_secret_read_policy(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput | Mapping[str, Any] | None,
) -> DryRunExecutionNoSecretReadPolicy:
    data = _coerce_input(data)
    passed = (
        data.dry_run_execution_no_secret_read_policy_defined is True
        and data.dry_run_execution_no_secret_read_enforced is True
        and data.no_api_key_read is True
        and data.no_env_var_read is True
        and data.no_hardcoded_secrets is True
        and data.api_key_read_requested is not True
        and data.env_var_read_requested is not True
        and data.hardcoded_secret_detected is not True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_SECRET_READ_POLICY_UNSAFE,)
    return DryRunExecutionNoSecretReadPolicy(
        score=_metric_score(data.no_secret_read_score, None, passed),
        defined=data.dry_run_execution_no_secret_read_policy_defined is True,
        policy_enforced=data.dry_run_execution_no_secret_read_enforced is True,
        no_api_key_read=data.no_api_key_read is True and data.api_key_read_requested is not True,
        no_env_var_read=data.no_env_var_read is True and data.env_var_read_requested is not True,
        no_hardcoded_secret=data.no_hardcoded_secrets is True and data.hardcoded_secret_detected is not True,
        risks=risks,
        details=("fail_closed_on_secret_read",),
    )


def define_dry_run_execution_network_block_policy(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput | Mapping[str, Any] | None,
) -> DryRunExecutionNetworkBlockPolicy:
    data = _coerce_input(data)
    passed = (
        data.dry_run_execution_network_block_policy_defined is True
        and data.dry_run_execution_network_blocked is True
        and data.dry_run_execution_external_api_blocked is True
        and data.network_transport_requested is not True
        and data.external_api_requested is not True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_NETWORK_NOT_BLOCKED,)
    return DryRunExecutionNetworkBlockPolicy(
        score=_metric_score(data.network_block_score, None, passed),
        defined=data.dry_run_execution_network_block_policy_defined is True,
        network_execution_blocked=data.dry_run_execution_network_blocked is True and data.network_transport_requested is not True,
        http_blocked=data.dry_run_execution_http_blocked is True and data.no_http_transport is True,
        websocket_blocked=data.dry_run_execution_websocket_blocked is True and data.no_websocket_transport is True,
        socket_blocked=data.dry_run_execution_socket_blocked is True and data.no_socket_transport is True,
        external_api_blocked=data.dry_run_execution_external_api_blocked is True and data.external_api_requested is not True,
        risks=risks,
        details=("network_execution_blocked", "external_api_blocked"),
    )


def define_dry_run_execution_http_websocket_socket_block_policy(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput | Mapping[str, Any] | None,
) -> DryRunExecutionNetworkBlockPolicy:
    data = _coerce_input(data)
    passed = (
        data.dry_run_execution_http_websocket_socket_block_policy_defined is True
        and data.dry_run_execution_http_blocked is True
        and data.dry_run_execution_websocket_blocked is True
        and data.dry_run_execution_socket_blocked is True
        and data.network_transport_requested is not True
    )
    risks = () if passed else (
        PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED,
    )
    return DryRunExecutionNetworkBlockPolicy(
        name="dry_run_execution_http_websocket_socket_block_policy",
        score=_metric_score(data.http_websocket_socket_block_score, None, passed),
        defined=data.dry_run_execution_http_websocket_socket_block_policy_defined is True,
        network_execution_blocked=data.dry_run_execution_network_blocked is True and data.network_transport_requested is not True,
        http_blocked=data.dry_run_execution_http_blocked is True and data.no_http_transport is True,
        websocket_blocked=data.dry_run_execution_websocket_blocked is True and data.no_websocket_transport is True,
        socket_blocked=data.dry_run_execution_socket_blocked is True and data.no_socket_transport is True,
        external_api_blocked=data.dry_run_execution_external_api_blocked is True,
        risks=risks,
        details=("http_websocket_socket_blocked",),
    )


def define_dry_run_execution_account_read_only_policy(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput | Mapping[str, Any] | None,
) -> DryRunExecutionAccountReadOnlyPolicy:
    data = _coerce_input(data)
    passed = (
        data.dry_run_execution_account_read_only_policy_defined is True
        and data.dry_run_execution_account_access_blocked is True
        and data.dry_run_execution_account_mutations_blocked is True
        and data.account_access_requested is not True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_UNSAFE,)
    return DryRunExecutionAccountReadOnlyPolicy(
        score=_metric_score(data.account_read_only_score, None, passed),
        defined=data.dry_run_execution_account_read_only_policy_defined is True,
        active_account_access_blocked=data.dry_run_execution_account_access_blocked is True and data.account_access_requested is not True,
        account_mutations_blocked=data.dry_run_execution_account_mutations_blocked is True,
        schema_only_account_review=True,
        risks=risks,
        details=("active_account_access_blocked",),
    )


def define_dry_run_execution_market_data_read_only_policy(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput | Mapping[str, Any] | None,
) -> DryRunExecutionMarketDataReadOnlyPolicy:
    data = _coerce_input(data)
    passed = (
        data.dry_run_execution_market_data_read_only_policy_defined is True
        and data.dry_run_execution_market_data_live_subscription_blocked is True
        and data.dry_run_execution_market_data_network_request_blocked is True
        and data.no_external_api is True
    )
    risks = () if passed else (
        PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_UNSAFE,
    )
    return DryRunExecutionMarketDataReadOnlyPolicy(
        score=_metric_score(data.market_data_read_only_score, None, passed),
        defined=data.dry_run_execution_market_data_read_only_policy_defined is True,
        read_only_market_data_only=True,
        live_subscription_blocked=data.dry_run_execution_market_data_live_subscription_blocked is True,
        network_request_blocked=data.dry_run_execution_market_data_network_request_blocked is True,
        schema_or_synthetic_only=True,
        risks=risks,
        details=("market_data_schema_or_synthetic_only",),
    )


def define_dry_run_execution_order_blocking_policy(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput | Mapping[str, Any] | None,
) -> DryRunExecutionOrderBlockingPolicy:
    data = _coerce_input(data)
    passed = (
        data.dry_run_execution_order_blocking_policy_defined is True
        and data.dry_run_execution_order_execution_blocked is True
        and data.dry_run_execution_cancel_replace_blocked is True
        and data.order_execution_requested is not True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_ORDER_BLOCKING_UNSAFE,)
    return DryRunExecutionOrderBlockingPolicy(
        score=_metric_score(data.order_blocking_score, None, passed),
        defined=data.dry_run_execution_order_blocking_policy_defined is True,
        order_execution_blocked=data.dry_run_execution_order_execution_blocked is True and data.order_execution_requested is not True,
        real_order_blocked=data.no_real_order is True,
        cancel_replace_blocked=data.dry_run_execution_cancel_replace_blocked is True,
        risks=risks,
        details=("submit_cancel_replace_blocked",),
    )


def define_dry_run_execution_position_mutation_block_policy(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput | Mapping[str, Any] | None,
) -> DryRunExecutionPositionMutationBlockPolicy:
    data = _coerce_input(data)
    passed = (
        data.dry_run_execution_position_mutation_block_policy_defined is True
        and data.dry_run_execution_position_mutation_blocked is True
        and data.position_mutation_requested is not True
    )
    risks = () if passed else (
        PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_UNSAFE,
    )
    return DryRunExecutionPositionMutationBlockPolicy(
        score=_metric_score(data.position_mutation_block_score, None, passed),
        defined=data.dry_run_execution_position_mutation_block_policy_defined is True,
        position_mutation_blocked=data.dry_run_execution_position_mutation_blocked is True
        and data.position_mutation_requested is not True,
        position_request_absent=data.position_mutation_requested is not True,
        close_modify_blocked=data.dry_run_execution_position_mutation_blocked is True,
        risks=risks,
        details=("position_close_modify_blocked",),
    )


def define_dry_run_execution_observability_plan(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput | Mapping[str, Any] | None,
) -> DryRunExecutionObservabilityPlan:
    data = _coerce_input(data)
    passed = data.dry_run_execution_observability_plan_defined is True
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_OBSERVABILITY_MISSING,)
    return DryRunExecutionObservabilityPlan(
        score=_metric_score(data.observability_score, None, passed),
        defined=passed,
        offline_events_defined=passed,
        connection_attempt_logging_disabled=True,
        sensitive_values_redacted=True,
        risks=risks,
        details=("offline_observability_events",),
    )


def define_dry_run_execution_journal_plan(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput | Mapping[str, Any] | None,
) -> DryRunExecutionJournalPlan:
    data = _coerce_input(data)
    passed = data.dry_run_execution_journal_plan_defined is True
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_JOURNAL_MISSING,)
    return DryRunExecutionJournalPlan(
        score=_metric_score(data.journal_score, None, passed),
        defined=passed,
        offline_journal_required=passed,
        sensitive_values_redacted=True,
        no_secret_material_logged=True,
        risks=risks,
        details=("offline_journal_only",),
    )


def define_dry_run_execution_human_approval_plan(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput | Mapping[str, Any] | None,
) -> DryRunExecutionHumanApprovalPlan:
    data = _coerce_input(data)
    passed = data.dry_run_execution_human_approval_plan_defined is True and data.dry_run_execution_human_approval_required is True
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_HUMAN_APPROVAL_MISSING,)
    return DryRunExecutionHumanApprovalPlan(
        score=_metric_score(data.human_approval_score, None, passed),
        defined=data.dry_run_execution_human_approval_plan_defined is True,
        human_approval_required=data.dry_run_execution_human_approval_required is True,
        approval_before_safety_gate=True,
        preparation_review_evidence_required=True,
        risks=risks,
        details=("human_approval_required_before_execution_safety_gate",),
    )


def define_dry_run_execution_stop_conditions_plan(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput | Mapping[str, Any] | None,
) -> DryRunExecutionStopConditionPlan:
    data = _coerce_input(data)
    passed = data.dry_run_execution_stop_conditions_plan_defined is True
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_STOP_CONDITIONS_MISSING,)
    return DryRunExecutionStopConditionPlan(
        score=_metric_score(data.stop_conditions_score, None, passed),
        defined=passed,
        stop_on_secret_read=True,
        stop_on_network_request=True,
        stop_on_order_or_position_request=True,
        stop_on_account_access_request=True,
        risks=risks,
        details=("stop_on_boundary_violation",),
    )


def define_dry_run_execution_success_criteria(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput | Mapping[str, Any] | None,
) -> DryRunExecutionSuccessCriteria:
    data = _coerce_input(data)
    passed = data.dry_run_execution_success_criteria_defined is True
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_SUCCESS_CRITERIA_MISSING,)
    return DryRunExecutionSuccessCriteria(
        score=_metric_score(data.success_criteria_score, None, passed),
        defined=passed,
        requires_no_real_connection=True,
        requires_no_secret_read=True,
        requires_all_guards_verified=True,
        risks=risks,
        details=("success_requires_no_real_boundary_violation",),
    )


def define_dry_run_execution_failure_criteria(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput | Mapping[str, Any] | None,
) -> DryRunExecutionFailureCriteria:
    data = _coerce_input(data)
    passed = data.dry_run_execution_failure_criteria_defined is True
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_FAILURE_CRITERIA_MISSING,)
    return DryRunExecutionFailureCriteria(
        score=_metric_score(data.failure_criteria_score, None, passed),
        defined=passed,
        failure_on_secret_network_order_position_or_account=True,
        failure_on_data_access=True,
        failure_on_real_execution=True,
        risks=risks,
        details=("failure_on_any_boundary_violation",),
    )


def define_dry_run_execution_audit_plan(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput | Mapping[str, Any] | None,
) -> DryRunExecutionAuditPlan:
    data = _coerce_input(data)
    passed = data.dry_run_execution_audit_plan_defined is True
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_AUDIT_PLAN_MISSING,)
    return DryRunExecutionAuditPlan(
        score=_metric_score(data.audit_plan_score, None, passed),
        defined=passed,
        audit_events_defined=passed,
        offline_evidence_required=True,
        next_safety_gate_trace_required=True,
        risks=risks,
        details=("audit_packet_for_execution_safety_gate",),
    )


def _plan_objects(data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput) -> tuple[Any, ...]:
    return (
        define_dry_run_execution_scope(data),
        define_dry_run_execution_sequence(data),
        define_dry_run_execution_preconditions(data),
        define_dry_run_execution_credentials_reference_policy(data),
        define_dry_run_execution_no_secret_read_policy(data),
        define_dry_run_execution_network_block_policy(data),
        define_dry_run_execution_http_websocket_socket_block_policy(data),
        define_dry_run_execution_account_read_only_policy(data),
        define_dry_run_execution_market_data_read_only_policy(data),
        define_dry_run_execution_order_blocking_policy(data),
        define_dry_run_execution_position_mutation_block_policy(data),
        define_dry_run_execution_observability_plan(data),
        define_dry_run_execution_journal_plan(data),
        define_dry_run_execution_human_approval_plan(data),
        define_dry_run_execution_stop_conditions_plan(data),
        define_dry_run_execution_success_criteria(data),
        define_dry_run_execution_failure_criteria(data),
        define_dry_run_execution_audit_plan(data),
    )


def compute_read_only_connection_dry_run_execution_plan_score(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlyConnectionDryRunExecutionPlanScore:
    data = _coerce_input(data)
    review_score = _metric_score(
        data.preparation_review_score,
        _get(_review(data), "review_score"),
        validate_dry_run_preparation_review_approval(data),
    )
    scope = define_dry_run_execution_scope(data)
    sequence = define_dry_run_execution_sequence(data)
    preconditions = define_dry_run_execution_preconditions(data)
    credentials = define_dry_run_execution_credentials_reference_policy(data)
    no_secret = define_dry_run_execution_no_secret_read_policy(data)
    network = define_dry_run_execution_network_block_policy(data)
    transports = define_dry_run_execution_http_websocket_socket_block_policy(data)
    account = define_dry_run_execution_account_read_only_policy(data)
    market_data = define_dry_run_execution_market_data_read_only_policy(data)
    order = define_dry_run_execution_order_blocking_policy(data)
    position = define_dry_run_execution_position_mutation_block_policy(data)
    observability = define_dry_run_execution_observability_plan(data)
    journal = define_dry_run_execution_journal_plan(data)
    human = define_dry_run_execution_human_approval_plan(data)
    stop = define_dry_run_execution_stop_conditions_plan(data)
    success = define_dry_run_execution_success_criteria(data)
    failure = define_dry_run_execution_failure_criteria(data)
    audit = define_dry_run_execution_audit_plan(data)
    values = (
        review_score,
        scope.score,
        sequence.score,
        preconditions.score,
        credentials.score,
        no_secret.score,
        network.score,
        transports.score,
        account.score,
        market_data.score,
        order.score,
        position.score,
        observability.score,
        journal.score,
        human.score,
        stop.score,
        success.score,
        failure.score,
        audit.score,
    )
    return PaperBrokerReadOnlyConnectionDryRunExecutionPlanScore(
        overall_score=_average(values),
        preparation_review_score=review_score,
        scope_score=scope.score,
        sequence_score=sequence.score,
        precondition_score=preconditions.score,
        credential_policy_score=credentials.score,
        no_secret_read_score=no_secret.score,
        network_block_score=network.score,
        http_websocket_socket_block_score=transports.score,
        account_read_only_score=account.score,
        market_data_read_only_score=market_data.score,
        order_blocking_score=order.score,
        position_mutation_block_score=position.score,
        observability_score=observability.score,
        journal_score=journal.score,
        human_approval_score=human.score,
        stop_conditions_score=stop.score,
        success_criteria_score=success.score,
        failure_criteria_score=failure.score,
        audit_plan_score=audit.score,
    )


def detect_read_only_connection_dry_run_execution_plan_risks(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput | Mapping[str, Any] | None,
) -> tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk, ...]:
    data = _coerce_input(data)
    risks: list[PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk] = []
    if not validate_dry_run_preparation_review_approval(data):
        risks.append(PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_PREPARATION_REVIEW_NOT_APPROVED)
    for plan in _plan_objects(data):
        risks.extend(_as_tuple(_get(plan, "risks", ())))
    if not _offline_boundary(data):
        risks.append(PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DATA_ACCESS_VIOLATION)
    if data.paper_broker_read_only_connection_dry_run_execution_safety_gate_requested is True:
        risks.append(
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE
        )
    return _dedupe(risks)


def generate_read_only_connection_dry_run_execution_plan_recommendations(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput | Mapping[str, Any] | None,
) -> tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation, ...]:
    risks = detect_read_only_connection_dry_run_execution_plan_risks(data)
    if not risks:
        return (
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN_SUITE,
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE,
        )
    mapping = {
        PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_PREPARATION_REVIEW_NOT_APPROVED: PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation.APPROVE_DRY_RUN_PREPARATION_REVIEW_FIRST,
        PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_SCOPE_UNCLEAR: PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation.DEFINE_DRY_RUN_EXECUTION_SCOPE,
        PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_SEQUENCE_MISSING: PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation.DEFINE_DRY_RUN_EXECUTION_SEQUENCE,
        PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_PRECONDITION_MISSING: PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation.DEFINE_DRY_RUN_EXECUTION_PRECONDITIONS,
        PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_CREDENTIAL_POLICY_UNSAFE: PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation.HARDEN_DRY_RUN_EXECUTION_CREDENTIAL_POLICY,
        PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_SECRET_READ_POLICY_UNSAFE: PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation.HARDEN_DRY_RUN_EXECUTION_NO_SECRET_READ_POLICY,
        PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_NETWORK_NOT_BLOCKED: PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation.BLOCK_DRY_RUN_EXECUTION_NETWORK,
        PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED: PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation.BLOCK_DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET,
        PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_UNSAFE: PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation.HARDEN_DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY,
        PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_UNSAFE: PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation.HARDEN_DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY,
        PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_ORDER_BLOCKING_UNSAFE: PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation.HARDEN_DRY_RUN_EXECUTION_ORDER_BLOCKING,
        PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_UNSAFE: PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation.HARDEN_DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK,
        PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_OBSERVABILITY_MISSING: PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation.COMPLETE_DRY_RUN_EXECUTION_OBSERVABILITY,
        PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_JOURNAL_MISSING: PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation.COMPLETE_DRY_RUN_EXECUTION_JOURNAL,
        PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_HUMAN_APPROVAL_MISSING: PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation.REQUIRE_DRY_RUN_EXECUTION_HUMAN_APPROVAL,
        PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_STOP_CONDITIONS_MISSING: PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation.DEFINE_DRY_RUN_EXECUTION_STOP_CONDITIONS,
        PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_SUCCESS_CRITERIA_MISSING: PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation.DEFINE_DRY_RUN_EXECUTION_SUCCESS_FAILURE_CRITERIA,
        PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_FAILURE_CRITERIA_MISSING: PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation.DEFINE_DRY_RUN_EXECUTION_SUCCESS_FAILURE_CRITERIA,
        PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_AUDIT_PLAN_MISSING: PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation.DEFINE_DRY_RUN_EXECUTION_AUDIT_PLAN,
        PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION: PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation.RESTORE_OFFLINE_BOUNDARIES,
        PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DATA_ACCESS_VIOLATION: PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation.REMOVE_DATA_ACCESS,
        PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE: PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE,
    }
    recommendations = [
        PaperBrokerReadOnlyConnectionDryRunExecutionPlanRecommendation.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE
    ]
    recommendations.extend(mapping[risk] for risk in risks if risk in mapping)
    return _dedupe(recommendations)


def _decision_for_risks(
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk, ...],
) -> PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision:
    if not risks:
        return PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN
    if PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_PREPARATION_REVIEW_NOT_APPROVED in risks:
        return PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_PREPARATION_REVIEW_FIXES
    if any(
        risk in risks
        for risk in (
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION,
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DATA_ACCESS_VIOLATION,
        )
    ):
        return PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_SCOPE_FIXES
    checks = (
        (
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_SCOPE_UNCLEAR,
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_SCOPE_FIXES,
        ),
        (
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_SEQUENCE_MISSING,
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_SEQUENCE_FIXES,
        ),
        (
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_PRECONDITION_MISSING,
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_PRECONDITION_FIXES,
        ),
        (
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_CREDENTIAL_POLICY_UNSAFE,
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_CREDENTIAL_POLICY_FIXES,
        ),
        (
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_SECRET_READ_POLICY_UNSAFE,
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_NO_SECRET_READ_FIXES,
        ),
        (
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_UNSAFE,
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_FIXES,
        ),
        (
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_UNSAFE,
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_FIXES,
        ),
        (
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_ORDER_BLOCKING_UNSAFE,
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_ORDER_BLOCKING_FIXES,
        ),
        (
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_UNSAFE,
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_FIXES,
        ),
        (
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_OBSERVABILITY_MISSING,
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_OBSERVABILITY_FIXES,
        ),
        (
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_JOURNAL_MISSING,
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_JOURNAL_FIXES,
        ),
        (
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_HUMAN_APPROVAL_MISSING,
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_HUMAN_APPROVAL_FIXES,
        ),
        (
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_STOP_CONDITIONS_MISSING,
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_STOP_CONDITION_FIXES,
        ),
        (
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_AUDIT_PLAN_MISSING,
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_AUDIT_FIXES,
        ),
    )
    if any(
        risk in risks
        for risk in (
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_NETWORK_NOT_BLOCKED,
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED,
        )
    ):
        return PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_NETWORK_BLOCK_FIXES
    if any(
        risk in risks
        for risk in (
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_SUCCESS_CRITERIA_MISSING,
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk.DRY_RUN_EXECUTION_FAILURE_CRITERIA_MISSING,
        )
    ):
        return PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.REQUIRE_DRY_RUN_EXECUTION_SUCCESS_FAILURE_FIXES
    for risk, decision in checks:
        if risk in risks:
            return decision
    return PaperBrokerReadOnlyConnectionDryRunExecutionPlanDecision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN


def _state_for_result(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput,
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPlanRisk, ...],
    score: PaperBrokerReadOnlyConnectionDryRunExecutionPlanScore,
) -> PaperBrokerReadOnlyConnectionDryRunExecutionPlanState:
    if data.paper_broker_read_only_connection_dry_run_preparation_review is None:
        return PaperBrokerReadOnlyConnectionDryRunExecutionPlanState.DRY_RUN_EXECUTION_PLAN_INPUT_INVALID
    if not risks and score.overall_score >= 85:
        return (
            PaperBrokerReadOnlyConnectionDryRunExecutionPlanState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE
        )
    if risks:
        return PaperBrokerReadOnlyConnectionDryRunExecutionPlanState.DRY_RUN_EXECUTION_PLAN_BLOCKED
    if score.overall_score >= 70:
        return PaperBrokerReadOnlyConnectionDryRunExecutionPlanState.DRY_RUN_EXECUTION_PLAN_COMPLETED_WITH_WARNINGS
    return PaperBrokerReadOnlyConnectionDryRunExecutionPlanState.NOT_READY


def evaluate_paper_broker_read_only_connection_dry_run_execution_plan(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPlanInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlyConnectionDryRunExecutionPlanResult:
    data = _coerce_input(data)
    score = compute_read_only_connection_dry_run_execution_plan_score(data)
    risks = detect_read_only_connection_dry_run_execution_plan_risks(data)
    recommendations = generate_read_only_connection_dry_run_execution_plan_recommendations(data)
    decision = _decision_for_risks(risks)
    state = _state_for_result(data, risks, score)
    return PaperBrokerReadOnlyConnectionDryRunExecutionPlanResult(
        state=state,
        decision=decision,
        execution_plan_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        recommendations=recommendations,
        dry_run_execution_scope=define_dry_run_execution_scope(data),
        dry_run_execution_sequence=define_dry_run_execution_sequence(data),
        dry_run_execution_preconditions=define_dry_run_execution_preconditions(data),
        dry_run_execution_credentials_reference_policy=define_dry_run_execution_credentials_reference_policy(data),
        dry_run_execution_no_secret_read_policy=define_dry_run_execution_no_secret_read_policy(data),
        dry_run_execution_network_block_policy=define_dry_run_execution_network_block_policy(data),
        dry_run_execution_http_websocket_socket_block_policy=define_dry_run_execution_http_websocket_socket_block_policy(
            data
        ),
        dry_run_execution_account_read_only_policy=define_dry_run_execution_account_read_only_policy(data),
        dry_run_execution_market_data_read_only_policy=define_dry_run_execution_market_data_read_only_policy(data),
        dry_run_execution_order_blocking_policy=define_dry_run_execution_order_blocking_policy(data),
        dry_run_execution_position_mutation_block_policy=define_dry_run_execution_position_mutation_block_policy(data),
        dry_run_execution_observability_plan=define_dry_run_execution_observability_plan(data),
        dry_run_execution_journal_plan=define_dry_run_execution_journal_plan(data),
        dry_run_execution_human_approval_plan=define_dry_run_execution_human_approval_plan(data),
        dry_run_execution_stop_conditions_plan=define_dry_run_execution_stop_conditions_plan(data),
        dry_run_execution_success_criteria=define_dry_run_execution_success_criteria(data),
        dry_run_execution_failure_criteria=define_dry_run_execution_failure_criteria(data),
        dry_run_execution_audit_plan=define_dry_run_execution_audit_plan(data),
        offline_only=True,
        summary=(
            "Paper broker read-only connection dry-run execution plan is approved for execution safety gate."
            if not risks
            else "Paper broker read-only connection dry-run execution plan is blocked until planning risks are fixed."
        ),
    )


def render_paper_broker_read_only_connection_dry_run_execution_plan_markdown(
    result: PaperBrokerReadOnlyConnectionDryRunExecutionPlanResult | Mapping[str, Any],
) -> str:
    if isinstance(result, Mapping):
        result = PaperBrokerReadOnlyConnectionDryRunExecutionPlanResult(**dict(result))
    risks = ", ".join(risk.value for risk in result.risks) or "none"
    recommendations = ", ".join(recommendation.value for recommendation in result.recommendations) or "none"
    sections = (
        ("scope", result.dry_run_execution_scope),
        ("sequence", result.dry_run_execution_sequence),
        ("preconditions", result.dry_run_execution_preconditions),
        ("credentials", result.dry_run_execution_credentials_reference_policy),
        ("no_secret_read", result.dry_run_execution_no_secret_read_policy),
        ("network_block", result.dry_run_execution_network_block_policy),
        ("http_websocket_socket_block", result.dry_run_execution_http_websocket_socket_block_policy),
        ("account_read_only", result.dry_run_execution_account_read_only_policy),
        ("market_data_read_only", result.dry_run_execution_market_data_read_only_policy),
        ("order_blocking", result.dry_run_execution_order_blocking_policy),
        ("position_mutation_block", result.dry_run_execution_position_mutation_block_policy),
        ("observability", result.dry_run_execution_observability_plan),
        ("journal", result.dry_run_execution_journal_plan),
        ("human_approval", result.dry_run_execution_human_approval_plan),
        ("stop_conditions", result.dry_run_execution_stop_conditions_plan),
        ("success_criteria", result.dry_run_execution_success_criteria),
        ("failure_criteria", result.dry_run_execution_failure_criteria),
        ("audit_plan", result.dry_run_execution_audit_plan),
    )
    lines = [
        "# Paper Broker Read-Only Connection Dry Run Execution Plan",
        "",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Execution plan score: {result.execution_plan_score}",
        f"- Offline only: {result.offline_only}",
        f"- Risks: {risks}",
        f"- Recommendations: {recommendations}",
        "",
        "## Enforced Execution Plan Boundaries",
        "- No dry-run execution or broker connection",
        "- No API key or environment variable read",
        "- No HTTP, websocket, socket, network transport, or external API",
        "- No order execution, position mutation, or active account access",
        "- No data/ access",
        "",
        "## Plan Sections",
    ]
    for name, section in sections:
        lines.append(f"- {name}: score={section.score}, defined={section.defined}, risks={len(section.risks)}")
    if result.summary:
        lines.extend(("", f"Summary: {result.summary}"))
    return "\n".join(lines)
