"""Models for the offline AGIcore Paper Broker Sandbox Dry Run Controlled Simulation Plan."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerSandboxDryRunControlledSimulationPlanState(StrEnum):
    NOT_READY = "NOT_READY"
    CONTROLLED_SIMULATION_PLAN_REVIEW_REQUIRED = "CONTROLLED_SIMULATION_PLAN_REVIEW_REQUIRED"
    PARTIALLY_PLANNED = "PARTIALLY_PLANNED"
    CONTROLLED_SIMULATION_PLAN_READY = "CONTROLLED_SIMULATION_PLAN_READY"
    READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_REVIEW = (
        "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_REVIEW"
    )


class PaperBrokerSandboxDryRunControlledSimulationPlanDecision(StrEnum):
    BLOCK_PAPER_BROKER_SANDBOX_CONTROLLED_SIMULATION = "BLOCK_PAPER_BROKER_SANDBOX_CONTROLLED_SIMULATION"
    REQUIRE_EXECUTION_AUTHORIZATION_GATE_FIXES = "REQUIRE_EXECUTION_AUTHORIZATION_GATE_FIXES"
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
    APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_PLAN = (
        "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_PLAN"
    )


class PaperBrokerSandboxDryRunControlledSimulationPlanRisk(StrEnum):
    EXECUTION_AUTHORIZATION_GATE_NOT_APPROVED = "EXECUTION_AUTHORIZATION_GATE_NOT_APPROVED"
    CONTROLLED_SIMULATION_SCOPE_UNCLEAR = "CONTROLLED_SIMULATION_SCOPE_UNCLEAR"
    CONTROLLED_SIMULATION_BOUNDARY_GAP = "CONTROLLED_SIMULATION_BOUNDARY_GAP"
    CONTROLLED_SIMULATION_SCENARIO_UNDEFINED = "CONTROLLED_SIMULATION_SCENARIO_UNDEFINED"
    CONTROLLED_SIMULATION_SESSION_LIMIT_GAP = "CONTROLLED_SIMULATION_SESSION_LIMIT_GAP"
    CONTROLLED_SIMULATION_CONNECTION_POLICY_GAP = "CONTROLLED_SIMULATION_CONNECTION_POLICY_GAP"
    CONTROLLED_SIMULATION_ORDER_POLICY_GAP = "CONTROLLED_SIMULATION_ORDER_POLICY_GAP"
    CONTROLLED_SIMULATION_POSITION_POLICY_GAP = "CONTROLLED_SIMULATION_POSITION_POLICY_GAP"
    CONTROLLED_SIMULATION_ACCOUNT_POLICY_GAP = "CONTROLLED_SIMULATION_ACCOUNT_POLICY_GAP"
    CONTROLLED_SIMULATION_OBSERVABILITY_GAP = "CONTROLLED_SIMULATION_OBSERVABILITY_GAP"
    CONTROLLED_SIMULATION_ROLLBACK_GAP = "CONTROLLED_SIMULATION_ROLLBACK_GAP"
    CONTROLLED_SIMULATION_KILL_SWITCH_GAP = "CONTROLLED_SIMULATION_KILL_SWITCH_GAP"
    CONTROLLED_SIMULATION_HUMAN_SUPERVISION_GAP = "CONTROLLED_SIMULATION_HUMAN_SUPERVISION_GAP"
    CONTROLLED_SIMULATION_JOURNAL_GAP = "CONTROLLED_SIMULATION_JOURNAL_GAP"
    CONTROLLED_SIMULATION_STOP_CONDITION_GAP = "CONTROLLED_SIMULATION_STOP_CONDITION_GAP"
    CONTROLLED_SIMULATION_ABORT_CONDITION_GAP = "CONTROLLED_SIMULATION_ABORT_CONDITION_GAP"
    CONTROLLED_SIMULATION_SUCCESS_FAILURE_CRITERIA_GAP = "CONTROLLED_SIMULATION_SUCCESS_FAILURE_CRITERIA_GAP"
    PREMATURE_PAPER_BROKER_SANDBOX_CONTROLLED_SIMULATION_EXECUTION = (
        "PREMATURE_PAPER_BROKER_SANDBOX_CONTROLLED_SIMULATION_EXECUTION"
    )


class PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation(StrEnum):
    HOLD_PAPER_BROKER_SANDBOX_CONTROLLED_SIMULATION_REVIEW = "HOLD_PAPER_BROKER_SANDBOX_CONTROLLED_SIMULATION_REVIEW"
    APPROVE_EXECUTION_AUTHORIZATION_GATE_FIRST = "APPROVE_EXECUTION_AUTHORIZATION_GATE_FIRST"
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
    COMPLETE_CONTROLLED_SIMULATION_SUCCESS_FAILURE_CRITERIA = "COMPLETE_CONTROLLED_SIMULATION_SUCCESS_FAILURE_CRITERIA"
    DELAY_PAPER_BROKER_SANDBOX_CONTROLLED_SIMULATION_EXECUTION = "DELAY_PAPER_BROKER_SANDBOX_CONTROLLED_SIMULATION_EXECUTION"
    RUN_PAPER_BROKER_SANDBOX_CONTROLLED_SIMULATION_PLAN_SUITE = "RUN_PAPER_BROKER_SANDBOX_CONTROLLED_SIMULATION_PLAN_SUITE"
    APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_REVIEW = (
        "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_REVIEW"
    )


@dataclass(frozen=True)
class PaperBrokerSandboxDryRunControlledSimulationPlanInput:
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
    execution_authorization_gate_approved: bool | None = None
    execution_authorization_gate_reviewed: bool | None = None
    controlled_simulation_scope_defined: bool | None = None
    controlled_simulation_scope_clear: bool | None = None
    controlled_simulation_boundaries_defined: bool | None = None
    controlled_simulation_boundaries_complete: bool | None = None
    controlled_simulation_scenario_defined: bool | None = None
    controlled_simulation_scenario_complete: bool | None = None
    controlled_simulation_session_limits_defined: bool | None = None
    controlled_simulation_session_limits_complete: bool | None = None
    controlled_simulation_connection_policy_defined: bool | None = None
    controlled_simulation_connection_policy_complete: bool | None = None
    controlled_simulation_order_policy_defined: bool | None = None
    controlled_simulation_order_policy_complete: bool | None = None
    controlled_simulation_position_policy_defined: bool | None = None
    controlled_simulation_position_policy_complete: bool | None = None
    controlled_simulation_account_policy_defined: bool | None = None
    controlled_simulation_account_policy_complete: bool | None = None
    controlled_simulation_observability_policy_defined: bool | None = None
    controlled_simulation_observability_policy_complete: bool | None = None
    controlled_simulation_rollback_policy_defined: bool | None = None
    controlled_simulation_rollback_policy_complete: bool | None = None
    controlled_simulation_kill_switch_policy_defined: bool | None = None
    controlled_simulation_kill_switch_policy_complete: bool | None = None
    controlled_simulation_human_supervision_policy_defined: bool | None = None
    controlled_simulation_human_supervision_policy_complete: bool | None = None
    controlled_simulation_journal_policy_defined: bool | None = None
    controlled_simulation_journal_policy_complete: bool | None = None
    controlled_simulation_stop_conditions_defined: bool | None = None
    controlled_simulation_stop_conditions_complete: bool | None = None
    controlled_simulation_abort_conditions_defined: bool | None = None
    controlled_simulation_abort_conditions_complete: bool | None = None
    controlled_simulation_success_criteria_defined: bool | None = None
    controlled_simulation_success_criteria_complete: bool | None = None
    controlled_simulation_failure_criteria_defined: bool | None = None
    controlled_simulation_failure_criteria_complete: bool | None = None
    paper_broker_sandbox_dry_run_controlled_simulation_plan_requested: bool | None = None
    paper_broker_sandbox_dry_run_controlled_simulation_requested: bool | None = None
    paper_broker_sandbox_dry_run_controlled_simulation_execution_requested: bool | None = None
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
    execution_authorization_gate_readiness_score: int | None = None
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
    controlled_simulation_success_criteria_score: int | None = None
    controlled_simulation_failure_criteria_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerSandboxDryRunControlledSimulationPlanSection:
    name: str
    score: int
    passed: bool
    risks: tuple[PaperBrokerSandboxDryRunControlledSimulationPlanRisk, ...] = ()
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerSandboxDryRunControlledSimulationPlanScore:
    overall_score: int
    execution_authorization_gate_readiness_score: int
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
    controlled_simulation_success_criteria_score: int
    controlled_simulation_failure_criteria_score: int


@dataclass(frozen=True)
class PaperBrokerSandboxDryRunControlledSimulationPlanResult:
    state: PaperBrokerSandboxDryRunControlledSimulationPlanState
    decision: PaperBrokerSandboxDryRunControlledSimulationPlanDecision
    plan_score: int
    score_breakdown: PaperBrokerSandboxDryRunControlledSimulationPlanScore
    risks: tuple[PaperBrokerSandboxDryRunControlledSimulationPlanRisk, ...] = ()
    execution_authorization_gate_readiness: PaperBrokerSandboxDryRunControlledSimulationPlanSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunControlledSimulationPlanSection("execution_authorization_gate_readiness", 0, False)
    )
    controlled_simulation_scope: PaperBrokerSandboxDryRunControlledSimulationPlanSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunControlledSimulationPlanSection("controlled_simulation_scope", 0, False)
    )
    controlled_simulation_boundaries: PaperBrokerSandboxDryRunControlledSimulationPlanSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunControlledSimulationPlanSection("controlled_simulation_boundaries", 0, False)
    )
    controlled_simulation_scenario: PaperBrokerSandboxDryRunControlledSimulationPlanSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunControlledSimulationPlanSection("controlled_simulation_scenario", 0, False)
    )
    controlled_simulation_session_limits: PaperBrokerSandboxDryRunControlledSimulationPlanSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunControlledSimulationPlanSection("controlled_simulation_session_limits", 0, False)
    )
    controlled_simulation_connection_policy: PaperBrokerSandboxDryRunControlledSimulationPlanSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunControlledSimulationPlanSection("controlled_simulation_connection_policy", 0, False)
    )
    controlled_simulation_order_policy: PaperBrokerSandboxDryRunControlledSimulationPlanSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunControlledSimulationPlanSection("controlled_simulation_order_policy", 0, False)
    )
    controlled_simulation_position_policy: PaperBrokerSandboxDryRunControlledSimulationPlanSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunControlledSimulationPlanSection("controlled_simulation_position_policy", 0, False)
    )
    controlled_simulation_account_policy: PaperBrokerSandboxDryRunControlledSimulationPlanSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunControlledSimulationPlanSection("controlled_simulation_account_policy", 0, False)
    )
    controlled_simulation_observability_policy: PaperBrokerSandboxDryRunControlledSimulationPlanSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunControlledSimulationPlanSection("controlled_simulation_observability_policy", 0, False)
    )
    controlled_simulation_rollback_policy: PaperBrokerSandboxDryRunControlledSimulationPlanSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunControlledSimulationPlanSection("controlled_simulation_rollback_policy", 0, False)
    )
    controlled_simulation_kill_switch_policy: PaperBrokerSandboxDryRunControlledSimulationPlanSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunControlledSimulationPlanSection("controlled_simulation_kill_switch_policy", 0, False)
    )
    controlled_simulation_human_supervision_policy: PaperBrokerSandboxDryRunControlledSimulationPlanSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunControlledSimulationPlanSection("controlled_simulation_human_supervision_policy", 0, False)
    )
    controlled_simulation_journal_policy: PaperBrokerSandboxDryRunControlledSimulationPlanSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunControlledSimulationPlanSection("controlled_simulation_journal_policy", 0, False)
    )
    controlled_simulation_stop_conditions: PaperBrokerSandboxDryRunControlledSimulationPlanSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunControlledSimulationPlanSection("controlled_simulation_stop_conditions", 0, False)
    )
    controlled_simulation_abort_conditions: PaperBrokerSandboxDryRunControlledSimulationPlanSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunControlledSimulationPlanSection("controlled_simulation_abort_conditions", 0, False)
    )
    controlled_simulation_success_criteria: PaperBrokerSandboxDryRunControlledSimulationPlanSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunControlledSimulationPlanSection("controlled_simulation_success_criteria", 0, False)
    )
    controlled_simulation_failure_criteria: PaperBrokerSandboxDryRunControlledSimulationPlanSection = field(
        default_factory=lambda: PaperBrokerSandboxDryRunControlledSimulationPlanSection("controlled_simulation_failure_criteria", 0, False)
    )
    recommendations: tuple[PaperBrokerSandboxDryRunControlledSimulationPlanRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
