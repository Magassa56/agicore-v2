from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agicore.trading.agicore_trading_v1_offline_smoke_demo import run_agicore_trading_v1_offline_smoke_demo
from agicore.trading.agicore_trading_v1_offline_smoke_demo_models import AGIcoreTradingV1OfflineSmokeDemoInput
from agicore.trading.agicore_trading_v1_offline_smoke_demo_review import (
    assert_agicore_trading_v1_offline_smoke_demo_review_boundaries,
    compute_agicore_trading_v1_offline_smoke_demo_review_metrics,
    compute_agicore_trading_v1_offline_smoke_demo_review_score,
    detect_agicore_trading_v1_offline_smoke_demo_review_risks,
    generate_agicore_trading_v1_offline_smoke_demo_review_recommendations,
    render_agicore_trading_v1_offline_smoke_demo_review_json_report,
    render_agicore_trading_v1_offline_smoke_demo_review_markdown_report,
    review_agicore_trading_v1_offline_smoke_demo,
    review_smoke_demo_approval,
    review_smoke_demo_boundaries,
    review_smoke_demo_broker_preview_step,
    review_smoke_demo_csv_replay_step,
    review_smoke_demo_end_to_end_flow,
    review_smoke_demo_journal_step,
    review_smoke_demo_no_live_trading_claim,
    review_smoke_demo_no_profitability_claim,
    review_smoke_demo_offline_report_step,
    review_smoke_demo_read_only_decision,
    review_smoke_demo_risk_guard_step,
    review_smoke_demo_sandbox_usability,
    review_smoke_demo_strategy_replay_step,
    validate_agicore_trading_v1_offline_smoke_demo_review_input,
)
from agicore.trading.agicore_trading_v1_offline_smoke_demo_review_models import (
    AGIcoreTradingV1OfflineSmokeDemoReviewDecision,
    AGIcoreTradingV1OfflineSmokeDemoReviewInput,
    AGIcoreTradingV1OfflineSmokeDemoReviewRecommendation,
    AGIcoreTradingV1OfflineSmokeDemoReviewRisk,
    AGIcoreTradingV1OfflineSmokeDemoReviewState,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/agicore_trading_v1_offline_smoke_demo_review.py"


def _input(**overrides):
    payload = {"smoke_demo_input": AGIcoreTradingV1OfflineSmokeDemoInput(run_id="smoke-demo-review-001")}
    payload.update(overrides)
    return AGIcoreTradingV1OfflineSmokeDemoReviewInput(**payload)


def test_nominal_smoke_demo_review():
    result = review_agicore_trading_v1_offline_smoke_demo(_input())

    assert result.decision is AGIcoreTradingV1OfflineSmokeDemoReviewDecision.APPROVE_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_REVIEW
    assert result.state is AGIcoreTradingV1OfflineSmokeDemoReviewState.READY_FOR_AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.metrics.expected_step_count == 7
    assert result.metrics.reviewed_step_count == 7
    assert result.metrics.failed_step_count == 0
    assert result.metrics.end_to_end_passed is True
    assert result.metrics.read_only_decision_passed is True
    assert result.sandbox_usability_review.passed is True
    assert result.boundary_review.passed is True
    assert result.report.markdown
    assert result.report.json


def test_input_manquant():
    result = review_agicore_trading_v1_offline_smoke_demo(None)

    assert validate_agicore_trading_v1_offline_smoke_demo_review_input(None) is False
    assert AGIcoreTradingV1OfflineSmokeDemoReviewRisk.SMOKE_DEMO_NOT_APPROVED in result.risks
    assert result.decision is AGIcoreTradingV1OfflineSmokeDemoReviewDecision.REQUIRE_SMOKE_DEMO_FIXES
    assert result.state is AGIcoreTradingV1OfflineSmokeDemoReviewState.AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_REVIEW_INPUT_INVALID


def test_smoke_demo_non_approuvee():
    smoke_demo = run_agicore_trading_v1_offline_smoke_demo(
        AGIcoreTradingV1OfflineSmokeDemoInput(force_csv_replay_failed=True)
    )
    result = review_agicore_trading_v1_offline_smoke_demo(
        _input(smoke_demo_result=smoke_demo, smoke_demo_input=None)
    )

    assert AGIcoreTradingV1OfflineSmokeDemoReviewRisk.SMOKE_DEMO_NOT_APPROVED in result.risks
    assert result.decision is AGIcoreTradingV1OfflineSmokeDemoReviewDecision.REQUIRE_SMOKE_DEMO_FIXES
    assert review_smoke_demo_approval(_input(smoke_demo_result=smoke_demo, smoke_demo_input=None)).passed is False


def test_smoke_demo_non_approuvee_forcee():
    result = review_agicore_trading_v1_offline_smoke_demo(_input(force_smoke_demo_not_approved=True))

    assert AGIcoreTradingV1OfflineSmokeDemoReviewRisk.SMOKE_DEMO_NOT_APPROVED in result.risks
    assert result.decision is AGIcoreTradingV1OfflineSmokeDemoReviewDecision.REQUIRE_SMOKE_DEMO_FIXES


def test_end_to_end_review_failed():
    result = review_agicore_trading_v1_offline_smoke_demo(_input(force_end_to_end_review_failed=True))

    assert AGIcoreTradingV1OfflineSmokeDemoReviewRisk.SMOKE_DEMO_END_TO_END_REVIEW_FAILED in result.risks
    assert result.decision is AGIcoreTradingV1OfflineSmokeDemoReviewDecision.REQUIRE_SMOKE_DEMO_END_TO_END_FIXES
    assert review_smoke_demo_end_to_end_flow(_input(force_end_to_end_review_failed=True)).passed is False


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("force_csv_replay_step_failed", AGIcoreTradingV1OfflineSmokeDemoReviewRisk.SMOKE_DEMO_CSV_REPLAY_STEP_FAILED),
        ("force_strategy_replay_step_failed", AGIcoreTradingV1OfflineSmokeDemoReviewRisk.SMOKE_DEMO_STRATEGY_REPLAY_STEP_FAILED),
        ("force_risk_guard_step_failed", AGIcoreTradingV1OfflineSmokeDemoReviewRisk.SMOKE_DEMO_RISK_GUARD_STEP_FAILED),
        ("force_broker_preview_step_failed", AGIcoreTradingV1OfflineSmokeDemoReviewRisk.SMOKE_DEMO_BROKER_PREVIEW_STEP_FAILED),
        ("force_journal_step_failed", AGIcoreTradingV1OfflineSmokeDemoReviewRisk.SMOKE_DEMO_JOURNAL_STEP_FAILED),
        ("force_offline_report_step_failed", AGIcoreTradingV1OfflineSmokeDemoReviewRisk.SMOKE_DEMO_OFFLINE_REPORT_STEP_FAILED),
    ),
)
def test_step_review_failed(field, risk):
    result = review_agicore_trading_v1_offline_smoke_demo(_input(**{field: True}))

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineSmokeDemoReviewDecision.REQUIRE_SMOKE_DEMO_STEP_REVIEW_FIXES
    assert result.metrics.failed_step_count == 1


