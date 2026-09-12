"""Process-crash proof for the canonical execution memory sink only.

L5 is rebuilt from a fixed synthetic request, not recovered from durable storage.
These tests deliberately make no whole-runtime recovery claim.
"""
from __future__ import annotations

import multiprocessing
import os
from datetime import UTC, datetime

from sqlalchemy import text

from agicore.agents.execution_agent import EVT_ORDER_PROCESSED, ExecutionAgent
from agicore.core.event_delivery_contracts import DispatchClass, HandlerManifestEntry
from agicore.core.events import EventBus
from agicore.l2_memory.adapters.sqlalchemy_engine import SqlAlchemyEngine
from agicore.l2_memory.migrations.init_schema import init_schema
from agicore.l2_memory.schemas.task import TaskRead
from agicore.l2_memory.services.event_delivery_service import EventDeliveryService
from agicore.l2_memory.services.memory_service import MemoryService
from agicore.l5_action.broker_mock import MockBroker
from agicore.l5_action.execution_service import ExecutionService
from agicore.l5_action.execution_transaction import L5ExecutionTransactionStore
from agicore.risk.exposure_models import RiskLimits, empty_snapshot
from agicore.risk.risk_execution_context import InMemoryRiskContextProvider, RiskExecutionContext
from agicore.risk.risk_manager import RiskManager
from tests.l5_secure_helpers import market_payload

NOW = datetime(2026, 8, 15, 10, 0, tzinfo=UTC)


def _mnq_service() -> ExecutionService:
    # Same synthetic risk fixture limits as existing agent tests; MNQ only.
    limits = RiskLimits(
        max_position_size=2.0, max_exposure_value=10_000_000.0,
        max_drawdown_pct=0.5, daily_loss_limit=100_000.0,
    )
    context = RiskExecutionContext(
        provider_id="test-canonical-l5", state_version=0, trading_day="2026-08-15",
        risk_limits=limits, exposure_snapshot=empty_snapshot(initial_equity=1_000_000.0),
        signed_positions={"MNQ": 0.0}, daily_realized_pnl=0.0,
        current_equity=1_000_000.0, peak_equity=1_000_000.0,
        execution_enabled=True, kill_switch_active=False, legacy_hard_deny=False,
    )
    prices = MockBroker(provider_id="test-l5-price")
    prices.set_market_price("MNQ", 100.0, observed_at=NOW)
    store = L5ExecutionTransactionStore(
        initial_context=context, initial_risk_journal=InMemoryRiskContextProvider(context).journal,
        price_provider=prices,
    )
    return ExecutionService(store, RiskManager(limits), prices)


def _run_sink(database: str, crash: bool, task_id: str) -> None:
    engine = SqlAlchemyEngine(f"sqlite:///{database}", delivery_authority=True)
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
        ),),
        registered_at=NOW,
    )
    if crash:
        # Kill after the real SQL transaction commits, before the inbox sees success.
        for name in ("create_event", "create_event_idempotent"):
            original = getattr(memory, name)

            def commit_then_die(*args, _original=original, **kwargs):
                _original(*args, **kwargs)
                os._exit(73)

            setattr(memory, name, commit_then_die)
    service = _mnq_service()
    agent = ExecutionAgent(
        service, memory, EventBus(canonical_delivery=delivery, acceptance_clock=lambda: NOW),
    )
    agent(TaskRead(
        id=task_id, task_type="execution.order", status="running", assigned_to=None,
        payload=market_payload("sink-restart", symbol="MNQ", quantity=1.0),
        result=None, error=None, created_at=NOW, updated_at=NOW,
    ))
    engine.dispose()


def _spawn(database: str, crash: bool, task_id: str) -> int:
    process = multiprocessing.get_context("spawn").Process(
        target=_run_sink, args=(database, crash, task_id),
    )
    process.start()
    process.join(20)
    if process.is_alive():
        process.terminate()
        process.join(5)
        raise AssertionError("sink worker timed out")
    return process.exitcode


def _effects(database: str) -> list[tuple]:
    engine = SqlAlchemyEngine(f"sqlite:///{database}")
    try:
        with engine.session() as session:
            return [tuple(row) for row in session.execute(text(
                "SELECT effect_id, payload_hash FROM events "
                "WHERE event_type = 'agent.execution.order.processed'"
            ))]
    finally:
        engine.dispose()


def test_sql_commit_then_process_death_retry_has_one_stable_memory_effect(tmp_path):
    restarted = str(tmp_path / "restarted.sqlite3")
    reference = str(tmp_path / "reference.sqlite3")
    assert _spawn(restarted, True, "first-attempt") == 73
    assert len(_effects(restarted)) == 1
    assert _spawn(restarted, False, "retry-other-task") == 0
    assert _spawn(restarted, False, "third-task") == 0
    assert _spawn(reference, False, "reference-task") == 0
    effects = _effects(restarted)
    assert len(effects) == 1
    assert effects[0][0] is not None
    assert effects == _effects(reference)
