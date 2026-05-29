"""Offline paper dry run simulation verifier for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_dry_run_models import (
    PaperDryRunFlowResult,
    PaperDryRunInput,
    PaperDryRunRecommendation,
    PaperDryRunResult,
    PaperDryRunRisk,
    PaperDryRunScore,
    PaperDryRunState,
    PaperDryRunTrace,
)


def _coerce_input(data: PaperDryRunInput | Mapping[str, Any]) -> PaperDryRunInput:
    if isinstance(data, PaperDryRunInput):
        return data
    return PaperDryRunInput(**dict(data))


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


def _clamp(value: int | float, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(round(value))))


def _average(values: Iterable[int | float | None], default: int = 0) -> int:
    usable = [float(value) for value in values if value is not None]
    if not usable:
        return default
    return _clamp(sum(usable) / len(usable))


def _weighted_average(values: Iterable[tuple[int | float | None, float]], default: int = 0) -> int:
    usable = [(float(value), weight) for value, weight in values if value is not None and weight > 0]
    if not usable:
        return default
    total_weight = sum(weight for _, weight in usable)
    return _clamp(sum(value * weight for value, weight in usable) / total_weight)


def _score(obj: Any, *names: str, default: int | None = None) -> int | None:
    for name in names:
        value = _get(obj, name)
        if isinstance(value, (int, float)):
            return _clamp(value)
    return default


def _bool_score(value: bool | None, unknown: int = 45) -> int:
    if value is True:
        return 100
    if value is False:
        return 0
    return unknown


def _dedupe(items: Iterable[Any]) -> tuple[Any, ...]:
    seen: set[Any] = set()
    result: list[Any] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return tuple(result)


def _upstream_items(data: PaperDryRunInput) -> tuple[Any, ...]:
    return (
        data.paper_trading_end_to_end,
        data.alpaca_paper_adapter,
        data.paper_broker_adapter,
        data.supervised_paper_session,
        data.human_validated_paper_session,
        data.controlled_paper_run,
        data.paper_execution_loop_readiness,
        data.paper_runtime_preparation,
        data.observability_verification,
        data.rollback_verification,
        data.kill_switch_verification,
    )


def _upstream_risks(data: PaperDryRunInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperDryRunInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _upstream_score(data: PaperDryRunInput, *names: str) -> int | None:
    values: list[int] = []
    for item in _upstream_items(data):
        values.extend(_score(item, name) for name in names)
        breakdown = _get(item, "score_breakdown")
        values.extend(_score(breakdown, name) for name in names)
    values = [value for value in values if value is not None]
    return _average(values) if values else None


def simulate_signal_flow(data: PaperDryRunInput | Mapping[str, Any]) -> PaperDryRunFlowResult:
    data = _coerce_input(data)
    score = _clamp(data.signal_flow_score) if data.signal_flow_score is not None else _average(
        (
            _bool_score(data.signal_event_available),
            _bool_score(data.signal_payload_valid),
            _bool_score(data.signal_timestamp_present),
            _bool_score(data.signal_flow_repeatable),
            _upstream_score(data, "signal_pipeline_score", "signal_flow_score"),
        ),
        default=45,
    )
    risks: list[PaperDryRunRisk] = []
    if (
        data.signal_event_available is not True
        or data.signal_payload_valid is not True
        or data.signal_timestamp_present is not True
        or score < 85
        or _has_upstream_risk(data, "SIGNAL")
    ):
        risks.append(PaperDryRunRisk.SIGNAL_FLOW_FAILURE)
    if data.signal_flow_repeatable is not True:
        risks.append(PaperDryRunRisk.DRY_RUN_NOT_REPEATABLE)
    events = (
        f"signal_flow_score={score}/100",
        f"signal_event_available={data.signal_event_available}",
        f"signal_payload_valid={data.signal_payload_valid}",
        f"signal_timestamp_present={data.signal_timestamp_present}",
        f"signal_flow_repeatable={data.signal_flow_repeatable}",
    )
    return PaperDryRunFlowResult("signal_flow", score, not risks and score >= 85, _dedupe(risks), events)


def simulate_decision_flow(data: PaperDryRunInput | Mapping[str, Any]) -> PaperDryRunFlowResult:
    data = _coerce_input(data)
    score = _clamp(data.decision_flow_score) if data.decision_flow_score is not None else _average(
        (
            _bool_score(data.decision_generated),
            _bool_score(data.decision_uses_signal),
            _bool_score(data.decision_deterministic),
            _bool_score(data.decision_trace_available),
            _upstream_score(data, "decision_pipeline_score", "decision_flow_score"),
        ),
        default=45,
    )
    risks: list[PaperDryRunRisk] = []
    if (
        data.decision_generated is not True
        or data.decision_uses_signal is not True
        or data.decision_trace_available is not True
        or score < 85
        or _has_upstream_risk(data, "DECISION")
    ):
        risks.append(PaperDryRunRisk.DECISION_FLOW_FAILURE)
    if data.decision_deterministic is not True:
        risks.append(PaperDryRunRisk.STATE_DRIFT_DETECTED)
    events = (
        f"decision_flow_score={score}/100",
        f"decision_generated={data.decision_generated}",
        f"decision_uses_signal={data.decision_uses_signal}",
        f"decision_deterministic={data.decision_deterministic}",
        f"decision_trace_available={data.decision_trace_available}",
    )
    return PaperDryRunFlowResult("decision_flow", score, not risks and score >= 85, _dedupe(risks), events)


def simulate_safety_gate_flow(data: PaperDryRunInput | Mapping[str, Any]) -> PaperDryRunFlowResult:
    data = _coerce_input(data)
    score = _clamp(data.safety_gate_score) if data.safety_gate_score is not None else _average(
        (
            _bool_score(data.safety_gate_available),
            _bool_score(data.safety_gate_passed),
            _bool_score(data.safety_reason_recorded),
            _bool_score(data.safety_bypass_prevented),
            _upstream_score(data, "safety_pipeline_score", "safety_gate_score", "kill_switch_score"),
        ),
        default=45,
    )
    risks: list[PaperDryRunRisk] = []
    if (
        data.safety_gate_available is not True
        or data.safety_gate_passed is not True
        or data.safety_reason_recorded is not True
        or score < 85
        or _has_upstream_risk(data, "SAFETY", "KILL_SWITCH")
    ):
        risks.append(PaperDryRunRisk.SAFETY_GATE_BLOCKED)
    if data.safety_bypass_prevented is not True:
        risks.append(PaperDryRunRisk.SAFETY_BYPASS_RISK)
    events = (
        f"safety_gate_score={score}/100",
        f"safety_gate_available={data.safety_gate_available}",
        f"safety_gate_passed={data.safety_gate_passed}",
        f"safety_reason_recorded={data.safety_reason_recorded}",
        f"safety_bypass_prevented={data.safety_bypass_prevented}",
    )
    return PaperDryRunFlowResult("safety_gate_flow", score, not risks and score >= 85, _dedupe(risks), events)


def simulate_paper_order_flow(data: PaperDryRunInput | Mapping[str, Any]) -> PaperDryRunFlowResult:
    data = _coerce_input(data)
    score = _clamp(data.paper_order_flow_score) if data.paper_order_flow_score is not None else _average(
        (
            _bool_score(data.paper_order_created),
            _bool_score(data.paper_order_validated),
            _bool_score(data.paper_order_not_routed),
            _bool_score(data.paper_order_idempotent),
            _upstream_score(data, "order_pipeline_score", "adapter_score", "alpaca_adapter_score"),
        ),
        default=45,
    )
    risks: list[PaperDryRunRisk] = []
    if (
        data.paper_order_created is not True
        or data.paper_order_validated is not True
        or data.paper_order_not_routed is not True
        or score < 85
        or _has_upstream_risk(data, "ORDER", "ADAPTER", "BROKER", "API_ACCESS", "NETWORK_LEAK")
    ):
        risks.append(PaperDryRunRisk.PAPER_ORDER_SIMULATION_FAILURE)
    if data.paper_order_idempotent is not True:
        risks.append(PaperDryRunRisk.DRY_RUN_NOT_REPEATABLE)
    events = (
        f"paper_order_flow_score={score}/100",
        f"paper_order_created={data.paper_order_created}",
        f"paper_order_validated={data.paper_order_validated}",
        f"paper_order_not_routed={data.paper_order_not_routed}",
        f"paper_order_idempotent={data.paper_order_idempotent}",
    )
    return PaperDryRunFlowResult("paper_order_flow", score, not risks and score >= 85, _dedupe(risks), events)


def simulate_position_update_flow(data: PaperDryRunInput | Mapping[str, Any]) -> PaperDryRunFlowResult:
    data = _coerce_input(data)
    score = _clamp(data.position_update_score) if data.position_update_score is not None else _average(
        (
            _bool_score(data.position_updated),
            _bool_score(data.position_reconciled),
            _bool_score(data.position_checkpointed),
            _bool_score(data.pnl_computed),
            _upstream_score(data, "position_pipeline_score", "position_update_score"),
        ),
        default=45,
    )
    risks: list[PaperDryRunRisk] = []
    if (
        data.position_updated is not True
        or data.position_reconciled is not True
        or data.pnl_computed is not True
        or score < 85
        or _has_upstream_risk(data, "POSITION")
    ):
        risks.append(PaperDryRunRisk.POSITION_UPDATE_FAILURE)
    if data.position_checkpointed is not True:
        risks.append(PaperDryRunRisk.STATE_DRIFT_DETECTED)
    events = (
        f"position_update_score={score}/100",
        f"position_updated={data.position_updated}",
        f"position_reconciled={data.position_reconciled}",
        f"position_checkpointed={data.position_checkpointed}",
        f"pnl_computed={data.pnl_computed}",
    )
    return PaperDryRunFlowResult("position_update_flow", score, not risks and score >= 85, _dedupe(risks), events)


def simulate_journal_flow(data: PaperDryRunInput | Mapping[str, Any]) -> PaperDryRunFlowResult:
    data = _coerce_input(data)
    score = _clamp(data.journal_flow_score) if data.journal_flow_score is not None else _average(
        (
            _bool_score(data.journal_entry_written),
            _bool_score(data.journal_links_order_position),
            _bool_score(data.journal_audit_trail_complete),
            _bool_score(data.journal_repeatable),
            _upstream_score(data, "journal_pipeline_score", "journal_flow_score"),
        ),
        default=45,
    )
    risks: list[PaperDryRunRisk] = []
    if (
        data.journal_entry_written is not True
        or data.journal_links_order_position is not True
        or data.journal_audit_trail_complete is not True
        or score < 85
        or _has_upstream_risk(data, "JOURNAL", "AUDIT")
    ):
        risks.append(PaperDryRunRisk.JOURNAL_WRITE_FAILURE)
    if data.journal_repeatable is not True:
        risks.append(PaperDryRunRisk.DRY_RUN_NOT_REPEATABLE)
    events = (
        f"journal_flow_score={score}/100",
        f"journal_entry_written={data.journal_entry_written}",
        f"journal_links_order_position={data.journal_links_order_position}",
        f"journal_audit_trail_complete={data.journal_audit_trail_complete}",
        f"journal_repeatable={data.journal_repeatable}",
    )
    return PaperDryRunFlowResult("journal_flow", score, not risks and score >= 85, _dedupe(risks), events)


def simulate_observability_flow(data: PaperDryRunInput | Mapping[str, Any]) -> PaperDryRunFlowResult:
    data = _coerce_input(data)
    score = _clamp(data.observability_flow_score) if data.observability_flow_score is not None else _average(
        (
            _bool_score(data.observability_event_emitted),
            _bool_score(data.metrics_recorded),
            _bool_score(data.trace_recorded),
            _bool_score(data.result_visible),
            _bool_score(data.state_reconciled),
            _upstream_score(data, "observability_pipeline_score", "observability_score"),
        ),
        default=45,
    )
    risks: list[PaperDryRunRisk] = []
    if (
        data.observability_event_emitted is not True
        or data.metrics_recorded is not True
        or data.trace_recorded is not True
        or data.result_visible is not True
        or score < 85
        or _has_upstream_risk(data, "OBSERVABILITY")
    ):
        risks.append(PaperDryRunRisk.OBSERVABILITY_EVENT_MISSING)
    if data.state_reconciled is not True or _has_upstream_risk(data, "DRIFT"):
        risks.append(PaperDryRunRisk.STATE_DRIFT_DETECTED)
    events = (
        f"observability_flow_score={score}/100",
        f"observability_event_emitted={data.observability_event_emitted}",
        f"metrics_recorded={data.metrics_recorded}",
        f"trace_recorded={data.trace_recorded}",
        f"result_visible={data.result_visible}",
        f"state_reconciled={data.state_reconciled}",
    )
    return PaperDryRunFlowResult("observability_flow", score, not risks and score >= 85, _dedupe(risks), events)


def detect_dry_run_risks(
    data: PaperDryRunInput | Mapping[str, Any],
    signal_flow: PaperDryRunFlowResult | None = None,
    decision_flow: PaperDryRunFlowResult | None = None,
    safety_gate_flow: PaperDryRunFlowResult | None = None,
    paper_order_flow: PaperDryRunFlowResult | None = None,
    position_update_flow: PaperDryRunFlowResult | None = None,
    journal_flow: PaperDryRunFlowResult | None = None,
    observability_flow: PaperDryRunFlowResult | None = None,
) -> tuple[PaperDryRunRisk, ...]:
    data = _coerce_input(data)
    flows = (
        signal_flow or simulate_signal_flow(data),
        decision_flow or simulate_decision_flow(data),
        safety_gate_flow or simulate_safety_gate_flow(data),
        paper_order_flow or simulate_paper_order_flow(data),
        position_update_flow or simulate_position_update_flow(data),
        journal_flow or simulate_journal_flow(data),
        observability_flow or simulate_observability_flow(data),
    )
    risks: list[PaperDryRunRisk] = []
    for flow in flows:
        risks.extend(flow.risks)
    if data.dry_run_repeatable is not True:
        risks.append(PaperDryRunRisk.DRY_RUN_NOT_REPEATABLE)
    if data.offline_mode_enforced is not True or _has_upstream_risk(data, "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK", "BROKER"):
        risks.append(PaperDryRunRisk.PAPER_ORDER_SIMULATION_FAILURE)
    return _dedupe(risks)


def compute_dry_run_score(
    data: PaperDryRunInput | Mapping[str, Any],
    risks: tuple[PaperDryRunRisk, ...] = (),
    signal_flow: PaperDryRunFlowResult | None = None,
    decision_flow: PaperDryRunFlowResult | None = None,
    safety_gate_flow: PaperDryRunFlowResult | None = None,
    paper_order_flow: PaperDryRunFlowResult | None = None,
    position_update_flow: PaperDryRunFlowResult | None = None,
    journal_flow: PaperDryRunFlowResult | None = None,
    observability_flow: PaperDryRunFlowResult | None = None,
) -> PaperDryRunScore:
    data = _coerce_input(data)
    signal = signal_flow or simulate_signal_flow(data)
    decision = decision_flow or simulate_decision_flow(data)
    safety = safety_gate_flow or simulate_safety_gate_flow(data)
    order = paper_order_flow or simulate_paper_order_flow(data)
    position = position_update_flow or simulate_position_update_flow(data)
    journal = journal_flow or simulate_journal_flow(data)
    observability = observability_flow or simulate_observability_flow(data)
    weighted = _weighted_average(
        (
            (signal.score, 1.1),
            (decision.score, 1.15),
            (safety.score, 1.35),
            (order.score, 1.25),
            (position.score, 1.05),
            (journal.score, 0.95),
            (observability.score, 1.1),
        )
    )
    penalty = min(70, len(set(risks)) * 6)
    overall = _clamp(weighted - penalty)
    critical_caps = {
        PaperDryRunRisk.SIGNAL_FLOW_FAILURE: 50,
        PaperDryRunRisk.DECISION_FLOW_FAILURE: 50,
        PaperDryRunRisk.SAFETY_GATE_BLOCKED: 40,
        PaperDryRunRisk.PAPER_ORDER_SIMULATION_FAILURE: 45,
        PaperDryRunRisk.SAFETY_BYPASS_RISK: 40,
    }
    for risk, cap in critical_caps.items():
        if risk in risks:
            overall = min(overall, cap)
    return PaperDryRunScore(
        overall_score=overall,
        signal_flow_score=signal.score,
        decision_flow_score=decision.score,
        safety_gate_score=safety.score,
        paper_order_flow_score=order.score,
        position_update_score=position.score,
        journal_flow_score=journal.score,
        observability_flow_score=observability.score,
    )


def _build_trace(risks: tuple[PaperDryRunRisk, ...]) -> PaperDryRunTrace:
    steps = ("signal", "decision", "safety_gate", "paper_order", "position_update", "journal", "observability", "result")
    blocked: list[str] = []
    if PaperDryRunRisk.SIGNAL_FLOW_FAILURE in risks:
        blocked.append("signal")
    if PaperDryRunRisk.DECISION_FLOW_FAILURE in risks:
        blocked.append("decision")
    if PaperDryRunRisk.SAFETY_GATE_BLOCKED in risks or PaperDryRunRisk.SAFETY_BYPASS_RISK in risks:
        blocked.append("safety_gate")
    if PaperDryRunRisk.PAPER_ORDER_SIMULATION_FAILURE in risks:
        blocked.append("paper_order")
    if PaperDryRunRisk.POSITION_UPDATE_FAILURE in risks:
        blocked.append("position_update")
    if PaperDryRunRisk.JOURNAL_WRITE_FAILURE in risks:
        blocked.append("journal")
    if PaperDryRunRisk.OBSERVABILITY_EVENT_MISSING in risks or PaperDryRunRisk.STATE_DRIFT_DETECTED in risks:
        blocked.append("observability")
    completed = tuple(step for step in steps if step not in blocked)
    return PaperDryRunTrace(steps, completed, _dedupe(blocked))


def _select_state(score: int, risks: tuple[PaperDryRunRisk, ...], dry_run_executed: bool | None, ready_for_trial: bool | None) -> PaperDryRunState:
    hard = {
        PaperDryRunRisk.SIGNAL_FLOW_FAILURE,
        PaperDryRunRisk.DECISION_FLOW_FAILURE,
        PaperDryRunRisk.SAFETY_GATE_BLOCKED,
        PaperDryRunRisk.PAPER_ORDER_SIMULATION_FAILURE,
        PaperDryRunRisk.SAFETY_BYPASS_RISK,
    }
    count = len(set(risks))
    if hard.intersection(risks) or score < 45 or count >= 6:
        return PaperDryRunState.NOT_READY
    if count >= 3 or score < 72:
        return PaperDryRunState.REVIEW_REQUIRED
    if count:
        return PaperDryRunState.PARTIALLY_READY
    if dry_run_executed is True and ready_for_trial is True and score >= 94:
        return PaperDryRunState.READY_FOR_SUPERVISED_PAPER_TRIAL
    if dry_run_executed is True and score >= 90:
        return PaperDryRunState.DRY_RUN_COMPLETED
    if score >= 85:
        return PaperDryRunState.DRY_RUN_READY
    return PaperDryRunState.PARTIALLY_READY


def generate_dry_run_recommendations(
    risks: tuple[PaperDryRunRisk, ...],
    state: PaperDryRunState | None = None,
) -> tuple[PaperDryRunRecommendation, ...]:
    recommendations: list[PaperDryRunRecommendation] = []
    if risks:
        recommendations.append(PaperDryRunRecommendation.HOLD_SUPERVISED_TRIAL_APPROVAL)
    mapping = {
        PaperDryRunRisk.SIGNAL_FLOW_FAILURE: PaperDryRunRecommendation.REPAIR_SIGNAL_FLOW,
        PaperDryRunRisk.DECISION_FLOW_FAILURE: PaperDryRunRecommendation.REPAIR_DECISION_FLOW,
        PaperDryRunRisk.SAFETY_GATE_BLOCKED: PaperDryRunRecommendation.UNBLOCK_SAFETY_GATE,
        PaperDryRunRisk.PAPER_ORDER_SIMULATION_FAILURE: PaperDryRunRecommendation.REPAIR_PAPER_ORDER_SIMULATION,
        PaperDryRunRisk.POSITION_UPDATE_FAILURE: PaperDryRunRecommendation.REPAIR_POSITION_UPDATE,
        PaperDryRunRisk.JOURNAL_WRITE_FAILURE: PaperDryRunRecommendation.REPAIR_JOURNAL_WRITE,
        PaperDryRunRisk.OBSERVABILITY_EVENT_MISSING: PaperDryRunRecommendation.RESTORE_OBSERVABILITY_EVENT,
        PaperDryRunRisk.STATE_DRIFT_DETECTED: PaperDryRunRecommendation.RECONCILE_DRY_RUN_STATE,
        PaperDryRunRisk.DRY_RUN_NOT_REPEATABLE: PaperDryRunRecommendation.STABILIZE_REPEATABILITY,
        PaperDryRunRisk.SAFETY_BYPASS_RISK: PaperDryRunRecommendation.VERIFY_SAFETY_BYPASS_PREVENTION,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(PaperDryRunRecommendation.RUN_PAPER_DRY_RUN_SUITE)
    if state == PaperDryRunState.READY_FOR_SUPERVISED_PAPER_TRIAL:
        recommendations.append(PaperDryRunRecommendation.APPROVE_SUPERVISED_PAPER_TRIAL_AFTER_MANUAL_REVIEW)
    return _dedupe(recommendations)


def evaluate_paper_dry_run(data: PaperDryRunInput | Mapping[str, Any]) -> PaperDryRunResult:
    data = _coerce_input(data)
    signal = simulate_signal_flow(data)
    decision = simulate_decision_flow(data)
    safety = simulate_safety_gate_flow(data)
    order = simulate_paper_order_flow(data)
    position = simulate_position_update_flow(data)
    journal = simulate_journal_flow(data)
    observability = simulate_observability_flow(data)
    risks = detect_dry_run_risks(data, signal, decision, safety, order, position, journal, observability)
    score = compute_dry_run_score(data, risks, signal, decision, safety, order, position, journal, observability)
    state = _select_state(score.overall_score, risks, data.dry_run_executed, data.ready_for_supervised_paper_trial)
    trace = _build_trace(risks)
    recommendations = generate_dry_run_recommendations(risks, state)
    offline_only = data.offline_mode_enforced is True and data.paper_order_not_routed is True and not _has_upstream_risk(
        data, "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK", "BROKER"
    )
    summary = f"{state.value}: score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return PaperDryRunResult(
        state=state,
        dry_run_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        signal_flow=signal,
        decision_flow=decision,
        safety_gate_flow=safety,
        paper_order_flow=order,
        position_update_flow=position,
        journal_flow=journal,
        observability_flow=observability,
        dry_run_trace=trace,
        recommendations=recommendations,
        offline_only=offline_only,
        summary=summary,
    )


def render_paper_dry_run_markdown(result: PaperDryRunResult) -> str:
    lines = [
        "# AGIcore Paper Dry Run",
        f"- State: {result.state.value}",
        f"- Score: {result.dry_run_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Score Breakdown",
        f"- Signal: {result.score_breakdown.signal_flow_score}/100",
        f"- Decision: {result.score_breakdown.decision_flow_score}/100",
        f"- Safety gate: {result.score_breakdown.safety_gate_score}/100",
        f"- Paper order: {result.score_breakdown.paper_order_flow_score}/100",
        f"- Position update: {result.score_breakdown.position_update_score}/100",
        f"- Journal: {result.score_breakdown.journal_flow_score}/100",
        f"- Observability: {result.score_breakdown.observability_flow_score}/100",
        "",
        "# Dry Run Flows",
    ]
    flows = (
        result.signal_flow,
        result.decision_flow,
        result.safety_gate_flow,
        result.paper_order_flow,
        result.position_update_flow,
        result.journal_flow,
        result.observability_flow,
    )
    for flow in flows:
        lines.append(
            f"- {flow.name}: passed={flow.passed}, score={flow.score}/100, "
            f"risks={', '.join(risk.value for risk in flow.risks) or 'none'}"
        )
        lines.extend(f"  - {event}" for event in flow.events)
    lines.extend(
        (
            "",
            "# Dry Run Trace",
            f"- Steps: {', '.join(result.dry_run_trace.steps)}",
            f"- Completed: {', '.join(result.dry_run_trace.completed_steps) or 'none'}",
            f"- Blocked: {', '.join(result.dry_run_trace.blocked_steps) or 'none'}",
            "",
            "# Dry Run Risks",
        )
    )
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Dry Run Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_dry_run_score",
    "detect_dry_run_risks",
    "evaluate_paper_dry_run",
    "generate_dry_run_recommendations",
    "render_paper_dry_run_markdown",
    "simulate_decision_flow",
    "simulate_journal_flow",
    "simulate_observability_flow",
    "simulate_paper_order_flow",
    "simulate_position_update_flow",
    "simulate_safety_gate_flow",
    "simulate_signal_flow",
]
