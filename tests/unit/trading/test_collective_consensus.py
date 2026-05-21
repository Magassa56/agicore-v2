"""Unit tests for the offline Autonomous Consensus & Collective Intelligence Engine."""
from __future__ import annotations

from agicore.trading.collective_consensus import (
    aggregate_consensus_votes,
    apply_minority_safety_override,
    build_consensus_graph,
    compute_collective_confidence,
    detect_consensus_risks,
    evaluate_collective_consensus,
    render_collective_consensus_markdown,
    resolve_authority_conflicts,
)
from agicore.trading.collective_consensus_models import (
    ConsensusDecision,
    ConsensusMode,
    ConsensusParticipant,
    ConsensusRecommendation,
    ConsensusRisk,
    ConsensusState,
    ConsensusVote,
)
from agicore.trading.hierarchical_supervisor_models import SupervisorDecision, SupervisorOverride, SupervisorResult
from agicore.trading.intent_alignment_models import IntentAlignmentMode, IntentAlignmentResult, IntentAlignmentState, IntentConfidence, IntentPriority, IntentRisk
from agicore.trading.learning_governance_models import LearningCycleStatus, LearningGovernanceDecision, LearningGovernanceMode, LearningGovernanceResult
from agicore.trading.meta_cognition_models import CognitiveRigidity, MetaCognitionMode, MetaCognitionResult, MetaCognitiveConfidence, MetaCognitiveRisk
from agicore.trading.mission_continuity_models import MissionContinuityMode, MissionContinuityResult, MissionContinuityScore
from agicore.trading.multi_agent_models import AgentConsensusStatus, AgentCoordinationResult, AgentVote
from agicore.trading.operational_awareness_models import OperationalAwarenessMode, OperationalAwarenessResult, OperationalConfidenceScore, OperationalHealthStatus
from agicore.trading.recovery_resilience_models import RecoveryMode, RecoveryResilienceResult, RecoveryRisk, ResilienceScore
from agicore.trading.recursive_self_evaluation_models import SelfEvaluationResult, SelfEvaluationScore, SelfEvaluationStatus, SystemAutonomyRecommendation
from agicore.trading.strategic_arbitration_models import (
    ArbitrationDecision,
    ArbitrationMode,
    ArbitrationPriority,
    ArbitrationResult,
    ArbitrationSeverity,
    ArbitrationState,
    PriorityGraph,
)
from agicore.trading.system_integrity_models import SystemIntegrityResult, SystemIntegrityStatus


def _arbitration(decision: ArbitrationDecision = ArbitrationDecision.CONTINUE_OPERATION, confidence: int = 90, mode: ArbitrationMode = ArbitrationMode.NORMAL_OPERATION, emergency: bool = False) -> ArbitrationResult:
    graph = PriorityGraph((ArbitrationPriority.SURVIVAL, ArbitrationPriority.INTEGRITY), (), (ArbitrationPriority.PERFORMANCE,), ArbitrationPriority.PERFORMANCE)
    return ArbitrationResult(mode, ArbitrationState.STABLE, decision, ArbitrationSeverity.CRITICAL if emergency else ArbitrationSeverity.LOW, confidence, ArbitrationPriority.PERFORMANCE, (), (), (), graph, (), emergency, "arbitration", ())


def _alignment(mode: IntentAlignmentMode = IntentAlignmentMode.FULLY_ALIGNED, score: int = 90, risks: tuple[IntentRisk, ...] = ()) -> IntentAlignmentResult:
    confidence = IntentConfidence(score, score, score, score, score, score, score)
    return IntentAlignmentResult(mode, IntentAlignmentState.ALIGNED, score, confidence, (IntentPriority.SAFETY,), (), (), risks, (), "mission", score, (), "alignment")


def _meta(mode: MetaCognitionMode = MetaCognitionMode.SELF_AWARE, risks: tuple[MetaCognitiveRisk, ...] = (), score: int = 90) -> MetaCognitionResult:
    confidence = MetaCognitiveConfidence(score, score, score, score, score, score, score)
    return MetaCognitionResult(mode, score, confidence, CognitiveRigidity.FLEXIBLE, (), (), (), risks, (), score, "reflect", (), "meta")


def _awareness(score: int = 90, mode: OperationalAwarenessMode = OperationalAwarenessMode.STABLE, health: OperationalHealthStatus = OperationalHealthStatus.HEALTHY) -> OperationalAwarenessResult:
    breakdown = OperationalConfidenceScore(score, score, score, score, score, score, score, score, score)
    return OperationalAwarenessResult(mode, health, score, breakdown, (), (), (), (), 20, score, "monitor", (), "awareness")


