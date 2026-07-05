from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agicore.trading.agicore_trading_v1_offline_sandbox_usage_guide import (
    assert_agicore_trading_v1_offline_sandbox_usage_guide_boundaries,
    build_agicore_trading_v1_offline_sandbox_usage_guide,
    build_sandbox_usage_guide_commands_section,
    build_sandbox_usage_guide_context,
    build_sandbox_usage_guide_known_limitations_section,
    build_sandbox_usage_guide_memory_usage_example_section,
    build_sandbox_usage_guide_next_steps_section,
    build_sandbox_usage_guide_prerequisites_section,
    build_sandbox_usage_guide_result_interpretation_section,
    build_sandbox_usage_guide_safety_section,
    build_sandbox_usage_guide_workflow_section,
    compute_agicore_trading_v1_offline_sandbox_usage_guide_score,
    detect_agicore_trading_v1_offline_sandbox_usage_guide_risks,
    generate_agicore_trading_v1_offline_sandbox_usage_guide_recommendations,
    render_agicore_trading_v1_offline_sandbox_usage_guide_json_report,
    render_agicore_trading_v1_offline_sandbox_usage_guide_markdown,
    validate_agicore_trading_v1_offline_sandbox_usage_guide_input,
    validate_sandbox_usage_guide_markdown,
    validate_sandbox_usage_guide_no_overclaims,
    validate_sandbox_usage_guide_safety_language,
)
from agicore.trading.agicore_trading_v1_offline_sandbox_usage_guide_models import (
    AGIcoreTradingV1OfflineSandboxUsageGuideDecision,
    AGIcoreTradingV1OfflineSandboxUsageGuideInput,
    AGIcoreTradingV1OfflineSandboxUsageGuideRecommendation,
    AGIcoreTradingV1OfflineSandboxUsageGuideRisk,
    AGIcoreTradingV1OfflineSandboxUsageGuideState,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/agicore_trading_v1_offline_sandbox_usage_guide.py"
DOC_PATH = ROOT / "docs/AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE.md"


def _input(**overrides):
    payload = {}
    payload.update(overrides)
    return AGIcoreTradingV1OfflineSandboxUsageGuideInput(**payload)


def test_nominal_sandbox_usage_guide():
    result = build_agicore_trading_v1_offline_sandbox_usage_guide(_input())

    assert result.decision is AGIcoreTradingV1OfflineSandboxUsageGuideDecision.APPROVE_AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE
    assert result.state is AGIcoreTradingV1OfflineSandboxUsageGuideState.READY_FOR_AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert len(result.commands) == 3
    assert len(result.safety_rules) == 12
    assert len(result.known_limitations) == 7
    assert validate_sandbox_usage_guide_markdown(result.report.markdown)
    assert validate_sandbox_usage_guide_safety_language(result.report.markdown)
    assert validate_sandbox_usage_guide_no_overclaims(result.report.markdown)


def test_input_manquant():
    result = build_agicore_trading_v1_offline_sandbox_usage_guide(None)

    assert validate_agicore_trading_v1_offline_sandbox_usage_guide_input(None) is False
    assert AGIcoreTradingV1OfflineSandboxUsageGuideRisk.SANDBOX_USAGE_GUIDE_INPUT_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineSandboxUsageGuideDecision.REQUIRE_SANDBOX_USAGE_GUIDE_INPUT_FIXES
    assert result.state is AGIcoreTradingV1OfflineSandboxUsageGuideState.AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE_INPUT_INVALID


def test_safety_language_manquant():
    result = build_agicore_trading_v1_offline_sandbox_usage_guide(_input(force_safety_language_missing=True))

    assert AGIcoreTradingV1OfflineSandboxUsageGuideRisk.SANDBOX_USAGE_GUIDE_SAFETY_LANGUAGE_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineSandboxUsageGuideDecision.REQUIRE_SANDBOX_USAGE_GUIDE_SAFETY_FIXES


def test_commands_manquantes():
    result = build_agicore_trading_v1_offline_sandbox_usage_guide(_input(force_commands_missing=True))

    assert AGIcoreTradingV1OfflineSandboxUsageGuideRisk.SANDBOX_USAGE_GUIDE_COMMANDS_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineSandboxUsageGuideDecision.REQUIRE_SANDBOX_USAGE_GUIDE_COMMAND_FIXES


def test_memory_example_manquant():
    result = build_agicore_trading_v1_offline_sandbox_usage_guide(_input(force_memory_example_missing=True))

    assert AGIcoreTradingV1OfflineSandboxUsageGuideRisk.SANDBOX_USAGE_GUIDE_MEMORY_EXAMPLE_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineSandboxUsageGuideDecision.REQUIRE_SANDBOX_USAGE_GUIDE_MEMORY_EXAMPLE_FIXES


def test_result_interpretation_manquant():
    result = build_agicore_trading_v1_offline_sandbox_usage_guide(_input(force_result_interpretation_missing=True))

    assert AGIcoreTradingV1OfflineSandboxUsageGuideRisk.SANDBOX_USAGE_GUIDE_RESULT_INTERPRETATION_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineSandboxUsageGuideDecision.REQUIRE_SANDBOX_USAGE_GUIDE_INTERPRETATION_FIXES


def test_limitations_manquantes():
    result = build_agicore_trading_v1_offline_sandbox_usage_guide(_input(force_limitations_missing=True))

    assert AGIcoreTradingV1OfflineSandboxUsageGuideRisk.SANDBOX_USAGE_GUIDE_LIMITATIONS_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineSandboxUsageGuideDecision.REQUIRE_SANDBOX_USAGE_GUIDE_LIMITATION_FIXES


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("force_live_trading_overclaim", AGIcoreTradingV1OfflineSandboxUsageGuideRisk.LIVE_TRADING_READINESS_OVERCLAIM),
        ("force_real_broker_overclaim", AGIcoreTradingV1OfflineSandboxUsageGuideRisk.REAL_BROKER_READINESS_OVERCLAIM),
        ("force_real_order_overclaim", AGIcoreTradingV1OfflineSandboxUsageGuideRisk.REAL_ORDER_EXECUTION_OVERCLAIM),
        ("force_profitability_overclaim", AGIcoreTradingV1OfflineSandboxUsageGuideRisk.PROFITABILITY_PROOF_OVERCLAIM),
        ("force_financial_advice_overclaim", AGIcoreTradingV1OfflineSandboxUsageGuideRisk.FINANCIAL_ADVICE_OVERCLAIM),
    ),
)
def test_overclaims_are_rejected(field, risk):
    result = build_agicore_trading_v1_offline_sandbox_usage_guide(_input(**{field: True}))

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineSandboxUsageGuideDecision.REQUIRE_SANDBOX_USAGE_GUIDE_NO_OVERCLAIM_FIXES
    assert validate_sandbox_usage_guide_no_overclaims(result.report.markdown) is False


