"""Models for the offline AGIcore controlled simulation review + precheck."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerSandboxControlledSimulationReviewPrecheckState(StrEnum):
    NOT_READY = "NOT_READY"
    REVIEW_PRECHECK_REQUIRED = "REVIEW_PRECHECK_REQUIRED"
    PARTIALLY_READY = "PARTIALLY_READY"
    CONTROLLED_SIMULATION_REVIEW_PRECHECK_READY = "CONTROLLED_SIMULATION_REVIEW_PRECHECK_READY"
    READY_FOR_CONTROLLED_SIMULATION_OFFLINE_RUNNER = "READY_FOR_CONTROLLED_SIMULATION_OFFLINE_RUNNER"


class PaperBrokerSandboxControlledSimulationReviewPrecheckDecision(StrEnum):
    BLOCK_CONTROLLED_SIMULATION = "BLOCK_CONTROLLED_SIMULATION"
    REQUIRE_CONTROLLED_SIMULATION_PLAN_FIXES = "REQUIRE_CONTROLLED_SIMULATION_PLAN_FIXES"
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
    REQUIRE_ABORT_CONDITION_FIXES = "REQUIRE_ABORT_CONDITION_FIXES"
    REQUIRE_SUCCESS_FAILURE_CRITERIA_FIXES = "REQUIRE_SUCCESS_FAILURE_CRITERIA_FIXES"
    APPROVE_CONTROLLED_SIMULATION_REVIEW_PRECHECK = "APPROVE_CONTROLLED_SIMULATION_REVIEW_PRECHECK"


class PaperBrokerSandboxControlledSimulationReviewPrecheckRisk(StrEnum):
    CONTROLLED_SIMULATION_PLAN_NOT_APPROVED = "CONTROLLED_SIMULATION_PLAN_NOT_APPROVED"
    CONTROLLED_SIMULATION_SCOPE_UNCLEAR = "CONTROLLED_SIMULATION_SCOPE_UNCLEAR"
    CONTROLLED_SIMULATION_BOUNDARY_INCOMPLETE = "CONTROLLED_SIMULATION_BOUNDARY_INCOMPLETE"
    CONTROLLED_SIMULATION_SCENARIO_INCOMPLETE = "CONTROLLED_SIMULATION_SCENARIO_INCOMPLETE"
    CONTROLLED_SIMULATION_SESSION_LIMIT_INCOMPLETE = "CONTROLLED_SIMULATION_SESSION_LIMIT_INCOMPLETE"
    CONTROLLED_SIMULATION_CONNECTION_POLICY_INCOMPLETE = "CONTROLLED_SIMULATION_CONNECTION_POLICY_INCOMPLETE"
    CONTROLLED_SIMULATION_ORDER_POLICY_INCOMPLETE = "CONTROLLED_SIMULATION_ORDER_POLICY_INCOMPLETE"
    CONTROLLED_SIMULATION_POSITION_POLICY_INCOMPLETE = "CONTROLLED_SIMULATION_POSITION_POLICY_INCOMPLETE"
    CONTROLLED_SIMULATION_ACCOUNT_POLICY_INCOMPLETE = "CONTROLLED_SIMULATION_ACCOUNT_POLICY_INCOMPLETE"
    CONTROLLED_SIMULATION_OBSERVABILITY_INCOMPLETE = "CONTROLLED_SIMULATION_OBSERVABILITY_INCOMPLETE"
    CONTROLLED_SIMULATION_ROLLBACK_INCOMPLETE = "CONTROLLED_SIMULATION_ROLLBACK_INCOMPLETE"
    CONTROLLED_SIMULATION_KILL_SWITCH_INCOMPLETE = "CONTROLLED_SIMULATION_KILL_SWITCH_INCOMPLETE"
    CONTROLLED_SIMULATION_HUMAN_SUPERVISION_INCOMPLETE = "CONTROLLED_SIMULATION_HUMAN_SUPERVISION_INCOMPLETE"
    CONTROLLED_SIMULATION_JOURNAL_INCOMPLETE = "CONTROLLED_SIMULATION_JOURNAL_INCOMPLETE"
    CONTROLLED_SIMULATION_STOP_CONDITION_INCOMPLETE = "CONTROLLED_SIMULATION_STOP_CONDITION_INCOMPLETE"
    CONTROLLED_SIMULATION_ABORT_CONDITION_INCOMPLETE = "CONTROLLED_SIMULATION_ABORT_CONDITION_INCOMPLETE"
    CONTROLLED_SIMULATION_SUCCESS_FAILURE_CRITERIA_INCOMPLETE = (
        "CONTROLLED_SIMULATION_SUCCESS_FAILURE_CRITERIA_INCOMPLETE"
    )
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    PREMATURE_CONTROLLED_SIMULATION_OFFLINE_RUNNER = "PREMATURE_CONTROLLED_SIMULATION_OFFLINE_RUNNER"


class PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation(StrEnum):
    HOLD_CONTROLLED_SIMULATION_OFFLINE_RUNNER = "HOLD_CONTROLLED_SIMULATION_OFFLINE_RUNNER"
    APPROVE_CONTROLLED_SIMULATION_PLAN_FIRST = "APPROVE_CONTROLLED_SIMULATION_PLAN_FIRST"
    CLARIFY_CONTROLLED_SIMULATION_SCOPE = "CLARIFY_CONTROLLED_SIMULATION_SCOPE"
    COMPLETE_CONTROLLED_SIMULATION_BOUNDARIES = "COMPLETE_CONTROLLED_SIMULATION_BOUNDARIES"
    COMPLETE_CONTROLLED_SIMULATION_SCENARIO = "COMPLETE_CONTROLLED_SIMULATION_SCENARIO"
    COMPLETE_CONTROLLED_SIMULATION_SESSION_LIMITS = "COMPLETE_CONTROLLED_SIMULATION_SESSION_LIMITS"
    COMPLETE_CONTROLLED_SIMULATION_CONNECTION_POLICY = "COMPLETE_CONTROLLED_SIMULATION_CONNECTION_POLICY"
    COMPLETE_CONTROLLED_SIMULATION_ORDER_POLICY = "COMPLETE_CONTROLLED_SIMULATION_ORDER_POLICY"
    COMPLETE_CONTROLLED_SIMULATION_POSITION_POLICY = "COMPLETE_CONTROLLED_SIMULATION_POSITION_POLICY"
    COMPLETE_CONTROLLED_SIMULATION_ACCOUNT_POLICY = "COMPLETE_CONTROLLED_SIMULATION_ACCOUNT_POLICY"
    COMPLETE_CONTROLLED_SIMULATION_OBSERVABILITY_POLICY = "COMPLETE_CONTROLLED_SIMULATION_OBSERVABILITY_POLICY"
    COMPLETE_CONTROLLED_SIMULATION_ROLLBACK_POLICY = "COMPLETE_CONTROLLED_SIMULATION_ROLLBACK_POLICY"
    COMPLETE_CONTROLLED_SIMULATION_KILL_SWITCH_POLICY = "COMPLETE_CONTROLLED_SIMULATION_KILL_SWITCH_POLICY"
    COMPLETE_CONTROLLED_SIMULATION_HUMAN_SUPERVISION_POLICY = "COMPLETE_CONTROLLED_SIMULATION_HUMAN_SUPERVISION_POLICY"
    COMPLETE_CONTROLLED_SIMULATION_JOURNAL_POLICY = "COMPLETE_CONTROLLED_SIMULATION_JOURNAL_POLICY"
    COMPLETE_CONTROLLED_SIMULATION_STOP_CONDITIONS = "COMPLETE_CONTROLLED_SIMULATION_STOP_CONDITIONS"
    COMPLETE_CONTROLLED_SIMULATION_ABORT_CONDITIONS = "COMPLETE_CONTROLLED_SIMULATION_ABORT_CONDITIONS"
    COMPLETE_CONTROLLED_SIMULATION_SUCCESS_FAILURE_CRITERIA = (
        "COMPLETE_CONTROLLED_SIMULATION_SUCCESS_FAILURE_CRITERIA"
    )
    RESTORE_REAL_EXECUTION_BOUNDARIES = "RESTORE_REAL_EXECUTION_BOUNDARIES"
    DELAY_CONTROLLED_SIMULATION_OFFLINE_RUNNER = "DELAY_CONTROLLED_SIMULATION_OFFLINE_RUNNER"
    RUN_CONTROLLED_SIMULATION_REVIEW_PRECHECK_SUITE = "RUN_CONTROLLED_SIMULATION_REVIEW_PRECHECK_SUITE"
    APPROVE_CONTROLLED_SIMULATION_OFFLINE_RUNNER = "APPROVE_CONTROLLED_SIMULATION_OFFLINE_RUNNER"


@dataclass(frozen=True)
class PaperBrokerSandboxControlledSimulationReviewPrecheckInput:
    paper_broker_sandbox_dry_run_controlled_simulation_plan: Any = None
    paper_broker_sandbox_dry_run_execution_authorization_gate: Any = None
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
    observability_verification: Any = None
    rollback_verification: Any = None
    kill_switch_verification: Any = None
    human_validated_paper_session: Any = None
    supervised_paper_session: Any = None
    controlled_simulation_plan_approved: bool | None = None
    controlled_simulation_plan_reviewed: bool | None = None
    controlled_simulation_scope_reviewed: bool | None = None
    controlled_simulation_scope_clear: bool | None = None
    controlled_simulation_boundaries_reviewed: bool | None = None
    controlled_simulation_boundaries_complete: bool | None = None
    controlled_simulation_scenario_reviewed: bool | None = None
    controlled_simulation_scenario_complete: bool | None = None
    controlled_simulation_session_limits_reviewed: bool | None = None
    controlled_simulation_session_limits_complete: bool | None = None
    controlled_simulation_connection_policy_reviewed: bool | None = None
    controlled_simulation_connection_policy_complete: bool | None = None
    controlled_simulation_order_policy_reviewed: bool | None = None
    controlled_simulation_order_policy_complete: bool | None = None
    controlled_simulation_position_policy_reviewed: bool | None = None
    controlled_simulation_position_policy_complete: bool | None = None
    controlled_simulation_account_policy_reviewed: bool | None = None
    controlled_simulation_account_policy_complete: bool | None = None
    controlled_simulation_observability_policy_reviewed: bool | None = None
    controlled_simulation_observability_policy_complete: bool | None = None
    controlled_simulation_rollback_policy_reviewed: bool | None = None
    controlled_simulation_rollback_policy_complete: bool | None = None
    controlled_simulation_kill_switch_policy_reviewed: bool | None = None
    controlled_simulation_kill_switch_policy_complete: bool | None = None
    controlled_simulation_human_supervision_policy_reviewed: bool | None = None
    controlled_simulation_human_supervision_policy_complete: bool | None = None
    controlled_simulation_journal_policy_reviewed: bool | None = None
    controlled_simulation_journal_policy_complete: bool | None = None
    controlled_simulation_stop_conditions_reviewed: bool | None = None
    controlled_simulation_stop_conditions_complete: bool | None = None
    controlled_simulation_abort_conditions_reviewed: bool | None = None
    controlled_simulation_abort_conditions_complete: bool | None = None
    controlled_simulation_success_failure_criteria_reviewed: bool | None = None
    controlled_simulation_success_failure_criteria_complete: bool | None = None
    controlled_simulation_pre_execution_safety_reviewed: bool | None = None
    controlled_simulation_pre_execution_safe: bool | None = None
    controlled_simulation_human_approval_required: bool | None = None
    controlled_simulation_human_approval_confirmed: bool | None = None
    controlled_simulation_review_precheck_requested: bool | None = None
    controlled_simulation_offline_runner_requested: bool | None = None
    controlled_simulation_real_execution_requested: bool | None = None
    controlled_simulation_execution_requested: bool | None = None
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
    controlled_simulation_plan_readiness_score: int | None = None
    controlled_simulation_scope_score: int | None = None
    controlled_simulation_boundaries_score: int | None = None
    controlled_simulation_scenario_score: int | None = None
    controlled_simulation_session_limits_score: int | None = None
    controlled_simulation_connection_policy_score: int | None = None
    controlled_simulation_order_policy_score: int | None = None
    controlled_simulation_position_policy_score: int | None = None
    controlled_simulation_account_policy_score: int | None = None
    controlled_simulation_observability_policy_score: int | None = None
    controlled_simulation_rollback_policy_score: int | None = None
    controlled_simulation_kill_switch_policy_score: int | None = None
    controlled_simulation_human_supervision_policy_score: int | None = None
    controlled_simulation_journal_policy_score: int | None = None
    controlled_simulation_stop_conditions_score: int | None = None
    controlled_simulation_abort_conditions_score: int | None = None
    controlled_simulation_success_failure_criteria_score: int | None = None
    controlled_simulation_pre_execution_safety_score: int | None = None
    controlled_simulation_no_real_execution_score: int | None = None
    controlled_simulation_offline_boundaries_score: int | None = None
    controlled_simulation_human_approval_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerSandboxControlledSimulationReviewPrecheckSection:
    name: str
    score: int
    passed: bool
    risks: tuple[PaperBrokerSandboxControlledSimulationReviewPrecheckRisk, ...] = ()
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerSandboxControlledSimulationReviewPrecheckScore:
    overall_score: int
    controlled_simulation_plan_readiness_score: int
    controlled_simulation_scope_score: int
    controlled_simulation_boundaries_score: int
    controlled_simulation_scenario_score: int
    controlled_simulation_session_limits_score: int
    controlled_simulation_connection_policy_score: int
    controlled_simulation_order_policy_score: int
    controlled_simulation_position_policy_score: int
    controlled_simulation_account_policy_score: int
    controlled_simulation_observability_policy_score: int
    controlled_simulation_rollback_policy_score: int
    controlled_simulation_kill_switch_policy_score: int
    controlled_simulation_human_supervision_policy_score: int
    controlled_simulation_journal_policy_score: int
    controlled_simulation_stop_conditions_score: int
    controlled_simulation_abort_conditions_score: int
    controlled_simulation_success_failure_criteria_score: int
    controlled_simulation_pre_execution_safety_score: int
    controlled_simulation_no_real_execution_score: int
    controlled_simulation_offline_boundaries_score: int
    controlled_simulation_human_approval_score: int


@dataclass(frozen=True)
class PaperBrokerSandboxControlledSimulationReviewPrecheckResult:
    state: PaperBrokerSandboxControlledSimulationReviewPrecheckState
    decision: PaperBrokerSandboxControlledSimulationReviewPrecheckDecision
    review_precheck_score: int
    score_breakdown: PaperBrokerSandboxControlledSimulationReviewPrecheckScore
    risks: tuple[PaperBrokerSandboxControlledSimulationReviewPrecheckRisk, ...] = ()
    controlled_simulation_plan_readiness: PaperBrokerSandboxControlledSimulationReviewPrecheckSection = field(
        default_factory=lambda: PaperBrokerSandboxControlledSimulationReviewPrecheckSection(
            "controlled_simulation_plan_readiness",
            0,
            False,
        )
    )
    controlled_simulation_scope: PaperBrokerSandboxControlledSimulationReviewPrecheckSection = field(
        default_factory=lambda: PaperBrokerSandboxControlledSimulationReviewPrecheckSection("controlled_simulation_scope", 0, False)
    )
    controlled_simulation_boundaries: PaperBrokerSandboxControlledSimulationReviewPrecheckSection = field(
        default_factory=lambda: PaperBrokerSandboxControlledSimulationReviewPrecheckSection("controlled_simulation_boundaries", 0, False)
    )
    controlled_simulation_scenario: PaperBrokerSandboxControlledSimulationReviewPrecheckSection = field(
        default_factory=lambda: PaperBrokerSandboxControlledSimulationReviewPrecheckSection("controlled_simulation_scenario", 0, False)
    )
    controlled_simulation_session_limits: PaperBrokerSandboxControlledSimulationReviewPrecheckSection = field(
        default_factory=lambda: PaperBrokerSandboxControlledSimulationReviewPrecheckSection("controlled_simulation_session_limits", 0, False)
    )
    controlled_simulation_connection_policy: PaperBrokerSandboxControlledSimulationReviewPrecheckSection = field(
        default_factory=lambda: PaperBrokerSandboxControlledSimulationReviewPrecheckSection(
            "controlled_simulation_connection_policy",
            0,
            False,
        )
    )
    controlled_simulation_order_policy: PaperBrokerSandboxControlledSimulationReviewPrecheckSection = field(
        default_factory=lambda: PaperBrokerSandboxControlledSimulationReviewPrecheckSection("controlled_simulation_order_policy", 0, False)
    )
    controlled_simulation_position_policy: PaperBrokerSandboxControlledSimulationReviewPrecheckSection = field(
        default_factory=lambda: PaperBrokerSandboxControlledSimulationReviewPrecheckSection("controlled_simulation_position_policy", 0, False)
    )
    controlled_simulation_account_policy: PaperBrokerSandboxControlledSimulationReviewPrecheckSection = field(
        default_factory=lambda: PaperBrokerSandboxControlledSimulationReviewPrecheckSection("controlled_simulation_account_policy", 0, False)
    )
    controlled_simulation_observability_policy: PaperBrokerSandboxControlledSimulationReviewPrecheckSection = field(
        default_factory=lambda: PaperBrokerSandboxControlledSimulationReviewPrecheckSection(
            "controlled_simulation_observability_policy",
            0,
            False,
        )
    )
    controlled_simulation_rollback_policy: PaperBrokerSandboxControlledSimulationReviewPrecheckSection = field(
        default_factory=lambda: PaperBrokerSandboxControlledSimulationReviewPrecheckSection("controlled_simulation_rollback_policy", 0, False)
    )
    controlled_simulation_kill_switch_policy: PaperBrokerSandboxControlledSimulationReviewPrecheckSection = field(
        default_factory=lambda: PaperBrokerSandboxControlledSimulationReviewPrecheckSection("controlled_simulation_kill_switch_policy", 0, False)
    )
    controlled_simulation_human_supervision_policy: PaperBrokerSandboxControlledSimulationReviewPrecheckSection = field(
        default_factory=lambda: PaperBrokerSandboxControlledSimulationReviewPrecheckSection(
            "controlled_simulation_human_supervision_policy",
            0,
            False,
        )
    )
    controlled_simulation_journal_policy: PaperBrokerSandboxControlledSimulationReviewPrecheckSection = field(
        default_factory=lambda: PaperBrokerSandboxControlledSimulationReviewPrecheckSection("controlled_simulation_journal_policy", 0, False)
    )
    controlled_simulation_stop_conditions: PaperBrokerSandboxControlledSimulationReviewPrecheckSection = field(
        default_factory=lambda: PaperBrokerSandboxControlledSimulationReviewPrecheckSection("controlled_simulation_stop_conditions", 0, False)
    )
    controlled_simulation_abort_conditions: PaperBrokerSandboxControlledSimulationReviewPrecheckSection = field(
        default_factory=lambda: PaperBrokerSandboxControlledSimulationReviewPrecheckSection("controlled_simulation_abort_conditions", 0, False)
    )
    controlled_simulation_success_failure_criteria: PaperBrokerSandboxControlledSimulationReviewPrecheckSection = field(
        default_factory=lambda: PaperBrokerSandboxControlledSimulationReviewPrecheckSection(
            "controlled_simulation_success_failure_criteria",
            0,
            False,
        )
    )
    controlled_simulation_pre_execution_safety: PaperBrokerSandboxControlledSimulationReviewPrecheckSection = field(
        default_factory=lambda: PaperBrokerSandboxControlledSimulationReviewPrecheckSection(
            "controlled_simulation_pre_execution_safety",
            0,
            False,
        )
    )
    controlled_simulation_no_real_execution: PaperBrokerSandboxControlledSimulationReviewPrecheckSection = field(
        default_factory=lambda: PaperBrokerSandboxControlledSimulationReviewPrecheckSection("controlled_simulation_no_real_execution", 0, False)
    )
    controlled_simulation_offline_boundaries: PaperBrokerSandboxControlledSimulationReviewPrecheckSection = field(
        default_factory=lambda: PaperBrokerSandboxControlledSimulationReviewPrecheckSection("controlled_simulation_offline_boundaries", 0, False)
    )
    controlled_simulation_human_approval: PaperBrokerSandboxControlledSimulationReviewPrecheckSection = field(
        default_factory=lambda: PaperBrokerSandboxControlledSimulationReviewPrecheckSection("controlled_simulation_human_approval", 0, False)
    )
    recommendations: tuple[PaperBrokerSandboxControlledSimulationReviewPrecheckRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
