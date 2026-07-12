"""Models for AGIcore Trading v1 offline final manual tag authorization."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AGIcoreTradingV1OfflineFinalManualTagAuthorizationState(StrEnum):
    NOT_READY = "NOT_READY"
    AGICORE_TRADING_V1_OFFLINE_FINAL_MANUAL_TAG_AUTHORIZATION_INPUT_INVALID = (
        "AGICORE_TRADING_V1_OFFLINE_FINAL_MANUAL_TAG_AUTHORIZATION_INPUT_INVALID"
    )
    AGICORE_TRADING_V1_OFFLINE_FINAL_MANUAL_TAG_AUTHORIZATION_BLOCKED = (
        "AGICORE_TRADING_V1_OFFLINE_FINAL_MANUAL_TAG_AUTHORIZATION_BLOCKED"
    )
    AGICORE_TRADING_V1_OFFLINE_FINAL_MANUAL_TAG_AUTHORIZATION_COMPLETED_WITH_WARNINGS = (
        "AGICORE_TRADING_V1_OFFLINE_FINAL_MANUAL_TAG_AUTHORIZATION_COMPLETED_WITH_WARNINGS"
    )
    AGICORE_TRADING_V1_OFFLINE_FINAL_MANUAL_TAG_AUTHORIZATION_COMPLETED = (
        "AGICORE_TRADING_V1_OFFLINE_FINAL_MANUAL_TAG_AUTHORIZATION_COMPLETED"
    )
    READY_FOR_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET = (
        "READY_FOR_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET"
    )


class AGIcoreTradingV1OfflineFinalManualTagAuthorizationDecision(StrEnum):
    BLOCK_AGICORE_TRADING_V1_OFFLINE_FINAL_MANUAL_TAG_AUTHORIZATION = (
        "BLOCK_AGICORE_TRADING_V1_OFFLINE_FINAL_MANUAL_TAG_AUTHORIZATION"
    )
    REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_INPUT_FIXES = "REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_INPUT_FIXES"
    REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_PREREQUISITE_FIXES = (
        "REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_PREREQUISITE_FIXES"
    )
    REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_TAG_NAME_FIXES = (
        "REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_TAG_NAME_FIXES"
    )
    REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_VERSION_FIXES = (
        "REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_VERSION_FIXES"
    )
    REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_CONDITION_FIXES = (
        "REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_CONDITION_FIXES"
    )
    REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_COMMAND_DOCUMENTATION_FIXES = (
        "REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_COMMAND_DOCUMENTATION_FIXES"
    )
    REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_STOP_RULE_FIXES = (
        "REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_STOP_RULE_FIXES"
    )
    REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_NO_OVERCLAIM_FIXES = (
        "REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_NO_OVERCLAIM_FIXES"
    )
    APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_MANUAL_TAG_AUTHORIZATION = (
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_MANUAL_TAG_AUTHORIZATION"
    )


class AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk(StrEnum):
    FINAL_MANUAL_TAG_AUTHORIZATION_INPUT_MISSING = "FINAL_MANUAL_TAG_AUTHORIZATION_INPUT_MISSING"
    FINAL_MANUAL_TAG_AUTHORIZATION_PREREQUISITES_INCOMPLETE = (
        "FINAL_MANUAL_TAG_AUTHORIZATION_PREREQUISITES_INCOMPLETE"
    )
    TAG_CREATION_EXECUTION_PLAN_REVIEW_NOT_APPROVED = "TAG_CREATION_EXECUTION_PLAN_REVIEW_NOT_APPROVED"
    TAG_CREATION_EXECUTION_PLAN_NOT_APPROVED = "TAG_CREATION_EXECUTION_PLAN_NOT_APPROVED"
    MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED = "MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED"
    MANUAL_TAG_CREATION_FINAL_CHECKLIST_NOT_APPROVED = "MANUAL_TAG_CREATION_FINAL_CHECKLIST_NOT_APPROVED"
    HUMAN_TAG_GO_NO_GO_NOT_APPROVED = "HUMAN_TAG_GO_NO_GO_NOT_APPROVED"
    TAG_CREATION_INSTRUCTIONS_REVIEW_NOT_APPROVED = "TAG_CREATION_INSTRUCTIONS_REVIEW_NOT_APPROVED"
    FINAL_TAG_REVIEW_NOT_APPROVED = "FINAL_TAG_REVIEW_NOT_APPROVED"
    RELEASE_PACKAGE_REVIEW_NOT_APPROVED = "RELEASE_PACKAGE_REVIEW_NOT_APPROVED"
    FINAL_READINESS_REVIEW_NOT_APPROVED = "FINAL_READINESS_REVIEW_NOT_APPROVED"
    FINAL_MANUAL_TAG_AUTHORIZATION_TAG_NAME_INVALID = "FINAL_MANUAL_TAG_AUTHORIZATION_TAG_NAME_INVALID"
    FINAL_MANUAL_TAG_AUTHORIZATION_VERSION_INVALID = "FINAL_MANUAL_TAG_AUTHORIZATION_VERSION_INVALID"
    FINAL_MANUAL_TAG_AUTHORIZATION_CONDITIONS_MISSING = "FINAL_MANUAL_TAG_AUTHORIZATION_CONDITIONS_MISSING"
    FINAL_MANUAL_TAG_AUTHORIZATION_COMMANDS_NOT_DOCUMENTATION_ONLY = (
        "FINAL_MANUAL_TAG_AUTHORIZATION_COMMANDS_NOT_DOCUMENTATION_ONLY"
    )
    FINAL_MANUAL_TAG_AUTHORIZATION_STOP_RULES_MISSING = (
        "FINAL_MANUAL_TAG_AUTHORIZATION_STOP_RULES_MISSING"
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


class AGIcoreTradingV1OfflineFinalManualTagAuthorizationRecommendation(StrEnum):
    PREPARE_MANUAL_TAG_CREATION_COMMAND_SHEET = "PREPARE_MANUAL_TAG_CREATION_COMMAND_SHEET"
    PROVIDE_FINAL_MANUAL_TAG_AUTHORIZATION_INPUT = "PROVIDE_FINAL_MANUAL_TAG_AUTHORIZATION_INPUT"
    RESTORE_FINAL_MANUAL_TAG_AUTHORIZATION_PREREQUISITES = (
        "RESTORE_FINAL_MANUAL_TAG_AUTHORIZATION_PREREQUISITES"
    )
    RESTORE_TAG_CREATION_EXECUTION_PLAN_REVIEW = "RESTORE_TAG_CREATION_EXECUTION_PLAN_REVIEW"
    RESTORE_TAG_CREATION_EXECUTION_PLAN = "RESTORE_TAG_CREATION_EXECUTION_PLAN"
    RESTORE_MANUAL_TAG_CREATION_APPROVAL = "RESTORE_MANUAL_TAG_CREATION_APPROVAL"
    RESTORE_MANUAL_TAG_CREATION_FINAL_CHECKLIST = "RESTORE_MANUAL_TAG_CREATION_FINAL_CHECKLIST"
    RESTORE_HUMAN_TAG_GO_NO_GO = "RESTORE_HUMAN_TAG_GO_NO_GO"
    RESTORE_TAG_CREATION_INSTRUCTIONS_REVIEW = "RESTORE_TAG_CREATION_INSTRUCTIONS_REVIEW"
    RESTORE_FINAL_TAG_REVIEW = "RESTORE_FINAL_TAG_REVIEW"
    RESTORE_RELEASE_PACKAGE_REVIEW = "RESTORE_RELEASE_PACKAGE_REVIEW"
    RESTORE_FINAL_READINESS_REVIEW = "RESTORE_FINAL_READINESS_REVIEW"
    RESTORE_FINAL_MANUAL_TAG_AUTHORIZATION_TAG_NAME = "RESTORE_FINAL_MANUAL_TAG_AUTHORIZATION_TAG_NAME"
    RESTORE_FINAL_MANUAL_TAG_AUTHORIZATION_VERSION = "RESTORE_FINAL_MANUAL_TAG_AUTHORIZATION_VERSION"
    RESTORE_FINAL_MANUAL_TAG_AUTHORIZATION_CONDITIONS = "RESTORE_FINAL_MANUAL_TAG_AUTHORIZATION_CONDITIONS"
    KEEP_FINAL_MANUAL_TAG_AUTHORIZATION_COMMANDS_DOCUMENTATION_ONLY = (
        "KEEP_FINAL_MANUAL_TAG_AUTHORIZATION_COMMANDS_DOCUMENTATION_ONLY"
    )
    RESTORE_FINAL_MANUAL_TAG_AUTHORIZATION_STOP_RULES = "RESTORE_FINAL_MANUAL_TAG_AUTHORIZATION_STOP_RULES"
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
class AGIcoreTradingV1OfflineFinalManualTagAuthorizationScore:
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
class AGIcoreTradingV1OfflineFinalManualTagAuthorizationPrerequisite:
    name: str
    approved: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalManualTagAuthorizationCondition:
    name: str
    present: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalManualTagAuthorizationCommand:
    command: str
    documentation_only: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalManualTagAuthorizationStopRule:
    rule: str
    present: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalManualTagAuthorizationTagMetadata:
    tag_name: str
    version: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalManualTagAuthorizationContext:
    authorization_id: str
    tag_metadata: AGIcoreTradingV1OfflineFinalManualTagAuthorizationTagMetadata
    prerequisites: tuple[AGIcoreTradingV1OfflineFinalManualTagAuthorizationPrerequisite, ...]
    conditions: tuple[AGIcoreTradingV1OfflineFinalManualTagAuthorizationCondition, ...]
    commands: tuple[AGIcoreTradingV1OfflineFinalManualTagAuthorizationCommand, ...]
    stop_rules: tuple[AGIcoreTradingV1OfflineFinalManualTagAuthorizationStopRule, ...]


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalManualTagAuthorizationReport:
    markdown: str
    json: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput:
    authorization_id: str = "agicore-trading-v1-offline-final-manual-tag-authorization"
    prerequisites_complete: bool = True
    execution_plan_review_approved: bool = True
    execution_plan_approved: bool = True
    manual_tag_creation_approval_approved: bool = True
    manual_tag_creation_final_checklist_approved: bool = True
    human_tag_go_no_go_approved: bool = True
    tag_creation_instructions_review_approved: bool = True
    final_tag_review_approved: bool = True
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
class AGIcoreTradingV1OfflineFinalManualTagAuthorizationResult:
    state: AGIcoreTradingV1OfflineFinalManualTagAuthorizationState
    decision: AGIcoreTradingV1OfflineFinalManualTagAuthorizationDecision
    score: AGIcoreTradingV1OfflineFinalManualTagAuthorizationScore
    risks: tuple[AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk, ...]
    recommendations: tuple[AGIcoreTradingV1OfflineFinalManualTagAuthorizationRecommendation, ...]
    context: AGIcoreTradingV1OfflineFinalManualTagAuthorizationContext | None = None
    report: AGIcoreTradingV1OfflineFinalManualTagAuthorizationReport | None = None
    file_read: bool = False
    data_accessed: bool = False
    git_tag_created: bool = False
    git_tag_pushed: bool = False
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False
    next_phase: str = "AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET"
