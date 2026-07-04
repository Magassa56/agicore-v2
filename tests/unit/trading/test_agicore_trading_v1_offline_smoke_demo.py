from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agicore.trading.agicore_trading_v1_offline_smoke_demo import (
    assert_agicore_trading_v1_offline_smoke_demo_boundaries,
    build_offline_smoke_demo_context,
    build_offline_smoke_demo_csv_string,
    build_offline_smoke_demo_market_bars,
    compute_agicore_trading_v1_offline_smoke_demo_metrics,
    compute_agicore_trading_v1_offline_smoke_demo_score,
    detect_agicore_trading_v1_offline_smoke_demo_risks,
    generate_agicore_trading_v1_offline_smoke_demo_recommendations,
    render_agicore_trading_v1_offline_smoke_demo_json_report,
    render_agicore_trading_v1_offline_smoke_demo_markdown_report,
    run_agicore_trading_v1_offline_smoke_demo,
    run_offline_smoke_demo_broker_preview_step,
    run_offline_smoke_demo_csv_replay_step,
    run_offline_smoke_demo_journal_step,
    run_offline_smoke_demo_report_step,
    run_offline_smoke_demo_risk_guard_step,
    run_offline_smoke_demo_strategy_replay_step,
    validate_agicore_trading_v1_offline_smoke_demo_input,
    validate_offline_smoke_demo_end_to_end_result,
    validate_offline_smoke_demo_no_live_trading_claim,
    validate_offline_smoke_demo_no_profitability_claim,
    validate_offline_smoke_demo_read_only_decision,
)
from agicore.trading.agicore_trading_v1_offline_smoke_demo_models import (
    AGIcoreTradingV1OfflineSmokeDemoDecision,
    AGIcoreTradingV1OfflineSmokeDemoInput,
    AGIcoreTradingV1OfflineSmokeDemoRecommendation,
    AGIcoreTradingV1OfflineSmokeDemoRisk,
    AGIcoreTradingV1OfflineSmokeDemoState,
    AGIcoreTradingV1OfflineSmokeDemoStepStatus,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/agicore_trading_v1_offline_smoke_demo.py"


def _input(**overrides):
    return AGIcoreTradingV1OfflineSmokeDemoInput(**overrides)


def test_nominal_smoke_demo_complet():
    result = run_agicore_trading_v1_offline_smoke_demo(_input())

    assert result.decision is AGIcoreTradingV1OfflineSmokeDemoDecision.APPROVE_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO
    assert result.state is AGIcoreTradingV1OfflineSmokeDemoState.READY_FOR_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_REVIEW
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert len(result.steps) == 7
    assert all(step.status is AGIcoreTradingV1OfflineSmokeDemoStepStatus.PASSED for step in result.steps)
    assert result.metrics.expected_step_count == 7
    assert result.metrics.passed_step_count == 7
    assert result.metrics.read_only_decision is True
    assert result.metrics.broker_preview_read_only is True
    assert result.metrics.journal_entry_count > 0
    assert validate_offline_smoke_demo_read_only_decision(result)
    assert "live_trading_ready: false" in result.report.markdown


def test_input_manquant():
    result = run_agicore_trading_v1_offline_smoke_demo(None)

    assert validate_agicore_trading_v1_offline_smoke_demo_input(None) is False
    assert AGIcoreTradingV1OfflineSmokeDemoRisk.SMOKE_DEMO_INPUT_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineSmokeDemoDecision.REQUIRE_SMOKE_DEMO_INPUT_FIXES
    assert result.state is AGIcoreTradingV1OfflineSmokeDemoState.AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_INPUT_INVALID


@pytest.mark.parametrize(
    ("field", "risk", "decision"),
    (
        (
            "force_csv_replay_failed",
            AGIcoreTradingV1OfflineSmokeDemoRisk.SMOKE_DEMO_CSV_REPLAY_FAILED,
            AGIcoreTradingV1OfflineSmokeDemoDecision.REQUIRE_SMOKE_DEMO_CSV_REPLAY_FIXES,
        ),
        (
            "force_strategy_replay_failed",
            AGIcoreTradingV1OfflineSmokeDemoRisk.SMOKE_DEMO_STRATEGY_REPLAY_FAILED,
            AGIcoreTradingV1OfflineSmokeDemoDecision.REQUIRE_SMOKE_DEMO_STRATEGY_REPLAY_FIXES,
        ),
        (
            "force_risk_guard_failed",
            AGIcoreTradingV1OfflineSmokeDemoRisk.SMOKE_DEMO_RISK_GUARD_FAILED,
            AGIcoreTradingV1OfflineSmokeDemoDecision.REQUIRE_SMOKE_DEMO_RISK_GUARD_FIXES,
        ),
        (
            "force_broker_preview_failed",
            AGIcoreTradingV1OfflineSmokeDemoRisk.SMOKE_DEMO_BROKER_PREVIEW_FAILED,
            AGIcoreTradingV1OfflineSmokeDemoDecision.REQUIRE_SMOKE_DEMO_BROKER_PREVIEW_FIXES,
        ),
        (
            "force_journal_failed",
            AGIcoreTradingV1OfflineSmokeDemoRisk.SMOKE_DEMO_JOURNAL_FAILED,
            AGIcoreTradingV1OfflineSmokeDemoDecision.REQUIRE_SMOKE_DEMO_JOURNAL_FIXES,
        ),
        (
            "force_report_failed",
            AGIcoreTradingV1OfflineSmokeDemoRisk.SMOKE_DEMO_REPORT_FAILED,
            AGIcoreTradingV1OfflineSmokeDemoDecision.REQUIRE_SMOKE_DEMO_REPORT_FIXES,
        ),
    ),
)
def test_step_failures_are_detected(field, risk, decision):
    result = run_agicore_trading_v1_offline_smoke_demo(_input(**{field: True}))

    assert risk in result.risks
    assert result.decision is decision
    assert result.state is AGIcoreTradingV1OfflineSmokeDemoState.AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_BLOCKED
    assert result.score.overall_score < 100


def test_end_to_end_validation_failed():
    result = run_agicore_trading_v1_offline_smoke_demo(_input(force_end_to_end_validation_failed=True))

    assert AGIcoreTradingV1OfflineSmokeDemoRisk.SMOKE_DEMO_END_TO_END_VALIDATION_FAILED in result.risks
    assert result.decision is AGIcoreTradingV1OfflineSmokeDemoDecision.BLOCK_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("force_live_trading_overclaim", AGIcoreTradingV1OfflineSmokeDemoRisk.LIVE_TRADING_READINESS_OVERCLAIM),
        ("force_real_broker_overclaim", AGIcoreTradingV1OfflineSmokeDemoRisk.REAL_BROKER_READINESS_OVERCLAIM),
        ("force_real_order_overclaim", AGIcoreTradingV1OfflineSmokeDemoRisk.REAL_ORDER_EXECUTION_OVERCLAIM),
        ("force_profitability_overclaim", AGIcoreTradingV1OfflineSmokeDemoRisk.PROFITABILITY_PROOF_OVERCLAIM),
        ("force_financial_advice_overclaim", AGIcoreTradingV1OfflineSmokeDemoRisk.FINANCIAL_ADVICE_OVERCLAIM),
    ),
)
def test_overclaims_are_rejected(field, risk):
    result = run_agicore_trading_v1_offline_smoke_demo(_input(**{field: True}))

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineSmokeDemoDecision.REQUIRE_SMOKE_DEMO_BOUNDARY_FIXES


