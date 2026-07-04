from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agicore.trading.agicore_trading_v1_candidate import evaluate_agicore_trading_v1_candidate
from agicore.trading.agicore_trading_v1_candidate_models import AGIcoreTradingV1CandidateInput
from agicore.trading.agicore_trading_v1_candidate_review import (
    assert_agicore_trading_v1_candidate_review_offline_boundaries,
    compute_agicore_trading_v1_candidate_review_metrics,
    compute_agicore_trading_v1_candidate_review_score,
    detect_agicore_trading_v1_candidate_review_risks,
    generate_agicore_trading_v1_candidate_review_recommendations,
    render_agicore_trading_v1_candidate_review_json_report,
    render_agicore_trading_v1_candidate_review_markdown_report,
    review_agicore_trading_v1_candidate,
    review_v1_candidate_capability_coverage,
    review_v1_candidate_csv_replay_capability,
    review_v1_candidate_journal_capability,
    review_v1_candidate_known_limitations,
    review_v1_candidate_no_live_trading_claim,
    review_v1_candidate_no_profitability_claim,
    review_v1_candidate_offline_report_capability,
    review_v1_candidate_product_readiness,
    review_v1_candidate_risk_guard_capability,
    review_v1_candidate_safety_boundaries,
    review_v1_candidate_simulated_broker_capability,
    review_v1_candidate_smoke_replay,
    review_v1_candidate_strategy_replay_capability,
    review_v1_candidate_synthetic_market_capability,
    validate_agicore_trading_v1_candidate_review_input,
)
from agicore.trading.agicore_trading_v1_candidate_review_models import (
    AGIcoreTradingV1CandidateReviewDecision,
    AGIcoreTradingV1CandidateReviewInput,
    AGIcoreTradingV1CandidateReviewRecommendation,
    AGIcoreTradingV1CandidateReviewRisk,
    AGIcoreTradingV1CandidateReviewState,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/agicore_trading_v1_candidate_review.py"


def _input(**overrides):
    payload = {
        "candidate_input": AGIcoreTradingV1CandidateInput(candidate_id="review-candidate-001", version="v1-offline"),
    }
    payload.update(overrides)
    return AGIcoreTradingV1CandidateReviewInput(**payload)


def test_nominal_v1_candidate_review():
    result = review_agicore_trading_v1_candidate(_input())

    assert result.decision is AGIcoreTradingV1CandidateReviewDecision.APPROVE_AGICORE_TRADING_V1_CANDIDATE_REVIEW
    assert result.state is AGIcoreTradingV1CandidateReviewState.READY_FOR_AGICORE_TRADING_V1_OFFLINE_RELEASE_DECISION
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.metrics.expected_capability_count == 7
    assert result.metrics.reviewed_capability_count == 7
    assert result.metrics.failed_capability_count == 0
    assert result.smoke_replay_review.passed is True
    assert result.safety_boundary_review.passed is True
    assert result.product_readiness_review.passed is True
    assert all(limitation.documented for limitation in result.known_limitations)
    assert result.report.markdown
    assert result.report.json


def test_input_missing():
    result = review_agicore_trading_v1_candidate(None)

    assert validate_agicore_trading_v1_candidate_review_input(None) is False
    assert AGIcoreTradingV1CandidateReviewRisk.AGICORE_TRADING_V1_CANDIDATE_NOT_APPROVED in result.risks
    assert result.decision is AGIcoreTradingV1CandidateReviewDecision.REQUIRE_AGICORE_TRADING_V1_CANDIDATE_FIXES
    assert result.state is AGIcoreTradingV1CandidateReviewState.AGICORE_TRADING_V1_CANDIDATE_REVIEW_INPUT_INVALID


def test_candidate_non_approved():
    candidate = evaluate_agicore_trading_v1_candidate(
        AGIcoreTradingV1CandidateInput(force_smoke_replay_failed=True)
    )
    result = review_agicore_trading_v1_candidate(_input(candidate_result=candidate, candidate_input=None))

    assert AGIcoreTradingV1CandidateReviewRisk.AGICORE_TRADING_V1_CANDIDATE_NOT_APPROVED in result.risks
    assert result.decision is AGIcoreTradingV1CandidateReviewDecision.REQUIRE_AGICORE_TRADING_V1_CANDIDATE_FIXES


def test_candidate_non_approved_forced():
    result = review_agicore_trading_v1_candidate(_input(force_candidate_not_approved=True))

    assert AGIcoreTradingV1CandidateReviewRisk.AGICORE_TRADING_V1_CANDIDATE_NOT_APPROVED in result.risks
    assert result.decision is AGIcoreTradingV1CandidateReviewDecision.REQUIRE_AGICORE_TRADING_V1_CANDIDATE_FIXES


def test_capability_coverage_incomplete():
    result = review_agicore_trading_v1_candidate(_input(force_capability_coverage_incomplete=True))

    assert AGIcoreTradingV1CandidateReviewRisk.V1_CAPABILITY_COVERAGE_INCOMPLETE in result.risks
    assert result.decision is AGIcoreTradingV1CandidateReviewDecision.REQUIRE_V1_CAPABILITY_COVERAGE_FIXES
    assert review_v1_candidate_capability_coverage(_input(force_capability_coverage_incomplete=True)).passed is False


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("force_csv_replay_review_failed", AGIcoreTradingV1CandidateReviewRisk.CSV_REPLAY_CAPABILITY_REVIEW_FAILED),
        ("force_synthetic_market_review_failed", AGIcoreTradingV1CandidateReviewRisk.SYNTHETIC_MARKET_CAPABILITY_REVIEW_FAILED),
        ("force_strategy_replay_review_failed", AGIcoreTradingV1CandidateReviewRisk.STRATEGY_REPLAY_CAPABILITY_REVIEW_FAILED),
        ("force_simulated_broker_review_failed", AGIcoreTradingV1CandidateReviewRisk.SIMULATED_BROKER_CAPABILITY_REVIEW_FAILED),
        ("force_risk_guard_review_failed", AGIcoreTradingV1CandidateReviewRisk.RISK_GUARD_CAPABILITY_REVIEW_FAILED),
        ("force_journal_review_failed", AGIcoreTradingV1CandidateReviewRisk.JOURNAL_CAPABILITY_REVIEW_FAILED),
        ("force_offline_report_review_failed", AGIcoreTradingV1CandidateReviewRisk.OFFLINE_REPORT_CAPABILITY_REVIEW_FAILED),
    ),
)
def test_capability_review_failed(field, risk):
    result = review_agicore_trading_v1_candidate(_input(**{field: True}))

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1CandidateReviewDecision.REQUIRE_V1_CAPABILITY_COVERAGE_FIXES
    assert result.metrics.failed_capability_count == 1


