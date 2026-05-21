"""Unit tests for the offline Autonomous Learning Governance Core."""
from __future__ import annotations

from agicore.trading.adaptive_policy_memory_models import (
    AdaptivePolicyMemory,
    PolicyContextSignature,
    PolicyMemoryEntry,
    PolicyMemoryRecommendation,
    PolicyPerformanceSnapshot,
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
    CognitiveAdaptationSignal,
    CognitiveFlexibilityScore,
    CognitiveLoadLevel,
)
from agicore.trading.learning_governance import (
    decide_learning_mode,
    detect_learning_risks,
    evaluate_learning_governance,
    render_learning_governance_markdown,
)
from agicore.trading.learning_governance_models import (
    LearningGovernanceDecision,
    LearningGovernanceMode,
    LearningGovernanceRisk,
)
from agicore.trading.meta_strategy_models import MetaStrategyDecision, MetaStrategySelectionResult
from agicore.trading.offline_dataset_models import DatasetQualityReport, OfflineLearningDataset
from agicore.trading.reward_models import RewardBreakdown, RewardComponent, RewardEvaluationResult, RewardLabel
from agicore.trading.rl_playground_models import RLExperimentConfig, RLPlaygroundResult, RLPolicyCandidate, RLPolicyScore
from agicore.trading.safe_rl_models import SafeRLExperimentResult, SafeRLStatus
from agicore.trading.strategic_memory_models import StrategicDriftSignal, StrategicTimelineAnalysis
from agicore.trading.tactical_execution_models import (
    TacticalExecutionEvent,
    TacticalExecutionQuality,
    TacticalExecutionResult,
    TacticalExecutionSignal,
    TacticalScoreBreakdown,
)


def _dataset(quality: int = 80, transitions: int = 25, dangerous: int = 0) -> DatasetQualityReport:
    return DatasetQualityReport(transitions, 12, 4, 12, dangerous, 1, 0, 0, quality, ())


def _reward(label: RewardLabel = RewardLabel.GOOD_DECISION, normalized: int = 75, total: int = 20) -> RewardEvaluationResult:
    c = RewardComponent("x", 0, "x")
    return RewardEvaluationResult(total, normalized, label, RewardBreakdown(c, c, c, c, c, c, c, c, c, c, c), (), ())


def _safe(status: SafeRLStatus = SafeRLStatus.SAFE) -> SafeRLExperimentResult:
    return SafeRLExperimentResult(status, (), (), (), (), (), (), "safe")


def _behavior(score: int = 80, pressure: BehavioralPressureLevel = BehavioralPressureLevel.LOW) -> BehavioralStabilityResult:
    return BehavioralStabilityResult(
        score,
        pressure,
        BehavioralRecoveryState.STABLE if score >= 60 else BehavioralRecoveryState.DETERIORATING,
        BehavioralStabilityScore(score, score, score, score, score, score),
        (),
        (),
        (),
        (),
    )


def _cognitive(
    mode: CognitiveAdaptationMode = CognitiveAdaptationMode.ADAPT,
    load: CognitiveLoadLevel = CognitiveLoadLevel.LOW,
    signals: tuple[CognitiveAdaptationSignal, ...] = (),
) -> CognitiveAdaptationResult:
    return CognitiveAdaptationResult(
        mode,
        load,
        80,
        CognitiveFlexibilityScore(80, 75, 80, 75, 75, 75),
        signals,
        (),
        (),
        (),
    )


def _policy_memory(dangerous: bool = False, disabled: tuple[str, ...] = ()) -> AdaptivePolicyMemory:
    recommendation = PolicyMemoryRecommendation.DISABLE_POLICY if dangerous else PolicyMemoryRecommendation.KEEP_POLICY
    entry = PolicyMemoryEntry("BALANCED", 10, 20, 75, 0.25 if dangerous else 0.02, 0.2, 0.7, 0.1, 80, recommendation, (), ())
    conservative = PolicyMemoryEntry("CONSERVATIVE", 6, 12, 70, 0.01, 0.35, 0.5, 0.15, 75, PolicyMemoryRecommendation.KEEP_POLICY, (), ())
    return AdaptivePolicyMemory(entries={"BALANCED": entry, "CONSERVATIVE": conservative}, disabled_policies=disabled)


