"""Models for the AGIcore offline risk metrics engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class RiskMetricsEngineState(StrEnum):
    NOT_READY = "NOT_READY"
    INPUT_INVALID = "INPUT_INVALID"
    RISK_METRICS_BLOCKED = "RISK_METRICS_BLOCKED"
    RISK_METRICS_COMPLETED_WITH_WARNINGS = "RISK_METRICS_COMPLETED_WITH_WARNINGS"
    RISK_METRICS_COMPLETED = "RISK_METRICS_COMPLETED"
    READY_FOR_PERFORMANCE_RISK_VALIDATION_GATE = "READY_FOR_PERFORMANCE_RISK_VALIDATION_GATE"


class RiskMetricsEngineDecision(StrEnum):
    BLOCK_RISK_METRICS = "BLOCK_RISK_METRICS"
    REQUIRE_PERFORMANCE_METRICS_FIXES = "REQUIRE_PERFORMANCE_METRICS_FIXES"
    REQUIRE_RISK_SAMPLE_FIXES = "REQUIRE_RISK_SAMPLE_FIXES"
    REQUIRE_EQUITY_SAMPLE_FIXES = "REQUIRE_EQUITY_SAMPLE_FIXES"
    REQUIRE_POSITION_SAMPLE_FIXES = "REQUIRE_POSITION_SAMPLE_FIXES"
    REQUIRE_THRESHOLD_FIXES = "REQUIRE_THRESHOLD_FIXES"
    REQUIRE_RISK_REVIEW = "REQUIRE_RISK_REVIEW"
    APPROVE_RISK_METRICS_ENGINE = "APPROVE_RISK_METRICS_ENGINE"


class RiskMetricsEngineRisk(StrEnum):
    PERFORMANCE_METRICS_NOT_APPROVED = "PERFORMANCE_METRICS_NOT_APPROVED"
    RISK_INPUT_MISSING = "RISK_INPUT_MISSING"
    TRADE_RISK_SAMPLE_EMPTY = "TRADE_RISK_SAMPLE_EMPTY"
    EQUITY_RISK_SAMPLE_INVALID = "EQUITY_RISK_SAMPLE_INVALID"
    POSITION_RISK_SAMPLE_INVALID = "POSITION_RISK_SAMPLE_INVALID"
    STOP_CONDITION_SAMPLE_INVALID = "STOP_CONDITION_SAMPLE_INVALID"
    MAX_LOSS_INVALID = "MAX_LOSS_INVALID"
    MAX_DRAWDOWN_INVALID = "MAX_DRAWDOWN_INVALID"
    LOSS_LIMIT_BREACHED = "LOSS_LIMIT_BREACHED"
    DRAWDOWN_LIMIT_BREACHED = "DRAWDOWN_LIMIT_BREACHED"
    RISK_PER_TRADE_TOO_HIGH = "RISK_PER_TRADE_TOO_HIGH"
    EXPOSURE_TOO_HIGH = "EXPOSURE_TOO_HIGH"
    CONSECUTIVE_LOSS_LIMIT_BREACHED = "CONSECUTIVE_LOSS_LIMIT_BREACHED"
    LOSS_STABILITY_WEAK = "LOSS_STABILITY_WEAK"
    STOP_CONDITION_QUALITY_WEAK = "STOP_CONDITION_QUALITY_WEAK"
    RISK_THRESHOLD_MISSING = "RISK_THRESHOLD_MISSING"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_PERFORMANCE_RISK_VALIDATION_GATE = "PREMATURE_PERFORMANCE_RISK_VALIDATION_GATE"


class RiskMetricsEngineRecommendation(StrEnum):
    HOLD_PERFORMANCE_RISK_VALIDATION_GATE = "HOLD_PERFORMANCE_RISK_VALIDATION_GATE"
    APPROVE_PERFORMANCE_METRICS_FIRST = "APPROVE_PERFORMANCE_METRICS_FIRST"
    PROVIDE_RISK_INPUTS = "PROVIDE_RISK_INPUTS"
    PROVIDE_TRADE_RISK_SAMPLES = "PROVIDE_TRADE_RISK_SAMPLES"
    REBUILD_EQUITY_RISK_SAMPLES = "REBUILD_EQUITY_RISK_SAMPLES"
    REBUILD_POSITION_RISK_SAMPLES = "REBUILD_POSITION_RISK_SAMPLES"
    REBUILD_STOP_CONDITION_SAMPLES = "REBUILD_STOP_CONDITION_SAMPLES"
    RECHECK_MAX_LOSS = "RECHECK_MAX_LOSS"
    RECHECK_MAX_DRAWDOWN = "RECHECK_MAX_DRAWDOWN"
    REDUCE_LOSS_LIMIT_USAGE = "REDUCE_LOSS_LIMIT_USAGE"
    REDUCE_DRAWDOWN = "REDUCE_DRAWDOWN"
    REDUCE_RISK_PER_TRADE = "REDUCE_RISK_PER_TRADE"
    REDUCE_EXPOSURE = "REDUCE_EXPOSURE"
    REDUCE_CONSECUTIVE_LOSSES = "REDUCE_CONSECUTIVE_LOSSES"
    IMPROVE_LOSS_STABILITY = "IMPROVE_LOSS_STABILITY"
    IMPROVE_STOP_CONDITION_QUALITY = "IMPROVE_STOP_CONDITION_QUALITY"
    DEFINE_RISK_THRESHOLDS = "DEFINE_RISK_THRESHOLDS"
    RESTORE_REAL_EXECUTION_BOUNDARIES = "RESTORE_REAL_EXECUTION_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_PERFORMANCE_RISK_VALIDATION_GATE = "DELAY_PERFORMANCE_RISK_VALIDATION_GATE"
    RUN_RISK_METRICS_ENGINE_SUITE = "RUN_RISK_METRICS_ENGINE_SUITE"
    APPROVE_PERFORMANCE_RISK_VALIDATION_GATE = "APPROVE_PERFORMANCE_RISK_VALIDATION_GATE"


@dataclass(frozen=True)
class TradeRiskSample:
    pnl: float
    quantity: float = 1.0
    entry_price: float = 0.0
    exit_price: float = 0.0
    risk_amount: float = 0.0
    symbol: str = ""
    step_open: int = 0
    step_close: int = 0


@dataclass(frozen=True)
class EquityRiskSample:
    step: int
    equity: float
    drawdown: float = 0.0
    drawdown_fraction: float = 0.0
    timestamp: str = ""


@dataclass(frozen=True)
class PositionRiskSample:
    step: int
    symbol: str
    quantity: float
    price: float
    equity: float
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0


@dataclass(frozen=True)
class StopConditionRiskSample:
    name: str
    configured: bool
    triggered: bool = False
    reasons: tuple[str, ...] = ()
    risks: tuple[Any, ...] = ()


@dataclass(frozen=True)
class RiskThresholds:
    max_loss_amount: float = 5_000.0
    max_drawdown_fraction: float = 0.20
    max_risk_per_trade_fraction: float = 0.02
    max_exposure_fraction: float = 1.0
    max_position_risk_amount: float = 100_000.0
    max_consecutive_losses: int = 3
    min_loss_stability_score: int = 70
    min_stop_condition_quality_score: int = 70
    min_quality_score: int = 70


@dataclass(frozen=True)
class RiskMetricSummary:
    max_loss: float = 0.0
    max_drawdown_fraction: float = 0.0
    loss_limit_usage: float = 0.0
    risk_per_trade_fraction: float = 0.0
    exposure_fraction: float = 0.0
    position_risk: float = 0.0
    consecutive_loss_count: int = 0
    loss_stability_score: int = 0
    stop_condition_quality_score: int = 0
    risk_quality_score: int = 0
    max_drawdown_amount: float = 0.0


@dataclass(frozen=True)
class RiskValidationFinding:
    name: str
    passed: bool
    score: int
    risks: tuple[RiskMetricsEngineRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class RiskMetricsEngineScore:
    overall_score: int
    performance_metrics_score: int
    risk_sample_score: int
    equity_sample_score: int
    position_sample_score: int
    stop_condition_score: int
    threshold_score: int
    max_loss_score: int
    drawdown_score: int
    risk_per_trade_score: int
    exposure_score: int
    consecutive_loss_score: int
    loss_stability_score: int
    boundary_score: int


@dataclass(frozen=True)
class RiskMetricsEngineInput:
    performance_metrics_result: Any = None
    performance_metrics_input: Any = None
    performance_metric_summary: Any = None
    performance_thresholds: Any = None
    controlled_simulation_result_report: Any = None
    controlled_simulation_offline_runner_result: Any = None
    offline_simulation_metrics: Any = None
    offline_equity_curve: Any = None
    offline_position_state: Any = None
    offline_stop_conditions: Any = None
    paper_runtime_forward_test_plan: Any = None
    official_paper_validation_report: Any = None
    paper_runtime_validation: Any = None
    paper_trading_runtime: Any = None
    observability_verification: Any = None
    rollback_verification: Any = None
    kill_switch_verification: Any = None
    human_validated_paper_session: Any = None
    supervised_paper_session: Any = None
    performance_metrics_approved: bool | None = None
    trade_risk_samples: tuple[TradeRiskSample | dict[str, Any], ...] | None = None
    equity_risk_samples: tuple[EquityRiskSample | dict[str, Any], ...] | None = None
    position_risk_samples: tuple[PositionRiskSample | dict[str, Any], ...] | None = None
    stop_condition_samples: tuple[StopConditionRiskSample | dict[str, Any], ...] | None = None
    thresholds: RiskThresholds | dict[str, Any] | None = field(default_factory=RiskThresholds)
    metric_tolerance: float = 1e-6
    performance_risk_validation_gate_requested: bool | None = False
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
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class RiskMetricsEngineResult:
    state: RiskMetricsEngineState
    decision: RiskMetricsEngineDecision
    engine_score: int
    score_breakdown: RiskMetricsEngineScore
    risks: tuple[RiskMetricsEngineRisk, ...] = ()
    recommendations: tuple[RiskMetricsEngineRecommendation, ...] = ()
    metric_summary: RiskMetricSummary = field(default_factory=RiskMetricSummary)
    thresholds: RiskThresholds = field(default_factory=RiskThresholds)
    trade_risk_samples: tuple[TradeRiskSample, ...] = ()
    equity_risk_samples: tuple[EquityRiskSample, ...] = ()
    position_risk_samples: tuple[PositionRiskSample, ...] = ()
    stop_condition_samples: tuple[StopConditionRiskSample, ...] = ()
    violations: tuple[RiskValidationFinding, ...] = ()
    findings: tuple[RiskValidationFinding, ...] = ()
    offline_only: bool = True
    summary: str = ""
