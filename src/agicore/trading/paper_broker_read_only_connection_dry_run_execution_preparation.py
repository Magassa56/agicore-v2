"""Offline preparation for AGIcore Paper Broker read-only connection dry-run execution internals."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_broker_read_only_connection_dry_run_execution_preparation_models import (
    DryRunExecutionAccountReadOnlyContract,
    DryRunExecutionAuditContract,
    DryRunExecutionSequenceContract,
    DryRunExecutionPreconditionContract,
    DryRunExecutionCredentialsReferenceContract,
    DryRunExecutionRuntimeContract,
    DryRunExecutionHumanApprovalContract,
    DryRunExecutionJournalContract,
    DryRunExecutionMarketDataReadOnlyContract,
    DryRunExecutionNetworkBlockGuard,
    DryRunExecutionNoSecretReadGuard,
    DryRunExecutionObservabilityContract,
    DryRunExecutionOrderBlockingContract,
    DryRunExecutionPositionMutationBlockContract,
    DryRunExecutionStopConditionContract,
    DryRunExecutionSuccessFailureContract,
    PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision,
    PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput,
    PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation,
    PaperBrokerReadOnlyConnectionDryRunExecutionPreparationResult,
    PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk,
    PaperBrokerReadOnlyConnectionDryRunExecutionPreparationScore,
    PaperBrokerReadOnlyConnectionDryRunExecutionPreparationState,
)


def _coerce_input(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput:
    if data is None:
        return PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput()
    if isinstance(data, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput):
        return data
    allowed = {field.name for field in fields(PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput)}
    payload = {key: value for key, value in dict(data).items() if key in allowed}
    return PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput(**payload)


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


def _gate(data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput) -> Any:
    return data.paper_broker_read_only_connection_dry_run_execution_safety_gate


def _upstream_items(data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput) -> tuple[Any, ...]:
    return (
        data.paper_broker_read_only_connection_dry_run_execution_safety_gate,
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


def _upstream_risks(data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _secret_boundary(data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput) -> bool:
    return (
        data.no_api_key_read is True
        and data.no_env_var_read is True
        and data.no_hardcoded_secrets is True
        and data.api_key_read_requested is not True
        and data.env_var_read_requested is not True
        and data.hardcoded_secret_detected is not True
    )


def _offline_boundary(data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput) -> bool:
    return (
        data.offline_mode_enforced is True
        and data.sandbox_mode_enforced is True
        and data.preparation_only is True
        and data.broker_connection_disabled is True
        and data.no_real_broker is True
        and data.no_alpaca_real is True
        and _secret_boundary(data)
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


def _data_boundary(data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput) -> bool:
    return data.data_access_requested is not True and not _has_upstream_risk(data, "DATA_ACCESS", "DATA/")


def validate_dry_run_execution_safety_gate_approval(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput | Mapping[str, Any] | None,
) -> bool:
    data = _coerce_input(data)
    gate = _gate(data)
    if gate is None or data.dry_run_execution_safety_gate_approved is False:
        return False
    approved_state = _state_contains(
        gate,
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE",
    )
    approved = data.dry_run_execution_safety_gate_approved is True or approved_state
    return approved and not _as_tuple(_get(gate, "risks", ())) and _get(gate, "offline_only", True) is True


def prepare_dry_run_execution_runtime_contract(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput | Mapping[str, Any] | None,
) -> DryRunExecutionRuntimeContract:
    data = _coerce_input(data)
    passed = data.dry_run_execution_runtime_contract_prepared is True and data.preparation_only is True and data.dry_run_executed is not True
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_RUNTIME_CONTRACT_MISSING,)
    return DryRunExecutionRuntimeContract(
        score=_metric_score(data.runtime_contract_score, None, passed),
        defined=data.dry_run_execution_runtime_contract_prepared is True,
        preparation_only=data.preparation_only is True,
        read_only_only=True,
        dry_run_execution_disabled=data.dry_run_executed is not True and data.dry_run_requested is not True,
        allowed_actions=("build_dry_run_contracts", "prepare_schema_placeholders", "document_offline_guards"),
        prohibited_actions=("dry_run_execution", "broker_connection", "api_key_read", "env_var_read", "http_request", "websocket_request", "socket_open", "order_execution", "position_mutation", "active_account_access"),
        risks=risks,
        details=("offline_preparation_only", "future_preparation_review_only"),
    )


def prepare_dry_run_execution_sequence_contract(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput | Mapping[str, Any] | None,
) -> DryRunExecutionSequenceContract:
    data = _coerce_input(data)
    connection_blocked = data.broker_connection_disabled is True and data.broker_connection_requested is not True
    network_blocked = data.no_http_transport is True and data.no_websocket_transport is True and data.no_socket_transport is True and data.network_transport_requested is not True
    passed = data.dry_run_execution_sequence_contract_prepared is True and connection_blocked and network_blocked and data.dry_run_executed is not True
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_SEQUENCE_CONTRACT_MISSING,)
    return DryRunExecutionSequenceContract(
        score=_metric_score(data.sequence_contract_score, None, passed),
        defined=data.dry_run_execution_sequence_contract_prepared is True,
        dry_run_not_executed=data.dry_run_executed is not True,
        connection_not_executed=connection_blocked,
        sequence_steps_defined=data.dry_run_execution_sequence_contract_prepared is True,
        network_transport_blocked=network_blocked,
        risks=risks,
        details=("dry_run_not_executed", "connection_not_executed", "offline_sequence_only"),
    )


def prepare_dry_run_execution_precondition_contract(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput | Mapping[str, Any] | None,
) -> DryRunExecutionPreconditionContract:
    data = _coerce_input(data)
    passed = (
        data.dry_run_execution_precondition_contract_prepared is True
        and data.dry_run_execution_safety_gate_approved is True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_PRECONDITION_CONTRACT_MISSING,)
    return DryRunExecutionPreconditionContract(
        score=_metric_score(data.precondition_contract_score, None, passed),
        defined=data.dry_run_execution_precondition_contract_prepared is True,
        safety_gate_required=data.dry_run_execution_safety_gate_approved is True,
        human_approval_required=True,
        stop_conditions_required=True,
        fail_closed=True,
        risks=risks,
        details=("safety_gate_required", "human_approval_required", "stop_conditions_required"),
    )


def prepare_dry_run_execution_credentials_reference_contract(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput | Mapping[str, Any] | None,
) -> DryRunExecutionCredentialsReferenceContract:
    data = _coerce_input(data)
    reference_only = data.dry_run_execution_credentials_reference_only is True
    secret_ok = _secret_boundary(data)
    passed = data.dry_run_execution_credentials_reference_contract_prepared is True and reference_only and secret_ok
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_CREDENTIAL_REFERENCE_UNSAFE,)
    return DryRunExecutionCredentialsReferenceContract(
        score=_metric_score(data.credentials_reference_score, None, passed),
        defined=data.dry_run_execution_credentials_reference_contract_prepared is True,
        reference_only=reference_only,
        no_secret_values=secret_ok,
        no_api_key_read=data.no_api_key_read is True and data.api_key_read_requested is not True,
        no_env_var_read=data.no_env_var_read is True and data.env_var_read_requested is not True,
        secret_source="none_in_this_phase",
        risks=risks,
        details=("credential_reference_names_only", "no_secret_material_loaded"),
    )


def prepare_dry_run_execution_no_secret_read_guard(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput | Mapping[str, Any] | None,
) -> DryRunExecutionNoSecretReadGuard:
    data = _coerce_input(data)
    passed = data.dry_run_execution_no_secret_read_guard_prepared is True and data.dry_run_execution_secret_read_guard_enforced is True and _secret_boundary(data)
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_SECRET_READ_GUARD_MISSING,)
    return DryRunExecutionNoSecretReadGuard(
        score=_metric_score(data.no_secret_read_guard_score, None, passed),
        defined=data.dry_run_execution_no_secret_read_guard_prepared is True,
        guard_enforced=data.dry_run_execution_secret_read_guard_enforced is True,
        no_api_key_read=data.no_api_key_read is True and data.api_key_read_requested is not True,
        no_env_var_read=data.no_env_var_read is True and data.env_var_read_requested is not True,
        no_hardcoded_secret=data.no_hardcoded_secrets is True and data.hardcoded_secret_detected is not True,
        risks=risks,
        details=("fail_closed_on_secret_read", "no_real_env_or_key_read"),
    )


def prepare_dry_run_execution_network_block_guard(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput | Mapping[str, Any] | None,
) -> DryRunExecutionNetworkBlockGuard:
    data = _coerce_input(data)
    passed = (
        data.dry_run_execution_network_block_guard_prepared is True
        and data.dry_run_execution_network_blocked is True
        and data.dry_run_execution_external_api_blocked is True
        and data.network_transport_requested is not True
        and data.external_api_requested is not True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD_MISSING,)
    return DryRunExecutionNetworkBlockGuard(
        score=_metric_score(data.network_block_guard_score, None, passed),
        defined=data.dry_run_execution_network_block_guard_prepared is True,
        network_execution_blocked=data.dry_run_execution_network_blocked is True and data.network_transport_requested is not True,
        http_blocked=data.dry_run_execution_http_transport_blocked is True and data.no_http_transport is True,
        websocket_blocked=data.dry_run_execution_websocket_transport_blocked is True and data.no_websocket_transport is True,
        socket_blocked=data.dry_run_execution_socket_transport_blocked is True and data.no_socket_transport is True,
        external_api_blocked=data.dry_run_execution_external_api_blocked is True and data.external_api_requested is not True,
        risks=risks,
        details=("network_execution_guard", "external_api_blocked"),
    )


def prepare_dry_run_execution_http_websocket_socket_block_guard(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput | Mapping[str, Any] | None,
) -> DryRunExecutionNetworkBlockGuard:
    data = _coerce_input(data)
    passed = (
        data.dry_run_execution_http_websocket_socket_block_guard_prepared is True
        and data.dry_run_execution_http_transport_blocked is True
        and data.dry_run_execution_websocket_transport_blocked is True
        and data.dry_run_execution_socket_transport_blocked is True
        and data.network_transport_requested is not True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_MISSING,)
    return DryRunExecutionNetworkBlockGuard(
        name="dry_run_execution_http_websocket_socket_block_guard",
        score=_metric_score(data.http_websocket_socket_block_guard_score, None, passed),
        defined=data.dry_run_execution_http_websocket_socket_block_guard_prepared is True,
        network_execution_blocked=data.dry_run_execution_network_blocked is True and data.network_transport_requested is not True,
        http_blocked=data.dry_run_execution_http_transport_blocked is True and data.no_http_transport is True,
        websocket_blocked=data.dry_run_execution_websocket_transport_blocked is True and data.no_websocket_transport is True,
        socket_blocked=data.dry_run_execution_socket_transport_blocked is True and data.no_socket_transport is True,
        external_api_blocked=data.dry_run_execution_external_api_blocked is True,
        risks=risks,
        details=("http_blocked", "websocket_blocked", "socket_blocked"),
    )


def prepare_dry_run_execution_account_read_only_contract(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput | Mapping[str, Any] | None,
) -> DryRunExecutionAccountReadOnlyContract:
    data = _coerce_input(data)
    passed = (
        data.dry_run_execution_account_read_only_contract_prepared is True
        and data.dry_run_execution_account_active_access_blocked is True
        and data.dry_run_execution_account_mutations_blocked is True
        and data.account_access_requested is not True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_UNSAFE,)
    return DryRunExecutionAccountReadOnlyContract(
        score=_metric_score(data.account_read_only_score, None, passed),
        defined=data.dry_run_execution_account_read_only_contract_prepared is True,
        active_account_access_blocked=data.dry_run_execution_account_active_access_blocked is True and data.account_access_requested is not True,
        account_mutations_blocked=data.dry_run_execution_account_mutations_blocked is True,
        schema_only_account_review=True,
        risks=risks,
        details=("account_schema_only", "active_account_access_blocked"),
    )


def prepare_dry_run_execution_market_data_read_only_contract(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput | Mapping[str, Any] | None,
) -> DryRunExecutionMarketDataReadOnlyContract:
    data = _coerce_input(data)
    passed = (
        data.dry_run_execution_market_data_read_only_contract_prepared is True
        and data.dry_run_execution_market_data_live_subscription_blocked is True
        and data.dry_run_execution_market_data_network_request_blocked is True
        and data.no_external_api is True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_UNSAFE,)
    return DryRunExecutionMarketDataReadOnlyContract(
        score=_metric_score(data.market_data_read_only_score, None, passed),
        defined=data.dry_run_execution_market_data_read_only_contract_prepared is True,
        read_only_market_data_only=True,
        live_subscription_blocked=data.dry_run_execution_market_data_live_subscription_blocked is True,
        network_request_blocked=data.dry_run_execution_market_data_network_request_blocked is True,
        schema_or_synthetic_only=True,
        risks=risks,
        details=("market_data_schema_only", "live_subscription_blocked"),
    )


def prepare_dry_run_execution_order_blocking_contract(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput | Mapping[str, Any] | None,
) -> DryRunExecutionOrderBlockingContract:
    data = _coerce_input(data)
    passed = (
        data.dry_run_execution_order_blocking_contract_prepared is True
        and data.dry_run_execution_order_execution_blocked is True
        and data.dry_run_execution_cancel_replace_blocked is True
        and data.order_execution_requested is not True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_ORDER_BLOCKING_UNSAFE,)
    return DryRunExecutionOrderBlockingContract(
        score=_metric_score(data.order_blocking_score, None, passed),
        defined=data.dry_run_execution_order_blocking_contract_prepared is True,
        order_execution_blocked=data.dry_run_execution_order_execution_blocked is True and data.order_execution_requested is not True,
        real_order_blocked=data.no_real_order is True,
        cancel_replace_blocked=data.dry_run_execution_cancel_replace_blocked is True,
        risks=risks,
        details=("submit_cancel_replace_blocked", "no_real_order_path"),
    )


def prepare_dry_run_execution_position_mutation_block_contract(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput | Mapping[str, Any] | None,
) -> DryRunExecutionPositionMutationBlockContract:
    data = _coerce_input(data)
    passed = (
        data.dry_run_execution_position_mutation_block_contract_prepared is True
        and data.dry_run_execution_position_mutation_blocked is True
        and data.position_mutation_requested is not True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_UNSAFE,)
    return DryRunExecutionPositionMutationBlockContract(
        score=_metric_score(data.position_mutation_block_score, None, passed),
        defined=data.dry_run_execution_position_mutation_block_contract_prepared is True,
        position_mutation_blocked=data.dry_run_execution_position_mutation_blocked is True and data.position_mutation_requested is not True,
        position_request_absent=data.position_mutation_requested is not True,
        close_modify_blocked=data.dry_run_execution_position_mutation_blocked is True,
        risks=risks,
        details=("position_close_modify_blocked", "no_position_mutation_path"),
    )


def prepare_dry_run_execution_observability_contract(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput | Mapping[str, Any] | None,
) -> DryRunExecutionObservabilityContract:
    data = _coerce_input(data)
    passed = data.dry_run_execution_observability_contract_prepared is True
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_OBSERVABILITY_INCOMPLETE,)
    return DryRunExecutionObservabilityContract(
        score=_metric_score(data.observability_score, None, passed),
        defined=data.dry_run_execution_observability_contract_prepared is True,
        offline_events_defined=passed,
        connection_attempt_logging_disabled=True,
        sensitive_values_redacted=True,
        risks=risks,
        details=("offline_guard_events", "no_connection_attempt_logging"),
    )


def prepare_dry_run_execution_journal_contract(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput | Mapping[str, Any] | None,
) -> DryRunExecutionJournalContract:
    data = _coerce_input(data)
    passed = data.dry_run_execution_journal_contract_prepared is True
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_JOURNAL_INCOMPLETE,)
    return DryRunExecutionJournalContract(
        score=_metric_score(data.journal_score, None, passed),
        defined=data.dry_run_execution_journal_contract_prepared is True,
        offline_journal_required=passed,
        sensitive_values_redacted=True,
        no_secret_material_logged=True,
        risks=risks,
        details=("offline_journal_only", "no_secret_material_logged"),
    )


def prepare_dry_run_execution_human_approval_contract(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput | Mapping[str, Any] | None,
) -> DryRunExecutionHumanApprovalContract:
    data = _coerce_input(data)
    passed = data.dry_run_execution_human_approval_contract_prepared is True and data.dry_run_execution_human_approval_required is True
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_HUMAN_APPROVAL_MISSING,)
    return DryRunExecutionHumanApprovalContract(
        score=_metric_score(data.human_approval_score, None, passed),
        defined=data.dry_run_execution_human_approval_contract_prepared is True,
        human_approval_required=data.dry_run_execution_human_approval_required is True,
        approval_before_review=True,
        safety_gate_evidence_required=True,
        risks=risks,
        details=("human_approval_required_before_review",),
    )


def prepare_dry_run_execution_stop_conditions_contract(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput | Mapping[str, Any] | None,
) -> DryRunExecutionStopConditionContract:
    data = _coerce_input(data)
    passed = data.dry_run_execution_stop_conditions_contract_prepared is True
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_STOP_CONDITIONS_MISSING,)
    return DryRunExecutionStopConditionContract(
        score=_metric_score(data.stop_conditions_score, None, passed),
        defined=data.dry_run_execution_stop_conditions_contract_prepared is True,
        stop_on_secret_read=True,
        stop_on_network_request=True,
        stop_on_order_or_position_request=True,
        stop_on_account_access_request=True,
        risks=risks,
        details=("stop_on_boundary_violation", "fail_closed"),
    )


def prepare_dry_run_execution_success_failure_contract(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput | Mapping[str, Any] | None,
) -> DryRunExecutionSuccessFailureContract:
    data = _coerce_input(data)
    passed = data.dry_run_execution_success_failure_contract_prepared is True
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_SUCCESS_FAILURE_CONTRACT_MISSING,)
    return DryRunExecutionSuccessFailureContract(
        score=_metric_score(data.success_failure_score, None, passed),
        defined=data.dry_run_execution_success_failure_contract_prepared is True,
        success_requires_no_real_connection=True,
        success_requires_all_guards_verified=True,
        failure_on_secret_network_order_position_or_account=True,
        risks=risks,
        details=("success_no_real_connection", "failure_on_any_boundary_violation"),
    )


def prepare_dry_run_execution_audit_contract(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput | Mapping[str, Any] | None,
) -> DryRunExecutionAuditContract:
    data = _coerce_input(data)
    passed = data.dry_run_execution_audit_contract_prepared is True
    risks = () if passed else (PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_AUDIT_CONTRACT_MISSING,)
    return DryRunExecutionAuditContract(
        score=_metric_score(data.audit_score, None, passed),
        defined=data.dry_run_execution_audit_contract_prepared is True,
        audit_events_defined=passed,
        offline_evidence_required=True,
        preparation_review_trace_required=True,
        risks=risks,
        details=("offline_audit_evidence", "preparation_review_trace"),
    )


def _contract_objects(data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput) -> tuple[Any, ...]:
    return (
        prepare_dry_run_execution_runtime_contract(data),
        prepare_dry_run_execution_sequence_contract(data),
        prepare_dry_run_execution_precondition_contract(data),
        prepare_dry_run_execution_credentials_reference_contract(data),
        prepare_dry_run_execution_no_secret_read_guard(data),
        prepare_dry_run_execution_network_block_guard(data),
        prepare_dry_run_execution_http_websocket_socket_block_guard(data),
        prepare_dry_run_execution_account_read_only_contract(data),
        prepare_dry_run_execution_market_data_read_only_contract(data),
        prepare_dry_run_execution_order_blocking_contract(data),
        prepare_dry_run_execution_position_mutation_block_contract(data),
        prepare_dry_run_execution_observability_contract(data),
        prepare_dry_run_execution_journal_contract(data),
        prepare_dry_run_execution_human_approval_contract(data),
        prepare_dry_run_execution_stop_conditions_contract(data),
        prepare_dry_run_execution_success_failure_contract(data),
        prepare_dry_run_execution_audit_contract(data),
    )


def compute_read_only_connection_dry_run_execution_preparation_score(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlyConnectionDryRunExecutionPreparationScore:
    data = _coerce_input(data)
    gate_score = _metric_score(data.dry_run_execution_safety_gate_score, _get(_gate(data), "safety_gate_score"), validate_dry_run_execution_safety_gate_approval(data))
    execution = prepare_dry_run_execution_runtime_contract(data)
    adapter = prepare_dry_run_execution_sequence_contract(data)
    schema = prepare_dry_run_execution_precondition_contract(data)
    credentials = prepare_dry_run_execution_credentials_reference_contract(data)
    no_secret = prepare_dry_run_execution_no_secret_read_guard(data)
    network = prepare_dry_run_execution_network_block_guard(data)
    http_ws_socket = prepare_dry_run_execution_http_websocket_socket_block_guard(data)
    account = prepare_dry_run_execution_account_read_only_contract(data)
    market_data = prepare_dry_run_execution_market_data_read_only_contract(data)
    order = prepare_dry_run_execution_order_blocking_contract(data)
    position = prepare_dry_run_execution_position_mutation_block_contract(data)
    observability = prepare_dry_run_execution_observability_contract(data)
    journal = prepare_dry_run_execution_journal_contract(data)
    human = prepare_dry_run_execution_human_approval_contract(data)
    stop = prepare_dry_run_execution_stop_conditions_contract(data)
    success_failure = prepare_dry_run_execution_success_failure_contract(data)
    audit = prepare_dry_run_execution_audit_contract(data)
    values = (gate_score, execution.score, adapter.score, schema.score, credentials.score, no_secret.score, network.score, http_ws_socket.score, account.score, market_data.score, order.score, position.score, observability.score, journal.score, human.score, stop.score, success_failure.score, audit.score)
    return PaperBrokerReadOnlyConnectionDryRunExecutionPreparationScore(
        overall_score=_average(values),
        dry_run_execution_safety_gate_score=gate_score,
        runtime_contract_score=execution.score,
        sequence_contract_score=adapter.score,
        precondition_contract_score=schema.score,
        credentials_reference_score=credentials.score,
        no_secret_read_guard_score=no_secret.score,
        network_block_guard_score=network.score,
        http_websocket_socket_block_guard_score=http_ws_socket.score,
        account_read_only_score=account.score,
        market_data_read_only_score=market_data.score,
        order_blocking_score=order.score,
        position_mutation_block_score=position.score,
        observability_score=observability.score,
        journal_score=journal.score,
        human_approval_score=human.score,
        stop_conditions_score=stop.score,
        success_failure_score=success_failure.score,
        audit_score=audit.score,
    )


def detect_read_only_connection_dry_run_execution_preparation_risks(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput | Mapping[str, Any] | None,
) -> tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk, ...]:
    data = _coerce_input(data)
    risks: list[PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk] = []
    if not validate_dry_run_execution_safety_gate_approval(data):
        risks.append(PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_SAFETY_GATE_NOT_APPROVED)
    for contract in _contract_objects(data):
        risks.extend(_as_tuple(_get(contract, "risks", ())))
    if not _secret_boundary(data):
        risks.append(PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_SECRET_READ_GUARD_MISSING)
    if not _offline_boundary(data):
        risks.append(PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DATA_ACCESS_VIOLATION)
    if data.paper_broker_read_only_connection_dry_run_execution_preparation_review_requested is True:
        risks.append(PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW)
    return _dedupe(risks)


def generate_read_only_connection_dry_run_execution_preparation_recommendations(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput | Mapping[str, Any] | None,
) -> tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation, ...]:
    risks = detect_read_only_connection_dry_run_execution_preparation_risks(data)
    if not risks:
        return (
            PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_SUITE,
            PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW,
        )
    mapping = {
        PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_SAFETY_GATE_NOT_APPROVED: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation.APPROVE_DRY_RUN_EXECUTION_SAFETY_GATE_FIRST,
        PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_RUNTIME_CONTRACT_MISSING: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation.PREPARE_DRY_RUN_EXECUTION_RUNTIME_CONTRACT,
        PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_SEQUENCE_CONTRACT_MISSING: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation.PREPARE_DRY_RUN_EXECUTION_SEQUENCE_CONTRACT,
        PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_PRECONDITION_CONTRACT_MISSING: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation.PREPARE_DRY_RUN_EXECUTION_PRECONDITION_CONTRACT,
        PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_CREDENTIAL_REFERENCE_UNSAFE: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation.HARDEN_DRY_RUN_EXECUTION_CREDENTIAL_REFERENCE,
        PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_SECRET_READ_GUARD_MISSING: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation.INSTALL_DRY_RUN_EXECUTION_NO_SECRET_READ_GUARD,
        PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD_MISSING: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation.INSTALL_DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD,
        PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_MISSING: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation.INSTALL_DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD,
        PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_UNSAFE: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation.HARDEN_DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY,
        PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_UNSAFE: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation.HARDEN_DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY,
        PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_ORDER_BLOCKING_UNSAFE: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation.HARDEN_DRY_RUN_EXECUTION_ORDER_BLOCKING,
        PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_UNSAFE: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation.HARDEN_DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK,
        PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_OBSERVABILITY_INCOMPLETE: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation.COMPLETE_DRY_RUN_EXECUTION_OBSERVABILITY,
        PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_JOURNAL_INCOMPLETE: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation.COMPLETE_DRY_RUN_EXECUTION_JOURNAL,
        PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_HUMAN_APPROVAL_MISSING: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation.REQUIRE_DRY_RUN_EXECUTION_HUMAN_APPROVAL,
        PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_STOP_CONDITIONS_MISSING: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation.DEFINE_DRY_RUN_EXECUTION_STOP_CONDITIONS,
        PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_SUCCESS_FAILURE_CONTRACT_MISSING: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation.PREPARE_DRY_RUN_EXECUTION_SUCCESS_FAILURE_CONTRACT,
        PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_AUDIT_CONTRACT_MISSING: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation.PREPARE_DRY_RUN_EXECUTION_AUDIT_CONTRACT,
        PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.REAL_EXECUTION_BOUNDARY_VIOLATION: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation.RESTORE_OFFLINE_BOUNDARIES,
        PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DATA_ACCESS_VIOLATION: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation.REMOVE_DATA_ACCESS,
        PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW,
    }
    recommendations = [
        PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW
    ]
    recommendations.extend(mapping[risk] for risk in risks if risk in mapping)
    return _dedupe(recommendations)


def _decision_for_risks(
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk, ...],
) -> PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision:
    if not risks:
        return PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION
    if PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_SAFETY_GATE_NOT_APPROVED in risks:
        return PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_SAFETY_GATE_FIXES
    if any(risk in risks for risk in (PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_SEQUENCE_CONTRACT_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.REAL_EXECUTION_BOUNDARY_VIOLATION, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DATA_ACCESS_VIOLATION)):
        return PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_SEQUENCE_CONTRACT_FIXES
    if PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_RUNTIME_CONTRACT_MISSING in risks:
        return PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_RUNTIME_CONTRACT_FIXES
    if PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_PRECONDITION_CONTRACT_MISSING in risks:
        return PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_PRECONDITION_CONTRACT_FIXES
    if PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_CREDENTIAL_REFERENCE_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_CREDENTIAL_REFERENCE_FIXES
    if PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_SECRET_READ_GUARD_MISSING in risks:
        return PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_NO_SECRET_READ_GUARD_FIXES
    if any(risk in risks for risk in (PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_MISSING)):
        return PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD_FIXES
    if PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_FIXES
    if PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_FIXES
    if PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_ORDER_BLOCKING_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_ORDER_BLOCKING_FIXES
    if PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_FIXES
    if PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_OBSERVABILITY_INCOMPLETE in risks:
        return PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_OBSERVABILITY_FIXES
    if PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_JOURNAL_INCOMPLETE in risks:
        return PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_JOURNAL_FIXES
    if PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_HUMAN_APPROVAL_MISSING in risks:
        return PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_HUMAN_APPROVAL_FIXES
    if PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_STOP_CONDITIONS_MISSING in risks:
        return PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_STOP_CONDITION_FIXES
    if PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_SUCCESS_FAILURE_CONTRACT_MISSING in risks:
        return PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_SUCCESS_FAILURE_FIXES
    if PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_AUDIT_CONTRACT_MISSING in risks:
        return PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_AUDIT_FIXES
    return PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION


def _state_for_result(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput,
    risks: tuple[PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk, ...],
    score: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationScore,
) -> PaperBrokerReadOnlyConnectionDryRunExecutionPreparationState:
    if data.paper_broker_read_only_connection_dry_run_execution_safety_gate is None:
        return PaperBrokerReadOnlyConnectionDryRunExecutionPreparationState.DRY_RUN_EXECUTION_PREPARATION_INPUT_INVALID
    if not risks and score.overall_score >= 85:
        return PaperBrokerReadOnlyConnectionDryRunExecutionPreparationState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW
    if risks:
        return PaperBrokerReadOnlyConnectionDryRunExecutionPreparationState.DRY_RUN_EXECUTION_PREPARATION_BLOCKED
    if score.overall_score >= 70:
        return PaperBrokerReadOnlyConnectionDryRunExecutionPreparationState.DRY_RUN_EXECUTION_PREPARATION_COMPLETED_WITH_WARNINGS
    return PaperBrokerReadOnlyConnectionDryRunExecutionPreparationState.NOT_READY


def evaluate_paper_broker_read_only_connection_dry_run_execution_preparation(
    data: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlyConnectionDryRunExecutionPreparationResult:
    data = _coerce_input(data)
    score = compute_read_only_connection_dry_run_execution_preparation_score(data)
    risks = detect_read_only_connection_dry_run_execution_preparation_risks(data)
    recommendations = generate_read_only_connection_dry_run_execution_preparation_recommendations(data)
    decision = _decision_for_risks(risks)
    state = _state_for_result(data, risks, score)
    return PaperBrokerReadOnlyConnectionDryRunExecutionPreparationResult(
        state=state,
        decision=decision,
        preparation_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        recommendations=recommendations,
        dry_run_execution_runtime_contract=prepare_dry_run_execution_runtime_contract(data),
        dry_run_execution_sequence_contract=prepare_dry_run_execution_sequence_contract(data),
        dry_run_execution_precondition_contract=prepare_dry_run_execution_precondition_contract(data),
        dry_run_execution_credentials_reference_contract=prepare_dry_run_execution_credentials_reference_contract(data),
        dry_run_execution_no_secret_read_guard=prepare_dry_run_execution_no_secret_read_guard(data),
        dry_run_execution_network_block_guard=prepare_dry_run_execution_network_block_guard(data),
        dry_run_execution_http_websocket_socket_block_guard=prepare_dry_run_execution_http_websocket_socket_block_guard(data),
        dry_run_execution_account_read_only_contract=prepare_dry_run_execution_account_read_only_contract(data),
        dry_run_execution_market_data_read_only_contract=prepare_dry_run_execution_market_data_read_only_contract(data),
        dry_run_execution_order_blocking_contract=prepare_dry_run_execution_order_blocking_contract(data),
        dry_run_execution_position_mutation_block_contract=prepare_dry_run_execution_position_mutation_block_contract(data),
        dry_run_execution_observability_contract=prepare_dry_run_execution_observability_contract(data),
        dry_run_execution_journal_contract=prepare_dry_run_execution_journal_contract(data),
        dry_run_execution_human_approval_contract=prepare_dry_run_execution_human_approval_contract(data),
        dry_run_execution_stop_conditions_contract=prepare_dry_run_execution_stop_conditions_contract(data),
        dry_run_execution_success_failure_contract=prepare_dry_run_execution_success_failure_contract(data),
        dry_run_execution_audit_contract=prepare_dry_run_execution_audit_contract(data),
        offline_only=True,
        summary=(
            "Paper broker read-only connection dry-run preparation is approved for preparation review."
            if not risks
            else "Paper broker read-only connection dry-run preparation is blocked until contract risks are fixed."
        ),
    )


def render_paper_broker_read_only_connection_dry_run_execution_preparation_markdown(
    result: PaperBrokerReadOnlyConnectionDryRunExecutionPreparationResult | Mapping[str, Any],
) -> str:
    if isinstance(result, Mapping):
        result = PaperBrokerReadOnlyConnectionDryRunExecutionPreparationResult(**dict(result))
    risks = ", ".join(risk.value for risk in result.risks) or "none"
    recommendations = ", ".join(recommendation.value for recommendation in result.recommendations) or "none"
    sections = (
        ("dry_run_execution_runtime_contract", result.dry_run_execution_runtime_contract),
        ("dry_run_execution_sequence_contract", result.dry_run_execution_sequence_contract),
        ("dry_run_execution_precondition_contract", result.dry_run_execution_precondition_contract),
        ("dry_run_execution_credentials_reference_contract", result.dry_run_execution_credentials_reference_contract),
        ("dry_run_execution_no_secret_read_guard", result.dry_run_execution_no_secret_read_guard),
        ("dry_run_execution_network_block_guard", result.dry_run_execution_network_block_guard),
        ("dry_run_execution_http_websocket_socket_block_guard", result.dry_run_execution_http_websocket_socket_block_guard),
        ("dry_run_execution_account_read_only_contract", result.dry_run_execution_account_read_only_contract),
        ("dry_run_execution_market_data_read_only_contract", result.dry_run_execution_market_data_read_only_contract),
        ("dry_run_execution_order_blocking_contract", result.dry_run_execution_order_blocking_contract),
        ("dry_run_execution_position_mutation_block_contract", result.dry_run_execution_position_mutation_block_contract),
        ("dry_run_execution_observability_contract", result.dry_run_execution_observability_contract),
        ("dry_run_execution_journal_contract", result.dry_run_execution_journal_contract),
        ("dry_run_execution_human_approval_contract", result.dry_run_execution_human_approval_contract),
        ("dry_run_execution_stop_conditions_contract", result.dry_run_execution_stop_conditions_contract),
        ("dry_run_execution_success_failure_contract", result.dry_run_execution_success_failure_contract),
        ("dry_run_execution_audit_contract", result.dry_run_execution_audit_contract),
    )
    lines = [
        "# Paper Broker Read-Only Connection Dry Run Execution Preparation",
        "",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Preparation score: {result.preparation_score}",
        f"- Offline only: {result.offline_only}",
        f"- Risks: {risks}",
        f"- Recommendations: {recommendations}",
        "",
        "## Enforced Preparation Boundaries",
        "- Preparation only: no dry run execution and no connection test",
        "- No broker, Alpaca, API key, environment variable, or hardcoded secret read",
        "- No HTTP, websocket, socket, network transport, or external API",
        "- No order execution, position mutation, trading, or active account access",
        "- No data/ access",
        "",
        "## Prepared Contracts",
    ]
    for name, section in sections:
        lines.append(f"- {name}: score={section.score}, defined={section.defined}, risks={len(section.risks)}")
    if result.summary:
        lines.extend(("", f"Summary: {result.summary}"))
    return "\n".join(lines)
