"""Models for the offline AGIcore Paper Broker Sandbox Session Review."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerSandboxSessionReviewState(StrEnum):
    NOT_READY = "NOT_READY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    PARTIALLY_READY = "PARTIALLY_READY"
    SANDBOX_SESSION_REVIEW_READY = "SANDBOX_SESSION_REVIEW_READY"
    READY_FOR_PAPER_BROKER_SANDBOX_SESSION = "READY_FOR_PAPER_BROKER_SANDBOX_SESSION"


class PaperBrokerSandboxSessionReviewDecision(StrEnum):
    BLOCK_PAPER_BROKER_SANDBOX_SESSION = "BLOCK_PAPER_BROKER_SANDBOX_SESSION"
    REQUIRE_PREPARATION_FIXES = "REQUIRE_PREPARATION_FIXES"
    REQUIRE_BOUNDARY_FIXES = "REQUIRE_BOUNDARY_FIXES"
    REQUIRE_ADAPTER_FIXES = "REQUIRE_ADAPTER_FIXES"
    REQUIRE_CONNECTION_FIXES = "REQUIRE_CONNECTION_FIXES"
    REQUIRE_ORDER_FIXES = "REQUIRE_ORDER_FIXES"
    REQUIRE_POSITION_FIXES = "REQUIRE_POSITION_FIXES"
    REQUIRE_ACCOUNT_FIXES = "REQUIRE_ACCOUNT_FIXES"
    REQUIRE_OBSERVABILITY_FIXES = "REQUIRE_OBSERVABILITY_FIXES"
    REQUIRE_ROLLBACK_FIXES = "REQUIRE_ROLLBACK_FIXES"
    REQUIRE_KILL_SWITCH_FIXES = "REQUIRE_KILL_SWITCH_FIXES"
    REQUIRE_SUPERVISION_FIXES = "REQUIRE_SUPERVISION_FIXES"
    APPROVE_PAPER_BROKER_SANDBOX_SESSION = "APPROVE_PAPER_BROKER_SANDBOX_SESSION"


class PaperBrokerSandboxSessionReviewRisk(StrEnum):
    SANDBOX_PREPARATION_NOT_APPROVED = "SANDBOX_PREPARATION_NOT_APPROVED"
    SANDBOX_SCOPE_UNCLEAR = "SANDBOX_SCOPE_UNCLEAR"
    SANDBOX_BOUNDARY_INCOMPLETE = "SANDBOX_BOUNDARY_INCOMPLETE"
    PAPER_BROKER_ADAPTER_REQUIREMENT_INCOMPLETE = "PAPER_BROKER_ADAPTER_REQUIREMENT_INCOMPLETE"
    MOCK_TO_BROKER_TRANSITION_NOT_READY = "MOCK_TO_BROKER_TRANSITION_NOT_READY"
    CONNECTION_READINESS_GAP = "CONNECTION_READINESS_GAP"
    ORDER_READINESS_GAP = "ORDER_READINESS_GAP"
    POSITION_READINESS_GAP = "POSITION_READINESS_GAP"
    ACCOUNT_READINESS_GAP = "ACCOUNT_READINESS_GAP"
    OBSERVABILITY_READINESS_GAP = "OBSERVABILITY_READINESS_GAP"
    ROLLBACK_READINESS_GAP = "ROLLBACK_READINESS_GAP"
    KILL_SWITCH_READINESS_GAP = "KILL_SWITCH_READINESS_GAP"
    HUMAN_SUPERVISION_READINESS_GAP = "HUMAN_SUPERVISION_READINESS_GAP"
    PREMATURE_BROKER_SANDBOX_SESSION = "PREMATURE_BROKER_SANDBOX_SESSION"


class PaperBrokerSandboxSessionReviewRecommendation(StrEnum):
    HOLD_PAPER_BROKER_SANDBOX_SESSION = "HOLD_PAPER_BROKER_SANDBOX_SESSION"
    APPROVE_SANDBOX_PREPARATION_FIRST = "APPROVE_SANDBOX_PREPARATION_FIRST"
    CLARIFY_BROKER_SANDBOX_SCOPE = "CLARIFY_BROKER_SANDBOX_SCOPE"
    COMPLETE_BROKER_SANDBOX_BOUNDARIES = "COMPLETE_BROKER_SANDBOX_BOUNDARIES"
    COMPLETE_PAPER_BROKER_ADAPTER_REQUIREMENTS = "COMPLETE_PAPER_BROKER_ADAPTER_REQUIREMENTS"
    COMPLETE_MOCK_TO_BROKER_TRANSITION_REVIEW = "COMPLETE_MOCK_TO_BROKER_TRANSITION_REVIEW"
    COMPLETE_SANDBOX_CONNECTION_REVIEW = "COMPLETE_SANDBOX_CONNECTION_REVIEW"
    COMPLETE_SANDBOX_ORDER_REVIEW = "COMPLETE_SANDBOX_ORDER_REVIEW"
    COMPLETE_SANDBOX_POSITION_REVIEW = "COMPLETE_SANDBOX_POSITION_REVIEW"
    COMPLETE_SANDBOX_ACCOUNT_REVIEW = "COMPLETE_SANDBOX_ACCOUNT_REVIEW"
    COMPLETE_SANDBOX_OBSERVABILITY_REVIEW = "COMPLETE_SANDBOX_OBSERVABILITY_REVIEW"
    COMPLETE_SANDBOX_ROLLBACK_REVIEW = "COMPLETE_SANDBOX_ROLLBACK_REVIEW"
    COMPLETE_SANDBOX_KILL_SWITCH_REVIEW = "COMPLETE_SANDBOX_KILL_SWITCH_REVIEW"
    COMPLETE_SANDBOX_HUMAN_SUPERVISION_REVIEW = "COMPLETE_SANDBOX_HUMAN_SUPERVISION_REVIEW"
    DELAY_PAPER_BROKER_SANDBOX_SESSION = "DELAY_PAPER_BROKER_SANDBOX_SESSION"
    RUN_PAPER_BROKER_SANDBOX_SESSION_REVIEW_SUITE = "RUN_PAPER_BROKER_SANDBOX_SESSION_REVIEW_SUITE"
    APPROVE_PAPER_BROKER_SANDBOX_SESSION = "APPROVE_PAPER_BROKER_SANDBOX_SESSION"


@dataclass(frozen=True)
class PaperBrokerSandboxSessionReviewInput:
    paper_broker_sandbox_session_preparation: Any = None
    paper_runtime_forward_test_plan: Any = None
    supervised_paper_runtime_trial: Any = None
    official_paper_validation_report: Any = None
    paper_runtime_validation: Any = None
    paper_runtime_release_candidate: Any = None
    paper_trading_runtime: Any = None
    paper_broker_adapter: Any = None
    alpaca_paper_adapter: Any = None
    broker_paper_sandbox: Any = None
    mock_alpaca_session: Any = None
    mock_connectivity_layer: Any = None
    observability_verification: Any = None
    rollback_verification: Any = None
    kill_switch_verification: Any = None
    human_validated_paper_session: Any = None
    supervised_paper_session: Any = None
    sandbox_preparation_approved: bool | None = None
    sandbox_preparation_reviewed: bool | None = None
    broker_sandbox_scope_reviewed: bool | None = None
    broker_sandbox_scope_clear: bool | None = None
    sandbox_scope_reviewed: bool | None = None
    sandbox_scope_clear: bool | None = None
    broker_sandbox_boundaries_reviewed: bool | None = None
    broker_sandbox_boundaries_complete: bool | None = None
    sandbox_boundaries_reviewed: bool | None = None
    sandbox_boundaries_complete: bool | None = None
    paper_broker_adapter_requirements_reviewed: bool | None = None
    paper_broker_adapter_requirements_complete: bool | None = None
    mock_to_broker_transition_reviewed: bool | None = None
    mock_to_broker_transition_ready: bool | None = None
    sandbox_connection_reviewed: bool | None = None
    sandbox_connection_ready: bool | None = None
    sandbox_order_reviewed: bool | None = None
    sandbox_order_ready: bool | None = None
    sandbox_position_reviewed: bool | None = None
    sandbox_position_ready: bool | None = None
    sandbox_account_reviewed: bool | None = None
    sandbox_account_ready: bool | None = None
    sandbox_observability_reviewed: bool | None = None
    sandbox_observability_ready: bool | None = None
    sandbox_rollback_reviewed: bool | None = None
    sandbox_rollback_ready: bool | None = None
    sandbox_kill_switch_reviewed: bool | None = None
    sandbox_kill_switch_ready: bool | None = None
    sandbox_human_supervision_reviewed: bool | None = None
    sandbox_human_supervision_ready: bool | None = None
    paper_broker_sandbox_session_requested: bool | None = None
    sandbox_session_review_requested: bool | None = None
    offline_mode_enforced: bool | None = None
    sandbox_mode_enforced: bool | None = None
    no_real_broker: bool | None = None
    no_alpaca_real: bool | None = None
    no_api_key_read: bool | None = None
    no_http_transport: bool | None = None
    no_websocket_transport: bool | None = None
    no_socket_transport: bool | None = None
    no_external_api: bool | None = None
    no_external_ml: bool | None = None
    no_external_llm: bool | None = None
    no_live_execution: bool | None = None
    no_real_order: bool | None = None
    sandbox_preparation_readiness_score: int | None = None
    broker_sandbox_scope_score: int | None = None
    broker_sandbox_boundaries_score: int | None = None
    paper_broker_adapter_requirements_score: int | None = None
    mock_to_broker_transition_readiness_score: int | None = None
    sandbox_connection_readiness_score: int | None = None
    sandbox_order_readiness_score: int | None = None
    sandbox_position_readiness_score: int | None = None
    sandbox_account_readiness_score: int | None = None
    sandbox_observability_readiness_score: int | None = None
    sandbox_rollback_readiness_score: int | None = None
    sandbox_kill_switch_readiness_score: int | None = None
    sandbox_human_supervision_readiness_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerSandboxSessionReviewSection:
    name: str
    score: int
    passed: bool
    risks: tuple[PaperBrokerSandboxSessionReviewRisk, ...] = ()
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerSandboxSessionReviewScore:
    overall_score: int
    sandbox_preparation_readiness_score: int
    broker_sandbox_scope_score: int
    broker_sandbox_boundaries_score: int
    paper_broker_adapter_requirements_score: int
    mock_to_broker_transition_readiness_score: int
    sandbox_connection_readiness_score: int
    sandbox_order_readiness_score: int
    sandbox_position_readiness_score: int
    sandbox_account_readiness_score: int
    sandbox_observability_readiness_score: int
    sandbox_rollback_readiness_score: int
    sandbox_kill_switch_readiness_score: int
    sandbox_human_supervision_readiness_score: int


@dataclass(frozen=True)
class PaperBrokerSandboxSessionReviewResult:
    state: PaperBrokerSandboxSessionReviewState
    decision: PaperBrokerSandboxSessionReviewDecision
    review_score: int
    score_breakdown: PaperBrokerSandboxSessionReviewScore
    risks: tuple[PaperBrokerSandboxSessionReviewRisk, ...] = ()
    sandbox_preparation_readiness: PaperBrokerSandboxSessionReviewSection = field(
        default_factory=lambda: PaperBrokerSandboxSessionReviewSection("sandbox_preparation_readiness", 0, False)
    )
    broker_sandbox_scope: PaperBrokerSandboxSessionReviewSection = field(
        default_factory=lambda: PaperBrokerSandboxSessionReviewSection("broker_sandbox_scope", 0, False)
    )
    broker_sandbox_boundaries: PaperBrokerSandboxSessionReviewSection = field(
        default_factory=lambda: PaperBrokerSandboxSessionReviewSection("broker_sandbox_boundaries", 0, False)
    )
    paper_broker_adapter_requirements: PaperBrokerSandboxSessionReviewSection = field(
        default_factory=lambda: PaperBrokerSandboxSessionReviewSection("paper_broker_adapter_requirements", 0, False)
    )
    mock_to_broker_transition_readiness: PaperBrokerSandboxSessionReviewSection = field(
        default_factory=lambda: PaperBrokerSandboxSessionReviewSection("mock_to_broker_transition_readiness", 0, False)
    )
    sandbox_connection_readiness: PaperBrokerSandboxSessionReviewSection = field(
        default_factory=lambda: PaperBrokerSandboxSessionReviewSection("sandbox_connection_readiness", 0, False)
    )
    sandbox_order_readiness: PaperBrokerSandboxSessionReviewSection = field(
        default_factory=lambda: PaperBrokerSandboxSessionReviewSection("sandbox_order_readiness", 0, False)
    )
    sandbox_position_readiness: PaperBrokerSandboxSessionReviewSection = field(
        default_factory=lambda: PaperBrokerSandboxSessionReviewSection("sandbox_position_readiness", 0, False)
    )
    sandbox_account_readiness: PaperBrokerSandboxSessionReviewSection = field(
        default_factory=lambda: PaperBrokerSandboxSessionReviewSection("sandbox_account_readiness", 0, False)
    )
    sandbox_observability_readiness: PaperBrokerSandboxSessionReviewSection = field(
        default_factory=lambda: PaperBrokerSandboxSessionReviewSection("sandbox_observability_readiness", 0, False)
    )
    sandbox_rollback_readiness: PaperBrokerSandboxSessionReviewSection = field(
        default_factory=lambda: PaperBrokerSandboxSessionReviewSection("sandbox_rollback_readiness", 0, False)
    )
    sandbox_kill_switch_readiness: PaperBrokerSandboxSessionReviewSection = field(
        default_factory=lambda: PaperBrokerSandboxSessionReviewSection("sandbox_kill_switch_readiness", 0, False)
    )
    sandbox_human_supervision_readiness: PaperBrokerSandboxSessionReviewSection = field(
        default_factory=lambda: PaperBrokerSandboxSessionReviewSection("sandbox_human_supervision_readiness", 0, False)
    )
    recommendations: tuple[PaperBrokerSandboxSessionReviewRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""

