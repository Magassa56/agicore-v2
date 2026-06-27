"""Final offline plan for a controlled read-only paper broker dry-run runner."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading import paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_plan_models as m

Risk = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanRisk
Decision = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanDecision
Recommendation = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanRecommendation


def _coerce_input(data):
    if data is None:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanInput()
    if isinstance(data, m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanInput):
        return data
    allowed = {field.name for field in fields(m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanInput)}
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanInput(**{key: value for key, value in dict(data).items() if key in allowed})


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


def _review(data):
    return data.paper_broker_read_only_connection_dry_run_controlled_offline_runner_preparation_review


def validate_offline_runner_preparation_review_approval(data) -> bool:
    data = _coerce_input(data)
    review = _review(data)
    if review is None or data.offline_runner_preparation_review_approved is False:
        return False
    approved = data.offline_runner_preparation_review_approved is True or _contains(
        (_get(review, "state"), _get(review, "decision")),
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_PREPARATION_REVIEW",
    )
    return approved and not _as_tuple(_get(review, "risks", ())) and _get(review, "offline_only", True) is True


def _offline_boundary(data) -> bool:
    expected = (
        data.offline_mode_enforced, data.sandbox_mode_enforced, data.final_plan_only,
        data.no_runner_executable_created, data.no_runner_execution, data.no_dry_run_execution,
        data.broker_connection_disabled, data.no_real_broker, data.no_alpaca_real,
        data.no_api_key_read, data.no_env_var_read, data.no_hardcoded_secrets,
        data.no_http_transport, data.no_websocket_transport, data.no_socket_transport,
        data.no_external_api, data.no_external_ml, data.no_external_llm, data.no_live_execution,
        data.no_real_account_access, data.no_real_order, data.no_position_mutation,
    )
    requested = (
        data.real_execution_requested, data.runner_creation_requested, data.runner_execution_requested,
        data.dry_run_requested, data.dry_run_executed, data.broker_connection_requested,
        data.api_key_read_requested, data.env_var_read_requested, data.hardcoded_secret_detected,
        data.network_transport_requested, data.external_api_requested, data.order_execution_requested,
        data.position_mutation_requested, data.account_access_requested,
    )
    return all(item is True for item in expected) and not any(item is True for item in requested)


def _data_boundary(data) -> bool:
    return data.data_access_requested is not True and not _contains(_get(_review(data), "risks", ()), "DATA_ACCESS", "DATA/")


_SPECS = {
    "scope": ("define_final_offline_runner_scope", m.FinalOfflineRunnerScope, Risk.FINAL_OFFLINE_RUNNER_SCOPE_UNCLEAR, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SCOPE_FIXES, Recommendation.FIX_FINAL_OFFLINE_RUNNER_SCOPE, "final_offline_runner_scope_defined", "scope_score", ("offline_only", "sandbox_only", "final_plan_only", "no_runner_executable_created")),
    "execution_mode": ("define_final_offline_runner_execution_mode", m.FinalOfflineRunnerExecutionMode, Risk.FINAL_OFFLINE_RUNNER_EXECUTION_MODE_UNSAFE, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_EXECUTION_MODE_FIXES, Recommendation.FIX_FINAL_OFFLINE_RUNNER_EXECUTION_MODE, "final_offline_runner_execution_mode_defined", "execution_mode_score", ("controlled_offline_mode", "deterministic_mode", "in_memory_only", "no_dry_run_execution")),
    "input_contract": ("define_final_offline_runner_input_contract", m.FinalOfflineRunnerInputContract, Risk.FINAL_OFFLINE_RUNNER_INPUT_CONTRACT_MISSING, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_INPUT_CONTRACT_FIXES, Recommendation.FIX_FINAL_OFFLINE_RUNNER_INPUT_CONTRACT, "final_offline_runner_input_contract_defined", "input_contract_score", ("schema_only_inputs", "synthetic_inputs_only", "no_real_credentials")),
    "synthetic_market_context": ("define_final_offline_runner_synthetic_market_context", m.FinalOfflineRunnerSyntheticMarketContext, Risk.FINAL_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_MISSING, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_FIXES, Recommendation.FIX_FINAL_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT, "final_offline_runner_synthetic_market_context_defined", "synthetic_market_context_score", ("synthetic_context_only", "in_memory_context", "no_data_access")),
    "read_only_broker_simulation": ("define_final_offline_runner_read_only_broker_simulation_contract", m.FinalOfflineRunnerReadOnlyBrokerSimulationContract, Risk.FINAL_OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_UNSAFE, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION_FIXES, Recommendation.FIX_FINAL_OFFLINE_RUNNER_READ_ONLY_BROKER_SIMULATION, "final_offline_runner_read_only_broker_simulation_defined", "read_only_broker_simulation_score", ("simulated_broker_only", "read_only_contract", "no_real_broker")),
    "no_real_broker_policy": ("define_final_offline_runner_no_real_broker_policy", m.FinalOfflineRunnerNoRealBrokerPolicy, Risk.FINAL_OFFLINE_RUNNER_REAL_BROKER_POLICY_UNSAFE, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_NO_REAL_BROKER_FIXES, Recommendation.FIX_FINAL_OFFLINE_RUNNER_NO_REAL_BROKER_POLICY, "final_offline_runner_no_real_broker_policy_defined", "no_real_broker_score", ("real_broker_blocked", "alpaca_blocked", "broker_connection_disabled")),
    "no_secret_read_policy": ("define_final_offline_runner_no_secret_read_policy", m.FinalOfflineRunnerNoSecretReadPolicy, Risk.FINAL_OFFLINE_RUNNER_SECRET_READ_POLICY_UNSAFE, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_NO_SECRET_READ_FIXES, Recommendation.FIX_FINAL_OFFLINE_RUNNER_NO_SECRET_READ_POLICY, "final_offline_runner_no_secret_read_policy_defined", "no_secret_read_score", ("no_api_key_read", "no_env_var_read", "no_hardcoded_secret")),
    "network_block_policy": ("define_final_offline_runner_network_block_policy", m.FinalOfflineRunnerNetworkBlockPolicy, Risk.FINAL_OFFLINE_RUNNER_NETWORK_NOT_BLOCKED, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_NETWORK_BLOCK_FIXES, Recommendation.FIX_FINAL_OFFLINE_RUNNER_NETWORK_BLOCK_POLICY, "final_offline_runner_network_block_policy_defined", "network_score", ("network_blocked", "http_blocked", "websocket_blocked", "socket_blocked", "external_api_blocked")),
    "http_websocket_socket_block_policy": ("define_final_offline_runner_http_websocket_socket_block_policy", m.FinalOfflineRunnerNetworkBlockPolicy, Risk.FINAL_OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_NOT_BLOCKED, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_NETWORK_BLOCK_FIXES, Recommendation.FIX_FINAL_OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_BLOCK_POLICY, "final_offline_runner_http_websocket_socket_block_policy_defined", "http_websocket_socket_score", ("network_blocked", "http_blocked", "websocket_blocked", "socket_blocked", "external_api_blocked")),
    "account_snapshot_policy": ("define_final_offline_runner_account_snapshot_policy", m.FinalOfflineRunnerAccountSnapshotPolicy, Risk.FINAL_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_UNSAFE, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_FIXES, Recommendation.FIX_FINAL_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT, "final_offline_runner_account_snapshot_policy_defined", "account_snapshot_score", ("simulated_snapshot_only", "read_only_snapshot", "active_account_access_blocked")),
    "market_data_snapshot_policy": ("define_final_offline_runner_market_data_snapshot_policy", m.FinalOfflineRunnerMarketDataSnapshotPolicy, Risk.FINAL_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_UNSAFE, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_FIXES, Recommendation.FIX_FINAL_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT, "final_offline_runner_market_data_snapshot_policy_defined", "market_data_snapshot_score", ("synthetic_snapshot_only", "read_only_snapshot", "live_subscription_blocked")),
    "order_blocking_policy": ("define_final_offline_runner_order_blocking_policy", m.FinalOfflineRunnerOrderBlockingPolicy, Risk.FINAL_OFFLINE_RUNNER_ORDER_BLOCKING_UNSAFE, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_ORDER_BLOCKING_FIXES, Recommendation.FIX_FINAL_OFFLINE_RUNNER_ORDER_BLOCKING, "final_offline_runner_order_blocking_policy_defined", "order_blocking_score", ("order_execution_blocked", "real_order_blocked", "cancel_replace_blocked")),
    "position_mutation_blocking_policy": ("define_final_offline_runner_position_mutation_blocking_policy", m.FinalOfflineRunnerPositionMutationBlockingPolicy, Risk.FINAL_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_UNSAFE, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_FIXES, Recommendation.FIX_FINAL_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING, "final_offline_runner_position_mutation_blocking_policy_defined", "position_mutation_score", ("position_mutation_blocked", "close_modify_blocked", "simulated_position_read_only")),
    "strategy_signal_observation_plan": ("define_final_offline_runner_strategy_signal_observation_plan", m.FinalOfflineRunnerStrategySignalObservationPlan, Risk.FINAL_OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_MISSING, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION_FIXES, Recommendation.FIX_FINAL_OFFLINE_RUNNER_STRATEGY_SIGNAL_OBSERVATION, "final_offline_runner_strategy_signal_observation_plan_defined", "strategy_signal_observation_score", ("observation_only", "no_signal_execution", "signal_trace_required")),
    "risk_observation_plan": ("define_final_offline_runner_risk_observation_plan", m.FinalOfflineRunnerRiskObservationPlan, Risk.FINAL_OFFLINE_RUNNER_RISK_OBSERVATION_MISSING, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_RISK_OBSERVATION_FIXES, Recommendation.FIX_FINAL_OFFLINE_RUNNER_RISK_OBSERVATION, "final_offline_runner_risk_observation_plan_defined", "risk_observation_score", ("observation_only", "no_risk_action_execution", "risk_trace_required")),
    "profitability_observation_plan": ("define_final_offline_runner_profitability_observation_plan", m.FinalOfflineRunnerProfitabilityObservationPlan, Risk.FINAL_OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_MISSING, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_PROFITABILITY_OBSERVATION_FIXES, Recommendation.FIX_FINAL_OFFLINE_RUNNER_PROFITABILITY_OBSERVATION, "final_offline_runner_profitability_observation_plan_defined", "profitability_observation_score", ("observation_only", "no_profit_promise", "profitability_trace_required")),
    "consistency_observation_plan": ("define_final_offline_runner_consistency_observation_plan", m.FinalOfflineRunnerConsistencyObservationPlan, Risk.FINAL_OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_MISSING, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_CONSISTENCY_OBSERVATION_FIXES, Recommendation.FIX_FINAL_OFFLINE_RUNNER_CONSISTENCY_OBSERVATION, "final_offline_runner_consistency_observation_plan_defined", "consistency_observation_score", ("observation_only", "deterministic_consistency_checks", "consistency_trace_required")),
    "journal_plan": ("define_final_offline_runner_journal_plan", m.FinalOfflineRunnerJournalPlan, Risk.FINAL_OFFLINE_RUNNER_JOURNAL_MISSING, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_JOURNAL_FIXES, Recommendation.FIX_FINAL_OFFLINE_RUNNER_JOURNAL, "final_offline_runner_journal_plan_defined", "journal_score", ("offline_journal_required", "no_secret_material_logged", "plan_events_recorded")),
    "observability_plan": ("define_final_offline_runner_observability_plan", m.FinalOfflineRunnerObservabilityPlan, Risk.FINAL_OFFLINE_RUNNER_OBSERVABILITY_MISSING, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_OBSERVABILITY_FIXES, Recommendation.FIX_FINAL_OFFLINE_RUNNER_OBSERVABILITY, "final_offline_runner_observability_plan_defined", "observability_score", ("offline_events_defined", "no_connection_attempt_metrics", "sensitive_values_redacted")),
    "human_approval_plan": ("define_final_offline_runner_human_approval_plan", m.FinalOfflineRunnerHumanApprovalPlan, Risk.FINAL_OFFLINE_RUNNER_HUMAN_APPROVAL_MISSING, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_HUMAN_APPROVAL_FIXES, Recommendation.FIX_FINAL_OFFLINE_RUNNER_HUMAN_APPROVAL, "final_offline_runner_human_approval_plan_defined", "human_approval_score", ("human_approval_required", "approval_before_final_safety_gate", "evidence_required")),
    "stop_conditions_plan": ("define_final_offline_runner_stop_conditions_plan", m.FinalOfflineRunnerStopConditionPlan, Risk.FINAL_OFFLINE_RUNNER_STOP_CONDITIONS_MISSING, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_STOP_CONDITION_FIXES, Recommendation.FIX_FINAL_OFFLINE_RUNNER_STOP_CONDITIONS, "final_offline_runner_stop_conditions_plan_defined", "stop_conditions_score", ("stop_on_secret_read", "stop_on_network_request", "stop_on_order_or_position_request", "stop_on_account_access_request")),
    "success_criteria": ("define_final_offline_runner_success_criteria", m.FinalOfflineRunnerSuccessCriteria, Risk.FINAL_OFFLINE_RUNNER_SUCCESS_CRITERIA_MISSING, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SUCCESS_FAILURE_FIXES, Recommendation.FIX_FINAL_OFFLINE_RUNNER_SUCCESS_FAILURE, "final_offline_runner_success_criteria_defined", "success_score", ("no_boundary_violation_required", "all_plans_defined", "no_runner_execution_required")),
    "failure_criteria": ("define_final_offline_runner_failure_criteria", m.FinalOfflineRunnerFailureCriteria, Risk.FINAL_OFFLINE_RUNNER_FAILURE_CRITERIA_MISSING, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SUCCESS_FAILURE_FIXES, Recommendation.FIX_FINAL_OFFLINE_RUNNER_SUCCESS_FAILURE, "final_offline_runner_failure_criteria_defined", "failure_score", ("fail_on_boundary_violation", "fail_on_missing_plan", "fail_on_execution_request")),
    "audit_plan": ("define_final_offline_runner_audit_plan", m.FinalOfflineRunnerAuditPlan, Risk.FINAL_OFFLINE_RUNNER_AUDIT_PLAN_MISSING, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_AUDIT_FIXES, Recommendation.FIX_FINAL_OFFLINE_RUNNER_AUDIT, "final_offline_runner_audit_plan_defined", "audit_score", ("audit_events_defined", "boundary_evidence_required", "immutable_final_plan_record_required")),
    "go_no_go_policy": ("define_final_offline_runner_go_no_go_policy", m.FinalOfflineRunnerGoNoGoPolicy, Risk.FINAL_OFFLINE_RUNNER_GO_NO_GO_POLICY_MISSING, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_GO_NO_GO_FIXES, Recommendation.FIX_FINAL_OFFLINE_RUNNER_GO_NO_GO, "final_offline_runner_go_no_go_policy_defined", "go_no_go_score", ("go_no_go_required", "no_go_on_risk", "next_phase_requires_clean_final_plan")),
    "abort_policy": ("define_final_offline_runner_abort_policy", m.FinalOfflineRunnerAbortPolicy, Risk.FINAL_OFFLINE_RUNNER_ABORT_POLICY_MISSING, Decision.REQUIRE_FINAL_OFFLINE_RUNNER_ABORT_FIXES, Recommendation.FIX_FINAL_OFFLINE_RUNNER_ABORT, "final_offline_runner_abort_policy_defined", "abort_score", ("abort_on_secret_read", "abort_on_network_or_broker_request", "abort_on_order_or_position_request")),
}


def _checks(data, attrs: tuple[str, ...]) -> dict[str, bool]:
    blocked = {
        "no_runner_executable_created": data.runner_creation_requested is not True,
        "no_dry_run_execution": data.dry_run_requested is not True and data.dry_run_executed is not True,
        "no_real_broker": data.broker_connection_requested is not True and data.no_real_broker is True,
        "real_broker_blocked": data.broker_connection_requested is not True and data.no_real_broker is True,
        "alpaca_blocked": data.no_alpaca_real is True,
        "broker_connection_disabled": data.broker_connection_disabled is True and data.broker_connection_requested is not True,
        "no_api_key_read": data.no_api_key_read is True and data.api_key_read_requested is not True,
        "no_env_var_read": data.no_env_var_read is True and data.env_var_read_requested is not True,
        "no_hardcoded_secret": data.no_hardcoded_secrets is True and data.hardcoded_secret_detected is not True,
        "network_blocked": data.network_transport_requested is not True,
        "http_blocked": data.no_http_transport is True,
        "websocket_blocked": data.no_websocket_transport is True,
        "socket_blocked": data.no_socket_transport is True,
        "external_api_blocked": data.no_external_api is True and data.external_api_requested is not True,
        "active_account_access_blocked": data.account_access_requested is not True,
        "order_execution_blocked": data.order_execution_requested is not True,
        "real_order_blocked": data.no_real_order is True and data.order_execution_requested is not True,
        "position_mutation_blocked": data.no_position_mutation is True and data.position_mutation_requested is not True,
        "no_data_access": data.data_access_requested is not True,
        "no_runner_execution_required": data.no_runner_execution is True and data.runner_execution_requested is not True,
        "fail_on_execution_request": data.runner_execution_requested is not True and data.dry_run_requested is not True,
        "next_phase_requires_clean_final_plan": data.paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_safety_gate_requested is not True,
        "no_connection_attempt_metrics": data.broker_connection_requested is not True,
    }
    return {attr: blocked.get(attr, True) for attr in attrs}


def _define(data, key: str):
    data = _coerce_input(data)
    _fn, cls, risk, _decision, _recommendation, flag, score_name, attrs = _SPECS[key]
    values = _checks(data, attrs)
    defined = _get(data, flag) is True and all(values.values())
    return cls(name=key, score=_metric_score(_get(data, score_name), _get(_get(_review(data), key), "score"), defined), defined=defined, risks=() if defined else (risk,), details=("final offline runner plan defined without creating or executing a runner",), **values)


def _make_define(key: str):
    def define(data):
        return _define(data, key)
    define.__name__ = _SPECS[key][0]
    return define


for _key, _spec in _SPECS.items():
    globals()[_spec[0]] = _make_define(_key)


def _artifacts(data):
    return {key: _define(data, key) for key in _SPECS}


_SCORE_MAP = {
    "scope_score": "scope", "execution_mode_score": "execution_mode", "input_contract_score": "input_contract", "synthetic_market_context_score": "synthetic_market_context", "read_only_broker_simulation_score": "read_only_broker_simulation", "no_real_broker_score": "no_real_broker_policy", "no_secret_read_score": "no_secret_read_policy", "network_score": "network_block_policy", "http_websocket_socket_score": "http_websocket_socket_block_policy", "account_snapshot_score": "account_snapshot_policy", "market_data_snapshot_score": "market_data_snapshot_policy", "order_blocking_score": "order_blocking_policy", "position_mutation_score": "position_mutation_blocking_policy", "strategy_signal_observation_score": "strategy_signal_observation_plan", "risk_observation_score": "risk_observation_plan", "profitability_observation_score": "profitability_observation_plan", "consistency_observation_score": "consistency_observation_plan", "journal_score": "journal_plan", "observability_score": "observability_plan", "human_approval_score": "human_approval_plan", "stop_conditions_score": "stop_conditions_plan", "success_score": "success_criteria", "failure_score": "failure_criteria", "audit_score": "audit_plan", "go_no_go_score": "go_no_go_policy", "abort_score": "abort_policy",
}


def compute_final_offline_runner_plan_score(data, artifacts: Mapping[str, Any] | None = None) -> m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanScore:
    data = _coerce_input(data)
    artifacts = dict(artifacts or _artifacts(data))
    review_score = _metric_score(data.offline_runner_preparation_review_score, _get(_get(_review(data), "score"), "overall_score"), validate_offline_runner_preparation_review_approval(data))
    scores = {key: _get(value, "score", 0) for key, value in artifacts.items()}
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanScore(overall_score=_average((review_score, *scores.values())), offline_runner_preparation_review_score=review_score, **{field: scores[key] for field, key in _SCORE_MAP.items()})


def detect_final_offline_runner_plan_risks(data, artifacts: Mapping[str, Any] | None = None) -> tuple[Risk, ...]:
    data = _coerce_input(data)
    artifacts = dict(artifacts or _artifacts(data))
    risks: list[Risk] = []
    if not validate_offline_runner_preparation_review_approval(data):
        risks.append(Risk.OFFLINE_RUNNER_PREPARATION_REVIEW_NOT_APPROVED)
    for artifact in artifacts.values():
        risks.extend(_as_tuple(_get(artifact, "risks", ())))
    if not _offline_boundary(data):
        risks.append(Risk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(Risk.DATA_ACCESS_VIOLATION)
    if data.paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_safety_gate_requested is True:
        risks.append(Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE)
    return _dedupe(risks)

def generate_final_offline_runner_plan_recommendations(data, risks: Iterable[Risk] | None = None) -> tuple[Recommendation, ...]:
    risks = tuple(risks if risks is not None else detect_final_offline_runner_plan_risks(data))
    if not risks:
        return (Recommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN_SUITE, Recommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE)
    recommendations = [Recommendation.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE]
    for risk in risks:
        if risk is Risk.OFFLINE_RUNNER_PREPARATION_REVIEW_NOT_APPROVED:
            recommendations.append(Recommendation.APPROVE_OFFLINE_RUNNER_PREPARATION_REVIEW_FIRST)
        elif risk is Risk.REAL_EXECUTION_BOUNDARY_VIOLATION:
            recommendations.append(Recommendation.RESTORE_OFFLINE_BOUNDARIES)
        elif risk is Risk.DATA_ACCESS_VIOLATION:
            recommendations.append(Recommendation.REMOVE_DATA_ACCESS)
        elif risk is Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE:
            recommendations.append(Recommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE)
        else:
            for _key, _spec in _SPECS.items():
                if risk is _spec[2]:
                    recommendations.append(_spec[4])
                    break
    return _dedupe(recommendations)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN
    if any(risk in {Risk.REAL_EXECUTION_BOUNDARY_VIOLATION, Risk.DATA_ACCESS_VIOLATION, Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE} for risk in risks):
        return Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN
    if risks[0] is Risk.OFFLINE_RUNNER_PREPARATION_REVIEW_NOT_APPROVED:
        return Decision.REQUIRE_OFFLINE_RUNNER_PREPARATION_REVIEW_FIXES
    for _key, _spec in _SPECS.items():
        if risks[0] is _spec[2]:
            return _spec[3]
    return Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_PLAN


def _state_for(data, risks: tuple[Risk, ...], score):
    if _review(data) is None:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanState.FINAL_OFFLINE_RUNNER_PLAN_INPUT_INVALID
    if not risks and score.overall_score >= 85:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE
    if risks:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanState.FINAL_OFFLINE_RUNNER_PLAN_BLOCKED
    if score.overall_score >= 70:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanState.FINAL_OFFLINE_RUNNER_PLAN_COMPLETED_WITH_WARNINGS
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanState.NOT_READY


def render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_plan_markdown(result) -> str:
    risks = ", ".join(_value(risk) for risk in result.risks) or "none"
    recommendations = ", ".join(_value(recommendation) for recommendation in result.recommendations) or "none"
    return "\n".join((
        "# Paper Broker Read-Only Connection Dry Run Controlled Offline Runner Final Plan",
        f"- State: {_value(result.state)}",
        f"- Decision: {_value(result.decision)}",
        f"- Score: {result.score.overall_score}",
        f"- Risks: {risks}",
        f"- Recommendations: {recommendations}",
        "- Boundary: offline/sandbox final plan only; no executable runner creation, no runner execution, no dry-run, no broker connection, no secrets, no network, no orders, no position mutation, no data access.",
        f"- Next phase: {result.next_phase}",
    ))


def evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_plan(data=None):
    data = _coerce_input(data)
    artifacts = _artifacts(data)
    score = compute_final_offline_runner_plan_score(data, artifacts)
    risks = detect_final_offline_runner_plan_risks(data, artifacts)
    recommendations = generate_final_offline_runner_plan_recommendations(data, risks)
    result = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanResult(
        state=_state_for(data, risks, score),
        decision=_decision_for(risks),
        score=score,
        risks=risks,
        recommendations=recommendations,
        summary="Final offline runner plan approved for final safety gate" if not risks else "Final offline runner plan blocked",
        offline_only=True,
        sandbox_only=True,
        final_plan_only=True,
        runner_created=False,
        runner_executed=False,
        dry_run_executed=False,
        artifacts=tuple(artifacts.values()),
        **artifacts,
    )
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerFinalPlanResult(
        **{**result.__dict__, "markdown_report": render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_plan_markdown(result)}
    )
