"""Deterministic in-memory CSV replay input v1 for AGIcore Trading."""

from __future__ import annotations

import csv
import json
from dataclasses import fields
from enum import Enum
from io import StringIO
from typing import Any, Iterable, Mapping

from agicore.trading.controlled_offline_runner_minimal_models import (
    ControlledOfflineSyntheticMarketBar,
    ControlledOfflineSyntheticMarketScenario,
)
from agicore.trading.csv_replay_input_v1_models import (
    CsvReplayBarV1,
    CsvReplayConversionResultV1,
    CsvReplayDatasetV1,
    CsvReplayInputV1Decision,
    CsvReplayInputV1HeaderSpec,
    CsvReplayInputV1Input,
    CsvReplayInputV1Recommendation,
    CsvReplayInputV1Report,
    CsvReplayInputV1Result,
    CsvReplayInputV1Risk,
    CsvReplayInputV1Score,
    CsvReplayInputV1State,
    CsvReplayNormalizedRowV1,
    CsvReplayRawRowV1,
    CsvReplayStatisticsV1,
)
from agicore.trading.synthetic_market_scenario_v1_models import (
    SyntheticMarketBarV1,
    SyntheticMarketScenarioV1,
    SyntheticMarketScenarioV1Profile,
)


Risk = CsvReplayInputV1Risk
Recommendation = CsvReplayInputV1Recommendation
Decision = CsvReplayInputV1Decision
State = CsvReplayInputV1State


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


def _coerce_input(data: CsvReplayInputV1Input | Mapping[str, Any] | None) -> CsvReplayInputV1Input | None:
    if data is None:
        return None
    if isinstance(data, CsvReplayInputV1Input):
        return data
    allowed = {field.name for field in fields(CsvReplayInputV1Input)}
    return CsvReplayInputV1Input(**{key: value for key, value in dict(data).items() if key in allowed})


def _header_spec(data: CsvReplayInputV1Input | None) -> CsvReplayInputV1HeaderSpec:
    if data and data.header_spec:
        return data.header_spec
    return CsvReplayInputV1HeaderSpec(delimiter=data.delimiter if data else ",")


def _boundary_risks(data: CsvReplayInputV1Input | None) -> tuple[Risk, ...]:
    if data is None:
        return ()
    risks: list[Risk] = []
    if data.file_read_requested or not data.no_file_read:
        risks.append(Risk.FILE_READ_BOUNDARY_VIOLATION)
    if data.file_write_requested or not data.no_file_write:
        risks.append(Risk.FILE_WRITE_BOUNDARY_VIOLATION)
    if data.real_data_access_requested or not data.no_real_data_access:
        risks.append(Risk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION)
    if (
        data.data_directory_read_requested
        or data.data_directory_write_requested
        or not data.no_data_directory_read
        or not data.no_data_directory_write
    ):
        risks.append(Risk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION)
    if data.broker_connection_requested or not data.no_real_broker or not data.no_alpaca_real:
        risks.append(Risk.REAL_BROKER_BOUNDARY_VIOLATION)
    if data.api_key_read_requested or data.env_var_read_requested or not data.no_api_key_read:
        risks.append(Risk.REAL_SECRET_BOUNDARY_VIOLATION)
    if not data.no_env_var_read or not data.no_hardcoded_secret:
        risks.append(Risk.REAL_SECRET_BOUNDARY_VIOLATION)
    if (
        data.network_requested
        or data.http_requested
        or data.websocket_requested
        or data.socket_requested
        or data.external_api_requested
        or not data.no_http_transport
        or not data.no_websocket_transport
        or not data.no_socket_transport
        or not data.no_external_api
        or not data.no_external_ml
        or not data.no_external_llm
    ):
        risks.append(Risk.NETWORK_BOUNDARY_VIOLATION)
    if data.order_execution_requested or not data.no_real_order:
        risks.append(Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION)
    if data.account_access_requested or not data.no_real_account_access:
        risks.append(Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION)
    if data.position_mutation_requested or not data.no_position_mutation:
        risks.append(Risk.POSITION_MUTATION_BOUNDARY_VIOLATION)
    if not data.offline_mode_enforced or not data.sandbox_mode_enforced:
        risks.append(Risk.NETWORK_BOUNDARY_VIOLATION)
    if not data.in_memory_only or not data.csv_string_only:
        risks.append(Risk.FILE_READ_BOUNDARY_VIOLATION)
    return _dedupe(risks)


