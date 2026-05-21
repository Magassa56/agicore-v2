"""Offline Autonomous Consensus & Collective Intelligence Engine for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .collective_consensus_models import (
    CollectiveConfidence,
    ConsensusDecision,
    ConsensusEvent,
    ConsensusGraph,
    ConsensusInput,
    ConsensusMode,
    ConsensusParticipant,
    ConsensusRecommendation,
    ConsensusResult,
    ConsensusRisk,
    ConsensusState,
    ConsensusVote,
)
from .hierarchical_supervisor_models import SupervisorDecision
from .intent_alignment_models import IntentAlignmentMode, IntentRisk
from .learning_governance_models import LearningGovernanceDecision, LearningGovernanceMode
from .meta_cognition_models import MetaCognitionMode, MetaCognitiveRisk
from .mission_continuity_models import MissionContinuityMode
from .multi_agent_models import AgentConsensusStatus, AgentVote
from .operational_awareness_models import OperationalAwarenessMode, OperationalHealthStatus
from .recovery_resilience_models import RecoveryMode, RecoveryRisk
from .recursive_self_evaluation_models import SelfEvaluationStatus, SystemAutonomyRecommendation
from .strategic_arbitration_models import ArbitrationDecision, ArbitrationMode, ArbitrationSeverity
from .system_integrity_models import SystemIntegrityStatus


SAFETY_VOTES = {ConsensusVote.BLOCK, ConsensusVote.SAFE_MODE, ConsensusVote.EMERGENCY_HALT}
APPROVAL_VOTES = {ConsensusVote.APPROVE, ConsensusVote.REDUCE_AUTONOMY}


def build_consensus_graph(
    consensus_input: ConsensusInput | None = None,
    *,
    participants: tuple[ConsensusParticipant, ...] | None = None,
    **kwargs,
) -> ConsensusGraph:
    """Build the weighted participant graph used for collective consensus."""
    data = _input(consensus_input, **kwargs)
    resolved = participants or _participants_from_input(data)
    dominant = _dominant_participant(resolved)
    safety = tuple(participant.name for participant in resolved if participant.safety_critical)
    disagreement_pairs: list[tuple[str, str]] = []
    edges: list[tuple[str, str, str]] = []
    for left_index, left in enumerate(resolved):
        for right in resolved[left_index + 1 :]:
            relation = "agree" if _vote_family(left.vote) == _vote_family(right.vote) else "disagree"
            edges.append((left.name, right.name, relation))
            if relation == "disagree":
                disagreement_pairs.append((left.name, right.name))
    return ConsensusGraph(resolved, tuple(edges), dominant, safety, tuple(disagreement_pairs))


def aggregate_consensus_votes(
    consensus_input: ConsensusInput | None = None,
    *,
    participants: tuple[ConsensusParticipant, ...] | None = None,
    **kwargs,
) -> dict[ConsensusVote, int]:
    """Aggregate participant votes by confidence-weighted authority."""
    data = _input(consensus_input, **kwargs)
    resolved = participants or _participants_from_input(data)
    totals = {vote: 0 for vote in ConsensusVote}
    for participant in resolved:
        multiplier = 1.25 if participant.safety_critical and participant.vote in SAFETY_VOTES else 1.0
        totals[participant.vote] += int(round(participant.weight * participant.confidence / 100 * multiplier))
    return totals


def detect_consensus_risks(
    consensus_input: ConsensusInput | None = None,
    *,
    participants: tuple[ConsensusParticipant, ...] | None = None,
    graph: ConsensusGraph | None = None,
    vote_totals: dict[ConsensusVote, int] | None = None,
    confidence: CollectiveConfidence | None = None,
    **kwargs,
) -> tuple[ConsensusRisk, ...]:
    """Detect fragmentation, authority conflicts, unsafe dominance and collapse risk."""
    data = _input(consensus_input, **kwargs)
    resolved = participants or _participants_from_input(data)
    resolved_graph = graph or build_consensus_graph(data, participants=resolved)
    totals = vote_totals or aggregate_consensus_votes(data, participants=resolved)
    resolved_confidence = confidence or compute_collective_confidence(data, participants=resolved, graph=resolved_graph, vote_totals=totals)
    risks: list[ConsensusRisk] = []

    if resolved_confidence.agreement_score < 55 or len(resolved_graph.disagreement_pairs) >= max(2, len(resolved)):
        risks.append(ConsensusRisk.CONSENSUS_FRAGMENTATION)
    if resolved_confidence.weighted_confidence_score < 55 or resolved_confidence.reasoning_coherence_score < 50:
        risks.append(ConsensusRisk.LOW_COLLECTIVE_CONFIDENCE)
    if _authority_conflict(resolved):
        risks.append(ConsensusRisk.AUTHORITY_CONFLICT)
    if apply_minority_safety_override(data, participants=resolved):
        risks.append(ConsensusRisk.MINORITY_SAFETY_OVERRIDE)
    if _dominant_unsafe(resolved, totals):
        risks.append(ConsensusRisk.DOMINANT_UNSAFE_PARTICIPANT)
    if len({ _vote_family(participant.vote) for participant in resolved if participant.vote != ConsensusVote.ABSTAIN }) >= 3:
        risks.append(ConsensusRisk.DISAGREEMENT_ESCALATION)
    if _reasoning_drift(data):
        risks.append(ConsensusRisk.COLLECTIVE_REASONING_DRIFT)
    if resolved_confidence.weighted_confidence_score < 35 or (ConsensusRisk.CONSENSUS_FRAGMENTATION in risks and ConsensusRisk.AUTHORITY_CONFLICT in risks):
        risks.append(ConsensusRisk.CONSENSUS_COLLAPSE_RISK)
    if _emergency_required(data, resolved):
        risks.append(ConsensusRisk.EMERGENCY_ALIGNMENT_REQUIRED)

    return tuple(dict.fromkeys(risks))


def compute_collective_confidence(
    consensus_input: ConsensusInput | None = None,
    *,
    participants: tuple[ConsensusParticipant, ...] | None = None,
    graph: ConsensusGraph | None = None,
    vote_totals: dict[ConsensusVote, int] | None = None,
    **kwargs,
) -> CollectiveConfidence:
    """Compute collective confidence component scores from 0..100."""
    data = _input(consensus_input, **kwargs)
    resolved = participants or _participants_from_input(data)
    resolved_graph = graph or build_consensus_graph(data, participants=resolved)
    totals = vote_totals or aggregate_consensus_votes(data, participants=resolved)
    total_weight = sum(max(1, participant.weight) for participant in resolved) or 1
    weighted = sum(participant.confidence * participant.weight for participant in resolved) / total_weight
    active_votes = [participant.vote for participant in resolved if participant.vote != ConsensusVote.ABSTAIN]
    largest_family = max((_vote_family_count(active_votes, family) for family in {"approve", "review", "block", "safe", "halt"}), default=0)
    agreement = int(round(100 * largest_family / max(1, len(active_votes))))
    safety_alert_weight = totals[ConsensusVote.BLOCK] + totals[ConsensusVote.SAFE_MODE] + totals[ConsensusVote.EMERGENCY_HALT]
    approval_weight = totals[ConsensusVote.APPROVE] + totals[ConsensusVote.REDUCE_AUTONOMY]
    safety_alignment = 85
    if safety_alert_weight and approval_weight > safety_alert_weight:
        safety_alignment -= 30
    if _emergency_required(data, resolved):
        safety_alignment -= 20
    authority = 85 - min(40, len(resolve_authority_conflicts(data, participants=resolved)) * 12)
    reasoning = 85
    if data.meta_cognition is not None:
        reasoning = min(reasoning, data.meta_cognition.confidence_score)
        if data.meta_cognition.mode in {MetaCognitionMode.CONTRADICTORY, MetaCognitionMode.DEGRADED_REASONING, MetaCognitionMode.RECALIBRATION_REQUIRED}:
            reasoning -= 20
    if data.intent_alignment is not None:
        reasoning = min(reasoning, data.intent_alignment.alignment_confidence)
    autonomy = 85
    if data.self_evaluation is not None:
        autonomy = min(autonomy, data.self_evaluation.score_breakdown.autonomy_readiness_score)
    if _unsafe_autonomy(data):
        autonomy -= 25

    return CollectiveConfidence(
        weighted_confidence_score=_clamp(weighted),
        agreement_score=_clamp(agreement),
        safety_alignment_score=_clamp(safety_alignment),
        authority_stability_score=_clamp(authority),
        reasoning_coherence_score=_clamp(reasoning),
        autonomy_safety_score=_clamp(autonomy),
    )


def resolve_authority_conflicts(
    consensus_input: ConsensusInput | None = None,
    *,
    participants: tuple[ConsensusParticipant, ...] | None = None,
    **kwargs,
) -> tuple[str, ...]:
    """Resolve and describe conflicts between high-authority participants."""
    data = _input(consensus_input, **kwargs)
    resolved = participants or _participants_from_input(data)
    conflicts: list[str] = []
    safety_votes = [participant for participant in resolved if participant.safety_critical and participant.vote in SAFETY_VOTES]
    approval_votes = [participant for participant in resolved if participant.weight >= 7 and participant.vote == ConsensusVote.APPROVE]
    for safety in safety_votes:
        for approval in approval_votes:
            conflicts.append(f"{safety.name} safety vote conflicts with {approval.name} approval.")
    return tuple(dict.fromkeys(conflicts))


def apply_minority_safety_override(
    consensus_input: ConsensusInput | None = None,
    *,
    participants: tuple[ConsensusParticipant, ...] | None = None,
    **kwargs,
) -> bool:
    """Apply minority safety override when any critical subsystem blocks with confidence."""
    data = _input(consensus_input, **kwargs)
    resolved = participants or _participants_from_input(data)
    return any(
        participant.safety_critical
        and participant.vote in SAFETY_VOTES
        and (participant.confidence >= 65 or participant.vote == ConsensusVote.EMERGENCY_HALT)
        for participant in resolved
    ) or _emergency_required(data, resolved)


def evaluate_collective_consensus(
    consensus_input: ConsensusInput | None = None,
    **kwargs,
) -> ConsensusResult:
    """Run the full offline collective consensus pipeline."""
    data = _input(consensus_input, **kwargs)
    participants = _participants_from_input(data)
    graph = build_consensus_graph(data, participants=participants)
    totals = aggregate_consensus_votes(data, participants=participants)
    confidence = compute_collective_confidence(data, participants=participants, graph=graph, vote_totals=totals)
    risks = detect_consensus_risks(data, participants=participants, graph=graph, vote_totals=totals, confidence=confidence)
    safety_override = apply_minority_safety_override(data, participants=participants)
    disagreements = resolve_authority_conflicts(data, participants=participants)
    decision = _decision(totals, risks, safety_override, confidence)
    mode = _mode(decision, risks, safety_override, confidence)
    state = _state(decision, risks, disagreements)
    recommendations = _recommendations(decision, risks)
    score = _global_confidence(confidence, risks, disagreements, safety_override)
    overrides = _safety_overrides(participants) if safety_override else ()
    event = ConsensusEvent(
        mode,
        decision,
        f"Collective consensus selected {decision.value} with confidence {score}/100.",
        datetime.now(UTC),
    )
    return ConsensusResult(
        mode,
        state,
        decision,
        score,
        confidence,
        participants,
        graph,
        totals,
        tuple(disagreements),
        overrides,
        risks,
        recommendations,
        _final_message(decision, score, risks),
        (event,),
    )


def render_collective_consensus_markdown(result: ConsensusResult) -> str:
    """Render collective consensus as Markdown."""
    lines = [
        "# Autonomous Consensus & Collective Intelligence Engine",
        "",
        "## Collective Consensus State",
        "",
        f"- Mode: {result.mode.value}",
        f"- State: {result.state.value}",
        "",
        "## Participants",
        "",
        *_bullet_lines(tuple(f"{participant.name}: {participant.vote.value} ({participant.confidence}/100, weight {participant.weight})" for participant in result.participants)),
        "",
        "## Votes",
        "",
        *_bullet_lines(tuple(f"{vote.value}: {weight}" for vote, weight in result.vote_totals.items() if weight > 0)),
        "",
        "## Consensus Graph",
        "",
        f"- Dominant participant: {result.graph.dominant_participant or 'None'}",
        *_bullet_lines(tuple(f"{left} - {relation} - {right}" for left, right, relation in result.graph.edges)),
        "",
        "## Collective Confidence",
        "",
        f"- {result.collective_confidence_score}/100",
        "",
        "## Disagreements",
        "",
        *_bullet_lines(result.disagreements),
        "",
        "## Safety Overrides",
        "",
        *_bullet_lines(result.safety_overrides),
        "",
        "## Final Collective Decision",
        "",
        f"- {result.decision.value}",
        f"- {result.final_message}",
        "",
        "## Recommendations",
        "",
        *_bullet_lines(tuple(recommendation.value for recommendation in result.recommendations)),
        "",
        "- Offline only: no broker, no real order, no external API, no external ML, no external LLM, no neural training, no live execution.",
        "",
    ]
    return "\n".join(lines)


def _participants_from_input(data: ConsensusInput) -> tuple[ConsensusParticipant, ...]:
    participants: list[ConsensusParticipant] = []
    if data.strategic_arbitration is not None:
        vote = {
            ArbitrationDecision.CONTINUE_OPERATION: ConsensusVote.APPROVE,
            ArbitrationDecision.REDUCE_RISK: ConsensusVote.REDUCE_AUTONOMY,
            ArbitrationDecision.ENABLE_SAFE_MODE: ConsensusVote.SAFE_MODE,
            ArbitrationDecision.FREEZE_LEARNING: ConsensusVote.REQUIRE_SUPERVISION,
            ArbitrationDecision.REQUIRE_SUPERVISION: ConsensusVote.REQUIRE_SUPERVISION,
            ArbitrationDecision.ROLLBACK_STRATEGY: ConsensusVote.SAFE_MODE,
            ArbitrationDecision.STOP_EXECUTION: ConsensusVote.BLOCK,
            ArbitrationDecision.EMERGENCY_LOCKDOWN: ConsensusVote.EMERGENCY_HALT,
        }[data.strategic_arbitration.decision]
        participants.append(ConsensusParticipant("strategic_arbitration", "arbitration", vote, data.strategic_arbitration.confidence_score, 10, vote in SAFETY_VOTES, (data.strategic_arbitration.final_message,), tuple(conflict.conflict_type.value for conflict in data.strategic_arbitration.conflicts)))
    if data.intent_alignment is not None:
        vote = ConsensusVote.APPROVE if data.intent_alignment.mode in {IntentAlignmentMode.FULLY_ALIGNED, IntentAlignmentMode.STABLE_ALIGNMENT} else ConsensusVote.SAFE_MODE if data.intent_alignment.mode == IntentAlignmentMode.CRITICAL_REALIGNMENT else ConsensusVote.REDUCE_AUTONOMY
        participants.append(ConsensusParticipant("intent_alignment", "mission", vote, data.intent_alignment.alignment_confidence, 9, IntentRisk.SAFETY_BOUNDARY_DRIFT in data.intent_alignment.risks or vote in SAFETY_VOTES, (data.intent_alignment.summary,), tuple(risk.value for risk in data.intent_alignment.risks)))
    if data.meta_cognition is not None:
        vote = ConsensusVote.APPROVE if data.meta_cognition.mode in {MetaCognitionMode.SELF_AWARE, MetaCognitionMode.REFLECTIVE} else ConsensusVote.REQUIRE_SUPERVISION if data.meta_cognition.mode in {MetaCognitionMode.UNCERTAIN, MetaCognitionMode.RIGID} else ConsensusVote.SAFE_MODE
        participants.append(ConsensusParticipant("meta_cognition", "reasoning", vote, data.meta_cognition.confidence_score, 7, MetaCognitiveRisk.COGNITIVE_COLLAPSE in data.meta_cognition.risks, (data.meta_cognition.summary,), tuple(risk.value for risk in data.meta_cognition.risks)))
    if data.operational_awareness is not None:
        vote = ConsensusVote.APPROVE if data.operational_awareness.health_status == OperationalHealthStatus.HEALTHY else ConsensusVote.REQUIRE_SUPERVISION if data.operational_awareness.health_status in {OperationalHealthStatus.WARNING, OperationalHealthStatus.DEGRADED} else ConsensusVote.SAFE_MODE
        if data.operational_awareness.health_status == OperationalHealthStatus.COLLAPSING:
            vote = ConsensusVote.EMERGENCY_HALT
        participants.append(ConsensusParticipant("operational_awareness", "operations", vote, data.operational_awareness.operational_confidence_score, 8, vote in SAFETY_VOTES, (data.operational_awareness.summary,), tuple(risk.value for risk in data.operational_awareness.risks)))
    if data.mission_continuity is not None:
        vote = ConsensusVote.APPROVE if data.mission_continuity.mode == MissionContinuityMode.FULL_OPERATION else ConsensusVote.SAFE_MODE if data.mission_continuity.mode in {MissionContinuityMode.SURVIVAL_CONTINUITY, MissionContinuityMode.SAFE_PAUSE} else ConsensusVote.REDUCE_AUTONOMY
        participants.append(ConsensusParticipant("mission_continuity", "continuity", vote, data.mission_continuity.continuity_score, 8, vote in SAFETY_VOTES, (data.mission_continuity.summary,), tuple(risk.value for risk in data.mission_continuity.risks)))
    if data.recovery_resilience is not None:
        vote = ConsensusVote.APPROVE if data.recovery_resilience.mode == RecoveryMode.NORMAL else ConsensusVote.EMERGENCY_HALT if data.recovery_resilience.mode == RecoveryMode.SURVIVAL_MODE else ConsensusVote.SAFE_MODE
        participants.append(ConsensusParticipant("recovery_resilience", "survival", vote, data.recovery_resilience.resilience_score, 9, vote in SAFETY_VOTES or RecoveryRisk.SYSTEM_COMPROMISED in data.recovery_resilience.risks, (data.recovery_resilience.summary,), tuple(risk.value for risk in data.recovery_resilience.risks)))
    if data.system_integrity is not None:
        vote = ConsensusVote.APPROVE if data.system_integrity.status == SystemIntegrityStatus.HEALTHY else ConsensusVote.REQUIRE_SUPERVISION if data.system_integrity.status == SystemIntegrityStatus.DEGRADED else ConsensusVote.SAFE_MODE
        if data.system_integrity.status in {SystemIntegrityStatus.COMPROMISED, SystemIntegrityStatus.ROLLBACK_RECOMMENDED}:
            vote = ConsensusVote.EMERGENCY_HALT
        participants.append(ConsensusParticipant("system_integrity", "integrity", vote, data.system_integrity.integrity_score, 10, vote in SAFETY_VOTES, (data.system_integrity.summary,), tuple(risk.value for risk in data.system_integrity.risks)))
    if data.learning_governance is not None:
        vote = ConsensusVote.APPROVE if data.learning_governance.decision == LearningGovernanceDecision.ALLOW_LEARNING else ConsensusVote.REDUCE_AUTONOMY if data.learning_governance.decision == LearningGovernanceDecision.ALLOW_LIMITED_LEARNING else ConsensusVote.REQUIRE_SUPERVISION
        if data.learning_governance.mode == LearningGovernanceMode.SAFETY_LOCKDOWN:
            vote = ConsensusVote.SAFE_MODE
        participants.append(ConsensusParticipant("learning_governance", "learning", vote, 75, 5, vote == ConsensusVote.SAFE_MODE, (data.learning_governance.safety_summary,), tuple(risk.value for risk in data.learning_governance.risks)))
    if data.self_evaluation is not None:
        vote = ConsensusVote.APPROVE if data.self_evaluation.autonomy_recommendation == SystemAutonomyRecommendation.MAINTAIN_AUTONOMY and data.self_evaluation.status == SelfEvaluationStatus.STABLE else ConsensusVote.REDUCE_AUTONOMY if data.self_evaluation.autonomy_recommendation == SystemAutonomyRecommendation.REDUCE_AUTONOMY else ConsensusVote.REQUIRE_SUPERVISION
        participants.append(ConsensusParticipant("self_evaluation", "autonomy", vote, data.self_evaluation.confidence_score, 6, data.self_evaluation.status == SelfEvaluationStatus.CONTRADICTORY, (data.self_evaluation.summary,), data.self_evaluation.contradictions))
    if data.supervisor_result is not None:
        vote = ConsensusVote.APPROVE if data.supervisor_result.final_executable and data.supervisor_result.decision == SupervisorDecision.APPROVE_SYSTEM_DECISION else ConsensusVote.REQUIRE_SUPERVISION
        if data.supervisor_result.decision in {SupervisorDecision.OVERRIDE_TO_BLOCK, SupervisorDecision.OVERRIDE_TO_STOP_SESSION}:
            vote = ConsensusVote.BLOCK
        if data.supervisor_result.decision == SupervisorDecision.EMERGENCY_HALT:
            vote = ConsensusVote.EMERGENCY_HALT
        participants.append(ConsensusParticipant("supervisor", "supervision", vote, 85, 10, vote in SAFETY_VOTES, (data.supervisor_result.recommendation,), data.supervisor_result.critical_risks))
    if data.agent_coordination is not None:
        vote = {
            AgentVote.APPROVE: ConsensusVote.APPROVE,
            AgentVote.APPROVE_REDUCED_RISK: ConsensusVote.REDUCE_AUTONOMY,
            AgentVote.REQUIRE_REVIEW: ConsensusVote.REQUIRE_SUPERVISION,
            AgentVote.BLOCK: ConsensusVote.BLOCK,
            AgentVote.STOP_SESSION: ConsensusVote.EMERGENCY_HALT,
            AgentVote.NO_OPINION: ConsensusVote.ABSTAIN,
        }[data.agent_coordination.final_vote]
        participants.append(ConsensusParticipant("agent_coordination", "agents", vote, data.agent_coordination.consensus_score, 7, data.agent_coordination.consensus_status in {AgentConsensusStatus.CONSENSUS_BLOCK, AgentConsensusStatus.CONSENSUS_STOP_SESSION}, (data.agent_coordination.recommendation,), data.agent_coordination.risks_detected))
    return tuple(participants)


def _decision(totals: dict[ConsensusVote, int], risks: tuple[ConsensusRisk, ...], safety_override: bool, confidence: CollectiveConfidence) -> ConsensusDecision:
    if ConsensusRisk.EMERGENCY_ALIGNMENT_REQUIRED in risks or totals[ConsensusVote.EMERGENCY_HALT] > 0:
        return ConsensusDecision.EMERGENCY_HALT
    if ConsensusRisk.CONSENSUS_COLLAPSE_RISK in risks and confidence.weighted_confidence_score < 35:
        return ConsensusDecision.NO_CONSENSUS
    if safety_override or totals[ConsensusVote.SAFE_MODE] >= max(totals[ConsensusVote.APPROVE], totals[ConsensusVote.REDUCE_AUTONOMY]):
        return ConsensusDecision.ENTER_SAFE_MODE
    if totals[ConsensusVote.BLOCK] > 0:
        return ConsensusDecision.BLOCK_COLLECTIVE_ACTION
    if ConsensusRisk.AUTHORITY_CONFLICT in risks:
        return ConsensusDecision.REQUIRE_SUPERVISION
    if totals[ConsensusVote.REQUIRE_SUPERVISION] > totals[ConsensusVote.APPROVE]:
        return ConsensusDecision.REQUIRE_SUPERVISION
    if totals[ConsensusVote.REDUCE_AUTONOMY] > 0 or ConsensusRisk.CONSENSUS_FRAGMENTATION in risks:
        return ConsensusDecision.APPROVE_WITH_REDUCED_AUTONOMY
    if totals[ConsensusVote.APPROVE] > 0:
        return ConsensusDecision.APPROVE_COLLECTIVE_DECISION
    return ConsensusDecision.NO_CONSENSUS


def _mode(decision: ConsensusDecision, risks: tuple[ConsensusRisk, ...], safety_override: bool, confidence: CollectiveConfidence) -> ConsensusMode:
    if decision == ConsensusDecision.EMERGENCY_HALT or ConsensusRisk.EMERGENCY_ALIGNMENT_REQUIRED in risks:
        return ConsensusMode.EMERGENCY_CONSENSUS
    if decision == ConsensusDecision.NO_CONSENSUS or ConsensusRisk.CONSENSUS_COLLAPSE_RISK in risks:
        return ConsensusMode.CONSENSUS_COLLAPSE
    if safety_override or decision == ConsensusDecision.ENTER_SAFE_MODE:
        return ConsensusMode.SAFETY_FIRST
    if decision == ConsensusDecision.REQUIRE_SUPERVISION or ConsensusRisk.AUTHORITY_CONFLICT in risks:
        return ConsensusMode.SUPERVISED_CONSENSUS
    if confidence.agreement_score < 60 or risks:
        return ConsensusMode.DEGRADED_CONSENSUS
    if confidence.authority_stability_score < 75:
        return ConsensusMode.WEIGHTED_AUTHORITY
    return ConsensusMode.NORMAL_CONSENSUS


def _state(decision: ConsensusDecision, risks: tuple[ConsensusRisk, ...], disagreements: tuple[str, ...]) -> ConsensusState:
    if decision == ConsensusDecision.EMERGENCY_HALT:
        return ConsensusState.EMERGENCY
    if decision == ConsensusDecision.NO_CONSENSUS:
        return ConsensusState.COLLAPSED
    if ConsensusRisk.MINORITY_SAFETY_OVERRIDE in risks:
        return ConsensusState.SAFETY_OVERRIDE
    if ConsensusRisk.CONSENSUS_FRAGMENTATION in risks:
        return ConsensusState.FRAGMENTED
    if disagreements:
        return ConsensusState.DISAGREEMENT
    return ConsensusState.STABLE


def _recommendations(decision: ConsensusDecision, risks: tuple[ConsensusRisk, ...]) -> tuple[ConsensusRecommendation, ...]:
    recommendations: list[ConsensusRecommendation] = []
    if decision == ConsensusDecision.EMERGENCY_HALT:
        recommendations.append(ConsensusRecommendation.HALT_SYSTEM)
        recommendations.append(ConsensusRecommendation.ACTIVATE_EMERGENCY_CONSENSUS)
    if decision == ConsensusDecision.ENTER_SAFE_MODE or ConsensusRisk.MINORITY_SAFETY_OVERRIDE in risks:
        recommendations.append(ConsensusRecommendation.ENTER_SAFE_MODE)
        recommendations.append(ConsensusRecommendation.PRIORITIZE_SAFETY_VOTES)
    if ConsensusRisk.DOMINANT_UNSAFE_PARTICIPANT in risks:
        recommendations.append(ConsensusRecommendation.IGNORE_UNSAFE_DOMINANT_SIGNAL)
    if ConsensusRisk.CONSENSUS_FRAGMENTATION in risks or ConsensusRisk.DISAGREEMENT_ESCALATION in risks:
        recommendations.append(ConsensusRecommendation.STABILIZE_CONSENSUS)
        recommendations.append(ConsensusRecommendation.REDUCE_AUTONOMY)
    if ConsensusRisk.AUTHORITY_CONFLICT in risks or decision == ConsensusDecision.REQUIRE_SUPERVISION:
        recommendations.append(ConsensusRecommendation.REQUIRE_HUMAN_SUPERVISION)
    if ConsensusRisk.LOW_COLLECTIVE_CONFIDENCE in risks or ConsensusRisk.COLLECTIVE_REASONING_DRIFT in risks:
        recommendations.append(ConsensusRecommendation.RECALIBRATE_PARTICIPANT_WEIGHTS)
    if not recommendations:
        recommendations.append(ConsensusRecommendation.CONTINUE_COLLECTIVE_OPERATION)
    return tuple(dict.fromkeys(recommendations))


def _global_confidence(confidence: CollectiveConfidence, risks: tuple[ConsensusRisk, ...], disagreements: tuple[str, ...], safety_override: bool) -> int:
    score = int(round(sum((
        confidence.weighted_confidence_score,
        confidence.agreement_score,
        confidence.safety_alignment_score,
        confidence.authority_stability_score,
        confidence.reasoning_coherence_score,
        confidence.autonomy_safety_score,
    )) / 6))
    score -= min(35, len(risks) * 4)
    score -= min(20, len(disagreements) * 5)
    if safety_override:
        score -= 5
    return _clamp(score)


def _dominant_participant(participants: tuple[ConsensusParticipant, ...]) -> str | None:
    if not participants:
        return None
    return max(participants, key=lambda participant: participant.weight * participant.confidence).name


def _vote_family(vote: ConsensusVote) -> str:
    if vote == ConsensusVote.APPROVE:
        return "approve"
    if vote == ConsensusVote.REDUCE_AUTONOMY:
        return "review"
    if vote == ConsensusVote.REQUIRE_SUPERVISION:
        return "review"
    if vote == ConsensusVote.BLOCK:
        return "block"
    if vote == ConsensusVote.SAFE_MODE:
        return "safe"
    if vote == ConsensusVote.EMERGENCY_HALT:
        return "halt"
    return "abstain"


def _vote_family_count(votes: list[ConsensusVote], family: str) -> int:
    return sum(1 for vote in votes if _vote_family(vote) == family)


def _authority_conflict(participants: tuple[ConsensusParticipant, ...]) -> bool:
    return bool(resolve_authority_conflicts(participants=participants))


def _dominant_unsafe(participants: tuple[ConsensusParticipant, ...], totals: dict[ConsensusVote, int]) -> bool:
    dominant_name = _dominant_participant(participants)
    if dominant_name is None:
        return False
    dominant = next(participant for participant in participants if participant.name == dominant_name)
    safety_weight = totals[ConsensusVote.BLOCK] + totals[ConsensusVote.SAFE_MODE] + totals[ConsensusVote.EMERGENCY_HALT]
    return dominant.vote == ConsensusVote.APPROVE and safety_weight > 0 and dominant.weight >= 8


def _reasoning_drift(data: ConsensusInput) -> bool:
    return (
        (data.meta_cognition is not None and data.meta_cognition.mode in {MetaCognitionMode.CONTRADICTORY, MetaCognitionMode.DEGRADED_REASONING, MetaCognitionMode.RECALIBRATION_REQUIRED})
        or (data.self_evaluation is not None and data.self_evaluation.status in {SelfEvaluationStatus.CONTRADICTORY, SelfEvaluationStatus.UNSTABLE})
        or (data.intent_alignment is not None and data.intent_alignment.mode in {IntentAlignmentMode.MISALIGNED, IntentAlignmentMode.CRITICAL_REALIGNMENT})
    )


def _emergency_required(data: ConsensusInput, participants: tuple[ConsensusParticipant, ...]) -> bool:
    emergency_votes = sum(1 for participant in participants if participant.vote == ConsensusVote.EMERGENCY_HALT)
    critical_layers = 0
    if data.strategic_arbitration is not None and (data.strategic_arbitration.emergency_lockdown or data.strategic_arbitration.mode == ArbitrationMode.EMERGENCY_LOCKDOWN or data.strategic_arbitration.severity == ArbitrationSeverity.CRITICAL):
        critical_layers += 1
    if data.system_integrity is not None and data.system_integrity.status in {SystemIntegrityStatus.COMPROMISED, SystemIntegrityStatus.ROLLBACK_RECOMMENDED}:
        critical_layers += 1
    if data.operational_awareness is not None and data.operational_awareness.mode == OperationalAwarenessMode.CRITICAL:
        critical_layers += 1
    if data.recovery_resilience is not None and data.recovery_resilience.mode == RecoveryMode.SURVIVAL_MODE:
        critical_layers += 1
    if data.intent_alignment is not None and data.intent_alignment.mode == IntentAlignmentMode.CRITICAL_REALIGNMENT:
        critical_layers += 1
    return emergency_votes >= 2 or critical_layers >= 3


def _unsafe_autonomy(data: ConsensusInput) -> bool:
    return (
        data.self_evaluation is not None
        and data.self_evaluation.autonomy_recommendation == SystemAutonomyRecommendation.MAINTAIN_AUTONOMY
        and (
            (data.system_integrity is not None and data.system_integrity.status != SystemIntegrityStatus.HEALTHY)
            or (data.intent_alignment is not None and IntentRisk.AUTONOMY_EXPANSION in data.intent_alignment.risks)
        )
    )


def _safety_overrides(participants: tuple[ConsensusParticipant, ...]) -> tuple[str, ...]:
    return tuple(participant.name for participant in participants if participant.safety_critical and participant.vote in SAFETY_VOTES)


def _final_message(decision: ConsensusDecision, confidence: int, risks: tuple[ConsensusRisk, ...]) -> str:
    return f"Collective decision {decision.value} with confidence {confidence}/100 and {len(risks)} consensus risk(s)."


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _input(consensus_input: ConsensusInput | None = None, **kwargs: Any) -> ConsensusInput:
    if consensus_input is not None:
        return consensus_input
    return ConsensusInput(**kwargs)


def _clamp(value: int | float) -> int:
    return max(0, min(100, int(round(value))))


__all__ = [
    "aggregate_consensus_votes",
    "apply_minority_safety_override",
    "build_consensus_graph",
    "compute_collective_confidence",
    "detect_consensus_risks",
    "evaluate_collective_consensus",
    "render_collective_consensus_markdown",
    "resolve_authority_conflicts",
]
