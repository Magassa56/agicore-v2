from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agicore.trading.agicore_trading_v1_offline_manual_tag_creation_final_checklist import (
    assert_agicore_trading_v1_offline_manual_tag_creation_final_checklist_boundaries,
    build_agicore_trading_v1_offline_manual_tag_creation_final_checklist,
    build_manual_tag_creation_final_checklist_context,
    compute_agicore_trading_v1_offline_manual_tag_creation_final_checklist_score,
    detect_agicore_trading_v1_offline_manual_tag_creation_final_checklist_risks,
    generate_agicore_trading_v1_offline_manual_tag_creation_final_checklist_recommendations,
    render_agicore_trading_v1_offline_manual_tag_creation_final_checklist_json_report,
    render_agicore_trading_v1_offline_manual_tag_creation_final_checklist_markdown,
    review_manual_tag_checklist_documented_commands_only,
    review_manual_tag_checklist_no_financial_advice_claim,
    review_manual_tag_checklist_no_git_tag_created,
    review_manual_tag_checklist_no_git_tag_pushed,
    review_manual_tag_checklist_no_live_trading_claim,
    review_manual_tag_checklist_no_profitability_claim,
    review_manual_tag_checklist_post_tag_items,
    review_manual_tag_checklist_pre_tag_items,
    review_manual_tag_checklist_prerequisites,
    review_manual_tag_checklist_stop_procedure,
    review_manual_tag_checklist_tag_name,
    review_manual_tag_checklist_version,
    validate_agicore_trading_v1_offline_manual_tag_creation_final_checklist_input,
    validate_manual_tag_creation_final_checklist_markdown,
)
from agicore.trading.agicore_trading_v1_offline_manual_tag_creation_final_checklist_models import (
    AGIcoreTradingV1OfflineManualTagCreationFinalChecklistDecision,
    AGIcoreTradingV1OfflineManualTagCreationFinalChecklistInput,
    AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRecommendation,
    AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk,
    AGIcoreTradingV1OfflineManualTagCreationFinalChecklistState,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/agicore_trading_v1_offline_manual_tag_creation_final_checklist.py"
DOC_PATH = ROOT / "docs/AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_FINAL_CHECKLIST.md"


def _input(**overrides):
    payload = {}
    payload.update(overrides)
    return AGIcoreTradingV1OfflineManualTagCreationFinalChecklistInput(**payload)


def test_nominal_final_checklist():
    result = build_agicore_trading_v1_offline_manual_tag_creation_final_checklist(_input())

    assert result.decision is AGIcoreTradingV1OfflineManualTagCreationFinalChecklistDecision.APPROVE_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_FINAL_CHECKLIST
    assert result.state is AGIcoreTradingV1OfflineManualTagCreationFinalChecklistState.READY_FOR_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_APPROVAL
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.git_tag_created is False
    assert result.git_tag_pushed is False
    assert result.context.tag_metadata.tag_name == "agicore-trading-v1-offline"
    assert result.context.tag_metadata.version == "v1.0.0-offline"
    assert validate_manual_tag_creation_final_checklist_markdown(result.report.markdown)


def test_input_manquant():
    result = build_agicore_trading_v1_offline_manual_tag_creation_final_checklist(None)

    assert validate_agicore_trading_v1_offline_manual_tag_creation_final_checklist_input(None) is False
    assert AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk.MANUAL_TAG_CHECKLIST_INPUT_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineManualTagCreationFinalChecklistDecision.REQUIRE_MANUAL_TAG_CHECKLIST_INPUT_FIXES
    assert result.state is AGIcoreTradingV1OfflineManualTagCreationFinalChecklistState.AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_FINAL_CHECKLIST_INPUT_INVALID


def test_prerequisites_incomplets():
    data = _input(prerequisites_complete=False)
    context = build_manual_tag_creation_final_checklist_context(data)
    result = build_agicore_trading_v1_offline_manual_tag_creation_final_checklist(data)

    assert review_manual_tag_checklist_prerequisites(context, data) is False
    assert AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk.MANUAL_TAG_CHECKLIST_PREREQUISITES_INCOMPLETE in result.risks
    assert result.decision is AGIcoreTradingV1OfflineManualTagCreationFinalChecklistDecision.REQUIRE_MANUAL_TAG_CHECKLIST_PREREQUISITE_FIXES


@pytest.mark.parametrize(
    "field",
    (
        "human_tag_go_no_go_approved",
        "tag_creation_instructions_review_approved",
        "final_tag_review_approved",
        "release_package_review_approved",
        "final_readiness_review_approved",
    ),
)
def test_prerequisite_approval_missing(field):
    data = _input(**{field: False})
    result = build_agicore_trading_v1_offline_manual_tag_creation_final_checklist(data)

    assert AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk.MANUAL_TAG_CHECKLIST_PREREQUISITES_INCOMPLETE in result.risks
    assert result.decision is AGIcoreTradingV1OfflineManualTagCreationFinalChecklistDecision.REQUIRE_MANUAL_TAG_CHECKLIST_PREREQUISITE_FIXES


def test_tag_name_invalide():
    result = build_agicore_trading_v1_offline_manual_tag_creation_final_checklist(_input(tag_name="bad"))

    assert review_manual_tag_checklist_tag_name(_input(tag_name="bad")) is False
    assert AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk.MANUAL_TAG_CHECKLIST_TAG_NAME_INVALID in result.risks
    assert result.decision is AGIcoreTradingV1OfflineManualTagCreationFinalChecklistDecision.REQUIRE_MANUAL_TAG_CHECKLIST_TAG_NAME_FIXES


def test_version_invalide():
    result = build_agicore_trading_v1_offline_manual_tag_creation_final_checklist(_input(version="v1-live"))

    assert review_manual_tag_checklist_version(_input(version="v1-live")) is False
    assert AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk.MANUAL_TAG_CHECKLIST_VERSION_INVALID in result.risks
    assert result.decision is AGIcoreTradingV1OfflineManualTagCreationFinalChecklistDecision.REQUIRE_MANUAL_TAG_CHECKLIST_VERSION_FIXES


def test_pre_tag_items_manquants():
    data = _input(pre_tag_items_present=False)
    context = build_manual_tag_creation_final_checklist_context(data)
    result = build_agicore_trading_v1_offline_manual_tag_creation_final_checklist(data)

    assert review_manual_tag_checklist_pre_tag_items(context) is False
    assert AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk.MANUAL_TAG_CHECKLIST_PRE_TAG_ITEMS_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineManualTagCreationFinalChecklistDecision.REQUIRE_MANUAL_TAG_CHECKLIST_PRE_TAG_FIXES


def test_commands_non_documentation_only():
    data = _input(commands_documentation_only=False)
    context = build_manual_tag_creation_final_checklist_context(data)
    result = build_agicore_trading_v1_offline_manual_tag_creation_final_checklist(data)

    assert review_manual_tag_checklist_documented_commands_only(context) is False
    assert AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk.MANUAL_TAG_CHECKLIST_COMMANDS_NOT_DOCUMENTATION_ONLY in result.risks
    assert result.decision is AGIcoreTradingV1OfflineManualTagCreationFinalChecklistDecision.REQUIRE_MANUAL_TAG_CHECKLIST_COMMAND_DOCUMENTATION_FIXES


def test_post_tag_items_manquants():
    data = _input(post_tag_items_present=False)
    context = build_manual_tag_creation_final_checklist_context(data)
    result = build_agicore_trading_v1_offline_manual_tag_creation_final_checklist(data)

    assert review_manual_tag_checklist_post_tag_items(context) is False
    assert AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk.MANUAL_TAG_CHECKLIST_POST_TAG_ITEMS_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineManualTagCreationFinalChecklistDecision.REQUIRE_MANUAL_TAG_CHECKLIST_POST_TAG_FIXES


def test_stop_rules_manquantes():
    data = _input(stop_rules_present=False)
    context = build_manual_tag_creation_final_checklist_context(data)
    result = build_agicore_trading_v1_offline_manual_tag_creation_final_checklist(data)

    assert review_manual_tag_checklist_stop_procedure(context) is False
    assert AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk.MANUAL_TAG_CHECKLIST_STOP_RULES_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineManualTagCreationFinalChecklistDecision.REQUIRE_MANUAL_TAG_CHECKLIST_STOP_RULE_FIXES


def test_git_tag_already_created():
    result = build_agicore_trading_v1_offline_manual_tag_creation_final_checklist(_input(git_tag_already_created=True))

    assert review_manual_tag_checklist_no_git_tag_created(_input(git_tag_already_created=True)) is False
    assert AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk.GIT_TAG_ALREADY_CREATED in result.risks
    assert result.decision is AGIcoreTradingV1OfflineManualTagCreationFinalChecklistDecision.REQUIRE_MANUAL_TAG_CHECKLIST_NO_OVERCLAIM_FIXES
    assert result.git_tag_created is False


def test_git_tag_already_pushed():
    result = build_agicore_trading_v1_offline_manual_tag_creation_final_checklist(_input(git_tag_already_pushed=True))

    assert review_manual_tag_checklist_no_git_tag_pushed(_input(git_tag_already_pushed=True)) is False
    assert AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk.GIT_TAG_ALREADY_PUSHED in result.risks
    assert result.decision is AGIcoreTradingV1OfflineManualTagCreationFinalChecklistDecision.REQUIRE_MANUAL_TAG_CHECKLIST_NO_OVERCLAIM_FIXES
    assert result.git_tag_pushed is False


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("live_trading_overclaim", AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk.LIVE_TRADING_READINESS_OVERCLAIM),
        ("real_broker_overclaim", AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk.REAL_BROKER_READINESS_OVERCLAIM),
        ("real_order_overclaim", AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk.REAL_ORDER_EXECUTION_OVERCLAIM),
        ("paper_broker_overclaim", AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk.PAPER_BROKER_CONNECTION_OVERCLAIM),
        ("profitability_overclaim", AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk.PROFITABILITY_PROOF_OVERCLAIM),
        ("financial_advice_overclaim", AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk.FINANCIAL_ADVICE_OVERCLAIM),
    ),
)
def test_overclaims_are_blocked(field, risk):
    result = build_agicore_trading_v1_offline_manual_tag_creation_final_checklist(_input(**{field: True}))

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineManualTagCreationFinalChecklistDecision.REQUIRE_MANUAL_TAG_CHECKLIST_NO_OVERCLAIM_FIXES


