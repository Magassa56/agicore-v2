"""Models for offline AGIcore Alpaca Paper adapter readiness."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class AlpacaPaperAdapterState(StrEnum):
    NOT_READY = "NOT_READY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    PARTIALLY_READY = "PARTIALLY_READY"
    ADAPTER_READY = "ADAPTER_READY"
    READY_FOR_END_TO_END_PAPER = "READY_FOR_END_TO_END_PAPER"


class AlpacaPaperAdapterRisk(StrEnum):
    ACCOUNT_MAPPING_FAILURE = "ACCOUNT_MAPPING_FAILURE"
    ORDER_MAPPING_FAILURE = "ORDER_MAPPING_FAILURE"
    POSITION_MAPPING_FAILURE = "POSITION_MAPPING_FAILURE"
    PAPER_TRANSLATION_FAILURE = "PAPER_TRANSLATION_FAILURE"
    UNSAFE_ORDER_ROUTING = "UNSAFE_ORDER_ROUTING"
    OBSERVABILITY_GAP = "OBSERVABILITY_GAP"
    SUPERVISION_BREAK = "SUPERVISION_BREAK"
    ROLLBACK_INCOMPATIBILITY = "ROLLBACK_INCOMPATIBILITY"
    PAPER_STATE_DRIFT = "PAPER_STATE_DRIFT"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"


class AlpacaPaperAdapterRecommendation(StrEnum):
    HOLD_END_TO_END_PAPER_APPROVAL = "HOLD_END_TO_END_PAPER_APPROVAL"
    FIX_ACCOUNT_MAPPING = "FIX_ACCOUNT_MAPPING"
    FIX_ORDER_MAPPING = "FIX_ORDER_MAPPING"
    FIX_POSITION_MAPPING = "FIX_POSITION_MAPPING"
    FIX_PAPER_TRANSLATION = "FIX_PAPER_TRANSLATION"
    BLOCK_UNSAFE_ORDER_ROUTING = "BLOCK_UNSAFE_ORDER_ROUTING"
    ADD_ADAPTER_OBSERVABILITY = "ADD_ADAPTER_OBSERVABILITY"
    RESTORE_SUPERVISION_CHAIN = "RESTORE_SUPERVISION_CHAIN"
    LINK_ADAPTER_ROLLBACK = "LINK_ADAPTER_ROLLBACK"
    LOCK_PAPER_STATE_DETERMINISM = "LOCK_PAPER_STATE_DETERMINISM"
    FIX_ADAPTER_CONFIGURATION = "FIX_ADAPTER_CONFIGURATION"
    RUN_ALPACA_ADAPTER_READINESS_SUITE = "RUN_ALPACA_ADAPTER_READINESS_SUITE"
    APPROVE_END_TO_END_PAPER_AFTER_MANUAL_REVIEW = (
        "APPROVE_END_TO_END_PAPER_AFTER_MANUAL_REVIEW"
    )


@dataclass(frozen=True)
class AlpacaPaperAdapterInput:
    paper_broker_adapter: Any = None
    supervised_paper_session: Any = None
    human_validated_paper_session: Any = None
    controlled_paper_run: Any = None
    paper_execution_loop_readiness: Any = None
    paper_runtime_preparation: Any = None
    account_id_mapping_defined: bool | None = None
    account_status_mapping_defined: bool | None = None
    account_equity_mapping_defined: bool | None = None
    account_buying_power_mapping_defined: bool | None = None
    account_currency_mapping_defined: bool | None = None
    order_symbol_mapping_defined: bool | None = None
    order_side_mapping_defined: bool | None = None
    order_type_mapping_defined: bool | None = None
    order_time_in_force_mapping_defined: bool | None = None
    order_qty_mapping_defined: bool | None = None
    position_symbol_mapping_defined: bool | None = None
    position_qty_mapping_defined: bool | None = None
    position_avg_entry_mapping_defined: bool | None = None
    position_market_value_mapping_defined: bool | None = None
    position_unrealized_pnl_mapping_defined: bool | None = None
    paper_order_translation_defined: bool | None = None
    paper_order_validation_defined: bool | None = None
    paper_order_idempotency_defined: bool | None = None
    paper_order_network_disabled: bool | None = None
    paper_order_routing_blocked: bool | None = None
    paper_account_translation_defined: bool | None = None
    paper_account_reconciliation_defined: bool | None = None
    paper_account_state_checkpointed: bool | None = None
    paper_position_translation_defined: bool | None = None
    paper_position_reconciliation_defined: bool | None = None
    paper_position_state_checkpointed: bool | None = None
    offline_mode_enforced: bool | None = None
    no_api_keys_required: bool | None = None
    no_http_transport: bool | None = None
    no_websocket_transport: bool | None = None
    observability_events_defined: bool | None = None
    rollback_linked: bool | None = None
    supervision_required: bool | None = None
    deterministic_mapping_required: bool | None = None
    paper_state_drift_monitoring_defined: bool | None = None
    ready_for_end_to_end_paper: bool | None = None
    account_mapping_score: int | None = None
    order_mapping_score: int | None = None
    position_mapping_score: int | None = None
    paper_order_translation_score: int | None = None
    paper_account_translation_score: int | None = None
    paper_position_translation_score: int | None = None
    adapter_safety_score: int | None = None
    observability_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class AlpacaPaperAdapterReviewSection:
    name: str
    score: int
    passed: bool
    risks: tuple[AlpacaPaperAdapterRisk, ...] = ()
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class AlpacaPaperAdapterGraph:
    nodes: tuple[str, ...] = ()
    edges: tuple[tuple[str, str, str], ...] = ()
    ready_edges: tuple[tuple[str, str], ...] = ()
    blocked_edges: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class AlpacaPaperAdapterScore:
    overall_score: int
    account_mapping_score: int
    order_mapping_score: int
    position_mapping_score: int
    paper_order_translation_score: int
    paper_account_translation_score: int
    paper_position_translation_score: int
    adapter_safety_score: int
    observability_score: int


@dataclass(frozen=True)
class AlpacaPaperAdapterResult:
    state: AlpacaPaperAdapterState
    alpaca_adapter_score: int
    score_breakdown: AlpacaPaperAdapterScore
    risks: tuple[AlpacaPaperAdapterRisk, ...] = ()
    account_mapping_review: AlpacaPaperAdapterReviewSection = field(
        default_factory=lambda: AlpacaPaperAdapterReviewSection("account_mapping_review", 0, False)
    )
    order_mapping_review: AlpacaPaperAdapterReviewSection = field(
        default_factory=lambda: AlpacaPaperAdapterReviewSection("order_mapping_review", 0, False)
    )
    position_mapping_review: AlpacaPaperAdapterReviewSection = field(
        default_factory=lambda: AlpacaPaperAdapterReviewSection("position_mapping_review", 0, False)
    )
    paper_order_translation_review: AlpacaPaperAdapterReviewSection = field(
        default_factory=lambda: AlpacaPaperAdapterReviewSection("paper_order_translation_review", 0, False)
    )
    paper_account_translation_review: AlpacaPaperAdapterReviewSection = field(
        default_factory=lambda: AlpacaPaperAdapterReviewSection("paper_account_translation_review", 0, False)
    )
    paper_position_translation_review: AlpacaPaperAdapterReviewSection = field(
        default_factory=lambda: AlpacaPaperAdapterReviewSection("paper_position_translation_review", 0, False)
    )
    adapter_graph: AlpacaPaperAdapterGraph = field(default_factory=AlpacaPaperAdapterGraph)
    recommendations: tuple[AlpacaPaperAdapterRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
