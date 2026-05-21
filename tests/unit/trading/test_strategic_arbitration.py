"""Unit tests for the offline Autonomous Strategic Arbitration Engine."""
from __future__ import annotations

from agicore.trading.behavioral_stability_models import BehavioralPressureLevel, BehavioralRecoveryState, BehavioralStabilityResult, BehavioralStabilityScore
from agicore.trading.executive_brain_models import ExecutiveBrainResult, ExecutiveDecision, ExecutiveIntent, ExecutiveMode, ExecutiveRiskAppetite, ExecutiveState
from agicore.trading.hierarchical_supervisor_models import SupervisorDecision, SupervisorOverride, SupervisorResult
from agicore.trading.intent_alignment_models import IntentAlignmentMode, IntentAlignmentResult, IntentAlignmentState, IntentConfidence, IntentPriority, IntentRisk
from agicore.trading.learning_governance_models import LearningCycleStatus, LearningGovernanceDecision, LearningGovernanceMode, LearningGovernanceResult
from agicore.trading.meta_cognition_models import CognitiveRigidity, MetaCognitionMode, MetaCognitionResult, MetaCognitiveConfidence, MetaCognitiveRisk
from agicore.trading.mission_continuity_models import MissionContinuityMode, MissionContinuityResult, MissionContinuityScore
from agicore.trading.operational_awareness_models import OperationalAwarenessMode, OperationalAwarenessResult, OperationalConfidenceScore, OperationalHealthStatus
from agicore.trading.recovery_resilience_models import RecoveryMode, RecoveryResilienceResult, RecoveryRisk, ResilienceScore
from agicore.trading.recursive_self_evaluation_models import SelfEvaluationResult, SelfEvaluationScore, SelfEvaluationStatus, SystemAutonomyRecommendation
from agicore.trading.strategic_arbitration import (
    apply_emergency_arbitration,
    arbitrate_strategic_decision,
    build_priority_graph,
    compute_arbitration_confidence,
    compute_arbitration_priority,
    detect_strategic_conflicts,
    evaluate_survival_priority,
    generate_arbitration_recommendations,
    render_strategic_arbitration_markdown,
    resolve_conflicts,
)
from agicore.trading.strategic_arbitration_models import (
    ArbitrationAuthority,
    ArbitrationConflictType,
    ArbitrationDecision,
    ArbitrationMode,
    ArbitrationPriority,
    ArbitrationRecommendation,
    ArbitrationSeverity,
    ArbitrationState,
)
from agicore.trading.strategic_planning_models import StrategicHorizon, StrategicObjective, StrategicPlan, StrategicPlanningResult, StrategicPlanStatus
from agicore.trading.system_integrity_models import SystemIntegrityResult, SystemIntegrityStatus
from agicore.trading.tactical_execution_models import TacticalExecutionQuality, TacticalExecutionResult, TacticalExecutionSignal, TacticalScoreBreakdown


def _executive(
    allow: bool = False,
    intent: ExecutiveIntent = ExecutiveIntent.CAPITAL_PRESERVATION,
    mode: ExecutiveMode = ExecutiveMode.DEFENSIVE,
    risk: ExecutiveRiskAppetite = ExecutiveRiskAppetite.LOW,
) -> ExecutiveBrainResult:
    state = ExecutiveState(mode, intent, risk, "objective", (), ())
    decision = ExecutiveDecision(allow, False, False, False, "LABEL", "action")
    return ExecutiveBrainResult(state, decision, (), "executive")


def _integrity(status: SystemIntegrityStatus = SystemIntegrityStatus.HEALTHY, score: int = 90) -> SystemIntegrityResult:
    return SystemIntegrityResult(status, score, (), (), (), "action", (), (), "integrity")


def _awareness(score: int = 90, mode: OperationalAwarenessMode = OperationalAwarenessMode.STABLE, health: OperationalHealthStatus = OperationalHealthStatus.HEALTHY) -> OperationalAwarenessResult:
    breakdown = OperationalConfidenceScore(score, score, score, score, score, score, score, score, score)
    return OperationalAwarenessResult(mode, health, score, breakdown, (), (), (), (), 20, score, "monitor", (), "awareness")


