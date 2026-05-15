"""HeartbeatAgent + HeartbeatScheduler — Phase 5 runtime stability handler.

Two collaborating components in a single file (tightly coupled domain) :

- ``HeartbeatAgent``      : ``TaskHandler`` for ``agent.heartbeat`` tasks.
- ``HeartbeatScheduler``  : minimal background thread that periodically
                            enqueues an ``agent.heartbeat`` task via
                            ``TaskQueue.enqueue``.

Design constraints honored
--------------------------
- No async framework — single thread for the scheduler.
- No cron, no APScheduler — vanilla ``threading.Thread`` + ``Event``.
- No new abstraction at the architecture level : we ship two concrete classes
  scoped to the heartbeat domain.
- Runtime Core (orchestrator/dispatcher/execution loop/queue/event bus) is
  used as-is. The scheduler only calls ``queue.enqueue(...)``, nothing else.
"""
from __future__ import annotations

import threading
import time
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import structlog

from agicore.core.events import EventBus
from agicore.core.task_queue import TaskQueue
from agicore.l2_memory.schemas.task import TaskCreate, TaskRead
from agicore.l2_memory.services.memory_service import MemoryService

logger = structlog.get_logger(__name__)


# Canonical identifiers exposed to the rest of the system
TASK_TYPE_HEARTBEAT: str = "agent.heartbeat"
EVT_HEARTBEAT_TICK: str = "agent.heartbeat.tick"
AGENT_ID: str = "heartbeat_agent"

# Default runtime states
RUNTIME_STATE_ACTIVE: str = "active"
RUNTIME_STATE_DEGRADED: str = "degraded"
RUNTIME_STATE_STOPPING: str = "stopping"


# ============================================================================
# HeartbeatAgent — the handler
# ============================================================================
class HeartbeatAgent:
    """Handler for ``agent.heartbeat`` tasks.

    On each invocation :
    - increment a process-local counter,
    - persist an ``agent.heartbeat.tick`` event in LTM,
    - emit the same event on the EventBus when provided,
    - return structured feedback : ``tick_id``, ``timestamp``, ``counter``,
      ``latency_ms``, ``runtime_state``.

    Parameters
    ----------
    memory : MemoryService
        Required. Domain event persistence target.
    event_bus : EventBus | None
        Optional in-process event bus.
    runtime_state_provider : Callable[[], str] | None
        Optional callable returning a runtime-state label. Defaults to a
        constant ``"active"``. Useful when wired to a ShutdownHandler so the
        agent can report ``"stopping"`` during graceful drain.
    """

    def __init__(
        self,
        memory: MemoryService,
        event_bus: EventBus | None = None,
        *,
        runtime_state_provider: Callable[[], str] | None = None,
    ) -> None:
        self._memory = memory
        self._bus = event_bus
        self._state_provider: Callable[[], str] = (
            runtime_state_provider if runtime_state_provider is not None
            else (lambda: RUNTIME_STATE_ACTIVE)
        )
        self._counter = 0

    @property
    def counter(self) -> int:
        """Number of ticks processed by this instance."""
        return self._counter

    @property
    def agent_id(self) -> str:
        return AGENT_ID

    def __call__(self, task: TaskRead) -> dict[str, Any]:
        started_at = datetime.now(timezone.utc)
        tick_id = f"hb-tick-{uuid4()}"
        self._counter += 1

        runtime_state = self._safe_runtime_state()

        logger.info(
            "heartbeat_agent.tick",
            task_id=task.id,
            tick_id=tick_id,
            counter=self._counter,
            runtime_state=runtime_state,
        )

        # Persist domain event in LTM
        self._memory.create_event(
            EVT_HEARTBEAT_TICK,
            task_id=task.id,
            agent_id=AGENT_ID,
            payload={
                "tick_id": tick_id,
                "counter": self._counter,
                "runtime_state": runtime_state,
            },
        )

        # Optional bus emission
        if self._bus is not None:
            self._bus.emit(
                EVT_HEARTBEAT_TICK,
                task_id=task.id,
                tick_id=tick_id,
                counter=self._counter,
                runtime_state=runtime_state,
            )

        finished_at = datetime.now(timezone.utc)
        latency_ms = (finished_at - started_at).total_seconds() * 1000.0

        return {
            "tick_id": tick_id,
            "timestamp": finished_at.isoformat(),
            "counter": self._counter,
            "latency_ms": round(latency_ms, 3),
            "runtime_state": runtime_state,
            "agent_id": AGENT_ID,
            "task_id": task.id,
        }

    def _safe_runtime_state(self) -> str:
        """Never let a faulty provider crash the heartbeat path."""
        try:
            return str(self._state_provider())
        except Exception as exc:
            logger.warning(
                "heartbeat_agent.state_provider_failed", error=str(exc)
            )
            return RUNTIME_STATE_DEGRADED


