"""Unit tests for the offline Autonomous Operational Awareness Engine."""
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
from agicore.trading.mission_continuity_models import (
    MissionContinuityMode,
    MissionContinuityResult,
    MissionContinuityScore,
)
from agicore.trading.multi_agent_models import AgentConsensusStatus, AgentCoordinationResult, AgentVote
from agicore.trading.operational_awareness import (
    analyze_operational_signals,
    build_operational_recommendations,
    compute_operational_confidence,
    detect_operational_risks,
    evaluate_operational_awareness,
    render_operational_awareness_markdown,
)
from agicore.trading.operational_awareness_models import (
    OperationalAwarenessMode,
    OperationalHealthStatus,
    OperationalRecommendation,
    OperationalRisk,
    OperationalSignal,
)
from agicore.trading.recursive_self_evaluation_models import (
    SelfEvaluationResult,
    SelfEvaluationScore,
    SelfEvaluationStatus,
    SystemAutonomyRecommendation,
)
from agicore.trading.recovery_resilience_models import RecoveryMode, RecoveryResilienceResult, RecoveryRisk, ResilienceScore
from agicore.trading.strategic_memory_models import StrategicDriftSignal, StrategicTimelineAnalysis
from agicore.trading.system_integrity_models import SystemIntegrityResult, SystemIntegrityStatus


def _continuity(mode: MissionContinuityMode = MissionContinuityMode.FULL_OPERATION, score: int = 85) -> MissionContinuityResult:
    breakdown = MissionContinuityScore(score, score, score, score, score, score, score)
    return MissionContinuityResult(mode, score, breakdown, (), (), (), (), (), (), (), (), "continuity")


def _recovery(mode: RecoveryMode = RecoveryMode.NORMAL, score: int = 85, risks: tuple[RecoveryRisk, ...] = ()) -> RecoveryResilienceResult:
    breakdown = ResilienceScore(score, score, score, score, score, score, score)
    return RecoveryResilienceResult(mode, score, breakdown, risks, (), (), (), (), (), (), "recovery")


def _integrity(status: SystemIntegrityStatus = SystemIntegrityStatus.HEALTHY, score: int = 85) -> SystemIntegrityResult:
    return SystemIntegrityResult(status, score, (), (), (), "action", (), (), "integrity")


def _executive(mode: ExecutiveMode = ExecutiveMode.NORMAL, stop: bool = False) -> ExecutiveBrainResult:
    state = ExecutiveState(mode, ExecutiveIntent.CONTROLLED_GROWTH, ExecutiveRiskAppetite.MODERATE, "objective", (), ())
    decision = ExecutiveDecision(not stop, False, False, stop, "LABEL", "action")
    return ExecutiveBrainResult(state, decision, (), "executive")


def _agent(score: int = 85, status: AgentConsensusStatus = AgentConsensusStatus.CONSENSUS_APPROVE, vote: AgentVote = AgentVote.APPROVE, disagreements: tuple[str, ...] = ()) -> AgentCoordinationResult:
    return AgentCoordinationResult(vote, status, score, (), disagreements, (), (), "agent")


def _supervisor(executable: bool = True, decision: SupervisorDecision = SupervisorDecision.APPROVE_SYSTEM_DECISION, conflicts: tuple[str, ...] = ()) -> SupervisorResult:
    return SupervisorResult(decision, executable, (SupervisorOverride.NONE,), (), (), (), conflicts, (), (), "supervisor")


def _cognitive(score: int = 85, load: CognitiveLoadLevel = CognitiveLoadLevel.LOW) -> CognitiveAdaptationResult:
    return CognitiveAdaptationResult(CognitiveAdaptationMode.ADAPT, load, score, CognitiveFlexibilityScore(score, score, score, score, score, score), (), (), (), ())


