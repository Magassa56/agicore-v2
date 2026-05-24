"""Models for the offline Autonomous Cognitive Governance Engine."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .cognitive_adaptation_models import CognitiveAdaptationResult
from .collective_consensus_models import ConsensusResult
from .global_orchestrator_models import GlobalOrchestratorResult
from .intent_alignment_models import IntentAlignmentResult
from .learning_governance_models import LearningGovernanceResult
from .meta_cognition_models import MetaCognitionResult
from .mission_continuity_models import MissionContinuityResult
from .operational_awareness_models import OperationalAwarenessResult
from .recovery_resilience_models import RecoveryResilienceResult
from .recursive_world_model_models import RecursiveWorldModelResult
from .self_reflection_audit_models import SelfReflectionAuditResult
from .strategic_arbitration_models import ArbitrationResult
from .system_integrity_models import SystemIntegrityResult


class CognitiveGovernanceMode(StrEnum):
    """Operating mode for cognitive governance."""

    NORMAL_GOVERNANCE = "NORMAL_GOVERNANCE"
    SUPERVISED_GOVERNANCE = "SUPERVISED_GOVERNANCE"
    RESTRICTED_GOVERNANCE = "RESTRICTED_GOVERNANCE"
    SAFE_GOVERNANCE = "SAFE_GOVERNANCE"
    DEGRADED_GOVERNANCE = "DEGRADED_GOVERNANCE"
    EMERGENCY_GOVERNANCE = "EMERGENCY_GOVERNANCE"
    LOCKED_GOVERNANCE = "LOCKED_GOVERNANCE"


class CognitiveAutonomyLevel(StrEnum):
    """Permitted cognitive autonomy level."""

    FULL_AUTONOMY = "FULL_AUTONOMY"
    LIMITED_AUTONOMY = "LIMITED_AUTONOMY"
    SUPERVISED_AUTONOMY = "SUPERVISED_AUTONOMY"
    OBSERVE_ONLY = "OBSERVE_ONLY"
    LOCKED_AUTONOMY = "LOCKED_AUTONOMY"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"


class CognitivePermission(StrEnum):
    """Cognitive permissions governed by policy."""

    ALLOW_ANALYSIS = "ALLOW_ANALYSIS"
    ALLOW_PLANNING = "ALLOW_PLANNING"
    ALLOW_FORECASTING = "ALLOW_FORECASTING"
    ALLOW_STRATEGY_EVOLUTION = "ALLOW_STRATEGY_EVOLUTION"
    ALLOW_RECURSIVE_UPDATES = "ALLOW_RECURSIVE_UPDATES"
    ALLOW_AUTONOMY_EXPANSION = "ALLOW_AUTONOMY_EXPANSION"
    ALLOW_EXECUTION_ROUTING = "ALLOW_EXECUTION_ROUTING"
    ALLOW_LEARNING_UPDATE = "ALLOW_LEARNING_UPDATE"
    DENY_HIGH_RISK_ACTIONS = "DENY_HIGH_RISK_ACTIONS"
    REQUIRE_AUDIT_TRACE = "REQUIRE_AUDIT_TRACE"


class CognitivePolicy(StrEnum):
    """Cognitive governance policies."""

    OFFLINE_ONLY_POLICY = "OFFLINE_ONLY_POLICY"
    AUDIT_TRACE_POLICY = "AUDIT_TRACE_POLICY"
    SAFETY_FIRST_POLICY = "SAFETY_FIRST_POLICY"
    AUTONOMY_LIMIT_POLICY = "AUTONOMY_LIMIT_POLICY"
    RECURSIVE_UPDATE_POLICY = "RECURSIVE_UPDATE_POLICY"
    LEARNING_UPDATE_POLICY = "LEARNING_UPDATE_POLICY"
    STRATEGY_EVOLUTION_POLICY = "STRATEGY_EVOLUTION_POLICY"
    EXECUTION_ROUTING_POLICY = "EXECUTION_ROUTING_POLICY"


class CognitiveGovernanceRisk(StrEnum):
    """Risks that can degrade cognitive governance."""

    AUTONOMY_ESCALATION_RISK = "AUTONOMY_ESCALATION_RISK"
    RECURSIVE_DRIFT_RISK = "RECURSIVE_DRIFT_RISK"
    POLICY_VIOLATION_RISK = "POLICY_VIOLATION_RISK"
    UNSAFE_PERMISSION_SET = "UNSAFE_PERMISSION_SET"
    GOVERNANCE_FRAGMENTATION = "GOVERNANCE_FRAGMENTATION"
    LOW_AUDITABILITY = "LOW_AUDITABILITY"
    META_COGNITIVE_INSTABILITY = "META_COGNITIVE_INSTABILITY"
    WORLD_MODEL_INCOHERENCE = "WORLD_MODEL_INCOHERENCE"
    SYSTEM_SAFE_MODE_REQUIRED = "SYSTEM_SAFE_MODE_REQUIRED"
    EMERGENCY_LOCK_REQUIRED = "EMERGENCY_LOCK_REQUIRED"


class CognitiveGovernanceDecision(StrEnum):
    """Final cognitive governance decision."""

    APPROVE_COGNITIVE_OPERATION = "APPROVE_COGNITIVE_OPERATION"
    APPROVE_WITH_RESTRICTIONS = "APPROVE_WITH_RESTRICTIONS"
    REDUCE_AUTONOMY_LEVEL = "REDUCE_AUTONOMY_LEVEL"
    ENFORCE_SAFE_GOVERNANCE = "ENFORCE_SAFE_GOVERNANCE"
    FREEZE_RECURSIVE_UPDATES = "FREEZE_RECURSIVE_UPDATES"
    DENY_AUTONOMY_EXPANSION = "DENY_AUTONOMY_EXPANSION"
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"
    ENTER_LOCKED_GOVERNANCE = "ENTER_LOCKED_GOVERNANCE"


class CognitiveGovernanceRecommendation(StrEnum):
    """Recommended controls emitted by cognitive governance."""

    REDUCE_AUTONOMY = "REDUCE_AUTONOMY"
    ENFORCE_AUDIT_TRACE = "ENFORCE_AUDIT_TRACE"
    FREEZE_RECURSIVE_SYSTEMS = "FREEZE_RECURSIVE_SYSTEMS"
    LIMIT_STRATEGY_EVOLUTION = "LIMIT_STRATEGY_EVOLUTION"
    REQUIRE_SUPERVISION = "REQUIRE_SUPERVISION"
    REBUILD_GOVERNANCE_POLICY = "REBUILD_GOVERNANCE_POLICY"
    PROTECT_WORLD_MODEL = "PROTECT_WORLD_MODEL"
    MAINTAIN_SAFE_GOVERNANCE = "MAINTAIN_SAFE_GOVERNANCE"
    CONTINUE_MONITORING = "CONTINUE_MONITORING"
    ENTER_EMERGENCY_LOCK = "ENTER_EMERGENCY_LOCK"


@dataclass(frozen=True)
class CognitiveGovernanceScore:
    """Governance score components normalized to 0..100."""

    autonomy_control_score: int
    auditability_score: int
    policy_compliance_score: int
    recursive_safety_score: int
    world_model_protection_score: int
    meta_cognitive_stability_score: int
    system_safety_score: int


@dataclass(frozen=True)
class CognitivePolicyEnforcement:
    """One policy enforcement result."""

    policy: CognitivePolicy
    allowed: bool
    enforced_permissions: tuple[CognitivePermission, ...]
    denied_permissions: tuple[CognitivePermission, ...]
    reason: str


@dataclass(frozen=True)
class CognitiveGovernanceInput:
    """Inputs consumed by the offline cognitive governance engine."""

    self_reflection_audit: SelfReflectionAuditResult | None = None
    recursive_world_model: RecursiveWorldModelResult | None = None
    global_orchestrator: GlobalOrchestratorResult | None = None
    meta_cognition: MetaCognitionResult | None = None
    cognitive_adaptation: CognitiveAdaptationResult | None = None
    system_integrity: SystemIntegrityResult | None = None
    intent_alignment: IntentAlignmentResult | None = None
    strategic_arbitration: ArbitrationResult | None = None
    collective_consensus: ConsensusResult | None = None
    learning_governance: LearningGovernanceResult | None = None
    recovery_resilience: RecoveryResilienceResult | None = None
    mission_continuity: MissionContinuityResult | None = None
    operational_awareness: OperationalAwarenessResult | None = None


@dataclass(frozen=True)
class CognitiveGovernanceEvent:
    """Auditable cognitive governance event."""

    mode: CognitiveGovernanceMode
    decision: CognitiveGovernanceDecision
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class CognitiveGovernanceResult:
    """Final cognitive governance result."""

    mode: CognitiveGovernanceMode
    autonomy_level: CognitiveAutonomyLevel
    decision: CognitiveGovernanceDecision
    permissions: tuple[CognitivePermission, ...]
    denied_permissions: tuple[CognitivePermission, ...]
    policy_enforcements: tuple[CognitivePolicyEnforcement, ...]
    risks: tuple[CognitiveGovernanceRisk, ...]
    governance_score: int
    score_breakdown: CognitiveGovernanceScore
    recommendations: tuple[CognitiveGovernanceRecommendation, ...]
    events: tuple[CognitiveGovernanceEvent, ...]
    summary: str


__all__ = [
    "CognitiveAutonomyLevel",
    "CognitiveGovernanceDecision",
    "CognitiveGovernanceEvent",
    "CognitiveGovernanceInput",
    "CognitiveGovernanceMode",
    "CognitiveGovernanceRecommendation",
    "CognitiveGovernanceResult",
    "CognitiveGovernanceRisk",
    "CognitiveGovernanceScore",
    "CognitivePermission",
    "CognitivePolicy",
    "CognitivePolicyEnforcement",
]
