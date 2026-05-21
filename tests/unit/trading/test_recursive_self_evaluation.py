"""Unit tests for the offline Recursive Self-Evaluation Engine."""
from __future__ import annotations

from agicore.trading.behavioral_stability_models import (
    BehavioralPressureLevel,
    BehavioralRecoveryState,
    BehavioralStabilityResult,
    BehavioralStabilityScore,
)
from agicore.trading.cognitive_adaptation_models import (
    CognitiveAdaptationMode,
    CognitiveAdaptationResult,
    CognitiveFlexibilityScore,
    CognitiveLoadLevel,
)
from agicore.trading.executive_brain_models import (
    ExecutiveBrainResult,
    ExecutiveDecision,
    ExecutiveIntent,
    ExecutiveMode,
    ExecutiveRiskAppetite,
    ExecutiveState,
)
from agicore.trading.hierarchical_supervisor_models import SupervisorDecision, SupervisorOverride, SupervisorResult
from agicore.trading.learning_governance_models import (
    LearningCycleStatus,
    LearningGovernanceDecision,
    LearningGovernanceMode,
    LearningGovernanceResult,
)
from agicore.trading.meta_strategy_models import MetaStrategyDecision, MetaStrategySelectionResult
from agicore.trading.multi_agent_models import AgentConsensusStatus, AgentCoordinationResult, AgentVote
from agicore.trading.recursive_self_evaluation import (
    compute_system_confidence_score,
    detect_internal_contradictions,
    evaluate_self_consistency,
    recommend_system_autonomy,
    render_self_evaluation_markdown,
)
from agicore.trading.recursive_self_evaluation_models import (
    SelfEvaluationSignal,
    SelfEvaluationStatus,
    SystemAutonomyRecommendation,
)
from agicore.trading.reward_models import RewardBreakdown, RewardComponent, RewardEvaluationResult, RewardLabel
from agicore.trading.strategic_memory_models import StrategicDriftSignal, StrategicTimelineAnalysis
from agicore.trading.tactical_execution_models import TacticalExecutionQuality, TacticalExecutionResult, TacticalScoreBreakdown


def _executive(allow: bool = True, mode: ExecutiveMode = ExecutiveMode.NORMAL, stop: bool = False) -> ExecutiveBrainResult:
    state = ExecutiveState(mode, ExecutiveIntent.CONTROLLED_GROWTH, ExecutiveRiskAppetite.MODERATE, "objective", (), ())
    decision = ExecutiveDecision(allow, False, False, stop, "LABEL", "action")
    return ExecutiveBrainResult(state, decision, (), "ok")


def _supervisor(executable: bool = True, decision: SupervisorDecision = SupervisorDecision.APPROVE_SYSTEM_DECISION, overrides: tuple[SupervisorOverride, ...] = (SupervisorOverride.NONE,)) -> SupervisorResult:
    return SupervisorResult(decision, executable, overrides, (), (), (), (), (), (), "ok")


def _governance(decision: LearningGovernanceDecision = LearningGovernanceDecision.ALLOW_LEARNING, mode: LearningGovernanceMode = LearningGovernanceMode.LEARN) -> LearningGovernanceResult:
    return LearningGovernanceResult(decision, mode, LearningCycleStatus.READY, (), (), (), (), (), "safe")


def _behavior(score: int = 80, pressure: BehavioralPressureLevel = BehavioralPressureLevel.LOW, recovery: BehavioralRecoveryState = BehavioralRecoveryState.STABLE) -> BehavioralStabilityResult:
    return BehavioralStabilityResult(score, pressure, recovery, BehavioralStabilityScore(score, score, score, score, score, score), (), (), (), ())


def _cognitive(score: int = 80, load: CognitiveLoadLevel = CognitiveLoadLevel.LOW) -> CognitiveAdaptationResult:
    return CognitiveAdaptationResult(CognitiveAdaptationMode.ADAPT, load, score, CognitiveFlexibilityScore(score, score, score, score, score, score), (), (), (), ())


