"""Unit tests for the offline Autonomous Global Orchestrator Core."""
from __future__ import annotations

from agicore.trading.behavioral_stability_models import BehavioralPressureLevel, BehavioralRecoveryState, BehavioralStabilityResult, BehavioralStabilityScore
from agicore.trading.collective_consensus_models import CollectiveConfidence, ConsensusDecision, ConsensusGraph, ConsensusMode, ConsensusResult, ConsensusState
from agicore.trading.executive_brain_models import ExecutiveBrainResult, ExecutiveDecision, ExecutiveIntent, ExecutiveMode, ExecutiveRiskAppetite, ExecutiveState
from agicore.trading.global_orchestrator import (
    apply_global_safe_mode,
    build_orchestration_graph,
    compute_orchestration_confidence,
    coordinate_engine_priorities,
    coordinate_global_orchestrator,
    detect_global_risks,
    evaluate_global_system_state,
    generate_orchestrator_recommendations,
    render_global_orchestrator_markdown,
    resolve_cross_layer_conflicts,
    schedule_coordination_cycle,
)
from agicore.trading.global_orchestrator_models import OrchestratorDecision, OrchestratorMode, OrchestratorPriority, OrchestratorRecommendation, OrchestratorRisk
from agicore.trading.hierarchical_supervisor_models import SupervisorDecision, SupervisorOverride, SupervisorResult
from agicore.trading.intent_alignment_models import IntentAlignmentMode, IntentAlignmentResult, IntentAlignmentState, IntentConfidence, IntentPriority
from agicore.trading.learning_governance_models import LearningCycleStatus, LearningGovernanceDecision, LearningGovernanceMode, LearningGovernanceResult
from agicore.trading.meta_cognition_models import CognitiveRigidity, MetaCognitionMode, MetaCognitionResult, MetaCognitiveConfidence
from agicore.trading.mission_continuity_models import MissionContinuityMode, MissionContinuityResult, MissionContinuityScore
from agicore.trading.operational_awareness_models import OperationalAwarenessMode, OperationalAwarenessResult, OperationalConfidenceScore, OperationalHealthStatus
from agicore.trading.recovery_resilience_models import RecoveryMode, RecoveryResilienceResult, ResilienceScore
from agicore.trading.recursive_self_evaluation_models import SelfEvaluationResult, SelfEvaluationScore, SelfEvaluationStatus, SystemAutonomyRecommendation
from agicore.trading.strategic_arbitration_models import ArbitrationDecision, ArbitrationMode, ArbitrationPriority, ArbitrationResult, ArbitrationSeverity, ArbitrationState, PriorityGraph
from agicore.trading.strategic_planning_models import StrategicHorizon, StrategicObjective, StrategicPlan, StrategicPlanningResult, StrategicPlanStatus
from agicore.trading.system_integrity_models import SystemIntegrityResult, SystemIntegrityStatus
from agicore.trading.tactical_execution_models import TacticalExecutionQuality, TacticalExecutionResult, TacticalScoreBreakdown


def _arbitration(decision: ArbitrationDecision = ArbitrationDecision.CONTINUE_OPERATION, mode: ArbitrationMode = ArbitrationMode.NORMAL_OPERATION, confidence: int = 90) -> ArbitrationResult:
    graph = PriorityGraph((ArbitrationPriority.SURVIVAL,), (), (ArbitrationPriority.PERFORMANCE,), ArbitrationPriority.PERFORMANCE)
    return ArbitrationResult(mode, ArbitrationState.STABLE, decision, ArbitrationSeverity.LOW, confidence, ArbitrationPriority.PERFORMANCE, (), (), (), graph, (), decision == ArbitrationDecision.EMERGENCY_LOCKDOWN, "arbitration", ())


def _consensus(decision: ConsensusDecision = ConsensusDecision.APPROVE_COLLECTIVE_DECISION, mode: ConsensusMode = ConsensusMode.NORMAL_CONSENSUS, score: int = 90) -> ConsensusResult:
    confidence = CollectiveConfidence(score, score, score, score, score, score)
    graph = ConsensusGraph((), (), None, (), ())
    return ConsensusResult(mode, ConsensusState.STABLE, decision, score, confidence, (), graph, {}, (), (), (), (), "consensus", ())


def _alignment(mode: IntentAlignmentMode = IntentAlignmentMode.FULLY_ALIGNED, score: int = 90) -> IntentAlignmentResult:
    confidence = IntentConfidence(score, score, score, score, score, score, score)
    return IntentAlignmentResult(mode, IntentAlignmentState.ALIGNED, score, confidence, (IntentPriority.SAFETY,), (), (), (), (), "mission", score, (), "alignment")


def _meta(mode: MetaCognitionMode = MetaCognitionMode.SELF_AWARE, score: int = 90) -> MetaCognitionResult:
    confidence = MetaCognitiveConfidence(score, score, score, score, score, score, score)
    return MetaCognitionResult(mode, score, confidence, CognitiveRigidity.FLEXIBLE, (), (), (), (), (), score, "reflect", (), "meta")


