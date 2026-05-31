"""Offline decision review for AGIcore Paper Trading Runtime creation."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_runtime_decision_review_models import (
    PaperRuntimeDecision,
    PaperRuntimeDecisionRecommendation,
    PaperRuntimeDecisionReview,
    PaperRuntimeDecisionReviewInput,
    PaperRuntimeDecisionReviewResult,
    PaperRuntimeDecisionReviewScore,
    PaperRuntimeDecisionReviewState,
    PaperRuntimeDecisionRisk,
)


def _coerce_input(data: PaperRuntimeDecisionReviewInput | Mapping[str, Any]) -> PaperRuntimeDecisionReviewInput:
    if isinstance(data, PaperRuntimeDecisionReviewInput):
        return data
    return PaperRuntimeDecisionReviewInput(**dict(data))


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


def _average(values: Iterable[int | float | None], default: int = 0) -> int:
    usable = [float(value) for value in values if value is not None]
    if not usable:
        return default
    return _clamp(sum(usable) / len(usable))


def _bool_score(value: bool | None, unknown: int = 45) -> int:
    if value is True:
        return 100
    if value is False:
        return 0
    return unknown


def _dedupe(items: Iterable[Any]) -> tuple[Any, ...]:
    seen: set[Any] = set()
    result: list[Any] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return tuple(result)


def _upstream_items(data: PaperRuntimeDecisionReviewInput) -> tuple[Any, ...]:
    return (
        data.paper_runtime_pre_review,
        data.full_paper_session,
        data.simulated_market_session,
        data.mock_alpaca_session,
        data.mock_connectivity_layer,
        data.alpaca_paper_connectivity_readiness,
        data.broker_paper_sandbox,
        data.paper_trading_end_to_end,
        data.paper_dry_run,
        data.supervised_paper_trial,
        data.observability_verification,
        data.rollback_verification,
        data.kill_switch_verification,
        data.human_validated_paper_session,
        data.supervised_paper_session,
    )


def _upstream_risks(data: PaperRuntimeDecisionReviewInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperRuntimeDecisionReviewInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _missing(required: tuple[str, ...], declared: tuple[str, ...]) -> tuple[str, ...]:
    declared_lower = {item.lower() for item in declared}
    return tuple(item for item in required if item.lower() not in declared_lower)


def _review(name: str, score: int, risk: PaperRuntimeDecisionRisk, failed: bool, details: tuple[str, ...] = ()) -> PaperRuntimeDecisionReview:
    risks = (risk,) if failed or score < 85 else ()
    return PaperRuntimeDecisionReview(name, _clamp(score), not risks and score >= 85, risks, details)


def review_module_coherence(data: PaperRuntimeDecisionReviewInput | Mapping[str, Any]) -> PaperRuntimeDecisionReview:
    data = _coerce_input(data)
    required = ("pre_review", "full_paper", "simulated_market", "mock", "sandbox", "paper")
    missing = tuple(item for item in required if not any(item in layer.lower() for layer in data.module_layers))
    score = data.module_coherence_score if data.module_coherence_score is not None else _clamp(100 - len(missing) * 12)
    failed = data.coherent_module_chain is not True or bool(missing) or _has_upstream_risk(data, "MODULE", "COHERENCE")
    return _review("module_coherence", score, PaperRuntimeDecisionRisk.MODULE_COHERENCE_GAP, failed, missing)


def review_duplicate_layers(data: PaperRuntimeDecisionReviewInput | Mapping[str, Any]) -> PaperRuntimeDecisionReview:
    data = _coerce_input(data)
    lowered = [layer.lower() for layer in data.module_layers]
    natural = tuple(sorted({layer for layer in lowered if lowered.count(layer) > 1}))
    details = tuple(data.duplicate_layers) + natural
    failed = bool(details) or _has_upstream_risk(data, "DUPLICATE")
    score = data.duplicate_score if data.duplicate_score is not None else (55 if failed else 100)
    return _review("duplicate_layers", score, PaperRuntimeDecisionRisk.DUPLICATE_LAYER_CONFLICT, failed, details)


def review_runtime_entrypoints(data: PaperRuntimeDecisionReviewInput | Mapping[str, Any]) -> PaperRuntimeDecisionReview:
    data = _coerce_input(data)
    missing = _missing(data.runtime_entrypoints_required, data.runtime_entrypoints)
    failed = bool(missing) or not data.runtime_entrypoints or _has_upstream_risk(data, "ENTRYPOINT")
    score = data.entrypoint_score if data.entrypoint_score is not None else _clamp(100 - len(missing) * 20 - (0 if data.runtime_entrypoints else 25))
    return _review("runtime_entrypoints", score, PaperRuntimeDecisionRisk.ENTRYPOINT_AMBIGUITY, failed, missing)


def review_safety_chain(data: PaperRuntimeDecisionReviewInput | Mapping[str, Any]) -> PaperRuntimeDecisionReview:
    data = _coerce_input(data)
    required = ("safety_gate", "risk_management", "kill_switch")
    missing = _missing(required, data.safety_chain_links)
    failed = bool(missing) or _has_upstream_risk(data, "SAFETY")
    score = data.safety_chain_score if data.safety_chain_score is not None else _clamp(100 - len(missing) * 18)
    return _review("safety_chain", score, PaperRuntimeDecisionRisk.SAFETY_CHAIN_INCOMPLETE, failed, missing)


def review_rollback_chain(data: PaperRuntimeDecisionReviewInput | Mapping[str, Any]) -> PaperRuntimeDecisionReview:
    data = _coerce_input(data)
    required = ("checkpoint", "restore", "rollback")
    missing = _missing(required, data.rollback_chain_links)
    failed = bool(missing) or _has_upstream_risk(data, "ROLLBACK")
    score = data.rollback_chain_score if data.rollback_chain_score is not None else _clamp(100 - len(missing) * 20)
    return _review("rollback_chain", score, PaperRuntimeDecisionRisk.ROLLBACK_CHAIN_INCOMPLETE, failed, missing)


def review_observability_chain(data: PaperRuntimeDecisionReviewInput | Mapping[str, Any]) -> PaperRuntimeDecisionReview:
    data = _coerce_input(data)
    required = ("logs", "metrics", "traces", "alerts")
    missing = _missing(required, data.observability_chain_links)
    failed = bool(missing) or _has_upstream_risk(data, "OBSERVABILITY")
    score = data.observability_chain_score if data.observability_chain_score is not None else _clamp(100 - len(missing) * 15)
    return _review("observability_chain", score, PaperRuntimeDecisionRisk.OBSERVABILITY_CHAIN_INCOMPLETE, failed, missing)


def review_human_supervision_chain(data: PaperRuntimeDecisionReviewInput | Mapping[str, Any]) -> PaperRuntimeDecisionReview:
    data = _coerce_input(data)
    required = ("human_approval", "operator_confirmation", "supervision")
    missing = _missing(required, data.human_supervision_links)
    failed = bool(missing) or _has_upstream_risk(data, "HUMAN", "SUPERVISION")
    score = data.human_supervision_score if data.human_supervision_score is not None else _clamp(100 - len(missing) * 20)
    return _review("human_supervision_chain", score, PaperRuntimeDecisionRisk.HUMAN_SUPERVISION_GAP, failed, missing)


def review_mock_to_paper_transition(data: PaperRuntimeDecisionReviewInput | Mapping[str, Any]) -> PaperRuntimeDecisionReview:
    data = _coerce_input(data)
    required = ("mock_connectivity", "mock_alpaca", "broker_sandbox", "paper_runtime")
    missing = _missing(required, data.mock_to_paper_transition_links)
    failed = bool(missing) or _has_upstream_risk(data, "MOCK_TO_PAPER", "TRANSITION")
    score = data.mock_to_paper_transition_score if data.mock_to_paper_transition_score is not None else _clamp(100 - len(missing) * 15)
    return _review("mock_to_paper_transition", score, PaperRuntimeDecisionRisk.MOCK_TO_PAPER_TRANSITION_GAP, failed, missing)


def review_runtime_readiness_decision(data: PaperRuntimeDecisionReviewInput | Mapping[str, Any]) -> PaperRuntimeDecisionReview:
    data = _coerce_input(data)
    failed = (
        data.runtime_scope_locked is not True
        or data.no_runtime_implementation_created is not True
        or bool(data.integration_gaps)
        or _has_upstream_risk(data, "RUNTIME_SCOPE", "PREMATURE_RUNTIME", "INTEGRATION")
    )
    risks: list[PaperRuntimeDecisionRisk] = []
    details: list[str] = []
    if data.runtime_scope_locked is not True:
        risks.append(PaperRuntimeDecisionRisk.RUNTIME_SCOPE_UNCLEAR)
        details.append("runtime_scope_unlocked")
    if data.no_runtime_implementation_created is not True:
        risks.append(PaperRuntimeDecisionRisk.PREMATURE_RUNTIME_CREATION)
        details.append("runtime_implementation_already_started")
    if data.integration_gaps or _has_upstream_risk(data, "INTEGRATION"):
        risks.append(PaperRuntimeDecisionRisk.MOCK_TO_PAPER_TRANSITION_GAP)
        details.extend(data.integration_gaps)
    score = data.runtime_decision_score if data.runtime_decision_score is not None else (55 if failed else 100)
    return PaperRuntimeDecisionReview("runtime_readiness_decision", _clamp(score), not risks and score >= 85, _dedupe(risks), tuple(details))


def detect_decision_review_risks(data: PaperRuntimeDecisionReviewInput | Mapping[str, Any], *reviews: PaperRuntimeDecisionReview) -> tuple[PaperRuntimeDecisionRisk, ...]:
    data = _coerce_input(data)
    if not reviews:
        reviews = (
            review_runtime_readiness_decision(data),
            review_module_coherence(data),
            review_duplicate_layers(data),
            review_runtime_entrypoints(data),
            review_safety_chain(data),
            review_rollback_chain(data),
            review_observability_chain(data),
            review_human_supervision_chain(data),
            review_mock_to_paper_transition(data),
        )
    risks: list[PaperRuntimeDecisionRisk] = []
    for review in reviews:
        risks.extend(review.risks)
    if (
        data.offline_mode_enforced is not True
        or data.no_real_broker is not True
        or data.no_api_key_read is not True
        or data.no_http_transport is not True
        or data.no_websocket_transport is not True
        or data.no_socket_transport is not True
        or data.no_external_api is not True
        or data.no_real_order is not True
        or _has_upstream_risk(data, "BROKER", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK", "EXTERNAL_DEPENDENCY")
    ):
        risks.append(PaperRuntimeDecisionRisk.RUNTIME_SCOPE_UNCLEAR)
    return _dedupe(risks)


def compute_decision_review_score(data: PaperRuntimeDecisionReviewInput | Mapping[str, Any], risks: tuple[PaperRuntimeDecisionRisk, ...] = (), *reviews: PaperRuntimeDecisionReview) -> PaperRuntimeDecisionReviewScore:
    data = _coerce_input(data)
    if not reviews:
        reviews = (
            review_runtime_readiness_decision(data),
            review_module_coherence(data),
            review_duplicate_layers(data),
            review_runtime_entrypoints(data),
            review_safety_chain(data),
            review_rollback_chain(data),
            review_observability_chain(data),
            review_human_supervision_chain(data),
            review_mock_to_paper_transition(data),
        )
    scores = tuple(review.score for review in reviews)
    base = _average(scores + (_bool_score(data.design_review_approved),))
    overall = _clamp(base - min(75, len(set(risks)) * 6))
    for risk, cap in {
        PaperRuntimeDecisionRisk.DUPLICATE_LAYER_CONFLICT: 55,
        PaperRuntimeDecisionRisk.ENTRYPOINT_AMBIGUITY: 55,
        PaperRuntimeDecisionRisk.SAFETY_CHAIN_INCOMPLETE: 50,
        PaperRuntimeDecisionRisk.ROLLBACK_CHAIN_INCOMPLETE: 50,
        PaperRuntimeDecisionRisk.OBSERVABILITY_CHAIN_INCOMPLETE: 55,
        PaperRuntimeDecisionRisk.HUMAN_SUPERVISION_GAP: 55,
        PaperRuntimeDecisionRisk.MOCK_TO_PAPER_TRANSITION_GAP: 60,
        PaperRuntimeDecisionRisk.RUNTIME_SCOPE_UNCLEAR: 40,
        PaperRuntimeDecisionRisk.PREMATURE_RUNTIME_CREATION: 35,
    }.items():
        if risk in risks:
            overall = min(overall, cap)
    return PaperRuntimeDecisionReviewScore(overall, *(scores[1:] + (scores[0],)))


def _select_decision(risks: tuple[PaperRuntimeDecisionRisk, ...], score: int, design: bool | None, creation: bool | None) -> PaperRuntimeDecision:
    if PaperRuntimeDecisionRisk.PREMATURE_RUNTIME_CREATION in risks or PaperRuntimeDecisionRisk.RUNTIME_SCOPE_UNCLEAR in risks or score < 45:
        return PaperRuntimeDecision.BLOCK_RUNTIME_CREATION
    if PaperRuntimeDecisionRisk.ENTRYPOINT_AMBIGUITY in risks:
        return PaperRuntimeDecision.REQUIRE_ENTRYPOINT_FIXES
    if PaperRuntimeDecisionRisk.DUPLICATE_LAYER_CONFLICT in risks:
        return PaperRuntimeDecision.REQUIRE_DUPLICATE_REDUCTION
    cleanup = {
        PaperRuntimeDecisionRisk.MODULE_COHERENCE_GAP,
        PaperRuntimeDecisionRisk.SAFETY_CHAIN_INCOMPLETE,
        PaperRuntimeDecisionRisk.ROLLBACK_CHAIN_INCOMPLETE,
        PaperRuntimeDecisionRisk.OBSERVABILITY_CHAIN_INCOMPLETE,
        PaperRuntimeDecisionRisk.HUMAN_SUPERVISION_GAP,
        PaperRuntimeDecisionRisk.MOCK_TO_PAPER_TRANSITION_GAP,
    }
    if cleanup.intersection(risks):
        return PaperRuntimeDecision.REQUIRE_INTEGRATION_CLEANUP
    if creation is True and score >= 94:
        return PaperRuntimeDecision.APPROVE_PAPER_TRADING_RUNTIME_CREATION
    if design is True and score >= 85:
        return PaperRuntimeDecision.APPROVE_PAPER_RUNTIME_DESIGN
    return PaperRuntimeDecision.REQUIRE_INTEGRATION_CLEANUP


def _select_state(decision: PaperRuntimeDecision, risks: tuple[PaperRuntimeDecisionRisk, ...], score: int) -> PaperRuntimeDecisionReviewState:
    if decision == PaperRuntimeDecision.BLOCK_RUNTIME_CREATION:
        return PaperRuntimeDecisionReviewState.NOT_READY
    if decision in {PaperRuntimeDecision.REQUIRE_INTEGRATION_CLEANUP, PaperRuntimeDecision.REQUIRE_ENTRYPOINT_FIXES, PaperRuntimeDecision.REQUIRE_DUPLICATE_REDUCTION}:
        return PaperRuntimeDecisionReviewState.BLOCKED_BY_INTEGRATION_GAPS if len(set(risks)) >= 3 else PaperRuntimeDecisionReviewState.REVIEW_REQUIRED
    if decision == PaperRuntimeDecision.APPROVE_PAPER_TRADING_RUNTIME_CREATION and score >= 94:
        return PaperRuntimeDecisionReviewState.READY_FOR_PAPER_TRADING_RUNTIME
    if decision == PaperRuntimeDecision.APPROVE_PAPER_RUNTIME_DESIGN and score >= 85:
        return PaperRuntimeDecisionReviewState.READY_FOR_PAPER_RUNTIME_DESIGN
    return PaperRuntimeDecisionReviewState.PARTIALLY_READY


def generate_decision_review_recommendations(risks: tuple[PaperRuntimeDecisionRisk, ...], decision: PaperRuntimeDecision | None = None) -> tuple[PaperRuntimeDecisionRecommendation, ...]:
    recommendations: list[PaperRuntimeDecisionRecommendation] = []
    if risks:
        recommendations.append(PaperRuntimeDecisionRecommendation.BLOCK_PAPER_RUNTIME_CREATION)
    mapping = {
        PaperRuntimeDecisionRisk.MODULE_COHERENCE_GAP: PaperRuntimeDecisionRecommendation.REPAIR_MODULE_COHERENCE,
        PaperRuntimeDecisionRisk.DUPLICATE_LAYER_CONFLICT: PaperRuntimeDecisionRecommendation.REDUCE_DUPLICATE_LAYERS,
        PaperRuntimeDecisionRisk.ENTRYPOINT_AMBIGUITY: PaperRuntimeDecisionRecommendation.CLARIFY_RUNTIME_ENTRYPOINTS,
        PaperRuntimeDecisionRisk.SAFETY_CHAIN_INCOMPLETE: PaperRuntimeDecisionRecommendation.COMPLETE_SAFETY_CHAIN,
        PaperRuntimeDecisionRisk.ROLLBACK_CHAIN_INCOMPLETE: PaperRuntimeDecisionRecommendation.COMPLETE_ROLLBACK_CHAIN,
        PaperRuntimeDecisionRisk.OBSERVABILITY_CHAIN_INCOMPLETE: PaperRuntimeDecisionRecommendation.COMPLETE_OBSERVABILITY_CHAIN,
        PaperRuntimeDecisionRisk.HUMAN_SUPERVISION_GAP: PaperRuntimeDecisionRecommendation.COMPLETE_HUMAN_SUPERVISION_CHAIN,
        PaperRuntimeDecisionRisk.MOCK_TO_PAPER_TRANSITION_GAP: PaperRuntimeDecisionRecommendation.COMPLETE_MOCK_TO_PAPER_TRANSITION,
        PaperRuntimeDecisionRisk.RUNTIME_SCOPE_UNCLEAR: PaperRuntimeDecisionRecommendation.LOCK_RUNTIME_SCOPE,
        PaperRuntimeDecisionRisk.PREMATURE_RUNTIME_CREATION: PaperRuntimeDecisionRecommendation.KEEP_RUNTIME_CREATION_BLOCKED,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(PaperRuntimeDecisionRecommendation.RUN_PAPER_RUNTIME_DECISION_REVIEW_SUITE)
    if decision == PaperRuntimeDecision.APPROVE_PAPER_RUNTIME_DESIGN:
        recommendations.append(PaperRuntimeDecisionRecommendation.APPROVE_RUNTIME_DESIGN_REVIEW)
    if decision == PaperRuntimeDecision.APPROVE_PAPER_TRADING_RUNTIME_CREATION:
        recommendations.append(PaperRuntimeDecisionRecommendation.APPROVE_RUNTIME_CREATION_AFTER_MANUAL_REVIEW)
    return _dedupe(recommendations)


def evaluate_paper_runtime_decision_review(data: PaperRuntimeDecisionReviewInput | Mapping[str, Any]) -> PaperRuntimeDecisionReviewResult:
    data = _coerce_input(data)
    reviews = (
        review_runtime_readiness_decision(data),
        review_module_coherence(data),
        review_duplicate_layers(data),
        review_runtime_entrypoints(data),
        review_safety_chain(data),
        review_rollback_chain(data),
        review_observability_chain(data),
        review_human_supervision_chain(data),
        review_mock_to_paper_transition(data),
    )
    risks = detect_decision_review_risks(data, *reviews)
    score = compute_decision_review_score(data, risks, *reviews)
    decision = _select_decision(risks, score.overall_score, data.design_review_approved, data.runtime_creation_approved)
    state = _select_state(decision, risks, score.overall_score)
    recommendations = generate_decision_review_recommendations(risks, decision)
    offline_only = (
        data.offline_mode_enforced is True
        and data.no_real_broker is True
        and data.no_api_key_read is True
        and data.no_http_transport is True
        and data.no_websocket_transport is True
        and data.no_socket_transport is True
        and data.no_external_api is True
        and data.no_real_order is True
        and data.no_runtime_implementation_created is True
        and not _has_upstream_risk(data, "BROKER", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK", "EXTERNAL_DEPENDENCY")
    )
    summary = f"{state.value}: decision={decision.value}, score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return PaperRuntimeDecisionReviewResult(
        state, decision, score.overall_score, score, risks,
        reviews[0], reviews[1], reviews[2], reviews[3], reviews[4], reviews[5],
        reviews[6], reviews[7], reviews[8], recommendations, offline_only, summary,
    )


def render_paper_runtime_decision_review_markdown(result: PaperRuntimeDecisionReviewResult) -> str:
    lines = [
        "# AGIcore Paper Trading Runtime Decision Review",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Score: {result.decision_review_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Score Breakdown",
        f"- Module coherence: {result.score_breakdown.module_coherence_score}/100",
        f"- Duplicates: {result.score_breakdown.duplicate_score}/100",
        f"- Entrypoints: {result.score_breakdown.entrypoint_score}/100",
        f"- Safety chain: {result.score_breakdown.safety_chain_score}/100",
        f"- Rollback chain: {result.score_breakdown.rollback_chain_score}/100",
        f"- Observability chain: {result.score_breakdown.observability_chain_score}/100",
        f"- Human supervision: {result.score_breakdown.human_supervision_score}/100",
        f"- Mock to paper: {result.score_breakdown.mock_to_paper_transition_score}/100",
        f"- Runtime decision: {result.score_breakdown.runtime_decision_score}/100",
        "",
        "# Decision Reviews",
    ]
    reviews = (
        result.runtime_readiness_decision,
        result.module_coherence,
        result.duplicate_layers,
        result.runtime_entrypoints,
        result.safety_chain,
        result.rollback_chain,
        result.observability_chain,
        result.human_supervision_chain,
        result.mock_to_paper_transition,
    )
    for review in reviews:
        lines.append(f"- {review.name}: passed={review.passed}, score={review.score}/100, risks={', '.join(risk.value for risk in review.risks) or 'none'}")
        lines.extend(f"  - {detail}" for detail in review.details)
    lines.append("")
    lines.append("# Decision Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Decision Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_decision_review_score",
    "detect_decision_review_risks",
    "evaluate_paper_runtime_decision_review",
    "generate_decision_review_recommendations",
    "render_paper_runtime_decision_review_markdown",
    "review_duplicate_layers",
    "review_human_supervision_chain",
    "review_mock_to_paper_transition",
    "review_module_coherence",
    "review_observability_chain",
    "review_rollback_chain",
    "review_runtime_entrypoints",
    "review_runtime_readiness_decision",
    "review_safety_chain",
]
