from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agicore.trading.controlled_offline_runner_minimal_models import (
    ControlledOfflineSyntheticMarketScenario,
)
from agicore.trading.csv_replay_input_v1 import (
    assert_csv_replay_input_v1_offline_boundaries,
    build_csv_replay_bar_v1,
    build_csv_replay_input_v1,
    compute_csv_replay_statistics_v1,
    convert_csv_replay_to_controlled_offline_runner_scenario_v1,
    convert_csv_replay_to_synthetic_market_scenario_v1,
    detect_csv_replay_input_v1_risks,
    generate_csv_replay_input_v1_recommendations,
    normalize_csv_replay_row_v1,
    parse_csv_replay_content_v1,
    render_csv_replay_input_v1_json_report,
    render_csv_replay_input_v1_markdown_report,
    validate_csv_replay_bars_v1,
    validate_csv_replay_headers_v1,
    validate_csv_replay_input_v1_input,
    validate_csv_replay_ohlcv_consistency_v1,
    validate_csv_replay_row_v1,
)
from agicore.trading.csv_replay_input_v1_models import (
    CsvReplayInputV1Decision,
    CsvReplayInputV1Input,
    CsvReplayInputV1Recommendation,
    CsvReplayInputV1Risk,
    CsvReplayInputV1State,
)
from agicore.trading.synthetic_market_scenario_v1_models import SyntheticMarketScenarioV1


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/csv_replay_input_v1.py"


CSV_CONTENT = """timestamp,open,high,low,close,volume
2026-01-01T00:00:00,100,105,99,104,1000
2026-01-01T00:01:00,104,108,103,107,1200
2026-01-01T00:02:00,107,110,106,109,1400
"""


def _input(csv_content: str = CSV_CONTENT, **overrides):
    payload = {
        "csv_content": csv_content,
        "dataset_id": "csv-001",
        "symbol": "SIM",
    }
    payload.update(overrides)
    return CsvReplayInputV1Input(**payload)


def test_nominal_complete_csv():
    result = build_csv_replay_input_v1(_input())

    assert result.decision is CsvReplayInputV1Decision.APPROVE_CSV_REPLAY_INPUT_V1
    assert result.state is CsvReplayInputV1State.READY_FOR_STRATEGY_REPLAY_ENGINE_V1
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.statistics.bar_count == 3
    assert result.synthetic_market_conversion.converted is True
    assert result.controlled_runner_conversion.converted is True
    assert result.report.markdown
    assert result.report.json


def test_input_missing():
    result = build_csv_replay_input_v1(None)

    assert validate_csv_replay_input_v1_input(None) is False
    assert CsvReplayInputV1Risk.CSV_REPLAY_INPUT_MISSING in result.risks
    assert result.decision is CsvReplayInputV1Decision.REQUIRE_CSV_REPLAY_INPUT_FIXES
    assert result.state is CsvReplayInputV1State.CSV_REPLAY_INPUT_V1_INPUT_INVALID


def test_csv_content_empty():
    result = build_csv_replay_input_v1(_input(""))

    assert CsvReplayInputV1Risk.CSV_REPLAY_CONTENT_EMPTY in result.risks
    assert result.decision is CsvReplayInputV1Decision.REQUIRE_CSV_REPLAY_INPUT_FIXES


def test_headers_missing():
    result = build_csv_replay_input_v1(_input("100,105,99,104,1000\n101,106,100,105,1000\n"))

    assert CsvReplayInputV1Risk.CSV_REPLAY_HEADER_MISSING in result.risks
    assert result.decision is CsvReplayInputV1Decision.REQUIRE_CSV_REPLAY_HEADER_FIXES


def test_headers_invalid():
    content = """timestamp,open,high,low,last,volume
2026-01-01T00:00:00,100,105,99,104,1000
"""
    result = build_csv_replay_input_v1(_input(content))

    assert validate_csv_replay_headers_v1(("timestamp", "open", "high", "low", "last", "volume")) is False
    assert CsvReplayInputV1Risk.CSV_REPLAY_HEADER_INVALID in result.risks
    assert result.decision is CsvReplayInputV1Decision.REQUIRE_CSV_REPLAY_HEADER_FIXES


def test_row_invalid():
    content = """timestamp,open,high,low,close,volume
2026-01-01T00:00:00,100,105,99,,1000
"""
    result = build_csv_replay_input_v1(_input(content))

    assert CsvReplayInputV1Risk.CSV_REPLAY_ROW_INVALID in result.risks
    assert result.decision is CsvReplayInputV1Decision.REQUIRE_CSV_REPLAY_ROW_FIXES