def _playground(one_policy: bool = False) -> RLPlaygroundResult:
    score = RLPolicyScore("BALANCED", 50, 10, 0.0, 0.1, 0.8, 80, 10, 5, 3, 2, ())
    candidates = (RLPolicyCandidate("BALANCED", 60, 55, True, True, True),)
    ranked = (score,) if one_policy else (score, RLPolicyScore("CONSERVATIVE", 40, 8, 0, 0.2, 0.9, 75, 10, 4, 4, 2, ()))
    return RLPlaygroundResult(RLExperimentConfig(), OfflineLearningDataset(()), candidates, (), ranked, score, ())


def _meta(decision: MetaStrategyDecision = MetaStrategyDecision.SELECT_POLICY) -> MetaStrategySelectionResult:
    return MetaStrategySelectionResult("BALANCED", decision, 75, (), (), (), False, "ok")


def _timeline(degradation: bool = False, drifts: tuple[StrategicDriftSignal, ...] = ()) -> StrategicTimelineAnalysis:
    return StrategicTimelineAnalysis(4, (), drifts, None, None, 80 if not degradation else 40, 80 if not degradation else 35, False, degradation, (), "timeline")


def _tactical(quality: TacticalExecutionQuality = TacticalExecutionQuality.GOOD) -> TacticalExecutionResult:
    return TacticalExecutionResult(quality, 75, TacticalScoreBreakdown(75, 75, 75, 75, 75, 75, 75), (TacticalExecutionSignal.TACTICAL_DISCIPLINE_STRONG,), (), (), (TacticalExecutionEvent(quality, "ok", __import__("datetime").datetime.now(__import__("datetime").UTC)),))


def test_allows_learning_when_inputs_are_stable() -> None:
    result = evaluate_learning_governance(
        cognitive_adaptation=_cognitive(),
        behavioral_stability=_behavior(),
        dataset_quality=_dataset(),
        safe_rl_result=_safe(),
        reward_evaluation=_reward(),
        rl_playground=_playground(),
        policy_memory=_policy_memory(),
    )

    assert result.mode == LearningGovernanceMode.LEARN
    assert result.decision == LearningGovernanceDecision.ALLOW_LEARNING


def test_observe_only_for_low_dataset_quality() -> None:
    mode = decide_learning_mode(dataset_quality=_dataset(quality=45, transitions=4), reward_evaluation=_reward())

    assert mode == LearningGovernanceMode.OBSERVE_ONLY
    assert LearningGovernanceRisk.LOW_DATASET_QUALITY in detect_learning_risks(dataset_quality=_dataset(45, 4))


def test_freezes_learning_on_safe_rl_blocked() -> None:
    result = evaluate_learning_governance(safe_rl_result=_safe(SafeRLStatus.BLOCKED), dataset_quality=_dataset())

    assert result.mode == LearningGovernanceMode.FREEZE_LEARNING
    assert result.decision == LearningGovernanceDecision.FREEZE_POLICY_UPDATE


def test_safety_lockdown_on_multiple_critical_risks() -> None:
    result = evaluate_learning_governance(
        safe_rl_result=_safe(SafeRLStatus.BLOCKED),
        cognitive_adaptation=_cognitive(load=CognitiveLoadLevel.OVERLOADED, signals=(CognitiveAdaptationSignal.COGNITIVE_OVERLOAD,)),
        behavioral_stability=_behavior(25, BehavioralPressureLevel.EXTREME),
    )

    assert result.mode == LearningGovernanceMode.SAFETY_LOCKDOWN
    assert result.decision == LearningGovernanceDecision.ENTER_SAFETY_LOCKDOWN


def test_locks_dangerous_policy_from_memory() -> None:
    result = evaluate_learning_governance(policy_memory=_policy_memory(dangerous=True), dataset_quality=_dataset(), reward_evaluation=_reward())

    assert result.decision == LearningGovernanceDecision.LOCK_DANGEROUS_POLICY
    assert "BALANCED" in result.locked_policies


