"""Offline scenario replay arena for AGIcore Trading."""
from __future__ import annotations

from statistics import mean
from typing import Iterable

from .autonomous_simulation import run_autonomous_trading_simulation
from .autonomous_simulation_models import (
    AutonomousSimulationConfig,
    AutonomousSimulationStatus,
    AutonomousSimulationStep,
)
from .behavior_models import (
    BehaviorAnalysisResult,
    BehaviorRecommendation,
    BehaviorScores,
    BehaviorSummary,
    SessionBehaviorClass,
)
from .paper_trading_models import PaperOrderRequest, PaperOrderSide
from .reward_models import RewardLabel
from .safe_rl_models import SafeRLStatus
from .scenario_replay_models import (
    ReplayArenaResult,
    ReplayArenaStatus,
    ReplayScenario,
    ReplayScenarioResult,
    ReplayScenarioStep,
    ReplayScenarioType,
)
from .strategy_dna_models import StrategyDNA, TradeDirection


def build_replay_scenario(
    scenario_type: ReplayScenarioType | str,
    *,
    name: str | None = None,
    steps_count: int = 4,
    strategy_dna: StrategyDNA | None = None,
    behavior_result: BehaviorAnalysisResult | None = None,
    config: AutonomousSimulationConfig | None = None,
    custom_steps: Iterable[ReplayScenarioStep] = (),
    description: str = "",
) -> ReplayScenario:
    """Build a deterministic offline replay scenario."""
    resolved_type = scenario_type if isinstance(scenario_type, ReplayScenarioType) else ReplayScenarioType(str(scenario_type))
    steps = tuple(custom_steps) if resolved_type == ReplayScenarioType.CUSTOM and tuple(custom_steps) else _scenario_steps(resolved_type, steps_count)
    return ReplayScenario(
        name=name or resolved_type.value,
        scenario_type=resolved_type,
        steps=steps,
        strategy_dna=strategy_dna or _default_strategy(),
        behavior_result=behavior_result or _default_behavior(resolved_type),
        config=config,
        description=description or f"Offline replay scenario: {resolved_type.value}",
    )


def run_replay_scenario(
    scenario: ReplayScenario,
    *,
    config: AutonomousSimulationConfig | None = None,
) -> ReplayScenarioResult:
    """Run one scenario through the autonomous simulation core."""
    simulation_steps = tuple(_to_simulation_step(scenario, step) for step in scenario.steps)
    simulation = run_autonomous_trading_simulation(
        simulation_steps,
        config=config or scenario.config or _default_config(),
    )
    dangerous = _dangerous_decision_count(simulation)
    safe_blocks = sum(1 for step in simulation.steps if step.safe_rl_result is not None and step.safe_rl_result.status == SafeRLStatus.BLOCKED)
    risks = _scenario_risks(
        scenario=scenario,
        simulation=simulation,
        dangerous_decisions=dangerous,
        safe_rl_blocks=safe_blocks,
    )
    score = _scenario_score(
        scenario=scenario,
        simulation=simulation,
        dangerous_decisions=dangerous,
        safe_rl_blocks=safe_blocks,
    )
    return ReplayScenarioResult(
        scenario=scenario,
        simulation_result=simulation,
        scenario_score=score,
        total_reward=simulation.total_reward,
        average_reward=simulation.average_reward,
        executed_orders=simulation.executed_orders,
        blocked_orders=simulation.blocked_orders,
        dangerous_decisions=dangerous,
        safe_rl_blocks=safe_blocks,
        risks_detected=risks,
        recommendations=_scenario_recommendations(score, risks),
    )


def run_replay_arena(
    scenarios: Iterable[ReplayScenario],
    *,
    config: AutonomousSimulationConfig | None = None,
) -> ReplayArenaResult:
    """Replay several scenarios and aggregate robustness metrics."""
    results = tuple(run_replay_scenario(scenario, config=config) for scenario in scenarios)
    return compare_replay_scenarios(results)