# ============================================================================
# HeartbeatScheduler — the producer thread
# ============================================================================
class HeartbeatScheduler:
    """Periodic enqueuer for heartbeat tasks.

    Owns a single daemon thread that wakes up every ``interval_s`` seconds
    and calls ``queue.enqueue(...)``. The thread terminates as soon as
    ``stop()`` is called, with a small polling resolution so external
    shutdown signals are honored quickly.

    Lifecycle :
        scheduler = HeartbeatScheduler(queue, interval_s=5.0)
        scheduler.start()
        ...
        scheduler.stop()  # idempotent, joins the thread

    Parameters
    ----------
    queue : TaskQueue
        Used to enqueue each tick task. Persists in LTM and wakes the loop.
    interval_s : float
        Seconds between successive enqueues. Must be > 0.
    poll_resolution_s : float
        Maximum sleep granularity. Smaller values react to ``stop()`` faster
        at the cost of slightly more CPU. Default 0.1 s.
    task_id_prefix : str
        Prefix used for generated task ids.
    assigned_to : str | None
        Optional ``assigned_to`` propagated on each enqueued task.
    payload_extra : dict | None
        Optional extra payload merged into every tick task.
    """

    _DEFAULT_POLL_RESOLUTION_S: float = 0.1

    def __init__(
        self,
        queue: TaskQueue,
        *,
        interval_s: float = 5.0,
        poll_resolution_s: float | None = None,
        task_id_prefix: str = "hb",
        assigned_to: str | None = AGENT_ID,
        payload_extra: dict[str, Any] | None = None,
    ) -> None:
        if interval_s <= 0:
            raise ValueError("interval_s must be > 0")
        if poll_resolution_s is not None and poll_resolution_s <= 0:
            raise ValueError("poll_resolution_s must be > 0")
        self._queue = queue
        self._interval = float(interval_s)
        self._poll = float(poll_resolution_s or min(self._DEFAULT_POLL_RESOLUTION_S, self._interval))
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._enqueued = 0
        self._last_enqueue_at: float | None = None
        self._task_id_prefix = task_id_prefix
        self._assigned_to = assigned_to
        self._payload_extra: dict[str, Any] = dict(payload_extra or {})

    @property
    def enqueued_count(self) -> int:
        """Total ticks enqueued since the last start()."""
        return self._enqueued

    @property
    def interval_s(self) -> float:
        return self._interval

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    # ------------------------------------------------------------------ Lifecycle
    def start(self) -> None:
        """Start the background thread. Idempotent."""
        if self.is_running():
            logger.debug("heartbeat_scheduler.already_running")
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._loop,
            name="heartbeat-scheduler",
            daemon=True,
        )
        self._thread.start()
        logger.info(
            "heartbeat_scheduler.started",
            interval_s=self._interval,
            poll_s=self._poll,
        )

    def stop(self, *, timeout_s: float = 5.0) -> None:
        """Signal the loop and join the thread. Idempotent."""
        if self._thread is None:
            return
        self._stop.set()
        self._thread.join(timeout=timeout_s)
        joined = not self._thread.is_alive()
        logger.info(
            "heartbeat_scheduler.stopped",
            joined=joined,
            enqueued_count=self._enqueued,
        )
        self._thread = None

    # ------------------------------------------------------------------ Loop body
    def _loop(self) -> None:
        next_tick_at = time.monotonic()
        while not self._stop.is_set():
            now = time.monotonic()
            if now >= next_tick_at:
                self._enqueue_one_tick()
                # schedule next on a fixed cadence to avoid drift
                next_tick_at = now + self._interval
            sleep_for = max(0.0, min(self._poll, next_tick_at - time.monotonic()))
            if sleep_for > 0:
                self._stop.wait(sleep_for)

    def _enqueue_one_tick(self) -> None:
        self._enqueued += 1
        self._last_enqueue_at = time.monotonic()
        task_id = f"{self._task_id_prefix}-{uuid4()}"
        payload: dict[str, Any] = {
            "scheduled_tick": self._enqueued,
            "scheduled_at": datetime.now(timezone.utc).isoformat(),
        }
        payload.update(self._payload_extra)
        try:
            self._queue.enqueue(
                TaskCreate(
                    id=task_id,
                    task_type=TASK_TYPE_HEARTBEAT,
                    assigned_to=self._assigned_to,
                    payload=payload,
                )
            )
            logger.debug(
                "heartbeat_scheduler.enqueued",
                task_id=task_id,
                count=self._enqueued,
            )
        except Exception as exc:
            # The scheduler MUST keep running even if a single enqueue fails.
            logger.error(
                "heartbeat_scheduler.enqueue_failed",
                error=str(exc),
                error_type=type(exc).__name__,
                exc_info=True,
            )

    # ------------------------------------------------------------------ Context mgr
    def __enter__(self) -> "HeartbeatScheduler":
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.stop()


__all__ = [
    "HeartbeatAgent",
    "HeartbeatScheduler",
    "TASK_TYPE_HEARTBEAT",
    "EVT_HEARTBEAT_TICK",
    "AGENT_ID",
    "RUNTIME_STATE_ACTIVE",
    "RUNTIME_STATE_DEGRADED",
    "RUNTIME_STATE_STOPPING",
]
