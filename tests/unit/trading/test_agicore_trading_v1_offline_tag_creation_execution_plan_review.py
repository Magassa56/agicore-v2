from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agicore.trading.agicore_trading_v1_offline_tag_creation_execution_plan_review import (
    assert_agicore_trading_v1_offline_tag_creation_execution_plan_review_boundaries,
    build_tag_creation_execution_plan_review_context,
    compute_agicore_trading_v1_offline_tag_creation_execution_plan_review_score,
    detect_agicore_trading_v1_offline_tag_creation_execution_plan_review_risks,
    generate_agicore_trading_v1_offline_tag_creation_execution_plan_review_recommendations,
    render_agicore_trading_v1_offline_tag_creation_execution_plan_review_json_report,
    render_agicore_trading_v1_offline_tag_creation_execution_plan_review_markdown,
    review_agicore_trading_v1_offline_tag_creation_execution_plan,
    review_tag_creation_execution_plan_approval,
    review_tag_creation_execution_plan_review_commands_documented_only,
    review_tag_creation_execution_plan_review_local_checks,
    review_tag_creation_execution_plan_review_no_financial_advice_claim,
    review_tag_creation_execution_plan_review_no_git_tag_created,
    review_tag_creation_execution_plan_review_no_git_tag_pushed,
    review_tag_creation_execution_plan_review_no_live_trading_claim,
    review_tag_creation_execution_plan_review_no_profitability_claim,
    review_tag_creation_execution_plan_review_prerequisites,
    review_tag_creation_execution_plan_review_remote_checks,
    review_tag_creation_execution_plan_review_steps,
    review_tag_creation_execution_plan_review_stop_rules,
    review_tag_creation_execution_plan_review_tag_name,
    review_tag_creation_execution_plan_review_version,
    validate_agicore_trading_v1_offline_tag_creation_execution_plan_review_input,
    validate_tag_creation_execution_plan_review_markdown,
)
from agicore.trading.agicore_trading_v1_offline_tag_creation_execution_plan_review_models import (
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewCommand,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewContext,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewCriterion,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewDecision,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewFinding,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewInput,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewPrerequisite,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRecommendation,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewReport,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewResult,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewScore,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewState,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewStopRule,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewTagMetadata,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/agicore_trading_v1_offline_tag_creation_execution_plan_review.py"
DOC_PATH = ROOT / "docs/AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_REVIEW.md"


def _input(**overrides):
    payload = {}
    payload.update(overrides)
    return AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewInput(**payload)


def test_models_are_importable():
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewInput
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewResult
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewState
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewDecision
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRecommendation
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewScore
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewContext
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewPrerequisite
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewCriterion
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewFinding
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewCommand
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewStopRule
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewTagMetadata
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewReport


def test_nominal_tag_creation_execution_plan_review():
    result = review_agicore_trading_v1_offline_tag_creation_execution_plan(_input())

    assert result.decision is AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewDecision.APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_REVIEW
    assert result.state is AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewState.READY_FOR_AGICORE_TRADING_V1_OFFLINE_FINAL_MANUAL_TAG_AUTHORIZATION
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.git_tag_created is False
    assert result.git_tag_pushed is False
    assert result.context.tag_metadata.tag_name == "agicore-trading-v1-offline"
    assert result.context.tag_metadata.version == "v1.0.0-offline"
    assert validate_tag_creation_execution_plan_review_markdown(result.report.markdown)


def test_input_manquant():
    result = review_agicore_trading_v1_offline_tag_creation_execution_plan(None)

    assert validate_agicore_trading_v1_offline_tag_creation_execution_plan_review_input(None) is False
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.TAG_CREATION_EXECUTION_PLAN_REVIEW_INPUT_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewDecision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_REVIEW_INPUT_FIXES
    assert result.state is AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewState.AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_REVIEW_INPUT_INVALID


def test_execution_plan_non_approuve():
    result = review_agicore_trading_v1_offline_tag_creation_execution_plan(_input(execution_plan_approved=False))

    assert review_tag_creation_execution_plan_approval(_input(execution_plan_approved=False)) is False
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.TAG_CREATION_EXECUTION_PLAN_NOT_APPROVED in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewDecision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_REVIEW_PREREQUISITE_FIXES


def test_prerequisites_incomplets():
    data = _input(prerequisites_complete=False)
    context = build_tag_creation_execution_plan_review_context(data)
    result = review_agicore_trading_v1_offline_tag_creation_execution_plan(data)

    assert review_tag_creation_execution_plan_review_prerequisites(context, data) is False
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.TAG_CREATION_EXECUTION_PLAN_REVIEW_PREREQUISITES_INCOMPLETE in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewDecision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_REVIEW_PREREQUISITE_FIXES


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("manual_tag_creation_approval_approved", AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED),
        ("manual_tag_creation_final_checklist_approved", AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.MANUAL_TAG_CREATION_FINAL_CHECKLIST_NOT_APPROVED),
        ("human_tag_go_no_go_approved", AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.HUMAN_TAG_GO_NO_GO_NOT_APPROVED),
        ("tag_creation_instructions_review_approved", AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.TAG_CREATION_INSTRUCTIONS_REVIEW_NOT_APPROVED),
        ("final_tag_review_approved", AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.FINAL_TAG_REVIEW_NOT_APPROVED),
        ("release_package_review_approved", AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED),
        ("final_readiness_review_approved", AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.FINAL_READINESS_REVIEW_NOT_APPROVED),
    ),
)
def test_prerequisite_approval_missing(field, risk):
    result = review_agicore_trading_v1_offline_tag_creation_execution_plan(_input(**{field: False}))

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewDecision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_REVIEW_PREREQUISITE_FIXES