def compare_replay_scenarios(
    scenario_results: Iterable[ReplayScenarioResult],
) -> ReplayArenaResult:
    """Compare scenario results and compute global robustness."""
    results = tuple(scenario_results)
    if not results:
        return ReplayArenaResult(
            scenario_results=(),
            best_scenario=None,
            worst_scenario=None,
            robustness_score=0,
            total_reward=0,
            average_reward=0.0,
            executed_orders=0,
            blocked_orders=0,
            dangerous_decisions=0,
            safe_rl_blocks=0,
            status=ReplayArenaStatus.NO_SCENARIOS,
            risks_detected=("No replay scenario provided.",),
            recommendations=("Build at least one offline scenario before comparing robustness.",),
        )
    best = max(results, key=lambda item: item.scenario_score)
    worst = min(results, key=lambda item: item.scenario_score)
    total_reward = sum(item.total_reward for item in results)
    dangerous = sum(item.dangerous_decisions for item in results)
    safe_blocks = sum(item.safe_rl_blocks for item in results)
    risks = tuple(dict.fromkeys(risk for item in results for risk in item.risks_detected))
    robustness = _clamp(mean(item.scenario_score for item in results))
    status = _arena_status(results, dangerous, safe_blocks)
    return ReplayArenaResult(
        scenario_results=results,
        best_scenario=best,
        worst_scenario=worst,
        robustness_score=robustness,
        total_reward=total_reward,
        average_reward=round(mean(item.average_reward for item in results), 2),
        executed_orders=sum(item.executed_orders for item in results),
        blocked_orders=sum(item.blocked_orders for item in results),
        dangerous_decisions=dangerous,
        safe_rl_blocks=safe_blocks,
        status=status,
        risks_detected=risks,
        recommendations=_arena_recommendations(robustness, risks, status),
    )


def render_replay_arena_markdown(result: ReplayArenaResult) -> str:
    """Render the replay arena result as Markdown."""
    lines = [
        "# Scenario Replay Arena",
        "",
        "## Resume Arena",
        "",
        f"- Status: {result.status.value}",
        f"- Scenarios: {len(result.scenario_results)}",
        f"- Total reward: {result.total_reward}",
        "",
        "## Scenarios testes",
        "",
        "| Scenario | Type | Score | Reward | Orders | Blocked | Safe RL blocks |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
        *_scenario_lines(result.scenario_results),
        "",
        "## Meilleur scenario",
        "",
        f"- {_scenario_name(result.best_scenario)}",
        "",
        "## Pire scenario",
        "",
        f"- {_scenario_name(result.worst_scenario)}",
        "",
        "## Robustesse globale",
        "",
        f"- Score: {result.robustness_score}/100",
        "",
        "## Risques detectes",
        "",
        *_bullet_lines(result.risks_detected),
        "",
        "## Recommandations AGIcore",
        "",
        *_bullet_lines(result.recommendations),
        "",
        "## Limites offline",
        "",
        "- Offline scenario replay only: no broker, no real order, no external ML, no neural training.",
        "- No NinjaTrader, Alpaca, Binance, Rithmic or Tradovate connection is used.",
        "",
    ]
    return "\n".join(lines)


def _to_simulation_step(scenario: ReplayScenario, step: ReplayScenarioStep) -> AutonomousSimulationStep:
    return AutonomousSimulationStep(
        step_id=f"{scenario.name}:{step.step_id}",
        prices=step.prices,
        ema_fast=step.ema_fast,
        ema_slow=step.ema_slow,
        atr=step.atr,
        ranges=step.ranges,
        volume=step.volume,
        order_request=PaperOrderRequest(
            symbol="MES",
            side=PaperOrderSide.BUY,
            quantity=1,
            simulated_price=step.prices[-1] if step.prices else 100.0,
        ),
        behavior_result=scenario.behavior_result,
        strategy_dna=scenario.strategy_dna,
        hour_of_day=step.hour_of_day,
    )


