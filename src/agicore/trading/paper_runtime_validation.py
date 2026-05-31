"""Offline validation layer for the AGIcore Paper Trading Runtime."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_runtime_validation_models import (
    PaperRuntimeValidationDecision,
    PaperRuntimeValidationInput,
    PaperRuntimeValidationRecommendation,
    PaperRuntimeValidationResult,
    PaperRuntimeValidationReview,
    PaperRuntimeValidationRisk,
    PaperRuntimeValidationScore,
    PaperRuntimeValidationState,
)


def _coerce_input(data: PaperRuntimeValidationInput | Mapping[str, Any]) -> PaperRuntimeValidationInput:
    if isinstance(data, PaperRuntimeValidationInput):
        return data
    return PaperRuntimeValidationInput(**dict(data))


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


def _upstream_items(data: PaperRuntimeValidationInput) -> tuple[Any, ...]:
    return (
        data.paper_runtime_release_candidate,
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


def _upstream_risks(data: PaperRuntimeValidationInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperRuntimeValidationInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _review(
    name: str,
    score: int,
    risk: PaperRuntimeValidationRisk,
    failed: bool,
    details: tuple[str, ...] = (),
) -> PaperRuntimeValidationReview:
    risks = (risk,) if failed or score < 85 else ()
    return PaperRuntimeValidationReview(name, _clamp(score), not risks and score >= 85, risks, details)


def validate_release_candidate_status(data: PaperRuntimeValidationInput | Mapping[str, Any]) -> PaperRuntimeValidationReview:
    data = _coerce_input(data)
    rc = data.paper_runtime_release_candidate
    failed = (
        data.release_candidate_ready is not True
        or not _state_contains(rc, "READY_FOR_PAPER_RUNTIME_VALIDATION", "APPROVE_PAPER_RUNTIME_RELEASE_CANDIDATE")
        or _has_upstream_risk(data, "RELEASE_CANDIDATE_NOT_READY", "PREMATURE_RC", "RC_SCOPE")
    )
    score = data.release_candidate_status_score if data.release_candidate_status_score is not None else _average((_bool_score(data.release_candidate_ready), int(_get(rc, "release_candidate_score", 45) or 45)))
    return _review("release_candidate_status", score, PaperRuntimeValidationRisk.RELEASE_CANDIDATE_NOT_READY, failed, (_value(_get(rc, "state")),))


def validate_runtime_execution_evidence(data: PaperRuntimeValidationInput | Mapping[str, Any]) -> PaperRuntimeValidationReview:
    data = _coerce_input(data)
    runtime = data.paper_trading_runtime
    failed = (
        data.runtime_execution_evidence_ready is not True
        or not _state_contains(runtime, "COMPLETED", "READY", "RUNNING")
        or _has_upstream_risk(data, "RUNTIME_EXECUTION", "RUNTIME_START", "RUNTIME_STOP")
    )
    score = data.runtime_execution_evidence_score if data.runtime_execution_evidence_score is not None else _bool_score(data.runtime_execution_evidence_ready)
    return _review("runtime_execution_evidence", score, PaperRuntimeValidationRisk.RUNTIME_EXECUTION_EVIDENCE_GAP, failed, (_value(_get(runtime, "state")),))


def validate_runtime_test_evidence(data: PaperRuntimeValidationInput | Mapping[str, Any]) -> PaperRuntimeValidationReview:
    data = _coerce_input(data)
    test_run = data.paper_runtime_test_run
    failed = (
        data.runtime_test_evidence_ready is not True
        or not _state_contains(test_run, "READY_FOR_EXTENDED_PAPER_RUNTIME_TEST", "TEST_RUN_COMPLETED")
        or _has_upstream_risk(data, "TEST_RUN", "SESSION_INIT", "MARKET_CYCLE", "SAFETY_GATE")
    )
    upstream_score = int(_get(test_run, "test_run_score", 100) or 100)
    score = data.runtime_test_evidence_score if data.runtime_test_evidence_score is not None else _average((_bool_score(data.runtime_test_evidence_ready), upstream_score))
    return _review("runtime_test_evidence", score, PaperRuntimeValidationRisk.RUNTIME_TEST_EVIDENCE_GAP, failed)


def validate_extended_test_evidence(data: PaperRuntimeValidationInput | Mapping[str, Any]) -> PaperRuntimeValidationReview:
    data = _coerce_input(data)
    extended = data.extended_paper_runtime_test
    failed = (
        data.extended_test_evidence_ready is not True
        or not _state_contains(extended, "READY_FOR_PAPER_RUNTIME_STABILIZATION_REVIEW", "EXTENDED_TEST_COMPLETED")
        or _has_upstream_risk(data, "EXTENDED_TEST", "MULTI_SCENARIO", "NOT_REPEATABLE")
    )
    upstream_score = int(_get(extended, "extended_runtime_score", 100) or 100)
    score = data.extended_test_evidence_score if data.extended_test_evidence_score is not None else _average((_bool_score(data.extended_test_evidence_ready), upstream_score))
    return _review("extended_test_evidence", score, PaperRuntimeValidationRisk.EXTENDED_TEST_EVIDENCE_GAP, failed)


def validate_stabilization_evidence(data: PaperRuntimeValidationInput | Mapping[str, Any]) -> PaperRuntimeValidationReview:
    data = _coerce_input(data)
    stabilization = data.paper_runtime_stabilization_review
    failed = (
        data.stabilization_evidence_ready is not True
        or not _state_contains(stabilization, "READY_FOR_PAPER_RUNTIME_RELEASE_CANDIDATE", "APPROVE_RELEASE_CANDIDATE_PREPARATION")
        or _has_upstream_risk(data, "STABILIZATION", "RUNTIME_STABILITY", "STATE_DRIFT")
    )
    upstream_score = int(_get(stabilization, "stabilization_score", 100) or 100)
    score = data.stabilization_evidence_score if data.stabilization_evidence_score is not None else _average((_bool_score(data.stabilization_evidence_ready), upstream_score))
    return _review("stabilization_evidence", score, PaperRuntimeValidationRisk.STABILIZATION_EVIDENCE_GAP, failed)


def validate_safety_evidence(data: PaperRuntimeValidationInput | Mapping[str, Any]) -> PaperRuntimeValidationReview:
    data = _coerce_input(data)
    failed = data.safety_evidence_ready is not True or _has_upstream_risk(data, "SAFETY", "BYPASS", "EXECUTION_LEAK")
    score = data.safety_evidence_score if data.safety_evidence_score is not None else _bool_score(data.safety_evidence_ready)
    return _review("safety_evidence", score, PaperRuntimeValidationRisk.SAFETY_EVIDENCE_GAP, failed)


def validate_observability_evidence(data: PaperRuntimeValidationInput | Mapping[str, Any]) -> PaperRuntimeValidationReview:
    data = _coerce_input(data)
    failed = data.observability_evidence_ready is not True or _has_upstream_risk(data, "OBSERVABILITY")
    score = data.observability_evidence_score if data.observability_evidence_score is not None else _bool_score(data.observability_evidence_ready)
    return _review("observability_evidence", score, PaperRuntimeValidationRisk.OBSERVABILITY_EVIDENCE_GAP, failed)


def validate_rollback_evidence(data: PaperRuntimeValidationInput | Mapping[str, Any]) -> PaperRuntimeValidationReview:
    data = _coerce_input(data)
    failed = data.rollback_evidence_ready is not True or _has_upstream_risk(data, "ROLLBACK")
    score = data.rollback_evidence_score if data.rollback_evidence_score is not None else _bool_score(data.rollback_evidence_ready)
    return _review("rollback_evidence", score, PaperRuntimeValidationRisk.ROLLBACK_EVIDENCE_GAP, failed)


def validate_kill_switch_evidence(data: PaperRuntimeValidationInput | Mapping[str, Any]) -> PaperRuntimeValidationReview:
    data = _coerce_input(data)
    failed = data.kill_switch_evidence_ready is not True or _has_upstream_risk(data, "KILL_SWITCH")
    score = data.kill_switch_evidence_score if data.kill_switch_evidence_score is not None else _bool_score(data.kill_switch_evidence_ready)
    return _review("kill_switch_evidence", score, PaperRuntimeValidationRisk.KILL_SWITCH_EVIDENCE_GAP, failed)


def validate_human_supervision_evidence(data: PaperRuntimeValidationInput | Mapping[str, Any]) -> PaperRuntimeValidationReview:
    data = _coerce_input(data)
    failed = data.human_supervision_evidence_ready is not True or _has_upstream_risk(data, "HUMAN", "SUPERVISION")
    score = data.human_supervision_evidence_score if data.human_supervision_evidence_score is not None else _bool_score(data.human_supervision_evidence_ready)
    return _review("human_supervision_evidence", score, PaperRuntimeValidationRisk.HUMAN_SUPERVISION_EVIDENCE_GAP, failed)


def validate_operational_boundaries(data: PaperRuntimeValidationInput | Mapping[str, Any]) -> PaperRuntimeValidationReview:
    data = _coerce_input(data)
    failed = data.operational_boundaries_validated is not True or not _offline_boundary(data) or _has_upstream_risk(data, "LIVE_EXECUTION", "NETWORK_LEAK", "BROKER", "EXTERNAL_DEPENDENCY")
    score = data.operational_boundaries_score if data.operational_boundaries_score is not None else _bool_score(data.operational_boundaries_validated)
    return _review("operational_boundaries", score, PaperRuntimeValidationRisk.OPERATIONAL_BOUNDARY_VIOLATION, failed)


def _offline_boundary(data: PaperRuntimeValidationInput) -> bool:
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
        and _get(data.paper_runtime_release_candidate, "offline_only", True) is True
        and not _has_upstream_risk(data, "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK", "BROKER", "EXTERNAL_DEPENDENCY")
    )


def detect_validation_risks(
    data: PaperRuntimeValidationInput | Mapping[str, Any],
    *reviews: PaperRuntimeValidationReview,
) -> tuple[PaperRuntimeValidationRisk, ...]:
    data = _coerce_input(data)
    if not reviews:
        reviews = (
            validate_release_candidate_status(data),
            validate_runtime_execution_evidence(data),
            validate_runtime_test_evidence(data),
            validate_extended_test_evidence(data),
            validate_stabilization_evidence(data),
            validate_safety_evidence(data),
            validate_observability_evidence(data),
            validate_rollback_evidence(data),
            validate_kill_switch_evidence(data),
            validate_human_supervision_evidence(data),
            validate_operational_boundaries(data),
        )
    risks: list[PaperRuntimeValidationRisk] = []
    for review in reviews:
        risks.extend(review.risks)
    if data.validation_approval_requested is not True or not _offline_boundary(data):
        risks.append(PaperRuntimeValidationRisk.PREMATURE_VALIDATION_APPROVAL)
    return _dedupe(risks)


def compute_validation_score(
    data: PaperRuntimeValidationInput | Mapping[str, Any],
    risks: tuple[PaperRuntimeValidationRisk, ...] = (),
    *reviews: PaperRuntimeValidationReview,
) -> PaperRuntimeValidationScore:
    data = _coerce_input(data)
    if not reviews:
        reviews = (
            validate_release_candidate_status(data),
            validate_runtime_execution_evidence(data),
            validate_runtime_test_evidence(data),
            validate_extended_test_evidence(data),
            validate_stabilization_evidence(data),
            validate_safety_evidence(data),
            validate_observability_evidence(data),
            validate_rollback_evidence(data),
            validate_kill_switch_evidence(data),
            validate_human_supervision_evidence(data),
            validate_operational_boundaries(data),
        )
    scores = tuple(review.score for review in reviews)
    overall = _clamp(_average(scores) - min(80, len(set(risks)) * 5))
    for risk, cap in {
        PaperRuntimeValidationRisk.RELEASE_CANDIDATE_NOT_READY: 45,
        PaperRuntimeValidationRisk.RUNTIME_EXECUTION_EVIDENCE_GAP: 55,
        PaperRuntimeValidationRisk.RUNTIME_TEST_EVIDENCE_GAP: 60,
        PaperRuntimeValidationRisk.EXTENDED_TEST_EVIDENCE_GAP: 60,
        PaperRuntimeValidationRisk.STABILIZATION_EVIDENCE_GAP: 55,
        PaperRuntimeValidationRisk.SAFETY_EVIDENCE_GAP: 50,
        PaperRuntimeValidationRisk.ROLLBACK_EVIDENCE_GAP: 55,
        PaperRuntimeValidationRisk.KILL_SWITCH_EVIDENCE_GAP: 50,
        PaperRuntimeValidationRisk.OPERATIONAL_BOUNDARY_VIOLATION: 40,
        PaperRuntimeValidationRisk.PREMATURE_VALIDATION_APPROVAL: 40,
    }.items():
        if risk in risks:
            overall = min(overall, cap)
    return PaperRuntimeValidationScore(overall, *scores)


def _select_decision(risks: tuple[PaperRuntimeValidationRisk, ...], score: int) -> PaperRuntimeValidationDecision:
    if PaperRuntimeValidationRisk.PREMATURE_VALIDATION_APPROVAL in risks or PaperRuntimeValidationRisk.OPERATIONAL_BOUNDARY_VIOLATION in risks or score < 45:
        return PaperRuntimeValidationDecision.BLOCK_VALIDATION
    if PaperRuntimeValidationRisk.RELEASE_CANDIDATE_NOT_READY in risks:
        return PaperRuntimeValidationDecision.REQUIRE_RELEASE_CANDIDATE_FIXES
    if PaperRuntimeValidationRisk.RUNTIME_EXECUTION_EVIDENCE_GAP in risks:
        return PaperRuntimeValidationDecision.REQUIRE_EXECUTION_EVIDENCE
    if PaperRuntimeValidationRisk.RUNTIME_TEST_EVIDENCE_GAP in risks or PaperRuntimeValidationRisk.EXTENDED_TEST_EVIDENCE_GAP in risks:
        return PaperRuntimeValidationDecision.REQUIRE_TEST_EVIDENCE
    if (
        PaperRuntimeValidationRisk.SAFETY_EVIDENCE_GAP in risks
        or PaperRuntimeValidationRisk.ROLLBACK_EVIDENCE_GAP in risks
        or PaperRuntimeValidationRisk.KILL_SWITCH_EVIDENCE_GAP in risks
    ):
        return PaperRuntimeValidationDecision.REQUIRE_SAFETY_EVIDENCE
    if risks:
        return PaperRuntimeValidationDecision.REQUIRE_TEST_EVIDENCE if score < 75 else PaperRuntimeValidationDecision.REQUIRE_SAFETY_EVIDENCE
    return PaperRuntimeValidationDecision.APPROVE_PAPER_RUNTIME_VALIDATION


def _select_state(decision: PaperRuntimeValidationDecision, score: int) -> PaperRuntimeValidationState:
    if decision == PaperRuntimeValidationDecision.BLOCK_VALIDATION:
        return PaperRuntimeValidationState.NOT_VALIDATED
    if decision != PaperRuntimeValidationDecision.APPROVE_PAPER_RUNTIME_VALIDATION:
        return PaperRuntimeValidationState.VALIDATION_REVIEW_REQUIRED if score < 82 else PaperRuntimeValidationState.PARTIALLY_VALIDATED
    if score >= 95:
        return PaperRuntimeValidationState.READY_FOR_OFFICIAL_PAPER_VALIDATION_REPORT
    return PaperRuntimeValidationState.VALIDATED


def generate_validation_recommendations(
    risks: tuple[PaperRuntimeValidationRisk, ...],
    decision: PaperRuntimeValidationDecision | None = None,
) -> tuple[PaperRuntimeValidationRecommendation, ...]:
    recommendations: list[PaperRuntimeValidationRecommendation] = []
    if risks:
        recommendations.append(PaperRuntimeValidationRecommendation.HOLD_VALIDATION)
    mapping = {
        PaperRuntimeValidationRisk.RELEASE_CANDIDATE_NOT_READY: PaperRuntimeValidationRecommendation.REPAIR_RELEASE_CANDIDATE_STATUS,
        PaperRuntimeValidationRisk.RUNTIME_EXECUTION_EVIDENCE_GAP: PaperRuntimeValidationRecommendation.COMPLETE_RUNTIME_EXECUTION_EVIDENCE,
        PaperRuntimeValidationRisk.RUNTIME_TEST_EVIDENCE_GAP: PaperRuntimeValidationRecommendation.COMPLETE_RUNTIME_TEST_EVIDENCE,
        PaperRuntimeValidationRisk.EXTENDED_TEST_EVIDENCE_GAP: PaperRuntimeValidationRecommendation.COMPLETE_EXTENDED_TEST_EVIDENCE,
        PaperRuntimeValidationRisk.STABILIZATION_EVIDENCE_GAP: PaperRuntimeValidationRecommendation.COMPLETE_STABILIZATION_EVIDENCE,
        PaperRuntimeValidationRisk.SAFETY_EVIDENCE_GAP: PaperRuntimeValidationRecommendation.COMPLETE_SAFETY_EVIDENCE,
        PaperRuntimeValidationRisk.OBSERVABILITY_EVIDENCE_GAP: PaperRuntimeValidationRecommendation.COMPLETE_OBSERVABILITY_EVIDENCE,
        PaperRuntimeValidationRisk.ROLLBACK_EVIDENCE_GAP: PaperRuntimeValidationRecommendation.COMPLETE_ROLLBACK_EVIDENCE,
        PaperRuntimeValidationRisk.KILL_SWITCH_EVIDENCE_GAP: PaperRuntimeValidationRecommendation.COMPLETE_KILL_SWITCH_EVIDENCE,
        PaperRuntimeValidationRisk.HUMAN_SUPERVISION_EVIDENCE_GAP: PaperRuntimeValidationRecommendation.COMPLETE_HUMAN_SUPERVISION_EVIDENCE,
        PaperRuntimeValidationRisk.OPERATIONAL_BOUNDARY_VIOLATION: PaperRuntimeValidationRecommendation.REINFORCE_OPERATIONAL_BOUNDARIES,
        PaperRuntimeValidationRisk.PREMATURE_VALIDATION_APPROVAL: PaperRuntimeValidationRecommendation.DELAY_VALIDATION_APPROVAL,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(PaperRuntimeValidationRecommendation.RUN_PAPER_RUNTIME_VALIDATION_SUITE)
    if decision == PaperRuntimeValidationDecision.APPROVE_PAPER_RUNTIME_VALIDATION:
        recommendations.append(PaperRuntimeValidationRecommendation.APPROVE_OFFICIAL_PAPER_VALIDATION_REPORT)
    return _dedupe(recommendations)


def evaluate_paper_runtime_validation(data: PaperRuntimeValidationInput | Mapping[str, Any]) -> PaperRuntimeValidationResult:
    data = _coerce_input(data)
    reviews = (
        validate_release_candidate_status(data),
        validate_runtime_execution_evidence(data),
        validate_runtime_test_evidence(data),
        validate_extended_test_evidence(data),
        validate_stabilization_evidence(data),
        validate_safety_evidence(data),
        validate_observability_evidence(data),
        validate_rollback_evidence(data),
        validate_kill_switch_evidence(data),
        validate_human_supervision_evidence(data),
        validate_operational_boundaries(data),
    )
    risks = detect_validation_risks(data, *reviews)
    score = compute_validation_score(data, risks, *reviews)
    decision = _select_decision(risks, score.overall_score)
    state = _select_state(decision, score.overall_score)
    recommendations = generate_validation_recommendations(risks, decision)
    offline_only = _offline_boundary(data)
    summary = f"{state.value}: decision={decision.value}, score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return PaperRuntimeValidationResult(state, decision, score.overall_score, score, risks, *reviews, recommendations, offline_only, summary)


def render_paper_runtime_validation_markdown(result: PaperRuntimeValidationResult) -> str:
    lines = [
        "# AGIcore Paper Runtime Validation",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Score: {result.validation_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Validation Reviews",
    ]
    reviews = (
        result.release_candidate_status,
        result.runtime_execution_evidence,
        result.runtime_test_evidence,
        result.extended_test_evidence,
        result.stabilization_evidence,
        result.safety_evidence,
        result.observability_evidence,
        result.rollback_evidence,
        result.kill_switch_evidence,
        result.human_supervision_evidence,
        result.operational_boundaries,
    )
    for review in reviews:
        lines.append(f"- {review.name}: passed={review.passed}, score={review.score}/100, risks={', '.join(risk.value for risk in review.risks) or 'none'}")
        lines.extend(f"  - {detail}" for detail in review.details if detail)
    lines.append("")
    lines.append("# Validation Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Validation Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_validation_score",
    "detect_validation_risks",
    "evaluate_paper_runtime_validation",
    "generate_validation_recommendations",
    "render_paper_runtime_validation_markdown",
    "validate_extended_test_evidence",
    "validate_human_supervision_evidence",
    "validate_kill_switch_evidence",
    "validate_observability_evidence",
    "validate_operational_boundaries",
    "validate_release_candidate_status",
    "validate_rollback_evidence",
    "validate_runtime_execution_evidence",
    "validate_runtime_test_evidence",
    "validate_safety_evidence",
    "validate_stabilization_evidence",
]
