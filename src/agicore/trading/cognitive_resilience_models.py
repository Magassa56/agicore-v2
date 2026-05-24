"""Models for the offline Autonomous Cognitive Resilience Engine."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .behavioral_stability_models import BehavioralStabilityResult
from .cognitive_governance_models import CognitiveGovernanceResult
from .cognitive_policy_models import CognitivePolicyResult
from .cognitive_stability_models import CognitiveStabilityResult
from .collective_consensus_models import ConsensusResult
from .global_orchestrator_models import GlobalOrchestratorResult
from .intent_alignment_models import IntentAlignmentResult
from .mission_continuity_models import MissionContinuityResult
from .operational_awareness_models import OperationalAwarenessResult
from .recursive_world_model_models import RecursiveWorldModelResult
from .recovery_resilience_models import RecoveryResilienceResult
from .self_reflection_audit_models import SelfReflectionAuditResult
from .strategic_arbitration_models import ArbitrationResult
from .system_integrity_models import SystemIntegrityResult


class CognitiveResilienceState(StrEnum):
    """Current cognitive resilience state."""

    RESILIENT = "RESILIENT"
    WATCH = "WATCH"
    DEGRADED = "DEGRADED"
    FRAGILE = "FRAGILE"
    CRITICAL = "CRITICAL"
    RECOVERING = "RECOVERING"
    COGNITIVE_SURVIVAL = "COGNITIVE_SURVIVAL"


class CognitiveResilienceMode(StrEnum):
    """Operating mode for cognitive resilience."""

    NORMAL_RESILIENCE = "NORMAL_RESILIENCE"
    MONITORING_RESILIENCE = "MONITORING_RESILIENCE"
    STABILIZE_COGNITION = "STABILIZE_COGNITION"
    ISOLATE_FAILURES = "ISOLATE_FAILURES"
    REBUILD_CONSENSUS = "REBUILD_CONSENSUS"
    PROTECT_MEMORY = "PROTECT_MEMORY"
    SURVIVAL_COGNITION = "SURVIVAL_COGNITION"
    LOCKED_RESILIENCE = "LOCKED_RESILIENCE"


class CognitiveResilienceRisk(StrEnum):
    """Risks that threaten cognitive resilience."""

    COGNITIVE_COLLAPSE_RISK = "COGNITIVE_COLLAPSE_RISK"
    CONSENSUS_BREAKDOWN = "CONSENSUS_BREAKDOWN"
    GOVERNANCE_FAILURE = "GOVERNANCE_FAILURE"
    POLICY_FAILURE = "POLICY_FAILURE"
    WORLD_MODEL_FAILURE = "WORLD_MODEL_FAILURE"
    ORCHESTRATION_FAILURE = "ORCHESTRATION_FAILURE"
    MEMORY_RISK = "MEMORY_RISK"
    RECURSIVE_FAILURE = "RECURSIVE_FAILURE"
    STRATEGIC_DRIFT_SURGE = "STRATEGIC_DRIFT_SURGE"
    BEHAVIORAL_DESTABILIZATION = "BEHAVIORAL_DESTABILIZATION"


class CognitiveResilienceAction(StrEnum):
    """Actions available to restore cognitive resilience."""

    KEEP_RUNNING = "KEEP_RUNNING"
    REDUCE_AUTONOMY = "REDUCE_AUTONOMY"
    ISOLATE_FAILURE_DOMAIN = "ISOLATE_FAILURE_DOMAIN"
    PROTECT_CRITICAL_MEMORY = "PROTECT_CRITICAL_MEMORY"
    REBUILD_MINIMAL_CONSENSUS = "REBUILD_MINIMAL_CONSENSUS"
    FREEZE_RECURSIVE_UPDATES = "FREEZE_RECURSIVE_UPDATES"
    FREEZE_STRATEGY_EVOLUTION = "FREEZE_STRATEGY_EVOLUTION"
    ENTER_COGNITIVE_SURVIVAL_MODE = "ENTER_COGNITIVE_SURVIVAL_MODE"
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"
    RESTORE_STABLE_BASELINE = "RESTORE_STABLE_BASELINE"


class CognitiveResilienceRecommendation(StrEnum):
    """Recommended resilience controls."""

    CONTINUE_RESILIENCE_MONITORING = "CONTINUE_RESILIENCE_MONITORING"
    STABILIZE_GOVERNANCE = "STABILIZE_GOVERNANCE"
    REBUILD_CONSENSUS_LAYER = "REBUILD_CONSENSUS_LAYER"
    PROTECT_WORLD_MODEL = "PROTECT_WORLD_MODEL"
    LOCK_HIGH_RISK_POLICIES = "LOCK_HIGH_RISK_POLICIES"
    PRESERVE_STRATEGIC_MEMORY = "PRESERVE_STRATEGIC_MEMORY"
    REDUCE_RECURSIVE_DEPTH = "REDUCE_RECURSIVE_DEPTH"
    INITIATE_COGNITIVE_RECOVERY = "INITIATE_COGNITIVE_RECOVERY"
    REQUIRE_SUPERVISION = "REQUIRE_SUPERVISION"
    RECHECK_SYSTEM_STABILITY = "RECHECK_SYSTEM_STABILITY"


@dataclass(frozen=True)
class CognitiveFailureDomain:
    """One isolated or monitored cognitive failure domain."""

    name: str
    risk: CognitiveResilienceRisk
    severity_score: int
    isolate: bool
    recovery_action: CognitiveResilienceAction
    reason: str


@dataclass(frozen=True)
class CognitiveRecoveryPlan:
    """Ordered offline cognitive recovery plan."""

    steps: tuple[CognitiveResilienceAction, ...]
    failure_domains: tuple[CognitiveFailureDomain, ...]
    protected_memory: bool
    minimal_consensus_required: bool
    recursive_updates_frozen: bool
    survival_mode_required: bool


@dataclass(frozen=True)
class CognitiveResilienceScore:
    """Resilience component scores normalized to 0..100."""

    stability_resilience_score: int
    governance_resilience_score: int
    policy_resilience_score: int
    consensus_resilience_score: int
    world_model_resilience_score: int
    orchestration_resilience_score: int
    memory_resilience_score: int
    behavioral_resilience_score: int


@dataclass(frozen=True)
class CognitiveResilienceInput:
    """Inputs consumed by the offline cognitive resilience engine."""

    cognitive_stability: CognitiveStabilityResult | None = None
    cognitive_policy: CognitivePolicyResult | None = None
    cognitive_governance: CognitiveGovernanceResult | None = None
    self_reflection_audit: SelfReflectionAuditResult | None = None
    recursive_world_model: RecursiveWorldModelResult | None = None
    global_orchestrator: GlobalOrchestratorResult | None = None
    collective_consensus: ConsensusResult | None = None
    strategic_arbitration: ArbitrationResult | None = None
    intent_alignment: IntentAlignmentResult | None = None
    operational_awareness: OperationalAwarenessResult | None = None
    system_integrity: SystemIntegrityResult | None = None
    mission_continuity: MissionContinuityResult | None = None
    recovery_resilience: RecoveryResilienceResult | None = None
    behavioral_stability: BehavioralStabilityResult | None = None


@dataclass(frozen=True)
class CognitiveResilienceEvent:
    """Auditable cognitive resilience event."""

    state: CognitiveResilienceState
    mode: CognitiveResilienceMode
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class CognitiveResilienceResult:
    """Final autonomous cognitive resilience result."""

    state: CognitiveResilienceState
    mode: CognitiveResilienceMode
    resilience_score: int
    score_breakdown: CognitiveResilienceScore
    risks: tuple[CognitiveResilienceRisk, ...]
    actions: tuple[CognitiveResilienceAction, ...]
    failure_domains: tuple[CognitiveFailureDomain, ...]
    recovery_plan: CognitiveRecoveryPlan
    recommendations: tuple[CognitiveResilienceRecommendation, ...]
    events: tuple[CognitiveResilienceEvent, ...]
    summary: str


__all__ = [
    "CognitiveFailureDomain",
    "CognitiveRecoveryPlan",
    "CognitiveResilienceAction",
    "CognitiveResilienceEvent",
    "CognitiveResilienceInput",
    "CognitiveResilienceMode",
    "CognitiveResilienceRecommendation",
    "CognitiveResilienceResult",
    "CognitiveResilienceRisk",
    "CognitiveResilienceScore",
    "CognitiveResilienceState",
]