def _scenario_steps(scenario_type: ReplayScenarioType, steps_count: int) -> tuple[ReplayScenarioStep, ...]:
    builders = {
        ReplayScenarioType.TREND_DAY: _trend_prices,
        ReplayScenarioType.RANGE_DAY: _range_prices,
        ReplayScenarioType.CHOPPY_DAY: _choppy_prices,
        ReplayScenarioType.HIGH_VOLATILITY_DAY: _high_vol_prices,
        ReplayScenarioType.LOW_VOLATILITY_DAY: _low_vol_prices,
        ReplayScenarioType.BREAKOUT_DAY: _breakout_prices,
        ReplayScenarioType.REVERSAL_DAY: _reversal_prices,
        ReplayScenarioType.NEWS_RISK_DAY: _news_prices,
        ReplayScenarioType.DEAD_MARKET_DAY: _dead_prices,
        ReplayScenarioType.REVENGE_RISK_SESSION: _choppy_prices,
        ReplayScenarioType.DISCIPLINED_SESSION: _trend_prices,
        ReplayScenarioType.CUSTOM: _range_prices,
    }
    builder = builders[scenario_type]
    return tuple(_step_from_prices(f"s{index + 1}", builder(index), scenario_type, index) for index in range(max(1, steps_count)))


def _step_from_prices(
    step_id: str,
    prices: tuple[float, ...],
    scenario_type: ReplayScenarioType,
    index: int,
) -> ReplayScenarioStep:
    ema_fast = tuple(price + _ema_gap(scenario_type) for price in prices)
    ema_slow = tuple(price - _ema_gap(scenario_type) for price in prices)
    atr_base = _atr_base(scenario_type)
    atr = tuple(atr_base for _ in prices[:-1]) + (atr_base * _atr_last_multiplier(scenario_type),)
    ranges = tuple(atr_base * 1.1 for _ in prices[:-1]) + (atr_base * _range_last_multiplier(scenario_type),)
    volume = tuple(100.0 for _ in prices[:-1]) + (100.0 * _volume_last_multiplier(scenario_type),)
    return ReplayScenarioStep(
        step_id=step_id,
        prices=prices,
        ema_fast=ema_fast,
        ema_slow=ema_slow,
        atr=atr,
        ranges=ranges,
        volume=volume,
        hour_of_day=10 + index,
    )


def _trend_prices(index: int) -> tuple[float, ...]:
    base = 100.0 + index * 2
    return (base, base + 1, base + 2, base + 3, base + 4)


def _range_prices(index: int) -> tuple[float, ...]:
    base = 100.0 + index * 0.1
    return (base, base + 0.2, base - 0.1, base + 0.1, base)


def _choppy_prices(index: int) -> tuple[float, ...]:
    base = 100.0 + index * 0.2
    return (base, base + 1.0, base - 0.8, base + 0.9, base - 0.7)


def _high_vol_prices(index: int) -> tuple[float, ...]:
    base = 100.0 + index
    return (base, base + 2.5, base - 2.0, base + 3.5, base + 1.0)


def _low_vol_prices(index: int) -> tuple[float, ...]:
    base = 100.0 + index * 0.05
    return (base, base + 0.04, base + 0.02, base + 0.05, base + 0.03)


def _breakout_prices(index: int) -> tuple[float, ...]:
    base = 100.0 + index
    return (base, base + 0.2, base + 0.1, base + 0.3, base + 3.0)


def _reversal_prices(index: int) -> tuple[float, ...]:
    base = 104.0 - index
    return (base, base - 1.0, base - 2.0, base - 1.0, base + 1.0)


def _news_prices(index: int) -> tuple[float, ...]:
    base = 100.0 + index
    return (base, base + 0.5, base - 0.4, base + 0.2, base + 5.5)


def _dead_prices(index: int) -> tuple[float, ...]:
    base = 100.0 + index * 0.01
    return (base, base + 0.01, base, base + 0.01, base)


def _ema_gap(scenario_type: ReplayScenarioType) -> float:
    if scenario_type in {ReplayScenarioType.CHOPPY_DAY, ReplayScenarioType.RANGE_DAY, ReplayScenarioType.DEAD_MARKET_DAY}:
        return 0.02
    return 0.4


def _atr_base(scenario_type: ReplayScenarioType) -> float:
    if scenario_type == ReplayScenarioType.LOW_VOLATILITY_DAY:
        return 0.2
    if scenario_type == ReplayScenarioType.DEAD_MARKET_DAY:
        return 0.05
    if scenario_type in {ReplayScenarioType.HIGH_VOLATILITY_DAY, ReplayScenarioType.NEWS_RISK_DAY}:
        return 2.0
    return 1.0


