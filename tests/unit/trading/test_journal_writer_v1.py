from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agicore.trading.journal_writer_v1 import (
    append_journal_entry_v1,
    assert_journal_writer_v1_offline_boundaries,
    build_journal_blocked_decision_entry_v1,
    build_journal_broker_preview_entry_v1,
    build_journal_context_v1,
    build_journal_entry_v1,
    build_journal_market_scenario_entry_v1,
    build_journal_metrics_entry_v1,
    build_journal_read_only_decision_entry_v1,
    build_journal_risk_guard_entry_v1,
    build_journal_run_completed_entry_v1,
    build_journal_run_started_entry_v1,
    build_journal_strategy_signal_entry_v1,
    build_journal_warning_entry_v1,
    build_journal_writer_v1,
    compute_journal_writer_v1_metrics,
    detect_journal_writer_v1_risks,
    generate_journal_writer_v1_recommendations,
    render_journal_writer_v1_json_report,
    render_journal_writer_v1_markdown_report,
    validate_journal_entry_v1,
    validate_journal_sequence_v1,
    validate_journal_writer_v1_input,
    validate_journal_writer_v1_integrity,
)
from agicore.trading.journal_writer_v1_models import (
    JournalEntrySeverityV1,
    JournalEntryTypeV1,
    JournalEntryV1,
    JournalSequenceV1,
    JournalWriterV1Decision,
    JournalWriterV1Input,
    JournalWriterV1Recommendation,
    JournalWriterV1Risk,
    JournalWriterV1State,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/journal_writer_v1.py"


def _input(**overrides):
    payload = {
        "run_id": "run-001",
        "symbol": "SIM",
        "scenario_id": "scenario-001",
        "market_scenario": {"profile": "TREND_UP", "bars": 8},
        "strategy_signal": {"action": "BUY", "confidence": 0.75},
        "broker_preview": {"action": "BUY", "read_only": True, "order_submitted": False},
        "risk_guard_result": {"decision": "APPROVE_RISK_GUARD_ENFORCEMENT_V1", "risks": []},
        "read_only_decision": {"action": "BUY", "order_submitted": False},
        "runner_metrics": {"bar_count": 8, "real_order_count": 0},
    }
    payload.update(overrides)
    return JournalWriterV1Input(**payload)


def test_nominal_complete_run():
    result = build_journal_writer_v1(_input())

    assert result.decision is JournalWriterV1Decision.APPROVE_JOURNAL_WRITER_V1
    assert result.state is JournalWriterV1State.READY_FOR_OFFLINE_REPORT_MARKDOWN_JSON_V1
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.sequence.complete is True
    assert result.metrics.total_entries == 8
    assert result.metrics.warning_count == 0
    assert result.metrics.blocked_count == 0
    assert result.report.markdown
    assert result.report.json


def test_input_missing():
    result = build_journal_writer_v1(None)

    assert validate_journal_writer_v1_input(None) is False
    assert JournalWriterV1Risk.JOURNAL_WRITER_INPUT_MISSING in result.risks
    assert result.decision is JournalWriterV1Decision.REQUIRE_JOURNAL_WRITER_INPUT_FIXES
    assert result.state is JournalWriterV1State.JOURNAL_WRITER_V1_INPUT_INVALID


def test_context_invalid():
    result = build_journal_writer_v1(_input(force_context_invalid=True))

    assert JournalWriterV1Risk.JOURNAL_CONTEXT_INVALID in result.risks
    assert result.decision is JournalWriterV1Decision.REQUIRE_JOURNAL_CONTEXT_FIXES


def test_entry_invalid():
    result = build_journal_writer_v1(_input(force_entry_invalid=True))

    assert JournalWriterV1Risk.JOURNAL_ENTRY_INVALID in result.risks
    assert result.decision is JournalWriterV1Decision.REQUIRE_JOURNAL_ENTRY_FIXES


def test_entry_type_invalid():
    custom = (
        {"index": 0, "entry_type": "BAD_TYPE", "severity": "INFO", "message": "bad type", "payload": {}},
    )
    result = build_journal_writer_v1(_input(custom_entries=custom))

    assert JournalWriterV1Risk.JOURNAL_ENTRY_TYPE_INVALID in result.risks
    assert result.decision is JournalWriterV1Decision.REQUIRE_JOURNAL_ENTRY_FIXES


def test_entry_severity_invalid():
    custom = (
        {"index": 0, "entry_type": "RUN_STARTED", "severity": "BAD_SEVERITY", "message": "bad severity", "payload": {}},
    )
    result = build_journal_writer_v1(_input(custom_entries=custom))

    assert JournalWriterV1Risk.JOURNAL_ENTRY_SEVERITY_INVALID in result.risks
    assert result.decision is JournalWriterV1Decision.REQUIRE_JOURNAL_ENTRY_FIXES


def test_sequence_invalid():
    result = build_journal_writer_v1(_input(force_sequence_invalid=True))

    assert JournalWriterV1Risk.JOURNAL_SEQUENCE_INVALID in result.risks
    assert result.decision is JournalWriterV1Decision.REQUIRE_JOURNAL_SEQUENCE_FIXES


def test_integrity_failed():
    result = build_journal_writer_v1(_input(force_integrity_failed=True))

    assert JournalWriterV1Risk.JOURNAL_INTEGRITY_FAILED in result.risks
    assert result.decision is JournalWriterV1Decision.REQUIRE_JOURNAL_INTEGRITY_FIXES


def test_metrics_calculated():
    result = build_journal_writer_v1(_input(warnings=("latency warning",), blocked_reason="risk blocked"))

    assert result.metrics.total_entries == 10
    assert result.metrics.warning_count == 1
    assert result.metrics.blocked_count == 1
    assert result.metrics.error_count == 0
    assert "WARNING_RECORDED" in result.metrics.event_types_present
    assert "DECISION_BLOCKED" in result.metrics.event_types_present


def test_warning_recorded():
    result = build_journal_writer_v1(_input(warnings=("synthetic warning",)))

    assert result.decision is JournalWriterV1Decision.APPROVE_JOURNAL_WRITER_V1
    assert result.metrics.warning_count == 1
    assert any(entry.entry_type is JournalEntryTypeV1.WARNING_RECORDED for entry in result.sequence.entries)


def test_blocked_decision_recorded():
    result = build_journal_writer_v1(_input(blocked_reason="risk guard rejected preview"))

    assert result.decision is JournalWriterV1Decision.APPROVE_JOURNAL_WRITER_V1
    assert result.metrics.blocked_count == 1
    assert any(entry.entry_type is JournalEntryTypeV1.DECISION_BLOCKED for entry in result.sequence.entries)


def test_run_completed_recorded():
    result = build_journal_writer_v1(_input())

    assert result.sequence.entries[-1].entry_type is JournalEntryTypeV1.RUN_COMPLETED
    assert result.sequence.complete is True
    assert validate_journal_sequence_v1(result.sequence) is True


def test_markdown_report():
    result = build_journal_writer_v1(_input())
    markdown = render_journal_writer_v1_markdown_report(result)

    assert "Journal Writer v1" in markdown
    assert "APPROVE_JOURNAL_WRITER_V1" in markdown
    assert "no file write" in markdown


def test_json_report():
    result = build_journal_writer_v1(_input())
    payload = json.loads(render_journal_writer_v1_json_report(result))

    assert payload["decision"] == "APPROVE_JOURNAL_WRITER_V1"
    assert payload["score"] == 100
    assert payload["risks"] == []
    assert payload["metrics"]["total_entries"] == 8
    assert payload["file_written"] is False
    assert payload["offline_only"] is True


def test_no_real_file_write_is_used():
    result = build_journal_writer_v1(_input())
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert result.file_written is False
    assert "open(" not in source
    assert "write_text" not in source
    assert "WriteAllText" not in source


def test_no_data_directory_read_is_used():
    result = build_journal_writer_v1(_input())
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert result.data_accessed is False
    assert "data/" not in source
    assert "read_text" not in source


def test_no_data_directory_write_is_used():
    result = build_journal_writer_v1(_input(data_directory_write_requested=False))

    assert result.file_written is False
    assert result.data_accessed is False


def test_no_network_socket_http_websocket_access_is_used():
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_modules = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported_from_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }

    assert imported_modules.isdisjoint({"requests", "httpx", "urllib", "socket", "websocket"})
    assert imported_from_modules.isdisjoint({"requests", "httpx", "urllib", "socket", "websocket"})


