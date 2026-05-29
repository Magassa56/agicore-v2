"""Models for offline AGIcore rollback verification."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class RollbackState(StrEnum):
    NOT_VERIFIED = "NOT_VERIFIED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
    VERIFIED = "VERIFIED"
    READY_FOR_OBSERVABILITY_VERIFICATION = "READY_FOR_OBSERVABILITY_VERIFICATION"


class RollbackRisk(StrEnum):
    SNAPSHOT_MISSING = "SNAPSHOT_MISSING"
    RECOVERY_POINT_INVALID = "RECOVERY_POINT_INVALID"
    RUNTIME_RESTORE_FAILURE = "RUNTIME_RESTORE_FAILURE"
    MEMORY_RESTORE_FAILURE = "MEMORY_RESTORE_FAILURE"
    EXECUTION_ROLLBACK_FAILURE = "EXECUTION_ROLLBACK_FAILURE"
    STATE_CORRUPTION_AFTER_ROLLBACK = "STATE_CORRUPTION_AFTER_ROLLBACK"
    PARTIAL_ROLLBACK_RISK = "PARTIAL_ROLLBACK_RISK"
    UNSAFE_RESTART_RISK = "UNSAFE_RESTART_RISK"
    RECOVERY_PATH_MISSING = "RECOVERY_PATH_MISSING"
    ROLLBACK_OBSERVABILITY_GAP = "ROLLBACK_OBSERVABILITY_GAP"


class RollbackRecommendation(StrEnum):
    HOLD_ROLLBACK_APPROVAL = "HOLD_ROLLBACK_APPROVAL"
    CREATE_SAFE_STATE_SNAPSHOT = "CREATE_SAFE_STATE_SNAPSHOT"
    REPAIR_RECOVERY_POINT = "REPAIR_RECOVERY_POINT"
    VERIFY_RUNTIME_RESTORE = "VERIFY_RUNTIME_RESTORE"
    VERIFY_MEMORY_RESTORE = "VERIFY_MEMORY_RESTORE"
    VERIFY_EXECUTION_ROLLBACK = "VERIFY_EXECUTION_ROLLBACK"
    REVALIDATE_POST_ROLLBACK_STATE = "REVALIDATE_POST_ROLLBACK_STATE"
    PREVENT_PARTIAL_ROLLBACK = "PREVENT_PARTIAL_ROLLBACK"
    BLOCK_UNSAFE_RESTART = "BLOCK_UNSAFE_RESTART"
    RESTORE_RECOVERY_PATH = "RESTORE_RECOVERY_PATH"
    ADD_ROLLBACK_OBSERVABILITY = "ADD_ROLLBACK_OBSERVABILITY"
    RUN_ROLLBACK_VERIFICATION_SUITE = "RUN_ROLLBACK_VERIFICATION_SUITE"
    APPROVE_OBSERVABILITY_VERIFICATION_AFTER_MANUAL_REVIEW = (
        "APPROVE_OBSERVABILITY_VERIFICATION_AFTER_MANUAL_REVIEW"
    )


@dataclass(frozen=True)
class RollbackVerificationInput:
    kill_switch_verification: Any = None
    runtime_isolation_review: Any = None
    sandbox_readiness_audit: Any = None
    stable_review: Any = None
    freeze_candidate_review: Any = None
    snapshot_available: bool | None = None
    snapshot_integrity_valid: bool | None = None
    snapshot_recent: bool | None = None
    snapshot_isolated: bool | None = None
    recovery_point_available: bool | None = None
    recovery_point_valid: bool | None = None
    recovery_point_compatible: bool | None = None
    recovery_path_available: bool | None = None
    runtime_restore_tested: bool | None = None
    runtime_restore_deterministic: bool | None = None
    runtime_state_clean: bool | None = None
    unsafe_restart_blocked: bool | None = None
    memory_restore_tested: bool | None = None
    memory_namespace_restored: bool | None = None
    memory_checksum_valid: bool | None = None
    memory_contamination_absent: bool | None = None
    execution_rollback_tested: bool | None = None
    simulated_orders_reverted: bool | None = None
    broker_state_unchanged: bool | None = None
    execution_queue_restored: bool | None = None
    post_rollback_state_valid: bool | None = None
    partial_rollback_detected: bool | None = None
    rollback_observable: bool | None = None
    rollback_audit_logged: bool | None = None
    ready_for_observability_verification: bool | None = None
    state_snapshot_score: int | None = None
    recovery_point_score: int | None = None
    runtime_restore_score: int | None = None
    memory_restore_score: int | None = None
    execution_rollback_score: int | None = None
    rollback_safety_score: int | None = None
    observability_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class RollbackReviewSection:
    name: str
    score: int
    passed: bool
    risks: tuple[RollbackRisk, ...] = ()
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class RollbackGraph:
    nodes: tuple[str, ...] = ()
    edges: tuple[tuple[str, str, str], ...] = ()
    restore_edges: tuple[tuple[str, str], ...] = ()
    failed_edges: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class RollbackScore:
    overall_score: int
    state_snapshot_score: int
    recovery_point_score: int
    runtime_restore_score: int
    memory_restore_score: int
    execution_rollback_score: int
    rollback_safety_score: int
    observability_score: int


@dataclass(frozen=True)
class RollbackVerificationResult:
    state: RollbackState
    rollback_score: int
    score_breakdown: RollbackScore
    risks: tuple[RollbackRisk, ...] = ()
    state_snapshot_review: RollbackReviewSection = field(
        default_factory=lambda: RollbackReviewSection("state_snapshot_review", 0, False)
    )
    recovery_point_review: RollbackReviewSection = field(
        default_factory=lambda: RollbackReviewSection("recovery_point_review", 0, False)
    )
    runtime_restore_review: RollbackReviewSection = field(
        default_factory=lambda: RollbackReviewSection("runtime_restore_review", 0, False)
    )
    memory_restore_review: RollbackReviewSection = field(
        default_factory=lambda: RollbackReviewSection("memory_restore_review", 0, False)
    )
    execution_rollback_review: RollbackReviewSection = field(
        default_factory=lambda: RollbackReviewSection("execution_rollback_review", 0, False)
    )
    rollback_graph: RollbackGraph = field(default_factory=RollbackGraph)
    recommendations: tuple[RollbackRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
