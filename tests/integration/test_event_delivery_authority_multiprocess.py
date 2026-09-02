from __future__ import annotations

import multiprocessing
from datetime import datetime, timezone
from queue import Empty

from sqlalchemy import text

from agicore.core.event_delivery_contracts import DispatchClass, HandlerManifestEntry
from agicore.l2_memory.adapters.sqlalchemy_engine import SqlAlchemyEngine
from agicore.l2_memory.migrations.add_event_delivery_authority import (
    add_event_delivery_authority,
)
from agicore.l2_memory.services.event_delivery_service import EventDeliveryService


NOW = datetime(2026, 8, 27, 13, 0, tzinfo=timezone.utc)


def _service(engine: SqlAlchemyEngine) -> EventDeliveryService:
    return EventDeliveryService(
        engine,
        authority_id="event-delivery",
        authority_version="v1",
        runtime_profile_id="signal-loop-v1",
        manifest_version="v1",
    )


def _accept_worker(database: str, value: int, start, ready, results) -> None:
    engine = SqlAlchemyEngine(f"sqlite:///{database}", delivery_authority=True)
    try:
        ready.put("ready")
        if not start.wait(timeout=30):
            results.put(("error", "start timeout"))
            return
        result = _service(engine).accept_emission(
            source_identity="receipt-multiprocess",
            consumer_id="execution-agent",
            outcome_id="outcome-multiprocess",
            outcome_hash="a" * 64,
            receipt_hash="b" * 64,
            source_sequence=1,
            event_type="agent.execution.order.processed",
            occurred_at=NOW,
            accepted_at=NOW,
            payload={"value": value},
        )
        results.put(("ok", result.status.value, result.emission.emission_effect_id))
    except BaseException as exc:
        results.put(("error", type(exc).__name__, str(exc)))
    finally:
        engine.dispose()


def _claim_worker(database: str, effect_id: str, worker: str, start, ready, results) -> None:
    engine = SqlAlchemyEngine(f"sqlite:///{database}", delivery_authority=True)
    try:
        ready.put("ready")
        if not start.wait(timeout=30):
            results.put(("error", "start timeout"))
            return
        result = _service(engine).claim(
            handler_effect_id=effect_id,
            worker_identity=worker,
            claimed_at=NOW,
        )
        results.put(("ok", result.status.value, result.delivery.fencing_generation))
    except BaseException as exc:
        results.put(("error", type(exc).__name__, str(exc)))
    finally:
        engine.dispose()


def _ordered_accept_worker(database: str, sequence: int, start, ready, results) -> None:
    engine = SqlAlchemyEngine(f"sqlite:///{database}", delivery_authority=True)
    try:
        ready.put("ready")
        if not start.wait(timeout=30):
            results.put(("error", "start timeout"))
            return
        try:
            _service(engine).accept_emission(
                source_identity=f"receipt-{sequence}",
                consumer_id="execution-agent",
                outcome_id=f"outcome-{sequence}",
                outcome_hash="a" * 64,
                receipt_hash="b" * 64,
                source_sequence=sequence,
                event_type="agent.execution.order.processed",
                occurred_at=NOW,
                accepted_at=NOW,
                payload={"sequence": sequence},
            )
            results.put(("ok", "accepted", sequence))
        except ValueError:
            results.put(("ok", "rejected", sequence))
    except BaseException as exc:
        results.put(("error", type(exc).__name__, str(exc)))
    finally:
        engine.dispose()


def _run_workers(target, args: tuple[tuple[object, ...], tuple[object, ...]]):
    context = multiprocessing.get_context("spawn")
    start = context.Event()
    ready = context.Queue()
    results = context.Queue()
    processes = [
        context.Process(target=target, args=(*worker_args, start, ready, results))
        for worker_args in args
    ]
    for process in processes:
        process.start()
    try:
        assert [ready.get(timeout=30) for _ in processes] == ["ready", "ready"]
        start.set()
        observed = [results.get(timeout=30) for _ in processes]
    except Empty as exc:  # pragma: no cover - failure diagnostic
        raise AssertionError("multiprocess worker did not report") from exc
    finally:
        start.set()
        for process in processes:
            process.join(timeout=30)
            if process.is_alive():
                process.terminate()
                process.join(timeout=10)
    assert all(process.exitcode == 0 for process in processes)
    assert all(item[0] == "ok" for item in observed), observed
    return observed


