"""Offline freeze readiness audit for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable

from agicore.trading.freeze_readiness_audit_models import (
    FreezeBlockerRisk,
    FreezeReadinessInput,
    FreezeReadinessResult,
    FreezeReadinessScore,
    FreezeReadinessState,
    FreezeRecommendation,
    RuntimeReadinessMatrix,
    RuntimeReadinessRow,
    SystemStabilitySnapshot,
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


def _average(values: Iterable[int | float]) -> int:
    usable = [float(value) for value in values if value is not None]
    if not usable:
        return 0
    return _clamp(sum(usable) / len(usable))


def _score(obj: Any, *names: str, default: int | None = None) -> int | None:
    for name in names:
        value = _get(obj, name)
        if isinstance(value, (int, float)):
            return _clamp(value)
    return default


def _bool_score(value: bool | None, unknown: int = 40) -> int:
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


def _risk_text(obj: Any) -> tuple[Any, ...]:
    return _as_tuple(_get(obj, "risks", ())) + _as_tuple(_get(obj, "blockers", ()))


def _has_risk(obj: Any, *needles: str) -> bool:
    return _contains(_risk_text(obj), *needles)


def _component_score(data: FreezeReadinessInput, explicit: str, obj_names: tuple[tuple[Any, tuple[str, ...]], ...], default: int) -> int:
    value = getattr(data, explicit)
    if isinstance(value, (int, float)):
        return _clamp(value)
    scores = []
    for obj, names in obj_names:
        found = _score(obj, *names)
        if found is not None:
            scores.append(found)
    if scores:
        return _average(scores)
    return default


def build_system_stability_snapshot(data: FreezeReadinessInput) -> SystemStabilitySnapshot:
    """Build a deterministic offline snapshot from explicit readiness evidence."""

    tests_score = _average(
        (
            100 if data.tests_green is True else 0 if data.tests_green is False else 35,
            100 * data.unit_test_pass_rate if data.unit_test_pass_rate is not None else 35,
            max(0, 100 - data.flaky_test_count * 15 - data.test_failure_count * 25),
        )
    )
    fragmentation_score = _clamp(100 - data.fragmented_engine_count * 20 - data.conflicting_engine_count * 25)
    conflict_score = _average(
        (
            fragmentation_score,
            _score(data.cognitive_consensus, "cognitive_consensus_score", "consensus_score", default=fragmentation_score),
            _score(data.cognitive_coherence, "cognitive_coherence_score", "coherence_score", default=fragmentation_score),
        )
    )
    safety_score = _component_score(
        data,
        "safety_score",
        (
            (data.cognitive_constitutional, ("constitutional_score",)),
            (data.risk_guard, ("risk_score", "safety_score")),
            (data.safe_rl_layer, ("safe_rl_score", "safety_score")),
        ),
        default=_average(
            (
                _bool_score(data.execution_sandboxed),
                _bool_score(data.broker_connection_disabled),
                _bool_score(data.external_api_disabled),
                _bool_score(data.live_execution_disabled),
            )
        ),
    )
    orchestration_score = _component_score(
        data,
        "orchestration_score",
        ((data.global_orchestrator, ("orchestrator_score", "coordination_score")),),
        default=_average((_bool_score(data.orchestrator_registered), min(100, data.orchestrator_route_count * 20))),
    )
    observability_score = _component_score(
        data,
        "observability_score",
        ((data.operational_awareness, ("operational_confidence_score", "observability_score")),),
        default=_average((_bool_score(data.runtime_observable), _bool_score(data.log_json_enabled), _bool_score(data.metrics_available))),
    )
    replay_score = _component_score(
        data,
        "replay_safety_score",
        ((data.session_replay, ("replay_safety_score", "determinism_score")),),
        default=_average((_bool_score(data.replay_deterministic), _bool_score(data.replay_uses_sandbox_data), _bool_score(data.replay_has_no_real_orders))),
    )
    memory_score = _average(
        (
            _bool_score(data.memory_state_consistent),
            data.memory_reconciliation_score if data.memory_reconciliation_score is not None else None,
            _score(data.adaptive_memory, "memory_score", "adaptive_memory_score", default=80),
            _score(data.cognitive_memory_consolidation, "memory_consolidation_score", default=80),
        )
    )
    sandbox_score = _average(
        (
            _bool_score(data.sandbox_ready),
            _bool_score(data.execution_sandboxed),
            _bool_score(data.broker_connection_disabled),
            _bool_score(data.external_api_disabled),
            _bool_score(data.live_execution_disabled),
        )
    )
    paper_score = _component_score(
        data,
        "paper_readiness_score",
        (
            (data.paper_execution_loop, ("paper_execution_score", "execution_score")),
            (data.paper_trading_adapter, ("paper_adapter_score", "adapter_score")),
        ),
        default=_average((_bool_score(data.paper_trading_loop_ready), _bool_score(data.paper_adapter_ready))),
    )
    global_score = _component_score(
        data,
        "global_stability_score",
        (
            (data.system_integrity, ("integrity_score", "system_integrity_score")),
            (data.cognitive_stability, ("cognitive_stability_score", "stability_score")),
        ),
        default=_average((tests_score, fragmentation_score, conflict_score, safety_score, orchestration_score)),
    )
    evidence = (
        f"tests={tests_score}/100",
        f"global_stability={global_score}/100",
        f"fragmented_engines={data.fragmented_engine_count}",
        f"conflicting_engines={data.conflicting_engine_count}",
        f"offline_guards broker_disabled={data.broker_connection_disabled} external_api_disabled={data.external_api_disabled} live_disabled={data.live_execution_disabled}",
    )
    return SystemStabilitySnapshot(
        global_stability_score=global_score,
        test_coverage_score=tests_score,
        cognitive_fragmentation_score=fragmentation_score,
        engine_conflict_score=conflict_score,
        safety_score=safety_score,
        orchestration_score=orchestration_score,
        runtime_coherence_score=_average((global_score, conflict_score, memory_score, orchestration_score)),
        observability_score=observability_score,
        replay_safety_score=replay_score,
        kill_switch_score=_bool_score(data.kill_switch_configured),
        rollback_score=_average((_bool_score(data.rollback_plan_available), _bool_score(data.rollback_tested))),
        memory_consistency_score=memory_score,
        sandbox_score=sandbox_score,
        paper_trading_score=paper_score,
        evidence=evidence + data.notes,
    )


def detect_freeze_blockers(
    data: FreezeReadinessInput,
    snapshot: SystemStabilitySnapshot | None = None,
) -> tuple[FreezeBlockerRisk, ...]:
    """Detect blockers that prevent a safe AGIcore freeze."""

    resolved = snapshot or build_system_stability_snapshot(data)
    blockers: list[FreezeBlockerRisk] = []
    if data.tests_green is not True or resolved.test_coverage_score < 85 or data.flaky_test_count > 0 or data.test_failure_count > 0:
        blockers.append(FreezeBlockerRisk.TEST_INSTABILITY)
    if (
        data.fragmented_engine_count > 0
        or data.conflicting_engine_count > 0
        or resolved.cognitive_fragmentation_score < 80
        or resolved.engine_conflict_score < 80
        or _has_risk(data.cognitive_consensus, "FRAGMENT", "CONFLICT")
        or _has_risk(data.cognitive_coherence, "CONFLICT", "INCOHER")
    ):
        blockers.append(FreezeBlockerRisk.ENGINE_FRAGMENTATION)
    if data.orchestrator_registered is not True or data.orchestrator_route_count <= 0 or resolved.orchestration_score < 75:
        blockers.append(FreezeBlockerRisk.ORCHESTRATION_GAP)
    if data.runtime_observable is not True or data.log_json_enabled is not True or resolved.observability_score < 75:
        blockers.append(FreezeBlockerRisk.RUNTIME_UNOBSERVABLE)
    if (
        data.replay_deterministic is not True
        or data.replay_uses_sandbox_data is not True
        or data.replay_has_no_real_orders is not True
        or resolved.replay_safety_score < 80
    ):
        blockers.append(FreezeBlockerRisk.REPLAY_UNSAFE)
    if data.kill_switch_configured is not True:
        blockers.append(FreezeBlockerRisk.KILL_SWITCH_MISSING)
    if data.rollback_plan_available is not True or resolved.rollback_score < 70:
        blockers.append(FreezeBlockerRisk.ROLLBACK_UNAVAILABLE)
    if data.memory_state_consistent is not True or resolved.memory_consistency_score < 75:
        blockers.append(FreezeBlockerRisk.MEMORY_INCONSISTENCY)
    if (
        data.execution_sandboxed is not True
        or data.broker_connection_disabled is not True
        or data.external_api_disabled is not True
        or data.live_execution_disabled is not True
        or resolved.sandbox_score < 85
    ):
        blockers.append(FreezeBlockerRisk.EXECUTION_UNSAFE)
    if data.paper_trading_loop_ready is not True or data.paper_adapter_ready is not True or resolved.paper_trading_score < 80:
        blockers.append(FreezeBlockerRisk.PAPER_RUNTIME_NOT_READY)
    return _dedupe(blockers)


def build_runtime_readiness_matrix(
    data: FreezeReadinessInput,
    blockers: tuple[FreezeBlockerRisk, ...] = (),
    snapshot: SystemStabilitySnapshot | None = None,
) -> RuntimeReadinessMatrix:
    """Build the offline runtime readiness matrix used by the audit report."""

    resolved = snapshot or build_system_stability_snapshot(data)

    def row(area: str, score: int, risks: tuple[FreezeBlockerRisk, ...], detail: str) -> RuntimeReadinessRow:
        active = tuple(risk for risk in risks if risk in blockers)
        return RuntimeReadinessRow(area=area, ready=not active and score >= 75, score=score, blockers=active, detail=detail)

    rows = (
        row("tests", resolved.test_coverage_score, (FreezeBlockerRisk.TEST_INSTABILITY,), "Unit and regression evidence."),
        row("engines", _average((resolved.cognitive_fragmentation_score, resolved.engine_conflict_score)), (FreezeBlockerRisk.ENGINE_FRAGMENTATION,), "Cognitive fragmentation and engine conflicts."),
        row("orchestration", resolved.orchestration_score, (FreezeBlockerRisk.ORCHESTRATION_GAP,), "Global routing registration."),
        row("observability", resolved.observability_score, (FreezeBlockerRisk.RUNTIME_UNOBSERVABLE,), "JSON logs and runtime telemetry."),
        row("replay", resolved.replay_safety_score, (FreezeBlockerRisk.REPLAY_UNSAFE,), "Deterministic offline replay safety."),
        row("kill_switch", resolved.kill_switch_score, (FreezeBlockerRisk.KILL_SWITCH_MISSING,), "Emergency stop readiness."),
        row("rollback", resolved.rollback_score, (FreezeBlockerRisk.ROLLBACK_UNAVAILABLE,), "Rollback plan and rehearsal evidence."),
        row("memory", resolved.memory_consistency_score, (FreezeBlockerRisk.MEMORY_INCONSISTENCY,), "STM/LTM state consistency."),
        row("sandbox", resolved.sandbox_score, (FreezeBlockerRisk.EXECUTION_UNSAFE,), "No broker, API, live order or live execution path."),
        row("paper_runtime", resolved.paper_trading_score, (FreezeBlockerRisk.PAPER_RUNTIME_NOT_READY,), "Paper adapter and loop readiness."),
    )
    return RuntimeReadinessMatrix(rows=rows)


def compute_freeze_readiness_score(
    data: FreezeReadinessInput,
    blockers: tuple[FreezeBlockerRisk, ...] = (),
    snapshot: SystemStabilitySnapshot | None = None,
) -> FreezeReadinessScore:
    """Compute freeze readiness scores normalized to 0..100."""

    resolved = snapshot or build_system_stability_snapshot(data)
    penalty = min(55, len(set(blockers)) * 6)
    critical_caps = {
        FreezeBlockerRisk.EXECUTION_UNSAFE: 45,
        FreezeBlockerRisk.KILL_SWITCH_MISSING: 65,
        FreezeBlockerRisk.REPLAY_UNSAFE: 70,
        FreezeBlockerRisk.TEST_INSTABILITY: 75,
    }
    weighted = _average(
        (
            resolved.global_stability_score * 1.25,
            resolved.test_coverage_score * 1.15,
            resolved.cognitive_fragmentation_score,
            resolved.engine_conflict_score,
            resolved.safety_score * 1.2,
            resolved.orchestration_score,
            resolved.runtime_coherence_score,
            resolved.observability_score,
            resolved.replay_safety_score,
            resolved.kill_switch_score,
            resolved.rollback_score,
            resolved.memory_consistency_score,
            resolved.sandbox_score * 1.2,
            resolved.paper_trading_score,
        )
    )
    overall = _clamp(weighted - penalty)
    for blocker, cap in critical_caps.items():
        if blocker in blockers:
            overall = min(overall, cap)
    return FreezeReadinessScore(
        overall_score=overall,
        stability_score=resolved.global_stability_score,
        tests_score=resolved.test_coverage_score,
        fragmentation_score=resolved.cognitive_fragmentation_score,
        safety_score=resolved.safety_score,
        orchestration_score=resolved.orchestration_score,
        runtime_coherence_score=resolved.runtime_coherence_score,
        observability_score=resolved.observability_score,
        replay_safety_score=resolved.replay_safety_score,
        kill_switch_score=resolved.kill_switch_score,
        rollback_score=resolved.rollback_score,
        memory_score=resolved.memory_consistency_score,
        sandbox_score=resolved.sandbox_score,
        paper_runtime_score=resolved.paper_trading_score,
    )


def _select_state(score: int, blockers: tuple[FreezeBlockerRisk, ...], matrix: RuntimeReadinessMatrix) -> FreezeReadinessState:
    blocker_count = len(set(blockers))
    if FreezeBlockerRisk.EXECUTION_UNSAFE in blockers or score < 40 or blocker_count >= 6:
        return FreezeReadinessState.NOT_READY
    if blocker_count >= 3 or score < 65:
        return FreezeReadinessState.PARTIALLY_READY
    if blocker_count:
        return FreezeReadinessState.FREEZE_CANDIDATE
    if score >= 92 and matrix.ready:
        return FreezeReadinessState.READY_TO_TRY
    if score >= 85:
        return FreezeReadinessState.STABLE
    return FreezeReadinessState.FREEZE_CANDIDATE


def generate_freeze_recommendations(
    blockers: tuple[FreezeBlockerRisk, ...],
    state: FreezeReadinessState | None = None,
) -> tuple[FreezeRecommendation, ...]:
    """Generate remediation recommendations from detected freeze blockers."""

    recommendations: list[FreezeRecommendation] = []
    if blockers:
        recommendations.append(FreezeRecommendation.KEEP_SYSTEM_FROZEN)
    mapping = {
        FreezeBlockerRisk.TEST_INSTABILITY: FreezeRecommendation.FIX_TEST_INSTABILITY,
        FreezeBlockerRisk.ENGINE_FRAGMENTATION: FreezeRecommendation.CONSOLIDATE_ENGINES,
        FreezeBlockerRisk.ORCHESTRATION_GAP: FreezeRecommendation.COMPLETE_ORCHESTRATION_REGISTRATION,
        FreezeBlockerRisk.RUNTIME_UNOBSERVABLE: FreezeRecommendation.ADD_RUNTIME_OBSERVABILITY,
        FreezeBlockerRisk.REPLAY_UNSAFE: FreezeRecommendation.HARDEN_REPLAY_SANDBOX,
        FreezeBlockerRisk.KILL_SWITCH_MISSING: FreezeRecommendation.CONFIGURE_KILL_SWITCH,
        FreezeBlockerRisk.ROLLBACK_UNAVAILABLE: FreezeRecommendation.PREPARE_ROLLBACK_PLAN,
        FreezeBlockerRisk.MEMORY_INCONSISTENCY: FreezeRecommendation.RECONCILE_MEMORY_STATE,
        FreezeBlockerRisk.EXECUTION_UNSAFE: FreezeRecommendation.ENFORCE_OFFLINE_EXECUTION_GUARDS,
        FreezeBlockerRisk.PAPER_RUNTIME_NOT_READY: FreezeRecommendation.VALIDATE_PAPER_RUNTIME,
    }
    recommendations.extend(mapping[blocker] for blocker in blockers)
    recommendations.append(FreezeRecommendation.RUN_FREEZE_REGRESSION_SUITE)
    if state in {FreezeReadinessState.STABLE, FreezeReadinessState.READY_TO_TRY}:
        recommendations.append(FreezeRecommendation.AUTHORIZE_READY_TO_TRY_ONLY_AFTER_REVIEW)
    return _dedupe(recommendations)


def evaluate_freeze_readiness(data: FreezeReadinessInput) -> FreezeReadinessResult:
    """Evaluate whether AGIcore is ready for freeze using offline evidence only."""

    snapshot = build_system_stability_snapshot(data)
    blockers = detect_freeze_blockers(data, snapshot)
    matrix = build_runtime_readiness_matrix(data, blockers, snapshot)
    score = compute_freeze_readiness_score(data, blockers, snapshot)
    state = _select_state(score.overall_score, blockers, matrix)
    recommendations = generate_freeze_recommendations(blockers, state)
    offline_only = data.broker_connection_disabled and data.external_api_disabled and data.live_execution_disabled
    summary = f"{state.value}: score={score.overall_score}, blockers={len(blockers)}, offline_only={offline_only}"
    return FreezeReadinessResult(
        state=state,
        freeze_readiness_score=score.overall_score,
        score_breakdown=score,
        blockers=blockers,
        snapshot=snapshot,
        runtime_matrix=matrix,
        recommendations=recommendations,
        offline_only=offline_only,
        summary=summary,
    )


def render_freeze_readiness_markdown(result: FreezeReadinessResult) -> str:
    """Render an explainable freeze readiness report."""

    lines = [
        "# AGIcore Freeze Readiness Audit",
        f"- State: {result.state.value}",
        f"- Score: {result.freeze_readiness_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Stability Snapshot",
        f"- Global stability: {result.snapshot.global_stability_score}/100",
        f"- Tests: {result.snapshot.test_coverage_score}/100",
        f"- Fragmentation: {result.snapshot.cognitive_fragmentation_score}/100",
        f"- Engine conflicts: {result.snapshot.engine_conflict_score}/100",
        f"- Safety: {result.snapshot.safety_score}/100",
        f"- Orchestration: {result.snapshot.orchestration_score}/100",
        f"- Runtime coherence: {result.snapshot.runtime_coherence_score}/100",
        f"- Observability: {result.snapshot.observability_score}/100",
        f"- Replay safety: {result.snapshot.replay_safety_score}/100",
        f"- Kill switch: {result.snapshot.kill_switch_score}/100",
        f"- Rollback: {result.snapshot.rollback_score}/100",
        f"- Memory consistency: {result.snapshot.memory_consistency_score}/100",
        f"- Sandbox: {result.snapshot.sandbox_score}/100",
        f"- Paper trading: {result.snapshot.paper_trading_score}/100",
        "",
        "# Runtime Readiness Matrix",
    ]
    lines.extend(
        f"- {row.area}: ready={row.ready}, score={row.score}/100, blockers={', '.join(blocker.value for blocker in row.blockers) or 'none'}"
        for row in result.runtime_matrix.rows
    )
    lines.append("")
    lines.append("# Freeze Blockers")
    lines.extend(f"- {blocker.value}" for blocker in result.blockers) if result.blockers else lines.append("- none")
    lines.append("")
    lines.append("# Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    lines.append("")
    lines.append("# Evidence")
    lines.extend(f"- {item}" for item in result.snapshot.evidence)
    return "\n".join(lines)


__all__ = [
    "build_runtime_readiness_matrix",
    "build_system_stability_snapshot",
    "compute_freeze_readiness_score",
    "detect_freeze_blockers",
    "evaluate_freeze_readiness",
    "generate_freeze_recommendations",
    "render_freeze_readiness_markdown",
]