def test_markdown_genere_and_helpers():
    result = build_agicore_trading_v1_offline_sandbox_usage_guide(_input())
    context = build_sandbox_usage_guide_context(_input())

    assert "# AGIcore Trading v1 Offline Sandbox Usage Guide" in result.report.markdown
    assert "pas de trading reel" in build_sandbox_usage_guide_safety_section(result.safety_rules)
    assert "etre sur main a jour" in build_sandbox_usage_guide_prerequisites_section()
    assert "test_agicore_trading_v1_offline_smoke_demo.py" in build_sandbox_usage_guide_commands_section(result.commands)
    assert "PYTHONPATH=src" in build_sandbox_usage_guide_memory_usage_example_section(_input())
    assert "APPROVE signifie seulement sandbox/offline OK" in build_sandbox_usage_guide_result_interpretation_section(_input())
    assert "strategies simples seulement" in build_sandbox_usage_guide_known_limitations_section(result.known_limitations)
    assert "lancer les tests" in build_sandbox_usage_guide_workflow_section()
    assert "Offline Local Runbook" in build_sandbox_usage_guide_next_steps_section(context)
    assert render_agicore_trading_v1_offline_sandbox_usage_guide_markdown(
        context,
        result.safety_rules,
        result.commands,
        result.known_limitations,
        _input(),
    )


def test_markdown_docs_valide():
    markdown = DOC_PATH.read_text(encoding="utf-8")

    assert validate_sandbox_usage_guide_markdown(markdown)
    assert validate_sandbox_usage_guide_safety_language(markdown)
    assert validate_sandbox_usage_guide_no_overclaims(markdown)
    assert "AGIcore Trading v1 Offline Local Runbook" in markdown


