"""Deterministic multi-scenario controlled simulation for AGIcore."""

from __future__ import annotations

import math
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.controlled_simulation_offline_runner import run_controlled_simulation_offline_runner
from agicore.trading.controlled_simulation_offline_runner_models import (
    ControlledSimulationOfflineRunnerInput,
    OfflineSignalEvent,
    OfflineSyntheticMarketBar,
)
from agicore.trading.multi_scenario_controlled_simulation_models import (
    ControlledSimulationScenarioDefinition,
    ControlledSimulationScenarioResult,
    ControlledSimulationScenarioType,
    MultiScenarioAggregateReport,
    MultiScenarioControlledSimulationDecision,
    MultiScenarioControlledSimulationInput,
    MultiScenarioControlledSimulationRecommendation,
    MultiScenarioControlledSimulationResult,
    MultiScenarioControlledSimulationRisk,
    MultiScenarioControlledSimulationScore,
    MultiScenarioControlledSimulationState,
    MultiScenarioFailureFinding,
    MultiScenarioMetricSummary,
    MultiScenarioRobustnessFinding,
)


_REQUIRED_SCENARIO_TYPES = (
    ControlledSimulationScenarioType.WINNING_SCENARIO,
    ControlledSimulationScenarioType.LOSING_SCENARIO,
    ControlledSimulationScenarioType.FLAT_SCENARIO,
    ControlledSimulationScenarioType.DRAWDOWN_SCENARIO,
    ControlledSimulationScenarioType.VOLATILE_SCENARIO,
    ControlledSimulationScenarioType.STOP_CONDITION_SCENARIO,
    ControlledSimulationScenarioType.RISK_VIOLATION_SCENARIO,
    ControlledSimulationScenarioType.POSITION_INCONSISTENCY_SCENARIO,
)


def _coerce_input(data: MultiScenarioControlledSimulationInput | Mapping[str, Any]) -> MultiScenarioControlledSimulationInput:
    if isinstance(data, MultiScenarioControlledSimulationInput):
        return data
    allowed = {field.name for field in fields(MultiScenarioControlledSimulationInput)}
    payload = {key: value for key, value in dict(data).items() if key in allowed}
    return MultiScenarioControlledSimulationInput(**payload)


def _value(item: Any) -> str:
    if item is None:
        return ""
    if isinstance(item, Enum):
        return str(item.value)
    return str(item)


def _get(obj: Any, name: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, Mapping):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _as_tuple(items: Any) -> tuple[Any, ...]:
    if items is None:
        return ()
    if isinstance(items, tuple):
        return items
    if isinstance(items, list):
        return tuple(items)
    if isinstance(items, set):
        return tuple(items)
    return (items,)


def _contains(items: Any, *needles: str) -> bool:
    text_items = tuple(_value(item).upper() for item in _as_tuple(items))
    return any(any(needle.upper() in item for item in text_items) for needle in needles)


def _dedupe(items: Iterable[Any]) -> tuple[Any, ...]:
    seen: set[Any] = set()
    result: list[Any] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return tuple(result)


def _clamp(value: int | float, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(round(value))))


def _finite(value: Any) -> bool:
    return isinstance(value, int | float) and math.isfinite(float(value))


def _numeric_or_inf(value: Any) -> bool:
    return isinstance(value, int | float) and not math.isnan(float(value))


def _round(value: float, digits: int = 10) -> float:
    return round(float(value), digits)


def _bar(step: int, close: float, symbol: str = "SIM", previous: float | None = None) -> OfflineSyntheticMarketBar:
    open_price = close if previous is None else previous
    high = max(open_price, close) + 0.5
    low = min(open_price, close) - 0.5
    return OfflineSyntheticMarketBar(step, symbol, open_price, high, low, close, 1_000.0, f"T{step}")


def _path(closes: tuple[float, ...], symbol: str = "SIM") -> tuple[OfflineSyntheticMarketBar, ...]:
    bars: list[OfflineSyntheticMarketBar] = []
    previous: float | None = None
    for step, close in enumerate(closes):
        bars.append(_bar(step, close, symbol, previous))
        previous = close
    return tuple(bars)


def _signals(items: tuple[tuple[int, str, float, str], ...], symbol: str = "SIM") -> tuple[OfflineSignalEvent, ...]:
    return tuple(OfflineSignalEvent(step, symbol, action, quantity, 1.0, reason) for step, action, quantity, reason in items)


def _upstream_items(data: MultiScenarioControlledSimulationInput) -> tuple[Any, ...]:
    return (
        data.performance_risk_validation_gate,
        data.performance_metrics_result,
        data.risk_metrics_result,
        data.controlled_simulation_result_report,
        data.controlled_simulation_offline_runner_result,
        data.offline_simulation_metrics,
        data.offline_equity_point,
        data.offline_position_state,
        data.offline_stop_condition_result,
        data.paper_runtime_forward_test_plan,
        data.official_paper_validation_report,
        data.paper_runtime_validation,
        data.paper_trading_runtime,
        data.observability_verification,
        data.rollback_verification,
        data.kill_switch_verification,
        data.human_validated_paper_session,
        data.supervised_paper_session,
    )


