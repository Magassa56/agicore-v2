"""Models for the offline Autonomous Cognitive Coherence Engine."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .cognitive_alignment_models import CognitiveAlignmentResult
from .cognitive_continuity_models import CognitiveContinuityResult
from .cognitive_governance_models import CognitiveGovernanceResult
from .cognitive_identity_models import CognitiveIdentityResult
from .cognitive_policy_models import CognitivePolicyResult
from .cognitive_recovery_models import CognitiveRecoveryResult
from .cognitive_resilience_models import CognitiveResilienceResult
from .cognitive_stability_models import CognitiveStabilityResult
from .collective_consensus_models import ConsensusResult
from .global_orchestrator_models import GlobalOrchestratorResult
from .intent_integrity_models import IntentIntegrityResult
from .multi_timeline_simulation_models import MultiTimelineSimulationResult
from .recursive_world_model_models import RecursiveWorldModelResult
from .scenario_forecast_models import ScenarioForecastResult
from .self_reflection_audit_models import SelfReflectionAuditResult
from .strategic_arbitration_models import ArbitrationResult


class CognitiveCoherenceState(StrEnum):
    """Current cognitive coherence state."""

    COHERENT = "COHERENT"
    COHERENCE_WATCH = "COHERENCE_WATCH"
    PARTIAL_INCOHERENCE = "PARTIAL_INCOHERENCE"
    LOGICAL_CONFLICT = "LOGICAL_CONFLICT"
    STRATEGIC_INCOHERENCE = "STRATEGIC_INCOHERENCE"
    SYSTEMIC_INCOHERENCE = "SYSTEMIC_INCOHERENCE"
    COHERENCE_AT_RISK = "COHERENCE_AT_RISK"
    COHERENCE_LOCKED = "COHERENCE_LOCKED"


class CognitiveCoherenceMode(StrEnum):
    """Operating mode for cognitive coherence."""

    NORMAL_COHERENCE = "NORMAL_COHERENCE"
    COHERENCE_MONITORING = "COHERENCE_MONITORING"
    LOGICAL_VALIDATION = "LOGICAL_VALIDATION"
    STRATEGIC_VALIDATION = "STRATEGIC_VALIDATION"
    WORLD_MODEL_VALIDATION = "WORLD_MODEL_VALIDATION"
    TIMELINE_VALIDATION = "TIMELINE_VALIDATION"
    SAFE_COHERENCE_MODE = "SAFE_COHERENCE_MODE"
    LOCKED_COHERENCE_MODE = "LOCKED_COHERENCE_MODE"


class CognitiveCoherenceRisk(StrEnum):
    """Risks that can break cognitive coherence."""

    LOGICAL_CONTRADICTION = "LOGICAL_CONTRADICTION"
    REASONING_CHAIN_BREAK = "REASONING_CHAIN_BREAK"
    DECISION_SEQUENCE_CONFLICT = "DECISION_SEQUENCE_CONFLICT"
    WORLD_MODEL_ACTION_MISMATCH = "WORLD_MODEL_ACTION_MISMATCH"
    TIMELINE_FORECAST_CONFLICT = "TIMELINE_FORECAST_CONFLICT"
    POLICY_REASONING_CONFLICT = "POLICY_REASONING_CONFLICT"
    ALIGNMENT_COHERENCE_BREAK = "ALIGNMENT_COHERENCE_BREAK"
    CONSENSUS_COHERENCE_BREAK = "CONSENSUS_COHERENCE_BREAK"
    STRATEGIC_CONCLUSION_INSTABILITY = "STRATEGIC_CONCLUSION_INSTABILITY"
    SYSTEMIC_COHERENCE_COLLAPSE = "SYSTEMIC_COHERENCE_COLLAPSE"


class CognitiveCoherenceAction(StrEnum):
    """Actions available to restore cognitive coherence."""

    PRESERVE_COHERENCE_STATE = "PRESERVE_COHERENCE_STATE"
    REBUILD_REASONING_CHAIN = "REBUILD_REASONING_CHAIN"
    RECHECK_DECISION_SEQUENCE = "RECHECK_DECISION_SEQUENCE"
    ALIGN_WORLD_MODEL_ACTIONS = "ALIGN_WORLD_MODEL_ACTIONS"
    RECONCILE_TIMELINE_FORECAST = "RECONCILE_TIMELINE_FORECAST"
    REPAIR_POLICY_REASONING = "REPAIR_POLICY_REASONING"
    REBUILD_CONSENSUS_COHERENCE = "REBUILD_CONSENSUS_COHERENCE"
    REDUCE_AUTONOMY = "REDUCE_AUTONOMY"
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"
    LOCK_COHERENCE_STATE = "LOCK_COHERENCE_STATE"


class CognitiveCoherenceRecommendation(StrEnum):
    """Recommended controls emitted by cognitive coherence."""

    CONTINUE_COHERENCE_MONITORING = "CONTINUE_COHERENCE_MONITORING"
    EXTEND_REASONING_TRACE = "EXTEND_REASONING_TRACE"
    VALIDATE_DECISION_CHAIN = "VALIDATE_DECISION_CHAIN"
    RECHECK_WORLD_MODEL_ACTION_LINK = "RECHECK_WORLD_MODEL_ACTION_LINK"
    RECONCILE_FORECAST_TIMELINES = "RECONCILE_FORECAST_TIMELINES"
    REPAIR_STRATEGIC_CONCLUSIONS = "REPAIR_STRATEGIC_CONCLUSIONS"
    KEEP_AUTONOMY_REDUCED = "KEEP_AUTONOMY_REDUCED"
    REQUIRE_SUPERVISION = "REQUIRE_SUPERVISION"
    UPDATE_COHERENCE_SNAPSHOT = "UPDATE_COHERENCE_SNAPSHOT"
    PRESERVE_LOGICAL_INVARIANTS = "PRESERVE_LOGICAL_INVARIANTS"


@dataclass(frozen=True)
class ReasoningChain:
    """One explainable reasoning chain across cognitive layers."""

    name: str
    steps: tuple[str, ...]
    score: int
    complete: bool
    broken_step: str | None = None


@dataclass(frozen=True)
class CoherenceAxis:
    """One evaluated coherence axis."""

    name: str
    score: int
    coherent: bool
    risk: CognitiveCoherenceRisk | None
    evidence: str


@dataclass(frozen=True)
class CoherenceMatrix:
    """Global coherence matrix across reasoning, policies and simulations."""

    axes: tuple[CoherenceAxis, ...]
    reasoning_chains: tuple[ReasoningChain, ...]
    global_score: int
    weakest_axis: str | None
    broken_axes: tuple[str, ...]
    locked: bool
    autonomy_reduced: bool


@dataclass(frozen=True)
class CognitiveCoherenceScore:
    """Coherence component scores normalized to 0..100."""

    logical_consistency_score: int
    reasoning_chain_score: int
    decision_sequence_score: int
    world_model_action_score: int
    timeline_forecast_score: int
    policy_reasoning_score: int
    alignment_coherence_score: int
    consensus_coherence_score: int
    strategic_conclusion_score: int
    systemic_coherence_score: int


@dataclass(frozen=True)
class CognitiveCoherenceInput:
    """Inputs consumed by the offline cognitive coherence engine."""

    cognitive_alignment: CognitiveAlignmentResult | None = None
    intent_integrity: IntentIntegrityResult | None = None
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
    scenario_forecast: ScenarioForecastResult | None = None
    multi_timeline: MultiTimelineSimulationResult | None = None
    strategic_arbitration: ArbitrationResult | None = None


@dataclass(frozen=True)
class CognitiveCoherenceEvent:
    """Auditable cognitive coherence event."""

    state: CognitiveCoherenceState
    mode: CognitiveCoherenceMode
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class CognitiveCoherenceResult:
    """Final autonomous cognitive coherence result."""

    state: CognitiveCoherenceState
    mode: CognitiveCoherenceMode
    cognitive_coherence_score: int
    score_breakdown: CognitiveCoherenceScore
    reasoning_chains: tuple[ReasoningChain, ...]
    axes: tuple[CoherenceAxis, ...]
    matrix: CoherenceMatrix
    risks: tuple[CognitiveCoherenceRisk, ...]
    actions: tuple[CognitiveCoherenceAction, ...]
    recommendations: tuple[CognitiveCoherenceRecommendation, ...]
    events: tuple[CognitiveCoherenceEvent, ...]
    summary: str


__all__ = [
    "CognitiveCoherenceAction",
    "CognitiveCoherenceEvent",
    "CognitiveCoherenceInput",
    "CognitiveCoherenceMode",
    "CognitiveCoherenceRecommendation",
    "CognitiveCoherenceResult",
    "CognitiveCoherenceRisk",
    "CognitiveCoherenceScore",
    "CognitiveCoherenceState",
    "CoherenceAxis",
    "CoherenceMatrix",
    "ReasoningChain",
]
