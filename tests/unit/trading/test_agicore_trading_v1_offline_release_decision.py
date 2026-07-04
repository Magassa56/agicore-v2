from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agicore.trading.agicore_trading_v1_candidate_review import review_agicore_trading_v1_candidate
from agicore.trading.agicore_trading_v1_candidate_review_models import AGIcoreTradingV1CandidateReviewInput
from agicore.trading.agicore_trading_v1_offline_release_decision import (
    assert_agicore_trading_v1_offline_release_decision_boundaries,
    build_offline_release_decision_summary,
    compute_agicore_trading_v1_offline_release_decision_metrics,
    compute_agicore_trading_v1_offline_release_decision_score,
    detect_agicore_trading_v1_offline_release_decision_risks,
    evaluate_agicore_trading_v1_offline_release_decision,
    evaluate_offline_release_capability_readiness,
    evaluate_offline_release_known_limitations,
    evaluate_offline_release_no_live_trading_claim,
    evaluate_offline_release_no_profitability_claim,
    evaluate_offline_release_non_goals,
    evaluate_offline_release_product_readiness,
    evaluate_offline_release_safety_boundaries,
    evaluate_offline_release_scope,
    evaluate_offline_release_testing_evidence,
    generate_agicore_trading_v1_offline_release_decision_recommendations,
    render_agicore_trading_v1_offline_release_decision_json_report,
    render_agicore_trading_v1_offline_release_decision_markdown_report,
    validate_agicore_trading_v1_offline_release_decision_input,
    validate_v1_candidate_review_approval,
)
from agicore.trading.agicore_trading_v1_offline_release_decision_models import (
    AGIcoreTradingV1OfflineReleaseDecisionDecision,
    AGIcoreTradingV1OfflineReleaseDecisionInput,
    AGIcoreTradingV1OfflineReleaseDecisionRecommendation,
    AGIcoreTradingV1OfflineReleaseDecisionRisk,
    AGIcoreTradingV1OfflineReleaseDecisionState,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/agicore_trading_v1_offline_release_decision.py"


def _input(**overrides):
    payload = {
        "candidate_review_input": AGIcoreTradingV1CandidateReviewInput(),
    }
    payload.update(overrides)
    return AGIcoreTradingV1OfflineReleaseDecisionInput(**payload)


def test_nominal_offline_release_decision():
    result = evaluate_agicore_trading_v1_offline_release_decision(_input())

    assert result.decision is AGIcoreTradingV1OfflineReleaseDecisionDecision.APPROVE_AGICORE_TRADING_V1_OFFLINE_RELEASE_DECISION
    assert result.state is AGIcoreTradingV1OfflineReleaseDecisionState.READY_FOR_AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.capability_readiness.ready is True
    assert result.capability_readiness.confirmed_capabilities[-1] == "V1_CANDIDATE_REVIEW"
    assert result.safety_boundary.passed is True
    assert result.testing_evidence.complete is True
    assert len(result.non_goals) == 7
    assert result.product_readiness.live_trading_ready is False
    assert result.product_readiness.profitability_proven is False
    assert result.report.markdown
    assert result.report.json


def test_input_missing():
    result = evaluate_agicore_trading_v1_offline_release_decision(None)

    assert validate_agicore_trading_v1_offline_release_decision_input(None) is False
    assert AGIcoreTradingV1OfflineReleaseDecisionRisk.V1_CANDIDATE_REVIEW_NOT_APPROVED in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleaseDecisionDecision.REQUIRE_V1_CANDIDATE_REVIEW_FIXES
    assert result.state is AGIcoreTradingV1OfflineReleaseDecisionState.AGICORE_TRADING_V1_OFFLINE_RELEASE_DECISION_INPUT_INVALID


def test_candidate_review_non_approved():
    review = review_agicore_trading_v1_candidate(
        AGIcoreTradingV1CandidateReviewInput(force_smoke_replay_failed=True)
    )
    result = evaluate_agicore_trading_v1_offline_release_decision(
        _input(candidate_review_input=None, candidate_review_result=review)
    )

    assert validate_v1_candidate_review_approval(_input(candidate_review_result=review, candidate_review_input=None), review) is False
    assert AGIcoreTradingV1OfflineReleaseDecisionRisk.V1_CANDIDATE_REVIEW_NOT_APPROVED in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleaseDecisionDecision.REQUIRE_V1_CANDIDATE_REVIEW_FIXES


def test_candidate_review_forced_non_approved():
    result = evaluate_agicore_trading_v1_offline_release_decision(_input(force_candidate_review_not_approved=True))

    assert AGIcoreTradingV1OfflineReleaseDecisionRisk.V1_CANDIDATE_REVIEW_NOT_APPROVED in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleaseDecisionDecision.REQUIRE_V1_CANDIDATE_REVIEW_FIXES


def test_scope_invalid():
    result = evaluate_agicore_trading_v1_offline_release_decision(_input(force_scope_invalid=True))

    assert evaluate_offline_release_scope(_input(force_scope_invalid=True)).valid is False
    assert AGIcoreTradingV1OfflineReleaseDecisionRisk.OFFLINE_RELEASE_SCOPE_INVALID in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleaseDecisionDecision.REQUIRE_OFFLINE_RELEASE_SCOPE_FIXES


def test_capability_incomplete():
    result = evaluate_agicore_trading_v1_offline_release_decision(_input(force_capability_incomplete=True))

    assert evaluate_offline_release_capability_readiness(_input(force_capability_incomplete=True)).ready is False
    assert AGIcoreTradingV1OfflineReleaseDecisionRisk.OFFLINE_RELEASE_CAPABILITY_INCOMPLETE in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleaseDecisionDecision.REQUIRE_OFFLINE_RELEASE_CAPABILITY_FIXES


def test_safety_boundary_incomplete():
    result = evaluate_agicore_trading_v1_offline_release_decision(_input(force_safety_boundary_incomplete=True))

    assert evaluate_offline_release_safety_boundaries(_input(force_safety_boundary_incomplete=True)).passed is False
    assert AGIcoreTradingV1OfflineReleaseDecisionRisk.OFFLINE_RELEASE_SAFETY_BOUNDARY_INCOMPLETE in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleaseDecisionDecision.REQUIRE_OFFLINE_RELEASE_SAFETY_FIXES


def test_testing_evidence_missing():
    result = evaluate_agicore_trading_v1_offline_release_decision(_input(force_testing_evidence_missing=True))

    assert evaluate_offline_release_testing_evidence(_input(force_testing_evidence_missing=True)).complete is False
    assert AGIcoreTradingV1OfflineReleaseDecisionRisk.OFFLINE_RELEASE_TESTING_EVIDENCE_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleaseDecisionDecision.REQUIRE_OFFLINE_RELEASE_TESTING_EVIDENCE_FIXES


def test_limitations_missing():
    result = evaluate_agicore_trading_v1_offline_release_decision(_input(force_limitations_missing=True))

    assert evaluate_offline_release_known_limitations(_input(force_limitations_missing=True)) == ()
    assert AGIcoreTradingV1OfflineReleaseDecisionRisk.OFFLINE_RELEASE_LIMITATIONS_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleaseDecisionDecision.REQUIRE_OFFLINE_RELEASE_LIMITATION_FIXES


def test_non_goals_missing():
    result = evaluate_agicore_trading_v1_offline_release_decision(_input(force_non_goals_missing=True))

    assert evaluate_offline_release_non_goals(_input(force_non_goals_missing=True)) == ()
    assert AGIcoreTradingV1OfflineReleaseDecisionRisk.OFFLINE_RELEASE_NON_GOALS_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleaseDecisionDecision.REQUIRE_OFFLINE_RELEASE_NON_GOAL_FIXES


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("force_live_trading_readiness_overclaim", AGIcoreTradingV1OfflineReleaseDecisionRisk.LIVE_TRADING_READINESS_OVERCLAIM),
        ("force_real_broker_readiness_overclaim", AGIcoreTradingV1OfflineReleaseDecisionRisk.REAL_BROKER_READINESS_OVERCLAIM),
        ("force_real_order_execution_overclaim", AGIcoreTradingV1OfflineReleaseDecisionRisk.REAL_ORDER_EXECUTION_OVERCLAIM),
        ("force_profitability_proof_overclaim", AGIcoreTradingV1OfflineReleaseDecisionRisk.PROFITABILITY_PROOF_OVERCLAIM),
        ("force_financial_advice_overclaim", AGIcoreTradingV1OfflineReleaseDecisionRisk.FINANCIAL_ADVICE_OVERCLAIM),
    ),
)
def test_product_overclaims_are_rejected(field, risk):
    result = evaluate_agicore_trading_v1_offline_release_decision(_input(**{field: True}))

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleaseDecisionDecision.REQUIRE_OFFLINE_RELEASE_NON_GOAL_FIXES
    assert evaluate_offline_release_product_readiness(_input(**{field: True})).offline_release_approved is False


