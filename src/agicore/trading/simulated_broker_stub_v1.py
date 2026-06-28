"""Deterministic in-memory simulated broker stub v1 for AGIcore Trading."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
from math import isfinite
from typing import Any, Iterable, Mapping

from agicore.trading.controlled_offline_runner_minimal_models import ControlledOfflineReadOnlyDecision
from agicore.trading.simulated_broker_stub_v1_models import (
    SimulatedBrokerAccountSnapshotV1,
    SimulatedBrokerExecutionPreviewV1,
    SimulatedBrokerExposureV1,
    SimulatedBrokerJournalEntryV1,
    SimulatedBrokerLimitsV1,
    SimulatedBrokerPositionSnapshotV1,
    SimulatedBrokerReadOnlyOrderPreviewV1,
    SimulatedBrokerRejectionV1,
    SimulatedBrokerStubV1Decision,
    SimulatedBrokerStubV1Input,
    SimulatedBrokerStubV1Metrics,
    SimulatedBrokerStubV1Recommendation,
    SimulatedBrokerStubV1Report,
    SimulatedBrokerStubV1Result,
    SimulatedBrokerStubV1Risk,
    SimulatedBrokerStubV1Score,
    SimulatedBrokerStubV1State,
)


Risk = SimulatedBrokerStubV1Risk
Recommendation = SimulatedBrokerStubV1Recommendation
Decision = SimulatedBrokerStubV1Decision
State = SimulatedBrokerStubV1State


_VALID_ACTIONS = {"BUY", "SELL", "HOLD"}


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


def _coerce_input(data: SimulatedBrokerStubV1Input | Mapping[str, Any] | None) -> SimulatedBrokerStubV1Input | None:
    if data is None:
        return None
    if isinstance(data, SimulatedBrokerStubV1Input):
        return data
    allowed = {field.name for field in fields(SimulatedBrokerStubV1Input)}
    return SimulatedBrokerStubV1Input(**{key: value for key, value in dict(data).items() if key in allowed})


def _finite(value: Any) -> bool:
    return isinstance(value, int | float) and isfinite(float(value))


def _non_negative(value: Any) -> bool:
    return _finite(value) and float(value) >= 0.0


def _positive(value: Any) -> bool:
    return _finite(value) and float(value) > 0.0


def _round(value: float) -> float:
    return round(float(value), 10)


def _action_from(data: SimulatedBrokerStubV1Input) -> str:
    decision = data.read_only_decision
    if isinstance(decision, ControlledOfflineReadOnlyDecision):
        return decision.action
    if isinstance(decision, Mapping):
        return str(decision.get("action", data.action)).upper()
    return data.action.upper()


def _symbol_from(data: SimulatedBrokerStubV1Input) -> str:
    decision = data.read_only_decision
    if isinstance(decision, ControlledOfflineReadOnlyDecision):
        return decision.symbol
    if isinstance(decision, Mapping):
        return str(decision.get("symbol", data.symbol))
    return data.symbol


def _quantity_from(data: SimulatedBrokerStubV1Input) -> float:
    decision = data.read_only_decision
    if isinstance(decision, ControlledOfflineReadOnlyDecision):
        return float(decision.proposed_position_size)
    if isinstance(decision, Mapping):
        return float(decision.get("proposed_position_size", decision.get("requested_quantity", data.requested_quantity)))
    return float(data.requested_quantity)


def _price_from(data: SimulatedBrokerStubV1Input) -> float:
    decision = data.read_only_decision
    if isinstance(decision, ControlledOfflineReadOnlyDecision):
        return float(decision.reference_price)
    if isinstance(decision, Mapping):
        return float(decision.get("reference_price", data.reference_price))
    return float(data.reference_price)


def validate_simulated_broker_stub_v1_input(data: SimulatedBrokerStubV1Input | Mapping[str, Any] | None) -> bool:
    data = _coerce_input(data)
    return (
        data is not None
        and bool(data.broker_id)
        and bool(data.account_id)
        and bool(data.symbol)
        and _action_from(data) in _VALID_ACTIONS
        and _non_negative(_quantity_from(data))
        and _positive(_price_from(data))
        and _non_negative(data.initial_cash)
        and _positive(data.initial_equity)
        and assert_simulated_broker_stub_v1_offline_boundaries(data)
    )


def build_simulated_broker_account_snapshot_v1(data: SimulatedBrokerStubV1Input | Mapping[str, Any] | None) -> SimulatedBrokerAccountSnapshotV1:
    data = _coerce_input(data) or SimulatedBrokerStubV1Input()
    if isinstance(data.account_snapshot, SimulatedBrokerAccountSnapshotV1):
        return data.account_snapshot
    if isinstance(data.account_snapshot, Mapping):
        payload = dict(data.account_snapshot)
        cash = float(payload.get("cash", data.initial_cash))
        equity = float(payload.get("equity", data.initial_equity))
        return SimulatedBrokerAccountSnapshotV1(
            account_id=str(payload.get("account_id", data.account_id)),
            cash=cash,
            equity=equity,
            buying_power=float(payload.get("buying_power", cash)),
            currency=str(payload.get("currency", "USD")),
            simulated=bool(payload.get("simulated", True)),
            read_only=bool(payload.get("read_only", True)),
            real_account=bool(payload.get("real_account", False)),
        )
    return SimulatedBrokerAccountSnapshotV1(data.account_id, data.initial_cash, data.initial_equity, data.initial_cash)


def build_simulated_broker_position_snapshot_v1(data: SimulatedBrokerStubV1Input | Mapping[str, Any] | None) -> SimulatedBrokerPositionSnapshotV1:
    data = _coerce_input(data) or SimulatedBrokerStubV1Input()
    if isinstance(data.position_snapshot, SimulatedBrokerPositionSnapshotV1):
        return data.position_snapshot
    if isinstance(data.position_snapshot, Mapping):
        payload = dict(data.position_snapshot)
        quantity = float(payload.get("quantity", data.initial_position_quantity))
        market_price = float(payload.get("market_price", data.reference_price))
        average_price = float(payload.get("average_price", market_price))
        return SimulatedBrokerPositionSnapshotV1(
            symbol=str(payload.get("symbol", data.symbol)),
            quantity=quantity,
            average_price=average_price,
            market_price=market_price,
            market_value=float(payload.get("market_value", quantity * market_price)),
            unrealized_pnl=float(payload.get("unrealized_pnl", quantity * (market_price - average_price))),
            simulated=bool(payload.get("simulated", True)),
            read_only=bool(payload.get("read_only", True)),
            real_position=bool(payload.get("real_position", False)),
        )
    market_value = data.initial_position_quantity * data.reference_price
    pnl = data.initial_position_quantity * (data.reference_price - data.average_price)
    return SimulatedBrokerPositionSnapshotV1(
        symbol=data.symbol,
        quantity=data.initial_position_quantity,
        average_price=data.average_price,
        market_price=data.reference_price,
        market_value=_round(market_value),
        unrealized_pnl=_round(pnl),
    )


def _build_limits(data: SimulatedBrokerStubV1Input | Mapping[str, Any] | None) -> SimulatedBrokerLimitsV1:
    data = _coerce_input(data) or SimulatedBrokerStubV1Input()
    if isinstance(data.limits, SimulatedBrokerLimitsV1):
        return data.limits
    if isinstance(data.limits, Mapping):
        payload = dict(data.limits)
        return SimulatedBrokerLimitsV1(
            max_order_notional=float(payload.get("max_order_notional", 10_000.0)),
            max_position_quantity=float(payload.get("max_position_quantity", 100.0)),
            max_margin_usage=float(payload.get("max_margin_usage", 0.5)),
            allow_short=bool(payload.get("allow_short", False)),
            simulated=bool(payload.get("simulated", True)),
        )
    return SimulatedBrokerLimitsV1()


def validate_simulated_broker_account_snapshot_v1(snapshot: SimulatedBrokerAccountSnapshotV1 | None) -> bool:
    return (
        snapshot is not None
        and bool(snapshot.account_id)
        and _non_negative(snapshot.cash)
        and _non_negative(snapshot.equity)
        and _non_negative(snapshot.buying_power)
        and bool(snapshot.currency)
        and snapshot.simulated is True
        and snapshot.read_only is True
        and snapshot.real_account is False
    )


def validate_simulated_broker_position_snapshot_v1(snapshot: SimulatedBrokerPositionSnapshotV1 | None) -> bool:
    return (
        snapshot is not None
        and bool(snapshot.symbol)
        and _finite(snapshot.quantity)
        and _positive(snapshot.average_price)
        and _positive(snapshot.market_price)
        and _finite(snapshot.market_value)
        and _finite(snapshot.unrealized_pnl)
        and abs(snapshot.market_value - snapshot.quantity * snapshot.market_price) < 0.0001
        and snapshot.simulated is True
        and snapshot.read_only is True
        and snapshot.real_position is False
    )


def _valid_limits(limits: SimulatedBrokerLimitsV1 | None) -> bool:
    return (
        limits is not None
        and _positive(limits.max_order_notional)
        and _non_negative(limits.max_position_quantity)
        and _finite(limits.max_margin_usage)
        and 0.0 <= limits.max_margin_usage <= 1.0
        and limits.simulated is True
    )


def simulate_broker_read_only_order_preview_v1(
    data: SimulatedBrokerStubV1Input | Mapping[str, Any] | None,
) -> SimulatedBrokerReadOnlyOrderPreviewV1:
    data = _coerce_input(data) or SimulatedBrokerStubV1Input()
    action = _action_from(data)
    quantity = 0.0 if action == "HOLD" else max(_quantity_from(data), 0.0)
    price = _price_from(data)
    return SimulatedBrokerReadOnlyOrderPreviewV1(
        symbol=_symbol_from(data),
        action=action,
        requested_quantity=_round(quantity),
        reference_price=_round(price),
        notional=_round(quantity * price),
        read_only=True,
        order_submitted=False,
        real_order=False,
        position_mutation=False,
    )


def simulate_broker_rejection_v1(reason: str = "read-only broker stub rejects real execution") -> SimulatedBrokerRejectionV1:
    return SimulatedBrokerRejectionV1(True, "SIMULATED_READ_ONLY_REJECTION", reason)


def compute_simulated_broker_available_cash_v1(
    account: SimulatedBrokerAccountSnapshotV1,
    preview: SimulatedBrokerReadOnlyOrderPreviewV1,
    data: SimulatedBrokerStubV1Input | Mapping[str, Any] | None = None,
) -> float:
    data = _coerce_input(data) or SimulatedBrokerStubV1Input()
    if data.force_available_cash_invalid:
        return -1.0
    reserved = preview.notional if preview.action == "BUY" else 0.0
    return _round(account.cash - reserved)


def compute_simulated_broker_margin_usage_v1(
    account: SimulatedBrokerAccountSnapshotV1,
    exposure_value: float,
    data: SimulatedBrokerStubV1Input | Mapping[str, Any] | None = None,
) -> float:
    data = _coerce_input(data) or SimulatedBrokerStubV1Input()
    if data.force_margin_usage_invalid:
        return 1.5
    return _round(abs(exposure_value) / account.equity) if account.equity > 0 else 0.0


def compute_simulated_broker_exposure_v1(
    account: SimulatedBrokerAccountSnapshotV1,
    position: SimulatedBrokerPositionSnapshotV1,
    preview: SimulatedBrokerReadOnlyOrderPreviewV1,
    data: SimulatedBrokerStubV1Input | Mapping[str, Any] | None = None,
) -> SimulatedBrokerExposureV1:
    data = _coerce_input(data) or SimulatedBrokerStubV1Input()
    signed_preview = preview.requested_quantity if preview.action == "BUY" else -preview.requested_quantity if preview.action == "SELL" else 0.0
    projected_quantity = position.quantity + signed_preview
    projected_value = projected_quantity * preview.reference_price
    gross = abs(projected_value)
    available_cash = compute_simulated_broker_available_cash_v1(account, preview, data)
    margin_usage = compute_simulated_broker_margin_usage_v1(account, gross, data)
    if data.force_exposure_invalid:
        gross = -1.0
    return SimulatedBrokerExposureV1(
        gross_exposure=_round(gross),
        net_exposure=_round(projected_value),
        exposure_fraction=_round(gross / account.equity) if account.equity > 0 else 0.0,
        margin_usage=margin_usage,
        available_cash=available_cash,
    )


def apply_simulated_broker_limits_v1(
    limits: SimulatedBrokerLimitsV1,
    exposure: SimulatedBrokerExposureV1,
    preview: SimulatedBrokerReadOnlyOrderPreviewV1,
) -> tuple[Risk, ...]:
    risks: list[Risk] = []
    if not _valid_limits(limits):
        risks.append(Risk.SIMULATED_BROKER_LIMITS_INVALID)
    if preview.notional > limits.max_order_notional or preview.requested_quantity > limits.max_position_quantity:
        risks.append(Risk.SIMULATED_BROKER_EXPOSURE_INVALID)
    if exposure.margin_usage > limits.max_margin_usage:
        risks.append(Risk.SIMULATED_BROKER_MARGIN_USAGE_INVALID)
    if not limits.allow_short and preview.action == "SELL" and exposure.net_exposure < 0:
        risks.append(Risk.SIMULATED_BROKER_EXPOSURE_INVALID)
    return _dedupe(risks)


def simulate_broker_acceptance_preview_v1(
    account: SimulatedBrokerAccountSnapshotV1,
    position: SimulatedBrokerPositionSnapshotV1,
    preview: SimulatedBrokerReadOnlyOrderPreviewV1,
    limits: SimulatedBrokerLimitsV1,
    exposure: SimulatedBrokerExposureV1,
) -> SimulatedBrokerExecutionPreviewV1:
    limit_risks = apply_simulated_broker_limits_v1(limits, exposure, preview)
    if limit_risks:
        return SimulatedBrokerExecutionPreviewV1(False, "SIMULATED_REJECTED", account.cash, position.quantity, "simulated limits rejected preview")
    signed = preview.requested_quantity if preview.action == "BUY" else -preview.requested_quantity if preview.action == "SELL" else 0.0
    return SimulatedBrokerExecutionPreviewV1(
        True,
        "SIMULATED_ACCEPTANCE_PREVIEW",
        exposure.available_cash,
        _round(position.quantity + signed),
        "simulated read-only acceptance preview; no order submitted",
    )


def generate_simulated_broker_journal_entries_v1(
    account: SimulatedBrokerAccountSnapshotV1,
    position: SimulatedBrokerPositionSnapshotV1,
    preview: SimulatedBrokerReadOnlyOrderPreviewV1,
    rejection: SimulatedBrokerRejectionV1,
    acceptance: SimulatedBrokerExecutionPreviewV1,
    exposure: SimulatedBrokerExposureV1,
    data: SimulatedBrokerStubV1Input | Mapping[str, Any] | None = None,
) -> tuple[SimulatedBrokerJournalEntryV1, ...]:
    data = _coerce_input(data) or SimulatedBrokerStubV1Input()
    if data.force_journal_missing:
        return ()
    return (
        SimulatedBrokerJournalEntryV1(0, "account_snapshot", "simulated account snapshot built", {"account_id": account.account_id}),
        SimulatedBrokerJournalEntryV1(1, "position_snapshot", "simulated position snapshot built", {"symbol": position.symbol, "quantity": position.quantity}),
        SimulatedBrokerJournalEntryV1(2, "read_only_order_preview", "read-only order preview recorded", {"action": preview.action, "notional": preview.notional}),
        SimulatedBrokerJournalEntryV1(3, "simulated_rejection", "real execution rejected by stub", {"code": rejection.code}),
        SimulatedBrokerJournalEntryV1(4, "acceptance_preview", "simulated acceptance preview computed", {"accepted": acceptance.accepted}),
        SimulatedBrokerJournalEntryV1(5, "exposure", "simulated exposure computed", {"gross_exposure": exposure.gross_exposure, "margin_usage": exposure.margin_usage}),
    )


def _valid_preview(preview: SimulatedBrokerReadOnlyOrderPreviewV1 | None) -> bool:
    return (
        preview is not None
        and bool(preview.symbol)
        and preview.action in _VALID_ACTIONS
        and _non_negative(preview.requested_quantity)
        and _positive(preview.reference_price)
        and _non_negative(preview.notional)
        and preview.read_only is True
        and preview.order_submitted is False
        and preview.real_order is False
        and preview.position_mutation is False
    )


def _valid_exposure(exposure: SimulatedBrokerExposureV1 | None) -> bool:
    return (
        exposure is not None
        and _non_negative(exposure.gross_exposure)
        and _finite(exposure.net_exposure)
        and _non_negative(exposure.exposure_fraction)
        and _finite(exposure.margin_usage)
        and 0.0 <= exposure.margin_usage <= 1.0
        and _non_negative(exposure.available_cash)
        and exposure.simulated is True
    )


def compute_simulated_broker_stub_v1_metrics(
    preview: SimulatedBrokerReadOnlyOrderPreviewV1,
    rejection: SimulatedBrokerRejectionV1,
    acceptance: SimulatedBrokerExecutionPreviewV1,
    exposure: SimulatedBrokerExposureV1,
    data: SimulatedBrokerStubV1Input | Mapping[str, Any] | None = None,
) -> SimulatedBrokerStubV1Metrics | None:
    data = _coerce_input(data) or SimulatedBrokerStubV1Input()
    if data.force_metrics_missing:
        return None
    return SimulatedBrokerStubV1Metrics(
        preview_count=1 if preview else 0,
        rejection_count=1 if rejection.rejected else 0,
        acceptance_preview_count=1 if acceptance else 0,
        real_order_count=0,
        real_account_access_count=0,
        position_mutation_count=0,
        data_access_count=0,
        gross_exposure=exposure.gross_exposure,
        available_cash=exposure.available_cash,
        margin_usage=exposure.margin_usage,
    )


def assert_simulated_broker_stub_v1_offline_boundaries(data: SimulatedBrokerStubV1Input | Mapping[str, Any] | None) -> bool:
    data = _coerce_input(data)
    return (
        data is not None
        and data.offline_mode_enforced is True
        and data.sandbox_mode_enforced is True
        and data.in_memory_only is True
        and data.simulated_broker_only is True
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


def detect_simulated_broker_stub_v1_risks(
    data: SimulatedBrokerStubV1Input | Mapping[str, Any] | None,
    account: SimulatedBrokerAccountSnapshotV1 | None = None,
    position: SimulatedBrokerPositionSnapshotV1 | None = None,
    limits: SimulatedBrokerLimitsV1 | None = None,
    preview: SimulatedBrokerReadOnlyOrderPreviewV1 | None = None,
    exposure: SimulatedBrokerExposureV1 | None = None,
    journal_entries: tuple[SimulatedBrokerJournalEntryV1, ...] = (),
    metrics: SimulatedBrokerStubV1Metrics | None = None,
) -> tuple[Risk, ...]:
    data = _coerce_input(data)
    risks: list[Risk] = []
    if data is None or not validate_simulated_broker_stub_v1_input(data):
        risks.append(Risk.SIMULATED_BROKER_INPUT_MISSING)
    if account is not None and not validate_simulated_broker_account_snapshot_v1(account):
        risks.append(Risk.SIMULATED_BROKER_ACCOUNT_SNAPSHOT_INVALID)
    if position is not None and not validate_simulated_broker_position_snapshot_v1(position):
        risks.append(Risk.SIMULATED_BROKER_POSITION_SNAPSHOT_INVALID)
    if limits is not None and not _valid_limits(limits):
        risks.append(Risk.SIMULATED_BROKER_LIMITS_INVALID)
    if preview is not None and not _valid_preview(preview):
        risks.append(Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION)
    if exposure is not None:
        if not _valid_exposure(exposure):
            risks.append(Risk.SIMULATED_BROKER_EXPOSURE_INVALID)
        if not _non_negative(exposure.available_cash):
            risks.append(Risk.SIMULATED_BROKER_AVAILABLE_CASH_INVALID)
        if not _finite(exposure.margin_usage) or not 0.0 <= exposure.margin_usage <= 1.0:
            risks.append(Risk.SIMULATED_BROKER_MARGIN_USAGE_INVALID)
    if limits is not None and exposure is not None and preview is not None:
        risks.extend(apply_simulated_broker_limits_v1(limits, exposure, preview))
    if not journal_entries:
        risks.append(Risk.SIMULATED_BROKER_JOURNAL_MISSING)
    if metrics is None:
        risks.append(Risk.SIMULATED_BROKER_METRICS_MISSING)
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
        if data.no_position_mutation is not True or data.position_mutation_requested:
            risks.append(Risk.POSITION_MUTATION_BOUNDARY_VIOLATION)
        if data.no_data_access is not True or data.data_access_requested:
            risks.append(Risk.DATA_ACCESS_BOUNDARY_VIOLATION)
    return _dedupe(risks)


def _score(flag: bool) -> int:
    return 100 if flag else 0


def _build_score(data, account, position, limits, exposure, journal_entries, metrics, risks) -> SimulatedBrokerStubV1Score:
    parts = (
        _score(data is not None and validate_simulated_broker_stub_v1_input(data)),
        _score(validate_simulated_broker_account_snapshot_v1(account)),
        _score(validate_simulated_broker_position_snapshot_v1(position)),
        _score(_valid_limits(limits)),
        _score(_valid_exposure(exposure)),
        _score(bool(journal_entries)),
        _score(metrics is not None),
        _score(data is not None and assert_simulated_broker_stub_v1_offline_boundaries(data)),
    )
    overall = 100 if not risks and all(part == 100 for part in parts) else round(sum(parts) / len(parts))
    return SimulatedBrokerStubV1Score(overall, *parts)


def generate_simulated_broker_stub_v1_recommendations(risks: Iterable[Risk] | None = None) -> tuple[Recommendation, ...]:
    risks = tuple(risks or ())
    if not risks:
        return (
            Recommendation.RUN_SIMULATED_BROKER_STUB_V1_TEST_SUITE,
            Recommendation.APPROVE_RISK_GUARD_ENFORCEMENT_V1,
        )
    mapping = {
        Risk.SIMULATED_BROKER_INPUT_MISSING: Recommendation.PROVIDE_SIMULATED_BROKER_INPUT,
        Risk.SIMULATED_BROKER_ACCOUNT_SNAPSHOT_INVALID: Recommendation.FIX_SIMULATED_ACCOUNT_SNAPSHOT,
        Risk.SIMULATED_BROKER_POSITION_SNAPSHOT_INVALID: Recommendation.FIX_SIMULATED_POSITION_SNAPSHOT,
        Risk.SIMULATED_BROKER_LIMITS_INVALID: Recommendation.FIX_SIMULATED_BROKER_LIMITS,
        Risk.SIMULATED_BROKER_EXPOSURE_INVALID: Recommendation.FIX_SIMULATED_BROKER_EXPOSURE,
        Risk.SIMULATED_BROKER_AVAILABLE_CASH_INVALID: Recommendation.FIX_SIMULATED_AVAILABLE_CASH,
        Risk.SIMULATED_BROKER_MARGIN_USAGE_INVALID: Recommendation.FIX_SIMULATED_MARGIN_USAGE,
        Risk.SIMULATED_BROKER_JOURNAL_MISSING: Recommendation.WRITE_SIMULATED_BROKER_JOURNAL,
        Risk.SIMULATED_BROKER_METRICS_MISSING: Recommendation.COMPUTE_SIMULATED_BROKER_METRICS,
        Risk.REAL_BROKER_BOUNDARY_VIOLATION: Recommendation.REMOVE_REAL_BROKER_ACCESS,
        Risk.REAL_SECRET_BOUNDARY_VIOLATION: Recommendation.REMOVE_REAL_SECRET_ACCESS,
        Risk.NETWORK_BOUNDARY_VIOLATION: Recommendation.REMOVE_NETWORK_ACCESS,
        Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION: Recommendation.KEEP_ORDER_PREVIEW_READ_ONLY,
        Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION: Recommendation.REMOVE_REAL_ACCOUNT_ACCESS,
        Risk.POSITION_MUTATION_BOUNDARY_VIOLATION: Recommendation.REMOVE_POSITION_MUTATION,
        Risk.DATA_ACCESS_BOUNDARY_VIOLATION: Recommendation.REMOVE_DATA_ACCESS,
    }
    return _dedupe(mapping[risk] for risk in risks if risk in mapping)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_SIMULATED_BROKER_STUB_V1
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
        return Decision.BLOCK_SIMULATED_BROKER_STUB_V1
    if Risk.SIMULATED_BROKER_INPUT_MISSING in risks:
        return Decision.REQUIRE_SIMULATED_BROKER_INPUT_FIXES
    if Risk.SIMULATED_BROKER_ACCOUNT_SNAPSHOT_INVALID in risks:
        return Decision.REQUIRE_SIMULATED_BROKER_ACCOUNT_SNAPSHOT_FIXES
    if Risk.SIMULATED_BROKER_POSITION_SNAPSHOT_INVALID in risks:
        return Decision.REQUIRE_SIMULATED_BROKER_POSITION_SNAPSHOT_FIXES
    if Risk.SIMULATED_BROKER_LIMITS_INVALID in risks:
        return Decision.REQUIRE_SIMULATED_BROKER_LIMITS_FIXES
    if Risk.SIMULATED_BROKER_EXPOSURE_INVALID in risks or Risk.SIMULATED_BROKER_AVAILABLE_CASH_INVALID in risks or Risk.SIMULATED_BROKER_MARGIN_USAGE_INVALID in risks:
        return Decision.REQUIRE_SIMULATED_BROKER_EXPOSURE_FIXES
    if Risk.SIMULATED_BROKER_JOURNAL_MISSING in risks:
        return Decision.REQUIRE_SIMULATED_BROKER_JOURNAL_FIXES
    if Risk.SIMULATED_BROKER_METRICS_MISSING in risks:
        return Decision.REQUIRE_SIMULATED_BROKER_METRICS_FIXES
    return Decision.BLOCK_SIMULATED_BROKER_STUB_V1


def _state_for(risks: tuple[Risk, ...], score: SimulatedBrokerStubV1Score) -> State:
    if Risk.SIMULATED_BROKER_INPUT_MISSING in risks:
        return State.SIMULATED_BROKER_STUB_V1_INPUT_INVALID
    if risks:
        return State.SIMULATED_BROKER_STUB_V1_BLOCKED
    if score.overall_score == 100:
        return State.READY_FOR_RISK_GUARD_ENFORCEMENT_V1
    if score.overall_score >= 70:
        return State.SIMULATED_BROKER_STUB_V1_COMPLETED_WITH_WARNINGS
    return State.NOT_READY


def render_simulated_broker_stub_v1_markdown_report(result: SimulatedBrokerStubV1Result) -> str:
    risks = ", ".join(_value(risk) for risk in result.risks) or "none"
    recs = ", ".join(_value(rec) for rec in result.recommendations) or "none"
    return "\n".join(
        (
            "# Simulated Broker Stub v1",
            f"- State: {result.state.value}",
            f"- Decision: {result.decision.value}",
            f"- Score: {result.score.overall_score}",
            f"- Order preview: {result.order_preview.action if result.order_preview else 'NONE'}",
            f"- Gross exposure: {result.exposure.gross_exposure if result.exposure else 0}",
            f"- Available cash: {result.exposure.available_cash if result.exposure else 0}",
            f"- Margin usage: {result.exposure.margin_usage if result.exposure else 0}",
            f"- Risks: {risks}",
            f"- Recommendations: {recs}",
            "- Boundary: simulated in-memory broker only; no real broker, no secret, no network, no order, no account access, no position mutation, no data access.",
            f"- Next phase: {result.next_phase}",
        )
    )


def render_simulated_broker_stub_v1_json_report(result: SimulatedBrokerStubV1Result) -> str:
    risks = ",".join(f'"{risk.value}"' for risk in result.risks)
    recs = ",".join(f'"{rec.value}"' for rec in result.recommendations)
    order_submitted = str(result.order_preview.order_submitted if result.order_preview else False).lower()
    return (
        "{"
        f"\"state\":\"{result.state.value}\","
        f"\"decision\":\"{result.decision.value}\","
        f"\"score\":{result.score.overall_score},"
        f"\"risks\":[{risks}],"
        f"\"recommendations\":[{recs}],"
        f"\"order_submitted\":{order_submitted},"
        f"\"real_order_count\":{result.metrics.real_order_count if result.metrics else 0},"
        f"\"gross_exposure\":{result.exposure.gross_exposure if result.exposure else 0},"
        f"\"available_cash\":{result.exposure.available_cash if result.exposure else 0},"
        f"\"margin_usage\":{result.exposure.margin_usage if result.exposure else 0},"
        "\"offline_only\":true,"
        "\"simulated_only\":true"
        "}"
    )


def build_simulated_broker_stub_v1(
    data: SimulatedBrokerStubV1Input | Mapping[str, Any] | None = None,
) -> SimulatedBrokerStubV1Result:
    data = _coerce_input(data)
    account = build_simulated_broker_account_snapshot_v1(data) if data is not None else None
    position = build_simulated_broker_position_snapshot_v1(data) if data is not None else None
    limits = _build_limits(data) if data is not None else None
    preview = simulate_broker_read_only_order_preview_v1(data) if data is not None else None
    rejection = simulate_broker_rejection_v1() if data is not None else None
    exposure = compute_simulated_broker_exposure_v1(account, position, preview, data) if account and position and preview else None
    acceptance = simulate_broker_acceptance_preview_v1(account, position, preview, limits, exposure) if account and position and preview and limits and exposure else None
    journal_entries = generate_simulated_broker_journal_entries_v1(account, position, preview, rejection, acceptance, exposure, data) if account and position and preview and rejection and acceptance and exposure else ()
    metrics = compute_simulated_broker_stub_v1_metrics(preview, rejection, acceptance, exposure, data) if preview and rejection and acceptance and exposure else None
    risks = detect_simulated_broker_stub_v1_risks(data, account, position, limits, preview, exposure, journal_entries, metrics)
    score = _build_score(data, account, position, limits, exposure, journal_entries, metrics, risks)
    recommendations = generate_simulated_broker_stub_v1_recommendations(risks)
    result = SimulatedBrokerStubV1Result(
        state=_state_for(risks, score),
        decision=_decision_for(risks),
        score=score,
        risks=risks,
        recommendations=recommendations,
        account_snapshot=account,
        position_snapshot=position,
        limits=limits,
        order_preview=preview,
        rejection=rejection,
        acceptance_preview=acceptance,
        exposure=exposure,
        journal_entries=journal_entries,
        metrics=metrics,
        report=None,
        offline_only=data is not None and data.offline_mode_enforced,
        simulated_only=data is not None and data.simulated_broker_only,
        real_order_submitted=False,
        real_account_accessed=False,
        position_mutated=False,
        data_accessed=False,
    )
    report = SimulatedBrokerStubV1Report(
        markdown=render_simulated_broker_stub_v1_markdown_report(result),
        json=render_simulated_broker_stub_v1_json_report(result),
    )
    return SimulatedBrokerStubV1Result(**{**result.__dict__, "report": report})


__all__ = [
    "build_simulated_broker_stub_v1",
    "validate_simulated_broker_stub_v1_input",
    "build_simulated_broker_account_snapshot_v1",
    "build_simulated_broker_position_snapshot_v1",
    "validate_simulated_broker_account_snapshot_v1",
    "validate_simulated_broker_position_snapshot_v1",
    "simulate_broker_read_only_order_preview_v1",
    "simulate_broker_rejection_v1",
    "simulate_broker_acceptance_preview_v1",
    "compute_simulated_broker_exposure_v1",
    "compute_simulated_broker_available_cash_v1",
    "compute_simulated_broker_margin_usage_v1",
    "apply_simulated_broker_limits_v1",
    "generate_simulated_broker_journal_entries_v1",
    "compute_simulated_broker_stub_v1_metrics",
    "detect_simulated_broker_stub_v1_risks",
    "generate_simulated_broker_stub_v1_recommendations",
    "render_simulated_broker_stub_v1_markdown_report",
    "render_simulated_broker_stub_v1_json_report",
    "assert_simulated_broker_stub_v1_offline_boundaries",
]
