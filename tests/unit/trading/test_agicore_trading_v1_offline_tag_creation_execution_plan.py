from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agicore.trading.agicore_trading_v1_offline_tag_creation_execution_plan import (
    assert_agicore_trading_v1_offline_tag_creation_execution_plan_boundaries,
    build_agicore_trading_v1_offline_tag_creation_execution_plan,
    build_tag_creation_execution_plan_context,
    compute_agicore_trading_v1_offline_tag_creation_execution_plan_score,
    detect_agicore_trading_v1_offline_tag_creation_execution_plan_risks,
    generate_agicore_trading_v1_offline_tag_creation_execution_plan_recommendations,
    render_agicore_trading_v1_offline_tag_creation_execution_plan_json_report,
    render_agicore_trading_v1_offline_tag_creation_execution_plan_markdown,
    review_tag_creation_execution_plan_commands_documented_only,
    review_tag_creation_execution_plan_no_financial_advice_claim,
    review_tag_creation_execution_plan_no_git_tag_created,
    review_tag_creation_execution_plan_no_git_tag_pushed,
    review_tag_creation_execution_plan_no_live_trading_claim,
    review_tag_creation_execution_plan_no_profitability_claim,
    review_tag_creation_execution_plan_pre_checks,
    review_tag_creation_execution_plan_prerequisites,
    review_tag_creation_execution_plan_remote_checks,
    review_tag_creation_execution_plan_steps,
    review_tag_creation_execution_plan_stop_rules,
    review_tag_creation_execution_plan_tag_name,
    review_tag_creation_execution_plan_version,
    validate_agicore_trading_v1_offline_tag_creation_execution_plan_input,
    validate_tag_creation_execution_plan_markdown,
)
from agicore.trading.agicore_trading_v1_offline_tag_creation_execution_plan_models import (
    AGIcoreTradingV1OfflineTagCreationExecutionPlanDecision,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanInput,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanRecommendation,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanState,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/agicore_trading_v1_offline_tag_creation_execution_plan.py"
DOC_PATH = ROOT / "docs/AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN.md"


def _input(**overrides):
    payload = {}
    payload.update(overrides)
    return AGIcoreTradingV1OfflineTagCreationExecutionPlanInput(**payload)


def test_nominal_tag_creation_execution_plan():
    result = build_agicore_trading_v1_offline_tag_creation_execution_plan(_input())

    assert result.decision is AGIcoreTradingV1OfflineTagCreationExecutionPlanDecision.APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN
    assert result.state is AGIcoreTradingV1OfflineTagCreationExecutionPlanState.READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_REVIEW
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.git_tag_created is False
    assert result.git_tag_pushed is False
    assert result.context.tag_metadata.tag_name == "agicore-trading-v1-offline"
    assert result.context.tag_metadata.version == "v1.0.0-offline"
    assert validate_tag_creation_execution_plan_markdown(result.report.markdown)


def test_input_manquant():
    result = build_agicore_trading_v1_offline_tag_creation_execution_plan(None)

    assert validate_agicore_trading_v1_offline_tag_creation_execution_plan_input(None) is False
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.TAG_CREATION_EXECUTION_PLAN_INPUT_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationExecutionPlanDecision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_INPUT_FIXES
    assert result.state is AGIcoreTradingV1OfflineTagCreationExecutionPlanState.AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_INPUT_INVALID


def test_prerequisites_incomplets():
    data = _input(prerequisites_complete=False)
    context = build_tag_creation_execution_plan_context(data)
    result = build_agicore_trading_v1_offline_tag_creation_execution_plan(data)

    assert review_tag_creation_execution_plan_prerequisites(context, data) is False
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.TAG_CREATION_EXECUTION_PLAN_PREREQUISITES_INCOMPLETE in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationExecutionPlanDecision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_PREREQUISITE_FIXES


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("manual_tag_creation_approval_approved", AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED),
        ("manual_tag_creation_final_checklist_approved", AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.MANUAL_TAG_CREATION_FINAL_CHECKLIST_NOT_APPROVED),
        ("human_tag_go_no_go_approved", AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.HUMAN_TAG_GO_NO_GO_NOT_APPROVED),
        ("tag_creation_instructions_review_approved", AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.TAG_CREATION_INSTRUCTIONS_REVIEW_NOT_APPROVED),
        ("final_tag_review_approved", AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.FINAL_TAG_REVIEW_NOT_APPROVED),
        ("release_package_review_approved", AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED),
        ("final_readiness_review_approved", AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.FINAL_READINESS_REVIEW_NOT_APPROVED),
    ),
)
def test_prerequisite_approval_missing(field, risk):
    result = build_agicore_trading_v1_offline_tag_creation_execution_plan(_input(**{field: False}))

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationExecutionPlanDecision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_PREREQUISITE_FIXES


