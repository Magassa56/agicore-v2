"""AGIcore Trading v1 offline candidate evaluator."""

from __future__ import annotations

import json
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.agicore_trading_v1_candidate_models import (
    AGIcoreTradingV1CandidateContext,
    AGIcoreTradingV1CandidateDecision,
    AGIcoreTradingV1CandidateInput,
    AGIcoreTradingV1CandidateMetrics,
    AGIcoreTradingV1CandidateRecommendation,
    AGIcoreTradingV1CandidateReport,
    AGIcoreTradingV1CandidateResult,
    AGIcoreTradingV1CandidateRisk,
    AGIcoreTradingV1CandidateScore,
    AGIcoreTradingV1CandidateState,
    AGIcoreTradingV1CapabilityCheck,
    AGIcoreTradingV1CapabilityName,
    AGIcoreTradingV1SmokeReplayResult,
)
from agicore.trading.csv_replay_input_v1 import build_csv_replay_input_v1
from agicore.trading.csv_replay_input_v1_models import CsvReplayInputV1Input
from agicore.trading.journal_writer_v1 import build_journal_writer_v1
from agicore.trading.journal_writer_v1_models import JournalWriterV1Input
from agicore.trading.offline_report_markdown_json_v1 import build_offline_report_markdown_json_v1
from agicore.trading.offline_report_markdown_json_v1_models import OfflineReportMarkdownJsonV1Input
from agicore.trading.risk_guard_enforcement_v1 import enforce_risk_guard_v1
from agicore.trading.risk_guard_enforcement_v1_models import RiskGuardEnforcementV1Input
from agicore.trading.simulated_broker_stub_v1 import build_simulated_broker_stub_v1
from agicore.trading.simulated_broker_stub_v1_models import SimulatedBrokerStubV1Input
from agicore.trading.strategy_replay_engine_v1 import run_strategy_replay_engine_v1
from agicore.trading.strategy_replay_engine_v1_models import (
    StrategyReplayEngineV1Input,
    StrategyReplayStrategyTypeV1,
)
from agicore.trading.synthetic_market_scenario_v1 import build_synthetic_market_scenario_v1
from agicore.trading.synthetic_market_scenario_v1_models import (
    SyntheticMarketScenarioV1Input,
    SyntheticMarketScenarioV1Profile,
)


Risk = AGIcoreTradingV1CandidateRisk
Recommendation = AGIcoreTradingV1CandidateRecommendation
Decision = AGIcoreTradingV1CandidateDecision
State = AGIcoreTradingV1CandidateState
Capability = AGIcoreTradingV1CapabilityName

EXPECTED_CAPABILITIES: tuple[Capability, ...] = tuple(Capability)


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
    data: AGIcoreTradingV1CandidateInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1CandidateInput | None:
    if data is None:
        return None
    if isinstance(data, AGIcoreTradingV1CandidateInput):
        return data
    allowed = {field.name for field in fields(AGIcoreTradingV1CandidateInput)}
    return AGIcoreTradingV1CandidateInput(**{key: value for key, value in dict(data).items() if key in allowed})


def _boundary_risks(data: AGIcoreTradingV1CandidateInput | None) -> tuple[Risk, ...]:
    if data is None:
        return ()
    risks: list[Risk] = []
    if data.file_read_requested or not data.no_file_read:
        risks.append(Risk.FILE_READ_BOUNDARY_VIOLATION)
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
    if not data.in_memory_only or not data.candidate_in_memory_only:
        risks.append(Risk.FILE_READ_BOUNDARY_VIOLATION)
    return _dedupe(risks)