def test_direct_capability_review_functions():
    data = _input()
    candidate = evaluate_agicore_trading_v1_candidate(data.candidate_input)

    reviews = (
        review_v1_candidate_csv_replay_capability(data, candidate),
        review_v1_candidate_synthetic_market_capability(data, candidate),
        review_v1_candidate_strategy_replay_capability(data, candidate),
        review_v1_candidate_simulated_broker_capability(data, candidate),
        review_v1_candidate_risk_guard_capability(data, candidate),
        review_v1_candidate_journal_capability(data, candidate),
        review_v1_candidate_offline_report_capability(data, candidate),
    )

    assert all(review.passed for review in reviews)
    assert {review.capability for review in reviews} == {
        "CSV_REPLAY_INPUT",
        "SYNTHETIC_MARKET_SCENARIO",
        "STRATEGY_REPLAY_ENGINE",
        "SIMULATED_BROKER_STUB",
        "RISK_GUARD_ENFORCEMENT",
        "JOURNAL_WRITER",
        "OFFLINE_REPORT_MARKDOWN_JSON",
    }


def test_smoke_replay_failed():
    result = review_agicore_trading_v1_candidate(_input(force_smoke_replay_failed=True))

    assert AGIcoreTradingV1CandidateReviewRisk.V1_SMOKE_REPLAY_REVIEW_FAILED in result.risks
    assert result.decision is AGIcoreTradingV1CandidateReviewDecision.REQUIRE_V1_SMOKE_REPLAY_FIXES
    assert review_v1_candidate_smoke_replay(_input(force_smoke_replay_failed=True)).passed is False


def test_product_readiness_incomplete():
    result = review_agicore_trading_v1_candidate(_input(force_product_readiness_incomplete=True))

    assert AGIcoreTradingV1CandidateReviewRisk.V1_PRODUCT_READINESS_INCOMPLETE in result.risks
    assert result.decision is AGIcoreTradingV1CandidateReviewDecision.REQUIRE_V1_PRODUCT_READINESS_FIXES
    assert review_v1_candidate_product_readiness(_input(force_product_readiness_incomplete=True)).passed is False


def test_limitations_not_documented():
    result = review_agicore_trading_v1_candidate(_input(force_limitations_not_documented=True))

    assert AGIcoreTradingV1CandidateReviewRisk.V1_LIMITATIONS_NOT_DOCUMENTED in result.risks
    assert result.decision is AGIcoreTradingV1CandidateReviewDecision.REQUIRE_V1_LIMITATION_DOCUMENTATION_FIXES
    assert not all(limitation.documented for limitation in review_v1_candidate_known_limitations(_input(force_limitations_not_documented=True)))


def test_live_trading_readiness_overclaim():
    result = review_agicore_trading_v1_candidate(_input(force_live_trading_readiness_overclaim=True))

    assert AGIcoreTradingV1CandidateReviewRisk.LIVE_TRADING_READINESS_OVERCLAIM in result.risks
    assert result.decision is AGIcoreTradingV1CandidateReviewDecision.REQUIRE_V1_PRODUCT_READINESS_FIXES
    assert review_v1_candidate_no_live_trading_claim(_input(force_live_trading_readiness_overclaim=True)).passed is False


