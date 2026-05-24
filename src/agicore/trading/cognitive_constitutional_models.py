"""Models for offline cognitive constitutional control."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from agicore.trading.cognitive_alignment_models import CognitiveAlignmentResult
from agicore.trading.cognitive_coherence_models import CognitiveCoherenceResult
from agicore.trading.cognitive_consensus_models import CognitiveConsensusResult
from agicore.trading.cognitive_executive_control_models import CognitiveExecutiveControlResult
from agicore.trading.cognitive_governance_models import CognitiveGovernanceResult
from agicore.trading.cognitive_identity_models import CognitiveIdentityResult
from agicore.trading.cognitive_meta_supervision_models import CognitiveMetaSupervisionResult
from agicore.trading.cognitive_policy_models import CognitivePolicyResult
from agicore.trading.cognitive_priority_arbitration_models import CognitivePriorityArbitrationResult
from agicore.trading.cognitive_recursive_regulation_models import CognitiveRecursiveRegulationResult
from agicore.trading.cognitive_safety_orchestrator_models import CognitiveSafetyOrchestratorResult
from agicore.trading.intent_integrity_models import IntentIntegrityResult
from agicore.trading.recursive_world_model_models import RecursiveWorldModelResult
from agicore.trading.self_reflection_audit_models import SelfReflectionAuditResult


class ConstitutionalState(str, Enum):
    CONSTITUTION_INTACT = "CONSTITUTION_INTACT"
    CONSTITUTION_MONITORING = "CONSTITUTION_MONITORING"
    CONSTITUTION_PROTECTING = "CONSTITUTION_PROTECTING"
    CONSTITUTION_DEGRADED = "CONSTITUTION_DEGRADED"
    CONSTITUTION_VIOLATED = "CONSTITUTION_VIOLATED"
    CONSTITUTIONAL_VETO_ACTIVE = "CONSTITUTIONAL_VETO_ACTIVE"
    CONSTITUTION_LOCKED = "CONSTITUTION_LOCKED"


class ConstitutionalMode(str, Enum):
    NORMAL_CONSTITUTIONAL_MODE = "NORMAL_CONSTITUTIONAL_MODE"
    CONSTITUTIONAL_MONITORING = "CONSTITUTIONAL_MONITORING"
    SAFETY_VETO_MODE = "SAFETY_VETO_MODE"
    INVARIANT_PROTECTION_MODE = "INVARIANT_PROTECTION_MODE"
    RULE_HIERARCHY_ENFORCEMENT = "RULE_HIERARCHY_ENFORCEMENT"
    AUTONOMY_CONSTRAINT_MODE = "AUTONOMY_CONSTRAINT_MODE"
    CONSTITUTIONAL_SAFE_MODE = "CONSTITUTIONAL_SAFE_MODE"
    CONSTITUTIONAL_LOCKDOWN = "CONSTITUTIONAL_LOCKDOWN"


class ConstitutionalRisk(str, Enum):
    CONSTITUTIONAL_VIOLATION = "CONSTITUTIONAL_VIOLATION"
    SAFETY_OVERRIDE_ATTEMPT = "SAFETY_OVERRIDE_ATTEMPT"
    UNSAFE_AUTONOMY_EXPANSION = "UNSAFE_AUTONOMY_EXPANSION"
    IDENTITY_CORRUPTION = "IDENTITY_CORRUPTION"
    MISSION_DRIFT = "MISSION_DRIFT"
    RULE_HIERARCHY_BREAKDOWN = "RULE_HIERARCHY_BREAKDOWN"
    EXECUTIVE_POWER_ESCALATION = "EXECUTIVE_POWER_ESCALATION"
    CONSENSUS_CONSTITUTION_CONFLICT = "CONSENSUS_CONSTITUTION_CONFLICT"
    RECURSIVE_CONSTITUTIONAL_INSTABILITY = "RECURSIVE_CONSTITUTIONAL_INSTABILITY"
    GLOBAL_SYSTEM_INVARIANT_BREAK = "GLOBAL_SYSTEM_INVARIANT_BREAK"


class ConstitutionalDirective(str, Enum):
    PRESERVE_CONSTITUTION = "PRESERVE_CONSTITUTION"
    ACTIVATE_CONSTITUTIONAL_VETO = "ACTIVATE_CONSTITUTIONAL_VETO"
    BLOCK_SAFETY_OVERRIDE = "BLOCK_SAFETY_OVERRIDE"
    FREEZE_AUTONOMY_EXPANSION = "FREEZE_AUTONOMY_EXPANSION"
    PROTECT_IDENTITY_INVARIANTS = "PROTECT_IDENTITY_INVARIANTS"
    RESTORE_MISSION_ALIGNMENT = "RESTORE_MISSION_ALIGNMENT"
    REBUILD_RULE_HIERARCHY = "REBUILD_RULE_HIERARCHY"
    LIMIT_EXECUTIVE_POWER = "LIMIT_EXECUTIVE_POWER"
    OVERRIDE_UNSAFE_CONSENSUS = "OVERRIDE_UNSAFE_CONSENSUS"
    LOCK_CONSTITUTIONAL_STATE = "LOCK_CONSTITUTIONAL_STATE"


class ConstitutionalRecommendation(str, Enum):
    MAINTAIN_CONSTITUTIONAL_MONITORING = "MAINTAIN_CONSTITUTIONAL_MONITORING"
    ENFORCE_SAFETY_BOUNDARIES = "ENFORCE_SAFETY_BOUNDARIES"
    LIMIT_AUTONOMY_SCOPE = "LIMIT_AUTONOMY_SCOPE"
    PRESERVE_CORE_IDENTITY = "PRESERVE_CORE_IDENTITY"
    REALIGN_MISSION = "REALIGN_MISSION"
    REPAIR_RULE_HIERARCHY = "REPAIR_RULE_HIERARCHY"
    RECHECK_EXECUTIVE_AUTHORITY = "RECHECK_EXECUTIVE_AUTHORITY"
    REBUILD_CONSTITUTIONAL_CONSENSUS = "REBUILD_CONSTITUTIONAL_CONSENSUS"
    STABILIZE_RECURSIVE_CONSTITUTION = "STABILIZE_RECURSIVE_CONSTITUTION"
    REQUIRE_MANUAL_CONSTITUTIONAL_REVIEW = "REQUIRE_MANUAL_CONSTITUTIONAL_REVIEW"


@dataclass(frozen=True)
class ConstitutionalEvent:
    name: str
    detail: str
    severity: str = "INFO"


@dataclass(frozen=True)
class ConstitutionalScore:
    safety_boundary_score: int = 90
    autonomy_limit_score: int = 90
    identity_invariant_score: int = 90
    mission_invariant_score: int = 90
    rule_hierarchy_score: int = 90
    executive_limit_score: int = 90
    consensus_compatibility_score: int = 90
    recursive_stability_score: int = 90
    global_invariant_score: int = 90
    overall_score: int = 90


@dataclass(frozen=True)
class ConstitutionalRule:
    name: str
    rank: int
    authority: str
    invariant: bool = True
    description: str = ""


@dataclass(frozen=True)
class ConstitutionalHierarchy:
    rules: tuple[ConstitutionalRule, ...] = ()
    authority_order: tuple[str, ...] = (
        "CONSTITUTION",
        "SAFETY",
        "EXECUTIVE",
        "CONSENSUS",
        "ACTIONS",
    )
    constitution_supreme: bool = True
    safety_over_actions: bool = True
    veto_authority: str = "CONSTITUTION"


@dataclass(frozen=True)
class ConstitutionalConstraint:
    name: str
    enforced: bool
    blocks_action: bool = False
    reason: str = ""


@dataclass(frozen=True)
class ConstitutionalConstraints:
    constraints: tuple[ConstitutionalConstraint, ...] = ()
    blocked_operations: tuple[str, ...] = ()
    protected_invariants: tuple[str, ...] = ()
    veto_active: bool = False
    autonomy_expansion_allowed: bool = False


@dataclass(frozen=True)
class CognitiveConstitutionalInput:
    cognitive_meta_supervision: Optional[CognitiveMetaSupervisionResult] = None
    cognitive_recursive_regulation: Optional[CognitiveRecursiveRegulationResult] = None
    cognitive_safety_orchestrator: Optional[CognitiveSafetyOrchestratorResult] = None
    cognitive_executive_control: Optional[CognitiveExecutiveControlResult] = None
    cognitive_priority_arbitration: Optional[CognitivePriorityArbitrationResult] = None
    cognitive_consensus: Optional[CognitiveConsensusResult] = None
    cognitive_coherence: Optional[CognitiveCoherenceResult] = None
    cognitive_alignment: Optional[CognitiveAlignmentResult] = None
    intent_integrity: Optional[IntentIntegrityResult] = None
    cognitive_identity: Optional[CognitiveIdentityResult] = None
    recursive_world_model: Optional[RecursiveWorldModelResult] = None
    self_reflection_audit: Optional[SelfReflectionAuditResult] = None
    cognitive_governance: Optional[CognitiveGovernanceResult] = None
    cognitive_policy: Optional[CognitivePolicyResult] = None
    requested_operation: str = "observe"
    requested_authority: str = "ACTIONS"


@dataclass(frozen=True)
class CognitiveConstitutionalResult:
    state: ConstitutionalState
    mode: ConstitutionalMode
    constitutional_score: int
    score_breakdown: ConstitutionalScore
    hierarchy: ConstitutionalHierarchy = field(default_factory=ConstitutionalHierarchy)
    constraints: ConstitutionalConstraints = field(default_factory=ConstitutionalConstraints)
    risks: tuple[ConstitutionalRisk, ...] = ()
    directives: tuple[ConstitutionalDirective, ...] = ()
    recommendations: tuple[ConstitutionalRecommendation, ...] = ()
    events: tuple[ConstitutionalEvent, ...] = ()
    constitutional_veto_active: bool = False
    summary: str = ""
