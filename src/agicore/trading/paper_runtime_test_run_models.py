"""Models for offline AGIcore Paper Runtime Test Run."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperRuntimeTestRunState(StrEnum):
    NOT_READY = "NOT_READY"
    TEST_REVIEW_REQUIRED = "TEST_REVIEW_REQUIRED"
    TEST_PARTIALLY_READY = "TEST_PARTIALLY_READY"
    TEST_RUN_READY = "TEST_RUN_READY"
    TEST_RUN_COMPLETED = "TEST_RUN_COMPLETED"
    READY_FOR_EXTENDED_PAPER_RUNTIME_TEST = "READY_FOR_EXTENDED_PAPER_RUNTIME_TEST"


class PaperRuntimeTestRunDecision(StrEnum):
    TEST_RUN_BLOCKED = "TEST_RUN_BLOCKED"
    TEST_RUN_REVIEW_REQUIRED = "TEST_RUN_REVIEW_REQUIRED"
    TEST_RUN_PARTIALLY_READY = "TEST_RUN_PARTIALLY_READY"
    TEST_RUN_READY = "TEST_RUN_READY"
    TEST_RUN_COMPLETED = "TEST_RUN_COMPLETED"
    READY_FOR_EXTENDED_PAPER_RUNTIME_TEST = "READY_FOR_EXTENDED_PAPER_RUNTIME_TEST"


class PaperRuntimeTestRunRisk(StrEnum):
    RUNTIME_START_FAILURE = "RUNTIME_START_FAILURE"
    SESSION_INIT_FAILURE = "SESSION_INIT_FAILURE"
    MARKET_CYCLE_FAILURE = "MARKET_CYCLE_FAILURE"
    SIGNAL_CYCLE_FAILURE = "SIGNAL_CYCLE_FAILURE"
    DECISION_CYCLE_FAILURE = "DECISION_CYCLE_FAILURE"
    SAFETY_GATE_FAILURE = "SAFETY_GATE_FAILURE"
    PAPER_ORDER_SIMULATION_FAILURE = "PAPER_ORDER_SIMULATION_FAILURE"
    POSITION_PNL_UPDATE_FAILURE = "POSITION_PNL_UPDATE_FAILURE"
    JOURNAL_OUTPUT_FAILURE = "JOURNAL_OUTPUT_FAILURE"
    OBSERVABILITY_OUTPUT_FAILURE = "OBSERVABILITY_OUTPUT_FAILURE"
    ROLLBACK_HOOK_FAILURE = "ROLLBACK_HOOK_FAILURE"
    KILL_SWITCH_HOOK_FAILURE = "KILL_SWITCH_HOOK_FAILURE"
    HUMAN_SUPERVISION_HOOK_FAILURE = "HUMAN_SUPERVISION_HOOK_FAILURE"
    RUNTIME_STOP_FAILURE = "RUNTIME_STOP_FAILURE"
    TEST_RUN_STATE_DRIFT = "TEST_RUN_STATE_DRIFT"


class PaperRuntimeTestRunRecommendation(StrEnum):
    HOLD_EXTENDED_TEST_APPROVAL = "HOLD_EXTENDED_TEST_APPROVAL"
    REPAIR_RUNTIME_START = "REPAIR_RUNTIME_START"
    REPAIR_SESSION_INIT = "REPAIR_SESSION_INIT"
    REPAIR_MARKET_CYCLE = "REPAIR_MARKET_CYCLE"
    REPAIR_SIGNAL_CYCLE = "REPAIR_SIGNAL_CYCLE"
    REPAIR_DECISION_CYCLE = "REPAIR_DECISION_CYCLE"
    REPAIR_SAFETY_GATE = "REPAIR_SAFETY_GATE"
    REPAIR_PAPER_ORDER_SIMULATION = "REPAIR_PAPER_ORDER_SIMULATION"
    REPAIR_POSITION_PNL_UPDATE = "REPAIR_POSITION_PNL_UPDATE"
    REPAIR_JOURNAL_OUTPUT = "REPAIR_JOURNAL_OUTPUT"
    REPAIR_OBSERVABILITY_OUTPUT = "REPAIR_OBSERVABILITY_OUTPUT"
    REPAIR_ROLLBACK_HOOK = "REPAIR_ROLLBACK_HOOK"
    REPAIR_KILL_SWITCH_HOOK = "REPAIR_KILL_SWITCH_HOOK"
    REPAIR_HUMAN_SUPERVISION_HOOK = "REPAIR_HUMAN_SUPERVISION_HOOK"
    REPAIR_RUNTIME_STOP = "REPAIR_RUNTIME_STOP"
    RECONCILE_TEST_RUN_STATE = "RECONCILE_TEST_RUN_STATE"
    RUN_PAPER_RUNTIME_TEST_RUN_SUITE = "RUN_PAPER_RUNTIME_TEST_RUN_SUITE"
    APPROVE_EXTENDED_TEST_AFTER_MANUAL_REVIEW = "APPROVE_EXTENDED_TEST_AFTER_MANUAL_REVIEW"


@dataclass(frozen=True)
class PaperRuntimeTestRunInput:
    paper_runtime_integration_review: Any = None
    paper_trading_runtime: Any = None
    paper_trading_runtime_design: Any = None
    paper_runtime_decision_review: Any = None
    full_paper_session: Any = None
    simulated_market_session: Any = None
    mock_alpaca_session: Any = None
    mock_connectivity_layer: Any = None
    observability_verification: Any = None
    rollback_verification: Any = None
    kill_switch_verification: Any = None
    human_validated_paper_session: Any = None
    supervised_paper_session: Any = None
    runtime_input: Any = None
    test_run_requested: bool | None = None
    ready_for_extended_test: bool | None = None
    offline_mode_enforced: bool | None = None
    sandbox_mode_enforced: bool | None = None
    no_real_broker: bool | None = None
    no_api_key_read: bool | None = None
    no_http_transport: bool | None = None
    no_websocket_transport: bool | None = None
    no_socket_transport: bool | None = None
    no_external_api: bool | None = None
    no_real_order: bool | None = None
    runtime_start_score: int | None = None
    session_init_score: int | None = None
    market_cycle_score: int | None = None
    signal_cycle_score: int | None = None
    decision_cycle_score: int | None = None
    safety_gate_score: int | None = None
    paper_order_simulation_score: int | None = None
    position_pnl_update_score: int | None = None
    journal_output_score: int | None = None
    observability_output_score: int | None = None
    rollback_hook_score: int | None = None
    kill_switch_hook_score: int | None = None
    human_supervision_hook_score: int | None = None
    runtime_stop_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperRuntimeTestCheck:
    name: str
    score: int
    passed: bool
    risks: tuple[PaperRuntimeTestRunRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperRuntimeTestRunScore:
    overall_score: int
    runtime_start_score: int
    session_init_score: int
    market_cycle_score: int
    signal_cycle_score: int
    decision_cycle_score: int
    safety_gate_score: int
    paper_order_simulation_score: int
    position_pnl_update_score: int
    journal_output_score: int
    observability_output_score: int
    rollback_hook_score: int
    kill_switch_hook_score: int
    human_supervision_hook_score: int
    runtime_stop_score: int


@dataclass(frozen=True)
class PaperRuntimeTestScenario:
    runtime_result: Any
    checks: tuple[PaperRuntimeTestCheck, ...]
    offline_only: bool


@dataclass(frozen=True)
class PaperRuntimeTestRunResult:
    state: PaperRuntimeTestRunState
    decision: PaperRuntimeTestRunDecision
    test_run_score: int
    score_breakdown: PaperRuntimeTestRunScore
    risks: tuple[PaperRuntimeTestRunRisk, ...] = ()
    runtime_start: PaperRuntimeTestCheck = field(default_factory=lambda: PaperRuntimeTestCheck("runtime_start", 0, False))
    session_init: PaperRuntimeTestCheck = field(default_factory=lambda: PaperRuntimeTestCheck("session_init", 0, False))
    market_cycle: PaperRuntimeTestCheck = field(default_factory=lambda: PaperRuntimeTestCheck("market_cycle", 0, False))
    signal_cycle: PaperRuntimeTestCheck = field(default_factory=lambda: PaperRuntimeTestCheck("signal_cycle", 0, False))
    decision_cycle: PaperRuntimeTestCheck = field(default_factory=lambda: PaperRuntimeTestCheck("decision_cycle", 0, False))
    safety_gate: PaperRuntimeTestCheck = field(default_factory=lambda: PaperRuntimeTestCheck("safety_gate", 0, False))
    paper_order_simulation: PaperRuntimeTestCheck = field(default_factory=lambda: PaperRuntimeTestCheck("paper_order_simulation", 0, False))
    position_pnl_update: PaperRuntimeTestCheck = field(default_factory=lambda: PaperRuntimeTestCheck("position_pnl_update", 0, False))
    journal_output: PaperRuntimeTestCheck = field(default_factory=lambda: PaperRuntimeTestCheck("journal_output", 0, False))
    observability_output: PaperRuntimeTestCheck = field(default_factory=lambda: PaperRuntimeTestCheck("observability_output", 0, False))
    rollback_hook: PaperRuntimeTestCheck = field(default_factory=lambda: PaperRuntimeTestCheck("rollback_hook", 0, False))
    kill_switch_hook: PaperRuntimeTestCheck = field(default_factory=lambda: PaperRuntimeTestCheck("kill_switch_hook", 0, False))
    human_supervision_hook: PaperRuntimeTestCheck = field(default_factory=lambda: PaperRuntimeTestCheck("human_supervision_hook", 0, False))
    runtime_stop: PaperRuntimeTestCheck = field(default_factory=lambda: PaperRuntimeTestCheck("runtime_stop", 0, False))
    runtime_result: Any = None
    recommendations: tuple[PaperRuntimeTestRunRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""

