from __future__ import annotations

import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from agicore.agents.execution_agent import AGENT_ID, EVT_ORDER_PROCESSED, ExecutionAgent
from agicore.core.events import EventBus
from agicore.l2_memory.schemas.task import TaskRead
from agicore.l5_action.broker_mock import MockBroker
from agicore.l5_action.broker_models import OrderStatus, OrderType
from agicore.l5_action.execution_outbox import (
    L5ExecutionDeliveryError,
    L5ExecutionDeliveryEvent,
    L5ExecutionOutcomeInbox,
    replay_inbox_journal,
)
from agicore.l5_action.execution_service import (
    CanonicalL5CancellationRequest,
    CanonicalL5ExecutionRequest,
    CanonicalL5LimitFillRequest,
    ExecutionService,
    L5CanonicalExecutionError,
)
from agicore.l5_action.execution_transaction import (
    L5ExecutionAuthorityState,
    L5ExecutionTransactionStore,
    replay_l5_execution_delivery_journal,
)
from agicore.risk.exposure_models import ExecutionIntent, IntentSide, RiskLimits, empty_snapshot
from agicore.risk.risk_execution_context import InMemoryRiskContextProvider, RiskExecutionContext
from agicore.risk.risk_manager import RiskManager

NOW = datetime(2026, 8, 16, 9, 0, tzinfo=UTC)


class CountingRiskManager(RiskManager):
    def __init__(self, limits: RiskLimits) -> None:
        super().__init__(limits)
        self.calls = 0

    def validate(self, intent, snapshot):
        self.calls += 1
        return super().validate(intent, snapshot)


class RecordingMemory:
    def __init__(self) -> None:
        self.events: list[dict[str, object]] = []

    def create_event(self, event_type, **kwargs):
        self.events.append({"event_type": event_type, **kwargs})


def _service(*, max_position: float = 10.0):
    limits = RiskLimits(
        max_position_size=max_position,
        max_exposure_value=1_000_000.0,
        max_drawdown_pct=0.5,
        daily_loss_limit=10_000.0,
    )
    snapshot = empty_snapshot(initial_equity=100_000.0)
    context = RiskExecutionContext(
        provider_id="outbox-provider",
        state_version=0,
        trading_day="2026-08-16",
        risk_limits=limits,
        exposure_snapshot=snapshot,
        signed_positions={"ES": 0.0},
        daily_realized_pnl=0.0,
        current_equity=100_000.0,
        peak_equity=100_000.0,
        execution_enabled=True,
        kill_switch_active=False,
        legacy_hard_deny=False,
    )
    seed = InMemoryRiskContextProvider(context)
    prices = MockBroker(provider_id="outbox-price")
    prices.set_market_price("ES", 100.0, observed_at=NOW)
    store = L5ExecutionTransactionStore(
        initial_context=context,
        initial_risk_journal=seed.journal,
        price_provider=prices,
    )
    manager = CountingRiskManager(limits)
    return ExecutionService(store, manager, prices), store, manager


def _intent(intent_id: str, *, price: float = 100.0) -> ExecutionIntent:
    return ExecutionIntent(
        intent_id=intent_id,
        symbol="ES",
        side=IntentSide.BUY,
        quantity=1.0,
        estimated_price=price,
        timestamp=NOW,
    )


def _market(suffix: str = "market") -> CanonicalL5ExecutionRequest:
    return CanonicalL5ExecutionRequest(
        intent=_intent(f"intent-{suffix}"),
        order_type=OrderType.MARKET,
        operation_id=f"operation-{suffix}",
        order_id=f"order-{suffix}",
        fill_id=f"fill-{suffix}",
        report_id=f"report-{suffix}",
        submitted_at=NOW,
        filled_at=NOW + timedelta(seconds=1),
    )


def _limit_placement(suffix: str = "limit") -> CanonicalL5ExecutionRequest:
    return CanonicalL5ExecutionRequest(
        intent=_intent(f"intent-{suffix}-placement", price=99.0),
        order_type=OrderType.LIMIT,
        operation_id=f"operation-{suffix}-placement",
        order_id=f"order-{suffix}",
        report_id=f"report-{suffix}-placement",
        submitted_at=NOW,
        limit_price=99.0,
    )


def _limit_fill(suffix: str = "limit") -> CanonicalL5LimitFillRequest:
    return CanonicalL5LimitFillRequest(
        intent=ExecutionIntent(
            intent_id=f"intent-{suffix}-fill",
            symbol="ES",
            side=IntentSide.BUY,
            quantity=1.0,
            estimated_price=98.0,
            timestamp=NOW + timedelta(seconds=2),
        ),
        order_id=f"order-{suffix}",
        eligibility_id=f"eligibility-{suffix}",
        operation_id=f"operation-{suffix}-fill",
        fill_id=f"fill-{suffix}",
        report_id=f"report-{suffix}-fill",
        market_price=98.0,
        observed_at=NOW + timedelta(seconds=1),
        filled_at=NOW + timedelta(seconds=3),
    )


def _task(task_id: str, request: CanonicalL5ExecutionRequest) -> TaskRead:
    payload = {
        "intent_id": request.intent.intent_id,
        "symbol": request.intent.symbol,
        "side": request.intent.side.value,
        "quantity": request.intent.quantity,
        "estimated_price": request.intent.estimated_price,
        "timestamp": request.intent.timestamp.isoformat(),
        "order_type": request.order_type.value,
        "operation_id": request.operation_id,
        "order_id": request.order_id,
        "fill_id": request.fill_id,
        "report_id": request.report_id,
        "submitted_at": request.submitted_at.isoformat(),
        "filled_at": request.filled_at.isoformat(),
    }
    return TaskRead(
        id=task_id,
        task_type="execution.order",
        status="running",
        assigned_to=None,
        payload=payload,
        result=None,
        error=None,
        created_at=NOW,
        updated_at=NOW,
    )


