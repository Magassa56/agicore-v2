"""Models for the AGIcore multi-scenario result report and robustness review."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from agicore.trading.multi_scenario_controlled_simulation_models import ControlledSimulationScenarioType


class MultiScenarioResultReportState(StrEnum):
    NOT_READY = "NOT_READY"
    REPORT_INPUT_INVALID = "REPORT_INPUT_INVALID"
    REPORT_BLOCKED = "REPORT_BLOCKED"
    REPORT_COMPLETED_WITH_WARNINGS = "REPORT_COMPLETED_WITH_WARNINGS"
    REPORT_COMPLETED = "REPORT_COMPLETED"
    READY_FOR_PAPER_BROKER_READ_ONLY_PREPARATION = "READY_FOR_PAPER_BROKER_READ_ONLY_PREPARATION"


class MultiScenarioResultReportDecision(StrEnum):
    BLOCK_MULTI_SCENARIO_RESULT_REPORT = "BLOCK_MULTI_SCENARIO_RESULT_REPORT"
    REQUIRE_MULTI_SCENARIO_FIXES = "REQUIRE_MULTI_SCENARIO_FIXES"
    REQUIRE_AGGREGATE_METRIC_FIXES = "REQUIRE_AGGREGATE_METRIC_FIXES"
    REQUIRE_ROBUSTNESS_FIXES = "REQUIRE_ROBUSTNESS_FIXES"
    REQUIRE_STABILITY_FIXES = "REQUIRE_STABILITY_FIXES"
    REQUIRE_RISK_REDUCTION = "REQUIRE_RISK_REDUCTION"
    REQUIRE_ADDITIONAL_SCENARIOS = "REQUIRE_ADDITIONAL_SCENARIOS"
    REQUIRE_POSITION_CONSISTENCY_FIXES = "REQUIRE_POSITION_CONSISTENCY_FIXES"
    REQUIRE_STOP_CONDITION_FIXES = "REQUIRE_STOP_CONDITION_FIXES"
    APPROVE_MULTI_SCENARIO_RESULT_REPORT_ROBUSTNESS_REVIEW = "APPROVE_MULTI_SCENARIO_RESULT_REPORT_ROBUSTNESS_REVIEW"


class MultiScenarioResultReportRisk(StrEnum):
    MULTI_SCENARIO_SIMULATION_NOT_APPROVED = "MULTI_SCENARIO_SIMULATION_NOT_APPROVED"
    MULTI_SCENARIO_RESULT_MISSING = "MULTI_SCENARIO_RESULT_MISSING"
    AGGREGATE_METRICS_MISSING = "AGGREGATE_METRICS_MISSING"
    SCENARIO_PASS_FAIL_REVIEW_INVALID = "SCENARIO_PASS_FAIL_REVIEW_INVALID"
    MULTI_SCENARIO_PNL_REVIEW_INVALID = "MULTI_SCENARIO_PNL_REVIEW_INVALID"
    MULTI_SCENARIO_DRAWDOWN_REVIEW_INVALID = "MULTI_SCENARIO_DRAWDOWN_REVIEW_INVALID"
    MULTI_SCENARIO_PROFIT_FACTOR_REVIEW_INVALID = "MULTI_SCENARIO_PROFIT_FACTOR_REVIEW_INVALID"
    MULTI_SCENARIO_EXPECTANCY_REVIEW_INVALID = "MULTI_SCENARIO_EXPECTANCY_REVIEW_INVALID"
    MULTI_SCENARIO_STABILITY_WEAK = "MULTI_SCENARIO_STABILITY_WEAK"
    MULTI_SCENARIO_ROBUSTNESS_WEAK = "MULTI_SCENARIO_ROBUSTNESS_WEAK"
    LOSING_SCENARIO_BEHAVIOR_INVALID = "LOSING_SCENARIO_BEHAVIOR_INVALID"
    DRAWDOWN_SCENARIO_BEHAVIOR_INVALID = "DRAWDOWN_SCENARIO_BEHAVIOR_INVALID"
    RISK_VIOLATION_SCENARIO_BEHAVIOR_INVALID = "RISK_VIOLATION_SCENARIO_BEHAVIOR_INVALID"
    POSITION_INCONSISTENCY_SCENARIO_BEHAVIOR_INVALID = "POSITION_INCONSISTENCY_SCENARIO_BEHAVIOR_INVALID"
    STOP_CONDITION_SCENARIO_BEHAVIOR_INVALID = "STOP_CONDITION_SCENARIO_BEHAVIOR_INVALID"
    PAPER_BROKER_READ_ONLY_PREPARATION_PREMATURE = "PAPER_BROKER_READ_ONLY_PREPARATION_PREMATURE"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"


class MultiScenarioResultReportRecommendation(StrEnum):
    HOLD_PAPER_BROKER_READ_ONLY_PREPARATION = "HOLD_PAPER_BROKER_READ_ONLY_PREPARATION"
    APPROVE_MULTI_SCENARIO_SIMULATION_FIRST = "APPROVE_MULTI_SCENARIO_SIMULATION_FIRST"
    PROVIDE_MULTI_SCENARIO_RESULT = "PROVIDE_MULTI_SCENARIO_RESULT"
    REBUILD_AGGREGATE_METRICS = "REBUILD_AGGREGATE_METRICS"
    RECHECK_SCENARIO_PASS_FAIL_DISTRIBUTION = "RECHECK_SCENARIO_PASS_FAIL_DISTRIBUTION"
    RECHECK_MULTI_SCENARIO_PNL = "RECHECK_MULTI_SCENARIO_PNL"
    REDUCE_MULTI_SCENARIO_DRAWDOWN = "REDUCE_MULTI_SCENARIO_DRAWDOWN"
    IMPROVE_MULTI_SCENARIO_PROFIT_FACTOR = "IMPROVE_MULTI_SCENARIO_PROFIT_FACTOR"
    IMPROVE_MULTI_SCENARIO_EXPECTANCY = "IMPROVE_MULTI_SCENARIO_EXPECTANCY"
    IMPROVE_MULTI_SCENARIO_STABILITY = "IMPROVE_MULTI_SCENARIO_STABILITY"
    IMPROVE_MULTI_SCENARIO_ROBUSTNESS = "IMPROVE_MULTI_SCENARIO_ROBUSTNESS"
    RECHECK_LOSING_SCENARIO = "RECHECK_LOSING_SCENARIO"
    RECHECK_DRAWDOWN_SCENARIO = "RECHECK_DRAWDOWN_SCENARIO"
    RECHECK_RISK_VIOLATION_SCENARIO = "RECHECK_RISK_VIOLATION_SCENARIO"
    RECHECK_POSITION_INCONSISTENCY_SCENARIO = "RECHECK_POSITION_INCONSISTENCY_SCENARIO"
    RECHECK_STOP_CONDITION_SCENARIO = "RECHECK_STOP_CONDITION_SCENARIO"
    DELAY_PAPER_BROKER_READ_ONLY_PREPARATION = "DELAY_PAPER_BROKER_READ_ONLY_PREPARATION"
    RESTORE_REAL_EXECUTION_BOUNDARIES = "RESTORE_REAL_EXECUTION_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    RUN_MULTI_SCENARIO_RESULT_REPORT_SUITE = "RUN_MULTI_SCENARIO_RESULT_REPORT_SUITE"
    APPROVE_PAPER_BROKER_READ_ONLY_PREPARATION = "APPROVE_PAPER_BROKER_READ_ONLY_PREPARATION"


@dataclass(frozen=True)
class MultiScenarioAggregateMetricReview:
    scenario_count: int = 0
    passed_scenario_count: int = 0
    failed_scenario_count: int = 0
    total_pnl: float = 0.0
    average_pnl: float = 0.0
    max_drawdown_fraction: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    expectancy: float = 0.0
    trade_count: int = 0
    passed: bool = False
    risks: tuple[MultiScenarioResultReportRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class MultiScenarioRobustnessReview:
    robustness_score: int = 0
    min_robustness_score: int = 60
    passed: bool = False
    risks: tuple[MultiScenarioResultReportRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class MultiScenarioStabilityReview:
    stability_score: int = 0
    min_stability_score: int = 60
    passed: bool = False
    risks: tuple[MultiScenarioResultReportRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class MultiScenarioBehaviorReview:
    scenario_type: ControlledSimulationScenarioType
    present: bool
    passed: bool
    scenario_count: int = 0
    pnl: float = 0.0
    max_drawdown_fraction: float = 0.0
    risks: tuple[MultiScenarioResultReportRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class MultiScenarioReadinessFinding:
    name: str
    passed: bool
    score: int
    risks: tuple[MultiScenarioResultReportRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class MultiScenarioPostRunFinding:
    name: str
    passed: bool
    score: int
    risks: tuple[MultiScenarioResultReportRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class MultiScenarioResultReportScore:
    overall_score: int
    simulation_approval_score: int
    aggregate_metric_score: int
    pass_fail_score: int
    pnl_score: int
    drawdown_score: int
    profit_factor_score: int
    expectancy_score: int
    stability_score: int
    robustness_score: int
    behavior_score: int
    readiness_score: int
    boundary_score: int


@dataclass(frozen=True)
class MultiScenarioResultReportInput:
    multi_scenario_controlled_simulation_result: Any = None
    multi_scenario_metric_summary: Any = None
    multi_scenario_aggregate_report: Any = None
    controlled_simulation_scenario_results: Any = None
    performance_risk_validation_gate: Any = None
    performance_metrics_result: Any = None
    risk_metrics_result: Any = None
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
    multi_scenario_simulation_approved: bool | None = None
    min_robustness_score: int = 60
    min_stability_score: int = 60
    min_total_pnl: float = 0.0
    max_drawdown_fraction: float = 0.25
    min_profit_factor: float = 1.0
    min_expectancy: float = 0.0
    max_failed_scenarios: int = 0
    paper_broker_read_only_preparation_requested: bool | None = False
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
class MultiScenarioResultReportResult:
    state: MultiScenarioResultReportState
    decision: MultiScenarioResultReportDecision
    report_score: int
    score_breakdown: MultiScenarioResultReportScore
    risks: tuple[MultiScenarioResultReportRisk, ...] = ()
    recommendations: tuple[MultiScenarioResultReportRecommendation, ...] = ()
    aggregate_metric_review: MultiScenarioAggregateMetricReview = field(default_factory=MultiScenarioAggregateMetricReview)
    robustness_review: MultiScenarioRobustnessReview = field(default_factory=MultiScenarioRobustnessReview)
    stability_review: MultiScenarioStabilityReview = field(default_factory=MultiScenarioStabilityReview)
    behavior_reviews: tuple[MultiScenarioBehaviorReview, ...] = ()
    readiness_finding: MultiScenarioReadinessFinding = field(
        default_factory=lambda: MultiScenarioReadinessFinding("paper_broker_read_only_readiness", False, 0)
    )
    findings: tuple[MultiScenarioPostRunFinding, ...] = ()
    offline_only: bool = True
    summary: str = ""
