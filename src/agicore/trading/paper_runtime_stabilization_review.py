"""Offline stabilization review for the AGIcore Paper Trading Runtime."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_runtime_stabilization_review_models import (
    PaperRuntimeStabilizationDecision,
    PaperRuntimeStabilizationRecommendation,
    PaperRuntimeStabilizationReview,
    PaperRuntimeStabilizationReviewInput,
    PaperRuntimeStabilizationReviewResult,
    PaperRuntimeStabilizationRisk,
    PaperRuntimeStabilizationScore,
    PaperRuntimeStabilizationState,
)


def _coerce_input(data: PaperRuntimeStabilizationReviewInput | Mapping[str, Any]) -> PaperRuntimeStabilizationReviewInput:
    if isinstance(data, PaperRuntimeStabilizationReviewInput):
        return data
    return PaperRuntimeStabilizationReviewInput(**dict(data))


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


def _upstream_items(data: PaperRuntimeStabilizationReviewInput) -> tuple[Any, ...]:
    return (
        data.extended_paper_runtime_test,
        data.paper_runtime_test_run,
        data.paper_trading_runtime,
        data.paper_runtime_integration_review,
        data.paper_trading_runtime_design,
        data.paper_runtime_decision_review,
        data.full_paper_session,
        data.simulated_market_session,
        data.mock_alpaca_session,
        data.mock_connectivity_layer,
        data.observability_verification,
        data.rollback_verification,
        data.kill_switch_verification,
        data.human_validated_paper_session,
        data.supervised_paper_session,
    )


def _upstream_risks(data: PaperRuntimeStabilizationReviewInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperRuntimeStabilizationReviewInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _review(name: str, score: int, risk: PaperRuntimeStabilizationRisk, failed: bool, details: tuple[str, ...] = ()) -> PaperRuntimeStabilizationReview:
    risks = (risk,) if failed or score < 85 else ()
    return PaperRuntimeStabilizationReview(name, _clamp(score), not risks and score >= 85, risks, details)


def review_runtime_stability(data: PaperRuntimeStabilizationReviewInput | Mapping[str, Any]) -> PaperRuntimeStabilizationReview:
    data = _coerce_input(data)
    extended = data.extended_paper_runtime_test
    failed = data.runtime_stable is not True or not _state_contains(extended, "READY_FOR_PAPER_RUNTIME_STABILIZATION_REVIEW") or _has_upstream_risk(data, "RUNTIME_STABILITY")
    score = data.runtime_stability_score if data.runtime_stability_score is not None else _average((_bool_score(data.runtime_stable), int(_get(extended, "extended_runtime_score", 45) or 45)))
    return _review("runtime_stability", score, PaperRuntimeStabilizationRisk.RUNTIME_STABILITY_FAILURE, failed, (_value(_get(extended, "state")),))


def review_scenario_repeatability(data: PaperRuntimeStabilizationReviewInput | Mapping[str, Any]) -> PaperRuntimeStabilizationReview:
    data = _coerce_input(data)
    failed = data.scenarios_repeatable is not True or _has_upstream_risk(data, "NOT_REPEATABLE", "REPEATABILITY")
    score = data.scenario_repeatability_score if data.scenario_repeatability_score is not None else _bool_score(data.scenarios_repeatable)
    return _review("scenario_repeatability", score, PaperRuntimeStabilizationRisk.SCENARIO_REPEATABILITY_FAILURE, failed)


def review_multi_session_consistency(data: PaperRuntimeStabilizationReviewInput | Mapping[str, Any]) -> PaperRuntimeStabilizationReview:
    data = _coerce_input(data)
    failed = data.multi_session_consistent is not True or _has_upstream_risk(data, "MULTI_SCENARIO", "MULTI_SESSION", "INCONSISTENCY")
    score = data.multi_session_consistency_score if data.multi_session_consistency_score is not None else _bool_score(data.multi_session_consistent)
    return _review("multi_session_consistency", score, PaperRuntimeStabilizationRisk.MULTI_SESSION_INCONSISTENCY, failed)


def review_error_handling_behavior(data: PaperRuntimeStabilizationReviewInput | Mapping[str, Any]) -> PaperRuntimeStabilizationReview:
    data = _coerce_input(data)
    failed = data.error_handling_stable is not True or _has_upstream_risk(data, "UNHANDLED", "ERROR_HANDLING")
    score = data.error_handling_score if data.error_handling_score is not None else _bool_score(data.error_handling_stable)
    return _review("error_handling_behavior", score, PaperRuntimeStabilizationRisk.ERROR_HANDLING_GAP, failed)


def review_rollback_stability(data: PaperRuntimeStabilizationReviewInput | Mapping[str, Any]) -> PaperRuntimeStabilizationReview:
    data = _coerce_input(data)
    failed = data.rollback_stable is not True or _has_upstream_risk(data, "ROLLBACK")
    score = data.rollback_stability_score if data.rollback_stability_score is not None else _bool_score(data.rollback_stable)
    return _review("rollback_stability", score, PaperRuntimeStabilizationRisk.ROLLBACK_STABILITY_GAP, failed)


def review_kill_switch_stability(data: PaperRuntimeStabilizationReviewInput | Mapping[str, Any]) -> PaperRuntimeStabilizationReview:
    data = _coerce_input(data)
    failed = data.kill_switch_stable is not True or _has_upstream_risk(data, "KILL_SWITCH")
    score = data.kill_switch_stability_score if data.kill_switch_stability_score is not None else _bool_score(data.kill_switch_stable)
    return _review("kill_switch_stability", score, PaperRuntimeStabilizationRisk.KILL_SWITCH_STABILITY_GAP, failed)


def review_human_supervision_stability(data: PaperRuntimeStabilizationReviewInput | Mapping[str, Any]) -> PaperRuntimeStabilizationReview:
    data = _coerce_input(data)
    failed = data.human_supervision_stable is not True or _has_upstream_risk(data, "HUMAN", "SUPERVISION")
    score = data.human_supervision_stability_score if data.human_supervision_stability_score is not None else _bool_score(data.human_supervision_stable)
    return _review("human_supervision_stability", score, PaperRuntimeStabilizationRisk.HUMAN_SUPERVISION_STABILITY_GAP, failed)


def review_journal_stability(data: PaperRuntimeStabilizationReviewInput | Mapping[str, Any]) -> PaperRuntimeStabilizationReview:
    data = _coerce_input(data)
    failed = data.journal_stable is not True or _has_upstream_risk(data, "JOURNAL")
    score = data.journal_stability_score if data.journal_stability_score is not None else _bool_score(data.journal_stable)
    return _review("journal_stability", score, PaperRuntimeStabilizationRisk.JOURNAL_STABILITY_GAP, failed)


def review_observability_stability(data: PaperRuntimeStabilizationReviewInput | Mapping[str, Any]) -> PaperRuntimeStabilizationReview:
    data = _coerce_input(data)
    failed = data.observability_stable is not True or _has_upstream_risk(data, "OBSERVABILITY")
    score = data.observability_stability_score if data.observability_stability_score is not None else _bool_score(data.observability_stable)
    return _review("observability_stability", score, PaperRuntimeStabilizationRisk.OBSERVABILITY_STABILITY_GAP, failed)


def review_runtime_state_drift(data: PaperRuntimeStabilizationReviewInput | Mapping[str, Any]) -> PaperRuntimeStabilizationReview:
    data = _coerce_input(data)
    failed = data.runtime_state_reconciled is not True or _has_upstream_risk(data, "DRIFT", "STATE_CORRUPTION")
    score = data.runtime_state_drift_score if data.runtime_state_drift_score is not None else _bool_score(data.runtime_state_reconciled)
    return _review("runtime_state_drift", score, PaperRuntimeStabilizationRisk.RUNTIME_STATE_DRIFT, failed)


def _offline_boundary(data: PaperRuntimeStabilizationReviewInput) -> bool:
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
        and _get(data.extended_paper_runtime_test, "offline_only", True) is True
        and not _has_upstream_risk(data, "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK", "BROKER", "EXTERNAL_DEPENDENCY")
    )


def detect_stabilization_risks(data: PaperRuntimeStabilizationReviewInput | Mapping[str, Any], *reviews: PaperRuntimeStabilizationReview) -> tuple[PaperRuntimeStabilizationRisk, ...]:
    data = _coerce_input(data)
    if not reviews:
        reviews = (
            review_runtime_stability(data),
            review_scenario_repeatability(data),
            review_multi_session_consistency(data),
            review_error_handling_behavior(data),
            review_rollback_stability(data),
            review_kill_switch_stability(data),
            review_human_supervision_stability(data),
            review_journal_stability(data),
            review_observability_stability(data),
            review_runtime_state_drift(data),
        )
    risks: list[PaperRuntimeStabilizationRisk] = []
    for review in reviews:
        risks.extend(review.risks)
    if data.release_candidate_requested is not True or not _offline_boundary(data):
        risks.append(PaperRuntimeStabilizationRisk.RELEASE_CANDIDATE_PREMATURE)
    return _dedupe(risks)


def compute_stabilization_score(data: PaperRuntimeStabilizationReviewInput | Mapping[str, Any], risks: tuple[PaperRuntimeStabilizationRisk, ...] = (), *reviews: PaperRuntimeStabilizationReview) -> PaperRuntimeStabilizationScore:
    data = _coerce_input(data)
    if not reviews:
        reviews = (
            review_runtime_stability(data),
            review_scenario_repeatability(data),
            review_multi_session_consistency(data),
            review_error_handling_behavior(data),
            review_rollback_stability(data),
            review_kill_switch_stability(data),
            review_human_supervision_stability(data),
            review_journal_stability(data),
            review_observability_stability(data),
            review_runtime_state_drift(data),
        )
    scores = tuple(review.score for review in reviews)
    overall = _clamp(_average(scores) - min(80, len(set(risks)) * 5))
    for risk, cap in {
        PaperRuntimeStabilizationRisk.RUNTIME_STABILITY_FAILURE: 45,
        PaperRuntimeStabilizationRisk.MULTI_SESSION_INCONSISTENCY: 55,
        PaperRuntimeStabilizationRisk.ROLLBACK_STABILITY_GAP: 55,
        PaperRuntimeStabilizationRisk.KILL_SWITCH_STABILITY_GAP: 50,
        PaperRuntimeStabilizationRisk.OBSERVABILITY_STABILITY_GAP: 60,
        PaperRuntimeStabilizationRisk.RUNTIME_STATE_DRIFT: 45,
        PaperRuntimeStabilizationRisk.RELEASE_CANDIDATE_PREMATURE: 40,
    }.items():
        if risk in risks:
            overall = min(overall, cap)
    return PaperRuntimeStabilizationScore(overall, *scores)


def _select_decision(risks: tuple[PaperRuntimeStabilizationRisk, ...], score: int) -> PaperRuntimeStabilizationDecision:
    if PaperRuntimeStabilizationRisk.RELEASE_CANDIDATE_PREMATURE in risks or PaperRuntimeStabilizationRisk.RUNTIME_STABILITY_FAILURE in risks or score < 45:
        return PaperRuntimeStabilizationDecision.BLOCK_RELEASE_CANDIDATE
    if PaperRuntimeStabilizationRisk.KILL_SWITCH_STABILITY_GAP in risks:
        return PaperRuntimeStabilizationDecision.REQUIRE_KILL_SWITCH_FIXES
    if PaperRuntimeStabilizationRisk.ROLLBACK_STABILITY_GAP in risks:
        return PaperRuntimeStabilizationDecision.REQUIRE_ROLLBACK_FIXES
    if PaperRuntimeStabilizationRisk.OBSERVABILITY_STABILITY_GAP in risks:
        return PaperRuntimeStabilizationDecision.REQUIRE_OBSERVABILITY_FIXES
    if risks:
        return PaperRuntimeStabilizationDecision.REQUIRE_RUNTIME_CLEANUP
    return PaperRuntimeStabilizationDecision.APPROVE_RELEASE_CANDIDATE_PREPARATION


def _select_state(decision: PaperRuntimeStabilizationDecision, score: int, risks: tuple[PaperRuntimeStabilizationRisk, ...]) -> PaperRuntimeStabilizationState:
    if decision == PaperRuntimeStabilizationDecision.BLOCK_RELEASE_CANDIDATE:
        return PaperRuntimeStabilizationState.NOT_STABLE
    if decision in {
        PaperRuntimeStabilizationDecision.REQUIRE_KILL_SWITCH_FIXES,
        PaperRuntimeStabilizationDecision.REQUIRE_ROLLBACK_FIXES,
        PaperRuntimeStabilizationDecision.REQUIRE_OBSERVABILITY_FIXES,
    }:
        return PaperRuntimeStabilizationState.STABILIZATION_REVIEW_REQUIRED
    if decision == PaperRuntimeStabilizationDecision.REQUIRE_RUNTIME_CLEANUP:
        return PaperRuntimeStabilizationState.STABILIZATION_REVIEW_REQUIRED if len(set(risks)) >= 3 or score < 72 else PaperRuntimeStabilizationState.PARTIALLY_STABLE
    if score >= 94:
        return PaperRuntimeStabilizationState.READY_FOR_PAPER_RUNTIME_RELEASE_CANDIDATE
    return PaperRuntimeStabilizationState.STABLE


def generate_stabilization_recommendations(risks: tuple[PaperRuntimeStabilizationRisk, ...], decision: PaperRuntimeStabilizationDecision | None = None) -> tuple[PaperRuntimeStabilizationRecommendation, ...]:
    recommendations: list[PaperRuntimeStabilizationRecommendation] = []
    if risks:
        recommendations.append(PaperRuntimeStabilizationRecommendation.HOLD_RELEASE_CANDIDATE)
    mapping = {
        PaperRuntimeStabilizationRisk.RUNTIME_STABILITY_FAILURE: PaperRuntimeStabilizationRecommendation.REPAIR_RUNTIME_STABILITY,
        PaperRuntimeStabilizationRisk.SCENARIO_REPEATABILITY_FAILURE: PaperRuntimeStabilizationRecommendation.STABILIZE_SCENARIO_REPEATABILITY,
        PaperRuntimeStabilizationRisk.MULTI_SESSION_INCONSISTENCY: PaperRuntimeStabilizationRecommendation.RECONCILE_MULTI_SESSION_CONSISTENCY,
        PaperRuntimeStabilizationRisk.ERROR_HANDLING_GAP: PaperRuntimeStabilizationRecommendation.IMPROVE_ERROR_HANDLING,
        PaperRuntimeStabilizationRisk.ROLLBACK_STABILITY_GAP: PaperRuntimeStabilizationRecommendation.REPAIR_ROLLBACK_STABILITY,
        PaperRuntimeStabilizationRisk.KILL_SWITCH_STABILITY_GAP: PaperRuntimeStabilizationRecommendation.REPAIR_KILL_SWITCH_STABILITY,
        PaperRuntimeStabilizationRisk.HUMAN_SUPERVISION_STABILITY_GAP: PaperRuntimeStabilizationRecommendation.REPAIR_HUMAN_SUPERVISION_STABILITY,
        PaperRuntimeStabilizationRisk.JOURNAL_STABILITY_GAP: PaperRuntimeStabilizationRecommendation.REPAIR_JOURNAL_STABILITY,
        PaperRuntimeStabilizationRisk.OBSERVABILITY_STABILITY_GAP: PaperRuntimeStabilizationRecommendation.REPAIR_OBSERVABILITY_STABILITY,
        PaperRuntimeStabilizationRisk.RUNTIME_STATE_DRIFT: PaperRuntimeStabilizationRecommendation.RECONCILE_RUNTIME_STATE_DRIFT,
        PaperRuntimeStabilizationRisk.RELEASE_CANDIDATE_PREMATURE: PaperRuntimeStabilizationRecommendation.DELAY_RELEASE_CANDIDATE,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(PaperRuntimeStabilizationRecommendation.RUN_STABILIZATION_REVIEW_SUITE)
    if decision == PaperRuntimeStabilizationDecision.APPROVE_RELEASE_CANDIDATE_PREPARATION:
        recommendations.append(PaperRuntimeStabilizationRecommendation.APPROVE_RELEASE_CANDIDATE_AFTER_MANUAL_REVIEW)
    return _dedupe(recommendations)


def evaluate_paper_runtime_stabilization_review(data: PaperRuntimeStabilizationReviewInput | Mapping[str, Any]) -> PaperRuntimeStabilizationReviewResult:
    data = _coerce_input(data)
    reviews = (
        review_runtime_stability(data),
        review_scenario_repeatability(data),
        review_multi_session_consistency(data),
        review_error_handling_behavior(data),
        review_rollback_stability(data),
        review_kill_switch_stability(data),
        review_human_supervision_stability(data),
        review_journal_stability(data),
        review_observability_stability(data),
        review_runtime_state_drift(data),
    )
    risks = detect_stabilization_risks(data, *reviews)
    score = compute_stabilization_score(data, risks, *reviews)
    decision = _select_decision(risks, score.overall_score)
    state = _select_state(decision, score.overall_score, risks)
    recommendations = generate_stabilization_recommendations(risks, decision)
    offline_only = _offline_boundary(data)
    summary = f"{state.value}: decision={decision.value}, score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return PaperRuntimeStabilizationReviewResult(state, decision, score.overall_score, score, risks, *reviews, recommendations, offline_only, summary)


def render_paper_runtime_stabilization_review_markdown(result: PaperRuntimeStabilizationReviewResult) -> str:
    lines = [
        "# AGIcore Paper Runtime Stabilization Review",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Score: {result.stabilization_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Stabilization Reviews",
    ]
    reviews = (
        result.runtime_stability,
        result.scenario_repeatability,
        result.multi_session_consistency,
        result.error_handling_behavior,
        result.rollback_stability,
        result.kill_switch_stability,
        result.human_supervision_stability,
        result.journal_stability,
        result.observability_stability,
        result.runtime_state_drift,
    )
    for review in reviews:
        lines.append(f"- {review.name}: passed={review.passed}, score={review.score}/100, risks={', '.join(risk.value for risk in review.risks) or 'none'}")
        lines.extend(f"  - {detail}" for detail in review.details)
    lines.append("")
    lines.append("# Stabilization Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Stabilization Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_stabilization_score",
    "detect_stabilization_risks",
    "evaluate_paper_runtime_stabilization_review",
    "generate_stabilization_recommendations",
    "render_paper_runtime_stabilization_review_markdown",
    "review_error_handling_behavior",
    "review_human_supervision_stability",
    "review_journal_stability",
    "review_kill_switch_stability",
    "review_multi_session_consistency",
    "review_observability_stability",
    "review_rollback_stability",
    "review_runtime_stability",
    "review_runtime_state_drift",
    "review_scenario_repeatability",
]