def test_tag_name_invalide():
    data = _input(tag_name="bad-tag")
    result = review_agicore_trading_v1_offline_tag_creation_execution_plan(data)

    assert review_tag_creation_execution_plan_review_tag_name(data) is False
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.TAG_CREATION_EXECUTION_PLAN_REVIEW_TAG_NAME_INVALID in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewDecision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_REVIEW_TAG_NAME_FIXES


def test_version_invalide():
    data = _input(version="v1-live")
    result = review_agicore_trading_v1_offline_tag_creation_execution_plan(data)

    assert review_tag_creation_execution_plan_review_version(data) is False
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.TAG_CREATION_EXECUTION_PLAN_REVIEW_VERSION_INVALID in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewDecision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_REVIEW_VERSION_FIXES


def test_steps_manquantes():
    data = _input(steps_present=False)
    context = build_tag_creation_execution_plan_review_context(data)
    result = review_agicore_trading_v1_offline_tag_creation_execution_plan(data)

    assert review_tag_creation_execution_plan_review_steps(context) is False
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.TAG_CREATION_EXECUTION_PLAN_REVIEW_STEPS_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewDecision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_REVIEW_STEP_FIXES


def test_commands_non_documentation_only():
    data = _input(commands_documentation_only=False)
    context = build_tag_creation_execution_plan_review_context(data)
    result = review_agicore_trading_v1_offline_tag_creation_execution_plan(data)

    assert review_tag_creation_execution_plan_review_commands_documented_only(context) is False
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.TAG_CREATION_EXECUTION_PLAN_REVIEW_COMMANDS_NOT_DOCUMENTATION_ONLY in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewDecision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_REVIEW_COMMAND_DOCUMENTATION_FIXES


def test_local_checks_manquants():
    data = _input(local_checks_present=False)
    context = build_tag_creation_execution_plan_review_context(data)
    result = review_agicore_trading_v1_offline_tag_creation_execution_plan(data)

    assert review_tag_creation_execution_plan_review_local_checks(context, data) is False
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.TAG_CREATION_EXECUTION_PLAN_REVIEW_LOCAL_CHECKS_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewDecision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_REVIEW_STEP_FIXES


def test_remote_checks_manquants():
    data = _input(remote_checks_present=False)
    context = build_tag_creation_execution_plan_review_context(data)
    result = review_agicore_trading_v1_offline_tag_creation_execution_plan(data)

    assert review_tag_creation_execution_plan_review_remote_checks(context, data) is False
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.TAG_CREATION_EXECUTION_PLAN_REVIEW_REMOTE_CHECKS_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewDecision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_REVIEW_STEP_FIXES


def test_stop_rules_manquantes():
    data = _input(stop_rules_present=False)
    context = build_tag_creation_execution_plan_review_context(data)
    result = review_agicore_trading_v1_offline_tag_creation_execution_plan(data)

    assert review_tag_creation_execution_plan_review_stop_rules(context) is False
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.TAG_CREATION_EXECUTION_PLAN_REVIEW_STOP_RULES_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewDecision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_REVIEW_STOP_RULE_FIXES


