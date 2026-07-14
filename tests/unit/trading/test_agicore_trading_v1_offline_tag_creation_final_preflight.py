from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agicore.trading.agicore_trading_v1_offline_tag_creation_final_preflight import (
    assert_agicore_trading_v1_offline_tag_creation_final_preflight_boundaries,
    build_tag_creation_final_preflight_context,
    compute_agicore_trading_v1_offline_tag_creation_final_preflight_score,
    detect_agicore_trading_v1_offline_tag_creation_final_preflight_risks,
    evaluate_agicore_trading_v1_offline_tag_creation_final_preflight,
    generate_agicore_trading_v1_offline_tag_creation_final_preflight_recommendations,
    render_agicore_trading_v1_offline_tag_creation_final_preflight_json_report,
    render_agicore_trading_v1_offline_tag_creation_final_preflight_markdown,
    review_tag_creation_final_preflight_documented_commands_only,
    review_tag_creation_final_preflight_expected_results,
    review_tag_creation_final_preflight_human_confirmation,
    review_tag_creation_final_preflight_no_financial_advice_claim,
    review_tag_creation_final_preflight_no_git_tag_created,
    review_tag_creation_final_preflight_no_git_tag_pushed,
    review_tag_creation_final_preflight_no_live_trading_claim,
    review_tag_creation_final_preflight_no_profitability_claim,
    review_tag_creation_final_preflight_prerequisites,
    review_tag_creation_final_preflight_required_checks,
    review_tag_creation_final_preflight_stop_rules,
    review_tag_creation_final_preflight_tag_name,
    review_tag_creation_final_preflight_version,
    validate_agicore_trading_v1_offline_tag_creation_final_preflight_input,
    validate_tag_creation_final_preflight_markdown,
)
from agicore.trading.agicore_trading_v1_offline_tag_creation_final_preflight_models import (
    AGIcoreTradingV1OfflineTagCreationFinalPreflightCheck,
    AGIcoreTradingV1OfflineTagCreationFinalPreflightCommand,
    AGIcoreTradingV1OfflineTagCreationFinalPreflightContext,
    AGIcoreTradingV1OfflineTagCreationFinalPreflightDecision,
    AGIcoreTradingV1OfflineTagCreationFinalPreflightExpectedResult,
    AGIcoreTradingV1OfflineTagCreationFinalPreflightInput,
    AGIcoreTradingV1OfflineTagCreationFinalPreflightPrerequisite,
    AGIcoreTradingV1OfflineTagCreationFinalPreflightRecommendation,
    AGIcoreTradingV1OfflineTagCreationFinalPreflightReport,
    AGIcoreTradingV1OfflineTagCreationFinalPreflightResult,
    AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk,
    AGIcoreTradingV1OfflineTagCreationFinalPreflightScore,
    AGIcoreTradingV1OfflineTagCreationFinalPreflightState,
    AGIcoreTradingV1OfflineTagCreationFinalPreflightStopRule,
    AGIcoreTradingV1OfflineTagCreationFinalPreflightTagMetadata,
)

ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/agicore_trading_v1_offline_tag_creation_final_preflight.py"
DOC_PATH = ROOT / "docs/AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT.md"


def _input(**overrides):
    return AGIcoreTradingV1OfflineTagCreationFinalPreflightInput(**overrides)


def test_models_are_importable():
    assert AGIcoreTradingV1OfflineTagCreationFinalPreflightInput
    assert AGIcoreTradingV1OfflineTagCreationFinalPreflightResult
    assert AGIcoreTradingV1OfflineTagCreationFinalPreflightState
    assert AGIcoreTradingV1OfflineTagCreationFinalPreflightDecision
    assert AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk
    assert AGIcoreTradingV1OfflineTagCreationFinalPreflightRecommendation
    assert AGIcoreTradingV1OfflineTagCreationFinalPreflightScore
    assert AGIcoreTradingV1OfflineTagCreationFinalPreflightContext
    assert AGIcoreTradingV1OfflineTagCreationFinalPreflightPrerequisite
    assert AGIcoreTradingV1OfflineTagCreationFinalPreflightCheck
    assert AGIcoreTradingV1OfflineTagCreationFinalPreflightExpectedResult
    assert AGIcoreTradingV1OfflineTagCreationFinalPreflightCommand
    assert AGIcoreTradingV1OfflineTagCreationFinalPreflightStopRule
    assert AGIcoreTradingV1OfflineTagCreationFinalPreflightTagMetadata
    assert AGIcoreTradingV1OfflineTagCreationFinalPreflightReport


def test_nominal_final_preflight():
    result = evaluate_agicore_trading_v1_offline_tag_creation_final_preflight(_input())

    assert result.decision is AGIcoreTradingV1OfflineTagCreationFinalPreflightDecision.APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT
    assert result.state is AGIcoreTradingV1OfflineTagCreationFinalPreflightState.READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT_REVIEW
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.git_tag_created is False
    assert result.git_tag_pushed is False


