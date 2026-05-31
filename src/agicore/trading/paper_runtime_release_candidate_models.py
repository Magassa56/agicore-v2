"""Models for offline AGIcore Paper Runtime Release Candidate preparation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperRuntimeReleaseCandidateState(StrEnum):
    NOT_READY = "NOT_READY"
    RC_REVIEW_REQUIRED = "RC_REVIEW_REQUIRED"
    PARTIALLY_READY = "PARTIALLY_READY"
    RELEASE_CANDIDATE_READY = "RELEASE_CANDIDATE_READY"
    READY_FOR_PAPER_RUNTIME_VALIDATION = "READY_FOR_PAPER_RUNTIME_VALIDATION"


class PaperRuntimeReleaseCandidateDecision(StrEnum):
    BLOCK_RELEASE_CANDIDATE = "BLOCK_RELEASE_CANDIDATE"
    REQUIRE_RUNTIME_FREEZE = "REQUIRE_RUNTIME_FREEZE"
    REQUIRE_TEST_COVERAGE_FIXES = "REQUIRE_TEST_COVERAGE_FIXES"
    REQUIRE_STABILITY_EVIDENCE = "REQUIRE_STABILITY_EVIDENCE"
    REQUIRE_DOCUMENTATION_FIXES = "REQUIRE_DOCUMENTATION_FIXES"
    APPROVE_PAPER_RUNTIME_RELEASE_CANDIDATE = "APPROVE_PAPER_RUNTIME_RELEASE_CANDIDATE"


class PaperRuntimeReleaseCandidateRisk(StrEnum):
    RC_SCOPE_UNCLEAR = "RC_SCOPE_UNCLEAR"
    RUNTIME_NOT_FROZEN = "RUNTIME_NOT_FROZEN"
    TEST_COVERAGE_GAP = "TEST_COVERAGE_GAP"
    STABILITY_EVIDENCE_INCOMPLETE = "STABILITY_EVIDENCE_INCOMPLETE"
    DOCUMENTATION_GAP = "DOCUMENTATION_GAP"
    OPERATIONAL_BOUNDARY_GAP = "OPERATIONAL_BOUNDARY_GAP"
    SAFETY_GUARD_GAP = "SAFETY_GUARD_GAP"
    OBSERVABILITY_READINESS_GAP = "OBSERVABILITY_READINESS_GAP"
    ROLLBACK_READINESS_GAP = "ROLLBACK_READINESS_GAP"
    KILL_SWITCH_READINESS_GAP = "KILL_SWITCH_READINESS_GAP"
    HUMAN_SUPERVISION_READINESS_GAP = "HUMAN_SUPERVISION_READINESS_GAP"
    PREMATURE_RC_APPROVAL = "PREMATURE_RC_APPROVAL"


class PaperRuntimeReleaseCandidateRecommendation(StrEnum):
    HOLD_RELEASE_CANDIDATE = "HOLD_RELEASE_CANDIDATE"
    CLARIFY_RELEASE_CANDIDATE_SCOPE = "CLARIFY_RELEASE_CANDIDATE_SCOPE"
    FREEZE_RUNTIME_SURFACE = "FREEZE_RUNTIME_SURFACE"
    REPAIR_TEST_COVERAGE = "REPAIR_TEST_COVERAGE"
    COMPLETE_STABILITY_EVIDENCE = "COMPLETE_STABILITY_EVIDENCE"
    COMPLETE_RUNTIME_DOCUMENTATION = "COMPLETE_RUNTIME_DOCUMENTATION"
    REINFORCE_OPERATIONAL_BOUNDARIES = "REINFORCE_OPERATIONAL_BOUNDARIES"
    REINFORCE_SAFETY_GUARDS = "REINFORCE_SAFETY_GUARDS"
    REPAIR_OBSERVABILITY_READINESS = "REPAIR_OBSERVABILITY_READINESS"
    REPAIR_ROLLBACK_READINESS = "REPAIR_ROLLBACK_READINESS"
    REPAIR_KILL_SWITCH_READINESS = "REPAIR_KILL_SWITCH_READINESS"
    REPAIR_HUMAN_SUPERVISION_READINESS = "REPAIR_HUMAN_SUPERVISION_READINESS"
    DELAY_RC_APPROVAL = "DELAY_RC_APPROVAL"
    RUN_RELEASE_CANDIDATE_REVIEW_SUITE = "RUN_RELEASE_CANDIDATE_REVIEW_SUITE"
    APPROVE_FOR_PAPER_RUNTIME_VALIDATION = "APPROVE_FOR_PAPER_RUNTIME_VALIDATION"


@dataclass(frozen=True)
class PaperRuntimeReleaseCandidateInput:
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
    rc_scope_defined: bool | None = None
    runtime_frozen: bool | None = None
    test_coverage_ready: bool | None = None
    stability_evidence_complete: bool | None = None
    documentation_ready: bool | None = None
    operational_boundaries_enforced: bool | None = None
    safety_guards_ready: bool | None = None
    observability_ready: bool | None = None
    rollback_ready: bool | None = None
    kill_switch_ready: bool | None = None
    human_supervision_ready: bool | None = None
    rc_approval_requested: bool | None = None
    offline_mode_enforced: bool | None = None
    sandbox_mode_enforced: bool | None = None
    no_real_broker: bool | None = None
    no_api_key_read: bool | None = None
    no_http_transport: bool | None = None
    no_websocket_transport: bool | None = None
    no_socket_transport: bool | None = None
    no_external_api: bool | None = None
    no_real_order: bool | None = None
    release_candidate_scope_score: int | None = None
    runtime_freeze_score: int | None = None
    runtime_test_coverage_score: int | None = None
    runtime_stability_evidence_score: int | None = None
    runtime_documentation_score: int | None = None
    runtime_operational_boundaries_score: int | None = None
    runtime_safety_guards_score: int | None = None
    runtime_observability_score: int | None = None
    runtime_rollback_score: int | None = None
    runtime_kill_switch_score: int | None = None
    runtime_human_supervision_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperRuntimeReleaseCandidateReview:
    name: str
    score: int
    passed: bool
    risks: tuple[PaperRuntimeReleaseCandidateRisk, ...] = ()
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperRuntimeReleaseCandidateScore:
    overall_score: int
    release_candidate_scope_score: int
    runtime_freeze_score: int
    runtime_test_coverage_score: int
    runtime_stability_evidence_score: int
    runtime_documentation_score: int
    runtime_operational_boundaries_score: int
    runtime_safety_guards_score: int
    runtime_observability_score: int
    runtime_rollback_score: int
    runtime_kill_switch_score: int
    runtime_human_supervision_score: int


@dataclass(frozen=True)
class PaperRuntimeReleaseCandidateResult:
    state: PaperRuntimeReleaseCandidateState
    decision: PaperRuntimeReleaseCandidateDecision
    release_candidate_score: int
    score_breakdown: PaperRuntimeReleaseCandidateScore
    risks: tuple[PaperRuntimeReleaseCandidateRisk, ...] = ()
    release_candidate_scope: PaperRuntimeReleaseCandidateReview = field(default_factory=lambda: PaperRuntimeReleaseCandidateReview("release_candidate_scope", 0, False))
    runtime_freeze_status: PaperRuntimeReleaseCandidateReview = field(default_factory=lambda: PaperRuntimeReleaseCandidateReview("runtime_freeze_status", 0, False))
    runtime_test_coverage: PaperRuntimeReleaseCandidateReview = field(default_factory=lambda: PaperRuntimeReleaseCandidateReview("runtime_test_coverage", 0, False))
    runtime_stability_evidence: PaperRuntimeReleaseCandidateReview = field(default_factory=lambda: PaperRuntimeReleaseCandidateReview("runtime_stability_evidence", 0, False))
    runtime_documentation_readiness: PaperRuntimeReleaseCandidateReview = field(default_factory=lambda: PaperRuntimeReleaseCandidateReview("runtime_documentation_readiness", 0, False))
    runtime_operational_boundaries: PaperRuntimeReleaseCandidateReview = field(default_factory=lambda: PaperRuntimeReleaseCandidateReview("runtime_operational_boundaries", 0, False))
    runtime_safety_guards: PaperRuntimeReleaseCandidateReview = field(default_factory=lambda: PaperRuntimeReleaseCandidateReview("runtime_safety_guards", 0, False))
    runtime_observability_readiness: PaperRuntimeReleaseCandidateReview = field(default_factory=lambda: PaperRuntimeReleaseCandidateReview("runtime_observability_readiness", 0, False))
    runtime_rollback_readiness: PaperRuntimeReleaseCandidateReview = field(default_factory=lambda: PaperRuntimeReleaseCandidateReview("runtime_rollback_readiness", 0, False))
    runtime_kill_switch_readiness: PaperRuntimeReleaseCandidateReview = field(default_factory=lambda: PaperRuntimeReleaseCandidateReview("runtime_kill_switch_readiness", 0, False))
    runtime_human_supervision_readiness: PaperRuntimeReleaseCandidateReview = field(default_factory=lambda: PaperRuntimeReleaseCandidateReview("runtime_human_supervision_readiness", 0, False))
    recommendations: tuple[PaperRuntimeReleaseCandidateRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
