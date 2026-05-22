"""Models for the offline Autonomous Adaptive Strategy Evolution Engine."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .adaptive_policy_memory_models import AdaptivePolicyMemory
from .behavioral_stability_models import BehavioralStabilityResult
from .collective_consensus_models import ConsensusResult
from .global_orchestrator_models import CoordinationResult, GlobalOrchestratorResult, SystemHealthSnapshot
from .intent_alignment_models import IntentAlignmentResult
from .learning_governance_models import LearningGovernanceResult
from .long_horizon_planning_models import LongHorizonPlanningResult
from .reward_models import RewardEvaluationResult
from .scenario_forecast_models import ScenarioForecastResult
from .scenario_replay_models import ReplayArenaResult
from .strategic_arbitration_models import ArbitrationResult
from .strategic_planning_models import StrategicPlanningResult
from .strategy_dna_models import StrategyDNA
from .tactical_execution_models import TacticalExecutionResult


class StrategyEvolutionMode(StrEnum):
    """Operating mode for offline strategy evolution."""

    STABLE_PRESERVATION = "STABLE_PRESERVATION"
    CONTROLLED_EVOLUTION = "CONTROLLED_EVOLUTION"
    MUTATION_EXPERIMENT = "MUTATION_EXPERIMENT"
    CONSERVATIVE_ADAPTATION = "CONSERVATIVE_ADAPTATION"
    RECOVERY_EVOLUTION = "RECOVERY_EVOLUTION"
    FREEZE_EVOLUTION = "FREEZE_EVOLUTION"
    SAFE_ROLLBACK = "SAFE_ROLLBACK"
    REBUILD_STRATEGY = "REBUILD_STRATEGY"


class StrategyMutation(StrEnum):
    """Allowed offline-only mutation families."""

    RISK_REDUCTION_MUTATION = "RISK_REDUCTION_MUTATION"
    ENTRY_FILTER_MUTATION = "ENTRY_FILTER_MUTATION"
    EXIT_FILTER_MUTATION = "EXIT_FILTER_MUTATION"
    VOLATILITY_ADAPTATION_MUTATION = "VOLATILITY_ADAPTATION_MUTATION"
    BEHAVIOR_GUARD_MUTATION = "BEHAVIOR_GUARD_MUTATION"
    CONTEXT_FILTER_MUTATION = "CONTEXT_FILTER_MUTATION"
    POSITION_SIZING_MUTATION = "POSITION_SIZING_MUTATION"
    TIME_WINDOW_MUTATION = "TIME_WINDOW_MUTATION"
    POLICY_SELECTION_MUTATION = "POLICY_SELECTION_MUTATION"
    NO_MUTATION = "NO_MUTATION"


class StrategyEvolutionRisk(StrEnum):
    """Risks that can make strategy evolution unsafe."""

    STRATEGY_DRIFT = "STRATEGY_DRIFT"
    OVER_MUTATION = "OVER_MUTATION"
    FITNESS_DEGRADATION = "FITNESS_DEGRADATION"
    BEHAVIORAL_UNSAFE_EVOLUTION = "BEHAVIORAL_UNSAFE_EVOLUTION"
    ALIGNMENT_BREAK = "ALIGNMENT_BREAK"
    LOW_EVIDENCE_EVOLUTION = "LOW_EVIDENCE_EVOLUTION"
    REWARD_OVERFIT = "REWARD_OVERFIT"
    LOSS_OF_CORE_DNA = "LOSS_OF_CORE_DNA"
    UNSTABLE_LINEAGE = "UNSTABLE_LINEAGE"
    UNSAFE_POLICY_PROPAGATION = "UNSAFE_POLICY_PROPAGATION"


class StrategyEvolutionDecision(StrEnum):
    """Final controlled evolution decision."""

    KEEP_CURRENT_STRATEGY = "KEEP_CURRENT_STRATEGY"
    APPLY_CONTROLLED_MUTATION = "APPLY_CONTROLLED_MUTATION"
    TEST_MUTATION_OFFLINE = "TEST_MUTATION_OFFLINE"
    FREEZE_STRATEGY_EVOLUTION = "FREEZE_STRATEGY_EVOLUTION"
    ROLLBACK_TO_STABLE_GENERATION = "ROLLBACK_TO_STABLE_GENERATION"
    REQUIRE_MORE_EVIDENCE = "REQUIRE_MORE_EVIDENCE"
    REBUILD_STRATEGY_FAMILY = "REBUILD_STRATEGY_FAMILY"
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"


class StrategyEvolutionRecommendation(StrEnum):
    """Recommended controls around strategy evolution."""

    PRESERVE_STRATEGY_DNA = "PRESERVE_STRATEGY_DNA"
    REDUCE_MUTATION_SCOPE = "REDUCE_MUTATION_SCOPE"
    TEST_IN_REPLAY_ARENA = "TEST_IN_REPLAY_ARENA"
    EXTEND_VALIDATION_WINDOW = "EXTEND_VALIDATION_WINDOW"
    FREEZE_POLICY_EXPANSION = "FREEZE_POLICY_EXPANSION"
    APPLY_RISK_REDUCTION = "APPLY_RISK_REDUCTION"
    ROLLBACK_UNSTABLE_VARIANT = "ROLLBACK_UNSTABLE_VARIANT"
    UPDATE_STRATEGY_MEMORY = "UPDATE_STRATEGY_MEMORY"
    COMPARE_GENERATIONS = "COMPARE_GENERATIONS"
    CONTINUE_STABLE_STRATEGY = "CONTINUE_STABLE_STRATEGY"


@dataclass(frozen=True)
class StrategyGeneration:
    """One strategy generation tracked by the offline lineage."""

    generation_id: str
    strategy_name: str
    version: int
    fitness_score: int
    mutations: tuple[StrategyMutation, ...] = ()
    parent_generation_id: str | None = None
    preserved_core_dna: bool = True
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class StrategyFitnessScore:
    """Component fitness scores normalized to 0..100."""

    performance_score: int
    risk_control_score: int
    dna_preservation_score: int
    behavioral_safety_score: int
    alignment_score: int
    evidence_score: int
    lineage_stability_score: int


@dataclass(frozen=True)
class StrategyLineageGraph:
    """Explainable graph of generations and mutation paths."""

    nodes: tuple[str, ...]
    edges: tuple[tuple[str, str, str], ...]
    stable_generations: tuple[str, ...]
    unstable_generations: tuple[str, ...]
    current_generation_id: str
    recommended_parent_id: str | None = None


@dataclass(frozen=True)
class StrategyEvolutionInput:
    """Inputs consumed by the offline strategy evolution engine."""

    scenario_forecast: ScenarioForecastResult | None = None
    long_horizon_plan: LongHorizonPlanningResult | None = None
    global_orchestrator: GlobalOrchestratorResult | None = None
    coordination_result: CoordinationResult | None = None
    health_snapshot: SystemHealthSnapshot | None = None
    strategic_result: StrategicPlanningResult | None = None
    policy_memory: AdaptivePolicyMemory | None = None
    strategy_dna: StrategyDNA | None = None
    reward_evaluation: RewardEvaluationResult | None = None
    tactical_execution: TacticalExecutionResult | None = None
    behavioral_stability: BehavioralStabilityResult | None = None
    intent_alignment: IntentAlignmentResult | None = None
    learning_governance: LearningGovernanceResult | None = None
    collective_consensus: ConsensusResult | None = None
    strategic_arbitration: ArbitrationResult | None = None
    replay_arena: ReplayArenaResult | None = None
    previous_generations: tuple[StrategyGeneration, ...] = ()


@dataclass(frozen=True)
class StrategyEvolutionEvent:
    """Auditable strategy evolution event."""

    decision: StrategyEvolutionDecision
    mode: StrategyEvolutionMode
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class StrategyEvolutionResult:
    """Final strategy evolution result."""

    mode: StrategyEvolutionMode
    decision: StrategyEvolutionDecision
    current_generation: StrategyGeneration
    fitness_score: int
    fitness_breakdown: StrategyFitnessScore
    proposed_mutations: tuple[StrategyMutation, ...]
    risks: tuple[StrategyEvolutionRisk, ...]
    lineage_graph: StrategyLineageGraph
    recommendations: tuple[StrategyEvolutionRecommendation, ...]
    preserved_core_dna: bool
    events: tuple[StrategyEvolutionEvent, ...]
    summary: str


__all__ = [
    "StrategyEvolutionDecision",
    "StrategyEvolutionEvent",
    "StrategyEvolutionInput",
    "StrategyEvolutionMode",
    "StrategyEvolutionRecommendation",
    "StrategyEvolutionResult",
    "StrategyEvolutionRisk",
    "StrategyFitnessScore",
    "StrategyGeneration",
    "StrategyLineageGraph",
    "StrategyMutation",
]
