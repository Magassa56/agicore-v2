"""Models for offline AGIcore paper trading runtime decision review."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperRuntimeDecisionReviewState(StrEnum):
    NOT_READY = "NOT_READY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    PARTIALLY_READY = "PARTIALLY_READY"
    READY_FOR_PAPER_RUNTIME_DESIGN = "READY_FOR_PAPER_RUNTIME_DESIGN"
    READY_FOR_PAPER_TRADING_RUNTIME = "READY_FOR_PAPER_TRADING_RUNTIME"
    BLOCKED_BY_INTEGRATION_GAPS = "BLOCKED_BY_INTEGRATION_GAPS"


class PaperRuntimeDecision(StrEnum):
    BLOCK_RUNTIME_CREATION = "BLOCK_RUNTIME_CREATION"
    REQUIRE_INTEGRATION_CLEANUP = "REQUIRE_INTEGRATION_CLEANUP"
    REQUIRE_ENTRYPOINT_FIXES = "REQUIRE_ENTRYPOINT_FIXES"
    REQUIRE_DUPLICATE_REDUCTION = "REQUIRE_DUPLICATE_REDUCTION"
    APPROVE_PAPER_RUNTIME_DESIGN = "APPROVE_PAPER_RUNTIME_DESIGN"
    APPROVE_PAPER_TRADING_RUNTIME_CREATION = "APPROVE_PAPER_TRADING_RUNTIME_CREATION"


class PaperRuntimeDecisionRisk(StrEnum):
    MODULE_COHERENCE_GAP = "MODULE_COHERENCE_GAP"
    DUPLICATE_LAYER_CONFLICT = "DUPLICATE_LAYER_CONFLICT"
    ENTRYPOINT_AMBIGUITY = "ENTRYPOINT_AMBIGUITY"
    SAFETY_CHAIN_INCOMPLETE = "SAFETY_CHAIN_INCOMPLETE"
    ROLLBACK_CHAIN_INCOMPLETE = "ROLLBACK_CHAIN_INCOMPLETE"
    OBSERVABILITY_CHAIN_INCOMPLETE = "OBSERVABILITY_CHAIN_INCOMPLETE"
    HUMAN_SUPERVISION_GAP = "HUMAN_SUPERVISION_GAP"
    MOCK_TO_PAPER_TRANSITION_GAP = "MOCK_TO_PAPER_TRANSITION_GAP"
    RUNTIME_SCOPE_UNCLEAR = "RUNTIME_SCOPE_UNCLEAR"
    PREMATURE_RUNTIME_CREATION = "PREMATURE_RUNTIME_CREATION"


class PaperRuntimeDecisionRecommendation(StrEnum):
    BLOCK_PAPER_RUNTIME_CREATION = "BLOCK_PAPER_RUNTIME_CREATION"
    REPAIR_MODULE_COHERENCE = "REPAIR_MODULE_COHERENCE"
    REDUCE_DUPLICATE_LAYERS = "REDUCE_DUPLICATE_LAYERS"
    CLARIFY_RUNTIME_ENTRYPOINTS = "CLARIFY_RUNTIME_ENTRYPOINTS"
    COMPLETE_SAFETY_CHAIN = "COMPLETE_SAFETY_CHAIN"
    COMPLETE_ROLLBACK_CHAIN = "COMPLETE_ROLLBACK_CHAIN"
    COMPLETE_OBSERVABILITY_CHAIN = "COMPLETE_OBSERVABILITY_CHAIN"
    COMPLETE_HUMAN_SUPERVISION_CHAIN = "COMPLETE_HUMAN_SUPERVISION_CHAIN"
    COMPLETE_MOCK_TO_PAPER_TRANSITION = "COMPLETE_MOCK_TO_PAPER_TRANSITION"
    LOCK_RUNTIME_SCOPE = "LOCK_RUNTIME_SCOPE"
    KEEP_RUNTIME_CREATION_BLOCKED = "KEEP_RUNTIME_CREATION_BLOCKED"
    RUN_PAPER_RUNTIME_DECISION_REVIEW_SUITE = "RUN_PAPER_RUNTIME_DECISION_REVIEW_SUITE"
    APPROVE_RUNTIME_DESIGN_REVIEW = "APPROVE_RUNTIME_DESIGN_REVIEW"
    APPROVE_RUNTIME_CREATION_AFTER_MANUAL_REVIEW = (
        "APPROVE_RUNTIME_CREATION_AFTER_MANUAL_REVIEW"
    )


@dataclass(frozen=True)
class PaperRuntimeDecisionReviewInput:
    paper_runtime_pre_review: Any = None
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
    human_validated_paper_session: Any = None
    supervised_paper_session: Any = None
    module_layers: tuple[str, ...] = ()
    coherent_module_chain: bool | None = None
    duplicate_layers: tuple[str, ...] = ()
    runtime_entrypoints: tuple[str, ...] = ()
    runtime_entrypoints_required: tuple[str, ...] = ()
    safety_chain_links: tuple[str, ...] = ()
    rollback_chain_links: tuple[str, ...] = ()
    observability_chain_links: tuple[str, ...] = ()
    human_supervision_links: tuple[str, ...] = ()
    mock_to_paper_transition_links: tuple[str, ...] = ()
    integration_gaps: tuple[str, ...] = ()
    runtime_scope_locked: bool | None = None
    no_runtime_implementation_created: bool | None = None
    design_review_approved: bool | None = None
    runtime_creation_approved: bool | None = None
    offline_mode_enforced: bool | None = None
    no_real_broker: bool | None = None
    no_api_key_read: bool | None = None
    no_http_transport: bool | None = None
    no_websocket_transport: bool | None = None
    no_socket_transport: bool | None = None
    no_external_api: bool | None = None
    no_real_order: bool | None = None
    module_coherence_score: int | None = None
    duplicate_score: int | None = None
    entrypoint_score: int | None = None
    safety_chain_score: int | None = None
    rollback_chain_score: int | None = None
    observability_chain_score: int | None = None
    human_supervision_score: int | None = None
    mock_to_paper_transition_score: int | None = None
    runtime_decision_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperRuntimeDecisionReview:
    name: str
    score: int
    passed: bool
    risks: tuple[PaperRuntimeDecisionRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperRuntimeDecisionReviewScore:
    overall_score: int
    module_coherence_score: int
    duplicate_score: int
    entrypoint_score: int
    safety_chain_score: int
    rollback_chain_score: int
    observability_chain_score: int
    human_supervision_score: int
    mock_to_paper_transition_score: int
    runtime_decision_score: int


@dataclass(frozen=True)
class PaperRuntimeDecisionReviewResult:
    state: PaperRuntimeDecisionReviewState
    decision: PaperRuntimeDecision
    decision_review_score: int
    score_breakdown: PaperRuntimeDecisionReviewScore
    risks: tuple[PaperRuntimeDecisionRisk, ...] = ()
    runtime_readiness_decision: PaperRuntimeDecisionReview = field(
        default_factory=lambda: PaperRuntimeDecisionReview("runtime_readiness_decision", 0, False)
    )
    module_coherence: PaperRuntimeDecisionReview = field(
        default_factory=lambda: PaperRuntimeDecisionReview("module_coherence", 0, False)
    )
    duplicate_layers: PaperRuntimeDecisionReview = field(
        default_factory=lambda: PaperRuntimeDecisionReview("duplicate_layers", 0, False)
    )
    runtime_entrypoints: PaperRuntimeDecisionReview = field(
        default_factory=lambda: PaperRuntimeDecisionReview("runtime_entrypoints", 0, False)
    )
    safety_chain: PaperRuntimeDecisionReview = field(
        default_factory=lambda: PaperRuntimeDecisionReview("safety_chain", 0, False)
    )
    rollback_chain: PaperRuntimeDecisionReview = field(
        default_factory=lambda: PaperRuntimeDecisionReview("rollback_chain", 0, False)
    )
    observability_chain: PaperRuntimeDecisionReview = field(
        default_factory=lambda: PaperRuntimeDecisionReview("observability_chain", 0, False)
    )
    human_supervision_chain: PaperRuntimeDecisionReview = field(
        default_factory=lambda: PaperRuntimeDecisionReview("human_supervision_chain", 0, False)
    )
    mock_to_paper_transition: PaperRuntimeDecisionReview = field(
        default_factory=lambda: PaperRuntimeDecisionReview("mock_to_paper_transition", 0, False)
    )
    recommendations: tuple[PaperRuntimeDecisionRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
