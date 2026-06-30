from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agicore.trading.offline_report_markdown_json_v1 import (
    assert_offline_report_markdown_json_v1_boundaries,
    build_offline_report_broker_section_v1,
    build_offline_report_context_v1,
    build_offline_report_journal_section_v1,
    build_offline_report_markdown_json_v1,
    build_offline_report_market_scenario_section_v1,
    build_offline_report_metrics_section_v1,
    build_offline_report_next_actions_section_v1,
    build_offline_report_risk_guard_section_v1,
    build_offline_report_summary_section_v1,
    build_offline_report_warnings_section_v1,
    compute_offline_report_markdown_json_v1_score,
    detect_offline_report_markdown_json_v1_risks,
    generate_offline_report_markdown_json_v1_recommendations,
    render_offline_report_json_dict_v1,
    render_offline_report_json_string_v1,
    render_offline_report_markdown_v1,
    validate_offline_report_json_v1,
    validate_offline_report_markdown_json_v1_input,
    validate_offline_report_markdown_v1,
)
from agicore.trading.offline_report_markdown_json_v1_models import (
    OfflineReportMarkdownJsonV1Decision,
    OfflineReportMarkdownJsonV1Input,
    OfflineReportMarkdownJsonV1Recommendation,
    OfflineReportMarkdownJsonV1Risk,
    OfflineReportMarkdownJsonV1State,
    OfflineReportSectionNameV1,
    OfflineReportSectionV1,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/offline_report_markdown_json_v1.py"


def _input(**overrides):
    payload = {
        "run_id": "run-001",
        "symbol": "SIM",
        "decision": "APPROVE_RISK_GUARD_ENFORCEMENT_V1",
        "score": 100,
        "market_scenario": {"profile": "TREND_UP", "bars": 8},
        "broker_result": {"mode": "SIMULATED", "read_only": True, "real_order_submitted": False},
        "risk_guard_result": {"decision": "APPROVE_RISK_GUARD_ENFORCEMENT_V1", "violations": []},
        "journal_result": {"total_entries": 8, "complete": True},
        "metrics": {"bar_count": 8, "risk_count": 0, "real_order_count": 0},
    }
    payload.update(overrides)
    return OfflineReportMarkdownJsonV1Input(**payload)


def test_nominal_complete_report():
    result = build_offline_report_markdown_json_v1(_input())

    assert result.decision is OfflineReportMarkdownJsonV1Decision.APPROVE_OFFLINE_REPORT_MARKDOWN_JSON_V1
    assert result.state is OfflineReportMarkdownJsonV1State.READY_FOR_CSV_REPLAY_INPUT_V1
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.metrics.section_count == 8
    assert result.markdown.content.startswith("# Offline Report Markdown JSON v1")
    assert result.json_report.payload["context"]["run_id"] == "run-001"


def test_input_missing():
    result = build_offline_report_markdown_json_v1(None)

    assert validate_offline_report_markdown_json_v1_input(None) is False
    assert OfflineReportMarkdownJsonV1Risk.OFFLINE_REPORT_INPUT_MISSING in result.risks
    assert result.decision is OfflineReportMarkdownJsonV1Decision.REQUIRE_OFFLINE_REPORT_INPUT_FIXES
    assert result.state is OfflineReportMarkdownJsonV1State.OFFLINE_REPORT_MARKDOWN_JSON_V1_INPUT_INVALID


def test_context_invalid():
    result = build_offline_report_markdown_json_v1(_input(force_context_invalid=True))

    assert OfflineReportMarkdownJsonV1Risk.OFFLINE_REPORT_CONTEXT_INVALID in result.risks
    assert result.decision is OfflineReportMarkdownJsonV1Decision.REQUIRE_OFFLINE_REPORT_CONTEXT_FIXES


def test_section_missing():
    result = build_offline_report_markdown_json_v1(_input(force_section_missing=True))

    assert OfflineReportMarkdownJsonV1Risk.OFFLINE_REPORT_SECTION_MISSING in result.risks
    assert result.decision is OfflineReportMarkdownJsonV1Decision.REQUIRE_OFFLINE_REPORT_SECTION_FIXES


def test_markdown_invalid():
    result = build_offline_report_markdown_json_v1(_input(force_markdown_invalid=True))

    assert OfflineReportMarkdownJsonV1Risk.OFFLINE_REPORT_MARKDOWN_INVALID in result.risks
    assert result.decision is OfflineReportMarkdownJsonV1Decision.REQUIRE_OFFLINE_REPORT_MARKDOWN_FIXES


def test_json_invalid():
    result = build_offline_report_markdown_json_v1(_input(force_json_invalid=True))

    assert OfflineReportMarkdownJsonV1Risk.OFFLINE_REPORT_JSON_INVALID in result.risks
    assert result.decision is OfflineReportMarkdownJsonV1Decision.REQUIRE_OFFLINE_REPORT_JSON_FIXES


def test_metrics_missing():
    result = build_offline_report_markdown_json_v1(_input(force_metrics_missing=True))

    assert OfflineReportMarkdownJsonV1Risk.OFFLINE_REPORT_METRICS_MISSING in result.risks
    assert result.decision is OfflineReportMarkdownJsonV1Decision.REQUIRE_OFFLINE_REPORT_METRICS_FIXES


def test_blocked_decision_is_represented():
    result = build_offline_report_markdown_json_v1(
        _input(decision="BLOCK_RISK_GUARD_ENFORCEMENT_V1", blocked_reason="cash insufficient")
    )

    assert "cash insufficient" in result.markdown.content
    assert result.json_report.payload["sections"]["SUMMARY"]["payload"]["blocked_reason"] == "cash insufficient"


def test_warnings_are_represented():
    result = build_offline_report_markdown_json_v1(_input(warnings=("synthetic warning",)))

    assert "synthetic warning" in result.markdown.content
    assert result.json_report.payload["sections"]["WARNINGS"]["payload"]["warnings"] == ["synthetic warning"]


def test_next_actions_are_represented():
    result = build_offline_report_markdown_json_v1(_input(next_actions=("Prepare replay",)))

    assert "Prepare replay" in result.markdown.content
    assert result.json_report.payload["sections"]["NEXT_ACTIONS"]["payload"]["next_actions"] == ["Prepare replay"]


def test_section_builders_and_markdown_report():
    data = _input()
    context = build_offline_report_context_v1(data)
    sections = (
        build_offline_report_summary_section_v1(context, data),
        build_offline_report_market_scenario_section_v1(data),
        build_offline_report_broker_section_v1(data),
        build_offline_report_risk_guard_section_v1(data),
        build_offline_report_journal_section_v1(data),
        build_offline_report_metrics_section_v1(data),
        build_offline_report_warnings_section_v1(data),
        build_offline_report_next_actions_section_v1(data),
    )
    markdown = render_offline_report_markdown_v1(context, sections)

    assert all(section.name in tuple(OfflineReportSectionNameV1) for section in sections)
    assert validate_offline_report_markdown_v1(markdown) is True


def test_json_dict_and_json_string_are_serializable():
    result = build_offline_report_markdown_json_v1(_input())
    payload = render_offline_report_json_dict_v1(result.context, result.sections, result.metrics)
    serialized = render_offline_report_json_string_v1(payload)

    assert validate_offline_report_json_v1(payload) is True
    assert json.loads(serialized)["schema"] == "offline_report_markdown_json_v1"
    assert json.loads(result.json_report.serialized)["context"]["symbol"] == "SIM"


def test_custom_section_invalid_is_detected():
    result = build_offline_report_markdown_json_v1(
        _input(custom_sections=(OfflineReportSectionV1(name="BAD", title="Bad", lines=("bad",)),))
    )

    assert OfflineReportMarkdownJsonV1Risk.OFFLINE_REPORT_SECTION_MISSING in result.risks


def test_score_and_risks_can_be_computed_directly():
    result = build_offline_report_markdown_json_v1(_input())
    risks = detect_offline_report_markdown_json_v1_risks(
        _input(),
        context=result.context,
        sections=result.sections,
        markdown=result.markdown,
        json_report=result.json_report,
        metrics=result.metrics,
    )
    score = compute_offline_report_markdown_json_v1_score(
        _input(),
        context=result.context,
        sections=result.sections,
        markdown=result.markdown,
        json_report=result.json_report,
        metrics=result.metrics,
        risks=risks,
    )

    assert risks == ()
    assert score.overall_score == 100


def test_recommendations_generated():
    recommendations = generate_offline_report_markdown_json_v1_recommendations(
        (OfflineReportMarkdownJsonV1Risk.OFFLINE_REPORT_JSON_INVALID,)
    )

    assert OfflineReportMarkdownJsonV1Recommendation.FIX_OFFLINE_REPORT_JSON in recommendations
    assert OfflineReportMarkdownJsonV1Recommendation.RUN_OFFLINE_REPORT_MARKDOWN_JSON_V1_TEST_SUITE in recommendations


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("file_write_requested", OfflineReportMarkdownJsonV1Risk.FILE_WRITE_BOUNDARY_VIOLATION),
        ("real_data_access_requested", OfflineReportMarkdownJsonV1Risk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_read_requested", OfflineReportMarkdownJsonV1Risk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_write_requested", OfflineReportMarkdownJsonV1Risk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("broker_connection_requested", OfflineReportMarkdownJsonV1Risk.REAL_BROKER_BOUNDARY_VIOLATION),
        ("api_key_read_requested", OfflineReportMarkdownJsonV1Risk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("env_var_read_requested", OfflineReportMarkdownJsonV1Risk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("network_requested", OfflineReportMarkdownJsonV1Risk.NETWORK_BOUNDARY_VIOLATION),
        ("http_requested", OfflineReportMarkdownJsonV1Risk.NETWORK_BOUNDARY_VIOLATION),
        ("websocket_requested", OfflineReportMarkdownJsonV1Risk.NETWORK_BOUNDARY_VIOLATION),
        ("socket_requested", OfflineReportMarkdownJsonV1Risk.NETWORK_BOUNDARY_VIOLATION),
        ("order_execution_requested", OfflineReportMarkdownJsonV1Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ("account_access_requested", OfflineReportMarkdownJsonV1Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ("position_mutation_requested", OfflineReportMarkdownJsonV1Risk.POSITION_MUTATION_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations_are_blocked(field, risk):
    result = build_offline_report_markdown_json_v1(_input(**{field: True}))

    assert risk in result.risks
    assert result.decision is OfflineReportMarkdownJsonV1Decision.BLOCK_OFFLINE_REPORT_MARKDOWN_JSON_V1
    assert assert_offline_report_markdown_json_v1_boundaries(_input(**{field: True})) is False


def test_no_file_write_or_data_directory_literal_in_module_source():
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert "open(" not in source
    assert ".write(" not in source
    assert "write_text" not in source
    assert "read_text" not in source
    assert "data/" not in source


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
    result = build_offline_report_markdown_json_v1(_input())

    assert result.file_written is False
    assert result.data_accessed is False
    assert result.real_order_submitted is False
    assert result.real_account_accessed is False
    assert result.position_mutated is False
