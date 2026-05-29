"""Offline paper trading end-to-end readiness audit for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_trading_end_to_end_models import (
    PaperTradingEndToEndGraph,
    PaperTradingEndToEndInput,
    PaperTradingEndToEndRecommendation,
    PaperTradingEndToEndResult,
    PaperTradingEndToEndReviewSection,
    PaperTradingEndToEndRisk,
    PaperTradingEndToEndScore,
    PaperTradingEndToEndState,
)


def _coerce_input(data: PaperTradingEndToEndInput | Mapping[str, Any]) -> PaperTradingEndToEndInput:
    if isinstance(data, PaperTradingEndToEndInput):
        return data
    return PaperTradingEndToEndInput(**dict(data))


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


def _upstream_items(data: PaperTradingEndToEndInput) -> tuple[Any, ...]:
    return (
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


def _upstream_risks(data: PaperTradingEndToEndInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream(data: PaperTradingEndToEndInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _upstream_score(data: PaperTradingEndToEndInput, *names: str) -> int | None:
    values: list[int] = []
    for item in _upstream_items(data):
        values.extend(_score(item, name) for name in names)
        breakdown = _get(item, "score_breakdown")
        values.extend(_score(breakdown, name) for name in names)
    values = [value for value in values if value is not None]
    return _average(values) if values else None


def verify_signal_pipeline(data: PaperTradingEndToEndInput | Mapping[str, Any]) -> PaperTradingEndToEndReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.signal_pipeline_score) if data.signal_pipeline_score is not None else _average(
        (
            _bool_score(data.signal_input_available),
            _bool_score(data.signal_validation_available),
            _bool_score(data.signal_context_attached),
            _bool_score(data.signal_to_decision_linked),
            _upstream_score(data, "signal_input_score"),
        ),
        default=45,
    )
    risks: list[PaperTradingEndToEndRisk] = []
    if (
        data.signal_input_available is not True
        or data.signal_validation_available is not True
        or data.signal_context_attached is not True
        or data.signal_to_decision_linked is not True
        or score < 85
    ):
        risks.append(PaperTradingEndToEndRisk.SIGNAL_PIPELINE_FAILURE)
    evidence = (
        f"signal_pipeline_score={score}/100",
        f"signal_input_available={data.signal_input_available}",
        f"signal_validation_available={data.signal_validation_available}",
        f"signal_context_attached={data.signal_context_attached}",
        f"signal_to_decision_linked={data.signal_to_decision_linked}",
    )
    return PaperTradingEndToEndReviewSection("signal_pipeline_review", score, not risks and score >= 85, tuple(risks), evidence)


def verify_decision_pipeline(data: PaperTradingEndToEndInput | Mapping[str, Any]) -> PaperTradingEndToEndReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.decision_pipeline_score) if data.decision_pipeline_score is not None else _average(
        (
            _bool_score(data.decision_pipeline_available),
            _bool_score(data.decision_context_scored),
            _bool_score(data.decision_output_deterministic),
            _bool_score(data.decision_to_safety_linked),
            _upstream_score(data, "decision_pipeline_score"),
        ),
        default=45,
    )
    risks: list[PaperTradingEndToEndRisk] = []
    if (
        data.decision_pipeline_available is not True
        or data.decision_context_scored is not True
        or data.decision_to_safety_linked is not True
        or score < 85
    ):
        risks.append(PaperTradingEndToEndRisk.DECISION_PIPELINE_FAILURE)
    if data.decision_output_deterministic is not True:
        risks.append(PaperTradingEndToEndRisk.STATE_DRIFT_RISK)
    evidence = (
        f"decision_pipeline_score={score}/100",
        f"decision_pipeline_available={data.decision_pipeline_available}",
        f"decision_context_scored={data.decision_context_scored}",
        f"decision_output_deterministic={data.decision_output_deterministic}",
        f"decision_to_safety_linked={data.decision_to_safety_linked}",
    )
    return PaperTradingEndToEndReviewSection("decision_pipeline_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_safety_pipeline(data: PaperTradingEndToEndInput | Mapping[str, Any]) -> PaperTradingEndToEndReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.safety_pipeline_score) if data.safety_pipeline_score is not None else _average(
        (
            _bool_score(data.safety_gate_available),
            _bool_score(data.risk_precheck_available),
            _bool_score(data.kill_switch_linked),
            _bool_score(data.rollback_linked),
            _bool_score(data.safety_to_adapter_linked),
            _upstream_score(data, "kill_switch_score", "rollback_score", "safety_gate_score"),
        ),
        default=45,
    )
    risks: list[PaperTradingEndToEndRisk] = []
    if (
        data.safety_gate_available is not True
        or data.risk_precheck_available is not True
        or data.kill_switch_linked is not True
        or data.safety_to_adapter_linked is not True
        or score < 85
        or _has_upstream(data, "KILL_SWITCH", "SAFETY")
    ):
        risks.append(PaperTradingEndToEndRisk.SAFETY_GATE_FAILURE)
    if data.rollback_linked is not True or _has_upstream(data, "ROLLBACK"):
        risks.append(PaperTradingEndToEndRisk.STATE_DRIFT_RISK)
    evidence = (
        f"safety_pipeline_score={score}/100",
        f"safety_gate_available={data.safety_gate_available}",
        f"risk_precheck_available={data.risk_precheck_available}",
        f"kill_switch_linked={data.kill_switch_linked}",
        f"rollback_linked={data.rollback_linked}",
        f"safety_to_adapter_linked={data.safety_to_adapter_linked}",
    )
    return PaperTradingEndToEndReviewSection("safety_pipeline_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_adapter_pipeline(data: PaperTradingEndToEndInput | Mapping[str, Any]) -> PaperTradingEndToEndReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.adapter_pipeline_score) if data.adapter_pipeline_score is not None else _average(
        (
            _bool_score(data.paper_broker_adapter_ready),
            _bool_score(data.alpaca_paper_adapter_ready),
            _bool_score(data.adapter_offline_only),
            _bool_score(data.adapter_to_order_linked),
            _upstream_score(data, "adapter_score", "alpaca_adapter_score"),
        ),
        default=45,
    )
    risks: list[PaperTradingEndToEndRisk] = []
    if (
        data.paper_broker_adapter_ready is not True
        or data.alpaca_paper_adapter_ready is not True
        or data.adapter_to_order_linked is not True
        or score < 85
        or _has_upstream(data, "ADAPTER", "MAPPING", "TRANSLATION")
    ):
        risks.append(PaperTradingEndToEndRisk.ADAPTER_PIPELINE_FAILURE)
    if data.adapter_offline_only is not True or _has_upstream(data, "BROKER", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK"):
        risks.append(PaperTradingEndToEndRisk.END_TO_END_INCONSISTENCY)
    evidence = (
        f"adapter_pipeline_score={score}/100",
        f"paper_broker_adapter_ready={data.paper_broker_adapter_ready}",
        f"alpaca_paper_adapter_ready={data.alpaca_paper_adapter_ready}",
        f"adapter_offline_only={data.adapter_offline_only}",
        f"adapter_to_order_linked={data.adapter_to_order_linked}",
    )
    return PaperTradingEndToEndReviewSection("adapter_pipeline_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_order_pipeline(data: PaperTradingEndToEndInput | Mapping[str, Any]) -> PaperTradingEndToEndReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.order_pipeline_score) if data.order_pipeline_score is not None else _average(
        (
            _bool_score(data.paper_order_model_available),
            _bool_score(data.paper_order_validation_available),
            _bool_score(data.paper_order_translation_available),
            _bool_score(data.paper_order_idempotent),
            _upstream_score(data, "paper_order_translation_score", "order_mapping_score"),
        ),
        default=45,
    )
    risks: list[PaperTradingEndToEndRisk] = []
    if (
        data.paper_order_model_available is not True
        or data.paper_order_validation_available is not True
        or data.paper_order_translation_available is not True
        or score < 85
    ):
        risks.append(PaperTradingEndToEndRisk.ORDER_PIPELINE_FAILURE)
    if data.paper_order_idempotent is not True:
        risks.append(PaperTradingEndToEndRisk.STATE_DRIFT_RISK)
    evidence = (
        f"order_pipeline_score={score}/100",
        f"paper_order_model_available={data.paper_order_model_available}",
        f"paper_order_validation_available={data.paper_order_validation_available}",
        f"paper_order_translation_available={data.paper_order_translation_available}",
        f"paper_order_idempotent={data.paper_order_idempotent}",
    )
    return PaperTradingEndToEndReviewSection("order_pipeline_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_position_pipeline(data: PaperTradingEndToEndInput | Mapping[str, Any]) -> PaperTradingEndToEndReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.position_pipeline_score) if data.position_pipeline_score is not None else _average(
        (
            _bool_score(data.paper_position_model_available),
            _bool_score(data.paper_position_reconciliation_available),
            _bool_score(data.paper_position_checkpointed),
            _bool_score(data.position_pnl_available),
            _upstream_score(data, "paper_position_translation_score", "position_mapping_score"),
        ),
        default=45,
    )
    risks: list[PaperTradingEndToEndRisk] = []
    if (
        data.paper_position_model_available is not True
        or data.paper_position_reconciliation_available is not True
        or data.position_pnl_available is not True
        or score < 85
    ):
        risks.append(PaperTradingEndToEndRisk.POSITION_PIPELINE_FAILURE)
    if data.paper_position_checkpointed is not True:
        risks.append(PaperTradingEndToEndRisk.STATE_DRIFT_RISK)
    evidence = (
        f"position_pipeline_score={score}/100",
        f"paper_position_model_available={data.paper_position_model_available}",
        f"paper_position_reconciliation_available={data.paper_position_reconciliation_available}",
        f"paper_position_checkpointed={data.paper_position_checkpointed}",
        f"position_pnl_available={data.position_pnl_available}",
    )
    return PaperTradingEndToEndReviewSection("position_pipeline_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_journal_pipeline(data: PaperTradingEndToEndInput | Mapping[str, Any]) -> PaperTradingEndToEndReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.journal_pipeline_score) if data.journal_pipeline_score is not None else _average(
        (
            _bool_score(data.paper_journal_available),
            _bool_score(data.paper_journal_records_orders),
            _bool_score(data.paper_journal_records_positions),
            _bool_score(data.paper_journal_exports_audit),
            _upstream_score(data, "paper_journal_score"),
        ),
        default=45,
    )
    risks: list[PaperTradingEndToEndRisk] = []
    if (
        data.paper_journal_available is not True
        or data.paper_journal_records_orders is not True
        or data.paper_journal_records_positions is not True
        or data.paper_journal_exports_audit is not True
        or score < 85
    ):
        risks.append(PaperTradingEndToEndRisk.JOURNAL_PIPELINE_FAILURE)
    evidence = (
        f"journal_pipeline_score={score}/100",
        f"paper_journal_available={data.paper_journal_available}",
        f"paper_journal_records_orders={data.paper_journal_records_orders}",
        f"paper_journal_records_positions={data.paper_journal_records_positions}",
        f"paper_journal_exports_audit={data.paper_journal_exports_audit}",
    )
    return PaperTradingEndToEndReviewSection("journal_pipeline_review", score, not risks and score >= 85, tuple(risks), evidence)


def verify_observability_pipeline(data: PaperTradingEndToEndInput | Mapping[str, Any]) -> PaperTradingEndToEndReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.observability_pipeline_score) if data.observability_pipeline_score is not None else _average(
        (
            _bool_score(data.observability_events_available),
            _bool_score(data.metrics_available),
            _bool_score(data.critical_alerts_available),
            _bool_score(data.result_summary_available),
            _bool_score(data.end_to_end_state_reconciled),
            _upstream_score(data, "observability_score"),
        ),
        default=45,
    )
    risks: list[PaperTradingEndToEndRisk] = []
    if (
        data.observability_events_available is not True
        or data.metrics_available is not True
        or data.critical_alerts_available is not True
        or data.result_summary_available is not True
        or score < 85
        or _has_upstream(data, "OBSERVABILITY")
    ):
        risks.append(PaperTradingEndToEndRisk.OBSERVABILITY_FAILURE)
    if data.end_to_end_state_reconciled is not True or _has_upstream(data, "DRIFT"):
        risks.append(PaperTradingEndToEndRisk.STATE_DRIFT_RISK)
    evidence = (
        f"observability_pipeline_score={score}/100",
        f"observability_events_available={data.observability_events_available}",
        f"metrics_available={data.metrics_available}",
        f"critical_alerts_available={data.critical_alerts_available}",
        f"result_summary_available={data.result_summary_available}",
        f"end_to_end_state_reconciled={data.end_to_end_state_reconciled}",
    )
    return PaperTradingEndToEndReviewSection("observability_pipeline_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def detect_end_to_end_risks(
    data: PaperTradingEndToEndInput | Mapping[str, Any],
    signal_pipeline_review: PaperTradingEndToEndReviewSection | None = None,
    decision_pipeline_review: PaperTradingEndToEndReviewSection | None = None,
    safety_pipeline_review: PaperTradingEndToEndReviewSection | None = None,
    adapter_pipeline_review: PaperTradingEndToEndReviewSection | None = None,
    order_pipeline_review: PaperTradingEndToEndReviewSection | None = None,
    position_pipeline_review: PaperTradingEndToEndReviewSection | None = None,
    journal_pipeline_review: PaperTradingEndToEndReviewSection | None = None,
    observability_pipeline_review: PaperTradingEndToEndReviewSection | None = None,
) -> tuple[PaperTradingEndToEndRisk, ...]:
    data = _coerce_input(data)
    sections = (
        signal_pipeline_review or verify_signal_pipeline(data),
        decision_pipeline_review or verify_decision_pipeline(data),
        safety_pipeline_review or verify_safety_pipeline(data),
        adapter_pipeline_review or verify_adapter_pipeline(data),
        order_pipeline_review or verify_order_pipeline(data),
        position_pipeline_review or verify_position_pipeline(data),
        journal_pipeline_review or verify_journal_pipeline(data),
        observability_pipeline_review or verify_observability_pipeline(data),
    )
    risks: list[PaperTradingEndToEndRisk] = []
    for section in sections:
        risks.extend(section.risks)
    if data.offline_mode_enforced is not True:
        risks.append(PaperTradingEndToEndRisk.END_TO_END_INCONSISTENCY)
    return _dedupe(risks)


def compute_end_to_end_score(
    data: PaperTradingEndToEndInput | Mapping[str, Any],
    risks: tuple[PaperTradingEndToEndRisk, ...] = (),
    signal_pipeline_review: PaperTradingEndToEndReviewSection | None = None,
    decision_pipeline_review: PaperTradingEndToEndReviewSection | None = None,
    safety_pipeline_review: PaperTradingEndToEndReviewSection | None = None,
    adapter_pipeline_review: PaperTradingEndToEndReviewSection | None = None,
    order_pipeline_review: PaperTradingEndToEndReviewSection | None = None,
    position_pipeline_review: PaperTradingEndToEndReviewSection | None = None,
    journal_pipeline_review: PaperTradingEndToEndReviewSection | None = None,
    observability_pipeline_review: PaperTradingEndToEndReviewSection | None = None,
) -> PaperTradingEndToEndScore:
    data = _coerce_input(data)
    signal = signal_pipeline_review or verify_signal_pipeline(data)
    decision = decision_pipeline_review or verify_decision_pipeline(data)
    safety = safety_pipeline_review or verify_safety_pipeline(data)
    adapter = adapter_pipeline_review or verify_adapter_pipeline(data)
    order = order_pipeline_review or verify_order_pipeline(data)
    position = position_pipeline_review or verify_position_pipeline(data)
    journal = journal_pipeline_review or verify_journal_pipeline(data)
    observability = observability_pipeline_review or verify_observability_pipeline(data)
    weighted = _weighted_average(
        (
            (signal.score, 1.1),
            (decision.score, 1.15),
            (safety.score, 1.3),
            (adapter.score, 1.25),
            (order.score, 1.1),
            (position.score, 1.05),
            (journal.score, 0.95),
            (observability.score, 1.1),
        )
    )
    penalty = min(72, len(set(risks)) * 6)
    overall = _clamp(weighted - penalty)
    critical_caps = {
        PaperTradingEndToEndRisk.SIGNAL_PIPELINE_FAILURE: 50,
        PaperTradingEndToEndRisk.DECISION_PIPELINE_FAILURE: 50,
        PaperTradingEndToEndRisk.SAFETY_GATE_FAILURE: 45,
        PaperTradingEndToEndRisk.ADAPTER_PIPELINE_FAILURE: 45,
        PaperTradingEndToEndRisk.ORDER_PIPELINE_FAILURE: 50,
        PaperTradingEndToEndRisk.END_TO_END_INCONSISTENCY: 45,
    }
    for risk, cap in critical_caps.items():
        if risk in risks:
            overall = min(overall, cap)
    return PaperTradingEndToEndScore(
        overall_score=overall,
        signal_pipeline_score=signal.score,
        decision_pipeline_score=decision.score,
        safety_pipeline_score=safety.score,
        adapter_pipeline_score=adapter.score,
        order_pipeline_score=order.score,
        position_pipeline_score=position.score,
        journal_pipeline_score=journal.score,
        observability_pipeline_score=observability.score,
    )


def _build_end_to_end_graph(risks: tuple[PaperTradingEndToEndRisk, ...]) -> PaperTradingEndToEndGraph:
    nodes = ("signal", "decision", "safety_gate", "adapter", "paper_order", "paper_position", "paper_journal", "observability", "result")
    edges = (
        ("signal", "decision", "feeds"),
        ("decision", "safety_gate", "gated_by"),
        ("safety_gate", "adapter", "authorizes"),
        ("adapter", "paper_order", "translates"),
        ("paper_order", "paper_position", "updates"),
        ("paper_position", "paper_journal", "records"),
        ("paper_journal", "observability", "emits"),
        ("observability", "result", "summarizes"),
    )
    blocked: list[tuple[str, str]] = []
    if PaperTradingEndToEndRisk.SIGNAL_PIPELINE_FAILURE in risks:
        blocked.append(("signal", "decision"))
    if PaperTradingEndToEndRisk.DECISION_PIPELINE_FAILURE in risks:
        blocked.append(("decision", "safety_gate"))
    if PaperTradingEndToEndRisk.SAFETY_GATE_FAILURE in risks:
        blocked.append(("safety_gate", "adapter"))
    if PaperTradingEndToEndRisk.ADAPTER_PIPELINE_FAILURE in risks:
        blocked.append(("adapter", "paper_order"))
    if PaperTradingEndToEndRisk.ORDER_PIPELINE_FAILURE in risks:
        blocked.append(("paper_order", "paper_position"))
    if PaperTradingEndToEndRisk.POSITION_PIPELINE_FAILURE in risks:
        blocked.append(("paper_position", "paper_journal"))
    if PaperTradingEndToEndRisk.JOURNAL_PIPELINE_FAILURE in risks:
        blocked.append(("paper_journal", "observability"))
    if PaperTradingEndToEndRisk.OBSERVABILITY_FAILURE in risks or PaperTradingEndToEndRisk.STATE_DRIFT_RISK in risks:
        blocked.append(("observability", "result"))
    return PaperTradingEndToEndGraph(nodes, edges, tuple((a, b) for a, b, _ in edges), _dedupe(blocked))


def _select_state(score: int, risks: tuple[PaperTradingEndToEndRisk, ...], ready_for_paper_dry_run: bool | None) -> PaperTradingEndToEndState:
    count = len(set(risks))
    hard = {
        PaperTradingEndToEndRisk.SIGNAL_PIPELINE_FAILURE,
        PaperTradingEndToEndRisk.DECISION_PIPELINE_FAILURE,
        PaperTradingEndToEndRisk.SAFETY_GATE_FAILURE,
        PaperTradingEndToEndRisk.ADAPTER_PIPELINE_FAILURE,
        PaperTradingEndToEndRisk.ORDER_PIPELINE_FAILURE,
        PaperTradingEndToEndRisk.END_TO_END_INCONSISTENCY,
    }
    if hard.intersection(risks) or score < 45 or count >= 6:
        return PaperTradingEndToEndState.NOT_READY
    if count >= 3 or score < 72:
        return PaperTradingEndToEndState.REVIEW_REQUIRED
    if count:
        return PaperTradingEndToEndState.PARTIALLY_READY
    if score >= 94 and ready_for_paper_dry_run is True:
        return PaperTradingEndToEndState.READY_FOR_PAPER_DRY_RUN
    if score >= 88:
        return PaperTradingEndToEndState.END_TO_END_READY
    return PaperTradingEndToEndState.PARTIALLY_READY


def generate_end_to_end_recommendations(
    risks: tuple[PaperTradingEndToEndRisk, ...],
    state: PaperTradingEndToEndState | None = None,
) -> tuple[PaperTradingEndToEndRecommendation, ...]:
    recommendations: list[PaperTradingEndToEndRecommendation] = []
    if risks:
        recommendations.append(PaperTradingEndToEndRecommendation.HOLD_PAPER_DRY_RUN_APPROVAL)
    mapping = {
        PaperTradingEndToEndRisk.SIGNAL_PIPELINE_FAILURE: PaperTradingEndToEndRecommendation.REPAIR_SIGNAL_PIPELINE,
        PaperTradingEndToEndRisk.DECISION_PIPELINE_FAILURE: PaperTradingEndToEndRecommendation.REPAIR_DECISION_PIPELINE,
        PaperTradingEndToEndRisk.SAFETY_GATE_FAILURE: PaperTradingEndToEndRecommendation.VERIFY_SAFETY_GATE,
        PaperTradingEndToEndRisk.ADAPTER_PIPELINE_FAILURE: PaperTradingEndToEndRecommendation.REPAIR_ADAPTER_PIPELINE,
        PaperTradingEndToEndRisk.ORDER_PIPELINE_FAILURE: PaperTradingEndToEndRecommendation.REPAIR_ORDER_PIPELINE,
        PaperTradingEndToEndRisk.POSITION_PIPELINE_FAILURE: PaperTradingEndToEndRecommendation.REPAIR_POSITION_PIPELINE,
        PaperTradingEndToEndRisk.JOURNAL_PIPELINE_FAILURE: PaperTradingEndToEndRecommendation.COMPLETE_PAPER_JOURNAL,
        PaperTradingEndToEndRisk.OBSERVABILITY_FAILURE: PaperTradingEndToEndRecommendation.RESTORE_OBSERVABILITY,
        PaperTradingEndToEndRisk.STATE_DRIFT_RISK: PaperTradingEndToEndRecommendation.LOCK_STATE_DETERMINISM,
        PaperTradingEndToEndRisk.END_TO_END_INCONSISTENCY: PaperTradingEndToEndRecommendation.RECONCILE_END_TO_END_FLOW,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(PaperTradingEndToEndRecommendation.RUN_END_TO_END_READINESS_SUITE)
    if state == PaperTradingEndToEndState.READY_FOR_PAPER_DRY_RUN:
        recommendations.append(PaperTradingEndToEndRecommendation.APPROVE_PAPER_DRY_RUN_AFTER_MANUAL_REVIEW)
    return _dedupe(recommendations)


def evaluate_paper_trading_end_to_end(data: PaperTradingEndToEndInput | Mapping[str, Any]) -> PaperTradingEndToEndResult:
    data = _coerce_input(data)
    signal = verify_signal_pipeline(data)
    decision = verify_decision_pipeline(data)
    safety = verify_safety_pipeline(data)
    adapter = verify_adapter_pipeline(data)
    order = verify_order_pipeline(data)
    position = verify_position_pipeline(data)
    journal = verify_journal_pipeline(data)
    observability = verify_observability_pipeline(data)
    risks = detect_end_to_end_risks(data, signal, decision, safety, adapter, order, position, journal, observability)
    score = compute_end_to_end_score(data, risks, signal, decision, safety, adapter, order, position, journal, observability)
    state = _select_state(score.overall_score, risks, data.ready_for_paper_dry_run)
    graph = _build_end_to_end_graph(risks)
    recommendations = generate_end_to_end_recommendations(risks, state)
    offline_only = data.offline_mode_enforced is True and data.adapter_offline_only is True and not _has_upstream(
        data, "BROKER", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK"
    )
    summary = f"{state.value}: score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return PaperTradingEndToEndResult(
        state=state,
        end_to_end_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        signal_pipeline_review=signal,
        decision_pipeline_review=decision,
        safety_pipeline_review=safety,
        adapter_pipeline_review=adapter,
        order_pipeline_review=order,
        position_pipeline_review=position,
        journal_pipeline_review=journal,
        observability_pipeline_review=observability,
        end_to_end_graph=graph,
        recommendations=recommendations,
        offline_only=offline_only,
        summary=summary,
    )


def render_paper_trading_end_to_end_markdown(result: PaperTradingEndToEndResult) -> str:
    lines = [
        "# AGIcore Paper Trading End-to-End",
        f"- State: {result.state.value}",
        f"- Score: {result.end_to_end_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Score Breakdown",
        f"- Signal: {result.score_breakdown.signal_pipeline_score}/100",
        f"- Decision: {result.score_breakdown.decision_pipeline_score}/100",
        f"- Safety: {result.score_breakdown.safety_pipeline_score}/100",
        f"- Adapter: {result.score_breakdown.adapter_pipeline_score}/100",
        f"- Order: {result.score_breakdown.order_pipeline_score}/100",
        f"- Position: {result.score_breakdown.position_pipeline_score}/100",
        f"- Journal: {result.score_breakdown.journal_pipeline_score}/100",
        f"- Observability: {result.score_breakdown.observability_pipeline_score}/100",
        "",
        "# End-to-End Reviews",
    ]
    sections = (
        result.signal_pipeline_review,
        result.decision_pipeline_review,
        result.safety_pipeline_review,
        result.adapter_pipeline_review,
        result.order_pipeline_review,
        result.position_pipeline_review,
        result.journal_pipeline_review,
        result.observability_pipeline_review,
    )
    for section in sections:
        lines.append(
            f"- {section.name}: passed={section.passed}, score={section.score}/100, "
            f"risks={', '.join(risk.value for risk in section.risks) or 'none'}"
        )
        lines.extend(f"  - {item}" for item in section.evidence)
    lines.append("")
    lines.append("# End-to-End Graph")
    lines.append(f"- Nodes: {', '.join(result.end_to_end_graph.nodes)}")
    lines.extend(f"- Edge: {source} -> {target} ({label})" for source, target, label in result.end_to_end_graph.edges)
    lines.append(
        "- Blocked edges: "
        + (", ".join(f"{source}->{target}" for source, target in result.end_to_end_graph.blocked_edges) or "none")
    )
    lines.append("")
    lines.append("# End-to-End Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# End-to-End Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_end_to_end_score",
    "detect_end_to_end_risks",
    "evaluate_paper_trading_end_to_end",
    "generate_end_to_end_recommendations",
    "render_paper_trading_end_to_end_markdown",
    "verify_adapter_pipeline",
    "verify_decision_pipeline",
    "verify_journal_pipeline",
    "verify_observability_pipeline",
    "verify_order_pipeline",
    "verify_position_pipeline",
    "verify_safety_pipeline",
    "verify_signal_pipeline",
]
