"""Models for offline AGIcore freeze candidate review."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class FreezeCandidateState(StrEnum):
    NOT_READY = "NOT_READY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    FREEZE_CANDIDATE = "FREEZE_CANDIDATE"
    STABLE = "STABLE"
    READY_FOR_SANDBOX = "READY_FOR_SANDBOX"


class FreezeCandidateBlocker(StrEnum):
    ARCHITECTURE_FRAGMENTATION = "ARCHITECTURE_FRAGMENTATION"
    RUNTIME_INSTABILITY = "RUNTIME_INSTABILITY"
    OBSERVABILITY_GAP = "OBSERVABILITY_GAP"
    REPLAY_UNSAFE = "REPLAY_UNSAFE"
    ROLLBACK_FAILURE_RISK = "ROLLBACK_FAILURE_RISK"
    KILL_SWITCH_ABSENT = "KILL_SWITCH_ABSENT"
    EXECUTION_LEAK_RISK = "EXECUTION_LEAK_RISK"
    COGNITIVE_DRIFT = "COGNITIVE_DRIFT"
    RECURSIVE_OVERFLOW_RISK = "RECURSIVE_OVERFLOW_RISK"
    SANDBOX_NOT_READY = "SANDBOX_NOT_READY"


class FreezeCandidateRecommendation(StrEnum):
    HOLD_FREEZE_APPROVAL = "HOLD_FREEZE_APPROVAL"
    REDUCE_ARCHITECTURE_FRAGMENTATION = "REDUCE_ARCHITECTURE_FRAGMENTATION"
    STABILIZE_RUNTIME = "STABILIZE_RUNTIME"
    COMPLETE_RUNTIME_OBSERVABILITY = "COMPLETE_RUNTIME_OBSERVABILITY"
    HARDEN_REPLAY_SAFETY = "HARDEN_REPLAY_SAFETY"
    VERIFY_ROLLBACK_RECOVERY = "VERIFY_ROLLBACK_RECOVERY"
    INSTALL_KILL_SWITCH = "INSTALL_KILL_SWITCH"
    SEAL_EXECUTION_BOUNDARY = "SEAL_EXECUTION_BOUNDARY"
    RECONCILE_COGNITIVE_DRIFT = "RECONCILE_COGNITIVE_DRIFT"
    LIMIT_RECURSIVE_DEPTH = "LIMIT_RECURSIVE_DEPTH"
    PREPARE_SANDBOX_RUNTIME = "PREPARE_SANDBOX_RUNTIME"
    RUN_FREEZE_CANDIDATE_REVIEW_SUITE = "RUN_FREEZE_CANDIDATE_REVIEW_SUITE"
    APPROVE_SANDBOX_ONLY_AFTER_MANUAL_REVIEW = "APPROVE_SANDBOX_ONLY_AFTER_MANUAL_REVIEW"


@dataclass(frozen=True)
class FreezeCandidateReviewInput:
    freeze_readiness_audit: Any = None
    cognitive_constitutional: Any = None
    cognitive_meta_supervision: Any = None
    cognitive_recursive_regulation: Any = None
    cognitive_safety_orchestrator: Any = None
    cognitive_executive_control: Any = None
    cognitive_priority_arbitration: Any = None
    cognitive_consensus: Any = None
    cognitive_coherence: Any = None
    cognitive_alignment: Any = None
    cognitive_memory_consolidation: Any = None
    intent_integrity: Any = None
    cognitive_identity: Any = None
    cognitive_continuity: Any = None
    recursive_world_model: Any = None
    self_reflection_audit: Any = None
    architecture_stable: bool | None = None
    module_fragmentation_count: int = 0
    import_coherence_score: int | None = None
    runtime_stable: bool | None = None
    runtime_recoverable: bool | None = None
    runtime_observable: bool | None = None
    logging_consistent: bool | None = None
    replay_safe: bool | None = None
    rollback_ready: bool | None = None
    rollback_tested: bool | None = None
    kill_switch_ready: bool | None = None
    sandbox_ready: bool | None = None
    paper_runtime_ready: bool | None = None
    execution_isolated: bool | None = None
    broker_disabled: bool = True
    external_api_disabled: bool = True
    live_execution_disabled: bool = True
    architecture_score: int | None = None
    runtime_score: int | None = None
    observability_score: int | None = None
    safety_score: int | None = None
    paper_runtime_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class FreezeCandidateReviewSection:
    name: str
    score: int
    passed: bool
    blockers: tuple[FreezeCandidateBlocker, ...] = ()
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class FreezeCandidateScore:
    overall_score: int
    architecture_score: int
    runtime_score: int
    safety_score: int
    observability_score: int
    paper_runtime_score: int
    orchestration_score: int
    recursive_score: int
    constitutional_score: int
    execution_isolation_score: int
    recoverability_score: int


@dataclass(frozen=True)
class FreezeCandidateReviewResult:
    state: FreezeCandidateState
    freeze_candidate_score: int
    score_breakdown: FreezeCandidateScore
    blockers: tuple[FreezeCandidateBlocker, ...] = ()
    architecture_review: FreezeCandidateReviewSection = field(
        default_factory=lambda: FreezeCandidateReviewSection("architecture", 0, False)
    )
    runtime_review: FreezeCandidateReviewSection = field(
        default_factory=lambda: FreezeCandidateReviewSection("runtime", 0, False)
    )
    safety_review: FreezeCandidateReviewSection = field(
        default_factory=lambda: FreezeCandidateReviewSection("safety", 0, False)
    )
    observability_review: FreezeCandidateReviewSection = field(
        default_factory=lambda: FreezeCandidateReviewSection("observability", 0, False)
    )
    paper_runtime_review: FreezeCandidateReviewSection = field(
        default_factory=lambda: FreezeCandidateReviewSection("paper_runtime", 0, False)
    )
    recommendations: tuple[FreezeCandidateRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