def test_profitability_and_live_trading_claim_validators():
    assert validate_offline_smoke_demo_no_profitability_claim(_input())
    assert validate_offline_smoke_demo_no_live_trading_claim(_input())
    assert validate_offline_smoke_demo_no_profitability_claim(_input(force_profitability_overclaim=True)) is False
    assert validate_offline_smoke_demo_no_live_trading_claim(_input(force_live_trading_overclaim=True)) is False
    assert validate_offline_smoke_demo_no_profitability_claim("profitability_proven: true") is False
    assert validate_offline_smoke_demo_no_live_trading_claim("live_trading_ready: true") is False


def test_markdown_report():
    result = run_agicore_trading_v1_offline_smoke_demo(_input())
    markdown = render_agicore_trading_v1_offline_smoke_demo_markdown_report(result)

    assert "# AGIcore Trading v1 Offline Smoke Demo" in markdown
    assert "CSV_REPLAY_INPUT_STEP: PASSED" in markdown
    assert "real_order_execution: false" in markdown
    assert "profitability_proven: false" in markdown


def test_json_report():
    result = run_agicore_trading_v1_offline_smoke_demo(_input())
    payload = json.loads(render_agicore_trading_v1_offline_smoke_demo_json_report(result))

    assert payload["schema"] == "agicore_trading_v1_offline_smoke_demo"
    assert payload["decision"] == "APPROVE_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO"
    assert payload["score"] == 100
    assert payload["live_trading_ready"] is False
    assert payload["real_broker_ready"] is False
    assert payload["real_order_execution"] is False
    assert payload["profitability_proven"] is False


