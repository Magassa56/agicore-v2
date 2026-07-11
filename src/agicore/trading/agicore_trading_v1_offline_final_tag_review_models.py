"""Models for AGIcore Trading v1 offline final tag review."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AGIcoreTradingV1OfflineFinalTagReviewState(StrEnum):
    NOT_READY = "NOT_READY"
    AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW_INPUT_INVALID = (
        "AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW_INPUT_INVALID"
    )
    AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW_BLOCKED = "AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW_BLOCKED"
    AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW_COMPLETED_WITH_WARNINGS = (
        "AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW_COMPLETED_WITH_WARNINGS"
    )
    AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW_COMPLETED = "AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW_COMPLETED"
    READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS = (
        "READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS"
    )


class AGIcoreTradingV1OfflineFinalTagReviewDecision(StrEnum):
    BLOCK_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW = "BLOCK_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW"
    REQUIRE_FINAL_TAG_REVIEW_INPUT_FIXES = "REQUIRE_FINAL_TAG_REVIEW_INPUT_FIXES"
    REQUIRE_FINAL_TAG_PREPARATION_FIXES = "REQUIRE_FINAL_TAG_PREPARATION_FIXES"
    REQUIRE_FINAL_TAG_NAME_FIXES = "REQUIRE_FINAL_TAG_NAME_FIXES"
    REQUIRE_FINAL_TAG_VERSION_FIXES = "REQUIRE_FINAL_TAG_VERSION_FIXES"
    REQUIRE_FINAL_TAG_DOCUMENT_FIXES = "REQUIRE_FINAL_TAG_DOCUMENT_FIXES"
    REQUIRE_FINAL_TAG_RELEASE_PACKAGE_FIXES = "REQUIRE_FINAL_TAG_RELEASE_PACKAGE_FIXES"
    REQUIRE_FINAL_TAG_TESTING_EVIDENCE_FIXES = "REQUIRE_FINAL_TAG_TESTING_EVIDENCE_FIXES"
    REQUIRE_FINAL_TAG_NO_OVERCLAIM_FIXES = "REQUIRE_FINAL_TAG_NO_OVERCLAIM_FIXES"
    APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW = "APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW"


class AGIcoreTradingV1OfflineFinalTagReviewRisk(StrEnum):
    FINAL_TAG_REVIEW_INPUT_MISSING = "FINAL_TAG_REVIEW_INPUT_MISSING"
    FINAL_TAG_PREPARATION_NOT_APPROVED = "FINAL_TAG_PREPARATION_NOT_APPROVED"
    FINAL_TAG_NAME_INVALID = "FINAL_TAG_NAME_INVALID"
    FINAL_TAG_VERSION_INVALID = "FINAL_TAG_VERSION_INVALID"
    FINAL_TAG_DOCUMENTS_MISSING = "FINAL_TAG_DOCUMENTS_MISSING"
    FINAL_TAG_RELEASE_PACKAGE_MISSING = "FINAL_TAG_RELEASE_PACKAGE_MISSING"
    FINAL_TAG_RELEASE_PACKAGE_REVIEW_MISSING = "FINAL_TAG_RELEASE_PACKAGE_REVIEW_MISSING"
    FINAL_TAG_FINAL_READINESS_MISSING = "FINAL_TAG_FINAL_READINESS_MISSING"
    FINAL_TAG_TESTING_EVIDENCE_MISSING = "FINAL_TAG_TESTING_EVIDENCE_MISSING"
    GIT_TAG_ALREADY_CREATED = "GIT_TAG_ALREADY_CREATED"
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


class AGIcoreTradingV1OfflineFinalTagReviewRecommendation(StrEnum):
    PROVIDE_FINAL_TAG_REVIEW_INPUT = "PROVIDE_FINAL_TAG_REVIEW_INPUT"
    RESTORE_FINAL_TAG_PREPARATION_APPROVAL = "RESTORE_FINAL_TAG_PREPARATION_APPROVAL"
    RESTORE_FINAL_TAG_NAME = "RESTORE_FINAL_TAG_NAME"
    RESTORE_FINAL_TAG_VERSION = "RESTORE_FINAL_TAG_VERSION"
    RESTORE_FINAL_TAG_DOCUMENTS = "RESTORE_FINAL_TAG_DOCUMENTS"
    RESTORE_FINAL_TAG_RELEASE_PACKAGE = "RESTORE_FINAL_TAG_RELEASE_PACKAGE"
    RESTORE_FINAL_TAG_RELEASE_PACKAGE_REVIEW = "RESTORE_FINAL_TAG_RELEASE_PACKAGE_REVIEW"
    RESTORE_FINAL_TAG_FINAL_READINESS = "RESTORE_FINAL_TAG_FINAL_READINESS"
    RESTORE_FINAL_TAG_TESTING_EVIDENCE = "RESTORE_FINAL_TAG_TESTING_EVIDENCE"
    DO_NOT_CREATE_GIT_TAG_IN_REVIEW = "DO_NOT_CREATE_GIT_TAG_IN_REVIEW"
    REMOVE_LIVE_TRADING_OVERCLAIM = "REMOVE_LIVE_TRADING_OVERCLAIM"
    REMOVE_REAL_BROKER_OVERCLAIM = "REMOVE_REAL_BROKER_OVERCLAIM"
    REMOVE_REAL_ORDER_OVERCLAIM = "REMOVE_REAL_ORDER_OVERCLAIM"
    REMOVE_PAPER_BROKER_OVERCLAIM = "REMOVE_PAPER_BROKER_OVERCLAIM"
    REMOVE_PROFITABILITY_OVERCLAIM = "REMOVE_PROFITABILITY_OVERCLAIM"
    REMOVE_FINANCIAL_ADVICE_OVERCLAIM = "REMOVE_FINANCIAL_ADVICE_OVERCLAIM"
    REMOVE_FILE_READ = "REMOVE_FILE_READ"
    REMOVE_REAL_DATA_ACCESS = "REMOVE_REAL_DATA_ACCESS"
    REMOVE_DATA_DIRECTORY_ACCESS = "REMOVE_DATA_DIRECTORY_ACCESS"
    REMOVE_REAL_BROKER_ACCESS = "REMOVE_REAL_BROKER_ACCESS"
    REMOVE_REAL_SECRET_ACCESS = "REMOVE_REAL_SECRET_ACCESS"
    REMOVE_NETWORK_ACCESS = "REMOVE_NETWORK_ACCESS"
    REMOVE_ORDER_EXECUTION = "REMOVE_ORDER_EXECUTION"
    REMOVE_ACCOUNT_ACCESS = "REMOVE_ACCOUNT_ACCESS"
    REMOVE_POSITION_MUTATION = "REMOVE_POSITION_MUTATION"
    PREPARE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS = (
        "PREPARE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS"
    )


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalTagReviewScore:
    overall_score: int
    input_score: int
    preparation_score: int
    tag_name_score: int
    version_score: int
    document_score: int
    release_package_score: int
    testing_evidence_score: int
    git_tag_score: int
    safety_score: int
    boundary_score: int


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalTagReviewDocument:
    path: str
    present: bool = True
    coherent: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalTagReviewCriterion:
    name: str
    passed: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalTagReviewFinding:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalTagReviewTestingEvidence:
    command: str
    result: str
    validated: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalTagReviewTagMetadata:
    tag_name: str
    version: str
    git_tag_created: bool
    creation_mode: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalTagReviewContext:
    review_id: str
    tag_metadata: AGIcoreTradingV1OfflineFinalTagReviewTagMetadata
    documents: tuple[AGIcoreTradingV1OfflineFinalTagReviewDocument, ...]
    testing_evidence: tuple[AGIcoreTradingV1OfflineFinalTagReviewTestingEvidence, ...]
    criteria: tuple[AGIcoreTradingV1OfflineFinalTagReviewCriterion, ...]


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalTagReviewReport:
    markdown: str
    json: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalTagReviewInput:
    review_id: str = "agicore-trading-v1-offline-final-tag-review"
    tag_preparation_approved: bool = True
    tag_name: str = "agicore-trading-v1-offline"
    version: str = "v1.0.0-offline"
    documents_present: bool = True
    release_package_validated: bool = True
    release_package_review_validated: bool = True
    final_readiness_validated: bool = True
    testing_evidence_present: bool = True
    git_tag_already_created: bool = False
    safety_language_present: bool = True
    live_trading_overclaim: bool = False
    real_broker_overclaim: bool = False
    real_order_overclaim: bool = False
    paper_broker_overclaim: bool = False
    profitability_overclaim: bool = False
    financial_advice_overclaim: bool = False
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
class AGIcoreTradingV1OfflineFinalTagReviewResult:
    state: AGIcoreTradingV1OfflineFinalTagReviewState
    decision: AGIcoreTradingV1OfflineFinalTagReviewDecision
    score: AGIcoreTradingV1OfflineFinalTagReviewScore
    risks: tuple[AGIcoreTradingV1OfflineFinalTagReviewRisk, ...]
    recommendations: tuple[AGIcoreTradingV1OfflineFinalTagReviewRecommendation, ...]
    context: AGIcoreTradingV1OfflineFinalTagReviewContext | None = None
    findings: tuple[AGIcoreTradingV1OfflineFinalTagReviewFinding, ...] = ()
    report: AGIcoreTradingV1OfflineFinalTagReviewReport | None = None
    file_read: bool = False
    data_accessed: bool = False
    git_tag_created: bool = False
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False
    next_phase: str = "AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS"
