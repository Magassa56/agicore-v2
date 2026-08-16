from __future__ import annotations

import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime, timezone

import pytest

from agicore.l5_action.broker_models import OrderStatus
from agicore.l5_action.broker_mock import MockBroker
from agicore.l5_action.execution_transaction import (
    AggregateRiskContextProvider,
    L5ExecutionAggregateState,
    L5ExecutionTransactionError,
    L5ExecutionTransactionEvent,
    L5ExecutionTransactionPlan,
    L5ExecutionTransactionStore,
    L5LimitFillEligibility,
    L5TransactionReport,
    replay_execution_transaction_journal,
    validate_execution_transaction_journal,
)
from agicore.risk.exposure_models import (
    ExecutionIntent,
    ExposureSnapshot,
    IntentSide,
    RiskLimits,
    SymbolExposure,
    empty_snapshot,
)
from agicore.risk.risk_execution_authorization import (
    RiskAuthorizationBoundary,
    RiskAuthorizationConsumption,
    RiskAuthorizationDecision,
    RiskAuthorizationError,
)
from agicore.risk.risk_execution_context import (
    FillTransition,
    InMemoryRiskContextProvider,
    RiskContextError,
    RiskExecutionContext,
    RiskExecutionJournalEvent,
)
from agicore.risk.risk_manager import RiskManager


NOW = datetime(2026, 8, 14, 9, 0, tzinfo=timezone.utc)
LATER = datetime(2026, 8, 14, 9, 1, tzinfo=timezone.utc)
FILLED_AT = datetime(2026, 8, 14, 9, 2, tzinfo=timezone.utc)
AFTER_FILLED = datetime(2026, 8, 14, 9, 3, tzinfo=timezone.utc)


def _canonical_sha256(value: object) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _mutable_json(value: object) -> object:
    if isinstance(value, dict) or hasattr(value, "items"):
        return {str(key): _mutable_json(nested) for key, nested in value.items()}
    if isinstance(value, (list, tuple)):
        return [_mutable_json(item) for item in value]
    return value


def _risk_event_payload(event: RiskExecutionJournalEvent) -> dict[str, object]:
    return {**event.fields_without_hash(), "event_hash": event.event_hash}


def _limits() -> RiskLimits:
    return RiskLimits(
        max_position_size=10.0,
        max_exposure_value=1_000_000.0,
        max_drawdown_pct=0.25,
        daily_loss_limit=2_000.0,
    )


def _context(*, limits: RiskLimits | None = None) -> RiskExecutionContext:
    snapshot = empty_snapshot(initial_equity=10_000.0)
    return RiskExecutionContext(
        provider_id="l5-aggregate",
        state_version=0,
        trading_day="2026-08-14",
        risk_limits=limits or _limits(),
        exposure_snapshot=snapshot,
        signed_positions={"ES": 0.0},
        daily_realized_pnl=0.0,
        current_equity=10_000.0,
        peak_equity=10_000.0,
        execution_enabled=True,
        kill_switch_active=False,
        legacy_hard_deny=False,
    )


def _setup(*, limits: RiskLimits | None = None) -> tuple[L5ExecutionTransactionStore, RiskAuthorizationBoundary]:
    context = _context(limits=limits)
    seed = InMemoryRiskContextProvider(context)
    price_provider = MockBroker(provider_id="transaction-test-price")
    price_provider.set_market_price("ES", 100.0, observed_at=NOW)
    store = L5ExecutionTransactionStore(
        initial_context=context,
        initial_risk_journal=seed.journal,
        price_provider=price_provider,
    )
    boundary = RiskAuthorizationBoundary(RiskManager(context.risk_limits), store.context_provider)
    return store, boundary


def _intent(
    intent_id: str,
    *,
    price: float = 100.0,
    timestamp: datetime = NOW,
    side: IntentSide = IntentSide.BUY,
) -> ExecutionIntent:
    return ExecutionIntent(
        intent_id=intent_id,
        symbol="ES",
        side=side,
        quantity=1.0,
        estimated_price=price,
        timestamp=timestamp,
    )


def _authorize_and_consume(
    store: L5ExecutionTransactionStore,
    boundary: RiskAuthorizationBoundary,
    intent: ExecutionIntent,
) -> tuple[RiskAuthorizationDecision, RiskAuthorizationConsumption]:
    context = store.state.risk_context
    decision = boundary.authorize(
        intent,
        expected_provider_id=context.provider_id,
        expected_context_state_version=context.state_version,
        expected_context_state_hash=context.state_hash,
    )
    assert decision.allowed is True
    return decision, boundary.verify_for_execution(decision, intent)


def _transition(
    intent_id: str,
    fill_id: str,
    *,
    quantity: float = 1.0,
    price: float = 100.0,
    avg_entry_price: float | None = None,
    mark_price: float | None = None,
    realized_pnl: float = 0.0,
    daily_realized_pnl: float | None = None,
) -> FillTransition:
    daily_pnl = realized_pnl if daily_realized_pnl is None else daily_realized_pnl
    current_equity = 10_000.0 + realized_pnl
    peak_equity = max(10_000.0, current_equity)
    snapshot = ExposureSnapshot(
        positions={
            "ES": SymbolExposure(
                symbol="ES",
                quantity=quantity,
                avg_entry_price=price if avg_entry_price is None else avg_entry_price,
                mark_price=price if mark_price is None else mark_price,
            )
        },
        realized_pnl_total=realized_pnl,
        daily_pnl=daily_pnl,
        initial_equity=10_000.0,
        peak_equity=peak_equity,
    )
    return FillTransition(
        intent_id=intent_id,
        fill_id=fill_id,
        signed_positions={"ES": quantity},
        exposure_snapshot=snapshot,
        daily_realized_pnl=daily_pnl,
        current_equity=current_equity,
        expected_peak_equity=peak_equity,
        payload={"source": "synthetic"},
    )


def _sell_transition(
    intent_id: str,
    fill_id: str,
    *,
    realized_pnl: float,
    daily_realized_pnl: float,
) -> FillTransition:
    snapshot = ExposureSnapshot(
        positions={},
        realized_pnl_total=realized_pnl,
        daily_pnl=daily_realized_pnl,
        initial_equity=10_000.0,
        peak_equity=10_000.0,
    )
    return FillTransition(
        intent_id=intent_id,
        fill_id=fill_id,
        signed_positions={"ES": 0.0},
        exposure_snapshot=snapshot,
        daily_realized_pnl=daily_realized_pnl,
        current_equity=10_000.0 + realized_pnl,
        expected_peak_equity=10_000.0,
        payload={"source": "synthetic-sell"},
    )