def _atr_last_multiplier(scenario_type: ReplayScenarioType) -> float:
    if scenario_type == ReplayScenarioType.NEWS_RISK_DAY:
        return 2.5
    if scenario_type == ReplayScenarioType.HIGH_VOLATILITY_DAY:
        return 1.8
    if scenario_type in {ReplayScenarioType.LOW_VOLATILITY_DAY, ReplayScenarioType.DEAD_MARKET_DAY}:
        return 0.5
    return 1.0


def _range_last_multiplier(scenario_type: ReplayScenarioType) -> float:
    if scenario_type in {ReplayScenarioType.NEWS_RISK_DAY, ReplayScenarioType.BREAKOUT_DAY}:
        return 2.4
    if scenario_type == ReplayScenarioType.HIGH_VOLATILITY_DAY:
        return 1.8
    return _atr_last_multiplier(scenario_type)


def _volume_last_multiplier(scenario_type: ReplayScenarioType) -> float:
    if scenario_type == ReplayScenarioType.NEWS_RISK_DAY:
        return 2.5
    if scenario_type == ReplayScenarioType.DEAD_MARKET_DAY:
        return 0.5
    return 1.0


def _default_behavior(scenario_type: ReplayScenarioType) -> BehaviorAnalysisResult:
    if scenario_type == ReplayScenarioType.REVENGE_RISK_SESSION:
        classes = (SessionBehaviorClass.REVENGE_TRADING_PROBABLE, SessionBehaviorClass.HIGH_RISK)
        emotional = 85
        risk = 90
        recs = (BehaviorRecommendation.STOP_TRADING,)
    elif scenario_type == ReplayScenarioType.DISCIPLINED_SESSION:
        classes = (SessionBehaviorClass.DISCIPLINED, SessionBehaviorClass.CONSISTENT)
        emotional = 65
        risk = 20
        recs = (BehaviorRecommendation.KEEP_CURRENT_RULES,)
    else:
        classes = (SessionBehaviorClass.DISCIPLINED,)
        emotional = 65
        risk = 25
        recs = (BehaviorRecommendation.KEEP_CURRENT_RULES,)
    return BehaviorAnalysisResult(
        classifications=classes,
        patterns=(),
        scores=BehaviorScores(
            discipline_score=80,
            emotional_risk_score=emotional,
            consistency_score=80,
            risk_escalation_score=risk,
        ),
        recommendations=recs,
        summary=BehaviorSummary(
            strengths=("offline scenario control",),
            weaknesses=(),
            dangerous_hours=(),
            favorable_context="scenario",
            probable_trader_profile="simulated",
        ),
    )


def _default_strategy() -> StrategyDNA:
    return StrategyDNA(
        name="EMA20",
        description="Offline EMA20 replay strategy",
        allowed_direction=TradeDirection.BOTH,
        ema_filter="EMA20 pullback",
    )


def _default_config() -> AutonomousSimulationConfig:
    return AutonomousSimulationConfig(max_steps=10, max_orders=3)


def _dangerous_decision_count(simulation) -> int:
    return sum(
        1
        for step in simulation.steps
        if step.reward_result is not None and step.reward_result.reward_label == RewardLabel.DANGEROUS_DECISION
    )


def _scenario_score(
    *,
    scenario: ReplayScenario,
    simulation,
    dangerous_decisions: int,
    safe_rl_blocks: int,
) -> int:
    score = 60 + simulation.average_reward / 4
    score += min(15, simulation.blocked_orders * 5) if _should_block(scenario.scenario_type) else min(15, simulation.executed_orders * 5)
    score -= dangerous_decisions * 20
    score -= safe_rl_blocks * 10
    if simulation.status == AutonomousSimulationStatus.STOPPED_SAFE_RL_BLOCKED and not _should_block(scenario.scenario_type):
        score -= 20
    if simulation.executed_orders > max(3, len(scenario.steps)):
        score -= 20
    return _clamp(score)


