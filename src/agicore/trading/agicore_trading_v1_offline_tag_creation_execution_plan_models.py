"""Models for AGIcore Trading v1 offline tag creation execution plan."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AGIcoreTradingV1OfflineTagCreationExecutionPlanState(StrEnum):
    NOT_READY = "NOT_READY"
    AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_INPUT_INVALID = (
        "AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_INPUT_INVALID"
    )
    AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_BLOCKED = (
        "AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_BLOCKED"
    )
    AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_COMPLETED_WITH_WARNINGS = (
        "AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_COMPLETED_WITH_WARNINGS"
    )
    AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_COMPLETED = (
        "AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_COMPLETED"
    )
    READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_REVIEW = (
        "READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_REVIEW"
    )


class AGIcoreTradingV1OfflineTagCreationExecutionPlanDecision(StrEnum):
    BLOCK_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN = (
        "BLOCK_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN"
    )
    REQUIRE_TAG_CREATION_EXECUTION_PLAN_INPUT_FIXES = "REQUIRE_TAG_CREATION_EXECUTION_PLAN_INPUT_FIXES"
    REQUIRE_TAG_CREATION_EXECUTION_PLAN_PREREQUISITE_FIXES = (
        "REQUIRE_TAG_CREATION_EXECUTION_PLAN_PREREQUISITE_FIXES"
    )
    REQUIRE_TAG_CREATION_EXECUTION_PLAN_TAG_NAME_FIXES = "REQUIRE_TAG_CREATION_EXECUTION_PLAN_TAG_NAME_FIXES"
    REQUIRE_TAG_CREATION_EXECUTION_PLAN_VERSION_FIXES = "REQUIRE_TAG_CREATION_EXECUTION_PLAN_VERSION_FIXES"
    REQUIRE_TAG_CREATION_EXECUTION_PLAN_STEP_FIXES = "REQUIRE_TAG_CREATION_EXECUTION_PLAN_STEP_FIXES"
    REQUIRE_TAG_CREATION_EXECUTION_PLAN_COMMAND_DOCUMENTATION_FIXES = (
        "REQUIRE_TAG_CREATION_EXECUTION_PLAN_COMMAND_DOCUMENTATION_FIXES"
    )
    REQUIRE_TAG_CREATION_EXECUTION_PLAN_STOP_RULE_FIXES = "REQUIRE_TAG_CREATION_EXECUTION_PLAN_STOP_RULE_FIXES"
    REQUIRE_TAG_CREATION_EXECUTION_PLAN_NO_OVERCLAIM_FIXES = "REQUIRE_TAG_CREATION_EXECUTION_PLAN_NO_OVERCLAIM_FIXES"
    APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN = (
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN"
    )


class AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk(StrEnum):
    TAG_CREATION_EXECUTION_PLAN_INPUT_MISSING = "TAG_CREATION_EXECUTION_PLAN_INPUT_MISSING"
    TAG_CREATION_EXECUTION_PLAN_PREREQUISITES_INCOMPLETE = "TAG_CREATION_EXECUTION_PLAN_PREREQUISITES_INCOMPLETE"
    MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED = "MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED"
    MANUAL_TAG_CREATION_FINAL_CHECKLIST_NOT_APPROVED = "MANUAL_TAG_CREATION_FINAL_CHECKLIST_NOT_APPROVED"
    HUMAN_TAG_GO_NO_GO_NOT_APPROVED = "HUMAN_TAG_GO_NO_GO_NOT_APPROVED"
    TAG_CREATION_INSTRUCTIONS_REVIEW_NOT_APPROVED = "TAG_CREATION_INSTRUCTIONS_REVIEW_NOT_APPROVED"
    FINAL_TAG_REVIEW_NOT_APPROVED = "FINAL_TAG_REVIEW_NOT_APPROVED"
    RELEASE_PACKAGE_REVIEW_NOT_APPROVED = "RELEASE_PACKAGE_REVIEW_NOT_APPROVED"
    FINAL_READINESS_REVIEW_NOT_APPROVED = "FINAL_READINESS_REVIEW_NOT_APPROVED"
    TAG_CREATION_EXECUTION_PLAN_TAG_NAME_INVALID = "TAG_CREATION_EXECUTION_PLAN_TAG_NAME_INVALID"
    TAG_CREATION_EXECUTION_PLAN_VERSION_INVALID = "TAG_CREATION_EXECUTION_PLAN_VERSION_INVALID"
    TAG_CREATION_EXECUTION_PLAN_STEPS_MISSING = "TAG_CREATION_EXECUTION_PLAN_STEPS_MISSING"
    TAG_CREATION_EXECUTION_PLAN_COMMANDS_NOT_DOCUMENTATION_ONLY = (
        "TAG_CREATION_EXECUTION_PLAN_COMMANDS_NOT_DOCUMENTATION_ONLY"
    )
    TAG_CREATION_EXECUTION_PLAN_STOP_RULES_MISSING = "TAG_CREATION_EXECUTION_PLAN_STOP_RULES_MISSING"
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


class AGIcoreTradingV1OfflineTagCreationExecutionPlanRecommendation(StrEnum):
    PROVIDE_TAG_CREATION_EXECUTION_PLAN_INPUT = "PROVIDE_TAG_CREATION_EXECUTION_PLAN_INPUT"
    RESTORE_TAG_CREATION_EXECUTION_PLAN_PREREQUISITES = "RESTORE_TAG_CREATION_EXECUTION_PLAN_PREREQUISITES"
    RESTORE_MANUAL_TAG_CREATION_APPROVAL = "RESTORE_MANUAL_TAG_CREATION_APPROVAL"
    RESTORE_MANUAL_TAG_CREATION_FINAL_CHECKLIST = "RESTORE_MANUAL_TAG_CREATION_FINAL_CHECKLIST"
    RESTORE_HUMAN_TAG_GO_NO_GO = "RESTORE_HUMAN_TAG_GO_NO_GO"
    RESTORE_TAG_CREATION_INSTRUCTIONS_REVIEW = "RESTORE_TAG_CREATION_INSTRUCTIONS_REVIEW"
    RESTORE_FINAL_TAG_REVIEW = "RESTORE_FINAL_TAG_REVIEW"
    RESTORE_RELEASE_PACKAGE_REVIEW = "RESTORE_RELEASE_PACKAGE_REVIEW"
    RESTORE_FINAL_READINESS_REVIEW = "RESTORE_FINAL_READINESS_REVIEW"
    RESTORE_TAG_CREATION_EXECUTION_PLAN_TAG_NAME = "RESTORE_TAG_CREATION_EXECUTION_PLAN_TAG_NAME"
    RESTORE_TAG_CREATION_EXECUTION_PLAN_VERSION = "RESTORE_TAG_CREATION_EXECUTION_PLAN_VERSION"
    RESTORE_TAG_CREATION_EXECUTION_PLAN_STEPS = "RESTORE_TAG_CREATION_EXECUTION_PLAN_STEPS"
    KEEP_TAG_CREATION_COMMANDS_DOCUMENTATION_ONLY = "KEEP_TAG_CREATION_COMMANDS_DOCUMENTATION_ONLY"
    RESTORE_TAG_CREATION_EXECUTION_PLAN_STOP_RULES = "RESTORE_TAG_CREATION_EXECUTION_PLAN_STOP_RULES"
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
    PREPARE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_REVIEW = (
        "PREPARE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_REVIEW"
    )


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationExecutionPlanScore:
    overall_score: int
    input_score: int
    prerequisite_score: int
    tag_name_score: int
    version_score: int
    step_score: int
    command_score: int
    pre_check_score: int
    remote_check_score: int
    stop_rule_score: int
    no_tag_score: int
    safety_score: int
    boundary_score: int


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationExecutionPlanPrerequisite:
    name: str
    approved: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationExecutionPlanStep:
    index: int
    description: str
    present: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationExecutionPlanCommand:
    command: str
    documentation_only: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationExecutionPlanStopRule:
    rule: str
    present: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationExecutionPlanTagMetadata:
    tag_name: str
    version: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationExecutionPlanContext:
    plan_id: str
    tag_metadata: AGIcoreTradingV1OfflineTagCreationExecutionPlanTagMetadata
    prerequisites: tuple[AGIcoreTradingV1OfflineTagCreationExecutionPlanPrerequisite, ...]
    steps: tuple[AGIcoreTradingV1OfflineTagCreationExecutionPlanStep, ...]
    commands: tuple[AGIcoreTradingV1OfflineTagCreationExecutionPlanCommand, ...]
    stop_rules: tuple[AGIcoreTradingV1OfflineTagCreationExecutionPlanStopRule, ...]


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationExecutionPlanReport:
    markdown: str
    json: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationExecutionPlanInput:
    plan_id: str = "agicore-trading-v1-offline-tag-creation-execution-plan"
    prerequisites_complete: bool = True
    manual_tag_creation_approval_approved: bool = True
    manual_tag_creation_final_checklist_approved: bool = True
    human_tag_go_no_go_approved: bool = True
    tag_creation_instructions_review_approved: bool = True
    final_tag_review_approved: bool = True
    release_package_review_approved: bool = True
    final_readiness_review_approved: bool = True
    tag_name: str = "agicore-trading-v1-offline"
    version: str = "v1.0.0-offline"
    steps_present: bool = True
    commands_documentation_only: bool = True
    pre_checks_present: bool = True
    remote_checks_present: bool = True
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
class AGIcoreTradingV1OfflineTagCreationExecutionPlanResult:
    state: AGIcoreTradingV1OfflineTagCreationExecutionPlanState
    decision: AGIcoreTradingV1OfflineTagCreationExecutionPlanDecision
    score: AGIcoreTradingV1OfflineTagCreationExecutionPlanScore
    risks: tuple[AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk, ...]
    recommendations: tuple[AGIcoreTradingV1OfflineTagCreationExecutionPlanRecommendation, ...]
    context: AGIcoreTradingV1OfflineTagCreationExecutionPlanContext | None = None
    report: AGIcoreTradingV1OfflineTagCreationExecutionPlanReport | None = None
    file_read: bool = False
    data_accessed: bool = False
    git_tag_created: bool = False
    git_tag_pushed: bool = False
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False
    next_phase: str = "AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_REVIEW"
