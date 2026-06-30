"""Deterministic in-memory journal writer v1 for AGIcore Trading."""

from __future__ import annotations

import json
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.journal_writer_v1_models import (
    JournalEntrySeverityV1,
    JournalEntryTypeV1,
    JournalEntryV1,
    JournalSequenceV1,
    JournalWriterV1Context,
    JournalWriterV1Decision,
    JournalWriterV1Input,
    JournalWriterV1Metrics,
    JournalWriterV1Recommendation,
    JournalWriterV1Report,
    JournalWriterV1Result,
    JournalWriterV1Risk,
    JournalWriterV1Score,
    JournalWriterV1State,
)


Risk = JournalWriterV1Risk
Recommendation = JournalWriterV1Recommendation
Decision = JournalWriterV1Decision
State = JournalWriterV1State
EntryType = JournalEntryTypeV1
Severity = JournalEntrySeverityV1


def _value(item: Any) -> str:
    return item.value if isinstance(item, Enum) else str(item)


def _dedupe(items: Iterable[Any]) -> tuple[Any, ...]:
    seen: set[Any] = set()
    out: list[Any] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return tuple(out)


def _coerce_input(data: JournalWriterV1Input | Mapping[str, Any] | None) -> JournalWriterV1Input | None:
    if data is None:
        return None
    if isinstance(data, JournalWriterV1Input):
        return data
    allowed = {field.name for field in fields(JournalWriterV1Input)}
    return JournalWriterV1Input(**{key: value for key, value in dict(data).items() if key in allowed})


def _parse_type(value: EntryType | str | None) -> EntryType | None:
    if isinstance(value, EntryType):
        return value
    if isinstance(value, str):
        try:
            return EntryType(value)
        except ValueError:
            return None
    return None


def _parse_severity(value: Severity | str | None) -> Severity | None:
    if isinstance(value, Severity):
        return value
    if isinstance(value, str):
        try:
            return Severity(value)
        except ValueError:
            return None
    return None


def _payload_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, int | float | str | bool):
        return value
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): _payload_value(item) for key, item in value.items()}
    if isinstance(value, tuple | list):
        return [_payload_value(item) for item in value]
    return str(value)


def build_journal_context_v1(data: JournalWriterV1Input | Mapping[str, Any] | None) -> JournalWriterV1Context:
    data = _coerce_input(data) or JournalWriterV1Input()
    return JournalWriterV1Context(
        run_id=data.run_id,
        symbol=data.symbol,
        scenario_id=data.scenario_id,
        deterministic=True,
        in_memory_only=True,
        offline_only=True,
    )


def validate_journal_writer_v1_input(data: JournalWriterV1Input | Mapping[str, Any] | None) -> bool:
    data = _coerce_input(data)
    return (
        data is not None
        and bool(data.run_id)
        and bool(data.symbol)
        and bool(data.scenario_id)
        and data.force_context_invalid is False
        and assert_journal_writer_v1_offline_boundaries(data)
    )


def build_journal_entry_v1(
    context: JournalWriterV1Context,
    index: int,
    entry_type: EntryType | str,
    severity: Severity | str,
    message: str,
    payload: Mapping[str, Any] | None = None,
) -> JournalEntryV1:
    parsed_type = _parse_type(entry_type)
    type_value = parsed_type.value if parsed_type else str(entry_type)
    return JournalEntryV1(
        entry_id=f"{context.run_id}:{index:04d}:{type_value}",
        index=index,
        entry_type=entry_type,
        severity=severity,
        message=message,
        payload=dict(payload or ()),
    )


def build_journal_run_started_entry_v1(context: JournalWriterV1Context, index: int = 0) -> JournalEntryV1:
    return build_journal_entry_v1(
        context,
        index,
        EntryType.RUN_STARTED,
        Severity.INFO,
        "offline run started",
        {"run_id": context.run_id, "symbol": context.symbol},
    )


def build_journal_market_scenario_entry_v1(context: JournalWriterV1Context, index: int, market_scenario: Any = None) -> JournalEntryV1:
    return build_journal_entry_v1(
        context,
        index,
        EntryType.MARKET_SCENARIO_CREATED,
        Severity.INFO,
        "synthetic market scenario recorded",
        {"scenario_id": context.scenario_id, "scenario": _payload_value(market_scenario)},
    )


