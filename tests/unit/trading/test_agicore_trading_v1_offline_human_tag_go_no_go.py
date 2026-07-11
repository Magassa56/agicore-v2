from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agicore.trading.agicore_trading_v1_offline_human_tag_go_no_go import (
    assert_agicore_trading_v1_offline_human_tag_go_no_go_boundaries,
    build_human_tag_go_no_go_context,
    compute_agicore_trading_v1_offline_human_tag_go_no_go_score,
    detect_agicore_trading_v1_offline_human_tag_go_no_go_risks,
    evaluate_agicore_trading_v1_offline_human_tag_go_no_go,
    generate_agicore_trading_v1_offline_human_tag_go_no_go_recommendations,
    render_agicore_trading_v1_offline_human_tag_go_no_go_json_report,
    render_agicore_trading_v1_offline_human_tag_go_no_go_markdown,
    review_human_tag_creation_instructions_review,
    review_human_tag_final_readiness_review,
    review_human_tag_final_tag_review,
    review_human_tag_go_decision,
    review_human_tag_guardrails,
    review_human_tag_name,
    review_human_tag_no_financial_advice_claim,
    review_human_tag_no_git_tag_created,
    review_human_tag_no_git_tag_pushed,
    review_human_tag_no_live_trading_claim,
    review_human_tag_no_profitability_claim,
    review_human_tag_prerequisites,
    review_human_tag_release_package_review,
    review_human_tag_version,
    validate_agicore_trading_v1_offline_human_tag_go_no_go_input,
    validate_human_tag_go_no_go_markdown,
)
from agicore.trading.agicore_trading_v1_offline_human_tag_go_no_go_models import (
    AGIcoreTradingV1OfflineHumanTagGoNoGoDecision,
    AGIcoreTradingV1OfflineHumanTagGoNoGoInput,
    AGIcoreTradingV1OfflineHumanTagGoNoGoRecommendation,
    AGIcoreTradingV1OfflineHumanTagGoNoGoRisk,
    AGIcoreTradingV1OfflineHumanTagGoNoGoState,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/agicore_trading_v1_offline_human_tag_go_no_go.py"
DOC_PATH = ROOT / "docs/AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO.md"


def _input(**overrides):
    payload = {}
    payload.update(overrides)
    return AGIcoreTradingV1OfflineHumanTagGoNoGoInput(**payload)


def test_nominal_human_tag_go_no_go():
    result = evaluate_agicore_trading_v1_offline_human_tag_go_no_go(_input())

    assert result.decision is AGIcoreTradingV1OfflineHumanTagGoNoGoDecision.APPROVE_AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO
    assert result.state is AGIcoreTradingV1OfflineHumanTagGoNoGoState.READY_FOR_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_FINAL_CHECKLIST
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.git_tag_created is False
    assert result.git_tag_pushed is False
    assert result.context.tag_metadata.tag_name == "agicore-trading-v1-offline"
    assert result.context.tag_metadata.version == "v1.0.0-offline"
    assert result.context.tag_metadata.human_decision == "GO_FOR_MANUAL_TAG_CREATION_LATER"
    assert validate_human_tag_go_no_go_markdown(result.report.markdown)


def test_input_manquant():
    result = evaluate_agicore_trading_v1_offline_human_tag_go_no_go(None)

    assert validate_agicore_trading_v1_offline_human_tag_go_no_go_input(None) is False
    assert AGIcoreTradingV1OfflineHumanTagGoNoGoRisk.HUMAN_TAG_GO_NO_GO_INPUT_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineHumanTagGoNoGoDecision.REQUIRE_HUMAN_TAG_INPUT_FIXES
    assert result.state is AGIcoreTradingV1OfflineHumanTagGoNoGoState.AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO_INPUT_INVALID


def test_prerequisites_incomplets():
    data = _input(prerequisites_complete=False)
    context = build_human_tag_go_no_go_context(data)
    result = evaluate_agicore_trading_v1_offline_human_tag_go_no_go(data)

    assert review_human_tag_prerequisites(context, data) is False
    assert AGIcoreTradingV1OfflineHumanTagGoNoGoRisk.HUMAN_TAG_PREREQUISITES_INCOMPLETE in result.risks
    assert result.decision is AGIcoreTradingV1OfflineHumanTagGoNoGoDecision.REQUIRE_HUMAN_TAG_PREREQUISITE_FIXES


def test_final_tag_review_non_approuvee():
    result = evaluate_agicore_trading_v1_offline_human_tag_go_no_go(_input(final_tag_review_approved=False))

    assert review_human_tag_final_tag_review(_input(final_tag_review_approved=False)) is False
    assert AGIcoreTradingV1OfflineHumanTagGoNoGoRisk.FINAL_TAG_REVIEW_NOT_APPROVED in result.risks
    assert result.decision is AGIcoreTradingV1OfflineHumanTagGoNoGoDecision.REQUIRE_HUMAN_TAG_PREREQUISITE_FIXES


def test_tag_creation_instructions_review_non_approuvee():
    result = evaluate_agicore_trading_v1_offline_human_tag_go_no_go(_input(tag_creation_instructions_review_approved=False))

    assert review_human_tag_creation_instructions_review(_input(tag_creation_instructions_review_approved=False)) is False
    assert AGIcoreTradingV1OfflineHumanTagGoNoGoRisk.TAG_CREATION_INSTRUCTIONS_REVIEW_NOT_APPROVED in result.risks
    assert result.decision is AGIcoreTradingV1OfflineHumanTagGoNoGoDecision.REQUIRE_HUMAN_TAG_PREREQUISITE_FIXES


def test_release_package_review_non_approuvee():
    result = evaluate_agicore_trading_v1_offline_human_tag_go_no_go(_input(release_package_review_approved=False))

    assert review_human_tag_release_package_review(_input(release_package_review_approved=False)) is False
    assert AGIcoreTradingV1OfflineHumanTagGoNoGoRisk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED in result.risks
    assert result.decision is AGIcoreTradingV1OfflineHumanTagGoNoGoDecision.REQUIRE_HUMAN_TAG_PREREQUISITE_FIXES


def test_final_readiness_review_non_approuvee():
    result = evaluate_agicore_trading_v1_offline_human_tag_go_no_go(_input(final_readiness_review_approved=False))

    assert review_human_tag_final_readiness_review(_input(final_readiness_review_approved=False)) is False
    assert AGIcoreTradingV1OfflineHumanTagGoNoGoRisk.FINAL_READINESS_REVIEW_NOT_APPROVED in result.risks
    assert result.decision is AGIcoreTradingV1OfflineHumanTagGoNoGoDecision.REQUIRE_HUMAN_TAG_PREREQUISITE_FIXES


def test_tag_name_invalide():
    result = evaluate_agicore_trading_v1_offline_human_tag_go_no_go(_input(tag_name="bad"))

    assert review_human_tag_name(_input(tag_name="bad")) is False
    assert AGIcoreTradingV1OfflineHumanTagGoNoGoRisk.HUMAN_TAG_NAME_INVALID in result.risks
    assert result.decision is AGIcoreTradingV1OfflineHumanTagGoNoGoDecision.REQUIRE_HUMAN_TAG_NAME_FIXES


def test_version_invalide():
    result = evaluate_agicore_trading_v1_offline_human_tag_go_no_go(_input(version="v1-live"))

    assert review_human_tag_version(_input(version="v1-live")) is False
    assert AGIcoreTradingV1OfflineHumanTagGoNoGoRisk.HUMAN_TAG_VERSION_INVALID in result.risks
    assert result.decision is AGIcoreTradingV1OfflineHumanTagGoNoGoDecision.REQUIRE_HUMAN_TAG_VERSION_FIXES


def test_guardrails_manquants():
    data = _input(guardrails_present=False)
    context = build_human_tag_go_no_go_context(data)
    result = evaluate_agicore_trading_v1_offline_human_tag_go_no_go(data)

    assert review_human_tag_guardrails(context) is False
    assert AGIcoreTradingV1OfflineHumanTagGoNoGoRisk.HUMAN_TAG_GUARDRAILS_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineHumanTagGoNoGoDecision.REQUIRE_HUMAN_TAG_GUARDRAIL_FIXES


def test_git_tag_already_created():
    result = evaluate_agicore_trading_v1_offline_human_tag_go_no_go(_input(git_tag_already_created=True))

    assert review_human_tag_no_git_tag_created(_input(git_tag_already_created=True)) is False
    assert AGIcoreTradingV1OfflineHumanTagGoNoGoRisk.GIT_TAG_ALREADY_CREATED in result.risks
    assert result.decision is AGIcoreTradingV1OfflineHumanTagGoNoGoDecision.REQUIRE_HUMAN_TAG_NO_OVERCLAIM_FIXES
    assert result.git_tag_created is False


def test_git_tag_already_pushed():
    result = evaluate_agicore_trading_v1_offline_human_tag_go_no_go(_input(git_tag_already_pushed=True))

    assert review_human_tag_no_git_tag_pushed(_input(git_tag_already_pushed=True)) is False
    assert AGIcoreTradingV1OfflineHumanTagGoNoGoRisk.GIT_TAG_ALREADY_PUSHED in result.risks
    assert result.decision is AGIcoreTradingV1OfflineHumanTagGoNoGoDecision.REQUIRE_HUMAN_TAG_NO_OVERCLAIM_FIXES
    assert result.git_tag_pushed is False


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("live_trading_overclaim", AGIcoreTradingV1OfflineHumanTagGoNoGoRisk.LIVE_TRADING_READINESS_OVERCLAIM),
        ("real_broker_overclaim", AGIcoreTradingV1OfflineHumanTagGoNoGoRisk.REAL_BROKER_READINESS_OVERCLAIM),
        ("real_order_overclaim", AGIcoreTradingV1OfflineHumanTagGoNoGoRisk.REAL_ORDER_EXECUTION_OVERCLAIM),
        ("paper_broker_overclaim", AGIcoreTradingV1OfflineHumanTagGoNoGoRisk.PAPER_BROKER_CONNECTION_OVERCLAIM),
        ("profitability_overclaim", AGIcoreTradingV1OfflineHumanTagGoNoGoRisk.PROFITABILITY_PROOF_OVERCLAIM),
        ("financial_advice_overclaim", AGIcoreTradingV1OfflineHumanTagGoNoGoRisk.FINANCIAL_ADVICE_OVERCLAIM),
    ),
)
def test_overclaims_are_blocked(field, risk):
    result = evaluate_agicore_trading_v1_offline_human_tag_go_no_go(_input(**{field: True}))

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineHumanTagGoNoGoDecision.REQUIRE_HUMAN_TAG_NO_OVERCLAIM_FIXES