def test_profitability_proof_missing():
    result = review_agicore_trading_v1_candidate(_input(force_profitability_claim=True))

    assert AGIcoreTradingV1CandidateReviewRisk.PROFITABILITY_PROOF_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1CandidateReviewDecision.REQUIRE_V1_PRODUCT_READINESS_FIXES
    assert review_v1_candidate_no_profitability_claim(_input(force_profitability_claim=True)).passed is False


def test_markdown_report():
    result = review_agicore_trading_v1_candidate(_input())
    markdown = render_agicore_trading_v1_candidate_review_markdown_report(result)

    assert "# AGIcore Trading v1 Candidate Review" in markdown
    assert "offline sandbox candidate only" in markdown
    assert "live_trading_ready: false" in markdown
    assert "profitability_proven: false" in markdown
    assert "CSV_REPLAY_INPUT" in markdown


def test_json_report():
    result = review_agicore_trading_v1_candidate(_input())
    payload = json.loads(render_agicore_trading_v1_candidate_review_json_report(result))

    assert payload["schema"] == "agicore_trading_v1_candidate_review"
    assert payload["decision"] == "APPROVE_AGICORE_TRADING_V1_CANDIDATE_REVIEW"
    assert payload["live_trading_ready"] is False
    assert payload["profitability_proven"] is False
    assert payload["metrics"]["reviewed_capability_count"] == 7


def test_metrics_risks_score_and_recommendations_directly():
    result = review_agicore_trading_v1_candidate(_input())
    risks = detect_agicore_trading_v1_candidate_review_risks(
        _input(),
        result.candidate_result,
        result.capability_reviews,
        result.smoke_replay_review,
        result.safety_boundary_review,
        result.product_readiness_review,
        result.known_limitations,
        result.findings,
    )
    metrics = compute_agicore_trading_v1_candidate_review_metrics(
        result.capability_reviews,
        result.smoke_replay_review,
        result.safety_boundary_review,
        result.known_limitations,
        result.findings,
        result.decision.value,
    )
    score = compute_agicore_trading_v1_candidate_review_score(
        _input(),
        result.candidate_result,
        result.capability_reviews,
        result.smoke_replay_review,
        result.safety_boundary_review,
        result.product_readiness_review,
        result.known_limitations,
        risks,
    )
    recommendations = generate_agicore_trading_v1_candidate_review_recommendations(risks)

    assert risks == ()
    assert metrics.reviewed_capability_count == 7
    assert score.overall_score == 100
    assert recommendations == (AGIcoreTradingV1CandidateReviewRecommendation.PROCEED_TO_OFFLINE_RELEASE_DECISION,)


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("file_read_requested", AGIcoreTradingV1CandidateReviewRisk.FILE_READ_BOUNDARY_VIOLATION),
        ("file_write_requested", AGIcoreTradingV1CandidateReviewRisk.FILE_WRITE_BOUNDARY_VIOLATION),
        ("real_data_access_requested", AGIcoreTradingV1CandidateReviewRisk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_access_requested", AGIcoreTradingV1CandidateReviewRisk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("broker_connection_requested", AGIcoreTradingV1CandidateReviewRisk.REAL_BROKER_BOUNDARY_VIOLATION),
        ("secret_read_requested", AGIcoreTradingV1CandidateReviewRisk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("network_requested", AGIcoreTradingV1CandidateReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("http_requested", AGIcoreTradingV1CandidateReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("websocket_requested", AGIcoreTradingV1CandidateReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("socket_requested", AGIcoreTradingV1CandidateReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("external_api_requested", AGIcoreTradingV1CandidateReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("order_execution_requested", AGIcoreTradingV1CandidateReviewRisk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ("account_access_requested", AGIcoreTradingV1CandidateReviewRisk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ("position_mutation_requested", AGIcoreTradingV1CandidateReviewRisk.POSITION_MUTATION_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations_are_blocked(field, risk):
    data = _input(**{field: True})
    result = review_agicore_trading_v1_candidate(data)

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1CandidateReviewDecision.REQUIRE_V1_SAFETY_BOUNDARY_FIXES
    assert assert_agicore_trading_v1_candidate_review_offline_boundaries(data) is False
    assert review_v1_candidate_safety_boundaries(data).passed is False


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
    result = review_agicore_trading_v1_candidate(_input())

    assert result.file_read is False
    assert result.file_written is False
    assert result.data_accessed is False
    assert result.real_order_submitted is False
    assert result.real_account_accessed is False
    assert result.position_mutated is False
    assert result.safety_boundary_review.real_order_submitted is False
    assert result.safety_boundary_review.real_account_accessed is False
    assert result.safety_boundary_review.position_mutated is False
