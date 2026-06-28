from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agicore.trading.controlled_offline_runner_minimal_models import (
    ControlledOfflineSyntheticMarketScenario,
)
from agicore.trading.synthetic_market_scenario_v1 import (
    assert_synthetic_market_scenario_v1_offline_boundaries,
    build_synthetic_market_scenario_v1,
    compute_synthetic_market_scenario_statistics,
    convert_synthetic_market_scenario_to_controlled_offline_runner_scenario,
    detect_synthetic_market_scenario_v1_risks,
    generate_synthetic_calm_market_scenario,
    generate_synthetic_gap_scenario,
    generate_synthetic_market_scenario_v1_recommendations,
    generate_synthetic_range_bound_scenario,
    generate_synthetic_trend_down_scenario,
    generate_synthetic_trend_up_scenario,
    generate_synthetic_volatility_spike_scenario,
    render_synthetic_market_scenario_v1_json_report,
    render_synthetic_market_scenario_v1_markdown_report,
    validate_synthetic_market_bars,
    validate_synthetic_market_ohlcv_consistency,
    validate_synthetic_market_scenario_v1_input,
)
from agicore.trading.synthetic_market_scenario_v1_models import (
    SyntheticMarketBarV1,
    SyntheticMarketScenarioV1Decision,
    SyntheticMarketScenarioV1Input,
    SyntheticMarketScenarioV1Profile,
    SyntheticMarketScenarioV1Recommendation,
    SyntheticMarketScenarioV1Risk,
    SyntheticMarketScenarioV1State,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/synthetic_market_scenario_v1.py"


def _input(profile=SyntheticMarketScenarioV1Profile.TREND_UP, **overrides):
    payload = {
        "profile": profile,
        "scenario_id": f"scenario-{str(profile).lower()}",
        "symbol": "SIM",
        "bar_count": 8,
        "initial_price": 100.0,
        "base_volume": 1000.0,
    }
    payload.update(overrides)
    return SyntheticMarketScenarioV1Input(**payload)


def _assert_nominal(result, profile):
    assert result.decision is SyntheticMarketScenarioV1Decision.APPROVE_SYNTHETIC_MARKET_SCENARIO_V1
    assert result.state is SyntheticMarketScenarioV1State.READY_FOR_SIMULATED_BROKER_STUB_V1
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.scenario.profile is profile
    assert result.statistics.bar_count == 8
    assert result.conversion.converted is True
    assert result.report.markdown
    assert result.report.json


def test_nominal_trend_up():
    result = build_synthetic_market_scenario_v1(_input(SyntheticMarketScenarioV1Profile.TREND_UP))

    _assert_nominal(result, SyntheticMarketScenarioV1Profile.TREND_UP)
    assert result.statistics.final_price > result.statistics.initial_price


def test_nominal_trend_down():
    result = build_synthetic_market_scenario_v1(_input(SyntheticMarketScenarioV1Profile.TREND_DOWN))

    _assert_nominal(result, SyntheticMarketScenarioV1Profile.TREND_DOWN)
    assert result.statistics.final_price < result.statistics.initial_price


def test_nominal_range_bound():
    result = build_synthetic_market_scenario_v1(_input(SyntheticMarketScenarioV1Profile.RANGE_BOUND))

    _assert_nominal(result, SyntheticMarketScenarioV1Profile.RANGE_BOUND)
    assert abs(result.statistics.percent_change) < 0.02


def test_nominal_volatility_spike():
    result = build_synthetic_market_scenario_v1(_input(SyntheticMarketScenarioV1Profile.VOLATILITY_SPIKE))

    _assert_nominal(result, SyntheticMarketScenarioV1Profile.VOLATILITY_SPIKE)
    assert result.statistics.simple_volatility > 0.02
    assert max(bar.volume for bar in result.scenario.bars) == 4000.0


def test_nominal_gap():
    result = build_synthetic_market_scenario_v1(_input(SyntheticMarketScenarioV1Profile.GAP))

    _assert_nominal(result, SyntheticMarketScenarioV1Profile.GAP)
    closes = [bar.close for bar in result.scenario.bars]
    assert max(closes[index] - closes[index - 1] for index in range(1, len(closes))) > 4.0


def test_nominal_calm_market():
    result = build_synthetic_market_scenario_v1(_input(SyntheticMarketScenarioV1Profile.CALM_MARKET))

    _assert_nominal(result, SyntheticMarketScenarioV1Profile.CALM_MARKET)
    assert result.statistics.simple_volatility < 0.002


def test_input_missing():
    result = build_synthetic_market_scenario_v1(None)

    assert validate_synthetic_market_scenario_v1_input(None) is False
    assert SyntheticMarketScenarioV1Risk.SYNTHETIC_MARKET_SCENARIO_INPUT_MISSING in result.risks
    assert result.decision is SyntheticMarketScenarioV1Decision.REQUIRE_SYNTHETIC_MARKET_SCENARIO_INPUT_FIXES


def test_profile_unsupported():
    result = build_synthetic_market_scenario_v1(_input("UNKNOWN"))

    assert SyntheticMarketScenarioV1Risk.SYNTHETIC_MARKET_SCENARIO_PROFILE_UNSUPPORTED in result.risks
    assert result.decision is SyntheticMarketScenarioV1Decision.REQUIRE_SYNTHETIC_MARKET_SCENARIO_INPUT_FIXES


def test_bar_count_invalid():
    result = build_synthetic_market_scenario_v1(_input(bar_count=1))

    assert SyntheticMarketScenarioV1Risk.SYNTHETIC_MARKET_SCENARIO_BAR_COUNT_INVALID in result.risks
    assert result.decision is SyntheticMarketScenarioV1Decision.REQUIRE_SYNTHETIC_MARKET_SCENARIO_INPUT_FIXES


def test_scenario_empty():
    result = build_synthetic_market_scenario_v1(_input(custom_bars=()))

    assert SyntheticMarketScenarioV1Risk.SYNTHETIC_MARKET_SCENARIO_EMPTY in result.risks
    assert result.decision is SyntheticMarketScenarioV1Decision.REQUIRE_SYNTHETIC_MARKET_BARS_FIXES


def test_bar_invalid():
    bad = SyntheticMarketBarV1(0, "T0", "SIM", 0.0, 1.0, 0.1, 0.5, 1000.0)
    result = build_synthetic_market_scenario_v1(_input(custom_bars=(bad,)))

    assert SyntheticMarketScenarioV1Risk.SYNTHETIC_MARKET_BAR_INVALID in result.risks
    assert result.decision is SyntheticMarketScenarioV1Decision.REQUIRE_SYNTHETIC_MARKET_BARS_FIXES


def test_ohlcv_inconsistent():
    bad = SyntheticMarketBarV1(0, "T0", "SIM", 100.0, 99.0, 101.0, 100.0, 1000.0)
    result = build_synthetic_market_scenario_v1(_input(custom_bars=(bad,)))

    assert validate_synthetic_market_ohlcv_consistency((bad,)) is False
    assert SyntheticMarketScenarioV1Risk.SYNTHETIC_MARKET_OHLCV_INCONSISTENT in result.risks
    assert result.decision is SyntheticMarketScenarioV1Decision.REQUIRE_SYNTHETIC_MARKET_OHLCV_FIXES


def test_volume_invalid():
    bad = SyntheticMarketBarV1(0, "T0", "SIM", 100.0, 101.0, 99.0, 100.0, -1.0)
    result = build_synthetic_market_scenario_v1(_input(custom_bars=(bad,)))

    assert validate_synthetic_market_bars((bad,)) is False
    assert SyntheticMarketScenarioV1Risk.SYNTHETIC_MARKET_VOLUME_INVALID in result.risks
    assert result.decision is SyntheticMarketScenarioV1Decision.REQUIRE_SYNTHETIC_MARKET_BARS_FIXES


def test_statistics_are_computed():
    scenario = generate_synthetic_trend_up_scenario(_input())
    stats = compute_synthetic_market_scenario_statistics(scenario)

    assert stats.bar_count == 8
    assert stats.initial_price == 100.0
    assert stats.final_price == 105.6
    assert stats.absolute_change == 5.6
    assert stats.percent_change == 0.056
    assert stats.total_volume == 8000.0
    assert stats.max_high > stats.final_price
    assert stats.min_low < stats.initial_price


def test_conversion_to_controlled_offline_runner_minimal():
    result = build_synthetic_market_scenario_v1(_input())
    conversion = convert_synthetic_market_scenario_to_controlled_offline_runner_scenario(result.scenario)

    assert conversion.converted is True
    assert isinstance(conversion.runner_scenario, ControlledOfflineSyntheticMarketScenario)
    assert conversion.runner_scenario.bars[0].step == result.scenario.bars[0].index


def test_markdown_report():
    result = build_synthetic_market_scenario_v1(_input())
    markdown = render_synthetic_market_scenario_v1_markdown_report(result)

    assert "Synthetic Market Scenario v1" in markdown
    assert "APPROVE_SYNTHETIC_MARKET_SCENARIO_V1" in markdown
    assert "deterministic synthetic data only" in markdown


def test_json_report():
    result = build_synthetic_market_scenario_v1(_input())
    payload = json.loads(render_synthetic_market_scenario_v1_json_report(result))

    assert payload["decision"] == "APPROVE_SYNTHETIC_MARKET_SCENARIO_V1"
    assert payload["score"] == 100
    assert payload["risks"] == []
    assert payload["offline_only"] is True
    assert payload["synthetic_only"] is True


def test_no_data_directory_access_is_used():
    result = build_synthetic_market_scenario_v1(_input())
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert result.offline_only is True
    assert "data/" not in source
    assert "open(" not in source
    assert "read_text" not in source


def test_no_network_socket_http_websocket_access_is_used():
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_modules = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported_from_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }

    assert imported_modules.isdisjoint({"requests", "httpx", "urllib", "socket", "websocket"})
    assert imported_from_modules.isdisjoint({"requests", "httpx", "urllib", "socket", "websocket"})


