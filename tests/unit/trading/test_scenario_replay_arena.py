"""Unit tests for the offline scenario replay arena."""
from __future__ import annotations

from agicore.trading.autonomous_simulation_models import AutonomousSimulationConfig
from agicore.trading.scenario_replay_arena import (
    build_replay_scenario,
    compare_replay_scenarios,
    render_replay_arena_markdown,
    run_replay_arena,
    run_replay_scenario,
)
from agicore.trading.scenario_replay_models import (
    ReplayArenaStatus,
    ReplayScenarioStep,
    ReplayScenarioType,
)


def test_build_replay_scenario_creates_deterministic_steps() -> None:
    scenario = build_replay_scenario(ReplayScenarioType.TREND_DAY, steps_count=3)

    assert scenario.name == "TREND_DAY"
    assert scenario.scenario_type == ReplayScenarioType.TREND_DAY
    assert len(scenario.steps) == 3
    assert scenario.strategy_dna is not None
    assert scenario.behavior_result is not None


def test_build_replay_scenario_supports_custom_steps() -> None:
    step = ReplayScenarioStep(
        step_id="custom-1",
        prices=(100, 101, 102),
        ema_fast=(100.5, 101.5, 102.5),
        ema_slow=(99.5, 100.5, 101.5),
        atr=(1, 1, 1),
        ranges=(1, 1, 1),
    )

    scenario = build_replay_scenario(
        ReplayScenarioType.CUSTOM,
        name="custom",
        custom_steps=(step,),
    )

    assert scenario.name == "custom"
    assert scenario.steps == (step,)


def test_run_replay_scenario_returns_metrics() -> None:
    scenario = build_replay_scenario(ReplayScenarioType.TREND_DAY, steps_count=2)

    result = run_replay_scenario(
        scenario,
        config=AutonomousSimulationConfig(max_steps=3, max_orders=3),
    )

    assert result.scenario == scenario
    assert 0 <= result.scenario_score <= 100
    assert result.simulation_result.total_steps >= 1
    assert result.total_reward == result.simulation_result.total_reward
    assert result.executed_orders >= 0


def test_run_replay_scenario_detects_risky_news_day() -> None:
    scenario = build_replay_scenario(ReplayScenarioType.NEWS_RISK_DAY, steps_count=2)

    result = run_replay_scenario(scenario)

    assert result.safe_rl_blocks >= 1
    assert result.blocked_orders >= 1
    assert result.risks_detected


def test_run_replay_arena_compares_best_and_worst() -> None:
    scenarios = (
        build_replay_scenario(ReplayScenarioType.TREND_DAY, steps_count=2),
        build_replay_scenario(ReplayScenarioType.NEWS_RISK_DAY, steps_count=2),
        build_replay_scenario(ReplayScenarioType.DISCIPLINED_SESSION, steps_count=2),
    )

    result = run_replay_arena(scenarios)

    assert result.status in {ReplayArenaStatus.COMPLETED, ReplayArenaStatus.COMPLETED_WITH_RISKS}
    assert len(result.scenario_results) == 3
    assert result.best_scenario is not None
    assert result.worst_scenario is not None
    assert result.best_scenario.scenario_score >= result.worst_scenario.scenario_score
    assert 0 <= result.robustness_score <= 100


def test_compare_replay_scenarios_handles_empty_input() -> None:
    result = compare_replay_scenarios(())

    assert result.status == ReplayArenaStatus.NO_SCENARIOS
    assert result.best_scenario is None
    assert result.worst_scenario is None
    assert result.robustness_score == 0


def test_render_replay_arena_markdown_contains_required_sections() -> None:
    arena = run_replay_arena(
        (
            build_replay_scenario(ReplayScenarioType.TREND_DAY, steps_count=1),
            build_replay_scenario(ReplayScenarioType.DEAD_MARKET_DAY, steps_count=1),
        )
    )

    markdown = render_replay_arena_markdown(arena)

    assert "# Scenario Replay Arena" in markdown
    assert "## Resume Arena" in markdown
    assert "## Scenarios testes" in markdown
    assert "## Meilleur scenario" in markdown
    assert "## Pire scenario" in markdown
    assert "## Robustesse globale" in markdown
    assert "## Risques detectes" in markdown
    assert "## Recommandations AGIcore" in markdown
    assert "## Limites offline" in markdown
    assert "no broker" in markdown