def _hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def test_result_and_outbox_publish_with_the_same_aggregate_assignment(monkeypatch) -> None:
    service, store, manager = _service()
    publications: list[object] = []
    original = store._publish_state

    def record(publication):
        publications.append(publication)
        original(publication)

    monkeypatch.setattr(store, "_publish_state", record)
    result = service.execute(_market("atomic"))
    assert len(publications) == 1
    assert isinstance(publications[0], L5ExecutionAuthorityState)
    assert result.outcome_id in store.delivery_state.outcomes
    assert len(store.state.orders) == len(store.state.fills) == 1
    assert manager.calls == 1


def test_duplicate_market_redelivers_without_risk_consumption_or_fill() -> None:
    service, store, manager = _service()
    first = service.execute(_market("duplicate"))
    before_context = store.state.risk_context
    before_journal = store.state.risk_journal
    second = service.execute(_market("duplicate"))
    assert first.outcome == second.outcome and second.redelivered
    assert manager.calls == 1 and len(service.consumptions) == 1
    assert len(store.state.orders) == len(store.state.fills) == 1
    assert store.state.risk_context == before_context and store.state.risk_journal == before_journal


def test_same_intent_with_different_payload_is_a_stable_conflict() -> None:
    service, store, manager = _service()
    service.execute(_market("conflict"))
    changed = replace(_market("conflict"), filled_at=NOW + timedelta(seconds=2))
    before = store.authority_state
    with pytest.raises(L5CanonicalExecutionError) as exc:
        service.execute(changed)
    assert exc.value.code == "INTENT_OUTCOME_CONFLICT"
    assert manager.calls == 1 and store.authority_state is before


def test_limit_placement_redelivery_creates_no_second_order() -> None:
    service, store, manager = _service()
    first = service.execute(_limit_placement("place"))
    second = service.execute(_limit_placement("place"))
    assert first.outcome_hash == second.outcome_hash and second.redelivered
    assert manager.calls == 1 and len(store.state.orders) == 1 and store.state.fills == {}


def test_limit_fill_redelivery_creates_no_second_fill() -> None:
    service, store, manager = _service()
    service.execute(_limit_placement("fill"))
    service.price_provider.set_market_price("ES", 98.0, observed_at=NOW + timedelta(seconds=1))
    first = service.fill_limit(_limit_fill("fill"))
    second = service.fill_limit(_limit_fill("fill"))
    assert first.outcome_hash == second.outcome_hash and second.redelivered
    assert manager.calls == 2 and len(store.state.fills) == 1


def test_limit_cancellation_redelivery_creates_no_second_effect() -> None:
    service, store, manager = _service()
    service.execute(_limit_placement("cancel"))
    request = CanonicalL5CancellationRequest(
        order_id="order-cancel",
        operation_id="operation-cancel",
        report_id="report-cancel",
        cancelled_at=NOW + timedelta(seconds=1),
    )
    first = service.cancel_limit(request)
    before = store.state
    second = service.cancel_limit(request)
    assert first.outcome_hash == second.outcome_hash and second.redelivered
    assert store.state is before and manager.calls == 1
    assert len(store.state.reports) == 2 and store.state.fills == {}


def test_risk_rejection_is_redelivered_without_second_violation_or_order() -> None:
    service, store, manager = _service(max_position=0.0)
    first = service.execute(_market("rejected"))
    second = service.execute(_market("rejected"))
    assert first.status == OrderStatus.REJECTED and first.outcome == second.outcome
    assert second.redelivered and manager.calls == 1 and service.consumptions == ()
    assert store.state.orders == {} and store.state.fills == {} and store.state.positions == {}
    assert len(store.delivery_state.outcomes) == 1


def test_rejected_outcome_is_observed_once_by_the_canonical_consumer() -> None:
    service, store, manager = _service(max_position=0.0)
    memory = RecordingMemory()
    bus = EventBus()
    observed = []
    bus.subscribe(EVT_ORDER_PROCESSED, observed.append)
    agent = ExecutionAgent(service, memory, bus)
    request = _market("rejection-observable")
    first = agent(_task("task-rejection-1", request))
    second = agent(_task("task-rejection-2", request))
    assert first["order_status"] == second["order_status"] == "REJECTED"
    assert second["redelivered"] is True
    assert len(memory.events) == len(observed) == 1
    assert manager.calls == 1 and store.state.orders == {} and store.state.fills == {}


def test_delivery_failure_leaves_outbox_pending() -> None:
    service, store, _ = _service()
    outcome = service.execute(_market("pending-delivery")).outcome
    assert service.pending_outcomes(AGENT_ID) == (outcome,)
    assert store.delivery_state.acknowledgements == {}


def test_lost_ack_then_redelivery_has_one_consumer_effect(monkeypatch) -> None:
    service, _, manager = _service()
    memory = RecordingMemory()
    bus = EventBus()
    observed = []
    bus.subscribe(EVT_ORDER_PROCESSED, observed.append)
    agent = ExecutionAgent(service, memory, bus)
    request = _market("ack-lost")
    original = service.acknowledge_outcome
    calls = 0

    def lose_once(receipt, inbox):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise L5CanonicalExecutionError("ACK_LOST", "simulated acknowledgement loss")
        return original(receipt, inbox)

    monkeypatch.setattr(service, "acknowledge_outcome", lose_once)
    with pytest.raises(L5CanonicalExecutionError, match="ACK_LOST"):
        agent(_task("task-ack-lost-1", request))
    assert len(memory.events) == len(observed) == 1
    assert len(service.pending_outcomes(AGENT_ID)) == 1
    feedback = agent(_task("task-ack-lost-2", request))
    assert feedback["redelivered"] is True
    assert len(memory.events) == len(observed) == 1 and agent.processed_count == 1
    assert service.pending_outcomes(AGENT_ID) == () and manager.calls == 1