def test_tag_name_invalide():
    result = build_agicore_trading_v1_offline_tag_creation_execution_plan(_input(tag_name="bad"))

    assert review_tag_creation_execution_plan_tag_name(_input(tag_name="bad")) is False
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.TAG_CREATION_EXECUTION_PLAN_TAG_NAME_INVALID in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationExecutionPlanDecision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_TAG_NAME_FIXES


def test_version_invalide():
    result = build_agicore_trading_v1_offline_tag_creation_execution_plan(_input(version="v1-live"))

    assert review_tag_creation_execution_plan_version(_input(version="v1-live")) is False
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.TAG_CREATION_EXECUTION_PLAN_VERSION_INVALID in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationExecutionPlanDecision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_VERSION_FIXES


@pytest.mark.parametrize("field", ("steps_present", "pre_checks_present", "remote_checks_present"))
def test_steps_or_checks_manquants(field):
    data = _input(**{field: False})
    context = build_tag_creation_execution_plan_context(data)
    result = build_agicore_trading_v1_offline_tag_creation_execution_plan(data)

    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.TAG_CREATION_EXECUTION_PLAN_STEPS_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationExecutionPlanDecision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_STEP_FIXES
    if field == "steps_present":
        assert review_tag_creation_execution_plan_steps(context) is False
    if field == "pre_checks_present":
        assert review_tag_creation_execution_plan_pre_checks(context, data) is False
    if field == "remote_checks_present":
        assert review_tag_creation_execution_plan_remote_checks(context, data) is False


def test_commands_non_documentation_only():
    data = _input(commands_documentation_only=False)
    context = build_tag_creation_execution_plan_context(data)
    result = build_agicore_trading_v1_offline_tag_creation_execution_plan(data)

    assert review_tag_creation_execution_plan_commands_documented_only(context) is False
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.TAG_CREATION_EXECUTION_PLAN_COMMANDS_NOT_DOCUMENTATION_ONLY in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationExecutionPlanDecision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_COMMAND_DOCUMENTATION_FIXES


def test_stop_rules_manquantes():
    data = _input(stop_rules_present=False)
    context = build_tag_creation_execution_plan_context(data)
    result = build_agicore_trading_v1_offline_tag_creation_execution_plan(data)

    assert review_tag_creation_execution_plan_stop_rules(context) is False
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.TAG_CREATION_EXECUTION_PLAN_STOP_RULES_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationExecutionPlanDecision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_STOP_RULE_FIXES


def test_git_tag_already_created():
    result = build_agicore_trading_v1_offline_tag_creation_execution_plan(_input(git_tag_already_created=True))

    assert review_tag_creation_execution_plan_no_git_tag_created(_input(git_tag_already_created=True)) is False
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.GIT_TAG_ALREADY_CREATED in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationExecutionPlanDecision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_NO_OVERCLAIM_FIXES
    assert result.git_tag_created is False


def test_git_tag_already_pushed():
    result = build_agicore_trading_v1_offline_tag_creation_execution_plan(_input(git_tag_already_pushed=True))

    assert review_tag_creation_execution_plan_no_git_tag_pushed(_input(git_tag_already_pushed=True)) is False
    assert AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.GIT_TAG_ALREADY_PUSHED in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationExecutionPlanDecision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_NO_OVERCLAIM_FIXES
    assert result.git_tag_pushed is False


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("live_trading_overclaim", AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.LIVE_TRADING_READINESS_OVERCLAIM),
        ("real_broker_overclaim", AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.REAL_BROKER_READINESS_OVERCLAIM),
        ("real_order_overclaim", AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.REAL_ORDER_EXECUTION_OVERCLAIM),
        ("paper_broker_overclaim", AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.PAPER_BROKER_CONNECTION_OVERCLAIM),
        ("profitability_overclaim", AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.PROFITABILITY_PROOF_OVERCLAIM),
        ("financial_advice_overclaim", AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.FINANCIAL_ADVICE_OVERCLAIM),
    ),
)
def test_overclaims_are_blocked(field, risk):
    result = build_agicore_trading_v1_offline_tag_creation_execution_plan(_input(**{field: True}))

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationExecutionPlanDecision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_NO_OVERCLAIM_FIXES