def build_journal_strategy_signal_entry_v1(context: JournalWriterV1Context, index: int, strategy_signal: Any = None) -> JournalEntryV1:
    return build_journal_entry_v1(
        context,
        index,
        EntryType.STRATEGY_SIGNAL_EVALUATED,
        Severity.INFO,
        "strategy signal evaluated",
        {"signal": _payload_value(strategy_signal)},
    )


def build_journal_broker_preview_entry_v1(context: JournalWriterV1Context, index: int, broker_preview: Any = None) -> JournalEntryV1:
    return build_journal_entry_v1(
        context,
        index,
        EntryType.BROKER_PREVIEW_CREATED,
        Severity.INFO,
        "simulated broker preview recorded",
        {"preview": _payload_value(broker_preview), "read_only": True},
    )


def build_journal_risk_guard_entry_v1(context: JournalWriterV1Context, index: int, risk_guard_result: Any = None) -> JournalEntryV1:
    return build_journal_entry_v1(
        context,
        index,
        EntryType.RISK_GUARD_EVALUATED,
        Severity.INFO,
        "risk guard result recorded",
        {"risk_guard": _payload_value(risk_guard_result)},
    )


def build_journal_read_only_decision_entry_v1(context: JournalWriterV1Context, index: int, read_only_decision: Any = None) -> JournalEntryV1:
    return build_journal_entry_v1(
        context,
        index,
        EntryType.READ_ONLY_DECISION_CREATED,
        Severity.INFO,
        "read-only decision recorded",
        {"decision": _payload_value(read_only_decision), "order_submitted": False},
    )


def build_journal_metrics_entry_v1(context: JournalWriterV1Context, index: int, runner_metrics: Any = None) -> JournalEntryV1:
    return build_journal_entry_v1(
        context,
        index,
        EntryType.METRICS_COMPUTED,
        Severity.INFO,
        "offline metrics computed",
        {"metrics": _payload_value(runner_metrics)},
    )


def build_journal_warning_entry_v1(context: JournalWriterV1Context, index: int, warning: str) -> JournalEntryV1:
    return build_journal_entry_v1(
        context,
        index,
        EntryType.WARNING_RECORDED,
        Severity.WARNING,
        "warning recorded",
        {"warning": warning},
    )


def build_journal_blocked_decision_entry_v1(context: JournalWriterV1Context, index: int, reason: str) -> JournalEntryV1:
    return build_journal_entry_v1(
        context,
        index,
        EntryType.DECISION_BLOCKED,
        Severity.BLOCKED,
        "decision blocked",
        {"reason": reason},
    )


def build_journal_run_completed_entry_v1(context: JournalWriterV1Context, index: int) -> JournalEntryV1:
    return build_journal_entry_v1(
        context,
        index,
        EntryType.RUN_COMPLETED,
        Severity.INFO,
        "offline run completed",
        {"run_id": context.run_id, "complete": True},
    )


def append_journal_entry_v1(sequence: JournalSequenceV1, entry: JournalEntryV1) -> JournalSequenceV1:
    return JournalSequenceV1(
        run_id=sequence.run_id,
        entries=sequence.entries + (entry,),
        complete=_parse_type(entry.entry_type) is EntryType.RUN_COMPLETED,
        in_memory_only=True,
    )


def _coerce_entry(item: JournalEntryV1 | Mapping[str, Any], context: JournalWriterV1Context, index: int) -> JournalEntryV1:
    if isinstance(item, JournalEntryV1):
        return item
    payload = dict(item)
    return build_journal_entry_v1(
        context,
        int(payload.get("index", index)),
        payload.get("entry_type", EntryType.WARNING_RECORDED),
        payload.get("severity", Severity.WARNING),
        str(payload.get("message", "")),
        payload.get("payload", {}),
    )


def validate_journal_entry_v1(entry: JournalEntryV1 | None) -> bool:
    return (
        entry is not None
        and bool(entry.entry_id)
        and isinstance(entry.index, int)
        and entry.index >= 0
        and _parse_type(entry.entry_type) is not None
        and _parse_severity(entry.severity) is not None
        and bool(entry.message)
        and isinstance(entry.payload, dict)
    )


