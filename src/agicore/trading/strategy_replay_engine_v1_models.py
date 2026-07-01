"""Models for deterministic in-memory strategy replay engine v1."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class StrategyReplayStrategyTypeV1(StrEnum):
    MOVING_AVERAGE_CROSSOVER = "MOVING_AVERAGE_CROSSOVER"
    BREAKOUT = "BREAKOUT"
    MEAN_REVERSION = "MEAN_REVERSION"


class StrategyReplayEngineV1State(StrEnum):
    NOT_READY = "NOT_READY"
    STRATEGY_REPLAY_ENGINE_V1_INPUT_INVALID = "STRATEGY_REPLAY_ENGINE_V1_INPUT_INVALID"
    STRATEGY_REPLAY_ENGINE_V1_BLOCKED = "STRATEGY_REPLAY_ENGINE_V1_BLOCKED"
    STRATEGY_REPLAY_ENGINE_V1_COMPLETED_WITH_WARNINGS = "STRATEGY_REPLAY_ENGINE_V1_COMPLETED_WITH_WARNINGS"
    STRATEGY_REPLAY_ENGINE_V1_COMPLETED = "STRATEGY_REPLAY_ENGINE_V1_COMPLETED"
    READY_FOR_AGICORE_TRADING_V1_CANDIDATE = "READY_FOR_AGICORE_TRADING_V1_CANDIDATE"


class StrategyReplayEngineV1Decision(StrEnum):
    BLOCK_STRATEGY_REPLAY_ENGINE_V1 = "BLOCK_STRATEGY_REPLAY_ENGINE_V1"
    REQUIRE_STRATEGY_REPLAY_INPUT_FIXES = "REQUIRE_STRATEGY_REPLAY_INPUT_FIXES"
    REQUIRE_STRATEGY_REPLAY_BARS_FIXES = "REQUIRE_STRATEGY_REPLAY_BARS_FIXES"
    REQUIRE_STRATEGY_SIGNAL_FIXES = "REQUIRE_STRATEGY_SIGNAL_FIXES"
    REQUIRE_STRATEGY_READ_ONLY_DECISION_FIXES = "REQUIRE_STRATEGY_READ_ONLY_DECISION_FIXES"
    REQUIRE_STRATEGY_RISK_GUARD_FIXES = "REQUIRE_STRATEGY_RISK_GUARD_FIXES"
    REQUIRE_STRATEGY_BROKER_PREVIEW_FIXES = "REQUIRE_STRATEGY_BROKER_PREVIEW_FIXES"
    REQUIRE_STRATEGY_JOURNAL_FIXES = "REQUIRE_STRATEGY_JOURNAL_FIXES"
    REQUIRE_STRATEGY_METRICS_FIXES = "REQUIRE_STRATEGY_METRICS_FIXES"
    REQUIRE_STRATEGY_REPORT_FIXES = "REQUIRE_STRATEGY_REPORT_FIXES"
    APPROVE_STRATEGY_REPLAY_ENGINE_V1 = "APPROVE_STRATEGY_REPLAY_ENGINE_V1"


class StrategyReplayEngineV1Risk(StrEnum):
    STRATEGY_REPLAY_INPUT_MISSING = "STRATEGY_REPLAY_INPUT_MISSING"
    STRATEGY_REPLAY_BARS_EMPTY = "STRATEGY_REPLAY_BARS_EMPTY"
    STRATEGY_REPLAY_BAR_INVALID = "STRATEGY_REPLAY_BAR_INVALID"
    STRATEGY_REPLAY_STRATEGY_UNSUPPORTED = "STRATEGY_REPLAY_STRATEGY_UNSUPPORTED"
    STRATEGY_REPLAY_SIGNAL_INVALID = "STRATEGY_REPLAY_SIGNAL_INVALID"
    STRATEGY_REPLAY_READ_ONLY_DECISION_INVALID = "STRATEGY_REPLAY_READ_ONLY_DECISION_INVALID"
    STRATEGY_REPLAY_RISK_GUARD_FAILED = "STRATEGY_REPLAY_RISK_GUARD_FAILED"
    STRATEGY_REPLAY_BROKER_PREVIEW_FAILED = "STRATEGY_REPLAY_BROKER_PREVIEW_FAILED"
    STRATEGY_REPLAY_JOURNAL_MISSING = "STRATEGY_REPLAY_JOURNAL_MISSING"
    STRATEGY_REPLAY_METRICS_MISSING = "STRATEGY_REPLAY_METRICS_MISSING"
    STRATEGY_REPLAY_REPORT_MISSING = "STRATEGY_REPLAY_REPORT_MISSING"
    FILE_READ_BOUNDARY_VIOLATION = "FILE_READ_BOUNDARY_VIOLATION"
    FILE_WRITE_BOUNDARY_VIOLATION = "FILE_WRITE_BOUNDARY_VIOLATION"
    REAL_DATA_ACCESS_BOUNDARY_VIOLATION = "REAL_DATA_ACCESS_BOUNDARY_VIOLATION"
    DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION = "DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION"
    REAL_BROKER_BOUNDARY_VIOLATION = "REAL_BROKER_BOUNDARY_VIOLATION"
    REAL_SECRET_BOUNDARY_VIOLATION = "REAL_SECRET_BOUNDARY_VIOLATION"
    NETWORK_BOUNDARY_VIOLATION = "NETWORK_BOUNDARY_VIOLATION"
    ORDER_EXECUTION_BOUNDARY_VIOLATION = "ORDER_EXECUTION_BOUNDARY_VIOLATION"
    ACCOUNT_ACCESS_BOUNDARY_VIOLATION = "ACCOUNT_ACCESS_BOUNDARY_VIOLATION"
    POSITION_MUTATION_BOUNDARY_VIOLATION = "POSITION_MUTATION_BOUNDARY_VIOLATION"


class StrategyReplayEngineV1Recommendation(StrEnum):
    PROVIDE_STRATEGY_REPLAY_INPUT = "PROVIDE_STRATEGY_REPLAY_INPUT"
    PROVIDE_STRATEGY_REPLAY_BARS = "PROVIDE_STRATEGY_REPLAY_BARS"
    FIX_STRATEGY_REPLAY_BARS = "FIX_STRATEGY_REPLAY_BARS"
    USE_SUPPORTED_STRATEGY = "USE_SUPPORTED_STRATEGY"
    FIX_STRATEGY_SIGNAL = "FIX_STRATEGY_SIGNAL"
    KEEP_DECISION_READ_ONLY = "KEEP_DECISION_READ_ONLY"
    FIX_STRATEGY_RISK_GUARDS = "FIX_STRATEGY_RISK_GUARDS"
    FIX_STRATEGY_BROKER_PREVIEW = "FIX_STRATEGY_BROKER_PREVIEW"
    WRITE_STRATEGY_REPLAY_JOURNAL = "WRITE_STRATEGY_REPLAY_JOURNAL"
    COMPUTE_STRATEGY_REPLAY_METRICS = "COMPUTE_STRATEGY_REPLAY_METRICS"
    GENERATE_STRATEGY_REPLAY_REPORT = "GENERATE_STRATEGY_REPLAY_REPORT"
    REMOVE_FILE_READ = "REMOVE_FILE_READ"
    REMOVE_FILE_WRITE = "REMOVE_FILE_WRITE"
    REMOVE_REAL_DATA_ACCESS = "REMOVE_REAL_DATA_ACCESS"
    REMOVE_DATA_DIRECTORY_ACCESS = "REMOVE_DATA_DIRECTORY_ACCESS"
    REMOVE_REAL_BROKER_ACCESS = "REMOVE_REAL_BROKER_ACCESS"
    REMOVE_REAL_SECRET_ACCESS = "REMOVE_REAL_SECRET_ACCESS"
    REMOVE_NETWORK_ACCESS = "REMOVE_NETWORK_ACCESS"
    REMOVE_ORDER_EXECUTION = "REMOVE_ORDER_EXECUTION"
    REMOVE_ACCOUNT_ACCESS = "REMOVE_ACCOUNT_ACCESS"
    REMOVE_POSITION_MUTATION = "REMOVE_POSITION_MUTATION"
    RUN_STRATEGY_REPLAY_ENGINE_V1_TEST_SUITE = "RUN_STRATEGY_REPLAY_ENGINE_V1_TEST_SUITE"
    APPROVE_AGICORE_TRADING_V1_CANDIDATE = "APPROVE_AGICORE_TRADING_V1_CANDIDATE"


@dataclass(frozen=True)
class StrategyReplayContextV1:
    run_id: str
    symbol: str
    strategy_type: StrategyReplayStrategyTypeV1 | str
    bar_count: int
    deterministic: bool = True
    offline_only: bool = True
    in_memory_only: bool = True


@dataclass(frozen=True)
class StrategyReplayBarV1:
    index: int
    timestamp: str
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class StrategyReplaySignalV1:
    symbol: str
    strategy_type: StrategyReplayStrategyTypeV1 | str
    action: str
    confidence: float
    reference_price: float
    reason: str
    read_only: bool = True


@dataclass(frozen=True)
class StrategyReplayReadOnlyDecisionV1:
    symbol: str
    action: str
    proposed_position_size: float
    reference_price: float
    reason: str
    read_only: bool = True
    order_submitted: bool = False
    position_mutated: bool = False


@dataclass(frozen=True)
class StrategyReplayRiskResultV1:
    passed: bool
    risks: tuple[StrategyReplayEngineV1Risk, ...] = ()
    reasons: tuple[str, ...] = ()
    risk_guard_result: Any = None


@dataclass(frozen=True)
class StrategyReplayBrokerPreviewV1:
    accepted: bool
    status: str
    notional: float
    reason: str
    read_only: bool = True
    order_submitted: bool = False
    real_order: bool = False
    position_mutation: bool = False
    broker_result: Any = None


@dataclass(frozen=True)
class StrategyReplayJournalResultV1:
    entry_count: int
    warning_count: int
    blocked_count: int
    complete: bool
    journal_result: Any = None


@dataclass(frozen=True)
class StrategyReplayMetricsV1:
    bar_count: int
    strategy_used: str
    final_signal: str
    final_decision: str
    risk_guard_passed: bool
    broker_preview_status: str
    journal_entry_count: int
    warnings_count: int
    blocked_count: int


@dataclass(frozen=True)
class StrategyReplayEngineV1Score:
    overall_score: int
    input_score: int
    bar_score: int
    signal_score: int
    decision_score: int
    risk_score: int
    broker_score: int
    journal_score: int
    metrics_score: int
    report_score: int
    boundary_score: int


@dataclass(frozen=True)
class StrategyReplayReportV1:
    markdown: str
    json: str


@dataclass(frozen=True)
class StrategyReplayEngineV1Input:
    bars: tuple[Any, ...] = ()
    strategy_type: StrategyReplayStrategyTypeV1 | str = StrategyReplayStrategyTypeV1.MOVING_AVERAGE_CROSSOVER
    run_id: str = "strategy-replay-v1"
    symbol: str = "SIM"
    requested_quantity: float = 5.0
    available_cash: float = 100_000.0
    margin_usage: float = 0.01
    daily_loss: float = 0.0
    drawdown: float = 0.0
    short_window: int = 2
    long_window: int = 3
    breakout_window: int = 3
    mean_reversion_window: int = 3
    max_position_size: float = 10.0
    max_notional_exposure: float = 10_000.0
    force_signal_invalid: bool = False
    force_read_only_decision_invalid: bool = False
    force_risk_guard_failed: bool = False
    force_broker_preview_failed: bool = False
    force_journal_missing: bool = False
    force_metrics_missing: bool = False
    force_report_missing: bool = False
    offline_mode_enforced: bool = True
    sandbox_mode_enforced: bool = True
    in_memory_only: bool = True
    replay_in_memory_only: bool = True
    no_file_read: bool = True
    no_file_write: bool = True
    no_real_data_access: bool = True
    no_data_directory_read: bool = True
    no_data_directory_write: bool = True
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
    file_read_requested: bool = False
    file_write_requested: bool = False
    real_data_access_requested: bool = False
    data_directory_read_requested: bool = False
    data_directory_write_requested: bool = False
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


@dataclass(frozen=True)
class StrategyReplayEngineV1Result:
    state: StrategyReplayEngineV1State
    decision: StrategyReplayEngineV1Decision
    score: StrategyReplayEngineV1Score
    risks: tuple[StrategyReplayEngineV1Risk, ...]
    recommendations: tuple[StrategyReplayEngineV1Recommendation, ...]
    context: StrategyReplayContextV1 | None = None
    bars: tuple[StrategyReplayBarV1, ...] = ()
    signal: StrategyReplaySignalV1 | None = None
    read_only_decision: StrategyReplayReadOnlyDecisionV1 | None = None
    risk_result: StrategyReplayRiskResultV1 | None = None
    broker_preview: StrategyReplayBrokerPreviewV1 | None = None
    journal: StrategyReplayJournalResultV1 | None = None
    metrics: StrategyReplayMetricsV1 | None = None
    report: StrategyReplayReportV1 | None = None
    offline_only: bool = True
    in_memory_only: bool = True
    file_read: bool = False
    file_written: bool = False
    data_accessed: bool = False
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False
    next_phase: str = "AGICORE_TRADING_V1_CANDIDATE"
