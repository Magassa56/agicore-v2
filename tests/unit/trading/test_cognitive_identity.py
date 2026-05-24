from __future__ import annotations

from types import SimpleNamespace

from agicore.trading.cognitive_continuity_models import CognitiveContinuityRisk, CognitiveContinuityState
from agicore.trading.cognitive_governance_models import (
    CognitiveAutonomyLevel,
    CognitiveGovernanceDecision,
    CognitiveGovernanceMode,
)
from agicore.trading.cognitive_identity import (
    build_cognitive_identity_profile,
    build_cognitive_invariants,
    compute_cognitive_identity_score,
    detect_cognitive_identity_risks,
    evaluate_cognitive_identity,
    generate_cognitive_identity_recommendations,
    render_cognitive_identity_markdown,
)
from agicore.trading.cognitive_identity_models import (
    CognitiveIdentityAction,
    CognitiveIdentityMode,
    CognitiveIdentityRecommendation,
    CognitiveIdentityRisk,
    CognitiveIdentityState,
)
from agicore.trading.cognitive_policy_models import CognitivePolicyMode, CognitivePolicyRisk
from agicore.trading.cognitive_recovery_models import CognitiveRecoveryState
from agicore.trading.cognitive_resilience_models import CognitiveResilienceState
from agicore.trading.cognitive_stability_models import CognitiveStabilityState
from agicore.trading.collective_consensus_models import ConsensusDecision, ConsensusMode, ConsensusRisk
from agicore.trading.intent_alignment_models import IntentAlignmentMode, IntentRisk
from agicore.trading.mission_continuity_models import MissionContinuityMode
from agicore.trading.recursive_world_model_models import WorldModelDecision, WorldModelRisk
from agicore.trading.strategic_memory_models import StrategicDriftSignal
from agicore.trading.strategy_dna_models import StrategyDNA, StrategyRiskRules, TradeDirection
from agicore.trading.system_integrity_models import SystemIntegrityStatus


def _strategy(name="EMA20 Pullback"):
    return StrategyDNA(
        name=name,
        description="Controlled pullback strategy",
        allowed_direction=TradeDirection.BOTH,
        risk_rules=StrategyRiskRules(max_daily_loss=500, risk_per_trade=0.5),
    )


def _continuity(state=CognitiveContinuityState.CONTINUOUS, score=84, risks=()):
    return SimpleNamespace(state=state, continuity_score=score, risks=risks)


def _intent(mode=IntentAlignmentMode.FULLY_ALIGNED, confidence=84, risks=(), priority_score=84):
    return SimpleNamespace(
        mode=mode,
        alignment_confidence=confidence,
        risks=risks,
        confidence_breakdown=SimpleNamespace(priority_stability_score=priority_score),
    )


def _governance(
    mode=CognitiveGovernanceMode.NORMAL_GOVERNANCE,
    decision=CognitiveGovernanceDecision.APPROVE_COGNITIVE_OPERATION,
    score=84,
    autonomy=CognitiveAutonomyLevel.LIMITED_AUTONOMY,
):
    return SimpleNamespace(mode=mode, decision=decision, governance_score=score, autonomy_level=autonomy)


def _policy(mode=CognitivePolicyMode.POLICY_NORMAL, score=84, risks=()):
    return SimpleNamespace(mode=mode, cognitive_policy_score=score, risks=risks)


def _world(score=84, decision=WorldModelDecision.MAINTAIN_WORLD_MODEL, risks=()):
    return SimpleNamespace(world_model_coherence_score=score, decision=decision, risks=risks)


def _consensus(decision=ConsensusDecision.APPROVE_COLLECTIVE_DECISION, mode=ConsensusMode.NORMAL_CONSENSUS, score=84, risks=()):
    return SimpleNamespace(decision=decision, mode=mode, collective_confidence_score=score, risks=risks)


def _timeline(score=84, drifts=()):
    return SimpleNamespace(strategic_health_score=score, drift_signals=drifts)


def test_identity_stable_when_continuity_and_alignment_are_strong() -> None:
    result = evaluate_cognitive_identity(
        cognitive_continuity=_continuity(),
        intent_alignment=_intent(),
        cognitive_governance=_governance(),
        cognitive_policy=_policy(),
        recursive_world_model=_world(),
        collective_consensus=_consensus(),
        strategic_timeline_analysis=_timeline(),
        strategy_dna=_strategy(),
    )

    assert result.state == CognitiveIdentityState.IDENTITY_STABLE
    assert result.mode == CognitiveIdentityMode.NORMAL_IDENTITY
    assert result.identity_score >= 75
    assert result.actions == (CognitiveIdentityAction.PRESERVE_IDENTITY_PROFILE,)


