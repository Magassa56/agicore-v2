"""Born-again processes, actual L5 positions, and cross-authority crash recovery."""
from __future__ import annotations

import json
import multiprocessing
import os
import sqlite3

import pytest

from agicore.agents.execution_agent import AGENT_ID, EVT_ORDER_PROCESSED, ExecutionAgent
from agicore.core.event_delivery_contracts import DispatchClass, HandlerManifestEntry
from agicore.core.events import EventBus
from agicore.l2_memory.adapters.sqlalchemy_engine import SqlAlchemyEngine
from agicore.l2_memory.migrations.init_schema import init_schema
from agicore.l2_memory.schemas.task import TaskRead
from agicore.l2_memory.services.event_delivery_service import EventDeliveryService
from agicore.l2_memory.services.memory_service import MemoryService
from agicore.l5_action.execution_service import ExecutionService
from agicore.l5_action.execution_transaction import L5ExecutionTransactionError
from agicore.l5_action.sqlite_l5_recovery import L5RecoveryError, SQLiteL5RecoveryStore
from agicore.risk.risk_manager import RiskManager
from tests.integration.test_execution_memory_sink_restart import NOW, _effects, _mnq_service
from tests.l5_secure_helpers import market_payload

MANIFEST = {AGENT_ID: ("event_bus", "memory")}


def _create(path, **kwargs):
    seed = _mnq_service()
    return SQLiteL5RecoveryStore.create(
        path, consumers=MANIFEST, initial_context=seed.state.risk_context,
        initial_risk_journal=seed.state.risk_journal, price_provider=seed.price_provider, **kwargs,
    )


def _resume(path, **kwargs):
    return SQLiteL5RecoveryStore.resume(
        path, consumers=MANIFEST, price_provider=_mnq_service().price_provider, **kwargs,
    )


def _worker(directory, phase):
    database = directory + "/memory.sqlite3"
    l5_path = directory + "/l5.sqlite3"
    engine = SqlAlchemyEngine(f"sqlite:///{database}", delivery_authority=True)
    if not os.path.exists(l5_path):
        init_schema(engine, include_event_delivery=True)
    memory = MemoryService(engine)
    delivery = EventDeliveryService(
        engine, authority_id="event-delivery", authority_version="v1",
        runtime_profile_id="execution-base-v1", manifest_version="v1",
    )
    delivery.register_manifest(
        event_type=EVT_ORDER_PROCESSED,
        entries=(HandlerManifestEntry(
            handler_id="idempotent-memory-delivery", handler_version="v1",
            required=True, ordinal=0, dispatch_class=DispatchClass.DIRECT,
        ),), registered_at=NOW,
    )
    resumed = os.path.exists(l5_path)
    store = (_resume(l5_path, bus_authority=delivery, expected_bus_anchor=delivery.anchor(), memory_engine=engine)
             if resumed else _create(l5_path, bus_authority=delivery, memory_engine=engine))
    if resumed and phase != "retry_before_commit":
        assert store.state.positions["MNQ"].quantity == 1
        assert len(store.state.fills) == 1
    service = ExecutionService(store, RiskManager(store.state.risk_context.risk_limits), store.price_provider)
    bus = EventBus(canonical_delivery=delivery, acceptance_clock=lambda: NOW)
    agent = ExecutionAgent(service, memory, bus)
    if phase in {"before_commit", "after_commit", "before_ack", "after_ack", "after_inbox", "after_effect", "after_bus_effect"}:
        original = store._persist

        def crash_publish(authority, overrides):
            ack = bool(authority.delivery_state.acknowledgements)
            target = ((phase in {"before_commit", "after_commit"} and bool(authority.aggregate_state.fills))
                      or (phase in {"before_ack", "after_ack"} and ack)
                      or (phase == "after_inbox" and any(s.receipts for s in overrides.values()))
                      or (phase == "after_effect" and any(s.effect_event_hashes for s in overrides.values()))
                      or (phase == "after_bus_effect" and any("event_bus" in effects
                          for s in overrides.values() for effects in s.effect_event_hashes.values())))
            if target and phase.startswith("before_"):
                os._exit(73)
            original(authority, overrides)
            if target:
                os._exit(73)
        store._persist = crash_publish
    if phase == "after_memory":
        original_memory = memory.create_event_idempotent

        def memory_die(*args, **kwargs):
            original_memory(*args, **kwargs)
            os._exit(73)
        memory.create_event_idempotent = memory_die
    if phase == "after_bus":
        original_bus = bus.accept_idempotent

        def bus_die(*args, **kwargs):
            original_bus(*args, **kwargs)
            os._exit(73)
        bus.accept_idempotent = bus_die
    task = TaskRead(
        id="task-" + phase, task_type="execution.order", status="running", assigned_to=None,
        payload=market_payload("recovery", symbol="MNQ", quantity=1),
        result=None, error=None, created_at=NOW, updated_at=NOW,
    )
    result = agent(task)
    assert result["committed"]
    assert store.state.positions["MNQ"].quantity == 1
    assert len(store.state.fills) == 1
    assert len(store.state.orders) == 1
    assert result["outcome_id"] not in {item.outcome_id for item in store.pending_outcomes(AGENT_ID)}
    # Rebuild a second time and prove that actual restored risk exposure denies >2.
    restored = _resume(l5_path, bus_authority=delivery, expected_bus_anchor=delivery.anchor(), memory_engine=engine)
    denied = ExecutionService(restored, RiskManager(restored.state.risk_context.risk_limits), restored.price_provider)
    request = ExecutionAgent._build_execution_request(market_payload("excess", symbol="MNQ", quantity=2))
    assert not denied.execute(request).committed
    assert len(restored.state.fills) == 1
    engine.dispose()