def _upstream_risks(data: MultiScenarioControlledSimulationInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: MultiScenarioControlledSimulationInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _state_contains(obj: Any, *needles: str) -> bool:
    return _contains((_get(obj, "state"), _get(obj, "decision")), *needles)


def _offline_boundary(data: MultiScenarioControlledSimulationInput) -> bool:
    return (
        data.offline_mode_enforced is True
        and data.sandbox_mode_enforced is True
        and data.no_real_broker is True
        and data.no_alpaca_real is True
        and data.no_api_key_read is True
        and data.no_http_transport is True
        and data.no_websocket_transport is True
        and data.no_socket_transport is True
        and data.no_external_api is True
        and data.no_external_ml is True
        and data.no_external_llm is True
        and data.no_live_execution is True
        and data.no_real_order is True
        and data.no_real_account_access is True
        and data.real_execution_requested is not True
        and all(_get(item, "offline_only", True) is True for item in _upstream_items(data))
        and not _has_upstream_risk(
            data,
            "LIVE_EXECUTION",
            "API_ACCESS",
            "NETWORK_LEAK",
            "BROKER_CONNECTIVITY",
            "EXTERNAL_DEPENDENCY",
            "HTTP",
            "WEBSOCKET",
            "SOCKET",
            "REAL_ORDER",
            "REAL_ACCOUNT",
            "REAL_EXECUTION",
            "API_KEY",
            "CREDENTIAL",
        )
    )


def _data_boundary(data: MultiScenarioControlledSimulationInput) -> bool:
    return (
        data.synthetic_data_only is True
        and data.in_memory_only is True
        and data.data_access_requested is not True
        and not _has_upstream_risk(data, "DATA_ACCESS", "DATA_ACCESS_VIOLATION", "REAL_DATA")
    )


def validate_performance_risk_validation_gate(
    data: MultiScenarioControlledSimulationInput | Mapping[str, Any],
) -> bool:
    data = _coerce_input(data)
    gate = data.performance_risk_validation_gate
    if gate is None:
        return False
    approved = (
        data.performance_risk_validation_approved is not False
        and (
            data.performance_risk_validation_approved is True
            or _state_contains(
                gate,
                "READY_FOR_MULTI_SCENARIO_CONTROLLED_SIMULATION",
                "APPROVE_PERFORMANCE_RISK_VALIDATION_GATE",
            )
        )
    )
    return (
        approved
        and _get(gate, "offline_only", True) is True
        and not _contains(
            _get(gate, "risks", ()),
            "PERFORMANCE_METRICS_NOT_APPROVED",
            "RISK_METRICS_NOT_APPROVED",
            "PERFORMANCE_RISK_INPUT_MISSING",
            "REAL_EXECUTION_BOUNDARY_VIOLATION",
            "DATA_ACCESS_VIOLATION",
            "PREMATURE_MULTI_SCENARIO_CONTROLLED_SIMULATION",
        )
    )


def build_winning_scenario(symbol: str = "SIM") -> ControlledSimulationScenarioDefinition:
    return ControlledSimulationScenarioDefinition(
        "winning",
        ControlledSimulationScenarioType.WINNING_SCENARIO,
        symbol,
        market_path=_path((100.0, 104.0, 108.0, 112.0), symbol),
        signal_sequence=_signals(((0, "BUY", 1.0, "winning_entry"), (3, "SELL", 1.0, "winning_exit")), symbol),
        description="simple winning trade",
    )


def build_losing_scenario(symbol: str = "SIM") -> ControlledSimulationScenarioDefinition:
    return ControlledSimulationScenarioDefinition(
        "losing",
        ControlledSimulationScenarioType.LOSING_SCENARIO,
        symbol,
        market_path=_path((100.0, 98.0, 96.0, 95.0), symbol),
        signal_sequence=_signals(((0, "BUY", 1.0, "losing_entry"), (3, "SELL", 1.0, "losing_exit")), symbol),
        description="controlled losing trade within limits",
    )


def build_flat_scenario(symbol: str = "SIM") -> ControlledSimulationScenarioDefinition:
    return ControlledSimulationScenarioDefinition(
        "flat",
        ControlledSimulationScenarioType.FLAT_SCENARIO,
        symbol,
        market_path=_path((100.0, 100.0, 100.0, 100.0), symbol),
        signal_sequence=_signals(((0, "HOLD", 0.0, "flat_start"), (3, "HOLD", 0.0, "flat_end")), symbol),
        description="flat no-trade scenario",
    )


def build_drawdown_scenario(symbol: str = "SIM") -> ControlledSimulationScenarioDefinition:
    return ControlledSimulationScenarioDefinition(
        "drawdown",
        ControlledSimulationScenarioType.DRAWDOWN_SCENARIO,
        symbol,
        market_path=_path((100.0, 90.0, 96.0, 106.0), symbol),
        signal_sequence=_signals(((0, "BUY", 1.0, "drawdown_entry"), (3, "SELL", 1.0, "drawdown_recovery_exit")), symbol),
        max_drawdown_fraction=0.50,
        description="temporary drawdown with recovery",
    )


def build_volatile_scenario(symbol: str = "SIM") -> ControlledSimulationScenarioDefinition:
    return ControlledSimulationScenarioDefinition(
        "volatile",
        ControlledSimulationScenarioType.VOLATILE_SCENARIO,
        symbol,
        market_path=_path((100.0, 112.0, 92.0, 115.0, 108.0), symbol),
        signal_sequence=_signals(((0, "BUY", 1.0, "volatile_entry"), (4, "SELL", 1.0, "volatile_exit")), symbol),
        max_drawdown_fraction=0.50,
        description="high volatility scenario",
    )


def build_stop_condition_scenario(symbol: str = "SIM") -> ControlledSimulationScenarioDefinition:
    return ControlledSimulationScenarioDefinition(
        "stop_condition",
        ControlledSimulationScenarioType.STOP_CONDITION_SCENARIO,
        symbol,
        market_path=_path((100.0, 97.0, 101.0, 103.0), symbol),
        signal_sequence=_signals(((0, "BUY", 1.0, "stop_policy_entry"), (3, "SELL", 1.0, "stop_policy_exit")), symbol),
        max_drawdown_fraction=0.20,
        max_loss_amount=5_000.0,
        stop_conditions_required=True,
        description="stop policy configured and not breached",
    )


def build_risk_violation_scenario(symbol: str = "SIM") -> ControlledSimulationScenarioDefinition:
    return ControlledSimulationScenarioDefinition(
        "risk_violation",
        ControlledSimulationScenarioType.RISK_VIOLATION_SCENARIO,
        symbol,
        market_path=_path((100.0, 101.0, 103.0, 104.0), symbol),
        signal_sequence=_signals(((0, "BUY", 1.0, "risk_control_entry"), (3, "SELL", 1.0, "risk_control_exit")), symbol),
        max_order_quantity=2.0,
        max_position_quantity=2.0,
        description="risk-control drill inside configured limits",
    )


def build_position_inconsistency_scenario(symbol: str = "SIM") -> ControlledSimulationScenarioDefinition:
    return ControlledSimulationScenarioDefinition(
        "position_inconsistency",
        ControlledSimulationScenarioType.POSITION_INCONSISTENCY_SCENARIO,
        symbol,
        market_path=_path((100.0, 102.0, 104.0), symbol),
        signal_sequence=_signals(((0, "BUY", 1.0, "open_position_probe"),), symbol),
        require_flat_final_position=False,
        allow_open_final_position=True,
        description="open-position probe explicitly allowed for robustness coverage",
    )


def _build_mixed_scenario(symbol: str = "SIM") -> ControlledSimulationScenarioDefinition:
    return ControlledSimulationScenarioDefinition(
        "mixed",
        ControlledSimulationScenarioType.MIXED_SCENARIO,
        symbol,
        market_path=_path((100.0, 104.0, 99.0, 103.0, 107.0), symbol),
        signal_sequence=_signals(
            (
                (0, "BUY", 1.0, "mixed_entry_a"),
                (1, "SELL", 1.0, "mixed_exit_a"),
                (2, "BUY", 1.0, "mixed_entry_b"),
                (4, "SELL", 1.0, "mixed_exit_b"),
            ),
            symbol,
        ),
        description="mixed scenario with multiple trades",
    )


def _coerce_scenario(item: ControlledSimulationScenarioDefinition | Mapping[str, Any]) -> ControlledSimulationScenarioDefinition:
    if isinstance(item, ControlledSimulationScenarioDefinition):
        return item
    allowed = {field.name for field in fields(ControlledSimulationScenarioDefinition)}
    payload = {key: value for key, value in dict(item).items() if key in allowed}
    scenario_type = payload.get("scenario_type", ControlledSimulationScenarioType.MIXED_SCENARIO)
    if not isinstance(scenario_type, ControlledSimulationScenarioType):
        scenario_type = ControlledSimulationScenarioType(str(scenario_type))
    payload["scenario_type"] = scenario_type
    return ControlledSimulationScenarioDefinition(**payload)


def build_multi_scenario_suite(
    data: MultiScenarioControlledSimulationInput | Mapping[str, Any] | None = None,
) -> tuple[ControlledSimulationScenarioDefinition, ...]:
    if data is not None:
        data = _coerce_input(data)
        if data.scenario_suite is not None:
            return tuple(_coerce_scenario(item) for item in data.scenario_suite)
    return (
        build_winning_scenario(),
        build_losing_scenario(),
        build_flat_scenario(),
        build_drawdown_scenario(),
        build_volatile_scenario(),
        build_stop_condition_scenario(),
        build_risk_violation_scenario(),
        build_position_inconsistency_scenario(),
        _build_mixed_scenario(),
    )


def _scenario_definition_valid(definition: ControlledSimulationScenarioDefinition) -> bool:
    return (
        bool(definition.scenario_id)
        and isinstance(definition.scenario_type, ControlledSimulationScenarioType)
        and bool(definition.market_path)
        and bool(definition.signal_sequence)
        and definition.initial_equity > 0
        and (definition.max_steps is None or definition.max_steps > 0)
        and (definition.max_order_quantity is None or definition.max_order_quantity > 0)
        and (definition.max_position_quantity is None or definition.max_position_quantity > 0)
        and (definition.max_drawdown_fraction is None or definition.max_drawdown_fraction >= 0)
        and (definition.max_loss_amount is None or definition.max_loss_amount >= 0)
    )


def _runner_input_for_scenario(
    definition: ControlledSimulationScenarioDefinition,
    data: MultiScenarioControlledSimulationInput,
) -> ControlledSimulationOfflineRunnerInput:
    return ControlledSimulationOfflineRunnerInput(
        controlled_simulation_review_precheck={
            "state": "READY_FOR_CONTROLLED_SIMULATION_OFFLINE_RUNNER",
            "decision": "APPROVE_CONTROLLED_SIMULATION_REVIEW_PRECHECK",
            "risks": (),
            "offline_only": True,
        },
        paper_runtime_forward_test_plan=data.paper_runtime_forward_test_plan,
        official_paper_validation_report=data.official_paper_validation_report,
        paper_runtime_validation=data.paper_runtime_validation,
        paper_trading_runtime=data.paper_trading_runtime,
        observability_verification=data.observability_verification,
        rollback_verification=data.rollback_verification,
        kill_switch_verification=data.kill_switch_verification,
        human_validated_paper_session=data.human_validated_paper_session,
        supervised_paper_session=data.supervised_paper_session,
        scenario_id=definition.scenario_id,
        symbol=definition.symbol,
        initial_equity=definition.initial_equity,
        synthetic_market_path=definition.market_path,
        signal_sequence=definition.signal_sequence,
        max_steps=definition.max_steps,
        max_order_quantity=definition.max_order_quantity,
        max_position_quantity=definition.max_position_quantity,
        max_drawdown_fraction=definition.max_drawdown_fraction,
        max_loss_amount=definition.max_loss_amount,
        commission_per_fill=definition.commission_per_fill,
        slippage_per_unit=definition.slippage_per_unit,
        require_flat_final_position=definition.require_flat_final_position,
        stop_conditions_required=definition.stop_conditions_required,
        review_precheck_approved=True,
        offline_mode_enforced=data.offline_mode_enforced,
        sandbox_mode_enforced=data.sandbox_mode_enforced,
        no_real_broker=data.no_real_broker,
        no_alpaca_real=data.no_alpaca_real,
        no_api_key_read=data.no_api_key_read,
        no_http_transport=data.no_http_transport,
        no_websocket_transport=data.no_websocket_transport,
        no_socket_transport=data.no_socket_transport,
        no_external_api=data.no_external_api,
        no_external_ml=data.no_external_ml,
        no_external_llm=data.no_external_llm,
        no_live_execution=data.no_live_execution,
        no_real_order=data.no_real_order,
        no_real_account_access=data.no_real_account_access,
        synthetic_data_only=data.synthetic_data_only,
        in_memory_only=data.in_memory_only,
        data_access_requested=data.data_access_requested,
        real_execution_requested=data.real_execution_requested,
        result_report_requested=False,
    )


def execute_controlled_simulation_scenario(
    definition: ControlledSimulationScenarioDefinition | Mapping[str, Any],
    data: MultiScenarioControlledSimulationInput | Mapping[str, Any] | None = None,
) -> ControlledSimulationScenarioResult:
    definition = _coerce_scenario(definition)
    data = MultiScenarioControlledSimulationInput() if data is None else _coerce_input(data)
    if not _scenario_definition_valid(definition):
        failure = MultiScenarioFailureFinding(
            definition.scenario_id,
            definition.scenario_type,
            "scenario_definition_invalid",
            (MultiScenarioControlledSimulationRisk.SCENARIO_DEFINITION_INVALID,),
        )
        return ControlledSimulationScenarioResult(
            definition.scenario_id,
            definition.scenario_type,
            False,
            None,
            risks=(MultiScenarioControlledSimulationRisk.SCENARIO_DEFINITION_INVALID,),
            failures=(failure,),
        )
    runner_result = run_controlled_simulation_offline_runner(_runner_input_for_scenario(definition, data))
    metrics = runner_result.metrics
    final_position_quantity = float(_get(runner_result.final_position, "quantity", 0.0) or 0.0)
    failures: list[MultiScenarioFailureFinding] = []
    if runner_result.risks:
        failures.append(
            MultiScenarioFailureFinding(
                definition.scenario_id,
                definition.scenario_type,
                "runner_risks_detected",
                (MultiScenarioControlledSimulationRisk.SCENARIO_EXECUTION_FAILED,),
                tuple(_value(risk) for risk in runner_result.risks),
            )
        )
    if abs(final_position_quantity) > 1e-9 and not definition.allow_open_final_position:
        failures.append(
            MultiScenarioFailureFinding(
                definition.scenario_id,
                definition.scenario_type,
                "final_position_inconsistent",
                (MultiScenarioControlledSimulationRisk.SCENARIO_EXECUTION_FAILED,),
                (f"quantity={final_position_quantity}",),
            )
        )
    rejected_decisions = tuple(decision for decision in runner_result.decisions if _get(decision, "accepted", True) is False)
    if rejected_decisions:
        failures.append(
            MultiScenarioFailureFinding(
                definition.scenario_id,
                definition.scenario_type,
                "decision_rejected",
                (MultiScenarioControlledSimulationRisk.SCENARIO_EXECUTION_FAILED,),
                tuple(_get(decision, "reason", "rejected") for decision in rejected_decisions),
            )
        )
    passed = not failures
    return ControlledSimulationScenarioResult(
        definition.scenario_id,
        definition.scenario_type,
        passed,
        runner_result,
        _round(metrics.total_pnl),
        _round(metrics.max_drawdown),
        _round(metrics.max_drawdown_fraction),
        _round(metrics.win_rate),
        float(metrics.profit_factor),
        _round(metrics.expectancy),
        int(metrics.trade_count),
        _round(final_position_quantity),
        tuple(runner_result.risks),
        tuple(failures),
    )


def compute_multi_scenario_pnl(scenario_results: tuple[ControlledSimulationScenarioResult, ...]) -> float:
    return _round(sum(result.pnl for result in scenario_results))


def compute_multi_scenario_drawdown(
    scenario_results: tuple[ControlledSimulationScenarioResult, ...],
) -> tuple[float, float]:
    if not scenario_results:
        return 0.0, 0.0
    return (
        _round(max(result.max_drawdown for result in scenario_results)),
        _round(max(result.max_drawdown_fraction for result in scenario_results)),
    )


def compute_multi_scenario_win_rate(scenario_results: tuple[ControlledSimulationScenarioResult, ...]) -> float:
    trade_results = tuple(result for result in scenario_results if result.trade_count > 0)
    if not trade_results:
        return 0.0
    return _round(sum(1 for result in trade_results if result.pnl > 0) / len(trade_results))


def compute_multi_scenario_profit_factor(scenario_results: tuple[ControlledSimulationScenarioResult, ...]) -> float:
    gross_profit = sum(result.pnl for result in scenario_results if result.pnl > 0)
    gross_loss = abs(sum(result.pnl for result in scenario_results if result.pnl < 0))
    if gross_loss == 0:
        return float("inf") if gross_profit > 0 else 0.0
    return _round(gross_profit / gross_loss)


def compute_multi_scenario_expectancy(scenario_results: tuple[ControlledSimulationScenarioResult, ...]) -> float:
    trade_results = tuple(result for result in scenario_results if result.trade_count > 0)
    if not trade_results:
        return 0.0
    return _round(sum(result.pnl for result in trade_results) / len(trade_results))


def compute_multi_scenario_stability_score(scenario_results: tuple[ControlledSimulationScenarioResult, ...]) -> int:
    if not scenario_results:
        return 0
    pnls = [result.pnl for result in scenario_results]
    average = sum(pnls) / len(pnls)
    dispersion = sum(abs(pnl - average) for pnl in pnls) / len(pnls)
    baseline = max(max(abs(pnl) for pnl in pnls), 1.0)
    _, max_drawdown_fraction = compute_multi_scenario_drawdown(scenario_results)
    failure_penalty = sum(1 for result in scenario_results if not result.passed) * 8
    return _clamp(100 - (dispersion / baseline * 35) - (max_drawdown_fraction * 100) - failure_penalty)


def compute_multi_scenario_robustness_score(
    metric_summary: MultiScenarioMetricSummary,
) -> int:
    if metric_summary.scenario_count <= 0:
        return 0
    pass_ratio_score = metric_summary.passed_scenario_count / metric_summary.scenario_count * 100
    drawdown_score = max(0.0, 100 - metric_summary.max_drawdown_fraction * 100)
    loss_penalty = min(30, metric_summary.loss_scenario_count * 4)
    risk_penalty = min(30, (metric_summary.risk_violation_count + metric_summary.position_inconsistency_count) * 10)
    profit_score = 100 if metric_summary.total_pnl >= 0 else 70
    return _clamp((pass_ratio_score + drawdown_score + metric_summary.stability_score + profit_score) / 4 - loss_penalty - risk_penalty)


def aggregate_multi_scenario_metrics(
    scenario_results: tuple[ControlledSimulationScenarioResult, ...],
) -> MultiScenarioMetricSummary:
    scenario_results = tuple(scenario_results)
    scenario_count = len(scenario_results)
    passed_count = sum(1 for result in scenario_results if result.passed)
    failed_count = scenario_count - passed_count
    total_pnl = compute_multi_scenario_pnl(scenario_results)
    max_drawdown, max_drawdown_fraction = compute_multi_scenario_drawdown(scenario_results)
    summary = MultiScenarioMetricSummary(
        scenario_count,
        passed_count,
        failed_count,
        total_pnl,
        _round(total_pnl / scenario_count) if scenario_count else 0.0,
        max_drawdown,
        max_drawdown_fraction,
        compute_multi_scenario_win_rate(scenario_results),
        compute_multi_scenario_profit_factor(scenario_results),
        compute_multi_scenario_expectancy(scenario_results),
        sum(result.trade_count for result in scenario_results),
        sum(1 for result in scenario_results if result.pnl < 0),
        sum(1 for result in scenario_results if result.max_drawdown_fraction >= 0.20),
        sum(1 for result in scenario_results if result.scenario_type == ControlledSimulationScenarioType.RISK_VIOLATION_SCENARIO and not result.passed),
        sum(
            1
            for result in scenario_results
            if result.scenario_type == ControlledSimulationScenarioType.POSITION_INCONSISTENCY_SCENARIO and not result.passed
        ),
        compute_multi_scenario_stability_score(scenario_results),
        0,
    )
    return MultiScenarioMetricSummary(
        summary.scenario_count,
        summary.passed_scenario_count,
        summary.failed_scenario_count,
        summary.total_pnl,
        summary.average_pnl,
        summary.max_drawdown,
        summary.max_drawdown_fraction,
        summary.win_rate,
        summary.profit_factor,
        summary.expectancy,
        summary.trade_count,
        summary.loss_scenario_count,
        summary.drawdown_breach_count,
        summary.risk_violation_count,
        summary.position_inconsistency_count,
        summary.stability_score,
        compute_multi_scenario_robustness_score(summary),
    )


def detect_multi_scenario_failures(
    scenario_results: tuple[ControlledSimulationScenarioResult, ...],
) -> tuple[MultiScenarioFailureFinding, ...]:
    failures: list[MultiScenarioFailureFinding] = []
    for result in scenario_results:
        failures.extend(result.failures)
    return tuple(failures)


def _missing_scenario_risks(scenario_suite: tuple[ControlledSimulationScenarioDefinition, ...]) -> tuple[MultiScenarioControlledSimulationRisk, ...]:
    present = {scenario.scenario_type for scenario in scenario_suite}
    mapping = {
        ControlledSimulationScenarioType.WINNING_SCENARIO: MultiScenarioControlledSimulationRisk.WINNING_SCENARIO_MISSING,
        ControlledSimulationScenarioType.LOSING_SCENARIO: MultiScenarioControlledSimulationRisk.LOSING_SCENARIO_MISSING,
        ControlledSimulationScenarioType.FLAT_SCENARIO: MultiScenarioControlledSimulationRisk.FLAT_SCENARIO_MISSING,
        ControlledSimulationScenarioType.DRAWDOWN_SCENARIO: MultiScenarioControlledSimulationRisk.DRAWDOWN_SCENARIO_MISSING,
        ControlledSimulationScenarioType.VOLATILE_SCENARIO: MultiScenarioControlledSimulationRisk.VOLATILE_SCENARIO_MISSING,
        ControlledSimulationScenarioType.STOP_CONDITION_SCENARIO: MultiScenarioControlledSimulationRisk.STOP_CONDITION_SCENARIO_MISSING,
        ControlledSimulationScenarioType.RISK_VIOLATION_SCENARIO: MultiScenarioControlledSimulationRisk.RISK_VIOLATION_SCENARIO_MISSING,
        ControlledSimulationScenarioType.POSITION_INCONSISTENCY_SCENARIO: MultiScenarioControlledSimulationRisk.POSITION_INCONSISTENCY_SCENARIO_MISSING,
    }
    return tuple(mapping[scenario_type] for scenario_type in _REQUIRED_SCENARIO_TYPES if scenario_type not in present)


def _robustness_findings(
    data: MultiScenarioControlledSimulationInput,
    summary: MultiScenarioMetricSummary,
) -> tuple[MultiScenarioRobustnessFinding, ...]:
    return (
        MultiScenarioRobustnessFinding(
            "metric_aggregation",
            summary.scenario_count > 0 and _finite(summary.total_pnl) and _numeric_or_inf(summary.profit_factor),
            100 if summary.scenario_count > 0 and _finite(summary.total_pnl) and _numeric_or_inf(summary.profit_factor) else 0,
            () if summary.scenario_count > 0 else (MultiScenarioControlledSimulationRisk.METRIC_AGGREGATION_INVALID,),
            (f"scenario_count={summary.scenario_count}",),
        ),
        MultiScenarioRobustnessFinding(
            "robustness_score",
            summary.robustness_score >= data.min_robustness_score,
            summary.robustness_score,
            () if summary.robustness_score >= data.min_robustness_score else (MultiScenarioControlledSimulationRisk.ROBUSTNESS_SCORE_WEAK,),
            (f"robustness_score={summary.robustness_score}", f"minimum={data.min_robustness_score}"),
        ),
        MultiScenarioRobustnessFinding(
            "drawdown",
            summary.max_drawdown_fraction <= data.max_drawdown_fraction,
            _clamp(100 - summary.max_drawdown_fraction * 100),
            () if summary.max_drawdown_fraction <= data.max_drawdown_fraction else (MultiScenarioControlledSimulationRisk.MULTI_SCENARIO_DRAWDOWN_TOO_HIGH,),
            (f"max_drawdown_fraction={summary.max_drawdown_fraction}", f"limit={data.max_drawdown_fraction}"),
        ),
        MultiScenarioRobustnessFinding(
            "loss_limit",
            summary.total_pnl >= -abs(data.max_loss_amount),
            100 if summary.total_pnl >= -abs(data.max_loss_amount) else 0,
            () if summary.total_pnl >= -abs(data.max_loss_amount) else (MultiScenarioControlledSimulationRisk.MULTI_SCENARIO_LOSS_LIMIT_BREACHED,),
            (f"total_pnl={summary.total_pnl}", f"limit={data.max_loss_amount}"),
        ),
        MultiScenarioRobustnessFinding(
            "scenario_execution",
            summary.failed_scenario_count <= data.max_failed_scenarios,
            _clamp(100 - summary.failed_scenario_count * 20),
            () if summary.failed_scenario_count <= data.max_failed_scenarios else (MultiScenarioControlledSimulationRisk.SCENARIO_EXECUTION_FAILED,),
            (f"failed_scenarios={summary.failed_scenario_count}", f"limit={data.max_failed_scenarios}"),
        ),
    )


def detect_multi_scenario_risks(
    data: MultiScenarioControlledSimulationInput | Mapping[str, Any],
    scenario_suite: tuple[ControlledSimulationScenarioDefinition, ...] | None = None,
    scenario_results: tuple[ControlledSimulationScenarioResult, ...] | None = None,
    metric_summary: MultiScenarioMetricSummary | None = None,
) -> tuple[MultiScenarioControlledSimulationRisk, ...]:
    data = _coerce_input(data)
    scenario_suite = build_multi_scenario_suite(data) if scenario_suite is None else tuple(scenario_suite)
    scenario_results = () if scenario_results is None else tuple(scenario_results)
    metric_summary = aggregate_multi_scenario_metrics(scenario_results) if metric_summary is None else metric_summary
    risks: list[MultiScenarioControlledSimulationRisk] = []
    if not validate_performance_risk_validation_gate(data):
        risks.append(MultiScenarioControlledSimulationRisk.PERFORMANCE_RISK_VALIDATION_NOT_APPROVED)
    if not scenario_suite:
        risks.append(MultiScenarioControlledSimulationRisk.SCENARIO_SUITE_EMPTY)
    if any(not _scenario_definition_valid(scenario) for scenario in scenario_suite):
        risks.append(MultiScenarioControlledSimulationRisk.SCENARIO_DEFINITION_INVALID)
    risks.extend(_missing_scenario_risks(scenario_suite))
    if scenario_results and any(not result.passed for result in scenario_results):
        risks.append(MultiScenarioControlledSimulationRisk.SCENARIO_EXECUTION_FAILED)
    if not scenario_results or metric_summary.scenario_count != len(scenario_results) or not _finite(metric_summary.total_pnl):
        risks.append(MultiScenarioControlledSimulationRisk.METRIC_AGGREGATION_INVALID)
    for finding in _robustness_findings(data, metric_summary):
        if not finding.passed:
            risks.extend(finding.risks)
    if not _offline_boundary(data):
        risks.append(MultiScenarioControlledSimulationRisk.REAL_EXECUTION_BOUNDARY_VIOLATION)
    if not _data_boundary(data):
        risks.append(MultiScenarioControlledSimulationRisk.DATA_ACCESS_VIOLATION)
    if data.multi_scenario_result_report_requested is True:
        risks.append(MultiScenarioControlledSimulationRisk.PREMATURE_MULTI_SCENARIO_RESULT_REPORT)
    return _dedupe(risks)


def _build_aggregate_report(
    data: MultiScenarioControlledSimulationInput,
    scenario_results: tuple[ControlledSimulationScenarioResult, ...],
) -> MultiScenarioAggregateReport:
    metric_summary = aggregate_multi_scenario_metrics(scenario_results)
    return MultiScenarioAggregateReport(
        metric_summary,
        scenario_results,
        _robustness_findings(data, metric_summary),
        detect_multi_scenario_failures(scenario_results),
    )


def _compute_score(
    data: MultiScenarioControlledSimulationInput,
    scenario_suite: tuple[ControlledSimulationScenarioDefinition, ...],
    scenario_results: tuple[ControlledSimulationScenarioResult, ...],
    metric_summary: MultiScenarioMetricSummary,
    risks: tuple[MultiScenarioControlledSimulationRisk, ...],
) -> MultiScenarioControlledSimulationScore:
    validation_gate_score = 100 if validate_performance_risk_validation_gate(data) else 0
    missing_count = len(_missing_scenario_risks(scenario_suite))
    scenario_suite_score = 100 if scenario_suite and missing_count == 0 and all(_scenario_definition_valid(s) for s in scenario_suite) else max(0, 70 - missing_count * 10)
    scenario_execution_score = _clamp((metric_summary.passed_scenario_count / metric_summary.scenario_count * 100) if metric_summary.scenario_count else 0)
    metric_aggregation_score = 100 if metric_summary.scenario_count == len(scenario_results) and _finite(metric_summary.total_pnl) else 0
    robustness_score = metric_summary.robustness_score
    risk_control_score = _clamp(100 - metric_summary.drawdown_breach_count * 10 - metric_summary.risk_violation_count * 20 - metric_summary.position_inconsistency_count * 20)
    boundary_score = 100 if _offline_boundary(data) and _data_boundary(data) else 0
    values = (
        validation_gate_score,
        scenario_suite_score,
        scenario_execution_score,
        metric_aggregation_score,
        robustness_score,
        risk_control_score,
        boundary_score,
    )
    overall = _clamp(sum(values) / len(values) - min(80, len(set(risks)) * 4))
    for risk, cap in {
        MultiScenarioControlledSimulationRisk.PERFORMANCE_RISK_VALIDATION_NOT_APPROVED: 50,
        MultiScenarioControlledSimulationRisk.SCENARIO_SUITE_EMPTY: 45,
        MultiScenarioControlledSimulationRisk.SCENARIO_DEFINITION_INVALID: 50,
        MultiScenarioControlledSimulationRisk.SCENARIO_EXECUTION_FAILED: 60,
        MultiScenarioControlledSimulationRisk.METRIC_AGGREGATION_INVALID: 50,
        MultiScenarioControlledSimulationRisk.ROBUSTNESS_SCORE_WEAK: 70,
        MultiScenarioControlledSimulationRisk.MULTI_SCENARIO_DRAWDOWN_TOO_HIGH: 70,
        MultiScenarioControlledSimulationRisk.MULTI_SCENARIO_LOSS_LIMIT_BREACHED: 70,
        MultiScenarioControlledSimulationRisk.REAL_EXECUTION_BOUNDARY_VIOLATION: 35,
        MultiScenarioControlledSimulationRisk.DATA_ACCESS_VIOLATION: 35,
        MultiScenarioControlledSimulationRisk.PREMATURE_MULTI_SCENARIO_RESULT_REPORT: 40,
    }.items():
        if risk in risks:
            overall = min(overall, cap)
    return MultiScenarioControlledSimulationScore(
        overall,
        validation_gate_score,
        scenario_suite_score,
        scenario_execution_score,
        metric_aggregation_score,
        robustness_score,
        risk_control_score,
        boundary_score,
    )


def _select_decision(
    risks: tuple[MultiScenarioControlledSimulationRisk, ...],
) -> MultiScenarioControlledSimulationDecision:
    if (
        MultiScenarioControlledSimulationRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in risks
        or MultiScenarioControlledSimulationRisk.DATA_ACCESS_VIOLATION in risks
        or MultiScenarioControlledSimulationRisk.PREMATURE_MULTI_SCENARIO_RESULT_REPORT in risks
    ):
        return MultiScenarioControlledSimulationDecision.BLOCK_MULTI_SCENARIO_CONTROLLED_SIMULATION
    if MultiScenarioControlledSimulationRisk.PERFORMANCE_RISK_VALIDATION_NOT_APPROVED in risks:
        return MultiScenarioControlledSimulationDecision.REQUIRE_PERFORMANCE_RISK_VALIDATION_FIXES
    if (
        MultiScenarioControlledSimulationRisk.SCENARIO_SUITE_EMPTY in risks
        or MultiScenarioControlledSimulationRisk.SCENARIO_DEFINITION_INVALID in risks
        or any("MISSING" in risk.value for risk in risks)
    ):
        return MultiScenarioControlledSimulationDecision.REQUIRE_SCENARIO_SUITE_FIXES
    if MultiScenarioControlledSimulationRisk.SCENARIO_EXECUTION_FAILED in risks:
        return MultiScenarioControlledSimulationDecision.REQUIRE_SCENARIO_EXECUTION_FIXES
    if MultiScenarioControlledSimulationRisk.METRIC_AGGREGATION_INVALID in risks:
        return MultiScenarioControlledSimulationDecision.REQUIRE_METRIC_AGGREGATION_FIXES
    if MultiScenarioControlledSimulationRisk.ROBUSTNESS_SCORE_WEAK in risks:
        return MultiScenarioControlledSimulationDecision.REQUIRE_ROBUSTNESS_FIXES
    if (
        MultiScenarioControlledSimulationRisk.MULTI_SCENARIO_DRAWDOWN_TOO_HIGH in risks
        or MultiScenarioControlledSimulationRisk.MULTI_SCENARIO_LOSS_LIMIT_BREACHED in risks
    ):
        return MultiScenarioControlledSimulationDecision.REQUIRE_RISK_REDUCTION
    return MultiScenarioControlledSimulationDecision.APPROVE_MULTI_SCENARIO_CONTROLLED_SIMULATION


def _select_state(
    decision: MultiScenarioControlledSimulationDecision,
    risks: tuple[MultiScenarioControlledSimulationRisk, ...],
    score: int,
) -> MultiScenarioControlledSimulationState:
    if decision == MultiScenarioControlledSimulationDecision.BLOCK_MULTI_SCENARIO_CONTROLLED_SIMULATION:
        return MultiScenarioControlledSimulationState.MULTI_SCENARIO_BLOCKED
    if decision in {
        MultiScenarioControlledSimulationDecision.REQUIRE_PERFORMANCE_RISK_VALIDATION_FIXES,
        MultiScenarioControlledSimulationDecision.REQUIRE_SCENARIO_SUITE_FIXES,
    }:
        return MultiScenarioControlledSimulationState.INPUT_INVALID
    if risks:
        return MultiScenarioControlledSimulationState.MULTI_SCENARIO_COMPLETED_WITH_WARNINGS
    if score >= 80:
        return MultiScenarioControlledSimulationState.READY_FOR_MULTI_SCENARIO_RESULT_REPORT
    return MultiScenarioControlledSimulationState.MULTI_SCENARIO_COMPLETED


def generate_multi_scenario_recommendations(
    risks: tuple[MultiScenarioControlledSimulationRisk, ...],
    decision: MultiScenarioControlledSimulationDecision | None = None,
) -> tuple[MultiScenarioControlledSimulationRecommendation, ...]:
    recommendations: list[MultiScenarioControlledSimulationRecommendation] = []
    if risks:
        recommendations.append(MultiScenarioControlledSimulationRecommendation.HOLD_MULTI_SCENARIO_RESULT_REPORT)
    mapping = {
        MultiScenarioControlledSimulationRisk.PERFORMANCE_RISK_VALIDATION_NOT_APPROVED: MultiScenarioControlledSimulationRecommendation.APPROVE_PERFORMANCE_RISK_VALIDATION_FIRST,
        MultiScenarioControlledSimulationRisk.SCENARIO_SUITE_EMPTY: MultiScenarioControlledSimulationRecommendation.PROVIDE_SCENARIO_SUITE,
        MultiScenarioControlledSimulationRisk.SCENARIO_DEFINITION_INVALID: MultiScenarioControlledSimulationRecommendation.FIX_SCENARIO_DEFINITIONS,
        MultiScenarioControlledSimulationRisk.WINNING_SCENARIO_MISSING: MultiScenarioControlledSimulationRecommendation.ADD_WINNING_SCENARIO,
        MultiScenarioControlledSimulationRisk.LOSING_SCENARIO_MISSING: MultiScenarioControlledSimulationRecommendation.ADD_LOSING_SCENARIO,
        MultiScenarioControlledSimulationRisk.FLAT_SCENARIO_MISSING: MultiScenarioControlledSimulationRecommendation.ADD_FLAT_SCENARIO,
        MultiScenarioControlledSimulationRisk.DRAWDOWN_SCENARIO_MISSING: MultiScenarioControlledSimulationRecommendation.ADD_DRAWDOWN_SCENARIO,
        MultiScenarioControlledSimulationRisk.VOLATILE_SCENARIO_MISSING: MultiScenarioControlledSimulationRecommendation.ADD_VOLATILE_SCENARIO,
        MultiScenarioControlledSimulationRisk.STOP_CONDITION_SCENARIO_MISSING: MultiScenarioControlledSimulationRecommendation.ADD_STOP_CONDITION_SCENARIO,
        MultiScenarioControlledSimulationRisk.RISK_VIOLATION_SCENARIO_MISSING: MultiScenarioControlledSimulationRecommendation.ADD_RISK_VIOLATION_SCENARIO,
        MultiScenarioControlledSimulationRisk.POSITION_INCONSISTENCY_SCENARIO_MISSING: MultiScenarioControlledSimulationRecommendation.ADD_POSITION_INCONSISTENCY_SCENARIO,
        MultiScenarioControlledSimulationRisk.SCENARIO_EXECUTION_FAILED: MultiScenarioControlledSimulationRecommendation.FIX_SCENARIO_EXECUTION,
        MultiScenarioControlledSimulationRisk.METRIC_AGGREGATION_INVALID: MultiScenarioControlledSimulationRecommendation.REBUILD_METRIC_AGGREGATION,
        MultiScenarioControlledSimulationRisk.ROBUSTNESS_SCORE_WEAK: MultiScenarioControlledSimulationRecommendation.IMPROVE_MULTI_SCENARIO_ROBUSTNESS,
        MultiScenarioControlledSimulationRisk.MULTI_SCENARIO_DRAWDOWN_TOO_HIGH: MultiScenarioControlledSimulationRecommendation.REDUCE_MULTI_SCENARIO_DRAWDOWN,
        MultiScenarioControlledSimulationRisk.MULTI_SCENARIO_LOSS_LIMIT_BREACHED: MultiScenarioControlledSimulationRecommendation.REDUCE_MULTI_SCENARIO_LOSS,
        MultiScenarioControlledSimulationRisk.REAL_EXECUTION_BOUNDARY_VIOLATION: MultiScenarioControlledSimulationRecommendation.RESTORE_REAL_EXECUTION_BOUNDARIES,
        MultiScenarioControlledSimulationRisk.DATA_ACCESS_VIOLATION: MultiScenarioControlledSimulationRecommendation.REMOVE_DATA_ACCESS,
        MultiScenarioControlledSimulationRisk.PREMATURE_MULTI_SCENARIO_RESULT_REPORT: MultiScenarioControlledSimulationRecommendation.DELAY_MULTI_SCENARIO_RESULT_REPORT,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(MultiScenarioControlledSimulationRecommendation.RUN_MULTI_SCENARIO_CONTROLLED_SIMULATION_SUITE)
    if decision == MultiScenarioControlledSimulationDecision.APPROVE_MULTI_SCENARIO_CONTROLLED_SIMULATION:
        recommendations.append(MultiScenarioControlledSimulationRecommendation.APPROVE_MULTI_SCENARIO_RESULT_REPORT)
    return _dedupe(recommendations)


def run_multi_scenario_controlled_simulation(
    data: MultiScenarioControlledSimulationInput | Mapping[str, Any],
) -> MultiScenarioControlledSimulationResult:
    data = _coerce_input(data)
    scenario_suite = build_multi_scenario_suite(data)
    if validate_performance_risk_validation_gate(data) and scenario_suite and all(_scenario_definition_valid(item) for item in scenario_suite):
        scenario_results = tuple(execute_controlled_simulation_scenario(item, data) for item in scenario_suite)
    else:
        scenario_results = ()
    aggregate_report = _build_aggregate_report(data, scenario_results)
    metric_summary = aggregate_report.metric_summary
    risks = detect_multi_scenario_risks(data, scenario_suite, scenario_results, metric_summary)
    score = _compute_score(data, scenario_suite, scenario_results, metric_summary, risks)
    decision = _select_decision(risks)
    state = _select_state(decision, risks, score.overall_score)
    recommendations = generate_multi_scenario_recommendations(risks, decision)
    offline_only = _offline_boundary(data) and _data_boundary(data)
    summary = (
        f"{state.value}: decision={decision.value}, score={score.overall_score}, "
        f"risks={len(risks)}, scenarios={metric_summary.scenario_count}, pnl={metric_summary.total_pnl}"
    )
    return MultiScenarioControlledSimulationResult(
        state,
        decision,
        score.overall_score,
        score,
        risks,
        recommendations,
        scenario_suite,
        scenario_results,
        aggregate_report,
        metric_summary,
        aggregate_report.failure_findings,
        aggregate_report.robustness_findings,
        offline_only,
        summary,
    )


def render_multi_scenario_controlled_simulation_markdown(result: MultiScenarioControlledSimulationResult) -> str:
    risks = "\n".join(f"- {risk.value}" for risk in result.risks) or "- None"
    recommendations = "\n".join(f"- {item.value}" for item in result.recommendations) or "- None"
    scenarios = "\n".join(
        f"- {item.scenario_id} ({item.scenario_type.value}): {'PASS' if item.passed else 'FAIL'}, pnl={item.pnl}, dd={item.max_drawdown_fraction}"
        for item in result.scenario_results
    ) or "- None"
    failures = "\n".join(f"- {item.scenario_id}: {item.failure}" for item in result.failures) or "- None"
    metrics = result.metric_summary
    return "\n".join(
        (
            "# AGIcore Multi-Scenario Controlled Simulation",
            "",
            f"State: {result.state.value}",
            f"Decision: {result.decision.value}",
            f"Score: {result.simulation_score}",
            f"Offline only: {result.offline_only}",
            "",
            "## Aggregate Metrics",
            f"Scenario count: {metrics.scenario_count}",
            f"Passed scenarios: {metrics.passed_scenario_count}",
            f"Failed scenarios: {metrics.failed_scenario_count}",
            f"Total PnL: {metrics.total_pnl}",
            f"Average PnL: {metrics.average_pnl}",
            f"Max drawdown fraction: {metrics.max_drawdown_fraction}",
            f"Win rate: {metrics.win_rate}",
            f"Profit factor: {metrics.profit_factor}",
            f"Expectancy: {metrics.expectancy}",
            f"Stability score: {metrics.stability_score}",
            f"Robustness score: {metrics.robustness_score}",
            "",
            "## Scenarios",
            scenarios,
            "",
            "## Failures",
            failures,
            "",
            "## Risks",
            risks,
            "",
            "## Recommendations",
            recommendations,
        )
    )


__all__ = [
    "run_multi_scenario_controlled_simulation",
    "validate_performance_risk_validation_gate",
    "build_multi_scenario_suite",
    "build_winning_scenario",
    "build_losing_scenario",
    "build_flat_scenario",
    "build_drawdown_scenario",
    "build_volatile_scenario",
    "build_stop_condition_scenario",
    "build_risk_violation_scenario",
    "build_position_inconsistency_scenario",
    "execute_controlled_simulation_scenario",
    "aggregate_multi_scenario_metrics",
    "compute_multi_scenario_pnl",
    "compute_multi_scenario_drawdown",
    "compute_multi_scenario_win_rate",
    "compute_multi_scenario_profit_factor",
    "compute_multi_scenario_expectancy",
    "compute_multi_scenario_stability_score",
    "compute_multi_scenario_robustness_score",
    "detect_multi_scenario_risks",
    "detect_multi_scenario_failures",
    "generate_multi_scenario_recommendations",
    "render_multi_scenario_controlled_simulation_markdown",
]
