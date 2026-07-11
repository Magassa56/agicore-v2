"""Models for AGIcore Trading v1 offline tag creation instructions review."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AGIcoreTradingV1OfflineTagCreationInstructionsReviewState(StrEnum):
    NOT_READY = "NOT_READY"
    AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW_INPUT_INVALID = (
        "AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW_INPUT_INVALID"
    )
    AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW_BLOCKED = (
        "AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW_BLOCKED"
    )
    AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW_COMPLETED_WITH_WARNINGS = (
        "AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW_COMPLETED_WITH_WARNINGS"
    )
    AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW_COMPLETED = (
        "AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW_COMPLETED"
    )
    READY_FOR_AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO = (
        "READY_FOR_AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO"
    )


class AGIcoreTradingV1OfflineTagCreationInstructionsReviewDecision(StrEnum):
    BLOCK_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW = (
        "BLOCK_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW"
    )
    REQUIRE_TAG_CREATION_INSTRUCTIONS_REVIEW_INPUT_FIXES = (
        "REQUIRE_TAG_CREATION_INSTRUCTIONS_REVIEW_INPUT_FIXES"
    )
    REQUIRE_TAG_CREATION_INSTRUCTIONS_FIXES = "REQUIRE_TAG_CREATION_INSTRUCTIONS_FIXES"
    REQUIRE_TAG_CREATION_TAG_NAME_FIXES = "REQUIRE_TAG_CREATION_TAG_NAME_FIXES"
    REQUIRE_TAG_CREATION_VERSION_FIXES = "REQUIRE_TAG_CREATION_VERSION_FIXES"
    REQUIRE_TAG_CREATION_PRE_CHECK_FIXES = "REQUIRE_TAG_CREATION_PRE_CHECK_FIXES"
    REQUIRE_TAG_CREATION_COMMAND_DOCUMENTATION_FIXES = "REQUIRE_TAG_CREATION_COMMAND_DOCUMENTATION_FIXES"
    REQUIRE_TAG_CREATION_HUMAN_GUARDRAIL_FIXES = "REQUIRE_TAG_CREATION_HUMAN_GUARDRAIL_FIXES"
    REQUIRE_TAG_CREATION_NO_OVERCLAIM_FIXES = "REQUIRE_TAG_CREATION_NO_OVERCLAIM_FIXES"
    APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW = (
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW"
    )


class AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk(StrEnum):
    TAG_CREATION_INSTRUCTIONS_REVIEW_INPUT_MISSING = "TAG_CREATION_INSTRUCTIONS_REVIEW_INPUT_MISSING"
    TAG_CREATION_INSTRUCTIONS_NOT_APPROVED = "TAG_CREATION_INSTRUCTIONS_NOT_APPROVED"
    TAG_CREATION_INSTRUCTIONS_DOCUMENT_MISSING = "TAG_CREATION_INSTRUCTIONS_DOCUMENT_MISSING"
    TAG_CREATION_TAG_NAME_INVALID = "TAG_CREATION_TAG_NAME_INVALID"
    TAG_CREATION_VERSION_INVALID = "TAG_CREATION_VERSION_INVALID"
    TAG_CREATION_PRE_CHECKS_MISSING = "TAG_CREATION_PRE_CHECKS_MISSING"
    TAG_CREATION_COMMANDS_NOT_DOCUMENTATION_ONLY = "TAG_CREATION_COMMANDS_NOT_DOCUMENTATION_ONLY"
    TAG_CREATION_POST_CHECKS_MISSING = "TAG_CREATION_POST_CHECKS_MISSING"
    TAG_CREATION_HUMAN_GUARDRAILS_MISSING = "TAG_CREATION_HUMAN_GUARDRAILS_MISSING"
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


class AGIcoreTradingV1OfflineTagCreationInstructionsReviewRecommendation(StrEnum):
    PROVIDE_TAG_CREATION_INSTRUCTIONS_REVIEW_INPUT = "PROVIDE_TAG_CREATION_INSTRUCTIONS_REVIEW_INPUT"
    RESTORE_TAG_CREATION_INSTRUCTIONS_APPROVAL = "RESTORE_TAG_CREATION_INSTRUCTIONS_APPROVAL"
    RESTORE_TAG_CREATION_INSTRUCTIONS_DOCUMENT = "RESTORE_TAG_CREATION_INSTRUCTIONS_DOCUMENT"
    RESTORE_TAG_CREATION_TAG_NAME = "RESTORE_TAG_CREATION_TAG_NAME"
    RESTORE_TAG_CREATION_VERSION = "RESTORE_TAG_CREATION_VERSION"
    RESTORE_TAG_CREATION_PRE_CHECKS = "RESTORE_TAG_CREATION_PRE_CHECKS"
    KEEP_TAG_COMMANDS_DOCUMENTATION_ONLY = "KEEP_TAG_COMMANDS_DOCUMENTATION_ONLY"
    RESTORE_TAG_CREATION_POST_CHECKS = "RESTORE_TAG_CREATION_POST_CHECKS"
    RESTORE_TAG_CREATION_HUMAN_GUARDRAILS = "RESTORE_TAG_CREATION_HUMAN_GUARDRAILS"
    DO_NOT_CREATE_GIT_TAG_IN_REVIEW = "DO_NOT_CREATE_GIT_TAG_IN_REVIEW"
    DO_NOT_PUSH_GIT_TAG_IN_REVIEW = "DO_NOT_PUSH_GIT_TAG_IN_REVIEW"
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
    PREPARE_AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO = (
        "PREPARE_AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO"
    )


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationInstructionsReviewScore:
    overall_score: int
    input_score: int
    approval_score: int
    document_score: int
    tag_name_score: int
    version_score: int
    pre_check_score: int
    command_score: int
    post_check_score: int
    guardrail_score: int
    no_tag_score: int
    safety_score: int
    boundary_score: int


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationInstructionsReviewTagMetadata:
    tag_name: str
    version: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationInstructionsReviewCommand:
    command: str
    documentation_only: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationInstructionsReviewGuardrail:
    name: str
    present: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationInstructionsReviewCriterion:
    name: str
    passed: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationInstructionsReviewFinding:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationInstructionsReviewContext:
    review_id: str
    prerequisite_decision: str
    tag_metadata: AGIcoreTradingV1OfflineTagCreationInstructionsReviewTagMetadata
    pre_checks: tuple[str, ...]
    commands: tuple[AGIcoreTradingV1OfflineTagCreationInstructionsReviewCommand, ...]
    post_checks: tuple[str, ...]
    guardrails: tuple[AGIcoreTradingV1OfflineTagCreationInstructionsReviewGuardrail, ...]
    criteria: tuple[AGIcoreTradingV1OfflineTagCreationInstructionsReviewCriterion, ...]


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationInstructionsReviewReport:
    markdown: str
    json: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationInstructionsReviewInput:
    review_id: str = "agicore-trading-v1-offline-tag-creation-instructions-review"
    instructions_approved: bool = True
    instructions_document_present: bool = True
    tag_name: str = "agicore-trading-v1-offline"
    version: str = "v1.0.0-offline"
    pre_checks_present: bool = True
    commands_documentation_only: bool = True
    post_checks_present: bool = True
    human_guardrails_present: bool = True
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
class AGIcoreTradingV1OfflineTagCreationInstructionsReviewResult:
    state: AGIcoreTradingV1OfflineTagCreationInstructionsReviewState
    decision: AGIcoreTradingV1OfflineTagCreationInstructionsReviewDecision
    score: AGIcoreTradingV1OfflineTagCreationInstructionsReviewScore
    risks: tuple[AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk, ...]
    recommendations: tuple[AGIcoreTradingV1OfflineTagCreationInstructionsReviewRecommendation, ...]
    context: AGIcoreTradingV1OfflineTagCreationInstructionsReviewContext | None = None
    findings: tuple[AGIcoreTradingV1OfflineTagCreationInstructionsReviewFinding, ...] = ()
    report: AGIcoreTradingV1OfflineTagCreationInstructionsReviewReport | None = None
    file_read: bool = False
    data_accessed: bool = False
    git_tag_created: bool = False
    git_tag_pushed: bool = False
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False
    next_phase: str = "AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO"
