"""Models for the offline Autonomous Cognitive Recovery Engine."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .cognitive_governance_models import CognitiveGovernanceResult
from .cognitive_policy_models import CognitivePolicyResult
from .cognitive_resilience_models import CognitiveResilienceResult
from .cognitive_stability_models import CognitiveStabilityResult
from .collective_consensus_models import ConsensusResult
from .global_orchestrator_models import GlobalOrchestratorResult
from .intent_alignment_models import IntentAlignmentResult
from .mission_continuity_models import MissionContinuityResult
from .recursive_world_model_models import RecursiveWorldModelResult
from .recovery_resilience_models import RecoveryResilienceResult
from .self_reflection_audit_models import SelfReflectionAuditResult
from .strategic_arbitration_models import ArbitrationResult
from .system_integrity_models import SystemIntegrityResult


class CognitiveRecoveryState(StrEnum):
    """Current deep cognitive recovery state."""

    RECOVERED = "RECOVERED"
    RECOVERING = "RECOVERING"
    PARTIAL_RECOVERY = "PARTIAL_RECOVERY"
    DEGRADED_RECOVERY = "DEGRADED_RECOVERY"
    FAILED_RECOVERY = "FAILED_RECOVERY"
    SAFE_RECOVERY = "SAFE_RECOVERY"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"


class CognitiveRecoveryMode(StrEnum):
    """Mode used to rebuild cognitive layers."""

    NORMAL_RECOVERY = "NORMAL_RECOVERY"
    MINIMAL_RECONSTRUCTION = "MINIMAL_RECONSTRUCTION"
    CONSENSUS_REBUILD = "CONSENSUS_REBUILD"
    GOVERNANCE_RESTORE = "GOVERNANCE_RESTORE"
    WORLD_MODEL_RESTORE = "WORLD_MODEL_RESTORE"
    POLICY_REPAIR = "POLICY_REPAIR"
    STABILITY_REBUILD = "STABILITY_REBUILD"
    SAFE_RECOVERY_MODE = "SAFE_RECOVERY_MODE"
    LOCKED_RECOVERY = "LOCKED_RECOVERY"


class CognitiveRecoveryRisk(StrEnum):
    """Risks that can block deep cognitive recovery."""

    RECOVERY_LOOP = "RECOVERY_LOOP"
    RECOVERY_FAILURE = "RECOVERY_FAILURE"
    CONSENSUS_REBUILD_FAILURE = "CONSENSUS_REBUILD_FAILURE"
    GOVERNANCE_RESTORE_FAILURE = "GOVERNANCE_RESTORE_FAILURE"
    POLICY_REPAIR_FAILURE = "POLICY_REPAIR_FAILURE"
    WORLD_MODEL_RESTORE_FAILURE = "WORLD_MODEL_RESTORE_FAILURE"
    STABILITY_REBUILD_FAILURE = "STABILITY_REBUILD_FAILURE"
    MEMORY_RESTORE_RISK = "MEMORY_RESTORE_RISK"
    UNSAFE_RECOVERY_PATH = "UNSAFE_RECOVERY_PATH"
    PREMATURE_REACTIVATION = "PREMATURE_REACTIVATION"


class CognitiveRecoveryAction(StrEnum):
    """Actions available to rebuild cognitive layers."""

    REBUILD_MINIMAL_CORE = "REBUILD_MINIMAL_CORE"
    RESTORE_CONSENSUS = "RESTORE_CONSENSUS"
    RESTORE_GOVERNANCE = "RESTORE_GOVERNANCE"
    REPAIR_POLICIES = "REPAIR_POLICIES"
    RESTORE_WORLD_MODEL = "RESTORE_WORLD_MODEL"
    REBUILD_STABILITY = "REBUILD_STABILITY"
    PROTECT_MEMORY = "PROTECT_MEMORY"
    KEEP_AUTONOMY_REDUCED = "KEEP_AUTONOMY_REDUCED"
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"
    MARK_RECOVERY_COMPLETE = "MARK_RECOVERY_COMPLETE"


class CognitiveRecoveryRecommendation(StrEnum):
    """Recommended controls during recovery."""

    CONTINUE_RECOVERY = "CONTINUE_RECOVERY"
    EXTEND_RECOVERY_WINDOW = "EXTEND_RECOVERY_WINDOW"
    RESTORE_MINIMAL_CONSENSUS_FIRST = "RESTORE_MINIMAL_CONSENSUS_FIRST"
    REPAIR_GOVERNANCE_BEFORE_POLICY = "REPAIR_GOVERNANCE_BEFORE_POLICY"
    VALIDATE_WORLD_MODEL_BEFORE_ACTION = "VALIDATE_WORLD_MODEL_BEFORE_ACTION"
    KEEP_LEARNING_FROZEN = "KEEP_LEARNING_FROZEN"
    KEEP_EXECUTION_DISABLED = "KEEP_EXECUTION_DISABLED"
    RECHECK_STABILITY = "RECHECK_STABILITY"
    PRESERVE_RECOVERY_CHECKPOINT = "PRESERVE_RECOVERY_CHECKPOINT"
    ESCALATE_TO_HUMAN_REVIEW = "ESCALATE_TO_HUMAN_REVIEW"


@dataclass(frozen=True)
class CognitiveRecoveryStep:
    """One ordered recovery step."""

    order: int
    action: CognitiveRecoveryAction
    target_layer: str
    reason: str
    required_before_autonomy: bool = True
    completed: bool = False


@dataclass(frozen=True)
class CognitiveRecoveryCheckpoint:
    """Checkpoint preserving recovery progress."""

    checkpoint_id: str
    layer: str
    score: int
    stable: bool
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class CognitiveRecoveryPlan:
    """Ordered deep cognitive recovery plan."""

    steps: tuple[CognitiveRecoveryStep, ...]
    checkpoints: tuple[CognitiveRecoveryCheckpoint, ...]
    learning_frozen: bool
    execution_disabled: bool
    autonomy_reduced: bool
    minimal_core_required: bool
    complete: bool


@dataclass(frozen=True)
class CognitiveRecoveryScore:
    """Recovery score components normalized to 0..100."""

    minimal_core_score: int
    consensus_recovery_score: int
    governance_recovery_score: int
    policy_recovery_score: int
    world_model_recovery_score: int
    stability_recovery_score: int
    memory_recovery_score: int
    orchestration_recovery_score: int


@dataclass(frozen=True)
class CognitiveRecoveryInput:
    """Inputs consumed by the offline cognitive recovery engine."""

    cognitive_resilience: CognitiveResilienceResult | None = None
    cognitive_stability: CognitiveStabilityResult | None = None
    cognitive_policy: CognitivePolicyResult | None = None
    cognitive_governance: CognitiveGovernanceResult | None = None
    self_reflection_audit: SelfReflectionAuditResult | None = None
    recursive_world_model: RecursiveWorldModelResult | None = None
    global_orchestrator: GlobalOrchestratorResult | None = None
    collective_consensus: ConsensusResult | None = None
    strategic_arbitration: ArbitrationResult | None = None
    intent_alignment: IntentAlignmentResult | None = None
    system_integrity: SystemIntegrityResult | None = None
    mission_continuity: MissionContinuityResult | None = None
    recovery_resilience: RecoveryResilienceResult | None = None
    previous_checkpoints: tuple[CognitiveRecoveryCheckpoint, ...] = ()


@dataclass(frozen=True)
class CognitiveRecoveryEvent:
    """Auditable cognitive recovery event."""

    state: CognitiveRecoveryState
    mode: CognitiveRecoveryMode
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class CognitiveRecoveryResult:
    """Final autonomous cognitive recovery result."""

    state: CognitiveRecoveryState
    mode: CognitiveRecoveryMode
    recovery_score: int
    score_breakdown: CognitiveRecoveryScore
    risks: tuple[CognitiveRecoveryRisk, ...]
    actions: tuple[CognitiveRecoveryAction, ...]
    recovery_plan: CognitiveRecoveryPlan
    checkpoints: tuple[CognitiveRecoveryCheckpoint, ...]
    recommendations: tuple[CognitiveRecoveryRecommendation, ...]
    events: tuple[CognitiveRecoveryEvent, ...]
    summary: str


__all__ = [
    "CognitiveRecoveryAction",
    "CognitiveRecoveryCheckpoint",
    "CognitiveRecoveryEvent",
    "CognitiveRecoveryInput",
    "CognitiveRecoveryMode",
    "CognitiveRecoveryPlan",
    "CognitiveRecoveryRecommendation",
    "CognitiveRecoveryResult",
    "CognitiveRecoveryRisk",
    "CognitiveRecoveryScore",
    "CognitiveRecoveryState",
    "CognitiveRecoveryStep",
]
