"""Offline observability verification for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.observability_verification_models import (
    ObservabilityGraph,
    ObservabilityRecommendation,
    ObservabilityReviewSection,
    ObservabilityRisk,
    ObservabilityScore,
    ObservabilityState,
    ObservabilityVerificationInput,
    ObservabilityVerificationResult,
)


def _coerce_input(data: ObservabilityVerificationInput | Mapping[str, Any]) -> ObservabilityVerificationInput:
    if isinstance(data, ObservabilityVerificationInput):
        return data
    return ObservabilityVerificationInput(**dict(data))


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


def _upstream_risks(data: ObservabilityVerificationInput) -> tuple[Any, ...]:
    upstream = (
        data.rollback_verification,
        data.kill_switch_verification,
        data.runtime_isolation_review,
        data.sandbox_readiness_audit,
        data.stable_review,
        data.freeze_candidate_review,
    )
    risks: tuple[Any, ...] = ()
    for item in upstream:
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream(data: ObservabilityVerificationInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _upstream_score(data: ObservabilityVerificationInput, *names: str) -> int | None:
    upstream = (
        data.rollback_verification,
        data.kill_switch_verification,
        data.runtime_isolation_review,
        data.sandbox_readiness_audit,
        data.stable_review,
        data.freeze_candidate_review,
    )
    values: list[int] = []
    for item in upstream:
        values.extend(_score(item, name) for name in names)
        breakdown = _get(item, "score_breakdown")
        values.extend(_score(breakdown, name) for name in names)
    values = [value for value in values if value is not None]
    return _average(values) if values else None


def verify_logging_visibility(
    data: ObservabilityVerificationInput | Mapping[str, Any],
) -> ObservabilityReviewSection:
    """Verify structured runtime logging and critical event visibility."""

    data = _coerce_input(data)
    score = _clamp(data.logging_score) if data.logging_score is not None else _average(
        (
            _bool_score(data.structured_logging_enabled),
            _bool_score(data.log_levels_configured),
            _bool_score(data.critical_events_logged),
            _bool_score(data.log_correlation_ids_present),
            _upstream_score(data, "observability_score"),
        ),
        default=45,
    )
    risks: list[ObservabilityRisk] = []
    if (
        data.structured_logging_enabled is not True
        or data.log_levels_configured is not True
        or data.log_correlation_ids_present is not True
        or score < 80
    ):
        risks.append(ObservabilityRisk.LOGGING_GAP)
    if data.critical_events_logged is not True or _has_upstream(data, "CRITICAL_EVENT"):
        risks.append(ObservabilityRisk.CRITICAL_EVENT_INVISIBLE)
    evidence = (
        f"logging_score={score}/100",
        f"structured_logging_enabled={data.structured_logging_enabled}",
        f"log_levels_configured={data.log_levels_configured}",
        f"critical_events_logged={data.critical_events_logged}",
        f"log_correlation_ids_present={data.log_correlation_ids_present}",
    )
    return ObservabilityReviewSection(
        name="logging_visibility_review",
        score=score,
        passed=not risks and score >= 85,
        risks=_dedupe(risks),
        evidence=evidence,
    )


def verify_metrics_visibility(
    data: ObservabilityVerificationInput | Mapping[str, Any],
) -> ObservabilityReviewSection:
    """Verify runtime, safety and latency metric coverage."""

    data = _coerce_input(data)
    score = _clamp(data.metrics_score) if data.metrics_score is not None else _average(
        (
            _bool_score(data.runtime_metrics_enabled),
            _bool_score(data.safety_metrics_enabled),
            _bool_score(data.latency_metrics_enabled),
            _bool_score(data.metric_labels_stable),
        ),
        default=45,
    )
    risks: list[ObservabilityRisk] = []
    if (
        data.runtime_metrics_enabled is not True
        or data.safety_metrics_enabled is not True
        or data.latency_metrics_enabled is not True
        or score < 80
    ):
        risks.append(ObservabilityRisk.METRICS_GAP)
    if data.metric_labels_stable is not True or _has_upstream(data, "OBSERVABILITY_DRIFT"):
        risks.append(ObservabilityRisk.OBSERVABILITY_DRIFT)
    evidence = (
        f"metrics_score={score}/100",
        f"runtime_metrics_enabled={data.runtime_metrics_enabled}",
        f"safety_metrics_enabled={data.safety_metrics_enabled}",
        f"latency_metrics_enabled={data.latency_metrics_enabled}",
        f"metric_labels_stable={data.metric_labels_stable}",
    )
    return ObservabilityReviewSection(
        name="metrics_visibility_review",
        score=score,
        passed=not risks and score >= 80,
        risks=_dedupe(risks),
        evidence=evidence,
    )


def verify_trace_visibility(
    data: ObservabilityVerificationInput | Mapping[str, Any],
) -> ObservabilityReviewSection:
    """Verify trace propagation and failure span visibility."""

    data = _coerce_input(data)
    score = _clamp(data.trace_score) if data.trace_score is not None else _average(
        (
            _bool_score(data.tracing_enabled),
            _bool_score(data.trace_context_propagated),
            _bool_score(data.runtime_spans_recorded),
            _bool_score(data.failure_spans_recorded),
        ),
        default=45,
    )
    risks: list[ObservabilityRisk] = []
    if (
        data.tracing_enabled is not True
        or data.trace_context_propagated is not True
        or data.runtime_spans_recorded is not True
        or score < 80
    ):
        risks.append(ObservabilityRisk.TRACE_GAP)
    if data.failure_spans_recorded is not True:
        risks.append(ObservabilityRisk.FAILURE_MODE_UNOBSERVED)
    evidence = (
        f"trace_score={score}/100",
        f"tracing_enabled={data.tracing_enabled}",
        f"trace_context_propagated={data.trace_context_propagated}",
        f"runtime_spans_recorded={data.runtime_spans_recorded}",
        f"failure_spans_recorded={data.failure_spans_recorded}",
    )
    return ObservabilityReviewSection(
        name="trace_visibility_review",
        score=score,
        passed=not risks and score >= 80,
        risks=_dedupe(risks),
        evidence=evidence,
    )


def verify_alerting_readiness(
    data: ObservabilityVerificationInput | Mapping[str, Any],
) -> ObservabilityReviewSection:
    """Verify offline-safe alerting for critical runtime and safety events."""

    data = _coerce_input(data)
    score = _clamp(data.alerting_score) if data.alerting_score is not None else _average(
        (
            _bool_score(data.alerting_configured),
            _bool_score(data.critical_alert_rules_present),
            _bool_score(data.alert_deduplication_enabled),
            _bool_score(data.alert_targets_offline_safe),
        ),
        default=45,
    )
    risks: list[ObservabilityRisk] = []
    if (
        data.alerting_configured is not True
        or data.critical_alert_rules_present is not True
        or data.alert_deduplication_enabled is not True
        or data.alert_targets_offline_safe is not True
        or score < 80
    ):
        risks.append(ObservabilityRisk.ALERTING_GAP)
    if data.critical_alert_rules_present is not True:
        risks.append(ObservabilityRisk.CRITICAL_EVENT_INVISIBLE)
    evidence = (
        f"alerting_score={score}/100",
        f"alerting_configured={data.alerting_configured}",
        f"critical_alert_rules_present={data.critical_alert_rules_present}",
        f"alert_deduplication_enabled={data.alert_deduplication_enabled}",
        f"alert_targets_offline_safe={data.alert_targets_offline_safe}",
    )
    return ObservabilityReviewSection(
        name="alerting_readiness_review",
        score=score,
        passed=not risks and score >= 80,
        risks=_dedupe(risks),
        evidence=evidence,
    )


def verify_audit_trail_integrity(
    data: ObservabilityVerificationInput | Mapping[str, Any],
) -> ObservabilityReviewSection:
    """Verify audit trail, paper visibility and runtime state observability."""

    data = _coerce_input(data)
    runtime_visibility_score = (
        _clamp(data.runtime_visibility_score)
        if data.runtime_visibility_score is not None
        else _average(
            (
                _bool_score(data.runtime_state_visible),
                _bool_score(data.failure_modes_visible),
                _bool_score(data.paper_runtime_events_visible),
                _upstream_score(data, "rollback_score", "kill_switch_score", "isolation_score"),
            ),
            default=45,
        )
    )
    score = _clamp(data.audit_trail_score) if data.audit_trail_score is not None else _average(
        (
            _bool_score(data.audit_trail_enabled),
            _bool_score(data.audit_events_immutable),
            _bool_score(data.safety_decisions_audited),
            runtime_visibility_score,
        ),
        default=45,
    )
    risks: list[ObservabilityRisk] = []
    if (
        data.audit_trail_enabled is not True
        or data.audit_events_immutable is not True
        or data.safety_decisions_audited is not True
        or score < 80
    ):
        risks.append(ObservabilityRisk.AUDIT_TRAIL_INCOMPLETE)
    if data.runtime_state_visible is not True or runtime_visibility_score < 80:
        risks.append(ObservabilityRisk.RUNTIME_STATE_OPAQUE)
    if data.failure_modes_visible is not True:
        risks.append(ObservabilityRisk.FAILURE_MODE_UNOBSERVED)
    if data.paper_runtime_events_visible is not True:
        risks.append(ObservabilityRisk.PAPER_RUNTIME_BLIND_SPOT)
    if data.observability_schema_stable is not True:
        risks.append(ObservabilityRisk.OBSERVABILITY_DRIFT)
    evidence = (
        f"audit_trail_score={score}/100",
        f"runtime_visibility_score={runtime_visibility_score}/100",
        f"audit_trail_enabled={data.audit_trail_enabled}",
        f"safety_decisions_audited={data.safety_decisions_audited}",
        f"paper_runtime_events_visible={data.paper_runtime_events_visible}",
    )
    return ObservabilityReviewSection(
        name="audit_trail_integrity_review",
        score=score,
        passed=not risks and score >= 80,
        risks=_dedupe(risks),
        evidence=evidence,
    )


def _build_observability_graph(risks: tuple[ObservabilityRisk, ...]) -> ObservabilityGraph:
    nodes = (
        "agicore_runtime",
        "logs",
        "metrics",
        "traces",
        "alerts",
        "audit_trail",
        "paper_runtime_prep",
    )
    edges = (
        ("agicore_runtime", "logs", "emits"),
        ("agicore_runtime", "metrics", "measures"),
        ("agicore_runtime", "traces", "correlates"),
        ("logs", "alerts", "triggers"),
        ("agicore_runtime", "audit_trail", "records"),
        ("audit_trail", "paper_runtime_prep", "gates"),
    )
    blind_edges: list[tuple[str, str]] = []
    if ObservabilityRisk.LOGGING_GAP in risks or ObservabilityRisk.CRITICAL_EVENT_INVISIBLE in risks:
        blind_edges.append(("agicore_runtime", "logs"))
    if ObservabilityRisk.METRICS_GAP in risks:
        blind_edges.append(("agicore_runtime", "metrics"))
    if ObservabilityRisk.TRACE_GAP in risks or ObservabilityRisk.FAILURE_MODE_UNOBSERVED in risks:
        blind_edges.append(("agicore_runtime", "traces"))
    if ObservabilityRisk.ALERTING_GAP in risks:
        blind_edges.append(("logs", "alerts"))
    if ObservabilityRisk.AUDIT_TRAIL_INCOMPLETE in risks or ObservabilityRisk.RUNTIME_STATE_OPAQUE in risks:
        blind_edges.append(("agicore_runtime", "audit_trail"))
    if ObservabilityRisk.PAPER_RUNTIME_BLIND_SPOT in risks:
        blind_edges.append(("audit_trail", "paper_runtime_prep"))
    return ObservabilityGraph(
        nodes=nodes,
        edges=edges,
        visible_edges=(
            ("agicore_runtime", "logs"),
            ("agicore_runtime", "metrics"),
            ("agicore_runtime", "traces"),
            ("logs", "alerts"),
            ("agicore_runtime", "audit_trail"),
        ),
        blind_edges=_dedupe(blind_edges),
    )


def detect_observability_risks(
    data: ObservabilityVerificationInput | Mapping[str, Any],
    logging_visibility_review: ObservabilityReviewSection | None = None,
    metrics_visibility_review: ObservabilityReviewSection | None = None,
    trace_visibility_review: ObservabilityReviewSection | None = None,
    alerting_readiness_review: ObservabilityReviewSection | None = None,
    audit_trail_integrity_review: ObservabilityReviewSection | None = None,
) -> tuple[ObservabilityRisk, ...]:
    """Detect observability verification risks."""

    data = _coerce_input(data)
    sections = (
        logging_visibility_review or verify_logging_visibility(data),
        metrics_visibility_review or verify_metrics_visibility(data),
        trace_visibility_review or verify_trace_visibility(data),
        alerting_readiness_review or verify_alerting_readiness(data),
        audit_trail_integrity_review or verify_audit_trail_integrity(data),
    )
    risks: list[ObservabilityRisk] = []
    for section in sections:
        risks.extend(section.risks)
    return _dedupe(risks)


def compute_observability_score(
    data: ObservabilityVerificationInput | Mapping[str, Any],
    risks: tuple[ObservabilityRisk, ...] = (),
    logging_visibility_review: ObservabilityReviewSection | None = None,
    metrics_visibility_review: ObservabilityReviewSection | None = None,
    trace_visibility_review: ObservabilityReviewSection | None = None,
    alerting_readiness_review: ObservabilityReviewSection | None = None,
    audit_trail_integrity_review: ObservabilityReviewSection | None = None,
) -> ObservabilityScore:
    """Compute observability verification score normalized to 0..100."""

    data = _coerce_input(data)
    logging = logging_visibility_review or verify_logging_visibility(data)
    metrics = metrics_visibility_review or verify_metrics_visibility(data)
    trace = trace_visibility_review or verify_trace_visibility(data)
    alerting = alerting_readiness_review or verify_alerting_readiness(data)
    audit = audit_trail_integrity_review or verify_audit_trail_integrity(data)
    runtime_visibility_score = (
        _clamp(data.runtime_visibility_score)
        if data.runtime_visibility_score is not None
        else _average(
            (
                _bool_score(data.runtime_state_visible),
                _bool_score(data.failure_modes_visible),
                _bool_score(data.paper_runtime_events_visible),
                _upstream_score(data, "observability_score"),
            )
        )
    )
    weighted = _weighted_average(
        (
            (logging.score, 1.2),
            (metrics.score, 1.05),
            (trace.score, 1.0),
            (alerting.score, 1.1),
            (audit.score, 1.2),
            (runtime_visibility_score, 1.15),
        )
    )
    penalty = min(70, len(set(risks)) * 7)
    overall = _clamp(weighted - penalty)
    critical_caps = {
        ObservabilityRisk.LOGGING_GAP: 55,
        ObservabilityRisk.CRITICAL_EVENT_INVISIBLE: 45,
        ObservabilityRisk.RUNTIME_STATE_OPAQUE: 55,
        ObservabilityRisk.FAILURE_MODE_UNOBSERVED: 55,
        ObservabilityRisk.PAPER_RUNTIME_BLIND_SPOT: 60,
        ObservabilityRisk.AUDIT_TRAIL_INCOMPLETE: 60,
    }
    for risk, cap in critical_caps.items():
        if risk in risks:
            overall = min(overall, cap)
    return ObservabilityScore(
        overall_score=overall,
        logging_score=logging.score,
        metrics_score=metrics.score,
        trace_score=trace.score,
        alerting_score=alerting.score,
        audit_trail_score=audit.score,
        runtime_visibility_score=_clamp(runtime_visibility_score),
    )


def _select_state(
    score: int,
    risks: tuple[ObservabilityRisk, ...],
    ready_for_paper_runtime_prep: bool | None,
) -> ObservabilityState:
    risk_count = len(set(risks))
    hard_risks = {
        ObservabilityRisk.LOGGING_GAP,
        ObservabilityRisk.CRITICAL_EVENT_INVISIBLE,
        ObservabilityRisk.RUNTIME_STATE_OPAQUE,
        ObservabilityRisk.FAILURE_MODE_UNOBSERVED,
        ObservabilityRisk.PAPER_RUNTIME_BLIND_SPOT,
    }
    if hard_risks.intersection(risks) or score < 45 or risk_count >= 6:
        return ObservabilityState.NOT_OBSERVABLE
    if risk_count >= 3 or score < 72:
        return ObservabilityState.REVIEW_REQUIRED
    if risk_count:
        return ObservabilityState.PARTIALLY_OBSERVABLE
    if score >= 94 and ready_for_paper_runtime_prep is True:
        return ObservabilityState.READY_FOR_PAPER_RUNTIME_PREP
    if score >= 88:
        return ObservabilityState.OBSERVABLE
    return ObservabilityState.PARTIALLY_OBSERVABLE


def generate_observability_recommendations(
    risks: tuple[ObservabilityRisk, ...],
    state: ObservabilityState | None = None,
) -> tuple[ObservabilityRecommendation, ...]:
    """Generate observability verification recommendations."""

    recommendations: list[ObservabilityRecommendation] = []
    if risks:
        recommendations.append(ObservabilityRecommendation.HOLD_OBSERVABILITY_APPROVAL)
    mapping = {
        ObservabilityRisk.LOGGING_GAP: ObservabilityRecommendation.ADD_STRUCTURED_RUNTIME_LOGGING,
        ObservabilityRisk.METRICS_GAP: ObservabilityRecommendation.ADD_RUNTIME_METRICS,
        ObservabilityRisk.TRACE_GAP: ObservabilityRecommendation.ADD_TRACE_CORRELATION,
        ObservabilityRisk.ALERTING_GAP: ObservabilityRecommendation.ADD_ALERTING_RULES,
        ObservabilityRisk.AUDIT_TRAIL_INCOMPLETE: ObservabilityRecommendation.COMPLETE_AUDIT_TRAIL,
        ObservabilityRisk.CRITICAL_EVENT_INVISIBLE: ObservabilityRecommendation.SURFACE_CRITICAL_EVENTS,
        ObservabilityRisk.RUNTIME_STATE_OPAQUE: ObservabilityRecommendation.EXPOSE_RUNTIME_STATE,
        ObservabilityRisk.FAILURE_MODE_UNOBSERVED: ObservabilityRecommendation.COVER_FAILURE_MODES,
        ObservabilityRisk.PAPER_RUNTIME_BLIND_SPOT: (
            ObservabilityRecommendation.REMOVE_PAPER_RUNTIME_BLIND_SPOTS
        ),
        ObservabilityRisk.OBSERVABILITY_DRIFT: ObservabilityRecommendation.STABILIZE_OBSERVABILITY_SCHEMA,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(ObservabilityRecommendation.RUN_OBSERVABILITY_VERIFICATION_SUITE)
    if state == ObservabilityState.READY_FOR_PAPER_RUNTIME_PREP:
        recommendations.append(
            ObservabilityRecommendation.APPROVE_PAPER_RUNTIME_PREP_AFTER_MANUAL_REVIEW
        )
    return _dedupe(recommendations)


def evaluate_observability(
    data: ObservabilityVerificationInput | Mapping[str, Any],
) -> ObservabilityVerificationResult:
    """Evaluate whether AGIcore has enough offline visibility for paper runtime prep."""

    data = _coerce_input(data)
    logging = verify_logging_visibility(data)
    metrics = verify_metrics_visibility(data)
    trace = verify_trace_visibility(data)
    alerting = verify_alerting_readiness(data)
    audit = verify_audit_trail_integrity(data)
    risks = detect_observability_risks(data, logging, metrics, trace, alerting, audit)
    score = compute_observability_score(data, risks, logging, metrics, trace, alerting, audit)
    state = _select_state(score.overall_score, risks, data.ready_for_paper_runtime_prep)
    graph = _build_observability_graph(risks)
    recommendations = generate_observability_recommendations(risks, state)
    offline_only = data.alert_targets_offline_safe is True and not _has_upstream(data, "API_ACCESS", "LIVE_EXECUTION")
    summary = f"{state.value}: score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return ObservabilityVerificationResult(
        state=state,
        observability_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        logging_visibility_review=logging,
        metrics_visibility_review=metrics,
        trace_visibility_review=trace,
        alerting_readiness_review=alerting,
        audit_trail_integrity_review=audit,
        observability_graph=graph,
        recommendations=recommendations,
        offline_only=offline_only,
        summary=summary,
    )


def render_observability_markdown(result: ObservabilityVerificationResult) -> str:
    """Render an explainable observability verification report."""

    lines = [
        "# AGIcore Observability Verification",
        f"- State: {result.state.value}",
        f"- Score: {result.observability_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Score Breakdown",
        f"- Logging: {result.score_breakdown.logging_score}/100",
        f"- Metrics: {result.score_breakdown.metrics_score}/100",
        f"- Traces: {result.score_breakdown.trace_score}/100",
        f"- Alerting: {result.score_breakdown.alerting_score}/100",
        f"- Audit trail: {result.score_breakdown.audit_trail_score}/100",
        f"- Runtime visibility: {result.score_breakdown.runtime_visibility_score}/100",
        "",
        "# Observability Reviews",
    ]
    for section in (
        result.logging_visibility_review,
        result.metrics_visibility_review,
        result.trace_visibility_review,
        result.alerting_readiness_review,
        result.audit_trail_integrity_review,
    ):
        lines.append(
            f"- {section.name}: passed={section.passed}, score={section.score}/100, "
            f"risks={', '.join(risk.value for risk in section.risks) or 'none'}"
        )
        lines.extend(f"  - {item}" for item in section.evidence)
    lines.append("")
    lines.append("# Observability Graph")
    lines.append(f"- Nodes: {', '.join(result.observability_graph.nodes)}")
    lines.extend(
        f"- Edge: {source} -> {target} ({label})"
        for source, target, label in result.observability_graph.edges
    )
    lines.append(
        "- Blind edges: "
        + (
            ", ".join(f"{source}->{target}" for source, target in result.observability_graph.blind_edges)
            or "none"
        )
    )
    lines.append("")
    lines.append("# Observability Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Observability Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    lines.append("")
    lines.append("# Verification Outlook")
    if result.state == ObservabilityState.READY_FOR_PAPER_RUNTIME_PREP:
        lines.append("- Observability is ready for manual paper runtime preparation review.")
    elif result.state == ObservabilityState.OBSERVABLE:
        lines.append("- Observability is established; paper runtime preparation remains gated.")
    elif result.state == ObservabilityState.PARTIALLY_OBSERVABLE:
        lines.append("- Observability is partial and remaining risks must be resolved.")
    else:
        lines.append("- Observability approval should remain blocked.")
    return "\n".join(lines)


__all__ = [
    "compute_observability_score",
    "detect_observability_risks",
    "evaluate_observability",
    "generate_observability_recommendations",
    "render_observability_markdown",
    "verify_alerting_readiness",
    "verify_audit_trail_integrity",
    "verify_logging_visibility",
    "verify_metrics_visibility",
    "verify_trace_visibility",
]
