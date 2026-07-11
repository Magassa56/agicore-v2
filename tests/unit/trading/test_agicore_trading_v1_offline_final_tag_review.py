from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agicore.trading.agicore_trading_v1_offline_final_tag_review import (
    assert_agicore_trading_v1_offline_final_tag_review_boundaries,
    build_final_tag_review_context,
    compute_agicore_trading_v1_offline_final_tag_review_score,
    detect_agicore_trading_v1_offline_final_tag_review_risks,
    generate_agicore_trading_v1_offline_final_tag_review_recommendations,
    render_agicore_trading_v1_offline_final_tag_review_json_report,
    render_agicore_trading_v1_offline_final_tag_review_markdown,
    review_agicore_trading_v1_offline_final_tag,
    review_final_tag_documents,
    review_final_tag_final_readiness,
    review_final_tag_name,
    review_final_tag_no_financial_advice_claim,
    review_final_tag_no_git_tag_created,
    review_final_tag_no_live_trading_claim,
    review_final_tag_no_profitability_claim,
    review_final_tag_preparation_approval,
    review_final_tag_release_package,
    review_final_tag_release_package_review,
    review_final_tag_safety_boundaries,
    review_final_tag_testing_evidence,
    review_final_tag_version,
    validate_agicore_trading_v1_offline_final_tag_review_input,
    validate_final_tag_review_markdown,
)
from agicore.trading.agicore_trading_v1_offline_final_tag_review_models import (
    AGIcoreTradingV1OfflineFinalTagReviewDecision,
    AGIcoreTradingV1OfflineFinalTagReviewInput,
    AGIcoreTradingV1OfflineFinalTagReviewRecommendation,
    AGIcoreTradingV1OfflineFinalTagReviewRisk,
    AGIcoreTradingV1OfflineFinalTagReviewState,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/agicore_trading_v1_offline_final_tag_review.py"
DOC_PATH = ROOT / "docs/AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW.md"


def _input(**overrides):
    payload = {}
    payload.update(overrides)
    return AGIcoreTradingV1OfflineFinalTagReviewInput(**payload)


def test_nominal_final_tag_review():
    result = review_agicore_trading_v1_offline_final_tag(_input())

    assert result.decision is AGIcoreTradingV1OfflineFinalTagReviewDecision.APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW
    assert result.state is AGIcoreTradingV1OfflineFinalTagReviewState.READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.git_tag_created is False
    assert len(result.context.documents) == 7
    assert len(result.context.testing_evidence) == 4
    assert result.context.tag_metadata.tag_name == "agicore-trading-v1-offline"
    assert result.context.tag_metadata.version == "v1.0.0-offline"
    assert validate_final_tag_review_markdown(result.report.markdown)


def test_input_manquant():
    result = review_agicore_trading_v1_offline_final_tag(None)

    assert validate_agicore_trading_v1_offline_final_tag_review_input(None) is False
    assert AGIcoreTradingV1OfflineFinalTagReviewRisk.FINAL_TAG_REVIEW_INPUT_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalTagReviewDecision.REQUIRE_FINAL_TAG_REVIEW_INPUT_FIXES
    assert result.state is AGIcoreTradingV1OfflineFinalTagReviewState.AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW_INPUT_INVALID


def test_tag_preparation_non_approuvee():
    result = review_agicore_trading_v1_offline_final_tag(_input(tag_preparation_approved=False))

    assert review_final_tag_preparation_approval(_input(tag_preparation_approved=False)) is False
    assert AGIcoreTradingV1OfflineFinalTagReviewRisk.FINAL_TAG_PREPARATION_NOT_APPROVED in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalTagReviewDecision.REQUIRE_FINAL_TAG_PREPARATION_FIXES


def test_tag_name_invalide():
    result = review_agicore_trading_v1_offline_final_tag(_input(tag_name="bad-tag"))

    assert review_final_tag_name(_input(tag_name="bad-tag")) is False
    assert AGIcoreTradingV1OfflineFinalTagReviewRisk.FINAL_TAG_NAME_INVALID in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalTagReviewDecision.REQUIRE_FINAL_TAG_NAME_FIXES


def test_version_invalide():
    result = review_agicore_trading_v1_offline_final_tag(_input(version="v1-live"))

    assert review_final_tag_version(_input(version="v1-live")) is False
    assert AGIcoreTradingV1OfflineFinalTagReviewRisk.FINAL_TAG_VERSION_INVALID in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalTagReviewDecision.REQUIRE_FINAL_TAG_VERSION_FIXES


def test_documents_manquants():
    data = _input(documents_present=False)
    context = build_final_tag_review_context(data)
    result = review_agicore_trading_v1_offline_final_tag(data)

    assert review_final_tag_documents(context) is False
    assert AGIcoreTradingV1OfflineFinalTagReviewRisk.FINAL_TAG_DOCUMENTS_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalTagReviewDecision.REQUIRE_FINAL_TAG_DOCUMENT_FIXES


def test_release_package_manquant():
    result = review_agicore_trading_v1_offline_final_tag(_input(release_package_validated=False))

    assert review_final_tag_release_package(_input(release_package_validated=False)) is False
    assert AGIcoreTradingV1OfflineFinalTagReviewRisk.FINAL_TAG_RELEASE_PACKAGE_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalTagReviewDecision.REQUIRE_FINAL_TAG_RELEASE_PACKAGE_FIXES


def test_release_package_review_manquante():
    result = review_agicore_trading_v1_offline_final_tag(_input(release_package_review_validated=False))

    assert review_final_tag_release_package_review(_input(release_package_review_validated=False)) is False
    assert AGIcoreTradingV1OfflineFinalTagReviewRisk.FINAL_TAG_RELEASE_PACKAGE_REVIEW_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalTagReviewDecision.REQUIRE_FINAL_TAG_RELEASE_PACKAGE_FIXES


def test_final_readiness_manquante():
    result = review_agicore_trading_v1_offline_final_tag(_input(final_readiness_validated=False))

    assert review_final_tag_final_readiness(_input(final_readiness_validated=False)) is False
    assert AGIcoreTradingV1OfflineFinalTagReviewRisk.FINAL_TAG_FINAL_READINESS_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalTagReviewDecision.REQUIRE_FINAL_TAG_RELEASE_PACKAGE_FIXES


def test_testing_evidence_manquante():
    data = _input(testing_evidence_present=False)
    context = build_final_tag_review_context(data)
    result = review_agicore_trading_v1_offline_final_tag(data)

    assert review_final_tag_testing_evidence(context) is False
    assert AGIcoreTradingV1OfflineFinalTagReviewRisk.FINAL_TAG_TESTING_EVIDENCE_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalTagReviewDecision.REQUIRE_FINAL_TAG_TESTING_EVIDENCE_FIXES


def test_git_tag_already_created():
    result = review_agicore_trading_v1_offline_final_tag(_input(git_tag_already_created=True))

    assert review_final_tag_no_git_tag_created(_input(git_tag_already_created=True)) is False
    assert AGIcoreTradingV1OfflineFinalTagReviewRisk.GIT_TAG_ALREADY_CREATED in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalTagReviewDecision.REQUIRE_FINAL_TAG_NO_OVERCLAIM_FIXES
    assert result.git_tag_created is False


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("live_trading_overclaim", AGIcoreTradingV1OfflineFinalTagReviewRisk.LIVE_TRADING_READINESS_OVERCLAIM),
        ("real_broker_overclaim", AGIcoreTradingV1OfflineFinalTagReviewRisk.REAL_BROKER_READINESS_OVERCLAIM),
        ("real_order_overclaim", AGIcoreTradingV1OfflineFinalTagReviewRisk.REAL_ORDER_EXECUTION_OVERCLAIM),
        ("paper_broker_overclaim", AGIcoreTradingV1OfflineFinalTagReviewRisk.PAPER_BROKER_CONNECTION_OVERCLAIM),
        ("profitability_overclaim", AGIcoreTradingV1OfflineFinalTagReviewRisk.PROFITABILITY_PROOF_OVERCLAIM),
        ("financial_advice_overclaim", AGIcoreTradingV1OfflineFinalTagReviewRisk.FINANCIAL_ADVICE_OVERCLAIM),
    ),
)
def test_overclaims_are_blocked(field, risk):
    data = _input(**{field: True})
    result = review_agicore_trading_v1_offline_final_tag(data)

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalTagReviewDecision.REQUIRE_FINAL_TAG_NO_OVERCLAIM_FIXES


