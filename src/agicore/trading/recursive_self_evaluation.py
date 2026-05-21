"""Offline Recursive Self-Evaluation Engine for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .behavioral_stability_models import BehavioralPressureLevel, BehavioralRecoveryState
from .cognitive_adaptation_models import CognitiveAdaptationMode, CognitiveLoadLevel
from .executive_brain_models import ExecutiveMode
from .hierarchical_supervisor_models import SupervisorDecision, SupervisorOverride
from .learning_governance_models import LearningGovernanceDecision, LearningGovernanceMode
from .meta_strategy_models import MetaStrategyDecision
from .multi_agent_models import AgentConsensusStatus, AgentVote
from .recursive_self_evaluation_models import (
    SelfEvaluationEvent,
    SelfEvaluationInput,
    SelfEvaluationResult,
    SelfEvaluationScore,
    SelfEvaluationSignal,
    SelfEvaluationStatus,
    SystemAutonomyRecommendation,
)
from .reward_models import RewardLabel
from .scenario_replay_models import ReplayArenaStatus
from .strategic_memory_models import StrategicDriftSignal
from .strategic_planning_models import StrategicPlanStatus
from .tactical_execution_models import TacticalExecutionQuality


def detect_internal_contradictions(
    evaluation_input: SelfEvaluationInput | None = None,
    **kwargs,
) -> tuple[str, ...]:
    """Detect contradictions between decision layers."""
    data = _input(evaluation_input, **kwargs)
    contradictions: list[str] = []
    if (
        data.executive_result is not None
        and data.executive_result.decision.allow_execution
        and data.supervisor_result is not None
        and not data.supervisor_result.final_executable
    ):
        contradictions.append("Executive Brain allows execution while Supervisor blocks final execution.")
    if (
        data.learning_governance is not None
        and data.learning_governance.decision == LearningGovernanceDecision.ALLOW_LEARNING
        and data.supervisor_result is not None
        and not data.supervisor_result.final_executable
    ):
        contradictions.append("Learning Governance allows learning while Supervisor blocks the system.")
    if (
        data.learning_governance is not None
        and data.learning_governance.decision == LearningGovernanceDecision.ALLOW_LEARNING
        and data.learning_governance.mode == LearningGovernanceMode.SAFETY_LOCKDOWN
    ):
        contradictions.append("Learning decision allows learning while governance mode is SAFETY_LOCKDOWN.")
    if (
        data.meta_strategy is not None
        and data.meta_strategy.decision == MetaStrategyDecision.BLOCK_ALL_POLICIES
        and data.executive_result is not None
        and data.executive_result.decision.allow_execution
    ):
        contradictions.append("Meta Strategy blocks all policies while Executive Brain allows execution.")
    if (
        data.agent_coordination is not None
        and data.agent_coordination.final_vote in {AgentVote.BLOCK, AgentVote.STOP_SESSION}
        and data.supervisor_result is not None
        and data.supervisor_result.final_executable
    ):
        contradictions.append("Agents vote to block/stop while Supervisor marks final decision executable.")
    return tuple(dict.fromkeys(contradictions))


def compute_system_confidence_score(
    evaluation_input: SelfEvaluationInput | None = None,
    **kwargs,
) -> SelfEvaluationScore:
    """Compute system confidence component scores from 0..100."""
    data = _input(evaluation_input, **kwargs)
    contradictions = detect_internal_contradictions(data)
    decision = 85 - len(contradictions) * 25
    strategic = 75
    behavioral = 75
    cognitive = 75
    consensus = 75
    governance = 75
    autonomy = 75

    if data.strategic_timeline_analysis is not None:
        strategic = data.strategic_timeline_analysis.stability_score
        if data.strategic_timeline_analysis.degradation_detected:
            strategic -= 20
    if data.strategic_result is not None and data.strategic_result.plan.status in {StrategicPlanStatus.PAUSED, StrategicPlanStatus.RECOVERY}:
        strategic -= 12
    if data.behavioral_stability is not None:
        behavioral = data.behavioral_stability.stability_score
        if data.behavioral_stability.pressure_level in {BehavioralPressureLevel.HIGH, BehavioralPressureLevel.EXTREME}:
            behavioral -= 15
        if data.behavioral_stability.recovery_state in {BehavioralRecoveryState.DETERIORATING, BehavioralRecoveryState.CRITICAL}:
            behavioral -= 15
    if data.cognitive_adaptation is not None:
        cognitive = data.cognitive_adaptation.global_score
        if data.cognitive_adaptation.load_level == CognitiveLoadLevel.OVERLOADED:
            cognitive -= 25
        elif data.cognitive_adaptation.load_level == CognitiveLoadLevel.HIGH:
            cognitive -= 10
    if data.agent_coordination is not None:
        consensus = data.agent_coordination.consensus_score
        if data.agent_coordination.consensus_status == AgentConsensusStatus.NO_CONSENSUS:
            consensus -= 20
        consensus -= min(25, len(data.agent_coordination.disagreements) * 6)
    if data.supervisor_result is not None:
        if not data.supervisor_result.final_executable:
            decision -= 15
            governance -= 15
        if data.supervisor_result.applied_overrides and any(override != SupervisorOverride.NONE for override in data.supervisor_result.applied_overrides):
            governance -= 15
    if data.learning_governance is not None:
        if data.learning_governance.decision in {
            LearningGovernanceDecision.ENTER_SAFETY_LOCKDOWN,
            LearningGovernanceDecision.FREEZE_POLICY_UPDATE,
            LearningGovernanceDecision.LOCK_DANGEROUS_POLICY,
        }:
            governance -= 30
            autonomy -= 25
        elif data.learning_governance.decision == LearningGovernanceDecision.ALLOW_LIMITED_LEARNING:
            governance -= 8
            autonomy -= 8
    if data.reward_evaluation is not None and data.reward_evaluation.reward_label in {RewardLabel.BAD_DECISION, RewardLabel.DANGEROUS_DECISION}:
        autonomy -= 12
    if data.tactical_execution is not None and data.tactical_execution.quality in {TacticalExecutionQuality.WEAK, TacticalExecutionQuality.DANGEROUS}:
        autonomy -= 12
    if data.replay_arena is not None:
        if data.replay_arena.status == ReplayArenaStatus.BLOCKED_BY_SAFETY:
            autonomy -= 20
        if data.replay_arena.robustness_score < 50:
            strategic -= 10
            autonomy -= 10

    return SelfEvaluationScore(
        decision_coherence_score=_clamp(decision),
        strategic_stability_score=_clamp(strategic),
        behavioral_stability_score=_clamp(behavioral),
        cognitive_stability_score=_clamp(cognitive),
        agent_consensus_score=_clamp(consensus),
        governance_safety_score=_clamp(governance),
        autonomy_readiness_score=_clamp(autonomy),
    )


def evaluate_self_consistency(
    evaluation_input: SelfEvaluationInput | None = None,
    **kwargs,
) -> SelfEvaluationResult:
    """Evaluate system self-consistency, confidence and recommended autonomy."""
    data = _input(evaluation_input, **kwargs)
    scores = compute_system_confidence_score(data)
    contradictions = detect_internal_contradictions(data)
    signals = _signals(data, scores, contradictions)
    confidence = _global_confidence(scores, signals)
    recommendation = recommend_system_autonomy(data, scores=scores, signals=signals, confidence_score=confidence)
    status = _status(recommendation, signals, confidence)
    event = SelfEvaluationEvent(
        status=status,
        autonomy_recommendation=recommendation,
        message=f"Self-evaluation confidence {confidence}/100; status {status.value}.",
        timestamp=datetime.now(UTC),
    )
    return SelfEvaluationResult(
        status=status,
        autonomy_recommendation=recommendation,
        confidence_score=confidence,
        score_breakdown=scores,
        signals=signals,
        contradictions=contradictions,
        recommended_actions=_actions(recommendation, signals),
        events=(event,),
        summary=f"System confidence {confidence}/100 with {len(contradictions)} contradiction(s).",
    )


def recommend_system_autonomy(
    evaluation_input: SelfEvaluationInput | None = None,
    *,
    scores: SelfEvaluationScore | None = None,
    signals: tuple[SelfEvaluationSignal, ...] | None = None,
    confidence_score: int | None = None,
    **kwargs,
) -> SystemAutonomyRecommendation:
    """Recommend system autonomy from self-evaluation evidence."""
    data = _input(evaluation_input, **kwargs)
    resolved_scores = scores or compute_system_confidence_score(data)
    resolved_signals = signals or _signals(data, resolved_scores, detect_internal_contradictions(data))
    confidence = confidence_score if confidence_score is not None else _global_confidence(resolved_scores, resolved_signals)
    critical = sum(1 for signal in resolved_signals if signal in _critical_signals())

    if SelfEvaluationSignal.INTERNAL_CONTRADICTION in resolved_signals and critical >= 2:
        return SystemAutonomyRecommendation.RECALIBRATE_SYSTEM
    if critical >= 3 or SelfEvaluationSignal.LEARNING_GOVERNANCE_BLOCK in resolved_signals:
        return SystemAutonomyRecommendation.FREEZE_AUTONOMY
    if SelfEvaluationSignal.INTERNAL_CONTRADICTION in resolved_signals:
        return SystemAutonomyRecommendation.REQUIRE_HUMAN_REVIEW
    if confidence < 40:
        return SystemAutonomyRecommendation.OBSERVE_ONLY
    if confidence < 60 or critical:
        return SystemAutonomyRecommendation.REDUCE_AUTONOMY
    if SelfEvaluationSignal.AUTONOMY_SAFE in resolved_signals and confidence >= 75:
        return SystemAutonomyRecommendation.MAINTAIN_AUTONOMY
    return SystemAutonomyRecommendation.REDUCE_AUTONOMY


def render_self_evaluation_markdown(result: SelfEvaluationResult) -> str:
    """Render recursive self-evaluation as Markdown."""
    lines = [
        "# Recursive Self-Evaluation Engine",
        "",
        "## Auto-evaluation AGIcore",
        "",
        f"- {result.summary}",
        "",
        "## Statut systeme",
        "",
        f"- {result.status.value}",
        "",
        "## Confiance globale",
        "",
        f"- {result.confidence_score}/100",
        "",
        "## Contradictions detectees",
        "",
        *_bullet_lines(result.contradictions),
        "",
        "## Stabilite strategique",
        "",
        f"- {result.score_breakdown.strategic_stability_score}/100",
        "",
        "## Stabilite comportementale",
        "",
        f"- {result.score_breakdown.behavioral_stability_score}/100",
        "",
        "## Charge cognitive",
        "",
        f"- {result.score_breakdown.cognitive_stability_score}/100",
        "",
        "## Recommandation autonomie",
        "",
        f"- {result.autonomy_recommendation.value}",
        "",
        "## Actions recommandees",
        "",
        *_bullet_lines(result.recommended_actions),
        "",
        "- Offline only: no broker, no real order, no external ML, no neural training.",
        "",
    ]
    return "\n".join(lines)


def _signals(
    data: SelfEvaluationInput,
    scores: SelfEvaluationScore,
    contradictions: tuple[str, ...],
) -> tuple[SelfEvaluationSignal, ...]:
    signals: list[SelfEvaluationSignal] = []
    signals.append(SelfEvaluationSignal.DECISION_COHERENCE_STRONG if scores.decision_coherence_score >= 70 and not contradictions else SelfEvaluationSignal.DECISION_COHERENCE_WEAK)
    if contradictions:
        signals.append(SelfEvaluationSignal.INTERNAL_CONTRADICTION)
    if _strategic_unstable(data, scores):
        signals.append(SelfEvaluationSignal.STRATEGIC_INSTABILITY)
    if _behavioral_unstable(data, scores):
        signals.append(SelfEvaluationSignal.BEHAVIORAL_INSTABILITY)
    if data.cognitive_adaptation is not None and data.cognitive_adaptation.load_level == CognitiveLoadLevel.OVERLOADED:
        signals.append(SelfEvaluationSignal.COGNITIVE_OVERLOAD)
    if data.agent_coordination is not None and (
        data.agent_coordination.consensus_score < 60
        or data.agent_coordination.consensus_status == AgentConsensusStatus.NO_CONSENSUS
    ):
        signals.append(SelfEvaluationSignal.AGENT_CONSENSUS_WEAK)
    if data.supervisor_result is not None and (
        not data.supervisor_result.final_executable
        or any(override != SupervisorOverride.NONE for override in data.supervisor_result.applied_overrides)
    ):
        signals.append(SelfEvaluationSignal.SUPERVISOR_OVERRIDE_ACTIVE)
    if data.learning_governance is not None and data.learning_governance.decision in {
        LearningGovernanceDecision.ENTER_SAFETY_LOCKDOWN,
        LearningGovernanceDecision.FREEZE_POLICY_UPDATE,
        LearningGovernanceDecision.LOCK_DANGEROUS_POLICY,
    }:
        signals.append(SelfEvaluationSignal.LEARNING_GOVERNANCE_BLOCK)
    preliminary_confidence = _avg_score(scores)
    signals.append(SelfEvaluationSignal.HIGH_CONFIDENCE_SYSTEM if preliminary_confidence >= 75 and not any(signal in signals for signal in _critical_signals()) else SelfEvaluationSignal.LOW_CONFIDENCE_SYSTEM)
    if contradictions and (_strategic_unstable(data, scores) or _behavioral_unstable(data, scores)):
        signals.append(SelfEvaluationSignal.RECALIBRATION_NEEDED)
    if not any(signal in signals for signal in _critical_signals()) and preliminary_confidence >= 70:
        signals.append(SelfEvaluationSignal.AUTONOMY_SAFE)
    else:
        signals.append(SelfEvaluationSignal.AUTONOMY_UNSAFE)
    return tuple(dict.fromkeys(signals))


def _status(
    recommendation: SystemAutonomyRecommendation,
    signals: tuple[SelfEvaluationSignal, ...],
    confidence: int,
) -> SelfEvaluationStatus:
    if SelfEvaluationSignal.INTERNAL_CONTRADICTION in signals:
        return SelfEvaluationStatus.CONTRADICTORY
    if recommendation == SystemAutonomyRecommendation.FREEZE_AUTONOMY:
        return SelfEvaluationStatus.AUTONOMY_REDUCED
    if recommendation == SystemAutonomyRecommendation.REQUIRE_HUMAN_REVIEW:
        return SelfEvaluationStatus.REVIEW_REQUIRED
    if any(signal in signals for signal in (SelfEvaluationSignal.BEHAVIORAL_INSTABILITY, SelfEvaluationSignal.COGNITIVE_OVERLOAD, SelfEvaluationSignal.AGENT_CONSENSUS_WEAK)):
        return SelfEvaluationStatus.UNSTABLE
    if confidence < 60 or SelfEvaluationSignal.STRATEGIC_INSTABILITY in signals:
        return SelfEvaluationStatus.DEGRADED
    return SelfEvaluationStatus.STABLE


def _actions(
    recommendation: SystemAutonomyRecommendation,
    signals: tuple[SelfEvaluationSignal, ...],
) -> tuple[str, ...]:
    actions: list[str] = []
    if recommendation == SystemAutonomyRecommendation.MAINTAIN_AUTONOMY:
        actions.append("Maintain current offline autonomy level.")
    elif recommendation == SystemAutonomyRecommendation.REDUCE_AUTONOMY:
        actions.append("Reduce autonomy and require additional confirmation.")
    elif recommendation == SystemAutonomyRecommendation.OBSERVE_ONLY:
        actions.append("Switch to observe-only mode until confidence improves.")
    elif recommendation == SystemAutonomyRecommendation.REQUIRE_HUMAN_REVIEW:
        actions.append("Require human review before any further autonomous decision.")
    elif recommendation == SystemAutonomyRecommendation.FREEZE_AUTONOMY:
        actions.append("Freeze autonomy until governance and safety blockers clear.")
    elif recommendation == SystemAutonomyRecommendation.RECALIBRATE_SYSTEM:
        actions.append("Recalibrate decision hierarchy and resolve contradictions.")
    if SelfEvaluationSignal.AGENT_CONSENSUS_WEAK in signals:
        actions.append("Review agent disagreement and consensus weights.")
    if SelfEvaluationSignal.STRATEGIC_INSTABILITY in signals:
        actions.append("Review strategic timeline degradation before continuing.")
    if SelfEvaluationSignal.COGNITIVE_OVERLOAD in signals:
        actions.append("Pause adaptive workflows and lower cognitive load.")
    return tuple(dict.fromkeys(actions))


def _strategic_unstable(data: SelfEvaluationInput, scores: SelfEvaluationScore) -> bool:
    return bool(
        scores.strategic_stability_score < 55
        or (
            data.strategic_timeline_analysis is not None
            and (
                data.strategic_timeline_analysis.degradation_detected
                or StrategicDriftSignal.STRATEGIC_DEGRADATION in data.strategic_timeline_analysis.drift_signals
            )
        )
    )


def _behavioral_unstable(data: SelfEvaluationInput, scores: SelfEvaluationScore) -> bool:
    return bool(
        scores.behavioral_stability_score < 55
        or (
            data.behavioral_stability is not None
            and data.behavioral_stability.recovery_state in {BehavioralRecoveryState.DETERIORATING, BehavioralRecoveryState.CRITICAL}
        )
    )


def _global_confidence(
    scores: SelfEvaluationScore,
    signals: tuple[SelfEvaluationSignal, ...],
) -> int:
    score = _avg_score(scores)
    score -= 9 * sum(1 for signal in signals if signal in _critical_signals())
    if SelfEvaluationSignal.HIGH_CONFIDENCE_SYSTEM in signals:
        score += 5
    if SelfEvaluationSignal.AUTONOMY_SAFE in signals:
        score += 5
    return _clamp(score)


def _avg_score(scores: SelfEvaluationScore) -> int:
    values = (
        scores.decision_coherence_score,
        scores.strategic_stability_score,
        scores.behavioral_stability_score,
        scores.cognitive_stability_score,
        scores.agent_consensus_score,
        scores.governance_safety_score,
        scores.autonomy_readiness_score,
    )
    return int(round(sum(values) / len(values)))


def _critical_signals() -> set[SelfEvaluationSignal]:
    return {
        SelfEvaluationSignal.INTERNAL_CONTRADICTION,
        SelfEvaluationSignal.STRATEGIC_INSTABILITY,
        SelfEvaluationSignal.BEHAVIORAL_INSTABILITY,
        SelfEvaluationSignal.COGNITIVE_OVERLOAD,
        SelfEvaluationSignal.AGENT_CONSENSUS_WEAK,
        SelfEvaluationSignal.SUPERVISOR_OVERRIDE_ACTIVE,
        SelfEvaluationSignal.LEARNING_GOVERNANCE_BLOCK,
    }


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _input(evaluation_input: SelfEvaluationInput | None = None, **kwargs: Any) -> SelfEvaluationInput:
    if evaluation_input is not None:
        return evaluation_input
    return SelfEvaluationInput(**kwargs)


def _clamp(value: int | float) -> int:
    return max(0, min(100, int(round(value))))


__all__ = [
    "compute_system_confidence_score",
    "detect_internal_contradictions",
    "evaluate_self_consistency",
    "recommend_system_autonomy",
    "render_self_evaluation_markdown",
]
