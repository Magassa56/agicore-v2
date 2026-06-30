"""Deterministic offline risk guard enforcement v1 for AGIcore Trading."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from math import isfinite
from typing import Any, Iterable, Mapping

from agicore.trading.controlled_offline_runner_minimal_models import ControlledOfflineSyntheticMarketScenario
from agicore.trading.risk_guard_enforcement_v1_models import (
    RiskGuardContextV1,
    RiskGuardEnforcementReportV1,
    RiskGuardEnforcementSummaryV1,
    RiskGuardEnforcementV1Decision,
    RiskGuardEnforcementV1Input,
    RiskGuardEnforcementV1Recommendation,
    RiskGuardEnforcementV1Result,
    RiskGuardEnforcementV1Risk,
    RiskGuardEnforcementV1Score,
    RiskGuardEnforcementV1State,
    RiskGuardEvaluationV1,
    RiskGuardLimitsV1,
    RiskGuardViolationV1,
)
from agicore.trading.simulated_broker_stub_v1_models import (
    SimulatedBrokerAccountSnapshotV1,
    SimulatedBrokerPositionSnapshotV1,
    SimulatedBrokerReadOnlyOrderPreviewV1,
)
from agicore.trading.synthetic_market_scenario_v1_models import SyntheticMarketScenarioV1


Risk = RiskGuardEnforcementV1Risk
Recommendation = RiskGuardEnforcementV1Recommendation
Decision = RiskGuardEnforcementV1Decision
State = RiskGuardEnforcementV1State


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


def _coerce_input(data: RiskGuardEnforcementV1Input | Mapping[str, Any] | None) -> RiskGuardEnforcementV1Input | None:
    if data is None:
        return None
    if isinstance(data, RiskGuardEnforcementV1Input):
        return data
    allowed = {field.name for field in fields(RiskGuardEnforcementV1Input)}
    return RiskGuardEnforcementV1Input(**{key: value for key, value in dict(data).items() if key in allowed})


def _finite(value: Any) -> bool:
    return isinstance(value, int | float) and isfinite(float(value))


def _non_negative(value: Any) -> bool:
    return _finite(value) and float(value) >= 0.0


def _positive(value: Any) -> bool:
    return _finite(value) and float(value) > 0.0


def _round(value: float) -> float:
    return round(float(value), 10)


def _violation(guard: str, risk: Risk, message: str, actual: Any = None, limit: Any = None) -> RiskGuardEvaluationV1:
    return RiskGuardEvaluationV1(
        guard_name=guard,
        passed=False,
        blocking=True,
        violation=RiskGuardViolationV1(guard, risk, message, actual, limit),
    )


def _pass(guard: str) -> RiskGuardEvaluationV1:
    return RiskGuardEvaluationV1(guard_name=guard, passed=True)


def build_risk_guard_limits_v1(data: RiskGuardEnforcementV1Input | Mapping[str, Any] | None) -> RiskGuardLimitsV1:
    data = _coerce_input(data) or RiskGuardEnforcementV1Input()
    if isinstance(data.limits, RiskGuardLimitsV1):
        return data.limits
    if isinstance(data.limits, Mapping):
        payload = dict(data.limits)
        return RiskGuardLimitsV1(
            max_position_size=float(payload.get("max_position_size", 10.0)),
            max_notional_exposure=float(payload.get("max_notional_exposure", 10_000.0)),
            min_available_cash=float(payload.get("min_available_cash", 0.0)),
            max_margin_usage=float(payload.get("max_margin_usage", 0.5)),
            max_daily_loss=float(payload.get("max_daily_loss", 1_000.0)),
            max_drawdown=float(payload.get("max_drawdown", 0.1)),
            allowed_symbols=tuple(payload.get("allowed_symbols", ("SIM",))),
        )
    return RiskGuardLimitsV1()


def _default_order_preview(data: RiskGuardEnforcementV1Input) -> SimulatedBrokerReadOnlyOrderPreviewV1:
    return SimulatedBrokerReadOnlyOrderPreviewV1(
        symbol=data.symbol,
        action="BUY" if data.requested_quantity else "HOLD",
        requested_quantity=data.requested_quantity,
        reference_price=data.reference_price,
        notional=_round(data.requested_quantity * data.reference_price),
    )


def _default_account(data: RiskGuardEnforcementV1Input) -> SimulatedBrokerAccountSnapshotV1:
    equity = max(data.available_cash + data.requested_quantity * data.reference_price, 1.0)
    return SimulatedBrokerAccountSnapshotV1("SIM-ACCOUNT", data.available_cash, equity, data.available_cash)


def _default_position(data: RiskGuardEnforcementV1Input) -> SimulatedBrokerPositionSnapshotV1:
    market_value = data.requested_quantity * data.reference_price
    return SimulatedBrokerPositionSnapshotV1(data.symbol, data.requested_quantity, data.reference_price, data.reference_price, market_value)


def _default_scenario(data: RiskGuardEnforcementV1Input) -> ControlledOfflineSyntheticMarketScenario:
    from agicore.trading.controlled_offline_runner_minimal_models import ControlledOfflineSyntheticMarketBar

    bars = (
        ControlledOfflineSyntheticMarketBar(0, data.symbol, data.reference_price, data.reference_price, data.reference_price, data.reference_price, 1000.0, "T0"),
        ControlledOfflineSyntheticMarketBar(1, data.symbol, data.reference_price, data.reference_price, data.reference_price, data.reference_price, 1000.0, "T1"),
    )
    return ControlledOfflineSyntheticMarketScenario("risk-guard-default", data.symbol, bars)


def build_risk_guard_context_v1(data: RiskGuardEnforcementV1Input | Mapping[str, Any] | None) -> RiskGuardContextV1:
    data = _coerce_input(data) or RiskGuardEnforcementV1Input()
    order_preview = data.order_preview if data.order_preview is not None else _default_order_preview(data)
    account = data.account_snapshot if data.account_snapshot is not None else _default_account(data)
    position = data.position_snapshot if data.position_snapshot is not None else _default_position(data)
    scenario = data.synthetic_market_scenario if data.synthetic_market_scenario is not None else _default_scenario(data)
    return RiskGuardContextV1(
        symbol=data.symbol,
        requested_quantity=data.requested_quantity,
        reference_price=data.reference_price,
        notional_exposure=_round(data.requested_quantity * data.reference_price),
        available_cash=data.available_cash,
        margin_usage=data.margin_usage,
        daily_loss=data.daily_loss,
        drawdown=data.drawdown,
        order_preview=order_preview,
        account_snapshot=account,
        position_snapshot=position,
        synthetic_market_scenario=scenario,
    )


def _valid_limits(limits: RiskGuardLimitsV1 | None) -> bool:
    return (
        limits is not None
        and _non_negative(limits.max_position_size)
        and _positive(limits.max_notional_exposure)
        and _non_negative(limits.min_available_cash)
        and _finite(limits.max_margin_usage)
        and 0.0 <= limits.max_margin_usage <= 1.0
        and _non_negative(limits.max_daily_loss)
        and _finite(limits.max_drawdown)
        and 0.0 <= limits.max_drawdown <= 1.0
        and bool(limits.allowed_symbols)
    )


def _valid_context(context: RiskGuardContextV1 | None) -> bool:
    return (
        context is not None
        and bool(context.symbol)
        and _non_negative(context.requested_quantity)
        and _positive(context.reference_price)
        and _non_negative(context.notional_exposure)
        and _finite(context.available_cash)
        and _finite(context.margin_usage)
        and _non_negative(context.daily_loss)
        and _non_negative(context.drawdown)
    )


def validate_risk_guard_enforcement_v1_input(data: RiskGuardEnforcementV1Input | Mapping[str, Any] | None) -> bool:
    data = _coerce_input(data)
    if data is None:
        return False
    limits = build_risk_guard_limits_v1(data)
    context = build_risk_guard_context_v1(data)
    return (
        bool(data.symbol)
        and _non_negative(data.requested_quantity)
        and _positive(data.reference_price)
        and _finite(data.available_cash)
        and _finite(data.margin_usage)
        and _non_negative(data.daily_loss)
        and _non_negative(data.drawdown)
        and data.force_context_invalid is False
        and _valid_limits(limits)
        and _valid_context(context)
        and assert_risk_guard_enforcement_v1_offline_boundaries(data)
    )


def enforce_max_position_size_guard_v1(context: RiskGuardContextV1, limits: RiskGuardLimitsV1) -> RiskGuardEvaluationV1:
    if context.requested_quantity > limits.max_position_size:
        return _violation("max_position_size", Risk.MAX_POSITION_SIZE_EXCEEDED, "requested quantity exceeds max position size", context.requested_quantity, limits.max_position_size)
    return _pass("max_position_size")


def enforce_max_notional_exposure_guard_v1(context: RiskGuardContextV1, limits: RiskGuardLimitsV1) -> RiskGuardEvaluationV1:
    if context.notional_exposure > limits.max_notional_exposure:
        return _violation("max_notional_exposure", Risk.MAX_NOTIONAL_EXPOSURE_EXCEEDED, "notional exposure exceeds limit", context.notional_exposure, limits.max_notional_exposure)
    return _pass("max_notional_exposure")


def enforce_available_cash_guard_v1(context: RiskGuardContextV1, limits: RiskGuardLimitsV1) -> RiskGuardEvaluationV1:
    required_cash = max(context.notional_exposure, limits.min_available_cash)
    if context.available_cash < required_cash:
        return _violation("available_cash", Risk.AVAILABLE_CASH_INSUFFICIENT, "available cash below required simulated cash", context.available_cash, required_cash)
    return _pass("available_cash")


def enforce_margin_usage_guard_v1(context: RiskGuardContextV1, limits: RiskGuardLimitsV1) -> RiskGuardEvaluationV1:
    if context.margin_usage > limits.max_margin_usage:
        return _violation("margin_usage", Risk.MARGIN_USAGE_EXCEEDED, "margin usage exceeds limit", context.margin_usage, limits.max_margin_usage)
    return _pass("margin_usage")


def enforce_max_drawdown_guard_v1(context: RiskGuardContextV1, limits: RiskGuardLimitsV1) -> RiskGuardEvaluationV1:
    if context.drawdown > limits.max_drawdown:
        return _violation("max_drawdown", Risk.MAX_DRAWDOWN_EXCEEDED, "drawdown exceeds limit", context.drawdown, limits.max_drawdown)
    return _pass("max_drawdown")


def enforce_daily_loss_guard_v1(context: RiskGuardContextV1, limits: RiskGuardLimitsV1) -> RiskGuardEvaluationV1:
    if context.daily_loss > limits.max_daily_loss:
        return _violation("daily_loss", Risk.DAILY_LOSS_LIMIT_EXCEEDED, "daily loss exceeds limit", context.daily_loss, limits.max_daily_loss)
    return _pass("daily_loss")


def enforce_symbol_allowlist_guard_v1(context: RiskGuardContextV1, limits: RiskGuardLimitsV1) -> RiskGuardEvaluationV1:
    if context.symbol not in limits.allowed_symbols:
        return _violation("symbol_allowlist", Risk.SYMBOL_NOT_ALLOWED, "symbol is not allowlisted", context.symbol, ",".join(limits.allowed_symbols))
    return _pass("symbol_allowlist")


def enforce_read_only_order_preview_guard_v1(context: RiskGuardContextV1) -> RiskGuardEvaluationV1:
    preview = context.order_preview
    valid = (
        isinstance(preview, SimulatedBrokerReadOnlyOrderPreviewV1)
        and preview.read_only is True
        and preview.order_submitted is False
        and preview.real_order is False
        and preview.position_mutation is False
        and preview.symbol == context.symbol
    )
    if not valid:
        return _violation("read_only_order_preview", Risk.READ_ONLY_ORDER_PREVIEW_INVALID, "order preview is not read-only simulated")
    return _pass("read_only_order_preview")


def enforce_no_real_execution_guard_v1(data: RiskGuardEnforcementV1Input | Mapping[str, Any] | None) -> RiskGuardEvaluationV1:
    if not assert_risk_guard_enforcement_v1_offline_boundaries(data):
        return _violation("no_real_execution", Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION, "offline no-real-execution boundary failed")
    return _pass("no_real_execution")


def enforce_account_snapshot_guard_v1(context: RiskGuardContextV1) -> RiskGuardEvaluationV1:
    account = context.account_snapshot
    valid = (
        isinstance(account, SimulatedBrokerAccountSnapshotV1)
        and bool(account.account_id)
        and _non_negative(account.cash)
        and _non_negative(account.equity)
        and _non_negative(account.buying_power)
        and account.simulated is True
        and account.read_only is True
        and account.real_account is False
    )
    if not valid:
        return _violation("account_snapshot", Risk.ACCOUNT_SNAPSHOT_INVALID, "account snapshot is not simulated read-only")
    return _pass("account_snapshot")


def enforce_position_snapshot_guard_v1(context: RiskGuardContextV1) -> RiskGuardEvaluationV1:
    position = context.position_snapshot
    valid = (
        isinstance(position, SimulatedBrokerPositionSnapshotV1)
        and position.symbol == context.symbol
        and _finite(position.quantity)
        and _positive(position.average_price)
        and _positive(position.market_price)
        and _finite(position.market_value)
        and position.simulated is True
        and position.read_only is True
        and position.real_position is False
    )
    if not valid:
        return _violation("position_snapshot", Risk.POSITION_SNAPSHOT_INVALID, "position snapshot is not simulated read-only")
    return _pass("position_snapshot")


def enforce_synthetic_market_scenario_guard_v1(context: RiskGuardContextV1) -> RiskGuardEvaluationV1:
    scenario = context.synthetic_market_scenario
    bars = getattr(scenario, "bars", ())
    valid = (
        isinstance(scenario, ControlledOfflineSyntheticMarketScenario | SyntheticMarketScenarioV1)
        and getattr(scenario, "symbol", context.symbol) == context.symbol
        and bool(bars)
    )
    if not valid:
        return _violation("synthetic_market_scenario", Risk.SYNTHETIC_MARKET_SCENARIO_INVALID, "synthetic market scenario is invalid")
    return _pass("synthetic_market_scenario")


def aggregate_risk_guard_evaluations_v1(evaluations: Iterable[RiskGuardEvaluationV1]) -> RiskGuardEnforcementSummaryV1:
    evaluations = tuple(evaluations)
    violations = tuple(item.violation for item in evaluations if item.violation is not None)
    blocking = tuple(item for item in evaluations if not item.passed and item.blocking)
    return RiskGuardEnforcementSummaryV1(
        all_passed=all(item.passed for item in evaluations),
        evaluation_count=len(evaluations),
        passed_count=sum(1 for item in evaluations if item.passed),
        violation_count=len(violations),
        blocking_violation_count=len(blocking),
    )


def assert_risk_guard_enforcement_v1_offline_boundaries(data: RiskGuardEnforcementV1Input | Mapping[str, Any] | None) -> bool:
    data = _coerce_input(data)
    return (
        data is not None
        and data.offline_mode_enforced is True
        and data.sandbox_mode_enforced is True
        and data.in_memory_only is True
        and data.risk_guard_simulated_only is True
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


def detect_risk_guard_enforcement_v1_risks(
    data: RiskGuardEnforcementV1Input | Mapping[str, Any] | None,
    limits: RiskGuardLimitsV1 | None = None,
    context: RiskGuardContextV1 | None = None,
    evaluations: tuple[RiskGuardEvaluationV1, ...] = (),
) -> tuple[Risk, ...]:
    data = _coerce_input(data)
    risks: list[Risk] = []
    if data is None:
        risks.append(Risk.RISK_GUARD_INPUT_MISSING)
        return tuple(risks)
    if limits is not None and not _valid_limits(limits):
        risks.append(Risk.RISK_GUARD_LIMITS_INVALID)
    if context is not None and (not _valid_context(context) or data.force_context_invalid):
        risks.append(Risk.RISK_GUARD_CONTEXT_INVALID)
    risks.extend(item.violation.risk for item in evaluations if item.violation is not None)
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
    if data.no_data_access is not True or data.data_access_requested:
        risks.append(Risk.DATA_ACCESS_BOUNDARY_VIOLATION)
    return _dedupe(risks)


def _score(flag: bool) -> int:
    return 100 if flag else 0


def compute_risk_guard_enforcement_v1_score(
    data: RiskGuardEnforcementV1Input | Mapping[str, Any] | None,
    limits: RiskGuardLimitsV1 | None,
    context: RiskGuardContextV1 | None,
    summary: RiskGuardEnforcementSummaryV1 | None,
    risks: tuple[Risk, ...],
) -> RiskGuardEnforcementV1Score:
    data = _coerce_input(data)
    parts = (
        _score(data is not None and validate_risk_guard_enforcement_v1_input(data)),
        _score(_valid_limits(limits)),
        _score(_valid_context(context) and (data is None or data.force_context_invalid is False)),
        _score(summary is not None and summary.all_passed),
        _score(data is not None and assert_risk_guard_enforcement_v1_offline_boundaries(data)),
    )
    overall = 100 if not risks and all(part == 100 for part in parts) else round(sum(parts) / len(parts))
    return RiskGuardEnforcementV1Score(overall, *parts)


def generate_risk_guard_enforcement_v1_recommendations(risks: Iterable[Risk] | None = None) -> tuple[Recommendation, ...]:
    risks = tuple(risks or ())
    if not risks:
        return (
            Recommendation.RUN_RISK_GUARD_ENFORCEMENT_V1_TEST_SUITE,
            Recommendation.APPROVE_JOURNAL_WRITER_V1,
        )
    mapping = {
        Risk.RISK_GUARD_INPUT_MISSING: Recommendation.PROVIDE_RISK_GUARD_INPUT,
        Risk.RISK_GUARD_LIMITS_INVALID: Recommendation.FIX_RISK_GUARD_LIMITS,
        Risk.RISK_GUARD_CONTEXT_INVALID: Recommendation.FIX_RISK_GUARD_CONTEXT,
        Risk.MAX_POSITION_SIZE_EXCEEDED: Recommendation.REDUCE_POSITION_SIZE,
        Risk.MAX_NOTIONAL_EXPOSURE_EXCEEDED: Recommendation.REDUCE_NOTIONAL_EXPOSURE,
        Risk.AVAILABLE_CASH_INSUFFICIENT: Recommendation.RESTORE_AVAILABLE_CASH,
        Risk.MARGIN_USAGE_EXCEEDED: Recommendation.REDUCE_MARGIN_USAGE,
        Risk.DAILY_LOSS_LIMIT_EXCEEDED: Recommendation.STOP_AFTER_DAILY_LOSS,
        Risk.MAX_DRAWDOWN_EXCEEDED: Recommendation.STOP_AFTER_DRAWDOWN,
        Risk.SYMBOL_NOT_ALLOWED: Recommendation.USE_ALLOWED_SYMBOL,
        Risk.READ_ONLY_ORDER_PREVIEW_INVALID: Recommendation.KEEP_ORDER_PREVIEW_READ_ONLY,
        Risk.ACCOUNT_SNAPSHOT_INVALID: Recommendation.FIX_ACCOUNT_SNAPSHOT,
        Risk.POSITION_SNAPSHOT_INVALID: Recommendation.FIX_POSITION_SNAPSHOT,
        Risk.SYNTHETIC_MARKET_SCENARIO_INVALID: Recommendation.FIX_SYNTHETIC_MARKET_SCENARIO,
        Risk.REAL_BROKER_BOUNDARY_VIOLATION: Recommendation.REMOVE_REAL_BROKER_ACCESS,
        Risk.REAL_SECRET_BOUNDARY_VIOLATION: Recommendation.REMOVE_REAL_SECRET_ACCESS,
        Risk.NETWORK_BOUNDARY_VIOLATION: Recommendation.REMOVE_NETWORK_ACCESS,
        Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION: Recommendation.REMOVE_ORDER_EXECUTION,
        Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION: Recommendation.REMOVE_ACCOUNT_ACCESS,
        Risk.POSITION_MUTATION_BOUNDARY_VIOLATION: Recommendation.REMOVE_POSITION_MUTATION,
        Risk.DATA_ACCESS_BOUNDARY_VIOLATION: Recommendation.REMOVE_DATA_ACCESS,
    }
    return _dedupe(mapping[risk] for risk in risks if risk in mapping)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_RISK_GUARD_ENFORCEMENT_V1
    boundary = {
        Risk.REAL_BROKER_BOUNDARY_VIOLATION,
        Risk.REAL_SECRET_BOUNDARY_VIOLATION,
        Risk.NETWORK_BOUNDARY_VIOLATION,
        Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION,
        Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION,
        Risk.POSITION_MUTATION_BOUNDARY_VIOLATION,
        Risk.DATA_ACCESS_BOUNDARY_VIOLATION,
    }
    if any(risk in boundary for risk in risks):
        return Decision.BLOCK_RISK_GUARD_ENFORCEMENT_V1
    if Risk.RISK_GUARD_INPUT_MISSING in risks:
        return Decision.REQUIRE_RISK_GUARD_INPUT_FIXES
    if Risk.RISK_GUARD_LIMITS_INVALID in risks:
        return Decision.REQUIRE_RISK_GUARD_LIMITS_FIXES
    if Risk.RISK_GUARD_CONTEXT_INVALID in risks:
        return Decision.REQUIRE_RISK_GUARD_CONTEXT_FIXES
    ordered = (
        (Risk.MAX_POSITION_SIZE_EXCEEDED, Decision.REQUIRE_MAX_POSITION_SIZE_FIXES),
        (Risk.MAX_NOTIONAL_EXPOSURE_EXCEEDED, Decision.REQUIRE_MAX_NOTIONAL_EXPOSURE_FIXES),
        (Risk.AVAILABLE_CASH_INSUFFICIENT, Decision.REQUIRE_AVAILABLE_CASH_FIXES),
        (Risk.MARGIN_USAGE_EXCEEDED, Decision.REQUIRE_MARGIN_USAGE_FIXES),
        (Risk.DAILY_LOSS_LIMIT_EXCEEDED, Decision.REQUIRE_DAILY_LOSS_FIXES),
        (Risk.MAX_DRAWDOWN_EXCEEDED, Decision.REQUIRE_DRAWDOWN_FIXES),
        (Risk.SYMBOL_NOT_ALLOWED, Decision.REQUIRE_SYMBOL_ALLOWLIST_FIXES),
        (Risk.READ_ONLY_ORDER_PREVIEW_INVALID, Decision.REQUIRE_READ_ONLY_ORDER_PREVIEW_FIXES),
        (Risk.ACCOUNT_SNAPSHOT_INVALID, Decision.REQUIRE_RISK_GUARD_CONTEXT_FIXES),
        (Risk.POSITION_SNAPSHOT_INVALID, Decision.REQUIRE_RISK_GUARD_CONTEXT_FIXES),
        (Risk.SYNTHETIC_MARKET_SCENARIO_INVALID, Decision.REQUIRE_RISK_GUARD_CONTEXT_FIXES),
    )
    for risk, decision in ordered:
        if risk in risks:
            return decision
    return Decision.BLOCK_RISK_GUARD_ENFORCEMENT_V1


def _state_for(risks: tuple[Risk, ...], score: RiskGuardEnforcementV1Score) -> State:
    if Risk.RISK_GUARD_INPUT_MISSING in risks or Risk.RISK_GUARD_LIMITS_INVALID in risks or Risk.RISK_GUARD_CONTEXT_INVALID in risks:
        return State.RISK_GUARD_ENFORCEMENT_V1_INPUT_INVALID
    if risks:
        return State.RISK_GUARD_ENFORCEMENT_V1_BLOCKED
    if score.overall_score == 100:
        return State.READY_FOR_JOURNAL_WRITER_V1
    if score.overall_score >= 70:
        return State.RISK_GUARD_ENFORCEMENT_V1_COMPLETED_WITH_WARNINGS
    return State.NOT_READY


def render_risk_guard_enforcement_v1_markdown_report(result: RiskGuardEnforcementV1Result) -> str:
    risks = ", ".join(_value(risk) for risk in result.risks) or "none"
    recs = ", ".join(_value(rec) for rec in result.recommendations) or "none"
    return "\n".join(
        (
            "# Risk Guard Enforcement v1",
            f"- State: {result.state.value}",
            f"- Decision: {result.decision.value}",
            f"- Score: {result.score.overall_score}",
            f"- Evaluations: {result.summary.evaluation_count if result.summary else 0}",
            f"- Violations: {result.summary.violation_count if result.summary else 0}",
            f"- Blocking violations: {result.summary.blocking_violation_count if result.summary else 0}",
            f"- Risks: {risks}",
            f"- Recommendations: {recs}",
            "- Boundary: deterministic in-memory risk guards only; no broker, no secret, no network, no order, no account access, no position mutation, no external data.",
            f"- Next phase: {result.next_phase}",
        )
    )


def render_risk_guard_enforcement_v1_json_report(result: RiskGuardEnforcementV1Result) -> str:
    risks = ",".join(f'"{risk.value}"' for risk in result.risks)
    recs = ",".join(f'"{rec.value}"' for rec in result.recommendations)
    return (
        "{"
        f"\"state\":\"{result.state.value}\","
        f"\"decision\":\"{result.decision.value}\","
        f"\"score\":{result.score.overall_score},"
        f"\"risks\":[{risks}],"
        f"\"recommendations\":[{recs}],"
        f"\"evaluation_count\":{result.summary.evaluation_count if result.summary else 0},"
        f"\"violation_count\":{result.summary.violation_count if result.summary else 0},"
        f"\"blocking_violation_count\":{result.summary.blocking_violation_count if result.summary else 0},"
        "\"offline_only\":true,"
        "\"simulated_only\":true"
        "}"
    )


def enforce_risk_guard_v1(
    data: RiskGuardEnforcementV1Input | Mapping[str, Any] | None = None,
) -> RiskGuardEnforcementV1Result:
    data = _coerce_input(data)
    limits = build_risk_guard_limits_v1(data) if data is not None else None
    context = build_risk_guard_context_v1(data) if data is not None else None
    evaluations: tuple[RiskGuardEvaluationV1, ...] = ()
    if limits is not None and context is not None:
        evaluations = (
            enforce_max_position_size_guard_v1(context, limits),
            enforce_max_notional_exposure_guard_v1(context, limits),
            enforce_available_cash_guard_v1(context, limits),
            enforce_margin_usage_guard_v1(context, limits),
            enforce_daily_loss_guard_v1(context, limits),
            enforce_max_drawdown_guard_v1(context, limits),
            enforce_symbol_allowlist_guard_v1(context, limits),
            enforce_read_only_order_preview_guard_v1(context),
            enforce_no_real_execution_guard_v1(data),
            enforce_account_snapshot_guard_v1(context),
            enforce_position_snapshot_guard_v1(context),
            enforce_synthetic_market_scenario_guard_v1(context),
        )
    summary = aggregate_risk_guard_evaluations_v1(evaluations)
    risks = detect_risk_guard_enforcement_v1_risks(data, limits, context, evaluations)
    score = compute_risk_guard_enforcement_v1_score(data, limits, context, summary, risks)
    recommendations = generate_risk_guard_enforcement_v1_recommendations(risks)
    result = RiskGuardEnforcementV1Result(
        state=_state_for(risks, score),
        decision=_decision_for(risks),
        score=score,
        risks=risks,
        recommendations=recommendations,
        limits=limits,
        context=context,
        evaluations=evaluations,
        violations=tuple(item.violation for item in evaluations if item.violation is not None),
        summary=summary,
        report=None,
        offline_only=data is not None and data.offline_mode_enforced,
        simulated_only=data is not None and data.risk_guard_simulated_only,
        real_order_submitted=False,
        real_account_accessed=False,
        position_mutated=False,
        data_accessed=False,
    )
    report = RiskGuardEnforcementReportV1(
        markdown=render_risk_guard_enforcement_v1_markdown_report(result),
        json=render_risk_guard_enforcement_v1_json_report(result),
    )
    return RiskGuardEnforcementV1Result(**{**result.__dict__, "report": report})


__all__ = [
    "enforce_risk_guard_v1",
    "validate_risk_guard_enforcement_v1_input",
    "build_risk_guard_limits_v1",
    "build_risk_guard_context_v1",
    "enforce_max_position_size_guard_v1",
    "enforce_max_notional_exposure_guard_v1",
    "enforce_available_cash_guard_v1",
    "enforce_margin_usage_guard_v1",
    "enforce_max_drawdown_guard_v1",
    "enforce_daily_loss_guard_v1",
    "enforce_symbol_allowlist_guard_v1",
    "enforce_read_only_order_preview_guard_v1",
    "enforce_no_real_execution_guard_v1",
    "enforce_account_snapshot_guard_v1",
    "enforce_position_snapshot_guard_v1",
    "enforce_synthetic_market_scenario_guard_v1",
    "aggregate_risk_guard_evaluations_v1",
    "compute_risk_guard_enforcement_v1_score",
    "detect_risk_guard_enforcement_v1_risks",
    "generate_risk_guard_enforcement_v1_recommendations",
    "render_risk_guard_enforcement_v1_markdown_report",
    "render_risk_guard_enforcement_v1_json_report",
    "assert_risk_guard_enforcement_v1_offline_boundaries",
]
