"""Models for AGIcore Trading v1 offline human tag go/no-go."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AGIcoreTradingV1OfflineHumanTagGoNoGoState(StrEnum):
    NOT_READY = "NOT_READY"
    AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO_INPUT_INVALID = (
        "AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO_INPUT_INVALID"
    )
    AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO_BLOCKED = "AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO_BLOCKED"
    AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO_COMPLETED_WITH_WARNINGS = (
        "AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO_COMPLETED_WITH_WARNINGS"
    )
    AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO_COMPLETED = "AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO_COMPLETED"
    READY_FOR_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_FINAL_CHECKLIST = (
        "READY_FOR_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_FINAL_CHECKLIST"
    )


class AGIcoreTradingV1OfflineHumanTagGoNoGoDecision(StrEnum):
    BLOCK_AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO = "BLOCK_AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO"
    REQUIRE_HUMAN_TAG_INPUT_FIXES = "REQUIRE_HUMAN_TAG_INPUT_FIXES"
    REQUIRE_HUMAN_TAG_PREREQUISITE_FIXES = "REQUIRE_HUMAN_TAG_PREREQUISITE_FIXES"
    REQUIRE_HUMAN_TAG_NAME_FIXES = "REQUIRE_HUMAN_TAG_NAME_FIXES"
    REQUIRE_HUMAN_TAG_VERSION_FIXES = "REQUIRE_HUMAN_TAG_VERSION_FIXES"
    REQUIRE_HUMAN_TAG_GUARDRAIL_FIXES = "REQUIRE_HUMAN_TAG_GUARDRAIL_FIXES"
    REQUIRE_HUMAN_TAG_NO_OVERCLAIM_FIXES = "REQUIRE_HUMAN_TAG_NO_OVERCLAIM_FIXES"
    APPROVE_AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO = "APPROVE_AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO"


class AGIcoreTradingV1OfflineHumanTagGoNoGoRisk(StrEnum):
    HUMAN_TAG_GO_NO_GO_INPUT_MISSING = "HUMAN_TAG_GO_NO_GO_INPUT_MISSING"
    HUMAN_TAG_PREREQUISITES_INCOMPLETE = "HUMAN_TAG_PREREQUISITES_INCOMPLETE"
    FINAL_TAG_REVIEW_NOT_APPROVED = "FINAL_TAG_REVIEW_NOT_APPROVED"
    TAG_CREATION_INSTRUCTIONS_REVIEW_NOT_APPROVED = "TAG_CREATION_INSTRUCTIONS_REVIEW_NOT_APPROVED"
    RELEASE_PACKAGE_REVIEW_NOT_APPROVED = "RELEASE_PACKAGE_REVIEW_NOT_APPROVED"
    FINAL_READINESS_REVIEW_NOT_APPROVED = "FINAL_READINESS_REVIEW_NOT_APPROVED"
    HUMAN_TAG_NAME_INVALID = "HUMAN_TAG_NAME_INVALID"
    HUMAN_TAG_VERSION_INVALID = "HUMAN_TAG_VERSION_INVALID"
    HUMAN_TAG_GUARDRAILS_MISSING = "HUMAN_TAG_GUARDRAILS_MISSING"
    GIT_TAG_ALREADY_CREATED = "GIT_TAG_ALREADY_CREATED"
    GIT_TAG_ALREADY_PUSHED = "GIT_TAG_ALREADY_PUSHED"
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


class AGIcoreTradingV1OfflineHumanTagGoNoGoRecommendation(StrEnum):
    PROVIDE_HUMAN_TAG_GO_NO_GO_INPUT = "PROVIDE_HUMAN_TAG_GO_NO_GO_INPUT"
    RESTORE_HUMAN_TAG_PREREQUISITES = "RESTORE_HUMAN_TAG_PREREQUISITES"
    RESTORE_FINAL_TAG_REVIEW_APPROVAL = "RESTORE_FINAL_TAG_REVIEW_APPROVAL"
    RESTORE_TAG_CREATION_INSTRUCTIONS_REVIEW_APPROVAL = "RESTORE_TAG_CREATION_INSTRUCTIONS_REVIEW_APPROVAL"
    RESTORE_RELEASE_PACKAGE_REVIEW_APPROVAL = "RESTORE_RELEASE_PACKAGE_REVIEW_APPROVAL"
    RESTORE_FINAL_READINESS_REVIEW_APPROVAL = "RESTORE_FINAL_READINESS_REVIEW_APPROVAL"
    RESTORE_HUMAN_TAG_NAME = "RESTORE_HUMAN_TAG_NAME"
    RESTORE_HUMAN_TAG_VERSION = "RESTORE_HUMAN_TAG_VERSION"
    RESTORE_HUMAN_TAG_GUARDRAILS = "RESTORE_HUMAN_TAG_GUARDRAILS"
    DO_NOT_CREATE_GIT_TAG_IN_THIS_PHASE = "DO_NOT_CREATE_GIT_TAG_IN_THIS_PHASE"
    DO_NOT_PUSH_GIT_TAG_IN_THIS_PHASE = "DO_NOT_PUSH_GIT_TAG_IN_THIS_PHASE"
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
    PREPARE_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_FINAL_CHECKLIST = (
        "PREPARE_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_FINAL_CHECKLIST"
    )


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineHumanTagGoNoGoScore:
    overall_score: int
    input_score: int
    prerequisite_score: int
    tag_name_score: int
    version_score: int
    go_decision_score: int
    guardrail_score: int
    no_tag_score: int
    safety_score: int
    boundary_score: int


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineHumanTagGoNoGoPrerequisite:
    name: str
    approved: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineHumanTagGoNoGoCriterion:
    name: str
    passed: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineHumanTagGoNoGoFinding:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineHumanTagGoNoGoTagMetadata:
    tag_name: str
    version: str
    human_decision: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineHumanTagGoNoGoGuardrail:
    name: str
    present: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineHumanTagGoNoGoContext:
    decision_id: str
    tag_metadata: AGIcoreTradingV1OfflineHumanTagGoNoGoTagMetadata
    prerequisites: tuple[AGIcoreTradingV1OfflineHumanTagGoNoGoPrerequisite, ...]
    guardrails: tuple[AGIcoreTradingV1OfflineHumanTagGoNoGoGuardrail, ...]
    criteria: tuple[AGIcoreTradingV1OfflineHumanTagGoNoGoCriterion, ...]


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineHumanTagGoNoGoReport:
    markdown: str
    json: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineHumanTagGoNoGoInput:
    decision_id: str = "agicore-trading-v1-offline-human-tag-go-no-go"
    prerequisites_complete: bool = True
    final_tag_review_approved: bool = True
    tag_creation_instructions_approved: bool = True
    tag_creation_instructions_review_approved: bool = True
    release_package_approved: bool = True
    release_package_review_approved: bool = True
    final_readiness_review_approved: bool = True
    tag_name: str = "agicore-trading-v1-offline"
    version: str = "v1.0.0-offline"
    human_go_decision: str = "GO_FOR_MANUAL_TAG_CREATION_LATER"
    guardrails_present: bool = True
    git_tag_already_created: bool = False
    git_tag_already_pushed: bool = False
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
class AGIcoreTradingV1OfflineHumanTagGoNoGoResult:
    state: AGIcoreTradingV1OfflineHumanTagGoNoGoState
    decision: AGIcoreTradingV1OfflineHumanTagGoNoGoDecision
    score: AGIcoreTradingV1OfflineHumanTagGoNoGoScore
    risks: tuple[AGIcoreTradingV1OfflineHumanTagGoNoGoRisk, ...]
    recommendations: tuple[AGIcoreTradingV1OfflineHumanTagGoNoGoRecommendation, ...]
    context: AGIcoreTradingV1OfflineHumanTagGoNoGoContext | None = None
    findings: tuple[AGIcoreTradingV1OfflineHumanTagGoNoGoFinding, ...] = ()
    report: AGIcoreTradingV1OfflineHumanTagGoNoGoReport | None = None
    file_read: bool = False
    data_accessed: bool = False
    git_tag_created: bool = False
    git_tag_pushed: bool = False
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False
    next_phase: str = "AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_FINAL_CHECKLIST"
