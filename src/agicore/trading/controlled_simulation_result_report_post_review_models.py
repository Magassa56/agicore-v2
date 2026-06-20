"""Models for the controlled simulation result report and post-run review."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ControlledSimulationResultReportState(StrEnum):
    NOT_READY = "NOT_READY"
    REPORT_INPUT_INVALID = "REPORT_INPUT_INVALID"
    REPORT_BLOCKED = "REPORT_BLOCKED"
    REPORT_COMPLETED_WITH_WARNINGS = "REPORT_COMPLETED_WITH_WARNINGS"
    REPORT_COMPLETED = "REPORT_COMPLETED"
    READY_FOR_PERFORMANCE_METRICS_ENGINE = "READY_FOR_PERFORMANCE_METRICS_ENGINE"


class ControlledSimulationResultReportDecision(StrEnum):
    BLOCK_RESULT_REPORT = "BLOCK_RESULT_REPORT"
    REQUIRE_OFFLINE_RUNNER_FIXES = "REQUIRE_OFFLINE_RUNNER_FIXES"
    REQUIRE_METRIC_FIXES = "REQUIRE_METRIC_FIXES"
    REQUIRE_EQUITY_CURVE_FIXES = "REQUIRE_EQUITY_CURVE_FIXES"
    REQUIRE_POSITION_FIXES = "REQUIRE_POSITION_FIXES"
    REQUIRE_STOP_CONDITION_FIXES = "REQUIRE_STOP_CONDITION_FIXES"
    REQUIRE_RISK_REVIEW_FIXES = "REQUIRE_RISK_REVIEW_FIXES"
    APPROVE_CONTROLLED_SIMULATION_RESULT_REPORT = "APPROVE_CONTROLLED_SIMULATION_RESULT_REPORT"


class ControlledSimulationResultReportRisk(StrEnum):
    OFFLINE_RUNNER_NOT_APPROVED = "OFFLINE_RUNNER_NOT_APPROVED"
    OFFLINE_RUNNER_RESULT_MISSING = "OFFLINE_RUNNER_RESULT_MISSING"
    METRICS_MISSING = "METRICS_MISSING"
    PNL_REPORT_INVALID = "PNL_REPORT_INVALID"
    DRAWDOWN_REPORT_INVALID = "DRAWDOWN_REPORT_INVALID"
    WIN_RATE_REPORT_INVALID = "WIN_RATE_REPORT_INVALID"
    PROFIT_FACTOR_REPORT_INVALID = "PROFIT_FACTOR_REPORT_INVALID"
    EXPECTANCY_REPORT_INVALID = "EXPECTANCY_REPORT_INVALID"
    EQUITY_CURVE_REVIEW_INVALID = "EQUITY_CURVE_REVIEW_INVALID"
    POSITION_CONSISTENCY_INVALID = "POSITION_CONSISTENCY_INVALID"
    STOP_CONDITION_REVIEW_INVALID = "STOP_CONDITION_REVIEW_INVALID"
    RISK_REVIEW_INCOMPLETE = "RISK_REVIEW_INCOMPLETE"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_PERFORMANCE_METRICS_ENGINE = "PREMATURE_PERFORMANCE_METRICS_ENGINE"


class ControlledSimulationResultReportRecommendation(StrEnum):
    HOLD_PERFORMANCE_METRICS_ENGINE = "HOLD_PERFORMANCE_METRICS_ENGINE"
    APPROVE_OFFLINE_RUNNER_FIRST = "APPROVE_OFFLINE_RUNNER_FIRST"
    PROVIDE_OFFLINE_RUNNER_RESULT = "PROVIDE_OFFLINE_RUNNER_RESULT"
    REBUILD_METRIC_SUMMARY = "REBUILD_METRIC_SUMMARY"
    RECHECK_PNL_REPORT = "RECHECK_PNL_REPORT"
    RECHECK_DRAWDOWN_REPORT = "RECHECK_DRAWDOWN_REPORT"
    RECHECK_WIN_RATE_REPORT = "RECHECK_WIN_RATE_REPORT"
    RECHECK_PROFIT_FACTOR_REPORT = "RECHECK_PROFIT_FACTOR_REPORT"
    RECHECK_EXPECTANCY_REPORT = "RECHECK_EXPECTANCY_REPORT"
    REBUILD_EQUITY_CURVE_REVIEW = "REBUILD_EQUITY_CURVE_REVIEW"
    RECONCILE_FINAL_POSITION = "RECONCILE_FINAL_POSITION"
    REVIEW_STOP_CONDITIONS = "REVIEW_STOP_CONDITIONS"
    COMPLETE_RISK_REVIEW = "COMPLETE_RISK_REVIEW"
    RESTORE_REAL_EXECUTION_BOUNDARIES = "RESTORE_REAL_EXECUTION_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_PERFORMANCE_METRICS_ENGINE = "DELAY_PERFORMANCE_METRICS_ENGINE"
    RUN_RESULT_REPORT_POST_REVIEW_SUITE = "RUN_RESULT_REPORT_POST_REVIEW_SUITE"
    APPROVE_PERFORMANCE_METRICS_ENGINE = "APPROVE_PERFORMANCE_METRICS_ENGINE"


@dataclass(frozen=True)
class OfflineSimulationMetricSummary:
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
    return_fraction: float


@dataclass(frozen=True)
class OfflineEquityCurveReview:
    point_count: int
    first_equity: float
    last_equity: float
    min_equity: float
    max_equity: float
    monotonic_steps: bool
    final_matches_metrics: bool
    passed: bool
    risks: tuple[ControlledSimulationResultReportRisk, ...] = ()


@dataclass(frozen=True)
class OfflinePnLQualityReview:
    reported_total_pnl: float
    recomputed_total_pnl: float
    realized_unrealized_total: float
    matches_equity_curve: bool
    matches_components: bool
    passed: bool
    risks: tuple[ControlledSimulationResultReportRisk, ...] = ()


@dataclass(frozen=True)
class OfflineDrawdownQualityReview:
    reported_max_drawdown: float
    recomputed_max_drawdown: float
    reported_max_drawdown_fraction: float
    recomputed_max_drawdown_fraction: float
    within_limit: bool
    passed: bool
    risks: tuple[ControlledSimulationResultReportRisk, ...] = ()


@dataclass(frozen=True)
class OfflinePositionConsistencyReview:
    symbol: str
    quantity: float
    average_price: float
    cash: float
    equity: float
    expected_flat: bool
    flat: bool
    equity_matches_curve: bool
    passed: bool
    risks: tuple[ControlledSimulationResultReportRisk, ...] = ()


@dataclass(frozen=True)
class OfflinePostRunFinding:
    name: str
    passed: bool
    score: int
    risks: tuple[ControlledSimulationResultReportRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ControlledSimulationResultReportScore:
    overall_score: int
    runner_score: int
    metric_score: int
    equity_curve_score: int
    pnl_score: int
    drawdown_score: int
    win_rate_score: int
    profit_factor_score: int
    expectancy_score: int
    position_score: int
    stop_condition_score: int
    risk_review_score: int
    boundary_score: int


@dataclass(frozen=True)
class ControlledSimulationResultReportInput:
    controlled_simulation_offline_runner_result: Any = None
    controlled_simulation_offline_runner_input: Any = None
    controlled_simulation_review_precheck: Any = None
    paper_broker_sandbox_dry_run_controlled_simulation_plan: Any = None
    paper_broker_sandbox_dry_run_execution_authorization_gate: Any = None
    paper_runtime_forward_test_plan: Any = None
    official_paper_validation_report: Any = None
    paper_runtime_validation: Any = None
    paper_trading_runtime: Any = None
    observability_verification: Any = None
    rollback_verification: Any = None
    kill_switch_verification: Any = None
    human_validated_paper_session: Any = None
    supervised_paper_session: Any = None
    offline_runner_approved: bool | None = None
    require_flat_final_position: bool = True
    max_allowed_drawdown_fraction: float | None = None
    metric_tolerance: float = 1e-6
    report_requested: bool | None = True
    performance_metrics_engine_requested: bool | None = False
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
class ControlledSimulationResultReportResult:
    state: ControlledSimulationResultReportState
    decision: ControlledSimulationResultReportDecision
    report_score: int
    score_breakdown: ControlledSimulationResultReportScore
    risks: tuple[ControlledSimulationResultReportRisk, ...] = ()
    recommendations: tuple[ControlledSimulationResultReportRecommendation, ...] = ()
    metric_summary: OfflineSimulationMetricSummary = field(
        default_factory=lambda: OfflineSimulationMetricSummary(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0)
    )
    equity_curve_review: OfflineEquityCurveReview = field(
        default_factory=lambda: OfflineEquityCurveReview(0, 0.0, 0.0, 0.0, 0.0, False, False, False)
    )
    pnl_quality: OfflinePnLQualityReview = field(
        default_factory=lambda: OfflinePnLQualityReview(0.0, 0.0, 0.0, False, False, False)
    )
    drawdown_quality: OfflineDrawdownQualityReview = field(
        default_factory=lambda: OfflineDrawdownQualityReview(0.0, 0.0, 0.0, 0.0, False, False)
    )
    win_rate_quality: OfflinePostRunFinding = field(
        default_factory=lambda: OfflinePostRunFinding("win_rate_quality", False, 0)
    )
    profit_factor_quality: OfflinePostRunFinding = field(
        default_factory=lambda: OfflinePostRunFinding("profit_factor_quality", False, 0)
    )
    expectancy_quality: OfflinePostRunFinding = field(
        default_factory=lambda: OfflinePostRunFinding("expectancy_quality", False, 0)
    )
    position_consistency: OfflinePositionConsistencyReview = field(
        default_factory=lambda: OfflinePositionConsistencyReview("", 0.0, 0.0, 0.0, 0.0, True, False, False, False)
    )
    stop_condition_review: OfflinePostRunFinding = field(
        default_factory=lambda: OfflinePostRunFinding("stop_condition_review", False, 0)
    )
    runner_risk_review: OfflinePostRunFinding = field(
        default_factory=lambda: OfflinePostRunFinding("runner_risk_review", False, 0)
    )
    findings: tuple[OfflinePostRunFinding, ...] = ()
    offline_only: bool = True
    summary: str = ""
