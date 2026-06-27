"""Safety gate for the controlled offline runner implementation plan."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading import paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate_models as m

Risk = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateRisk
Decision = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateDecision
Recommendation = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateRecommendation


_SPEC_DATA = (
    ("scope_boundary", "validate_offline_runner_implementation_safety_scope_boundary", "OfflineRunnerImplementationSafetyScopeBoundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SCOPE_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SCOPE_FIXES", "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SCOPE"),
    ("architecture_boundary", "validate_offline_runner_implementation_safety_architecture_boundary", "OfflineRunnerImplementationSafetyArchitectureBoundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ARCHITECTURE_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ARCHITECTURE_FIXES", "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ARCHITECTURE"),
    ("sequence_boundary", "validate_offline_runner_implementation_safety_sequence_boundary", "OfflineRunnerImplementationSafetySequenceBoundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SEQUENCE_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SEQUENCE_FIXES", "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SEQUENCE"),
    ("runtime_contract_boundary", "validate_offline_runner_implementation_safety_runtime_contract_boundary", "OfflineRunnerImplementationSafetyRuntimeContractBoundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_RUNTIME_CONTRACT_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_RUNTIME_CONTRACT_FIXES", "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_RUNTIME_CONTRACT"),
    ("input_adapter_boundary", "validate_offline_runner_implementation_safety_input_adapter_boundary", "OfflineRunnerImplementationSafetyInputAdapterBoundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_INPUT_ADAPTER_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_INPUT_ADAPTER_FIXES", "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_INPUT_ADAPTER"),
    ("synthetic_market_context_adapter_boundary", "validate_offline_runner_implementation_safety_synthetic_market_context_adapter_boundary", "OfflineRunnerImplementationSafetySyntheticMarketContextAdapterBoundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SYNTHETIC_MARKET_CONTEXT_ADAPTER_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SYNTHETIC_MARKET_CONTEXT_ADAPTER_FIXES", "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SYNTHETIC_MARKET_CONTEXT_ADAPTER"),
    ("simulated_broker_adapter_boundary", "validate_offline_runner_implementation_safety_simulated_broker_adapter_boundary", "OfflineRunnerImplementationSafetySimulatedBrokerAdapterBoundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SIMULATED_BROKER_ADAPTER_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SIMULATED_BROKER_ADAPTER_FIXES", "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SIMULATED_BROKER_ADAPTER"),
    ("account_snapshot_adapter_boundary", "validate_offline_runner_implementation_safety_account_snapshot_adapter_boundary", "OfflineRunnerImplementationSafetyAccountSnapshotAdapterBoundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ACCOUNT_SNAPSHOT_ADAPTER_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ACCOUNT_SNAPSHOT_ADAPTER_FIXES", "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ACCOUNT_SNAPSHOT_ADAPTER"),
    ("market_data_snapshot_adapter_boundary", "validate_offline_runner_implementation_safety_market_data_snapshot_adapter_boundary", "OfflineRunnerImplementationSafetyMarketDataSnapshotAdapterBoundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_MARKET_DATA_SNAPSHOT_ADAPTER_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_MARKET_DATA_SNAPSHOT_ADAPTER_FIXES", "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_MARKET_DATA_SNAPSHOT_ADAPTER"),
    ("strategy_signal_probe_boundary", "validate_offline_runner_implementation_safety_strategy_signal_probe_boundary", "OfflineRunnerImplementationSafetyStrategySignalProbeBoundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_STRATEGY_SIGNAL_PROBE_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_STRATEGY_SIGNAL_PROBE_FIXES", "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_STRATEGY_SIGNAL_PROBE"),
    ("risk_observer_boundary", "validate_offline_runner_implementation_safety_risk_observer_boundary", "OfflineRunnerImplementationSafetyRiskObserverBoundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_RISK_OBSERVER_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_RISK_OBSERVER_FIXES", "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_RISK_OBSERVER"),
    ("profitability_observer_boundary", "validate_offline_runner_implementation_safety_profitability_observer_boundary", "OfflineRunnerImplementationSafetyProfitabilityObserverBoundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_PROFITABILITY_OBSERVER_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_PROFITABILITY_OBSERVER_FIXES", "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_PROFITABILITY_OBSERVER"),
    ("consistency_observer_boundary", "validate_offline_runner_implementation_safety_consistency_observer_boundary", "OfflineRunnerImplementationSafetyConsistencyObserverBoundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_CONSISTENCY_OBSERVER_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_CONSISTENCY_OBSERVER_FIXES", "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_CONSISTENCY_OBSERVER"),
    ("journal_writer_boundary", "validate_offline_runner_implementation_safety_journal_writer_boundary", "OfflineRunnerImplementationSafetyJournalWriterBoundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_JOURNAL_WRITER_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_JOURNAL_WRITER_FIXES", "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_JOURNAL_WRITER"),
    ("observability_boundary", "validate_offline_runner_implementation_safety_observability_boundary", "OfflineRunnerImplementationSafetyObservabilityBoundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_OBSERVABILITY_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_OBSERVABILITY_FIXES", "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_OBSERVABILITY"),
    ("human_approval_boundary", "validate_offline_runner_implementation_safety_human_approval_boundary", "OfflineRunnerImplementationSafetyHumanApprovalBoundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_HUMAN_APPROVAL_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_HUMAN_APPROVAL_FIXES", "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_HUMAN_APPROVAL"),
    ("stop_condition_boundary", "validate_offline_runner_implementation_safety_stop_condition_boundary", "OfflineRunnerImplementationSafetyStopConditionBoundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_STOP_CONDITION_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_STOP_CONDITION_FIXES", "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_STOP_CONDITIONS"),
    ("success_failure_boundary", "validate_offline_runner_implementation_safety_success_failure_boundary", "OfflineRunnerImplementationSafetySuccessFailureBoundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SUCCESS_FAILURE_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SUCCESS_FAILURE_FIXES", "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SUCCESS_FAILURE"),
    ("audit_boundary", "validate_offline_runner_implementation_safety_audit_boundary", "OfflineRunnerImplementationSafetyAuditBoundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_AUDIT_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_AUDIT_FIXES", "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_AUDIT"),
    ("go_no_go_boundary", "validate_offline_runner_implementation_safety_go_no_go_boundary", "OfflineRunnerImplementationSafetyGoNoGoBoundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GO_NO_GO_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GO_NO_GO_FIXES", "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GO_NO_GO"),
    ("abort_boundary", "validate_offline_runner_implementation_safety_abort_boundary", "OfflineRunnerImplementationSafetyAbortBoundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ABORT_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ABORT_FIXES", "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ABORT"),
    ("no_real_broker_boundary", "validate_offline_runner_implementation_safety_no_real_broker_boundary", "OfflineRunnerImplementationSafetyNoRealBrokerBoundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_REAL_BROKER_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_NO_REAL_BROKER_FIXES", "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_NO_REAL_BROKER"),
    ("no_secret_read_boundary", "validate_offline_runner_implementation_safety_no_secret_read_boundary", "OfflineRunnerImplementationSafetyNoSecretReadBoundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_SECRET_READ_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_NO_SECRET_READ_FIXES", "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_NO_SECRET_READ"),
    ("network_block_boundary", "validate_offline_runner_implementation_safety_network_block_boundary", "OfflineRunnerImplementationSafetyNetworkBlockBoundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_NETWORK_BLOCK_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_NETWORK_BLOCK_FIXES", "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_NETWORK_BLOCK"),
    ("http_websocket_socket_block_boundary", "validate_offline_runner_implementation_safety_http_websocket_socket_block_boundary", "OfflineRunnerImplementationSafetyNetworkBlockBoundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_HTTP_WEBSOCKET_SOCKET_BLOCK_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_NETWORK_BLOCK_FIXES", "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_HTTP_WEBSOCKET_SOCKET_BLOCK"),
    ("order_blocking_boundary", "validate_offline_runner_implementation_safety_order_blocking_boundary", "OfflineRunnerImplementationSafetyOrderBlockingBoundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ORDER_BLOCKING_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ORDER_BLOCKING_FIXES", "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ORDER_BLOCKING"),
    ("position_mutation_blocking_boundary", "validate_offline_runner_implementation_safety_position_mutation_blocking_boundary", "OfflineRunnerImplementationSafetyPositionMutationBlockingBoundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_POSITION_MUTATION_BLOCKING_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_POSITION_MUTATION_BLOCKING_FIXES", "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_POSITION_MUTATION_BLOCKING"),
    ("data_access_boundary", "validate_offline_runner_implementation_safety_data_access_boundary", "OfflineRunnerImplementationSafetyDataAccessBoundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_DATA_ACCESS_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_DATA_ACCESS_FIXES", "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_DATA_ACCESS"),
    ("test_strategy_boundary", "validate_offline_runner_implementation_safety_test_strategy_boundary", "OfflineRunnerImplementationSafetyTestStrategyBoundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_TEST_STRATEGY_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_TEST_STRATEGY_FIXES", "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_TEST_STRATEGY"),
    ("rollback_strategy_boundary", "validate_offline_runner_implementation_safety_rollback_strategy_boundary", "OfflineRunnerImplementationSafetyRollbackStrategyBoundary", "OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ROLLBACK_STRATEGY_BOUNDARY_FAILED", "REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ROLLBACK_STRATEGY_FIXES", "FIX_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_ROLLBACK_STRATEGY"),
)

_SPECS = {
    key: (fn, getattr(m, cls), getattr(Risk, risk), getattr(Decision, decision), getattr(Recommendation, recommendation))
    for key, fn, cls, risk, decision, recommendation in _SPEC_DATA
}


def _coerce_input(data):
    if data is None:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateInput()
    if isinstance(data, m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateInput):
        return data
    allowed = {field.name for field in fields(m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateInput)}
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateInput(**{key: value for key, value in dict(data).items() if key in allowed})


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


def _plan(data):
    return data.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_plan


def validate_offline_runner_implementation_plan_approval(data) -> bool:
    data = _coerce_input(data)
    plan = _plan(data)
    if plan is None or data.offline_runner_implementation_plan_approved is False:
        return False
    approved = data.offline_runner_implementation_plan_approved is True or _contains(
        (_get(plan, "state"), _get(plan, "decision")),
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN",
    )
    return approved and not _as_tuple(_get(plan, "risks", ())) and _get(plan, "offline_only", True) is True


def _checks(data) -> dict[str, bool]:
    return {
        "offline_only": data.offline_mode_enforced is True,
        "sandbox_only": data.sandbox_mode_enforced is True,
        "implementation_safety_gate_only": data.implementation_safety_gate_only is True and data.real_execution_requested is not True,
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
        "stop_conditions_validated": True,
        "audit_validated": True,
        "test_strategy_validated": data.test_strategy_required is True,
        "rollback_strategy_validated": data.rollback_strategy_required is True,
    }


def _validate(data, key: str):
    data = _coerce_input(data)
    _fn, cls, risk, _decision, _recommendation = _SPECS[key]
    checks = _checks(data)
    passed = _get(data, f"offline_runner_implementation_safety_{key}_valid") is True and all(checks.values())
    return cls(
        name=key,
        score=_metric_score(_get(data, f"{key}_score"), _get(_get(_plan(data), key), "score"), passed),
        passed=passed,
        risks=() if passed else (risk,),
        details=("offline implementation safety boundary validated without creating or executing a runner",),
        **checks,
    )


def _make_validate(key: str):
    def validate(data):
        return _validate(data, key)

    validate.__name__ = _SPECS[key][0]
    return validate


for _key, _spec in _SPECS.items():
    globals()[_spec[0]] = _make_validate(_key)


def _boundaries(data):
    return {key: _validate(data, key) for key in _SPECS}


def _offline_boundary(data) -> bool:
    checks = _checks(data)
    return all(checks.values()) and data.no_external_ml is True and data.no_external_llm is True and data.no_live_execution is True


def _data_boundary(data) -> bool:
    return data.data_access_requested is not True and not _contains(_get(_plan(data), "risks", ()), "DATA_ACCESS", "DATA/")


def compute_offline_runner_implementation_safety_gate_score(data, boundaries: Mapping[str, Any] | None = None) -> m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateScore:
    data = _coerce_input(data)
    boundaries = dict(boundaries or _boundaries(data))
    approved = validate_offline_runner_implementation_plan_approval(data)
    plan_score = _metric_score(
        data.implementation_plan_score,
        _get(_get(_plan(data), "score"), "overall_score") if approved else None,
        approved,
    )
    values = {key: _get(value, "score", 0) for key, value in boundaries.items()}
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateScore(
        overall_score=_average((plan_score, *values.values())),
        implementation_plan_score=plan_score,
        **{f"{key}_score": value for key, value in values.items()},
    )


def detect_offline_runner_implementation_safety_gate_risks(data, boundaries: Mapping[str, Any] | None = None) -> tuple[Risk, ...]:
    data = _coerce_input(data)
    boundaries = dict(boundaries or _boundaries(data))
    risks: list[Risk] = []
    if not validate_offline_runner_implementation_plan_approval(data):
        risks.append(Risk.OFFLINE_RUNNER_IMPLEMENTATION_PLAN_NOT_APPROVED)
    for boundary in boundaries.values():
        risks.extend(_as_tuple(_get(boundary, "risks", ())))
    if not _offline_boundary(data):
        risks.append(Risk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(Risk.DATA_ACCESS_VIOLATION)
    if data.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_requested is True:
        risks.append(Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION)
    return _dedupe(risks)


def generate_offline_runner_implementation_safety_gate_recommendations(data, risks: Iterable[Risk] | None = None) -> tuple[Recommendation, ...]:
    risks = tuple(risks if risks is not None else detect_offline_runner_implementation_safety_gate_risks(data))
    if not risks:
        return (
            Recommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE_SUITE,
            Recommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION,
        )
    recommendations = [Recommendation.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION]
    if Risk.OFFLINE_RUNNER_IMPLEMENTATION_PLAN_NOT_APPROVED in risks:
        recommendations.append(Recommendation.APPROVE_OFFLINE_RUNNER_IMPLEMENTATION_PLAN_FIRST)
    if Risk.REAL_EXECUTION_BOUNDARY_VIOLATION in risks:
        recommendations.append(Recommendation.RESTORE_OFFLINE_BOUNDARIES)
    if Risk.DATA_ACCESS_VIOLATION in risks:
        recommendations.append(Recommendation.REMOVE_DATA_ACCESS)
    if Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION in risks:
        recommendations.append(Recommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION)
    for risk in risks:
        for _key, (_fn, _cls, spec_risk, _decision, recommendation) in _SPECS.items():
            if risk is spec_risk:
                recommendations.append(recommendation)
                break
    return _dedupe(recommendations)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE
    if any(risk in {Risk.REAL_EXECUTION_BOUNDARY_VIOLATION, Risk.DATA_ACCESS_VIOLATION, Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION} for risk in risks):
        return Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE
    if risks[0] is Risk.OFFLINE_RUNNER_IMPLEMENTATION_PLAN_NOT_APPROVED:
        return Decision.REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_PLAN_FIXES
    for _key, (_fn, _cls, risk, decision, _recommendation) in _SPECS.items():
        if risks[0] is risk:
            return decision
    return Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE


def _state_for(data, risks: tuple[Risk, ...], score):
    if _plan(data) is None:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateState.OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE_INPUT_INVALID
    if not risks and score.overall_score >= 85:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION
    if risks:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateState.OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE_BLOCKED
    if score.overall_score >= 70:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateState.OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE_COMPLETED_WITH_WARNINGS
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateState.NOT_READY


def render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate_markdown(result) -> str:
    risks = ", ".join(_value(risk) for risk in result.risks) or "none"
    recommendations = ", ".join(_value(recommendation) for recommendation in result.recommendations) or "none"
    return "\n".join((
        "# Paper Broker Read-Only Connection Dry Run Controlled Offline Runner Implementation Safety Gate",
        f"- State: {_value(result.state)}",
        f"- Decision: {_value(result.decision)}",
        f"- Score: {result.score.overall_score}",
        f"- Risks: {risks}",
        f"- Recommendations: {recommendations}",
        "- Boundary: implementation safety gate only; no executable runner creation, no runner execution, no dry-run, no broker connection, no secrets, no network, no orders, no position mutation, no data access.",
        f"- Next phase: {result.next_phase}",
    ))


def evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate(data=None):
    data = _coerce_input(data)
    boundaries = _boundaries(data)
    score = compute_offline_runner_implementation_safety_gate_score(data, boundaries)
    risks = detect_offline_runner_implementation_safety_gate_risks(data, boundaries)
    recommendations = generate_offline_runner_implementation_safety_gate_recommendations(data, risks)
    result = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateResult(
        state=_state_for(data, risks, score),
        decision=_decision_for(risks),
        score=score,
        risks=risks,
        recommendations=recommendations,
        summary="Offline runner implementation safety gate approved for implementation preparation" if not risks else "Offline runner implementation safety gate blocked",
        offline_only=True,
        sandbox_only=True,
        implementation_safety_gate_only=True,
        runner_created=False,
        runner_executed=False,
        dry_run_executed=False,
        boundaries=tuple(boundaries.values()),
        **boundaries,
    )
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateResult(
        **{**result.__dict__, "markdown_report": render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate_markdown(result)}
    )
