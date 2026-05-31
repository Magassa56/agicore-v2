"""Models for offline AGIcore Extended Paper Runtime Test."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ExtendedPaperRuntimeTestState(StrEnum):
    NOT_READY = "NOT_READY"
    EXTENDED_TEST_REVIEW_REQUIRED = "EXTENDED_TEST_REVIEW_REQUIRED"
    EXTENDED_TEST_PARTIALLY_READY = "EXTENDED_TEST_PARTIALLY_READY"
    EXTENDED_TEST_READY = "EXTENDED_TEST_READY"
    EXTENDED_TEST_COMPLETED = "EXTENDED_TEST_COMPLETED"
    READY_FOR_PAPER_RUNTIME_STABILIZATION_REVIEW = "READY_FOR_PAPER_RUNTIME_STABILIZATION_REVIEW"


class ExtendedPaperRuntimeTestDecision(StrEnum):
    EXTENDED_TEST_BLOCKED = "EXTENDED_TEST_BLOCKED"
    EXTENDED_TEST_REVIEW_REQUIRED = "EXTENDED_TEST_REVIEW_REQUIRED"
    EXTENDED_TEST_PARTIALLY_READY = "EXTENDED_TEST_PARTIALLY_READY"
    EXTENDED_TEST_READY = "EXTENDED_TEST_READY"
    EXTENDED_TEST_COMPLETED = "EXTENDED_TEST_COMPLETED"
    READY_FOR_PAPER_RUNTIME_STABILIZATION_REVIEW = "READY_FOR_PAPER_RUNTIME_STABILIZATION_REVIEW"


class ExtendedPaperRuntimeTestRisk(StrEnum):
    NOMINAL_SCENARIO_FAILURE = "NOMINAL_SCENARIO_FAILURE"
    SAFETY_GATE_BLOCK_FAILURE = "SAFETY_GATE_BLOCK_FAILURE"
    ROLLBACK_SCENARIO_FAILURE = "ROLLBACK_SCENARIO_FAILURE"
    KILL_SWITCH_SCENARIO_FAILURE = "KILL_SWITCH_SCENARIO_FAILURE"
    HUMAN_SUPERVISION_PAUSE_FAILURE = "HUMAN_SUPERVISION_PAUSE_FAILURE"
    JOURNAL_FAILURE_UNHANDLED = "JOURNAL_FAILURE_UNHANDLED"
    OBSERVABILITY_GAP_UNHANDLED = "OBSERVABILITY_GAP_UNHANDLED"
    RUNTIME_STATE_DRIFT_UNHANDLED = "RUNTIME_STATE_DRIFT_UNHANDLED"
    MULTI_SCENARIO_INCONSISTENCY = "MULTI_SCENARIO_INCONSISTENCY"
    EXTENDED_TEST_NOT_REPEATABLE = "EXTENDED_TEST_NOT_REPEATABLE"
    RUNTIME_STABILITY_RISK = "RUNTIME_STABILITY_RISK"


class ExtendedPaperRuntimeTestRecommendation(StrEnum):
    HOLD_STABILIZATION_REVIEW_APPROVAL = "HOLD_STABILIZATION_REVIEW_APPROVAL"
    REPAIR_NOMINAL_SCENARIO = "REPAIR_NOMINAL_SCENARIO"
    REPAIR_SAFETY_GATE_BLOCK_HANDLING = "REPAIR_SAFETY_GATE_BLOCK_HANDLING"
    REPAIR_ROLLBACK_SCENARIO = "REPAIR_ROLLBACK_SCENARIO"
    REPAIR_KILL_SWITCH_SCENARIO = "REPAIR_KILL_SWITCH_SCENARIO"
    REPAIR_HUMAN_SUPERVISION_PAUSE = "REPAIR_HUMAN_SUPERVISION_PAUSE"
    HANDLE_JOURNAL_FAILURE = "HANDLE_JOURNAL_FAILURE"
    HANDLE_OBSERVABILITY_GAP = "HANDLE_OBSERVABILITY_GAP"
    HANDLE_RUNTIME_STATE_DRIFT = "HANDLE_RUNTIME_STATE_DRIFT"
    RECONCILE_MULTI_SCENARIO_CONSISTENCY = "RECONCILE_MULTI_SCENARIO_CONSISTENCY"
    STABILIZE_REPEATABILITY = "STABILIZE_REPEATABILITY"
    REPAIR_RUNTIME_STABILITY = "REPAIR_RUNTIME_STABILITY"
    RUN_EXTENDED_PAPER_RUNTIME_TEST_SUITE = "RUN_EXTENDED_PAPER_RUNTIME_TEST_SUITE"
    APPROVE_STABILIZATION_REVIEW_AFTER_MANUAL_REVIEW = "APPROVE_STABILIZATION_REVIEW_AFTER_MANUAL_REVIEW"


@dataclass(frozen=True)
class ExtendedPaperRuntimeTestInput:
    paper_runtime_test_run: Any = None
    paper_trading_runtime: Any = None
    paper_runtime_integration_review: Any = None
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
    extended_test_requested: bool | None = None
    ready_for_stabilization_review: bool | None = None
    scenarios_repeatable: bool | None = None
    offline_mode_enforced: bool | None = None
    sandbox_mode_enforced: bool | None = None
    no_real_broker: bool | None = None
    no_api_key_read: bool | None = None
    no_http_transport: bool | None = None
    no_websocket_transport: bool | None = None
    no_socket_transport: bool | None = None
    no_external_api: bool | None = None
    no_real_order: bool | None = None
    nominal_score: int | None = None
    safety_gate_block_score: int | None = None
    rollback_score: int | None = None
    kill_switch_score: int | None = None
    human_supervision_pause_score: int | None = None
    journal_failure_score: int | None = None
    observability_gap_score: int | None = None
    runtime_state_drift_score: int | None = None
    multi_scenario_consistency_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class ExtendedRuntimeScenarioResult:
    name: str
    score: int
    passed: bool
    expected_state: str
    actual_state: str
    handled: bool
    risks: tuple[ExtendedPaperRuntimeTestRisk, ...] = ()
    runtime_result: Any = None
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ExtendedRuntimeConsistencyReview:
    score: int
    passed: bool
    risks: tuple[ExtendedPaperRuntimeTestRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ExtendedPaperRuntimeTestScore:
    overall_score: int
    nominal_score: int
    safety_gate_block_score: int
    rollback_score: int
    kill_switch_score: int
    human_supervision_pause_score: int
    journal_failure_score: int
    observability_gap_score: int
    runtime_state_drift_score: int
    multi_scenario_consistency_score: int


@dataclass(frozen=True)
class ExtendedPaperRuntimeTestResult:
    state: ExtendedPaperRuntimeTestState
    decision: ExtendedPaperRuntimeTestDecision
    extended_runtime_score: int
    score_breakdown: ExtendedPaperRuntimeTestScore
    risks: tuple[ExtendedPaperRuntimeTestRisk, ...] = ()
    nominal_scenario: ExtendedRuntimeScenarioResult = field(default_factory=lambda: ExtendedRuntimeScenarioResult("nominal", 0, False, "", "", False))
    safety_gate_block_scenario: ExtendedRuntimeScenarioResult = field(default_factory=lambda: ExtendedRuntimeScenarioResult("safety_gate_block", 0, False, "", "", False))
    rollback_scenario: ExtendedRuntimeScenarioResult = field(default_factory=lambda: ExtendedRuntimeScenarioResult("rollback", 0, False, "", "", False))
    kill_switch_scenario: ExtendedRuntimeScenarioResult = field(default_factory=lambda: ExtendedRuntimeScenarioResult("kill_switch", 0, False, "", "", False))
    human_supervision_pause_scenario: ExtendedRuntimeScenarioResult = field(default_factory=lambda: ExtendedRuntimeScenarioResult("human_supervision_pause", 0, False, "", "", False))
    journal_failure_scenario: ExtendedRuntimeScenarioResult = field(default_factory=lambda: ExtendedRuntimeScenarioResult("journal_failure", 0, False, "", "", False))
    observability_gap_scenario: ExtendedRuntimeScenarioResult = field(default_factory=lambda: ExtendedRuntimeScenarioResult("observability_gap", 0, False, "", "", False))
    runtime_state_drift_scenario: ExtendedRuntimeScenarioResult = field(default_factory=lambda: ExtendedRuntimeScenarioResult("runtime_state_drift", 0, False, "", "", False))
    consistency_review: ExtendedRuntimeConsistencyReview = field(default_factory=lambda: ExtendedRuntimeConsistencyReview(0, False))
    recommendations: tuple[ExtendedPaperRuntimeTestRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""

