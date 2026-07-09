from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agicore.trading.agicore_trading_v1_offline_release_package import (
    assert_agicore_trading_v1_offline_release_package_boundaries,
    build_agicore_trading_v1_offline_release_package,
    build_release_package_capabilities_section,
    build_release_package_commands_section,
    build_release_package_context,
    build_release_package_documents_section,
    build_release_package_known_limitations_section,
    build_release_package_next_steps_section,
    build_release_package_non_goals_section,
    build_release_package_safety_rules_section,
    build_release_package_summary_section,
    build_release_package_testing_evidence_section,
    compute_agicore_trading_v1_offline_release_package_score,
    detect_agicore_trading_v1_offline_release_package_risks,
    generate_agicore_trading_v1_offline_release_package_recommendations,
    render_agicore_trading_v1_offline_release_package_json_report,
    render_agicore_trading_v1_offline_release_package_markdown,
    validate_agicore_trading_v1_offline_release_package_input,
    validate_release_package_markdown,
    validate_release_package_no_overclaims,
    validate_release_package_safety_language,
)
from agicore.trading.agicore_trading_v1_offline_release_package_models import (
    AGIcoreTradingV1OfflineReleasePackageDecision,
    AGIcoreTradingV1OfflineReleasePackageInput,
    AGIcoreTradingV1OfflineReleasePackageRecommendation,
    AGIcoreTradingV1OfflineReleasePackageRisk,
    AGIcoreTradingV1OfflineReleasePackageState,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/agicore_trading_v1_offline_release_package.py"
DOC_PATH = ROOT / "docs/AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE.md"


def _input(**overrides):
    payload = {}
    payload.update(overrides)
    return AGIcoreTradingV1OfflineReleasePackageInput(**payload)


def test_nominal_release_package():
    result = build_agicore_trading_v1_offline_release_package(_input())

    assert result.decision is AGIcoreTradingV1OfflineReleasePackageDecision.APPROVE_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE
    assert result.state is AGIcoreTradingV1OfflineReleasePackageState.READY_FOR_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert len(result.documents) == 4
    assert len(result.capabilities) == 9
    assert len(result.testing_evidence) == 4
    assert len(result.commands) == 3
    assert len(result.safety_rules) == 6
    assert len(result.known_limitations) == 7
    assert len(result.non_goals) == 6
    assert validate_release_package_markdown(result.report.markdown)
    assert validate_release_package_safety_language(result.report.markdown)
    assert validate_release_package_no_overclaims(result.report.markdown)


def test_input_manquant():
    result = build_agicore_trading_v1_offline_release_package(None)

    assert validate_agicore_trading_v1_offline_release_package_input(None) is False
    assert AGIcoreTradingV1OfflineReleasePackageRisk.RELEASE_PACKAGE_INPUT_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleasePackageDecision.REQUIRE_RELEASE_PACKAGE_INPUT_FIXES
    assert result.state is AGIcoreTradingV1OfflineReleasePackageState.AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_INPUT_INVALID


def test_documents_manquants():
    result = build_agicore_trading_v1_offline_release_package(_input(force_documents_missing=True))

    assert AGIcoreTradingV1OfflineReleasePackageRisk.RELEASE_PACKAGE_DOCUMENTS_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleasePackageDecision.REQUIRE_RELEASE_PACKAGE_DOCUMENT_FIXES


def test_capabilities_manquantes():
    result = build_agicore_trading_v1_offline_release_package(_input(force_capabilities_missing=True))

    assert AGIcoreTradingV1OfflineReleasePackageRisk.RELEASE_PACKAGE_CAPABILITIES_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleasePackageDecision.REQUIRE_RELEASE_PACKAGE_CAPABILITY_FIXES


def test_testing_evidence_manquante():
    result = build_agicore_trading_v1_offline_release_package(_input(force_testing_evidence_missing=True))

    assert AGIcoreTradingV1OfflineReleasePackageRisk.RELEASE_PACKAGE_TESTING_EVIDENCE_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleasePackageDecision.REQUIRE_RELEASE_PACKAGE_TESTING_EVIDENCE_FIXES


def test_commands_manquantes():
    result = build_agicore_trading_v1_offline_release_package(_input(force_commands_missing=True))

    assert AGIcoreTradingV1OfflineReleasePackageRisk.RELEASE_PACKAGE_COMMANDS_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleasePackageDecision.REQUIRE_RELEASE_PACKAGE_COMMAND_FIXES


def test_safety_language_manquant():
    result = build_agicore_trading_v1_offline_release_package(_input(force_safety_language_missing=True))

    assert AGIcoreTradingV1OfflineReleasePackageRisk.RELEASE_PACKAGE_SAFETY_LANGUAGE_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleasePackageDecision.REQUIRE_RELEASE_PACKAGE_SAFETY_FIXES


def test_limitations_manquantes():
    result = build_agicore_trading_v1_offline_release_package(_input(force_limitations_missing=True))

    assert AGIcoreTradingV1OfflineReleasePackageRisk.RELEASE_PACKAGE_LIMITATIONS_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleasePackageDecision.REQUIRE_RELEASE_PACKAGE_LIMITATION_FIXES


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("force_live_trading_overclaim", AGIcoreTradingV1OfflineReleasePackageRisk.LIVE_TRADING_READINESS_OVERCLAIM),
        ("force_real_broker_overclaim", AGIcoreTradingV1OfflineReleasePackageRisk.REAL_BROKER_READINESS_OVERCLAIM),
        ("force_real_order_overclaim", AGIcoreTradingV1OfflineReleasePackageRisk.REAL_ORDER_EXECUTION_OVERCLAIM),
        ("force_paper_broker_overclaim", AGIcoreTradingV1OfflineReleasePackageRisk.PAPER_BROKER_CONNECTION_OVERCLAIM),
        ("force_profitability_overclaim", AGIcoreTradingV1OfflineReleasePackageRisk.PROFITABILITY_PROOF_OVERCLAIM),
        ("force_financial_advice_overclaim", AGIcoreTradingV1OfflineReleasePackageRisk.FINANCIAL_ADVICE_OVERCLAIM),
    ),
)
def test_overclaims_are_rejected(field, risk):
    result = build_agicore_trading_v1_offline_release_package(_input(**{field: True}))

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleasePackageDecision.REQUIRE_RELEASE_PACKAGE_NO_OVERCLAIM_FIXES
    assert validate_release_package_no_overclaims(result.report.markdown) is False