def validate_journal_sequence_v1(sequence: JournalSequenceV1 | None) -> bool:
    if sequence is None or not sequence.entries or not sequence.in_memory_only:
        return False
    indexes = tuple(entry.index for entry in sequence.entries)
    expected = tuple(range(len(sequence.entries)))
    if indexes != expected:
        return False
    if _parse_type(sequence.entries[0].entry_type) is not EntryType.RUN_STARTED:
        return False
    if sequence.complete and _parse_type(sequence.entries[-1].entry_type) is not EntryType.RUN_COMPLETED:
        return False
    return all(validate_journal_entry_v1(entry) for entry in sequence.entries)


def validate_journal_writer_v1_integrity(sequence: JournalSequenceV1 | None) -> bool:
    if not validate_journal_sequence_v1(sequence):
        return False
    types = {_parse_type(entry.entry_type) for entry in sequence.entries}
    required = {
        EntryType.RUN_STARTED,
        EntryType.MARKET_SCENARIO_CREATED,
        EntryType.STRATEGY_SIGNAL_EVALUATED,
        EntryType.BROKER_PREVIEW_CREATED,
        EntryType.RISK_GUARD_EVALUATED,
        EntryType.READ_ONLY_DECISION_CREATED,
        EntryType.METRICS_COMPUTED,
        EntryType.RUN_COMPLETED,
    }
    return required.issubset(types)


def _build_entries(data: JournalWriterV1Input, context: JournalWriterV1Context) -> tuple[JournalEntryV1, ...]:
    if data.custom_entries is not None:
        return tuple(_coerce_entry(item, context, index) for index, item in enumerate(data.custom_entries))
    entries: list[JournalEntryV1] = [
        build_journal_run_started_entry_v1(context, 0),
        build_journal_market_scenario_entry_v1(context, 1, data.market_scenario),
        build_journal_strategy_signal_entry_v1(context, 2, data.strategy_signal),
        build_journal_broker_preview_entry_v1(context, 3, data.broker_preview),
        build_journal_risk_guard_entry_v1(context, 4, data.risk_guard_result),
        build_journal_read_only_decision_entry_v1(context, 5, data.read_only_decision),
        build_journal_metrics_entry_v1(context, 6, data.runner_metrics),
    ]
    if data.force_entry_invalid:
        entries.append(JournalEntryV1("", len(entries), EntryType.WARNING_RECORDED, Severity.WARNING, "", {}))
    for warning in data.warnings:
        entries.append(build_journal_warning_entry_v1(context, len(entries), warning))
    if data.blocked_reason:
        entries.append(build_journal_blocked_decision_entry_v1(context, len(entries), data.blocked_reason))
    entries.append(build_journal_run_completed_entry_v1(context, len(entries)))
    if data.force_sequence_invalid and entries:
        last = entries[-1]
        entries[-1] = JournalEntryV1(last.entry_id, last.index + 2, last.entry_type, last.severity, last.message, last.payload)
    return tuple(entries)


def compute_journal_writer_v1_metrics(sequence: JournalSequenceV1 | None, data: JournalWriterV1Input | Mapping[str, Any] | None = None) -> JournalWriterV1Metrics | None:
    data = _coerce_input(data) or JournalWriterV1Input()
    if data.force_metrics_missing or sequence is None or not sequence.entries:
        return None
    severities = tuple(_parse_severity(entry.severity) for entry in sequence.entries)
    types = tuple(_parse_type(entry.entry_type) for entry in sequence.entries)
    return JournalWriterV1Metrics(
        total_entries=len(sequence.entries),
        warning_count=sum(1 for item in severities if item is Severity.WARNING),
        blocked_count=sum(1 for item in severities if item is Severity.BLOCKED),
        error_count=sum(1 for item in severities if item is Severity.ERROR),
        event_types_present=tuple(_dedupe(item.value for item in types if item is not None)),
        first_index=sequence.entries[0].index,
        last_index=sequence.entries[-1].index,
        complete=sequence.complete,
    )


