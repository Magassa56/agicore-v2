"""Models for AGIcore Trading v1 offline release decision."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from agicore.trading.agicore_trading_v1_candidate_review_models import (
    AGIcoreTradingV1CandidateReviewInput,
    AGIcoreTradingV1CandidateReviewResult,
)


class AGIcoreTradingV1OfflineReleaseDecisionState(StrEnum):
    NOT_READY = "NOT_READY"
    AGICORE_TRADING_V1_OFFLINE_RELEASE_DECISION_INPUT_INVALID = "AGICORE_TRADING_V1_OFFLINE_RELEASE_DECISION_INPUT_INVALID"
    AGICORE_TRADING_V1_OFFLINE_RELEASE_DECISION_BLOCKED = "AGICORE_TRADING_V1_OFFLINE_RELEASE_DECISION_BLOCKED"
    AGICORE_TRADING_V1_OFFLINE_RELEASE_DECISION_COMPLETED_WITH_WARNINGS = "AGICORE_TRADING_V1_OFFLINE_RELEASE_DECISION_COMPLETED_WITH_WARNINGS"
    AGICORE_TRADING_V1_OFFLINE_RELEASE_DECISION_COMPLETED = "AGICORE_TRADING_V1_OFFLINE_RELEASE_DECISION_COMPLETED"
    READY_FOR_AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES = "READY_FOR_AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES"


class AGIcoreTradingV1OfflineReleaseDecisionDecision(StrEnum):
    BLOCK_AGICORE_TRADING_V1_OFFLINE_RELEASE_DECISION = "BLOCK_AGICORE_TRADING_V1_OFFLINE_RELEASE_DECISION"
    REQUIRE_V1_CANDIDATE_REVIEW_FIXES = "REQUIRE_V1_CANDIDATE_REVIEW_FIXES"
    REQUIRE_OFFLINE_RELEASE_SCOPE_FIXES = "REQUIRE_OFFLINE_RELEASE_SCOPE_FIXES"
    REQUIRE_OFFLINE_RELEASE_CAPABILITY_FIXES = "REQUIRE_OFFLINE_RELEASE_CAPABILITY_FIXES"
    REQUIRE_OFFLINE_RELEASE_SAFETY_FIXES = "REQUIRE_OFFLINE_RELEASE_SAFETY_FIXES"
    REQUIRE_OFFLINE_RELEASE_TESTING_EVIDENCE_FIXES = "REQUIRE_OFFLINE_RELEASE_TESTING_EVIDENCE_FIXES"
    REQUIRE_OFFLINE_RELEASE_LIMITATION_FIXES = "REQUIRE_OFFLINE_RELEASE_LIMITATION_FIXES"
    REQUIRE_OFFLINE_RELEASE_NON_GOAL_FIXES = "REQUIRE_OFFLINE_RELEASE_NON_GOAL_FIXES"
    APPROVE_AGICORE_TRADING_V1_OFFLINE_RELEASE_DECISION = "APPROVE_AGICORE_TRADING_V1_OFFLINE_RELEASE_DECISION"


class AGIcoreTradingV1OfflineReleaseDecisionRisk(StrEnum):
    V1_CANDIDATE_REVIEW_NOT_APPROVED = "V1_CANDIDATE_REVIEW_NOT_APPROVED"
    OFFLINE_RELEASE_SCOPE_INVALID = "OFFLINE_RELEASE_SCOPE_INVALID"
    OFFLINE_RELEASE_CAPABILITY_INCOMPLETE = "OFFLINE_RELEASE_CAPABILITY_INCOMPLETE"
    OFFLINE_RELEASE_SAFETY_BOUNDARY_INCOMPLETE = "OFFLINE_RELEASE_SAFETY_BOUNDARY_INCOMPLETE"
    OFFLINE_RELEASE_TESTING_EVIDENCE_MISSING = "OFFLINE_RELEASE_TESTING_EVIDENCE_MISSING"
    OFFLINE_RELEASE_LIMITATIONS_MISSING = "OFFLINE_RELEASE_LIMITATIONS_MISSING"
    OFFLINE_RELEASE_NON_GOALS_MISSING = "OFFLINE_RELEASE_NON_GOALS_MISSING"
    LIVE_TRADING_READINESS_OVERCLAIM = "LIVE_TRADING_READINESS_OVERCLAIM"
    REAL_BROKER_READINESS_OVERCLAIM = "REAL_BROKER_READINESS_OVERCLAIM"
    REAL_ORDER_EXECUTION_OVERCLAIM = "REAL_ORDER_EXECUTION_OVERCLAIM"
    PROFITABILITY_PROOF_OVERCLAIM = "PROFITABILITY_PROOF_OVERCLAIM"
    FINANCIAL_ADVICE_OVERCLAIM = "FINANCIAL_ADVICE_OVERCLAIM"
    FILE_READ_BOUNDARY_VIOLATION = "FILE_READ_BOUNDARY_VIOLATION"
    FILE_WRITE_BOUNDARY_VIOLATION = "FILE_WRITE_BOUNDARY_VIOLATION"
    REAL_DATA_ACCESS_BOUNDARY_VIOLATION = "REAL_DATA_ACCESS_BOUNDARY_VIOLATION"
    DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION = "DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION"
    REAL_BROKER_BOUNDARY_VIOLATION = "REAL_BROKER_BOUNDARY_VIOLATION"
    REAL_SECRET_BOUNDARY_VIOLATION = "REAL_SECRET_BOUNDARY_VIOLATION"
    NETWORK_BOUNDARY_VIOLATION = "NETWORK_BOUNDARY_VIOLATION"
    ORDER_EXECUTION_BOUNDARY_VIOLATION = "ORDER_EXECUTION_BOUNDARY_VIOLATION"
    ACCOUNT_ACCESS_BOUNDARY_VIOLATION = "ACCOUNT_ACCESS_BOUNDARY_VIOLATION"
    POSITION_MUTATION_BOUNDARY_VIOLATION = "POSITION_MUTATION_BOUNDARY_VIOLATION"


class AGIcoreTradingV1OfflineReleaseDecisionRecommendation(StrEnum):
    FIX_V1_CANDIDATE_REVIEW_APPROVAL = "FIX_V1_CANDIDATE_REVIEW_APPROVAL"
    CLARIFY_OFFLINE_RELEASE_SCOPE = "CLARIFY_OFFLINE_RELEASE_SCOPE"
    COMPLETE_OFFLINE_RELEASE_CAPABILITIES = "COMPLETE_OFFLINE_RELEASE_CAPABILITIES"
    FIX_OFFLINE_RELEASE_SAFETY_BOUNDARIES = "FIX_OFFLINE_RELEASE_SAFETY_BOUNDARIES"
    PROVIDE_OFFLINE_RELEASE_TESTING_EVIDENCE = "PROVIDE_OFFLINE_RELEASE_TESTING_EVIDENCE"
    DOCUMENT_OFFLINE_RELEASE_LIMITATIONS = "DOCUMENT_OFFLINE_RELEASE_LIMITATIONS"
    DOCUMENT_OFFLINE_RELEASE_NON_GOALS = "DOCUMENT_OFFLINE_RELEASE_NON_GOALS"
    REMOVE_LIVE_TRADING_READINESS_CLAIM = "REMOVE_LIVE_TRADING_READINESS_CLAIM"
    REMOVE_REAL_BROKER_READINESS_CLAIM = "REMOVE_REAL_BROKER_READINESS_CLAIM"
    REMOVE_REAL_ORDER_EXECUTION_CLAIM = "REMOVE_REAL_ORDER_EXECUTION_CLAIM"
    REMOVE_PROFITABILITY_PROOF_CLAIM = "REMOVE_PROFITABILITY_PROOF_CLAIM"
    REMOVE_FINANCIAL_ADVICE_CLAIM = "REMOVE_FINANCIAL_ADVICE_CLAIM"
    REMOVE_FILE_READ = "REMOVE_FILE_READ"
    REMOVE_FILE_WRITE = "REMOVE_FILE_WRITE"
    REMOVE_REAL_DATA_ACCESS = "REMOVE_REAL_DATA_ACCESS"
    REMOVE_DATA_DIRECTORY_ACCESS = "REMOVE_DATA_DIRECTORY_ACCESS"
    REMOVE_REAL_BROKER_ACCESS = "REMOVE_REAL_BROKER_ACCESS"
    REMOVE_REAL_SECRET_ACCESS = "REMOVE_REAL_SECRET_ACCESS"
    REMOVE_NETWORK_ACCESS = "REMOVE_NETWORK_ACCESS"
    REMOVE_ORDER_EXECUTION = "REMOVE_ORDER_EXECUTION"
    REMOVE_ACCOUNT_ACCESS = "REMOVE_ACCOUNT_ACCESS"
    REMOVE_POSITION_MUTATION = "REMOVE_POSITION_MUTATION"
    PREPARE_AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES = "PREPARE_AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES"


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleaseDecisionScore:
    overall_score: int
    review_score: int
    scope_score: int
    capability_score: int
    safety_score: int
    testing_score: int
    limitation_score: int
    non_goal_score: int
    product_score: int
    report_score: int


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleaseScope:
    name: str
    offline_only: bool
    sandbox_only: bool
    in_memory_decision_only: bool
    valid: bool


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleaseCapabilityReadiness:
    expected_capabilities: tuple[str, ...]
    confirmed_capabilities: tuple[str, ...]
    missing_capabilities: tuple[str, ...]
    ready: bool


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleaseSafetyBoundary:
    passed: bool
    file_read: bool = False
    file_written: bool = False
    data_accessed: bool = False
    real_broker_accessed: bool = False
    real_secret_read: bool = False
    network_used: bool = False
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleaseTestingEvidence:
    targeted_tests_passed: bool
    trading_tests_passed: bool
    unit_tests_passed: bool
    diff_check_passed: bool
    complete: bool


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleaseKnownLimitation:
    code: str
    description: str
    documented: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleaseNonGoal:
    code: str
    description: str
    documented: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleaseProductReadiness:
    release_label: str
    offline_release_approved: bool
    live_trading_ready: bool
    real_broker_ready: bool
    real_orders_ready: bool
    profitability_proven: bool
    financial_advice: bool


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleaseDecisionSummary:
    decision: str
    release_label: str
    summary: str
    next_phase: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleaseDecisionMetrics:
    expected_capability_count: int
    confirmed_capability_count: int
    missing_capability_count: int
    limitation_count: int
    non_goal_count: int
    testing_evidence_complete: bool
    global_score: int
    final_decision: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleaseDecisionReport:
    markdown: str
    json: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleaseDecisionInput:
    candidate_review_input: AGIcoreTradingV1CandidateReviewInput | None = field(default_factory=AGIcoreTradingV1CandidateReviewInput)
    candidate_review_result: AGIcoreTradingV1CandidateReviewResult | None = None
    force_candidate_review_not_approved: bool = False
    force_scope_invalid: bool = False
    force_capability_incomplete: bool = False
    force_safety_boundary_incomplete: bool = False
    force_testing_evidence_missing: bool = False
    force_limitations_missing: bool = False
    force_non_goals_missing: bool = False
    force_live_trading_readiness_overclaim: bool = False
    force_real_broker_readiness_overclaim: bool = False
    force_real_order_execution_overclaim: bool = False
    force_profitability_proof_overclaim: bool = False
    force_financial_advice_overclaim: bool = False
    force_report_missing: bool = False
    targeted_tests_passed: bool = True
    trading_tests_passed: bool = True
    unit_tests_passed: bool = True
    diff_check_passed: bool = True
    file_read_requested: bool = False
    file_write_requested: bool = False
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
class AGIcoreTradingV1OfflineReleaseDecisionResult:
    state: AGIcoreTradingV1OfflineReleaseDecisionState
    decision: AGIcoreTradingV1OfflineReleaseDecisionDecision
    score: AGIcoreTradingV1OfflineReleaseDecisionScore
    risks: tuple[AGIcoreTradingV1OfflineReleaseDecisionRisk, ...]
    recommendations: tuple[AGIcoreTradingV1OfflineReleaseDecisionRecommendation, ...]
    scope: AGIcoreTradingV1OfflineReleaseScope | None = None
    capability_readiness: AGIcoreTradingV1OfflineReleaseCapabilityReadiness | None = None
    safety_boundary: AGIcoreTradingV1OfflineReleaseSafetyBoundary | None = None
    testing_evidence: AGIcoreTradingV1OfflineReleaseTestingEvidence | None = None
    known_limitations: tuple[AGIcoreTradingV1OfflineReleaseKnownLimitation, ...] = ()
    non_goals: tuple[AGIcoreTradingV1OfflineReleaseNonGoal, ...] = ()
    product_readiness: AGIcoreTradingV1OfflineReleaseProductReadiness | None = None
    summary: AGIcoreTradingV1OfflineReleaseDecisionSummary | None = None
    metrics: AGIcoreTradingV1OfflineReleaseDecisionMetrics | None = None
    report: AGIcoreTradingV1OfflineReleaseDecisionReport | None = None
    candidate_review_result: Any = None
    file_read: bool = False
    file_written: bool = False
    data_accessed: bool = False
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False
    next_phase: str = "AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES"
