"""Offline-only safety gate for controlled offline runner implementation skeleton plan."""
from __future__ import annotations

from dataclasses import fields
from typing import Any, Iterable, Mapping

from agicore.trading import paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_safety_gate_models as m

Risk = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateRisk
Decision = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateDecision
Recommendation = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateRecommendation
_SPECS = {
    k: (fn, getattr(m, cls), getattr(Risk, risk), getattr(Decision, decision), getattr(Recommendation, f"FIX_{risk}"))
    for k, cls, risk, decision, fn in m._ITEMS
}


def _coerce_input(data):
    if data is None:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateInput()
    if isinstance(data, m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateInput):
        return data
    allowed = {
        field.name
        for field in fields(m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateInput)
    }
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateInput(
        **{k: v for k, v in dict(data).items() if k in allowed}
    )


def _value(item: Any) -> str:
    return str(getattr(item, "value", item))


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
    if isinstance(items, list | set):
        return tuple(items)
    return (items,)


def _contains(items: Any, *needles: str) -> bool:
    values = tuple(_value(item) for item in _as_tuple(items))
    return any(needle in values for needle in needles)


def _dedupe(items: Iterable[Any]) -> tuple[Any, ...]:
    seen = set()
    out = []
    for item in items:
        key = _value(item)
        if key not in seen:
            seen.add(key)
            out.append(item)
    return tuple(out)


def _clamp(value: int | float, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(round(value))))


def _average(values: Iterable[int | float | None], default: int = 0) -> int:
    vals = [float(value) for value in values if value is not None]
    return default if not vals else _clamp(sum(vals) / len(vals))


def _metric_score(explicit: int | None, fallback: Any, safe: bool) -> int:
    if not safe:
        return 0
    if explicit is not None:
        return _clamp(explicit)
    if fallback is not None:
        return _clamp(fallback)
    return 100


def _plan(data):
    return data.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_plan


def validate_offline_runner_implementation_skeleton_plan_approval(data) -> bool:
    data = _coerce_input(data)
    plan = _plan(data)
    if plan is None or data.offline_runner_implementation_skeleton_plan_approved is False:
        return False
    approved = data.offline_runner_implementation_skeleton_plan_approved is True or _contains(
        (_get(plan, "state"), _get(plan, "decision")),
        "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE",
        "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PLAN",
    )
    return (
        approved
        and not _as_tuple(_get(plan, "risks", ()))
        and _get(plan, "offline_only", True) is True
        and _get(plan, "runner_created", False) is False
    )


def _checks(data) -> dict[str, bool]:
    return {
        "offline_only": data.offline_mode_enforced is True,
        "sandbox_only": data.sandbox_mode_enforced is True,
        "skeleton_safety_gate_only": data.skeleton_safety_gate_only is True and data.real_execution_requested is not True,
        "no_runner_created": data.no_runner_created is True and data.runner_creation_requested is not True,
        "no_runner_execution": data.no_runner_execution is True and data.runner_execution_requested is not True,
        "no_dry_run_execution": data.no_dry_run_execution is True and data.dry_run_requested is not True and data.dry_run_executed is not True,
        "no_real_broker": data.no_real_broker is True and data.no_broker_connection is True and data.no_alpaca_real is True and data.broker_connection_requested is not True,
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
        "stub_only": data.stubs_only is True and data.runner_creation_requested is not True,
        "observation_only": data.order_execution_requested is not True and data.position_mutation_requested is not True,
        "human_approval_required": data.human_approval_required is True,
        "stop_conditions_safe": True,
        "audit_safe": True,
        "test_strategy_safe": data.test_strategy_required is True,
        "rollback_strategy_safe": data.rollback_strategy_required is True,
        "readiness_criteria_safe": data.readiness_criteria_required is True,
    }


def _validate(data, key: str):
    data = _coerce_input(data)
    fn, cls, risk, _decision, _recommendation = _SPECS[key]
    checks = _checks(data)
    safe = _get(data, f"offline_runner_{key}_safe") is True and all(checks.values())
    return cls(
        name=fn,
        score=_metric_score(_get(data, f"{key}_score"), _get(_get(_plan(data), key), "score"), safe),
        safe=safe,
        risks=() if safe else (risk,),
        details=("offline skeleton safety boundary validated without creating or executing a runner",),
        **checks,
    )


def _make_validate(key: str):
    def validate(data=None):
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


def compute_offline_runner_skeleton_safety_gate_score(
    data, boundaries: Mapping[str, Any] | None = None
) -> m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateScore:
    data = _coerce_input(data)
    boundaries = dict(boundaries or _boundaries(data))
    approved = validate_offline_runner_implementation_skeleton_plan_approval(data)
    plan_score = _metric_score(
        data.implementation_skeleton_plan_score,
        _get(_get(_plan(data), "score"), "overall_score") if approved else None,
        approved,
    )
    vals = {key: _get(value, "score", 0) for key, value in boundaries.items()}
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateScore(
        overall_score=_average((plan_score, *vals.values())),
        implementation_skeleton_plan_score=plan_score,
        **{f"{key}_score": value for key, value in vals.items()},
    )


