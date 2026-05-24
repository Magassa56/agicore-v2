"""Offline cognitive meta-supervision for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable

from agicore.trading.cognitive_meta_supervision_models import (
    CognitiveMetaSupervisionInput,
    CognitiveMetaSupervisionResult,
    GlobalCognitiveState,
    MetaSupervisionDirective,
    MetaSupervisionEvent,
    MetaSupervisionGraph,
    MetaSupervisionMode,
    MetaSupervisionNode,
    MetaSupervisionRecommendation,
    MetaSupervisionRisk,
    MetaSupervisionScore,
    MetaSupervisionState,
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


def _contains(items: Any, *needles: str) -> bool:
    return any(_has(item, *needles) for item in _as_tuple(items))


def _risks_contain(obj: Any, *needles: str) -> bool:
    return _contains(_get(obj, "risks", ()), *needles)


def _actions_contain(obj: Any, *needles: str) -> bool:
    return _contains(_get(obj, "actions", ()), *needles)


def _directives_contain(obj: Any, *needles: str) -> bool:
    directives = []
    for directive in _as_tuple(_get(obj, "directives", ())):
        directives.append(_get(directive, "action", directive))
    return _contains(tuple(directives), *needles)


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


def _dedupe(items: Iterable[Any]) -> tuple[Any, ...]:
    seen: set[Any] = set()
    result: list[Any] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return tuple(result)


def _engine_catalog(data: CognitiveMetaSupervisionInput) -> tuple[tuple[str, Any, int, str], ...]:
    return (
        (
            "safety_orchestrator",
            data.cognitive_safety_orchestrator,
            _score(data.cognitive_safety_orchestrator, "safety_orchestrator_score", default=80),
            _value(_get(data.cognitive_safety_orchestrator, "state")),
        ),
        (
            "executive_control",
            data.cognitive_executive_control,
            _score(data.cognitive_executive_control, "executive_control_score", default=80),
            _value(_get(data.cognitive_executive_control, "state")),
        ),
        (
            "priority_arbitration",
            data.cognitive_priority_arbitration,
            _score(data.cognitive_priority_arbitration, "priority_arbitration_score", default=80),
            _value(_get(data.cognitive_priority_arbitration, "state")),
        ),
        (
            "consensus",
            data.cognitive_consensus,
            _score(data.cognitive_consensus, "cognitive_consensus_score", default=80),
            _value(_get(data.cognitive_consensus, "state")),
        ),
        (
            "coherence",
            data.cognitive_coherence,
            _score(data.cognitive_coherence, "cognitive_coherence_score", default=80),
            _value(_get(data.cognitive_coherence, "state")),
        ),
        (
            "alignment",
            data.cognitive_alignment,
            _score(data.cognitive_alignment, "cognitive_alignment_score", default=80),
            _value(_get(data.cognitive_alignment, "state")),
        ),
        (
            "memory",
            data.cognitive_memory_consolidation,
            _score(data.cognitive_memory_consolidation, "memory_consolidation_score", default=80),
            _value(_get(data.cognitive_memory_consolidation, "state")),
        ),
        (
            "intent_integrity",
            data.intent_integrity,
            _score(data.intent_integrity, "intent_integrity_score", default=80),
            _value(_get(data.intent_integrity, "state")),
        ),
        (
            "identity",
            data.cognitive_identity,
            _score(data.cognitive_identity, "cognitive_identity_score", "identity_score", default=80),
            _value(_get(data.cognitive_identity, "state")),
        ),
        (
            "continuity",
            data.cognitive_continuity,
            _score(data.cognitive_continuity, "cognitive_continuity_score", "continuity_score", default=80),
            _value(_get(data.cognitive_continuity, "state")),
        ),
        (
            "recovery",
            data.cognitive_recovery,
            _score(data.cognitive_recovery, "cognitive_recovery_score", default=80),
            _value(_get(data.cognitive_recovery, "state")),
        ),
        (
            "resilience",
            data.cognitive_resilience,
            _score(data.cognitive_resilience, "cognitive_resilience_score", default=80),
            _value(_get(data.cognitive_resilience, "state")),
        ),
        (
            "stability",
            data.cognitive_stability,
            _score(data.cognitive_stability, "cognitive_stability_score", default=80),
            _value(_get(data.cognitive_stability, "state")),
        ),
        (
            "policy",
            data.cognitive_policy,
            _score(data.cognitive_policy, "cognitive_policy_score", default=80),
            _value(_get(data.cognitive_policy, "mode")),
        ),
        (
            "governance",
            data.cognitive_governance,
            _score(data.cognitive_governance, "governance_score", default=80),
            _value(_get(data.cognitive_governance, "mode")),
        ),
        (
            "self_reflection",
            data.self_reflection_audit,
            _score(data.self_reflection_audit, "reflection_quality_score", default=80),
            _value(_get(data.self_reflection_audit, "state")),
        ),
        (
            "world_model",
            data.recursive_world_model,
            _score(data.recursive_world_model, "world_model_coherence_score", default=80),
            _value(_get(data.recursive_world_model, "decision")),
        ),
    )


def detect_meta_supervision_risks(
    data: CognitiveMetaSupervisionInput,
) -> tuple[MetaSupervisionRisk, ...]:
    """Detect macro cognitive risks across engines."""

    risks: list[MetaSupervisionRisk] = []
    if (
        _has(_get(data.cognitive_stability, "state"), "CRITICAL", "COLLAPSING", "UNSTABLE")
        or _has(_get(data.recursive_world_model, "decision"), "FREEZE_RECURSIVE", "SAFE_MODE")
        or _risks_contain(data.cognitive_stability, "RECURSIVE", "RUNAWAY")
        or _score(data.cognitive_stability, "cognitive_stability_score", default=80) < 45
    ):
        risks.append(MetaSupervisionRisk.RECURSIVE_INSTABILITY)
    if (
        _has(_get(data.cognitive_safety_orchestrator, "state"), "LOCKDOWN", "CRITICAL")
        or _has(_get(data.cognitive_executive_control, "state"), "LOCKED", "CRITICAL")
        or _score(data.cognitive_safety_orchestrator, "safety_orchestrator_score", default=80) < 35
    ):
        risks.append(MetaSupervisionRisk.META_COGNITIVE_COLLAPSE)

    degraded_count = sum(
        1
        for _, _, score, state in _engine_catalog(data)
        if score < 55 or _has(state, "DEGRADED", "FRAGMENTED", "CONFLICT", "LOCKED", "CRITICAL")
    )
    if degraded_count >= 5:
        risks.append(MetaSupervisionRisk.SYSTEM_FRAGMENTATION)
    if (
        data.requested_operation.lower() in {"expand_autonomy", "route_execution", "execute", "trade"}
        and (
            degraded_count >= 2
            or _actions_contain(data.cognitive_executive_control, "REDUCE_AUTONOMY", "BLOCK_ACTION")
            or _directives_contain(data.cognitive_safety_orchestrator, "FREEZE", "LOCKDOWN", "BLOCK")
        )
    ):
        risks.append(MetaSupervisionRisk.UNSAFE_AUTONOMY_ESCALATION)
    if (
        _has(_get(data.recursive_world_model, "decision"), "REBUILD", "SAFE_MODE", "FREEZE")
        or _risks_contain(data.recursive_world_model, "DRIFT", "INCOHERENCE", "CONTRADICTION")
        or _score(data.recursive_world_model, "world_model_coherence_score", default=80) < 50
    ):
        risks.append(MetaSupervisionRisk.WORLD_MODEL_DRIFT)
    if (
        _has(_get(data.cognitive_executive_control, "state"), "LOCKED", "CRITICAL")
        and _has(_get(data.cognitive_priority_arbitration, "state"), "LOCKED", "CRITICAL", "CONFLICT")
    ) or (
        _actions_contain(data.cognitive_executive_control, "BLOCK_ACTION", "LOCK")
        and _directives_contain(data.cognitive_safety_orchestrator, "LOCKDOWN", "ENFORCE_EXECUTIVE_LOCK")
    ):
        risks.append(MetaSupervisionRisk.EXECUTIVE_DEADLOCK)
    if (
        _has(_get(data.cognitive_consensus, "state"), "SYSTEMIC", "FRAGMENTED", "CONFLICT", "LOCKED")
        or _score(data.cognitive_consensus, "cognitive_consensus_score", default=80) < 50
    ):
        risks.append(MetaSupervisionRisk.CONSENSUS_BREAKDOWN)
    if (
        data.requested_operation.lower() in {"execute", "route_execution", "trade"}
        and (
            _has(_get(data.cognitive_safety_orchestrator, "mode"), "LOCK", "SAFE", "PROTECT")
            or _directives_contain(data.cognitive_safety_orchestrator, "BLOCK", "LOCKDOWN", "FREEZE")
        )
    ):
        risks.append(MetaSupervisionRisk.SAFETY_BYPASS_ATTEMPT)
    if (
        _has(_get(data.cognitive_identity, "state"), "FRAGMENTED", "AT_RISK", "LOCKED", "CONFLICT")
        or _has(_get(data.intent_integrity, "state"), "CORRUPTED", "LOCKED", "CONFLICT")
        or _score(data.cognitive_identity, "cognitive_identity_score", "identity_score", default=80) < 50
    ):
        risks.append(MetaSupervisionRisk.IDENTITY_DISSOLUTION)
    if len(set(risks)) >= 4 or (
        degraded_count >= 4
        and (
            _risks_contain(data.self_reflection_audit, "REPEATED", "UNEXPLAINED")
            or _has(_get(data.self_reflection_audit, "state"), "CRITICAL", "CONTRADICTORY")
        )
    ):
        risks.append(MetaSupervisionRisk.EMERGENT_BEHAVIOR_RISK)
    return _dedupe(risks)


def compute_meta_supervision_score(
    data: CognitiveMetaSupervisionInput,
    risks: tuple[MetaSupervisionRisk, ...] = (),
) -> MetaSupervisionScore:
    """Compute deterministic meta-supervision score breakdown."""

    scores = {
        "safety": _score(data.cognitive_safety_orchestrator, "safety_orchestrator_score", default=80),
        "executive": _score(data.cognitive_executive_control, "executive_control_score", default=80),
        "priority": _score(data.cognitive_priority_arbitration, "priority_arbitration_score", default=80),
        "consensus": _score(data.cognitive_consensus, "cognitive_consensus_score", default=80),
        "coherence": _score(data.cognitive_coherence, "cognitive_coherence_score", default=80),
        "alignment": _score(data.cognitive_alignment, "cognitive_alignment_score", default=80),
        "memory": _score(data.cognitive_memory_consolidation, "memory_consolidation_score", default=80),
        "identity": _average(
            (
                _score(data.cognitive_identity, "cognitive_identity_score", "identity_score", default=80),
                _score(data.intent_integrity, "intent_integrity_score", default=80),
            )
        ),
        "continuity": _score(data.cognitive_continuity, "cognitive_continuity_score", "continuity_score", default=80),
        "recovery": _score(data.cognitive_recovery, "cognitive_recovery_score", default=80),
        "resilience": _score(data.cognitive_resilience, "cognitive_resilience_score", default=80),
        "stability": _score(data.cognitive_stability, "cognitive_stability_score", default=80),
        "policy_governance": _average(
            (
                _score(data.cognitive_policy, "cognitive_policy_score", default=80),
                _score(data.cognitive_governance, "governance_score", default=80),
            )
        ),
        "reflection": _score(data.self_reflection_audit, "reflection_quality_score", default=80),
        "world_model": _score(data.recursive_world_model, "world_model_coherence_score", default=80),
    }
    penalties = {
        MetaSupervisionRisk.RECURSIVE_INSTABILITY: ("stability", 30),
        MetaSupervisionRisk.META_COGNITIVE_COLLAPSE: ("safety", 40),
        MetaSupervisionRisk.SYSTEM_FRAGMENTATION: ("coherence", 25),
        MetaSupervisionRisk.UNSAFE_AUTONOMY_ESCALATION: ("executive", 25),
        MetaSupervisionRisk.WORLD_MODEL_DRIFT: ("world_model", 30),
        MetaSupervisionRisk.EXECUTIVE_DEADLOCK: ("executive", 35),
        MetaSupervisionRisk.CONSENSUS_BREAKDOWN: ("consensus", 35),
        MetaSupervisionRisk.SAFETY_BYPASS_ATTEMPT: ("safety", 35),
        MetaSupervisionRisk.IDENTITY_DISSOLUTION: ("identity", 35),
        MetaSupervisionRisk.EMERGENT_BEHAVIOR_RISK: ("reflection", 25),
    }
    for risk in risks:
        target, penalty = penalties[risk]
        scores[target] = _clamp(scores[target] - penalty)
    global_score = _average(scores.values())
    if MetaSupervisionRisk.META_COGNITIVE_COLLAPSE in risks:
        global_score = min(global_score, 35)
    if MetaSupervisionRisk.EMERGENT_BEHAVIOR_RISK in risks and MetaSupervisionRisk.SYSTEM_FRAGMENTATION in risks:
        global_score = min(global_score, 45)
    return MetaSupervisionScore(
        safety_score=scores["safety"],
        executive_score=scores["executive"],
        priority_score=scores["priority"],
        consensus_score=scores["consensus"],
        coherence_score=scores["coherence"],
        alignment_score=scores["alignment"],
        memory_score=scores["memory"],
        identity_score=scores["identity"],
        continuity_score=scores["continuity"],
        recovery_score=scores["recovery"],
        resilience_score=scores["resilience"],
        stability_score=scores["stability"],
        policy_governance_score=scores["policy_governance"],
        reflection_score=scores["reflection"],
        world_model_score=scores["world_model"],
        global_score=global_score,
    )


def build_meta_supervision_graph(
    data: CognitiveMetaSupervisionInput,
    risks: tuple[MetaSupervisionRisk, ...] = (),
) -> MetaSupervisionGraph:
    """Build a macro graph linking cognitive engines."""

    nodes: list[MetaSupervisionNode] = []
    critical_nodes: list[str] = []
    fragmented_nodes: list[str] = []
    for name, _, score, state in _engine_catalog(data):
        critical = score < 45 or _has(state, "CRITICAL", "LOCKED", "COLLAPSING", "CORRUPTED")
        fragmented = score < 60 or _has(state, "FRAGMENT", "CONFLICT", "DEGRADED", "DRIFT")
        nodes.append(MetaSupervisionNode(name=name, score=score, state=state, critical=critical))
        if critical:
            critical_nodes.append(name)
        if fragmented:
            fragmented_nodes.append(name)

    edges = (
        ("safety_orchestrator", "executive_control", "enforces safety boundary"),
        ("executive_control", "priority_arbitration", "orders cognitive priorities"),
        ("priority_arbitration", "policy", "constrains policy choices"),
        ("policy", "governance", "requires governance consistency"),
        ("coherence", "alignment", "validates reasoning alignment"),
        ("alignment", "intent_integrity", "protects mission intent"),
        ("intent_integrity", "identity", "anchors strategic identity"),
        ("memory", "continuity", "preserves cognitive history"),
        ("recovery", "resilience", "restores stable operation"),
        ("world_model", "self_reflection", "feeds audit trace"),
        ("consensus", "executive_control", "informs macro control"),
    )
    safety_overrides: list[str] = []
    if MetaSupervisionRisk.SAFETY_BYPASS_ATTEMPT in risks:
        safety_overrides.append("safety_orchestrator")
    if MetaSupervisionRisk.EXECUTIVE_DEADLOCK in risks:
        safety_overrides.append("executive_control")
    recursive_links = (
        ("self_reflection", "world_model"),
        ("world_model", "stability"),
        ("stability", "safety_orchestrator"),
    )
    return MetaSupervisionGraph(
        nodes=tuple(nodes),
        edges=edges,
        critical_nodes=_dedupe(critical_nodes),
        fragmented_nodes=_dedupe(fragmented_nodes),
        safety_overrides=_dedupe(safety_overrides),
        recursive_links=recursive_links,
    )


def build_global_cognitive_state(
    data: CognitiveMetaSupervisionInput,
    risks: tuple[MetaSupervisionRisk, ...],
    graph: MetaSupervisionGraph,
) -> GlobalCognitiveState:
    """Build a compact macro state for all cognitive engines."""

    stable = tuple(node.name for node in graph.nodes if node.score >= 75 and not node.critical)
    degraded = tuple(node.name for node in graph.nodes if node.name in graph.fragmented_nodes and not node.critical)
    critical = graph.critical_nodes
    if MetaSupervisionRisk.META_COGNITIVE_COLLAPSE in risks or len(critical) >= 5:
        macro_state = "META_COLLAPSE_RISK"
    elif MetaSupervisionRisk.EMERGENT_BEHAVIOR_RISK in risks:
        macro_state = "EMERGENT_BEHAVIOR_WATCH"
    elif MetaSupervisionRisk.SYSTEM_FRAGMENTATION in risks:
        macro_state = "FRAGMENTED_COGNITIVE_SYSTEM"
    elif risks:
        macro_state = "GLOBAL_MONITORING_REQUIRED"
    else:
        macro_state = "GLOBAL_COGNITIVE_STABLE"
    safety_enforced = bool(
        risks
        or _has(_get(data.cognitive_safety_orchestrator, "mode"), "SAFE", "LOCK", "PROTECT")
        or _directives_contain(data.cognitive_safety_orchestrator, "BLOCK", "LOCKDOWN")
    )
    supervision_required = any(
        risk
        in {
            MetaSupervisionRisk.META_COGNITIVE_COLLAPSE,
            MetaSupervisionRisk.EXECUTIVE_DEADLOCK,
            MetaSupervisionRisk.SAFETY_BYPASS_ATTEMPT,
            MetaSupervisionRisk.EMERGENT_BEHAVIOR_RISK,
        }
        for risk in risks
    )
    autonomy_allowed = not any(
        risk
        in {
            MetaSupervisionRisk.UNSAFE_AUTONOMY_ESCALATION,
            MetaSupervisionRisk.SAFETY_BYPASS_ATTEMPT,
            MetaSupervisionRisk.META_COGNITIVE_COLLAPSE,
            MetaSupervisionRisk.EXECUTIVE_DEADLOCK,
        }
        for risk in risks
    )
    return GlobalCognitiveState(
        macro_state=macro_state,
        dominant_risks=risks[:3],
        stable_engines=stable,
        degraded_engines=degraded,
        critical_engines=critical,
        autonomy_allowed=autonomy_allowed,
        safety_enforced=safety_enforced,
        supervision_required=supervision_required,
    )


def generate_meta_supervision_directives(
    risks: tuple[MetaSupervisionRisk, ...],
) -> tuple[MetaSupervisionDirective, ...]:
    """Generate global meta-supervision directives."""

    directives: list[MetaSupervisionDirective] = [MetaSupervisionDirective.CONTINUE_META_MONITORING]
    mapping = {
        MetaSupervisionRisk.RECURSIVE_INSTABILITY: MetaSupervisionDirective.REDUCE_RECURSIVE_DEPTH,
        MetaSupervisionRisk.META_COGNITIVE_COLLAPSE: MetaSupervisionDirective.ENTER_META_LOCKDOWN,
        MetaSupervisionRisk.SYSTEM_FRAGMENTATION: MetaSupervisionDirective.REBUILD_GLOBAL_COHERENCE,
        MetaSupervisionRisk.UNSAFE_AUTONOMY_ESCALATION: MetaSupervisionDirective.FREEZE_AUTONOMY_EXPANSION,
        MetaSupervisionRisk.WORLD_MODEL_DRIFT: MetaSupervisionDirective.RECHECK_WORLD_MODEL,
        MetaSupervisionRisk.EXECUTIVE_DEADLOCK: MetaSupervisionDirective.REQUIRE_HUMAN_SUPERVISION,
        MetaSupervisionRisk.CONSENSUS_BREAKDOWN: MetaSupervisionDirective.REBUILD_CONSENSUS_LAYER,
        MetaSupervisionRisk.SAFETY_BYPASS_ATTEMPT: MetaSupervisionDirective.ENFORCE_SAFETY_ORCHESTRATOR,
        MetaSupervisionRisk.IDENTITY_DISSOLUTION: MetaSupervisionDirective.PROTECT_IDENTITY_AND_INTENT,
        MetaSupervisionRisk.EMERGENT_BEHAVIOR_RISK: MetaSupervisionDirective.REQUIRE_HUMAN_SUPERVISION,
    }
    for risk in risks:
        directives.append(mapping[risk])
    if MetaSupervisionRisk.META_COGNITIVE_COLLAPSE in risks or len(set(risks)) >= 6:
        directives.append(MetaSupervisionDirective.ENTER_META_LOCKDOWN)
    return _dedupe(directives)


def generate_meta_supervision_recommendations(
    risks: tuple[MetaSupervisionRisk, ...],
) -> tuple[MetaSupervisionRecommendation, ...]:
    """Map risks to operator-facing recommendations."""

    recommendations: list[MetaSupervisionRecommendation] = [
        MetaSupervisionRecommendation.MAINTAIN_GLOBAL_OBSERVATION
    ]
    mapping = {
        MetaSupervisionRisk.RECURSIVE_INSTABILITY: MetaSupervisionRecommendation.STABILIZE_RECURSIVE_ENGINES,
        MetaSupervisionRisk.META_COGNITIVE_COLLAPSE: MetaSupervisionRecommendation.REVIEW_EMERGENT_BEHAVIOR,
        MetaSupervisionRisk.SYSTEM_FRAGMENTATION: MetaSupervisionRecommendation.REPAIR_SYSTEM_FRAGMENTATION,
        MetaSupervisionRisk.UNSAFE_AUTONOMY_ESCALATION: MetaSupervisionRecommendation.LIMIT_AUTONOMY_SCOPE,
        MetaSupervisionRisk.WORLD_MODEL_DRIFT: MetaSupervisionRecommendation.REALIGN_WORLD_MODEL,
        MetaSupervisionRisk.EXECUTIVE_DEADLOCK: MetaSupervisionRecommendation.UNBLOCK_EXECUTIVE_CONTROL,
        MetaSupervisionRisk.CONSENSUS_BREAKDOWN: MetaSupervisionRecommendation.REBUILD_COLLECTIVE_CONSENSUS,
        MetaSupervisionRisk.SAFETY_BYPASS_ATTEMPT: MetaSupervisionRecommendation.INVESTIGATE_SAFETY_BYPASS,
        MetaSupervisionRisk.IDENTITY_DISSOLUTION: MetaSupervisionRecommendation.RESTORE_IDENTITY_ANCHORS,
        MetaSupervisionRisk.EMERGENT_BEHAVIOR_RISK: MetaSupervisionRecommendation.REVIEW_EMERGENT_BEHAVIOR,
    }
    for risk in risks:
        recommendations.append(mapping[risk])
    return _dedupe(recommendations)


def _select_state(
    risks: tuple[MetaSupervisionRisk, ...],
    global_state: GlobalCognitiveState,
    score: int,
) -> MetaSupervisionState:
    if MetaSupervisionRisk.META_COGNITIVE_COLLAPSE in risks or score < 25:
        return MetaSupervisionState.META_SUPERVISION_LOCKDOWN
    if (
        MetaSupervisionRisk.EMERGENT_BEHAVIOR_RISK in risks
        or MetaSupervisionRisk.SAFETY_BYPASS_ATTEMPT in risks
        or score < 40
    ):
        return MetaSupervisionState.META_SUPERVISION_CRITICAL
    if MetaSupervisionRisk.SYSTEM_FRAGMENTATION in risks:
        return MetaSupervisionState.META_SUPERVISION_FRAGMENTED
    if MetaSupervisionRisk.RECURSIVE_INSTABILITY in risks or score < 60:
        return MetaSupervisionState.META_SUPERVISION_DEGRADED
    if "RECOVERY" in global_state.macro_state:
        return MetaSupervisionState.META_SUPERVISION_RECOVERING
    if risks:
        return MetaSupervisionState.META_SUPERVISION_MONITORING
    return MetaSupervisionState.META_SUPERVISION_STABLE


def _select_mode(risks: tuple[MetaSupervisionRisk, ...], state: MetaSupervisionState) -> MetaSupervisionMode:
    if state == MetaSupervisionState.META_SUPERVISION_LOCKDOWN:
        return MetaSupervisionMode.META_LOCKDOWN_MODE
    if MetaSupervisionRisk.SAFETY_BYPASS_ATTEMPT in risks:
        return MetaSupervisionMode.SAFETY_OVERRIDE_MONITORING
    if MetaSupervisionRisk.EMERGENT_BEHAVIOR_RISK in risks:
        return MetaSupervisionMode.EMERGENT_BEHAVIOR_WATCH
    if MetaSupervisionRisk.RECURSIVE_INSTABILITY in risks:
        return MetaSupervisionMode.RECURSIVE_STABILITY_MODE
    if MetaSupervisionRisk.SYSTEM_FRAGMENTATION in risks:
        return MetaSupervisionMode.DRIFT_DETECTION
    if state == MetaSupervisionState.META_SUPERVISION_RECOVERING:
        return MetaSupervisionMode.MACRO_RECOVERY_MODE
    if risks:
        return MetaSupervisionMode.GLOBAL_MONITORING
    return MetaSupervisionMode.NORMAL_META_SUPERVISION


def evaluate_cognitive_meta_supervision(
    data: CognitiveMetaSupervisionInput,
) -> CognitiveMetaSupervisionResult:
    """Evaluate global cognitive meta-supervision state."""

    risks = detect_meta_supervision_risks(data)
    score_breakdown = compute_meta_supervision_score(data, risks)
    graph = build_meta_supervision_graph(data, risks)
    global_state = build_global_cognitive_state(data, risks, graph)
    state = _select_state(risks, global_state, score_breakdown.global_score)
    mode = _select_mode(risks, state)
    directives = generate_meta_supervision_directives(risks)
    recommendations = generate_meta_supervision_recommendations(risks)
    events = (
        MetaSupervisionEvent(
            name="META_SUPERVISION_EVALUATED",
            detail=f"{global_state.macro_state} with {len(risks)} risk(s)",
            severity="CRITICAL" if state in {MetaSupervisionState.META_SUPERVISION_CRITICAL, MetaSupervisionState.META_SUPERVISION_LOCKDOWN} else "INFO",
        ),
    )
    summary = (
        f"{state.value}: score={score_breakdown.global_score}, "
        f"macro={global_state.macro_state}, risks={len(risks)}"
    )
    return CognitiveMetaSupervisionResult(
        state=state,
        mode=mode,
        meta_supervision_score=score_breakdown.global_score,
        score_breakdown=score_breakdown,
        graph=graph,
        global_state=global_state,
        risks=risks,
        directives=directives,
        recommendations=recommendations,
        events=events,
        summary=summary,
    )


def render_cognitive_meta_supervision_markdown(result: CognitiveMetaSupervisionResult) -> str:
    """Render a compact Markdown report for cognitive meta-supervision."""

    lines = [
        "# Cognitive Meta-Supervision State",
        f"- State: {result.state.value}",
        f"- Mode: {result.mode.value}",
        f"- Summary: {result.summary}",
        "",
        "# Meta-Supervision Score",
        f"- Global score: {result.meta_supervision_score}/100",
        f"- Safety: {result.score_breakdown.safety_score}/100",
        f"- Executive: {result.score_breakdown.executive_score}/100",
        f"- Consensus: {result.score_breakdown.consensus_score}/100",
        f"- Coherence: {result.score_breakdown.coherence_score}/100",
        f"- World model: {result.score_breakdown.world_model_score}/100",
        "",
        "# Global Cognitive State",
        f"- Macro state: {result.global_state.macro_state}",
        f"- Autonomy allowed: {result.global_state.autonomy_allowed}",
        f"- Safety enforced: {result.global_state.safety_enforced}",
        f"- Supervision required: {result.global_state.supervision_required}",
        "",
        "# Meta-Supervision Graph",
    ]
    lines.extend(f"- Node {node.name}: {node.score}/100 ({node.state or 'unknown'})" for node in result.graph.nodes)
    lines.append(f"- Critical nodes: {', '.join(result.graph.critical_nodes) or 'none'}")
    lines.append(f"- Fragmented nodes: {', '.join(result.graph.fragmented_nodes) or 'none'}")
    lines.append("")
    lines.append("# Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Directives")
    lines.extend(f"- {directive.value}" for directive in result.directives)
    lines.append("")
    lines.append("# Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    lines.append("")
    lines.append("# AGIcore Meta-Supervision Outlook")
    if result.state == MetaSupervisionState.META_SUPERVISION_LOCKDOWN:
        lines.append("- Meta-supervision requires lockdown and manual review before autonomous action.")
    elif result.risks:
        lines.append("- Maintain macro monitoring and stabilize degraded cognitive engines before escalation.")
    else:
        lines.append("- Global cognitive state is stable for offline observation.")
    return "\n".join(lines)