def test_direct_step_review_functions():
    data = _input()
    smoke_demo = run_agicore_trading_v1_offline_smoke_demo(data.smoke_demo_input)

    reviews = (
        review_smoke_demo_csv_replay_step(data, smoke_demo),
        review_smoke_demo_strategy_replay_step(data, smoke_demo),
        review_smoke_demo_risk_guard_step(data, smoke_demo),
        review_smoke_demo_broker_preview_step(data, smoke_demo),
        review_smoke_demo_journal_step(data, smoke_demo),
        review_smoke_demo_offline_report_step(data, smoke_demo),
    )

    assert all(review.passed for review in reviews)
    assert {review.step_name for review in reviews} == {
        "CSV_REPLAY_INPUT_STEP",
        "STRATEGY_REPLAY_ENGINE_STEP",
        "RISK_GUARD_STEP",
        "SIMULATED_BROKER_PREVIEW_STEP",
        "JOURNAL_WRITER_STEP",
        "OFFLINE_REPORT_STEP",
    }


def test_read_only_decision_invalid():
    result = review_agicore_trading_v1_offline_smoke_demo(_input(force_read_only_decision_invalid=True))

    assert AGIcoreTradingV1OfflineSmokeDemoReviewRisk.SMOKE_DEMO_READ_ONLY_DECISION_INVALID in result.risks
    assert result.decision is AGIcoreTradingV1OfflineSmokeDemoReviewDecision.REQUIRE_SMOKE_DEMO_READ_ONLY_DECISION_FIXES
    assert review_smoke_demo_read_only_decision(_input(force_read_only_decision_invalid=True)).passed is False


