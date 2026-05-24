"""Offline cognitive executive control engine for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Optional

from agicore.trading.cognitive_executive_control_models import (
    CognitiveExecutiveControlInput,
    CognitiveExecutiveControlResult,
    ExecutiveControlAction,
    ExecutiveControlDecisionGraph,
    ExecutiveControlDirective,
    ExecutiveControlEvent,
    ExecutiveControlMode,
    ExecutiveControlRecommendation,
    ExecutiveControlRisk,
    ExecutiveControlScore,
    ExecutiveControlState,
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


def _risks_contain(obj: Any, *needles: str) -> bool:
    return any(_has(risk, *needles) for risk in _as_tuple(_get(obj, "risks", ())))


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


def detect_executive_control_risks(
    data: CognitiveExecutiveControlInput,
) -> tuple[ExecutiveControlRisk, ...]:
    """Detect risks that require executive control over cognitive actions."""

    risks: list[ExecutiveControlRisk] = []

    if (
        _has(_get(data.system_integrity, "status"), "COMPROMISED", "PROTECTION", "ROLLBACK")
        or _has(_get(data.global_orchestrator, "mode"), "EMERGENCY", "SURVIVAL")
        or _risks_contain(data.system_integrity, "SAFETY_LOCKDOWN", "LOW_SYSTEM_CONFIDENCE")
    ):
        risks.append(ExecutiveControlRisk.EXECUTIVE_OVERRIDE_REQUIRED)

    if (
        _has(_get(data.cognitive_governance, "autonomy_level"), "FULL")
        and (
            _score(data.cognitive_alignment, "cognitive_alignment_score", default=80) < 60
            or _score(data.cognitive_coherence, "cognitive_coherence_score", default=80) < 60
            or _score(data.cognitive_consensus, "cognitive_consensus_score", default=80) < 60
        )
    ) or _risks_contain(data.cognitive_governance, "AUTONOMY", "UNSAFE_PERMISSION"):
        risks.append(ExecutiveControlRisk.AUTONOMY_TOO_HIGH)

    if (
        _has(_get(data.cognitive_policy, "mode"), "LOCKED", "SAFE", "RESTRICTED")
        or _has(_get(data.cognitive_policy, "decisions"), "DENY", "LOCKDOWN")
        or _risks_contain(data.cognitive_policy, "SAFETY_CRITICAL", "EXECUTION_ROUTING_UNSAFE", "POLICY_CONFLICT")
    ):
        risks.append(ExecutiveControlRisk.POLICY_BLOCK_REQUIRED)

    if (
        _has(_get(data.cognitive_alignment, "state"), "MISALIGNMENT", "LOCKED")
        or _score(data.cognitive_alignment, "cognitive_alignment_score", default=80) < 55
        or _risks_contain(data.cognitive_alignment, "BREAK", "COLLAPSE")
    ):
        risks.append(ExecutiveControlRisk.ALIGNMENT_FAILURE)

    if (
        _has(_get(data.cognitive_coherence, "state"), "INCOHERENCE", "CONFLICT", "LOCKED")
        or _score(data.cognitive_coherence, "cognitive_coherence_score", default=80) < 55
        or _has(_get(data.self_reflection_audit, "state"), "CONTRADICTORY", "CRITICAL")
    ):
        risks.append(ExecutiveControlRisk.COHERENCE_FAILURE)

    if (
        _has(_get(data.cognitive_consensus, "state"), "FRAGMENTED", "CONFLICT", "LOCKED")
        or _score(data.cognitive_consensus, "cognitive_consensus_score", default=80) < 55
        or _risks_contain(data.cognitive_consensus, "COLLAPSE", "DEADLOCK")
    ):
        risks.append(ExecutiveControlRisk.CONSENSUS_FAILURE)

    if (
        _has(_get(data.cognitive_memory_consolidation, "state"), "DEGRADED", "CONFLICTED", "LOCKED", "AT_RISK")
        or _score(data.cognitive_memory_consolidation, "memory_consolidation_score", default=80) < 55
        or _risks_contain(data.cognitive_memory_consolidation, "CORRUPTION", "CONTINUITY_MEMORY_BREAK")
    ):
        risks.append(ExecutiveControlRisk.MEMORY_FAILURE)

    if (
        _has(_get(data.intent_integrity, "state"), "CONFLICT", "CORRUPTED", "LOCKED", "AT_RISK")
        or _score(data.intent_integrity, "intent_integrity_score", default=80) < 55
        or _risks_contain(data.intent_integrity, "COLLAPSE", "CORRUPTION", "MISMATCH")
    ):
        risks.append(ExecutiveControlRisk.INTENT_FAILURE)

    if (
        _has(_get(data.cognitive_recovery, "state"), "RECOVERING", "PARTIAL", "DEGRADED", "FAILED", "SAFE")
        or _has(_get(data.cognitive_resilience, "state"), "RECOVERING", "FRAGILE", "CRITICAL", "SURVIVAL")
        or _has(_get(data.mission_continuity, "mode"), "RECOVERY", "SURVIVAL", "SAFE_PAUSE")
    ):
        risks.append(ExecutiveControlRisk.RECOVERY_INCOMPLETE)

    critical_flags = sum(
        1
        for condition in (
            _has(_get(data.system_integrity, "status"), "COMPROMISED", "PROTECTION", "ROLLBACK"),
            _has(_get(data.cognitive_stability, "state"), "CRITICAL", "COLLAPSING"),
            _has(_get(data.cognitive_consensus, "state"), "LOCKED", "SYSTEMIC"),
            _has(_get(data.cognitive_memory_consolidation, "state"), "LOCKED"),
            _has(_get(data.cognitive_governance, "mode"), "LOCKED", "EMERGENCY"),
            _has(_get(data.cognitive_policy, "mode"), "LOCKED"),
            _has(_get(data.intent_integrity, "state"), "LOCKED", "CORRUPTED"),
        )
        if condition
    )
    if len(set(risks)) >= 7 or critical_flags >= 3:
        risks.append(ExecutiveControlRisk.SYSTEMIC_CONTROL_COLLAPSE)

    return _dedupe(risks)


def compute_executive_control_score(
    data: CognitiveExecutiveControlInput,
    risks: tuple[ExecutiveControlRisk, ...] = (),
) -> ExecutiveControlScore:
    """Compute deterministic 0..100 executive control scores."""

    autonomy = _average(
        (
            _score(data.cognitive_governance, "governance_score", default=80),
            65 if _has(_get(data.cognitive_governance, "autonomy_level"), "FULL") else 85,
        )
    )
    policy = _score(data.cognitive_policy, "cognitive_policy_score", default=80)
    alignment = _average(
        (
            _score(data.cognitive_alignment, "cognitive_alignment_score", default=80),
            _score(data.cognitive_identity, "cognitive_identity_score", "identity_score", default=80),
        )
    )
    coherence = _average(
        (
            _score(data.cognitive_coherence, "cognitive_coherence_score", default=80),
            _score(data.self_reflection_audit, "reflection_quality_score", default=80),
            _score(data.recursive_world_model, "world_model_coherence_score", default=80),
        )
    )
    consensus = _score(data.cognitive_consensus, "cognitive_consensus_score", default=80)
    memory = _score(data.cognitive_memory_consolidation, "memory_consolidation_score", default=80)
    intent = _score(data.intent_integrity, "intent_integrity_score", default=80)
    recovery = _average(
        (
            _score(data.cognitive_recovery, "cognitive_recovery_score", default=80),
            _score(data.cognitive_resilience, "cognitive_resilience_score", default=80),
            _score(data.cognitive_continuity, "cognitive_continuity_score", "continuity_score", default=80),
        )
    )
    systemic = _average(
        (
            _score(data.system_integrity, "integrity_score", default=80),
            _score(data.mission_continuity, "continuity_score", default=80),
            _score(data.global_orchestrator, "orchestration_confidence", "confidence_score", default=80),
            _score(data.cognitive_stability, "cognitive_stability_score", default=80),
        )
    )
    values = {
        "autonomy": autonomy,
        "policy": policy,
        "alignment": alignment,
        "coherence": coherence,
        "consensus": consensus,
        "memory": memory,
        "intent": intent,
        "recovery": recovery,
        "systemic": systemic,
    }
    penalties = {
        ExecutiveControlRisk.AUTONOMY_TOO_HIGH: ("autonomy", 30),
        ExecutiveControlRisk.POLICY_BLOCK_REQUIRED: ("policy", 35),
        ExecutiveControlRisk.ALIGNMENT_FAILURE: ("alignment", 32),
        ExecutiveControlRisk.COHERENCE_FAILURE: ("coherence", 32),
        ExecutiveControlRisk.CONSENSUS_FAILURE: ("consensus", 32),
        ExecutiveControlRisk.MEMORY_FAILURE: ("memory", 32),
        ExecutiveControlRisk.INTENT_FAILURE: ("intent", 36),
        ExecutiveControlRisk.RECOVERY_INCOMPLETE: ("recovery", 24),
        ExecutiveControlRisk.EXECUTIVE_OVERRIDE_REQUIRED: ("systemic", 28),
    }
    for risk in risks:
        if risk in penalties:
            key, penalty = penalties[risk]
            values[key] = _clamp(values[key] - penalty)
    if ExecutiveControlRisk.SYSTEMIC_CONTROL_COLLAPSE in risks:
        values["systemic"] = _clamp(values["systemic"] - 38)

    systemic_control = _average(values.values())
    return ExecutiveControlScore(
        autonomy_control_score=values["autonomy"],
        policy_control_score=values["policy"],
        alignment_control_score=values["alignment"],
        coherence_control_score=values["coherence"],
        consensus_control_score=values["consensus"],
        memory_control_score=values["memory"],
        intent_control_score=values["intent"],
        recovery_control_score=values["recovery"],
        systemic_control_score=systemic_control,
    )


def build_executive_directives(
    risks: tuple[ExecutiveControlRisk, ...],
    score: ExecutiveControlScore,
) -> tuple[ExecutiveControlDirective, ...]:
    """Build explainable executive directives from detected risks."""

    directives: list[ExecutiveControlDirective] = []
    if not risks and score.systemic_control_score >= 75:
        directives.append(
            ExecutiveControlDirective(
                directive_id="allow_continue",
                action=ExecutiveControlAction.ALLOW_CONTINUE,
                priority=20,
                reason="All key cognitive control scores are stable.",
            )
        )
    else:
        directives.append(
            ExecutiveControlDirective(
                directive_id="allow_with_limits",
                action=ExecutiveControlAction.ALLOW_WITH_LIMITS,
                priority=35,
                reason="Control remains possible only with explicit limits.",
            )
        )
    if ExecutiveControlRisk.AUTONOMY_TOO_HIGH in risks or any(
        risk in risks
        for risk in (
            ExecutiveControlRisk.ALIGNMENT_FAILURE,
            ExecutiveControlRisk.COHERENCE_FAILURE,
            ExecutiveControlRisk.CONSENSUS_FAILURE,
        )
    ):
        directives.append(
            ExecutiveControlDirective(
                directive_id="reduce_autonomy",
                action=ExecutiveControlAction.REDUCE_AUTONOMY,
                priority=70,
                reason="Autonomy must be reduced until cognitive control stabilizes.",
                requires_supervision=True,
            )
        )
    if ExecutiveControlRisk.POLICY_BLOCK_REQUIRED in risks or ExecutiveControlRisk.INTENT_FAILURE in risks:
        directives.append(
            ExecutiveControlDirective(
                directive_id="block_action",
                action=ExecutiveControlAction.BLOCK_ACTION,
                priority=90,
                reason="Policy or intent integrity requires blocking the requested action.",
                requires_supervision=True,
                blocks_execution=True,
            )
        )
    if any(
        risk in risks
        for risk in (
            ExecutiveControlRisk.RECOVERY_INCOMPLETE,
            ExecutiveControlRisk.MEMORY_FAILURE,
            ExecutiveControlRisk.EXECUTIVE_OVERRIDE_REQUIRED,
        )
    ):
        directives.append(
            ExecutiveControlDirective(
                directive_id="require_supervision",
                action=ExecutiveControlAction.REQUIRE_SUPERVISION,
                priority=75,
                reason="Recovery, memory or system integrity requires supervision.",
                requires_supervision=True,
            )
        )
    if len(risks) >= 4 or ExecutiveControlRisk.EXECUTIVE_OVERRIDE_REQUIRED in risks:
        directives.append(
            ExecutiveControlDirective(
                directive_id="enter_safe_mode",
                action=ExecutiveControlAction.ENTER_SAFE_MODE,
                priority=85,
                reason="Multiple control risks require safe mode.",
                requires_supervision=True,
                blocks_execution=True,
            )
        )
        directives.append(
            ExecutiveControlDirective(
                directive_id="freeze_recursive_updates",
                action=ExecutiveControlAction.FREEZE_RECURSIVE_UPDATES,
                priority=80,
                reason="Recursive updates remain frozen while executive control is degraded.",
            )
        )
        directives.append(
            ExecutiveControlDirective(
                directive_id="freeze_learning",
                action=ExecutiveControlAction.FREEZE_LEARNING,
                priority=80,
                reason="Learning updates remain frozen under safe executive control.",
            )
        )
    if ExecutiveControlRisk.SYSTEMIC_CONTROL_COLLAPSE in risks:
        directives.append(
            ExecutiveControlDirective(
                directive_id="lock_executive_control",
                action=ExecutiveControlAction.LOCK_EXECUTIVE_CONTROL,
                priority=100,
                reason="Systemic control collapse requires executive lock.",
                requires_supervision=True,
                blocks_execution=True,
            )
        )
        directives.append(
            ExecutiveControlDirective(
                directive_id="escalate_to_human",
                action=ExecutiveControlAction.ESCALATE_TO_HUMAN,
                priority=100,
                reason="Human validation is required before any further action.",
                requires_supervision=True,
                blocks_execution=True,
            )
        )
    return tuple(sorted(_dedupe(directives), key=lambda directive: directive.priority, reverse=True))


def build_executive_decision_graph(
    directives: tuple[ExecutiveControlDirective, ...],
    risks: tuple[ExecutiveControlRisk, ...],
) -> ExecutiveControlDecisionGraph:
    """Build an explainable executive control decision graph."""

    nodes = (
        "autonomy",
        "policy",
        "alignment",
        "coherence",
        "consensus",
        "memory",
        "intent",
        "recovery",
        "systemic_control",
    )
    edges = (
        ("alignment", "autonomy", "limits"),
        ("coherence", "consensus", "validates"),
        ("policy", "intent", "enforces"),
        ("memory", "systemic_control", "stabilizes"),
        ("recovery", "systemic_control", "gates"),
        ("systemic_control", "autonomy", "authorizes"),
    )
    blocked_nodes: list[str] = []
    if ExecutiveControlRisk.POLICY_BLOCK_REQUIRED in risks:
        blocked_nodes.append("policy")
    if ExecutiveControlRisk.INTENT_FAILURE in risks:
        blocked_nodes.append("intent")
    if ExecutiveControlRisk.MEMORY_FAILURE in risks:
        blocked_nodes.append("memory")
    if ExecutiveControlRisk.CONSENSUS_FAILURE in risks:
        blocked_nodes.append("consensus")
    locked = ExecutiveControlRisk.SYSTEMIC_CONTROL_COLLAPSE in risks
    safe_mode_required = locked or any(
        directive.action == ExecutiveControlAction.ENTER_SAFE_MODE for directive in directives
    )
    return ExecutiveControlDecisionGraph(
        nodes=nodes,
        edges=edges,
        active_directives=directives,
        blocked_nodes=tuple(blocked_nodes),
        safe_mode_required=safe_mode_required,
        locked=locked,
    )


def generate_executive_control_recommendations(
    risks: tuple[ExecutiveControlRisk, ...],
) -> tuple[ExecutiveControlRecommendation, ...]:
    recommendations: list[ExecutiveControlRecommendation] = [ExecutiveControlRecommendation.CONTINUE_MONITORING]
    if ExecutiveControlRisk.POLICY_BLOCK_REQUIRED in risks:
        recommendations.append(ExecutiveControlRecommendation.ENFORCE_POLICY_BLOCKS)
    if ExecutiveControlRisk.ALIGNMENT_FAILURE in risks:
        recommendations.append(ExecutiveControlRecommendation.RECHECK_ALIGNMENT)
    if ExecutiveControlRisk.COHERENCE_FAILURE in risks:
        recommendations.append(ExecutiveControlRecommendation.RECHECK_COHERENCE)
    if ExecutiveControlRisk.CONSENSUS_FAILURE in risks:
        recommendations.append(ExecutiveControlRecommendation.REBUILD_CONSENSUS)
    if ExecutiveControlRisk.MEMORY_FAILURE in risks:
        recommendations.append(ExecutiveControlRecommendation.PROTECT_MEMORY)
    if ExecutiveControlRisk.INTENT_FAILURE in risks:
        recommendations.append(ExecutiveControlRecommendation.RESTORE_INTENT_INTEGRITY)
    if ExecutiveControlRisk.RECOVERY_INCOMPLETE in risks:
        recommendations.append(ExecutiveControlRecommendation.KEEP_RECOVERY_ACTIVE)
    if any(
        risk in risks
        for risk in (
            ExecutiveControlRisk.EXECUTIVE_OVERRIDE_REQUIRED,
            ExecutiveControlRisk.AUTONOMY_TOO_HIGH,
            ExecutiveControlRisk.SYSTEMIC_CONTROL_COLLAPSE,
        )
    ):
        recommendations.append(ExecutiveControlRecommendation.REQUIRE_MANUAL_VALIDATION)
    if ExecutiveControlRisk.SYSTEMIC_CONTROL_COLLAPSE in risks:
        recommendations.append(ExecutiveControlRecommendation.MAINTAIN_EXECUTIVE_LOCK)
    return _dedupe(recommendations)


def _state_mode(
    score: int,
    risks: tuple[ExecutiveControlRisk, ...],
) -> tuple[ExecutiveControlState, ExecutiveControlMode]:
    if ExecutiveControlRisk.SYSTEMIC_CONTROL_COLLAPSE in risks:
        return ExecutiveControlState.EXECUTIVE_CONTROL_LOCKED, ExecutiveControlMode.LOCKED_CONTROL
    if len(risks) >= 6 or score < 30:
        return ExecutiveControlState.EXECUTIVE_CONTROL_CRITICAL, ExecutiveControlMode.EMERGENCY_CONTROL
    if ExecutiveControlRisk.RECOVERY_INCOMPLETE in risks and len(risks) <= 3:
        return ExecutiveControlState.EXECUTIVE_CONTROL_RECOVERING, ExecutiveControlMode.RECOVERY_CONTROL
    if len(risks) >= 4 or score < 45:
        return ExecutiveControlState.EXECUTIVE_CONTROL_DEGRADED, ExecutiveControlMode.SAFE_CONTROL_MODE
    if any(
        risk in risks
        for risk in (
            ExecutiveControlRisk.POLICY_BLOCK_REQUIRED,
            ExecutiveControlRisk.INTENT_FAILURE,
            ExecutiveControlRisk.EXECUTIVE_OVERRIDE_REQUIRED,
        )
    ):
        return ExecutiveControlState.EXECUTIVE_CONTROL_RESTRICTED, ExecutiveControlMode.SUPERVISED_CONTROL
    if risks or score < 75:
        return ExecutiveControlState.EXECUTIVE_CONTROL_WATCH, ExecutiveControlMode.MONITORING_CONTROL
    return ExecutiveControlState.EXECUTIVE_CONTROL_STABLE, ExecutiveControlMode.NORMAL_EXECUTIVE_CONTROL


def evaluate_cognitive_executive_control(
    data: CognitiveExecutiveControlInput,
) -> CognitiveExecutiveControlResult:
    """Evaluate whether AGIcore can continue, restrict, block or lock control."""

    risks = detect_executive_control_risks(data)
    score_breakdown = compute_executive_control_score(data, risks)
    score = score_breakdown.systemic_control_score
    directives = build_executive_directives(risks, score_breakdown)
    graph = build_executive_decision_graph(directives, risks)
    state, mode = _state_mode(score, risks)
    actions = _dedupe(directive.action for directive in directives)
    recommendations = generate_executive_control_recommendations(risks)
    events = (
        ExecutiveControlEvent(
            name="COGNITIVE_EXECUTIVE_CONTROL_EVALUATED",
            detail=f"Executive control score {score} with {len(risks)} risk(s).",
            severity="WARNING" if risks else "INFO",
        ),
    )
    summary = (
        "Executive control locked due to systemic control collapse."
        if state == ExecutiveControlState.EXECUTIVE_CONTROL_LOCKED
        else "Executive control restricts or supervises the requested action."
        if risks
        else "Executive control allows continuation under offline constraints."
    )
    return CognitiveExecutiveControlResult(
        state=state,
        mode=mode,
        executive_control_score=score,
        score_breakdown=score_breakdown,
        directives=directives,
        decision_graph=graph,
        risks=risks,
        actions=actions,
        recommendations=recommendations,
        events=events,
        summary=summary,
    )


def render_cognitive_executive_control_markdown(result: CognitiveExecutiveControlResult) -> str:
    """Render the cognitive executive control report."""

    directives = "\n".join(
        f"- {directive.directive_id}: {directive.action.value} priority={directive.priority}, blocks={directive.blocks_execution} - {directive.reason}"
        for directive in result.directives
    ) or "- No directives."
    graph = "\n".join(
        (
            f"- Nodes: {', '.join(result.decision_graph.nodes)}",
            f"- Blocked nodes: {', '.join(result.decision_graph.blocked_nodes) or 'none'}",
            f"- Safe mode required: {result.decision_graph.safe_mode_required}",
            f"- Locked: {result.decision_graph.locked}",
        )
    )
    risks = "\n".join(f"- {risk.value}" for risk in result.risks) or "- No executive control risks."
    actions = "\n".join(f"- {action.value}" for action in result.actions) or "- No actions."
    recommendations = "\n".join(f"- {rec.value}" for rec in result.recommendations) or "- No recommendations."

    return "\n".join(
        (
            "# Cognitive Executive Control State",
            f"- State: {result.state.value}",
            f"- Mode: {result.mode.value}",
            "",
            "# Executive Control Score",
            f"- Score: {result.executive_control_score}/100",
            f"- Autonomy: {result.score_breakdown.autonomy_control_score}/100",
            f"- Policy: {result.score_breakdown.policy_control_score}/100",
            f"- Systemic: {result.score_breakdown.systemic_control_score}/100",
            "",
            "# Directives",
            directives,
            "",
            "# Decision Graph",
            graph,
            "",
            "# Risks",
            risks,
            "",
            "# Actions",
            actions,
            "",
            "# Recommendations",
            recommendations,
            "",
            "# AGIcore Executive Control Outlook",
            f"- Summary: {result.summary}",
            "- Offline only: no broker, no external API, no live execution.",
        )
    )
