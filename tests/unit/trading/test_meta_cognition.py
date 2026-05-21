"""Unit tests for the offline Autonomous Meta-Cognition Engine."""
from __future__ import annotations

from agicore.trading.behavioral_stability_models import BehavioralPressureLevel, BehavioralRecoveryState, BehavioralStabilityResult, BehavioralStabilityScore
from agicore.trading.cognitive_adaptation_models import CognitiveAdaptationMode, CognitiveAdaptationResult, CognitiveFlexibilityScore, CognitiveLoadLevel
from agicore.trading.executive_brain_models import ExecutiveBrainResult, ExecutiveDecision, ExecutiveIntent, ExecutiveMode, ExecutiveRiskAppetite, ExecutiveState
from agicore.trading.hierarchical_supervisor_models import SupervisorDecision, SupervisorOverride, SupervisorResult
from agicore.trading.learning_governance_models import LearningCycleStatus, LearningGovernanceDecision, LearningGovernanceMode, LearningGovernanceResult
from agicore.trading.meta_cognition import (
    analyze_reasoning_stability,
    build_meta_cognitive_recommendations,
    compute_meta_cognitive_confidence,
    detect_cognitive_biases,
    detect_meta_cognitive_risks,
    evaluate_meta_cognition,
    render_meta_cognition_markdown,
)
from agicore.trading.meta_cognition_models import (
    CognitiveBias,
    CognitiveContradiction,
    CognitiveRigidity,
    MetaCognitionMode,
    MetaCognitiveRecommendation,
    MetaCognitiveRisk,
)
from agicore.trading.multi_agent_models import AgentConsensusStatus, AgentCoordinationResult, AgentVote
from agicore.trading.operational_awareness_models import (
    OperationalAwarenessMode,
    OperationalAwarenessResult,
    OperationalConfidenceScore,
    OperationalHealthStatus,
    OperationalRisk,
)
from agicore.trading.recursive_self_evaluation_models import SelfEvaluationResult, SelfEvaluationScore, SelfEvaluationStatus, SystemAutonomyRecommendation
from agicore.trading.strategic_memory_models import StrategicDriftSignal, StrategicTimelineAnalysis
from agicore.trading.system_integrity_models import SystemIntegrityResult, SystemIntegrityStatus


def _awareness(score: int = 85, mode: OperationalAwarenessMode = OperationalAwarenessMode.STABLE, health: OperationalHealthStatus = OperationalHealthStatus.HEALTHY, risks: tuple[OperationalRisk, ...] = ()) -> OperationalAwarenessResult:
    breakdown = OperationalConfidenceScore(score, score, score, score, score, score, score, score, score)
    return OperationalAwarenessResult(mode, health, score, breakdown, (), risks, (), (), 25, score, "monitoring", (), "awareness")


def _self_eval(confidence: int = 85, status: SelfEvaluationStatus = SelfEvaluationStatus.STABLE, recommendation: SystemAutonomyRecommendation = SystemAutonomyRecommendation.MAINTAIN_AUTONOMY) -> SelfEvaluationResult:
    score = SelfEvaluationScore(confidence, confidence, confidence, confidence, confidence, confidence, confidence)
    return SelfEvaluationResult(status, recommendation, confidence, score, (), (), (), (), "self")


def _executive(allow: bool = True, mode: ExecutiveMode = ExecutiveMode.NORMAL, stop: bool = False) -> ExecutiveBrainResult:
    state = ExecutiveState(mode, ExecutiveIntent.CONTROLLED_GROWTH, ExecutiveRiskAppetite.MODERATE, "objective", (), ())
    decision = ExecutiveDecision(allow, False, False, stop, "LABEL", "action")
    return ExecutiveBrainResult(state, decision, (), "executive")


def _supervisor(executable: bool = True, decision: SupervisorDecision = SupervisorDecision.APPROVE_SYSTEM_DECISION, conflicts: tuple[str, ...] = ()) -> SupervisorResult:
    return SupervisorResult(decision, executable, (SupervisorOverride.NONE,), (), (), (), conflicts, (), (), "supervisor")


