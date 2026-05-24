"""Models for the offline Autonomous Cognitive Alignment Engine."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .cognitive_continuity_models import CognitiveContinuityResult
from .cognitive_governance_models import CognitiveGovernanceResult
from .cognitive_identity_models import CognitiveIdentityResult
from .cognitive_policy_models import CognitivePolicyResult
from .cognitive_recovery_models import CognitiveRecoveryResult
from .cognitive_resilience_models import CognitiveResilienceResult
from .cognitive_stability_models import CognitiveStabilityResult
from .collective_consensus_models import ConsensusResult
from .global_orchestrator_models import GlobalOrchestratorResult
from .intent_alignment_models import IntentAlignmentResult
from .intent_integrity_models import IntentIntegrityResult
from .mission_continuity_models import MissionContinuityResult
from .recursive_world_model_models import RecursiveWorldModelResult
from .self_reflection_audit_models import SelfReflectionAuditResult
from .system_integrity_models import SystemIntegrityResult


class CognitiveAlignmentState(StrEnum):
    """Current cognitive alignment state."""

    FULLY_ALIGNED = "FULLY_ALIGNED"
    ALIGNED_WATCH = "ALIGNED_WATCH"
    PARTIAL_MISALIGNMENT = "PARTIAL_MISALIGNMENT"
    STRATEGIC_MISALIGNMENT = "STRATEGIC_MISALIGNMENT"
    POLICY_MISALIGNMENT = "POLICY_MISALIGNMENT"
    INTENT_MISALIGNMENT = "INTENT_MISALIGNMENT"
    SYSTEMIC_MISALIGNMENT = "SYSTEMIC_MISALIGNMENT"
    ALIGNMENT_LOCKED = "ALIGNMENT_LOCKED"


class CognitiveAlignmentMode(StrEnum):
    """Operating mode for global cognitive alignment."""

    NORMAL_ALIGNMENT = "NORMAL_ALIGNMENT"
    ALIGNMENT_MONITORING = "ALIGNMENT_MONITORING"
    MISSION_ALIGNMENT = "MISSION_ALIGNMENT"
    IDENTITY_ALIGNMENT = "IDENTITY_ALIGNMENT"
    INTENT_ALIGNMENT_REPAIR = "INTENT_ALIGNMENT_REPAIR"
    POLICY_ALIGNMENT_REPAIR = "POLICY_ALIGNMENT_REPAIR"
    SYSTEMIC_ALIGNMENT_REPAIR = "SYSTEMIC_ALIGNMENT_REPAIR"
    SAFE_ALIGNMENT_MODE = "SAFE_ALIGNMENT_MODE"
    LOCKED_ALIGNMENT_MODE = "LOCKED_ALIGNMENT_MODE"


class CognitiveAlignmentRisk(StrEnum):
    """Risks that can break global cognitive alignment."""

    MISSION_ALIGNMENT_BREAK = "MISSION_ALIGNMENT_BREAK"
    IDENTITY_ALIGNMENT_BREAK = "IDENTITY_ALIGNMENT_BREAK"
    INTENT_ALIGNMENT_BREAK = "INTENT_ALIGNMENT_BREAK"
    POLICY_ALIGNMENT_BREAK = "POLICY_ALIGNMENT_BREAK"
    GOVERNANCE_ALIGNMENT_BREAK = "GOVERNANCE_ALIGNMENT_BREAK"
    WORLD_MODEL_ALIGNMENT_BREAK = "WORLD_MODEL_ALIGNMENT_BREAK"
    CONSENSUS_ALIGNMENT_BREAK = "CONSENSUS_ALIGNMENT_BREAK"
    DECISION_ACTION_MISALIGNMENT = "DECISION_ACTION_MISALIGNMENT"
    AUTONOMY_ALIGNMENT_RISK = "AUTONOMY_ALIGNMENT_RISK"
    SYSTEMIC_ALIGNMENT_COLLAPSE = "SYSTEMIC_ALIGNMENT_COLLAPSE"


class CognitiveAlignmentAction(StrEnum):
    """Actions available to restore cognitive alignment."""

    PRESERVE_ALIGNMENT_STATE = "PRESERVE_ALIGNMENT_STATE"
    REALIGN_MISSION = "REALIGN_MISSION"
    REALIGN_IDENTITY = "REALIGN_IDENTITY"
    REALIGN_INTENT = "REALIGN_INTENT"
    REALIGN_POLICY = "REALIGN_POLICY"
    REALIGN_GOVERNANCE = "REALIGN_GOVERNANCE"
    REALIGN_WORLD_MODEL = "REALIGN_WORLD_MODEL"
    REBUILD_CONSENSUS_ALIGNMENT = "REBUILD_CONSENSUS_ALIGNMENT"
    REDUCE_AUTONOMY = "REDUCE_AUTONOMY"
    LOCK_ALIGNMENT_STATE = "LOCK_ALIGNMENT_STATE"


class CognitiveAlignmentRecommendation(StrEnum):
    """Recommended global alignment controls."""

    CONTINUE_ALIGNMENT_MONITORING = "CONTINUE_ALIGNMENT_MONITORING"
    VERIFY_MISSION_ALIGNMENT = "VERIFY_MISSION_ALIGNMENT"
    REPAIR_IDENTITY_ALIGNMENT = "REPAIR_IDENTITY_ALIGNMENT"
    REPAIR_INTENT_ALIGNMENT = "REPAIR_INTENT_ALIGNMENT"
    REPAIR_POLICY_ALIGNMENT = "REPAIR_POLICY_ALIGNMENT"
    RECHECK_GOVERNANCE_ALIGNMENT = "RECHECK_GOVERNANCE_ALIGNMENT"
    REBUILD_CONSENSUS_CONTEXT = "REBUILD_CONSENSUS_CONTEXT"
    KEEP_AUTONOMY_REDUCED = "KEEP_AUTONOMY_REDUCED"
    REQUIRE_SUPERVISION = "REQUIRE_SUPERVISION"
    UPDATE_ALIGNMENT_SNAPSHOT = "UPDATE_ALIGNMENT_SNAPSHOT"


@dataclass(frozen=True)
class AlignmentAxis:
    """One evaluated alignment axis."""

    name: str
    score: int
    aligned: bool
    risk: CognitiveAlignmentRisk | None
    evidence: str


@dataclass(frozen=True)
class AlignmentMatrix:
    """Global alignment matrix across mission, identity, intent and controls."""

    axes: tuple[AlignmentAxis, ...]
    global_score: int
    weakest_axis: str | None
    broken_axes: tuple[str, ...]
    autonomy_reduced: bool
    locked: bool


@dataclass(frozen=True)
class CognitiveAlignmentScore:
    """Alignment component scores normalized to 0..100."""

    mission_alignment_score: int
    identity_alignment_score: int
    intent_alignment_score: int
    policy_alignment_score: int
    governance_alignment_score: int
    world_model_alignment_score: int
    consensus_alignment_score: int
    decision_action_alignment_score: int
    autonomy_alignment_score: int
    systemic_alignment_score: int


@dataclass(frozen=True)
class CognitiveAlignmentInput:
    """Inputs consumed by the offline cognitive alignment engine."""

    intent_integrity: IntentIntegrityResult | None = None
    cognitive_identity: CognitiveIdentityResult | None = None
    cognitive_continuity: CognitiveContinuityResult | None = None
    cognitive_recovery: CognitiveRecoveryResult | None = None
    cognitive_resilience: CognitiveResilienceResult | None = None
    cognitive_stability: CognitiveStabilityResult | None = None
    cognitive_policy: CognitivePolicyResult | None = None
    cognitive_governance: CognitiveGovernanceResult | None = None
    self_reflection_audit: SelfReflectionAuditResult | None = None
    recursive_world_model: RecursiveWorldModelResult | None = None
    global_orchestrator: GlobalOrchestratorResult | None = None
    collective_consensus: ConsensusResult | None = None
    intent_alignment: IntentAlignmentResult | None = None
    mission_continuity: MissionContinuityResult | None = None
    system_integrity: SystemIntegrityResult | None = None


@dataclass(frozen=True)
class CognitiveAlignmentEvent:
    """Auditable cognitive alignment event."""

    state: CognitiveAlignmentState
    mode: CognitiveAlignmentMode
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class CognitiveAlignmentResult:
    """Final autonomous cognitive alignment result."""

    state: CognitiveAlignmentState
    mode: CognitiveAlignmentMode
    cognitive_alignment_score: int
    score_breakdown: CognitiveAlignmentScore
    axes: tuple[AlignmentAxis, ...]
    matrix: AlignmentMatrix
    risks: tuple[CognitiveAlignmentRisk, ...]
    actions: tuple[CognitiveAlignmentAction, ...]
    recommendations: tuple[CognitiveAlignmentRecommendation, ...]
    events: tuple[CognitiveAlignmentEvent, ...]
    summary: str


__all__ = [
    "AlignmentAxis",
    "AlignmentMatrix",
    "CognitiveAlignmentAction",
    "CognitiveAlignmentEvent",
    "CognitiveAlignmentInput",
    "CognitiveAlignmentMode",
    "CognitiveAlignmentRecommendation",
    "CognitiveAlignmentResult",
    "CognitiveAlignmentRisk",
    "CognitiveAlignmentScore",
    "CognitiveAlignmentState",
]
