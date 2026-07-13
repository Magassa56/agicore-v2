from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agicore.trading.agicore_trading_v1_offline_final_tag_creation_human_confirmation import (
    assert_agicore_trading_v1_offline_final_tag_creation_human_confirmation_boundaries,
    build_final_tag_creation_human_confirmation_context,
    compute_agicore_trading_v1_offline_final_tag_creation_human_confirmation_score,
    detect_agicore_trading_v1_offline_final_tag_creation_human_confirmation_risks,
    evaluate_agicore_trading_v1_offline_final_tag_creation_human_confirmation,
    generate_agicore_trading_v1_offline_final_tag_creation_human_confirmation_recommendations,
    render_agicore_trading_v1_offline_final_tag_creation_human_confirmation_json_report,
    render_agicore_trading_v1_offline_final_tag_creation_human_confirmation_markdown,
    review_final_tag_creation_human_confirmation_command_sheet_review,
    review_final_tag_creation_human_confirmation_conditions,
    review_final_tag_creation_human_confirmation_documented_commands_only,
    review_final_tag_creation_human_confirmation_final_authorization,
    review_final_tag_creation_human_confirmation_no_financial_advice_claim,
    review_final_tag_creation_human_confirmation_no_git_tag_created,
    review_final_tag_creation_human_confirmation_no_git_tag_pushed,
    review_final_tag_creation_human_confirmation_no_live_trading_claim,
    review_final_tag_creation_human_confirmation_no_profitability_claim,
    review_final_tag_creation_human_confirmation_prerequisites,
    review_final_tag_creation_human_confirmation_stop_rules,
    review_final_tag_creation_human_confirmation_tag_name,
    review_final_tag_creation_human_confirmation_version,
    validate_agicore_trading_v1_offline_final_tag_creation_human_confirmation_input,
    validate_final_tag_creation_human_confirmation_markdown,
)
from agicore.trading.agicore_trading_v1_offline_final_tag_creation_human_confirmation_models import (
    AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationCommand,
    AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationCondition,
    AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationContext,
    AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationDecision,
    AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationInput,
    AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationPrerequisite,
    AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRecommendation,
    AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationReport,
    AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationResult,
    AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk,
    AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationScore,
    AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationState,
    AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationStopRule,
    AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationTagMetadata,
)

ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/agicore_trading_v1_offline_final_tag_creation_human_confirmation.py"
DOC_PATH = ROOT / "docs/AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION.md"


def _input(**overrides):
    return AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationInput(**overrides)


def test_models_are_importable():
    assert AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationInput
    assert AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationResult
    assert AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationState
    assert AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationDecision
    assert AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk
    assert AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRecommendation
    assert AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationScore
    assert AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationContext
    assert AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationPrerequisite
    assert AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationCondition
    assert AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationCommand
    assert AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationStopRule
    assert AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationTagMetadata
    assert AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationReport


def test_nominal_final_tag_creation_human_confirmation():
    result = evaluate_agicore_trading_v1_offline_final_tag_creation_human_confirmation(_input())

    assert result.decision is AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationDecision.APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION
    assert result.state is AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationState.READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.git_tag_created is False
    assert result.git_tag_pushed is False
    assert result.context.human_confirmation == "HUMAN_CONFIRMATION_READY_FOR_MANUAL_TAG_CREATION_LATER"


def test_input_manquant():
    result = evaluate_agicore_trading_v1_offline_final_tag_creation_human_confirmation(None)

    assert validate_agicore_trading_v1_offline_final_tag_creation_human_confirmation_input(None) is False
    assert AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_INPUT_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationDecision.REQUIRE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_INPUT_FIXES
    assert result.state is AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationState.AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_INPUT_INVALID