def test_repeated_identical_acknowledgement_is_idempotent() -> None:
    service, store, _ = _service()
    outcome = service.execute(_market("ack-repeat")).outcome
    inbox = L5ExecutionOutcomeInbox("consumer-a")
    receipt = inbox.accept(outcome).receipt
    first = service.acknowledge_outcome(receipt, inbox)
    version = store.delivery_state.delivery_version
    second = service.acknowledge_outcome(receipt, inbox)
    assert first == second and store.delivery_state.delivery_version == version
    assert len(store.delivery_state.acknowledgements) == 1


def test_falsified_or_wrong_consumer_acknowledgement_is_rejected() -> None:
    service, store, _ = _service()
    outcome = service.execute(_market("ack-invalid")).outcome
    left = L5ExecutionOutcomeInbox("consumer-left")
    right = L5ExecutionOutcomeInbox("consumer-right")
    receipt = left.accept(outcome).receipt
    before = store.authority_state
    with pytest.raises(L5CanonicalExecutionError) as wrong:
        service.acknowledge_outcome(receipt, right)
    assert wrong.value.code == "UNISSUED_RECEIPT"
    forged = replace(receipt, outcome_hash="0" * 64)
    with pytest.raises(L5CanonicalExecutionError) as invalid:
        service.acknowledge_outcome(forged, left)
    assert invalid.value.code == "INVALID_RECEIPT"
    assert store.authority_state is before


def test_inbox_rejects_same_outcome_id_with_different_rehashed_payload() -> None:
    service, _, _ = _service()
    outcome = service.execute(_market("inbox-conflict")).outcome
    inbox = L5ExecutionOutcomeInbox("consumer-inbox-conflict")
    inbox.accept(outcome)
    forged_fields = outcome.fields_without_hash()
    forged_fields["order_id"] = "order-conflicting-payload"
    forged = replace(
        outcome,
        order_id="order-conflicting-payload",
        outcome_hash=_hash(forged_fields),
    )
    assert forged.outcome_id == outcome.outcome_id and forged.is_intact()
    before = inbox.state
    with pytest.raises(L5ExecutionDeliveryError) as exc:
        inbox.accept(forged)
    assert exc.value.code == "OUTCOME_IDENTITY_CONFLICT"
    assert inbox.state is before and len(inbox.receipts) == 1


def test_concurrent_same_intent_has_one_risk_one_commit_one_outcome() -> None:
    service, store, manager = _service()
    request = _market("concurrent")
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: service.execute(request), range(8)))
    assert len({result.outcome_hash for result in results}) == 1
    assert sum(not result.redelivered for result in results) == 1
    assert manager.calls == 1 and len(service.consumptions) == 1
    assert len(store.state.fills) == len(store.delivery_state.outcomes) == 1


def test_concurrent_inbox_accept_and_ack_publish_once() -> None:
    service, store, _ = _service()
    outcome = service.execute(_market("concurrent-delivery")).outcome
    inbox = L5ExecutionOutcomeInbox("consumer-concurrent")
    with ThreadPoolExecutor(max_workers=8) as pool:
        acceptances = list(pool.map(lambda _: inbox.accept(outcome), range(8)))
    assert sum(item.accepted_new for item in acceptances) == 1
    assert len(inbox.receipts) == 1
    receipt = acceptances[0].receipt
    with ThreadPoolExecutor(max_workers=8) as pool:
        acknowledgements = list(pool.map(lambda _: service.acknowledge_outcome(receipt, inbox), range(8)))
    assert len({item.acknowledgement_hash for item in acknowledgements}) == 1
    assert len(store.delivery_state.acknowledgements) == 1


@pytest.mark.parametrize("interrupt", [KeyboardInterrupt, SystemExit, MemoryError])
def test_interruption_before_inbox_receipt_publication_changes_nothing(monkeypatch, interrupt) -> None:
    service, _, _ = _service()
    outcome = service.execute(_market(f"inbox-interrupt-{interrupt.__name__}")).outcome
    inbox = L5ExecutionOutcomeInbox("consumer-inbox-interrupt")
    before = inbox.state
    monkeypatch.setattr(inbox, "_publish_state", lambda _state: (_ for _ in ()).throw(interrupt()))
    with pytest.raises(interrupt):
        inbox.accept(outcome)
    assert inbox.state is before and inbox.receipts == ()
    assert service.pending_outcomes("consumer-inbox-interrupt") == (outcome,)


@pytest.mark.parametrize("interrupt", [KeyboardInterrupt, SystemExit, MemoryError])
def test_interruption_before_ack_publication_leaves_pending_and_retryable(monkeypatch, interrupt) -> None:
    service, store, _ = _service()
    outcome = service.execute(_market(f"ack-interrupt-{interrupt.__name__}")).outcome
    inbox = L5ExecutionOutcomeInbox("consumer-ack-interrupt")
    receipt = inbox.accept(outcome).receipt
    before = store.authority_state
    original = store._publish_state
    monkeypatch.setattr(store, "_publish_state", lambda _state: (_ for _ in ()).throw(interrupt()))
    with pytest.raises(interrupt):
        service.acknowledge_outcome(receipt, inbox)
    assert store.authority_state is before
    assert service.pending_outcomes("consumer-ack-interrupt") == (outcome,)
    monkeypatch.setattr(store, "_publish_state", original)
    service.acknowledge_outcome(receipt, inbox)
    assert service.pending_outcomes("consumer-ack-interrupt") == ()