def test_no_real_key_or_env_var_is_read():
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert "environ" not in source
    assert "getenv" not in source
    assert "dotenv" not in source
    assert "API_KEY" not in source


def test_no_real_order_is_produced():
    result = build_journal_writer_v1(_input(order_execution_requested=False))

    assert result.real_order_submitted is False


def test_no_real_account_access():
    result = build_journal_writer_v1(_input(account_access_requested=False))

    assert result.real_account_accessed is False


def test_no_real_position_mutation():
    result = build_journal_writer_v1(_input(position_mutation_requested=False))

    assert result.position_mutated is False


def test_recommendations_generated():
    nominal = build_journal_writer_v1(_input())
    recs = generate_journal_writer_v1_recommendations(
        (JournalWriterV1Risk.JOURNAL_SEQUENCE_INVALID,)
    )

    assert JournalWriterV1Recommendation.APPROVE_OFFLINE_REPORT_MARKDOWN_JSON_V1 in nominal.recommendations
    assert JournalWriterV1Recommendation.FIX_JOURNAL_SEQUENCE in recs


def test_metrics_missing():
    result = build_journal_writer_v1(_input(force_metrics_missing=True))

    assert JournalWriterV1Risk.JOURNAL_METRICS_MISSING in result.risks
    assert result.decision is JournalWriterV1Decision.REQUIRE_JOURNAL_METRICS_FIXES


