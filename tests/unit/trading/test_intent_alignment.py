"""Unit tests for the offline Autonomous Intent Alignment Engine."""
from __future__ import annotations

from agicore.trading.executive_brain_models import ExecutiveBrainResult, ExecutiveDecision, ExecutiveIntent, ExecutiveMode, ExecutiveRiskAppetite, ExecutiveState
from agicore.trading.hierarchical_supervisor_models import SupervisorDecision, SupervisorOverride, SupervisorResult
from agicore.trading.intent_alignment import (
    analyze_priority_stability,
    build_alignment_recommendations,
    compute_alignment_confidence,
    detect_alignment_drifts,
    detect_intent_conflicts,
    evaluate_intent_alignment,
    render_intent_alignment_markdown,
)
from agicore.trading.intent_alignment_models import (
    IntentAlignmentMode,
    IntentAlignmentState,
    IntentConflict,
    IntentDrift,
    IntentRecommendation,
    IntentRisk,
)
from agicore.trading.learning_governance_models import LearningCycleStatus, LearningGovernanceDecision, LearningGovernanceMode, LearningGovernanceResult
from agicore.trading.meta_cognition_models import (
    CognitiveRigidity,
    MetaCognitionMode,
    MetaCognitionResult,
    MetaCognitiveConfidence,
    MetaCognitiveRisk,
)
from agicore.trading.mission_continuity_models import MissionContinuityMode, MissionContinuityResult, MissionContinuityScore
from agicore.trading.operational_awareness_models import OperationalAwarenessMode, OperationalAwarenessResult, OperationalConfidenceScore, OperationalHealthStatus, OperationalRisk
from agicore.trading.recursive_self_evaluation_models import SelfEvaluationResult, SelfEvaluationScore, SelfEvaluationStatus, SystemAutonomyRecommendation
from agicore.trading.strategic_planning_models import StrategicHorizon, StrategicObjective, StrategicPlan, StrategicPlanningResult, StrategicPlanStatus
from agicore.trading.system_integrity_models import SystemIntegrityResult, SystemIntegrityStatus


def _executive(
    allow: bool = False,
    intent: ExecutiveIntent = ExecutiveIntent.CAPITAL_PRESERVATION,
    mode: ExecutiveMode = ExecutiveMode.DEFENSIVE,
    risk: ExecutiveRiskAppetite = ExecutiveRiskAppetite.LOW,
) -> ExecutiveBrainResult:
    state = ExecutiveState(mode, intent, risk, "protect capital", (), ())
    decision = ExecutiveDecision(allow, False, False, False, "LABEL", "action")
    return ExecutiveBrainResult(state, decision, (), "executive")


def _supervisor(executable: bool = True, decision: SupervisorDecision = SupervisorDecision.APPROVE_SYSTEM_DECISION) -> SupervisorResult:
    return SupervisorResult(decision, executable, (SupervisorOverride.NONE,), (), (), (), (), (), (), "supervisor")


def _governance(decision: LearningGovernanceDecision = LearningGovernanceDecision.PAUSE_LEARNING, mode: LearningGovernanceMode = LearningGovernanceMode.OBSERVE_ONLY) -> LearningGovernanceResult:
    return LearningGovernanceResult(decision, mode, LearningCycleStatus.OBSERVING, (), (), (), (), (), "governance")


def _self_eval(confidence: int = 85, status: SelfEvaluationStatus = SelfEvaluationStatus.STABLE, recommendation: SystemAutonomyRecommendation = SystemAutonomyRecommendation.REDUCE_AUTONOMY) -> SelfEvaluationResult:
    score = SelfEvaluationScore(confidence, confidence, confidence, confidence, confidence, confidence, confidence)
    return SelfEvaluationResult(status, recommendation, confidence, score, (), (), (), (), "self")


def _awareness(score: int = 85, mode: OperationalAwarenessMode = OperationalAwarenessMode.STABLE, health: OperationalHealthStatus = OperationalHealthStatus.HEALTHY, risks: tuple[OperationalRisk, ...] = ()) -> OperationalAwarenessResult:
    breakdown = OperationalConfidenceScore(score, score, score, score, score, score, score, score, score)
    return OperationalAwarenessResult(mode, health, score, breakdown, (), risks, (), (), 20, score, "monitoring", (), "awareness")