@pytest.mark.parametrize("interrupt", [KeyboardInterrupt, SystemExit, MemoryError])
def test_interruption_before_authority_publication_has_no_partial_state(monkeypatch, interrupt) -> None:
    service, store, manager = _service()
    before = store.authority_state
    monkeypatch.setattr(store, "_publish_state", lambda _state: (_ for _ in ()).throw(interrupt()))
    with pytest.raises(interrupt):
        service.execute(_market(f"interrupt-{interrupt.__name__}"))
    assert store.authority_state is before
    assert store.state.orders == {} and store.delivery_state.outcomes == {}
    assert manager.calls == 1 and len(service.consumptions) == 1


def test_delivery_ack_and_redelivery_do_not_change_risk_context_or_journal() -> None:
    service, store, manager = _service()
    request = _market("risk-static")
    outcome = service.execute(request).outcome
    context = store.state.risk_context
    journal = store.state.risk_journal
    inbox = L5ExecutionOutcomeInbox("consumer-risk-static")
    receipt = inbox.accept(outcome).receipt
    service.acknowledge_outcome(receipt, inbox)
    service.execute(request)
    assert store.state.risk_context == context and store.state.risk_journal == journal
    assert manager.calls == 1


def test_delivery_and_inbox_replay_reconstruct_exact_states_without_risk_call() -> None:
    service, store, manager = _service()
    outcome = service.execute(_market("replay")).outcome
    inbox = L5ExecutionOutcomeInbox("consumer-replay")
    receipt = inbox.accept(outcome).receipt
    service.acknowledge_outcome(receipt, inbox)
    calls = manager.calls
    replayed_inbox, inbox_hash = replay_inbox_journal(
        inbox.state.journal,
        expected_final_hash=inbox.state.journal[-1].event_hash,
    )
    replayed_delivery, delivery_hash = replay_l5_execution_delivery_journal(
        store.delivery_state.journal,
        execution_events=store.state.execution_journal,
        expected_final_hash=store.delivery_state.journal[-1].event_hash,
        inbox_events=inbox.state.journal,
        expected_inbox_hash=inbox.state.journal[-1].event_hash,
    )
    assert replayed_inbox == inbox.state and replayed_delivery == store.delivery_state
    assert inbox_hash == inbox.state.journal[-1].event_hash
    assert delivery_hash == store.delivery_state.journal[-1].event_hash
    assert manager.calls == calls


def test_delivery_replay_rejects_truncation_with_original_anchor() -> None:
    service, store, _ = _service()
    service.execute(_market("truncate"))
    inbox = L5ExecutionOutcomeInbox("consumer-empty")
    with pytest.raises(L5ExecutionDeliveryError, match="final hash"):
        replay_l5_execution_delivery_journal(
            store.delivery_state.journal[:-1],
            execution_events=store.state.execution_journal,
            expected_final_hash=store.delivery_state.journal[-1].event_hash,
            inbox_events=inbox.state.journal,
            expected_inbox_hash=inbox.state.journal[-1].event_hash,
        )


def test_delivery_replay_rejects_acknowledgement_without_prior_inbox_acceptance() -> None:
    service, store, _ = _service()
    outcome = service.execute(_market("orphan-ack")).outcome
    accepted = L5ExecutionOutcomeInbox("consumer-orphan")
    receipt = accepted.accept(outcome).receipt
    service.acknowledge_outcome(receipt, accepted)
    empty = L5ExecutionOutcomeInbox("consumer-empty")
    with pytest.raises(L5ExecutionDeliveryError, match="prior inbox acceptance"):
        replay_l5_execution_delivery_journal(
            store.delivery_state.journal,
            execution_events=store.state.execution_journal,
            expected_final_hash=store.delivery_state.journal[-1].event_hash,
            inbox_events=empty.state.journal,
            expected_inbox_hash=empty.state.journal[-1].event_hash,
        )


@pytest.mark.parametrize("mutation", ["tamper", "remove", "duplicate", "reorder"])
def test_delivery_replay_rejects_tamper_removal_duplication_and_reordering(mutation) -> None:
    service, store, _ = _service()
    service.execute(_market("journal-a"))
    service.execute(_market("journal-b"))
    events = list(store.delivery_state.journal)
    if mutation == "tamper":
        events[-1] = replace(events[-1], event_hash="0" * 64)
    elif mutation == "remove":
        events.pop(1)
    elif mutation == "duplicate":
        events.append(events[-1])
    else:
        events[1], events[2] = events[2], events[1]
    inbox = L5ExecutionOutcomeInbox("consumer-empty")
    with pytest.raises(L5ExecutionDeliveryError):
        replay_l5_execution_delivery_journal(
            tuple(events),
            execution_events=store.state.execution_journal,
            expected_final_hash=events[-1].event_hash,
            inbox_events=inbox.state.journal,
            expected_inbox_hash=inbox.state.journal[-1].event_hash,
        )