def test_no_live_trading_and_no_profitability_claim_helpers():
    assert evaluate_offline_release_no_live_trading_claim(_input()) is True
    assert evaluate_offline_release_no_profitability_claim(_input()) is True
    assert evaluate_offline_release_no_live_trading_claim(_input(force_live_trading_readiness_overclaim=True)) is False
    assert evaluate_offline_release_no_profitability_claim(_input(force_profitability_proof_overclaim=True)) is False


def test_markdown_report():
    result = evaluate_agicore_trading_v1_offline_release_decision(_input())
    markdown = render_agicore_trading_v1_offline_release_decision_markdown_report(result)

    assert "# AGIcore Trading v1 Offline Release Decision" in markdown
    assert "offline sandbox only" in markdown
    assert "live_trading_ready: false" in markdown
    assert "real_broker_ready: false" in markdown
    assert "profitability_proven: false" in markdown
    assert "NOT_FINANCIAL_ADVICE" in markdown


def test_json_report():
    result = evaluate_agicore_trading_v1_offline_release_decision(_input())
    payload = json.loads(render_agicore_trading_v1_offline_release_decision_json_report(result))

    assert payload["schema"] == "agicore_trading_v1_offline_release_decision"
    assert payload["decision"] == "APPROVE_AGICORE_TRADING_V1_OFFLINE_RELEASE_DECISION"
    assert payload["live_trading_ready"] is False
    assert payload["real_broker_ready"] is False
    assert payload["real_orders_ready"] is False
    assert payload["profitability_proven"] is False
    assert payload["financial_advice"] is False