def validate_csv_replay_input_v1_input(data: CsvReplayInputV1Input | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and isinstance(payload.csv_content, str) and payload.symbol and payload.dataset_id)


def parse_csv_replay_content_v1(data: CsvReplayInputV1Input | Mapping[str, Any]) -> tuple[CsvReplayRawRowV1, ...]:
    payload = _coerce_input(data)
    if payload is None:
        return ()
    content = payload.csv_content.strip()
    if not content:
        return ()
    reader = csv.DictReader(StringIO(content), delimiter=_header_spec(payload).delimiter)
    if not validate_csv_replay_headers_v1(tuple(reader.fieldnames or ()), _header_spec(payload)):
        return ()
    rows: list[CsvReplayRawRowV1] = []
    for index, row in enumerate(reader):
        values = {str(key).strip(): str(value).strip() for key, value in row.items() if key is not None}
        rows.append(CsvReplayRawRowV1(index=index, values=values))
    return tuple(rows)


def validate_csv_replay_headers_v1(
    headers: Iterable[str] | None,
    header_spec: CsvReplayInputV1HeaderSpec | None = None,
) -> bool:
    spec = header_spec or CsvReplayInputV1HeaderSpec()
    normalized = tuple(str(header).strip().lower() for header in (headers or ()))
    if not normalized:
        return False
    return set(normalized) == set(spec.required_columns)


def _timestamp_valid(value: str) -> bool:
    stripped = str(value).strip()
    return bool(stripped and any(char.isdigit() for char in stripped))


def _to_float(value: str) -> float:
    return float(str(value).strip())


def validate_csv_replay_row_v1(
    row: CsvReplayRawRowV1 | Mapping[str, Any],
    header_spec: CsvReplayInputV1HeaderSpec | None = None,
) -> bool:
    spec = header_spec or CsvReplayInputV1HeaderSpec()
    values = row.values if isinstance(row, CsvReplayRawRowV1) else dict(row).get("values", dict(row))
    if set(values) != set(spec.required_columns):
        return False
    if not _timestamp_valid(str(values.get("timestamp", ""))):
        return False
    try:
        numbers = [_to_float(str(values[column])) for column in ("open", "high", "low", "close", "volume")]
    except (TypeError, ValueError):
        return False
    return all(number == number for number in numbers)


def normalize_csv_replay_row_v1(row: CsvReplayRawRowV1 | Mapping[str, Any]) -> CsvReplayNormalizedRowV1:
    values = row.values if isinstance(row, CsvReplayRawRowV1) else dict(row).get("values", dict(row))
    index = row.index if isinstance(row, CsvReplayRawRowV1) else int(dict(row).get("index", 0))
    return CsvReplayNormalizedRowV1(
        index=index,
        timestamp=str(values["timestamp"]).strip(),
        open=_to_float(str(values["open"])),
        high=_to_float(str(values["high"])),
        low=_to_float(str(values["low"])),
        close=_to_float(str(values["close"])),
        volume=_to_float(str(values["volume"])),
    )


def build_csv_replay_bar_v1(row: CsvReplayNormalizedRowV1, symbol: str = "SIM") -> CsvReplayBarV1:
    return CsvReplayBarV1(
        index=row.index,
        timestamp=row.timestamp,
        symbol=symbol,
        open=row.open,
        high=row.high,
        low=row.low,
        close=row.close,
        volume=row.volume,
    )


def _bar_valid(bar: CsvReplayBarV1) -> bool:
    prices = (bar.open, bar.high, bar.low, bar.close)
    return (
        bool(bar.timestamp)
        and bool(bar.symbol)
        and all(price > 0 for price in prices)
        and bar.volume >= 0
    )


def validate_csv_replay_bars_v1(bars: Iterable[CsvReplayBarV1]) -> bool:
    bar_tuple = tuple(bars)
    return bool(bar_tuple) and all(_bar_valid(bar) for bar in bar_tuple)


def validate_csv_replay_ohlcv_consistency_v1(bars: Iterable[CsvReplayBarV1]) -> bool:
    bar_tuple = tuple(bars)
    if not bar_tuple:
        return False
    for bar in bar_tuple:
        if bar.high < max(bar.open, bar.close, bar.low):
            return False
        if bar.low > min(bar.open, bar.close, bar.high):
            return False
        if bar.volume < 0:
            return False
    return True