def _integrity(status: SystemIntegrityStatus = SystemIntegrityStatus.HEALTHY, score: int = 90) -> SystemIntegrityResult:
    return SystemIntegrityResult(status, score, (), (), (), "action", (), (), "integrity")


def _mission(mode: MissionContinuityMode = MissionContinuityMode.FULL_OPERATION, score: int = 90) -> MissionContinuityResult:
    breakdown = MissionContinuityScore(score, score, score, score, score, score, score)
    return MissionContinuityResult(mode, score, breakdown, (), (), (), (), (), (), (), (), "mission")


def _strategy(
    objective: StrategicObjective = StrategicObjective.CAPITAL_PRESERVATION,
    status: StrategicPlanStatus = StrategicPlanStatus.ACTIVE,
    progress: int = 85,
    many_goals: bool = False,
) -> StrategicPlanningResult:
    goals = ("a", "b", "c", "d") if many_goals else ("preserve capital",)
    constraints = ("max risk", "review") if many_goals else ("max risk",)
    risks = ("risk1", "risk2") if many_goals else ()
    recommendations = ("rec1", "rec2") if many_goals else ()
    plan = StrategicPlan(
        StrategicHorizon.WEEKLY,
        objective,
        status,
        goals,
        constraints,
        3,
        1.0,
        "discipline",
        None,
        {},
        risks,
        recommendations,
        (),
    )
    return StrategicPlanningResult(plan, progress, (), (), "strategy")


def _meta(mode: MetaCognitionMode = MetaCognitionMode.SELF_AWARE, risks: tuple[MetaCognitiveRisk, ...] = (), score: int = 85) -> MetaCognitionResult:
    confidence = MetaCognitiveConfidence(score, score, score, score, score, score, score)
    return MetaCognitionResult(mode, score, confidence, CognitiveRigidity.FLEXIBLE, (), (), (), risks, (), score, "reflective", (), "meta")


def test_fully_aligned_when_safety_and_priorities_match() -> None:
    result = evaluate_intent_alignment(
        meta_cognition=_meta(),
        operational_awareness=_awareness(),
        mission_continuity=_mission(),
        system_integrity=_integrity(),
        executive_result=_executive(),
        strategic_result=_strategy(),
        learning_governance=_governance(),
        self_evaluation=_self_eval(),
        supervisor_result=_supervisor(),
    )

    assert result.mode == IntentAlignmentMode.FULLY_ALIGNED
    assert result.state == IntentAlignmentState.ALIGNED
    assert result.alignment_confidence >= 85


def test_detects_autonomy_drift_when_autonomy_expands_under_critical_risk() -> None:
    result = evaluate_intent_alignment(
        meta_cognition=_meta(risks=(MetaCognitiveRisk.AUTONOMY_OVEREXPANSION,)),
        operational_awareness=_awareness(80, OperationalAwarenessMode.CRITICAL, OperationalHealthStatus.CRITICAL, (OperationalRisk.AUTONOMY_DRIFT,)),
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 30),
        executive_result=_executive(True, ExecutiveIntent.CONTROLLED_GROWTH, ExecutiveMode.OPPORTUNITY, ExecutiveRiskAppetite.ELEVATED),
        self_evaluation=_self_eval(80, SelfEvaluationStatus.STABLE, SystemAutonomyRecommendation.MAINTAIN_AUTONOMY),
    )

    assert IntentDrift.AUTONOMY_EXPANDING in result.drifts
    assert IntentRisk.AUTONOMY_EXPANSION in result.risks
    assert result.mode in {IntentAlignmentMode.AUTONOMY_DRIFT, IntentAlignmentMode.CRITICAL_REALIGNMENT}


