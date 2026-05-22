"""Models for the offline Autonomous Scenario Forecast Engine."""
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
from .strategic_arbitration_models import ArbitrationResult
from .strategic_memory_models import StrategicTimelineAnalysis
from .system_integrity_models import SystemIntegrityResult


class ForecastScenarioType(StrEnum):
    """Forecast scenario archetypes."""

    STABLE_CONTINUATION = "STABLE_CONTINUATION"
    CONTROLLED_GROWTH = "CONTROLLED_GROWTH"
    RECOVERY_SUCCESS = "RECOVERY_SUCCESS"
    RECOVERY_FAILURE = "RECOVERY_FAILURE"
    STRATEGIC_DRIFT = "STRATEGIC_DRIFT"
    BEHAVIORAL_REGRESSION = "BEHAVIORAL_REGRESSION"
    SYSTEM_DEGRADATION = "SYSTEM_DEGRADATION"
    SAFE_MODE_TRANSITION = "SAFE_MODE_TRANSITION"
    MISSION_CONTINUITY_BREAK = "MISSION_CONTINUITY_BREAK"
    EMERGENCY_LOCKDOWN_PATH = "EMERGENCY_LOCKDOWN_PATH"


class ForecastProbabilityBand(StrEnum):
    """Relative probability bucket for one scenario."""

    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"
    UNKNOWN = "UNKNOWN"


class ForecastDecision(StrEnum):
    """Final scenario forecast decision."""

    CONTINUE_CURRENT_PATH = "CONTINUE_CURRENT_PATH"
    PRIORITIZE_SAFE_SCENARIO = "PRIORITIZE_SAFE_SCENARIO"
    PREPARE_RECOVERY_PATH = "PREPARE_RECOVERY_PATH"
    AVOID_HIGH_RISK_SCENARIO = "AVOID_HIGH_RISK_SCENARIO"
    REQUIRE_OBSERVATION_WINDOW = "REQUIRE_OBSERVATION_WINDOW"
    ENTER_FORECAST_SAFE_MODE = "ENTER_FORECAST_SAFE_MODE"
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"
    REBUILD_FORECAST_MODEL = "REBUILD_FORECAST_MODEL"


class ForecastRecommendation(StrEnum):
    """Recommended forecast controls."""

    INCREASE_MONITORING = "INCREASE_MONITORING"
    REDUCE_RISK_EXPOSURE = "REDUCE_RISK_EXPOSURE"
    PROTECT_STRATEGIC_MEMORY = "PROTECT_STRATEGIC_MEMORY"
    FREEZE_POLICY_EXPANSION = "FREEZE_POLICY_EXPANSION"
    PRIORITIZE_RECOVERY_SCENARIO = "PRIORITIZE_RECOVERY_SCENARIO"
    EXTEND_OBSERVATION_PERIOD = "EXTEND_OBSERVATION_PERIOD"
    UPDATE_LONG_HORIZON_PLAN = "UPDATE_LONG_HORIZON_PLAN"
    CHECK_SYSTEM_INTEGRITY = "CHECK_SYSTEM_INTEGRITY"
    STABILIZE_BEHAVIOR = "STABILIZE_BEHAVIOR"
    MAINTAIN_CURRENT_TRAJECTORY = "MAINTAIN_CURRENT_TRAJECTORY"


@dataclass(frozen=True)
class ForecastScenario:
    """One forecasted future path."""

    scenario_type: ForecastScenarioType
    probability_band: ForecastProbabilityBand
    probability_score: int
    survivable: bool
    stability_impact_score: int
    description: str
    risk_notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class ForecastBifurcation:
    """Critical fork between opposing future scenarios."""

    positive_scenario: ForecastScenarioType
    negative_scenario: ForecastScenarioType
    severity_score: int
    trigger: str
    recommended_resolution: str


@dataclass(frozen=True)
class ForecastRiskMap:
    """Future risk map by system category, normalized to 0..100."""

    strategy: int
    behavior: int
    cognition: int
    integrity: int
    continuity: int
    recovery: int
    mission: int


@dataclass(frozen=True)
class ForecastStabilityScore:
    """Forecast stability component scores normalized to 0..100."""

    scenario_balance_score: int
    survivability_score: int
    system_health_score: int
    behavioral_stability_score: int
    continuity_score: int
    confidence_score: int


@dataclass(frozen=True)
class ScenarioForecastInput:
    """Inputs consumed by the offline scenario forecast engine."""

    long_horizon_plan: LongHorizonPlanningResult | None = None
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
class ForecastEvent:
    """Auditable forecast event."""

    decision: ForecastDecision
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class ScenarioForecastResult:
    """Final scenario forecast result."""

    decision: ForecastDecision
    forecast_stability_score: int
    stability_breakdown: ForecastStabilityScore
    scenarios: tuple[ForecastScenario, ...]
    bifurcations: tuple[ForecastBifurcation, ...]
    risk_map: ForecastRiskMap
    recommendations: tuple[ForecastRecommendation, ...]
    survivable_scenarios: tuple[ForecastScenarioType, ...]
    critical_scenarios: tuple[ForecastScenarioType, ...]
    events: tuple[ForecastEvent, ...]
    summary: str


__all__ = [
    "ForecastBifurcation",
    "ForecastDecision",
    "ForecastEvent",
    "ForecastProbabilityBand",
    "ForecastRecommendation",
    "ForecastRiskMap",
    "ForecastScenario",
    "ForecastScenarioType",
    "ForecastStabilityScore",
    "ScenarioForecastInput",
    "ScenarioForecastResult",
]
