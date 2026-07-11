from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agicore.trading.agicore_trading_v1_offline_release_package_review import (
    assert_agicore_trading_v1_offline_release_package_review_boundaries,
    build_release_package_review_context,
    compute_agicore_trading_v1_offline_release_package_review_score,
    detect_agicore_trading_v1_offline_release_package_review_risks,
    generate_agicore_trading_v1_offline_release_package_review_recommendations,
    render_agicore_trading_v1_offline_release_package_review_json_report,
    render_agicore_trading_v1_offline_release_package_review_markdown,
    review_agicore_trading_v1_offline_release_package,
    review_release_package_capabilities,
    review_release_package_commands,
    review_release_package_documents,
    review_release_package_human_readability,
    review_release_package_known_limitations,
    review_release_package_no_financial_advice_claim,
    review_release_package_no_live_trading_claim,
    review_release_package_no_profitability_claim,
    review_release_package_non_goals,
    review_release_package_safety_rules,
    review_release_package_testing_evidence,
    validate_agicore_trading_v1_offline_release_package_review_input,
    validate_release_package_review_markdown,
)
from agicore.trading.agicore_trading_v1_offline_release_package_review_models import (
    AGIcoreTradingV1OfflineReleasePackageReviewDecision,
    AGIcoreTradingV1OfflineReleasePackageReviewInput,
    AGIcoreTradingV1OfflineReleasePackageReviewRecommendation,
    AGIcoreTradingV1OfflineReleasePackageReviewRisk,
    AGIcoreTradingV1OfflineReleasePackageReviewState,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/agicore_trading_v1_offline_release_package_review.py"
DOC_PATH = ROOT / "docs/AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW.md"


def _input(**overrides):
    payload = {}
    payload.update(overrides)
    return AGIcoreTradingV1OfflineReleasePackageReviewInput(**payload)


def test_nominal_release_package_review():
    result = review_agicore_trading_v1_offline_release_package(_input())

    assert result.decision is AGIcoreTradingV1OfflineReleasePackageReviewDecision.APPROVE_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW
    assert result.state is AGIcoreTradingV1OfflineReleasePackageReviewState.READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert len(result.documents) == 5
    assert len(result.capabilities) == 10
    assert len(result.testing_evidence) == 4
    assert len(result.criteria) == 9
    assert len(result.findings) == 9
    assert validate_release_package_review_markdown(result.report.markdown)
    assert review_release_package_human_readability(result.report.markdown)
    assert review_release_package_no_live_trading_claim(result.report.markdown)
    assert review_release_package_no_profitability_claim(result.report.markdown)
    assert review_release_package_no_financial_advice_claim(result.report.markdown)


def test_input_manquant():
    result = review_agicore_trading_v1_offline_release_package(None)

    assert validate_agicore_trading_v1_offline_release_package_review_input(None) is False
    assert AGIcoreTradingV1OfflineReleasePackageReviewRisk.RELEASE_PACKAGE_REVIEW_INPUT_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleasePackageReviewDecision.REQUIRE_RELEASE_PACKAGE_REVIEW_INPUT_FIXES
    assert result.state is AGIcoreTradingV1OfflineReleasePackageReviewState.AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW_INPUT_INVALID


def test_documents_review_incomplet():
    result = review_agicore_trading_v1_offline_release_package(_input(force_documents_incomplete=True))

    assert AGIcoreTradingV1OfflineReleasePackageReviewRisk.RELEASE_PACKAGE_DOCUMENT_REVIEW_INCOMPLETE in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleasePackageReviewDecision.REQUIRE_RELEASE_PACKAGE_DOCUMENT_REVIEW_FIXES


def test_capabilities_review_incomplet():
    result = review_agicore_trading_v1_offline_release_package(_input(force_capabilities_incomplete=True))

    assert AGIcoreTradingV1OfflineReleasePackageReviewRisk.RELEASE_PACKAGE_CAPABILITY_REVIEW_INCOMPLETE in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleasePackageReviewDecision.REQUIRE_RELEASE_PACKAGE_CAPABILITY_REVIEW_FIXES


def test_testing_evidence_missing():
    result = review_agicore_trading_v1_offline_release_package(_input(force_testing_evidence_missing=True))

    assert AGIcoreTradingV1OfflineReleasePackageReviewRisk.RELEASE_PACKAGE_TESTING_EVIDENCE_REVIEW_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleasePackageReviewDecision.REQUIRE_RELEASE_PACKAGE_TESTING_EVIDENCE_REVIEW_FIXES


def test_command_review_missing():
    result = review_agicore_trading_v1_offline_release_package(_input(force_commands_missing=True))

    assert AGIcoreTradingV1OfflineReleasePackageReviewRisk.RELEASE_PACKAGE_COMMAND_REVIEW_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleasePackageReviewDecision.REQUIRE_RELEASE_PACKAGE_COMMAND_REVIEW_FIXES
    assert review_release_package_commands(_input(force_commands_missing=True)) is False


def test_safety_review_missing():
    result = review_agicore_trading_v1_offline_release_package(_input(force_safety_missing=True))

    assert AGIcoreTradingV1OfflineReleasePackageReviewRisk.RELEASE_PACKAGE_SAFETY_REVIEW_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleasePackageReviewDecision.REQUIRE_RELEASE_PACKAGE_SAFETY_REVIEW_FIXES
    assert review_release_package_safety_rules(_input(force_safety_missing=True)) is False


def test_limitations_review_missing():
    result = review_agicore_trading_v1_offline_release_package(_input(force_limitations_missing=True))

    assert AGIcoreTradingV1OfflineReleasePackageReviewRisk.RELEASE_PACKAGE_LIMITATION_REVIEW_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleasePackageReviewDecision.REQUIRE_RELEASE_PACKAGE_LIMITATION_REVIEW_FIXES
    assert review_release_package_known_limitations(_input(force_limitations_missing=True)) is False


def test_non_goals_review_missing():
    result = review_agicore_trading_v1_offline_release_package(_input(force_non_goals_missing=True))

    assert AGIcoreTradingV1OfflineReleasePackageReviewRisk.RELEASE_PACKAGE_NON_GOAL_REVIEW_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleasePackageReviewDecision.REQUIRE_RELEASE_PACKAGE_SAFETY_REVIEW_FIXES
    assert review_release_package_non_goals(_input(force_non_goals_missing=True)) is False


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("force_live_trading_overclaim", AGIcoreTradingV1OfflineReleasePackageReviewRisk.LIVE_TRADING_READINESS_OVERCLAIM),
        ("force_real_broker_overclaim", AGIcoreTradingV1OfflineReleasePackageReviewRisk.REAL_BROKER_READINESS_OVERCLAIM),
        ("force_real_order_overclaim", AGIcoreTradingV1OfflineReleasePackageReviewRisk.REAL_ORDER_EXECUTION_OVERCLAIM),
        ("force_paper_broker_overclaim", AGIcoreTradingV1OfflineReleasePackageReviewRisk.PAPER_BROKER_CONNECTION_OVERCLAIM),
        ("force_profitability_overclaim", AGIcoreTradingV1OfflineReleasePackageReviewRisk.PROFITABILITY_PROOF_OVERCLAIM),
        ("force_financial_advice_overclaim", AGIcoreTradingV1OfflineReleasePackageReviewRisk.FINANCIAL_ADVICE_OVERCLAIM),
    ),
)
def test_overclaims_are_rejected(field, risk):
    result = review_agicore_trading_v1_offline_release_package(_input(**{field: True}))

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleasePackageReviewDecision.REQUIRE_RELEASE_PACKAGE_NO_OVERCLAIM_FIXES


