from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agicore.trading.agicore_trading_v1_offline_local_runbook import (
    assert_agicore_trading_v1_offline_local_runbook_boundaries,
    build_agicore_trading_v1_offline_local_runbook,
    build_local_runbook_context,
    build_local_runbook_diagnostics_section,
    build_local_runbook_git_rules_section,
    build_local_runbook_interpretation_section,
    build_local_runbook_known_limitations_section,
    build_local_runbook_next_steps_section,
    build_local_runbook_prerequisites_section,
    build_local_runbook_safety_section,
    build_local_runbook_smoke_demo_section,
    build_local_runbook_stop_procedure_section,
    build_local_runbook_sync_section,
    build_local_runbook_tests_section,
    compute_agicore_trading_v1_offline_local_runbook_score,
    detect_agicore_trading_v1_offline_local_runbook_risks,
    generate_agicore_trading_v1_offline_local_runbook_recommendations,
    render_agicore_trading_v1_offline_local_runbook_json_report,
    render_agicore_trading_v1_offline_local_runbook_markdown,
    validate_agicore_trading_v1_offline_local_runbook_input,
    validate_local_runbook_git_safety_rules,
    validate_local_runbook_markdown,
    validate_local_runbook_no_overclaims,
    validate_local_runbook_safety_language,
)
from agicore.trading.agicore_trading_v1_offline_local_runbook_models import (
    AGIcoreTradingV1OfflineLocalRunbookDecision,
    AGIcoreTradingV1OfflineLocalRunbookInput,
    AGIcoreTradingV1OfflineLocalRunbookRecommendation,
    AGIcoreTradingV1OfflineLocalRunbookRisk,
    AGIcoreTradingV1OfflineLocalRunbookState,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/agicore_trading_v1_offline_local_runbook.py"
DOC_PATH = ROOT / "docs/AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK.md"


def _input(**overrides):
    payload = {}
    payload.update(overrides)
    return AGIcoreTradingV1OfflineLocalRunbookInput(**payload)


def test_nominal_local_runbook():
    result = build_agicore_trading_v1_offline_local_runbook(_input())

    assert result.decision is AGIcoreTradingV1OfflineLocalRunbookDecision.APPROVE_AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK
    assert result.state is AGIcoreTradingV1OfflineLocalRunbookState.READY_FOR_AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_REVIEW
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert len(result.safety_rules) == 12
    assert len(result.sync_commands) == 4
    assert len(result.test_commands) == 4
    assert len(result.diagnostic_rules) == 5
    assert len(result.git_rules) == 5
    assert len(result.known_limitations) == 7
    assert validate_local_runbook_markdown(result.report.markdown)
    assert validate_local_runbook_safety_language(result.report.markdown)
    assert validate_local_runbook_git_safety_rules(result.report.markdown)
    assert validate_local_runbook_no_overclaims(result.report.markdown)


def test_input_manquant():
    result = build_agicore_trading_v1_offline_local_runbook(None)

    assert validate_agicore_trading_v1_offline_local_runbook_input(None) is False
    assert AGIcoreTradingV1OfflineLocalRunbookRisk.LOCAL_RUNBOOK_INPUT_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineLocalRunbookDecision.REQUIRE_LOCAL_RUNBOOK_INPUT_FIXES
    assert result.state is AGIcoreTradingV1OfflineLocalRunbookState.AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK_INPUT_INVALID


def test_safety_language_manquant():
    result = build_agicore_trading_v1_offline_local_runbook(_input(force_safety_language_missing=True))

    assert AGIcoreTradingV1OfflineLocalRunbookRisk.LOCAL_RUNBOOK_SAFETY_LANGUAGE_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineLocalRunbookDecision.REQUIRE_LOCAL_RUNBOOK_SAFETY_FIXES


def test_sync_commands_manquantes():
    result = build_agicore_trading_v1_offline_local_runbook(_input(force_sync_commands_missing=True))

    assert AGIcoreTradingV1OfflineLocalRunbookRisk.LOCAL_RUNBOOK_SYNC_COMMANDS_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineLocalRunbookDecision.REQUIRE_LOCAL_RUNBOOK_SYNC_FIXES


def test_test_commands_manquantes():
    result = build_agicore_trading_v1_offline_local_runbook(_input(force_test_commands_missing=True))

    assert AGIcoreTradingV1OfflineLocalRunbookRisk.LOCAL_RUNBOOK_TEST_COMMANDS_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineLocalRunbookDecision.REQUIRE_LOCAL_RUNBOOK_TEST_COMMAND_FIXES


def test_smoke_demo_section_manquante():
    result = build_agicore_trading_v1_offline_local_runbook(_input(force_smoke_demo_missing=True))

    assert AGIcoreTradingV1OfflineLocalRunbookRisk.LOCAL_RUNBOOK_SMOKE_DEMO_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineLocalRunbookDecision.REQUIRE_LOCAL_RUNBOOK_SMOKE_DEMO_FIXES


def test_interpretation_manquante():
    result = build_agicore_trading_v1_offline_local_runbook(_input(force_interpretation_missing=True))

    assert AGIcoreTradingV1OfflineLocalRunbookRisk.LOCAL_RUNBOOK_INTERPRETATION_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineLocalRunbookDecision.REQUIRE_LOCAL_RUNBOOK_INTERPRETATION_FIXES


def test_diagnostics_manquants():
    result = build_agicore_trading_v1_offline_local_runbook(_input(force_diagnostics_missing=True))

    assert AGIcoreTradingV1OfflineLocalRunbookRisk.LOCAL_RUNBOOK_DIAGNOSTICS_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineLocalRunbookDecision.REQUIRE_LOCAL_RUNBOOK_DIAGNOSTIC_FIXES


def test_git_rules_manquantes():
    result = build_agicore_trading_v1_offline_local_runbook(_input(force_git_rules_missing=True))

    assert AGIcoreTradingV1OfflineLocalRunbookRisk.LOCAL_RUNBOOK_GIT_RULES_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineLocalRunbookDecision.REQUIRE_LOCAL_RUNBOOK_GIT_RULE_FIXES


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("force_live_trading_overclaim", AGIcoreTradingV1OfflineLocalRunbookRisk.LIVE_TRADING_READINESS_OVERCLAIM),
        ("force_real_broker_overclaim", AGIcoreTradingV1OfflineLocalRunbookRisk.REAL_BROKER_READINESS_OVERCLAIM),
        ("force_real_order_overclaim", AGIcoreTradingV1OfflineLocalRunbookRisk.REAL_ORDER_EXECUTION_OVERCLAIM),
        ("force_profitability_overclaim", AGIcoreTradingV1OfflineLocalRunbookRisk.PROFITABILITY_PROOF_OVERCLAIM),
        ("force_financial_advice_overclaim", AGIcoreTradingV1OfflineLocalRunbookRisk.FINANCIAL_ADVICE_OVERCLAIM),
    ),
)
def test_overclaims_are_rejected(field, risk):
    result = build_agicore_trading_v1_offline_local_runbook(_input(**{field: True}))

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineLocalRunbookDecision.REQUIRE_LOCAL_RUNBOOK_NO_OVERCLAIM_FIXES
    assert validate_local_runbook_no_overclaims(result.report.markdown) is False


