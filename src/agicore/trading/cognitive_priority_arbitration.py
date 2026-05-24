"""Offline cognitive priority arbitration engine for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Optional

from agicore.trading.cognitive_priority_arbitration_models import (
    ArbitrationDecisionMatrix,
    CognitivePriority,
    CognitivePriorityArbitrationInput,
    CognitivePriorityArbitrationResult,
    PriorityArbitrationAction,
    PriorityArbitrationEvent,
    PriorityArbitrationMode,
    PriorityArbitrationRecommendation,
    PriorityArbitrationRisk,
    PriorityArbitrationScore,
    PriorityArbitrationState,
    PriorityConflict,
    PriorityHierarchy,
    PriorityResolution,
)


BASE_PRIORITY_ORDER = (
    "executive_control",
    "safety",
    "stability",
    "continuity",
    "mission",
    "capital_preservation",
    "recovery",
    "coherence",
    "alignment",
    "policy",
    "performance",
    "autonomy_expansion",
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


def _priority_score_map(data: CognitivePriorityArbitrationInput) -> dict[str, int]:
    return {
        "executive_control": _score(data.cognitive_executive_control, "executive_control_score", default=80),
        "safety": _average(
            (
                _score(data.system_integrity, "integrity_score", default=80),
                _score(data.cognitive_resilience, "cognitive_resilience_score", default=80),
                _score(data.cognitive_stability, "cognitive_stability_score", default=80),
            )
        ),
        "stability": _average(
            (
                _score(data.cognitive_stability, "cognitive_stability_score", default=80),
                _score(data.cognitive_coherence, "cognitive_coherence_score", default=80),
            )
        ),
        "continuity": _average(
            (
                _score(data.cognitive_continuity, "cognitive_continuity_score", "continuity_score", default=80),
                _score(data.mission_continuity, "continuity_score", default=80),
            )
        ),
        "mission": _average(
            (
                _score(data.mission_continuity, "continuity_score", default=80),
                _score(data.intent_integrity, "intent_integrity_score", default=80),
            )
        ),
        "capital_preservation": _average(
            (
                _score(data.cognitive_policy, "cognitive_policy_score", default=80),
                _score(data.system_integrity, "integrity_score", default=80),
            )
        ),
        "recovery": _average(
            (
                _score(data.cognitive_recovery, "cognitive_recovery_score", default=80),
                _score(data.cognitive_resilience, "cognitive_resilience_score", default=80),
            )
        ),
        "coherence": _score(data.cognitive_coherence, "cognitive_coherence_score", default=80),
        "alignment": _average(
            (
                _score(data.cognitive_alignment, "cognitive_alignment_score", default=80),
                _score(data.cognitive_identity, "cognitive_identity_score", "identity_score", default=80),
            )
        ),
        "policy": _average(
            (
                _score(data.cognitive_policy, "cognitive_policy_score", default=80),
                _score(data.cognitive_governance, "governance_score", default=80),
            )
        ),
        "performance": 60,
        "autonomy_expansion": 50 if _has(_get(data.cognitive_governance, "autonomy_level"), "FULL") else 35,
    }


def compute_priority_arbitration_score(
    data: CognitivePriorityArbitrationInput,
    risks: tuple[PriorityArbitrationRisk, ...] = (),
) -> PriorityArbitrationScore:
    """Compute deterministic 0..100 priority arbitration scores."""

    scores = _priority_score_map(data)
    penalties = {
        PriorityArbitrationRisk.SAFETY_PRIORITY_LOSS: ("safety", 35),
        PriorityArbitrationRisk.CAPITAL_PROTECTION_FAILURE: ("capital_preservation", 32),
        PriorityArbitrationRisk.EXECUTIVE_PRIORITY_CONFLICT: ("executive_control", 30),
        PriorityArbitrationRisk.POLICY_ALIGNMENT_CONFLICT: ("policy", 28),
        PriorityArbitrationRisk.RECOVERY_PRIORITY_SUPPRESSION: ("recovery", 25),
        PriorityArbitrationRisk.COHERENCE_PRIORITY_DRIFT: ("coherence", 25),
        PriorityArbitrationRisk.CONSENSUS_PRIORITY_FAILURE: ("stability", 25),
        PriorityArbitrationRisk.PRIORITY_COLLISION: ("stability", 18),
        PriorityArbitrationRisk.UNRESOLVED_PRIORITY_DEADLOCK: ("executive_control", 35),
    }
    for risk in risks:
        if risk in penalties:
            key, penalty = penalties[risk]
            scores[key] = _clamp(scores[key] - penalty)
    overall = _average(
        (
            scores["safety"],
            scores["stability"],
            scores["continuity"],
            scores["mission"],
            scores["capital_preservation"],
            scores["recovery"],
            scores["coherence"],
            scores["alignment"],
            scores["policy"],
            scores["executive_control"],
        )
    )
    if PriorityArbitrationRisk.SYSTEMIC_PRIORITY_COLLAPSE in risks:
        overall = _clamp(overall - 40)
    return PriorityArbitrationScore(
        safety_priority_score=scores["safety"],
        stability_priority_score=scores["stability"],
        continuity_priority_score=scores["continuity"],
        mission_priority_score=scores["mission"],
        capital_preservation_score=scores["capital_preservation"],
        recovery_priority_score=scores["recovery"],
        coherence_priority_score=scores["coherence"],
        alignment_priority_score=scores["alignment"],
        policy_priority_score=scores["policy"],
        executive_control_score=scores["executive_control"],
        overall_priority_score=overall,
    )


def build_priority_hierarchy(
    data: CognitivePriorityArbitrationInput,
    score: Optional[PriorityArbitrationScore] = None,
) -> PriorityHierarchy:
    """Build the explicable priority hierarchy."""

    score = score or compute_priority_arbitration_score(data)
    score_map = {
        "executive_control": score.executive_control_score,
        "safety": score.safety_priority_score,
        "stability": score.stability_priority_score,
        "continuity": score.continuity_priority_score,
        "mission": score.mission_priority_score,
        "capital_preservation": score.capital_preservation_score,
        "recovery": score.recovery_priority_score,
        "coherence": score.coherence_priority_score,
        "alignment": score.alignment_priority_score,
        "policy": score.policy_priority_score,
        "performance": 60,
        "autonomy_expansion": 50 if _has(_get(data.cognitive_governance, "autonomy_level"), "FULL") else 35,
    }
    locked: set[str] = set()
    if _has(_get(data.cognitive_executive_control, "state"), "LOCKED", "CRITICAL"):
        locked.add("executive_control")
    if _has(_get(data.system_integrity, "status"), "COMPROMISED", "PROTECTION", "ROLLBACK"):
        locked.add("safety")
    if _has(_get(data.cognitive_memory_consolidation, "state"), "LOCKED", "AT_RISK"):
        locked.add("continuity")
    if _has(_get(data.cognitive_recovery, "state"), "RECOVERING", "PARTIAL", "DEGRADED"):
        locked.add("recovery")

    priorities = tuple(
        CognitivePriority(
            name=name,
            rank=index + 1,
            weight=100 - index * 6,
            score=score_map[name],
            locked=name in locked,
            reason=f"{name} rank {index + 1} by safety-first hierarchy.",
        )
        for index, name in enumerate(BASE_PRIORITY_ORDER)
    )
    return PriorityHierarchy(
        priorities=priorities,
        dominant_priority="executive_control" if "executive_control" in locked else "safety",
        locked_priorities=tuple(sorted(locked)),
        safety_dominant=True,
        capital_protection_dominant=True,
    )


def detect_priority_conflicts(
    data: CognitivePriorityArbitrationInput,
    hierarchy: Optional[PriorityHierarchy] = None,
) -> tuple[PriorityConflict, ...]:
    """Detect direct priority conflicts in the cognitive stack."""

    hierarchy = hierarchy or build_priority_hierarchy(data)
    conflicts: list[PriorityConflict] = []
    requested = data.requested_priority.lower().strip() or "performance"

    if requested in {"performance", "autonomy_expansion"} and (
        _has(_get(data.system_integrity, "status"), "DEGRADED", "UNSTABLE", "COMPROMISED", "PROTECTION")
        or _has(_get(data.cognitive_stability, "state"), "UNSTABLE", "CRITICAL", "COLLAPSING")
    ):
        conflicts.append(
            PriorityConflict(
                conflict_id="safety_vs_requested_priority",
                higher_priority="safety",
                lower_priority=requested,
                risk=PriorityArbitrationRisk.SAFETY_PRIORITY_LOSS,
                severity_score=92,
                reason="Safety must dominate performance or autonomy expansion under degraded conditions.",
            )
        )
    if requested in {"performance", "autonomy_expansion"} and (
        _has(_get(data.cognitive_policy, "mode"), "SAFE", "LOCKED", "RESTRICTED")
        or _has(_get(data.intent_integrity, "state"), "CONFLICT", "CORRUPTED", "LOCKED")
    ):
        conflicts.append(
            PriorityConflict(
                conflict_id="capital_vs_expansion",
                higher_priority="capital_preservation",
                lower_priority=requested,
                risk=PriorityArbitrationRisk.CAPITAL_PROTECTION_FAILURE,
                severity_score=86,
                reason="Capital preservation must dominate expansion while policy or intent is restricted.",
            )
        )
    if _has(_get(data.cognitive_executive_control, "state"), "RESTRICTED", "CRITICAL", "LOCKED") and requested not in {
        "executive_control",
        "safety",
    }:
        conflicts.append(
            PriorityConflict(
                conflict_id="executive_override",
                higher_priority="executive_control",
                lower_priority=requested,
                risk=PriorityArbitrationRisk.EXECUTIVE_PRIORITY_CONFLICT,
                severity_score=95,
                reason="Executive control overrides lower operational priorities.",
            )
        )
    if (
        _has(_get(data.cognitive_policy, "mode"), "SAFE", "LOCKED", "RESTRICTED")
        and _has(_get(data.cognitive_alignment, "state"), "MISALIGNMENT", "LOCKED")
    ):
        conflicts.append(
            PriorityConflict(
                conflict_id="policy_alignment_sync",
                higher_priority="policy_alignment",
                lower_priority="requested_action",
                risk=PriorityArbitrationRisk.POLICY_ALIGNMENT_CONFLICT,
                severity_score=82,
                reason="Policy and alignment are not synchronized.",
            )
        )
    if _has(_get(data.cognitive_recovery, "state"), "RECOVERING", "PARTIAL", "DEGRADED") and requested in {
        "performance",
        "autonomy_expansion",
    }:
        conflicts.append(
            PriorityConflict(
                conflict_id="recovery_vs_optimization",
                higher_priority="recovery",
                lower_priority=requested,
                risk=PriorityArbitrationRisk.RECOVERY_PRIORITY_SUPPRESSION,
                severity_score=78,
                reason="Recovery must dominate aggressive optimization.",
            )
        )
    if _has(_get(data.cognitive_coherence, "state"), "CONFLICT", "INCOHERENCE", "LOCKED") or _score(
        data.cognitive_coherence, "cognitive_coherence_score", default=80
    ) < 55:
        conflicts.append(
            PriorityConflict(
                conflict_id="coherence_priority_drift",
                higher_priority="coherence",
                lower_priority=requested,
                risk=PriorityArbitrationRisk.COHERENCE_PRIORITY_DRIFT,
                severity_score=74,
                reason="Coherence drift prevents lower-priority optimization.",
            )
        )
    if _has(_get(data.cognitive_consensus, "state"), "FRAGMENTED", "CONFLICT", "LOCKED") or _score(
        data.cognitive_consensus, "cognitive_consensus_score", default=80
    ) < 55:
        conflicts.append(
            PriorityConflict(
                conflict_id="consensus_priority_failure",
                higher_priority="consensus",
                lower_priority=requested,
                risk=PriorityArbitrationRisk.CONSENSUS_PRIORITY_FAILURE,
                severity_score=80,
                reason="Consensus is too weak to authorize requested priority.",
            )
        )
    if len(conflicts) >= 2:
        conflicts.append(
            PriorityConflict(
                conflict_id="priority_collision",
                higher_priority="safety",
                lower_priority=requested,
                risk=PriorityArbitrationRisk.PRIORITY_COLLISION,
                severity_score=70,
                reason="Multiple priority conflicts are active simultaneously.",
            )
        )
    if len(conflicts) >= 5 and not hierarchy.locked_priorities:
        conflicts.append(
            PriorityConflict(
                conflict_id="priority_deadlock",
                higher_priority="executive_control",
                lower_priority=requested,
                risk=PriorityArbitrationRisk.UNRESOLVED_PRIORITY_DEADLOCK,
                severity_score=90,
                reason="Priority conflicts require executive deadlock resolution.",
            )
        )
    return tuple(conflicts)


def detect_priority_arbitration_risks(
    data: CognitivePriorityArbitrationInput,
    conflicts: Optional[tuple[PriorityConflict, ...]] = None,
) -> tuple[PriorityArbitrationRisk, ...]:
    """Detect arbitration risks from conflicts and critical control states."""

    conflicts = conflicts or detect_priority_conflicts(data)
    risks = [conflict.risk for conflict in conflicts]
    critical_flags = sum(
        1
        for condition in (
            _has(_get(data.cognitive_executive_control, "state"), "LOCKED", "CRITICAL"),
            _has(_get(data.system_integrity, "status"), "COMPROMISED", "PROTECTION", "ROLLBACK"),
            _has(_get(data.cognitive_consensus, "state"), "LOCKED", "SYSTEMIC"),
            _has(_get(data.cognitive_memory_consolidation, "state"), "LOCKED"),
            _has(_get(data.cognitive_stability, "state"), "CRITICAL", "COLLAPSING"),
            _has(_get(data.intent_integrity, "state"), "LOCKED", "CORRUPTED"),
        )
        if condition
    )
    if len(set(risks)) >= 7 or critical_flags >= 3:
        risks.append(PriorityArbitrationRisk.SYSTEMIC_PRIORITY_COLLAPSE)
    return _dedupe(risks)


def resolve_priority_conflicts(
    conflicts: tuple[PriorityConflict, ...],
) -> tuple[PriorityResolution, ...]:
    """Resolve priority conflicts with deterministic safety-first rules."""

    resolutions: list[PriorityResolution] = []
    for conflict in conflicts:
        if conflict.risk == PriorityArbitrationRisk.SAFETY_PRIORITY_LOSS:
            action = PriorityArbitrationAction.PRESERVE_SAFETY_PRIORITY
        elif conflict.risk == PriorityArbitrationRisk.CAPITAL_PROTECTION_FAILURE:
            action = PriorityArbitrationAction.PRIORITIZE_CAPITAL_PROTECTION
        elif conflict.risk == PriorityArbitrationRisk.EXECUTIVE_PRIORITY_CONFLICT:
            action = PriorityArbitrationAction.ESCALATE_TO_EXECUTIVE_CONTROL
        elif conflict.risk == PriorityArbitrationRisk.RECOVERY_PRIORITY_SUPPRESSION:
            action = PriorityArbitrationAction.CONTINUE_WITH_CONSTRAINTS
        elif conflict.risk == PriorityArbitrationRisk.SYSTEMIC_PRIORITY_COLLAPSE:
            action = PriorityArbitrationAction.LOCK_PRIORITY_SYSTEM
        elif conflict.risk == PriorityArbitrationRisk.UNRESOLVED_PRIORITY_DEADLOCK:
            action = PriorityArbitrationAction.REQUIRE_HUMAN_SUPERVISION
        else:
            action = PriorityArbitrationAction.BLOCK_NON_CRITICAL_ACTIONS
        resolutions.append(
            PriorityResolution(
                conflict_id=conflict.conflict_id,
                winning_priority=conflict.higher_priority,
                action=action,
                reason=f"{conflict.higher_priority} dominates {conflict.lower_priority}: {conflict.reason}",
                resolved=conflict.risk != PriorityArbitrationRisk.UNRESOLVED_PRIORITY_DEADLOCK,
            )
        )
    return tuple(resolutions)


def build_arbitration_decision_matrix(
    hierarchy: PriorityHierarchy,
    conflicts: tuple[PriorityConflict, ...],
    resolutions: tuple[PriorityResolution, ...],
    risks: tuple[PriorityArbitrationRisk, ...],
) -> ArbitrationDecisionMatrix:
    """Build an explainable arbitration decision matrix."""

    locked = PriorityArbitrationRisk.SYSTEMIC_PRIORITY_COLLAPSE in risks
    safe_mode = locked or any(
        risk
        in risks
        for risk in (
            PriorityArbitrationRisk.SAFETY_PRIORITY_LOSS,
            PriorityArbitrationRisk.EXECUTIVE_PRIORITY_CONFLICT,
            PriorityArbitrationRisk.UNRESOLVED_PRIORITY_DEADLOCK,
        )
    )
    blocked = ["autonomy_expansion", "high_risk_operations"] if risks else ()
    if PriorityArbitrationRisk.POLICY_ALIGNMENT_CONFLICT in risks:
        blocked = tuple(blocked) + ("policy_bypass",)
    allowed = ("monitoring", "safe_analysis", "recovery_flow") if risks else (
        "monitoring",
        "safe_analysis",
        "constrained_operation",
    )
    return ArbitrationDecisionMatrix(
        hierarchy=hierarchy,
        conflicts=conflicts,
        resolutions=resolutions,
        allowed_actions=tuple(allowed),
        blocked_actions=tuple(blocked),
        safe_mode_required=safe_mode,
        executive_override_active=PriorityArbitrationRisk.EXECUTIVE_PRIORITY_CONFLICT in risks,
        locked=locked,
    )


def generate_priority_arbitration_recommendations(
    risks: tuple[PriorityArbitrationRisk, ...],
) -> tuple[PriorityArbitrationRecommendation, ...]:
    recommendations: list[PriorityArbitrationRecommendation] = [
        PriorityArbitrationRecommendation.CONTINUE_PRIORITY_MONITORING,
        PriorityArbitrationRecommendation.MAINTAIN_SAFETY_DOMINANCE,
    ]
    if PriorityArbitrationRisk.EXECUTIVE_PRIORITY_CONFLICT in risks:
        recommendations.append(PriorityArbitrationRecommendation.RECHECK_EXECUTIVE_CONTROL)
    if PriorityArbitrationRisk.PRIORITY_COLLISION in risks or PriorityArbitrationRisk.UNRESOLVED_PRIORITY_DEADLOCK in risks:
        recommendations.append(PriorityArbitrationRecommendation.REBUILD_PRIORITY_HIERARCHY)
    if PriorityArbitrationRisk.RECOVERY_PRIORITY_SUPPRESSION in risks:
        recommendations.append(PriorityArbitrationRecommendation.PRESERVE_RECOVERY_FLOW)
    if PriorityArbitrationRisk.POLICY_ALIGNMENT_CONFLICT in risks:
        recommendations.append(PriorityArbitrationRecommendation.ENFORCE_POLICY_ALIGNMENT)
    if PriorityArbitrationRisk.COHERENCE_PRIORITY_DRIFT in risks or PriorityArbitrationRisk.CONSENSUS_PRIORITY_FAILURE in risks:
        recommendations.append(PriorityArbitrationRecommendation.STABILIZE_COGNITIVE_STATE)
    if risks:
        recommendations.append(PriorityArbitrationRecommendation.REDUCE_OPERATIONAL_SCOPE)
    if any(
        risk in risks
        for risk in (
            PriorityArbitrationRisk.UNRESOLVED_PRIORITY_DEADLOCK,
            PriorityArbitrationRisk.SYSTEMIC_PRIORITY_COLLAPSE,
        )
    ):
        recommendations.append(PriorityArbitrationRecommendation.REQUIRE_MANUAL_VALIDATION)
    if PriorityArbitrationRisk.SYSTEMIC_PRIORITY_COLLAPSE in risks:
        recommendations.append(PriorityArbitrationRecommendation.MAINTAIN_SAFE_MODE)
    return _dedupe(recommendations)


def _actions_from_resolutions(
    resolutions: tuple[PriorityResolution, ...],
    risks: tuple[PriorityArbitrationRisk, ...],
) -> tuple[PriorityArbitrationAction, ...]:
    actions: list[PriorityArbitrationAction] = [
        PriorityArbitrationAction.PRESERVE_SAFETY_PRIORITY,
        PriorityArbitrationAction.CONTINUE_WITH_CONSTRAINTS,
    ]
    actions.extend(resolution.action for resolution in resolutions)
    if any(
        risk in risks
        for risk in (
            PriorityArbitrationRisk.SAFETY_PRIORITY_LOSS,
            PriorityArbitrationRisk.PRIORITY_COLLISION,
            PriorityArbitrationRisk.POLICY_ALIGNMENT_CONFLICT,
        )
    ):
        actions.append(PriorityArbitrationAction.BLOCK_NON_CRITICAL_ACTIONS)
        actions.append(PriorityArbitrationAction.REDUCE_AUTONOMY)
    if any(
        risk in risks
        for risk in (
            PriorityArbitrationRisk.EXECUTIVE_PRIORITY_CONFLICT,
            PriorityArbitrationRisk.UNRESOLVED_PRIORITY_DEADLOCK,
        )
    ):
        actions.append(PriorityArbitrationAction.REQUIRE_HUMAN_SUPERVISION)
    if len(risks) >= 4 or PriorityArbitrationRisk.SYSTEMIC_PRIORITY_COLLAPSE in risks:
        actions.append(PriorityArbitrationAction.ACTIVATE_SAFE_MODE)
        actions.append(PriorityArbitrationAction.FREEZE_HIGH_RISK_OPERATIONS)
    if PriorityArbitrationRisk.SYSTEMIC_PRIORITY_COLLAPSE in risks:
        actions.append(PriorityArbitrationAction.LOCK_PRIORITY_SYSTEM)
    return _dedupe(actions)


def _state_mode(
    score: int,
    risks: tuple[PriorityArbitrationRisk, ...],
) -> tuple[PriorityArbitrationState, PriorityArbitrationMode]:
    if PriorityArbitrationRisk.SYSTEMIC_PRIORITY_COLLAPSE in risks:
        return PriorityArbitrationState.PRIORITY_ARBITRATION_LOCKED, PriorityArbitrationMode.LOCKED_ARBITRATION_MODE
    if len(risks) >= 6 or score < 30:
        return PriorityArbitrationState.PRIORITY_ARBITRATION_CRITICAL, PriorityArbitrationMode.EMERGENCY_ARBITRATION
    if PriorityArbitrationRisk.EXECUTIVE_PRIORITY_CONFLICT in risks:
        return PriorityArbitrationState.PRIORITY_ARBITRATION_ESCALATED, PriorityArbitrationMode.EXECUTIVE_OVERRIDE_MODE
    if PriorityArbitrationRisk.RECOVERY_PRIORITY_SUPPRESSION in risks and len(risks) <= 3:
        return PriorityArbitrationState.PRIORITY_ARBITRATION_RECOVERING, PriorityArbitrationMode.RECOVERY_PRIORITY_MODE
    if len(risks) >= 4 or score < 45:
        return PriorityArbitrationState.PRIORITY_ARBITRATION_DEGRADED, PriorityArbitrationMode.SAFE_MODE_ARBITRATION
    if PriorityArbitrationRisk.CAPITAL_PROTECTION_FAILURE in risks:
        return PriorityArbitrationState.PRIORITY_ARBITRATION_CONFLICTED, PriorityArbitrationMode.CAPITAL_PRESERVATION_MODE
    if risks:
        return PriorityArbitrationState.PRIORITY_ARBITRATION_CONFLICTED, PriorityArbitrationMode.SAFETY_FIRST_ARBITRATION
    return PriorityArbitrationState.PRIORITY_ARBITRATION_STABLE, PriorityArbitrationMode.NORMAL_ARBITRATION


def evaluate_cognitive_priority_arbitration(
    data: CognitivePriorityArbitrationInput,
) -> CognitivePriorityArbitrationResult:
    """Evaluate cognitive priority conflicts and produce a safe hierarchy."""

    preliminary_score = compute_priority_arbitration_score(data)
    hierarchy = build_priority_hierarchy(data, preliminary_score)
    conflicts = detect_priority_conflicts(data, hierarchy)
    risks = detect_priority_arbitration_risks(data, conflicts)
    score_breakdown = compute_priority_arbitration_score(data, risks)
    hierarchy = build_priority_hierarchy(data, score_breakdown)
    conflicts = detect_priority_conflicts(data, hierarchy)
    risks = detect_priority_arbitration_risks(data, conflicts)
    resolutions = resolve_priority_conflicts(conflicts)
    matrix = build_arbitration_decision_matrix(hierarchy, conflicts, resolutions, risks)
    actions = _actions_from_resolutions(resolutions, risks)
    recommendations = generate_priority_arbitration_recommendations(risks)
    score = score_breakdown.overall_priority_score
    state, mode = _state_mode(score, risks)
    events = (
        PriorityArbitrationEvent(
            name="COGNITIVE_PRIORITY_ARBITRATION_EVALUATED",
            detail=f"Priority arbitration score {score} with {len(conflicts)} conflict(s).",
            severity="WARNING" if risks else "INFO",
        ),
    )
    summary = (
        "Priority system locked due to systemic collapse."
        if state == PriorityArbitrationState.PRIORITY_ARBITRATION_LOCKED
        else "Priority arbitration resolved conflicts using safety-first hierarchy."
        if risks
        else "Priority arbitration stable with safety and capital preservation dominant."
    )
    return CognitivePriorityArbitrationResult(
        state=state,
        mode=mode,
        priority_arbitration_score=score,
        score_breakdown=score_breakdown,
        hierarchy=hierarchy,
        conflicts=conflicts,
        resolutions=resolutions,
        decision_matrix=matrix,
        risks=risks,
        actions=actions,
        recommendations=recommendations,
        events=events,
        summary=summary,
    )


def render_cognitive_priority_arbitration_markdown(result: CognitivePriorityArbitrationResult) -> str:
    """Render the cognitive priority arbitration report."""

    hierarchy = "\n".join(
        f"- {priority.rank}. {priority.name}: score={priority.score}/100, locked={priority.locked}"
        for priority in result.hierarchy.priorities
    ) or "- No hierarchy."
    conflicts = "\n".join(
        f"- {conflict.conflict_id}: {conflict.higher_priority} > {conflict.lower_priority} ({conflict.risk.value})"
        for conflict in result.conflicts
    ) or "- No conflicts."
    resolutions = "\n".join(
        f"- {resolution.conflict_id}: {resolution.winning_priority} via {resolution.action.value}, resolved={resolution.resolved}"
        for resolution in result.resolutions
    ) or "- No resolutions."
    matrix = "\n".join(
        (
            f"- Safe mode required: {result.decision_matrix.safe_mode_required}",
            f"- Executive override active: {result.decision_matrix.executive_override_active}",
            f"- Locked: {result.decision_matrix.locked}",
            f"- Allowed actions: {', '.join(result.decision_matrix.allowed_actions)}",
            f"- Blocked actions: {', '.join(result.decision_matrix.blocked_actions) or 'none'}",
        )
    )
    risks = "\n".join(f"- {risk.value}" for risk in result.risks) or "- No priority arbitration risks."
    actions = "\n".join(f"- {action.value}" for action in result.actions) or "- No actions."
    recommendations = "\n".join(f"- {rec.value}" for rec in result.recommendations) or "- No recommendations."

    return "\n".join(
        (
            "# Cognitive Priority Arbitration State",
            f"- State: {result.state.value}",
            f"- Mode: {result.mode.value}",
            "",
            "# Arbitration Score",
            f"- Score: {result.priority_arbitration_score}/100",
            f"- Safety: {result.score_breakdown.safety_priority_score}/100",
            f"- Capital preservation: {result.score_breakdown.capital_preservation_score}/100",
            "",
            "# Priority Hierarchy",
            hierarchy,
            "",
            "# Priority Conflicts",
            conflicts,
            "",
            "# Priority Resolutions",
            resolutions,
            "",
            "# Decision Matrix",
            matrix,
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
            "# AGIcore Priority Arbitration Outlook",
            f"- Summary: {result.summary}",
            "- Offline only: no broker, no external API, no live execution.",
        )
    )
