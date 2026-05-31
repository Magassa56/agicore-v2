"""Models for the offline AGIcore Official Paper Validation Report."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class OfficialPaperValidationReportState(StrEnum):
    REPORT_NOT_READY = "REPORT_NOT_READY"
    REPORT_REVIEW_REQUIRED = "REPORT_REVIEW_REQUIRED"
    REPORT_PARTIALLY_READY = "REPORT_PARTIALLY_READY"
    REPORT_READY = "REPORT_READY"
    READY_FOR_SUPERVISED_PAPER_RUNTIME_TRIAL = "READY_FOR_SUPERVISED_PAPER_RUNTIME_TRIAL"


class OfficialPaperValidationReportDecision(StrEnum):
    BLOCK_SUPERVISED_TRIAL = "BLOCK_SUPERVISED_TRIAL"
    REQUIRE_REPORT_COMPLETION = "REQUIRE_REPORT_COMPLETION"
    REQUIRE_EVIDENCE_FIXES = "REQUIRE_EVIDENCE_FIXES"
    REQUIRE_BOUNDARY_FIXES = "REQUIRE_BOUNDARY_FIXES"
    APPROVE_SUPERVISED_PAPER_RUNTIME_TRIAL = "APPROVE_SUPERVISED_PAPER_RUNTIME_TRIAL"


class OfficialPaperValidationReportRisk(StrEnum):
    RUNTIME_CREATION_EVIDENCE_MISSING = "RUNTIME_CREATION_EVIDENCE_MISSING"
    INTEGRATION_EVIDENCE_MISSING = "INTEGRATION_EVIDENCE_MISSING"
    TEST_RUN_EVIDENCE_MISSING = "TEST_RUN_EVIDENCE_MISSING"
    EXTENDED_TEST_EVIDENCE_MISSING = "EXTENDED_TEST_EVIDENCE_MISSING"
    STABILIZATION_EVIDENCE_MISSING = "STABILIZATION_EVIDENCE_MISSING"
    RELEASE_CANDIDATE_EVIDENCE_MISSING = "RELEASE_CANDIDATE_EVIDENCE_MISSING"
    VALIDATION_EVIDENCE_MISSING = "VALIDATION_EVIDENCE_MISSING"
    SAFETY_EVIDENCE_MISSING = "SAFETY_EVIDENCE_MISSING"
    OBSERVABILITY_EVIDENCE_MISSING = "OBSERVABILITY_EVIDENCE_MISSING"
    ROLLBACK_EVIDENCE_MISSING = "ROLLBACK_EVIDENCE_MISSING"
    KILL_SWITCH_EVIDENCE_MISSING = "KILL_SWITCH_EVIDENCE_MISSING"
    HUMAN_SUPERVISION_EVIDENCE_MISSING = "HUMAN_SUPERVISION_EVIDENCE_MISSING"
    OPERATIONAL_BOUNDARY_EVIDENCE_MISSING = "OPERATIONAL_BOUNDARY_EVIDENCE_MISSING"
    PREMATURE_SUPERVISED_TRIAL = "PREMATURE_SUPERVISED_TRIAL"


class OfficialPaperValidationReportRecommendation(StrEnum):
    HOLD_SUPERVISED_TRIAL = "HOLD_SUPERVISED_TRIAL"
    COMPLETE_RUNTIME_CREATION_EVIDENCE = "COMPLETE_RUNTIME_CREATION_EVIDENCE"
    COMPLETE_INTEGRATION_EVIDENCE = "COMPLETE_INTEGRATION_EVIDENCE"
    COMPLETE_TEST_RUN_EVIDENCE = "COMPLETE_TEST_RUN_EVIDENCE"
    COMPLETE_EXTENDED_TEST_EVIDENCE = "COMPLETE_EXTENDED_TEST_EVIDENCE"
    COMPLETE_STABILIZATION_EVIDENCE = "COMPLETE_STABILIZATION_EVIDENCE"
    COMPLETE_RELEASE_CANDIDATE_EVIDENCE = "COMPLETE_RELEASE_CANDIDATE_EVIDENCE"
    COMPLETE_VALIDATION_EVIDENCE = "COMPLETE_VALIDATION_EVIDENCE"
    COMPLETE_SAFETY_EVIDENCE = "COMPLETE_SAFETY_EVIDENCE"
    COMPLETE_OBSERVABILITY_EVIDENCE = "COMPLETE_OBSERVABILITY_EVIDENCE"
    COMPLETE_ROLLBACK_EVIDENCE = "COMPLETE_ROLLBACK_EVIDENCE"
    COMPLETE_KILL_SWITCH_EVIDENCE = "COMPLETE_KILL_SWITCH_EVIDENCE"
    COMPLETE_HUMAN_SUPERVISION_EVIDENCE = "COMPLETE_HUMAN_SUPERVISION_EVIDENCE"
    REINFORCE_OPERATIONAL_BOUNDARIES = "REINFORCE_OPERATIONAL_BOUNDARIES"
    DELAY_SUPERVISED_TRIAL = "DELAY_SUPERVISED_TRIAL"
    RUN_OFFICIAL_REPORT_REVIEW_SUITE = "RUN_OFFICIAL_REPORT_REVIEW_SUITE"
    APPROVE_SUPERVISED_PAPER_RUNTIME_TRIAL = "APPROVE_SUPERVISED_PAPER_RUNTIME_TRIAL"


@dataclass(frozen=True)
class OfficialPaperValidationReportInput:
    paper_runtime_validation: Any = None
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
    runtime_creation_evidence_ready: bool | None = None
    integration_review_evidence_ready: bool | None = None
    test_run_evidence_ready: bool | None = None
    extended_test_evidence_ready: bool | None = None
    stabilization_evidence_ready: bool | None = None
    release_candidate_evidence_ready: bool | None = None
    runtime_validation_evidence_ready: bool | None = None
    safety_evidence_ready: bool | None = None
    observability_evidence_ready: bool | None = None
    rollback_evidence_ready: bool | None = None
    kill_switch_evidence_ready: bool | None = None
    human_supervision_evidence_ready: bool | None = None
    operational_boundary_evidence_ready: bool | None = None
    supervised_trial_requested: bool | None = None
    offline_mode_enforced: bool | None = None
    sandbox_mode_enforced: bool | None = None
    no_real_broker: bool | None = None
    no_api_key_read: bool | None = None
    no_http_transport: bool | None = None
    no_websocket_transport: bool | None = None
    no_socket_transport: bool | None = None
    no_external_api: bool | None = None
    no_real_order: bool | None = None
    runtime_creation_evidence_score: int | None = None
    integration_review_evidence_score: int | None = None
    test_run_evidence_score: int | None = None
    extended_test_evidence_score: int | None = None
    stabilization_evidence_score: int | None = None
    release_candidate_evidence_score: int | None = None
    runtime_validation_evidence_score: int | None = None
    safety_evidence_score: int | None = None
    observability_evidence_score: int | None = None
    rollback_evidence_score: int | None = None
    kill_switch_evidence_score: int | None = None
    human_supervision_evidence_score: int | None = None
    operational_boundary_evidence_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class OfficialPaperValidationEvidence:
    name: str
    score: int
    present: bool
    risks: tuple[OfficialPaperValidationReportRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class OfficialPaperValidationReportScore:
    overall_score: int
    runtime_creation_evidence_score: int
    integration_review_evidence_score: int
    test_run_evidence_score: int
    extended_test_evidence_score: int
    stabilization_evidence_score: int
    release_candidate_evidence_score: int
    runtime_validation_evidence_score: int
    safety_evidence_score: int
    observability_evidence_score: int
    rollback_evidence_score: int
    kill_switch_evidence_score: int
    human_supervision_evidence_score: int
    operational_boundary_evidence_score: int


@dataclass(frozen=True)
class OfficialPaperValidationReportResult:
    state: OfficialPaperValidationReportState
    decision: OfficialPaperValidationReportDecision
    report_score: int
    score_breakdown: OfficialPaperValidationReportScore
    risks: tuple[OfficialPaperValidationReportRisk, ...] = ()
    runtime_creation_evidence: OfficialPaperValidationEvidence = field(default_factory=lambda: OfficialPaperValidationEvidence("runtime_creation_evidence", 0, False))
    integration_review_evidence: OfficialPaperValidationEvidence = field(default_factory=lambda: OfficialPaperValidationEvidence("integration_review_evidence", 0, False))
    test_run_evidence: OfficialPaperValidationEvidence = field(default_factory=lambda: OfficialPaperValidationEvidence("test_run_evidence", 0, False))
    extended_test_evidence: OfficialPaperValidationEvidence = field(default_factory=lambda: OfficialPaperValidationEvidence("extended_test_evidence", 0, False))
    stabilization_evidence: OfficialPaperValidationEvidence = field(default_factory=lambda: OfficialPaperValidationEvidence("stabilization_evidence", 0, False))
    release_candidate_evidence: OfficialPaperValidationEvidence = field(default_factory=lambda: OfficialPaperValidationEvidence("release_candidate_evidence", 0, False))
    runtime_validation_evidence: OfficialPaperValidationEvidence = field(default_factory=lambda: OfficialPaperValidationEvidence("runtime_validation_evidence", 0, False))
    safety_evidence: OfficialPaperValidationEvidence = field(default_factory=lambda: OfficialPaperValidationEvidence("safety_evidence", 0, False))
    observability_evidence: OfficialPaperValidationEvidence = field(default_factory=lambda: OfficialPaperValidationEvidence("observability_evidence", 0, False))
    rollback_evidence: OfficialPaperValidationEvidence = field(default_factory=lambda: OfficialPaperValidationEvidence("rollback_evidence", 0, False))
    kill_switch_evidence: OfficialPaperValidationEvidence = field(default_factory=lambda: OfficialPaperValidationEvidence("kill_switch_evidence", 0, False))
    human_supervision_evidence: OfficialPaperValidationEvidence = field(default_factory=lambda: OfficialPaperValidationEvidence("human_supervision_evidence", 0, False))
    operational_boundary_evidence: OfficialPaperValidationEvidence = field(default_factory=lambda: OfficialPaperValidationEvidence("operational_boundary_evidence", 0, False))
    recommendations: tuple[OfficialPaperValidationReportRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
