"""Offline Autonomous Recovery & Resilience Engine for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .adaptive_policy_memory_models import PolicyMemoryRecommendation
from .behavioral_stability_models import BehavioralPressureLevel, BehavioralRecoveryState
from .cognitive_adaptation_models import CognitiveLoadLevel
from .learning_governance_models import LearningGovernanceDecision, LearningGovernanceMode
from .recursive_self_evaluation_models import (
    SelfEvaluationStatus,
    SystemAutonomyRecommendation,
)
from .recovery_resilience_models import (
    RecoveryAction,
    RecoveryEvent,
    RecoveryMode,
    RecoveryResilienceInput,
    RecoveryResilienceResult,
    RecoveryRisk,
    RecoveryStep,
    ResilienceScore,
)
from .scenario_replay_models import ReplayArenaStatus
from .strategic_memory_models import StrategicDriftSignal
from .strategic_planning_models import StrategicPlanStatus
from .system_integrity_models import ModuleHealthStatus, SystemIntegrityStatus


def evaluate_recovery_resilience(
    recovery_input: RecoveryResilienceInput | None = None,
    **kwargs,
) -> RecoveryResilienceResult:
    """Evaluate recovery mode, resilience score and ordered recovery plan."""
    data = _input(recovery_input, **kwargs)
    score_breakdown = compute_resilience_score(data)
    risks = detect_recovery_risks(data, score_breakdown=score_breakdown)
    plan = build_recovery_plan(data, risks=risks)
    actions = tuple(dict.fromkeys(step.action for step in plan))
    mode = _mode(data, risks, plan, score_breakdown)
    resilience_score = _global_resilience(score_breakdown, risks)
    isolated_modules = tuple(dict.fromkeys(step.target for step in plan if step.action == RecoveryAction.ISOLATE_UNSTABLE_MODULE))
    disabled_policies = tuple(dict.fromkeys(step.target for step in plan if step.action == RecoveryAction.DISABLE_DANGEROUS_POLICY))
    event_action = actions[0] if actions else RecoveryAction.KEEP_RUNNING
    event = RecoveryEvent(
        mode=mode,
        action=event_action,
        message=f"Recovery mode {mode.value}; resilience {resilience_score}/100.",
        timestamp=datetime.now(UTC),
    )
    return RecoveryResilienceResult(
        mode=mode,
        resilience_score=resilience_score,
        score_breakdown=score_breakdown,
        risks=risks,
        actions=actions,
        recovery_plan=plan,
        isolated_modules=isolated_modules,
        disabled_policies=disabled_policies,
        recommendations=_recommendations(mode, risks, plan),
        events=(event,),
        summary=f"Recovery mode {mode.value} with resilience {resilience_score}/100 and {len(plan)} planned step(s).",
    )


def detect_recovery_risks(
    recovery_input: RecoveryResilienceInput | None = None,
    *,
    score_breakdown: ResilienceScore | None = None,
    **kwargs,
) -> tuple[RecoveryRisk, ...]:
    """Detect recovery and resilience risks from available offline layers."""
    data = _input(recovery_input, **kwargs)
    scores = score_breakdown or compute_resilience_score(data)
    risks: list[RecoveryRisk] = []

    if data.system_integrity is not None:
        if data.system_integrity.status in {SystemIntegrityStatus.COMPROMISED, SystemIntegrityStatus.PROTECTION_MODE}:
            risks.append(RecoveryRisk.SYSTEM_COMPROMISED)
        if data.system_integrity.status == SystemIntegrityStatus.ROLLBACK_RECOMMENDED or data.system_integrity.recommended_action == "ROLLBACK_RECOMMENDED":
            risks.append(RecoveryRisk.ROLLBACK_REQUIRED)
        if data.system_integrity.modules_to_isolate:
            risks.append(RecoveryRisk.MODULE_INSTABILITY)

    if data.self_evaluation is not None:
        if data.self_evaluation.confidence_score < 50:
            risks.append(RecoveryRisk.LOW_CONFIDENCE)
        if data.self_evaluation.autonomy_recommendation in {
            SystemAutonomyRecommendation.FREEZE_AUTONOMY,
            SystemAutonomyRecommendation.REQUIRE_HUMAN_REVIEW,
            SystemAutonomyRecommendation.RECALIBRATE_SYSTEM,
        }:
            risks.append(RecoveryRisk.LOW_CONFIDENCE)

    if data.learning_governance is not None and (
        data.learning_governance.mode in {LearningGovernanceMode.SAFETY_LOCKDOWN, LearningGovernanceMode.FREEZE_LEARNING}
        or data.learning_governance.decision in {
            LearningGovernanceDecision.ENTER_SAFETY_LOCKDOWN,
            LearningGovernanceDecision.FREEZE_POLICY_UPDATE,
            LearningGovernanceDecision.LOCK_DANGEROUS_POLICY,
        }
    ):
        risks.append(RecoveryRisk.GOVERNANCE_LOCKDOWN)

    if data.cognitive_adaptation is not None and data.cognitive_adaptation.load_level == CognitiveLoadLevel.OVERLOADED:
        risks.append(RecoveryRisk.COGNITIVE_OVERLOAD)

    if data.behavioral_stability is not None and (
        data.behavioral_stability.pressure_level == BehavioralPressureLevel.EXTREME
        or data.behavioral_stability.recovery_state in {BehavioralRecoveryState.DETERIORATING, BehavioralRecoveryState.CRITICAL}
        or data.behavioral_stability.stability_score < 45
    ):
        risks.append(RecoveryRisk.BEHAVIORAL_SPIRAL)

    if data.strategic_timeline_analysis is not None and (
        data.strategic_timeline_analysis.strategic_health_score < 45
        or data.strategic_timeline_analysis.degradation_detected
        or StrategicDriftSignal.STRATEGIC_DEGRADATION in data.strategic_timeline_analysis.drift_signals
    ):
        risks.append(RecoveryRisk.STRATEGIC_COLLAPSE)

    if data.strategic_result is not None and data.strategic_result.plan.status in {
        StrategicPlanStatus.PAUSED,
        StrategicPlanStatus.RECOVERY,
        StrategicPlanStatus.REVIEW_REQUIRED,
    }:
        risks.append(RecoveryRisk.STRATEGIC_COLLAPSE)

    if _dangerous_policies(data):
        risks.append(RecoveryRisk.POLICY_FAILURE)

    if data.replay_arena is not None and (
        data.replay_arena.status == ReplayArenaStatus.BLOCKED_BY_SAFETY
        or data.replay_arena.robustness_score < 40
    ):
        risks.append(RecoveryRisk.RECOVERY_FAILURE)

    if scores.module_stability_score < 45:
        risks.append(RecoveryRisk.MODULE_INSTABILITY)

    return tuple(dict.fromkeys(risks))


def build_recovery_plan(
    recovery_input: RecoveryResilienceInput | None = None,
    *,
    risks: tuple[RecoveryRisk, ...] | None = None,
    **kwargs,
) -> tuple[RecoveryStep, ...]:
    """Build an ordered recovery plan without mutating external state."""
    data = _input(recovery_input, **kwargs)
    resolved_risks = risks or detect_recovery_risks(data)
    steps: list[RecoveryStep] = []

    if not resolved_risks:
        steps.append(_step(steps, RecoveryAction.KEEP_RUNNING, "system", "System resilience is stable."))
        if _rebuild_ready(data):
            steps.append(_step(steps, RecoveryAction.REBUILD_GRADUALLY, "system", "Stability is returning; rebuild confidence gradually."))
        return tuple(steps)

    if RecoveryRisk.SYSTEM_COMPROMISED in resolved_risks:
        steps.append(_step(steps, RecoveryAction.ENTER_SURVIVAL_MODE, "system", "System integrity is compromised or in protection mode."))
    if RecoveryRisk.ROLLBACK_REQUIRED in resolved_risks:
        steps.append(_step(steps, RecoveryAction.RESTORE_LAST_STABLE_STATE, "system", "Integrity layer recommends rollback."))
    if RecoveryRisk.GOVERNANCE_LOCKDOWN in resolved_risks:
        steps.append(_step(steps, RecoveryAction.FREEZE_LEARNING, "learning_governance", "Learning governance is frozen or locked down."))
    if RecoveryRisk.LOW_CONFIDENCE in resolved_risks:
        steps.append(_step(steps, RecoveryAction.REDUCE_AUTONOMY, "autonomy", "Self-evaluation confidence or autonomy recommendation is unsafe."))
    for module_name in _modules_to_isolate(data):
        steps.append(_step(steps, RecoveryAction.ISOLATE_UNSTABLE_MODULE, module_name, "Module health report recommends isolation."))
    for policy_name in _dangerous_policies(data):
        steps.append(_step(steps, RecoveryAction.DISABLE_DANGEROUS_POLICY, policy_name, "Policy memory marks policy as dangerous or disabled."))
    if _critical_count(resolved_risks) >= 3:
        steps.append(_step(steps, RecoveryAction.REQUIRE_HUMAN_REVIEW, "recovery", "Multiple critical recovery risks are active."))
    if RecoveryRisk.RECOVERY_FAILURE not in resolved_risks and _rebuild_ready(data):
        steps.append(_step(steps, RecoveryAction.REBUILD_GRADUALLY, "system", "Partial stability allows gradual rebuilding."))

    return tuple(steps)


def compute_resilience_score(
    recovery_input: RecoveryResilienceInput | None = None,
    **kwargs,
) -> ResilienceScore:
    """Compute recovery resilience component scores from 0..100."""
    data = _input(recovery_input, **kwargs)
    system_integrity = 75
    module_stability = 75
    strategic = 75
    behavioral = 75
    cognitive = 75
    governance = 75
    policy = 75

    if data.system_integrity is not None:
        system_integrity = data.system_integrity.integrity_score
        if data.system_integrity.module_reports:
            module_stability = int(round(sum(report.health_score for report in data.system_integrity.module_reports) / len(data.system_integrity.module_reports)))
        if data.system_integrity.modules_to_isolate:
            module_stability -= min(35, len(data.system_integrity.modules_to_isolate) * 12)

    if data.strategic_timeline_analysis is not None:
        strategic = data.strategic_timeline_analysis.strategic_health_score
        if data.strategic_timeline_analysis.degradation_detected:
            strategic -= 15
    if data.strategic_result is not None:
        strategic = min(strategic, data.strategic_result.progress_score)
        if data.strategic_result.plan.status in {StrategicPlanStatus.PAUSED, StrategicPlanStatus.RECOVERY, StrategicPlanStatus.REVIEW_REQUIRED}:
            strategic -= 12

    if data.behavioral_stability is not None:
        behavioral = data.behavioral_stability.stability_score
        if data.behavioral_stability.pressure_level == BehavioralPressureLevel.EXTREME:
            behavioral -= 20
        if data.behavioral_stability.recovery_state in {BehavioralRecoveryState.DETERIORATING, BehavioralRecoveryState.CRITICAL}:
            behavioral -= 20

    if data.cognitive_adaptation is not None:
        cognitive = data.cognitive_adaptation.global_score
        if data.cognitive_adaptation.load_level == CognitiveLoadLevel.OVERLOADED:
            cognitive -= 25
        elif data.cognitive_adaptation.load_level == CognitiveLoadLevel.HIGH:
            cognitive -= 10

    if data.learning_governance is not None:
        if data.learning_governance.mode == LearningGovernanceMode.SAFETY_LOCKDOWN:
            governance = 20
        elif data.learning_governance.mode == LearningGovernanceMode.FREEZE_LEARNING:
            governance = 35
        elif data.learning_governance.decision == LearningGovernanceDecision.ALLOW_LIMITED_LEARNING:
            governance = 65

    if data.self_evaluation is not None:
        system_integrity = min(system_integrity, data.self_evaluation.confidence_score + 5)
        if data.self_evaluation.status in {SelfEvaluationStatus.CONTRADICTORY, SelfEvaluationStatus.UNSTABLE}:
            system_integrity -= 15

    if data.policy_memory is not None:
        dangerous = _dangerous_policies(data)
        policy -= min(45, len(dangerous) * 15)
        if data.policy_memory.entries:
            avg_confidence = int(round(sum(entry.confidence_score for entry in data.policy_memory.entries.values()) / len(data.policy_memory.entries)))
            policy = min(policy, avg_confidence)

    if data.replay_arena is not None:
        policy = min(policy, data.replay_arena.robustness_score)
        if data.replay_arena.status == ReplayArenaStatus.BLOCKED_BY_SAFETY:
            policy -= 20

    return ResilienceScore(
        system_integrity_score=_clamp(system_integrity),
        module_stability_score=_clamp(module_stability),
        strategic_resilience_score=_clamp(strategic),
        behavioral_resilience_score=_clamp(behavioral),
        cognitive_resilience_score=_clamp(cognitive),
        governance_resilience_score=_clamp(governance),
        policy_resilience_score=_clamp(policy),
    )


def render_recovery_resilience_markdown(result: RecoveryResilienceResult) -> str:
    """Render recovery and resilience result as Markdown."""
    lines = [
        "# Autonomous Recovery & Resilience Engine",
        "",
        "## Mode recuperation",
        "",
        f"- {result.mode.value}",
        "",
        "## Score resilience",
        "",
        f"- {result.resilience_score}/100",
        "",
        "## Risques detectes",
        "",
        *_bullet_lines(tuple(risk.value for risk in result.risks)),
        "",
        "## Actions recovery",
        "",
        *_bullet_lines(tuple(action.value for action in result.actions)),
        "",
        "## Modules isoles",
        "",
        *_bullet_lines(result.isolated_modules),
        "",
        "## Politiques desactivees",
        "",
        *_bullet_lines(result.disabled_policies),
        "",
        "## Plan de reconstruction",
        "",
        *_plan_lines(result.recovery_plan),
        "",
        "## Recommandations AGIcore",
        "",
        *_bullet_lines(result.recommendations),
        "",
        "- Offline only: no broker, no real order, no external ML, no neural training.",
        "",
    ]
    return "\n".join(lines)


def _mode(
    data: RecoveryResilienceInput,
    risks: tuple[RecoveryRisk, ...],
    plan: tuple[RecoveryStep, ...],
    scores: ResilienceScore,
) -> RecoveryMode:
    if _critical_count(risks) >= 4 or RecoveryRisk.RECOVERY_FAILURE in risks:
        return RecoveryMode.PAUSED_RECOVERY
    if RecoveryRisk.ROLLBACK_REQUIRED in risks:
        return RecoveryMode.STRATEGIC_ROLLBACK
    if RecoveryRisk.SYSTEM_COMPROMISED in risks:
        return RecoveryMode.SURVIVAL_MODE
    if any(step.action == RecoveryAction.ISOLATE_UNSTABLE_MODULE for step in plan):
        return RecoveryMode.ISOLATE_MODULES
    if RecoveryRisk.COGNITIVE_OVERLOAD in risks or RecoveryRisk.GOVERNANCE_LOCKDOWN in risks:
        return RecoveryMode.REDUCE_COMPLEXITY
    if risks:
        return RecoveryMode.STABILIZE
    if _rebuild_ready(data) and _global_resilience(scores, risks) < 90:
        return RecoveryMode.REBUILD_CONFIDENCE
    return RecoveryMode.NORMAL


def _global_resilience(scores: ResilienceScore, risks: tuple[RecoveryRisk, ...]) -> int:
    values = (
        scores.system_integrity_score,
        scores.module_stability_score,
        scores.strategic_resilience_score,
        scores.behavioral_resilience_score,
        scores.cognitive_resilience_score,
        scores.governance_resilience_score,
        scores.policy_resilience_score,
    )
    score = int(round(sum(values) / len(values)))
    score -= 5 * len(risks)
    score -= 5 * _critical_count(risks)
    return _clamp(score)


def _modules_to_isolate(data: RecoveryResilienceInput) -> tuple[str, ...]:
    modules: list[str] = []
    if data.system_integrity is not None:
        modules.extend(data.system_integrity.modules_to_isolate)
        modules.extend(
            report.module_name
            for report in data.system_integrity.module_reports
            if report.isolate_recommended or report.health_status in {ModuleHealthStatus.BLOCKED, ModuleHealthStatus.ISOLATE}
        )
    return tuple(dict.fromkeys(modules))


def _dangerous_policies(data: RecoveryResilienceInput) -> tuple[str, ...]:
    if data.policy_memory is None:
        return ()
    policies = list(data.policy_memory.disabled_policies)
    policies.extend(
        name
        for name, entry in data.policy_memory.entries.items()
        if entry.recommendation == PolicyMemoryRecommendation.DISABLE_POLICY
        or entry.dangerous_decision_rate >= 0.25
        or entry.confidence_score < 35
    )
    return tuple(dict.fromkeys(policies))


def _rebuild_ready(data: RecoveryResilienceInput) -> bool:
    return bool(
        (data.self_evaluation is None or data.self_evaluation.confidence_score >= 65)
        and (data.behavioral_stability is None or data.behavioral_stability.stability_score >= 65)
        and (data.cognitive_adaptation is None or data.cognitive_adaptation.load_level in {CognitiveLoadLevel.LOW, CognitiveLoadLevel.MODERATE})
        and (data.system_integrity is None or data.system_integrity.integrity_score >= 65)
    )


def _recommendations(
    mode: RecoveryMode,
    risks: tuple[RecoveryRisk, ...],
    plan: tuple[RecoveryStep, ...],
) -> tuple[str, ...]:
    recommendations: list[str] = []
    if mode == RecoveryMode.NORMAL:
        recommendations.append("Keep monitored offline operation active.")
    elif mode == RecoveryMode.REBUILD_CONFIDENCE:
        recommendations.append("Rebuild autonomy gradually with conservative thresholds.")
    elif mode == RecoveryMode.STRATEGIC_ROLLBACK:
        recommendations.append("Restore the last stable logical state before resuming strategy selection.")
    elif mode == RecoveryMode.SURVIVAL_MODE:
        recommendations.append("Enter survival mode and prioritize capital/system preservation.")
    elif mode == RecoveryMode.PAUSED_RECOVERY:
        recommendations.append("Pause recovery and require human review before further adaptation.")
    else:
        recommendations.append("Stabilize the stack before allowing autonomous escalation.")
    if any(step.action == RecoveryAction.ISOLATE_UNSTABLE_MODULE for step in plan):
        recommendations.append("Keep isolated modules out of the decision path until health improves.")
    if RecoveryRisk.GOVERNANCE_LOCKDOWN in risks:
        recommendations.append("Keep learning frozen until governance lock clears.")
    if RecoveryRisk.POLICY_FAILURE in risks:
        recommendations.append("Disable dangerous policies in offline selection memory.")
    return tuple(dict.fromkeys(recommendations))


def _critical_count(risks: tuple[RecoveryRisk, ...]) -> int:
    return sum(1 for risk in risks if risk in _critical_risks())


def _critical_risks() -> set[RecoveryRisk]:
    return {
        RecoveryRisk.SYSTEM_COMPROMISED,
        RecoveryRisk.STRATEGIC_COLLAPSE,
        RecoveryRisk.BEHAVIORAL_SPIRAL,
        RecoveryRisk.COGNITIVE_OVERLOAD,
        RecoveryRisk.GOVERNANCE_LOCKDOWN,
        RecoveryRisk.ROLLBACK_REQUIRED,
        RecoveryRisk.RECOVERY_FAILURE,
    }


def _step(
    steps: list[RecoveryStep],
    action: RecoveryAction,
    target: str,
    reason: str,
) -> RecoveryStep:
    return RecoveryStep(len(steps) + 1, action, target, reason)


def _plan_lines(plan: tuple[RecoveryStep, ...]) -> list[str]:
    if not plan:
        return ["- None"]
    return [f"- {step.order}. {step.action.value} -> {step.target}: {step.reason}" for step in plan]


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _input(recovery_input: RecoveryResilienceInput | None = None, **kwargs: Any) -> RecoveryResilienceInput:
    if recovery_input is not None:
        return recovery_input
    return RecoveryResilienceInput(**kwargs)


def _clamp(value: int | float) -> int:
    return max(0, min(100, int(round(value))))


__all__ = [
    "build_recovery_plan",
    "compute_resilience_score",
    "detect_recovery_risks",
    "evaluate_recovery_resilience",
    "render_recovery_resilience_markdown",
]
