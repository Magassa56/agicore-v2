"""Models for the offline Autonomous Cognitive Intent Integrity Engine."""
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
from .mission_continuity_models import MissionContinuityResult
from .recursive_world_model_models import RecursiveWorldModelResult
from .self_reflection_audit_models import SelfReflectionAuditResult
from .strategic_memory_models import StrategicTimelineAnalysis
from .system_integrity_models import SystemIntegrityResult


class IntentIntegrityState(StrEnum):
    """Current intent integrity state."""

    INTENT_INTACT = "INTENT_INTACT"
    INTENT_WATCH = "INTENT_WATCH"
    INTENT_DRIFT = "INTENT_DRIFT"
    INTENT_CONFLICT = "INTENT_CONFLICT"
    INTENT_CORRUPTED = "INTENT_CORRUPTED"
    INTENT_AT_RISK = "INTENT_AT_RISK"
    INTENT_REPAIRING = "INTENT_REPAIRING"
    INTENT_LOCKED = "INTENT_LOCKED"


class IntentIntegrityMode(StrEnum):
    """Operating mode for intent integrity."""

    NORMAL_INTENT_INTEGRITY = "NORMAL_INTENT_INTEGRITY"
    INTENT_MONITORING = "INTENT_MONITORING"
    INTENT_CHAIN_VERIFICATION = "INTENT_CHAIN_VERIFICATION"
    MISSION_INTENT_PROTECTION = "MISSION_INTENT_PROTECTION"
    IDENTITY_INTENT_SYNC = "IDENTITY_INTENT_SYNC"
    POLICY_INTENT_ENFORCEMENT = "POLICY_INTENT_ENFORCEMENT"
    SAFE_INTENT_MODE = "SAFE_INTENT_MODE"
    LOCKED_INTENT_MODE = "LOCKED_INTENT_MODE"


class IntentIntegrityRisk(StrEnum):
    """Risks that can break internal intent integrity."""

    INTENT_DRIFT_RISK = "INTENT_DRIFT_RISK"
    MISSION_INTENT_MISMATCH = "MISSION_INTENT_MISMATCH"
    IDENTITY_INTENT_CONFLICT = "IDENTITY_INTENT_CONFLICT"
    POLICY_INTENT_CONFLICT = "POLICY_INTENT_CONFLICT"
    GOVERNANCE_INTENT_CONFLICT = "GOVERNANCE_INTENT_CONFLICT"
    DECISION_INTENT_MISMATCH = "DECISION_INTENT_MISMATCH"
    AUTONOMY_INTENT_EXPANSION = "AUTONOMY_INTENT_EXPANSION"
    INTENT_CHAIN_BREAK = "INTENT_CHAIN_BREAK"
    INTENT_CORRUPTION_RISK = "INTENT_CORRUPTION_RISK"
    INTENT_COLLAPSE_RISK = "INTENT_COLLAPSE_RISK"


class IntentIntegrityAction(StrEnum):
    """Actions available to restore intent integrity."""

    PRESERVE_INTENT_CHAIN = "PRESERVE_INTENT_CHAIN"
    VERIFY_MISSION_INTENT = "VERIFY_MISSION_INTENT"
    SYNC_IDENTITY_INTENT = "SYNC_IDENTITY_INTENT"
    ENFORCE_POLICY_INTENT = "ENFORCE_POLICY_INTENT"
    RESTORE_DECISION_INTENT_LINK = "RESTORE_DECISION_INTENT_LINK"
    REDUCE_AUTONOMY = "REDUCE_AUTONOMY"
    REQUIRE_INTENT_AUDIT = "REQUIRE_INTENT_AUDIT"
    LOCK_INTENT_STATE = "LOCK_INTENT_STATE"
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"
    MARK_INTENT_INTEGRITY_RESTORED = "MARK_INTENT_INTEGRITY_RESTORED"


class IntentIntegrityRecommendation(StrEnum):
    """Recommended controls from intent integrity."""

    CONTINUE_INTENT_MONITORING = "CONTINUE_INTENT_MONITORING"
    VERIFY_MISSION_OBJECTIVES = "VERIFY_MISSION_OBJECTIVES"
    REPAIR_INTENT_CHAIN = "REPAIR_INTENT_CHAIN"
    ALIGN_INTENT_WITH_IDENTITY = "ALIGN_INTENT_WITH_IDENTITY"
    ALIGN_INTENT_WITH_POLICY = "ALIGN_INTENT_WITH_POLICY"
    RECHECK_GOVERNANCE_CONSISTENCY = "RECHECK_GOVERNANCE_CONSISTENCY"
    REDUCE_AUTONOMY_DURING_INTENT_REPAIR = "REDUCE_AUTONOMY_DURING_INTENT_REPAIR"
    REQUIRE_SUPERVISION = "REQUIRE_SUPERVISION"
    UPDATE_INTENT_SNAPSHOT = "UPDATE_INTENT_SNAPSHOT"
    PRESERVE_CORE_INTENT = "PRESERVE_CORE_INTENT"


@dataclass(frozen=True)
class IntentIntegrityCheck:
    """One auditable check in the intent integrity chain."""

    name: str
    passed: bool
    score: int
    risk: IntentIntegrityRisk | None
    message: str


@dataclass(frozen=True)
class IntentChain:
    """Explainable chain linking mission, identity, policies and decisions."""

    mission_intent: str
    identity_intent: str
    policy_intent: str
    governance_intent: str
    decision_intent: str
    chain_score: int
    broken_links: tuple[str, ...]
    verified: bool


@dataclass(frozen=True)
class IntentIntegrityScore:
    """Intent integrity component scores normalized to 0..100."""

    mission_intent_score: int
    identity_intent_score: int
    policy_intent_score: int
    governance_intent_score: int
    decision_link_score: int
    autonomy_intent_score: int
    chain_integrity_score: int
    corruption_resistance_score: int


@dataclass(frozen=True)
class IntentIntegrityInput:
    """Inputs consumed by the offline intent integrity engine."""

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
    system_integrity: SystemIntegrityResult | None = None
    mission_continuity: MissionContinuityResult | None = None
    strategic_timeline_analysis: StrategicTimelineAnalysis | None = None


@dataclass(frozen=True)
class IntentIntegrityEvent:
    """Auditable intent integrity event."""

    state: IntentIntegrityState
    mode: IntentIntegrityMode
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class IntentIntegrityResult:
    """Final autonomous intent integrity result."""

    state: IntentIntegrityState
    mode: IntentIntegrityMode
    intent_integrity_score: int
    score_breakdown: IntentIntegrityScore
    intent_chain: IntentChain
    checks: tuple[IntentIntegrityCheck, ...]
    risks: tuple[IntentIntegrityRisk, ...]
    actions: tuple[IntentIntegrityAction, ...]
    recommendations: tuple[IntentIntegrityRecommendation, ...]
    events: tuple[IntentIntegrityEvent, ...]
    summary: str


__all__ = [
    "IntentChain",
    "IntentIntegrityAction",
    "IntentIntegrityCheck",
    "IntentIntegrityEvent",
    "IntentIntegrityInput",
    "IntentIntegrityMode",
    "IntentIntegrityRecommendation",
    "IntentIntegrityResult",
    "IntentIntegrityRisk",
    "IntentIntegrityScore",
    "IntentIntegrityState",
]
