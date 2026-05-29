"""Models for offline AGIcore supervised paper session readiness."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class SupervisedPaperSessionState(StrEnum):
    NOT_READY = "NOT_READY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    PARTIALLY_READY = "PARTIALLY_READY"
    SUPERVISED_SESSION_READY = "SUPERVISED_SESSION_READY"
    READY_FOR_PAPER_BROKER_ADAPTER = "READY_FOR_PAPER_BROKER_ADAPTER"


class SupervisedPaperSessionRisk(StrEnum):
    SUPERVISION_CHAIN_BROKEN = "SUPERVISION_CHAIN_BROKEN"
    OPERATOR_VISIBILITY_LOSS = "OPERATOR_VISIBILITY_LOSS"
    EMERGENCY_INTERVENTION_FAILURE = "EMERGENCY_INTERVENTION_FAILURE"
    SESSION_MONITORING_GAP = "SESSION_MONITORING_GAP"
    DECISION_TRACEABILITY_LOSS = "DECISION_TRACEABILITY_LOSS"
    PAPER_SESSION_DRIFT = "PAPER_SESSION_DRIFT"
    HUMAN_OVERRIDE_FAILURE = "HUMAN_OVERRIDE_FAILURE"
    OBSERVABILITY_DEGRADATION = "OBSERVABILITY_DEGRADATION"
    ROLLBACK_UNAVAILABLE = "ROLLBACK_UNAVAILABLE"
    SAFETY_BYPASS_RISK = "SAFETY_BYPASS_RISK"


class SupervisedPaperSessionRecommendation(StrEnum):
    HOLD_PAPER_BROKER_ADAPTER_APPROVAL = "HOLD_PAPER_BROKER_ADAPTER_APPROVAL"
    REPAIR_SUPERVISION_CHAIN = "REPAIR_SUPERVISION_CHAIN"
    RESTORE_OPERATOR_VISIBILITY = "RESTORE_OPERATOR_VISIBILITY"
    VERIFY_EMERGENCY_INTERVENTION = "VERIFY_EMERGENCY_INTERVENTION"
    COMPLETE_SESSION_MONITORING = "COMPLETE_SESSION_MONITORING"
    RESTORE_DECISION_TRACEABILITY = "RESTORE_DECISION_TRACEABILITY"
    LOCK_PAPER_SESSION_DETERMINISM = "LOCK_PAPER_SESSION_DETERMINISM"
    ENABLE_HUMAN_OVERRIDE = "ENABLE_HUMAN_OVERRIDE"
    RESTORE_OBSERVABILITY = "RESTORE_OBSERVABILITY"
    LINK_ROLLBACK = "LINK_ROLLBACK"
    BLOCK_SAFETY_BYPASS = "BLOCK_SAFETY_BYPASS"
    RUN_SUPERVISED_SESSION_READINESS_SUITE = "RUN_SUPERVISED_SESSION_READINESS_SUITE"
    APPROVE_PAPER_BROKER_ADAPTER_AFTER_MANUAL_REVIEW = (
        "APPROVE_PAPER_BROKER_ADAPTER_AFTER_MANUAL_REVIEW"
    )


@dataclass(frozen=True)
class SupervisedPaperSessionInput:
    human_validated_paper_session: Any = None
    controlled_paper_run: Any = None
    paper_execution_loop_readiness: Any = None
    paper_runtime_preparation: Any = None
    observability_verification: Any = None
    rollback_verification: Any = None
    kill_switch_verification: Any = None
    runtime_isolation_review: Any = None
    sandbox_readiness_audit: Any = None
    stable_review: Any = None
    human_supervisor_assigned: bool | None = None
    supervision_protocol_defined: bool | None = None
    continuous_supervision_required: bool | None = None
    supervision_handoff_blocked: bool | None = None
    operator_dashboard_available: bool | None = None
    live_session_state_visible: bool | None = None
    risk_state_visible: bool | None = None
    paper_position_visible: bool | None = None
    human_override_available: bool | None = None
    emergency_stop_available: bool | None = None
    kill_switch_linked: bool | None = None
    emergency_drill_verified: bool | None = None
    operator_can_halt_session: bool | None = None
    post_halt_state_safe: bool | None = None
    session_metrics_streaming: bool | None = None
    critical_alerts_enabled: bool | None = None
    audit_events_streaming: bool | None = None
    rollback_linked: bool | None = None
    observability_linked: bool | None = None
    decision_trace_enabled: bool | None = None
    decision_inputs_recorded: bool | None = None
    decision_outputs_recorded: bool | None = None
    operator_decisions_logged: bool | None = None
    session_drift_monitoring_enabled: bool | None = None
    safety_bypass_blocked: bool | None = None
    ready_for_paper_broker_adapter: bool | None = None
    supervision_chain_score: int | None = None
    operator_visibility_score: int | None = None
    emergency_intervention_score: int | None = None
    session_monitoring_score: int | None = None
    decision_traceability_score: int | None = None
    observability_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class SupervisedPaperSessionReviewSection:
    name: str
    score: int
    passed: bool
    risks: tuple[SupervisedPaperSessionRisk, ...] = ()
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class SupervisedPaperSessionGraph:
    nodes: tuple[str, ...] = ()
    edges: tuple[tuple[str, str, str], ...] = ()
    ready_edges: tuple[tuple[str, str], ...] = ()
    blocked_edges: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class SupervisedPaperSessionScore:
    overall_score: int
    supervision_chain_score: int
    operator_visibility_score: int
    emergency_intervention_score: int
    session_monitoring_score: int
    decision_traceability_score: int
    observability_score: int


@dataclass(frozen=True)
class SupervisedPaperSessionResult:
    state: SupervisedPaperSessionState
    supervised_session_score: int
    score_breakdown: SupervisedPaperSessionScore
    risks: tuple[SupervisedPaperSessionRisk, ...] = ()
    supervision_chain_review: SupervisedPaperSessionReviewSection = field(
        default_factory=lambda: SupervisedPaperSessionReviewSection("supervision_chain_review", 0, False)
    )
    operator_visibility_review: SupervisedPaperSessionReviewSection = field(
        default_factory=lambda: SupervisedPaperSessionReviewSection("operator_visibility_review", 0, False)
    )
    emergency_intervention_review: SupervisedPaperSessionReviewSection = field(
        default_factory=lambda: SupervisedPaperSessionReviewSection("emergency_intervention_review", 0, False)
    )
    session_monitoring_review: SupervisedPaperSessionReviewSection = field(
        default_factory=lambda: SupervisedPaperSessionReviewSection("session_monitoring_review", 0, False)
    )
    decision_traceability_review: SupervisedPaperSessionReviewSection = field(
        default_factory=lambda: SupervisedPaperSessionReviewSection("decision_traceability_review", 0, False)
    )
    supervised_session_graph: SupervisedPaperSessionGraph = field(
        default_factory=SupervisedPaperSessionGraph
    )
    recommendations: tuple[SupervisedPaperSessionRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
