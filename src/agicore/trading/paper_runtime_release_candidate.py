"""Offline release candidate preparation for the AGIcore Paper Trading Runtime."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_runtime_release_candidate_models import (
    PaperRuntimeReleaseCandidateDecision,
    PaperRuntimeReleaseCandidateInput,
    PaperRuntimeReleaseCandidateRecommendation,
    PaperRuntimeReleaseCandidateResult,
    PaperRuntimeReleaseCandidateReview,
    PaperRuntimeReleaseCandidateRisk,
    PaperRuntimeReleaseCandidateScore,
    PaperRuntimeReleaseCandidateState,
)


def _coerce_input(data: PaperRuntimeReleaseCandidateInput | Mapping[str, Any]) -> PaperRuntimeReleaseCandidateInput:
    if isinstance(data, PaperRuntimeReleaseCandidateInput):
        return data
    return PaperRuntimeReleaseCandidateInput(**dict(data))


def _value(item: Any) -> str:
    if item is None:
        return ""
    if isinstance(item, Enum):
        return str(item.value)
    return str(item)


def _get(obj: Any, name: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, Mapping):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _as_tuple(items: Any) -> tuple[Any, ...]:
    if items is None:
        return ()
    if isinstance(items, tuple):
        return items
    if isinstance(items, list):
        return tuple(items)
    if isinstance(items, set):
        return tuple(items)
    return (items,)


def _contains(items: Any, *needles: str) -> bool:
    text_items = tuple(_value(item).upper() for item in _as_tuple(items))
    return any(any(needle.upper() in item for item in text_items) for needle in needles)


def _clamp(value: int | float, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(round(value))))


def _bool_score(value: bool | None, unknown: int = 45) -> int:
    if value is True:
        return 100
    if value is False:
        return 0
    return unknown


def _average(values: Iterable[int | float | None], default: int = 0) -> int:
    usable = [float(value) for value in values if value is not None]
    if not usable:
        return default
    return _clamp(sum(usable) / len(usable))


def _dedupe(items: Iterable[Any]) -> tuple[Any, ...]:
    seen: set[Any] = set()
    result: list[Any] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return tuple(result)


def _upstream_items(data: PaperRuntimeReleaseCandidateInput) -> tuple[Any, ...]:
    return (
        data.paper_runtime_stabilization_review,
        data.extended_paper_runtime_test,
        data.paper_runtime_test_run,
        data.paper_trading_runtime,
        data.paper_runtime_integration_review,
        data.paper_trading_runtime_design,
        data.paper_runtime_decision_review,
        data.full_paper_session,
        data.observability_verification,
        data.rollback_verification,
        data.kill_switch_verification,
        data.human_validated_paper_session,
        data.supervised_paper_session,
    )


def _upstream_risks(data: PaperRuntimeReleaseCandidateInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperRuntimeReleaseCandidateInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _review(
    name: str,
    score: int,
    risk: PaperRuntimeReleaseCandidateRisk,
    failed: bool,
    details: tuple[str, ...] = (),
) -> PaperRuntimeReleaseCandidateReview:
    risks = (risk,) if failed or score < 85 else ()
    return PaperRuntimeReleaseCandidateReview(name, _clamp(score), not risks and score >= 85, risks, details)


def review_release_candidate_scope(data: PaperRuntimeReleaseCandidateInput | Mapping[str, Any]) -> PaperRuntimeReleaseCandidateReview:
    data = _coerce_input(data)
    design = data.paper_trading_runtime_design
    decision = data.paper_runtime_decision_review
    failed = (
        data.rc_scope_defined is not True
        or not _state_contains(design, "READY_FOR_RUNTIME_IMPLEMENTATION", "RUNTIME_DESIGN_READY")
        or not _state_contains(decision, "READY_FOR_PAPER_TRADING_RUNTIME", "APPROVE_PAPER_TRADING_RUNTIME_CREATION")
        or _has_upstream_risk(data, "SCOPE_UNCLEAR", "SCOPE_DRIFT")
    )
    score = data.release_candidate_scope_score if data.release_candidate_scope_score is not None else _bool_score(data.rc_scope_defined)
    details = (_value(_get(design, "state")), _value(_get(decision, "state")))
    return _review("release_candidate_scope", score, PaperRuntimeReleaseCandidateRisk.RC_SCOPE_UNCLEAR, failed, details)


def review_runtime_freeze_status(data: PaperRuntimeReleaseCandidateInput | Mapping[str, Any]) -> PaperRuntimeReleaseCandidateReview:
    data = _coerce_input(data)
    failed = data.runtime_frozen is not True or _has_upstream_risk(data, "NOT_FROZEN", "RUNTIME_MUTATION", "DRIFT")
    score = data.runtime_freeze_score if data.runtime_freeze_score is not None else _bool_score(data.runtime_frozen)
    return _review("runtime_freeze_status", score, PaperRuntimeReleaseCandidateRisk.RUNTIME_NOT_FROZEN, failed)


def review_runtime_test_coverage(data: PaperRuntimeReleaseCandidateInput | Mapping[str, Any]) -> PaperRuntimeReleaseCandidateReview:
    data = _coerce_input(data)
    extended = data.extended_paper_runtime_test
    test_run = data.paper_runtime_test_run
    failed = (
        data.test_coverage_ready is not True
        or not _state_contains(extended, "READY_FOR_PAPER_RUNTIME_STABILIZATION_REVIEW", "EXTENDED_TEST_COMPLETED")
        or not _state_contains(test_run, "READY_FOR_EXTENDED_PAPER_RUNTIME_TEST", "TEST_RUN_COMPLETED")
        or _has_upstream_risk(data, "TEST_COVERAGE", "TEST_RUN", "EXTENDED_TEST_NOT_REPEATABLE")
    )
    upstream_score = _average((_get(extended, "extended_runtime_score", None), _get(test_run, "test_run_score", None)), default=100)
    score = data.runtime_test_coverage_score if data.runtime_test_coverage_score is not None else _average((_bool_score(data.test_coverage_ready), upstream_score))
    return _review("runtime_test_coverage", score, PaperRuntimeReleaseCandidateRisk.TEST_COVERAGE_GAP, failed)


def review_runtime_stability_evidence(data: PaperRuntimeReleaseCandidateInput | Mapping[str, Any]) -> PaperRuntimeReleaseCandidateReview:
    data = _coerce_input(data)
    stabilization = data.paper_runtime_stabilization_review
    failed = (
        data.stability_evidence_complete is not True
        or not _state_contains(stabilization, "READY_FOR_PAPER_RUNTIME_RELEASE_CANDIDATE", "APPROVE_RELEASE_CANDIDATE_PREPARATION")
        or _has_upstream_risk(data, "STABILITY", "INCONSISTENCY", "STATE_DRIFT")
    )
    upstream_score = int(_get(stabilization, "stabilization_score", 45) or 45)
    score = data.runtime_stability_evidence_score if data.runtime_stability_evidence_score is not None else _average((_bool_score(data.stability_evidence_complete), upstream_score))
    return _review("runtime_stability_evidence", score, PaperRuntimeReleaseCandidateRisk.STABILITY_EVIDENCE_INCOMPLETE, failed, (_value(_get(stabilization, "state")),))


def review_runtime_documentation_readiness(data: PaperRuntimeReleaseCandidateInput | Mapping[str, Any]) -> PaperRuntimeReleaseCandidateReview:
    data = _coerce_input(data)
    failed = data.documentation_ready is not True or _has_upstream_risk(data, "DOCUMENTATION")
    score = data.runtime_documentation_score if data.runtime_documentation_score is not None else _bool_score(data.documentation_ready)
    return _review("runtime_documentation_readiness", score, PaperRuntimeReleaseCandidateRisk.DOCUMENTATION_GAP, failed)


def review_runtime_operational_boundaries(data: PaperRuntimeReleaseCandidateInput | Mapping[str, Any]) -> PaperRuntimeReleaseCandidateReview:
    data = _coerce_input(data)
    failed = data.operational_boundaries_enforced is not True or not _offline_boundary(data) or _has_upstream_risk(data, "BOUNDARY", "LIVE_EXECUTION", "NETWORK_LEAK")
    score = data.runtime_operational_boundaries_score if data.runtime_operational_boundaries_score is not None else _bool_score(data.operational_boundaries_enforced)
    return _review("runtime_operational_boundaries", score, PaperRuntimeReleaseCandidateRisk.OPERATIONAL_BOUNDARY_GAP, failed)


def review_runtime_safety_guards(data: PaperRuntimeReleaseCandidateInput | Mapping[str, Any]) -> PaperRuntimeReleaseCandidateReview:
    data = _coerce_input(data)
    failed = data.safety_guards_ready is not True or _has_upstream_risk(data, "SAFETY", "BYPASS")
    score = data.runtime_safety_guards_score if data.runtime_safety_guards_score is not None else _bool_score(data.safety_guards_ready)
    return _review("runtime_safety_guards", score, PaperRuntimeReleaseCandidateRisk.SAFETY_GUARD_GAP, failed)


def review_runtime_observability_readiness(data: PaperRuntimeReleaseCandidateInput | Mapping[str, Any]) -> PaperRuntimeReleaseCandidateReview:
    data = _coerce_input(data)
    failed = data.observability_ready is not True or _has_upstream_risk(data, "OBSERVABILITY")
    score = data.runtime_observability_score if data.runtime_observability_score is not None else _bool_score(data.observability_ready)
    return _review("runtime_observability_readiness", score, PaperRuntimeReleaseCandidateRisk.OBSERVABILITY_READINESS_GAP, failed)


def review_runtime_rollback_readiness(data: PaperRuntimeReleaseCandidateInput | Mapping[str, Any]) -> PaperRuntimeReleaseCandidateReview:
    data = _coerce_input(data)
    failed = data.rollback_ready is not True or _has_upstream_risk(data, "ROLLBACK")
    score = data.runtime_rollback_score if data.runtime_rollback_score is not None else _bool_score(data.rollback_ready)
    return _review("runtime_rollback_readiness", score, PaperRuntimeReleaseCandidateRisk.ROLLBACK_READINESS_GAP, failed)


def review_runtime_kill_switch_readiness(data: PaperRuntimeReleaseCandidateInput | Mapping[str, Any]) -> PaperRuntimeReleaseCandidateReview:
    data = _coerce_input(data)
    failed = data.kill_switch_ready is not True or _has_upstream_risk(data, "KILL_SWITCH")
    score = data.runtime_kill_switch_score if data.runtime_kill_switch_score is not None else _bool_score(data.kill_switch_ready)
    return _review("runtime_kill_switch_readiness", score, PaperRuntimeReleaseCandidateRisk.KILL_SWITCH_READINESS_GAP, failed)


def review_runtime_human_supervision_readiness(data: PaperRuntimeReleaseCandidateInput | Mapping[str, Any]) -> PaperRuntimeReleaseCandidateReview:
    data = _coerce_input(data)
    failed = data.human_supervision_ready is not True or _has_upstream_risk(data, "HUMAN", "SUPERVISION")
    score = data.runtime_human_supervision_score if data.runtime_human_supervision_score is not None else _bool_score(data.human_supervision_ready)
    return _review("runtime_human_supervision_readiness", score, PaperRuntimeReleaseCandidateRisk.HUMAN_SUPERVISION_READINESS_GAP, failed)


def _offline_boundary(data: PaperRuntimeReleaseCandidateInput) -> bool:
    return (
        data.offline_mode_enforced is True
        and data.sandbox_mode_enforced is True
        and data.no_real_broker is True
        and data.no_api_key_read is True
        and data.no_http_transport is True
        and data.no_websocket_transport is True
        and data.no_socket_transport is True
        and data.no_external_api is True
        and data.no_real_order is True
        and _get(data.paper_runtime_stabilization_review, "offline_only", True) is True
        and not _has_upstream_risk(data, "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK", "BROKER", "EXTERNAL_DEPENDENCY")
    )


def detect_release_candidate_risks(
    data: PaperRuntimeReleaseCandidateInput | Mapping[str, Any],
    *reviews: PaperRuntimeReleaseCandidateReview,
) -> tuple[PaperRuntimeReleaseCandidateRisk, ...]:
    data = _coerce_input(data)
    if not reviews:
        reviews = (
            review_release_candidate_scope(data),
            review_runtime_freeze_status(data),
            review_runtime_test_coverage(data),
            review_runtime_stability_evidence(data),
            review_runtime_documentation_readiness(data),
            review_runtime_operational_boundaries(data),
            review_runtime_safety_guards(data),
            review_runtime_observability_readiness(data),
            review_runtime_rollback_readiness(data),
            review_runtime_kill_switch_readiness(data),
            review_runtime_human_supervision_readiness(data),
        )
    risks: list[PaperRuntimeReleaseCandidateRisk] = []
    for review in reviews:
        risks.extend(review.risks)
    if data.rc_approval_requested is not True or not _offline_boundary(data):
        risks.append(PaperRuntimeReleaseCandidateRisk.PREMATURE_RC_APPROVAL)
    return _dedupe(risks)


def compute_release_candidate_score(
    data: PaperRuntimeReleaseCandidateInput | Mapping[str, Any],
    risks: tuple[PaperRuntimeReleaseCandidateRisk, ...] = (),
    *reviews: PaperRuntimeReleaseCandidateReview,
) -> PaperRuntimeReleaseCandidateScore:
    data = _coerce_input(data)
    if not reviews:
        reviews = (
            review_release_candidate_scope(data),
            review_runtime_freeze_status(data),
            review_runtime_test_coverage(data),
            review_runtime_stability_evidence(data),
            review_runtime_documentation_readiness(data),
            review_runtime_operational_boundaries(data),
            review_runtime_safety_guards(data),
            review_runtime_observability_readiness(data),
            review_runtime_rollback_readiness(data),
            review_runtime_kill_switch_readiness(data),
            review_runtime_human_supervision_readiness(data),
        )
    scores = tuple(review.score for review in reviews)
    overall = _clamp(_average(scores) - min(80, len(set(risks)) * 5))
    for risk, cap in {
        PaperRuntimeReleaseCandidateRisk.RC_SCOPE_UNCLEAR: 50,
        PaperRuntimeReleaseCandidateRisk.RUNTIME_NOT_FROZEN: 55,
        PaperRuntimeReleaseCandidateRisk.TEST_COVERAGE_GAP: 60,
        PaperRuntimeReleaseCandidateRisk.STABILITY_EVIDENCE_INCOMPLETE: 55,
        PaperRuntimeReleaseCandidateRisk.OPERATIONAL_BOUNDARY_GAP: 50,
        PaperRuntimeReleaseCandidateRisk.SAFETY_GUARD_GAP: 50,
        PaperRuntimeReleaseCandidateRisk.ROLLBACK_READINESS_GAP: 55,
        PaperRuntimeReleaseCandidateRisk.KILL_SWITCH_READINESS_GAP: 50,
        PaperRuntimeReleaseCandidateRisk.PREMATURE_RC_APPROVAL: 40,
    }.items():
        if risk in risks:
            overall = min(overall, cap)
    return PaperRuntimeReleaseCandidateScore(overall, *scores)


def _select_decision(risks: tuple[PaperRuntimeReleaseCandidateRisk, ...], score: int) -> PaperRuntimeReleaseCandidateDecision:
    if PaperRuntimeReleaseCandidateRisk.PREMATURE_RC_APPROVAL in risks or PaperRuntimeReleaseCandidateRisk.RC_SCOPE_UNCLEAR in risks or score < 45:
        return PaperRuntimeReleaseCandidateDecision.BLOCK_RELEASE_CANDIDATE
    if PaperRuntimeReleaseCandidateRisk.RUNTIME_NOT_FROZEN in risks:
        return PaperRuntimeReleaseCandidateDecision.REQUIRE_RUNTIME_FREEZE
    if PaperRuntimeReleaseCandidateRisk.TEST_COVERAGE_GAP in risks:
        return PaperRuntimeReleaseCandidateDecision.REQUIRE_TEST_COVERAGE_FIXES
    if PaperRuntimeReleaseCandidateRisk.STABILITY_EVIDENCE_INCOMPLETE in risks:
        return PaperRuntimeReleaseCandidateDecision.REQUIRE_STABILITY_EVIDENCE
    if PaperRuntimeReleaseCandidateRisk.DOCUMENTATION_GAP in risks:
        return PaperRuntimeReleaseCandidateDecision.REQUIRE_DOCUMENTATION_FIXES
    if risks:
        return PaperRuntimeReleaseCandidateDecision.BLOCK_RELEASE_CANDIDATE if score < 60 else PaperRuntimeReleaseCandidateDecision.REQUIRE_STABILITY_EVIDENCE
    return PaperRuntimeReleaseCandidateDecision.APPROVE_PAPER_RUNTIME_RELEASE_CANDIDATE


def _select_state(decision: PaperRuntimeReleaseCandidateDecision, score: int) -> PaperRuntimeReleaseCandidateState:
    if decision == PaperRuntimeReleaseCandidateDecision.BLOCK_RELEASE_CANDIDATE:
        return PaperRuntimeReleaseCandidateState.NOT_READY
    if decision in {
        PaperRuntimeReleaseCandidateDecision.REQUIRE_RUNTIME_FREEZE,
        PaperRuntimeReleaseCandidateDecision.REQUIRE_TEST_COVERAGE_FIXES,
        PaperRuntimeReleaseCandidateDecision.REQUIRE_STABILITY_EVIDENCE,
        PaperRuntimeReleaseCandidateDecision.REQUIRE_DOCUMENTATION_FIXES,
    }:
        return PaperRuntimeReleaseCandidateState.RC_REVIEW_REQUIRED if score < 82 else PaperRuntimeReleaseCandidateState.PARTIALLY_READY
    if score >= 95:
        return PaperRuntimeReleaseCandidateState.READY_FOR_PAPER_RUNTIME_VALIDATION
    return PaperRuntimeReleaseCandidateState.RELEASE_CANDIDATE_READY


def generate_release_candidate_recommendations(
    risks: tuple[PaperRuntimeReleaseCandidateRisk, ...],
    decision: PaperRuntimeReleaseCandidateDecision | None = None,
) -> tuple[PaperRuntimeReleaseCandidateRecommendation, ...]:
    recommendations: list[PaperRuntimeReleaseCandidateRecommendation] = []
    if risks:
        recommendations.append(PaperRuntimeReleaseCandidateRecommendation.HOLD_RELEASE_CANDIDATE)
    mapping = {
        PaperRuntimeReleaseCandidateRisk.RC_SCOPE_UNCLEAR: PaperRuntimeReleaseCandidateRecommendation.CLARIFY_RELEASE_CANDIDATE_SCOPE,
        PaperRuntimeReleaseCandidateRisk.RUNTIME_NOT_FROZEN: PaperRuntimeReleaseCandidateRecommendation.FREEZE_RUNTIME_SURFACE,
        PaperRuntimeReleaseCandidateRisk.TEST_COVERAGE_GAP: PaperRuntimeReleaseCandidateRecommendation.REPAIR_TEST_COVERAGE,
        PaperRuntimeReleaseCandidateRisk.STABILITY_EVIDENCE_INCOMPLETE: PaperRuntimeReleaseCandidateRecommendation.COMPLETE_STABILITY_EVIDENCE,
        PaperRuntimeReleaseCandidateRisk.DOCUMENTATION_GAP: PaperRuntimeReleaseCandidateRecommendation.COMPLETE_RUNTIME_DOCUMENTATION,
        PaperRuntimeReleaseCandidateRisk.OPERATIONAL_BOUNDARY_GAP: PaperRuntimeReleaseCandidateRecommendation.REINFORCE_OPERATIONAL_BOUNDARIES,
        PaperRuntimeReleaseCandidateRisk.SAFETY_GUARD_GAP: PaperRuntimeReleaseCandidateRecommendation.REINFORCE_SAFETY_GUARDS,
        PaperRuntimeReleaseCandidateRisk.OBSERVABILITY_READINESS_GAP: PaperRuntimeReleaseCandidateRecommendation.REPAIR_OBSERVABILITY_READINESS,
        PaperRuntimeReleaseCandidateRisk.ROLLBACK_READINESS_GAP: PaperRuntimeReleaseCandidateRecommendation.REPAIR_ROLLBACK_READINESS,
        PaperRuntimeReleaseCandidateRisk.KILL_SWITCH_READINESS_GAP: PaperRuntimeReleaseCandidateRecommendation.REPAIR_KILL_SWITCH_READINESS,
        PaperRuntimeReleaseCandidateRisk.HUMAN_SUPERVISION_READINESS_GAP: PaperRuntimeReleaseCandidateRecommendation.REPAIR_HUMAN_SUPERVISION_READINESS,
        PaperRuntimeReleaseCandidateRisk.PREMATURE_RC_APPROVAL: PaperRuntimeReleaseCandidateRecommendation.DELAY_RC_APPROVAL,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(PaperRuntimeReleaseCandidateRecommendation.RUN_RELEASE_CANDIDATE_REVIEW_SUITE)
    if decision == PaperRuntimeReleaseCandidateDecision.APPROVE_PAPER_RUNTIME_RELEASE_CANDIDATE:
        recommendations.append(PaperRuntimeReleaseCandidateRecommendation.APPROVE_FOR_PAPER_RUNTIME_VALIDATION)
    return _dedupe(recommendations)


def evaluate_paper_runtime_release_candidate(data: PaperRuntimeReleaseCandidateInput | Mapping[str, Any]) -> PaperRuntimeReleaseCandidateResult:
    data = _coerce_input(data)
    reviews = (
        review_release_candidate_scope(data),
        review_runtime_freeze_status(data),
        review_runtime_test_coverage(data),
        review_runtime_stability_evidence(data),
        review_runtime_documentation_readiness(data),
        review_runtime_operational_boundaries(data),
        review_runtime_safety_guards(data),
        review_runtime_observability_readiness(data),
        review_runtime_rollback_readiness(data),
        review_runtime_kill_switch_readiness(data),
        review_runtime_human_supervision_readiness(data),
    )
    risks = detect_release_candidate_risks(data, *reviews)
    score = compute_release_candidate_score(data, risks, *reviews)
    decision = _select_decision(risks, score.overall_score)
    state = _select_state(decision, score.overall_score)
    recommendations = generate_release_candidate_recommendations(risks, decision)
    offline_only = _offline_boundary(data)
    summary = f"{state.value}: decision={decision.value}, score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return PaperRuntimeReleaseCandidateResult(state, decision, score.overall_score, score, risks, *reviews, recommendations, offline_only, summary)


def render_paper_runtime_release_candidate_markdown(result: PaperRuntimeReleaseCandidateResult) -> str:
    lines = [
        "# AGIcore Paper Runtime Release Candidate",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Score: {result.release_candidate_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Release Candidate Reviews",
    ]
    reviews = (
        result.release_candidate_scope,
        result.runtime_freeze_status,
        result.runtime_test_coverage,
        result.runtime_stability_evidence,
        result.runtime_documentation_readiness,
        result.runtime_operational_boundaries,
        result.runtime_safety_guards,
        result.runtime_observability_readiness,
        result.runtime_rollback_readiness,
        result.runtime_kill_switch_readiness,
        result.runtime_human_supervision_readiness,
    )
    for review in reviews:
        lines.append(f"- {review.name}: passed={review.passed}, score={review.score}/100, risks={', '.join(risk.value for risk in review.risks) or 'none'}")
        lines.extend(f"  - {detail}" for detail in review.details if detail)
    lines.append("")
    lines.append("# Release Candidate Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Release Candidate Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_release_candidate_score",
    "detect_release_candidate_risks",
    "evaluate_paper_runtime_release_candidate",
    "generate_release_candidate_recommendations",
    "render_paper_runtime_release_candidate_markdown",
    "review_release_candidate_scope",
    "review_runtime_documentation_readiness",
    "review_runtime_freeze_status",
    "review_runtime_human_supervision_readiness",
    "review_runtime_kill_switch_readiness",
    "review_runtime_observability_readiness",
    "review_runtime_operational_boundaries",
    "review_runtime_rollback_readiness",
    "review_runtime_safety_guards",
    "review_runtime_stability_evidence",
    "review_runtime_test_coverage",
]
