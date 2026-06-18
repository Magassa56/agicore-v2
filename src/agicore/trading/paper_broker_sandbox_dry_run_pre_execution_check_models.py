"""Models for the offline AGIcore Paper Broker Sandbox Dry Run Pre-Execution Check."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerSandboxDryRunPreExecutionCheckState(StrEnum):
    NOT_READY = "NOT_READY"
    PRE_EXECUTION_CHECK_REQUIRED = "PRE_EXECUTION_CHECK_REQUIRED"
    PARTIALLY_READY = "PARTIALLY_READY"
    PRE_EXECUTION_CHECK_READY = "PRE_EXECUTION_CHECK_READY"
    READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_REVIEW = "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_REVIEW"


class PaperBrokerSandboxDryRunPreExecutionCheckDecision(StrEnum):
    BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN = "BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN"
    REQUIRE_DRY_RUN_REVIEW_FIXES = "REQUIRE_DRY_RUN_REVIEW_FIXES"
    REQUIRE_SCOPE_FIXES = "REQUIRE_SCOPE_FIXES"
    REQUIRE_BOUNDARY_FIXES = "REQUIRE_BOUNDARY_FIXES"
    REQUIRE_CONNECTION_SAFETY_FIXES = "REQUIRE_CONNECTION_SAFETY_FIXES"
    REQUIRE_ORDER_SAFETY_FIXES = "REQUIRE_ORDER_SAFETY_FIXES"
    REQUIRE_POSITION_SAFETY_FIXES = "REQUIRE_POSITION_SAFETY_FIXES"
    REQUIRE_ACCOUNT_SAFETY_FIXES = "REQUIRE_ACCOUNT_SAFETY_FIXES"
    REQUIRE_OBSERVABILITY_FIXES = "REQUIRE_OBSERVABILITY_FIXES"
    REQUIRE_ROLLBACK_FIXES = "REQUIRE_ROLLBACK_FIXES"
    REQUIRE_KILL_SWITCH_FIXES = "REQUIRE_KILL_SWITCH_FIXES"
    REQUIRE_SUPERVISION_FIXES = "REQUIRE_SUPERVISION_FIXES"
    REQUIRE_JOURNAL_FIXES = "REQUIRE_JOURNAL_FIXES"
    REQUIRE_STOP_CONDITION_FIXES = "REQUIRE_STOP_CONDITION_FIXES"
    APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION_CHECK = "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION_CHECK"


class PaperBrokerSandboxDryRunPreExecutionCheckRisk(StrEnum):
    DRY_RUN_REVIEW_NOT_APPROVED = "DRY_RUN_REVIEW_NOT_APPROVED"
    PRE_EXECUTION_SCOPE_UNCLEAR = "PRE_EXECUTION_SCOPE_UNCLEAR"
    PRE_EXECUTION_BOUNDARY_GAP = "PRE_EXECUTION_BOUNDARY_GAP"
    CONNECTION_PRE_EXECUTION_SAFETY_GAP = "CONNECTION_PRE_EXECUTION_SAFETY_GAP"
    ORDER_PRE_EXECUTION_SAFETY_GAP = "ORDER_PRE_EXECUTION_SAFETY_GAP"
    POSITION_PRE_EXECUTION_SAFETY_GAP = "POSITION_PRE_EXECUTION_SAFETY_GAP"
    ACCOUNT_PRE_EXECUTION_SAFETY_GAP = "ACCOUNT_PRE_EXECUTION_SAFETY_GAP"
    OBSERVABILITY_PRE_EXECUTION_GAP = "OBSERVABILITY_PRE_EXECUTION_GAP"
    ROLLBACK_PRE_EXECUTION_GAP = "ROLLBACK_PRE_EXECUTION_GAP"
    KILL_SWITCH_PRE_EXECUTION_GAP = "KILL_SWITCH_PRE_EXECUTION_GAP"
    HUMAN_SUPERVISION_PRE_EXECUTION_GAP = "HUMAN_SUPERVISION_PRE_EXECUTION_GAP"
    JOURNAL_PRE_EXECUTION_GAP = "JOURNAL_PRE_EXECUTION_GAP"
    STOP_CONDITIONS_PRE_EXECUTION_GAP = "STOP_CONDITIONS_PRE_EXECUTION_GAP"
    SUCCESS_FAILURE_CRITERIA_PRE_EXECUTION_GAP = "SUCCESS_FAILURE_CRITERIA_PRE_EXECUTION_GAP"
    PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION = "PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION"


class PaperBrokerSandboxDryRunPreExecutionCheckRecommendation(StrEnum):
    HOLD_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION = "HOLD_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION"
    APPROVE_DRY_RUN_REVIEW_FIRST = "APPROVE_DRY_RUN_REVIEW_FIRST"
    CLARIFY_PRE_EXECUTION_SCOPE = "CLARIFY_PRE_EXECUTION_SCOPE"
    COMPLETE_PRE_EXECUTION_BOUNDARIES = "COMPLETE_PRE_EXECUTION_BOUNDARIES"
    COMPLETE_CONNECTION_PRE_EXECUTION_SAFETY = "COMPLETE_CONNECTION_PRE_EXECUTION_SAFETY"
    COMPLETE_ORDER_PRE_EXECUTION_SAFETY = "COMPLETE_ORDER_PRE_EXECUTION_SAFETY"
    COMPLETE_POSITION_PRE_EXECUTION_SAFETY = "COMPLETE_POSITION_PRE_EXECUTION_SAFETY"
    COMPLETE_ACCOUNT_PRE_EXECUTION_SAFETY = "COMPLETE_ACCOUNT_PRE_EXECUTION_SAFETY"
    COMPLETE_OBSERVABILITY_PRE_EXECUTION_SAFETY = "COMPLETE_OBSERVABILITY_PRE_EXECUTION_SAFETY"
    COMPLETE_ROLLBACK_PRE_EXECUTION_SAFETY = "COMPLETE_ROLLBACK_PRE_EXECUTION_SAFETY"
    COMPLETE_KILL_SWITCH_PRE_EXECUTION_SAFETY = "COMPLETE_KILL_SWITCH_PRE_EXECUTION_SAFETY"
    COMPLETE_HUMAN_SUPERVISION_PRE_EXECUTION_SAFETY = "COMPLETE_HUMAN_SUPERVISION_PRE_EXECUTION_SAFETY"
    COMPLETE_JOURNAL_PRE_EXECUTION_SAFETY = "COMPLETE_JOURNAL_PRE_EXECUTION_SAFETY"
    COMPLETE_STOP_CONDITIONS_PRE_EXECUTION_SAFETY = "COMPLETE_STOP_CONDITIONS_PRE_EXECUTION_SAFETY"
    COMPLETE_SUCCESS_FAILURE_CRITERIA_PRE_EXECUTION_SAFETY = "COMPLETE_SUCCESS_FAILURE_CRITERIA_PRE_EXECUTION_SAFETY"
    DELAY_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION = "DELAY_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION"
    RUN_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION_CHECK_SUITE = "RUN_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION_CHECK_SUITE"
    APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_REVIEW = "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_REVIEW"


@dataclass(frozen=True)
class PaperBrokerSandboxDryRunPreExecutionCheckInput:
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
    dry_run_review_approved: bool | None = None
    dry_run_review_reviewed: bool | None = None
    pre_execution_scope_reviewed: bool | None = None
    pre_execution_scope_clear: bool | None = None
    pre_execution_boundaries_reviewed: bool | None = None
    pre_execution_boundaries_complete: bool | None = None
    connection_pre_execution_safety_reviewed: bool | None = None
    connection_pre_execution_safe: bool | None = None
    order_pre_execution_safety_reviewed: bool | None = None
    order_pre_execution_safe: bool | None = None
    position_pre_execution_safety_reviewed: bool | None = None
    position_pre_execution_safe: bool | None = None
    account_pre_execution_safety_reviewed: bool | None = None
    account_pre_execution_safe: bool | None = None
    observability_pre_execution_safety_reviewed: bool | None = None
    observability_pre_execution_safe: bool | None = None
    rollback_pre_execution_safety_reviewed: bool | None = None
    rollback_pre_execution_safe: bool | None = None
    kill_switch_pre_execution_safety_reviewed: bool | None = None
    kill_switch_pre_execution_safe: bool | None = None
    human_supervision_pre_execution_safety_reviewed: bool | None = None
    human_supervision_pre_execution_safe: bool | None = None
    journal_pre_execution_safety_reviewed: bool | None = None
    journal_pre_execution_safe: bool | None = None
    stop_conditions_pre_execution_safety_reviewed: bool | None = None
    stop_conditions_pre_execution_safe: bool | None = None
    success_failure_criteria_pre_execution_safety_reviewed: bool | None = None
    success_failure_criteria_pre_execution_safe: bool | None = None
    paper_broker_sandbox_dry_run_pre_execution_check_requested: bool | None = None
    paper_broker_sandbox_dry_run_execution_requested: bool | None = None
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
    no_real_account_access: bool | None = None
    no_dry_run_execution: bool | None = None
    no_pre_execution: bool | None = None
    dry_run_review_approval_score: int | None = None
    pre_execution_scope_score: int | None = None
    pre_execution_boundaries_score: int | None = None
    connection_pre_execution_safety_score: int | None = None
    order_pre_execution_safety_score: int | None = None
    position_pre_execution_safety_score: int | None = None
    account_pre_execution_safety_score: int | None = None
    observability_pre_execution_safety_score: int | None = None
    rollback_pre_execution_safety_score: int | None = None
    kill_switch_pre_execution_safety_score: int | None = None
    human_supervision_pre_execution_safety_score: int | None = None
    journal_pre_execution_safety_score: int | None = None
    stop_conditions_pre_execution_safety_score: int | None = None
    success_failure_criteria_pre_execution_safety_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerSandboxDryRunPreExecutionCheckSection:
    name: str
    score: int
    passed: bool
    risks: tuple[PaperBrokerSandboxDryRunPreExecutionCheckRisk, ...] = ()
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerSandboxDryRunPreExecutionCheckScore:
    overall_score: int
    dry_run_review_approval_score: int
    pre_execution_scope_score: int
    pre_execution_boundaries_score: int
    connection_pre_execution_safety_score: int
    order_pre_execution_safety_score: int
    position_pre_execution_safety_score: int
    account_pre_execution_safety_score: int
    observability_pre_execution_safety_score: int
    rollback_pre_execution_safety_score: int
    kill_switch_pre_execution_safety_score: int
    human_supervision_pre_execution_safety_score: int
    journal_pre_execution_safety_score: int
    stop_conditions_pre_execution_safety_score: int
    success_failure_criteria_pre_execution_safety_score: int


@dataclass(frozen=True)
class PaperBrokerSandboxDryRunPreExecutionCheckResult:
    state: PaperBrokerSandboxDryRunPreExecutionCheckState
    decision: PaperBrokerSandboxDryRunPreExecutionCheckDecision
    check_score: int
    score_breakdown: PaperBrokerSandboxDryRunPreExecutionCheckScore
    risks: tuple[PaperBrokerSandboxDryRunPreExecutionCheckRisk, ...] = ()
    dry_run_review_approval: PaperBrokerSandboxDryRunPreExecutionCheckSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunPreExecutionCheckSection("dry_run_review_approval", 0, False)
    )
    pre_execution_scope: PaperBrokerSandboxDryRunPreExecutionCheckSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunPreExecutionCheckSection("pre_execution_scope", 0, False)
    )
    pre_execution_boundaries: PaperBrokerSandboxDryRunPreExecutionCheckSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunPreExecutionCheckSection("pre_execution_boundaries", 0, False)
    )
    connection_pre_execution_safety: PaperBrokerSandboxDryRunPreExecutionCheckSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunPreExecutionCheckSection("connection_pre_execution_safety", 0, False)
    )
    order_pre_execution_safety: PaperBrokerSandboxDryRunPreExecutionCheckSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunPreExecutionCheckSection("order_pre_execution_safety", 0, False)
    )
    position_pre_execution_safety: PaperBrokerSandboxDryRunPreExecutionCheckSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunPreExecutionCheckSection("position_pre_execution_safety", 0, False)
    )
    account_pre_execution_safety: PaperBrokerSandboxDryRunPreExecutionCheckSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunPreExecutionCheckSection("account_pre_execution_safety", 0, False)
    )
    observability_pre_execution_safety: PaperBrokerSandboxDryRunPreExecutionCheckSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunPreExecutionCheckSection("observability_pre_execution_safety", 0, False)
    )
    rollback_pre_execution_safety: PaperBrokerSandboxDryRunPreExecutionCheckSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunPreExecutionCheckSection("rollback_pre_execution_safety", 0, False)
    )
    kill_switch_pre_execution_safety: PaperBrokerSandboxDryRunPreExecutionCheckSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunPreExecutionCheckSection("kill_switch_pre_execution_safety", 0, False)
    )
    human_supervision_pre_execution_safety: PaperBrokerSandboxDryRunPreExecutionCheckSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunPreExecutionCheckSection("human_supervision_pre_execution_safety", 0, False)
    )
    journal_pre_execution_safety: PaperBrokerSandboxDryRunPreExecutionCheckSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunPreExecutionCheckSection("journal_pre_execution_safety", 0, False)
    )
    stop_conditions_pre_execution_safety: PaperBrokerSandboxDryRunPreExecutionCheckSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunPreExecutionCheckSection("stop_conditions_pre_execution_safety", 0, False)
    )
    success_failure_criteria_pre_execution_safety: PaperBrokerSandboxDryRunPreExecutionCheckSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunPreExecutionCheckSection("success_failure_criteria_pre_execution_safety", 0, False)
    )
    recommendations: tuple[PaperBrokerSandboxDryRunPreExecutionCheckRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
