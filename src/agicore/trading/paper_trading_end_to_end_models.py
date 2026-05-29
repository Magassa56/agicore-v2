"""Models for offline AGIcore paper trading end-to-end readiness."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperTradingEndToEndState(StrEnum):
    NOT_READY = "NOT_READY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    PARTIALLY_READY = "PARTIALLY_READY"
    END_TO_END_READY = "END_TO_END_READY"
    READY_FOR_PAPER_DRY_RUN = "READY_FOR_PAPER_DRY_RUN"


class PaperTradingEndToEndRisk(StrEnum):
    SIGNAL_PIPELINE_FAILURE = "SIGNAL_PIPELINE_FAILURE"
    DECISION_PIPELINE_FAILURE = "DECISION_PIPELINE_FAILURE"
    SAFETY_GATE_FAILURE = "SAFETY_GATE_FAILURE"
    ADAPTER_PIPELINE_FAILURE = "ADAPTER_PIPELINE_FAILURE"
    ORDER_PIPELINE_FAILURE = "ORDER_PIPELINE_FAILURE"
    POSITION_PIPELINE_FAILURE = "POSITION_PIPELINE_FAILURE"
    JOURNAL_PIPELINE_FAILURE = "JOURNAL_PIPELINE_FAILURE"
    OBSERVABILITY_FAILURE = "OBSERVABILITY_FAILURE"
    STATE_DRIFT_RISK = "STATE_DRIFT_RISK"
    END_TO_END_INCONSISTENCY = "END_TO_END_INCONSISTENCY"


class PaperTradingEndToEndRecommendation(StrEnum):
    HOLD_PAPER_DRY_RUN_APPROVAL = "HOLD_PAPER_DRY_RUN_APPROVAL"
    REPAIR_SIGNAL_PIPELINE = "REPAIR_SIGNAL_PIPELINE"
    REPAIR_DECISION_PIPELINE = "REPAIR_DECISION_PIPELINE"
    VERIFY_SAFETY_GATE = "VERIFY_SAFETY_GATE"
    REPAIR_ADAPTER_PIPELINE = "REPAIR_ADAPTER_PIPELINE"
    REPAIR_ORDER_PIPELINE = "REPAIR_ORDER_PIPELINE"
    REPAIR_POSITION_PIPELINE = "REPAIR_POSITION_PIPELINE"
    COMPLETE_PAPER_JOURNAL = "COMPLETE_PAPER_JOURNAL"
    RESTORE_OBSERVABILITY = "RESTORE_OBSERVABILITY"
    LOCK_STATE_DETERMINISM = "LOCK_STATE_DETERMINISM"
    RECONCILE_END_TO_END_FLOW = "RECONCILE_END_TO_END_FLOW"
    RUN_END_TO_END_READINESS_SUITE = "RUN_END_TO_END_READINESS_SUITE"
    APPROVE_PAPER_DRY_RUN_AFTER_MANUAL_REVIEW = "APPROVE_PAPER_DRY_RUN_AFTER_MANUAL_REVIEW"


@dataclass(frozen=True)
class PaperTradingEndToEndInput:
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
    signal_input_available: bool | None = None
    signal_validation_available: bool | None = None
    signal_context_attached: bool | None = None
    signal_to_decision_linked: bool | None = None
    decision_pipeline_available: bool | None = None
    decision_context_scored: bool | None = None
    decision_output_deterministic: bool | None = None
    decision_to_safety_linked: bool | None = None
    safety_gate_available: bool | None = None
    risk_precheck_available: bool | None = None
    kill_switch_linked: bool | None = None
    rollback_linked: bool | None = None
    safety_to_adapter_linked: bool | None = None
    paper_broker_adapter_ready: bool | None = None
    alpaca_paper_adapter_ready: bool | None = None
    adapter_offline_only: bool | None = None
    adapter_to_order_linked: bool | None = None
    paper_order_model_available: bool | None = None
    paper_order_validation_available: bool | None = None
    paper_order_translation_available: bool | None = None
    paper_order_idempotent: bool | None = None
    paper_position_model_available: bool | None = None
    paper_position_reconciliation_available: bool | None = None
    paper_position_checkpointed: bool | None = None
    position_pnl_available: bool | None = None
    paper_journal_available: bool | None = None
    paper_journal_records_orders: bool | None = None
    paper_journal_records_positions: bool | None = None
    paper_journal_exports_audit: bool | None = None
    observability_events_available: bool | None = None
    metrics_available: bool | None = None
    critical_alerts_available: bool | None = None
    result_summary_available: bool | None = None
    end_to_end_state_reconciled: bool | None = None
    offline_mode_enforced: bool | None = None
    ready_for_paper_dry_run: bool | None = None
    signal_pipeline_score: int | None = None
    decision_pipeline_score: int | None = None
    safety_pipeline_score: int | None = None
    adapter_pipeline_score: int | None = None
    order_pipeline_score: int | None = None
    position_pipeline_score: int | None = None
    journal_pipeline_score: int | None = None
    observability_pipeline_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperTradingEndToEndReviewSection:
    name: str
    score: int
    passed: bool
    risks: tuple[PaperTradingEndToEndRisk, ...] = ()
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperTradingEndToEndGraph:
    nodes: tuple[str, ...] = ()
    edges: tuple[tuple[str, str, str], ...] = ()
    ready_edges: tuple[tuple[str, str], ...] = ()
    blocked_edges: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class PaperTradingEndToEndScore:
    overall_score: int
    signal_pipeline_score: int
    decision_pipeline_score: int
    safety_pipeline_score: int
    adapter_pipeline_score: int
    order_pipeline_score: int
    position_pipeline_score: int
    journal_pipeline_score: int
    observability_pipeline_score: int


@dataclass(frozen=True)
class PaperTradingEndToEndResult:
    state: PaperTradingEndToEndState
    end_to_end_score: int
    score_breakdown: PaperTradingEndToEndScore
    risks: tuple[PaperTradingEndToEndRisk, ...] = ()
    signal_pipeline_review: PaperTradingEndToEndReviewSection = field(
        default_factory=lambda: PaperTradingEndToEndReviewSection("signal_pipeline_review", 0, False)
    )
    decision_pipeline_review: PaperTradingEndToEndReviewSection = field(
        default_factory=lambda: PaperTradingEndToEndReviewSection("decision_pipeline_review", 0, False)
    )
    safety_pipeline_review: PaperTradingEndToEndReviewSection = field(
        default_factory=lambda: PaperTradingEndToEndReviewSection("safety_pipeline_review", 0, False)
    )
    adapter_pipeline_review: PaperTradingEndToEndReviewSection = field(
        default_factory=lambda: PaperTradingEndToEndReviewSection("adapter_pipeline_review", 0, False)
    )
    order_pipeline_review: PaperTradingEndToEndReviewSection = field(
        default_factory=lambda: PaperTradingEndToEndReviewSection("order_pipeline_review", 0, False)
    )
    position_pipeline_review: PaperTradingEndToEndReviewSection = field(
        default_factory=lambda: PaperTradingEndToEndReviewSection("position_pipeline_review", 0, False)
    )
    journal_pipeline_review: PaperTradingEndToEndReviewSection = field(
        default_factory=lambda: PaperTradingEndToEndReviewSection("journal_pipeline_review", 0, False)
    )
    observability_pipeline_review: PaperTradingEndToEndReviewSection = field(
        default_factory=lambda: PaperTradingEndToEndReviewSection("observability_pipeline_review", 0, False)
    )
    end_to_end_graph: PaperTradingEndToEndGraph = field(default_factory=PaperTradingEndToEndGraph)
    recommendations: tuple[PaperTradingEndToEndRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
