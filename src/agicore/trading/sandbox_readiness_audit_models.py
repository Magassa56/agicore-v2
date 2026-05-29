"""Models for offline AGIcore sandbox readiness audit."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class SandboxReadinessState(StrEnum):
    NOT_READY = "NOT_READY"
    SANDBOX_REVIEW_REQUIRED = "SANDBOX_REVIEW_REQUIRED"
    SANDBOX_CANDIDATE = "SANDBOX_CANDIDATE"
    SANDBOX_READY = "SANDBOX_READY"
    READY_FOR_PAPER_RUNTIME = "READY_FOR_PAPER_RUNTIME"


class SandboxBlocker(StrEnum):
    LIVE_EXECUTION_LEAK = "LIVE_EXECUTION_LEAK"
    BROKER_CONNECTION_RISK = "BROKER_CONNECTION_RISK"
    API_EXPOSURE_RISK = "API_EXPOSURE_RISK"
    KILL_SWITCH_FAILURE = "KILL_SWITCH_FAILURE"
    ROLLBACK_FAILURE = "ROLLBACK_FAILURE"
    OBSERVABILITY_GAP = "OBSERVABILITY_GAP"
    STATE_CORRUPTION_RISK = "STATE_CORRUPTION_RISK"
    MEMORY_PERSISTENCE_RISK = "MEMORY_PERSISTENCE_RISK"
    PAPER_RUNTIME_NOT_READY = "PAPER_RUNTIME_NOT_READY"
    SANDBOX_ISOLATION_FAILURE = "SANDBOX_ISOLATION_FAILURE"


class SandboxRecommendation(StrEnum):
    HOLD_SANDBOX_ENTRY = "HOLD_SANDBOX_ENTRY"
    SEAL_LIVE_EXECUTION_PATHS = "SEAL_LIVE_EXECUTION_PATHS"
    DISABLE_BROKER_CONNECTIONS = "DISABLE_BROKER_CONNECTIONS"
    DISABLE_EXTERNAL_APIS = "DISABLE_EXTERNAL_APIS"
    VERIFY_KILL_SWITCH = "VERIFY_KILL_SWITCH"
    VERIFY_ROLLBACK = "VERIFY_ROLLBACK"
    COMPLETE_OBSERVABILITY = "COMPLETE_OBSERVABILITY"
    PROTECT_RUNTIME_STATE = "PROTECT_RUNTIME_STATE"
    ISOLATE_MEMORY_PERSISTENCE = "ISOLATE_MEMORY_PERSISTENCE"
    PREPARE_PAPER_RUNTIME = "PREPARE_PAPER_RUNTIME"
    REBUILD_SANDBOX_ISOLATION = "REBUILD_SANDBOX_ISOLATION"
    RUN_SANDBOX_READINESS_SUITE = "RUN_SANDBOX_READINESS_SUITE"
    APPROVE_PAPER_RUNTIME_ONLY_AFTER_MANUAL_REVIEW = "APPROVE_PAPER_RUNTIME_ONLY_AFTER_MANUAL_REVIEW"


@dataclass(frozen=True)
class SandboxReadinessInput:
    stable_review: Any = None
    freeze_candidate_review: Any = None
    freeze_readiness_audit: Any = None
    live_execution_disabled: bool = True
    execution_isolated: bool | None = None
    broker_disabled: bool = True
    broker_credentials_absent: bool | None = None
    external_api_disabled: bool = True
    api_credentials_absent: bool | None = None
    sandbox_network_isolated: bool | None = None
    sandbox_filesystem_isolated: bool | None = None
    sandbox_state_clean: bool | None = None
    runtime_state_validated: bool | None = None
    state_checksum_valid: bool | None = None
    memory_persistence_isolated: bool | None = None
    memory_snapshot_reversible: bool | None = None
    kill_switch_configured: bool | None = None
    kill_switch_tested: bool | None = None
    rollback_plan_available: bool | None = None
    rollback_tested: bool | None = None
    runtime_observable: bool | None = None
    structured_logging_enabled: bool | None = None
    metrics_available: bool | None = None
    audit_events_enabled: bool | None = None
    replay_runtime_verified: bool | None = None
    replay_runtime_score: int | None = None
    paper_runtime_prepared: bool | None = None
    paper_runtime_dependencies_ready: bool | None = None
    paper_runtime_score: int | None = None
    isolation_score: int | None = None
    kill_switch_score: int | None = None
    rollback_score: int | None = None
    observability_score: int | None = None
    state_integrity_score: int | None = None
    memory_persistence_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class SandboxReviewSection:
    name: str
    score: int
    passed: bool
    blockers: tuple[SandboxBlocker, ...] = ()
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class SandboxScore:
    overall_score: int
    runtime_isolation_score: int
    kill_switch_score: int
    rollback_score: int
    observability_score: int
    paper_runtime_preparation_score: int
    state_integrity_score: int
    memory_persistence_score: int
    replay_runtime_score: int


@dataclass(frozen=True)
class SandboxReadinessResult:
    state: SandboxReadinessState
    sandbox_score: int
    score_breakdown: SandboxScore
    blockers: tuple[SandboxBlocker, ...] = ()
    runtime_isolation_review: SandboxReviewSection = field(
        default_factory=lambda: SandboxReviewSection("runtime_isolation", 0, False)
    )
    kill_switch_review: SandboxReviewSection = field(
        default_factory=lambda: SandboxReviewSection("kill_switch", 0, False)
    )
    rollback_review: SandboxReviewSection = field(
        default_factory=lambda: SandboxReviewSection("rollback", 0, False)
    )
    observability_review: SandboxReviewSection = field(
        default_factory=lambda: SandboxReviewSection("observability", 0, False)
    )
    paper_runtime_preparation_review: SandboxReviewSection = field(
        default_factory=lambda: SandboxReviewSection("paper_runtime_preparation", 0, False)
    )
    recommendations: tuple[SandboxRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
