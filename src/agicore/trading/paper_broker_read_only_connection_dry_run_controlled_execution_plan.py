"""Offline controlled execution plan for AGIcore Paper Broker read-only connection dry-runs."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Callable, Iterable, Mapping

from agicore.trading import paper_broker_read_only_connection_dry_run_controlled_execution_plan_models as m


def _coerce_input(data: m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanInput | Mapping[str, Any] | None) -> m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanInput:
    if data is None:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanInput()
    if isinstance(data, m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanInput):
        return data
    allowed = {field.name for field in fields(m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanInput)}
    return m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanInput(**{k: v for k, v in dict(data).items() if k in allowed})


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


def _metric_score(explicit: int | None, passed: bool) -> int:
    if explicit is not None:
        return _clamp(explicit)
    return 100 if passed else 0


def _final_safety_gate(data: m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanInput) -> Any:
    return data.paper_broker_read_only_connection_dry_run_execution_final_safety_gate


def _upstream_items(data: m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanInput) -> tuple[Any, ...]:
    return (
        data.paper_broker_read_only_connection_dry_run_execution_final_safety_gate,
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


def _upstream_risks(data: m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def validate_dry_run_execution_final_safety_gate_approval(data: m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanInput | Mapping[str, Any] | None) -> bool:
    data = _coerce_input(data)
    gate = _final_safety_gate(data)
    if gate is None or data.dry_run_execution_final_safety_gate_approved is False:
        return False
    approved_state = _state_contains(
        gate,
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PLAN",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_SAFETY_GATE",
    )
    approved = data.dry_run_execution_final_safety_gate_approved is True or approved_state
    return approved and not _as_tuple(_get(gate, "risks", ())) and _get(gate, "offline_only", True) is True


def _offline_boundary(data: m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanInput) -> bool:
    return (
        data.offline_mode_enforced is True
        and data.sandbox_mode_enforced is True
        and data.controlled_plan_only is True
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


def _data_boundary(data: m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanInput) -> bool:
    return data.data_access_requested is not True and not _has_upstream_risk(data, "DATA_ACCESS", "DATA/", "REAL_DATA")

_Check = tuple[str, Callable[[m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanInput], bool]]


def _section(data, *, flag: str, score: str, risk, cls, checks: tuple[_Check, ...], name: str | None = None):
    data = _coerce_input(data)
    values = {field: check(data) for field, check in checks}
    passed = _get(data, flag) is True and all(values.values())
    payload = {
        "defined": passed,
        "score": _metric_score(_get(data, score), passed),
        "risks": () if passed else (risk,),
        "details": ("offline controlled execution plan section prepared without executing dry-run",),
        **values,
    }
    if name is not None:
        payload["name"] = name
    return cls(**payload)

def define_controlled_execution_scope(data):
    return _section(data, flag="controlled_execution_scope_defined", score="scope_score", risk=m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_EXECUTION_SCOPE_UNCLEAR, cls=m.ControlledExecutionScope, checks=(
        ("offline_only", lambda d: d.offline_mode_enforced is True),
        ("sandbox_only", lambda d: d.sandbox_mode_enforced is True),
        ("controlled_plan_only", lambda d: d.controlled_plan_only is True),
        ("dry_run_execution_disabled", lambda d: d.dry_run_executed is not True and d.dry_run_requested is not True),
    ))


def define_controlled_execution_sequence(data):
    return _section(data, flag="controlled_execution_sequence_defined", score="sequence_score", risk=m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_EXECUTION_SEQUENCE_MISSING, cls=m.ControlledExecutionSequence, checks=(
        ("sequence_steps_defined", lambda d: True),
        ("dry_run_not_executed", lambda d: d.dry_run_executed is not True),
        ("connection_not_executed", lambda d: d.broker_connection_requested is not True),
        ("fail_closed", lambda d: True),
    ))


def define_controlled_execution_preconditions(data):
    return _section(data, flag="controlled_execution_preconditions_defined", score="precondition_score", risk=m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_EXECUTION_PRECONDITION_MISSING, cls=m.ControlledExecutionPrecondition, checks=(
        ("final_safety_gate_required", lambda d: validate_dry_run_execution_final_safety_gate_approval(d)),
        ("safety_gate_required", lambda d: True),
        ("human_approval_required", lambda d: d.controlled_human_approval_required is True),
        ("stop_conditions_required", lambda d: True),
    ))


def define_controlled_credentials_reference_policy(data):
    return _section(data, flag="controlled_credentials_reference_policy_defined", score="credentials_score", risk=m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_CREDENTIAL_POLICY_UNSAFE, cls=m.ControlledCredentialsReferencePolicy, checks=(
        ("reference_only", lambda d: d.controlled_credentials_reference_only is True),
        ("no_secret_values", lambda d: d.hardcoded_secret_detected is not True),
        ("no_api_key_read", lambda d: d.no_api_key_read is True and d.api_key_read_requested is not True),
        ("no_env_var_read", lambda d: d.no_env_var_read is True and d.env_var_read_requested is not True),
    ))


def define_controlled_no_secret_read_policy(data):
    return _section(data, flag="controlled_no_secret_read_policy_defined", score="no_secret_score", risk=m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_SECRET_READ_POLICY_UNSAFE, cls=m.ControlledNoSecretReadPolicy, checks=(
        ("no_api_key_read", lambda d: d.no_api_key_read is True and d.api_key_read_requested is not True),
        ("no_env_var_read", lambda d: d.no_env_var_read is True and d.env_var_read_requested is not True),
        ("no_hardcoded_secret", lambda d: d.no_hardcoded_secrets is True and d.hardcoded_secret_detected is not True),
        ("fail_on_secret_read_request", lambda d: True),
    ))


def _network_checks():
    return (
        ("network_execution_blocked", lambda d: d.controlled_network_blocked is True and d.network_transport_requested is not True),
        ("http_blocked", lambda d: d.controlled_http_blocked is True and d.no_http_transport is True),
        ("websocket_blocked", lambda d: d.controlled_websocket_blocked is True and d.no_websocket_transport is True),
        ("socket_blocked", lambda d: d.controlled_socket_blocked is True and d.no_socket_transport is True),
        ("external_api_blocked", lambda d: d.controlled_external_api_blocked is True and d.external_api_requested is not True),
    )


def define_controlled_network_block_policy(data):
    return _section(data, flag="controlled_network_block_policy_defined", score="network_score", risk=m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_NETWORK_NOT_BLOCKED, cls=m.ControlledNetworkBlockPolicy, checks=_network_checks())


def define_controlled_http_websocket_socket_block_policy(data):
    return _section(data, flag="controlled_http_websocket_socket_block_policy_defined", score="http_websocket_socket_score", risk=m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED, cls=m.ControlledNetworkBlockPolicy, checks=_network_checks(), name="controlled_http_websocket_socket_block_policy")


def define_controlled_account_read_only_policy(data):
    return _section(data, flag="controlled_account_read_only_policy_defined", score="account_score", risk=m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_ACCOUNT_READ_ONLY_UNSAFE, cls=m.ControlledAccountReadOnlyPolicy, checks=(
        ("active_account_access_blocked", lambda d: d.controlled_active_account_access_blocked is True and d.account_access_requested is not True),
        ("account_mutations_blocked", lambda d: d.controlled_account_mutations_blocked is True),
        ("schema_only_account_review", lambda d: True),
    ))


def define_controlled_market_data_read_only_policy(data):
    return _section(data, flag="controlled_market_data_read_only_policy_defined", score="market_data_score", risk=m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_MARKET_DATA_READ_ONLY_UNSAFE, cls=m.ControlledMarketDataReadOnlyPolicy, checks=(
        ("read_only_market_data_only", lambda d: True),
        ("live_subscription_blocked", lambda d: d.controlled_market_data_live_subscription_blocked is True),
        ("network_request_blocked", lambda d: d.controlled_market_data_network_request_blocked is True and d.network_transport_requested is not True),
        ("schema_or_synthetic_only", lambda d: True),
    ))


def define_controlled_order_blocking_policy(data):
    return _section(data, flag="controlled_order_blocking_policy_defined", score="order_score", risk=m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_ORDER_BLOCKING_UNSAFE, cls=m.ControlledOrderBlockingPolicy, checks=(
        ("order_execution_blocked", lambda d: d.controlled_order_execution_blocked is True and d.order_execution_requested is not True),
        ("real_order_blocked", lambda d: d.no_real_order is True),
        ("cancel_replace_blocked", lambda d: d.controlled_cancel_replace_blocked is True),
    ))


def define_controlled_position_mutation_block_policy(data):
    return _section(data, flag="controlled_position_mutation_block_policy_defined", score="position_score", risk=m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_POSITION_MUTATION_BLOCK_UNSAFE, cls=m.ControlledPositionMutationBlockPolicy, checks=(
        ("position_mutation_blocked", lambda d: d.controlled_position_mutation_blocked is True and d.position_mutation_requested is not True),
        ("position_request_absent", lambda d: True),
        ("close_modify_blocked", lambda d: True),
    ))


def define_controlled_observability_plan(data):
    return _section(data, flag="controlled_observability_plan_defined", score="observability_score", risk=m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_OBSERVABILITY_MISSING, cls=m.ControlledObservabilityPlan, checks=(
        ("offline_events_defined", lambda d: True),
        ("connection_attempt_logging_disabled", lambda d: True),
        ("sensitive_values_redacted", lambda d: True),
    ))


def define_controlled_journal_plan(data):
    return _section(data, flag="controlled_journal_plan_defined", score="journal_score", risk=m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_JOURNAL_MISSING, cls=m.ControlledJournalPlan, checks=(
        ("offline_journal_required", lambda d: True),
        ("sensitive_values_redacted", lambda d: True),
        ("no_secret_material_logged", lambda d: d.no_hardcoded_secrets is True),
    ))


def define_controlled_human_approval_plan(data):
    return _section(data, flag="controlled_human_approval_plan_defined", score="human_approval_score", risk=m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_HUMAN_APPROVAL_MISSING, cls=m.ControlledHumanApprovalPlan, checks=(
        ("human_approval_required", lambda d: d.controlled_human_approval_required is True),
        ("approval_before_safety_gate", lambda d: True),
        ("final_safety_gate_evidence_required", lambda d: validate_dry_run_execution_final_safety_gate_approval(d)),
    ))


def define_controlled_stop_conditions_plan(data):
    return _section(data, flag="controlled_stop_conditions_plan_defined", score="stop_conditions_score", risk=m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_STOP_CONDITIONS_MISSING, cls=m.ControlledStopConditionPlan, checks=(
        ("stop_on_secret_read", lambda d: True),
        ("stop_on_network_request", lambda d: True),
        ("stop_on_order_or_position_request", lambda d: True),
        ("stop_on_account_access_request", lambda d: True),
    ))


def define_controlled_success_criteria(data):
    return _section(data, flag="controlled_success_criteria_defined", score="success_score", risk=m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_SUCCESS_CRITERIA_MISSING, cls=m.ControlledSuccessCriteria, checks=(
        ("success_requires_no_real_connection", lambda d: d.broker_connection_requested is not True),
        ("success_requires_all_guards_verified", lambda d: d.controlled_network_blocked is True and d.controlled_order_execution_blocked is True and d.controlled_position_mutation_blocked is True),
        ("success_requires_go_no_go_approval", lambda d: True),
    ))


def define_controlled_failure_criteria(data):
    return _section(data, flag="controlled_failure_criteria_defined", score="failure_score", risk=m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_FAILURE_CRITERIA_MISSING, cls=m.ControlledFailureCriteria, checks=(
        ("failure_on_secret_read", lambda d: True),
        ("failure_on_network_request", lambda d: True),
        ("failure_on_order_position_or_account", lambda d: True),
    ))


def define_controlled_audit_plan(data):
    return _section(data, flag="controlled_audit_plan_defined", score="audit_score", risk=m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_AUDIT_PLAN_MISSING, cls=m.ControlledAuditPlan, checks=(
        ("audit_events_defined", lambda d: True),
        ("offline_evidence_required", lambda d: True),
        ("controlled_plan_trace_required", lambda d: True),
    ))


def define_controlled_go_no_go_policy(data):
    return _section(data, flag="controlled_go_no_go_policy_defined", score="go_no_go_score", risk=m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_GO_NO_GO_POLICY_MISSING, cls=m.ControlledGoNoGoPolicy, checks=(
        ("go_requires_all_sections_ready", lambda d: True),
        ("no_go_on_any_boundary_violation", lambda d: True),
        ("human_go_required", lambda d: d.controlled_human_approval_required is True),
    ))


def define_controlled_abort_policy(data):
    return _section(data, flag="controlled_abort_policy_defined", score="abort_score", risk=m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.CONTROLLED_ABORT_POLICY_MISSING, cls=m.ControlledAbortPolicy, checks=(
        ("abort_on_secret_read", lambda d: True),
        ("abort_on_network_request", lambda d: True),
        ("abort_on_order_position_or_account", lambda d: True),
        ("abort_on_go_no_go_failure", lambda d: True),
    ))

def _sections(data):
    return (
        define_controlled_execution_scope(data),
        define_controlled_execution_sequence(data),
        define_controlled_execution_preconditions(data),
        define_controlled_credentials_reference_policy(data),
        define_controlled_no_secret_read_policy(data),
        define_controlled_network_block_policy(data),
        define_controlled_http_websocket_socket_block_policy(data),
        define_controlled_account_read_only_policy(data),
        define_controlled_market_data_read_only_policy(data),
        define_controlled_order_blocking_policy(data),
        define_controlled_position_mutation_block_policy(data),
        define_controlled_observability_plan(data),
        define_controlled_journal_plan(data),
        define_controlled_human_approval_plan(data),
        define_controlled_stop_conditions_plan(data),
        define_controlled_success_criteria(data),
        define_controlled_failure_criteria(data),
        define_controlled_audit_plan(data),
        define_controlled_go_no_go_policy(data),
        define_controlled_abort_policy(data),
    )


def compute_controlled_execution_plan_score(data):
    data = _coerce_input(data)
    gate_ok = validate_dry_run_execution_final_safety_gate_approval(data)
    gate_score = _metric_score(data.final_safety_gate_score, gate_ok)
    sections = _sections(data)
    scores = (gate_score,) + tuple(section.score for section in sections)
    return m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanScore(
        overall_score=_average(scores),
        final_safety_gate_score=gate_score,
        scope_score=sections[0].score,
        sequence_score=sections[1].score,
        precondition_score=sections[2].score,
        credentials_score=sections[3].score,
        no_secret_score=sections[4].score,
        network_score=sections[5].score,
        http_websocket_socket_score=sections[6].score,
        account_score=sections[7].score,
        market_data_score=sections[8].score,
        order_score=sections[9].score,
        position_score=sections[10].score,
        observability_score=sections[11].score,
        journal_score=sections[12].score,
        human_approval_score=sections[13].score,
        stop_conditions_score=sections[14].score,
        success_score=sections[15].score,
        failure_score=sections[16].score,
        audit_score=sections[17].score,
        go_no_go_score=sections[18].score,
        abort_score=sections[19].score,
    )


def detect_controlled_execution_plan_risks(data):
    data = _coerce_input(data)
    risks: list[m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk] = []
    if not validate_dry_run_execution_final_safety_gate_approval(data):
        risks.append(m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.DRY_RUN_EXECUTION_FINAL_SAFETY_GATE_NOT_APPROVED)
    for section in _sections(data):
        risks.extend(_as_tuple(section.risks))
    if not _offline_boundary(data):
        risks.append(m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.DATA_ACCESS_VIOLATION)
    if data.paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate_requested is True:
        risks.append(m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE)
    return _dedupe(risks)


def generate_controlled_execution_plan_recommendations(data):
    risks = detect_controlled_execution_plan_risks(data)
    rec = m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRecommendation
    risk = m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk
    if not risks:
        return (
            rec.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PLAN_SUITE,
            rec.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE,
        )
    mapping = {
        risk.DRY_RUN_EXECUTION_FINAL_SAFETY_GATE_NOT_APPROVED: rec.APPROVE_DRY_RUN_EXECUTION_FINAL_SAFETY_GATE_FIRST,
        risk.CONTROLLED_EXECUTION_SCOPE_UNCLEAR: rec.DEFINE_CONTROLLED_EXECUTION_SCOPE,
        risk.CONTROLLED_EXECUTION_SEQUENCE_MISSING: rec.DEFINE_CONTROLLED_EXECUTION_SEQUENCE,
        risk.CONTROLLED_EXECUTION_PRECONDITION_MISSING: rec.DEFINE_CONTROLLED_EXECUTION_PRECONDITIONS,
        risk.CONTROLLED_CREDENTIAL_POLICY_UNSAFE: rec.HARDEN_CONTROLLED_CREDENTIAL_POLICY,
        risk.CONTROLLED_SECRET_READ_POLICY_UNSAFE: rec.HARDEN_CONTROLLED_NO_SECRET_READ_POLICY,
        risk.CONTROLLED_NETWORK_NOT_BLOCKED: rec.BLOCK_CONTROLLED_NETWORK_TRANSPORT,
        risk.CONTROLLED_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED: rec.BLOCK_CONTROLLED_HTTP_WEBSOCKET_SOCKET,
        risk.CONTROLLED_ACCOUNT_READ_ONLY_UNSAFE: rec.HARDEN_CONTROLLED_ACCOUNT_READ_ONLY,
        risk.CONTROLLED_MARKET_DATA_READ_ONLY_UNSAFE: rec.HARDEN_CONTROLLED_MARKET_DATA_READ_ONLY,
        risk.CONTROLLED_ORDER_BLOCKING_UNSAFE: rec.HARDEN_CONTROLLED_ORDER_BLOCKING,
        risk.CONTROLLED_POSITION_MUTATION_BLOCK_UNSAFE: rec.HARDEN_CONTROLLED_POSITION_MUTATION_BLOCK,
        risk.CONTROLLED_OBSERVABILITY_MISSING: rec.COMPLETE_CONTROLLED_OBSERVABILITY,
        risk.CONTROLLED_JOURNAL_MISSING: rec.COMPLETE_CONTROLLED_JOURNAL,
        risk.CONTROLLED_HUMAN_APPROVAL_MISSING: rec.REQUIRE_CONTROLLED_HUMAN_APPROVAL,
        risk.CONTROLLED_STOP_CONDITIONS_MISSING: rec.DEFINE_CONTROLLED_STOP_CONDITIONS,
        risk.CONTROLLED_SUCCESS_CRITERIA_MISSING: rec.DEFINE_CONTROLLED_SUCCESS_FAILURE_CRITERIA,
        risk.CONTROLLED_FAILURE_CRITERIA_MISSING: rec.DEFINE_CONTROLLED_SUCCESS_FAILURE_CRITERIA,
        risk.CONTROLLED_AUDIT_PLAN_MISSING: rec.COMPLETE_CONTROLLED_AUDIT_PLAN,
        risk.CONTROLLED_GO_NO_GO_POLICY_MISSING: rec.DEFINE_CONTROLLED_GO_NO_GO_POLICY,
        risk.CONTROLLED_ABORT_POLICY_MISSING: rec.DEFINE_CONTROLLED_ABORT_POLICY,
        risk.REAL_EXECUTION_BOUNDARY_VIOLATION: rec.RESTORE_OFFLINE_BOUNDARIES,
        risk.DATA_ACCESS_VIOLATION: rec.REMOVE_DATA_ACCESS,
        risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE: rec.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE,
    }
    recommendations = [rec.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE]
    recommendations.extend(mapping[item] for item in risks if item in mapping)
    return _dedupe(recommendations)


def _decision_for_risks(risks):
    decision = m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanDecision
    risk = m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanRisk
    if not risks:
        return decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PLAN
    if risk.DRY_RUN_EXECUTION_FINAL_SAFETY_GATE_NOT_APPROVED in risks:
        return decision.REQUIRE_FINAL_SAFETY_GATE_FIXES
    if risk.REAL_EXECUTION_BOUNDARY_VIOLATION in risks or risk.DATA_ACCESS_VIOLATION in risks:
        return decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PLAN
    ordered = (
        (risk.CONTROLLED_EXECUTION_SCOPE_UNCLEAR, decision.REQUIRE_CONTROLLED_SCOPE_FIXES),
        (risk.CONTROLLED_EXECUTION_SEQUENCE_MISSING, decision.REQUIRE_CONTROLLED_SEQUENCE_FIXES),
        (risk.CONTROLLED_EXECUTION_PRECONDITION_MISSING, decision.REQUIRE_CONTROLLED_PRECONDITION_FIXES),
        (risk.CONTROLLED_CREDENTIAL_POLICY_UNSAFE, decision.REQUIRE_CONTROLLED_CREDENTIAL_POLICY_FIXES),
        (risk.CONTROLLED_SECRET_READ_POLICY_UNSAFE, decision.REQUIRE_CONTROLLED_NO_SECRET_READ_FIXES),
        (risk.CONTROLLED_NETWORK_NOT_BLOCKED, decision.REQUIRE_CONTROLLED_NETWORK_BLOCK_FIXES),
        (risk.CONTROLLED_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED, decision.REQUIRE_CONTROLLED_NETWORK_BLOCK_FIXES),
        (risk.CONTROLLED_ACCOUNT_READ_ONLY_UNSAFE, decision.REQUIRE_CONTROLLED_ACCOUNT_READ_ONLY_FIXES),
        (risk.CONTROLLED_MARKET_DATA_READ_ONLY_UNSAFE, decision.REQUIRE_CONTROLLED_MARKET_DATA_READ_ONLY_FIXES),
        (risk.CONTROLLED_ORDER_BLOCKING_UNSAFE, decision.REQUIRE_CONTROLLED_ORDER_BLOCKING_FIXES),
        (risk.CONTROLLED_POSITION_MUTATION_BLOCK_UNSAFE, decision.REQUIRE_CONTROLLED_POSITION_MUTATION_BLOCK_FIXES),
        (risk.CONTROLLED_OBSERVABILITY_MISSING, decision.REQUIRE_CONTROLLED_OBSERVABILITY_FIXES),
        (risk.CONTROLLED_JOURNAL_MISSING, decision.REQUIRE_CONTROLLED_JOURNAL_FIXES),
        (risk.CONTROLLED_HUMAN_APPROVAL_MISSING, decision.REQUIRE_CONTROLLED_HUMAN_APPROVAL_FIXES),
        (risk.CONTROLLED_STOP_CONDITIONS_MISSING, decision.REQUIRE_CONTROLLED_STOP_CONDITION_FIXES),
        (risk.CONTROLLED_SUCCESS_CRITERIA_MISSING, decision.REQUIRE_CONTROLLED_SUCCESS_FAILURE_FIXES),
        (risk.CONTROLLED_FAILURE_CRITERIA_MISSING, decision.REQUIRE_CONTROLLED_SUCCESS_FAILURE_FIXES),
        (risk.CONTROLLED_AUDIT_PLAN_MISSING, decision.REQUIRE_CONTROLLED_AUDIT_FIXES),
        (risk.CONTROLLED_GO_NO_GO_POLICY_MISSING, decision.REQUIRE_CONTROLLED_GO_NO_GO_FIXES),
        (risk.CONTROLLED_ABORT_POLICY_MISSING, decision.REQUIRE_CONTROLLED_ABORT_POLICY_FIXES),
    )
    for item, selected in ordered:
        if item in risks:
            return selected
    return decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PLAN


def _state_for_result(data, risks, score):
    state = m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanState
    if data.paper_broker_read_only_connection_dry_run_execution_final_safety_gate is None:
        return state.CONTROLLED_EXECUTION_PLAN_INPUT_INVALID
    if not risks and score.overall_score >= 85:
        return state.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_SAFETY_GATE
    if risks:
        return state.CONTROLLED_EXECUTION_PLAN_BLOCKED
    if score.overall_score >= 70:
        return state.CONTROLLED_EXECUTION_PLAN_COMPLETED_WITH_WARNINGS
    return state.NOT_READY


def evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_plan(data):
    data = _coerce_input(data)
    score = compute_controlled_execution_plan_score(data)
    risks = detect_controlled_execution_plan_risks(data)
    sections = _sections(data)
    return m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanResult(
        state=_state_for_result(data, risks, score),
        decision=_decision_for_risks(risks),
        controlled_plan_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        recommendations=generate_controlled_execution_plan_recommendations(data),
        controlled_dry_run_execution_scope=sections[0],
        controlled_dry_run_execution_sequence=sections[1],
        controlled_dry_run_execution_precondition=sections[2],
        controlled_credentials_reference_policy=sections[3],
        controlled_no_secret_read_policy=sections[4],
        controlled_network_block_policy=sections[5],
        controlled_http_websocket_socket_block_policy=sections[6],
        controlled_account_read_only_policy=sections[7],
        controlled_market_data_read_only_policy=sections[8],
        controlled_order_blocking_policy=sections[9],
        controlled_position_mutation_block_policy=sections[10],
        controlled_observability_plan=sections[11],
        controlled_journal_plan=sections[12],
        controlled_human_approval_plan=sections[13],
        controlled_stop_conditions_plan=sections[14],
        controlled_success_criteria=sections[15],
        controlled_failure_criteria=sections[16],
        controlled_audit_plan=sections[17],
        controlled_go_no_go_policy=sections[18],
        controlled_abort_policy=sections[19],
        offline_only=True,
        summary=(
            "Paper broker read-only connection dry-run controlled execution plan is approved for controlled execution safety gate."
            if not risks
            else "Paper broker read-only connection dry-run controlled execution plan is blocked until plan risks are fixed."
        ),
    )


def render_paper_broker_read_only_connection_dry_run_controlled_execution_plan_markdown(result):
    if isinstance(result, Mapping):
        result = m.PaperBrokerReadOnlyConnectionDryRunControlledExecutionPlanResult(**dict(result))
    risks = ", ".join(item.value for item in result.risks) or "none"
    recommendations = ", ".join(item.value for item in result.recommendations) or "none"
    sections = (
        ("controlled_dry_run_execution_scope", result.controlled_dry_run_execution_scope),
        ("controlled_dry_run_execution_sequence", result.controlled_dry_run_execution_sequence),
        ("controlled_dry_run_execution_precondition", result.controlled_dry_run_execution_precondition),
        ("controlled_credentials_reference_policy", result.controlled_credentials_reference_policy),
        ("controlled_no_secret_read_policy", result.controlled_no_secret_read_policy),
        ("controlled_network_block_policy", result.controlled_network_block_policy),
        ("controlled_http_websocket_socket_block_policy", result.controlled_http_websocket_socket_block_policy),
        ("controlled_account_read_only_policy", result.controlled_account_read_only_policy),
        ("controlled_market_data_read_only_policy", result.controlled_market_data_read_only_policy),
        ("controlled_order_blocking_policy", result.controlled_order_blocking_policy),
        ("controlled_position_mutation_block_policy", result.controlled_position_mutation_block_policy),
        ("controlled_observability_plan", result.controlled_observability_plan),
        ("controlled_journal_plan", result.controlled_journal_plan),
        ("controlled_human_approval_plan", result.controlled_human_approval_plan),
        ("controlled_stop_conditions_plan", result.controlled_stop_conditions_plan),
        ("controlled_success_criteria", result.controlled_success_criteria),
        ("controlled_failure_criteria", result.controlled_failure_criteria),
        ("controlled_audit_plan", result.controlled_audit_plan),
        ("controlled_go_no_go_policy", result.controlled_go_no_go_policy),
        ("controlled_abort_policy", result.controlled_abort_policy),
    )
    lines = [
        "# Paper Broker Read-Only Connection Dry Run Controlled Execution Plan",
        "",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Controlled execution plan score: {result.controlled_plan_score}",
        f"- Offline only: {result.offline_only}",
        f"- Risks: {risks}",
        f"- Recommendations: {recommendations}",
        "",
        "## Enforced Controlled Execution Plan Boundaries",
        "- Controlled execution plan only: no dry-run execution and no connection test",
        "- No broker, Alpaca, API key, environment variable, or hardcoded secret read",
        "- No HTTP, websocket, socket, network transport, or external API",
        "- No order execution, position mutation, trading, or active account access",
        "- No data/ access",
        "",
        "## Controlled Execution Plan Sections",
    ]
    for name, section in sections:
        lines.append(f"- {name}: score={section.score}, defined={section.defined}, risks={len(section.risks)}")
    if result.summary:
        lines.extend(("", f"Summary: {result.summary}"))
    return "\n".join(lines)