def test_helpers_and_direct_step_execution():
    data = _input()
    context = build_offline_smoke_demo_context(data)
    csv_content = build_offline_smoke_demo_csv_string(data)
    csv_step = run_offline_smoke_demo_csv_replay_step(data)
    bars = build_offline_smoke_demo_market_bars(csv_step.payload)
    strategy_step = run_offline_smoke_demo_strategy_replay_step(data, bars)
    risk_step = run_offline_smoke_demo_risk_guard_step(data, strategy_step.payload)
    broker_step = run_offline_smoke_demo_broker_preview_step(data, strategy_step.payload)
    journal_step = run_offline_smoke_demo_journal_step(
        data,
        csv_step.payload,
        strategy_step.payload,
        risk_step.payload,
        broker_step.payload,
    )
    report_step = run_offline_smoke_demo_report_step(
        data,
        csv_step.payload,
        strategy_step.payload,
        risk_step.payload,
        broker_step.payload,
        journal_step.payload,
    )

    assert context.run_id == data.run_id
    assert csv_content.startswith("timestamp,open,high,low,close,volume")
    assert len(bars) == 5
    assert csv_step.status is AGIcoreTradingV1OfflineSmokeDemoStepStatus.PASSED
    assert strategy_step.status is AGIcoreTradingV1OfflineSmokeDemoStepStatus.PASSED
    assert risk_step.status is AGIcoreTradingV1OfflineSmokeDemoStepStatus.PASSED
    assert broker_step.status is AGIcoreTradingV1OfflineSmokeDemoStepStatus.PASSED
    assert journal_step.status is AGIcoreTradingV1OfflineSmokeDemoStepStatus.PASSED
    assert report_step.status is AGIcoreTradingV1OfflineSmokeDemoStepStatus.PASSED


def test_score_risks_recommendations_directly():
    result = run_agicore_trading_v1_offline_smoke_demo(_input())
    risks = detect_agicore_trading_v1_offline_smoke_demo_risks(_input(), result.steps, result.metrics)
    score = compute_agicore_trading_v1_offline_smoke_demo_score(_input(), result.steps, result.metrics, risks)
    recommendations = generate_agicore_trading_v1_offline_smoke_demo_recommendations(risks)

    assert validate_offline_smoke_demo_end_to_end_result(result.steps, _input())
    assert risks == ()
    assert score.overall_score == 100
    assert recommendations == (
        AGIcoreTradingV1OfflineSmokeDemoRecommendation.RUN_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_TEST_SUITE,
        AGIcoreTradingV1OfflineSmokeDemoRecommendation.APPROVE_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_REVIEW,
    )


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("file_read_requested", AGIcoreTradingV1OfflineSmokeDemoRisk.FILE_READ_BOUNDARY_VIOLATION),
        ("file_write_requested", AGIcoreTradingV1OfflineSmokeDemoRisk.FILE_WRITE_BOUNDARY_VIOLATION),
        ("real_data_access_requested", AGIcoreTradingV1OfflineSmokeDemoRisk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_read_requested", AGIcoreTradingV1OfflineSmokeDemoRisk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_write_requested", AGIcoreTradingV1OfflineSmokeDemoRisk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("broker_connection_requested", AGIcoreTradingV1OfflineSmokeDemoRisk.REAL_BROKER_BOUNDARY_VIOLATION),
        ("api_key_read_requested", AGIcoreTradingV1OfflineSmokeDemoRisk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("env_var_read_requested", AGIcoreTradingV1OfflineSmokeDemoRisk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("network_requested", AGIcoreTradingV1OfflineSmokeDemoRisk.NETWORK_BOUNDARY_VIOLATION),
        ("http_requested", AGIcoreTradingV1OfflineSmokeDemoRisk.NETWORK_BOUNDARY_VIOLATION),
        ("websocket_requested", AGIcoreTradingV1OfflineSmokeDemoRisk.NETWORK_BOUNDARY_VIOLATION),
        ("socket_requested", AGIcoreTradingV1OfflineSmokeDemoRisk.NETWORK_BOUNDARY_VIOLATION),
        ("external_api_requested", AGIcoreTradingV1OfflineSmokeDemoRisk.NETWORK_BOUNDARY_VIOLATION),
        ("order_execution_requested", AGIcoreTradingV1OfflineSmokeDemoRisk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ("account_access_requested", AGIcoreTradingV1OfflineSmokeDemoRisk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ("position_mutation_requested", AGIcoreTradingV1OfflineSmokeDemoRisk.POSITION_MUTATION_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations_are_blocked(field, risk):
    data = _input(**{field: True})
    result = run_agicore_trading_v1_offline_smoke_demo(data)

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineSmokeDemoDecision.REQUIRE_SMOKE_DEMO_BOUNDARY_FIXES
    assert assert_agicore_trading_v1_offline_smoke_demo_boundaries(data) is False


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


def test_no_file_data_network_order_account_or_position_side_effects_are_reported():
    result = run_agicore_trading_v1_offline_smoke_demo(_input())

    assert result.file_read is False
    assert result.file_written is False
    assert result.data_accessed is False
    assert result.real_order_submitted is False
    assert result.real_account_accessed is False
    assert result.position_mutated is False