def assert_journal_writer_v1_offline_boundaries(data: JournalWriterV1Input | Mapping[str, Any] | None) -> bool:
    data = _coerce_input(data)
    return (
        data is not None
        and data.offline_mode_enforced is True
        and data.sandbox_mode_enforced is True
        and data.in_memory_only is True
        and data.no_file_write is True
        and data.no_real_data_access is True
        and data.no_data_directory_read is True
        and data.no_data_directory_write is True
        and data.no_real_broker is True
        and data.no_alpaca_real is True
        and data.no_api_key_read is True
        and data.no_env_var_read is True
        and data.no_hardcoded_secret is True
        and data.no_http_transport is True
        and data.no_websocket_transport is True
        and data.no_socket_transport is True
        and data.no_external_api is True
        and data.no_external_ml is True
        and data.no_external_llm is True
        and data.no_real_order is True
        and data.no_real_account_access is True
        and data.no_position_mutation is True
        and data.file_write_requested is False
        and data.real_data_access_requested is False
        and data.data_directory_read_requested is False
        and data.data_directory_write_requested is False
        and data.broker_connection_requested is False
        and data.api_key_read_requested is False
        and data.env_var_read_requested is False
        and data.network_requested is False
        and data.http_requested is False
        and data.websocket_requested is False
        and data.socket_requested is False
        and data.external_api_requested is False
        and data.order_execution_requested is False
        and data.account_access_requested is False
        and data.position_mutation_requested is False
    )


def detect_journal_writer_v1_risks(
    data: JournalWriterV1Input | Mapping[str, Any] | None,
    context: JournalWriterV1Context | None = None,
    sequence: JournalSequenceV1 | None = None,
    metrics: JournalWriterV1Metrics | None = None,
    report: JournalWriterV1Report | None = None,
) -> tuple[Risk, ...]:
    data = _coerce_input(data)
    risks: list[Risk] = []
    if data is None:
        risks.append(Risk.JOURNAL_WRITER_INPUT_MISSING)
        return tuple(risks)
    if context is None or not context.run_id or not context.symbol or data.force_context_invalid:
        risks.append(Risk.JOURNAL_CONTEXT_INVALID)
    if sequence is None or not sequence.entries:
        risks.append(Risk.JOURNAL_SEQUENCE_INVALID)
    else:
        for entry in sequence.entries:
            if not validate_journal_entry_v1(entry):
                risks.append(Risk.JOURNAL_ENTRY_INVALID)
            if _parse_type(entry.entry_type) is None:
                risks.append(Risk.JOURNAL_ENTRY_TYPE_INVALID)
            if _parse_severity(entry.severity) is None:
                risks.append(Risk.JOURNAL_ENTRY_SEVERITY_INVALID)
        if not validate_journal_sequence_v1(sequence):
            risks.append(Risk.JOURNAL_SEQUENCE_INVALID)
        if not validate_journal_writer_v1_integrity(sequence) or data.force_integrity_failed:
            risks.append(Risk.JOURNAL_INTEGRITY_FAILED)
    if metrics is None:
        risks.append(Risk.JOURNAL_METRICS_MISSING)
    if report is None:
        risks.append(Risk.JOURNAL_REPORT_MISSING)
    if data.no_file_write is not True or data.file_write_requested:
        risks.append(Risk.FILE_WRITE_BOUNDARY_VIOLATION)
    if data.no_real_data_access is not True or data.real_data_access_requested:
        risks.append(Risk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION)
    if data.no_data_directory_read is not True or data.no_data_directory_write is not True or data.data_directory_read_requested or data.data_directory_write_requested:
        risks.append(Risk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION)
    if data.no_real_broker is not True or data.no_alpaca_real is not True or data.broker_connection_requested:
        risks.append(Risk.REAL_BROKER_BOUNDARY_VIOLATION)
    if data.no_api_key_read is not True or data.no_env_var_read is not True or data.no_hardcoded_secret is not True or data.api_key_read_requested or data.env_var_read_requested:
        risks.append(Risk.REAL_SECRET_BOUNDARY_VIOLATION)
    if data.no_http_transport is not True or data.no_websocket_transport is not True or data.no_socket_transport is not True or data.no_external_api is not True or data.network_requested or data.http_requested or data.websocket_requested or data.socket_requested or data.external_api_requested:
        risks.append(Risk.NETWORK_BOUNDARY_VIOLATION)
    if data.no_real_order is not True or data.order_execution_requested:
        risks.append(Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION)
    if data.no_real_account_access is not True or data.account_access_requested:
        risks.append(Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION)
    if data.no_position_mutation is not True or data.position_mutation_requested:
        risks.append(Risk.POSITION_MUTATION_BOUNDARY_VIOLATION)
    return _dedupe(risks)


