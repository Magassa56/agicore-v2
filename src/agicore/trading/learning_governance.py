"""Offline Autonomous Learning Governance Core for AGIcore Trading."""
from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from typing import Any

from .adaptive_policy_memory_models import PolicyMemoryRecommendation
from .behavioral_stability_models import BehavioralPressureLevel, BehavioralRecoveryState
from .cognitive_adaptation_models import CognitiveAdaptationMode, CognitiveAdaptationSignal, CognitiveLoadLevel
from .executive_brain_models import ExecutiveMode
from .learning_governance_models import (
    LearningCycleStatus,
    LearningGovernanceDecision,
    LearningGovernanceEvent,
    LearningGovernanceInput,
    LearningGovernanceMode,
    LearningGovernanceResult,
    LearningGovernanceRisk,
)
from .meta_strategy_models import MetaStrategyDecision
from .reward_models import RewardLabel
from .safe_rl_models import SafeRLStatus
from .strategic_memory_models import StrategicDriftSignal
from .strategic_planning_models import StrategicPlanStatus
from .tactical_execution_models import TacticalExecutionQuality


def detect_learning_risks(
    governance_input: LearningGovernanceInput | None = None,
    **kwargs,
) -> tuple[LearningGovernanceRisk, ...]:
    """Detect risks before permitting offline autonomous learning."""
    data = _input(governance_input, **kwargs)
    risks: list[LearningGovernanceRisk] = []
    if _overfitting_risk(data):
        risks.append(LearningGovernanceRisk.OVERFITTING_RISK)
    if _policy_drift_risk(data):
        risks.append(LearningGovernanceRisk.POLICY_DRIFT_RISK)
    if _reward_hacking_risk(data):
        risks.append(LearningGovernanceRisk.REWARD_HACKING_RISK)
    if _behavioral_instability(data):
        risks.append(LearningGovernanceRisk.BEHAVIORAL_INSTABILITY)
    if _cognitive_overload(data):
        risks.append(LearningGovernanceRisk.COGNITIVE_OVERLOAD)
    if _low_dataset_quality(data):
        risks.append(LearningGovernanceRisk.LOW_DATASET_QUALITY)
    if _unsafe_rl_status(data):
        risks.append(LearningGovernanceRisk.UNSAFE_RL_STATUS)
    if _strategic_degradation(data):
        risks.append(LearningGovernanceRisk.STRATEGIC_DEGRADATION)
    if _tactical_deterioration(data):
        risks.append(LearningGovernanceRisk.TACTICAL_DETERIORATION)
    if _excessive_adaptation(data):
        risks.append(LearningGovernanceRisk.EXCESSIVE_ADAPTATION)
    if _insufficient_evidence(data):
        risks.append(LearningGovernanceRisk.INSUFFICIENT_EVIDENCE)
    return tuple(dict.fromkeys(risks))


def decide_learning_mode(
    governance_input: LearningGovernanceInput | None = None,
    **kwargs,
) -> LearningGovernanceMode:
    """Select the governance mode for offline learning."""
    data = _input(governance_input, **kwargs)
    risks = detect_learning_risks(data)
    critical_count = sum(1 for risk in risks if risk in _critical_risks())

    if critical_count >= 2 or _executive_lockdown(data):
        return LearningGovernanceMode.SAFETY_LOCKDOWN
    if LearningGovernanceRisk.UNSAFE_RL_STATUS in risks or LearningGovernanceRisk.COGNITIVE_OVERLOAD in risks:
        return LearningGovernanceMode.FREEZE_LEARNING
    if LearningGovernanceRisk.BEHAVIORAL_INSTABILITY in risks:
        return LearningGovernanceMode.RECOVERY_MODE
    if LearningGovernanceRisk.LOW_DATASET_QUALITY in risks or LearningGovernanceRisk.INSUFFICIENT_EVIDENCE in risks:
        return LearningGovernanceMode.OBSERVE_ONLY
    if LearningGovernanceRisk.EXCESSIVE_ADAPTATION in risks or LearningGovernanceRisk.POLICY_DRIFT_RISK in risks:
        return LearningGovernanceMode.REDUCE_ADAPTATION
    if _stable_exploit_context(data, risks):
        return LearningGovernanceMode.EXPLOIT_ONLY
    if _learning_allowed(data, risks):
        return LearningGovernanceMode.LEARN
    return LearningGovernanceMode.OBSERVE_ONLY


