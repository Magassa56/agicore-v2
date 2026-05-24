"""Models for offline cognitive executive control."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from agicore.trading.cognitive_alignment_models import CognitiveAlignmentResult
from agicore.trading.cognitive_coherence_models import CognitiveCoherenceResult
from agicore.trading.cognitive_consensus_models import CognitiveConsensusResult
from agicore.trading.cognitive_continuity_models import CognitiveContinuityResult
from agicore.trading.cognitive_governance_models import CognitiveGovernanceResult
from agicore.trading.cognitive_identity_models import CognitiveIdentityResult
from agicore.trading.cognitive_memory_consolidation_models import CognitiveMemoryConsolidationResult
from agicore.trading.cognitive_policy_models import CognitivePolicyResult
from agicore.trading.cognitive_recovery_models import CognitiveRecoveryResult
from agicore.trading.cognitive_resilience_models import CognitiveResilienceResult
from agicore.trading.cognitive_stability_models import CognitiveStabilityResult
from agicore.trading.global_orchestrator_models import GlobalOrchestratorResult
from agicore.trading.intent_integrity_models import IntentIntegrityResult
from agicore.trading.mission_continuity_models import MissionContinuityResult
from agicore.trading.recursive_world_model_models import RecursiveWorldModelResult
from agicore.trading.self_reflection_audit_models import SelfReflectionAuditResult
from agicore.trading.system_integrity_models import SystemIntegrityResult


class ExecutiveControlState(str, Enum):
    EXECUTIVE_CONTROL_STABLE = "EXECUTIVE_CONTROL_STABLE"
    EXECUTIVE_CONTROL_WATCH = "EXECUTIVE_CONTROL_WATCH"
    EXECUTIVE_CONTROL_RESTRICTED = "EXECUTIVE_CONTROL_RESTRICTED"
    EXECUTIVE_CONTROL_DEGRADED = "EXECUTIVE_CONTROL_DEGRADED"
    EXECUTIVE_CONTROL_CRITICAL = "EXECUTIVE_CONTROL_CRITICAL"
    EXECUTIVE_CONTROL_LOCKED = "EXECUTIVE_CONTROL_LOCKED"
    EXECUTIVE_CONTROL_RECOVERING = "EXECUTIVE_CONTROL_RECOVERING"


class ExecutiveControlMode(str, Enum):
    NORMAL_EXECUTIVE_CONTROL = "NORMAL_EXECUTIVE_CONTROL"
    MONITORING_CONTROL = "MONITORING_CONTROL"
    RESTRICTED_CONTROL = "RESTRICTED_CONTROL"
    SAFE_CONTROL_MODE = "SAFE_CONTROL_MODE"
    SUPERVISED_CONTROL = "SUPERVISED_CONTROL"
    RECOVERY_CONTROL = "RECOVERY_CONTROL"
    EMERGENCY_CONTROL = "EMERGENCY_CONTROL"
    LOCKED_CONTROL = "LOCKED_CONTROL"


class ExecutiveControlRisk(str, Enum):
    EXECUTIVE_OVERRIDE_REQUIRED = "EXECUTIVE_OVERRIDE_REQUIRED"
    AUTONOMY_TOO_HIGH = "AUTONOMY_TOO_HIGH"
    POLICY_BLOCK_REQUIRED = "POLICY_BLOCK_REQUIRED"
    ALIGNMENT_FAILURE = "ALIGNMENT_FAILURE"
    COHERENCE_FAILURE = "COHERENCE_FAILURE"
    CONSENSUS_FAILURE = "CONSENSUS_FAILURE"
    MEMORY_FAILURE = "MEMORY_FAILURE"
    INTENT_FAILURE = "INTENT_FAILURE"
    RECOVERY_INCOMPLETE = "RECOVERY_INCOMPLETE"
    SYSTEMIC_CONTROL_COLLAPSE = "SYSTEMIC_CONTROL_COLLAPSE"


class ExecutiveControlAction(str, Enum):
    ALLOW_CONTINUE = "ALLOW_CONTINUE"
    ALLOW_WITH_LIMITS = "ALLOW_WITH_LIMITS"
    REDUCE_AUTONOMY = "REDUCE_AUTONOMY"
    BLOCK_ACTION = "BLOCK_ACTION"
    REQUIRE_SUPERVISION = "REQUIRE_SUPERVISION"
    ENTER_SAFE_MODE = "ENTER_SAFE_MODE"
    FREEZE_LEARNING = "FREEZE_LEARNING"
    FREEZE_RECURSIVE_UPDATES = "FREEZE_RECURSIVE_UPDATES"
    LOCK_EXECUTIVE_CONTROL = "LOCK_EXECUTIVE_CONTROL"
    ESCALATE_TO_HUMAN = "ESCALATE_TO_HUMAN"


class ExecutiveControlRecommendation(str, Enum):
    CONTINUE_MONITORING = "CONTINUE_MONITORING"
    ENFORCE_POLICY_BLOCKS = "ENFORCE_POLICY_BLOCKS"
    RECHECK_ALIGNMENT = "RECHECK_ALIGNMENT"
    RECHECK_COHERENCE = "RECHECK_COHERENCE"
    REBUILD_CONSENSUS = "REBUILD_CONSENSUS"
    PROTECT_MEMORY = "PROTECT_MEMORY"
    RESTORE_INTENT_INTEGRITY = "RESTORE_INTENT_INTEGRITY"
    KEEP_RECOVERY_ACTIVE = "KEEP_RECOVERY_ACTIVE"
    REQUIRE_MANUAL_VALIDATION = "REQUIRE_MANUAL_VALIDATION"
    MAINTAIN_EXECUTIVE_LOCK = "MAINTAIN_EXECUTIVE_LOCK"


@dataclass(frozen=True)
class ExecutiveControlEvent:
    name: str
    detail: str
    severity: str = "INFO"


@dataclass(frozen=True)
class ExecutiveControlScore:
    autonomy_control_score: int = 80
    policy_control_score: int = 80
    alignment_control_score: int = 80
    coherence_control_score: int = 80
    consensus_control_score: int = 80
    memory_control_score: int = 80
    intent_control_score: int = 80
    recovery_control_score: int = 80
    systemic_control_score: int = 80


@dataclass(frozen=True)
class ExecutiveControlDirective:
    directive_id: str
    action: ExecutiveControlAction
    priority: int
    reason: str
    requires_supervision: bool = False
    blocks_execution: bool = False


@dataclass(frozen=True)
class ExecutiveControlDecisionGraph:
    nodes: tuple[str, ...] = ()
    edges: tuple[tuple[str, str, str], ...] = ()
    active_directives: tuple[ExecutiveControlDirective, ...] = ()
    blocked_nodes: tuple[str, ...] = ()
    safe_mode_required: bool = False
    locked: bool = False


@dataclass(frozen=True)
class CognitiveExecutiveControlInput:
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
    global_orchestrator: Optional[GlobalOrchestratorResult] = None
    system_integrity: Optional[SystemIntegrityResult] = None
    mission_continuity: Optional[MissionContinuityResult] = None
    requested_action: str = "continue"


@dataclass(frozen=True)
class CognitiveExecutiveControlResult:
    state: ExecutiveControlState
    mode: ExecutiveControlMode
    executive_control_score: int
    score_breakdown: ExecutiveControlScore
    directives: tuple[ExecutiveControlDirective, ...] = ()
    decision_graph: ExecutiveControlDecisionGraph = field(default_factory=ExecutiveControlDecisionGraph)
    risks: tuple[ExecutiveControlRisk, ...] = ()
    actions: tuple[ExecutiveControlAction, ...] = ()
    recommendations: tuple[ExecutiveControlRecommendation, ...] = ()
    events: tuple[ExecutiveControlEvent, ...] = ()
    summary: str = ""