def test_prerequisites_incomplets():
    data = _input(prerequisites_complete=False)
    context = build_final_tag_creation_human_confirmation_context(data)
    result = evaluate_agicore_trading_v1_offline_final_tag_creation_human_confirmation(data)

    assert review_final_tag_creation_human_confirmation_prerequisites(context, data) is False
    assert AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_PREREQUISITES_INCOMPLETE in result.risks


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("command_sheet_review_approved", AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_NOT_APPROVED),
        ("final_manual_tag_authorization_approved", AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.FINAL_MANUAL_TAG_AUTHORIZATION_NOT_APPROVED),
        ("execution_plan_review_approved", AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.TAG_CREATION_EXECUTION_PLAN_REVIEW_NOT_APPROVED),
        ("manual_tag_creation_approval_approved", AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED),
        ("human_tag_go_no_go_approved", AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.HUMAN_TAG_GO_NO_GO_NOT_APPROVED),
        ("release_package_review_approved", AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED),
        ("final_readiness_review_approved", AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.FINAL_READINESS_REVIEW_NOT_APPROVED),
    ),
)
def test_prerequisite_approval_missing(field, risk):
    result = evaluate_agicore_trading_v1_offline_final_tag_creation_human_confirmation(_input(**{field: False}))

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationDecision.REQUIRE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_PREREQUISITE_FIXES


def test_specific_prerequisite_helpers():
    assert review_final_tag_creation_human_confirmation_command_sheet_review(_input(command_sheet_review_approved=False)) is False
    assert review_final_tag_creation_human_confirmation_final_authorization(_input(final_manual_tag_authorization_approved=False)) is False


def test_tag_name_invalide():
    data = _input(tag_name="bad-tag")
    result = evaluate_agicore_trading_v1_offline_final_tag_creation_human_confirmation(data)

    assert review_final_tag_creation_human_confirmation_tag_name(data) is False
    assert AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_TAG_NAME_INVALID in result.risks


def test_version_invalide():
    data = _input(version="v1-live")
    result = evaluate_agicore_trading_v1_offline_final_tag_creation_human_confirmation(data)

    assert review_final_tag_creation_human_confirmation_version(data) is False
    assert AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_VERSION_INVALID in result.risks


def test_conditions_manquantes():
    data = _input(conditions_present=False)
    context = build_final_tag_creation_human_confirmation_context(data)
    result = evaluate_agicore_trading_v1_offline_final_tag_creation_human_confirmation(data)

    assert review_final_tag_creation_human_confirmation_conditions(context) is False
    assert AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_CONDITIONS_MISSING in result.risks


def test_commands_non_documentation_only():
    data = _input(commands_documentation_only=False)
    context = build_final_tag_creation_human_confirmation_context(data)
    result = evaluate_agicore_trading_v1_offline_final_tag_creation_human_confirmation(data)

    assert review_final_tag_creation_human_confirmation_documented_commands_only(context) is False
    assert AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_COMMANDS_NOT_DOCUMENTATION_ONLY in result.risks


def test_stop_rules_manquantes():
    data = _input(stop_rules_present=False)
    context = build_final_tag_creation_human_confirmation_context(data)
    result = evaluate_agicore_trading_v1_offline_final_tag_creation_human_confirmation(data)

    assert review_final_tag_creation_human_confirmation_stop_rules(context) is False
    assert AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_STOP_RULES_MISSING in result.risks


def test_git_tag_already_created_or_pushed():
    created = evaluate_agicore_trading_v1_offline_final_tag_creation_human_confirmation(_input(git_tag_already_created=True))
    pushed = evaluate_agicore_trading_v1_offline_final_tag_creation_human_confirmation(_input(git_tag_already_pushed=True))

    assert review_final_tag_creation_human_confirmation_no_git_tag_created(_input(git_tag_already_created=True)) is False
    assert review_final_tag_creation_human_confirmation_no_git_tag_pushed(_input(git_tag_already_pushed=True)) is False
    assert AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.GIT_TAG_ALREADY_CREATED in created.risks
    assert AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.GIT_TAG_ALREADY_PUSHED in pushed.risks
    assert created.git_tag_created is False
    assert pushed.git_tag_pushed is False


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("live_trading_overclaim", AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.LIVE_TRADING_READINESS_OVERCLAIM),
        ("real_broker_overclaim", AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.REAL_BROKER_READINESS_OVERCLAIM),
        ("real_order_overclaim", AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.REAL_ORDER_EXECUTION_OVERCLAIM),
        ("paper_broker_overclaim", AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.PAPER_BROKER_CONNECTION_OVERCLAIM),
        ("profitability_overclaim", AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.PROFITABILITY_PROOF_OVERCLAIM),
        ("financial_advice_overclaim", AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.FINANCIAL_ADVICE_OVERCLAIM),
    ),
)
def test_overclaims(field, risk):
    result = evaluate_agicore_trading_v1_offline_final_tag_creation_human_confirmation(_input(**{field: True}))

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationDecision.REQUIRE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_NO_OVERCLAIM_FIXES


