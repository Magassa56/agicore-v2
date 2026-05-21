"""Unit tests for the offline Autonomous Recovery & Resilience Engine."""
from __future__ import annotations

from agicore.trading.adaptive_policy_memory_models import (
    AdaptivePolicyMemory,
    PolicyMemoryEntry,
    PolicyMemoryRecommendation,
)
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
from agicore.trading.learning_governance_models import (
    LearningCycleStatus,
    LearningGovernanceDecision,
    LearningGovernanceMode,
    LearningGovernanceResult,
)
from agicore.trading.recursive_self_evaluation_models import (
    SelfEvaluationResult,
    SelfEvaluationScore,
    SelfEvaluationStatus,
    SystemAutonomyRecommendation,
)
from agicore.trading.recovery_resilience import (
    build_recovery_plan,
    compute_resilience_score,
    detect_recovery_risks,
    evaluate_recovery_resilience,
    render_recovery_resilience_markdown,
)
from agicore.trading.recovery_resilience_models import RecoveryAction, RecoveryMode, RecoveryRisk
from agicore.trading.strategic_memory_models import StrategicDriftSignal, StrategicTimelineAnalysis
from agicore.trading.system_integrity_models import (
    ModuleHealthStatus,
    ModuleIntegrityReport,
    SystemIntegrityResult,
    SystemIntegrityRisk,
    SystemIntegrityStatus,
)


def _integrity(
    status: SystemIntegrityStatus = SystemIntegrityStatus.HEALTHY,
    score: int = 85,
    modules: tuple[str, ...] = (),
    recommended_action: str = "MAINTAIN_MONITORED_OPERATION",
) -> SystemIntegrityResult:
    reports = tuple(
        ModuleIntegrityReport(name, ModuleHealthStatus.ISOLATE, 20, (SystemIntegrityRisk.MODULE_INSTABILITY,), ("bad",), True)
        for name in modules
    )
    return SystemIntegrityResult(status, score, (), reports, modules, recommended_action, (), (), "integrity")


def _self_eval(
    confidence: int = 85,
    recommendation: SystemAutonomyRecommendation = SystemAutonomyRecommendation.MAINTAIN_AUTONOMY,
    status: SelfEvaluationStatus = SelfEvaluationStatus.STABLE,
) -> SelfEvaluationResult:
    scores = SelfEvaluationScore(confidence, confidence, confidence, confidence, confidence, confidence, confidence)
    return SelfEvaluationResult(status, recommendation, confidence, scores, (), (), (), (), "self")


def _governance(
    decision: LearningGovernanceDecision = LearningGovernanceDecision.ALLOW_LEARNING,
    mode: LearningGovernanceMode = LearningGovernanceMode.LEARN,
) -> LearningGovernanceResult:
    return LearningGovernanceResult(decision, mode, LearningCycleStatus.READY, (), (), (), (), (), "gov")


def _cognitive(score: int = 80, load: CognitiveLoadLevel = CognitiveLoadLevel.LOW) -> CognitiveAdaptationResult:
    return CognitiveAdaptationResult(CognitiveAdaptationMode.ADAPT, load, score, CognitiveFlexibilityScore(score, score, score, score, score, score), (), (), (), ())


def _behavior(score: int = 80, pressure: BehavioralPressureLevel = BehavioralPressureLevel.LOW, recovery: BehavioralRecoveryState = BehavioralRecoveryState.STABLE) -> BehavioralStabilityResult:
    return BehavioralStabilityResult(score, pressure, recovery, BehavioralStabilityScore(score, score, score, score, score, score), (), (), (), ())


def _timeline(health: int = 80, degradation: bool = False) -> StrategicTimelineAnalysis:
    drifts = (StrategicDriftSignal.STRATEGIC_DEGRADATION,) if degradation else ()
    return StrategicTimelineAnalysis(4, (), drifts, None, None, health, health, not degradation, degradation, (), "timeline")


def _policy_memory(disabled: tuple[str, ...] = ("AGGRESSIVE",)) -> AdaptivePolicyMemory:
    entry = PolicyMemoryEntry("AGGRESSIVE", 10, -20.0, 35.0, 0.40, 0.1, 0.7, 0.2, 25, PolicyMemoryRecommendation.DISABLE_POLICY, (), ())
    return AdaptivePolicyMemory({"AGGRESSIVE": entry}, (), disabled)


def test_system_compromised_triggers_survival_mode() -> None:
    result = evaluate_recovery_resilience(system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 25))

    assert result.mode == RecoveryMode.SURVIVAL_MODE
    assert RecoveryRisk.SYSTEM_COMPROMISED in result.risks
    assert RecoveryAction.ENTER_SURVIVAL_MODE in result.actions