def test_no_overclaim_helpers():
    assert review_human_tag_no_live_trading_claim(_input()) is True
    assert review_human_tag_no_live_trading_claim(_input(live_trading_overclaim=True)) is False
    assert review_human_tag_no_profitability_claim(_input()) is True
    assert review_human_tag_no_profitability_claim(_input(profitability_overclaim=True)) is False
    assert review_human_tag_no_financial_advice_claim(_input()) is True
    assert review_human_tag_no_financial_advice_claim(_input(financial_advice_overclaim=True)) is False


def test_human_go_decision_helper():
    assert review_human_tag_go_decision(_input()) is True
    assert review_human_tag_go_decision(_input(human_go_decision="NO_GO")) is False


def test_markdown_genere():
    data = _input()
    context = build_human_tag_go_no_go_context(data)
    result = evaluate_agicore_trading_v1_offline_human_tag_go_no_go(data)
    markdown = render_agicore_trading_v1_offline_human_tag_go_no_go_markdown(context, result.findings)

    assert "AGIcore Trading v1 Offline Human Tag Go/No-Go" in markdown
    assert "GO_FOR_MANUAL_TAG_CREATION_LATER" in markdown
    assert "ne jamais faire git add ." in markdown
    assert validate_human_tag_go_no_go_markdown(markdown)


