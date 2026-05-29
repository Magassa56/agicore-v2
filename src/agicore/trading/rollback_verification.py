"""Offline rollback verification for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.rollback_verification_models import (
    RollbackGraph,
    RollbackRecommendation,
    RollbackReviewSection,
    RollbackRisk,
    RollbackScore,
    RollbackState,
    RollbackVerificationInput,
    RollbackVerificationResult,
)


def _coerce_input(data: RollbackVerificationInput | Mapping[str, Any]) -> RollbackVerificationInput:
    if isinstance(data, RollbackVerificationInput):
        return data
    return RollbackVerificationInput(**dict(data))


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


def _upstream_risks(data: RollbackVerificationInput) -> tuple[Any, ...]:
    upstream = (
        data.kill_switch_verification,
        data.runtime_isolation_review,
        data.sandbox_readiness_audit,
        data.stable_review,
        data.freeze_candidate_review,
    )
    risks: tuple[Any, ...] = ()
    for item in upstream:
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream(data: RollbackVerificationInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _upstream_score(data: RollbackVerificationInput, *names: str) -> int | None:
    upstream = (
        data.kill_switch_verification,
        data.runtime_isolation_review,
        data.sandbox_readiness_audit,
        data.stable_review,
        data.freeze_candidate_review,
    )
    values: list[int] = []
    for item in upstream:
        values.extend(_score(item, name) for name in names)
        breakdown = _get(item, "score_breakdown")
        values.extend(_score(breakdown, name) for name in names)
    values = [value for value in values if value is not None]
    return _average(values) if values else None


def verify_state_snapshot(data: RollbackVerificationInput | Mapping[str, Any]) -> RollbackReviewSection:
    """Verify safe rollback state snapshot availability and integrity."""

    data = _coerce_input(data)
    score = _clamp(data.state_snapshot_score) if data.state_snapshot_score is not None else _average(
        (
            _bool_score(data.snapshot_available),
            _bool_score(data.snapshot_integrity_valid),
            _bool_score(data.snapshot_recent),
            _bool_score(data.snapshot_isolated),
            _upstream_score(data, "recovery_safety_score", "rollback_score"),
        ),
        default=45,
    )
    risks: list[RollbackRisk] = []
    if data.snapshot_available is not True or data.snapshot_isolated is not True:
        risks.append(RollbackRisk.SNAPSHOT_MISSING)
    if data.snapshot_integrity_valid is not True or data.snapshot_recent is not True or score < 80:
        risks.append(RollbackRisk.STATE_CORRUPTION_AFTER_ROLLBACK)
    evidence = (
        f"state_snapshot_score={score}/100",
        f"snapshot_available={data.snapshot_available}",
        f"snapshot_integrity_valid={data.snapshot_integrity_valid}",
        f"snapshot_recent={data.snapshot_recent}",
        f"snapshot_isolated={data.snapshot_isolated}",
    )
    return RollbackReviewSection(
        name="state_snapshot_review",
        score=score,
        passed=not risks and score >= 85,
        risks=_dedupe(risks),
        evidence=evidence,
    )


def verify_recovery_point(data: RollbackVerificationInput | Mapping[str, Any]) -> RollbackReviewSection:
    """Verify that a valid recovery point and recovery path exist."""

    data = _coerce_input(data)
    score = _clamp(data.recovery_point_score) if data.recovery_point_score is not None else _average(
        (
            _bool_score(data.recovery_point_available),
            _bool_score(data.recovery_point_valid),
            _bool_score(data.recovery_point_compatible),
            _bool_score(data.recovery_path_available),
            _upstream_score(data, "recovery_safety_score"),
        ),
        default=45,
    )
    risks: list[RollbackRisk] = []
    if (
        data.recovery_point_available is not True
        or data.recovery_point_valid is not True
        or data.recovery_point_compatible is not True
        or score < 80
        or _has_upstream(data, "RECOVERY_POINT", "RECOVERY_PATH_CORRUPTION")
    ):
        risks.append(RollbackRisk.RECOVERY_POINT_INVALID)
    if data.recovery_path_available is not True or _has_upstream(data, "RECOVERY_PATH_MISSING"):
        risks.append(RollbackRisk.RECOVERY_PATH_MISSING)
    evidence = (
        f"recovery_point_score={score}/100",
        f"recovery_point_available={data.recovery_point_available}",
        f"recovery_point_valid={data.recovery_point_valid}",
        f"recovery_point_compatible={data.recovery_point_compatible}",
        f"recovery_path_available={data.recovery_path_available}",
    )
    return RollbackReviewSection(
        name="recovery_point_review",
        score=score,
        passed=not risks and score >= 85,
        risks=_dedupe(risks),
        evidence=evidence,
    )


def verify_runtime_restore(data: RollbackVerificationInput | Mapping[str, Any]) -> RollbackReviewSection:
    """Verify runtime restoration and restart safety after rollback."""

    data = _coerce_input(data)
    score = _clamp(data.runtime_restore_score) if data.runtime_restore_score is not None else _average(
        (
            _bool_score(data.runtime_restore_tested),
            _bool_score(data.runtime_restore_deterministic),
            _bool_score(data.runtime_state_clean),
            _bool_score(data.unsafe_restart_blocked),
        ),
        default=45,
    )
    risks: list[RollbackRisk] = []
    if (
        data.runtime_restore_tested is not True
        or data.runtime_restore_deterministic is not True
        or score < 80
        or _has_upstream(data, "RUNTIME_RESTORE", "RUNTIME_INSTABILITY")
    ):
        risks.append(RollbackRisk.RUNTIME_RESTORE_FAILURE)
    if data.runtime_state_clean is not True:
        risks.append(RollbackRisk.STATE_CORRUPTION_AFTER_ROLLBACK)
    if data.unsafe_restart_blocked is not True:
        risks.append(RollbackRisk.UNSAFE_RESTART_RISK)
    evidence = (
        f"runtime_restore_score={score}/100",
        f"runtime_restore_tested={data.runtime_restore_tested}",
        f"runtime_restore_deterministic={data.runtime_restore_deterministic}",
        f"runtime_state_clean={data.runtime_state_clean}",
        f"unsafe_restart_blocked={data.unsafe_restart_blocked}",
    )
    return RollbackReviewSection(
        name="runtime_restore_review",
        score=score,
        passed=not risks and score >= 80,
        risks=_dedupe(risks),
        evidence=evidence,
    )


def verify_memory_restore(data: RollbackVerificationInput | Mapping[str, Any]) -> RollbackReviewSection:
    """Verify memory restoration and contamination isolation."""

    data = _coerce_input(data)
    score = _clamp(data.memory_restore_score) if data.memory_restore_score is not None else _average(
        (
            _bool_score(data.memory_restore_tested),
            _bool_score(data.memory_namespace_restored),
            _bool_score(data.memory_checksum_valid),
            _bool_score(data.memory_contamination_absent),
        ),
        default=45,
    )
    risks: list[RollbackRisk] = []
    if (
        data.memory_restore_tested is not True
        or data.memory_namespace_restored is not True
        or data.memory_checksum_valid is not True
        or data.memory_contamination_absent is not True
        or score < 80
        or _has_upstream(data, "MEMORY_RESTORE", "MEMORY_CROSS")
    ):
        risks.append(RollbackRisk.MEMORY_RESTORE_FAILURE)
    if data.memory_checksum_valid is not True or data.memory_contamination_absent is not True:
        risks.append(RollbackRisk.STATE_CORRUPTION_AFTER_ROLLBACK)
    evidence = (
        f"memory_restore_score={score}/100",
        f"memory_restore_tested={data.memory_restore_tested}",
        f"memory_namespace_restored={data.memory_namespace_restored}",
        f"memory_checksum_valid={data.memory_checksum_valid}",
        f"memory_contamination_absent={data.memory_contamination_absent}",
    )
    return RollbackReviewSection(
        name="memory_restore_review",
        score=score,
        passed=not risks and score >= 80,
        risks=_dedupe(risks),
        evidence=evidence,
    )


def verify_execution_rollback(data: RollbackVerificationInput | Mapping[str, Any]) -> RollbackReviewSection:
    """Verify simulated execution rollback without broker or live order impact."""

    data = _coerce_input(data)
    score = _clamp(data.execution_rollback_score) if data.execution_rollback_score is not None else _average(
        (
            _bool_score(data.execution_rollback_tested),
            _bool_score(data.simulated_orders_reverted),
            _bool_score(data.broker_state_unchanged),
            _bool_score(data.execution_queue_restored),
            _upstream_score(data, "execution_stop_score", "isolation_score"),
        ),
        default=45,
    )
    risks: list[RollbackRisk] = []
    if (
        data.execution_rollback_tested is not True
        or data.simulated_orders_reverted is not True
        or data.broker_state_unchanged is not True
        or data.execution_queue_restored is not True
        or score < 85
        or _has_upstream(data, "EXECUTION_ROLLBACK", "EXECUTION_CONTINUATION", "BROKER")
    ):
        risks.append(RollbackRisk.EXECUTION_ROLLBACK_FAILURE)
    evidence = (
        f"execution_rollback_score={score}/100",
        f"execution_rollback_tested={data.execution_rollback_tested}",
        f"simulated_orders_reverted={data.simulated_orders_reverted}",
        f"broker_state_unchanged={data.broker_state_unchanged}",
        f"execution_queue_restored={data.execution_queue_restored}",
    )
    return RollbackReviewSection(
        name="execution_rollback_review",
        score=score,
        passed=not risks and score >= 85,
        risks=tuple(risks),
        evidence=evidence,
    )


def _rollback_safety_review(data: RollbackVerificationInput | Mapping[str, Any]) -> RollbackReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.rollback_safety_score) if data.rollback_safety_score is not None else _average(
        (
            _bool_score(data.post_rollback_state_valid),
            _bool_score(data.partial_rollback_detected is False),
            _bool_score(data.rollback_observable),
            _bool_score(data.rollback_audit_logged),
        ),
        default=45,
    )
    risks: list[RollbackRisk] = []
    if data.post_rollback_state_valid is not True or score < 80:
        risks.append(RollbackRisk.STATE_CORRUPTION_AFTER_ROLLBACK)
    if data.partial_rollback_detected is not False:
        risks.append(RollbackRisk.PARTIAL_ROLLBACK_RISK)
    if data.rollback_observable is not True or data.rollback_audit_logged is not True:
        risks.append(RollbackRisk.ROLLBACK_OBSERVABILITY_GAP)
    evidence = (
        f"rollback_safety_score={score}/100",
        f"post_rollback_state_valid={data.post_rollback_state_valid}",
        f"partial_rollback_detected={data.partial_rollback_detected}",
        f"rollback_observable={data.rollback_observable}",
        f"rollback_audit_logged={data.rollback_audit_logged}",
    )
    return RollbackReviewSection(
        name="rollback_safety_review",
        score=score,
        passed=not risks and score >= 80,
        risks=_dedupe(risks),
        evidence=evidence,
    )


def _build_rollback_graph(risks: tuple[RollbackRisk, ...]) -> RollbackGraph:
    nodes = (
        "error_event",
        "state_snapshot",
        "recovery_point",
        "runtime_restore",
        "memory_restore",
        "execution_rollback",
        "safe_state",
        "observability_log",
    )
    edges = (
        ("error_event", "state_snapshot", "selects"),
        ("state_snapshot", "recovery_point", "anchors"),
        ("recovery_point", "runtime_restore", "restores"),
        ("recovery_point", "memory_restore", "restores"),
        ("recovery_point", "execution_rollback", "reverts"),
        ("runtime_restore", "safe_state", "validates"),
        ("safe_state", "observability_log", "records"),
    )
    failed_edges: list[tuple[str, str]] = []
    if RollbackRisk.SNAPSHOT_MISSING in risks:
        failed_edges.append(("error_event", "state_snapshot"))
    if RollbackRisk.RECOVERY_POINT_INVALID in risks or RollbackRisk.RECOVERY_PATH_MISSING in risks:
        failed_edges.append(("state_snapshot", "recovery_point"))
    if RollbackRisk.RUNTIME_RESTORE_FAILURE in risks or RollbackRisk.UNSAFE_RESTART_RISK in risks:
        failed_edges.append(("recovery_point", "runtime_restore"))
    if RollbackRisk.MEMORY_RESTORE_FAILURE in risks:
        failed_edges.append(("recovery_point", "memory_restore"))
    if RollbackRisk.EXECUTION_ROLLBACK_FAILURE in risks:
        failed_edges.append(("recovery_point", "execution_rollback"))
    if (
        RollbackRisk.STATE_CORRUPTION_AFTER_ROLLBACK in risks
        or RollbackRisk.PARTIAL_ROLLBACK_RISK in risks
    ):
        failed_edges.append(("runtime_restore", "safe_state"))
    if RollbackRisk.ROLLBACK_OBSERVABILITY_GAP in risks:
        failed_edges.append(("safe_state", "observability_log"))
    return RollbackGraph(
        nodes=nodes,
        edges=edges,
        restore_edges=(
            ("recovery_point", "runtime_restore"),
            ("recovery_point", "memory_restore"),
            ("recovery_point", "execution_rollback"),
        ),
        failed_edges=_dedupe(failed_edges),
    )


def detect_rollback_risks(
    data: RollbackVerificationInput | Mapping[str, Any],
    state_snapshot_review: RollbackReviewSection | None = None,
    recovery_point_review: RollbackReviewSection | None = None,
    runtime_restore_review: RollbackReviewSection | None = None,
    memory_restore_review: RollbackReviewSection | None = None,
    execution_rollback_review: RollbackReviewSection | None = None,
    rollback_safety_review: RollbackReviewSection | None = None,
) -> tuple[RollbackRisk, ...]:
    """Detect rollback verification risks."""

    data = _coerce_input(data)
    sections = (
        state_snapshot_review or verify_state_snapshot(data),
        recovery_point_review or verify_recovery_point(data),
        runtime_restore_review or verify_runtime_restore(data),
        memory_restore_review or verify_memory_restore(data),
        execution_rollback_review or verify_execution_rollback(data),
        rollback_safety_review or _rollback_safety_review(data),
    )
    risks: list[RollbackRisk] = []
    for section in sections:
        risks.extend(section.risks)
    return _dedupe(risks)


def compute_rollback_score(
    data: RollbackVerificationInput | Mapping[str, Any],
    risks: tuple[RollbackRisk, ...] = (),
    state_snapshot_review: RollbackReviewSection | None = None,
    recovery_point_review: RollbackReviewSection | None = None,
    runtime_restore_review: RollbackReviewSection | None = None,
    memory_restore_review: RollbackReviewSection | None = None,
    execution_rollback_review: RollbackReviewSection | None = None,
    rollback_safety_review: RollbackReviewSection | None = None,
) -> RollbackScore:
    """Compute rollback verification score normalized to 0..100."""

    data = _coerce_input(data)
    snapshot = state_snapshot_review or verify_state_snapshot(data)
    recovery = recovery_point_review or verify_recovery_point(data)
    runtime = runtime_restore_review or verify_runtime_restore(data)
    memory = memory_restore_review or verify_memory_restore(data)
    execution = execution_rollback_review or verify_execution_rollback(data)
    safety = rollback_safety_review or _rollback_safety_review(data)
    observability_score = data.observability_score if data.observability_score is not None else _average(
        (
            _bool_score(data.rollback_observable),
            _bool_score(data.rollback_audit_logged),
            _upstream_score(data, "observability_score"),
        )
    )
    weighted = _weighted_average(
        (
            (snapshot.score, 1.25),
            (recovery.score, 1.25),
            (runtime.score, 1.15),
            (memory.score, 1.0),
            (execution.score, 1.15),
            (safety.score, 1.0),
            (observability_score, 0.75),
        )
    )
    penalty = min(70, len(set(risks)) * 7)
    overall = _clamp(weighted - penalty)
    critical_caps = {
        RollbackRisk.SNAPSHOT_MISSING: 45,
        RollbackRisk.RECOVERY_POINT_INVALID: 50,
        RollbackRisk.RUNTIME_RESTORE_FAILURE: 50,
        RollbackRisk.MEMORY_RESTORE_FAILURE: 55,
        RollbackRisk.EXECUTION_ROLLBACK_FAILURE: 45,
        RollbackRisk.STATE_CORRUPTION_AFTER_ROLLBACK: 55,
        RollbackRisk.RECOVERY_PATH_MISSING: 50,
    }
    for risk, cap in critical_caps.items():
        if risk in risks:
            overall = min(overall, cap)
    return RollbackScore(
        overall_score=overall,
        state_snapshot_score=snapshot.score,
        recovery_point_score=recovery.score,
        runtime_restore_score=runtime.score,
        memory_restore_score=memory.score,
        execution_rollback_score=execution.score,
        rollback_safety_score=safety.score,
        observability_score=_clamp(observability_score),
    )


def _select_state(
    score: int,
    risks: tuple[RollbackRisk, ...],
    ready_for_observability_verification: bool | None,
) -> RollbackState:
    risk_count = len(set(risks))
    hard_risks = {
        RollbackRisk.SNAPSHOT_MISSING,
        RollbackRisk.RECOVERY_POINT_INVALID,
        RollbackRisk.RUNTIME_RESTORE_FAILURE,
        RollbackRisk.EXECUTION_ROLLBACK_FAILURE,
        RollbackRisk.RECOVERY_PATH_MISSING,
    }
    if hard_risks.intersection(risks) or score < 45 or risk_count >= 6:
        return RollbackState.NOT_VERIFIED
    if risk_count >= 3 or score < 72:
        return RollbackState.REVIEW_REQUIRED
    if risk_count:
        return RollbackState.PARTIALLY_VERIFIED
    if score >= 94 and ready_for_observability_verification is True:
        return RollbackState.READY_FOR_OBSERVABILITY_VERIFICATION
    if score >= 88:
        return RollbackState.VERIFIED
    return RollbackState.PARTIALLY_VERIFIED


def generate_rollback_recommendations(
    risks: tuple[RollbackRisk, ...],
    state: RollbackState | None = None,
) -> tuple[RollbackRecommendation, ...]:
    """Generate rollback verification recommendations."""

    recommendations: list[RollbackRecommendation] = []
    if risks:
        recommendations.append(RollbackRecommendation.HOLD_ROLLBACK_APPROVAL)
    mapping = {
        RollbackRisk.SNAPSHOT_MISSING: RollbackRecommendation.CREATE_SAFE_STATE_SNAPSHOT,
        RollbackRisk.RECOVERY_POINT_INVALID: RollbackRecommendation.REPAIR_RECOVERY_POINT,
        RollbackRisk.RUNTIME_RESTORE_FAILURE: RollbackRecommendation.VERIFY_RUNTIME_RESTORE,
        RollbackRisk.MEMORY_RESTORE_FAILURE: RollbackRecommendation.VERIFY_MEMORY_RESTORE,
        RollbackRisk.EXECUTION_ROLLBACK_FAILURE: RollbackRecommendation.VERIFY_EXECUTION_ROLLBACK,
        RollbackRisk.STATE_CORRUPTION_AFTER_ROLLBACK: (
            RollbackRecommendation.REVALIDATE_POST_ROLLBACK_STATE
        ),
        RollbackRisk.PARTIAL_ROLLBACK_RISK: RollbackRecommendation.PREVENT_PARTIAL_ROLLBACK,
        RollbackRisk.UNSAFE_RESTART_RISK: RollbackRecommendation.BLOCK_UNSAFE_RESTART,
        RollbackRisk.RECOVERY_PATH_MISSING: RollbackRecommendation.RESTORE_RECOVERY_PATH,
        RollbackRisk.ROLLBACK_OBSERVABILITY_GAP: RollbackRecommendation.ADD_ROLLBACK_OBSERVABILITY,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(RollbackRecommendation.RUN_ROLLBACK_VERIFICATION_SUITE)
    if state == RollbackState.READY_FOR_OBSERVABILITY_VERIFICATION:
        recommendations.append(
            RollbackRecommendation.APPROVE_OBSERVABILITY_VERIFICATION_AFTER_MANUAL_REVIEW
        )
    return _dedupe(recommendations)


def evaluate_rollback(
    data: RollbackVerificationInput | Mapping[str, Any],
) -> RollbackVerificationResult:
    """Evaluate whether AGIcore can roll back to a safe state offline."""

    data = _coerce_input(data)
    snapshot = verify_state_snapshot(data)
    recovery = verify_recovery_point(data)
    runtime = verify_runtime_restore(data)
    memory = verify_memory_restore(data)
    execution = verify_execution_rollback(data)
    safety = _rollback_safety_review(data)
    risks = detect_rollback_risks(data, snapshot, recovery, runtime, memory, execution, safety)
    score = compute_rollback_score(data, risks, snapshot, recovery, runtime, memory, execution, safety)
    state = _select_state(score.overall_score, risks, data.ready_for_observability_verification)
    graph = _build_rollback_graph(risks)
    recommendations = generate_rollback_recommendations(risks, state)
    offline_only = data.broker_state_unchanged is True and not _has_upstream(data, "LIVE_EXECUTION", "API_ACCESS")
    summary = f"{state.value}: score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return RollbackVerificationResult(
        state=state,
        rollback_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        state_snapshot_review=snapshot,
        recovery_point_review=recovery,
        runtime_restore_review=runtime,
        memory_restore_review=memory,
        execution_rollback_review=execution,
        rollback_graph=graph,
        recommendations=recommendations,
        offline_only=offline_only,
        summary=summary,
    )


def render_rollback_markdown(result: RollbackVerificationResult) -> str:
    """Render an explainable rollback verification report."""

    lines = [
        "# AGIcore Rollback Verification",
        f"- State: {result.state.value}",
        f"- Score: {result.rollback_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Score Breakdown",
        f"- State snapshot: {result.score_breakdown.state_snapshot_score}/100",
        f"- Recovery point: {result.score_breakdown.recovery_point_score}/100",
        f"- Runtime restore: {result.score_breakdown.runtime_restore_score}/100",
        f"- Memory restore: {result.score_breakdown.memory_restore_score}/100",
        f"- Execution rollback: {result.score_breakdown.execution_rollback_score}/100",
        f"- Rollback safety: {result.score_breakdown.rollback_safety_score}/100",
        f"- Observability: {result.score_breakdown.observability_score}/100",
        "",
        "# Rollback Reviews",
    ]
    for section in (
        result.state_snapshot_review,
        result.recovery_point_review,
        result.runtime_restore_review,
        result.memory_restore_review,
        result.execution_rollback_review,
    ):
        lines.append(
            f"- {section.name}: passed={section.passed}, score={section.score}/100, "
            f"risks={', '.join(risk.value for risk in section.risks) or 'none'}"
        )
        lines.extend(f"  - {item}" for item in section.evidence)
    lines.append("")
    lines.append("# Rollback Graph")
    lines.append(f"- Nodes: {', '.join(result.rollback_graph.nodes)}")
    lines.extend(
        f"- Edge: {source} -> {target} ({label})"
        for source, target, label in result.rollback_graph.edges
    )
    lines.append(
        "- Failed edges: "
        + (
            ", ".join(f"{source}->{target}" for source, target in result.rollback_graph.failed_edges)
            or "none"
        )
    )
    lines.append("")
    lines.append("# Rollback Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Rollback Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    lines.append("")
    lines.append("# Verification Outlook")
    if result.state == RollbackState.READY_FOR_OBSERVABILITY_VERIFICATION:
        lines.append("- Rollback is ready for manual observability verification review.")
    elif result.state == RollbackState.VERIFIED:
        lines.append("- Rollback is verified; observability verification remains gated.")
    elif result.state == RollbackState.PARTIALLY_VERIFIED:
        lines.append("- Rollback is partially verified and remaining risks must be resolved.")
    else:
        lines.append("- Rollback approval should remain blocked.")
    return "\n".join(lines)


__all__ = [
    "compute_rollback_score",
    "detect_rollback_risks",
    "evaluate_rollback",
    "generate_rollback_recommendations",
    "render_rollback_markdown",
    "verify_execution_rollback",
    "verify_memory_restore",
    "verify_recovery_point",
    "verify_runtime_restore",
    "verify_state_snapshot",
]