def evaluate_learning_governance(
    governance_input: LearningGovernanceInput | None = None,
    **kwargs,
) -> LearningGovernanceResult:
    """Evaluate governance decision for offline learning and policy updates."""
    data = _input(governance_input, **kwargs)
    risks = detect_learning_risks(data)
    mode = decide_learning_mode(data)
    locked = _locked_policies(data, risks)
    decision = _decision_for(mode, risks, locked)
    status = _cycle_status_for(mode, decision)
    event = LearningGovernanceEvent(
        decision=decision,
        mode=mode,
        message=f"Learning governance mode {mode.value}; decision {decision.value}.",
        timestamp=datetime.now(UTC),
    )
    return LearningGovernanceResult(
        decision=decision,
        mode=mode,
        cycle_status=status,
        risks=risks,
        locked_policies=locked,
        learning_conditions=_learning_conditions(mode, risks),
        recommended_actions=_recommended_actions(mode, decision, risks, locked),
        events=(event,),
        safety_summary=_safety_summary(mode, decision, risks),
    )


def render_learning_governance_markdown(result: LearningGovernanceResult) -> str:
    """Render learning governance result as Markdown."""
    lines = [
        "# Autonomous Learning Governance Core",
        "",
        "## Decision gouvernance",
        "",
        f"- {result.decision.value}",
        f"- Cycle status: {result.cycle_status.value}",
        "",
        "## Mode apprentissage",
        "",
        f"- {result.mode.value}",
        "",
        "## Risques detectes",
        "",
        *_bullet_lines(tuple(risk.value for risk in result.risks)),
        "",
        "## Politiques verrouillees",
        "",
        *_bullet_lines(result.locked_policies),
        "",
        "## Conditions d'apprentissage",
        "",
        *_bullet_lines(result.learning_conditions),
        "",
        "## Actions recommandees",
        "",
        *_bullet_lines(result.recommended_actions),
        "",
        "## Securite AGIcore",
        "",
        f"- {result.safety_summary}",
        "- Offline only: no broker, no real order, no external ML, no neural training.",
        "",
    ]
    return "\n".join(lines)


def _decision_for(
    mode: LearningGovernanceMode,
    risks: tuple[LearningGovernanceRisk, ...],
    locked: tuple[str, ...],
) -> LearningGovernanceDecision:
    if mode == LearningGovernanceMode.SAFETY_LOCKDOWN:
        return LearningGovernanceDecision.ENTER_SAFETY_LOCKDOWN
    if locked:
        return LearningGovernanceDecision.LOCK_DANGEROUS_POLICY
    if mode == LearningGovernanceMode.FREEZE_LEARNING:
        return LearningGovernanceDecision.FREEZE_POLICY_UPDATE
    if mode == LearningGovernanceMode.RECOVERY_MODE:
        return LearningGovernanceDecision.PAUSE_LEARNING
    if LearningGovernanceRisk.EXCESSIVE_ADAPTATION in risks or LearningGovernanceRisk.POLICY_DRIFT_RISK in risks:
        return LearningGovernanceDecision.ALLOW_LIMITED_LEARNING
    if mode in {LearningGovernanceMode.OBSERVE_ONLY, LearningGovernanceMode.REDUCE_ADAPTATION}:
        return LearningGovernanceDecision.ALLOW_LIMITED_LEARNING
    if mode == LearningGovernanceMode.EXPLOIT_ONLY:
        return LearningGovernanceDecision.FREEZE_POLICY_UPDATE
    if mode == LearningGovernanceMode.LEARN:
        return LearningGovernanceDecision.ALLOW_LEARNING
    return LearningGovernanceDecision.REQUIRE_HUMAN_REVIEW


