"""Models for the offline AGIcore Paper Runtime Forward Test Plan."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperRuntimeForwardTestPlanState(StrEnum):
    PLAN_NOT_READY = "PLAN_NOT_READY"
    PLAN_REVIEW_REQUIRED = "PLAN_REVIEW_REQUIRED"
    PLAN_PARTIALLY_READY = "PLAN_PARTIALLY_READY"
    PLAN_READY = "PLAN_READY"
    READY_FOR_PAPER_BROKER_SANDBOX_SESSION = "READY_FOR_PAPER_BROKER_SANDBOX_SESSION"


class PaperRuntimeForwardTestPlanDecision(StrEnum):
    BLOCK_FORWARD_TEST = "BLOCK_FORWARD_TEST"
    REQUIRE_SCOPE_FIXES = "REQUIRE_SCOPE_FIXES"
    REQUIRE_SUPERVISION_FIXES = "REQUIRE_SUPERVISION_FIXES"
    REQUIRE_LIMIT_FIXES = "REQUIRE_LIMIT_FIXES"
    REQUIRE_OBSERVABILITY_FIXES = "REQUIRE_OBSERVABILITY_FIXES"
    REQUIRE_ROLLBACK_FIXES = "REQUIRE_ROLLBACK_FIXES"
    REQUIRE_KILL_SWITCH_FIXES = "REQUIRE_KILL_SWITCH_FIXES"
    APPROVE_PAPER_RUNTIME_FORWARD_TEST_PLAN = "APPROVE_PAPER_RUNTIME_FORWARD_TEST_PLAN"


class PaperRuntimeForwardTestPlanRisk(StrEnum):
    FORWARD_TEST_SCOPE_UNCLEAR = "FORWARD_TEST_SCOPE_UNCLEAR"
    DURATION_UNDEFINED = "DURATION_UNDEFINED"
    SESSION_LIMITS_MISSING = "SESSION_LIMITS_MISSING"
    SIMULATED_LOSS_LIMITS_MISSING = "SIMULATED_LOSS_LIMITS_MISSING"
    HUMAN_SUPERVISION_RULES_MISSING = "HUMAN_SUPERVISION_RULES_MISSING"
    JOURNAL_REQUIREMENTS_MISSING = "JOURNAL_REQUIREMENTS_MISSING"
    OBSERVABILITY_REQUIREMENTS_MISSING = "OBSERVABILITY_REQUIREMENTS_MISSING"
    ROLLBACK_RULES_MISSING = "ROLLBACK_RULES_MISSING"
    KILL_SWITCH_RULES_MISSING = "KILL_SWITCH_RULES_MISSING"
    SUCCESS_CRITERIA_UNCLEAR = "SUCCESS_CRITERIA_UNCLEAR"
    FAILURE_CRITERIA_UNCLEAR = "FAILURE_CRITERIA_UNCLEAR"
    STOP_CONDITIONS_MISSING = "STOP_CONDITIONS_MISSING"
    PREMATURE_BROKER_SANDBOX_SESSION = "PREMATURE_BROKER_SANDBOX_SESSION"


class PaperRuntimeForwardTestPlanRecommendation(StrEnum):
    HOLD_BROKER_SANDBOX_SESSION = "HOLD_BROKER_SANDBOX_SESSION"
    CLARIFY_FORWARD_TEST_SCOPE = "CLARIFY_FORWARD_TEST_SCOPE"
    DEFINE_FORWARD_TEST_DURATION = "DEFINE_FORWARD_TEST_DURATION"
    DEFINE_ALLOWED_SESSION_LIMITS = "DEFINE_ALLOWED_SESSION_LIMITS"
    DEFINE_SIMULATED_LOSS_LIMITS = "DEFINE_SIMULATED_LOSS_LIMITS"
    DEFINE_HUMAN_SUPERVISION_RULES = "DEFINE_HUMAN_SUPERVISION_RULES"
    DEFINE_JOURNAL_REQUIREMENTS = "DEFINE_JOURNAL_REQUIREMENTS"
    DEFINE_OBSERVABILITY_REQUIREMENTS = "DEFINE_OBSERVABILITY_REQUIREMENTS"
    DEFINE_ROLLBACK_RULES = "DEFINE_ROLLBACK_RULES"
    DEFINE_KILL_SWITCH_RULES = "DEFINE_KILL_SWITCH_RULES"
    DEFINE_SUCCESS_CRITERIA = "DEFINE_SUCCESS_CRITERIA"
    DEFINE_FAILURE_CRITERIA = "DEFINE_FAILURE_CRITERIA"
    DEFINE_STOP_CONDITIONS = "DEFINE_STOP_CONDITIONS"
    DELAY_BROKER_SANDBOX_SESSION = "DELAY_BROKER_SANDBOX_SESSION"
    RUN_FORWARD_TEST_PLAN_REVIEW_SUITE = "RUN_FORWARD_TEST_PLAN_REVIEW_SUITE"
    APPROVE_PAPER_BROKER_SANDBOX_SESSION_PREP = "APPROVE_PAPER_BROKER_SANDBOX_SESSION_PREP"


@dataclass(frozen=True)
class PaperRuntimeForwardTestPlanInput:
    supervised_paper_runtime_trial: Any = None
    official_paper_validation_report: Any = None
    paper_runtime_validation: Any = None
    paper_runtime_release_candidate: Any = None
    paper_runtime_stabilization_review: Any = None
    extended_paper_runtime_test: Any = None
    paper_runtime_test_run: Any = None
    paper_trading_runtime: Any = None
    paper_runtime_integration_review: Any = None
    paper_trading_runtime_design: Any = None
    paper_runtime_decision_review: Any = None
    observability_verification: Any = None
    rollback_verification: Any = None
    kill_switch_verification: Any = None
    human_validated_paper_session: Any = None
    supervised_paper_session: Any = None
    forward_test_scope_defined: bool | None = None
    duration_defined: bool | None = None
    session_limits_defined: bool | None = None
    simulated_loss_limits_defined: bool | None = None
    human_supervision_rules_defined: bool | None = None
    journal_requirements_defined: bool | None = None
    observability_requirements_defined: bool | None = None
    rollback_rules_defined: bool | None = None
    kill_switch_rules_defined: bool | None = None
    success_criteria_defined: bool | None = None
    failure_criteria_defined: bool | None = None
    stop_conditions_defined: bool | None = None
    broker_sandbox_session_requested: bool | None = None
    max_sessions: int | None = None
    duration_days: int | None = None
    max_simulated_loss_pct: float | None = None
    offline_mode_enforced: bool | None = None
    sandbox_mode_enforced: bool | None = None
    no_real_broker: bool | None = None
    no_api_key_read: bool | None = None
    no_http_transport: bool | None = None
    no_websocket_transport: bool | None = None
    no_socket_transport: bool | None = None
    no_external_api: bool | None = None
    no_real_order: bool | None = None
    forward_test_scope_score: int | None = None
    forward_test_duration_score: int | None = None
    allowed_session_limits_score: int | None = None
    simulated_loss_limits_score: int | None = None
    human_supervision_rules_score: int | None = None
    journal_requirements_score: int | None = None
    observability_requirements_score: int | None = None
    rollback_rules_score: int | None = None
    kill_switch_rules_score: int | None = None
    success_criteria_score: int | None = None
    failure_criteria_score: int | None = None
    stop_conditions_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperRuntimeForwardTestPlanSection:
    name: str
    score: int
    defined: bool
    risks: tuple[PaperRuntimeForwardTestPlanRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperRuntimeForwardTestPlanScore:
    overall_score: int
    forward_test_scope_score: int
    forward_test_duration_score: int
    allowed_session_limits_score: int
    simulated_loss_limits_score: int
    human_supervision_rules_score: int
    journal_requirements_score: int
    observability_requirements_score: int
    rollback_rules_score: int
    kill_switch_rules_score: int
    success_criteria_score: int
    failure_criteria_score: int
    stop_conditions_score: int


@dataclass(frozen=True)
class PaperRuntimeForwardTestPlanResult:
    state: PaperRuntimeForwardTestPlanState
    decision: PaperRuntimeForwardTestPlanDecision
    forward_test_plan_score: int
    score_breakdown: PaperRuntimeForwardTestPlanScore
    risks: tuple[PaperRuntimeForwardTestPlanRisk, ...] = ()
    forward_test_scope: PaperRuntimeForwardTestPlanSection = field(default_factory=lambda: PaperRuntimeForwardTestPlanSection("forward_test_scope", 0, False))
    forward_test_duration: PaperRuntimeForwardTestPlanSection = field(default_factory=lambda: PaperRuntimeForwardTestPlanSection("forward_test_duration", 0, False))
    allowed_session_limits: PaperRuntimeForwardTestPlanSection = field(default_factory=lambda: PaperRuntimeForwardTestPlanSection("allowed_session_limits", 0, False))
    simulated_loss_limits: PaperRuntimeForwardTestPlanSection = field(default_factory=lambda: PaperRuntimeForwardTestPlanSection("simulated_loss_limits", 0, False))
    human_supervision_rules: PaperRuntimeForwardTestPlanSection = field(default_factory=lambda: PaperRuntimeForwardTestPlanSection("human_supervision_rules", 0, False))
    journal_requirements: PaperRuntimeForwardTestPlanSection = field(default_factory=lambda: PaperRuntimeForwardTestPlanSection("journal_requirements", 0, False))
    observability_requirements: PaperRuntimeForwardTestPlanSection = field(default_factory=lambda: PaperRuntimeForwardTestPlanSection("observability_requirements", 0, False))
    rollback_rules: PaperRuntimeForwardTestPlanSection = field(default_factory=lambda: PaperRuntimeForwardTestPlanSection("rollback_rules", 0, False))
    kill_switch_rules: PaperRuntimeForwardTestPlanSection = field(default_factory=lambda: PaperRuntimeForwardTestPlanSection("kill_switch_rules", 0, False))
    success_criteria: PaperRuntimeForwardTestPlanSection = field(default_factory=lambda: PaperRuntimeForwardTestPlanSection("success_criteria", 0, False))
    failure_criteria: PaperRuntimeForwardTestPlanSection = field(default_factory=lambda: PaperRuntimeForwardTestPlanSection("failure_criteria", 0, False))
    stop_conditions: PaperRuntimeForwardTestPlanSection = field(default_factory=lambda: PaperRuntimeForwardTestPlanSection("stop_conditions", 0, False))
    recommendations: tuple[PaperRuntimeForwardTestPlanRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