def _spawn(directory, phase):
    process = multiprocessing.get_context("spawn").Process(target=_worker, args=(str(directory), phase))
    process.start()
    process.join(25)
    if process.is_alive():
        process.terminate()
        process.join(5)
        pytest.fail("recovery process timed out")
    return process.exitcode


def _document(path):
    with sqlite3.connect(path) as connection:
        return json.loads(connection.execute("SELECT document FROM recovery").fetchone()[0])


@pytest.mark.parametrize("phase", [
    "before_commit", "after_commit", "after_inbox", "after_memory",
    "after_effect", "after_bus", "after_bus_effect", "before_ack", "after_ack",
])
def test_crash_fresh_process_retry_matches_independent_reference(tmp_path, phase):
    restarted = tmp_path / "restarted"
    reference = tmp_path / "reference"
    restarted.mkdir()
    reference.mkdir()
    assert _spawn(restarted, phase) == 73
    assert _spawn(restarted, "retry_before_commit" if phase == "before_commit" else "retry") == 0
    assert _spawn(restarted, "retry") == 0
    assert _spawn(reference, "reference") == 0
    assert _document(restarted / "l5.sqlite3") == _document(reference / "l5.sqlite3")
    assert _effects(str(restarted / "memory.sqlite3")) == _effects(str(reference / "memory.sqlite3"))
    assert len(_effects(str(restarted / "memory.sqlite3"))) == 1


def test_absent_existing_manifest_and_anchor_fail_closed(tmp_path):
    path = tmp_path / "l5.sqlite3"
    with pytest.raises(sqlite3.OperationalError):
        _resume(path)
    assert not path.exists()
    store = _create(path)
    with pytest.raises(FileExistsError):
        _create(path)
    with pytest.raises(L5RecoveryError, match="CONFIGURATION"):
        SQLiteL5RecoveryStore.resume(path, consumers={"other": ()}, price_provider=store.price_provider)
    with pytest.raises(L5RecoveryError, match="CONSUMER"):
        store.consumer_inbox("other")
    with pytest.raises(L5RecoveryError, match="ANCHOR"):
        _resume(path, expected_anchor=type(store.anchor)(3, store.anchor.digest))


