"""Models for AGIcore multi-scenario controlled simulation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from agicore.trading.controlled_simulation_offline_runner_models import (
    OfflineSignalEvent,
    OfflineSyntheticMarketBar,
)


class ControlledSimulationScenarioType(StrEnum):
    WINNING_SCENARIO = "WINNING_SCENARIO"
    LOSING_SCENARIO = "LOSING_SCENARIO"
    FLAT_SCENARIO = "FLAT_SCENARIO"
    DRAWDOWN_SCENARIO = "DRAWDOWN_SCENARIO"
    VOLATILE_SCENARIO = "VOLATILE_SCENARIO"
    STOP_CONDITION_SCENARIO = "STOP_CONDITION_SCENARIO"
    RISK_VIOLATION_SCENARIO = "RISK_VIOLATION_SCENARIO"
    POSITION_INCONSISTENCY_SCENARIO = "POSITION_INCONSISTENCY_SCENARIO"
    MIXED_SCENARIO = "MIXED_SCENARIO"


class MultiScenarioControlledSimulationState(StrEnum):
    NOT_READY = "NOT_READY"
    INPUT_INVALID = "INPUT_INVALID"
    MULTI_SCENARIO_BLOCKED = "MULTI_SCENARIO_BLOCKED"
    MULTI_SCENARIO_COMPLETED_WITH_WARNINGS = "MULTI_SCENARIO_COMPLETED_WITH_WARNINGS"
    MULTI_SCENARIO_COMPLETED = "MULTI_SCENARIO_COMPLETED"
    READY_FOR_MULTI_SCENARIO_RESULT_REPORT = "READY_FOR_MULTI_SCENARIO_RESULT_REPORT"


class MultiScenarioControlledSimulationDecision(StrEnum):
    BLOCK_MULTI_SCENARIO_CONTROLLED_SIMULATION = "BLOCK_MULTI_SCENARIO_CONTROLLED_SIMULATION"
    REQUIRE_PERFORMANCE_RISK_VALIDATION_FIXES = "REQUIRE_PERFORMANCE_RISK_VALIDATION_FIXES"
    REQUIRE_SCENARIO_SUITE_FIXES = "REQUIRE_SCENARIO_SUITE_FIXES"
    REQUIRE_SCENARIO_EXECUTION_FIXES = "REQUIRE_SCENARIO_EXECUTION_FIXES"
    REQUIRE_METRIC_AGGREGATION_FIXES = "REQUIRE_METRIC_AGGREGATION_FIXES"
    REQUIRE_ROBUSTNESS_FIXES = "REQUIRE_ROBUSTNESS_FIXES"
    REQUIRE_RISK_REDUCTION = "REQUIRE_RISK_REDUCTION"
    APPROVE_MULTI_SCENARIO_CONTROLLED_SIMULATION = "APPROVE_MULTI_SCENARIO_CONTROLLED_SIMULATION"


class MultiScenarioControlledSimulationRisk(StrEnum):
    PERFORMANCE_RISK_VALIDATION_NOT_APPROVED = "PERFORMANCE_RISK_VALIDATION_NOT_APPROVED"
    SCENARIO_SUITE_EMPTY = "SCENARIO_SUITE_EMPTY"
    SCENARIO_DEFINITION_INVALID = "SCENARIO_DEFINITION_INVALID"
    WINNING_SCENARIO_MISSING = "WINNING_SCENARIO_MISSING"
    LOSING_SCENARIO_MISSING = "LOSING_SCENARIO_MISSING"
    FLAT_SCENARIO_MISSING = "FLAT_SCENARIO_MISSING"
    DRAWDOWN_SCENARIO_MISSING = "DRAWDOWN_SCENARIO_MISSING"
    VOLATILE_SCENARIO_MISSING = "VOLATILE_SCENARIO_MISSING"
    STOP_CONDITION_SCENARIO_MISSING = "STOP_CONDITION_SCENARIO_MISSING"
    RISK_VIOLATION_SCENARIO_MISSING = "RISK_VIOLATION_SCENARIO_MISSING"
    POSITION_INCONSISTENCY_SCENARIO_MISSING = "POSITION_INCONSISTENCY_SCENARIO_MISSING"
    SCENARIO_EXECUTION_FAILED = "SCENARIO_EXECUTION_FAILED"
    METRIC_AGGREGATION_INVALID = "METRIC_AGGREGATION_INVALID"
    ROBUSTNESS_SCORE_WEAK = "ROBUSTNESS_SCORE_WEAK"
    MULTI_SCENARIO_DRAWDOWN_TOO_HIGH = "MULTI_SCENARIO_DRAWDOWN_TOO_HIGH"
    MULTI_SCENARIO_LOSS_LIMIT_BREACHED = "MULTI_SCENARIO_LOSS_LIMIT_BREACHED"
    REAL_EXECUTION_BOUNDARY_VIOLATION = "REAL_EXECUTION_BOUNDARY_VIOLATION"
    DATA_ACCESS_VIOLATION = "DATA_ACCESS_VIOLATION"
    PREMATURE_MULTI_SCENARIO_RESULT_REPORT = "PREMATURE_MULTI_SCENARIO_RESULT_REPORT"


class MultiScenarioControlledSimulationRecommendation(StrEnum):
    HOLD_MULTI_SCENARIO_RESULT_REPORT = "HOLD_MULTI_SCENARIO_RESULT_REPORT"
    APPROVE_PERFORMANCE_RISK_VALIDATION_FIRST = "APPROVE_PERFORMANCE_RISK_VALIDATION_FIRST"
    PROVIDE_SCENARIO_SUITE = "PROVIDE_SCENARIO_SUITE"
    FIX_SCENARIO_DEFINITIONS = "FIX_SCENARIO_DEFINITIONS"
    ADD_WINNING_SCENARIO = "ADD_WINNING_SCENARIO"
    ADD_LOSING_SCENARIO = "ADD_LOSING_SCENARIO"
    ADD_FLAT_SCENARIO = "ADD_FLAT_SCENARIO"
    ADD_DRAWDOWN_SCENARIO = "ADD_DRAWDOWN_SCENARIO"
    ADD_VOLATILE_SCENARIO = "ADD_VOLATILE_SCENARIO"
    ADD_STOP_CONDITION_SCENARIO = "ADD_STOP_CONDITION_SCENARIO"
    ADD_RISK_VIOLATION_SCENARIO = "ADD_RISK_VIOLATION_SCENARIO"
    ADD_POSITION_INCONSISTENCY_SCENARIO = "ADD_POSITION_INCONSISTENCY_SCENARIO"
    FIX_SCENARIO_EXECUTION = "FIX_SCENARIO_EXECUTION"
    REBUILD_METRIC_AGGREGATION = "REBUILD_METRIC_AGGREGATION"
    IMPROVE_MULTI_SCENARIO_ROBUSTNESS = "IMPROVE_MULTI_SCENARIO_ROBUSTNESS"
    REDUCE_MULTI_SCENARIO_DRAWDOWN = "REDUCE_MULTI_SCENARIO_DRAWDOWN"
    REDUCE_MULTI_SCENARIO_LOSS = "REDUCE_MULTI_SCENARIO_LOSS"
    RESTORE_REAL_EXECUTION_BOUNDARIES = "RESTORE_REAL_EXECUTION_BOUNDARIES"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    DELAY_MULTI_SCENARIO_RESULT_REPORT = "DELAY_MULTI_SCENARIO_RESULT_REPORT"
    RUN_MULTI_SCENARIO_CONTROLLED_SIMULATION_SUITE = "RUN_MULTI_SCENARIO_CONTROLLED_SIMULATION_SUITE"
    APPROVE_MULTI_SCENARIO_RESULT_REPORT = "APPROVE_MULTI_SCENARIO_RESULT_REPORT"


@dataclass(frozen=True)
class ControlledSimulationScenarioDefinition:
    scenario_id: str
    scenario_type: ControlledSimulationScenarioType
    symbol: str = "SIM"
    initial_equity: float = 100_000.0
    market_path: tuple[OfflineSyntheticMarketBar | dict[str, Any], ...] = ()
    signal_sequence: tuple[OfflineSignalEvent | dict[str, Any], ...] = ()
    max_steps: int | None = 100
    max_order_quantity: float | None = 10.0
    max_position_quantity: float | None = 10.0
    max_drawdown_fraction: float | None = 0.25
    max_loss_amount: float | None = 10_000.0
    commission_per_fill: float = 0.0
    slippage_per_unit: float = 0.0
    require_flat_final_position: bool = True
    stop_conditions_required: bool = True
    allow_open_final_position: bool = False
    description: str = ""


@dataclass(frozen=True)
class MultiScenarioFailureFinding:
    scenario_id: str
    scenario_type: ControlledSimulationScenarioType
    failure: str
    risks: tuple[MultiScenarioControlledSimulationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class MultiScenarioRobustnessFinding:
    name: str
    passed: bool
    score: int
    risks: tuple[MultiScenarioControlledSimulationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class ControlledSimulationScenarioResult:
    scenario_id: str
    scenario_type: ControlledSimulationScenarioType
    passed: bool
    runner_result: Any = None
    pnl: float = 0.0
    max_drawdown: float = 0.0
    max_drawdown_fraction: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    expectancy: float = 0.0
    trade_count: int = 0
    final_position_quantity: float = 0.0
    risks: tuple[Any, ...] = ()
    failures: tuple[MultiScenarioFailureFinding, ...] = ()


@dataclass(frozen=True)
class MultiScenarioMetricSummary:
    scenario_count: int = 0
    passed_scenario_count: int = 0
    failed_scenario_count: int = 0
    total_pnl: float = 0.0
    average_pnl: float = 0.0
    max_drawdown: float = 0.0
    max_drawdown_fraction: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    expectancy: float = 0.0
    trade_count: int = 0
    loss_scenario_count: int = 0
    drawdown_breach_count: int = 0
    risk_violation_count: int = 0
    position_inconsistency_count: int = 0
    stability_score: int = 0
    robustness_score: int = 0


@dataclass(frozen=True)
class MultiScenarioAggregateReport:
    metric_summary: MultiScenarioMetricSummary = field(default_factory=MultiScenarioMetricSummary)
    scenario_results: tuple[ControlledSimulationScenarioResult, ...] = ()
    robustness_findings: tuple[MultiScenarioRobustnessFinding, ...] = ()
    failure_findings: tuple[MultiScenarioFailureFinding, ...] = ()


@dataclass(frozen=True)
class MultiScenarioControlledSimulationScore:
    overall_score: int
    validation_gate_score: int
    scenario_suite_score: int
    scenario_execution_score: int
    metric_aggregation_score: int
    robustness_score: int
    risk_control_score: int
    boundary_score: int


@dataclass(frozen=True)
class MultiScenarioControlledSimulationInput:
    performance_risk_validation_gate: Any = None
    performance_metrics_result: Any = None
    risk_metrics_result: Any = None
    controlled_simulation_result_report: Any = None
    controlled_simulation_offline_runner_result: Any = None
    offline_simulation_metrics: Any = None
    offline_equity_point: Any = None
    offline_position_state: Any = None
    offline_stop_condition_result: Any = None
    paper_runtime_forward_test_plan: Any = None
    official_paper_validation_report: Any = None
    paper_runtime_validation: Any = None
    paper_trading_runtime: Any = None
    observability_verification: Any = None
    rollback_verification: Any = None
    kill_switch_verification: Any = None
    human_validated_paper_session: Any = None
    supervised_paper_session: Any = None
    performance_risk_validation_approved: bool | None = None
    scenario_suite: tuple[ControlledSimulationScenarioDefinition | dict[str, Any], ...] | None = None
    min_robustness_score: int = 60
    max_drawdown_fraction: float = 0.25
    max_loss_amount: float = 10_000.0
    max_failed_scenarios: int = 0
    multi_scenario_result_report_requested: bool | None = False
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
class MultiScenarioControlledSimulationResult:
    state: MultiScenarioControlledSimulationState
    decision: MultiScenarioControlledSimulationDecision
    simulation_score: int
    score_breakdown: MultiScenarioControlledSimulationScore
    risks: tuple[MultiScenarioControlledSimulationRisk, ...] = ()
    recommendations: tuple[MultiScenarioControlledSimulationRecommendation, ...] = ()
    scenario_suite: tuple[ControlledSimulationScenarioDefinition, ...] = ()
    scenario_results: tuple[ControlledSimulationScenarioResult, ...] = ()
    aggregate_report: MultiScenarioAggregateReport = field(default_factory=MultiScenarioAggregateReport)
    metric_summary: MultiScenarioMetricSummary = field(default_factory=MultiScenarioMetricSummary)
    failures: tuple[MultiScenarioFailureFinding, ...] = ()
    robustness_findings: tuple[MultiScenarioRobustnessFinding, ...] = ()
    offline_only: bool = True
    summary: str = ""