def _market_plan(
    store: L5ExecutionTransactionStore,
    boundary: RiskAuthorizationBoundary,
    *,
    suffix: str = "one",
    timestamp: datetime = NOW,
    submitted_at: datetime = NOW,
    filled_at: datetime = LATER,
):
    intent = _intent(f"intent-{suffix}", timestamp=timestamp)
    decision, consumption = _authorize_and_consume(store, boundary, intent)
    plan = store.prepare_market(
        boundary=boundary,
        intent=intent,
        consumption=consumption,
        operation_id=f"operation-{suffix}",
        order_id=f"order-{suffix}",
        fill_id=f"fill-{suffix}",
        report_id=f"report-{suffix}",
        submitted_at=submitted_at,
        fill_price=100.0,
        filled_at=filled_at,
        transition=_transition(intent.intent_id, f"fill-{suffix}"),
    )
    return intent, decision, consumption, plan


def _place_limit(
    store: L5ExecutionTransactionStore,
    boundary: RiskAuthorizationBoundary,
    *,
    suffix: str = "limit",
    limit_price: float = 101.0,
):
    intent = _intent(f"intent-place-{suffix}", price=limit_price)
    _, consumption = _authorize_and_consume(store, boundary, intent)
    plan = store.prepare_limit_placement(
        boundary=boundary,
        intent=intent,
        consumption=consumption,
        operation_id=f"operation-place-{suffix}",
        order_id=f"order-{suffix}",
        report_id=f"report-place-{suffix}",
        limit_price=limit_price,
        submitted_at=NOW,
    )
    return intent, consumption, store.commit(plan, boundary=boundary)


def _complete_limit_cycle():
    store, boundary = _setup()
    _place_limit(store, boundary)
    store.price_provider.set_market_price("ES", 100.0, observed_at=LATER)
    eligibility = store.evaluate_limit_eligibility(
        order_id="order-limit",
        eligibility_id="eligibility-limit",
        market_price=100.0,
        observed_at=LATER,
    )
    intent = _intent("intent-fill-limit", timestamp=LATER)
    _, consumption = _authorize_and_consume(store, boundary, intent)
    plan = store.prepare_limit_fill(
        boundary=boundary,
        intent=intent,
        consumption=consumption,
        eligibility=eligibility,
        operation_id="operation-fill-limit",
        fill_id="fill-limit",
        report_id="report-fill-limit",
        filled_at=FILLED_AT,
        transition=_transition(intent.intent_id, "fill-limit"),
    )
    return store, boundary, store.commit(plan, boundary=boundary)


def test_prepare_market_is_side_effect_free() -> None:
    store, boundary = _setup()
    before = store.state

    _, _, consumption, plan = _market_plan(store, boundary)

    assert store.state is before
    assert store.state.state_hash == before.state_hash
    assert store.state.orders == {}
    assert store.state.fills == {}
    assert store.state.risk_context.state_version == 0
    assert len(store.state.risk_journal) == 1
    assert plan.next_state.state_version == 1
    assert consumption in boundary.consumptions


def test_market_commit_publishes_fill_position_context_and_journals_together() -> None:
    store, boundary = _setup()
    before = store.state
    _, _, _, plan = _market_plan(store, boundary)

    after = store.commit(plan, boundary=boundary)

    assert after is store.state
    assert after.state_version == before.state_version + 1
    assert after.orders["order-one"].status == OrderStatus.FILLED
    assert after.fills["fill-one"].order_id == "order-one"
    assert after.positions["ES"].quantity == 1.0
    assert after.risk_context.state_version == before.risk_context.state_version + 1
    assert after.risk_context.signed_positions == {"ES": 1.0}
    assert len(after.risk_journal) == len(before.risk_journal) + 2
    assert [event.event_type for event in after.risk_journal[-2:]] == ["FILL_RECEIVED", "STATE_COMMITTED"]
    assert len(after.execution_journal) == len(before.execution_journal) + 1
    assert after.execution_journal[-1].event_type == "MARKET_COMMITTED"


def test_successful_commit_uses_exactly_one_aggregate_publication(monkeypatch: pytest.MonkeyPatch) -> None:
    store, boundary = _setup()
    _, _, _, plan = _market_plan(store, boundary)
    published = []
    original_publish = store._publish_state

    def record_publication(next_state: object) -> None:
        published.append(next_state)
        original_publish(next_state)

    monkeypatch.setattr(store, "_publish_state", record_publication)
    after = store.commit(plan, boundary=boundary)

    assert published == [after]
    assert store.state is after


def test_blocked_authorization_cannot_prepare_or_mutate_transaction_state() -> None:
    store, boundary = _setup()
    context = store.state.risk_context
    blocked_intent = ExecutionIntent(
        intent_id="intent-blocked",
        symbol="ES",
        side=IntentSide.BUY,
        quantity=11.0,
        estimated_price=100.0,
        timestamp=NOW,
    )
    decision = boundary.authorize(
        blocked_intent,
        expected_provider_id=context.provider_id,
        expected_context_state_version=context.state_version,
        expected_context_state_hash=context.state_hash,
    )

    assert decision.allowed is False
    assert decision.violations
    with pytest.raises(RiskAuthorizationError, match="RISK_AUTHORIZATION_BLOCKED"):
        boundary.verify_for_execution(decision, blocked_intent)
    assert store.state.risk_context is context
    assert not store.state.orders
    assert not store.state.fills


def test_failed_aggregate_cas_publishes_no_second_mutation() -> None:
    store, boundary = _setup()
    _, _, _, first = _market_plan(store, boundary, suffix="first")
    _, _, _, second = _market_plan(store, boundary, suffix="second")
    committed = store.commit(first, boundary=boundary)

    with pytest.raises(L5ExecutionTransactionError, match="STALE_AGGREGATE_STATE"):
        store.commit(second, boundary=boundary)

    assert store.state is committed
    assert set(store.state.orders) == {"order-first"}
    assert set(store.state.fills) == {"fill-first"}
    assert store.state.risk_context.state_version == 1


@pytest.mark.parametrize("interrupt_type", [KeyboardInterrupt, SystemExit])
def test_interruption_before_single_publication_leaves_state_unchanged(
    monkeypatch: pytest.MonkeyPatch,
    interrupt_type: type[BaseException],
) -> None:
    store, boundary = _setup()
    _, _, _, plan = _market_plan(store, boundary)
    before = store.state

    def interrupt(_next_state: object) -> None:
        raise interrupt_type

    monkeypatch.setattr(store, "_publish_state", interrupt)
    with pytest.raises(interrupt_type):
        store.commit(plan, boundary=boundary)

    assert store.state is before
    assert store.state.state_hash == before.state_hash
    assert not store.state.fills


