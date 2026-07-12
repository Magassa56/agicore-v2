from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agicore.trading.agicore_trading_v1_offline_final_manual_tag_authorization import (
    assert_agicore_trading_v1_offline_final_manual_tag_authorization_boundaries,
    build_final_manual_tag_authorization_context,
    compute_agicore_trading_v1_offline_final_manual_tag_authorization_score,
    detect_agicore_trading_v1_offline_final_manual_tag_authorization_risks,
    evaluate_agicore_trading_v1_offline_final_manual_tag_authorization,
    generate_agicore_trading_v1_offline_final_manual_tag_authorization_recommendations,
    render_agicore_trading_v1_offline_final_manual_tag_authorization_json_report,
    render_agicore_trading_v1_offline_final_manual_tag_authorization_markdown,
    review_final_manual_tag_authorization_conditions,
    review_final_manual_tag_authorization_documented_commands_only,
    review_final_manual_tag_authorization_execution_plan_review,
    review_final_manual_tag_authorization_final_checklist,
    review_final_manual_tag_authorization_human_go_no_go,
    review_final_manual_tag_authorization_manual_approval,
    review_final_manual_tag_authorization_no_financial_advice_claim,
    review_final_manual_tag_authorization_no_git_tag_created,
    review_final_manual_tag_authorization_no_git_tag_pushed,
    review_final_manual_tag_authorization_no_live_trading_claim,
    review_final_manual_tag_authorization_no_profitability_claim,
    review_final_manual_tag_authorization_prerequisites,
    review_final_manual_tag_authorization_stop_rules,
    review_final_manual_tag_authorization_tag_name,
    review_final_manual_tag_authorization_version,
    validate_agicore_trading_v1_offline_final_manual_tag_authorization_input,
    validate_final_manual_tag_authorization_markdown,
)
from agicore.trading.agicore_trading_v1_offline_final_manual_tag_authorization_models import (
    AGIcoreTradingV1OfflineFinalManualTagAuthorizationCommand,
    AGIcoreTradingV1OfflineFinalManualTagAuthorizationCondition,
    AGIcoreTradingV1OfflineFinalManualTagAuthorizationContext,
    AGIcoreTradingV1OfflineFinalManualTagAuthorizationDecision,
    AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput,
    AGIcoreTradingV1OfflineFinalManualTagAuthorizationPrerequisite,
    AGIcoreTradingV1OfflineFinalManualTagAuthorizationRecommendation,
    AGIcoreTradingV1OfflineFinalManualTagAuthorizationReport,
    AGIcoreTradingV1OfflineFinalManualTagAuthorizationResult,
    AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk,
    AGIcoreTradingV1OfflineFinalManualTagAuthorizationScore,
    AGIcoreTradingV1OfflineFinalManualTagAuthorizationState,
    AGIcoreTradingV1OfflineFinalManualTagAuthorizationStopRule,
    AGIcoreTradingV1OfflineFinalManualTagAuthorizationTagMetadata,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/agicore_trading_v1_offline_final_manual_tag_authorization.py"
DOC_PATH = ROOT / "docs/AGICORE_TRADING_V1_OFFLINE_FINAL_MANUAL_TAG_AUTHORIZATION.md"


def _input(**overrides):
    payload = {}
    payload.update(overrides)
    return AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput(**payload)


def test_models_are_importable():
    assert AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput
    assert AGIcoreTradingV1OfflineFinalManualTagAuthorizationResult
    assert AGIcoreTradingV1OfflineFinalManualTagAuthorizationState
    assert AGIcoreTradingV1OfflineFinalManualTagAuthorizationDecision
    assert AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk
    assert AGIcoreTradingV1OfflineFinalManualTagAuthorizationRecommendation
    assert AGIcoreTradingV1OfflineFinalManualTagAuthorizationScore
    assert AGIcoreTradingV1OfflineFinalManualTagAuthorizationContext
    assert AGIcoreTradingV1OfflineFinalManualTagAuthorizationPrerequisite
    assert AGIcoreTradingV1OfflineFinalManualTagAuthorizationCondition
    assert AGIcoreTradingV1OfflineFinalManualTagAuthorizationCommand
    assert AGIcoreTradingV1OfflineFinalManualTagAuthorizationStopRule
    assert AGIcoreTradingV1OfflineFinalManualTagAuthorizationTagMetadata
    assert AGIcoreTradingV1OfflineFinalManualTagAuthorizationReport


def test_nominal_final_manual_tag_authorization():
    result = evaluate_agicore_trading_v1_offline_final_manual_tag_authorization(_input())

    assert result.decision is AGIcoreTradingV1OfflineFinalManualTagAuthorizationDecision.APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_MANUAL_TAG_AUTHORIZATION
    assert result.state is AGIcoreTradingV1OfflineFinalManualTagAuthorizationState.READY_FOR_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.git_tag_created is False
    assert result.git_tag_pushed is False
    assert result.context.tag_metadata.tag_name == "agicore-trading-v1-offline"
    assert result.context.tag_metadata.version == "v1.0.0-offline"
    assert validate_final_manual_tag_authorization_markdown(result.report.markdown)


def test_input_manquant():
    result = evaluate_agicore_trading_v1_offline_final_manual_tag_authorization(None)

    assert validate_agicore_trading_v1_offline_final_manual_tag_authorization_input(None) is False
    assert AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.FINAL_MANUAL_TAG_AUTHORIZATION_INPUT_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalManualTagAuthorizationDecision.REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_INPUT_FIXES
    assert result.state is AGIcoreTradingV1OfflineFinalManualTagAuthorizationState.AGICORE_TRADING_V1_OFFLINE_FINAL_MANUAL_TAG_AUTHORIZATION_INPUT_INVALID


def test_prerequisites_incomplets():
    data = _input(prerequisites_complete=False)
    context = build_final_manual_tag_authorization_context(data)
    result = evaluate_agicore_trading_v1_offline_final_manual_tag_authorization(data)

    assert review_final_manual_tag_authorization_prerequisites(context, data) is False
    assert AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.FINAL_MANUAL_TAG_AUTHORIZATION_PREREQUISITES_INCOMPLETE in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalManualTagAuthorizationDecision.REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_PREREQUISITE_FIXES


def test_execution_plan_review_non_approuvee():
    data = _input(execution_plan_review_approved=False)
    result = evaluate_agicore_trading_v1_offline_final_manual_tag_authorization(data)

    assert review_final_manual_tag_authorization_execution_plan_review(data) is False
    assert AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.TAG_CREATION_EXECUTION_PLAN_REVIEW_NOT_APPROVED in result.risks


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("execution_plan_approved", AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.TAG_CREATION_EXECUTION_PLAN_NOT_APPROVED),
        ("manual_tag_creation_approval_approved", AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED),
        ("manual_tag_creation_final_checklist_approved", AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.MANUAL_TAG_CREATION_FINAL_CHECKLIST_NOT_APPROVED),
        ("human_tag_go_no_go_approved", AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.HUMAN_TAG_GO_NO_GO_NOT_APPROVED),
        ("tag_creation_instructions_review_approved", AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.TAG_CREATION_INSTRUCTIONS_REVIEW_NOT_APPROVED),
        ("final_tag_review_approved", AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.FINAL_TAG_REVIEW_NOT_APPROVED),
        ("release_package_review_approved", AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED),
        ("final_readiness_review_approved", AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.FINAL_READINESS_REVIEW_NOT_APPROVED),
    ),
)
def test_prerequisite_approval_missing(field, risk):
    result = evaluate_agicore_trading_v1_offline_final_manual_tag_authorization(_input(**{field: False}))

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalManualTagAuthorizationDecision.REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_PREREQUISITE_FIXES