def test_rehashed_economically_impossible_outcome_is_rejected_semantically() -> None:
    service, store, _ = _service()
    outcome = service.execute(_market("semantic-forgery")).outcome
    impossible_fields = outcome.fields_without_hash()
    impossible_fields["order_id"] = "order-forged-but-well-formed"
    impossible = replace(
        outcome,
        order_id="order-forged-but-well-formed",
        outcome_hash=_hash(impossible_fields),
    )
    assert impossible.is_intact()
    event = L5ExecutionDeliveryEvent.create(
        sequence_number=2,
        event_type="OUTCOME_PUBLISHED",
        delivery_version_before=0,
        delivery_hash_before=store.delivery_state.journal[1].delivery_hash_before,
        payload={"outcome": impossible.canonical()},
        previous_event_hash=store.delivery_state.journal[0].event_hash,
    )
    inbox = L5ExecutionOutcomeInbox("consumer-empty")
    with pytest.raises(L5ExecutionDeliveryError, match="authoritative transaction"):
        replay_l5_execution_delivery_journal(
            (store.delivery_state.journal[0], event),
            execution_events=store.state.execution_journal,
            expected_final_hash=event.event_hash,
            inbox_events=inbox.state.journal,
            expected_inbox_hash=inbox.state.journal[-1].event_hash,
        )


def test_outcome_and_receipt_payloads_are_deeply_immutable_and_intact() -> None:
    service, _, _ = _service()
    outcome = service.execute(_market("immutable")).outcome
    inbox = L5ExecutionOutcomeInbox("consumer-immutable")
    acceptance = inbox.accept(outcome)
    assert outcome.is_intact() and acceptance.receipt.is_intact()
    with pytest.raises(TypeError):
        outcome.request_payload["intent"] = {}
    with pytest.raises(TypeError):
        inbox.state.outcome_hashes[outcome.outcome_id] = "0" * 64
    assert outcome.is_intact() and acceptance.receipt.is_intact()


def test_no_implicit_nondeterministic_identity_fields_are_published() -> None:
    service, store, _ = _service()
    outcome = service.execute(_market("deterministic")).outcome
    forbidden = {"uuid", "nonce", "random", "generated_at", "created_at"}

    def keys(value):
        if isinstance(value, dict):
            return set(value) | set().union(*(keys(item) for item in value.values()))
        if isinstance(value, list):
            return set().union(*(keys(item) for item in value), set())
        return set()

    assert not (keys(outcome.canonical()) & forbidden)
    assert not (keys(store.delivery_state.journal[-1].canonical()) & forbidden)


def test_identical_inputs_produce_identical_outcomes_and_delivery_journals() -> None:
    left_service, left_store, _ = _service()
    right_service, right_store, _ = _service()
    left = left_service.execute(_market("determinism"))
    right = right_service.execute(_market("determinism"))
    assert left.outcome == right.outcome
    assert left_store.delivery_state == right_store.delivery_state
    assert left_store.authority_state.authority_hash == right_store.authority_state.authority_hash


class FailOnceMemory(RecordingMemory):
    def __init__(self) -> None:
        super().__init__()
        self.calls = 0

    def create_event(self, event_type, **kwargs):
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("memory unavailable")
        super().create_event(event_type, **kwargs)


def test_two_services_share_intent_serialization_and_risk_boundary() -> None:
    first, store, manager = _service()
    second = ExecutionService(store, manager, first.price_provider)
    request = _market("two-services")
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = tuple(pool.map(lambda service: service.execute(request), (first, second)))
    assert len({item.outcome_hash for item in results}) == 1
    assert sum(not item.redelivered for item in results) == 1
    assert manager.calls == 1
    assert len(first.consumptions) == 1
    assert len(store.state.orders) == len(store.state.fills) == 1
    assert len(store.delivery_state.outcomes) == 1


def test_two_services_keep_distinct_intents_independent() -> None:
    first, store, manager = _service()
    second = ExecutionService(store, manager, first.price_provider)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = (
            pool.submit(first.execute, _limit_placement("independent-a")),
            pool.submit(second.execute, _limit_placement("independent-b")),
        )
        outcomes = tuple(future.result() for future in results)
    assert all(item.committed for item in outcomes)
    assert manager.calls == 2
    assert len(store.state.orders) == len(store.delivery_state.outcomes) == 2


def test_explicit_missing_outcome_fails_before_authority_mutation(monkeypatch) -> None:
    service, store, manager = _service()
    before = store.authority_state
    original = store.commit

    def without_outcome(plan, *, boundary, outcome_spec):
        return original(plan, boundary=boundary, outcome_spec=None)

    monkeypatch.setattr(store, "commit", without_outcome)
    with pytest.raises(Exception, match="OUTCOME_REQUIRED"):
        service.execute(_market("missing-outcome"))
    assert store.authority_state is before
    assert store.state.orders == store.state.fills == store.state.positions == {}
    assert store.state.reports == {}
    assert store.delivery_state.outcomes == {}
    assert len(store.delivery_state.journal) == 1
    assert manager.calls == 1 and len(service.consumptions) == 1


def test_missing_cancellation_outcome_fails_without_any_mutation(monkeypatch) -> None:
    service, store, _ = _service()
    service.execute(_limit_placement("cancel-no-outcome"))
    request = CanonicalL5CancellationRequest(
        order_id="order-cancel-no-outcome",
        operation_id="operation-cancel-no-outcome",
        report_id="report-cancel-no-outcome",
        cancelled_at=NOW + timedelta(seconds=1),
    )
    before = store.authority_state
    original = store.cancel_limit

    def without_outcome(**kwargs):
        kwargs["outcome_spec"] = None
        return original(**kwargs)

    monkeypatch.setattr(store, "cancel_limit", without_outcome)
    with pytest.raises(Exception, match="OUTCOME_REQUIRED"):
        service.cancel_limit(request)
    assert store.authority_state is before
    assert store.state.orders[request.order_id].status == OrderStatus.PENDING