def test_markdown_genere_and_helpers():
    result = build_agicore_trading_v1_offline_release_package(_input())
    context = build_release_package_context(_input())

    assert "# AGIcore Trading v1 Offline Release Package" in result.report.markdown
    assert "utilisable localement en sandbox" in build_release_package_summary_section()
    assert "AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES.md" in build_release_package_documents_section(result.documents)
    assert "CSV Replay Input v1" in build_release_package_capabilities_section(result.capabilities)
    assert "final readiness test : 37 passed" in build_release_package_testing_evidence_section(result.testing_evidence)
    assert "test_agicore_trading_v1_offline_smoke_demo.py" in build_release_package_commands_section(result.commands)
    assert "ne jamais connecter de broker reel" in build_release_package_safety_rules_section(result.safety_rules)
    assert "strategies simples seulement" in build_release_package_known_limitations_section(result.known_limitations)
    assert "pas de trading reel" in build_release_package_non_goals_section(result.non_goals)
    assert "Release Package Review" in build_release_package_next_steps_section(context)
    assert render_agicore_trading_v1_offline_release_package_markdown(
        context,
        result.documents,
        result.capabilities,
        result.testing_evidence,
        result.commands,
        result.safety_rules,
        result.known_limitations,
        result.non_goals,
    )


