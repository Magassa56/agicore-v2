"""Models for offline AGIcore Paper Runtime Validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperRuntimeValidationState(StrEnum):
    NOT_VALIDATED = "NOT_VALIDATED"
    VALIDATION_REVIEW_REQUIRED = "VALIDATION_REVIEW_REQUIRED"
    PARTIALLY_VALIDATED = "PARTIALLY_VALIDATED"
    VALIDATED = "VALIDATED"
    READY_FOR_OFFICIAL_PAPER_VALIDATION_REPORT = "READY_FOR_OFFICIAL_PAPER_VALIDATION_REPORT"


class PaperRuntimeValidationDecision(StrEnum):
    BLOCK_VALIDATION = "BLOCK_VALIDATION"
    REQUIRE_RELEASE_CANDIDATE_FIXES = "REQUIRE_RELEASE_CANDIDATE_FIXES"
    REQUIRE_EXECUTION_EVIDENCE = "REQUIRE_EXECUTION_EVIDENCE"
    REQUIRE_TEST_EVIDENCE = "REQUIRE_TEST_EVIDENCE"
    REQUIRE_SAFETY_EVIDENCE = "REQUIRE_SAFETY_EVIDENCE"
    APPROVE_PAPER_RUNTIME_VALIDATION = "APPROVE_PAPER_RUNTIME_VALIDATION"


class PaperRuntimeValidationRisk(StrEnum):
    RELEASE_CANDIDATE_NOT_READY = "RELEASE_CANDIDATE_NOT_READY"
    RUNTIME_EXECUTION_EVIDENCE_GAP = "RUNTIME_EXECUTION_EVIDENCE_GAP"
    RUNTIME_TEST_EVIDENCE_GAP = "RUNTIME_TEST_EVIDENCE_GAP"
    EXTENDED_TEST_EVIDENCE_GAP = "EXTENDED_TEST_EVIDENCE_GAP"
    STABILIZATION_EVIDENCE_GAP = "STABILIZATION_EVIDENCE_GAP"
    SAFETY_EVIDENCE_GAP = "SAFETY_EVIDENCE_GAP"
    OBSERVABILITY_EVIDENCE_GAP = "OBSERVABILITY_EVIDENCE_GAP"
    ROLLBACK_EVIDENCE_GAP = "ROLLBACK_EVIDENCE_GAP"
    KILL_SWITCH_EVIDENCE_GAP = "KILL_SWITCH_EVIDENCE_GAP"
    HUMAN_SUPERVISION_EVIDENCE_GAP = "HUMAN_SUPERVISION_EVIDENCE_GAP"
    OPERATIONAL_BOUNDARY_VIOLATION = "OPERATIONAL_BOUNDARY_VIOLATION"
    PREMATURE_VALIDATION_APPROVAL = "PREMATURE_VALIDATION_APPROVAL"


class PaperRuntimeValidationRecommendation(StrEnum):
    HOLD_VALIDATION = "HOLD_VALIDATION"
    REPAIR_RELEASE_CANDIDATE_STATUS = "REPAIR_RELEASE_CANDIDATE_STATUS"
    COMPLETE_RUNTIME_EXECUTION_EVIDENCE = "COMPLETE_RUNTIME_EXECUTION_EVIDENCE"
    COMPLETE_RUNTIME_TEST_EVIDENCE = "COMPLETE_RUNTIME_TEST_EVIDENCE"
    COMPLETE_EXTENDED_TEST_EVIDENCE = "COMPLETE_EXTENDED_TEST_EVIDENCE"
    COMPLETE_STABILIZATION_EVIDENCE = "COMPLETE_STABILIZATION_EVIDENCE"
    COMPLETE_SAFETY_EVIDENCE = "COMPLETE_SAFETY_EVIDENCE"
    COMPLETE_OBSERVABILITY_EVIDENCE = "COMPLETE_OBSERVABILITY_EVIDENCE"
    COMPLETE_ROLLBACK_EVIDENCE = "COMPLETE_ROLLBACK_EVIDENCE"
    COMPLETE_KILL_SWITCH_EVIDENCE = "COMPLETE_KILL_SWITCH_EVIDENCE"
    COMPLETE_HUMAN_SUPERVISION_EVIDENCE = "COMPLETE_HUMAN_SUPERVISION_EVIDENCE"
    REINFORCE_OPERATIONAL_BOUNDARIES = "REINFORCE_OPERATIONAL_BOUNDARIES"
    DELAY_VALIDATION_APPROVAL = "DELAY_VALIDATION_APPROVAL"
    RUN_PAPER_RUNTIME_VALIDATION_SUITE = "RUN_PAPER_RUNTIME_VALIDATION_SUITE"
    APPROVE_OFFICIAL_PAPER_VALIDATION_REPORT = "APPROVE_OFFICIAL_PAPER_VALIDATION_REPORT"


@dataclass(frozen=True)
class PaperRuntimeValidationInput:
    paper_runtime_release_candidate: Any = None
    paper_runtime_stabilization_review: Any = None
    extended_paper_runtime_test: Any = None
    paper_runtime_test_run: Any = None
    paper_trading_runtime: Any = None
    paper_runtime_integration_review: Any = None
    paper_trading_runtime_design: Any = None
    paper_runtime_decision_review: Any = None
    full_paper_session: Any = None
    observability_verification: Any = None
    rollback_verification: Any = None
    kill_switch_verification: Any = None
    human_validated_paper_session: Any = None
    supervised_paper_session: Any = None
    release_candidate_ready: bool | None = None
    runtime_execution_evidence_ready: bool | None = None
    runtime_test_evidence_ready: bool | None = None
    extended_test_evidence_ready: bool | None = None
    stabilization_evidence_ready: bool | None = None
    safety_evidence_ready: bool | None = None
    observability_evidence_ready: bool | None = None
    rollback_evidence_ready: bool | None = None
    kill_switch_evidence_ready: bool | None = None
    human_supervision_evidence_ready: bool | None = None
    operational_boundaries_validated: bool | None = None
    validation_approval_requested: bool | None = None
    offline_mode_enforced: bool | None = None
    sandbox_mode_enforced: bool | None = None
    no_real_broker: bool | None = None
    no_api_key_read: bool | None = None
    no_http_transport: bool | None = None
    no_websocket_transport: bool | None = None
    no_socket_transport: bool | None = None
    no_external_api: bool | None = None
    no_real_order: bool | None = None
    release_candidate_status_score: int | None = None
    runtime_execution_evidence_score: int | None = None
    runtime_test_evidence_score: int | None = None
    extended_test_evidence_score: int | None = None
    stabilization_evidence_score: int | None = None
    safety_evidence_score: int | None = None
    observability_evidence_score: int | None = None
    rollback_evidence_score: int | None = None
    kill_switch_evidence_score: int | None = None
    human_supervision_evidence_score: int | None = None
    operational_boundaries_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperRuntimeValidationReview:
    name: str
    score: int
    passed: bool
    risks: tuple[PaperRuntimeValidationRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperRuntimeValidationScore:
    overall_score: int
    release_candidate_status_score: int
    runtime_execution_evidence_score: int
    runtime_test_evidence_score: int
    extended_test_evidence_score: int
    stabilization_evidence_score: int
    safety_evidence_score: int
    observability_evidence_score: int
    rollback_evidence_score: int
    kill_switch_evidence_score: int
    human_supervision_evidence_score: int
    operational_boundaries_score: int


@dataclass(frozen=True)
class PaperRuntimeValidationResult:
    state: PaperRuntimeValidationState
    decision: PaperRuntimeValidationDecision
    validation_score: int
    score_breakdown: PaperRuntimeValidationScore
    risks: tuple[PaperRuntimeValidationRisk, ...] = ()
    release_candidate_status: PaperRuntimeValidationReview = field(default_factory=lambda: PaperRuntimeValidationReview("release_candidate_status", 0, False))
    runtime_execution_evidence: PaperRuntimeValidationReview = field(default_factory=lambda: PaperRuntimeValidationReview("runtime_execution_evidence", 0, False))
    runtime_test_evidence: PaperRuntimeValidationReview = field(default_factory=lambda: PaperRuntimeValidationReview("runtime_test_evidence", 0, False))
    extended_test_evidence: PaperRuntimeValidationReview = field(default_factory=lambda: PaperRuntimeValidationReview("extended_test_evidence", 0, False))
    stabilization_evidence: PaperRuntimeValidationReview = field(default_factory=lambda: PaperRuntimeValidationReview("stabilization_evidence", 0, False))
    safety_evidence: PaperRuntimeValidationReview = field(default_factory=lambda: PaperRuntimeValidationReview("safety_evidence", 0, False))
    observability_evidence: PaperRuntimeValidationReview = field(default_factory=lambda: PaperRuntimeValidationReview("observability_evidence", 0, False))
    rollback_evidence: PaperRuntimeValidationReview = field(default_factory=lambda: PaperRuntimeValidationReview("rollback_evidence", 0, False))
    kill_switch_evidence: PaperRuntimeValidationReview = field(default_factory=lambda: PaperRuntimeValidationReview("kill_switch_evidence", 0, False))
    human_supervision_evidence: PaperRuntimeValidationReview = field(default_factory=lambda: PaperRuntimeValidationReview("human_supervision_evidence", 0, False))
    operational_boundaries: PaperRuntimeValidationReview = field(default_factory=lambda: PaperRuntimeValidationReview("operational_boundaries", 0, False))
    recommendations: tuple[PaperRuntimeValidationRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