def detect_offline_runner_skeleton_safety_gate_risks(data, boundaries: Mapping[str, Any] | None = None) -> tuple[Risk, ...]:
    data = _coerce_input(data)
    boundaries = dict(boundaries or _boundaries(data))
    risks = []
    if not validate_offline_runner_implementation_skeleton_plan_approval(data):
        risks.append(Risk.OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PLAN_NOT_APPROVED)
    for boundary in boundaries.values():
        risks.extend(_as_tuple(_get(boundary, "risks", ())))
    if not _offline_boundary(data):
        risks.append(Risk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(Risk.DATA_ACCESS_VIOLATION)
    if data.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_preparation_requested is True:
        risks.append(Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION)
    return _dedupe(risks)


def generate_offline_runner_skeleton_safety_gate_recommendations(
    data, risks: Iterable[Risk] | None = None
) -> tuple[Recommendation, ...]:
    risks = tuple(risks if risks is not None else detect_offline_runner_skeleton_safety_gate_risks(data))
    if not risks:
        return (
            Recommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE_SUITE,
            Recommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION,
        )
    recs = [Recommendation.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION]
    if Risk.OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PLAN_NOT_APPROVED in risks:
        recs.append(Recommendation.APPROVE_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PLAN_FIRST)
    for risk in risks:
        name = f"FIX_{_value(risk)}"
        if hasattr(Recommendation, name):
            recs.append(getattr(Recommendation, name))
    if Risk.REAL_EXECUTION_BOUNDARY_VIOLATION in risks:
        recs.append(Recommendation.RESTORE_OFFLINE_BOUNDARIES)
    if Risk.DATA_ACCESS_VIOLATION in risks:
        recs.append(Recommendation.REMOVE_DATA_ACCESS)
    if Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION in risks:
        recs.append(Recommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION)
    return _dedupe(recs)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE
    if any(
        risk
        in {
            Risk.REAL_EXECUTION_BOUNDARY_VIOLATION,
            Risk.DATA_ACCESS_VIOLATION,
            Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION,
        }
        for risk in risks
    ):
        return Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE
    if risks[0] is Risk.OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PLAN_NOT_APPROVED:
        return Decision.REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PLAN_FIXES
    for _key, (_fn, _cls, risk, decision, _rec) in _SPECS.items():
        if risks[0] is risk:
            return decision
    return Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE


def _state_for(data, risks: tuple[Risk, ...], score):
    if Risk.OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PLAN_NOT_APPROVED in risks:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateState.OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE_INPUT_INVALID
    if not risks and score.overall_score >= 100:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION
    if risks:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateState.OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE_BLOCKED
    if score.overall_score >= 70:
        return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateState.OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE_COMPLETED_WITH_WARNINGS
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateState.NOT_READY


def render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_safety_gate_markdown(result) -> str:
    result = (
        evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_safety_gate(result)
        if not hasattr(result, "decision")
        else result
    )
    risks = ", ".join(_value(r) for r in result.risks) or "none"
    recs = ", ".join(_value(r) for r in result.recommendations) or "none"
    return "\n".join(
        (
            "# Paper Broker Read-Only Connection Dry Run Controlled Offline Runner Implementation Skeleton Safety Gate",
            f"- State: {_value(result.state)}",
            f"- Decision: {_value(result.decision)}",
            f"- Score: {result.score.overall_score}",
            f"- Risks: {risks}",
            f"- Recommendations: {recs}",
            "- Boundary: skeleton safety gate only; stub contracts only; no executable runner creation, no runner execution, no dry-run, no broker connection, no secrets, no network, no orders, no position mutation, no data access.",
            f"- Next phase: {result.next_phase}",
        )
    )


def evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_safety_gate(data=None):
    data = _coerce_input(data)
    boundaries = _boundaries(data)
    score = compute_offline_runner_skeleton_safety_gate_score(data, boundaries)
    risks = detect_offline_runner_skeleton_safety_gate_risks(data, boundaries)
    recommendations = generate_offline_runner_skeleton_safety_gate_recommendations(data, risks)
    result = m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateResult(
        state=_state_for(data, risks, score),
        decision=_decision_for(risks),
        score=score,
        risks=risks,
        recommendations=recommendations,
        summary="Offline runner implementation skeleton safety gate approved for skeleton preparation"
        if not risks
        else "Offline runner implementation skeleton safety gate blocked",
        offline_only=True,
        sandbox_only=True,
        skeleton_safety_gate_only=True,
        runner_created=False,
        runner_executed=False,
        dry_run_executed=False,
        boundaries=boundaries,
        **boundaries,
    )
    return m.PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateResult(
        **{
            **result.__dict__,
            "markdown_report": render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_safety_gate_markdown(result),
        }
    )


__all__ = [
    "evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_safety_gate",
    "validate_offline_runner_implementation_skeleton_plan_approval",
    "compute_offline_runner_skeleton_safety_gate_score",
    "detect_offline_runner_skeleton_safety_gate_risks",
    "generate_offline_runner_skeleton_safety_gate_recommendations",
    "render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_safety_gate_markdown",
] + [fn for fn, _c, _r, _d, _rec in _SPECS.values()]
