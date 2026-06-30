"""Models for deterministic offline risk guard enforcement v1."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class RiskGuardEnforcementV1State(StrEnum):
    NOT_READY = "NOT_READY"
    RISK_GUARD_ENFORCEMENT_V1_INPUT_INVALID = "RISK_GUARD_ENFORCEMENT_V1_INPUT_INVALID"
    RISK_GUARD_ENFORCEMENT_V1_BLOCKED = "RISK_GUARD_ENFORCEMENT_V1_BLOCKED"
    RISK_GUARD_ENFORCEMENT_V1_COMPLETED_WITH_WARNINGS = "RISK_GUARD_ENFORCEMENT_V1_COMPLETED_WITH_WARNINGS"
    RISK_GUARD_ENFORCEMENT_V1_COMPLETED = "RISK_GUARD_ENFORCEMENT_V1_COMPLETED"
    READY_FOR_JOURNAL_WRITER_V1 = "READY_FOR_JOURNAL_WRITER_V1"


class RiskGuardEnforcementV1Decision(StrEnum):
    BLOCK_RISK_GUARD_ENFORCEMENT_V1 = "BLOCK_RISK_GUARD_ENFORCEMENT_V1"
    REQUIRE_RISK_GUARD_INPUT_FIXES = "REQUIRE_RISK_GUARD_INPUT_FIXES"
    REQUIRE_RISK_GUARD_LIMITS_FIXES = "REQUIRE_RISK_GUARD_LIMITS_FIXES"
    REQUIRE_RISK_GUARD_CONTEXT_FIXES = "REQUIRE_RISK_GUARD_CONTEXT_FIXES"
    REQUIRE_MAX_POSITION_SIZE_FIXES = "REQUIRE_MAX_POSITION_SIZE_FIXES"
    REQUIRE_MAX_NOTIONAL_EXPOSURE_FIXES = "REQUIRE_MAX_NOTIONAL_EXPOSURE_FIXES"
    REQUIRE_AVAILABLE_CASH_FIXES = "REQUIRE_AVAILABLE_CASH_FIXES"
    REQUIRE_MARGIN_USAGE_FIXES = "REQUIRE_MARGIN_USAGE_FIXES"
    REQUIRE_DAILY_LOSS_FIXES = "REQUIRE_DAILY_LOSS_FIXES"
    REQUIRE_DRAWDOWN_FIXES = "REQUIRE_DRAWDOWN_FIXES"
    REQUIRE_SYMBOL_ALLOWLIST_FIXES = "REQUIRE_SYMBOL_ALLOWLIST_FIXES"
    REQUIRE_READ_ONLY_ORDER_PREVIEW_FIXES = "REQUIRE_READ_ONLY_ORDER_PREVIEW_FIXES"
    REQUIRE_NO_REAL_EXECUTION_BOUNDARY_FIXES = "REQUIRE_NO_REAL_EXECUTION_BOUNDARY_FIXES"
    APPROVE_RISK_GUARD_ENFORCEMENT_V1 = "APPROVE_RISK_GUARD_ENFORCEMENT_V1"


class RiskGuardEnforcementV1Risk(StrEnum):
    RISK_GUARD_INPUT_MISSING = "RISK_GUARD_INPUT_MISSING"
    RISK_GUARD_LIMITS_INVALID = "RISK_GUARD_LIMITS_INVALID"
    RISK_GUARD_CONTEXT_INVALID = "RISK_GUARD_CONTEXT_INVALID"
    MAX_POSITION_SIZE_EXCEEDED = "MAX_POSITION_SIZE_EXCEEDED"
    MAX_NOTIONAL_EXPOSURE_EXCEEDED = "MAX_NOTIONAL_EXPOSURE_EXCEEDED"
    AVAILABLE_CASH_INSUFFICIENT = "AVAILABLE_CASH_INSUFFICIENT"
    MARGIN_USAGE_EXCEEDED = "MARGIN_USAGE_EXCEEDED"
    DAILY_LOSS_LIMIT_EXCEEDED = "DAILY_LOSS_LIMIT_EXCEEDED"
    MAX_DRAWDOWN_EXCEEDED = "MAX_DRAWDOWN_EXCEEDED"
    SYMBOL_NOT_ALLOWED = "SYMBOL_NOT_ALLOWED"
    READ_ONLY_ORDER_PREVIEW_INVALID = "READ_ONLY_ORDER_PREVIEW_INVALID"
    ACCOUNT_SNAPSHOT_INVALID = "ACCOUNT_SNAPSHOT_INVALID"
    POSITION_SNAPSHOT_INVALID = "POSITION_SNAPSHOT_INVALID"
    SYNTHETIC_MARKET_SCENARIO_INVALID = "SYNTHETIC_MARKET_SCENARIO_INVALID"
    REAL_BROKER_BOUNDARY_VIOLATION = "REAL_BROKER_BOUNDARY_VIOLATION"
    REAL_SECRET_BOUNDARY_VIOLATION = "REAL_SECRET_BOUNDARY_VIOLATION"
    NETWORK_BOUNDARY_VIOLATION = "NETWORK_BOUNDARY_VIOLATION"
    ORDER_EXECUTION_BOUNDARY_VIOLATION = "ORDER_EXECUTION_BOUNDARY_VIOLATION"
    ACCOUNT_ACCESS_BOUNDARY_VIOLATION = "ACCOUNT_ACCESS_BOUNDARY_VIOLATION"
    POSITION_MUTATION_BOUNDARY_VIOLATION = "POSITION_MUTATION_BOUNDARY_VIOLATION"
    DATA_ACCESS_BOUNDARY_VIOLATION = "DATA_ACCESS_BOUNDARY_VIOLATION"


class RiskGuardEnforcementV1Recommendation(StrEnum):
    PROVIDE_RISK_GUARD_INPUT = "PROVIDE_RISK_GUARD_INPUT"
    FIX_RISK_GUARD_LIMITS = "FIX_RISK_GUARD_LIMITS"
    FIX_RISK_GUARD_CONTEXT = "FIX_RISK_GUARD_CONTEXT"
    REDUCE_POSITION_SIZE = "REDUCE_POSITION_SIZE"
    REDUCE_NOTIONAL_EXPOSURE = "REDUCE_NOTIONAL_EXPOSURE"
    RESTORE_AVAILABLE_CASH = "RESTORE_AVAILABLE_CASH"
    REDUCE_MARGIN_USAGE = "REDUCE_MARGIN_USAGE"
    STOP_AFTER_DAILY_LOSS = "STOP_AFTER_DAILY_LOSS"
    STOP_AFTER_DRAWDOWN = "STOP_AFTER_DRAWDOWN"
    USE_ALLOWED_SYMBOL = "USE_ALLOWED_SYMBOL"
    KEEP_ORDER_PREVIEW_READ_ONLY = "KEEP_ORDER_PREVIEW_READ_ONLY"
    FIX_ACCOUNT_SNAPSHOT = "FIX_ACCOUNT_SNAPSHOT"
    FIX_POSITION_SNAPSHOT = "FIX_POSITION_SNAPSHOT"
    FIX_SYNTHETIC_MARKET_SCENARIO = "FIX_SYNTHETIC_MARKET_SCENARIO"
    REMOVE_REAL_BROKER_ACCESS = "REMOVE_REAL_BROKER_ACCESS"
    REMOVE_REAL_SECRET_ACCESS = "REMOVE_REAL_SECRET_ACCESS"
    REMOVE_NETWORK_ACCESS = "REMOVE_NETWORK_ACCESS"
    REMOVE_ORDER_EXECUTION = "REMOVE_ORDER_EXECUTION"
    REMOVE_ACCOUNT_ACCESS = "REMOVE_ACCOUNT_ACCESS"
    REMOVE_POSITION_MUTATION = "REMOVE_POSITION_MUTATION"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    RUN_RISK_GUARD_ENFORCEMENT_V1_TEST_SUITE = "RUN_RISK_GUARD_ENFORCEMENT_V1_TEST_SUITE"
    APPROVE_JOURNAL_WRITER_V1 = "APPROVE_JOURNAL_WRITER_V1"


@dataclass(frozen=True)
class RiskGuardLimitsV1:
    max_position_size: float = 10.0
    max_notional_exposure: float = 10_000.0
    min_available_cash: float = 0.0
    max_margin_usage: float = 0.5
    max_daily_loss: float = 1_000.0
    max_drawdown: float = 0.1
    allowed_symbols: tuple[str, ...] = ("SIM",)


@dataclass(frozen=True)
class RiskGuardContextV1:
    symbol: str
    requested_quantity: float
    reference_price: float
    notional_exposure: float
    available_cash: float
    margin_usage: float
    daily_loss: float
    drawdown: float
    order_preview: Any = None
    account_snapshot: Any = None
    position_snapshot: Any = None
    synthetic_market_scenario: Any = None


@dataclass(frozen=True)
class RiskGuardViolationV1:
    guard_name: str
    risk: RiskGuardEnforcementV1Risk
    message: str
    actual: float | str | bool | None = None
    limit: float | str | bool | None = None


@dataclass(frozen=True)
class RiskGuardEvaluationV1:
    guard_name: str
    passed: bool
    blocking: bool = True
    violation: RiskGuardViolationV1 | None = None


@dataclass(frozen=True)
class RiskGuardEnforcementSummaryV1:
    all_passed: bool
    evaluation_count: int
    passed_count: int
    violation_count: int
    blocking_violation_count: int


@dataclass(frozen=True)
class RiskGuardEnforcementV1Score:
    overall_score: int
    input_score: int
    limits_score: int
    context_score: int
    guard_score: int
    boundary_score: int


@dataclass(frozen=True)
class RiskGuardEnforcementReportV1:
    markdown: str
    json: str


@dataclass(frozen=True)
class RiskGuardEnforcementV1Input:
    symbol: str = "SIM"
    requested_quantity: float = 5.0
    reference_price: float = 100.0
    available_cash: float = 99_500.0
    margin_usage: float = 0.01
    daily_loss: float = 0.0
    drawdown: float = 0.0
    limits: RiskGuardLimitsV1 | dict[str, Any] | None = None
    order_preview: Any = None
    account_snapshot: Any = None
    position_snapshot: Any = None
    synthetic_market_scenario: Any = None
    force_context_invalid: bool = False
    offline_mode_enforced: bool = True
    sandbox_mode_enforced: bool = True
    in_memory_only: bool = True
    risk_guard_simulated_only: bool = True
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
class RiskGuardEnforcementV1Result:
    state: RiskGuardEnforcementV1State
    decision: RiskGuardEnforcementV1Decision
    score: RiskGuardEnforcementV1Score
    risks: tuple[RiskGuardEnforcementV1Risk, ...]
    recommendations: tuple[RiskGuardEnforcementV1Recommendation, ...]
    limits: RiskGuardLimitsV1 | None = None
    context: RiskGuardContextV1 | None = None
    evaluations: tuple[RiskGuardEvaluationV1, ...] = ()
    violations: tuple[RiskGuardViolationV1, ...] = ()
    summary: RiskGuardEnforcementSummaryV1 | None = None
    report: RiskGuardEnforcementReportV1 | None = None
    offline_only: bool = True
    simulated_only: bool = True
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False
    data_accessed: bool = False
    next_phase: str = "JOURNAL_WRITER_V1"
