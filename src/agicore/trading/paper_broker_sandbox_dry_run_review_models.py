"""Models for the offline AGIcore Paper Broker Sandbox Dry Run Review."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerSandboxDryRunReviewState(StrEnum):
    NOT_READY = "NOT_READY"
    DRY_RUN_REVIEW_REQUIRED = "DRY_RUN_REVIEW_REQUIRED"
    PARTIALLY_READY = "PARTIALLY_READY"
    DRY_RUN_REVIEW_READY = "DRY_RUN_REVIEW_READY"
    READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION_CHECK = "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION_CHECK"


class PaperBrokerSandboxDryRunReviewDecision(StrEnum):
    BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN = "BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN"
    REQUIRE_DRY_RUN_PLAN_FIXES = "REQUIRE_DRY_RUN_PLAN_FIXES"
    REQUIRE_SCOPE_FIXES = "REQUIRE_SCOPE_FIXES"
    REQUIRE_BOUNDARY_FIXES = "REQUIRE_BOUNDARY_FIXES"
    REQUIRE_SCENARIO_FIXES = "REQUIRE_SCENARIO_FIXES"
    REQUIRE_SESSION_LIMIT_FIXES = "REQUIRE_SESSION_LIMIT_FIXES"
    REQUIRE_CONNECTION_POLICY_FIXES = "REQUIRE_CONNECTION_POLICY_FIXES"
    REQUIRE_ORDER_POLICY_FIXES = "REQUIRE_ORDER_POLICY_FIXES"
    REQUIRE_POSITION_POLICY_FIXES = "REQUIRE_POSITION_POLICY_FIXES"
    REQUIRE_ACCOUNT_POLICY_FIXES = "REQUIRE_ACCOUNT_POLICY_FIXES"
    REQUIRE_OBSERVABILITY_FIXES = "REQUIRE_OBSERVABILITY_FIXES"
    REQUIRE_ROLLBACK_FIXES = "REQUIRE_ROLLBACK_FIXES"
    REQUIRE_KILL_SWITCH_FIXES = "REQUIRE_KILL_SWITCH_FIXES"
    REQUIRE_SUPERVISION_FIXES = "REQUIRE_SUPERVISION_FIXES"
    REQUIRE_JOURNAL_FIXES = "REQUIRE_JOURNAL_FIXES"
    REQUIRE_STOP_CONDITION_FIXES = "REQUIRE_STOP_CONDITION_FIXES"
    APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_REVIEW = "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_REVIEW"


class PaperBrokerSandboxDryRunReviewRisk(StrEnum):
    DRY_RUN_PLAN_NOT_APPROVED = "DRY_RUN_PLAN_NOT_APPROVED"
    DRY_RUN_SCOPE_UNCLEAR = "DRY_RUN_SCOPE_UNCLEAR"
    DRY_RUN_BOUNDARY_INCOMPLETE = "DRY_RUN_BOUNDARY_INCOMPLETE"
    DRY_RUN_SCENARIO_INCOMPLETE = "DRY_RUN_SCENARIO_INCOMPLETE"
    DRY_RUN_SESSION_LIMIT_INCOMPLETE = "DRY_RUN_SESSION_LIMIT_INCOMPLETE"
    DRY_RUN_CONNECTION_POLICY_INCOMPLETE = "DRY_RUN_CONNECTION_POLICY_INCOMPLETE"
    DRY_RUN_ORDER_POLICY_INCOMPLETE = "DRY_RUN_ORDER_POLICY_INCOMPLETE"
    DRY_RUN_POSITION_POLICY_INCOMPLETE = "DRY_RUN_POSITION_POLICY_INCOMPLETE"
    DRY_RUN_ACCOUNT_POLICY_INCOMPLETE = "DRY_RUN_ACCOUNT_POLICY_INCOMPLETE"
    DRY_RUN_OBSERVABILITY_INCOMPLETE = "DRY_RUN_OBSERVABILITY_INCOMPLETE"
    DRY_RUN_ROLLBACK_INCOMPLETE = "DRY_RUN_ROLLBACK_INCOMPLETE"
    DRY_RUN_KILL_SWITCH_INCOMPLETE = "DRY_RUN_KILL_SWITCH_INCOMPLETE"
    DRY_RUN_HUMAN_SUPERVISION_INCOMPLETE = "DRY_RUN_HUMAN_SUPERVISION_INCOMPLETE"
    DRY_RUN_JOURNAL_INCOMPLETE = "DRY_RUN_JOURNAL_INCOMPLETE"
    DRY_RUN_STOP_CONDITION_INCOMPLETE = "DRY_RUN_STOP_CONDITION_INCOMPLETE"
    DRY_RUN_SUCCESS_CRITERIA_INCOMPLETE = "DRY_RUN_SUCCESS_CRITERIA_INCOMPLETE"
    DRY_RUN_FAILURE_CRITERIA_INCOMPLETE = "DRY_RUN_FAILURE_CRITERIA_INCOMPLETE"
    PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION = "PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION"


class PaperBrokerSandboxDryRunReviewRecommendation(StrEnum):
    HOLD_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION = "HOLD_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION"
    APPROVE_DRY_RUN_PLAN_FIRST = "APPROVE_DRY_RUN_PLAN_FIRST"
    CLARIFY_DRY_RUN_SCOPE = "CLARIFY_DRY_RUN_SCOPE"
    COMPLETE_DRY_RUN_BOUNDARIES = "COMPLETE_DRY_RUN_BOUNDARIES"
    COMPLETE_DRY_RUN_SCENARIO = "COMPLETE_DRY_RUN_SCENARIO"
    COMPLETE_DRY_RUN_SESSION_LIMITS = "COMPLETE_DRY_RUN_SESSION_LIMITS"
    COMPLETE_DRY_RUN_CONNECTION_POLICY = "COMPLETE_DRY_RUN_CONNECTION_POLICY"
    COMPLETE_DRY_RUN_ORDER_POLICY = "COMPLETE_DRY_RUN_ORDER_POLICY"
    COMPLETE_DRY_RUN_POSITION_POLICY = "COMPLETE_DRY_RUN_POSITION_POLICY"
    COMPLETE_DRY_RUN_ACCOUNT_POLICY = "COMPLETE_DRY_RUN_ACCOUNT_POLICY"
    COMPLETE_DRY_RUN_OBSERVABILITY_POLICY = "COMPLETE_DRY_RUN_OBSERVABILITY_POLICY"
    COMPLETE_DRY_RUN_ROLLBACK_POLICY = "COMPLETE_DRY_RUN_ROLLBACK_POLICY"
    COMPLETE_DRY_RUN_KILL_SWITCH_POLICY = "COMPLETE_DRY_RUN_KILL_SWITCH_POLICY"
    COMPLETE_DRY_RUN_HUMAN_SUPERVISION_POLICY = "COMPLETE_DRY_RUN_HUMAN_SUPERVISION_POLICY"
    COMPLETE_DRY_RUN_JOURNAL_POLICY = "COMPLETE_DRY_RUN_JOURNAL_POLICY"
    COMPLETE_DRY_RUN_STOP_CONDITIONS = "COMPLETE_DRY_RUN_STOP_CONDITIONS"
    COMPLETE_DRY_RUN_SUCCESS_CRITERIA = "COMPLETE_DRY_RUN_SUCCESS_CRITERIA"
    COMPLETE_DRY_RUN_FAILURE_CRITERIA = "COMPLETE_DRY_RUN_FAILURE_CRITERIA"
    DELAY_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION = "DELAY_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION"
    RUN_PAPER_BROKER_SANDBOX_DRY_RUN_REVIEW_SUITE = "RUN_PAPER_BROKER_SANDBOX_DRY_RUN_REVIEW_SUITE"
    APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION_CHECK = "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION_CHECK"


@dataclass(frozen=True)
class PaperBrokerSandboxDryRunReviewInput:
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
    dry_run_plan_approved: bool | None = None
    dry_run_plan_reviewed: bool | None = None
    dry_run_scope_reviewed: bool | None = None
    dry_run_scope_clear: bool | None = None
    dry_run_boundaries_reviewed: bool | None = None
    dry_run_boundaries_complete: bool | None = None
    dry_run_scenario_reviewed: bool | None = None
    dry_run_scenario_complete: bool | None = None
    dry_run_session_limits_reviewed: bool | None = None
    dry_run_session_limits_complete: bool | None = None
    dry_run_connection_policy_reviewed: bool | None = None
    dry_run_connection_policy_complete: bool | None = None
    dry_run_order_policy_reviewed: bool | None = None
    dry_run_order_policy_complete: bool | None = None
    dry_run_position_policy_reviewed: bool | None = None
    dry_run_position_policy_complete: bool | None = None
    dry_run_account_policy_reviewed: bool | None = None
    dry_run_account_policy_complete: bool | None = None
    dry_run_observability_policy_reviewed: bool | None = None
    dry_run_observability_policy_complete: bool | None = None
    dry_run_rollback_policy_reviewed: bool | None = None
    dry_run_rollback_policy_complete: bool | None = None
    dry_run_kill_switch_policy_reviewed: bool | None = None
    dry_run_kill_switch_policy_complete: bool | None = None
    dry_run_human_supervision_policy_reviewed: bool | None = None
    dry_run_human_supervision_policy_complete: bool | None = None
    dry_run_journal_policy_reviewed: bool | None = None
    dry_run_journal_policy_complete: bool | None = None
    dry_run_stop_conditions_reviewed: bool | None = None
    dry_run_stop_conditions_complete: bool | None = None
    dry_run_success_criteria_reviewed: bool | None = None
    dry_run_success_criteria_complete: bool | None = None
    dry_run_failure_criteria_reviewed: bool | None = None
    dry_run_failure_criteria_complete: bool | None = None
    paper_broker_sandbox_dry_run_review_requested: bool | None = None
    paper_broker_sandbox_dry_run_pre_execution_requested: bool | None = None
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
    dry_run_plan_readiness_score: int | None = None
    dry_run_scope_score: int | None = None
    dry_run_boundaries_score: int | None = None
    dry_run_scenario_score: int | None = None
    dry_run_session_limits_score: int | None = None
    dry_run_connection_policy_score: int | None = None
    dry_run_order_policy_score: int | None = None
    dry_run_position_policy_score: int | None = None
    dry_run_account_policy_score: int | None = None
    dry_run_observability_policy_score: int | None = None
    dry_run_rollback_policy_score: int | None = None
    dry_run_kill_switch_policy_score: int | None = None
    dry_run_human_supervision_policy_score: int | None = None
    dry_run_journal_policy_score: int | None = None
    dry_run_stop_conditions_score: int | None = None
    dry_run_success_criteria_score: int | None = None
    dry_run_failure_criteria_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerSandboxDryRunReviewSection:
    name: str
    score: int
    passed: bool
    risks: tuple[PaperBrokerSandboxDryRunReviewRisk, ...] = ()
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerSandboxDryRunReviewScore:
    overall_score: int
    dry_run_plan_readiness_score: int
    dry_run_scope_score: int
    dry_run_boundaries_score: int
    dry_run_scenario_score: int
    dry_run_session_limits_score: int
    dry_run_connection_policy_score: int
    dry_run_order_policy_score: int
    dry_run_position_policy_score: int
    dry_run_account_policy_score: int
    dry_run_observability_policy_score: int
    dry_run_rollback_policy_score: int
    dry_run_kill_switch_policy_score: int
    dry_run_human_supervision_policy_score: int
    dry_run_journal_policy_score: int
    dry_run_stop_conditions_score: int
    dry_run_success_criteria_score: int
    dry_run_failure_criteria_score: int


@dataclass(frozen=True)
class PaperBrokerSandboxDryRunReviewResult:
    state: PaperBrokerSandboxDryRunReviewState
    decision: PaperBrokerSandboxDryRunReviewDecision
    review_score: int
    score_breakdown: PaperBrokerSandboxDryRunReviewScore
    risks: tuple[PaperBrokerSandboxDryRunReviewRisk, ...] = ()
    dry_run_plan_readiness: PaperBrokerSandboxDryRunReviewSection = field(default_factory=lambda: PaperBrokerSandboxDryRunReviewSection("dry_run_plan_readiness", 0, False))
    dry_run_scope: PaperBrokerSandboxDryRunReviewSection = field(default_factory=lambda: PaperBrokerSandboxDryRunReviewSection("dry_run_scope", 0, False))
    dry_run_boundaries: PaperBrokerSandboxDryRunReviewSection = field(default_factory=lambda: PaperBrokerSandboxDryRunReviewSection("dry_run_boundaries", 0, False))
    dry_run_scenario: PaperBrokerSandboxDryRunReviewSection = field(default_factory=lambda: PaperBrokerSandboxDryRunReviewSection("dry_run_scenario", 0, False))
    dry_run_session_limits: PaperBrokerSandboxDryRunReviewSection = field(default_factory=lambda: PaperBrokerSandboxDryRunReviewSection("dry_run_session_limits", 0, False))
    dry_run_connection_policy: PaperBrokerSandboxDryRunReviewSection = field(default_factory=lambda: PaperBrokerSandboxDryRunReviewSection("dry_run_connection_policy", 0, False))
    dry_run_order_policy: PaperBrokerSandboxDryRunReviewSection = field(default_factory=lambda: PaperBrokerSandboxDryRunReviewSection("dry_run_order_policy", 0, False))
    dry_run_position_policy: PaperBrokerSandboxDryRunReviewSection = field(default_factory=lambda: PaperBrokerSandboxDryRunReviewSection("dry_run_position_policy", 0, False))
    dry_run_account_policy: PaperBrokerSandboxDryRunReviewSection = field(default_factory=lambda: PaperBrokerSandboxDryRunReviewSection("dry_run_account_policy", 0, False))
    dry_run_observability_policy: PaperBrokerSandboxDryRunReviewSection = field(default_factory=lambda: PaperBrokerSandboxDryRunReviewSection("dry_run_observability_policy", 0, False))
    dry_run_rollback_policy: PaperBrokerSandboxDryRunReviewSection = field(default_factory=lambda: PaperBrokerSandboxDryRunReviewSection("dry_run_rollback_policy", 0, False))
    dry_run_kill_switch_policy: PaperBrokerSandboxDryRunReviewSection = field(default_factory=lambda: PaperBrokerSandboxDryRunReviewSection("dry_run_kill_switch_policy", 0, False))
    dry_run_human_supervision_policy: PaperBrokerSandboxDryRunReviewSection = field(default_factory=lambda: PaperBrokerSandboxDryRunReviewSection("dry_run_human_supervision_policy", 0, False))
    dry_run_journal_policy: PaperBrokerSandboxDryRunReviewSection = field(default_factory=lambda: PaperBrokerSandboxDryRunReviewSection("dry_run_journal_policy", 0, False))
    dry_run_stop_conditions: PaperBrokerSandboxDryRunReviewSection = field(default_factory=lambda: PaperBrokerSandboxDryRunReviewSection("dry_run_stop_conditions", 0, False))
    dry_run_success_criteria: PaperBrokerSandboxDryRunReviewSection = field(default_factory=lambda: PaperBrokerSandboxDryRunReviewSection("dry_run_success_criteria", 0, False))
    dry_run_failure_criteria: PaperBrokerSandboxDryRunReviewSection = field(default_factory=lambda: PaperBrokerSandboxDryRunReviewSection("dry_run_failure_criteria", 0, False))
    recommendations: tuple[PaperBrokerSandboxDryRunReviewRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""

