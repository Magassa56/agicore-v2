"""Models for offline cognitive safety orchestration."""

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
from agicore.trading.cognitive_priority_arbitration_models import CognitivePriorityArbitrationResult
from agicore.trading.cognitive_recovery_models import CognitiveRecoveryResult
from agicore.trading.cognitive_resilience_models import CognitiveResilienceResult
from agicore.trading.cognitive_stability_models import CognitiveStabilityResult
from agicore.trading.intent_integrity_models import IntentIntegrityResult
from agicore.trading.mission_continuity_models import MissionContinuityResult
from agicore.trading.recursive_world_model_models import RecursiveWorldModelResult
from agicore.trading.self_reflection_audit_models import SelfReflectionAuditResult
from agicore.trading.system_integrity_models import SystemIntegrityResult


class SafetyOrchestratorState(str, Enum):
    SAFETY_ORCHESTRATOR_STABLE = "SAFETY_ORCHESTRATOR_STABLE"
    SAFETY_ORCHESTRATOR_MONITORING = "SAFETY_ORCHESTRATOR_MONITORING"
    SAFETY_ORCHESTRATOR_PROTECTING = "SAFETY_ORCHESTRATOR_PROTECTING"
    SAFETY_ORCHESTRATOR_DEGRADED = "SAFETY_ORCHESTRATOR_DEGRADED"
    SAFETY_ORCHESTRATOR_CRITICAL = "SAFETY_ORCHESTRATOR_CRITICAL"
    SAFETY_ORCHESTRATOR_LOCKDOWN = "SAFETY_ORCHESTRATOR_LOCKDOWN"
    SAFETY_ORCHESTRATOR_RECOVERING = "SAFETY_ORCHESTRATOR_RECOVERING"


class SafetyOrchestratorMode(str, Enum):
    NORMAL_SAFETY_MODE = "NORMAL_SAFETY_MODE"
    PROTECTIVE_MODE = "PROTECTIVE_MODE"
    SAFE_MODE_COORDINATION = "SAFE_MODE_COORDINATION"
    RECOVERY_PROTECTION_MODE = "RECOVERY_PROTECTION_MODE"
    EXECUTIVE_SAFETY_MODE = "EXECUTIVE_SAFETY_MODE"
    CASCADE_PREVENTION_MODE = "CASCADE_PREVENTION_MODE"
    EMERGENCY_LOCKDOWN_MODE = "EMERGENCY_LOCKDOWN_MODE"
    FULL_SAFETY_LOCK_MODE = "FULL_SAFETY_LOCK_MODE"


class SafetyOrchestratorRisk(str, Enum):
    SYSTEMIC_CASCADE_RISK = "SYSTEMIC_CASCADE_RISK"
    EXECUTIVE_CONTROL_FAILURE = "EXECUTIVE_CONTROL_FAILURE"
    PRIORITY_ARBITRATION_FAILURE = "PRIORITY_ARBITRATION_FAILURE"
    ALIGNMENT_BREAKDOWN = "ALIGNMENT_BREAKDOWN"
    COHERENCE_COLLAPSE = "COHERENCE_COLLAPSE"
    MEMORY_CORRUPTION_SPREAD = "MEMORY_CORRUPTION_SPREAD"
    RECOVERY_FAILURE = "RECOVERY_FAILURE"
    POLICY_GOVERNANCE_DRIFT = "POLICY_GOVERNANCE_DRIFT"
    UNSAFE_AUTONOMOUS_ACTION = "UNSAFE_AUTONOMOUS_ACTION"
    GLOBAL_SAFETY_COLLAPSE = "GLOBAL_SAFETY_COLLAPSE"


class SafetyOrchestratorAction(str, Enum):
    ACTIVATE_GLOBAL_SAFE_MODE = "ACTIVATE_GLOBAL_SAFE_MODE"
    FREEZE_AUTONOMOUS_OPERATIONS = "FREEZE_AUTONOMOUS_OPERATIONS"
    REDUCE_SYSTEM_SCOPE = "REDUCE_SYSTEM_SCOPE"
    PROTECT_MEMORY_SYSTEM = "PROTECT_MEMORY_SYSTEM"
    ENFORCE_EXECUTIVE_LOCK = "ENFORCE_EXECUTIVE_LOCK"
    BLOCK_HIGH_RISK_DECISIONS = "BLOCK_HIGH_RISK_DECISIONS"
    MAINTAIN_RECOVERY_PIPELINE = "MAINTAIN_RECOVERY_PIPELINE"
    REQUIRE_HUMAN_SUPERVISION = "REQUIRE_HUMAN_SUPERVISION"
    ISOLATE_UNSAFE_COMPONENTS = "ISOLATE_UNSAFE_COMPONENTS"
    LOCKDOWN_SYSTEM = "LOCKDOWN_SYSTEM"


