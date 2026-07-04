from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agicore.trading.agicore_trading_v1_candidate import (
    assert_agicore_trading_v1_candidate_offline_boundaries,
    build_agicore_trading_v1_candidate_context,
    compute_agicore_trading_v1_candidate_metrics,
    compute_agicore_trading_v1_candidate_score,
    detect_agicore_trading_v1_candidate_risks,
    evaluate_agicore_trading_v1_candidate,
    generate_agicore_trading_v1_candidate_recommendations,
    render_agicore_trading_v1_candidate_json_report,
    render_agicore_trading_v1_candidate_markdown_report,
    run_agicore_trading_v1_candidate_smoke_replay,
    validate_agicore_trading_v1_candidate_input,
    validate_v1_candidate_csv_replay_capability,
    validate_v1_candidate_journal_capability,
    validate_v1_candidate_offline_report_capability,
    validate_v1_candidate_risk_guard_capability,
    validate_v1_candidate_simulated_broker_capability,
    validate_v1_candidate_strategy_replay_capability,
    validate_v1_candidate_synthetic_market_capability,
)
from agicore.trading.agicore_trading_v1_candidate_models import (
    AGIcoreTradingV1CandidateDecision,
    AGIcoreTradingV1CandidateInput,
    AGIcoreTradingV1CandidateRecommendation,
    AGIcoreTradingV1CandidateRisk,
    AGIcoreTradingV1CandidateState,
    AGIcoreTradingV1CapabilityName,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/agicore_trading_v1_candidate.py"


def _input(**overrides):
    payload = {
        "candidate_id": "candidate-001",
        "version": "v1-offline",
    }
    payload.update(overrides)
    return AGIcoreTradingV1CandidateInput(**payload)


def test_nominal_v1_candidate():
    result = evaluate_agicore_trading_v1_candidate(_input())

    assert result.decision is AGIcoreTradingV1CandidateDecision.APPROVE_AGICORE_TRADING_V1_CANDIDATE
    assert result.state is AGIcoreTradingV1CandidateState.READY_FOR_AGICORE_TRADING_V1_CANDIDATE_REVIEW
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.metrics.expected_capability_count == 7
    assert result.metrics.validated_capability_count == 7
    assert result.metrics.failed_capability_count == 0
    assert result.smoke_replay.passed is True
    assert result.report.markdown
    assert result.report.json


def test_input_missing():
    result = evaluate_agicore_trading_v1_candidate(None)

    assert validate_agicore_trading_v1_candidate_input(None) is False
    assert AGIcoreTradingV1CandidateRisk.AGICORE_TRADING_V1_INPUT_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1CandidateDecision.REQUIRE_AGICORE_TRADING_V1_INPUT_FIXES
    assert result.state is AGIcoreTradingV1CandidateState.AGICORE_TRADING_V1_CANDIDATE_INPUT_INVALID


@pytest.mark.parametrize(
    ("field", "risk", "decision"),
    (
        (
            "force_csv_replay_capability_missing",
            AGIcoreTradingV1CandidateRisk.CSV_REPLAY_CAPABILITY_MISSING,
            AGIcoreTradingV1CandidateDecision.REQUIRE_CSV_REPLAY_CAPABILITY_FIXES,
        ),
        (
            "force_synthetic_market_capability_missing",
            AGIcoreTradingV1CandidateRisk.SYNTHETIC_MARKET_CAPABILITY_MISSING,
            AGIcoreTradingV1CandidateDecision.REQUIRE_SYNTHETIC_MARKET_CAPABILITY_FIXES,
        ),
        (
            "force_strategy_replay_capability_missing",
            AGIcoreTradingV1CandidateRisk.STRATEGY_REPLAY_CAPABILITY_MISSING,
            AGIcoreTradingV1CandidateDecision.REQUIRE_STRATEGY_REPLAY_CAPABILITY_FIXES,
        ),
        (
            "force_simulated_broker_capability_missing",
            AGIcoreTradingV1CandidateRisk.SIMULATED_BROKER_CAPABILITY_MISSING,
            AGIcoreTradingV1CandidateDecision.REQUIRE_SIMULATED_BROKER_CAPABILITY_FIXES,
        ),
        (
            "force_risk_guard_capability_missing",
            AGIcoreTradingV1CandidateRisk.RISK_GUARD_CAPABILITY_MISSING,
            AGIcoreTradingV1CandidateDecision.REQUIRE_RISK_GUARD_CAPABILITY_FIXES,
        ),
        (
            "force_journal_capability_missing",
            AGIcoreTradingV1CandidateRisk.JOURNAL_CAPABILITY_MISSING,
            AGIcoreTradingV1CandidateDecision.REQUIRE_JOURNAL_CAPABILITY_FIXES,
        ),
        (
            "force_offline_report_capability_missing",
            AGIcoreTradingV1CandidateRisk.OFFLINE_REPORT_CAPABILITY_MISSING,
            AGIcoreTradingV1CandidateDecision.REQUIRE_OFFLINE_REPORT_CAPABILITY_FIXES,
        ),
    ),
)
def test_capability_missing(field, risk, decision):
    result = evaluate_agicore_trading_v1_candidate(_input(**{field: True}))

    assert risk in result.risks
    assert result.decision is decision
    assert result.metrics.failed_capability_count == 1


def test_smoke_replay_failed():
    result = evaluate_agicore_trading_v1_candidate(_input(force_smoke_replay_failed=True))

    assert AGIcoreTradingV1CandidateRisk.V1_SMOKE_REPLAY_FAILED in result.risks
    assert result.decision is AGIcoreTradingV1CandidateDecision.REQUIRE_V1_SMOKE_REPLAY_FIXES


def test_metrics_missing():
    result = evaluate_agicore_trading_v1_candidate(_input(force_metrics_missing=True))

    assert AGIcoreTradingV1CandidateRisk.V1_CANDIDATE_METRICS_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1CandidateDecision.BLOCK_AGICORE_TRADING_V1_CANDIDATE


def test_report_missing():
    result = evaluate_agicore_trading_v1_candidate(_input(force_report_missing=True))

    assert AGIcoreTradingV1CandidateRisk.V1_CANDIDATE_REPORT_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1CandidateDecision.BLOCK_AGICORE_TRADING_V1_CANDIDATE


def test_markdown_report():
    result = evaluate_agicore_trading_v1_candidate(_input())
    markdown = render_agicore_trading_v1_candidate_markdown_report(result)

    assert "# AGIcore Trading v1 Candidate" in markdown
    assert "CSV_REPLAY_INPUT" in markdown
    assert "file_read: false" in markdown


def test_json_report():
    result = evaluate_agicore_trading_v1_candidate(_input())
    payload = json.loads(render_agicore_trading_v1_candidate_json_report(result))

    assert payload["schema"] == "agicore_trading_v1_candidate"
    assert payload["decision"] == "APPROVE_AGICORE_TRADING_V1_CANDIDATE"
    assert payload["metrics"]["validated_capability_count"] == 7


def test_direct_capability_checks_and_metrics():
    data = _input()
    context = build_agicore_trading_v1_candidate_context(data)
    checks = (
        validate_v1_candidate_csv_replay_capability(data),
        validate_v1_candidate_synthetic_market_capability(data),
        validate_v1_candidate_strategy_replay_capability(data),
        validate_v1_candidate_simulated_broker_capability(data),
        validate_v1_candidate_risk_guard_capability(data),
        validate_v1_candidate_journal_capability(data),
        validate_v1_candidate_offline_report_capability(data),
    )
    smoke = run_agicore_trading_v1_candidate_smoke_replay(data)
    metrics = compute_agicore_trading_v1_candidate_metrics(checks, smoke, data=data)

    assert context.capability_count == 7
    assert {check.capability for check in checks} == set(AGIcoreTradingV1CapabilityName)
    assert all(check.passed for check in checks)
    assert smoke.passed is True
    assert smoke.real_order_submitted is False
    assert metrics.validated_capability_count == 7


def test_score_and_risks_can_be_computed_directly():
    result = evaluate_agicore_trading_v1_candidate(_input())
    risks = detect_agicore_trading_v1_candidate_risks(
        _input(),
        result.capability_checks,
        result.smoke_replay,
        result.metrics,
        result.report,
    )
    score = compute_agicore_trading_v1_candidate_score(
        _input(),
        result.capability_checks,
        result.smoke_replay,
        result.metrics,
        result.report,
        risks,
    )

    assert risks == ()
    assert score.overall_score == 100


def test_recommendations_generated():
    recommendations = generate_agicore_trading_v1_candidate_recommendations(
        (AGIcoreTradingV1CandidateRisk.CSV_REPLAY_CAPABILITY_MISSING,)
    )

    assert AGIcoreTradingV1CandidateRecommendation.FIX_CSV_REPLAY_CAPABILITY in recommendations
    assert AGIcoreTradingV1CandidateRecommendation.RUN_AGICORE_TRADING_V1_CANDIDATE_TEST_SUITE in recommendations


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("file_read_requested", AGIcoreTradingV1CandidateRisk.FILE_READ_BOUNDARY_VIOLATION),
        ("file_write_requested", AGIcoreTradingV1CandidateRisk.FILE_WRITE_BOUNDARY_VIOLATION),
        ("real_data_access_requested", AGIcoreTradingV1CandidateRisk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_read_requested", AGIcoreTradingV1CandidateRisk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_write_requested", AGIcoreTradingV1CandidateRisk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("broker_connection_requested", AGIcoreTradingV1CandidateRisk.REAL_BROKER_BOUNDARY_VIOLATION),
        ("api_key_read_requested", AGIcoreTradingV1CandidateRisk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("env_var_read_requested", AGIcoreTradingV1CandidateRisk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("network_requested", AGIcoreTradingV1CandidateRisk.NETWORK_BOUNDARY_VIOLATION),
        ("http_requested", AGIcoreTradingV1CandidateRisk.NETWORK_BOUNDARY_VIOLATION),
        ("websocket_requested", AGIcoreTradingV1CandidateRisk.NETWORK_BOUNDARY_VIOLATION),
        ("socket_requested", AGIcoreTradingV1CandidateRisk.NETWORK_BOUNDARY_VIOLATION),
        ("order_execution_requested", AGIcoreTradingV1CandidateRisk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ("account_access_requested", AGIcoreTradingV1CandidateRisk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ("position_mutation_requested", AGIcoreTradingV1CandidateRisk.POSITION_MUTATION_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations_are_blocked(field, risk):
    data = _input(**{field: True})
    result = evaluate_agicore_trading_v1_candidate(data)

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1CandidateDecision.BLOCK_AGICORE_TRADING_V1_CANDIDATE
    assert assert_agicore_trading_v1_candidate_offline_boundaries(data) is False


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
    result = evaluate_agicore_trading_v1_candidate(_input())

    assert result.file_read is False
    assert result.file_written is False
    assert result.data_accessed is False
    assert result.real_order_submitted is False
    assert result.real_account_accessed is False
    assert result.position_mutated is False
    assert result.smoke_replay.real_order_submitted is False
    assert result.smoke_replay.real_account_accessed is False
    assert result.smoke_replay.position_mutated is False