def test_git_tag_already_created():
    data = _input(git_tag_already_created=True)
    result = review_agicore_trading_v1_offline_tag_creation_execution_plan(data)

    assert review_tag_creation_execution_plan_review_no_git_tag_created(data) is False
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.GIT_TAG_ALREADY_CREATED in result.risks
    assert result.git_tag_created is False


def test_git_tag_already_pushed():
    data = _input(git_tag_already_pushed=True)
    result = review_agicore_trading_v1_offline_tag_creation_execution_plan(data)

    assert review_tag_creation_execution_plan_review_no_git_tag_pushed(data) is False
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.GIT_TAG_ALREADY_PUSHED in result.risks
    assert result.git_tag_pushed is False


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("live_trading_overclaim", AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.LIVE_TRADING_READINESS_OVERCLAIM),
        ("real_broker_overclaim", AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.REAL_BROKER_READINESS_OVERCLAIM),
        ("real_order_overclaim", AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.REAL_ORDER_EXECUTION_OVERCLAIM),
        ("paper_broker_overclaim", AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.PAPER_BROKER_CONNECTION_OVERCLAIM),
        ("profitability_overclaim", AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.PROFITABILITY_PROOF_OVERCLAIM),
        ("financial_advice_overclaim", AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.FINANCIAL_ADVICE_OVERCLAIM),
    ),
)
def test_overclaims(field, risk):
    data = _input(**{field: True})
    result = review_agicore_trading_v1_offline_tag_creation_execution_plan(data)

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewDecision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_REVIEW_NO_OVERCLAIM_FIXES


def test_no_overclaim_helpers():
    assert review_tag_creation_execution_plan_review_no_live_trading_claim(_input(live_trading_overclaim=True)) is False
    assert review_tag_creation_execution_plan_review_no_profitability_claim(_input(profitability_overclaim=True)) is False
    assert review_tag_creation_execution_plan_review_no_financial_advice_claim(_input(financial_advice_overclaim=True)) is False


def test_markdown_genere():
    result = review_agicore_trading_v1_offline_tag_creation_execution_plan(_input())
    markdown = render_agicore_trading_v1_offline_tag_creation_execution_plan_review_markdown(
        result.context, result.findings
    )

    assert "AGIcore Trading v1 Offline Tag Creation Execution Plan Review" in markdown
    assert "git tag -a agicore-trading-v1-offline" in markdown
    assert validate_tag_creation_execution_plan_review_markdown(markdown)


def test_markdown_docs_valide():
    assert DOC_PATH.exists()
    markdown = DOC_PATH.read_text(encoding="utf-8")

    assert validate_tag_creation_execution_plan_review_markdown(markdown)


def test_json_report():
    result = review_agicore_trading_v1_offline_tag_creation_execution_plan(_input())
    report = render_agicore_trading_v1_offline_tag_creation_execution_plan_review_json_report(result)
    payload = json.loads(report)

    assert payload["decision"] == "APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_REVIEW"
    assert payload["state"] == "READY_FOR_AGICORE_TRADING_V1_OFFLINE_FINAL_MANUAL_TAG_AUTHORIZATION"
    assert payload["score"] == 100
    assert payload["git_tag_created"] is False
    assert payload["git_tag_pushed"] is False


def test_score_risks_recommendations():
    data = _input()
    context = build_tag_creation_execution_plan_review_context(data)
    risks = detect_agicore_trading_v1_offline_tag_creation_execution_plan_review_risks(data, context)
    score = compute_agicore_trading_v1_offline_tag_creation_execution_plan_review_score(data, context, risks)
    recommendations = generate_agicore_trading_v1_offline_tag_creation_execution_plan_review_recommendations(risks)

    assert risks == ()
    assert score.overall_score == 100
    assert recommendations == (
        AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRecommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_FINAL_MANUAL_TAG_AUTHORIZATION,
    )


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("file_read_requested", AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.FILE_READ_BOUNDARY_VIOLATION),
        ("real_data_access_requested", AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_access_requested", AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("broker_connection_requested", AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.REAL_BROKER_BOUNDARY_VIOLATION),
        ("secret_read_requested", AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("network_requested", AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("http_requested", AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("websocket_requested", AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("socket_requested", AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("external_api_requested", AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("order_execution_requested", AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ("account_access_requested", AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ("position_mutation_requested", AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk.POSITION_MUTATION_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations(field, risk):
    data = _input(**{field: True})
    result = review_agicore_trading_v1_offline_tag_creation_execution_plan(data)

    assert assert_agicore_trading_v1_offline_tag_creation_execution_plan_review_boundaries(data) is False
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
    result = review_agicore_trading_v1_offline_tag_creation_execution_plan(_input())

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
