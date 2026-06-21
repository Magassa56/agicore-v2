"""Offline preparation for AGIcore Paper Broker read-only connection internals."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_broker_read_only_connection_preparation_models import (
    AccountReadOnlyContract,
    BrokerAdapterBoundary,
    ConnectionConfigurationSchema,
    ConnectionHumanApprovalContract,
    ConnectionJournalContract,
    ConnectionObservabilityContract,
    ConnectionStopConditionContract,
    CredentialsReferenceContract,
    MarketDataReadOnlyContract,
    NetworkExecutionBlockGuard,
    NoSecretReadGuard,
    OrderBlockingContract,
    PaperBrokerReadOnlyConnectionPreparationDecision,
    PaperBrokerReadOnlyConnectionPreparationInput,
    PaperBrokerReadOnlyConnectionPreparationRecommendation,
    PaperBrokerReadOnlyConnectionPreparationResult,
    PaperBrokerReadOnlyConnectionPreparationRisk,
    PaperBrokerReadOnlyConnectionPreparationScore,
    PaperBrokerReadOnlyConnectionPreparationState,
    PositionMutationBlockContract,
    ReadOnlyConnectionContract,
)


def _coerce_input(
    data: PaperBrokerReadOnlyConnectionPreparationInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlyConnectionPreparationInput:
    if data is None:
        return PaperBrokerReadOnlyConnectionPreparationInput()
    if isinstance(data, PaperBrokerReadOnlyConnectionPreparationInput):
        return data
    allowed = {field.name for field in fields(PaperBrokerReadOnlyConnectionPreparationInput)}
    payload = {key: value for key, value in dict(data).items() if key in allowed}
    return PaperBrokerReadOnlyConnectionPreparationInput(**payload)


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


def _upstream_items(data: PaperBrokerReadOnlyConnectionPreparationInput) -> tuple[Any, ...]:
    return (
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


def _upstream_risks(data: PaperBrokerReadOnlyConnectionPreparationInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperBrokerReadOnlyConnectionPreparationInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _offline_boundary(data: PaperBrokerReadOnlyConnectionPreparationInput) -> bool:
    return (
        data.offline_mode_enforced is True
        and data.sandbox_mode_enforced is True
        and data.preparation_only is True
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
        and all(_get(item, "offline_only", True) is True for item in _upstream_items(data))
        and not _has_upstream_risk(
            data,
            "LIVE_EXECUTION",
            "BROKER_CONNECTIVITY",
            "BROKER_CONNECTION",
            "API_ACCESS",
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


def _data_boundary(data: PaperBrokerReadOnlyConnectionPreparationInput) -> bool:
    return (
        data.data_access_requested is not True
        and not _has_upstream_risk(data, "DATA_ACCESS", "DATA_ACCESS_VIOLATION", "REAL_DATA")
    )


def _secret_boundary(data: PaperBrokerReadOnlyConnectionPreparationInput) -> bool:
    return (
        data.no_api_key_read is True
        and data.no_env_var_read is True
        and data.no_hardcoded_secrets is True
        and data.api_key_read_requested is not True
        and data.env_var_read_requested is not True
        and data.hardcoded_secret_detected is not True
        and not _has_upstream_risk(data, "API_KEY", "SECRET", "CREDENTIAL")
    )


def validate_connection_safety_gate_approval(
    data: PaperBrokerReadOnlyConnectionPreparationInput | Mapping[str, Any] | None,
) -> bool:
    data = _coerce_input(data)
    gate = data.paper_broker_read_only_connection_safety_gate
    if gate is None or data.connection_safety_gate_approved is False:
        return False
    approved_state = _state_contains(
        gate,
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE",
    )
    approved = data.connection_safety_gate_approved is True or approved_state
    return (
        approved
        and not _as_tuple(_get(gate, "risks", ()))
        and _get(gate, "offline_only", True) is True
        and not _has_upstream_risk(data, "CONNECTION_SAFETY_BLOCKED", "REAL_EXECUTION", "DATA_ACCESS")
    )


def prepare_read_only_connection_contract(
    data: PaperBrokerReadOnlyConnectionPreparationInput | Mapping[str, Any] | None,
) -> ReadOnlyConnectionContract:
    data = _coerce_input(data)
    passed = (
        data.read_only_connection_contract_prepared is True
        and data.preparation_only is True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionPreparationRisk.READ_ONLY_CONNECTION_CONTRACT_MISSING,)
    score = _metric_score(data.connection_contract_score, None, passed)
    return ReadOnlyConnectionContract(
        score=score,
        defined=data.read_only_connection_contract_prepared is True,
        preparation_only=data.preparation_only is True,
        read_only_only=True,
        no_connection_execution=data.broker_connection_disabled is True and data.broker_connection_requested is not True,
        allowed_actions=("build_internal_contracts", "prepare_schema_placeholders", "document_offline_guards"),
        prohibited_actions=(
            "broker_connection",
            "api_key_read",
            "env_var_read",
            "http_request",
            "websocket_request",
            "socket_open",
            "order_execution",
            "position_mutation",
            "active_account_access",
        ),
        risks=risks,
        details=("offline_preparation_only", "future_review_only"),
    )


def prepare_broker_adapter_boundary(
    data: PaperBrokerReadOnlyConnectionPreparationInput | Mapping[str, Any] | None,
) -> BrokerAdapterBoundary:
    data = _coerce_input(data)
    adapter_blocked = data.broker_connection_disabled is True and data.broker_connection_requested is not True
    network_blocked = (
        data.no_http_transport is True
        and data.no_websocket_transport is True
        and data.no_socket_transport is True
        and data.network_transport_requested is not True
    )
    passed = (
        data.broker_adapter_boundary_prepared is True
        and data.no_real_broker is True
        and data.no_alpaca_real is True
        and adapter_blocked
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionPreparationRisk.BROKER_ADAPTER_BOUNDARY_UNSAFE,)
    score = _metric_score(data.broker_adapter_boundary_score, None, passed)
    return BrokerAdapterBoundary(
        score=score,
        defined=data.broker_adapter_boundary_prepared is True,
        no_real_broker=data.no_real_broker is True,
        no_alpaca_real=data.no_alpaca_real is True,
        adapter_instantiation_blocked=adapter_blocked,
        network_transport_blocked=network_blocked,
        paper_only_future_reference=True,
        risks=risks,
        details=("no_adapter_instantiation", "no_real_or_alpaca_broker"),
    )


def prepare_connection_configuration_schema(
    data: PaperBrokerReadOnlyConnectionPreparationInput | Mapping[str, Any] | None,
) -> ConnectionConfigurationSchema:
    data = _coerce_input(data)
    env_blocked = data.no_env_var_read is True and data.env_var_read_requested is not True
    api_key_absent = data.no_api_key_read is True and data.api_key_read_requested is not True
    reference_only = data.network_transport_requested is not True and data.external_api_requested is not True
    passed = data.connection_configuration_schema_prepared is True and env_blocked and api_key_absent and reference_only
    risks = () if passed else (PaperBrokerReadOnlyConnectionPreparationRisk.CONNECTION_CONFIGURATION_SCHEMA_UNSAFE,)
    score = _metric_score(data.configuration_schema_score, None, passed)
    return ConnectionConfigurationSchema(
        score=score,
        defined=data.connection_configuration_schema_prepared is True,
        schema_only=True,
        env_var_read_blocked=env_blocked,
        api_key_value_absent=api_key_absent,
        network_fields_reference_only=reference_only,
        required_fields=("broker_kind_reference", "paper_environment_label", "read_only_mode", "offline_guard_set"),
        prohibited_fields=("api_key_value", "secret_value", "env_var_read", "base_url_connection", "socket_handle"),
        risks=risks,
        details=("schema_without_secret_values", "no_env_lookup"),
    )


def prepare_credentials_reference_contract(
    data: PaperBrokerReadOnlyConnectionPreparationInput | Mapping[str, Any] | None,
) -> CredentialsReferenceContract:
    data = _coerce_input(data)
    reference_only = data.credentials_reference_only is True
    secret_ok = _secret_boundary(data)
    passed = data.credentials_reference_contract_prepared is True and reference_only and secret_ok
    risks = () if passed else (PaperBrokerReadOnlyConnectionPreparationRisk.CREDENTIAL_REFERENCE_CONTRACT_UNSAFE,)
    score = _metric_score(data.credential_reference_contract_score, None, passed)
    return CredentialsReferenceContract(
        score=score,
        defined=data.credentials_reference_contract_prepared is True,
        reference_only=reference_only,
        no_secret_values=secret_ok,
        no_api_key_read=data.no_api_key_read is True and data.api_key_read_requested is not True,
        no_env_var_read=data.no_env_var_read is True and data.env_var_read_requested is not True,
        secret_source="none_in_this_phase",
        risks=risks,
        details=("credential_reference_names_only", "no_secret_material_loaded"),
    )


def prepare_no_secret_read_guard(
    data: PaperBrokerReadOnlyConnectionPreparationInput | Mapping[str, Any] | None,
) -> NoSecretReadGuard:
    data = _coerce_input(data)
    api_key_blocked = data.no_api_key_read is True and data.api_key_read_requested is not True
    env_blocked = data.no_env_var_read is True and data.env_var_read_requested is not True
    hardcoded_blocked = data.no_hardcoded_secrets is True and data.hardcoded_secret_detected is not True
    passed = (
        data.no_secret_read_guard_prepared is True
        and data.secret_read_guard_enforced is True
        and api_key_blocked
        and env_blocked
        and hardcoded_blocked
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionPreparationRisk.SECRET_READ_GUARD_MISSING,)
    score = _metric_score(data.no_secret_read_guard_score, None, passed)
    return NoSecretReadGuard(
        score=score,
        defined=data.no_secret_read_guard_prepared is True,
        no_api_key_read=api_key_blocked,
        no_env_var_read=env_blocked,
        no_hardcoded_secret=hardcoded_blocked,
        guard_enforced=data.secret_read_guard_enforced is True,
        risks=risks,
        details=("block_api_key_read", "block_env_var_read", "block_hardcoded_secret"),
    )


def prepare_network_execution_block_guard(
    data: PaperBrokerReadOnlyConnectionPreparationInput | Mapping[str, Any] | None,
) -> NetworkExecutionBlockGuard:
    data = _coerce_input(data)
    network_blocked = data.network_execution_blocked is True and data.network_transport_requested is not True
    passed = (
        data.network_execution_block_guard_prepared is True
        and network_blocked
        and data.broker_connection_requested is not True
        and data.external_api_requested is not True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionPreparationRisk.NETWORK_EXECUTION_BLOCK_GUARD_MISSING,)
    score = _metric_score(data.network_block_guard_score, None, passed)
    return NetworkExecutionBlockGuard(
        score=score,
        defined=data.network_execution_block_guard_prepared is True,
        network_execution_blocked=network_blocked,
        http_blocked=data.no_http_transport is True and data.http_transport_blocked is True,
        websocket_blocked=data.no_websocket_transport is True and data.websocket_transport_blocked is True,
        socket_blocked=data.no_socket_transport is True and data.socket_transport_blocked is True,
        external_api_blocked=data.no_external_api is True and data.external_api_requested is not True,
        risks=risks,
        details=("no_network_execution", "no_broker_connection_attempt"),
    )


def prepare_http_websocket_socket_block_guard(
    data: PaperBrokerReadOnlyConnectionPreparationInput | Mapping[str, Any] | None,
) -> NetworkExecutionBlockGuard:
    data = _coerce_input(data)
    http = data.no_http_transport is True and data.http_transport_blocked is True
    websocket = data.no_websocket_transport is True and data.websocket_transport_blocked is True
    socket = data.no_socket_transport is True and data.socket_transport_blocked is True
    external = data.no_external_api is True and data.external_api_requested is not True
    passed = (
        data.http_websocket_socket_block_guard_prepared is True
        and http
        and websocket
        and socket
        and external
        and data.network_transport_requested is not True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionPreparationRisk.HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_MISSING,)
    score = _metric_score(data.http_websocket_socket_block_guard_score, None, passed)
    return NetworkExecutionBlockGuard(
        name="http_websocket_socket_block_guard",
        score=score,
        defined=data.http_websocket_socket_block_guard_prepared is True,
        network_execution_blocked=passed,
        http_blocked=http,
        websocket_blocked=websocket,
        socket_blocked=socket,
        external_api_blocked=external,
        risks=risks,
        details=("http_blocked", "websocket_blocked", "socket_blocked", "external_api_blocked"),
    )


def prepare_account_read_only_contract(
    data: PaperBrokerReadOnlyConnectionPreparationInput | Mapping[str, Any] | None,
) -> AccountReadOnlyContract:
    data = _coerce_input(data)
    active_blocked = data.account_active_access_blocked is True and data.account_access_requested is not True
    mutations_blocked = data.account_mutations_blocked is True and data.no_real_account_access is True
    passed = data.account_read_only_contract_prepared is True and active_blocked and mutations_blocked
    risks = () if passed else (PaperBrokerReadOnlyConnectionPreparationRisk.ACCOUNT_READ_ONLY_CONTRACT_UNSAFE,)
    score = _metric_score(data.account_read_only_contract_score, None, passed)
    return AccountReadOnlyContract(
        score=score,
        defined=data.account_read_only_contract_prepared is True,
        active_account_access_blocked=active_blocked,
        account_mutations_blocked=mutations_blocked,
        read_only_schema_only=True,
        risks=risks,
        details=("no_active_account_access", "no_account_mutation"),
    )


def prepare_market_data_read_only_contract(
    data: PaperBrokerReadOnlyConnectionPreparationInput | Mapping[str, Any] | None,
) -> MarketDataReadOnlyContract:
    data = _coerce_input(data)
    live_blocked = data.market_data_live_subscription_blocked is True
    network_blocked = data.market_data_network_request_blocked is True and data.network_transport_requested is not True
    passed = data.market_data_read_only_contract_prepared is True and live_blocked and network_blocked
    risks = () if passed else (PaperBrokerReadOnlyConnectionPreparationRisk.MARKET_DATA_READ_ONLY_CONTRACT_UNSAFE,)
    score = _metric_score(data.market_data_read_only_contract_score, None, passed)
    return MarketDataReadOnlyContract(
        score=score,
        defined=data.market_data_read_only_contract_prepared is True,
        read_only_market_data_only=True,
        live_subscription_blocked=live_blocked,
        network_request_blocked=network_blocked,
        synthetic_or_schema_only=True,
        risks=risks,
        details=("future_market_data_read_only", "no_live_subscription_or_network_request"),
    )


def prepare_order_blocking_contract(
    data: PaperBrokerReadOnlyConnectionPreparationInput | Mapping[str, Any] | None,
) -> OrderBlockingContract:
    data = _coerce_input(data)
    order_blocked = data.order_execution_blocked is True and data.order_execution_requested is not True
    real_order_blocked = data.no_real_order is True
    cancel_replace_blocked = data.cancel_replace_blocked is True
    passed = data.order_blocking_contract_prepared is True and order_blocked and real_order_blocked and cancel_replace_blocked
    risks = () if passed else (PaperBrokerReadOnlyConnectionPreparationRisk.ORDER_BLOCKING_CONTRACT_UNSAFE,)
    score = _metric_score(data.order_blocking_contract_score, None, passed)
    return OrderBlockingContract(
        score=score,
        defined=data.order_blocking_contract_prepared is True,
        order_execution_blocked=order_blocked,
        real_order_blocked=real_order_blocked,
        cancel_replace_blocked=cancel_replace_blocked,
        risks=risks,
        details=("submit_cancel_replace_order_blocked",),
    )


def prepare_position_mutation_block_contract(
    data: PaperBrokerReadOnlyConnectionPreparationInput | Mapping[str, Any] | None,
) -> PositionMutationBlockContract:
    data = _coerce_input(data)
    position_blocked = data.position_mutation_blocked is True and data.no_position_mutation is True
    request_absent = data.position_mutation_requested is not True
    passed = data.position_mutation_block_contract_prepared is True and position_blocked and request_absent
    risks = () if passed else (PaperBrokerReadOnlyConnectionPreparationRisk.POSITION_MUTATION_BLOCK_CONTRACT_UNSAFE,)
    score = _metric_score(data.position_mutation_block_score, None, passed)
    return PositionMutationBlockContract(
        score=score,
        defined=data.position_mutation_block_contract_prepared is True,
        position_mutation_blocked=position_blocked,
        position_request_absent=request_absent,
        close_modify_blocked=position_blocked,
        risks=risks,
        details=("position_create_update_close_blocked",),
    )


def prepare_connection_observability_contract(
    data: PaperBrokerReadOnlyConnectionPreparationInput | Mapping[str, Any] | None,
) -> ConnectionObservabilityContract:
    data = _coerce_input(data)
    passed = data.observability_contract_prepared is True and not _has_upstream_risk(data, "OBSERVABILITY_CONNECTION")
    risks = () if passed else (PaperBrokerReadOnlyConnectionPreparationRisk.OBSERVABILITY_CONTRACT_INCOMPLETE,)
    score = _metric_score(data.observability_contract_score, None, passed)
    return ConnectionObservabilityContract(
        score=score,
        defined=data.observability_contract_prepared is True,
        offline_events_defined=True,
        connection_attempt_logging_disabled=True,
        sensitive_values_redacted=True,
        risks=risks,
        details=("offline_audit_events_only", "no_connection_attempt_logging_of_secrets"),
    )


def prepare_connection_journal_contract(
    data: PaperBrokerReadOnlyConnectionPreparationInput | Mapping[str, Any] | None,
) -> ConnectionJournalContract:
    data = _coerce_input(data)
    passed = data.journal_contract_prepared is True and not _has_upstream_risk(data, "JOURNAL_CONNECTION")
    risks = () if passed else (PaperBrokerReadOnlyConnectionPreparationRisk.JOURNAL_CONTRACT_INCOMPLETE,)
    score = _metric_score(data.journal_contract_score, None, passed)
    return ConnectionJournalContract(
        score=score,
        defined=data.journal_contract_prepared is True,
        offline_journal_required=True,
        sensitive_values_redacted=True,
        no_secret_material_logged=True,
        risks=risks,
        details=("journal_preparation_decision_offline", "redact_sensitive_values"),
    )


def prepare_connection_human_approval_contract(
    data: PaperBrokerReadOnlyConnectionPreparationInput | Mapping[str, Any] | None,
) -> ConnectionHumanApprovalContract:
    data = _coerce_input(data)
    required = data.human_approval_required is True
    passed = data.human_approval_contract_prepared is True and required
    risks = () if passed else (PaperBrokerReadOnlyConnectionPreparationRisk.HUMAN_APPROVAL_CONTRACT_MISSING,)
    score = _metric_score(data.human_approval_contract_score, None, passed)
    return ConnectionHumanApprovalContract(
        score=score,
        defined=data.human_approval_contract_prepared is True,
        human_approval_required=required,
        approval_before_review=True,
        safety_gate_evidence_required=True,
        risks=risks,
        details=("explicit_human_approval_before_preparation_review",),
    )


def prepare_connection_stop_conditions_contract(
    data: PaperBrokerReadOnlyConnectionPreparationInput | Mapping[str, Any] | None,
) -> ConnectionStopConditionContract:
    data = _coerce_input(data)
    passed = data.stop_conditions_contract_prepared is True
    risks = () if passed else (PaperBrokerReadOnlyConnectionPreparationRisk.STOP_CONDITION_CONTRACT_MISSING,)
    score = _metric_score(data.stop_conditions_contract_score, None, passed)
    return ConnectionStopConditionContract(
        score=score,
        defined=data.stop_conditions_contract_prepared is True,
        stop_on_secret_read=True,
        stop_on_network_request=True,
        stop_on_order_or_position_request=True,
        stop_on_account_access_request=True,
        risks=risks,
        details=("stop_on_secret_network_order_position_or_account_request",),
    )


def _contract_objects(data: PaperBrokerReadOnlyConnectionPreparationInput) -> tuple[Any, ...]:
    return (
        prepare_read_only_connection_contract(data),
        prepare_broker_adapter_boundary(data),
        prepare_connection_configuration_schema(data),
        prepare_credentials_reference_contract(data),
        prepare_no_secret_read_guard(data),
        prepare_network_execution_block_guard(data),
        prepare_http_websocket_socket_block_guard(data),
        prepare_account_read_only_contract(data),
        prepare_market_data_read_only_contract(data),
        prepare_order_blocking_contract(data),
        prepare_position_mutation_block_contract(data),
        prepare_connection_observability_contract(data),
        prepare_connection_journal_contract(data),
        prepare_connection_human_approval_contract(data),
        prepare_connection_stop_conditions_contract(data),
    )


def compute_read_only_connection_preparation_score(
    data: PaperBrokerReadOnlyConnectionPreparationInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlyConnectionPreparationScore:
    data = _coerce_input(data)
    gate_ok = validate_connection_safety_gate_approval(data)
    gate_score = data.connection_safety_gate_score
    if gate_score is None:
        gate_score = _get(data.paper_broker_read_only_connection_safety_gate, "safety_gate_score")
    gate_score = _metric_score(gate_score, None, gate_ok)
    contract = prepare_read_only_connection_contract(data)
    boundary = prepare_broker_adapter_boundary(data)
    schema = prepare_connection_configuration_schema(data)
    credentials = prepare_credentials_reference_contract(data)
    secret = prepare_no_secret_read_guard(data)
    network = prepare_network_execution_block_guard(data)
    transports = prepare_http_websocket_socket_block_guard(data)
    account = prepare_account_read_only_contract(data)
    market = prepare_market_data_read_only_contract(data)
    orders = prepare_order_blocking_contract(data)
    positions = prepare_position_mutation_block_contract(data)
    observability = prepare_connection_observability_contract(data)
    journal = prepare_connection_journal_contract(data)
    human = prepare_connection_human_approval_contract(data)
    stops = prepare_connection_stop_conditions_contract(data)
    scores = (
        gate_score,
        contract.score,
        boundary.score,
        schema.score,
        credentials.score,
        secret.score,
        network.score,
        transports.score,
        account.score,
        market.score,
        orders.score,
        positions.score,
        observability.score,
        journal.score,
        human.score,
        stops.score,
    )
    return PaperBrokerReadOnlyConnectionPreparationScore(
        overall_score=_average(scores),
        connection_safety_gate_score=gate_score,
        connection_contract_score=contract.score,
        broker_adapter_boundary_score=boundary.score,
        configuration_schema_score=schema.score,
        credential_reference_contract_score=credentials.score,
        no_secret_read_guard_score=secret.score,
        network_block_guard_score=network.score,
        http_websocket_socket_block_guard_score=transports.score,
        account_read_only_contract_score=account.score,
        market_data_read_only_contract_score=market.score,
        order_blocking_contract_score=orders.score,
        position_mutation_block_score=positions.score,
        observability_contract_score=observability.score,
        journal_contract_score=journal.score,
        human_approval_contract_score=human.score,
        stop_conditions_contract_score=stops.score,
    )


def detect_read_only_connection_preparation_risks(
    data: PaperBrokerReadOnlyConnectionPreparationInput | Mapping[str, Any] | None,
) -> tuple[PaperBrokerReadOnlyConnectionPreparationRisk, ...]:
    data = _coerce_input(data)
    risks: list[PaperBrokerReadOnlyConnectionPreparationRisk] = []
    if not validate_connection_safety_gate_approval(data):
        risks.append(PaperBrokerReadOnlyConnectionPreparationRisk.CONNECTION_SAFETY_GATE_NOT_APPROVED)
    for contract in _contract_objects(data):
        risks.extend(_as_tuple(_get(contract, "risks", ())))
    if not _secret_boundary(data):
        risks.append(PaperBrokerReadOnlyConnectionPreparationRisk.SECRET_READ_GUARD_MISSING)
    if not _offline_boundary(data):
        risks.append(PaperBrokerReadOnlyConnectionPreparationRisk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(PaperBrokerReadOnlyConnectionPreparationRisk.DATA_ACCESS_VIOLATION)
    if data.paper_broker_read_only_connection_preparation_review_requested is True:
        risks.append(PaperBrokerReadOnlyConnectionPreparationRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW)
    return _dedupe(risks)


def generate_read_only_connection_preparation_recommendations(
    data: PaperBrokerReadOnlyConnectionPreparationInput | Mapping[str, Any] | None,
) -> tuple[PaperBrokerReadOnlyConnectionPreparationRecommendation, ...]:
    risks = detect_read_only_connection_preparation_risks(data)
    if not risks:
        return (
            PaperBrokerReadOnlyConnectionPreparationRecommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_SUITE,
            PaperBrokerReadOnlyConnectionPreparationRecommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW,
        )
    mapping = {
        PaperBrokerReadOnlyConnectionPreparationRisk.CONNECTION_SAFETY_GATE_NOT_APPROVED: PaperBrokerReadOnlyConnectionPreparationRecommendation.APPROVE_CONNECTION_SAFETY_GATE_FIRST,
        PaperBrokerReadOnlyConnectionPreparationRisk.READ_ONLY_CONNECTION_CONTRACT_MISSING: PaperBrokerReadOnlyConnectionPreparationRecommendation.PREPARE_READ_ONLY_CONNECTION_CONTRACT,
        PaperBrokerReadOnlyConnectionPreparationRisk.BROKER_ADAPTER_BOUNDARY_UNSAFE: PaperBrokerReadOnlyConnectionPreparationRecommendation.HARDEN_BROKER_ADAPTER_BOUNDARY,
        PaperBrokerReadOnlyConnectionPreparationRisk.CONNECTION_CONFIGURATION_SCHEMA_UNSAFE: PaperBrokerReadOnlyConnectionPreparationRecommendation.HARDEN_CONNECTION_CONFIGURATION_SCHEMA,
        PaperBrokerReadOnlyConnectionPreparationRisk.CREDENTIAL_REFERENCE_CONTRACT_UNSAFE: PaperBrokerReadOnlyConnectionPreparationRecommendation.HARDEN_CREDENTIAL_REFERENCE_CONTRACT,
        PaperBrokerReadOnlyConnectionPreparationRisk.SECRET_READ_GUARD_MISSING: PaperBrokerReadOnlyConnectionPreparationRecommendation.INSTALL_NO_SECRET_READ_GUARD,
        PaperBrokerReadOnlyConnectionPreparationRisk.NETWORK_EXECUTION_BLOCK_GUARD_MISSING: PaperBrokerReadOnlyConnectionPreparationRecommendation.INSTALL_NETWORK_EXECUTION_BLOCK_GUARD,
        PaperBrokerReadOnlyConnectionPreparationRisk.HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_MISSING: PaperBrokerReadOnlyConnectionPreparationRecommendation.INSTALL_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD,
        PaperBrokerReadOnlyConnectionPreparationRisk.ACCOUNT_READ_ONLY_CONTRACT_UNSAFE: PaperBrokerReadOnlyConnectionPreparationRecommendation.HARDEN_ACCOUNT_READ_ONLY_CONTRACT,
        PaperBrokerReadOnlyConnectionPreparationRisk.MARKET_DATA_READ_ONLY_CONTRACT_UNSAFE: PaperBrokerReadOnlyConnectionPreparationRecommendation.HARDEN_MARKET_DATA_READ_ONLY_CONTRACT,
        PaperBrokerReadOnlyConnectionPreparationRisk.ORDER_BLOCKING_CONTRACT_UNSAFE: PaperBrokerReadOnlyConnectionPreparationRecommendation.HARDEN_ORDER_BLOCKING_CONTRACT,
        PaperBrokerReadOnlyConnectionPreparationRisk.POSITION_MUTATION_BLOCK_CONTRACT_UNSAFE: PaperBrokerReadOnlyConnectionPreparationRecommendation.HARDEN_POSITION_MUTATION_BLOCK_CONTRACT,
        PaperBrokerReadOnlyConnectionPreparationRisk.OBSERVABILITY_CONTRACT_INCOMPLETE: PaperBrokerReadOnlyConnectionPreparationRecommendation.COMPLETE_CONNECTION_OBSERVABILITY_CONTRACT,
        PaperBrokerReadOnlyConnectionPreparationRisk.JOURNAL_CONTRACT_INCOMPLETE: PaperBrokerReadOnlyConnectionPreparationRecommendation.COMPLETE_CONNECTION_JOURNAL_CONTRACT,
        PaperBrokerReadOnlyConnectionPreparationRisk.HUMAN_APPROVAL_CONTRACT_MISSING: PaperBrokerReadOnlyConnectionPreparationRecommendation.REQUIRE_CONNECTION_HUMAN_APPROVAL,
        PaperBrokerReadOnlyConnectionPreparationRisk.STOP_CONDITION_CONTRACT_MISSING: PaperBrokerReadOnlyConnectionPreparationRecommendation.DEFINE_CONNECTION_STOP_CONDITIONS,
        PaperBrokerReadOnlyConnectionPreparationRisk.REAL_EXECUTION_BOUNDARY_VIOLATION: PaperBrokerReadOnlyConnectionPreparationRecommendation.RESTORE_OFFLINE_BOUNDARIES,
        PaperBrokerReadOnlyConnectionPreparationRisk.DATA_ACCESS_VIOLATION: PaperBrokerReadOnlyConnectionPreparationRecommendation.REMOVE_DATA_ACCESS,
        PaperBrokerReadOnlyConnectionPreparationRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW: PaperBrokerReadOnlyConnectionPreparationRecommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW,
    }
    recommendations = [
        PaperBrokerReadOnlyConnectionPreparationRecommendation.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION
    ]
    recommendations.extend(mapping[risk] for risk in risks if risk in mapping)
    return _dedupe(recommendations)


def _decision_for_risks(
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationRisk, ...],
) -> PaperBrokerReadOnlyConnectionPreparationDecision:
    if not risks:
        return PaperBrokerReadOnlyConnectionPreparationDecision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION
    if PaperBrokerReadOnlyConnectionPreparationRisk.CONNECTION_SAFETY_GATE_NOT_APPROVED in risks:
        return PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_CONNECTION_SAFETY_GATE_FIXES
    if PaperBrokerReadOnlyConnectionPreparationRisk.READ_ONLY_CONNECTION_CONTRACT_MISSING in risks:
        return PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_CONNECTION_CONTRACT_FIXES
    if PaperBrokerReadOnlyConnectionPreparationRisk.BROKER_ADAPTER_BOUNDARY_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_BROKER_ADAPTER_BOUNDARY_FIXES
    if PaperBrokerReadOnlyConnectionPreparationRisk.SECRET_READ_GUARD_MISSING in risks:
        return PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_NO_SECRET_READ_GUARD_FIXES
    if any(
        risk in risks
        for risk in (
            PaperBrokerReadOnlyConnectionPreparationRisk.NETWORK_EXECUTION_BLOCK_GUARD_MISSING,
            PaperBrokerReadOnlyConnectionPreparationRisk.HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_MISSING,
        )
    ):
        return PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_NETWORK_BLOCK_GUARD_FIXES
    if PaperBrokerReadOnlyConnectionPreparationRisk.CONNECTION_CONFIGURATION_SCHEMA_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_CONFIGURATION_SCHEMA_FIXES
    if PaperBrokerReadOnlyConnectionPreparationRisk.CREDENTIAL_REFERENCE_CONTRACT_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_CREDENTIAL_REFERENCE_CONTRACT_FIXES
    if PaperBrokerReadOnlyConnectionPreparationRisk.ACCOUNT_READ_ONLY_CONTRACT_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_ACCOUNT_READ_ONLY_CONTRACT_FIXES
    if PaperBrokerReadOnlyConnectionPreparationRisk.MARKET_DATA_READ_ONLY_CONTRACT_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_MARKET_DATA_READ_ONLY_CONTRACT_FIXES
    if PaperBrokerReadOnlyConnectionPreparationRisk.ORDER_BLOCKING_CONTRACT_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_ORDER_BLOCKING_CONTRACT_FIXES
    if PaperBrokerReadOnlyConnectionPreparationRisk.POSITION_MUTATION_BLOCK_CONTRACT_UNSAFE in risks:
        return PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_POSITION_MUTATION_BLOCK_FIXES
    if PaperBrokerReadOnlyConnectionPreparationRisk.OBSERVABILITY_CONTRACT_INCOMPLETE in risks:
        return PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_OBSERVABILITY_CONTRACT_FIXES
    if PaperBrokerReadOnlyConnectionPreparationRisk.JOURNAL_CONTRACT_INCOMPLETE in risks:
        return PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_JOURNAL_CONTRACT_FIXES
    if PaperBrokerReadOnlyConnectionPreparationRisk.HUMAN_APPROVAL_CONTRACT_MISSING in risks:
        return PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_HUMAN_APPROVAL_CONTRACT_FIXES
    if any(
        risk in risks
        for risk in (
            PaperBrokerReadOnlyConnectionPreparationRisk.BROKER_ADAPTER_BOUNDARY_UNSAFE,
            PaperBrokerReadOnlyConnectionPreparationRisk.REAL_EXECUTION_BOUNDARY_VIOLATION,
            PaperBrokerReadOnlyConnectionPreparationRisk.DATA_ACCESS_VIOLATION,
        )
    ):
        return PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_BROKER_ADAPTER_BOUNDARY_FIXES
    return PaperBrokerReadOnlyConnectionPreparationDecision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION


def _state_for_result(
    data: PaperBrokerReadOnlyConnectionPreparationInput,
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationRisk, ...],
    score: PaperBrokerReadOnlyConnectionPreparationScore,
) -> PaperBrokerReadOnlyConnectionPreparationState:
    if data.paper_broker_read_only_connection_safety_gate is None:
        return PaperBrokerReadOnlyConnectionPreparationState.CONNECTION_PREPARATION_INPUT_INVALID
    if not risks and score.overall_score >= 85:
        return PaperBrokerReadOnlyConnectionPreparationState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW
    if risks:
        return PaperBrokerReadOnlyConnectionPreparationState.CONNECTION_PREPARATION_BLOCKED
    if score.overall_score >= 70:
        return PaperBrokerReadOnlyConnectionPreparationState.CONNECTION_PREPARATION_COMPLETED_WITH_WARNINGS
    return PaperBrokerReadOnlyConnectionPreparationState.NOT_READY


def evaluate_paper_broker_read_only_connection_preparation(
    data: PaperBrokerReadOnlyConnectionPreparationInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlyConnectionPreparationResult:
    data = _coerce_input(data)
    score = compute_read_only_connection_preparation_score(data)
    risks = detect_read_only_connection_preparation_risks(data)
    recommendations = generate_read_only_connection_preparation_recommendations(data)
    decision = _decision_for_risks(risks)
    state = _state_for_result(data, risks, score)
    return PaperBrokerReadOnlyConnectionPreparationResult(
        state=state,
        decision=decision,
        preparation_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        recommendations=recommendations,
        read_only_connection_contract=prepare_read_only_connection_contract(data),
        broker_adapter_boundary=prepare_broker_adapter_boundary(data),
        connection_configuration_schema=prepare_connection_configuration_schema(data),
        credentials_reference_contract=prepare_credentials_reference_contract(data),
        no_secret_read_guard=prepare_no_secret_read_guard(data),
        network_execution_block_guard=prepare_network_execution_block_guard(data),
        http_websocket_socket_block_guard=prepare_http_websocket_socket_block_guard(data),
        account_read_only_contract=prepare_account_read_only_contract(data),
        market_data_read_only_contract=prepare_market_data_read_only_contract(data),
        order_blocking_contract=prepare_order_blocking_contract(data),
        position_mutation_block_contract=prepare_position_mutation_block_contract(data),
        observability_contract=prepare_connection_observability_contract(data),
        journal_contract=prepare_connection_journal_contract(data),
        human_approval_contract=prepare_connection_human_approval_contract(data),
        stop_conditions_contract=prepare_connection_stop_conditions_contract(data),
        offline_only=True,
        summary=(
            "Paper broker read-only connection preparation is approved for preparation review."
            if not risks
            else "Paper broker read-only connection preparation is blocked until contract risks are fixed."
        ),
    )


def render_paper_broker_read_only_connection_preparation_markdown(
    result: PaperBrokerReadOnlyConnectionPreparationResult | Mapping[str, Any],
) -> str:
    if isinstance(result, Mapping):
        result = PaperBrokerReadOnlyConnectionPreparationResult(**dict(result))
    risks = ", ".join(risk.value for risk in result.risks) or "none"
    recommendations = ", ".join(recommendation.value for recommendation in result.recommendations) or "none"
    contracts = (
        result.read_only_connection_contract,
        result.broker_adapter_boundary,
        result.connection_configuration_schema,
        result.credentials_reference_contract,
        result.no_secret_read_guard,
        result.network_execution_block_guard,
        result.http_websocket_socket_block_guard,
        result.account_read_only_contract,
        result.market_data_read_only_contract,
        result.order_blocking_contract,
        result.position_mutation_block_contract,
        result.observability_contract,
        result.journal_contract,
        result.human_approval_contract,
        result.stop_conditions_contract,
    )
    lines = [
        "# Paper Broker Read-Only Connection Preparation",
        "",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Preparation score: {result.preparation_score}",
        f"- Offline only: {result.offline_only}",
        f"- Risks: {risks}",
        f"- Recommendations: {recommendations}",
        "",
        "## Enforced Preparation Boundaries",
        "- No broker connection or adapter instantiation",
        "- No API key or environment variable read",
        "- No HTTP, websocket, socket or external API",
        "- No order execution or position mutation",
        "- No active account access and no data/ access",
        "",
        "## Prepared Contracts",
    ]
    for contract in contracts:
        lines.append(f"- {contract.name}: score={contract.score}, defined={contract.defined}, risks={len(contract.risks)}")
    if result.summary:
        lines.extend(("", f"Summary: {result.summary}"))
    return "\n".join(lines)
