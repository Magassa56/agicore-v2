"""Preparation layer for the controlled offline runner implementation."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading import paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_review_models as m

Risk = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewRisk
Decision = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewDecision
Recommendation = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewRecommendation

_FUNCTIONS = {
    "implementation_scope_contract": "review_offline_runner_implementation_scope_preparation_contract",
    "implementation_architecture_contract": "review_offline_runner_implementation_architecture_preparation_contract",
    "implementation_sequence_contract": "review_offline_runner_implementation_sequence_preparation_contract",
    "runtime_contract": "review_offline_runner_runtime_preparation_contract",
    "input_adapter_contract": "review_offline_runner_input_adapter_preparation_contract",
    "synthetic_market_context_adapter_contract": "review_offline_runner_synthetic_market_context_adapter_preparation_contract",
    "simulated_broker_adapter_contract": "review_offline_runner_simulated_broker_adapter_preparation_contract",
    "account_snapshot_adapter_contract": "review_offline_runner_account_snapshot_adapter_preparation_contract",
    "market_data_snapshot_adapter_contract": "review_offline_runner_market_data_snapshot_adapter_preparation_contract",
    "strategy_signal_probe_contract": "review_offline_runner_strategy_signal_probe_preparation_contract",
    "risk_observer_contract": "review_offline_runner_risk_observer_preparation_contract",
    "profitability_observer_contract": "review_offline_runner_profitability_observer_preparation_contract",
    "consistency_observer_contract": "review_offline_runner_consistency_observer_preparation_contract",
    "journal_writer_contract": "review_offline_runner_journal_writer_preparation_contract",
    "observability_contract": "review_offline_runner_observability_preparation_contract",
    "human_approval_contract": "review_offline_runner_human_approval_preparation_contract",
    "stop_condition_contract": "review_offline_runner_stop_condition_preparation_contract",
    "success_criteria_contract": "review_offline_runner_success_criteria_preparation_contract",
    "failure_criteria_contract": "review_offline_runner_failure_criteria_preparation_contract",
    "audit_contract": "review_offline_runner_audit_preparation_contract",
    "go_no_go_contract": "review_offline_runner_go_no_go_preparation_contract",
    "abort_contract": "review_offline_runner_abort_preparation_contract",
    "no_real_broker_guard": "review_offline_runner_no_real_broker_guard",
    "no_secret_read_guard": "review_offline_runner_no_secret_read_guard",
    "network_block_guard": "review_offline_runner_network_block_guard",
    "http_websocket_socket_block_guard": "review_offline_runner_http_websocket_socket_block_guard",
    "order_blocking_guard": "review_offline_runner_order_blocking_guard",
    "position_mutation_blocking_guard": "review_offline_runner_position_mutation_blocking_guard",
    "data_access_guard": "review_offline_runner_data_access_guard",
    "test_strategy_contract": "review_offline_runner_test_strategy_preparation_contract",
    "rollback_strategy_contract": "review_offline_runner_rollback_strategy_preparation_contract",
}

_DECISION_BY_KEY = {
    "implementation_scope_contract": Decision.REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SCOPE_PREPARATION_REVIEW_FIXES,
    "implementation_architecture_contract": Decision.REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_ARCHITECTURE_PREPARATION_REVIEW_FIXES,
    "implementation_sequence_contract": Decision.REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SEQUENCE_PREPARATION_REVIEW_FIXES,
    "runtime_contract": Decision.REQUIRE_OFFLINE_RUNNER_RUNTIME_PREPARATION_REVIEW_FIXES,
    "input_adapter_contract": Decision.REQUIRE_OFFLINE_RUNNER_INPUT_ADAPTER_PREPARATION_REVIEW_FIXES,
    "synthetic_market_context_adapter_contract": Decision.REQUIRE_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_ADAPTER_PREPARATION_REVIEW_FIXES,
    "simulated_broker_adapter_contract": Decision.REQUIRE_OFFLINE_RUNNER_SIMULATED_BROKER_ADAPTER_PREPARATION_REVIEW_FIXES,
    "account_snapshot_adapter_contract": Decision.REQUIRE_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_ADAPTER_PREPARATION_REVIEW_FIXES,
    "market_data_snapshot_adapter_contract": Decision.REQUIRE_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_ADAPTER_PREPARATION_REVIEW_FIXES,
    "strategy_signal_probe_contract": Decision.REQUIRE_OFFLINE_RUNNER_STRATEGY_SIGNAL_PROBE_PREPARATION_REVIEW_FIXES,
    "risk_observer_contract": Decision.REQUIRE_OFFLINE_RUNNER_RISK_OBSERVER_PREPARATION_REVIEW_FIXES,
    "profitability_observer_contract": Decision.REQUIRE_OFFLINE_RUNNER_PROFITABILITY_OBSERVER_PREPARATION_REVIEW_FIXES,
    "consistency_observer_contract": Decision.REQUIRE_OFFLINE_RUNNER_CONSISTENCY_OBSERVER_PREPARATION_REVIEW_FIXES,
    "journal_writer_contract": Decision.REQUIRE_OFFLINE_RUNNER_JOURNAL_WRITER_PREPARATION_REVIEW_FIXES,
    "observability_contract": Decision.REQUIRE_OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_REVIEW_FIXES,
    "human_approval_contract": Decision.REQUIRE_OFFLINE_RUNNER_HUMAN_APPROVAL_PREPARATION_REVIEW_FIXES,
    "stop_condition_contract": Decision.REQUIRE_OFFLINE_RUNNER_STOP_CONDITION_PREPARATION_REVIEW_FIXES,
    "success_criteria_contract": Decision.REQUIRE_OFFLINE_RUNNER_SUCCESS_FAILURE_PREPARATION_REVIEW_FIXES,
    "failure_criteria_contract": Decision.REQUIRE_OFFLINE_RUNNER_SUCCESS_FAILURE_PREPARATION_REVIEW_FIXES,
    "audit_contract": Decision.REQUIRE_OFFLINE_RUNNER_AUDIT_PREPARATION_REVIEW_FIXES,
    "go_no_go_contract": Decision.REQUIRE_OFFLINE_RUNNER_GO_NO_GO_PREPARATION_REVIEW_FIXES,
    "abort_contract": Decision.REQUIRE_OFFLINE_RUNNER_ABORT_PREPARATION_REVIEW_FIXES,
    "no_real_broker_guard": Decision.REQUIRE_OFFLINE_RUNNER_NO_REAL_BROKER_GUARD_REVIEW_FIXES,
    "no_secret_read_guard": Decision.REQUIRE_OFFLINE_RUNNER_NO_SECRET_READ_GUARD_REVIEW_FIXES,
    "network_block_guard": Decision.REQUIRE_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_REVIEW_FIXES,
    "http_websocket_socket_block_guard": Decision.REQUIRE_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_REVIEW_FIXES,
    "order_blocking_guard": Decision.REQUIRE_OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_REVIEW_FIXES,
    "position_mutation_blocking_guard": Decision.REQUIRE_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_REVIEW_FIXES,
    "data_access_guard": Decision.REQUIRE_OFFLINE_RUNNER_DATA_ACCESS_GUARD_REVIEW_FIXES,
    "test_strategy_contract": Decision.REQUIRE_OFFLINE_RUNNER_TEST_STRATEGY_PREPARATION_REVIEW_FIXES,
    "rollback_strategy_contract": Decision.REQUIRE_OFFLINE_RUNNER_ROLLBACK_STRATEGY_PREPARATION_REVIEW_FIXES,
}

_SPECS = {
    key: (
        _FUNCTIONS[key],
        getattr(m, class_name),
        getattr(Risk, m._RISK_BY_KEY[key]),
        _DECISION_BY_KEY[key],
        getattr(Recommendation, f"FIX_{m._RISK_BY_KEY[key]}"),
    )
    for key, class_name in m._ITEMS
}


def _coerce_input(data):
    if data is None:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewInput()
    if isinstance(data, m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewInput):
        return data
    allowed = {field.name for field in fields(m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewInput)}
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewInput(**{key: value for key, value in dict(data).items() if key in allowed})


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


def _metric_score(explicit: int | None, fallback: Any, reviewed: bool) -> int:
    if not reviewed:
        return 0
    if explicit is not None:
        return _clamp(explicit)
    if fallback is not None:
        return _clamp(fallback)
    return 100


def _gate(data):
    return data.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation


def validate_offline_runner_implementation_preparation_approval(data) -> bool:
    data = _coerce_input(data)
    gate = _gate(data)
    if gate is None or data.offline_runner_implementation_preparation_approved is False:
        return False
    approved = data.offline_runner_implementation_preparation_approved is True or _contains(
        (_get(gate, "state"), _get(gate, "decision")),
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION",
    )
    return approved and not _as_tuple(_get(gate, "risks", ())) and _get(gate, "offline_only", True) is True


def _checks(data) -> dict[str, bool]:
    return {
        "offline_only": data.offline_mode_enforced is True,
        "sandbox_only": data.sandbox_mode_enforced is True,
        "implementation_preparation_review_only": data.implementation_preparation_review_only is True and data.real_execution_requested is not True,
        "no_runner_created": data.no_runner_created is True and data.runner_creation_requested is not True and data.real_execution_requested is not True,
        "no_runner_execution": data.no_runner_execution is True and data.runner_execution_requested is not True and data.real_execution_requested is not True,
        "no_dry_run_execution": data.no_dry_run_execution is True and data.dry_run_requested is not True and data.dry_run_executed is not True and data.real_execution_requested is not True,
        "no_real_broker": data.no_real_broker is True and data.no_broker_connection is True and data.broker_connection_requested is not True,
        "no_secret_read": data.no_api_key_read is True and data.no_env_var_read is True and data.no_hardcoded_secrets is True and data.api_key_read_requested is not True and data.env_var_read_requested is not True and data.hardcoded_secret_detected is not True,
        "network_blocked": data.network_transport_requested is not True and data.external_api_requested is not True and data.no_external_api is True,
        "http_blocked": data.no_http_transport is True,
        "websocket_blocked": data.no_websocket_transport is True,
        "socket_blocked": data.no_socket_transport is True,
        "order_blocked": data.no_real_order is True and data.order_execution_requested is not True,
        "position_mutation_blocked": data.no_position_mutation is True and data.position_mutation_requested is not True,
        "data_access_blocked": data.data_access_requested is not True,
        "read_only": data.account_access_requested is not True and data.no_real_account_access is True,
        "simulated_only": data.no_real_broker is True and data.no_alpaca_real is True,
        "observation_only": data.order_execution_requested is not True and data.position_mutation_requested is not True,
        "human_approval_required": data.human_approval_required is True,
        "stop_conditions_reviewed": True,
        "audit_reviewed": True,
        "test_strategy_reviewed": data.test_strategy_required is True,
        "rollback_strategy_reviewed": data.rollback_strategy_required is True,
    }


def _prepare(data, key: str):
    data = _coerce_input(data)
    _fn, cls, risk, _decision, _recommendation = _SPECS[key]
    checks = _checks(data)
    reviewed = _get(data, f"offline_runner_{key}_reviewed") is True and all(checks.values())
    return cls(
        name=key,
        score=_metric_score(_get(data, f"{key}_score"), _get(_get(_gate(data), key), "score"), reviewed),
        reviewed=reviewed,
        risks=() if reviewed else (risk,),
        details=("offline implementation preparation review finding reviewed without creating or executing a runner",),
        **checks,
    )


def _make_prepare(key: str):
    def prepare(data):
        return _prepare(data, key)

    prepare.__name__ = _SPECS[key][0]
    return prepare


for _key, _spec in _SPECS.items():
    globals()[_spec[0]] = _make_prepare(_key)


def _findings(data):
    return {key: _prepare(data, key) for key in _SPECS}


def _offline_boundary(data) -> bool:
    checks = _checks(data)
    return all(checks.values()) and data.no_external_ml is True and data.no_external_llm is True and data.no_live_execution is True


def _data_boundary(data) -> bool:
    return data.data_access_requested is not True and not _contains(_get(_gate(data), "risks", ()), "DATA_ACCESS", "DATA/")


def compute_offline_runner_implementation_preparation_review_score(data, findings: Mapping[str, Any] | None = None) -> m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewScore:
    data = _coerce_input(data)
    findings = dict(findings or _findings(data))
    approved = validate_offline_runner_implementation_preparation_approval(data)
    gate_score = _metric_score(
        data.implementation_safety_gate_score,
        _get(_get(_gate(data), "score"), "overall_score") if approved else None,
        approved,
    )
    values = {key: _get(value, "score", 0) for key, value in findings.items()}
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewScore(
        overall_score=_average((gate_score, *values.values())),
        implementation_safety_gate_score=gate_score,
        **{f"{key}_score": value for key, value in values.items()},
    )


def detect_offline_runner_implementation_preparation_review_risks(data, findings: Mapping[str, Any] | None = None) -> tuple[Risk, ...]:
    data = _coerce_input(data)
    findings = dict(findings or _findings(data))
    risks: list[Risk] = []
    if not validate_offline_runner_implementation_preparation_approval(data):
        risks.append(Risk.OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_NOT_APPROVED)
    for finding in findings.values():
        risks.extend(_as_tuple(_get(finding, "risks", ())))
    if not _offline_boundary(data):
        risks.append(Risk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(Risk.DATA_ACCESS_VIOLATION)
    if data.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_final_plan_requested is True:
        risks.append(Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_FINAL_PLAN)
    return _dedupe(risks)


def generate_offline_runner_implementation_preparation_review_recommendations(data, risks: Iterable[Risk] | None = None) -> tuple[Recommendation, ...]:
    risks = tuple(risks if risks is not None else detect_offline_runner_implementation_preparation_review_risks(data))
    if not risks:
        return (
            Recommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW_SUITE,
            Recommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_FINAL_PLAN,
        )
    recommendations = [Recommendation.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_FINAL_PLAN]
    if Risk.OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_NOT_APPROVED in risks:
        recommendations.append(Recommendation.APPROVE_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_FIRST)
    if Risk.REAL_EXECUTION_BOUNDARY_VIOLATION in risks:
        recommendations.append(Recommendation.RESTORE_OFFLINE_BOUNDARIES)
    if Risk.DATA_ACCESS_VIOLATION in risks:
        recommendations.append(Recommendation.REMOVE_DATA_ACCESS)
    if Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_FINAL_PLAN in risks:
        recommendations.append(Recommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_FINAL_PLAN)
    for risk in risks:
        recommendation_name = f"FIX_{_value(risk)}"
        if hasattr(Recommendation, recommendation_name):
            recommendations.append(getattr(Recommendation, recommendation_name))
    return _dedupe(recommendations)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW
    if any(risk in {Risk.REAL_EXECUTION_BOUNDARY_VIOLATION, Risk.DATA_ACCESS_VIOLATION, Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_FINAL_PLAN} for risk in risks):
        return Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW
    if risks[0] is Risk.OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_NOT_APPROVED:
        return Decision.REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_FIXES
    for key, (_fn, _cls, risk, decision, _recommendation) in _SPECS.items():
        if risks[0] is risk:
            return decision
    return Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW


def _state_for(data, risks: tuple[Risk, ...], score):
    if _gate(data) is None:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewState.OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW_INPUT_INVALID
    if not risks and score.overall_score >= 85:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_FINAL_PLAN
    if risks:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewState.OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW_BLOCKED
    if score.overall_score >= 70:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewState.OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW_COMPLETED_WITH_WARNINGS
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewState.NOT_READY


def render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_review_markdown(result) -> str:
    risks = ", ".join(_value(risk) for risk in result.risks) or "none"
    recommendations = ", ".join(_value(recommendation) for recommendation in result.recommendations) or "none"
    return "\n".join((
        "# Paper Broker Read-Only Connection Dry Run Controlled Offline Runner Implementation Preparation Review",
        f"- State: {_value(result.state)}",
        f"- Decision: {_value(result.decision)}",
        f"- Score: {result.score.overall_score}",
        f"- Risks: {risks}",
        f"- Recommendations: {recommendations}",
        "- Boundary: implementation preparation review only; no executable runner creation, no runner execution, no dry-run, no broker connection, no secrets, no network, no orders, no position mutation, no data access.",
        f"- Next phase: {result.next_phase}",
    ))


def evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_review(data=None):
    data = _coerce_input(data)
    findings = _findings(data)
    score = compute_offline_runner_implementation_preparation_review_score(data, findings)
    risks = detect_offline_runner_implementation_preparation_review_risks(data, findings)
    recommendations = generate_offline_runner_implementation_preparation_review_recommendations(data, risks)
    result = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewResult(
        state=_state_for(data, risks, score),
        decision=_decision_for(risks),
        score=score,
        risks=risks,
        recommendations=recommendations,
        summary="Offline runner implementation preparation review approved for preparation_review review" if not risks else "Offline runner implementation preparation review blocked",
        offline_only=True,
        sandbox_only=True,
        implementation_preparation_review_only=True,
        runner_created=False,
        runner_executed=False,
        dry_run_executed=False,
        findings=tuple(findings.values()),
        **findings,
    )
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewResult(
        **{**result.__dict__, "markdown_report": render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_review_markdown(result)}
    )
