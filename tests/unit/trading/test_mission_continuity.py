"""Unit tests for the offline Autonomous Mission Continuity Engine."""
from __future__ import annotations

from agicore.trading.adaptive_policy_memory_models import AdaptivePolicyMemory
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
from agicore.trading.mission_continuity import (
    build_continuity_plan,
    compute_continuity_score,
    detect_continuity_risks,
    evaluate_mission_continuity,
    prioritize_critical_modules,
    render_mission_continuity_markdown,
)
from agicore.trading.mission_continuity_models import (
    ContinuityAction,
    ContinuityRisk,
    MissionContinuityMode,
    MissionCriticality,
)
from agicore.trading.multi_agent_models import AgentConsensusStatus, AgentCoordinationResult, AgentVote
from agicore.trading.recursive_self_evaluation_models import (
    SelfEvaluationResult,
    SelfEvaluationScore,
    SelfEvaluationStatus,
    SystemAutonomyRecommendation,
)
from agicore.trading.recovery_resilience_models import (
    RecoveryMode,
    RecoveryResilienceResult,
    RecoveryRisk,
    ResilienceScore,
)
from agicore.trading.strategic_memory_models import StrategicDriftSignal, StrategicTimelineAnalysis
from agicore.trading.system_integrity_models import (
    ModuleHealthStatus,
    ModuleIntegrityReport,
    SystemIntegrityResult,
    SystemIntegrityRisk,
    SystemIntegrityStatus,
)


def _integrity(status: SystemIntegrityStatus = SystemIntegrityStatus.HEALTHY, score: int = 85, modules: tuple[str, ...] = ()) -> SystemIntegrityResult:
    reports = tuple(
        ModuleIntegrityReport(name, ModuleHealthStatus.ISOLATE, 20, (SystemIntegrityRisk.MODULE_INSTABILITY,), ("bad",), True)
        for name in modules
    )
    return SystemIntegrityResult(status, score, (), reports, modules, "action", (), (), "integrity")


def _recovery(mode: RecoveryMode = RecoveryMode.NORMAL, score: int = 80, risks: tuple[RecoveryRisk, ...] = (), isolated: tuple[str, ...] = ()) -> RecoveryResilienceResult:
    breakdown = ResilienceScore(score, score, score, score, score, score, score)
    return RecoveryResilienceResult(mode, score, breakdown, risks, (), (), isolated, (), (), (), "recovery")


def _executive(mode: ExecutiveMode = ExecutiveMode.NORMAL, stop: bool = False) -> ExecutiveBrainResult:
    state = ExecutiveState(mode, ExecutiveIntent.CONTROLLED_GROWTH, ExecutiveRiskAppetite.MODERATE, "objective", (), ())
    decision = ExecutiveDecision(not stop, False, False, stop, "LABEL", "action")
    return ExecutiveBrainResult(state, decision, (), "executive")


def _supervisor(executable: bool = True, decision: SupervisorDecision = SupervisorDecision.APPROVE_SYSTEM_DECISION, overrides: tuple[SupervisorOverride, ...] = (SupervisorOverride.NONE,)) -> SupervisorResult:
    return SupervisorResult(decision, executable, overrides, (), (), (), (), (), (), "supervisor")


def _self_eval(confidence: int = 85, recommendation: SystemAutonomyRecommendation = SystemAutonomyRecommendation.MAINTAIN_AUTONOMY, status: SelfEvaluationStatus = SelfEvaluationStatus.STABLE) -> SelfEvaluationResult:
    score = SelfEvaluationScore(confidence, confidence, confidence, confidence, confidence, confidence, confidence)
    return SelfEvaluationResult(status, recommendation, confidence, score, (), (), (), (), "self")


def _governance(mode: LearningGovernanceMode = LearningGovernanceMode.LEARN, decision: LearningGovernanceDecision = LearningGovernanceDecision.ALLOW_LEARNING) -> LearningGovernanceResult:
    return LearningGovernanceResult(decision, mode, LearningCycleStatus.READY, (), (), (), (), (), "gov")


def _agent(score: int = 80, status: AgentConsensusStatus = AgentConsensusStatus.CONSENSUS_APPROVE, vote: AgentVote = AgentVote.APPROVE) -> AgentCoordinationResult:
    return AgentCoordinationResult(vote, status, score, (), (), (), (), "agent")


def _timeline(count: int = 4, health: int = 80, degradation: bool = False) -> StrategicTimelineAnalysis:
    drifts = (StrategicDriftSignal.PERSISTENT_DRAWDOWN,) if degradation else ()
    return StrategicTimelineAnalysis(count, (), drifts, None, None, health, health, not degradation, degradation, (), "timeline")


def test_full_operation_when_all_layers_are_stable() -> None:
    result = evaluate_mission_continuity(
        system_integrity=_integrity(),
        recovery_resilience=_recovery(),
        executive_result=_executive(),
        supervisor_result=_supervisor(),
        self_evaluation=_self_eval(),
        strategic_timeline_analysis=_timeline(),
    )

    assert result.mode == MissionContinuityMode.FULL_OPERATION
    assert result.continuity_score >= 70
    assert ContinuityAction.KEEP_CORE_RUNNING in result.actions
    assert ContinuityAction.PRESERVE_MEMORY in result.actions


