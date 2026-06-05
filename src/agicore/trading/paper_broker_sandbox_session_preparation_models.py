"""Models for the offline AGIcore Paper Broker Sandbox Session Preparation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerSandboxSessionPreparationState(StrEnum):
    NOT_READY = "NOT_READY"
    PREPARATION_REVIEW_REQUIRED = "PREPARATION_REVIEW_REQUIRED"
    PARTIALLY_PREPARED = "PARTIALLY_PREPARED"
    SANDBOX_SESSION_PREPARED = "SANDBOX_SESSION_PREPARED"
    READY_FOR_PAPER_BROKER_SANDBOX_SESSION_REVIEW = "READY_FOR_PAPER_BROKER_SANDBOX_SESSION_REVIEW"


class PaperBrokerSandboxSessionPreparationDecision(StrEnum):
    BLOCK_BROKER_SANDBOX_SESSION = "BLOCK_BROKER_SANDBOX_SESSION"
    REQUIRE_FORWARD_TEST_PLAN_FIXES = "REQUIRE_FORWARD_TEST_PLAN_FIXES"
    REQUIRE_BOUNDARY_FIXES = "REQUIRE_BOUNDARY_FIXES"
    REQUIRE_ADAPTER_REQUIREMENT_FIXES = "REQUIRE_ADAPTER_REQUIREMENT_FIXES"
    REQUIRE_OBSERVABILITY_FIXES = "REQUIRE_OBSERVABILITY_FIXES"
    REQUIRE_ROLLBACK_FIXES = "REQUIRE_ROLLBACK_FIXES"
    REQUIRE_KILL_SWITCH_FIXES = "REQUIRE_KILL_SWITCH_FIXES"
    REQUIRE_SUPERVISION_FIXES = "REQUIRE_SUPERVISION_FIXES"
    APPROVE_PAPER_BROKER_SANDBOX_SESSION_PREPARATION = "APPROVE_PAPER_BROKER_SANDBOX_SESSION_PREPARATION"


class PaperBrokerSandboxSessionPreparationRisk(StrEnum):
    FORWARD_TEST_PLAN_NOT_APPROVED = "FORWARD_TEST_PLAN_NOT_APPROVED"
    SANDBOX_SCOPE_UNCLEAR = "SANDBOX_SCOPE_UNCLEAR"
    SANDBOX_BOUNDARY_GAP = "SANDBOX_BOUNDARY_GAP"
    PAPER_BROKER_ADAPTER_REQUIREMENT_GAP = "PAPER_BROKER_ADAPTER_REQUIREMENT_GAP"
    MOCK_TO_BROKER_TRANSITION_GAP = "MOCK_TO_BROKER_TRANSITION_GAP"
    CONNECTION_PRECONDITION_GAP = "CONNECTION_PRECONDITION_GAP"
    ORDER_PRECONDITION_GAP = "ORDER_PRECONDITION_GAP"
    POSITION_PRECONDITION_GAP = "POSITION_PRECONDITION_GAP"
    ACCOUNT_PRECONDITION_GAP = "ACCOUNT_PRECONDITION_GAP"
    OBSERVABILITY_REQUIREMENT_GAP = "OBSERVABILITY_REQUIREMENT_GAP"
    ROLLBACK_REQUIREMENT_GAP = "ROLLBACK_REQUIREMENT_GAP"
    KILL_SWITCH_REQUIREMENT_GAP = "KILL_SWITCH_REQUIREMENT_GAP"
    HUMAN_SUPERVISION_REQUIREMENT_GAP = "HUMAN_SUPERVISION_REQUIREMENT_GAP"
    PREMATURE_SANDBOX_SESSION = "PREMATURE_SANDBOX_SESSION"


class PaperBrokerSandboxSessionPreparationRecommendation(StrEnum):
    HOLD_PAPER_BROKER_SANDBOX_SESSION = "HOLD_PAPER_BROKER_SANDBOX_SESSION"
    APPROVE_FORWARD_TEST_PLAN_FIRST = "APPROVE_FORWARD_TEST_PLAN_FIRST"
    CLARIFY_SANDBOX_SESSION_SCOPE = "CLARIFY_SANDBOX_SESSION_SCOPE"
    DEFINE_SANDBOX_BOUNDARIES = "DEFINE_SANDBOX_BOUNDARIES"
    DEFINE_PAPER_BROKER_ADAPTER_REQUIREMENTS = "DEFINE_PAPER_BROKER_ADAPTER_REQUIREMENTS"
    DEFINE_MOCK_TO_BROKER_TRANSITION_REQUIREMENTS = "DEFINE_MOCK_TO_BROKER_TRANSITION_REQUIREMENTS"
    DEFINE_SANDBOX_CONNECTION_PRECONDITIONS = "DEFINE_SANDBOX_CONNECTION_PRECONDITIONS"
    DEFINE_SANDBOX_ORDER_PRECONDITIONS = "DEFINE_SANDBOX_ORDER_PRECONDITIONS"
    DEFINE_SANDBOX_POSITION_PRECONDITIONS = "DEFINE_SANDBOX_POSITION_PRECONDITIONS"
    DEFINE_SANDBOX_ACCOUNT_PRECONDITIONS = "DEFINE_SANDBOX_ACCOUNT_PRECONDITIONS"
    DEFINE_SANDBOX_OBSERVABILITY_REQUIREMENTS = "DEFINE_SANDBOX_OBSERVABILITY_REQUIREMENTS"
    DEFINE_SANDBOX_ROLLBACK_REQUIREMENTS = "DEFINE_SANDBOX_ROLLBACK_REQUIREMENTS"
    DEFINE_SANDBOX_KILL_SWITCH_REQUIREMENTS = "DEFINE_SANDBOX_KILL_SWITCH_REQUIREMENTS"
    DEFINE_SANDBOX_HUMAN_SUPERVISION_REQUIREMENTS = "DEFINE_SANDBOX_HUMAN_SUPERVISION_REQUIREMENTS"
    DELAY_SANDBOX_SESSION = "DELAY_SANDBOX_SESSION"
    RUN_BROKER_SANDBOX_PREPARATION_REVIEW_SUITE = "RUN_BROKER_SANDBOX_PREPARATION_REVIEW_SUITE"
    APPROVE_PAPER_BROKER_SANDBOX_SESSION_REVIEW = "APPROVE_PAPER_BROKER_SANDBOX_SESSION_REVIEW"


@dataclass(frozen=True)
class PaperBrokerSandboxSessionPreparationInput:
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
    forward_test_plan_approved: bool | None = None
    sandbox_session_scope_defined: bool | None = None
    sandbox_session_boundaries_defined: bool | None = None
    paper_broker_adapter_requirements_defined: bool | None = None
    mock_to_broker_transition_requirements_defined: bool | None = None
    sandbox_connection_preconditions_defined: bool | None = None
    sandbox_order_preconditions_defined: bool | None = None
    sandbox_position_preconditions_defined: bool | None = None
    sandbox_account_preconditions_defined: bool | None = None
    sandbox_observability_requirements_defined: bool | None = None
    sandbox_rollback_requirements_defined: bool | None = None
    sandbox_kill_switch_requirements_defined: bool | None = None
    sandbox_human_supervision_requirements_defined: bool | None = None
    sandbox_session_requested: bool | None = None
    offline_mode_enforced: bool | None = None
    sandbox_mode_enforced: bool | None = None
    no_real_broker: bool | None = None
    no_alpaca_real: bool | None = None
    no_api_key_read: bool | None = None
    no_http_transport: bool | None = None
    no_websocket_transport: bool | None = None
    no_socket_transport: bool | None = None
    no_external_api: bool | None = None
    no_real_order: bool | None = None
    forward_test_plan_readiness_score: int | None = None
    sandbox_session_scope_score: int | None = None
    sandbox_session_boundaries_score: int | None = None
    paper_broker_adapter_requirements_score: int | None = None
    mock_to_broker_transition_requirements_score: int | None = None
    sandbox_connection_preconditions_score: int | None = None
    sandbox_order_preconditions_score: int | None = None
    sandbox_position_preconditions_score: int | None = None
    sandbox_account_preconditions_score: int | None = None
    sandbox_observability_requirements_score: int | None = None
    sandbox_rollback_requirements_score: int | None = None
    sandbox_kill_switch_requirements_score: int | None = None
    sandbox_human_supervision_requirements_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerSandboxSessionPreparationSection:
    name: str
    score: int
    defined: bool
    risks: tuple[PaperBrokerSandboxSessionPreparationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerSandboxSessionPreparationScore:
    overall_score: int
    forward_test_plan_readiness_score: int
    sandbox_session_scope_score: int
    sandbox_session_boundaries_score: int
    paper_broker_adapter_requirements_score: int
    mock_to_broker_transition_requirements_score: int
    sandbox_connection_preconditions_score: int
    sandbox_order_preconditions_score: int
    sandbox_position_preconditions_score: int
    sandbox_account_preconditions_score: int
    sandbox_observability_requirements_score: int
    sandbox_rollback_requirements_score: int
    sandbox_kill_switch_requirements_score: int
    sandbox_human_supervision_requirements_score: int


@dataclass(frozen=True)
class PaperBrokerSandboxSessionPreparationResult:
    state: PaperBrokerSandboxSessionPreparationState
    decision: PaperBrokerSandboxSessionPreparationDecision
    preparation_score: int
    score_breakdown: PaperBrokerSandboxSessionPreparationScore
    risks: tuple[PaperBrokerSandboxSessionPreparationRisk, ...] = ()
    forward_test_plan_readiness: PaperBrokerSandboxSessionPreparationSection = field(default_factory=lambda: PaperBrokerSandboxSessionPreparationSection("forward_test_plan_readiness", 0, False))
    sandbox_session_scope: PaperBrokerSandboxSessionPreparationSection = field(default_factory=lambda: PaperBrokerSandboxSessionPreparationSection("sandbox_session_scope", 0, False))
    sandbox_session_boundaries: PaperBrokerSandboxSessionPreparationSection = field(default_factory=lambda: PaperBrokerSandboxSessionPreparationSection("sandbox_session_boundaries", 0, False))
    paper_broker_adapter_requirements: PaperBrokerSandboxSessionPreparationSection = field(default_factory=lambda: PaperBrokerSandboxSessionPreparationSection("paper_broker_adapter_requirements", 0, False))
    mock_to_broker_transition_requirements: PaperBrokerSandboxSessionPreparationSection = field(default_factory=lambda: PaperBrokerSandboxSessionPreparationSection("mock_to_broker_transition_requirements", 0, False))
    sandbox_connection_preconditions: PaperBrokerSandboxSessionPreparationSection = field(default_factory=lambda: PaperBrokerSandboxSessionPreparationSection("sandbox_connection_preconditions", 0, False))
    sandbox_order_preconditions: PaperBrokerSandboxSessionPreparationSection = field(default_factory=lambda: PaperBrokerSandboxSessionPreparationSection("sandbox_order_preconditions", 0, False))
    sandbox_position_preconditions: PaperBrokerSandboxSessionPreparationSection = field(default_factory=lambda: PaperBrokerSandboxSessionPreparationSection("sandbox_position_preconditions", 0, False))
    sandbox_account_preconditions: PaperBrokerSandboxSessionPreparationSection = field(default_factory=lambda: PaperBrokerSandboxSessionPreparationSection("sandbox_account_preconditions", 0, False))
    sandbox_observability_requirements: PaperBrokerSandboxSessionPreparationSection = field(default_factory=lambda: PaperBrokerSandboxSessionPreparationSection("sandbox_observability_requirements", 0, False))
    sandbox_rollback_requirements: PaperBrokerSandboxSessionPreparationSection = field(default_factory=lambda: PaperBrokerSandboxSessionPreparationSection("sandbox_rollback_requirements", 0, False))
    sandbox_kill_switch_requirements: PaperBrokerSandboxSessionPreparationSection = field(default_factory=lambda: PaperBrokerSandboxSessionPreparationSection("sandbox_kill_switch_requirements", 0, False))
    sandbox_human_supervision_requirements: PaperBrokerSandboxSessionPreparationSection = field(default_factory=lambda: PaperBrokerSandboxSessionPreparationSection("sandbox_human_supervision_requirements", 0, False))
    recommendations: tuple[PaperBrokerSandboxSessionPreparationRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
