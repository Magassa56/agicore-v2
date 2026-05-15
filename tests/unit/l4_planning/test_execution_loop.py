"""Tests for ExecutionLoop."""
from __future__ import annotations

import threading
import time

import pytest

from agicore.l2_memory.schemas.task import TaskCreate
from agicore.l4_planning.execution_loop import ExecutionLoop
from agicore.l4_planning.handlers import HandlerRegistry
from agicore.l4_planning.orchestrator import AgentOrchestrator


def test_run_once_processes_pending(
    orchestrator: AgentOrchestrator,
    registry: HandlerRegistry,
) -> None:
    registry.register("tx.echo", lambda t: {"id": t.id})
    for i in range(2):
        orchestrator.submit_task(TaskCreate(id=f"t-{i}", task_type="tx.echo"))

    loop = ExecutionLoop(orchestrator, poll_interval=0.0, batch_size=10)
    n = loop.run_once()
    assert n == 2


def test_run_once_returns_zero_when_no_pending(
    orchestrator: AgentOrchestrator,
) -> None:
    loop = ExecutionLoop(orchestrator, poll_interval=0.0)
    assert loop.run_once() == 0


def test_run_forever_max_iterations(
    orchestrator: AgentOrchestrator,
    registry: HandlerRegistry,
) -> None:
    registry.register("tx.echo", lambda t: {})
    for i in range(3):
        orchestrator.submit_task(TaskCreate(id=f"t-{i}", task_type="tx.echo"))

    loop = ExecutionLoop(orchestrator, poll_interval=0.0, batch_size=2)
    total = loop.run_forever(max_iterations=3)
    assert total >= 3


def test_run_forever_stops_when_signaled(
    orchestrator: AgentOrchestrator,
    registry: HandlerRegistry,
) -> None:
    registry.register("tx.echo", lambda t: {})
    orchestrator.submit_task(TaskCreate(id="t-0", task_type="tx.echo"))

    loop = ExecutionLoop(orchestrator, poll_interval=0.5)
    thread = threading.Thread(target=lambda: loop.run_forever(max_iterations=100))
    thread.start()
    time.sleep(0.05)
    loop.stop()
    thread.join(timeout=2.0)
    assert not thread.is_alive()


def test_invalid_args() -> None:
    class _Stub:
        pass

    with pytest.raises(ValueError):
        ExecutionLoop(_Stub(), poll_interval=-1)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        ExecutionLoop(_Stub(), batch_size=0)  # type: ignore[arg-type]