def _behavior(score: int = 85, pressure: BehavioralPressureLevel = BehavioralPressureLevel.LOW, recovery: BehavioralRecoveryState = BehavioralRecoveryState.STABLE) -> BehavioralStabilityResult:
    return BehavioralStabilityResult(score, pressure, recovery, BehavioralStabilityScore(score, score, score, score, score, score), (), (), (), ())


def _self_eval(confidence: int = 85, recommendation: SystemAutonomyRecommendation = SystemAutonomyRecommendation.MAINTAIN_AUTONOMY, status: SelfEvaluationStatus = SelfEvaluationStatus.STABLE) -> SelfEvaluationResult:
    scores = SelfEvaluationScore(confidence, confidence, confidence, confidence, confidence, confidence, confidence)
    return SelfEvaluationResult(status, recommendation, confidence, scores, (), (), (), (), "self")


def _timeline(count: int = 4, stability: int = 85, degradation: bool = False) -> StrategicTimelineAnalysis:
    drifts = (StrategicDriftSignal.STRATEGIC_DEGRADATION, StrategicDriftSignal.STABILITY_DECLINE) if degradation else ()
    return StrategicTimelineAnalysis(count, (), drifts, None, None, stability, stability, not degradation, degradation, (), "timeline")


def test_optimal_operation_with_strong_inputs() -> None:
    result = evaluate_operational_awareness(
        mission_continuity=_continuity(),
        recovery_resilience=_recovery(),
        system_integrity=_integrity(),
        executive_result=_executive(),
        agent_coordination=_agent(),
        supervisor_result=_supervisor(),
        cognitive_adaptation=_cognitive(),
        behavioral_stability=_behavior(),
        self_evaluation=_self_eval(),
        strategic_timeline_analysis=_timeline(),
    )

    assert result.mode == OperationalAwarenessMode.OPTIMAL
    assert result.health_status == OperationalHealthStatus.HEALTHY
    assert OperationalRecommendation.MAINTAIN_OPERATION in result.recommendations


def test_silent_degradation_detected_from_multiple_weak_scores() -> None:
    risks = detect_operational_risks(
        mission_continuity=_continuity(MissionContinuityMode.DEGRADED_OPERATION, 62),
        recovery_resilience=_recovery(RecoveryMode.STABILIZE, 62),
        system_integrity=_integrity(SystemIntegrityStatus.DEGRADED, 62),
        agent_coordination=_agent(62),
        self_evaluation=_self_eval(62),
    )

    assert OperationalRisk.SILENT_DEGRADATION in risks


def test_coordination_drift_detected_from_no_consensus() -> None:
    risks = detect_operational_risks(agent_coordination=_agent(40, AgentConsensusStatus.NO_CONSENSUS, disagreements=("a", "b")))

    assert OperationalRisk.AGENT_COORDINATION_DRIFT in risks


def test_cognitive_saturation_pushes_high_load() -> None:
    result = evaluate_operational_awareness(cognitive_adaptation=_cognitive(35, CognitiveLoadLevel.OVERLOADED))

    assert OperationalRisk.COGNITIVE_SATURATION in result.risks
    assert result.mode in {OperationalAwarenessMode.HIGH_LOAD, OperationalAwarenessMode.DEGRADED}
    assert OperationalRecommendation.FREEZE_LEARNING in result.recommendations


def test_critical_when_integrity_and_continuity_are_unstable() -> None:
    result = evaluate_operational_awareness(
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 25),
        mission_continuity=_continuity(MissionContinuityMode.SURVIVAL_CONTINUITY, 30),
        recovery_resilience=_recovery(RecoveryMode.PAUSED_RECOVERY, 25, (RecoveryRisk.RECOVERY_FAILURE,)),
    )

    assert result.mode == OperationalAwarenessMode.CRITICAL
    assert result.health_status in {OperationalHealthStatus.CRITICAL, OperationalHealthStatus.COLLAPSING}
    assert OperationalRecommendation.PRIORITIZE_CRITICAL_SYSTEMS in result.recommendations