def test_detects_overfitting_when_one_policy_dominates() -> None:
    risks = detect_learning_risks(rl_playground=_playground(one_policy=True))

    assert LearningGovernanceRisk.OVERFITTING_RISK in risks


def test_detects_reward_hacking_with_high_reward_and_danger() -> None:
    risks = detect_learning_risks(
        reward_evaluation=_reward(RewardLabel.EXCELLENT_DECISION, 95, 80),
        tactical_execution=_tactical(TacticalExecutionQuality.DANGEROUS),
        dataset_quality=_dataset(dangerous=2),
    )

    assert LearningGovernanceRisk.REWARD_HACKING_RISK in risks


def test_reduce_adaptation_on_excessive_adaptation_signal() -> None:
    result = evaluate_learning_governance(
        cognitive_adaptation=_cognitive(signals=(CognitiveAdaptationSignal.OVER_REACTION_RISK,)),
        dataset_quality=_dataset(),
        reward_evaluation=_reward(),
    )

    assert result.mode == LearningGovernanceMode.REDUCE_ADAPTATION
    assert result.decision == LearningGovernanceDecision.ALLOW_LIMITED_LEARNING


def test_recovery_mode_for_behavioral_instability() -> None:
    result = evaluate_learning_governance(behavioral_stability=_behavior(35, BehavioralPressureLevel.HIGH), dataset_quality=_dataset())

    assert result.mode == LearningGovernanceMode.RECOVERY_MODE
    assert result.decision == LearningGovernanceDecision.PAUSE_LEARNING


def test_exploit_only_for_stable_pattern() -> None:
    result = evaluate_learning_governance(
        cognitive_adaptation=_cognitive(CognitiveAdaptationMode.EXPLOIT_STABLE_PATTERN),
        reward_evaluation=_reward(RewardLabel.GOOD_DECISION, 80, 25),
        dataset_quality=_dataset(),
        behavioral_stability=_behavior(),
    )

    assert result.mode == LearningGovernanceMode.EXPLOIT_ONLY
    assert result.decision == LearningGovernanceDecision.FREEZE_POLICY_UPDATE


def test_detects_policy_drift_from_meta_block_and_timeline() -> None:
    risks = detect_learning_risks(
        meta_strategy=_meta(MetaStrategyDecision.BLOCK_ALL_POLICIES),
        strategic_timeline_analysis=_timeline(True, (StrategicDriftSignal.DANGEROUS_POLICY,)),
    )

    assert LearningGovernanceRisk.POLICY_DRIFT_RISK in risks
    assert LearningGovernanceRisk.STRATEGIC_DEGRADATION in risks


def test_detects_excessive_adaptation_from_policy_snapshots() -> None:
    snapshots = tuple(
        PolicyPerformanceSnapshot(f"P{i}", 10, 70, 70, 0, 0.2, 0.7, 0.1, PolicyContextSignature())
        for i in range(5)
    )
    memory = AdaptivePolicyMemory(snapshots=snapshots)

    assert LearningGovernanceRisk.EXCESSIVE_ADAPTATION in detect_learning_risks(policy_memory=memory)


def test_render_learning_governance_markdown_contains_required_sections() -> None:
    result = evaluate_learning_governance(
        cognitive_adaptation=_cognitive(),
        behavioral_stability=_behavior(),
        dataset_quality=_dataset(),
        safe_rl_result=_safe(),
        reward_evaluation=_reward(),
        rl_playground=_playground(),
        policy_memory=_policy_memory(),
    )

    markdown = render_learning_governance_markdown(result)

    assert "# Autonomous Learning Governance Core" in markdown
    assert "## Decision gouvernance" in markdown
    assert "## Mode apprentissage" in markdown
    assert "## Risques detectes" in markdown
    assert "## Politiques verrouillees" in markdown
    assert "## Conditions d'apprentissage" in markdown
    assert "## Actions recommandees" in markdown
    assert "## Securite AGIcore" in markdown
    assert "no broker" in markdown
