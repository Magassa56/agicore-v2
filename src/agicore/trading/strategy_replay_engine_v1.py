"""Deterministic in-memory strategy replay engine v1 for AGIcore Trading."""

from __future__ import annotations

import json
from dataclasses import fields
from enum import Enum
from math import isfinite
from typing import Any, Iterable, Mapping

from agicore.trading.controlled_offline_runner_minimal_models import (
    ControlledOfflineSyntheticMarketBar,
    ControlledOfflineSyntheticMarketScenario,
)
from agicore.trading.journal_writer_v1 import build_journal_writer_v1
from agicore.trading.journal_writer_v1_models import JournalWriterV1Input
from agicore.trading.risk_guard_enforcement_v1 import enforce_risk_guard_v1
from agicore.trading.risk_guard_enforcement_v1_models import RiskGuardEnforcementV1Input
from agicore.trading.simulated_broker_stub_v1 import build_simulated_broker_stub_v1
from agicore.trading.simulated_broker_stub_v1_models import SimulatedBrokerStubV1Input
from agicore.trading.strategy_replay_engine_v1_models import (
    StrategyReplayBarV1,
    StrategyReplayBrokerPreviewV1,
    StrategyReplayContextV1,
    StrategyReplayEngineV1Decision,
    StrategyReplayEngineV1Input,
    StrategyReplayEngineV1Recommendation,
    StrategyReplayEngineV1Result,
    StrategyReplayEngineV1Risk,
    StrategyReplayEngineV1Score,
    StrategyReplayEngineV1State,
    StrategyReplayJournalResultV1,
    StrategyReplayMetricsV1,
    StrategyReplayReadOnlyDecisionV1,
    StrategyReplayReportV1,
    StrategyReplayRiskResultV1,
    StrategyReplaySignalV1,
    StrategyReplayStrategyTypeV1,
)


Risk = StrategyReplayEngineV1Risk
Recommendation = StrategyReplayEngineV1Recommendation
Decision = StrategyReplayEngineV1Decision
State = StrategyReplayEngineV1State
StrategyType = StrategyReplayStrategyTypeV1


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


def _coerce_input(data: StrategyReplayEngineV1Input | Mapping[str, Any] | None) -> StrategyReplayEngineV1Input | None:
    if data is None:
        return None
    if isinstance(data, StrategyReplayEngineV1Input):
        return data
    allowed = {field.name for field in fields(StrategyReplayEngineV1Input)}
    return StrategyReplayEngineV1Input(**{key: value for key, value in dict(data).items() if key in allowed})


def _finite(value: Any) -> bool:
    return isinstance(value, int | float) and isfinite(float(value))


def _round(value: float) -> float:
    return round(float(value), 10)


def _parse_strategy(value: StrategyType | str | None) -> StrategyType | None:
    if isinstance(value, StrategyType):
        return value
    if isinstance(value, str):
        try:
            return StrategyType(value)
        except ValueError:
            return None
    return None


def _boundary_risks(data: StrategyReplayEngineV1Input | None) -> tuple[Risk, ...]:
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
    if not data.in_memory_only or not data.replay_in_memory_only:
        risks.append(Risk.FILE_READ_BOUNDARY_VIOLATION)
    return _dedupe(risks)


