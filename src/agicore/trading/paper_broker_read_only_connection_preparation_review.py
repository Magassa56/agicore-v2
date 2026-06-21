"""Offline review for AGIcore Paper Broker read-only connection preparation."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_broker_read_only_connection_preparation_review_models import (
    AccountReadOnlyContractReviewFinding,
    BrokerAdapterBoundaryReviewFinding,
    ConfigurationSchemaReviewFinding,
    ConnectionContractReviewFinding,
    CredentialsReferenceReviewFinding,
    HumanApprovalContractReviewFinding,
    JournalContractReviewFinding,
    MarketDataReadOnlyContractReviewFinding,
    NetworkExecutionBlockGuardReviewFinding,
    NoSecretReadGuardReviewFinding,
    ObservabilityContractReviewFinding,
    OrderBlockingContractReviewFinding,
    PaperBrokerReadOnlyConnectionPreparationReviewDecision,
    PaperBrokerReadOnlyConnectionPreparationReviewInput,
    PaperBrokerReadOnlyConnectionPreparationReviewRecommendation,
    PaperBrokerReadOnlyConnectionPreparationReviewResult,
    PaperBrokerReadOnlyConnectionPreparationReviewRisk,
    PaperBrokerReadOnlyConnectionPreparationReviewScore,
    PaperBrokerReadOnlyConnectionPreparationReviewState,
    PositionMutationBlockContractReviewFinding,
    StopConditionContractReviewFinding,
)


def _coerce_input(
    data: PaperBrokerReadOnlyConnectionPreparationReviewInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlyConnectionPreparationReviewInput:
    if data is None:
        return PaperBrokerReadOnlyConnectionPreparationReviewInput()
    if isinstance(data, PaperBrokerReadOnlyConnectionPreparationReviewInput):
        return data
    allowed = {field.name for field in fields(PaperBrokerReadOnlyConnectionPreparationReviewInput)}
    payload = {key: value for key, value in dict(data).items() if key in allowed}
    return PaperBrokerReadOnlyConnectionPreparationReviewInput(**payload)


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


def _preparation(data: PaperBrokerReadOnlyConnectionPreparationReviewInput) -> Any:
    return data.paper_broker_read_only_connection_preparation


def _contract(data: PaperBrokerReadOnlyConnectionPreparationReviewInput, name: str) -> Any:
    return _get(_preparation(data), name)


def _contract_ok(contract: Any) -> bool:
    return contract is not None and _get(contract, "defined", True) is True and not _as_tuple(_get(contract, "risks", ()))


def _upstream_items(data: PaperBrokerReadOnlyConnectionPreparationReviewInput) -> tuple[Any, ...]:
    return (
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


def _upstream_risks(data: PaperBrokerReadOnlyConnectionPreparationReviewInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperBrokerReadOnlyConnectionPreparationReviewInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _offline_boundary(data: PaperBrokerReadOnlyConnectionPreparationReviewInput) -> bool:
    return (
        data.offline_mode_enforced is True
        and data.sandbox_mode_enforced is True
        and data.review_only is True
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


def _data_boundary(data: PaperBrokerReadOnlyConnectionPreparationReviewInput) -> bool:
    return (
        data.data_access_requested is not True
        and not _has_upstream_risk(data, "DATA_ACCESS", "DATA_ACCESS_VIOLATION", "REAL_DATA")
    )


def validate_connection_preparation_approval(
    data: PaperBrokerReadOnlyConnectionPreparationReviewInput | Mapping[str, Any] | None,
) -> bool:
    data = _coerce_input(data)
    preparation = _preparation(data)
    if preparation is None or data.connection_preparation_approved is False:
        return False
    approved_state = _state_contains(
        preparation,
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION",
    )
    approved = data.connection_preparation_approved is True or approved_state
    return (
        approved
        and not _as_tuple(_get(preparation, "risks", ()))
        and _get(preparation, "offline_only", True) is True
        and not _has_upstream_risk(data, "CONNECTION_PREPARATION_BLOCKED", "REAL_EXECUTION", "DATA_ACCESS")
    )


def review_read_only_connection_contract(
    data: PaperBrokerReadOnlyConnectionPreparationReviewInput | Mapping[str, Any] | None,
) -> ConnectionContractReviewFinding:
    data = _coerce_input(data)
    contract = _contract(data, "read_only_connection_contract")
    no_connection = _get(contract, "no_connection_execution") is True and data.broker_connection_disabled is True
    passed = (
        data.connection_contract_review_verified is not False
        and _contract_ok(contract)
        and _get(contract, "read_only_only") is True
        and no_connection
        and _get(contract, "preparation_only") is True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionPreparationReviewRisk.READ_ONLY_CONNECTION_CONTRACT_REVIEW_FAILED,)
    score = _metric_score(data.connection_contract_score, _get(contract, "score"), passed)
    return ConnectionContractReviewFinding(
        score, passed, contract is not None, _get(contract, "read_only_only") is True, no_connection, risks, ("read_only_no_connection",)
    )


def review_broker_adapter_boundary(
    data: PaperBrokerReadOnlyConnectionPreparationReviewInput | Mapping[str, Any] | None,
) -> BrokerAdapterBoundaryReviewFinding:
    data = _coerce_input(data)
    boundary = _contract(data, "broker_adapter_boundary")
    no_real = _get(boundary, "no_real_broker") is True and data.no_real_broker is True
    no_alpaca = _get(boundary, "no_alpaca_real") is True and data.no_alpaca_real is True
    adapter_blocked = _get(boundary, "adapter_instantiation_blocked") is True and data.broker_connection_requested is not True
    network_blocked = _get(boundary, "network_transport_blocked") is True and data.network_transport_requested is not True
    passed = (
        data.broker_adapter_boundary_review_verified is not False
        and _contract_ok(boundary)
        and no_real
        and no_alpaca
        and adapter_blocked
        and network_blocked
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionPreparationReviewRisk.BROKER_ADAPTER_BOUNDARY_REVIEW_FAILED,)
    score = _metric_score(data.broker_adapter_boundary_score, _get(boundary, "score"), passed)
    return BrokerAdapterBoundaryReviewFinding(
        score, passed, boundary is not None, no_real, no_alpaca, adapter_blocked, network_blocked, risks, ("broker_adapter_boundary",)
    )


def review_connection_configuration_schema(
    data: PaperBrokerReadOnlyConnectionPreparationReviewInput | Mapping[str, Any] | None,
) -> ConfigurationSchemaReviewFinding:
    data = _coerce_input(data)
    schema = _contract(data, "connection_configuration_schema")
    schema_only = _get(schema, "schema_only") is True
    env_blocked = _get(schema, "env_var_read_blocked") is True and data.env_var_read_requested is not True
    api_absent = _get(schema, "api_key_value_absent") is True and data.api_key_read_requested is not True
    reference_only = _get(schema, "network_fields_reference_only") is True and data.network_transport_requested is not True
    passed = (
        data.configuration_schema_review_verified is not False
        and _contract_ok(schema)
        and schema_only
        and env_blocked
        and api_absent
        and reference_only
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionPreparationReviewRisk.CONNECTION_CONFIGURATION_SCHEMA_REVIEW_FAILED,)
    score = _metric_score(data.configuration_schema_score, _get(schema, "score"), passed)
    return ConfigurationSchemaReviewFinding(
        score, passed, schema is not None, schema_only, env_blocked, api_absent, reference_only, risks, ("schema_no_env_or_secret",)
    )


def review_credentials_reference_contract(
    data: PaperBrokerReadOnlyConnectionPreparationReviewInput | Mapping[str, Any] | None,
) -> CredentialsReferenceReviewFinding:
    data = _coerce_input(data)
    contract = _contract(data, "credentials_reference_contract")
    reference_only = _get(contract, "reference_only") is True
    no_secret = _get(contract, "no_secret_values") is True and data.hardcoded_secret_detected is not True
    no_api = _get(contract, "no_api_key_read") is True and data.api_key_read_requested is not True
    no_env = _get(contract, "no_env_var_read") is True and data.env_var_read_requested is not True
    passed = (
        data.credential_reference_review_verified is not False
        and _contract_ok(contract)
        and reference_only
        and no_secret
        and no_api
        and no_env
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionPreparationReviewRisk.CREDENTIAL_REFERENCE_CONTRACT_REVIEW_FAILED,)
    score = _metric_score(data.credential_reference_score, _get(contract, "score"), passed)
    return CredentialsReferenceReviewFinding(
        score, passed, contract is not None, reference_only, no_secret, no_api, no_env, risks, ("credential_reference_only",)
    )


def review_no_secret_read_guard(
    data: PaperBrokerReadOnlyConnectionPreparationReviewInput | Mapping[str, Any] | None,
) -> NoSecretReadGuardReviewFinding:
    data = _coerce_input(data)
    guard = _contract(data, "no_secret_read_guard")
    no_api = _get(guard, "no_api_key_read") is True and data.api_key_read_requested is not True
    no_env = _get(guard, "no_env_var_read") is True and data.env_var_read_requested is not True
    no_hardcoded = _get(guard, "no_hardcoded_secret") is True and data.hardcoded_secret_detected is not True
    enforced = _get(guard, "guard_enforced") is True
    passed = data.no_secret_read_guard_review_verified is not False and _contract_ok(guard) and enforced and no_api and no_env and no_hardcoded
    risks = () if passed else (PaperBrokerReadOnlyConnectionPreparationReviewRisk.SECRET_READ_GUARD_REVIEW_FAILED,)
    score = _metric_score(data.no_secret_read_guard_score, _get(guard, "score"), passed)
    return NoSecretReadGuardReviewFinding(score, passed, guard is not None, enforced, no_api, no_env, no_hardcoded, risks, ("secret_read_guard",))


def review_network_execution_block_guard(
    data: PaperBrokerReadOnlyConnectionPreparationReviewInput | Mapping[str, Any] | None,
) -> NetworkExecutionBlockGuardReviewFinding:
    data = _coerce_input(data)
    guard = _contract(data, "network_execution_block_guard")
    network = _get(guard, "network_execution_blocked") is True and data.network_transport_requested is not True
    external = _get(guard, "external_api_blocked") is True and data.external_api_requested is not True
    passed = (
        data.network_block_guard_review_verified is not False
        and _contract_ok(guard)
        and network
        and external
        and data.broker_connection_requested is not True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionPreparationReviewRisk.NETWORK_EXECUTION_BLOCK_GUARD_REVIEW_FAILED,)
    score = _metric_score(data.network_block_guard_score, _get(guard, "score"), passed)
    return NetworkExecutionBlockGuardReviewFinding(
        score,
        passed,
        guard is not None,
        network,
        _get(guard, "http_blocked") is True,
        _get(guard, "websocket_blocked") is True,
        _get(guard, "socket_blocked") is True,
        external,
        risks,
        ("network_block_guard",),
    )


def review_http_websocket_socket_block_guard(
    data: PaperBrokerReadOnlyConnectionPreparationReviewInput | Mapping[str, Any] | None,
) -> NetworkExecutionBlockGuardReviewFinding:
    data = _coerce_input(data)
    guard = _contract(data, "http_websocket_socket_block_guard")
    http = _get(guard, "http_blocked") is True and data.no_http_transport is True
    websocket = _get(guard, "websocket_blocked") is True and data.no_websocket_transport is True
    socket = _get(guard, "socket_blocked") is True and data.no_socket_transport is True
    external = _get(guard, "external_api_blocked") is True and data.no_external_api is True
    passed = (
        data.http_websocket_socket_block_guard_review_verified is not False
        and _contract_ok(guard)
        and http
        and websocket
        and socket
        and external
        and data.network_transport_requested is not True
    )
    risks = () if passed else (PaperBrokerReadOnlyConnectionPreparationReviewRisk.HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW_FAILED,)
    score = _metric_score(data.http_websocket_socket_block_guard_score, _get(guard, "score"), passed)
    return NetworkExecutionBlockGuardReviewFinding(score, passed, guard is not None, passed, http, websocket, socket, external, risks, ("transport_guards",))


def review_account_read_only_contract(
    data: PaperBrokerReadOnlyConnectionPreparationReviewInput | Mapping[str, Any] | None,
) -> AccountReadOnlyContractReviewFinding:
    data = _coerce_input(data)
    contract = _contract(data, "account_read_only_contract")
    active_blocked = _get(contract, "active_account_access_blocked") is True and data.account_access_requested is not True
    mutations_blocked = _get(contract, "account_mutations_blocked") is True and data.no_real_account_access is True
    schema_only = _get(contract, "read_only_schema_only") is True
    passed = data.account_read_only_contract_review_verified is not False and _contract_ok(contract) and active_blocked and mutations_blocked and schema_only
    risks = () if passed else (PaperBrokerReadOnlyConnectionPreparationReviewRisk.ACCOUNT_READ_ONLY_CONTRACT_REVIEW_FAILED,)
    score = _metric_score(data.account_read_only_score, _get(contract, "score"), passed)
    return AccountReadOnlyContractReviewFinding(score, passed, contract is not None, active_blocked, mutations_blocked, schema_only, risks, ("account_read_only",))


def review_market_data_read_only_contract(
    data: PaperBrokerReadOnlyConnectionPreparationReviewInput | Mapping[str, Any] | None,
) -> MarketDataReadOnlyContractReviewFinding:
    data = _coerce_input(data)
    contract = _contract(data, "market_data_read_only_contract")
    read_only = _get(contract, "read_only_market_data_only") is True
    live_blocked = _get(contract, "live_subscription_blocked") is True
    network_blocked = _get(contract, "network_request_blocked") is True and data.network_transport_requested is not True
    synthetic = _get(contract, "synthetic_or_schema_only") is True
    passed = data.market_data_read_only_contract_review_verified is not False and _contract_ok(contract) and read_only and live_blocked and network_blocked and synthetic
    risks = () if passed else (PaperBrokerReadOnlyConnectionPreparationReviewRisk.MARKET_DATA_READ_ONLY_CONTRACT_REVIEW_FAILED,)
    score = _metric_score(data.market_data_read_only_score, _get(contract, "score"), passed)
    return MarketDataReadOnlyContractReviewFinding(score, passed, contract is not None, read_only, live_blocked, network_blocked, synthetic, risks, ("market_data_read_only",))


def review_order_blocking_contract(
    data: PaperBrokerReadOnlyConnectionPreparationReviewInput | Mapping[str, Any] | None,
) -> OrderBlockingContractReviewFinding:
    data = _coerce_input(data)
    contract = _contract(data, "order_blocking_contract")
    order_blocked = _get(contract, "order_execution_blocked") is True and data.order_execution_requested is not True
    real_order_blocked = _get(contract, "real_order_blocked") is True and data.no_real_order is True
    cancel_replace = _get(contract, "cancel_replace_blocked") is True
    passed = data.order_blocking_contract_review_verified is not False and _contract_ok(contract) and order_blocked and real_order_blocked and cancel_replace
    risks = () if passed else (PaperBrokerReadOnlyConnectionPreparationReviewRisk.ORDER_BLOCKING_CONTRACT_REVIEW_FAILED,)
    score = _metric_score(data.order_blocking_score, _get(contract, "score"), passed)
    return OrderBlockingContractReviewFinding(score, passed, contract is not None, order_blocked, real_order_blocked, cancel_replace, risks, ("orders_blocked",))


def review_position_mutation_block_contract(
    data: PaperBrokerReadOnlyConnectionPreparationReviewInput | Mapping[str, Any] | None,
) -> PositionMutationBlockContractReviewFinding:
    data = _coerce_input(data)
    contract = _contract(data, "position_mutation_block_contract")
    position_blocked = _get(contract, "position_mutation_blocked") is True and data.no_position_mutation is True
    request_absent = _get(contract, "position_request_absent") is True and data.position_mutation_requested is not True
    close_modify = _get(contract, "close_modify_blocked") is True
    passed = data.position_mutation_block_review_verified is not False and _contract_ok(contract) and position_blocked and request_absent and close_modify
    risks = () if passed else (PaperBrokerReadOnlyConnectionPreparationReviewRisk.POSITION_MUTATION_BLOCK_CONTRACT_REVIEW_FAILED,)
    score = _metric_score(data.position_mutation_block_score, _get(contract, "score"), passed)
    return PositionMutationBlockContractReviewFinding(score, passed, contract is not None, position_blocked, request_absent, close_modify, risks, ("positions_blocked",))


def review_connection_observability_contract(
    data: PaperBrokerReadOnlyConnectionPreparationReviewInput | Mapping[str, Any] | None,
) -> ObservabilityContractReviewFinding:
    data = _coerce_input(data)
    contract = _contract(data, "observability_contract")
    offline_events = _get(contract, "offline_events_defined") is True
    no_connection_log = _get(contract, "connection_attempt_logging_disabled") is True
    redacted = _get(contract, "sensitive_values_redacted") is True
    passed = data.observability_contract_review_verified is not False and _contract_ok(contract) and offline_events and no_connection_log and redacted
    risks = () if passed else (PaperBrokerReadOnlyConnectionPreparationReviewRisk.OBSERVABILITY_CONTRACT_REVIEW_FAILED,)
    score = _metric_score(data.observability_score, _get(contract, "score"), passed)
    return ObservabilityContractReviewFinding(score, passed, contract is not None, offline_events, no_connection_log, redacted, risks, ("offline_observability",))


def review_connection_journal_contract(
    data: PaperBrokerReadOnlyConnectionPreparationReviewInput | Mapping[str, Any] | None,
) -> JournalContractReviewFinding:
    data = _coerce_input(data)
    contract = _contract(data, "journal_contract")
    offline_journal = _get(contract, "offline_journal_required") is True
    redacted = _get(contract, "sensitive_values_redacted") is True
    no_secret_log = _get(contract, "no_secret_material_logged") is True
    passed = data.journal_contract_review_verified is not False and _contract_ok(contract) and offline_journal and redacted and no_secret_log
    risks = () if passed else (PaperBrokerReadOnlyConnectionPreparationReviewRisk.JOURNAL_CONTRACT_REVIEW_FAILED,)
    score = _metric_score(data.journal_score, _get(contract, "score"), passed)
    return JournalContractReviewFinding(score, passed, contract is not None, offline_journal, redacted, no_secret_log, risks, ("offline_journal",))


def review_connection_human_approval_contract(
    data: PaperBrokerReadOnlyConnectionPreparationReviewInput | Mapping[str, Any] | None,
) -> HumanApprovalContractReviewFinding:
    data = _coerce_input(data)
    contract = _contract(data, "human_approval_contract")
    required = _get(contract, "human_approval_required") is True
    before_review = _get(contract, "approval_before_review") is True
    evidence = _get(contract, "safety_gate_evidence_required") is True
    passed = data.human_approval_contract_review_verified is not False and _contract_ok(contract) and required and before_review and evidence
    risks = () if passed else (PaperBrokerReadOnlyConnectionPreparationReviewRisk.HUMAN_APPROVAL_CONTRACT_REVIEW_FAILED,)
    score = _metric_score(data.human_approval_score, _get(contract, "score"), passed)
    return HumanApprovalContractReviewFinding(score, passed, contract is not None, required, before_review, evidence, risks, ("human_approval_required",))


def review_connection_stop_conditions_contract(
    data: PaperBrokerReadOnlyConnectionPreparationReviewInput | Mapping[str, Any] | None,
) -> StopConditionContractReviewFinding:
    data = _coerce_input(data)
    contract = _contract(data, "stop_conditions_contract")
    stop_secret = _get(contract, "stop_on_secret_read") is True
    stop_network = _get(contract, "stop_on_network_request") is True
    stop_order_position = _get(contract, "stop_on_order_or_position_request") is True
    stop_account = _get(contract, "stop_on_account_access_request") is True
    passed = data.stop_conditions_contract_review_verified is not False and _contract_ok(contract) and stop_secret and stop_network and stop_order_position and stop_account
    risks = () if passed else (PaperBrokerReadOnlyConnectionPreparationReviewRisk.STOP_CONDITION_CONTRACT_REVIEW_FAILED,)
    score = _metric_score(data.stop_conditions_score, _get(contract, "score"), passed)
    return StopConditionContractReviewFinding(score, passed, contract is not None, stop_secret, stop_network, stop_order_position, stop_account, risks, ("stop_conditions",))


def _review_objects(data: PaperBrokerReadOnlyConnectionPreparationReviewInput) -> tuple[Any, ...]:
    return (
        review_read_only_connection_contract(data),
        review_broker_adapter_boundary(data),
        review_connection_configuration_schema(data),
        review_credentials_reference_contract(data),
        review_no_secret_read_guard(data),
        review_network_execution_block_guard(data),
        review_http_websocket_socket_block_guard(data),
        review_account_read_only_contract(data),
        review_market_data_read_only_contract(data),
        review_order_blocking_contract(data),
        review_position_mutation_block_contract(data),
        review_connection_observability_contract(data),
        review_connection_journal_contract(data),
        review_connection_human_approval_contract(data),
        review_connection_stop_conditions_contract(data),
    )


def compute_read_only_connection_preparation_review_score(
    data: PaperBrokerReadOnlyConnectionPreparationReviewInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlyConnectionPreparationReviewScore:
    data = _coerce_input(data)
    prep_ok = validate_connection_preparation_approval(data)
    prep_score = data.connection_preparation_score
    if prep_score is None:
        prep_score = _get(_preparation(data), "preparation_score")
    prep_score = _metric_score(prep_score, None, prep_ok)
    contract = review_read_only_connection_contract(data)
    boundary = review_broker_adapter_boundary(data)
    schema = review_connection_configuration_schema(data)
    credential = review_credentials_reference_contract(data)
    secret = review_no_secret_read_guard(data)
    network = review_network_execution_block_guard(data)
    transports = review_http_websocket_socket_block_guard(data)
    account = review_account_read_only_contract(data)
    market = review_market_data_read_only_contract(data)
    orders = review_order_blocking_contract(data)
    positions = review_position_mutation_block_contract(data)
    observability = review_connection_observability_contract(data)
    journal = review_connection_journal_contract(data)
    human = review_connection_human_approval_contract(data)
    stops = review_connection_stop_conditions_contract(data)
    scores = (
        prep_score,
        contract.score,
        boundary.score,
        schema.score,
        credential.score,
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
    return PaperBrokerReadOnlyConnectionPreparationReviewScore(
        overall_score=_average(scores),
        connection_preparation_score=prep_score,
        connection_contract_score=contract.score,
        broker_adapter_boundary_score=boundary.score,
        configuration_schema_score=schema.score,
        credential_reference_score=credential.score,
        no_secret_read_guard_score=secret.score,
        network_block_guard_score=network.score,
        http_websocket_socket_block_guard_score=transports.score,
        account_read_only_score=account.score,
        market_data_read_only_score=market.score,
        order_blocking_score=orders.score,
        position_mutation_block_score=positions.score,
        observability_score=observability.score,
        journal_score=journal.score,
        human_approval_score=human.score,
        stop_conditions_score=stops.score,
    )


def detect_read_only_connection_preparation_review_risks(
    data: PaperBrokerReadOnlyConnectionPreparationReviewInput | Mapping[str, Any] | None,
) -> tuple[PaperBrokerReadOnlyConnectionPreparationReviewRisk, ...]:
    data = _coerce_input(data)
    risks: list[PaperBrokerReadOnlyConnectionPreparationReviewRisk] = []
    if not validate_connection_preparation_approval(data):
        risks.append(PaperBrokerReadOnlyConnectionPreparationReviewRisk.CONNECTION_PREPARATION_NOT_APPROVED)
    for review in _review_objects(data):
        risks.extend(_as_tuple(_get(review, "risks", ())))
    if not _offline_boundary(data):
        risks.append(PaperBrokerReadOnlyConnectionPreparationReviewRisk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(PaperBrokerReadOnlyConnectionPreparationReviewRisk.DATA_ACCESS_VIOLATION)
    if data.paper_broker_read_only_connection_dry_run_plan_requested is True:
        risks.append(PaperBrokerReadOnlyConnectionPreparationReviewRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN)
    return _dedupe(risks)


def generate_read_only_connection_preparation_review_recommendations(
    data: PaperBrokerReadOnlyConnectionPreparationReviewInput | Mapping[str, Any] | None,
) -> tuple[PaperBrokerReadOnlyConnectionPreparationReviewRecommendation, ...]:
    risks = detect_read_only_connection_preparation_review_risks(data)
    if not risks:
        return (
            PaperBrokerReadOnlyConnectionPreparationReviewRecommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW_SUITE,
            PaperBrokerReadOnlyConnectionPreparationReviewRecommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN,
        )
    mapping = {
        PaperBrokerReadOnlyConnectionPreparationReviewRisk.CONNECTION_PREPARATION_NOT_APPROVED: PaperBrokerReadOnlyConnectionPreparationReviewRecommendation.APPROVE_CONNECTION_PREPARATION_FIRST,
        PaperBrokerReadOnlyConnectionPreparationReviewRisk.READ_ONLY_CONNECTION_CONTRACT_REVIEW_FAILED: PaperBrokerReadOnlyConnectionPreparationReviewRecommendation.FIX_READ_ONLY_CONNECTION_CONTRACT,
        PaperBrokerReadOnlyConnectionPreparationReviewRisk.BROKER_ADAPTER_BOUNDARY_REVIEW_FAILED: PaperBrokerReadOnlyConnectionPreparationReviewRecommendation.FIX_BROKER_ADAPTER_BOUNDARY,
        PaperBrokerReadOnlyConnectionPreparationReviewRisk.CONNECTION_CONFIGURATION_SCHEMA_REVIEW_FAILED: PaperBrokerReadOnlyConnectionPreparationReviewRecommendation.FIX_CONNECTION_CONFIGURATION_SCHEMA,
        PaperBrokerReadOnlyConnectionPreparationReviewRisk.CREDENTIAL_REFERENCE_CONTRACT_REVIEW_FAILED: PaperBrokerReadOnlyConnectionPreparationReviewRecommendation.FIX_CREDENTIAL_REFERENCE_CONTRACT,
        PaperBrokerReadOnlyConnectionPreparationReviewRisk.SECRET_READ_GUARD_REVIEW_FAILED: PaperBrokerReadOnlyConnectionPreparationReviewRecommendation.FIX_NO_SECRET_READ_GUARD,
        PaperBrokerReadOnlyConnectionPreparationReviewRisk.NETWORK_EXECUTION_BLOCK_GUARD_REVIEW_FAILED: PaperBrokerReadOnlyConnectionPreparationReviewRecommendation.FIX_NETWORK_EXECUTION_BLOCK_GUARD,
        PaperBrokerReadOnlyConnectionPreparationReviewRisk.HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW_FAILED: PaperBrokerReadOnlyConnectionPreparationReviewRecommendation.FIX_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD,
        PaperBrokerReadOnlyConnectionPreparationReviewRisk.ACCOUNT_READ_ONLY_CONTRACT_REVIEW_FAILED: PaperBrokerReadOnlyConnectionPreparationReviewRecommendation.FIX_ACCOUNT_READ_ONLY_CONTRACT,
        PaperBrokerReadOnlyConnectionPreparationReviewRisk.MARKET_DATA_READ_ONLY_CONTRACT_REVIEW_FAILED: PaperBrokerReadOnlyConnectionPreparationReviewRecommendation.FIX_MARKET_DATA_READ_ONLY_CONTRACT,
        PaperBrokerReadOnlyConnectionPreparationReviewRisk.ORDER_BLOCKING_CONTRACT_REVIEW_FAILED: PaperBrokerReadOnlyConnectionPreparationReviewRecommendation.FIX_ORDER_BLOCKING_CONTRACT,
        PaperBrokerReadOnlyConnectionPreparationReviewRisk.POSITION_MUTATION_BLOCK_CONTRACT_REVIEW_FAILED: PaperBrokerReadOnlyConnectionPreparationReviewRecommendation.FIX_POSITION_MUTATION_BLOCK_CONTRACT,
        PaperBrokerReadOnlyConnectionPreparationReviewRisk.OBSERVABILITY_CONTRACT_REVIEW_FAILED: PaperBrokerReadOnlyConnectionPreparationReviewRecommendation.FIX_OBSERVABILITY_CONTRACT,
        PaperBrokerReadOnlyConnectionPreparationReviewRisk.JOURNAL_CONTRACT_REVIEW_FAILED: PaperBrokerReadOnlyConnectionPreparationReviewRecommendation.FIX_JOURNAL_CONTRACT,
        PaperBrokerReadOnlyConnectionPreparationReviewRisk.HUMAN_APPROVAL_CONTRACT_REVIEW_FAILED: PaperBrokerReadOnlyConnectionPreparationReviewRecommendation.FIX_HUMAN_APPROVAL_CONTRACT,
        PaperBrokerReadOnlyConnectionPreparationReviewRisk.STOP_CONDITION_CONTRACT_REVIEW_FAILED: PaperBrokerReadOnlyConnectionPreparationReviewRecommendation.FIX_STOP_CONDITION_CONTRACT,
        PaperBrokerReadOnlyConnectionPreparationReviewRisk.REAL_EXECUTION_BOUNDARY_VIOLATION: PaperBrokerReadOnlyConnectionPreparationReviewRecommendation.RESTORE_OFFLINE_BOUNDARIES,
        PaperBrokerReadOnlyConnectionPreparationReviewRisk.DATA_ACCESS_VIOLATION: PaperBrokerReadOnlyConnectionPreparationReviewRecommendation.REMOVE_DATA_ACCESS,
        PaperBrokerReadOnlyConnectionPreparationReviewRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN: PaperBrokerReadOnlyConnectionPreparationReviewRecommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN,
    }
    recommendations = [
        PaperBrokerReadOnlyConnectionPreparationReviewRecommendation.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN
    ]
    recommendations.extend(mapping[risk] for risk in risks if risk in mapping)
    return _dedupe(recommendations)


def _decision_for_risks(
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationReviewRisk, ...],
) -> PaperBrokerReadOnlyConnectionPreparationReviewDecision:
    if not risks:
        return PaperBrokerReadOnlyConnectionPreparationReviewDecision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW
    if PaperBrokerReadOnlyConnectionPreparationReviewRisk.CONNECTION_PREPARATION_NOT_APPROVED in risks:
        return PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_CONNECTION_PREPARATION_FIXES
    if PaperBrokerReadOnlyConnectionPreparationReviewRisk.READ_ONLY_CONNECTION_CONTRACT_REVIEW_FAILED in risks:
        return PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_CONNECTION_CONTRACT_REVIEW_FIXES
    if PaperBrokerReadOnlyConnectionPreparationReviewRisk.BROKER_ADAPTER_BOUNDARY_REVIEW_FAILED in risks:
        return PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_BROKER_ADAPTER_BOUNDARY_REVIEW_FIXES
    if PaperBrokerReadOnlyConnectionPreparationReviewRisk.CONNECTION_CONFIGURATION_SCHEMA_REVIEW_FAILED in risks:
        return PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_CONFIGURATION_SCHEMA_REVIEW_FIXES
    if PaperBrokerReadOnlyConnectionPreparationReviewRisk.CREDENTIAL_REFERENCE_CONTRACT_REVIEW_FAILED in risks:
        return PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_CREDENTIAL_REFERENCE_REVIEW_FIXES
    if PaperBrokerReadOnlyConnectionPreparationReviewRisk.SECRET_READ_GUARD_REVIEW_FAILED in risks:
        return PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_NO_SECRET_READ_GUARD_REVIEW_FIXES
    if any(
        risk in risks
        for risk in (
            PaperBrokerReadOnlyConnectionPreparationReviewRisk.NETWORK_EXECUTION_BLOCK_GUARD_REVIEW_FAILED,
            PaperBrokerReadOnlyConnectionPreparationReviewRisk.HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW_FAILED,
        )
    ):
        return PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_NETWORK_BLOCK_GUARD_REVIEW_FIXES
    if PaperBrokerReadOnlyConnectionPreparationReviewRisk.ACCOUNT_READ_ONLY_CONTRACT_REVIEW_FAILED in risks:
        return PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_ACCOUNT_READ_ONLY_CONTRACT_REVIEW_FIXES
    if PaperBrokerReadOnlyConnectionPreparationReviewRisk.MARKET_DATA_READ_ONLY_CONTRACT_REVIEW_FAILED in risks:
        return PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_MARKET_DATA_READ_ONLY_CONTRACT_REVIEW_FIXES
    if PaperBrokerReadOnlyConnectionPreparationReviewRisk.ORDER_BLOCKING_CONTRACT_REVIEW_FAILED in risks:
        return PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_ORDER_BLOCKING_CONTRACT_REVIEW_FIXES
    if PaperBrokerReadOnlyConnectionPreparationReviewRisk.POSITION_MUTATION_BLOCK_CONTRACT_REVIEW_FAILED in risks:
        return PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_POSITION_MUTATION_BLOCK_REVIEW_FIXES
    if PaperBrokerReadOnlyConnectionPreparationReviewRisk.OBSERVABILITY_CONTRACT_REVIEW_FAILED in risks:
        return PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_OBSERVABILITY_CONTRACT_REVIEW_FIXES
    if PaperBrokerReadOnlyConnectionPreparationReviewRisk.JOURNAL_CONTRACT_REVIEW_FAILED in risks:
        return PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_JOURNAL_CONTRACT_REVIEW_FIXES
    if PaperBrokerReadOnlyConnectionPreparationReviewRisk.HUMAN_APPROVAL_CONTRACT_REVIEW_FAILED in risks:
        return PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_HUMAN_APPROVAL_CONTRACT_REVIEW_FIXES
    if PaperBrokerReadOnlyConnectionPreparationReviewRisk.STOP_CONDITION_CONTRACT_REVIEW_FAILED in risks:
        return PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_STOP_CONDITION_CONTRACT_REVIEW_FIXES
    if any(
        risk in risks
        for risk in (
            PaperBrokerReadOnlyConnectionPreparationReviewRisk.REAL_EXECUTION_BOUNDARY_VIOLATION,
            PaperBrokerReadOnlyConnectionPreparationReviewRisk.DATA_ACCESS_VIOLATION,
        )
    ):
        return PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_BROKER_ADAPTER_BOUNDARY_REVIEW_FIXES
    return PaperBrokerReadOnlyConnectionPreparationReviewDecision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW


def _state_for_result(
    data: PaperBrokerReadOnlyConnectionPreparationReviewInput,
    risks: tuple[PaperBrokerReadOnlyConnectionPreparationReviewRisk, ...],
    score: PaperBrokerReadOnlyConnectionPreparationReviewScore,
) -> PaperBrokerReadOnlyConnectionPreparationReviewState:
    if data.paper_broker_read_only_connection_preparation is None:
        return PaperBrokerReadOnlyConnectionPreparationReviewState.CONNECTION_PREPARATION_REVIEW_INPUT_INVALID
    if not risks and score.overall_score >= 85:
        return PaperBrokerReadOnlyConnectionPreparationReviewState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN
    if risks:
        return PaperBrokerReadOnlyConnectionPreparationReviewState.CONNECTION_PREPARATION_REVIEW_BLOCKED
    if score.overall_score >= 70:
        return PaperBrokerReadOnlyConnectionPreparationReviewState.CONNECTION_PREPARATION_REVIEW_COMPLETED_WITH_WARNINGS
    return PaperBrokerReadOnlyConnectionPreparationReviewState.NOT_READY


def evaluate_paper_broker_read_only_connection_preparation_review(
    data: PaperBrokerReadOnlyConnectionPreparationReviewInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlyConnectionPreparationReviewResult:
    data = _coerce_input(data)
    score = compute_read_only_connection_preparation_review_score(data)
    risks = detect_read_only_connection_preparation_review_risks(data)
    recommendations = generate_read_only_connection_preparation_review_recommendations(data)
    decision = _decision_for_risks(risks)
    state = _state_for_result(data, risks, score)
    return PaperBrokerReadOnlyConnectionPreparationReviewResult(
        state=state,
        decision=decision,
        review_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        recommendations=recommendations,
        connection_contract_review=review_read_only_connection_contract(data),
        broker_adapter_boundary_review=review_broker_adapter_boundary(data),
        configuration_schema_review=review_connection_configuration_schema(data),
        credentials_reference_review=review_credentials_reference_contract(data),
        no_secret_read_guard_review=review_no_secret_read_guard(data),
        network_execution_block_guard_review=review_network_execution_block_guard(data),
        http_websocket_socket_block_guard_review=review_http_websocket_socket_block_guard(data),
        account_read_only_contract_review=review_account_read_only_contract(data),
        market_data_read_only_contract_review=review_market_data_read_only_contract(data),
        order_blocking_contract_review=review_order_blocking_contract(data),
        position_mutation_block_contract_review=review_position_mutation_block_contract(data),
        observability_contract_review=review_connection_observability_contract(data),
        journal_contract_review=review_connection_journal_contract(data),
        human_approval_contract_review=review_connection_human_approval_contract(data),
        stop_conditions_contract_review=review_connection_stop_conditions_contract(data),
        offline_only=True,
        summary=(
            "Paper broker read-only connection preparation review is approved for dry-run planning."
            if not risks
            else "Paper broker read-only connection preparation review is blocked until review risks are fixed."
        ),
    )


def render_paper_broker_read_only_connection_preparation_review_markdown(
    result: PaperBrokerReadOnlyConnectionPreparationReviewResult | Mapping[str, Any],
) -> str:
    if isinstance(result, Mapping):
        result = PaperBrokerReadOnlyConnectionPreparationReviewResult(**dict(result))
    risks = ", ".join(risk.value for risk in result.risks) or "none"
    recommendations = ", ".join(recommendation.value for recommendation in result.recommendations) or "none"
    sections = (
        ("connection_contract", result.connection_contract_review),
        ("broker_adapter_boundary", result.broker_adapter_boundary_review),
        ("configuration_schema", result.configuration_schema_review),
        ("credentials_reference", result.credentials_reference_review),
        ("no_secret_read_guard", result.no_secret_read_guard_review),
        ("network_execution_block_guard", result.network_execution_block_guard_review),
        ("http_websocket_socket_block_guard", result.http_websocket_socket_block_guard_review),
        ("account_read_only_contract", result.account_read_only_contract_review),
        ("market_data_read_only_contract", result.market_data_read_only_contract_review),
        ("order_blocking_contract", result.order_blocking_contract_review),
        ("position_mutation_block_contract", result.position_mutation_block_contract_review),
        ("observability_contract", result.observability_contract_review),
        ("journal_contract", result.journal_contract_review),
        ("human_approval_contract", result.human_approval_contract_review),
        ("stop_conditions_contract", result.stop_conditions_contract_review),
    )
    lines = [
        "# Paper Broker Read-Only Connection Preparation Review",
        "",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Review score: {result.review_score}",
        f"- Offline only: {result.offline_only}",
        f"- Risks: {risks}",
        f"- Recommendations: {recommendations}",
        "",
        "## Enforced Review Boundaries",
        "- No broker connection, dry run, or connection test",
        "- No API key or environment variable read",
        "- No HTTP, websocket, socket, or external API",
        "- No order execution, position mutation, or account access",
        "- No data/ access",
        "",
        "## Review Findings",
    ]
    for name, finding in sections:
        lines.append(f"- {name}: score={finding.score}, passed={finding.passed}, risks={len(finding.risks)}")
    if result.summary:
        lines.extend(("", f"Summary: {result.summary}"))
    return "\n".join(lines)