def _cycle_status_for(mode: LearningGovernanceMode, decision: LearningGovernanceDecision) -> LearningCycleStatus:
    if decision == LearningGovernanceDecision.ENTER_SAFETY_LOCKDOWN:
        return LearningCycleStatus.LOCKED_DOWN
    if decision == LearningGovernanceDecision.REQUIRE_HUMAN_REVIEW:
        return LearningCycleStatus.HUMAN_REVIEW_REQUIRED
    if mode == LearningGovernanceMode.LEARN:
        return LearningCycleStatus.READY
    if mode in {LearningGovernanceMode.OBSERVE_ONLY, LearningGovernanceMode.EXPLOIT_ONLY}:
        return LearningCycleStatus.OBSERVING
    if mode in {LearningGovernanceMode.FREEZE_LEARNING, LearningGovernanceMode.REDUCE_ADAPTATION}:
        return LearningCycleStatus.FROZEN if mode == LearningGovernanceMode.FREEZE_LEARNING else LearningCycleStatus.LIMITED
    if mode == LearningGovernanceMode.RECOVERY_MODE:
        return LearningCycleStatus.RECOVERY
    return LearningCycleStatus.LIMITED


def _overfitting_risk(data: LearningGovernanceInput) -> bool:
    if data.rl_playground is None:
        return False
    if len(data.rl_playground.ranked_scores) <= 1 and data.rl_playground.best_policy is not None:
        return True
    if data.policy_memory is None or not data.policy_memory.entries:
        return False
    total = sum(entry.total_evaluations for entry in data.policy_memory.entries.values())
    if total == 0:
        return False
    top = max(entry.total_evaluations for entry in data.policy_memory.entries.values())
    return bool(top / total > 0.75 and len(data.policy_memory.entries) <= 2)


def _policy_drift_risk(data: LearningGovernanceInput) -> bool:
    if data.meta_strategy is not None and data.meta_strategy.decision in {MetaStrategyDecision.NO_STRATEGY, MetaStrategyDecision.BLOCK_ALL_POLICIES}:
        return True
    if data.strategic_timeline_analysis is not None and StrategicDriftSignal.DANGEROUS_POLICY in data.strategic_timeline_analysis.drift_signals:
        return True
    return False


def _reward_hacking_risk(data: LearningGovernanceInput) -> bool:
    high_reward = data.reward_evaluation is not None and data.reward_evaluation.normalized_reward >= 85
    tactical_bad = data.tactical_execution is not None and data.tactical_execution.quality in {TacticalExecutionQuality.WEAK, TacticalExecutionQuality.DANGEROUS}
    dangerous_dataset = data.dataset_quality is not None and data.dataset_quality.dangerous_decision_count > 0
    dangerous_policy = any(entry.dangerous_decision_rate > 0.2 for entry in (data.policy_memory.entries.values() if data.policy_memory else ()))
    return bool(high_reward and (tactical_bad or dangerous_dataset or dangerous_policy))


def _behavioral_instability(data: LearningGovernanceInput) -> bool:
    return bool(
        data.behavioral_stability is not None
        and (
            data.behavioral_stability.stability_score < 50
            or data.behavioral_stability.pressure_level in {BehavioralPressureLevel.HIGH, BehavioralPressureLevel.EXTREME}
            or data.behavioral_stability.recovery_state in {BehavioralRecoveryState.DETERIORATING, BehavioralRecoveryState.CRITICAL}
        )
    )


def _cognitive_overload(data: LearningGovernanceInput) -> bool:
    return bool(
        data.cognitive_adaptation is not None
        and (
            data.cognitive_adaptation.load_level == CognitiveLoadLevel.OVERLOADED
            or data.cognitive_adaptation.adaptation_mode == CognitiveAdaptationMode.PAUSE
            or CognitiveAdaptationSignal.COGNITIVE_OVERLOAD in data.cognitive_adaptation.signals
        )
    )


def _low_dataset_quality(data: LearningGovernanceInput) -> bool:
    return bool(data.dataset_quality is not None and (data.dataset_quality.quality_score < 60 or data.dataset_quality.transitions_count < 10))


