"""Models for offline AGIcore human validated paper session readiness."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class HumanValidatedPaperSessionState(StrEnum):
    NOT_READY = "NOT_READY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    PARTIALLY_READY = "PARTIALLY_READY"
    HUMAN_VALIDATION_READY = "HUMAN_VALIDATION_READY"
    READY_FOR_SUPERVISED_PAPER_SESSION = "READY_FOR_SUPERVISED_PAPER_SESSION"


class HumanValidationRisk(StrEnum):
    HUMAN_APPROVAL_MISSING = "HUMAN_APPROVAL_MISSING"
    OPERATOR_CONFIRMATION_FAILURE = "OPERATOR_CONFIRMATION_FAILURE"
    SESSION_AUTHORIZATION_MISSING = "SESSION_AUTHORIZATION_MISSING"
    AUDIT_TRAIL_INCOMPLETE = "AUDIT_TRAIL_INCOMPLETE"
    DECISION_TRACEABILITY_LOSS = "DECISION_TRACEABILITY_LOSS"
    REVERSIBILITY_NOT_VERIFIED = "REVERSIBILITY_NOT_VERIFIED"
    HUMAN_OVERRIDE_UNAVAILABLE = "HUMAN_OVERRIDE_UNAVAILABLE"
    SUPERVISION_GAP = "SUPERVISION_GAP"
    PAPER_SESSION_DRIFT = "PAPER_SESSION_DRIFT"
    VALIDATION_BYPASS_RISK = "VALIDATION_BYPASS_RISK"


class HumanValidationRecommendation(StrEnum):
    HOLD_SUPERVISED_PAPER_SESSION_APPROVAL = "HOLD_SUPERVISED_PAPER_SESSION_APPROVAL"
    CAPTURE_EXPLICIT_HUMAN_APPROVAL = "CAPTURE_EXPLICIT_HUMAN_APPROVAL"
    REPAIR_OPERATOR_CONFIRMATION_FLOW = "REPAIR_OPERATOR_CONFIRMATION_FLOW"
    AUTHORIZE_SESSION_SCOPE = "AUTHORIZE_SESSION_SCOPE"
    COMPLETE_AUDIT_TRAIL = "COMPLETE_AUDIT_TRAIL"
    RESTORE_DECISION_TRACEABILITY = "RESTORE_DECISION_TRACEABILITY"
    VERIFY_REVERSIBILITY_PATH = "VERIFY_REVERSIBILITY_PATH"
    ENABLE_HUMAN_OVERRIDE = "ENABLE_HUMAN_OVERRIDE"
    CLOSE_SUPERVISION_GAP = "CLOSE_SUPERVISION_GAP"
    LOCK_PAPER_SESSION_DETERMINISM = "LOCK_PAPER_SESSION_DETERMINISM"
    BLOCK_VALIDATION_BYPASS = "BLOCK_VALIDATION_BYPASS"
    RUN_HUMAN_VALIDATION_READINESS_SUITE = "RUN_HUMAN_VALIDATION_READINESS_SUITE"
    APPROVE_SUPERVISED_PAPER_SESSION_AFTER_MANUAL_REVIEW = (
        "APPROVE_SUPERVISED_PAPER_SESSION_AFTER_MANUAL_REVIEW"
    )


@dataclass(frozen=True)
class HumanValidatedPaperSessionInput:
    controlled_paper_run: Any = None
    paper_execution_loop_readiness: Any = None
    paper_runtime_preparation: Any = None
    observability_verification: Any = None
    rollback_verification: Any = None
    kill_switch_verification: Any = None
    runtime_isolation_review: Any = None
    sandbox_readiness_audit: Any = None
    stable_review: Any = None
    assigned_operator_present: bool | None = None
    explicit_approval_required: bool | None = None
    explicit_approval_captured: bool | None = None
    approval_timestamp_recorded: bool | None = None
    session_scope_confirmed: bool | None = None
    operator_identity_verified: bool | None = None
    confirmation_challenge_completed: bool | None = None
    risk_acknowledgement_recorded: bool | None = None
    dry_run_acknowledged: bool | None = None
    human_override_available: bool | None = None
    session_id_assigned: bool | None = None
    session_limits_authorized: bool | None = None
    paper_only_authorized: bool | None = None
    autonomy_disabled: bool | None = None
    validation_bypass_blocked: bool | None = None
    audit_trail_enabled: bool | None = None
    decision_trace_enabled: bool | None = None
    operator_actions_logged: bool | None = None
    session_events_exportable: bool | None = None
    observability_linked: bool | None = None
    rollback_plan_attached: bool | None = None
    kill_switch_attached: bool | None = None
    recovery_checkpoint_available: bool | None = None
    reversal_drill_recorded: bool | None = None
    session_drift_monitoring_enabled: bool | None = None
    ready_for_supervised_paper_session: bool | None = None
    human_approval_score: int | None = None
    operator_confirmation_score: int | None = None
    session_authorization_score: int | None = None
    auditability_score: int | None = None
    reversibility_score: int | None = None
    supervision_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class HumanValidatedPaperSessionReviewSection:
    name: str
    score: int
    passed: bool
    risks: tuple[HumanValidationRisk, ...] = ()
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class HumanValidatedPaperSessionGraph:
    nodes: tuple[str, ...] = ()
    edges: tuple[tuple[str, str, str], ...] = ()
    ready_edges: tuple[tuple[str, str], ...] = ()
    blocked_edges: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class HumanValidatedPaperSessionScore:
    overall_score: int
    human_approval_score: int
    operator_confirmation_score: int
    session_authorization_score: int
    auditability_score: int
    reversibility_score: int
    supervision_score: int


@dataclass(frozen=True)
class HumanValidatedPaperSessionResult:
    state: HumanValidatedPaperSessionState
    human_validation_score: int
    score_breakdown: HumanValidatedPaperSessionScore
    risks: tuple[HumanValidationRisk, ...] = ()
    human_approval_review: HumanValidatedPaperSessionReviewSection = field(
        default_factory=lambda: HumanValidatedPaperSessionReviewSection("human_approval_review", 0, False)
    )
    operator_confirmation_review: HumanValidatedPaperSessionReviewSection = field(
        default_factory=lambda: HumanValidatedPaperSessionReviewSection("operator_confirmation_review", 0, False)
    )
    session_authorization_review: HumanValidatedPaperSessionReviewSection = field(
        default_factory=lambda: HumanValidatedPaperSessionReviewSection("session_authorization_review", 0, False)
    )
    auditability_review: HumanValidatedPaperSessionReviewSection = field(
        default_factory=lambda: HumanValidatedPaperSessionReviewSection("auditability_review", 0, False)
    )
    reversibility_review: HumanValidatedPaperSessionReviewSection = field(
        default_factory=lambda: HumanValidatedPaperSessionReviewSection("reversibility_review", 0, False)
    )
    human_validation_graph: HumanValidatedPaperSessionGraph = field(
        default_factory=HumanValidatedPaperSessionGraph
    )
    recommendations: tuple[HumanValidationRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
