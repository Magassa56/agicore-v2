"""Deterministic in-memory Markdown/JSON offline reports for AGIcore Trading."""

from __future__ import annotations

import json
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.offline_report_markdown_json_v1_models import (
    OfflineReportContextV1,
    OfflineReportJsonV1,
    OfflineReportMarkdownJsonV1Decision,
    OfflineReportMarkdownJsonV1Input,
    OfflineReportMarkdownJsonV1Recommendation,
    OfflineReportMarkdownJsonV1Result,
    OfflineReportMarkdownJsonV1Risk,
    OfflineReportMarkdownJsonV1Score,
    OfflineReportMarkdownJsonV1State,
    OfflineReportMarkdownV1,
    OfflineReportMetricsV1,
    OfflineReportSectionNameV1,
    OfflineReportSectionV1,
)


Risk = OfflineReportMarkdownJsonV1Risk
Recommendation = OfflineReportMarkdownJsonV1Recommendation
Decision = OfflineReportMarkdownJsonV1Decision
State = OfflineReportMarkdownJsonV1State
SectionName = OfflineReportSectionNameV1

EXPECTED_SECTIONS: tuple[SectionName, ...] = tuple(SectionName)


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


def _coerce_input(
    data: OfflineReportMarkdownJsonV1Input | Mapping[str, Any] | None,
) -> OfflineReportMarkdownJsonV1Input | None:
    if data is None:
        return None
    if isinstance(data, OfflineReportMarkdownJsonV1Input):
        return data
    allowed = {field.name for field in fields(OfflineReportMarkdownJsonV1Input)}
    return OfflineReportMarkdownJsonV1Input(
        **{key: value for key, value in dict(data).items() if key in allowed}
    )


def _parse_section_name(value: SectionName | str | None) -> SectionName | None:
    if isinstance(value, SectionName):
        return value
    if isinstance(value, str):
        try:
            return SectionName(value)
        except ValueError:
            return None
    return None


def _safe_payload(value: Any) -> Any:
    if value is None:
        return {}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {str(key): _safe_payload(val) for key, val in value.items()}
    if isinstance(value, tuple):
        return [_safe_payload(item) for item in value]
    if isinstance(value, list):
        return [_safe_payload(item) for item in value]
    if hasattr(value, "__dict__"):
        return {
            key: _safe_payload(val)
            for key, val in vars(value).items()
            if not key.startswith("_")
        }
    return str(value)


def _section_to_payload(section: OfflineReportSectionV1) -> dict[str, Any]:
    name = _parse_section_name(section.name)
    return {
        "name": _value(name or section.name),
        "title": section.title,
        "lines": list(section.lines),
        "payload": _safe_payload(section.payload),
    }


def _coerce_section(section: OfflineReportSectionV1 | Mapping[str, Any]) -> OfflineReportSectionV1:
    if isinstance(section, OfflineReportSectionV1):
        return section
    payload = dict(section)
    return OfflineReportSectionV1(
        name=payload.get("name", ""),
        title=str(payload.get("title", "")),
        lines=tuple(str(line) for line in payload.get("lines", ())),
        payload=dict(payload.get("payload", {})),
    )


