"""Models for the offline Autonomous Multi-Timeline Simulation Engine."""
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
from .operational_awareness_models import OperationalAwarenessResult
from .recovery_resilience_models import RecoveryResilienceResult
from .reward_models import RewardEvaluationResult
from .scenario_forecast_models import ScenarioForecastResult
from .strategic_arbitration_models import ArbitrationResult
from .strategic_memory_models import StrategicTimelineAnalysis
from .strategy_evolution_models import StrategyEvolutionResult
from .system_integrity_models import SystemIntegrityResult


class TimelineScenario(StrEnum):
    """Supported future timeline scenario types."""

    BASELINE_TIMELINE = "BASELINE_TIMELINE"
    SAFE_TIMELINE = "SAFE_TIMELINE"
    RECOVERY_TIMELINE = "RECOVERY_TIMELINE"
    GROWTH_TIMELINE = "GROWTH_TIMELINE"
    DEGRADED_TIMELINE = "DEGRADED_TIMELINE"
    HIGH_VOLATILITY_TIMELINE = "HIGH_VOLATILITY_TIMELINE"
    BEHAVIORAL_RISK_TIMELINE = "BEHAVIORAL_RISK_TIMELINE"
    SYSTEM_RISK_TIMELINE = "SYSTEM_RISK_TIMELINE"
    EMERGENCY_TIMELINE = "EMERGENCY_TIMELINE"
    UNKNOWN_TIMELINE = "UNKNOWN_TIMELINE"


class TimelineOutcome(StrEnum):
    """Simulated outcome for one timeline."""

    STABLE = "STABLE"
    IMPROVING = "IMPROVING"
    DEGRADED = "DEGRADED"
    UNSTABLE = "UNSTABLE"
    COLLAPSING = "COLLAPSING"
    RECOVERING = "RECOVERING"
    SAFE_MODE = "SAFE_MODE"
    EMERGENCY_STOP = "EMERGENCY_STOP"


class TimelineRisk(StrEnum):
    """Risks detected across simulated future timelines."""

    DIVERGENCE_RISK = "DIVERGENCE_RISK"
    COLLAPSE_RISK = "COLLAPSE_RISK"
    STRATEGIC_DRIFT_RISK = "STRATEGIC_DRIFT_RISK"
    BEHAVIORAL_REGRESSION_RISK = "BEHAVIORAL_REGRESSION_RISK"
    SYSTEM_FAILURE_RISK = "SYSTEM_FAILURE_RISK"
    RECOVERY_FAILURE_RISK = "RECOVERY_FAILURE_RISK"
    SAFE_MODE_DEPENDENCY = "SAFE_MODE_DEPENDENCY"
    LOW_SURVIVABILITY = "LOW_SURVIVABILITY"
    TIMELINE_UNCERTAINTY = "TIMELINE_UNCERTAINTY"
    INCOMPATIBLE_FUTURE_PATH = "INCOMPATIBLE_FUTURE_PATH"


class TimelineDecision(StrEnum):
    """Final multi-timeline decision."""

    SELECT_STABLE_TIMELINE = "SELECT_STABLE_TIMELINE"
    SELECT_RECOVERY_TIMELINE = "SELECT_RECOVERY_TIMELINE"
    SELECT_SAFE_TIMELINE = "SELECT_SAFE_TIMELINE"
    AVOID_UNSTABLE_TIMELINE = "AVOID_UNSTABLE_TIMELINE"
    REQUIRE_MORE_SIMULATION = "REQUIRE_MORE_SIMULATION"
    ENTER_TIMELINE_SAFE_MODE = "ENTER_TIMELINE_SAFE_MODE"
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"
    REBUILD_TIMELINE_SET = "REBUILD_TIMELINE_SET"


class TimelineRecommendation(StrEnum):
    """Recommended controls from multi-timeline simulation."""

    FOLLOW_BASELINE_IF_STABLE = "FOLLOW_BASELINE_IF_STABLE"
    PRIORITIZE_SAFE_TIMELINE = "PRIORITIZE_SAFE_TIMELINE"
    PRIORITIZE_RECOVERY_PATH = "PRIORITIZE_RECOVERY_PATH"
    AVOID_HIGH_DIVERGENCE_PATH = "AVOID_HIGH_DIVERGENCE_PATH"
    EXTEND_SIMULATION_DEPTH = "EXTEND_SIMULATION_DEPTH"
    REDUCE_STRATEGIC_RISK = "REDUCE_STRATEGIC_RISK"
    STABILIZE_BEHAVIOR_BEFORE_EXECUTION = "STABILIZE_BEHAVIOR_BEFORE_EXECUTION"
    CHECK_SYSTEM_INTEGRITY = "CHECK_SYSTEM_INTEGRITY"
    UPDATE_FORECAST_MODEL = "UPDATE_FORECAST_MODEL"
    PRESERVE_TIMELINE_MEMORY = "PRESERVE_TIMELINE_MEMORY"


@dataclass(frozen=True)
class TimelineState:
    """Projected state for one future timeline."""

    scenario: TimelineScenario
    stability_score: int
    recovery_score: int
    growth_score: int
    safety_score: int
    system_health_score: int
    behavior_score: int
    outcome: TimelineOutcome
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class TimelineDivergence:
    """Divergence between baseline and an alternative timeline."""

    baseline: TimelineScenario
    alternative: TimelineScenario
    divergence_score: int
    severity: str
    drivers: tuple[str, ...]


@dataclass(frozen=True)
class TimelineSurvivabilityScore:
    """Survivability components for one timeline."""

    scenario: TimelineScenario
    survivability_score: int
    stability_component: int
    safety_component: int
    recovery_component: int
    mission_component: int
    confidence_component: int


@dataclass(frozen=True)
class TimelineComparisonGraph:
    """Explainable comparison graph across timelines."""

    nodes: tuple[str, ...]
    edges: tuple[tuple[str, str, str], ...]
    stable_paths: tuple[TimelineScenario, ...]
    unstable_paths: tuple[TimelineScenario, ...]
    recommended_path: TimelineScenario | None


@dataclass(frozen=True)
class MultiTimelineSimulationInput:
    """Inputs consumed by the offline multi-timeline simulator."""

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
    requested_timelines: tuple[TimelineScenario, ...] = ()


@dataclass(frozen=True)
class TimelineEvent:
    """Auditable timeline simulation event."""

    decision: TimelineDecision
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class MultiTimelineSimulationResult:
    """Final multi-timeline simulation result."""

    decision: TimelineDecision
    selected_timeline: TimelineScenario | None
    timeline_states: tuple[TimelineState, ...]
    divergences: tuple[TimelineDivergence, ...]
    survivability_scores: tuple[TimelineSurvivabilityScore, ...]
    comparison_graph: TimelineComparisonGraph
    risks: tuple[TimelineRisk, ...]
    recommendations: tuple[TimelineRecommendation, ...]
    overall_survivability_score: int
    events: tuple[TimelineEvent, ...]
    summary: str


__all__ = [
    "MultiTimelineSimulationInput",
    "MultiTimelineSimulationResult",
    "TimelineComparisonGraph",
    "TimelineDecision",
    "TimelineDivergence",
    "TimelineEvent",
    "TimelineOutcome",
    "TimelineRecommendation",
    "TimelineRisk",
    "TimelineScenario",
    "TimelineState",
    "TimelineSurvivabilityScore",
]