def test_stale_writer_cannot_publish_and_ram_stays_unchanged(tmp_path):
    path = tmp_path / "l5.sqlite3"
    first = _create(path)
    stale = _resume(path)
    before = stale.authority_state
    request = ExecutionAgent._build_execution_request(market_payload("one", symbol="MNQ", quantity=1))
    for store in (first, stale):
        service = ExecutionService(store, RiskManager(store.state.risk_context.risk_limits), store.price_provider)
        if store is first:
            assert service.execute(request).committed
        else:
            with pytest.raises(L5ExecutionTransactionError, match="PUBLICATION_FAILED") as error:
                service.execute(request)
            assert isinstance(error.value.__cause__, L5RecoveryError)
            assert "STALE" in str(error.value.__cause__)
    assert stale.authority_state == before
    assert _resume(path).state.positions["MNQ"].quantity == 1


def test_corruption_and_missing_anchor_rejected(tmp_path):
    path = tmp_path / "l5.sqlite3"
    _create(path)
    with sqlite3.connect(path) as connection:
        connection.execute("UPDATE recovery SET document='{}'")
    with pytest.raises(L5RecoveryError, match="ANCHOR"):
        _resume(path)
    with sqlite3.connect(path) as connection:
        connection.execute("DELETE FROM recovery")
    with pytest.raises(L5RecoveryError, match="MISSING"):
        _resume(path)