def _governance(decision: LearningGovernanceDecision = LearningGovernanceDecision.PAUSE_LEARNING, mode: LearningGovernanceMode = LearningGovernanceMode.OBSERVE_ONLY) -> LearningGovernanceResult:
    return LearningGovernanceResult(decision, mode, LearningCycleStatus.OBSERVING, (), (), (), (), (), "governance")


def _supervisor(executable: bool = True, decision: SupervisorDecision = SupervisorDecision.APPROVE_SYSTEM_DECISION) -> SupervisorResult:
    return SupervisorResult(decision, executable, (SupervisorOverride.NONE,), (), (), (), (), (), (), "supervisor")


def _mission(mode: MissionContinuityMode = MissionContinuityMode.FULL_OPERATION, score: int = 90) -> MissionContinuityResult:
    breakdown = MissionContinuityScore(score, score, score, score, score, score, score)
    return MissionContinuityResult(mode, score, breakdown, (), (), (), (), (), (), (), (), "mission")


def _recovery(mode: RecoveryMode = RecoveryMode.NORMAL, score: int = 90, risks: tuple[RecoveryRisk, ...] = ()) -> RecoveryResilienceResult:
    breakdown = ResilienceScore(score, score, score, score, score, score, score)
    return RecoveryResilienceResult(mode, score, breakdown, risks, (), (), (), (), (), (), "recovery")


def _alignment(mode: IntentAlignmentMode = IntentAlignmentMode.FULLY_ALIGNED, score: int = 90, risks: tuple[IntentRisk, ...] = ()) -> IntentAlignmentResult:
    confidence = IntentConfidence(score, score, score, score, score, score, score)
    return IntentAlignmentResult(mode, IntentAlignmentState.ALIGNED, score, confidence, (IntentPriority.SAFETY,), (), (), risks, (), "mission", score, (), "alignment")


def _meta(mode: MetaCognitionMode = MetaCognitionMode.SELF_AWARE, risks: tuple[MetaCognitiveRisk, ...] = (), score: int = 90) -> MetaCognitionResult:
    confidence = MetaCognitiveConfidence(score, score, score, score, score, score, score)
    return MetaCognitionResult(mode, score, confidence, CognitiveRigidity.FLEXIBLE, (), (), (), risks, (), score, "reflect", (), "meta")


def _self_eval(recommendation: SystemAutonomyRecommendation = SystemAutonomyRecommendation.REDUCE_AUTONOMY, status: SelfEvaluationStatus = SelfEvaluationStatus.STABLE, score: int = 90) -> SelfEvaluationResult:
    breakdown = SelfEvaluationScore(score, score, score, score, score, score, score)
    return SelfEvaluationResult(status, recommendation, score, breakdown, (), (), (), (), "self")


def _strategy(objective: StrategicObjective = StrategicObjective.CAPITAL_PRESERVATION, status: StrategicPlanStatus = StrategicPlanStatus.ACTIVE) -> StrategicPlanningResult:
    plan = StrategicPlan(StrategicHorizon.WEEKLY, objective, status, ("objective",), ("risk",), 3, 1.0, "discipline")
    return StrategicPlanningResult(plan, 80, (), (), "strategy")


def _tactical(quality: TacticalExecutionQuality = TacticalExecutionQuality.GOOD, signals: tuple[TacticalExecutionSignal, ...] = ()) -> TacticalExecutionResult:
    return TacticalExecutionResult(quality, 80, TacticalScoreBreakdown(80, 80, 80, 80, 80, 80, 80), signals, (), (), ())


def _behavior(pressure: BehavioralPressureLevel = BehavioralPressureLevel.LOW, recovery: BehavioralRecoveryState = BehavioralRecoveryState.STABLE) -> BehavioralStabilityResult:
    return BehavioralStabilityResult(85, pressure, recovery, BehavioralStabilityScore(85, 85, 85, 85, 85, 85), (), (), (), ())


