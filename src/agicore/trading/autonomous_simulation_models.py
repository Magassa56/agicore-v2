"""Models for the offline autonomous trading simulation core."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from .adaptive_policy_memory_models import AdaptivePolicyMemory
from .behavior_models import BehaviorAnalysisResult
from .context_scoring_models import ContextScoringResult
from .market_regime_models import MarketRegimeAnalysis
from .meta_strategy_models import MetaStrategySelectionResult
from .offline_dataset_models import OfflineLearningDataset, LearningTransition
from .paper_execution_models import PaperExecutionResult
from .paper_trading_models import PaperOrderRequest
from .reward_models import RewardEvaluationResult
from .safe_rl_models import SafeRLExperimentConfig, SafeRLExperimentResult
from .semi_auto_decision_models import SemiAutoDecisionResult
from .strategy_dna_models import StrategyDNA


class AutonomousSimulationStatus(StrEnum):
    """Final status for the offline autonomous simulation."""

    COMPLETED = "COMPLETED"
    STOPPED_SAFE_RL_BLOCKED = "STOPPED_SAFE_RL_BLOCKED"
    STOPPED_MAX_STEPS = "STOPPED_MAX_STEPS"
    STOPPED_MAX_ORDERS = "STOPPED_MAX_ORDERS"
    STOPPED_DAILY_LOSS_LIMIT = "STOPPED_DAILY_LOSS_LIMIT"
    STOPPED_SESSION = "STOPPED_SESSION"
    NO_STEPS = "NO_STEPS"


class AutonomousSimulationEventType(StrEnum):
    """Auditable events emitted by the offline simulation loop."""

    SIMULATION_STARTED = "SIMULATION_STARTED"
    STEP_STARTED = "STEP_STARTED"
    MARKET_REGIME_DETECTED = "MARKET_REGIME_DETECTED"
    CONTEXT_SCORED = "CONTEXT_SCORED"
    META_STRATEGY_SELECTED = "META_STRATEGY_SELECTED"
    SEMI_AUTO_DECISION_BUILT = "SEMI_AUTO_DECISION_BUILT"
    PAPER_EXECUTION_SKIPPED = "PAPER_EXECUTION_SKIPPED"
    PAPER_EXECUTION_COMPLETED = "PAPER_EXECUTION_COMPLETED"
    REWARD_EVALUATED = "REWARD_EVALUATED"
    LEARNING_TRANSITION_BUILT = "LEARNING_TRANSITION_BUILT"
    POLICY_MEMORY_UPDATED = "POLICY_MEMORY_UPDATED"
    SAFE_RL_VALIDATED = "SAFE_RL_VALIDATED"
    GUARDRAIL_STOP = "GUARDRAIL_STOP"
    SIMULATION_COMPLETED = "SIMULATION_COMPLETED"


@dataclass(frozen=True)
class AutonomousSimulationConfig:
    """Configuration for the offline autonomous trading simulation."""

    max_steps: int = 10
    max_orders: int = 3
    daily_loss_limit: float = 500.0
    default_order_quantity: float = 1.0
    trading_enabled: bool = True
    risk_allowed: bool = True
    allow_high_risk_override: bool = False
    safe_rl_config: SafeRLExperimentConfig = field(
        default_factory=lambda: SafeRLExperimentConfig(
            min_dataset_quality_score=0,
            min_transitions_count=0,
        )
    )


@dataclass(frozen=True)
class AutonomousSimulationStep:
    """One simulated context snapshot and its offline outputs."""

    step_id: str
    prices: tuple[float, ...] = ()
    ema_fast: tuple[float, ...] = ()
    ema_slow: tuple[float, ...] = ()
    atr: tuple[float, ...] = ()
    ranges: tuple[float, ...] = ()
    volume: tuple[float, ...] = ()
    timestamps: tuple[datetime, ...] = ()
    order_request: PaperOrderRequest | None = None
    market_regime: MarketRegimeAnalysis | None = None
    context_score: ContextScoringResult | None = None
    behavior_result: BehaviorAnalysisResult | None = None
    strategy_dna: StrategyDNA | None = None
    hour_of_day: int | None = None
    session_trade_count: int = 0
    meta_strategy_result: MetaStrategySelectionResult | None = None
    semi_auto_decision: SemiAutoDecisionResult | None = None
    paper_execution_result: PaperExecutionResult | None = None
    reward_result: RewardEvaluationResult | None = None
    learning_transition: LearningTransition | None = None
    safe_rl_result: SafeRLExperimentResult | None = None


@dataclass(frozen=True)
class AutonomousSimulationEvent:
    """One auditable event emitted by the offline autonomous loop."""

    event_type: AutonomousSimulationEventType
    message: str
    step_id: str | None
    timestamp: datetime


@dataclass(frozen=True)
class AutonomousSimulationResult:
    """Complete result from an offline autonomous trading simulation."""

    total_steps: int
    executed_orders: int
    blocked_orders: int
    total_reward: int
    average_reward: float
    final_policy_memory: AdaptivePolicyMemory
    learning_dataset: OfflineLearningDataset
    event_log: tuple[AutonomousSimulationEvent, ...]
    status: AutonomousSimulationStatus
    safe_rl_result: SafeRLExperimentResult | None = None
    steps: tuple[AutonomousSimulationStep, ...] = ()
    safety_message: str = (
        "Offline autonomous simulation only. No broker, API, external ML, neural training, "
        "NinjaTrader, Alpaca, Binance, Rithmic or Tradovate connection is used. No real order is sent."
    )


__all__ = [
    "AutonomousSimulationConfig",
    "AutonomousSimulationEvent",
    "AutonomousSimulationEventType",
    "AutonomousSimulationResult",
    "AutonomousSimulationStatus",
    "AutonomousSimulationStep",
]