def test_markdown_genere_and_helpers():
    result = build_agicore_trading_v1_offline_local_runbook(_input())
    context = build_local_runbook_context(_input())

    assert "# AGIcore Trading v1 Offline Local Runbook" in result.report.markdown
    assert "pas de trading reel" in build_local_runbook_safety_section(result.safety_rules)
    assert "depot local propre" in build_local_runbook_prerequisites_section()
    assert "git switch main" in build_local_runbook_sync_section(result.sync_commands)
    assert "test_agicore_trading_v1_offline_smoke_demo.py" in build_local_runbook_tests_section(result.test_commands)
    assert "PYTHONPATH=src" in build_local_runbook_smoke_demo_section(_input())
    assert "APPROVE signifie seulement offline/sandbox OK" in build_local_runbook_interpretation_section(_input())
    assert "ModuleNotFoundError" in build_local_runbook_diagnostics_section(result.diagnostic_rules)
    assert "git add ." in build_local_runbook_git_rules_section(result.git_rules)
    assert "strategies simples seulement" in build_local_runbook_known_limitations_section(result.known_limitations)
    assert "data/ est staged" in build_local_runbook_stop_procedure_section()
    assert "Final Readiness Review" in build_local_runbook_next_steps_section(context)
    assert render_agicore_trading_v1_offline_local_runbook_markdown(
        context,
        result.safety_rules,
        result.sync_commands,
        result.test_commands,
        result.diagnostic_rules,
        result.git_rules,
        result.known_limitations,
        _input(),
    )


