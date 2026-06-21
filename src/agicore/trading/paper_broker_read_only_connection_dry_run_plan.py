"""Offline plan for a future paper broker read-only connection dry run."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_broker_read_only_connection_dry_run_plan_models import (
    DryRunAccountReadOnlyPolicy,
    DryRunCredentialsReferencePolicy,
    DryRunEnvironmentBoundary,
    DryRunFailureCriteria,
    DryRunHumanApprovalPlan,
    DryRunJournalPlan,
    DryRunMarketDataReadOnlyPolicy,
    DryRunNetworkBlockPolicy,
    DryRunNoSecretReadPolicy,
    DryRunObservabilityPlan,
    DryRunOrderBlockingPolicy,
    DryRunPositionMutationBlockPolicy,
    DryRunPrecondition,
    DryRunScope,
    DryRunStopConditionPlan,
    DryRunSuccessCriteria,
    PaperBrokerReadOnlyConnectionDryRunPlanDecision,
    PaperBrokerReadOnlyConnectionDryRunPlanInput,
    PaperBrokerReadOnlyConnectionDryRunPlanRecommendation,
    PaperBrokerReadOnlyConnectionDryRunPlanResult,
    PaperBrokerReadOnlyConnectionDryRunPlanRisk,
    PaperBrokerReadOnlyConnectionDryRunPlanScore,
    PaperBrokerReadOnlyConnectionDryRunPlanState,
)


def _coerce_input(
    data: PaperBrokerReadOnlyConnectionDryRunPlanInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlyConnectionDryRunPlanInput:
    if data is None:
        return PaperBrokerReadOnlyConnectionDryRunPlanInput()
    if isinstance(data, PaperBrokerReadOnlyConnectionDryRunPlanInput):
        return data
    allowed = {field.name for field in fields(PaperBrokerReadOnlyConnectionDryRunPlanInput)}
    payload = {key: value for key, value in dict(data).items() if key in allowed}
    return PaperBrokerReadOnlyConnectionDryRunPlanInput(**payload)


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


def _review(data: PaperBrokerReadOnlyConnectionDryRunPlanInput) -> Any:
    return data.paper_broker_read_only_connection_preparation_review


def _upstream_items(data: PaperBrokerReadOnlyConnectionDryRunPlanInput) -> tuple[Any, ...]:
    return (
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


def _upstream_risks(data: PaperBrokerReadOnlyConnectionDryRunPlanInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperBrokerReadOnlyConnectionDryRunPlanInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _offline_boundary(data: PaperBrokerReadOnlyConnectionDryRunPlanInput) -> bool:
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


def _data_boundary(data: PaperBrokerReadOnlyConnectionDryRunPlanInput) -> bool:
    return data.data_access_requested is not True and not _has_upstream_risk(data, "DATA_ACCESS", "DATA/")


def validate_connection_preparation_review_approval(
    data: PaperBrokerReadOnlyConnectionDryRunPlanInput | Mapping[str, Any] | None,
) -> bool:
    data = _coerce_input(data)
    if data.connection_preparation_review_approved is False:
        return False
    review = _review(data)
    if review is None:
        return False
    if _as_tuple(_get(review, "risks", ())) or _as_tuple(_get(review, "blockers", ())) or _get(review, "offline_only", True) is not True:
        return False
    if data.connection_preparation_review_approved is True:
        return True
    return _state_contains(
        review,
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW",
    )


def define_dry_run_scope(data: PaperBrokerReadOnlyConnectionDryRunPlanInput | Mapping[str, Any] | None) -> DryRunScope:
    data = _coerce_input(data)
    passed = data.dry_run_scope_defined is True and data.plan_only is True and data.dry_run_executed is not True
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_SCOPE_UNCLEAR,)
    score = _metric_score(data.dry_run_scope_score, None, passed)
    return DryRunScope(
        score=score,
        defined=data.dry_run_scope_defined is True,
        plan_only=data.plan_only is True,
        read_only_only=data.no_real_order is True and data.no_position_mutation is True,
        dry_run_not_executed=data.dry_run_executed is not True,
        allowed_actions=("define_future_read_only_dry_run", "verify_offline_guards", "document_success_failure_criteria"),
        prohibited_actions=("connect_broker", "read_secret", "open_network_transport", "send_order", "mutate_position"),
        risks=risks,
        details=("Plan-only read-only connection dry run scope; no dry run execution in this phase.",),
    )


def define_dry_run_environment_boundaries(
    data: PaperBrokerReadOnlyConnectionDryRunPlanInput | Mapping[str, Any] | None,
) -> DryRunEnvironmentBoundary:
    data = _coerce_input(data)
    passed = (
        data.dry_run_environment_boundaries_defined is True
        and data.offline_mode_enforced is True
        and data.sandbox_mode_enforced is True
        and data.broker_connection_disabled is True
        and data.no_real_broker is True
        and data.no_alpaca_real is True
        and data.no_http_transport is True
        and data.no_websocket_transport is True
        and data.no_socket_transport is True
        and data.no_external_api is True
        and _data_boundary(data)
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_ENVIRONMENT_BOUNDARY_MISSING,)
    score = _metric_score(data.dry_run_boundary_score, None, passed)
    return DryRunEnvironmentBoundary(
        score=score,
        defined=data.dry_run_environment_boundaries_defined is True,
        offline_only=data.offline_mode_enforced is True,
        sandbox_only=data.sandbox_mode_enforced is True,
        broker_connection_disabled=data.broker_connection_disabled is True,
        network_transport_blocked=(
            data.no_http_transport is True and data.no_websocket_transport is True and data.no_socket_transport is True
        ),
        data_access_blocked=_data_boundary(data),
        risks=risks,
        details=("Broker, Alpaca, network transport, API, account, order, position, and data access stay blocked.",),
    )


def define_dry_run_preconditions(
    data: PaperBrokerReadOnlyConnectionDryRunPlanInput | Mapping[str, Any] | None,
) -> DryRunPrecondition:
    data = _coerce_input(data)
    review_ok = validate_connection_preparation_review_approval(data)
    passed = (
        data.dry_run_preconditions_defined is True
        and review_ok
        and data.dry_run_human_approval_required is True
        and data.dry_run_stop_conditions_plan_defined is True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_PRECONDITION_MISSING,)
    score = _metric_score(data.dry_run_precondition_score, None, passed)
    return DryRunPrecondition(
        score=score,
        defined=data.dry_run_preconditions_defined is True,
        preparation_review_required=True,
        human_approval_required=data.dry_run_human_approval_required is True,
        safety_gate_required=True,
        stop_conditions_required=data.dry_run_stop_conditions_plan_defined is True,
        risks=risks,
        details=("Preparation review approval, human approval, safety gate, and stop conditions are mandatory.",),
    )


def define_dry_run_credentials_reference_policy(
    data: PaperBrokerReadOnlyConnectionDryRunPlanInput | Mapping[str, Any] | None,
) -> DryRunCredentialsReferencePolicy:
    data = _coerce_input(data)
    passed = (
        data.dry_run_credentials_reference_policy_defined is True
        and data.dry_run_credentials_reference_only is True
        and data.no_api_key_read is True
        and data.no_env_var_read is True
        and data.no_hardcoded_secrets is True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_CREDENTIAL_POLICY_UNSAFE,)
    score = _metric_score(data.dry_run_credential_policy_score, None, passed)
    return DryRunCredentialsReferencePolicy(
        score=score,
        defined=data.dry_run_credentials_reference_policy_defined is True,
        reference_only=data.dry_run_credentials_reference_only is True,
        no_secret_values=data.no_hardcoded_secrets is True,
        no_api_key_read=data.no_api_key_read is True,
        no_env_var_read=data.no_env_var_read is True,
        risks=risks,
        details=("Only credential references are allowed; no key, environment variable, or secret value is read.",),
    )


def define_dry_run_no_secret_read_policy(
    data: PaperBrokerReadOnlyConnectionDryRunPlanInput | Mapping[str, Any] | None,
) -> DryRunNoSecretReadPolicy:
    data = _coerce_input(data)
    passed = (
        data.dry_run_no_secret_read_policy_defined is True
        and data.dry_run_secret_read_blocked is True
        and data.no_api_key_read is True
        and data.no_env_var_read is True
        and data.no_hardcoded_secrets is True
        and data.api_key_read_requested is not True
        and data.env_var_read_requested is not True
        and data.hardcoded_secret_detected is not True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_SECRET_READ_POLICY_UNSAFE,)
    score = _metric_score(data.dry_run_no_secret_read_score, None, passed)
    return DryRunNoSecretReadPolicy(
        score=score,
        defined=data.dry_run_no_secret_read_policy_defined is True,
        no_api_key_read=data.no_api_key_read is True and data.api_key_read_requested is not True,
        no_env_var_read=data.no_env_var_read is True and data.env_var_read_requested is not True,
        no_hardcoded_secret=data.no_hardcoded_secrets is True and data.hardcoded_secret_detected is not True,
        policy_enforced=data.dry_run_secret_read_blocked is True,
        risks=risks,
        details=("The dry-run plan must fail closed on any secret, API key, or environment-variable read request.",),
    )


def define_dry_run_network_block_policy(
    data: PaperBrokerReadOnlyConnectionDryRunPlanInput | Mapping[str, Any] | None,
) -> DryRunNetworkBlockPolicy:
    data = _coerce_input(data)
    passed = (
        data.dry_run_network_block_policy_defined is True
        and data.dry_run_network_blocked is True
        and data.dry_run_external_api_blocked is True
        and data.network_transport_requested is not True
        and data.external_api_requested is not True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_NETWORK_NOT_BLOCKED,)
    score = _metric_score(data.dry_run_network_block_score, None, passed)
    return DryRunNetworkBlockPolicy(
        score=score,
        defined=data.dry_run_network_block_policy_defined is True,
        network_execution_blocked=data.dry_run_network_blocked is True and data.network_transport_requested is not True,
        http_blocked=data.no_http_transport is True,
        websocket_blocked=data.no_websocket_transport is True,
        socket_blocked=data.no_socket_transport is True,
        external_api_blocked=data.dry_run_external_api_blocked is True and data.external_api_requested is not True,
        risks=risks,
        details=("All network execution and external API access remain blocked by policy.",),
    )


def define_dry_run_http_websocket_socket_block_policy(
    data: PaperBrokerReadOnlyConnectionDryRunPlanInput | Mapping[str, Any] | None,
) -> DryRunNetworkBlockPolicy:
    data = _coerce_input(data)
    passed = (
        data.dry_run_http_websocket_socket_block_policy_defined is True
        and data.dry_run_http_blocked is True
        and data.dry_run_websocket_blocked is True
        and data.dry_run_socket_blocked is True
        and data.no_http_transport is True
        and data.no_websocket_transport is True
        and data.no_socket_transport is True
        and data.network_transport_requested is not True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED,)
    score = _metric_score(data.dry_run_http_websocket_socket_block_score, None, passed)
    return DryRunNetworkBlockPolicy(
        name="dry_run_http_websocket_socket_block_policy",
        score=score,
        defined=data.dry_run_http_websocket_socket_block_policy_defined is True,
        network_execution_blocked=data.dry_run_network_blocked is True and data.network_transport_requested is not True,
        http_blocked=data.dry_run_http_blocked is True and data.no_http_transport is True,
        websocket_blocked=data.dry_run_websocket_blocked is True and data.no_websocket_transport is True,
        socket_blocked=data.dry_run_socket_blocked is True and data.no_socket_transport is True,
        external_api_blocked=data.dry_run_external_api_blocked is True,
        risks=risks,
        details=("HTTP, websocket, and raw socket transports are explicitly blocked for the planned dry run.",),
    )


def define_dry_run_account_read_only_policy(
    data: PaperBrokerReadOnlyConnectionDryRunPlanInput | Mapping[str, Any] | None,
) -> DryRunAccountReadOnlyPolicy:
    data = _coerce_input(data)
    passed = (
        data.dry_run_account_read_only_policy_defined is True
        and data.dry_run_account_access_blocked is True
        and data.dry_run_account_mutations_blocked is True
        and data.no_real_account_access is True
        and data.account_access_requested is not True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_ACCOUNT_READ_ONLY_UNSAFE,)
    score = _metric_score(data.dry_run_account_read_only_score, None, passed)
    return DryRunAccountReadOnlyPolicy(
        score=score,
        defined=data.dry_run_account_read_only_policy_defined is True,
        active_account_access_blocked=data.dry_run_account_access_blocked is True and data.account_access_requested is not True,
        account_mutations_blocked=data.dry_run_account_mutations_blocked is True,
        schema_only_account_review=data.no_real_account_access is True,
        risks=risks,
        details=("Account handling is schema-only/read-only; active account access and mutations are blocked.",),
    )


def define_dry_run_market_data_read_only_policy(
    data: PaperBrokerReadOnlyConnectionDryRunPlanInput | Mapping[str, Any] | None,
) -> DryRunMarketDataReadOnlyPolicy:
    data = _coerce_input(data)
    passed = (
        data.dry_run_market_data_read_only_policy_defined is True
        and data.dry_run_market_data_live_subscription_blocked is True
        and data.dry_run_market_data_network_request_blocked is True
        and data.no_external_api is True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_MARKET_DATA_READ_ONLY_UNSAFE,)
    score = _metric_score(data.dry_run_market_data_read_only_score, None, passed)
    return DryRunMarketDataReadOnlyPolicy(
        score=score,
        defined=data.dry_run_market_data_read_only_policy_defined is True,
        read_only_market_data_only=True,
        live_subscription_blocked=data.dry_run_market_data_live_subscription_blocked is True,
        network_request_blocked=data.dry_run_market_data_network_request_blocked is True,
        synthetic_or_schema_only=data.no_external_api is True,
        risks=risks,
        details=("Market-data policy is read-only and schema/synthetic only; live network subscriptions are blocked.",),
    )


def define_dry_run_order_blocking_policy(
    data: PaperBrokerReadOnlyConnectionDryRunPlanInput | Mapping[str, Any] | None,
) -> DryRunOrderBlockingPolicy:
    data = _coerce_input(data)
    passed = (
        data.dry_run_order_blocking_policy_defined is True
        and data.dry_run_order_execution_blocked is True
        and data.dry_run_cancel_replace_blocked is True
        and data.no_real_order is True
        and data.order_execution_requested is not True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_ORDER_BLOCKING_UNSAFE,)
    score = _metric_score(data.dry_run_order_blocking_score, None, passed)
    return DryRunOrderBlockingPolicy(
        score=score,
        defined=data.dry_run_order_blocking_policy_defined is True,
        order_execution_blocked=data.dry_run_order_execution_blocked is True and data.order_execution_requested is not True,
        real_order_blocked=data.no_real_order is True,
        cancel_replace_blocked=data.dry_run_cancel_replace_blocked is True,
        risks=risks,
        details=("Order submission, cancel, and replace paths must stay unavailable during the dry-run plan phase.",),
    )


def define_dry_run_position_mutation_block_policy(
    data: PaperBrokerReadOnlyConnectionDryRunPlanInput | Mapping[str, Any] | None,
) -> DryRunPositionMutationBlockPolicy:
    data = _coerce_input(data)
    passed = (
        data.dry_run_position_mutation_block_policy_defined is True
        and data.dry_run_position_mutation_blocked is True
        and data.no_position_mutation is True
        and data.position_mutation_requested is not True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_POSITION_MUTATION_BLOCK_UNSAFE,)
    score = _metric_score(data.dry_run_position_mutation_block_score, None, passed)
    return DryRunPositionMutationBlockPolicy(
        score=score,
        defined=data.dry_run_position_mutation_block_policy_defined is True,
        position_mutation_blocked=data.dry_run_position_mutation_blocked is True and data.position_mutation_requested is not True,
        position_request_absent=data.position_mutation_requested is not True,
        close_modify_blocked=data.dry_run_position_mutation_blocked is True,
        risks=risks,
        details=("Position close, modify, and mutation paths stay blocked.",),
    )


def define_dry_run_observability_plan(
    data: PaperBrokerReadOnlyConnectionDryRunPlanInput | Mapping[str, Any] | None,
) -> DryRunObservabilityPlan:
    data = _coerce_input(data)
    passed = data.dry_run_observability_plan_defined is True
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_OBSERVABILITY_PLAN_MISSING,)
    score = _metric_score(data.dry_run_observability_score, None, passed)
    return DryRunObservabilityPlan(
        score=score,
        defined=data.dry_run_observability_plan_defined is True,
        offline_events_defined=passed,
        connection_attempt_logging_disabled=True,
        sensitive_values_redacted=True,
        risks=risks,
        details=("Observability covers offline guard checks and excludes connection attempts or secret material.",),
    )


def define_dry_run_journal_plan(data: PaperBrokerReadOnlyConnectionDryRunPlanInput | Mapping[str, Any] | None) -> DryRunJournalPlan:
    data = _coerce_input(data)
    passed = data.dry_run_journal_plan_defined is True
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_JOURNAL_PLAN_MISSING,)
    score = _metric_score(data.dry_run_journal_score, None, passed)
    return DryRunJournalPlan(
        score=score,
        defined=data.dry_run_journal_plan_defined is True,
        offline_journal_required=passed,
        sensitive_values_redacted=True,
        no_secret_material_logged=True,
        risks=risks,
        details=("Journal entries are offline-only and redact any credential reference metadata.",),
    )


def define_dry_run_human_approval_plan(
    data: PaperBrokerReadOnlyConnectionDryRunPlanInput | Mapping[str, Any] | None,
) -> DryRunHumanApprovalPlan:
    data = _coerce_input(data)
    passed = data.dry_run_human_approval_plan_defined is True and data.dry_run_human_approval_required is True
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_HUMAN_APPROVAL_MISSING,)
    score = _metric_score(data.dry_run_human_approval_score, None, passed)
    return DryRunHumanApprovalPlan(
        score=score,
        defined=data.dry_run_human_approval_plan_defined is True,
        human_approval_required=data.dry_run_human_approval_required is True,
        approval_before_safety_gate=True,
        dry_run_plan_evidence_required=True,
        risks=risks,
        details=("Human approval is required before the next safety gate can be considered.",),
    )


def define_dry_run_stop_conditions_plan(
    data: PaperBrokerReadOnlyConnectionDryRunPlanInput | Mapping[str, Any] | None,
) -> DryRunStopConditionPlan:
    data = _coerce_input(data)
    passed = data.dry_run_stop_conditions_plan_defined is True
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_STOP_CONDITIONS_MISSING,)
    score = _metric_score(data.dry_run_stop_conditions_score, None, passed)
    return DryRunStopConditionPlan(
        score=score,
        defined=data.dry_run_stop_conditions_plan_defined is True,
        stop_on_secret_read=True,
        stop_on_network_request=True,
        stop_on_order_or_position_request=True,
        stop_on_account_access_request=True,
        risks=risks,
        details=("Any secret, network, order, position, or account access request is a stop condition.",),
    )


def define_dry_run_success_criteria(
    data: PaperBrokerReadOnlyConnectionDryRunPlanInput | Mapping[str, Any] | None,
) -> DryRunSuccessCriteria:
    data = _coerce_input(data)
    passed = data.dry_run_success_criteria_defined is True
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_SUCCESS_CRITERIA_MISSING,)
    score = _metric_score(data.dry_run_success_criteria_score, None, passed)
    return DryRunSuccessCriteria(
        score=score,
        defined=data.dry_run_success_criteria_defined is True,
        no_real_connection_attempted=True,
        all_guards_verified=passed,
        read_only_boundaries_preserved=True,
        risks=risks,
        details=("Success requires no real connection attempt and all read-only/offline guards verified.",),
    )


def define_dry_run_failure_criteria(
    data: PaperBrokerReadOnlyConnectionDryRunPlanInput | Mapping[str, Any] | None,
) -> DryRunFailureCriteria:
    data = _coerce_input(data)
    passed = data.dry_run_failure_criteria_defined is True
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_FAILURE_CRITERIA_MISSING,)
    score = _metric_score(data.dry_run_failure_criteria_score, None, passed)
    return DryRunFailureCriteria(
        score=score,
        defined=data.dry_run_failure_criteria_defined is True,
        fail_on_secret_read=True,
        fail_on_network_attempt=True,
        fail_on_order_or_position_request=True,
        fail_on_account_access_request=True,
        risks=risks,
        details=("Failure criteria are fail-closed on secret, network, order, position, or account access attempts.",),
    )


def _plan_objects(
    data: PaperBrokerReadOnlyConnectionDryRunPlanInput,
) -> tuple[Any, ...]:
    return (
        define_dry_run_scope(data),
        define_dry_run_environment_boundaries(data),
        define_dry_run_preconditions(data),
        define_dry_run_credentials_reference_policy(data),
        define_dry_run_no_secret_read_policy(data),
        define_dry_run_network_block_policy(data),
        define_dry_run_http_websocket_socket_block_policy(data),
        define_dry_run_account_read_only_policy(data),
        define_dry_run_market_data_read_only_policy(data),
        define_dry_run_order_blocking_policy(data),
        define_dry_run_position_mutation_block_policy(data),
        define_dry_run_observability_plan(data),
        define_dry_run_journal_plan(data),
        define_dry_run_human_approval_plan(data),
        define_dry_run_stop_conditions_plan(data),
        define_dry_run_success_criteria(data),
        define_dry_run_failure_criteria(data),
    )


def compute_read_only_connection_dry_run_plan_score(
    data: PaperBrokerReadOnlyConnectionDryRunPlanInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlyConnectionDryRunPlanScore:
    data = _coerce_input(data)
    review_score = _metric_score(
        data.connection_preparation_review_score,
        _get(_review(data), "review_score", _get(_review(data), "score", None)),
        validate_connection_preparation_review_approval(data),
    )
    scope = define_dry_run_scope(data)
    boundary = define_dry_run_environment_boundaries(data)
    preconditions = define_dry_run_preconditions(data)
    credential_policy = define_dry_run_credentials_reference_policy(data)
    no_secret = define_dry_run_no_secret_read_policy(data)
    network = define_dry_run_network_block_policy(data)
    http_ws_socket = define_dry_run_http_websocket_socket_block_policy(data)
    account = define_dry_run_account_read_only_policy(data)
    market_data = define_dry_run_market_data_read_only_policy(data)
    order = define_dry_run_order_blocking_policy(data)
    position = define_dry_run_position_mutation_block_policy(data)
    observability = define_dry_run_observability_plan(data)
    journal = define_dry_run_journal_plan(data)
    human = define_dry_run_human_approval_plan(data)
    stop = define_dry_run_stop_conditions_plan(data)
    success = define_dry_run_success_criteria(data)
    failure = define_dry_run_failure_criteria(data)
    values = (
        review_score,
        scope.score,
        boundary.score,
        preconditions.score,
        credential_policy.score,
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
        success.score,
        failure.score,
    )
    return PaperBrokerReadOnlyConnectionDryRunPlanScore(
        overall_score=_average(values),
        connection_preparation_review_score=review_score,
        scope_score=scope.score,
        boundary_score=boundary.score,
        precondition_score=preconditions.score,
        credential_policy_score=credential_policy.score,
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
        success_criteria_score=success.score,
        failure_criteria_score=failure.score,
    )


def detect_read_only_connection_dry_run_plan_risks(
    data: PaperBrokerReadOnlyConnectionDryRunPlanInput | Mapping[str, Any] | None,
) -> tuple[PaperBrokerReadOnlyConnectionDryRunPlanRisk, ...]:
    data = _coerce_input(data)
    risks: list[PaperBrokerReadOnlyConnectionDryRunPlanRisk] = []
    if not validate_connection_preparation_review_approval(data):
        risks.append(PaperBrokerReadOnlyConnectionDryRunPlanRisk.CONNECTION_PREPARATION_REVIEW_NOT_APPROVED)
    for item in _plan_objects(data):
        risks.extend(_as_tuple(_get(item, "risks", ())))
    if not _offline_boundary(data):
        risks.append(PaperBrokerReadOnlyConnectionDryRunPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(PaperBrokerReadOnlyConnectionDryRunPlanRisk.DATA_ACCESS_VIOLATION)
    if data.paper_broker_read_only_connection_dry_run_safety_gate_requested is True:
        risks.append(PaperBrokerReadOnlyConnectionDryRunPlanRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE)
    return _dedupe(risks)


def generate_read_only_connection_dry_run_plan_recommendations(
    data: PaperBrokerReadOnlyConnectionDryRunPlanInput | Mapping[str, Any] | None,
) -> tuple[PaperBrokerReadOnlyConnectionDryRunPlanRecommendation, ...]:
    risks = detect_read_only_connection_dry_run_plan_risks(data)
    if not risks:
        return (
            PaperBrokerReadOnlyConnectionDryRunPlanRecommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN_SUITE,
            PaperBrokerReadOnlyConnectionDryRunPlanRecommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE,
        )
    mapping = {
        PaperBrokerReadOnlyConnectionDryRunPlanRisk.CONNECTION_PREPARATION_REVIEW_NOT_APPROVED: PaperBrokerReadOnlyConnectionDryRunPlanRecommendation.APPROVE_CONNECTION_PREPARATION_REVIEW_FIRST,
        PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_SCOPE_UNCLEAR: PaperBrokerReadOnlyConnectionDryRunPlanRecommendation.DEFINE_DRY_RUN_SCOPE,
        PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_ENVIRONMENT_BOUNDARY_MISSING: PaperBrokerReadOnlyConnectionDryRunPlanRecommendation.DEFINE_DRY_RUN_ENVIRONMENT_BOUNDARIES,
        PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_PRECONDITION_MISSING: PaperBrokerReadOnlyConnectionDryRunPlanRecommendation.DEFINE_DRY_RUN_PRECONDITIONS,
        PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_CREDENTIAL_POLICY_UNSAFE: PaperBrokerReadOnlyConnectionDryRunPlanRecommendation.HARDEN_DRY_RUN_CREDENTIAL_POLICY,
        PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_SECRET_READ_POLICY_UNSAFE: PaperBrokerReadOnlyConnectionDryRunPlanRecommendation.HARDEN_DRY_RUN_NO_SECRET_READ_POLICY,
        PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_NETWORK_NOT_BLOCKED: PaperBrokerReadOnlyConnectionDryRunPlanRecommendation.BLOCK_DRY_RUN_NETWORK,
        PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED: PaperBrokerReadOnlyConnectionDryRunPlanRecommendation.BLOCK_DRY_RUN_HTTP_WEBSOCKET_SOCKET,
        PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_ACCOUNT_READ_ONLY_UNSAFE: PaperBrokerReadOnlyConnectionDryRunPlanRecommendation.HARDEN_DRY_RUN_ACCOUNT_READ_ONLY,
        PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_MARKET_DATA_READ_ONLY_UNSAFE: PaperBrokerReadOnlyConnectionDryRunPlanRecommendation.HARDEN_DRY_RUN_MARKET_DATA_READ_ONLY,
        PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_ORDER_BLOCKING_UNSAFE: PaperBrokerReadOnlyConnectionDryRunPlanRecommendation.HARDEN_DRY_RUN_ORDER_BLOCKING,
        PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_POSITION_MUTATION_BLOCK_UNSAFE: PaperBrokerReadOnlyConnectionDryRunPlanRecommendation.HARDEN_DRY_RUN_POSITION_MUTATION_BLOCK,
        PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_OBSERVABILITY_PLAN_MISSING: PaperBrokerReadOnlyConnectionDryRunPlanRecommendation.DEFINE_DRY_RUN_OBSERVABILITY,
        PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_JOURNAL_PLAN_MISSING: PaperBrokerReadOnlyConnectionDryRunPlanRecommendation.DEFINE_DRY_RUN_JOURNAL,
        PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_HUMAN_APPROVAL_MISSING: PaperBrokerReadOnlyConnectionDryRunPlanRecommendation.REQUIRE_DRY_RUN_HUMAN_APPROVAL,
        PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_STOP_CONDITIONS_MISSING: PaperBrokerReadOnlyConnectionDryRunPlanRecommendation.DEFINE_DRY_RUN_STOP_CONDITIONS,
        PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_SUCCESS_CRITERIA_MISSING: PaperBrokerReadOnlyConnectionDryRunPlanRecommendation.DEFINE_DRY_RUN_SUCCESS_FAILURE_CRITERIA,
        PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_FAILURE_CRITERIA_MISSING: PaperBrokerReadOnlyConnectionDryRunPlanRecommendation.DEFINE_DRY_RUN_SUCCESS_FAILURE_CRITERIA,
        PaperBrokerReadOnlyConnectionDryRunPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION: PaperBrokerReadOnlyConnectionDryRunPlanRecommendation.RESTORE_OFFLINE_BOUNDARIES,
        PaperBrokerReadOnlyConnectionDryRunPlanRisk.DATA_ACCESS_VIOLATION: PaperBrokerReadOnlyConnectionDryRunPlanRecommendation.REMOVE_DATA_ACCESS,
        PaperBrokerReadOnlyConnectionDryRunPlanRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE: PaperBrokerReadOnlyConnectionDryRunPlanRecommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE,
    }
    recommendations = [
        PaperBrokerReadOnlyConnectionDryRunPlanRecommendation.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE
    ]
    recommendations.extend(mapping[risk] for risk in risks if risk in mapping)
    return _dedupe(recommendations)


def _decision_for_risks(
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPlanRisk, ...],
) -> PaperBrokerReadOnlyConnectionDryRunPlanDecision:
    if not risks:
        return PaperBrokerReadOnlyConnectionDryRunPlanDecision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN
    if PaperBrokerReadOnlyConnectionDryRunPlanRisk.CONNECTION_PREPARATION_REVIEW_NOT_APPROVED in risks:
        return PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_CONNECTION_PREPARATION_REVIEW_FIXES
    if any(
        risk in risks
        for risk in (
            PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_ENVIRONMENT_BOUNDARY_MISSING,
            PaperBrokerReadOnlyConnectionDryRunPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION,
            PaperBrokerReadOnlyConnectionDryRunPlanRisk.DATA_ACCESS_VIOLATION,
        )
    ):
        return PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_BOUNDARY_FIXES
    if PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_SCOPE_UNCLEAR in risks:
        return PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_SCOPE_FIXES
    if PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_PRECONDITION_MISSING in risks:
        return PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_PRECONDITION_FIXES
    if PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_CREDENTIAL_POLICY_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_CREDENTIAL_POLICY_FIXES
    if PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_SECRET_READ_POLICY_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_NO_SECRET_READ_FIXES
    if any(
        risk in risks
        for risk in (
            PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_NETWORK_NOT_BLOCKED,
            PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED,
        )
    ):
        return PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_NETWORK_BLOCK_FIXES
    if PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_ACCOUNT_READ_ONLY_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_ACCOUNT_READ_ONLY_FIXES
    if PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_MARKET_DATA_READ_ONLY_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_MARKET_DATA_READ_ONLY_FIXES
    if PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_ORDER_BLOCKING_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_ORDER_BLOCKING_FIXES
    if PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_POSITION_MUTATION_BLOCK_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_POSITION_MUTATION_BLOCK_FIXES
    if PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_OBSERVABILITY_PLAN_MISSING in risks:
        return PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_OBSERVABILITY_FIXES
    if PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_JOURNAL_PLAN_MISSING in risks:
        return PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_JOURNAL_FIXES
    if PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_HUMAN_APPROVAL_MISSING in risks:
        return PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_HUMAN_APPROVAL_FIXES
    if PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_STOP_CONDITIONS_MISSING in risks:
        return PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_STOP_CONDITION_FIXES
    if any(
        risk in risks
        for risk in (
            PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_SUCCESS_CRITERIA_MISSING,
            PaperBrokerReadOnlyConnectionDryRunPlanRisk.DRY_RUN_FAILURE_CRITERIA_MISSING,
        )
    ):
        return PaperBrokerReadOnlyConnectionDryRunPlanDecision.REQUIRE_DRY_RUN_SUCCESS_FAILURE_CRITERIA_FIXES
    return PaperBrokerReadOnlyConnectionDryRunPlanDecision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN


def _state_for_result(
    data: PaperBrokerReadOnlyConnectionDryRunPlanInput,
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunPlanRisk, ...],
    score: PaperBrokerReadOnlyConnectionDryRunPlanScore,
) -> PaperBrokerReadOnlyConnectionDryRunPlanState:
    if data.paper_broker_read_only_connection_preparation_review is None:
        return PaperBrokerReadOnlyConnectionDryRunPlanState.DRY_RUN_PLAN_INPUT_INVALID
    if not risks and score.overall_score >= 85:
        return PaperBrokerReadOnlyConnectionDryRunPlanState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE
    if risks:
        return PaperBrokerReadOnlyConnectionDryRunPlanState.DRY_RUN_PLAN_BLOCKED
    if score.overall_score >= 70:
        return PaperBrokerReadOnlyConnectionDryRunPlanState.DRY_RUN_PLAN_COMPLETED_WITH_WARNINGS
    return PaperBrokerReadOnlyConnectionDryRunPlanState.NOT_READY


def evaluate_paper_broker_read_only_connection_dry_run_plan(
    data: PaperBrokerReadOnlyConnectionDryRunPlanInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlyConnectionDryRunPlanResult:
    data = _coerce_input(data)
    score = compute_read_only_connection_dry_run_plan_score(data)
    risks = detect_read_only_connection_dry_run_plan_risks(data)
    recommendations = generate_read_only_connection_dry_run_plan_recommendations(data)
    decision = _decision_for_risks(risks)
    state = _state_for_result(data, risks, score)
    return PaperBrokerReadOnlyConnectionDryRunPlanResult(
        state=state,
        decision=decision,
        dry_run_plan_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        recommendations=recommendations,
        dry_run_scope=define_dry_run_scope(data),
        environment_boundaries=define_dry_run_environment_boundaries(data),
        preconditions=define_dry_run_preconditions(data),
        credentials_reference_policy=define_dry_run_credentials_reference_policy(data),
        no_secret_read_policy=define_dry_run_no_secret_read_policy(data),
        network_block_policy=define_dry_run_network_block_policy(data),
        http_websocket_socket_block_policy=define_dry_run_http_websocket_socket_block_policy(data),
        account_read_only_policy=define_dry_run_account_read_only_policy(data),
        market_data_read_only_policy=define_dry_run_market_data_read_only_policy(data),
        order_blocking_policy=define_dry_run_order_blocking_policy(data),
        position_mutation_block_policy=define_dry_run_position_mutation_block_policy(data),
        observability_plan=define_dry_run_observability_plan(data),
        journal_plan=define_dry_run_journal_plan(data),
        human_approval_plan=define_dry_run_human_approval_plan(data),
        stop_conditions_plan=define_dry_run_stop_conditions_plan(data),
        success_criteria=define_dry_run_success_criteria(data),
        failure_criteria=define_dry_run_failure_criteria(data),
        offline_only=True,
        summary=(
            "Paper broker read-only connection dry-run plan is approved for the dry-run safety gate."
            if not risks
            else "Paper broker read-only connection dry-run plan is blocked until plan risks are fixed."
        ),
    )


def render_paper_broker_read_only_connection_dry_run_plan_markdown(
    result: PaperBrokerReadOnlyConnectionDryRunPlanResult | Mapping[str, Any],
) -> str:
    if isinstance(result, Mapping):
        result = PaperBrokerReadOnlyConnectionDryRunPlanResult(**dict(result))
    risks = ", ".join(risk.value for risk in result.risks) or "none"
    recommendations = ", ".join(recommendation.value for recommendation in result.recommendations) or "none"
    sections = (
        ("dry_run_scope", result.dry_run_scope),
        ("environment_boundaries", result.environment_boundaries),
        ("preconditions", result.preconditions),
        ("credentials_reference_policy", result.credentials_reference_policy),
        ("no_secret_read_policy", result.no_secret_read_policy),
        ("network_block_policy", result.network_block_policy),
        ("http_websocket_socket_block_policy", result.http_websocket_socket_block_policy),
        ("account_read_only_policy", result.account_read_only_policy),
        ("market_data_read_only_policy", result.market_data_read_only_policy),
        ("order_blocking_policy", result.order_blocking_policy),
        ("position_mutation_block_policy", result.position_mutation_block_policy),
        ("observability_plan", result.observability_plan),
        ("journal_plan", result.journal_plan),
        ("human_approval_plan", result.human_approval_plan),
        ("stop_conditions_plan", result.stop_conditions_plan),
        ("success_criteria", result.success_criteria),
        ("failure_criteria", result.failure_criteria),
    )
    lines = [
        "# Paper Broker Read-Only Connection Dry Run Plan",
        "",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Dry run plan score: {result.dry_run_plan_score}",
        f"- Offline only: {result.offline_only}",
        f"- Risks: {risks}",
        f"- Recommendations: {recommendations}",
        "",
        "## Enforced Plan Boundaries",
        "- Plan-only: no dry run execution and no connection test",
        "- No broker, Alpaca, API key, environment variable, or hardcoded secret read",
        "- No HTTP, websocket, socket, network transport, or external API",
        "- No order execution, position mutation, or active account access",
        "- No data/ access",
        "",
        "## Dry Run Plan Sections",
    ]
    for name, section in sections:
        lines.append(f"- {name}: score={section.score}, defined={section.defined}, risks={len(section.risks)}")
    if result.summary:
        lines.extend(("", f"Summary: {result.summary}"))
    return "\n".join(lines)
