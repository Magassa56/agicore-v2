"""RuntimeMonitor — passive observability layer for AGIcore-v2.

Subscribes to lifecycle events on the EventBus, queries L2 memory through
existing repositories (read-only), and exposes structured snapshots of the
runtime state. Zero background threads, zero new abstractions.

Wired up explicitly after building a RuntimeEngine ::

    rt = RuntimeEngine(...)
    monitor = RuntimeMonitor(
        memory=rt.memory,
        event_bus=rt.event_bus,
        engine=rt.orchestrator._engine,
        queue=rt.queue,
        registry=rt.registry,
        shutdown=rt.shutdown_handler,
    )
    snapshot = monitor.get_runtime_status()

Constraints honored
-------------------
- Thread-safe via a single ``threading.RLock``.
- Zero ``print()``.
- No background threads. No timers. No external dependencies.
- Read-only against L2 (uses existing TaskRepository / MemoryService).
- No new abstraction at the architecture level — a single concrete observer.
"""
from __future__ import annotations

import threading
import time
from collections import Counter
from collections.abc import Callable
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

import structlog

from agicore.core.events import (
    EVT_TASK_CANCELLED,
    EVT_TASK_COMPLETED,
    EVT_TASK_CREATED,
    EVT_TASK_DISPATCHED,
    EVT_TASK_FAILED,
    EVT_TASK_RETRIED,
    EVT_TASK_STARTED,
    WILDCARD,
    Event,
    EventBus,
)
from agicore.core.shutdown import ShutdownHandler
from agicore.core.task_queue import TaskQueue
from agicore.l2_memory.adapters.sqlalchemy_engine import SqlAlchemyEngine
from agicore.l2_memory.models.task import (
    TASK_STATUS_COMPLETED,
    TASK_STATUS_FAILED,
    TASK_STATUS_PENDING,
    TASK_STATUS_RUNNING,
)
from agicore.l2_memory.repositories.task_repository import TaskRepository
from agicore.l2_memory.services.memory_service import MemoryService

# `HandlerRegistry` lives in l4_planning. Importing it at runtime would
# create a core → l4_planning dependency, but core is a base layer that
# l4_planning imports. We keep the type hint only.
if TYPE_CHECKING:  # pragma: no cover
    from agicore.l4_planning.handlers import HandlerRegistry

logger = structlog.get_logger(__name__)


# Heartbeat event type — read at runtime to avoid hard-coding agents/ deps.
# Kept as a constant string so the monitor stays domain-agnostic.
HEARTBEAT_EVENT_TYPE: str = "agent.heartbeat.tick"


