"""Models for the deterministic AGIcore controlled simulation offline runner."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ControlledSimulationOfflineRunnerState(StrEnum):
    NOT_READY = "NOT_READY"
    RUNNER_INPUT_INVALID = "RUNNER_INPUT_INVALID"
    RUNNER_BLOCKED = "RUNNER_BLOCKED"
    RUNNER_COMPLETED_WITH_WARNINGS = "RUNNER_COMPLETED_WITH_WARNINGS"
    RUNNER_COMPLETED = "RUNNER_COMPLETED"
    READY_FOR_CONTROLLED_SIMULATION_RESULT_REPORT = "READY_FOR_CONTROLLED_SIMULATION_RESULT_REPORT"


class ControlledSimulationOfflineRunnerDecision(StrEnum):
    BLOCK_CONTROLLED_SIMULATION_RUNNER = "BLOCK_CONTROLLED_SIMULATION_RUNNER"
    REQUIRE_REVIEW_PRECHECK_FIXES = "REQUIRE_REVIEW_PRECHECK_FIXES"
    REQUIRE_SCENARIO_FIXES = "REQUIRE_SCENARIO_FIXES"
    REQUIRE_SIGNAL_FIXES = "REQUIRE_SIGNAL_FIXES"
    REQUIRE_RISK_LIMIT_FIXES = "REQUIRE_RISK_LIMIT_FIXES"
    REQUIRE_METRIC_FIXES = "REQUIRE_METRIC_FIXES"
    APPROVE_CONTROLLED_SIMULATION_OFFLINE_RUNNER = "APPROVE_CONTROLLED_SIMULATION_OFFLINE_RUNNER"


class ControlledSimulationOfflineRunnerRisk(StrEnum):
    REVIEW_PRECHECK_NOT_APPROVED = "REVIEW_PRECHECK_NOT_APPROVED"
    OFFLINE_SCENARIO_EMPTY = "OFFLINE_SCENARIO_EMPTY"
    SYNTHETIC_MARKET_PATH_INVALID = "SYNTHETIC_MARKET_PATH_INVALID"
    SIGNAL_SEQUENCE_INVALID = "SIGNAL_SEQUENCE_INVALID"
    RISK_LIMITS_MISSING = "RISK_LIMITS_MISSING"
    STOP_CONDITIONS_MISSING = "STOP_CONDITIONS_MISSING"
    EQUITY_CURVE_INVALID = "EQUITY_CURVE_INVALID"
    PNL_COMPUTATION_INVALID = "PNL_COMPUTATION_INVALID"
    DRAWDOWN_LIMIT_BREACHED = "DRAWDOWN_LIMIT_BREACHED"
    LOSS_LIMIT_BREACHED = "LOSS_LIMIT_BREACHED"
    UNEXPECTED_OPEN_POSITION = "UNEXPECTED_OPEN_POSITION"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_RESULT_REPORT = "PREMATURE_RESULT_REPORT"


class ControlledSimulationOfflineRunnerRecommendation(StrEnum):
    HOLD_CONTROLLED_SIMULATION_RESULT_REPORT = "HOLD_CONTROLLED_SIMULATION_RESULT_REPORT"
    APPROVE_REVIEW_PRECHECK_FIRST = "APPROVE_REVIEW_PRECHECK_FIRST"
    PROVIDE_SYNTHETIC_SCENARIO = "PROVIDE_SYNTHETIC_SCENARIO"
    FIX_SYNTHETIC_MARKET_PATH = "FIX_SYNTHETIC_MARKET_PATH"
    FIX_SIGNAL_SEQUENCE = "FIX_SIGNAL_SEQUENCE"
    DEFINE_RISK_LIMITS = "DEFINE_RISK_LIMITS"
    DEFINE_STOP_CONDITIONS = "DEFINE_STOP_CONDITIONS"
    REBUILD_EQUITY_CURVE = "REBUILD_EQUITY_CURVE"
    RECHECK_PNL_COMPUTATION = "RECHECK_PNL_COMPUTATION"
    REDUCE_DRAWDOWN_EXPOSURE = "REDUCE_DRAWDOWN_EXPOSURE"
    REDUCE_LOSS_EXPOSURE = "REDUCE_LOSS_EXPOSURE"
    CLOSE_FINAL_POSITION = "CLOSE_FINAL_POSITION"
    RESTORE_OFFLINE_REAL_EXECUTION_BOUNDARIES = "RESTORE_OFFLINE_REAL_EXECUTION_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_CONTROLLED_SIMULATION_RESULT_REPORT = "DELAY_CONTROLLED_SIMULATION_RESULT_REPORT"
    RUN_CONTROLLED_SIMULATION_OFFLINE_RUNNER_SUITE = "RUN_CONTROLLED_SIMULATION_OFFLINE_RUNNER_SUITE"
    APPROVE_CONTROLLED_SIMULATION_RESULT_REPORT = "APPROVE_CONTROLLED_SIMULATION_RESULT_REPORT"


@dataclass(frozen=True)
class OfflineSyntheticMarketBar:
    step: int
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0
    timestamp: str = ""


@dataclass(frozen=True)
class OfflineSignalEvent:
    step: int
    symbol: str
    action: str
    quantity: float = 1.0
    confidence: float = 1.0
    reason: str = ""


@dataclass(frozen=True)
class OfflineSimulatedDecision:
    step: int
    symbol: str
    action: str
    quantity: float
    reference_price: float
    accepted: bool
    reason: str = ""


@dataclass(frozen=True)
class OfflineSimulatedFill:
    step: int
    symbol: str
    side: str
    quantity: float
    price: float
    gross_value: float
    commission: float
    slippage: float
    realized_pnl: float
    status: str
    reason: str = ""


@dataclass(frozen=True)
class OfflinePositionState:
    symbol: str
    quantity: float
    average_price: float
    cash: float
    realized_pnl: float
    unrealized_pnl: float
    equity: float
    closed_trade_pnls: tuple[float, ...] = ()


@dataclass(frozen=True)
class OfflineEquityPoint:
    step: int
    timestamp: str
    cash: float
    position_value: float
    equity: float
    realized_pnl: float
    unrealized_pnl: float
    drawdown: float
    drawdown_fraction: float


@dataclass(frozen=True)
class OfflineSimulationStepLog:
    step: int
    symbol: str
    price: float
    signal_action: str
    decision_action: str
    fill_status: str
    position_quantity: float
    equity: float
    risks: tuple[ControlledSimulationOfflineRunnerRisk, ...] = ()
    message: str = ""


@dataclass(frozen=True)
class OfflineSimulationMetrics:
    initial_equity: float
    final_equity: float
    total_pnl: float
    realized_pnl: float
    unrealized_pnl: float
    max_drawdown: float
    max_drawdown_fraction: float
    trade_count: int
    winning_trade_count: int
    losing_trade_count: int
    win_rate: float
    profit_factor: float
    expectancy: float


@dataclass(frozen=True)
class OfflineStopConditionResult:
    triggered: bool
    risks: tuple[ControlledSimulationOfflineRunnerRisk, ...] = ()
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class ControlledSimulationOfflineRunnerScore:
    overall_score: int
    review_precheck_score: int
    scenario_score: int
    signal_score: int
    risk_limit_score: int
    metric_score: int
    boundary_score: int


@dataclass(frozen=True)
class ControlledSimulationOfflineRunnerInput:
    controlled_simulation_review_precheck: Any = None
    paper_broker_sandbox_dry_run_controlled_simulation_plan: Any = None
    paper_broker_sandbox_dry_run_execution_authorization_gate: Any = None
    paper_broker_sandbox_dry_run_execution_review: Any = None
    paper_broker_sandbox_dry_run_pre_execution_check: Any = None
    paper_broker_sandbox_dry_run_review: Any = None
    paper_broker_sandbox_dry_run_plan: Any = None
    paper_runtime_forward_test_plan: Any = None
    supervised_paper_runtime_trial: Any = None
    official_paper_validation_report: Any = None
    paper_runtime_validation: Any = None
    paper_trading_runtime: Any = None
    observability_verification: Any = None
    rollback_verification: Any = None
    kill_switch_verification: Any = None
    human_validated_paper_session: Any = None
    supervised_paper_session: Any = None
    scenario_id: str = "controlled-simulation-offline"
    symbol: str = "SIM"
    initial_equity: float = 100_000.0
    synthetic_market_path: tuple[OfflineSyntheticMarketBar | dict[str, Any], ...] | None = None
    signal_sequence: tuple[OfflineSignalEvent | dict[str, Any], ...] | None = None
    max_steps: int | None = 100
    max_order_quantity: float | None = 10.0
    max_position_quantity: float | None = 10.0
    max_drawdown_fraction: float | None = 0.20
    max_loss_amount: float | None = 5_000.0
    commission_per_fill: float = 0.0
    slippage_per_unit: float = 0.0
    require_flat_final_position: bool = True
    stop_conditions_required: bool = True
    review_precheck_approved: bool | None = None
    offline_mode_enforced: bool | None = True
    sandbox_mode_enforced: bool | None = True
    no_real_broker: bool | None = True
    no_alpaca_real: bool | None = True
    no_api_key_read: bool | None = True
    no_http_transport: bool | None = True
    no_websocket_transport: bool | None = True
    no_socket_transport: bool | None = True
    no_external_api: bool | None = True
    no_external_ml: bool | None = True
    no_external_llm: bool | None = True
    no_live_execution: bool | None = True
    no_real_order: bool | None = True
    no_real_account_access: bool | None = True
    synthetic_data_only: bool | None = True
    in_memory_only: bool | None = True
    data_access_requested: bool | None = False
    real_execution_requested: bool | None = False
    result_report_requested: bool | None = False
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class ControlledSimulationOfflineRunnerResult:
    state: ControlledSimulationOfflineRunnerState
    decision: ControlledSimulationOfflineRunnerDecision
    runner_score: int
    score_breakdown: ControlledSimulationOfflineRunnerScore
    risks: tuple[ControlledSimulationOfflineRunnerRisk, ...] = ()
    recommendations: tuple[ControlledSimulationOfflineRunnerRecommendation, ...] = ()
    market_path: tuple[OfflineSyntheticMarketBar, ...] = ()
    signal_sequence: tuple[OfflineSignalEvent, ...] = ()
    decisions: tuple[OfflineSimulatedDecision, ...] = ()
    fills: tuple[OfflineSimulatedFill, ...] = ()
    final_position: OfflinePositionState = field(
        default_factory=lambda: OfflinePositionState("", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    )
    equity_curve: tuple[OfflineEquityPoint, ...] = ()
    step_logs: tuple[OfflineSimulationStepLog, ...] = ()
    metrics: OfflineSimulationMetrics = field(
        default_factory=lambda: OfflineSimulationMetrics(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0, 0.0, 0.0, 0.0)
    )
    stop_conditions: OfflineStopConditionResult = field(default_factory=OfflineStopConditionResult)
    offline_only: bool = True
    summary: str = ""
