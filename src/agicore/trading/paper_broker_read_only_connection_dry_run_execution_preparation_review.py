"""Offline review for AGIcore Paper Broker read-only connection dry-run execution preparation."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Callable, Iterable, Mapping

from agicore.trading import paper_broker_read_only_connection_dry_run_execution_preparation_review_models as m


def _coerce_input(data: m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewInput | Mapping[str, Any] | None) -> m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewInput:
    if data is None:
        return m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewInput()
    if isinstance(data, m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewInput):
        return data
    allowed = {field.name for field in fields(m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewInput)}
    return m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewInput(**{k: v for k, v in dict(data).items() if k in allowed})


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
    return default if not usable else _clamp(sum(usable) / len(usable))


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


def _preparation(data: m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewInput) -> Any:
    return data.paper_broker_read_only_connection_dry_run_execution_preparation


def _contract(data: m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewInput, name: str) -> Any:
    return _get(_preparation(data), name)


def _contract_ok(contract: Any) -> bool:
    return contract is not None and _get(contract, "defined", True) is True and not _as_tuple(_get(contract, "risks", ()))


def _upstream_items(data: m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewInput) -> tuple[Any, ...]:
    return (
        data.paper_broker_read_only_connection_dry_run_execution_preparation,
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


def _upstream_risks(data: m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _offline_boundary(data: m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewInput) -> bool:
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
        and data.dry_run_requested is not True
        and data.dry_run_executed is not True
        and all(_get(item, "offline_only", True) is True for item in _upstream_items(data))
        and not _has_upstream_risk(data, "LIVE_EXECUTION", "BROKER_CONNECTION", "API_KEY", "SECRET_READ", "NETWORK", "HTTP", "WEBSOCKET", "SOCKET", "REAL_ORDER", "REAL_ACCOUNT", "REAL_EXECUTION", "POSITION_MUTATION", "ALPACA_REAL")
    )


def _data_boundary(data: m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewInput) -> bool:
    return data.data_access_requested is not True and not _has_upstream_risk(data, "DATA_ACCESS", "DATA/", "REAL_DATA")


def validate_dry_run_execution_preparation_approval(data: m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewInput | Mapping[str, Any] | None) -> bool:
    data = _coerce_input(data)
    preparation = _preparation(data)
    if preparation is None or data.dry_run_execution_preparation_approved is False:
        return False
    approved_state = _state_contains(
        preparation,
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION",
    )
    approved = data.dry_run_execution_preparation_approved is True or approved_state
    return approved and not _as_tuple(_get(preparation, "risks", ())) and _get(preparation, "offline_only", True) is True

_Check = tuple[str, Callable[[m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewInput, Any], bool]]


def _review(
    data: m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewInput | Mapping[str, Any] | None,
    *,
    contract_name: str,
    flag_name: str,
    score_name: str,
    risk: m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk,
    cls: type,
    checks: tuple[_Check, ...],
    name: str | None = None,
) -> Any:
    data = _coerce_input(data)
    contract = _contract(data, contract_name)
    values = {field: check(data, contract) for field, check in checks}
    passed = _get(data, flag_name) is not False and _contract_ok(contract) and all(values.values())
    risks = () if passed else (risk,)
    payload = {
        "score": _metric_score(_get(data, score_name), _get(contract, "score"), passed),
        "passed": passed,
        "risks": risks,
        "details": (f"{contract_name} reviewed offline without dry-run execution",),
        **values,
    }
    if name is not None:
        payload["name"] = name
    return cls(**payload)


def review_dry_run_execution_runtime_contract(data):
    return _review(
        data,
        contract_name="dry_run_execution_runtime_contract",
        flag_name="dry_run_execution_runtime_contract_review_verified",
        score_name="runtime_contract_score",
        risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_RUNTIME_CONTRACT_REVIEW_FAILED,
        cls=m.DryRunExecutionRuntimeContractReviewFinding,
        checks=(
            ("preparation_only", lambda d, c: _get(c, "preparation_only") is True and d.dry_run_executed is not True),
            ("read_only_only", lambda d, c: _get(c, "read_only_only") is True),
            ("dry_run_execution_disabled", lambda d, c: _get(c, "dry_run_execution_disabled") is True),
        ),
    )


def review_dry_run_execution_sequence_contract(data):
    return _review(
        data,
        contract_name="dry_run_execution_sequence_contract",
        flag_name="dry_run_execution_sequence_contract_review_verified",
        score_name="sequence_contract_score",
        risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_SEQUENCE_CONTRACT_REVIEW_FAILED,
        cls=m.DryRunExecutionSequenceContractReviewFinding,
        checks=(
            ("dry_run_not_executed", lambda d, c: _get(c, "dry_run_not_executed") is True and d.dry_run_executed is not True),
            ("connection_not_executed", lambda d, c: _get(c, "connection_not_executed") is True and d.broker_connection_requested is not True),
            ("sequence_steps_defined", lambda d, c: _get(c, "sequence_steps_defined") is True),
            ("network_transport_blocked", lambda d, c: _get(c, "network_transport_blocked") is True),
        ),
    )


def review_dry_run_execution_precondition_contract(data):
    return _review(
        data,
        contract_name="dry_run_execution_precondition_contract",
        flag_name="dry_run_execution_precondition_contract_review_verified",
        score_name="precondition_contract_score",
        risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_PRECONDITION_REVIEW_FAILED,
        cls=m.DryRunExecutionPreconditionContractReviewFinding,
        checks=(
            ("safety_gate_required", lambda d, c: _get(c, "safety_gate_required") is True),
            ("human_approval_required", lambda d, c: _get(c, "human_approval_required") is True),
            ("stop_conditions_required", lambda d, c: _get(c, "stop_conditions_required") is True),
            ("fail_closed", lambda d, c: _get(c, "fail_closed") is True),
        ),
    )


def review_dry_run_execution_credentials_reference_contract(data):
    return _review(
        data,
        contract_name="dry_run_execution_credentials_reference_contract",
        flag_name="dry_run_execution_credential_reference_review_verified",
        score_name="credentials_reference_score",
        risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_CREDENTIAL_REFERENCE_REVIEW_FAILED,
        cls=m.DryRunExecutionCredentialsReferenceReviewFinding,
        checks=(
            ("reference_only", lambda d, c: _get(c, "reference_only") is True),
            ("no_secret_values", lambda d, c: _get(c, "no_secret_values") is True and d.hardcoded_secret_detected is not True),
            ("no_api_key_read", lambda d, c: _get(c, "no_api_key_read") is True and d.api_key_read_requested is not True),
            ("no_env_var_read", lambda d, c: _get(c, "no_env_var_read") is True and d.env_var_read_requested is not True),
        ),
    )


def review_dry_run_execution_no_secret_read_guard(data):
    return _review(
        data,
        contract_name="dry_run_execution_no_secret_read_guard",
        flag_name="dry_run_execution_no_secret_read_guard_review_verified",
        score_name="no_secret_read_guard_score",
        risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_SECRET_READ_GUARD_REVIEW_FAILED,
        cls=m.DryRunExecutionNoSecretReadGuardReviewFinding,
        checks=(
            ("guard_enforced", lambda d, c: _get(c, "guard_enforced") is True),
            ("no_api_key_read", lambda d, c: _get(c, "no_api_key_read") is True and d.api_key_read_requested is not True),
            ("no_env_var_read", lambda d, c: _get(c, "no_env_var_read") is True and d.env_var_read_requested is not True),
            ("no_hardcoded_secret", lambda d, c: _get(c, "no_hardcoded_secret") is True and d.hardcoded_secret_detected is not True),
        ),
    )


def _network_checks() -> tuple[_Check, ...]:
    return (
        ("network_execution_blocked", lambda d, c: _get(c, "network_execution_blocked") is True and d.network_transport_requested is not True),
        ("http_blocked", lambda d, c: _get(c, "http_blocked") is True and d.no_http_transport is True),
        ("websocket_blocked", lambda d, c: _get(c, "websocket_blocked") is True and d.no_websocket_transport is True),
        ("socket_blocked", lambda d, c: _get(c, "socket_blocked") is True and d.no_socket_transport is True),
        ("external_api_blocked", lambda d, c: _get(c, "external_api_blocked") is True and d.external_api_requested is not True),
    )


def review_dry_run_execution_network_block_guard(data):
    return _review(
        data,
        contract_name="dry_run_execution_network_block_guard",
        flag_name="dry_run_execution_network_block_guard_review_verified",
        score_name="network_block_guard_score",
        risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD_REVIEW_FAILED,
        cls=m.DryRunExecutionNetworkBlockGuardReviewFinding,
        checks=_network_checks(),
    )


def review_dry_run_execution_http_websocket_socket_block_guard(data):
    return _review(
        data,
        contract_name="dry_run_execution_http_websocket_socket_block_guard",
        flag_name="dry_run_execution_http_websocket_socket_block_guard_review_verified",
        score_name="http_websocket_socket_block_guard_score",
        risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW_FAILED,
        cls=m.DryRunExecutionNetworkBlockGuardReviewFinding,
        checks=_network_checks(),
        name="dry_run_execution_http_websocket_socket_block_guard_review",
    )


def review_dry_run_execution_account_read_only_contract(data):
    return _review(
        data,
        contract_name="dry_run_execution_account_read_only_contract",
        flag_name="dry_run_execution_account_read_only_review_verified",
        score_name="account_read_only_score",
        risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_REVIEW_FAILED,
        cls=m.DryRunExecutionAccountReadOnlyReviewFinding,
        checks=(
            ("active_account_access_blocked", lambda d, c: _get(c, "active_account_access_blocked") is True and d.account_access_requested is not True),
            ("account_mutations_blocked", lambda d, c: _get(c, "account_mutations_blocked") is True),
            ("schema_only_account_review", lambda d, c: _get(c, "schema_only_account_review") is True),
        ),
    )


def review_dry_run_execution_market_data_read_only_contract(data):
    return _review(
        data,
        contract_name="dry_run_execution_market_data_read_only_contract",
        flag_name="dry_run_execution_market_data_read_only_review_verified",
        score_name="market_data_read_only_score",
        risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_REVIEW_FAILED,
        cls=m.DryRunExecutionMarketDataReadOnlyReviewFinding,
        checks=(
            ("read_only_market_data_only", lambda d, c: _get(c, "read_only_market_data_only") is True),
            ("live_subscription_blocked", lambda d, c: _get(c, "live_subscription_blocked") is True),
            ("network_request_blocked", lambda d, c: _get(c, "network_request_blocked") is True and d.network_transport_requested is not True),
            ("schema_or_synthetic_only", lambda d, c: _get(c, "schema_or_synthetic_only") is True),
        ),
    )

def review_dry_run_execution_order_blocking_contract(data):
    return _review(
        data,
        contract_name="dry_run_execution_order_blocking_contract",
        flag_name="dry_run_execution_order_blocking_review_verified",
        score_name="order_blocking_score",
        risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_ORDER_BLOCKING_REVIEW_FAILED,
        cls=m.DryRunExecutionOrderBlockingReviewFinding,
        checks=(
            ("order_execution_blocked", lambda d, c: _get(c, "order_execution_blocked") is True and d.order_execution_requested is not True),
            ("real_order_blocked", lambda d, c: _get(c, "real_order_blocked") is True and d.no_real_order is True),
            ("cancel_replace_blocked", lambda d, c: _get(c, "cancel_replace_blocked") is True),
        ),
    )


def review_dry_run_execution_position_mutation_block_contract(data):
    return _review(
        data,
        contract_name="dry_run_execution_position_mutation_block_contract",
        flag_name="dry_run_execution_position_mutation_block_review_verified",
        score_name="position_mutation_block_score",
        risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_REVIEW_FAILED,
        cls=m.DryRunExecutionPositionMutationBlockReviewFinding,
        checks=(
            ("position_mutation_blocked", lambda d, c: _get(c, "position_mutation_blocked") is True and d.position_mutation_requested is not True),
            ("position_request_absent", lambda d, c: _get(c, "position_request_absent") is True),
            ("close_modify_blocked", lambda d, c: _get(c, "close_modify_blocked") is True),
        ),
    )


def review_dry_run_execution_observability_contract(data):
    return _review(
        data,
        contract_name="dry_run_execution_observability_contract",
        flag_name="dry_run_execution_observability_review_verified",
        score_name="observability_score",
        risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_OBSERVABILITY_REVIEW_FAILED,
        cls=m.DryRunExecutionObservabilityReviewFinding,
        checks=(
            ("offline_events_defined", lambda d, c: _get(c, "offline_events_defined") is True),
            ("connection_attempt_logging_disabled", lambda d, c: _get(c, "connection_attempt_logging_disabled") is True),
            ("sensitive_values_redacted", lambda d, c: _get(c, "sensitive_values_redacted") is True),
        ),
    )


def review_dry_run_execution_journal_contract(data):
    return _review(
        data,
        contract_name="dry_run_execution_journal_contract",
        flag_name="dry_run_execution_journal_review_verified",
        score_name="journal_score",
        risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_JOURNAL_REVIEW_FAILED,
        cls=m.DryRunExecutionJournalReviewFinding,
        checks=(
            ("offline_journal_required", lambda d, c: _get(c, "offline_journal_required") is True),
            ("sensitive_values_redacted", lambda d, c: _get(c, "sensitive_values_redacted") is True),
            ("no_secret_material_logged", lambda d, c: _get(c, "no_secret_material_logged") is True),
        ),
    )


def review_dry_run_execution_human_approval_contract(data):
    return _review(
        data,
        contract_name="dry_run_execution_human_approval_contract",
        flag_name="dry_run_execution_human_approval_review_verified",
        score_name="human_approval_score",
        risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_HUMAN_APPROVAL_REVIEW_FAILED,
        cls=m.DryRunExecutionHumanApprovalReviewFinding,
        checks=(
            ("human_approval_required", lambda d, c: _get(c, "human_approval_required") is True),
            ("approval_before_review", lambda d, c: _get(c, "approval_before_review") is True),
            ("safety_gate_evidence_required", lambda d, c: _get(c, "safety_gate_evidence_required") is True),
        ),
    )


def review_dry_run_execution_stop_conditions_contract(data):
    return _review(
        data,
        contract_name="dry_run_execution_stop_conditions_contract",
        flag_name="dry_run_execution_stop_conditions_review_verified",
        score_name="stop_conditions_score",
        risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_STOP_CONDITION_REVIEW_FAILED,
        cls=m.DryRunExecutionStopConditionReviewFinding,
        checks=(
            ("stop_on_secret_read", lambda d, c: _get(c, "stop_on_secret_read") is True),
            ("stop_on_network_request", lambda d, c: _get(c, "stop_on_network_request") is True),
            ("stop_on_order_or_position_request", lambda d, c: _get(c, "stop_on_order_or_position_request") is True),
            ("stop_on_account_access_request", lambda d, c: _get(c, "stop_on_account_access_request") is True),
        ),
    )


def review_dry_run_execution_success_failure_contract(data):
    return _review(
        data,
        contract_name="dry_run_execution_success_failure_contract",
        flag_name="dry_run_execution_success_failure_review_verified",
        score_name="success_failure_score",
        risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_SUCCESS_FAILURE_REVIEW_FAILED,
        cls=m.DryRunExecutionSuccessFailureReviewFinding,
        checks=(
            ("success_requires_no_real_connection", lambda d, c: _get(c, "success_requires_no_real_connection") is True),
            ("success_requires_all_guards_verified", lambda d, c: _get(c, "success_requires_all_guards_verified") is True),
            ("failure_on_secret_network_order_position_or_account", lambda d, c: _get(c, "failure_on_secret_network_order_position_or_account") is True),
        ),
    )


def review_dry_run_execution_audit_contract(data):
    return _review(
        data,
        contract_name="dry_run_execution_audit_contract",
        flag_name="dry_run_execution_audit_review_verified",
        score_name="audit_score",
        risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_AUDIT_REVIEW_FAILED,
        cls=m.DryRunExecutionAuditReviewFinding,
        checks=(
            ("audit_events_defined", lambda d, c: _get(c, "audit_events_defined") is True),
            ("offline_evidence_required", lambda d, c: _get(c, "offline_evidence_required") is True),
            ("preparation_review_trace_required", lambda d, c: _get(c, "preparation_review_trace_required") is True),
        ),
    )


def _review_objects(data: m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewInput) -> tuple[Any, ...]:
    return (
        review_dry_run_execution_runtime_contract(data),
        review_dry_run_execution_sequence_contract(data),
        review_dry_run_execution_precondition_contract(data),
        review_dry_run_execution_credentials_reference_contract(data),
        review_dry_run_execution_no_secret_read_guard(data),
        review_dry_run_execution_network_block_guard(data),
        review_dry_run_execution_http_websocket_socket_block_guard(data),
        review_dry_run_execution_account_read_only_contract(data),
        review_dry_run_execution_market_data_read_only_contract(data),
        review_dry_run_execution_order_blocking_contract(data),
        review_dry_run_execution_position_mutation_block_contract(data),
        review_dry_run_execution_observability_contract(data),
        review_dry_run_execution_journal_contract(data),
        review_dry_run_execution_human_approval_contract(data),
        review_dry_run_execution_stop_conditions_contract(data),
        review_dry_run_execution_success_failure_contract(data),
        review_dry_run_execution_audit_contract(data),
    )


def compute_read_only_connection_dry_run_execution_preparation_review_score(data):
    data = _coerce_input(data)
    prep_ok = validate_dry_run_execution_preparation_approval(data)
    prep_score = data.dry_run_execution_preparation_score
    if prep_score is None:
        prep_score = _get(_preparation(data), "preparation_score")
    prep_score = _metric_score(prep_score, None, prep_ok)
    reviews = _review_objects(data)
    scores = (prep_score,) + tuple(_get(review, "score") for review in reviews)
    return m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewScore(
        overall_score=_average(scores),
        dry_run_execution_preparation_score=prep_score,
        runtime_contract_score=reviews[0].score,
        sequence_contract_score=reviews[1].score,
        precondition_contract_score=reviews[2].score,
        credentials_reference_score=reviews[3].score,
        no_secret_read_guard_score=reviews[4].score,
        network_block_guard_score=reviews[5].score,
        http_websocket_socket_block_guard_score=reviews[6].score,
        account_read_only_score=reviews[7].score,
        market_data_read_only_score=reviews[8].score,
        order_blocking_score=reviews[9].score,
        position_mutation_block_score=reviews[10].score,
        observability_score=reviews[11].score,
        journal_score=reviews[12].score,
        human_approval_score=reviews[13].score,
        stop_conditions_score=reviews[14].score,
        success_failure_score=reviews[15].score,
        audit_score=reviews[16].score,
    )

def detect_read_only_connection_dry_run_execution_preparation_review_risks(data):
    data = _coerce_input(data)
    risks: list[m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk] = []
    if not validate_dry_run_execution_preparation_approval(data):
        risks.append(m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_PREPARATION_NOT_APPROVED)
    for review in _review_objects(data):
        risks.extend(_as_tuple(_get(review, "risks", ())))
    if not _offline_boundary(data):
        risks.append(m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DATA_ACCESS_VIOLATION)
    if data.paper_broker_read_only_connection_dry_run_execution_final_plan_requested is True or data.paper_broker_read_only_connection_dry_run_execution_controlled_run_plan_requested is True:
        risks.append(m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN)
    return _dedupe(risks)


def generate_read_only_connection_dry_run_execution_preparation_review_recommendations(data):
    risks = detect_read_only_connection_dry_run_execution_preparation_review_risks(data)
    rec = m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRecommendation
    risk = m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk
    if not risks:
        return (
            rec.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW_SUITE,
            rec.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN,
        )
    mapping = {
        risk.DRY_RUN_EXECUTION_PREPARATION_NOT_APPROVED: rec.APPROVE_DRY_RUN_EXECUTION_PREPARATION_FIRST,
        risk.DRY_RUN_EXECUTION_RUNTIME_CONTRACT_REVIEW_FAILED: rec.FIX_DRY_RUN_EXECUTION_RUNTIME_CONTRACT_REVIEW,
        risk.DRY_RUN_EXECUTION_SEQUENCE_CONTRACT_REVIEW_FAILED: rec.FIX_DRY_RUN_EXECUTION_SEQUENCE_CONTRACT_REVIEW,
        risk.DRY_RUN_EXECUTION_PRECONDITION_REVIEW_FAILED: rec.FIX_DRY_RUN_EXECUTION_PRECONDITION_REVIEW,
        risk.DRY_RUN_EXECUTION_CREDENTIAL_REFERENCE_REVIEW_FAILED: rec.FIX_DRY_RUN_EXECUTION_CREDENTIAL_REFERENCE_REVIEW,
        risk.DRY_RUN_EXECUTION_SECRET_READ_GUARD_REVIEW_FAILED: rec.FIX_DRY_RUN_EXECUTION_NO_SECRET_READ_GUARD_REVIEW,
        risk.DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD_REVIEW_FAILED: rec.FIX_DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD_REVIEW,
        risk.DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW_FAILED: rec.FIX_DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW,
        risk.DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_REVIEW_FAILED: rec.FIX_DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_REVIEW,
        risk.DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_REVIEW_FAILED: rec.FIX_DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_REVIEW,
        risk.DRY_RUN_EXECUTION_ORDER_BLOCKING_REVIEW_FAILED: rec.FIX_DRY_RUN_EXECUTION_ORDER_BLOCKING_REVIEW,
        risk.DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_REVIEW_FAILED: rec.FIX_DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_REVIEW,
        risk.DRY_RUN_EXECUTION_OBSERVABILITY_REVIEW_FAILED: rec.FIX_DRY_RUN_EXECUTION_OBSERVABILITY_REVIEW,
        risk.DRY_RUN_EXECUTION_JOURNAL_REVIEW_FAILED: rec.FIX_DRY_RUN_EXECUTION_JOURNAL_REVIEW,
        risk.DRY_RUN_EXECUTION_HUMAN_APPROVAL_REVIEW_FAILED: rec.FIX_DRY_RUN_EXECUTION_HUMAN_APPROVAL_REVIEW,
        risk.DRY_RUN_EXECUTION_STOP_CONDITION_REVIEW_FAILED: rec.FIX_DRY_RUN_EXECUTION_STOP_CONDITION_REVIEW,
        risk.DRY_RUN_EXECUTION_SUCCESS_FAILURE_REVIEW_FAILED: rec.FIX_DRY_RUN_EXECUTION_SUCCESS_FAILURE_REVIEW,
        risk.DRY_RUN_EXECUTION_AUDIT_REVIEW_FAILED: rec.FIX_DRY_RUN_EXECUTION_AUDIT_REVIEW,
        risk.REAL_EXECUTION_BOUNDARY_VIOLATION: rec.RESTORE_OFFLINE_BOUNDARIES,
        risk.DATA_ACCESS_VIOLATION: rec.REMOVE_DATA_ACCESS,
        risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN: rec.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN,
    }
    recommendations = [rec.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN]
    recommendations.extend(mapping[item] for item in risks if item in mapping)
    return _dedupe(recommendations)


def _decision_for_risks(risks):
    decision = m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewDecision
    risk = m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk
    if not risks:
        return decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW
    if risk.DRY_RUN_EXECUTION_PREPARATION_NOT_APPROVED in risks:
        return decision.REQUIRE_DRY_RUN_EXECUTION_PREPARATION_FIXES
    if risk.REAL_EXECUTION_BOUNDARY_VIOLATION in risks or risk.DATA_ACCESS_VIOLATION in risks:
        return decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW
    ordered = (
        (risk.DRY_RUN_EXECUTION_RUNTIME_CONTRACT_REVIEW_FAILED, decision.REQUIRE_DRY_RUN_EXECUTION_RUNTIME_CONTRACT_REVIEW_FIXES),
        (risk.DRY_RUN_EXECUTION_SEQUENCE_CONTRACT_REVIEW_FAILED, decision.REQUIRE_DRY_RUN_EXECUTION_SEQUENCE_CONTRACT_REVIEW_FIXES),
        (risk.DRY_RUN_EXECUTION_PRECONDITION_REVIEW_FAILED, decision.REQUIRE_DRY_RUN_EXECUTION_PRECONDITION_REVIEW_FIXES),
        (risk.DRY_RUN_EXECUTION_CREDENTIAL_REFERENCE_REVIEW_FAILED, decision.REQUIRE_DRY_RUN_EXECUTION_CREDENTIAL_REFERENCE_REVIEW_FIXES),
        (risk.DRY_RUN_EXECUTION_SECRET_READ_GUARD_REVIEW_FAILED, decision.REQUIRE_DRY_RUN_EXECUTION_NO_SECRET_READ_GUARD_REVIEW_FIXES),
        (risk.DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD_REVIEW_FAILED, decision.REQUIRE_DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD_REVIEW_FIXES),
        (risk.DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW_FAILED, decision.REQUIRE_DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD_REVIEW_FIXES),
        (risk.DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_REVIEW_FAILED, decision.REQUIRE_DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_REVIEW_FIXES),
        (risk.DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_REVIEW_FAILED, decision.REQUIRE_DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_REVIEW_FIXES),
        (risk.DRY_RUN_EXECUTION_ORDER_BLOCKING_REVIEW_FAILED, decision.REQUIRE_DRY_RUN_EXECUTION_ORDER_BLOCKING_REVIEW_FIXES),
        (risk.DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_REVIEW_FAILED, decision.REQUIRE_DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_REVIEW_FIXES),
        (risk.DRY_RUN_EXECUTION_OBSERVABILITY_REVIEW_FAILED, decision.REQUIRE_DRY_RUN_EXECUTION_OBSERVABILITY_REVIEW_FIXES),
        (risk.DRY_RUN_EXECUTION_JOURNAL_REVIEW_FAILED, decision.REQUIRE_DRY_RUN_EXECUTION_JOURNAL_REVIEW_FIXES),
        (risk.DRY_RUN_EXECUTION_HUMAN_APPROVAL_REVIEW_FAILED, decision.REQUIRE_DRY_RUN_EXECUTION_HUMAN_APPROVAL_REVIEW_FIXES),
        (risk.DRY_RUN_EXECUTION_STOP_CONDITION_REVIEW_FAILED, decision.REQUIRE_DRY_RUN_EXECUTION_STOP_CONDITION_REVIEW_FIXES),
        (risk.DRY_RUN_EXECUTION_SUCCESS_FAILURE_REVIEW_FAILED, decision.REQUIRE_DRY_RUN_EXECUTION_SUCCESS_FAILURE_REVIEW_FIXES),
        (risk.DRY_RUN_EXECUTION_AUDIT_REVIEW_FAILED, decision.REQUIRE_DRY_RUN_EXECUTION_AUDIT_REVIEW_FIXES),
    )
    for item, selected in ordered:
        if item in risks:
            return selected
    return decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW


def _state_for_result(data, risks, score):
    state = m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewState
    if data.paper_broker_read_only_connection_dry_run_execution_preparation is None:
        return state.DRY_RUN_EXECUTION_PREPARATION_REVIEW_INPUT_INVALID
    if not risks and score.overall_score >= 85:
        return state.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN
    if risks:
        return state.DRY_RUN_EXECUTION_PREPARATION_REVIEW_BLOCKED
    if score.overall_score >= 70:
        return state.DRY_RUN_EXECUTION_PREPARATION_REVIEW_COMPLETED_WITH_WARNINGS
    return state.NOT_READY


def evaluate_paper_broker_read_only_connection_dry_run_execution_preparation_review(data):
    data = _coerce_input(data)
    score = compute_read_only_connection_dry_run_execution_preparation_review_score(data)
    risks = detect_read_only_connection_dry_run_execution_preparation_review_risks(data)
    reviews = _review_objects(data)
    return m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewResult(
        state=_state_for_result(data, risks, score),
        decision=_decision_for_risks(risks),
        review_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        recommendations=generate_read_only_connection_dry_run_execution_preparation_review_recommendations(data),
        dry_run_execution_runtime_contract_review=reviews[0],
        dry_run_execution_sequence_contract_review=reviews[1],
        dry_run_execution_precondition_contract_review=reviews[2],
        dry_run_execution_credentials_reference_review=reviews[3],
        dry_run_execution_no_secret_read_guard_review=reviews[4],
        dry_run_execution_network_block_guard_review=reviews[5],
        dry_run_execution_http_websocket_socket_block_guard_review=reviews[6],
        dry_run_execution_account_read_only_contract_review=reviews[7],
        dry_run_execution_market_data_read_only_contract_review=reviews[8],
        dry_run_execution_order_blocking_contract_review=reviews[9],
        dry_run_execution_position_mutation_block_contract_review=reviews[10],
        dry_run_execution_observability_contract_review=reviews[11],
        dry_run_execution_journal_contract_review=reviews[12],
        dry_run_execution_human_approval_contract_review=reviews[13],
        dry_run_execution_stop_conditions_contract_review=reviews[14],
        dry_run_execution_success_failure_contract_review=reviews[15],
        dry_run_execution_audit_contract_review=reviews[16],
        offline_only=True,
        summary=(
            "Paper broker read-only connection dry-run execution preparation review is approved for final plan."
            if not risks
            else "Paper broker read-only connection dry-run execution preparation review is blocked until review risks are fixed."
        ),
    )


def render_paper_broker_read_only_connection_dry_run_execution_preparation_review_markdown(result):
    if isinstance(result, Mapping):
        result = m.PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewResult(**dict(result))
    risks = ", ".join(risk.value for risk in result.risks) or "none"
    recommendations = ", ".join(recommendation.value for recommendation in result.recommendations) or "none"
    sections = (
        ("dry_run_execution_runtime_contract", result.dry_run_execution_runtime_contract_review),
        ("dry_run_execution_sequence_contract", result.dry_run_execution_sequence_contract_review),
        ("dry_run_execution_precondition_contract", result.dry_run_execution_precondition_contract_review),
        ("dry_run_execution_credentials_reference", result.dry_run_execution_credentials_reference_review),
        ("dry_run_execution_no_secret_read_guard", result.dry_run_execution_no_secret_read_guard_review),
        ("dry_run_execution_network_block_guard", result.dry_run_execution_network_block_guard_review),
        ("dry_run_execution_http_websocket_socket_block_guard", result.dry_run_execution_http_websocket_socket_block_guard_review),
        ("dry_run_execution_account_read_only_contract", result.dry_run_execution_account_read_only_contract_review),
        ("dry_run_execution_market_data_read_only_contract", result.dry_run_execution_market_data_read_only_contract_review),
        ("dry_run_execution_order_blocking_contract", result.dry_run_execution_order_blocking_contract_review),
        ("dry_run_execution_position_mutation_block_contract", result.dry_run_execution_position_mutation_block_contract_review),
        ("dry_run_execution_observability_contract", result.dry_run_execution_observability_contract_review),
        ("dry_run_execution_journal_contract", result.dry_run_execution_journal_contract_review),
        ("dry_run_execution_human_approval_contract", result.dry_run_execution_human_approval_contract_review),
        ("dry_run_execution_stop_conditions_contract", result.dry_run_execution_stop_conditions_contract_review),
        ("dry_run_execution_success_failure_contract", result.dry_run_execution_success_failure_contract_review),
        ("dry_run_execution_audit_contract", result.dry_run_execution_audit_contract_review),
    )
    lines = [
        "# Paper Broker Read-Only Connection Dry Run Execution Preparation Review",
        "",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Review score: {result.review_score}",
        f"- Offline only: {result.offline_only}",
        f"- Risks: {risks}",
        f"- Recommendations: {recommendations}",
        "",
        "## Enforced Review Boundaries",
        "- Review only: no dry-run execution and no connection test",
        "- No broker, Alpaca, API key, environment variable, or hardcoded secret read",
        "- No HTTP, websocket, socket, network transport, or external API",
        "- No order execution, position mutation, trading, or active account access",
        "- No data/ access",
        "",
        "## Review Findings",
    ]
    for name, finding in sections:
        lines.append(f"- {name}: score={finding.score}, passed={finding.passed}, risks={len(finding.risks)}")
    if result.summary:
        lines.extend(("", f"Summary: {result.summary}"))
    return "\n".join(lines)