def compute_csv_replay_statistics_v1(bars: Iterable[CsvReplayBarV1]) -> CsvReplayStatisticsV1 | None:
    bar_tuple = tuple(bars)
    if not validate_csv_replay_bars_v1(bar_tuple):
        return None
    initial = bar_tuple[0]
    final = bar_tuple[-1]
    absolute_change = final.close - initial.open
    percent_change = absolute_change / initial.open if initial.open else 0.0
    return CsvReplayStatisticsV1(
        bar_count=len(bar_tuple),
        initial_timestamp=initial.timestamp,
        final_timestamp=final.timestamp,
        initial_price=initial.open,
        final_price=final.close,
        absolute_change=absolute_change,
        percent_change=percent_change,
        total_volume=sum(bar.volume for bar in bar_tuple),
        max_high=max(bar.high for bar in bar_tuple),
        min_low=min(bar.low for bar in bar_tuple),
    )


def convert_csv_replay_to_synthetic_market_scenario_v1(
    dataset: CsvReplayDatasetV1 | None,
) -> CsvReplayConversionResultV1:
    if dataset is None or not dataset.bars:
        return CsvReplayConversionResultV1(
            converted=False,
            target="SYNTHETIC_MARKET_SCENARIO_V1",
            risks=(Risk.CSV_REPLAY_CONVERSION_FAILED,),
        )
    bars = tuple(
        SyntheticMarketBarV1(
            index=bar.index,
            timestamp=bar.timestamp,
            symbol=bar.symbol,
            open=bar.open,
            high=bar.high,
            low=bar.low,
            close=bar.close,
            volume=bar.volume,
        )
        for bar in dataset.bars
    )
    scenario = SyntheticMarketScenarioV1(
        scenario_id=dataset.dataset_id,
        profile=SyntheticMarketScenarioV1Profile.RANGE_BOUND,
        symbol=dataset.symbol,
        bars=bars,
    )
    return CsvReplayConversionResultV1(
        converted=True,
        target="SYNTHETIC_MARKET_SCENARIO_V1",
        scenario=scenario,
    )


def convert_csv_replay_to_controlled_offline_runner_scenario_v1(
    dataset: CsvReplayDatasetV1 | None,
) -> CsvReplayConversionResultV1:
    if dataset is None or not dataset.bars:
        return CsvReplayConversionResultV1(
            converted=False,
            target="CONTROLLED_OFFLINE_RUNNER_MINIMAL",
            risks=(Risk.CSV_REPLAY_CONVERSION_FAILED,),
        )
    bars = tuple(
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
        for bar in dataset.bars
    )
    scenario = ControlledOfflineSyntheticMarketScenario(
        scenario_id=dataset.dataset_id,
        symbol=dataset.symbol,
        bars=bars,
    )
    return CsvReplayConversionResultV1(
        converted=True,
        target="CONTROLLED_OFFLINE_RUNNER_MINIMAL",
        scenario=scenario,
    )


def _safe_payload(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, tuple):
        return [_safe_payload(item) for item in value]
    if isinstance(value, list):
        return [_safe_payload(item) for item in value]
    if isinstance(value, Mapping):
        return {str(key): _safe_payload(item) for key, item in value.items()}
    if hasattr(value, "__dict__"):
        return {
            key: _safe_payload(item)
            for key, item in vars(value).items()
            if not key.startswith("_")
        }
    return str(value)


def render_csv_replay_input_v1_markdown_report(
    result: CsvReplayInputV1Result | Mapping[str, Any],
) -> str:
    if isinstance(result, CsvReplayInputV1Result):
        decision = result.decision.value
        state = result.state.value
        score = result.score.overall_score
        risks = tuple(risk.value for risk in result.risks)
        stats = result.statistics
        bar_count = stats.bar_count if stats else 0
    else:
        payload = dict(result)
        decision = str(payload.get("decision", ""))
        state = str(payload.get("state", ""))
        score = int(payload.get("score", 0))
        risks = tuple(str(risk) for risk in payload.get("risks", ()))
        bar_count = int(payload.get("bar_count", 0))
    lines = [
        "# CSV Replay Input v1",
        "",
        f"- decision: {decision}",
        f"- state: {state}",
        f"- score: {score}",
        f"- bars: {bar_count}",
        f"- risks: {', '.join(risks) if risks else 'none'}",
        "",
        "## Boundaries",
        "- source: in-memory CSV string",
        "- file_read: false",
        "- file_written: false",
        "- broker: simulated/offline only",
    ]
    return "\n".join(lines) + "\n"


