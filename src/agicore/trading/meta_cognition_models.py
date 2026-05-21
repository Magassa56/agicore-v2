"""Models for the offline Autonomous Meta-Cognition Engine."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .behavioral_stability_models import BehavioralStabilityResult
from .cognitive_adaptation_models import CognitiveAdaptationResult
from .executive_brain_models import ExecutiveBrainResult
from .hierarchical_supervisor_models import SupervisorResult
from .learning_governance_models import LearningGovernanceResult
from .multi_agent_models import AgentCoordinationResult
from .operational_awareness_models import OperationalAwarenessResult
from .recursive_self_evaluation_models import SelfEvaluationResult
from .strategic_memory_models import StrategicTimelineAnalysis
from .system_integrity_models import SystemIntegrityResult


class MetaCognitionMode(StrEnum):
    """Meta-cognitive reasoning mode."""

    SELF_AWARE = "SELF_AWARE"
    REFLECTIVE = "REFLECTIVE"
    UNCERTAIN = "UNCERTAIN"
    OVERCONFIDENT = "OVERCONFIDENT"
    RIGID = "RIGID"
    CONTRADICTORY = "CONTRADICTORY"
    DEGRADED_REASONING = "DEGRADED_REASONING"
    RECALIBRATION_REQUIRED = "RECALIBRATION_REQUIRED"


class CognitiveBias(StrEnum):
    """Biases detected in the decision reasoning process."""

    OVERCONFIDENCE = "OVERCONFIDENCE"
    CONFIRMATION_BIAS = "CONFIRMATION_BIAS"
    REACTIONARY_DECISION = "REACTIONARY_DECISION"
    STRATEGIC_RIGIDITY = "STRATEGIC_RIGIDITY"
    RECENCY_BIAS = "RECENCY_BIAS"
    FEEDBACK_IGNORANCE = "FEEDBACK_IGNORANCE"
    COGNITIVE_FRAGMENTATION = "COGNITIVE_FRAGMENTATION"
    EXCESSIVE_AUTONOMY = "EXCESSIVE_AUTONOMY"
    DECISION_INCONSISTENCY = "DECISION_INCONSISTENCY"
    REASONING_DRIFT = "REASONING_DRIFT"


class CognitiveRigidity(StrEnum):
    """Rigidity level for the reasoning process."""

    FLEXIBLE = "FLEXIBLE"
    SOMEWHAT_RIGID = "SOMEWHAT_RIGID"
    RIGID = "RIGID"
    LOCKED = "LOCKED"


class CognitiveContradiction(StrEnum):
    """Contradictions detected between reasoning layers."""

    EXECUTIVE_SUPERVISOR_DIVERGENCE = "EXECUTIVE_SUPERVISOR_DIVERGENCE"
    SELF_EVALUATION_CONTRADICTION = "SELF_EVALUATION_CONTRADICTION"
    AWARENESS_CONFIDENCE_MISMATCH = "AWARENESS_CONFIDENCE_MISMATCH"
    STRATEGY_GOVERNANCE_MISMATCH = "STRATEGY_GOVERNANCE_MISMATCH"
    AGENT_SUPERVISOR_MISMATCH = "AGENT_SUPERVISOR_MISMATCH"
    MEMORY_REASONING_MISMATCH = "MEMORY_REASONING_MISMATCH"


class MetaCognitiveSignal(StrEnum):
    """Signals emitted by meta-cognitive analysis."""

    REASONING_STABLE = "REASONING_STABLE"
    REASONING_UNSTABLE = "REASONING_UNSTABLE"
    REFLECTION_NEEDED = "REFLECTION_NEEDED"
    SELF_AWARENESS_STRONG = "SELF_AWARENESS_STRONG"
    SELF_AWARENESS_WEAK = "SELF_AWARENESS_WEAK"
    CONTRADICTION_DETECTED = "CONTRADICTION_DETECTED"
    BIAS_DETECTED = "BIAS_DETECTED"
    RIGIDITY_DETECTED = "RIGIDITY_DETECTED"
    FEEDBACK_CONNECTED = "FEEDBACK_CONNECTED"
    FEEDBACK_DISCONNECTED = "FEEDBACK_DISCONNECTED"
    RECALIBRATION_NEEDED = "RECALIBRATION_NEEDED"


class MetaCognitiveRisk(StrEnum):
    """Risks that can degrade meta-cognitive reasoning quality."""

    LOGICAL_INSTABILITY = "LOGICAL_INSTABILITY"
    STRATEGIC_CONTRADICTION = "STRATEGIC_CONTRADICTION"
    COGNITIVE_COLLAPSE = "COGNITIVE_COLLAPSE"
    META_CONFIDENCE_FAILURE = "META_CONFIDENCE_FAILURE"
    REASONING_DEGRADATION = "REASONING_DEGRADATION"
    AUTONOMY_OVEREXPANSION = "AUTONOMY_OVEREXPANSION"
    FEEDBACK_DISCONNECTION = "FEEDBACK_DISCONNECTION"
    DECISION_CHAOS = "DECISION_CHAOS"
    SELF_EVALUATION_DRIFT = "SELF_EVALUATION_DRIFT"
    RECALIBRATION_FAILURE = "RECALIBRATION_FAILURE"


class MetaCognitiveRecommendation(StrEnum):
    """Recommended meta-cognitive controls."""

    REDUCE_AUTONOMY = "REDUCE_AUTONOMY"
    REQUIRE_SUPERVISION = "REQUIRE_SUPERVISION"
    RECALIBRATE_REASONING = "RECALIBRATE_REASONING"
    FREEZE_DECISION_EXPANSION = "FREEZE_DECISION_EXPANSION"
    INCREASE_REFLECTION = "INCREASE_REFLECTION"
    REBUILD_LOGICAL_STABILITY = "REBUILD_LOGICAL_STABILITY"
    REVIEW_STRATEGIC_ALIGNMENT = "REVIEW_STRATEGIC_ALIGNMENT"
    STABILIZE_REASONING = "STABILIZE_REASONING"
    CONTINUE_MONITORING = "CONTINUE_MONITORING"
    ENTER_SAFE_REASONING_MODE = "ENTER_SAFE_REASONING_MODE"


@dataclass(frozen=True)
class MetaCognitiveConfidence:
    """Meta-cognitive component scores normalized to 0..100."""

    reasoning_stability_score: int
    self_awareness_score: int
    contradiction_resistance_score: int
    bias_resistance_score: int
    strategic_alignment_score: int
    feedback_integration_score: int
    autonomy_calibration_score: int


@dataclass(frozen=True)
class MetaCognitionInput:
    """Inputs consumed by the offline meta-cognition engine."""

    operational_awareness: OperationalAwarenessResult | None = None
    self_evaluation: SelfEvaluationResult | None = None
    executive_result: ExecutiveBrainResult | None = None
    cognitive_adaptation: CognitiveAdaptationResult | None = None
    behavioral_stability: BehavioralStabilityResult | None = None
    system_integrity: SystemIntegrityResult | None = None
    strategic_timeline_analysis: StrategicTimelineAnalysis | None = None
    agent_coordination: AgentCoordinationResult | None = None
    supervisor_result: SupervisorResult | None = None
    learning_governance: LearningGovernanceResult | None = None


@dataclass(frozen=True)
class MetaCognitiveEvent:
    """Auditable meta-cognitive event."""

    mode: MetaCognitionMode
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class MetaCognitionResult:
    """Final meta-cognitive reasoning assessment."""

    mode: MetaCognitionMode
    confidence_score: int
    confidence_breakdown: MetaCognitiveConfidence
    rigidity: CognitiveRigidity
    biases: tuple[CognitiveBias, ...]
    contradictions: tuple[CognitiveContradiction, ...]
    signals: tuple[MetaCognitiveSignal, ...]
    risks: tuple[MetaCognitiveRisk, ...]
    recommendations: tuple[MetaCognitiveRecommendation, ...]
    reasoning_stability_score: int
    reflective_state: str
    events: tuple[MetaCognitiveEvent, ...]
    summary: str


__all__ = [
    "CognitiveBias",
    "CognitiveContradiction",
    "CognitiveRigidity",
    "MetaCognitionInput",
    "MetaCognitionMode",
    "MetaCognitionResult",
    "MetaCognitiveConfidence",
    "MetaCognitiveEvent",
    "MetaCognitiveRecommendation",
    "MetaCognitiveRisk",
    "MetaCognitiveSignal",
]
