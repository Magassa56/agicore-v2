"""Deterministic in-memory AGIcore Trading v1 offline smoke demo."""

from __future__ import annotations

import json
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.agicore_trading_v1_offline_smoke_demo_models import (
    AGIcoreTradingV1OfflineSmokeDemoContext,
    AGIcoreTradingV1OfflineSmokeDemoDecision,
    AGIcoreTradingV1OfflineSmokeDemoInput,
    AGIcoreTradingV1OfflineSmokeDemoMetrics,
    AGIcoreTradingV1OfflineSmokeDemoRecommendation,
    AGIcoreTradingV1OfflineSmokeDemoReport,
    AGIcoreTradingV1OfflineSmokeDemoResult,
    AGIcoreTradingV1OfflineSmokeDemoRisk,
    AGIcoreTradingV1OfflineSmokeDemoScore,
    AGIcoreTradingV1OfflineSmokeDemoState,
    AGIcoreTradingV1OfflineSmokeDemoStep,
    AGIcoreTradingV1OfflineSmokeDemoStepStatus,
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
from agicore.trading.simulated_broker_stub_v1_models import SimulatedBrokerReadOnlyOrderPreviewV1, SimulatedBrokerStubV1Input
from agicore.trading.strategy_replay_engine_v1 import run_strategy_replay_engine_v1
from agicore.trading.strategy_replay_engine_v1_models import StrategyReplayEngineV1Input


Risk = AGIcoreTradingV1OfflineSmokeDemoRisk
Recommendation = AGIcoreTradingV1OfflineSmokeDemoRecommendation
Decision = AGIcoreTradingV1OfflineSmokeDemoDecision
State = AGIcoreTradingV1OfflineSmokeDemoState
StepStatus = AGIcoreTradingV1OfflineSmokeDemoStepStatus

CSV_REPLAY_INPUT_STEP = "CSV_REPLAY_INPUT_STEP"
STRATEGY_REPLAY_ENGINE_STEP = "STRATEGY_REPLAY_ENGINE_STEP"
RISK_GUARD_STEP = "RISK_GUARD_STEP"
SIMULATED_BROKER_PREVIEW_STEP = "SIMULATED_BROKER_PREVIEW_STEP"
JOURNAL_WRITER_STEP = "JOURNAL_WRITER_STEP"
OFFLINE_REPORT_STEP = "OFFLINE_REPORT_STEP"
END_TO_END_VALIDATION_STEP = "END_TO_END_VALIDATION_STEP"

EXPECTED_STEPS: tuple[str, ...] = (
    CSV_REPLAY_INPUT_STEP,
    STRATEGY_REPLAY_ENGINE_STEP,
    RISK_GUARD_STEP,
    SIMULATED_BROKER_PREVIEW_STEP,
    JOURNAL_WRITER_STEP,
    OFFLINE_REPORT_STEP,
    END_TO_END_VALIDATION_STEP,
)


def _coerce_input(
    data: AGIcoreTradingV1OfflineSmokeDemoInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineSmokeDemoInput | None:
    if data is None:
        return None
    if isinstance(data, AGIcoreTradingV1OfflineSmokeDemoInput):
        return data
    allowed = {field.name for field in fields(AGIcoreTradingV1OfflineSmokeDemoInput)}
    return AGIcoreTradingV1OfflineSmokeDemoInput(**{key: value for key, value in dict(data).items() if key in allowed})


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


def _passed_step(name: str, message: str, payload: Any = None) -> AGIcoreTradingV1OfflineSmokeDemoStep:
    return AGIcoreTradingV1OfflineSmokeDemoStep(name=name, status=StepStatus.PASSED, message=message, payload=payload)


def _failed_step(
    name: str,
    message: str,
    risk: Risk,
    payload: Any = None,
) -> AGIcoreTradingV1OfflineSmokeDemoStep:
    return AGIcoreTradingV1OfflineSmokeDemoStep(
        name=name,
        status=StepStatus.FAILED,
        message=message,
        risks=(risk,),
        payload=payload,
    )


def _boundary_risks(data: AGIcoreTradingV1OfflineSmokeDemoInput | None) -> tuple[Risk, ...]:
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
    if (
        data.api_key_read_requested
        or data.env_var_read_requested
        or not data.no_api_key_read
        or not data.no_env_var_read
        or not data.no_hardcoded_secret
    ):
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
    if not data.in_memory_only:
        risks.append(Risk.FILE_READ_BOUNDARY_VIOLATION)
    return _dedupe(risks)


def _overclaim_risks(data: AGIcoreTradingV1OfflineSmokeDemoInput | None) -> tuple[Risk, ...]:
    if data is None:
        return ()
    risks: list[Risk] = []
    if data.force_live_trading_overclaim:
        risks.append(Risk.LIVE_TRADING_READINESS_OVERCLAIM)
    if data.force_real_broker_overclaim:
        risks.append(Risk.REAL_BROKER_READINESS_OVERCLAIM)
    if data.force_real_order_overclaim:
        risks.append(Risk.REAL_ORDER_EXECUTION_OVERCLAIM)
    if data.force_profitability_overclaim:
        risks.append(Risk.PROFITABILITY_PROOF_OVERCLAIM)
    if data.force_financial_advice_overclaim:
        risks.append(Risk.FINANCIAL_ADVICE_OVERCLAIM)
    return tuple(risks)


def assert_agicore_trading_v1_offline_smoke_demo_boundaries(
    data: AGIcoreTradingV1OfflineSmokeDemoInput | Mapping[str, Any] | None,
) -> bool:
    return not _boundary_risks(_coerce_input(data))


def validate_agicore_trading_v1_offline_smoke_demo_input(
    data: AGIcoreTradingV1OfflineSmokeDemoInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(
        payload
        and payload.run_id
        and payload.symbol
        and payload.strategy_type
        and assert_agicore_trading_v1_offline_smoke_demo_boundaries(payload)
    )


def build_offline_smoke_demo_context(
    data: AGIcoreTradingV1OfflineSmokeDemoInput | Mapping[str, Any],
) -> AGIcoreTradingV1OfflineSmokeDemoContext:
    payload = _coerce_input(data)
    if payload is None:
        raise ValueError("AGIcore Trading v1 offline smoke demo input is required")
    return AGIcoreTradingV1OfflineSmokeDemoContext(
        run_id=payload.run_id,
        symbol=payload.symbol,
        strategy_type=payload.strategy_type,
    )


def build_offline_smoke_demo_csv_string(
    data: AGIcoreTradingV1OfflineSmokeDemoInput | Mapping[str, Any] | None = None,
) -> str:
    _coerce_input(data)
    return (
        "timestamp,open,high,low,close,volume\n"
        f"2026-01-01T00:00:00,100,105,99,104,1000\n"
        f"2026-01-01T00:01:00,104,108,103,107,1200\n"
        f"2026-01-01T00:02:00,107,110,106,109,1400\n"
        f"2026-01-01T00:03:00,109,112,108,111,1600\n"
        f"2026-01-01T00:04:00,111,114,110,113,1800\n"
    )


def _bar_to_mapping(bar: Any) -> dict[str, Any]:
    return {
        "timestamp": getattr(bar, "timestamp", ""),
        "open": float(getattr(bar, "open", 0.0)),
        "high": float(getattr(bar, "high", 0.0)),
        "low": float(getattr(bar, "low", 0.0)),
        "close": float(getattr(bar, "close", 0.0)),
        "volume": float(getattr(bar, "volume", 0.0)),
    }


def build_offline_smoke_demo_market_bars(csv_replay_result: Any = None) -> tuple[dict[str, Any], ...]:
    dataset = getattr(csv_replay_result, "dataset", None)
    if dataset is not None and getattr(dataset, "bars", ()):
        return tuple(_bar_to_mapping(bar) for bar in dataset.bars)
    return (
        {"timestamp": "2026-01-01T00:00:00", "open": 100.0, "high": 105.0, "low": 99.0, "close": 104.0, "volume": 1000.0},
        {"timestamp": "2026-01-01T00:01:00", "open": 104.0, "high": 108.0, "low": 103.0, "close": 107.0, "volume": 1200.0},
        {"timestamp": "2026-01-01T00:02:00", "open": 107.0, "high": 110.0, "low": 106.0, "close": 109.0, "volume": 1400.0},
        {"timestamp": "2026-01-01T00:03:00", "open": 109.0, "high": 112.0, "low": 108.0, "close": 111.0, "volume": 1600.0},
        {"timestamp": "2026-01-01T00:04:00", "open": 111.0, "high": 114.0, "low": 110.0, "close": 113.0, "volume": 1800.0},
    )


def run_offline_smoke_demo_csv_replay_step(
    data: AGIcoreTradingV1OfflineSmokeDemoInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineSmokeDemoStep:
    payload = _coerce_input(data)
    if payload is None or payload.force_csv_replay_failed:
        return _failed_step(CSV_REPLAY_INPUT_STEP, "CSV replay step failed", Risk.SMOKE_DEMO_CSV_REPLAY_FAILED)
    result = build_csv_replay_input_v1(
        CsvReplayInputV1Input(
            csv_content=build_offline_smoke_demo_csv_string(payload),
            dataset_id=f"{payload.run_id}-csv",
            symbol=payload.symbol,
        )
    )
    passed = not result.risks and result.dataset is not None and bool(result.dataset.bars)
    if not passed:
        return _failed_step(CSV_REPLAY_INPUT_STEP, "CSV replay did not produce validated bars", Risk.SMOKE_DEMO_CSV_REPLAY_FAILED, result)
    return _passed_step(CSV_REPLAY_INPUT_STEP, "CSV replay parsed in-memory OHLCV bars", result)


def run_offline_smoke_demo_strategy_replay_step(
    data: AGIcoreTradingV1OfflineSmokeDemoInput | Mapping[str, Any] | None,
    bars: tuple[Any, ...],
) -> AGIcoreTradingV1OfflineSmokeDemoStep:
    payload = _coerce_input(data)
    if payload is None or payload.force_strategy_replay_failed:
        return _failed_step(
            STRATEGY_REPLAY_ENGINE_STEP,
            "Strategy replay step failed",
            Risk.SMOKE_DEMO_STRATEGY_REPLAY_FAILED,
        )
    result = run_strategy_replay_engine_v1(
        StrategyReplayEngineV1Input(
            bars=bars,
            strategy_type=payload.strategy_type,
            run_id=payload.run_id,
            symbol=payload.symbol,
        )
    )
    decision = getattr(result, "read_only_decision", None)
    passed = not result.risks and decision is not None and bool(getattr(decision, "read_only", False))
    passed = passed and not bool(getattr(decision, "order_submitted", True))
    if not passed:
        return _failed_step(
            STRATEGY_REPLAY_ENGINE_STEP,
            "Strategy replay did not produce a valid read-only decision",
            Risk.SMOKE_DEMO_STRATEGY_REPLAY_FAILED,
            result,
        )
    return _passed_step(STRATEGY_REPLAY_ENGINE_STEP, "Strategy replay produced a read-only decision", result)


def run_offline_smoke_demo_risk_guard_step(
    data: AGIcoreTradingV1OfflineSmokeDemoInput | Mapping[str, Any] | None,
    strategy_replay_result: Any,
) -> AGIcoreTradingV1OfflineSmokeDemoStep:
    payload = _coerce_input(data)
    if payload is None or payload.force_risk_guard_failed:
        return _failed_step(RISK_GUARD_STEP, "Risk guard step failed", Risk.SMOKE_DEMO_RISK_GUARD_FAILED)
    decision = getattr(strategy_replay_result, "read_only_decision", None)
    requested_quantity = float(getattr(decision, "proposed_position_size", 5.0))
    reference_price = float(getattr(decision, "reference_price", 100.0))
    order_preview = SimulatedBrokerReadOnlyOrderPreviewV1(
        symbol=payload.symbol,
        action=str(getattr(decision, "action", "BUY")),
        requested_quantity=requested_quantity,
        reference_price=reference_price,
        notional=requested_quantity * reference_price,
    )
    result = enforce_risk_guard_v1(
        RiskGuardEnforcementV1Input(
            symbol=payload.symbol,
            requested_quantity=requested_quantity,
            reference_price=reference_price,
            order_preview=order_preview,
        )
    )
    passed = not result.risks and result.summary is not None and result.summary.all_passed
    if not passed:
        return _failed_step(RISK_GUARD_STEP, "Risk guard did not pass", Risk.SMOKE_DEMO_RISK_GUARD_FAILED, result)
    return _passed_step(RISK_GUARD_STEP, "Risk guard passed deterministic offline limits", result)


def run_offline_smoke_demo_broker_preview_step(
    data: AGIcoreTradingV1OfflineSmokeDemoInput | Mapping[str, Any] | None,
    strategy_replay_result: Any,
) -> AGIcoreTradingV1OfflineSmokeDemoStep:
    payload = _coerce_input(data)
    if payload is None or payload.force_broker_preview_failed:
        return _failed_step(
            SIMULATED_BROKER_PREVIEW_STEP,
            "Simulated broker preview step failed",
            Risk.SMOKE_DEMO_BROKER_PREVIEW_FAILED,
        )
    decision = getattr(strategy_replay_result, "read_only_decision", None)
    result = build_simulated_broker_stub_v1(
        SimulatedBrokerStubV1Input(
            symbol=payload.symbol,
            action=str(getattr(decision, "action", "BUY")),
            requested_quantity=float(getattr(decision, "proposed_position_size", 5.0)),
            reference_price=float(getattr(decision, "reference_price", 100.0)),
            read_only_decision=decision,
        )
    )
    preview = getattr(result, "order_preview", None)
    passed = not result.risks and preview is not None and bool(getattr(preview, "read_only", False))
    passed = passed and not bool(getattr(preview, "order_submitted", True))
    if not passed:
        return _failed_step(
            SIMULATED_BROKER_PREVIEW_STEP,
            "Simulated broker did not produce a read-only preview",
            Risk.SMOKE_DEMO_BROKER_PREVIEW_FAILED,
            result,
        )
    return _passed_step(SIMULATED_BROKER_PREVIEW_STEP, "Simulated broker produced read-only preview", result)


def run_offline_smoke_demo_journal_step(
    data: AGIcoreTradingV1OfflineSmokeDemoInput | Mapping[str, Any] | None,
    csv_replay_result: Any,
    strategy_replay_result: Any,
    risk_guard_result: Any,
    broker_preview_result: Any,
) -> AGIcoreTradingV1OfflineSmokeDemoStep:
    payload = _coerce_input(data)
    if payload is None or payload.force_journal_failed:
        return _failed_step(JOURNAL_WRITER_STEP, "Journal writer step failed", Risk.SMOKE_DEMO_JOURNAL_FAILED)
    result = build_journal_writer_v1(
        JournalWriterV1Input(
            run_id=payload.run_id,
            symbol=payload.symbol,
            market_scenario={"bar_count": len(build_offline_smoke_demo_market_bars(csv_replay_result))},
            strategy_signal=getattr(strategy_replay_result, "signal", None),
            broker_preview=getattr(broker_preview_result, "order_preview", None),
            risk_guard_result=getattr(risk_guard_result, "summary", None),
            read_only_decision=getattr(strategy_replay_result, "read_only_decision", None),
            runner_metrics=getattr(strategy_replay_result, "metrics", None),
        )
    )
    passed = not result.risks and result.metrics is not None and result.metrics.complete
    if not passed:
        return _failed_step(JOURNAL_WRITER_STEP, "Journal writer did not produce a complete journal", Risk.SMOKE_DEMO_JOURNAL_FAILED, result)
    return _passed_step(JOURNAL_WRITER_STEP, "Journal writer recorded the smoke demo in memory", result)


def run_offline_smoke_demo_report_step(
    data: AGIcoreTradingV1OfflineSmokeDemoInput | Mapping[str, Any] | None,
    csv_replay_result: Any,
    strategy_replay_result: Any,
    risk_guard_result: Any,
    broker_preview_result: Any,
    journal_result: Any,
) -> AGIcoreTradingV1OfflineSmokeDemoStep:
    payload = _coerce_input(data)
    if payload is None or payload.force_report_failed:
        return _failed_step(OFFLINE_REPORT_STEP, "Offline report step failed", Risk.SMOKE_DEMO_REPORT_FAILED)
    result = build_offline_report_markdown_json_v1(
        OfflineReportMarkdownJsonV1Input(
            run_id=payload.run_id,
            symbol=payload.symbol,
            decision="APPROVE_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO",
            score=100,
            market_scenario={"bar_count": len(build_offline_smoke_demo_market_bars(csv_replay_result))},
            broker_result=broker_preview_result,
            risk_guard_result=risk_guard_result,
            journal_result=journal_result,
            metrics=getattr(strategy_replay_result, "metrics", None),
            next_actions=("Review AGIcore Trading v1 offline smoke demo",),
        )
    )
    markdown = getattr(getattr(result, "markdown", None), "content", "")
    json_report = getattr(getattr(result, "json_report", None), "serialized", "")
    passed = not result.risks and bool(markdown) and bool(json_report)
    if not passed:
        return _failed_step(OFFLINE_REPORT_STEP, "Offline report did not produce Markdown and JSON", Risk.SMOKE_DEMO_REPORT_FAILED, result)
    return _passed_step(OFFLINE_REPORT_STEP, "Offline report produced Markdown and JSON in memory", result)


def validate_offline_smoke_demo_read_only_decision(result: Any) -> bool:
    strategy = getattr(result, "strategy_replay_result", result)
    decision = getattr(strategy, "read_only_decision", None)
    broker = getattr(result, "broker_preview_result", None)
    preview = getattr(broker, "order_preview", None)
    decision_ok = decision is not None and bool(getattr(decision, "read_only", False))
    decision_ok = decision_ok and not bool(getattr(decision, "order_submitted", True))
    if preview is None:
        return decision_ok
    return decision_ok and bool(getattr(preview, "read_only", False)) and not bool(getattr(preview, "order_submitted", True))


def validate_offline_smoke_demo_no_profitability_claim(
    data: AGIcoreTradingV1OfflineSmokeDemoInput | Mapping[str, Any] | str | None,
) -> bool:
    if isinstance(data, str):
        lowered = data.lower()
        forbidden = ("profitability_proven: true", "profitable strategy", "guaranteed profit")
        return not any(token in lowered for token in forbidden)
    payload = _coerce_input(data)
    return not (payload and payload.force_profitability_overclaim)


def validate_offline_smoke_demo_no_live_trading_claim(
    data: AGIcoreTradingV1OfflineSmokeDemoInput | Mapping[str, Any] | str | None,
) -> bool:
    if isinstance(data, str):
        lowered = data.lower()
        forbidden = ("live_trading_ready: true", "ready for live trading", "real trading ready")
        return not any(token in lowered for token in forbidden)
    payload = _coerce_input(data)
    return not (payload and payload.force_live_trading_overclaim)


def validate_offline_smoke_demo_end_to_end_result(
    steps: tuple[AGIcoreTradingV1OfflineSmokeDemoStep, ...],
    data: AGIcoreTradingV1OfflineSmokeDemoInput | Mapping[str, Any] | None = None,
) -> bool:
    payload = _coerce_input(data)
    names = {step.name for step in steps}
    return bool(
        not (payload and payload.force_end_to_end_validation_failed)
        and all(name in names for name in EXPECTED_STEPS[:-1])
        and all(step.status is StepStatus.PASSED for step in steps if step.name in EXPECTED_STEPS[:-1])
    )


def compute_agicore_trading_v1_offline_smoke_demo_metrics(
    steps: tuple[AGIcoreTradingV1OfflineSmokeDemoStep, ...],
    strategy_replay_result: Any = None,
    broker_preview_result: Any = None,
    journal_result: Any = None,
    report_result: Any = None,
    final_decision: str = "",
) -> AGIcoreTradingV1OfflineSmokeDemoMetrics:
    passed = sum(1 for step in steps if step.status is StepStatus.PASSED)
    failed = sum(1 for step in steps if step.status is StepStatus.FAILED)
    decision = getattr(strategy_replay_result, "read_only_decision", None)
    preview = getattr(broker_preview_result, "order_preview", None)
    journal_metrics = getattr(journal_result, "metrics", None)
    markdown = getattr(getattr(report_result, "markdown", None), "content", "")
    json_report = getattr(getattr(report_result, "json_report", None), "serialized", "")
    return AGIcoreTradingV1OfflineSmokeDemoMetrics(
        expected_step_count=len(EXPECTED_STEPS),
        passed_step_count=passed,
        failed_step_count=failed,
        read_only_decision=bool(decision and getattr(decision, "read_only", False) and not getattr(decision, "order_submitted", True)),
        broker_preview_read_only=bool(preview and getattr(preview, "read_only", False) and not getattr(preview, "order_submitted", True)),
        journal_entry_count=int(getattr(journal_metrics, "total_entries", 0)),
        markdown_report_present=bool(markdown),
        json_report_present=bool(json_report),
        final_decision=final_decision,
    )


def detect_agicore_trading_v1_offline_smoke_demo_risks(
    data: AGIcoreTradingV1OfflineSmokeDemoInput | Mapping[str, Any] | None,
    steps: tuple[AGIcoreTradingV1OfflineSmokeDemoStep, ...] = (),
    metrics: AGIcoreTradingV1OfflineSmokeDemoMetrics | None = None,
) -> tuple[Risk, ...]:
    payload = _coerce_input(data)
    risks: list[Risk] = []
    if payload is None:
        risks.append(Risk.SMOKE_DEMO_INPUT_MISSING)
    for step in steps:
        risks.extend(step.risks)
    if payload is not None and metrics is not None:
        if not metrics.markdown_report_present or not metrics.json_report_present:
            risks.append(Risk.SMOKE_DEMO_REPORT_FAILED)
    risks.extend(_overclaim_risks(payload))
    risks.extend(_boundary_risks(payload))
    return _dedupe(risks)


def compute_agicore_trading_v1_offline_smoke_demo_score(
    data: AGIcoreTradingV1OfflineSmokeDemoInput | Mapping[str, Any] | None,
    steps: tuple[AGIcoreTradingV1OfflineSmokeDemoStep, ...] = (),
    metrics: AGIcoreTradingV1OfflineSmokeDemoMetrics | None = None,
    risks: tuple[Risk, ...] = (),
) -> AGIcoreTradingV1OfflineSmokeDemoScore:
    payload = _coerce_input(data)
    input_score = 100 if validate_agicore_trading_v1_offline_smoke_demo_input(payload) else 0
    step_score = 100 if len(steps) == len(EXPECTED_STEPS) and all(step.status is StepStatus.PASSED for step in steps) else 0
    read_only_score = 100 if metrics and metrics.read_only_decision and metrics.broker_preview_read_only else 0
    report_score = 100 if metrics and metrics.markdown_report_present and metrics.json_report_present else 0
    overclaim_score = 100 if not _overclaim_risks(payload) else 0
    boundary_score = 100 if not _boundary_risks(payload) else 0
    overall = min(input_score, step_score, read_only_score, report_score, overclaim_score, boundary_score)
    if risks:
        overall = min(overall, max(0, 100 - len(risks) * 10))
    return AGIcoreTradingV1OfflineSmokeDemoScore(
        overall_score=overall,
        input_score=input_score,
        step_score=step_score,
        read_only_score=read_only_score,
        report_score=report_score,
        overclaim_score=overclaim_score,
        boundary_score=boundary_score,
    )


def generate_agicore_trading_v1_offline_smoke_demo_recommendations(
    risks: Iterable[Risk],
) -> tuple[Recommendation, ...]:
    mapping = {
        Risk.SMOKE_DEMO_INPUT_MISSING: Recommendation.PROVIDE_SMOKE_DEMO_INPUT,
        Risk.SMOKE_DEMO_CSV_REPLAY_FAILED: Recommendation.FIX_SMOKE_DEMO_CSV_REPLAY,
        Risk.SMOKE_DEMO_STRATEGY_REPLAY_FAILED: Recommendation.FIX_SMOKE_DEMO_STRATEGY_REPLAY,
        Risk.SMOKE_DEMO_RISK_GUARD_FAILED: Recommendation.FIX_SMOKE_DEMO_RISK_GUARD,
        Risk.SMOKE_DEMO_BROKER_PREVIEW_FAILED: Recommendation.FIX_SMOKE_DEMO_BROKER_PREVIEW,
        Risk.SMOKE_DEMO_JOURNAL_FAILED: Recommendation.FIX_SMOKE_DEMO_JOURNAL,
        Risk.SMOKE_DEMO_REPORT_FAILED: Recommendation.FIX_SMOKE_DEMO_REPORT,
        Risk.SMOKE_DEMO_END_TO_END_VALIDATION_FAILED: Recommendation.FIX_SMOKE_DEMO_END_TO_END_VALIDATION,
        Risk.LIVE_TRADING_READINESS_OVERCLAIM: Recommendation.REMOVE_LIVE_TRADING_READINESS_CLAIM,
        Risk.REAL_BROKER_READINESS_OVERCLAIM: Recommendation.REMOVE_REAL_BROKER_READINESS_CLAIM,
        Risk.REAL_ORDER_EXECUTION_OVERCLAIM: Recommendation.REMOVE_REAL_ORDER_EXECUTION_CLAIM,
        Risk.PROFITABILITY_PROOF_OVERCLAIM: Recommendation.REMOVE_PROFITABILITY_PROOF_CLAIM,
        Risk.FINANCIAL_ADVICE_OVERCLAIM: Recommendation.REMOVE_FINANCIAL_ADVICE_CLAIM,
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
    recommendations.append(Recommendation.RUN_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_TEST_SUITE)
    if not risks:
        recommendations.append(Recommendation.APPROVE_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_REVIEW)
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
    if isinstance(value, (tuple, list)):
        return [_payload_value(item) for item in value]
    if hasattr(value, "__dict__"):
        return {
            key: _payload_value(item)
            for key, item in vars(value).items()
            if not key.startswith("_")
            and key
            not in {
                "payload",
                "csv_replay_result",
                "strategy_replay_result",
                "risk_guard_result",
                "broker_preview_result",
                "journal_result",
                "offline_report_result",
            }
        }
    return str(value)


def render_agicore_trading_v1_offline_smoke_demo_markdown_report(
    result: AGIcoreTradingV1OfflineSmokeDemoResult | Mapping[str, Any],
) -> str:
    if not isinstance(result, AGIcoreTradingV1OfflineSmokeDemoResult):
        return "# AGIcore Trading v1 Offline Smoke Demo\n"
    lines = [
        "# AGIcore Trading v1 Offline Smoke Demo",
        "",
        f"- decision: {result.decision.value}",
        f"- state: {result.state.value}",
        f"- score: {result.score.overall_score}",
        "- status: offline/sandbox smoke demo only",
        "- live_trading_ready: false",
        "- real_broker_ready: false",
        "- real_order_execution: false",
        "- profitability_proven: false",
        "- financial_advice: false",
        f"- risks: {', '.join(risk.value for risk in result.risks) if result.risks else 'none'}",
        "",
        "## Steps",
    ]
    for step in result.steps:
        lines.append(f"- {step.name}: {step.status.value} - {step.message}")
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


def render_agicore_trading_v1_offline_smoke_demo_json_report(
    result: AGIcoreTradingV1OfflineSmokeDemoResult | Mapping[str, Any],
) -> str:
    if isinstance(result, AGIcoreTradingV1OfflineSmokeDemoResult):
        payload = {
            "schema": "agicore_trading_v1_offline_smoke_demo",
            "decision": result.decision.value,
            "state": result.state.value,
            "score": result.score.overall_score,
            "risks": [risk.value for risk in result.risks],
            "recommendations": [recommendation.value for recommendation in result.recommendations],
            "context": _payload_value(result.context),
            "steps": _payload_value(result.steps),
            "metrics": _payload_value(result.metrics),
            "live_trading_ready": False,
            "real_broker_ready": False,
            "real_order_execution": False,
            "profitability_proven": False,
            "financial_advice": False,
            "file_read": result.file_read,
            "file_written": result.file_written,
            "real_order_submitted": result.real_order_submitted,
            "real_account_accessed": result.real_account_accessed,
            "position_mutated": result.position_mutated,
        }
    else:
        payload = dict(result)
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO
    boundary_or_overclaim = {
        Risk.LIVE_TRADING_READINESS_OVERCLAIM,
        Risk.REAL_BROKER_READINESS_OVERCLAIM,
        Risk.REAL_ORDER_EXECUTION_OVERCLAIM,
        Risk.PROFITABILITY_PROOF_OVERCLAIM,
        Risk.FINANCIAL_ADVICE_OVERCLAIM,
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
    if any(risk in boundary_or_overclaim for risk in risks):
        return Decision.REQUIRE_SMOKE_DEMO_BOUNDARY_FIXES
    ordered = (
        (Risk.SMOKE_DEMO_INPUT_MISSING, Decision.REQUIRE_SMOKE_DEMO_INPUT_FIXES),
        (Risk.SMOKE_DEMO_CSV_REPLAY_FAILED, Decision.REQUIRE_SMOKE_DEMO_CSV_REPLAY_FIXES),
        (Risk.SMOKE_DEMO_STRATEGY_REPLAY_FAILED, Decision.REQUIRE_SMOKE_DEMO_STRATEGY_REPLAY_FIXES),
        (Risk.SMOKE_DEMO_RISK_GUARD_FAILED, Decision.REQUIRE_SMOKE_DEMO_RISK_GUARD_FIXES),
        (Risk.SMOKE_DEMO_BROKER_PREVIEW_FAILED, Decision.REQUIRE_SMOKE_DEMO_BROKER_PREVIEW_FIXES),
        (Risk.SMOKE_DEMO_JOURNAL_FAILED, Decision.REQUIRE_SMOKE_DEMO_JOURNAL_FIXES),
        (Risk.SMOKE_DEMO_REPORT_FAILED, Decision.REQUIRE_SMOKE_DEMO_REPORT_FIXES),
    )
    for risk, decision in ordered:
        if risk in risks:
            return decision
    return Decision.BLOCK_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO


def _state_for(risks: tuple[Risk, ...], decision: Decision) -> State:
    if Risk.SMOKE_DEMO_INPUT_MISSING in risks:
        return State.AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_INPUT_INVALID
    if decision is Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO:
        return State.READY_FOR_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_REVIEW
    return State.AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_BLOCKED


def run_agicore_trading_v1_offline_smoke_demo(
    data: AGIcoreTradingV1OfflineSmokeDemoInput | Mapping[str, Any] | None = None,
) -> AGIcoreTradingV1OfflineSmokeDemoResult:
    payload = _coerce_input(data)
    if payload is None:
        risks = (Risk.SMOKE_DEMO_INPUT_MISSING,)
        score = compute_agicore_trading_v1_offline_smoke_demo_score(None, (), None, risks)
        return AGIcoreTradingV1OfflineSmokeDemoResult(
            state=State.AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO_INPUT_INVALID,
            decision=Decision.REQUIRE_SMOKE_DEMO_INPUT_FIXES,
            score=score,
            risks=risks,
            recommendations=generate_agicore_trading_v1_offline_smoke_demo_recommendations(risks),
        )

    context = build_offline_smoke_demo_context(payload)
    steps: list[AGIcoreTradingV1OfflineSmokeDemoStep] = []

    csv_step = run_offline_smoke_demo_csv_replay_step(payload)
    steps.append(csv_step)
    csv_result = csv_step.payload if csv_step.status is StepStatus.PASSED else None
    bars = build_offline_smoke_demo_market_bars(csv_result)

    strategy_step = run_offline_smoke_demo_strategy_replay_step(payload, bars)
    steps.append(strategy_step)
    strategy_result = strategy_step.payload if strategy_step.status is StepStatus.PASSED else None

    risk_step = run_offline_smoke_demo_risk_guard_step(payload, strategy_result)
    steps.append(risk_step)
    risk_result = risk_step.payload if risk_step.status is StepStatus.PASSED else None

    broker_step = run_offline_smoke_demo_broker_preview_step(payload, strategy_result)
    steps.append(broker_step)
    broker_result = broker_step.payload if broker_step.status is StepStatus.PASSED else None

    journal_step = run_offline_smoke_demo_journal_step(payload, csv_result, strategy_result, risk_result, broker_result)
    steps.append(journal_step)
    journal_result = journal_step.payload if journal_step.status is StepStatus.PASSED else None

    report_step = run_offline_smoke_demo_report_step(payload, csv_result, strategy_result, risk_result, broker_result, journal_result)
    steps.append(report_step)
    offline_report_result = report_step.payload if report_step.status is StepStatus.PASSED else None

    end_to_end_passed = validate_offline_smoke_demo_end_to_end_result(tuple(steps), payload)
    if end_to_end_passed:
        steps.append(_passed_step(END_TO_END_VALIDATION_STEP, "End-to-end smoke demo validation passed"))
    else:
        steps.append(
            _failed_step(
                END_TO_END_VALIDATION_STEP,
                "End-to-end smoke demo validation failed",
                Risk.SMOKE_DEMO_END_TO_END_VALIDATION_FAILED,
            )
        )

    preliminary_metrics = compute_agicore_trading_v1_offline_smoke_demo_metrics(
        tuple(steps),
        strategy_result,
        broker_result,
        journal_result,
        offline_report_result,
    )
    risks = detect_agicore_trading_v1_offline_smoke_demo_risks(payload, tuple(steps), preliminary_metrics)
    decision = _decision_for(risks)
    state = _state_for(risks, decision)
    metrics = compute_agicore_trading_v1_offline_smoke_demo_metrics(
        tuple(steps),
        strategy_result,
        broker_result,
        journal_result,
        offline_report_result,
        decision.value,
    )
    score = compute_agicore_trading_v1_offline_smoke_demo_score(payload, tuple(steps), metrics, risks)
    recommendations = generate_agicore_trading_v1_offline_smoke_demo_recommendations(risks)
    result_without_report = AGIcoreTradingV1OfflineSmokeDemoResult(
        state=state,
        decision=decision,
        score=score,
        risks=risks,
        recommendations=recommendations,
        context=context,
        steps=tuple(steps),
        metrics=metrics,
        csv_replay_result=csv_result,
        strategy_replay_result=strategy_result,
        risk_guard_result=risk_result,
        broker_preview_result=broker_result,
        journal_result=journal_result,
        offline_report_result=offline_report_result,
    )
    report = AGIcoreTradingV1OfflineSmokeDemoReport(
        markdown=render_agicore_trading_v1_offline_smoke_demo_markdown_report(result_without_report),
        json=render_agicore_trading_v1_offline_smoke_demo_json_report(result_without_report),
    )
    return AGIcoreTradingV1OfflineSmokeDemoResult(**{**result_without_report.__dict__, "report": report})
