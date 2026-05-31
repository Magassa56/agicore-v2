"""Models for offline AGIcore paper trading runtime pre-review."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperRuntimePreReviewState(StrEnum):
    NOT_READY = "NOT_READY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    PARTIALLY_READY = "PARTIALLY_READY"
    RUNTIME_PRE_REVIEW_READY = "RUNTIME_PRE_REVIEW_READY"
    READY_FOR_PAPER_TRADING_RUNTIME = "READY_FOR_PAPER_TRADING_RUNTIME"


class PaperRuntimePreReviewRisk(StrEnum):
    MODULE_MAP_INCOMPLETE = "MODULE_MAP_INCOMPLETE"
    DUPLICATE_RUNTIME_LAYER = "DUPLICATE_RUNTIME_LAYER"
    DEPENDENCY_GAP = "DEPENDENCY_GAP"
    ENTRYPOINT_MISSING = "ENTRYPOINT_MISSING"
    INTEGRATION_GAP = "INTEGRATION_GAP"
    OBSERVABILITY_GAP = "OBSERVABILITY_GAP"
    SAFETY_LINK_MISSING = "SAFETY_LINK_MISSING"
    ROLLBACK_LINK_MISSING = "ROLLBACK_LINK_MISSING"
    KILL_SWITCH_LINK_MISSING = "KILL_SWITCH_LINK_MISSING"
    RUNTIME_SCOPE_DRIFT = "RUNTIME_SCOPE_DRIFT"


class PaperRuntimePreReviewRecommendation(StrEnum):
    HOLD_RUNTIME_IMPLEMENTATION = "HOLD_RUNTIME_IMPLEMENTATION"
    COMPLETE_TRADING_MODULE_MAP = "COMPLETE_TRADING_MODULE_MAP"
    CONSOLIDATE_DUPLICATE_RUNTIME_LAYERS = "CONSOLIDATE_DUPLICATE_RUNTIME_LAYERS"
    RESOLVE_RUNTIME_DEPENDENCIES = "RESOLVE_RUNTIME_DEPENDENCIES"
    DEFINE_RUNTIME_ENTRYPOINTS = "DEFINE_RUNTIME_ENTRYPOINTS"
    CLOSE_RUNTIME_INTEGRATION_GAPS = "CLOSE_RUNTIME_INTEGRATION_GAPS"
    RESTORE_RUNTIME_OBSERVABILITY = "RESTORE_RUNTIME_OBSERVABILITY"
    LINK_RUNTIME_SAFETY_GATE = "LINK_RUNTIME_SAFETY_GATE"
    LINK_RUNTIME_ROLLBACK = "LINK_RUNTIME_ROLLBACK"
    LINK_RUNTIME_KILL_SWITCH = "LINK_RUNTIME_KILL_SWITCH"
    FREEZE_RUNTIME_SCOPE = "FREEZE_RUNTIME_SCOPE"
    RUN_PAPER_RUNTIME_PRE_REVIEW_SUITE = "RUN_PAPER_RUNTIME_PRE_REVIEW_SUITE"
    APPROVE_PAPER_TRADING_RUNTIME_IMPLEMENTATION = (
        "APPROVE_PAPER_TRADING_RUNTIME_IMPLEMENTATION"
    )


@dataclass(frozen=True)
class PaperRuntimePreReviewInput:
    full_paper_session: Any = None
    simulated_market_session: Any = None
    mock_alpaca_session: Any = None
    mock_connectivity_layer: Any = None
    alpaca_paper_connectivity_readiness: Any = None
    broker_paper_sandbox: Any = None
    paper_trading_end_to_end: Any = None
    paper_dry_run: Any = None
    supervised_paper_trial: Any = None
    observability_verification: Any = None
    rollback_verification: Any = None
    kill_switch_verification: Any = None
    trading_modules: tuple[str, ...] = ()
    runtime_candidates: tuple[str, ...] = ()
    duplicate_layers: tuple[str, ...] = ()
    dependencies_declared: tuple[str, ...] = ()
    dependencies_required: tuple[str, ...] = ()
    entrypoints_declared: tuple[str, ...] = ()
    entrypoints_required: tuple[str, ...] = ()
    integration_gaps: tuple[str, ...] = ()
    observability_links: tuple[str, ...] = ()
    safety_links: tuple[str, ...] = ()
    rollback_links: tuple[str, ...] = ()
    kill_switch_links: tuple[str, ...] = ()
    runtime_scope_locked: bool | None = None
    no_runtime_implementation_created: bool | None = None
    offline_mode_enforced: bool | None = None
    no_real_broker: bool | None = None
    no_api_key_read: bool | None = None
    no_http_transport: bool | None = None
    no_websocket_transport: bool | None = None
    no_socket_transport: bool | None = None
    no_external_api: bool | None = None
    no_real_order: bool | None = None
    pre_review_validated: bool | None = None
    ready_for_paper_trading_runtime: bool | None = None
    module_map_score: int | None = None
    duplicate_score: int | None = None
    dependency_score: int | None = None
    entrypoint_score: int | None = None
    integration_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperRuntimeModuleMap:
    modules: tuple[str, ...] = ()
    runtime_candidates: tuple[str, ...] = ()
    categories: tuple[tuple[str, str], ...] = ()
    missing_expected_modules: tuple[str, ...] = ()
    score: int = 0
    risks: tuple[PaperRuntimePreReviewRisk, ...] = ()


@dataclass(frozen=True)
class PaperRuntimeReview:
    name: str
    score: int
    passed: bool
    risks: tuple[PaperRuntimePreReviewRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperRuntimePreReviewScore:
    overall_score: int
    module_map_score: int
    duplicate_score: int
    dependency_score: int
    entrypoint_score: int
    integration_score: int


@dataclass(frozen=True)
class PaperRuntimePreReviewResult:
    state: PaperRuntimePreReviewState
    pre_review_score: int
    score_breakdown: PaperRuntimePreReviewScore
    risks: tuple[PaperRuntimePreReviewRisk, ...] = ()
    module_map: PaperRuntimeModuleMap = field(default_factory=PaperRuntimeModuleMap)
    duplicate_review: PaperRuntimeReview = field(
        default_factory=lambda: PaperRuntimeReview("duplicates", 0, False)
    )
    dependency_review: PaperRuntimeReview = field(
        default_factory=lambda: PaperRuntimeReview("dependencies", 0, False)
    )
    entrypoint_review: PaperRuntimeReview = field(
        default_factory=lambda: PaperRuntimeReview("entrypoints", 0, False)
    )
    integration_gap_review: PaperRuntimeReview = field(
        default_factory=lambda: PaperRuntimeReview("integration_gaps", 0, False)
    )
    recommendations: tuple[PaperRuntimePreReviewRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
