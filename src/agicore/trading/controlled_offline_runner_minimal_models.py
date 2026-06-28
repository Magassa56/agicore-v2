"""Models for the minimal controlled offline runner."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ControlledOfflineRunnerMinimalState(StrEnum):
    NOT_READY = "NOT_READY"
    CONTROLLED_OFFLINE_RUNNER_INPUT_INVALID = "CONTROLLED_OFFLINE_RUNNER_INPUT_INVALID"
    CONTROLLED_OFFLINE_RUNNER_BLOCKED = "CONTROLLED_OFFLINE_RUNNER_BLOCKED"
    CONTROLLED_OFFLINE_RUNNER_COMPLETED_WITH_WARNINGS = "CONTROLLED_OFFLINE_RUNNER_COMPLETED_WITH_WARNINGS"
    CONTROLLED_OFFLINE_RUNNER_COMPLETED = "CONTROLLED_OFFLINE_RUNNER_COMPLETED"
    READY_FOR_CONTROLLED_OFFLINE_RUNNER_MINIMAL_REVIEW = "READY_FOR_CONTROLLED_OFFLINE_RUNNER_MINIMAL_REVIEW"


class ControlledOfflineRunnerMinimalDecision(StrEnum):
    BLOCK_CONTROLLED_OFFLINE_RUNNER_MINIMAL = "BLOCK_CONTROLLED_OFFLINE_RUNNER_MINIMAL"
    REQUIRE_CONTROLLED_OFFLINE_RUNNER_INPUT_FIXES = "REQUIRE_CONTROLLED_OFFLINE_RUNNER_INPUT_FIXES"
    REQUIRE_CONTROLLED_OFFLINE_MARKET_SCENARIO_FIXES = "REQUIRE_CONTROLLED_OFFLINE_MARKET_SCENARIO_FIXES"
    REQUIRE_CONTROLLED_OFFLINE_ACCOUNT_SNAPSHOT_FIXES = "REQUIRE_CONTROLLED_OFFLINE_ACCOUNT_SNAPSHOT_FIXES"
    REQUIRE_CONTROLLED_OFFLINE_BROKER_SNAPSHOT_FIXES = "REQUIRE_CONTROLLED_OFFLINE_BROKER_SNAPSHOT_FIXES"
    REQUIRE_CONTROLLED_OFFLINE_RISK_GUARD_FIXES = "REQUIRE_CONTROLLED_OFFLINE_RISK_GUARD_FIXES"
    REQUIRE_CONTROLLED_OFFLINE_JOURNAL_FIXES = "REQUIRE_CONTROLLED_OFFLINE_JOURNAL_FIXES"
    REQUIRE_CONTROLLED_OFFLINE_METRICS_FIXES = "REQUIRE_CONTROLLED_OFFLINE_METRICS_FIXES"
    APPROVE_CONTROLLED_OFFLINE_RUNNER_MINIMAL = "APPROVE_CONTROLLED_OFFLINE_RUNNER_MINIMAL"


class ControlledOfflineRunnerMinimalRisk(StrEnum):
    CONTROLLED_OFFLINE_RUNNER_INPUT_MISSING = "CONTROLLED_OFFLINE_RUNNER_INPUT_MISSING"
    CONTROLLED_OFFLINE_MARKET_SCENARIO_EMPTY = "CONTROLLED_OFFLINE_MARKET_SCENARIO_EMPTY"
    CONTROLLED_OFFLINE_MARKET_SCENARIO_INVALID = "CONTROLLED_OFFLINE_MARKET_SCENARIO_INVALID"
    CONTROLLED_OFFLINE_ACCOUNT_SNAPSHOT_INVALID = "CONTROLLED_OFFLINE_ACCOUNT_SNAPSHOT_INVALID"
    CONTROLLED_OFFLINE_BROKER_SNAPSHOT_INVALID = "CONTROLLED_OFFLINE_BROKER_SNAPSHOT_INVALID"
    CONTROLLED_OFFLINE_STRATEGY_SIGNAL_INVALID = "CONTROLLED_OFFLINE_STRATEGY_SIGNAL_INVALID"
    CONTROLLED_OFFLINE_RISK_GUARD_FAILED = "CONTROLLED_OFFLINE_RISK_GUARD_FAILED"
    CONTROLLED_OFFLINE_JOURNAL_MISSING = "CONTROLLED_OFFLINE_JOURNAL_MISSING"
    CONTROLLED_OFFLINE_METRICS_MISSING = "CONTROLLED_OFFLINE_METRICS_MISSING"
    REAL_BROKER_BOUNDARY_VIOLATION = "REAL_BROKER_BOUNDARY_VIOLATION"
    REAL_SECRET_BOUNDARY_VIOLATION = "REAL_SECRET_BOUNDARY_VIOLATION"
    NETWORK_BOUNDARY_VIOLATION = "NETWORK_BOUNDARY_VIOLATION"
    ORDER_EXECUTION_BOUNDARY_VIOLATION = "ORDER_EXECUTION_BOUNDARY_VIOLATION"
    ACCOUNT_ACCESS_BOUNDARY_VIOLATION = "ACCOUNT_ACCESS_BOUNDARY_VIOLATION"
    DATA_ACCESS_BOUNDARY_VIOLATION = "DATA_ACCESS_BOUNDARY_VIOLATION"


class ControlledOfflineRunnerMinimalRecommendation(StrEnum):
    PROVIDE_CONTROLLED_OFFLINE_RUNNER_INPUT = "PROVIDE_CONTROLLED_OFFLINE_RUNNER_INPUT"
    PROVIDE_SYNTHETIC_MARKET_SCENARIO = "PROVIDE_SYNTHETIC_MARKET_SCENARIO"
    FIX_SYNTHETIC_MARKET_SCENARIO = "FIX_SYNTHETIC_MARKET_SCENARIO"
    FIX_SIMULATED_ACCOUNT_SNAPSHOT = "FIX_SIMULATED_ACCOUNT_SNAPSHOT"
    FIX_SIMULATED_BROKER_SNAPSHOT = "FIX_SIMULATED_BROKER_SNAPSHOT"
    FIX_STRATEGY_SIGNAL = "FIX_STRATEGY_SIGNAL"
    FIX_RISK_GUARDS = "FIX_RISK_GUARDS"
    WRITE_IN_MEMORY_JOURNAL = "WRITE_IN_MEMORY_JOURNAL"
    COMPUTE_MINIMAL_METRICS = "COMPUTE_MINIMAL_METRICS"
    RESTORE_OFFLINE_BOUNDARIES = "RESTORE_OFFLINE_BOUNDARIES"
    REMOVE_REAL_SECRET_ACCESS = "REMOVE_REAL_SECRET_ACCESS"
    REMOVE_NETWORK_ACCESS = "REMOVE_NETWORK_ACCESS"
    KEEP_DECISION_READ_ONLY = "KEEP_DECISION_READ_ONLY"
    REMOVE_ACCOUNT_ACCESS = "REMOVE_ACCOUNT_ACCESS"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    RUN_CONTROLLED_OFFLINE_RUNNER_MINIMAL_TEST_SUITE = "RUN_CONTROLLED_OFFLINE_RUNNER_MINIMAL_TEST_SUITE"
    APPROVE_CONTROLLED_OFFLINE_RUNNER_MINIMAL_REVIEW = "APPROVE_CONTROLLED_OFFLINE_RUNNER_MINIMAL_REVIEW"


@dataclass(frozen=True)
class ControlledOfflineSyntheticMarketBar:
    step: int
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0
    timestamp: str = ""


@dataclass(frozen=True)
class ControlledOfflineSyntheticMarketScenario:
    scenario_id: str
    symbol: str
    bars: tuple[ControlledOfflineSyntheticMarketBar, ...]
    deterministic: bool = True
    in_memory_only: bool = True


@dataclass(frozen=True)
class ControlledOfflineSimulatedAccountSnapshot:
    account_id: str
    cash: float
    equity: float
    currency: str = "USD"
    simulated: bool = True
    read_only: bool = True


@dataclass(frozen=True)
class ControlledOfflineSimulatedBrokerSnapshot:
    broker_id: str
    connected: bool
    simulated: bool = True
    read_only: bool = True
    orders_supported: bool = False
    real_broker: bool = False


@dataclass(frozen=True)
class ControlledOfflineStrategySignal:
    symbol: str
    action: str
    confidence: float
    reason: str
    observation_only: bool = True


@dataclass(frozen=True)
class ControlledOfflineRiskGuardResult:
    passed: bool
    max_position_size: float
    proposed_position_size: float
    risks: tuple[ControlledOfflineRunnerMinimalRisk, ...] = ()
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class ControlledOfflineReadOnlyDecision:
    symbol: str
    action: str
    proposed_position_size: float
    reference_price: float
    order_submitted: bool = False
    position_mutated: bool = False
    read_only: bool = True
    reason: str = ""


@dataclass(frozen=True)
class ControlledOfflineJournalEntry:
    step: int
    event_type: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ControlledOfflineRunnerMetrics:
    bar_count: int
    start_price: float
    end_price: float
    price_change: float
    price_change_fraction: float
    proposed_position_size: float
    order_count: int
    real_order_count: int
    account_access_count: int
    data_access_count: int


@dataclass(frozen=True)
class ControlledOfflineRunnerMinimalScore:
    overall_score: int
    input_score: int
    scenario_score: int
    account_score: int
    broker_score: int
    signal_score: int
    risk_guard_score: int
    journal_score: int
    metrics_score: int
    boundary_score: int


@dataclass(frozen=True)
class ControlledOfflineRunnerReport:
    markdown: str
    json: str


@dataclass(frozen=True)
class ControlledOfflineRunnerMinimalInput:
    scenario_id: str = "controlled-offline-minimal"
    symbol: str = "SIM"
    synthetic_market_bars: tuple[ControlledOfflineSyntheticMarketBar | dict[str, Any], ...] | None = None
    account_snapshot: ControlledOfflineSimulatedAccountSnapshot | dict[str, Any] | None = None
    broker_snapshot: ControlledOfflineSimulatedBrokerSnapshot | dict[str, Any] | None = None
    initial_cash: float = 100_000.0
    max_position_size: float = 10.0
    risk_fraction: float = 0.01
    force_strategy_signal_invalid: bool = False
    force_risk_guard_failed: bool = False
    force_journal_missing: bool = False
    force_metrics_missing: bool = False
    offline_mode_enforced: bool = True
    sandbox_mode_enforced: bool = True
    in_memory_only: bool = True
    synthetic_data_only: bool = True
    no_real_broker: bool = True
    no_alpaca_real: bool = True
    no_api_key_read: bool = True
    no_env_var_read: bool = True
    no_hardcoded_secret: bool = True
    no_http_transport: bool = True
    no_websocket_transport: bool = True
    no_socket_transport: bool = True
    no_external_api: bool = True
    no_external_ml: bool = True
    no_external_llm: bool = True
    no_real_order: bool = True
    no_real_account_access: bool = True
    no_position_mutation: bool = True
    no_data_access: bool = True
    broker_connection_requested: bool = False
    api_key_read_requested: bool = False
    env_var_read_requested: bool = False
    network_requested: bool = False
    http_requested: bool = False
    websocket_requested: bool = False
    socket_requested: bool = False
    external_api_requested: bool = False
    order_execution_requested: bool = False
    account_access_requested: bool = False
    position_mutation_requested: bool = False
    data_access_requested: bool = False


@dataclass(frozen=True)
class ControlledOfflineRunnerMinimalResult:
    state: ControlledOfflineRunnerMinimalState
    decision: ControlledOfflineRunnerMinimalDecision
    score: ControlledOfflineRunnerMinimalScore
    risks: tuple[ControlledOfflineRunnerMinimalRisk, ...]
    recommendations: tuple[ControlledOfflineRunnerMinimalRecommendation, ...]
    scenario: ControlledOfflineSyntheticMarketScenario | None = None
    account_snapshot: ControlledOfflineSimulatedAccountSnapshot | None = None
    broker_snapshot: ControlledOfflineSimulatedBrokerSnapshot | None = None
    strategy_signal: ControlledOfflineStrategySignal | None = None
    risk_guard: ControlledOfflineRiskGuardResult | None = None
    read_only_decision: ControlledOfflineReadOnlyDecision | None = None
    journal_entries: tuple[ControlledOfflineJournalEntry, ...] = ()
    metrics: ControlledOfflineRunnerMetrics | None = None
    report: ControlledOfflineRunnerReport | None = None
    offline_only: bool = True
    sandbox_only: bool = True
    in_memory_only: bool = True
    runner_executed: bool = True
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    data_accessed: bool = False