def _scenario_risks(
    *,
    scenario: ReplayScenario,
    simulation,
    dangerous_decisions: int,
    safe_rl_blocks: int,
) -> tuple[str, ...]:
    risks: list[str] = []
    if dangerous_decisions:
        risks.append(f"{scenario.name}: dangerous reward labels detected.")
    if safe_rl_blocks:
        risks.append(f"{scenario.name}: Safe RL blocked the replay.")
    if _should_block(scenario.scenario_type) and simulation.executed_orders:
        risks.append(f"{scenario.name}: executed orders in a scenario that should favor blocking.")
    if not _should_block(scenario.scenario_type) and simulation.blocked_orders > simulation.executed_orders:
        risks.append(f"{scenario.name}: excessive blocking in a tradable scenario.")
    if simulation.executed_orders >= 3 and scenario.scenario_type in {ReplayScenarioType.CHOPPY_DAY, ReplayScenarioType.RANGE_DAY}:
        risks.append(f"{scenario.name}: possible overtrading in non-directional conditions.")
    return tuple(dict.fromkeys(risks))


def _scenario_recommendations(score: int, risks: tuple[str, ...]) -> tuple[str, ...]:
    if score >= 75 and not risks:
        return ("Scenario behavior is robust enough for offline comparison.",)
    items = ["Review replay decisions before using this scenario for policy prioritization."]
    if risks:
        items.append("Inspect blocked/executed order balance and Safe RL guardrails.")
    return tuple(items)


def _arena_status(
    results: tuple[ReplayScenarioResult, ...],
    dangerous_decisions: int,
    safe_rl_blocks: int,
) -> ReplayArenaStatus:
    if safe_rl_blocks and all(item.safe_rl_blocks for item in results):
        return ReplayArenaStatus.BLOCKED_BY_SAFETY
    if dangerous_decisions or safe_rl_blocks or any(item.risks_detected for item in results):
        return ReplayArenaStatus.COMPLETED_WITH_RISKS
    return ReplayArenaStatus.COMPLETED


def _arena_recommendations(
    robustness: int,
    risks: tuple[str, ...],
    status: ReplayArenaStatus,
) -> tuple[str, ...]:
    if status == ReplayArenaStatus.NO_SCENARIOS:
        return ("Build scenarios before running the arena.",)
    items: list[str] = []
    if robustness >= 75 and not risks:
        items.append("Current offline policy behavior is robust across replay scenarios.")
    else:
        items.append("Use worst-scenario diagnostics to tighten policy selection and risk gates.")
    if risks:
        items.append("Review risky scenarios before future offline RL or policy memory updates.")
    items.append("Keep all replay analysis offline; do not connect brokers or route orders.")
    return tuple(dict.fromkeys(items))


def _should_block(scenario_type: ReplayScenarioType) -> bool:
    return scenario_type in {
        ReplayScenarioType.CHOPPY_DAY,
        ReplayScenarioType.HIGH_VOLATILITY_DAY,
        ReplayScenarioType.NEWS_RISK_DAY,
        ReplayScenarioType.DEAD_MARKET_DAY,
        ReplayScenarioType.REVENGE_RISK_SESSION,
    }


def _scenario_lines(results: tuple[ReplayScenarioResult, ...]) -> list[str]:
    if not results:
        return ["| None | None | 0 | 0 | 0 | 0 | 0 |"]
    return [
        (
            f"| {item.scenario.name} | {item.scenario.scenario_type.value} | {item.scenario_score} | "
            f"{item.total_reward} | {item.executed_orders} | {item.blocked_orders} | {item.safe_rl_blocks} |"
        )
        for item in results
    ]


def _scenario_name(result: ReplayScenarioResult | None) -> str:
    if result is None:
        return "None"
    return f"{result.scenario.name} ({result.scenario_score}/100)"


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _clamp(value: int | float) -> int:
    return max(0, min(100, int(round(value))))


__all__ = [
    "build_replay_scenario",
    "compare_replay_scenarios",
    "render_replay_arena_markdown",
    "run_replay_arena",
    "run_replay_scenario",
]