def test_input_manquant():
    result = evaluate_agicore_trading_v1_offline_tag_creation_final_preflight(None)

    assert validate_agicore_trading_v1_offline_tag_creation_final_preflight_input(None) is False
    assert AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.TAG_CREATION_FINAL_PREFLIGHT_INPUT_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationFinalPreflightDecision.REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_INPUT_FIXES
    assert result.state is AGIcoreTradingV1OfflineTagCreationFinalPreflightState.AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT_INPUT_INVALID


def test_prerequisites_incomplets():
    data = _input(prerequisites_complete=False)
    context = build_tag_creation_final_preflight_context(data)
    result = evaluate_agicore_trading_v1_offline_tag_creation_final_preflight(data)

    assert review_tag_creation_final_preflight_prerequisites(context, data) is False
    assert AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.TAG_CREATION_FINAL_PREFLIGHT_PREREQUISITES_INCOMPLETE in result.risks


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("final_tag_creation_human_confirmation_approved", AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_NOT_APPROVED),
        ("command_sheet_review_approved", AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_NOT_APPROVED),
        ("final_manual_tag_authorization_approved", AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.FINAL_MANUAL_TAG_AUTHORIZATION_NOT_APPROVED),
        ("execution_plan_review_approved", AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.TAG_CREATION_EXECUTION_PLAN_REVIEW_NOT_APPROVED),
        ("manual_tag_creation_approval_approved", AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED),
        ("human_tag_go_no_go_approved", AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.HUMAN_TAG_GO_NO_GO_NOT_APPROVED),
        ("release_package_review_approved", AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED),
        ("final_readiness_review_approved", AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.FINAL_READINESS_REVIEW_NOT_APPROVED),
    ),
)
def test_prerequisite_approval_missing(field, risk):
    result = evaluate_agicore_trading_v1_offline_tag_creation_final_preflight(_input(**{field: False}))

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationFinalPreflightDecision.REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_PREREQUISITE_FIXES


def test_human_confirmation_missing():
    data = _input(human_confirmation_present=False)
    context = build_tag_creation_final_preflight_context(data)
    result = evaluate_agicore_trading_v1_offline_tag_creation_final_preflight(data)

    assert review_tag_creation_final_preflight_human_confirmation(context) is False
    assert AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.TAG_CREATION_FINAL_PREFLIGHT_HUMAN_CONFIRMATION_MISSING in result.risks


def test_tag_name_invalide():
    data = _input(tag_name="bad-tag")
    result = evaluate_agicore_trading_v1_offline_tag_creation_final_preflight(data)

    assert review_tag_creation_final_preflight_tag_name(data) is False
    assert AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.TAG_CREATION_FINAL_PREFLIGHT_TAG_NAME_INVALID in result.risks


def test_version_invalide():
    data = _input(version="v1-live")
    result = evaluate_agicore_trading_v1_offline_tag_creation_final_preflight(data)

    assert review_tag_creation_final_preflight_version(data) is False
    assert AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.TAG_CREATION_FINAL_PREFLIGHT_VERSION_INVALID in result.risks


def test_checks_expected_commands_stop_rules_missing():
    data = _input(required_checks_present=False, expected_results_present=False, commands_documentation_only=False, stop_rules_present=False)
    context = build_tag_creation_final_preflight_context(data)
    result = evaluate_agicore_trading_v1_offline_tag_creation_final_preflight(data)

    assert review_tag_creation_final_preflight_required_checks(context) is False
    assert review_tag_creation_final_preflight_expected_results(context) is False
    assert review_tag_creation_final_preflight_documented_commands_only(context) is False
    assert review_tag_creation_final_preflight_stop_rules(context) is False
    assert AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.TAG_CREATION_FINAL_PREFLIGHT_CHECKS_MISSING in result.risks
    assert AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.TAG_CREATION_FINAL_PREFLIGHT_EXPECTED_RESULTS_MISSING in result.risks
    assert AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.TAG_CREATION_FINAL_PREFLIGHT_COMMANDS_NOT_DOCUMENTATION_ONLY in result.risks
    assert AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.TAG_CREATION_FINAL_PREFLIGHT_STOP_RULES_MISSING in result.risks