def test_no_overclaim_helpers():
    assert review_manual_tag_checklist_no_live_trading_claim(_input()) is True
    assert review_manual_tag_checklist_no_live_trading_claim(_input(live_trading_overclaim=True)) is False
    assert review_manual_tag_checklist_no_profitability_claim(_input()) is True
    assert review_manual_tag_checklist_no_profitability_claim(_input(profitability_overclaim=True)) is False
    assert review_manual_tag_checklist_no_financial_advice_claim(_input()) is True
    assert review_manual_tag_checklist_no_financial_advice_claim(_input(financial_advice_overclaim=True)) is False


def test_markdown_genere():
    data = _input()
    context = build_manual_tag_creation_final_checklist_context(data)
    markdown = render_agicore_trading_v1_offline_manual_tag_creation_final_checklist_markdown(context)

    assert "AGIcore Trading v1 Offline Manual Tag Creation Final Checklist" in markdown
    assert "git tag -a agicore-trading-v1-offline" in markdown
    assert "STOP si tests rouges" in markdown
    assert validate_manual_tag_creation_final_checklist_markdown(markdown)


def test_markdown_docs_valide():
    markdown = DOC_PATH.read_text(encoding="utf-8")

    assert validate_manual_tag_creation_final_checklist_markdown(markdown)
    assert "AGIcore Trading v1 Offline Manual Tag Creation Approval" in markdown


