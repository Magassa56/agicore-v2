"""Models for AGIcore Trading v1 offline release package."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AGIcoreTradingV1OfflineReleasePackageState(StrEnum):
    NOT_READY = "NOT_READY"
    AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_INPUT_INVALID = "AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_INPUT_INVALID"
    AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_BLOCKED = "AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_BLOCKED"
    AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_COMPLETED_WITH_WARNINGS = (
        "AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_COMPLETED_WITH_WARNINGS"
    )
    AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_COMPLETED = "AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_COMPLETED"
    READY_FOR_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW = (
        "READY_FOR_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW"
    )


class AGIcoreTradingV1OfflineReleasePackageDecision(StrEnum):
    BLOCK_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE = "BLOCK_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE"
    REQUIRE_RELEASE_PACKAGE_INPUT_FIXES = "REQUIRE_RELEASE_PACKAGE_INPUT_FIXES"
    REQUIRE_RELEASE_PACKAGE_DOCUMENT_FIXES = "REQUIRE_RELEASE_PACKAGE_DOCUMENT_FIXES"
    REQUIRE_RELEASE_PACKAGE_CAPABILITY_FIXES = "REQUIRE_RELEASE_PACKAGE_CAPABILITY_FIXES"
    REQUIRE_RELEASE_PACKAGE_TESTING_EVIDENCE_FIXES = "REQUIRE_RELEASE_PACKAGE_TESTING_EVIDENCE_FIXES"
    REQUIRE_RELEASE_PACKAGE_COMMAND_FIXES = "REQUIRE_RELEASE_PACKAGE_COMMAND_FIXES"
    REQUIRE_RELEASE_PACKAGE_SAFETY_FIXES = "REQUIRE_RELEASE_PACKAGE_SAFETY_FIXES"
    REQUIRE_RELEASE_PACKAGE_LIMITATION_FIXES = "REQUIRE_RELEASE_PACKAGE_LIMITATION_FIXES"
    REQUIRE_RELEASE_PACKAGE_NO_OVERCLAIM_FIXES = "REQUIRE_RELEASE_PACKAGE_NO_OVERCLAIM_FIXES"
    APPROVE_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE = "APPROVE_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE"


class AGIcoreTradingV1OfflineReleasePackageRisk(StrEnum):
    RELEASE_PACKAGE_INPUT_MISSING = "RELEASE_PACKAGE_INPUT_MISSING"
    RELEASE_PACKAGE_DOCUMENTS_MISSING = "RELEASE_PACKAGE_DOCUMENTS_MISSING"
    RELEASE_PACKAGE_CAPABILITIES_MISSING = "RELEASE_PACKAGE_CAPABILITIES_MISSING"
    RELEASE_PACKAGE_TESTING_EVIDENCE_MISSING = "RELEASE_PACKAGE_TESTING_EVIDENCE_MISSING"
    RELEASE_PACKAGE_COMMANDS_MISSING = "RELEASE_PACKAGE_COMMANDS_MISSING"
    RELEASE_PACKAGE_SAFETY_LANGUAGE_MISSING = "RELEASE_PACKAGE_SAFETY_LANGUAGE_MISSING"
    RELEASE_PACKAGE_LIMITATIONS_MISSING = "RELEASE_PACKAGE_LIMITATIONS_MISSING"
    LIVE_TRADING_READINESS_OVERCLAIM = "LIVE_TRADING_READINESS_OVERCLAIM"
    REAL_BROKER_READINESS_OVERCLAIM = "REAL_BROKER_READINESS_OVERCLAIM"
    REAL_ORDER_EXECUTION_OVERCLAIM = "REAL_ORDER_EXECUTION_OVERCLAIM"
    PAPER_BROKER_CONNECTION_OVERCLAIM = "PAPER_BROKER_CONNECTION_OVERCLAIM"
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


class AGIcoreTradingV1OfflineReleasePackageRecommendation(StrEnum):
    PROVIDE_RELEASE_PACKAGE_INPUT = "PROVIDE_RELEASE_PACKAGE_INPUT"
    RESTORE_RELEASE_PACKAGE_DOCUMENTS = "RESTORE_RELEASE_PACKAGE_DOCUMENTS"
    RESTORE_RELEASE_PACKAGE_CAPABILITIES = "RESTORE_RELEASE_PACKAGE_CAPABILITIES"
    RESTORE_RELEASE_PACKAGE_TESTING_EVIDENCE = "RESTORE_RELEASE_PACKAGE_TESTING_EVIDENCE"
    RESTORE_RELEASE_PACKAGE_COMMANDS = "RESTORE_RELEASE_PACKAGE_COMMANDS"
    RESTORE_RELEASE_PACKAGE_SAFETY_LANGUAGE = "RESTORE_RELEASE_PACKAGE_SAFETY_LANGUAGE"
    RESTORE_RELEASE_PACKAGE_LIMITATIONS = "RESTORE_RELEASE_PACKAGE_LIMITATIONS"
    REMOVE_LIVE_TRADING_READINESS_CLAIM = "REMOVE_LIVE_TRADING_READINESS_CLAIM"
    REMOVE_REAL_BROKER_READINESS_CLAIM = "REMOVE_REAL_BROKER_READINESS_CLAIM"
    REMOVE_REAL_ORDER_EXECUTION_CLAIM = "REMOVE_REAL_ORDER_EXECUTION_CLAIM"
    REMOVE_PAPER_BROKER_CONNECTION_CLAIM = "REMOVE_PAPER_BROKER_CONNECTION_CLAIM"
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
    PREPARE_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW = (
        "PREPARE_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW"
    )


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleasePackageScore:
    overall_score: int
    input_score: int
    document_score: int
    capability_score: int
    testing_evidence_score: int
    command_score: int
    safety_score: int
    limitation_score: int
    non_goal_score: int
    overclaim_score: int
    boundary_score: int


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleasePackageContext:
    title: str
    status: str
    next_step: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleasePackageDocument:
    name: str
    included: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleasePackageCapability:
    name: str
    delivered: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleasePackageTestingEvidence:
    name: str
    result: str
    validated: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleasePackageCommand:
    command: str
    description: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleasePackageSafetyRule:
    text: str
    explicit: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleasePackageKnownLimitation:
    text: str
    documented: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleasePackageNonGoal:
    text: str
    explicit: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleasePackageReport:
    markdown: str
    json: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleasePackageInput:
    package_id: str = "agicore-trading-v1-offline-release-package"
    force_documents_missing: bool = False
    force_capabilities_missing: bool = False
    force_testing_evidence_missing: bool = False
    force_commands_missing: bool = False
    force_safety_language_missing: bool = False
    force_limitations_missing: bool = False
    force_live_trading_overclaim: bool = False
    force_real_broker_overclaim: bool = False
    force_real_order_overclaim: bool = False
    force_paper_broker_overclaim: bool = False
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
class AGIcoreTradingV1OfflineReleasePackageResult:
    state: AGIcoreTradingV1OfflineReleasePackageState
    decision: AGIcoreTradingV1OfflineReleasePackageDecision
    score: AGIcoreTradingV1OfflineReleasePackageScore
    risks: tuple[AGIcoreTradingV1OfflineReleasePackageRisk, ...]
    recommendations: tuple[AGIcoreTradingV1OfflineReleasePackageRecommendation, ...]
    context: AGIcoreTradingV1OfflineReleasePackageContext | None = None
    documents: tuple[AGIcoreTradingV1OfflineReleasePackageDocument, ...] = ()
    capabilities: tuple[AGIcoreTradingV1OfflineReleasePackageCapability, ...] = ()
    testing_evidence: tuple[AGIcoreTradingV1OfflineReleasePackageTestingEvidence, ...] = ()
    commands: tuple[AGIcoreTradingV1OfflineReleasePackageCommand, ...] = ()
    safety_rules: tuple[AGIcoreTradingV1OfflineReleasePackageSafetyRule, ...] = ()
    known_limitations: tuple[AGIcoreTradingV1OfflineReleasePackageKnownLimitation, ...] = ()
    non_goals: tuple[AGIcoreTradingV1OfflineReleasePackageNonGoal, ...] = ()
    report: AGIcoreTradingV1OfflineReleasePackageReport | None = None
    file_read: bool = False
    data_accessed: bool = False
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False
    next_phase: str = "AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW"