def _boundary_risks(data: OfflineReportMarkdownJsonV1Input | None) -> tuple[Risk, ...]:
    if data is None:
        return ()
    risks: list[Risk] = []
    if data.file_write_requested or not data.no_file_write:
        risks.append(Risk.FILE_WRITE_BOUNDARY_VIOLATION)
    if data.real_data_access_requested or not data.no_real_data_access:
        risks.append(Risk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION)
    if (
        data.data_directory_read_requested
        or data.data_directory_write_requested
        or not data.no_data_directory_read
        or not data.no_data_directory_write
    ):
        risks.append(Risk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION)
    if data.broker_connection_requested or not data.no_real_broker or not data.no_alpaca_real:
        risks.append(Risk.REAL_BROKER_BOUNDARY_VIOLATION)
    if data.api_key_read_requested or data.env_var_read_requested or not data.no_api_key_read:
        risks.append(Risk.REAL_SECRET_BOUNDARY_VIOLATION)
    if not data.no_env_var_read or not data.no_hardcoded_secret:
        risks.append(Risk.REAL_SECRET_BOUNDARY_VIOLATION)
    if (
        data.network_requested
        or data.http_requested
        or data.websocket_requested
        or data.socket_requested
        or data.external_api_requested
        or not data.no_http_transport
        or not data.no_websocket_transport
        or not data.no_socket_transport
        or not data.no_external_api
        or not data.no_external_ml
        or not data.no_external_llm
    ):
        risks.append(Risk.NETWORK_BOUNDARY_VIOLATION)
    if data.order_execution_requested or not data.no_real_order:
        risks.append(Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION)
    if data.account_access_requested or not data.no_real_account_access:
        risks.append(Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION)
    if data.position_mutation_requested or not data.no_position_mutation:
        risks.append(Risk.POSITION_MUTATION_BOUNDARY_VIOLATION)
    if not data.offline_mode_enforced or not data.sandbox_mode_enforced:
        risks.append(Risk.NETWORK_BOUNDARY_VIOLATION)
    if not data.in_memory_only or not data.report_in_memory_only:
        risks.append(Risk.FILE_WRITE_BOUNDARY_VIOLATION)
    return _dedupe(risks)


def validate_offline_report_markdown_json_v1_input(
    data: OfflineReportMarkdownJsonV1Input | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.run_id and payload.symbol and isinstance(payload.score, int))


def build_offline_report_context_v1(
    data: OfflineReportMarkdownJsonV1Input | Mapping[str, Any],
) -> OfflineReportContextV1:
    payload = _coerce_input(data)
    if payload is None:
        raise ValueError("offline report input is required")
    if payload.force_context_invalid:
        return OfflineReportContextV1(run_id="", symbol="", decision="", score=-1)
    return OfflineReportContextV1(
        run_id=payload.run_id,
        symbol=payload.symbol,
        decision=payload.decision,
        score=payload.score,
    )


def build_offline_report_summary_section_v1(
    context: OfflineReportContextV1,
    data: OfflineReportMarkdownJsonV1Input | Mapping[str, Any],
) -> OfflineReportSectionV1:
    payload = _coerce_input(data)
    blocked_reason = payload.blocked_reason if payload else ""
    lines = (
        f"Run: {context.run_id}",
        f"Symbol: {context.symbol}",
        f"Decision: {context.decision}",
        f"Score: {context.score}",
        f"Blocked reason: {blocked_reason or 'none'}",
    )
    return OfflineReportSectionV1(
        name=SectionName.SUMMARY,
        title="Summary",
        lines=lines,
        payload={
            "run_id": context.run_id,
            "symbol": context.symbol,
            "decision": context.decision,
            "score": context.score,
            "blocked_reason": blocked_reason,
        },
    )


def build_offline_report_market_scenario_section_v1(
    data: OfflineReportMarkdownJsonV1Input | Mapping[str, Any],
) -> OfflineReportSectionV1:
    payload = _coerce_input(data)
    scenario = _safe_payload(payload.market_scenario if payload else {})
    return OfflineReportSectionV1(
        name=SectionName.MARKET_SCENARIO,
        title="Market Scenario",
        lines=("Synthetic market scenario captured in memory.", f"Payload: {scenario}"),
        payload={"market_scenario": scenario},
    )


def build_offline_report_broker_section_v1(
    data: OfflineReportMarkdownJsonV1Input | Mapping[str, Any],
) -> OfflineReportSectionV1:
    payload = _coerce_input(data)
    broker = _safe_payload(payload.broker_result if payload else {})
    return OfflineReportSectionV1(
        name=SectionName.SIMULATED_BROKER,
        title="Simulated Broker",
        lines=("Simulated broker preview only.", f"Payload: {broker}"),
        payload={"broker_result": broker, "real_order_submitted": False},
    )


def build_offline_report_risk_guard_section_v1(
    data: OfflineReportMarkdownJsonV1Input | Mapping[str, Any],
) -> OfflineReportSectionV1:
    payload = _coerce_input(data)
    risk_guard = _safe_payload(payload.risk_guard_result if payload else {})
    return OfflineReportSectionV1(
        name=SectionName.RISK_GUARDS,
        title="Risk Guards",
        lines=("Risk guard result captured.", f"Payload: {risk_guard}"),
        payload={"risk_guard_result": risk_guard},
    )