def test_required_prerequisite_helpers():
    assert review_final_manual_tag_authorization_manual_approval(_input(manual_tag_creation_approval_approved=False)) is False
    assert review_final_manual_tag_authorization_final_checklist(_input(manual_tag_creation_final_checklist_approved=False)) is False
    assert review_final_manual_tag_authorization_human_go_no_go(_input(human_tag_go_no_go_approved=False)) is False


def test_tag_name_invalide():
    data = _input(tag_name="bad-tag")
    result = evaluate_agicore_trading_v1_offline_final_manual_tag_authorization(data)

    assert review_final_manual_tag_authorization_tag_name(data) is False
    assert AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.FINAL_MANUAL_TAG_AUTHORIZATION_TAG_NAME_INVALID in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalManualTagAuthorizationDecision.REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_TAG_NAME_FIXES


def test_version_invalide():
    data = _input(version="v1-live")
    result = evaluate_agicore_trading_v1_offline_final_manual_tag_authorization(data)

    assert review_final_manual_tag_authorization_version(data) is False
    assert AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.FINAL_MANUAL_TAG_AUTHORIZATION_VERSION_INVALID in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalManualTagAuthorizationDecision.REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_VERSION_FIXES


def test_conditions_manquantes():
    data = _input(conditions_present=False)
    context = build_final_manual_tag_authorization_context(data)
    result = evaluate_agicore_trading_v1_offline_final_manual_tag_authorization(data)

    assert review_final_manual_tag_authorization_conditions(context) is False
    assert AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.FINAL_MANUAL_TAG_AUTHORIZATION_CONDITIONS_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalManualTagAuthorizationDecision.REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_CONDITION_FIXES


