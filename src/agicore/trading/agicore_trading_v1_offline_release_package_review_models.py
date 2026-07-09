"""Models for AGIcore Trading v1 offline release package review."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AGIcoreTradingV1OfflineReleasePackageReviewState(StrEnum):
    NOT_READY = "NOT_READY"
    AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW_INPUT_INVALID = (
        "AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW_INPUT_INVALID"
    )
    AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW_BLOCKED = (
        "AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW_BLOCKED"
    )
    AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW_COMPLETED_WITH_WARNINGS = (
        "AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW_COMPLETED_WITH_WARNINGS"
    )
    AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW_COMPLETED = (
        "AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW_COMPLETED"
    )
    READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION = "READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION"


class AGIcoreTradingV1OfflineReleasePackageReviewDecision(StrEnum):
    BLOCK_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW = (
        "BLOCK_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW"
    )
    REQUIRE_RELEASE_PACKAGE_REVIEW_INPUT_FIXES = "REQUIRE_RELEASE_PACKAGE_REVIEW_INPUT_FIXES"
    REQUIRE_RELEASE_PACKAGE_DOCUMENT_REVIEW_FIXES = "REQUIRE_RELEASE_PACKAGE_DOCUMENT_REVIEW_FIXES"
    REQUIRE_RELEASE_PACKAGE_CAPABILITY_REVIEW_FIXES = "REQUIRE_RELEASE_PACKAGE_CAPABILITY_REVIEW_FIXES"
    REQUIRE_RELEASE_PACKAGE_TESTING_EVIDENCE_REVIEW_FIXES = "REQUIRE_RELEASE_PACKAGE_TESTING_EVIDENCE_REVIEW_FIXES"
    REQUIRE_RELEASE_PACKAGE_COMMAND_REVIEW_FIXES = "REQUIRE_RELEASE_PACKAGE_COMMAND_REVIEW_FIXES"
    REQUIRE_RELEASE_PACKAGE_SAFETY_REVIEW_FIXES = "REQUIRE_RELEASE_PACKAGE_SAFETY_REVIEW_FIXES"
    REQUIRE_RELEASE_PACKAGE_LIMITATION_REVIEW_FIXES = "REQUIRE_RELEASE_PACKAGE_LIMITATION_REVIEW_FIXES"
    REQUIRE_RELEASE_PACKAGE_NO_OVERCLAIM_FIXES = "REQUIRE_RELEASE_PACKAGE_NO_OVERCLAIM_FIXES"
    APPROVE_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW = (
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW"
    )


class AGIcoreTradingV1OfflineReleasePackageReviewRisk(StrEnum):
    RELEASE_PACKAGE_REVIEW_INPUT_MISSING = "RELEASE_PACKAGE_REVIEW_INPUT_MISSING"
    RELEASE_PACKAGE_DOCUMENT_REVIEW_INCOMPLETE = "RELEASE_PACKAGE_DOCUMENT_REVIEW_INCOMPLETE"
    RELEASE_PACKAGE_CAPABILITY_REVIEW_INCOMPLETE = "RELEASE_PACKAGE_CAPABILITY_REVIEW_INCOMPLETE"
    RELEASE_PACKAGE_TESTING_EVIDENCE_REVIEW_MISSING = "RELEASE_PACKAGE_TESTING_EVIDENCE_REVIEW_MISSING"
    RELEASE_PACKAGE_COMMAND_REVIEW_MISSING = "RELEASE_PACKAGE_COMMAND_REVIEW_MISSING"
    RELEASE_PACKAGE_SAFETY_REVIEW_MISSING = "RELEASE_PACKAGE_SAFETY_REVIEW_MISSING"
    RELEASE_PACKAGE_LIMITATION_REVIEW_MISSING = "RELEASE_PACKAGE_LIMITATION_REVIEW_MISSING"
    RELEASE_PACKAGE_NON_GOAL_REVIEW_MISSING = "RELEASE_PACKAGE_NON_GOAL_REVIEW_MISSING"
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


class AGIcoreTradingV1OfflineReleasePackageReviewRecommendation(StrEnum):
    PROVIDE_RELEASE_PACKAGE_REVIEW_INPUT = "PROVIDE_RELEASE_PACKAGE_REVIEW_INPUT"
    RESTORE_RELEASE_PACKAGE_DOCUMENT_REVIEW = "RESTORE_RELEASE_PACKAGE_DOCUMENT_REVIEW"
    RESTORE_RELEASE_PACKAGE_CAPABILITY_REVIEW = "RESTORE_RELEASE_PACKAGE_CAPABILITY_REVIEW"
    RESTORE_RELEASE_PACKAGE_TESTING_EVIDENCE_REVIEW = "RESTORE_RELEASE_PACKAGE_TESTING_EVIDENCE_REVIEW"
    RESTORE_RELEASE_PACKAGE_COMMAND_REVIEW = "RESTORE_RELEASE_PACKAGE_COMMAND_REVIEW"
    RESTORE_RELEASE_PACKAGE_SAFETY_REVIEW = "RESTORE_RELEASE_PACKAGE_SAFETY_REVIEW"
    RESTORE_RELEASE_PACKAGE_LIMITATION_REVIEW = "RESTORE_RELEASE_PACKAGE_LIMITATION_REVIEW"
    RESTORE_RELEASE_PACKAGE_NON_GOAL_REVIEW = "RESTORE_RELEASE_PACKAGE_NON_GOAL_REVIEW"
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
    PREPARE_AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION = "PREPARE_AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION"


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleasePackageReviewScore:
    overall_score: int
    input_score: int
    document_score: int
    capability_score: int
    testing_evidence_score: int
    command_score: int
    safety_score: int
    limitation_score: int
    non_goal_score: int
    readability_score: int
    overclaim_score: int
    boundary_score: int


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleasePackageReviewContext:
    title: str
    status: str
    expected_decision: str
    next_step: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleasePackageReviewDocument:
    name: str
    verified: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleasePackageReviewCapability:
    name: str
    verified: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleasePackageReviewTestingEvidence:
    name: str
    result: str
    verified: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleasePackageReviewCriterion:
    text: str
    satisfied: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleasePackageReviewFinding:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleasePackageReviewReport:
    markdown: str
    json: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleasePackageReviewInput:
    review_id: str = "agicore-trading-v1-offline-release-package-review"
    force_documents_incomplete: bool = False
    force_capabilities_incomplete: bool = False
    force_testing_evidence_missing: bool = False
    force_commands_missing: bool = False
    force_safety_missing: bool = False
    force_limitations_missing: bool = False
    force_non_goals_missing: bool = False
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
class AGIcoreTradingV1OfflineReleasePackageReviewResult:
    state: AGIcoreTradingV1OfflineReleasePackageReviewState
    decision: AGIcoreTradingV1OfflineReleasePackageReviewDecision
    score: AGIcoreTradingV1OfflineReleasePackageReviewScore
    risks: tuple[AGIcoreTradingV1OfflineReleasePackageReviewRisk, ...]
    recommendations: tuple[AGIcoreTradingV1OfflineReleasePackageReviewRecommendation, ...]
    context: AGIcoreTradingV1OfflineReleasePackageReviewContext | None = None
    documents: tuple[AGIcoreTradingV1OfflineReleasePackageReviewDocument, ...] = ()
    capabilities: tuple[AGIcoreTradingV1OfflineReleasePackageReviewCapability, ...] = ()
    testing_evidence: tuple[AGIcoreTradingV1OfflineReleasePackageReviewTestingEvidence, ...] = ()
    criteria: tuple[AGIcoreTradingV1OfflineReleasePackageReviewCriterion, ...] = ()
    findings: tuple[AGIcoreTradingV1OfflineReleasePackageReviewFinding, ...] = ()
    report: AGIcoreTradingV1OfflineReleasePackageReviewReport | None = None
    file_read: bool = False
    data_accessed: bool = False
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False
    next_phase: str = "AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION"