def test_metrics_score_risks_summary_and_recommendations_directly():
    result = evaluate_agicore_trading_v1_offline_release_decision(_input())
    risks = detect_agicore_trading_v1_offline_release_decision_risks(
        _input(),
        result.candidate_review_result,
        result.scope,
        result.capability_readiness,
        result.safety_boundary,
        result.testing_evidence,
        result.known_limitations,
        result.non_goals,
        result.product_readiness,
    )
    score = compute_agicore_trading_v1_offline_release_decision_score(
        _input(),
        result.candidate_review_result,
        result.scope,
        result.capability_readiness,
        result.safety_boundary,
        result.testing_evidence,
        result.known_limitations,
        result.non_goals,
        result.product_readiness,
        risks,
    )
    metrics = compute_agicore_trading_v1_offline_release_decision_metrics(
        result.capability_readiness,
        result.known_limitations,
        result.non_goals,
        result.testing_evidence,
        result.decision.value,
        score.overall_score,
    )
    summary = build_offline_release_decision_summary(result.decision)
    recommendations = generate_agicore_trading_v1_offline_release_decision_recommendations(risks)

    assert risks == ()
    assert score.overall_score == 100
    assert metrics.confirmed_capability_count == 8
    assert summary.next_phase == "AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES"
    assert recommendations == (
        AGIcoreTradingV1OfflineReleaseDecisionRecommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES,
    )


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("file_read_requested", AGIcoreTradingV1OfflineReleaseDecisionRisk.FILE_READ_BOUNDARY_VIOLATION),
        ("file_write_requested", AGIcoreTradingV1OfflineReleaseDecisionRisk.FILE_WRITE_BOUNDARY_VIOLATION),
        ("real_data_access_requested", AGIcoreTradingV1OfflineReleaseDecisionRisk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_access_requested", AGIcoreTradingV1OfflineReleaseDecisionRisk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("broker_connection_requested", AGIcoreTradingV1OfflineReleaseDecisionRisk.REAL_BROKER_BOUNDARY_VIOLATION),
        ("secret_read_requested", AGIcoreTradingV1OfflineReleaseDecisionRisk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("network_requested", AGIcoreTradingV1OfflineReleaseDecisionRisk.NETWORK_BOUNDARY_VIOLATION),
        ("http_requested", AGIcoreTradingV1OfflineReleaseDecisionRisk.NETWORK_BOUNDARY_VIOLATION),
        ("websocket_requested", AGIcoreTradingV1OfflineReleaseDecisionRisk.NETWORK_BOUNDARY_VIOLATION),
        ("socket_requested", AGIcoreTradingV1OfflineReleaseDecisionRisk.NETWORK_BOUNDARY_VIOLATION),
        ("external_api_requested", AGIcoreTradingV1OfflineReleaseDecisionRisk.NETWORK_BOUNDARY_VIOLATION),
        ("order_execution_requested", AGIcoreTradingV1OfflineReleaseDecisionRisk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ("account_access_requested", AGIcoreTradingV1OfflineReleaseDecisionRisk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ("position_mutation_requested", AGIcoreTradingV1OfflineReleaseDecisionRisk.POSITION_MUTATION_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations_are_blocked(field, risk):
    data = _input(**{field: True})
    result = evaluate_agicore_trading_v1_offline_release_decision(data)

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleaseDecisionDecision.REQUIRE_OFFLINE_RELEASE_SAFETY_FIXES
    assert assert_agicore_trading_v1_offline_release_decision_boundaries(data) is False


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
    result = evaluate_agicore_trading_v1_offline_release_decision(_input())

    assert result.file_read is False
    assert result.file_written is False
    assert result.data_accessed is False
    assert result.real_order_submitted is False
    assert result.real_account_accessed is False
    assert result.position_mutated is False
    assert result.safety_boundary.real_order_submitted is False
    assert result.safety_boundary.real_account_accessed is False
    assert result.safety_boundary.position_mutated is False