def test_ordinary_publication_error_is_controlled_without_mutation(monkeypatch: pytest.MonkeyPatch) -> None:
    store, boundary = _setup()
    _, _, _, plan = _market_plan(store, boundary)
    before = store.state

    def fail(_next_state: object) -> None:
        raise RuntimeError("synthetic publication failure")

    monkeypatch.setattr(store, "_publish_state", fail)
    with pytest.raises(L5ExecutionTransactionError) as exc_info:
        store.commit(plan, boundary=boundary)

    assert exc_info.value.code == "TRANSACTION_PUBLICATION_FAILED"
    assert store.state is before
    assert not store.state.fills


def test_committing_same_transaction_twice_is_rejected() -> None:
    store, boundary = _setup()
    _, _, _, plan = _market_plan(store, boundary)
    committed = store.commit(plan, boundary=boundary)

    with pytest.raises(L5ExecutionTransactionError, match="TRANSACTION_ALREADY_COMMITTED"):
        store.commit(plan, boundary=boundary)

    assert store.state is committed
    assert len(store.state.fills) == 1


def test_falsified_transaction_plan_is_rejected_without_mutation() -> None:
    store, boundary = _setup()
    _, _, _, plan = _market_plan(store, boundary)
    before = store.state
    falsified = replace(plan, plan_hash="0" * 64)

    with pytest.raises(L5ExecutionTransactionError, match="INVALID_TRANSACTION_PLAN"):
        store.commit(falsified, boundary=boundary)

    assert store.state is before
    assert not store.state.orders
    assert not store.state.fills


def test_concurrent_commits_have_exactly_one_winner() -> None:
    store, boundary = _setup()
    _, _, _, plan = _market_plan(store, boundary)

    def attempt() -> str:
        try:
            store.commit(plan, boundary=boundary)
            return "committed"
        except L5ExecutionTransactionError as exc:
            return exc.code

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _index: attempt(), range(8)))

    assert results.count("committed") == 1
    assert results.count("TRANSACTION_ALREADY_COMMITTED") == 7
    assert len(store.state.orders) == 1
    assert len(store.state.fills) == 1
    assert store.state.risk_context.state_version == 1


def test_same_consumption_cannot_commit_two_limit_placements() -> None:
    store, boundary = _setup()
    intent = _intent("intent-reused-limit")
    _, consumption = _authorize_and_consume(store, boundary, intent)
    first = store.prepare_limit_placement(
        boundary=boundary,
        intent=intent,
        consumption=consumption,
        operation_id="operation-limit-first",
        order_id="order-limit-first",
        report_id="report-limit-first",
        limit_price=100.0,
        submitted_at=NOW,
    )
    second = store.prepare_limit_placement(
        boundary=boundary,
        intent=intent,
        consumption=consumption,
        operation_id="operation-limit-second",
        order_id="order-limit-second",
        report_id="report-limit-second",
        limit_price=100.0,
        submitted_at=NOW,
    )
    committed = store.commit(first, boundary=boundary)

    with pytest.raises(L5ExecutionTransactionError) as exc_info:
        store.commit(second, boundary=boundary)

    assert exc_info.value.code == "RISK_CONSUMPTION_ALREADY_USED"
    assert store.state is committed
    assert set(store.state.orders) == {"order-limit-first"}
    assert len(store.state.reports) == 1
    assert not store.state.fills


def test_limit_consumption_cannot_be_reused_for_market() -> None:
    store, boundary = _setup()
    intent = _intent("intent-cross-operation")
    _, consumption = _authorize_and_consume(store, boundary, intent)
    placement = store.prepare_limit_placement(
        boundary=boundary,
        intent=intent,
        consumption=consumption,
        operation_id="operation-placement",
        order_id="order-placement",
        report_id="report-placement",
        limit_price=100.0,
        submitted_at=NOW,
    )
    placed = store.commit(placement, boundary=boundary)

    with pytest.raises(L5ExecutionTransactionError) as exc_info:
        store.prepare_market(
            boundary=boundary,
            intent=intent,
            consumption=consumption,
            operation_id="operation-market",
            order_id="order-market",
            fill_id="fill-market",
            report_id="report-market",
            submitted_at=NOW,
            fill_price=100.0,
            filled_at=LATER,
            transition=_transition(intent.intent_id, "fill-market"),
        )

    assert exc_info.value.code == "RISK_CONSUMPTION_ALREADY_USED"
    assert store.state is placed
    assert len(store.state.orders) == 1
    assert not store.state.fills


def test_concurrent_distinct_plans_with_same_consumption_have_one_winner() -> None:
    store, boundary = _setup()
    intent = _intent("intent-concurrent-consumption")
    _, consumption = _authorize_and_consume(store, boundary, intent)
    plans = [
        store.prepare_limit_placement(
            boundary=boundary,
            intent=intent,
            consumption=consumption,
            operation_id=f"operation-{index}",
            order_id=f"order-{index}",
            report_id=f"report-{index}",
            limit_price=100.0,
            submitted_at=NOW,
        )
        for index in range(8)
    ]

    def attempt(plan: L5ExecutionTransactionPlan) -> str:
        try:
            store.commit(plan, boundary=boundary)
            return "committed"
        except L5ExecutionTransactionError as exc:
            return exc.code

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(attempt, plans))

    assert results.count("committed") == 1
    assert results.count("RISK_CONSUMPTION_ALREADY_USED") == 7
    assert len(store.state.orders) == 1
    assert len(store.state.reports) == 1
    assert len(store.state.execution_journal) == 2
    assert not store.state.fills


def test_fully_rehashed_semantically_forged_plan_is_rejected() -> None:
    store, boundary = _setup()
    _, _, _, plan = _market_plan(store, boundary)
    before = store.state
    extra_report = L5TransactionReport(
        report_id="report-injected",
        order_id=plan.order_id,
        status=OrderStatus.FILLED,
        occurred_at=plan.filled_at,
        message="injected",
    )
    forged_base = replace(
        plan.next_state,
        reports={**plan.next_state.reports, extra_report.report_id: extra_report},
        execution_journal=before.execution_journal,
    )
    forged_payload = forged_base.components_payload()
    forged_payload["consumption_hash"] = plan.consumption.consumption_hash
    forged_event = L5ExecutionTransactionEvent.create(
        sequence_number=len(before.execution_journal) + 1,
        event_type="MARKET_COMMITTED",
        operation_id=plan.operation_id,
        state_version_before=before.state_version,
        state_hash_before=before.state_hash,
        payload=forged_payload,
        previous_event_hash=before.execution_journal[-1].event_hash,
    )
    forged_state = replace(
        forged_base,
        execution_journal=(*before.execution_journal, forged_event),
    )
    forged_plan = L5ExecutionTransactionPlan._create(
        operation_id=plan.operation_id,
        operation_kind=plan.operation_kind,
        current=before,
        intent=plan.intent,
        order_id=plan.order_id,
        report_id=plan.report_id,
        consumption=plan.consumption,
        next_state=forged_state,
        submitted_at=plan.submitted_at,
        fill_id=plan.fill_id,
        fill_price=plan.fill_price,
        filled_at=plan.filled_at,
        price_observation=plan.price_observation,
        transition=plan.transition,
    )
    assert forged_plan.is_intact()
    assert forged_plan.plan_hash != plan.plan_hash

    with pytest.raises(L5ExecutionTransactionError) as exc_info:
        store.commit(forged_plan, boundary=boundary)

    assert exc_info.value.code == "INVALID_TRANSACTION_SEMANTICS"
    assert store.state is before
    assert not store.state.orders
    assert not store.state.fills


