"""Offline integration review for the AGIcore Paper Trading Runtime."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_runtime_integration_review_models import (
    PaperRuntimeIntegrationDecision,
    PaperRuntimeIntegrationRecommendation,
    PaperRuntimeIntegrationReview,
    PaperRuntimeIntegrationReviewInput,
    PaperRuntimeIntegrationReviewResult,
    PaperRuntimeIntegrationReviewScore,
    PaperRuntimeIntegrationReviewState,
    PaperRuntimeIntegrationRisk,
)


def _coerce_input(data: PaperRuntimeIntegrationReviewInput | Mapping[str, Any]) -> PaperRuntimeIntegrationReviewInput:
    if isinstance(data, PaperRuntimeIntegrationReviewInput):
        return data
    return PaperRuntimeIntegrationReviewInput(**dict(data))


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


def _upstream_items(data: PaperRuntimeIntegrationReviewInput) -> tuple[Any, ...]:
    return (
        data.paper_trading_runtime,
        data.paper_trading_runtime_design,
        data.paper_runtime_decision_review,
        data.paper_runtime_pre_review,
        data.full_paper_session,
        data.simulated_market_session,
        data.mock_alpaca_session,
        data.mock_connectivity_layer,
        data.alpaca_paper_connectivity_readiness,
        data.broker_paper_sandbox,
        data.observability_verification,
        data.rollback_verification,
        data.kill_switch_verification,
        data.human_validated_paper_session,
        data.supervised_paper_session,
    )


def _upstream_risks(data: PaperRuntimeIntegrationReviewInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperRuntimeIntegrationReviewInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _runtime_completed(data: PaperRuntimeIntegrationReviewInput) -> bool:
    runtime = data.paper_trading_runtime
    return _state_contains(runtime, "COMPLETED") and _get(runtime, "offline_only") is True and not _as_tuple(_get(runtime, "risks", ()))


def _review(name: str, score: int, risk: PaperRuntimeIntegrationRisk, failed: bool, details: tuple[str, ...] = ()) -> PaperRuntimeIntegrationReview:
    risks = (risk,) if failed or score < 85 else ()
    return PaperRuntimeIntegrationReview(name, _clamp(score), not risks and score >= 85, risks, details)


def review_runtime_design_alignment(data: PaperRuntimeIntegrationReviewInput | Mapping[str, Any]) -> PaperRuntimeIntegrationReview:
    data = _coerce_input(data)
    runtime = data.paper_trading_runtime
    design = data.paper_trading_runtime_design
    failed = (
        data.runtime_entrypoint_present is not True
        or data.runtime_state_machine_aligned is not True
        or data.runtime_design_approved is not True
        or not _state_contains(design, "READY_FOR_RUNTIME_IMPLEMENTATION", "APPROVE_RUNTIME_IMPLEMENTATION")
        or not _state_contains(runtime, "COMPLETED")
        or _has_upstream_risk(data, "RUNTIME_DESIGN", "STATE_MACHINE", "ARCHITECTURE")
    )
    score = data.runtime_design_alignment_score if data.runtime_design_alignment_score is not None else _average((
        _bool_score(data.runtime_entrypoint_present),
        _bool_score(data.runtime_state_machine_aligned),
        _bool_score(data.runtime_design_approved),
        100 if _state_contains(design, "READY_FOR_RUNTIME_IMPLEMENTATION", "APPROVE_RUNTIME_IMPLEMENTATION") else 45,
        100 if _state_contains(runtime, "COMPLETED") else 45,
    ))
    details = (f"runtime_state={_value(_get(runtime, 'state'))}", f"design_state={_value(_get(design, 'state'))}")
    return _review("runtime_design_alignment", score, PaperRuntimeIntegrationRisk.RUNTIME_DESIGN_MISMATCH, failed, details)


def review_decision_review_alignment(data: PaperRuntimeIntegrationReviewInput | Mapping[str, Any]) -> PaperRuntimeIntegrationReview:
    data = _coerce_input(data)
    decision = data.paper_runtime_decision_review
    failed = data.decision_review_approved is not True or not _state_contains(decision, "READY_FOR_PAPER_TRADING_RUNTIME", "APPROVE_PAPER_TRADING_RUNTIME_CREATION")
    score = data.decision_review_alignment_score if data.decision_review_alignment_score is not None else _average((
        _bool_score(data.decision_review_approved),
        100 if _state_contains(decision, "READY_FOR_PAPER_TRADING_RUNTIME", "APPROVE_PAPER_TRADING_RUNTIME_CREATION") else 45,
    ))
    return _review("decision_review_alignment", score, PaperRuntimeIntegrationRisk.DECISION_REVIEW_MISMATCH, failed, (_value(_get(decision, "state")),))


def review_full_session_alignment(data: PaperRuntimeIntegrationReviewInput | Mapping[str, Any]) -> PaperRuntimeIntegrationReview:
    data = _coerce_input(data)
    failed = data.full_session_chain_aligned is not True or not _state_contains(data.full_paper_session, "READY_FOR_PAPER_TRADING_RUNTIME", "FULL_SESSION_COMPLETED")
    score = data.full_session_alignment_score if data.full_session_alignment_score is not None else _average((_bool_score(data.full_session_chain_aligned), 100 if not failed else 45))
    return _review("full_session_alignment", score, PaperRuntimeIntegrationRisk.FULL_SESSION_MISMATCH, failed, (_value(_get(data.full_paper_session, "state")),))


def review_simulated_market_alignment(data: PaperRuntimeIntegrationReviewInput | Mapping[str, Any]) -> PaperRuntimeIntegrationReview:
    data = _coerce_input(data)
    failed = data.simulated_market_chain_aligned is not True or not _state_contains(data.simulated_market_session, "READY_FOR_FULL_PAPER_SESSION", "SIMULATED_SESSION_COMPLETED")
    score = data.simulated_market_alignment_score if data.simulated_market_alignment_score is not None else _average((_bool_score(data.simulated_market_chain_aligned), 100 if not failed else 45))
    return _review("simulated_market_alignment", score, PaperRuntimeIntegrationRisk.SIMULATED_MARKET_MISMATCH, failed, (_value(_get(data.simulated_market_session, "state")),))


def review_mock_alpaca_alignment(data: PaperRuntimeIntegrationReviewInput | Mapping[str, Any]) -> PaperRuntimeIntegrationReview:
    data = _coerce_input(data)
    failed = data.mock_alpaca_chain_aligned is not True or not _state_contains(data.mock_alpaca_session, "READY_FOR_SIMULATED_MARKET_SESSION", "MOCK_SESSION_COMPLETED")
    score = data.mock_alpaca_alignment_score if data.mock_alpaca_alignment_score is not None else _average((_bool_score(data.mock_alpaca_chain_aligned), 100 if not failed else 45))
    return _review("mock_alpaca_alignment", score, PaperRuntimeIntegrationRisk.MOCK_ALPACA_MISMATCH, failed, (_value(_get(data.mock_alpaca_session, "state")),))


def review_mock_connectivity_alignment(data: PaperRuntimeIntegrationReviewInput | Mapping[str, Any]) -> PaperRuntimeIntegrationReview:
    data = _coerce_input(data)
    failed = data.mock_connectivity_chain_aligned is not True or not _state_contains(data.mock_connectivity_layer, "READY_FOR_MOCK_ALPACA_SESSION", "MOCK_CONNECTIVITY_VALIDATED")
    score = data.mock_connectivity_alignment_score if data.mock_connectivity_alignment_score is not None else _average((_bool_score(data.mock_connectivity_chain_aligned), 100 if not failed else 45))
    return _review("mock_connectivity_alignment", score, PaperRuntimeIntegrationRisk.MOCK_CONNECTIVITY_MISMATCH, failed, (_value(_get(data.mock_connectivity_layer, "state")),))


def review_observability_integration(data: PaperRuntimeIntegrationReviewInput | Mapping[str, Any]) -> PaperRuntimeIntegrationReview:
    data = _coerce_input(data)
    runtime = data.paper_trading_runtime
    report = _get(runtime, "report")
    observed_count = int(_get(report, "observability_count", 0) or 0)
    failed = data.observability_events_linked is not True or data.observability_reported is not True or observed_count <= 0 or _has_upstream_risk(data, "OBSERVABILITY")
    score = data.observability_integration_score if data.observability_integration_score is not None else _average((_bool_score(data.observability_events_linked), _bool_score(data.observability_reported), 100 if observed_count > 0 else 0))
    return _review("observability_integration", score, PaperRuntimeIntegrationRisk.OBSERVABILITY_INTEGRATION_GAP, failed, (f"observability_count={observed_count}",))


def review_rollback_integration(data: PaperRuntimeIntegrationReviewInput | Mapping[str, Any]) -> PaperRuntimeIntegrationReview:
    data = _coerce_input(data)
    failed = data.rollback_hook_linked is not True or data.rollback_stop_state_supported is not True or _has_upstream_risk(data, "ROLLBACK")
    score = data.rollback_integration_score if data.rollback_integration_score is not None else _average((_bool_score(data.rollback_hook_linked), _bool_score(data.rollback_stop_state_supported)))
    return _review("rollback_integration", score, PaperRuntimeIntegrationRisk.ROLLBACK_INTEGRATION_GAP, failed)


def review_kill_switch_integration(data: PaperRuntimeIntegrationReviewInput | Mapping[str, Any]) -> PaperRuntimeIntegrationReview:
    data = _coerce_input(data)
    failed = data.kill_switch_hook_linked is not True or data.kill_switch_stop_state_supported is not True or _has_upstream_risk(data, "KILL_SWITCH")
    score = data.kill_switch_integration_score if data.kill_switch_integration_score is not None else _average((_bool_score(data.kill_switch_hook_linked), _bool_score(data.kill_switch_stop_state_supported)))
    return _review("kill_switch_integration", score, PaperRuntimeIntegrationRisk.KILL_SWITCH_INTEGRATION_GAP, failed)


def review_human_supervision_integration(data: PaperRuntimeIntegrationReviewInput | Mapping[str, Any]) -> PaperRuntimeIntegrationReview:
    data = _coerce_input(data)
    failed = data.human_supervision_hook_linked is not True or data.human_pause_state_supported is not True or _has_upstream_risk(data, "HUMAN", "SUPERVISION")
    score = data.human_supervision_integration_score if data.human_supervision_integration_score is not None else _average((_bool_score(data.human_supervision_hook_linked), _bool_score(data.human_pause_state_supported)))
    return _review("human_supervision_integration", score, PaperRuntimeIntegrationRisk.HUMAN_SUPERVISION_INTEGRATION_GAP, failed)


def review_runtime_report_integration(data: PaperRuntimeIntegrationReviewInput | Mapping[str, Any]) -> PaperRuntimeIntegrationReview:
    data = _coerce_input(data)
    runtime = data.paper_trading_runtime
    report = _get(runtime, "report")
    failed = data.runtime_report_available is not True or data.runtime_report_complete is not True or report is None or int(_get(report, "journal_count", 0) or 0) <= 0
    score = data.runtime_report_score if data.runtime_report_score is not None else _average((_bool_score(data.runtime_report_available), _bool_score(data.runtime_report_complete), 100 if report is not None else 0))
    return _review("runtime_report_integration", score, PaperRuntimeIntegrationRisk.RUNTIME_REPORT_GAP, failed, (f"report_available={report is not None}",))


def _offline_boundary(data: PaperRuntimeIntegrationReviewInput) -> bool:
    return (
        data.integration_scope_locked is True
        and data.offline_mode_enforced is True
        and data.sandbox_mode_enforced is True
        and data.no_real_broker is True
        and data.no_api_key_read is True
        and data.no_http_transport is True
        and data.no_websocket_transport is True
        and data.no_socket_transport is True
        and data.no_external_api is True
        and data.no_real_order is True
        and _get(data.paper_trading_runtime, "offline_only") is True
        and not _has_upstream_risk(data, "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK", "BROKER", "EXTERNAL_DEPENDENCY")
    )


def detect_integration_review_risks(data: PaperRuntimeIntegrationReviewInput | Mapping[str, Any], *reviews: PaperRuntimeIntegrationReview) -> tuple[PaperRuntimeIntegrationRisk, ...]:
    data = _coerce_input(data)
    if not reviews:
        reviews = (
            review_runtime_design_alignment(data),
            review_decision_review_alignment(data),
            review_full_session_alignment(data),
            review_simulated_market_alignment(data),
            review_mock_alpaca_alignment(data),
            review_mock_connectivity_alignment(data),
            review_observability_integration(data),
            review_rollback_integration(data),
            review_kill_switch_integration(data),
            review_human_supervision_integration(data),
            review_runtime_report_integration(data),
        )
    risks: list[PaperRuntimeIntegrationRisk] = []
    for review in reviews:
        risks.extend(review.risks)
    if not _offline_boundary(data):
        risks.append(PaperRuntimeIntegrationRisk.INTEGRATION_SCOPE_DRIFT)
    return _dedupe(risks)


def compute_integration_review_score(data: PaperRuntimeIntegrationReviewInput | Mapping[str, Any], risks: tuple[PaperRuntimeIntegrationRisk, ...] = (), *reviews: PaperRuntimeIntegrationReview) -> PaperRuntimeIntegrationReviewScore:
    data = _coerce_input(data)
    if not reviews:
        reviews = (
            review_runtime_design_alignment(data),
            review_decision_review_alignment(data),
            review_full_session_alignment(data),
            review_simulated_market_alignment(data),
            review_mock_alpaca_alignment(data),
            review_mock_connectivity_alignment(data),
            review_observability_integration(data),
            review_rollback_integration(data),
            review_kill_switch_integration(data),
            review_human_supervision_integration(data),
            review_runtime_report_integration(data),
        )
    scores = tuple(review.score for review in reviews)
    overall = _clamp(_average(scores) - min(80, len(set(risks)) * 5))
    for risk, cap in {
        PaperRuntimeIntegrationRisk.RUNTIME_DESIGN_MISMATCH: 55,
        PaperRuntimeIntegrationRisk.DECISION_REVIEW_MISMATCH: 55,
        PaperRuntimeIntegrationRisk.OBSERVABILITY_INTEGRATION_GAP: 60,
        PaperRuntimeIntegrationRisk.ROLLBACK_INTEGRATION_GAP: 55,
        PaperRuntimeIntegrationRisk.KILL_SWITCH_INTEGRATION_GAP: 50,
        PaperRuntimeIntegrationRisk.HUMAN_SUPERVISION_INTEGRATION_GAP: 55,
        PaperRuntimeIntegrationRisk.RUNTIME_REPORT_GAP: 60,
        PaperRuntimeIntegrationRisk.INTEGRATION_SCOPE_DRIFT: 40,
    }.items():
        if risk in risks:
            overall = min(overall, cap)
    return PaperRuntimeIntegrationReviewScore(overall, *scores)


def _select_decision(score: int, risks: tuple[PaperRuntimeIntegrationRisk, ...], ready_for_test_run: bool | None) -> PaperRuntimeIntegrationDecision:
    if PaperRuntimeIntegrationRisk.INTEGRATION_SCOPE_DRIFT in risks or score < 45:
        return PaperRuntimeIntegrationDecision.INTEGRATION_BLOCKED
    hard = {
        PaperRuntimeIntegrationRisk.RUNTIME_DESIGN_MISMATCH,
        PaperRuntimeIntegrationRisk.DECISION_REVIEW_MISMATCH,
        PaperRuntimeIntegrationRisk.KILL_SWITCH_INTEGRATION_GAP,
    }
    if hard.intersection(risks):
        return PaperRuntimeIntegrationDecision.INTEGRATION_CLEANUP_REQUIRED
    if len(set(risks)) >= 3:
        return PaperRuntimeIntegrationDecision.INTEGRATION_CLEANUP_REQUIRED
    if risks:
        return PaperRuntimeIntegrationDecision.INTEGRATION_PARTIALLY_READY
    if ready_for_test_run is True and score >= 94:
        return PaperRuntimeIntegrationDecision.READY_FOR_PAPER_RUNTIME_TEST_RUN
    if score >= 85:
        return PaperRuntimeIntegrationDecision.INTEGRATION_READY
    return PaperRuntimeIntegrationDecision.INTEGRATION_PARTIALLY_READY


def _select_state(decision: PaperRuntimeIntegrationDecision, score: int) -> PaperRuntimeIntegrationReviewState:
    if decision == PaperRuntimeIntegrationDecision.INTEGRATION_BLOCKED:
        return PaperRuntimeIntegrationReviewState.NOT_READY
    if decision == PaperRuntimeIntegrationDecision.INTEGRATION_CLEANUP_REQUIRED:
        return PaperRuntimeIntegrationReviewState.REVIEW_REQUIRED
    if decision == PaperRuntimeIntegrationDecision.INTEGRATION_PARTIALLY_READY:
        return PaperRuntimeIntegrationReviewState.PARTIALLY_INTEGRATED
    if decision == PaperRuntimeIntegrationDecision.READY_FOR_PAPER_RUNTIME_TEST_RUN and score >= 94:
        return PaperRuntimeIntegrationReviewState.READY_FOR_PAPER_RUNTIME_TEST_RUN
    return PaperRuntimeIntegrationReviewState.INTEGRATION_READY


def generate_integration_review_recommendations(risks: tuple[PaperRuntimeIntegrationRisk, ...], decision: PaperRuntimeIntegrationDecision | None = None) -> tuple[PaperRuntimeIntegrationRecommendation, ...]:
    recommendations: list[PaperRuntimeIntegrationRecommendation] = []
    if risks:
        recommendations.append(PaperRuntimeIntegrationRecommendation.HOLD_TEST_RUN_APPROVAL)
    mapping = {
        PaperRuntimeIntegrationRisk.RUNTIME_DESIGN_MISMATCH: PaperRuntimeIntegrationRecommendation.ALIGN_RUNTIME_DESIGN,
        PaperRuntimeIntegrationRisk.DECISION_REVIEW_MISMATCH: PaperRuntimeIntegrationRecommendation.ALIGN_DECISION_REVIEW,
        PaperRuntimeIntegrationRisk.FULL_SESSION_MISMATCH: PaperRuntimeIntegrationRecommendation.ALIGN_FULL_SESSION,
        PaperRuntimeIntegrationRisk.SIMULATED_MARKET_MISMATCH: PaperRuntimeIntegrationRecommendation.ALIGN_SIMULATED_MARKET,
        PaperRuntimeIntegrationRisk.MOCK_ALPACA_MISMATCH: PaperRuntimeIntegrationRecommendation.ALIGN_MOCK_ALPACA,
        PaperRuntimeIntegrationRisk.MOCK_CONNECTIVITY_MISMATCH: PaperRuntimeIntegrationRecommendation.ALIGN_MOCK_CONNECTIVITY,
        PaperRuntimeIntegrationRisk.OBSERVABILITY_INTEGRATION_GAP: PaperRuntimeIntegrationRecommendation.REPAIR_OBSERVABILITY_INTEGRATION,
        PaperRuntimeIntegrationRisk.ROLLBACK_INTEGRATION_GAP: PaperRuntimeIntegrationRecommendation.REPAIR_ROLLBACK_INTEGRATION,
        PaperRuntimeIntegrationRisk.KILL_SWITCH_INTEGRATION_GAP: PaperRuntimeIntegrationRecommendation.REPAIR_KILL_SWITCH_INTEGRATION,
        PaperRuntimeIntegrationRisk.HUMAN_SUPERVISION_INTEGRATION_GAP: PaperRuntimeIntegrationRecommendation.REPAIR_HUMAN_SUPERVISION_INTEGRATION,
        PaperRuntimeIntegrationRisk.RUNTIME_REPORT_GAP: PaperRuntimeIntegrationRecommendation.COMPLETE_RUNTIME_REPORT,
        PaperRuntimeIntegrationRisk.INTEGRATION_SCOPE_DRIFT: PaperRuntimeIntegrationRecommendation.LOCK_INTEGRATION_SCOPE,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(PaperRuntimeIntegrationRecommendation.RUN_INTEGRATION_REVIEW_SUITE)
    if decision == PaperRuntimeIntegrationDecision.INTEGRATION_READY:
        recommendations.append(PaperRuntimeIntegrationRecommendation.APPROVE_INTEGRATION_AFTER_MANUAL_REVIEW)
    if decision == PaperRuntimeIntegrationDecision.READY_FOR_PAPER_RUNTIME_TEST_RUN:
        recommendations.append(PaperRuntimeIntegrationRecommendation.APPROVE_TEST_RUN_AFTER_MANUAL_REVIEW)
    return _dedupe(recommendations)


def evaluate_paper_runtime_integration_review(data: PaperRuntimeIntegrationReviewInput | Mapping[str, Any]) -> PaperRuntimeIntegrationReviewResult:
    data = _coerce_input(data)
    reviews = (
        review_runtime_design_alignment(data),
        review_decision_review_alignment(data),
        review_full_session_alignment(data),
        review_simulated_market_alignment(data),
        review_mock_alpaca_alignment(data),
        review_mock_connectivity_alignment(data),
        review_observability_integration(data),
        review_rollback_integration(data),
        review_kill_switch_integration(data),
        review_human_supervision_integration(data),
        review_runtime_report_integration(data),
    )
    risks = detect_integration_review_risks(data, *reviews)
    score = compute_integration_review_score(data, risks, *reviews)
    decision = _select_decision(score.overall_score, risks, data.ready_for_test_run)
    state = _select_state(decision, score.overall_score)
    recommendations = generate_integration_review_recommendations(risks, decision)
    offline_only = _offline_boundary(data)
    summary = f"{state.value}: decision={decision.value}, score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return PaperRuntimeIntegrationReviewResult(state, decision, score.overall_score, score, risks, *reviews, recommendations, offline_only, summary)


def render_paper_runtime_integration_review_markdown(result: PaperRuntimeIntegrationReviewResult) -> str:
    lines = [
        "# AGIcore Paper Runtime Integration Review",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Score: {result.integration_review_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Integration Reviews",
    ]
    reviews = (
        result.runtime_design_alignment,
        result.decision_review_alignment,
        result.full_session_alignment,
        result.simulated_market_alignment,
        result.mock_alpaca_alignment,
        result.mock_connectivity_alignment,
        result.observability_integration,
        result.rollback_integration,
        result.kill_switch_integration,
        result.human_supervision_integration,
        result.runtime_report_integration,
    )
    for review in reviews:
        lines.append(f"- {review.name}: passed={review.passed}, score={review.score}/100, risks={', '.join(risk.value for risk in review.risks) or 'none'}")
        lines.extend(f"  - {detail}" for detail in review.details)
    lines.append("")
    lines.append("# Integration Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Integration Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_integration_review_score",
    "detect_integration_review_risks",
    "evaluate_paper_runtime_integration_review",
    "generate_integration_review_recommendations",
    "render_paper_runtime_integration_review_markdown",
    "review_decision_review_alignment",
    "review_full_session_alignment",
    "review_human_supervision_integration",
    "review_kill_switch_integration",
    "review_mock_alpaca_alignment",
    "review_mock_connectivity_alignment",
    "review_observability_integration",
    "review_rollback_integration",
    "review_runtime_design_alignment",
    "review_runtime_report_integration",
    "review_simulated_market_alignment",
]
