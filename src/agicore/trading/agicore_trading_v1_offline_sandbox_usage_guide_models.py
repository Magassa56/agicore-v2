"""Models for AGIcore Trading v1 offline sandbox usage guide."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AGIcoreTradingV1OfflineSandboxUsageGuideState(StrEnum):
    NOT_READY = "NOT_READY"
    AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE_INPUT_INVALID = (
        "AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE_INPUT_INVALID"
    )
    AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE_BLOCKED = (
        "AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE_BLOCKED"
    )
    AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE_COMPLETED_WITH_WARNINGS = (
        "AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE_COMPLETED_WITH_WARNINGS"
    )
    AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE_COMPLETED = (
        "AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE_COMPLETED"
    )
    READY_FOR_AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK = "READY_FOR_AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK"


class AGIcoreTradingV1OfflineSandboxUsageGuideDecision(StrEnum):
    BLOCK_AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE = (
        "BLOCK_AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE"
    )
    REQUIRE_SANDBOX_USAGE_GUIDE_INPUT_FIXES = "REQUIRE_SANDBOX_USAGE_GUIDE_INPUT_FIXES"
    REQUIRE_SANDBOX_USAGE_GUIDE_SAFETY_FIXES = "REQUIRE_SANDBOX_USAGE_GUIDE_SAFETY_FIXES"
    REQUIRE_SANDBOX_USAGE_GUIDE_COMMAND_FIXES = "REQUIRE_SANDBOX_USAGE_GUIDE_COMMAND_FIXES"
    REQUIRE_SANDBOX_USAGE_GUIDE_MEMORY_EXAMPLE_FIXES = "REQUIRE_SANDBOX_USAGE_GUIDE_MEMORY_EXAMPLE_FIXES"
    REQUIRE_SANDBOX_USAGE_GUIDE_INTERPRETATION_FIXES = "REQUIRE_SANDBOX_USAGE_GUIDE_INTERPRETATION_FIXES"
    REQUIRE_SANDBOX_USAGE_GUIDE_LIMITATION_FIXES = "REQUIRE_SANDBOX_USAGE_GUIDE_LIMITATION_FIXES"
    REQUIRE_SANDBOX_USAGE_GUIDE_NO_OVERCLAIM_FIXES = "REQUIRE_SANDBOX_USAGE_GUIDE_NO_OVERCLAIM_FIXES"
    APPROVE_AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE = (
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE"
    )


class AGIcoreTradingV1OfflineSandboxUsageGuideRisk(StrEnum):
    SANDBOX_USAGE_GUIDE_INPUT_MISSING = "SANDBOX_USAGE_GUIDE_INPUT_MISSING"
    SANDBOX_USAGE_GUIDE_SAFETY_LANGUAGE_MISSING = "SANDBOX_USAGE_GUIDE_SAFETY_LANGUAGE_MISSING"
    SANDBOX_USAGE_GUIDE_COMMANDS_MISSING = "SANDBOX_USAGE_GUIDE_COMMANDS_MISSING"
    SANDBOX_USAGE_GUIDE_MEMORY_EXAMPLE_MISSING = "SANDBOX_USAGE_GUIDE_MEMORY_EXAMPLE_MISSING"
    SANDBOX_USAGE_GUIDE_RESULT_INTERPRETATION_MISSING = "SANDBOX_USAGE_GUIDE_RESULT_INTERPRETATION_MISSING"
    SANDBOX_USAGE_GUIDE_LIMITATIONS_MISSING = "SANDBOX_USAGE_GUIDE_LIMITATIONS_MISSING"
    LIVE_TRADING_READINESS_OVERCLAIM = "LIVE_TRADING_READINESS_OVERCLAIM"
    REAL_BROKER_READINESS_OVERCLAIM = "REAL_BROKER_READINESS_OVERCLAIM"
    REAL_ORDER_EXECUTION_OVERCLAIM = "REAL_ORDER_EXECUTION_OVERCLAIM"
    PROFITABILITY_PROOF_OVERCLAIM = "PROFITABILITY_PROOF_OVERCLAIM"
    FINANCIAL_ADVICE_OVERCLAIM = "FINANCIAL_ADVICE_OVERCLAIM"
    FILE_READ_BOUNDARY_VIOLATION = "FILE_READ_BOUNDARY_VIOLATION"
    REAL_DATA_ACCESS_BOUNDARY_VIOLATION = "REAL_DATA_ACCESS_BOUNDARY_VIOLATION"
    DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION = "DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION"
    REAL_BROKER_BOUNDARY_VIOLATION = "REAL_BROKER_BOUNDARY_VIOLATION"
    REAL_SECRET_BOUNDARY_VIOLATION = "REAL_SECRET_BOUNDARY_VIOLATION"
    NETWORK_BOUNDARY_VIOLATION = "NETWORK_BOUNDARY_VIOLATION"
    ORDER_EXECUTION_BOUNDARY_VIOLATION = "ORDER_EXECUTION_BOUNDARY_VIOLATION"
    ACCOUNT_ACCESS_BOUNDARY_VIOLATION = "ACCOUNT_ACCESS_BOUNDARY_VIOLATION"
    POSITION_MUTATION_BOUNDARY_VIOLATION = "POSITION_MUTATION_BOUNDARY_VIOLATION"


class AGIcoreTradingV1OfflineSandboxUsageGuideRecommendation(StrEnum):
    PROVIDE_SANDBOX_USAGE_GUIDE_INPUT = "PROVIDE_SANDBOX_USAGE_GUIDE_INPUT"
    RESTORE_SANDBOX_USAGE_GUIDE_SAFETY_LANGUAGE = "RESTORE_SANDBOX_USAGE_GUIDE_SAFETY_LANGUAGE"
    RESTORE_SANDBOX_USAGE_GUIDE_COMMANDS = "RESTORE_SANDBOX_USAGE_GUIDE_COMMANDS"
    RESTORE_SANDBOX_USAGE_GUIDE_MEMORY_EXAMPLE = "RESTORE_SANDBOX_USAGE_GUIDE_MEMORY_EXAMPLE"
    RESTORE_SANDBOX_USAGE_GUIDE_INTERPRETATION = "RESTORE_SANDBOX_USAGE_GUIDE_INTERPRETATION"
    RESTORE_SANDBOX_USAGE_GUIDE_LIMITATIONS = "RESTORE_SANDBOX_USAGE_GUIDE_LIMITATIONS"
    REMOVE_LIVE_TRADING_READINESS_CLAIM = "REMOVE_LIVE_TRADING_READINESS_CLAIM"
    REMOVE_REAL_BROKER_READINESS_CLAIM = "REMOVE_REAL_BROKER_READINESS_CLAIM"
    REMOVE_REAL_ORDER_EXECUTION_CLAIM = "REMOVE_REAL_ORDER_EXECUTION_CLAIM"
    REMOVE_PROFITABILITY_PROOF_CLAIM = "REMOVE_PROFITABILITY_PROOF_CLAIM"
    REMOVE_FINANCIAL_ADVICE_CLAIM = "REMOVE_FINANCIAL_ADVICE_CLAIM"
    REMOVE_FILE_READ = "REMOVE_FILE_READ"
    REMOVE_REAL_DATA_ACCESS = "REMOVE_REAL_DATA_ACCESS"
    REMOVE_DATA_DIRECTORY_ACCESS = "REMOVE_DATA_DIRECTORY_ACCESS"
    REMOVE_REAL_BROKER_ACCESS = "REMOVE_REAL_BROKER_ACCESS"
    REMOVE_REAL_SECRET_ACCESS = "REMOVE_REAL_SECRET_ACCESS"
    REMOVE_NETWORK_ACCESS = "REMOVE_NETWORK_ACCESS"
    REMOVE_ORDER_EXECUTION = "REMOVE_ORDER_EXECUTION"
    REMOVE_ACCOUNT_ACCESS = "REMOVE_ACCOUNT_ACCESS"
    REMOVE_POSITION_MUTATION = "REMOVE_POSITION_MUTATION"
    PREPARE_AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK = "PREPARE_AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK"


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineSandboxUsageGuideScore:
    overall_score: int
    input_score: int
    safety_score: int
    command_score: int
    memory_example_score: int
    interpretation_score: int
    limitation_score: int
    overclaim_score: int
    boundary_score: int


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineSandboxUsageGuideContext:
    title: str
    status: str
    next_step: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineSandboxUsageGuideSection:
    name: str
    content: str
    required: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineSandboxUsageGuideCommand:
    command: str
    description: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineSandboxUsageGuideSafetyRule:
    text: str
    explicit: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineSandboxUsageGuideKnownLimitation:
    text: str
    documented: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineSandboxUsageGuideReport:
    markdown: str
    json: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineSandboxUsageGuideInput:
    guide_id: str = "agicore-trading-v1-offline-sandbox-usage-guide"
    force_safety_language_missing: bool = False
    force_commands_missing: bool = False
    force_memory_example_missing: bool = False
    force_result_interpretation_missing: bool = False
    force_limitations_missing: bool = False
    force_live_trading_overclaim: bool = False
    force_real_broker_overclaim: bool = False
    force_real_order_overclaim: bool = False
    force_profitability_overclaim: bool = False
    force_financial_advice_overclaim: bool = False
    file_read_requested: bool = False
    real_data_access_requested: bool = False
    data_directory_access_requested: bool = False
    broker_connection_requested: bool = False
    secret_read_requested: bool = False
    network_requested: bool = False
    http_requested: bool = False
    websocket_requested: bool = False
    socket_requested: bool = False
    external_api_requested: bool = False
    order_execution_requested: bool = False
    account_access_requested: bool = False
    position_mutation_requested: bool = False


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineSandboxUsageGuideResult:
    state: AGIcoreTradingV1OfflineSandboxUsageGuideState
    decision: AGIcoreTradingV1OfflineSandboxUsageGuideDecision
    score: AGIcoreTradingV1OfflineSandboxUsageGuideScore
    risks: tuple[AGIcoreTradingV1OfflineSandboxUsageGuideRisk, ...]
    recommendations: tuple[AGIcoreTradingV1OfflineSandboxUsageGuideRecommendation, ...]
    context: AGIcoreTradingV1OfflineSandboxUsageGuideContext | None = None
    sections: tuple[AGIcoreTradingV1OfflineSandboxUsageGuideSection, ...] = ()
    commands: tuple[AGIcoreTradingV1OfflineSandboxUsageGuideCommand, ...] = ()
    safety_rules: tuple[AGIcoreTradingV1OfflineSandboxUsageGuideSafetyRule, ...] = ()
    known_limitations: tuple[AGIcoreTradingV1OfflineSandboxUsageGuideKnownLimitation, ...] = ()
    report: AGIcoreTradingV1OfflineSandboxUsageGuideReport | None = None
    file_read: bool = False
    data_accessed: bool = False
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False
    next_phase: str = "AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK"
