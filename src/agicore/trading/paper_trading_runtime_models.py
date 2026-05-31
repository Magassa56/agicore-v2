"""Models for the offline AGIcore paper trading runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperTradingRuntimeState(StrEnum):
    NOT_STARTED = "NOT_STARTED"
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    RUNNING = "RUNNING"
    PAUSED_BY_SUPERVISION = "PAUSED_BY_SUPERVISION"
    STOPPED_BY_KILL_SWITCH = "STOPPED_BY_KILL_SWITCH"
    STOPPED_BY_ROLLBACK = "STOPPED_BY_ROLLBACK"
    COMPLETED = "COMPLETED"
    FAILED_SAFE = "FAILED_SAFE"


class PaperTradingRuntimeRisk(StrEnum):
    RUNTIME_INITIALIZATION_FAILURE = "RUNTIME_INITIALIZATION_FAILURE"
    MARKET_CYCLE_FAILURE = "MARKET_CYCLE_FAILURE"
    SIGNAL_CYCLE_FAILURE = "SIGNAL_CYCLE_FAILURE"
    DECISION_CYCLE_FAILURE = "DECISION_CYCLE_FAILURE"
    SAFETY_GATE_FAILURE = "SAFETY_GATE_FAILURE"
    PAPER_ORDER_SIMULATION_FAILURE = "PAPER_ORDER_SIMULATION_FAILURE"
    POSITION_PNL_UPDATE_FAILURE = "POSITION_PNL_UPDATE_FAILURE"
    JOURNAL_WRITE_FAILURE = "JOURNAL_WRITE_FAILURE"
    OBSERVABILITY_EMIT_FAILURE = "OBSERVABILITY_EMIT_FAILURE"
    ROLLBACK_HOOK_FAILURE = "ROLLBACK_HOOK_FAILURE"
    KILL_SWITCH_HOOK_FAILURE = "KILL_SWITCH_HOOK_FAILURE"
    HUMAN_SUPERVISION_FAILURE = "HUMAN_SUPERVISION_FAILURE"
    RUNTIME_STATE_DRIFT = "RUNTIME_STATE_DRIFT"


class PaperTradingRuntimeRecommendation(StrEnum):
    HOLD_RUNTIME_APPROVAL = "HOLD_RUNTIME_APPROVAL"
    REPAIR_RUNTIME_INITIALIZATION = "REPAIR_RUNTIME_INITIALIZATION"
    REPAIR_MARKET_CYCLE = "REPAIR_MARKET_CYCLE"
    REPAIR_SIGNAL_CYCLE = "REPAIR_SIGNAL_CYCLE"
    REPAIR_DECISION_CYCLE = "REPAIR_DECISION_CYCLE"
    REPAIR_SAFETY_GATE = "REPAIR_SAFETY_GATE"
    REPAIR_PAPER_ORDER_SIMULATION = "REPAIR_PAPER_ORDER_SIMULATION"
    REPAIR_POSITION_PNL_UPDATE = "REPAIR_POSITION_PNL_UPDATE"
    REPAIR_RUNTIME_JOURNAL = "REPAIR_RUNTIME_JOURNAL"
    REPAIR_RUNTIME_OBSERVABILITY = "REPAIR_RUNTIME_OBSERVABILITY"
    REPAIR_ROLLBACK_HOOK = "REPAIR_ROLLBACK_HOOK"
    REPAIR_KILL_SWITCH_HOOK = "REPAIR_KILL_SWITCH_HOOK"
    REPAIR_HUMAN_SUPERVISION_HOOK = "REPAIR_HUMAN_SUPERVISION_HOOK"
    RECONCILE_RUNTIME_STATE = "RECONCILE_RUNTIME_STATE"
    RUN_PAPER_RUNTIME_SUITE = "RUN_PAPER_RUNTIME_SUITE"
    APPROVE_RUNTIME_AFTER_MANUAL_REVIEW = "APPROVE_RUNTIME_AFTER_MANUAL_REVIEW"


@dataclass(frozen=True)
class PaperTradingRuntimeInput:
    paper_trading_runtime_design: Any = None
    paper_runtime_decision_review: Any = None
    paper_runtime_pre_review: Any = None
    full_paper_session: Any = None
    simulated_market_session: Any = None
    mock_alpaca_session: Any = None
    mock_connectivity_layer: Any = None
    alpaca_paper_connectivity_readiness: Any = None
    broker_paper_sandbox: Any = None
    paper_trading_end_to_end: Any = None
    paper_dry_run: Any = None
    supervised_paper_trial: Any = None
    observability_verification: Any = None
    rollback_verification: Any = None
    kill_switch_verification: Any = None
    human_validated_paper_session: Any = None
    supervised_paper_session: Any = None
    session_id: str = "paper-runtime-session"
    symbol: str = "AGICORE.PAPER"
    market_price: float | None = 100.0
    previous_price: float | None = 99.0
    quantity: float = 1.0
    initial_cash: float = 10_000.0
    initial_position: float = 0.0
    approved_by_human: bool | None = None
    operator_confirmed: bool | None = None
    session_authorized: bool | None = None
    supervision_pause_requested: bool = False
    kill_switch_triggered: bool = False
    rollback_requested: bool = False
    safety_gate_enabled: bool | None = None
    risk_limits_enforced: bool | None = None
    paper_order_not_routed: bool | None = None
    journal_enabled: bool | None = None
    observability_enabled: bool | None = None
    rollback_hook_available: bool | None = None
    kill_switch_hook_available: bool | None = None
    offline_mode_enforced: bool | None = None
    sandbox_mode_enforced: bool | None = None
    no_real_broker: bool | None = None
    no_api_key_read: bool | None = None
    no_http_transport: bool | None = None
    no_websocket_transport: bool | None = None
    no_socket_transport: bool | None = None
    no_external_api: bool | None = None
    no_real_order: bool | None = None
    force_market_failure: bool = False
    force_signal_failure: bool = False
    force_decision_failure: bool = False
    force_order_failure: bool = False
    force_position_failure: bool = False
    force_journal_failure: bool = False
    force_observability_failure: bool = False
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperTradingRuntimeStep:
    name: str
    state: PaperTradingRuntimeState
    passed: bool
    score: int
    risks: tuple[PaperTradingRuntimeRisk, ...] = ()
    events: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperRuntimeMarketSnapshot:
    symbol: str
    price: float
    previous_price: float
    event: str


@dataclass(frozen=True)
class PaperRuntimeSignal:
    symbol: str
    action: str
    confidence: float
    reason: str


@dataclass(frozen=True)
class PaperRuntimeDecision:
    symbol: str
    action: str
    quantity: float
    reason: str


@dataclass(frozen=True)
class PaperRuntimeOrder:
    order_id: str
    symbol: str
    side: str
    quantity: float
    price: float
    status: str
    routed: bool = False


@dataclass(frozen=True)
class PaperRuntimePosition:
    symbol: str
    quantity: float
    average_price: float
    cash: float
    realized_pnl: float
    unrealized_pnl: float


@dataclass(frozen=True)
class PaperTradingRuntimeReport:
    session_id: str
    state: PaperTradingRuntimeState
    score: int
    risks: tuple[PaperTradingRuntimeRisk, ...]
    events: tuple[str, ...]
    order_count: int
    journal_count: int
    observability_count: int


@dataclass(frozen=True)
class PaperTradingRuntimeResult:
    state: PaperTradingRuntimeState
    runtime_score: int
    risks: tuple[PaperTradingRuntimeRisk, ...]
    recommendations: tuple[PaperTradingRuntimeRecommendation, ...]
    session: PaperTradingRuntimeStep
    market_cycle: PaperTradingRuntimeStep
    signal_cycle: PaperTradingRuntimeStep
    decision_cycle: PaperTradingRuntimeStep
    safety_gate: PaperTradingRuntimeStep
    paper_order_simulation: PaperTradingRuntimeStep
    position_pnl_update: PaperTradingRuntimeStep
    journal: PaperTradingRuntimeStep
    observability: PaperTradingRuntimeStep
    rollback_hook: PaperTradingRuntimeStep
    kill_switch_hook: PaperTradingRuntimeStep
    human_supervision_hook: PaperTradingRuntimeStep
    stop: PaperTradingRuntimeStep
    market_snapshot: PaperRuntimeMarketSnapshot | None = None
    signal: PaperRuntimeSignal | None = None
    decision: PaperRuntimeDecision | None = None
    order: PaperRuntimeOrder | None = None
    position: PaperRuntimePosition | None = None
    journal_entries: tuple[str, ...] = ()
    observability_events: tuple[str, ...] = ()
    report: PaperTradingRuntimeReport | None = None
    offline_only: bool = True
    summary: str = ""