def test_limit_placement_is_pending_without_fill_or_context_mutation() -> None:
    store, boundary = _setup()
    before = store.state

    _, _, after = _place_limit(store, boundary)

    assert after.orders["order-limit"].status == OrderStatus.PENDING
    assert after.fills == {}
    assert after.positions == {}
    assert after.risk_context == before.risk_context
    assert after.risk_journal == before.risk_journal
    assert after.execution_journal[-1].event_type == "LIMIT_PLACED"


def test_limit_trigger_without_fresh_authorization_produces_no_fill() -> None:
    store, boundary = _setup()
    placement_intent, placement_consumption, placed = _place_limit(store, boundary)
    store.price_provider.set_market_price("ES", 100.0, observed_at=LATER)
    eligibility = store.evaluate_limit_eligibility(
        order_id="order-limit",
        eligibility_id="eligibility-limit",
        market_price=100.0,
        observed_at=LATER,
    )

    with pytest.raises(L5ExecutionTransactionError) as exc_info:
        store.prepare_limit_fill(
            boundary=boundary,
            intent=placement_intent,
            consumption=placement_consumption,
            eligibility=eligibility,
            operation_id="operation-fill-limit",
            fill_id="fill-limit",
            report_id="report-fill-limit",
            filled_at=FILLED_AT,
            transition=_transition(placement_intent.intent_id, "fill-limit"),
        )

    assert exc_info.value.code == "RISK_CONSUMPTION_ALREADY_USED"
    assert store.state is placed
    assert not store.state.fills
    assert store.state.risk_context.state_version == 0


def test_limit_with_fresh_authorization_commits_fill_and_context_together() -> None:
    store, boundary = _setup()
    _, _, placed = _place_limit(store, boundary)
    store.price_provider.set_market_price("ES", 100.0, observed_at=LATER)
    eligibility = store.evaluate_limit_eligibility(
        order_id="order-limit",
        eligibility_id="eligibility-limit",
        market_price=100.0,
        observed_at=LATER,
    )
    assert store.state is placed
    assert not store.state.fills
    fill_intent = _intent("intent-fill-limit", timestamp=LATER)
    _, fill_consumption = _authorize_and_consume(store, boundary, fill_intent)
    plan = store.prepare_limit_fill(
        boundary=boundary,
        intent=fill_intent,
        consumption=fill_consumption,
        eligibility=eligibility,
        operation_id="operation-fill-limit",
        fill_id="fill-limit",
        report_id="report-fill-limit",
        filled_at=FILLED_AT,
        transition=_transition(fill_intent.intent_id, "fill-limit"),
    )

    after = store.commit(plan, boundary=boundary)

    assert placed.fills == {}
    assert after.orders["order-limit"].status == OrderStatus.FILLED
    assert after.fills["fill-limit"].intent_id == "intent-fill-limit"
    assert after.positions["ES"].quantity == 1.0
    assert after.risk_context.state_version == 1
    assert [event.event_type for event in after.execution_journal[-2:]] == ["LIMIT_PLACED", "LIMIT_FILLED"]


def test_stale_limit_fill_authorization_produces_zero_target_fill() -> None:
    store, boundary = _setup()
    _place_limit(store, boundary)
    store.price_provider.set_market_price("ES", 100.0, observed_at=LATER)
    eligibility = store.evaluate_limit_eligibility(
        order_id="order-limit",
        eligibility_id="eligibility-limit",
        market_price=100.0,
        observed_at=LATER,
    )
    fill_intent = _intent("intent-fill-limit", timestamp=LATER)
    _, stale_consumption = _authorize_and_consume(store, boundary, fill_intent)

    _, _, _, advance_plan = _market_plan(
        store,
        boundary,
        suffix="advance",
        timestamp=LATER,
        submitted_at=LATER,
        filled_at=FILLED_AT,
    )
    store.commit(advance_plan, boundary=boundary)
    before_failed_fill = store.state

    with pytest.raises(L5ExecutionTransactionError, match="STALE_RISK_CONSUMPTION"):
        store.prepare_limit_fill(
            boundary=boundary,
            intent=fill_intent,
            consumption=stale_consumption,
            eligibility=eligibility,
            operation_id="operation-fill-limit",
            fill_id="fill-limit",
            report_id="report-fill-limit",
            filled_at=FILLED_AT,
            transition=_transition(fill_intent.intent_id, "fill-limit", quantity=2.0),
        )

    assert store.state is before_failed_fill
    assert "fill-limit" not in store.state.fills
    assert store.state.orders["order-limit"].status == OrderStatus.PENDING


def test_market_fill_price_must_equal_authorized_price_even_when_exposure_would_breach() -> None:
    limits = RiskLimits(
        max_position_size=10.0,
        max_exposure_value=150.0,
        max_drawdown_pct=0.25,
        daily_loss_limit=2_000.0,
    )
    store, boundary = _setup(limits=limits)
    intent = _intent("intent-price-bound", price=100.0)
    decision, consumption = _authorize_and_consume(store, boundary, intent)
    before = store.state
    assert decision.allowed is True
    assert intent.quantity * 200.0 > limits.max_exposure_value

    with pytest.raises(L5ExecutionTransactionError) as exc_info:
        store.prepare_market(
            boundary=boundary,
            intent=intent,
            consumption=consumption,
            operation_id="operation-price-bound",
            order_id="order-price-bound",
            fill_id="fill-price-bound",
            report_id="report-price-bound",
            submitted_at=NOW,
            fill_price=200.0,
            filled_at=LATER,
            transition=_transition(intent.intent_id, "fill-price-bound", price=200.0),
        )

    assert exc_info.value.code == "AUTHORIZED_PRICE_MISMATCH"
    assert store.state is before
    assert not store.state.orders
    assert not store.state.fills


