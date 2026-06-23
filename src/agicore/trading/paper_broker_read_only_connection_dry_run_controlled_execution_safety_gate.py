"""Offline controlled execution safety gate for AGIcore read-only connection dry-run execution final plans."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate_models import (
    ControlledAccountReadOnlySafetyFinding,
    ControlledAuditSafetyFinding,
    ControlledCredentialsSafetyFinding,
    ControlledAbortPolicySafetyFinding,
    ControlledExecutionPreconditionSafetyFinding,
    ControlledExecutionScopeSafetyFinding,
    ControlledExecutionSequenceSafetyFinding,
    ControlledGoNoGoSafetyFinding,
    ControlledHumanApprovalSafetyFinding,
    ControlledJournalSafetyFinding,
    ControlledMarketDataReadOnlySafetyFinding,
    ControlledNetworkBlockSafetyFinding,
    ControlledObservabilitySafetyFinding,
    ControlledOrderBlockingSafetyFinding,
    ControlledPositionMutationBlockSafetyFinding,
    ControlledStopConditionSafetyFinding,
    ControlledSuccessFailureSafetyFinding,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateDecision,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateInput,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRecommendation,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateResult,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRisk,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateScore,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateState,
)


Risk = PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRisk
Decision = PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateDecision
Recommendation = PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateRecommendation


def _coerce_input(
    data: PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateInput | Mapping[str, Any] | None,
) -> PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateInput:
    if data is None:
        return PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateInput()
    if isinstance(data, PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateInput):
        return data
    allowed = {field.name for field in fields(PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateInput)}
    return PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateInput(
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
    return default if not usable else _clamp(sum(usable) / len(usable))


def _metric_score(explicit: int | None, fallback: Any, passed: bool) -> int:
    if explicit is not None:
        return _clamp(explicit)
    if fallback is not None:
        return _clamp(fallback)
    return 100 if passed else 0


def _plan(data: PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateInput) -> Any:
    return data.paper_broker_read_only_connection_dry_run_controlled_execution_plan


_SECTION_ATTRS = {
    "scope": "controlled_dry_run_execution_scope",
    "sequence": "controlled_dry_run_execution_sequence",
    "precondition": "controlled_dry_run_execution_precondition",
    "credentials_reference_policy": "controlled_credentials_reference_policy",
    "no_secret_read_policy": "controlled_no_secret_read_policy",
    "network_block_policy": "controlled_network_block_policy",
    "http_websocket_socket_block_policy": "controlled_http_websocket_socket_block_policy",
    "account_read_only_policy": "controlled_account_read_only_policy",
    "market_data_read_only_policy": "controlled_market_data_read_only_policy",
    "order_blocking_policy": "controlled_order_blocking_policy",
    "position_mutation_block_policy": "controlled_position_mutation_block_policy",
    "observability_plan": "controlled_observability_plan",
    "journal_plan": "controlled_journal_plan",
    "human_approval_plan": "controlled_human_approval_plan",
    "stop_conditions_plan": "controlled_stop_conditions_plan",
    "success_criteria": "controlled_success_criteria",
    "failure_criteria": "controlled_failure_criteria",
    "audit_plan": "controlled_audit_plan",
    "go_no_go_policy": "controlled_go_no_go_policy",
    "abort_policy": "controlled_abort_policy",
}


def _section(data: PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateInput, name: str) -> Any:
    return _get(_plan(data), _SECTION_ATTRS[name])


def _section_ok(section: Any) -> bool:
    return (
        section is not None
        and _get(section, "defined", True) is True
        and _get(section, "passed", True) is True
        and not _as_tuple(_get(section, "risks", ()))
    )


def _upstream_items(data: PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateInput) -> tuple[Any, ...]:
    return (
        data.paper_broker_read_only_connection_dry_run_controlled_execution_plan,
        data.paper_broker_read_only_connection_dry_run_execution_preparation_review,
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
    )


def _upstream_risks(data: PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _offline_boundary(data: PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateInput) -> bool:
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


def _data_boundary(data: PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateInput) -> bool:
    return data.data_access_requested is not True and not _has_upstream_risk(data, "DATA_ACCESS", "DATA/")


def validate_controlled_execution_plan_approval(
    data: PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateInput | Mapping[str, Any] | None,
) -> bool:
    data = _coerce_input(data)
    plan = _plan(data)
    if plan is None or data.controlled_execution_plan_approved is False:
        return False
    approved_state = _state_contains(
        plan,
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PLAN",
    )
    approved = data.controlled_execution_plan_approved is True or approved_state
    return approved and not _as_tuple(_get(plan, "risks", ())) and _get(plan, "offline_only", True) is True


def _finding(cls: Any, score: int, passed: bool, risk: Risk, details: str, *values: bool) -> Any:
    return cls(score, passed, () if passed else (risk,), (details,), *values)


def verify_controlled_execution_scope_safety(data):
    data = _coerce_input(data)
    section = _section(data, "scope")
    values = (
        _get(section, "offline_only") is True and _offline_boundary(data),
        _get(section, "sandbox_only") is True,
        _get(section, "controlled_plan_only") is True,
        _get(section, "dry_run_execution_disabled") is True and data.dry_run_executed is not True,
        _offline_boundary(data) and _data_boundary(data),
    )
    passed = data.controlled_execution_scope_safety_verified is not False and _section_ok(section) and all(values)
    return _finding(ControlledExecutionScopeSafetyFinding, _metric_score(data.scope_score, _get(section, "score"), passed), passed, Risk.CONTROLLED_EXECUTION_SCOPE_UNSAFE, "controlled_execution_scope_safety", *values)


def verify_controlled_execution_sequence_safety(data):
    data = _coerce_input(data)
    section = _section(data, "sequence")
    values = (
        _get(section, "sequence_steps_defined") is True,
        _get(section, "dry_run_not_executed") is True,
        _get(section, "connection_not_executed") is True,
        _get(section, "fail_closed") is True,
    )
    passed = data.controlled_execution_sequence_safety_verified is not False and _section_ok(section) and all(values)
    return _finding(ControlledExecutionSequenceSafetyFinding, _metric_score(data.sequence_score, _get(section, "score"), passed), passed, Risk.CONTROLLED_EXECUTION_SEQUENCE_UNSAFE, "controlled_execution_sequence_safety", *values)


def verify_controlled_execution_precondition_safety(data):
    data = _coerce_input(data)
    section = _section(data, "precondition")
    values = (
        validate_controlled_execution_plan_approval(data),
        _get(section, "safety_gate_required") is True,
        _get(section, "human_approval_required") is True,
        _get(section, "stop_conditions_required") is True,
    )
    passed = data.controlled_execution_precondition_safety_verified is not False and _section_ok(section) and all(values)
    return _finding(ControlledExecutionPreconditionSafetyFinding, _metric_score(data.precondition_score, _get(section, "score"), passed), passed, Risk.CONTROLLED_EXECUTION_PRECONDITION_UNSAFE, "controlled_execution_precondition_safety", *values)


def verify_controlled_credentials_reference_safety(data):
    data = _coerce_input(data)
    section = _section(data, "credentials_reference_policy")
    values = (
        _get(section, "reference_only") is True,
        _get(section, "no_secret_values") is True,
        _get(section, "no_api_key_read") is True,
        _get(section, "no_env_var_read") is True,
    )
    passed = data.controlled_credentials_reference_safety_verified is not False and _section_ok(section) and all(values)
    return _finding(ControlledCredentialsSafetyFinding, _metric_score(data.credentials_score, _get(section, "score"), passed), passed, Risk.CONTROLLED_CREDENTIAL_POLICY_UNSAFE, "controlled_credentials_reference_safety", *values)


def verify_controlled_no_secret_read_safety(data):
    data = _coerce_input(data)
    section = _section(data, "no_secret_read_policy")
    values = (
        True,
        _get(section, "no_hardcoded_secret") is True and data.hardcoded_secret_detected is not True,
        _get(section, "no_api_key_read") is True and data.api_key_read_requested is not True,
        _get(section, "no_env_var_read") is True and data.env_var_read_requested is not True,
    )
    passed = data.controlled_no_secret_read_safety_verified is not False and _section_ok(section) and all(values) and _get(section, "fail_on_secret_read_request") is True
    return _finding(ControlledCredentialsSafetyFinding, _metric_score(data.no_secret_read_score, _get(section, "score"), passed), passed, Risk.CONTROLLED_SECRET_READ_POLICY_UNSAFE, "controlled_no_secret_read_safety", *values)


def verify_controlled_network_block_safety(data):
    data = _coerce_input(data)
    section = _section(data, "network_block_policy")
    values = (
        _get(section, "network_execution_blocked") is True and data.network_transport_requested is not True,
        _get(section, "http_blocked") is True,
        _get(section, "websocket_blocked") is True,
        _get(section, "socket_blocked") is True,
        _get(section, "external_api_blocked") is True and data.external_api_requested is not True,
    )
    passed = data.controlled_network_block_safety_verified is not False and _section_ok(section) and all(values)
    return _finding(ControlledNetworkBlockSafetyFinding, _metric_score(data.network_block_score, _get(section, "score"), passed), passed, Risk.CONTROLLED_NETWORK_NOT_BLOCKED, "controlled_network_block_safety", *values)


def verify_controlled_http_websocket_socket_block_safety(data):
    data = _coerce_input(data)
    section = _section(data, "http_websocket_socket_block_policy")
    values = (
        _get(section, "network_execution_blocked") is True and data.network_transport_requested is not True,
        _get(section, "http_blocked") is True,
        _get(section, "websocket_blocked") is True,
        _get(section, "socket_blocked") is True,
        _get(section, "external_api_blocked") is True,
    )
    passed = data.controlled_http_websocket_socket_block_safety_verified is not False and _section_ok(section) and all(values)
    return _finding(ControlledNetworkBlockSafetyFinding, _metric_score(data.http_websocket_socket_block_score, _get(section, "score"), passed), passed, Risk.CONTROLLED_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED, "controlled_http_websocket_socket_block_safety", *values)


def verify_controlled_account_read_only_safety(data):
    data = _coerce_input(data)
    section = _section(data, "account_read_only_policy")
    values = (
        _get(section, "active_account_access_blocked") is True and data.account_access_requested is not True,
        _get(section, "account_mutations_blocked") is True,
        _get(section, "schema_only_account_review") is True,
    )
    passed = data.controlled_account_read_only_safety_verified is not False and _section_ok(section) and all(values)
    return _finding(ControlledAccountReadOnlySafetyFinding, _metric_score(data.account_read_only_score, _get(section, "score"), passed), passed, Risk.CONTROLLED_ACCOUNT_READ_ONLY_UNSAFE, "controlled_account_read_only_safety", *values)


def verify_controlled_market_data_read_only_safety(data):
    data = _coerce_input(data)
    section = _section(data, "market_data_read_only_policy")
    values = (
        _get(section, "read_only_market_data_only") is True,
        _get(section, "live_subscription_blocked") is True,
        _get(section, "network_request_blocked") is True and data.network_transport_requested is not True,
        _get(section, "schema_or_synthetic_only") is True,
    )
    passed = data.controlled_market_data_read_only_safety_verified is not False and _section_ok(section) and all(values)
    return _finding(ControlledMarketDataReadOnlySafetyFinding, _metric_score(data.market_data_read_only_score, _get(section, "score"), passed), passed, Risk.CONTROLLED_MARKET_DATA_READ_ONLY_UNSAFE, "controlled_market_data_read_only_safety", *values)


def verify_controlled_order_blocking_safety(data):
    data = _coerce_input(data)
    section = _section(data, "order_blocking_policy")
    values = (
        _get(section, "order_execution_blocked") is True and data.order_execution_requested is not True,
        _get(section, "real_order_blocked") is True,
        _get(section, "cancel_replace_blocked") is True,
    )
    passed = data.controlled_order_blocking_safety_verified is not False and _section_ok(section) and all(values)
    return _finding(ControlledOrderBlockingSafetyFinding, _metric_score(data.order_blocking_score, _get(section, "score"), passed), passed, Risk.CONTROLLED_ORDER_BLOCKING_UNSAFE, "controlled_order_blocking_safety", *values)


def verify_controlled_position_mutation_block_safety(data):
    data = _coerce_input(data)
    section = _section(data, "position_mutation_block_policy")
    values = (
        _get(section, "position_mutation_blocked") is True and data.position_mutation_requested is not True,
        _get(section, "position_request_absent") is True,
        _get(section, "close_modify_blocked") is True,
    )
    passed = data.controlled_position_mutation_block_safety_verified is not False and _section_ok(section) and all(values)
    return _finding(ControlledPositionMutationBlockSafetyFinding, _metric_score(data.position_mutation_block_score, _get(section, "score"), passed), passed, Risk.CONTROLLED_POSITION_MUTATION_BLOCK_UNSAFE, "controlled_position_mutation_block_safety", *values)


def verify_controlled_observability_safety(data):
    data = _coerce_input(data)
    section = _section(data, "observability_plan")
    values = (
        _get(section, "offline_events_defined") is True,
        _get(section, "connection_attempt_logging_disabled") is True,
        _get(section, "sensitive_values_redacted") is True,
    )
    passed = data.controlled_observability_safety_verified is not False and _section_ok(section) and all(values)
    return _finding(ControlledObservabilitySafetyFinding, _metric_score(data.observability_score, _get(section, "score"), passed), passed, Risk.CONTROLLED_OBSERVABILITY_INCOMPLETE, "controlled_observability_safety", *values)


def verify_controlled_journal_safety(data):
    data = _coerce_input(data)
    section = _section(data, "journal_plan")
    values = (
        _get(section, "offline_journal_required") is True,
        _get(section, "sensitive_values_redacted") is True,
        _get(section, "no_secret_material_logged") is True,
    )
    passed = data.controlled_journal_safety_verified is not False and _section_ok(section) and all(values)
    return _finding(ControlledJournalSafetyFinding, _metric_score(data.journal_score, _get(section, "score"), passed), passed, Risk.CONTROLLED_JOURNAL_INCOMPLETE, "controlled_journal_safety", *values)


def verify_controlled_human_approval_safety(data):
    data = _coerce_input(data)
    section = _section(data, "human_approval_plan")
    values = (
        _get(section, "human_approval_required") is True,
        _get(section, "approval_before_safety_gate") is True,
        _get(section, "final_safety_gate_evidence_required") is True,
    )
    passed = data.controlled_human_approval_safety_verified is not False and _section_ok(section) and all(values)
    return _finding(ControlledHumanApprovalSafetyFinding, _metric_score(data.human_approval_score, _get(section, "score"), passed), passed, Risk.CONTROLLED_HUMAN_APPROVAL_MISSING, "controlled_human_approval_safety", *values)


def verify_controlled_stop_conditions_safety(data):
    data = _coerce_input(data)
    section = _section(data, "stop_conditions_plan")
    values = (
        _get(section, "stop_on_secret_read") is True,
        _get(section, "stop_on_network_request") is True,
        _get(section, "stop_on_order_or_position_request") is True,
        _get(section, "stop_on_account_access_request") is True,
    )
    passed = data.controlled_stop_conditions_safety_verified is not False and _section_ok(section) and all(values)
    return _finding(ControlledStopConditionSafetyFinding, _metric_score(data.stop_conditions_score, _get(section, "score"), passed), passed, Risk.CONTROLLED_STOP_CONDITIONS_MISSING, "controlled_stop_conditions_safety", *values)


def verify_controlled_success_failure_criteria_safety(data):
    data = _coerce_input(data)
    success = _section(data, "success_criteria")
    failure = _section(data, "failure_criteria")
    success_ok = (
        _section_ok(success)
        and _get(success, "success_requires_no_real_connection") is True
        and _get(success, "success_requires_all_guards_verified") is True
        and _get(success, "success_requires_go_no_go_approval") is True
    )
    failure_ok = (
        _section_ok(failure)
        and _get(failure, "failure_on_secret_read") is True
        and _get(failure, "failure_on_network_request") is True
        and _get(failure, "failure_on_order_position_or_account") is True
    )
    passed = data.controlled_success_failure_criteria_safety_verified is not False and success_ok and failure_ok
    fallback = _average((_get(success, "score"), _get(failure, "score"))) if success is not None and failure is not None else None
    values = (_get(success, "defined") is True, _get(failure, "defined") is True, _get(success, "success_requires_no_real_connection") is True, failure_ok)
    return _finding(ControlledSuccessFailureSafetyFinding, _metric_score(data.success_failure_criteria_score, fallback, passed), passed, Risk.CONTROLLED_SUCCESS_FAILURE_CRITERIA_UNSAFE, "controlled_success_failure_criteria_safety", *values)


def verify_controlled_audit_plan_safety(data):
    data = _coerce_input(data)
    section = _section(data, "audit_plan")
    values = (
        _get(section, "audit_events_defined") is True,
        _get(section, "offline_evidence_required") is True,
        _get(section, "controlled_plan_trace_required") is True,
    )
    passed = data.controlled_audit_plan_safety_verified is not False and _section_ok(section) and all(values)
    return _finding(ControlledAuditSafetyFinding, _metric_score(data.audit_plan_score, _get(section, "score"), passed), passed, Risk.CONTROLLED_AUDIT_PLAN_MISSING, "controlled_audit_plan_safety", *values)


def verify_controlled_go_no_go_policy_safety(data):
    data = _coerce_input(data)
    section = _section(data, "go_no_go_policy")
    values = (
        _get(section, "go_requires_all_sections_ready") is True,
        _get(section, "no_go_on_any_boundary_violation") is True,
        _get(section, "human_go_required") is True,
    )
    passed = data.controlled_go_no_go_policy_safety_verified is not False and _section_ok(section) and all(values)
    return _finding(ControlledGoNoGoSafetyFinding, _metric_score(data.go_no_go_score, _get(section, "score"), passed), passed, Risk.CONTROLLED_GO_NO_GO_POLICY_MISSING, "controlled_go_no_go_policy_safety", *values)


def verify_controlled_abort_policy_safety(data):
    data = _coerce_input(data)
    section = _section(data, "abort_policy")
    values = (
        _get(section, "abort_on_secret_read") is True,
        _get(section, "abort_on_network_request") is True,
        _get(section, "abort_on_order_position_or_account") is True,
        _get(section, "abort_on_go_no_go_failure") is True,
    )
    passed = data.controlled_abort_policy_safety_verified is not False and _section_ok(section) and all(values)
    return _finding(ControlledAbortPolicySafetyFinding, _metric_score(data.abort_policy_score, _get(section, "score"), passed), passed, Risk.CONTROLLED_ABORT_POLICY_MISSING, "controlled_abort_policy_safety", *values)


def _safety_objects(data: PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateInput) -> tuple[Any, ...]:
    return (
        verify_controlled_execution_scope_safety(data),
        verify_controlled_execution_sequence_safety(data),
        verify_controlled_execution_precondition_safety(data),
        verify_controlled_credentials_reference_safety(data),
        verify_controlled_no_secret_read_safety(data),
        verify_controlled_network_block_safety(data),
        verify_controlled_http_websocket_socket_block_safety(data),
        verify_controlled_account_read_only_safety(data),
        verify_controlled_market_data_read_only_safety(data),
        verify_controlled_order_blocking_safety(data),
        verify_controlled_position_mutation_block_safety(data),
        verify_controlled_observability_safety(data),
        verify_controlled_journal_safety(data),
        verify_controlled_human_approval_safety(data),
        verify_controlled_stop_conditions_safety(data),
        verify_controlled_success_failure_criteria_safety(data),
        verify_controlled_audit_plan_safety(data),
        verify_controlled_go_no_go_policy_safety(data),
        verify_controlled_abort_policy_safety(data),
    )


def compute_controlled_execution_safety_gate_score(data):
    data = _coerce_input(data)
    plan_score = _metric_score(data.controlled_plan_score, _get(_plan(data), "controlled_plan_score"), validate_controlled_execution_plan_approval(data))
    findings = _safety_objects(data)
    scores = (plan_score,) + tuple(int(_get(finding, "score", 0)) for finding in findings)
    return PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateScore(
        _average(scores),
        plan_score,
        findings[0].score,
        findings[1].score,
        findings[2].score,
        findings[3].score,
        findings[4].score,
        findings[5].score,
        findings[6].score,
        findings[7].score,
        findings[8].score,
        findings[9].score,
        findings[10].score,
        findings[11].score,
        findings[12].score,
        findings[13].score,
        findings[14].score,
        findings[15].score,
        findings[16].score,
        findings[17].score,
        findings[18].score,
    )


def detect_controlled_execution_safety_gate_risks(data):
    data = _coerce_input(data)
    risks: list[Risk] = []
    if not validate_controlled_execution_plan_approval(data):
        risks.append(Risk.CONTROLLED_EXECUTION_PLAN_NOT_APPROVED)
    for finding in _safety_objects(data):
        risks.extend(_as_tuple(_get(finding, "risks", ())))
    if not _offline_boundary(data):
        risks.append(Risk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(Risk.DATA_ACCESS_VIOLATION)
    if data.paper_broker_read_only_connection_dry_run_controlled_execution_preparation_requested is True:
        risks.append(Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION)
    return _dedupe(risks)


def generate_controlled_execution_safety_gate_recommendations(data):
    risks = detect_controlled_execution_safety_gate_risks(data)
    if not risks:
        return (
            Recommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE_SUITE,
            Recommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION,
        )
    mapping = {
        Risk.CONTROLLED_EXECUTION_PLAN_NOT_APPROVED: Recommendation.APPROVE_CONTROLLED_EXECUTION_PLAN_FIRST,
        Risk.CONTROLLED_EXECUTION_SCOPE_UNSAFE: Recommendation.HARDEN_CONTROLLED_EXECUTION_SCOPE,
        Risk.CONTROLLED_EXECUTION_SEQUENCE_UNSAFE: Recommendation.HARDEN_CONTROLLED_EXECUTION_SEQUENCE,
        Risk.CONTROLLED_EXECUTION_PRECONDITION_UNSAFE: Recommendation.HARDEN_CONTROLLED_EXECUTION_PRECONDITIONS,
        Risk.CONTROLLED_CREDENTIAL_POLICY_UNSAFE: Recommendation.HARDEN_CONTROLLED_CREDENTIALS,
        Risk.CONTROLLED_SECRET_READ_POLICY_UNSAFE: Recommendation.HARDEN_CONTROLLED_NO_SECRET_READ,
        Risk.CONTROLLED_NETWORK_NOT_BLOCKED: Recommendation.BLOCK_CONTROLLED_NETWORK,
        Risk.CONTROLLED_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED: Recommendation.BLOCK_CONTROLLED_HTTP_WEBSOCKET_SOCKET,
        Risk.CONTROLLED_ACCOUNT_READ_ONLY_UNSAFE: Recommendation.HARDEN_CONTROLLED_ACCOUNT_READ_ONLY,
        Risk.CONTROLLED_MARKET_DATA_READ_ONLY_UNSAFE: Recommendation.HARDEN_CONTROLLED_MARKET_DATA_READ_ONLY,
        Risk.CONTROLLED_ORDER_BLOCKING_UNSAFE: Recommendation.HARDEN_CONTROLLED_ORDER_BLOCKING,
        Risk.CONTROLLED_POSITION_MUTATION_BLOCK_UNSAFE: Recommendation.HARDEN_CONTROLLED_POSITION_MUTATION_BLOCK,
        Risk.CONTROLLED_OBSERVABILITY_INCOMPLETE: Recommendation.COMPLETE_CONTROLLED_OBSERVABILITY,
        Risk.CONTROLLED_JOURNAL_INCOMPLETE: Recommendation.COMPLETE_CONTROLLED_JOURNAL,
        Risk.CONTROLLED_HUMAN_APPROVAL_MISSING: Recommendation.REQUIRE_CONTROLLED_HUMAN_APPROVAL,
        Risk.CONTROLLED_STOP_CONDITIONS_MISSING: Recommendation.DEFINE_CONTROLLED_STOP_CONDITIONS,
        Risk.CONTROLLED_SUCCESS_FAILURE_CRITERIA_UNSAFE: Recommendation.HARDEN_CONTROLLED_SUCCESS_FAILURE_CRITERIA,
        Risk.CONTROLLED_AUDIT_PLAN_MISSING: Recommendation.DEFINE_CONTROLLED_AUDIT_PLAN,
        Risk.CONTROLLED_GO_NO_GO_POLICY_MISSING: Recommendation.DEFINE_CONTROLLED_GO_NO_GO_POLICY,
        Risk.CONTROLLED_ABORT_POLICY_MISSING: Recommendation.DEFINE_CONTROLLED_ABORT_POLICY,
        Risk.REAL_EXECUTION_BOUNDARY_VIOLATION: Recommendation.RESTORE_OFFLINE_BOUNDARIES,
        Risk.DATA_ACCESS_VIOLATION: Recommendation.REMOVE_DATA_ACCESS,
        Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION: Recommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION,
    }
    recommendations = [Recommendation.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION]
    recommendations.extend(mapping[risk] for risk in risks if risk in mapping)
    return _dedupe(recommendations)


def _decision_for_risks(risks):
    if not risks:
        return Decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE
    if any(risk in risks for risk in (Risk.REAL_EXECUTION_BOUNDARY_VIOLATION, Risk.DATA_ACCESS_VIOLATION)):
        return Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE
    ordered = (
        (Risk.CONTROLLED_EXECUTION_PLAN_NOT_APPROVED, Decision.REQUIRE_CONTROLLED_EXECUTION_PLAN_FIXES),
        (Risk.CONTROLLED_EXECUTION_SCOPE_UNSAFE, Decision.REQUIRE_CONTROLLED_SCOPE_SAFETY_FIXES),
        (Risk.CONTROLLED_EXECUTION_SEQUENCE_UNSAFE, Decision.REQUIRE_CONTROLLED_SEQUENCE_SAFETY_FIXES),
        (Risk.CONTROLLED_EXECUTION_PRECONDITION_UNSAFE, Decision.REQUIRE_CONTROLLED_PRECONDITION_SAFETY_FIXES),
        (Risk.CONTROLLED_CREDENTIAL_POLICY_UNSAFE, Decision.REQUIRE_CONTROLLED_CREDENTIAL_SAFETY_FIXES),
        (Risk.CONTROLLED_SECRET_READ_POLICY_UNSAFE, Decision.REQUIRE_CONTROLLED_NO_SECRET_READ_FIXES),
        (Risk.CONTROLLED_NETWORK_NOT_BLOCKED, Decision.REQUIRE_CONTROLLED_NETWORK_BLOCK_FIXES),
        (Risk.CONTROLLED_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED, Decision.REQUIRE_CONTROLLED_NETWORK_BLOCK_FIXES),
        (Risk.CONTROLLED_ACCOUNT_READ_ONLY_UNSAFE, Decision.REQUIRE_CONTROLLED_ACCOUNT_READ_ONLY_FIXES),
        (Risk.CONTROLLED_MARKET_DATA_READ_ONLY_UNSAFE, Decision.REQUIRE_CONTROLLED_MARKET_DATA_READ_ONLY_FIXES),
        (Risk.CONTROLLED_ORDER_BLOCKING_UNSAFE, Decision.REQUIRE_CONTROLLED_ORDER_BLOCKING_FIXES),
        (Risk.CONTROLLED_POSITION_MUTATION_BLOCK_UNSAFE, Decision.REQUIRE_CONTROLLED_POSITION_MUTATION_BLOCK_FIXES),
        (Risk.CONTROLLED_HUMAN_APPROVAL_MISSING, Decision.REQUIRE_CONTROLLED_HUMAN_APPROVAL_FIXES),
        (Risk.CONTROLLED_STOP_CONDITIONS_MISSING, Decision.REQUIRE_CONTROLLED_STOP_CONDITION_FIXES),
        (Risk.CONTROLLED_SUCCESS_FAILURE_CRITERIA_UNSAFE, Decision.REQUIRE_CONTROLLED_STOP_CONDITION_FIXES),
        (Risk.CONTROLLED_AUDIT_PLAN_MISSING, Decision.REQUIRE_CONTROLLED_AUDIT_FIXES),
        (Risk.CONTROLLED_GO_NO_GO_POLICY_MISSING, Decision.REQUIRE_CONTROLLED_GO_NO_GO_FIXES),
        (Risk.CONTROLLED_ABORT_POLICY_MISSING, Decision.REQUIRE_CONTROLLED_ABORT_POLICY_FIXES),
    )
    for risk, decision in ordered:
        if risk in risks:
            return decision
    return Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE


def _state_for_result(data, risks, score):
    state = PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateState
    if data.paper_broker_read_only_connection_dry_run_controlled_execution_plan is None:
        return state.CONTROLLED_EXECUTION_SAFETY_GATE_INPUT_INVALID
    if not risks and score.overall_score >= 85:
        return state.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION
    if risks:
        return state.CONTROLLED_EXECUTION_SAFETY_GATE_BLOCKED
    if score.overall_score >= 70:
        return state.CONTROLLED_EXECUTION_SAFETY_GATE_COMPLETED_WITH_WARNINGS
    return state.NOT_READY


def evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate(data):
    data = _coerce_input(data)
    score = compute_controlled_execution_safety_gate_score(data)
    risks = detect_controlled_execution_safety_gate_risks(data)
    findings = _safety_objects(data)
    return PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateResult(
        state=_state_for_result(data, risks, score),
        decision=_decision_for_risks(risks),
        safety_gate_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        recommendations=generate_controlled_execution_safety_gate_recommendations(data),
        scope_safety=findings[0],
        sequence_safety=findings[1],
        precondition_safety=findings[2],
        credentials_reference_safety=findings[3],
        no_secret_read_safety=findings[4],
        network_block_safety=findings[5],
        http_websocket_socket_block_safety=findings[6],
        account_read_only_safety=findings[7],
        market_data_read_only_safety=findings[8],
        order_blocking_safety=findings[9],
        position_mutation_block_safety=findings[10],
        observability_safety=findings[11],
        journal_safety=findings[12],
        human_approval_safety=findings[13],
        stop_conditions_safety=findings[14],
        success_failure_criteria_safety=findings[15],
        audit_plan_safety=findings[16],
        go_no_go_policy_safety=findings[17],
        abort_policy_safety=findings[18],
        offline_only=True,
        summary=(
            "Paper broker read-only connection dry-run execution controlled execution safety gate is approved for controlled execution planning."
            if not risks
            else "Paper broker read-only connection dry-run execution controlled execution safety gate is blocked until safety risks are fixed."
        ),
    )


def render_paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate_markdown(result):
    if isinstance(result, Mapping):
        result = PaperBrokerReadOnlyConnectionDryRunControlledExecutionSafetyGateResult(**dict(result))
    risks = ", ".join(risk.value for risk in result.risks) or "none"
    recommendations = ", ".join(recommendation.value for recommendation in result.recommendations) or "none"
    return "\n".join(
        (
            "# Paper Broker Read-Only Connection Dry Run Controlled Execution Safety Gate",
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
            "- Go/no-go policy: verified",
        )
    )
