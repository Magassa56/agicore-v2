"""Models for AGIcore Trading v1 offline candidate review."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from agicore.trading.agicore_trading_v1_candidate_models import (
    AGIcoreTradingV1CandidateInput,
    AGIcoreTradingV1CandidateResult,
)


class AGIcoreTradingV1CandidateReviewState(StrEnum):
    NOT_READY = "NOT_READY"
    AGICORE_TRADING_V1_CANDIDATE_REVIEW_INPUT_INVALID = "AGICORE_TRADING_V1_CANDIDATE_REVIEW_INPUT_INVALID"
    AGICORE_TRADING_V1_CANDIDATE_REVIEW_BLOCKED = "AGICORE_TRADING_V1_CANDIDATE_REVIEW_BLOCKED"
    AGICORE_TRADING_V1_CANDIDATE_REVIEW_COMPLETED_WITH_WARNINGS = "AGICORE_TRADING_V1_CANDIDATE_REVIEW_COMPLETED_WITH_WARNINGS"
    AGICORE_TRADING_V1_CANDIDATE_REVIEW_COMPLETED = "AGICORE_TRADING_V1_CANDIDATE_REVIEW_COMPLETED"
    READY_FOR_AGICORE_TRADING_V1_OFFLINE_RELEASE_DECISION = "READY_FOR_AGICORE_TRADING_V1_OFFLINE_RELEASE_DECISION"


class AGIcoreTradingV1CandidateReviewDecision(StrEnum):
    BLOCK_AGICORE_TRADING_V1_CANDIDATE_REVIEW = "BLOCK_AGICORE_TRADING_V1_CANDIDATE_REVIEW"
    REQUIRE_AGICORE_TRADING_V1_CANDIDATE_FIXES = "REQUIRE_AGICORE_TRADING_V1_CANDIDATE_FIXES"
    REQUIRE_V1_CAPABILITY_COVERAGE_FIXES = "REQUIRE_V1_CAPABILITY_COVERAGE_FIXES"
    REQUIRE_V1_SMOKE_REPLAY_FIXES = "REQUIRE_V1_SMOKE_REPLAY_FIXES"
    REQUIRE_V1_SAFETY_BOUNDARY_FIXES = "REQUIRE_V1_SAFETY_BOUNDARY_FIXES"
    REQUIRE_V1_PRODUCT_READINESS_FIXES = "REQUIRE_V1_PRODUCT_READINESS_FIXES"
    REQUIRE_V1_LIMITATION_DOCUMENTATION_FIXES = "REQUIRE_V1_LIMITATION_DOCUMENTATION_FIXES"
    APPROVE_AGICORE_TRADING_V1_CANDIDATE_REVIEW = "APPROVE_AGICORE_TRADING_V1_CANDIDATE_REVIEW"


class AGIcoreTradingV1CandidateReviewRisk(StrEnum):
    AGICORE_TRADING_V1_CANDIDATE_NOT_APPROVED = "AGICORE_TRADING_V1_CANDIDATE_NOT_APPROVED"
    V1_CAPABILITY_COVERAGE_INCOMPLETE = "V1_CAPABILITY_COVERAGE_INCOMPLETE"
    CSV_REPLAY_CAPABILITY_REVIEW_FAILED = "CSV_REPLAY_CAPABILITY_REVIEW_FAILED"
    SYNTHETIC_MARKET_CAPABILITY_REVIEW_FAILED = "SYNTHETIC_MARKET_CAPABILITY_REVIEW_FAILED"
    STRATEGY_REPLAY_CAPABILITY_REVIEW_FAILED = "STRATEGY_REPLAY_CAPABILITY_REVIEW_FAILED"
    SIMULATED_BROKER_CAPABILITY_REVIEW_FAILED = "SIMULATED_BROKER_CAPABILITY_REVIEW_FAILED"
    RISK_GUARD_CAPABILITY_REVIEW_FAILED = "RISK_GUARD_CAPABILITY_REVIEW_FAILED"
    JOURNAL_CAPABILITY_REVIEW_FAILED = "JOURNAL_CAPABILITY_REVIEW_FAILED"
    OFFLINE_REPORT_CAPABILITY_REVIEW_FAILED = "OFFLINE_REPORT_CAPABILITY_REVIEW_FAILED"
    V1_SMOKE_REPLAY_REVIEW_FAILED = "V1_SMOKE_REPLAY_REVIEW_FAILED"
    V1_PRODUCT_READINESS_INCOMPLETE = "V1_PRODUCT_READINESS_INCOMPLETE"
    V1_LIMITATIONS_NOT_DOCUMENTED = "V1_LIMITATIONS_NOT_DOCUMENTED"
    LIVE_TRADING_READINESS_OVERCLAIM = "LIVE_TRADING_READINESS_OVERCLAIM"
    PROFITABILITY_PROOF_MISSING = "PROFITABILITY_PROOF_MISSING"
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


class AGIcoreTradingV1CandidateReviewRecommendation(StrEnum):
    FIX_AGICORE_TRADING_V1_CANDIDATE_APPROVAL = "FIX_AGICORE_TRADING_V1_CANDIDATE_APPROVAL"
    COMPLETE_V1_CAPABILITY_COVERAGE = "COMPLETE_V1_CAPABILITY_COVERAGE"
    FIX_CSV_REPLAY_CAPABILITY_REVIEW = "FIX_CSV_REPLAY_CAPABILITY_REVIEW"
    FIX_SYNTHETIC_MARKET_CAPABILITY_REVIEW = "FIX_SYNTHETIC_MARKET_CAPABILITY_REVIEW"
    FIX_STRATEGY_REPLAY_CAPABILITY_REVIEW = "FIX_STRATEGY_REPLAY_CAPABILITY_REVIEW"
    FIX_SIMULATED_BROKER_CAPABILITY_REVIEW = "FIX_SIMULATED_BROKER_CAPABILITY_REVIEW"
    FIX_RISK_GUARD_CAPABILITY_REVIEW = "FIX_RISK_GUARD_CAPABILITY_REVIEW"
    FIX_JOURNAL_CAPABILITY_REVIEW = "FIX_JOURNAL_CAPABILITY_REVIEW"
    FIX_OFFLINE_REPORT_CAPABILITY_REVIEW = "FIX_OFFLINE_REPORT_CAPABILITY_REVIEW"
    FIX_V1_SMOKE_REPLAY_REVIEW = "FIX_V1_SMOKE_REPLAY_REVIEW"
    CLARIFY_OFFLINE_PRODUCT_READINESS = "CLARIFY_OFFLINE_PRODUCT_READINESS"
    DOCUMENT_V1_LIMITATIONS = "DOCUMENT_V1_LIMITATIONS"
    REMOVE_LIVE_TRADING_READINESS_CLAIM = "REMOVE_LIVE_TRADING_READINESS_CLAIM"
    REMOVE_PROFITABILITY_CLAIM = "REMOVE_PROFITABILITY_CLAIM"
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
    PROCEED_TO_OFFLINE_RELEASE_DECISION = "PROCEED_TO_OFFLINE_RELEASE_DECISION"


@dataclass(frozen=True)
class AGIcoreTradingV1CandidateReviewScore:
    overall_score: int
    candidate_score: int
    capability_score: int
    smoke_replay_score: int
    safety_boundary_score: int
    product_readiness_score: int
    limitations_score: int
    claim_score: int
    report_score: int


@dataclass(frozen=True)
class AGIcoreTradingV1CandidateReviewFinding:
    finding_id: str
    category: str
    passed: bool
    message: str
    risk: AGIcoreTradingV1CandidateReviewRisk | None = None


@dataclass(frozen=True)
class AGIcoreTradingV1CapabilityReview:
    capability: str
    passed: bool
    detail: str
    source_decision: str = ""
    source_risks: tuple[str, ...] = ()


@dataclass(frozen=True)
class AGIcoreTradingV1SmokeReplayReview:
    passed: bool
    status: str
    read_only: bool
    offline_only: bool
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False


@dataclass(frozen=True)
class AGIcoreTradingV1SafetyBoundaryReview:
    passed: bool
    offline_only: bool
    in_memory_only: bool
    file_read: bool
    file_written: bool
    data_accessed: bool
    real_order_submitted: bool
    real_account_accessed: bool
    position_mutated: bool
    risks: tuple[AGIcoreTradingV1CandidateReviewRisk, ...] = ()


@dataclass(frozen=True)
class AGIcoreTradingV1ProductReadinessReview:
    passed: bool
    offline_candidate_only: bool
    product_decision: str
    no_live_trading_claim: bool
    no_profitability_claim: bool


@dataclass(frozen=True)
class AGIcoreTradingV1KnownLimitation:
    code: str
    description: str
    documented: bool = True
    severity: str = "INFO"


@dataclass(frozen=True)
class AGIcoreTradingV1CandidateReviewMetrics:
    expected_capability_count: int
    reviewed_capability_count: int
    failed_capability_count: int
    smoke_replay_passed: bool
    safety_boundaries_passed: bool
    known_limitations_count: int
    findings_count: int
    global_score: int
    final_decision: str


@dataclass(frozen=True)
class AGIcoreTradingV1CandidateReviewReport:
    markdown: str
    json: str


@dataclass(frozen=True)
class AGIcoreTradingV1CandidateReviewInput:
    candidate_input: AGIcoreTradingV1CandidateInput | None = field(default_factory=AGIcoreTradingV1CandidateInput)
    candidate_result: AGIcoreTradingV1CandidateResult | None = None
    force_candidate_not_approved: bool = False
    force_capability_coverage_incomplete: bool = False
    force_csv_replay_review_failed: bool = False
    force_synthetic_market_review_failed: bool = False
    force_strategy_replay_review_failed: bool = False
    force_simulated_broker_review_failed: bool = False
    force_risk_guard_review_failed: bool = False
    force_journal_review_failed: bool = False
    force_offline_report_review_failed: bool = False
    force_smoke_replay_failed: bool = False
    force_product_readiness_incomplete: bool = False
    force_limitations_not_documented: bool = False
    force_live_trading_readiness_overclaim: bool = False
    force_profitability_claim: bool = False
    force_report_missing: bool = False
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
class AGIcoreTradingV1CandidateReviewResult:
    state: AGIcoreTradingV1CandidateReviewState
    decision: AGIcoreTradingV1CandidateReviewDecision
    score: AGIcoreTradingV1CandidateReviewScore
    risks: tuple[AGIcoreTradingV1CandidateReviewRisk, ...]
    recommendations: tuple[AGIcoreTradingV1CandidateReviewRecommendation, ...]
    findings: tuple[AGIcoreTradingV1CandidateReviewFinding, ...] = ()
    capability_reviews: tuple[AGIcoreTradingV1CapabilityReview, ...] = ()
    smoke_replay_review: AGIcoreTradingV1SmokeReplayReview | None = None
    safety_boundary_review: AGIcoreTradingV1SafetyBoundaryReview | None = None
    product_readiness_review: AGIcoreTradingV1ProductReadinessReview | None = None
    known_limitations: tuple[AGIcoreTradingV1KnownLimitation, ...] = ()
    metrics: AGIcoreTradingV1CandidateReviewMetrics | None = None
    report: AGIcoreTradingV1CandidateReviewReport | None = None
    candidate_result: Any = None
    offline_only: bool = True
    in_memory_only: bool = True
    file_read: bool = False
    file_written: bool = False
    data_accessed: bool = False
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False
    next_phase: str = "AGICORE_TRADING_V1_OFFLINE_RELEASE_DECISION"
