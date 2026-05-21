"""Models for the offline Autonomous Long-Horizon Planning Engine."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .behavioral_stability_models import BehavioralStabilityResult
from .collective_consensus_models import ConsensusResult
from .global_orchestrator_models import CoordinationResult, GlobalOrchestratorResult, SystemHealthSnapshot
from .intent_alignment_models import IntentAlignmentResult
from .mission_continuity_models import MissionContinuityResult
from .operational_awareness_models import OperationalAwarenessResult
from .recovery_resilience_models import RecoveryResilienceResult
from .reward_models import RewardEvaluationResult
from .strategic_arbitration_models import ArbitrationResult
from .strategic_memory_models import StrategicTimelineAnalysis
from .strategic_planning_models import StrategicPlanningResult
from .system_integrity_models import SystemIntegrityResult
from .tactical_execution_models import TacticalExecutionResult


class PlanningHorizon(StrEnum):
    """Planning horizon for long-horizon offline projections."""

    NEXT_SESSION = "NEXT_SESSION"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    EVALUATION_CHALLENGE = "EVALUATION_CHALLENGE"
    MULTI_PHASE_RECOVERY = "MULTI_PHASE_RECOVERY"
    LONG_TERM_GROWTH = "LONG_TERM_GROWTH"


class FutureScenarioType(StrEnum):
    """Future scenario archetypes."""

    STABLE_GROWTH = "STABLE_GROWTH"
    CONTROLLED_RECOVERY = "CONTROLLED_RECOVERY"
    DRAWDOWN_CONTINUATION = "DRAWDOWN_CONTINUATION"
    VOLATILITY_SPIKE = "VOLATILITY_SPIKE"
    BEHAVIORAL_DEGRADATION = "BEHAVIORAL_DEGRADATION"
    STRATEGIC_DRIFT = "STRATEGIC_DRIFT"
    SYSTEM_INSTABILITY = "SYSTEM_INSTABILITY"
    SAFE_MODE_REQUIRED = "SAFE_MODE_REQUIRED"
    LEARNING_IMPROVEMENT = "LEARNING_IMPROVEMENT"
    MISSION_CONTINUITY_RISK = "MISSION_CONTINUITY_RISK"


class PlanningRisk(StrEnum):
    """Risks projected by the long-horizon planner."""

    FUTURE_DRAWDOWN_RISK = "FUTURE_DRAWDOWN_RISK"
    STRATEGIC_DRIFT_RISK = "STRATEGIC_DRIFT_RISK"
    BEHAVIORAL_REGRESSION_RISK = "BEHAVIORAL_REGRESSION_RISK"
    SYSTEM_INSTABILITY_RISK = "SYSTEM_INSTABILITY_RISK"
    LEARNING_OVERADAPTATION_RISK = "LEARNING_OVERADAPTATION_RISK"
    LOW_CONFIDENCE_PROJECTION = "LOW_CONFIDENCE_PROJECTION"
    MISSION_DEVIATION_RISK = "MISSION_DEVIATION_RISK"
    RECOVERY_FAILURE_RISK = "RECOVERY_FAILURE_RISK"
    EXECUTION_QUALITY_DECAY = "EXECUTION_QUALITY_DECAY"
    CONTINUITY_BREAKDOWN_RISK = "CONTINUITY_BREAKDOWN_RISK"


class PlanningDecision(StrEnum):
    """Final planning decision."""

    PROCEED_WITH_PLAN = "PROCEED_WITH_PLAN"
    REDUCE_RISK_PLAN = "REDUCE_RISK_PLAN"
    OBSERVE_BEFORE_ACTION = "OBSERVE_BEFORE_ACTION"
    PRIORITIZE_RECOVERY = "PRIORITIZE_RECOVERY"
    PRIORITIZE_STABILITY = "PRIORITIZE_STABILITY"
    ENTER_LONG_HORIZON_SAFE_MODE = "ENTER_LONG_HORIZON_SAFE_MODE"
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"
    REBUILD_PLAN = "REBUILD_PLAN"


class PlanningRecommendation(StrEnum):
    """Recommended long-horizon controls."""

    LIMIT_TRADES_NEXT_SESSION = "LIMIT_TRADES_NEXT_SESSION"
    PRIORITIZE_CAPITAL_PRESERVATION = "PRIORITIZE_CAPITAL_PRESERVATION"
    CONTINUE_CONTROLLED_GROWTH = "CONTINUE_CONTROLLED_GROWTH"
    STRENGTHEN_BEHAVIORAL_GUARDS = "STRENGTHEN_BEHAVIORAL_GUARDS"
    FREEZE_POLICY_EXPANSION = "FREEZE_POLICY_EXPANSION"
    INCREASE_OBSERVATION_WINDOW = "INCREASE_OBSERVATION_WINDOW"
    PREPARE_RECOVERY_SEQUENCE = "PREPARE_RECOVERY_SEQUENCE"
    MAINTAIN_CURRENT_TRAJECTORY = "MAINTAIN_CURRENT_TRAJECTORY"
    RECHECK_SYSTEM_INTEGRITY = "RECHECK_SYSTEM_INTEGRITY"
    UPDATE_STRATEGIC_MEMORY = "UPDATE_STRATEGIC_MEMORY"


@dataclass(frozen=True)
class FutureScenario:
    """One plausible future scenario."""

    scenario_type: FutureScenarioType
    probability_score: int
    impact_score: int
    horizon: PlanningHorizon
    description: str
    recommended_bias: str


@dataclass(frozen=True)
class FutureProjection:
    """Projected future metrics from current offline evidence."""

    horizon: PlanningHorizon
    projected_stability_score: int
    projected_drawdown_risk_score: int
    projected_recovery_score: int
    projected_behavior_score: int
    projected_system_health_score: int
    projection_confidence: int


@dataclass(frozen=True)
class StrategicTrajectory:
    """Long-horizon strategic trajectory."""

    trajectory_label: str
    current_phase: str
    target_phase: str
    phase_sequence: tuple[str, ...]
    stability_trend: str
    expected_sessions: int
    notes: tuple[str, ...]


@dataclass(frozen=True)
class HorizonPlanGraph:
    """Explainable graph of scenarios, phases and controls."""

    horizon: PlanningHorizon
    nodes: tuple[str, ...]
    edges: tuple[tuple[str, str, str], ...]
    critical_path: tuple[str, ...]
    blocked_paths: tuple[str, ...]


@dataclass(frozen=True)
class LongHorizonPlanningInput:
    """Inputs consumed by the offline long-horizon planning engine."""

    global_orchestrator: GlobalOrchestratorResult | None = None
    coordination_result: CoordinationResult | None = None
    health_snapshot: SystemHealthSnapshot | None = None
    strategic_result: StrategicPlanningResult | None = None
    strategic_timeline_analysis: StrategicTimelineAnalysis | None = None
    operational_awareness: OperationalAwarenessResult | None = None
    mission_continuity: MissionContinuityResult | None = None
    recovery_resilience: RecoveryResilienceResult | None = None
    system_integrity: SystemIntegrityResult | None = None
    intent_alignment: IntentAlignmentResult | None = None
    strategic_arbitration: ArbitrationResult | None = None
    collective_consensus: ConsensusResult | None = None
    behavioral_stability: BehavioralStabilityResult | None = None
    tactical_execution: TacticalExecutionResult | None = None
    reward_evaluation: RewardEvaluationResult | None = None
    horizon: PlanningHorizon = PlanningHorizon.WEEKLY


@dataclass(frozen=True)
class PlanningEvent:
    """Auditable planning event."""

    decision: PlanningDecision
    horizon: PlanningHorizon
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class LongHorizonPlanningResult:
    """Final long-horizon planning result."""

    horizon: PlanningHorizon
    decision: PlanningDecision
    projection_confidence: int
    scenarios: tuple[FutureScenario, ...]
    projection: FutureProjection
    trajectory: StrategicTrajectory
    risks: tuple[PlanningRisk, ...]
    plan_graph: HorizonPlanGraph
    recommendations: tuple[PlanningRecommendation, ...]
    events: tuple[PlanningEvent, ...]
    summary: str


__all__ = [
    "FutureProjection",
    "FutureScenario",
    "FutureScenarioType",
    "HorizonPlanGraph",
    "LongHorizonPlanningInput",
    "LongHorizonPlanningResult",
    "PlanningDecision",
    "PlanningEvent",
    "PlanningHorizon",
    "PlanningRecommendation",
    "PlanningRisk",
    "StrategicTrajectory",
]