def _cognitive(score: int = 85, load: CognitiveLoadLevel = CognitiveLoadLevel.LOW, flexibility: int = 85, mode: CognitiveAdaptationMode = CognitiveAdaptationMode.ADAPT) -> CognitiveAdaptationResult:
    return CognitiveAdaptationResult(mode, load, score, CognitiveFlexibilityScore(flexibility, flexibility, flexibility, flexibility, flexibility, flexibility), (), (), (), ())


def _behavior(score: int = 85, pressure: BehavioralPressureLevel = BehavioralPressureLevel.LOW) -> BehavioralStabilityResult:
    return BehavioralStabilityResult(score, pressure, BehavioralRecoveryState.STABLE, BehavioralStabilityScore(score, score, score, score, score, score), (), (), (), ())


def _agent(score: int = 85, status: AgentConsensusStatus = AgentConsensusStatus.CONSENSUS_APPROVE, vote: AgentVote = AgentVote.APPROVE, disagreements: tuple[str, ...] = ()) -> AgentCoordinationResult:
    return AgentCoordinationResult(vote, status, score, (), disagreements, (), (), "agent")


def _timeline(count: int = 4, health: int = 85, degradation: bool = False) -> StrategicTimelineAnalysis:
    drifts = (StrategicDriftSignal.STRATEGIC_DEGRADATION,) if degradation else ()
    return StrategicTimelineAnalysis(count, (), drifts, None, None, health, health, not degradation, degradation, (), "timeline")


def _integrity(status: SystemIntegrityStatus = SystemIntegrityStatus.HEALTHY, score: int = 85) -> SystemIntegrityResult:
    return SystemIntegrityResult(status, score, (), (), (), "action", (), (), "integrity")


def _governance(decision: LearningGovernanceDecision = LearningGovernanceDecision.ALLOW_LEARNING, mode: LearningGovernanceMode = LearningGovernanceMode.LEARN) -> LearningGovernanceResult:
    return LearningGovernanceResult(decision, mode, LearningCycleStatus.READY, (), (), (), (), (), "gov")


def test_self_aware_mode_when_reasoning_is_stable() -> None:
    result = evaluate_meta_cognition(
        operational_awareness=_awareness(),
        self_evaluation=_self_eval(),
        executive_result=_executive(),
        supervisor_result=_supervisor(),
        cognitive_adaptation=_cognitive(),
        agent_coordination=_agent(),
        strategic_timeline_analysis=_timeline(),
    )

    assert result.mode == MetaCognitionMode.SELF_AWARE
    assert result.confidence_score >= 70
    assert result.rigidity == CognitiveRigidity.FLEXIBLE


def test_detects_overconfidence_with_critical_warnings() -> None:
    biases = detect_cognitive_biases(
        operational_awareness=_awareness(85, OperationalAwarenessMode.CRITICAL, OperationalHealthStatus.CRITICAL, (OperationalRisk.AUTONOMY_DRIFT, OperationalRisk.COGNITIVE_SATURATION, OperationalRisk.EXECUTIVE_INSTABILITY))
    )

    assert CognitiveBias.OVERCONFIDENCE in biases


def test_detects_executive_supervisor_contradiction() -> None:
    result = evaluate_meta_cognition(
        executive_result=_executive(allow=True),
        supervisor_result=_supervisor(False, SupervisorDecision.OVERRIDE_TO_BLOCK),
    )

    assert result.mode == MetaCognitionMode.CONTRADICTORY
    assert CognitiveContradiction.EXECUTIVE_SUPERVISOR_DIVERGENCE in result.contradictions
    assert MetaCognitiveRisk.LOGICAL_INSTABILITY in result.risks


def test_detects_rigidity_from_low_cognitive_flexibility() -> None:
    result = evaluate_meta_cognition(cognitive_adaptation=_cognitive(55, CognitiveLoadLevel.MODERATE, flexibility=25))

    assert result.rigidity in {CognitiveRigidity.RIGID, CognitiveRigidity.LOCKED}
    assert CognitiveBias.STRATEGIC_RIGIDITY in result.biases
    assert result.mode == MetaCognitionMode.RIGID


