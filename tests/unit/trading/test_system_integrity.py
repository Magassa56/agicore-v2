"""Unit tests for the offline Autonomous System Integrity Engine."""
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
from agicore.trading.multi_agent_models import AgentConsensusStatus, AgentCoordinationResult, AgentVote
from agicore.trading.recursive_self_evaluation_models import (
    SelfEvaluationResult,
    SelfEvaluationScore,
    SelfEvaluationStatus,
    SystemAutonomyRecommendation,
)
from agicore.trading.safe_rl_models import SafeRLExperimentResult, SafeRLStatus
from agicore.trading.strategic_memory_models import StrategicDriftSignal, StrategicTimelineAnalysis
from agicore.trading.system_integrity import (
    compute_module_health,
    detect_system_integrity_risks,
    evaluate_system_integrity,
    recommend_integrity_action,
    render_system_integrity_markdown,
)
from agicore.trading.system_integrity_models import (
    ModuleHealthStatus,
    SystemIntegrityRisk,
    SystemIntegrityStatus,
)


def _self_eval(
    status: SelfEvaluationStatus = SelfEvaluationStatus.STABLE,
    recommendation: SystemAutonomyRecommendation = SystemAutonomyRecommendation.MAINTAIN_AUTONOMY,
    confidence: int = 85,
) -> SelfEvaluationResult:
    score = SelfEvaluationScore(confidence, confidence, confidence, confidence, confidence, confidence, confidence)
    return SelfEvaluationResult(status, recommendation, confidence, score, (), (), (), (), "self eval")


def _governance(
    decision: LearningGovernanceDecision = LearningGovernanceDecision.ALLOW_LEARNING,
    mode: LearningGovernanceMode = LearningGovernanceMode.LEARN,
) -> LearningGovernanceResult:
    return LearningGovernanceResult(decision, mode, LearningCycleStatus.READY, (), (), (), (), (), "governance")


def _cognitive(score: int = 80, load: CognitiveLoadLevel = CognitiveLoadLevel.LOW) -> CognitiveAdaptationResult:
    return CognitiveAdaptationResult(CognitiveAdaptationMode.ADAPT, load, score, CognitiveFlexibilityScore(score, score, score, score, score, score), (), (), (), ())


def _behavior(score: int = 80, pressure: BehavioralPressureLevel = BehavioralPressureLevel.LOW, recovery: BehavioralRecoveryState = BehavioralRecoveryState.STABLE) -> BehavioralStabilityResult:
    return BehavioralStabilityResult(score, pressure, recovery, BehavioralStabilityScore(score, score, score, score, score, score), (), (), (), ())


def _executive(allow: bool = True) -> ExecutiveBrainResult:
    state = ExecutiveState(ExecutiveMode.NORMAL, ExecutiveIntent.CONTROLLED_GROWTH, ExecutiveRiskAppetite.MODERATE, "objective", (), ())
    decision = ExecutiveDecision(allow, False, False, False, "ALLOW", "continue")
    return ExecutiveBrainResult(state, decision, (), "executive")


def _supervisor(executable: bool = True, decision: SupervisorDecision = SupervisorDecision.APPROVE_SYSTEM_DECISION, overrides: tuple[SupervisorOverride, ...] = (SupervisorOverride.NONE,)) -> SupervisorResult:
    return SupervisorResult(decision, executable, overrides, (), (), (), (), (), (), "supervisor")


def _agent(score: int = 80, vote: AgentVote = AgentVote.APPROVE, status: AgentConsensusStatus = AgentConsensusStatus.CONSENSUS_APPROVE) -> AgentCoordinationResult:
    return AgentCoordinationResult(vote, status, score, (), (), (), (), "agent")


def _timeline(stability: int = 80, health: int = 80, degradation: bool = False) -> StrategicTimelineAnalysis:
    drifts = (StrategicDriftSignal.STRATEGIC_DEGRADATION,) if degradation else ()
    return StrategicTimelineAnalysis(3, (), drifts, None, None, stability, health, not degradation, degradation, (), "timeline")


def _safe_rl(status: SafeRLStatus = SafeRLStatus.SAFE) -> SafeRLExperimentResult:
    return SafeRLExperimentResult(status, (), (), (), (), (), (), "safe rl")


def test_detects_contradictory_self_evaluation_as_layer_conflict() -> None:
    risks = detect_system_integrity_risks(
        self_evaluation=_self_eval(SelfEvaluationStatus.CONTRADICTORY, SystemAutonomyRecommendation.REQUIRE_HUMAN_REVIEW, 45)
    )

    assert SystemIntegrityRisk.LOGIC_CONFLICT in risks
    assert SystemIntegrityRisk.LAYER_CONTRADICTION in risks
    assert SystemIntegrityRisk.AUTONOMY_UNSAFE in risks


def test_learning_safety_lockdown_detects_governance_failure() -> None:
    risks = detect_system_integrity_risks(
        learning_governance=_governance(
            LearningGovernanceDecision.ENTER_SAFETY_LOCKDOWN,
            LearningGovernanceMode.SAFETY_LOCKDOWN,
        )
    )

    assert SystemIntegrityRisk.GOVERNANCE_FAILURE in risks
    assert SystemIntegrityRisk.SAFETY_LOCKDOWN_REQUIRED in risks


