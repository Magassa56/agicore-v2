"""Models for offline AGIcore runtime isolation review."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class RuntimeIsolationState(StrEnum):
    NOT_ISOLATED = "NOT_ISOLATED"
    ISOLATION_REVIEW_REQUIRED = "ISOLATION_REVIEW_REQUIRED"
    PARTIALLY_ISOLATED = "PARTIALLY_ISOLATED"
    ISOLATED = "ISOLATED"
    READY_FOR_PAPER_RUNTIME = "READY_FOR_PAPER_RUNTIME"


class IsolationRisk(StrEnum):
    EXTERNAL_API_ACCESS = "EXTERNAL_API_ACCESS"
    BROKER_CONNECTIVITY = "BROKER_CONNECTIVITY"
    NETWORK_LEAK = "NETWORK_LEAK"
    FILESYSTEM_ESCAPE = "FILESYSTEM_ESCAPE"
    MEMORY_CROSS_CONTAMINATION = "MEMORY_CROSS_CONTAMINATION"
    EXECUTION_BOUNDARY_FAILURE = "EXECUTION_BOUNDARY_FAILURE"
    DEPENDENCY_ESCAPE = "DEPENDENCY_ESCAPE"
    STORAGE_CORRUPTION_RISK = "STORAGE_CORRUPTION_RISK"
    OBSERVABILITY_ISOLATION_GAP = "OBSERVABILITY_ISOLATION_GAP"
    SANDBOX_BREAKOUT_RISK = "SANDBOX_BREAKOUT_RISK"


class IsolationRecommendation(StrEnum):
    HOLD_RUNTIME_ISOLATION_APPROVAL = "HOLD_RUNTIME_ISOLATION_APPROVAL"
    DISABLE_EXTERNAL_API_ACCESS = "DISABLE_EXTERNAL_API_ACCESS"
    DISABLE_BROKER_CONNECTIVITY = "DISABLE_BROKER_CONNECTIVITY"
    SEAL_NETWORK_BOUNDARY = "SEAL_NETWORK_BOUNDARY"
    RESTRICT_FILESYSTEM_SCOPE = "RESTRICT_FILESYSTEM_SCOPE"
    ISOLATE_MEMORY_CONTEXT = "ISOLATE_MEMORY_CONTEXT"
    REPAIR_EXECUTION_BOUNDARY = "REPAIR_EXECUTION_BOUNDARY"
    VENDOR_OR_MOCK_EXTERNAL_DEPENDENCIES = "VENDOR_OR_MOCK_EXTERNAL_DEPENDENCIES"
    PROTECT_STORAGE_STATE = "PROTECT_STORAGE_STATE"
    ADD_ISOLATED_OBSERVABILITY = "ADD_ISOLATED_OBSERVABILITY"
    REBUILD_SANDBOX_BOUNDARY = "REBUILD_SANDBOX_BOUNDARY"
    RUN_RUNTIME_ISOLATION_SUITE = "RUN_RUNTIME_ISOLATION_SUITE"
    APPROVE_PAPER_RUNTIME_AFTER_MANUAL_REVIEW = "APPROVE_PAPER_RUNTIME_AFTER_MANUAL_REVIEW"


@dataclass(frozen=True)
class RuntimeIsolationInput:
    sandbox_readiness_audit: Any = None
    stable_review: Any = None
    freeze_candidate_review: Any = None
    freeze_readiness_audit: Any = None
    execution_isolated: bool | None = None
    live_execution_disabled: bool = True
    real_order_path_disabled: bool | None = None
    broker_disabled: bool = True
    broker_credentials_absent: bool | None = None
    external_api_disabled: bool = True
    api_credentials_absent: bool | None = None
    network_disabled: bool | None = None
    network_allowlist_empty: bool | None = None
    filesystem_root_restricted: bool | None = None
    data_directory_readonly: bool | None = None
    temp_directory_isolated: bool | None = None
    memory_namespace_isolated: bool | None = None
    memory_snapshot_clean: bool | None = None
    memory_cross_run_guard: bool | None = None
    storage_namespace_isolated: bool | None = None
    storage_rollback_available: bool | None = None
    storage_checksum_valid: bool | None = None
    dependencies_offline: bool | None = None
    dependency_mocks_available: bool | None = None
    dependency_lock_verified: bool | None = None
    runtime_observable: bool | None = None
    isolated_logging_enabled: bool | None = None
    isolated_metrics_enabled: bool | None = None
    sandbox_escape_tests_passed: bool | None = None
    paper_runtime_ready: bool | None = None
    execution_boundary_score: int | None = None
    memory_boundary_score: int | None = None
    storage_boundary_score: int | None = None
    network_boundary_score: int | None = None
    dependency_boundary_score: int | None = None
    observability_score: int | None = None
    sandbox_breakout_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class RuntimeIsolationReviewSection:
    name: str
    score: int
    passed: bool
    risks: tuple[IsolationRisk, ...] = ()
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class RuntimeIsolationGraph:
    nodes: tuple[str, ...] = ()
    edges: tuple[tuple[str, str, str], ...] = ()
    blocked_edges: tuple[tuple[str, str], ...] = ()
    escape_edges: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class RuntimeIsolationScore:
    overall_score: int
    execution_boundary_score: int
    memory_boundary_score: int
    storage_boundary_score: int
    network_boundary_score: int
    external_dependency_score: int
    observability_score: int
    sandbox_breakout_score: int


@dataclass(frozen=True)
class RuntimeIsolationResult:
    state: RuntimeIsolationState
    isolation_score: int
    score_breakdown: RuntimeIsolationScore
    risks: tuple[IsolationRisk, ...] = ()
    execution_boundaries: RuntimeIsolationReviewSection = field(
        default_factory=lambda: RuntimeIsolationReviewSection("execution_boundaries", 0, False)
    )
    memory_boundaries: RuntimeIsolationReviewSection = field(
        default_factory=lambda: RuntimeIsolationReviewSection("memory_boundaries", 0, False)
    )
    storage_boundaries: RuntimeIsolationReviewSection = field(
        default_factory=lambda: RuntimeIsolationReviewSection("storage_boundaries", 0, False)
    )
    network_boundaries: RuntimeIsolationReviewSection = field(
        default_factory=lambda: RuntimeIsolationReviewSection("network_boundaries", 0, False)
    )
    external_dependency_boundaries: RuntimeIsolationReviewSection = field(
        default_factory=lambda: RuntimeIsolationReviewSection("external_dependency_boundaries", 0, False)
    )
    isolation_graph: RuntimeIsolationGraph = field(default_factory=RuntimeIsolationGraph)
    recommendations: tuple[IsolationRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
