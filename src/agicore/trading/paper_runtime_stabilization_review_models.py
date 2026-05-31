"""Models for offline AGIcore Paper Runtime Stabilization Review."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperRuntimeStabilizationState(StrEnum):
    NOT_STABLE = "NOT_STABLE"
    STABILIZATION_REVIEW_REQUIRED = "STABILIZATION_REVIEW_REQUIRED"
    PARTIALLY_STABLE = "PARTIALLY_STABLE"
    STABLE = "STABLE"
    READY_FOR_PAPER_RUNTIME_RELEASE_CANDIDATE = "READY_FOR_PAPER_RUNTIME_RELEASE_CANDIDATE"


class PaperRuntimeStabilizationDecision(StrEnum):
    BLOCK_RELEASE_CANDIDATE = "BLOCK_RELEASE_CANDIDATE"
    REQUIRE_RUNTIME_CLEANUP = "REQUIRE_RUNTIME_CLEANUP"
    REQUIRE_OBSERVABILITY_FIXES = "REQUIRE_OBSERVABILITY_FIXES"
    REQUIRE_ROLLBACK_FIXES = "REQUIRE_ROLLBACK_FIXES"
    REQUIRE_KILL_SWITCH_FIXES = "REQUIRE_KILL_SWITCH_FIXES"
    APPROVE_RELEASE_CANDIDATE_PREPARATION = "APPROVE_RELEASE_CANDIDATE_PREPARATION"


class PaperRuntimeStabilizationRisk(StrEnum):
    RUNTIME_STABILITY_FAILURE = "RUNTIME_STABILITY_FAILURE"
    SCENARIO_REPEATABILITY_FAILURE = "SCENARIO_REPEATABILITY_FAILURE"
    MULTI_SESSION_INCONSISTENCY = "MULTI_SESSION_INCONSISTENCY"
    ERROR_HANDLING_GAP = "ERROR_HANDLING_GAP"
    ROLLBACK_STABILITY_GAP = "ROLLBACK_STABILITY_GAP"
    KILL_SWITCH_STABILITY_GAP = "KILL_SWITCH_STABILITY_GAP"
    HUMAN_SUPERVISION_STABILITY_GAP = "HUMAN_SUPERVISION_STABILITY_GAP"
    JOURNAL_STABILITY_GAP = "JOURNAL_STABILITY_GAP"
    OBSERVABILITY_STABILITY_GAP = "OBSERVABILITY_STABILITY_GAP"
    RUNTIME_STATE_DRIFT = "RUNTIME_STATE_DRIFT"
    RELEASE_CANDIDATE_PREMATURE = "RELEASE_CANDIDATE_PREMATURE"


class PaperRuntimeStabilizationRecommendation(StrEnum):
    HOLD_RELEASE_CANDIDATE = "HOLD_RELEASE_CANDIDATE"
    REPAIR_RUNTIME_STABILITY = "REPAIR_RUNTIME_STABILITY"
    STABILIZE_SCENARIO_REPEATABILITY = "STABILIZE_SCENARIO_REPEATABILITY"
    RECONCILE_MULTI_SESSION_CONSISTENCY = "RECONCILE_MULTI_SESSION_CONSISTENCY"
    IMPROVE_ERROR_HANDLING = "IMPROVE_ERROR_HANDLING"
    REPAIR_ROLLBACK_STABILITY = "REPAIR_ROLLBACK_STABILITY"
    REPAIR_KILL_SWITCH_STABILITY = "REPAIR_KILL_SWITCH_STABILITY"
    REPAIR_HUMAN_SUPERVISION_STABILITY = "REPAIR_HUMAN_SUPERVISION_STABILITY"
    REPAIR_JOURNAL_STABILITY = "REPAIR_JOURNAL_STABILITY"
    REPAIR_OBSERVABILITY_STABILITY = "REPAIR_OBSERVABILITY_STABILITY"
    RECONCILE_RUNTIME_STATE_DRIFT = "RECONCILE_RUNTIME_STATE_DRIFT"
    DELAY_RELEASE_CANDIDATE = "DELAY_RELEASE_CANDIDATE"
    RUN_STABILIZATION_REVIEW_SUITE = "RUN_STABILIZATION_REVIEW_SUITE"
    APPROVE_RELEASE_CANDIDATE_AFTER_MANUAL_REVIEW = "APPROVE_RELEASE_CANDIDATE_AFTER_MANUAL_REVIEW"


@dataclass(frozen=True)
class PaperRuntimeStabilizationReviewInput:
    extended_paper_runtime_test: Any = None
    paper_runtime_test_run: Any = None
    paper_trading_runtime: Any = None
    paper_runtime_integration_review: Any = None
    paper_trading_runtime_design: Any = None
    paper_runtime_decision_review: Any = None
    full_paper_session: Any = None
    simulated_market_session: Any = None
    mock_alpaca_session: Any = None
    mock_connectivity_layer: Any = None
    observability_verification: Any = None
    rollback_verification: Any = None
    kill_switch_verification: Any = None
    human_validated_paper_session: Any = None
    supervised_paper_session: Any = None
    runtime_stable: bool | None = None
    scenarios_repeatable: bool | None = None
    multi_session_consistent: bool | None = None
    error_handling_stable: bool | None = None
    rollback_stable: bool | None = None
    kill_switch_stable: bool | None = None
    human_supervision_stable: bool | None = None
    journal_stable: bool | None = None
    observability_stable: bool | None = None
    runtime_state_reconciled: bool | None = None
    release_candidate_requested: bool | None = None
    offline_mode_enforced: bool | None = None
    sandbox_mode_enforced: bool | None = None
    no_real_broker: bool | None = None
    no_api_key_read: bool | None = None
    no_http_transport: bool | None = None
    no_websocket_transport: bool | None = None
    no_socket_transport: bool | None = None
    no_external_api: bool | None = None
    no_real_order: bool | None = None
    runtime_stability_score: int | None = None
    scenario_repeatability_score: int | None = None
    multi_session_consistency_score: int | None = None
    error_handling_score: int | None = None
    rollback_stability_score: int | None = None
    kill_switch_stability_score: int | None = None
    human_supervision_stability_score: int | None = None
    journal_stability_score: int | None = None
    observability_stability_score: int | None = None
    runtime_state_drift_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperRuntimeStabilizationReview:
    name: str
    score: int
    passed: bool
    risks: tuple[PaperRuntimeStabilizationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperRuntimeStabilizationScore:
    overall_score: int
    runtime_stability_score: int
    scenario_repeatability_score: int
    multi_session_consistency_score: int
    error_handling_score: int
    rollback_stability_score: int
    kill_switch_stability_score: int
    human_supervision_stability_score: int
    journal_stability_score: int
    observability_stability_score: int
    runtime_state_drift_score: int


@dataclass(frozen=True)
class PaperRuntimeStabilizationReviewResult:
    state: PaperRuntimeStabilizationState
    decision: PaperRuntimeStabilizationDecision
    stabilization_score: int
    score_breakdown: PaperRuntimeStabilizationScore
    risks: tuple[PaperRuntimeStabilizationRisk, ...] = ()
    runtime_stability: PaperRuntimeStabilizationReview = field(default_factory=lambda: PaperRuntimeStabilizationReview("runtime_stability", 0, False))
    scenario_repeatability: PaperRuntimeStabilizationReview = field(default_factory=lambda: PaperRuntimeStabilizationReview("scenario_repeatability", 0, False))
    multi_session_consistency: PaperRuntimeStabilizationReview = field(default_factory=lambda: PaperRuntimeStabilizationReview("multi_session_consistency", 0, False))
    error_handling_behavior: PaperRuntimeStabilizationReview = field(default_factory=lambda: PaperRuntimeStabilizationReview("error_handling_behavior", 0, False))
    rollback_stability: PaperRuntimeStabilizationReview = field(default_factory=lambda: PaperRuntimeStabilizationReview("rollback_stability", 0, False))
    kill_switch_stability: PaperRuntimeStabilizationReview = field(default_factory=lambda: PaperRuntimeStabilizationReview("kill_switch_stability", 0, False))
    human_supervision_stability: PaperRuntimeStabilizationReview = field(default_factory=lambda: PaperRuntimeStabilizationReview("human_supervision_stability", 0, False))
    journal_stability: PaperRuntimeStabilizationReview = field(default_factory=lambda: PaperRuntimeStabilizationReview("journal_stability", 0, False))
    observability_stability: PaperRuntimeStabilizationReview = field(default_factory=lambda: PaperRuntimeStabilizationReview("observability_stability", 0, False))
    runtime_state_drift: PaperRuntimeStabilizationReview = field(default_factory=lambda: PaperRuntimeStabilizationReview("runtime_state_drift", 0, False))
    recommendations: tuple[PaperRuntimeStabilizationRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""

