from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agicore.trading.agicore_trading_v1_offline_tag_creation_instructions_review import (
    assert_agicore_trading_v1_offline_tag_creation_instructions_review_boundaries,
    build_tag_creation_instructions_review_context,
    compute_agicore_trading_v1_offline_tag_creation_instructions_review_score,
    detect_agicore_trading_v1_offline_tag_creation_instructions_review_risks,
    generate_agicore_trading_v1_offline_tag_creation_instructions_review_recommendations,
    render_agicore_trading_v1_offline_tag_creation_instructions_review_json_report,
    render_agicore_trading_v1_offline_tag_creation_instructions_review_markdown,
    review_agicore_trading_v1_offline_tag_creation_instructions,
    review_tag_creation_documented_commands_only,
    review_tag_creation_human_guardrails,
    review_tag_creation_instructions_approval,
    review_tag_creation_instructions_document,
    review_tag_creation_instructions_tag_name,
    review_tag_creation_instructions_version,
    review_tag_creation_no_financial_advice_claim,
    review_tag_creation_no_git_tag_created,
    review_tag_creation_no_git_tag_pushed,
    review_tag_creation_no_live_trading_claim,
    review_tag_creation_no_profitability_claim,
    review_tag_creation_post_checks,
    review_tag_creation_pre_checks,
    validate_agicore_trading_v1_offline_tag_creation_instructions_review_input,
    validate_tag_creation_instructions_review_markdown,
)
from agicore.trading.agicore_trading_v1_offline_tag_creation_instructions_review_models import (
    AGIcoreTradingV1OfflineTagCreationInstructionsReviewDecision,
    AGIcoreTradingV1OfflineTagCreationInstructionsReviewInput,
    AGIcoreTradingV1OfflineTagCreationInstructionsReviewRecommendation,
    AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk,
    AGIcoreTradingV1OfflineTagCreationInstructionsReviewState,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/agicore_trading_v1_offline_tag_creation_instructions_review.py"
DOC_PATH = ROOT / "docs/AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW.md"


def _input(**overrides):
    payload = {}
    payload.update(overrides)
    return AGIcoreTradingV1OfflineTagCreationInstructionsReviewInput(**payload)


def test_nominal_tag_creation_instructions_review():
    result = review_agicore_trading_v1_offline_tag_creation_instructions(_input())

    assert result.decision is AGIcoreTradingV1OfflineTagCreationInstructionsReviewDecision.APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW
    assert result.state is AGIcoreTradingV1OfflineTagCreationInstructionsReviewState.READY_FOR_AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.git_tag_created is False
    assert result.git_tag_pushed is False
    assert result.context.prerequisite_decision == "APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS"
    assert result.context.tag_metadata.tag_name == "agicore-trading-v1-offline"
    assert result.context.tag_metadata.version == "v1.0.0-offline"
    assert validate_tag_creation_instructions_review_markdown(result.report.markdown)


def test_input_manquant():
    result = review_agicore_trading_v1_offline_tag_creation_instructions(None)

    assert validate_agicore_trading_v1_offline_tag_creation_instructions_review_input(None) is False
    assert AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk.TAG_CREATION_INSTRUCTIONS_REVIEW_INPUT_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationInstructionsReviewDecision.REQUIRE_TAG_CREATION_INSTRUCTIONS_REVIEW_INPUT_FIXES
    assert result.state is AGIcoreTradingV1OfflineTagCreationInstructionsReviewState.AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW_INPUT_INVALID


def test_instructions_non_approuvees():
    result = review_agicore_trading_v1_offline_tag_creation_instructions(_input(instructions_approved=False))

    assert review_tag_creation_instructions_approval(_input(instructions_approved=False)) is False
    assert AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk.TAG_CREATION_INSTRUCTIONS_NOT_APPROVED in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationInstructionsReviewDecision.REQUIRE_TAG_CREATION_INSTRUCTIONS_FIXES


def test_document_manquant():
    result = review_agicore_trading_v1_offline_tag_creation_instructions(_input(instructions_document_present=False))

    assert review_tag_creation_instructions_document(_input(instructions_document_present=False)) is False
    assert AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk.TAG_CREATION_INSTRUCTIONS_DOCUMENT_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationInstructionsReviewDecision.REQUIRE_TAG_CREATION_INSTRUCTIONS_FIXES


def test_tag_name_invalide():
    result = review_agicore_trading_v1_offline_tag_creation_instructions(_input(tag_name="bad"))

    assert review_tag_creation_instructions_tag_name(_input(tag_name="bad")) is False
    assert AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk.TAG_CREATION_TAG_NAME_INVALID in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationInstructionsReviewDecision.REQUIRE_TAG_CREATION_TAG_NAME_FIXES


def test_version_invalide():
    result = review_agicore_trading_v1_offline_tag_creation_instructions(_input(version="v1-live"))

    assert review_tag_creation_instructions_version(_input(version="v1-live")) is False
    assert AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk.TAG_CREATION_VERSION_INVALID in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationInstructionsReviewDecision.REQUIRE_TAG_CREATION_VERSION_FIXES


def test_pre_checks_manquants():
    data = _input(pre_checks_present=False)
    context = build_tag_creation_instructions_review_context(data)
    result = review_agicore_trading_v1_offline_tag_creation_instructions(data)

    assert review_tag_creation_pre_checks(context) is False
    assert AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk.TAG_CREATION_PRE_CHECKS_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationInstructionsReviewDecision.REQUIRE_TAG_CREATION_PRE_CHECK_FIXES


def test_commands_non_documentation_only():
    data = _input(commands_documentation_only=False)
    context = build_tag_creation_instructions_review_context(data)
    result = review_agicore_trading_v1_offline_tag_creation_instructions(data)

    assert review_tag_creation_documented_commands_only(context) is False
    assert AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk.TAG_CREATION_COMMANDS_NOT_DOCUMENTATION_ONLY in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationInstructionsReviewDecision.REQUIRE_TAG_CREATION_COMMAND_DOCUMENTATION_FIXES


def test_post_checks_manquants():
    data = _input(post_checks_present=False)
    context = build_tag_creation_instructions_review_context(data)
    result = review_agicore_trading_v1_offline_tag_creation_instructions(data)

    assert review_tag_creation_post_checks(context) is False
    assert AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk.TAG_CREATION_POST_CHECKS_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationInstructionsReviewDecision.REQUIRE_TAG_CREATION_COMMAND_DOCUMENTATION_FIXES


def test_human_guardrails_manquants():
    data = _input(human_guardrails_present=False)
    context = build_tag_creation_instructions_review_context(data)
    result = review_agicore_trading_v1_offline_tag_creation_instructions(data)

    assert review_tag_creation_human_guardrails(context) is False
    assert AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk.TAG_CREATION_HUMAN_GUARDRAILS_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationInstructionsReviewDecision.REQUIRE_TAG_CREATION_HUMAN_GUARDRAIL_FIXES


def test_git_tag_already_created():
    result = review_agicore_trading_v1_offline_tag_creation_instructions(_input(git_tag_already_created=True))

    assert review_tag_creation_no_git_tag_created(_input(git_tag_already_created=True)) is False
    assert AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk.GIT_TAG_ALREADY_CREATED in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationInstructionsReviewDecision.REQUIRE_TAG_CREATION_NO_OVERCLAIM_FIXES
    assert result.git_tag_created is False


def test_git_tag_already_pushed():
    result = review_agicore_trading_v1_offline_tag_creation_instructions(_input(git_tag_already_pushed=True))

    assert review_tag_creation_no_git_tag_pushed(_input(git_tag_already_pushed=True)) is False
    assert AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk.GIT_TAG_ALREADY_PUSHED in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationInstructionsReviewDecision.REQUIRE_TAG_CREATION_NO_OVERCLAIM_FIXES
    assert result.git_tag_pushed is False


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("live_trading_overclaim", AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk.LIVE_TRADING_READINESS_OVERCLAIM),
        ("real_broker_overclaim", AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk.REAL_BROKER_READINESS_OVERCLAIM),
        ("real_order_overclaim", AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk.REAL_ORDER_EXECUTION_OVERCLAIM),
        ("paper_broker_overclaim", AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk.PAPER_BROKER_CONNECTION_OVERCLAIM),
        ("profitability_overclaim", AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk.PROFITABILITY_PROOF_OVERCLAIM),
        ("financial_advice_overclaim", AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk.FINANCIAL_ADVICE_OVERCLAIM),
    ),
)
def test_overclaims_are_blocked(field, risk):
    result = review_agicore_trading_v1_offline_tag_creation_instructions(_input(**{field: True}))

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationInstructionsReviewDecision.REQUIRE_TAG_CREATION_NO_OVERCLAIM_FIXES


