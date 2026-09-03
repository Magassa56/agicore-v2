from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta

import pytest

from agicore.agents.execution_agent import ExecutionAgent
from agicore.l5_action.broker_mock import MockBroker
from agicore.l5_action.broker_models import OrderRequest, OrderSide, OrderStatus, OrderType
from agicore.l5_action.execution_service import (
    CanonicalL5CancellationRequest,
    CanonicalL5ExecutionRequest,
    CanonicalL5LimitFillRequest,
    ExecutionService,
    L5CanonicalExecutionError,
    L5RiskGateRequiredError,
)
from agicore.l5_action.execution_transaction import (
    L5ExecutionTransactionError,
    L5ExecutionTransactionStore,
    replay_execution_transaction_journal,
)
from agicore.risk.exposure_models import ExecutionIntent, IntentSide, RiskLimits, empty_snapshot
from agicore.risk.risk_execution_context import InMemoryRiskContextProvider, RiskExecutionContext
from agicore.risk.risk_manager import RiskManager

NOW = datetime(2026, 8, 15, 9, 0, tzinfo=UTC)


class CountingRiskManager(RiskManager):
    def __init__(self, limits: RiskLimits) -> None:
        super().__init__(limits)
        self.calls = 0

    def validate(self, intent, snapshot):
        self.calls += 1
        return super().validate(intent, snapshot)


def _context(
    *,
    execution_enabled: bool = True,
    max_position: float = 10.0,
    max_exposure: float = 1_000_000.0,
) -> RiskExecutionContext:
    limits = RiskLimits(
        max_position_size=max_position,
        max_exposure_value=max_exposure,
        max_drawdown_pct=0.25,
        daily_loss_limit=2_000.0,
    )
    snapshot = empty_snapshot(initial_equity=10_000.0)
    return RiskExecutionContext(
        provider_id="canonical-l5",
        state_version=0,
        trading_day="2026-08-15",
        risk_limits=limits,
        exposure_snapshot=snapshot,
        signed_positions={"ES": 0.0},
        daily_realized_pnl=0.0,
        current_equity=10_000.0,
        peak_equity=10_000.0,
        execution_enabled=execution_enabled,
        kill_switch_active=False,
        legacy_hard_deny=False,
    )


def _service(**context_kwargs):
    context = _context(**context_kwargs)
    seed = InMemoryRiskContextProvider(context)
    price_provider = MockBroker(provider_id="canonical-l5-price")
    price_provider.set_market_price("ES", 100.0, observed_at=NOW)
    store = L5ExecutionTransactionStore(
        initial_context=context,
        initial_risk_journal=seed.journal,
        price_provider=price_provider,
    )
    manager = CountingRiskManager(context.risk_limits)
    return ExecutionService(store, manager, price_provider), store, manager


def _intent(intent_id: str, *, side: IntentSide = IntentSide.BUY, price: float = 100.0) -> ExecutionIntent:
    return ExecutionIntent(
        intent_id=intent_id,
        symbol="ES",
        side=side,
        quantity=1.0,
        estimated_price=price,
        timestamp=NOW,
    )


def _market(intent_id: str = "intent-market", *, side: IntentSide = IntentSide.BUY, price: float = 100.0):
    suffix = intent_id.replace("intent-", "")
    return CanonicalL5ExecutionRequest(
        intent=_intent(intent_id, side=side, price=price),
        order_type=OrderType.MARKET,
        operation_id=f"operation-{suffix}",
        order_id=f"order-{suffix}",
        report_id=f"report-{suffix}",
        submitted_at=NOW,
        fill_id=f"fill-{suffix}",
        filled_at=NOW + timedelta(seconds=1),
    )


def test_market_requires_one_risk_evaluation_and_commits_one_fill() -> None:
    service, store, manager = _service()
    before = store.state
    result = service.execute(_market())
    after = store.state
    assert manager.calls == 1
    assert result.committed and result.status == OrderStatus.FILLED
    assert len(service.consumptions) == 1
    assert len(after.orders) == len(after.fills) == len(after.reports) == 1
    assert after.positions["ES"].quantity == 1.0
    assert after.risk_context.state_version == before.risk_context.state_version + 1
    assert len(after.risk_journal) == len(before.risk_journal) + 2
    replayed, journal_hash = replay_execution_transaction_journal(
        after.execution_journal,
        expected_final_hash=after.execution_journal[-1].event_hash,
    )
    assert replayed == after
    assert journal_hash == after.execution_journal[-1].event_hash


