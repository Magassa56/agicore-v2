"""End-to-end Runtime Engine tests — full pipeline.

receive → enqueue → dispatch → execute → log → persist memory → feedback
"""
from __future__ import annotations

import threading
import time

from agicore.core.events import (
    EVT_TASK_COMPLETED,
    EVT_TASK_CREATED,
    EVT_TASK_FAILED,
    EVT_TASK_STARTED,
)
from agicore.core.retry import RetryPolicy
from agicore.l2_memory.schemas.task import TaskCreate
from agicore.l4_planning.runtime import RuntimeEngine


def test_full_pipeline_happy_path() -> None:
    """receive → enqueue → dispatch → execute → log → persist → feedback."""
    rt = RuntimeEngine(
        db_url="sqlite:///:memory:",
        retry_policy=RetryPolicy(max_attempts=1, initial_delay=0, jitter=False),
        poll_interval=0.0,
    )
    try:
        # 1. registered handler
        def echo_handler(task):
            return {"echoed": task.payload, "task_id": task.id}

        rt.register_handler("tx.echo", echo_handler)

        # 2. capture lifecycle events
        seen: list[str] = []
        rt.subscribe("*", lambda ev: seen.append(ev.event_type))

        # 3. submit (receive + enqueue)
        submitted = rt.submit(
            TaskCreate(id="t-1", task_type="tx.echo", payload={"msg": "hello"})
        )
        assert submitted.status == "pending"

        # 4. drain via run_once (dispatch + execute)
        n = rt.run_once()
        assert n == 1

        # 5. feedback : completed task with result
        from agicore.l2_memory.repositories.task_repository import TaskRepository
        with rt.orchestrator._engine.session() as s:  # type: ignore[attr-defined]
            repo = TaskRepository(s)
            final = repo.get("t-1")
        assert final is not None
        assert final.status == "completed"
        assert final.result == {"echoed": {"msg": "hello"}, "task_id": "t-1"}

        # 6. memory persistence : events were written to LTM
        events = rt.memory.get_recent_events(limit=20)
        types = [e.event_type for e in events]
        assert EVT_TASK_CREATED in types
        assert EVT_TASK_STARTED in types
        assert EVT_TASK_COMPLETED in types

        # 7. event bus propagation
        assert EVT_TASK_CREATED in seen
        assert EVT_TASK_STARTED in seen
        assert EVT_TASK_COMPLETED in seen
        assert EVT_TASK_FAILED not in seen
    finally:
        rt.shutdown()


def test_full_pipeline_failure_path() -> None:
    rt = RuntimeEngine(
        retry_policy=RetryPolicy(max_attempts=2, initial_delay=0, jitter=False),
        poll_interval=0.0,
    )
    try:
        def boom(task):
            raise RuntimeError("kaboom")

        rt.register_handler("tx.boom", boom)

        rt.submit(TaskCreate(id="t-fail", task_type="tx.boom"))
        rt.run_once()

        from agicore.l2_memory.repositories.task_repository import TaskRepository
        with rt.orchestrator._engine.session() as s:  # type: ignore[attr-defined]
            repo = TaskRepository(s)
            final = repo.get("t-fail")
        assert final is not None
        assert final.status == "failed"
        assert final.error is not None
        assert "kaboom" in final.error

        events = rt.memory.get_recent_events(limit=20)
        types = [e.event_type for e in events]
        assert EVT_TASK_FAILED in types
    finally:
        rt.shutdown()


def test_runtime_loop_consumes_via_queue_wakeup() -> None:
    """The execution loop must wake up immediately when a task is enqueued
    (rather than waiting out the full poll_interval)."""
    rt = RuntimeEngine(
        retry_policy=RetryPolicy(max_attempts=1, initial_delay=0, jitter=False),
        poll_interval=10.0,  # very long — only wakeup signal can interrupt it
    )

    def counter_handler(task):
        return {"id": task.id}

    rt.register_handler("tx.tick", counter_handler)

    completed: list[str] = []
    rt.subscribe(EVT_TASK_COMPLETED, lambda ev: completed.append(ev.payload["task_id"]))

    # Producer thread
    def produce_then_stop():
        time.sleep(0.05)
        rt.submit(TaskCreate(id="t-1", task_type="tx.tick"))
        time.sleep(0.05)
        rt.stop()

    producer = threading.Thread(target=produce_then_stop)
    consumer = threading.Thread(target=lambda: rt.run_forever(max_iterations=5))

    consumer.start()
    producer.start()

    producer.join(timeout=5.0)
    consumer.join(timeout=5.0)

    assert not consumer.is_alive(), "consumer did not exit"
    assert "t-1" in completed
    rt.shutdown()


def test_graceful_shutdown_drains_then_exits() -> None:
    rt = RuntimeEngine(
        retry_policy=RetryPolicy(max_attempts=1, initial_delay=0, jitter=False),
        poll_interval=0.01,
    )
    try:
        rt.register_handler("tx.echo", lambda t: {"ok": True})
        for i in range(3):
            rt.submit(TaskCreate(id=f"t-{i}", task_type="tx.echo"))

        thread = threading.Thread(target=lambda: rt.run_forever(max_iterations=10))
        thread.start()
        time.sleep(0.1)
        rt.stop()
        thread.join(timeout=5.0)

        assert not thread.is_alive()
    finally:
        rt.shutdown()


def test_runtime_context_manager() -> None:
    """RuntimeEngine usable as a context manager with auto-shutdown."""
    with RuntimeEngine(poll_interval=0.0) as rt:
        rt.register_handler("tx.noop", lambda t: {})
        rt.submit(TaskCreate(id="t-1", task_type="tx.noop"))
        n = rt.run_once()
        assert n == 1
    # After __exit__, engine is disposed.
