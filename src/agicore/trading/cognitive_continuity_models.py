"""Models for the offline Autonomous Cognitive Continuity Engine."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

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
from .recovery_resilience_models import RecoveryResilienceResult
from .self_reflection_audit_models import SelfReflectionAuditResult
from .strategic_memory_models import StrategicTimelineAnalysis
from .system_integrity_models import SystemIntegrityResult


class CognitiveContinuityState(StrEnum):
    """Current cognitive continuity state."""

    CONTINUOUS = "CONTINUOUS"
    WATCH = "WATCH"
    DEGRADED_CONTINUITY = "DEGRADED_CONTINUITY"
    FRAGMENTED_CONTINUITY = "FRAGMENTED_CONTINUITY"
    MISSION_AT_RISK = "MISSION_AT_RISK"
    IDENTITY_DRIFT = "IDENTITY_DRIFT"
    CONTINUITY_FAILURE = "CONTINUITY_FAILURE"
    RECOVERING_CONTINUITY = "RECOVERING_CONTINUITY"


class CognitiveContinuityMode(StrEnum):
    """Operating mode for cognitive continuity."""

    NORMAL_CONTINUITY = "NORMAL_CONTINUITY"
    MEMORY_PRESERVATION = "MEMORY_PRESERVATION"
    MISSION_PRESERVATION = "MISSION_PRESERVATION"
    IDENTITY_PRESERVATION = "IDENTITY_PRESERVATION"
    DECISION_CHAIN_REPAIR = "DECISION_CHAIN_REPAIR"
    RECOVERY_CONTINUITY = "RECOVERY_CONTINUITY"
    SAFE_CONTINUITY_MODE = "SAFE_CONTINUITY_MODE"
    LOCKED_CONTINUITY = "LOCKED_CONTINUITY"


class CognitiveContinuityRisk(StrEnum):
    """Risks that can break cognitive continuity."""

    MEMORY_CONTINUITY_BREAK = "MEMORY_CONTINUITY_BREAK"
    DECISION_CHAIN_BREAK = "DECISION_CHAIN_BREAK"
    MISSION_DRIFT = "MISSION_DRIFT"
    STRATEGIC_IDENTITY_DRIFT = "STRATEGIC_IDENTITY_DRIFT"
    PRIORITY_ORDER_LOSS = "PRIORITY_ORDER_LOSS"
    RECOVERY_DISCONTINUITY = "RECOVERY_DISCONTINUITY"
    GOVERNANCE_CONTINUITY_RISK = "GOVERNANCE_CONTINUITY_RISK"
    WORLD_MODEL_CONTINUITY_RISK = "WORLD_MODEL_CONTINUITY_RISK"
    CONSENSUS_CONTINUITY_RISK = "CONSENSUS_CONTINUITY_RISK"
    EXECUTION_CONTEXT_LOSS = "EXECUTION_CONTEXT_LOSS"


class CognitiveContinuityAction(StrEnum):
    """Actions available to preserve cognitive continuity."""

    PRESERVE_STRATEGIC_MEMORY = "PRESERVE_STRATEGIC_MEMORY"
    REPAIR_DECISION_CHAIN = "REPAIR_DECISION_CHAIN"
    RESTORE_MISSION_ANCHOR = "RESTORE_MISSION_ANCHOR"
    RESTORE_PRIORITY_ORDER = "RESTORE_PRIORITY_ORDER"
    PROTECT_IDENTITY_ANCHOR = "PROTECT_IDENTITY_ANCHOR"
    SYNC_WORLD_MODEL_CONTEXT = "SYNC_WORLD_MODEL_CONTEXT"
    REBUILD_CONSENSUS_CONTEXT = "REBUILD_CONSENSUS_CONTEXT"
    KEEP_AUTONOMY_REDUCED = "KEEP_AUTONOMY_REDUCED"
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"
    MARK_CONTINUITY_RESTORED = "MARK_CONTINUITY_RESTORED"


class CognitiveContinuityRecommendation(StrEnum):
    """Recommended continuity controls."""

    CONTINUE_CONTINUITY_MONITORING = "CONTINUE_CONTINUITY_MONITORING"
    EXTEND_MEMORY_CHECKPOINTS = "EXTEND_MEMORY_CHECKPOINTS"
    RESTORE_MISSION_BEFORE_ACTION = "RESTORE_MISSION_BEFORE_ACTION"
    VERIFY_IDENTITY_ANCHORS = "VERIFY_IDENTITY_ANCHORS"
    REPAIR_DECISION_TRACE = "REPAIR_DECISION_TRACE"
    KEEP_RECOVERY_MODE_ACTIVE = "KEEP_RECOVERY_MODE_ACTIVE"
    PROTECT_GOVERNANCE_CONTEXT = "PROTECT_GOVERNANCE_CONTEXT"
    UPDATE_CONTINUITY_SNAPSHOT = "UPDATE_CONTINUITY_SNAPSHOT"
    REQUIRE_SUPERVISION = "REQUIRE_SUPERVISION"
    RECHECK_WORLD_MODEL_ALIGNMENT = "RECHECK_WORLD_MODEL_ALIGNMENT"


@dataclass(frozen=True)
class CognitiveContinuityAnchor:
    """One continuity anchor preserving identity, mission or context."""

    name: str
    score: int
    protected: bool
    risk: CognitiveContinuityRisk | None
    note: str


@dataclass(frozen=True)
class CognitiveContinuityPlan:
    """Plan for preserving cognitive continuity."""

    anchors: tuple[CognitiveContinuityAnchor, ...]
    actions: tuple[CognitiveContinuityAction, ...]
    memory_preserved: bool
    mission_preserved: bool
    identity_preserved: bool
    autonomy_reduced: bool
    human_review_required: bool


@dataclass(frozen=True)
class CognitiveContinuityScore:
    """Continuity component scores normalized to 0..100."""

    memory_continuity_score: int
    decision_chain_score: int
    mission_anchor_score: int
    strategic_identity_score: int
    priority_order_score: int
    recovery_continuity_score: int
    governance_context_score: int
    world_model_context_score: int
    consensus_context_score: int


@dataclass(frozen=True)
class CognitiveContinuityInput:
    """Inputs consumed by the offline cognitive continuity engine."""

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
    recovery_resilience: RecoveryResilienceResult | None = None


@dataclass(frozen=True)
class CognitiveContinuityEvent:
    """Auditable cognitive continuity event."""

    state: CognitiveContinuityState
    mode: CognitiveContinuityMode
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class CognitiveContinuityResult:
    """Final autonomous cognitive continuity result."""

    state: CognitiveContinuityState
    mode: CognitiveContinuityMode
    continuity_score: int
    score_breakdown: CognitiveContinuityScore
    anchors: tuple[CognitiveContinuityAnchor, ...]
    risks: tuple[CognitiveContinuityRisk, ...]
    actions: tuple[CognitiveContinuityAction, ...]
    continuity_plan: CognitiveContinuityPlan
    recommendations: tuple[CognitiveContinuityRecommendation, ...]
    events: tuple[CognitiveContinuityEvent, ...]
    summary: str


__all__ = [
    "CognitiveContinuityAction",
    "CognitiveContinuityAnchor",
    "CognitiveContinuityEvent",
    "CognitiveContinuityInput",
    "CognitiveContinuityMode",
    "CognitiveContinuityPlan",
    "CognitiveContinuityRecommendation",
    "CognitiveContinuityResult",
    "CognitiveContinuityRisk",
    "CognitiveContinuityScore",
    "CognitiveContinuityState",
]
