"""Models for deterministic in-memory journal writer v1."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class JournalEntryTypeV1(StrEnum):
    RUN_STARTED = "RUN_STARTED"
    MARKET_SCENARIO_CREATED = "MARKET_SCENARIO_CREATED"
    STRATEGY_SIGNAL_EVALUATED = "STRATEGY_SIGNAL_EVALUATED"
    BROKER_PREVIEW_CREATED = "BROKER_PREVIEW_CREATED"
    RISK_GUARD_EVALUATED = "RISK_GUARD_EVALUATED"
    READ_ONLY_DECISION_CREATED = "READ_ONLY_DECISION_CREATED"
    METRICS_COMPUTED = "METRICS_COMPUTED"
    WARNING_RECORDED = "WARNING_RECORDED"
    DECISION_BLOCKED = "DECISION_BLOCKED"
    RUN_COMPLETED = "RUN_COMPLETED"


class JournalEntrySeverityV1(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    BLOCKED = "BLOCKED"
    ERROR = "ERROR"


class JournalWriterV1State(StrEnum):
    NOT_READY = "NOT_READY"
    JOURNAL_WRITER_V1_INPUT_INVALID = "JOURNAL_WRITER_V1_INPUT_INVALID"
    JOURNAL_WRITER_V1_BLOCKED = "JOURNAL_WRITER_V1_BLOCKED"
    JOURNAL_WRITER_V1_COMPLETED_WITH_WARNINGS = "JOURNAL_WRITER_V1_COMPLETED_WITH_WARNINGS"
    JOURNAL_WRITER_V1_COMPLETED = "JOURNAL_WRITER_V1_COMPLETED"
    READY_FOR_OFFLINE_REPORT_MARKDOWN_JSON_V1 = "READY_FOR_OFFLINE_REPORT_MARKDOWN_JSON_V1"


class JournalWriterV1Decision(StrEnum):
    BLOCK_JOURNAL_WRITER_V1 = "BLOCK_JOURNAL_WRITER_V1"
    REQUIRE_JOURNAL_WRITER_INPUT_FIXES = "REQUIRE_JOURNAL_WRITER_INPUT_FIXES"
    REQUIRE_JOURNAL_CONTEXT_FIXES = "REQUIRE_JOURNAL_CONTEXT_FIXES"
    REQUIRE_JOURNAL_ENTRY_FIXES = "REQUIRE_JOURNAL_ENTRY_FIXES"
    REQUIRE_JOURNAL_SEQUENCE_FIXES = "REQUIRE_JOURNAL_SEQUENCE_FIXES"
    REQUIRE_JOURNAL_INTEGRITY_FIXES = "REQUIRE_JOURNAL_INTEGRITY_FIXES"
    REQUIRE_JOURNAL_METRICS_FIXES = "REQUIRE_JOURNAL_METRICS_FIXES"
    REQUIRE_JOURNAL_REPORT_FIXES = "REQUIRE_JOURNAL_REPORT_FIXES"
    APPROVE_JOURNAL_WRITER_V1 = "APPROVE_JOURNAL_WRITER_V1"


class JournalWriterV1Risk(StrEnum):
    JOURNAL_WRITER_INPUT_MISSING = "JOURNAL_WRITER_INPUT_MISSING"
    JOURNAL_CONTEXT_INVALID = "JOURNAL_CONTEXT_INVALID"
    JOURNAL_ENTRY_INVALID = "JOURNAL_ENTRY_INVALID"
    JOURNAL_ENTRY_TYPE_INVALID = "JOURNAL_ENTRY_TYPE_INVALID"
    JOURNAL_ENTRY_SEVERITY_INVALID = "JOURNAL_ENTRY_SEVERITY_INVALID"
    JOURNAL_SEQUENCE_INVALID = "JOURNAL_SEQUENCE_INVALID"
    JOURNAL_INTEGRITY_FAILED = "JOURNAL_INTEGRITY_FAILED"
    JOURNAL_METRICS_MISSING = "JOURNAL_METRICS_MISSING"
    JOURNAL_REPORT_MISSING = "JOURNAL_REPORT_MISSING"
    FILE_WRITE_BOUNDARY_VIOLATION = "FILE_WRITE_BOUNDARY_VIOLATION"
    REAL_DATA_ACCESS_BOUNDARY_VIOLATION = "REAL_DATA_ACCESS_BOUNDARY_VIOLATION"
    DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION = "DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION"
    REAL_BROKER_BOUNDARY_VIOLATION = "REAL_BROKER_BOUNDARY_VIOLATION"
    REAL_SECRET_BOUNDARY_VIOLATION = "REAL_SECRET_BOUNDARY_VIOLATION"
    NETWORK_BOUNDARY_VIOLATION = "NETWORK_BOUNDARY_VIOLATION"
    ORDER_EXECUTION_BOUNDARY_VIOLATION = "ORDER_EXECUTION_BOUNDARY_VIOLATION"
    ACCOUNT_ACCESS_BOUNDARY_VIOLATION = "ACCOUNT_ACCESS_BOUNDARY_VIOLATION"
    POSITION_MUTATION_BOUNDARY_VIOLATION = "POSITION_MUTATION_BOUNDARY_VIOLATION"


class JournalWriterV1Recommendation(StrEnum):
    PROVIDE_JOURNAL_WRITER_INPUT = "PROVIDE_JOURNAL_WRITER_INPUT"
    FIX_JOURNAL_CONTEXT = "FIX_JOURNAL_CONTEXT"
    FIX_JOURNAL_ENTRY = "FIX_JOURNAL_ENTRY"
    USE_VALID_JOURNAL_ENTRY_TYPE = "USE_VALID_JOURNAL_ENTRY_TYPE"
    USE_VALID_JOURNAL_ENTRY_SEVERITY = "USE_VALID_JOURNAL_ENTRY_SEVERITY"
    FIX_JOURNAL_SEQUENCE = "FIX_JOURNAL_SEQUENCE"
    FIX_JOURNAL_INTEGRITY = "FIX_JOURNAL_INTEGRITY"
    COMPUTE_JOURNAL_METRICS = "COMPUTE_JOURNAL_METRICS"
    GENERATE_JOURNAL_REPORT = "GENERATE_JOURNAL_REPORT"
    REMOVE_FILE_WRITE = "REMOVE_FILE_WRITE"
    REMOVE_REAL_DATA_ACCESS = "REMOVE_REAL_DATA_ACCESS"
    REMOVE_DATA_DIRECTORY_ACCESS = "REMOVE_DATA_DIRECTORY_ACCESS"
    REMOVE_REAL_BROKER_ACCESS = "REMOVE_REAL_BROKER_ACCESS"
    REMOVE_REAL_SECRET_ACCESS = "REMOVE_REAL_SECRET_ACCESS"
    REMOVE_NETWORK_ACCESS = "REMOVE_NETWORK_ACCESS"
    REMOVE_ORDER_EXECUTION = "REMOVE_ORDER_EXECUTION"
    REMOVE_ACCOUNT_ACCESS = "REMOVE_ACCOUNT_ACCESS"
    REMOVE_POSITION_MUTATION = "REMOVE_POSITION_MUTATION"
    RUN_JOURNAL_WRITER_V1_TEST_SUITE = "RUN_JOURNAL_WRITER_V1_TEST_SUITE"
    APPROVE_OFFLINE_REPORT_MARKDOWN_JSON_V1 = "APPROVE_OFFLINE_REPORT_MARKDOWN_JSON_V1"


@dataclass(frozen=True)
class JournalWriterV1Context:
    run_id: str
    symbol: str
    scenario_id: str
    deterministic: bool = True
    in_memory_only: bool = True
    offline_only: bool = True


@dataclass(frozen=True)
class JournalEntryV1:
    entry_id: str
    index: int
    entry_type: JournalEntryTypeV1 | str
    severity: JournalEntrySeverityV1 | str
    message: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class JournalSequenceV1:
    run_id: str
    entries: tuple[JournalEntryV1, ...]
    complete: bool = False
    in_memory_only: bool = True


@dataclass(frozen=True)
class JournalWriterV1Metrics:
    total_entries: int
    warning_count: int
    blocked_count: int
    error_count: int
    event_types_present: tuple[str, ...]
    first_index: int
    last_index: int
    complete: bool


@dataclass(frozen=True)
class JournalWriterV1Score:
    overall_score: int
    input_score: int
    context_score: int
    entry_score: int
    sequence_score: int
    integrity_score: int
    metrics_score: int
    report_score: int
    boundary_score: int


@dataclass(frozen=True)
class JournalWriterV1Report:
    markdown: str
    json: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class JournalWriterV1Input:
    run_id: str = "offline-run-v1"
    symbol: str = "SIM"
    scenario_id: str = "synthetic-market-v1"
    market_scenario: Any = None
    strategy_signal: Any = None
    broker_preview: Any = None
    risk_guard_result: Any = None
    read_only_decision: Any = None
    runner_metrics: Any = None
    warnings: tuple[str, ...] = ()
    blocked_reason: str = ""
    custom_entries: tuple[JournalEntryV1 | dict[str, Any], ...] | None = None
    force_context_invalid: bool = False
    force_entry_invalid: bool = False
    force_sequence_invalid: bool = False
    force_integrity_failed: bool = False
    force_metrics_missing: bool = False
    force_report_missing: bool = False
    offline_mode_enforced: bool = True
    sandbox_mode_enforced: bool = True
    in_memory_only: bool = True
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
class JournalWriterV1Result:
    state: JournalWriterV1State
    decision: JournalWriterV1Decision
    score: JournalWriterV1Score
    risks: tuple[JournalWriterV1Risk, ...]
    recommendations: tuple[JournalWriterV1Recommendation, ...]
    context: JournalWriterV1Context | None = None
    sequence: JournalSequenceV1 | None = None
    metrics: JournalWriterV1Metrics | None = None
    report: JournalWriterV1Report | None = None
    offline_only: bool = True
    in_memory_only: bool = True
    file_written: bool = False
    data_accessed: bool = False
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False
    next_phase: str = "OFFLINE_REPORT_MARKDOWN_JSON_V1"