def build_offline_report_journal_section_v1(
    data: OfflineReportMarkdownJsonV1Input | Mapping[str, Any],
) -> OfflineReportSectionV1:
    payload = _coerce_input(data)
    journal = _safe_payload(payload.journal_result if payload else {})
    return OfflineReportSectionV1(
        name=SectionName.JOURNAL,
        title="Journal",
        lines=("Journal summary captured in memory.", f"Payload: {journal}"),
        payload={"journal_result": journal},
    )


def build_offline_report_metrics_section_v1(
    data: OfflineReportMarkdownJsonV1Input | Mapping[str, Any],
) -> OfflineReportSectionV1:
    payload = _coerce_input(data)
    metrics = _safe_payload(payload.metrics if payload else {})
    return OfflineReportSectionV1(
        name=SectionName.METRICS,
        title="Metrics",
        lines=("Offline runner metrics captured.", f"Payload: {metrics}"),
        payload={"metrics": metrics},
    )


def build_offline_report_warnings_section_v1(
    data: OfflineReportMarkdownJsonV1Input | Mapping[str, Any],
) -> OfflineReportSectionV1:
    payload = _coerce_input(data)
    warnings = tuple(payload.warnings) if payload else ()
    lines = tuple(warnings) if warnings else ("No warnings.",)
    return OfflineReportSectionV1(
        name=SectionName.WARNINGS,
        title="Warnings",
        lines=lines,
        payload={"warnings": list(warnings)},
    )


def build_offline_report_next_actions_section_v1(
    data: OfflineReportMarkdownJsonV1Input | Mapping[str, Any],
) -> OfflineReportSectionV1:
    payload = _coerce_input(data)
    next_actions = tuple(payload.next_actions) if payload else ()
    lines = tuple(next_actions) if next_actions else ("No next action defined.",)
    return OfflineReportSectionV1(
        name=SectionName.NEXT_ACTIONS,
        title="Next Actions",
        lines=lines,
        payload={"next_actions": list(next_actions)},
    )


def _build_default_sections(
    context: OfflineReportContextV1,
    data: OfflineReportMarkdownJsonV1Input,
) -> tuple[OfflineReportSectionV1, ...]:
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
    return sections[:-1] if data.force_section_missing else sections


def render_offline_report_markdown_v1(
    context: OfflineReportContextV1,
    sections: tuple[OfflineReportSectionV1, ...],
) -> OfflineReportMarkdownV1:
    lines = [
        "# Offline Report Markdown JSON v1",
        "",
        f"- run_id: {context.run_id}",
        f"- symbol: {context.symbol}",
        f"- decision: {context.decision}",
        f"- score: {context.score}",
        "",
    ]
    for section in sections:
        name = _parse_section_name(section.name)
        section_label = _value(name or section.name)
        lines.append(f"## {section_label}")
        lines.append("")
        lines.append(f"### {section.title}")
        lines.extend(f"- {line}" for line in section.lines)
        lines.append("")
    return OfflineReportMarkdownV1(content="\n".join(lines).strip() + "\n")


def render_offline_report_json_dict_v1(
    context: OfflineReportContextV1,
    sections: tuple[OfflineReportSectionV1, ...],
    metrics: OfflineReportMetricsV1 | None = None,
) -> dict[str, Any]:
    section_payloads = [_section_to_payload(section) for section in sections]
    return {
        "schema": "offline_report_markdown_json_v1",
        "context": {
            "run_id": context.run_id,
            "symbol": context.symbol,
            "decision": context.decision,
            "score": context.score,
            "next_phase": context.next_phase,
            "deterministic": context.deterministic,
            "offline_only": context.offline_only,
            "in_memory_only": context.in_memory_only,
        },
        "sections": {item["name"]: item for item in section_payloads},
        "section_order": [item["name"] for item in section_payloads],
        "metrics": _safe_payload(metrics) if metrics else {},
    }


