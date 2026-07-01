"""Models for deterministic in-memory CSV replay input v1."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class CsvReplayInputV1State(StrEnum):
    NOT_READY = "NOT_READY"
    CSV_REPLAY_INPUT_V1_INPUT_INVALID = "CSV_REPLAY_INPUT_V1_INPUT_INVALID"
    CSV_REPLAY_INPUT_V1_BLOCKED = "CSV_REPLAY_INPUT_V1_BLOCKED"
    CSV_REPLAY_INPUT_V1_COMPLETED_WITH_WARNINGS = "CSV_REPLAY_INPUT_V1_COMPLETED_WITH_WARNINGS"
    CSV_REPLAY_INPUT_V1_COMPLETED = "CSV_REPLAY_INPUT_V1_COMPLETED"
    READY_FOR_STRATEGY_REPLAY_ENGINE_V1 = "READY_FOR_STRATEGY_REPLAY_ENGINE_V1"


class CsvReplayInputV1Decision(StrEnum):
    BLOCK_CSV_REPLAY_INPUT_V1 = "BLOCK_CSV_REPLAY_INPUT_V1"
    REQUIRE_CSV_REPLAY_INPUT_FIXES = "REQUIRE_CSV_REPLAY_INPUT_FIXES"
    REQUIRE_CSV_REPLAY_HEADER_FIXES = "REQUIRE_CSV_REPLAY_HEADER_FIXES"
    REQUIRE_CSV_REPLAY_ROW_FIXES = "REQUIRE_CSV_REPLAY_ROW_FIXES"
    REQUIRE_CSV_REPLAY_BAR_FIXES = "REQUIRE_CSV_REPLAY_BAR_FIXES"
    REQUIRE_CSV_REPLAY_OHLCV_FIXES = "REQUIRE_CSV_REPLAY_OHLCV_FIXES"
    REQUIRE_CSV_REPLAY_STATISTICS_FIXES = "REQUIRE_CSV_REPLAY_STATISTICS_FIXES"
    REQUIRE_CSV_REPLAY_CONVERSION_FIXES = "REQUIRE_CSV_REPLAY_CONVERSION_FIXES"
    APPROVE_CSV_REPLAY_INPUT_V1 = "APPROVE_CSV_REPLAY_INPUT_V1"


class CsvReplayInputV1Risk(StrEnum):
    CSV_REPLAY_INPUT_MISSING = "CSV_REPLAY_INPUT_MISSING"
    CSV_REPLAY_CONTENT_EMPTY = "CSV_REPLAY_CONTENT_EMPTY"
    CSV_REPLAY_HEADER_MISSING = "CSV_REPLAY_HEADER_MISSING"
    CSV_REPLAY_HEADER_INVALID = "CSV_REPLAY_HEADER_INVALID"
    CSV_REPLAY_ROW_INVALID = "CSV_REPLAY_ROW_INVALID"
    CSV_REPLAY_NUMERIC_VALUE_INVALID = "CSV_REPLAY_NUMERIC_VALUE_INVALID"
    CSV_REPLAY_TIMESTAMP_INVALID = "CSV_REPLAY_TIMESTAMP_INVALID"
    CSV_REPLAY_BAR_INVALID = "CSV_REPLAY_BAR_INVALID"
    CSV_REPLAY_OHLCV_INCONSISTENT = "CSV_REPLAY_OHLCV_INCONSISTENT"
    CSV_REPLAY_VOLUME_INVALID = "CSV_REPLAY_VOLUME_INVALID"
    CSV_REPLAY_STATISTICS_MISSING = "CSV_REPLAY_STATISTICS_MISSING"
    CSV_REPLAY_CONVERSION_FAILED = "CSV_REPLAY_CONVERSION_FAILED"
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


class CsvReplayInputV1Recommendation(StrEnum):
    PROVIDE_CSV_REPLAY_INPUT = "PROVIDE_CSV_REPLAY_INPUT"
    PROVIDE_CSV_REPLAY_CONTENT = "PROVIDE_CSV_REPLAY_CONTENT"
    PROVIDE_REQUIRED_CSV_HEADERS = "PROVIDE_REQUIRED_CSV_HEADERS"
    FIX_CSV_REPLAY_HEADERS = "FIX_CSV_REPLAY_HEADERS"
    FIX_CSV_REPLAY_ROWS = "FIX_CSV_REPLAY_ROWS"
    FIX_CSV_REPLAY_NUMERIC_VALUES = "FIX_CSV_REPLAY_NUMERIC_VALUES"
    FIX_CSV_REPLAY_TIMESTAMPS = "FIX_CSV_REPLAY_TIMESTAMPS"
    FIX_CSV_REPLAY_BARS = "FIX_CSV_REPLAY_BARS"
    FIX_CSV_REPLAY_OHLCV = "FIX_CSV_REPLAY_OHLCV"
    FIX_CSV_REPLAY_VOLUME = "FIX_CSV_REPLAY_VOLUME"
    COMPUTE_CSV_REPLAY_STATISTICS = "COMPUTE_CSV_REPLAY_STATISTICS"
    FIX_CSV_REPLAY_CONVERSION = "FIX_CSV_REPLAY_CONVERSION"
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
    RUN_CSV_REPLAY_INPUT_V1_TEST_SUITE = "RUN_CSV_REPLAY_INPUT_V1_TEST_SUITE"
    APPROVE_STRATEGY_REPLAY_ENGINE_V1 = "APPROVE_STRATEGY_REPLAY_ENGINE_V1"


@dataclass(frozen=True)
class CsvReplayInputV1HeaderSpec:
    required_columns: tuple[str, ...] = ("timestamp", "open", "high", "low", "close", "volume")
    normalized_columns: tuple[str, ...] = ("timestamp", "open", "high", "low", "close", "volume")
    delimiter: str = ","


@dataclass(frozen=True)
class CsvReplayRawRowV1:
    index: int
    values: dict[str, str]


@dataclass(frozen=True)
class CsvReplayNormalizedRowV1:
    index: int
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class CsvReplayBarV1:
    index: int
    timestamp: str
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class CsvReplayDatasetV1:
    dataset_id: str
    symbol: str
    bars: tuple[CsvReplayBarV1, ...]
    source: str = "IN_MEMORY_CSV_STRING"
    deterministic: bool = True
    offline_only: bool = True


@dataclass(frozen=True)
class CsvReplayStatisticsV1:
    bar_count: int
    initial_timestamp: str
    final_timestamp: str
    initial_price: float
    final_price: float
    absolute_change: float
    percent_change: float
    total_volume: float
    max_high: float
    min_low: float


@dataclass(frozen=True)
class CsvReplayConversionResultV1:
    converted: bool
    target: str
    scenario: Any = None
    risks: tuple[CsvReplayInputV1Risk, ...] = ()


@dataclass(frozen=True)
class CsvReplayInputV1Score:
    overall_score: int
    input_score: int
    header_score: int
    row_score: int
    bar_score: int
    ohlcv_score: int
    statistics_score: int
    conversion_score: int
    boundary_score: int


@dataclass(frozen=True)
class CsvReplayInputV1Report:
    markdown: str
    json: str


@dataclass(frozen=True)
class CsvReplayInputV1Input:
    csv_content: str = ""
    dataset_id: str = "csv-replay-v1"
    symbol: str = "SIM"
    delimiter: str = ","
    header_spec: CsvReplayInputV1HeaderSpec | None = None
    force_statistics_missing: bool = False
    force_conversion_failed: bool = False
    offline_mode_enforced: bool = True
    sandbox_mode_enforced: bool = True
    in_memory_only: bool = True
    csv_string_only: bool = True
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
class CsvReplayInputV1Result:
    state: CsvReplayInputV1State
    decision: CsvReplayInputV1Decision
    score: CsvReplayInputV1Score
    risks: tuple[CsvReplayInputV1Risk, ...]
    recommendations: tuple[CsvReplayInputV1Recommendation, ...]
    header_spec: CsvReplayInputV1HeaderSpec | None = None
    raw_rows: tuple[CsvReplayRawRowV1, ...] = ()
    normalized_rows: tuple[CsvReplayNormalizedRowV1, ...] = ()
    dataset: CsvReplayDatasetV1 | None = None
    statistics: CsvReplayStatisticsV1 | None = None
    synthetic_market_conversion: CsvReplayConversionResultV1 | None = None
    controlled_runner_conversion: CsvReplayConversionResultV1 | None = None
    report: CsvReplayInputV1Report | None = None
    offline_only: bool = True
    in_memory_only: bool = True
    file_read: bool = False
    file_written: bool = False
    data_accessed: bool = False
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False
    next_phase: str = "STRATEGY_REPLAY_ENGINE_V1"