def test_no_overclaim_helpers():
    assert review_tag_creation_no_live_trading_claim(_input()) is True
    assert review_tag_creation_no_live_trading_claim(_input(live_trading_overclaim=True)) is False
    assert review_tag_creation_no_profitability_claim(_input()) is True
    assert review_tag_creation_no_profitability_claim(_input(profitability_overclaim=True)) is False
    assert review_tag_creation_no_financial_advice_claim(_input()) is True
    assert review_tag_creation_no_financial_advice_claim(_input(financial_advice_overclaim=True)) is False


def test_markdown_genere():
    data = _input()
    context = build_tag_creation_instructions_review_context(data)
    result = review_agicore_trading_v1_offline_tag_creation_instructions(data)
    markdown = render_agicore_trading_v1_offline_tag_creation_instructions_review_markdown(context, result.findings)

    assert "AGIcore Trading v1 Offline Tag Creation Instructions Review" in markdown
    assert "git tag -a agicore-trading-v1-offline" in markdown
    assert "validation explicite de Bama" in markdown
    assert validate_tag_creation_instructions_review_markdown(markdown)


def test_markdown_docs_valide():
    markdown = DOC_PATH.read_text(encoding="utf-8")

    assert validate_tag_creation_instructions_review_markdown(markdown)
    assert "AGIcore Trading v1 Offline Human Tag Go/No-Go" in markdown


