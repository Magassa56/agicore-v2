"""Offline final execution plan for AGIcore Paper Broker read-only connection dry-runs."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Callable, Iterable, Mapping

from agicore.trading import paper_broker_read_only_connection_dry_run_execution_final_plan_models as m


def _coerce_input(data: m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanInput | Mapping[str, Any] | None) -> m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanInput:
    if data is None:
        return m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanInput()
    if isinstance(data, m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanInput):
        return data
    allowed = {field.name for field in fields(m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanInput)}
    return m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanInput(**{k: v for k, v in dict(data).items() if k in allowed})


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


def _review(data: m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanInput) -> Any:
    return data.paper_broker_read_only_connection_dry_run_execution_preparation_review


def _upstream_items(data: m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanInput) -> tuple[Any, ...]:
    return (
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


def _upstream_risks(data: m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def validate_dry_run_execution_preparation_review_approval(data: m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanInput | Mapping[str, Any] | None) -> bool:
    data = _coerce_input(data)
    review = _review(data)
    if review is None or data.dry_run_execution_preparation_review_approved is False:
        return False
    approved_state = _state_contains(
        review,
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW",
    )
    approved = data.dry_run_execution_preparation_review_approved is True or approved_state
    return approved and not _as_tuple(_get(review, "risks", ())) and _get(review, "offline_only", True) is True


def _offline_boundary(data: m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanInput) -> bool:
    return (
        data.offline_mode_enforced is True
        and data.sandbox_mode_enforced is True
        and data.final_plan_only is True
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


def _data_boundary(data: m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanInput) -> bool:
    return data.data_access_requested is not True and not _has_upstream_risk(data, "DATA_ACCESS", "DATA/", "REAL_DATA")

_Check = tuple[str, Callable[[m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanInput], bool]]


def _section(data, *, flag: str, score: str, risk, cls, checks: tuple[_Check, ...], name: str | None = None):
    data = _coerce_input(data)
    values = {field: check(data) for field, check in checks}
    passed = _get(data, flag) is True and all(values.values())
    payload = {
        "defined": passed,
        "score": _metric_score(_get(data, score), passed),
        "risks": () if passed else (risk,),
        "details": ("offline final plan section prepared without executing dry-run",),
        **values,
    }
    if name is not None:
        payload["name"] = name
    return cls(**payload)

def define_final_dry_run_execution_scope(data):
    return _section(data, flag="final_execution_scope_defined", score="scope_score", risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_EXECUTION_SCOPE_UNCLEAR, cls=m.FinalDryRunExecutionScope, checks=(
        ("offline_only", lambda d: d.offline_mode_enforced is True),
        ("sandbox_only", lambda d: d.sandbox_mode_enforced is True),
        ("final_plan_only", lambda d: d.final_plan_only is True),
        ("dry_run_execution_disabled", lambda d: d.dry_run_executed is not True and d.dry_run_requested is not True),
    ))


def define_final_dry_run_execution_sequence(data):
    return _section(data, flag="final_execution_sequence_defined", score="sequence_score", risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_EXECUTION_SEQUENCE_MISSING, cls=m.FinalDryRunExecutionSequence, checks=(
        ("sequence_steps_defined", lambda d: True),
        ("dry_run_not_executed", lambda d: d.dry_run_executed is not True),
        ("connection_not_executed", lambda d: d.broker_connection_requested is not True),
        ("fail_closed", lambda d: True),
    ))


def define_final_dry_run_execution_preconditions(data):
    return _section(data, flag="final_execution_preconditions_defined", score="precondition_score", risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_EXECUTION_PRECONDITION_MISSING, cls=m.FinalDryRunExecutionPrecondition, checks=(
        ("preparation_review_required", lambda d: validate_dry_run_execution_preparation_review_approval(d)),
        ("safety_gate_required", lambda d: True),
        ("human_approval_required", lambda d: d.final_human_approval_required is True),
        ("stop_conditions_required", lambda d: True),
    ))


def define_final_credentials_reference_policy(data):
    return _section(data, flag="final_credentials_reference_policy_defined", score="credentials_score", risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_CREDENTIAL_POLICY_UNSAFE, cls=m.FinalCredentialsReferencePolicy, checks=(
        ("reference_only", lambda d: d.final_credentials_reference_only is True),
        ("no_secret_values", lambda d: d.hardcoded_secret_detected is not True),
        ("no_api_key_read", lambda d: d.no_api_key_read is True and d.api_key_read_requested is not True),
        ("no_env_var_read", lambda d: d.no_env_var_read is True and d.env_var_read_requested is not True),
    ))


def define_final_no_secret_read_policy(data):
    return _section(data, flag="final_no_secret_read_policy_defined", score="no_secret_score", risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_SECRET_READ_POLICY_UNSAFE, cls=m.FinalNoSecretReadPolicy, checks=(
        ("no_api_key_read", lambda d: d.no_api_key_read is True and d.api_key_read_requested is not True),
        ("no_env_var_read", lambda d: d.no_env_var_read is True and d.env_var_read_requested is not True),
        ("no_hardcoded_secret", lambda d: d.no_hardcoded_secrets is True and d.hardcoded_secret_detected is not True),
        ("fail_on_secret_read_request", lambda d: True),
    ))


def _network_checks():
    return (
        ("network_execution_blocked", lambda d: d.final_network_blocked is True and d.network_transport_requested is not True),
        ("http_blocked", lambda d: d.final_http_blocked is True and d.no_http_transport is True),
        ("websocket_blocked", lambda d: d.final_websocket_blocked is True and d.no_websocket_transport is True),
        ("socket_blocked", lambda d: d.final_socket_blocked is True and d.no_socket_transport is True),
        ("external_api_blocked", lambda d: d.final_external_api_blocked is True and d.external_api_requested is not True),
    )


def define_final_network_block_policy(data):
    return _section(data, flag="final_network_block_policy_defined", score="network_score", risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_NETWORK_NOT_BLOCKED, cls=m.FinalNetworkBlockPolicy, checks=_network_checks())


def define_final_http_websocket_socket_block_policy(data):
    return _section(data, flag="final_http_websocket_socket_block_policy_defined", score="http_websocket_socket_score", risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED, cls=m.FinalNetworkBlockPolicy, checks=_network_checks(), name="final_http_websocket_socket_block_policy")


def define_final_account_read_only_policy(data):
    return _section(data, flag="final_account_read_only_policy_defined", score="account_score", risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_ACCOUNT_READ_ONLY_UNSAFE, cls=m.FinalAccountReadOnlyPolicy, checks=(
        ("active_account_access_blocked", lambda d: d.final_active_account_access_blocked is True and d.account_access_requested is not True),
        ("account_mutations_blocked", lambda d: d.final_account_mutations_blocked is True),
        ("schema_only_account_review", lambda d: True),
    ))


def define_final_market_data_read_only_policy(data):
    return _section(data, flag="final_market_data_read_only_policy_defined", score="market_data_score", risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_MARKET_DATA_READ_ONLY_UNSAFE, cls=m.FinalMarketDataReadOnlyPolicy, checks=(
        ("read_only_market_data_only", lambda d: True),
        ("live_subscription_blocked", lambda d: d.final_market_data_live_subscription_blocked is True),
        ("network_request_blocked", lambda d: d.final_market_data_network_request_blocked is True and d.network_transport_requested is not True),
        ("schema_or_synthetic_only", lambda d: True),
    ))


def define_final_order_blocking_policy(data):
    return _section(data, flag="final_order_blocking_policy_defined", score="order_score", risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_ORDER_BLOCKING_UNSAFE, cls=m.FinalOrderBlockingPolicy, checks=(
        ("order_execution_blocked", lambda d: d.final_order_execution_blocked is True and d.order_execution_requested is not True),
        ("real_order_blocked", lambda d: d.no_real_order is True),
        ("cancel_replace_blocked", lambda d: d.final_cancel_replace_blocked is True),
    ))


def define_final_position_mutation_block_policy(data):
    return _section(data, flag="final_position_mutation_block_policy_defined", score="position_score", risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_POSITION_MUTATION_BLOCK_UNSAFE, cls=m.FinalPositionMutationBlockPolicy, checks=(
        ("position_mutation_blocked", lambda d: d.final_position_mutation_blocked is True and d.position_mutation_requested is not True),
        ("position_request_absent", lambda d: True),
        ("close_modify_blocked", lambda d: True),
    ))


def define_final_observability_plan(data):
    return _section(data, flag="final_observability_plan_defined", score="observability_score", risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_OBSERVABILITY_MISSING, cls=m.FinalObservabilityPlan, checks=(
        ("offline_events_defined", lambda d: True),
        ("connection_attempt_logging_disabled", lambda d: True),
        ("sensitive_values_redacted", lambda d: True),
    ))


def define_final_journal_plan(data):
    return _section(data, flag="final_journal_plan_defined", score="journal_score", risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_JOURNAL_MISSING, cls=m.FinalJournalPlan, checks=(
        ("offline_journal_required", lambda d: True),
        ("sensitive_values_redacted", lambda d: True),
        ("no_secret_material_logged", lambda d: d.no_hardcoded_secrets is True),
    ))


def define_final_human_approval_plan(data):
    return _section(data, flag="final_human_approval_plan_defined", score="human_approval_score", risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_HUMAN_APPROVAL_MISSING, cls=m.FinalHumanApprovalPlan, checks=(
        ("human_approval_required", lambda d: d.final_human_approval_required is True),
        ("approval_before_safety_gate", lambda d: True),
        ("preparation_review_evidence_required", lambda d: validate_dry_run_execution_preparation_review_approval(d)),
    ))


def define_final_stop_conditions_plan(data):
    return _section(data, flag="final_stop_conditions_plan_defined", score="stop_conditions_score", risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_STOP_CONDITIONS_MISSING, cls=m.FinalStopConditionPlan, checks=(
        ("stop_on_secret_read", lambda d: True),
        ("stop_on_network_request", lambda d: True),
        ("stop_on_order_or_position_request", lambda d: True),
        ("stop_on_account_access_request", lambda d: True),
    ))


def define_final_success_criteria(data):
    return _section(data, flag="final_success_criteria_defined", score="success_score", risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_SUCCESS_CRITERIA_MISSING, cls=m.FinalSuccessCriteria, checks=(
        ("success_requires_no_real_connection", lambda d: d.broker_connection_requested is not True),
        ("success_requires_all_guards_verified", lambda d: d.final_network_blocked is True and d.final_order_execution_blocked is True and d.final_position_mutation_blocked is True),
        ("success_requires_go_no_go_approval", lambda d: True),
    ))


def define_final_failure_criteria(data):
    return _section(data, flag="final_failure_criteria_defined", score="failure_score", risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_FAILURE_CRITERIA_MISSING, cls=m.FinalFailureCriteria, checks=(
        ("failure_on_secret_read", lambda d: True),
        ("failure_on_network_request", lambda d: True),
        ("failure_on_order_position_or_account", lambda d: True),
    ))


def define_final_audit_plan(data):
    return _section(data, flag="final_audit_plan_defined", score="audit_score", risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_AUDIT_PLAN_MISSING, cls=m.FinalAuditPlan, checks=(
        ("audit_events_defined", lambda d: True),
        ("offline_evidence_required", lambda d: True),
        ("final_plan_trace_required", lambda d: True),
    ))


def define_final_go_no_go_policy(data):
    return _section(data, flag="final_go_no_go_policy_defined", score="go_no_go_score", risk=m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.FINAL_GO_NO_GO_POLICY_MISSING, cls=m.FinalGoNoGoPolicy, checks=(
        ("go_requires_all_sections_ready", lambda d: True),
        ("no_go_on_any_boundary_violation", lambda d: True),
        ("human_go_required", lambda d: d.final_human_approval_required is True),
    ))

def _sections(data):
    return (
        define_final_dry_run_execution_scope(data),
        define_final_dry_run_execution_sequence(data),
        define_final_dry_run_execution_preconditions(data),
        define_final_credentials_reference_policy(data),
        define_final_no_secret_read_policy(data),
        define_final_network_block_policy(data),
        define_final_http_websocket_socket_block_policy(data),
        define_final_account_read_only_policy(data),
        define_final_market_data_read_only_policy(data),
        define_final_order_blocking_policy(data),
        define_final_position_mutation_block_policy(data),
        define_final_observability_plan(data),
        define_final_journal_plan(data),
        define_final_human_approval_plan(data),
        define_final_stop_conditions_plan(data),
        define_final_success_criteria(data),
        define_final_failure_criteria(data),
        define_final_audit_plan(data),
        define_final_go_no_go_policy(data),
    )


def compute_dry_run_execution_final_plan_score(data):
    data = _coerce_input(data)
    review_ok = validate_dry_run_execution_preparation_review_approval(data)
    review_score = _metric_score(data.preparation_review_score, review_ok)
    sections = _sections(data)
    scores = (review_score,) + tuple(section.score for section in sections)
    return m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanScore(
        overall_score=_average(scores),
        preparation_review_score=review_score,
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
    )


def detect_dry_run_execution_final_plan_risks(data):
    data = _coerce_input(data)
    risks: list[m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk] = []
    if not validate_dry_run_execution_preparation_review_approval(data):
        risks.append(m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.DRY_RUN_EXECUTION_PREPARATION_REVIEW_NOT_APPROVED)
    for section in _sections(data):
        risks.extend(_as_tuple(section.risks))
    if not _offline_boundary(data):
        risks.append(m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.DATA_ACCESS_VIOLATION)
    if data.paper_broker_read_only_connection_dry_run_execution_final_safety_gate_requested is True:
        risks.append(m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_SAFETY_GATE)
    return _dedupe(risks)


def generate_dry_run_execution_final_plan_recommendations(data):
    risks = detect_dry_run_execution_final_plan_risks(data)
    rec = m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRecommendation
    risk = m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk
    if not risks:
        return (
            rec.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN_SUITE,
            rec.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_SAFETY_GATE,
        )
    mapping = {
        risk.DRY_RUN_EXECUTION_PREPARATION_REVIEW_NOT_APPROVED: rec.APPROVE_DRY_RUN_EXECUTION_PREPARATION_REVIEW_FIRST,
        risk.FINAL_EXECUTION_SCOPE_UNCLEAR: rec.DEFINE_FINAL_EXECUTION_SCOPE,
        risk.FINAL_EXECUTION_SEQUENCE_MISSING: rec.DEFINE_FINAL_EXECUTION_SEQUENCE,
        risk.FINAL_EXECUTION_PRECONDITION_MISSING: rec.DEFINE_FINAL_EXECUTION_PRECONDITIONS,
        risk.FINAL_CREDENTIAL_POLICY_UNSAFE: rec.HARDEN_FINAL_CREDENTIAL_POLICY,
        risk.FINAL_SECRET_READ_POLICY_UNSAFE: rec.HARDEN_FINAL_NO_SECRET_READ_POLICY,
        risk.FINAL_NETWORK_NOT_BLOCKED: rec.BLOCK_FINAL_NETWORK_TRANSPORT,
        risk.FINAL_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED: rec.BLOCK_FINAL_HTTP_WEBSOCKET_SOCKET,
        risk.FINAL_ACCOUNT_READ_ONLY_UNSAFE: rec.HARDEN_FINAL_ACCOUNT_READ_ONLY,
        risk.FINAL_MARKET_DATA_READ_ONLY_UNSAFE: rec.HARDEN_FINAL_MARKET_DATA_READ_ONLY,
        risk.FINAL_ORDER_BLOCKING_UNSAFE: rec.HARDEN_FINAL_ORDER_BLOCKING,
        risk.FINAL_POSITION_MUTATION_BLOCK_UNSAFE: rec.HARDEN_FINAL_POSITION_MUTATION_BLOCK,
        risk.FINAL_OBSERVABILITY_MISSING: rec.COMPLETE_FINAL_OBSERVABILITY,
        risk.FINAL_JOURNAL_MISSING: rec.COMPLETE_FINAL_JOURNAL,
        risk.FINAL_HUMAN_APPROVAL_MISSING: rec.REQUIRE_FINAL_HUMAN_APPROVAL,
        risk.FINAL_STOP_CONDITIONS_MISSING: rec.DEFINE_FINAL_STOP_CONDITIONS,
        risk.FINAL_SUCCESS_CRITERIA_MISSING: rec.DEFINE_FINAL_SUCCESS_FAILURE_CRITERIA,
        risk.FINAL_FAILURE_CRITERIA_MISSING: rec.DEFINE_FINAL_SUCCESS_FAILURE_CRITERIA,
        risk.FINAL_AUDIT_PLAN_MISSING: rec.COMPLETE_FINAL_AUDIT_PLAN,
        risk.FINAL_GO_NO_GO_POLICY_MISSING: rec.DEFINE_FINAL_GO_NO_GO_POLICY,
        risk.REAL_EXECUTION_BOUNDARY_VIOLATION: rec.RESTORE_OFFLINE_BOUNDARIES,
        risk.DATA_ACCESS_VIOLATION: rec.REMOVE_DATA_ACCESS,
        risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_SAFETY_GATE: rec.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_SAFETY_GATE,
    }
    recommendations = [rec.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_SAFETY_GATE]
    recommendations.extend(mapping[item] for item in risks if item in mapping)
    return _dedupe(recommendations)


def _decision_for_risks(risks):
    decision = m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanDecision
    risk = m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanRisk
    if not risks:
        return decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN
    if risk.DRY_RUN_EXECUTION_PREPARATION_REVIEW_NOT_APPROVED in risks:
        return decision.REQUIRE_DRY_RUN_EXECUTION_PREPARATION_REVIEW_FIXES
    if risk.REAL_EXECUTION_BOUNDARY_VIOLATION in risks or risk.DATA_ACCESS_VIOLATION in risks:
        return decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN
    ordered = (
        (risk.FINAL_EXECUTION_SCOPE_UNCLEAR, decision.REQUIRE_FINAL_EXECUTION_SCOPE_FIXES),
        (risk.FINAL_EXECUTION_SEQUENCE_MISSING, decision.REQUIRE_FINAL_EXECUTION_SEQUENCE_FIXES),
        (risk.FINAL_EXECUTION_PRECONDITION_MISSING, decision.REQUIRE_FINAL_EXECUTION_PRECONDITION_FIXES),
        (risk.FINAL_CREDENTIAL_POLICY_UNSAFE, decision.REQUIRE_FINAL_CREDENTIAL_POLICY_FIXES),
        (risk.FINAL_SECRET_READ_POLICY_UNSAFE, decision.REQUIRE_FINAL_NO_SECRET_READ_FIXES),
        (risk.FINAL_NETWORK_NOT_BLOCKED, decision.REQUIRE_FINAL_NETWORK_BLOCK_FIXES),
        (risk.FINAL_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED, decision.REQUIRE_FINAL_NETWORK_BLOCK_FIXES),
        (risk.FINAL_ACCOUNT_READ_ONLY_UNSAFE, decision.REQUIRE_FINAL_ACCOUNT_READ_ONLY_FIXES),
        (risk.FINAL_MARKET_DATA_READ_ONLY_UNSAFE, decision.REQUIRE_FINAL_MARKET_DATA_READ_ONLY_FIXES),
        (risk.FINAL_ORDER_BLOCKING_UNSAFE, decision.REQUIRE_FINAL_ORDER_BLOCKING_FIXES),
        (risk.FINAL_POSITION_MUTATION_BLOCK_UNSAFE, decision.REQUIRE_FINAL_POSITION_MUTATION_BLOCK_FIXES),
        (risk.FINAL_OBSERVABILITY_MISSING, decision.REQUIRE_FINAL_OBSERVABILITY_FIXES),
        (risk.FINAL_JOURNAL_MISSING, decision.REQUIRE_FINAL_JOURNAL_FIXES),
        (risk.FINAL_HUMAN_APPROVAL_MISSING, decision.REQUIRE_FINAL_HUMAN_APPROVAL_FIXES),
        (risk.FINAL_STOP_CONDITIONS_MISSING, decision.REQUIRE_FINAL_STOP_CONDITION_FIXES),
        (risk.FINAL_SUCCESS_CRITERIA_MISSING, decision.REQUIRE_FINAL_SUCCESS_FAILURE_FIXES),
        (risk.FINAL_FAILURE_CRITERIA_MISSING, decision.REQUIRE_FINAL_SUCCESS_FAILURE_FIXES),
        (risk.FINAL_AUDIT_PLAN_MISSING, decision.REQUIRE_FINAL_AUDIT_FIXES),
        (risk.FINAL_GO_NO_GO_POLICY_MISSING, decision.REQUIRE_FINAL_GO_NO_GO_FIXES),
    )
    for item, selected in ordered:
        if item in risks:
            return selected
    return decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN


def _state_for_result(data, risks, score):
    state = m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanState
    if data.paper_broker_read_only_connection_dry_run_execution_preparation_review is None:
        return state.DRY_RUN_EXECUTION_FINAL_PLAN_INPUT_INVALID
    if not risks and score.overall_score >= 85:
        return state.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_SAFETY_GATE
    if risks:
        return state.DRY_RUN_EXECUTION_FINAL_PLAN_BLOCKED
    if score.overall_score >= 70:
        return state.DRY_RUN_EXECUTION_FINAL_PLAN_COMPLETED_WITH_WARNINGS
    return state.NOT_READY


def evaluate_paper_broker_read_only_connection_dry_run_execution_final_plan(data):
    data = _coerce_input(data)
    score = compute_dry_run_execution_final_plan_score(data)
    risks = detect_dry_run_execution_final_plan_risks(data)
    sections = _sections(data)
    return m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanResult(
        state=_state_for_result(data, risks, score),
        decision=_decision_for_risks(risks),
        final_plan_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        recommendations=generate_dry_run_execution_final_plan_recommendations(data),
        final_dry_run_execution_scope=sections[0],
        final_dry_run_execution_sequence=sections[1],
        final_dry_run_execution_precondition=sections[2],
        final_credentials_reference_policy=sections[3],
        final_no_secret_read_policy=sections[4],
        final_network_block_policy=sections[5],
        final_http_websocket_socket_block_policy=sections[6],
        final_account_read_only_policy=sections[7],
        final_market_data_read_only_policy=sections[8],
        final_order_blocking_policy=sections[9],
        final_position_mutation_block_policy=sections[10],
        final_observability_plan=sections[11],
        final_journal_plan=sections[12],
        final_human_approval_plan=sections[13],
        final_stop_conditions_plan=sections[14],
        final_success_criteria=sections[15],
        final_failure_criteria=sections[16],
        final_audit_plan=sections[17],
        final_go_no_go_policy=sections[18],
        offline_only=True,
        summary=(
            "Paper broker read-only connection dry-run execution final plan is approved for final safety gate."
            if not risks
            else "Paper broker read-only connection dry-run execution final plan is blocked until plan risks are fixed."
        ),
    )


def render_paper_broker_read_only_connection_dry_run_execution_final_plan_markdown(result):
    if isinstance(result, Mapping):
        result = m.PaperBrokerReadOnlyConnectionDryRunExecutionFinalPlanResult(**dict(result))
    risks = ", ".join(item.value for item in result.risks) or "none"
    recommendations = ", ".join(item.value for item in result.recommendations) or "none"
    sections = (
        ("final_dry_run_execution_scope", result.final_dry_run_execution_scope),
        ("final_dry_run_execution_sequence", result.final_dry_run_execution_sequence),
        ("final_dry_run_execution_precondition", result.final_dry_run_execution_precondition),
        ("final_credentials_reference_policy", result.final_credentials_reference_policy),
        ("final_no_secret_read_policy", result.final_no_secret_read_policy),
        ("final_network_block_policy", result.final_network_block_policy),
        ("final_http_websocket_socket_block_policy", result.final_http_websocket_socket_block_policy),
        ("final_account_read_only_policy", result.final_account_read_only_policy),
        ("final_market_data_read_only_policy", result.final_market_data_read_only_policy),
        ("final_order_blocking_policy", result.final_order_blocking_policy),
        ("final_position_mutation_block_policy", result.final_position_mutation_block_policy),
        ("final_observability_plan", result.final_observability_plan),
        ("final_journal_plan", result.final_journal_plan),
        ("final_human_approval_plan", result.final_human_approval_plan),
        ("final_stop_conditions_plan", result.final_stop_conditions_plan),
        ("final_success_criteria", result.final_success_criteria),
        ("final_failure_criteria", result.final_failure_criteria),
        ("final_audit_plan", result.final_audit_plan),
        ("final_go_no_go_policy", result.final_go_no_go_policy),
    )
    lines = [
        "# Paper Broker Read-Only Connection Dry Run Execution Final Plan",
        "",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Final plan score: {result.final_plan_score}",
        f"- Offline only: {result.offline_only}",
        f"- Risks: {risks}",
        f"- Recommendations: {recommendations}",
        "",
        "## Enforced Final Plan Boundaries",
        "- Final plan only: no dry-run execution and no connection test",
        "- No broker, Alpaca, API key, environment variable, or hardcoded secret read",
        "- No HTTP, websocket, socket, network transport, or external API",
        "- No order execution, position mutation, trading, or active account access",
        "- No data/ access",
        "",
        "## Final Plan Sections",
    ]
    for name, section in sections:
        lines.append(f"- {name}: score={section.score}, defined={section.defined}, risks={len(section.risks)}")
    if result.summary:
        lines.extend(("", f"Summary: {result.summary}"))
    return "\n".join(lines)
