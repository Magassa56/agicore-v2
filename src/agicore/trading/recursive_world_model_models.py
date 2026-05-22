"""Models for the offline Autonomous Recursive World Model Engine."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .behavioral_stability_models import BehavioralStabilityResult
from .cognitive_adaptation_models import CognitiveAdaptationResult
from .collective_consensus_models import ConsensusResult
from .global_orchestrator_models import CoordinationResult, GlobalOrchestratorResult, SystemHealthSnapshot
from .intent_alignment_models import IntentAlignmentResult
from .long_horizon_planning_models import LongHorizonPlanningResult
from .mission_continuity_models import MissionContinuityResult
from .multi_timeline_simulation_models import MultiTimelineSimulationResult
from .operational_awareness_models import OperationalAwarenessResult
from .recovery_resilience_models import RecoveryResilienceResult
from .reward_models import RewardEvaluationResult
from .scenario_forecast_models import ScenarioForecastResult
from .strategic_arbitration_models import ArbitrationResult
from .strategic_memory_models import StrategicTimelineAnalysis
from .strategy_evolution_models import StrategyEvolutionResult
from .system_integrity_models import SystemIntegrityResult


class WorldModelLayer(StrEnum):
    """Recursive world model layers."""

    PERCEPTION = "PERCEPTION"
    STATE_MEMORY = "STATE_MEMORY"
    DYNAMICS = "DYNAMICS"
    PLANNING = "PLANNING"
    ACTION = "ACTION"
    GOVERNANCE = "GOVERNANCE"
    SAFETY = "SAFETY"
    META_COGNITION = "META_COGNITION"
    FORECASTING = "FORECASTING"
    ORCHESTRATION = "ORCHESTRATION"


class WorldModelRisk(StrEnum):
    """World model risks detected across recursive layers."""

    WORLD_MODEL_INCOHERENCE = "WORLD_MODEL_INCOHERENCE"
    CAUSAL_CONTRADICTION = "CAUSAL_CONTRADICTION"
    STATE_DRIFT = "STATE_DRIFT"
    DYNAMICS_INSTABILITY = "DYNAMICS_INSTABILITY"
    PLANNING_ACTION_MISMATCH = "PLANNING_ACTION_MISMATCH"
    FORECAST_REALITY_GAP = "FORECAST_REALITY_GAP"
    ORCHESTRATION_DESYNC = "ORCHESTRATION_DESYNC"
    GOVERNANCE_MISALIGNMENT = "GOVERNANCE_MISALIGNMENT"
    SAFETY_MODEL_FAILURE = "SAFETY_MODEL_FAILURE"
    RECURSIVE_FEEDBACK_LOOP = "RECURSIVE_FEEDBACK_LOOP"


class WorldModelDecision(StrEnum):
    """Final recursive world model decision."""

    MAINTAIN_WORLD_MODEL = "MAINTAIN_WORLD_MODEL"
    UPDATE_INTERNAL_STATE = "UPDATE_INTERNAL_STATE"
    REBUILD_CAUSAL_GRAPH = "REBUILD_CAUSAL_GRAPH"
    PRIORITIZE_SAFETY_MODEL = "PRIORITIZE_SAFETY_MODEL"
    ENTER_WORLD_MODEL_SAFE_MODE = "ENTER_WORLD_MODEL_SAFE_MODE"
    REQUIRE_MORE_OBSERVATION = "REQUIRE_MORE_OBSERVATION"
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"
    FREEZE_RECURSIVE_UPDATES = "FREEZE_RECURSIVE_UPDATES"


class WorldModelRecommendation(StrEnum):
    """Recommended controls from the recursive world model."""

    UPDATE_STATE_MEMORY = "UPDATE_STATE_MEMORY"
    REBALANCE_CAUSAL_LINKS = "REBALANCE_CAUSAL_LINKS"
    CHECK_FORECAST_ALIGNMENT = "CHECK_FORECAST_ALIGNMENT"
    STABILIZE_DYNAMICS = "STABILIZE_DYNAMICS"
    ALIGN_PLANNING_ACTION = "ALIGN_PLANNING_ACTION"
    REDUCE_RECURSIVE_DEPTH = "REDUCE_RECURSIVE_DEPTH"
    PROTECT_SAFETY_MODEL = "PROTECT_SAFETY_MODEL"
    SYNC_ORCHESTRATION_STATE = "SYNC_ORCHESTRATION_STATE"
    EXTEND_OBSERVATION_WINDOW = "EXTEND_OBSERVATION_WINDOW"
    PRESERVE_WORLD_MODEL_SNAPSHOT = "PRESERVE_WORLD_MODEL_SNAPSHOT"


@dataclass(frozen=True)
class WorldModelState:
    """Current score and status of one world model layer."""

    layer: WorldModelLayer
    coherence_score: int
    confidence_score: int
    status: str
    signals: tuple[str, ...] = ()


@dataclass(frozen=True)
class WorldModelCausalLink:
    """Directed causal relation between world model layers."""

    source: WorldModelLayer
    target: WorldModelLayer
    strength_score: int
    polarity: str
    evidence: str


@dataclass(frozen=True)
class WorldModelPrediction:
    """Predicted impact from one layer to another."""

    source_layer: WorldModelLayer
    target_layer: WorldModelLayer
    impact_score: int
    confidence_score: int
    prediction: str
    risks: tuple[WorldModelRisk, ...] = ()


@dataclass(frozen=True)
class WorldModelCoherenceScore:
    """World model coherence components normalized to 0..100."""

    perception_score: int
    state_memory_score: int
    dynamics_score: int
    planning_score: int
    action_score: int
    governance_score: int
    safety_score: int
    meta_cognition_score: int
    forecasting_score: int
    orchestration_score: int
    causal_consistency_score: int


@dataclass(frozen=True)
class WorldModelGraph:
    """Recursive world model causal graph."""

    layers: tuple[WorldModelLayer, ...]
    links: tuple[WorldModelCausalLink, ...]
    critical_layers: tuple[WorldModelLayer, ...]
    unstable_layers: tuple[WorldModelLayer, ...]
    dominant_layer: WorldModelLayer | None


@dataclass(frozen=True)
class RecursiveWorldModelInput:
    """Inputs consumed by the offline recursive world model engine."""

    multi_timeline: MultiTimelineSimulationResult | None = None
    scenario_forecast: ScenarioForecastResult | None = None
    long_horizon_plan: LongHorizonPlanningResult | None = None
    strategy_evolution: StrategyEvolutionResult | None = None
    global_orchestrator: GlobalOrchestratorResult | None = None
    coordination_result: CoordinationResult | None = None
    health_snapshot: SystemHealthSnapshot | None = None
    strategic_timeline_analysis: StrategicTimelineAnalysis | None = None
    operational_awareness: OperationalAwarenessResult | None = None
    mission_continuity: MissionContinuityResult | None = None
    recovery_resilience: RecoveryResilienceResult | None = None
    system_integrity: SystemIntegrityResult | None = None
    intent_alignment: IntentAlignmentResult | None = None
    strategic_arbitration: ArbitrationResult | None = None
    collective_consensus: ConsensusResult | None = None
    behavioral_stability: BehavioralStabilityResult | None = None
    cognitive_adaptation: CognitiveAdaptationResult | None = None
    reward_evaluation: RewardEvaluationResult | None = None


@dataclass(frozen=True)
class WorldModelEvent:
    """Auditable recursive world model event."""

    decision: WorldModelDecision
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class RecursiveWorldModelResult:
    """Final recursive world model result."""

    decision: WorldModelDecision
    world_model_coherence_score: int
    coherence_breakdown: WorldModelCoherenceScore
    states: tuple[WorldModelState, ...]
    graph: WorldModelGraph
    predictions: tuple[WorldModelPrediction, ...]
    risks: tuple[WorldModelRisk, ...]
    recommendations: tuple[WorldModelRecommendation, ...]
    events: tuple[WorldModelEvent, ...]
    summary: str


__all__ = [
    "RecursiveWorldModelInput",
    "RecursiveWorldModelResult",
    "WorldModelCausalLink",
    "WorldModelCoherenceScore",
    "WorldModelDecision",
    "WorldModelEvent",
    "WorldModelGraph",
    "WorldModelLayer",
    "WorldModelPrediction",
    "WorldModelRecommendation",
    "WorldModelRisk",
    "WorldModelState",
]
