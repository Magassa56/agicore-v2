"""Implementation plan for a controlled offline read-only paper broker dry-run runner."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading import paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_plan_models as m

Risk = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanRisk
Decision = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanDecision
Recommendation = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanRecommendation


def _coerce_input(data):
    if data is None:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanInput()
    if isinstance(data, m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanInput):
        return data
    allowed = {field.name for field in fields(m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanInput)}
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanInput(**{key: value for key, value in dict(data).items() if key in allowed})


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


def _gate(data):
    return data.paper_broker_read_only_connection_dry_run_controlled_offline_runner_final_safety_gate


def validate_final_offline_runner_safety_gate_approval(data) -> bool:
    data = _coerce_input(data)
    gate = _gate(data)
    if gate is None or data.final_offline_runner_safety_gate_approved is False:
        return False
    approved = data.final_offline_runner_safety_gate_approved is True or _contains(
        (_get(gate, "state"), _get(gate, "decision")),
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_FINAL_SAFETY_GATE",
    )
    return approved and not _as_tuple(_get(gate, "risks", ())) and _get(gate, "offline_only", True) is True


_SPECS = {
    "implementation_scope": ("define_offline_runner_implementation_scope", m.OfflineRunnerImplementationScope, Risk.OFFLINE_RUNNER_IMPLEMENTATION_SCOPE_UNCLEAR, Decision.REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SCOPE_FIXES, Recommendation.FIX_OFFLINE_RUNNER_IMPLEMENTATION_SCOPE),
    "implementation_architecture": ("define_offline_runner_implementation_architecture", m.OfflineRunnerImplementationArchitecture, Risk.OFFLINE_RUNNER_IMPLEMENTATION_ARCHITECTURE_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_ARCHITECTURE_FIXES, Recommendation.FIX_OFFLINE_RUNNER_IMPLEMENTATION_ARCHITECTURE),
    "implementation_sequence": ("define_offline_runner_implementation_sequence", m.OfflineRunnerImplementationSequence, Risk.OFFLINE_RUNNER_IMPLEMENTATION_SEQUENCE_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SEQUENCE_FIXES, Recommendation.FIX_OFFLINE_RUNNER_IMPLEMENTATION_SEQUENCE),
    "runtime_contract": ("define_offline_runner_runtime_contract", m.OfflineRunnerRuntimeContract, Risk.OFFLINE_RUNNER_RUNTIME_CONTRACT_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_RUNTIME_CONTRACT_FIXES, Recommendation.FIX_OFFLINE_RUNNER_RUNTIME_CONTRACT),
    "input_adapter_contract": ("define_offline_runner_input_adapter_contract", m.OfflineRunnerInputAdapterContract, Risk.OFFLINE_RUNNER_INPUT_ADAPTER_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_INPUT_ADAPTER_FIXES, Recommendation.FIX_OFFLINE_RUNNER_INPUT_ADAPTER),
    "synthetic_market_context_adapter": ("define_offline_runner_synthetic_market_context_adapter", m.OfflineRunnerSyntheticMarketContextAdapter, Risk.OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_ADAPTER_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_ADAPTER_FIXES, Recommendation.FIX_OFFLINE_RUNNER_SYNTHETIC_MARKET_CONTEXT_ADAPTER),
    "simulated_broker_adapter_contract": ("define_offline_runner_simulated_broker_adapter_contract", m.OfflineRunnerSimulatedBrokerAdapterContract, Risk.OFFLINE_RUNNER_SIMULATED_BROKER_ADAPTER_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_SIMULATED_BROKER_ADAPTER_FIXES, Recommendation.FIX_OFFLINE_RUNNER_SIMULATED_BROKER_ADAPTER),
    "account_snapshot_adapter_contract": ("define_offline_runner_account_snapshot_adapter_contract", m.OfflineRunnerAccountSnapshotAdapterContract, Risk.OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_ADAPTER_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_ADAPTER_FIXES, Recommendation.FIX_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_ADAPTER),
    "market_data_snapshot_adapter_contract": ("define_offline_runner_market_data_snapshot_adapter_contract", m.OfflineRunnerMarketDataSnapshotAdapterContract, Risk.OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_ADAPTER_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_ADAPTER_FIXES, Recommendation.FIX_OFFLINE_RUNNER_MARKET_DATA_SNAPSHOT_ADAPTER),
    "strategy_signal_probe_contract": ("define_offline_runner_strategy_signal_probe_contract", m.OfflineRunnerStrategySignalProbeContract, Risk.OFFLINE_RUNNER_STRATEGY_SIGNAL_PROBE_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_STRATEGY_SIGNAL_PROBE_FIXES, Recommendation.FIX_OFFLINE_RUNNER_STRATEGY_SIGNAL_PROBE),
    "risk_observer_contract": ("define_offline_runner_risk_observer_contract", m.OfflineRunnerRiskObserverContract, Risk.OFFLINE_RUNNER_RISK_OBSERVER_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_RISK_OBSERVER_FIXES, Recommendation.FIX_OFFLINE_RUNNER_RISK_OBSERVER),
    "profitability_observer_contract": ("define_offline_runner_profitability_observer_contract", m.OfflineRunnerProfitabilityObserverContract, Risk.OFFLINE_RUNNER_PROFITABILITY_OBSERVER_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_PROFITABILITY_OBSERVER_FIXES, Recommendation.FIX_OFFLINE_RUNNER_PROFITABILITY_OBSERVER),
    "consistency_observer_contract": ("define_offline_runner_consistency_observer_contract", m.OfflineRunnerConsistencyObserverContract, Risk.OFFLINE_RUNNER_CONSISTENCY_OBSERVER_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_CONSISTENCY_OBSERVER_FIXES, Recommendation.FIX_OFFLINE_RUNNER_CONSISTENCY_OBSERVER),
    "journal_writer_contract": ("define_offline_runner_journal_writer_contract", m.OfflineRunnerJournalWriterContract, Risk.OFFLINE_RUNNER_JOURNAL_WRITER_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_JOURNAL_WRITER_FIXES, Recommendation.FIX_OFFLINE_RUNNER_JOURNAL_WRITER),
    "observability_contract": ("define_offline_runner_observability_contract", m.OfflineRunnerObservabilityContract, Risk.OFFLINE_RUNNER_OBSERVABILITY_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_OBSERVABILITY_FIXES, Recommendation.FIX_OFFLINE_RUNNER_OBSERVABILITY),
    "human_approval_contract": ("define_offline_runner_human_approval_contract", m.OfflineRunnerHumanApprovalContract, Risk.OFFLINE_RUNNER_HUMAN_APPROVAL_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_HUMAN_APPROVAL_FIXES, Recommendation.FIX_OFFLINE_RUNNER_HUMAN_APPROVAL),
    "stop_condition_contract": ("define_offline_runner_stop_condition_contract", m.OfflineRunnerStopConditionContract, Risk.OFFLINE_RUNNER_STOP_CONDITIONS_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_STOP_CONDITION_FIXES, Recommendation.FIX_OFFLINE_RUNNER_STOP_CONDITIONS),
    "success_criteria_contract": ("define_offline_runner_success_criteria_contract", m.OfflineRunnerSuccessCriteriaContract, Risk.OFFLINE_RUNNER_SUCCESS_CRITERIA_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_SUCCESS_FAILURE_FIXES, Recommendation.FIX_OFFLINE_RUNNER_SUCCESS_FAILURE),
    "failure_criteria_contract": ("define_offline_runner_failure_criteria_contract", m.OfflineRunnerFailureCriteriaContract, Risk.OFFLINE_RUNNER_FAILURE_CRITERIA_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_SUCCESS_FAILURE_FIXES, Recommendation.FIX_OFFLINE_RUNNER_SUCCESS_FAILURE),
    "audit_contract": ("define_offline_runner_audit_contract", m.OfflineRunnerAuditContract, Risk.OFFLINE_RUNNER_AUDIT_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_AUDIT_FIXES, Recommendation.FIX_OFFLINE_RUNNER_AUDIT),
    "go_no_go_contract": ("define_offline_runner_go_no_go_contract", m.OfflineRunnerGoNoGoContract, Risk.OFFLINE_RUNNER_GO_NO_GO_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_GO_NO_GO_FIXES, Recommendation.FIX_OFFLINE_RUNNER_GO_NO_GO),
    "abort_contract": ("define_offline_runner_abort_contract", m.OfflineRunnerAbortContract, Risk.OFFLINE_RUNNER_ABORT_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_ABORT_FIXES, Recommendation.FIX_OFFLINE_RUNNER_ABORT),
    "no_real_broker_guard": ("define_offline_runner_no_real_broker_guard", m.OfflineRunnerNoRealBrokerGuard, Risk.OFFLINE_RUNNER_REAL_BROKER_GUARD_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_NO_REAL_BROKER_GUARD_FIXES, Recommendation.FIX_OFFLINE_RUNNER_NO_REAL_BROKER_GUARD),
    "no_secret_read_guard": ("define_offline_runner_no_secret_read_guard", m.OfflineRunnerNoSecretReadGuard, Risk.OFFLINE_RUNNER_SECRET_READ_GUARD_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_NO_SECRET_READ_GUARD_FIXES, Recommendation.FIX_OFFLINE_RUNNER_NO_SECRET_READ_GUARD),
    "network_block_guard": ("define_offline_runner_network_block_guard", m.OfflineRunnerNetworkBlockGuard, Risk.OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_FIXES, Recommendation.FIX_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD),
    "http_websocket_socket_block_guard": ("define_offline_runner_http_websocket_socket_block_guard", m.OfflineRunnerNetworkBlockGuard, Risk.OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_NETWORK_BLOCK_GUARD_FIXES, Recommendation.FIX_OFFLINE_RUNNER_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD),
    "order_blocking_guard": ("define_offline_runner_order_blocking_guard", m.OfflineRunnerOrderBlockingGuard, Risk.OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_ORDER_BLOCKING_GUARD_FIXES, Recommendation.FIX_OFFLINE_RUNNER_ORDER_BLOCKING_GUARD),
    "position_mutation_blocking_guard": ("define_offline_runner_position_mutation_blocking_guard", m.OfflineRunnerPositionMutationBlockingGuard, Risk.OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD_FIXES, Recommendation.FIX_OFFLINE_RUNNER_POSITION_MUTATION_BLOCKING_GUARD),
    "data_access_guard": ("define_offline_runner_data_access_guard", m.OfflineRunnerDataAccessGuard, Risk.OFFLINE_RUNNER_DATA_ACCESS_GUARD_UNSAFE, Decision.REQUIRE_OFFLINE_RUNNER_DATA_ACCESS_GUARD_FIXES, Recommendation.FIX_OFFLINE_RUNNER_DATA_ACCESS_GUARD),
    "test_strategy": ("define_offline_runner_test_strategy", m.OfflineRunnerTestStrategy, Risk.OFFLINE_RUNNER_TEST_STRATEGY_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_TEST_STRATEGY_FIXES, Recommendation.FIX_OFFLINE_RUNNER_TEST_STRATEGY),
    "rollback_strategy": ("define_offline_runner_rollback_strategy", m.OfflineRunnerRollbackStrategy, Risk.OFFLINE_RUNNER_ROLLBACK_STRATEGY_MISSING, Decision.REQUIRE_OFFLINE_RUNNER_ROLLBACK_STRATEGY_FIXES, Recommendation.FIX_OFFLINE_RUNNER_ROLLBACK_STRATEGY),
}


def _checks(data) -> dict[str, bool]:
    return {
        "offline_only": data.offline_mode_enforced is True,
        "sandbox_only": data.sandbox_mode_enforced is True,
        "implementation_plan_only": data.implementation_plan_only is True and data.real_execution_requested is not True,
        "no_runner_created": data.no_runner_created is True and data.runner_creation_requested is not True and data.real_execution_requested is not True,
        "no_runner_execution": data.no_runner_execution is True and data.runner_execution_requested is not True and data.real_execution_requested is not True,
        "no_dry_run_execution": data.no_dry_run_execution is True and data.dry_run_requested is not True and data.dry_run_executed is not True and data.real_execution_requested is not True,
        "no_real_broker": data.no_real_broker is True and data.broker_connection_requested is not True,
        "no_secret_read": data.no_api_key_read is True and data.no_env_var_read is True and data.api_key_read_requested is not True and data.env_var_read_requested is not True and data.hardcoded_secret_detected is not True,
        "network_blocked": data.network_transport_requested is not True and data.external_api_requested is not True and data.no_external_api is True,
        "http_blocked": data.no_http_transport is True,
        "websocket_blocked": data.no_websocket_transport is True,
        "socket_blocked": data.no_socket_transport is True,
        "order_blocked": data.no_real_order is True and data.order_execution_requested is not True,
        "position_mutation_blocked": data.no_position_mutation is True and data.position_mutation_requested is not True,
        "data_access_blocked": data.data_access_requested is not True,
        "read_only": data.account_access_requested is not True,
        "simulated_only": data.no_real_broker is True,
        "observation_only": data.order_execution_requested is not True and data.position_mutation_requested is not True,
        "human_approval_required": data.human_approval_required is True,
        "stop_conditions_defined": True,
        "audit_defined": True,
    }


def _define(data, key: str):
    data = _coerce_input(data)
    _fn, cls, risk, _decision, _recommendation = _SPECS[key]
    checks = _checks(data)
    defined = _get(data, f"offline_runner_{key}_defined") is True and all(checks.values())
    return cls(
        name=key,
        score=_metric_score(_get(data, f"{key}_score"), _get(_get(_gate(data), key), "score"), defined),
        defined=defined,
        risks=() if defined else (risk,),
        details=("offline implementation plan artifact defined without creating or executing a runner",),
        **checks,
    )


def _make_define(key: str):
    def define(data):
        return _define(data, key)
    define.__name__ = _SPECS[key][0]
    return define


for _key, _spec in _SPECS.items():
    globals()[_spec[0]] = _make_define(_key)


def _artifacts(data):
    return {key: _define(data, key) for key in _SPECS}


def _offline_boundary(data) -> bool:
    checks = _checks(data)
    return all(checks.values()) and data.no_alpaca_real is True and data.no_external_ml is True and data.no_external_llm is True and data.no_live_execution is True


def _data_boundary(data) -> bool:
    return data.data_access_requested is not True and not _contains(_get(_gate(data), "risks", ()), "DATA_ACCESS", "DATA/")


def compute_offline_runner_implementation_plan_score(data, artifacts: Mapping[str, Any] | None = None) -> m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanScore:
    data = _coerce_input(data)
    artifacts = dict(artifacts or _artifacts(data))
    gate_score = _metric_score(data.final_safety_gate_score, _get(_get(_gate(data), "score"), "overall_score"), validate_final_offline_runner_safety_gate_approval(data))
    values = {key: _get(value, "score", 0) for key, value in artifacts.items()}
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanScore(
        overall_score=_average((gate_score, *values.values())),
        final_safety_gate_score=gate_score,
        **{f"{key}_score": value for key, value in values.items()},
    )


def detect_offline_runner_implementation_plan_risks(data, artifacts: Mapping[str, Any] | None = None) -> tuple[Risk, ...]:
    data = _coerce_input(data)
    artifacts = dict(artifacts or _artifacts(data))
    risks: list[Risk] = []
    if not validate_final_offline_runner_safety_gate_approval(data):
        risks.append(Risk.FINAL_OFFLINE_RUNNER_SAFETY_GATE_NOT_APPROVED)
    for artifact in artifacts.values():
        risks.extend(_as_tuple(_get(artifact, "risks", ())))
    if not _offline_boundary(data):
        risks.append(Risk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(Risk.DATA_ACCESS_VIOLATION)
    if data.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate_requested is True:
        risks.append(Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE)
    return _dedupe(risks)


def generate_offline_runner_implementation_plan_recommendations(data, risks: Iterable[Risk] | None = None) -> tuple[Recommendation, ...]:
    risks = tuple(risks if risks is not None else detect_offline_runner_implementation_plan_risks(data))
    if not risks:
        return (
            Recommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN_SUITE,
            Recommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE,
        )
    recommendations = [Recommendation.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE]
    if Risk.FINAL_OFFLINE_RUNNER_SAFETY_GATE_NOT_APPROVED in risks:
        recommendations.append(Recommendation.APPROVE_FINAL_OFFLINE_RUNNER_SAFETY_GATE_FIRST)
    if Risk.REAL_EXECUTION_BOUNDARY_VIOLATION in risks:
        recommendations.append(Recommendation.RESTORE_OFFLINE_BOUNDARIES)
    if Risk.DATA_ACCESS_VIOLATION in risks:
        recommendations.append(Recommendation.REMOVE_DATA_ACCESS)
    if Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE in risks:
        recommendations.append(Recommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE)
    for risk in risks:
        for _key, (_fn, _cls, spec_risk, _decision, recommendation) in _SPECS.items():
            if risk is spec_risk:
                recommendations.append(recommendation)
                break
    return _dedupe(recommendations)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN
    if any(risk in {Risk.REAL_EXECUTION_BOUNDARY_VIOLATION, Risk.DATA_ACCESS_VIOLATION, Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE} for risk in risks):
        return Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN
    if risks[0] is Risk.FINAL_OFFLINE_RUNNER_SAFETY_GATE_NOT_APPROVED:
        return Decision.REQUIRE_FINAL_OFFLINE_RUNNER_SAFETY_GATE_FIXES
    for _key, (_fn, _cls, risk, decision, _recommendation) in _SPECS.items():
        if risks[0] is risk:
            return decision
    return Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PLAN


def _state_for(data, risks: tuple[Risk, ...], score):
    if _gate(data) is None:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanState.OFFLINE_RUNNER_IMPLEMENTATION_PLAN_INPUT_INVALID
    if not risks and score.overall_score >= 85:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE
    if risks:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanState.OFFLINE_RUNNER_IMPLEMENTATION_PLAN_BLOCKED
    if score.overall_score >= 70:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanState.OFFLINE_RUNNER_IMPLEMENTATION_PLAN_COMPLETED_WITH_WARNINGS
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanState.NOT_READY


def render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_plan_markdown(result) -> str:
    risks = ", ".join(_value(risk) for risk in result.risks) or "none"
    recommendations = ", ".join(_value(recommendation) for recommendation in result.recommendations) or "none"
    return "\n".join((
        "# Paper Broker Read-Only Connection Dry Run Controlled Offline Runner Implementation Plan",
        f"- State: {_value(result.state)}",
        f"- Decision: {_value(result.decision)}",
        f"- Score: {result.score.overall_score}",
        f"- Risks: {risks}",
        f"- Recommendations: {recommendations}",
        "- Boundary: implementation plan only; no executable runner creation, no runner execution, no dry-run, no broker connection, no secrets, no network, no orders, no position mutation, no data access.",
        f"- Next phase: {result.next_phase}",
    ))


def evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_plan(data=None):
    data = _coerce_input(data)
    artifacts = _artifacts(data)
    score = compute_offline_runner_implementation_plan_score(data, artifacts)
    risks = detect_offline_runner_implementation_plan_risks(data, artifacts)
    recommendations = generate_offline_runner_implementation_plan_recommendations(data, risks)
    result = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanResult(
        state=_state_for(data, risks, score),
        decision=_decision_for(risks),
        score=score,
        risks=risks,
        recommendations=recommendations,
        summary="Offline runner implementation plan approved for implementation safety gate" if not risks else "Offline runner implementation plan blocked",
        offline_only=True,
        sandbox_only=True,
        implementation_plan_only=True,
        runner_created=False,
        runner_executed=False,
        dry_run_executed=False,
        artifacts=tuple(artifacts.values()),
        **artifacts,
    )
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPlanResult(
        **{**result.__dict__, "markdown_report": render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_plan_markdown(result)}
    )
