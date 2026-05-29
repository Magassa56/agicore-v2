"""Offline supervised paper session readiness audit for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.supervised_paper_session_models import (
    SupervisedPaperSessionGraph,
    SupervisedPaperSessionInput,
    SupervisedPaperSessionRecommendation,
    SupervisedPaperSessionResult,
    SupervisedPaperSessionReviewSection,
    SupervisedPaperSessionRisk,
    SupervisedPaperSessionScore,
    SupervisedPaperSessionState,
)


def _coerce_input(data: SupervisedPaperSessionInput | Mapping[str, Any]) -> SupervisedPaperSessionInput:
    if isinstance(data, SupervisedPaperSessionInput):
        return data
    return SupervisedPaperSessionInput(**dict(data))


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


def _upstream_items(data: SupervisedPaperSessionInput) -> tuple[Any, ...]:
    return (
        data.human_validated_paper_session,
        data.controlled_paper_run,
        data.paper_execution_loop_readiness,
        data.paper_runtime_preparation,
        data.observability_verification,
        data.rollback_verification,
        data.kill_switch_verification,
        data.runtime_isolation_review,
        data.sandbox_readiness_audit,
        data.stable_review,
    )


def _upstream_risks(data: SupervisedPaperSessionInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream(data: SupervisedPaperSessionInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _upstream_score(data: SupervisedPaperSessionInput, *names: str) -> int | None:
    values: list[int] = []
    for item in _upstream_items(data):
        values.extend(_score(item, name) for name in names)
        breakdown = _get(item, "score_breakdown")
        values.extend(_score(breakdown, name) for name in names)
    values = [value for value in values if value is not None]
    return _average(values) if values else None


def verify_supervision_chain(
    data: SupervisedPaperSessionInput | Mapping[str, Any],
) -> SupervisedPaperSessionReviewSection:
    """Verify the continuous human supervision chain."""

    data = _coerce_input(data)
    score = _clamp(data.supervision_chain_score) if data.supervision_chain_score is not None else _average(
        (
            _bool_score(data.human_supervisor_assigned),
            _bool_score(data.supervision_protocol_defined),
            _bool_score(data.continuous_supervision_required),
            _bool_score(data.supervision_handoff_blocked),
            _upstream_score(data, "human_validation_score", "controlled_paper_score"),
        ),
        default=45,
    )
    risks: list[SupervisedPaperSessionRisk] = []
    if (
        data.human_supervisor_assigned is not True
        or data.supervision_protocol_defined is not True
        or data.continuous_supervision_required is not True
        or score < 85
        or _has_upstream(data, "HUMAN_APPROVAL_MISSING", "SUPERVISION_GAP")
    ):
        risks.append(SupervisedPaperSessionRisk.SUPERVISION_CHAIN_BROKEN)
    if data.supervision_handoff_blocked is not True:
        risks.append(SupervisedPaperSessionRisk.SAFETY_BYPASS_RISK)
    evidence = (
        f"supervision_chain_score={score}/100",
        f"human_supervisor_assigned={data.human_supervisor_assigned}",
        f"supervision_protocol_defined={data.supervision_protocol_defined}",
        f"continuous_supervision_required={data.continuous_supervision_required}",
        f"supervision_handoff_blocked={data.supervision_handoff_blocked}",
    )
    return SupervisedPaperSessionReviewSection("supervision_chain_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_operator_visibility(
    data: SupervisedPaperSessionInput | Mapping[str, Any],
) -> SupervisedPaperSessionReviewSection:
    """Verify operator visibility and human override during the session."""

    data = _coerce_input(data)
    score = _clamp(data.operator_visibility_score) if data.operator_visibility_score is not None else _average(
        (
            _bool_score(data.operator_dashboard_available),
            _bool_score(data.live_session_state_visible),
            _bool_score(data.risk_state_visible),
            _bool_score(data.paper_position_visible),
            _bool_score(data.human_override_available),
        ),
        default=45,
    )
    risks: list[SupervisedPaperSessionRisk] = []
    if (
        data.operator_dashboard_available is not True
        or data.live_session_state_visible is not True
        or data.risk_state_visible is not True
        or data.paper_position_visible is not True
        or score < 85
    ):
        risks.append(SupervisedPaperSessionRisk.OPERATOR_VISIBILITY_LOSS)
    if data.human_override_available is not True or _has_upstream(data, "HUMAN_OVERRIDE"):
        risks.append(SupervisedPaperSessionRisk.HUMAN_OVERRIDE_FAILURE)
    evidence = (
        f"operator_visibility_score={score}/100",
        f"operator_dashboard_available={data.operator_dashboard_available}",
        f"live_session_state_visible={data.live_session_state_visible}",
        f"risk_state_visible={data.risk_state_visible}",
        f"paper_position_visible={data.paper_position_visible}",
        f"human_override_available={data.human_override_available}",
    )
    return SupervisedPaperSessionReviewSection("operator_visibility_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_emergency_intervention(
    data: SupervisedPaperSessionInput | Mapping[str, Any],
) -> SupervisedPaperSessionReviewSection:
    """Verify emergency halt, kill switch and post-halt safety."""

    data = _coerce_input(data)
    score = _clamp(data.emergency_intervention_score) if data.emergency_intervention_score is not None else _average(
        (
            _bool_score(data.emergency_stop_available),
            _bool_score(data.kill_switch_linked),
            _bool_score(data.emergency_drill_verified),
            _bool_score(data.operator_can_halt_session),
            _bool_score(data.post_halt_state_safe),
            _upstream_score(data, "kill_switch_score"),
        ),
        default=45,
    )
    risks: list[SupervisedPaperSessionRisk] = []
    if (
        data.emergency_stop_available is not True
        or data.kill_switch_linked is not True
        or data.emergency_drill_verified is not True
        or data.operator_can_halt_session is not True
        or score < 85
        or _has_upstream(data, "KILL_SWITCH", "EMERGENCY")
    ):
        risks.append(SupervisedPaperSessionRisk.EMERGENCY_INTERVENTION_FAILURE)
    if data.post_halt_state_safe is not True:
        risks.append(SupervisedPaperSessionRisk.PAPER_SESSION_DRIFT)
    evidence = (
        f"emergency_intervention_score={score}/100",
        f"emergency_stop_available={data.emergency_stop_available}",
        f"kill_switch_linked={data.kill_switch_linked}",
        f"emergency_drill_verified={data.emergency_drill_verified}",
        f"operator_can_halt_session={data.operator_can_halt_session}",
        f"post_halt_state_safe={data.post_halt_state_safe}",
    )
    return SupervisedPaperSessionReviewSection("emergency_intervention_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_session_monitoring(
    data: SupervisedPaperSessionInput | Mapping[str, Any],
) -> SupervisedPaperSessionReviewSection:
    """Verify session monitoring, alerts, audit events, rollback and observability."""

    data = _coerce_input(data)
    observability_score = data.observability_score if data.observability_score is not None else _average(
        (
            _bool_score(data.observability_linked),
            _upstream_score(data, "observability_score"),
        )
    )
    score = _clamp(data.session_monitoring_score) if data.session_monitoring_score is not None else _average(
        (
            _bool_score(data.session_metrics_streaming),
            _bool_score(data.critical_alerts_enabled),
            _bool_score(data.audit_events_streaming),
            _bool_score(data.rollback_linked),
            _bool_score(data.observability_linked),
            observability_score,
            _upstream_score(data, "rollback_score"),
        ),
        default=45,
    )
    risks: list[SupervisedPaperSessionRisk] = []
    if (
        data.session_metrics_streaming is not True
        or data.critical_alerts_enabled is not True
        or data.audit_events_streaming is not True
        or score < 85
    ):
        risks.append(SupervisedPaperSessionRisk.SESSION_MONITORING_GAP)
    if data.rollback_linked is not True or _has_upstream(data, "ROLLBACK"):
        risks.append(SupervisedPaperSessionRisk.ROLLBACK_UNAVAILABLE)
    if data.observability_linked is not True or observability_score < 80 or _has_upstream(data, "OBSERVABILITY"):
        risks.append(SupervisedPaperSessionRisk.OBSERVABILITY_DEGRADATION)
    evidence = (
        f"session_monitoring_score={score}/100",
        f"observability_score={observability_score}/100",
        f"session_metrics_streaming={data.session_metrics_streaming}",
        f"critical_alerts_enabled={data.critical_alerts_enabled}",
        f"audit_events_streaming={data.audit_events_streaming}",
        f"rollback_linked={data.rollback_linked}",
        f"observability_linked={data.observability_linked}",
    )
    return SupervisedPaperSessionReviewSection("session_monitoring_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def verify_decision_traceability(
    data: SupervisedPaperSessionInput | Mapping[str, Any],
) -> SupervisedPaperSessionReviewSection:
    """Verify traceability, drift monitoring and safety bypass prevention."""

    data = _coerce_input(data)
    score = _clamp(data.decision_traceability_score) if data.decision_traceability_score is not None else _average(
        (
            _bool_score(data.decision_trace_enabled),
            _bool_score(data.decision_inputs_recorded),
            _bool_score(data.decision_outputs_recorded),
            _bool_score(data.operator_decisions_logged),
            _bool_score(data.session_drift_monitoring_enabled),
            _bool_score(data.safety_bypass_blocked),
        ),
        default=45,
    )
    risks: list[SupervisedPaperSessionRisk] = []
    if (
        data.decision_trace_enabled is not True
        or data.decision_inputs_recorded is not True
        or data.decision_outputs_recorded is not True
        or data.operator_decisions_logged is not True
        or score < 85
        or _has_upstream(data, "DECISION_TRACEABILITY")
    ):
        risks.append(SupervisedPaperSessionRisk.DECISION_TRACEABILITY_LOSS)
    if data.session_drift_monitoring_enabled is not True or _has_upstream(data, "DRIFT"):
        risks.append(SupervisedPaperSessionRisk.PAPER_SESSION_DRIFT)
    if data.safety_bypass_blocked is not True or _has_upstream(data, "SAFETY_BYPASS", "VALIDATION_BYPASS"):
        risks.append(SupervisedPaperSessionRisk.SAFETY_BYPASS_RISK)
    evidence = (
        f"decision_traceability_score={score}/100",
        f"decision_trace_enabled={data.decision_trace_enabled}",
        f"decision_inputs_recorded={data.decision_inputs_recorded}",
        f"decision_outputs_recorded={data.decision_outputs_recorded}",
        f"operator_decisions_logged={data.operator_decisions_logged}",
        f"session_drift_monitoring_enabled={data.session_drift_monitoring_enabled}",
        f"safety_bypass_blocked={data.safety_bypass_blocked}",
    )
    return SupervisedPaperSessionReviewSection("decision_traceability_review", score, not risks and score >= 85, _dedupe(risks), evidence)


def _build_supervised_session_graph(risks: tuple[SupervisedPaperSessionRisk, ...]) -> SupervisedPaperSessionGraph:
    nodes = (
        "supervision_chain",
        "operator_visibility",
        "emergency_intervention",
        "session_monitoring",
        "decision_traceability",
        "paper_broker_adapter",
    )
    edges = (
        ("supervision_chain", "operator_visibility", "exposes"),
        ("operator_visibility", "emergency_intervention", "enables"),
        ("emergency_intervention", "session_monitoring", "guards"),
        ("session_monitoring", "decision_traceability", "records"),
        ("decision_traceability", "paper_broker_adapter", "gates"),
    )
    blocked: list[tuple[str, str]] = []
    if SupervisedPaperSessionRisk.SUPERVISION_CHAIN_BROKEN in risks:
        blocked.append(("supervision_chain", "operator_visibility"))
    if (
        SupervisedPaperSessionRisk.OPERATOR_VISIBILITY_LOSS in risks
        or SupervisedPaperSessionRisk.HUMAN_OVERRIDE_FAILURE in risks
    ):
        blocked.append(("operator_visibility", "emergency_intervention"))
    if SupervisedPaperSessionRisk.EMERGENCY_INTERVENTION_FAILURE in risks:
        blocked.append(("emergency_intervention", "session_monitoring"))
    if (
        SupervisedPaperSessionRisk.SESSION_MONITORING_GAP in risks
        or SupervisedPaperSessionRisk.OBSERVABILITY_DEGRADATION in risks
        or SupervisedPaperSessionRisk.ROLLBACK_UNAVAILABLE in risks
    ):
        blocked.append(("session_monitoring", "decision_traceability"))
    if (
        SupervisedPaperSessionRisk.DECISION_TRACEABILITY_LOSS in risks
        or SupervisedPaperSessionRisk.PAPER_SESSION_DRIFT in risks
        or SupervisedPaperSessionRisk.SAFETY_BYPASS_RISK in risks
    ):
        blocked.append(("decision_traceability", "paper_broker_adapter"))
    return SupervisedPaperSessionGraph(
        nodes=nodes,
        edges=edges,
        ready_edges=(
            ("supervision_chain", "operator_visibility"),
            ("operator_visibility", "emergency_intervention"),
            ("emergency_intervention", "session_monitoring"),
            ("session_monitoring", "decision_traceability"),
            ("decision_traceability", "paper_broker_adapter"),
        ),
        blocked_edges=_dedupe(blocked),
    )


def detect_supervised_session_risks(
    data: SupervisedPaperSessionInput | Mapping[str, Any],
    supervision_chain_review: SupervisedPaperSessionReviewSection | None = None,
    operator_visibility_review: SupervisedPaperSessionReviewSection | None = None,
    emergency_intervention_review: SupervisedPaperSessionReviewSection | None = None,
    session_monitoring_review: SupervisedPaperSessionReviewSection | None = None,
    decision_traceability_review: SupervisedPaperSessionReviewSection | None = None,
) -> tuple[SupervisedPaperSessionRisk, ...]:
    """Detect risks that block a supervised offline paper session."""

    data = _coerce_input(data)
    sections = (
        supervision_chain_review or verify_supervision_chain(data),
        operator_visibility_review or verify_operator_visibility(data),
        emergency_intervention_review or verify_emergency_intervention(data),
        session_monitoring_review or verify_session_monitoring(data),
        decision_traceability_review or verify_decision_traceability(data),
    )
    risks: list[SupervisedPaperSessionRisk] = []
    for section in sections:
        risks.extend(section.risks)
    return _dedupe(risks)


def compute_supervised_session_score(
    data: SupervisedPaperSessionInput | Mapping[str, Any],
    risks: tuple[SupervisedPaperSessionRisk, ...] = (),
    supervision_chain_review: SupervisedPaperSessionReviewSection | None = None,
    operator_visibility_review: SupervisedPaperSessionReviewSection | None = None,
    emergency_intervention_review: SupervisedPaperSessionReviewSection | None = None,
    session_monitoring_review: SupervisedPaperSessionReviewSection | None = None,
    decision_traceability_review: SupervisedPaperSessionReviewSection | None = None,
) -> SupervisedPaperSessionScore:
    """Compute supervised paper session readiness score normalized to 0..100."""

    data = _coerce_input(data)
    supervision = supervision_chain_review or verify_supervision_chain(data)
    visibility = operator_visibility_review or verify_operator_visibility(data)
    emergency = emergency_intervention_review or verify_emergency_intervention(data)
    monitoring = session_monitoring_review or verify_session_monitoring(data)
    traceability = decision_traceability_review or verify_decision_traceability(data)
    observability_score = data.observability_score if data.observability_score is not None else _average(
        (
            _bool_score(data.observability_linked),
            _upstream_score(data, "observability_score"),
        )
    )
    weighted = _weighted_average(
        (
            (supervision.score, 1.35),
            (visibility.score, 1.15),
            (emergency.score, 1.3),
            (monitoring.score, 1.2),
            (traceability.score, 1.2),
            (observability_score, 0.85),
        )
    )
    penalty = min(72, len(set(risks)) * 7)
    overall = _clamp(weighted - penalty)
    critical_caps = {
        SupervisedPaperSessionRisk.SUPERVISION_CHAIN_BROKEN: 45,
        SupervisedPaperSessionRisk.OPERATOR_VISIBILITY_LOSS: 50,
        SupervisedPaperSessionRisk.EMERGENCY_INTERVENTION_FAILURE: 45,
        SupervisedPaperSessionRisk.HUMAN_OVERRIDE_FAILURE: 50,
        SupervisedPaperSessionRisk.ROLLBACK_UNAVAILABLE: 55,
        SupervisedPaperSessionRisk.SAFETY_BYPASS_RISK: 45,
    }
    for risk, cap in critical_caps.items():
        if risk in risks:
            overall = min(overall, cap)
    return SupervisedPaperSessionScore(
        overall_score=overall,
        supervision_chain_score=supervision.score,
        operator_visibility_score=visibility.score,
        emergency_intervention_score=emergency.score,
        session_monitoring_score=monitoring.score,
        decision_traceability_score=traceability.score,
        observability_score=_clamp(observability_score),
    )


def _select_state(
    score: int,
    risks: tuple[SupervisedPaperSessionRisk, ...],
    ready_for_paper_broker_adapter: bool | None,
) -> SupervisedPaperSessionState:
    count = len(set(risks))
    hard = {
        SupervisedPaperSessionRisk.SUPERVISION_CHAIN_BROKEN,
        SupervisedPaperSessionRisk.OPERATOR_VISIBILITY_LOSS,
        SupervisedPaperSessionRisk.EMERGENCY_INTERVENTION_FAILURE,
        SupervisedPaperSessionRisk.HUMAN_OVERRIDE_FAILURE,
        SupervisedPaperSessionRisk.ROLLBACK_UNAVAILABLE,
        SupervisedPaperSessionRisk.SAFETY_BYPASS_RISK,
    }
    if hard.intersection(risks) or score < 45 or count >= 6:
        return SupervisedPaperSessionState.NOT_READY
    if count >= 3 or score < 72:
        return SupervisedPaperSessionState.REVIEW_REQUIRED
    if count:
        return SupervisedPaperSessionState.PARTIALLY_READY
    if score >= 94 and ready_for_paper_broker_adapter is True:
        return SupervisedPaperSessionState.READY_FOR_PAPER_BROKER_ADAPTER
    if score >= 88:
        return SupervisedPaperSessionState.SUPERVISED_SESSION_READY
    return SupervisedPaperSessionState.PARTIALLY_READY


def generate_supervised_session_recommendations(
    risks: tuple[SupervisedPaperSessionRisk, ...],
    state: SupervisedPaperSessionState | None = None,
) -> tuple[SupervisedPaperSessionRecommendation, ...]:
    """Generate supervised paper session recommendations."""

    recommendations: list[SupervisedPaperSessionRecommendation] = []
    if risks:
        recommendations.append(SupervisedPaperSessionRecommendation.HOLD_PAPER_BROKER_ADAPTER_APPROVAL)
    mapping = {
        SupervisedPaperSessionRisk.SUPERVISION_CHAIN_BROKEN: SupervisedPaperSessionRecommendation.REPAIR_SUPERVISION_CHAIN,
        SupervisedPaperSessionRisk.OPERATOR_VISIBILITY_LOSS: SupervisedPaperSessionRecommendation.RESTORE_OPERATOR_VISIBILITY,
        SupervisedPaperSessionRisk.EMERGENCY_INTERVENTION_FAILURE: SupervisedPaperSessionRecommendation.VERIFY_EMERGENCY_INTERVENTION,
        SupervisedPaperSessionRisk.SESSION_MONITORING_GAP: SupervisedPaperSessionRecommendation.COMPLETE_SESSION_MONITORING,
        SupervisedPaperSessionRisk.DECISION_TRACEABILITY_LOSS: SupervisedPaperSessionRecommendation.RESTORE_DECISION_TRACEABILITY,
        SupervisedPaperSessionRisk.PAPER_SESSION_DRIFT: SupervisedPaperSessionRecommendation.LOCK_PAPER_SESSION_DETERMINISM,
        SupervisedPaperSessionRisk.HUMAN_OVERRIDE_FAILURE: SupervisedPaperSessionRecommendation.ENABLE_HUMAN_OVERRIDE,
        SupervisedPaperSessionRisk.OBSERVABILITY_DEGRADATION: SupervisedPaperSessionRecommendation.RESTORE_OBSERVABILITY,
        SupervisedPaperSessionRisk.ROLLBACK_UNAVAILABLE: SupervisedPaperSessionRecommendation.LINK_ROLLBACK,
        SupervisedPaperSessionRisk.SAFETY_BYPASS_RISK: SupervisedPaperSessionRecommendation.BLOCK_SAFETY_BYPASS,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(SupervisedPaperSessionRecommendation.RUN_SUPERVISED_SESSION_READINESS_SUITE)
    if state == SupervisedPaperSessionState.READY_FOR_PAPER_BROKER_ADAPTER:
        recommendations.append(SupervisedPaperSessionRecommendation.APPROVE_PAPER_BROKER_ADAPTER_AFTER_MANUAL_REVIEW)
    return _dedupe(recommendations)


def evaluate_supervised_paper_session(
    data: SupervisedPaperSessionInput | Mapping[str, Any],
) -> SupervisedPaperSessionResult:
    """Evaluate whether AGIcore is ready for a supervised offline paper session."""

    data = _coerce_input(data)
    supervision = verify_supervision_chain(data)
    visibility = verify_operator_visibility(data)
    emergency = verify_emergency_intervention(data)
    monitoring = verify_session_monitoring(data)
    traceability = verify_decision_traceability(data)
    risks = detect_supervised_session_risks(data, supervision, visibility, emergency, monitoring, traceability)
    score = compute_supervised_session_score(data, risks, supervision, visibility, emergency, monitoring, traceability)
    state = _select_state(score.overall_score, risks, data.ready_for_paper_broker_adapter)
    graph = _build_supervised_session_graph(risks)
    recommendations = generate_supervised_session_recommendations(risks, state)
    offline_only = not _has_upstream(data, "BROKER", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK")
    summary = f"{state.value}: score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return SupervisedPaperSessionResult(
        state=state,
        supervised_session_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        supervision_chain_review=supervision,
        operator_visibility_review=visibility,
        emergency_intervention_review=emergency,
        session_monitoring_review=monitoring,
        decision_traceability_review=traceability,
        supervised_session_graph=graph,
        recommendations=recommendations,
        offline_only=offline_only,
        summary=summary,
    )


def render_supervised_paper_session_markdown(result: SupervisedPaperSessionResult) -> str:
    """Render an explainable supervised paper session report."""

    lines = [
        "# AGIcore Supervised Paper Session",
        f"- State: {result.state.value}",
        f"- Score: {result.supervised_session_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Score Breakdown",
        f"- Supervision chain: {result.score_breakdown.supervision_chain_score}/100",
        f"- Operator visibility: {result.score_breakdown.operator_visibility_score}/100",
        f"- Emergency intervention: {result.score_breakdown.emergency_intervention_score}/100",
        f"- Session monitoring: {result.score_breakdown.session_monitoring_score}/100",
        f"- Decision traceability: {result.score_breakdown.decision_traceability_score}/100",
        f"- Observability: {result.score_breakdown.observability_score}/100",
        "",
        "# Supervised Session Reviews",
    ]
    for section in (
        result.supervision_chain_review,
        result.operator_visibility_review,
        result.emergency_intervention_review,
        result.session_monitoring_review,
        result.decision_traceability_review,
    ):
        lines.append(
            f"- {section.name}: passed={section.passed}, score={section.score}/100, "
            f"risks={', '.join(risk.value for risk in section.risks) or 'none'}"
        )
        lines.extend(f"  - {item}" for item in section.evidence)
    lines.append("")
    lines.append("# Supervised Session Graph")
    lines.append(f"- Nodes: {', '.join(result.supervised_session_graph.nodes)}")
    lines.extend(
        f"- Edge: {source} -> {target} ({label})"
        for source, target, label in result.supervised_session_graph.edges
    )
    lines.append(
        "- Blocked edges: "
        + (
            ", ".join(f"{source}->{target}" for source, target in result.supervised_session_graph.blocked_edges)
            or "none"
        )
    )
    lines.append("")
    lines.append("# Supervised Session Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Supervised Session Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    lines.append("")
    lines.append("# Readiness Outlook")
    if result.state == SupervisedPaperSessionState.READY_FOR_PAPER_BROKER_ADAPTER:
        lines.append("- Supervised paper session is ready for paper broker adapter preparation.")
    elif result.state == SupervisedPaperSessionState.SUPERVISED_SESSION_READY:
        lines.append("- Supervised paper session is ready; broker adapter remains gated.")
    elif result.state == SupervisedPaperSessionState.PARTIALLY_READY:
        lines.append("- Supervised paper session is partially ready and remaining risks must be resolved.")
    else:
        lines.append("- Paper broker adapter approval should remain blocked.")
    return "\n".join(lines)


__all__ = [
    "compute_supervised_session_score",
    "detect_supervised_session_risks",
    "evaluate_supervised_paper_session",
    "generate_supervised_session_recommendations",
    "render_supervised_paper_session_markdown",
    "verify_decision_traceability",
    "verify_emergency_intervention",
    "verify_operator_visibility",
    "verify_session_monitoring",
    "verify_supervision_chain",
]
