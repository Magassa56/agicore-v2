"""Models for offline AGIcore stable review."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class StableReviewState(StrEnum):
    NOT_STABLE = "NOT_STABLE"
    STABILITY_REVIEW_REQUIRED = "STABILITY_REVIEW_REQUIRED"
    STABLE_CANDIDATE = "STABLE_CANDIDATE"
    STABLE = "STABLE"
    READY_FOR_SANDBOX_PREP = "READY_FOR_SANDBOX_PREP"


class StabilityBlocker(StrEnum):
    TEST_SUITE_INSTABILITY = "TEST_SUITE_INSTABILITY"
    CODEBASE_FRAGMENTATION = "CODEBASE_FRAGMENTATION"
    IMPORT_STRUCTURE_RISK = "IMPORT_STRUCTURE_RISK"
    RUNTIME_STATE_AMBIGUITY = "RUNTIME_STATE_AMBIGUITY"
    LOGGING_INCONSISTENCY = "LOGGING_INCONSISTENCY"
    OBSERVABILITY_GAP = "OBSERVABILITY_GAP"
    SANDBOX_PREP_INCOMPLETE = "SANDBOX_PREP_INCOMPLETE"
    REPLAY_RUNTIME_UNVERIFIED = "REPLAY_RUNTIME_UNVERIFIED"
    KILL_SWITCH_UNVERIFIED = "KILL_SWITCH_UNVERIFIED"
    ROLLBACK_UNVERIFIED = "ROLLBACK_UNVERIFIED"


class StableRecommendation(StrEnum):
    HOLD_STABLE_PROMOTION = "HOLD_STABLE_PROMOTION"
    FIX_TEST_SUITE_INSTABILITY = "FIX_TEST_SUITE_INSTABILITY"
    CONSOLIDATE_CODEBASE_MODULES = "CONSOLIDATE_CODEBASE_MODULES"
    REPAIR_IMPORT_STRUCTURE = "REPAIR_IMPORT_STRUCTURE"
    CLARIFY_RUNTIME_STATE = "CLARIFY_RUNTIME_STATE"
    STANDARDIZE_LOGGING = "STANDARDIZE_LOGGING"
    COMPLETE_OBSERVABILITY = "COMPLETE_OBSERVABILITY"
    COMPLETE_SANDBOX_PREP = "COMPLETE_SANDBOX_PREP"
    VERIFY_REPLAY_RUNTIME = "VERIFY_REPLAY_RUNTIME"
    VERIFY_KILL_SWITCH = "VERIFY_KILL_SWITCH"
    VERIFY_ROLLBACK = "VERIFY_ROLLBACK"
    RUN_STABLE_REVIEW_SUITE = "RUN_STABLE_REVIEW_SUITE"
    APPROVE_SANDBOX_PREP_AFTER_MANUAL_REVIEW = "APPROVE_SANDBOX_PREP_AFTER_MANUAL_REVIEW"


@dataclass(frozen=True)
class StableReviewInput:
    freeze_candidate_review: Any = None
    freeze_readiness_audit: Any = None
    tests_green: bool | None = None
    unit_test_pass_rate: float | None = None
    flaky_test_count: int = 0
    test_failure_count: int = 0
    codebase_stable: bool | None = None
    module_fragmentation_count: int = 0
    module_coherence_score: int | None = None
    import_structure_valid: bool | None = None
    import_coherence_score: int | None = None
    runtime_state_clear: bool | None = None
    runtime_state_score: int | None = None
    runtime_recoverable: bool | None = None
    logging_consistent: bool | None = None
    structured_logging_enabled: bool | None = None
    runtime_observable: bool | None = None
    metrics_available: bool | None = None
    replay_runtime_verified: bool | None = None
    replay_runtime_score: int | None = None
    kill_switch_verified: bool | None = None
    rollback_verified: bool | None = None
    sandbox_prep_complete: bool | None = None
    paper_runtime_ready: bool | None = None
    execution_isolated: bool | None = None
    broker_disabled: bool = True
    external_api_disabled: bool = True
    live_execution_disabled: bool = True
    codebase_score: int | None = None
    runtime_score: int | None = None
    testing_score: int | None = None
    observability_score: int | None = None
    sandbox_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class StableReviewSection:
    name: str
    score: int
    passed: bool
    blockers: tuple[StabilityBlocker, ...] = ()
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class StableScore:
    overall_score: int
    codebase_score: int
    runtime_score: int
    testing_score: int
    observability_score: int
    sandbox_score: int
    import_structure_score: int
    logging_score: int
    replay_score: int
    kill_switch_score: int
    rollback_score: int


@dataclass(frozen=True)
class StableReviewResult:
    state: StableReviewState
    stable_score: int
    score_breakdown: StableScore
    blockers: tuple[StabilityBlocker, ...] = ()
    codebase_review: StableReviewSection = field(
        default_factory=lambda: StableReviewSection("codebase", 0, False)
    )
    runtime_review: StableReviewSection = field(
        default_factory=lambda: StableReviewSection("runtime", 0, False)
    )
    testing_review: StableReviewSection = field(
        default_factory=lambda: StableReviewSection("testing", 0, False)
    )
    observability_review: StableReviewSection = field(
        default_factory=lambda: StableReviewSection("observability", 0, False)
    )
    sandbox_review: StableReviewSection = field(
        default_factory=lambda: StableReviewSection("sandbox", 0, False)
    )
    recommendations: tuple[StableRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
