"""Models for offline cognitive meta-supervision."""

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
from agicore.trading.cognitive_safety_orchestrator_models import CognitiveSafetyOrchestratorResult
from agicore.trading.cognitive_stability_models import CognitiveStabilityResult
from agicore.trading.intent_integrity_models import IntentIntegrityResult
from agicore.trading.recursive_world_model_models import RecursiveWorldModelResult
from agicore.trading.self_reflection_audit_models import SelfReflectionAuditResult


class MetaSupervisionState(str, Enum):
    META_SUPERVISION_STABLE = "META_SUPERVISION_STABLE"
    META_SUPERVISION_MONITORING = "META_SUPERVISION_MONITORING"
    META_SUPERVISION_DEGRADED = "META_SUPERVISION_DEGRADED"
    META_SUPERVISION_FRAGMENTED = "META_SUPERVISION_FRAGMENTED"
    META_SUPERVISION_CRITICAL = "META_SUPERVISION_CRITICAL"
    META_SUPERVISION_LOCKDOWN = "META_SUPERVISION_LOCKDOWN"
    META_SUPERVISION_RECOVERING = "META_SUPERVISION_RECOVERING"


class MetaSupervisionMode(str, Enum):
    NORMAL_META_SUPERVISION = "NORMAL_META_SUPERVISION"
    GLOBAL_MONITORING = "GLOBAL_MONITORING"
    DRIFT_DETECTION = "DRIFT_DETECTION"
    EMERGENT_BEHAVIOR_WATCH = "EMERGENT_BEHAVIOR_WATCH"
    RECURSIVE_STABILITY_MODE = "RECURSIVE_STABILITY_MODE"
    SAFETY_OVERRIDE_MONITORING = "SAFETY_OVERRIDE_MONITORING"
    MACRO_RECOVERY_MODE = "MACRO_RECOVERY_MODE"
    META_LOCKDOWN_MODE = "META_LOCKDOWN_MODE"


class MetaSupervisionRisk(str, Enum):
    RECURSIVE_INSTABILITY = "RECURSIVE_INSTABILITY"
    META_COGNITIVE_COLLAPSE = "META_COGNITIVE_COLLAPSE"
    SYSTEM_FRAGMENTATION = "SYSTEM_FRAGMENTATION"
    UNSAFE_AUTONOMY_ESCALATION = "UNSAFE_AUTONOMY_ESCALATION"
    WORLD_MODEL_DRIFT = "WORLD_MODEL_DRIFT"
    EXECUTIVE_DEADLOCK = "EXECUTIVE_DEADLOCK"
    CONSENSUS_BREAKDOWN = "CONSENSUS_BREAKDOWN"
    SAFETY_BYPASS_ATTEMPT = "SAFETY_BYPASS_ATTEMPT"
    IDENTITY_DISSOLUTION = "IDENTITY_DISSOLUTION"
    EMERGENT_BEHAVIOR_RISK = "EMERGENT_BEHAVIOR_RISK"


class MetaSupervisionDirective(str, Enum):
    CONTINUE_META_MONITORING = "CONTINUE_META_MONITORING"
    REDUCE_RECURSIVE_DEPTH = "REDUCE_RECURSIVE_DEPTH"
    FREEZE_AUTONOMY_EXPANSION = "FREEZE_AUTONOMY_EXPANSION"
    REBUILD_GLOBAL_COHERENCE = "REBUILD_GLOBAL_COHERENCE"
    REBUILD_CONSENSUS_LAYER = "REBUILD_CONSENSUS_LAYER"
    PROTECT_IDENTITY_AND_INTENT = "PROTECT_IDENTITY_AND_INTENT"
    RECHECK_WORLD_MODEL = "RECHECK_WORLD_MODEL"
    ENFORCE_SAFETY_ORCHESTRATOR = "ENFORCE_SAFETY_ORCHESTRATOR"
    REQUIRE_HUMAN_SUPERVISION = "REQUIRE_HUMAN_SUPERVISION"
    ENTER_META_LOCKDOWN = "ENTER_META_LOCKDOWN"


