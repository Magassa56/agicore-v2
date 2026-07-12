"""Models for AGIcore Trading v1 offline manual tag creation command sheet review."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewState(StrEnum):
    NOT_READY = "NOT_READY"
    AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_INPUT_INVALID = (
        "AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_INPUT_INVALID"
    )
    AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_BLOCKED = (
        "AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_BLOCKED"
    )
    AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_COMPLETED_WITH_WARNINGS = (
        "AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_COMPLETED_WITH_WARNINGS"
    )
    AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_COMPLETED = (
        "AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_COMPLETED"
    )
    READY_FOR_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION = (
        "READY_FOR_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION"
    )


class AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewDecision(StrEnum):
    BLOCK_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW = (
        "BLOCK_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW"
    )
    REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_INPUT_FIXES = (
        "REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_INPUT_FIXES"
    )
    REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_PREREQUISITE_FIXES = (
        "REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_PREREQUISITE_FIXES"
    )
    REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_TAG_NAME_FIXES = (
        "REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_TAG_NAME_FIXES"
    )
    REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_VERSION_FIXES = (
        "REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_VERSION_FIXES"
    )
    REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_PRE_TAG_COMMAND_FIXES = (
        "REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_PRE_TAG_COMMAND_FIXES"
    )
    REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_EXPECTED_RESULT_FIXES = (
        "REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_EXPECTED_RESULT_FIXES"
    )
    REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_TAG_COMMAND_FIXES = (
        "REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_TAG_COMMAND_FIXES"
    )
    REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_STOP_RULE_FIXES = (
        "REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_STOP_RULE_FIXES"
    )
    REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_NO_OVERCLAIM_FIXES = (
        "REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_NO_OVERCLAIM_FIXES"
    )
    APPROVE_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW = (
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW"
    )


class AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk(StrEnum):
    MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_INPUT_MISSING = (
        "MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_INPUT_MISSING"
    )
    MANUAL_TAG_CREATION_COMMAND_SHEET_NOT_APPROVED = "MANUAL_TAG_CREATION_COMMAND_SHEET_NOT_APPROVED"
    MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_PREREQUISITES_INCOMPLETE = (
        "MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_PREREQUISITES_INCOMPLETE"
    )
    FINAL_MANUAL_TAG_AUTHORIZATION_NOT_APPROVED = "FINAL_MANUAL_TAG_AUTHORIZATION_NOT_APPROVED"
    TAG_CREATION_EXECUTION_PLAN_REVIEW_NOT_APPROVED = "TAG_CREATION_EXECUTION_PLAN_REVIEW_NOT_APPROVED"
    MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED = "MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED"
    HUMAN_TAG_GO_NO_GO_NOT_APPROVED = "HUMAN_TAG_GO_NO_GO_NOT_APPROVED"
    RELEASE_PACKAGE_REVIEW_NOT_APPROVED = "RELEASE_PACKAGE_REVIEW_NOT_APPROVED"
    FINAL_READINESS_REVIEW_NOT_APPROVED = "FINAL_READINESS_REVIEW_NOT_APPROVED"
    MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_TAG_NAME_INVALID = (
        "MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_TAG_NAME_INVALID"
    )
    MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_VERSION_INVALID = (
        "MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_VERSION_INVALID"
    )
    MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_PRE_TAG_COMMANDS_MISSING = (
        "MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_PRE_TAG_COMMANDS_MISSING"
    )
    MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_EXPECTED_RESULTS_MISSING = (
        "MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_EXPECTED_RESULTS_MISSING"
    )
    MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_TAG_COMMANDS_NOT_DOCUMENTATION_ONLY = (
        "MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_TAG_COMMANDS_NOT_DOCUMENTATION_ONLY"
    )
    MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_STOP_RULES_MISSING = (
        "MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_STOP_RULES_MISSING"
    )
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


class AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRecommendation(StrEnum):
    PREPARE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION = "PREPARE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION"
    PROVIDE_COMMAND_SHEET_REVIEW_INPUT = "PROVIDE_COMMAND_SHEET_REVIEW_INPUT"
    RESTORE_COMMAND_SHEET_APPROVAL = "RESTORE_COMMAND_SHEET_APPROVAL"
    RESTORE_COMMAND_SHEET_REVIEW_PREREQUISITES = "RESTORE_COMMAND_SHEET_REVIEW_PREREQUISITES"
    RESTORE_FINAL_MANUAL_TAG_AUTHORIZATION = "RESTORE_FINAL_MANUAL_TAG_AUTHORIZATION"
    RESTORE_TAG_CREATION_EXECUTION_PLAN_REVIEW = "RESTORE_TAG_CREATION_EXECUTION_PLAN_REVIEW"
    RESTORE_MANUAL_TAG_CREATION_APPROVAL = "RESTORE_MANUAL_TAG_CREATION_APPROVAL"
    RESTORE_HUMAN_TAG_GO_NO_GO = "RESTORE_HUMAN_TAG_GO_NO_GO"
    RESTORE_RELEASE_PACKAGE_REVIEW = "RESTORE_RELEASE_PACKAGE_REVIEW"
    RESTORE_FINAL_READINESS_REVIEW = "RESTORE_FINAL_READINESS_REVIEW"
    RESTORE_COMMAND_SHEET_REVIEW_TAG_NAME = "RESTORE_COMMAND_SHEET_REVIEW_TAG_NAME"
    RESTORE_COMMAND_SHEET_REVIEW_VERSION = "RESTORE_COMMAND_SHEET_REVIEW_VERSION"
    RESTORE_PRE_TAG_COMMAND_REVIEW = "RESTORE_PRE_TAG_COMMAND_REVIEW"
    RESTORE_EXPECTED_RESULT_REVIEW = "RESTORE_EXPECTED_RESULT_REVIEW"
    KEEP_TAG_COMMANDS_DOCUMENTATION_ONLY = "KEEP_TAG_COMMANDS_DOCUMENTATION_ONLY"
    RESTORE_STOP_RULE_REVIEW = "RESTORE_STOP_RULE_REVIEW"
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


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewScore:
    overall_score: int
    input_score: int
    prerequisite_score: int
    tag_name_score: int
    version_score: int
    pre_tag_command_score: int
    expected_result_score: int
    tag_command_score: int
    post_tag_command_score: int
    stop_rule_score: int
    documentation_score: int
    no_tag_score: int
    safety_score: int
    boundary_score: int


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewPrerequisite:
    name: str
    approved: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewCommand:
    command: str
    block: str
    present: bool = True
    documentation_only: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewExpectedResult:
    result: str
    present: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewStopRule:
    rule: str
    present: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewTagMetadata:
    tag_name: str
    version: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewContext:
    review_id: str
    tag_metadata: AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewTagMetadata
    prerequisites: tuple[AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewPrerequisite, ...]
    pre_tag_commands: tuple[AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewCommand, ...]
    expected_results: tuple[AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewExpectedResult, ...]
    tag_creation_commands: tuple[AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewCommand, ...]
    tag_push_commands: tuple[AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewCommand, ...]
    post_tag_commands: tuple[AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewCommand, ...]
    stop_rules: tuple[AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewStopRule, ...]


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewReport:
    markdown: str
    json: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewInput:
    review_id: str = "agicore-trading-v1-offline-manual-tag-creation-command-sheet-review"
    command_sheet_approved: bool = True
    prerequisites_complete: bool = True
    final_manual_tag_authorization_approved: bool = True
    execution_plan_review_approved: bool = True
    manual_tag_creation_approval_approved: bool = True
    human_tag_go_no_go_approved: bool = True
    release_package_review_approved: bool = True
    final_readiness_review_approved: bool = True
    tag_name: str = "agicore-trading-v1-offline"
    version: str = "v1.0.0-offline"
    pre_tag_commands_present: bool = True
    expected_results_present: bool = True
    tag_creation_command_documentation_only: bool = True
    tag_push_command_documentation_only: bool = True
    post_tag_commands_present: bool = True
    stop_rules_present: bool = True
    documented_commands_only: bool = True
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
class AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewResult:
    state: AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewState
    decision: AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewDecision
    score: AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewScore
    risks: tuple[AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk, ...]
    recommendations: tuple[AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRecommendation, ...]
    context: AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewContext | None = None
    report: AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewReport | None = None
    file_read: bool = False
    data_accessed: bool = False
    git_tag_created: bool = False
    git_tag_pushed: bool = False
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False
    next_phase: str = "AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION"