def _mission(mode: MissionContinuityMode = MissionContinuityMode.FULL_OPERATION, score: int = 90) -> MissionContinuityResult:
    breakdown = MissionContinuityScore(score, score, score, score, score, score, score)
    return MissionContinuityResult(mode, score, breakdown, (), (), (), (), (), (), (), (), "mission")


def _recovery(mode: RecoveryMode = RecoveryMode.NORMAL, score: int = 90, risks: tuple[RecoveryRisk, ...] = ()) -> RecoveryResilienceResult:
    breakdown = ResilienceScore(score, score, score, score, score, score, score)
    return RecoveryResilienceResult(mode, score, breakdown, risks, (), (), (), (), (), (), "recovery")


def _integrity(status: SystemIntegrityStatus = SystemIntegrityStatus.HEALTHY, score: int = 90) -> SystemIntegrityResult:
    return SystemIntegrityResult(status, score, (), (), (), "action", (), (), "integrity")


def _governance(decision: LearningGovernanceDecision = LearningGovernanceDecision.PAUSE_LEARNING, mode: LearningGovernanceMode = LearningGovernanceMode.OBSERVE_ONLY) -> LearningGovernanceResult:
    return LearningGovernanceResult(decision, mode, LearningCycleStatus.OBSERVING, (), (), (), (), (), "governance")


def _self_eval(recommendation: SystemAutonomyRecommendation = SystemAutonomyRecommendation.REDUCE_AUTONOMY, status: SelfEvaluationStatus = SelfEvaluationStatus.STABLE, score: int = 90) -> SelfEvaluationResult:
    breakdown = SelfEvaluationScore(score, score, score, score, score, score, score)
    return SelfEvaluationResult(status, recommendation, score, breakdown, (), (), (), (), "self")


def _supervisor(executable: bool = True, decision: SupervisorDecision = SupervisorDecision.APPROVE_SYSTEM_DECISION) -> SupervisorResult:
    return SupervisorResult(decision, executable, (SupervisorOverride.NONE,), (), (), (), (), (), (), "supervisor")


def _agents(vote: AgentVote = AgentVote.APPROVE, score: int = 90, status: AgentConsensusStatus = AgentConsensusStatus.CONSENSUS_APPROVE) -> AgentCoordinationResult:
    return AgentCoordinationResult(vote, status, score, (), (), (), (), "agents")


def test_normal_consensus_approves_when_all_participants_agree() -> None:
    result = evaluate_collective_consensus(
        strategic_arbitration=_arbitration(),
        intent_alignment=_alignment(),
        meta_cognition=_meta(),
        operational_awareness=_awareness(),
        mission_continuity=_mission(),
        system_integrity=_integrity(),
        supervisor_result=_supervisor(),
        agent_coordination=_agents(),
    )

    assert result.mode == ConsensusMode.NORMAL_CONSENSUS
    assert result.state == ConsensusState.STABLE
    assert result.decision == ConsensusDecision.APPROVE_COLLECTIVE_DECISION
    assert result.collective_confidence_score >= 70


def test_weighted_votes_prioritize_safety_participants() -> None:
    participants = (
        ConsensusParticipant("performance", "profit", ConsensusVote.APPROVE, 90, 10, False),
        ConsensusParticipant("integrity", "safety", ConsensusVote.SAFE_MODE, 80, 8, True),
    )
    totals = aggregate_consensus_votes(participants=participants)

    assert totals[ConsensusVote.SAFE_MODE] >= totals[ConsensusVote.APPROVE] - 10


def test_minority_safety_override_blocks_dominant_approval() -> None:
    participants = (
        ConsensusParticipant("performance", "profit", ConsensusVote.APPROVE, 95, 10, False),
        ConsensusParticipant("system_integrity", "integrity", ConsensusVote.EMERGENCY_HALT, 70, 4, True),
    )

    assert apply_minority_safety_override(participants=participants)
    risks = detect_consensus_risks(participants=participants)
    assert ConsensusRisk.MINORITY_SAFETY_OVERRIDE in risks


