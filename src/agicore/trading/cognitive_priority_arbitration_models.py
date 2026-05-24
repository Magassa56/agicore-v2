"""Models for offline cognitive priority arbitration."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from agicore.trading.cognitive_alignment_models import CognitiveAlignmentResult
from agicore.trading.cognitive_coherence_models import CognitiveCoherenceResult
from agicore.trading.cognitive_consensus_models import CognitiveConsensusResult
from agicore.trading.cognitive_continuity_models import CognitiveContinuityResult
from agicore.trading.cognitive_executive_control_models import CognitiveExecutiveControlResult
from agicore.trading.cognitive_governance_models import CognitiveGovernanceResult
from agicore.trading.cognitive_identity_models import CognitiveIdentityResult
from agicore.trading.cognitive_memory_consolidation_models import CognitiveMemoryConsolidationResult
from agicore.trading.cognitive_policy_models import CognitivePolicyResult
from agicore.trading.cognitive_recovery_models import CognitiveRecoveryResult
from agicore.trading.cognitive_resilience_models import CognitiveResilienceResult
from agicore.trading.cognitive_stability_models import CognitiveStabilityResult
from agicore.trading.intent_integrity_models import IntentIntegrityResult
from agicore.trading.mission_continuity_models import MissionContinuityResult
from agicore.trading.recursive_world_model_models import RecursiveWorldModelResult
from agicore.trading.self_reflection_audit_models import SelfReflectionAuditResult
from agicore.trading.system_integrity_models import SystemIntegrityResult


class PriorityArbitrationState(str, Enum):
    PRIORITY_ARBITRATION_STABLE = "PRIORITY_ARBITRATION_STABLE"
    PRIORITY_ARBITRATION_CONFLICTED = "PRIORITY_ARBITRATION_CONFLICTED"
    PRIORITY_ARBITRATION_ESCALATED = "PRIORITY_ARBITRATION_ESCALATED"
    PRIORITY_ARBITRATION_DEGRADED = "PRIORITY_ARBITRATION_DEGRADED"
    PRIORITY_ARBITRATION_CRITICAL = "PRIORITY_ARBITRATION_CRITICAL"
    PRIORITY_ARBITRATION_LOCKED = "PRIORITY_ARBITRATION_LOCKED"
    PRIORITY_ARBITRATION_RECOVERING = "PRIORITY_ARBITRATION_RECOVERING"


class PriorityArbitrationMode(str, Enum):
    NORMAL_ARBITRATION = "NORMAL_ARBITRATION"
    SAFETY_FIRST_ARBITRATION = "SAFETY_FIRST_ARBITRATION"
    RECOVERY_PRIORITY_MODE = "RECOVERY_PRIORITY_MODE"
    CAPITAL_PRESERVATION_MODE = "CAPITAL_PRESERVATION_MODE"
    EXECUTIVE_OVERRIDE_MODE = "EXECUTIVE_OVERRIDE_MODE"
    SAFE_MODE_ARBITRATION = "SAFE_MODE_ARBITRATION"
    EMERGENCY_ARBITRATION = "EMERGENCY_ARBITRATION"
    LOCKED_ARBITRATION_MODE = "LOCKED_ARBITRATION_MODE"


class PriorityArbitrationRisk(str, Enum):
    PRIORITY_COLLISION = "PRIORITY_COLLISION"
    SAFETY_PRIORITY_LOSS = "SAFETY_PRIORITY_LOSS"
    CAPITAL_PROTECTION_FAILURE = "CAPITAL_PROTECTION_FAILURE"
    EXECUTIVE_PRIORITY_CONFLICT = "EXECUTIVE_PRIORITY_CONFLICT"
    POLICY_ALIGNMENT_CONFLICT = "POLICY_ALIGNMENT_CONFLICT"
    RECOVERY_PRIORITY_SUPPRESSION = "RECOVERY_PRIORITY_SUPPRESSION"
    COHERENCE_PRIORITY_DRIFT = "COHERENCE_PRIORITY_DRIFT"
    CONSENSUS_PRIORITY_FAILURE = "CONSENSUS_PRIORITY_FAILURE"
    SYSTEMIC_PRIORITY_COLLAPSE = "SYSTEMIC_PRIORITY_COLLAPSE"
    UNRESOLVED_PRIORITY_DEADLOCK = "UNRESOLVED_PRIORITY_DEADLOCK"


class PriorityArbitrationAction(str, Enum):
    PRESERVE_SAFETY_PRIORITY = "PRESERVE_SAFETY_PRIORITY"
    PRIORITIZE_CAPITAL_PROTECTION = "PRIORITIZE_CAPITAL_PROTECTION"
    REDUCE_AUTONOMY = "REDUCE_AUTONOMY"
    ESCALATE_TO_EXECUTIVE_CONTROL = "ESCALATE_TO_EXECUTIVE_CONTROL"
    BLOCK_NON_CRITICAL_ACTIONS = "BLOCK_NON_CRITICAL_ACTIONS"
    ACTIVATE_SAFE_MODE = "ACTIVATE_SAFE_MODE"
    FREEZE_HIGH_RISK_OPERATIONS = "FREEZE_HIGH_RISK_OPERATIONS"
    REQUIRE_HUMAN_SUPERVISION = "REQUIRE_HUMAN_SUPERVISION"
    LOCK_PRIORITY_SYSTEM = "LOCK_PRIORITY_SYSTEM"
    CONTINUE_WITH_CONSTRAINTS = "CONTINUE_WITH_CONSTRAINTS"


class PriorityArbitrationRecommendation(str, Enum):
    MAINTAIN_SAFETY_DOMINANCE = "MAINTAIN_SAFETY_DOMINANCE"
    RECHECK_EXECUTIVE_CONTROL = "RECHECK_EXECUTIVE_CONTROL"
    REBUILD_PRIORITY_HIERARCHY = "REBUILD_PRIORITY_HIERARCHY"
    PRESERVE_RECOVERY_FLOW = "PRESERVE_RECOVERY_FLOW"
    ENFORCE_POLICY_ALIGNMENT = "ENFORCE_POLICY_ALIGNMENT"
    STABILIZE_COGNITIVE_STATE = "STABILIZE_COGNITIVE_STATE"
    REDUCE_OPERATIONAL_SCOPE = "REDUCE_OPERATIONAL_SCOPE"
    REQUIRE_MANUAL_VALIDATION = "REQUIRE_MANUAL_VALIDATION"
    MAINTAIN_SAFE_MODE = "MAINTAIN_SAFE_MODE"
    CONTINUE_PRIORITY_MONITORING = "CONTINUE_PRIORITY_MONITORING"


@dataclass(frozen=True)
class PriorityArbitrationEvent:
    name: str
    detail: str
    severity: str = "INFO"


@dataclass(frozen=True)
class PriorityArbitrationScore:
    safety_priority_score: int = 90
    stability_priority_score: int = 80
    continuity_priority_score: int = 80
    mission_priority_score: int = 80
    capital_preservation_score: int = 90
    recovery_priority_score: int = 80
    coherence_priority_score: int = 80
    alignment_priority_score: int = 80
    policy_priority_score: int = 80
    executive_control_score: int = 80
    overall_priority_score: int = 80


@dataclass(frozen=True)
class CognitivePriority:
    name: str
    rank: int
    weight: int
    score: int
    locked: bool = False
    reason: str = ""


@dataclass(frozen=True)
class PriorityConflict:
    conflict_id: str
    higher_priority: str
    lower_priority: str
    risk: PriorityArbitrationRisk
    severity_score: int
    reason: str


@dataclass(frozen=True)
class PriorityResolution:
    conflict_id: str
    winning_priority: str
    action: PriorityArbitrationAction
    reason: str
    resolved: bool = True


@dataclass(frozen=True)
class PriorityHierarchy:
    priorities: tuple[CognitivePriority, ...] = ()
    dominant_priority: str = "safety"
    locked_priorities: tuple[str, ...] = ()
    safety_dominant: bool = True
    capital_protection_dominant: bool = True


@dataclass(frozen=True)
class ArbitrationDecisionMatrix:
    hierarchy: PriorityHierarchy = field(default_factory=PriorityHierarchy)
    conflicts: tuple[PriorityConflict, ...] = ()
    resolutions: tuple[PriorityResolution, ...] = ()
    allowed_actions: tuple[str, ...] = ()
    blocked_actions: tuple[str, ...] = ()
    safe_mode_required: bool = False
    executive_override_active: bool = False
    locked: bool = False


@dataclass(frozen=True)
class CognitivePriorityArbitrationInput:
    cognitive_executive_control: Optional[CognitiveExecutiveControlResult] = None
    cognitive_memory_consolidation: Optional[CognitiveMemoryConsolidationResult] = None
    cognitive_consensus: Optional[CognitiveConsensusResult] = None
    cognitive_coherence: Optional[CognitiveCoherenceResult] = None
    cognitive_alignment: Optional[CognitiveAlignmentResult] = None
    intent_integrity: Optional[IntentIntegrityResult] = None
    cognitive_identity: Optional[CognitiveIdentityResult] = None
    cognitive_continuity: Optional[CognitiveContinuityResult] = None
    cognitive_recovery: Optional[CognitiveRecoveryResult] = None
    cognitive_resilience: Optional[CognitiveResilienceResult] = None
    cognitive_stability: Optional[CognitiveStabilityResult] = None
    cognitive_policy: Optional[CognitivePolicyResult] = None
    cognitive_governance: Optional[CognitiveGovernanceResult] = None
    self_reflection_audit: Optional[SelfReflectionAuditResult] = None
    recursive_world_model: Optional[RecursiveWorldModelResult] = None
    system_integrity: Optional[SystemIntegrityResult] = None
    mission_continuity: Optional[MissionContinuityResult] = None
    requested_priority: str = "performance"


@dataclass(frozen=True)
class CognitivePriorityArbitrationResult:
    state: PriorityArbitrationState
    mode: PriorityArbitrationMode
    priority_arbitration_score: int
    score_breakdown: PriorityArbitrationScore
    hierarchy: PriorityHierarchy = field(default_factory=PriorityHierarchy)
    conflicts: tuple[PriorityConflict, ...] = ()
    resolutions: tuple[PriorityResolution, ...] = ()
    decision_matrix: ArbitrationDecisionMatrix = field(default_factory=ArbitrationDecisionMatrix)
    risks: tuple[PriorityArbitrationRisk, ...] = ()
    actions: tuple[PriorityArbitrationAction, ...] = ()
    recommendations: tuple[PriorityArbitrationRecommendation, ...] = ()
    events: tuple[PriorityArbitrationEvent, ...] = ()
    summary: str = ""
