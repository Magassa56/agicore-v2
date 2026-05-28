"""Offline freeze candidate review for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable

from agicore.trading.freeze_candidate_review_models import (
    FreezeCandidateBlocker,
    FreezeCandidateRecommendation,
    FreezeCandidateReviewInput,
    FreezeCandidateReviewResult,
    FreezeCandidateReviewSection,
    FreezeCandidateScore,
    FreezeCandidateState,
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


def _risk_text(obj: Any) -> tuple[Any, ...]:
    return _as_tuple(_get(obj, "risks", ())) + _as_tuple(_get(obj, "blockers", ()))


def _has_risk(obj: Any, *needles: str) -> bool:
    return _contains(_risk_text(obj), *needles)


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


def _state(obj: Any) -> str:
    return _value(_get(obj, "state", _get(obj, "mode", ""))).upper()


def _readiness_snapshot(data: FreezeCandidateReviewInput) -> Any:
    return _get(data.freeze_readiness_audit, "snapshot")


def _readiness_score(data: FreezeCandidateReviewInput, name: str) -> int | None:
    audit = data.freeze_readiness_audit
    if audit is None:
        return None
    score = _score(audit, "freeze_readiness_score")
    if name == "overall":
        return score
    breakdown = _get(audit, "score_breakdown")
    snapshot = _get(audit, "snapshot")
    mapping = {
        "architecture": (
            _score(snapshot, "cognitive_fragmentation_score"),
            _score(snapshot, "engine_conflict_score"),
        ),
        "runtime": (
            _score(snapshot, "global_stability_score"),
            _score(snapshot, "runtime_coherence_score"),
        ),
        "observability": (_score(snapshot, "observability_score"),),
        "replay": (_score(snapshot, "replay_safety_score"),),
        "rollback": (_score(snapshot, "rollback_score"),),
        "sandbox": (_score(snapshot, "sandbox_score"),),
        "paper": (
            _score(snapshot, "paper_trading_score"),
            _score(breakdown, "paper_runtime_score"),
        ),
    }
    return _average(mapping.get(name, ()), default=score or 0)


def _freeze_audit_has_blocker(data: FreezeCandidateReviewInput, *needles: str) -> bool:
    return _contains(_get(data.freeze_readiness_audit, "blockers", ()), *needles)


def build_architecture_review(data: FreezeCandidateReviewInput) -> FreezeCandidateReviewSection:
    """Review architecture stability, module fragmentation and import coherence."""

    import_score = data.import_coherence_score if data.import_coherence_score is not None else 75
    explicit = data.architecture_score
    freeze_score = _readiness_score(data, "architecture")
    consensus = _score(data.cognitive_consensus, "cognitive_consensus_score", "consensus_score")
    coherence = _score(data.cognitive_coherence, "cognitive_coherence_score", "coherence_score")
    priority = _score(data.cognitive_priority_arbitration, "priority_arbitration_score")
    score = _clamp(explicit) if explicit is not None else _average(
        (
            freeze_score,
            consensus,
            coherence,
            priority,
            import_score,
            _bool_score(data.architecture_stable),
            max(0, 100 - data.module_fragmentation_count * 18),
        ),
        default=60,
    )
    blockers: list[FreezeCandidateBlocker] = []
    if (
        data.architecture_stable is not True
        or data.module_fragmentation_count > 0
        or import_score < 75
        or score < 78
        or _freeze_audit_has_blocker(data, "ENGINE_FRAGMENTATION")
        or _has_risk(data.cognitive_consensus, "FRAGMENT", "CONFLICT")
        or _has_risk(data.cognitive_coherence, "CONFLICT", "INCOHER")
    ):
        blockers.append(FreezeCandidateBlocker.ARCHITECTURE_FRAGMENTATION)
    evidence = (
        f"architecture_score={score}/100",
        f"module_fragmentation_count={data.module_fragmentation_count}",
        f"import_coherence_score={import_score}/100",
    )
    return FreezeCandidateReviewSection(
        name="architecture",
        score=score,
        passed=not blockers and score >= 78,
        blockers=tuple(blockers),
        evidence=evidence,
    )


def build_runtime_review(data: FreezeCandidateReviewInput) -> FreezeCandidateReviewSection:
    """Review runtime stability, recoverability, replay and rollback readiness."""

    explicit = data.runtime_score
    freeze_runtime = _readiness_score(data, "runtime")
    replay = _readiness_score(data, "replay")
    rollback = _readiness_score(data, "rollback")
    continuity = _score(data.cognitive_continuity, "cognitive_continuity_score", "continuity_score")
    score = _clamp(explicit) if explicit is not None else _average(
        (
            freeze_runtime,
            replay,
            rollback,
            continuity,
            _bool_score(data.runtime_stable),
            _bool_score(data.runtime_recoverable),
            _bool_score(data.replay_safe),
            _bool_score(data.rollback_ready),
            _bool_score(data.rollback_tested),
        ),
        default=55,
    )
    blockers: list[FreezeCandidateBlocker] = []
    if data.runtime_stable is not True or score < 75:
        blockers.append(FreezeCandidateBlocker.RUNTIME_INSTABILITY)
    if data.replay_safe is not True or (replay is not None and replay < 80) or _freeze_audit_has_blocker(data, "REPLAY_UNSAFE"):
        blockers.append(FreezeCandidateBlocker.REPLAY_UNSAFE)
    if data.rollback_ready is not True or data.rollback_tested is not True or (rollback is not None and rollback < 70):
        blockers.append(FreezeCandidateBlocker.ROLLBACK_FAILURE_RISK)
    evidence = (
        f"runtime_score={score}/100",
        f"runtime_recoverable={data.runtime_recoverable}",
        f"replay_safe={data.replay_safe}",
        f"rollback_ready={data.rollback_ready}",
    )
    return FreezeCandidateReviewSection(
        name="runtime",
        score=score,
        passed=not blockers and score >= 75,
        blockers=_dedupe(blockers),
        evidence=evidence,
    )


def build_safety_review(data: FreezeCandidateReviewInput) -> FreezeCandidateReviewSection:
    """Review safety, constitutional integrity and execution isolation."""

    explicit = data.safety_score
    constitutional = _score(data.cognitive_constitutional, "constitutional_score")
    meta = _score(data.cognitive_meta_supervision, "meta_supervision_score")
    recursive = _score(data.cognitive_recursive_regulation, "recursive_regulation_score")
    safety = _score(data.cognitive_safety_orchestrator, "safety_orchestrator_score")
    executive = _score(data.cognitive_executive_control, "executive_control_score")
    world = _score(data.recursive_world_model, "world_model_coherence_score")
    intent = _score(data.intent_integrity, "intent_integrity_score")
    identity = _score(data.cognitive_identity, "cognitive_identity_score", "identity_score")
    execution_score = _average(
        (
            _bool_score(data.execution_isolated),
            _bool_score(data.broker_disabled),
            _bool_score(data.external_api_disabled),
            _bool_score(data.live_execution_disabled),
        )
    )
    score = _clamp(explicit) if explicit is not None else _average(
        (
            constitutional,
            meta,
            recursive,
            safety,
            executive,
            world,
            intent,
            identity,
            execution_score,
            _bool_score(data.kill_switch_ready),
        ),
        default=55,
    )
    blockers: list[FreezeCandidateBlocker] = []
    if data.kill_switch_ready is not True or _freeze_audit_has_blocker(data, "KILL_SWITCH"):
        blockers.append(FreezeCandidateBlocker.KILL_SWITCH_ABSENT)
    if (
        data.execution_isolated is not True
        or data.broker_disabled is not True
        or data.external_api_disabled is not True
        or data.live_execution_disabled is not True
        or _freeze_audit_has_blocker(data, "EXECUTION_UNSAFE")
    ):
        blockers.append(FreezeCandidateBlocker.EXECUTION_LEAK_RISK)
    if (
        _has(_state(data.cognitive_meta_supervision), "DRIFT", "FRAGMENT", "CRITICAL", "LOCKDOWN")
        or _has(_state(data.cognitive_alignment), "DRIFT", "MISALIGN")
        or _has(_state(data.intent_integrity), "DRIFT", "CONFLICT", "CORRUPT")
        or _has(_state(data.cognitive_identity), "FRAGMENT", "CORRUPT", "AT_RISK")
        or _has_risk(data.cognitive_meta_supervision, "DRIFT", "FRAGMENT", "IDENTITY")
        or (meta is not None and meta < 70)
        or (intent is not None and intent < 70)
        or (identity is not None and identity < 70)
    ):
        blockers.append(FreezeCandidateBlocker.COGNITIVE_DRIFT)
    if (
        _has(_state(data.cognitive_recursive_regulation), "LOCK", "CRITICAL", "OVERFLOW")
        or _has(_value(_get(data.recursive_world_model, "decision")), "REBUILD", "FREEZE", "LOCK")
        or _has_risk(data.cognitive_recursive_regulation, "UNBOUNDED", "RECURSIVE", "OVERFLOW")
        or (recursive is not None and recursive < 70)
        or (world is not None and world < 70)
    ):
        blockers.append(FreezeCandidateBlocker.RECURSIVE_OVERFLOW_RISK)
    if score < 75:
        blockers.append(FreezeCandidateBlocker.RUNTIME_INSTABILITY)
    evidence = (
        f"safety_score={score}/100",
        f"constitutional_score={constitutional}",
        f"recursive_score={recursive}",
        f"execution_isolated={data.execution_isolated}",
    )
    return FreezeCandidateReviewSection(
        name="safety",
        score=score,
        passed=not blockers and score >= 75,
        blockers=_dedupe(blockers),
        evidence=evidence,
    )


def build_observability_review(data: FreezeCandidateReviewInput) -> FreezeCandidateReviewSection:
    """Review runtime observability and logging consistency."""

    explicit = data.observability_score
    freeze_score = _readiness_score(data, "observability")
    reflection = _score(data.self_reflection_audit, "reflection_quality_score")
    score = _clamp(explicit) if explicit is not None else _average(
        (
            freeze_score,
            reflection,
            _bool_score(data.runtime_observable),
            _bool_score(data.logging_consistent),
        ),
        default=50,
    )
    blockers = []
    if (
        data.runtime_observable is not True
        or data.logging_consistent is not True
        or score < 75
        or _freeze_audit_has_blocker(data, "RUNTIME_UNOBSERVABLE")
    ):
        blockers.append(FreezeCandidateBlocker.OBSERVABILITY_GAP)
    evidence = (
        f"observability_score={score}/100",
        f"runtime_observable={data.runtime_observable}",
        f"logging_consistent={data.logging_consistent}",
    )
    return FreezeCandidateReviewSection(
        name="observability",
        score=score,
        passed=not blockers and score >= 75,
        blockers=tuple(blockers),
        evidence=evidence,
    )


def build_paper_runtime_review(data: FreezeCandidateReviewInput) -> FreezeCandidateReviewSection:
    """Review sandbox and paper runtime readiness."""

    explicit = data.paper_runtime_score
    freeze_paper = _readiness_score(data, "paper")
    freeze_sandbox = _readiness_score(data, "sandbox")
    score = _clamp(explicit) if explicit is not None else _average(
        (
            freeze_paper,
            freeze_sandbox,
            _bool_score(data.sandbox_ready),
            _bool_score(data.paper_runtime_ready),
        ),
        default=45,
    )
    blockers = []
    if data.sandbox_ready is not True or (freeze_sandbox is not None and freeze_sandbox < 85):
        blockers.append(FreezeCandidateBlocker.SANDBOX_NOT_READY)
    if data.paper_runtime_ready is not True or (freeze_paper is not None and freeze_paper < 80):
        blockers.append(FreezeCandidateBlocker.SANDBOX_NOT_READY)
    evidence = (
        f"paper_runtime_score={score}/100",
        f"sandbox_ready={data.sandbox_ready}",
        f"paper_runtime_ready={data.paper_runtime_ready}",
    )
    return FreezeCandidateReviewSection(
        name="paper_runtime",
        score=score,
        passed=not blockers and score >= 80,
        blockers=_dedupe(blockers),
        evidence=evidence,
    )


def detect_freeze_candidate_blockers(
    data: FreezeCandidateReviewInput,
    architecture_review: FreezeCandidateReviewSection | None = None,
    runtime_review: FreezeCandidateReviewSection | None = None,
    safety_review: FreezeCandidateReviewSection | None = None,
    observability_review: FreezeCandidateReviewSection | None = None,
    paper_runtime_review: FreezeCandidateReviewSection | None = None,
) -> tuple[FreezeCandidateBlocker, ...]:
    """Detect blockers for official freeze candidate approval."""

    sections = (
        architecture_review or build_architecture_review(data),
        runtime_review or build_runtime_review(data),
        safety_review or build_safety_review(data),
        observability_review or build_observability_review(data),
        paper_runtime_review or build_paper_runtime_review(data),
    )
    blockers: list[FreezeCandidateBlocker] = []
    for section in sections:
        blockers.extend(section.blockers)
    return _dedupe(blockers)


def compute_freeze_candidate_score(
    data: FreezeCandidateReviewInput,
    blockers: tuple[FreezeCandidateBlocker, ...] = (),
    architecture_review: FreezeCandidateReviewSection | None = None,
    runtime_review: FreezeCandidateReviewSection | None = None,
    safety_review: FreezeCandidateReviewSection | None = None,
    observability_review: FreezeCandidateReviewSection | None = None,
    paper_runtime_review: FreezeCandidateReviewSection | None = None,
) -> FreezeCandidateScore:
    """Compute official freeze candidate review score."""

    architecture = architecture_review or build_architecture_review(data)
    runtime = runtime_review or build_runtime_review(data)
    safety = safety_review or build_safety_review(data)
    observability = observability_review or build_observability_review(data)
    paper = paper_runtime_review or build_paper_runtime_review(data)
    orchestration = _average(
        (
            _score(data.cognitive_meta_supervision, "meta_supervision_score"),
            _score(data.cognitive_consensus, "cognitive_consensus_score", "consensus_score"),
            _score(data.cognitive_coherence, "cognitive_coherence_score", "coherence_score"),
            _readiness_score(data, "overall"),
        ),
        default=architecture.score,
    )
    recursive = _average(
        (
            _score(data.cognitive_recursive_regulation, "recursive_regulation_score"),
            _score(data.recursive_world_model, "world_model_coherence_score"),
        ),
        default=safety.score,
    )
    constitutional = _average(
        (
            _score(data.cognitive_constitutional, "constitutional_score"),
            _score(data.cognitive_safety_orchestrator, "safety_orchestrator_score"),
        ),
        default=safety.score,
    )
    execution = _average(
        (
            _bool_score(data.execution_isolated),
            _bool_score(data.broker_disabled),
            _bool_score(data.external_api_disabled),
            _bool_score(data.live_execution_disabled),
        )
    )
    recoverability = _average(
        (
            _bool_score(data.runtime_recoverable),
            _bool_score(data.rollback_ready),
            _bool_score(data.rollback_tested),
            _score(data.cognitive_continuity, "cognitive_continuity_score", "continuity_score"),
        )
    )
    weighted = _weighted_average(
        (
            (architecture.score, 1.1),
            (runtime.score, 1.1),
            (safety.score, 1.25),
            (observability.score, 1.0),
            (paper.score, 1.0),
            (orchestration, 1.0),
            (recursive, 1.0),
            (constitutional, 1.0),
            (execution, 1.2),
            (recoverability, 1.0),
        )
    )
    penalty = min(60, len(set(blockers)) * 6)
    overall = _clamp(weighted - penalty)
    critical_caps = {
        FreezeCandidateBlocker.EXECUTION_LEAK_RISK: 45,
        FreezeCandidateBlocker.KILL_SWITCH_ABSENT: 65,
        FreezeCandidateBlocker.REPLAY_UNSAFE: 70,
        FreezeCandidateBlocker.RECURSIVE_OVERFLOW_RISK: 70,
        FreezeCandidateBlocker.ARCHITECTURE_FRAGMENTATION: 78,
    }
    for blocker, cap in critical_caps.items():
        if blocker in blockers:
            overall = min(overall, cap)
    return FreezeCandidateScore(
        overall_score=overall,
        architecture_score=architecture.score,
        runtime_score=runtime.score,
        safety_score=safety.score,
        observability_score=observability.score,
        paper_runtime_score=paper.score,
        orchestration_score=orchestration,
        recursive_score=recursive,
        constitutional_score=constitutional,
        execution_isolation_score=execution,
        recoverability_score=recoverability,
    )


def _select_state(score: int, blockers: tuple[FreezeCandidateBlocker, ...]) -> FreezeCandidateState:
    blocker_count = len(set(blockers))
    if FreezeCandidateBlocker.EXECUTION_LEAK_RISK in blockers or score < 40 or blocker_count >= 6:
        return FreezeCandidateState.NOT_READY
    if blocker_count >= 3 or score < 68:
        return FreezeCandidateState.REVIEW_REQUIRED
    if blocker_count:
        return FreezeCandidateState.FREEZE_CANDIDATE
    if score >= 94:
        return FreezeCandidateState.READY_FOR_SANDBOX
    if score >= 88:
        return FreezeCandidateState.STABLE
    return FreezeCandidateState.FREEZE_CANDIDATE


def generate_freeze_candidate_recommendations(
    blockers: tuple[FreezeCandidateBlocker, ...],
    state: FreezeCandidateState | None = None,
) -> tuple[FreezeCandidateRecommendation, ...]:
    """Generate review recommendations from freeze candidate blockers."""

    recommendations: list[FreezeCandidateRecommendation] = []
    if blockers:
        recommendations.append(FreezeCandidateRecommendation.HOLD_FREEZE_APPROVAL)
    mapping = {
        FreezeCandidateBlocker.ARCHITECTURE_FRAGMENTATION: FreezeCandidateRecommendation.REDUCE_ARCHITECTURE_FRAGMENTATION,
        FreezeCandidateBlocker.RUNTIME_INSTABILITY: FreezeCandidateRecommendation.STABILIZE_RUNTIME,
        FreezeCandidateBlocker.OBSERVABILITY_GAP: FreezeCandidateRecommendation.COMPLETE_RUNTIME_OBSERVABILITY,
        FreezeCandidateBlocker.REPLAY_UNSAFE: FreezeCandidateRecommendation.HARDEN_REPLAY_SAFETY,
        FreezeCandidateBlocker.ROLLBACK_FAILURE_RISK: FreezeCandidateRecommendation.VERIFY_ROLLBACK_RECOVERY,
        FreezeCandidateBlocker.KILL_SWITCH_ABSENT: FreezeCandidateRecommendation.INSTALL_KILL_SWITCH,
        FreezeCandidateBlocker.EXECUTION_LEAK_RISK: FreezeCandidateRecommendation.SEAL_EXECUTION_BOUNDARY,
        FreezeCandidateBlocker.COGNITIVE_DRIFT: FreezeCandidateRecommendation.RECONCILE_COGNITIVE_DRIFT,
        FreezeCandidateBlocker.RECURSIVE_OVERFLOW_RISK: FreezeCandidateRecommendation.LIMIT_RECURSIVE_DEPTH,
        FreezeCandidateBlocker.SANDBOX_NOT_READY: FreezeCandidateRecommendation.PREPARE_SANDBOX_RUNTIME,
    }
    recommendations.extend(mapping[blocker] for blocker in blockers)
    recommendations.append(FreezeCandidateRecommendation.RUN_FREEZE_CANDIDATE_REVIEW_SUITE)
    if state in {FreezeCandidateState.STABLE, FreezeCandidateState.READY_FOR_SANDBOX}:
        recommendations.append(FreezeCandidateRecommendation.APPROVE_SANDBOX_ONLY_AFTER_MANUAL_REVIEW)
    return _dedupe(recommendations)


def evaluate_freeze_candidate(data: FreezeCandidateReviewInput) -> FreezeCandidateReviewResult:
    """Evaluate whether AGIcore can be considered freeze candidate, stable or sandbox-ready."""

    architecture = build_architecture_review(data)
    runtime = build_runtime_review(data)
    safety = build_safety_review(data)
    observability = build_observability_review(data)
    paper = build_paper_runtime_review(data)
    blockers = detect_freeze_candidate_blockers(data, architecture, runtime, safety, observability, paper)
    score = compute_freeze_candidate_score(data, blockers, architecture, runtime, safety, observability, paper)
    state = _select_state(score.overall_score, blockers)
    recommendations = generate_freeze_candidate_recommendations(blockers, state)
    offline_only = data.broker_disabled and data.external_api_disabled and data.live_execution_disabled
    summary = f"{state.value}: score={score.overall_score}, blockers={len(blockers)}, offline_only={offline_only}"
    return FreezeCandidateReviewResult(
        state=state,
        freeze_candidate_score=score.overall_score,
        score_breakdown=score,
        blockers=blockers,
        architecture_review=architecture,
        runtime_review=runtime,
        safety_review=safety,
        observability_review=observability,
        paper_runtime_review=paper,
        recommendations=recommendations,
        offline_only=offline_only,
        summary=summary,
    )


def render_freeze_candidate_markdown(result: FreezeCandidateReviewResult) -> str:
    """Render an explainable freeze candidate review report."""

    lines = [
        "# AGIcore Freeze Candidate Review",
        f"- State: {result.state.value}",
        f"- Score: {result.freeze_candidate_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Score Breakdown",
        f"- Architecture: {result.score_breakdown.architecture_score}/100",
        f"- Runtime: {result.score_breakdown.runtime_score}/100",
        f"- Safety: {result.score_breakdown.safety_score}/100",
        f"- Observability: {result.score_breakdown.observability_score}/100",
        f"- Paper runtime: {result.score_breakdown.paper_runtime_score}/100",
        f"- Orchestration: {result.score_breakdown.orchestration_score}/100",
        f"- Recursive regulation: {result.score_breakdown.recursive_score}/100",
        f"- Constitutional integrity: {result.score_breakdown.constitutional_score}/100",
        f"- Execution isolation: {result.score_breakdown.execution_isolation_score}/100",
        f"- Recoverability: {result.score_breakdown.recoverability_score}/100",
        "",
        "# Review Sections",
    ]
    for section in (
        result.architecture_review,
        result.runtime_review,
        result.safety_review,
        result.observability_review,
        result.paper_runtime_review,
    ):
        lines.append(
            f"- {section.name}: passed={section.passed}, score={section.score}/100, "
            f"blockers={', '.join(blocker.value for blocker in section.blockers) or 'none'}"
        )
        lines.extend(f"  - {item}" for item in section.evidence)
    lines.append("")
    lines.append("# Freeze Candidate Blockers")
    lines.extend(f"- {blocker.value}" for blocker in result.blockers) if result.blockers else lines.append("- none")
    lines.append("")
    lines.append("# Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    lines.append("")
    lines.append("# Freeze Candidate Outlook")
    if result.state == FreezeCandidateState.READY_FOR_SANDBOX:
        lines.append("- Sandbox or paper try can be reviewed for manual approval.")
    elif result.state == FreezeCandidateState.STABLE:
        lines.append("- Freeze stability is established; sandbox readiness still requires review.")
    elif result.state == FreezeCandidateState.FREEZE_CANDIDATE:
        lines.append("- Freeze candidacy is plausible but remaining blockers must be closed.")
    else:
        lines.append("- Freeze approval should remain blocked until review issues are resolved.")
    return "\n".join(lines)


__all__ = [
    "build_architecture_review",
    "build_observability_review",
    "build_paper_runtime_review",
    "build_runtime_review",
    "build_safety_review",
    "compute_freeze_candidate_score",
    "detect_freeze_candidate_blockers",
    "evaluate_freeze_candidate",
    "generate_freeze_candidate_recommendations",
    "render_freeze_candidate_markdown",
]