def _score(flag: bool) -> int:
    return 100 if flag else 0


def _build_score(data, context, sequence, metrics, report, risks) -> JournalWriterV1Score:
    parts = (
        _score(data is not None and validate_journal_writer_v1_input(data)),
        _score(context is not None and bool(context.run_id) and bool(context.symbol)),
        _score(sequence is not None and all(validate_journal_entry_v1(entry) for entry in sequence.entries)),
        _score(validate_journal_sequence_v1(sequence)),
        _score(data is not None and data.force_integrity_failed is False and validate_journal_writer_v1_integrity(sequence)),
        _score(metrics is not None),
        _score(report is not None and bool(report.markdown) and bool(report.json)),
        _score(data is not None and assert_journal_writer_v1_offline_boundaries(data)),
    )
    overall = 100 if not risks and all(part == 100 for part in parts) else round(sum(parts) / len(parts))
    return JournalWriterV1Score(overall, *parts)


def generate_journal_writer_v1_recommendations(risks: Iterable[Risk] | None = None) -> tuple[Recommendation, ...]:
    risks = tuple(risks or ())
    if not risks:
        return (
            Recommendation.RUN_JOURNAL_WRITER_V1_TEST_SUITE,
            Recommendation.APPROVE_OFFLINE_REPORT_MARKDOWN_JSON_V1,
        )
    mapping = {
        Risk.JOURNAL_WRITER_INPUT_MISSING: Recommendation.PROVIDE_JOURNAL_WRITER_INPUT,
        Risk.JOURNAL_CONTEXT_INVALID: Recommendation.FIX_JOURNAL_CONTEXT,
        Risk.JOURNAL_ENTRY_INVALID: Recommendation.FIX_JOURNAL_ENTRY,
        Risk.JOURNAL_ENTRY_TYPE_INVALID: Recommendation.USE_VALID_JOURNAL_ENTRY_TYPE,
        Risk.JOURNAL_ENTRY_SEVERITY_INVALID: Recommendation.USE_VALID_JOURNAL_ENTRY_SEVERITY,
        Risk.JOURNAL_SEQUENCE_INVALID: Recommendation.FIX_JOURNAL_SEQUENCE,
        Risk.JOURNAL_INTEGRITY_FAILED: Recommendation.FIX_JOURNAL_INTEGRITY,
        Risk.JOURNAL_METRICS_MISSING: Recommendation.COMPUTE_JOURNAL_METRICS,
        Risk.JOURNAL_REPORT_MISSING: Recommendation.GENERATE_JOURNAL_REPORT,
        Risk.FILE_WRITE_BOUNDARY_VIOLATION: Recommendation.REMOVE_FILE_WRITE,
        Risk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION: Recommendation.REMOVE_REAL_DATA_ACCESS,
        Risk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION: Recommendation.REMOVE_DATA_DIRECTORY_ACCESS,
        Risk.REAL_BROKER_BOUNDARY_VIOLATION: Recommendation.REMOVE_REAL_BROKER_ACCESS,
        Risk.REAL_SECRET_BOUNDARY_VIOLATION: Recommendation.REMOVE_REAL_SECRET_ACCESS,
        Risk.NETWORK_BOUNDARY_VIOLATION: Recommendation.REMOVE_NETWORK_ACCESS,
        Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION: Recommendation.REMOVE_ORDER_EXECUTION,
        Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION: Recommendation.REMOVE_ACCOUNT_ACCESS,
        Risk.POSITION_MUTATION_BOUNDARY_VIOLATION: Recommendation.REMOVE_POSITION_MUTATION,
    }
    return _dedupe(mapping[risk] for risk in risks if risk in mapping)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_JOURNAL_WRITER_V1
    boundary = {
        Risk.FILE_WRITE_BOUNDARY_VIOLATION,
        Risk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION,
        Risk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION,
        Risk.REAL_BROKER_BOUNDARY_VIOLATION,
        Risk.REAL_SECRET_BOUNDARY_VIOLATION,
        Risk.NETWORK_BOUNDARY_VIOLATION,
        Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION,
        Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION,
        Risk.POSITION_MUTATION_BOUNDARY_VIOLATION,
    }
    if any(risk in boundary for risk in risks):
        return Decision.BLOCK_JOURNAL_WRITER_V1
    if Risk.JOURNAL_WRITER_INPUT_MISSING in risks:
        return Decision.REQUIRE_JOURNAL_WRITER_INPUT_FIXES
    if Risk.JOURNAL_CONTEXT_INVALID in risks:
        return Decision.REQUIRE_JOURNAL_CONTEXT_FIXES
    if Risk.JOURNAL_ENTRY_INVALID in risks or Risk.JOURNAL_ENTRY_TYPE_INVALID in risks or Risk.JOURNAL_ENTRY_SEVERITY_INVALID in risks:
        return Decision.REQUIRE_JOURNAL_ENTRY_FIXES
    if Risk.JOURNAL_SEQUENCE_INVALID in risks:
        return Decision.REQUIRE_JOURNAL_SEQUENCE_FIXES
    if Risk.JOURNAL_INTEGRITY_FAILED in risks:
        return Decision.REQUIRE_JOURNAL_INTEGRITY_FIXES
    if Risk.JOURNAL_METRICS_MISSING in risks:
        return Decision.REQUIRE_JOURNAL_METRICS_FIXES
    if Risk.JOURNAL_REPORT_MISSING in risks:
        return Decision.REQUIRE_JOURNAL_REPORT_FIXES
    return Decision.BLOCK_JOURNAL_WRITER_V1