def render_csv_replay_input_v1_json_report(
    result: CsvReplayInputV1Result | Mapping[str, Any],
) -> str:
    if isinstance(result, CsvReplayInputV1Result):
        payload = {
            "schema": "csv_replay_input_v1",
            "decision": result.decision.value,
            "state": result.state.value,
            "score": result.score.overall_score,
            "risks": [risk.value for risk in result.risks],
            "recommendations": [recommendation.value for recommendation in result.recommendations],
            "statistics": _safe_payload(result.statistics),
            "dataset": _safe_payload(result.dataset),
            "synthetic_market_conversion": _safe_payload(result.synthetic_market_conversion),
            "controlled_runner_conversion": _safe_payload(result.controlled_runner_conversion),
            "offline_only": result.offline_only,
            "in_memory_only": result.in_memory_only,
            "file_read": result.file_read,
            "file_written": result.file_written,
        }
    else:
        payload = dict(result)
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def compute_csv_replay_input_v1_score(
    data: CsvReplayInputV1Input | Mapping[str, Any] | None,
    headers_valid: bool = False,
    raw_rows: tuple[CsvReplayRawRowV1, ...] = (),
    normalized_rows: tuple[CsvReplayNormalizedRowV1, ...] = (),
    bars: tuple[CsvReplayBarV1, ...] = (),
    statistics: CsvReplayStatisticsV1 | None = None,
    synthetic_conversion: CsvReplayConversionResultV1 | None = None,
    controlled_conversion: CsvReplayConversionResultV1 | None = None,
    risks: tuple[Risk, ...] = (),
) -> CsvReplayInputV1Score:
    payload = _coerce_input(data)
    input_score = 100 if validate_csv_replay_input_v1_input(payload) and payload and payload.csv_content.strip() else 0
    header_score = 100 if headers_valid else 0
    row_score = 100 if raw_rows and len(raw_rows) == len(normalized_rows) else 0
    bar_score = 100 if validate_csv_replay_bars_v1(bars) else 0
    ohlcv_score = 100 if validate_csv_replay_ohlcv_consistency_v1(bars) else 0
    statistics_score = 100 if statistics else 0
    conversion_score = 100 if synthetic_conversion and controlled_conversion and synthetic_conversion.converted and controlled_conversion.converted else 0
    boundary_score = 100 if not _boundary_risks(payload) else 0
    parts = (
        input_score,
        header_score,
        row_score,
        bar_score,
        ohlcv_score,
        statistics_score,
        conversion_score,
        boundary_score,
    )
    overall = min(parts)
    if risks:
        overall = min(overall, max(0, 100 - len(risks) * 10))
    return CsvReplayInputV1Score(
        overall_score=overall,
        input_score=input_score,
        header_score=header_score,
        row_score=row_score,
        bar_score=bar_score,
        ohlcv_score=ohlcv_score,
        statistics_score=statistics_score,
        conversion_score=conversion_score,
        boundary_score=boundary_score,
    )


