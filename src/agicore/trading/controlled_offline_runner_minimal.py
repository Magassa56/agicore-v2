"""Minimal deterministic controlled offline runner for AGIcore Trading."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from math import isfinite
from typing import Any, Iterable, Mapping

from agicore.trading.controlled_offline_runner_minimal_models import (
    ControlledOfflineJournalEntry,
    ControlledOfflineReadOnlyDecision,
    ControlledOfflineRiskGuardResult,
    ControlledOfflineRunnerMetrics,
    ControlledOfflineRunnerMinimalDecision,
    ControlledOfflineRunnerMinimalInput,
    ControlledOfflineRunnerMinimalRecommendation,
    ControlledOfflineRunnerMinimalResult,
    ControlledOfflineRunnerMinimalRisk,
    ControlledOfflineRunnerMinimalScore,
    ControlledOfflineRunnerMinimalState,
    ControlledOfflineRunnerReport,
    ControlledOfflineSimulatedAccountSnapshot,
    ControlledOfflineSimulatedBrokerSnapshot,
    ControlledOfflineStrategySignal,
    ControlledOfflineSyntheticMarketBar,
    ControlledOfflineSyntheticMarketScenario,
)


Risk = ControlledOfflineRunnerMinimalRisk
Recommendation = ControlledOfflineRunnerMinimalRecommendation
Decision = ControlledOfflineRunnerMinimalDecision
State = ControlledOfflineRunnerMinimalState


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


def _coerce_input(data: ControlledOfflineRunnerMinimalInput | Mapping[str, Any] | None) -> ControlledOfflineRunnerMinimalInput | None:
    if data is None:
        return None
    if isinstance(data, ControlledOfflineRunnerMinimalInput):
        return data
    allowed = {field.name for field in fields(ControlledOfflineRunnerMinimalInput)}
    return ControlledOfflineRunnerMinimalInput(**{key: value for key, value in dict(data).items() if key in allowed})


def _finite_number(value: Any) -> bool:
    return isinstance(value, int | float) and isfinite(float(value))


def _coerce_bar(item: ControlledOfflineSyntheticMarketBar | Mapping[str, Any], index: int, symbol: str) -> ControlledOfflineSyntheticMarketBar:
    if isinstance(item, ControlledOfflineSyntheticMarketBar):
        return item
    payload = dict(item)
    close = float(payload.get("close", payload.get("price", 0.0)))
    open_price = float(payload.get("open", close))
    return ControlledOfflineSyntheticMarketBar(
        step=int(payload.get("step", index)),
        symbol=str(payload.get("symbol", symbol)),
        open=open_price,
        high=float(payload.get("high", max(open_price, close))),
        low=float(payload.get("low", min(open_price, close))),
        close=close,
        volume=float(payload.get("volume", 0.0)),
        timestamp=str(payload.get("timestamp", f"T{index}")),
    )


def _default_bars(symbol: str) -> tuple[ControlledOfflineSyntheticMarketBar, ...]:
    closes = (100.0, 102.0, 101.0, 105.0)
    bars: list[ControlledOfflineSyntheticMarketBar] = []
    previous = closes[0]
    for step, close in enumerate(closes):
        open_price = previous if step else close
        bars.append(
            ControlledOfflineSyntheticMarketBar(
                step=step,
                symbol=symbol,
                open=open_price,
                high=max(open_price, close) + 1.0,
                low=min(open_price, close) - 1.0,
                close=close,
                volume=1000.0,
                timestamp=f"T{step}",
            )
        )
        previous = close
    return tuple(bars)


def _valid_bar(bar: ControlledOfflineSyntheticMarketBar) -> bool:
    prices = (bar.open, bar.high, bar.low, bar.close)
    return (
        isinstance(bar.step, int)
        and bool(bar.symbol)
        and all(_finite_number(price) and float(price) > 0 for price in prices)
        and _finite_number(bar.volume)
        and bar.volume >= 0
        and bar.high >= max(bar.open, bar.close)
        and bar.low <= min(bar.open, bar.close)
    )


def _valid_scenario(scenario: ControlledOfflineSyntheticMarketScenario | None) -> bool:
    return (
        scenario is not None
        and bool(scenario.scenario_id)
        and bool(scenario.symbol)
        and bool(scenario.bars)
        and all(_valid_bar(bar) for bar in scenario.bars)
    )


def _valid_account(snapshot: ControlledOfflineSimulatedAccountSnapshot | None) -> bool:
    return (
        snapshot is not None
        and bool(snapshot.account_id)
        and _finite_number(snapshot.cash)
        and _finite_number(snapshot.equity)
        and snapshot.cash >= 0
        and snapshot.equity >= 0
        and snapshot.simulated is True
        and snapshot.read_only is True
    )


def _valid_broker(snapshot: ControlledOfflineSimulatedBrokerSnapshot | None) -> bool:
    return (
        snapshot is not None
        and bool(snapshot.broker_id)
        and snapshot.connected is False
        and snapshot.simulated is True
        and snapshot.read_only is True
        and snapshot.orders_supported is False
        and snapshot.real_broker is False
    )


def _valid_signal(signal: ControlledOfflineStrategySignal | None) -> bool:
    return (
        signal is not None
        and signal.action in {"BUY", "SELL", "HOLD"}
        and 0.0 <= signal.confidence <= 1.0
        and bool(signal.symbol)
        and signal.observation_only is True
    )


def validate_controlled_offline_runner_minimal_input(data: ControlledOfflineRunnerMinimalInput | Mapping[str, Any] | None) -> bool:
    data = _coerce_input(data)
    return (
        data is not None
        and bool(data.scenario_id)
        and bool(data.symbol)
        and _finite_number(data.initial_cash)
        and data.initial_cash > 0
        and _finite_number(data.max_position_size)
        and data.max_position_size >= 0
        and _finite_number(data.risk_fraction)
        and 0 <= data.risk_fraction <= 1
        and data.offline_mode_enforced is True
        and data.sandbox_mode_enforced is True
        and data.in_memory_only is True
        and data.synthetic_data_only is True
    )


def build_controlled_offline_synthetic_market_scenario(data: ControlledOfflineRunnerMinimalInput | Mapping[str, Any] | None) -> ControlledOfflineSyntheticMarketScenario:
    data = _coerce_input(data) or ControlledOfflineRunnerMinimalInput()
    raw_bars = data.synthetic_market_bars if data.synthetic_market_bars is not None else _default_bars(data.symbol)
    bars = tuple(_coerce_bar(item, index, data.symbol) for index, item in enumerate(raw_bars))
    return ControlledOfflineSyntheticMarketScenario(
        scenario_id=data.scenario_id,
        symbol=data.symbol,
        bars=bars,
        deterministic=True,
        in_memory_only=True,
    )


def build_controlled_offline_simulated_account_snapshot(data: ControlledOfflineRunnerMinimalInput | Mapping[str, Any] | None) -> ControlledOfflineSimulatedAccountSnapshot:
    data = _coerce_input(data) or ControlledOfflineRunnerMinimalInput()
    if isinstance(data.account_snapshot, ControlledOfflineSimulatedAccountSnapshot):
        return data.account_snapshot
    if isinstance(data.account_snapshot, Mapping):
        payload = dict(data.account_snapshot)
        return ControlledOfflineSimulatedAccountSnapshot(
            account_id=str(payload.get("account_id", "SIM-ACCOUNT")),
            cash=float(payload.get("cash", data.initial_cash)),
            equity=float(payload.get("equity", payload.get("cash", data.initial_cash))),
            currency=str(payload.get("currency", "USD")),
            simulated=bool(payload.get("simulated", True)),
            read_only=bool(payload.get("read_only", True)),
        )
    return ControlledOfflineSimulatedAccountSnapshot("SIM-ACCOUNT", data.initial_cash, data.initial_cash)


def build_controlled_offline_simulated_broker_snapshot(data: ControlledOfflineRunnerMinimalInput | Mapping[str, Any] | None) -> ControlledOfflineSimulatedBrokerSnapshot:
    data = _coerce_input(data) or ControlledOfflineRunnerMinimalInput()
    if isinstance(data.broker_snapshot, ControlledOfflineSimulatedBrokerSnapshot):
        return data.broker_snapshot
    if isinstance(data.broker_snapshot, Mapping):
        payload = dict(data.broker_snapshot)
        return ControlledOfflineSimulatedBrokerSnapshot(
            broker_id=str(payload.get("broker_id", "SIM-BROKER")),
            connected=bool(payload.get("connected", False)),
            simulated=bool(payload.get("simulated", True)),
            read_only=bool(payload.get("read_only", True)),
            orders_supported=bool(payload.get("orders_supported", False)),
            real_broker=bool(payload.get("real_broker", False)),
        )
    return ControlledOfflineSimulatedBrokerSnapshot("SIM-BROKER", connected=False)


def evaluate_controlled_offline_strategy_signal(
    scenario: ControlledOfflineSyntheticMarketScenario,
    data: ControlledOfflineRunnerMinimalInput | Mapping[str, Any] | None = None,
) -> ControlledOfflineStrategySignal:
    data = _coerce_input(data) or ControlledOfflineRunnerMinimalInput()
    if data.force_strategy_signal_invalid:
        return ControlledOfflineStrategySignal(scenario.symbol, "EXECUTE", 1.5, "forced invalid", False)
    if not scenario.bars:
        return ControlledOfflineStrategySignal(scenario.symbol, "HOLD", 0.0, "empty scenario")
    start = scenario.bars[0].close
    end = scenario.bars[-1].close
    if end > start:
        return ControlledOfflineStrategySignal(scenario.symbol, "BUY", 0.75, "synthetic upward drift")
    if end < start:
        return ControlledOfflineStrategySignal(scenario.symbol, "SELL", 0.75, "synthetic downward drift")
    return ControlledOfflineStrategySignal(scenario.symbol, "HOLD", 0.5, "flat synthetic path")


def compute_controlled_offline_position_size(
    account: ControlledOfflineSimulatedAccountSnapshot,
    signal: ControlledOfflineStrategySignal,
    scenario: ControlledOfflineSyntheticMarketScenario,
    data: ControlledOfflineRunnerMinimalInput | Mapping[str, Any] | None = None,
) -> float:
    data = _coerce_input(data) or ControlledOfflineRunnerMinimalInput()
    if signal.action == "HOLD" or not scenario.bars:
        return 0.0
    reference_price = scenario.bars[-1].close
    budget = account.equity * data.risk_fraction
    raw_size = budget / reference_price if reference_price > 0 else 0.0
    return round(min(max(raw_size, 0.0), data.max_position_size), 10)


def apply_controlled_offline_risk_guards(
    data: ControlledOfflineRunnerMinimalInput | Mapping[str, Any] | None,
    account: ControlledOfflineSimulatedAccountSnapshot,
    broker: ControlledOfflineSimulatedBrokerSnapshot,
    signal: ControlledOfflineStrategySignal,
    position_size: float,
) -> ControlledOfflineRiskGuardResult:
    data = _coerce_input(data) or ControlledOfflineRunnerMinimalInput()
    risks: list[Risk] = []
    reasons: list[str] = []
    if data.force_risk_guard_failed:
        risks.append(Risk.CONTROLLED_OFFLINE_RISK_GUARD_FAILED)
        reasons.append("forced risk guard failure")
    if not _valid_account(account):
        risks.append(Risk.CONTROLLED_OFFLINE_ACCOUNT_SNAPSHOT_INVALID)
        reasons.append("invalid simulated account snapshot")
    if not _valid_broker(broker):
        risks.append(Risk.CONTROLLED_OFFLINE_BROKER_SNAPSHOT_INVALID)
        reasons.append("invalid simulated broker snapshot")
    if not _valid_signal(signal):
        risks.append(Risk.CONTROLLED_OFFLINE_STRATEGY_SIGNAL_INVALID)
        reasons.append("invalid observation-only signal")
    if position_size > data.max_position_size:
        risks.append(Risk.CONTROLLED_OFFLINE_RISK_GUARD_FAILED)
        reasons.append("position size exceeds configured maximum")
    if signal.action != "HOLD" and position_size <= 0:
        risks.append(Risk.CONTROLLED_OFFLINE_RISK_GUARD_FAILED)
        reasons.append("non-hold signal has no simulated size")
    return ControlledOfflineRiskGuardResult(
        passed=not risks,
        max_position_size=data.max_position_size,
        proposed_position_size=position_size,
        risks=_dedupe(risks),
        reasons=tuple(reasons),
    )


def simulate_controlled_offline_read_only_decision(
    scenario: ControlledOfflineSyntheticMarketScenario,
    signal: ControlledOfflineStrategySignal,
    risk_guard: ControlledOfflineRiskGuardResult,
) -> ControlledOfflineReadOnlyDecision:
    reference_price = scenario.bars[-1].close if scenario.bars else 0.0
    action = signal.action if risk_guard.passed else "HOLD"
    size = risk_guard.proposed_position_size if risk_guard.passed else 0.0
    return ControlledOfflineReadOnlyDecision(
        symbol=signal.symbol,
        action=action,
        proposed_position_size=size,
        reference_price=reference_price,
        order_submitted=False,
        position_mutated=False,
        read_only=True,
        reason="read-only simulated decision; no order submitted",
    )


def write_controlled_offline_journal_entries(
    scenario: ControlledOfflineSyntheticMarketScenario,
    account: ControlledOfflineSimulatedAccountSnapshot,
    broker: ControlledOfflineSimulatedBrokerSnapshot,
    signal: ControlledOfflineStrategySignal,
    risk_guard: ControlledOfflineRiskGuardResult,
    decision: ControlledOfflineReadOnlyDecision,
    data: ControlledOfflineRunnerMinimalInput | Mapping[str, Any] | None = None,
) -> tuple[ControlledOfflineJournalEntry, ...]:
    data = _coerce_input(data) or ControlledOfflineRunnerMinimalInput()
    if data.force_journal_missing:
        return ()
    return (
        ControlledOfflineJournalEntry(0, "scenario_built", "synthetic in-memory scenario built", {"bars": len(scenario.bars)}),
        ControlledOfflineJournalEntry(1, "snapshot_built", "simulated read-only snapshots built", {"account": account.account_id, "broker": broker.broker_id}),
        ControlledOfflineJournalEntry(2, "signal_observed", "strategy signal observed", {"action": signal.action, "confidence": signal.confidence}),
        ControlledOfflineJournalEntry(3, "risk_guard_checked", "offline risk guards checked", {"passed": risk_guard.passed}),
        ControlledOfflineJournalEntry(4, "read_only_decision", "read-only decision recorded", {"action": decision.action, "order_submitted": decision.order_submitted}),
    )


def compute_controlled_offline_runner_metrics(
    scenario: ControlledOfflineSyntheticMarketScenario,
    decision: ControlledOfflineReadOnlyDecision,
    data: ControlledOfflineRunnerMinimalInput | Mapping[str, Any] | None = None,
) -> ControlledOfflineRunnerMetrics | None:
    data = _coerce_input(data) or ControlledOfflineRunnerMinimalInput()
    if data.force_metrics_missing or not scenario.bars:
        return None
    start = scenario.bars[0].close
    end = scenario.bars[-1].close
    change = round(end - start, 10)
    return ControlledOfflineRunnerMetrics(
        bar_count=len(scenario.bars),
        start_price=start,
        end_price=end,
        price_change=change,
        price_change_fraction=round(change / start, 10) if start else 0.0,
        proposed_position_size=decision.proposed_position_size,
        order_count=0,
        real_order_count=0,
        account_access_count=0,
        data_access_count=0,
    )


def assert_controlled_offline_runner_no_real_execution_boundaries(data: ControlledOfflineRunnerMinimalInput | Mapping[str, Any] | None) -> bool:
    data = _coerce_input(data)
    return (
        data is not None
        and data.offline_mode_enforced is True
        and data.sandbox_mode_enforced is True
        and data.in_memory_only is True
        and data.synthetic_data_only is True
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
        and data.no_data_access is True
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
        and data.data_access_requested is False
    )


def detect_controlled_offline_runner_risks(
    data: ControlledOfflineRunnerMinimalInput | Mapping[str, Any] | None,
    scenario: ControlledOfflineSyntheticMarketScenario | None = None,
    account: ControlledOfflineSimulatedAccountSnapshot | None = None,
    broker: ControlledOfflineSimulatedBrokerSnapshot | None = None,
    signal: ControlledOfflineStrategySignal | None = None,
    risk_guard: ControlledOfflineRiskGuardResult | None = None,
    journal_entries: tuple[ControlledOfflineJournalEntry, ...] = (),
    metrics: ControlledOfflineRunnerMetrics | None = None,
) -> tuple[Risk, ...]:
    data = _coerce_input(data)
    risks: list[Risk] = []
    if data is None or not validate_controlled_offline_runner_minimal_input(data):
        risks.append(Risk.CONTROLLED_OFFLINE_RUNNER_INPUT_MISSING)
    if scenario is None or not scenario.bars:
        risks.append(Risk.CONTROLLED_OFFLINE_MARKET_SCENARIO_EMPTY)
    elif not _valid_scenario(scenario):
        risks.append(Risk.CONTROLLED_OFFLINE_MARKET_SCENARIO_INVALID)
    if account is not None and not _valid_account(account):
        risks.append(Risk.CONTROLLED_OFFLINE_ACCOUNT_SNAPSHOT_INVALID)
    if broker is not None and not _valid_broker(broker):
        risks.append(Risk.CONTROLLED_OFFLINE_BROKER_SNAPSHOT_INVALID)
    if signal is not None and not _valid_signal(signal):
        risks.append(Risk.CONTROLLED_OFFLINE_STRATEGY_SIGNAL_INVALID)
    if risk_guard is not None and not risk_guard.passed:
        risks.extend(risk_guard.risks or (Risk.CONTROLLED_OFFLINE_RISK_GUARD_FAILED,))
    if not journal_entries:
        risks.append(Risk.CONTROLLED_OFFLINE_JOURNAL_MISSING)
    if metrics is None:
        risks.append(Risk.CONTROLLED_OFFLINE_METRICS_MISSING)
    if data is not None:
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
        if data.no_data_access is not True or data.data_access_requested:
            risks.append(Risk.DATA_ACCESS_BOUNDARY_VIOLATION)
    return _dedupe(risks)


def _score(flag: bool) -> int:
    return 100 if flag else 0


def _build_score(data, scenario, account, broker, signal, risk_guard, journal_entries, metrics, risks) -> ControlledOfflineRunnerMinimalScore:
    boundary_ok = data is not None and assert_controlled_offline_runner_no_real_execution_boundaries(data)
    parts = {
        "input_score": _score(data is not None and validate_controlled_offline_runner_minimal_input(data)),
        "scenario_score": _score(_valid_scenario(scenario)),
        "account_score": _score(_valid_account(account)),
        "broker_score": _score(_valid_broker(broker)),
        "signal_score": _score(_valid_signal(signal)),
        "risk_guard_score": _score(risk_guard is not None and risk_guard.passed),
        "journal_score": _score(bool(journal_entries)),
        "metrics_score": _score(metrics is not None),
        "boundary_score": _score(boundary_ok),
    }
    overall = 100 if not risks and all(value == 100 for value in parts.values()) else round(sum(parts.values()) / len(parts))
    return ControlledOfflineRunnerMinimalScore(overall_score=overall, **parts)


def generate_controlled_offline_runner_recommendations(
    data: ControlledOfflineRunnerMinimalInput | Mapping[str, Any] | None,
    risks: Iterable[Risk] | None = None,
) -> tuple[Recommendation, ...]:
    risks = tuple(risks or ())
    if not risks:
        return (
            Recommendation.RUN_CONTROLLED_OFFLINE_RUNNER_MINIMAL_TEST_SUITE,
            Recommendation.APPROVE_CONTROLLED_OFFLINE_RUNNER_MINIMAL_REVIEW,
        )
    mapping = {
        Risk.CONTROLLED_OFFLINE_RUNNER_INPUT_MISSING: Recommendation.PROVIDE_CONTROLLED_OFFLINE_RUNNER_INPUT,
        Risk.CONTROLLED_OFFLINE_MARKET_SCENARIO_EMPTY: Recommendation.PROVIDE_SYNTHETIC_MARKET_SCENARIO,
        Risk.CONTROLLED_OFFLINE_MARKET_SCENARIO_INVALID: Recommendation.FIX_SYNTHETIC_MARKET_SCENARIO,
        Risk.CONTROLLED_OFFLINE_ACCOUNT_SNAPSHOT_INVALID: Recommendation.FIX_SIMULATED_ACCOUNT_SNAPSHOT,
        Risk.CONTROLLED_OFFLINE_BROKER_SNAPSHOT_INVALID: Recommendation.FIX_SIMULATED_BROKER_SNAPSHOT,
        Risk.CONTROLLED_OFFLINE_STRATEGY_SIGNAL_INVALID: Recommendation.FIX_STRATEGY_SIGNAL,
        Risk.CONTROLLED_OFFLINE_RISK_GUARD_FAILED: Recommendation.FIX_RISK_GUARDS,
        Risk.CONTROLLED_OFFLINE_JOURNAL_MISSING: Recommendation.WRITE_IN_MEMORY_JOURNAL,
        Risk.CONTROLLED_OFFLINE_METRICS_MISSING: Recommendation.COMPUTE_MINIMAL_METRICS,
        Risk.REAL_BROKER_BOUNDARY_VIOLATION: Recommendation.RESTORE_OFFLINE_BOUNDARIES,
        Risk.REAL_SECRET_BOUNDARY_VIOLATION: Recommendation.REMOVE_REAL_SECRET_ACCESS,
        Risk.NETWORK_BOUNDARY_VIOLATION: Recommendation.REMOVE_NETWORK_ACCESS,
        Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION: Recommendation.KEEP_DECISION_READ_ONLY,
        Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION: Recommendation.REMOVE_ACCOUNT_ACCESS,
        Risk.DATA_ACCESS_BOUNDARY_VIOLATION: Recommendation.REMOVE_DATA_ACCESS,
    }
    return _dedupe(mapping[risk] for risk in risks if risk in mapping)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_CONTROLLED_OFFLINE_RUNNER_MINIMAL
    boundary_risks = {
        Risk.REAL_BROKER_BOUNDARY_VIOLATION,
        Risk.REAL_SECRET_BOUNDARY_VIOLATION,
        Risk.NETWORK_BOUNDARY_VIOLATION,
        Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION,
        Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION,
        Risk.DATA_ACCESS_BOUNDARY_VIOLATION,
    }
    if any(risk in boundary_risks for risk in risks):
        return Decision.BLOCK_CONTROLLED_OFFLINE_RUNNER_MINIMAL
    if Risk.CONTROLLED_OFFLINE_RUNNER_INPUT_MISSING in risks:
        return Decision.REQUIRE_CONTROLLED_OFFLINE_RUNNER_INPUT_FIXES
    if Risk.CONTROLLED_OFFLINE_MARKET_SCENARIO_EMPTY in risks or Risk.CONTROLLED_OFFLINE_MARKET_SCENARIO_INVALID in risks:
        return Decision.REQUIRE_CONTROLLED_OFFLINE_MARKET_SCENARIO_FIXES
    if Risk.CONTROLLED_OFFLINE_ACCOUNT_SNAPSHOT_INVALID in risks:
        return Decision.REQUIRE_CONTROLLED_OFFLINE_ACCOUNT_SNAPSHOT_FIXES
    if Risk.CONTROLLED_OFFLINE_BROKER_SNAPSHOT_INVALID in risks:
        return Decision.REQUIRE_CONTROLLED_OFFLINE_BROKER_SNAPSHOT_FIXES
    if Risk.CONTROLLED_OFFLINE_RISK_GUARD_FAILED in risks or Risk.CONTROLLED_OFFLINE_STRATEGY_SIGNAL_INVALID in risks:
        return Decision.REQUIRE_CONTROLLED_OFFLINE_RISK_GUARD_FIXES
    if Risk.CONTROLLED_OFFLINE_JOURNAL_MISSING in risks:
        return Decision.REQUIRE_CONTROLLED_OFFLINE_JOURNAL_FIXES
    if Risk.CONTROLLED_OFFLINE_METRICS_MISSING in risks:
        return Decision.REQUIRE_CONTROLLED_OFFLINE_METRICS_FIXES
    return Decision.BLOCK_CONTROLLED_OFFLINE_RUNNER_MINIMAL


def _state_for(risks: tuple[Risk, ...], score: ControlledOfflineRunnerMinimalScore) -> State:
    if Risk.CONTROLLED_OFFLINE_RUNNER_INPUT_MISSING in risks:
        return State.CONTROLLED_OFFLINE_RUNNER_INPUT_INVALID
    boundary_risks = {
        Risk.REAL_BROKER_BOUNDARY_VIOLATION,
        Risk.REAL_SECRET_BOUNDARY_VIOLATION,
        Risk.NETWORK_BOUNDARY_VIOLATION,
        Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION,
        Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION,
        Risk.DATA_ACCESS_BOUNDARY_VIOLATION,
    }
    if any(risk in boundary_risks for risk in risks):
        return State.CONTROLLED_OFFLINE_RUNNER_BLOCKED
    if not risks and score.overall_score == 100:
        return State.READY_FOR_CONTROLLED_OFFLINE_RUNNER_MINIMAL_REVIEW
    if risks:
        return State.CONTROLLED_OFFLINE_RUNNER_BLOCKED
    if score.overall_score >= 70:
        return State.CONTROLLED_OFFLINE_RUNNER_COMPLETED_WITH_WARNINGS
    return State.NOT_READY


def render_controlled_offline_runner_markdown_report(result: ControlledOfflineRunnerMinimalResult) -> str:
    risks = ", ".join(_value(risk) for risk in result.risks) or "none"
    recs = ", ".join(_value(rec) for rec in result.recommendations) or "none"
    return "\n".join(
        (
            "# Controlled Offline Runner Minimal Report",
            f"- State: {result.state.value}",
            f"- Decision: {result.decision.value}",
            f"- Score: {result.score.overall_score}",
            f"- Risks: {risks}",
            f"- Recommendations: {recs}",
            f"- Bars: {result.metrics.bar_count if result.metrics else 0}",
            f"- Read-only action: {result.read_only_decision.action if result.read_only_decision else 'NONE'}",
            "- Boundary: in-memory synthetic simulation only; no broker, no secret, no network, no order, no account access, no data access.",
        )
    )


def render_controlled_offline_runner_json_report(result: ControlledOfflineRunnerMinimalResult) -> str:
    metrics = result.metrics
    return (
        "{"
        f"\"state\":\"{result.state.value}\","
        f"\"decision\":\"{result.decision.value}\","
        f"\"score\":{result.score.overall_score},"
        f"\"risks\":[{','.join('\"' + risk.value + '\"' for risk in result.risks)}],"
        f"\"recommendations\":[{','.join('\"' + rec.value + '\"' for rec in result.recommendations)}],"
        f"\"bar_count\":{metrics.bar_count if metrics else 0},"
        f"\"order_count\":{metrics.order_count if metrics else 0},"
        f"\"real_order_count\":{metrics.real_order_count if metrics else 0},"
        "\"offline_only\":true,"
        "\"read_only\":true"
        "}"
    )


def run_controlled_offline_runner_minimal(
    data: ControlledOfflineRunnerMinimalInput | Mapping[str, Any] | None = None,
) -> ControlledOfflineRunnerMinimalResult:
    coerced = _coerce_input(data)
    scenario = build_controlled_offline_synthetic_market_scenario(coerced) if coerced is not None else None
    account = build_controlled_offline_simulated_account_snapshot(coerced) if coerced is not None else None
    broker = build_controlled_offline_simulated_broker_snapshot(coerced) if coerced is not None else None
    signal = evaluate_controlled_offline_strategy_signal(scenario, coerced) if scenario is not None else None
    position_size = compute_controlled_offline_position_size(account, signal, scenario, coerced) if account and signal and scenario else 0.0
    risk_guard = apply_controlled_offline_risk_guards(coerced, account, broker, signal, position_size) if account and broker and signal else None
    decision = simulate_controlled_offline_read_only_decision(scenario, signal, risk_guard) if scenario and signal and risk_guard else None
    journal_entries = write_controlled_offline_journal_entries(scenario, account, broker, signal, risk_guard, decision, coerced) if scenario and account and broker and signal and risk_guard and decision else ()
    metrics = compute_controlled_offline_runner_metrics(scenario, decision, coerced) if scenario and decision else None
    risks = detect_controlled_offline_runner_risks(coerced, scenario, account, broker, signal, risk_guard, journal_entries, metrics)
    score = _build_score(coerced, scenario, account, broker, signal, risk_guard, journal_entries, metrics, risks)
    recommendations = generate_controlled_offline_runner_recommendations(coerced, risks)
    result = ControlledOfflineRunnerMinimalResult(
        state=_state_for(risks, score),
        decision=_decision_for(risks),
        score=score,
        risks=risks,
        recommendations=recommendations,
        scenario=scenario,
        account_snapshot=account,
        broker_snapshot=broker,
        strategy_signal=signal,
        risk_guard=risk_guard,
        read_only_decision=decision,
        journal_entries=journal_entries,
        metrics=metrics,
        report=None,
        offline_only=coerced is not None and coerced.offline_mode_enforced is True,
        sandbox_only=coerced is not None and coerced.sandbox_mode_enforced is True,
        in_memory_only=coerced is not None and coerced.in_memory_only is True,
        runner_executed=coerced is not None,
        real_order_submitted=False,
        real_account_accessed=False,
        data_accessed=False,
    )
    report = ControlledOfflineRunnerReport(
        markdown=render_controlled_offline_runner_markdown_report(result),
        json=render_controlled_offline_runner_json_report(result),
    )
    return ControlledOfflineRunnerMinimalResult(**{**result.__dict__, "report": report})


__all__ = [
    "run_controlled_offline_runner_minimal",
    "validate_controlled_offline_runner_minimal_input",
    "build_controlled_offline_synthetic_market_scenario",
    "build_controlled_offline_simulated_account_snapshot",
    "build_controlled_offline_simulated_broker_snapshot",
    "evaluate_controlled_offline_strategy_signal",
    "apply_controlled_offline_risk_guards",
    "compute_controlled_offline_position_size",
    "simulate_controlled_offline_read_only_decision",
    "write_controlled_offline_journal_entries",
    "compute_controlled_offline_runner_metrics",
    "detect_controlled_offline_runner_risks",
    "generate_controlled_offline_runner_recommendations",
    "render_controlled_offline_runner_markdown_report",
    "render_controlled_offline_runner_json_report",
    "assert_controlled_offline_runner_no_real_execution_boundaries",
]