def test_limit_fill_price_must_equal_fresh_intent_authorized_price() -> None:
    store, boundary = _setup()
    _place_limit(store, boundary)
    store.price_provider.set_market_price("ES", 100.0, observed_at=LATER)
    eligibility = store.evaluate_limit_eligibility(
        order_id="order-limit",
        eligibility_id="eligibility-price",
        market_price=100.0,
        observed_at=LATER,
    )
    intent = _intent("intent-limit-price", price=99.0, timestamp=LATER)
    _, consumption = _authorize_and_consume(store, boundary, intent)
    before = store.state

    with pytest.raises(L5ExecutionTransactionError) as exc_info:
        store.prepare_limit_fill(
            boundary=boundary,
            intent=intent,
            consumption=consumption,
            eligibility=eligibility,
            operation_id="operation-limit-price",
            fill_id="fill-limit-price",
            report_id="report-limit-price",
            filled_at=FILLED_AT,
            transition=_transition(intent.intent_id, "fill-limit-price"),
        )

    assert exc_info.value.code == "AUTHORIZED_PRICE_MISMATCH"
    assert store.state is before
    assert store.state.orders["order-limit"].status == OrderStatus.PENDING
    assert not store.state.fills


def test_rehashed_false_limit_eligibility_is_rejected_before_prepare() -> None:
    store, boundary = _setup()
    _place_limit(store, boundary, limit_price=99.0)
    store.price_provider.set_market_price("ES", 100.0, observed_at=LATER)
    authoritative = store.evaluate_limit_eligibility(
        order_id="order-limit",
        eligibility_id="eligibility-forged",
        market_price=100.0,
        observed_at=LATER,
    )
    forged_fields = authoritative.fields_without_hash()
    forged_fields["eligible"] = True
    forged = replace(
        authoritative,
        eligible=True,
        eligibility_hash=_canonical_sha256(forged_fields),
    )
    intent = _intent("intent-forged-eligibility", timestamp=LATER)
    _, consumption = _authorize_and_consume(store, boundary, intent)
    before = store.state

    assert authoritative.eligible is False
    assert authoritative.market_price > before.orders["order-limit"].limit_price
    assert forged.eligible is True
    assert forged.is_intact() is True
    assert forged.eligibility_hash == _canonical_sha256(forged.fields_without_hash())

    with pytest.raises(L5ExecutionTransactionError) as exc_info:
        store.prepare_limit_fill(
            boundary=boundary,
            intent=intent,
            consumption=consumption,
            eligibility=forged,
            operation_id="operation-forged-eligibility",
            fill_id="fill-forged-eligibility",
            report_id="report-forged-eligibility",
            filled_at=FILLED_AT,
            transition=_transition(intent.intent_id, "fill-forged-eligibility"),
        )

    assert exc_info.value.code == "INVALID_LIMIT_ELIGIBILITY"
    assert store.state is before
    assert store.state.state_hash == before.state_hash
    assert store.state.orders["order-limit"].status == OrderStatus.PENDING
    assert store.state.fills == {}
    assert store.state.positions == {}
    assert store.state.risk_context == before.risk_context
    assert store.state.risk_journal == before.risk_journal
    assert store.state.execution_journal == before.execution_journal


def test_fill_daily_pnl_without_realized_delta_is_rejected_before_publication() -> None:
    store, boundary = _setup()
    intent = _intent("intent-false-daily-pnl")
    _, consumption = _authorize_and_consume(store, boundary, intent)
    transition = _transition(
        intent.intent_id,
        "fill-false-daily-pnl",
        realized_pnl=0.0,
        daily_realized_pnl=25.0,
    )
    before = store.state

    assert transition.exposure_snapshot.realized_pnl_total == 0.0
    assert transition.daily_realized_pnl == 25.0
    assert transition.exposure_snapshot.daily_pnl == 25.0

    with pytest.raises(L5ExecutionTransactionError) as exc_info:
        store.prepare_market(
            boundary=boundary,
            intent=intent,
            consumption=consumption,
            operation_id="operation-false-daily-pnl",
            order_id="order-false-daily-pnl",
            fill_id="fill-false-daily-pnl",
            report_id="report-false-daily-pnl",
            submitted_at=NOW,
            fill_price=100.0,
            filled_at=LATER,
            transition=transition,
        )

    assert exc_info.value.code == "INVALID_FILL_TRANSITION"
    assert store.state is before
    assert store.state.orders == {}
    assert store.state.fills == {}
    assert store.state.risk_context == before.risk_context
    assert store.state.risk_journal == before.risk_journal
    assert store.state.execution_journal == before.execution_journal


def test_realized_sell_loss_cannot_be_hidden_from_daily_pnl() -> None:
    store, boundary = _setup()
    _, _, _, buy_plan = _market_plan(store, boundary, suffix="daily-loss-buy")
    after_buy = store.commit(buy_plan, boundary=boundary)
    sell_intent = _intent(
        "intent-daily-loss-sell",
        price=90.0,
        timestamp=FILLED_AT,
        side=IntentSide.SELL,
    )
    _, sell_consumption = _authorize_and_consume(store, boundary, sell_intent)
    fraudulent_transition = _sell_transition(
        sell_intent.intent_id,
        "fill-daily-loss-sell",
        realized_pnl=-10.0,
        daily_realized_pnl=0.0,
    )

    assert after_buy.positions["ES"].quantity == 1.0
    assert after_buy.positions["ES"].avg_entry_price == 100.0
    assert fraudulent_transition.exposure_snapshot.realized_pnl_total == -10.0
    assert fraudulent_transition.daily_realized_pnl == 0.0
    assert fraudulent_transition.exposure_snapshot.daily_pnl == 0.0

    store.price_provider.set_market_price("ES", 90.0, observed_at=FILLED_AT)

    with pytest.raises(L5ExecutionTransactionError) as exc_info:
        store.prepare_market(
            boundary=boundary,
            intent=sell_intent,
            consumption=sell_consumption,
            operation_id="operation-daily-loss-sell",
            order_id="order-daily-loss-sell",
            fill_id="fill-daily-loss-sell",
            report_id="report-daily-loss-sell",
            submitted_at=FILLED_AT,
            fill_price=90.0,
            filled_at=AFTER_FILLED,
            transition=fraudulent_transition,
        )

    assert exc_info.value.code == "INVALID_FILL_TRANSITION"
    assert store.state is after_buy
    assert tuple(store.state.fills) == ("fill-daily-loss-buy",)
    assert store.state.positions["ES"].quantity == 1.0
    assert store.state.risk_context.state_version == 1
    assert store.state.risk_context.daily_realized_pnl == 0.0
    assert len(store.state.risk_journal) == len(after_buy.risk_journal)
    assert len(store.state.execution_journal) == len(after_buy.execution_journal)