def test_no_real_key_or_env_var_is_read():
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert "environ" not in source
    assert "getenv" not in source
    assert "dotenv" not in source
    assert "API_KEY" not in source


@pytest.mark.parametrize(
    ("overrides", "expected"),
    (
        ({"real_data_access_requested": True}, SyntheticMarketScenarioV1Risk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION),
        ({"data_directory_access_requested": True}, SyntheticMarketScenarioV1Risk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ({"network_requested": True}, SyntheticMarketScenarioV1Risk.NETWORK_BOUNDARY_VIOLATION),
        ({"broker_access_requested": True}, SyntheticMarketScenarioV1Risk.REAL_BROKER_BOUNDARY_VIOLATION),
        ({"api_key_read_requested": True}, SyntheticMarketScenarioV1Risk.REAL_SECRET_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations(overrides, expected):
    result = build_synthetic_market_scenario_v1(_input(**overrides))

    assert expected in result.risks
    assert result.decision is SyntheticMarketScenarioV1Decision.BLOCK_SYNTHETIC_MARKET_SCENARIO_V1


def test_recommendations():
    nominal = build_synthetic_market_scenario_v1(_input())
    blocked_recs = generate_synthetic_market_scenario_v1_recommendations(
        (SyntheticMarketScenarioV1Risk.NETWORK_BOUNDARY_VIOLATION,)
    )

    assert SyntheticMarketScenarioV1Recommendation.APPROVE_SIMULATED_BROKER_STUB_V1 in nominal.recommendations
    assert SyntheticMarketScenarioV1Recommendation.REMOVE_NETWORK_ACCESS in blocked_recs


def test_required_generators_and_boundaries_are_deterministic():
    data = _input()
    generated = (
        generate_synthetic_trend_up_scenario(_input(SyntheticMarketScenarioV1Profile.TREND_UP)),
        generate_synthetic_trend_down_scenario(_input(SyntheticMarketScenarioV1Profile.TREND_DOWN)),
        generate_synthetic_range_bound_scenario(_input(SyntheticMarketScenarioV1Profile.RANGE_BOUND)),
        generate_synthetic_volatility_spike_scenario(_input(SyntheticMarketScenarioV1Profile.VOLATILITY_SPIKE)),
        generate_synthetic_gap_scenario(_input(SyntheticMarketScenarioV1Profile.GAP)),
        generate_synthetic_calm_market_scenario(_input(SyntheticMarketScenarioV1Profile.CALM_MARKET)),
    )

    assert assert_synthetic_market_scenario_v1_offline_boundaries(data) is True
    assert detect_synthetic_market_scenario_v1_risks(data, generated[0], compute_synthetic_market_scenario_statistics(generated[0]), convert_synthetic_market_scenario_to_controlled_offline_runner_scenario(generated[0])) == ()
    assert generated[0] == generate_synthetic_trend_up_scenario(_input(SyntheticMarketScenarioV1Profile.TREND_UP))
    assert all(validate_synthetic_market_bars(item.bars) for item in generated)
