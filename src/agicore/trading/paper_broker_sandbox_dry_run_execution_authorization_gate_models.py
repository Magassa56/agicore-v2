"""Models for the offline AGIcore Paper Broker Sandbox Dry Run Execution Authorization Gate."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerSandboxDryRunExecutionAuthorizationGateState(StrEnum):
    NOT_AUTHORIZED = "NOT_AUTHORIZED"
    EXECUTION_AUTHORIZATION_REVIEW_REQUIRED = "EXECUTION_AUTHORIZATION_REVIEW_REQUIRED"
    PARTIALLY_AUTHORIZED = "PARTIALLY_AUTHORIZED"
    EXECUTION_AUTHORIZATION_GATE_READY = "EXECUTION_AUTHORIZATION_GATE_READY"
    READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_PLAN = (
        "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_PLAN"
    )


class PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision(StrEnum):
    BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION = "BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION"
    REQUIRE_EXECUTION_REVIEW_FIXES = "REQUIRE_EXECUTION_REVIEW_FIXES"
    REQUIRE_SCOPE_FIXES = "REQUIRE_SCOPE_FIXES"
    REQUIRE_BOUNDARY_FIXES = "REQUIRE_BOUNDARY_FIXES"
    REQUIRE_SCENARIO_FIXES = "REQUIRE_SCENARIO_FIXES"
    REQUIRE_SESSION_LIMIT_FIXES = "REQUIRE_SESSION_LIMIT_FIXES"
    REQUIRE_CONNECTION_AUTHORIZATION_FIXES = "REQUIRE_CONNECTION_AUTHORIZATION_FIXES"
    REQUIRE_ORDER_AUTHORIZATION_FIXES = "REQUIRE_ORDER_AUTHORIZATION_FIXES"
    REQUIRE_POSITION_AUTHORIZATION_FIXES = "REQUIRE_POSITION_AUTHORIZATION_FIXES"
    REQUIRE_ACCOUNT_AUTHORIZATION_FIXES = "REQUIRE_ACCOUNT_AUTHORIZATION_FIXES"
    REQUIRE_OBSERVABILITY_FIXES = "REQUIRE_OBSERVABILITY_FIXES"
    REQUIRE_ROLLBACK_FIXES = "REQUIRE_ROLLBACK_FIXES"
    REQUIRE_KILL_SWITCH_FIXES = "REQUIRE_KILL_SWITCH_FIXES"
    REQUIRE_SUPERVISION_FIXES = "REQUIRE_SUPERVISION_FIXES"
    REQUIRE_JOURNAL_FIXES = "REQUIRE_JOURNAL_FIXES"
    REQUIRE_STOP_CONDITION_FIXES = "REQUIRE_STOP_CONDITION_FIXES"
    REQUIRE_ABORT_CONDITION_FIXES = "REQUIRE_ABORT_CONDITION_FIXES"
    APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION_GATE = (
        "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION_GATE"
    )


class PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk(StrEnum):
    EXECUTION_REVIEW_NOT_APPROVED = "EXECUTION_REVIEW_NOT_APPROVED"
    EXECUTION_AUTHORIZATION_SCOPE_UNCLEAR = "EXECUTION_AUTHORIZATION_SCOPE_UNCLEAR"
    EXECUTION_AUTHORIZATION_BOUNDARY_GAP = "EXECUTION_AUTHORIZATION_BOUNDARY_GAP"
    EXECUTION_SCENARIO_AUTHORIZATION_GAP = "EXECUTION_SCENARIO_AUTHORIZATION_GAP"
    EXECUTION_SESSION_LIMIT_AUTHORIZATION_GAP = "EXECUTION_SESSION_LIMIT_AUTHORIZATION_GAP"
    EXECUTION_CONNECTION_AUTHORIZATION_GAP = "EXECUTION_CONNECTION_AUTHORIZATION_GAP"
    EXECUTION_ORDER_AUTHORIZATION_GAP = "EXECUTION_ORDER_AUTHORIZATION_GAP"
    EXECUTION_POSITION_AUTHORIZATION_GAP = "EXECUTION_POSITION_AUTHORIZATION_GAP"
    EXECUTION_ACCOUNT_AUTHORIZATION_GAP = "EXECUTION_ACCOUNT_AUTHORIZATION_GAP"
    EXECUTION_OBSERVABILITY_AUTHORIZATION_GAP = "EXECUTION_OBSERVABILITY_AUTHORIZATION_GAP"
    EXECUTION_ROLLBACK_AUTHORIZATION_GAP = "EXECUTION_ROLLBACK_AUTHORIZATION_GAP"
    EXECUTION_KILL_SWITCH_AUTHORIZATION_GAP = "EXECUTION_KILL_SWITCH_AUTHORIZATION_GAP"
    EXECUTION_HUMAN_SUPERVISION_AUTHORIZATION_GAP = "EXECUTION_HUMAN_SUPERVISION_AUTHORIZATION_GAP"
    EXECUTION_JOURNAL_AUTHORIZATION_GAP = "EXECUTION_JOURNAL_AUTHORIZATION_GAP"
    EXECUTION_STOP_CONDITION_AUTHORIZATION_GAP = "EXECUTION_STOP_CONDITION_AUTHORIZATION_GAP"
    EXECUTION_ABORT_CONDITION_AUTHORIZATION_GAP = "EXECUTION_ABORT_CONDITION_AUTHORIZATION_GAP"
    EXECUTION_SUCCESS_FAILURE_AUTHORIZATION_GAP = "EXECUTION_SUCCESS_FAILURE_AUTHORIZATION_GAP"
    PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION = (
        "PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION"
    )


class PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation(StrEnum):
    HOLD_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_PLAN = (
        "HOLD_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_PLAN"
    )
    APPROVE_EXECUTION_REVIEW_FIRST = "APPROVE_EXECUTION_REVIEW_FIRST"
    CLARIFY_EXECUTION_AUTHORIZATION_SCOPE = "CLARIFY_EXECUTION_AUTHORIZATION_SCOPE"
    COMPLETE_EXECUTION_AUTHORIZATION_BOUNDARIES = "COMPLETE_EXECUTION_AUTHORIZATION_BOUNDARIES"
    COMPLETE_EXECUTION_SCENARIO_AUTHORIZATION = "COMPLETE_EXECUTION_SCENARIO_AUTHORIZATION"
    COMPLETE_EXECUTION_SESSION_LIMIT_AUTHORIZATION = "COMPLETE_EXECUTION_SESSION_LIMIT_AUTHORIZATION"
    COMPLETE_EXECUTION_CONNECTION_AUTHORIZATION = "COMPLETE_EXECUTION_CONNECTION_AUTHORIZATION"
    COMPLETE_EXECUTION_ORDER_AUTHORIZATION = "COMPLETE_EXECUTION_ORDER_AUTHORIZATION"
    COMPLETE_EXECUTION_POSITION_AUTHORIZATION = "COMPLETE_EXECUTION_POSITION_AUTHORIZATION"
    COMPLETE_EXECUTION_ACCOUNT_AUTHORIZATION = "COMPLETE_EXECUTION_ACCOUNT_AUTHORIZATION"
    COMPLETE_EXECUTION_OBSERVABILITY_AUTHORIZATION = "COMPLETE_EXECUTION_OBSERVABILITY_AUTHORIZATION"
    COMPLETE_EXECUTION_ROLLBACK_AUTHORIZATION = "COMPLETE_EXECUTION_ROLLBACK_AUTHORIZATION"
    COMPLETE_EXECUTION_KILL_SWITCH_AUTHORIZATION = "COMPLETE_EXECUTION_KILL_SWITCH_AUTHORIZATION"
    COMPLETE_EXECUTION_HUMAN_SUPERVISION_AUTHORIZATION = "COMPLETE_EXECUTION_HUMAN_SUPERVISION_AUTHORIZATION"
    COMPLETE_EXECUTION_JOURNAL_AUTHORIZATION = "COMPLETE_EXECUTION_JOURNAL_AUTHORIZATION"
    COMPLETE_EXECUTION_STOP_CONDITION_AUTHORIZATION = "COMPLETE_EXECUTION_STOP_CONDITION_AUTHORIZATION"
    COMPLETE_EXECUTION_ABORT_CONDITION_AUTHORIZATION = "COMPLETE_EXECUTION_ABORT_CONDITION_AUTHORIZATION"
    COMPLETE_EXECUTION_SUCCESS_FAILURE_AUTHORIZATION = "COMPLETE_EXECUTION_SUCCESS_FAILURE_AUTHORIZATION"
    DELAY_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION = (
        "DELAY_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION"
    )
    RUN_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION_GATE_SUITE = (
        "RUN_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION_GATE_SUITE"
    )
    APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_PLAN = (
        "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_PLAN"
    )


@dataclass(frozen=True)
class PaperBrokerSandboxDryRunExecutionAuthorizationGateInput:
    paper_broker_sandbox_dry_run_execution_review: Any = None
    paper_broker_sandbox_dry_run_pre_execution_check: Any = None
    paper_broker_sandbox_dry_run_review: Any = None
    paper_broker_sandbox_dry_run_plan: Any = None
    paper_broker_sandbox_session_authorization_gate: Any = None
    paper_broker_sandbox_session_review: Any = None
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
    execution_review_approved: bool | None = None
    execution_review_reviewed: bool | None = None
    execution_authorization_scope_reviewed: bool | None = None
    execution_authorization_scope_clear: bool | None = None
    execution_authorization_boundaries_reviewed: bool | None = None
    execution_authorization_boundaries_complete: bool | None = None
    execution_scenario_authorization_reviewed: bool | None = None
    execution_scenario_authorization_complete: bool | None = None
    execution_session_limit_authorization_reviewed: bool | None = None
    execution_session_limit_authorization_complete: bool | None = None
    execution_connection_authorization_reviewed: bool | None = None
    execution_connection_authorization_complete: bool | None = None
    execution_order_authorization_reviewed: bool | None = None
    execution_order_authorization_complete: bool | None = None
    execution_position_authorization_reviewed: bool | None = None
    execution_position_authorization_complete: bool | None = None
    execution_account_authorization_reviewed: bool | None = None
    execution_account_authorization_complete: bool | None = None
    execution_observability_authorization_reviewed: bool | None = None
    execution_observability_authorization_complete: bool | None = None
    execution_rollback_authorization_reviewed: bool | None = None
    execution_rollback_authorization_complete: bool | None = None
    execution_kill_switch_authorization_reviewed: bool | None = None
    execution_kill_switch_authorization_complete: bool | None = None
    execution_human_supervision_authorization_reviewed: bool | None = None
    execution_human_supervision_authorization_complete: bool | None = None
    execution_journal_authorization_reviewed: bool | None = None
    execution_journal_authorization_complete: bool | None = None
    execution_stop_condition_authorization_reviewed: bool | None = None
    execution_stop_condition_authorization_complete: bool | None = None
    execution_abort_condition_authorization_reviewed: bool | None = None
    execution_abort_condition_authorization_complete: bool | None = None
    execution_success_failure_authorization_reviewed: bool | None = None
    execution_success_failure_authorization_complete: bool | None = None
    paper_broker_sandbox_dry_run_execution_authorization_gate_requested: bool | None = None
    paper_broker_sandbox_dry_run_execution_requested: bool | None = None
    paper_broker_sandbox_dry_run_controlled_simulation_requested: bool | None = None
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
    no_dry_run_execution: bool | None = None
    no_controlled_simulation_execution: bool | None = None
    no_real_order: bool | None = None
    no_real_account_access: bool | None = None
    execution_review_approval_score: int | None = None
    execution_authorization_scope_score: int | None = None
    execution_authorization_boundaries_score: int | None = None
    execution_scenario_authorization_score: int | None = None
    execution_session_limit_authorization_score: int | None = None
    execution_connection_authorization_score: int | None = None
    execution_order_authorization_score: int | None = None
    execution_position_authorization_score: int | None = None
    execution_account_authorization_score: int | None = None
    execution_observability_authorization_score: int | None = None
    execution_rollback_authorization_score: int | None = None
    execution_kill_switch_authorization_score: int | None = None
    execution_human_supervision_authorization_score: int | None = None
    execution_journal_authorization_score: int | None = None
    execution_stop_condition_authorization_score: int | None = None
    execution_abort_condition_authorization_score: int | None = None
    execution_success_failure_authorization_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerSandboxDryRunExecutionAuthorizationGateSection:
    name: str
    score: int
    passed: bool
    risks: tuple[PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk, ...] = ()
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerSandboxDryRunExecutionAuthorizationGateScore:
    overall_score: int
    execution_review_approval_score: int
    execution_authorization_scope_score: int
    execution_authorization_boundaries_score: int
    execution_scenario_authorization_score: int
    execution_session_limit_authorization_score: int
    execution_connection_authorization_score: int
    execution_order_authorization_score: int
    execution_position_authorization_score: int
    execution_account_authorization_score: int
    execution_observability_authorization_score: int
    execution_rollback_authorization_score: int
    execution_kill_switch_authorization_score: int
    execution_human_supervision_authorization_score: int
    execution_journal_authorization_score: int
    execution_stop_condition_authorization_score: int
    execution_abort_condition_authorization_score: int
    execution_success_failure_authorization_score: int


@dataclass(frozen=True)
class PaperBrokerSandboxDryRunExecutionAuthorizationGateResult:
    state: PaperBrokerSandboxDryRunExecutionAuthorizationGateState
    decision: PaperBrokerSandboxDryRunExecutionAuthorizationGateDecision
    authorization_score: int
    score_breakdown: PaperBrokerSandboxDryRunExecutionAuthorizationGateScore
    risks: tuple[PaperBrokerSandboxDryRunExecutionAuthorizationGateRisk, ...] = ()
    execution_review_approval: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection("execution_review_approval", 0, False)
    )
    execution_authorization_scope: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection("execution_authorization_scope", 0, False)
    )
    execution_authorization_boundaries: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection("execution_authorization_boundaries", 0, False)
    )
    execution_scenario_authorization: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection("execution_scenario_authorization", 0, False)
    )
    execution_session_limit_authorization: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection("execution_session_limit_authorization", 0, False)
    )
    execution_connection_authorization: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection("execution_connection_authorization", 0, False)
    )
    execution_order_authorization: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection("execution_order_authorization", 0, False)
    )
    execution_position_authorization: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection("execution_position_authorization", 0, False)
    )
    execution_account_authorization: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection("execution_account_authorization", 0, False)
    )
    execution_observability_authorization: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection("execution_observability_authorization", 0, False)
    )
    execution_rollback_authorization: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection("execution_rollback_authorization", 0, False)
    )
    execution_kill_switch_authorization: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection("execution_kill_switch_authorization", 0, False)
    )
    execution_human_supervision_authorization: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection("execution_human_supervision_authorization", 0, False)
    )
    execution_journal_authorization: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection("execution_journal_authorization", 0, False)
    )
    execution_stop_condition_authorization: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection("execution_stop_condition_authorization", 0, False)
    )
    execution_abort_condition_authorization: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection("execution_abort_condition_authorization", 0, False)
    )
    execution_success_failure_authorization: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionAuthorizationGateSection("execution_success_failure_authorization", 0, False)
    )
    recommendations: tuple[PaperBrokerSandboxDryRunExecutionAuthorizationGateRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
