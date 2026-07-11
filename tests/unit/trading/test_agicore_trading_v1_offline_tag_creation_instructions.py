from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agicore.trading.agicore_trading_v1_offline_tag_creation_instructions import (
    assert_agicore_trading_v1_offline_tag_creation_instructions_boundaries,
    build_agicore_trading_v1_offline_tag_creation_instructions,
    build_tag_creation_commands_section,
    build_tag_creation_instructions_context,
    build_tag_creation_post_checks_section,
    build_tag_creation_pre_checks_section,
    build_tag_creation_safety_section,
    compute_agicore_trading_v1_offline_tag_creation_instructions_score,
    detect_agicore_trading_v1_offline_tag_creation_instructions_risks,
    generate_agicore_trading_v1_offline_tag_creation_instructions_recommendations,
    render_agicore_trading_v1_offline_tag_creation_instructions_json_report,
    render_agicore_trading_v1_offline_tag_creation_instructions_markdown,
    validate_agicore_trading_v1_offline_tag_creation_instructions_input,
    validate_tag_creation_instructions_markdown,
    validate_tag_creation_instructions_no_git_tag_created,
    validate_tag_creation_instructions_no_overclaims,
    validate_tag_creation_instructions_safety_language,
)
from agicore.trading.agicore_trading_v1_offline_tag_creation_instructions_models import (
    AGIcoreTradingV1OfflineTagCreationInstructionsDecision,
    AGIcoreTradingV1OfflineTagCreationInstructionsInput,
    AGIcoreTradingV1OfflineTagCreationInstructionsRecommendation,
    AGIcoreTradingV1OfflineTagCreationInstructionsRisk,
    AGIcoreTradingV1OfflineTagCreationInstructionsState,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/agicore_trading_v1_offline_tag_creation_instructions.py"
DOC_PATH = ROOT / "docs/AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS.md"


def _input(**overrides):
    payload = {}
    payload.update(overrides)
    return AGIcoreTradingV1OfflineTagCreationInstructionsInput(**payload)


def test_nominal_tag_creation_instructions():
    result = build_agicore_trading_v1_offline_tag_creation_instructions(_input())

    assert result.decision is AGIcoreTradingV1OfflineTagCreationInstructionsDecision.APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS
    assert result.state is AGIcoreTradingV1OfflineTagCreationInstructionsState.READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.git_tag_created is False
    assert result.git_tag_pushed is False
    assert result.context.prerequisite_decision == "APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW"
    assert result.context.tag_name == "agicore-trading-v1-offline"
    assert result.context.version == "v1.0.0-offline"
    assert len(result.context.pre_checks) == 5
    assert len(result.context.manual_commands) == 2
    assert len(result.context.post_checks) == 3
    assert validate_tag_creation_instructions_markdown(result.report.markdown)


def test_input_manquant():
    result = build_agicore_trading_v1_offline_tag_creation_instructions(None)

    assert validate_agicore_trading_v1_offline_tag_creation_instructions_input(None) is False
    assert AGIcoreTradingV1OfflineTagCreationInstructionsRisk.TAG_CREATION_INSTRUCTIONS_INPUT_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationInstructionsDecision.REQUIRE_TAG_CREATION_INSTRUCTIONS_INPUT_FIXES
    assert result.state is AGIcoreTradingV1OfflineTagCreationInstructionsState.AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_INPUT_INVALID


def test_final_tag_review_non_approuvee():
    result = build_agicore_trading_v1_offline_tag_creation_instructions(_input(final_tag_review_approved=False))

    assert AGIcoreTradingV1OfflineTagCreationInstructionsRisk.FINAL_TAG_REVIEW_NOT_APPROVED in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationInstructionsDecision.REQUIRE_TAG_CREATION_INSTRUCTIONS_FINAL_REVIEW_FIXES


def test_tag_name_invalide():
    result = build_agicore_trading_v1_offline_tag_creation_instructions(_input(tag_name="bad-tag"))

    assert AGIcoreTradingV1OfflineTagCreationInstructionsRisk.TAG_CREATION_TAG_NAME_INVALID in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationInstructionsDecision.REQUIRE_TAG_CREATION_INSTRUCTIONS_TAG_NAME_FIXES


def test_version_invalide():
    result = build_agicore_trading_v1_offline_tag_creation_instructions(_input(version="v1-live"))

    assert AGIcoreTradingV1OfflineTagCreationInstructionsRisk.TAG_CREATION_VERSION_INVALID in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationInstructionsDecision.REQUIRE_TAG_CREATION_INSTRUCTIONS_VERSION_FIXES


def test_pre_checks_manquants():
    data = _input(pre_checks_present=False)
    result = build_agicore_trading_v1_offline_tag_creation_instructions(data)

    assert all(not check.present for check in build_tag_creation_pre_checks_section(data))
    assert AGIcoreTradingV1OfflineTagCreationInstructionsRisk.TAG_CREATION_PRE_CHECKS_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationInstructionsDecision.REQUIRE_TAG_CREATION_INSTRUCTIONS_PRE_CHECK_FIXES


def test_manual_commands_manquantes():
    data = _input(manual_commands_documented=False)
    result = build_agicore_trading_v1_offline_tag_creation_instructions(data)

    assert build_tag_creation_commands_section(data) == ()
    assert AGIcoreTradingV1OfflineTagCreationInstructionsRisk.TAG_CREATION_COMMANDS_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationInstructionsDecision.REQUIRE_TAG_CREATION_INSTRUCTIONS_COMMAND_FIXES


def test_post_checks_manquants():
    data = _input(post_checks_present=False)
    result = build_agicore_trading_v1_offline_tag_creation_instructions(data)

    assert all(not check.present for check in build_tag_creation_post_checks_section(data))
    assert AGIcoreTradingV1OfflineTagCreationInstructionsRisk.TAG_CREATION_POST_CHECKS_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationInstructionsDecision.REQUIRE_TAG_CREATION_INSTRUCTIONS_POST_CHECK_FIXES


def test_warning_manquant():
    result = build_agicore_trading_v1_offline_tag_creation_instructions(_input(warning_present=False))

    assert AGIcoreTradingV1OfflineTagCreationInstructionsRisk.TAG_CREATION_WARNING_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationInstructionsDecision.REQUIRE_TAG_CREATION_INSTRUCTIONS_SAFETY_FIXES


def test_safety_language_manquant():
    result = build_agicore_trading_v1_offline_tag_creation_instructions(_input(safety_language_present=False))

    assert validate_tag_creation_instructions_safety_language(_input(safety_language_present=False)) is False
    assert AGIcoreTradingV1OfflineTagCreationInstructionsRisk.TAG_CREATION_SAFETY_LANGUAGE_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationInstructionsDecision.REQUIRE_TAG_CREATION_INSTRUCTIONS_SAFETY_FIXES


def test_git_tag_already_created():
    result = build_agicore_trading_v1_offline_tag_creation_instructions(_input(git_tag_already_created=True))

    assert validate_tag_creation_instructions_no_git_tag_created(_input(git_tag_already_created=True)) is False
    assert AGIcoreTradingV1OfflineTagCreationInstructionsRisk.GIT_TAG_ALREADY_CREATED in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationInstructionsDecision.REQUIRE_TAG_CREATION_INSTRUCTIONS_SAFETY_FIXES
    assert result.git_tag_created is False


def test_git_tag_command_executed():
    result = build_agicore_trading_v1_offline_tag_creation_instructions(_input(git_tag_command_executed=True))

    assert AGIcoreTradingV1OfflineTagCreationInstructionsRisk.GIT_TAG_COMMAND_EXECUTED in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationInstructionsDecision.REQUIRE_TAG_CREATION_INSTRUCTIONS_SAFETY_FIXES
    assert result.git_tag_created is False


def test_git_push_tag_executed():
    result = build_agicore_trading_v1_offline_tag_creation_instructions(_input(git_push_tag_executed=True))

    assert AGIcoreTradingV1OfflineTagCreationInstructionsRisk.GIT_TAG_PUSH_EXECUTED in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationInstructionsDecision.REQUIRE_TAG_CREATION_INSTRUCTIONS_SAFETY_FIXES
    assert result.git_tag_pushed is False


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("live_trading_overclaim", AGIcoreTradingV1OfflineTagCreationInstructionsRisk.LIVE_TRADING_READINESS_OVERCLAIM),
        ("real_broker_overclaim", AGIcoreTradingV1OfflineTagCreationInstructionsRisk.REAL_BROKER_READINESS_OVERCLAIM),
        ("real_order_overclaim", AGIcoreTradingV1OfflineTagCreationInstructionsRisk.REAL_ORDER_EXECUTION_OVERCLAIM),
        ("paper_broker_overclaim", AGIcoreTradingV1OfflineTagCreationInstructionsRisk.PAPER_BROKER_CONNECTION_OVERCLAIM),
        ("profitability_overclaim", AGIcoreTradingV1OfflineTagCreationInstructionsRisk.PROFITABILITY_PROOF_OVERCLAIM),
        ("financial_advice_overclaim", AGIcoreTradingV1OfflineTagCreationInstructionsRisk.FINANCIAL_ADVICE_OVERCLAIM),
    ),
)
def test_overclaims_are_blocked(field, risk):
    data = _input(**{field: True})
    result = build_agicore_trading_v1_offline_tag_creation_instructions(data)

    assert validate_tag_creation_instructions_no_overclaims(data) is False
    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationInstructionsDecision.REQUIRE_TAG_CREATION_INSTRUCTIONS_NO_OVERCLAIM_FIXES