def test_detects_priority_conflict_between_growth_and_capital_preservation() -> None:
    conflicts = detect_intent_conflicts(
        executive_result=_executive(False, ExecutiveIntent.CONTROLLED_GROWTH, ExecutiveMode.OPPORTUNITY),
        strategic_result=_strategy(StrategicObjective.CAPITAL_PRESERVATION),
    )

    assert IntentConflict.PRIORITY_COLLISION in conflicts


def test_detects_mission_divergence_when_strategy_expands_during_lockdown() -> None:
    drifts = detect_alignment_drifts(
        system_integrity=_integrity(SystemIntegrityStatus.PROTECTION_MODE, 25),
        strategic_result=_strategy(StrategicObjective.POLICY_VALIDATION),
        learning_governance=_governance(LearningGovernanceDecision.ALLOW_LEARNING, LearningGovernanceMode.LEARN),
        executive_result=_executive(False, ExecutiveIntent.POLICY_TESTING),
    )

    assert IntentDrift.MISSION_DIVERGING in drifts
    assert IntentDrift.SAFETY_BOUNDARY_WEAKENING in drifts


def test_critical_realignment_when_safety_and_mission_drift_together() -> None:
    result = evaluate_intent_alignment(
        operational_awareness=_awareness(75, OperationalAwarenessMode.CRITICAL, OperationalHealthStatus.CRITICAL),
        mission_continuity=_mission(MissionContinuityMode.SURVIVAL_CONTINUITY, 30),
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 20),
        executive_result=_executive(True, ExecutiveIntent.CONTROLLED_GROWTH, ExecutiveMode.OPPORTUNITY, ExecutiveRiskAppetite.ELEVATED),
        learning_governance=_governance(LearningGovernanceDecision.ALLOW_LEARNING, LearningGovernanceMode.LEARN),
    )

    assert result.mode == IntentAlignmentMode.CRITICAL_REALIGNMENT
    assert result.state == IntentAlignmentState.CRITICAL
    assert IntentRisk.ALIGNMENT_COLLAPSE in result.risks


def test_confidence_penalizes_executive_supervisor_contradiction() -> None:
    confidence = compute_alignment_confidence(
        executive_result=_executive(True, ExecutiveIntent.CONTROLLED_GROWTH),
        supervisor_result=_supervisor(False, SupervisorDecision.OVERRIDE_TO_BLOCK),
    )

    assert confidence.priority_stability_score < 60
    assert confidence.governance_alignment_score < 70


def test_priority_stability_penalizes_goal_fragmentation() -> None:
    stability = analyze_priority_stability(strategic_result=_strategy(many_goals=True))

    assert stability < 65


def test_build_recommendations_restores_safety_and_priority_order() -> None:
    recommendations = build_alignment_recommendations(
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 20),
        executive_result=_executive(True, ExecutiveIntent.CONTROLLED_GROWTH, ExecutiveMode.OPPORTUNITY, ExecutiveRiskAppetite.ELEVATED),
        strategic_result=_strategy(StrategicObjective.CAPITAL_PRESERVATION),
        learning_governance=_governance(LearningGovernanceDecision.ALLOW_LEARNING, LearningGovernanceMode.LEARN),
    )

    assert IntentRecommendation.REINFORCE_SAFETY_CONSTRAINTS in recommendations
    assert IntentRecommendation.RESTORE_PRIORITY_ORDER in recommendations
    assert IntentRecommendation.CONTINUE_MONITORING in recommendations


def test_render_intent_alignment_markdown_contains_required_sections() -> None:
    result = evaluate_intent_alignment(
        operational_awareness=_awareness(),
        mission_continuity=_mission(),
        system_integrity=_integrity(),
        executive_result=_executive(),
        strategic_result=_strategy(),
    )

    markdown = render_intent_alignment_markdown(result)

    assert "# Autonomous Intent Alignment Engine" in markdown
    assert "## Intent Alignment State" in markdown
    assert "## Strategic Goal Stability" in markdown
    assert "## Priority Analysis" in markdown
    assert "## Intent Conflicts" in markdown
    assert "## Alignment Risks" in markdown
    assert "## Alignment Confidence" in markdown
    assert "## Recommendations" in markdown
    assert "## AGIcore Alignment Status" in markdown
    assert "no broker" in markdown
