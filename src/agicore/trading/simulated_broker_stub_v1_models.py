"""Models for deterministic simulated broker stub v1."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class SimulatedBrokerStubV1State(StrEnum):
    NOT_READY = "NOT_READY"
    SIMULATED_BROKER_STUB_V1_INPUT_INVALID = "SIMULATED_BROKER_STUB_V1_INPUT_INVALID"
    SIMULATED_BROKER_STUB_V1_BLOCKED = "SIMULATED_BROKER_STUB_V1_BLOCKED"
    SIMULATED_BROKER_STUB_V1_COMPLETED_WITH_WARNINGS = "SIMULATED_BROKER_STUB_V1_COMPLETED_WITH_WARNINGS"
    SIMULATED_BROKER_STUB_V1_COMPLETED = "SIMULATED_BROKER_STUB_V1_COMPLETED"
    READY_FOR_RISK_GUARD_ENFORCEMENT_V1 = "READY_FOR_RISK_GUARD_ENFORCEMENT_V1"


class SimulatedBrokerStubV1Decision(StrEnum):
    BLOCK_SIMULATED_BROKER_STUB_V1 = "BLOCK_SIMULATED_BROKER_STUB_V1"
    REQUIRE_SIMULATED_BROKER_INPUT_FIXES = "REQUIRE_SIMULATED_BROKER_INPUT_FIXES"
    REQUIRE_SIMULATED_BROKER_ACCOUNT_SNAPSHOT_FIXES = "REQUIRE_SIMULATED_BROKER_ACCOUNT_SNAPSHOT_FIXES"
    REQUIRE_SIMULATED_BROKER_POSITION_SNAPSHOT_FIXES = "REQUIRE_SIMULATED_BROKER_POSITION_SNAPSHOT_FIXES"
    REQUIRE_SIMULATED_BROKER_LIMITS_FIXES = "REQUIRE_SIMULATED_BROKER_LIMITS_FIXES"
    REQUIRE_SIMULATED_BROKER_EXPOSURE_FIXES = "REQUIRE_SIMULATED_BROKER_EXPOSURE_FIXES"
    REQUIRE_SIMULATED_BROKER_JOURNAL_FIXES = "REQUIRE_SIMULATED_BROKER_JOURNAL_FIXES"
    REQUIRE_SIMULATED_BROKER_METRICS_FIXES = "REQUIRE_SIMULATED_BROKER_METRICS_FIXES"
    APPROVE_SIMULATED_BROKER_STUB_V1 = "APPROVE_SIMULATED_BROKER_STUB_V1"


class SimulatedBrokerStubV1Risk(StrEnum):
    SIMULATED_BROKER_INPUT_MISSING = "SIMULATED_BROKER_INPUT_MISSING"
    SIMULATED_BROKER_ACCOUNT_SNAPSHOT_INVALID = "SIMULATED_BROKER_ACCOUNT_SNAPSHOT_INVALID"
    SIMULATED_BROKER_POSITION_SNAPSHOT_INVALID = "SIMULATED_BROKER_POSITION_SNAPSHOT_INVALID"
    SIMULATED_BROKER_LIMITS_INVALID = "SIMULATED_BROKER_LIMITS_INVALID"
    SIMULATED_BROKER_EXPOSURE_INVALID = "SIMULATED_BROKER_EXPOSURE_INVALID"
    SIMULATED_BROKER_AVAILABLE_CASH_INVALID = "SIMULATED_BROKER_AVAILABLE_CASH_INVALID"
    SIMULATED_BROKER_MARGIN_USAGE_INVALID = "SIMULATED_BROKER_MARGIN_USAGE_INVALID"
    SIMULATED_BROKER_JOURNAL_MISSING = "SIMULATED_BROKER_JOURNAL_MISSING"
    SIMULATED_BROKER_METRICS_MISSING = "SIMULATED_BROKER_METRICS_MISSING"
    REAL_BROKER_BOUNDARY_VIOLATION = "REAL_BROKER_BOUNDARY_VIOLATION"
    REAL_SECRET_BOUNDARY_VIOLATION = "REAL_SECRET_BOUNDARY_VIOLATION"
    NETWORK_BOUNDARY_VIOLATION = "NETWORK_BOUNDARY_VIOLATION"
    ORDER_EXECUTION_BOUNDARY_VIOLATION = "ORDER_EXECUTION_BOUNDARY_VIOLATION"
    ACCOUNT_ACCESS_BOUNDARY_VIOLATION = "ACCOUNT_ACCESS_BOUNDARY_VIOLATION"
    POSITION_MUTATION_BOUNDARY_VIOLATION = "POSITION_MUTATION_BOUNDARY_VIOLATION"
    DATA_ACCESS_BOUNDARY_VIOLATION = "DATA_ACCESS_BOUNDARY_VIOLATION"


class SimulatedBrokerStubV1Recommendation(StrEnum):
    PROVIDE_SIMULATED_BROKER_INPUT = "PROVIDE_SIMULATED_BROKER_INPUT"
    FIX_SIMULATED_ACCOUNT_SNAPSHOT = "FIX_SIMULATED_ACCOUNT_SNAPSHOT"
    FIX_SIMULATED_POSITION_SNAPSHOT = "FIX_SIMULATED_POSITION_SNAPSHOT"
    FIX_SIMULATED_BROKER_LIMITS = "FIX_SIMULATED_BROKER_LIMITS"
    FIX_SIMULATED_BROKER_EXPOSURE = "FIX_SIMULATED_BROKER_EXPOSURE"
    FIX_SIMULATED_AVAILABLE_CASH = "FIX_SIMULATED_AVAILABLE_CASH"
    FIX_SIMULATED_MARGIN_USAGE = "FIX_SIMULATED_MARGIN_USAGE"
    WRITE_SIMULATED_BROKER_JOURNAL = "WRITE_SIMULATED_BROKER_JOURNAL"
    COMPUTE_SIMULATED_BROKER_METRICS = "COMPUTE_SIMULATED_BROKER_METRICS"
    REMOVE_REAL_BROKER_ACCESS = "REMOVE_REAL_BROKER_ACCESS"
    REMOVE_REAL_SECRET_ACCESS = "REMOVE_REAL_SECRET_ACCESS"
    REMOVE_NETWORK_ACCESS = "REMOVE_NETWORK_ACCESS"
    KEEP_ORDER_PREVIEW_READ_ONLY = "KEEP_ORDER_PREVIEW_READ_ONLY"
    REMOVE_REAL_ACCOUNT_ACCESS = "REMOVE_REAL_ACCOUNT_ACCESS"
    REMOVE_POSITION_MUTATION = "REMOVE_POSITION_MUTATION"
    REMOVE_DATA_ACCESS = "REMOVE_DATA_ACCESS"
    RUN_SIMULATED_BROKER_STUB_V1_TEST_SUITE = "RUN_SIMULATED_BROKER_STUB_V1_TEST_SUITE"
    APPROVE_RISK_GUARD_ENFORCEMENT_V1 = "APPROVE_RISK_GUARD_ENFORCEMENT_V1"


@dataclass(frozen=True)
class SimulatedBrokerAccountSnapshotV1:
    account_id: str
    cash: float
    equity: float
    buying_power: float
    currency: str = "USD"
    simulated: bool = True
    read_only: bool = True
    real_account: bool = False


@dataclass(frozen=True)
class SimulatedBrokerPositionSnapshotV1:
    symbol: str
    quantity: float
    average_price: float
    market_price: float
    market_value: float
    unrealized_pnl: float = 0.0
    simulated: bool = True
    read_only: bool = True
    real_position: bool = False


@dataclass(frozen=True)
class SimulatedBrokerReadOnlyOrderPreviewV1:
    symbol: str
    action: str
    requested_quantity: float
    reference_price: float
    notional: float
    read_only: bool = True
    order_submitted: bool = False
    real_order: bool = False
    position_mutation: bool = False


@dataclass(frozen=True)
class SimulatedBrokerExecutionPreviewV1:
    accepted: bool
    status: str
    estimated_cash_after: float
    estimated_position_after: float
    reason: str
    simulated: bool = True
    read_only: bool = True
    real_execution: bool = False


@dataclass(frozen=True)
class SimulatedBrokerRejectionV1:
    rejected: bool
    code: str
    reason: str
    simulated: bool = True
    real_order_submitted: bool = False


@dataclass(frozen=True)
class SimulatedBrokerLimitsV1:
    max_order_notional: float = 10_000.0
    max_position_quantity: float = 100.0
    max_margin_usage: float = 0.5
    allow_short: bool = False
    simulated: bool = True


@dataclass(frozen=True)
class SimulatedBrokerExposureV1:
    gross_exposure: float
    net_exposure: float
    exposure_fraction: float
    margin_usage: float
    available_cash: float
    simulated: bool = True


@dataclass(frozen=True)
class SimulatedBrokerJournalEntryV1:
    step: int
    event_type: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SimulatedBrokerStubV1Metrics:
    preview_count: int
    rejection_count: int
    acceptance_preview_count: int
    real_order_count: int
    real_account_access_count: int
    position_mutation_count: int
    data_access_count: int
    gross_exposure: float
    available_cash: float
    margin_usage: float


@dataclass(frozen=True)
class SimulatedBrokerStubV1Score:
    overall_score: int
    input_score: int
    account_score: int
    position_score: int
    limits_score: int
    exposure_score: int
    journal_score: int
    metrics_score: int
    boundary_score: int


@dataclass(frozen=True)
class SimulatedBrokerStubV1Report:
    markdown: str
    json: str


@dataclass(frozen=True)
class SimulatedBrokerStubV1Input:
    broker_id: str = "SIM-BROKER-STUB-V1"
    account_id: str = "SIM-ACCOUNT"
    symbol: str = "SIM"
    action: str = "BUY"
    requested_quantity: float = 5.0
    reference_price: float = 100.0
    initial_cash: float = 100_000.0
    initial_equity: float = 100_000.0
    initial_position_quantity: float = 0.0
    average_price: float = 100.0
    account_snapshot: SimulatedBrokerAccountSnapshotV1 | dict[str, Any] | None = None
    position_snapshot: SimulatedBrokerPositionSnapshotV1 | dict[str, Any] | None = None
    limits: SimulatedBrokerLimitsV1 | dict[str, Any] | None = None
    read_only_decision: Any = None
    force_exposure_invalid: bool = False
    force_available_cash_invalid: bool = False
    force_margin_usage_invalid: bool = False
    force_journal_missing: bool = False
    force_metrics_missing: bool = False
    offline_mode_enforced: bool = True
    sandbox_mode_enforced: bool = True
    in_memory_only: bool = True
    simulated_broker_only: bool = True
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
class SimulatedBrokerStubV1Result:
    state: SimulatedBrokerStubV1State
    decision: SimulatedBrokerStubV1Decision
    score: SimulatedBrokerStubV1Score
    risks: tuple[SimulatedBrokerStubV1Risk, ...]
    recommendations: tuple[SimulatedBrokerStubV1Recommendation, ...]
    account_snapshot: SimulatedBrokerAccountSnapshotV1 | None = None
    position_snapshot: SimulatedBrokerPositionSnapshotV1 | None = None
    limits: SimulatedBrokerLimitsV1 | None = None
    order_preview: SimulatedBrokerReadOnlyOrderPreviewV1 | None = None
    rejection: SimulatedBrokerRejectionV1 | None = None
    acceptance_preview: SimulatedBrokerExecutionPreviewV1 | None = None
    exposure: SimulatedBrokerExposureV1 | None = None
    journal_entries: tuple[SimulatedBrokerJournalEntryV1, ...] = ()
    metrics: SimulatedBrokerStubV1Metrics | None = None
    report: SimulatedBrokerStubV1Report | None = None
    offline_only: bool = True
    simulated_only: bool = True
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False
    data_accessed: bool = False
    next_phase: str = "RISK_GUARD_ENFORCEMENT_V1"
