from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agicore.trading.agicore_trading_v1_offline_final_readiness_review import (
    assert_agicore_trading_v1_offline_final_readiness_boundaries,
    build_final_readiness_context,
    compute_agicore_trading_v1_offline_final_readiness_score,
    detect_agicore_trading_v1_offline_final_readiness_risks,
    generate_agicore_trading_v1_offline_final_readiness_recommendations,
    render_agicore_trading_v1_offline_final_readiness_json_report,
    render_agicore_trading_v1_offline_final_readiness_markdown,
    review_agicore_trading_v1_offline_final_readiness,
    review_final_readiness_capabilities,
    review_final_readiness_documentation,
    review_final_readiness_known_limitations,
    review_final_readiness_local_runbook,
    review_final_readiness_no_financial_advice_claim,
    review_final_readiness_no_live_trading_claim,
    review_final_readiness_no_profitability_claim,
    review_final_readiness_non_goals,
    review_final_readiness_safety_boundaries,
    review_final_readiness_sandbox_usage_guide,
    review_final_readiness_smoke_demo,
    review_final_readiness_testing_evidence,
    validate_agicore_trading_v1_offline_final_readiness_input,
    validate_final_readiness_markdown,
)
from agicore.trading.agicore_trading_v1_offline_final_readiness_review_models import (
    AGIcoreTradingV1OfflineFinalReadinessDecision,
    AGIcoreTradingV1OfflineFinalReadinessInput,
    AGIcoreTradingV1OfflineFinalReadinessRecommendation,
    AGIcoreTradingV1OfflineFinalReadinessRisk,
    AGIcoreTradingV1OfflineFinalReadinessState,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/agicore_trading_v1_offline_final_readiness_review.py"
DOC_PATH = ROOT / "docs/AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_REVIEW.md"


def _input(**overrides):
    payload = {}
    payload.update(overrides)
    return AGIcoreTradingV1OfflineFinalReadinessInput(**payload)


def test_nominal_final_readiness_review():
    result = review_agicore_trading_v1_offline_final_readiness(_input())

    assert result.decision is AGIcoreTradingV1OfflineFinalReadinessDecision.APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_REVIEW
    assert result.state is AGIcoreTradingV1OfflineFinalReadinessState.READY_FOR_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert len(result.capabilities) == 15
    assert len(result.testing_evidence) == 4
    assert len(result.documentation_checks) == 4
    assert len(result.known_limitations) == 8
    assert len(result.non_goals) == 6
    assert validate_final_readiness_markdown(result.report.markdown)
    assert review_final_readiness_no_live_trading_claim(result.report.markdown)
    assert review_final_readiness_no_profitability_claim(result.report.markdown)
    assert review_final_readiness_no_financial_advice_claim(result.report.markdown)


def test_input_manquant():
    result = review_agicore_trading_v1_offline_final_readiness(None)

    assert validate_agicore_trading_v1_offline_final_readiness_input(None) is False
    assert AGIcoreTradingV1OfflineFinalReadinessRisk.FINAL_READINESS_INPUT_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalReadinessDecision.REQUIRE_FINAL_READINESS_INPUT_FIXES
    assert result.state is AGIcoreTradingV1OfflineFinalReadinessState.AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_INPUT_INVALID


def test_capabilities_incompletes():
    result = review_agicore_trading_v1_offline_final_readiness(_input(force_capabilities_incomplete=True))

    assert AGIcoreTradingV1OfflineFinalReadinessRisk.FINAL_READINESS_CAPABILITIES_INCOMPLETE in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalReadinessDecision.REQUIRE_FINAL_READINESS_CAPABILITY_FIXES


def test_testing_evidence_manquante():
    result = review_agicore_trading_v1_offline_final_readiness(_input(force_testing_evidence_missing=True))

    assert AGIcoreTradingV1OfflineFinalReadinessRisk.FINAL_READINESS_TESTING_EVIDENCE_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalReadinessDecision.REQUIRE_FINAL_READINESS_TESTING_EVIDENCE_FIXES


def test_documentation_manquante():
    result = review_agicore_trading_v1_offline_final_readiness(_input(force_documentation_missing=True))

    assert AGIcoreTradingV1OfflineFinalReadinessRisk.FINAL_READINESS_DOCUMENTATION_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalReadinessDecision.REQUIRE_FINAL_READINESS_DOCUMENTATION_FIXES


def test_smoke_demo_manquante():
    result = review_agicore_trading_v1_offline_final_readiness(_input(force_smoke_demo_missing=True))

    assert AGIcoreTradingV1OfflineFinalReadinessRisk.FINAL_READINESS_SMOKE_DEMO_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalReadinessDecision.REQUIRE_FINAL_READINESS_SMOKE_DEMO_FIXES
    assert review_final_readiness_smoke_demo(_input(force_smoke_demo_missing=True)) is False


def test_sandbox_usage_guide_manquant():
    result = review_agicore_trading_v1_offline_final_readiness(_input(force_sandbox_usage_guide_missing=True))

    assert AGIcoreTradingV1OfflineFinalReadinessRisk.FINAL_READINESS_SANDBOX_USAGE_GUIDE_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalReadinessDecision.REQUIRE_FINAL_READINESS_DOCUMENTATION_FIXES
    assert review_final_readiness_sandbox_usage_guide(_input(force_sandbox_usage_guide_missing=True)) is False


def test_local_runbook_manquant():
    result = review_agicore_trading_v1_offline_final_readiness(_input(force_local_runbook_missing=True))

    assert AGIcoreTradingV1OfflineFinalReadinessRisk.FINAL_READINESS_LOCAL_RUNBOOK_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalReadinessDecision.REQUIRE_FINAL_READINESS_DOCUMENTATION_FIXES
    assert review_final_readiness_local_runbook(_input(force_local_runbook_missing=True)) is False


def test_safety_boundary_manquante():
    result = review_agicore_trading_v1_offline_final_readiness(_input(force_safety_boundary_missing=True))

    assert AGIcoreTradingV1OfflineFinalReadinessRisk.FINAL_READINESS_SAFETY_BOUNDARY_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalReadinessDecision.REQUIRE_FINAL_READINESS_SAFETY_FIXES
    assert review_final_readiness_safety_boundaries(_input(force_safety_boundary_missing=True)) is False


def test_limitations_manquantes():
    result = review_agicore_trading_v1_offline_final_readiness(_input(force_limitations_missing=True))

    assert AGIcoreTradingV1OfflineFinalReadinessRisk.FINAL_READINESS_LIMITATIONS_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalReadinessDecision.REQUIRE_FINAL_READINESS_LIMITATION_FIXES


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("force_live_trading_overclaim", AGIcoreTradingV1OfflineFinalReadinessRisk.LIVE_TRADING_READINESS_OVERCLAIM),
        ("force_real_broker_overclaim", AGIcoreTradingV1OfflineFinalReadinessRisk.REAL_BROKER_READINESS_OVERCLAIM),
        ("force_real_order_overclaim", AGIcoreTradingV1OfflineFinalReadinessRisk.REAL_ORDER_EXECUTION_OVERCLAIM),
        ("force_paper_broker_overclaim", AGIcoreTradingV1OfflineFinalReadinessRisk.PAPER_BROKER_CONNECTION_OVERCLAIM),
        ("force_profitability_overclaim", AGIcoreTradingV1OfflineFinalReadinessRisk.PROFITABILITY_PROOF_OVERCLAIM),
        ("force_financial_advice_overclaim", AGIcoreTradingV1OfflineFinalReadinessRisk.FINANCIAL_ADVICE_OVERCLAIM),
    ),
)
def test_overclaims_are_rejected(field, risk):
    result = review_agicore_trading_v1_offline_final_readiness(_input(**{field: True}))

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalReadinessDecision.REQUIRE_FINAL_READINESS_NO_OVERCLAIM_FIXES


