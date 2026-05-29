"""Models for offline AGIcore controlled paper run readiness."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ControlledPaperRunState(StrEnum):
    NOT_READY = "NOT_READY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    PARTIALLY_READY = "PARTIALLY_READY"
    CONTROLLED_PAPER_READY = "CONTROLLED_PAPER_READY"
    READY_FOR_HUMAN_VALIDATED_SESSION = "READY_FOR_HUMAN_VALIDATED_SESSION"


class ControlledPaperRunRisk(StrEnum):
    HUMAN_VALIDATION_MISSING = "HUMAN_VALIDATION_MISSING"
    PAPER_SESSION_CONTROL_FAILURE = "PAPER_SESSION_CONTROL_FAILURE"
    SIMULATED_TRADE_FLOW_INVALID = "SIMULATED_TRADE_FLOW_INVALID"
    EMERGENCY_SHUTDOWN_UNAVAILABLE = "EMERGENCY_SHUTDOWN_UNAVAILABLE"
    RECOVERY_PATH_UNVERIFIED = "RECOVERY_PATH_UNVERIFIED"
    PAPER_SESSION_STATE_CORRUPTION = "PAPER_SESSION_STATE_CORRUPTION"
    PAPER_EXECUTION_DRIFT = "PAPER_EXECUTION_DRIFT"
    SAFETY_GUARD_BYPASS = "SAFETY_GUARD_BYPASS"
    OBSERVABILITY_LOSS = "OBSERVABILITY_LOSS"
    CONTROLLED_RUN_NOT_REPEATABLE = "CONTROLLED_RUN_NOT_REPEATABLE"


class ControlledPaperRunRecommendation(StrEnum):
    HOLD_CONTROLLED_PAPER_RUN_APPROVAL = "HOLD_CONTROLLED_PAPER_RUN_APPROVAL"
    REQUIRE_HUMAN_VALIDATION_GATE = "REQUIRE_HUMAN_VALIDATION_GATE"
    REPAIR_PAPER_SESSION_CONTROLS = "REPAIR_PAPER_SESSION_CONTROLS"
    VALIDATE_SIMULATED_TRADE_FLOW = "VALIDATE_SIMULATED_TRADE_FLOW"
    VERIFY_EMERGENCY_SHUTDOWN_PATH = "VERIFY_EMERGENCY_SHUTDOWN_PATH"
    VERIFY_PAPER_RECOVERY_PATH = "VERIFY_PAPER_RECOVERY_PATH"
    PROTECT_PAPER_SESSION_STATE = "PROTECT_PAPER_SESSION_STATE"
    LOCK_EXECUTION_DETERMINISM = "LOCK_EXECUTION_DETERMINISM"
    ENFORCE_SAFETY_GUARDS = "ENFORCE_SAFETY_GUARDS"
    RESTORE_OBSERVABILITY_COVERAGE = "RESTORE_OBSERVABILITY_COVERAGE"
    MAKE_CONTROLLED_RUN_REPEATABLE = "MAKE_CONTROLLED_RUN_REPEATABLE"
    RUN_CONTROLLED_PAPER_READINESS_SUITE = "RUN_CONTROLLED_PAPER_READINESS_SUITE"
    APPROVE_HUMAN_VALIDATED_SESSION_AFTER_MANUAL_REVIEW = (
        "APPROVE_HUMAN_VALIDATED_SESSION_AFTER_MANUAL_REVIEW"
    )


@dataclass(frozen=True)
class ControlledPaperRunInput:
    paper_execution_loop_readiness: Any = None
    paper_runtime_preparation: Any = None
    observability_verification: Any = None
    rollback_verification: Any = None
    kill_switch_verification: Any = None
    runtime_isolation_review: Any = None
    sandbox_readiness_audit: Any = None
    stable_review: Any = None
    human_operator_assigned: bool | None = None
    manual_approval_required: bool | None = None
    manual_approval_recorded: bool | None = None
    session_scope_acknowledged: bool | None = None
    simulated_trade_flow_defined: bool | None = None
    paper_order_preview_available: bool | None = None
    paper_fill_simulation_available: bool | None = None
    paper_pnl_preview_available: bool | None = None
    flow_repeatable: bool | None = None
    session_limits_configured: bool | None = None
    risk_limits_enforced: bool | None = None
    safety_guards_locked: bool | None = None
    session_state_checkpointed: bool | None = None
    controlled_run_repeatable: bool | None = None
    emergency_shutdown_available: bool | None = None
    kill_switch_linked: bool | None = None
    shutdown_drill_verified: bool | None = None
    post_shutdown_state_safe: bool | None = None
    recovery_path_available: bool | None = None
    rollback_linked: bool | None = None
    recovery_drill_verified: bool | None = None
    post_recovery_state_consistent: bool | None = None
    observability_connected: bool | None = None
    ready_for_human_validated_session: bool | None = None
    human_validation_score: int | None = None
    simulated_trade_flow_score: int | None = None
    paper_session_control_score: int | None = None
    emergency_shutdown_score: int | None = None
    paper_recovery_score: int | None = None
    observability_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class ControlledPaperRunReviewSection:
    name: str
    score: int
    passed: bool
    risks: tuple[ControlledPaperRunRisk, ...] = ()
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class ControlledPaperRunGraph:
    nodes: tuple[str, ...] = ()
    edges: tuple[tuple[str, str, str], ...] = ()
    ready_edges: tuple[tuple[str, str], ...] = ()
    blocked_edges: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class ControlledPaperRunScore:
    overall_score: int
    human_validation_score: int
    simulated_trade_flow_score: int
    paper_session_control_score: int
    emergency_shutdown_score: int
    paper_recovery_score: int
    observability_score: int


@dataclass(frozen=True)
class ControlledPaperRunResult:
    state: ControlledPaperRunState
    controlled_paper_score: int
    score_breakdown: ControlledPaperRunScore
    risks: tuple[ControlledPaperRunRisk, ...] = ()
    human_validation_review: ControlledPaperRunReviewSection = field(
        default_factory=lambda: ControlledPaperRunReviewSection("human_validation_review", 0, False)
    )
    simulated_trade_flow_review: ControlledPaperRunReviewSection = field(
        default_factory=lambda: ControlledPaperRunReviewSection("simulated_trade_flow_review", 0, False)
    )
    paper_session_controls_review: ControlledPaperRunReviewSection = field(
        default_factory=lambda: ControlledPaperRunReviewSection("paper_session_controls_review", 0, False)
    )
    emergency_shutdown_review: ControlledPaperRunReviewSection = field(
        default_factory=lambda: ControlledPaperRunReviewSection("emergency_shutdown_review", 0, False)
    )
    paper_recovery_review: ControlledPaperRunReviewSection = field(
        default_factory=lambda: ControlledPaperRunReviewSection("paper_recovery_review", 0, False)
    )
    controlled_paper_graph: ControlledPaperRunGraph = field(default_factory=ControlledPaperRunGraph)
    recommendations: tuple[ControlledPaperRunRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