def test_authority_conflict_requires_supervision() -> None:
    result = evaluate_collective_consensus(
        strategic_arbitration=_arbitration(ArbitrationDecision.CONTINUE_OPERATION, 90),
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 20),
        supervisor_result=_supervisor(False, SupervisorDecision.OVERRIDE_TO_BLOCK),
    )

    assert ConsensusRisk.AUTHORITY_CONFLICT in result.risks
    assert result.decision in {ConsensusDecision.ENTER_SAFE_MODE, ConsensusDecision.EMERGENCY_HALT, ConsensusDecision.REQUIRE_SUPERVISION}
    assert ConsensusRecommendation.REQUIRE_HUMAN_SUPERVISION in result.recommendations


def test_emergency_consensus_when_multiple_critical_layers_alert() -> None:
    result = evaluate_collective_consensus(
        strategic_arbitration=_arbitration(ArbitrationDecision.EMERGENCY_LOCKDOWN, 20, ArbitrationMode.EMERGENCY_LOCKDOWN, True),
        intent_alignment=_alignment(IntentAlignmentMode.CRITICAL_REALIGNMENT, 20, (IntentRisk.ALIGNMENT_COLLAPSE,)),
        operational_awareness=_awareness(20, OperationalAwarenessMode.CRITICAL, OperationalHealthStatus.COLLAPSING),
        recovery_resilience=_recovery(RecoveryMode.SURVIVAL_MODE, 20, (RecoveryRisk.SYSTEM_COMPROMISED,)),
        system_integrity=_integrity(SystemIntegrityStatus.COMPROMISED, 20),
    )

    assert result.mode == ConsensusMode.EMERGENCY_CONSENSUS
    assert result.decision == ConsensusDecision.EMERGENCY_HALT
    assert ConsensusRisk.EMERGENCY_ALIGNMENT_REQUIRED in result.risks


def test_collective_confidence_decreases_with_fragmentation() -> None:
    participants = (
        ConsensusParticipant("a", "x", ConsensusVote.APPROVE, 40, 5, False),
        ConsensusParticipant("b", "y", ConsensusVote.BLOCK, 40, 5, True),
        ConsensusParticipant("c", "z", ConsensusVote.REQUIRE_SUPERVISION, 40, 5, False),
    )
    graph = build_consensus_graph(participants=participants)
    confidence = compute_collective_confidence(participants=participants, graph=graph)

    assert confidence.weighted_confidence_score == 40
    assert confidence.agreement_score < 50


def test_consensus_collapse_when_confidence_is_very_low() -> None:
    participants = (
        ConsensusParticipant("a", "x", ConsensusVote.APPROVE, 20, 5, False),
        ConsensusParticipant("b", "y", ConsensusVote.BLOCK, 20, 5, True),
        ConsensusParticipant("c", "z", ConsensusVote.REQUIRE_SUPERVISION, 20, 5, False),
    )
    result = evaluate_collective_consensus()
    risks = detect_consensus_risks(participants=participants)

    assert ConsensusRisk.CONSENSUS_COLLAPSE_RISK in risks
    assert result.decision == ConsensusDecision.NO_CONSENSUS


def test_resolve_authority_conflicts_explains_disagreement() -> None:
    participants = (
        ConsensusParticipant("performance", "profit", ConsensusVote.APPROVE, 90, 10, False),
        ConsensusParticipant("supervisor", "supervision", ConsensusVote.BLOCK, 80, 10, True),
    )
    conflicts = resolve_authority_conflicts(participants=participants)

    assert conflicts
    assert "supervisor" in conflicts[0]


def test_agent_coordination_vote_maps_to_collective_block() -> None:
    result = evaluate_collective_consensus(agent_coordination=_agents(AgentVote.BLOCK, 85, AgentConsensusStatus.CONSENSUS_BLOCK))

    assert result.decision in {ConsensusDecision.BLOCK_COLLECTIVE_ACTION, ConsensusDecision.ENTER_SAFE_MODE}
    assert any(participant.name == "agent_coordination" for participant in result.participants)


def test_render_collective_consensus_markdown_contains_required_sections() -> None:
    result = evaluate_collective_consensus(
        strategic_arbitration=_arbitration(),
        intent_alignment=_alignment(),
        system_integrity=_integrity(),
        supervisor_result=_supervisor(),
    )
    markdown = render_collective_consensus_markdown(result)

    assert "# Autonomous Consensus & Collective Intelligence Engine" in markdown
    assert "## Collective Consensus State" in markdown
    assert "## Participants" in markdown
    assert "## Votes" in markdown
    assert "## Consensus Graph" in markdown
    assert "## Collective Confidence" in markdown
    assert "## Disagreements" in markdown
    assert "## Safety Overrides" in markdown
    assert "## Final Collective Decision" in markdown
    assert "## Recommendations" in markdown
    assert "no broker" in markdown
