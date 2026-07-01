from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agicore.trading.strategy_replay_engine_v1 import (
    apply_strategy_replay_risk_guards_v1,
    assert_strategy_replay_engine_v1_offline_boundaries,
    build_strategy_read_only_decision_v1,
    build_strategy_replay_context_v1,
    build_strategy_replay_journal_v1,
    build_strategy_replay_report_v1,
    compute_breakout_signal_v1,
    compute_mean_reversion_signal_v1,
    compute_moving_average_signal_v1,
    compute_strategy_replay_metrics_v1,
    compute_strategy_replay_signal_v1,
    detect_strategy_replay_engine_v1_risks,
    generate_strategy_replay_engine_v1_recommendations,
    normalize_strategy_replay_bars_v1,
    render_strategy_replay_engine_v1_json_report,
    render_strategy_replay_engine_v1_markdown_report,
    run_strategy_replay_engine_v1,
    simulate_strategy_replay_broker_preview_v1,
    validate_strategy_replay_bars_v1,
    validate_strategy_replay_engine_v1_input,
)
from agicore.trading.strategy_replay_engine_v1_models import (
    StrategyReplayEngineV1Decision,
    StrategyReplayEngineV1Input,
    StrategyReplayEngineV1Recommendation,
    StrategyReplayEngineV1Risk,
    StrategyReplayEngineV1State,
    StrategyReplayStrategyTypeV1,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/strategy_replay_engine_v1.py"


TREND_UP_BARS = (
    {"timestamp": "2026-01-01T00:00:00", "open": 100, "high": 105, "low": 99, "close": 104, "volume": 1000},
    {"timestamp": "2026-01-01T00:01:00", "open": 104, "high": 108, "low": 103, "close": 107, "volume": 1000},
    {"timestamp": "2026-01-01T00:02:00", "open": 107, "high": 110, "low": 106, "close": 109, "volume": 1000},
    {"timestamp": "2026-01-01T00:03:00", "open": 109, "high": 112, "low": 108, "close": 111, "volume": 1000},
)


BREAKOUT_BARS = (
    {"timestamp": "2026-01-01T00:00:00", "open": 100, "high": 105, "low": 99, "close": 101, "volume": 1000},
    {"timestamp": "2026-01-01T00:01:00", "open": 101, "high": 106, "low": 100, "close": 102, "volume": 1000},
    {"timestamp": "2026-01-01T00:02:00", "open": 102, "high": 107, "low": 101, "close": 103, "volume": 1000},
    {"timestamp": "2026-01-01T00:03:00", "open": 103, "high": 112, "low": 102, "close": 110, "volume": 1000},
)


MEAN_REVERSION_BARS = (
    {"timestamp": "2026-01-01T00:00:00", "open": 100, "high": 102, "low": 98, "close": 100, "volume": 1000},
    {"timestamp": "2026-01-01T00:01:00", "open": 100, "high": 102, "low": 98, "close": 100, "volume": 1000},
    {"timestamp": "2026-01-01T00:02:00", "open": 100, "high": 101, "low": 89, "close": 90, "volume": 1000},
)


def _input(strategy=StrategyReplayStrategyTypeV1.MOVING_AVERAGE_CROSSOVER, bars=TREND_UP_BARS, **overrides):
    payload = {
        "bars": bars,
        "strategy_type": strategy,
        "run_id": "replay-001",
        "symbol": "SIM",
        "requested_quantity": 5.0,
        "available_cash": 100_000.0,
    }
    payload.update(overrides)
    return StrategyReplayEngineV1Input(**payload)


def _assert_nominal(result, strategy):
    assert result.decision is StrategyReplayEngineV1Decision.APPROVE_STRATEGY_REPLAY_ENGINE_V1
    assert result.state is StrategyReplayEngineV1State.READY_FOR_AGICORE_TRADING_V1_CANDIDATE
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.context.strategy_type == strategy
    assert result.signal.read_only is True
    assert result.read_only_decision.read_only is True
    assert result.read_only_decision.order_submitted is False
    assert result.risk_result.passed is True
    assert result.broker_preview.read_only is True
    assert result.journal.complete is True
    assert result.metrics.bar_count == len(result.bars)
    assert result.report.markdown
    assert result.report.json


def test_nominal_moving_average_crossover():
    result = run_strategy_replay_engine_v1(_input())

    _assert_nominal(result, StrategyReplayStrategyTypeV1.MOVING_AVERAGE_CROSSOVER)
    assert result.signal.action == "BUY"


def test_nominal_breakout():
    result = run_strategy_replay_engine_v1(
        _input(StrategyReplayStrategyTypeV1.BREAKOUT, bars=BREAKOUT_BARS)
    )

    _assert_nominal(result, StrategyReplayStrategyTypeV1.BREAKOUT)
    assert result.signal.action == "BUY"


def test_nominal_mean_reversion():
    result = run_strategy_replay_engine_v1(
        _input(StrategyReplayStrategyTypeV1.MEAN_REVERSION, bars=MEAN_REVERSION_BARS)
    )

    _assert_nominal(result, StrategyReplayStrategyTypeV1.MEAN_REVERSION)
    assert result.signal.action == "BUY"


def test_input_missing():
    result = run_strategy_replay_engine_v1(None)

    assert validate_strategy_replay_engine_v1_input(None) is False
    assert StrategyReplayEngineV1Risk.STRATEGY_REPLAY_INPUT_MISSING in result.risks
    assert result.decision is StrategyReplayEngineV1Decision.REQUIRE_STRATEGY_REPLAY_INPUT_FIXES


def test_bars_empty():
    result = run_strategy_replay_engine_v1(_input(bars=()))

    assert StrategyReplayEngineV1Risk.STRATEGY_REPLAY_BARS_EMPTY in result.risks
    assert result.state is StrategyReplayEngineV1State.STRATEGY_REPLAY_ENGINE_V1_INPUT_INVALID
    assert result.decision is StrategyReplayEngineV1Decision.REQUIRE_STRATEGY_REPLAY_BARS_FIXES


def test_bar_invalid():
    result = run_strategy_replay_engine_v1(
        _input(bars=({"timestamp": "2026-01-01", "open": -1, "high": 1, "low": 1, "close": 1, "volume": 1},))
    )

    assert StrategyReplayEngineV1Risk.STRATEGY_REPLAY_BAR_INVALID in result.risks
    assert result.decision is StrategyReplayEngineV1Decision.REQUIRE_STRATEGY_REPLAY_BARS_FIXES


def test_strategy_unsupported():
    result = run_strategy_replay_engine_v1(_input(strategy="BAD_STRATEGY"))

    assert StrategyReplayEngineV1Risk.STRATEGY_REPLAY_STRATEGY_UNSUPPORTED in result.risks
    assert result.decision is StrategyReplayEngineV1Decision.REQUIRE_STRATEGY_REPLAY_INPUT_FIXES


def test_signal_invalid():
    result = run_strategy_replay_engine_v1(_input(force_signal_invalid=True))

    assert StrategyReplayEngineV1Risk.STRATEGY_REPLAY_SIGNAL_INVALID in result.risks
    assert result.decision is StrategyReplayEngineV1Decision.REQUIRE_STRATEGY_SIGNAL_FIXES


def test_read_only_decision_invalid():
    result = run_strategy_replay_engine_v1(_input(force_read_only_decision_invalid=True))

    assert StrategyReplayEngineV1Risk.STRATEGY_REPLAY_READ_ONLY_DECISION_INVALID in result.risks
    assert result.decision is StrategyReplayEngineV1Decision.REQUIRE_STRATEGY_READ_ONLY_DECISION_FIXES


def test_risk_guard_failed():
    result = run_strategy_replay_engine_v1(_input(force_risk_guard_failed=True))

    assert StrategyReplayEngineV1Risk.STRATEGY_REPLAY_RISK_GUARD_FAILED in result.risks
    assert result.decision is StrategyReplayEngineV1Decision.REQUIRE_STRATEGY_RISK_GUARD_FIXES


def test_broker_preview_failed():
    result = run_strategy_replay_engine_v1(_input(force_broker_preview_failed=True))

    assert StrategyReplayEngineV1Risk.STRATEGY_REPLAY_BROKER_PREVIEW_FAILED in result.risks
    assert result.decision is StrategyReplayEngineV1Decision.REQUIRE_STRATEGY_BROKER_PREVIEW_FIXES


def test_journal_missing():
    result = run_strategy_replay_engine_v1(_input(force_journal_missing=True))

    assert StrategyReplayEngineV1Risk.STRATEGY_REPLAY_JOURNAL_MISSING in result.risks
    assert result.decision is StrategyReplayEngineV1Decision.REQUIRE_STRATEGY_JOURNAL_FIXES


def test_metrics_missing():
    result = run_strategy_replay_engine_v1(_input(force_metrics_missing=True))

    assert StrategyReplayEngineV1Risk.STRATEGY_REPLAY_METRICS_MISSING in result.risks
    assert result.decision is StrategyReplayEngineV1Decision.REQUIRE_STRATEGY_METRICS_FIXES


def test_report_missing():
    result = run_strategy_replay_engine_v1(_input(force_report_missing=True))

    assert StrategyReplayEngineV1Risk.STRATEGY_REPLAY_REPORT_MISSING in result.risks
    assert result.decision is StrategyReplayEngineV1Decision.REQUIRE_STRATEGY_REPORT_FIXES


def test_direct_signal_functions_and_pipeline_helpers():
    data = _input()
    context = build_strategy_replay_context_v1(data)
    bars = normalize_strategy_replay_bars_v1(data.bars, data.symbol)
    signal = compute_strategy_replay_signal_v1(context, bars, data)
    decision = build_strategy_read_only_decision_v1(signal, data)
    risk = apply_strategy_replay_risk_guards_v1(context, bars, decision, data)
    broker = simulate_strategy_replay_broker_preview_v1(decision, data)
    journal = build_strategy_replay_journal_v1(context, signal, decision, risk, broker, data)
    metrics = compute_strategy_replay_metrics_v1(context, signal, decision, risk, broker, journal, data)

    assert validate_strategy_replay_bars_v1(bars) is True
    assert compute_moving_average_signal_v1(bars).action == "BUY"
    assert compute_breakout_signal_v1(normalize_strategy_replay_bars_v1(BREAKOUT_BARS)).action == "BUY"
    assert compute_mean_reversion_signal_v1(normalize_strategy_replay_bars_v1(MEAN_REVERSION_BARS)).action == "BUY"
    assert decision.read_only is True
    assert risk.passed is True
    assert broker.accepted is True
    assert journal.complete is True
    assert metrics.strategy_used == "MOVING_AVERAGE_CROSSOVER"


def test_markdown_report():
    result = run_strategy_replay_engine_v1(_input())
    markdown = render_strategy_replay_engine_v1_markdown_report(result)

    assert "# Strategy Replay Engine v1" in markdown
    assert "file_read: false" in markdown
    assert "real_order_submitted: false" in markdown


def test_json_report():
    result = run_strategy_replay_engine_v1(_input())
    payload = json.loads(render_strategy_replay_engine_v1_json_report(result))

    assert payload["schema"] == "strategy_replay_engine_v1"
    assert payload["decision"] == "APPROVE_STRATEGY_REPLAY_ENGINE_V1"
    assert payload["metrics"]["bar_count"] == 4


def test_build_report_directly():
    result = run_strategy_replay_engine_v1(_input())
    report = build_strategy_replay_report_v1(result, _input())

    assert report.markdown
    assert json.loads(report.json)["state"] == "READY_FOR_AGICORE_TRADING_V1_CANDIDATE"


def test_risks_can_be_detected_directly():
    result = run_strategy_replay_engine_v1(_input())
    risks = detect_strategy_replay_engine_v1_risks(
        _input(),
        bars=result.bars,
        signal=result.signal,
        read_only_decision=result.read_only_decision,
        risk_result=result.risk_result,
        broker_preview=result.broker_preview,
        journal=result.journal,
        metrics=result.metrics,
        report=result.report,
    )

    assert risks == ()


def test_recommendations_generated():
    recommendations = generate_strategy_replay_engine_v1_recommendations(
        (StrategyReplayEngineV1Risk.STRATEGY_REPLAY_SIGNAL_INVALID,)
    )

    assert StrategyReplayEngineV1Recommendation.FIX_STRATEGY_SIGNAL in recommendations
    assert StrategyReplayEngineV1Recommendation.RUN_STRATEGY_REPLAY_ENGINE_V1_TEST_SUITE in recommendations


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("file_read_requested", StrategyReplayEngineV1Risk.FILE_READ_BOUNDARY_VIOLATION),
        ("file_write_requested", StrategyReplayEngineV1Risk.FILE_WRITE_BOUNDARY_VIOLATION),
        ("real_data_access_requested", StrategyReplayEngineV1Risk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_read_requested", StrategyReplayEngineV1Risk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_write_requested", StrategyReplayEngineV1Risk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("broker_connection_requested", StrategyReplayEngineV1Risk.REAL_BROKER_BOUNDARY_VIOLATION),
        ("api_key_read_requested", StrategyReplayEngineV1Risk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("env_var_read_requested", StrategyReplayEngineV1Risk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("network_requested", StrategyReplayEngineV1Risk.NETWORK_BOUNDARY_VIOLATION),
        ("http_requested", StrategyReplayEngineV1Risk.NETWORK_BOUNDARY_VIOLATION),
        ("websocket_requested", StrategyReplayEngineV1Risk.NETWORK_BOUNDARY_VIOLATION),
        ("socket_requested", StrategyReplayEngineV1Risk.NETWORK_BOUNDARY_VIOLATION),
        ("order_execution_requested", StrategyReplayEngineV1Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ("account_access_requested", StrategyReplayEngineV1Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ("position_mutation_requested", StrategyReplayEngineV1Risk.POSITION_MUTATION_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations_are_blocked(field, risk):
    data = _input(**{field: True})
    result = run_strategy_replay_engine_v1(data)

    assert risk in result.risks
    assert result.decision is StrategyReplayEngineV1Decision.BLOCK_STRATEGY_REPLAY_ENGINE_V1
    assert assert_strategy_replay_engine_v1_offline_boundaries(data) is False


def test_no_file_read_or_write_calls_in_module_source():
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert "open(" not in source
    assert ".write(" not in source
    assert "write_text" not in source
    assert "read_text" not in source
    assert "Path(" not in source
    assert "data/" not in source


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
    result = run_strategy_replay_engine_v1(_input())

    assert result.file_read is False
    assert result.file_written is False
    assert result.data_accessed is False
    assert result.real_order_submitted is False
    assert result.real_account_accessed is False
    assert result.position_mutated is False
    assert result.read_only_decision.order_submitted is False
    assert result.broker_preview.order_submitted is False