def _unsafe_rl_status(data: LearningGovernanceInput) -> bool:
    return bool(data.safe_rl_result is not None and data.safe_rl_result.status in {SafeRLStatus.BLOCKED, SafeRLStatus.REVIEW_REQUIRED})


def _strategic_degradation(data: LearningGovernanceInput) -> bool:
    if data.strategic_timeline_analysis is not None and data.strategic_timeline_analysis.degradation_detected:
        return True
    if data.strategic_result is not None and data.strategic_result.plan.status in {StrategicPlanStatus.PAUSED, StrategicPlanStatus.RECOVERY}:
        return True
    return False


def _tactical_deterioration(data: LearningGovernanceInput) -> bool:
    return bool(data.tactical_execution is not None and data.tactical_execution.quality in {TacticalExecutionQuality.WEAK, TacticalExecutionQuality.DANGEROUS})


def _excessive_adaptation(data: LearningGovernanceInput) -> bool:
    if data.cognitive_adaptation is not None and CognitiveAdaptationSignal.OVER_REACTION_RISK in data.cognitive_adaptation.signals:
        return True
    if data.policy_memory is None or len(data.policy_memory.snapshots) < 4:
        return False
    recent = data.policy_memory.snapshots[-5:]
    unique_policies = {snapshot.policy_name for snapshot in recent}
    return bool(len(unique_policies) >= 4)


def _insufficient_evidence(data: LearningGovernanceInput) -> bool:
    missing = sum(
        item is None
        for item in (
            data.dataset_quality,
            data.reward_evaluation,
            data.rl_playground,
            data.policy_memory,
        )
    )
    return bool(missing >= 3)


def _locked_policies(
    data: LearningGovernanceInput,
    risks: tuple[LearningGovernanceRisk, ...],
) -> tuple[str, ...]:
    locked: list[str] = []
    if data.policy_memory is not None:
        locked.extend(data.policy_memory.disabled_policies)
        for entry in data.policy_memory.entries.values():
            if entry.recommendation == PolicyMemoryRecommendation.DISABLE_POLICY or entry.dangerous_decision_rate >= 0.2:
                locked.append(entry.policy_name)
    if LearningGovernanceRisk.POLICY_DRIFT_RISK in risks and data.meta_strategy is not None and data.meta_strategy.selected_policy_name:
        locked.append(data.meta_strategy.selected_policy_name)
    return tuple(dict.fromkeys(locked))


def _stable_exploit_context(
    data: LearningGovernanceInput,
    risks: tuple[LearningGovernanceRisk, ...],
) -> bool:
    no_critical = not any(risk in risks for risk in _critical_risks())
    stable_cognitive = data.cognitive_adaptation is not None and data.cognitive_adaptation.adaptation_mode == CognitiveAdaptationMode.EXPLOIT_STABLE_PATTERN
    positive_reward = data.reward_evaluation is not None and data.reward_evaluation.reward_label in {RewardLabel.GOOD_DECISION, RewardLabel.EXCELLENT_DECISION}
    return bool(no_critical and stable_cognitive and positive_reward)


def _learning_allowed(
    data: LearningGovernanceInput,
    risks: tuple[LearningGovernanceRisk, ...],
) -> bool:
    if risks:
        return False
    dataset_ok = data.dataset_quality is not None and data.dataset_quality.quality_score >= 70 and data.dataset_quality.transitions_count >= 10
    behavior_ok = data.behavioral_stability is None or data.behavioral_stability.stability_score >= 70
    reward_ok = data.reward_evaluation is not None and data.reward_evaluation.reward_label in {RewardLabel.GOOD_DECISION, RewardLabel.EXCELLENT_DECISION}
    safe_ok = data.safe_rl_result is None or data.safe_rl_result.status == SafeRLStatus.SAFE
    return bool(dataset_ok and behavior_ok and reward_ok and safe_ok)


def _executive_lockdown(data: LearningGovernanceInput) -> bool:
    return bool(data.executive_result is not None and data.executive_result.state.mode in {ExecutiveMode.SURVIVAL, ExecutiveMode.PAUSED})


