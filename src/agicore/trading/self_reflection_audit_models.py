"""Models for the offline Autonomous Self-Reflection & Cognitive Audit Engine."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .behavioral_stability_models import BehavioralStabilityResult
from .cognitive_adaptation_models import CognitiveAdaptationResult
from .collective_consensus_models import ConsensusResult
from .global_orchestrator_models import GlobalOrchestratorResult
from .intent_alignment_models import IntentAlignmentResult
from .learning_governance_models import LearningGovernanceResult
from .meta_cognition_models import MetaCognitionResult
from .multi_timeline_simulation_models import MultiTimelineSimulationResult
from .recursive_self_evaluation_models import SelfEvaluationResult
from .recursive_world_model_models import RecursiveWorldModelResult
from .scenario_forecast_models import ScenarioForecastResult
from .strategic_arbitration_models import ArbitrationResult
from .strategic_memory_models import StrategicTimelineAnalysis


class ReflectionState(StrEnum):
    """Self-reflection state."""

    CLEAR_REFLECTION = "CLEAR_REFLECTION"
    PARTIAL_REFLECTION = "PARTIAL_REFLECTION"
    DEGRADED_REFLECTION = "DEGRADED_REFLECTION"
    CONTRADICTORY_REFLECTION = "CONTRADICTORY_REFLECTION"
    AUDIT_REQUIRED = "AUDIT_REQUIRED"
    CRITICAL_REVIEW = "CRITICAL_REVIEW"
    SELF_CORRECTION_NEEDED = "SELF_CORRECTION_NEEDED"


class ReflectionDepth(StrEnum):
    """Depth of cognitive audit required."""

    SHALLOW = "SHALLOW"
    STANDARD = "STANDARD"
    DEEP = "DEEP"
    RECURSIVE = "RECURSIVE"
    CRITICAL = "CRITICAL"


class CognitiveAuditSignal(StrEnum):
    """Signals emitted by self-reflection and cognitive audit."""

    DECISION_TRACE_AVAILABLE = "DECISION_TRACE_AVAILABLE"
    REASONING_GAP = "REASONING_GAP"
    STRATEGIC_CONTRADICTION = "STRATEGIC_CONTRADICTION"
    BEHAVIORAL_DRIFT_DETECTED = "BEHAVIORAL_DRIFT_DETECTED"
    COGNITIVE_BIAS_DETECTED = "COGNITIVE_BIAS_DETECTED"
    WORLD_MODEL_INCONSISTENCY = "WORLD_MODEL_INCONSISTENCY"
    ORCHESTRATION_MISMATCH = "ORCHESTRATION_MISMATCH"
    FORECAST_MISMATCH = "FORECAST_MISMATCH"
    AUDIT_TRAIL_INCOMPLETE = "AUDIT_TRAIL_INCOMPLETE"
    SELF_CORRECTION_OPPORTUNITY = "SELF_CORRECTION_OPPORTUNITY"


class CognitiveAuditRisk(StrEnum):
    """Risks detected during self-reflection audit."""

    UNEXPLAINED_DECISION = "UNEXPLAINED_DECISION"
    REPEATED_COGNITIVE_ERROR = "REPEATED_COGNITIVE_ERROR"
    STRATEGIC_SELF_CONTRADICTION = "STRATEGIC_SELF_CONTRADICTION"
    BEHAVIORAL_DECAY = "BEHAVIORAL_DECAY"
    REFLECTION_FAILURE = "REFLECTION_FAILURE"
    LOW_AUDIT_CONFIDENCE = "LOW_AUDIT_CONFIDENCE"
    WORLD_MODEL_DRIFT = "WORLD_MODEL_DRIFT"
    META_COGNITIVE_DRIFT = "META_COGNITIVE_DRIFT"
    INCOMPLETE_TRACEABILITY = "INCOMPLETE_TRACEABILITY"
    SELF_CORRECTION_FAILURE = "SELF_CORRECTION_FAILURE"


class CognitiveAuditRecommendation(StrEnum):
    """Recommended corrective actions from cognitive audit."""

    REQUIRE_DEEP_AUDIT = "REQUIRE_DEEP_AUDIT"
    REBUILD_DECISION_TRACE = "REBUILD_DECISION_TRACE"
    CORRECT_STRATEGIC_CONFLICT = "CORRECT_STRATEGIC_CONFLICT"
    STABILIZE_BEHAVIORAL_BASELINE = "STABILIZE_BEHAVIORAL_BASELINE"
    RECALIBRATE_META_COGNITION = "RECALIBRATE_META_COGNITION"
    UPDATE_WORLD_MODEL = "UPDATE_WORLD_MODEL"
    EXTEND_AUDIT_TRAIL = "EXTEND_AUDIT_TRAIL"
    REDUCE_AUTONOMY_DURING_AUDIT = "REDUCE_AUTONOMY_DURING_AUDIT"
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"
    CONTINUE_REFLECTION_MONITORING = "CONTINUE_REFLECTION_MONITORING"


@dataclass(frozen=True)
class CognitiveAuditFinding:
    """One ordered audit finding."""

    title: str
    severity_score: int
    signals: tuple[CognitiveAuditSignal, ...]
    risks: tuple[CognitiveAuditRisk, ...]
    explanation: str
    corrective_action: CognitiveAuditRecommendation


@dataclass(frozen=True)
class ReflectionQualityScore:
    """Reflection quality components normalized to 0..100."""

    traceability_score: int
    reasoning_coherence_score: int
    strategic_consistency_score: int
    behavioral_awareness_score: int
    meta_cognitive_score: int
    world_model_alignment_score: int
    self_correction_readiness_score: int


@dataclass(frozen=True)
class CognitiveAuditTrail:
    """Explainable audit trail across decision layers."""

    steps: tuple[str, ...]
    missing_steps: tuple[str, ...]
    linked_engines: tuple[str, ...]
    trace_complete: bool
    confidence_score: int


@dataclass(frozen=True)
class SelfReflectionAuditInput:
    """Inputs consumed by the offline self-reflection audit engine."""

    recursive_world_model: RecursiveWorldModelResult | None = None
    global_orchestrator: GlobalOrchestratorResult | None = None
    meta_cognition: MetaCognitionResult | None = None
    cognitive_adaptation: CognitiveAdaptationResult | None = None
    behavioral_stability: BehavioralStabilityResult | None = None
    strategic_timeline_analysis: StrategicTimelineAnalysis | None = None
    scenario_forecast: ScenarioForecastResult | None = None
    multi_timeline: MultiTimelineSimulationResult | None = None
    intent_alignment: IntentAlignmentResult | None = None
    strategic_arbitration: ArbitrationResult | None = None
    collective_consensus: ConsensusResult | None = None
    learning_governance: LearningGovernanceResult | None = None
    self_evaluation: SelfEvaluationResult | None = None


@dataclass(frozen=True)
class CognitiveAuditEvent:
    """Auditable self-reflection audit event."""

    state: ReflectionState
    depth: ReflectionDepth
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class SelfReflectionAuditResult:
    """Final self-reflection audit result."""

    state: ReflectionState
    depth: ReflectionDepth
    reflection_quality_score: int
    quality_breakdown: ReflectionQualityScore
    signals: tuple[CognitiveAuditSignal, ...]
    risks: tuple[CognitiveAuditRisk, ...]
    findings: tuple[CognitiveAuditFinding, ...]
    audit_trail: CognitiveAuditTrail
    recommendations: tuple[CognitiveAuditRecommendation, ...]
    events: tuple[CognitiveAuditEvent, ...]
    summary: str


__all__ = [
    "CognitiveAuditEvent",
    "CognitiveAuditFinding",
    "CognitiveAuditRecommendation",
    "CognitiveAuditRisk",
    "CognitiveAuditSignal",
    "CognitiveAuditTrail",
    "ReflectionDepth",
    "ReflectionQualityScore",
    "ReflectionState",
    "SelfReflectionAuditInput",
    "SelfReflectionAuditResult",
]
