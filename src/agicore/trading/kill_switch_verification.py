"""Offline kill switch verification for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.kill_switch_verification_models import (
    KillSwitchGraph,
    KillSwitchRecommendation,
    KillSwitchReviewSection,
    KillSwitchRisk,
    KillSwitchScore,
    KillSwitchState,
    KillSwitchVerificationInput,
    KillSwitchVerificationResult,
)


def _coerce_input(data: KillSwitchVerificationInput | Mapping[str, Any]) -> KillSwitchVerificationInput:
    if isinstance(data, KillSwitchVerificationInput):
        return data
    return KillSwitchVerificationInput(**dict(data))


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


def _latency_score(latency_ms: int | float | None, max_latency_ms: int | float | None) -> int | None:
    if latency_ms is None:
        return None
    threshold = max(float(max_latency_ms or 1), 1.0)
    if latency_ms <= threshold:
        return 100
    if latency_ms >= threshold * 4:
        return 0
    return _clamp(100 - ((float(latency_ms) - threshold) / (threshold * 3)) * 100)


def _dedupe(items: Iterable[Any]) -> tuple[Any, ...]:
    seen: set[Any] = set()
    result: list[Any] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return tuple(result)


def _upstream_risks(data: KillSwitchVerificationInput) -> tuple[Any, ...]:
    upstream = (
        data.runtime_isolation_review,
        data.sandbox_readiness_audit,
        data.stable_review,
        data.freeze_candidate_review,
        data.freeze_readiness_audit,
    )
    risks: tuple[Any, ...] = ()
    for item in upstream:
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream(data: KillSwitchVerificationInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _runtime_isolation_score(data: KillSwitchVerificationInput) -> int | None:
    review = data.runtime_isolation_review
    return _score(review, "kill_switch_score", "isolation_score", "sandbox_score", "score")


def _sandbox_kill_switch_score(data: KillSwitchVerificationInput) -> int | None:
    audit = data.sandbox_readiness_audit
    if audit is None:
        return None
    breakdown = _get(audit, "score_breakdown")
    return _score(breakdown, "kill_switch_score") or _score(audit, "sandbox_score")


def verify_shutdown_path(data: KillSwitchVerificationInput | Mapping[str, Any]) -> KillSwitchReviewSection:
    """Verify that the kill signal can trigger a bounded shutdown path."""

    data = _coerce_input(data)
    latency_score = _latency_score(data.shutdown_latency_ms, data.max_shutdown_latency_ms)
    score = _clamp(data.shutdown_path_score) if data.shutdown_path_score is not None else _average(
        (
            _bool_score(data.kill_switch_present),
            _bool_score(data.kill_signal_registered),
            _bool_score(data.shutdown_path_tested),
            _bool_score(data.shutdown_idempotent),
            latency_score,
            _sandbox_kill_switch_score(data),
        ),
        default=45,
    )
    risks: list[KillSwitchRisk] = []
    if (
        data.kill_switch_present is not True
        or data.kill_signal_registered is not True
        or _has_upstream(data, "KILL_SWITCH")
    ):
        risks.append(KillSwitchRisk.KILL_SWITCH_FAILURE)
    if data.shutdown_path_tested is not True or data.shutdown_idempotent is not True or score < 80:
        risks.append(KillSwitchRisk.SHUTDOWN_PATH_FAILURE)
    if latency_score is not None and latency_score < 85:
        risks.append(KillSwitchRisk.EMERGENCY_RESPONSE_DELAY)
    evidence = (
        f"shutdown_path_score={score}/100",
        f"kill_switch_present={data.kill_switch_present}",
        f"kill_signal_registered={data.kill_signal_registered}",
        f"shutdown_path_tested={data.shutdown_path_tested}",
        f"shutdown_latency_ms={data.shutdown_latency_ms}",
    )
    return KillSwitchReviewSection(
        name="shutdown_path_review",
        score=score,
        passed=not risks and score >= 85,
        risks=_dedupe(risks),
        evidence=evidence,
    )


def verify_execution_stop(data: KillSwitchVerificationInput | Mapping[str, Any]) -> KillSwitchReviewSection:
    """Verify that simulated execution cannot continue after the kill signal."""

    data = _coerce_input(data)
    score = _clamp(data.execution_stop_score) if data.execution_stop_score is not None else _average(
        (
            _bool_score(data.execution_stop_signal_propagates),
            _bool_score(data.simulated_orders_cancelled),
            _bool_score(data.broker_path_blocked),
            _bool_score(data.execution_queue_drained),
            _runtime_isolation_score(data),
        ),
        default=45,
    )
    risks: list[KillSwitchRisk] = []
    if (
        data.execution_stop_signal_propagates is not True
        or data.simulated_orders_cancelled is not True
        or data.broker_path_blocked is not True
        or data.execution_queue_drained is not True
        or score < 85
        or _has_upstream(data, "EXECUTION_CONTINUATION", "EXECUTION_BOUNDARY", "LIVE_EXECUTION")
    ):
        risks.append(KillSwitchRisk.EXECUTION_CONTINUATION)
    evidence = (
        f"execution_stop_score={score}/100",
        f"execution_stop_signal_propagates={data.execution_stop_signal_propagates}",
        f"simulated_orders_cancelled={data.simulated_orders_cancelled}",
        f"broker_path_blocked={data.broker_path_blocked}",
        f"execution_queue_drained={data.execution_queue_drained}",
    )
    return KillSwitchReviewSection(
        name="execution_stop_review",
        score=score,
        passed=not risks and score >= 85,
        risks=tuple(risks),
        evidence=evidence,
    )


def verify_cognitive_stop(data: KillSwitchVerificationInput | Mapping[str, Any]) -> KillSwitchReviewSection:
    """Verify that cognitive and recursive loops stop on critical signal."""

    data = _coerce_input(data)
    score = _clamp(data.cognitive_stop_score) if data.cognitive_stop_score is not None else _average(
        (
            _bool_score(data.cognitive_stop_signal_propagates),
            _bool_score(data.cognitive_loops_drained),
            _bool_score(data.recursive_tasks_cancelled),
            _bool_score(data.new_cognitive_tasks_blocked),
        ),
        default=45,
    )
    risks: list[KillSwitchRisk] = []
    if (
        data.cognitive_stop_signal_propagates is not True
        or data.cognitive_loops_drained is not True
        or data.recursive_tasks_cancelled is not True
        or data.new_cognitive_tasks_blocked is not True
        or score < 80
        or _has_upstream(data, "COGNITIVE_LOOP", "RECURSIVE_OVERFLOW", "COGNITIVE_DRIFT")
    ):
        risks.append(KillSwitchRisk.COGNITIVE_LOOP_CONTINUATION)
    evidence = (
        f"cognitive_stop_score={score}/100",
        f"cognitive_stop_signal_propagates={data.cognitive_stop_signal_propagates}",
        f"cognitive_loops_drained={data.cognitive_loops_drained}",
        f"recursive_tasks_cancelled={data.recursive_tasks_cancelled}",
        f"new_cognitive_tasks_blocked={data.new_cognitive_tasks_blocked}",
    )
    return KillSwitchReviewSection(
        name="cognitive_stop_review",
        score=score,
        passed=not risks and score >= 80,
        risks=tuple(risks),
        evidence=evidence,
    )


def verify_runtime_halt(data: KillSwitchVerificationInput | Mapping[str, Any]) -> KillSwitchReviewSection:
    """Verify that runtime workers and schedulers halt on critical signal."""

    data = _coerce_input(data)
    score = _clamp(data.runtime_halt_score) if data.runtime_halt_score is not None else _average(
        (
            _bool_score(data.runtime_halt_signal_propagates),
            _bool_score(data.schedulers_stopped),
            _bool_score(data.event_bus_quiesced),
            _bool_score(data.background_workers_stopped),
        ),
        default=45,
    )
    risks: list[KillSwitchRisk] = []
    if (
        data.runtime_halt_signal_propagates is not True
        or data.schedulers_stopped is not True
        or data.event_bus_quiesced is not True
        or data.background_workers_stopped is not True
        or score < 80
        or _has_upstream(data, "RUNTIME_HALT", "RUNTIME_INSTABILITY")
    ):
        risks.append(KillSwitchRisk.RUNTIME_HALT_FAILURE)
    evidence = (
        f"runtime_halt_score={score}/100",
        f"runtime_halt_signal_propagates={data.runtime_halt_signal_propagates}",
        f"schedulers_stopped={data.schedulers_stopped}",
        f"event_bus_quiesced={data.event_bus_quiesced}",
        f"background_workers_stopped={data.background_workers_stopped}",
    )
    return KillSwitchReviewSection(
        name="runtime_halt_review",
        score=score,
        passed=not risks and score >= 80,
        risks=tuple(risks),
        evidence=evidence,
    )


def verify_emergency_lockdown(data: KillSwitchVerificationInput | Mapping[str, Any]) -> KillSwitchReviewSection:
    """Verify emergency lockdown and recovery safety controls."""

    data = _coerce_input(data)
    score = _clamp(data.emergency_lockdown_score) if data.emergency_lockdown_score is not None else _average(
        (
            _bool_score(data.emergency_lockdown_available),
            _bool_score(data.safety_overrides_blocked),
            _bool_score(data.lockdown_idempotent),
            _bool_score(data.lockdown_audit_logged),
        ),
        default=45,
    )
    risks: list[KillSwitchRisk] = []
    if (
        data.emergency_lockdown_available is not True
        or data.lockdown_idempotent is not True
        or data.lockdown_audit_logged is not True
        or score < 80
        or _has_upstream(data, "LOCKDOWN")
    ):
        risks.append(KillSwitchRisk.LOCKDOWN_FAILURE)
    if data.safety_overrides_blocked is not True or _has_upstream(data, "SAFETY_OVERRIDE"):
        risks.append(KillSwitchRisk.SAFETY_OVERRIDE_RISK)
    evidence = (
        f"emergency_lockdown_score={score}/100",
        f"emergency_lockdown_available={data.emergency_lockdown_available}",
        f"safety_overrides_blocked={data.safety_overrides_blocked}",
        f"lockdown_idempotent={data.lockdown_idempotent}",
        f"lockdown_audit_logged={data.lockdown_audit_logged}",
    )
    return KillSwitchReviewSection(
        name="emergency_lockdown_review",
        score=score,
        passed=not risks and score >= 80,
        risks=_dedupe(risks),
        evidence=evidence,
    )


def _verify_recovery_safety(data: KillSwitchVerificationInput | Mapping[str, Any]) -> KillSwitchReviewSection:
    data = _coerce_input(data)
    score = _clamp(data.recovery_safety_score) if data.recovery_safety_score is not None else _average(
        (
            _bool_score(data.state_snapshot_persisted),
            _bool_score(data.recovery_checkpoint_valid),
            _bool_score(data.rollback_path_available),
        ),
        default=45,
    )
    risks: list[KillSwitchRisk] = []
    if data.state_snapshot_persisted is not True or score < 80:
        risks.append(KillSwitchRisk.STATE_PERSISTENCE_FAILURE)
    if (
        data.recovery_checkpoint_valid is not True
        or data.rollback_path_available is not True
        or _has_upstream(data, "ROLLBACK_FAILURE", "RECOVERY_PATH")
    ):
        risks.append(KillSwitchRisk.RECOVERY_PATH_CORRUPTION)
    evidence = (
        f"recovery_safety_score={score}/100",
        f"state_snapshot_persisted={data.state_snapshot_persisted}",
        f"recovery_checkpoint_valid={data.recovery_checkpoint_valid}",
        f"rollback_path_available={data.rollback_path_available}",
    )
    return KillSwitchReviewSection(
        name="recovery_safety_review",
        score=score,
        passed=not risks and score >= 80,
        risks=_dedupe(risks),
        evidence=evidence,
    )


def _build_kill_switch_graph(risks: tuple[KillSwitchRisk, ...]) -> KillSwitchGraph:
    nodes = (
        "critical_event",
        "kill_switch",
        "shutdown_path",
        "execution_stop",
        "cognitive_stop",
        "runtime_halt",
        "emergency_lockdown",
        "recovery_checkpoint",
    )
    edges = (
        ("critical_event", "kill_switch", "triggers"),
        ("kill_switch", "shutdown_path", "signals"),
        ("shutdown_path", "execution_stop", "stops"),
        ("shutdown_path", "cognitive_stop", "stops"),
        ("shutdown_path", "runtime_halt", "halts"),
        ("runtime_halt", "emergency_lockdown", "locks"),
        ("emergency_lockdown", "recovery_checkpoint", "persists"),
    )
    failed_edges: list[tuple[str, str]] = []
    if KillSwitchRisk.KILL_SWITCH_FAILURE in risks:
        failed_edges.append(("critical_event", "kill_switch"))
    if KillSwitchRisk.SHUTDOWN_PATH_FAILURE in risks:
        failed_edges.append(("kill_switch", "shutdown_path"))
    if KillSwitchRisk.EXECUTION_CONTINUATION in risks:
        failed_edges.append(("shutdown_path", "execution_stop"))
    if KillSwitchRisk.COGNITIVE_LOOP_CONTINUATION in risks:
        failed_edges.append(("shutdown_path", "cognitive_stop"))
    if KillSwitchRisk.RUNTIME_HALT_FAILURE in risks:
        failed_edges.append(("shutdown_path", "runtime_halt"))
    if KillSwitchRisk.LOCKDOWN_FAILURE in risks or KillSwitchRisk.SAFETY_OVERRIDE_RISK in risks:
        failed_edges.append(("runtime_halt", "emergency_lockdown"))
    if (
        KillSwitchRisk.STATE_PERSISTENCE_FAILURE in risks
        or KillSwitchRisk.RECOVERY_PATH_CORRUPTION in risks
    ):
        failed_edges.append(("emergency_lockdown", "recovery_checkpoint"))
    return KillSwitchGraph(
        nodes=nodes,
        edges=edges,
        stop_edges=(
            ("shutdown_path", "execution_stop"),
            ("shutdown_path", "cognitive_stop"),
            ("shutdown_path", "runtime_halt"),
        ),
        failed_edges=_dedupe(failed_edges),
    )


def detect_kill_switch_risks(
    data: KillSwitchVerificationInput | Mapping[str, Any],
    shutdown_path_review: KillSwitchReviewSection | None = None,
    execution_stop_review: KillSwitchReviewSection | None = None,
    cognitive_stop_review: KillSwitchReviewSection | None = None,
    runtime_halt_review: KillSwitchReviewSection | None = None,
    emergency_lockdown_review: KillSwitchReviewSection | None = None,
    recovery_safety_review: KillSwitchReviewSection | None = None,
) -> tuple[KillSwitchRisk, ...]:
    """Detect kill switch verification risks."""

    data = _coerce_input(data)
    sections = (
        shutdown_path_review or verify_shutdown_path(data),
        execution_stop_review or verify_execution_stop(data),
        cognitive_stop_review or verify_cognitive_stop(data),
        runtime_halt_review or verify_runtime_halt(data),
        emergency_lockdown_review or verify_emergency_lockdown(data),
        recovery_safety_review or _verify_recovery_safety(data),
    )
    risks: list[KillSwitchRisk] = []
    for section in sections:
        risks.extend(section.risks)
    return _dedupe(risks)


def compute_kill_switch_score(
    data: KillSwitchVerificationInput | Mapping[str, Any],
    risks: tuple[KillSwitchRisk, ...] = (),
    shutdown_path_review: KillSwitchReviewSection | None = None,
    execution_stop_review: KillSwitchReviewSection | None = None,
    cognitive_stop_review: KillSwitchReviewSection | None = None,
    runtime_halt_review: KillSwitchReviewSection | None = None,
    emergency_lockdown_review: KillSwitchReviewSection | None = None,
    recovery_safety_review: KillSwitchReviewSection | None = None,
) -> KillSwitchScore:
    """Compute kill switch verification score normalized to 0..100."""

    data = _coerce_input(data)
    shutdown = shutdown_path_review or verify_shutdown_path(data)
    execution = execution_stop_review or verify_execution_stop(data)
    cognitive = cognitive_stop_review or verify_cognitive_stop(data)
    runtime = runtime_halt_review or verify_runtime_halt(data)
    lockdown = emergency_lockdown_review or verify_emergency_lockdown(data)
    recovery = recovery_safety_review or _verify_recovery_safety(data)
    weighted = _weighted_average(
        (
            (shutdown.score, 1.3),
            (execution.score, 1.2),
            (cognitive.score, 1.0),
            (runtime.score, 1.15),
            (lockdown.score, 1.1),
            (recovery.score, 0.9),
        )
    )
    penalty = min(70, len(set(risks)) * 7)
    overall = _clamp(weighted - penalty)
    critical_caps = {
        KillSwitchRisk.KILL_SWITCH_FAILURE: 40,
        KillSwitchRisk.SHUTDOWN_PATH_FAILURE: 50,
        KillSwitchRisk.EXECUTION_CONTINUATION: 45,
        KillSwitchRisk.COGNITIVE_LOOP_CONTINUATION: 55,
        KillSwitchRisk.RUNTIME_HALT_FAILURE: 50,
        KillSwitchRisk.LOCKDOWN_FAILURE: 55,
        KillSwitchRisk.SAFETY_OVERRIDE_RISK: 55,
    }
    for risk, cap in critical_caps.items():
        if risk in risks:
            overall = min(overall, cap)
    return KillSwitchScore(
        overall_score=overall,
        shutdown_path_score=shutdown.score,
        execution_stop_score=execution.score,
        cognitive_stop_score=cognitive.score,
        runtime_halt_score=runtime.score,
        emergency_lockdown_score=lockdown.score,
        recovery_safety_score=recovery.score,
    )


def _select_state(
    score: int,
    risks: tuple[KillSwitchRisk, ...],
    ready_for_rollback_verification: bool | None,
) -> KillSwitchState:
    risk_count = len(set(risks))
    hard_risks = {
        KillSwitchRisk.KILL_SWITCH_FAILURE,
        KillSwitchRisk.SHUTDOWN_PATH_FAILURE,
        KillSwitchRisk.EXECUTION_CONTINUATION,
        KillSwitchRisk.RUNTIME_HALT_FAILURE,
    }
    if hard_risks.intersection(risks) or score < 45 or risk_count >= 6:
        return KillSwitchState.NOT_VERIFIED
    if risk_count >= 3 or score < 72:
        return KillSwitchState.REVIEW_REQUIRED
    if risk_count:
        return KillSwitchState.PARTIALLY_VERIFIED
    if score >= 94 and ready_for_rollback_verification is True:
        return KillSwitchState.READY_FOR_ROLLBACK_VERIFICATION
    if score >= 88:
        return KillSwitchState.VERIFIED
    return KillSwitchState.PARTIALLY_VERIFIED


def generate_kill_switch_recommendations(
    risks: tuple[KillSwitchRisk, ...],
    state: KillSwitchState | None = None,
) -> tuple[KillSwitchRecommendation, ...]:
    """Generate kill switch verification recommendations."""

    recommendations: list[KillSwitchRecommendation] = []
    if risks:
        recommendations.append(KillSwitchRecommendation.HOLD_KILL_SWITCH_APPROVAL)
    mapping = {
        KillSwitchRisk.KILL_SWITCH_FAILURE: KillSwitchRecommendation.INSTALL_KILL_SWITCH_GUARD,
        KillSwitchRisk.SHUTDOWN_PATH_FAILURE: KillSwitchRecommendation.REPAIR_SHUTDOWN_PATH,
        KillSwitchRisk.EXECUTION_CONTINUATION: KillSwitchRecommendation.FORCE_EXECUTION_STOP_PROPAGATION,
        KillSwitchRisk.COGNITIVE_LOOP_CONTINUATION: (
            KillSwitchRecommendation.STOP_COGNITIVE_LOOPS_ON_CRITICAL_SIGNAL
        ),
        KillSwitchRisk.RUNTIME_HALT_FAILURE: KillSwitchRecommendation.HALT_RUNTIME_WORKERS,
        KillSwitchRisk.LOCKDOWN_FAILURE: KillSwitchRecommendation.HARDEN_EMERGENCY_LOCKDOWN,
        KillSwitchRisk.SAFETY_OVERRIDE_RISK: KillSwitchRecommendation.BLOCK_SAFETY_OVERRIDES,
        KillSwitchRisk.EMERGENCY_RESPONSE_DELAY: (
            KillSwitchRecommendation.REDUCE_EMERGENCY_RESPONSE_LATENCY
        ),
        KillSwitchRisk.STATE_PERSISTENCE_FAILURE: KillSwitchRecommendation.PERSIST_SAFE_STOP_STATE,
        KillSwitchRisk.RECOVERY_PATH_CORRUPTION: KillSwitchRecommendation.REPAIR_RECOVERY_CHECKPOINT,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(KillSwitchRecommendation.RUN_KILL_SWITCH_VERIFICATION_SUITE)
    if state == KillSwitchState.READY_FOR_ROLLBACK_VERIFICATION:
        recommendations.append(
            KillSwitchRecommendation.APPROVE_ROLLBACK_VERIFICATION_AFTER_MANUAL_REVIEW
        )
    return _dedupe(recommendations)


def evaluate_kill_switch(
    data: KillSwitchVerificationInput | Mapping[str, Any],
) -> KillSwitchVerificationResult:
    """Evaluate whether AGIcore can stop runtime, cognitive and execution activity offline."""

    data = _coerce_input(data)
    shutdown = verify_shutdown_path(data)
    execution = verify_execution_stop(data)
    cognitive = verify_cognitive_stop(data)
    runtime = verify_runtime_halt(data)
    lockdown = verify_emergency_lockdown(data)
    recovery = _verify_recovery_safety(data)
    risks = detect_kill_switch_risks(data, shutdown, execution, cognitive, runtime, lockdown, recovery)
    score = compute_kill_switch_score(data, risks, shutdown, execution, cognitive, runtime, lockdown, recovery)
    state = _select_state(score.overall_score, risks, data.ready_for_rollback_verification)
    graph = _build_kill_switch_graph(risks)
    recommendations = generate_kill_switch_recommendations(risks, state)
    offline_only = data.broker_path_blocked is True and not _has_upstream(data, "LIVE_EXECUTION", "API_ACCESS")
    summary = f"{state.value}: score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return KillSwitchVerificationResult(
        state=state,
        kill_switch_score=score.overall_score,
        score_breakdown=score,
        risks=risks,
        shutdown_path_review=shutdown,
        execution_stop_review=execution,
        cognitive_stop_review=cognitive,
        runtime_halt_review=runtime,
        emergency_lockdown_review=lockdown,
        recovery_safety_review=recovery,
        kill_switch_graph=graph,
        recommendations=recommendations,
        offline_only=offline_only,
        summary=summary,
    )


def render_kill_switch_markdown(result: KillSwitchVerificationResult) -> str:
    """Render an explainable kill switch verification report."""

    lines = [
        "# AGIcore Kill Switch Verification",
        f"- State: {result.state.value}",
        f"- Score: {result.kill_switch_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Score Breakdown",
        f"- Shutdown path: {result.score_breakdown.shutdown_path_score}/100",
        f"- Execution stop: {result.score_breakdown.execution_stop_score}/100",
        f"- Cognitive stop: {result.score_breakdown.cognitive_stop_score}/100",
        f"- Runtime halt: {result.score_breakdown.runtime_halt_score}/100",
        f"- Emergency lockdown: {result.score_breakdown.emergency_lockdown_score}/100",
        f"- Recovery safety: {result.score_breakdown.recovery_safety_score}/100",
        "",
        "# Kill Switch Reviews",
    ]
    for section in (
        result.shutdown_path_review,
        result.execution_stop_review,
        result.cognitive_stop_review,
        result.runtime_halt_review,
        result.emergency_lockdown_review,
        result.recovery_safety_review,
    ):
        lines.append(
            f"- {section.name}: passed={section.passed}, score={section.score}/100, "
            f"risks={', '.join(risk.value for risk in section.risks) or 'none'}"
        )
        lines.extend(f"  - {item}" for item in section.evidence)
    lines.append("")
    lines.append("# Kill Switch Graph")
    lines.append(f"- Nodes: {', '.join(result.kill_switch_graph.nodes)}")
    lines.extend(
        f"- Edge: {source} -> {target} ({label})"
        for source, target, label in result.kill_switch_graph.edges
    )
    lines.append(
        "- Failed edges: "
        + (
            ", ".join(f"{source}->{target}" for source, target in result.kill_switch_graph.failed_edges)
            or "none"
        )
    )
    lines.append("")
    lines.append("# Kill Switch Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Kill Switch Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    lines.append("")
    lines.append("# Verification Outlook")
    if result.state == KillSwitchState.READY_FOR_ROLLBACK_VERIFICATION:
        lines.append("- Kill switch is ready for manual rollback verification review.")
    elif result.state == KillSwitchState.VERIFIED:
        lines.append("- Kill switch is verified; rollback verification remains gated.")
    elif result.state == KillSwitchState.PARTIALLY_VERIFIED:
        lines.append("- Kill switch is partially verified and remaining risks must be resolved.")
    else:
        lines.append("- Kill switch approval should remain blocked.")
    return "\n".join(lines)


__all__ = [
    "compute_kill_switch_score",
    "detect_kill_switch_risks",
    "evaluate_kill_switch",
    "generate_kill_switch_recommendations",
    "render_kill_switch_markdown",
    "verify_cognitive_stop",
    "verify_emergency_lockdown",
    "verify_execution_stop",
    "verify_runtime_halt",
    "verify_shutdown_path",
]
