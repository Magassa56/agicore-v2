"""Offline paper trading runtime pre-review for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_runtime_pre_review_models import (
    PaperRuntimeModuleMap,
    PaperRuntimePreReviewInput,
    PaperRuntimePreReviewRecommendation,
    PaperRuntimePreReviewResult,
    PaperRuntimePreReviewRisk,
    PaperRuntimePreReviewScore,
    PaperRuntimePreReviewState,
    PaperRuntimeReview,
)

EXPECTED_MODULE_KEYWORDS = (
    "full_paper_session",
    "simulated_market_session",
    "mock_alpaca_session",
    "mock_connectivity_layer",
    "paper_trading_end_to_end",
    "paper_dry_run",
    "supervised_paper_trial",
    "observability",
    "rollback",
    "kill_switch",
)


def _coerce_input(data: PaperRuntimePreReviewInput | Mapping[str, Any]) -> PaperRuntimePreReviewInput:
    if isinstance(data, PaperRuntimePreReviewInput):
        return data
    return PaperRuntimePreReviewInput(**dict(data))


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


def _upstream_items(data: PaperRuntimePreReviewInput) -> tuple[Any, ...]:
    return (
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
    )


def _upstream_risks(data: PaperRuntimePreReviewInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperRuntimePreReviewInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _missing(required: tuple[str, ...], declared: tuple[str, ...]) -> tuple[str, ...]:
    declared_lower = {item.lower() for item in declared}
    return tuple(item for item in required if item.lower() not in declared_lower)


def _category(module: str) -> str:
    lowered = module.lower()
    if "runtime" in lowered:
        return "runtime"
    if "session" in lowered:
        return "session"
    if "adapter" in lowered or "connectivity" in lowered or "sandbox" in lowered:
        return "connectivity"
    if "observability" in lowered or "rollback" in lowered or "kill" in lowered or "safety" in lowered:
        return "safety"
    return "support"


def map_trading_modules(data: PaperRuntimePreReviewInput | Mapping[str, Any]) -> PaperRuntimeModuleMap:
    data = _coerce_input(data)
    modules = _dedupe(data.trading_modules)
    runtime_candidates = _dedupe(data.runtime_candidates)
    categories = tuple((module, _category(module)) for module in modules)
    missing_expected = tuple(
        keyword for keyword in EXPECTED_MODULE_KEYWORDS if not any(keyword in module.lower() for module in modules)
    )
    score = data.module_map_score if data.module_map_score is not None else _clamp(
        100 - len(missing_expected) * 8 - (0 if modules else 40) - (0 if runtime_candidates else 10)
    )
    risks = (PaperRuntimePreReviewRisk.MODULE_MAP_INCOMPLETE,) if missing_expected or not modules else ()
    return PaperRuntimeModuleMap(modules, runtime_candidates, categories, missing_expected, _clamp(score), risks)


def detect_runtime_duplicates(data: PaperRuntimePreReviewInput | Mapping[str, Any]) -> PaperRuntimeReview:
    data = _coerce_input(data)
    lowered = [module.lower() for module in data.runtime_candidates]
    natural_duplicates = tuple(sorted({module for module in lowered if lowered.count(module) > 1}))
    declared = tuple(data.duplicate_layers)
    duplicate_runtime_candidates = len(set(lowered)) < len(lowered) or len(data.runtime_candidates) > 1
    has_duplicates = bool(declared or natural_duplicates or duplicate_runtime_candidates)
    score = data.duplicate_score if data.duplicate_score is not None else (55 if has_duplicates else 100)
    risks = (PaperRuntimePreReviewRisk.DUPLICATE_RUNTIME_LAYER,) if has_duplicates else ()
    details = declared + natural_duplicates
    if duplicate_runtime_candidates and not details:
        details = tuple(data.runtime_candidates)
    return PaperRuntimeReview("duplicates", _clamp(score), not risks and score >= 85, risks, details)


def review_runtime_dependencies(data: PaperRuntimePreReviewInput | Mapping[str, Any]) -> PaperRuntimeReview:
    data = _coerce_input(data)
    missing = _missing(data.dependencies_required, data.dependencies_declared)
    score = data.dependency_score if data.dependency_score is not None else _clamp(100 - len(missing) * 15)
    risks = (PaperRuntimePreReviewRisk.DEPENDENCY_GAP,) if missing or score < 85 else ()
    return PaperRuntimeReview("dependencies", _clamp(score), not risks and score >= 85, risks, missing)


def review_runtime_entrypoints(data: PaperRuntimePreReviewInput | Mapping[str, Any]) -> PaperRuntimeReview:
    data = _coerce_input(data)
    missing = _missing(data.entrypoints_required, data.entrypoints_declared)
    score = data.entrypoint_score if data.entrypoint_score is not None else _clamp(100 - len(missing) * 20)
    risks = (PaperRuntimePreReviewRisk.ENTRYPOINT_MISSING,) if missing or not data.entrypoints_declared or score < 85 else ()
    return PaperRuntimeReview("entrypoints", _clamp(score), not risks and score >= 85, risks, missing)


def review_runtime_integration_gaps(data: PaperRuntimePreReviewInput | Mapping[str, Any]) -> PaperRuntimeReview:
    data = _coerce_input(data)
    risks: list[PaperRuntimePreReviewRisk] = []
    if data.integration_gaps:
        risks.append(PaperRuntimePreReviewRisk.INTEGRATION_GAP)
    if not data.observability_links or _has_upstream_risk(data, "OBSERVABILITY"):
        risks.append(PaperRuntimePreReviewRisk.OBSERVABILITY_GAP)
    if not data.safety_links or _has_upstream_risk(data, "SAFETY"):
        risks.append(PaperRuntimePreReviewRisk.SAFETY_LINK_MISSING)
    if not data.rollback_links or _has_upstream_risk(data, "ROLLBACK"):
        risks.append(PaperRuntimePreReviewRisk.ROLLBACK_LINK_MISSING)
    if not data.kill_switch_links or _has_upstream_risk(data, "KILL_SWITCH"):
        risks.append(PaperRuntimePreReviewRisk.KILL_SWITCH_LINK_MISSING)
    if data.runtime_scope_locked is not True or data.no_runtime_implementation_created is not True:
        risks.append(PaperRuntimePreReviewRisk.RUNTIME_SCOPE_DRIFT)
    score = data.integration_score if data.integration_score is not None else _clamp(100 - len(set(risks)) * 11)
    return PaperRuntimeReview("integration_gaps", _clamp(score), not risks and score >= 85, _dedupe(risks), data.integration_gaps)


def detect_pre_review_risks(
    data: PaperRuntimePreReviewInput | Mapping[str, Any],
    module_map: PaperRuntimeModuleMap | None = None,
    duplicate_review: PaperRuntimeReview | None = None,
    dependency_review: PaperRuntimeReview | None = None,
    entrypoint_review: PaperRuntimeReview | None = None,
    integration_gap_review: PaperRuntimeReview | None = None,
) -> tuple[PaperRuntimePreReviewRisk, ...]:
    data = _coerce_input(data)
    module_map = module_map or map_trading_modules(data)
    duplicate_review = duplicate_review or detect_runtime_duplicates(data)
    dependency_review = dependency_review or review_runtime_dependencies(data)
    entrypoint_review = entrypoint_review or review_runtime_entrypoints(data)
    integration_gap_review = integration_gap_review or review_runtime_integration_gaps(data)
    risks: list[PaperRuntimePreReviewRisk] = []
    risks.extend(module_map.risks)
    risks.extend(duplicate_review.risks)
    risks.extend(dependency_review.risks)
    risks.extend(entrypoint_review.risks)
    risks.extend(integration_gap_review.risks)
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
        risks.append(PaperRuntimePreReviewRisk.RUNTIME_SCOPE_DRIFT)
    return _dedupe(risks)


def compute_pre_review_score(
    data: PaperRuntimePreReviewInput | Mapping[str, Any],
    risks: tuple[PaperRuntimePreReviewRisk, ...] = (),
    module_map: PaperRuntimeModuleMap | None = None,
    duplicate_review: PaperRuntimeReview | None = None,
    dependency_review: PaperRuntimeReview | None = None,
    entrypoint_review: PaperRuntimeReview | None = None,
    integration_gap_review: PaperRuntimeReview | None = None,
) -> PaperRuntimePreReviewScore:
    data = _coerce_input(data)
    module_map = module_map or map_trading_modules(data)
    duplicate_review = duplicate_review or detect_runtime_duplicates(data)
    dependency_review = dependency_review or review_runtime_dependencies(data)
    entrypoint_review = entrypoint_review or review_runtime_entrypoints(data)
    integration_gap_review = integration_gap_review or review_runtime_integration_gaps(data)
    base = _average(
        (
            module_map.score,
            duplicate_review.score,
            dependency_review.score,
            entrypoint_review.score,
            integration_gap_review.score,
            _bool_score(data.pre_review_validated),
        )
    )
    overall = _clamp(base - min(70, len(set(risks)) * 6))
    for risk, cap in {
        PaperRuntimePreReviewRisk.DUPLICATE_RUNTIME_LAYER: 55,
        PaperRuntimePreReviewRisk.ENTRYPOINT_MISSING: 60,
        PaperRuntimePreReviewRisk.SAFETY_LINK_MISSING: 55,
        PaperRuntimePreReviewRisk.ROLLBACK_LINK_MISSING: 55,
        PaperRuntimePreReviewRisk.KILL_SWITCH_LINK_MISSING: 50,
        PaperRuntimePreReviewRisk.RUNTIME_SCOPE_DRIFT: 40,
    }.items():
        if risk in risks:
            overall = min(overall, cap)
    return PaperRuntimePreReviewScore(
        overall,
        module_map.score,
        duplicate_review.score,
        dependency_review.score,
        entrypoint_review.score,
        integration_gap_review.score,
    )


def _select_state(score: int, risks: tuple[PaperRuntimePreReviewRisk, ...], ready_for_runtime: bool | None) -> PaperRuntimePreReviewState:
    hard = {
        PaperRuntimePreReviewRisk.DUPLICATE_RUNTIME_LAYER,
        PaperRuntimePreReviewRisk.ENTRYPOINT_MISSING,
        PaperRuntimePreReviewRisk.SAFETY_LINK_MISSING,
        PaperRuntimePreReviewRisk.ROLLBACK_LINK_MISSING,
        PaperRuntimePreReviewRisk.KILL_SWITCH_LINK_MISSING,
        PaperRuntimePreReviewRisk.RUNTIME_SCOPE_DRIFT,
    }
    if hard.intersection(risks) or score < 45:
        return PaperRuntimePreReviewState.NOT_READY
    if len(set(risks)) >= 3 or score < 72:
        return PaperRuntimePreReviewState.REVIEW_REQUIRED
    if risks:
        return PaperRuntimePreReviewState.PARTIALLY_READY
    if ready_for_runtime is True and score >= 94:
        return PaperRuntimePreReviewState.READY_FOR_PAPER_TRADING_RUNTIME
    if score >= 85:
        return PaperRuntimePreReviewState.RUNTIME_PRE_REVIEW_READY
    return PaperRuntimePreReviewState.PARTIALLY_READY


def generate_pre_review_recommendations(
    risks: tuple[PaperRuntimePreReviewRisk, ...],
    state: PaperRuntimePreReviewState | None = None,
) -> tuple[PaperRuntimePreReviewRecommendation, ...]:
    recommendations: list[PaperRuntimePreReviewRecommendation] = []
    if risks:
        recommendations.append(PaperRuntimePreReviewRecommendation.HOLD_RUNTIME_IMPLEMENTATION)
    mapping = {
        PaperRuntimePreReviewRisk.MODULE_MAP_INCOMPLETE: PaperRuntimePreReviewRecommendation.COMPLETE_TRADING_MODULE_MAP,
        PaperRuntimePreReviewRisk.DUPLICATE_RUNTIME_LAYER: PaperRuntimePreReviewRecommendation.CONSOLIDATE_DUPLICATE_RUNTIME_LAYERS,
        PaperRuntimePreReviewRisk.DEPENDENCY_GAP: PaperRuntimePreReviewRecommendation.RESOLVE_RUNTIME_DEPENDENCIES,
        PaperRuntimePreReviewRisk.ENTRYPOINT_MISSING: PaperRuntimePreReviewRecommendation.DEFINE_RUNTIME_ENTRYPOINTS,
        PaperRuntimePreReviewRisk.INTEGRATION_GAP: PaperRuntimePreReviewRecommendation.CLOSE_RUNTIME_INTEGRATION_GAPS,
        PaperRuntimePreReviewRisk.OBSERVABILITY_GAP: PaperRuntimePreReviewRecommendation.RESTORE_RUNTIME_OBSERVABILITY,
        PaperRuntimePreReviewRisk.SAFETY_LINK_MISSING: PaperRuntimePreReviewRecommendation.LINK_RUNTIME_SAFETY_GATE,
        PaperRuntimePreReviewRisk.ROLLBACK_LINK_MISSING: PaperRuntimePreReviewRecommendation.LINK_RUNTIME_ROLLBACK,
        PaperRuntimePreReviewRisk.KILL_SWITCH_LINK_MISSING: PaperRuntimePreReviewRecommendation.LINK_RUNTIME_KILL_SWITCH,
        PaperRuntimePreReviewRisk.RUNTIME_SCOPE_DRIFT: PaperRuntimePreReviewRecommendation.FREEZE_RUNTIME_SCOPE,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(PaperRuntimePreReviewRecommendation.RUN_PAPER_RUNTIME_PRE_REVIEW_SUITE)
    if state == PaperRuntimePreReviewState.READY_FOR_PAPER_TRADING_RUNTIME:
        recommendations.append(PaperRuntimePreReviewRecommendation.APPROVE_PAPER_TRADING_RUNTIME_IMPLEMENTATION)
    return _dedupe(recommendations)


def evaluate_paper_runtime_pre_review(data: PaperRuntimePreReviewInput | Mapping[str, Any]) -> PaperRuntimePreReviewResult:
    data = _coerce_input(data)
    module_map = map_trading_modules(data)
    duplicate_review = detect_runtime_duplicates(data)
    dependency_review = review_runtime_dependencies(data)
    entrypoint_review = review_runtime_entrypoints(data)
    integration_gap_review = review_runtime_integration_gaps(data)
    risks = detect_pre_review_risks(data, module_map, duplicate_review, dependency_review, entrypoint_review, integration_gap_review)
    score = compute_pre_review_score(data, risks, module_map, duplicate_review, dependency_review, entrypoint_review, integration_gap_review)
    state = _select_state(score.overall_score, risks, data.ready_for_paper_trading_runtime)
    recommendations = generate_pre_review_recommendations(risks, state)
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
    summary = f"{state.value}: score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return PaperRuntimePreReviewResult(
        state=state,
        pre_review_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        module_map=module_map,
        duplicate_review=duplicate_review,
        dependency_review=dependency_review,
        entrypoint_review=entrypoint_review,
        integration_gap_review=integration_gap_review,
        recommendations=recommendations,
        offline_only=offline_only,
        summary=summary,
    )


def render_paper_runtime_pre_review_markdown(result: PaperRuntimePreReviewResult) -> str:
    lines = [
        "# AGIcore Paper Trading Runtime Pre-Review",
        f"- State: {result.state.value}",
        f"- Score: {result.pre_review_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Score Breakdown",
        f"- Module map: {result.score_breakdown.module_map_score}/100",
        f"- Duplicates: {result.score_breakdown.duplicate_score}/100",
        f"- Dependencies: {result.score_breakdown.dependency_score}/100",
        f"- Entrypoints: {result.score_breakdown.entrypoint_score}/100",
        f"- Integration: {result.score_breakdown.integration_score}/100",
        "",
        "# Trading Module Map",
    ]
    lines.extend(f"- {module}: {category}" for module, category in result.module_map.categories)
    lines.append("- Missing expected modules: " + (", ".join(result.module_map.missing_expected_modules) or "none"))
    lines.append("")
    lines.append("# Runtime Reviews")
    for review in (
        result.duplicate_review,
        result.dependency_review,
        result.entrypoint_review,
        result.integration_gap_review,
    ):
        lines.append(
            f"- {review.name}: passed={review.passed}, score={review.score}/100, "
            f"risks={', '.join(risk.value for risk in review.risks) or 'none'}"
        )
        lines.extend(f"  - {detail}" for detail in review.details)
    lines.append("")
    lines.append("# Pre-Review Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Pre-Review Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_pre_review_score",
    "detect_pre_review_risks",
    "detect_runtime_duplicates",
    "evaluate_paper_runtime_pre_review",
    "generate_pre_review_recommendations",
    "map_trading_modules",
    "render_paper_runtime_pre_review_markdown",
    "review_runtime_dependencies",
    "review_runtime_entrypoints",
    "review_runtime_integration_gaps",
]