def render_offline_report_json_string_v1(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def validate_offline_report_markdown_v1(
    markdown: OfflineReportMarkdownV1 | str | None,
) -> bool:
    content = markdown.content if isinstance(markdown, OfflineReportMarkdownV1) else markdown
    if not isinstance(content, str) or not content.strip():
        return False
    if "# Offline Report Markdown JSON v1" not in content:
        return False
    return all(f"## {_value(section)}" in content for section in EXPECTED_SECTIONS)


def validate_offline_report_json_v1(json_report: OfflineReportJsonV1 | Mapping[str, Any] | None) -> bool:
    if isinstance(json_report, OfflineReportJsonV1):
        payload = json_report.payload
        serialized = json_report.serialized
    elif isinstance(json_report, Mapping):
        payload = dict(json_report)
        serialized = render_offline_report_json_string_v1(payload)
    else:
        return False
    if not isinstance(payload, dict) or "context" not in payload or "sections" not in payload:
        return False
    try:
        parsed = json.loads(serialized)
    except (TypeError, ValueError):
        return False
    if not isinstance(parsed, dict):
        return False
    sections = payload.get("sections")
    if not isinstance(sections, dict):
        return False
    return all(_value(section) in sections for section in EXPECTED_SECTIONS)


def _validate_context(context: OfflineReportContextV1 | None) -> bool:
    return bool(
        context
        and context.run_id
        and context.symbol
        and context.decision
        and 0 <= context.score <= 100
        and context.offline_only
        and context.in_memory_only
    )


def _validate_sections(sections: tuple[OfflineReportSectionV1, ...]) -> bool:
    names = {_parse_section_name(section.name) for section in sections}
    if any(name is None for name in names):
        return False
    if set(EXPECTED_SECTIONS) != names:
        return False
    return all(section.title and section.lines for section in sections)


def compute_offline_report_markdown_json_v1_score(
    data: OfflineReportMarkdownJsonV1Input | Mapping[str, Any] | None,
    context: OfflineReportContextV1 | None = None,
    sections: tuple[OfflineReportSectionV1, ...] = (),
    markdown: OfflineReportMarkdownV1 | None = None,
    json_report: OfflineReportJsonV1 | None = None,
    metrics: OfflineReportMetricsV1 | None = None,
    risks: tuple[Risk, ...] = (),
) -> OfflineReportMarkdownJsonV1Score:
    payload = _coerce_input(data)
    input_score = 100 if validate_offline_report_markdown_json_v1_input(payload) else 0
    context_score = 100 if _validate_context(context) else 0
    section_score = 100 if _validate_sections(sections) else 0
    markdown_score = 100 if validate_offline_report_markdown_v1(markdown) else 0
    json_score = 100 if validate_offline_report_json_v1(json_report) else 0
    metrics_score = 100 if metrics and metrics.complete else 0
    boundary_score = 100 if not _boundary_risks(payload) else 0
    parts = (
        input_score,
        context_score,
        section_score,
        markdown_score,
        json_score,
        metrics_score,
        boundary_score,
    )
    overall = min(parts)
    if risks:
        overall = min(overall, max(0, 100 - (len(risks) * 10)))
    return OfflineReportMarkdownJsonV1Score(
        overall_score=overall,
        input_score=input_score,
        context_score=context_score,
        section_score=section_score,
        markdown_score=markdown_score,
        json_score=json_score,
        metrics_score=metrics_score,
        boundary_score=boundary_score,
    )


def _compute_metrics(
    sections: tuple[OfflineReportSectionV1, ...],
    markdown: OfflineReportMarkdownV1 | None,
    json_report: OfflineReportJsonV1 | None,
    warning_count: int,
    risk_count: int = 0,
    recommendation_count: int = 0,
) -> OfflineReportMetricsV1:
    return OfflineReportMetricsV1(
        section_count=len(sections),
        warning_count=warning_count,
        risk_count=risk_count,
        recommendation_count=recommendation_count,
        markdown_length=len(markdown.content) if markdown else 0,
        json_key_count=len(json_report.payload) if json_report else 0,
        complete=len(sections) == len(EXPECTED_SECTIONS) and bool(markdown and json_report),
    )


def detect_offline_report_markdown_json_v1_risks(
    data: OfflineReportMarkdownJsonV1Input | Mapping[str, Any] | None,
    context: OfflineReportContextV1 | None = None,
    sections: tuple[OfflineReportSectionV1, ...] = (),
    markdown: OfflineReportMarkdownV1 | None = None,
    json_report: OfflineReportJsonV1 | None = None,
    metrics: OfflineReportMetricsV1 | None = None,
) -> tuple[Risk, ...]:
    payload = _coerce_input(data)
    risks: list[Risk] = []
    if not validate_offline_report_markdown_json_v1_input(payload):
        risks.append(Risk.OFFLINE_REPORT_INPUT_MISSING)
    if not _validate_context(context):
        risks.append(Risk.OFFLINE_REPORT_CONTEXT_INVALID)
    if not _validate_sections(sections):
        risks.append(Risk.OFFLINE_REPORT_SECTION_MISSING)
    if not validate_offline_report_markdown_v1(markdown):
        risks.append(Risk.OFFLINE_REPORT_MARKDOWN_INVALID)
    if not validate_offline_report_json_v1(json_report):
        risks.append(Risk.OFFLINE_REPORT_JSON_INVALID)
    if not metrics or not metrics.complete:
        risks.append(Risk.OFFLINE_REPORT_METRICS_MISSING)
    risks.extend(_boundary_risks(payload))
    return _dedupe(risks)


def generate_offline_report_markdown_json_v1_recommendations(
    risks: Iterable[Risk],
) -> tuple[Recommendation, ...]:
    mapping = {
        Risk.OFFLINE_REPORT_INPUT_MISSING: Recommendation.PROVIDE_OFFLINE_REPORT_INPUT,
        Risk.OFFLINE_REPORT_CONTEXT_INVALID: Recommendation.FIX_OFFLINE_REPORT_CONTEXT,
        Risk.OFFLINE_REPORT_SECTION_MISSING: Recommendation.PROVIDE_ALL_OFFLINE_REPORT_SECTIONS,
        Risk.OFFLINE_REPORT_MARKDOWN_INVALID: Recommendation.FIX_OFFLINE_REPORT_MARKDOWN,
        Risk.OFFLINE_REPORT_JSON_INVALID: Recommendation.FIX_OFFLINE_REPORT_JSON,
        Risk.OFFLINE_REPORT_METRICS_MISSING: Recommendation.COMPUTE_OFFLINE_REPORT_METRICS,
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
    recommendations = [mapping[risk] for risk in risks if risk in mapping]
    recommendations.append(Recommendation.RUN_OFFLINE_REPORT_MARKDOWN_JSON_V1_TEST_SUITE)
    if not recommendations or recommendations == [Recommendation.RUN_OFFLINE_REPORT_MARKDOWN_JSON_V1_TEST_SUITE]:
        recommendations.append(Recommendation.APPROVE_CSV_REPLAY_INPUT_V1_PREPARATION)
    return _dedupe(recommendations)


def assert_offline_report_markdown_json_v1_boundaries(
    data: OfflineReportMarkdownJsonV1Input | Mapping[str, Any] | None,
) -> bool:
    return not _boundary_risks(_coerce_input(data))


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_OFFLINE_REPORT_MARKDOWN_JSON_V1
    boundary_set = {
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
    if any(risk in boundary_set for risk in risks):
        return Decision.BLOCK_OFFLINE_REPORT_MARKDOWN_JSON_V1
    if Risk.OFFLINE_REPORT_INPUT_MISSING in risks:
        return Decision.REQUIRE_OFFLINE_REPORT_INPUT_FIXES
    if Risk.OFFLINE_REPORT_CONTEXT_INVALID in risks:
        return Decision.REQUIRE_OFFLINE_REPORT_CONTEXT_FIXES
    if Risk.OFFLINE_REPORT_SECTION_MISSING in risks:
        return Decision.REQUIRE_OFFLINE_REPORT_SECTION_FIXES
    if Risk.OFFLINE_REPORT_MARKDOWN_INVALID in risks:
        return Decision.REQUIRE_OFFLINE_REPORT_MARKDOWN_FIXES
    if Risk.OFFLINE_REPORT_JSON_INVALID in risks:
        return Decision.REQUIRE_OFFLINE_REPORT_JSON_FIXES
    if Risk.OFFLINE_REPORT_METRICS_MISSING in risks:
        return Decision.REQUIRE_OFFLINE_REPORT_METRICS_FIXES
    return Decision.BLOCK_OFFLINE_REPORT_MARKDOWN_JSON_V1


def _state_for(risks: tuple[Risk, ...], decision: Decision) -> State:
    if Risk.OFFLINE_REPORT_INPUT_MISSING in risks:
        return State.OFFLINE_REPORT_MARKDOWN_JSON_V1_INPUT_INVALID
    if decision is Decision.APPROVE_OFFLINE_REPORT_MARKDOWN_JSON_V1:
        return State.READY_FOR_CSV_REPLAY_INPUT_V1
    return State.OFFLINE_REPORT_MARKDOWN_JSON_V1_BLOCKED


def build_offline_report_markdown_json_v1(
    data: OfflineReportMarkdownJsonV1Input | Mapping[str, Any] | None,
) -> OfflineReportMarkdownJsonV1Result:
    payload = _coerce_input(data)
    context = build_offline_report_context_v1(payload) if payload else None
    sections: tuple[OfflineReportSectionV1, ...] = ()
    markdown: OfflineReportMarkdownV1 | None = None
    json_report: OfflineReportJsonV1 | None = None
    metrics: OfflineReportMetricsV1 | None = None

    if payload and context:
        if payload.custom_sections is not None:
            sections = tuple(_coerce_section(section) for section in payload.custom_sections)
        else:
            sections = _build_default_sections(context, payload)
        markdown = OfflineReportMarkdownV1("") if payload.force_markdown_invalid else render_offline_report_markdown_v1(context, sections)
        if payload.force_json_invalid:
            json_report = OfflineReportJsonV1(payload={}, serialized="{invalid-json")
        else:
            base_metrics = _compute_metrics(sections, markdown, None, len(payload.warnings))
            json_payload = render_offline_report_json_dict_v1(context, sections, base_metrics)
            json_report = OfflineReportJsonV1(
                payload=json_payload,
                serialized=render_offline_report_json_string_v1(json_payload),
            )
        if not payload.force_metrics_missing:
            metrics = _compute_metrics(sections, markdown, json_report, len(payload.warnings))
            if json_report and validate_offline_report_json_v1(json_report):
                refreshed_payload = render_offline_report_json_dict_v1(context, sections, metrics)
                json_report = OfflineReportJsonV1(
                    payload=refreshed_payload,
                    serialized=render_offline_report_json_string_v1(refreshed_payload),
                )

    risks = detect_offline_report_markdown_json_v1_risks(
        payload,
        context=context,
        sections=sections,
        markdown=markdown,
        json_report=json_report,
        metrics=metrics,
    )
    recommendations = generate_offline_report_markdown_json_v1_recommendations(risks)
    if metrics is not None:
        metrics = OfflineReportMetricsV1(
            section_count=metrics.section_count,
            warning_count=metrics.warning_count,
            risk_count=len(risks),
            recommendation_count=len(recommendations),
            markdown_length=metrics.markdown_length,
            json_key_count=metrics.json_key_count,
            complete=metrics.complete,
        )
        if json_report and validate_offline_report_json_v1(json_report):
            refreshed_payload = render_offline_report_json_dict_v1(context, sections, metrics)  # type: ignore[arg-type]
            json_report = OfflineReportJsonV1(
                payload=refreshed_payload,
                serialized=render_offline_report_json_string_v1(refreshed_payload),
            )
    score = compute_offline_report_markdown_json_v1_score(
        payload,
        context=context,
        sections=sections,
        markdown=markdown,
        json_report=json_report,
        metrics=metrics,
        risks=risks,
    )
    decision = _decision_for(risks)
    state = _state_for(risks, decision)
    return OfflineReportMarkdownJsonV1Result(
        state=state,
        decision=decision,
        score=score,
        risks=risks,
        recommendations=recommendations,
        context=context,
        sections=sections,
        markdown=markdown,
        json_report=json_report,
        metrics=metrics,
        offline_only=True,
        in_memory_only=True,
        file_written=False,
        data_accessed=False,
        real_order_submitted=False,
        real_account_accessed=False,
        position_mutated=False,
    )