def _awareness(score: int = 90, mode: OperationalAwarenessMode = OperationalAwarenessMode.STABLE, health: OperationalHealthStatus = OperationalHealthStatus.HEALTHY) -> OperationalAwarenessResult:
    breakdown = OperationalConfidenceScore(score, score, score, score, score, score, score, score, score)
    return OperationalAwarenessResult(mode, health, score, breakdown, (), (), (), (), 20, score, "monitor", (), "awareness")


def _mission(mode: MissionContinuityMode = MissionContinuityMode.FULL_OPERATION, score: int = 90) -> MissionContinuityResult:
    breakdown = MissionContinuityScore(score, score, score, score, score, score, score)
    return MissionContinuityResult(mode, score, breakdown, (), (), (), (), (), (), (), (), "mission")


def _recovery(mode: RecoveryMode = RecoveryMode.NORMAL, score: int = 90) -> RecoveryResilienceResult:
    breakdown = ResilienceScore(score, score, score, score, score, score, score)
    return RecoveryResilienceResult(mode, score, breakdown, (), (), (), (), (), (), (), "recovery")


def _integrity(status: SystemIntegrityStatus = SystemIntegrityStatus.HEALTHY, score: int = 90) -> SystemIntegrityResult:
    return SystemIntegrityResult(status, score, (), (), (), "action", (), (), "integrity")


def _governance(decision: LearningGovernanceDecision = LearningGovernanceDecision.PAUSE_LEARNING, mode: LearningGovernanceMode = LearningGovernanceMode.OBSERVE_ONLY) -> LearningGovernanceResult:
    return LearningGovernanceResult(decision, mode, LearningCycleStatus.OBSERVING, (), (), (), (), (), "governance")


def _self_eval(recommendation: SystemAutonomyRecommendation = SystemAutonomyRecommendation.REDUCE_AUTONOMY, status: SelfEvaluationStatus = SelfEvaluationStatus.STABLE, score: int = 90) -> SelfEvaluationResult:
    breakdown = SelfEvaluationScore(score, score, score, score, score, score, score)
    return SelfEvaluationResult(status, recommendation, score, breakdown, (), (), (), (), "self")


def _supervisor(executable: bool = True, decision: SupervisorDecision = SupervisorDecision.APPROVE_SYSTEM_DECISION) -> SupervisorResult:
    return SupervisorResult(decision, executable, (SupervisorOverride.NONE,), (), (), (), (), (), (), "supervisor")


def _executive(allow: bool = False, mode: ExecutiveMode = ExecutiveMode.DEFENSIVE) -> ExecutiveBrainResult:
    state = ExecutiveState(mode, ExecutiveIntent.CAPITAL_PRESERVATION, ExecutiveRiskAppetite.LOW, "objective", (), ())
    decision = ExecutiveDecision(allow, False, False, False, "LABEL", "action")
    return ExecutiveBrainResult(state, decision, (), "executive")


def _strategy(status: StrategicPlanStatus = StrategicPlanStatus.ACTIVE) -> StrategicPlanningResult:
    plan = StrategicPlan(StrategicHorizon.WEEKLY, StrategicObjective.CAPITAL_PRESERVATION, status, ("objective",), ("risk",), 3, 1.0, "discipline")
    return StrategicPlanningResult(plan, 80, (), (), "strategy")


def _tactical(quality: TacticalExecutionQuality = TacticalExecutionQuality.GOOD) -> TacticalExecutionResult:
    return TacticalExecutionResult(quality, 80, TacticalScoreBreakdown(80, 80, 80, 80, 80, 80, 80), (), (), (), ())


def _behavior(pressure: BehavioralPressureLevel = BehavioralPressureLevel.LOW, recovery: BehavioralRecoveryState = BehavioralRecoveryState.STABLE) -> BehavioralStabilityResult:
    return BehavioralStabilityResult(85, pressure, recovery, BehavioralStabilityScore(85, 85, 85, 85, 85, 85), (), (), (), ())


def test_build_orchestration_graph_connects_active_engines() -> None:
    graph = build_orchestration_graph(system_integrity=_integrity(), recovery_resilience=_recovery(), mission_continuity=_mission(), operational_awareness=_awareness())

    assert "system_integrity" in graph.engines
    assert graph.routes
    assert graph.critical_routes


def test_normal_coordinated_operation_when_engines_are_aligned() -> None:
    result = coordinate_global_orchestrator(
        strategic_arbitration=_arbitration(),
        collective_consensus=_consensus(),
        intent_alignment=_alignment(),
        operational_awareness=_awareness(),
        system_integrity=_integrity(),
        executive_result=_executive(),
    )

    assert result.system_state.mode == OrchestratorMode.COORDINATED_OPERATION
    assert result.decision == OrchestratorDecision.CONTINUE_COORDINATED_OPERATION
    assert result.confidence_score >= 70