def test_cognitive_and_behavioral_drift_are_detected() -> None:
    risks = detect_system_integrity_risks(
        cognitive_adaptation=_cognitive(30, CognitiveLoadLevel.OVERLOADED),
        behavioral_stability=_behavior(30, BehavioralPressureLevel.EXTREME, BehavioralRecoveryState.CRITICAL),
        strategic_timeline_analysis=_timeline(35, 35, degradation=True),
    )

    assert SystemIntegrityRisk.COGNITIVE_OVERLOAD in risks
    assert SystemIntegrityRisk.BEHAVIORAL_DRIFT in risks
    assert SystemIntegrityRisk.STRATEGIC_DRIFT in risks


def test_compute_module_health_marks_blocked_modules_for_isolation() -> None:
    reports = compute_module_health(
        safe_rl_result=_safe_rl(SafeRLStatus.BLOCKED),
        self_evaluation=_self_eval(SelfEvaluationStatus.DEGRADED, SystemAutonomyRecommendation.FREEZE_AUTONOMY, 35),
    )

    statuses = {report.module_name: report.health_status for report in reports}
    assert statuses["safe_rl_layer"] in {ModuleHealthStatus.BLOCKED, ModuleHealthStatus.ISOLATE}
    assert any(report.isolate_recommended for report in reports)


def test_risk_accumulation_from_multiple_unhealthy_modules() -> None:
    risks = detect_system_integrity_risks(
        self_evaluation=_self_eval(SelfEvaluationStatus.CONTRADICTORY, SystemAutonomyRecommendation.RECALIBRATE_SYSTEM, 25),
        learning_governance=_governance(LearningGovernanceDecision.FREEZE_POLICY_UPDATE, LearningGovernanceMode.FREEZE_LEARNING),
        safe_rl_result=_safe_rl(SafeRLStatus.BLOCKED),
        cognitive_adaptation=_cognitive(20, CognitiveLoadLevel.OVERLOADED),
    )

    assert SystemIntegrityRisk.RISK_ACCUMULATION in risks
    assert SystemIntegrityRisk.RECALIBRATION_REQUIRED in risks


def test_evaluate_system_integrity_healthy_stack() -> None:
    result = evaluate_system_integrity(
        self_evaluation=_self_eval(),
        learning_governance=_governance(),
        cognitive_adaptation=_cognitive(),
        behavioral_stability=_behavior(),
        executive_result=_executive(),
        supervisor_result=_supervisor(),
        agent_coordination=_agent(),
        strategic_timeline_analysis=_timeline(),
        safe_rl_result=_safe_rl(),
    )

    assert result.status == SystemIntegrityStatus.HEALTHY
    assert result.integrity_score >= 75
    assert result.modules_to_isolate == ()


def test_evaluate_system_integrity_protection_or_rollback_for_critical_stack() -> None:
    result = evaluate_system_integrity(
        self_evaluation=_self_eval(SelfEvaluationStatus.CONTRADICTORY, SystemAutonomyRecommendation.RECALIBRATE_SYSTEM, 20),
        learning_governance=_governance(LearningGovernanceDecision.ENTER_SAFETY_LOCKDOWN, LearningGovernanceMode.SAFETY_LOCKDOWN),
        cognitive_adaptation=_cognitive(20, CognitiveLoadLevel.OVERLOADED),
        behavioral_stability=_behavior(20, BehavioralPressureLevel.EXTREME, BehavioralRecoveryState.CRITICAL),
        safe_rl_result=_safe_rl(SafeRLStatus.BLOCKED),
    )

    assert result.status in {
        SystemIntegrityStatus.PROTECTION_MODE,
        SystemIntegrityStatus.COMPROMISED,
        SystemIntegrityStatus.ROLLBACK_RECOMMENDED,
    }
    assert result.modules_to_isolate
    assert result.recommended_action in {"PROTECTION_MODE", "ROLLBACK_RECOMMENDED", "ISOLATE_UNSTABLE_MODULES"}


def test_cross_layer_conflict_from_executive_and_supervisor() -> None:
    risks = detect_system_integrity_risks(
        executive_result=_executive(allow=True),
        supervisor_result=_supervisor(False, SupervisorDecision.OVERRIDE_TO_BLOCK, (SupervisorOverride.BLOCK_DANGEROUS_CONSENSUS,)),
    )

    assert SystemIntegrityRisk.LOGIC_CONFLICT in risks
    assert SystemIntegrityRisk.LAYER_CONTRADICTION in risks


def test_recommend_integrity_action_for_compromised_stack() -> None:
    primary, actions = recommend_integrity_action(
        self_evaluation=_self_eval(SelfEvaluationStatus.CONTRADICTORY, SystemAutonomyRecommendation.RECALIBRATE_SYSTEM, 20),
        safe_rl_result=_safe_rl(SafeRLStatus.BLOCKED),
    )

    assert primary in {"ROLLBACK_RECOMMENDED", "PROTECTION_MODE", "ISOLATE_UNSTABLE_MODULES"}
    assert actions


def test_render_system_integrity_markdown_contains_required_sections() -> None:
    result = evaluate_system_integrity(
        self_evaluation=_self_eval(),
        learning_governance=_governance(),
        cognitive_adaptation=_cognitive(),
        behavioral_stability=_behavior(),
        safe_rl_result=_safe_rl(),
    )

    markdown = render_system_integrity_markdown(result)

    assert "# Autonomous System Integrity Engine" in markdown
    assert "## Integrite systeme" in markdown
    assert "## Score global" in markdown
    assert "## Statut" in markdown
    assert "## Risques detectes" in markdown
    assert "## Sante des modules" in markdown
    assert "## Modules a isoler" in markdown
    assert "## Recommandation protection/rollback" in markdown
    assert "## Actions AGIcore" in markdown
    assert "no broker" in markdown
