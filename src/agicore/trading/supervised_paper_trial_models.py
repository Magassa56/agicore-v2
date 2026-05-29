"""Models for offline AGIcore supervised paper trial verification."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class SupervisedPaperTrialState(StrEnum):
    NOT_READY = "NOT_READY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    PARTIALLY_READY = "PARTIALLY_READY"
    TRIAL_READY = "TRIAL_READY"
    TRIAL_COMPLETED = "TRIAL_COMPLETED"
    READY_FOR_BROKER_PAPER_SANDBOX = "READY_FOR_BROKER_PAPER_SANDBOX"


class SupervisedPaperTrialRisk(StrEnum):
    TRIAL_SCENARIO_MISSING = "TRIAL_SCENARIO_MISSING"
    SUPERVISION_FLOW_BROKEN = "SUPERVISION_FLOW_BROKEN"
    SAFETY_GATE_FAILURE = "SAFETY_GATE_FAILURE"
    JOURNAL_INCOMPLETE = "JOURNAL_INCOMPLETE"
    OBSERVABILITY_GAP = "OBSERVABILITY_GAP"
    ROLLBACK_PATH_UNVERIFIED = "ROLLBACK_PATH_UNVERIFIED"
    DRY_RUN_INCONSISTENCY = "DRY_RUN_INCONSISTENCY"
    PAPER_STATE_DRIFT = "PAPER_STATE_DRIFT"
    HUMAN_OVERRIDE_FAILURE = "HUMAN_OVERRIDE_FAILURE"
    TRIAL_NOT_REPEATABLE = "TRIAL_NOT_REPEATABLE"


class SupervisedPaperTrialRecommendation(StrEnum):
    HOLD_BROKER_PAPER_SANDBOX_APPROVAL = "HOLD_BROKER_PAPER_SANDBOX_APPROVAL"
    DEFINE_TRIAL_SCENARIO = "DEFINE_TRIAL_SCENARIO"
    REPAIR_SUPERVISION_FLOW = "REPAIR_SUPERVISION_FLOW"
    VERIFY_TRIAL_SAFETY_GATE = "VERIFY_TRIAL_SAFETY_GATE"
    COMPLETE_TRIAL_JOURNAL = "COMPLETE_TRIAL_JOURNAL"
    RESTORE_TRIAL_OBSERVABILITY = "RESTORE_TRIAL_OBSERVABILITY"
    VERIFY_ROLLBACK_PATH = "VERIFY_ROLLBACK_PATH"
    RECONCILE_DRY_RUN_OUTPUT = "RECONCILE_DRY_RUN_OUTPUT"
    RECONCILE_PAPER_STATE = "RECONCILE_PAPER_STATE"
    ENABLE_HUMAN_OVERRIDE = "ENABLE_HUMAN_OVERRIDE"
    STABILIZE_TRIAL_REPEATABILITY = "STABILIZE_TRIAL_REPEATABILITY"
    RUN_SUPERVISED_PAPER_TRIAL_SUITE = "RUN_SUPERVISED_PAPER_TRIAL_SUITE"
    APPROVE_BROKER_PAPER_SANDBOX_AFTER_MANUAL_REVIEW = (
        "APPROVE_BROKER_PAPER_SANDBOX_AFTER_MANUAL_REVIEW"
    )


@dataclass(frozen=True)
class SupervisedPaperTrialInput:
    paper_dry_run: Any = None
    paper_trading_end_to_end: Any = None
    alpaca_paper_adapter: Any = None
    paper_broker_adapter: Any = None
    supervised_paper_session: Any = None
    human_validated_paper_session: Any = None
    controlled_paper_run: Any = None
    paper_execution_loop_readiness: Any = None
    observability_verification: Any = None
    rollback_verification: Any = None
    kill_switch_verification: Any = None
    trial_scenario_defined: bool | None = None
    scenario_inputs_fixed: bool | None = None
    scenario_expected_outputs_defined: bool | None = None
    scenario_repeatable: bool | None = None
    human_supervisor_assigned: bool | None = None
    operator_confirmation_available: bool | None = None
    supervision_session_active: bool | None = None
    human_override_available: bool | None = None
    dry_run_completed: bool | None = None
    dry_run_output_reconciled: bool | None = None
    safety_gate_available: bool | None = None
    safety_gate_passed: bool | None = None
    kill_switch_linked: bool | None = None
    safety_bypass_blocked: bool | None = None
    journal_entry_written: bool | None = None
    journal_captures_scenario: bool | None = None
    journal_captures_decisions: bool | None = None
    final_report_available: bool | None = None
    observability_events_emitted: bool | None = None
    metrics_recorded: bool | None = None
    traces_recorded: bool | None = None
    alerts_visible: bool | None = None
    rollback_path_available: bool | None = None
    recovery_point_verified: bool | None = None
    post_rollback_state_safe: bool | None = None
    rollback_audit_recorded: bool | None = None
    paper_state_reconciled: bool | None = None
    trial_repeatable: bool | None = None
    offline_mode_enforced: bool | None = None
    trial_executed: bool | None = None
    ready_for_broker_paper_sandbox: bool | None = None
    trial_scenario_score: int | None = None
    supervised_execution_score: int | None = None
    trial_safety_gate_score: int | None = None
    trial_journal_score: int | None = None
    trial_observability_score: int | None = None
    trial_rollback_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class SupervisedPaperTrialReviewSection:
    name: str
    score: int
    passed: bool
    risks: tuple[SupervisedPaperTrialRisk, ...] = ()
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class SupervisedPaperTrialTrace:
    steps: tuple[str, ...] = ()
    completed_steps: tuple[str, ...] = ()
    blocked_steps: tuple[str, ...] = ()


@dataclass(frozen=True)
class SupervisedPaperTrialScore:
    overall_score: int
    trial_scenario_score: int
    supervised_execution_score: int
    trial_safety_gate_score: int
    trial_journal_score: int
    trial_observability_score: int
    trial_rollback_score: int


@dataclass(frozen=True)
class SupervisedPaperTrialResult:
    state: SupervisedPaperTrialState
    trial_score: int
    score_breakdown: SupervisedPaperTrialScore
    risks: tuple[SupervisedPaperTrialRisk, ...] = ()
    trial_scenario_review: SupervisedPaperTrialReviewSection = field(
        default_factory=lambda: SupervisedPaperTrialReviewSection("trial_scenario_review", 0, False)
    )
    supervised_execution_review: SupervisedPaperTrialReviewSection = field(
        default_factory=lambda: SupervisedPaperTrialReviewSection("supervised_execution_review", 0, False)
    )
    trial_safety_gate_review: SupervisedPaperTrialReviewSection = field(
        default_factory=lambda: SupervisedPaperTrialReviewSection("trial_safety_gate_review", 0, False)
    )
    trial_journal_review: SupervisedPaperTrialReviewSection = field(
        default_factory=lambda: SupervisedPaperTrialReviewSection("trial_journal_review", 0, False)
    )
    trial_observability_review: SupervisedPaperTrialReviewSection = field(
        default_factory=lambda: SupervisedPaperTrialReviewSection("trial_observability_review", 0, False)
    )
    trial_rollback_review: SupervisedPaperTrialReviewSection = field(
        default_factory=lambda: SupervisedPaperTrialReviewSection("trial_rollback_review", 0, False)
    )
    trial_trace: SupervisedPaperTrialTrace = field(default_factory=SupervisedPaperTrialTrace)
    recommendations: tuple[SupervisedPaperTrialRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