def _state_for(risks: tuple[Risk, ...], score: JournalWriterV1Score) -> State:
    if Risk.JOURNAL_WRITER_INPUT_MISSING in risks or Risk.JOURNAL_CONTEXT_INVALID in risks:
        return State.JOURNAL_WRITER_V1_INPUT_INVALID
    if risks:
        return State.JOURNAL_WRITER_V1_BLOCKED
    if score.overall_score == 100:
        return State.READY_FOR_OFFLINE_REPORT_MARKDOWN_JSON_V1
    if score.overall_score >= 70:
        return State.JOURNAL_WRITER_V1_COMPLETED_WITH_WARNINGS
    return State.NOT_READY


def _entry_payload(entry: JournalEntryV1) -> dict[str, Any]:
    return {
        "entry_id": entry.entry_id,
        "index": entry.index,
        "entry_type": _value(entry.entry_type),
        "severity": _value(entry.severity),
        "message": entry.message,
        "payload": _payload_value(entry.payload),
    }


def render_journal_writer_v1_markdown_report(result: JournalWriterV1Result) -> str:
    risks = ", ".join(_value(risk) for risk in result.risks) or "none"
    recs = ", ".join(_value(rec) for rec in result.recommendations) or "none"
    return "\n".join(
        (
            "# Journal Writer v1",
            f"- State: {result.state.value}",
            f"- Decision: {result.decision.value}",
            f"- Score: {result.score.overall_score}",
            f"- Entries: {result.metrics.total_entries if result.metrics else 0}",
            f"- Warnings: {result.metrics.warning_count if result.metrics else 0}",
            f"- Blocked: {result.metrics.blocked_count if result.metrics else 0}",
            f"- Errors: {result.metrics.error_count if result.metrics else 0}",
            f"- Risks: {risks}",
            f"- Recommendations: {recs}",
            "- Boundary: deterministic in-memory journal only; no file write, no data directory access, no broker, no secret, no network, no order, no account access, no position mutation.",
            f"- Next phase: {result.next_phase}",
        )
    )