def test_markdown_docs_valide():
    markdown = DOC_PATH.read_text(encoding="utf-8")

    assert validate_human_tag_go_no_go_markdown(markdown)
    assert "AGIcore Trading v1 Offline Manual Tag Creation Final Checklist" in markdown


def test_json_report():
    result = evaluate_agicore_trading_v1_offline_human_tag_go_no_go(_input())
    payload = json.loads(render_agicore_trading_v1_offline_human_tag_go_no_go_json_report(result))

    assert payload["schema"] == "agicore_trading_v1_offline_human_tag_go_no_go"
    assert payload["decision"] == "APPROVE_AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO"
    assert payload["state"] == "READY_FOR_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_FINAL_CHECKLIST"
    assert payload["score"] == 100
    assert payload["git_tag_created"] is False
    assert payload["git_tag_pushed"] is False
    assert payload["real_order_execution"] is False
    assert payload["paper_broker_connected"] is False


def test_score_risks_and_recommendations_directly():
    data = _input()
    context = build_human_tag_go_no_go_context(data)
    risks = detect_agicore_trading_v1_offline_human_tag_go_no_go_risks(data, context)
    score = compute_agicore_trading_v1_offline_human_tag_go_no_go_score(data, context, risks)
    recommendations = generate_agicore_trading_v1_offline_human_tag_go_no_go_recommendations(risks)

    assert risks == ()
    assert score.overall_score == 100
    assert recommendations == (
        AGIcoreTradingV1OfflineHumanTagGoNoGoRecommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_FINAL_CHECKLIST,
    )


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("file_read_requested", AGIcoreTradingV1OfflineHumanTagGoNoGoRisk.FILE_READ_BOUNDARY_VIOLATION),
        ("real_data_access_requested", AGIcoreTradingV1OfflineHumanTagGoNoGoRisk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_access_requested", AGIcoreTradingV1OfflineHumanTagGoNoGoRisk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("broker_connection_requested", AGIcoreTradingV1OfflineHumanTagGoNoGoRisk.REAL_BROKER_BOUNDARY_VIOLATION),
        ("secret_read_requested", AGIcoreTradingV1OfflineHumanTagGoNoGoRisk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("network_requested", AGIcoreTradingV1OfflineHumanTagGoNoGoRisk.NETWORK_BOUNDARY_VIOLATION),
        ("http_requested", AGIcoreTradingV1OfflineHumanTagGoNoGoRisk.NETWORK_BOUNDARY_VIOLATION),
        ("websocket_requested", AGIcoreTradingV1OfflineHumanTagGoNoGoRisk.NETWORK_BOUNDARY_VIOLATION),
        ("socket_requested", AGIcoreTradingV1OfflineHumanTagGoNoGoRisk.NETWORK_BOUNDARY_VIOLATION),
        ("external_api_requested", AGIcoreTradingV1OfflineHumanTagGoNoGoRisk.NETWORK_BOUNDARY_VIOLATION),
        ("order_execution_requested", AGIcoreTradingV1OfflineHumanTagGoNoGoRisk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ("account_access_requested", AGIcoreTradingV1OfflineHumanTagGoNoGoRisk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ("position_mutation_requested", AGIcoreTradingV1OfflineHumanTagGoNoGoRisk.POSITION_MUTATION_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations_are_blocked(field, risk):
    data = _input(**{field: True})
    result = evaluate_agicore_trading_v1_offline_human_tag_go_no_go(data)

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineHumanTagGoNoGoDecision.REQUIRE_HUMAN_TAG_NO_OVERCLAIM_FIXES
    assert assert_agicore_trading_v1_offline_human_tag_go_no_go_boundaries(data) is False


def test_no_git_tag_subprocess_or_shell_execution_in_module_source():
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden_imports = {"subprocess", "os"}
    forbidden_calls = {"system", "popen", "run", "call", "check_call", "check_output", "Popen"}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert not {alias.name.split(".")[0] for alias in node.names} & forbidden_imports
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in forbidden_imports
        if isinstance(node, ast.Call):
            func_name = getattr(node.func, "attr", getattr(node.func, "id", ""))
            assert func_name not in forbidden_calls


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


def test_no_secret_env_read_and_no_side_effects_reported():
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    result = evaluate_agicore_trading_v1_offline_human_tag_go_no_go(_input())

    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            assert node.attr not in {"environ", "getenv"}
        if isinstance(node, ast.Call):
            assert getattr(node.func, "attr", "") != "getenv"
    assert result.file_read is False
    assert result.data_accessed is False
    assert result.git_tag_created is False
    assert result.git_tag_pushed is False
    assert result.real_order_submitted is False
    assert result.real_account_accessed is False
    assert result.position_mutated is False
