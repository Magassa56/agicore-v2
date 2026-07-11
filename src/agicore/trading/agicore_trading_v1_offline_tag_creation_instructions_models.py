"""Models for AGIcore Trading v1 offline tag creation instructions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AGIcoreTradingV1OfflineTagCreationInstructionsState(StrEnum):
    NOT_READY = "NOT_READY"
    AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_INPUT_INVALID = (
        "AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_INPUT_INVALID"
    )
    AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_BLOCKED = (
        "AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_BLOCKED"
    )
    AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_COMPLETED_WITH_WARNINGS = (
        "AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_COMPLETED_WITH_WARNINGS"
    )
    AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_COMPLETED = (
        "AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_COMPLETED"
    )
    READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW = (
        "READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW"
    )


class AGIcoreTradingV1OfflineTagCreationInstructionsDecision(StrEnum):
    BLOCK_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS = (
        "BLOCK_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS"
    )
    REQUIRE_TAG_CREATION_INSTRUCTIONS_INPUT_FIXES = "REQUIRE_TAG_CREATION_INSTRUCTIONS_INPUT_FIXES"
    REQUIRE_TAG_CREATION_INSTRUCTIONS_FINAL_REVIEW_FIXES = "REQUIRE_TAG_CREATION_INSTRUCTIONS_FINAL_REVIEW_FIXES"
    REQUIRE_TAG_CREATION_INSTRUCTIONS_TAG_NAME_FIXES = "REQUIRE_TAG_CREATION_INSTRUCTIONS_TAG_NAME_FIXES"
    REQUIRE_TAG_CREATION_INSTRUCTIONS_VERSION_FIXES = "REQUIRE_TAG_CREATION_INSTRUCTIONS_VERSION_FIXES"
    REQUIRE_TAG_CREATION_INSTRUCTIONS_PRE_CHECK_FIXES = "REQUIRE_TAG_CREATION_INSTRUCTIONS_PRE_CHECK_FIXES"
    REQUIRE_TAG_CREATION_INSTRUCTIONS_COMMAND_FIXES = "REQUIRE_TAG_CREATION_INSTRUCTIONS_COMMAND_FIXES"
    REQUIRE_TAG_CREATION_INSTRUCTIONS_POST_CHECK_FIXES = "REQUIRE_TAG_CREATION_INSTRUCTIONS_POST_CHECK_FIXES"
    REQUIRE_TAG_CREATION_INSTRUCTIONS_SAFETY_FIXES = "REQUIRE_TAG_CREATION_INSTRUCTIONS_SAFETY_FIXES"
    REQUIRE_TAG_CREATION_INSTRUCTIONS_NO_OVERCLAIM_FIXES = "REQUIRE_TAG_CREATION_INSTRUCTIONS_NO_OVERCLAIM_FIXES"
    APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS = (
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS"
    )


class AGIcoreTradingV1OfflineTagCreationInstructionsRisk(StrEnum):
    TAG_CREATION_INSTRUCTIONS_INPUT_MISSING = "TAG_CREATION_INSTRUCTIONS_INPUT_MISSING"
    FINAL_TAG_REVIEW_NOT_APPROVED = "FINAL_TAG_REVIEW_NOT_APPROVED"
    TAG_CREATION_TAG_NAME_INVALID = "TAG_CREATION_TAG_NAME_INVALID"
    TAG_CREATION_VERSION_INVALID = "TAG_CREATION_VERSION_INVALID"
    TAG_CREATION_PRE_CHECKS_MISSING = "TAG_CREATION_PRE_CHECKS_MISSING"
    TAG_CREATION_COMMANDS_MISSING = "TAG_CREATION_COMMANDS_MISSING"
    TAG_CREATION_POST_CHECKS_MISSING = "TAG_CREATION_POST_CHECKS_MISSING"
    TAG_CREATION_WARNING_MISSING = "TAG_CREATION_WARNING_MISSING"
    TAG_CREATION_SAFETY_LANGUAGE_MISSING = "TAG_CREATION_SAFETY_LANGUAGE_MISSING"
    GIT_TAG_ALREADY_CREATED = "GIT_TAG_ALREADY_CREATED"
    GIT_TAG_COMMAND_EXECUTED = "GIT_TAG_COMMAND_EXECUTED"
    GIT_TAG_PUSH_EXECUTED = "GIT_TAG_PUSH_EXECUTED"
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


class AGIcoreTradingV1OfflineTagCreationInstructionsRecommendation(StrEnum):
    PROVIDE_TAG_CREATION_INSTRUCTIONS_INPUT = "PROVIDE_TAG_CREATION_INSTRUCTIONS_INPUT"
    RESTORE_FINAL_TAG_REVIEW_APPROVAL = "RESTORE_FINAL_TAG_REVIEW_APPROVAL"
    RESTORE_TAG_CREATION_TAG_NAME = "RESTORE_TAG_CREATION_TAG_NAME"
    RESTORE_TAG_CREATION_VERSION = "RESTORE_TAG_CREATION_VERSION"
    RESTORE_TAG_CREATION_PRE_CHECKS = "RESTORE_TAG_CREATION_PRE_CHECKS"
    RESTORE_TAG_CREATION_COMMANDS = "RESTORE_TAG_CREATION_COMMANDS"
    RESTORE_TAG_CREATION_POST_CHECKS = "RESTORE_TAG_CREATION_POST_CHECKS"
    RESTORE_TAG_CREATION_WARNING = "RESTORE_TAG_CREATION_WARNING"
    RESTORE_TAG_CREATION_SAFETY_LANGUAGE = "RESTORE_TAG_CREATION_SAFETY_LANGUAGE"
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
    PREPARE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW = (
        "PREPARE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW"
    )


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationInstructionsScore:
    overall_score: int
    input_score: int
    final_review_score: int
    tag_name_score: int
    version_score: int
    pre_check_score: int
    command_score: int
    post_check_score: int
    safety_score: int
    no_execution_score: int
    boundary_score: int


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationInstructionsCommand:
    command: str
    purpose: str
    documentation_only: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationInstructionsCheck:
    name: str
    command: str
    expected: str
    present: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationInstructionsSafetyRule:
    name: str
    present: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationInstructionsContext:
    instruction_id: str
    prerequisite_decision: str
    tag_name: str
    version: str
    pre_checks: tuple[AGIcoreTradingV1OfflineTagCreationInstructionsCheck, ...]
    manual_commands: tuple[AGIcoreTradingV1OfflineTagCreationInstructionsCommand, ...]
    post_checks: tuple[AGIcoreTradingV1OfflineTagCreationInstructionsCheck, ...]
    safety_rules: tuple[AGIcoreTradingV1OfflineTagCreationInstructionsSafetyRule, ...]


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationInstructionsReport:
    markdown: str
    json: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationInstructionsInput:
    instruction_id: str = "agicore-trading-v1-offline-tag-creation-instructions"
    final_tag_review_approved: bool = True
    tag_name: str = "agicore-trading-v1-offline"
    version: str = "v1.0.0-offline"
    pre_checks_present: bool = True
    manual_commands_documented: bool = True
    post_checks_present: bool = True
    warning_present: bool = True
    safety_language_present: bool = True
    git_tag_already_created: bool = False
    git_tag_command_executed: bool = False
    git_push_tag_executed: bool = False
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
class AGIcoreTradingV1OfflineTagCreationInstructionsResult:
    state: AGIcoreTradingV1OfflineTagCreationInstructionsState
    decision: AGIcoreTradingV1OfflineTagCreationInstructionsDecision
    score: AGIcoreTradingV1OfflineTagCreationInstructionsScore
    risks: tuple[AGIcoreTradingV1OfflineTagCreationInstructionsRisk, ...]
    recommendations: tuple[AGIcoreTradingV1OfflineTagCreationInstructionsRecommendation, ...]
    context: AGIcoreTradingV1OfflineTagCreationInstructionsContext | None = None
    report: AGIcoreTradingV1OfflineTagCreationInstructionsReport | None = None
    file_read: bool = False
    data_accessed: bool = False
    git_tag_created: bool = False
    git_tag_pushed: bool = False
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False
    next_phase: str = "AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW"