@pytest.mark.parametrize(
    ("transition_kwargs", "expected_code"),
    [
        ({"mark_price": 99.0}, "INVALID_FILL_TRANSITION"),
        ({"avg_entry_price": 99.0}, "INVALID_TRANSACTION_STATE"),
        ({"quantity": 2.0}, "INVALID_TRANSACTION_STATE"),
        ({"realized_pnl": 5.0}, "INVALID_TRANSACTION_STATE"),
    ],
)
def test_incompatible_fill_transition_is_rejected_without_publication(
    transition_kwargs: dict[str, float],
    expected_code: str,
) -> None:
    store, boundary = _setup()
    intent = _intent("intent-bad-transition")
    _, consumption = _authorize_and_consume(store, boundary, intent)
    before = store.state

    with pytest.raises(L5ExecutionTransactionError) as exc_info:
        store.prepare_market(
            boundary=boundary,
            intent=intent,
            consumption=consumption,
            operation_id="operation-bad-transition",
            order_id="order-bad-transition",
            fill_id="fill-bad-transition",
            report_id="report-bad-transition",
            submitted_at=NOW,
            fill_price=100.0,
            filled_at=LATER,
            transition=_transition(intent.intent_id, "fill-bad-transition", **transition_kwargs),
        )

    assert exc_info.value.code == expected_code
    assert store.state is before
    assert not store.state.orders
    assert not store.state.fills


@pytest.mark.parametrize(
    ("submitted_at", "filled_at"),
    [
        (datetime(2026, 8, 14, 8, 59, tzinfo=timezone.utc), LATER),
        (LATER, NOW),
    ],
)
def test_market_rejects_inverted_chronology(
    submitted_at: datetime,
    filled_at: datetime,
) -> None:
    store, boundary = _setup()
    intent = _intent("intent-market-chronology")
    _, consumption = _authorize_and_consume(store, boundary, intent)
    before = store.state

    with pytest.raises(L5ExecutionTransactionError) as exc_info:
        store.prepare_market(
            boundary=boundary,
            intent=intent,
            consumption=consumption,
            operation_id="operation-market-chronology",
            order_id="order-market-chronology",
            fill_id="fill-market-chronology",
            report_id="report-market-chronology",
            submitted_at=submitted_at,
            fill_price=100.0,
            filled_at=filled_at,
            transition=_transition(intent.intent_id, "fill-market-chronology"),
        )

    assert exc_info.value.code == "INVALID_TRANSACTION_CHRONOLOGY"
    assert store.state is before


def test_limit_rejects_inverted_placement_and_fill_chronology() -> None:
    store, boundary = _setup()
    placement_intent = _intent("intent-limit-chronology")
    _, placement_consumption = _authorize_and_consume(store, boundary, placement_intent)
    before = store.state

    with pytest.raises(L5ExecutionTransactionError) as placement_error:
        store.prepare_limit_placement(
            boundary=boundary,
            intent=placement_intent,
            consumption=placement_consumption,
            operation_id="operation-bad-placement-time",
            order_id="order-bad-placement-time",
            report_id="report-bad-placement-time",
            limit_price=101.0,
            submitted_at=datetime(2026, 8, 14, 8, 59, tzinfo=timezone.utc),
        )
    assert placement_error.value.code == "INVALID_TRANSACTION_CHRONOLOGY"
    assert store.state is before

    _place_limit(store, boundary, suffix="chronology")
    store.price_provider.set_market_price("ES", 100.0, observed_at=LATER)
    eligibility = store.evaluate_limit_eligibility(
        order_id="order-chronology",
        eligibility_id="eligibility-chronology",
        market_price=100.0,
        observed_at=LATER,
    )
    fill_intent = _intent("intent-fill-chronology", timestamp=NOW)
    _, fill_consumption = _authorize_and_consume(store, boundary, fill_intent)
    placed = store.state
    with pytest.raises(L5ExecutionTransactionError) as fill_error:
        store.prepare_limit_fill(
            boundary=boundary,
            intent=fill_intent,
            consumption=fill_consumption,
            eligibility=eligibility,
            operation_id="operation-fill-chronology",
            fill_id="fill-chronology",
            report_id="report-fill-chronology",
            filled_at=FILLED_AT,
            transition=_transition(fill_intent.intent_id, "fill-chronology"),
        )
    assert fill_error.value.code == "INVALID_TRANSACTION_CHRONOLOGY"
    assert store.state is placed
    assert not store.state.fills


@pytest.mark.parametrize("mapping_name", ["orders", "positions", "fills", "reports"])
def test_aggregate_state_rejects_mapping_key_identity_mismatch(mapping_name: str) -> None:
    store, boundary = _setup()
    _, _, _, plan = _market_plan(store, boundary)
    state = plan.next_state
    record = next(iter(getattr(state, mapping_name).values()))

    with pytest.raises(L5ExecutionTransactionError) as exc_info:
        replace(state, **{mapping_name: {"wrong-key": record}})

    assert exc_info.value.code == "INVALID_TRANSACTION_STATE"
    assert not store.state.orders
    assert not store.state.fills


def test_failed_prepare_does_not_release_consumed_authorization() -> None:
    store, boundary = _setup()
    intent = _intent("intent-failed-prepare")
    decision, consumption = _authorize_and_consume(store, boundary, intent)
    before = store.state

    with pytest.raises(L5ExecutionTransactionError, match="FILL_TRANSITION_MISMATCH"):
        store.prepare_market(
            boundary=boundary,
            intent=intent,
            consumption=consumption,
            operation_id="operation-failed",
            order_id="order-failed",
            fill_id="fill-failed",
            report_id="report-failed",
            submitted_at=NOW,
            fill_price=100.0,
            filled_at=LATER,
            transition=_transition(intent.intent_id, "different-fill"),
        )

    with pytest.raises(RiskAuthorizationError) as exc_info:
        boundary.verify_for_execution(decision, intent)
    assert exc_info.value.code == "AUTHORIZATION_ALREADY_CONSUMED"
    assert store.state is before
    assert not store.state.fills


def test_plans_hashes_and_journals_are_fully_deterministic() -> None:
    left_store, left_boundary = _setup()
    right_store, right_boundary = _setup()
    _, _, _, left_plan = _market_plan(left_store, left_boundary)
    _, _, _, right_plan = _market_plan(right_store, right_boundary)

    assert left_plan.plan_hash == right_plan.plan_hash
    assert left_plan.next_state.state_hash == right_plan.next_state.state_hash
    assert left_plan.next_state.execution_journal == right_plan.next_state.execution_journal

    left = left_store.commit(left_plan, boundary=left_boundary)
    right = right_store.commit(right_plan, boundary=right_boundary)
    assert left == right
    assert left.state_hash == right.state_hash