def test_report_missing():
    result = build_journal_writer_v1(_input(force_report_missing=True))

    assert JournalWriterV1Risk.JOURNAL_REPORT_MISSING in result.risks
    assert result.decision is JournalWriterV1Decision.REQUIRE_JOURNAL_REPORT_FIXES


@pytest.mark.parametrize(
    ("overrides", "expected"),
    (
        ({"file_write_requested": True}, JournalWriterV1Risk.FILE_WRITE_BOUNDARY_VIOLATION),
        ({"real_data_access_requested": True}, JournalWriterV1Risk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION),
        ({"data_directory_read_requested": True}, JournalWriterV1Risk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ({"data_directory_write_requested": True}, JournalWriterV1Risk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ({"broker_connection_requested": True}, JournalWriterV1Risk.REAL_BROKER_BOUNDARY_VIOLATION),
        ({"api_key_read_requested": True}, JournalWriterV1Risk.REAL_SECRET_BOUNDARY_VIOLATION),
        ({"network_requested": True}, JournalWriterV1Risk.NETWORK_BOUNDARY_VIOLATION),
        ({"order_execution_requested": True}, JournalWriterV1Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ({"account_access_requested": True}, JournalWriterV1Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ({"position_mutation_requested": True}, JournalWriterV1Risk.POSITION_MUTATION_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations(overrides, expected):
    result = build_journal_writer_v1(_input(**overrides))

    assert expected in result.risks
    assert result.decision is JournalWriterV1Decision.BLOCK_JOURNAL_WRITER_V1


def test_required_functions_are_callable_and_deterministic():
    data = _input()
    context = build_journal_context_v1(data)
    entries = (
        build_journal_run_started_entry_v1(context, 0),
        build_journal_market_scenario_entry_v1(context, 1, data.market_scenario),
        build_journal_strategy_signal_entry_v1(context, 2, data.strategy_signal),
        build_journal_broker_preview_entry_v1(context, 3, data.broker_preview),
        build_journal_risk_guard_entry_v1(context, 4, data.risk_guard_result),
        build_journal_read_only_decision_entry_v1(context, 5, data.read_only_decision),
        build_journal_metrics_entry_v1(context, 6, data.runner_metrics),
        build_journal_run_completed_entry_v1(context, 7),
    )
    sequence = JournalSequenceV1(context.run_id, entries, complete=True)
    appended = append_journal_entry_v1(
        JournalSequenceV1(context.run_id, entries[:-1], complete=False),
        entries[-1],
    )
    metrics = compute_journal_writer_v1_metrics(sequence, data)
    risks = detect_journal_writer_v1_risks(data, context, sequence, metrics, build_journal_writer_v1(data).report)

    assert validate_journal_writer_v1_input(data) is True
    assert assert_journal_writer_v1_offline_boundaries(data) is True
    assert all(validate_journal_entry_v1(entry) for entry in entries)
    assert validate_journal_sequence_v1(sequence) is True
    assert validate_journal_writer_v1_integrity(sequence) is True
    assert appended.complete is True
    assert metrics.total_entries == 8
    assert risks == ()


def test_build_generic_entry():
    context = build_journal_context_v1(_input())
    entry = build_journal_entry_v1(context, 0, JournalEntryTypeV1.RUN_STARTED, JournalEntrySeverityV1.INFO, "started")

    assert entry.entry_id == "run-001:0000:RUN_STARTED"
    assert validate_journal_entry_v1(entry) is True
