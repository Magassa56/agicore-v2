"""Models for AGIcore Trading v1 offline local runbook."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AGIcoreTradingV1OfflineLocalRunbookState(StrEnum):
    NOT_READY = "NOT_READY"
    AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK_INPUT_INVALID = "AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK_INPUT_INVALID"
    AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK_BLOCKED = "AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK_BLOCKED"
    AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK_COMPLETED_WITH_WARNINGS = (
        "AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK_COMPLETED_WITH_WARNINGS"
    )
    AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK_COMPLETED = "AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK_COMPLETED"
    READY_FOR_AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_REVIEW = (
        "READY_FOR_AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_REVIEW"
    )


class AGIcoreTradingV1OfflineLocalRunbookDecision(StrEnum):
    BLOCK_AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK = "BLOCK_AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK"
    REQUIRE_LOCAL_RUNBOOK_INPUT_FIXES = "REQUIRE_LOCAL_RUNBOOK_INPUT_FIXES"
    REQUIRE_LOCAL_RUNBOOK_SAFETY_FIXES = "REQUIRE_LOCAL_RUNBOOK_SAFETY_FIXES"
    REQUIRE_LOCAL_RUNBOOK_SYNC_FIXES = "REQUIRE_LOCAL_RUNBOOK_SYNC_FIXES"
    REQUIRE_LOCAL_RUNBOOK_TEST_COMMAND_FIXES = "REQUIRE_LOCAL_RUNBOOK_TEST_COMMAND_FIXES"
    REQUIRE_LOCAL_RUNBOOK_SMOKE_DEMO_FIXES = "REQUIRE_LOCAL_RUNBOOK_SMOKE_DEMO_FIXES"
    REQUIRE_LOCAL_RUNBOOK_INTERPRETATION_FIXES = "REQUIRE_LOCAL_RUNBOOK_INTERPRETATION_FIXES"
    REQUIRE_LOCAL_RUNBOOK_DIAGNOSTIC_FIXES = "REQUIRE_LOCAL_RUNBOOK_DIAGNOSTIC_FIXES"
    REQUIRE_LOCAL_RUNBOOK_GIT_RULE_FIXES = "REQUIRE_LOCAL_RUNBOOK_GIT_RULE_FIXES"
    REQUIRE_LOCAL_RUNBOOK_NO_OVERCLAIM_FIXES = "REQUIRE_LOCAL_RUNBOOK_NO_OVERCLAIM_FIXES"
    APPROVE_AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK = "APPROVE_AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK"


class AGIcoreTradingV1OfflineLocalRunbookRisk(StrEnum):
    LOCAL_RUNBOOK_INPUT_MISSING = "LOCAL_RUNBOOK_INPUT_MISSING"
    LOCAL_RUNBOOK_SAFETY_LANGUAGE_MISSING = "LOCAL_RUNBOOK_SAFETY_LANGUAGE_MISSING"
    LOCAL_RUNBOOK_SYNC_COMMANDS_MISSING = "LOCAL_RUNBOOK_SYNC_COMMANDS_MISSING"
    LOCAL_RUNBOOK_TEST_COMMANDS_MISSING = "LOCAL_RUNBOOK_TEST_COMMANDS_MISSING"
    LOCAL_RUNBOOK_SMOKE_DEMO_MISSING = "LOCAL_RUNBOOK_SMOKE_DEMO_MISSING"
    LOCAL_RUNBOOK_INTERPRETATION_MISSING = "LOCAL_RUNBOOK_INTERPRETATION_MISSING"
    LOCAL_RUNBOOK_DIAGNOSTICS_MISSING = "LOCAL_RUNBOOK_DIAGNOSTICS_MISSING"
    LOCAL_RUNBOOK_GIT_RULES_MISSING = "LOCAL_RUNBOOK_GIT_RULES_MISSING"
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


class AGIcoreTradingV1OfflineLocalRunbookRecommendation(StrEnum):
    PROVIDE_LOCAL_RUNBOOK_INPUT = "PROVIDE_LOCAL_RUNBOOK_INPUT"
    RESTORE_LOCAL_RUNBOOK_SAFETY_LANGUAGE = "RESTORE_LOCAL_RUNBOOK_SAFETY_LANGUAGE"
    RESTORE_LOCAL_RUNBOOK_SYNC_COMMANDS = "RESTORE_LOCAL_RUNBOOK_SYNC_COMMANDS"
    RESTORE_LOCAL_RUNBOOK_TEST_COMMANDS = "RESTORE_LOCAL_RUNBOOK_TEST_COMMANDS"
    RESTORE_LOCAL_RUNBOOK_SMOKE_DEMO = "RESTORE_LOCAL_RUNBOOK_SMOKE_DEMO"
    RESTORE_LOCAL_RUNBOOK_INTERPRETATION = "RESTORE_LOCAL_RUNBOOK_INTERPRETATION"
    RESTORE_LOCAL_RUNBOOK_DIAGNOSTICS = "RESTORE_LOCAL_RUNBOOK_DIAGNOSTICS"
    RESTORE_LOCAL_RUNBOOK_GIT_RULES = "RESTORE_LOCAL_RUNBOOK_GIT_RULES"
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
    PREPARE_AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_REVIEW = (
        "PREPARE_AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_REVIEW"
    )


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineLocalRunbookScore:
    overall_score: int
    input_score: int
    safety_score: int
    sync_score: int
    test_command_score: int
    smoke_demo_score: int
    interpretation_score: int
    diagnostic_score: int
    git_rule_score: int
    overclaim_score: int
    boundary_score: int


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineLocalRunbookContext:
    title: str
    status: str
    next_step: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineLocalRunbookSection:
    name: str
    content: str
    required: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineLocalRunbookCommand:
    command: str
    description: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineLocalRunbookSafetyRule:
    text: str
    explicit: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineLocalRunbookDiagnosticRule:
    symptom: str
    action: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineLocalRunbookGitRule:
    text: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineLocalRunbookKnownLimitation:
    text: str
    documented: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineLocalRunbookReport:
    markdown: str
    json: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineLocalRunbookInput:
    runbook_id: str = "agicore-trading-v1-offline-local-runbook"
    force_safety_language_missing: bool = False
    force_sync_commands_missing: bool = False
    force_test_commands_missing: bool = False
    force_smoke_demo_missing: bool = False
    force_interpretation_missing: bool = False
    force_diagnostics_missing: bool = False
    force_git_rules_missing: bool = False
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
class AGIcoreTradingV1OfflineLocalRunbookResult:
    state: AGIcoreTradingV1OfflineLocalRunbookState
    decision: AGIcoreTradingV1OfflineLocalRunbookDecision
    score: AGIcoreTradingV1OfflineLocalRunbookScore
    risks: tuple[AGIcoreTradingV1OfflineLocalRunbookRisk, ...]
    recommendations: tuple[AGIcoreTradingV1OfflineLocalRunbookRecommendation, ...]
    context: AGIcoreTradingV1OfflineLocalRunbookContext | None = None
    sections: tuple[AGIcoreTradingV1OfflineLocalRunbookSection, ...] = ()
    sync_commands: tuple[AGIcoreTradingV1OfflineLocalRunbookCommand, ...] = ()
    test_commands: tuple[AGIcoreTradingV1OfflineLocalRunbookCommand, ...] = ()
    safety_rules: tuple[AGIcoreTradingV1OfflineLocalRunbookSafetyRule, ...] = ()
    diagnostic_rules: tuple[AGIcoreTradingV1OfflineLocalRunbookDiagnosticRule, ...] = ()
    git_rules: tuple[AGIcoreTradingV1OfflineLocalRunbookGitRule, ...] = ()
    known_limitations: tuple[AGIcoreTradingV1OfflineLocalRunbookKnownLimitation, ...] = ()
    report: AGIcoreTradingV1OfflineLocalRunbookReport | None = None
    file_read: bool = False
    data_accessed: bool = False
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False
    next_phase: str = "AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_REVIEW"
