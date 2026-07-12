from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agicore.trading.agicore_trading_v1_offline_manual_tag_creation_command_sheet_review import (
    assert_agicore_trading_v1_offline_manual_tag_creation_command_sheet_review_boundaries,
    build_manual_tag_creation_command_sheet_review_context,
    compute_agicore_trading_v1_offline_manual_tag_creation_command_sheet_review_score,
    detect_agicore_trading_v1_offline_manual_tag_creation_command_sheet_review_risks,
    generate_agicore_trading_v1_offline_manual_tag_creation_command_sheet_review_recommendations,
    render_agicore_trading_v1_offline_manual_tag_creation_command_sheet_review_json_report,
    render_agicore_trading_v1_offline_manual_tag_creation_command_sheet_review_markdown,
    review_agicore_trading_v1_offline_manual_tag_creation_command_sheet,
    review_manual_tag_creation_command_sheet_approval,
    review_manual_tag_creation_command_sheet_review_documented_commands_only,
    review_manual_tag_creation_command_sheet_review_expected_results,
    review_manual_tag_creation_command_sheet_review_no_financial_advice_claim,
    review_manual_tag_creation_command_sheet_review_no_git_tag_created,
    review_manual_tag_creation_command_sheet_review_no_git_tag_pushed,
    review_manual_tag_creation_command_sheet_review_no_live_trading_claim,
    review_manual_tag_creation_command_sheet_review_no_profitability_claim,
    review_manual_tag_creation_command_sheet_review_post_tag_commands,
    review_manual_tag_creation_command_sheet_review_pre_tag_commands,
    review_manual_tag_creation_command_sheet_review_prerequisites,
    review_manual_tag_creation_command_sheet_review_stop_rules,
    review_manual_tag_creation_command_sheet_review_tag_creation_command,
    review_manual_tag_creation_command_sheet_review_tag_name,
    review_manual_tag_creation_command_sheet_review_tag_push_command,
    review_manual_tag_creation_command_sheet_review_version,
    validate_agicore_trading_v1_offline_manual_tag_creation_command_sheet_review_input,
    validate_manual_tag_creation_command_sheet_review_markdown,
)
from agicore.trading.agicore_trading_v1_offline_manual_tag_creation_command_sheet_review_models import (
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewCommand,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewContext,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewDecision,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewExpectedResult,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewInput,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewPrerequisite,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRecommendation,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewReport,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewResult,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewScore,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewState,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewStopRule,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewTagMetadata,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/agicore_trading_v1_offline_manual_tag_creation_command_sheet_review.py"
DOC_PATH = ROOT / "docs/AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW.md"


def _input(**overrides):
    return AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewInput(**overrides)


def test_models_are_importable():
    assert AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewInput
    assert AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewResult
    assert AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewState
    assert AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewDecision
    assert AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk
    assert AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRecommendation
    assert AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewScore
    assert AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewContext
    assert AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewPrerequisite
    assert AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewCommand
    assert AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewExpectedResult
    assert AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewStopRule
    assert AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewTagMetadata
    assert AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewReport


def test_nominal_command_sheet_review():
    result = review_agicore_trading_v1_offline_manual_tag_creation_command_sheet(_input())

    assert result.decision is AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewDecision.APPROVE_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW
    assert result.state is AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewState.READY_FOR_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.git_tag_created is False
    assert result.git_tag_pushed is False
    assert result.context.tag_metadata.tag_name == "agicore-trading-v1-offline"
    assert result.context.tag_metadata.version == "v1.0.0-offline"
    assert validate_manual_tag_creation_command_sheet_review_markdown(result.report.markdown)


def test_input_manquant():
    result = review_agicore_trading_v1_offline_manual_tag_creation_command_sheet(None)

    assert validate_agicore_trading_v1_offline_manual_tag_creation_command_sheet_review_input(None) is False
    assert AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_INPUT_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewDecision.REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_INPUT_FIXES
    assert result.state is AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewState.AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_INPUT_INVALID


def test_command_sheet_non_approuvee():
    data = _input(command_sheet_approved=False)
    result = review_agicore_trading_v1_offline_manual_tag_creation_command_sheet(data)

    assert review_manual_tag_creation_command_sheet_approval(data) is False
    assert AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.MANUAL_TAG_CREATION_COMMAND_SHEET_NOT_APPROVED in result.risks
    assert result.decision is AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewDecision.REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_PREREQUISITE_FIXES


def test_prerequisites_incomplets():
    data = _input(prerequisites_complete=False)
    context = build_manual_tag_creation_command_sheet_review_context(data)
    result = review_agicore_trading_v1_offline_manual_tag_creation_command_sheet(data)

    assert review_manual_tag_creation_command_sheet_review_prerequisites(context, data) is False
    assert AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_PREREQUISITES_INCOMPLETE in result.risks


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("final_manual_tag_authorization_approved", AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.FINAL_MANUAL_TAG_AUTHORIZATION_NOT_APPROVED),
        ("execution_plan_review_approved", AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.TAG_CREATION_EXECUTION_PLAN_REVIEW_NOT_APPROVED),
        ("manual_tag_creation_approval_approved", AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED),
        ("human_tag_go_no_go_approved", AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.HUMAN_TAG_GO_NO_GO_NOT_APPROVED),
        ("release_package_review_approved", AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED),
        ("final_readiness_review_approved", AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.FINAL_READINESS_REVIEW_NOT_APPROVED),
    ),
)
def test_prerequisite_approval_missing(field, risk):
    result = review_agicore_trading_v1_offline_manual_tag_creation_command_sheet(_input(**{field: False}))

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewDecision.REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_PREREQUISITE_FIXES