def test_markdown_docs_valide():
    markdown = DOC_PATH.read_text(encoding="utf-8")

    assert validate_local_runbook_markdown(markdown)
    assert validate_local_runbook_safety_language(markdown)
    assert validate_local_runbook_git_safety_rules(markdown)
    assert validate_local_runbook_no_overclaims(markdown)
    assert "AGIcore Trading v1 Offline Final Readiness Review" in markdown


def test_json_report():
    result = build_agicore_trading_v1_offline_local_runbook(_input())
    payload = json.loads(render_agicore_trading_v1_offline_local_runbook_json_report(result))

    assert payload["schema"] == "agicore_trading_v1_offline_local_runbook"
    assert payload["decision"] == "APPROVE_AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK"
    assert payload["score"] == 100
    assert payload["live_trading_ready"] is False
    assert payload["real_broker_ready"] is False
    assert payload["real_order_execution"] is False
    assert payload["profitability_proven"] is False
    assert payload["financial_advice"] is False


def test_score_risks_and_recommendations_directly():
    result = build_agicore_trading_v1_offline_local_runbook(_input())
    risks = detect_agicore_trading_v1_offline_local_runbook_risks(
        _input(),
        result.report.markdown,
        result.sync_commands,
        result.test_commands,
        result.safety_rules,
        result.diagnostic_rules,
        result.git_rules,
    )
    score = compute_agicore_trading_v1_offline_local_runbook_score(
        _input(),
        result.report.markdown,
        result.sync_commands,
        result.test_commands,
        result.safety_rules,
        result.diagnostic_rules,
        result.git_rules,
        risks,
    )
    recommendations = generate_agicore_trading_v1_offline_local_runbook_recommendations(risks)

    assert risks == ()
    assert score.overall_score == 100
    assert recommendations == (
        AGIcoreTradingV1OfflineLocalRunbookRecommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_REVIEW,
    )


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("file_read_requested", AGIcoreTradingV1OfflineLocalRunbookRisk.FILE_READ_BOUNDARY_VIOLATION),
        ("real_data_access_requested", AGIcoreTradingV1OfflineLocalRunbookRisk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_access_requested", AGIcoreTradingV1OfflineLocalRunbookRisk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("broker_connection_requested", AGIcoreTradingV1OfflineLocalRunbookRisk.REAL_BROKER_BOUNDARY_VIOLATION),
        ("secret_read_requested", AGIcoreTradingV1OfflineLocalRunbookRisk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("network_requested", AGIcoreTradingV1OfflineLocalRunbookRisk.NETWORK_BOUNDARY_VIOLATION),
        ("http_requested", AGIcoreTradingV1OfflineLocalRunbookRisk.NETWORK_BOUNDARY_VIOLATION),
        ("websocket_requested", AGIcoreTradingV1OfflineLocalRunbookRisk.NETWORK_BOUNDARY_VIOLATION),
        ("socket_requested", AGIcoreTradingV1OfflineLocalRunbookRisk.NETWORK_BOUNDARY_VIOLATION),
        ("external_api_requested", AGIcoreTradingV1OfflineLocalRunbookRisk.NETWORK_BOUNDARY_VIOLATION),
        ("order_execution_requested", AGIcoreTradingV1OfflineLocalRunbookRisk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ("account_access_requested", AGIcoreTradingV1OfflineLocalRunbookRisk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ("position_mutation_requested", AGIcoreTradingV1OfflineLocalRunbookRisk.POSITION_MUTATION_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations_are_blocked(field, risk):
    data = _input(**{field: True})
    result = build_agicore_trading_v1_offline_local_runbook(data)

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineLocalRunbookDecision.BLOCK_AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK
    assert assert_agicore_trading_v1_offline_local_runbook_boundaries(data) is False


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
    result = build_agicore_trading_v1_offline_local_runbook(_input())

    assert result.file_read is False
    assert result.data_accessed is False
    assert result.real_order_submitted is False
    assert result.real_account_accessed is False
    assert result.position_mutated is False