def test_executive_instability_and_autonomy_drift_detected() -> None:
    risks = detect_operational_risks(
        executive_result=_executive(ExecutiveMode.SURVIVAL, stop=True),
        self_evaluation=_self_eval(35, SystemAutonomyRecommendation.FREEZE_AUTONOMY, SelfEvaluationStatus.AUTONOMY_REDUCED),
    )

    assert OperationalRisk.EXECUTIVE_INSTABILITY in risks
    assert OperationalRisk.AUTONOMY_DRIFT in risks


def test_memory_fragmentation_detected_from_empty_timeline() -> None:
    risks = detect_operational_risks(strategic_timeline_analysis=_timeline(0, 35, degradation=True))

    assert OperationalRisk.MEMORY_FRAGMENTATION in risks
    assert OperationalRisk.STRATEGIC_INCONSISTENCY in risks


def test_recovery_stagnation_recommends_recovery() -> None:
    recommendations = build_operational_recommendations(
        recovery_resilience=_recovery(RecoveryMode.PAUSED_RECOVERY, 30, (RecoveryRisk.RECOVERY_FAILURE, RecoveryRisk.LOW_CONFIDENCE))
    )

    assert OperationalRecommendation.INITIATE_RECOVERY in recommendations
    assert OperationalRecommendation.CONTINUE_MONITORING in recommendations


def test_compute_operational_confidence_penalizes_multiple_weak_layers() -> None:
    score = compute_operational_confidence(
        mission_continuity=_continuity(MissionContinuityMode.SAFE_PAUSE, 30),
        recovery_resilience=_recovery(RecoveryMode.PAUSED_RECOVERY, 30),
        system_integrity=_integrity(SystemIntegrityStatus.PROTECTION_MODE, 30),
        agent_coordination=_agent(35, AgentConsensusStatus.NO_CONSENSUS, AgentVote.BLOCK, ("a", "b")),
        cognitive_adaptation=_cognitive(30, CognitiveLoadLevel.OVERLOADED),
        behavioral_stability=_behavior(30, BehavioralPressureLevel.EXTREME, BehavioralRecoveryState.CRITICAL),
    )

    assert score.system_health_score < 20
    assert score.continuity_score < 20
    assert score.coordination_score < 20
    assert score.cognitive_load_score < 10


def test_analyze_operational_signals_reports_fragmentation_and_load() -> None:
    signals = analyze_operational_signals(
        cognitive_adaptation=_cognitive(40, CognitiveLoadLevel.HIGH),
        agent_coordination=_agent(40, AgentConsensusStatus.NO_CONSENSUS),
        strategic_timeline_analysis=_timeline(0, 40, degradation=True),
    )

    assert OperationalSignal.SYSTEM_HEALTH_WEAK in signals
    assert OperationalSignal.COORDINATION_DRIFTING in signals
    assert OperationalSignal.MEMORY_FRAGMENTED in signals
    assert OperationalSignal.LOAD_ELEVATED in signals


def test_render_operational_awareness_markdown_contains_required_sections() -> None:
    result = evaluate_operational_awareness(
        mission_continuity=_continuity(MissionContinuityMode.DEGRADED_OPERATION, 65),
        recovery_resilience=_recovery(RecoveryMode.STABILIZE, 65),
        agent_coordination=_agent(55, AgentConsensusStatus.NO_CONSENSUS),
    )

    markdown = render_operational_awareness_markdown(result)

    assert "# Autonomous Operational Awareness Engine" in markdown
    assert "## Operational Status" in markdown
    assert "## Operational Confidence" in markdown
    assert "## Active Signals" in markdown
    assert "## Detected Risks" in markdown
    assert "## System Load" in markdown
    assert "## Coordination Quality" in markdown
    assert "## Operational Recommendations" in markdown
    assert "## AGIcore Monitoring State" in markdown
    assert "no broker" in markdown
