"""Offline cognitive memory consolidation engine for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Optional

from agicore.trading.cognitive_memory_consolidation_models import (
    CognitiveMemoryConsolidationInput,
    CognitiveMemoryConsolidationResult,
    ConsolidatedMemorySnapshot,
    MemoryCluster,
    MemoryConsolidationAction,
    MemoryConsolidationEvent,
    MemoryConsolidationMode,
    MemoryConsolidationRecommendation,
    MemoryConsolidationRisk,
    MemoryConsolidationScore,
    MemoryConsolidationState,
    MemoryTrace,
)


CORE_INVARIANTS = (
    "mission_offline_only",
    "safety_first",
    "discipline_preservation",
    "capital_preservation",
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
    return (items,)


def _clamp(value: int | float, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(round(value))))


def _average(values: Iterable[int | float]) -> int:
    usable = [float(value) for value in values if value is not None]
    if not usable:
        return 80
    return _clamp(sum(usable) / len(usable))


def _score(obj: Any, *names: str, default: int = 80) -> int:
    for name in names:
        value = _get(obj, name)
        if isinstance(value, (int, float)):
            return _clamp(value)
    return default


def _risks_contain(obj: Any, *needles: str) -> bool:
    return any(_has(risk, *needles) for risk in _as_tuple(_get(obj, "risks", ())))


def _dedupe(items: Iterable[Any]) -> tuple[Any, ...]:
    seen: set[Any] = set()
    result: list[Any] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return tuple(result)


def _trace(
    trace_id: str,
    source: str,
    content: str,
    confidence_score: int,
    *,
    critical: bool = False,
    contradicted: bool = False,
    tags: tuple[str, ...] = (),
) -> MemoryTrace:
    return MemoryTrace(
        trace_id=trace_id,
        source=source,
        content=content,
        confidence_score=_clamp(confidence_score),
        critical=critical,
        contradicted=contradicted,
        tags=tags,
    )


def build_memory_traces(data: CognitiveMemoryConsolidationInput) -> tuple[MemoryTrace, ...]:
    """Build deterministic memory traces from compatible cognitive outputs."""

    traces: list[MemoryTrace] = list(data.manual_traces)

    if data.cognitive_consensus is not None:
        traces.append(
            _trace(
                "cognitive_consensus",
                "CognitiveConsensusResult",
                f"Consensus { _value(_get(data.cognitive_consensus, 'state')) }",
                _score(data.cognitive_consensus, "cognitive_consensus_score"),
                critical=True,
                contradicted=_has(_get(data.cognitive_consensus, "state"), "CONFLICT", "LOCKED", "FRAGMENTED"),
                tags=("consensus", "reasoning"),
            )
        )
    for chain in _as_tuple(_get(data.cognitive_consensus, "reasoning_chains", ())) + _as_tuple(
        _get(data.cognitive_coherence, "reasoning_chains", ())
    ):
        traces.append(
            _trace(
                f"reasoning_{len(traces) + 1}",
                "ReasoningChain",
                f"{_get(chain, 'name', 'chain')}: {' | '.join(str(step) for step in _as_tuple(_get(chain, 'steps', ())))}",
                _score(chain, "score"),
                critical=False,
                contradicted=not bool(_get(chain, "complete", _get(chain, "agreed", True))) or bool(_get(chain, "conflict", None)),
                tags=("reasoning",),
            )
        )
    if data.cognitive_coherence is not None:
        traces.append(
            _trace(
                "cognitive_coherence",
                "CognitiveCoherenceResult",
                f"Coherence { _value(_get(data.cognitive_coherence, 'state')) }",
                _score(data.cognitive_coherence, "cognitive_coherence_score"),
                critical=True,
                contradicted=_has(_get(data.cognitive_coherence, "state"), "CONFLICT", "INCOHERENCE", "LOCKED"),
                tags=("reasoning", "coherence"),
            )
        )
    if data.cognitive_alignment is not None:
        traces.append(
            _trace(
                "cognitive_alignment",
                "CognitiveAlignmentResult",
                f"Alignment { _value(_get(data.cognitive_alignment, 'state')) }",
                _score(data.cognitive_alignment, "cognitive_alignment_score"),
                critical=True,
                contradicted=_has(_get(data.cognitive_alignment, "state"), "MISALIGNMENT", "LOCKED"),
                tags=("identity", "invariant"),
            )
        )
    if data.intent_integrity is not None:
        traces.append(
            _trace(
                "intent_integrity",
                "IntentIntegrityResult",
                f"Intent { _value(_get(data.intent_integrity, 'state')) }",
                _score(data.intent_integrity, "intent_integrity_score"),
                critical=True,
                contradicted=_has(_get(data.intent_integrity, "state"), "CONFLICT", "CORRUPTED", "LOCKED"),
                tags=("intent", "invariant"),
            )
        )
    if data.cognitive_identity is not None:
        traces.append(
            _trace(
                "cognitive_identity",
                "CognitiveIdentityResult",
                f"Identity { _value(_get(data.cognitive_identity, 'state')) }",
                _score(data.cognitive_identity, "cognitive_identity_score", "identity_score"),
                critical=True,
                contradicted=_has(_get(data.cognitive_identity, "state"), "DRIFT", "CONFLICT", "LOCKED", "AT_RISK"),
                tags=("identity", "invariant"),
            )
        )
    if data.cognitive_continuity is not None:
        traces.append(
            _trace(
                "cognitive_continuity",
                "CognitiveContinuityResult",
                f"Continuity { _value(_get(data.cognitive_continuity, 'state')) }",
                _score(data.cognitive_continuity, "cognitive_continuity_score", "continuity_score"),
                critical=True,
                contradicted=_has(_get(data.cognitive_continuity, "state"), "BREAK", "FRAGMENTED", "FAILURE", "RISK"),
                tags=("continuity", "long_term"),
            )
        )
    if data.cognitive_recovery is not None:
        traces.append(
            _trace(
                "cognitive_recovery",
                "CognitiveRecoveryResult",
                f"Recovery { _value(_get(data.cognitive_recovery, 'state')) }",
                _score(data.cognitive_recovery, "cognitive_recovery_score"),
                contradicted=_has(_get(data.cognitive_recovery, "state"), "FAILED", "DEGRADED", "HUMAN"),
                tags=("recovery",),
            )
        )
    if data.cognitive_resilience is not None:
        traces.append(
            _trace(
                "cognitive_resilience",
                "CognitiveResilienceResult",
                f"Resilience { _value(_get(data.cognitive_resilience, 'state')) }",
                _score(data.cognitive_resilience, "cognitive_resilience_score"),
                critical=True,
                contradicted=_has(_get(data.cognitive_resilience, "state"), "CRITICAL", "SURVIVAL", "FRAGILE"),
                tags=("resilience", "safety"),
            )
        )
    if data.cognitive_stability is not None:
        traces.append(
            _trace(
                "cognitive_stability",
                "CognitiveStabilityResult",
                f"Stability { _value(_get(data.cognitive_stability, 'state')) }",
                _score(data.cognitive_stability, "cognitive_stability_score"),
                critical=True,
                contradicted=_has(_get(data.cognitive_stability, "state"), "UNSTABLE", "CRITICAL", "COLLAPSING"),
                tags=("stability", "safety"),
            )
        )
    if data.self_reflection_audit is not None:
        traces.append(
            _trace(
                "self_reflection_audit",
                "SelfReflectionAuditResult",
                f"Audit { _value(_get(data.self_reflection_audit, 'state')) }",
                _score(data.self_reflection_audit, "reflection_quality_score"),
                critical=True,
                contradicted=_has(_get(data.self_reflection_audit, "state"), "CONTRADICTORY", "CRITICAL", "REQUIRED"),
                tags=("audit", "reasoning"),
            )
        )
    if data.recursive_world_model is not None:
        traces.append(
            _trace(
                "recursive_world_model",
                "RecursiveWorldModelResult",
                f"World model { _value(_get(data.recursive_world_model, 'decision')) }",
                _score(data.recursive_world_model, "world_model_coherence_score"),
                critical=True,
                contradicted=_risks_contain(data.recursive_world_model, "INCOHERENCE", "CONTRADICTION", "MISMATCH"),
                tags=("world_model", "long_term"),
            )
        )
    if data.strategic_timeline_analysis is not None:
        traces.append(
            _trace(
                "strategic_timeline",
                "StrategicTimelineAnalysis",
                f"Timeline snapshots={_get(data.strategic_timeline_analysis, 'snapshots_count', 0)}",
                _score(data.strategic_timeline_analysis, "strategic_health_score", "stability_score"),
                critical=True,
                contradicted=bool(_get(data.strategic_timeline_analysis, "degradation_detected", False)),
                tags=("strategy", "long_term"),
            )
        )
    if data.session_replay is not None:
        traces.append(
            _trace(
                "session_replay",
                "SessionReplayResult",
                f"Replay sessions={len(_as_tuple(_get(data.session_replay, 'sessions', ())))}",
                _score(data.session_replay, "discipline_score"),
                contradicted=_score(data.session_replay, "discipline_score") < 60,
                tags=("discipline", "experience"),
            )
        )
    if data.trade_journal_result is not None:
        traces.append(
            _trace(
                "trade_journal",
                "JournalAnalysisResult",
                f"Journal trades={_get(data.trade_journal_result, 'total_trades', 0)}",
                _clamp(
                    (
                        float(_get(data.trade_journal_result, "playbook_compliance_rate", 1.0))
                        + float(_get(data.trade_journal_result, "risk_rules_compliance_rate", 1.0))
                    )
                    * 50
                ),
                contradicted=bool(_get(data.trade_journal_result, "trades_to_review", ())),
                tags=("journal", "experience"),
            )
        )
    if data.strategy_dna is not None:
        traces.append(
            _trace(
                "strategy_dna",
                "StrategyDNA",
                f"Strategy DNA {_get(data.strategy_dna, 'name', 'unknown')}",
                90,
                critical=True,
                tags=("strategy", "invariant"),
            )
        )

    return tuple(traces)


def build_memory_clusters(traces: tuple[MemoryTrace, ...]) -> tuple[MemoryCluster, ...]:
    """Group traces into explainable memory clusters."""

    groups = {
        "reasoning_memory": ("reasoning", "audit", "coherence"),
        "strategic_experience": ("strategy", "experience", "journal", "discipline"),
        "invariant_memory": ("invariant", "identity", "intent", "safety"),
        "continuity_memory": ("continuity", "long_term", "world_model", "recovery", "resilience", "stability"),
    }
    clusters: list[MemoryCluster] = []
    assigned: set[str] = set()
    for name, tags in groups.items():
        cluster_traces = tuple(
            trace for trace in traces if trace.trace_id not in assigned and any(tag in trace.tags for tag in tags)
        )
        assigned.update(trace.trace_id for trace in cluster_traces)
        if not cluster_traces:
            continue
        conflict_count = sum(1 for trace in cluster_traces if trace.contradicted)
        confidence = _average(trace.confidence_score for trace in cluster_traces)
        clusters.append(
            MemoryCluster(
                name=name,
                traces=cluster_traces,
                consolidated_summary=f"{len(cluster_traces)} trace(s), {conflict_count} contradiction(s)",
                confidence_score=_clamp(confidence - conflict_count * 8),
                conflict_count=conflict_count,
                protected=any(trace.critical for trace in cluster_traces),
            )
        )
    leftovers = tuple(trace for trace in traces if trace.trace_id not in assigned)
    if leftovers:
        conflict_count = sum(1 for trace in leftovers if trace.contradicted)
        clusters.append(
            MemoryCluster(
                name="misc_memory",
                traces=leftovers,
                consolidated_summary=f"{len(leftovers)} uncategorized trace(s)",
                confidence_score=_average(trace.confidence_score for trace in leftovers),
                conflict_count=conflict_count,
                protected=any(trace.critical for trace in leftovers),
            )
        )
    return tuple(clusters)


def detect_memory_consolidation_risks(
    data: CognitiveMemoryConsolidationInput,
    traces: Optional[tuple[MemoryTrace, ...]] = None,
    clusters: Optional[tuple[MemoryCluster, ...]] = None,
) -> tuple[MemoryConsolidationRisk, ...]:
    """Detect risks created by weak or contradictory cognitive memory."""

    traces = traces or build_memory_traces(data)
    clusters = clusters or build_memory_clusters(traces)
    risks: list[MemoryConsolidationRisk] = []
    contradicted = tuple(trace for trace in traces if trace.contradicted)
    critical_contradicted = tuple(trace for trace in contradicted if trace.critical)

    if len(clusters) < 3 or len(traces) <= 2:
        risks.append(MemoryConsolidationRisk.MEMORY_FRAGMENTATION)
    if contradicted:
        risks.append(MemoryConsolidationRisk.CONTRADICTORY_MEMORY_TRACE)
    if not any("reasoning" in trace.tags for trace in traces) or _risks_contain(data.cognitive_coherence, "REASONING_CHAIN_BREAK"):
        risks.append(MemoryConsolidationRisk.REASONING_TRACE_LOSS)
    if not any("experience" in trace.tags or "strategy" in trace.tags for trace in traces):
        risks.append(MemoryConsolidationRisk.STRATEGIC_EXPERIENCE_LOSS)
    if (
        _has(_get(data.cognitive_alignment, "state"), "MISALIGNMENT", "LOCKED")
        or _has(_get(data.intent_integrity, "state"), "DRIFT", "CONFLICT", "LOCKED")
        or _risks_contain(data.cognitive_alignment, "BREAK")
    ):
        risks.append(MemoryConsolidationRisk.INVARIANT_MEMORY_DRIFT)
    if len(traces) > 12 and len(critical_contradicted) > 1:
        risks.append(MemoryConsolidationRisk.CONSOLIDATION_OVERWRITE_RISK)
    if _average(trace.confidence_score for trace in traces) < 55:
        risks.append(MemoryConsolidationRisk.LOW_MEMORY_CONFIDENCE)
    if (
        _has(_get(data.cognitive_identity, "state"), "DRIFT", "CONFLICT", "LOCKED", "AT_RISK")
        or _risks_contain(data.cognitive_identity, "MISMATCH", "DRIFT")
    ):
        risks.append(MemoryConsolidationRisk.IDENTITY_MEMORY_MISMATCH)
    if (
        _has(_get(data.cognitive_continuity, "state"), "BREAK", "FRAGMENTED", "FAILURE", "RISK")
        or _risks_contain(data.cognitive_continuity, "BREAK", "LOSS")
    ):
        risks.append(MemoryConsolidationRisk.CONTINUITY_MEMORY_BREAK)
    if len(critical_contradicted) >= 4 or (
        MemoryConsolidationRisk.INVARIANT_MEMORY_DRIFT in risks
        and MemoryConsolidationRisk.CONTINUITY_MEMORY_BREAK in risks
        and MemoryConsolidationRisk.IDENTITY_MEMORY_MISMATCH in risks
    ):
        risks.append(MemoryConsolidationRisk.MEMORY_CORRUPTION_RISK)

    return _dedupe(risks)


def compute_memory_consolidation_score(
    data: CognitiveMemoryConsolidationInput,
    traces: Optional[tuple[MemoryTrace, ...]] = None,
    clusters: Optional[tuple[MemoryCluster, ...]] = None,
    risks: tuple[MemoryConsolidationRisk, ...] = (),
) -> MemoryConsolidationScore:
    """Compute deterministic 0..100 memory consolidation scores."""

    traces = traces or build_memory_traces(data)
    clusters = clusters or build_memory_clusters(traces)
    trace_integrity = _average(trace.confidence_score for trace in traces)
    contradiction_count = sum(1 for trace in traces if trace.contradicted)
    strategic = _average(
        trace.confidence_score for trace in traces if any(tag in trace.tags for tag in ("strategy", "experience", "journal"))
    )
    invariant = _average(trace.confidence_score for trace in traces if "invariant" in trace.tags or "identity" in trace.tags)
    continuity = _average(
        (
            _score(data.cognitive_continuity, "cognitive_continuity_score", "continuity_score", default=80),
            _score(data.strategic_timeline_analysis, "strategic_health_score", "stability_score", default=80),
        )
    )
    identity = _score(data.cognitive_identity, "cognitive_identity_score", "identity_score", default=invariant)
    sync = _average(cluster.confidence_score for cluster in clusters)
    protection = 90 if any(cluster.protected for cluster in clusters) else 65
    cleanup = _clamp(100 - contradiction_count * 14)

    values = {
        "trace": trace_integrity,
        "strategic": strategic,
        "invariant": invariant,
        "cleanup": cleanup,
        "continuity": continuity,
        "identity": identity,
        "sync": sync,
        "protection": protection,
    }
    penalties = {
        MemoryConsolidationRisk.MEMORY_FRAGMENTATION: ("sync", 20),
        MemoryConsolidationRisk.CONTRADICTORY_MEMORY_TRACE: ("cleanup", 25),
        MemoryConsolidationRisk.REASONING_TRACE_LOSS: ("trace", 20),
        MemoryConsolidationRisk.STRATEGIC_EXPERIENCE_LOSS: ("strategic", 20),
        MemoryConsolidationRisk.INVARIANT_MEMORY_DRIFT: ("invariant", 28),
        MemoryConsolidationRisk.CONSOLIDATION_OVERWRITE_RISK: ("protection", 28),
        MemoryConsolidationRisk.LOW_MEMORY_CONFIDENCE: ("trace", 25),
        MemoryConsolidationRisk.IDENTITY_MEMORY_MISMATCH: ("identity", 28),
        MemoryConsolidationRisk.CONTINUITY_MEMORY_BREAK: ("continuity", 28),
    }
    for risk in risks:
        if risk in penalties:
            key, penalty = penalties[risk]
            values[key] = _clamp(values[key] - penalty)
    overall = _average(values.values())
    if MemoryConsolidationRisk.MEMORY_CORRUPTION_RISK in risks:
        overall = _clamp(overall - 35)

    return MemoryConsolidationScore(
        trace_integrity_score=values["trace"],
        strategic_experience_score=values["strategic"],
        invariant_stability_score=values["invariant"],
        contradiction_cleanup_score=values["cleanup"],
        continuity_score=values["continuity"],
        identity_memory_score=values["identity"],
        long_term_sync_score=values["sync"],
        snapshot_protection_score=values["protection"],
        overall_memory_score=overall,
    )


def consolidate_memory_snapshot(
    traces: tuple[MemoryTrace, ...],
    clusters: tuple[MemoryCluster, ...],
    score: MemoryConsolidationScore,
    risks: tuple[MemoryConsolidationRisk, ...] = (),
) -> ConsolidatedMemorySnapshot:
    """Create an explainable consolidated memory snapshot."""

    critical_ids = tuple(trace.trace_id for trace in traces if trace.critical)
    cleaned = sum(cluster.conflict_count for cluster in clusters)
    protected = bool(critical_ids) or any(
        risk
        in risks
        for risk in (
            MemoryConsolidationRisk.CONSOLIDATION_OVERWRITE_RISK,
            MemoryConsolidationRisk.IDENTITY_MEMORY_MISMATCH,
            MemoryConsolidationRisk.CONTINUITY_MEMORY_BREAK,
        )
    )
    locked = MemoryConsolidationRisk.MEMORY_CORRUPTION_RISK in risks
    summary = (
        f"Consolidated {len(traces)} trace(s) into {len(clusters)} cluster(s); "
        f"{cleaned} contradiction(s) marked for cleanup."
    )
    return ConsolidatedMemorySnapshot(
        summary=summary,
        clusters=clusters,
        preserved_invariants=CORE_INVARIANTS,
        critical_trace_ids=critical_ids,
        contradictions_cleaned=cleaned,
        memory_confidence_score=score.overall_memory_score,
        protected=protected,
        locked=locked,
    )


def generate_memory_consolidation_recommendations(
    risks: tuple[MemoryConsolidationRisk, ...],
) -> tuple[MemoryConsolidationRecommendation, ...]:
    recommendations: list[MemoryConsolidationRecommendation] = [
        MemoryConsolidationRecommendation.CONTINUE_MEMORY_MONITORING,
        MemoryConsolidationRecommendation.UPDATE_CONSOLIDATED_MEMORY,
    ]
    if MemoryConsolidationRisk.MEMORY_FRAGMENTATION in risks:
        recommendations.append(MemoryConsolidationRecommendation.EXTEND_MEMORY_CHECKPOINTS)
    if MemoryConsolidationRisk.CONTRADICTORY_MEMORY_TRACE in risks:
        recommendations.append(MemoryConsolidationRecommendation.REPAIR_CONFLICTED_TRACES)
        recommendations.append(MemoryConsolidationRecommendation.MERGE_SAFE_TRACES_ONLY)
    if MemoryConsolidationRisk.CONSOLIDATION_OVERWRITE_RISK in risks:
        recommendations.append(MemoryConsolidationRecommendation.AVOID_OVERWRITE)
    if any(
        risk in risks
        for risk in (
            MemoryConsolidationRisk.STRATEGIC_EXPERIENCE_LOSS,
            MemoryConsolidationRisk.CONTINUITY_MEMORY_BREAK,
        )
    ):
        recommendations.append(MemoryConsolidationRecommendation.PRESERVE_STRATEGIC_SNAPSHOTS)
    if any(
        risk
        in risks
        for risk in (
            MemoryConsolidationRisk.INVARIANT_MEMORY_DRIFT,
            MemoryConsolidationRisk.IDENTITY_MEMORY_MISMATCH,
            MemoryConsolidationRisk.MEMORY_CORRUPTION_RISK,
        )
    ):
        recommendations.append(MemoryConsolidationRecommendation.RECHECK_IDENTITY_MEMORY)
        recommendations.append(MemoryConsolidationRecommendation.KEEP_AUTONOMY_REDUCED)
        recommendations.append(MemoryConsolidationRecommendation.REQUIRE_SUPERVISION)
    return _dedupe(recommendations)


def _actions_for_risks(risks: tuple[MemoryConsolidationRisk, ...]) -> tuple[MemoryConsolidationAction, ...]:
    actions: list[MemoryConsolidationAction] = [
        MemoryConsolidationAction.PRESERVE_MEMORY_STATE,
        MemoryConsolidationAction.MERGE_REASONING_TRACES,
        MemoryConsolidationAction.SYNC_LONG_TERM_MEMORY,
    ]
    if MemoryConsolidationRisk.STRATEGIC_EXPERIENCE_LOSS not in risks:
        actions.append(MemoryConsolidationAction.COMPRESS_STRATEGIC_EXPERIENCE)
    if any(
        risk in risks
        for risk in (
            MemoryConsolidationRisk.INVARIANT_MEMORY_DRIFT,
            MemoryConsolidationRisk.IDENTITY_MEMORY_MISMATCH,
        )
    ):
        actions.append(MemoryConsolidationAction.STABILIZE_INVARIANT_MEMORY)
    if MemoryConsolidationRisk.CONTRADICTORY_MEMORY_TRACE in risks:
        actions.append(MemoryConsolidationAction.CLEAN_CONTRADICTIONS)
    if any(
        risk
        in risks
        for risk in (
            MemoryConsolidationRisk.CONSOLIDATION_OVERWRITE_RISK,
            MemoryConsolidationRisk.CONTINUITY_MEMORY_BREAK,
            MemoryConsolidationRisk.MEMORY_CORRUPTION_RISK,
        )
    ):
        actions.append(MemoryConsolidationAction.PROTECT_MEMORY_SNAPSHOT)
        actions.append(MemoryConsolidationAction.REDUCE_AUTONOMY)
    if MemoryConsolidationRisk.MEMORY_CORRUPTION_RISK in risks:
        actions.append(MemoryConsolidationAction.REQUIRE_HUMAN_REVIEW)
        actions.append(MemoryConsolidationAction.LOCK_MEMORY_STATE)
    return _dedupe(actions)


def _state_and_mode(
    score: int,
    risks: tuple[MemoryConsolidationRisk, ...],
) -> tuple[MemoryConsolidationState, MemoryConsolidationMode]:
    if MemoryConsolidationRisk.MEMORY_CORRUPTION_RISK in risks:
        return MemoryConsolidationState.MEMORY_LOCKED, MemoryConsolidationMode.LOCKED_MEMORY_MODE
    if score < 35 or len(risks) >= 7:
        return MemoryConsolidationState.MEMORY_AT_RISK, MemoryConsolidationMode.SAFE_MEMORY_MODE
    if MemoryConsolidationRisk.CONTRADICTORY_MEMORY_TRACE in risks:
        return MemoryConsolidationState.MEMORY_CONFLICTED, MemoryConsolidationMode.CONTRADICTION_CLEANUP
    if MemoryConsolidationRisk.MEMORY_FRAGMENTATION in risks:
        return MemoryConsolidationState.MEMORY_FRAGMENTED, MemoryConsolidationMode.TRACE_MERGING
    if MemoryConsolidationRisk.INVARIANT_MEMORY_DRIFT in risks:
        return MemoryConsolidationState.MEMORY_REPAIRING, MemoryConsolidationMode.INVARIANT_STABILIZATION
    if risks or score < 75:
        return MemoryConsolidationState.MEMORY_WATCH, MemoryConsolidationMode.LONG_TERM_MEMORY_SYNC
    return MemoryConsolidationState.MEMORY_CONSOLIDATED, MemoryConsolidationMode.NORMAL_CONSOLIDATION


def evaluate_cognitive_memory_consolidation(
    data: CognitiveMemoryConsolidationInput,
) -> CognitiveMemoryConsolidationResult:
    """Consolidate cognitive memory traces into a stable offline snapshot."""

    traces = build_memory_traces(data)
    clusters = build_memory_clusters(traces)
    risks = detect_memory_consolidation_risks(data, traces, clusters)
    score_breakdown = compute_memory_consolidation_score(data, traces, clusters, risks)
    snapshot = consolidate_memory_snapshot(traces, clusters, score_breakdown, risks)
    score = score_breakdown.overall_memory_score
    state, mode = _state_and_mode(score, risks)
    actions = _actions_for_risks(risks)
    recommendations = generate_memory_consolidation_recommendations(risks)
    events = (
        MemoryConsolidationEvent(
            name="COGNITIVE_MEMORY_CONSOLIDATED",
            detail=f"Memory score {score} with {len(traces)} trace(s) and {len(risks)} risk(s).",
            severity="WARNING" if risks else "INFO",
        ),
    )
    summary = (
        "Cognitive memory locked because corruption risk is critical."
        if state == MemoryConsolidationState.MEMORY_LOCKED
        else "Cognitive memory requires cleanup before broad consolidation."
        if risks
        else "Cognitive memory consolidated with stable invariants."
    )
    return CognitiveMemoryConsolidationResult(
        state=state,
        mode=mode,
        memory_consolidation_score=score,
        score_breakdown=score_breakdown,
        traces=traces,
        clusters=clusters,
        snapshot=snapshot,
        risks=risks,
        actions=actions,
        recommendations=recommendations,
        events=events,
        summary=summary,
    )


def render_cognitive_memory_consolidation_markdown(result: CognitiveMemoryConsolidationResult) -> str:
    """Render the cognitive memory consolidation report."""

    traces = "\n".join(
        f"- {trace.trace_id}: {trace.source} ({trace.confidence_score}/100), critical={trace.critical}, contradicted={trace.contradicted}"
        for trace in result.traces
    ) or "- No traces."
    clusters = "\n".join(
        f"- {cluster.name}: {cluster.confidence_score}/100, conflicts={cluster.conflict_count}, protected={cluster.protected}"
        for cluster in result.clusters
    ) or "- No clusters."
    snapshot = "\n".join(
        (
            f"- Summary: {result.snapshot.summary}",
            f"- Memory confidence: {result.snapshot.memory_confidence_score}/100",
            f"- Protected: {result.snapshot.protected}",
            f"- Locked: {result.snapshot.locked}",
            f"- Preserved invariants: {', '.join(result.snapshot.preserved_invariants)}",
        )
    )
    risks = "\n".join(f"- {risk.value}" for risk in result.risks) or "- No critical memory risks."
    actions = "\n".join(f"- {action.value}" for action in result.actions) or "- No actions."
    recommendations = "\n".join(f"- {rec.value}" for rec in result.recommendations) or "- No recommendations."

    return "\n".join(
        (
            "# Cognitive Memory Consolidation State",
            f"- State: {result.state.value}",
            f"- Mode: {result.mode.value}",
            "",
            "# Memory Score",
            f"- Score: {result.memory_consolidation_score}/100",
            f"- Trace integrity: {result.score_breakdown.trace_integrity_score}/100",
            f"- Invariant stability: {result.score_breakdown.invariant_stability_score}/100",
            "",
            "# Memory Traces",
            traces,
            "",
            "# Memory Clusters",
            clusters,
            "",
            "# Consolidated Snapshot",
            snapshot,
            "",
            "# Memory Risks",
            risks,
            "",
            "# Actions",
            actions,
            "",
            "# Recommendations",
            recommendations,
            "",
            "# AGIcore Memory Consolidation Outlook",
            f"- Summary: {result.summary}",
            "- Offline only: no broker, no external API, no live execution.",
        )
    )
