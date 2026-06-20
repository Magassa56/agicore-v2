"""Models for the AGIcore offline performance/risk validation gate."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PerformanceRiskValidationGateState(StrEnum):
    NOT_READY = "NOT_READY"
    VALIDATION_INPUT_INVALID = "VALIDATION_INPUT_INVALID"
    VALIDATION_BLOCKED = "VALIDATION_BLOCKED"
    VALIDATION_COMPLETED_WITH_WARNINGS = "VALIDATION_COMPLETED_WITH_WARNINGS"
    VALIDATION_COMPLETED = "VALIDATION_COMPLETED"
    READY_FOR_MULTI_SCENARIO_CONTROLLED_SIMULATION = "READY_FOR_MULTI_SCENARIO_CONTROLLED_SIMULATION"


class PerformanceRiskValidationGateDecision(StrEnum):
    BLOCK_PERFORMANCE_RISK_VALIDATION = "BLOCK_PERFORMANCE_RISK_VALIDATION"
    REQUIRE_PERFORMANCE_METRICS_FIXES = "REQUIRE_PERFORMANCE_METRICS_FIXES"
    REQUIRE_RISK_METRICS_FIXES = "REQUIRE_RISK_METRICS_FIXES"
    REQUIRE_MORE_TRADES = "REQUIRE_MORE_TRADES"
    REQUIRE_DRAWDOWN_REDUCTION = "REQUIRE_DRAWDOWN_REDUCTION"
    REQUIRE_RISK_REDUCTION = "REQUIRE_RISK_REDUCTION"
    REQUIRE_STABILITY_IMPROVEMENT = "REQUIRE_STABILITY_IMPROVEMENT"
    REQUIRE_ADDITIONAL_SCENARIOS = "REQUIRE_ADDITIONAL_SCENARIOS"
    APPROVE_PERFORMANCE_RISK_VALIDATION_GATE = "APPROVE_PERFORMANCE_RISK_VALIDATION_GATE"


class PerformanceRiskValidationGateRisk(StrEnum):
    PERFORMANCE_METRICS_NOT_APPROVED = "PERFORMANCE_METRICS_NOT_APPROVED"
    RISK_METRICS_NOT_APPROVED = "RISK_METRICS_NOT_APPROVED"
    PERFORMANCE_RISK_INPUT_MISSING = "PERFORMANCE_RISK_INPUT_MISSING"
    PNL_VALIDATION_FAILED = "PNL_VALIDATION_FAILED"
    RETURN_VALIDATION_FAILED = "RETURN_VALIDATION_FAILED"
    DRAWDOWN_VALIDATION_FAILED = "DRAWDOWN_VALIDATION_FAILED"
    PROFIT_FACTOR_VALIDATION_FAILED = "PROFIT_FACTOR_VALIDATION_FAILED"
    EXPECTANCY_VALIDATION_FAILED = "EXPECTANCY_VALIDATION_FAILED"
    TRADE_COUNT_TOO_LOW = "TRADE_COUNT_TOO_LOW"
    WIN_RATE_VALIDATION_WARNING = "WIN_RATE_VALIDATION_WARNING"
    RISK_PER_TRADE_TOO_HIGH = "RISK_PER_TRADE_TOO_HIGH"
    EXPOSURE_TOO_HIGH = "EXPOSURE_TOO_HIGH"
    LOSS_LIMIT_USAGE_TOO_HIGH = "LOSS_LIMIT_USAGE_TOO_HIGH"
    STABILITY_VALIDATION_FAILED = "STABILITY_VALIDATION_FAILED"
    RULE_VIOLATION_DETECTED = "RULE_VIOLATION_DETECTED"
    VALIDATION_THRESHOLD_MISSING = "VALIDATION_THRESHOLD_MISSING"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_MULTI_SCENARIO_CONTROLLED_SIMULATION = "PREMATURE_MULTI_SCENARIO_CONTROLLED_SIMULATION"


class PerformanceRiskValidationGateRecommendation(StrEnum):
    HOLD_MULTI_SCENARIO_CONTROLLED_SIMULATION = "HOLD_MULTI_SCENARIO_CONTROLLED_SIMULATION"
    APPROVE_PERFORMANCE_METRICS_FIRST = "APPROVE_PERFORMANCE_METRICS_FIRST"
    APPROVE_RISK_METRICS_FIRST = "APPROVE_RISK_METRICS_FIRST"
    PROVIDE_PERFORMANCE_RISK_INPUTS = "PROVIDE_PERFORMANCE_RISK_INPUTS"
    RECHECK_PNL = "RECHECK_PNL"
    RECHECK_RETURN = "RECHECK_RETURN"
    REDUCE_DRAWDOWN = "REDUCE_DRAWDOWN"
    IMPROVE_PROFIT_FACTOR = "IMPROVE_PROFIT_FACTOR"
    IMPROVE_EXPECTANCY = "IMPROVE_EXPECTANCY"
    ADD_MORE_TRADES = "ADD_MORE_TRADES"
    IMPROVE_WIN_RATE_SAMPLE = "IMPROVE_WIN_RATE_SAMPLE"
    REDUCE_RISK_PER_TRADE = "REDUCE_RISK_PER_TRADE"
    REDUCE_EXPOSURE = "REDUCE_EXPOSURE"
    REDUCE_LOSS_LIMIT_USAGE = "REDUCE_LOSS_LIMIT_USAGE"
    IMPROVE_STABILITY = "IMPROVE_STABILITY"
    RESOLVE_RULE_VIOLATIONS = "RESOLVE_RULE_VIOLATIONS"
    DEFINE_VALIDATION_THRESHOLDS = "DEFINE_VALIDATION_THRESHOLDS"
    RESTORE_REAL_EXECUTION_BOUNDARIES = "RESTORE_REAL_EXECUTION_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_MULTI_SCENARIO_CONTROLLED_SIMULATION = "DELAY_MULTI_SCENARIO_CONTROLLED_SIMULATION"
    RUN_PERFORMANCE_RISK_VALIDATION_GATE_SUITE = "RUN_PERFORMANCE_RISK_VALIDATION_GATE_SUITE"
    APPROVE_MULTI_SCENARIO_CONTROLLED_SIMULATION = "APPROVE_MULTI_SCENARIO_CONTROLLED_SIMULATION"


@dataclass(frozen=True)
class PerformanceRiskValidationThresholds:
    min_total_pnl: float = 0.0
    min_return_fraction: float = 0.0
    max_drawdown_fraction: float = 0.20
    min_profit_factor: float = 1.0
    min_expectancy: float = 0.0
    min_trade_count: int = 1
    min_win_rate: float = 0.0
    max_risk_per_trade_fraction: float = 0.02
    max_exposure_fraction: float = 1.0
    max_loss_limit_usage: float = 1.0
    min_performance_stability_score: int = 50
    min_risk_stability_score: int = 70
    min_performance_quality_score: int = 70
    min_risk_quality_score: int = 70
    max_rule_violation_count: int = 0
    min_gate_score: int = 80


@dataclass(frozen=True)
class PerformanceRiskValidationFinding:
    name: str
    passed: bool
    score: int
    risks: tuple[PerformanceRiskValidationGateRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class PerformanceRiskValidationSummary:
    total_pnl: float = 0.0
    return_fraction: float = 0.0
    max_drawdown_fraction: float = 0.0
    profit_factor: float = 0.0
    expectancy: float = 0.0
    trade_count: int = 0
    win_rate: float = 0.0
    risk_per_trade_fraction: float = 0.0
    exposure_fraction: float = 0.0
    loss_limit_usage: float = 0.0
    performance_stability_score: int = 0
    risk_stability_score: int = 0
    performance_quality_score: int = 0
    risk_quality_score: int = 0
    rule_violation_count: int = 0


@dataclass(frozen=True)
class PerformanceRiskValidationGateScore:
    overall_score: int
    performance_approval_score: int
    risk_approval_score: int
    pnl_score: int
    return_score: int
    drawdown_score: int
    profit_factor_score: int
    expectancy_score: int
    trade_count_score: int
    win_rate_score: int
    risk_per_trade_score: int
    exposure_score: int
    loss_limit_score: int
    stability_score: int
    rule_violation_score: int
    threshold_score: int
    boundary_score: int


@dataclass(frozen=True)
class PerformanceRiskValidationGateInput:
    performance_metrics_result: Any = None
    risk_metrics_result: Any = None
    performance_metric_summary: Any = None
    risk_metric_summary: Any = None
    performance_thresholds: Any = None
    risk_thresholds: Any = None
    controlled_simulation_result_report: Any = None
    controlled_simulation_offline_runner_result: Any = None
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
    risk_metrics_approved: bool | None = None
    thresholds: PerformanceRiskValidationThresholds | dict[str, Any] | None = field(default_factory=PerformanceRiskValidationThresholds)
    metric_tolerance: float = 1e-6
    multi_scenario_controlled_simulation_requested: bool | None = False
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
class PerformanceRiskValidationGateResult:
    state: PerformanceRiskValidationGateState
    decision: PerformanceRiskValidationGateDecision
    gate_score: int
    score_breakdown: PerformanceRiskValidationGateScore
    risks: tuple[PerformanceRiskValidationGateRisk, ...] = ()
    recommendations: tuple[PerformanceRiskValidationGateRecommendation, ...] = ()
    validation_summary: PerformanceRiskValidationSummary = field(default_factory=PerformanceRiskValidationSummary)
    thresholds: PerformanceRiskValidationThresholds = field(default_factory=PerformanceRiskValidationThresholds)
    findings: tuple[PerformanceRiskValidationFinding, ...] = ()
    offline_only: bool = True
    summary: str = ""
