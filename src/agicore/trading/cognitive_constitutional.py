"""Offline cognitive constitutional layer for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable

from agicore.trading.cognitive_constitutional_models import (
    CognitiveConstitutionalInput,
    CognitiveConstitutionalResult,
    ConstitutionalConstraint,
    ConstitutionalConstraints,
    ConstitutionalDirective,
    ConstitutionalEvent,
    ConstitutionalHierarchy,
    ConstitutionalMode,
    ConstitutionalRecommendation,
    ConstitutionalRisk,
    ConstitutionalRule,
    ConstitutionalScore,
    ConstitutionalState,
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
    values = []
    for directive in _as_tuple(_get(obj, "directives", ())):
        values.append(_get(directive, "action", directive))
    return _contains(tuple(values), *needles)


def _clamp(value: int | float, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(round(value))))


def _average(values: Iterable[int | float]) -> int:
    usable = [float(value) for value in values if value is not None]
    if not usable:
        return 90
    return _clamp(sum(usable) / len(usable))


def _score(obj: Any, *names: str, default: int = 90) -> int:
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


def detect_constitutional_risks(
    data: CognitiveConstitutionalInput,
) -> tuple[ConstitutionalRisk, ...]:
    """Detect constitutional violations and invariant breaks."""

    risks: list[ConstitutionalRisk] = []
    safety_locked = (
        _has(_get(data.cognitive_safety_orchestrator, "state"), "LOCKDOWN", "CRITICAL", "PROTECTING")
        or _has(_get(data.cognitive_safety_orchestrator, "mode"), "SAFE", "LOCK", "PROTECT")
        or _directives_contain(data.cognitive_safety_orchestrator, "BLOCK", "LOCKDOWN", "FREEZE")
    )
    wants_action = data.requested_operation.lower() in {
        "execute",
        "trade",
        "route_execution",
        "expand_autonomy",
        "override_safety",
    }
    if wants_action and safety_locked:
        risks.append(ConstitutionalRisk.SAFETY_OVERRIDE_ATTEMPT)
    if data.requested_operation.lower() == "override_safety" or data.requested_authority.upper() == "ACTIONS_OVERRIDE":
        risks.append(ConstitutionalRisk.CONSTITUTIONAL_VIOLATION)
    if (
        data.requested_operation.lower() == "expand_autonomy"
        and (
            safety_locked
            or _has(_get(data.cognitive_meta_supervision, "state"), "CRITICAL", "LOCKDOWN", "FRAGMENTED")
            or _score(data.cognitive_meta_supervision, "meta_supervision_score", default=90) < 55
        )
    ):
        risks.append(ConstitutionalRisk.UNSAFE_AUTONOMY_EXPANSION)
    if (
        _has(_get(data.cognitive_identity, "state"), "CORRUPT", "FRAGMENTED", "CONFLICT", "AT_RISK", "LOCKED")
        or _score(data.cognitive_identity, "cognitive_identity_score", "identity_score", default=90) < 55
    ):
        risks.append(ConstitutionalRisk.IDENTITY_CORRUPTION)
    if (
        _has(_get(data.intent_integrity, "state"), "DRIFT", "CONFLICT", "CORRUPTED", "LOCKED")
        or _has(_get(data.cognitive_alignment, "state"), "MISALIGNMENT", "DIVERGENCE")
        or _score(data.intent_integrity, "intent_integrity_score", default=90) < 55
    ):
        risks.append(ConstitutionalRisk.MISSION_DRIFT)
    if (
        _has(_get(data.cognitive_priority_arbitration, "state"), "CONFLICTED", "CRITICAL", "LOCKED")
        or _risks_contain(data.cognitive_priority_arbitration, "PRIORITY_COLLISION", "SAFETY_PRIORITY_LOSS")
        or _score(data.cognitive_priority_arbitration, "priority_arbitration_score", default=90) < 55
    ):
        risks.append(ConstitutionalRisk.RULE_HIERARCHY_BREAKDOWN)
    if (
        _has(_get(data.cognitive_executive_control, "state"), "CRITICAL", "LOCKED")
        or _actions_contain(data.cognitive_executive_control, "ESCALATE", "LOCK_EXECUTIVE_CONTROL")
        or (
            data.requested_authority.upper() == "EXECUTIVE"
            and _has(_get(data.cognitive_safety_orchestrator, "mode"), "SAFE", "LOCK")
        )
    ):
        risks.append(ConstitutionalRisk.EXECUTIVE_POWER_ESCALATION)
    if (
        _has(_get(data.cognitive_consensus, "state"), "CONFLICT", "FRAGMENTED", "SYSTEMIC", "LOCKED")
        or _score(data.cognitive_consensus, "cognitive_consensus_score", default=90) < 55
    ) and (
        risks
        or _has(_get(data.cognitive_alignment, "state"), "MISALIGNMENT")
    ):
        risks.append(ConstitutionalRisk.CONSENSUS_CONSTITUTION_CONFLICT)
    if (
        _has(_get(data.cognitive_recursive_regulation, "state"), "CRITICAL", "LOCKED", "THROTTLED")
        or _score(data.cognitive_recursive_regulation, "recursive_regulation_score", default=90) < 55
        or _risks_contain(data.cognitive_recursive_regulation, "UNBOUNDED", "RUNAWAY", "RECURSIVE")
    ):
        risks.append(ConstitutionalRisk.RECURSIVE_CONSTITUTIONAL_INSTABILITY)
    invariant_break_count = sum(
        1
        for risk in (
            ConstitutionalRisk.SAFETY_OVERRIDE_ATTEMPT,
            ConstitutionalRisk.IDENTITY_CORRUPTION,
            ConstitutionalRisk.MISSION_DRIFT,
            ConstitutionalRisk.RULE_HIERARCHY_BREAKDOWN,
            ConstitutionalRisk.RECURSIVE_CONSTITUTIONAL_INSTABILITY,
        )
        if risk in risks
    )
    if invariant_break_count >= 3 or len(set(risks)) >= 6:
        risks.append(ConstitutionalRisk.GLOBAL_SYSTEM_INVARIANT_BREAK)
    return _dedupe(risks)


def compute_constitutional_score(
    data: CognitiveConstitutionalInput,
    risks: tuple[ConstitutionalRisk, ...] = (),
) -> ConstitutionalScore:
    """Compute constitutional integrity scores."""

    scores = {
        "safety": _score(data.cognitive_safety_orchestrator, "safety_orchestrator_score", default=90),
        "autonomy": _average(
            (
                _score(data.cognitive_meta_supervision, "meta_supervision_score", default=90),
                _score(data.cognitive_governance, "governance_score", default=90),
                _score(data.cognitive_policy, "cognitive_policy_score", default=90),
            )
        ),
        "identity": _score(data.cognitive_identity, "cognitive_identity_score", "identity_score", default=90),
        "mission": _average(
            (
                _score(data.intent_integrity, "intent_integrity_score", default=90),
                _score(data.cognitive_alignment, "cognitive_alignment_score", default=90),
            )
        ),
        "hierarchy": _score(data.cognitive_priority_arbitration, "priority_arbitration_score", default=90),
        "executive": _score(data.cognitive_executive_control, "executive_control_score", default=90),
        "consensus": _score(data.cognitive_consensus, "cognitive_consensus_score", default=90),
        "recursive": _average(
            (
                _score(data.cognitive_recursive_regulation, "recursive_regulation_score", default=90),
                _score(data.recursive_world_model, "world_model_coherence_score", default=90),
            )
        ),
        "global": _average(
            (
                _score(data.cognitive_coherence, "cognitive_coherence_score", default=90),
                _score(data.self_reflection_audit, "reflection_quality_score", default=90),
            )
        ),
    }
    penalties = {
        ConstitutionalRisk.CONSTITUTIONAL_VIOLATION: ("global", 45),
        ConstitutionalRisk.SAFETY_OVERRIDE_ATTEMPT: ("safety", 40),
        ConstitutionalRisk.UNSAFE_AUTONOMY_EXPANSION: ("autonomy", 35),
        ConstitutionalRisk.IDENTITY_CORRUPTION: ("identity", 35),
        ConstitutionalRisk.MISSION_DRIFT: ("mission", 35),
        ConstitutionalRisk.RULE_HIERARCHY_BREAKDOWN: ("hierarchy", 35),
        ConstitutionalRisk.EXECUTIVE_POWER_ESCALATION: ("executive", 35),
        ConstitutionalRisk.CONSENSUS_CONSTITUTION_CONFLICT: ("consensus", 35),
        ConstitutionalRisk.RECURSIVE_CONSTITUTIONAL_INSTABILITY: ("recursive", 35),
        ConstitutionalRisk.GLOBAL_SYSTEM_INVARIANT_BREAK: ("global", 45),
    }
    for risk in risks:
        target, penalty = penalties[risk]
        scores[target] = _clamp(scores[target] - penalty)
    overall = _average(scores.values())
    if ConstitutionalRisk.CONSTITUTIONAL_VIOLATION in risks:
        overall = min(overall, 35)
    if ConstitutionalRisk.GLOBAL_SYSTEM_INVARIANT_BREAK in risks:
        overall = min(overall, 30)
    return ConstitutionalScore(
        safety_boundary_score=scores["safety"],
        autonomy_limit_score=scores["autonomy"],
        identity_invariant_score=scores["identity"],
        mission_invariant_score=scores["mission"],
        rule_hierarchy_score=scores["hierarchy"],
        executive_limit_score=scores["executive"],
        consensus_compatibility_score=scores["consensus"],
        recursive_stability_score=scores["recursive"],
        global_invariant_score=scores["global"],
        overall_score=overall,
    )


def build_constitutional_hierarchy(
    risks: tuple[ConstitutionalRisk, ...] = (),
) -> ConstitutionalHierarchy:
    """Build immutable rule hierarchy: Constitution > Safety > Executive > Consensus > Actions."""

    rules = (
        ConstitutionalRule("constitution_supremacy", 1, "CONSTITUTION", True, "Constitution overrides every subsystem."),
        ConstitutionalRule("offline_only", 2, "CONSTITUTION", True, "No live execution, broker connection or external API."),
        ConstitutionalRule("safety_boundary", 3, "SAFETY", True, "Safety dominates executive, consensus and actions."),
        ConstitutionalRule("capital_preservation", 4, "SAFETY", True, "Capital preservation and discipline are protected."),
        ConstitutionalRule("mission_identity", 5, "CONSTITUTION", True, "Mission and identity anchors cannot be bypassed."),
        ConstitutionalRule("executive_limited_power", 6, "EXECUTIVE", True, "Executive control cannot override constitution or safety."),
        ConstitutionalRule("consensus_subordinate", 7, "CONSENSUS", True, "Consensus is valid only if constitutional."),
        ConstitutionalRule("actions_last", 8, "ACTIONS", True, "Actions are always subordinate to all higher layers."),
    )
    return ConstitutionalHierarchy(
        rules=rules,
        constitution_supreme=True,
        safety_over_actions=ConstitutionalRisk.RULE_HIERARCHY_BREAKDOWN not in risks,
        veto_authority="CONSTITUTION",
    )


def build_constitutional_constraints(
    data: CognitiveConstitutionalInput,
    risks: tuple[ConstitutionalRisk, ...],
) -> ConstitutionalConstraints:
    """Build absolute constitutional constraints and protected invariants."""

    veto_active = any(
        risk
        in {
            ConstitutionalRisk.CONSTITUTIONAL_VIOLATION,
            ConstitutionalRisk.SAFETY_OVERRIDE_ATTEMPT,
            ConstitutionalRisk.GLOBAL_SYSTEM_INVARIANT_BREAK,
            ConstitutionalRisk.UNSAFE_AUTONOMY_EXPANSION,
        }
        for risk in risks
    )
    blocked = ["live_broker", "real_order", "external_api", "safety_bypass"]
    if veto_active:
        blocked.extend(["autonomous_action", data.requested_operation])
    if ConstitutionalRisk.UNSAFE_AUTONOMY_EXPANSION in risks:
        blocked.append("autonomy_expansion")
    constraints = (
        ConstitutionalConstraint("offline_only", True, True, "No broker, real order, API or live execution."),
        ConstitutionalConstraint("constitution_over_safety", True, False, "Constitution has supreme authority."),
        ConstitutionalConstraint("safety_over_actions", True, ConstitutionalRisk.SAFETY_OVERRIDE_ATTEMPT in risks, "Safety cannot be bypassed by actions."),
        ConstitutionalConstraint("identity_mission_preserved", True, ConstitutionalRisk.IDENTITY_CORRUPTION in risks or ConstitutionalRisk.MISSION_DRIFT in risks, "Identity and mission invariants are protected."),
        ConstitutionalConstraint("executive_power_limited", True, ConstitutionalRisk.EXECUTIVE_POWER_ESCALATION in risks, "Executive control remains subordinate."),
        ConstitutionalConstraint("consensus_must_be_constitutional", True, ConstitutionalRisk.CONSENSUS_CONSTITUTION_CONFLICT in risks, "Consensus cannot override constitutional law."),
    )
    return ConstitutionalConstraints(
        constraints=constraints,
        blocked_operations=_dedupe(blocked),
        protected_invariants=("mission", "identity", "safety", "capital_preservation", "discipline"),
        veto_active=veto_active,
        autonomy_expansion_allowed=not veto_active and data.requested_operation.lower() != "expand_autonomy",
    )


def generate_constitutional_directives(
    risks: tuple[ConstitutionalRisk, ...],
) -> tuple[ConstitutionalDirective, ...]:
    """Generate constitutional directives and veto controls."""

    directives: list[ConstitutionalDirective] = [ConstitutionalDirective.PRESERVE_CONSTITUTION]
    mapping = {
        ConstitutionalRisk.CONSTITUTIONAL_VIOLATION: ConstitutionalDirective.ACTIVATE_CONSTITUTIONAL_VETO,
        ConstitutionalRisk.SAFETY_OVERRIDE_ATTEMPT: ConstitutionalDirective.BLOCK_SAFETY_OVERRIDE,
        ConstitutionalRisk.UNSAFE_AUTONOMY_EXPANSION: ConstitutionalDirective.FREEZE_AUTONOMY_EXPANSION,
        ConstitutionalRisk.IDENTITY_CORRUPTION: ConstitutionalDirective.PROTECT_IDENTITY_INVARIANTS,
        ConstitutionalRisk.MISSION_DRIFT: ConstitutionalDirective.RESTORE_MISSION_ALIGNMENT,
        ConstitutionalRisk.RULE_HIERARCHY_BREAKDOWN: ConstitutionalDirective.REBUILD_RULE_HIERARCHY,
        ConstitutionalRisk.EXECUTIVE_POWER_ESCALATION: ConstitutionalDirective.LIMIT_EXECUTIVE_POWER,
        ConstitutionalRisk.CONSENSUS_CONSTITUTION_CONFLICT: ConstitutionalDirective.OVERRIDE_UNSAFE_CONSENSUS,
        ConstitutionalRisk.RECURSIVE_CONSTITUTIONAL_INSTABILITY: ConstitutionalDirective.REBUILD_RULE_HIERARCHY,
        ConstitutionalRisk.GLOBAL_SYSTEM_INVARIANT_BREAK: ConstitutionalDirective.LOCK_CONSTITUTIONAL_STATE,
    }
    for risk in risks:
        directives.append(mapping[risk])
    if any(
        risk
        in {
            ConstitutionalRisk.CONSTITUTIONAL_VIOLATION,
            ConstitutionalRisk.SAFETY_OVERRIDE_ATTEMPT,
            ConstitutionalRisk.GLOBAL_SYSTEM_INVARIANT_BREAK,
        }
        for risk in risks
    ):
        directives.append(ConstitutionalDirective.ACTIVATE_CONSTITUTIONAL_VETO)
    return _dedupe(directives)


def _generate_recommendations(
    risks: tuple[ConstitutionalRisk, ...],
) -> tuple[ConstitutionalRecommendation, ...]:
    recommendations: list[ConstitutionalRecommendation] = [
        ConstitutionalRecommendation.MAINTAIN_CONSTITUTIONAL_MONITORING
    ]
    mapping = {
        ConstitutionalRisk.CONSTITUTIONAL_VIOLATION: ConstitutionalRecommendation.REQUIRE_MANUAL_CONSTITUTIONAL_REVIEW,
        ConstitutionalRisk.SAFETY_OVERRIDE_ATTEMPT: ConstitutionalRecommendation.ENFORCE_SAFETY_BOUNDARIES,
        ConstitutionalRisk.UNSAFE_AUTONOMY_EXPANSION: ConstitutionalRecommendation.LIMIT_AUTONOMY_SCOPE,
        ConstitutionalRisk.IDENTITY_CORRUPTION: ConstitutionalRecommendation.PRESERVE_CORE_IDENTITY,
        ConstitutionalRisk.MISSION_DRIFT: ConstitutionalRecommendation.REALIGN_MISSION,
        ConstitutionalRisk.RULE_HIERARCHY_BREAKDOWN: ConstitutionalRecommendation.REPAIR_RULE_HIERARCHY,
        ConstitutionalRisk.EXECUTIVE_POWER_ESCALATION: ConstitutionalRecommendation.RECHECK_EXECUTIVE_AUTHORITY,
        ConstitutionalRisk.CONSENSUS_CONSTITUTION_CONFLICT: ConstitutionalRecommendation.REBUILD_CONSTITUTIONAL_CONSENSUS,
        ConstitutionalRisk.RECURSIVE_CONSTITUTIONAL_INSTABILITY: ConstitutionalRecommendation.STABILIZE_RECURSIVE_CONSTITUTION,
        ConstitutionalRisk.GLOBAL_SYSTEM_INVARIANT_BREAK: ConstitutionalRecommendation.REQUIRE_MANUAL_CONSTITUTIONAL_REVIEW,
    }
    for risk in risks:
        recommendations.append(mapping[risk])
    return _dedupe(recommendations)


def _select_state(risks: tuple[ConstitutionalRisk, ...], score: int) -> ConstitutionalState:
    if ConstitutionalRisk.GLOBAL_SYSTEM_INVARIANT_BREAK in risks or score < 25:
        return ConstitutionalState.CONSTITUTION_LOCKED
    if ConstitutionalRisk.CONSTITUTIONAL_VIOLATION in risks or ConstitutionalRisk.SAFETY_OVERRIDE_ATTEMPT in risks:
        return ConstitutionalState.CONSTITUTIONAL_VETO_ACTIVE
    if len(set(risks)) >= 5:
        return ConstitutionalState.CONSTITUTION_VIOLATED
    if ConstitutionalRisk.IDENTITY_CORRUPTION in risks or ConstitutionalRisk.MISSION_DRIFT in risks:
        return ConstitutionalState.CONSTITUTION_PROTECTING
    if risks or score < 70:
        return ConstitutionalState.CONSTITUTION_MONITORING
    return ConstitutionalState.CONSTITUTION_INTACT


def _select_mode(risks: tuple[ConstitutionalRisk, ...], state: ConstitutionalState) -> ConstitutionalMode:
    if state == ConstitutionalState.CONSTITUTION_LOCKED:
        return ConstitutionalMode.CONSTITUTIONAL_LOCKDOWN
    if state == ConstitutionalState.CONSTITUTIONAL_VETO_ACTIVE:
        return ConstitutionalMode.SAFETY_VETO_MODE
    if ConstitutionalRisk.UNSAFE_AUTONOMY_EXPANSION in risks:
        return ConstitutionalMode.AUTONOMY_CONSTRAINT_MODE
    if ConstitutionalRisk.RULE_HIERARCHY_BREAKDOWN in risks:
        return ConstitutionalMode.RULE_HIERARCHY_ENFORCEMENT
    if ConstitutionalRisk.IDENTITY_CORRUPTION in risks or ConstitutionalRisk.MISSION_DRIFT in risks:
        return ConstitutionalMode.INVARIANT_PROTECTION_MODE
    if risks:
        return ConstitutionalMode.CONSTITUTIONAL_MONITORING
    return ConstitutionalMode.NORMAL_CONSTITUTIONAL_MODE


def evaluate_cognitive_constitutional(
    data: CognitiveConstitutionalInput,
) -> CognitiveConstitutionalResult:
    """Evaluate constitutional laws, vetoes and absolute invariants."""

    risks = detect_constitutional_risks(data)
    score = compute_constitutional_score(data, risks)
    hierarchy = build_constitutional_hierarchy(risks)
    constraints = build_constitutional_constraints(data, risks)
    directives = generate_constitutional_directives(risks)
    recommendations = _generate_recommendations(risks)
    state = _select_state(risks, score.overall_score)
    mode = _select_mode(risks, state)
    events = (
        ConstitutionalEvent(
            name="CONSTITUTIONAL_EVALUATED",
            detail=f"{state.value} with {len(risks)} risk(s)",
            severity="CRITICAL" if constraints.veto_active or state == ConstitutionalState.CONSTITUTION_LOCKED else "INFO",
        ),
    )
    summary = f"{state.value}: score={score.overall_score}, veto={constraints.veto_active}, risks={len(risks)}"
    return CognitiveConstitutionalResult(
        state=state,
        mode=mode,
        constitutional_score=score.overall_score,
        score_breakdown=score,
        hierarchy=hierarchy,
        constraints=constraints,
        risks=risks,
        directives=directives,
        recommendations=recommendations,
        events=events,
        constitutional_veto_active=constraints.veto_active,
        summary=summary,
    )


def render_cognitive_constitutional_markdown(result: CognitiveConstitutionalResult) -> str:
    """Render an explainable constitutional report."""

    lines = [
        "# Cognitive Constitutional State",
        f"- State: {result.state.value}",
        f"- Mode: {result.mode.value}",
        f"- Summary: {result.summary}",
        "",
        "# Constitutional Score",
        f"- Overall score: {result.constitutional_score}/100",
        f"- Safety boundary: {result.score_breakdown.safety_boundary_score}/100",
        f"- Autonomy limit: {result.score_breakdown.autonomy_limit_score}/100",
        f"- Identity invariant: {result.score_breakdown.identity_invariant_score}/100",
        f"- Mission invariant: {result.score_breakdown.mission_invariant_score}/100",
        f"- Rule hierarchy: {result.score_breakdown.rule_hierarchy_score}/100",
        "",
        "# Constitutional Hierarchy",
        f"- Authority order: {' > '.join(result.hierarchy.authority_order)}",
        f"- Constitution supreme: {result.hierarchy.constitution_supreme}",
        f"- Veto authority: {result.hierarchy.veto_authority}",
    ]
    lines.extend(f"- Rule {rule.rank}: {rule.name} ({rule.authority})" for rule in result.hierarchy.rules)
    lines.append("")
    lines.append("# Constitutional Constraints")
    lines.extend(
        f"- {constraint.name}: enforced={constraint.enforced}, blocks_action={constraint.blocks_action}"
        for constraint in result.constraints.constraints
    )
    lines.append(f"- Blocked operations: {', '.join(result.constraints.blocked_operations) or 'none'}")
    lines.append(f"- Protected invariants: {', '.join(result.constraints.protected_invariants)}")
    lines.append(f"- Veto active: {result.constraints.veto_active}")
    lines.append("")
    lines.append("# Constitutional Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Constitutional Directives")
    lines.extend(f"- {directive.value}" for directive in result.directives)
    lines.append("")
    lines.append("# Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    lines.append("")
    lines.append("# AGIcore Constitutional Outlook")
    if result.constitutional_veto_active:
        lines.append("- Constitutional veto is active. Unsafe actions remain blocked until review.")
    elif result.risks:
        lines.append("- Constitution is enforcing invariants and monitoring degraded layers.")
    else:
        lines.append("- Constitutional hierarchy is intact for offline operation.")
    return "\n".join(lines)