def test_blocked_and_guarded_intents_publish_nothing() -> None:
    blocked_service, blocked_store, blocked_manager = _service(max_position=0.0)
    blocked_before = blocked_store.state
    blocked = blocked_service.execute(_market("intent-blocked"))
    assert blocked.status == OrderStatus.REJECTED and not blocked.committed
    assert blocked_manager.calls == 1
    assert blocked_store.state is blocked_before
    assert blocked_service.consumptions == ()

    guarded_service, guarded_store, guarded_manager = _service(execution_enabled=False)
    guarded_before = guarded_store.state
    guarded = guarded_service.execute(_market("intent-disabled"))
    assert guarded.status == OrderStatus.REJECTED and not guarded.committed
    assert guarded_manager.calls == 0
    assert guarded_store.state is guarded_before
    assert guarded_service.consumptions == ()


def test_raw_execution_service_and_mock_broker_apis_fail_closed() -> None:
    service, store, _ = _service()
    before = store.state
    raw = OrderRequest(symbol="ES", side=OrderSide.BUY, quantity=1.0)
    with pytest.raises(L5RiskGateRequiredError):
        service.submit(raw)
    with pytest.raises(L5RiskGateRequiredError):
        service.submit_market_order("ES", OrderSide.BUY, 1.0)
    with pytest.raises(L5RiskGateRequiredError):
        _ = service.broker
    broker = MockBroker()
    broker.set_market_price("ES", 100.0, observed_at=NOW)
    with pytest.raises(L5RiskGateRequiredError):
        broker.submit_order(raw)
    broker.set_market_price("ES", 90.0, observed_at=NOW + timedelta(seconds=1))
    assert broker.get_market_price("ES") == 90.0
    assert broker.get_all_orders() == [] and broker.get_position("ES") is None
    assert store.state is before


def test_limit_placement_and_fill_require_distinct_authorizations() -> None:
    service, store, manager = _service()
    placement = CanonicalL5ExecutionRequest(
        intent=_intent("intent-limit-place", price=99.0),
        order_type=OrderType.LIMIT,
        operation_id="operation-limit-place",
        order_id="order-limit",
        report_id="report-limit-place",
        submitted_at=NOW,
        limit_price=99.0,
    )
    pending = service.execute(placement)
    assert pending.status == OrderStatus.PENDING and pending.committed
    assert manager.calls == 1 and len(service.consumptions) == 1
    assert store.state.fills == {} and store.state.positions == {}
    service.price_provider.set_market_price(
        "ES", 100.0, observed_at=NOW + timedelta(seconds=1)
    )
    ineligible = CanonicalL5LimitFillRequest(
        intent=ExecutionIntent(
            intent_id="intent-limit-ineligible", symbol="ES", side=IntentSide.BUY,
            quantity=1.0, estimated_price=100.0,
            timestamp=NOW + timedelta(seconds=1),
        ),
        order_id="order-limit",
        eligibility_id="eligibility-ineligible",
        operation_id="operation-limit-ineligible",
        fill_id="fill-limit-ineligible",
        report_id="report-limit-ineligible",
        market_price=100.0,
        observed_at=NOW + timedelta(seconds=1),
        filled_at=NOW + timedelta(seconds=2),
    )
    before = store.state
    with pytest.raises(L5CanonicalExecutionError) as exc:
        service.fill_limit(ineligible)
    assert exc.value.code == "LIMIT_NOT_ELIGIBLE"
    assert manager.calls == 1 and store.state is before
    service.price_provider.set_market_price(
        "ES", 98.0, observed_at=NOW + timedelta(seconds=1)
    )
    fill = CanonicalL5LimitFillRequest(
        intent=ExecutionIntent(
            intent_id="intent-limit-fill",
            symbol="ES",
            side=IntentSide.BUY,
            quantity=1.0,
            estimated_price=98.0,
            timestamp=NOW + timedelta(seconds=2),
        ),
        order_id="order-limit",
        eligibility_id="eligibility-fill",
        operation_id="operation-limit-fill",
        fill_id="fill-limit",
        report_id="report-limit-fill",
        market_price=98.0,
        observed_at=NOW + timedelta(seconds=1),
        filled_at=NOW + timedelta(seconds=3),
    )
    result = service.fill_limit(fill)
    assert result.status == OrderStatus.FILLED
    assert manager.calls == 2 and len(service.consumptions) == 2
    assert len(store.state.fills) == 1 and store.state.positions["ES"].quantity == 1.0