def test_markdown_docs_valide():
    markdown = DOC_PATH.read_text(encoding="utf-8")

    assert validate_release_package_markdown(markdown)
    assert validate_release_package_safety_language(markdown)
    assert validate_release_package_no_overclaims(markdown)
    assert "AGIcore Trading v1 Offline Release Package Review" in markdown


def test_json_report():
    result = build_agicore_trading_v1_offline_release_package(_input())
    payload = json.loads(render_agicore_trading_v1_offline_release_package_json_report(result))

    assert payload["schema"] == "agicore_trading_v1_offline_release_package"
    assert payload["decision"] == "APPROVE_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE"
    assert payload["score"] == 100
    assert payload["live_trading_ready"] is False
    assert payload["real_broker_ready"] is False
    assert payload["real_order_execution"] is False
    assert payload["paper_broker_connected"] is False
    assert payload["profitability_proven"] is False
    assert payload["financial_advice"] is False


def test_score_risks_and_recommendations_directly():
    result = build_agicore_trading_v1_offline_release_package(_input())
    risks = detect_agicore_trading_v1_offline_release_package_risks(
        _input(),
        result.report.markdown,
        result.documents,
        result.capabilities,
        result.testing_evidence,
        result.commands,
        result.safety_rules,
        result.known_limitations,
    )
    score = compute_agicore_trading_v1_offline_release_package_score(
        _input(),
        result.report.markdown,
        result.documents,
        result.capabilities,
        result.testing_evidence,
        result.commands,
        result.safety_rules,
        result.known_limitations,
        result.non_goals,
        risks,
    )
    recommendations = generate_agicore_trading_v1_offline_release_package_recommendations(risks)

    assert risks == ()
    assert score.overall_score == 100
    assert recommendations == (
        AGIcoreTradingV1OfflineReleasePackageRecommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW,
    )


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("file_read_requested", AGIcoreTradingV1OfflineReleasePackageRisk.FILE_READ_BOUNDARY_VIOLATION),
        ("real_data_access_requested", AGIcoreTradingV1OfflineReleasePackageRisk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_access_requested", AGIcoreTradingV1OfflineReleasePackageRisk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("broker_connection_requested", AGIcoreTradingV1OfflineReleasePackageRisk.REAL_BROKER_BOUNDARY_VIOLATION),
        ("secret_read_requested", AGIcoreTradingV1OfflineReleasePackageRisk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("network_requested", AGIcoreTradingV1OfflineReleasePackageRisk.NETWORK_BOUNDARY_VIOLATION),
        ("http_requested", AGIcoreTradingV1OfflineReleasePackageRisk.NETWORK_BOUNDARY_VIOLATION),
        ("websocket_requested", AGIcoreTradingV1OfflineReleasePackageRisk.NETWORK_BOUNDARY_VIOLATION),
        ("socket_requested", AGIcoreTradingV1OfflineReleasePackageRisk.NETWORK_BOUNDARY_VIOLATION),
        ("external_api_requested", AGIcoreTradingV1OfflineReleasePackageRisk.NETWORK_BOUNDARY_VIOLATION),
        ("order_execution_requested", AGIcoreTradingV1OfflineReleasePackageRisk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ("account_access_requested", AGIcoreTradingV1OfflineReleasePackageRisk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ("position_mutation_requested", AGIcoreTradingV1OfflineReleasePackageRisk.POSITION_MUTATION_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations_are_blocked(field, risk):
    data = _input(**{field: True})
    result = build_agicore_trading_v1_offline_release_package(data)

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleasePackageDecision.BLOCK_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE
    assert assert_agicore_trading_v1_offline_release_package_boundaries(data) is False


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
    result = build_agicore_trading_v1_offline_release_package(_input())

    assert result.file_read is False
    assert result.data_accessed is False
    assert result.real_order_submitted is False
    assert result.real_account_accessed is False
    assert result.position_mutated is False
