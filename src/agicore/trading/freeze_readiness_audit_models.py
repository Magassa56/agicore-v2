"""Models for offline AGIcore freeze readiness audit."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class FreezeReadinessState(StrEnum):
    NOT_READY = "NOT_READY"
    PARTIALLY_READY = "PARTIALLY_READY"
    FREEZE_CANDIDATE = "FREEZE_CANDIDATE"
    STABLE = "STABLE"
    READY_TO_TRY = "READY_TO_TRY"


class FreezeBlockerRisk(StrEnum):
    TEST_INSTABILITY = "TEST_INSTABILITY"
    ENGINE_FRAGMENTATION = "ENGINE_FRAGMENTATION"
    ORCHESTRATION_GAP = "ORCHESTRATION_GAP"
    RUNTIME_UNOBSERVABLE = "RUNTIME_UNOBSERVABLE"
    REPLAY_UNSAFE = "REPLAY_UNSAFE"
    KILL_SWITCH_MISSING = "KILL_SWITCH_MISSING"
    ROLLBACK_UNAVAILABLE = "ROLLBACK_UNAVAILABLE"
    MEMORY_INCONSISTENCY = "MEMORY_INCONSISTENCY"
    EXECUTION_UNSAFE = "EXECUTION_UNSAFE"
    PAPER_RUNTIME_NOT_READY = "PAPER_RUNTIME_NOT_READY"


class FreezeRecommendation(StrEnum):
    KEEP_SYSTEM_FROZEN = "KEEP_SYSTEM_FROZEN"
    FIX_TEST_INSTABILITY = "FIX_TEST_INSTABILITY"
    CONSOLIDATE_ENGINES = "CONSOLIDATE_ENGINES"
    COMPLETE_ORCHESTRATION_REGISTRATION = "COMPLETE_ORCHESTRATION_REGISTRATION"
    ADD_RUNTIME_OBSERVABILITY = "ADD_RUNTIME_OBSERVABILITY"
    HARDEN_REPLAY_SANDBOX = "HARDEN_REPLAY_SANDBOX"
    CONFIGURE_KILL_SWITCH = "CONFIGURE_KILL_SWITCH"
    PREPARE_ROLLBACK_PLAN = "PREPARE_ROLLBACK_PLAN"
    RECONCILE_MEMORY_STATE = "RECONCILE_MEMORY_STATE"
    ENFORCE_OFFLINE_EXECUTION_GUARDS = "ENFORCE_OFFLINE_EXECUTION_GUARDS"
    VALIDATE_PAPER_RUNTIME = "VALIDATE_PAPER_RUNTIME"
    RUN_FREEZE_REGRESSION_SUITE = "RUN_FREEZE_REGRESSION_SUITE"
    AUTHORIZE_READY_TO_TRY_ONLY_AFTER_REVIEW = "AUTHORIZE_READY_TO_TRY_ONLY_AFTER_REVIEW"


@dataclass(frozen=True)
class FreezeReadinessInput:
    tests_green: bool | None = None
    unit_test_pass_rate: float | None = None
    flaky_test_count: int = 0
    test_failure_count: int = 0
    engine_count: int = 0
    fragmented_engine_count: int = 0
    conflicting_engine_count: int = 0
    orchestrator_registered: bool | None = None
    orchestrator_route_count: int = 0
    runtime_observable: bool | None = None
    log_json_enabled: bool | None = None
    metrics_available: bool | None = None
    replay_deterministic: bool | None = None
    replay_uses_sandbox_data: bool | None = None
    replay_has_no_real_orders: bool | None = None
    kill_switch_configured: bool | None = None
    rollback_plan_available: bool | None = None
    rollback_tested: bool | None = None
    memory_state_consistent: bool | None = None
    memory_reconciliation_score: int | None = None
    execution_sandboxed: bool | None = None
    broker_connection_disabled: bool = True
    external_api_disabled: bool = True
    live_execution_disabled: bool = True
    paper_trading_loop_ready: bool | None = None
    paper_adapter_ready: bool | None = None
    sandbox_ready: bool | None = None
    global_stability_score: int | None = None
    safety_score: int | None = None
    orchestration_score: int | None = None
    observability_score: int | None = None
    replay_safety_score: int | None = None
    paper_readiness_score: int | None = None
    system_integrity: Any = None
    cognitive_stability: Any = None
    cognitive_consensus: Any = None
    cognitive_coherence: Any = None
    cognitive_constitutional: Any = None
    global_orchestrator: Any = None
    operational_awareness: Any = None
    session_replay: Any = None
    paper_execution_loop: Any = None
    paper_trading_adapter: Any = None
    adaptive_memory: Any = None
    cognitive_memory_consolidation: Any = None
    risk_guard: Any = None
    safe_rl_layer: Any = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class SystemStabilitySnapshot:
    global_stability_score: int
    test_coverage_score: int
    cognitive_fragmentation_score: int
    engine_conflict_score: int
    safety_score: int
    orchestration_score: int
    runtime_coherence_score: int
    observability_score: int
    replay_safety_score: int
    kill_switch_score: int
    rollback_score: int
    memory_consistency_score: int
    sandbox_score: int
    paper_trading_score: int
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class RuntimeReadinessRow:
    area: str
    ready: bool
    score: int
    blockers: tuple[FreezeBlockerRisk, ...] = ()
    detail: str = ""


@dataclass(frozen=True)
class RuntimeReadinessMatrix:
    rows: tuple[RuntimeReadinessRow, ...] = ()

    @property
    def ready(self) -> bool:
        return all(row.ready for row in self.rows)


@dataclass(frozen=True)
class FreezeReadinessScore:
    overall_score: int
    stability_score: int
    tests_score: int
    fragmentation_score: int
    safety_score: int
    orchestration_score: int
    runtime_coherence_score: int
    observability_score: int
    replay_safety_score: int
    kill_switch_score: int
    rollback_score: int
    memory_score: int
    sandbox_score: int
    paper_runtime_score: int


@dataclass(frozen=True)
class FreezeReadinessResult:
    state: FreezeReadinessState
    freeze_readiness_score: int
    score_breakdown: FreezeReadinessScore
    blockers: tuple[FreezeBlockerRisk, ...] = ()
    snapshot: SystemStabilitySnapshot = field(default_factory=lambda: SystemStabilitySnapshot(
        global_stability_score=0,
        test_coverage_score=0,
        cognitive_fragmentation_score=0,
        engine_conflict_score=0,
        safety_score=0,
        orchestration_score=0,
        runtime_coherence_score=0,
        observability_score=0,
        replay_safety_score=0,
        kill_switch_score=0,
        rollback_score=0,
        memory_consistency_score=0,
        sandbox_score=0,
        paper_trading_score=0,
    ))
    runtime_matrix: RuntimeReadinessMatrix = field(default_factory=RuntimeReadinessMatrix)
    recommendations: tuple[FreezeRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