def _bootstrap(database) -> tuple[str, str]:
    url = f"sqlite:///{database.as_posix()}"
    engine = SqlAlchemyEngine(url, delivery_authority=True)
    add_event_delivery_authority(engine)
    service = _service(engine)
    service.register_manifest(
        event_type="agent.execution.order.processed",
        entries=(
            HandlerManifestEntry(
                handler_id="signal-loop",
                handler_version="v1",
                required=True,
                ordinal=0,
                dispatch_class=DispatchClass.DIRECT,
            ),
        ),
        registered_at=NOW,
    )
    engine.dispose()
    return url, database.as_posix()


def test_two_spawned_processes_accept_same_emission_once(tmp_path) -> None:
    database = tmp_path / "delivery-process-same.sqlite3"
    url, path = _bootstrap(database)
    observed = _run_workers(_accept_worker, ((path, 1), (path, 1)))
    assert sorted(item[1] for item in observed) == ["ALREADY_APPLIED", "APPLIED_NEW"]
    assert len({item[2] for item in observed}) == 1
    engine = SqlAlchemyEngine(url, delivery_authority=True)
    try:
        with engine.session() as session:
            assert session.execute(text("SELECT COUNT(*) FROM event_bus_emissions")).scalar_one() == 1
            assert session.execute(text("SELECT COUNT(*) FROM event_handler_deliveries")).scalar_one() == 1
            assert session.execute(text("SELECT COUNT(*) FROM event_delivery_journal")).scalar_one() == 1
    finally:
        engine.dispose()


def test_two_spawned_processes_conflict_on_different_payload(tmp_path) -> None:
    database = tmp_path / "delivery-process-conflict.sqlite3"
    url, path = _bootstrap(database)
    observed = _run_workers(_accept_worker, ((path, 1), (path, 2)))
    assert sorted(item[1] for item in observed) == ["APPLIED_NEW", "CONFLICT"]
    engine = SqlAlchemyEngine(url, delivery_authority=True)
    try:
        with engine.session() as session:
            assert session.execute(text("SELECT COUNT(*) FROM event_bus_emissions")).scalar_one() == 1
    finally:
        engine.dispose()


def test_two_spawned_processes_claim_same_handler_once(tmp_path) -> None:
    database = tmp_path / "delivery-process-claim.sqlite3"
    url, path = _bootstrap(database)
    engine = SqlAlchemyEngine(url, delivery_authority=True)
    try:
        emission = _service(engine).accept_emission(
            source_identity="receipt-claim",
            consumer_id="execution-agent",
            outcome_id="outcome-claim",
            outcome_hash="a" * 64,
            receipt_hash="b" * 64,
            source_sequence=1,
            event_type="agent.execution.order.processed",
            occurred_at=NOW,
            accepted_at=NOW,
            payload={},
        )
        effect_id = emission.deliveries[0].handler_effect_id
    finally:
        engine.dispose()
    observed = _run_workers(
        _claim_worker,
        ((path, effect_id, "worker-a"), (path, effect_id, "worker-b")),
    )
    assert sorted(item[1] for item in observed) == ["CLAIMED", "UNAVAILABLE"]
    verifier = SqlAlchemyEngine(url, delivery_authority=True)
    try:
        with verifier.session() as session:
            row = session.execute(
                text(
                    "SELECT status, fencing_generation FROM event_handler_deliveries "
                    "WHERE handler_effect_id = :effect_id"
                ),
                {"effect_id": effect_id},
            ).one()
        assert tuple(row) == ("CLAIMED", 1)
    finally:
        verifier.dispose()


def test_two_spawned_processes_never_commit_regressive_source_order(tmp_path) -> None:
    database = tmp_path / "delivery-process-order.sqlite3"
    url, path = _bootstrap(database)
    observed = _run_workers(
        _ordered_accept_worker,
        ((path, 10), (path, 11)),
    )
    assert any(item[1] == "accepted" for item in observed)
    engine = SqlAlchemyEngine(url, delivery_authority=True)
    try:
        with engine.session() as session:
            committed = list(
                session.execute(
                    text(
                        "SELECT source_sequence FROM event_bus_emissions "
                        "ORDER BY accepted_sequence"
                    )
                ).scalars()
            )
        assert committed == sorted(set(committed))
    finally:
        engine.dispose()