class SafetyOrchestratorRecommendation(str, Enum):
    MAINTAIN_SAFETY_COORDINATION = "MAINTAIN_SAFETY_COORDINATION"
    RECHECK_EXECUTIVE_CONTROL = "RECHECK_EXECUTIVE_CONTROL"
    REBUILD_ALIGNMENT = "REBUILD_ALIGNMENT"
    STABILIZE_COGNITIVE_STATE = "STABILIZE_COGNITIVE_STATE"
    ENFORCE_POLICY_CONSISTENCY = "ENFORCE_POLICY_CONSISTENCY"
    PRESERVE_MEMORY_INTEGRITY = "PRESERVE_MEMORY_INTEGRITY"
    MAINTAIN_RECOVERY_OPERATIONS = "MAINTAIN_RECOVERY_OPERATIONS"
    REDUCE_AUTONOMY_SCOPE = "REDUCE_AUTONOMY_SCOPE"
    REQUIRE_MANUAL_APPROVAL = "REQUIRE_MANUAL_APPROVAL"
    KEEP_LOCKDOWN_ACTIVE = "KEEP_LOCKDOWN_ACTIVE"


@dataclass(frozen=True)
class SafetyOrchestratorEvent:
    name: str
    detail: str
    severity: str = "INFO"


@dataclass(frozen=True)
class SafetyOrchestratorScore:
    executive_safety_score: int = 80
    priority_safety_score: int = 80
    policy_governance_score: int = 80
    recovery_resilience_score: int = 80
    coherence_alignment_score: int = 80
    consensus_score: int = 80
    continuity_score: int = 80
    intent_safety_score: int = 80
    memory_safety_score: int = 80
    world_model_safety_score: int = 80
    overall_safety_score: int = 80


@dataclass(frozen=True)
class SafetyDirective:
    directive_id: str
    action: SafetyOrchestratorAction
    priority: int
    reason: str
    blocks_autonomy: bool = False
    requires_supervision: bool = False


@dataclass(frozen=True)
class SafetyProtectionLayer:
    name: str
    active: bool
    protection_score: int
    protected_components: tuple[str, ...] = ()
    reason: str = ""


@dataclass(frozen=True)
class SafetyCascadeRisk:
    cascade_id: str
    source_layer: str
    target_layers: tuple[str, ...]
    severity_score: int
    contained: bool
    reason: str


@dataclass(frozen=True)
class SafetyCoordinationGraph:
    layers: tuple[SafetyProtectionLayer, ...] = ()
    routes: tuple[tuple[str, str, str], ...] = ()
    blocked_components: tuple[str, ...] = ()
    isolated_components: tuple[str, ...] = ()
    safe_mode_active: bool = False
    lockdown_active: bool = False


@dataclass(frozen=True)
class SafetyStabilizationPlan:
    steps: tuple[str, ...] = ()
    required_actions: tuple[SafetyOrchestratorAction, ...] = ()
    protected_memory: bool = False
    recovery_pipeline_active: bool = False
    human_supervision_required: bool = False
    lockdown_required: bool = False


@dataclass(frozen=True)
class CognitiveSafetyOrchestratorInput:
    cognitive_executive_control: Optional[CognitiveExecutiveControlResult] = None
    cognitive_priority_arbitration: Optional[CognitivePriorityArbitrationResult] = None
    cognitive_consensus: Optional[CognitiveConsensusResult] = None
    cognitive_coherence: Optional[CognitiveCoherenceResult] = None
    cognitive_alignment: Optional[CognitiveAlignmentResult] = None
    cognitive_memory_consolidation: Optional[CognitiveMemoryConsolidationResult] = None
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
    requested_operation: str = "monitor"


@dataclass(frozen=True)
class CognitiveSafetyOrchestratorResult:
    state: SafetyOrchestratorState
    mode: SafetyOrchestratorMode
    safety_orchestrator_score: int
    score_breakdown: SafetyOrchestratorScore
    directives: tuple[SafetyDirective, ...] = ()
    coordination_graph: SafetyCoordinationGraph = field(default_factory=SafetyCoordinationGraph)
    cascade_risks: tuple[SafetyCascadeRisk, ...] = ()
    stabilization_plan: SafetyStabilizationPlan = field(default_factory=SafetyStabilizationPlan)
    risks: tuple[SafetyOrchestratorRisk, ...] = ()
    actions: tuple[SafetyOrchestratorAction, ...] = ()
    recommendations: tuple[SafetyOrchestratorRecommendation, ...] = ()
    events: tuple[SafetyOrchestratorEvent, ...] = ()
    summary: str = ""
