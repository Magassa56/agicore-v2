"""Deterministic offline synthetic market scenario library v1."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from math import isfinite
from typing import Any, Iterable, Mapping

from agicore.trading.controlled_offline_runner_minimal_models import (
    ControlledOfflineSyntheticMarketBar,
    ControlledOfflineSyntheticMarketScenario,
)
from agicore.trading.synthetic_market_scenario_v1_models import (
    SyntheticMarketBarV1,
    SyntheticMarketScenarioV1,
    SyntheticMarketScenarioV1ConversionResult,
    SyntheticMarketScenarioV1Decision,
    SyntheticMarketScenarioV1Input,
    SyntheticMarketScenarioV1Profile,
    SyntheticMarketScenarioV1Recommendation,
    SyntheticMarketScenarioV1Report,
    SyntheticMarketScenarioV1Result,
    SyntheticMarketScenarioV1Risk,
    SyntheticMarketScenarioV1Score,
    SyntheticMarketScenarioV1State,
    SyntheticMarketScenarioV1Statistics,
)


Risk = SyntheticMarketScenarioV1Risk
Recommendation = SyntheticMarketScenarioV1Recommendation
Decision = SyntheticMarketScenarioV1Decision
State = SyntheticMarketScenarioV1State
Profile = SyntheticMarketScenarioV1Profile


def _value(item: Any) -> str:
    return item.value if isinstance(item, Enum) else str(item)


def _dedupe(items: Iterable[Any]) -> tuple[Any, ...]:
    seen: set[Any] = set()
    out: list[Any] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return tuple(out)


def _coerce_input(data: SyntheticMarketScenarioV1Input | Mapping[str, Any] | None) -> SyntheticMarketScenarioV1Input | None:
    if data is None:
        return None
    if isinstance(data, SyntheticMarketScenarioV1Input):
        return data
    allowed = {field.name for field in fields(SyntheticMarketScenarioV1Input)}
    return SyntheticMarketScenarioV1Input(**{key: value for key, value in dict(data).items() if key in allowed})


def _parse_profile(profile: SyntheticMarketScenarioV1Profile | str | None) -> SyntheticMarketScenarioV1Profile | None:
    if isinstance(profile, SyntheticMarketScenarioV1Profile):
        return profile
    if isinstance(profile, str):
        try:
            return SyntheticMarketScenarioV1Profile(profile.upper())
        except ValueError:
            return None
    return None


def _finite_positive(value: Any) -> bool:
    return isinstance(value, int | float) and isfinite(float(value)) and float(value) > 0


def _round(value: float) -> float:
    return round(float(value), 10)


def _bar(index: int, symbol: str, open_price: float, close: float, spread: float, volume: float) -> SyntheticMarketBarV1:
    high = max(open_price, close) + abs(spread)
    low = max(0.0001, min(open_price, close) - abs(spread))
    return SyntheticMarketBarV1(
        index=index,
        timestamp=f"T{index:03d}",
        symbol=symbol,
        open=_round(open_price),
        high=_round(high),
        low=_round(low),
        close=_round(close),
        volume=_round(volume),
    )


def _scenario(data: SyntheticMarketScenarioV1Input, profile: Profile, closes: tuple[float, ...], volumes: tuple[float, ...], spread: float) -> SyntheticMarketScenarioV1:
    bars = []
    previous = closes[0]
    for index, close in enumerate(closes):
        open_price = previous if index else close
        bars.append(_bar(index, data.symbol, open_price, close, spread, volumes[index]))
        previous = close
    return SyntheticMarketScenarioV1(data.scenario_id, profile, data.symbol, tuple(bars))


def _linear_closes(start: float, count: int, step: float) -> tuple[float, ...]:
    return tuple(_round(max(0.0001, start + step * index)) for index in range(count))


def _volumes(base: float, count: int, multiplier_at: int | None = None, multiplier: float = 1.0) -> tuple[float, ...]:
    return tuple(_round(base * (multiplier if index == multiplier_at else 1.0)) for index in range(count))


def validate_synthetic_market_scenario_v1_input(data: SyntheticMarketScenarioV1Input | Mapping[str, Any] | None) -> bool:
    data = _coerce_input(data)
    return (
        data is not None
        and _parse_profile(data.profile) is not None
        and bool(data.scenario_id)
        and bool(data.symbol)
        and isinstance(data.bar_count, int)
        and data.bar_count >= 2
        and _finite_positive(data.initial_price)
        and _finite_positive(data.base_volume)
        and assert_synthetic_market_scenario_v1_offline_boundaries(data)
    )


def _coerce_bar(item: SyntheticMarketBarV1 | Mapping[str, Any], index: int, symbol: str) -> SyntheticMarketBarV1:
    if isinstance(item, SyntheticMarketBarV1):
        return item
    payload = dict(item)
    return SyntheticMarketBarV1(
        index=int(payload.get("index", payload.get("step", index))),
        timestamp=str(payload.get("timestamp", f"T{index:03d}")),
        symbol=str(payload.get("symbol", symbol)),
        open=float(payload.get("open", payload.get("close", 0.0))),
        high=float(payload.get("high", payload.get("close", 0.0))),
        low=float(payload.get("low", payload.get("close", 0.0))),
        close=float(payload.get("close", payload.get("price", 0.0))),
        volume=float(payload.get("volume", 0.0)),
    )


def generate_synthetic_trend_up_scenario(data: SyntheticMarketScenarioV1Input | Mapping[str, Any]) -> SyntheticMarketScenarioV1:
    data = _coerce_input(data) or SyntheticMarketScenarioV1Input(profile=Profile.TREND_UP)
    closes = _linear_closes(data.initial_price, data.bar_count, 0.8)
    return _scenario(data, Profile.TREND_UP, closes, _volumes(data.base_volume, data.bar_count), 0.35)


def generate_synthetic_trend_down_scenario(data: SyntheticMarketScenarioV1Input | Mapping[str, Any]) -> SyntheticMarketScenarioV1:
    data = _coerce_input(data) or SyntheticMarketScenarioV1Input(profile=Profile.TREND_DOWN)
    closes = _linear_closes(data.initial_price, data.bar_count, -0.7)
    return _scenario(data, Profile.TREND_DOWN, closes, _volumes(data.base_volume, data.bar_count), 0.35)


def generate_synthetic_range_bound_scenario(data: SyntheticMarketScenarioV1Input | Mapping[str, Any]) -> SyntheticMarketScenarioV1:
    data = _coerce_input(data) or SyntheticMarketScenarioV1Input(profile=Profile.RANGE_BOUND)
    pattern = (0.0, 1.2, -0.9, 0.8, -1.1, 0.4)
    closes = tuple(_round(data.initial_price + pattern[index % len(pattern)]) for index in range(data.bar_count))
    return _scenario(data, Profile.RANGE_BOUND, closes, _volumes(data.base_volume, data.bar_count), 0.45)


def generate_synthetic_volatility_spike_scenario(data: SyntheticMarketScenarioV1Input | Mapping[str, Any]) -> SyntheticMarketScenarioV1:
    data = _coerce_input(data) or SyntheticMarketScenarioV1Input(profile=Profile.VOLATILITY_SPIKE)
    spike = data.bar_count // 2
    closes = tuple(_round(data.initial_price + ((-1) ** index) * (4.0 if index == spike else 0.6)) for index in range(data.bar_count))
    return _scenario(data, Profile.VOLATILITY_SPIKE, closes, _volumes(data.base_volume, data.bar_count, spike, 4.0), 1.25)


def generate_synthetic_gap_scenario(data: SyntheticMarketScenarioV1Input | Mapping[str, Any]) -> SyntheticMarketScenarioV1:
    data = _coerce_input(data) or SyntheticMarketScenarioV1Input(profile=Profile.GAP)
    gap = data.bar_count // 2
    closes = tuple(_round(data.initial_price + 0.25 * index + (5.0 if index >= gap else 0.0)) for index in range(data.bar_count))
    return _scenario(data, Profile.GAP, closes, _volumes(data.base_volume, data.bar_count, gap, 2.0), 0.5)


def generate_synthetic_calm_market_scenario(data: SyntheticMarketScenarioV1Input | Mapping[str, Any]) -> SyntheticMarketScenarioV1:
    data = _coerce_input(data) or SyntheticMarketScenarioV1Input(profile=Profile.CALM_MARKET)
    pattern = (0.0, 0.1, -0.05, 0.05)
    closes = tuple(_round(data.initial_price + pattern[index % len(pattern)]) for index in range(data.bar_count))
    return _scenario(data, Profile.CALM_MARKET, closes, _volumes(data.base_volume * 0.5, data.bar_count), 0.12)


def _build_scenario(data: SyntheticMarketScenarioV1Input) -> SyntheticMarketScenarioV1 | None:
    profile = _parse_profile(data.profile)
    if data.custom_bars is not None:
        bars = tuple(_coerce_bar(item, index, data.symbol) for index, item in enumerate(data.custom_bars))
        return SyntheticMarketScenarioV1(data.scenario_id, profile or Profile.TREND_UP, data.symbol, bars)
    if profile is Profile.TREND_UP:
        return generate_synthetic_trend_up_scenario(data)
    if profile is Profile.TREND_DOWN:
        return generate_synthetic_trend_down_scenario(data)
    if profile is Profile.RANGE_BOUND:
        return generate_synthetic_range_bound_scenario(data)
    if profile is Profile.VOLATILITY_SPIKE:
        return generate_synthetic_volatility_spike_scenario(data)
    if profile is Profile.GAP:
        return generate_synthetic_gap_scenario(data)
    if profile is Profile.CALM_MARKET:
        return generate_synthetic_calm_market_scenario(data)
    return None


def validate_synthetic_market_ohlcv_consistency(bars: Iterable[SyntheticMarketBarV1] | None) -> bool:
    if not bars:
        return False
    for bar in bars:
        if not (
            bar.high >= max(bar.open, bar.close)
            and bar.low <= min(bar.open, bar.close)
            and bar.high >= bar.low
        ):
            return False
    return True


def validate_synthetic_market_bars(bars: Iterable[SyntheticMarketBarV1] | None) -> bool:
    bars = tuple(bars or ())
    return (
        bool(bars)
        and all(
            isinstance(bar.index, int)
            and bool(bar.timestamp)
            and bool(bar.symbol)
            and all(_finite_positive(value) for value in (bar.open, bar.high, bar.low, bar.close))
            and isinstance(bar.volume, int | float)
            and isfinite(float(bar.volume))
            and bar.volume >= 0
            for bar in bars
        )
        and validate_synthetic_market_ohlcv_consistency(bars)
    )


def compute_synthetic_market_scenario_statistics(scenario: SyntheticMarketScenarioV1 | None) -> SyntheticMarketScenarioV1Statistics | None:
    if scenario is None or not scenario.bars or not validate_synthetic_market_bars(scenario.bars):
        return None
    closes = tuple(bar.close for bar in scenario.bars)
    returns = tuple((closes[index] - closes[index - 1]) / closes[index - 1] for index in range(1, len(closes)) if closes[index - 1])
    mean_return = sum(returns) / len(returns) if returns else 0.0
    variance = sum((item - mean_return) ** 2 for item in returns) / len(returns) if returns else 0.0
    initial = closes[0]
    final = closes[-1]
    change = final - initial
    return SyntheticMarketScenarioV1Statistics(
        bar_count=len(scenario.bars),
        initial_price=_round(initial),
        final_price=_round(final),
        absolute_change=_round(change),
        percent_change=_round(change / initial if initial else 0.0),
        total_volume=_round(sum(bar.volume for bar in scenario.bars)),
        simple_volatility=_round(variance ** 0.5),
        max_high=_round(max(bar.high for bar in scenario.bars)),
        min_low=_round(min(bar.low for bar in scenario.bars)),
    )


def convert_synthetic_market_scenario_to_controlled_offline_runner_scenario(
    scenario: SyntheticMarketScenarioV1 | None,
) -> SyntheticMarketScenarioV1ConversionResult:
    if scenario is None or not validate_synthetic_market_bars(scenario.bars):
        return SyntheticMarketScenarioV1ConversionResult(False, None, (Risk.SYNTHETIC_MARKET_CONVERSION_FAILED,))
    runner_bars = tuple(
        ControlledOfflineSyntheticMarketBar(
            step=bar.index,
            symbol=bar.symbol,
            open=bar.open,
            high=bar.high,
            low=bar.low,
            close=bar.close,
            volume=bar.volume,
            timestamp=bar.timestamp,
        )
        for bar in scenario.bars
    )
    return SyntheticMarketScenarioV1ConversionResult(
        True,
        ControlledOfflineSyntheticMarketScenario(scenario.scenario_id, scenario.symbol, runner_bars),
        (),
    )


def assert_synthetic_market_scenario_v1_offline_boundaries(data: SyntheticMarketScenarioV1Input | Mapping[str, Any] | None) -> bool:
    data = _coerce_input(data)
    return (
        data is not None
        and data.offline_mode_enforced is True
        and data.deterministic_generation is True
        and data.synthetic_data_only is True
        and data.in_memory_only is True
        and data.no_real_data_access is True
        and data.no_data_directory_access is True
        and data.no_network is True
        and data.no_http_transport is True
        and data.no_websocket_transport is True
        and data.no_socket_transport is True
        and data.no_external_api is True
        and data.no_real_broker is True
        and data.no_alpaca_real is True
        and data.no_api_key_read is True
        and data.no_env_var_read is True
        and data.no_hardcoded_secret is True
        and data.real_data_access_requested is False
        and data.data_directory_access_requested is False
        and data.network_requested is False
        and data.http_requested is False
        and data.websocket_requested is False
        and data.socket_requested is False
        and data.external_api_requested is False
        and data.broker_access_requested is False
        and data.api_key_read_requested is False
        and data.env_var_read_requested is False
    )


def detect_synthetic_market_scenario_v1_risks(
    data: SyntheticMarketScenarioV1Input | Mapping[str, Any] | None,
    scenario: SyntheticMarketScenarioV1 | None = None,
    statistics: SyntheticMarketScenarioV1Statistics | None = None,
    conversion: SyntheticMarketScenarioV1ConversionResult | None = None,
) -> tuple[Risk, ...]:
    data = _coerce_input(data)
    risks: list[Risk] = []
    if data is None:
        risks.append(Risk.SYNTHETIC_MARKET_SCENARIO_INPUT_MISSING)
        return tuple(risks)
    if _parse_profile(data.profile) is None:
        risks.append(Risk.SYNTHETIC_MARKET_SCENARIO_PROFILE_UNSUPPORTED)
    if not isinstance(data.bar_count, int) or data.bar_count < 2:
        risks.append(Risk.SYNTHETIC_MARKET_SCENARIO_BAR_COUNT_INVALID)
    if scenario is None or not scenario.bars:
        risks.append(Risk.SYNTHETIC_MARKET_SCENARIO_EMPTY)
    else:
        if any(not all(_finite_positive(value) for value in (bar.open, bar.high, bar.low, bar.close)) for bar in scenario.bars):
            risks.append(Risk.SYNTHETIC_MARKET_BAR_INVALID)
        if any(not isinstance(bar.volume, int | float) or not isfinite(float(bar.volume)) or bar.volume < 0 for bar in scenario.bars):
            risks.append(Risk.SYNTHETIC_MARKET_VOLUME_INVALID)
        if not validate_synthetic_market_ohlcv_consistency(scenario.bars):
            risks.append(Risk.SYNTHETIC_MARKET_OHLCV_INCONSISTENT)
    if statistics is None:
        risks.append(Risk.SYNTHETIC_MARKET_STATISTICS_MISSING)
    if conversion is None or not conversion.converted:
        risks.append(Risk.SYNTHETIC_MARKET_CONVERSION_FAILED)
    if data.no_real_data_access is not True or data.real_data_access_requested:
        risks.append(Risk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION)
    if data.no_data_directory_access is not True or data.data_directory_access_requested:
        risks.append(Risk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION)
    if data.no_network is not True or data.no_http_transport is not True or data.no_websocket_transport is not True or data.no_socket_transport is not True or data.no_external_api is not True or data.network_requested or data.http_requested or data.websocket_requested or data.socket_requested or data.external_api_requested:
        risks.append(Risk.NETWORK_BOUNDARY_VIOLATION)
    if data.no_real_broker is not True or data.no_alpaca_real is not True or data.broker_access_requested:
        risks.append(Risk.REAL_BROKER_BOUNDARY_VIOLATION)
    if data.no_api_key_read is not True or data.no_env_var_read is not True or data.no_hardcoded_secret is not True or data.api_key_read_requested or data.env_var_read_requested:
        risks.append(Risk.REAL_SECRET_BOUNDARY_VIOLATION)
    return _dedupe(risks)


def _score(flag: bool) -> int:
    return 100 if flag else 0


def _build_score(data, scenario, statistics, conversion, risks) -> SyntheticMarketScenarioV1Score:
    input_ok = validate_synthetic_market_scenario_v1_input(data)
    bar_ok = scenario is not None and bool(scenario.bars) and validate_synthetic_market_bars(scenario.bars)
    ohlcv_ok = scenario is not None and validate_synthetic_market_ohlcv_consistency(scenario.bars)
    statistics_ok = statistics is not None
    conversion_ok = conversion is not None and conversion.converted
    boundary_ok = assert_synthetic_market_scenario_v1_offline_boundaries(data)
    parts = (
        _score(input_ok),
        _score(bar_ok),
        _score(ohlcv_ok),
        _score(statistics_ok),
        _score(conversion_ok),
        _score(boundary_ok),
    )
    overall = 100 if not risks and all(part == 100 for part in parts) else round(sum(parts) / len(parts))
    return SyntheticMarketScenarioV1Score(overall, *parts)


def generate_synthetic_market_scenario_v1_recommendations(risks: Iterable[Risk] | None = None) -> tuple[Recommendation, ...]:
    risks = tuple(risks or ())
    if not risks:
        return (
            Recommendation.RUN_SYNTHETIC_MARKET_SCENARIO_V1_TEST_SUITE,
            Recommendation.APPROVE_SIMULATED_BROKER_STUB_V1,
        )
    mapping = {
        Risk.SYNTHETIC_MARKET_SCENARIO_INPUT_MISSING: Recommendation.PROVIDE_SYNTHETIC_MARKET_SCENARIO_INPUT,
        Risk.SYNTHETIC_MARKET_SCENARIO_PROFILE_UNSUPPORTED: Recommendation.USE_SUPPORTED_SYNTHETIC_MARKET_PROFILE,
        Risk.SYNTHETIC_MARKET_SCENARIO_BAR_COUNT_INVALID: Recommendation.FIX_SYNTHETIC_MARKET_BAR_COUNT,
        Risk.SYNTHETIC_MARKET_SCENARIO_EMPTY: Recommendation.GENERATE_SYNTHETIC_MARKET_BARS,
        Risk.SYNTHETIC_MARKET_BAR_INVALID: Recommendation.FIX_SYNTHETIC_MARKET_BARS,
        Risk.SYNTHETIC_MARKET_OHLCV_INCONSISTENT: Recommendation.FIX_SYNTHETIC_MARKET_OHLCV,
        Risk.SYNTHETIC_MARKET_VOLUME_INVALID: Recommendation.FIX_SYNTHETIC_MARKET_VOLUME,
        Risk.SYNTHETIC_MARKET_STATISTICS_MISSING: Recommendation.COMPUTE_SYNTHETIC_MARKET_STATISTICS,
        Risk.SYNTHETIC_MARKET_CONVERSION_FAILED: Recommendation.FIX_CONTROLLED_OFFLINE_RUNNER_CONVERSION,
        Risk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION: Recommendation.REMOVE_REAL_DATA_ACCESS,
        Risk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION: Recommendation.REMOVE_DATA_DIRECTORY_ACCESS,
        Risk.NETWORK_BOUNDARY_VIOLATION: Recommendation.REMOVE_NETWORK_ACCESS,
        Risk.REAL_BROKER_BOUNDARY_VIOLATION: Recommendation.REMOVE_REAL_BROKER_ACCESS,
        Risk.REAL_SECRET_BOUNDARY_VIOLATION: Recommendation.REMOVE_REAL_SECRET_ACCESS,
    }
    return _dedupe(mapping[risk] for risk in risks if risk in mapping)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_SYNTHETIC_MARKET_SCENARIO_V1
    boundary = {
        Risk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION,
        Risk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION,
        Risk.NETWORK_BOUNDARY_VIOLATION,
        Risk.REAL_BROKER_BOUNDARY_VIOLATION,
        Risk.REAL_SECRET_BOUNDARY_VIOLATION,
    }
    if any(risk in boundary for risk in risks):
        return Decision.BLOCK_SYNTHETIC_MARKET_SCENARIO_V1
    if Risk.SYNTHETIC_MARKET_SCENARIO_INPUT_MISSING in risks or Risk.SYNTHETIC_MARKET_SCENARIO_PROFILE_UNSUPPORTED in risks or Risk.SYNTHETIC_MARKET_SCENARIO_BAR_COUNT_INVALID in risks:
        return Decision.REQUIRE_SYNTHETIC_MARKET_SCENARIO_INPUT_FIXES
    if Risk.SYNTHETIC_MARKET_SCENARIO_EMPTY in risks or Risk.SYNTHETIC_MARKET_BAR_INVALID in risks or Risk.SYNTHETIC_MARKET_VOLUME_INVALID in risks:
        return Decision.REQUIRE_SYNTHETIC_MARKET_BARS_FIXES
    if Risk.SYNTHETIC_MARKET_OHLCV_INCONSISTENT in risks:
        return Decision.REQUIRE_SYNTHETIC_MARKET_OHLCV_FIXES
    if Risk.SYNTHETIC_MARKET_STATISTICS_MISSING in risks:
        return Decision.REQUIRE_SYNTHETIC_MARKET_STATISTICS_FIXES
    if Risk.SYNTHETIC_MARKET_CONVERSION_FAILED in risks:
        return Decision.REQUIRE_SYNTHETIC_MARKET_CONVERSION_FIXES
    return Decision.BLOCK_SYNTHETIC_MARKET_SCENARIO_V1


def _state_for(risks: tuple[Risk, ...], score: SyntheticMarketScenarioV1Score) -> State:
    input_risks = {
        Risk.SYNTHETIC_MARKET_SCENARIO_INPUT_MISSING,
        Risk.SYNTHETIC_MARKET_SCENARIO_PROFILE_UNSUPPORTED,
        Risk.SYNTHETIC_MARKET_SCENARIO_BAR_COUNT_INVALID,
    }
    if any(risk in input_risks for risk in risks):
        return State.SYNTHETIC_MARKET_SCENARIO_V1_INPUT_INVALID
    if risks:
        return State.SYNTHETIC_MARKET_SCENARIO_V1_BLOCKED
    if score.overall_score == 100:
        return State.READY_FOR_SIMULATED_BROKER_STUB_V1
    if score.overall_score >= 70:
        return State.SYNTHETIC_MARKET_SCENARIO_V1_COMPLETED_WITH_WARNINGS
    return State.NOT_READY


def render_synthetic_market_scenario_v1_markdown_report(result: SyntheticMarketScenarioV1Result) -> str:
    risks = ", ".join(_value(risk) for risk in result.risks) or "none"
    recs = ", ".join(_value(rec) for rec in result.recommendations) or "none"
    stats = result.statistics
    return "\n".join(
        (
            "# Synthetic Market Scenario v1",
            f"- State: {result.state.value}",
            f"- Decision: {result.decision.value}",
            f"- Score: {result.score.overall_score}",
            f"- Profile: {result.scenario.profile.value if result.scenario else 'NONE'}",
            f"- Bars: {stats.bar_count if stats else 0}",
            f"- Initial price: {stats.initial_price if stats else 0}",
            f"- Final price: {stats.final_price if stats else 0}",
            f"- Risks: {risks}",
            f"- Recommendations: {recs}",
            "- Boundary: deterministic synthetic data only; no data directory, no network, no broker, no secret.",
            f"- Next phase: {result.next_phase}",
        )
    )


def render_synthetic_market_scenario_v1_json_report(result: SyntheticMarketScenarioV1Result) -> str:
    stats = result.statistics
    risks = ",".join(f'"{risk.value}"' for risk in result.risks)
    return (
        "{"
        f"\"state\":\"{result.state.value}\","
        f"\"decision\":\"{result.decision.value}\","
        f"\"score\":{result.score.overall_score},"
        f"\"profile\":\"{result.scenario.profile.value if result.scenario else 'NONE'}\","
        f"\"bar_count\":{stats.bar_count if stats else 0},"
        f"\"initial_price\":{stats.initial_price if stats else 0},"
        f"\"final_price\":{stats.final_price if stats else 0},"
        f"\"risks\":[{risks}],"
        "\"offline_only\":true,"
        "\"synthetic_only\":true"
        "}"
    )


def build_synthetic_market_scenario_v1(
    data: SyntheticMarketScenarioV1Input | Mapping[str, Any] | None = None,
) -> SyntheticMarketScenarioV1Result:
    data = _coerce_input(data)
    scenario = _build_scenario(data) if data is not None else None
    statistics = compute_synthetic_market_scenario_statistics(scenario)
    conversion = convert_synthetic_market_scenario_to_controlled_offline_runner_scenario(scenario)
    risks = detect_synthetic_market_scenario_v1_risks(data, scenario, statistics, conversion)
    score = _build_score(data, scenario, statistics, conversion, risks)
    recommendations = generate_synthetic_market_scenario_v1_recommendations(risks)
    result = SyntheticMarketScenarioV1Result(
        state=_state_for(risks, score),
        decision=_decision_for(risks),
        score=score,
        risks=risks,
        recommendations=recommendations,
        scenario=scenario,
        statistics=statistics,
        conversion=conversion,
        report=None,
        offline_only=data is not None and data.offline_mode_enforced,
        synthetic_only=data is not None and data.synthetic_data_only,
    )
    report = SyntheticMarketScenarioV1Report(
        markdown=render_synthetic_market_scenario_v1_markdown_report(result),
        json=render_synthetic_market_scenario_v1_json_report(result),
    )
    return SyntheticMarketScenarioV1Result(**{**result.__dict__, "report": report})


__all__ = [
    "build_synthetic_market_scenario_v1",
    "validate_synthetic_market_scenario_v1_input",
    "generate_synthetic_trend_up_scenario",
    "generate_synthetic_trend_down_scenario",
    "generate_synthetic_range_bound_scenario",
    "generate_synthetic_volatility_spike_scenario",
    "generate_synthetic_gap_scenario",
    "generate_synthetic_calm_market_scenario",
    "validate_synthetic_market_bars",
    "validate_synthetic_market_ohlcv_consistency",
    "compute_synthetic_market_scenario_statistics",
    "convert_synthetic_market_scenario_to_controlled_offline_runner_scenario",
    "detect_synthetic_market_scenario_v1_risks",
    "generate_synthetic_market_scenario_v1_recommendations",
    "render_synthetic_market_scenario_v1_markdown_report",
    "render_synthetic_market_scenario_v1_json_report",
    "assert_synthetic_market_scenario_v1_offline_boundaries",
]
