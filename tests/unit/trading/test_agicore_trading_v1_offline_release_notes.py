from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agicore.trading.agicore_trading_v1_offline_release_notes import (
    assert_agicore_trading_v1_offline_release_notes_boundaries,
    build_agicore_trading_v1_offline_release_notes,
    build_offline_release_notes_capability_section,
    build_offline_release_notes_context,
    build_offline_release_notes_known_limitations_section,
    build_offline_release_notes_next_steps_section,
    build_offline_release_notes_non_goals_section,
    build_offline_release_notes_testing_evidence_section,
    build_offline_release_notes_usage_guidance_section,
    compute_agicore_trading_v1_offline_release_notes_score,
    detect_agicore_trading_v1_offline_release_notes_risks,
    generate_agicore_trading_v1_offline_release_notes_recommendations,
    render_agicore_trading_v1_offline_release_notes_json_report,
    render_agicore_trading_v1_offline_release_notes_markdown,
    validate_agicore_trading_v1_offline_release_notes_input,
    validate_offline_release_notes_markdown,
    validate_offline_release_notes_no_overclaims,
    validate_offline_release_notes_safety_language,
)
from agicore.trading.agicore_trading_v1_offline_release_notes_models import (
    AGIcoreTradingV1OfflineReleaseNotesDecision,
    AGIcoreTradingV1OfflineReleaseNotesInput,
    AGIcoreTradingV1OfflineReleaseNotesRecommendation,
    AGIcoreTradingV1OfflineReleaseNotesRisk,
    AGIcoreTradingV1OfflineReleaseNotesState,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/agicore_trading_v1_offline_release_notes.py"
DOC_PATH = ROOT / "docs/AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES.md"


def _input(**overrides):
    payload = {}
    payload.update(overrides)
    return AGIcoreTradingV1OfflineReleaseNotesInput(**payload)


def test_nominal_release_notes():
    result = build_agicore_trading_v1_offline_release_notes(_input())

    assert result.decision is AGIcoreTradingV1OfflineReleaseNotesDecision.APPROVE_AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES
    assert result.state is AGIcoreTradingV1OfflineReleaseNotesState.READY_FOR_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert len(result.capabilities) == 10
    assert len(result.non_goals) == 10
    assert len(result.testing_evidence) == 4
    assert len(result.known_limitations) == 7
    assert validate_offline_release_notes_markdown(result.report.markdown)
    assert validate_offline_release_notes_safety_language(result.report.markdown)
    assert validate_offline_release_notes_no_overclaims(result.report.markdown)


def test_input_missing():
    result = build_agicore_trading_v1_offline_release_notes(None)

    assert validate_agicore_trading_v1_offline_release_notes_input(None) is False
    assert AGIcoreTradingV1OfflineReleaseNotesRisk.OFFLINE_RELEASE_NOTES_INPUT_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleaseNotesDecision.REQUIRE_OFFLINE_RELEASE_NOTES_INPUT_FIXES
    assert result.state is AGIcoreTradingV1OfflineReleaseNotesState.AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES_INPUT_INVALID


def test_capabilities_missing():
    result = build_agicore_trading_v1_offline_release_notes(_input(force_capabilities_missing=True))

    assert AGIcoreTradingV1OfflineReleaseNotesRisk.OFFLINE_RELEASE_NOTES_CAPABILITIES_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleaseNotesDecision.REQUIRE_OFFLINE_RELEASE_NOTES_CAPABILITY_FIXES


def test_non_goals_missing():
    result = build_agicore_trading_v1_offline_release_notes(_input(force_non_goals_missing=True))

    assert AGIcoreTradingV1OfflineReleaseNotesRisk.OFFLINE_RELEASE_NOTES_NON_GOALS_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleaseNotesDecision.REQUIRE_OFFLINE_RELEASE_NOTES_NON_GOAL_FIXES


def test_testing_evidence_missing():
    result = build_agicore_trading_v1_offline_release_notes(_input(force_testing_evidence_missing=True))

    assert AGIcoreTradingV1OfflineReleaseNotesRisk.OFFLINE_RELEASE_NOTES_TESTING_EVIDENCE_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleaseNotesDecision.REQUIRE_OFFLINE_RELEASE_NOTES_TESTING_EVIDENCE_FIXES


def test_limitations_missing():
    result = build_agicore_trading_v1_offline_release_notes(_input(force_limitations_missing=True))

    assert AGIcoreTradingV1OfflineReleaseNotesRisk.OFFLINE_RELEASE_NOTES_LIMITATIONS_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleaseNotesDecision.REQUIRE_OFFLINE_RELEASE_NOTES_LIMITATION_FIXES


def test_safety_language_missing():
    result = build_agicore_trading_v1_offline_release_notes(_input(force_safety_language_missing=True))

    assert AGIcoreTradingV1OfflineReleaseNotesRisk.OFFLINE_RELEASE_NOTES_SAFETY_LANGUAGE_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleaseNotesDecision.REQUIRE_OFFLINE_RELEASE_NOTES_SAFETY_LANGUAGE_FIXES


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("force_live_trading_overclaim", AGIcoreTradingV1OfflineReleaseNotesRisk.LIVE_TRADING_READINESS_OVERCLAIM),
        ("force_real_broker_overclaim", AGIcoreTradingV1OfflineReleaseNotesRisk.REAL_BROKER_READINESS_OVERCLAIM),
        ("force_real_order_overclaim", AGIcoreTradingV1OfflineReleaseNotesRisk.REAL_ORDER_EXECUTION_OVERCLAIM),
        ("force_profitability_overclaim", AGIcoreTradingV1OfflineReleaseNotesRisk.PROFITABILITY_PROOF_OVERCLAIM),
        ("force_financial_advice_overclaim", AGIcoreTradingV1OfflineReleaseNotesRisk.FINANCIAL_ADVICE_OVERCLAIM),
    ),
)
def test_overclaims_are_rejected(field, risk):
    result = build_agicore_trading_v1_offline_release_notes(_input(**{field: True}))

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleaseNotesDecision.REQUIRE_OFFLINE_RELEASE_NOTES_NO_OVERCLAIM_FIXES
    assert validate_offline_release_notes_no_overclaims(result.report.markdown) is False