def test_limit_cancellation_is_atomic_and_replayable_without_fill() -> None:
    service, store, manager = _service()
    service.execute(CanonicalL5ExecutionRequest(
        intent=_intent("intent-cancel-place", price=99.0), order_type=OrderType.LIMIT,
        operation_id="operation-cancel-place", order_id="order-cancel",
        report_id="report-cancel-place", submitted_at=NOW, limit_price=99.0,
    ))
    risk_context = store.state.risk_context
    result = service.cancel_limit(CanonicalL5CancellationRequest(
        order_id="order-cancel", operation_id="operation-cancel",
        report_id="report-cancel", cancelled_at=NOW + timedelta(seconds=1),
    ))
    assert result.status == OrderStatus.CANCELLED and result.committed
    assert manager.calls == 1
    assert store.state.orders["order-cancel"].cancelled_at == NOW + timedelta(seconds=1)
    assert store.state.fills == {} and store.state.positions == {}
    assert store.state.risk_context == risk_context
    assert store.state.execution_journal[-1].event_type == "LIMIT_CANCELLED"
    replayed, _ = replay_execution_transaction_journal(
        store.state.execution_journal,
        expected_final_hash=store.state.execution_journal[-1].event_hash,
    )
    assert replayed == store.state


def test_consumption_remains_spent_after_publication_failure(monkeypatch) -> None:
    service, store, manager = _service()
    before = store.state
    monkeypatch.setattr(store, "_publish_state", lambda _: (_ for _ in ()).throw(RuntimeError("boom")))
    with pytest.raises(L5ExecutionTransactionError) as exc:
        service.execute(_market("intent-publication-fails"))
    assert exc.value.code == "TRANSACTION_PUBLICATION_FAILED"
    assert store.state is before and len(service.consumptions) == 1 and manager.calls == 1
    with pytest.raises(L5CanonicalExecutionError) as retry:
        service.execute(_market("intent-publication-fails"))
    assert retry.value.code == "INTENT_ALREADY_CONSUMED"
    assert manager.calls == 1 and store.state is before


def test_concurrent_duplicate_intent_returns_one_authoritative_outcome_twice() -> None:
    service, store, manager = _service()
    request = _market("intent-concurrent")

    def run():
        try:
            return service.execute(request)
        except L5CanonicalExecutionError as exc:
            return exc.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(lambda _: run(), range(2)))
    assert all(not isinstance(item, str) and item.committed for item in outcomes)
    assert {item.outcome_hash for item in outcomes} == {outcomes[0].outcome_hash}
    assert sum(item.redelivered for item in outcomes) == 1
    assert manager.calls == 1
    assert len(store.state.orders) == len(store.state.fills) == 1


def test_concurrent_limit_fills_return_one_authoritative_outcome_twice() -> None:
    service, store, manager = _service()
    service.execute(CanonicalL5ExecutionRequest(
        intent=_intent("intent-limit-concurrent-place", price=99.0),
        order_type=OrderType.LIMIT,
        operation_id="operation-limit-concurrent-place",
        order_id="order-limit-concurrent",
        report_id="report-limit-concurrent-place",
        submitted_at=NOW,
        limit_price=99.0,
    ))
    service.price_provider.set_market_price(
        "ES", 98.0, observed_at=NOW + timedelta(seconds=1)
    )
    fill_request = CanonicalL5LimitFillRequest(
        intent=ExecutionIntent(
            intent_id="intent-limit-concurrent-fill",
            symbol="ES",
            side=IntentSide.BUY,
            quantity=1.0,
            estimated_price=98.0,
            timestamp=NOW + timedelta(seconds=2),
        ),
        order_id="order-limit-concurrent",
        eligibility_id="eligibility-limit-concurrent",
        operation_id="operation-limit-concurrent-fill",
        fill_id="fill-limit-concurrent",
        report_id="report-limit-concurrent-fill",
        market_price=98.0,
        observed_at=NOW + timedelta(seconds=1),
        filled_at=NOW + timedelta(seconds=3),
    )

    def run():
        try:
            return service.fill_limit(fill_request)
        except L5CanonicalExecutionError as exc:
            return exc.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(lambda _: run(), range(2)))

    assert all(not isinstance(item, str) and item.committed for item in outcomes)
    assert {item.outcome_hash for item in outcomes} == {outcomes[0].outcome_hash}
    assert sum(item.redelivered for item in outcomes) == 1
    assert manager.calls == 2  # one placement evaluation and one fill evaluation
    assert len(service.consumptions) == 2
    assert len(store.state.orders) == len(store.state.fills) == 1
    assert len(store.state.reports) == 2
    assert store.state.orders["order-limit-concurrent"].status == OrderStatus.FILLED
    assert store.state.positions["ES"].quantity == 1.0