def test_no_overclaim_helpers():
    assert review_final_tag_creation_human_confirmation_no_live_trading_claim(_input(live_trading_overclaim=True)) is False
    assert review_final_tag_creation_human_confirmation_no_profitability_claim(_input(profitability_overclaim=True)) is False
    assert review_final_tag_creation_human_confirmation_no_financial_advice_claim(_input(financial_advice_overclaim=True)) is False


def test_markdown_genere_et_docs_valide():
    result = evaluate_agicore_trading_v1_offline_final_tag_creation_human_confirmation(_input())
    markdown = render_agicore_trading_v1_offline_final_tag_creation_human_confirmation_markdown(result.context)

    assert validate_final_tag_creation_human_confirmation_markdown(markdown)
    assert validate_final_tag_creation_human_confirmation_markdown(DOC_PATH.read_text(encoding="utf-8"))


def test_json_report():
    result = evaluate_agicore_trading_v1_offline_final_tag_creation_human_confirmation(_input())
    payload = json.loads(render_agicore_trading_v1_offline_final_tag_creation_human_confirmation_json_report(result))

    assert payload["decision"] == "APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION"
    assert payload["state"] == "READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT"
    assert payload["score"] == 100
    assert payload["git_tag_created"] is False
    assert payload["git_tag_pushed"] is False


def test_score_risks_recommendations():
    data = _input()
    context = build_final_tag_creation_human_confirmation_context(data)
    risks = detect_agicore_trading_v1_offline_final_tag_creation_human_confirmation_risks(data, context)
    score = compute_agicore_trading_v1_offline_final_tag_creation_human_confirmation_score(data, context, risks)
    recommendations = generate_agicore_trading_v1_offline_final_tag_creation_human_confirmation_recommendations(risks)

    assert risks == ()
    assert score.overall_score == 100
    assert recommendations == (
        AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRecommendation.PREPARE_TAG_CREATION_FINAL_PREFLIGHT,
    )


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("file_read_requested", AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.FILE_READ_BOUNDARY_VIOLATION),
        ("real_data_access_requested", AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_access_requested", AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("broker_connection_requested", AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.REAL_BROKER_BOUNDARY_VIOLATION),
        ("secret_read_requested", AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("network_requested", AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.NETWORK_BOUNDARY_VIOLATION),
        ("http_requested", AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.NETWORK_BOUNDARY_VIOLATION),
        ("websocket_requested", AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.NETWORK_BOUNDARY_VIOLATION),
        ("socket_requested", AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.NETWORK_BOUNDARY_VIOLATION),
        ("external_api_requested", AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.NETWORK_BOUNDARY_VIOLATION),
        ("order_execution_requested", AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ("account_access_requested", AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ("position_mutation_requested", AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk.POSITION_MUTATION_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations(field, risk):
    data = _input(**{field: True})
    result = evaluate_agicore_trading_v1_offline_final_tag_creation_human_confirmation(data)

    assert assert_agicore_trading_v1_offline_final_tag_creation_human_confirmation_boundaries(data) is False
    assert risk in result.risks


def test_no_file_network_env_order_or_git_execution_calls():
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden_imports = {"pathlib", "os", "shutil", "socket", "requests", "httpx", "urllib", "websocket", "websockets", "subprocess"}
    forbidden_calls = {"open", "read_text", "write_text", "read_bytes", "write_bytes", "getenv", "environ"}
    imports = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    calls = {node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
    attr_calls = {node.func.attr for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)}
    result = evaluate_agicore_trading_v1_offline_final_tag_creation_human_confirmation(_input())

    assert forbidden_imports.isdisjoint(imports)
    assert forbidden_calls.isdisjoint(calls | attr_calls)
    assert "Popen" not in source
    assert result.real_order_submitted is False
    assert result.real_account_accessed is False
    assert result.position_mutated is False
    assert result.file_read is False
    assert result.data_accessed is False
