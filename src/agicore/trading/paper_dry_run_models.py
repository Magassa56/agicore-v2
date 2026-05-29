"""Models for offline AGIcore paper dry run verification."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperDryRunState(StrEnum):
    NOT_READY = "NOT_READY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    PARTIALLY_READY = "PARTIALLY_READY"
    DRY_RUN_READY = "DRY_RUN_READY"
    DRY_RUN_COMPLETED = "DRY_RUN_COMPLETED"
    READY_FOR_SUPERVISED_PAPER_TRIAL = "READY_FOR_SUPERVISED_PAPER_TRIAL"


class PaperDryRunRisk(StrEnum):
    SIGNAL_FLOW_FAILURE = "SIGNAL_FLOW_FAILURE"
    DECISION_FLOW_FAILURE = "DECISION_FLOW_FAILURE"
    SAFETY_GATE_BLOCKED = "SAFETY_GATE_BLOCKED"
    PAPER_ORDER_SIMULATION_FAILURE = "PAPER_ORDER_SIMULATION_FAILURE"
    POSITION_UPDATE_FAILURE = "POSITION_UPDATE_FAILURE"
    JOURNAL_WRITE_FAILURE = "JOURNAL_WRITE_FAILURE"
    OBSERVABILITY_EVENT_MISSING = "OBSERVABILITY_EVENT_MISSING"
    STATE_DRIFT_DETECTED = "STATE_DRIFT_DETECTED"
    DRY_RUN_NOT_REPEATABLE = "DRY_RUN_NOT_REPEATABLE"
    SAFETY_BYPASS_RISK = "SAFETY_BYPASS_RISK"


class PaperDryRunRecommendation(StrEnum):
    HOLD_SUPERVISED_TRIAL_APPROVAL = "HOLD_SUPERVISED_TRIAL_APPROVAL"
    REPAIR_SIGNAL_FLOW = "REPAIR_SIGNAL_FLOW"
    REPAIR_DECISION_FLOW = "REPAIR_DECISION_FLOW"
    UNBLOCK_SAFETY_GATE = "UNBLOCK_SAFETY_GATE"
    REPAIR_PAPER_ORDER_SIMULATION = "REPAIR_PAPER_ORDER_SIMULATION"
    REPAIR_POSITION_UPDATE = "REPAIR_POSITION_UPDATE"
    REPAIR_JOURNAL_WRITE = "REPAIR_JOURNAL_WRITE"
    RESTORE_OBSERVABILITY_EVENT = "RESTORE_OBSERVABILITY_EVENT"
    RECONCILE_DRY_RUN_STATE = "RECONCILE_DRY_RUN_STATE"
    STABILIZE_REPEATABILITY = "STABILIZE_REPEATABILITY"
    VERIFY_SAFETY_BYPASS_PREVENTION = "VERIFY_SAFETY_BYPASS_PREVENTION"
    RUN_PAPER_DRY_RUN_SUITE = "RUN_PAPER_DRY_RUN_SUITE"
    APPROVE_SUPERVISED_PAPER_TRIAL_AFTER_MANUAL_REVIEW = "APPROVE_SUPERVISED_PAPER_TRIAL_AFTER_MANUAL_REVIEW"


@dataclass(frozen=True)
class PaperDryRunInput:
    paper_trading_end_to_end: Any = None
    alpaca_paper_adapter: Any = None
    paper_broker_adapter: Any = None
    supervised_paper_session: Any = None
    human_validated_paper_session: Any = None
    controlled_paper_run: Any = None
    paper_execution_loop_readiness: Any = None
    paper_runtime_preparation: Any = None
    observability_verification: Any = None
    rollback_verification: Any = None
    kill_switch_verification: Any = None
    signal_event_available: bool | None = None
    signal_payload_valid: bool | None = None
    signal_timestamp_present: bool | None = None
    signal_flow_repeatable: bool | None = None
    decision_generated: bool | None = None
    decision_uses_signal: bool | None = None
    decision_deterministic: bool | None = None
    decision_trace_available: bool | None = None
    safety_gate_available: bool | None = None
    safety_gate_passed: bool | None = None
    safety_reason_recorded: bool | None = None
    safety_bypass_prevented: bool | None = None
    paper_order_created: bool | None = None
    paper_order_validated: bool | None = None
    paper_order_not_routed: bool | None = None
    paper_order_idempotent: bool | None = None
    position_updated: bool | None = None
    position_reconciled: bool | None = None
    position_checkpointed: bool | None = None
    pnl_computed: bool | None = None
    journal_entry_written: bool | None = None
    journal_links_order_position: bool | None = None
    journal_audit_trail_complete: bool | None = None
    journal_repeatable: bool | None = None
    observability_event_emitted: bool | None = None
    metrics_recorded: bool | None = None
    trace_recorded: bool | None = None
    result_visible: bool | None = None
    state_reconciled: bool | None = None
    dry_run_repeatable: bool | None = None
    offline_mode_enforced: bool | None = None
    dry_run_executed: bool | None = None
    ready_for_supervised_paper_trial: bool | None = None
    signal_flow_score: int | None = None
    decision_flow_score: int | None = None
    safety_gate_score: int | None = None
    paper_order_flow_score: int | None = None
    position_update_score: int | None = None
    journal_flow_score: int | None = None
    observability_flow_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperDryRunFlowResult:
    name: str
    score: int
    passed: bool
    risks: tuple[PaperDryRunRisk, ...] = ()
    events: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperDryRunTrace:
    steps: tuple[str, ...] = ()
    completed_steps: tuple[str, ...] = ()
    blocked_steps: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperDryRunScore:
    overall_score: int
    signal_flow_score: int
    decision_flow_score: int
    safety_gate_score: int
    paper_order_flow_score: int
    position_update_score: int
    journal_flow_score: int
    observability_flow_score: int


@dataclass(frozen=True)
class PaperDryRunResult:
    state: PaperDryRunState
    dry_run_score: int
    score_breakdown: PaperDryRunScore
    risks: tuple[PaperDryRunRisk, ...] = ()
    signal_flow: PaperDryRunFlowResult = field(
        default_factory=lambda: PaperDryRunFlowResult("signal_flow", 0, False)
    )
    decision_flow: PaperDryRunFlowResult = field(
        default_factory=lambda: PaperDryRunFlowResult("decision_flow", 0, False)
    )
    safety_gate_flow: PaperDryRunFlowResult = field(
        default_factory=lambda: PaperDryRunFlowResult("safety_gate_flow", 0, False)
    )
    paper_order_flow: PaperDryRunFlowResult = field(
        default_factory=lambda: PaperDryRunFlowResult("paper_order_flow", 0, False)
    )
    position_update_flow: PaperDryRunFlowResult = field(
        default_factory=lambda: PaperDryRunFlowResult("position_update_flow", 0, False)
    )
    journal_flow: PaperDryRunFlowResult = field(
        default_factory=lambda: PaperDryRunFlowResult("journal_flow", 0, False)
    )
    observability_flow: PaperDryRunFlowResult = field(
        default_factory=lambda: PaperDryRunFlowResult("observability_flow", 0, False)
    )
    dry_run_trace: PaperDryRunTrace = field(default_factory=PaperDryRunTrace)
    recommendations: tuple[PaperDryRunRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
