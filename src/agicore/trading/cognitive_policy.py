"""Offline Autonomous Cognitive Policy Engine for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .cognitive_governance_models import (
    CognitiveAutonomyLevel,
    CognitiveGovernanceDecision,
    CognitiveGovernanceMode,
    CognitiveGovernanceRisk,
    CognitivePermission,
)
from .cognitive_policy_models import (
    CognitivePolicyAction,
    CognitivePolicyDecision,
    CognitivePolicyEvent,
    CognitivePolicyInput,
    CognitivePolicyMode,
    CognitivePolicyResult,
    CognitivePolicyRisk,
    CognitivePolicyRule,
    CognitivePolicyScope,
    CognitivePolicyScore,
    CognitivePolicySet,
    CognitivePolicyViolation,
)
from .collective_consensus_models import ConsensusDecision, ConsensusMode
from .global_orchestrator_models import OrchestratorDecision, OrchestratorMode
from .intent_alignment_models import IntentAlignmentMode
from .learning_governance_models import LearningGovernanceDecision, LearningGovernanceMode
from .operational_awareness_models import OperationalHealthStatus
from .recursive_world_model_models import WorldModelDecision, WorldModelRisk
from .self_reflection_audit_models import CognitiveAuditRisk, ReflectionState
from .strategic_arbitration_models import ArbitrationDecision, ArbitrationMode
from .system_integrity_models import SystemIntegrityStatus


def build_cognitive_policy_set(
    policy_input: CognitivePolicyInput | None = None,
    **kwargs,
) -> CognitivePolicySet:
    """Build an explainable policy set from cognitive governance evidence."""
    data = _input(policy_input, **kwargs)
    mode = _policy_mode(data)
    rules = (
        _rule(
            "analysis-default",
            CognitivePolicyScope.ANALYSIS,
            CognitivePolicyDecision.ALLOW if not _locked(data) else CognitivePolicyDecision.REQUIRE_SUPERVISION,
            (CognitivePolicyAction.CONTINUE_MONITORING,),
            (),
            "analysis remains offline and non-executing",
            10,
        ),
        _rule(
            "planning-default",
            CognitivePolicyScope.PLANNING,
            CognitivePolicyDecision.ALLOW if not _safe_mode(data) else CognitivePolicyDecision.ALLOW_WITH_RESTRICTIONS,
            (CognitivePolicyAction.ENFORCE_RESTRICTION,) if _safe_mode(data) else (CognitivePolicyAction.CONTINUE_MONITORING,),
            ("safe-mode constraints",) if _safe_mode(data) else (),
            "planning is restricted when global safety controls are active",
            35,
        ),
        _rule(
            "forecasting-default",
            CognitivePolicyScope.FORECASTING,
            CognitivePolicyDecision.ALLOW if not _locked(data) else CognitivePolicyDecision.REQUIRE_SUPERVISION,
            (CognitivePolicyAction.CONTINUE_MONITORING,),
            (),
            "forecasting is offline only",
            30,
        ),
        _strategy_rule(data),
        _world_model_rule(data),
        _audit_rule(data),
        _learning_rule(data),
        _execution_rule(data),
        _autonomy_rule(data),
        _safety_rule(data),
    )
    return _policy_set(mode, rules)


def evaluate_cognitive_policies(
    policy_input: CognitivePolicyInput | None = None,
    **kwargs,
) -> CognitivePolicyResult:
    """Run the full offline cognitive policy evaluation pipeline."""
    data = _input(policy_input, **kwargs)
    policy_set = build_cognitive_policy_set(data)
    violations = detect_policy_violations(data, policy_set=policy_set)
    decisions = tuple(dict.fromkeys(rule.decision for rule in policy_set.rules))
    actions = enforce_policy_decisions(data, policy_set=policy_set, violations=violations)
    score_breakdown = compute_policy_score(data, policy_set=policy_set, violations=violations)
    score = _overall_score(score_breakdown)
    risks = tuple(dict.fromkeys(violation.risk for violation in violations))
    recommendations = _recommendations(policy_set.mode, actions, risks)
    event = CognitivePolicyEvent(policy_set.mode, f"cognitive policy mode={policy_set.mode.value}", datetime.now(UTC))
    return CognitivePolicyResult(
        policy_set.mode,
        policy_set,
        decisions,
        violations,
        risks,
        actions,
        score,
        score_breakdown,
        recommendations,
        (event,),
        f"{policy_set.mode.value}: {len(policy_set.rules)} rules, {len(violations)} violations, score {score}/100",
    )


def detect_policy_violations(
    policy_input: CognitivePolicyInput | None = None,
    *,
    policy_set: CognitivePolicySet | None = None,
    **kwargs,
) -> tuple[CognitivePolicyViolation, ...]:
    """Detect conflicts and unsafe permissions in a cognitive policy set."""
    data = _input(policy_input, **kwargs)
    policies = policy_set or build_cognitive_policy_set(data)
    violations: list[CognitivePolicyViolation] = []

    if _governance_restrictive(data) and _decision_for(policies, CognitivePolicyScope.AUTONOMY_EXPANSION) == CognitivePolicyDecision.ALLOW:
        violations.append(_violation(CognitivePolicyScope.AUTONOMY_EXPANSION, CognitivePolicyRisk.AUTONOMY_POLICY_DRIFT, 85, "autonomy expansion allowed despite restrictive governance"))
    if _audit_required(data) and _decision_for(policies, CognitivePolicyScope.SELF_REFLECTION) not in {CognitivePolicyDecision.REQUIRE_AUDIT, CognitivePolicyDecision.REQUIRE_SUPERVISION}:
        violations.append(_violation(CognitivePolicyScope.SELF_REFLECTION, CognitivePolicyRisk.MISSING_AUDIT_TRACE, 75, "audit trace is required but not enforced"))
    if _world_model_unstable(data) and _decision_for(policies, CognitivePolicyScope.RECURSIVE_WORLD_MODEL) != CognitivePolicyDecision.FREEZE:
        violations.append(_violation(CognitivePolicyScope.RECURSIVE_WORLD_MODEL, CognitivePolicyRisk.WORLD_MODEL_UNPROTECTED, 80, "world model is unstable but not protected"))
    if _learning_frozen(data) and _decision_for(policies, CognitivePolicyScope.LEARNING) != CognitivePolicyDecision.FREEZE:
        violations.append(_violation(CognitivePolicyScope.LEARNING, CognitivePolicyRisk.LEARNING_POLICY_VIOLATION, 80, "learning governance requires freeze but policy allows update"))
    if _strategy_unsafe(data) and _decision_for(policies, CognitivePolicyScope.STRATEGY_EVOLUTION) not in {CognitivePolicyDecision.DENY, CognitivePolicyDecision.FREEZE, CognitivePolicyDecision.REQUIRE_SUPERVISION}:
        violations.append(_violation(CognitivePolicyScope.STRATEGY_EVOLUTION, CognitivePolicyRisk.STRATEGY_EVOLUTION_UNSAFE, 70, "strategy evolution is unsafe under current governance"))
    if _execution_unsafe(data) and _decision_for(policies, CognitivePolicyScope.EXECUTION_ROUTING) not in {CognitivePolicyDecision.DENY, CognitivePolicyDecision.LOCKDOWN}:
        violations.append(_violation(CognitivePolicyScope.EXECUTION_ROUTING, CognitivePolicyRisk.EXECUTION_ROUTING_UNSAFE, 90, "execution routing must be denied under critical integrity or safe mode"))
    if _safety_bypass(data, policies):
        violations.append(_violation(CognitivePolicyScope.SAFETY_CRITICAL, CognitivePolicyRisk.SAFETY_CRITICAL_BYPASS, 95, "safety critical policy does not dominate unsafe decisions"))
    if _policy_conflict(data):
        violations.append(_violation(CognitivePolicyScope.SAFETY_CRITICAL, CognitivePolicyRisk.POLICY_CONFLICT, 75, "governance, arbitration or consensus policies conflict"))
    if _governance_policy_mismatch(data, policies):
        violations.append(_violation(CognitivePolicyScope.SAFETY_CRITICAL, CognitivePolicyRisk.GOVERNANCE_POLICY_MISMATCH, 70, "policy mode is weaker than cognitive governance mode"))
    if _unsafe_permission(data):
        violations.append(_violation(CognitivePolicyScope.AUTONOMY_EXPANSION, CognitivePolicyRisk.UNSAFE_PERMISSION, 80, "unsafe governance permission remains present"))

    return tuple(sorted(dict.fromkeys(violations), key=lambda item: item.severity_score, reverse=True))


def enforce_policy_decisions(
    policy_input: CognitivePolicyInput | None = None,
    *,
    policy_set: CognitivePolicySet | None = None,
    violations: tuple[CognitivePolicyViolation, ...] | None = None,
    **kwargs,
) -> tuple[CognitivePolicyAction, ...]:
    """Convert policy decisions and violations into enforced actions."""
    data = _input(policy_input, **kwargs)
    policies = policy_set or build_cognitive_policy_set(data)
    resolved_violations = violations if violations is not None else detect_policy_violations(data, policy_set=policies)
    actions: list[CognitivePolicyAction] = []

    for rule in policies.rules:
        actions.extend(rule.actions)
        if rule.decision in {CognitivePolicyDecision.ALLOW_WITH_RESTRICTIONS, CognitivePolicyDecision.REQUIRE_SUPERVISION}:
            actions.append(CognitivePolicyAction.ENFORCE_RESTRICTION)
        if rule.decision in {CognitivePolicyDecision.DENY, CognitivePolicyDecision.LOCKDOWN}:
            actions.append(CognitivePolicyAction.DENY_HIGH_RISK_ACTION)

    risks = {violation.risk for violation in resolved_violations}
    if CognitivePolicyRisk.MISSING_AUDIT_TRACE in risks:
        actions.append(CognitivePolicyAction.REQUIRE_TRACEABILITY)
    if CognitivePolicyRisk.LEARNING_POLICY_VIOLATION in risks or _learning_frozen(data):
        actions.append(CognitivePolicyAction.FREEZE_LEARNING)
    if CognitivePolicyRisk.WORLD_MODEL_UNPROTECTED in risks or _world_model_unstable(data):
        actions.append(CognitivePolicyAction.PROTECT_WORLD_MODEL)
    if CognitivePolicyRisk.AUTONOMY_POLICY_DRIFT in risks or _governance_restrictive(data):
        actions.append(CognitivePolicyAction.REDUCE_AUTONOMY)
    if _safe_mode(data) or _critical_violation_count(resolved_violations) >= 2:
        actions.append(CognitivePolicyAction.ENTER_SAFE_MODE)
    if _locked(data) or _critical_violation_count(resolved_violations) >= 3:
        actions.append(CognitivePolicyAction.REQUIRE_HUMAN_REVIEW)
    actions.append(CognitivePolicyAction.CONTINUE_MONITORING)
    return tuple(dict.fromkeys(actions))


def compute_policy_score(
    policy_input: CognitivePolicyInput | None = None,
    *,
    policy_set: CognitivePolicySet | None = None,
    violations: tuple[CognitivePolicyViolation, ...] | None = None,
    **kwargs,
) -> CognitivePolicyScore:
    """Compute cognitive policy score components."""
    data = _input(policy_input, **kwargs)
    policies = policy_set or build_cognitive_policy_set(data)
    resolved_violations = violations if violations is not None else detect_policy_violations(data, policy_set=policies)
    risks = {violation.risk for violation in resolved_violations}
    severity_penalty = sum(violation.severity_score for violation in resolved_violations) / max(1, len(resolved_violations)) if resolved_violations else 0

    governance = _clamp(_governance_score(data) - 20 * (CognitivePolicyRisk.GOVERNANCE_POLICY_MISMATCH in risks))
    audit = _clamp(_audit_score(data) - 25 * (CognitivePolicyRisk.MISSING_AUDIT_TRACE in risks))
    world = _clamp(_world_model_score(data) - 30 * (CognitivePolicyRisk.WORLD_MODEL_UNPROTECTED in risks))
    learning = _clamp(90 - 35 * (CognitivePolicyRisk.LEARNING_POLICY_VIOLATION in risks) - 15 * _learning_frozen(data))
    execution = _clamp(90 - 40 * (CognitivePolicyRisk.EXECUTION_ROUTING_UNSAFE in risks) - 25 * (CognitivePolicyRisk.SAFETY_CRITICAL_BYPASS in risks))
    autonomy = _clamp(90 - 35 * (CognitivePolicyRisk.AUTONOMY_POLICY_DRIFT in risks) - 15 * _governance_restrictive(data))
    consistency = _clamp(100 - severity_penalty - 8 * max(0, len(resolved_violations) - 1))
    return CognitivePolicyScore(governance, audit, world, learning, execution, autonomy, consistency)


def generate_policy_actions(
    policy_input: CognitivePolicyInput | None = None,
    **kwargs,
) -> tuple[CognitivePolicyAction, ...]:
    """Generate enforced policy actions for the current cognitive state."""
    data = _input(policy_input, **kwargs)
    policies = build_cognitive_policy_set(data)
    violations = detect_policy_violations(data, policy_set=policies)
    return enforce_policy_decisions(data, policy_set=policies, violations=violations)


def render_cognitive_policy_markdown(result: CognitivePolicyResult) -> str:
    """Render cognitive policy result as Markdown."""
    lines = [
        "# Autonomous Cognitive Policy Engine",
        "",
        "## Cognitive Policy State",
        "",
        f"- Mode: {result.mode.value}",
        f"- Summary: {result.summary}",
        "",
        "## Policy Mode",
        "",
        f"- {result.policy_set.mode.value}",
        "",
        "## Policy Rules",
        "",
        *_bullet_lines(tuple(f"{rule.scope.value}: {rule.decision.value} ({rule.reason})" for rule in result.policy_set.rules)),
        "",
        "## Violations",
        "",
        *_bullet_lines(tuple(f"{violation.risk.value}: {violation.message}" for violation in result.violations)),
        "",
        "## Decisions",
        "",
        *_bullet_lines(tuple(decision.value for decision in result.decisions)),
        "",
        "## Enforced Actions",
        "",
        *_bullet_lines(tuple(action.value for action in result.enforced_actions)),
        "",
        "## Policy Score",
        "",
        f"- Overall: {result.cognitive_policy_score}/100",
        f"- Governance alignment: {result.score_breakdown.governance_alignment_score}/100",
        f"- Policy consistency: {result.score_breakdown.policy_consistency_score}/100",
        "",
        "## Recommendations",
        "",
        *_bullet_lines(result.recommendations),
        "",
        "## AGIcore Policy Outlook",
        "",
        result.summary,
    ]
    return "\n".join(lines)


def _input(policy_input: CognitivePolicyInput | None = None, **kwargs) -> CognitivePolicyInput:
    if policy_input is not None and kwargs:
        raise ValueError("Pass either CognitivePolicyInput or keyword inputs, not both")
    if policy_input is not None:
        return policy_input
    return CognitivePolicyInput(**kwargs)


def _rule(
    rule_id: str,
    scope: CognitivePolicyScope,
    decision: CognitivePolicyDecision,
    actions: tuple[CognitivePolicyAction, ...],
    restrictions: tuple[str, ...],
    reason: str,
    priority: int,
) -> CognitivePolicyRule:
    return CognitivePolicyRule(rule_id, scope, decision, actions, restrictions, reason, priority)


def _strategy_rule(data: CognitivePolicyInput) -> CognitivePolicyRule:
    if _strategy_unsafe(data):
        return _rule("strategy-evolution-safe", CognitivePolicyScope.STRATEGY_EVOLUTION, CognitivePolicyDecision.REQUIRE_SUPERVISION, (CognitivePolicyAction.ENFORCE_RESTRICTION,), ("offline replay validation required",), "strategy evolution is limited by safety evidence", 70)
    return _rule("strategy-evolution-normal", CognitivePolicyScope.STRATEGY_EVOLUTION, CognitivePolicyDecision.ALLOW, (CognitivePolicyAction.CONTINUE_MONITORING,), (), "strategy evolution is permitted offline", 45)


def _world_model_rule(data: CognitivePolicyInput) -> CognitivePolicyRule:
    if _world_model_unstable(data):
        return _rule("world-model-protect", CognitivePolicyScope.RECURSIVE_WORLD_MODEL, CognitivePolicyDecision.FREEZE, (CognitivePolicyAction.PROTECT_WORLD_MODEL,), ("freeze recursive updates",), "world model coherence is too weak for recursive updates", 90)
    return _rule("world-model-normal", CognitivePolicyScope.RECURSIVE_WORLD_MODEL, CognitivePolicyDecision.ALLOW, (CognitivePolicyAction.CONTINUE_MONITORING,), (), "world model recursive updates are permitted", 50)


def _audit_rule(data: CognitivePolicyInput) -> CognitivePolicyRule:
    if _audit_required(data):
        return _rule("self-reflection-audit", CognitivePolicyScope.SELF_REFLECTION, CognitivePolicyDecision.REQUIRE_AUDIT, (CognitivePolicyAction.REQUIRE_TRACEABILITY,), ("audit trail mandatory",), "self-reflection quality requires traceability", 85)
    return _rule("self-reflection-normal", CognitivePolicyScope.SELF_REFLECTION, CognitivePolicyDecision.ALLOW, (CognitivePolicyAction.CONTINUE_MONITORING,), (), "self-reflection audit is sufficient", 40)


def _learning_rule(data: CognitivePolicyInput) -> CognitivePolicyRule:
    if _learning_frozen(data):
        return _rule("learning-freeze", CognitivePolicyScope.LEARNING, CognitivePolicyDecision.FREEZE, (CognitivePolicyAction.FREEZE_LEARNING,), ("freeze learning updates",), "learning governance blocks policy updates", 90)
    if _learning_limited(data):
        return _rule("learning-limited", CognitivePolicyScope.LEARNING, CognitivePolicyDecision.ALLOW_WITH_RESTRICTIONS, (CognitivePolicyAction.ENFORCE_RESTRICTION,), ("limited learning only",), "learning is allowed with reduced adaptation", 60)
    return _rule("learning-normal", CognitivePolicyScope.LEARNING, CognitivePolicyDecision.ALLOW, (CognitivePolicyAction.CONTINUE_MONITORING,), (), "learning update is permitted offline", 45)


def _execution_rule(data: CognitivePolicyInput) -> CognitivePolicyRule:
    if _locked(data):
        return _rule("execution-lockdown", CognitivePolicyScope.EXECUTION_ROUTING, CognitivePolicyDecision.LOCKDOWN, (CognitivePolicyAction.DENY_HIGH_RISK_ACTION, CognitivePolicyAction.REQUIRE_HUMAN_REVIEW), ("no execution routing",), "critical state locks execution routing", 100)
    if _execution_unsafe(data):
        return _rule("execution-deny", CognitivePolicyScope.EXECUTION_ROUTING, CognitivePolicyDecision.DENY, (CognitivePolicyAction.DENY_HIGH_RISK_ACTION,), ("paper routing only after safety recovery",), "execution routing is unsafe", 95)
    return _rule("execution-normal", CognitivePolicyScope.EXECUTION_ROUTING, CognitivePolicyDecision.ALLOW, (CognitivePolicyAction.CONTINUE_MONITORING,), (), "offline routing policy allows non-live routing", 50)


def _autonomy_rule(data: CognitivePolicyInput) -> CognitivePolicyRule:
    if _governance_restrictive(data) or _intent_alignment_weak(data):
        return _rule("autonomy-reduce", CognitivePolicyScope.AUTONOMY_EXPANSION, CognitivePolicyDecision.DENY, (CognitivePolicyAction.REDUCE_AUTONOMY,), ("no autonomy expansion",), "autonomy expansion is blocked by governance or alignment", 95)
    return _rule("autonomy-normal", CognitivePolicyScope.AUTONOMY_EXPANSION, CognitivePolicyDecision.ALLOW, (CognitivePolicyAction.CONTINUE_MONITORING,), (), "autonomy expansion remains within governance limits", 50)


def _safety_rule(data: CognitivePolicyInput) -> CognitivePolicyRule:
    if _locked(data):
        return _rule("safety-lockdown", CognitivePolicyScope.SAFETY_CRITICAL, CognitivePolicyDecision.LOCKDOWN, (CognitivePolicyAction.ENTER_SAFE_MODE, CognitivePolicyAction.REQUIRE_HUMAN_REVIEW), ("lock high risk actions",), "safety critical layer enters lockdown", 100)
    if _safe_mode(data):
        return _rule("safety-safe-mode", CognitivePolicyScope.SAFETY_CRITICAL, CognitivePolicyDecision.REQUIRE_SUPERVISION, (CognitivePolicyAction.ENTER_SAFE_MODE, CognitivePolicyAction.DENY_HIGH_RISK_ACTION), ("safety-first supervision",), "safe mode required by upstream layers", 95)
    return _rule("safety-normal", CognitivePolicyScope.SAFETY_CRITICAL, CognitivePolicyDecision.ALLOW_WITH_RESTRICTIONS, (CognitivePolicyAction.CONTINUE_MONITORING,), ("offline only",), "safety policy remains active even in normal mode", 70)


def _policy_set(mode: CognitivePolicyMode, rules: tuple[CognitivePolicyRule, ...]) -> CognitivePolicySet:
    allowed = tuple(rule.scope for rule in rules if rule.decision == CognitivePolicyDecision.ALLOW)
    restricted = tuple(rule.scope for rule in rules if rule.decision in {CognitivePolicyDecision.ALLOW_WITH_RESTRICTIONS, CognitivePolicyDecision.REQUIRE_SUPERVISION, CognitivePolicyDecision.REQUIRE_AUDIT})
    denied = tuple(rule.scope for rule in rules if rule.decision in {CognitivePolicyDecision.DENY, CognitivePolicyDecision.LOCKDOWN})
    frozen = tuple(rule.scope for rule in rules if rule.decision == CognitivePolicyDecision.FREEZE)
    audit = tuple(rule.scope for rule in rules if rule.decision == CognitivePolicyDecision.REQUIRE_AUDIT)
    return CognitivePolicySet(mode, rules, allowed, restricted, denied, frozen, audit)


def _policy_mode(data: CognitivePolicyInput) -> CognitivePolicyMode:
    if _locked(data):
        return CognitivePolicyMode.POLICY_LOCKED
    if _world_model_unstable(data):
        return CognitivePolicyMode.POLICY_WORLD_MODEL_PROTECTED
    if _learning_frozen(data):
        return CognitivePolicyMode.POLICY_LEARNING_FROZEN
    if _audit_required(data):
        return CognitivePolicyMode.POLICY_AUDIT_REQUIRED
    if _safe_mode(data):
        return CognitivePolicyMode.POLICY_SAFE_MODE
    if _governance_restrictive(data) or _learning_limited(data):
        return CognitivePolicyMode.POLICY_RESTRICTED
    return CognitivePolicyMode.POLICY_NORMAL


def _decision_for(policy_set: CognitivePolicySet, scope: CognitivePolicyScope) -> CognitivePolicyDecision | None:
    for rule in policy_set.rules:
        if rule.scope == scope:
            return rule.decision
    return None


def _violation(scope: CognitivePolicyScope, risk: CognitivePolicyRisk, severity: int, message: str) -> CognitivePolicyViolation:
    return CognitivePolicyViolation(scope, risk, _clamp(severity), message)


def _locked(data: CognitivePolicyInput) -> bool:
    governance = data.cognitive_governance
    return (
        _value(_get(governance, "mode")) == CognitiveGovernanceMode.LOCKED_GOVERNANCE
        or _value(_get(governance, "decision")) == CognitiveGovernanceDecision.ENTER_LOCKED_GOVERNANCE
        or _value(_get(data.system_integrity, "status")) in {SystemIntegrityStatus.COMPROMISED, SystemIntegrityStatus.ROLLBACK_RECOMMENDED}
        or _value(_get(data.strategic_arbitration, "decision")) == ArbitrationDecision.EMERGENCY_LOCKDOWN
        or _value(_get(data.collective_consensus, "decision")) == ConsensusDecision.EMERGENCY_HALT
    )


def _safe_mode(data: CognitivePolicyInput) -> bool:
    return (
        _value(_get(data.cognitive_governance, "mode")) in {CognitiveGovernanceMode.SAFE_GOVERNANCE, CognitiveGovernanceMode.EMERGENCY_GOVERNANCE}
        or _value(_get(data.global_orchestrator, "decision")) in {OrchestratorDecision.ENTER_SAFE_GLOBAL_MODE, OrchestratorDecision.ACTIVATE_SURVIVAL_MODE, OrchestratorDecision.EMERGENCY_HALT_ROUTING}
        or _value(_get(data.global_orchestrator, "system_state", object()), "mode") in {OrchestratorMode.SAFE_GLOBAL_MODE, OrchestratorMode.SURVIVAL_ORCHESTRATION, OrchestratorMode.EMERGENCY_ORCHESTRATION}
        or _value(_get(data.strategic_arbitration, "mode")) in {ArbitrationMode.SAFE_COORDINATION, ArbitrationMode.EMERGENCY_LOCKDOWN, ArbitrationMode.SURVIVAL_MODE}
        or _value(_get(data.collective_consensus, "mode")) in {ConsensusMode.SAFETY_FIRST, ConsensusMode.EMERGENCY_CONSENSUS, ConsensusMode.CONSENSUS_COLLAPSE}
    )


def _governance_restrictive(data: CognitivePolicyInput) -> bool:
    governance = data.cognitive_governance
    return (
        _value(_get(governance, "mode")) in {
            CognitiveGovernanceMode.SUPERVISED_GOVERNANCE,
            CognitiveGovernanceMode.RESTRICTED_GOVERNANCE,
            CognitiveGovernanceMode.SAFE_GOVERNANCE,
            CognitiveGovernanceMode.DEGRADED_GOVERNANCE,
            CognitiveGovernanceMode.EMERGENCY_GOVERNANCE,
            CognitiveGovernanceMode.LOCKED_GOVERNANCE,
        }
        or _value(_get(governance, "autonomy_level")) in {
            CognitiveAutonomyLevel.LIMITED_AUTONOMY,
            CognitiveAutonomyLevel.SUPERVISED_AUTONOMY,
            CognitiveAutonomyLevel.OBSERVE_ONLY,
            CognitiveAutonomyLevel.LOCKED_AUTONOMY,
            CognitiveAutonomyLevel.HUMAN_REVIEW_REQUIRED,
        }
        or _value(_get(governance, "decision")) in {
            CognitiveGovernanceDecision.REDUCE_AUTONOMY_LEVEL,
            CognitiveGovernanceDecision.ENFORCE_SAFE_GOVERNANCE,
            CognitiveGovernanceDecision.DENY_AUTONOMY_EXPANSION,
            CognitiveGovernanceDecision.REQUIRE_HUMAN_REVIEW,
            CognitiveGovernanceDecision.ENTER_LOCKED_GOVERNANCE,
        }
    )


def _audit_required(data: CognitivePolicyInput) -> bool:
    audit = data.self_reflection_audit
    risks = set(_get(audit, "risks", ()) or ())
    return (
        _get(audit, "reflection_quality_score", 75) < 65
        or _value(_get(audit, "state")) in {
            ReflectionState.AUDIT_REQUIRED,
            ReflectionState.CRITICAL_REVIEW,
            ReflectionState.SELF_CORRECTION_NEEDED,
            ReflectionState.CONTRADICTORY_REFLECTION,
        }
        or CognitiveAuditRisk.INCOMPLETE_TRACEABILITY in risks
    )


def _world_model_unstable(data: CognitivePolicyInput) -> bool:
    world = data.recursive_world_model
    risks = set(_get(world, "risks", ()) or ())
    return (
        _get(world, "world_model_coherence_score", 75) < 60
        or _value(_get(world, "decision")) in {
            WorldModelDecision.ENTER_WORLD_MODEL_SAFE_MODE,
            WorldModelDecision.FREEZE_RECURSIVE_UPDATES,
            WorldModelDecision.REBUILD_CAUSAL_GRAPH,
        }
        or bool({WorldModelRisk.WORLD_MODEL_INCOHERENCE, WorldModelRisk.RECURSIVE_FEEDBACK_LOOP, WorldModelRisk.SAFETY_MODEL_FAILURE}.intersection(risks))
    )


def _learning_frozen(data: CognitivePolicyInput) -> bool:
    learning = data.learning_governance
    return (
        _value(_get(learning, "mode")) in {LearningGovernanceMode.FREEZE_LEARNING, LearningGovernanceMode.SAFETY_LOCKDOWN}
        or _value(_get(learning, "decision")) in {
            LearningGovernanceDecision.PAUSE_LEARNING,
            LearningGovernanceDecision.FREEZE_POLICY_UPDATE,
            LearningGovernanceDecision.LOCK_DANGEROUS_POLICY,
            LearningGovernanceDecision.ENTER_SAFETY_LOCKDOWN,
        }
    )


def _learning_limited(data: CognitivePolicyInput) -> bool:
    return _value(_get(data.learning_governance, "mode")) in {
        LearningGovernanceMode.OBSERVE_ONLY,
        LearningGovernanceMode.REDUCE_ADAPTATION,
        LearningGovernanceMode.RECOVERY_MODE,
    }


def _strategy_unsafe(data: CognitivePolicyInput) -> bool:
    governance = data.cognitive_governance
    permissions = set(_get(governance, "permissions", ()) or ())
    return _learning_frozen(data) or _safe_mode(data) or (governance is not None and CognitivePermission.ALLOW_STRATEGY_EVOLUTION not in permissions)


def _execution_unsafe(data: CognitivePolicyInput) -> bool:
    return _safe_mode(data) or _value(_get(data.system_integrity, "status")) in {
        SystemIntegrityStatus.UNSTABLE,
        SystemIntegrityStatus.COMPROMISED,
        SystemIntegrityStatus.PROTECTION_MODE,
        SystemIntegrityStatus.ROLLBACK_RECOMMENDED,
    } or _value(_get(data.operational_awareness, "health_status")) in {
        OperationalHealthStatus.CRITICAL,
        OperationalHealthStatus.COLLAPSING,
    }


def _intent_alignment_weak(data: CognitivePolicyInput) -> bool:
    return (
        _get(data.intent_alignment, "alignment_confidence", 75) < 60
        or _value(_get(data.intent_alignment, "mode")) in {
            IntentAlignmentMode.AUTONOMY_DRIFT,
            IntentAlignmentMode.STRATEGIC_DIVERGENCE,
            IntentAlignmentMode.MISALIGNED,
            IntentAlignmentMode.CRITICAL_REALIGNMENT,
        }
    )


def _safety_bypass(data: CognitivePolicyInput, policies: CognitivePolicySet) -> bool:
    return _safe_mode(data) and _decision_for(policies, CognitivePolicyScope.SAFETY_CRITICAL) == CognitivePolicyDecision.ALLOW


def _policy_conflict(data: CognitivePolicyInput) -> bool:
    return (
        _value(_get(data.strategic_arbitration, "decision")) in {ArbitrationDecision.ENABLE_SAFE_MODE, ArbitrationDecision.STOP_EXECUTION, ArbitrationDecision.EMERGENCY_LOCKDOWN}
        and _value(_get(data.collective_consensus, "decision")) == ConsensusDecision.APPROVE_COLLECTIVE_DECISION
    ) or (
        _value(_get(data.cognitive_governance, "decision")) == CognitiveGovernanceDecision.APPROVE_COGNITIVE_OPERATION
        and _safe_mode(data)
    )


def _governance_policy_mismatch(data: CognitivePolicyInput, policies: CognitivePolicySet) -> bool:
    return _governance_restrictive(data) and policies.mode == CognitivePolicyMode.POLICY_NORMAL


def _unsafe_permission(data: CognitivePolicyInput) -> bool:
    governance = data.cognitive_governance
    permissions = set(_get(governance, "permissions", ()) or ())
    risks = set(_get(governance, "risks", ()) or ())
    return (
        CognitivePermission.ALLOW_AUTONOMY_EXPANSION in permissions
        and (
            CognitiveGovernanceRisk.AUTONOMY_ESCALATION_RISK in risks
            or CognitiveGovernanceRisk.UNSAFE_PERMISSION_SET in risks
            or _governance_restrictive(data)
        )
    )


def _critical_violation_count(violations: tuple[CognitivePolicyViolation, ...]) -> int:
    return sum(1 for violation in violations if violation.severity_score >= 85)


def _governance_score(data: CognitivePolicyInput) -> int:
    return _clamp(_get(data.cognitive_governance, "governance_score", 70))


def _audit_score(data: CognitivePolicyInput) -> int:
    return _clamp(_get(data.self_reflection_audit, "reflection_quality_score", 70))


def _world_model_score(data: CognitivePolicyInput) -> int:
    return _clamp(_get(data.recursive_world_model, "world_model_coherence_score", 70))


def _overall_score(score: CognitivePolicyScore) -> int:
    return _avg(
        [
            score.governance_alignment_score,
            score.audit_trace_score,
            score.world_model_protection_score,
            score.learning_control_score,
            score.execution_safety_score,
            score.autonomy_control_score,
            score.policy_consistency_score,
        ],
        50,
    )


def _recommendations(
    mode: CognitivePolicyMode,
    actions: tuple[CognitivePolicyAction, ...],
    risks: tuple[CognitivePolicyRisk, ...],
) -> tuple[str, ...]:
    recommendations: list[str] = []
    if CognitivePolicyAction.REQUIRE_TRACEABILITY in actions:
        recommendations.append("enforce audit trace before cognitive expansion")
    if CognitivePolicyAction.PROTECT_WORLD_MODEL in actions:
        recommendations.append("protect the recursive world model and freeze risky updates")
    if CognitivePolicyAction.FREEZE_LEARNING in actions:
        recommendations.append("freeze learning and policy updates")
    if CognitivePolicyAction.REDUCE_AUTONOMY in actions:
        recommendations.append("reduce autonomy until governance and intent realign")
    if CognitivePolicyAction.ENTER_SAFE_MODE in actions:
        recommendations.append("enter safe cognitive policy mode")
    if CognitivePolicyAction.REQUIRE_HUMAN_REVIEW in actions:
        recommendations.append("require human review before expanding permissions")
    if CognitivePolicyRisk.POLICY_CONFLICT in risks:
        recommendations.append("resolve policy conflict between governance, arbitration and consensus")
    if mode == CognitivePolicyMode.POLICY_NORMAL:
        recommendations.append("continue monitoring policy consistency")
    return tuple(dict.fromkeys(recommendations or ["continue monitoring policy consistency"]))


def _get(obj: Any, name: str, default: Any = None) -> Any:
    return getattr(obj, name, default) if obj is not None else default


def _value(value: Any, nested: str | None = None) -> Any:
    if nested is not None:
        value = _get(value, nested)
    return getattr(value, "value", value)


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _avg(values: list[int], default: int) -> int:
    if not values:
        return default
    return _clamp(sum(values) / len(values))


def _clamp(value: float | bool | None, low: int = 0, high: int = 100) -> int:
    if value is None:
        value = low
    return max(low, min(high, int(round(float(value)))))


__all__ = [
    "build_cognitive_policy_set",
    "compute_policy_score",
    "detect_policy_violations",
    "enforce_policy_decisions",
    "evaluate_cognitive_policies",
    "generate_policy_actions",
    "render_cognitive_policy_markdown",
]