def test_degraded_integrity_disables_non_critical_modules() -> None:
    states = prioritize_critical_modules(system_integrity=_integrity(SystemIntegrityStatus.DEGRADED, 65))
    disabled = {state.module_name for state in states if not state.enabled}

    assert "rl_playground" in disabled
    assert "scenario_replay_arena" in disabled
    assert all(state.enabled for state in states if state.criticality in {MissionCriticality.CRITICAL, MissionCriticality.HIGH})


def test_low_integrity_moves_to_essential_or_survival_mode() -> None:
    result = evaluate_mission_continuity(
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 25, modules=("paper_execution_loop", "rl_playground")),
        recovery_resilience=_recovery(RecoveryMode.SURVIVAL_MODE, 30),
    )

    assert result.mode in {MissionContinuityMode.SURVIVAL_CONTINUITY, MissionContinuityMode.SAFE_PAUSE}
    assert ContinuityRisk.CORE_FAILURE in result.risks
    assert ContinuityAction.ACTIVATE_SAFE_MODE in result.actions


def test_isolated_modules_trigger_isolated_operation() -> None:
    result = evaluate_mission_continuity(
        system_integrity=_integrity(SystemIntegrityStatus.DEGRADED, 60, modules=("paper_execution_loop",)),
        recovery_resilience=_recovery(RecoveryMode.ISOLATE_MODULES, 60, isolated=("paper_execution_loop",)),
    )

    assert result.mode == MissionContinuityMode.ISOLATED_OPERATION
    assert "paper_execution_loop" in result.disabled_modules
    assert ContinuityAction.ISOLATE_FAILURE_DOMAIN in result.actions


def test_supervision_failure_reduces_autonomy() -> None:
    risks = detect_continuity_risks(
        supervisor_result=_supervisor(False, SupervisorDecision.EMERGENCY_HALT, (SupervisorOverride.EMERGENCY_HALT,))
    )

    assert ContinuityRisk.SUPERVISION_FAILURE in risks

    actions = build_continuity_plan(
        supervisor_result=_supervisor(False, SupervisorDecision.EMERGENCY_HALT, (SupervisorOverride.EMERGENCY_HALT,))
    )
    assert ContinuityAction.REDUCE_AUTONOMY in actions


def test_learning_lockdown_freezes_learning() -> None:
    actions = build_continuity_plan(
        learning_governance=_governance(LearningGovernanceMode.SAFETY_LOCKDOWN, LearningGovernanceDecision.ENTER_SAFETY_LOCKDOWN)
    )

    assert ContinuityAction.FREEZE_LEARNING in actions


def test_memory_risk_detected_from_strategic_timeline() -> None:
    risks = detect_continuity_risks(strategic_timeline_analysis=_timeline(0, 25, degradation=True))

    assert ContinuityRisk.STRATEGIC_MEMORY_LOSS in risks
    assert ContinuityRisk.MEMORY_RISK in risks


def test_recovery_transition_when_rebuild_is_ready() -> None:
    result = evaluate_mission_continuity(
        recovery_resilience=_recovery(RecoveryMode.REBUILD_CONFIDENCE, 72),
        system_integrity=_integrity(SystemIntegrityStatus.DEGRADED, 72),
        self_evaluation=_self_eval(),
    )

    assert result.mode == MissionContinuityMode.RECOVERY_TRANSITION
    assert ContinuityAction.PREPARE_RECOVERY_PHASE in result.actions


def test_compute_continuity_score_penalizes_unstable_autonomy_and_consensus() -> None:
    score = compute_continuity_score(
        self_evaluation=_self_eval(35, SystemAutonomyRecommendation.FREEZE_AUTONOMY, SelfEvaluationStatus.AUTONOMY_REDUCED),
        agent_coordination=_agent(35, AgentConsensusStatus.NO_CONSENSUS),
        strategic_timeline_analysis=_timeline(0, 30, degradation=True),
    )

    assert score.autonomy_stability_score < 30
    assert score.supervision_score < 45
    assert score.memory_preservation_score < 20


def test_policy_memory_presence_keeps_memory_module_available() -> None:
    states = prioritize_critical_modules(policy_memory=AdaptivePolicyMemory())
    memory_state = next(state for state in states if state.module_name == "adaptive_policy_memory")

    assert memory_state.enabled
    assert memory_state.criticality == MissionCriticality.NORMAL


def test_render_mission_continuity_markdown_contains_required_sections() -> None:
    result = evaluate_mission_continuity(
        system_integrity=_integrity(SystemIntegrityStatus.DEGRADED, 65),
        recovery_resilience=_recovery(RecoveryMode.STABILIZE, 65),
        strategic_timeline_analysis=_timeline(),
    )

    markdown = render_mission_continuity_markdown(result)

    assert "# Autonomous Mission Continuity Engine" in markdown
    assert "## Mission Continuity Status" in markdown
    assert "## Continuity Score" in markdown
    assert "## Operating Mode" in markdown
    assert "## Critical Modules" in markdown
    assert "## Disabled Modules" in markdown
    assert "## Risks Detected" in markdown
    assert "## Continuity Actions" in markdown
    assert "## Recovery Preparation" in markdown
    assert "## AGIcore Recommendations" in markdown
    assert "no broker" in markdown