def test_execution_journal_replay_reconstructs_exact_final_state() -> None:
    store, boundary = _setup()
    _, _, _, plan = _market_plan(store, boundary)
    committed = store.commit(plan, boundary=boundary)

    replayed, journal_hash = replay_execution_transaction_journal(
        committed.execution_journal,
        expected_final_hash=committed.execution_journal[-1].event_hash,
    )

    assert len(committed.execution_journal) == 2
    assert replayed == committed
    assert replayed.state_hash == committed.state_hash
    assert journal_hash == committed.execution_journal[-1].event_hash


def test_execution_journal_anchor_detects_truncated_tail() -> None:
    store, boundary = _setup()
    _, _, _, plan = _market_plan(store, boundary)
    events = store.commit(plan, boundary=boundary).execution_journal
    expected_final_hash = events[-1].event_hash

    with pytest.raises(L5ExecutionTransactionError, match="journal final hash differs"):
        replay_execution_transaction_journal(
            events[:-1],
            expected_final_hash=expected_final_hash,
        )


@pytest.mark.parametrize("tamper", ["modified", "removed", "reordered"])
def test_execution_journal_detects_tampering_removal_and_reordering(tamper: str) -> None:
    _, _, committed = _complete_limit_cycle()
    events = committed.execution_journal
    assert len(events) == 3

    if tamper == "modified":
        altered = (*events[:-1], replace(events[-1], event_hash="0" * 64))
    elif tamper == "removed":
        altered = (events[0], events[2])
    else:
        altered = (events[0], events[2], events[1])

    with pytest.raises(L5ExecutionTransactionError, match="INVALID_TRANSACTION_JOURNAL"):
        validate_execution_transaction_journal(altered)


def test_rehashed_event_is_rejected_by_original_final_anchor() -> None:
    _, _, committed = _complete_limit_cycle()
    events = committed.execution_journal
    last = events[-1]
    rehashed = L5ExecutionTransactionEvent.create(
        sequence_number=last.sequence_number,
        event_type="MARKET_COMMITTED",
        operation_id=last.operation_id,
        state_version_before=last.state_version_before,
        state_hash_before=last.state_hash_before,
        payload=last.payload,
        previous_event_hash=last.previous_event_hash,
    )
    altered = (*events[:-1], rehashed)
    assert rehashed.event_hash != last.event_hash

    with pytest.raises(L5ExecutionTransactionError) as exc_info:
        replay_execution_transaction_journal(
            altered,
            expected_final_hash=last.event_hash,
        )

    assert exc_info.value.code == "INVALID_TRANSACTION_JOURNAL"


def test_rehashed_semantically_impossible_event_is_rejected_without_anchor_comparison() -> None:
    _, _, committed = _complete_limit_cycle()
    events = committed.execution_journal
    last = events[-1]
    impossible = L5ExecutionTransactionEvent.create(
        sequence_number=last.sequence_number,
        event_type="MARKET_COMMITTED",
        operation_id=last.operation_id,
        state_version_before=last.state_version_before,
        state_hash_before=last.state_hash_before,
        payload=last.payload,
        previous_event_hash=last.previous_event_hash,
    )

    with pytest.raises(L5ExecutionTransactionError) as exc_info:
        validate_execution_transaction_journal((*events[:-1], impossible))

    assert exc_info.value.code == "INVALID_TRANSACTION_JOURNAL"


def test_replay_rejects_rehashed_economically_false_limit_eligibility() -> None:
    _, _, committed = _complete_limit_cycle()
    events = committed.execution_journal
    last = events[-1]
    payload = _mutable_json(last.payload)
    assert isinstance(payload, dict)
    operation_inputs = payload["operation_inputs"]
    assert isinstance(operation_inputs, dict)
    eligibility = operation_inputs["eligibility"]
    assert isinstance(eligibility, dict)
    eligibility["market_price"] = 102.0
    eligibility["eligible"] = True
    eligibility_fields = {
        key: value
        for key, value in eligibility.items()
        if key != "eligibility_hash"
    }
    eligibility["eligibility_hash"] = _canonical_sha256(eligibility_fields)
    forged_eligibility = L5LimitFillEligibility(
        schema_version=eligibility["schema_version"],
        eligibility_id=eligibility["eligibility_id"],
        order_id=eligibility["order_id"],
        aggregate_state_version=eligibility["aggregate_state_version"],
        aggregate_state_hash=eligibility["aggregate_state_hash"],
        price_observation_hash=eligibility["price_observation_hash"],
        market_price=eligibility["market_price"],
        observed_at=datetime.fromisoformat(eligibility["observed_at"]),
        eligible=eligibility["eligible"],
        eligibility_hash=eligibility["eligibility_hash"],
    )
    forged_event = L5ExecutionTransactionEvent.create(
        sequence_number=last.sequence_number,
        event_type=last.event_type,
        operation_id=last.operation_id,
        state_version_before=last.state_version_before,
        state_hash_before=last.state_hash_before,
        payload=payload,
        previous_event_hash=last.previous_event_hash,
    )

    assert committed.orders["order-limit"].limit_price == 101.0
    assert forged_eligibility.market_price == 102.0
    assert forged_eligibility.eligible is True
    assert forged_eligibility.is_intact() is True
    assert forged_event.event_hash == _canonical_sha256(forged_event.fields_without_hash())

    with pytest.raises(L5ExecutionTransactionError) as exc_info:
        validate_execution_transaction_journal((*events[:-1], forged_event))

    assert exc_info.value.code == "INVALID_LIMIT_ELIGIBILITY"