def test_detects_profit_vs_safety_conflict() -> None:
    conflicts = detect_strategic_conflicts(
        executive_result=_executive(True, ExecutiveIntent.CONTROLLED_GROWTH, ExecutiveMode.OPPORTUNITY, ExecutiveRiskAppetite.ELEVATED),
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 25),
    )

    assert any(conflict.conflict_type == ArbitrationConflictType.PROFIT_VS_SAFETY for conflict in conflicts)


def test_priority_hierarchy_selects_survival_over_performance() -> None:
    conflicts = detect_strategic_conflicts(
        recovery_resilience=_recovery(RecoveryMode.SURVIVAL_MODE, 20, (RecoveryRisk.SYSTEM_COMPROMISED,)),
        executive_result=_executive(True, ExecutiveIntent.CONTROLLED_GROWTH, ExecutiveMode.OPPORTUNITY, ExecutiveRiskAppetite.ELEVATED),
    )

    assert evaluate_survival_priority(recovery_resilience=_recovery(RecoveryMode.SURVIVAL_MODE))
    assert compute_arbitration_priority(conflicts) == ArbitrationPriority.SURVIVAL


def test_learning_vs_stability_freezes_learning() -> None:
    result = arbitrate_strategic_decision(
        learning_governance=_governance(LearningGovernanceDecision.ALLOW_LEARNING, LearningGovernanceMode.LEARN),
        system_integrity=_integrity(SystemIntegrityStatus.UNSTABLE, 45),
    )

    assert any(conflict.conflict_type == ArbitrationConflictType.LEARNING_VS_STABILITY for conflict in result.conflicts)
    assert ArbitrationRecommendation.FREEZE_LEARNING in result.recommendations


def test_autonomy_vs_supervision_requires_human_supervision() -> None:
    conflicts = detect_strategic_conflicts(
        self_evaluation=_self_eval(SystemAutonomyRecommendation.MAINTAIN_AUTONOMY),
        supervisor_result=_supervisor(False, SupervisorDecision.OVERRIDE_TO_BLOCK),
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 20),
    )
    resolutions = resolve_conflicts(conflicts)

    assert any(conflict.conflict_type == ArbitrationConflictType.AUTONOMY_VS_SUPERVISION for conflict in conflicts)
    assert any(resolution.authority == ArbitrationAuthority.SUPERVISION_CONTROLLER for resolution in resolutions)


def test_execution_vs_alignment_blocks_or_locks_down() -> None:
    result = arbitrate_strategic_decision(
        executive_result=_executive(True, ExecutiveIntent.CONTROLLED_GROWTH),
        intent_alignment=_alignment(IntentAlignmentMode.CRITICAL_REALIGNMENT, 20, (IntentRisk.ALIGNMENT_COLLAPSE, IntentRisk.SAFETY_BOUNDARY_DRIFT)),
    )

    assert any(conflict.conflict_type == ArbitrationConflictType.EXECUTION_VS_ALIGNMENT for conflict in result.conflicts)
    assert result.decision in {ArbitrationDecision.STOP_EXECUTION, ArbitrationDecision.EMERGENCY_LOCKDOWN, ArbitrationDecision.REDUCE_RISK}