def detect_csv_replay_input_v1_risks(
    data: CsvReplayInputV1Input | Mapping[str, Any] | None,
    headers_present: bool = False,
    headers_valid: bool = False,
    raw_rows: tuple[CsvReplayRawRowV1, ...] = (),
    normalized_rows: tuple[CsvReplayNormalizedRowV1, ...] = (),
    bars: tuple[CsvReplayBarV1, ...] = (),
    statistics: CsvReplayStatisticsV1 | None = None,
    synthetic_conversion: CsvReplayConversionResultV1 | None = None,
    controlled_conversion: CsvReplayConversionResultV1 | None = None,
) -> tuple[Risk, ...]:
    payload = _coerce_input(data)
    risks: list[Risk] = []
    if payload is None:
        risks.append(Risk.CSV_REPLAY_INPUT_MISSING)
    elif not payload.csv_content.strip():
        risks.append(Risk.CSV_REPLAY_CONTENT_EMPTY)
    if payload is not None and payload.csv_content.strip() and not headers_present:
        risks.append(Risk.CSV_REPLAY_HEADER_MISSING)
    if headers_present and not headers_valid:
        risks.append(Risk.CSV_REPLAY_HEADER_INVALID)
    if headers_valid and not raw_rows:
        risks.append(Risk.CSV_REPLAY_ROW_INVALID)
    if raw_rows and len(raw_rows) != len(normalized_rows):
        risks.append(Risk.CSV_REPLAY_ROW_INVALID)
    if raw_rows:
        for row in raw_rows:
            if not validate_csv_replay_row_v1(row, _header_spec(payload)):
                values = row.values
                if not _timestamp_valid(values.get("timestamp", "")):
                    risks.append(Risk.CSV_REPLAY_TIMESTAMP_INVALID)
                for column in ("open", "high", "low", "close", "volume"):
                    try:
                        _to_float(values.get(column, ""))
                    except (TypeError, ValueError):
                        risks.append(Risk.CSV_REPLAY_NUMERIC_VALUE_INVALID)
                        break
                risks.append(Risk.CSV_REPLAY_ROW_INVALID)
    if bars and not validate_csv_replay_bars_v1(bars):
        risks.append(Risk.CSV_REPLAY_BAR_INVALID)
    if bars and not validate_csv_replay_ohlcv_consistency_v1(bars):
        risks.append(Risk.CSV_REPLAY_OHLCV_INCONSISTENT)
    if any(bar.volume < 0 for bar in bars):
        risks.append(Risk.CSV_REPLAY_VOLUME_INVALID)
    if headers_valid and raw_rows and not statistics:
        risks.append(Risk.CSV_REPLAY_STATISTICS_MISSING)
    if (
        headers_valid
        and raw_rows
        and (
            not synthetic_conversion
            or not controlled_conversion
            or not synthetic_conversion.converted
            or not controlled_conversion.converted
        )
    ):
        risks.append(Risk.CSV_REPLAY_CONVERSION_FAILED)
    risks.extend(_boundary_risks(payload))
    return _dedupe(risks)


def generate_csv_replay_input_v1_recommendations(
    risks: Iterable[Risk],
) -> tuple[Recommendation, ...]:
    mapping = {
        Risk.CSV_REPLAY_INPUT_MISSING: Recommendation.PROVIDE_CSV_REPLAY_INPUT,
        Risk.CSV_REPLAY_CONTENT_EMPTY: Recommendation.PROVIDE_CSV_REPLAY_CONTENT,
        Risk.CSV_REPLAY_HEADER_MISSING: Recommendation.PROVIDE_REQUIRED_CSV_HEADERS,
        Risk.CSV_REPLAY_HEADER_INVALID: Recommendation.FIX_CSV_REPLAY_HEADERS,
        Risk.CSV_REPLAY_ROW_INVALID: Recommendation.FIX_CSV_REPLAY_ROWS,
        Risk.CSV_REPLAY_NUMERIC_VALUE_INVALID: Recommendation.FIX_CSV_REPLAY_NUMERIC_VALUES,
        Risk.CSV_REPLAY_TIMESTAMP_INVALID: Recommendation.FIX_CSV_REPLAY_TIMESTAMPS,
        Risk.CSV_REPLAY_BAR_INVALID: Recommendation.FIX_CSV_REPLAY_BARS,
        Risk.CSV_REPLAY_OHLCV_INCONSISTENT: Recommendation.FIX_CSV_REPLAY_OHLCV,
        Risk.CSV_REPLAY_VOLUME_INVALID: Recommendation.FIX_CSV_REPLAY_VOLUME,
        Risk.CSV_REPLAY_STATISTICS_MISSING: Recommendation.COMPUTE_CSV_REPLAY_STATISTICS,
        Risk.CSV_REPLAY_CONVERSION_FAILED: Recommendation.FIX_CSV_REPLAY_CONVERSION,
        Risk.FILE_READ_BOUNDARY_VIOLATION: Recommendation.REMOVE_FILE_READ,
        Risk.FILE_WRITE_BOUNDARY_VIOLATION: Recommendation.REMOVE_FILE_WRITE,
        Risk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION: Recommendation.REMOVE_REAL_DATA_ACCESS,
        Risk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION: Recommendation.REMOVE_DATA_DIRECTORY_ACCESS,
        Risk.REAL_BROKER_BOUNDARY_VIOLATION: Recommendation.REMOVE_REAL_BROKER_ACCESS,
        Risk.REAL_SECRET_BOUNDARY_VIOLATION: Recommendation.REMOVE_REAL_SECRET_ACCESS,
        Risk.NETWORK_BOUNDARY_VIOLATION: Recommendation.REMOVE_NETWORK_ACCESS,
        Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION: Recommendation.REMOVE_ORDER_EXECUTION,
        Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION: Recommendation.REMOVE_ACCOUNT_ACCESS,
        Risk.POSITION_MUTATION_BOUNDARY_VIOLATION: Recommendation.REMOVE_POSITION_MUTATION,
    }
    recommendations = [mapping[risk] for risk in risks if risk in mapping]
    recommendations.append(Recommendation.RUN_CSV_REPLAY_INPUT_V1_TEST_SUITE)
    if not recommendations or recommendations == [Recommendation.RUN_CSV_REPLAY_INPUT_V1_TEST_SUITE]:
        recommendations.append(Recommendation.APPROVE_STRATEGY_REPLAY_ENGINE_V1)
    return _dedupe(recommendations)