def test_markdown_genere_and_helpers():
    data = _input()
    result = review_agicore_trading_v1_offline_final_readiness(data)
    context = build_final_readiness_context(data)
    capabilities = review_final_readiness_capabilities(data)
    testing_evidence = review_final_readiness_testing_evidence(data)
    documentation = review_final_readiness_documentation(data)
    limitations = review_final_readiness_known_limitations(data)
    non_goals = review_final_readiness_non_goals()

    assert "# AGIcore Trading v1 Offline Final Readiness Review" in result.report.markdown
    assert len(capabilities) == 15
    assert len(testing_evidence) == 4
    assert len(documentation) == 4
    assert len(limitations) == 8
    assert len(non_goals) == 6
    assert render_agicore_trading_v1_offline_final_readiness_markdown(
        context,
        capabilities,
        testing_evidence,
        documentation,
        result.readiness_criteria,
        limitations,
        non_goals,
    )


def test_markdown_docs_valide():
    markdown = DOC_PATH.read_text(encoding="utf-8")

    assert validate_final_readiness_markdown(markdown)
    assert review_final_readiness_no_live_trading_claim(markdown)
    assert review_final_readiness_no_profitability_claim(markdown)
    assert review_final_readiness_no_financial_advice_claim(markdown)
    assert "AGIcore Trading v1 Offline Release Package" in markdown