def test_markdown_generated_and_sections_helpers():
    result = build_agicore_trading_v1_offline_release_notes(_input())
    context = build_offline_release_notes_context(_input())

    assert "# AGIcore Trading v1 Offline Release Notes" in result.report.markdown
    assert "CSV Replay Input v1" in build_offline_release_notes_capability_section(result.capabilities)
    assert "pas de trading reel" in build_offline_release_notes_non_goals_section(result.non_goals)
    assert "37 passed" in build_offline_release_notes_testing_evidence_section(result.testing_evidence)
    assert "strategies simples seulement" in build_offline_release_notes_known_limitations_section(result.known_limitations)
    assert "local/offline" in build_offline_release_notes_usage_guidance_section(result.usage_guidance)
    assert "Offline Smoke Demo" in build_offline_release_notes_next_steps_section(context)
    assert render_agicore_trading_v1_offline_release_notes_markdown(
        context,
        result.capabilities,
        result.non_goals,
        result.testing_evidence,
        result.known_limitations,
        result.usage_guidance,
    )


def test_markdown_docs_validated():
    markdown = DOC_PATH.read_text(encoding="utf-8")

    assert validate_offline_release_notes_markdown(markdown)
    assert validate_offline_release_notes_safety_language(markdown)
    assert validate_offline_release_notes_no_overclaims(markdown)
    assert "AGIcore Trading v1 Offline Smoke Demo" in markdown


def test_json_report():
    result = build_agicore_trading_v1_offline_release_notes(_input())
    payload = json.loads(render_agicore_trading_v1_offline_release_notes_json_report(result))

    assert payload["schema"] == "agicore_trading_v1_offline_release_notes"
    assert payload["decision"] == "APPROVE_AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES"
    assert payload["live_trading_ready"] is False
    assert payload["real_broker_ready"] is False
    assert payload["real_orders_ready"] is False
    assert payload["profitability_proven"] is False
    assert payload["financial_advice"] is False


def test_score_risks_and_recommendations_directly():
    result = build_agicore_trading_v1_offline_release_notes(_input())
    risks = detect_agicore_trading_v1_offline_release_notes_risks(
        _input(),
        result.report.markdown,
        result.capabilities,
        result.non_goals,
        result.testing_evidence,
        result.known_limitations,
    )
    score = compute_agicore_trading_v1_offline_release_notes_score(
        _input(),
        result.report.markdown,
        result.capabilities,
        result.non_goals,
        result.testing_evidence,
        result.known_limitations,
        risks,
    )
    recommendations = generate_agicore_trading_v1_offline_release_notes_recommendations(risks)

    assert risks == ()
    assert score.overall_score == 100
    assert recommendations == (
        AGIcoreTradingV1OfflineReleaseNotesRecommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO,
    )


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("file_read_requested", AGIcoreTradingV1OfflineReleaseNotesRisk.FILE_READ_BOUNDARY_VIOLATION),
        ("real_data_access_requested", AGIcoreTradingV1OfflineReleaseNotesRisk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_access_requested", AGIcoreTradingV1OfflineReleaseNotesRisk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("broker_connection_requested", AGIcoreTradingV1OfflineReleaseNotesRisk.REAL_BROKER_BOUNDARY_VIOLATION),
        ("secret_read_requested", AGIcoreTradingV1OfflineReleaseNotesRisk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("network_requested", AGIcoreTradingV1OfflineReleaseNotesRisk.NETWORK_BOUNDARY_VIOLATION),
        ("http_requested", AGIcoreTradingV1OfflineReleaseNotesRisk.NETWORK_BOUNDARY_VIOLATION),
        ("websocket_requested", AGIcoreTradingV1OfflineReleaseNotesRisk.NETWORK_BOUNDARY_VIOLATION),
        ("socket_requested", AGIcoreTradingV1OfflineReleaseNotesRisk.NETWORK_BOUNDARY_VIOLATION),
        ("external_api_requested", AGIcoreTradingV1OfflineReleaseNotesRisk.NETWORK_BOUNDARY_VIOLATION),
        ("order_execution_requested", AGIcoreTradingV1OfflineReleaseNotesRisk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ("account_access_requested", AGIcoreTradingV1OfflineReleaseNotesRisk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ("position_mutation_requested", AGIcoreTradingV1OfflineReleaseNotesRisk.POSITION_MUTATION_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations_are_blocked(field, risk):
    data = _input(**{field: True})
    result = build_agicore_trading_v1_offline_release_notes(data)

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineReleaseNotesDecision.BLOCK_AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES
    assert assert_agicore_trading_v1_offline_release_notes_boundaries(data) is False


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
    result = build_agicore_trading_v1_offline_release_notes(_input())

    assert result.file_read is False
    assert result.data_accessed is False
    assert result.real_order_submitted is False
    assert result.real_account_accessed is False
    assert result.position_mutated is False