def test_sections_and_markdown_helpers():
    data = _input()
    context = build_tag_creation_instructions_context(data)
    markdown = render_agicore_trading_v1_offline_tag_creation_instructions_markdown(context)

    assert len(build_tag_creation_safety_section(data)) == 10
    assert len(build_tag_creation_pre_checks_section(data)) == 5
    assert len(build_tag_creation_commands_section(data)) == 2
    assert len(build_tag_creation_post_checks_section(data)) == 3
    assert "git tag -a agicore-trading-v1-offline" in markdown
    assert "documentation" not in markdown.lower() or "Commandes proposees" in markdown
    assert validate_tag_creation_instructions_markdown(markdown)


def test_markdown_docs_valide():
    markdown = DOC_PATH.read_text(encoding="utf-8")

    assert validate_tag_creation_instructions_markdown(markdown)
    assert "instructions only, no Git tag created" in markdown
    assert "STOP avant commit" in markdown


def test_json_report():
    result = build_agicore_trading_v1_offline_tag_creation_instructions(_input())
    payload = json.loads(render_agicore_trading_v1_offline_tag_creation_instructions_json_report(result))

    assert payload["schema"] == "agicore_trading_v1_offline_tag_creation_instructions"
    assert payload["decision"] == "APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS"
    assert payload["state"] == "READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW"
    assert payload["score"] == 100
    assert payload["context"]["tag_name"] == "agicore-trading-v1-offline"
    assert payload["git_tag_created"] is False
    assert payload["git_tag_pushed"] is False
    assert payload["real_order_execution"] is False


