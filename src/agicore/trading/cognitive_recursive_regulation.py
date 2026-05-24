"""Offline cognitive recursive regulation for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable

from agicore.trading.cognitive_recursive_regulation_models import (
    CognitiveRecursiveRegulationInput,
    CognitiveRecursiveRegulationResult,
    RecursiveChainNode,
    RecursiveRegulationDirective,
    RecursiveRegulationEvent,
    RecursiveRegulationGraph,
    RecursiveRegulationMode,
    RecursiveRegulationRecommendation,
    RecursiveRegulationRisk,
    RecursiveRegulationScore,
    RecursiveRegulationState,
    RecursiveStabilizationPlan,
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


def _directives_contain(obj: Any, *needles: str) -> bool:
    values = []
    for directive in _as_tuple(_get(obj, "directives", ())):
        values.append(_get(directive, "action", directive))
    return _contains(tuple(values), *needles)


def _actions_contain(obj: Any, *needles: str) -> bool:
    return _contains(_get(obj, "actions", ()), *needles)


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


def detect_recursive_regulation_risks(
    data: CognitiveRecursiveRegulationInput,
) -> tuple[RecursiveRegulationRisk, ...]:
    """Detect unsafe recursive loops, propagation and expansion."""

    risks: list[RecursiveRegulationRisk] = []
    if data.requested_recursive_depth > data.max_allowed_depth or data.recursive_cycle_count >= 8:
        risks.append(RecursiveRegulationRisk.RUNAWAY_RECURSION)
    if (
        _has(_get(data.recursive_world_model, "decision"), "FREEZE_RECURSIVE", "SAFE_MODE")
        or _risks_contain(data.recursive_world_model, "FEEDBACK_LOOP", "RECURSIVE_FEEDBACK")
        or _directives_contain(data.cognitive_meta_supervision, "REDUCE_RECURSIVE_DEPTH")
    ):
        risks.append(RecursiveRegulationRisk.RECURSIVE_FEEDBACK_LOOP)
    if data.signal_amplification_factor >= 2.0 or _risks_contain(
        data.cognitive_meta_supervision, "EMERGENT_BEHAVIOR", "SYSTEM_FRAGMENTATION"
    ):
        risks.append(RecursiveRegulationRisk.COGNITIVE_SIGNAL_AMPLIFICATION)
    if (
        _score(data.recursive_world_model, "world_model_coherence_score", default=80) < 50
        or _risks_contain(data.recursive_world_model, "DRIFT", "INCOHERENCE", "RECURSIVE")
        or _has(_get(data.recursive_world_model, "decision"), "REBUILD", "SAFE_MODE")
    ):
        risks.append(RecursiveRegulationRisk.WORLD_MODEL_RECURSIVE_DRIFT)
    if (
        _has(_get(data.self_reflection_audit, "state"), "CONTRADICTORY", "CRITICAL", "SELF_CORRECTION")
        or _score(data.self_reflection_audit, "reflection_quality_score", default=80) < 45
        or _risks_contain(data.self_reflection_audit, "SELF", "REFLECTION_FAILURE")
    ):
        risks.append(RecursiveRegulationRisk.SELF_REFERENCE_COLLAPSE)
    if (
        _has(_get(data.cognitive_meta_supervision, "state"), "CRITICAL", "LOCKDOWN")
        or _risks_contain(data.cognitive_meta_supervision, "META", "RECURSIVE_INSTABILITY")
        or _score(data.cognitive_meta_supervision, "meta_supervision_score", default=80) < 45
    ):
        risks.append(RecursiveRegulationRisk.META_LOOP_INSTABILITY)

    unstable_engines = sum(
        1
        for obj, score_name, state_name in (
            (data.cognitive_consensus, "cognitive_consensus_score", "state"),
            (data.cognitive_coherence, "cognitive_coherence_score", "state"),
            (data.cognitive_alignment, "cognitive_alignment_score", "state"),
            (data.intent_integrity, "intent_integrity_score", "state"),
            (data.cognitive_memory_consolidation, "memory_consolidation_score", "state"),
        )
        if _score(obj, score_name, default=80) < 55
        or _has(_get(obj, state_name), "CONFLICT", "LOCKED", "DRIFT", "CORRUPTED", "INCOHERENCE")
    )
    if unstable_engines >= 3:
        risks.append(RecursiveRegulationRisk.CROSS_ENGINE_RECURSIVE_PROPAGATION)
    if (
        _has(_get(data.cognitive_executive_control, "state"), "LOCKED", "CRITICAL")
        or _actions_contain(data.cognitive_executive_control, "LOCK", "FREEZE_RECURSIVE")
        or _score(data.cognitive_executive_control, "executive_control_score", default=80) < 45
    ):
        risks.append(RecursiveRegulationRisk.EXECUTIVE_RECURSION_LOCK)
    if (
        _has(_get(data.cognitive_consensus, "state"), "FRAGMENTED", "SYSTEMIC", "LOCKED", "CONFLICT")
        or _score(data.cognitive_consensus, "cognitive_consensus_score", default=80) < 45
    ):
        risks.append(RecursiveRegulationRisk.RECURSIVE_CONSENSUS_CASCADE)
    if (
        data.requested_recursive_depth >= data.max_allowed_depth + 2
        or data.recursive_cycle_count >= 12
        or _directives_contain(data.cognitive_meta_supervision, "FREEZE_AUTONOMY_EXPANSION", "ENTER_META_LOCKDOWN")
    ):
        risks.append(RecursiveRegulationRisk.UNBOUNDED_REASONING_EXPANSION)
    return _dedupe(risks)


def compute_recursive_regulation_score(
    data: CognitiveRecursiveRegulationInput,
    risks: tuple[RecursiveRegulationRisk, ...] = (),
) -> RecursiveRegulationScore:
    """Compute recursive safety scores normalized to 0..100."""

    depth_pressure = max(0, data.requested_recursive_depth - data.max_allowed_depth)
    cycle_pressure = max(0, data.recursive_cycle_count - 3)
    scores = {
        "depth": _clamp(90 - depth_pressure * 18 - cycle_pressure * 5),
        "feedback": _average(
            (
                _score(data.recursive_world_model, "world_model_coherence_score", default=80),
                _score(data.self_reflection_audit, "reflection_quality_score", default=80),
            )
        ),
        "amplification": _clamp(90 - max(0.0, data.signal_amplification_factor - 1.0) * 25),
        "world_model": _score(data.recursive_world_model, "world_model_coherence_score", default=80),
        "self_reference": _score(data.self_reflection_audit, "reflection_quality_score", default=80),
        "meta_loop": _score(data.cognitive_meta_supervision, "meta_supervision_score", default=80),
        "propagation": _average(
            (
                _score(data.cognitive_coherence, "cognitive_coherence_score", default=80),
                _score(data.cognitive_alignment, "cognitive_alignment_score", default=80),
                _score(data.intent_integrity, "intent_integrity_score", default=80),
                _score(data.cognitive_memory_consolidation, "memory_consolidation_score", default=80),
            )
        ),
        "executive": _score(data.cognitive_executive_control, "executive_control_score", default=80),
        "consensus": _score(data.cognitive_consensus, "cognitive_consensus_score", default=80),
        "reasoning": _clamp(90 - data.requested_recursive_depth * 4 - max(0, data.recursive_cycle_count - 1) * 3),
    }
    penalties = {
        RecursiveRegulationRisk.RUNAWAY_RECURSION: ("depth", 35),
        RecursiveRegulationRisk.RECURSIVE_FEEDBACK_LOOP: ("feedback", 35),
        RecursiveRegulationRisk.COGNITIVE_SIGNAL_AMPLIFICATION: ("amplification", 30),
        RecursiveRegulationRisk.WORLD_MODEL_RECURSIVE_DRIFT: ("world_model", 35),
        RecursiveRegulationRisk.SELF_REFERENCE_COLLAPSE: ("self_reference", 35),
        RecursiveRegulationRisk.META_LOOP_INSTABILITY: ("meta_loop", 35),
        RecursiveRegulationRisk.CROSS_ENGINE_RECURSIVE_PROPAGATION: ("propagation", 30),
        RecursiveRegulationRisk.EXECUTIVE_RECURSION_LOCK: ("executive", 35),
        RecursiveRegulationRisk.RECURSIVE_CONSENSUS_CASCADE: ("consensus", 35),
        RecursiveRegulationRisk.UNBOUNDED_REASONING_EXPANSION: ("reasoning", 40),
    }
    for risk in risks:
        target, penalty = penalties[risk]
        scores[target] = _clamp(scores[target] - penalty)
    overall = _average(scores.values())
    if RecursiveRegulationRisk.UNBOUNDED_REASONING_EXPANSION in risks:
        overall = min(overall, 40)
    if len(set(risks)) >= 6:
        overall = min(overall, 35)
    return RecursiveRegulationScore(
        recursion_depth_score=scores["depth"],
        feedback_loop_score=scores["feedback"],
        amplification_score=scores["amplification"],
        world_model_recursion_score=scores["world_model"],
        self_reference_score=scores["self_reference"],
        meta_loop_score=scores["meta_loop"],
        propagation_score=scores["propagation"],
        executive_recursion_score=scores["executive"],
        consensus_recursion_score=scores["consensus"],
        reasoning_expansion_score=scores["reasoning"],
        overall_score=overall,
    )


def generate_recursive_regulation_directives(
    risks: tuple[RecursiveRegulationRisk, ...],
) -> tuple[RecursiveRegulationDirective, ...]:
    """Generate anti-instability recursive directives."""

    directives: list[RecursiveRegulationDirective] = [
        RecursiveRegulationDirective.CONTINUE_RECURSIVE_MONITORING
    ]
    mapping = {
        RecursiveRegulationRisk.RUNAWAY_RECURSION: RecursiveRegulationDirective.LIMIT_RECURSIVE_DEPTH,
        RecursiveRegulationRisk.RECURSIVE_FEEDBACK_LOOP: RecursiveRegulationDirective.BREAK_FEEDBACK_LOOP,
        RecursiveRegulationRisk.COGNITIVE_SIGNAL_AMPLIFICATION: RecursiveRegulationDirective.THROTTLE_RECURSIVE_SIGNALS,
        RecursiveRegulationRisk.WORLD_MODEL_RECURSIVE_DRIFT: RecursiveRegulationDirective.STABILIZE_WORLD_MODEL_RECURSION,
        RecursiveRegulationRisk.SELF_REFERENCE_COLLAPSE: RecursiveRegulationDirective.PROTECT_SELF_REFERENCE,
        RecursiveRegulationRisk.META_LOOP_INSTABILITY: RecursiveRegulationDirective.LIMIT_RECURSIVE_DEPTH,
        RecursiveRegulationRisk.CROSS_ENGINE_RECURSIVE_PROPAGATION: RecursiveRegulationDirective.CONTAIN_CROSS_ENGINE_PROPAGATION,
        RecursiveRegulationRisk.EXECUTIVE_RECURSION_LOCK: RecursiveRegulationDirective.PROTECT_EXECUTIVE_CONTROL,
        RecursiveRegulationRisk.RECURSIVE_CONSENSUS_CASCADE: RecursiveRegulationDirective.PROTECT_RECURSIVE_CONSENSUS,
        RecursiveRegulationRisk.UNBOUNDED_REASONING_EXPANSION: RecursiveRegulationDirective.LOCK_RECURSIVE_EXPANSION,
    }
    for risk in risks:
        directives.append(mapping[risk])
    if len(set(risks)) >= 5:
        directives.append(RecursiveRegulationDirective.THROTTLE_RECURSIVE_SIGNALS)
        directives.append(RecursiveRegulationDirective.LIMIT_RECURSIVE_DEPTH)
    return _dedupe(directives)


def build_recursive_regulation_graph(
    data: CognitiveRecursiveRegulationInput,
    risks: tuple[RecursiveRegulationRisk, ...] = (),
) -> RecursiveRegulationGraph:
    """Build recursive chain and propagation graph."""

    nodes = (
        RecursiveChainNode(
            "meta_supervision",
            recursion_depth=min(data.requested_recursive_depth, data.max_allowed_depth + 2),
            score=_score(data.cognitive_meta_supervision, "meta_supervision_score", default=80),
            throttled=RecursiveRegulationRisk.META_LOOP_INSTABILITY in risks,
            risk="meta loop instability" if RecursiveRegulationRisk.META_LOOP_INSTABILITY in risks else "",
        ),
        RecursiveChainNode(
            "world_model",
            recursion_depth=data.requested_recursive_depth,
            score=_score(data.recursive_world_model, "world_model_coherence_score", default=80),
            throttled=RecursiveRegulationRisk.WORLD_MODEL_RECURSIVE_DRIFT in risks,
            risk="world model recursive drift" if RecursiveRegulationRisk.WORLD_MODEL_RECURSIVE_DRIFT in risks else "",
        ),
        RecursiveChainNode(
            "self_reflection",
            recursion_depth=max(1, data.requested_recursive_depth - 1),
            score=_score(data.self_reflection_audit, "reflection_quality_score", default=80),
            throttled=RecursiveRegulationRisk.SELF_REFERENCE_COLLAPSE in risks,
            risk="self reference collapse" if RecursiveRegulationRisk.SELF_REFERENCE_COLLAPSE in risks else "",
        ),
        RecursiveChainNode(
            "consensus",
            recursion_depth=max(1, data.requested_recursive_depth - 1),
            score=_score(data.cognitive_consensus, "cognitive_consensus_score", default=80),
            throttled=RecursiveRegulationRisk.RECURSIVE_CONSENSUS_CASCADE in risks,
            risk="recursive consensus cascade" if RecursiveRegulationRisk.RECURSIVE_CONSENSUS_CASCADE in risks else "",
        ),
        RecursiveChainNode(
            "executive_control",
            recursion_depth=1,
            score=_score(data.cognitive_executive_control, "executive_control_score", default=80),
            throttled=RecursiveRegulationRisk.EXECUTIVE_RECURSION_LOCK in risks,
            risk="executive recursion lock" if RecursiveRegulationRisk.EXECUTIVE_RECURSION_LOCK in risks else "",
        ),
    )
    edges = (
        ("meta_supervision", "world_model", "observes recursive world state"),
        ("world_model", "self_reflection", "feeds recursive audit"),
        ("self_reflection", "meta_supervision", "returns self-reference"),
        ("consensus", "executive_control", "feeds control decision"),
        ("executive_control", "meta_supervision", "limits recursion"),
    )
    feedback_loops = ()
    if RecursiveRegulationRisk.RECURSIVE_FEEDBACK_LOOP in risks:
        feedback_loops = (("world_model", "self_reflection"), ("self_reflection", "meta_supervision"))
    propagation_paths = ()
    if RecursiveRegulationRisk.CROSS_ENGINE_RECURSIVE_PROPAGATION in risks:
        propagation_paths = (
            ("coherence", "alignment", "reasoning propagation"),
            ("alignment", "intent_integrity", "intent propagation"),
            ("intent_integrity", "memory", "memory propagation"),
        )
    throttled_nodes = tuple(node.name for node in nodes if node.throttled)
    locked_nodes = ("recursive_expansion",) if RecursiveRegulationRisk.UNBOUNDED_REASONING_EXPANSION in risks else ()
    return RecursiveRegulationGraph(
        nodes=nodes,
        edges=edges,
        feedback_loops=feedback_loops,
        propagation_paths=propagation_paths,
        throttled_nodes=throttled_nodes,
        locked_nodes=locked_nodes,
        max_depth=data.max_allowed_depth,
    )


def build_recursive_stabilization_plan(
    data: CognitiveRecursiveRegulationInput,
    directives: tuple[RecursiveRegulationDirective, ...],
    risks: tuple[RecursiveRegulationRisk, ...],
) -> RecursiveStabilizationPlan:
    """Build a deterministic plan for recursive stabilization."""

    steps = ["Monitor recursive chain and keep all regulation offline."]
    if RecursiveRegulationDirective.LIMIT_RECURSIVE_DEPTH in directives:
        steps.append(f"Limit recursive depth to {data.max_allowed_depth}.")
    if RecursiveRegulationDirective.THROTTLE_RECURSIVE_SIGNALS in directives:
        steps.append("Throttle amplified recursive signals before propagation.")
    if RecursiveRegulationDirective.BREAK_FEEDBACK_LOOP in directives:
        steps.append("Break unsafe feedback loops between world model, reflection and meta-supervision.")
    if RecursiveRegulationDirective.CONTAIN_CROSS_ENGINE_PROPAGATION in directives:
        steps.append("Contain cross-engine recursive propagation.")
    if RecursiveRegulationDirective.PROTECT_RECURSIVE_CONSENSUS in directives:
        steps.append("Protect recursive consensus from cascade amplification.")
    if RecursiveRegulationDirective.PROTECT_EXECUTIVE_CONTROL in directives:
        steps.append("Protect executive control from recursive lock.")
    if RecursiveRegulationDirective.LOCK_RECURSIVE_EXPANSION in directives:
        steps.append("Lock unbounded reasoning expansion pending manual review.")
    return RecursiveStabilizationPlan(
        max_allowed_depth=data.max_allowed_depth,
        throttle_active=any(
            directive
            in {
                RecursiveRegulationDirective.THROTTLE_RECURSIVE_SIGNALS,
                RecursiveRegulationDirective.LIMIT_RECURSIVE_DEPTH,
                RecursiveRegulationDirective.LOCK_RECURSIVE_EXPANSION,
            }
            for directive in directives
        ),
        propagation_contained=RecursiveRegulationRisk.CROSS_ENGINE_RECURSIVE_PROPAGATION in risks,
        consensus_protected=RecursiveRegulationDirective.PROTECT_RECURSIVE_CONSENSUS in directives,
        executive_protected=RecursiveRegulationDirective.PROTECT_EXECUTIVE_CONTROL in directives,
        world_model_stabilized=RecursiveRegulationDirective.STABILIZE_WORLD_MODEL_RECURSION in directives,
        steps=tuple(steps),
        directives=directives,
    )


def generate_recursive_regulation_recommendations(
    risks: tuple[RecursiveRegulationRisk, ...],
) -> tuple[RecursiveRegulationRecommendation, ...]:
    """Map recursive risks to corrective recommendations."""

    recommendations: list[RecursiveRegulationRecommendation] = [
        RecursiveRegulationRecommendation.MAINTAIN_RECURSIVE_OBSERVATION
    ]
    mapping = {
        RecursiveRegulationRisk.RUNAWAY_RECURSION: RecursiveRegulationRecommendation.REDUCE_RECURSIVE_DEPTH,
        RecursiveRegulationRisk.RECURSIVE_FEEDBACK_LOOP: RecursiveRegulationRecommendation.REBUILD_RECURSIVE_CHAIN,
        RecursiveRegulationRisk.COGNITIVE_SIGNAL_AMPLIFICATION: RecursiveRegulationRecommendation.SLOW_REASONING_EXPANSION,
        RecursiveRegulationRisk.WORLD_MODEL_RECURSIVE_DRIFT: RecursiveRegulationRecommendation.REALIGN_WORLD_MODEL_RECURSION,
        RecursiveRegulationRisk.SELF_REFERENCE_COLLAPSE: RecursiveRegulationRecommendation.STABILIZE_SELF_REFERENCE,
        RecursiveRegulationRisk.META_LOOP_INSTABILITY: RecursiveRegulationRecommendation.REDUCE_RECURSIVE_DEPTH,
        RecursiveRegulationRisk.CROSS_ENGINE_RECURSIVE_PROPAGATION: RecursiveRegulationRecommendation.ISOLATE_RECURSIVE_ENGINE,
        RecursiveRegulationRisk.EXECUTIVE_RECURSION_LOCK: RecursiveRegulationRecommendation.RECHECK_EXECUTIVE_RECURSION,
        RecursiveRegulationRisk.RECURSIVE_CONSENSUS_CASCADE: RecursiveRegulationRecommendation.REBUILD_RECURSIVE_CONSENSUS,
        RecursiveRegulationRisk.UNBOUNDED_REASONING_EXPANSION: RecursiveRegulationRecommendation.REQUIRE_MANUAL_RECURSION_REVIEW,
    }
    for risk in risks:
        recommendations.append(mapping[risk])
    return _dedupe(recommendations)


def _select_state(risks: tuple[RecursiveRegulationRisk, ...], score: int) -> RecursiveRegulationState:
    if RecursiveRegulationRisk.UNBOUNDED_REASONING_EXPANSION in risks or score < 25:
        return RecursiveRegulationState.RECURSION_LOCKED
    if len(set(risks)) >= 6 or RecursiveRegulationRisk.RUNAWAY_RECURSION in risks and score < 45:
        return RecursiveRegulationState.RECURSION_CRITICAL
    if RecursiveRegulationRisk.CROSS_ENGINE_RECURSIVE_PROPAGATION in risks:
        return RecursiveRegulationState.RECURSION_DEGRADED
    if RecursiveRegulationRisk.RUNAWAY_RECURSION in risks or RecursiveRegulationRisk.COGNITIVE_SIGNAL_AMPLIFICATION in risks:
        return RecursiveRegulationState.RECURSION_THROTTLED
    if RecursiveRegulationRisk.META_LOOP_INSTABILITY in risks:
        return RecursiveRegulationState.RECURSION_RECOVERING
    if risks:
        return RecursiveRegulationState.RECURSION_MONITORING
    return RecursiveRegulationState.RECURSION_STABLE


def _select_mode(risks: tuple[RecursiveRegulationRisk, ...], state: RecursiveRegulationState) -> RecursiveRegulationMode:
    if state == RecursiveRegulationState.RECURSION_LOCKED:
        return RecursiveRegulationMode.RECURSIVE_LOCKDOWN
    if state == RecursiveRegulationState.RECURSION_CRITICAL:
        return RecursiveRegulationMode.RECURSIVE_SAFE_MODE
    if RecursiveRegulationRisk.RECURSIVE_FEEDBACK_LOOP in risks:
        return RecursiveRegulationMode.FEEDBACK_LOOP_CONTROL
    if RecursiveRegulationRisk.CROSS_ENGINE_RECURSIVE_PROPAGATION in risks:
        return RecursiveRegulationMode.PROPAGATION_CONTROL
    if RecursiveRegulationRisk.RUNAWAY_RECURSION in risks or RecursiveRegulationRisk.COGNITIVE_SIGNAL_AMPLIFICATION in risks:
        return RecursiveRegulationMode.RECURSIVE_THROTTLING
    if risks:
        return RecursiveRegulationMode.RECURSIVE_STABILIZATION
    return RecursiveRegulationMode.NORMAL_RECURSIVE_REGULATION


def evaluate_cognitive_recursive_regulation(
    data: CognitiveRecursiveRegulationInput,
) -> CognitiveRecursiveRegulationResult:
    """Evaluate recursive regulation and generate anti-instability controls."""

    risks = detect_recursive_regulation_risks(data)
    score_breakdown = compute_recursive_regulation_score(data, risks)
    directives = generate_recursive_regulation_directives(risks)
    graph = build_recursive_regulation_graph(data, risks)
    plan = build_recursive_stabilization_plan(data, directives, risks)
    state = _select_state(risks, score_breakdown.overall_score)
    mode = _select_mode(risks, state)
    recommendations = generate_recursive_regulation_recommendations(risks)
    events = (
        RecursiveRegulationEvent(
            name="RECURSIVE_REGULATION_EVALUATED",
            detail=f"{state.value} with {len(risks)} risk(s)",
            severity="CRITICAL" if state in {RecursiveRegulationState.RECURSION_CRITICAL, RecursiveRegulationState.RECURSION_LOCKED} else "INFO",
        ),
    )
    summary = f"{state.value}: score={score_breakdown.overall_score}, risks={len(risks)}, max_depth={data.max_allowed_depth}"
    return CognitiveRecursiveRegulationResult(
        state=state,
        mode=mode,
        recursive_regulation_score=score_breakdown.overall_score,
        score_breakdown=score_breakdown,
        graph=graph,
        stabilization_plan=plan,
        risks=risks,
        directives=directives,
        recommendations=recommendations,
        events=events,
        summary=summary,
    )


def render_cognitive_recursive_regulation_markdown(result: CognitiveRecursiveRegulationResult) -> str:
    """Render an explainable Markdown report for recursive regulation."""

    lines = [
        "# Cognitive Recursive Regulation State",
        f"- State: {result.state.value}",
        f"- Mode: {result.mode.value}",
        f"- Summary: {result.summary}",
        "",
        "# Recursive Safety Score",
        f"- Overall score: {result.recursive_regulation_score}/100",
        f"- Depth: {result.score_breakdown.recursion_depth_score}/100",
        f"- Feedback loop: {result.score_breakdown.feedback_loop_score}/100",
        f"- Amplification: {result.score_breakdown.amplification_score}/100",
        f"- World model recursion: {result.score_breakdown.world_model_recursion_score}/100",
        "",
        "# Recursive Regulation Graph",
    ]
    lines.extend(
        f"- Node {node.name}: depth={node.recursion_depth}, score={node.score}/100, throttled={node.throttled}"
        for node in result.graph.nodes
    )
    lines.append(f"- Feedback loops: {len(result.graph.feedback_loops)}")
    lines.append(f"- Propagation paths: {len(result.graph.propagation_paths)}")
    lines.append(f"- Throttled nodes: {', '.join(result.graph.throttled_nodes) or 'none'}")
    lines.append("")
    lines.append("# Recursive Stabilization Plan")
    lines.extend(f"- {step}" for step in result.stabilization_plan.steps)
    lines.append(f"- Throttle active: {result.stabilization_plan.throttle_active}")
    lines.append(f"- Propagation contained: {result.stabilization_plan.propagation_contained}")
    lines.append("")
    lines.append("# Recursive Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Directives")
    lines.extend(f"- {directive.value}" for directive in result.directives)
    lines.append("")
    lines.append("# Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    lines.append("")
    lines.append("# AGIcore Recursive Regulation Outlook")
    if result.state == RecursiveRegulationState.RECURSION_LOCKED:
        lines.append("- Recursive expansion is locked until manual review and stabilization.")
    elif result.risks:
        lines.append("- Recursive loops require throttling, containment and continued offline monitoring.")
    else:
        lines.append("- Recursive chain is stable under current offline limits.")
    return "\n".join(lines)
