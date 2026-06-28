"""Models for deterministic synthetic market scenarios v1."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class SyntheticMarketScenarioV1Profile(StrEnum):
    TREND_UP = "TREND_UP"
    TREND_DOWN = "TREND_DOWN"
    RANGE_BOUND = "RANGE_BOUND"
    VOLATILITY_SPIKE = "VOLATILITY_SPIKE"
    GAP = "GAP"
    CALM_MARKET = "CALM_MARKET"


class SyntheticMarketScenarioV1State(StrEnum):
    NOT_READY = "NOT_READY"
    SYNTHETIC_MARKET_SCENARIO_V1_INPUT_INVALID = "SYNTHETIC_MARKET_SCENARIO_V1_INPUT_INVALID"
    SYNTHETIC_MARKET_SCENARIO_V1_BLOCKED = "SYNTHETIC_MARKET_SCENARIO_V1_BLOCKED"
    SYNTHETIC_MARKET_SCENARIO_V1_COMPLETED_WITH_WARNINGS = "SYNTHETIC_MARKET_SCENARIO_V1_COMPLETED_WITH_WARNINGS"
    SYNTHETIC_MARKET_SCENARIO_V1_COMPLETED = "SYNTHETIC_MARKET_SCENARIO_V1_COMPLETED"
    READY_FOR_SIMULATED_BROKER_STUB_V1 = "READY_FOR_SIMULATED_BROKER_STUB_V1"


class SyntheticMarketScenarioV1Decision(StrEnum):
    BLOCK_SYNTHETIC_MARKET_SCENARIO_V1 = "BLOCK_SYNTHETIC_MARKET_SCENARIO_V1"
    REQUIRE_SYNTHETIC_MARKET_SCENARIO_INPUT_FIXES = "REQUIRE_SYNTHETIC_MARKET_SCENARIO_INPUT_FIXES"
    REQUIRE_SYNTHETIC_MARKET_BARS_FIXES = "REQUIRE_SYNTHETIC_MARKET_BARS_FIXES"
    REQUIRE_SYNTHETIC_MARKET_OHLCV_FIXES = "REQUIRE_SYNTHETIC_MARKET_OHLCV_FIXES"
    REQUIRE_SYNTHETIC_MARKET_STATISTICS_FIXES = "REQUIRE_SYNTHETIC_MARKET_STATISTICS_FIXES"
    REQUIRE_SYNTHETIC_MARKET_CONVERSION_FIXES = "REQUIRE_SYNTHETIC_MARKET_CONVERSION_FIXES"
    APPROVE_SYNTHETIC_MARKET_SCENARIO_V1 = "APPROVE_SYNTHETIC_MARKET_SCENARIO_V1"


class SyntheticMarketScenarioV1Risk(StrEnum):
    SYNTHETIC_MARKET_SCENARIO_INPUT_MISSING = "SYNTHETIC_MARKET_SCENARIO_INPUT_MISSING"
    SYNTHETIC_MARKET_SCENARIO_PROFILE_UNSUPPORTED = "SYNTHETIC_MARKET_SCENARIO_PROFILE_UNSUPPORTED"
    SYNTHETIC_MARKET_SCENARIO_BAR_COUNT_INVALID = "SYNTHETIC_MARKET_SCENARIO_BAR_COUNT_INVALID"
    SYNTHETIC_MARKET_SCENARIO_EMPTY = "SYNTHETIC_MARKET_SCENARIO_EMPTY"
    SYNTHETIC_MARKET_BAR_INVALID = "SYNTHETIC_MARKET_BAR_INVALID"
    SYNTHETIC_MARKET_OHLCV_INCONSISTENT = "SYNTHETIC_MARKET_OHLCV_INCONSISTENT"
    SYNTHETIC_MARKET_VOLUME_INVALID = "SYNTHETIC_MARKET_VOLUME_INVALID"
    SYNTHETIC_MARKET_STATISTICS_MISSING = "SYNTHETIC_MARKET_STATISTICS_MISSING"
    SYNTHETIC_MARKET_CONVERSION_FAILED = "SYNTHETIC_MARKET_CONVERSION_FAILED"
    REAL_DATA_ACCESS_BOUNDARY_VIOLATION = "REAL_DATA_ACCESS_BOUNDARY_VIOLATION"
    DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION = "DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION"
    NETWORK_BOUNDARY_VIOLATION = "NETWORK_BOUNDARY_VIOLATION"
    REAL_BROKER_BOUNDARY_VIOLATION = "REAL_BROKER_BOUNDARY_VIOLATION"
    REAL_SECRET_BOUNDARY_VIOLATION = "REAL_SECRET_BOUNDARY_VIOLATION"


class SyntheticMarketScenarioV1Recommendation(StrEnum):
    PROVIDE_SYNTHETIC_MARKET_SCENARIO_INPUT = "PROVIDE_SYNTHETIC_MARKET_SCENARIO_INPUT"
    USE_SUPPORTED_SYNTHETIC_MARKET_PROFILE = "USE_SUPPORTED_SYNTHETIC_MARKET_PROFILE"
    FIX_SYNTHETIC_MARKET_BAR_COUNT = "FIX_SYNTHETIC_MARKET_BAR_COUNT"
    GENERATE_SYNTHETIC_MARKET_BARS = "GENERATE_SYNTHETIC_MARKET_BARS"
    FIX_SYNTHETIC_MARKET_BARS = "FIX_SYNTHETIC_MARKET_BARS"
    FIX_SYNTHETIC_MARKET_OHLCV = "FIX_SYNTHETIC_MARKET_OHLCV"
    FIX_SYNTHETIC_MARKET_VOLUME = "FIX_SYNTHETIC_MARKET_VOLUME"
    COMPUTE_SYNTHETIC_MARKET_STATISTICS = "COMPUTE_SYNTHETIC_MARKET_STATISTICS"
    FIX_CONTROLLED_OFFLINE_RUNNER_CONVERSION = "FIX_CONTROLLED_OFFLINE_RUNNER_CONVERSION"
    REMOVE_REAL_DATA_ACCESS = "REMOVE_REAL_DATA_ACCESS"
    REMOVE_DATA_DIRECTORY_ACCESS = "REMOVE_DATA_DIRECTORY_ACCESS"
    REMOVE_NETWORK_ACCESS = "REMOVE_NETWORK_ACCESS"
    REMOVE_REAL_BROKER_ACCESS = "REMOVE_REAL_BROKER_ACCESS"
    REMOVE_REAL_SECRET_ACCESS = "REMOVE_REAL_SECRET_ACCESS"
    RUN_SYNTHETIC_MARKET_SCENARIO_V1_TEST_SUITE = "RUN_SYNTHETIC_MARKET_SCENARIO_V1_TEST_SUITE"
    APPROVE_SIMULATED_BROKER_STUB_V1 = "APPROVE_SIMULATED_BROKER_STUB_V1"


@dataclass(frozen=True)
class SyntheticMarketBarV1:
    index: int
    timestamp: str
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class SyntheticMarketScenarioV1:
    scenario_id: str
    profile: SyntheticMarketScenarioV1Profile
    symbol: str
    bars: tuple[SyntheticMarketBarV1, ...]
    deterministic: bool = True
    offline_only: bool = True
    synthetic_only: bool = True


@dataclass(frozen=True)
class SyntheticMarketScenarioV1Statistics:
    bar_count: int
    initial_price: float
    final_price: float
    absolute_change: float
    percent_change: float
    total_volume: float
    simple_volatility: float
    max_high: float
    min_low: float


@dataclass(frozen=True)
class SyntheticMarketScenarioV1ConversionResult:
    converted: bool
    runner_scenario: Any = None
    risks: tuple[SyntheticMarketScenarioV1Risk, ...] = ()


@dataclass(frozen=True)
class SyntheticMarketScenarioV1Score:
    overall_score: int
    input_score: int
    bar_score: int
    ohlcv_score: int
    statistics_score: int
    conversion_score: int
    boundary_score: int


@dataclass(frozen=True)
class SyntheticMarketScenarioV1Report:
    markdown: str
    json: str


@dataclass(frozen=True)
class SyntheticMarketScenarioV1Input:
    profile: SyntheticMarketScenarioV1Profile | str = SyntheticMarketScenarioV1Profile.TREND_UP
    scenario_id: str = "synthetic-market-v1"
    symbol: str = "SIM"
    bar_count: int = 12
    initial_price: float = 100.0
    base_volume: float = 1000.0
    custom_bars: tuple[SyntheticMarketBarV1 | dict[str, Any], ...] | None = None
    offline_mode_enforced: bool = True
    deterministic_generation: bool = True
    synthetic_data_only: bool = True
    in_memory_only: bool = True
    no_real_data_access: bool = True
    no_data_directory_access: bool = True
    no_network: bool = True
    no_http_transport: bool = True
    no_websocket_transport: bool = True
    no_socket_transport: bool = True
    no_external_api: bool = True
    no_real_broker: bool = True
    no_alpaca_real: bool = True
    no_api_key_read: bool = True
    no_env_var_read: bool = True
    no_hardcoded_secret: bool = True
    real_data_access_requested: bool = False
    data_directory_access_requested: bool = False
    network_requested: bool = False
    http_requested: bool = False
    websocket_requested: bool = False
    socket_requested: bool = False
    external_api_requested: bool = False
    broker_access_requested: bool = False
    api_key_read_requested: bool = False
    env_var_read_requested: bool = False


@dataclass(frozen=True)
class SyntheticMarketScenarioV1Result:
    state: SyntheticMarketScenarioV1State
    decision: SyntheticMarketScenarioV1Decision
    score: SyntheticMarketScenarioV1Score
    risks: tuple[SyntheticMarketScenarioV1Risk, ...]
    recommendations: tuple[SyntheticMarketScenarioV1Recommendation, ...]
    scenario: SyntheticMarketScenarioV1 | None = None
    statistics: SyntheticMarketScenarioV1Statistics | None = None
    conversion: SyntheticMarketScenarioV1ConversionResult | None = None
    report: SyntheticMarketScenarioV1Report | None = None
    offline_only: bool = True
    synthetic_only: bool = True
    next_phase: str = "SIMULATED_BROKER_STUB_V1"