def test_json_report():
    result = build_agicore_trading_v1_offline_sandbox_usage_guide(_input())
    payload = json.loads(render_agicore_trading_v1_offline_sandbox_usage_guide_json_report(result))

    assert payload["schema"] == "agicore_trading_v1_offline_sandbox_usage_guide"
    assert payload["decision"] == "APPROVE_AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE"
    assert payload["score"] == 100
    assert payload["live_trading_ready"] is False
    assert payload["real_broker_ready"] is False
    assert payload["real_order_execution"] is False
    assert payload["profitability_proven"] is False
    assert payload["financial_advice"] is False


def test_score_risks_and_recommendations_directly():
    result = build_agicore_trading_v1_offline_sandbox_usage_guide(_input())
    risks = detect_agicore_trading_v1_offline_sandbox_usage_guide_risks(
        _input(),
        result.report.markdown,
        result.commands,
        result.safety_rules,
        result.known_limitations,
    )
    score = compute_agicore_trading_v1_offline_sandbox_usage_guide_score(
        _input(),
        result.report.markdown,
        result.commands,
        result.safety_rules,
        result.known_limitations,
        risks,
    )
    recommendations = generate_agicore_trading_v1_offline_sandbox_usage_guide_recommendations(risks)

    assert risks == ()
    assert score.overall_score == 100
    assert recommendations == (
        AGIcoreTradingV1OfflineSandboxUsageGuideRecommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK,
    )


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("file_read_requested", AGIcoreTradingV1OfflineSandboxUsageGuideRisk.FILE_READ_BOUNDARY_VIOLATION),
        ("real_data_access_requested", AGIcoreTradingV1OfflineSandboxUsageGuideRisk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_access_requested", AGIcoreTradingV1OfflineSandboxUsageGuideRisk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("broker_connection_requested", AGIcoreTradingV1OfflineSandboxUsageGuideRisk.REAL_BROKER_BOUNDARY_VIOLATION),
        ("secret_read_requested", AGIcoreTradingV1OfflineSandboxUsageGuideRisk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("network_requested", AGIcoreTradingV1OfflineSandboxUsageGuideRisk.NETWORK_BOUNDARY_VIOLATION),
        ("http_requested", AGIcoreTradingV1OfflineSandboxUsageGuideRisk.NETWORK_BOUNDARY_VIOLATION),
        ("websocket_requested", AGIcoreTradingV1OfflineSandboxUsageGuideRisk.NETWORK_BOUNDARY_VIOLATION),
        ("socket_requested", AGIcoreTradingV1OfflineSandboxUsageGuideRisk.NETWORK_BOUNDARY_VIOLATION),
        ("external_api_requested", AGIcoreTradingV1OfflineSandboxUsageGuideRisk.NETWORK_BOUNDARY_VIOLATION),
        ("order_execution_requested", AGIcoreTradingV1OfflineSandboxUsageGuideRisk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ("account_access_requested", AGIcoreTradingV1OfflineSandboxUsageGuideRisk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ("position_mutation_requested", AGIcoreTradingV1OfflineSandboxUsageGuideRisk.POSITION_MUTATION_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations_are_blocked(field, risk):
    data = _input(**{field: True})
    result = build_agicore_trading_v1_offline_sandbox_usage_guide(data)

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineSandboxUsageGuideDecision.BLOCK_AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE
    assert assert_agicore_trading_v1_offline_sandbox_usage_guide_boundaries(data) is False


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


def test_no_real_secret_environment_read():
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert all(alias.name != "os" for alias in node.names)
        if isinstance(node, ast.Attribute):
            assert node.attr not in {"environ", "getenv"}
        if isinstance(node, ast.Call):
            assert getattr(node.func, "attr", "") != "getenv"


def test_no_order_account_or_position_side_effects_are_reported():
    result = build_agicore_trading_v1_offline_sandbox_usage_guide(_input())

    assert result.file_read is False
    assert result.data_accessed is False
    assert result.real_order_submitted is False
    assert result.real_account_accessed is False
    assert result.position_mutated is False