def test_score_risks_and_recommendations_directly():
    data = _input()
    context = build_tag_creation_instructions_context(data)
    risks = detect_agicore_trading_v1_offline_tag_creation_instructions_risks(data, context)
    score = compute_agicore_trading_v1_offline_tag_creation_instructions_score(data, context, risks)
    recommendations = generate_agicore_trading_v1_offline_tag_creation_instructions_recommendations(risks)

    assert risks == ()
    assert score.overall_score == 100
    assert recommendations == (
        AGIcoreTradingV1OfflineTagCreationInstructionsRecommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW,
    )


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("file_read_requested", AGIcoreTradingV1OfflineTagCreationInstructionsRisk.FILE_READ_BOUNDARY_VIOLATION),
        ("real_data_access_requested", AGIcoreTradingV1OfflineTagCreationInstructionsRisk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_access_requested", AGIcoreTradingV1OfflineTagCreationInstructionsRisk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("broker_connection_requested", AGIcoreTradingV1OfflineTagCreationInstructionsRisk.REAL_BROKER_BOUNDARY_VIOLATION),
        ("secret_read_requested", AGIcoreTradingV1OfflineTagCreationInstructionsRisk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("network_requested", AGIcoreTradingV1OfflineTagCreationInstructionsRisk.NETWORK_BOUNDARY_VIOLATION),
        ("http_requested", AGIcoreTradingV1OfflineTagCreationInstructionsRisk.NETWORK_BOUNDARY_VIOLATION),
        ("websocket_requested", AGIcoreTradingV1OfflineTagCreationInstructionsRisk.NETWORK_BOUNDARY_VIOLATION),
        ("socket_requested", AGIcoreTradingV1OfflineTagCreationInstructionsRisk.NETWORK_BOUNDARY_VIOLATION),
        ("external_api_requested", AGIcoreTradingV1OfflineTagCreationInstructionsRisk.NETWORK_BOUNDARY_VIOLATION),
        ("order_execution_requested", AGIcoreTradingV1OfflineTagCreationInstructionsRisk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ("account_access_requested", AGIcoreTradingV1OfflineTagCreationInstructionsRisk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ("position_mutation_requested", AGIcoreTradingV1OfflineTagCreationInstructionsRisk.POSITION_MUTATION_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations_are_blocked(field, risk):
    data = _input(**{field: True})
    result = build_agicore_trading_v1_offline_tag_creation_instructions(data)

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationInstructionsDecision.REQUIRE_TAG_CREATION_INSTRUCTIONS_NO_OVERCLAIM_FIXES
    assert assert_agicore_trading_v1_offline_tag_creation_instructions_boundaries(data) is False


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


def test_no_order_account_or_position_side_effects_are_reported():
    result = build_agicore_trading_v1_offline_tag_creation_instructions(_input())

    assert result.file_read is False
    assert result.data_accessed is False
    assert result.git_tag_created is False
    assert result.git_tag_pushed is False
    assert result.real_order_submitted is False
    assert result.real_account_accessed is False
    assert result.position_mutated is False
