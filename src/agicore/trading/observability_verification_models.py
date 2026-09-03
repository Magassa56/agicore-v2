"""Models for offline AGIcore observability verification."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ObservabilityState(StrEnum):
    NOT_OBSERVABLE = "NOT_OBSERVABLE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    PARTIALLY_OBSERVABLE = "PARTIALLY_OBSERVABLE"
    OBSERVABLE = "OBSERVABLE"
    READY_FOR_PAPER_RUNTIME_PREP = "READY_FOR_PAPER_RUNTIME_PREP"


class ObservabilityRisk(StrEnum):
    LOGGING_GAP = "LOGGING_GAP"
    METRICS_GAP = "METRICS_GAP"
    TRACE_GAP = "TRACE_GAP"
    ALERTING_GAP = "ALERTING_GAP"
    AUDIT_TRAIL_INCOMPLETE = "AUDIT_TRAIL_INCOMPLETE"
    CRITICAL_EVENT_INVISIBLE = "CRITICAL_EVENT_INVISIBLE"
    RUNTIME_STATE_OPAQUE = "RUNTIME_STATE_OPAQUE"
    FAILURE_MODE_UNOBSERVED = "FAILURE_MODE_UNOBSERVED"
    PAPER_RUNTIME_BLIND_SPOT = "PAPER_RUNTIME_BLIND_SPOT"
    OBSERVABILITY_DRIFT = "OBSERVABILITY_DRIFT"


class ObservabilityRecommendation(StrEnum):
    HOLD_OBSERVABILITY_APPROVAL = "HOLD_OBSERVABILITY_APPROVAL"
    ADD_STRUCTURED_RUNTIME_LOGGING = "ADD_STRUCTURED_RUNTIME_LOGGING"
    ADD_RUNTIME_METRICS = "ADD_RUNTIME_METRICS"
    ADD_TRACE_CORRELATION = "ADD_TRACE_CORRELATION"
    ADD_ALERTING_RULES = "ADD_ALERTING_RULES"
    COMPLETE_AUDIT_TRAIL = "COMPLETE_AUDIT_TRAIL"
    SURFACE_CRITICAL_EVENTS = "SURFACE_CRITICAL_EVENTS"
    EXPOSE_RUNTIME_STATE = "EXPOSE_RUNTIME_STATE"
    COVER_FAILURE_MODES = "COVER_FAILURE_MODES"
    REMOVE_PAPER_RUNTIME_BLIND_SPOTS = "REMOVE_PAPER_RUNTIME_BLIND_SPOTS"
    STABILIZE_OBSERVABILITY_SCHEMA = "STABILIZE_OBSERVABILITY_SCHEMA"
    RUN_OBSERVABILITY_VERIFICATION_SUITE = "RUN_OBSERVABILITY_VERIFICATION_SUITE"
    APPROVE_PAPER_RUNTIME_PREP_AFTER_MANUAL_REVIEW = (
        "APPROVE_PAPER_RUNTIME_PREP_AFTER_MANUAL_REVIEW"
    )


@dataclass(frozen=True)
class ObservabilityVerificationInput:
    rollback_verification: Any = None
    kill_switch_verification: Any = None
    runtime_isolation_review: Any = None
    sandbox_readiness_audit: Any = None
    stable_review: Any = None
    freeze_candidate_review: Any = None
    structured_logging_enabled: bool | None = None
    log_levels_configured: bool | None = None
    critical_events_logged: bool | None = None
    log_correlation_ids_present: bool | None = None
    runtime_metrics_enabled: bool | None = None
    safety_metrics_enabled: bool | None = None
    latency_metrics_enabled: bool | None = None
    metric_labels_stable: bool | None = None
    tracing_enabled: bool | None = None
    trace_context_propagated: bool | None = None
    runtime_spans_recorded: bool | None = None
    failure_spans_recorded: bool | None = None
    alerting_configured: bool | None = None
    critical_alert_rules_present: bool | None = None
    alert_deduplication_enabled: bool | None = None
    alert_targets_offline_safe: bool | None = None
    audit_trail_enabled: bool | None = None
    audit_events_immutable: bool | None = None
    safety_decisions_audited: bool | None = None
    paper_runtime_events_visible: bool | None = None
    runtime_state_visible: bool | None = None
    failure_modes_visible: bool | None = None
    observability_schema_stable: bool | None = None
    ready_for_paper_runtime_prep: bool | None = None
    logging_score: int | None = None
    metrics_score: int | None = None
    trace_score: int | None = None
    alerting_score: int | None = None
    audit_trail_score: int | None = None
    runtime_visibility_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class ObservabilityReviewSection:
    name: str
    score: int
    passed: bool
    risks: tuple[ObservabilityRisk, ...] = ()
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class ObservabilityGraph:
    nodes: tuple[str, ...] = ()
    edges: tuple[tuple[str, str, str], ...] = ()
    visible_edges: tuple[tuple[str, str], ...] = ()
    blind_edges: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class ObservabilityScore:
    overall_score: int
    logging_score: int
    metrics_score: int
    trace_score: int
    alerting_score: int
    audit_trail_score: int
    runtime_visibility_score: int


@dataclass(frozen=True)
class ObservabilityVerificationResult:
    state: ObservabilityState
    observability_score: int
    score_breakdown: ObservabilityScore
    risks: tuple[ObservabilityRisk, ...] = ()
    logging_visibility_review: ObservabilityReviewSection = field(
        default_factory=lambda: ObservabilityReviewSection("logging_visibility_review", 0, False)
    )
    metrics_visibility_review: ObservabilityReviewSection = field(
        default_factory=lambda: ObservabilityReviewSection("metrics_visibility_review", 0, False)
    )
    trace_visibility_review: ObservabilityReviewSection = field(
        default_factory=lambda: ObservabilityReviewSection("trace_visibility_review", 0, False)
    )
    alerting_readiness_review: ObservabilityReviewSection = field(
        default_factory=lambda: ObservabilityReviewSection("alerting_readiness_review", 0, False)
    )
    audit_trail_integrity_review: ObservabilityReviewSection = field(
        default_factory=lambda: ObservabilityReviewSection("audit_trail_integrity_review", 0, False)
    )
    observability_graph: ObservabilityGraph = field(default_factory=ObservabilityGraph)
    recommendations: tuple[ObservabilityRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