class MetaSupervisionRecommendation(str, Enum):
    MAINTAIN_GLOBAL_OBSERVATION = "MAINTAIN_GLOBAL_OBSERVATION"
    STABILIZE_RECURSIVE_ENGINES = "STABILIZE_RECURSIVE_ENGINES"
    REPAIR_SYSTEM_FRAGMENTATION = "REPAIR_SYSTEM_FRAGMENTATION"
    LIMIT_AUTONOMY_SCOPE = "LIMIT_AUTONOMY_SCOPE"
    REALIGN_WORLD_MODEL = "REALIGN_WORLD_MODEL"
    UNBLOCK_EXECUTIVE_CONTROL = "UNBLOCK_EXECUTIVE_CONTROL"
    REBUILD_COLLECTIVE_CONSENSUS = "REBUILD_COLLECTIVE_CONSENSUS"
    INVESTIGATE_SAFETY_BYPASS = "INVESTIGATE_SAFETY_BYPASS"
    RESTORE_IDENTITY_ANCHORS = "RESTORE_IDENTITY_ANCHORS"
    REVIEW_EMERGENT_BEHAVIOR = "REVIEW_EMERGENT_BEHAVIOR"


@dataclass(frozen=True)
class MetaSupervisionEvent:
    name: str
    detail: str
    severity: str = "INFO"


@dataclass(frozen=True)
class MetaSupervisionScore:
    safety_score: int = 80
    executive_score: int = 80
    priority_score: int = 80
    consensus_score: int = 80
    coherence_score: int = 80
    alignment_score: int = 80
    memory_score: int = 80
    identity_score: int = 80
    continuity_score: int = 80
    recovery_score: int = 80
    resilience_score: int = 80
    stability_score: int = 80
    policy_governance_score: int = 80
    reflection_score: int = 80
    world_model_score: int = 80
    global_score: int = 80


@dataclass(frozen=True)
class MetaSupervisionNode:
    name: str
    score: int
    state: str = ""
    critical: bool = False


@dataclass(frozen=True)
class MetaSupervisionGraph:
    nodes: tuple[MetaSupervisionNode, ...] = ()
    edges: tuple[tuple[str, str, str], ...] = ()
    critical_nodes: tuple[str, ...] = ()
    fragmented_nodes: tuple[str, ...] = ()
    safety_overrides: tuple[str, ...] = ()
    recursive_links: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class GlobalCognitiveState:
    macro_state: str
    dominant_risks: tuple[MetaSupervisionRisk, ...] = ()
    stable_engines: tuple[str, ...] = ()
    degraded_engines: tuple[str, ...] = ()
    critical_engines: tuple[str, ...] = ()
    autonomy_allowed: bool = True
    safety_enforced: bool = False
    supervision_required: bool = False


@dataclass(frozen=True)
class CognitiveMetaSupervisionInput:
    cognitive_safety_orchestrator: Optional[CognitiveSafetyOrchestratorResult] = None
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
    requested_operation: str = "observe"


@dataclass(frozen=True)
class CognitiveMetaSupervisionResult:
    state: MetaSupervisionState
    mode: MetaSupervisionMode
    meta_supervision_score: int
    score_breakdown: MetaSupervisionScore
    graph: MetaSupervisionGraph = field(default_factory=MetaSupervisionGraph)
    global_state: GlobalCognitiveState = field(
        default_factory=lambda: GlobalCognitiveState(macro_state="UNKNOWN")
    )
    risks: tuple[MetaSupervisionRisk, ...] = ()
    directives: tuple[MetaSupervisionDirective, ...] = ()
    recommendations: tuple[MetaSupervisionRecommendation, ...] = ()
    events: tuple[MetaSupervisionEvent, ...] = ()
    summary: str = ""
