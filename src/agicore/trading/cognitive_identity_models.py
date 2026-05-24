"""Models for the offline Autonomous Cognitive Identity Engine."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .cognitive_continuity_models import CognitiveContinuityResult
from .cognitive_governance_models import CognitiveGovernanceResult
from .cognitive_policy_models import CognitivePolicyResult
from .cognitive_recovery_models import CognitiveRecoveryResult
from .cognitive_resilience_models import CognitiveResilienceResult
from .cognitive_stability_models import CognitiveStabilityResult
from .collective_consensus_models import ConsensusResult
from .global_orchestrator_models import GlobalOrchestratorResult
from .intent_alignment_models import IntentAlignmentResult
from .mission_continuity_models import MissionContinuityResult
from .recursive_world_model_models import RecursiveWorldModelResult
from .self_reflection_audit_models import SelfReflectionAuditResult
from .strategic_memory_models import StrategicTimelineAnalysis
from .strategy_dna_models import StrategyDNA
from .system_integrity_models import SystemIntegrityResult


class CognitiveIdentityState(StrEnum):
    """Current cognitive identity state."""

    IDENTITY_STABLE = "IDENTITY_STABLE"
    IDENTITY_WATCH = "IDENTITY_WATCH"
    IDENTITY_DRIFT = "IDENTITY_DRIFT"
    IDENTITY_FRAGMENTED = "IDENTITY_FRAGMENTED"
    IDENTITY_CONFLICTED = "IDENTITY_CONFLICTED"
    IDENTITY_AT_RISK = "IDENTITY_AT_RISK"
    IDENTITY_RESTORING = "IDENTITY_RESTORING"
    IDENTITY_LOCKED = "IDENTITY_LOCKED"


class CognitiveIdentityMode(StrEnum):
    """Operating mode for cognitive identity preservation."""

    NORMAL_IDENTITY = "NORMAL_IDENTITY"
    IDENTITY_MONITORING = "IDENTITY_MONITORING"
    INVARIANT_PROTECTION = "INVARIANT_PROTECTION"
    MISSION_ALIGNMENT = "MISSION_ALIGNMENT"
    PRIORITY_RESTORATION = "PRIORITY_RESTORATION"
    IDENTITY_REPAIR = "IDENTITY_REPAIR"
    SAFE_IDENTITY_MODE = "SAFE_IDENTITY_MODE"
    LOCKED_IDENTITY_MODE = "LOCKED_IDENTITY_MODE"


class CognitiveIdentityRisk(StrEnum):
    """Risks that can degrade AGIcore cognitive identity."""

    STRATEGIC_IDENTITY_DRIFT = "STRATEGIC_IDENTITY_DRIFT"
    MISSION_IDENTITY_MISMATCH = "MISSION_IDENTITY_MISMATCH"
    PRIORITY_INVARIANT_BREAK = "PRIORITY_INVARIANT_BREAK"
    GOVERNANCE_IDENTITY_CONFLICT = "GOVERNANCE_IDENTITY_CONFLICT"
    POLICY_IDENTITY_CONFLICT = "POLICY_IDENTITY_CONFLICT"
    WORLD_MODEL_IDENTITY_DRIFT = "WORLD_MODEL_IDENTITY_DRIFT"
    CONSENSUS_IDENTITY_FRAGMENTATION = "CONSENSUS_IDENTITY_FRAGMENTATION"
    RECOVERY_IDENTITY_DISCONTINUITY = "RECOVERY_IDENTITY_DISCONTINUITY"
    AUTONOMY_IDENTITY_EXPANSION = "AUTONOMY_IDENTITY_EXPANSION"
    IDENTITY_COLLAPSE_RISK = "IDENTITY_COLLAPSE_RISK"


class CognitiveIdentityAction(StrEnum):
    """Actions available to preserve cognitive identity."""

    PRESERVE_IDENTITY_PROFILE = "PRESERVE_IDENTITY_PROFILE"
    PROTECT_CORE_INVARIANTS = "PROTECT_CORE_INVARIANTS"
    RESTORE_MISSION_ALIGNMENT = "RESTORE_MISSION_ALIGNMENT"
    RESTORE_PRIORITY_INVARIANTS = "RESTORE_PRIORITY_INVARIANTS"
    SYNC_GOVERNANCE_WITH_IDENTITY = "SYNC_GOVERNANCE_WITH_IDENTITY"
    SYNC_POLICY_WITH_IDENTITY = "SYNC_POLICY_WITH_IDENTITY"
    REPAIR_IDENTITY_CONTEXT = "REPAIR_IDENTITY_CONTEXT"
    KEEP_AUTONOMY_REDUCED = "KEEP_AUTONOMY_REDUCED"
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"
    LOCK_IDENTITY_STATE = "LOCK_IDENTITY_STATE"


class CognitiveIdentityRecommendation(StrEnum):
    """Recommended controls emitted by cognitive identity."""

    CONTINUE_IDENTITY_MONITORING = "CONTINUE_IDENTITY_MONITORING"
    VERIFY_MISSION_ALIGNMENT = "VERIFY_MISSION_ALIGNMENT"
    PROTECT_STRATEGIC_DNA = "PROTECT_STRATEGIC_DNA"
    RECHECK_PRIORITY_ORDER = "RECHECK_PRIORITY_ORDER"
    REPAIR_IDENTITY_FRAGMENTATION = "REPAIR_IDENTITY_FRAGMENTATION"
    UPDATE_IDENTITY_SNAPSHOT = "UPDATE_IDENTITY_SNAPSHOT"
    KEEP_RECOVERY_CONTEXT_ACTIVE = "KEEP_RECOVERY_CONTEXT_ACTIVE"
    LIMIT_AUTONOMY_EXPANSION = "LIMIT_AUTONOMY_EXPANSION"
    REQUIRE_SUPERVISION = "REQUIRE_SUPERVISION"
    PRESERVE_CORE_IDENTITY = "PRESERVE_CORE_IDENTITY"


@dataclass(frozen=True)
class CognitiveInvariant:
    """One core identity invariant that should remain protected."""

    name: str
    description: str
    priority: int
    score: int
    protected: bool
    violated_by: tuple[CognitiveIdentityRisk, ...] = ()


@dataclass(frozen=True)
class CognitiveIdentityProfile:
    """Explainable identity profile assembled from mission and strategy context."""

    profile_name: str
    mission_statement: str
    strategy_name: str | None
    core_priorities: tuple[str, ...]
    invariants: tuple[CognitiveInvariant, ...]
    identity_score: int
    autonomy_limited: bool
    locked: bool


@dataclass(frozen=True)
class CognitiveIdentityScore:
    """Identity component scores normalized to 0..100."""

    mission_alignment_score: int
    strategic_dna_score: int
    priority_invariant_score: int
    governance_identity_score: int
    policy_identity_score: int
    world_model_identity_score: int
    consensus_identity_score: int
    continuity_identity_score: int
    autonomy_safety_score: int


@dataclass(frozen=True)
class CognitiveIdentityInput:
    """Inputs consumed by the offline cognitive identity engine."""

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
    system_integrity: SystemIntegrityResult | None = None
    mission_continuity: MissionContinuityResult | None = None
    strategic_timeline_analysis: StrategicTimelineAnalysis | None = None
    strategy_dna: StrategyDNA | None = None


@dataclass(frozen=True)
class CognitiveIdentityEvent:
    """Auditable cognitive identity event."""

    state: CognitiveIdentityState
    mode: CognitiveIdentityMode
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class CognitiveIdentityResult:
    """Final autonomous cognitive identity result."""

    state: CognitiveIdentityState
    mode: CognitiveIdentityMode
    identity_score: int
    score_breakdown: CognitiveIdentityScore
    profile: CognitiveIdentityProfile
    invariants: tuple[CognitiveInvariant, ...]
    risks: tuple[CognitiveIdentityRisk, ...]
    actions: tuple[CognitiveIdentityAction, ...]
    recommendations: tuple[CognitiveIdentityRecommendation, ...]
    events: tuple[CognitiveIdentityEvent, ...]
    summary: str


__all__ = [
    "CognitiveIdentityAction",
    "CognitiveIdentityEvent",
    "CognitiveIdentityInput",
    "CognitiveIdentityMode",
    "CognitiveIdentityProfile",
    "CognitiveIdentityRecommendation",
    "CognitiveIdentityResult",
    "CognitiveIdentityRisk",
    "CognitiveIdentityScore",
    "CognitiveIdentityState",
    "CognitiveInvariant",
]