def assert_csv_replay_input_v1_offline_boundaries(
    data: CsvReplayInputV1Input | Mapping[str, Any] | None,
) -> bool:
    return not _boundary_risks(_coerce_input(data))


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_CSV_REPLAY_INPUT_V1
    boundary_set = {
        Risk.FILE_READ_BOUNDARY_VIOLATION,
        Risk.FILE_WRITE_BOUNDARY_VIOLATION,
        Risk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION,
        Risk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION,
        Risk.REAL_BROKER_BOUNDARY_VIOLATION,
        Risk.REAL_SECRET_BOUNDARY_VIOLATION,
        Risk.NETWORK_BOUNDARY_VIOLATION,
        Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION,
        Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION,
        Risk.POSITION_MUTATION_BOUNDARY_VIOLATION,
    }
    if any(risk in boundary_set for risk in risks):
        return Decision.BLOCK_CSV_REPLAY_INPUT_V1
    if Risk.CSV_REPLAY_INPUT_MISSING in risks or Risk.CSV_REPLAY_CONTENT_EMPTY in risks:
        return Decision.REQUIRE_CSV_REPLAY_INPUT_FIXES
    if Risk.CSV_REPLAY_HEADER_MISSING in risks or Risk.CSV_REPLAY_HEADER_INVALID in risks:
        return Decision.REQUIRE_CSV_REPLAY_HEADER_FIXES
    if (
        Risk.CSV_REPLAY_ROW_INVALID in risks
        or Risk.CSV_REPLAY_NUMERIC_VALUE_INVALID in risks
        or Risk.CSV_REPLAY_TIMESTAMP_INVALID in risks
    ):
        return Decision.REQUIRE_CSV_REPLAY_ROW_FIXES
    if Risk.CSV_REPLAY_BAR_INVALID in risks or Risk.CSV_REPLAY_VOLUME_INVALID in risks:
        return Decision.REQUIRE_CSV_REPLAY_BAR_FIXES
    if Risk.CSV_REPLAY_OHLCV_INCONSISTENT in risks:
        return Decision.REQUIRE_CSV_REPLAY_OHLCV_FIXES
    if Risk.CSV_REPLAY_STATISTICS_MISSING in risks:
        return Decision.REQUIRE_CSV_REPLAY_STATISTICS_FIXES
    if Risk.CSV_REPLAY_CONVERSION_FAILED in risks:
        return Decision.REQUIRE_CSV_REPLAY_CONVERSION_FIXES
    return Decision.BLOCK_CSV_REPLAY_INPUT_V1


def _state_for(risks: tuple[Risk, ...], decision: Decision) -> State:
    if Risk.CSV_REPLAY_INPUT_MISSING in risks or Risk.CSV_REPLAY_CONTENT_EMPTY in risks:
        return State.CSV_REPLAY_INPUT_V1_INPUT_INVALID
    if decision is Decision.APPROVE_CSV_REPLAY_INPUT_V1:
        return State.READY_FOR_STRATEGY_REPLAY_ENGINE_V1
    return State.CSV_REPLAY_INPUT_V1_BLOCKED