def test_replay_rejects_rehashed_daily_pnl_unrelated_to_realized_delta() -> None:
    store, boundary = _setup()
    _, _, _, buy_plan = _market_plan(store, boundary, suffix="replay-daily-buy")
    after_buy = store.commit(buy_plan, boundary=boundary)
    sell_intent = _intent(
        "intent-replay-daily-sell",
        price=90.0,
        timestamp=FILLED_AT,
        side=IntentSide.SELL,
    )
    _, sell_consumption = _authorize_and_consume(store, boundary, sell_intent)
    valid_transition = _sell_transition(
        sell_intent.intent_id,
        "fill-replay-daily-sell",
        realized_pnl=-10.0,
        daily_realized_pnl=-10.0,
    )
    store.price_provider.set_market_price("ES", 90.0, observed_at=FILLED_AT)
    sell_plan = store.prepare_market(
        boundary=boundary,
        intent=sell_intent,
        consumption=sell_consumption,
        operation_id="operation-replay-daily-sell",
        order_id="order-replay-daily-sell",
        fill_id="fill-replay-daily-sell",
        report_id="report-replay-daily-sell",
        submitted_at=FILLED_AT,
        fill_price=90.0,
        filled_at=AFTER_FILLED,
        transition=valid_transition,
    )
    committed = store.commit(sell_plan, boundary=boundary)
    assert committed.risk_context.daily_realized_pnl == -10.0

    forged_transition = _sell_transition(
        sell_intent.intent_id,
        "fill-replay-daily-sell",
        realized_pnl=-10.0,
        daily_realized_pnl=0.0,
    )
    before_context = after_buy.risk_context
    forged_context = RiskExecutionContext(
        provider_id=before_context.provider_id,
        state_version=before_context.state_version + 1,
        trading_day=before_context.trading_day,
        risk_limits=before_context.risk_limits,
        exposure_snapshot=forged_transition.exposure_snapshot,
        signed_positions=forged_transition.signed_positions,
        daily_realized_pnl=forged_transition.daily_realized_pnl,
        current_equity=forged_transition.current_equity,
        peak_equity=forged_transition.expected_peak_equity,
        execution_enabled=before_context.execution_enabled,
        kill_switch_active=before_context.kill_switch_active,
        legacy_hard_deny=before_context.legacy_hard_deny,
    )
    prior_risk_journal = after_buy.risk_journal
    forged_fill_event = RiskExecutionJournalEvent.create(
        sequence_number=len(prior_risk_journal) + 1,
        event_type="FILL_RECEIVED",
        provider_id=before_context.provider_id,
        intent_id=sell_intent.intent_id,
        state_version_before=before_context.state_version,
        state_version_after=forged_context.state_version,
        context_hash_before=before_context.state_hash,
        context_hash_after=forged_context.state_hash,
        payload={"transition": forged_transition.canonical()},
        previous_event_hash=prior_risk_journal[-1].event_hash,
    )
    forged_commit_event = RiskExecutionJournalEvent.create(
        sequence_number=len(prior_risk_journal) + 2,
        event_type="STATE_COMMITTED",
        provider_id=before_context.provider_id,
        intent_id=sell_intent.intent_id,
        state_version_before=before_context.state_version,
        state_version_after=forged_context.state_version,
        context_hash_before=before_context.state_hash,
        context_hash_after=forged_context.state_hash,
        payload={"context": forged_context.canonical()},
        previous_event_hash=forged_fill_event.event_hash,
    )
    forged_risk_journal = (*prior_risk_journal, forged_fill_event, forged_commit_event)
    last = committed.execution_journal[-1]
    payload = _mutable_json(last.payload)
    assert isinstance(payload, dict)
    payload["risk_context"] = forged_context.canonical()
    payload["risk_journal"] = [_risk_event_payload(event) for event in forged_risk_journal]
    operation_inputs = payload["operation_inputs"]
    assert isinstance(operation_inputs, dict)
    operation_inputs["transition"] = forged_transition.canonical()
    forged_transaction_event = L5ExecutionTransactionEvent.create(
        sequence_number=last.sequence_number,
        event_type=last.event_type,
        operation_id=last.operation_id,
        state_version_before=last.state_version_before,
        state_hash_before=last.state_hash_before,
        payload=payload,
        previous_event_hash=last.previous_event_hash,
    )

    assert forged_context.exposure_snapshot.realized_pnl_total == -10.0
    assert forged_context.daily_realized_pnl == 0.0
    assert forged_context.exposure_snapshot.daily_pnl == 0.0
    assert forged_transaction_event.event_hash == _canonical_sha256(
        forged_transaction_event.fields_without_hash()
    )

    with pytest.raises(L5ExecutionTransactionError) as exc_info:
        validate_execution_transaction_journal(
            (*committed.execution_journal[:-1], forged_transaction_event)
        )

    assert exc_info.value.code == "INVALID_TRANSACTION_JOURNAL"


def test_duplicate_consumption_hash_in_rehashed_journal_is_rejected() -> None:
    _, _, committed = _complete_limit_cycle()
    events = committed.execution_journal
    placement = events[1]
    last = events[-1]
    payload = dict(last.payload)
    payload["consumption_hash"] = placement.payload["consumption_hash"]
    duplicated = L5ExecutionTransactionEvent.create(
        sequence_number=last.sequence_number,
        event_type=last.event_type,
        operation_id=last.operation_id,
        state_version_before=last.state_version_before,
        state_hash_before=last.state_hash_before,
        payload=payload,
        previous_event_hash=last.previous_event_hash,
    )

    with pytest.raises(L5ExecutionTransactionError) as exc_info:
        validate_execution_transaction_journal((*events[:-1], duplicated))

    assert exc_info.value.code == "INVALID_TRANSACTION_JOURNAL"


def test_aggregate_context_provider_is_read_only() -> None:
    store, _ = _setup()
    provider = store.context_provider
    assert isinstance(provider, AggregateRiskContextProvider)
    before = store.state

    with pytest.raises(RiskContextError, match="TRANSACTION_REQUIRED"):
        provider.commit_fill(0, before.risk_context.state_hash, _transition("intent", "fill"))

    assert store.state is before


def test_plan_event_and_payload_models_reject_malformed_structures() -> None:
    store, boundary = _setup()
    _, _, _, plan = _market_plan(store, boundary)
    event = plan.next_state.execution_journal[-1]

    with pytest.raises(L5ExecutionTransactionError) as operation_error:
        replace(plan, operation_kind="UNSUPPORTED")
    assert operation_error.value.code == "INVALID_TRANSACTION_PLAN"

    with pytest.raises(L5ExecutionTransactionError) as version_error:
        replace(plan, expected_state_version=True)
    assert version_error.value.code == "INVALID_TRANSACTION_PLAN"

    with pytest.raises(L5ExecutionTransactionError) as event_error:
        replace(event, event_type="UNSUPPORTED")
    assert event_error.value.code == "INVALID_TRANSACTION_EVENT"

    with pytest.raises(L5ExecutionTransactionError) as payload_error:
        L5ExecutionTransactionEvent.create(
            sequence_number=2,
            event_type="MARKET_COMMITTED",
            operation_id="operation",
            state_version_before=0,
            state_hash_before=store.state.state_hash,
            payload={1: "non-string-key"},
            previous_event_hash=store.state.execution_journal[-1].event_hash,
        )
    assert payload_error.value.code == "INVALID_TRANSACTION_DATA"


def test_transaction_event_payload_is_deeply_immutable_and_defensively_copied() -> None:
    store, boundary = _setup()
    _, _, _, plan = _market_plan(store, boundary)
    source = {"nested": {"values": [1, 2]}}
    event = L5ExecutionTransactionEvent.create(
        sequence_number=2,
        event_type="MARKET_COMMITTED",
        operation_id="operation-copy",
        state_version_before=0,
        state_hash_before=store.state.state_hash,
        payload=source,
        previous_event_hash=store.state.execution_journal[-1].event_hash,
    )
    original_hash = event.event_hash
    source["nested"]["values"].append(3)

    assert event.payload["nested"]["values"] == (1, 2)
    assert event.event_hash == original_hash
    with pytest.raises(TypeError):
        event.payload["nested"]["new"] = "forbidden"
