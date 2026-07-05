"""Models for AGIcore Trading v1 offline final readiness review."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AGIcoreTradingV1OfflineFinalReadinessState(StrEnum):
    NOT_READY = "NOT_READY"
    AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_INPUT_INVALID = (
        "AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_INPUT_INVALID"
    )
    AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_BLOCKED = "AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_BLOCKED"
    AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_COMPLETED_WITH_WARNINGS = (
        "AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_COMPLETED_WITH_WARNINGS"
    )
    AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_COMPLETED = "AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_COMPLETED"
    READY_FOR_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE = "READY_FOR_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE"


class AGIcoreTradingV1OfflineFinalReadinessDecision(StrEnum):
    BLOCK_AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_REVIEW = (
        "BLOCK_AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_REVIEW"
    )
    REQUIRE_FINAL_READINESS_INPUT_FIXES = "REQUIRE_FINAL_READINESS_INPUT_FIXES"
    REQUIRE_FINAL_READINESS_CAPABILITY_FIXES = "REQUIRE_FINAL_READINESS_CAPABILITY_FIXES"
    REQUIRE_FINAL_READINESS_TESTING_EVIDENCE_FIXES = "REQUIRE_FINAL_READINESS_TESTING_EVIDENCE_FIXES"
    REQUIRE_FINAL_READINESS_DOCUMENTATION_FIXES = "REQUIRE_FINAL_READINESS_DOCUMENTATION_FIXES"
    REQUIRE_FINAL_READINESS_SMOKE_DEMO_FIXES = "REQUIRE_FINAL_READINESS_SMOKE_DEMO_FIXES"
    REQUIRE_FINAL_READINESS_SAFETY_FIXES = "REQUIRE_FINAL_READINESS_SAFETY_FIXES"
    REQUIRE_FINAL_READINESS_LIMITATION_FIXES = "REQUIRE_FINAL_READINESS_LIMITATION_FIXES"
    REQUIRE_FINAL_READINESS_NO_OVERCLAIM_FIXES = "REQUIRE_FINAL_READINESS_NO_OVERCLAIM_FIXES"
    APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_REVIEW = (
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_REVIEW"
    )


class AGIcoreTradingV1OfflineFinalReadinessRisk(StrEnum):
    FINAL_READINESS_INPUT_MISSING = "FINAL_READINESS_INPUT_MISSING"
    FINAL_READINESS_CAPABILITIES_INCOMPLETE = "FINAL_READINESS_CAPABILITIES_INCOMPLETE"
    FINAL_READINESS_TESTING_EVIDENCE_MISSING = "FINAL_READINESS_TESTING_EVIDENCE_MISSING"
    FINAL_READINESS_DOCUMENTATION_MISSING = "FINAL_READINESS_DOCUMENTATION_MISSING"
    FINAL_READINESS_SMOKE_DEMO_MISSING = "FINAL_READINESS_SMOKE_DEMO_MISSING"
    FINAL_READINESS_SANDBOX_USAGE_GUIDE_MISSING = "FINAL_READINESS_SANDBOX_USAGE_GUIDE_MISSING"
    FINAL_READINESS_LOCAL_RUNBOOK_MISSING = "FINAL_READINESS_LOCAL_RUNBOOK_MISSING"
    FINAL_READINESS_SAFETY_BOUNDARY_MISSING = "FINAL_READINESS_SAFETY_BOUNDARY_MISSING"
    FINAL_READINESS_LIMITATIONS_MISSING = "FINAL_READINESS_LIMITATIONS_MISSING"
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


class AGIcoreTradingV1OfflineFinalReadinessRecommendation(StrEnum):
    PROVIDE_FINAL_READINESS_INPUT = "PROVIDE_FINAL_READINESS_INPUT"
    COMPLETE_FINAL_READINESS_CAPABILITIES = "COMPLETE_FINAL_READINESS_CAPABILITIES"
    RESTORE_FINAL_READINESS_TESTING_EVIDENCE = "RESTORE_FINAL_READINESS_TESTING_EVIDENCE"
    RESTORE_FINAL_READINESS_DOCUMENTATION = "RESTORE_FINAL_READINESS_DOCUMENTATION"
    RESTORE_FINAL_READINESS_SMOKE_DEMO = "RESTORE_FINAL_READINESS_SMOKE_DEMO"
    RESTORE_FINAL_READINESS_SANDBOX_USAGE_GUIDE = "RESTORE_FINAL_READINESS_SANDBOX_USAGE_GUIDE"
    RESTORE_FINAL_READINESS_LOCAL_RUNBOOK = "RESTORE_FINAL_READINESS_LOCAL_RUNBOOK"
    RESTORE_FINAL_READINESS_SAFETY_BOUNDARIES = "RESTORE_FINAL_READINESS_SAFETY_BOUNDARIES"
    RESTORE_FINAL_READINESS_LIMITATIONS = "RESTORE_FINAL_READINESS_LIMITATIONS"
    REMOVE_LIVE_TRADING_READINESS_CLAIM = "REMOVE_LIVE_TRADING_READINESS_CLAIM"
    REMOVE_REAL_BROKER_READINESS_CLAIM = "REMOVE_REAL_BROKER_READINESS_CLAIM"
    REMOVE_REAL_ORDER_EXECUTION_CLAIM = "REMOVE_REAL_ORDER_EXECUTION_CLAIM"
    REMOVE_PAPER_BROKER_CONNECTION_CLAIM = "REMOVE_PAPER_BROKER_CONNECTION_CLAIM"
    REMOVE_PROFITABILITY_PROOF_CLAIM = "REMOVE_PROFITABILITY_PROOF_CLAIM"
    REMOVE_FINANCIAL_ADVICE_CLAIM = "REMOVE_FINANCIAL_ADVICE_CLAIM"
    REMOVE_FILE_READ = "REMOVE_FILE_READ"
    REMOVE_REAL_DATA_ACCESS = "REMOVE_REAL_DATA_ACCESS"
    REMOVE_DATA_DIRECTORY_ACCESS = "REMOVE_DATA_DIRECTORY_ACCESS"
    REMOVE_REAL_BROKER_ACCESS = "REMOVE_REAL_BROKER_ACCESS"
    REMOVE_REAL_SECRET_ACCESS = "REMOVE_REAL_SECRET_ACCESS"
    REMOVE_NETWORK_ACCESS = "REMOVE_NETWORK_ACCESS"
    REMOVE_ORDER_EXECUTION = "REMOVE_ORDER_EXECUTION"
    REMOVE_ACCOUNT_ACCESS = "REMOVE_ACCOUNT_ACCESS"
    REMOVE_POSITION_MUTATION = "REMOVE_POSITION_MUTATION"
    PREPARE_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE = "PREPARE_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE"


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalReadinessScore:
    overall_score: int
    input_score: int
    capability_score: int
    testing_evidence_score: int
    documentation_score: int
    smoke_demo_score: int
    safety_score: int
    limitation_score: int
    non_goal_score: int
    overclaim_score: int
    boundary_score: int


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalReadinessContext:
    title: str
    status: str
    expected_decision: str
    next_step: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalReadinessCapability:
    name: str
    validated: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalReadinessTestingEvidence:
    name: str
    result: str
    validated: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalReadinessDocumentationCheck:
    name: str
    present: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalReadinessCriterion:
    text: str
    satisfied: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalReadinessKnownLimitation:
    text: str
    documented: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalReadinessNonGoal:
    text: str
    explicit: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalReadinessReport:
    markdown: str
    json: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineFinalReadinessInput:
    review_id: str = "agicore-trading-v1-offline-final-readiness-review"
    force_capabilities_incomplete: bool = False
    force_testing_evidence_missing: bool = False
    force_documentation_missing: bool = False
    force_smoke_demo_missing: bool = False
    force_sandbox_usage_guide_missing: bool = False
    force_local_runbook_missing: bool = False
    force_safety_boundary_missing: bool = False
    force_limitations_missing: bool = False
    force_live_trading_overclaim: bool = False
    force_real_broker_overclaim: bool = False
    force_real_order_overclaim: bool = False
    force_paper_broker_overclaim: bool = False
    force_profitability_overclaim: bool = False
    force_financial_advice_overclaim: bool = False
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
class AGIcoreTradingV1OfflineFinalReadinessResult:
    state: AGIcoreTradingV1OfflineFinalReadinessState
    decision: AGIcoreTradingV1OfflineFinalReadinessDecision
    score: AGIcoreTradingV1OfflineFinalReadinessScore
    risks: tuple[AGIcoreTradingV1OfflineFinalReadinessRisk, ...]
    recommendations: tuple[AGIcoreTradingV1OfflineFinalReadinessRecommendation, ...]
    context: AGIcoreTradingV1OfflineFinalReadinessContext | None = None
    capabilities: tuple[AGIcoreTradingV1OfflineFinalReadinessCapability, ...] = ()
    testing_evidence: tuple[AGIcoreTradingV1OfflineFinalReadinessTestingEvidence, ...] = ()
    documentation_checks: tuple[AGIcoreTradingV1OfflineFinalReadinessDocumentationCheck, ...] = ()
    readiness_criteria: tuple[AGIcoreTradingV1OfflineFinalReadinessCriterion, ...] = ()
    known_limitations: tuple[AGIcoreTradingV1OfflineFinalReadinessKnownLimitation, ...] = ()
    non_goals: tuple[AGIcoreTradingV1OfflineFinalReadinessNonGoal, ...] = ()
    report: AGIcoreTradingV1OfflineFinalReadinessReport | None = None
    file_read: bool = False
    data_accessed: bool = False
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False
    next_phase: str = "AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE"
