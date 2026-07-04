"""Models for AGIcore Trading v1 offline release notes."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from agicore.trading.agicore_trading_v1_offline_release_decision_models import (
    AGIcoreTradingV1OfflineReleaseDecisionInput,
    AGIcoreTradingV1OfflineReleaseDecisionResult,
)


class AGIcoreTradingV1OfflineReleaseNotesState(StrEnum):
    NOT_READY = "NOT_READY"
    AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES_INPUT_INVALID = "AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES_INPUT_INVALID"
    AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES_BLOCKED = "AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES_BLOCKED"
    AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES_COMPLETED_WITH_WARNINGS = "AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES_COMPLETED_WITH_WARNINGS"
    AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES_COMPLETED = "AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES_COMPLETED"
    READY_FOR_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO = "READY_FOR_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO"


class AGIcoreTradingV1OfflineReleaseNotesDecision(StrEnum):
    BLOCK_AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES = "BLOCK_AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES"
    REQUIRE_OFFLINE_RELEASE_NOTES_INPUT_FIXES = "REQUIRE_OFFLINE_RELEASE_NOTES_INPUT_FIXES"
    REQUIRE_OFFLINE_RELEASE_NOTES_CAPABILITY_FIXES = "REQUIRE_OFFLINE_RELEASE_NOTES_CAPABILITY_FIXES"
    REQUIRE_OFFLINE_RELEASE_NOTES_NON_GOAL_FIXES = "REQUIRE_OFFLINE_RELEASE_NOTES_NON_GOAL_FIXES"
    REQUIRE_OFFLINE_RELEASE_NOTES_TESTING_EVIDENCE_FIXES = "REQUIRE_OFFLINE_RELEASE_NOTES_TESTING_EVIDENCE_FIXES"
    REQUIRE_OFFLINE_RELEASE_NOTES_LIMITATION_FIXES = "REQUIRE_OFFLINE_RELEASE_NOTES_LIMITATION_FIXES"
    REQUIRE_OFFLINE_RELEASE_NOTES_SAFETY_LANGUAGE_FIXES = "REQUIRE_OFFLINE_RELEASE_NOTES_SAFETY_LANGUAGE_FIXES"
    REQUIRE_OFFLINE_RELEASE_NOTES_NO_OVERCLAIM_FIXES = "REQUIRE_OFFLINE_RELEASE_NOTES_NO_OVERCLAIM_FIXES"
    APPROVE_AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES = "APPROVE_AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES"


class AGIcoreTradingV1OfflineReleaseNotesRisk(StrEnum):
    OFFLINE_RELEASE_NOTES_INPUT_MISSING = "OFFLINE_RELEASE_NOTES_INPUT_MISSING"
    OFFLINE_RELEASE_NOTES_CAPABILITIES_MISSING = "OFFLINE_RELEASE_NOTES_CAPABILITIES_MISSING"
    OFFLINE_RELEASE_NOTES_NON_GOALS_MISSING = "OFFLINE_RELEASE_NOTES_NON_GOALS_MISSING"
    OFFLINE_RELEASE_NOTES_TESTING_EVIDENCE_MISSING = "OFFLINE_RELEASE_NOTES_TESTING_EVIDENCE_MISSING"
    OFFLINE_RELEASE_NOTES_LIMITATIONS_MISSING = "OFFLINE_RELEASE_NOTES_LIMITATIONS_MISSING"
    OFFLINE_RELEASE_NOTES_SAFETY_LANGUAGE_MISSING = "OFFLINE_RELEASE_NOTES_SAFETY_LANGUAGE_MISSING"
    LIVE_TRADING_READINESS_OVERCLAIM = "LIVE_TRADING_READINESS_OVERCLAIM"
    REAL_BROKER_READINESS_OVERCLAIM = "REAL_BROKER_READINESS_OVERCLAIM"
    REAL_ORDER_EXECUTION_OVERCLAIM = "REAL_ORDER_EXECUTION_OVERCLAIM"
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


class AGIcoreTradingV1OfflineReleaseNotesRecommendation(StrEnum):
    PROVIDE_OFFLINE_RELEASE_NOTES_INPUT = "PROVIDE_OFFLINE_RELEASE_NOTES_INPUT"
    RESTORE_OFFLINE_RELEASE_NOTES_CAPABILITIES = "RESTORE_OFFLINE_RELEASE_NOTES_CAPABILITIES"
    RESTORE_OFFLINE_RELEASE_NOTES_NON_GOALS = "RESTORE_OFFLINE_RELEASE_NOTES_NON_GOALS"
    RESTORE_OFFLINE_RELEASE_NOTES_TESTING_EVIDENCE = "RESTORE_OFFLINE_RELEASE_NOTES_TESTING_EVIDENCE"
    RESTORE_OFFLINE_RELEASE_NOTES_LIMITATIONS = "RESTORE_OFFLINE_RELEASE_NOTES_LIMITATIONS"
    RESTORE_OFFLINE_RELEASE_NOTES_SAFETY_LANGUAGE = "RESTORE_OFFLINE_RELEASE_NOTES_SAFETY_LANGUAGE"
    REMOVE_LIVE_TRADING_READINESS_CLAIM = "REMOVE_LIVE_TRADING_READINESS_CLAIM"
    REMOVE_REAL_BROKER_READINESS_CLAIM = "REMOVE_REAL_BROKER_READINESS_CLAIM"
    REMOVE_REAL_ORDER_EXECUTION_CLAIM = "REMOVE_REAL_ORDER_EXECUTION_CLAIM"
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
    PREPARE_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO = "PREPARE_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO"


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleaseNotesScore:
    overall_score: int
    input_score: int
    capability_score: int
    non_goal_score: int
    testing_score: int
    limitation_score: int
    safety_language_score: int
    overclaim_score: int
    boundary_score: int


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleaseNotesContext:
    title: str
    status: str
    decision: str
    next_step: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleaseNotesCapability:
    name: str
    included: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleaseNotesNonGoal:
    text: str
    explicit: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleaseNotesTestingEvidence:
    label: str
    result: str
    passed: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleaseNotesKnownLimitation:
    text: str
    documented: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleaseNotesUsageGuidance:
    text: str
    explicit: bool = True


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleaseNotesReport:
    markdown: str
    json: str


@dataclass(frozen=True)
class AGIcoreTradingV1OfflineReleaseNotesInput:
    offline_release_decision_input: AGIcoreTradingV1OfflineReleaseDecisionInput | None = field(default_factory=AGIcoreTradingV1OfflineReleaseDecisionInput)
    offline_release_decision_result: AGIcoreTradingV1OfflineReleaseDecisionResult | None = None
    force_capabilities_missing: bool = False
    force_non_goals_missing: bool = False
    force_testing_evidence_missing: bool = False
    force_limitations_missing: bool = False
    force_safety_language_missing: bool = False
    force_live_trading_overclaim: bool = False
    force_real_broker_overclaim: bool = False
    force_real_order_overclaim: bool = False
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
class AGIcoreTradingV1OfflineReleaseNotesResult:
    state: AGIcoreTradingV1OfflineReleaseNotesState
    decision: AGIcoreTradingV1OfflineReleaseNotesDecision
    score: AGIcoreTradingV1OfflineReleaseNotesScore
    risks: tuple[AGIcoreTradingV1OfflineReleaseNotesRisk, ...]
    recommendations: tuple[AGIcoreTradingV1OfflineReleaseNotesRecommendation, ...]
    context: AGIcoreTradingV1OfflineReleaseNotesContext | None = None
    capabilities: tuple[AGIcoreTradingV1OfflineReleaseNotesCapability, ...] = ()
    non_goals: tuple[AGIcoreTradingV1OfflineReleaseNotesNonGoal, ...] = ()
    testing_evidence: tuple[AGIcoreTradingV1OfflineReleaseNotesTestingEvidence, ...] = ()
    known_limitations: tuple[AGIcoreTradingV1OfflineReleaseNotesKnownLimitation, ...] = ()
    usage_guidance: tuple[AGIcoreTradingV1OfflineReleaseNotesUsageGuidance, ...] = ()
    report: AGIcoreTradingV1OfflineReleaseNotesReport | None = None
    offline_release_decision_result: Any = None
    file_read: bool = False
    data_accessed: bool = False
    real_order_submitted: bool = False
    real_account_accessed: bool = False
    position_mutated: bool = False
    next_phase: str = "AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO"
