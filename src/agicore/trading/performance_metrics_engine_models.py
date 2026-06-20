"""Models for the AGIcore offline performance metrics engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PerformanceMetricsEngineState(StrEnum):
    NOT_READY = "NOT_READY"
    INPUT_INVALID = "INPUT_INVALID"
    METRICS_BLOCKED = "METRICS_BLOCKED"
    METRICS_COMPLETED_WITH_WARNINGS = "METRICS_COMPLETED_WITH_WARNINGS"
    METRICS_COMPLETED = "METRICS_COMPLETED"
    READY_FOR_RISK_METRICS_ENGINE = "READY_FOR_RISK_METRICS_ENGINE"


class PerformanceMetricsEngineDecision(StrEnum):
    BLOCK_PERFORMANCE_METRICS = "BLOCK_PERFORMANCE_METRICS"
    REQUIRE_RESULT_REPORT_FIXES = "REQUIRE_RESULT_REPORT_FIXES"
    REQUIRE_TRADE_SAMPLE_FIXES = "REQUIRE_TRADE_SAMPLE_FIXES"
    REQUIRE_EQUITY_SAMPLE_FIXES = "REQUIRE_EQUITY_SAMPLE_FIXES"
    REQUIRE_THRESHOLD_FIXES = "REQUIRE_THRESHOLD_FIXES"
    REQUIRE_PERFORMANCE_REVIEW = "REQUIRE_PERFORMANCE_REVIEW"
    APPROVE_PERFORMANCE_METRICS_ENGINE = "APPROVE_PERFORMANCE_METRICS_ENGINE"


class PerformanceMetricsEngineRisk(StrEnum):
    RESULT_REPORT_NOT_APPROVED = "RESULT_REPORT_NOT_APPROVED"
    PERFORMANCE_INPUT_MISSING = "PERFORMANCE_INPUT_MISSING"
    TRADE_SAMPLE_EMPTY = "TRADE_SAMPLE_EMPTY"
    EQUITY_SAMPLE_INVALID = "EQUITY_SAMPLE_INVALID"
    PNL_INVALID = "PNL_INVALID"
    RETURN_INVALID = "RETURN_INVALID"
    DRAWDOWN_INVALID = "DRAWDOWN_INVALID"
    WIN_RATE_INVALID = "WIN_RATE_INVALID"
    PROFIT_FACTOR_INVALID = "PROFIT_FACTOR_INVALID"
    EXPECTANCY_INVALID = "EXPECTANCY_INVALID"
    TRADE_COUNT_TOO_LOW = "TRADE_COUNT_TOO_LOW"
    RISK_REWARD_INVALID = "RISK_REWARD_INVALID"
    PERFORMANCE_STABILITY_WEAK = "PERFORMANCE_STABILITY_WEAK"
    PERFORMANCE_THRESHOLD_MISSING = "PERFORMANCE_THRESHOLD_MISSING"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_RISK_METRICS_ENGINE = "PREMATURE_RISK_METRICS_ENGINE"


class PerformanceMetricsEngineRecommendation(StrEnum):
    HOLD_RISK_METRICS_ENGINE = "HOLD_RISK_METRICS_ENGINE"
    APPROVE_RESULT_REPORT_FIRST = "APPROVE_RESULT_REPORT_FIRST"
    PROVIDE_PERFORMANCE_INPUTS = "PROVIDE_PERFORMANCE_INPUTS"
    PROVIDE_TRADE_SAMPLES = "PROVIDE_TRADE_SAMPLES"
    REBUILD_EQUITY_SAMPLES = "REBUILD_EQUITY_SAMPLES"
    RECHECK_PNL = "RECHECK_PNL"
    RECHECK_RETURN = "RECHECK_RETURN"
    RECHECK_DRAWDOWN = "RECHECK_DRAWDOWN"
    RECHECK_WIN_RATE = "RECHECK_WIN_RATE"
    RECHECK_PROFIT_FACTOR = "RECHECK_PROFIT_FACTOR"
    RECHECK_EXPECTANCY = "RECHECK_EXPECTANCY"
    INCREASE_TRADE_SAMPLE_SIZE = "INCREASE_TRADE_SAMPLE_SIZE"
    RECHECK_RISK_REWARD = "RECHECK_RISK_REWARD"
    IMPROVE_PERFORMANCE_STABILITY = "IMPROVE_PERFORMANCE_STABILITY"
    DEFINE_PERFORMANCE_THRESHOLDS = "DEFINE_PERFORMANCE_THRESHOLDS"
    RESTORE_REAL_EXECUTION_BOUNDARIES = "RESTORE_REAL_EXECUTION_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_RISK_METRICS_ENGINE = "DELAY_RISK_METRICS_ENGINE"
    RUN_PERFORMANCE_METRICS_ENGINE_SUITE = "RUN_PERFORMANCE_METRICS_ENGINE_SUITE"
    APPROVE_RISK_METRICS_ENGINE = "APPROVE_RISK_METRICS_ENGINE"


@dataclass(frozen=True)
class TradePerformanceSample:
    pnl: float
    quantity: float = 1.0
    entry_price: float = 0.0
    exit_price: float = 0.0
    symbol: str = ""
    step_open: int = 0
    step_close: int = 0


@dataclass(frozen=True)
class EquityPerformanceSample:
    step: int
    equity: float
    drawdown: float = 0.0
    drawdown_fraction: float = 0.0
    timestamp: str = ""


@dataclass(frozen=True)
class PerformanceThresholds:
    min_trade_count: int = 1
    max_drawdown_fraction: float = 0.20
    min_win_rate: float = 0.0
    min_profit_factor: float = 0.0
    min_expectancy: float = -1_000_000.0
    min_return_fraction: float = -1.0
    min_risk_reward_ratio: float = 0.0
    min_stability_score: int = 50
    min_quality_score: int = 70


@dataclass(frozen=True)
class PerformanceMetricSummary:
    total_pnl: float
    return_fraction: float
    return_percent: float
    max_drawdown: float
    max_drawdown_fraction: float
    win_rate: float
    profit_factor: float
    expectancy: float
    trade_count: int
    average_win: float
    average_loss: float
    risk_reward_ratio: float
    stability_score: int
    quality_score: int


@dataclass(frozen=True)
class PerformanceValidationFinding:
    name: str
    passed: bool
    score: int
    risks: tuple[PerformanceMetricsEngineRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class PerformanceMetricsEngineScore:
    overall_score: int
    result_report_score: int
    trade_sample_score: int
    equity_sample_score: int
    threshold_score: int
    pnl_score: int
    return_score: int
    drawdown_score: int
    win_rate_score: int
    profit_factor_score: int
    expectancy_score: int
    trade_count_score: int
    risk_reward_score: int
    stability_score: int
    boundary_score: int


@dataclass(frozen=True)
class PerformanceMetricsEngineInput:
    controlled_simulation_result_report: Any = None
    controlled_simulation_offline_runner_result: Any = None
    controlled_simulation_result_report_input: Any = None
    controlled_simulation_offline_runner_input: Any = None
    controlled_simulation_review_precheck: Any = None
    paper_runtime_forward_test_plan: Any = None
    official_paper_validation_report: Any = None
    paper_runtime_validation: Any = None
    paper_trading_runtime: Any = None
    observability_verification: Any = None
    rollback_verification: Any = None
    kill_switch_verification: Any = None
    human_validated_paper_session: Any = None
    supervised_paper_session: Any = None
    result_report_approved: bool | None = None
    trade_samples: tuple[TradePerformanceSample | dict[str, Any], ...] | None = None
    equity_samples: tuple[EquityPerformanceSample | dict[str, Any], ...] | None = None
    thresholds: PerformanceThresholds | dict[str, Any] | None = field(default_factory=PerformanceThresholds)
    metric_tolerance: float = 1e-6
    risk_metrics_engine_requested: bool | None = False
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
class PerformanceMetricsEngineResult:
    state: PerformanceMetricsEngineState
    decision: PerformanceMetricsEngineDecision
    engine_score: int
    score_breakdown: PerformanceMetricsEngineScore
    risks: tuple[PerformanceMetricsEngineRisk, ...] = ()
    recommendations: tuple[PerformanceMetricsEngineRecommendation, ...] = ()
    metric_summary: PerformanceMetricSummary = field(
        default_factory=lambda: PerformanceMetricSummary(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0, 0.0, 0, 0)
    )
    thresholds: PerformanceThresholds = field(default_factory=PerformanceThresholds)
    trade_samples: tuple[TradePerformanceSample, ...] = ()
    equity_samples: tuple[EquityPerformanceSample, ...] = ()
    findings: tuple[PerformanceValidationFinding, ...] = ()
    offline_only: bool = True
    summary: str = ""
