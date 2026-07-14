"""Models for AGIcore Trading v1 offline tag creation final preflight."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AGIcoreTradingV1OfflineTagCreationFinalPreflightState(StrEnum):
    NOT_READY = "NOT_READY"
    AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT_INPUT_INVALID = (
        "AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT_INPUT_INVALID"
    )
    AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT_BLOCKED = (
        "AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT_BLOCKED"
    )
    AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT_COMPLETED_WITH_WARNINGS = (
        "AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT_COMPLETED_WITH_WARNINGS"
    )
    AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT_COMPLETED = (
        "AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT_COMPLETED"
    )
    READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT_REVIEW = (
        "READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT_REVIEW"
    )


class AGIcoreTradingV1OfflineTagCreationFinalPreflightDecision(StrEnum):
    BLOCK_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT = (
        "BLOCK_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT"
    )
    REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_INPUT_FIXES = "REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_INPUT_FIXES"
    REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_PREREQUISITE_FIXES = (
        "REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_PREREQUISITE_FIXES"
    )
    REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_HUMAN_CONFIRMATION_FIXES = (
        "REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_HUMAN_CONFIRMATION_FIXES"
    )
    REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_TAG_NAME_FIXES = "REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_TAG_NAME_FIXES"
    REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_VERSION_FIXES = "REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_VERSION_FIXES"
    REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_CHECK_FIXES = "REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_CHECK_FIXES"
    REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_EXPECTED_RESULT_FIXES = (
        "REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_EXPECTED_RESULT_FIXES"
    )
    REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_COMMAND_DOCUMENTATION_FIXES = (
        "REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_COMMAND_DOCUMENTATION_FIXES"
    )
    REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_STOP_RULE_FIXES = "REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_STOP_RULE_FIXES"
    REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_NO_OVERCLAIM_FIXES = (
        "REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_NO_OVERCLAIM_FIXES"
    )
    APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT = (
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT"
    )


class AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk(StrEnum):
    TAG_CREATION_FINAL_PREFLIGHT_INPUT_MISSING = "TAG_CREATION_FINAL_PREFLIGHT_INPUT_MISSING"
    TAG_CREATION_FINAL_PREFLIGHT_PREREQUISITES_INCOMPLETE = (
        "TAG_CREATION_FINAL_PREFLIGHT_PREREQUISITES_INCOMPLETE"
    )
    FINAL_TAG_CREATION_HUMAN_CONFIRMATION_NOT_APPROVED = "FINAL_TAG_CREATION_HUMAN_CONFIRMATION_NOT_APPROVED"
    MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_NOT_APPROVED = (
        "MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_NOT_APPROVED"
    )
    FINAL_MANUAL_TAG_AUTHORIZATION_NOT_APPROVED = "FINAL_MANUAL_TAG_AUTHORIZATION_NOT_APPROVED"
    TAG_CREATION_EXECUTION_PLAN_REVIEW_NOT_APPROVED = "TAG_CREATION_EXECUTION_PLAN_REVIEW_NOT_APPROVED"
    MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED = "MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED"
    HUMAN_TAG_GO_NO_GO_NOT_APPROVED = "HUMAN_TAG_GO_NO_GO_NOT_APPROVED"
    RELEASE_PACKAGE_REVIEW_NOT_APPROVED = "RELEASE_PACKAGE_REVIEW_NOT_APPROVED"
    FINAL_READINESS_REVIEW_NOT_APPROVED = "FINAL_READINESS_REVIEW_NOT_APPROVED"
    TAG_CREATION_FINAL_PREFLIGHT_HUMAN_CONFIRMATION_MISSING = (
        "TAG_CREATION_FINAL_PREFLIGHT_HUMAN_CONFIRMATION_MISSING"
    )
    TAG_CREATION_FINAL_PREFLIGHT_TAG_NAME_INVALID = "TAG_CREATION_FINAL_PREFLIGHT_TAG_NAME_INVALID"
    TAG_CREATION_FINAL_PREFLIGHT_VERSION_INVALID = "TAG_CREATION_FINAL_PREFLIGHT_VERSION_INVALID"
    TAG_CREATION_FINAL_PREFLIGHT_CHECKS_MISSING = "TAG_CREATION_FINAL_PREFLIGHT_CHECKS_MISSING"
    TAG_CREATION_FINAL_PREFLIGHT_EXPECTED_RESULTS_MISSING = (
        "TAG_CREATION_FINAL_PREFLIGHT_EXPECTED_RESULTS_MISSING"
    )
    TAG_CREATION_FINAL_PREFLIGHT_COMMANDS_NOT_DOCUMENTATION_ONLY = (
        "TAG_CREATION_FINAL_PREFLIGHT_COMMANDS_NOT_DOCUMENTATION_ONLY"
    )
    TAG_CREATION_FINAL_PREFLIGHT_STOP_RULES_MISSING = "TAG_CREATION_FINAL_PREFLIGHT_STOP_RULES_MISSING"
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


class AGIcoreTradingV1OfflineTagCreationFinalPreflightRecommendation(StrEnum):
    PREPARE_FINAL_PREFLIGHT_REVIEW = "PREPARE_FINAL_PREFLIGHT_REVIEW"
    PROVIDE_FINAL_PREFLIGHT_INPUT = "PROVIDE_FINAL_PREFLIGHT_INPUT"
    RESTORE_PREREQUISITES = "RESTORE_PREREQUISITES"
    RESTORE_HUMAN_CONFIRMATION = "RESTORE_HUMAN_CONFIRMATION"
    RESTORE_TAG_NAME = "RESTORE_TAG_NAME"
    RESTORE_VERSION = "RESTORE_VERSION"
    RESTORE_REQUIRED_CHECKS = "RESTORE_REQUIRED_CHECKS"
    RESTORE_EXPECTED_RESULTS = "RESTORE_EXPECTED_RESULTS"
    KEEP_COMMANDS_DOCUMENTATION_ONLY = "KEEP_COMMANDS_DOCUMENTATION_ONLY"
    RESTORE_STOP_RULES = "RESTORE_STOP_RULES"
    DO_NOT_CREATE_GIT_TAG_IN_THIS_PHASE = "DO_NOT_CREATE_GIT_TAG_IN_THIS_PHASE"
    DO_NOT_PUSH_GIT_TAG_IN_THIS_PHASE = "DO_NOT_PUSH_GIT_TAG_IN_THIS_PHASE"
    REMOVE_OVERCLAIM = "REMOVE_OVERCLAIM"
    REMOVE_BOUNDARY_VIOLATION = "REMOVE_BOUNDARY_VIOLATION"


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationFinalPreflightScore:
    overall_score: int
    input_score: int
    prerequisite_score: int
    human_confirmation_score: int
    tag_name_score: int
    version_score: int
    check_score: int
    expected_result_score: int
    command_score: int
    stop_rule_score: int
    no_tag_score: int
    safety_score: int
    boundary_score: int


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationFinalPreflightPrerequisite:
    name: str
    approved: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationFinalPreflightCheck:
    check: str
    present: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationFinalPreflightExpectedResult:
    result: str
    present: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationFinalPreflightCommand:
    command: str
    documentation_only: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationFinalPreflightStopRule:
    rule: str
    present: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationFinalPreflightTagMetadata:
    tag_name: str
    version: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationFinalPreflightContext:
    preflight_id: str
    tag_metadata: AGIcoreTradingV1OfflineTagCreationFinalPreflightTagMetadata
    prerequisites: tuple[AGIcoreTradingV1OfflineTagCreationFinalPreflightPrerequisite, ...]
    human_confirmation_present: bool
    required_checks: tuple[AGIcoreTradingV1OfflineTagCreationFinalPreflightCheck, ...]
    expected_results: tuple[AGIcoreTradingV1OfflineTagCreationFinalPreflightExpectedResult, ...]
    commands: tuple[AGIcoreTradingV1OfflineTagCreationFinalPreflightCommand, ...]
    stop_rules: tuple[AGIcoreTradingV1OfflineTagCreationFinalPreflightStopRule, ...]


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationFinalPreflightReport:
    markdown: str
    json: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineTagCreationFinalPreflightInput:
    preflight_id: str = "agicore-trading-v1-offline-tag-creation-final-preflight"
    prerequisites_complete: bool = True
    final_tag_creation_human_confirmation_approved: bool = True
    command_sheet_review_approved: bool = True
    final_manual_tag_authorization_approved: bool = True
    execution_plan_review_approved: bool = True
    manual_tag_creation_approval_approved: bool = True
    human_tag_go_no_go_approved: bool = True
    release_package_review_approved: bool = True
    final_readiness_review_approved: bool = True
    human_confirmation_present: bool = True
    tag_name: str = "agicore-trading-v1-offline"
    version: str = "v1.0.0-offline"
    required_checks_present: bool = True
    expected_results_present: bool = True
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
class AGIcoreTradingV1OfflineTagCreationFinalPreflightResult:
    state: AGIcoreTradingV1OfflineTagCreationFinalPreflightState
    decision: AGIcoreTradingV1OfflineTagCreationFinalPreflightDecision
    score: AGIcoreTradingV1OfflineTagCreationFinalPreflightScore
    risks: tuple[AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk, ...]
    recommendations: tuple[AGIcoreTradingV1OfflineTagCreationFinalPreflightRecommendation, ...]
    context: AGIcoreTradingV1OfflineTagCreationFinalPreflightContext | None = None
    report: AGIcoreTradingV1OfflineTagCreationFinalPreflightReport | None = None
    file_read: bool = False
    data_accessed: bool = False
    git_tag_created: bool = False
    git_tag_pushed: bool = False
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False
    next_phase: str = "AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT_REVIEW"
