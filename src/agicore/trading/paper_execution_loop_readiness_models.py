"""Models for offline AGIcore paper execution loop readiness."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperExecutionLoopReadinessState(StrEnum):
    NOT_READY = "NOT_READY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    PARTIALLY_READY = "PARTIALLY_READY"
    PAPER_LOOP_READY = "PAPER_LOOP_READY"
    READY_FOR_CONTROLLED_PAPER_RUN = "READY_FOR_CONTROLLED_PAPER_RUN"


class PaperExecutionLoopRisk(StrEnum):
    SIGNAL_INPUT_MISSING = "SIGNAL_INPUT_MISSING"
    DECISION_PIPELINE_INCOMPLETE = "DECISION_PIPELINE_INCOMPLETE"
    SAFETY_GATE_UNVERIFIED = "SAFETY_GATE_UNVERIFIED"
    SIMULATED_EXECUTION_UNREADY = "SIMULATED_EXECUTION_UNREADY"
    PAPER_JOURNAL_MISSING = "PAPER_JOURNAL_MISSING"
    RISK_ENGINE_NOT_CONNECTED = "RISK_ENGINE_NOT_CONNECTED"
    OBSERVABILITY_BLIND_SPOT = "OBSERVABILITY_BLIND_SPOT"
    KILL_SWITCH_NOT_LINKED = "KILL_SWITCH_NOT_LINKED"
    ROLLBACK_NOT_LINKED = "ROLLBACK_NOT_LINKED"
    PAPER_LOOP_STATE_CORRUPTION_RISK = "PAPER_LOOP_STATE_CORRUPTION_RISK"


class PaperExecutionLoopRecommendation(StrEnum):
    HOLD_PAPER_LOOP_APPROVAL = "HOLD_PAPER_LOOP_APPROVAL"
    CONNECT_SIGNAL_INPUTS = "CONNECT_SIGNAL_INPUTS"
    COMPLETE_DECISION_PIPELINE = "COMPLETE_DECISION_PIPELINE"
    VERIFY_SAFETY_GATE = "VERIFY_SAFETY_GATE"
    PREPARE_SIMULATED_EXECUTION = "PREPARE_SIMULATED_EXECUTION"
    ENABLE_PAPER_JOURNAL = "ENABLE_PAPER_JOURNAL"
    CONNECT_RISK_ENGINE = "CONNECT_RISK_ENGINE"
    ADD_LOOP_OBSERVABILITY = "ADD_LOOP_OBSERVABILITY"
    LINK_KILL_SWITCH = "LINK_KILL_SWITCH"
    LINK_ROLLBACK = "LINK_ROLLBACK"
    PROTECT_PAPER_LOOP_STATE = "PROTECT_PAPER_LOOP_STATE"
    RUN_PAPER_LOOP_READINESS_SUITE = "RUN_PAPER_LOOP_READINESS_SUITE"
    APPROVE_CONTROLLED_PAPER_RUN_AFTER_MANUAL_REVIEW = (
        "APPROVE_CONTROLLED_PAPER_RUN_AFTER_MANUAL_REVIEW"
    )


@dataclass(frozen=True)
class PaperExecutionLoopReadinessInput:
    paper_runtime_preparation: Any = None
    observability_verification: Any = None
    rollback_verification: Any = None
    kill_switch_verification: Any = None
    runtime_isolation_review: Any = None
    sandbox_readiness_audit: Any = None
    stable_review: Any = None
    signal_source_available: bool | None = None
    context_signal_available: bool | None = None
    strategy_signal_available: bool | None = None
    signal_validation_enabled: bool | None = None
    semi_auto_decision_ready: bool | None = None
    context_scoring_connected: bool | None = None
    strategy_dna_connected: bool | None = None
    decision_output_deterministic: bool | None = None
    safety_prechecks_enabled: bool | None = None
    risk_engine_connected: bool | None = None
    kill_switch_linked: bool | None = None
    rollback_linked: bool | None = None
    simulated_adapter_available: bool | None = None
    simulated_order_path_verified: bool | None = None
    real_broker_blocked: bool | None = None
    execution_events_emitted: bool | None = None
    paper_journal_available: bool | None = None
    paper_trade_events_recorded: bool | None = None
    paper_pnl_recorded: bool | None = None
    paper_audit_export_available: bool | None = None
    loop_observability_connected: bool | None = None
    paper_loop_state_checkpointed: bool | None = None
    ready_for_controlled_paper_run: bool | None = None
    signal_input_score: int | None = None
    decision_pipeline_score: int | None = None
    safety_gate_score: int | None = None
    simulated_execution_score: int | None = None
    paper_journal_score: int | None = None
    loop_observability_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperExecutionLoopReviewSection:
    name: str
    score: int
    passed: bool
    risks: tuple[PaperExecutionLoopRisk, ...] = ()
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperExecutionLoopGraph:
    nodes: tuple[str, ...] = ()
    edges: tuple[tuple[str, str, str], ...] = ()
    ready_edges: tuple[tuple[str, str], ...] = ()
    blocked_edges: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class PaperExecutionLoopScore:
    overall_score: int
    signal_input_score: int
    decision_pipeline_score: int
    safety_gate_score: int
    simulated_execution_score: int
    paper_journal_score: int
    loop_observability_score: int


@dataclass(frozen=True)
class PaperExecutionLoopReadinessResult:
    state: PaperExecutionLoopReadinessState
    paper_loop_score: int
    score_breakdown: PaperExecutionLoopScore
    blockers: tuple[PaperExecutionLoopRisk, ...] = ()
    signal_input_review: PaperExecutionLoopReviewSection = field(
        default_factory=lambda: PaperExecutionLoopReviewSection("signal_input_review", 0, False)
    )
    decision_pipeline_review: PaperExecutionLoopReviewSection = field(
        default_factory=lambda: PaperExecutionLoopReviewSection("decision_pipeline_review", 0, False)
    )
    safety_gate_review: PaperExecutionLoopReviewSection = field(
        default_factory=lambda: PaperExecutionLoopReviewSection("safety_gate_review", 0, False)
    )
    simulated_execution_review: PaperExecutionLoopReviewSection = field(
        default_factory=lambda: PaperExecutionLoopReviewSection("simulated_execution_review", 0, False)
    )
    paper_journal_review: PaperExecutionLoopReviewSection = field(
        default_factory=lambda: PaperExecutionLoopReviewSection("paper_journal_review", 0, False)
    )
    paper_loop_graph: PaperExecutionLoopGraph = field(default_factory=PaperExecutionLoopGraph)
    recommendations: tuple[PaperExecutionLoopRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
