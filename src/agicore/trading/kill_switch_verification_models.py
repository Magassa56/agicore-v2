"""Models for offline AGIcore kill switch verification."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class KillSwitchState(StrEnum):
    NOT_VERIFIED = "NOT_VERIFIED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
    VERIFIED = "VERIFIED"
    READY_FOR_ROLLBACK_VERIFICATION = "READY_FOR_ROLLBACK_VERIFICATION"


class KillSwitchRisk(StrEnum):
    KILL_SWITCH_FAILURE = "KILL_SWITCH_FAILURE"
    SHUTDOWN_PATH_FAILURE = "SHUTDOWN_PATH_FAILURE"
    EXECUTION_CONTINUATION = "EXECUTION_CONTINUATION"
    COGNITIVE_LOOP_CONTINUATION = "COGNITIVE_LOOP_CONTINUATION"
    RUNTIME_HALT_FAILURE = "RUNTIME_HALT_FAILURE"
    LOCKDOWN_FAILURE = "LOCKDOWN_FAILURE"
    SAFETY_OVERRIDE_RISK = "SAFETY_OVERRIDE_RISK"
    EMERGENCY_RESPONSE_DELAY = "EMERGENCY_RESPONSE_DELAY"
    STATE_PERSISTENCE_FAILURE = "STATE_PERSISTENCE_FAILURE"
    RECOVERY_PATH_CORRUPTION = "RECOVERY_PATH_CORRUPTION"


class KillSwitchRecommendation(StrEnum):
    HOLD_KILL_SWITCH_APPROVAL = "HOLD_KILL_SWITCH_APPROVAL"
    INSTALL_KILL_SWITCH_GUARD = "INSTALL_KILL_SWITCH_GUARD"
    REPAIR_SHUTDOWN_PATH = "REPAIR_SHUTDOWN_PATH"
    FORCE_EXECUTION_STOP_PROPAGATION = "FORCE_EXECUTION_STOP_PROPAGATION"
    STOP_COGNITIVE_LOOPS_ON_CRITICAL_SIGNAL = "STOP_COGNITIVE_LOOPS_ON_CRITICAL_SIGNAL"
    HALT_RUNTIME_WORKERS = "HALT_RUNTIME_WORKERS"
    HARDEN_EMERGENCY_LOCKDOWN = "HARDEN_EMERGENCY_LOCKDOWN"
    BLOCK_SAFETY_OVERRIDES = "BLOCK_SAFETY_OVERRIDES"
    REDUCE_EMERGENCY_RESPONSE_LATENCY = "REDUCE_EMERGENCY_RESPONSE_LATENCY"
    PERSIST_SAFE_STOP_STATE = "PERSIST_SAFE_STOP_STATE"
    REPAIR_RECOVERY_CHECKPOINT = "REPAIR_RECOVERY_CHECKPOINT"
    RUN_KILL_SWITCH_VERIFICATION_SUITE = "RUN_KILL_SWITCH_VERIFICATION_SUITE"
    APPROVE_ROLLBACK_VERIFICATION_AFTER_MANUAL_REVIEW = (
        "APPROVE_ROLLBACK_VERIFICATION_AFTER_MANUAL_REVIEW"
    )


@dataclass(frozen=True)
class KillSwitchVerificationInput:
    runtime_isolation_review: Any = None
    sandbox_readiness_audit: Any = None
    stable_review: Any = None
    freeze_candidate_review: Any = None
    freeze_readiness_audit: Any = None
    kill_switch_present: bool | None = None
    kill_signal_registered: bool | None = None
    shutdown_path_tested: bool | None = None
    shutdown_idempotent: bool | None = None
    shutdown_latency_ms: int | float | None = None
    max_shutdown_latency_ms: int | float = 500
    execution_stop_signal_propagates: bool | None = None
    simulated_orders_cancelled: bool | None = None
    broker_path_blocked: bool | None = None
    execution_queue_drained: bool | None = None
    cognitive_stop_signal_propagates: bool | None = None
    cognitive_loops_drained: bool | None = None
    recursive_tasks_cancelled: bool | None = None
    new_cognitive_tasks_blocked: bool | None = None
    runtime_halt_signal_propagates: bool | None = None
    schedulers_stopped: bool | None = None
    event_bus_quiesced: bool | None = None
    background_workers_stopped: bool | None = None
    emergency_lockdown_available: bool | None = None
    safety_overrides_blocked: bool | None = None
    lockdown_idempotent: bool | None = None
    lockdown_audit_logged: bool | None = None
    state_snapshot_persisted: bool | None = None
    recovery_checkpoint_valid: bool | None = None
    rollback_path_available: bool | None = None
    ready_for_rollback_verification: bool | None = None
    shutdown_path_score: int | None = None
    execution_stop_score: int | None = None
    cognitive_stop_score: int | None = None
    runtime_halt_score: int | None = None
    emergency_lockdown_score: int | None = None
    recovery_safety_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class KillSwitchReviewSection:
    name: str
    score: int
    passed: bool
    risks: tuple[KillSwitchRisk, ...] = ()
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class KillSwitchGraph:
    nodes: tuple[str, ...] = ()
    edges: tuple[tuple[str, str, str], ...] = ()
    stop_edges: tuple[tuple[str, str], ...] = ()
    failed_edges: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class KillSwitchScore:
    overall_score: int
    shutdown_path_score: int
    execution_stop_score: int
    cognitive_stop_score: int
    runtime_halt_score: int
    emergency_lockdown_score: int
    recovery_safety_score: int


@dataclass(frozen=True)
class KillSwitchVerificationResult:
    state: KillSwitchState
    kill_switch_score: int
    score_breakdown: KillSwitchScore
    risks: tuple[KillSwitchRisk, ...] = ()
    shutdown_path_review: KillSwitchReviewSection = field(
        default_factory=lambda: KillSwitchReviewSection("shutdown_path_review", 0, False)
    )
    execution_stop_review: KillSwitchReviewSection = field(
        default_factory=lambda: KillSwitchReviewSection("execution_stop_review", 0, False)
    )
    cognitive_stop_review: KillSwitchReviewSection = field(
        default_factory=lambda: KillSwitchReviewSection("cognitive_stop_review", 0, False)
    )
    runtime_halt_review: KillSwitchReviewSection = field(
        default_factory=lambda: KillSwitchReviewSection("runtime_halt_review", 0, False)
    )
    emergency_lockdown_review: KillSwitchReviewSection = field(
        default_factory=lambda: KillSwitchReviewSection("emergency_lockdown_review", 0, False)
    )
    recovery_safety_review: KillSwitchReviewSection = field(
        default_factory=lambda: KillSwitchReviewSection("recovery_safety_review", 0, False)
    )
    kill_switch_graph: KillSwitchGraph = field(default_factory=KillSwitchGraph)
    recommendations: tuple[KillSwitchRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