def test_missing_limit_fill_outcome_fails_without_fill_or_context_mutation(monkeypatch) -> None:
    service, store, _ = _service()
    service.execute(_limit_placement("fill-no-outcome"))
    service.price_provider.set_market_price("ES", 98.0, observed_at=NOW + timedelta(seconds=1))
    before = store.authority_state
    original = store.commit

    def without_outcome(plan, *, boundary, outcome_spec):
        return original(plan, boundary=boundary, outcome_spec=None)

    monkeypatch.setattr(store, "commit", without_outcome)
    with pytest.raises(Exception, match="OUTCOME_REQUIRED"):
        service.fill_limit(_limit_fill("fill-no-outcome"))
    assert store.authority_state is before
    assert store.state.fills == {} and store.state.positions == {}
    assert store.state.risk_context == before.aggregate_state.risk_context


def test_independent_inboxes_for_same_store_consumer_are_rejected() -> None:
    service, _, _ = _service()
    first = L5ExecutionOutcomeInbox("consumer-shared-authority")
    second = L5ExecutionOutcomeInbox("consumer-shared-authority")
    assert service.outcome_inbox(first.consumer_id, first) is first
    with pytest.raises(L5CanonicalExecutionError) as conflict:
        service.outcome_inbox(second.consumer_id, second)
    assert conflict.value.code == "CONSUMER_CONFIGURATION_CONFLICT"


@pytest.mark.parametrize(
    "mutation",
    (
        "other_order", "other_report", "other_fill", "authorized_price",
        "executed_price", "explicit_time", "request_payload", "intent_hash",
        "price_provider", "context_hash", "limits_hash", "decision_evidence",
        "consumption_hash",
    ),
)
def test_supplied_rehashed_outcome_spec_must_equal_authoritative_reconstruction(
    monkeypatch,
    mutation,
) -> None:
    service, store, _ = _service()
    service.execute(_market("existing-semantic"))
    original = store.outcome_spec_for_plan

    def forged(plan, *, boundary):
        spec = original(plan, boundary=boundary)
        if mutation == "other_order":
            return replace(spec, order_id="order-existing-semantic")
        if mutation == "other_report":
            return replace(spec, report_id="report-existing-semantic")
        if mutation == "other_fill":
            return replace(spec, fill_id="fill-existing-semantic")
        if mutation == "authorized_price":
            return replace(spec, authorized_price=101.0)
        if mutation == "executed_price":
            return replace(spec, execution_price=101.0)
        if mutation == "explicit_time":
            return replace(spec, explicit_times={**dict(spec.explicit_times), "filled_at": (NOW + timedelta(seconds=9)).isoformat()})
        if mutation == "request_payload":
            return replace(spec, request_payload={**dict(spec.request_payload), "operation_id": "operation-forged"})
        if mutation == "intent_hash":
            return replace(spec, intent_hash="0" * 64)
        if mutation == "price_provider":
            return replace(spec, price_identity={**dict(spec.price_identity), "provider_id": "forged-price"})
        if mutation == "context_hash":
            return replace(spec, context_state_hash="0" * 64)
        if mutation == "limits_hash":
            return replace(spec, risk_limits_hash="0" * 64)
        if mutation == "decision_evidence":
            return replace(spec, decision_evidence={**dict(spec.decision_evidence), "provider_id": "forged-risk"})
        return replace(spec, consumption_hash="0" * 64)

    monkeypatch.setattr(store, "outcome_spec_for_plan", forged)
    before = store.authority_state
    with pytest.raises(Exception, match="INVALID_OUTCOME_SEMANTICS"):
        service.execute(_market(f"forged-{mutation}"))
    assert store.authority_state is before


def test_memory_failure_after_receipt_retries_only_unfinished_effect() -> None:
    service, store, manager = _service()
    memory = FailOnceMemory()
    agent = ExecutionAgent(service, memory)
    request = _market("memory-retry")
    with pytest.raises(RuntimeError, match="memory unavailable"):
        agent(_task("memory-retry-1", request))
    assert len(agent.outcome_inbox.receipts) == 1
    assert store.delivery_state.acknowledgements == {}
    result = agent(_task("memory-retry-2", request))
    assert result["redelivered"] is True
    assert memory.calls == 2 and len(memory.events) == 1
    assert len(store.delivery_state.acknowledgements) == 1
    assert manager.calls == 1


def test_event_bus_failure_retries_bus_without_repeating_memory(monkeypatch) -> None:
    service, store, _ = _service()
    memory = RecordingMemory()
    bus = EventBus()
    emitted: list[dict[str, object]] = []
    original = bus.emit
    calls = 0

    def fail_once(event_type, **payload):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise RuntimeError("bus unavailable")
        emitted.append(dict(payload))
        return original(event_type, **payload)

    monkeypatch.setattr(bus, "emit", fail_once)
    agent = ExecutionAgent(service, memory, bus)
    request = _market("bus-retry")
    with pytest.raises(RuntimeError, match="bus unavailable"):
        agent(_task("bus-retry-1", request))
    assert len(memory.events) == 1 and store.delivery_state.acknowledgements == {}
    agent(_task("bus-retry-2", request))
    assert len(memory.events) == 1 and len(emitted) == 1 and calls == 2
    assert len(store.delivery_state.acknowledgements) == 1


