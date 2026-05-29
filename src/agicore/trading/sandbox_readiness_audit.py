"""Offline sandbox readiness audit for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable

from agicore.trading.sandbox_readiness_audit_models import (
    SandboxBlocker,
    SandboxReadinessInput,
    SandboxReadinessResult,
    SandboxReadinessState,
    SandboxRecommendation,
    SandboxReviewSection,
    SandboxScore,
)


def _value(item: Any) -> str:
    if item is None:
        return ""
    if isinstance(item, Enum):
        return str(item.value)
    return str(item)


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
    text_items = tuple(_value(item).upper() for item in _as_tuple(items))
    return any(any(needle.upper() in item for item in text_items) for needle in needles)


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


def _stable_score(data: SandboxReadinessInput, *names: str) -> int | None:
    review = data.stable_review
    if review is None:
        return None
    breakdown = _get(review, "score_breakdown")
    section_scores = []
    for name in names:
        section_scores.append(_score(_get(review, f"{name}_review"), "score"))
    direct_scores = [_score(breakdown, f"{name}_score") for name in names]
    values = [value for value in section_scores + direct_scores if value is not None]
    if values:
        return _average(values)
    return _score(review, "stable_score")


def _candidate_score(data: SandboxReadinessInput, *names: str) -> int | None:
    review = data.freeze_candidate_review
    if review is None:
        return None
    breakdown = _get(review, "score_breakdown")
    values = [_score(_get(review, f"{name}_review"), "score") for name in names]
    values.extend(_score(breakdown, f"{name}_score") for name in names)
    values = [value for value in values if value is not None]
    if values:
        return _average(values)
    return _score(review, "freeze_candidate_score")


def _readiness_snapshot(data: SandboxReadinessInput) -> Any:
    return _get(data.freeze_readiness_audit, "snapshot")


def _readiness_score(data: SandboxReadinessInput, *names: str) -> int | None:
    snapshot = _readiness_snapshot(data)
    values = [_score(snapshot, name) for name in names]
    return _average(values) if any(value is not None for value in values) else None


def _has_upstream_blocker(data: SandboxReadinessInput, *needles: str) -> bool:
    blockers = (
        _as_tuple(_get(data.stable_review, "blockers", ()))
        + _as_tuple(_get(data.freeze_candidate_review, "blockers", ()))
        + _as_tuple(_get(data.freeze_readiness_audit, "blockers", ()))
    )
    return _contains(blockers, *needles)


def build_runtime_isolation_review(data: SandboxReadinessInput) -> SandboxReviewSection:
    """Review live execution, broker, API and sandbox isolation boundaries."""

    state_score = data.state_integrity_score if data.state_integrity_score is not None else _average(
        (
            _bool_score(data.sandbox_state_clean),
            _bool_score(data.runtime_state_validated),
            _bool_score(data.state_checksum_valid),
            _stable_score(data, "runtime"),
        )
    )
    memory_score = data.memory_persistence_score if data.memory_persistence_score is not None else _average(
        (
            _bool_score(data.memory_persistence_isolated),
            _bool_score(data.memory_snapshot_reversible),
        )
    )
    score = _clamp(data.isolation_score) if data.isolation_score is not None else _average(
        (
            _bool_score(data.live_execution_disabled),
            _bool_score(data.execution_isolated),
            _bool_score(data.broker_disabled),
            _bool_score(data.broker_credentials_absent),
            _bool_score(data.external_api_disabled),
            _bool_score(data.api_credentials_absent),
            _bool_score(data.sandbox_network_isolated),
            _bool_score(data.sandbox_filesystem_isolated),
            state_score,
            memory_score,
            _stable_score(data, "sandbox"),
            _readiness_score(data, "sandbox_score"),
        ),
        default=45,
    )
    blockers: list[SandboxBlocker] = []
    if data.live_execution_disabled is not True:
        blockers.append(SandboxBlocker.LIVE_EXECUTION_LEAK)
    if data.broker_disabled is not True or data.broker_credentials_absent is not True:
        blockers.append(SandboxBlocker.BROKER_CONNECTION_RISK)
    if data.external_api_disabled is not True or data.api_credentials_absent is not True:
        blockers.append(SandboxBlocker.API_EXPOSURE_RISK)
    if (
        data.execution_isolated is not True
        or data.sandbox_network_isolated is not True
        or data.sandbox_filesystem_isolated is not True
        or _has_upstream_blocker(data, "EXECUTION_LEAK", "EXECUTION_UNSAFE", "SANDBOX_PREP_INCOMPLETE")
    ):
        blockers.append(SandboxBlocker.SANDBOX_ISOLATION_FAILURE)
    if data.sandbox_state_clean is not True or data.runtime_state_validated is not True or data.state_checksum_valid is not True or state_score < 80:
        blockers.append(SandboxBlocker.STATE_CORRUPTION_RISK)
    if data.memory_persistence_isolated is not True or data.memory_snapshot_reversible is not True or memory_score < 80:
        blockers.append(SandboxBlocker.MEMORY_PERSISTENCE_RISK)
    evidence = (
        f"isolation_score={score}/100",
        f"state_integrity_score={state_score}/100",
        f"memory_persistence_score={memory_score}/100",
        f"live_execution_disabled={data.live_execution_disabled}",
        f"broker_disabled={data.broker_disabled}",
        f"external_api_disabled={data.external_api_disabled}",
    )
    return SandboxReviewSection(
        name="runtime_isolation",
        score=score,
        passed=not blockers and score >= 85,
        blockers=_dedupe(blockers),
        evidence=evidence,
    )


def build_kill_switch_review(data: SandboxReadinessInput) -> SandboxReviewSection:
    """Review kill switch configuration and test evidence."""

    score = _clamp(data.kill_switch_score) if data.kill_switch_score is not None else _average(
        (
            _bool_score(data.kill_switch_configured),
            _bool_score(data.kill_switch_tested),
            _stable_score(data, "sandbox"),
        ),
        default=45,
    )
    blockers = []
    if data.kill_switch_configured is not True or data.kill_switch_tested is not True or score < 85:
        blockers.append(SandboxBlocker.KILL_SWITCH_FAILURE)
    evidence = (
        f"kill_switch_score={score}/100",
        f"kill_switch_configured={data.kill_switch_configured}",
        f"kill_switch_tested={data.kill_switch_tested}",
    )
    return SandboxReviewSection(
        name="kill_switch",
        score=score,
        passed=not blockers and score >= 85,
        blockers=tuple(blockers),
        evidence=evidence,
    )


def build_rollback_review(data: SandboxReadinessInput) -> SandboxReviewSection:
    """Review rollback plan and rollback test evidence."""

    score = _clamp(data.rollback_score) if data.rollback_score is not None else _average(
        (
            _bool_score(data.rollback_plan_available),
            _bool_score(data.rollback_tested),
            _readiness_score(data, "rollback_score"),
        ),
        default=45,
    )
    blockers = []
    if data.rollback_plan_available is not True or data.rollback_tested is not True or score < 80:
        blockers.append(SandboxBlocker.ROLLBACK_FAILURE)
    evidence = (
        f"rollback_score={score}/100",
        f"rollback_plan_available={data.rollback_plan_available}",
        f"rollback_tested={data.rollback_tested}",
    )
    return SandboxReviewSection(
        name="rollback",
        score=score,
        passed=not blockers and score >= 80,
        blockers=tuple(blockers),
        evidence=evidence,
    )


def build_observability_review(data: SandboxReadinessInput) -> SandboxReviewSection:
    """Review observability required before sandbox entry."""

    score = _clamp(data.observability_score) if data.observability_score is not None else _average(
        (
            _bool_score(data.runtime_observable),
            _bool_score(data.structured_logging_enabled),
            _bool_score(data.metrics_available),
            _bool_score(data.audit_events_enabled),
            _stable_score(data, "observability"),
            _candidate_score(data, "observability"),
            _readiness_score(data, "observability_score"),
        ),
        default=45,
    )
    blockers = []
    if (
        data.runtime_observable is not True
        or data.structured_logging_enabled is not True
        or data.metrics_available is not True
        or data.audit_events_enabled is not True
        or score < 80
        or _has_upstream_blocker(data, "OBSERVABILITY_GAP", "RUNTIME_UNOBSERVABLE")
    ):
        blockers.append(SandboxBlocker.OBSERVABILITY_GAP)
    evidence = (
        f"observability_score={score}/100",
        f"runtime_observable={data.runtime_observable}",
        f"structured_logging_enabled={data.structured_logging_enabled}",
        f"metrics_available={data.metrics_available}",
        f"audit_events_enabled={data.audit_events_enabled}",
    )
    return SandboxReviewSection(
        name="observability",
        score=score,
        passed=not blockers and score >= 80,
        blockers=tuple(blockers),
        evidence=evidence,
    )


def build_paper_runtime_preparation_review(data: SandboxReadinessInput) -> SandboxReviewSection:
    """Review preconditions for later paper runtime preparation."""

    replay_score = data.replay_runtime_score if data.replay_runtime_score is not None else _average(
        (
            _bool_score(data.replay_runtime_verified),
            _readiness_score(data, "replay_safety_score"),
        )
    )
    score = _clamp(data.paper_runtime_score) if data.paper_runtime_score is not None else _average(
        (
            _bool_score(data.paper_runtime_prepared),
            _bool_score(data.paper_runtime_dependencies_ready),
            replay_score,
            _stable_score(data, "sandbox"),
            _candidate_score(data, "paper_runtime"),
            _readiness_score(data, "paper_trading_score"),
        ),
        default=45,
    )
    blockers = []
    if data.replay_runtime_verified is not True or replay_score < 80:
        blockers.append(SandboxBlocker.PAPER_RUNTIME_NOT_READY)
    if data.paper_runtime_prepared is not True or data.paper_runtime_dependencies_ready is not True or score < 80:
        blockers.append(SandboxBlocker.PAPER_RUNTIME_NOT_READY)
    evidence = (
        f"paper_runtime_score={score}/100",
        f"replay_score={replay_score}/100",
        f"paper_runtime_prepared={data.paper_runtime_prepared}",
        f"paper_runtime_dependencies_ready={data.paper_runtime_dependencies_ready}",
    )
    return SandboxReviewSection(
        name="paper_runtime_preparation",
        score=score,
        passed=not blockers and score >= 80,
        blockers=_dedupe(blockers),
        evidence=evidence,
    )


def detect_sandbox_blockers(
    data: SandboxReadinessInput,
    runtime_isolation_review: SandboxReviewSection | None = None,
    kill_switch_review: SandboxReviewSection | None = None,
    rollback_review: SandboxReviewSection | None = None,
    observability_review: SandboxReviewSection | None = None,
    paper_runtime_preparation_review: SandboxReviewSection | None = None,
) -> tuple[SandboxBlocker, ...]:
    """Detect sandbox blockers before any paper runtime preparation."""

    sections = (
        runtime_isolation_review or build_runtime_isolation_review(data),
        kill_switch_review or build_kill_switch_review(data),
        rollback_review or build_rollback_review(data),
        observability_review or build_observability_review(data),
        paper_runtime_preparation_review or build_paper_runtime_preparation_review(data),
    )
    blockers: list[SandboxBlocker] = []
    for section in sections:
        blockers.extend(section.blockers)
    return _dedupe(blockers)


def compute_sandbox_score(
    data: SandboxReadinessInput,
    blockers: tuple[SandboxBlocker, ...] = (),
    runtime_isolation_review: SandboxReviewSection | None = None,
    kill_switch_review: SandboxReviewSection | None = None,
    rollback_review: SandboxReviewSection | None = None,
    observability_review: SandboxReviewSection | None = None,
    paper_runtime_preparation_review: SandboxReviewSection | None = None,
) -> SandboxScore:
    """Compute sandbox readiness score normalized to 0..100."""

    isolation = runtime_isolation_review or build_runtime_isolation_review(data)
    kill_switch = kill_switch_review or build_kill_switch_review(data)
    rollback = rollback_review or build_rollback_review(data)
    observability = observability_review or build_observability_review(data)
    paper = paper_runtime_preparation_review or build_paper_runtime_preparation_review(data)
    state_score = data.state_integrity_score if data.state_integrity_score is not None else _average(
        (
            _bool_score(data.sandbox_state_clean),
            _bool_score(data.runtime_state_validated),
            _bool_score(data.state_checksum_valid),
        )
    )
    memory_score = data.memory_persistence_score if data.memory_persistence_score is not None else _average(
        (
            _bool_score(data.memory_persistence_isolated),
            _bool_score(data.memory_snapshot_reversible),
        )
    )
    replay_score = data.replay_runtime_score if data.replay_runtime_score is not None else _average(
        (
            _bool_score(data.replay_runtime_verified),
            _readiness_score(data, "replay_safety_score"),
        )
    )
    weighted = _weighted_average(
        (
            (isolation.score, 1.35),
            (kill_switch.score, 1.0),
            (rollback.score, 0.95),
            (observability.score, 1.0),
            (paper.score, 0.85),
            (state_score, 0.95),
            (memory_score, 0.85),
            (replay_score, 0.85),
        )
    )
    penalty = min(65, len(set(blockers)) * 7)
    overall = _clamp(weighted - penalty)
    critical_caps = {
        SandboxBlocker.LIVE_EXECUTION_LEAK: 35,
        SandboxBlocker.BROKER_CONNECTION_RISK: 45,
        SandboxBlocker.API_EXPOSURE_RISK: 50,
        SandboxBlocker.SANDBOX_ISOLATION_FAILURE: 55,
        SandboxBlocker.KILL_SWITCH_FAILURE: 70,
        SandboxBlocker.ROLLBACK_FAILURE: 75,
    }
    for blocker, cap in critical_caps.items():
        if blocker in blockers:
            overall = min(overall, cap)
    return SandboxScore(
        overall_score=overall,
        runtime_isolation_score=isolation.score,
        kill_switch_score=kill_switch.score,
        rollback_score=rollback.score,
        observability_score=observability.score,
        paper_runtime_preparation_score=paper.score,
        state_integrity_score=_clamp(state_score),
        memory_persistence_score=_clamp(memory_score),
        replay_runtime_score=_clamp(replay_score),
    )


def _select_state(score: int, blockers: tuple[SandboxBlocker, ...]) -> SandboxReadinessState:
    blocker_count = len(set(blockers))
    hard_blockers = {
        SandboxBlocker.LIVE_EXECUTION_LEAK,
        SandboxBlocker.BROKER_CONNECTION_RISK,
        SandboxBlocker.API_EXPOSURE_RISK,
        SandboxBlocker.SANDBOX_ISOLATION_FAILURE,
    }
    if hard_blockers.intersection(blockers) or score < 45 or blocker_count >= 6:
        return SandboxReadinessState.NOT_READY
    if blocker_count >= 3 or score < 72:
        return SandboxReadinessState.SANDBOX_REVIEW_REQUIRED
    if blocker_count:
        return SandboxReadinessState.SANDBOX_CANDIDATE
    if score >= 94:
        return SandboxReadinessState.READY_FOR_PAPER_RUNTIME
    if score >= 88:
        return SandboxReadinessState.SANDBOX_READY
    return SandboxReadinessState.SANDBOX_CANDIDATE


def generate_sandbox_recommendations(
    blockers: tuple[SandboxBlocker, ...],
    state: SandboxReadinessState | None = None,
) -> tuple[SandboxRecommendation, ...]:
    """Generate remediation recommendations for sandbox readiness."""

    recommendations: list[SandboxRecommendation] = []
    if blockers:
        recommendations.append(SandboxRecommendation.HOLD_SANDBOX_ENTRY)
    mapping = {
        SandboxBlocker.LIVE_EXECUTION_LEAK: SandboxRecommendation.SEAL_LIVE_EXECUTION_PATHS,
        SandboxBlocker.BROKER_CONNECTION_RISK: SandboxRecommendation.DISABLE_BROKER_CONNECTIONS,
        SandboxBlocker.API_EXPOSURE_RISK: SandboxRecommendation.DISABLE_EXTERNAL_APIS,
        SandboxBlocker.KILL_SWITCH_FAILURE: SandboxRecommendation.VERIFY_KILL_SWITCH,
        SandboxBlocker.ROLLBACK_FAILURE: SandboxRecommendation.VERIFY_ROLLBACK,
        SandboxBlocker.OBSERVABILITY_GAP: SandboxRecommendation.COMPLETE_OBSERVABILITY,
        SandboxBlocker.STATE_CORRUPTION_RISK: SandboxRecommendation.PROTECT_RUNTIME_STATE,
        SandboxBlocker.MEMORY_PERSISTENCE_RISK: SandboxRecommendation.ISOLATE_MEMORY_PERSISTENCE,
        SandboxBlocker.PAPER_RUNTIME_NOT_READY: SandboxRecommendation.PREPARE_PAPER_RUNTIME,
        SandboxBlocker.SANDBOX_ISOLATION_FAILURE: SandboxRecommendation.REBUILD_SANDBOX_ISOLATION,
    }
    recommendations.extend(mapping[blocker] for blocker in blockers)
    recommendations.append(SandboxRecommendation.RUN_SANDBOX_READINESS_SUITE)
    if state in {SandboxReadinessState.SANDBOX_READY, SandboxReadinessState.READY_FOR_PAPER_RUNTIME}:
        recommendations.append(SandboxRecommendation.APPROVE_PAPER_RUNTIME_ONLY_AFTER_MANUAL_REVIEW)
    return _dedupe(recommendations)


def evaluate_sandbox_readiness(data: SandboxReadinessInput) -> SandboxReadinessResult:
    """Evaluate whether AGIcore Trading can enter an isolated sandbox."""

    isolation = build_runtime_isolation_review(data)
    kill_switch = build_kill_switch_review(data)
    rollback = build_rollback_review(data)
    observability = build_observability_review(data)
    paper = build_paper_runtime_preparation_review(data)
    blockers = detect_sandbox_blockers(data, isolation, kill_switch, rollback, observability, paper)
    score = compute_sandbox_score(data, blockers, isolation, kill_switch, rollback, observability, paper)
    state = _select_state(score.overall_score, blockers)
    recommendations = generate_sandbox_recommendations(blockers, state)
    offline_only = data.live_execution_disabled and data.broker_disabled and data.external_api_disabled
    summary = f"{state.value}: score={score.overall_score}, blockers={len(blockers)}, offline_only={offline_only}"
    return SandboxReadinessResult(
        state=state,
        sandbox_score=score.overall_score,
        score_breakdown=score,
        blockers=blockers,
        runtime_isolation_review=isolation,
        kill_switch_review=kill_switch,
        rollback_review=rollback,
        observability_review=observability,
        paper_runtime_preparation_review=paper,
        recommendations=recommendations,
        offline_only=offline_only,
        summary=summary,
    )


def render_sandbox_readiness_markdown(result: SandboxReadinessResult) -> str:
    """Render an explainable sandbox readiness audit report."""

    lines = [
        "# AGIcore Sandbox Readiness Audit",
        f"- State: {result.state.value}",
        f"- Score: {result.sandbox_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Score Breakdown",
        f"- Runtime isolation: {result.score_breakdown.runtime_isolation_score}/100",
        f"- Kill switch: {result.score_breakdown.kill_switch_score}/100",
        f"- Rollback: {result.score_breakdown.rollback_score}/100",
        f"- Observability: {result.score_breakdown.observability_score}/100",
        f"- Paper runtime preparation: {result.score_breakdown.paper_runtime_preparation_score}/100",
        f"- State integrity: {result.score_breakdown.state_integrity_score}/100",
        f"- Memory persistence: {result.score_breakdown.memory_persistence_score}/100",
        f"- Replay runtime: {result.score_breakdown.replay_runtime_score}/100",
        "",
        "# Sandbox Reviews",
    ]
    for section in (
        result.runtime_isolation_review,
        result.kill_switch_review,
        result.rollback_review,
        result.observability_review,
        result.paper_runtime_preparation_review,
    ):
        lines.append(
            f"- {section.name}: passed={section.passed}, score={section.score}/100, "
            f"blockers={', '.join(blocker.value for blocker in section.blockers) or 'none'}"
        )
        lines.extend(f"  - {item}" for item in section.evidence)
    lines.append("")
    lines.append("# Sandbox Blockers")
    lines.extend(f"- {blocker.value}" for blocker in result.blockers) if result.blockers else lines.append("- none")
    lines.append("")
    lines.append("# Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    lines.append("")
    lines.append("# Sandbox Outlook")
    if result.state == SandboxReadinessState.READY_FOR_PAPER_RUNTIME:
        lines.append("- Sandbox is ready for manual paper runtime preparation review.")
    elif result.state == SandboxReadinessState.SANDBOX_READY:
        lines.append("- Sandbox entry criteria are met; paper runtime remains gated.")
    elif result.state == SandboxReadinessState.SANDBOX_CANDIDATE:
        lines.append("- Sandbox candidacy is plausible but remaining blockers must be resolved.")
    else:
        lines.append("- Sandbox entry should remain blocked until isolation issues are resolved.")
    return "\n".join(lines)


__all__ = [
    "build_kill_switch_review",
    "build_observability_review",
    "build_paper_runtime_preparation_review",
    "build_rollback_review",
    "build_runtime_isolation_review",
    "compute_sandbox_score",
    "detect_sandbox_blockers",
    "evaluate_sandbox_readiness",
    "generate_sandbox_recommendations",
    "render_sandbox_readiness_markdown",
]
