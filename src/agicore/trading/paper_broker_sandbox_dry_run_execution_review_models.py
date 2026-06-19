"""Models for the offline AGIcore Paper Broker Sandbox Dry Run Execution Review."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerSandboxDryRunExecutionReviewState(StrEnum):
    NOT_READY = "NOT_READY"
    EXECUTION_REVIEW_REQUIRED = "EXECUTION_REVIEW_REQUIRED"
    PARTIALLY_READY = "PARTIALLY_READY"
    DRY_RUN_EXECUTION_REVIEW_READY = "DRY_RUN_EXECUTION_REVIEW_READY"
    READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION_GATE = (
        "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION_GATE"
    )


class PaperBrokerSandboxDryRunExecutionReviewDecision(StrEnum):
    BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION = "BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION"
    REQUIRE_PRE_EXECUTION_CHECK_FIXES = "REQUIRE_PRE_EXECUTION_CHECK_FIXES"
    REQUIRE_SCOPE_FIXES = "REQUIRE_SCOPE_FIXES"
    REQUIRE_BOUNDARY_FIXES = "REQUIRE_BOUNDARY_FIXES"
    REQUIRE_SCENARIO_FIXES = "REQUIRE_SCENARIO_FIXES"
    REQUIRE_SESSION_LIMIT_FIXES = "REQUIRE_SESSION_LIMIT_FIXES"
    REQUIRE_CONNECTION_CONTROL_FIXES = "REQUIRE_CONNECTION_CONTROL_FIXES"
    REQUIRE_ORDER_CONTROL_FIXES = "REQUIRE_ORDER_CONTROL_FIXES"
    REQUIRE_POSITION_CONTROL_FIXES = "REQUIRE_POSITION_CONTROL_FIXES"
    REQUIRE_ACCOUNT_CONTROL_FIXES = "REQUIRE_ACCOUNT_CONTROL_FIXES"
    REQUIRE_OBSERVABILITY_FIXES = "REQUIRE_OBSERVABILITY_FIXES"
    REQUIRE_ROLLBACK_FIXES = "REQUIRE_ROLLBACK_FIXES"
    REQUIRE_KILL_SWITCH_FIXES = "REQUIRE_KILL_SWITCH_FIXES"
    REQUIRE_SUPERVISION_FIXES = "REQUIRE_SUPERVISION_FIXES"
    REQUIRE_JOURNAL_FIXES = "REQUIRE_JOURNAL_FIXES"
    REQUIRE_STOP_CONDITION_FIXES = "REQUIRE_STOP_CONDITION_FIXES"
    REQUIRE_ABORT_CONDITION_FIXES = "REQUIRE_ABORT_CONDITION_FIXES"
    APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_REVIEW = "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_REVIEW"


class PaperBrokerSandboxDryRunExecutionReviewRisk(StrEnum):
    PRE_EXECUTION_CHECK_NOT_APPROVED = "PRE_EXECUTION_CHECK_NOT_APPROVED"
    EXECUTION_SCOPE_UNCLEAR = "EXECUTION_SCOPE_UNCLEAR"
    EXECUTION_BOUNDARY_GAP = "EXECUTION_BOUNDARY_GAP"
    EXECUTION_SCENARIO_GAP = "EXECUTION_SCENARIO_GAP"
    EXECUTION_SESSION_LIMIT_GAP = "EXECUTION_SESSION_LIMIT_GAP"
    EXECUTION_CONNECTION_CONTROL_GAP = "EXECUTION_CONNECTION_CONTROL_GAP"
    EXECUTION_ORDER_CONTROL_GAP = "EXECUTION_ORDER_CONTROL_GAP"
    EXECUTION_POSITION_CONTROL_GAP = "EXECUTION_POSITION_CONTROL_GAP"
    EXECUTION_ACCOUNT_CONTROL_GAP = "EXECUTION_ACCOUNT_CONTROL_GAP"
    EXECUTION_OBSERVABILITY_GAP = "EXECUTION_OBSERVABILITY_GAP"
    EXECUTION_ROLLBACK_GAP = "EXECUTION_ROLLBACK_GAP"
    EXECUTION_KILL_SWITCH_GAP = "EXECUTION_KILL_SWITCH_GAP"
    EXECUTION_HUMAN_SUPERVISION_GAP = "EXECUTION_HUMAN_SUPERVISION_GAP"
    EXECUTION_JOURNAL_GAP = "EXECUTION_JOURNAL_GAP"
    EXECUTION_STOP_CONDITION_GAP = "EXECUTION_STOP_CONDITION_GAP"
    EXECUTION_SUCCESS_FAILURE_CRITERIA_GAP = "EXECUTION_SUCCESS_FAILURE_CRITERIA_GAP"
    EXECUTION_ABORT_CONDITION_GAP = "EXECUTION_ABORT_CONDITION_GAP"
    PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_REAL_EXECUTION = "PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_REAL_EXECUTION"


class PaperBrokerSandboxDryRunExecutionReviewRecommendation(StrEnum):
    HOLD_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION = "HOLD_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION"
    APPROVE_PRE_EXECUTION_CHECK_FIRST = "APPROVE_PRE_EXECUTION_CHECK_FIRST"
    CLARIFY_EXECUTION_SCOPE = "CLARIFY_EXECUTION_SCOPE"
    COMPLETE_EXECUTION_BOUNDARIES = "COMPLETE_EXECUTION_BOUNDARIES"
    COMPLETE_EXECUTION_SCENARIO = "COMPLETE_EXECUTION_SCENARIO"
    COMPLETE_EXECUTION_SESSION_LIMITS = "COMPLETE_EXECUTION_SESSION_LIMITS"
    COMPLETE_EXECUTION_CONNECTION_CONTROL = "COMPLETE_EXECUTION_CONNECTION_CONTROL"
    COMPLETE_EXECUTION_ORDER_CONTROL = "COMPLETE_EXECUTION_ORDER_CONTROL"
    COMPLETE_EXECUTION_POSITION_CONTROL = "COMPLETE_EXECUTION_POSITION_CONTROL"
    COMPLETE_EXECUTION_ACCOUNT_CONTROL = "COMPLETE_EXECUTION_ACCOUNT_CONTROL"
    COMPLETE_EXECUTION_OBSERVABILITY_CONTROL = "COMPLETE_EXECUTION_OBSERVABILITY_CONTROL"
    COMPLETE_EXECUTION_ROLLBACK_CONTROL = "COMPLETE_EXECUTION_ROLLBACK_CONTROL"
    COMPLETE_EXECUTION_KILL_SWITCH_CONTROL = "COMPLETE_EXECUTION_KILL_SWITCH_CONTROL"
    COMPLETE_EXECUTION_HUMAN_SUPERVISION_CONTROL = "COMPLETE_EXECUTION_HUMAN_SUPERVISION_CONTROL"
    COMPLETE_EXECUTION_JOURNAL_CONTROL = "COMPLETE_EXECUTION_JOURNAL_CONTROL"
    COMPLETE_EXECUTION_STOP_CONDITIONS = "COMPLETE_EXECUTION_STOP_CONDITIONS"
    COMPLETE_EXECUTION_SUCCESS_FAILURE_CRITERIA = "COMPLETE_EXECUTION_SUCCESS_FAILURE_CRITERIA"
    COMPLETE_EXECUTION_ABORT_CONDITIONS = "COMPLETE_EXECUTION_ABORT_CONDITIONS"
    DELAY_PAPER_BROKER_SANDBOX_DRY_RUN_REAL_EXECUTION = "DELAY_PAPER_BROKER_SANDBOX_DRY_RUN_REAL_EXECUTION"
    RUN_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_REVIEW_SUITE = "RUN_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_REVIEW_SUITE"
    APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION_GATE = (
        "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION_GATE"
    )


@dataclass(frozen=True)
class PaperBrokerSandboxDryRunExecutionReviewInput:
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
    pre_execution_check_approved: bool | None = None
    pre_execution_check_reviewed: bool | None = None
    execution_scope_reviewed: bool | None = None
    execution_scope_clear: bool | None = None
    execution_boundaries_reviewed: bool | None = None
    execution_boundaries_complete: bool | None = None
    execution_scenario_reviewed: bool | None = None
    execution_scenario_complete: bool | None = None
    execution_session_limits_reviewed: bool | None = None
    execution_session_limits_complete: bool | None = None
    execution_connection_control_reviewed: bool | None = None
    execution_connection_control_complete: bool | None = None
    execution_order_control_reviewed: bool | None = None
    execution_order_control_complete: bool | None = None
    execution_position_control_reviewed: bool | None = None
    execution_position_control_complete: bool | None = None
    execution_account_control_reviewed: bool | None = None
    execution_account_control_complete: bool | None = None
    execution_observability_control_reviewed: bool | None = None
    execution_observability_control_complete: bool | None = None
    execution_rollback_control_reviewed: bool | None = None
    execution_rollback_control_complete: bool | None = None
    execution_kill_switch_control_reviewed: bool | None = None
    execution_kill_switch_control_complete: bool | None = None
    execution_human_supervision_control_reviewed: bool | None = None
    execution_human_supervision_control_complete: bool | None = None
    execution_journal_control_reviewed: bool | None = None
    execution_journal_control_complete: bool | None = None
    execution_stop_conditions_reviewed: bool | None = None
    execution_stop_conditions_complete: bool | None = None
    execution_success_failure_criteria_reviewed: bool | None = None
    execution_success_failure_criteria_complete: bool | None = None
    execution_abort_conditions_reviewed: bool | None = None
    execution_abort_conditions_complete: bool | None = None
    paper_broker_sandbox_dry_run_execution_review_requested: bool | None = None
    paper_broker_sandbox_dry_run_execution_requested: bool | None = None
    paper_broker_sandbox_dry_run_real_execution_requested: bool | None = None
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
    no_real_execution: bool | None = None
    no_real_order: bool | None = None
    no_real_account_access: bool | None = None
    pre_execution_check_approval_score: int | None = None
    execution_scope_score: int | None = None
    execution_boundaries_score: int | None = None
    execution_scenario_score: int | None = None
    execution_session_limits_score: int | None = None
    execution_connection_control_score: int | None = None
    execution_order_control_score: int | None = None
    execution_position_control_score: int | None = None
    execution_account_control_score: int | None = None
    execution_observability_control_score: int | None = None
    execution_rollback_control_score: int | None = None
    execution_kill_switch_control_score: int | None = None
    execution_human_supervision_control_score: int | None = None
    execution_journal_control_score: int | None = None
    execution_stop_conditions_score: int | None = None
    execution_success_failure_criteria_score: int | None = None
    execution_abort_conditions_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerSandboxDryRunExecutionReviewSection:
    name: str
    score: int
    passed: bool
    risks: tuple[PaperBrokerSandboxDryRunExecutionReviewRisk, ...] = ()
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerSandboxDryRunExecutionReviewScore:
    overall_score: int
    pre_execution_check_approval_score: int
    execution_scope_score: int
    execution_boundaries_score: int
    execution_scenario_score: int
    execution_session_limits_score: int
    execution_connection_control_score: int
    execution_order_control_score: int
    execution_position_control_score: int
    execution_account_control_score: int
    execution_observability_control_score: int
    execution_rollback_control_score: int
    execution_kill_switch_control_score: int
    execution_human_supervision_control_score: int
    execution_journal_control_score: int
    execution_stop_conditions_score: int
    execution_success_failure_criteria_score: int
    execution_abort_conditions_score: int


@dataclass(frozen=True)
class PaperBrokerSandboxDryRunExecutionReviewResult:
    state: PaperBrokerSandboxDryRunExecutionReviewState
    decision: PaperBrokerSandboxDryRunExecutionReviewDecision
    review_score: int
    score_breakdown: PaperBrokerSandboxDryRunExecutionReviewScore
    risks: tuple[PaperBrokerSandboxDryRunExecutionReviewRisk, ...] = ()
    pre_execution_check_approval: PaperBrokerSandboxDryRunExecutionReviewSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionReviewSection("pre_execution_check_approval", 0, False)
    )
    execution_scope: PaperBrokerSandboxDryRunExecutionReviewSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionReviewSection("execution_scope", 0, False)
    )
    execution_boundaries: PaperBrokerSandboxDryRunExecutionReviewSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionReviewSection("execution_boundaries", 0, False)
    )
    execution_scenario: PaperBrokerSandboxDryRunExecutionReviewSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionReviewSection("execution_scenario", 0, False)
    )
    execution_session_limits: PaperBrokerSandboxDryRunExecutionReviewSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionReviewSection("execution_session_limits", 0, False)
    )
    execution_connection_control: PaperBrokerSandboxDryRunExecutionReviewSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionReviewSection("execution_connection_control", 0, False)
    )
    execution_order_control: PaperBrokerSandboxDryRunExecutionReviewSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionReviewSection("execution_order_control", 0, False)
    )
    execution_position_control: PaperBrokerSandboxDryRunExecutionReviewSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionReviewSection("execution_position_control", 0, False)
    )
    execution_account_control: PaperBrokerSandboxDryRunExecutionReviewSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionReviewSection("execution_account_control", 0, False)
    )
    execution_observability_control: PaperBrokerSandboxDryRunExecutionReviewSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionReviewSection("execution_observability_control", 0, False)
    )
    execution_rollback_control: PaperBrokerSandboxDryRunExecutionReviewSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionReviewSection("execution_rollback_control", 0, False)
    )
    execution_kill_switch_control: PaperBrokerSandboxDryRunExecutionReviewSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionReviewSection("execution_kill_switch_control", 0, False)
    )
    execution_human_supervision_control: PaperBrokerSandboxDryRunExecutionReviewSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionReviewSection("execution_human_supervision_control", 0, False)
    )
    execution_journal_control: PaperBrokerSandboxDryRunExecutionReviewSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionReviewSection("execution_journal_control", 0, False)
    )
    execution_stop_conditions: PaperBrokerSandboxDryRunExecutionReviewSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionReviewSection("execution_stop_conditions", 0, False)
    )
    execution_success_failure_criteria: PaperBrokerSandboxDryRunExecutionReviewSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionReviewSection("execution_success_failure_criteria", 0, False)
    )
    execution_abort_conditions: PaperBrokerSandboxDryRunExecutionReviewSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunExecutionReviewSection("execution_abort_conditions", 0, False)
    )
    recommendations: tuple[PaperBrokerSandboxDryRunExecutionReviewRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