def test_detects_identity_drift_and_mission_mismatch() -> None:
    risks = detect_cognitive_identity_risks(
        cognitive_continuity=_continuity(
            CognitiveContinuityState.IDENTITY_DRIFT,
            risks=(CognitiveContinuityRisk.STRATEGIC_IDENTITY_DRIFT,),
        ),
        intent_alignment=_intent(IntentAlignmentMode.MISALIGNED, 35, (IntentRisk.MISSION_DIVERGENCE,)),
        strategic_timeline_analysis=_timeline(35, (StrategicDriftSignal.STRATEGIC_DEGRADATION,)),
    )

    assert CognitiveIdentityRisk.STRATEGIC_IDENTITY_DRIFT in risks
    assert CognitiveIdentityRisk.MISSION_IDENTITY_MISMATCH in risks


def test_detects_priority_governance_policy_world_and_consensus_risks() -> None:
    risks = detect_cognitive_identity_risks(
        intent_alignment=_intent(IntentAlignmentMode.PRIORITY_CONFLICT, priority_score=35),
        cognitive_governance=_governance(
            CognitiveGovernanceMode.LOCKED_GOVERNANCE,
            CognitiveGovernanceDecision.ENTER_LOCKED_GOVERNANCE,
            35,
        ),
        cognitive_policy=_policy(
            CognitivePolicyMode.POLICY_LOCKED,
            35,
            (CognitivePolicyRisk.GOVERNANCE_POLICY_MISMATCH,),
        ),
        recursive_world_model=_world(35, WorldModelDecision.REBUILD_CAUSAL_GRAPH, (WorldModelRisk.WORLD_MODEL_INCOHERENCE,)),
        collective_consensus=_consensus(
            ConsensusDecision.NO_CONSENSUS,
            ConsensusMode.CONSENSUS_COLLAPSE,
            35,
            (ConsensusRisk.CONSENSUS_FRAGMENTATION,),
        ),
    )

    assert CognitiveIdentityRisk.PRIORITY_INVARIANT_BREAK in risks
    assert CognitiveIdentityRisk.GOVERNANCE_IDENTITY_CONFLICT in risks
    assert CognitiveIdentityRisk.POLICY_IDENTITY_CONFLICT in risks
    assert CognitiveIdentityRisk.WORLD_MODEL_IDENTITY_DRIFT in risks
    assert CognitiveIdentityRisk.CONSENSUS_IDENTITY_FRAGMENTATION in risks


def test_locks_identity_on_collapse_risk() -> None:
    result = evaluate_cognitive_identity(
        cognitive_continuity=_continuity(CognitiveContinuityState.CONTINUITY_FAILURE, 20),
        cognitive_stability=SimpleNamespace(state=CognitiveStabilityState.COLLAPSING),
        system_integrity=SimpleNamespace(status=SystemIntegrityStatus.COMPROMISED),
    )

    assert result.state == CognitiveIdentityState.IDENTITY_LOCKED
    assert result.mode == CognitiveIdentityMode.LOCKED_IDENTITY_MODE
    assert CognitiveIdentityRisk.IDENTITY_COLLAPSE_RISK in result.risks
    assert CognitiveIdentityAction.LOCK_IDENTITY_STATE in result.actions


def test_recovery_identity_discontinuity_maps_to_restoring_state() -> None:
    result = evaluate_cognitive_identity(
        cognitive_continuity=_continuity(CognitiveContinuityState.RECOVERING_CONTINUITY),
        cognitive_recovery=SimpleNamespace(state=CognitiveRecoveryState.RECOVERING),
        cognitive_resilience=SimpleNamespace(state=CognitiveResilienceState.RECOVERING),
    )

    assert result.state == CognitiveIdentityState.IDENTITY_RESTORING
    assert result.mode == CognitiveIdentityMode.IDENTITY_REPAIR
    assert CognitiveIdentityRisk.RECOVERY_IDENTITY_DISCONTINUITY in result.risks


def test_autonomy_expansion_is_limited_when_risks_exist() -> None:
    risks = detect_cognitive_identity_risks(
        intent_alignment=_intent(IntentAlignmentMode.MISALIGNED, 35),
        cognitive_governance=_governance(autonomy=CognitiveAutonomyLevel.FULL_AUTONOMY),
    )

    assert CognitiveIdentityRisk.AUTONOMY_IDENTITY_EXPANSION in risks


