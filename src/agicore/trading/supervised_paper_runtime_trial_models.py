"""Models for the offline AGIcore Supervised Paper Runtime Trial."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class SupervisedPaperRuntimeTrialState(StrEnum):
    NOT_READY = "NOT_READY"
    TRIAL_REVIEW_REQUIRED = "TRIAL_REVIEW_REQUIRED"
    TRIAL_PARTIALLY_READY = "TRIAL_PARTIALLY_READY"
    SUPERVISED_TRIAL_READY = "SUPERVISED_TRIAL_READY"
    SUPERVISED_TRIAL_COMPLETED = "SUPERVISED_TRIAL_COMPLETED"
    READY_FOR_PAPER_RUNTIME_FORWARD_TEST_PLAN = "READY_FOR_PAPER_RUNTIME_FORWARD_TEST_PLAN"


class SupervisedPaperRuntimeTrialDecision(StrEnum):
    BLOCK_SUPERVISED_TRIAL = "BLOCK_SUPERVISED_TRIAL"
    REQUIRE_AUTHORIZATION_FIXES = "REQUIRE_AUTHORIZATION_FIXES"
    REQUIRE_SUPERVISION_FIXES = "REQUIRE_SUPERVISION_FIXES"
    REQUIRE_RUNTIME_TRIAL_FIXES = "REQUIRE_RUNTIME_TRIAL_FIXES"
    REQUIRE_SAFETY_FIXES = "REQUIRE_SAFETY_FIXES"
    REQUIRE_OBSERVABILITY_FIXES = "REQUIRE_OBSERVABILITY_FIXES"
    REQUIRE_ROLLBACK_FIXES = "REQUIRE_ROLLBACK_FIXES"
    REQUIRE_KILL_SWITCH_FIXES = "REQUIRE_KILL_SWITCH_FIXES"
    APPROVE_SUPERVISED_PAPER_RUNTIME_TRIAL = "APPROVE_SUPERVISED_PAPER_RUNTIME_TRIAL"


class SupervisedPaperRuntimeTrialRisk(StrEnum):
    TRIAL_AUTHORIZATION_MISSING = "TRIAL_AUTHORIZATION_MISSING"
    HUMAN_SUPERVISION_INACTIVE = "HUMAN_SUPERVISION_INACTIVE"
    RUNTIME_TRIAL_START_FAILURE = "RUNTIME_TRIAL_START_FAILURE"
    SESSION_INIT_FAILURE = "SESSION_INIT_FAILURE"
    RUNTIME_CYCLE_FAILURE = "RUNTIME_CYCLE_FAILURE"
    SAFETY_GATE_FAILURE = "SAFETY_GATE_FAILURE"
    PAPER_ORDER_SIMULATION_FAILURE = "PAPER_ORDER_SIMULATION_FAILURE"
    POSITION_PNL_FAILURE = "POSITION_PNL_FAILURE"
    JOURNAL_FAILURE = "JOURNAL_FAILURE"
    OBSERVABILITY_FAILURE = "OBSERVABILITY_FAILURE"
    ROLLBACK_FAILURE = "ROLLBACK_FAILURE"
    KILL_SWITCH_FAILURE = "KILL_SWITCH_FAILURE"
    HUMAN_INTERVENTION_FAILURE = "HUMAN_INTERVENTION_FAILURE"
    TRIAL_STOP_FAILURE = "TRIAL_STOP_FAILURE"
    PREMATURE_FORWARD_TEST_PLAN = "PREMATURE_FORWARD_TEST_PLAN"


class SupervisedPaperRuntimeTrialRecommendation(StrEnum):
    HOLD_FORWARD_TEST_PLAN = "HOLD_FORWARD_TEST_PLAN"
    COMPLETE_TRIAL_AUTHORIZATION = "COMPLETE_TRIAL_AUTHORIZATION"
    ACTIVATE_HUMAN_SUPERVISION = "ACTIVATE_HUMAN_SUPERVISION"
    REPAIR_RUNTIME_TRIAL_START = "REPAIR_RUNTIME_TRIAL_START"
    REPAIR_SESSION_INIT = "REPAIR_SESSION_INIT"
    REPAIR_RUNTIME_CYCLES = "REPAIR_RUNTIME_CYCLES"
    REPAIR_SAFETY_GATE = "REPAIR_SAFETY_GATE"
    REPAIR_PAPER_ORDER_SIMULATION = "REPAIR_PAPER_ORDER_SIMULATION"
    REPAIR_POSITION_PNL = "REPAIR_POSITION_PNL"
    REPAIR_JOURNAL = "REPAIR_JOURNAL"
    REPAIR_OBSERVABILITY = "REPAIR_OBSERVABILITY"
    REPAIR_ROLLBACK = "REPAIR_ROLLBACK"
    REPAIR_KILL_SWITCH = "REPAIR_KILL_SWITCH"
    REPAIR_HUMAN_INTERVENTION = "REPAIR_HUMAN_INTERVENTION"
    REPAIR_TRIAL_STOP = "REPAIR_TRIAL_STOP"
    DELAY_FORWARD_TEST_PLAN = "DELAY_FORWARD_TEST_PLAN"
    RUN_SUPERVISED_RUNTIME_TRIAL_SUITE = "RUN_SUPERVISED_RUNTIME_TRIAL_SUITE"
    APPROVE_FORWARD_TEST_PLAN_PREPARATION = "APPROVE_FORWARD_TEST_PLAN_PREPARATION"


@dataclass(frozen=True)
class SupervisedPaperRuntimeTrialInput:
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
    full_paper_session: Any = None
    observability_verification: Any = None
    rollback_verification: Any = None
    kill_switch_verification: Any = None
    human_validated_paper_session: Any = None
    supervised_paper_session: Any = None
    trial_authorized: bool | None = None
    human_supervision_active: bool | None = None
    runtime_trial_started: bool | None = None
    session_initialized: bool | None = None
    runtime_cycles_completed: bool | None = None
    safety_gate_passed: bool | None = None
    paper_order_simulated: bool | None = None
    position_pnl_updated: bool | None = None
    journal_written: bool | None = None
    observability_emitted: bool | None = None
    rollback_verified: bool | None = None
    kill_switch_verified: bool | None = None
    human_intervention_verified: bool | None = None
    runtime_trial_stopped: bool | None = None
    forward_test_plan_requested: bool | None = None
    offline_mode_enforced: bool | None = None
    sandbox_mode_enforced: bool | None = None
    no_real_broker: bool | None = None
    no_api_key_read: bool | None = None
    no_http_transport: bool | None = None
    no_websocket_transport: bool | None = None
    no_socket_transport: bool | None = None
    no_external_api: bool | None = None
    no_real_order: bool | None = None
    trial_authorization_score: int | None = None
    human_supervision_score: int | None = None
    runtime_trial_start_score: int | None = None
    session_init_score: int | None = None
    runtime_cycles_score: int | None = None
    safety_gate_score: int | None = None
    paper_order_simulation_score: int | None = None
    position_pnl_score: int | None = None
    journal_score: int | None = None
    observability_score: int | None = None
    rollback_score: int | None = None
    kill_switch_score: int | None = None
    human_intervention_score: int | None = None
    trial_stop_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class SupervisedPaperRuntimeTrialCheck:
    name: str
    score: int
    passed: bool
    risks: tuple[SupervisedPaperRuntimeTrialRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class SupervisedPaperRuntimeTrialScore:
    overall_score: int
    trial_authorization_score: int
    human_supervision_score: int
    runtime_trial_start_score: int
    session_init_score: int
    runtime_cycles_score: int
    safety_gate_score: int
    paper_order_simulation_score: int
    position_pnl_score: int
    journal_score: int
    observability_score: int
    rollback_score: int
    kill_switch_score: int
    human_intervention_score: int
    trial_stop_score: int


@dataclass(frozen=True)
class SupervisedPaperRuntimeTrialResult:
    state: SupervisedPaperRuntimeTrialState
    decision: SupervisedPaperRuntimeTrialDecision
    supervised_trial_score: int
    score_breakdown: SupervisedPaperRuntimeTrialScore
    risks: tuple[SupervisedPaperRuntimeTrialRisk, ...] = ()
    trial_authorization: SupervisedPaperRuntimeTrialCheck = field(default_factory=lambda: SupervisedPaperRuntimeTrialCheck("trial_authorization", 0, False))
    human_supervision_active: SupervisedPaperRuntimeTrialCheck = field(default_factory=lambda: SupervisedPaperRuntimeTrialCheck("human_supervision_active", 0, False))
    runtime_trial_start: SupervisedPaperRuntimeTrialCheck = field(default_factory=lambda: SupervisedPaperRuntimeTrialCheck("runtime_trial_start", 0, False))
    runtime_trial_session_init: SupervisedPaperRuntimeTrialCheck = field(default_factory=lambda: SupervisedPaperRuntimeTrialCheck("runtime_trial_session_init", 0, False))
    runtime_trial_cycles: SupervisedPaperRuntimeTrialCheck = field(default_factory=lambda: SupervisedPaperRuntimeTrialCheck("runtime_trial_cycles", 0, False))
    runtime_trial_safety_gate: SupervisedPaperRuntimeTrialCheck = field(default_factory=lambda: SupervisedPaperRuntimeTrialCheck("runtime_trial_safety_gate", 0, False))
    runtime_trial_paper_order_simulation: SupervisedPaperRuntimeTrialCheck = field(default_factory=lambda: SupervisedPaperRuntimeTrialCheck("runtime_trial_paper_order_simulation", 0, False))
    runtime_trial_position_pnl: SupervisedPaperRuntimeTrialCheck = field(default_factory=lambda: SupervisedPaperRuntimeTrialCheck("runtime_trial_position_pnl", 0, False))
    runtime_trial_journal: SupervisedPaperRuntimeTrialCheck = field(default_factory=lambda: SupervisedPaperRuntimeTrialCheck("runtime_trial_journal", 0, False))
    runtime_trial_observability: SupervisedPaperRuntimeTrialCheck = field(default_factory=lambda: SupervisedPaperRuntimeTrialCheck("runtime_trial_observability", 0, False))
    runtime_trial_rollback: SupervisedPaperRuntimeTrialCheck = field(default_factory=lambda: SupervisedPaperRuntimeTrialCheck("runtime_trial_rollback", 0, False))
    runtime_trial_kill_switch: SupervisedPaperRuntimeTrialCheck = field(default_factory=lambda: SupervisedPaperRuntimeTrialCheck("runtime_trial_kill_switch", 0, False))
    runtime_trial_human_intervention: SupervisedPaperRuntimeTrialCheck = field(default_factory=lambda: SupervisedPaperRuntimeTrialCheck("runtime_trial_human_intervention", 0, False))
    runtime_trial_stop: SupervisedPaperRuntimeTrialCheck = field(default_factory=lambda: SupervisedPaperRuntimeTrialCheck("runtime_trial_stop", 0, False))
    recommendations: tuple[SupervisedPaperRuntimeTrialRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