def test_tag_name_invalide():
    data = _input(tag_name="bad-tag")
    result = review_agicore_trading_v1_offline_manual_tag_creation_command_sheet(data)

    assert review_manual_tag_creation_command_sheet_review_tag_name(data) is False
    assert AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_TAG_NAME_INVALID in result.risks
    assert result.decision is AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewDecision.REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_TAG_NAME_FIXES


def test_version_invalide():
    data = _input(version="v1-live")
    result = review_agicore_trading_v1_offline_manual_tag_creation_command_sheet(data)

    assert review_manual_tag_creation_command_sheet_review_version(data) is False
    assert AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_VERSION_INVALID in result.risks
    assert result.decision is AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewDecision.REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_VERSION_FIXES


def test_pre_tag_commands_manquantes():
    data = _input(pre_tag_commands_present=False)
    context = build_manual_tag_creation_command_sheet_review_context(data)
    result = review_agicore_trading_v1_offline_manual_tag_creation_command_sheet(data)

    assert review_manual_tag_creation_command_sheet_review_pre_tag_commands(context) is False
    assert AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_PRE_TAG_COMMANDS_MISSING in result.risks


def test_expected_results_manquants():
    data = _input(expected_results_present=False)
    context = build_manual_tag_creation_command_sheet_review_context(data)
    result = review_agicore_trading_v1_offline_manual_tag_creation_command_sheet(data)

    assert review_manual_tag_creation_command_sheet_review_expected_results(context) is False
    assert AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_EXPECTED_RESULTS_MISSING in result.risks


def test_tag_commands_non_documentation_only():
    data = _input(tag_creation_command_documentation_only=False)
    context = build_manual_tag_creation_command_sheet_review_context(data)
    result = review_agicore_trading_v1_offline_manual_tag_creation_command_sheet(data)

    assert review_manual_tag_creation_command_sheet_review_tag_creation_command(context) is False
    assert AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_TAG_COMMANDS_NOT_DOCUMENTATION_ONLY in result.risks
    assert result.decision is AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewDecision.REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_TAG_COMMAND_FIXES


def test_push_command_non_documentation_only():
    data = _input(tag_push_command_documentation_only=False)
    context = build_manual_tag_creation_command_sheet_review_context(data)
    result = review_agicore_trading_v1_offline_manual_tag_creation_command_sheet(data)

    assert review_manual_tag_creation_command_sheet_review_tag_push_command(context) is False
    assert AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_TAG_COMMANDS_NOT_DOCUMENTATION_ONLY in result.risks


def test_post_tag_commands_manquantes():
    data = _input(post_tag_commands_present=False)
    context = build_manual_tag_creation_command_sheet_review_context(data)

    assert review_manual_tag_creation_command_sheet_review_post_tag_commands(context) is False


def test_documented_commands_only_false():
    data = _input(documented_commands_only=False)
    context = build_manual_tag_creation_command_sheet_review_context(data)

    assert review_manual_tag_creation_command_sheet_review_documented_commands_only(context) is False


def test_stop_rules_manquantes():
    data = _input(stop_rules_present=False)
    context = build_manual_tag_creation_command_sheet_review_context(data)
    result = review_agicore_trading_v1_offline_manual_tag_creation_command_sheet(data)

    assert review_manual_tag_creation_command_sheet_review_stop_rules(context) is False
    assert AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_STOP_RULES_MISSING in result.risks


def test_git_tag_already_created():
    data = _input(git_tag_already_created=True)
    result = review_agicore_trading_v1_offline_manual_tag_creation_command_sheet(data)

    assert review_manual_tag_creation_command_sheet_review_no_git_tag_created(data) is False
    assert AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.GIT_TAG_ALREADY_CREATED in result.risks
    assert result.git_tag_created is False


