"""Models for offline AGIcore Paper Trading Runtime integration review."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperRuntimeIntegrationReviewState(StrEnum):
    NOT_READY = "NOT_READY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    PARTIALLY_INTEGRATED = "PARTIALLY_INTEGRATED"
    INTEGRATION_READY = "INTEGRATION_READY"
    READY_FOR_PAPER_RUNTIME_TEST_RUN = "READY_FOR_PAPER_RUNTIME_TEST_RUN"


class PaperRuntimeIntegrationDecision(StrEnum):
    INTEGRATION_BLOCKED = "INTEGRATION_BLOCKED"
    INTEGRATION_CLEANUP_REQUIRED = "INTEGRATION_CLEANUP_REQUIRED"
    INTEGRATION_PARTIALLY_READY = "INTEGRATION_PARTIALLY_READY"
    INTEGRATION_READY = "INTEGRATION_READY"
    READY_FOR_PAPER_RUNTIME_TEST_RUN = "READY_FOR_PAPER_RUNTIME_TEST_RUN"


class PaperRuntimeIntegrationRisk(StrEnum):
    RUNTIME_DESIGN_MISMATCH = "RUNTIME_DESIGN_MISMATCH"
    DECISION_REVIEW_MISMATCH = "DECISION_REVIEW_MISMATCH"
    FULL_SESSION_MISMATCH = "FULL_SESSION_MISMATCH"
    SIMULATED_MARKET_MISMATCH = "SIMULATED_MARKET_MISMATCH"
    MOCK_ALPACA_MISMATCH = "MOCK_ALPACA_MISMATCH"
    MOCK_CONNECTIVITY_MISMATCH = "MOCK_CONNECTIVITY_MISMATCH"
    OBSERVABILITY_INTEGRATION_GAP = "OBSERVABILITY_INTEGRATION_GAP"
    ROLLBACK_INTEGRATION_GAP = "ROLLBACK_INTEGRATION_GAP"
    KILL_SWITCH_INTEGRATION_GAP = "KILL_SWITCH_INTEGRATION_GAP"
    HUMAN_SUPERVISION_INTEGRATION_GAP = "HUMAN_SUPERVISION_INTEGRATION_GAP"
    RUNTIME_REPORT_GAP = "RUNTIME_REPORT_GAP"
    INTEGRATION_SCOPE_DRIFT = "INTEGRATION_SCOPE_DRIFT"


class PaperRuntimeIntegrationRecommendation(StrEnum):
    HOLD_TEST_RUN_APPROVAL = "HOLD_TEST_RUN_APPROVAL"
    ALIGN_RUNTIME_DESIGN = "ALIGN_RUNTIME_DESIGN"
    ALIGN_DECISION_REVIEW = "ALIGN_DECISION_REVIEW"
    ALIGN_FULL_SESSION = "ALIGN_FULL_SESSION"
    ALIGN_SIMULATED_MARKET = "ALIGN_SIMULATED_MARKET"
    ALIGN_MOCK_ALPACA = "ALIGN_MOCK_ALPACA"
    ALIGN_MOCK_CONNECTIVITY = "ALIGN_MOCK_CONNECTIVITY"
    REPAIR_OBSERVABILITY_INTEGRATION = "REPAIR_OBSERVABILITY_INTEGRATION"
    REPAIR_ROLLBACK_INTEGRATION = "REPAIR_ROLLBACK_INTEGRATION"
    REPAIR_KILL_SWITCH_INTEGRATION = "REPAIR_KILL_SWITCH_INTEGRATION"
    REPAIR_HUMAN_SUPERVISION_INTEGRATION = "REPAIR_HUMAN_SUPERVISION_INTEGRATION"
    COMPLETE_RUNTIME_REPORT = "COMPLETE_RUNTIME_REPORT"
    LOCK_INTEGRATION_SCOPE = "LOCK_INTEGRATION_SCOPE"
    RUN_INTEGRATION_REVIEW_SUITE = "RUN_INTEGRATION_REVIEW_SUITE"
    APPROVE_INTEGRATION_AFTER_MANUAL_REVIEW = "APPROVE_INTEGRATION_AFTER_MANUAL_REVIEW"
    APPROVE_TEST_RUN_AFTER_MANUAL_REVIEW = "APPROVE_TEST_RUN_AFTER_MANUAL_REVIEW"


@dataclass(frozen=True)
class PaperRuntimeIntegrationReviewInput:
    paper_trading_runtime: Any = None
    paper_trading_runtime_design: Any = None
    paper_runtime_decision_review: Any = None
    paper_runtime_pre_review: Any = None
    full_paper_session: Any = None
    simulated_market_session: Any = None
    mock_alpaca_session: Any = None
    mock_connectivity_layer: Any = None
    alpaca_paper_connectivity_readiness: Any = None
    broker_paper_sandbox: Any = None
    observability_verification: Any = None
    rollback_verification: Any = None
    kill_switch_verification: Any = None
    human_validated_paper_session: Any = None
    supervised_paper_session: Any = None
    runtime_entrypoint_present: bool | None = None
    runtime_state_machine_aligned: bool | None = None
    runtime_design_approved: bool | None = None
    decision_review_approved: bool | None = None
    full_session_chain_aligned: bool | None = None
    simulated_market_chain_aligned: bool | None = None
    mock_alpaca_chain_aligned: bool | None = None
    mock_connectivity_chain_aligned: bool | None = None
    observability_events_linked: bool | None = None
    observability_reported: bool | None = None
    rollback_hook_linked: bool | None = None
    rollback_stop_state_supported: bool | None = None
    kill_switch_hook_linked: bool | None = None
    kill_switch_stop_state_supported: bool | None = None
    human_supervision_hook_linked: bool | None = None
    human_pause_state_supported: bool | None = None
    runtime_report_available: bool | None = None
    runtime_report_complete: bool | None = None
    integration_scope_locked: bool | None = None
    offline_mode_enforced: bool | None = None
    sandbox_mode_enforced: bool | None = None
    no_real_broker: bool | None = None
    no_api_key_read: bool | None = None
    no_http_transport: bool | None = None
    no_websocket_transport: bool | None = None
    no_socket_transport: bool | None = None
    no_external_api: bool | None = None
    no_real_order: bool | None = None
    ready_for_test_run: bool | None = None
    runtime_design_alignment_score: int | None = None
    decision_review_alignment_score: int | None = None
    full_session_alignment_score: int | None = None
    simulated_market_alignment_score: int | None = None
    mock_alpaca_alignment_score: int | None = None
    mock_connectivity_alignment_score: int | None = None
    observability_integration_score: int | None = None
    rollback_integration_score: int | None = None
    kill_switch_integration_score: int | None = None
    human_supervision_integration_score: int | None = None
    runtime_report_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperRuntimeIntegrationReview:
    name: str
    score: int
    passed: bool
    risks: tuple[PaperRuntimeIntegrationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperRuntimeIntegrationReviewScore:
    overall_score: int
    runtime_design_alignment_score: int
    decision_review_alignment_score: int
    full_session_alignment_score: int
    simulated_market_alignment_score: int
    mock_alpaca_alignment_score: int
    mock_connectivity_alignment_score: int
    observability_integration_score: int
    rollback_integration_score: int
    kill_switch_integration_score: int
    human_supervision_integration_score: int
    runtime_report_score: int


@dataclass(frozen=True)
class PaperRuntimeIntegrationReviewResult:
    state: PaperRuntimeIntegrationReviewState
    decision: PaperRuntimeIntegrationDecision
    integration_review_score: int
    score_breakdown: PaperRuntimeIntegrationReviewScore
    risks: tuple[PaperRuntimeIntegrationRisk, ...] = ()
    runtime_design_alignment: PaperRuntimeIntegrationReview = field(default_factory=lambda: PaperRuntimeIntegrationReview("runtime_design_alignment", 0, False))
    decision_review_alignment: PaperRuntimeIntegrationReview = field(default_factory=lambda: PaperRuntimeIntegrationReview("decision_review_alignment", 0, False))
    full_session_alignment: PaperRuntimeIntegrationReview = field(default_factory=lambda: PaperRuntimeIntegrationReview("full_session_alignment", 0, False))
    simulated_market_alignment: PaperRuntimeIntegrationReview = field(default_factory=lambda: PaperRuntimeIntegrationReview("simulated_market_alignment", 0, False))
    mock_alpaca_alignment: PaperRuntimeIntegrationReview = field(default_factory=lambda: PaperRuntimeIntegrationReview("mock_alpaca_alignment", 0, False))
    mock_connectivity_alignment: PaperRuntimeIntegrationReview = field(default_factory=lambda: PaperRuntimeIntegrationReview("mock_connectivity_alignment", 0, False))
    observability_integration: PaperRuntimeIntegrationReview = field(default_factory=lambda: PaperRuntimeIntegrationReview("observability_integration", 0, False))
    rollback_integration: PaperRuntimeIntegrationReview = field(default_factory=lambda: PaperRuntimeIntegrationReview("rollback_integration", 0, False))
    kill_switch_integration: PaperRuntimeIntegrationReview = field(default_factory=lambda: PaperRuntimeIntegrationReview("kill_switch_integration", 0, False))
    human_supervision_integration: PaperRuntimeIntegrationReview = field(default_factory=lambda: PaperRuntimeIntegrationReview("human_supervision_integration", 0, False))
    runtime_report_integration: PaperRuntimeIntegrationReview = field(default_factory=lambda: PaperRuntimeIntegrationReview("runtime_report_integration", 0, False))
    recommendations: tuple[PaperRuntimeIntegrationRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""