def test_git_tag_already_created_or_pushed():
    created = evaluate_agicore_trading_v1_offline_tag_creation_final_preflight(_input(git_tag_already_created=True))
    pushed = evaluate_agicore_trading_v1_offline_tag_creation_final_preflight(_input(git_tag_already_pushed=True))

    assert review_tag_creation_final_preflight_no_git_tag_created(_input(git_tag_already_created=True)) is False
    assert review_tag_creation_final_preflight_no_git_tag_pushed(_input(git_tag_already_pushed=True)) is False
    assert AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.GIT_TAG_ALREADY_CREATED in created.risks
    assert AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.GIT_TAG_ALREADY_PUSHED in pushed.risks
    assert created.git_tag_created is False
    assert pushed.git_tag_pushed is False


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("live_trading_overclaim", AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.LIVE_TRADING_READINESS_OVERCLAIM),
        ("real_broker_overclaim", AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.REAL_BROKER_READINESS_OVERCLAIM),
        ("real_order_overclaim", AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.REAL_ORDER_EXECUTION_OVERCLAIM),
        ("paper_broker_overclaim", AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.PAPER_BROKER_CONNECTION_OVERCLAIM),
        ("profitability_overclaim", AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.PROFITABILITY_PROOF_OVERCLAIM),
        ("financial_advice_overclaim", AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.FINANCIAL_ADVICE_OVERCLAIM),
    ),
)
def test_overclaims(field, risk):
    result = evaluate_agicore_trading_v1_offline_tag_creation_final_preflight(_input(**{field: True}))

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationFinalPreflightDecision.REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_NO_OVERCLAIM_FIXES


def test_no_overclaim_helpers():
    assert review_tag_creation_final_preflight_no_live_trading_claim(_input(live_trading_overclaim=True)) is False
    assert review_tag_creation_final_preflight_no_profitability_claim(_input(profitability_overclaim=True)) is False
    assert review_tag_creation_final_preflight_no_financial_advice_claim(_input(financial_advice_overclaim=True)) is False


def test_markdown_genere_et_docs_valide():
    result = evaluate_agicore_trading_v1_offline_tag_creation_final_preflight(_input())
    markdown = render_agicore_trading_v1_offline_tag_creation_final_preflight_markdown(result.context)

    assert validate_tag_creation_final_preflight_markdown(markdown)
    assert validate_tag_creation_final_preflight_markdown(DOC_PATH.read_text(encoding="utf-8"))


def test_json_report():
    result = evaluate_agicore_trading_v1_offline_tag_creation_final_preflight(_input())
    payload = json.loads(render_agicore_trading_v1_offline_tag_creation_final_preflight_json_report(result))

    assert payload["decision"] == "APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT"
    assert payload["state"] == "READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT_REVIEW"
    assert payload["score"] == 100
    assert payload["git_tag_created"] is False
    assert payload["git_tag_pushed"] is False


def test_score_risks_recommendations():
    data = _input()
    context = build_tag_creation_final_preflight_context(data)
    risks = detect_agicore_trading_v1_offline_tag_creation_final_preflight_risks(data, context)
    score = compute_agicore_trading_v1_offline_tag_creation_final_preflight_score(data, context, risks)
    recommendations = generate_agicore_trading_v1_offline_tag_creation_final_preflight_recommendations(risks)

    assert risks == ()
    assert score.overall_score == 100
    assert recommendations == (AGIcoreTradingV1OfflineTagCreationFinalPreflightRecommendation.PREPARE_FINAL_PREFLIGHT_REVIEW,)


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("file_read_requested", AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.FILE_READ_BOUNDARY_VIOLATION),
        ("real_data_access_requested", AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_access_requested", AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("broker_connection_requested", AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.REAL_BROKER_BOUNDARY_VIOLATION),
        ("secret_read_requested", AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("network_requested", AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.NETWORK_BOUNDARY_VIOLATION),
        ("http_requested", AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.NETWORK_BOUNDARY_VIOLATION),
        ("websocket_requested", AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.NETWORK_BOUNDARY_VIOLATION),
        ("socket_requested", AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.NETWORK_BOUNDARY_VIOLATION),
        ("external_api_requested", AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.NETWORK_BOUNDARY_VIOLATION),
        ("order_execution_requested", AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ("account_access_requested", AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ("position_mutation_requested", AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk.POSITION_MUTATION_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations(field, risk):
    data = _input(**{field: True})
    result = evaluate_agicore_trading_v1_offline_tag_creation_final_preflight(data)

    assert assert_agicore_trading_v1_offline_tag_creation_final_preflight_boundaries(data) is False
    assert risk in result.risks


def test_no_file_network_env_order_or_git_execution_calls():
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden_imports = {"pathlib", "os", "shutil", "socket", "requests", "httpx", "urllib", "websocket", "websockets", "subprocess"}
    forbidden_calls = {"open", "read_text", "write_text", "read_bytes", "write_bytes", "getenv", "environ"}
    imports = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    calls = {node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
    attr_calls = {node.func.attr for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)}
    result = evaluate_agicore_trading_v1_offline_tag_creation_final_preflight(_input())

    assert forbidden_imports.isdisjoint(imports)
    assert forbidden_calls.isdisjoint(calls | attr_calls)
    assert "Popen" not in source
    assert result.real_order_submitted is False
    assert result.real_account_accessed is False
    assert result.position_mutated is False
    assert result.file_read is False
    assert result.data_accessed is False