def test_no_overclaim_helpers():
    assert review_tag_creation_execution_plan_no_live_trading_claim(_input()) is True
    assert review_tag_creation_execution_plan_no_live_trading_claim(_input(live_trading_overclaim=True)) is False
    assert review_tag_creation_execution_plan_no_profitability_claim(_input()) is True
    assert review_tag_creation_execution_plan_no_profitability_claim(_input(profitability_overclaim=True)) is False
    assert review_tag_creation_execution_plan_no_financial_advice_claim(_input()) is True
    assert review_tag_creation_execution_plan_no_financial_advice_claim(_input(financial_advice_overclaim=True)) is False


def test_markdown_genere():
    data = _input()
    context = build_tag_creation_execution_plan_context(data)
    markdown = render_agicore_trading_v1_offline_tag_creation_execution_plan_markdown(context)

    assert "AGIcore Trading v1 Offline Tag Creation Execution Plan" in markdown
    assert "git ls-remote --tags origin agicore-trading-v1-offline" in markdown
    assert "10. pousser le tag manuellement seulement apres creation locale validee" in markdown
    assert validate_tag_creation_execution_plan_markdown(markdown)


def test_markdown_docs_valide():
    markdown = DOC_PATH.read_text(encoding="utf-8")

    assert validate_tag_creation_execution_plan_markdown(markdown)
    assert "AGIcore Trading v1 Offline Tag Creation Execution Plan Review" in markdown


def test_json_report():
    result = build_agicore_trading_v1_offline_tag_creation_execution_plan(_input())
    payload = json.loads(render_agicore_trading_v1_offline_tag_creation_execution_plan_json_report(result))

    assert payload["schema"] == "agicore_trading_v1_offline_tag_creation_execution_plan"
    assert payload["decision"] == "APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN"
    assert payload["state"] == "READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_REVIEW"
    assert payload["score"] == 100
    assert payload["git_tag_created"] is False
    assert payload["git_tag_pushed"] is False
    assert payload["commands_documented_only"] is True
    assert payload["real_order_execution"] is False


def test_score_risks_and_recommendations_directly():
    data = _input()
    context = build_tag_creation_execution_plan_context(data)
    risks = detect_agicore_trading_v1_offline_tag_creation_execution_plan_risks(data, context)
    score = compute_agicore_trading_v1_offline_tag_creation_execution_plan_score(data, context, risks)
    recommendations = generate_agicore_trading_v1_offline_tag_creation_execution_plan_recommendations(risks)

    assert risks == ()
    assert score.overall_score == 100
    assert recommendations == (
        AGIcoreTradingV1OfflineTagCreationExecutionPlanRecommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_REVIEW,
    )


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("file_read_requested", AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.FILE_READ_BOUNDARY_VIOLATION),
        ("real_data_access_requested", AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_access_requested", AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("broker_connection_requested", AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.REAL_BROKER_BOUNDARY_VIOLATION),
        ("secret_read_requested", AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("network_requested", AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.NETWORK_BOUNDARY_VIOLATION),
        ("http_requested", AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.NETWORK_BOUNDARY_VIOLATION),
        ("websocket_requested", AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.NETWORK_BOUNDARY_VIOLATION),
        ("socket_requested", AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.NETWORK_BOUNDARY_VIOLATION),
        ("external_api_requested", AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.NETWORK_BOUNDARY_VIOLATION),
        ("order_execution_requested", AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ("account_access_requested", AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ("position_mutation_requested", AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk.POSITION_MUTATION_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations_are_blocked(field, risk):
    data = _input(**{field: True})
    result = build_agicore_trading_v1_offline_tag_creation_execution_plan(data)

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationExecutionPlanDecision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_NO_OVERCLAIM_FIXES
    assert assert_agicore_trading_v1_offline_tag_creation_execution_plan_boundaries(data) is False


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
    result = build_agicore_trading_v1_offline_tag_creation_execution_plan(_input())

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