def test_json_report():
    result = build_agicore_trading_v1_offline_manual_tag_creation_final_checklist(_input())
    payload = json.loads(render_agicore_trading_v1_offline_manual_tag_creation_final_checklist_json_report(result))

    assert payload["schema"] == "agicore_trading_v1_offline_manual_tag_creation_final_checklist"
    assert payload["decision"] == "APPROVE_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_FINAL_CHECKLIST"
    assert payload["state"] == "READY_FOR_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_APPROVAL"
    assert payload["score"] == 100
    assert payload["git_tag_created"] is False
    assert payload["git_tag_pushed"] is False
    assert payload["commands_documented_only"] is True
    assert payload["real_order_execution"] is False


def test_score_risks_and_recommendations_directly():
    data = _input()
    context = build_manual_tag_creation_final_checklist_context(data)
    risks = detect_agicore_trading_v1_offline_manual_tag_creation_final_checklist_risks(data, context)
    score = compute_agicore_trading_v1_offline_manual_tag_creation_final_checklist_score(data, context, risks)
    recommendations = generate_agicore_trading_v1_offline_manual_tag_creation_final_checklist_recommendations(risks)

    assert risks == ()
    assert score.overall_score == 100
    assert recommendations == (
        AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRecommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_APPROVAL,
    )


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("file_read_requested", AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk.FILE_READ_BOUNDARY_VIOLATION),
        ("real_data_access_requested", AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_access_requested", AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("broker_connection_requested", AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk.REAL_BROKER_BOUNDARY_VIOLATION),
        ("secret_read_requested", AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("network_requested", AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk.NETWORK_BOUNDARY_VIOLATION),
        ("http_requested", AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk.NETWORK_BOUNDARY_VIOLATION),
        ("websocket_requested", AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk.NETWORK_BOUNDARY_VIOLATION),
        ("socket_requested", AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk.NETWORK_BOUNDARY_VIOLATION),
        ("external_api_requested", AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk.NETWORK_BOUNDARY_VIOLATION),
        ("order_execution_requested", AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ("account_access_requested", AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ("position_mutation_requested", AGIcoreTradingV1OfflineManualTagCreationFinalChecklistRisk.POSITION_MUTATION_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations_are_blocked(field, risk):
    data = _input(**{field: True})
    result = build_agicore_trading_v1_offline_manual_tag_creation_final_checklist(data)

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineManualTagCreationFinalChecklistDecision.REQUIRE_MANUAL_TAG_CHECKLIST_NO_OVERCLAIM_FIXES
    assert assert_agicore_trading_v1_offline_manual_tag_creation_final_checklist_boundaries(data) is False


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
    result = build_agicore_trading_v1_offline_manual_tag_creation_final_checklist(_input())

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