def test_rollback_recommended_triggers_strategic_rollback() -> None:
    result = evaluate_recovery_resilience(
        system_integrity=_integrity(SystemIntegrityStatus.ROLLBACK_RECOMMENDED, 20, recommended_action="ROLLBACK_RECOMMENDED")
    )

    assert result.mode == RecoveryMode.STRATEGIC_ROLLBACK
    assert RecoveryRisk.ROLLBACK_REQUIRED in result.risks
    assert RecoveryAction.RESTORE_LAST_STABLE_STATE in result.actions


def test_isolates_unstable_modules_from_integrity_reports() -> None:
    result = evaluate_recovery_resilience(system_integrity=_integrity(SystemIntegrityStatus.UNSTABLE, 45, modules=("safe_rl_layer",)))

    assert result.mode == RecoveryMode.ISOLATE_MODULES
    assert "safe_rl_layer" in result.isolated_modules
    assert RecoveryAction.ISOLATE_UNSTABLE_MODULE in result.actions


def test_freezes_learning_when_governance_locked() -> None:
    plan = build_recovery_plan(
        learning_governance=_governance(
            LearningGovernanceDecision.ENTER_SAFETY_LOCKDOWN,
            LearningGovernanceMode.SAFETY_LOCKDOWN,
        )
    )

    assert any(step.action == RecoveryAction.FREEZE_LEARNING for step in plan)


def test_reduces_autonomy_on_low_self_evaluation_confidence() -> None:
    risks = detect_recovery_risks(
        self_evaluation=_self_eval(35, SystemAutonomyRecommendation.REDUCE_AUTONOMY, SelfEvaluationStatus.AUTONOMY_REDUCED)
    )

    assert RecoveryRisk.LOW_CONFIDENCE in risks


def test_disables_dangerous_policies_from_policy_memory() -> None:
    result = evaluate_recovery_resilience(policy_memory=_policy_memory())

    assert RecoveryRisk.POLICY_FAILURE in result.risks
    assert "AGGRESSIVE" in result.disabled_policies
    assert RecoveryAction.DISABLE_DANGEROUS_POLICY in result.actions


def test_compute_resilience_score_penalizes_spiral_and_overload() -> None:
    score = compute_resilience_score(
        behavioral_stability=_behavior(30, BehavioralPressureLevel.EXTREME, BehavioralRecoveryState.CRITICAL),
        cognitive_adaptation=_cognitive(30, CognitiveLoadLevel.OVERLOADED),
        strategic_timeline_analysis=_timeline(30, degradation=True),
    )

    assert score.behavioral_resilience_score < 30
    assert score.cognitive_resilience_score < 20
    assert score.strategic_resilience_score < 30


def test_paused_recovery_for_multiple_critical_risks() -> None:
    result = evaluate_recovery_resilience(
        system_integrity=_integrity(SystemIntegrityStatus.PROTECTION_MODE, 20, modules=("safe_rl_layer",)),
        learning_governance=_governance(LearningGovernanceDecision.ENTER_SAFETY_LOCKDOWN, LearningGovernanceMode.SAFETY_LOCKDOWN),
        cognitive_adaptation=_cognitive(20, CognitiveLoadLevel.OVERLOADED),
        behavioral_stability=_behavior(20, BehavioralPressureLevel.EXTREME, BehavioralRecoveryState.CRITICAL),
        strategic_timeline_analysis=_timeline(20, degradation=True),
    )

    assert result.mode == RecoveryMode.PAUSED_RECOVERY
    assert RecoveryAction.REQUIRE_HUMAN_REVIEW in result.actions


def test_stable_system_keeps_running_and_can_rebuild_gradually() -> None:
    result = evaluate_recovery_resilience(
        system_integrity=_integrity(),
        self_evaluation=_self_eval(),
        behavioral_stability=_behavior(),
        cognitive_adaptation=_cognitive(),
    )

    assert result.mode in {RecoveryMode.NORMAL, RecoveryMode.REBUILD_CONFIDENCE}
    assert RecoveryAction.KEEP_RUNNING in result.actions
    assert RecoveryAction.REBUILD_GRADUALLY in result.actions
    assert result.resilience_score >= 70


def test_render_recovery_resilience_markdown_contains_required_sections() -> None:
    result = evaluate_recovery_resilience(
        system_integrity=_integrity(SystemIntegrityStatus.UNSTABLE, 45, modules=("governance",)),
        policy_memory=_policy_memory(),
    )

    markdown = render_recovery_resilience_markdown(result)

    assert "# Autonomous Recovery & Resilience Engine" in markdown
    assert "## Mode recuperation" in markdown
    assert "## Score resilience" in markdown
    assert "## Risques detectes" in markdown
    assert "## Actions recovery" in markdown
    assert "## Modules isoles" in markdown
    assert "## Politiques desactivees" in markdown
    assert "## Plan de reconstruction" in markdown
    assert "## Recommandations AGIcore" in markdown
    assert "no broker" in markdown