def test_numeric_value_invalid():
    content = """timestamp,open,high,low,close,volume
2026-01-01T00:00:00,100,bad,99,104,1000
"""
    result = build_csv_replay_input_v1(_input(content))

    assert CsvReplayInputV1Risk.CSV_REPLAY_NUMERIC_VALUE_INVALID in result.risks
    assert result.decision is CsvReplayInputV1Decision.REQUIRE_CSV_REPLAY_ROW_FIXES


def test_timestamp_invalid():
    content = """timestamp,open,high,low,close,volume
bad-time,100,105,99,104,1000
"""
    result = build_csv_replay_input_v1(_input(content))

    assert CsvReplayInputV1Risk.CSV_REPLAY_TIMESTAMP_INVALID in result.risks
    assert result.decision is CsvReplayInputV1Decision.REQUIRE_CSV_REPLAY_ROW_FIXES


def test_bar_invalid():
    content = """timestamp,open,high,low,close,volume
2026-01-01T00:00:00,-100,105,99,104,1000
"""
    result = build_csv_replay_input_v1(_input(content))

    assert CsvReplayInputV1Risk.CSV_REPLAY_BAR_INVALID in result.risks
    assert result.decision is CsvReplayInputV1Decision.REQUIRE_CSV_REPLAY_BAR_FIXES


def test_ohlcv_inconsistent():
    content = """timestamp,open,high,low,close,volume
2026-01-01T00:00:00,100,101,99,104,1000
"""
    result = build_csv_replay_input_v1(_input(content))

    assert CsvReplayInputV1Risk.CSV_REPLAY_OHLCV_INCONSISTENT in result.risks
    assert result.decision is CsvReplayInputV1Decision.REQUIRE_CSV_REPLAY_OHLCV_FIXES


def test_volume_invalid():
    content = """timestamp,open,high,low,close,volume
2026-01-01T00:00:00,100,105,99,104,-1
"""
    result = build_csv_replay_input_v1(_input(content))

    assert CsvReplayInputV1Risk.CSV_REPLAY_VOLUME_INVALID in result.risks
    assert CsvReplayInputV1Risk.CSV_REPLAY_BAR_INVALID in result.risks


def test_statistics_calculated():
    result = build_csv_replay_input_v1(_input())
    stats = compute_csv_replay_statistics_v1(result.dataset.bars)

    assert stats.bar_count == 3
    assert stats.initial_timestamp == "2026-01-01T00:00:00"
    assert stats.final_timestamp == "2026-01-01T00:02:00"
    assert stats.initial_price == 100.0
    assert stats.final_price == 109.0
    assert stats.absolute_change == 9.0
    assert stats.percent_change == 0.09
    assert stats.total_volume == 3600.0
    assert stats.max_high == 110.0
    assert stats.min_low == 99.0


def test_statistics_missing():
    result = build_csv_replay_input_v1(_input(force_statistics_missing=True))

    assert CsvReplayInputV1Risk.CSV_REPLAY_STATISTICS_MISSING in result.risks
    assert result.decision is CsvReplayInputV1Decision.REQUIRE_CSV_REPLAY_STATISTICS_FIXES


def test_conversion_to_synthetic_market_scenario_v1():
    result = build_csv_replay_input_v1(_input())
    conversion = convert_csv_replay_to_synthetic_market_scenario_v1(result.dataset)

    assert conversion.converted is True
    assert isinstance(conversion.scenario, SyntheticMarketScenarioV1)
    assert conversion.scenario.bars[0].timestamp == "2026-01-01T00:00:00"


def test_conversion_to_controlled_offline_runner_minimal():
    result = build_csv_replay_input_v1(_input())
    conversion = convert_csv_replay_to_controlled_offline_runner_scenario_v1(result.dataset)

    assert conversion.converted is True
    assert isinstance(conversion.scenario, ControlledOfflineSyntheticMarketScenario)
    assert conversion.scenario.bars[0].step == 0


def test_conversion_failed():
    result = build_csv_replay_input_v1(_input(force_conversion_failed=True))

    assert CsvReplayInputV1Risk.CSV_REPLAY_CONVERSION_FAILED in result.risks
    assert result.decision is CsvReplayInputV1Decision.REQUIRE_CSV_REPLAY_CONVERSION_FIXES


def test_parse_normalize_build_and_validate_directly():
    raw_rows = parse_csv_replay_content_v1(_input())
    normalized = normalize_csv_replay_row_v1(raw_rows[0])
    bar = build_csv_replay_bar_v1(normalized, "SIM")

    assert validate_csv_replay_row_v1(raw_rows[0]) is True
    assert bar.close == 104.0
    assert validate_csv_replay_bars_v1((bar,)) is True
    assert validate_csv_replay_ohlcv_consistency_v1((bar,)) is True


