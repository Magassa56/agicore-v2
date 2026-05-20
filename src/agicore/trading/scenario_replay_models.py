"""Models for the offline scenario replay arena."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .autonomous_simulation_models import AutonomousSimulationConfig, AutonomousSimulationResult
from .behavior_models import BehaviorAnalysisResult
from .strategy_dna_models import StrategyDNA


class ReplayScenarioType(StrEnum):
    """Supported offline market/session replay scenario types."""

    TREND_DAY = "TREND_DAY"
    RANGE_DAY = "RANGE_DAY"
    CHOPPY_DAY = "CHOPPY_DAY"
    HIGH_VOLATILITY_DAY = "HIGH_VOLATILITY_DAY"
    LOW_VOLATILITY_DAY = "LOW_VOLATILITY_DAY"
    BREAKOUT_DAY = "BREAKOUT_DAY"
    REVERSAL_DAY = "REVERSAL_DAY"
    NEWS_RISK_DAY = "NEWS_RISK_DAY"
    DEAD_MARKET_DAY = "DEAD_MARKET_DAY"
    REVENGE_RISK_SESSION = "REVENGE_RISK_SESSION"
    DISCIPLINED_SESSION = "DISCIPLINED_SESSION"
    CUSTOM = "CUSTOM"


class ReplayArenaStatus(StrEnum):
    """Final arena status after replaying one or more scenarios."""

    COMPLETED = "COMPLETED"
    COMPLETED_WITH_RISKS = "COMPLETED_WITH_RISKS"
    BLOCKED_BY_SAFETY = "BLOCKED_BY_SAFETY"
    NO_SCENARIOS = "NO_SCENARIOS"


@dataclass(frozen=True)
class ReplayScenarioStep:
    """One generated or custom replay step."""

    step_id: str
    prices: tuple[float, ...]
    ema_fast: tuple[float, ...]
    ema_slow: tuple[float, ...]
    atr: tuple[float, ...]
    ranges: tuple[float, ...]
    volume: tuple[float, ...] = ()
    hour_of_day: int | None = None


@dataclass(frozen=True)
class ReplayScenario:
    """Scenario definition consumed by the replay arena."""

    name: str
    scenario_type: ReplayScenarioType
    steps: tuple[ReplayScenarioStep, ...]
    strategy_dna: StrategyDNA | None = None
    behavior_result: BehaviorAnalysisResult | None = None
    config: AutonomousSimulationConfig | None = None
    description: str = ""


@dataclass(frozen=True)
class ReplayScenarioResult:
    """Replay result and robustness metrics for one scenario."""

    scenario: ReplayScenario
    simulation_result: AutonomousSimulationResult
    scenario_score: int
    total_reward: int
    average_reward: float
    executed_orders: int
    blocked_orders: int
    dangerous_decisions: int
    safe_rl_blocks: int
    risks_detected: tuple[str, ...]
    recommendations: tuple[str, ...]


@dataclass(frozen=True)
class ReplayArenaResult:
    """Aggregated result for multiple replayed scenarios."""

    scenario_results: tuple[ReplayScenarioResult, ...]
    best_scenario: ReplayScenarioResult | None
    worst_scenario: ReplayScenarioResult | None
    robustness_score: int
    total_reward: int
    average_reward: float
    executed_orders: int
    blocked_orders: int
    dangerous_decisions: int
    safe_rl_blocks: int
    status: ReplayArenaStatus
    risks_detected: tuple[str, ...]
    recommendations: tuple[str, ...]


__all__ = [
    "ReplayArenaResult",
    "ReplayArenaStatus",
    "ReplayScenario",
    "ReplayScenarioResult",
    "ReplayScenarioStep",
    "ReplayScenarioType",
]
