"""Models for AGIcore Trading v1 offline final tag creation human confirmation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationState(StrEnum):
    NOT_READY = "NOT_READY"
    AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_INPUT_INVALID = (
        "AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_INPUT_INVALID"
    )
    AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_BLOCKED = (
        "AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_BLOCKED"
    )
    AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_COMPLETED_WITH_WARNINGS = (
        "AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_COMPLETED_WITH_WARNINGS"
    )
    AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_COMPLETED = (
        "AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_COMPLETED"
    )
    READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT = (
        "READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT"
    )


class AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationDecision(StrEnum):
    BLOCK_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION = (
        "BLOCK_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION"
    )
    REQUIRE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_INPUT_FIXES = (
        "REQUIRE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_INPUT_FIXES"
    )
    REQUIRE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_PREREQUISITE_FIXES = (
        "REQUIRE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_PREREQUISITE_FIXES"
    )
    REQUIRE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_TAG_NAME_FIXES = (
        "REQUIRE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_TAG_NAME_FIXES"
    )
    REQUIRE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_VERSION_FIXES = (
        "REQUIRE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_VERSION_FIXES"
    )
    REQUIRE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_CONDITION_FIXES = (
        "REQUIRE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_CONDITION_FIXES"
    )
    REQUIRE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_COMMAND_DOCUMENTATION_FIXES = (
        "REQUIRE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_COMMAND_DOCUMENTATION_FIXES"
    )
    REQUIRE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_STOP_RULE_FIXES = (
        "REQUIRE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_STOP_RULE_FIXES"
    )
    REQUIRE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_NO_OVERCLAIM_FIXES = (
        "REQUIRE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_NO_OVERCLAIM_FIXES"
    )
    APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION = (
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION"
    )


class AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk(StrEnum):
    FINAL_TAG_CREATION_HUMAN_CONFIRMATION_INPUT_MISSING = "FINAL_TAG_CREATION_HUMAN_CONFIRMATION_INPUT_MISSING"
    FINAL_TAG_CREATION_HUMAN_CONFIRMATION_PREREQUISITES_INCOMPLETE = (
        "FINAL_TAG_CREATION_HUMAN_CONFIRMATION_PREREQUISITES_INCOMPLETE"
    )
    MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_NOT_APPROVED = (
        "MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_NOT_APPROVED"
    )
    FINAL_MANUAL_TAG_AUTHORIZATION_NOT_APPROVED = "FINAL_MANUAL_TAG_AUTHORIZATION_NOT_APPROVED"
    TAG_CREATION_EXECUTION_PLAN_REVIEW_NOT_APPROVED = "TAG_CREATION_EXECUTION_PLAN_REVIEW_NOT_APPROVED"
    MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED = "MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED"
    HUMAN_TAG_GO_NO_GO_NOT_APPROVED = "HUMAN_TAG_GO_NO_GO_NOT_APPROVED"
    RELEASE_PACKAGE_REVIEW_NOT_APPROVED = "RELEASE_PACKAGE_REVIEW_NOT_APPROVED"
    FINAL_READINESS_REVIEW_NOT_APPROVED = "FINAL_READINESS_REVIEW_NOT_APPROVED"
    FINAL_TAG_CREATION_HUMAN_CONFIRMATION_TAG_NAME_INVALID = (
        "FINAL_TAG_CREATION_HUMAN_CONFIRMATION_TAG_NAME_INVALID"
    )
    FINAL_TAG_CREATION_HUMAN_CONFIRMATION_VERSION_INVALID = (
        "FINAL_TAG_CREATION_HUMAN_CONFIRMATION_VERSION_INVALID"
    )
    FINAL_TAG_CREATION_HUMAN_CONFIRMATION_CONDITIONS_MISSING = (
        "FINAL_TAG_CREATION_HUMAN_CONFIRMATION_CONDITIONS_MISSING"
    )
    FINAL_TAG_CREATION_HUMAN_CONFIRMATION_COMMANDS_NOT_DOCUMENTATION_ONLY = (
        "FINAL_TAG_CREATION_HUMAN_CONFIRMATION_COMMANDS_NOT_DOCUMENTATION_ONLY"
    )
    FINAL_TAG_CREATION_HUMAN_CONFIRMATION_STOP_RULES_MISSING = (
        "FINAL_TAG_CREATION_HUMAN_CONFIRMATION_STOP_RULES_MISSING"
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


class AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRecommendation(StrEnum):
    PREPARE_TAG_CREATION_FINAL_PREFLIGHT = "PREPARE_TAG_CREATION_FINAL_PREFLIGHT"
    PROVIDE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_INPUT = (
        "PROVIDE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_INPUT"
    )
    RESTORE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_PREREQUISITES = (
        "RESTORE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_PREREQUISITES"
    )
    RESTORE_TAG_NAME = "RESTORE_TAG_NAME"
    RESTORE_VERSION = "RESTORE_VERSION"
    RESTORE_CONDITIONS = "RESTORE_CONDITIONS"
    KEEP_COMMANDS_DOCUMENTATION_ONLY = "KEEP_COMMANDS_DOCUMENTATION_ONLY"
    RESTORE_STOP_RULES = "RESTORE_STOP_RULES"
    DO_NOT_CREATE_GIT_TAG_IN_THIS_PHASE = "DO_NOT_CREATE_GIT_TAG_IN_THIS_PHASE"
    DO_NOT_PUSH_GIT_TAG_IN_THIS_PHASE = "DO_NOT_PUSH_GIT_TAG_IN_THIS_PHASE"
    REMOVE_OVERCLAIM = "REMOVE_OVERCLAIM"
    REMOVE_BOUNDARY_VIOLATION = "REMOVE_BOUNDARY_VIOLATION"


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationScore:
    overall_score: int
    input_score: int
    prerequisite_score: int
    tag_name_score: int
    version_score: int
    condition_score: int
    command_score: int
    stop_rule_score: int
    no_tag_score: int
    safety_score: int
    boundary_score: int


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationPrerequisite:
    name: str
    approved: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationCondition:
    condition: str
    present: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationCommand:
    command: str
    documentation_only: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationStopRule:
    rule: str
    present: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationTagMetadata:
    tag_name: str
    version: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationContext:
    confirmation_id: str
    tag_metadata: AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationTagMetadata
    prerequisites: tuple[AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationPrerequisite, ...]
    human_confirmation: str
    conditions: tuple[AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationCondition, ...]
    commands: tuple[AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationCommand, ...]
    stop_rules: tuple[AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationStopRule, ...]


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationReport:
    markdown: str
    json: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationInput:
    confirmation_id: str = "agicore-trading-v1-offline-final-tag-creation-human-confirmation"
    prerequisites_complete: bool = True
    command_sheet_review_approved: bool = True
    command_sheet_approved: bool = True
    final_manual_tag_authorization_approved: bool = True
    execution_plan_review_approved: bool = True
    manual_tag_creation_approval_approved: bool = True
    human_tag_go_no_go_approved: bool = True
    release_package_review_approved: bool = True
    final_readiness_review_approved: bool = True
    tag_name: str = "agicore-trading-v1-offline"
    version: str = "v1.0.0-offline"
    conditions_present: bool = True
    commands_documentation_only: bool = True
    stop_rules_present: bool = True
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
class AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationResult:
    state: AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationState
    decision: AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationDecision
    score: AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationScore
    risks: tuple[AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk, ...]
    recommendations: tuple[AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRecommendation, ...]
    context: AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationContext | None = None
    report: AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationReport | None = None
    file_read: bool = False
    data_accessed: bool = False
    git_tag_created: bool = False
    git_tag_pushed: bool = False
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False
    next_phase: str = "AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT"