def test_report_markdown():
    result = build_csv_replay_input_v1(_input())
    markdown = render_csv_replay_input_v1_markdown_report(result)

    assert "# CSV Replay Input v1" in markdown
    assert "file_read: false" in markdown
    assert "bars: 3" in markdown


def test_report_json():
    result = build_csv_replay_input_v1(_input())
    payload = json.loads(render_csv_replay_input_v1_json_report(result))

    assert payload["schema"] == "csv_replay_input_v1"
    assert payload["decision"] == "APPROVE_CSV_REPLAY_INPUT_V1"
    assert payload["statistics"]["bar_count"] == 3


def test_recommendations_generated():
    recommendations = generate_csv_replay_input_v1_recommendations(
        (CsvReplayInputV1Risk.CSV_REPLAY_HEADER_INVALID,)
    )

    assert CsvReplayInputV1Recommendation.FIX_CSV_REPLAY_HEADERS in recommendations
    assert CsvReplayInputV1Recommendation.RUN_CSV_REPLAY_INPUT_V1_TEST_SUITE in recommendations


def test_risks_can_be_detected_directly():
    result = build_csv_replay_input_v1(_input())
    risks = detect_csv_replay_input_v1_risks(
        _input(),
        headers_present=True,
        headers_valid=True,
        raw_rows=result.raw_rows,
        normalized_rows=result.normalized_rows,
        bars=result.dataset.bars,
        statistics=result.statistics,
        synthetic_conversion=result.synthetic_market_conversion,
        controlled_conversion=result.controlled_runner_conversion,
    )

    assert risks == ()


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("file_read_requested", CsvReplayInputV1Risk.FILE_READ_BOUNDARY_VIOLATION),
        ("file_write_requested", CsvReplayInputV1Risk.FILE_WRITE_BOUNDARY_VIOLATION),
        ("real_data_access_requested", CsvReplayInputV1Risk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_read_requested", CsvReplayInputV1Risk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_write_requested", CsvReplayInputV1Risk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("broker_connection_requested", CsvReplayInputV1Risk.REAL_BROKER_BOUNDARY_VIOLATION),
        ("api_key_read_requested", CsvReplayInputV1Risk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("env_var_read_requested", CsvReplayInputV1Risk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("network_requested", CsvReplayInputV1Risk.NETWORK_BOUNDARY_VIOLATION),
        ("http_requested", CsvReplayInputV1Risk.NETWORK_BOUNDARY_VIOLATION),
        ("websocket_requested", CsvReplayInputV1Risk.NETWORK_BOUNDARY_VIOLATION),
        ("socket_requested", CsvReplayInputV1Risk.NETWORK_BOUNDARY_VIOLATION),
        ("order_execution_requested", CsvReplayInputV1Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ("account_access_requested", CsvReplayInputV1Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ("position_mutation_requested", CsvReplayInputV1Risk.POSITION_MUTATION_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations_are_blocked(field, risk):
    data = _input(**{field: True})
    result = build_csv_replay_input_v1(data)

    assert risk in result.risks
    assert result.decision is CsvReplayInputV1Decision.BLOCK_CSV_REPLAY_INPUT_V1
    assert assert_csv_replay_input_v1_offline_boundaries(data) is False


def test_no_file_read_or_write_calls_in_module_source():
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert "open(" not in source
    assert ".write(" not in source
    assert "write_text" not in source
    assert "read_text" not in source
    assert "Path(" not in source


def test_no_network_socket_http_websocket_imports_or_calls():
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    forbidden_imports = {"requests", "httpx", "urllib", "socket", "websocket"}
    forbidden_calls = {"request", "urlopen", "connect", "send", "create_connection"}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert not {alias.name.split(".")[0] for alias in node.names} & forbidden_imports
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in forbidden_imports
        if isinstance(node, ast.Call):
            func_name = getattr(node.func, "attr", getattr(node.func, "id", ""))
            assert func_name not in forbidden_calls


def test_no_real_secret_environment_read():
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert all(alias.name != "os" for alias in node.names)
        if isinstance(node, ast.Attribute):
            assert node.attr not in {"environ", "getenv"}
        if isinstance(node, ast.Call):
            assert getattr(node.func, "attr", "") != "getenv"


def test_no_order_account_or_position_side_effects_are_reported():
    result = build_csv_replay_input_v1(_input())

    assert result.file_read is False
    assert result.file_written is False
    assert result.data_accessed is False
    assert result.real_order_submitted is False
    assert result.real_account_accessed is False
    assert result.position_mutated is False