def test_two_agents_same_consumer_converge_and_concurrent_effects_run_once() -> None:
    service, store, manager = _service()
    memory = RecordingMemory()
    first = ExecutionAgent(service, memory)
    second = ExecutionAgent(service, memory)
    assert first.outcome_inbox is second.outcome_inbox
    request = _market("two-agents")
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = tuple(pool.map(
            lambda index: (first if index % 2 else second)(_task(f"two-agents-{index}", request)),
            range(8),
        ))
    assert len(memory.events) == 1
    assert len({item["acknowledgement_hash"] for item in results}) == 1
    assert len(store.delivery_state.acknowledgements) == 1
    assert manager.calls == 1


def test_ack_is_rejected_until_all_effects_are_complete() -> None:
    service, store, _ = _service()
    outcome = service.execute(_market("ack-effects")).outcome
    inbox = L5ExecutionOutcomeInbox("consumer-effects")
    receipt = inbox.accept(outcome, required_effects=("memory", "event_bus")).receipt
    inbox.apply_effect(receipt, "memory", lambda: None)
    with pytest.raises(L5CanonicalExecutionError) as incomplete:
        service.acknowledge_outcome(receipt, inbox)
    assert incomplete.value.code == "INCOMPLETE_EFFECTS"
    assert store.delivery_state.acknowledgements == {}
    inbox.apply_effect(receipt, "event_bus", lambda: None)
    service.acknowledge_outcome(receipt, inbox)
    assert len(store.delivery_state.acknowledgements) == 1


@pytest.mark.parametrize("interrupt", [KeyboardInterrupt, SystemExit])
def test_agent_does_not_mask_system_interruptions(monkeypatch, interrupt) -> None:
    service, store, _ = _service()
    memory = RecordingMemory()
    monkeypatch.setattr(memory, "create_event", lambda *args, **kwargs: (_ for _ in ()).throw(interrupt()))
    agent = ExecutionAgent(service, memory)
    with pytest.raises(interrupt):
        agent(_task(f"system-{interrupt.__name__}", _market(f"system-{interrupt.__name__}")))
    assert store.delivery_state.acknowledgements == {}


def test_stale_blocked_decision_cannot_publish_on_newer_aggregate(monkeypatch) -> None:
    service, store, manager = _service()
    second = ExecutionService(store, manager, service.price_provider)
    blocked = CanonicalL5ExecutionRequest(
        intent=ExecutionIntent(
            intent_id="intent-stale-rejection",
            symbol="ES",
            side=IntentSide.SELL,
            quantity=1.0,
            estimated_price=100.0,
            timestamp=NOW,
        ),
        order_type=OrderType.MARKET,
        operation_id="operation-stale-rejection",
        order_id="order-stale-rejection",
        fill_id="fill-stale-rejection",
        report_id="report-stale-rejection",
        submitted_at=NOW,
        filled_at=NOW + timedelta(seconds=1),
    )
    original = store.publish_rejection_outcome

    def advance_then_publish(**kwargs):
        second.execute(_limit_placement("advance-rejection-cas"))
        return original(**kwargs)

    monkeypatch.setattr(store, "publish_rejection_outcome", advance_then_publish)
    with pytest.raises(L5CanonicalExecutionError) as stale:
        service.execute(blocked)
    assert stale.value.code == "STALE_AGGREGATE_STATE"
    assert store.outcome_for_intent(blocked.intent.intent_id) is None
    assert len(store.delivery_state.outcomes) == 1
    assert manager.calls == 2


def test_replay_rejects_rehashed_blocked_intent_forgery() -> None:
    service, store, _ = _service(max_position=0.0)
    outcome = service.execute(_market("blocked-intent-forgery")).outcome
    request = dict(outcome.request_payload)
    request["intent"] = {**dict(request["intent"]), "quantity": 2.0}
    fields = outcome.fields_without_hash()
    fields["request_payload"] = request
    fields["request_hash"] = _hash(request)
    fields["outcome_id"] = f"l5-outcome-{_hash({'request_hash': fields['request_hash'], 'intent_id': outcome.intent_id, 'operation_kind': outcome.operation_kind})}"
    forged = replace(
        outcome,
        request_payload=request,
        request_hash=fields["request_hash"],
        outcome_id=fields["outcome_id"],
        outcome_hash=_hash(fields),
    )
    assert forged.is_intact()
    event = L5ExecutionDeliveryEvent.create(
        sequence_number=2,
        event_type="OUTCOME_PUBLISHED",
        delivery_version_before=0,
        delivery_hash_before=store.delivery_state.journal[1].delivery_hash_before,
        payload={"outcome": forged.canonical()},
        previous_event_hash=store.delivery_state.journal[0].event_hash,
    )
    empty = L5ExecutionOutcomeInbox("empty-blocked-forgery")
    with pytest.raises(L5ExecutionDeliveryError, match="canonical risk evidence"):
        replay_l5_execution_delivery_journal(
            (store.delivery_state.journal[0], event),
            execution_events=store.state.execution_journal,
            expected_final_hash=event.event_hash,
            inbox_events=empty.state.journal,
            expected_inbox_hash=empty.state.journal[-1].event_hash,
        )


