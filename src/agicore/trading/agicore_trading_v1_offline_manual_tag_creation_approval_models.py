"""Models for AGIcore Trading v1 offline manual tag creation approval."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AGIcoreTradingV1OfflineManualTagCreationApprovalState(StrEnum):
    NOT_READY = "NOT_READY"
    AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_APPROVAL_INPUT_INVALID = (
        "AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_APPROVAL_INPUT_INVALID"
    )
    AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_APPROVAL_BLOCKED = (
        "AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_APPROVAL_BLOCKED"
    )
    AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_APPROVAL_COMPLETED_WITH_WARNINGS = (
        "AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_APPROVAL_COMPLETED_WITH_WARNINGS"
    )
    AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_APPROVAL_COMPLETED = (
        "AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_APPROVAL_COMPLETED"
    )
    READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN = (
        "READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN"
    )


class AGIcoreTradingV1OfflineManualTagCreationApprovalDecision(StrEnum):
    BLOCK_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_APPROVAL = (
        "BLOCK_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_APPROVAL"
    )
    REQUIRE_MANUAL_TAG_CREATION_APPROVAL_INPUT_FIXES = "REQUIRE_MANUAL_TAG_CREATION_APPROVAL_INPUT_FIXES"
    REQUIRE_MANUAL_TAG_CREATION_APPROVAL_PREREQUISITE_FIXES = (
        "REQUIRE_MANUAL_TAG_CREATION_APPROVAL_PREREQUISITE_FIXES"
    )
    REQUIRE_MANUAL_TAG_CREATION_APPROVAL_TAG_NAME_FIXES = "REQUIRE_MANUAL_TAG_CREATION_APPROVAL_TAG_NAME_FIXES"
    REQUIRE_MANUAL_TAG_CREATION_APPROVAL_VERSION_FIXES = "REQUIRE_MANUAL_TAG_CREATION_APPROVAL_VERSION_FIXES"
    REQUIRE_MANUAL_TAG_CREATION_APPROVAL_CONDITION_FIXES = "REQUIRE_MANUAL_TAG_CREATION_APPROVAL_CONDITION_FIXES"
    REQUIRE_MANUAL_TAG_CREATION_APPROVAL_COMMAND_DOCUMENTATION_FIXES = (
        "REQUIRE_MANUAL_TAG_CREATION_APPROVAL_COMMAND_DOCUMENTATION_FIXES"
    )
    REQUIRE_MANUAL_TAG_CREATION_APPROVAL_STOP_RULE_FIXES = (
        "REQUIRE_MANUAL_TAG_CREATION_APPROVAL_STOP_RULE_FIXES"
    )
    REQUIRE_MANUAL_TAG_CREATION_APPROVAL_NO_OVERCLAIM_FIXES = (
        "REQUIRE_MANUAL_TAG_CREATION_APPROVAL_NO_OVERCLAIM_FIXES"
    )
    APPROVE_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_APPROVAL = (
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_APPROVAL"
    )


class AGIcoreTradingV1OfflineManualTagCreationApprovalRisk(StrEnum):
    MANUAL_TAG_CREATION_APPROVAL_INPUT_MISSING = "MANUAL_TAG_CREATION_APPROVAL_INPUT_MISSING"
    MANUAL_TAG_CREATION_APPROVAL_PREREQUISITES_INCOMPLETE = (
        "MANUAL_TAG_CREATION_APPROVAL_PREREQUISITES_INCOMPLETE"
    )
    HUMAN_TAG_GO_NO_GO_NOT_APPROVED = "HUMAN_TAG_GO_NO_GO_NOT_APPROVED"
    MANUAL_TAG_CREATION_FINAL_CHECKLIST_NOT_APPROVED = "MANUAL_TAG_CREATION_FINAL_CHECKLIST_NOT_APPROVED"
    TAG_CREATION_INSTRUCTIONS_REVIEW_NOT_APPROVED = "TAG_CREATION_INSTRUCTIONS_REVIEW_NOT_APPROVED"
    FINAL_TAG_REVIEW_NOT_APPROVED = "FINAL_TAG_REVIEW_NOT_APPROVED"
    RELEASE_PACKAGE_REVIEW_NOT_APPROVED = "RELEASE_PACKAGE_REVIEW_NOT_APPROVED"
    FINAL_READINESS_REVIEW_NOT_APPROVED = "FINAL_READINESS_REVIEW_NOT_APPROVED"
    MANUAL_TAG_CREATION_APPROVAL_TAG_NAME_INVALID = "MANUAL_TAG_CREATION_APPROVAL_TAG_NAME_INVALID"
    MANUAL_TAG_CREATION_APPROVAL_VERSION_INVALID = "MANUAL_TAG_CREATION_APPROVAL_VERSION_INVALID"
    MANUAL_TAG_CREATION_APPROVAL_CONDITIONS_MISSING = "MANUAL_TAG_CREATION_APPROVAL_CONDITIONS_MISSING"
    MANUAL_TAG_CREATION_APPROVAL_COMMANDS_NOT_DOCUMENTATION_ONLY = (
        "MANUAL_TAG_CREATION_APPROVAL_COMMANDS_NOT_DOCUMENTATION_ONLY"
    )
    MANUAL_TAG_CREATION_APPROVAL_STOP_RULES_MISSING = "MANUAL_TAG_CREATION_APPROVAL_STOP_RULES_MISSING"
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


class AGIcoreTradingV1OfflineManualTagCreationApprovalRecommendation(StrEnum):
    PROVIDE_MANUAL_TAG_CREATION_APPROVAL_INPUT = "PROVIDE_MANUAL_TAG_CREATION_APPROVAL_INPUT"
    RESTORE_MANUAL_TAG_CREATION_APPROVAL_PREREQUISITES = (
        "RESTORE_MANUAL_TAG_CREATION_APPROVAL_PREREQUISITES"
    )
    RESTORE_HUMAN_TAG_GO_NO_GO_APPROVAL = "RESTORE_HUMAN_TAG_GO_NO_GO_APPROVAL"
    RESTORE_MANUAL_TAG_CREATION_FINAL_CHECKLIST_APPROVAL = (
        "RESTORE_MANUAL_TAG_CREATION_FINAL_CHECKLIST_APPROVAL"
    )
    RESTORE_TAG_CREATION_INSTRUCTIONS_REVIEW_APPROVAL = (
        "RESTORE_TAG_CREATION_INSTRUCTIONS_REVIEW_APPROVAL"
    )
    RESTORE_FINAL_TAG_REVIEW_APPROVAL = "RESTORE_FINAL_TAG_REVIEW_APPROVAL"
    RESTORE_RELEASE_PACKAGE_REVIEW_APPROVAL = "RESTORE_RELEASE_PACKAGE_REVIEW_APPROVAL"
    RESTORE_FINAL_READINESS_REVIEW_APPROVAL = "RESTORE_FINAL_READINESS_REVIEW_APPROVAL"
    RESTORE_MANUAL_TAG_CREATION_APPROVAL_TAG_NAME = "RESTORE_MANUAL_TAG_CREATION_APPROVAL_TAG_NAME"
    RESTORE_MANUAL_TAG_CREATION_APPROVAL_VERSION = "RESTORE_MANUAL_TAG_CREATION_APPROVAL_VERSION"
    RESTORE_MANUAL_TAG_CREATION_APPROVAL_CONDITIONS = "RESTORE_MANUAL_TAG_CREATION_APPROVAL_CONDITIONS"
    KEEP_MANUAL_TAG_CREATION_COMMANDS_DOCUMENTATION_ONLY = (
        "KEEP_MANUAL_TAG_CREATION_COMMANDS_DOCUMENTATION_ONLY"
    )
    RESTORE_MANUAL_TAG_CREATION_APPROVAL_STOP_RULES = "RESTORE_MANUAL_TAG_CREATION_APPROVAL_STOP_RULES"
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
    PREPARE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN = (
        "PREPARE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN"
    )


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineManualTagCreationApprovalScore:
    overall_score: int
    input_score: int
    prerequisite_score: int
    tag_name_score: int
    version_score: int
    decision_score: int
    condition_score: int
    command_score: int
    stop_rule_score: int
    no_tag_score: int
    safety_score: int
    boundary_score: int


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineManualTagCreationApprovalPrerequisite:
    name: str
    approved: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineManualTagCreationApprovalCriterion:
    name: str
    passed: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineManualTagCreationApprovalFinding:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineManualTagCreationApprovalTagMetadata:
    tag_name: str
    version: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineManualTagCreationApprovalCondition:
    name: str
    present: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineManualTagCreationApprovalCommand:
    command: str
    documentation_only: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineManualTagCreationApprovalStopRule:
    rule: str
    present: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineManualTagCreationApprovalContext:
    approval_id: str
    tag_metadata: AGIcoreTradingV1OfflineManualTagCreationApprovalTagMetadata
    approval_decision: str
    prerequisites: tuple[AGIcoreTradingV1OfflineManualTagCreationApprovalPrerequisite, ...]
    conditions: tuple[AGIcoreTradingV1OfflineManualTagCreationApprovalCondition, ...]
    commands: tuple[AGIcoreTradingV1OfflineManualTagCreationApprovalCommand, ...]
    stop_rules: tuple[AGIcoreTradingV1OfflineManualTagCreationApprovalStopRule, ...]
    criteria: tuple[AGIcoreTradingV1OfflineManualTagCreationApprovalCriterion, ...]


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineManualTagCreationApprovalReport:
    markdown: str
    json: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineManualTagCreationApprovalInput:
    approval_id: str = "agicore-trading-v1-offline-manual-tag-creation-approval"
    prerequisites_complete: bool = True
    human_tag_go_no_go_approved: bool = True
    manual_tag_creation_final_checklist_approved: bool = True
    tag_creation_instructions_review_approved: bool = True
    final_tag_review_approved: bool = True
    release_package_review_approved: bool = True
    final_readiness_review_approved: bool = True
    tag_name: str = "agicore-trading-v1-offline"
    version: str = "v1.0.0-offline"
    approval_decision: str = "APPROVED_FOR_MANUAL_TAG_CREATION_LATER"
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
class AGIcoreTradingV1OfflineManualTagCreationApprovalResult:
    state: AGIcoreTradingV1OfflineManualTagCreationApprovalState
    decision: AGIcoreTradingV1OfflineManualTagCreationApprovalDecision
    score: AGIcoreTradingV1OfflineManualTagCreationApprovalScore
    risks: tuple[AGIcoreTradingV1OfflineManualTagCreationApprovalRisk, ...]
    recommendations: tuple[AGIcoreTradingV1OfflineManualTagCreationApprovalRecommendation, ...]
    context: AGIcoreTradingV1OfflineManualTagCreationApprovalContext | None = None
    findings: tuple[AGIcoreTradingV1OfflineManualTagCreationApprovalFinding, ...] = ()
    report: AGIcoreTradingV1OfflineManualTagCreationApprovalReport | None = None
    file_read: bool = False
    data_accessed: bool = False
    git_tag_created: bool = False
    git_tag_pushed: bool = False
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False
    next_phase: str = "AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN"