def test_reasoning_drift_from_strategic_degradation() -> None:
    biases = detect_cognitive_biases(strategic_timeline_analysis=_timeline(5, 35, degradation=True))

    assert CognitiveBias.REASONING_DRIFT in biases


def test_recalibration_required_with_multiple_risks() -> None:
    result = evaluate_meta_cognition(
        operational_awareness=_awareness(80, OperationalAwarenessMode.CRITICAL, OperationalHealthStatus.CRITICAL, (OperationalRisk.MEMORY_FRAGMENTATION, OperationalRisk.AUTONOMY_DRIFT, OperationalRisk.COGNITIVE_SATURATION)),
        self_evaluation=_self_eval(25, SelfEvaluationStatus.CONTRADICTORY, SystemAutonomyRecommendation.RECALIBRATE_SYSTEM),
        executive_result=_executive(allow=True),
        supervisor_result=_supervisor(False, SupervisorDecision.EMERGENCY_HALT, ("conflict", "halt")),
        cognitive_adaptation=_cognitive(20, CognitiveLoadLevel.OVERLOADED, flexibility=20),
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 20),
        learning_governance=_governance(LearningGovernanceDecision.ALLOW_LEARNING, LearningGovernanceMode.LEARN),
    )

    assert result.mode == MetaCognitionMode.RECALIBRATION_REQUIRED
    assert MetaCognitiveRecommendation.RECALIBRATE_REASONING in result.recommendations


def test_compute_confidence_penalizes_self_evaluation_contradiction() -> None:
    confidence = compute_meta_cognitive_confidence(self_evaluation=_self_eval(40, SelfEvaluationStatus.CONTRADICTORY))

    assert confidence.reasoning_stability_score < 60
    assert confidence.contradiction_resistance_score < 60
    assert confidence.self_awareness_score < 40


def test_analyze_reasoning_stability_penalizes_biases_and_contradictions() -> None:
    stability = analyze_reasoning_stability(
        self_evaluation=_self_eval(40, SelfEvaluationStatus.CONTRADICTORY),
        executive_result=_executive(allow=True),
        supervisor_result=_supervisor(False),
        strategic_timeline_analysis=_timeline(1, 35, degradation=True),
    )

    assert stability < 50


def test_feedback_ignorance_detected_when_exploiting_degraded_memory() -> None:
    biases = detect_cognitive_biases(
        learning_governance=_governance(LearningGovernanceDecision.ALLOW_LEARNING, LearningGovernanceMode.EXPLOIT_ONLY),
        strategic_timeline_analysis=_timeline(5, 40, degradation=True),
    )

    assert CognitiveBias.FEEDBACK_IGNORANCE in biases


def test_build_recommendations_for_overconfidence_and_contradiction() -> None:
    recommendations = build_meta_cognitive_recommendations(
        operational_awareness=_awareness(85, OperationalAwarenessMode.CRITICAL, OperationalHealthStatus.CRITICAL, (OperationalRisk.AUTONOMY_DRIFT, OperationalRisk.COGNITIVE_SATURATION, OperationalRisk.EXECUTIVE_INSTABILITY)),
        executive_result=_executive(allow=True),
        supervisor_result=_supervisor(False),
    )

    assert MetaCognitiveRecommendation.REDUCE_AUTONOMY in recommendations
    assert MetaCognitiveRecommendation.REBUILD_LOGICAL_STABILITY in recommendations
    assert MetaCognitiveRecommendation.CONTINUE_MONITORING in recommendations


def test_render_meta_cognition_markdown_contains_required_sections() -> None:
    result = evaluate_meta_cognition(
        operational_awareness=_awareness(),
        self_evaluation=_self_eval(),
        cognitive_adaptation=_cognitive(),
    )

    markdown = render_meta_cognition_markdown(result)

    assert "# Autonomous Meta-Cognition Engine" in markdown
    assert "## Meta-Cognitive State" in markdown
    assert "## Reasoning Stability" in markdown
    assert "## Detected Biases" in markdown
    assert "## Cognitive Contradictions" in markdown
    assert "## Meta-Cognitive Risks" in markdown
    assert "## Confidence Score" in markdown
    assert "## Recommendations" in markdown
    assert "## AGIcore Reflective State" in markdown
    assert "no broker" in markdown