def test_sandbox_usability_incomplete():
    result = review_agicore_trading_v1_offline_smoke_demo(_input(force_sandbox_usability_incomplete=True))

    assert AGIcoreTradingV1OfflineSmokeDemoReviewRisk.SMOKE_DEMO_SANDBOX_USABILITY_INCOMPLETE in result.risks
    assert result.decision is AGIcoreTradingV1OfflineSmokeDemoReviewDecision.REQUIRE_SMOKE_DEMO_SANDBOX_USABILITY_FIXES
    assert review_smoke_demo_sandbox_usability(_input(force_sandbox_usability_incomplete=True)).passed is False


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("force_live_trading_overclaim", AGIcoreTradingV1OfflineSmokeDemoReviewRisk.LIVE_TRADING_READINESS_OVERCLAIM),
        ("force_real_broker_overclaim", AGIcoreTradingV1OfflineSmokeDemoReviewRisk.REAL_BROKER_READINESS_OVERCLAIM),
        ("force_real_order_overclaim", AGIcoreTradingV1OfflineSmokeDemoReviewRisk.REAL_ORDER_EXECUTION_OVERCLAIM),
        ("force_profitability_overclaim", AGIcoreTradingV1OfflineSmokeDemoReviewRisk.PROFITABILITY_PROOF_OVERCLAIM),
        ("force_financial_advice_overclaim", AGIcoreTradingV1OfflineSmokeDemoReviewRisk.FINANCIAL_ADVICE_OVERCLAIM),
    ),
)
def test_overclaims_are_rejected(field, risk):
    result = review_agicore_trading_v1_offline_smoke_demo(_input(**{field: True}))

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineSmokeDemoReviewDecision.REQUIRE_SMOKE_DEMO_NO_OVERCLAIM_FIXES


def test_no_live_trading_and_no_profitability_claim_helpers():
    assert review_smoke_demo_no_live_trading_claim(_input()).passed is True
    assert review_smoke_demo_no_profitability_claim(_input()).passed is True
    assert review_smoke_demo_no_live_trading_claim(_input(force_live_trading_overclaim=True)).passed is False
    assert review_smoke_demo_no_profitability_claim(_input(force_profitability_overclaim=True)).passed is False


def test_markdown_report():
    result = review_agicore_trading_v1_offline_smoke_demo(_input())
    markdown = render_agicore_trading_v1_offline_smoke_demo_review_markdown_report(result)

    assert "# AGIcore Trading v1 Offline Smoke Demo Review" in markdown
    assert "offline/sandbox review only" in markdown
    assert "CSV_REPLAY_INPUT_STEP" in markdown
    assert "live_trading_ready: false" in markdown
    assert "profitability_proven: false" in markdown