def test_score_penalizes_all_identity_components() -> None:
    score = compute_cognitive_identity_score(
        cognitive_continuity=_continuity(score=45),
        cognitive_governance=_governance(score=45),
        cognitive_policy=_policy(score=45),
        recursive_world_model=_world(score=45),
        collective_consensus=_consensus(score=45),
        intent_alignment=_intent(confidence=45, priority_score=45),
        strategic_timeline_analysis=_timeline(score=45),
        strategy_dna=_strategy(),
        risks=(
            CognitiveIdentityRisk.MISSION_IDENTITY_MISMATCH,
            CognitiveIdentityRisk.STRATEGIC_IDENTITY_DRIFT,
            CognitiveIdentityRisk.PRIORITY_INVARIANT_BREAK,
            CognitiveIdentityRisk.GOVERNANCE_IDENTITY_CONFLICT,
            CognitiveIdentityRisk.POLICY_IDENTITY_CONFLICT,
            CognitiveIdentityRisk.WORLD_MODEL_IDENTITY_DRIFT,
            CognitiveIdentityRisk.CONSENSUS_IDENTITY_FRAGMENTATION,
            CognitiveIdentityRisk.IDENTITY_COLLAPSE_RISK,
        ),
    )

    assert score.mission_alignment_score < 20
    assert score.strategic_dna_score < 20
    assert score.priority_invariant_score < 20
    assert score.consensus_identity_score < 20


def test_build_invariants_marks_violated_invariants_unprotected() -> None:
    invariants = build_cognitive_invariants(
        risks=(
            CognitiveIdentityRisk.MISSION_IDENTITY_MISMATCH,
            CognitiveIdentityRisk.POLICY_IDENTITY_CONFLICT,
        ),
        strategy_dna=_strategy(),
    )

    mission = next(invariant for invariant in invariants if invariant.name == "mission_continuity")
    discipline = next(invariant for invariant in invariants if invariant.name == "discipline_and_capital_preservation")
    assert mission.protected is False
    assert discipline.protected is False
    assert CognitiveIdentityRisk.MISSION_IDENTITY_MISMATCH in mission.violated_by


def test_profile_preserves_strategy_dna_and_core_priorities() -> None:
    profile = build_cognitive_identity_profile(identity_score=88, strategy_dna=_strategy("ORB Filter"))

    assert profile.strategy_name == "ORB Filter"
    assert "SAFETY" in profile.core_priorities
    assert profile.identity_score == 88
    assert profile.locked is False


def test_recommendations_cover_identity_controls() -> None:
    recommendations = generate_cognitive_identity_recommendations(
        risks=(
            CognitiveIdentityRisk.MISSION_IDENTITY_MISMATCH,
            CognitiveIdentityRisk.STRATEGIC_IDENTITY_DRIFT,
            CognitiveIdentityRisk.PRIORITY_INVARIANT_BREAK,
            CognitiveIdentityRisk.CONSENSUS_IDENTITY_FRAGMENTATION,
            CognitiveIdentityRisk.RECOVERY_IDENTITY_DISCONTINUITY,
            CognitiveIdentityRisk.AUTONOMY_IDENTITY_EXPANSION,
        ),
        state=CognitiveIdentityState.IDENTITY_AT_RISK,
    )

    assert CognitiveIdentityRecommendation.VERIFY_MISSION_ALIGNMENT in recommendations
    assert CognitiveIdentityRecommendation.PROTECT_STRATEGIC_DNA in recommendations
    assert CognitiveIdentityRecommendation.RECHECK_PRIORITY_ORDER in recommendations
    assert CognitiveIdentityRecommendation.REPAIR_IDENTITY_FRAGMENTATION in recommendations
    assert CognitiveIdentityRecommendation.LIMIT_AUTONOMY_EXPANSION in recommendations
    assert CognitiveIdentityRecommendation.REQUIRE_SUPERVISION in recommendations


def test_render_cognitive_identity_markdown_contains_required_sections() -> None:
    result = evaluate_cognitive_identity(
        cognitive_continuity=_continuity(),
        intent_alignment=_intent(),
        cognitive_governance=_governance(),
        cognitive_policy=_policy(),
        recursive_world_model=_world(),
        collective_consensus=_consensus(),
        strategy_dna=_strategy(),
    )
    markdown = render_cognitive_identity_markdown(result)

    assert "Cognitive Identity State" in markdown
    assert "Identity Score" in markdown
    assert "Identity Profile" in markdown
    assert "Core Invariants" in markdown
    assert "Identity Risks" in markdown
    assert "Actions" in markdown
    assert "Recommendations" in markdown
    assert "AGIcore Cognitive Identity Outlook" in markdown