def test_json_report():
    result = review_agicore_trading_v1_offline_tag_creation_instructions(_input())
    payload = json.loads(render_agicore_trading_v1_offline_tag_creation_instructions_review_json_report(result))

    assert payload["schema"] == "agicore_trading_v1_offline_tag_creation_instructions_review"
    assert payload["decision"] == "APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW"
    assert payload["state"] == "READY_FOR_AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO"
    assert payload["score"] == 100
    assert payload["git_tag_created"] is False
    assert payload["git_tag_pushed"] is False
    assert payload["real_order_execution"] is False


def test_score_risks_and_recommendations_directly():
    data = _input()
    context = build_tag_creation_instructions_review_context(data)
    risks = detect_agicore_trading_v1_offline_tag_creation_instructions_review_risks(data, context)
    score = compute_agicore_trading_v1_offline_tag_creation_instructions_review_score(data, context, risks)
    recommendations = generate_agicore_trading_v1_offline_tag_creation_instructions_review_recommendations(risks)

    assert risks == ()
    assert score.overall_score == 100
    assert recommendations == (
        AGIcoreTradingV1OfflineTagCreationInstructionsReviewRecommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO,
    )


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("file_read_requested", AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk.FILE_READ_BOUNDARY_VIOLATION),
        ("real_data_access_requested", AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_access_requested", AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("broker_connection_requested", AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk.REAL_BROKER_BOUNDARY_VIOLATION),
        ("secret_read_requested", AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("network_requested", AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("http_requested", AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("websocket_requested", AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("socket_requested", AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("external_api_requested", AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk.NETWORK_BOUNDARY_VIOLATION),
        ("order_execution_requested", AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ("account_access_requested", AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ("position_mutation_requested", AGIcoreTradingV1OfflineTagCreationInstructionsReviewRisk.POSITION_MUTATION_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations_are_blocked(field, risk):
    data = _input(**{field: True})
    result = review_agicore_trading_v1_offline_tag_creation_instructions(data)

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagCreationInstructionsReviewDecision.REQUIRE_TAG_CREATION_NO_OVERCLAIM_FIXES
    assert assert_agicore_trading_v1_offline_tag_creation_instructions_review_boundaries(data) is False


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
    result = review_agicore_trading_v1_offline_tag_creation_instructions(_input())

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