def test_emergency_lockdown_on_multiple_critical_risks() -> None:
    result = arbitrate_strategic_decision(
        recovery_resilience=_recovery(RecoveryMode.SURVIVAL_MODE, 15, (RecoveryRisk.SYSTEM_COMPROMISED,)),
        mission_continuity=_mission(MissionContinuityMode.SURVIVAL_CONTINUITY, 20),
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 15),
        operational_awareness=_awareness(20, OperationalAwarenessMode.CRITICAL, OperationalHealthStatus.COLLAPSING),
        intent_alignment=_alignment(IntentAlignmentMode.CRITICAL_REALIGNMENT, 10, (IntentRisk.ALIGNMENT_COLLAPSE,)),
        executive_result=_executive(True, ExecutiveIntent.CONTROLLED_GROWTH, ExecutiveMode.OPPORTUNITY, ExecutiveRiskAppetite.ELEVATED),
    )

    assert apply_emergency_arbitration(
        recovery_resilience=_recovery(RecoveryMode.SURVIVAL_MODE, 15, (RecoveryRisk.SYSTEM_COMPROMISED,)),
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 15),
        intent_alignment=_alignment(IntentAlignmentMode.CRITICAL_REALIGNMENT, 10, (IntentRisk.ALIGNMENT_COLLAPSE,)),
        executive_result=_executive(True, ExecutiveIntent.CONTROLLED_GROWTH),
    )
    assert result.mode == ArbitrationMode.EMERGENCY_LOCKDOWN
    assert result.state == ArbitrationState.LOCKDOWN_REQUIRED
    assert result.emergency_lockdown


def test_priority_graph_contains_fixed_hierarchy() -> None:
    graph = build_priority_graph(system_integrity=_integrity(SystemIntegrityStatus.DEGRADED, 55))

    assert graph.ordered_priorities[0] == ArbitrationPriority.SURVIVAL
    assert graph.ordered_priorities[-1] == ArbitrationPriority.LEARNING
    assert (ArbitrationPriority.SURVIVAL, ArbitrationPriority.INTEGRITY) in graph.edges


def test_confidence_decreases_with_critical_inputs() -> None:
    confidence = compute_arbitration_confidence(
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 20),
        operational_awareness=_awareness(25, OperationalAwarenessMode.CRITICAL, OperationalHealthStatus.CRITICAL),
        executive_result=_executive(True, ExecutiveIntent.CONTROLLED_GROWTH),
    )

    assert confidence < 50


def test_recommendations_include_safe_controls_for_danger() -> None:
    recommendations = generate_arbitration_recommendations(
        executive_result=_executive(True, ExecutiveIntent.CONTROLLED_GROWTH),
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 20),
        learning_governance=_governance(LearningGovernanceDecision.ALLOW_LEARNING, LearningGovernanceMode.LEARN),
    )

    assert ArbitrationRecommendation.ENABLE_SAFE_MODE in recommendations
    assert ArbitrationRecommendation.LOCK_HIGH_RISK_ACTIONS in recommendations


def test_detects_strategy_vs_discipline_conflict() -> None:
    conflicts = detect_strategic_conflicts(
        strategic_result=_strategy(StrategicObjective.CONTROLLED_GROWTH),
        tactical_execution=_tactical(TacticalExecutionQuality.WEAK, (TacticalExecutionSignal.TACTICAL_DISCIPLINE_WEAK,)),
        behavioral_stability=_behavior(BehavioralPressureLevel.HIGH, BehavioralRecoveryState.DETERIORATING),
    )

    assert any(conflict.conflict_type == ArbitrationConflictType.STRATEGY_VS_DISCIPLINE for conflict in conflicts)


def test_render_strategic_arbitration_markdown_contains_required_sections() -> None:
    result = arbitrate_strategic_decision(
        executive_result=_executive(True, ExecutiveIntent.CONTROLLED_GROWTH),
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 20),
        meta_cognition=_meta(MetaCognitionMode.DEGRADED_REASONING, (MetaCognitiveRisk.COGNITIVE_COLLAPSE,)),
    )
    markdown = render_strategic_arbitration_markdown(result)

    assert "# Autonomous Strategic Arbitration Engine" in markdown
    assert "## Strategic Arbitration State" in markdown
    assert "## Detected Conflicts" in markdown
    assert "## Priority Graph" in markdown
    assert "## Arbitration Decision" in markdown
    assert "## Severity" in markdown
    assert "## Active Authorities" in markdown
    assert "## Recommendations" in markdown
    assert "## AGIcore Final Arbitration" in markdown
    assert "no broker" in markdown