def test_no_overclaim_helpers():
    assert review_final_tag_no_live_trading_claim(_input()) is True
    assert review_final_tag_no_live_trading_claim(_input(live_trading_overclaim=True)) is False
    assert review_final_tag_no_profitability_claim(_input()) is True
    assert review_final_tag_no_profitability_claim(_input(profitability_overclaim=True)) is False
    assert review_final_tag_no_financial_advice_claim(_input()) is True
    assert review_final_tag_no_financial_advice_claim(_input(financial_advice_overclaim=True)) is False


def test_markdown_genere():
    data = _input()
    context = build_final_tag_review_context(data)
    result = review_agicore_trading_v1_offline_final_tag(data)
    markdown = render_agicore_trading_v1_offline_final_tag_review_markdown(context, result.findings)

    assert "AGIcore Trading v1 Offline Final Tag Review" in markdown
    assert "agicore-trading-v1-offline" in markdown
    assert "v1.0.0-offline" in markdown
    assert "aucun tag Git cree" in markdown
    assert validate_final_tag_review_markdown(markdown)


def test_markdown_docs_valide():
    markdown = DOC_PATH.read_text(encoding="utf-8")

    assert validate_final_tag_review_markdown(markdown)
    assert "AGIcore Trading v1 Offline Tag Creation Instructions" in markdown