def test_markdown_genere_and_helpers():
    result = review_agicore_trading_v1_offline_release_package(_input())
    context = build_release_package_review_context(_input())
    documents = review_release_package_documents(_input())
    capabilities = review_release_package_capabilities(_input())
    testing_evidence = review_release_package_testing_evidence(_input())

    assert "# AGIcore Trading v1 Offline Release Package Review" in result.report.markdown
    assert len(documents) == 5
    assert len(capabilities) == 10
    assert len(testing_evidence) == 4
    assert render_agicore_trading_v1_offline_release_package_review_markdown(
        context,
        documents,
        capabilities,
        testing_evidence,
        result.criteria,
    )


def test_markdown_docs_valide():
    markdown = DOC_PATH.read_text(encoding="utf-8")

    assert validate_release_package_review_markdown(markdown)
    assert review_release_package_no_live_trading_claim(markdown)
    assert review_release_package_no_profitability_claim(markdown)
    assert review_release_package_no_financial_advice_claim(markdown)
    assert "AGIcore Trading v1 Offline Tag Preparation" in markdown


def test_json_report():
    result = review_agicore_trading_v1_offline_release_package(_input())
    payload = json.loads(render_agicore_trading_v1_offline_release_package_review_json_report(result))

    assert payload["schema"] == "agicore_trading_v1_offline_release_package_review"
    assert payload["decision"] == "APPROVE_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW"
    assert payload["score"] == 100
    assert payload["live_trading_ready"] is False
    assert payload["real_broker_ready"] is False
    assert payload["real_order_execution"] is False
    assert payload["paper_broker_connected"] is False
    assert payload["profitability_proven"] is False
    assert payload["financial_advice"] is False