def test_rehashed_semantic_corruption_is_rejected(tmp_path):
    import hashlib

    path = tmp_path / "l5.sqlite3"
    store = _create(path)
    service = ExecutionService(store, RiskManager(store.state.risk_context.risk_limits), store.price_provider)
    service.execute(ExecutionAgent._build_execution_request(market_payload("one", symbol="MNQ", quantity=1)))
    document = _document(path)
    event = document["execution"][-1]
    event["payload"]["positions"]["MNQ"]["quantity"] = 2.0
    event["event_hash"] = hashlib.sha256(json.dumps(
        {key: value for key, value in event.items() if key != "event_hash"},
        sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()
    encoded = json.dumps(document, sort_keys=True, separators=(",", ":"), allow_nan=False)
    with sqlite3.connect(path) as connection:
        connection.execute("UPDATE recovery SET document=?, digest=?", (encoded, hashlib.sha256(encoded.encode()).hexdigest()))
    with pytest.raises(L5RecoveryError, match="INVALID_RECOVERY_DOCUMENT"):
        _resume(path)


def test_canonical_ack_resume_requires_bus_proof(tmp_path):
    assert _spawn(tmp_path, "reference") == 0
    with pytest.raises(L5RecoveryError, match="UNVERIFIED_BUS_ACCEPTANCE"):
        _resume(tmp_path / "l5.sqlite3")


def test_foreign_outcome_and_changed_effect_manifest_leave_storage_unchanged(tmp_path):
    owner = _create(tmp_path / "owner.sqlite3")
    foreign = _create(tmp_path / "foreign.sqlite3")
    service = ExecutionService(foreign, RiskManager(foreign.state.risk_context.risk_limits), foreign.price_provider)
    result = service.execute(ExecutionAgent._build_execution_request(market_payload("one", symbol="MNQ", quantity=1)))
    before = owner.anchor
    inbox = owner.consumer_inbox(AGENT_ID)
    with pytest.raises(L5RecoveryError, match="INBOX_OUTCOME_CONFLICT"):
        inbox.accept(result.outcome, required_effects=MANIFEST[AGENT_ID])
    with pytest.raises(L5RecoveryError, match="CONFIGURATION"):
        inbox.accept(result.outcome, required_effects=("memory",))
    assert owner.anchor == before
    assert not inbox.receipts
    assert _resume(tmp_path / "owner.sqlite3").anchor == before


def _existing_authorities(directory):
    engine = SqlAlchemyEngine(f"sqlite:///{directory / 'memory.sqlite3'}", delivery_authority=True)
    delivery = EventDeliveryService(
        engine, authority_id="event-delivery", authority_version="v1",
        runtime_profile_id="execution-base-v1", manifest_version="v1",
    )
    return engine, delivery


def test_forged_ack_is_refused_before_durable_or_ram_publication(tmp_path):
    assert _spawn(tmp_path, "before_ack") == 73
    engine, delivery = _existing_authorities(tmp_path)
    path = tmp_path / "l5.sqlite3"
    store = _resume(path, memory_engine=engine, bus_authority=delivery, expected_bus_anchor=delivery.anchor())
    service = ExecutionService(store, RiskManager(store.state.risk_context.risk_limits), store.price_provider)
    inbox = store.consumer_inbox(AGENT_ID)
    receipt = inbox.receipts[0]
    before = store.anchor
    with pytest.raises(ValueError, match="UNVERIFIED_BUS_ACCEPTANCE"):
        service.acknowledge_outcome(receipt, inbox, emission_accepted_hash="f" * 64)
    assert store.anchor == before
    assert len(store.pending_outcomes(AGENT_ID)) == 1
    assert _resume(path, memory_engine=engine, bus_authority=delivery,
                   expected_bus_anchor=delivery.anchor()).anchor == before
    engine.dispose()


@pytest.mark.parametrize("damage, expected", [
    ("missing", "MEMORY_EFFECT_MISSING"),
    ("conflicting", "MEMORY_EFFECT_CONFLICT"),
    ("absent_authority", "MEMORY_AUTHORITY_REQUIRED"),
    ("foreign_authority", "MEMORY_EFFECT_MISSING"),
])
def test_completed_memory_requires_exact_surviving_sink_proof(tmp_path, damage, expected):
    assert _spawn(tmp_path, "after_effect") == 73
    path = tmp_path / "l5.sqlite3"
    before = _document(path)
    engine, delivery = _existing_authorities(tmp_path)
    if damage == "missing":
        with sqlite3.connect(tmp_path / "memory.sqlite3") as connection:
            connection.execute("DELETE FROM events WHERE effect_id IS NOT NULL")
    elif damage == "conflicting":
        # Keep effect_id and hash unchanged: checking just the stored hash is insufficient.
        with sqlite3.connect(tmp_path / "memory.sqlite3") as connection:
            connection.execute("UPDATE events SET payload='{}' WHERE effect_id IS NOT NULL")
    foreign = None
    if damage == "foreign_authority":
        foreign = SqlAlchemyEngine(f"sqlite:///{tmp_path / 'foreign.sqlite3'}")
        init_schema(foreign)
    with pytest.raises(L5RecoveryError, match=expected):
        _resume(path, memory_engine=(None if damage == "absent_authority" else foreign or engine),
                bus_authority=delivery, expected_bus_anchor=delivery.anchor())
    assert _document(path) == before
    if foreign is not None:
        foreign.dispose()
    engine.dispose()


def test_completed_bus_requires_exact_surviving_proof_before_ack(tmp_path):
    assert _spawn(tmp_path, "after_bus_effect") == 73
    path = tmp_path / "l5.sqlite3"
    engine, _ = _existing_authorities(tmp_path)
    foreign = SqlAlchemyEngine(f"sqlite:///{tmp_path / 'foreign.sqlite3'}", delivery_authority=True)
    init_schema(foreign, include_event_delivery=True)
    delivery = EventDeliveryService(
        foreign, authority_id="event-delivery", authority_version="v1",
        runtime_profile_id="execution-base-v1", manifest_version="v1",
    )
    delivery.register_manifest(event_type=EVT_ORDER_PROCESSED, entries=(HandlerManifestEntry(
        handler_id="idempotent-memory-delivery", handler_version="v1", required=True,
        ordinal=0, dispatch_class=DispatchClass.DIRECT,
    ),), registered_at=NOW)
    before = _document(path)
    with pytest.raises(L5RecoveryError, match="UNVERIFIED_BUS_ACCEPTANCE"):
        _resume(path, memory_engine=engine, bus_authority=delivery, expected_bus_anchor=delivery.anchor())
    assert _document(path) == before
    foreign.dispose()
    engine.dispose()


def test_forged_memory_completion_is_refused_before_publication(tmp_path):
    engine = SqlAlchemyEngine(f"sqlite:///{tmp_path / 'memory.sqlite3'}")
    init_schema(engine)
    store = _create(tmp_path / "l5.sqlite3", memory_engine=engine)
    service = ExecutionService(store, RiskManager(store.state.risk_context.risk_limits), store.price_provider)
    result = service.execute(ExecutionAgent._build_execution_request(market_payload("one", symbol="MNQ", quantity=1)))
    inbox = store.consumer_inbox(AGENT_ID)
    receipt = inbox.accept(result.outcome, required_effects=MANIFEST[AGENT_ID]).receipt
    before = store.anchor
    with pytest.raises(L5RecoveryError, match="MEMORY_EFFECT_MISSING"):
        inbox.apply_effect(receipt, "memory", lambda: None)
    assert store.anchor == before
    assert not inbox.state.effect_event_hashes
    engine.dispose()


def test_recovered_required_bus_handler_completes_and_remains_replayable(tmp_path):
    from agicore.l2_memory.services.idempotent_memory_delivery_handler import (
        IdempotentMemoryDeliveryHandler,
    )

    assert _spawn(tmp_path, "after_bus") == 73
    assert _spawn(tmp_path, "retry") == 0
    engine, delivery = _existing_authorities(tmp_path)
    handler = IdempotentMemoryDeliveryHandler(delivery, MemoryService(engine))
    assert handler.run_one(worker_identity="recovery-handler", observed_at=NOW).status == "COMPLETED"
    assert handler.run_one(worker_identity="recovery-handler", observed_at=NOW).status == "IDLE"
    replayed = delivery.replay(expected_anchor=delivery.anchor())
    assert all(item.status == "COMPLETED" for item in replayed.deliveries)
    assert all(item.status == "COMPLETED" for item in replayed.emissions)
    store = _resume(tmp_path / "l5.sqlite3", memory_engine=engine, bus_authority=delivery,
                    expected_bus_anchor=delivery.anchor())
    assert store.state.positions["MNQ"].quantity == 1
    pending = store.pending_outcomes(AGENT_ID)
    assert len(pending) == 1
    assert pending[0].intent_id == "intent-excess" and not pending[0].committed
    assert all(item.intent_id != "intent-recovery" for item in pending)
    with sqlite3.connect(tmp_path / "memory.sqlite3") as connection:
        assert connection.execute("SELECT COUNT(*) FROM events WHERE effect_id IS NOT NULL").fetchone()[0] == 2
    engine.dispose()


def test_whole_database_rollback_requires_independent_anchor(tmp_path):
    path = tmp_path / "l5.sqlite3"
    store = _create(path)
    with sqlite3.connect(path) as connection:
        old = connection.execute("SELECT version, digest, document FROM recovery").fetchone()
    service = ExecutionService(store, RiskManager(store.state.risk_context.risk_limits), store.price_provider)
    service.execute(ExecutionAgent._build_execution_request(market_payload("one", symbol="MNQ", quantity=1)))
    current = store.anchor
    with sqlite3.connect(path) as connection:
        connection.execute("UPDATE recovery SET version=?, digest=?, document=?", old)
    # A valid whole-file rollback cannot be detected from that same file alone.
    assert _resume(path).state.state_version == 0
    with pytest.raises(L5RecoveryError, match="ANCHOR"):
        _resume(path, expected_anchor=current)