def _agent(score: int = 80, status: AgentConsensusStatus = AgentConsensusStatus.CONSENSUS_APPROVE, vote: AgentVote = AgentVote.APPROVE) -> AgentCoordinationResult:
    return AgentCoordinationResult(vote, status, score, (), (), (), (), "ok")


def _timeline(stability: int = 80, degradation: bool = False) -> StrategicTimelineAnalysis:
    drifts = (StrategicDriftSignal.STRATEGIC_DEGRADATION,) if degradation else ()
    return StrategicTimelineAnalysis(4, (), drifts, None, None, stability, stability, not degradation, degradation, (), "timeline")


def _meta(decision: MetaStrategyDecision = MetaStrategyDecision.SELECT_POLICY) -> MetaStrategySelectionResult:
    return MetaStrategySelectionResult("BALANCED", decision, 80, (), (), (), False, "ok")


def _reward(label: RewardLabel = RewardLabel.GOOD_DECISION) -> RewardEvaluationResult:
    c = RewardComponent("x", 0, "x")
    return RewardEvaluationResult(20, 75, label, RewardBreakdown(c, c, c, c, c, c, c, c, c, c, c), (), ())


def _tactical(quality: TacticalExecutionQuality = TacticalExecutionQuality.GOOD) -> TacticalExecutionResult:
    return TacticalExecutionResult(quality, 75, TacticalScoreBreakdown(75, 75, 75, 75, 75, 75, 75), (), (), (), ())


def test_detects_executive_supervisor_contradiction() -> None:
    contradictions = detect_internal_contradictions(
        executive_result=_executive(allow=True),
        supervisor_result=_supervisor(executable=False, decision=SupervisorDecision.OVERRIDE_TO_BLOCK),
    )

    assert contradictions
    assert "Executive Brain allows execution" in contradictions[0]


def test_detects_learning_governance_supervisor_contradiction() -> None:
    contradictions = detect_internal_contradictions(
        learning_governance=_governance(LearningGovernanceDecision.ALLOW_LEARNING),
        supervisor_result=_supervisor(executable=False),
    )

    assert any("Learning Governance allows learning" in item for item in contradictions)


def test_compute_confidence_scores_penalize_instability() -> None:
    scores = compute_system_confidence_score(
        behavioral_stability=_behavior(35, BehavioralPressureLevel.EXTREME, BehavioralRecoveryState.CRITICAL),
        cognitive_adaptation=_cognitive(40, CognitiveLoadLevel.OVERLOADED),
        strategic_timeline_analysis=_timeline(35, degradation=True),
        agent_coordination=_agent(45, AgentConsensusStatus.NO_CONSENSUS),
        learning_governance=_governance(LearningGovernanceDecision.ENTER_SAFETY_LOCKDOWN, LearningGovernanceMode.SAFETY_LOCKDOWN),
    )

    assert scores.behavioral_stability_score < 40
    assert scores.cognitive_stability_score < 30
    assert scores.governance_safety_score < 60


def test_evaluate_self_consistency_stable_system_maintains_autonomy() -> None:
    result = evaluate_self_consistency(
        learning_governance=_governance(),
        cognitive_adaptation=_cognitive(),
        behavioral_stability=_behavior(),
        executive_result=_executive(),
        supervisor_result=_supervisor(),
        agent_coordination=_agent(),
        strategic_timeline_analysis=_timeline(),
        meta_strategy=_meta(),
        reward_evaluation=_reward(),
        tactical_execution=_tactical(),
    )

    assert result.status == SelfEvaluationStatus.STABLE
    assert result.autonomy_recommendation == SystemAutonomyRecommendation.MAINTAIN_AUTONOMY
    assert SelfEvaluationSignal.AUTONOMY_SAFE in result.signals