def test_json_report():
    result = review_agicore_trading_v1_offline_smoke_demo(_input())
    payload = json.loads(render_agicore_trading_v1_offline_smoke_demo_review_json_report(result))

    assert payload["schema"] == "agicore_trading_v1_offline_smoke_demo_review"
    assert payload["decision"] == "APPROVE_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_REVIEW"
    assert payload["local_sandbox_usable"] is True
    assert payload["live_trading_ready"] is False
    assert payload["real_broker_ready"] is False
    assert payload["real_order_execution"] is False
    assert payload["profitability_proven"] is False


def test_metrics_risks_score_and_recommendations_directly():
    result = review_agicore_trading_v1_offline_smoke_demo(_input())
    risks = detect_agicore_trading_v1_offline_smoke_demo_review_risks(
        _input(),
        result.smoke_demo_result,
        result.step_reviews,
        result.findings,
        result.sandbox_usability_review,
        result.boundary_review,
    )
    metrics = compute_agicore_trading_v1_offline_smoke_demo_review_metrics(
        result.step_reviews,
        result.findings,
        result.sandbox_usability_review,
        result.boundary_review,
        result.decision.value,
    )
    score = compute_agicore_trading_v1_offline_smoke_demo_review_score(
        _input(),
        result.findings[0],
        result.findings[1],
        result.step_reviews,
        result.findings[2],
        result.sandbox_usability_review,
        result.boundary_review,
        result.findings[3],
        result.findings[4],
        risks,
    )
    recommendations = generate_agicore_trading_v1_offline_smoke_demo_review_recommendations(risks)

    assert risks == ()
    assert metrics.reviewed_step_count == 7
    assert score.overall_score == 100
    assert recommendations == (
        AGIcoreTradingV1OfflineSmokeDemoReviewRecommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE,
    )


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("file_read_requested", AGIcoreTradingV1OfflineSmokeDemoReviewRisk.FILE_READ_BOUNDARY_VIOLATION),
        ("file_write_requested", AGIcoreTradingV1OfflineSmokeDemoReviewRisk.FILE_WRITE_BOUNDARY_VIOLATION),
        ("real_data_access_requested", AGIcoreTradingV1OfflineSmokeDemoReviewRisk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_access_requested", AGIcoreTradingV1OfflineSmokeDemoReviewRisk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("broker_connection_requested", AGIcoreTradingV1OfflineSmokeDemoReviewRisk.REAL_BROKER_BOUNDARY_VIOLATION),
        ("secret_read_requested", AGIcoreTradingV1OfflineSmokeDemoReviewRisk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("network_requested", AGIcoreTradingV1OfflineSmokeDemoReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("http_requested", AGIcoreTradingV1OfflineSmokeDemoReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("websocket_requested", AGIcoreTradingV1OfflineSmokeDemoReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("socket_requested", AGIcoreTradingV1OfflineSmokeDemoReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("external_api_requested", AGIcoreTradingV1OfflineSmokeDemoReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("order_execution_requested", AGIcoreTradingV1OfflineSmokeDemoReviewRisk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ("account_access_requested", AGIcoreTradingV1OfflineSmokeDemoReviewRisk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ("position_mutation_requested", AGIcoreTradingV1OfflineSmokeDemoReviewRisk.POSITION_MUTATION_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations_are_blocked(field, risk):
    data = _input(**{field: True})
    result = review_agicore_trading_v1_offline_smoke_demo(data)

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineSmokeDemoReviewDecision.REQUIRE_SMOKE_DEMO_BOUNDARY_FIXES
    assert assert_agicore_trading_v1_offline_smoke_demo_review_boundaries(data) is False
    assert review_smoke_demo_boundaries(data).passed is False


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
    result = review_agicore_trading_v1_offline_smoke_demo(_input())

    assert result.file_read is False
    assert result.file_written is False
    assert result.data_accessed is False
    assert result.real_order_submitted is False
    assert result.real_account_accessed is False
    assert result.position_mutated is False
    assert result.boundary_review.real_order_submitted is False
    assert result.boundary_review.real_account_accessed is False
    assert result.boundary_review.position_mutated is False
