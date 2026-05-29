"""Models for offline AGIcore paper broker adapter readiness."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperBrokerAdapterState(StrEnum):
    NOT_READY = "NOT_READY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    PARTIALLY_READY = "PARTIALLY_READY"
    ADAPTER_READY = "ADAPTER_READY"
    READY_FOR_ALPACA_PAPER_ADAPTER = "READY_FOR_ALPACA_PAPER_ADAPTER"


class PaperBrokerAdapterRisk(StrEnum):
    BROKER_INTERFACE_MISSING = "BROKER_INTERFACE_MISSING"
    ORDER_TRANSLATION_FAILURE = "ORDER_TRANSLATION_FAILURE"
    POSITION_TRANSLATION_FAILURE = "POSITION_TRANSLATION_FAILURE"
    ACCOUNT_TRANSLATION_FAILURE = "ACCOUNT_TRANSLATION_FAILURE"
    SAFETY_LAYER_MISSING = "SAFETY_LAYER_MISSING"
    OBSERVABILITY_GAP = "OBSERVABILITY_GAP"
    ROLLBACK_INCOMPATIBILITY = "ROLLBACK_INCOMPATIBILITY"
    SUPERVISION_CHAIN_BREAK = "SUPERVISION_CHAIN_BREAK"
    PAPER_DRIFT_RISK = "PAPER_DRIFT_RISK"
    ADAPTER_CONFIGURATION_ERROR = "ADAPTER_CONFIGURATION_ERROR"


class PaperBrokerAdapterRecommendation(StrEnum):
    HOLD_ALPACA_PAPER_ADAPTER_APPROVAL = "HOLD_ALPACA_PAPER_ADAPTER_APPROVAL"
    DEFINE_BROKER_INTERFACE_CONTRACT = "DEFINE_BROKER_INTERFACE_CONTRACT"
    FIX_ORDER_TRANSLATION_CONTRACT = "FIX_ORDER_TRANSLATION_CONTRACT"
    FIX_POSITION_TRANSLATION_CONTRACT = "FIX_POSITION_TRANSLATION_CONTRACT"
    FIX_ACCOUNT_TRANSLATION_CONTRACT = "FIX_ACCOUNT_TRANSLATION_CONTRACT"
    ADD_ADAPTER_SAFETY_LAYER = "ADD_ADAPTER_SAFETY_LAYER"
    ADD_ADAPTER_OBSERVABILITY = "ADD_ADAPTER_OBSERVABILITY"
    LINK_ADAPTER_ROLLBACK = "LINK_ADAPTER_ROLLBACK"
    RESTORE_SUPERVISION_CHAIN = "RESTORE_SUPERVISION_CHAIN"
    LOCK_ADAPTER_DETERMINISM = "LOCK_ADAPTER_DETERMINISM"
    FIX_ADAPTER_CONFIGURATION = "FIX_ADAPTER_CONFIGURATION"
    RUN_ADAPTER_READINESS_SUITE = "RUN_ADAPTER_READINESS_SUITE"
    APPROVE_ALPACA_PAPER_ADAPTER_AFTER_MANUAL_REVIEW = (
        "APPROVE_ALPACA_PAPER_ADAPTER_AFTER_MANUAL_REVIEW"
    )


@dataclass(frozen=True)
class PaperBrokerAdapterInput:
    supervised_paper_session: Any = None
    human_validated_paper_session: Any = None
    controlled_paper_run: Any = None
    paper_execution_loop_readiness: Any = None
    paper_runtime_preparation: Any = None
    observability_verification: Any = None
    rollback_verification: Any = None
    kill_switch_verification: Any = None
    broker_interface_defined: bool | None = None
    broker_capability_contract_defined: bool | None = None
    adapter_config_schema_defined: bool | None = None
    offline_adapter_mode_enforced: bool | None = None
    no_network_transport_configured: bool | None = None
    order_model_mapping_defined: bool | None = None
    order_side_mapping_defined: bool | None = None
    order_type_mapping_defined: bool | None = None
    order_validation_contract_defined: bool | None = None
    order_idempotency_defined: bool | None = None
    position_model_mapping_defined: bool | None = None
    position_quantity_mapping_defined: bool | None = None
    position_pnl_mapping_defined: bool | None = None
    position_reconciliation_defined: bool | None = None
    account_model_mapping_defined: bool | None = None
    buying_power_mapping_defined: bool | None = None
    equity_balance_mapping_defined: bool | None = None
    account_risk_limits_defined: bool | None = None
    safety_prechecks_required: bool | None = None
    kill_switch_linked: bool | None = None
    rollback_linked: bool | None = None
    supervision_required: bool | None = None
    observability_events_defined: bool | None = None
    deterministic_translation_required: bool | None = None
    paper_drift_monitoring_defined: bool | None = None
    ready_for_alpaca_paper_adapter: bool | None = None
    broker_interface_score: int | None = None
    order_translation_score: int | None = None
    position_translation_score: int | None = None
    account_translation_score: int | None = None
    adapter_safety_score: int | None = None
    observability_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerAdapterReviewSection:
    name: str
    score: int
    passed: bool
    risks: tuple[PaperBrokerAdapterRisk, ...] = ()
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperBrokerAdapterGraph:
    nodes: tuple[str, ...] = ()
    edges: tuple[tuple[str, str, str], ...] = ()
    ready_edges: tuple[tuple[str, str], ...] = ()
    blocked_edges: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class PaperBrokerAdapterScore:
    overall_score: int
    broker_interface_score: int
    order_translation_score: int
    position_translation_score: int
    account_translation_score: int
    adapter_safety_score: int
    observability_score: int


@dataclass(frozen=True)
class PaperBrokerAdapterResult:
    state: PaperBrokerAdapterState
    adapter_score: int
    score_breakdown: PaperBrokerAdapterScore
    risks: tuple[PaperBrokerAdapterRisk, ...] = ()
    broker_interface_review: PaperBrokerAdapterReviewSection = field(
        default_factory=lambda: PaperBrokerAdapterReviewSection("broker_interface_review", 0, False)
    )
    order_translation_review: PaperBrokerAdapterReviewSection = field(
        default_factory=lambda: PaperBrokerAdapterReviewSection("order_translation_review", 0, False)
    )
    position_translation_review: PaperBrokerAdapterReviewSection = field(
        default_factory=lambda: PaperBrokerAdapterReviewSection("position_translation_review", 0, False)
    )
    account_translation_review: PaperBrokerAdapterReviewSection = field(
        default_factory=lambda: PaperBrokerAdapterReviewSection("account_translation_review", 0, False)
    )
    adapter_safety_review: PaperBrokerAdapterReviewSection = field(
        default_factory=lambda: PaperBrokerAdapterReviewSection("adapter_safety_review", 0, False)
    )
    adapter_graph: PaperBrokerAdapterGraph = field(default_factory=PaperBrokerAdapterGraph)
    recommendations: tuple[PaperBrokerAdapterRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
