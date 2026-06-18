"""Models for the offline AGIcore Paper Broker Sandbox Dry Run Plan."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerSandboxDryRunPlanState(StrEnum):
    NOT_READY = "NOT_READY"
    DRY_RUN_PLAN_REVIEW_REQUIRED = "DRY_RUN_PLAN_REVIEW_REQUIRED"
    PARTIALLY_PLANNED = "PARTIALLY_PLANNED"
    DRY_RUN_PLAN_READY = "DRY_RUN_PLAN_READY"
    READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_REVIEW = "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_REVIEW"


class PaperBrokerSandboxDryRunPlanDecision(StrEnum):
    BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN = "BLOCK_PAPER_BROKER_SANDBOX_DRY_RUN"
    REQUIRE_AUTHORIZATION_GATE_FIXES = "REQUIRE_AUTHORIZATION_GATE_FIXES"
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
    APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_PLAN = "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_PLAN"


class PaperBrokerSandboxDryRunPlanRisk(StrEnum):
    AUTHORIZATION_GATE_NOT_APPROVED = "AUTHORIZATION_GATE_NOT_APPROVED"
    DRY_RUN_SCOPE_UNCLEAR = "DRY_RUN_SCOPE_UNCLEAR"
    DRY_RUN_BOUNDARY_GAP = "DRY_RUN_BOUNDARY_GAP"
    DRY_RUN_SCENARIO_UNDEFINED = "DRY_RUN_SCENARIO_UNDEFINED"
    DRY_RUN_SESSION_LIMIT_GAP = "DRY_RUN_SESSION_LIMIT_GAP"
    DRY_RUN_CONNECTION_POLICY_GAP = "DRY_RUN_CONNECTION_POLICY_GAP"
    DRY_RUN_ORDER_POLICY_GAP = "DRY_RUN_ORDER_POLICY_GAP"
    DRY_RUN_POSITION_POLICY_GAP = "DRY_RUN_POSITION_POLICY_GAP"
    DRY_RUN_ACCOUNT_POLICY_GAP = "DRY_RUN_ACCOUNT_POLICY_GAP"
    DRY_RUN_OBSERVABILITY_GAP = "DRY_RUN_OBSERVABILITY_GAP"
    DRY_RUN_ROLLBACK_GAP = "DRY_RUN_ROLLBACK_GAP"
    DRY_RUN_KILL_SWITCH_GAP = "DRY_RUN_KILL_SWITCH_GAP"
    DRY_RUN_HUMAN_SUPERVISION_GAP = "DRY_RUN_HUMAN_SUPERVISION_GAP"
    DRY_RUN_JOURNAL_GAP = "DRY_RUN_JOURNAL_GAP"
    DRY_RUN_STOP_CONDITION_GAP = "DRY_RUN_STOP_CONDITION_GAP"
    PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION = "PREMATURE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION"


class PaperBrokerSandboxDryRunPlanRecommendation(StrEnum):
    HOLD_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION = "HOLD_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION"
    APPROVE_AUTHORIZATION_GATE_FIRST = "APPROVE_AUTHORIZATION_GATE_FIRST"
    CLARIFY_DRY_RUN_SCOPE = "CLARIFY_DRY_RUN_SCOPE"
    COMPLETE_DRY_RUN_BOUNDARIES = "COMPLETE_DRY_RUN_BOUNDARIES"
    DEFINE_DRY_RUN_SCENARIO = "DEFINE_DRY_RUN_SCENARIO"
    DEFINE_DRY_RUN_SESSION_LIMITS = "DEFINE_DRY_RUN_SESSION_LIMITS"
    DEFINE_DRY_RUN_CONNECTION_POLICY = "DEFINE_DRY_RUN_CONNECTION_POLICY"
    DEFINE_DRY_RUN_ORDER_POLICY = "DEFINE_DRY_RUN_ORDER_POLICY"
    DEFINE_DRY_RUN_POSITION_POLICY = "DEFINE_DRY_RUN_POSITION_POLICY"
    DEFINE_DRY_RUN_ACCOUNT_POLICY = "DEFINE_DRY_RUN_ACCOUNT_POLICY"
    DEFINE_DRY_RUN_OBSERVABILITY_POLICY = "DEFINE_DRY_RUN_OBSERVABILITY_POLICY"
    DEFINE_DRY_RUN_ROLLBACK_POLICY = "DEFINE_DRY_RUN_ROLLBACK_POLICY"
    DEFINE_DRY_RUN_KILL_SWITCH_POLICY = "DEFINE_DRY_RUN_KILL_SWITCH_POLICY"
    DEFINE_DRY_RUN_HUMAN_SUPERVISION_POLICY = "DEFINE_DRY_RUN_HUMAN_SUPERVISION_POLICY"
    DEFINE_DRY_RUN_JOURNAL_POLICY = "DEFINE_DRY_RUN_JOURNAL_POLICY"
    DEFINE_DRY_RUN_STOP_CONDITIONS = "DEFINE_DRY_RUN_STOP_CONDITIONS"
    DEFINE_DRY_RUN_SUCCESS_AND_FAILURE_CRITERIA = "DEFINE_DRY_RUN_SUCCESS_AND_FAILURE_CRITERIA"
    DELAY_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION = "DELAY_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION"
    RUN_PAPER_BROKER_SANDBOX_DRY_RUN_PLAN_SUITE = "RUN_PAPER_BROKER_SANDBOX_DRY_RUN_PLAN_SUITE"
    APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_REVIEW = "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_REVIEW"


@dataclass(frozen=True)
class PaperBrokerSandboxDryRunPlanInput:
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
    authorization_gate_approved: bool | None = None
    authorization_gate_reviewed: bool | None = None
    dry_run_scope_defined: bool | None = None
    dry_run_scope_clear: bool | None = None
    dry_run_boundaries_defined: bool | None = None
    dry_run_boundaries_complete: bool | None = None
    dry_run_scenario_defined: bool | None = None
    dry_run_session_limits_defined: bool | None = None
    dry_run_connection_policy_defined: bool | None = None
    dry_run_order_policy_defined: bool | None = None
    dry_run_position_policy_defined: bool | None = None
    dry_run_account_policy_defined: bool | None = None
    dry_run_observability_policy_defined: bool | None = None
    dry_run_rollback_policy_defined: bool | None = None
    dry_run_kill_switch_policy_defined: bool | None = None
    dry_run_human_supervision_policy_defined: bool | None = None
    dry_run_journal_policy_defined: bool | None = None
    dry_run_stop_conditions_defined: bool | None = None
    dry_run_success_criteria_defined: bool | None = None
    dry_run_failure_criteria_defined: bool | None = None
    paper_broker_sandbox_dry_run_plan_requested: bool | None = None
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
    authorization_gate_readiness_score: int | None = None
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
class PaperBrokerSandboxDryRunPlanSection:
    name: str
    score: int
    defined: bool
    risks: tuple[PaperBrokerSandboxDryRunPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerSandboxDryRunPlanScore:
    overall_score: int
    authorization_gate_readiness_score: int
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
class PaperBrokerSandboxDryRunPlanResult:
    state: PaperBrokerSandboxDryRunPlanState
    decision: PaperBrokerSandboxDryRunPlanDecision
    plan_score: int
    score_breakdown: PaperBrokerSandboxDryRunPlanScore
    risks: tuple[PaperBrokerSandboxDryRunPlanRisk, ...] = ()
    authorization_gate_readiness: PaperBrokerSandboxDryRunPlanSection = field(default_factory=lambda: PaperBrokerSandboxDryRunPlanSection("authorization_gate_readiness", 0, False))
    dry_run_scope: PaperBrokerSandboxDryRunPlanSection = field(default_factory=lambda: PaperBrokerSandboxDryRunPlanSection("dry_run_scope", 0, False))
    dry_run_boundaries: PaperBrokerSandboxDryRunPlanSection = field(default_factory=lambda: PaperBrokerSandboxDryRunPlanSection("dry_run_boundaries", 0, False))
    dry_run_scenario: PaperBrokerSandboxDryRunPlanSection = field(default_factory=lambda: PaperBrokerSandboxDryRunPlanSection("dry_run_scenario", 0, False))
    dry_run_session_limits: PaperBrokerSandboxDryRunPlanSection = field(default_factory=lambda: PaperBrokerSandboxDryRunPlanSection("dry_run_session_limits", 0, False))
    dry_run_connection_policy: PaperBrokerSandboxDryRunPlanSection = field(default_factory=lambda: PaperBrokerSandboxDryRunPlanSection("dry_run_connection_policy", 0, False))
    dry_run_order_policy: PaperBrokerSandboxDryRunPlanSection = field(default_factory=lambda: PaperBrokerSandboxDryRunPlanSection("dry_run_order_policy", 0, False))
    dry_run_position_policy: PaperBrokerSandboxDryRunPlanSection = field(default_factory=lambda: PaperBrokerSandboxDryRunPlanSection("dry_run_position_policy", 0, False))
    dry_run_account_policy: PaperBrokerSandboxDryRunPlanSection = field(default_factory=lambda: PaperBrokerSandboxDryRunPlanSection("dry_run_account_policy", 0, False))
    dry_run_observability_policy: PaperBrokerSandboxDryRunPlanSection = field(default_factory=lambda: PaperBrokerSandboxDryRunPlanSection("dry_run_observability_policy", 0, False))
    dry_run_rollback_policy: PaperBrokerSandboxDryRunPlanSection = field(default_factory=lambda: PaperBrokerSandboxDryRunPlanSection("dry_run_rollback_policy", 0, False))
    dry_run_kill_switch_policy: PaperBrokerSandboxDryRunPlanSection = field(default_factory=lambda: PaperBrokerSandboxDryRunPlanSection("dry_run_kill_switch_policy", 0, False))
    dry_run_human_supervision_policy: PaperBrokerSandboxDryRunPlanSection = field(default_factory=lambda: PaperBrokerSandboxDryRunPlanSection("dry_run_human_supervision_policy", 0, False))
    dry_run_journal_policy: PaperBrokerSandboxDryRunPlanSection = field(default_factory=lambda: PaperBrokerSandboxDryRunPlanSection("dry_run_journal_policy", 0, False))
    dry_run_stop_conditions: PaperBrokerSandboxDryRunPlanSection = field(default_factory=lambda: PaperBrokerSandboxDryRunPlanSection("dry_run_stop_conditions", 0, False))
    dry_run_success_criteria: PaperBrokerSandboxDryRunPlanSection = field(default_factory=lambda: PaperBrokerSandboxDryRunPlanSection("dry_run_success_criteria", 0, False))
    dry_run_failure_criteria: PaperBrokerSandboxDryRunPlanSection = field(default_factory=lambda: PaperBrokerSandboxDryRunPlanSection("dry_run_failure_criteria", 0, False))
    recommendations: tuple[PaperBrokerSandboxDryRunPlanRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""