def test_git_tag_already_pushed():
    data = _input(git_tag_already_pushed=True)
    result = review_agicore_trading_v1_offline_manual_tag_creation_command_sheet(data)

    assert review_manual_tag_creation_command_sheet_review_no_git_tag_pushed(data) is False
    assert AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.GIT_TAG_ALREADY_PUSHED in result.risks
    assert result.git_tag_pushed is False


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("live_trading_overclaim", AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.LIVE_TRADING_READINESS_OVERCLAIM),
        ("real_broker_overclaim", AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.REAL_BROKER_READINESS_OVERCLAIM),
        ("real_order_overclaim", AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.REAL_ORDER_EXECUTION_OVERCLAIM),
        ("paper_broker_overclaim", AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.PAPER_BROKER_CONNECTION_OVERCLAIM),
        ("profitability_overclaim", AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.PROFITABILITY_PROOF_OVERCLAIM),
        ("financial_advice_overclaim", AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.FINANCIAL_ADVICE_OVERCLAIM),
    ),
)
def test_overclaims(field, risk):
    result = review_agicore_trading_v1_offline_manual_tag_creation_command_sheet(_input(**{field: True}))

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewDecision.REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_NO_OVERCLAIM_FIXES


def test_no_overclaim_helpers():
    assert review_manual_tag_creation_command_sheet_review_no_live_trading_claim(_input(live_trading_overclaim=True)) is False
    assert review_manual_tag_creation_command_sheet_review_no_profitability_claim(_input(profitability_overclaim=True)) is False
    assert review_manual_tag_creation_command_sheet_review_no_financial_advice_claim(_input(financial_advice_overclaim=True)) is False


def test_markdown_genere():
    result = review_agicore_trading_v1_offline_manual_tag_creation_command_sheet(_input())
    markdown = render_agicore_trading_v1_offline_manual_tag_creation_command_sheet_review_markdown(result.context)

    assert "AGIcore Trading v1 Offline Manual Tag Creation Command Sheet Review" in markdown
    assert "git tag -a agicore-trading-v1-offline" in markdown
    assert validate_manual_tag_creation_command_sheet_review_markdown(markdown)


def test_markdown_docs_valide():
    assert DOC_PATH.exists()
    markdown = DOC_PATH.read_text(encoding="utf-8")

    assert validate_manual_tag_creation_command_sheet_review_markdown(markdown)


def test_json_report():
    result = review_agicore_trading_v1_offline_manual_tag_creation_command_sheet(_input())
    report = render_agicore_trading_v1_offline_manual_tag_creation_command_sheet_review_json_report(result)
    payload = json.loads(report)

    assert payload["decision"] == "APPROVE_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW"
    assert payload["state"] == "READY_FOR_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION"
    assert payload["score"] == 100
    assert payload["git_tag_created"] is False
    assert payload["git_tag_pushed"] is False
    assert payload["commands_documented_only"] is True


def test_score_risks_recommendations():
    data = _input()
    context = build_manual_tag_creation_command_sheet_review_context(data)
    risks = detect_agicore_trading_v1_offline_manual_tag_creation_command_sheet_review_risks(data, context)
    score = compute_agicore_trading_v1_offline_manual_tag_creation_command_sheet_review_score(data, context, risks)
    recommendations = generate_agicore_trading_v1_offline_manual_tag_creation_command_sheet_review_recommendations(risks)

    assert risks == ()
    assert score.overall_score == 100
    assert recommendations == (
        AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRecommendation.PREPARE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION,
    )


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("file_read_requested", AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.FILE_READ_BOUNDARY_VIOLATION),
        ("real_data_access_requested", AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_access_requested", AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("broker_connection_requested", AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.REAL_BROKER_BOUNDARY_VIOLATION),
        ("secret_read_requested", AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("network_requested", AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("http_requested", AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("websocket_requested", AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("socket_requested", AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("external_api_requested", AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("order_execution_requested", AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ("account_access_requested", AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ("position_mutation_requested", AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk.POSITION_MUTATION_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations(field, risk):
    data = _input(**{field: True})
    result = review_agicore_trading_v1_offline_manual_tag_creation_command_sheet(data)

    assert assert_agicore_trading_v1_offline_manual_tag_creation_command_sheet_review_boundaries(data) is False
    assert risk in result.risks


def test_no_file_read_write_or_data_access():
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden_calls = {"open", "read_text", "write_text", "read_bytes", "write_bytes"}
    forbidden_imports = {"pathlib", "os", "shutil"}
    calls = {node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
    imports = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}

    assert forbidden_calls.isdisjoint(calls)
    assert forbidden_imports.isdisjoint(imports)


def test_no_network_http_websocket_socket_or_env_secret_access():
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden_imports = {"socket", "requests", "httpx", "urllib", "websocket", "websockets", "os"}
    forbidden_calls = {"getenv", "environ"}
    imports = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    calls = {node.func.attr for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)}

    assert forbidden_imports.isdisjoint(imports)
    assert forbidden_calls.isdisjoint(calls)


def test_no_order_account_or_position_side_effects():
    result = review_agicore_trading_v1_offline_manual_tag_creation_command_sheet(_input())

    assert result.real_order_submitted is False
    assert result.real_account_accessed is False
    assert result.position_mutated is False
    assert result.file_read is False
    assert result.data_accessed is False


def test_no_git_tag_or_push_execution_calls():
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden_imports = {"subprocess"}
    imports = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    calls = {node.func.attr for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)}

    assert forbidden_imports.isdisjoint(imports)
    assert "run" not in calls
    assert "Popen" not in source