def test_incomplete_task_payload_is_rejected_before_risk_validation() -> None:
    _, _, manager = _service()
    with pytest.raises(L5CanonicalExecutionError) as exc:
        ExecutionAgent._build_execution_request({"symbol": "ES", "side": "BUY", "quantity": 1.0})
    assert exc.value.code == "INVALID_TASK_PAYLOAD"
    assert manager.calls == 0


def test_artificially_low_payload_price_cannot_bypass_exposure_limit() -> None:
    service, store, manager = _service(max_exposure=500.0)
    service.price_provider.set_market_price("ES", 1_000.0, observed_at=NOW)
    before = store.state
    with pytest.raises(L5CanonicalExecutionError) as exc:
        service.execute(_market("intent-low-price", price=1.0))
    assert exc.value.code == "AUTHORIZED_PRICE_MISMATCH"
    assert manager.calls == 0
    assert store.state is before and store.state.orders == {} and store.state.fills == {}
    assert 1_000.0 > store.state.risk_context.risk_limits.max_exposure_value


def test_caller_cannot_fabricate_sell_gain_with_payload_price() -> None:
    service, store, manager = _service()
    service.execute(_market("intent-buy"))
    service.price_provider.set_market_price("ES", 90.0, observed_at=NOW)
    before = store.state
    with pytest.raises(L5CanonicalExecutionError) as exc:
        service.execute(_market("intent-fake-sell", side=IntentSide.SELL, price=1_000.0))
    assert exc.value.code == "AUTHORIZED_PRICE_MISMATCH"
    assert manager.calls == 1
    assert store.state is before
    assert len(store.state.fills) == 1 and store.state.positions["ES"].realized_pnl == 0.0


def test_price_change_after_authorization_spends_consumption_without_fill(monkeypatch) -> None:
    service, store, manager = _service()
    before = store.state
    original = store.prepare_market

    def prepare_then_change_price(**kwargs):
        plan = original(**kwargs)
        service.price_provider.set_market_price(
            "ES", 101.0, observed_at=NOW + timedelta(seconds=1)
        )
        return plan

    monkeypatch.setattr(store, "prepare_market", prepare_then_change_price)
    with pytest.raises(L5ExecutionTransactionError) as exc:
        service.execute(_market("intent-stale-price"))
    assert exc.value.code == "STALE_PRICE_OBSERVATION"
    assert manager.calls == 1 and len(service.consumptions) == 1
    assert store.state is before and store.state.orders == {} and store.state.fills == {}
    with pytest.raises(L5CanonicalExecutionError) as retry:
        service.execute(_market("intent-stale-price"))
    assert retry.value.code == "INTENT_ALREADY_CONSUMED"


def test_price_observation_identity_is_published_and_replayed() -> None:
    service, store, _ = _service()
    result = service.execute(_market("intent-price-audit"))
    event = store.state.execution_journal[-1]
    observation = event.payload["operation_inputs"]["price_observation"]
    assert result.price_provider_id == observation["provider_id"]
    assert result.price_version == observation["price_version"]
    assert result.price_observation_hash == observation["observation_hash"]
    assert result.execution_price == observation["price"] == 100.0
    replayed, _ = replay_execution_transaction_journal(
        store.state.execution_journal,
        expected_final_hash=store.state.execution_journal[-1].event_hash,
    )
    assert replayed == store.state


def test_price_provider_runtime_error_is_controlled_before_risk(monkeypatch) -> None:
    service, store, manager = _service()
    before = store.state
    monkeypatch.setattr(
        service.price_provider,
        "snapshot",
        lambda _symbol: (_ for _ in ()).throw(RuntimeError("provider failed")),
    )
    with pytest.raises(L5CanonicalExecutionError) as exc:
        service.execute(_market("intent-provider-error"))
    assert exc.value.code == "PRICE_PROVIDER_ERROR"
    assert manager.calls == 0 and service.consumptions == () and store.state is before