def validate_agicore_trading_v1_candidate_input(
    data: AGIcoreTradingV1CandidateInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(
        payload
        and payload.candidate_id
        and payload.version
        and assert_agicore_trading_v1_candidate_offline_boundaries(payload)
    )


def build_agicore_trading_v1_candidate_context(
    data: AGIcoreTradingV1CandidateInput | Mapping[str, Any],
) -> AGIcoreTradingV1CandidateContext:
    payload = _coerce_input(data)
    if payload is None:
        raise ValueError("AGIcore Trading v1 candidate input is required")
    return AGIcoreTradingV1CandidateContext(
        candidate_id=payload.candidate_id,
        version=payload.version,
        capability_count=len(EXPECTED_CAPABILITIES),
    )


def _check(
    capability: Capability,
    passed: bool,
    detail: str,
    component_decision: str = "",
    risks: Iterable[Any] = (),
) -> AGIcoreTradingV1CapabilityCheck:
    return AGIcoreTradingV1CapabilityCheck(
        capability=capability,
        passed=passed,
        detail=detail,
        component_decision=component_decision,
        risks=tuple(_value(risk) for risk in risks),
    )


def _sample_csv() -> str:
    return (
        "timestamp,open,high,low,close,volume\n"
        "2026-01-01T00:00:00,100,105,99,104,1000\n"
        "2026-01-01T00:01:00,104,108,103,107,1200\n"
        "2026-01-01T00:02:00,107,110,106,109,1400\n"
        "2026-01-01T00:03:00,109,112,108,111,1600\n"
    )


def _sample_bars() -> tuple[dict[str, float | str], ...]:
    return (
        {"timestamp": "2026-01-01T00:00:00", "open": 100.0, "high": 105.0, "low": 99.0, "close": 104.0, "volume": 1000.0},
        {"timestamp": "2026-01-01T00:01:00", "open": 104.0, "high": 108.0, "low": 103.0, "close": 107.0, "volume": 1200.0},
        {"timestamp": "2026-01-01T00:02:00", "open": 107.0, "high": 110.0, "low": 106.0, "close": 109.0, "volume": 1400.0},
        {"timestamp": "2026-01-01T00:03:00", "open": 109.0, "high": 112.0, "low": 108.0, "close": 111.0, "volume": 1600.0},
    )


def validate_v1_candidate_csv_replay_capability(
    data: AGIcoreTradingV1CandidateInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1CapabilityCheck:
    payload = _coerce_input(data)
    if payload and payload.force_csv_replay_capability_missing:
        return _check(Capability.CSV_REPLAY_INPUT, False, "csv replay capability forced missing")
    result = build_csv_replay_input_v1(CsvReplayInputV1Input(csv_content=_sample_csv()))
    return _check(
        Capability.CSV_REPLAY_INPUT,
        not result.risks and result.dataset is not None,
        "CSV replay parses in-memory OHLCV string",
        result.decision.value,
        result.risks,
    )


def validate_v1_candidate_synthetic_market_capability(
    data: AGIcoreTradingV1CandidateInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1CapabilityCheck:
    payload = _coerce_input(data)
    if payload and payload.force_synthetic_market_capability_missing:
        return _check(Capability.SYNTHETIC_MARKET_SCENARIO, False, "synthetic market capability forced missing")
    result = build_synthetic_market_scenario_v1(
        SyntheticMarketScenarioV1Input(profile=SyntheticMarketScenarioV1Profile.TREND_UP, bar_count=4)
    )
    return _check(
        Capability.SYNTHETIC_MARKET_SCENARIO,
        not result.risks and result.scenario is not None,
        "Synthetic market scenario generates deterministic bars",
        result.decision.value,
        result.risks,
    )


def validate_v1_candidate_strategy_replay_capability(
    data: AGIcoreTradingV1CandidateInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1CapabilityCheck:
    payload = _coerce_input(data)
    if payload and payload.force_strategy_replay_capability_missing:
        return _check(Capability.STRATEGY_REPLAY_ENGINE, False, "strategy replay capability forced missing")
    result = run_strategy_replay_engine_v1(
        StrategyReplayEngineV1Input(bars=_sample_bars(), strategy_type=StrategyReplayStrategyTypeV1.MOVING_AVERAGE_CROSSOVER)
    )
    return _check(
        Capability.STRATEGY_REPLAY_ENGINE,
        not result.risks and result.read_only_decision is not None and not result.read_only_decision.order_submitted,
        "Strategy replay engine produces read-only replay",
        result.decision.value,
        result.risks,
    )


def validate_v1_candidate_simulated_broker_capability(
    data: AGIcoreTradingV1CandidateInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1CapabilityCheck:
    payload = _coerce_input(data)
    if payload and payload.force_simulated_broker_capability_missing:
        return _check(Capability.SIMULATED_BROKER_STUB, False, "simulated broker capability forced missing")
    result = build_simulated_broker_stub_v1(SimulatedBrokerStubV1Input())
    return _check(
        Capability.SIMULATED_BROKER_STUB,
        not result.risks and result.order_preview is not None and not result.order_preview.order_submitted,
        "Simulated broker stub creates read-only preview",
        result.decision.value,
        result.risks,
    )


def validate_v1_candidate_risk_guard_capability(
    data: AGIcoreTradingV1CandidateInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1CapabilityCheck:
    payload = _coerce_input(data)
    if payload and payload.force_risk_guard_capability_missing:
        return _check(Capability.RISK_GUARD_ENFORCEMENT, False, "risk guard capability forced missing")
    result = enforce_risk_guard_v1(RiskGuardEnforcementV1Input())
    return _check(
        Capability.RISK_GUARD_ENFORCEMENT,
        not result.risks and result.summary is not None and result.summary.all_passed,
        "Risk guard enforcement validates offline limits",
        result.decision.value,
        result.risks,
    )


def validate_v1_candidate_journal_capability(
    data: AGIcoreTradingV1CandidateInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1CapabilityCheck:
    payload = _coerce_input(data)
    if payload and payload.force_journal_capability_missing:
        return _check(Capability.JOURNAL_WRITER, False, "journal capability forced missing")
    result = build_journal_writer_v1(
        JournalWriterV1Input(
            market_scenario={"bars": 4},
            strategy_signal={"action": "BUY"},
            broker_preview={"read_only": True},
            risk_guard_result={"passed": True},
            read_only_decision={"order_submitted": False},
            runner_metrics={"bar_count": 4},
        )
    )
    return _check(
        Capability.JOURNAL_WRITER,
        not result.risks and result.metrics is not None and result.metrics.complete,
        "Journal writer records an in-memory run",
        result.decision.value,
        result.risks,
    )


def validate_v1_candidate_offline_report_capability(
    data: AGIcoreTradingV1CandidateInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1CapabilityCheck:
    payload = _coerce_input(data)
    if payload and payload.force_offline_report_capability_missing:
        return _check(Capability.OFFLINE_REPORT_MARKDOWN_JSON, False, "offline report capability forced missing")
    result = build_offline_report_markdown_json_v1(
        OfflineReportMarkdownJsonV1Input(
            market_scenario={"bars": 4},
            broker_result={"read_only": True},
            risk_guard_result={"passed": True},
            journal_result={"complete": True},
            metrics={"bar_count": 4},
        )
    )
    return _check(
        Capability.OFFLINE_REPORT_MARKDOWN_JSON,
        not result.risks and result.markdown is not None and result.json_report is not None,
        "Offline report produces Markdown and JSON in memory",
        result.decision.value,
        result.risks,
    )


def run_agicore_trading_v1_candidate_smoke_replay(
    data: AGIcoreTradingV1CandidateInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1SmokeReplayResult:
    payload = _coerce_input(data)
    if payload and payload.force_smoke_replay_failed:
        return AGIcoreTradingV1SmokeReplayResult(False, "FAILED", "", "", 0)
    csv_result = build_csv_replay_input_v1(CsvReplayInputV1Input(csv_content=_sample_csv()))
    bars = tuple(csv_result.dataset.bars) if csv_result.dataset else _sample_bars()
    replay = run_strategy_replay_engine_v1(
        StrategyReplayEngineV1Input(bars=bars, strategy_type=StrategyReplayStrategyTypeV1.MOVING_AVERAGE_CROSSOVER)
    )
    passed = not replay.risks and replay.read_only_decision is not None and not replay.read_only_decision.order_submitted
    return AGIcoreTradingV1SmokeReplayResult(
        passed=passed,
        status="PASSED" if passed else "FAILED",
        strategy_decision=replay.decision.value,
        strategy_state=replay.state.value,
        score=replay.score.overall_score,
        read_only=True,
        offline_only=True,
        real_order_submitted=False,
        real_account_accessed=False,
        position_mutated=False,
        replay_result=replay,
    )


def compute_agicore_trading_v1_candidate_metrics(
    capability_checks: tuple[AGIcoreTradingV1CapabilityCheck, ...],
    smoke_replay: AGIcoreTradingV1SmokeReplayResult | None,
    final_decision: str = "",
    data: AGIcoreTradingV1CandidateInput | Mapping[str, Any] | None = None,
) -> AGIcoreTradingV1CandidateMetrics | None:
    payload = _coerce_input(data)
    if payload and payload.force_metrics_missing:
        return None
    validated = sum(1 for check in capability_checks if check.passed)
    failed = len(capability_checks) - validated
    smoke_status = smoke_replay.status if smoke_replay else "MISSING"
    score = int(round((validated / len(EXPECTED_CAPABILITIES)) * 100)) if EXPECTED_CAPABILITIES else 0
    if not smoke_replay or not smoke_replay.passed:
        score = min(score, 80)
    return AGIcoreTradingV1CandidateMetrics(
        expected_capability_count=len(EXPECTED_CAPABILITIES),
        validated_capability_count=validated,
        failed_capability_count=failed,
        smoke_replay_status=smoke_status,
        global_score=score,
        final_decision=final_decision,
    )


def _capability_risks(checks: tuple[AGIcoreTradingV1CapabilityCheck, ...]) -> tuple[Risk, ...]:
    mapping = {
        Capability.CSV_REPLAY_INPUT: Risk.CSV_REPLAY_CAPABILITY_MISSING,
        Capability.SYNTHETIC_MARKET_SCENARIO: Risk.SYNTHETIC_MARKET_CAPABILITY_MISSING,
        Capability.STRATEGY_REPLAY_ENGINE: Risk.STRATEGY_REPLAY_CAPABILITY_MISSING,
        Capability.SIMULATED_BROKER_STUB: Risk.SIMULATED_BROKER_CAPABILITY_MISSING,
        Capability.RISK_GUARD_ENFORCEMENT: Risk.RISK_GUARD_CAPABILITY_MISSING,
        Capability.JOURNAL_WRITER: Risk.JOURNAL_CAPABILITY_MISSING,
        Capability.OFFLINE_REPORT_MARKDOWN_JSON: Risk.OFFLINE_REPORT_CAPABILITY_MISSING,
    }
    risks: list[Risk] = []
    for check in checks:
        capability = Capability(check.capability)
        if not check.passed:
            risks.append(mapping[capability])
    return tuple(risks)


def detect_agicore_trading_v1_candidate_risks(
    data: AGIcoreTradingV1CandidateInput | Mapping[str, Any] | None,
    capability_checks: tuple[AGIcoreTradingV1CapabilityCheck, ...] = (),
    smoke_replay: AGIcoreTradingV1SmokeReplayResult | None = None,
    metrics: AGIcoreTradingV1CandidateMetrics | None = None,
    report: AGIcoreTradingV1CandidateReport | None = None,
) -> tuple[Risk, ...]:
    payload = _coerce_input(data)
    risks: list[Risk] = []
    if payload is None:
        risks.append(Risk.AGICORE_TRADING_V1_INPUT_MISSING)
    risks.extend(_capability_risks(capability_checks))
    if smoke_replay is not None and not smoke_replay.passed:
        risks.append(Risk.V1_SMOKE_REPLAY_FAILED)
    if smoke_replay is None and payload is not None:
        risks.append(Risk.V1_SMOKE_REPLAY_FAILED)
    if metrics is None and payload is not None:
        risks.append(Risk.V1_CANDIDATE_METRICS_MISSING)
    if report is None and payload is not None:
        risks.append(Risk.V1_CANDIDATE_REPORT_MISSING)
    risks.extend(_boundary_risks(payload))
    return _dedupe(risks)


def compute_agicore_trading_v1_candidate_score(
    data: AGIcoreTradingV1CandidateInput | Mapping[str, Any] | None,
    capability_checks: tuple[AGIcoreTradingV1CapabilityCheck, ...] = (),
    smoke_replay: AGIcoreTradingV1SmokeReplayResult | None = None,
    metrics: AGIcoreTradingV1CandidateMetrics | None = None,
    report: AGIcoreTradingV1CandidateReport | None = None,
    risks: tuple[Risk, ...] = (),
) -> AGIcoreTradingV1CandidateScore:
    payload = _coerce_input(data)
    input_score = 100 if validate_agicore_trading_v1_candidate_input(payload) else 0
    capability_score = 100 if len(capability_checks) == len(EXPECTED_CAPABILITIES) and all(check.passed for check in capability_checks) else 0
    smoke_score = 100 if smoke_replay and smoke_replay.passed else 0
    metrics_score = 100 if metrics else 0
    report_score = 100 if report and report.markdown and report.json else 0
    boundary_score = 100 if not _boundary_risks(payload) else 0
    overall = min(input_score, capability_score, smoke_score, metrics_score, report_score, boundary_score)
    if risks:
        overall = min(overall, max(0, 100 - len(risks) * 10))
    return AGIcoreTradingV1CandidateScore(
        overall_score=overall,
        input_score=input_score,
        capability_score=capability_score,
        smoke_replay_score=smoke_score,
        metrics_score=metrics_score,
        report_score=report_score,
        boundary_score=boundary_score,
    )


def generate_agicore_trading_v1_candidate_recommendations(
    risks: Iterable[Risk],
) -> tuple[Recommendation, ...]:
    mapping = {
        Risk.AGICORE_TRADING_V1_INPUT_MISSING: Recommendation.PROVIDE_AGICORE_TRADING_V1_INPUT,
        Risk.CSV_REPLAY_CAPABILITY_MISSING: Recommendation.FIX_CSV_REPLAY_CAPABILITY,
        Risk.SYNTHETIC_MARKET_CAPABILITY_MISSING: Recommendation.FIX_SYNTHETIC_MARKET_CAPABILITY,
        Risk.STRATEGY_REPLAY_CAPABILITY_MISSING: Recommendation.FIX_STRATEGY_REPLAY_CAPABILITY,
        Risk.SIMULATED_BROKER_CAPABILITY_MISSING: Recommendation.FIX_SIMULATED_BROKER_CAPABILITY,
        Risk.RISK_GUARD_CAPABILITY_MISSING: Recommendation.FIX_RISK_GUARD_CAPABILITY,
        Risk.JOURNAL_CAPABILITY_MISSING: Recommendation.FIX_JOURNAL_CAPABILITY,
        Risk.OFFLINE_REPORT_CAPABILITY_MISSING: Recommendation.FIX_OFFLINE_REPORT_CAPABILITY,
        Risk.V1_SMOKE_REPLAY_FAILED: Recommendation.FIX_V1_SMOKE_REPLAY,
        Risk.V1_CANDIDATE_METRICS_MISSING: Recommendation.COMPUTE_V1_CANDIDATE_METRICS,
        Risk.V1_CANDIDATE_REPORT_MISSING: Recommendation.GENERATE_V1_CANDIDATE_REPORT,
        Risk.FILE_READ_BOUNDARY_VIOLATION: Recommendation.REMOVE_FILE_READ,
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
    recommendations.append(Recommendation.RUN_AGICORE_TRADING_V1_CANDIDATE_TEST_SUITE)
    if not recommendations or recommendations == [Recommendation.RUN_AGICORE_TRADING_V1_CANDIDATE_TEST_SUITE]:
        recommendations.append(Recommendation.APPROVE_AGICORE_TRADING_V1_CANDIDATE_REVIEW)
    return _dedupe(recommendations)


def _payload_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {str(key): _payload_value(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_payload_value(item) for item in value]
    if isinstance(value, list):
        return [_payload_value(item) for item in value]
    if hasattr(value, "__dict__"):
        return {key: _payload_value(item) for key, item in vars(value).items() if not key.startswith("_") and key != "replay_result"}
    return str(value)


def render_agicore_trading_v1_candidate_markdown_report(
    result: AGIcoreTradingV1CandidateResult | Mapping[str, Any],
) -> str:
    if not isinstance(result, AGIcoreTradingV1CandidateResult):
        return "# AGIcore Trading v1 Candidate\n"
    lines = [
        "# AGIcore Trading v1 Candidate",
        "",
        f"- decision: {result.decision.value}",
        f"- state: {result.state.value}",
        f"- score: {result.score.overall_score}",
        f"- capabilities_expected: {len(EXPECTED_CAPABILITIES)}",
        f"- capabilities_validated: {result.metrics.validated_capability_count if result.metrics else 0}",
        f"- smoke_replay: {result.smoke_replay.status if result.smoke_replay else 'MISSING'}",
        f"- risks: {', '.join(risk.value for risk in result.risks) if result.risks else 'none'}",
        "",
        "## Capability Checks",
    ]
    for check in result.capability_checks:
        lines.append(f"- {check.capability}: {'PASS' if check.passed else 'FAIL'} - {check.detail}")
    lines.extend(
        [
            "",
            "## Boundaries",
            "- file_read: false",
            "- file_written: false",
            "- real_order_submitted: false",
            "- real_account_accessed: false",
            "- position_mutated: false",
        ]
    )
    return "\n".join(lines) + "\n"


def render_agicore_trading_v1_candidate_json_report(
    result: AGIcoreTradingV1CandidateResult | Mapping[str, Any],
) -> str:
    if isinstance(result, AGIcoreTradingV1CandidateResult):
        payload = {
            "schema": "agicore_trading_v1_candidate",
            "decision": result.decision.value,
            "state": result.state.value,
            "score": result.score.overall_score,
            "risks": [risk.value for risk in result.risks],
            "recommendations": [recommendation.value for recommendation in result.recommendations],
            "context": _payload_value(result.context),
            "capability_checks": _payload_value(result.capability_checks),
            "smoke_replay": _payload_value(result.smoke_replay),
            "metrics": _payload_value(result.metrics),
            "file_read": result.file_read,
            "file_written": result.file_written,
            "real_order_submitted": result.real_order_submitted,
            "real_account_accessed": result.real_account_accessed,
            "position_mutated": result.position_mutated,
        }
    else:
        payload = dict(result)
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def assert_agicore_trading_v1_candidate_offline_boundaries(
    data: AGIcoreTradingV1CandidateInput | Mapping[str, Any] | None,
) -> bool:
    return not _boundary_risks(_coerce_input(data))


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_AGICORE_TRADING_V1_CANDIDATE
    boundary_set = {
        Risk.FILE_READ_BOUNDARY_VIOLATION,
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
        return Decision.BLOCK_AGICORE_TRADING_V1_CANDIDATE
    ordered = (
        (Risk.AGICORE_TRADING_V1_INPUT_MISSING, Decision.REQUIRE_AGICORE_TRADING_V1_INPUT_FIXES),
        (Risk.CSV_REPLAY_CAPABILITY_MISSING, Decision.REQUIRE_CSV_REPLAY_CAPABILITY_FIXES),
        (Risk.SYNTHETIC_MARKET_CAPABILITY_MISSING, Decision.REQUIRE_SYNTHETIC_MARKET_CAPABILITY_FIXES),
        (Risk.STRATEGY_REPLAY_CAPABILITY_MISSING, Decision.REQUIRE_STRATEGY_REPLAY_CAPABILITY_FIXES),
        (Risk.SIMULATED_BROKER_CAPABILITY_MISSING, Decision.REQUIRE_SIMULATED_BROKER_CAPABILITY_FIXES),
        (Risk.RISK_GUARD_CAPABILITY_MISSING, Decision.REQUIRE_RISK_GUARD_CAPABILITY_FIXES),
        (Risk.JOURNAL_CAPABILITY_MISSING, Decision.REQUIRE_JOURNAL_CAPABILITY_FIXES),
        (Risk.OFFLINE_REPORT_CAPABILITY_MISSING, Decision.REQUIRE_OFFLINE_REPORT_CAPABILITY_FIXES),
        (Risk.V1_SMOKE_REPLAY_FAILED, Decision.REQUIRE_V1_SMOKE_REPLAY_FIXES),
    )
    for risk, decision in ordered:
        if risk in risks:
            return decision
    return Decision.BLOCK_AGICORE_TRADING_V1_CANDIDATE


def _state_for(risks: tuple[Risk, ...], decision: Decision) -> State:
    if Risk.AGICORE_TRADING_V1_INPUT_MISSING in risks:
        return State.AGICORE_TRADING_V1_CANDIDATE_INPUT_INVALID
    if decision is Decision.APPROVE_AGICORE_TRADING_V1_CANDIDATE:
        return State.READY_FOR_AGICORE_TRADING_V1_CANDIDATE_REVIEW
    return State.AGICORE_TRADING_V1_CANDIDATE_BLOCKED


def evaluate_agicore_trading_v1_candidate(
    data: AGIcoreTradingV1CandidateInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1CandidateResult:
    payload = _coerce_input(data)
    context = build_agicore_trading_v1_candidate_context(payload) if payload else None
    checks: tuple[AGIcoreTradingV1CapabilityCheck, ...] = ()
    smoke_replay = None
    metrics = None
    report = None
    if payload:
        checks = (
            validate_v1_candidate_csv_replay_capability(payload),
            validate_v1_candidate_synthetic_market_capability(payload),
            validate_v1_candidate_strategy_replay_capability(payload),
            validate_v1_candidate_simulated_broker_capability(payload),
            validate_v1_candidate_risk_guard_capability(payload),
            validate_v1_candidate_journal_capability(payload),
            validate_v1_candidate_offline_report_capability(payload),
        )
        smoke_replay = run_agicore_trading_v1_candidate_smoke_replay(payload)
        metrics = compute_agicore_trading_v1_candidate_metrics(checks, smoke_replay, data=payload)
    early_risks = detect_agicore_trading_v1_candidate_risks(payload, checks, smoke_replay, metrics, None)
    early_decision = _decision_for(early_risks)
    if metrics is None and payload and not payload.force_metrics_missing:
        metrics = compute_agicore_trading_v1_candidate_metrics(checks, smoke_replay, early_decision.value, payload)
    score_without_report = compute_agicore_trading_v1_candidate_score(payload, checks, smoke_replay, metrics, None, early_risks)
    early_result = AGIcoreTradingV1CandidateResult(
        state=State.NOT_READY,
        decision=early_decision,
        score=score_without_report,
        risks=early_risks,
        recommendations=generate_agicore_trading_v1_candidate_recommendations(early_risks),
        context=context,
        capability_checks=checks,
        smoke_replay=smoke_replay,
        metrics=metrics,
    )
    if payload and not payload.force_report_missing:
        report = AGIcoreTradingV1CandidateReport(
            markdown=render_agicore_trading_v1_candidate_markdown_report(early_result),
            json=render_agicore_trading_v1_candidate_json_report(early_result),
        )
    risks = detect_agicore_trading_v1_candidate_risks(payload, checks, smoke_replay, metrics, report)
    decision = _decision_for(risks)
    state = _state_for(risks, decision)
    if metrics is not None:
        metrics = AGIcoreTradingV1CandidateMetrics(
            expected_capability_count=metrics.expected_capability_count,
            validated_capability_count=metrics.validated_capability_count,
            failed_capability_count=metrics.failed_capability_count,
            smoke_replay_status=metrics.smoke_replay_status,
            global_score=100 if not risks else metrics.global_score,
            final_decision=decision.value,
        )
    score = compute_agicore_trading_v1_candidate_score(payload, checks, smoke_replay, metrics, report, risks)
    recommendations = generate_agicore_trading_v1_candidate_recommendations(risks)
    final_without_report = AGIcoreTradingV1CandidateResult(
        state=state,
        decision=decision,
        score=score,
        risks=risks,
        recommendations=recommendations,
        context=context,
        capability_checks=checks,
        smoke_replay=smoke_replay,
        metrics=metrics,
        report=None,
        offline_only=True,
        in_memory_only=True,
        file_read=False,
        file_written=False,
        data_accessed=False,
        real_order_submitted=False,
        real_account_accessed=False,
        position_mutated=False,
    )
    if payload and not payload.force_report_missing:
        report = AGIcoreTradingV1CandidateReport(
            markdown=render_agicore_trading_v1_candidate_markdown_report(final_without_report),
            json=render_agicore_trading_v1_candidate_json_report(final_without_report),
        )
    return AGIcoreTradingV1CandidateResult(**{**final_without_report.__dict__, "report": report})
