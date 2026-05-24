"""Models for the offline cognitive consensus engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from agicore.trading.cognitive_alignment_models import CognitiveAlignmentResult
from agicore.trading.cognitive_coherence_models import CognitiveCoherenceResult
from agicore.trading.cognitive_continuity_models import CognitiveContinuityResult
from agicore.trading.cognitive_governance_models import CognitiveGovernanceResult
from agicore.trading.cognitive_identity_models import CognitiveIdentityResult
from agicore.trading.cognitive_policy_models import CognitivePolicyResult
from agicore.trading.cognitive_recovery_models import CognitiveRecoveryResult
from agicore.trading.cognitive_resilience_models import CognitiveResilienceResult
from agicore.trading.cognitive_stability_models import CognitiveStabilityResult
from agicore.trading.collective_consensus_models import ConsensusResult as CollectiveConsensusResult
from agicore.trading.global_orchestrator_models import CoordinationResult
from agicore.trading.intent_integrity_models import IntentIntegrityResult
from agicore.trading.multi_timeline_simulation_models import MultiTimelineSimulationResult
from agicore.trading.recursive_world_model_models import RecursiveWorldModelResult
from agicore.trading.scenario_forecast_models import ScenarioForecastResult
from agicore.trading.self_reflection_audit_models import SelfReflectionAuditResult
from agicore.trading.strategic_arbitration_models import ArbitrationResult


class CognitiveConsensusState(str, Enum):
    CONSENSUS_REACHED = "CONSENSUS_REACHED"
    CONSENSUS_MONITORING = "CONSENSUS_MONITORING"
    PARTIAL_CONSENSUS = "PARTIAL_CONSENSUS"
    STRATEGIC_DISAGREEMENT = "STRATEGIC_DISAGREEMENT"
    CONSENSUS_FRAGMENTED = "CONSENSUS_FRAGMENTED"
    HIGH_CONFLICT_STATE = "HIGH_CONFLICT_STATE"
    SYSTEMIC_CONFLICT = "SYSTEMIC_CONFLICT"
    CONSENSUS_LOCKED = "CONSENSUS_LOCKED"


class CognitiveConsensusMode(str, Enum):
    NORMAL_CONSENSUS = "NORMAL_CONSENSUS"
    CONSENSUS_VALIDATION = "CONSENSUS_VALIDATION"
    MULTI_TIMELINE_CONSENSUS = "MULTI_TIMELINE_CONSENSUS"
    STRATEGIC_ARBITRATION = "STRATEGIC_ARBITRATION"
    SAFE_CONSENSUS_MODE = "SAFE_CONSENSUS_MODE"
    CONFLICT_RESOLUTION_MODE = "CONFLICT_RESOLUTION_MODE"
    HUMAN_SUPERVISION_MODE = "HUMAN_SUPERVISION_MODE"
    LOCKED_CONSENSUS_MODE = "LOCKED_CONSENSUS_MODE"


class CognitiveConsensusRisk(str, Enum):
    REASONING_CONFLICT = "REASONING_CONFLICT"
    TIMELINE_CONFLICT = "TIMELINE_CONFLICT"
    STRATEGIC_CONFLICT = "STRATEGIC_CONFLICT"
    WORLD_MODEL_CONFLICT = "WORLD_MODEL_CONFLICT"
    POLICY_CONFLICT = "POLICY_CONFLICT"
    ALIGNMENT_CONFLICT = "ALIGNMENT_CONFLICT"
    DECISION_DEADLOCK = "DECISION_DEADLOCK"
    CONSENSUS_FRAGMENTATION = "CONSENSUS_FRAGMENTATION"
    AUTONOMY_CONFLICT = "AUTONOMY_CONFLICT"
    SYSTEMIC_CONSENSUS_COLLAPSE = "SYSTEMIC_CONSENSUS_COLLAPSE"


class CognitiveConsensusAction(str, Enum):
    PRESERVE_CONSENSUS_STATE = "PRESERVE_CONSENSUS_STATE"
    REBUILD_CONSENSUS = "REBUILD_CONSENSUS"
    RECONCILE_REASONING = "RECONCILE_REASONING"
    RECONCILE_TIMELINES = "RECONCILE_TIMELINES"
    RECONCILE_WORLD_MODEL = "RECONCILE_WORLD_MODEL"
    REDUCE_AUTONOMY = "REDUCE_AUTONOMY"
    REQUIRE_SUPERVISION = "REQUIRE_SUPERVISION"
    FORCE_SAFE_MODE = "FORCE_SAFE_MODE"
    LOCK_CONSENSUS_STATE = "LOCK_CONSENSUS_STATE"
    ESCALATE_TO_HUMAN = "ESCALATE_TO_HUMAN"


class CognitiveConsensusRecommendation(str, Enum):
    CONTINUE_CONSENSUS_MONITORING = "CONTINUE_CONSENSUS_MONITORING"
    EXTEND_REASONING_DEBATE = "EXTEND_REASONING_DEBATE"
    RECHECK_TIMELINE_ALIGNMENT = "RECHECK_TIMELINE_ALIGNMENT"
    REBUILD_CONFLICTED_CONSENSUS = "REBUILD_CONFLICTED_CONSENSUS"
    REPAIR_WORLD_MODEL_ALIGNMENT = "REPAIR_WORLD_MODEL_ALIGNMENT"
    REDUCE_DECISION_SCOPE = "REDUCE_DECISION_SCOPE"
    ENABLE_SAFE_CONSENSUS = "ENABLE_SAFE_CONSENSUS"
    REQUIRE_MANUAL_VALIDATION = "REQUIRE_MANUAL_VALIDATION"
    PRESERVE_CONSENSUS_SNAPSHOT = "PRESERVE_CONSENSUS_SNAPSHOT"
    UPDATE_CONSENSUS_STATE = "UPDATE_CONSENSUS_STATE"


@dataclass(frozen=True)
class CognitiveConsensusEvent:
    name: str
    detail: str
    severity: str = "INFO"


@dataclass(frozen=True)
class CognitiveConsensusScore:
    reasoning_consensus_score: int = 80
    timeline_consensus_score: int = 80
    strategic_consensus_score: int = 80
    world_model_consensus_score: int = 80
    policy_consensus_score: int = 80
    alignment_consensus_score: int = 80
    decision_consensus_score: int = 80
    autonomy_consensus_score: int = 80
    systemic_consensus_score: int = 80


@dataclass(frozen=True)
class ConsensusNode:
    name: str
    source: str
    confidence_score: int
    position: str
    risk: Optional[CognitiveConsensusRisk] = None


@dataclass(frozen=True)
class ConsensusVote:
    node_name: str
    vote: str
    confidence_score: int
    reason: str
    supports_safe_mode: bool = False
    risk: Optional[CognitiveConsensusRisk] = None


@dataclass(frozen=True)
class ConsensusReasoningChain:
    name: str
    steps: tuple[str, ...] = ()
    score: int = 80
    agreed: bool = True
    conflict: Optional[str] = None


@dataclass(frozen=True)
class ConsensusScenario:
    name: str
    probability_score: int = 50
    survivability_score: int = 80
    preferred: bool = False
    conflict: Optional[str] = None


@dataclass(frozen=True)
class ConsensusMatrix:
    nodes: tuple[ConsensusNode, ...] = ()
    votes: tuple[ConsensusVote, ...] = ()
    reasoning_chains: tuple[ConsensusReasoningChain, ...] = ()
    scenarios: tuple[ConsensusScenario, ...] = ()
    global_score: int = 80
    agreement_score: int = 80
    conflict_count: int = 0
    winning_position: str = "APPROVE"
    conflict_resolutions: tuple[str, ...] = ()
    locked: bool = False
    autonomy_reduced: bool = False


@dataclass(frozen=True)
class CognitiveConsensusInput:
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
    global_orchestrator: Optional[CoordinationResult] = None
    collective_consensus: Optional[CollectiveConsensusResult] = None
    scenario_forecast: Optional[ScenarioForecastResult] = None
    multi_timeline_simulation: Optional[MultiTimelineSimulationResult] = None
    strategic_arbitration: Optional[ArbitrationResult] = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class CognitiveConsensusResult:
    state: CognitiveConsensusState
    mode: CognitiveConsensusMode
    cognitive_consensus_score: int
    score_breakdown: CognitiveConsensusScore
    nodes: tuple[ConsensusNode, ...] = ()
    votes: tuple[ConsensusVote, ...] = ()
    reasoning_chains: tuple[ConsensusReasoningChain, ...] = ()
    scenarios: tuple[ConsensusScenario, ...] = ()
    matrix: ConsensusMatrix = field(default_factory=ConsensusMatrix)
    risks: tuple[CognitiveConsensusRisk, ...] = ()
    actions: tuple[CognitiveConsensusAction, ...] = ()
    recommendations: tuple[CognitiveConsensusRecommendation, ...] = ()
    events: tuple[CognitiveConsensusEvent, ...] = ()
    summary: str = ""