class RuntimeMonitor:
    """Passive runtime observer.

    Parameters
    ----------
    memory : MemoryService
        Read-only access to LTM events.
    event_bus : EventBus
        Subscribed to all events (wildcard) for live counter updates.
    engine : SqlAlchemyEngine | None
        Optional. When provided, enables queue-depth and task-list inspection.
    queue : TaskQueue | None
        Optional. Reports cumulative ``enqueued_count``.
    registry : HandlerRegistry | None
        Optional. Reports registered handler types.
    shutdown : ShutdownHandler | None
        Optional. Reports ``is_stopping`` flag.
    """

    def __init__(
        self,
        *,
        memory: MemoryService,
        event_bus: EventBus,
        engine: SqlAlchemyEngine | None = None,
        queue: TaskQueue | None = None,
        registry: "HandlerRegistry | None" = None,
        shutdown: ShutdownHandler | None = None,
    ) -> None:
        self._memory = memory
        self._bus = event_bus
        self._engine = engine
        self._queue = queue
        self._registry = registry
        self._shutdown = shutdown

        self._lock = threading.RLock()
        self._counters: Counter[str] = Counter()
        self._events_by_type: Counter[str] = Counter()
        self._last_event_at: datetime | None = None
        self._last_heartbeat_at: datetime | None = None
        self._last_heartbeat_counter: int | None = None
        self._last_error: dict[str, Any] | None = None

        self._monotonic_start = time.monotonic()
        self._wallclock_start = datetime.now(timezone.utc)
        self._last_reset_at: datetime = self._wallclock_start

        self._unsub: list[Callable[[], None]] = []
        self._attach()

    # ------------------------------------------------------------------ Lifecycle
    def _attach(self) -> None:
        self._unsub.append(self._bus.subscribe(WILDCARD, self._on_event))
        logger.info("runtime_monitor.attached")

    def detach(self) -> None:
        """Unsubscribe from the bus. Idempotent."""
        for u in list(self._unsub):
            try:
                u()
            except Exception as exc:  # pragma: no cover
                logger.warning("runtime_monitor.unsubscribe_failed", error=str(exc))
        self._unsub.clear()
        logger.info("runtime_monitor.detached")

    def __enter__(self) -> "RuntimeMonitor":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.detach()

    # ------------------------------------------------------------------ Bus handler
    def _on_event(self, event: Event) -> None:
        with self._lock:
            self._events_by_type[event.event_type] += 1
            self._last_event_at = event.timestamp

            t = event.event_type
            if t == EVT_TASK_CREATED:
                self._counters["tasks_created"] += 1
            elif t == EVT_TASK_DISPATCHED:
                self._counters["tasks_dispatched"] += 1
            elif t == EVT_TASK_STARTED:
                self._counters["tasks_started"] += 1
            elif t == EVT_TASK_COMPLETED:
                self._counters["tasks_completed"] += 1
            elif t == EVT_TASK_FAILED:
                self._counters["tasks_failed"] += 1
                self._last_error = {
                    "task_id": event.payload.get("task_id"),
                    "error": event.payload.get("error"),
                    "timestamp": event.timestamp.isoformat(),
                }
            elif t == EVT_TASK_RETRIED:
                self._counters["tasks_retried"] += 1
            elif t == EVT_TASK_CANCELLED:
                self._counters["tasks_cancelled"] += 1
            elif t == HEARTBEAT_EVENT_TYPE:
                self._last_heartbeat_at = event.timestamp
                raw = event.payload.get("counter")
                if raw is not None:
                    try:
                        self._last_heartbeat_counter = int(raw)
                    except (TypeError, ValueError):
                        pass

    # ------------------------------------------------------------------ Public API
    def get_runtime_status(self) -> dict[str, Any]:
        """Snapshot of the live runtime — uptime, handlers, queue depth."""
        with self._lock:
            return {
                "started_at_utc": self._wallclock_start.isoformat(),
                "uptime_s": round(time.monotonic() - self._monotonic_start, 3),
                "is_stopping": (
                    self._shutdown.is_stopping() if self._shutdown is not None else False
                ),
                "handlers_registered": (
                    self._registry.list_types() if self._registry is not None else []
                ),
                "queue_enqueued_total": (
                    self._queue.enqueued_count if self._queue is not None else None
                ),
                "queue_depth_pending": self._count_pending_tasks(),
                "tasks_running": self._count_tasks_with_status(TASK_STATUS_RUNNING),
                "last_event_at_utc": (
                    self._last_event_at.isoformat() if self._last_event_at else None
                ),
                "last_heartbeat_at_utc": (
                    self._last_heartbeat_at.isoformat()
                    if self._last_heartbeat_at else None
                ),
                "last_heartbeat_counter": self._last_heartbeat_counter,
            }

    def get_metrics(self) -> dict[str, Any]:
        """Cumulative counters since the last reset."""
        with self._lock:
            return {
                "tasks_created": int(self._counters["tasks_created"]),
                "tasks_dispatched": int(self._counters["tasks_dispatched"]),
                "tasks_started": int(self._counters["tasks_started"]),
                "tasks_completed": int(self._counters["tasks_completed"]),
                "tasks_failed": int(self._counters["tasks_failed"]),
                "tasks_retried": int(self._counters["tasks_retried"]),
                "tasks_cancelled": int(self._counters["tasks_cancelled"]),
                "events_total": int(sum(self._events_by_type.values())),
                "events_by_type": dict(self._events_by_type),
                "last_error": dict(self._last_error) if self._last_error else None,
                "last_reset_at_utc": self._last_reset_at.isoformat(),
            }

    def get_recent_activity(self, limit: int = 20) -> dict[str, Any]:
        """Recent LTM events + per-status task lists."""
        if limit <= 0:
            raise ValueError("limit must be > 0")
        recent_events = self._memory.get_recent_events(limit=limit)
        return {
            "limit": limit,
            "events": [
                {
                    "id": e.id,
                    "event_type": e.event_type,
                    "task_id": e.task_id,
                    "agent_id": e.agent_id,
                    "session_id": e.session_id,
                    "created_at": e.created_at.isoformat(),
                    "payload": dict(e.payload),
                }
                for e in recent_events
            ],
            "pending_tasks": self._list_tasks(TASK_STATUS_PENDING, limit=limit),
            "completed_tasks": self._list_tasks(TASK_STATUS_COMPLETED, limit=limit),
            "failed_tasks": self._list_tasks(TASK_STATUS_FAILED, limit=limit),
        }

    def reset_metrics(self) -> None:
        """Zero all counters and clear the last error. Uptime is preserved."""
        with self._lock:
            self._counters.clear()
            self._events_by_type.clear()
            self._last_event_at = None
            self._last_heartbeat_at = None
            self._last_heartbeat_counter = None
            self._last_error = None
            self._last_reset_at = datetime.now(timezone.utc)
        logger.info("runtime_monitor.metrics_reset")

    # ------------------------------------------------------------------ Helpers
    def _count_pending_tasks(self) -> int | None:
        return self._count_tasks_with_status(TASK_STATUS_PENDING)

    def _count_tasks_with_status(self, status: str) -> int | None:
        if self._engine is None:
            return None
        try:
            with self._engine.session() as s:
                repo = TaskRepository(s)
                rows = repo.list_by_status(status, limit=10000)
            return len(rows)
        except Exception as exc:
            logger.warning(
                "runtime_monitor.count_tasks_failed", status=status, error=str(exc)
            )
            return None

    def _list_tasks(self, status: str, *, limit: int) -> list[dict[str, Any]]:
        if self._engine is None:
            return []
        try:
            with self._engine.session() as s:
                repo = TaskRepository(s)
                tasks = repo.list_by_status(status, limit=limit)
            return [
                {
                    "id": t.id,
                    "task_type": t.task_type,
                    "status": t.status,
                    "assigned_to": t.assigned_to,
                    "created_at": t.created_at.isoformat(),
                    "updated_at": t.updated_at.isoformat(),
                    "error": t.error,
                }
                for t in tasks
            ]
        except Exception as exc:
            logger.warning(
                "runtime_monitor.list_tasks_failed", status=status, error=str(exc)
            )
            return []


__all__ = ["RuntimeMonitor", "HEARTBEAT_EVENT_TYPE"]
