"""Models for deterministic in-memory offline Markdown/JSON reports v1."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class OfflineReportSectionNameV1(StrEnum):
    SUMMARY = "SUMMARY"
    MARKET_SCENARIO = "MARKET_SCENARIO"
    SIMULATED_BROKER = "SIMULATED_BROKER"
    RISK_GUARDS = "RISK_GUARDS"
    JOURNAL = "JOURNAL"
    METRICS = "METRICS"
    WARNINGS = "WARNINGS"
    NEXT_ACTIONS = "NEXT_ACTIONS"


class OfflineReportMarkdownJsonV1State(StrEnum):
    NOT_READY = "NOT_READY"
    OFFLINE_REPORT_MARKDOWN_JSON_V1_INPUT_INVALID = "OFFLINE_REPORT_MARKDOWN_JSON_V1_INPUT_INVALID"
    OFFLINE_REPORT_MARKDOWN_JSON_V1_BLOCKED = "OFFLINE_REPORT_MARKDOWN_JSON_V1_BLOCKED"
    OFFLINE_REPORT_MARKDOWN_JSON_V1_COMPLETED_WITH_WARNINGS = (
        "OFFLINE_REPORT_MARKDOWN_JSON_V1_COMPLETED_WITH_WARNINGS"
    )
    OFFLINE_REPORT_MARKDOWN_JSON_V1_COMPLETED = "OFFLINE_REPORT_MARKDOWN_JSON_V1_COMPLETED"
    READY_FOR_CSV_REPLAY_INPUT_V1 = "READY_FOR_CSV_REPLAY_INPUT_V1"


class OfflineReportMarkdownJsonV1Decision(StrEnum):
    BLOCK_OFFLINE_REPORT_MARKDOWN_JSON_V1 = "BLOCK_OFFLINE_REPORT_MARKDOWN_JSON_V1"
    REQUIRE_OFFLINE_REPORT_INPUT_FIXES = "REQUIRE_OFFLINE_REPORT_INPUT_FIXES"
    REQUIRE_OFFLINE_REPORT_CONTEXT_FIXES = "REQUIRE_OFFLINE_REPORT_CONTEXT_FIXES"
    REQUIRE_OFFLINE_REPORT_SECTION_FIXES = "REQUIRE_OFFLINE_REPORT_SECTION_FIXES"
    REQUIRE_OFFLINE_REPORT_MARKDOWN_FIXES = "REQUIRE_OFFLINE_REPORT_MARKDOWN_FIXES"
    REQUIRE_OFFLINE_REPORT_JSON_FIXES = "REQUIRE_OFFLINE_REPORT_JSON_FIXES"
    REQUIRE_OFFLINE_REPORT_METRICS_FIXES = "REQUIRE_OFFLINE_REPORT_METRICS_FIXES"
    APPROVE_OFFLINE_REPORT_MARKDOWN_JSON_V1 = "APPROVE_OFFLINE_REPORT_MARKDOWN_JSON_V1"


class OfflineReportMarkdownJsonV1Risk(StrEnum):
    OFFLINE_REPORT_INPUT_MISSING = "OFFLINE_REPORT_INPUT_MISSING"
    OFFLINE_REPORT_CONTEXT_INVALID = "OFFLINE_REPORT_CONTEXT_INVALID"
    OFFLINE_REPORT_SECTION_MISSING = "OFFLINE_REPORT_SECTION_MISSING"
    OFFLINE_REPORT_MARKDOWN_INVALID = "OFFLINE_REPORT_MARKDOWN_INVALID"
    OFFLINE_REPORT_JSON_INVALID = "OFFLINE_REPORT_JSON_INVALID"
    OFFLINE_REPORT_METRICS_MISSING = "OFFLINE_REPORT_METRICS_MISSING"
    FILE_WRITE_BOUNDARY_VIOLATION = "FILE_WRITE_BOUNDARY_VIOLATION"
    REAL_DATA_ACCESS_BOUNDARY_VIOLATION = "REAL_DATA_ACCESS_BOUNDARY_VIOLATION"
    DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION = "DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION"
    REAL_BROKER_BOUNDARY_VIOLATION = "REAL_BROKER_BOUNDARY_VIOLATION"
    REAL_SECRET_BOUNDARY_VIOLATION = "REAL_SECRET_BOUNDARY_VIOLATION"
    NETWORK_BOUNDARY_VIOLATION = "NETWORK_BOUNDARY_VIOLATION"
    ORDER_EXECUTION_BOUNDARY_VIOLATION = "ORDER_EXECUTION_BOUNDARY_VIOLATION"
    ACCOUNT_ACCESS_BOUNDARY_VIOLATION = "ACCOUNT_ACCESS_BOUNDARY_VIOLATION"
    POSITION_MUTATION_BOUNDARY_VIOLATION = "POSITION_MUTATION_BOUNDARY_VIOLATION"


class OfflineReportMarkdownJsonV1Recommendation(StrEnum):
    PROVIDE_OFFLINE_REPORT_INPUT = "PROVIDE_OFFLINE_REPORT_INPUT"
    FIX_OFFLINE_REPORT_CONTEXT = "FIX_OFFLINE_REPORT_CONTEXT"
    PROVIDE_ALL_OFFLINE_REPORT_SECTIONS = "PROVIDE_ALL_OFFLINE_REPORT_SECTIONS"
    FIX_OFFLINE_REPORT_MARKDOWN = "FIX_OFFLINE_REPORT_MARKDOWN"
    FIX_OFFLINE_REPORT_JSON = "FIX_OFFLINE_REPORT_JSON"
    COMPUTE_OFFLINE_REPORT_METRICS = "COMPUTE_OFFLINE_REPORT_METRICS"
    REMOVE_FILE_WRITE = "REMOVE_FILE_WRITE"
    REMOVE_REAL_DATA_ACCESS = "REMOVE_REAL_DATA_ACCESS"
    REMOVE_DATA_DIRECTORY_ACCESS = "REMOVE_DATA_DIRECTORY_ACCESS"
    REMOVE_REAL_BROKER_ACCESS = "REMOVE_REAL_BROKER_ACCESS"
    REMOVE_REAL_SECRET_ACCESS = "REMOVE_REAL_SECRET_ACCESS"
    REMOVE_NETWORK_ACCESS = "REMOVE_NETWORK_ACCESS"
    REMOVE_ORDER_EXECUTION = "REMOVE_ORDER_EXECUTION"
    REMOVE_ACCOUNT_ACCESS = "REMOVE_ACCOUNT_ACCESS"
    REMOVE_POSITION_MUTATION = "REMOVE_POSITION_MUTATION"
    RUN_OFFLINE_REPORT_MARKDOWN_JSON_V1_TEST_SUITE = "RUN_OFFLINE_REPORT_MARKDOWN_JSON_V1_TEST_SUITE"
    APPROVE_CSV_REPLAY_INPUT_V1_PREPARATION = "APPROVE_CSV_REPLAY_INPUT_V1_PREPARATION"


@dataclass(frozen=True)
class OfflineReportContextV1:
    run_id: str
    symbol: str
    decision: str
    score: int
    next_phase: str = "CSV_REPLAY_INPUT_V1"
    deterministic: bool = True
    offline_only: bool = True
    in_memory_only: bool = True


@dataclass(frozen=True)
class OfflineReportSectionV1:
    name: OfflineReportSectionNameV1 | str
    title: str
    lines: tuple[str, ...]
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OfflineReportMarkdownV1:
    content: str


@dataclass(frozen=True)
class OfflineReportJsonV1:
    payload: dict[str, Any]
    serialized: str


@dataclass(frozen=True)
class OfflineReportMetricsV1:
    section_count: int
    warning_count: int
    risk_count: int
    recommendation_count: int
    markdown_length: int
    json_key_count: int
    complete: bool


@dataclass(frozen=True)
class OfflineReportMarkdownJsonV1Score:
    overall_score: int
    input_score: int
    context_score: int
    section_score: int
    markdown_score: int
    json_score: int
    metrics_score: int
    boundary_score: int


@dataclass(frozen=True)
class OfflineReportMarkdownJsonV1Input:
    run_id: str = "offline-run-v1"
    symbol: str = "SIM"
    decision: str = "APPROVE_OFFLINE_REPORT_MARKDOWN_JSON_V1"
    score: int = 100
    market_scenario: Any = None
    broker_result: Any = None
    risk_guard_result: Any = None
    journal_result: Any = None
    metrics: Any = None
    warnings: tuple[str, ...] = ()
    next_actions: tuple[str, ...] = ("Prepare CSV replay input v1",)
    blocked_reason: str = ""
    custom_sections: tuple[OfflineReportSectionV1 | dict[str, Any], ...] | None = None
    force_context_invalid: bool = False
    force_section_missing: bool = False
    force_markdown_invalid: bool = False
    force_json_invalid: bool = False
    force_metrics_missing: bool = False
    offline_mode_enforced: bool = True
    sandbox_mode_enforced: bool = True
    in_memory_only: bool = True
    report_in_memory_only: bool = True
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
class OfflineReportMarkdownJsonV1Result:
    state: OfflineReportMarkdownJsonV1State
    decision: OfflineReportMarkdownJsonV1Decision
    score: OfflineReportMarkdownJsonV1Score
    risks: tuple[OfflineReportMarkdownJsonV1Risk, ...]
    recommendations: tuple[OfflineReportMarkdownJsonV1Recommendation, ...]
    context: OfflineReportContextV1 | None = None
    sections: tuple[OfflineReportSectionV1, ...] = ()
    markdown: OfflineReportMarkdownV1 | None = None
    json_report: OfflineReportJsonV1 | None = None
    metrics: OfflineReportMetricsV1 | None = None
    offline_only: bool = True
    in_memory_only: bool = True
    file_written: bool = False
    data_accessed: bool = False
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False
    next_phase: str = "CSV_REPLAY_INPUT_V1"