def test_detects_safe_global_mode_from_integrity_and_execution_conflict() -> None:
    risks = detect_global_risks(
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 20),
        executive_result=_executive(True),
        supervisor_result=_supervisor(False, SupervisorDecision.OVERRIDE_TO_BLOCK),
    )

    assert OrchestratorRisk.GLOBAL_SAFE_MODE_REQUIRED in risks
    assert OrchestratorRisk.UNSAFE_COORDINATION in risks
    assert OrchestratorRisk.EXECUTION_DESYNCHRONIZATION in risks


def test_survival_priority_overrides_all_other_priorities() -> None:
    priority = coordinate_engine_priorities(
        recovery_resilience=_recovery(RecoveryMode.SURVIVAL_MODE, 20),
        learning_governance=_governance(LearningGovernanceDecision.ALLOW_LEARNING, LearningGovernanceMode.LEARN),
    )

    assert priority == OrchestratorPriority.SURVIVAL
    assert apply_global_safe_mode(recovery_resilience=_recovery(RecoveryMode.SURVIVAL_MODE, 20)) is False


def test_survival_orchestration_decision() -> None:
    result = coordinate_global_orchestrator(
        recovery_resilience=_recovery(RecoveryMode.SURVIVAL_MODE, 20),
        mission_continuity=_mission(MissionContinuityMode.SURVIVAL_CONTINUITY, 20),
        executive_result=_executive(False, ExecutiveMode.SURVIVAL),
    )

    assert result.system_state.mode == OrchestratorMode.SURVIVAL_ORCHESTRATION
    assert result.decision == OrchestratorDecision.ACTIVATE_SURVIVAL_MODE
    assert OrchestratorRecommendation.ACTIVATE_SURVIVAL_MODE in result.recommendations


def test_resolve_cross_layer_conflicts_between_learning_and_safe_mode() -> None:
    conflicts = resolve_cross_layer_conflicts(
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 20),
        learning_governance=_governance(LearningGovernanceDecision.ALLOW_LEARNING, LearningGovernanceMode.LEARN),
    )

    assert conflicts
    assert "Learning is allowed" in conflicts[0]


def test_confidence_drops_with_multiple_degraded_engines() -> None:
    confidence = compute_orchestration_confidence(
        collective_consensus=_consensus(ConsensusDecision.NO_CONSENSUS, ConsensusMode.CONSENSUS_COLLAPSE, 20),
        intent_alignment=_alignment(IntentAlignmentMode.CRITICAL_REALIGNMENT, 20),
        operational_awareness=_awareness(20, OperationalAwarenessMode.CRITICAL, OperationalHealthStatus.CRITICAL),
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 20),
        meta_cognition=_meta(MetaCognitionMode.DEGRADED_REASONING, 20),
    )

    assert confidence < 35


def test_schedule_cycle_marks_safe_mode_and_supervision() -> None:
    state = evaluate_global_system_state(
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 20),
        executive_result=_executive(True),
        supervisor_result=_supervisor(False, SupervisorDecision.OVERRIDE_TO_BLOCK),
    )
    cycle = schedule_coordination_cycle(system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 20), executive_result=_executive(True), supervisor_result=_supervisor(False, SupervisorDecision.OVERRIDE_TO_BLOCK), state=state)

    assert cycle.safe_mode
    assert cycle.requires_supervision
    assert "pause_conflicting_routes" in cycle.actions


def test_recommendations_for_unstable_global_state() -> None:
    recommendations = generate_orchestrator_recommendations(
        collective_consensus=_consensus(ConsensusDecision.NO_CONSENSUS, ConsensusMode.CONSENSUS_COLLAPSE, 20),
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 20),
        learning_governance=_governance(LearningGovernanceDecision.ALLOW_LEARNING, LearningGovernanceMode.LEARN),
    )

    assert OrchestratorRecommendation.ENTER_GLOBAL_SAFE_MODE in recommendations
    assert OrchestratorRecommendation.FREEZE_LEARNING in recommendations


def test_render_global_orchestrator_markdown_contains_required_sections() -> None:
    result = coordinate_global_orchestrator(
        strategic_arbitration=_arbitration(),
        collective_consensus=_consensus(),
        intent_alignment=_alignment(),
        system_integrity=_integrity(),
        strategic_result=_strategy(),
        tactical_execution=_tactical(),
        behavioral_stability=_behavior(),
    )
    markdown = render_global_orchestrator_markdown(result)

    assert "# Autonomous Global Orchestrator Core" in markdown
    assert "## Global System State" in markdown
    assert "## Active Engines" in markdown
    assert "## Orchestration Graph" in markdown
    assert "## Coordination Cycles" in markdown
    assert "## Risks" in markdown
    assert "## Priorities" in markdown
    assert "## Global Decisions" in markdown
    assert "## Recommendations" in markdown
    assert "## AGIcore Orchestrator State" in markdown
    assert "no broker" in markdown