def render_journal_writer_v1_json_report(result: JournalWriterV1Result) -> str:
    payload = {
        "state": result.state.value,
        "decision": result.decision.value,
        "score": result.score.overall_score,
        "risks": [risk.value for risk in result.risks],
        "recommendations": [rec.value for rec in result.recommendations],
        "entries": [_entry_payload(entry) for entry in result.sequence.entries] if result.sequence else [],
        "metrics": _payload_value(result.metrics.__dict__) if result.metrics else None,
        "offline_only": True,
        "in_memory_only": True,
        "file_written": False,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _build_report(result: JournalWriterV1Result) -> JournalWriterV1Report:
    payload = {
        "run_id": result.context.run_id if result.context else "",
        "entry_count": result.metrics.total_entries if result.metrics else 0,
        "risks": [risk.value for risk in result.risks],
        "next_phase": result.next_phase,
    }
    return JournalWriterV1Report(
        markdown=render_journal_writer_v1_markdown_report(result),
        json=render_journal_writer_v1_json_report(result),
        payload=payload,
    )


def build_journal_writer_v1(
    data: JournalWriterV1Input | Mapping[str, Any] | None = None,
) -> JournalWriterV1Result:
    data = _coerce_input(data)
    context = build_journal_context_v1(data) if data is not None else None
    sequence = None
    if data is not None and context is not None:
        entries = _build_entries(data, context)
        sequence = JournalSequenceV1(context.run_id, entries, complete=bool(entries and _parse_type(entries[-1].entry_type) is EntryType.RUN_COMPLETED))
    metrics = compute_journal_writer_v1_metrics(sequence, data) if sequence is not None else None
    report_placeholder = None if data is None or data.force_report_missing else JournalWriterV1Report("", "", {})
    early_risks = detect_journal_writer_v1_risks(data, context, sequence, metrics, report_placeholder)
    score_placeholder = JournalWriterV1Score(0, 0, 0, 0, 0, 0, 0, 0, 0)
    result = JournalWriterV1Result(
        state=State.NOT_READY,
        decision=Decision.BLOCK_JOURNAL_WRITER_V1,
        score=score_placeholder,
        risks=early_risks,
        recommendations=generate_journal_writer_v1_recommendations(early_risks),
        context=context,
        sequence=sequence,
        metrics=metrics,
        report=None,
        offline_only=data is not None and data.offline_mode_enforced,
        in_memory_only=data is not None and data.in_memory_only,
        file_written=False,
        data_accessed=False,
        real_order_submitted=False,
        real_account_accessed=False,
        position_mutated=False,
    )
    report = None if data is None or data.force_report_missing else _build_report(result)
    risks = detect_journal_writer_v1_risks(data, context, sequence, metrics, report)
    score = _build_score(data, context, sequence, metrics, report, risks)
    recommendations = generate_journal_writer_v1_recommendations(risks)
    final = JournalWriterV1Result(
        state=_state_for(risks, score),
        decision=_decision_for(risks),
        score=score,
        risks=risks,
        recommendations=recommendations,
        context=context,
        sequence=sequence,
        metrics=metrics,
        report=None,
        offline_only=data is not None and data.offline_mode_enforced,
        in_memory_only=data is not None and data.in_memory_only,
        file_written=False,
        data_accessed=False,
        real_order_submitted=False,
        real_account_accessed=False,
        position_mutated=False,
    )
    report = None if data is None or data.force_report_missing else _build_report(final)
    return JournalWriterV1Result(**{**final.__dict__, "report": report})


__all__ = [
    "build_journal_writer_v1",
    "validate_journal_writer_v1_input",
    "build_journal_context_v1",
    "build_journal_entry_v1",
    "build_journal_run_started_entry_v1",
    "build_journal_market_scenario_entry_v1",
    "build_journal_strategy_signal_entry_v1",
    "build_journal_broker_preview_entry_v1",
    "build_journal_risk_guard_entry_v1",
    "build_journal_read_only_decision_entry_v1",
    "build_journal_metrics_entry_v1",
    "build_journal_warning_entry_v1",
    "build_journal_blocked_decision_entry_v1",
    "build_journal_run_completed_entry_v1",
    "append_journal_entry_v1",
    "validate_journal_entry_v1",
    "validate_journal_sequence_v1",
    "validate_journal_writer_v1_integrity",
    "compute_journal_writer_v1_metrics",
    "detect_journal_writer_v1_risks",
    "generate_journal_writer_v1_recommendations",
    "render_journal_writer_v1_markdown_report",
    "render_journal_writer_v1_json_report",
    "assert_journal_writer_v1_offline_boundaries",
]