def _critical_risks() -> set[LearningGovernanceRisk]:
    return {
        LearningGovernanceRisk.UNSAFE_RL_STATUS,
        LearningGovernanceRisk.COGNITIVE_OVERLOAD,
        LearningGovernanceRisk.BEHAVIORAL_INSTABILITY,
        LearningGovernanceRisk.STRATEGIC_DEGRADATION,
        LearningGovernanceRisk.REWARD_HACKING_RISK,
        LearningGovernanceRisk.POLICY_DRIFT_RISK,
    }


def _learning_conditions(mode: LearningGovernanceMode, risks: tuple[LearningGovernanceRisk, ...]) -> tuple[str, ...]:
    if mode == LearningGovernanceMode.LEARN:
        return ("Dataset quality >= 70.", "Behavioral stability acceptable.", "Safe RL allows offline experiments.", "Reward quality positive.")
    if mode == LearningGovernanceMode.EXPLOIT_ONLY:
        return ("Exploit stable pattern only.", "No policy update.", "Continue offline monitoring.")
    if mode == LearningGovernanceMode.OBSERVE_ONLY:
        return ("Collect more evidence.", "Do not update policies.", "Review dataset and reward coverage.")
    if mode == LearningGovernanceMode.RECOVERY_MODE:
        return ("Learning paused during recovery.", "Use review-only workflows.", "Rebuild behavioral stability first.")
    if mode == LearningGovernanceMode.FREEZE_LEARNING:
        return ("Freeze policy updates.", "Resolve safety/cognitive blockers.", "No autonomous learning changes.")
    if mode == LearningGovernanceMode.SAFETY_LOCKDOWN:
        return ("All learning blocked.", "Human review required.", "Safety risks must clear first.")
    return tuple(f"Risk present: {risk.value}" for risk in risks) or ("Limited offline learning only.",)


def _recommended_actions(
    mode: LearningGovernanceMode,
    decision: LearningGovernanceDecision,
    risks: tuple[LearningGovernanceRisk, ...],
    locked: tuple[str, ...],
) -> tuple[str, ...]:
    actions: list[str] = []
    if decision == LearningGovernanceDecision.ENTER_SAFETY_LOCKDOWN:
        actions.append("Enter safety lockdown and stop learning updates.")
    if locked:
        actions.append("Lock dangerous policies and require review before reuse.")
    if LearningGovernanceRisk.LOW_DATASET_QUALITY in risks or LearningGovernanceRisk.INSUFFICIENT_EVIDENCE in risks:
        actions.append("Collect more offline transitions before learning.")
    if LearningGovernanceRisk.REWARD_HACKING_RISK in risks:
        actions.append("Audit reward components against tactical and safety violations.")
    if LearningGovernanceRisk.OVERFITTING_RISK in risks:
        actions.append("Increase policy diversity before policy updates.")
    if mode == LearningGovernanceMode.RECOVERY_MODE:
        actions.append("Switch to recovery mode and reduce adaptation.")
    if mode == LearningGovernanceMode.LEARN:
        actions.append("Allow offline learning governance cycle.")
    return tuple(dict.fromkeys(actions or ("Continue observation and keep all learning offline.",)))


def _safety_summary(
    mode: LearningGovernanceMode,
    decision: LearningGovernanceDecision,
    risks: tuple[LearningGovernanceRisk, ...],
) -> str:
    if mode == LearningGovernanceMode.SAFETY_LOCKDOWN:
        return "Critical risks detected; autonomous learning is locked down."
    if risks:
        return f"{len(risks)} governance risk(s) detected; learning is constrained."
    if decision == LearningGovernanceDecision.ALLOW_LEARNING:
        return "Learning allowed offline under safety constraints."
    return "Learning remains constrained and offline-only."


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _input(governance_input: LearningGovernanceInput | None = None, **kwargs: Any) -> LearningGovernanceInput:
    if governance_input is not None:
        return governance_input
    return LearningGovernanceInput(**kwargs)


__all__ = [
    "decide_learning_mode",
    "detect_learning_risks",
    "evaluate_learning_governance",
    "render_learning_governance_markdown",
]
