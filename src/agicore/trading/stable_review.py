"""Offline stable review for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable

from agicore.trading.stable_review_models import (
    StabilityBlocker,
    StableRecommendation,
    StableReviewInput,
    StableReviewResult,
    StableReviewSection,
    StableReviewState,
    StableScore,
)


def _value(item: Any) -> str:
    if item is None:
        return ""
    if isinstance(item, Enum):
        return str(item.value)
    return str(item)


def _has(item: Any, *needles: str) -> bool:
    text = _value(item).upper()
    return any(needle.upper() in text for needle in needles)


def _get(obj: Any, name: str, default: Any = None) -> Any:
    return getattr(obj, name, default) if obj is not None else default


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
    return any(_has(item, *needles) for item in _as_tuple(items))


def _clamp(value: int | float, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(round(value))))


def _average(values: Iterable[int | float | None], default: int = 0) -> int:
    usable = [float(value) for value in values if value is not None]
    if not usable:
        return default
    return _clamp(sum(usable) / len(usable))


def _weighted_average(values: Iterable[tuple[int | float | None, float]], default: int = 0) -> int:
    usable = [(float(value), weight) for value, weight in values if value is not None and weight > 0]
    if not usable:
        return default
    total_weight = sum(weight for _, weight in usable)
    return _clamp(sum(value * weight for value, weight in usable) / total_weight)


def _score(obj: Any, *names: str, default: int | None = None) -> int | None:
    for name in names:
        value = _get(obj, name)
        if isinstance(value, (int, float)):
            return _clamp(value)
    return default


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


def _candidate_section(data: StableReviewInput, name: str) -> Any:
    return _get(data.freeze_candidate_review, f"{name}_review")


def _candidate_score(data: StableReviewInput, *names: str) -> int | None:
    review = data.freeze_candidate_review
    if review is None:
        return None
    score = _score(review, "freeze_candidate_score")
    breakdown = _get(review, "score_breakdown")
    section_scores = []
    for name in names:
        section_scores.append(_score(_candidate_section(data, name), "score"))
    direct = [_score(breakdown, f"{name}_score") for name in names]
    resolved = [value for value in section_scores + direct if value is not None]
    if resolved:
        return _average(resolved)
    return score


def _readiness_snapshot(data: StableReviewInput) -> Any:
    return _get(data.freeze_readiness_audit, "snapshot")


def _readiness_score(data: StableReviewInput, *names: str) -> int | None:
    snapshot = _readiness_snapshot(data)
    if snapshot is None:
        return None
    values = [_score(snapshot, name) for name in names]
    return _average(values) if any(value is not None for value in values) else None


def _candidate_has_blocker(data: StableReviewInput, *needles: str) -> bool:
    return _contains(_get(data.freeze_candidate_review, "blockers", ()), *needles)


def _readiness_has_blocker(data: StableReviewInput, *needles: str) -> bool:
    return _contains(_get(data.freeze_readiness_audit, "blockers", ()), *needles)


def build_codebase_stability_review(data: StableReviewInput) -> StableReviewSection:
    """Review codebase stability, module coherence and import structure."""

    import_score = data.import_coherence_score if data.import_coherence_score is not None else 75
    module_score = data.module_coherence_score if data.module_coherence_score is not None else max(
        0, 100 - data.module_fragmentation_count * 18
    )
    score = _clamp(data.codebase_score) if data.codebase_score is not None else _average(
        (
            _candidate_score(data, "architecture"),
            _readiness_score(data, "cognitive_fragmentation_score", "engine_conflict_score"),
            _bool_score(data.codebase_stable),
            _bool_score(data.import_structure_valid),
            module_score,
            import_score,
        ),
        default=60,
    )
    blockers: list[StabilityBlocker] = []
    if (
        data.codebase_stable is not True
        or data.module_fragmentation_count > 0
        or module_score < 78
        or _candidate_has_blocker(data, "ARCHITECTURE_FRAGMENTATION")
    ):
        blockers.append(StabilityBlocker.CODEBASE_FRAGMENTATION)
    if data.import_structure_valid is not True or import_score < 78:
        blockers.append(StabilityBlocker.IMPORT_STRUCTURE_RISK)
    evidence = (
        f"codebase_score={score}/100",
        f"module_fragmentation_count={data.module_fragmentation_count}",
        f"module_coherence_score={module_score}/100",
        f"import_coherence_score={import_score}/100",
    )
    return StableReviewSection(
        name="codebase",
        score=score,
        passed=not blockers and score >= 80,
        blockers=_dedupe(blockers),
        evidence=evidence,
    )


def build_runtime_stability_review(data: StableReviewInput) -> StableReviewSection:
    """Review runtime state clarity and recoverability."""

    runtime_state_score = data.runtime_state_score if data.runtime_state_score is not None else _bool_score(
        data.runtime_state_clear
    )
    score = _clamp(data.runtime_score) if data.runtime_score is not None else _average(
        (
            _candidate_score(data, "runtime"),
            _readiness_score(data, "global_stability_score", "runtime_coherence_score"),
            runtime_state_score,
            _bool_score(data.runtime_recoverable),
        ),
        default=55,
    )
    blockers: list[StabilityBlocker] = []
    if (
        data.runtime_state_clear is not True
        or runtime_state_score < 78
        or score < 78
        or _candidate_has_blocker(data, "RUNTIME_INSTABILITY")
    ):
        blockers.append(StabilityBlocker.RUNTIME_STATE_AMBIGUITY)
    evidence = (
        f"runtime_score={score}/100",
        f"runtime_state_score={runtime_state_score}/100",
        f"runtime_recoverable={data.runtime_recoverable}",
    )
    return StableReviewSection(
        name="runtime",
        score=score,
        passed=not blockers and score >= 78,
        blockers=_dedupe(blockers),
        evidence=evidence,
    )


def build_testing_stability_review(data: StableReviewInput) -> StableReviewSection:
    """Review test suite stability and regression confidence."""

    pass_rate_score = 100 * data.unit_test_pass_rate if data.unit_test_pass_rate is not None else 45
    instability_penalty = min(80, data.flaky_test_count * 15 + data.test_failure_count * 25)
    score = _clamp(data.testing_score) if data.testing_score is not None else _average(
        (
            _bool_score(data.tests_green),
            pass_rate_score,
            max(0, 100 - instability_penalty),
            _readiness_score(data, "test_coverage_score"),
        ),
        default=50,
    )
    blockers: list[StabilityBlocker] = []
    if (
        data.tests_green is not True
        or score < 85
        or data.flaky_test_count > 0
        or data.test_failure_count > 0
        or _readiness_has_blocker(data, "TEST")
    ):
        blockers.append(StabilityBlocker.TEST_SUITE_INSTABILITY)
    evidence = (
        f"testing_score={score}/100",
        f"unit_test_pass_rate={data.unit_test_pass_rate}",
        f"flaky_test_count={data.flaky_test_count}",
        f"test_failure_count={data.test_failure_count}",
    )
    return StableReviewSection(
        name="testing",
        score=score,
        passed=not blockers and score >= 85,
        blockers=tuple(blockers),
        evidence=evidence,
    )


def build_observability_stability_review(data: StableReviewInput) -> StableReviewSection:
    """Review logging consistency and runtime observability."""

    logging_score = _average((_bool_score(data.logging_consistent), _bool_score(data.structured_logging_enabled)))
    score = _clamp(data.observability_score) if data.observability_score is not None else _average(
        (
            _candidate_score(data, "observability"),
            _readiness_score(data, "observability_score"),
            logging_score,
            _bool_score(data.runtime_observable),
            _bool_score(data.metrics_available),
        ),
        default=50,
    )
    blockers: list[StabilityBlocker] = []
    if data.logging_consistent is not True or data.structured_logging_enabled is not True or logging_score < 80:
        blockers.append(StabilityBlocker.LOGGING_INCONSISTENCY)
    if (
        data.runtime_observable is not True
        or data.metrics_available is not True
        or score < 78
        or _candidate_has_blocker(data, "OBSERVABILITY_GAP")
        or _readiness_has_blocker(data, "RUNTIME_UNOBSERVABLE")
    ):
        blockers.append(StabilityBlocker.OBSERVABILITY_GAP)
    evidence = (
        f"observability_score={score}/100",
        f"logging_score={logging_score}/100",
        f"runtime_observable={data.runtime_observable}",
        f"metrics_available={data.metrics_available}",
    )
    return StableReviewSection(
        name="observability",
        score=score,
        passed=not blockers and score >= 78,
        blockers=_dedupe(blockers),
        evidence=evidence,
    )


def build_sandbox_stability_review(data: StableReviewInput) -> StableReviewSection:
    """Review sandbox preparation, replay runtime, kill switch and rollback readiness."""

    replay_score = data.replay_runtime_score if data.replay_runtime_score is not None else _average(
        (
            _bool_score(data.replay_runtime_verified),
            _readiness_score(data, "replay_safety_score"),
        )
    )
    kill_switch_score = _bool_score(data.kill_switch_verified)
    rollback_score = _bool_score(data.rollback_verified)
    isolation_score = _average(
        (
            _bool_score(data.execution_isolated),
            _bool_score(data.broker_disabled),
            _bool_score(data.external_api_disabled),
            _bool_score(data.live_execution_disabled),
        )
    )
    score = _clamp(data.sandbox_score) if data.sandbox_score is not None else _average(
        (
            _candidate_score(data, "paper_runtime"),
            _readiness_score(data, "sandbox_score", "paper_trading_score"),
            _bool_score(data.sandbox_prep_complete),
            _bool_score(data.paper_runtime_ready),
            replay_score,
            kill_switch_score,
            rollback_score,
            isolation_score,
        ),
        default=45,
    )
    blockers: list[StabilityBlocker] = []
    if (
        data.sandbox_prep_complete is not True
        or data.paper_runtime_ready is not True
        or data.execution_isolated is not True
        or data.broker_disabled is not True
        or data.external_api_disabled is not True
        or data.live_execution_disabled is not True
        or _candidate_has_blocker(data, "SANDBOX_NOT_READY", "EXECUTION_LEAK_RISK")
    ):
        blockers.append(StabilityBlocker.SANDBOX_PREP_INCOMPLETE)
    if data.replay_runtime_verified is not True or replay_score < 80:
        blockers.append(StabilityBlocker.REPLAY_RUNTIME_UNVERIFIED)
    if data.kill_switch_verified is not True:
        blockers.append(StabilityBlocker.KILL_SWITCH_UNVERIFIED)
    if data.rollback_verified is not True:
        blockers.append(StabilityBlocker.ROLLBACK_UNVERIFIED)
    evidence = (
        f"sandbox_score={score}/100",
        f"replay_score={replay_score}/100",
        f"kill_switch_score={kill_switch_score}/100",
        f"rollback_score={rollback_score}/100",
        f"isolation_score={isolation_score}/100",
    )
    return StableReviewSection(
        name="sandbox",
        score=score,
        passed=not blockers and score >= 80,
        blockers=_dedupe(blockers),
        evidence=evidence,
    )


def detect_stability_blockers(
    data: StableReviewInput,
    codebase_review: StableReviewSection | None = None,
    runtime_review: StableReviewSection | None = None,
    testing_review: StableReviewSection | None = None,
    observability_review: StableReviewSection | None = None,
    sandbox_review: StableReviewSection | None = None,
) -> tuple[StabilityBlocker, ...]:
    """Detect blockers that prevent promotion from freeze candidate to stable."""

    sections = (
        codebase_review or build_codebase_stability_review(data),
        runtime_review or build_runtime_stability_review(data),
        testing_review or build_testing_stability_review(data),
        observability_review or build_observability_stability_review(data),
        sandbox_review or build_sandbox_stability_review(data),
    )
    blockers: list[StabilityBlocker] = []
    for section in sections:
        blockers.extend(section.blockers)
    return _dedupe(blockers)


def compute_stable_score(
    data: StableReviewInput,
    blockers: tuple[StabilityBlocker, ...] = (),
    codebase_review: StableReviewSection | None = None,
    runtime_review: StableReviewSection | None = None,
    testing_review: StableReviewSection | None = None,
    observability_review: StableReviewSection | None = None,
    sandbox_review: StableReviewSection | None = None,
) -> StableScore:
    """Compute stable review scores normalized to 0..100."""

    codebase = codebase_review or build_codebase_stability_review(data)
    runtime = runtime_review or build_runtime_stability_review(data)
    testing = testing_review or build_testing_stability_review(data)
    observability = observability_review or build_observability_stability_review(data)
    sandbox = sandbox_review or build_sandbox_stability_review(data)
    import_score = data.import_coherence_score if data.import_coherence_score is not None else _average(
        (_bool_score(data.import_structure_valid),)
    )
    logging_score = _average((_bool_score(data.logging_consistent), _bool_score(data.structured_logging_enabled)))
    replay_score = data.replay_runtime_score if data.replay_runtime_score is not None else _average(
        (_bool_score(data.replay_runtime_verified), _readiness_score(data, "replay_safety_score"))
    )
    kill_switch_score = _bool_score(data.kill_switch_verified)
    rollback_score = _bool_score(data.rollback_verified)
    weighted = _weighted_average(
        (
            (codebase.score, 1.15),
            (runtime.score, 1.1),
            (testing.score, 1.25),
            (observability.score, 1.0),
            (sandbox.score, 1.0),
            (import_score, 0.9),
            (logging_score, 0.9),
            (replay_score, 0.9),
            (kill_switch_score, 0.8),
            (rollback_score, 0.8),
        )
    )
    penalty = min(60, len(set(blockers)) * 6)
    overall = _clamp(weighted - penalty)
    critical_caps = {
        StabilityBlocker.TEST_SUITE_INSTABILITY: 72,
        StabilityBlocker.CODEBASE_FRAGMENTATION: 76,
        StabilityBlocker.IMPORT_STRUCTURE_RISK: 78,
        StabilityBlocker.RUNTIME_STATE_AMBIGUITY: 72,
        StabilityBlocker.SANDBOX_PREP_INCOMPLETE: 82,
    }
    for blocker, cap in critical_caps.items():
        if blocker in blockers:
            overall = min(overall, cap)
    return StableScore(
        overall_score=overall,
        codebase_score=codebase.score,
        runtime_score=runtime.score,
        testing_score=testing.score,
        observability_score=observability.score,
        sandbox_score=sandbox.score,
        import_structure_score=_clamp(import_score),
        logging_score=logging_score,
        replay_score=_clamp(replay_score),
        kill_switch_score=kill_switch_score,
        rollback_score=rollback_score,
    )


def _select_state(score: int, blockers: tuple[StabilityBlocker, ...]) -> StableReviewState:
    blocker_count = len(set(blockers))
    if score < 45 or blocker_count >= 6:
        return StableReviewState.NOT_STABLE
    if blocker_count >= 3 or score < 70:
        return StableReviewState.STABILITY_REVIEW_REQUIRED
    if blocker_count:
        return StableReviewState.STABLE_CANDIDATE
    if score >= 94:
        return StableReviewState.READY_FOR_SANDBOX_PREP
    if score >= 88:
        return StableReviewState.STABLE
    return StableReviewState.STABLE_CANDIDATE


def generate_stable_recommendations(
    blockers: tuple[StabilityBlocker, ...],
    state: StableReviewState | None = None,
) -> tuple[StableRecommendation, ...]:
    """Generate recommendations for stable promotion."""

    recommendations: list[StableRecommendation] = []
    if blockers:
        recommendations.append(StableRecommendation.HOLD_STABLE_PROMOTION)
    mapping = {
        StabilityBlocker.TEST_SUITE_INSTABILITY: StableRecommendation.FIX_TEST_SUITE_INSTABILITY,
        StabilityBlocker.CODEBASE_FRAGMENTATION: StableRecommendation.CONSOLIDATE_CODEBASE_MODULES,
        StabilityBlocker.IMPORT_STRUCTURE_RISK: StableRecommendation.REPAIR_IMPORT_STRUCTURE,
        StabilityBlocker.RUNTIME_STATE_AMBIGUITY: StableRecommendation.CLARIFY_RUNTIME_STATE,
        StabilityBlocker.LOGGING_INCONSISTENCY: StableRecommendation.STANDARDIZE_LOGGING,
        StabilityBlocker.OBSERVABILITY_GAP: StableRecommendation.COMPLETE_OBSERVABILITY,
        StabilityBlocker.SANDBOX_PREP_INCOMPLETE: StableRecommendation.COMPLETE_SANDBOX_PREP,
        StabilityBlocker.REPLAY_RUNTIME_UNVERIFIED: StableRecommendation.VERIFY_REPLAY_RUNTIME,
        StabilityBlocker.KILL_SWITCH_UNVERIFIED: StableRecommendation.VERIFY_KILL_SWITCH,
        StabilityBlocker.ROLLBACK_UNVERIFIED: StableRecommendation.VERIFY_ROLLBACK,
    }
    recommendations.extend(mapping[blocker] for blocker in blockers)
    recommendations.append(StableRecommendation.RUN_STABLE_REVIEW_SUITE)
    if state in {StableReviewState.STABLE, StableReviewState.READY_FOR_SANDBOX_PREP}:
        recommendations.append(StableRecommendation.APPROVE_SANDBOX_PREP_AFTER_MANUAL_REVIEW)
    return _dedupe(recommendations)


def evaluate_stable_review(data: StableReviewInput) -> StableReviewResult:
    """Evaluate whether AGIcore can move from freeze candidate to stable."""

    codebase = build_codebase_stability_review(data)
    runtime = build_runtime_stability_review(data)
    testing = build_testing_stability_review(data)
    observability = build_observability_stability_review(data)
    sandbox = build_sandbox_stability_review(data)
    blockers = detect_stability_blockers(data, codebase, runtime, testing, observability, sandbox)
    score = compute_stable_score(data, blockers, codebase, runtime, testing, observability, sandbox)
    state = _select_state(score.overall_score, blockers)
    recommendations = generate_stable_recommendations(blockers, state)
    offline_only = data.broker_disabled and data.external_api_disabled and data.live_execution_disabled
    summary = f"{state.value}: score={score.overall_score}, blockers={len(blockers)}, offline_only={offline_only}"
    return StableReviewResult(
        state=state,
        stable_score=score.overall_score,
        score_breakdown=score,
        blockers=blockers,
        codebase_review=codebase,
        runtime_review=runtime,
        testing_review=testing,
        observability_review=observability,
        sandbox_review=sandbox,
        recommendations=recommendations,
        offline_only=offline_only,
        summary=summary,
    )


def render_stable_review_markdown(result: StableReviewResult) -> str:
    """Render an explainable stable review report."""

    lines = [
        "# AGIcore Stable Review",
        f"- State: {result.state.value}",
        f"- Score: {result.stable_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Score Breakdown",
        f"- Codebase: {result.score_breakdown.codebase_score}/100",
        f"- Runtime: {result.score_breakdown.runtime_score}/100",
        f"- Testing: {result.score_breakdown.testing_score}/100",
        f"- Observability: {result.score_breakdown.observability_score}/100",
        f"- Sandbox: {result.score_breakdown.sandbox_score}/100",
        f"- Import structure: {result.score_breakdown.import_structure_score}/100",
        f"- Logging: {result.score_breakdown.logging_score}/100",
        f"- Replay runtime: {result.score_breakdown.replay_score}/100",
        f"- Kill switch: {result.score_breakdown.kill_switch_score}/100",
        f"- Rollback: {result.score_breakdown.rollback_score}/100",
        "",
        "# Stability Sections",
    ]
    for section in (
        result.codebase_review,
        result.runtime_review,
        result.testing_review,
        result.observability_review,
        result.sandbox_review,
    ):
        lines.append(
            f"- {section.name}: passed={section.passed}, score={section.score}/100, "
            f"blockers={', '.join(blocker.value for blocker in section.blockers) or 'none'}"
        )
        lines.extend(f"  - {item}" for item in section.evidence)
    lines.append("")
    lines.append("# Stability Blockers")
    lines.extend(f"- {blocker.value}" for blocker in result.blockers) if result.blockers else lines.append("- none")
    lines.append("")
    lines.append("# Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    lines.append("")
    lines.append("# Stable Outlook")
    if result.state == StableReviewState.READY_FOR_SANDBOX_PREP:
        lines.append("- Stable review is ready for sandbox preparation review.")
    elif result.state == StableReviewState.STABLE:
        lines.append("- Stable criteria are met; sandbox preparation still needs explicit approval.")
    elif result.state == StableReviewState.STABLE_CANDIDATE:
        lines.append("- Stable candidacy is plausible but remaining blockers must be resolved.")
    else:
        lines.append("- Stable promotion should remain blocked until review issues are resolved.")
    return "\n".join(lines)


__all__ = [
    "build_codebase_stability_review",
    "build_observability_stability_review",
    "build_runtime_stability_review",
    "build_sandbox_stability_review",
    "build_testing_stability_review",
    "compute_stable_score",
    "detect_stability_blockers",
    "evaluate_stable_review",
    "generate_stable_recommendations",
    "render_stable_review_markdown",
]