def test_commands_non_documentation_only():
    data = _input(commands_documentation_only=False)
    context = build_final_manual_tag_authorization_context(data)
    result = evaluate_agicore_trading_v1_offline_final_manual_tag_authorization(data)

    assert review_final_manual_tag_authorization_documented_commands_only(context) is False
    assert AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.FINAL_MANUAL_TAG_AUTHORIZATION_COMMANDS_NOT_DOCUMENTATION_ONLY in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalManualTagAuthorizationDecision.REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_COMMAND_DOCUMENTATION_FIXES


def test_stop_rules_manquantes():
    data = _input(stop_rules_present=False)
    context = build_final_manual_tag_authorization_context(data)
    result = evaluate_agicore_trading_v1_offline_final_manual_tag_authorization(data)

    assert review_final_manual_tag_authorization_stop_rules(context) is False
    assert AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.FINAL_MANUAL_TAG_AUTHORIZATION_STOP_RULES_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalManualTagAuthorizationDecision.REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_STOP_RULE_FIXES


def test_git_tag_already_created():
    data = _input(git_tag_already_created=True)
    result = evaluate_agicore_trading_v1_offline_final_manual_tag_authorization(data)

    assert review_final_manual_tag_authorization_no_git_tag_created(data) is False
    assert AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.GIT_TAG_ALREADY_CREATED in result.risks
    assert result.git_tag_created is False


def test_git_tag_already_pushed():
    data = _input(git_tag_already_pushed=True)
    result = evaluate_agicore_trading_v1_offline_final_manual_tag_authorization(data)

    assert review_final_manual_tag_authorization_no_git_tag_pushed(data) is False
    assert AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.GIT_TAG_ALREADY_PUSHED in result.risks
    assert result.git_tag_pushed is False


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("live_trading_overclaim", AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.LIVE_TRADING_READINESS_OVERCLAIM),
        ("real_broker_overclaim", AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.REAL_BROKER_READINESS_OVERCLAIM),
        ("real_order_overclaim", AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.REAL_ORDER_EXECUTION_OVERCLAIM),
        ("paper_broker_overclaim", AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.PAPER_BROKER_CONNECTION_OVERCLAIM),
        ("profitability_overclaim", AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.PROFITABILITY_PROOF_OVERCLAIM),
        ("financial_advice_overclaim", AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.FINANCIAL_ADVICE_OVERCLAIM),
    ),
)
def test_overclaims(field, risk):
    result = evaluate_agicore_trading_v1_offline_final_manual_tag_authorization(_input(**{field: True}))

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalManualTagAuthorizationDecision.REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_NO_OVERCLAIM_FIXES