def test_json_report():
    result = review_agicore_trading_v1_offline_final_readiness(_input())
    payload = json.loads(render_agicore_trading_v1_offline_final_readiness_json_report(result))

    assert payload["schema"] == "agicore_trading_v1_offline_final_readiness_review"
    assert payload["decision"] == "APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_REVIEW"
    assert payload["score"] == 100
    assert payload["live_trading_ready"] is False
    assert payload["real_broker_ready"] is False
    assert payload["real_order_execution"] is False
    assert payload["paper_broker_connected"] is False
    assert payload["profitability_proven"] is False
    assert payload["financial_advice"] is False


def test_score_risks_and_recommendations_directly():
    result = review_agicore_trading_v1_offline_final_readiness(_input())
    risks = detect_agicore_trading_v1_offline_final_readiness_risks(
        _input(),
        result.report.markdown,
        result.capabilities,
        result.testing_evidence,
        result.documentation_checks,
        result.known_limitations,
    )
    score = compute_agicore_trading_v1_offline_final_readiness_score(
        _input(),
        result.report.markdown,
        result.capabilities,
        result.testing_evidence,
        result.documentation_checks,
        result.readiness_criteria,
        result.known_limitations,
        result.non_goals,
        risks,
    )
    recommendations = generate_agicore_trading_v1_offline_final_readiness_recommendations(risks)

    assert risks == ()
    assert score.overall_score == 100
    assert recommendations == (
        AGIcoreTradingV1OfflineFinalReadinessRecommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE,
    )


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("file_read_requested", AGIcoreTradingV1OfflineFinalReadinessRisk.FILE_READ_BOUNDARY_VIOLATION),
        ("real_data_access_requested", AGIcoreTradingV1OfflineFinalReadinessRisk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_access_requested", AGIcoreTradingV1OfflineFinalReadinessRisk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("broker_connection_requested", AGIcoreTradingV1OfflineFinalReadinessRisk.REAL_BROKER_BOUNDARY_VIOLATION),
        ("secret_read_requested", AGIcoreTradingV1OfflineFinalReadinessRisk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("network_requested", AGIcoreTradingV1OfflineFinalReadinessRisk.NETWORK_BOUNDARY_VIOLATION),
        ("http_requested", AGIcoreTradingV1OfflineFinalReadinessRisk.NETWORK_BOUNDARY_VIOLATION),
        ("websocket_requested", AGIcoreTradingV1OfflineFinalReadinessRisk.NETWORK_BOUNDARY_VIOLATION),
        ("socket_requested", AGIcoreTradingV1OfflineFinalReadinessRisk.NETWORK_BOUNDARY_VIOLATION),
        ("external_api_requested", AGIcoreTradingV1OfflineFinalReadinessRisk.NETWORK_BOUNDARY_VIOLATION),
        ("order_execution_requested", AGIcoreTradingV1OfflineFinalReadinessRisk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ("account_access_requested", AGIcoreTradingV1OfflineFinalReadinessRisk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ("position_mutation_requested", AGIcoreTradingV1OfflineFinalReadinessRisk.POSITION_MUTATION_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations_are_blocked(field, risk):
    data = _input(**{field: True})
    result = review_agicore_trading_v1_offline_final_readiness(data)

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalReadinessDecision.BLOCK_AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_REVIEW
    assert assert_agicore_trading_v1_offline_final_readiness_boundaries(data) is False


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
    result = review_agicore_trading_v1_offline_final_readiness(_input())

    assert result.file_read is False
    assert result.data_accessed is False
    assert result.real_order_submitted is False
    assert result.real_account_accessed is False
    assert result.position_mutated is False
