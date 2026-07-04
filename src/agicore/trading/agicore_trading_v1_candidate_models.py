"""Models for AGIcore Trading v1 offline candidate evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class AGIcoreTradingV1CapabilityName(StrEnum):
    CSV_REPLAY_INPUT = "CSV_REPLAY_INPUT"
    SYNTHETIC_MARKET_SCENARIO = "SYNTHETIC_MARKET_SCENARIO"
    STRATEGY_REPLAY_ENGINE = "STRATEGY_REPLAY_ENGINE"
    SIMULATED_BROKER_STUB = "SIMULATED_BROKER_STUB"
    RISK_GUARD_ENFORCEMENT = "RISK_GUARD_ENFORCEMENT"
    JOURNAL_WRITER = "JOURNAL_WRITER"
    OFFLINE_REPORT_MARKDOWN_JSON = "OFFLINE_REPORT_MARKDOWN_JSON"


class AGIcoreTradingV1CandidateState(StrEnum):
    NOT_READY = "NOT_READY"
    AGICORE_TRADING_V1_CANDIDATE_INPUT_INVALID = "AGICORE_TRADING_V1_CANDIDATE_INPUT_INVALID"
    AGICORE_TRADING_V1_CANDIDATE_BLOCKED = "AGICORE_TRADING_V1_CANDIDATE_BLOCKED"
    AGICORE_TRADING_V1_CANDIDATE_COMPLETED_WITH_WARNINGS = "AGICORE_TRADING_V1_CANDIDATE_COMPLETED_WITH_WARNINGS"
    AGICORE_TRADING_V1_CANDIDATE_COMPLETED = "AGICORE_TRADING_V1_CANDIDATE_COMPLETED"
    READY_FOR_AGICORE_TRADING_V1_CANDIDATE_REVIEW = "READY_FOR_AGICORE_TRADING_V1_CANDIDATE_REVIEW"


class AGIcoreTradingV1CandidateDecision(StrEnum):
    BLOCK_AGICORE_TRADING_V1_CANDIDATE = "BLOCK_AGICORE_TRADING_V1_CANDIDATE"
    REQUIRE_AGICORE_TRADING_V1_INPUT_FIXES = "REQUIRE_AGICORE_TRADING_V1_INPUT_FIXES"
    REQUIRE_CSV_REPLAY_CAPABILITY_FIXES = "REQUIRE_CSV_REPLAY_CAPABILITY_FIXES"
    REQUIRE_SYNTHETIC_MARKET_CAPABILITY_FIXES = "REQUIRE_SYNTHETIC_MARKET_CAPABILITY_FIXES"
    REQUIRE_STRATEGY_REPLAY_CAPABILITY_FIXES = "REQUIRE_STRATEGY_REPLAY_CAPABILITY_FIXES"
    REQUIRE_SIMULATED_BROKER_CAPABILITY_FIXES = "REQUIRE_SIMULATED_BROKER_CAPABILITY_FIXES"
    REQUIRE_RISK_GUARD_CAPABILITY_FIXES = "REQUIRE_RISK_GUARD_CAPABILITY_FIXES"
    REQUIRE_JOURNAL_CAPABILITY_FIXES = "REQUIRE_JOURNAL_CAPABILITY_FIXES"
    REQUIRE_OFFLINE_REPORT_CAPABILITY_FIXES = "REQUIRE_OFFLINE_REPORT_CAPABILITY_FIXES"
    REQUIRE_V1_SMOKE_REPLAY_FIXES = "REQUIRE_V1_SMOKE_REPLAY_FIXES"
    APPROVE_AGICORE_TRADING_V1_CANDIDATE = "APPROVE_AGICORE_TRADING_V1_CANDIDATE"


class AGIcoreTradingV1CandidateRisk(StrEnum):
    AGICORE_TRADING_V1_INPUT_MISSING = "AGICORE_TRADING_V1_INPUT_MISSING"
    CSV_REPLAY_CAPABILITY_MISSING = "CSV_REPLAY_CAPABILITY_MISSING"
    SYNTHETIC_MARKET_CAPABILITY_MISSING = "SYNTHETIC_MARKET_CAPABILITY_MISSING"
    STRATEGY_REPLAY_CAPABILITY_MISSING = "STRATEGY_REPLAY_CAPABILITY_MISSING"
    SIMULATED_BROKER_CAPABILITY_MISSING = "SIMULATED_BROKER_CAPABILITY_MISSING"
    RISK_GUARD_CAPABILITY_MISSING = "RISK_GUARD_CAPABILITY_MISSING"
    JOURNAL_CAPABILITY_MISSING = "JOURNAL_CAPABILITY_MISSING"
    OFFLINE_REPORT_CAPABILITY_MISSING = "OFFLINE_REPORT_CAPABILITY_MISSING"
    V1_SMOKE_REPLAY_FAILED = "V1_SMOKE_REPLAY_FAILED"
    V1_CANDIDATE_METRICS_MISSING = "V1_CANDIDATE_METRICS_MISSING"
    V1_CANDIDATE_REPORT_MISSING = "V1_CANDIDATE_REPORT_MISSING"
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


class AGIcoreTradingV1CandidateRecommendation(StrEnum):
    PROVIDE_AGICORE_TRADING_V1_INPUT = "PROVIDE_AGICORE_TRADING_V1_INPUT"
    FIX_CSV_REPLAY_CAPABILITY = "FIX_CSV_REPLAY_CAPABILITY"
    FIX_SYNTHETIC_MARKET_CAPABILITY = "FIX_SYNTHETIC_MARKET_CAPABILITY"
    FIX_STRATEGY_REPLAY_CAPABILITY = "FIX_STRATEGY_REPLAY_CAPABILITY"
    FIX_SIMULATED_BROKER_CAPABILITY = "FIX_SIMULATED_BROKER_CAPABILITY"
    FIX_RISK_GUARD_CAPABILITY = "FIX_RISK_GUARD_CAPABILITY"
    FIX_JOURNAL_CAPABILITY = "FIX_JOURNAL_CAPABILITY"
    FIX_OFFLINE_REPORT_CAPABILITY = "FIX_OFFLINE_REPORT_CAPABILITY"
    FIX_V1_SMOKE_REPLAY = "FIX_V1_SMOKE_REPLAY"
    COMPUTE_V1_CANDIDATE_METRICS = "COMPUTE_V1_CANDIDATE_METRICS"
    GENERATE_V1_CANDIDATE_REPORT = "GENERATE_V1_CANDIDATE_REPORT"
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
    RUN_AGICORE_TRADING_V1_CANDIDATE_TEST_SUITE = "RUN_AGICORE_TRADING_V1_CANDIDATE_TEST_SUITE"
    APPROVE_AGICORE_TRADING_V1_CANDIDATE_REVIEW = "APPROVE_AGICORE_TRADING_V1_CANDIDATE_REVIEW"


@dataclass(frozen=True)
class AGIcoreTradingV1CandidateContext:
    candidate_id: str
    version: str
    capability_count: int
    deterministic: bool = True
    offline_only: bool = True
    in_memory_only: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1CapabilityCheck:
    capability: AGIcoreTradingV1CapabilityName | str
    passed: bool
    detail: str
    component_decision: str = ""
    risks: tuple[str, ...] = ()


@dataclass(frozen=True)
class AGIcoreTradingV1SmokeReplayResult:
    passed: bool
    status: str
    strategy_decision: str
    strategy_state: str
    score: int
    read_only: bool = True
    offline_only: bool = True
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False
    replay_result: Any = None


@dataclass(frozen=True)
class AGIcoreTradingV1CandidateMetrics:
    expected_capability_count: int
    validated_capability_count: int
    failed_capability_count: int
    smoke_replay_status: str
    global_score: int
    final_decision: str


@dataclass(frozen=True)
class AGIcoreTradingV1CandidateScore:
    overall_score: int
    input_score: int
    capability_score: int
    smoke_replay_score: int
    metrics_score: int
    report_score: int
    boundary_score: int


@dataclass(frozen=True)
class AGIcoreTradingV1CandidateReport:
    markdown: str
    json: str


@dataclass(frozen=True)
class AGIcoreTradingV1CandidateInput:
    candidate_id: str = "agicore-trading-v1-candidate"
    version: str = "v1-offline"
    force_csv_replay_capability_missing: bool = False
    force_synthetic_market_capability_missing: bool = False
    force_strategy_replay_capability_missing: bool = False
    force_simulated_broker_capability_missing: bool = False
    force_risk_guard_capability_missing: bool = False
    force_journal_capability_missing: bool = False
    force_offline_report_capability_missing: bool = False
    force_smoke_replay_failed: bool = False
    force_metrics_missing: bool = False
    force_report_missing: bool = False
    offline_mode_enforced: bool = True
    sandbox_mode_enforced: bool = True
    in_memory_only: bool = True
    candidate_in_memory_only: bool = True
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
class AGIcoreTradingV1CandidateResult:
    state: AGIcoreTradingV1CandidateState
    decision: AGIcoreTradingV1CandidateDecision
    score: AGIcoreTradingV1CandidateScore
    risks: tuple[AGIcoreTradingV1CandidateRisk, ...]
    recommendations: tuple[AGIcoreTradingV1CandidateRecommendation, ...]
    context: AGIcoreTradingV1CandidateContext | None = None
    capability_checks: tuple[AGIcoreTradingV1CapabilityCheck, ...] = ()
    smoke_replay: AGIcoreTradingV1SmokeReplayResult | None = None
    metrics: AGIcoreTradingV1CandidateMetrics | None = None
    report: AGIcoreTradingV1CandidateReport | None = None
    offline_only: bool = True
    in_memory_only: bool = True
    file_read: bool = False
    file_written: bool = False
    data_accessed: bool = False
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False
    next_phase: str = "AGICORE_TRADING_V1_CANDIDATE_REVIEW"