def build_csv_replay_input_v1(
    data: CsvReplayInputV1Input | Mapping[str, Any] | None,
) -> CsvReplayInputV1Result:
    payload = _coerce_input(data)
    spec = _header_spec(payload)
    headers_present = False
    headers_valid = False
    raw_rows: tuple[CsvReplayRawRowV1, ...] = ()
    normalized_rows: tuple[CsvReplayNormalizedRowV1, ...] = ()
    bars: tuple[CsvReplayBarV1, ...] = ()
    dataset: CsvReplayDatasetV1 | None = None
    statistics: CsvReplayStatisticsV1 | None = None
    synthetic_conversion: CsvReplayConversionResultV1 | None = None
    controlled_conversion: CsvReplayConversionResultV1 | None = None

    if payload and payload.csv_content.strip():
        reader = csv.reader(StringIO(payload.csv_content.strip()), delimiter=spec.delimiter)
        parsed_lines = tuple(reader)
        headers = tuple(parsed_lines[0]) if parsed_lines else ()
        normalized_headers = {str(header).strip().lower() for header in headers}
        headers_present = bool(normalized_headers & set(spec.required_columns))
        headers_valid = validate_csv_replay_headers_v1(headers, spec)
        raw_rows = parse_csv_replay_content_v1(payload) if headers_valid else ()
        normalized: list[CsvReplayNormalizedRowV1] = []
        built_bars: list[CsvReplayBarV1] = []
        for row in raw_rows:
            if validate_csv_replay_row_v1(row, spec):
                normalized_row = normalize_csv_replay_row_v1(row)
                normalized.append(normalized_row)
                built_bars.append(build_csv_replay_bar_v1(normalized_row, payload.symbol))
        normalized_rows = tuple(normalized)
        bars = tuple(built_bars)
        if bars:
            dataset = CsvReplayDatasetV1(dataset_id=payload.dataset_id, symbol=payload.symbol, bars=bars)
        if dataset and not payload.force_statistics_missing:
            statistics = compute_csv_replay_statistics_v1(dataset.bars)
        if dataset and not payload.force_conversion_failed:
            synthetic_conversion = convert_csv_replay_to_synthetic_market_scenario_v1(dataset)
            controlled_conversion = convert_csv_replay_to_controlled_offline_runner_scenario_v1(dataset)
        elif dataset:
            synthetic_conversion = CsvReplayConversionResultV1(
                converted=False,
                target="SYNTHETIC_MARKET_SCENARIO_V1",
                risks=(Risk.CSV_REPLAY_CONVERSION_FAILED,),
            )
            controlled_conversion = CsvReplayConversionResultV1(
                converted=False,
                target="CONTROLLED_OFFLINE_RUNNER_MINIMAL",
                risks=(Risk.CSV_REPLAY_CONVERSION_FAILED,),
            )

    risks = detect_csv_replay_input_v1_risks(
        payload,
        headers_present=headers_present,
        headers_valid=headers_valid,
        raw_rows=raw_rows,
        normalized_rows=normalized_rows,
        bars=bars,
        statistics=statistics,
        synthetic_conversion=synthetic_conversion,
        controlled_conversion=controlled_conversion,
    )
    recommendations = generate_csv_replay_input_v1_recommendations(risks)
    score = compute_csv_replay_input_v1_score(
        payload,
        headers_valid=headers_valid,
        raw_rows=raw_rows,
        normalized_rows=normalized_rows,
        bars=bars,
        statistics=statistics,
        synthetic_conversion=synthetic_conversion,
        controlled_conversion=controlled_conversion,
        risks=risks,
    )
    decision = _decision_for(risks)
    state = _state_for(risks, decision)
    result_without_report = CsvReplayInputV1Result(
        state=state,
        decision=decision,
        score=score,
        risks=risks,
        recommendations=recommendations,
        header_spec=spec,
        raw_rows=raw_rows,
        normalized_rows=normalized_rows,
        dataset=dataset,
        statistics=statistics,
        synthetic_market_conversion=synthetic_conversion,
        controlled_runner_conversion=controlled_conversion,
    )
    report = CsvReplayInputV1Report(
        markdown=render_csv_replay_input_v1_markdown_report(result_without_report),
        json=render_csv_replay_input_v1_json_report(result_without_report),
    )
    return CsvReplayInputV1Result(
        state=state,
        decision=decision,
        score=score,
        risks=risks,
        recommendations=recommendations,
        header_spec=spec,
        raw_rows=raw_rows,
        normalized_rows=normalized_rows,
        dataset=dataset,
        statistics=statistics,
        synthetic_market_conversion=synthetic_conversion,
        controlled_runner_conversion=controlled_conversion,
        report=report,
        offline_only=True,
        in_memory_only=True,
        file_read=False,
        file_written=False,
        data_accessed=False,
        real_order_submitted=False,
        real_account_accessed=False,
        position_mutated=False,
    )
