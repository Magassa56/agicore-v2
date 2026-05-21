"""Models for the offline Autonomous Consensus & Collective Intelligence Engine."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .hierarchical_supervisor_models import SupervisorResult
from .intent_alignment_models import IntentAlignmentResult
from .learning_governance_models import LearningGovernanceResult
from .meta_cognition_models import MetaCognitionResult
from .mission_continuity_models import MissionContinuityResult
from .multi_agent_models import AgentCoordinationResult
from .operational_awareness_models import OperationalAwarenessResult
from .recovery_resilience_models import RecoveryResilienceResult
from .recursive_self_evaluation_models import SelfEvaluationResult
from .strategic_arbitration_models import ArbitrationResult
from .system_integrity_models import SystemIntegrityResult


class ConsensusState(StrEnum):
    """Coarse state of the collective consensus layer."""

    STABLE = "STABLE"
    DISAGREEMENT = "DISAGREEMENT"
    FRAGMENTED = "FRAGMENTED"
    SAFETY_OVERRIDE = "SAFETY_OVERRIDE"
    EMERGENCY = "EMERGENCY"
    COLLAPSED = "COLLAPSED"


class ConsensusMode(StrEnum):
    """Consensus operating mode."""

    NORMAL_CONSENSUS = "NORMAL_CONSENSUS"
    WEIGHTED_AUTHORITY = "WEIGHTED_AUTHORITY"
    SAFETY_FIRST = "SAFETY_FIRST"
    EMERGENCY_CONSENSUS = "EMERGENCY_CONSENSUS"
    SUPERVISED_CONSENSUS = "SUPERVISED_CONSENSUS"
    DEGRADED_CONSENSUS = "DEGRADED_CONSENSUS"
    CONSENSUS_COLLAPSE = "CONSENSUS_COLLAPSE"


class ConsensusDecision(StrEnum):
    """Final collective decision."""

    APPROVE_COLLECTIVE_DECISION = "APPROVE_COLLECTIVE_DECISION"
    APPROVE_WITH_REDUCED_AUTONOMY = "APPROVE_WITH_REDUCED_AUTONOMY"
    REQUIRE_SUPERVISION = "REQUIRE_SUPERVISION"
    BLOCK_COLLECTIVE_ACTION = "BLOCK_COLLECTIVE_ACTION"
    ENTER_SAFE_MODE = "ENTER_SAFE_MODE"
    EMERGENCY_HALT = "EMERGENCY_HALT"
    NO_CONSENSUS = "NO_CONSENSUS"


class ConsensusVote(StrEnum):
    """Vote emitted by a participant."""

    APPROVE = "APPROVE"
    REDUCE_AUTONOMY = "REDUCE_AUTONOMY"
    REQUIRE_SUPERVISION = "REQUIRE_SUPERVISION"
    BLOCK = "BLOCK"
    SAFE_MODE = "SAFE_MODE"
    EMERGENCY_HALT = "EMERGENCY_HALT"
    ABSTAIN = "ABSTAIN"


class ConsensusRisk(StrEnum):
    """Risks detected during collective consensus."""

    CONSENSUS_FRAGMENTATION = "CONSENSUS_FRAGMENTATION"
    LOW_COLLECTIVE_CONFIDENCE = "LOW_COLLECTIVE_CONFIDENCE"
    AUTHORITY_CONFLICT = "AUTHORITY_CONFLICT"
    MINORITY_SAFETY_OVERRIDE = "MINORITY_SAFETY_OVERRIDE"
    DOMINANT_UNSAFE_PARTICIPANT = "DOMINANT_UNSAFE_PARTICIPANT"
    DISAGREEMENT_ESCALATION = "DISAGREEMENT_ESCALATION"
    COLLECTIVE_REASONING_DRIFT = "COLLECTIVE_REASONING_DRIFT"
    CONSENSUS_COLLAPSE_RISK = "CONSENSUS_COLLAPSE_RISK"
    EMERGENCY_ALIGNMENT_REQUIRED = "EMERGENCY_ALIGNMENT_REQUIRED"


class ConsensusRecommendation(StrEnum):
    """Recommended controls after consensus evaluation."""

    STABILIZE_CONSENSUS = "STABILIZE_CONSENSUS"
    REDUCE_AUTONOMY = "REDUCE_AUTONOMY"
    REQUIRE_HUMAN_SUPERVISION = "REQUIRE_HUMAN_SUPERVISION"
    PRIORITIZE_SAFETY_VOTES = "PRIORITIZE_SAFETY_VOTES"
    ACTIVATE_EMERGENCY_CONSENSUS = "ACTIVATE_EMERGENCY_CONSENSUS"
    IGNORE_UNSAFE_DOMINANT_SIGNAL = "IGNORE_UNSAFE_DOMINANT_SIGNAL"
    CONTINUE_COLLECTIVE_OPERATION = "CONTINUE_COLLECTIVE_OPERATION"
    ENTER_SAFE_MODE = "ENTER_SAFE_MODE"
    HALT_SYSTEM = "HALT_SYSTEM"
    RECALIBRATE_PARTICIPANT_WEIGHTS = "RECALIBRATE_PARTICIPANT_WEIGHTS"


@dataclass(frozen=True)
class ConsensusParticipant:
    """One subsystem participating in collective consensus."""

    name: str
    authority: str
    vote: ConsensusVote
    confidence: int
    weight: int
    safety_critical: bool
    reasons: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConsensusGraph:
    """Weighted participant graph for explainable aggregation."""

    participants: tuple[ConsensusParticipant, ...]
    edges: tuple[tuple[str, str, str], ...]
    dominant_participant: str | None
    safety_participants: tuple[str, ...]
    disagreement_pairs: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class CollectiveConfidence:
    """Collective confidence component scores normalized to 0..100."""

    weighted_confidence_score: int
    agreement_score: int
    safety_alignment_score: int
    authority_stability_score: int
    reasoning_coherence_score: int
    autonomy_safety_score: int


@dataclass(frozen=True)
class ConsensusInput:
    """Inputs consumed by the offline collective consensus engine."""

    strategic_arbitration: ArbitrationResult | None = None
    intent_alignment: IntentAlignmentResult | None = None
    meta_cognition: MetaCognitionResult | None = None
    operational_awareness: OperationalAwarenessResult | None = None
    mission_continuity: MissionContinuityResult | None = None
    recovery_resilience: RecoveryResilienceResult | None = None
    system_integrity: SystemIntegrityResult | None = None
    learning_governance: LearningGovernanceResult | None = None
    self_evaluation: SelfEvaluationResult | None = None
    supervisor_result: SupervisorResult | None = None
    agent_coordination: AgentCoordinationResult | None = None


@dataclass(frozen=True)
class ConsensusEvent:
    """Auditable consensus event."""

    mode: ConsensusMode
    decision: ConsensusDecision
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class ConsensusResult:
    """Final collective consensus result."""

    mode: ConsensusMode
    state: ConsensusState
    decision: ConsensusDecision
    collective_confidence_score: int
    confidence_breakdown: CollectiveConfidence
    participants: tuple[ConsensusParticipant, ...]
    graph: ConsensusGraph
    vote_totals: dict[ConsensusVote, int]
    disagreements: tuple[str, ...]
    safety_overrides: tuple[str, ...]
    risks: tuple[ConsensusRisk, ...]
    recommendations: tuple[ConsensusRecommendation, ...]
    final_message: str
    events: tuple[ConsensusEvent, ...]


__all__ = [
    "CollectiveConfidence",
    "ConsensusDecision",
    "ConsensusEvent",
    "ConsensusGraph",
    "ConsensusInput",
    "ConsensusMode",
    "ConsensusParticipant",
    "ConsensusRecommendation",
    "ConsensusResult",
    "ConsensusRisk",
    "ConsensusState",
    "ConsensusVote",
]
