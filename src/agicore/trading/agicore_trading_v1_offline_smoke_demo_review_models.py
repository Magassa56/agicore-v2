"""Models for AGIcore Trading v1 offline smoke demo review."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from agicore.trading.agicore_trading_v1_offline_smoke_demo_models import (
    AGIcoreTradingV1OfflineSmokeDemoInput,
    AGIcoreTradingV1OfflineSmokeDemoResult,
)


class AGIcoreTradingV1OfflineSmokeDemoReviewState(StrEnum):
    NOT_READY = "NOT_READY"
    AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_REVIEW_INPUT_INVALID = (
        "AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_REVIEW_INPUT_INVALID"
    )
    AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_REVIEW_BLOCKED = "AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_REVIEW_BLOCKED"
    AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_REVIEW_COMPLETED_WITH_WARNINGS = (
        "AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_REVIEW_COMPLETED_WITH_WARNINGS"
    )
    AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_REVIEW_COMPLETED = "AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_REVIEW_COMPLETED"
    READY_FOR_AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE = (
        "READY_FOR_AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE"
    )


class AGIcoreTradingV1OfflineSmokeDemoReviewDecision(StrEnum):
    BLOCK_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_REVIEW = "BLOCK_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_REVIEW"
    REQUIRE_SMOKE_DEMO_FIXES = "REQUIRE_SMOKE_DEMO_FIXES"
    REQUIRE_SMOKE_DEMO_END_TO_END_FIXES = "REQUIRE_SMOKE_DEMO_END_TO_END_FIXES"
    REQUIRE_SMOKE_DEMO_STEP_REVIEW_FIXES = "REQUIRE_SMOKE_DEMO_STEP_REVIEW_FIXES"
    REQUIRE_SMOKE_DEMO_READ_ONLY_DECISION_FIXES = "REQUIRE_SMOKE_DEMO_READ_ONLY_DECISION_FIXES"
    REQUIRE_SMOKE_DEMO_SANDBOX_USABILITY_FIXES = "REQUIRE_SMOKE_DEMO_SANDBOX_USABILITY_FIXES"
    REQUIRE_SMOKE_DEMO_BOUNDARY_FIXES = "REQUIRE_SMOKE_DEMO_BOUNDARY_FIXES"
    REQUIRE_SMOKE_DEMO_NO_OVERCLAIM_FIXES = "REQUIRE_SMOKE_DEMO_NO_OVERCLAIM_FIXES"
    APPROVE_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_REVIEW = (
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_REVIEW"
    )


class AGIcoreTradingV1OfflineSmokeDemoReviewRisk(StrEnum):
    SMOKE_DEMO_NOT_APPROVED = "SMOKE_DEMO_NOT_APPROVED"
    SMOKE_DEMO_END_TO_END_REVIEW_FAILED = "SMOKE_DEMO_END_TO_END_REVIEW_FAILED"
    SMOKE_DEMO_CSV_REPLAY_STEP_FAILED = "SMOKE_DEMO_CSV_REPLAY_STEP_FAILED"
    SMOKE_DEMO_STRATEGY_REPLAY_STEP_FAILED = "SMOKE_DEMO_STRATEGY_REPLAY_STEP_FAILED"
    SMOKE_DEMO_RISK_GUARD_STEP_FAILED = "SMOKE_DEMO_RISK_GUARD_STEP_FAILED"
    SMOKE_DEMO_BROKER_PREVIEW_STEP_FAILED = "SMOKE_DEMO_BROKER_PREVIEW_STEP_FAILED"
    SMOKE_DEMO_JOURNAL_STEP_FAILED = "SMOKE_DEMO_JOURNAL_STEP_FAILED"
    SMOKE_DEMO_OFFLINE_REPORT_STEP_FAILED = "SMOKE_DEMO_OFFLINE_REPORT_STEP_FAILED"
    SMOKE_DEMO_READ_ONLY_DECISION_INVALID = "SMOKE_DEMO_READ_ONLY_DECISION_INVALID"
    SMOKE_DEMO_SANDBOX_USABILITY_INCOMPLETE = "SMOKE_DEMO_SANDBOX_USABILITY_INCOMPLETE"
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


class AGIcoreTradingV1OfflineSmokeDemoReviewRecommendation(StrEnum):
    FIX_SMOKE_DEMO_APPROVAL = "FIX_SMOKE_DEMO_APPROVAL"
    FIX_SMOKE_DEMO_END_TO_END_FLOW = "FIX_SMOKE_DEMO_END_TO_END_FLOW"
    FIX_SMOKE_DEMO_CSV_REPLAY_STEP = "FIX_SMOKE_DEMO_CSV_REPLAY_STEP"
    FIX_SMOKE_DEMO_STRATEGY_REPLAY_STEP = "FIX_SMOKE_DEMO_STRATEGY_REPLAY_STEP"
    FIX_SMOKE_DEMO_RISK_GUARD_STEP = "FIX_SMOKE_DEMO_RISK_GUARD_STEP"
    FIX_SMOKE_DEMO_BROKER_PREVIEW_STEP = "FIX_SMOKE_DEMO_BROKER_PREVIEW_STEP"
    FIX_SMOKE_DEMO_JOURNAL_STEP = "FIX_SMOKE_DEMO_JOURNAL_STEP"
    FIX_SMOKE_DEMO_OFFLINE_REPORT_STEP = "FIX_SMOKE_DEMO_OFFLINE_REPORT_STEP"
    KEEP_SMOKE_DEMO_READ_ONLY = "KEEP_SMOKE_DEMO_READ_ONLY"
    CLARIFY_SANDBOX_USAGE = "CLARIFY_SANDBOX_USAGE"
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
    PREPARE_AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE = (
        "PREPARE_AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE"
    )


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineSmokeDemoReviewFinding:
    finding_id: str
    category: str
    passed: bool
    message: str
    risk: AGIcoreTradingV1OfflineSmokeDemoReviewRisk | None = None


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineSmokeDemoStepReview:
    step_name: str
    passed: bool
    status: str
    message: str
    risk: AGIcoreTradingV1OfflineSmokeDemoReviewRisk | None = None


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineSmokeDemoBoundaryReview:
    passed: bool
    offline_only: bool
    in_memory_only: bool
    file_read: bool
    file_written: bool
    data_accessed: bool
    real_order_submitted: bool
    real_account_accessed: bool
    position_mutated: bool
    risks: tuple[AGIcoreTradingV1OfflineSmokeDemoReviewRisk, ...] = ()


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineSmokeDemoSandboxUsabilityReview:
    passed: bool
    local_sandbox_usable: bool
    deterministic: bool
    in_memory_reports: bool
    no_live_trading_claim: bool
    no_profitability_claim: bool


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineSmokeDemoReviewMetrics:
    expected_step_count: int
    reviewed_step_count: int
    failed_step_count: int
    end_to_end_passed: bool
    read_only_decision_passed: bool
    sandbox_usability_passed: bool
    boundary_passed: bool
    findings_count: int
    global_score: int
    final_decision: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineSmokeDemoReviewScore:
    overall_score: int
    approval_score: int
    end_to_end_score: int
    step_score: int
    read_only_score: int
    sandbox_usability_score: int
    boundary_score: int
    overclaim_score: int
    report_score: int


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineSmokeDemoReviewReport:
    markdown: str
    json: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineSmokeDemoReviewInput:
    smoke_demo_input: AGIcoreTradingV1OfflineSmokeDemoInput | None = field(default_factory=AGIcoreTradingV1OfflineSmokeDemoInput)
    smoke_demo_result: AGIcoreTradingV1OfflineSmokeDemoResult | None = None
    force_smoke_demo_not_approved: bool = False
    force_end_to_end_review_failed: bool = False
    force_csv_replay_step_failed: bool = False
    force_strategy_replay_step_failed: bool = False
    force_risk_guard_step_failed: bool = False
    force_broker_preview_step_failed: bool = False
    force_journal_step_failed: bool = False
    force_offline_report_step_failed: bool = False
    force_read_only_decision_invalid: bool = False
    force_sandbox_usability_incomplete: bool = False
    force_live_trading_overclaim: bool = False
    force_real_broker_overclaim: bool = False
    force_real_order_overclaim: bool = False
    force_profitability_overclaim: bool = False
    force_financial_advice_overclaim: bool = False
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
class AGIcoreTradingV1OfflineSmokeDemoReviewResult:
    state: AGIcoreTradingV1OfflineSmokeDemoReviewState
    decision: AGIcoreTradingV1OfflineSmokeDemoReviewDecision
    score: AGIcoreTradingV1OfflineSmokeDemoReviewScore
    risks: tuple[AGIcoreTradingV1OfflineSmokeDemoReviewRisk, ...]
    recommendations: tuple[AGIcoreTradingV1OfflineSmokeDemoReviewRecommendation, ...]
    findings: tuple[AGIcoreTradingV1OfflineSmokeDemoReviewFinding, ...] = ()
    step_reviews: tuple[AGIcoreTradingV1OfflineSmokeDemoStepReview, ...] = ()
    boundary_review: AGIcoreTradingV1OfflineSmokeDemoBoundaryReview | None = None
    sandbox_usability_review: AGIcoreTradingV1OfflineSmokeDemoSandboxUsabilityReview | None = None
    metrics: AGIcoreTradingV1OfflineSmokeDemoReviewMetrics | None = None
    report: AGIcoreTradingV1OfflineSmokeDemoReviewReport | None = None
    smoke_demo_result: Any = None
    offline_only: bool = True
    in_memory_only: bool = True
    file_read: bool = False
    file_written: bool = False
    data_accessed: bool = False
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False
    next_phase: str = "AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE"
