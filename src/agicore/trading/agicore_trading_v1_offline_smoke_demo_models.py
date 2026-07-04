"""Models for AGIcore Trading v1 offline smoke demo."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class AGIcoreTradingV1OfflineSmokeDemoState(StrEnum):
    NOT_READY = "NOT_READY"
    AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_INPUT_INVALID = "AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_INPUT_INVALID"
    AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_BLOCKED = "AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_BLOCKED"
    AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_COMPLETED_WITH_WARNINGS = (
        "AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_COMPLETED_WITH_WARNINGS"
    )
    AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_COMPLETED = "AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_COMPLETED"
    READY_FOR_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_REVIEW = (
        "READY_FOR_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_REVIEW"
    )


class AGIcoreTradingV1OfflineSmokeDemoDecision(StrEnum):
    BLOCK_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO = "BLOCK_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO"
    REQUIRE_SMOKE_DEMO_INPUT_FIXES = "REQUIRE_SMOKE_DEMO_INPUT_FIXES"
    REQUIRE_SMOKE_DEMO_CSV_REPLAY_FIXES = "REQUIRE_SMOKE_DEMO_CSV_REPLAY_FIXES"
    REQUIRE_SMOKE_DEMO_STRATEGY_REPLAY_FIXES = "REQUIRE_SMOKE_DEMO_STRATEGY_REPLAY_FIXES"
    REQUIRE_SMOKE_DEMO_RISK_GUARD_FIXES = "REQUIRE_SMOKE_DEMO_RISK_GUARD_FIXES"
    REQUIRE_SMOKE_DEMO_BROKER_PREVIEW_FIXES = "REQUIRE_SMOKE_DEMO_BROKER_PREVIEW_FIXES"
    REQUIRE_SMOKE_DEMO_JOURNAL_FIXES = "REQUIRE_SMOKE_DEMO_JOURNAL_FIXES"
    REQUIRE_SMOKE_DEMO_REPORT_FIXES = "REQUIRE_SMOKE_DEMO_REPORT_FIXES"
    REQUIRE_SMOKE_DEMO_BOUNDARY_FIXES = "REQUIRE_SMOKE_DEMO_BOUNDARY_FIXES"
    APPROVE_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO = "APPROVE_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO"


class AGIcoreTradingV1OfflineSmokeDemoRisk(StrEnum):
    SMOKE_DEMO_INPUT_MISSING = "SMOKE_DEMO_INPUT_MISSING"
    SMOKE_DEMO_CSV_REPLAY_FAILED = "SMOKE_DEMO_CSV_REPLAY_FAILED"
    SMOKE_DEMO_STRATEGY_REPLAY_FAILED = "SMOKE_DEMO_STRATEGY_REPLAY_FAILED"
    SMOKE_DEMO_RISK_GUARD_FAILED = "SMOKE_DEMO_RISK_GUARD_FAILED"
    SMOKE_DEMO_BROKER_PREVIEW_FAILED = "SMOKE_DEMO_BROKER_PREVIEW_FAILED"
    SMOKE_DEMO_JOURNAL_FAILED = "SMOKE_DEMO_JOURNAL_FAILED"
    SMOKE_DEMO_REPORT_FAILED = "SMOKE_DEMO_REPORT_FAILED"
    SMOKE_DEMO_END_TO_END_VALIDATION_FAILED = "SMOKE_DEMO_END_TO_END_VALIDATION_FAILED"
    LIVE_TRADING_READINESS_OVERCLAIM = "LIVE_TRADING_READINESS_OVERCLAIM"
    REAL_BROKER_READINESS_OVERCLAIM = "REAL_BROKER_READINESS_OVERCLAIM"
    REAL_ORDER_EXECUTION_OVERCLAIM = "REAL_ORDER_EXECUTION_OVERCLAIM"
    PROFITABILITY_PROOF_OVERCLAIM = "PROFITABILITY_PROOF_OVERCLAIM"
    FINANCIAL_ADVICE_OVERCLAIM = "FINANCIAL_ADVICE_OVERCLAIM"
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


class AGIcoreTradingV1OfflineSmokeDemoRecommendation(StrEnum):
    PROVIDE_SMOKE_DEMO_INPUT = "PROVIDE_SMOKE_DEMO_INPUT"
    FIX_SMOKE_DEMO_CSV_REPLAY = "FIX_SMOKE_DEMO_CSV_REPLAY"
    FIX_SMOKE_DEMO_STRATEGY_REPLAY = "FIX_SMOKE_DEMO_STRATEGY_REPLAY"
    FIX_SMOKE_DEMO_RISK_GUARD = "FIX_SMOKE_DEMO_RISK_GUARD"
    FIX_SMOKE_DEMO_BROKER_PREVIEW = "FIX_SMOKE_DEMO_BROKER_PREVIEW"
    FIX_SMOKE_DEMO_JOURNAL = "FIX_SMOKE_DEMO_JOURNAL"
    FIX_SMOKE_DEMO_REPORT = "FIX_SMOKE_DEMO_REPORT"
    FIX_SMOKE_DEMO_END_TO_END_VALIDATION = "FIX_SMOKE_DEMO_END_TO_END_VALIDATION"
    REMOVE_LIVE_TRADING_READINESS_CLAIM = "REMOVE_LIVE_TRADING_READINESS_CLAIM"
    REMOVE_REAL_BROKER_READINESS_CLAIM = "REMOVE_REAL_BROKER_READINESS_CLAIM"
    REMOVE_REAL_ORDER_EXECUTION_CLAIM = "REMOVE_REAL_ORDER_EXECUTION_CLAIM"
    REMOVE_PROFITABILITY_PROOF_CLAIM = "REMOVE_PROFITABILITY_PROOF_CLAIM"
    REMOVE_FINANCIAL_ADVICE_CLAIM = "REMOVE_FINANCIAL_ADVICE_CLAIM"
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
    RUN_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_TEST_SUITE = (
        "RUN_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_TEST_SUITE"
    )
    APPROVE_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_REVIEW = (
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_REVIEW"
    )


class AGIcoreTradingV1OfflineSmokeDemoStepStatus(StrEnum):
    NOT_RUN = "NOT_RUN"
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineSmokeDemoContext:
    run_id: str
    symbol: str
    strategy_type: str
    deterministic: bool = True
    offline_only: bool = True
    in_memory_only: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineSmokeDemoStep:
    name: str
    status: AGIcoreTradingV1OfflineSmokeDemoStepStatus
    message: str
    risks: tuple[AGIcoreTradingV1OfflineSmokeDemoRisk, ...] = ()
    payload: Any = None


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineSmokeDemoMetrics:
    expected_step_count: int
    passed_step_count: int
    failed_step_count: int
    read_only_decision: bool
    broker_preview_read_only: bool
    journal_entry_count: int
    markdown_report_present: bool
    json_report_present: bool
    final_decision: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineSmokeDemoScore:
    overall_score: int
    input_score: int
    step_score: int
    read_only_score: int
    report_score: int
    overclaim_score: int
    boundary_score: int


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineSmokeDemoReport:
    markdown: str
    json: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineSmokeDemoInput:
    run_id: str = "agicore-trading-v1-offline-smoke-demo"
    symbol: str = "SIM"
    strategy_type: str = "MOVING_AVERAGE_CROSSOVER"
    force_csv_replay_failed: bool = False
    force_strategy_replay_failed: bool = False
    force_risk_guard_failed: bool = False
    force_broker_preview_failed: bool = False
    force_journal_failed: bool = False
    force_report_failed: bool = False
    force_end_to_end_validation_failed: bool = False
    force_live_trading_overclaim: bool = False
    force_real_broker_overclaim: bool = False
    force_real_order_overclaim: bool = False
    force_profitability_overclaim: bool = False
    force_financial_advice_overclaim: bool = False
    offline_mode_enforced: bool = True
    sandbox_mode_enforced: bool = True
    in_memory_only: bool = True
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
class AGIcoreTradingV1OfflineSmokeDemoResult:
    state: AGIcoreTradingV1OfflineSmokeDemoState
    decision: AGIcoreTradingV1OfflineSmokeDemoDecision
    score: AGIcoreTradingV1OfflineSmokeDemoScore
    risks: tuple[AGIcoreTradingV1OfflineSmokeDemoRisk, ...]
    recommendations: tuple[AGIcoreTradingV1OfflineSmokeDemoRecommendation, ...]
    context: AGIcoreTradingV1OfflineSmokeDemoContext | None = None
    steps: tuple[AGIcoreTradingV1OfflineSmokeDemoStep, ...] = ()
    metrics: AGIcoreTradingV1OfflineSmokeDemoMetrics | None = None
    report: AGIcoreTradingV1OfflineSmokeDemoReport | None = None
    csv_replay_result: Any = None
    strategy_replay_result: Any = None
    risk_guard_result: Any = None
    broker_preview_result: Any = None
    journal_result: Any = None
    offline_report_result: Any = None
    offline_only: bool = True
    in_memory_only: bool = True
    file_read: bool = False
    file_written: bool = False
    data_accessed: bool = False
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False
    next_phase: str = "AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_REVIEW"