def test_score_risks_and_recommendations_directly():
    result = review_agicore_trading_v1_offline_release_package(_input())
    risks = detect_agicore_trading_v1_offline_release_package_review_risks(
        _input(),
        result.report.markdown,
        result.documents,
        result.capabilities,
        result.testing_evidence,
        result.criteria,
    )
    score = compute_agicore_trading_v1_offline_release_package_review_score(
        _input(),
        result.report.markdown,
        result.documents,
        result.capabilities,
        result.testing_evidence,
        result.criteria,
        risks,
    )
    recommendations = generate_agicore_trading_v1_offline_release_package_review_recommendations(risks)

    assert risks == ()
    assert score.overall_score == 100
    assert recommendations == (
        AGIcoreTradingV1OfflineReleasePackageReviewRecommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION,
    )


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("file_read_requested", AGIcoreTradingV1OfflineReleasePackageReviewRisk.FILE_READ_BOUNDARY_VIOLATION),
        ("real_data_access_requested", AGIcoreTradingV1OfflineReleasePackageReviewRisk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_access_requested", AGIcoreTradingV1OfflineReleasePackageReviewRisk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("broker_connection_requested", AGIcoreTradingV1OfflineReleasePackageReviewRisk.REAL_BROKER_BOUNDARY_VIOLATION),
        ("secret_read_requested", AGIcoreTradingV1OfflineReleasePackageReviewRisk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("network_requested", AGIcoreTradingV1OfflineReleasePackageReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("http_requested", AGIcoreTradingV1OfflineReleasePackageReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("websocket_requested", AGIcoreTradingV1OfflineReleasePackageReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("socket_requested", AGIcoreTradingV1OfflineReleasePackageReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("external_api_requested", AGIcoreTradingV1OfflineReleasePackageReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("order_execution_requested", AGIcoreTradingV1OfflineReleasePackageReviewRisk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ("account_access_requested", AGIcoreTradingV1OfflineReleasePackageReviewRisk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ("position_mutation_requested", AGIcoreTradingV1OfflineReleasePackageReviewRisk.POSITION_MUTATION_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations_are_blocked(field, risk):
    data = _input(**{field: True})
    result = review_agicore_trading_v1_offline_release_package(data)

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleasePackageReviewDecision.BLOCK_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW
    assert assert_agicore_trading_v1_offline_release_package_review_boundaries(data) is False


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
    result = review_agicore_trading_v1_offline_release_package(_input())

    assert result.file_read is False
    assert result.data_accessed is False
    assert result.real_order_submitted is False
    assert result.real_account_accessed is False
    assert result.position_mutated is False