def test_no_overclaim_helpers():
    assert review_final_manual_tag_authorization_no_live_trading_claim(_input(live_trading_overclaim=True)) is False
    assert review_final_manual_tag_authorization_no_profitability_claim(_input(profitability_overclaim=True)) is False
    assert review_final_manual_tag_authorization_no_financial_advice_claim(_input(financial_advice_overclaim=True)) is False


def test_markdown_genere():
    result = evaluate_agicore_trading_v1_offline_final_manual_tag_authorization(_input())
    markdown = render_agicore_trading_v1_offline_final_manual_tag_authorization_markdown(result.context)

    assert "AGIcore Trading v1 Offline Final Manual Tag Authorization" in markdown
    assert "git tag -a agicore-trading-v1-offline" in markdown
    assert validate_final_manual_tag_authorization_markdown(markdown)


def test_markdown_docs_valide():
    assert DOC_PATH.exists()
    markdown = DOC_PATH.read_text(encoding="utf-8")

    assert validate_final_manual_tag_authorization_markdown(markdown)


def test_json_report():
    result = evaluate_agicore_trading_v1_offline_final_manual_tag_authorization(_input())
    report = render_agicore_trading_v1_offline_final_manual_tag_authorization_json_report(result)
    payload = json.loads(report)

    assert payload["decision"] == "APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_MANUAL_TAG_AUTHORIZATION"
    assert payload["state"] == "READY_FOR_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET"
    assert payload["score"] == 100
    assert payload["git_tag_created"] is False
    assert payload["git_tag_pushed"] is False


def test_score_risks_recommendations():
    data = _input()
    context = build_final_manual_tag_authorization_context(data)
    risks = detect_agicore_trading_v1_offline_final_manual_tag_authorization_risks(data, context)
    score = compute_agicore_trading_v1_offline_final_manual_tag_authorization_score(data, context, risks)
    recommendations = generate_agicore_trading_v1_offline_final_manual_tag_authorization_recommendations(risks)

    assert risks == ()
    assert score.overall_score == 100
    assert recommendations == (
        AGIcoreTradingV1OfflineFinalManualTagAuthorizationRecommendation.PREPARE_MANUAL_TAG_CREATION_COMMAND_SHEET,
    )


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("file_read_requested", AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.FILE_READ_BOUNDARY_VIOLATION),
        ("real_data_access_requested", AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_access_requested", AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("broker_connection_requested", AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.REAL_BROKER_BOUNDARY_VIOLATION),
        ("secret_read_requested", AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("network_requested", AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.NETWORK_BOUNDARY_VIOLATION),
        ("http_requested", AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.NETWORK_BOUNDARY_VIOLATION),
        ("websocket_requested", AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.NETWORK_BOUNDARY_VIOLATION),
        ("socket_requested", AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.NETWORK_BOUNDARY_VIOLATION),
        ("external_api_requested", AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.NETWORK_BOUNDARY_VIOLATION),
        ("order_execution_requested", AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ("account_access_requested", AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ("position_mutation_requested", AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk.POSITION_MUTATION_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations(field, risk):
    data = _input(**{field: True})
    result = evaluate_agicore_trading_v1_offline_final_manual_tag_authorization(data)

    assert assert_agicore_trading_v1_offline_final_manual_tag_authorization_boundaries(data) is False
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
    result = evaluate_agicore_trading_v1_offline_final_manual_tag_authorization(_input())

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