def test_replay_rejects_rehashed_blocked_violation_forgery() -> None:
    service, store, _ = _service(max_position=0.0)
    outcome = service.execute(_market("blocked-violation-forgery")).outcome
    decision = dict(outcome.decision_evidence)
    violations = [dict(item) for item in decision["violations"]]
    violations[0]["actual_value"] = 999.0
    decision_fields = {
        **decision,
        "violations": violations,
    }
    decision_fields.pop("authorization_id")
    decision_fields.pop("decision_hash")
    decision_hash = _hash(decision_fields)
    forged_decision = {
        **decision_fields,
        "authorization_id": f"risk-auth-{decision_hash}",
        "decision_hash": decision_hash,
    }
    fields = outcome.fields_without_hash()
    fields.update({
        "decision_evidence": forged_decision,
        "authorization_id": forged_decision["authorization_id"],
        "decision_hash": decision_hash,
    })
    forged = replace(
        outcome,
        decision_evidence=forged_decision,
        authorization_id=forged_decision["authorization_id"],
        decision_hash=decision_hash,
        outcome_hash=_hash(fields),
    )
    assert forged.is_intact()
    event = L5ExecutionDeliveryEvent.create(
        sequence_number=2,
        event_type="OUTCOME_PUBLISHED",
        delivery_version_before=0,
        delivery_hash_before=store.delivery_state.journal[1].delivery_hash_before,
        payload={"outcome": forged.canonical()},
        previous_event_hash=store.delivery_state.journal[0].event_hash,
    )
    empty = L5ExecutionOutcomeInbox("empty-violation-forgery")
    with pytest.raises(L5ExecutionDeliveryError, match="canonical risk evidence"):
        replay_l5_execution_delivery_journal(
            (store.delivery_state.journal[0], event),
            execution_events=store.state.execution_journal,
            expected_final_hash=event.event_hash,
            inbox_events=empty.state.journal,
            expected_inbox_hash=empty.state.journal[-1].event_hash,
        )


def test_multiple_consumer_journals_replay_with_exact_ack_causality() -> None:
    service, store, _ = _service()
    outcome = service.execute(_market("multi-consumer")).outcome
    left = L5ExecutionOutcomeInbox("consumer-multi-left")
    right = L5ExecutionOutcomeInbox("consumer-multi-right")
    left_receipt = left.accept(outcome, required_effects=("memory",)).receipt
    right_receipt = right.accept(outcome, required_effects=("memory",)).receipt
    left.apply_effect(left_receipt, "memory", lambda: None)
    right.apply_effect(right_receipt, "memory", lambda: None)
    service.acknowledge_outcome(left_receipt, left)
    service.acknowledge_outcome(right_receipt, right)
    replayed, _ = replay_l5_execution_delivery_journal(
        store.delivery_state.journal,
        execution_events=store.state.execution_journal,
        expected_final_hash=store.delivery_state.journal[-1].event_hash,
        inbox_events={
            left.consumer_id: left.state.journal,
            right.consumer_id: right.state.journal,
        },
        expected_inbox_hash={
            left.consumer_id: left.state.journal[-1].event_hash,
            right.consumer_id: right.state.journal[-1].event_hash,
        },
    )
    assert replayed == store.delivery_state


def test_replay_rejects_ack_when_effect_completion_is_removed() -> None:
    service, store, _ = _service()
    outcome = service.execute(_market("effect-removed")).outcome
    inbox = L5ExecutionOutcomeInbox("consumer-effect-removed")
    receipt = inbox.accept(outcome, required_effects=("memory",)).receipt
    inbox.apply_effect(receipt, "memory", lambda: None)
    service.acknowledge_outcome(receipt, inbox)
    acceptance_only = inbox.state.journal[:2]
    with pytest.raises(L5ExecutionDeliveryError):
        replay_l5_execution_delivery_journal(
            store.delivery_state.journal,
            execution_events=store.state.execution_journal,
            expected_final_hash=store.delivery_state.journal[-1].event_hash,
            inbox_events=acceptance_only,
            expected_inbox_hash=acceptance_only[-1].event_hash,
        )


def test_pending_market_outcomes_follow_publication_sequence_and_partial_ack() -> None:
    service, store, _ = _service()
    outcomes = tuple(service.execute(_market(f"ordered-market-{index}")).outcome for index in range(3))
    consumer = "consumer-market-order"
    assert service.pending_outcomes(consumer) == outcomes
    inbox = L5ExecutionOutcomeInbox(consumer)
    receipt = inbox.accept(outcomes[0]).receipt
    service.acknowledge_outcome(receipt, inbox)
    assert service.pending_outcomes(consumer) == outcomes[1:]
    replayed, _ = replay_l5_execution_delivery_journal(
        store.delivery_state.journal,
        execution_events=store.state.execution_journal,
        expected_final_hash=store.delivery_state.journal[-1].event_hash,
        inbox_events=inbox.state.journal,
        expected_inbox_hash=inbox.state.journal[-1].event_hash,
    )
    assert replayed.pending_for(consumer) == outcomes[1:]


def test_limit_placement_precedes_fill_even_when_ids_sort_in_reverse() -> None:
    selected = None
    for index in range(32):
        service, _store, _ = _service()
        placement = service.execute(_limit_placement(f"lexical-{index}")).outcome
        service.price_provider.set_market_price("ES", 98.0, observed_at=NOW + timedelta(seconds=1))
        fill = service.fill_limit(_limit_fill(f"lexical-{index}")).outcome
        if placement.outcome_id > fill.outcome_id:
            selected = (service, placement, fill)
            break
    assert selected is not None
    service, placement, fill = selected
    assert service.pending_outcomes("consumer-limit-order") == (placement, fill)


def test_limit_placement_precedes_cancellation() -> None:
    service, _, _ = _service()
    placement = service.execute(_limit_placement("ordered-cancel")).outcome
    cancellation = service.cancel_limit(CanonicalL5CancellationRequest(
        order_id="order-ordered-cancel",
        operation_id="operation-ordered-cancel",
        report_id="report-ordered-cancel",
        cancelled_at=NOW + timedelta(seconds=1),
    )).outcome
    assert service.pending_outcomes("consumer-cancel-order") == (placement, cancellation)
