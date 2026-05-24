"""Offline cognitive safety orchestrator for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Optional

from agicore.trading.cognitive_safety_orchestrator_models import (
    CognitiveSafetyOrchestratorInput,
    CognitiveSafetyOrchestratorResult,
    SafetyCascadeRisk,
    SafetyCoordinationGraph,
    SafetyDirective,
    SafetyOrchestratorAction,
    SafetyOrchestratorEvent,
    SafetyOrchestratorMode,
    SafetyOrchestratorRecommendation,
    SafetyOrchestratorRisk,
    SafetyOrchestratorScore,
    SafetyOrchestratorState,
    SafetyProtectionLayer,
    SafetyStabilizationPlan,
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


def _actions_contain(obj: Any, *needles: str) -> bool:
    return any(_has(action, *needles) for action in _as_tuple(_get(obj, "actions", ())))


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


def detect_safety_orchestrator_risks(
    data: CognitiveSafetyOrchestratorInput,
) -> tuple[SafetyOrchestratorRisk, ...]:
    """Detect global cognitive safety risks."""

    risks: list[SafetyOrchestratorRisk] = []
    if (
        _has(_get(data.cognitive_executive_control, "state"), "CRITICAL", "LOCKED")
        or _actions_contain(data.cognitive_executive_control, "LOCK", "ESCALATE", "BLOCK_ACTION")
        or _score(data.cognitive_executive_control, "executive_control_score", default=80) < 45
    ):
        risks.append(SafetyOrchestratorRisk.EXECUTIVE_CONTROL_FAILURE)
    if (
        _has(_get(data.cognitive_priority_arbitration, "state"), "CRITICAL", "LOCKED", "DEGRADED")
        or _score(data.cognitive_priority_arbitration, "priority_arbitration_score", default=80) < 45
    ):
        risks.append(SafetyOrchestratorRisk.PRIORITY_ARBITRATION_FAILURE)
    if (
        _has(_get(data.cognitive_alignment, "state"), "MISALIGNMENT", "LOCKED")
        or _has(_get(data.cognitive_identity, "state"), "CONFLICT", "AT_RISK", "LOCKED")
        or _score(data.cognitive_alignment, "cognitive_alignment_score", default=80) < 50
    ):
        risks.append(SafetyOrchestratorRisk.ALIGNMENT_BREAKDOWN)
    if (
        _has(_get(data.cognitive_coherence, "state"), "CONFLICT", "INCOHERENCE", "LOCKED")
        or _has(_get(data.cognitive_stability, "state"), "UNSTABLE", "CRITICAL", "COLLAPSING")
        or _score(data.cognitive_coherence, "cognitive_coherence_score", default=80) < 50
    ):
        risks.append(SafetyOrchestratorRisk.COHERENCE_COLLAPSE)
    if (
        _has(_get(data.cognitive_memory_consolidation, "state"), "LOCKED", "CONFLICTED", "AT_RISK")
        or _risks_contain(data.cognitive_memory_consolidation, "CORRUPTION", "MEMORY")
        or _score(data.cognitive_memory_consolidation, "memory_consolidation_score", default=80) < 50
    ):
        risks.append(SafetyOrchestratorRisk.MEMORY_CORRUPTION_SPREAD)
    if (
        _has(_get(data.cognitive_recovery, "state"), "FAILED", "DEGRADED", "PARTIAL")
        or _has(_get(data.cognitive_resilience, "state"), "CRITICAL", "FRAGILE", "SURVIVAL")
        or _score(data.cognitive_recovery, "cognitive_recovery_score", default=80) < 45
    ):
        risks.append(SafetyOrchestratorRisk.RECOVERY_FAILURE)
    if (
        _has(_get(data.cognitive_policy, "mode"), "LOCKED", "SAFE", "RESTRICTED")
        and _has(_get(data.cognitive_governance, "mode"), "LOCKED", "EMERGENCY", "DEGRADED", "SAFE")
    ) or _risks_contain(data.cognitive_policy, "GOVERNANCE", "POLICY_CONFLICT"):
        risks.append(SafetyOrchestratorRisk.POLICY_GOVERNANCE_DRIFT)
    if (
        data.requested_operation.lower() in {"execute", "route_execution", "expand_autonomy", "trade"}
        and (
            risks
            or _has(_get(data.intent_integrity, "state"), "CONFLICT", "CORRUPTED", "LOCKED")
            or _has(_get(data.mission_continuity, "mode"), "SAFE_PAUSE", "SURVIVAL", "ESSENTIAL")
        )
    ):
        risks.append(SafetyOrchestratorRisk.UNSAFE_AUTONOMOUS_ACTION)

    cascade_count = sum(
        1
        for condition in (
            _has(_get(data.system_integrity, "status"), "COMPROMISED", "PROTECTION", "ROLLBACK"),
            _has(_get(data.cognitive_consensus, "state"), "LOCKED", "SYSTEMIC", "CONFLICT"),
            _has(_get(data.intent_integrity, "state"), "CORRUPTED", "LOCKED"),
            _has(_get(data.recursive_world_model, "decision"), "SAFE_MODE", "REBUILD", "FREEZE"),
            len(risks) >= 4,
        )
        if condition
    )
    if cascade_count >= 2:
        risks.append(SafetyOrchestratorRisk.SYSTEMIC_CASCADE_RISK)
    if len(set(risks)) >= 7 or cascade_count >= 4:
        risks.append(SafetyOrchestratorRisk.GLOBAL_SAFETY_COLLAPSE)
    return _dedupe(risks)


def compute_safety_orchestrator_score(
    data: CognitiveSafetyOrchestratorInput,
    risks: tuple[SafetyOrchestratorRisk, ...] = (),
) -> SafetyOrchestratorScore:
    """Compute deterministic 0..100 safety orchestration scores."""

    values = {
        "executive": _score(data.cognitive_executive_control, "executive_control_score", default=80),
        "priority": _score(data.cognitive_priority_arbitration, "priority_arbitration_score", default=80),
        "policy": _average(
            (
                _score(data.cognitive_policy, "cognitive_policy_score", default=80),
                _score(data.cognitive_governance, "governance_score", default=80),
            )
        ),
        "recovery": _average(
            (
                _score(data.cognitive_recovery, "cognitive_recovery_score", default=80),
                _score(data.cognitive_resilience, "cognitive_resilience_score", default=80),
            )
        ),
        "coherence_alignment": _average(
            (
                _score(data.cognitive_coherence, "cognitive_coherence_score", default=80),
                _score(data.cognitive_alignment, "cognitive_alignment_score", default=80),
                _score(data.cognitive_stability, "cognitive_stability_score", default=80),
            )
        ),
        "consensus": _score(data.cognitive_consensus, "cognitive_consensus_score", default=80),
        "continuity": _average(
            (
                _score(data.cognitive_continuity, "cognitive_continuity_score", "continuity_score", default=80),
                _score(data.mission_continuity, "continuity_score", default=80),
            )
        ),
        "intent": _average(
            (
                _score(data.intent_integrity, "intent_integrity_score", default=80),
                _score(data.cognitive_identity, "cognitive_identity_score", "identity_score", default=80),
            )
        ),
        "memory": _score(data.cognitive_memory_consolidation, "memory_consolidation_score", default=80),
        "world_model": _score(data.recursive_world_model, "world_model_coherence_score", default=80),
    }
    penalties = {
        SafetyOrchestratorRisk.EXECUTIVE_CONTROL_FAILURE: ("executive", 35),
        SafetyOrchestratorRisk.PRIORITY_ARBITRATION_FAILURE: ("priority", 32),
        SafetyOrchestratorRisk.ALIGNMENT_BREAKDOWN: ("coherence_alignment", 30),
        SafetyOrchestratorRisk.COHERENCE_COLLAPSE: ("coherence_alignment", 32),
        SafetyOrchestratorRisk.MEMORY_CORRUPTION_SPREAD: ("memory", 35),
        SafetyOrchestratorRisk.RECOVERY_FAILURE: ("recovery", 30),
        SafetyOrchestratorRisk.POLICY_GOVERNANCE_DRIFT: ("policy", 28),
        SafetyOrchestratorRisk.UNSAFE_AUTONOMOUS_ACTION: ("executive", 25),
        SafetyOrchestratorRisk.SYSTEMIC_CASCADE_RISK: ("world_model", 25),
    }
    for risk in risks:
        if risk in penalties:
            key, penalty = penalties[risk]
            values[key] = _clamp(values[key] - penalty)
    overall = _average(values.values())
    if SafetyOrchestratorRisk.GLOBAL_SAFETY_COLLAPSE in risks:
        overall = _clamp(overall - 42)
    return SafetyOrchestratorScore(
        executive_safety_score=values["executive"],
        priority_safety_score=values["priority"],
        policy_governance_score=values["policy"],
        recovery_resilience_score=values["recovery"],
        coherence_alignment_score=values["coherence_alignment"],
        consensus_score=values["consensus"],
        continuity_score=values["continuity"],
        intent_safety_score=values["intent"],
        memory_safety_score=values["memory"],
        world_model_safety_score=values["world_model"],
        overall_safety_score=overall,
    )


def detect_cascade_risks(
    data: CognitiveSafetyOrchestratorInput,
    risks: tuple[SafetyOrchestratorRisk, ...],
) -> tuple[SafetyCascadeRisk, ...]:
    """Detect likely cross-layer safety cascades."""

    cascades: list[SafetyCascadeRisk] = []
    if SafetyOrchestratorRisk.MEMORY_CORRUPTION_SPREAD in risks:
        cascades.append(
            SafetyCascadeRisk(
                cascade_id="memory_to_continuity",
                source_layer="memory",
                target_layers=("continuity", "identity", "intent"),
                severity_score=85,
                contained=SafetyOrchestratorRisk.GLOBAL_SAFETY_COLLAPSE not in risks,
                reason="Memory corruption can spread to continuity and identity layers.",
            )
        )
    if SafetyOrchestratorRisk.COHERENCE_COLLAPSE in risks or SafetyOrchestratorRisk.ALIGNMENT_BREAKDOWN in risks:
        cascades.append(
            SafetyCascadeRisk(
                cascade_id="reasoning_to_decision",
                source_layer="coherence_alignment",
                target_layers=("consensus", "executive_control", "policy"),
                severity_score=80,
                contained=SafetyOrchestratorRisk.GLOBAL_SAFETY_COLLAPSE not in risks,
                reason="Reasoning or alignment failure can degrade executive decisions.",
            )
        )
    if SafetyOrchestratorRisk.EXECUTIVE_CONTROL_FAILURE in risks or SafetyOrchestratorRisk.PRIORITY_ARBITRATION_FAILURE in risks:
        cascades.append(
            SafetyCascadeRisk(
                cascade_id="control_to_autonomy",
                source_layer="executive_control",
                target_layers=("autonomy", "operation_routing", "safe_mode"),
                severity_score=90,
                contained=False if SafetyOrchestratorRisk.GLOBAL_SAFETY_COLLAPSE in risks else True,
                reason="Control or priority failure can permit unsafe autonomous routing.",
            )
        )
    if SafetyOrchestratorRisk.SYSTEMIC_CASCADE_RISK in risks:
        cascades.append(
            SafetyCascadeRisk(
                cascade_id="systemic_cascade",
                source_layer="system_integrity",
                target_layers=("all_cognitive_layers",),
                severity_score=95,
                contained=SafetyOrchestratorRisk.GLOBAL_SAFETY_COLLAPSE not in risks,
                reason="Multiple critical layers indicate systemic cascade risk.",
            )
        )
    return tuple(cascades)


def build_safety_directives(
    risks: tuple[SafetyOrchestratorRisk, ...],
    score: SafetyOrchestratorScore,
) -> tuple[SafetyDirective, ...]:
    """Build prioritized safety directives."""

    directives: list[SafetyDirective] = []
    if not risks and score.overall_safety_score >= 75:
        directives.append(
            SafetyDirective(
                directive_id="maintain_safety_coordination",
                action=SafetyOrchestratorAction.REDUCE_SYSTEM_SCOPE,
                priority=20,
                reason="Safety state is stable; continue monitoring with normal scope.",
            )
        )
    if risks:
        directives.append(
            SafetyDirective(
                directive_id="activate_global_safe_mode",
                action=SafetyOrchestratorAction.ACTIVATE_GLOBAL_SAFE_MODE,
                priority=85,
                reason="One or more cognitive safety risks are active.",
                blocks_autonomy=True,
            )
        )
        directives.append(
            SafetyDirective(
                directive_id="block_high_risk_decisions",
                action=SafetyOrchestratorAction.BLOCK_HIGH_RISK_DECISIONS,
                priority=80,
                reason="Autonomous high-risk decisions remain blocked until safety stabilizes.",
                blocks_autonomy=True,
            )
        )
    if SafetyOrchestratorRisk.MEMORY_CORRUPTION_SPREAD in risks:
        directives.append(
            SafetyDirective(
                directive_id="protect_memory_system",
                action=SafetyOrchestratorAction.PROTECT_MEMORY_SYSTEM,
                priority=88,
                reason="Memory integrity must be protected before further orchestration.",
            )
        )
    if SafetyOrchestratorRisk.RECOVERY_FAILURE in risks:
        directives.append(
            SafetyDirective(
                directive_id="maintain_recovery_pipeline",
                action=SafetyOrchestratorAction.MAINTAIN_RECOVERY_PIPELINE,
                priority=76,
                reason="Recovery and resilience pipeline must remain active.",
            )
        )
    if SafetyOrchestratorRisk.EXECUTIVE_CONTROL_FAILURE in risks:
        directives.append(
            SafetyDirective(
                directive_id="enforce_executive_lock",
                action=SafetyOrchestratorAction.ENFORCE_EXECUTIVE_LOCK,
                priority=92,
                reason="Executive safety requires lock or strict supervision.",
                blocks_autonomy=True,
                requires_supervision=True,
            )
        )
    if SafetyOrchestratorRisk.SYSTEMIC_CASCADE_RISK in risks:
        directives.append(
            SafetyDirective(
                directive_id="freeze_autonomous_operations",
                action=SafetyOrchestratorAction.FREEZE_AUTONOMOUS_OPERATIONS,
                priority=90,
                reason="Cascade prevention requires freezing autonomous operations.",
                blocks_autonomy=True,
                requires_supervision=True,
            )
        )
        directives.append(
            SafetyDirective(
                directive_id="isolate_unsafe_components",
                action=SafetyOrchestratorAction.ISOLATE_UNSAFE_COMPONENTS,
                priority=84,
                reason="Unsafe components must be isolated to prevent propagation.",
                requires_supervision=True,
            )
        )
    if SafetyOrchestratorRisk.UNSAFE_AUTONOMOUS_ACTION in risks:
        directives.append(
            SafetyDirective(
                directive_id="require_human_supervision",
                action=SafetyOrchestratorAction.REQUIRE_HUMAN_SUPERVISION,
                priority=86,
                reason="Requested autonomous action is unsafe under current safety state.",
                blocks_autonomy=True,
                requires_supervision=True,
            )
        )
    if SafetyOrchestratorRisk.GLOBAL_SAFETY_COLLAPSE in risks:
        directives.append(
            SafetyDirective(
                directive_id="lockdown_system",
                action=SafetyOrchestratorAction.LOCKDOWN_SYSTEM,
                priority=100,
                reason="Global safety collapse requires full safety lockdown.",
                blocks_autonomy=True,
                requires_supervision=True,
            )
        )
    return tuple(sorted(_dedupe(directives), key=lambda directive: directive.priority, reverse=True))


def build_safety_coordination_graph(
    data: CognitiveSafetyOrchestratorInput,
    directives: tuple[SafetyDirective, ...],
    risks: tuple[SafetyOrchestratorRisk, ...],
) -> SafetyCoordinationGraph:
    """Build the safety coordination graph."""

    layers = (
        SafetyProtectionLayer("executive_control", data.cognitive_executive_control is not None, _score(data.cognitive_executive_control, "executive_control_score"), ("autonomy", "routing"), "Controls final authority."),
        SafetyProtectionLayer("priority_arbitration", data.cognitive_priority_arbitration is not None, _score(data.cognitive_priority_arbitration, "priority_arbitration_score"), ("safety", "capital"), "Orders cognitive priorities."),
        SafetyProtectionLayer("policy_governance", data.cognitive_policy is not None or data.cognitive_governance is not None, _average((_score(data.cognitive_policy, "cognitive_policy_score"), _score(data.cognitive_governance, "governance_score"))), ("permissions", "rules"), "Enforces constraints."),
        SafetyProtectionLayer("memory", data.cognitive_memory_consolidation is not None, _score(data.cognitive_memory_consolidation, "memory_consolidation_score"), ("memory", "identity"), "Protects consolidated memory."),
        SafetyProtectionLayer("recovery", data.cognitive_recovery is not None or data.cognitive_resilience is not None, _average((_score(data.cognitive_recovery, "cognitive_recovery_score"), _score(data.cognitive_resilience, "cognitive_resilience_score"))), ("recovery", "resilience"), "Coordinates recovery."),
        SafetyProtectionLayer("world_model", data.recursive_world_model is not None, _score(data.recursive_world_model, "world_model_coherence_score"), ("causal_graph", "planning"), "Checks model safety."),
    )
    routes = (
        ("executive_control", "priority_arbitration", "override"),
        ("priority_arbitration", "policy_governance", "enforce"),
        ("policy_governance", "world_model", "restrict"),
        ("memory", "continuity", "preserve"),
        ("recovery", "executive_control", "stabilize"),
        ("world_model", "executive_control", "safety_feedback"),
    )
    blocked = []
    if any(directive.blocks_autonomy for directive in directives):
        blocked.append("autonomous_operations")
    if SafetyOrchestratorRisk.POLICY_GOVERNANCE_DRIFT in risks:
        blocked.append("policy_bypass")
    isolated = []
    if SafetyOrchestratorRisk.MEMORY_CORRUPTION_SPREAD in risks:
        isolated.append("memory")
    if SafetyOrchestratorRisk.COHERENCE_COLLAPSE in risks:
        isolated.append("coherence")
    return SafetyCoordinationGraph(
        layers=layers,
        routes=routes,
        blocked_components=tuple(blocked),
        isolated_components=tuple(isolated),
        safe_mode_active=bool(risks),
        lockdown_active=SafetyOrchestratorRisk.GLOBAL_SAFETY_COLLAPSE in risks,
    )


def build_safety_stabilization_plan(
    directives: tuple[SafetyDirective, ...],
    cascade_risks: tuple[SafetyCascadeRisk, ...],
    risks: tuple[SafetyOrchestratorRisk, ...],
) -> SafetyStabilizationPlan:
    """Build ordered stabilization plan."""

    steps = ["Maintain offline-only safety coordination."]
    if risks:
        steps.append("Activate global safe mode and block high-risk autonomous operations.")
    if SafetyOrchestratorRisk.MEMORY_CORRUPTION_SPREAD in risks:
        steps.append("Protect memory system and preserve consolidated snapshots.")
    if SafetyOrchestratorRisk.RECOVERY_FAILURE in risks:
        steps.append("Keep recovery and resilience pipeline active.")
    if cascade_risks:
        steps.append("Contain cascade routes before any autonomous action.")
    if SafetyOrchestratorRisk.GLOBAL_SAFETY_COLLAPSE in risks:
        steps.append("Lock down system and require manual approval.")
    required_actions = tuple(_dedupe(directive.action for directive in directives))
    return SafetyStabilizationPlan(
        steps=tuple(steps),
        required_actions=required_actions,
        protected_memory=SafetyOrchestratorRisk.MEMORY_CORRUPTION_SPREAD in risks,
        recovery_pipeline_active=SafetyOrchestratorRisk.RECOVERY_FAILURE in risks,
        human_supervision_required=any(directive.requires_supervision for directive in directives),
        lockdown_required=SafetyOrchestratorRisk.GLOBAL_SAFETY_COLLAPSE in risks,
    )


def generate_safety_orchestrator_recommendations(
    risks: tuple[SafetyOrchestratorRisk, ...],
) -> tuple[SafetyOrchestratorRecommendation, ...]:
    recommendations: list[SafetyOrchestratorRecommendation] = [
        SafetyOrchestratorRecommendation.MAINTAIN_SAFETY_COORDINATION
    ]
    if SafetyOrchestratorRisk.EXECUTIVE_CONTROL_FAILURE in risks:
        recommendations.append(SafetyOrchestratorRecommendation.RECHECK_EXECUTIVE_CONTROL)
    if SafetyOrchestratorRisk.ALIGNMENT_BREAKDOWN in risks:
        recommendations.append(SafetyOrchestratorRecommendation.REBUILD_ALIGNMENT)
    if SafetyOrchestratorRisk.COHERENCE_COLLAPSE in risks or SafetyOrchestratorRisk.SYSTEMIC_CASCADE_RISK in risks:
        recommendations.append(SafetyOrchestratorRecommendation.STABILIZE_COGNITIVE_STATE)
    if SafetyOrchestratorRisk.POLICY_GOVERNANCE_DRIFT in risks:
        recommendations.append(SafetyOrchestratorRecommendation.ENFORCE_POLICY_CONSISTENCY)
    if SafetyOrchestratorRisk.MEMORY_CORRUPTION_SPREAD in risks:
        recommendations.append(SafetyOrchestratorRecommendation.PRESERVE_MEMORY_INTEGRITY)
    if SafetyOrchestratorRisk.RECOVERY_FAILURE in risks:
        recommendations.append(SafetyOrchestratorRecommendation.MAINTAIN_RECOVERY_OPERATIONS)
    if risks:
        recommendations.append(SafetyOrchestratorRecommendation.REDUCE_AUTONOMY_SCOPE)
    if SafetyOrchestratorRisk.UNSAFE_AUTONOMOUS_ACTION in risks or SafetyOrchestratorRisk.GLOBAL_SAFETY_COLLAPSE in risks:
        recommendations.append(SafetyOrchestratorRecommendation.REQUIRE_MANUAL_APPROVAL)
    if SafetyOrchestratorRisk.GLOBAL_SAFETY_COLLAPSE in risks:
        recommendations.append(SafetyOrchestratorRecommendation.KEEP_LOCKDOWN_ACTIVE)
    return _dedupe(recommendations)


def _actions_from_directives(directives: tuple[SafetyDirective, ...]) -> tuple[SafetyOrchestratorAction, ...]:
    return _dedupe(directive.action for directive in directives)


def _state_mode(
    score: int,
    risks: tuple[SafetyOrchestratorRisk, ...],
) -> tuple[SafetyOrchestratorState, SafetyOrchestratorMode]:
    if SafetyOrchestratorRisk.GLOBAL_SAFETY_COLLAPSE in risks:
        return SafetyOrchestratorState.SAFETY_ORCHESTRATOR_LOCKDOWN, SafetyOrchestratorMode.FULL_SAFETY_LOCK_MODE
    if len(risks) >= 6 or score < 30:
        return SafetyOrchestratorState.SAFETY_ORCHESTRATOR_CRITICAL, SafetyOrchestratorMode.EMERGENCY_LOCKDOWN_MODE
    if SafetyOrchestratorRisk.SYSTEMIC_CASCADE_RISK in risks:
        return SafetyOrchestratorState.SAFETY_ORCHESTRATOR_DEGRADED, SafetyOrchestratorMode.CASCADE_PREVENTION_MODE
    if SafetyOrchestratorRisk.EXECUTIVE_CONTROL_FAILURE in risks:
        return SafetyOrchestratorState.SAFETY_ORCHESTRATOR_PROTECTING, SafetyOrchestratorMode.EXECUTIVE_SAFETY_MODE
    if SafetyOrchestratorRisk.RECOVERY_FAILURE in risks:
        return SafetyOrchestratorState.SAFETY_ORCHESTRATOR_RECOVERING, SafetyOrchestratorMode.RECOVERY_PROTECTION_MODE
    if risks or score < 75:
        return SafetyOrchestratorState.SAFETY_ORCHESTRATOR_MONITORING, SafetyOrchestratorMode.PROTECTIVE_MODE
    return SafetyOrchestratorState.SAFETY_ORCHESTRATOR_STABLE, SafetyOrchestratorMode.NORMAL_SAFETY_MODE


def evaluate_cognitive_safety_orchestrator(
    data: CognitiveSafetyOrchestratorInput,
) -> CognitiveSafetyOrchestratorResult:
    """Coordinate cognitive safety before autonomous operation."""

    risks = detect_safety_orchestrator_risks(data)
    score_breakdown = compute_safety_orchestrator_score(data, risks)
    cascade_risks = detect_cascade_risks(data, risks)
    directives = build_safety_directives(risks, score_breakdown)
    graph = build_safety_coordination_graph(data, directives, risks)
    plan = build_safety_stabilization_plan(directives, cascade_risks, risks)
    actions = _actions_from_directives(directives)
    recommendations = generate_safety_orchestrator_recommendations(risks)
    score = score_breakdown.overall_safety_score
    state, mode = _state_mode(score, risks)
    events = (
        SafetyOrchestratorEvent(
            name="COGNITIVE_SAFETY_ORCHESTRATOR_EVALUATED",
            detail=f"Safety score {score} with {len(risks)} risk(s) and {len(cascade_risks)} cascade(s).",
            severity="WARNING" if risks else "INFO",
        ),
    )
    summary = (
        "Global safety lockdown active due to collapse risk."
        if state == SafetyOrchestratorState.SAFETY_ORCHESTRATOR_LOCKDOWN
        else "Safety orchestrator is protecting AGIcore before autonomous action."
        if risks
        else "Safety orchestrator stable; offline monitoring remains active."
    )
    return CognitiveSafetyOrchestratorResult(
        state=state,
        mode=mode,
        safety_orchestrator_score=score,
        score_breakdown=score_breakdown,
        directives=directives,
        coordination_graph=graph,
        cascade_risks=cascade_risks,
        stabilization_plan=plan,
        risks=risks,
        actions=actions,
        recommendations=recommendations,
        events=events,
        summary=summary,
    )


def render_cognitive_safety_orchestrator_markdown(result: CognitiveSafetyOrchestratorResult) -> str:
    """Render the safety orchestrator report."""

    directives = "\n".join(
        f"- {directive.directive_id}: {directive.action.value} priority={directive.priority}, blocks={directive.blocks_autonomy}"
        for directive in result.directives
    ) or "- No directives."
    graph = "\n".join(
        (
            f"- Layers: {', '.join(layer.name for layer in result.coordination_graph.layers)}",
            f"- Blocked components: {', '.join(result.coordination_graph.blocked_components) or 'none'}",
            f"- Isolated components: {', '.join(result.coordination_graph.isolated_components) or 'none'}",
            f"- Safe mode active: {result.coordination_graph.safe_mode_active}",
            f"- Lockdown active: {result.coordination_graph.lockdown_active}",
        )
    )
    cascades = "\n".join(
        f"- {cascade.cascade_id}: {cascade.source_layer} -> {', '.join(cascade.target_layers)} severity={cascade.severity_score}, contained={cascade.contained}"
        for cascade in result.cascade_risks
    ) or "- No cascade risks."
    plan = "\n".join(f"- {step}" for step in result.stabilization_plan.steps) or "- No stabilization steps."
    risks = "\n".join(f"- {risk.value}" for risk in result.risks) or "- No safety risks."
    actions = "\n".join(f"- {action.value}" for action in result.actions) or "- No actions."
    recommendations = "\n".join(f"- {rec.value}" for rec in result.recommendations) or "- No recommendations."
    return "\n".join(
        (
            "# Cognitive Safety Orchestrator State",
            f"- State: {result.state.value}",
            f"- Mode: {result.mode.value}",
            "",
            "# Safety Orchestrator Score",
            f"- Score: {result.safety_orchestrator_score}/100",
            f"- Executive safety: {result.score_breakdown.executive_safety_score}/100",
            f"- Memory safety: {result.score_breakdown.memory_safety_score}/100",
            "",
            "# Safety Directives",
            directives,
            "",
            "# Safety Coordination Graph",
            graph,
            "",
            "# Cascade Risks",
            cascades,
            "",
            "# Stabilization Plan",
            plan,
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
            "# AGIcore Safety Outlook",
            f"- Summary: {result.summary}",
            "- Offline only: no broker, no external API, no live execution.",
        )
    )