def test_evaluate_self_consistency_contradictory_requires_review_or_recalibration() -> None:
    result = evaluate_self_consistency(
        executive_result=_executive(allow=True),
        supervisor_result=_supervisor(False, SupervisorDecision.OVERRIDE_TO_BLOCK, (SupervisorOverride.BLOCK_DANGEROUS_CONSENSUS,)),
        strategic_timeline_analysis=_timeline(35, degradation=True),
        behavioral_stability=_behavior(35),
    )

    assert result.status == SelfEvaluationStatus.CONTRADICTORY
    assert result.autonomy_recommendation in {
        SystemAutonomyRecommendation.REQUIRE_HUMAN_REVIEW,
        SystemAutonomyRecommendation.RECALIBRATE_SYSTEM,
    }
    assert SelfEvaluationSignal.INTERNAL_CONTRADICTION in result.signals


def test_learning_governance_block_freezes_autonomy() -> None:
    result = evaluate_self_consistency(
        learning_governance=_governance(LearningGovernanceDecision.ENTER_SAFETY_LOCKDOWN, LearningGovernanceMode.SAFETY_LOCKDOWN)
    )

    assert result.autonomy_recommendation == SystemAutonomyRecommendation.FREEZE_AUTONOMY
    assert SelfEvaluationSignal.LEARNING_GOVERNANCE_BLOCK in result.signals


def test_agent_weak_consensus_reduces_autonomy() -> None:
    result = evaluate_self_consistency(agent_coordination=_agent(40, AgentConsensusStatus.NO_CONSENSUS))

    assert SelfEvaluationSignal.AGENT_CONSENSUS_WEAK in result.signals
    assert result.autonomy_recommendation in {
        SystemAutonomyRecommendation.REDUCE_AUTONOMY,
        SystemAutonomyRecommendation.OBSERVE_ONLY,
    }


def test_cognitive_overload_signal_detected() -> None:
    result = evaluate_self_consistency(cognitive_adaptation=_cognitive(30, CognitiveLoadLevel.OVERLOADED))

    assert SelfEvaluationSignal.COGNITIVE_OVERLOAD in result.signals
    assert result.status in {SelfEvaluationStatus.UNSTABLE, SelfEvaluationStatus.DEGRADED}


def test_recommend_observe_only_for_low_confidence() -> None:
    recommendation = recommend_system_autonomy(
        behavioral_stability=_behavior(20, BehavioralPressureLevel.EXTREME, BehavioralRecoveryState.CRITICAL),
        cognitive_adaptation=_cognitive(20, CognitiveLoadLevel.OVERLOADED),
        strategic_timeline_analysis=_timeline(20, degradation=True),
        agent_coordination=_agent(20, AgentConsensusStatus.NO_CONSENSUS),
    )

    assert recommendation in {
        SystemAutonomyRecommendation.OBSERVE_ONLY,
        SystemAutonomyRecommendation.FREEZE_AUTONOMY,
    }


def test_meta_strategy_block_with_executive_allow_is_contradiction() -> None:
    contradictions = detect_internal_contradictions(
        executive_result=_executive(allow=True),
        meta_strategy=_meta(MetaStrategyDecision.BLOCK_ALL_POLICIES),
    )

    assert any("Meta Strategy blocks all policies" in item for item in contradictions)


def test_render_self_evaluation_markdown_contains_required_sections() -> None:
    result = evaluate_self_consistency(
        learning_governance=_governance(),
        cognitive_adaptation=_cognitive(),
        behavioral_stability=_behavior(),
        executive_result=_executive(),
        supervisor_result=_supervisor(),
        agent_coordination=_agent(),
        strategic_timeline_analysis=_timeline(),
    )

    markdown = render_self_evaluation_markdown(result)

    assert "# Recursive Self-Evaluation Engine" in markdown
    assert "## Auto-evaluation AGIcore" in markdown
    assert "## Statut systeme" in markdown
    assert "## Confiance globale" in markdown
    assert "## Contradictions detectees" in markdown
    assert "## Stabilite strategique" in markdown
    assert "## Stabilite comportementale" in markdown
    assert "## Charge cognitive" in markdown
    assert "## Recommandation autonomie" in markdown
    assert "## Actions recommandees" in markdown
    assert "no broker" in markdown