def test_json_report():
    result = review_agicore_trading_v1_offline_final_tag(_input())
    payload = json.loads(render_agicore_trading_v1_offline_final_tag_review_json_report(result))

    assert payload["schema"] == "agicore_trading_v1_offline_final_tag_review"
    assert payload["decision"] == "APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW"
    assert payload["state"] == "READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS"
    assert payload["score"] == 100
    assert payload["context"]["tag_metadata"]["tag_name"] == "agicore-trading-v1-offline"
    assert payload["git_tag_created"] is False
    assert payload["real_broker_ready"] is False
    assert payload["real_order_execution"] is False


def test_score_risks_and_recommendations_directly():
    data = _input()
    context = build_final_tag_review_context(data)
    risks = detect_agicore_trading_v1_offline_final_tag_review_risks(data, context)
    score = compute_agicore_trading_v1_offline_final_tag_review_score(data, context, risks)
    recommendations = generate_agicore_trading_v1_offline_final_tag_review_recommendations(risks)

    assert risks == ()
    assert score.overall_score == 100
    assert recommendations == (
        AGIcoreTradingV1OfflineFinalTagReviewRecommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS,
    )


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("file_read_requested", AGIcoreTradingV1OfflineFinalTagReviewRisk.FILE_READ_BOUNDARY_VIOLATION),
        ("real_data_access_requested", AGIcoreTradingV1OfflineFinalTagReviewRisk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_access_requested", AGIcoreTradingV1OfflineFinalTagReviewRisk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("broker_connection_requested", AGIcoreTradingV1OfflineFinalTagReviewRisk.REAL_BROKER_BOUNDARY_VIOLATION),
        ("secret_read_requested", AGIcoreTradingV1OfflineFinalTagReviewRisk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("network_requested", AGIcoreTradingV1OfflineFinalTagReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("http_requested", AGIcoreTradingV1OfflineFinalTagReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("websocket_requested", AGIcoreTradingV1OfflineFinalTagReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("socket_requested", AGIcoreTradingV1OfflineFinalTagReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("external_api_requested", AGIcoreTradingV1OfflineFinalTagReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("order_execution_requested", AGIcoreTradingV1OfflineFinalTagReviewRisk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ("account_access_requested", AGIcoreTradingV1OfflineFinalTagReviewRisk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ("position_mutation_requested", AGIcoreTradingV1OfflineFinalTagReviewRisk.POSITION_MUTATION_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations_are_blocked(field, risk):
    data = _input(**{field: True})
    result = review_agicore_trading_v1_offline_final_tag(data)

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalTagReviewDecision.REQUIRE_FINAL_TAG_NO_OVERCLAIM_FIXES
    assert assert_agicore_trading_v1_offline_final_tag_review_boundaries(data) is False
    assert review_final_tag_safety_boundaries(data) is False


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
    result = review_agicore_trading_v1_offline_final_tag(_input())

    assert result.file_read is False
    assert result.data_accessed is False
    assert result.git_tag_created is False
    assert result.real_order_submitted is False
    assert result.real_account_accessed is False
    assert result.position_mutated is False