def validate_strategy_replay_engine_v1_input(
    data: StrategyReplayEngineV1Input | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(
        payload
        and payload.run_id
        and payload.symbol
        and payload.bars
        and _parse_strategy(payload.strategy_type)
        and assert_strategy_replay_engine_v1_offline_boundaries(payload)
    )


def build_strategy_replay_context_v1(
    data: StrategyReplayEngineV1Input | Mapping[str, Any],
) -> StrategyReplayContextV1:
    payload = _coerce_input(data)
    if payload is None:
        raise ValueError("strategy replay input is required")
    return StrategyReplayContextV1(
        run_id=payload.run_id,
        symbol=payload.symbol,
        strategy_type=payload.strategy_type,
        bar_count=len(payload.bars),
    )


def _invalid_bar(index: int, symbol: str) -> StrategyReplayBarV1:
    return StrategyReplayBarV1(index=index, timestamp="", symbol=symbol, open=0.0, high=0.0, low=0.0, close=0.0, volume=-1.0)


def _bar_from_any(item: Any, index: int, default_symbol: str) -> StrategyReplayBarV1:
    if isinstance(item, StrategyReplayBarV1):
        return item
    try:
        if isinstance(item, Mapping):
            payload = dict(item)
            raw_index = payload.get("index", payload.get("step", index))
            return StrategyReplayBarV1(
                index=int(raw_index),
                timestamp=str(payload.get("timestamp", "")),
                symbol=str(payload.get("symbol", default_symbol)),
                open=float(payload.get("open", 0.0)),
                high=float(payload.get("high", 0.0)),
                low=float(payload.get("low", 0.0)),
                close=float(payload.get("close", 0.0)),
                volume=float(payload.get("volume", 0.0)),
            )
        raw_index = getattr(item, "index", getattr(item, "step", index))
        return StrategyReplayBarV1(
            index=int(raw_index),
            timestamp=str(getattr(item, "timestamp", "")),
            symbol=str(getattr(item, "symbol", default_symbol)),
            open=float(getattr(item, "open")),
            high=float(getattr(item, "high")),
            low=float(getattr(item, "low")),
            close=float(getattr(item, "close")),
            volume=float(getattr(item, "volume", 0.0)),
        )
    except (TypeError, ValueError, AttributeError):
        return _invalid_bar(index, default_symbol)


def normalize_strategy_replay_bars_v1(
    bars: Iterable[Any],
    symbol: str = "SIM",
) -> tuple[StrategyReplayBarV1, ...]:
    return tuple(_bar_from_any(item, index, symbol) for index, item in enumerate(tuple(bars)))


def validate_strategy_replay_bars_v1(bars: Iterable[StrategyReplayBarV1]) -> bool:
    bar_tuple = tuple(bars)
    if not bar_tuple:
        return False
    for bar in bar_tuple:
        prices = (bar.open, bar.high, bar.low, bar.close)
        if not bar.timestamp or not bar.symbol:
            return False
        if not all(_finite(price) and float(price) > 0.0 for price in prices):
            return False
        if not _finite(bar.volume) or bar.volume < 0.0:
            return False
        if bar.high < max(bar.open, bar.low, bar.close):
            return False
        if bar.low > min(bar.open, bar.high, bar.close):
            return False
    return True


def _average(values: Iterable[float]) -> float:
    items = tuple(values)
    return sum(items) / len(items) if items else 0.0


def _signal(
    bars: tuple[StrategyReplayBarV1, ...],
    strategy_type: StrategyType,
    action: str,
    confidence: float,
    reason: str,
) -> StrategyReplaySignalV1:
    reference = bars[-1].close if bars else 0.0
    symbol = bars[-1].symbol if bars else "SIM"
    return StrategyReplaySignalV1(
        symbol=symbol,
        strategy_type=strategy_type,
        action=action,
        confidence=max(0.0, min(1.0, _round(confidence))),
        reference_price=reference,
        reason=reason,
    )


def compute_moving_average_signal_v1(
    bars: Iterable[StrategyReplayBarV1],
    short_window: int = 2,
    long_window: int = 3,
) -> StrategyReplaySignalV1:
    bar_tuple = tuple(bars)
    if len(bar_tuple) < max(short_window, long_window):
        return _signal(bar_tuple, StrategyType.MOVING_AVERAGE_CROSSOVER, "HOLD", 0.5, "insufficient_bars")
    closes = tuple(bar.close for bar in bar_tuple)
    short_ma = _average(closes[-short_window:])
    long_ma = _average(closes[-long_window:])
    diff = short_ma - long_ma
    action = "BUY" if diff > 0 else "SELL" if diff < 0 else "HOLD"
    confidence = 0.5 + min(abs(diff) / max(bar_tuple[-1].close, 1.0), 0.5)
    return _signal(bar_tuple, StrategyType.MOVING_AVERAGE_CROSSOVER, action, confidence, f"short_ma={short_ma};long_ma={long_ma}")


def compute_breakout_signal_v1(
    bars: Iterable[StrategyReplayBarV1],
    breakout_window: int = 3,
) -> StrategyReplaySignalV1:
    bar_tuple = tuple(bars)
    if len(bar_tuple) <= breakout_window:
        return _signal(bar_tuple, StrategyType.BREAKOUT, "HOLD", 0.5, "insufficient_bars")
    previous = bar_tuple[-(breakout_window + 1):-1]
    current = bar_tuple[-1]
    max_high = max(bar.high for bar in previous)
    min_low = min(bar.low for bar in previous)
    if current.close > max_high:
        return _signal(bar_tuple, StrategyType.BREAKOUT, "BUY", 0.75, f"close_above_breakout={max_high}")
    if current.close < min_low:
        return _signal(bar_tuple, StrategyType.BREAKOUT, "SELL", 0.75, f"close_below_breakdown={min_low}")
    return _signal(bar_tuple, StrategyType.BREAKOUT, "HOLD", 0.55, "inside_range")


def compute_mean_reversion_signal_v1(
    bars: Iterable[StrategyReplayBarV1],
    mean_reversion_window: int = 3,
) -> StrategyReplaySignalV1:
    bar_tuple = tuple(bars)
    if len(bar_tuple) < mean_reversion_window:
        return _signal(bar_tuple, StrategyType.MEAN_REVERSION, "HOLD", 0.5, "insufficient_bars")
    closes = tuple(bar.close for bar in bar_tuple)
    mean_price = _average(closes[-mean_reversion_window:])
    current = closes[-1]
    if current < mean_price * 0.995:
        return _signal(bar_tuple, StrategyType.MEAN_REVERSION, "BUY", 0.7, f"below_mean={mean_price}")
    if current > mean_price * 1.005:
        return _signal(bar_tuple, StrategyType.MEAN_REVERSION, "SELL", 0.7, f"above_mean={mean_price}")
    return _signal(bar_tuple, StrategyType.MEAN_REVERSION, "HOLD", 0.55, "near_mean")


def compute_strategy_replay_signal_v1(
    context: StrategyReplayContextV1,
    bars: Iterable[StrategyReplayBarV1],
    data: StrategyReplayEngineV1Input | Mapping[str, Any] | None = None,
) -> StrategyReplaySignalV1:
    payload = _coerce_input(data) or StrategyReplayEngineV1Input(bars=tuple(bars), strategy_type=context.strategy_type)
    strategy = _parse_strategy(context.strategy_type)
    if payload.force_signal_invalid or strategy is None:
        return StrategyReplaySignalV1("", str(context.strategy_type), "EXECUTE", 2.0, 0.0, "invalid_signal", read_only=False)
    if strategy is StrategyType.MOVING_AVERAGE_CROSSOVER:
        return compute_moving_average_signal_v1(bars, payload.short_window, payload.long_window)
    if strategy is StrategyType.BREAKOUT:
        return compute_breakout_signal_v1(bars, payload.breakout_window)
    return compute_mean_reversion_signal_v1(bars, payload.mean_reversion_window)


def build_strategy_read_only_decision_v1(
    signal: StrategyReplaySignalV1,
    data: StrategyReplayEngineV1Input | Mapping[str, Any] | None = None,
) -> StrategyReplayReadOnlyDecisionV1:
    payload = _coerce_input(data) or StrategyReplayEngineV1Input()
    quantity = 0.0 if signal.action == "HOLD" else float(payload.requested_quantity)
    return StrategyReplayReadOnlyDecisionV1(
        symbol=signal.symbol,
        action=signal.action,
        proposed_position_size=quantity,
        reference_price=signal.reference_price,
        reason=signal.reason,
        read_only=not payload.force_read_only_decision_invalid,
        order_submitted=payload.force_read_only_decision_invalid,
        position_mutated=payload.force_read_only_decision_invalid,
    )


def _controlled_scenario(context: StrategyReplayContextV1, bars: tuple[StrategyReplayBarV1, ...]) -> ControlledOfflineSyntheticMarketScenario:
    runner_bars = tuple(
        ControlledOfflineSyntheticMarketBar(
            step=bar.index,
            symbol=bar.symbol,
            open=bar.open,
            high=bar.high,
            low=bar.low,
            close=bar.close,
            volume=bar.volume,
            timestamp=bar.timestamp,
        )
        for bar in bars
    )
    return ControlledOfflineSyntheticMarketScenario(context.run_id, context.symbol, runner_bars)


def apply_strategy_replay_risk_guards_v1(
    context: StrategyReplayContextV1,
    bars: tuple[StrategyReplayBarV1, ...],
    decision: StrategyReplayReadOnlyDecisionV1,
    data: StrategyReplayEngineV1Input | Mapping[str, Any] | None = None,
) -> StrategyReplayRiskResultV1:
    payload = _coerce_input(data) or StrategyReplayEngineV1Input()
    if payload.force_risk_guard_failed:
        return StrategyReplayRiskResultV1(False, (Risk.STRATEGY_REPLAY_RISK_GUARD_FAILED,), ("forced_risk_guard_failure",))
    risk_input = RiskGuardEnforcementV1Input(
        symbol=decision.symbol,
        requested_quantity=decision.proposed_position_size,
        reference_price=decision.reference_price,
        available_cash=payload.available_cash,
        margin_usage=payload.margin_usage,
        daily_loss=payload.daily_loss,
        drawdown=payload.drawdown,
        limits={
            "max_position_size": payload.max_position_size,
            "max_notional_exposure": payload.max_notional_exposure,
            "allowed_symbols": (context.symbol,),
        },
        synthetic_market_scenario=_controlled_scenario(context, bars),
    )
    risk_result = enforce_risk_guard_v1(risk_input)
    passed = not risk_result.risks and bool(risk_result.summary and risk_result.summary.all_passed)
    risks = () if passed else (Risk.STRATEGY_REPLAY_RISK_GUARD_FAILED,)
    reasons = tuple(_value(risk) for risk in risk_result.risks)
    return StrategyReplayRiskResultV1(passed, risks, reasons, risk_result)


def simulate_strategy_replay_broker_preview_v1(
    decision: StrategyReplayReadOnlyDecisionV1,
    data: StrategyReplayEngineV1Input | Mapping[str, Any] | None = None,
) -> StrategyReplayBrokerPreviewV1:
    payload = _coerce_input(data) or StrategyReplayEngineV1Input()
    if payload.force_broker_preview_failed:
        return StrategyReplayBrokerPreviewV1(False, "FAILED", 0.0, "forced_broker_preview_failure")
    broker_result = build_simulated_broker_stub_v1(
        SimulatedBrokerStubV1Input(
            symbol=decision.symbol,
            action=decision.action,
            requested_quantity=decision.proposed_position_size,
            reference_price=decision.reference_price,
            initial_cash=payload.available_cash,
            initial_equity=payload.available_cash,
            read_only_decision={
                "symbol": decision.symbol,
                "action": decision.action,
                "proposed_position_size": decision.proposed_position_size,
                "reference_price": decision.reference_price,
            },
        )
    )
    accepted = not broker_result.risks and broker_result.acceptance_preview is not None
    status = broker_result.acceptance_preview.status if broker_result.acceptance_preview else "FAILED"
    reason = broker_result.acceptance_preview.reason if broker_result.acceptance_preview else "broker_preview_missing"
    return StrategyReplayBrokerPreviewV1(
        accepted=accepted,
        status=status,
        notional=_round(decision.proposed_position_size * decision.reference_price),
        reason=reason,
        read_only=True,
        order_submitted=False,
        real_order=False,
        position_mutation=False,
        broker_result=broker_result,
    )


def build_strategy_replay_journal_v1(
    context: StrategyReplayContextV1,
    signal: StrategyReplaySignalV1,
    decision: StrategyReplayReadOnlyDecisionV1,
    risk_result: StrategyReplayRiskResultV1,
    broker_preview: StrategyReplayBrokerPreviewV1,
    data: StrategyReplayEngineV1Input | Mapping[str, Any] | None = None,
) -> StrategyReplayJournalResultV1 | None:
    payload = _coerce_input(data) or StrategyReplayEngineV1Input()
    if payload.force_journal_missing:
        return None
    journal_result = build_journal_writer_v1(
        JournalWriterV1Input(
            run_id=context.run_id,
            symbol=context.symbol,
            scenario_id=f"{context.run_id}:scenario",
            strategy_signal={"action": signal.action, "confidence": signal.confidence, "reason": signal.reason},
            broker_preview={"status": broker_preview.status, "read_only": broker_preview.read_only},
            risk_guard_result={"passed": risk_result.passed, "risks": tuple(_value(risk) for risk in risk_result.risks)},
            read_only_decision={"action": decision.action, "order_submitted": decision.order_submitted},
            runner_metrics={"bar_count": context.bar_count},
            blocked_reason="" if risk_result.passed else "risk_guard_failed",
        )
    )
    metrics = journal_result.metrics
    return StrategyReplayJournalResultV1(
        entry_count=metrics.total_entries if metrics else 0,
        warning_count=metrics.warning_count if metrics else 0,
        blocked_count=metrics.blocked_count if metrics else 0,
        complete=bool(metrics and metrics.complete),
        journal_result=journal_result,
    )


def compute_strategy_replay_metrics_v1(
    context: StrategyReplayContextV1,
    signal: StrategyReplaySignalV1,
    decision: StrategyReplayReadOnlyDecisionV1,
    risk_result: StrategyReplayRiskResultV1,
    broker_preview: StrategyReplayBrokerPreviewV1,
    journal: StrategyReplayJournalResultV1 | None,
    data: StrategyReplayEngineV1Input | Mapping[str, Any] | None = None,
) -> StrategyReplayMetricsV1 | None:
    payload = _coerce_input(data) or StrategyReplayEngineV1Input()
    if payload.force_metrics_missing:
        return None
    return StrategyReplayMetricsV1(
        bar_count=context.bar_count,
        strategy_used=_value(context.strategy_type),
        final_signal=signal.action,
        final_decision=decision.action,
        risk_guard_passed=risk_result.passed,
        broker_preview_status=broker_preview.status,
        journal_entry_count=journal.entry_count if journal else 0,
        warnings_count=journal.warning_count if journal else 0,
        blocked_count=journal.blocked_count if journal else 0,
    )


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
        return {key: _payload_value(item) for key, item in vars(value).items() if not key.startswith("_")}
    return str(value)


def render_strategy_replay_engine_v1_markdown_report(
    result: StrategyReplayEngineV1Result | Mapping[str, Any],
) -> str:
    if isinstance(result, StrategyReplayEngineV1Result):
        lines = [
            "# Strategy Replay Engine v1",
            "",
            f"- decision: {result.decision.value}",
            f"- state: {result.state.value}",
            f"- score: {result.score.overall_score}",
            f"- bars: {len(result.bars)}",
            f"- strategy: {_value(result.context.strategy_type) if result.context else 'none'}",
            f"- signal: {result.signal.action if result.signal else 'none'}",
            f"- read_only_decision: {result.read_only_decision.action if result.read_only_decision else 'none'}",
            f"- risk_guard_passed: {result.risk_result.passed if result.risk_result else False}",
            f"- broker_preview_status: {result.broker_preview.status if result.broker_preview else 'none'}",
            f"- journal_entries: {result.journal.entry_count if result.journal else 0}",
            f"- risks: {', '.join(risk.value for risk in result.risks) if result.risks else 'none'}",
            "",
            "## Boundaries",
            "- file_read: false",
            "- file_written: false",
            "- real_order_submitted: false",
            "- real_account_accessed: false",
            "- position_mutated: false",
        ]
        return "\n".join(lines) + "\n"
    payload = dict(result)
    return f"# Strategy Replay Engine v1\n\n- decision: {payload.get('decision', '')}\n"


def render_strategy_replay_engine_v1_json_report(
    result: StrategyReplayEngineV1Result | Mapping[str, Any],
) -> str:
    if isinstance(result, StrategyReplayEngineV1Result):
        payload = {
            "schema": "strategy_replay_engine_v1",
            "decision": result.decision.value,
            "state": result.state.value,
            "score": result.score.overall_score,
            "risks": [risk.value for risk in result.risks],
            "recommendations": [recommendation.value for recommendation in result.recommendations],
            "context": _payload_value(result.context),
            "signal": _payload_value(result.signal),
            "read_only_decision": _payload_value(result.read_only_decision),
            "risk_result": _payload_value(result.risk_result),
            "broker_preview": _payload_value(result.broker_preview),
            "journal": _payload_value(result.journal),
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


def build_strategy_replay_report_v1(
    result: StrategyReplayEngineV1Result,
    data: StrategyReplayEngineV1Input | Mapping[str, Any] | None = None,
) -> StrategyReplayReportV1 | None:
    payload = _coerce_input(data)
    if payload and payload.force_report_missing:
        return None
    return StrategyReplayReportV1(
        markdown=render_strategy_replay_engine_v1_markdown_report(result),
        json=render_strategy_replay_engine_v1_json_report(result),
    )


def _signal_valid(signal: StrategyReplaySignalV1 | None) -> bool:
    return bool(
        signal
        and signal.symbol
        and signal.action in {"BUY", "SELL", "HOLD"}
        and 0.0 <= signal.confidence <= 1.0
        and signal.reference_price > 0.0
        and signal.read_only
    )


def _decision_valid(decision: StrategyReplayReadOnlyDecisionV1 | None) -> bool:
    return bool(
        decision
        and decision.symbol
        and decision.action in {"BUY", "SELL", "HOLD"}
        and decision.proposed_position_size >= 0.0
        and decision.reference_price > 0.0
        and decision.read_only
        and not decision.order_submitted
        and not decision.position_mutated
    )


def detect_strategy_replay_engine_v1_risks(
    data: StrategyReplayEngineV1Input | Mapping[str, Any] | None,
    bars: tuple[StrategyReplayBarV1, ...] = (),
    signal: StrategyReplaySignalV1 | None = None,
    read_only_decision: StrategyReplayReadOnlyDecisionV1 | None = None,
    risk_result: StrategyReplayRiskResultV1 | None = None,
    broker_preview: StrategyReplayBrokerPreviewV1 | None = None,
    journal: StrategyReplayJournalResultV1 | None = None,
    metrics: StrategyReplayMetricsV1 | None = None,
    report: StrategyReplayReportV1 | None = None,
) -> tuple[Risk, ...]:
    payload = _coerce_input(data)
    risks: list[Risk] = []
    if payload is None:
        risks.append(Risk.STRATEGY_REPLAY_INPUT_MISSING)
    elif not payload.bars:
        risks.append(Risk.STRATEGY_REPLAY_BARS_EMPTY)
    if payload is not None and _parse_strategy(payload.strategy_type) is None:
        risks.append(Risk.STRATEGY_REPLAY_STRATEGY_UNSUPPORTED)
    if bars and not validate_strategy_replay_bars_v1(bars):
        risks.append(Risk.STRATEGY_REPLAY_BAR_INVALID)
    if payload is not None and payload.bars and not bars:
        risks.append(Risk.STRATEGY_REPLAY_BARS_EMPTY)
    if not _signal_valid(signal) and payload is not None and bars and _parse_strategy(payload.strategy_type):
        risks.append(Risk.STRATEGY_REPLAY_SIGNAL_INVALID)
    if not _decision_valid(read_only_decision) and signal is not None:
        risks.append(Risk.STRATEGY_REPLAY_READ_ONLY_DECISION_INVALID)
    if not risk_result or not risk_result.passed or risk_result.risks:
        if read_only_decision is not None:
            risks.append(Risk.STRATEGY_REPLAY_RISK_GUARD_FAILED)
    if (
        not broker_preview
        or not broker_preview.accepted
        or not broker_preview.read_only
        or broker_preview.order_submitted
        or broker_preview.real_order
        or broker_preview.position_mutation
    ):
        if risk_result is not None:
            risks.append(Risk.STRATEGY_REPLAY_BROKER_PREVIEW_FAILED)
    if not journal or not journal.complete or journal.entry_count <= 0:
        if broker_preview is not None:
            risks.append(Risk.STRATEGY_REPLAY_JOURNAL_MISSING)
    if metrics is None:
        if journal is not None:
            risks.append(Risk.STRATEGY_REPLAY_METRICS_MISSING)
    if report is None or not report.markdown or not report.json:
        risks.append(Risk.STRATEGY_REPLAY_REPORT_MISSING)
    risks.extend(_boundary_risks(payload))
    return _dedupe(risks)


def generate_strategy_replay_engine_v1_recommendations(
    risks: Iterable[Risk],
) -> tuple[Recommendation, ...]:
    mapping = {
        Risk.STRATEGY_REPLAY_INPUT_MISSING: Recommendation.PROVIDE_STRATEGY_REPLAY_INPUT,
        Risk.STRATEGY_REPLAY_BARS_EMPTY: Recommendation.PROVIDE_STRATEGY_REPLAY_BARS,
        Risk.STRATEGY_REPLAY_BAR_INVALID: Recommendation.FIX_STRATEGY_REPLAY_BARS,
        Risk.STRATEGY_REPLAY_STRATEGY_UNSUPPORTED: Recommendation.USE_SUPPORTED_STRATEGY,
        Risk.STRATEGY_REPLAY_SIGNAL_INVALID: Recommendation.FIX_STRATEGY_SIGNAL,
        Risk.STRATEGY_REPLAY_READ_ONLY_DECISION_INVALID: Recommendation.KEEP_DECISION_READ_ONLY,
        Risk.STRATEGY_REPLAY_RISK_GUARD_FAILED: Recommendation.FIX_STRATEGY_RISK_GUARDS,
        Risk.STRATEGY_REPLAY_BROKER_PREVIEW_FAILED: Recommendation.FIX_STRATEGY_BROKER_PREVIEW,
        Risk.STRATEGY_REPLAY_JOURNAL_MISSING: Recommendation.WRITE_STRATEGY_REPLAY_JOURNAL,
        Risk.STRATEGY_REPLAY_METRICS_MISSING: Recommendation.COMPUTE_STRATEGY_REPLAY_METRICS,
        Risk.STRATEGY_REPLAY_REPORT_MISSING: Recommendation.GENERATE_STRATEGY_REPLAY_REPORT,
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
    recommendations.append(Recommendation.RUN_STRATEGY_REPLAY_ENGINE_V1_TEST_SUITE)
    if not recommendations or recommendations == [Recommendation.RUN_STRATEGY_REPLAY_ENGINE_V1_TEST_SUITE]:
        recommendations.append(Recommendation.APPROVE_AGICORE_TRADING_V1_CANDIDATE)
    return _dedupe(recommendations)


def _build_score(
    data: StrategyReplayEngineV1Input | None,
    bars: tuple[StrategyReplayBarV1, ...],
    signal: StrategyReplaySignalV1 | None,
    decision: StrategyReplayReadOnlyDecisionV1 | None,
    risk_result: StrategyReplayRiskResultV1 | None,
    broker_preview: StrategyReplayBrokerPreviewV1 | None,
    journal: StrategyReplayJournalResultV1 | None,
    metrics: StrategyReplayMetricsV1 | None,
    report: StrategyReplayReportV1 | None,
    risks: tuple[Risk, ...],
) -> StrategyReplayEngineV1Score:
    input_score = 100 if data is not None and data.bars and _parse_strategy(data.strategy_type) else 0
    bar_score = 100 if validate_strategy_replay_bars_v1(bars) else 0
    signal_score = 100 if _signal_valid(signal) else 0
    decision_score = 100 if _decision_valid(decision) else 0
    risk_score = 100 if risk_result and risk_result.passed and not risk_result.risks else 0
    broker_score = 100 if broker_preview and broker_preview.accepted and broker_preview.read_only and not broker_preview.order_submitted and not broker_preview.real_order else 0
    journal_score = 100 if journal and journal.complete and journal.entry_count > 0 else 0
    metrics_score = 100 if metrics else 0
    report_score = 100 if report and report.markdown and report.json else 0
    boundary_score = 100 if not _boundary_risks(data) else 0
    parts = (
        input_score,
        bar_score,
        signal_score,
        decision_score,
        risk_score,
        broker_score,
        journal_score,
        metrics_score,
        report_score,
        boundary_score,
    )
    overall = min(parts)
    if risks:
        overall = min(overall, max(0, 100 - len(risks) * 10))
    return StrategyReplayEngineV1Score(
        overall_score=overall,
        input_score=input_score,
        bar_score=bar_score,
        signal_score=signal_score,
        decision_score=decision_score,
        risk_score=risk_score,
        broker_score=broker_score,
        journal_score=journal_score,
        metrics_score=metrics_score,
        report_score=report_score,
        boundary_score=boundary_score,
    )


def assert_strategy_replay_engine_v1_offline_boundaries(
    data: StrategyReplayEngineV1Input | Mapping[str, Any] | None,
) -> bool:
    return not _boundary_risks(_coerce_input(data))


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_STRATEGY_REPLAY_ENGINE_V1
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
        return Decision.BLOCK_STRATEGY_REPLAY_ENGINE_V1
    if Risk.STRATEGY_REPLAY_INPUT_MISSING in risks:
        return Decision.REQUIRE_STRATEGY_REPLAY_INPUT_FIXES
    if Risk.STRATEGY_REPLAY_BARS_EMPTY in risks or Risk.STRATEGY_REPLAY_BAR_INVALID in risks:
        return Decision.REQUIRE_STRATEGY_REPLAY_BARS_FIXES
    if Risk.STRATEGY_REPLAY_STRATEGY_UNSUPPORTED in risks:
        return Decision.REQUIRE_STRATEGY_REPLAY_INPUT_FIXES
    if Risk.STRATEGY_REPLAY_SIGNAL_INVALID in risks:
        return Decision.REQUIRE_STRATEGY_SIGNAL_FIXES
    if Risk.STRATEGY_REPLAY_READ_ONLY_DECISION_INVALID in risks:
        return Decision.REQUIRE_STRATEGY_READ_ONLY_DECISION_FIXES
    if Risk.STRATEGY_REPLAY_RISK_GUARD_FAILED in risks:
        return Decision.REQUIRE_STRATEGY_RISK_GUARD_FIXES
    if Risk.STRATEGY_REPLAY_BROKER_PREVIEW_FAILED in risks:
        return Decision.REQUIRE_STRATEGY_BROKER_PREVIEW_FIXES
    if Risk.STRATEGY_REPLAY_JOURNAL_MISSING in risks:
        return Decision.REQUIRE_STRATEGY_JOURNAL_FIXES
    if Risk.STRATEGY_REPLAY_METRICS_MISSING in risks:
        return Decision.REQUIRE_STRATEGY_METRICS_FIXES
    if Risk.STRATEGY_REPLAY_REPORT_MISSING in risks:
        return Decision.REQUIRE_STRATEGY_REPORT_FIXES
    return Decision.BLOCK_STRATEGY_REPLAY_ENGINE_V1


def _state_for(risks: tuple[Risk, ...], decision: Decision) -> State:
    if Risk.STRATEGY_REPLAY_INPUT_MISSING in risks or Risk.STRATEGY_REPLAY_BARS_EMPTY in risks:
        return State.STRATEGY_REPLAY_ENGINE_V1_INPUT_INVALID
    if decision is Decision.APPROVE_STRATEGY_REPLAY_ENGINE_V1:
        return State.READY_FOR_AGICORE_TRADING_V1_CANDIDATE
    return State.STRATEGY_REPLAY_ENGINE_V1_BLOCKED


def run_strategy_replay_engine_v1(
    data: StrategyReplayEngineV1Input | Mapping[str, Any] | None,
) -> StrategyReplayEngineV1Result:
    payload = _coerce_input(data)
    context = build_strategy_replay_context_v1(payload) if payload else None
    bars = normalize_strategy_replay_bars_v1(payload.bars, payload.symbol) if payload else ()
    signal = None
    read_only_decision = None
    risk_result = None
    broker_preview = None
    journal = None
    metrics = None
    report = None

    if payload and context and bars and validate_strategy_replay_bars_v1(bars) and _parse_strategy(payload.strategy_type):
        signal = compute_strategy_replay_signal_v1(context, bars, payload)
        read_only_decision = build_strategy_read_only_decision_v1(signal, payload)
        if _signal_valid(signal) and _decision_valid(read_only_decision):
            risk_result = apply_strategy_replay_risk_guards_v1(context, bars, read_only_decision, payload)
            broker_preview = simulate_strategy_replay_broker_preview_v1(read_only_decision, payload)
            journal = build_strategy_replay_journal_v1(context, signal, read_only_decision, risk_result, broker_preview, payload)
            metrics = compute_strategy_replay_metrics_v1(context, signal, read_only_decision, risk_result, broker_preview, journal, payload)

    early_risks = detect_strategy_replay_engine_v1_risks(
        payload,
        bars=bars,
        signal=signal,
        read_only_decision=read_only_decision,
        risk_result=risk_result,
        broker_preview=broker_preview,
        journal=journal,
        metrics=metrics,
        report=StrategyReplayReportV1("", "") if payload and not payload.force_report_missing else None,
    )
    early_score = _build_score(payload, bars, signal, read_only_decision, risk_result, broker_preview, journal, metrics, None, early_risks)
    early = StrategyReplayEngineV1Result(
        state=State.NOT_READY,
        decision=Decision.BLOCK_STRATEGY_REPLAY_ENGINE_V1,
        score=early_score,
        risks=early_risks,
        recommendations=generate_strategy_replay_engine_v1_recommendations(early_risks),
        context=context,
        bars=bars,
        signal=signal,
        read_only_decision=read_only_decision,
        risk_result=risk_result,
        broker_preview=broker_preview,
        journal=journal,
        metrics=metrics,
    )
    report = build_strategy_replay_report_v1(early, payload)
    risks = detect_strategy_replay_engine_v1_risks(
        payload,
        bars=bars,
        signal=signal,
        read_only_decision=read_only_decision,
        risk_result=risk_result,
        broker_preview=broker_preview,
        journal=journal,
        metrics=metrics,
        report=report,
    )
    score = _build_score(payload, bars, signal, read_only_decision, risk_result, broker_preview, journal, metrics, report, risks)
    recommendations = generate_strategy_replay_engine_v1_recommendations(risks)
    decision = _decision_for(risks)
    state = _state_for(risks, decision)
    final_without_report = StrategyReplayEngineV1Result(
        state=state,
        decision=decision,
        score=score,
        risks=risks,
        recommendations=recommendations,
        context=context,
        bars=bars,
        signal=signal,
        read_only_decision=read_only_decision,
        risk_result=risk_result,
        broker_preview=broker_preview,
        journal=journal,
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
    report = build_strategy_replay_report_v1(final_without_report, payload)
    return StrategyReplayEngineV1Result(**{**final_without_report.__dict__, "report": report})
