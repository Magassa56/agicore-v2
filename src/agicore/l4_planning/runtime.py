"""RuntimeEngine — AGIcore-v2 Runtime Engine v1.

Single entry point that wires every Phase 3 component together :
- structured logging
- L2 memory (SQLite STM + SQLAlchemy LTM)
- handler registry
- dispatcher
- orchestrator (task lifecycle)
- task queue (enqueue + wakeup)
- execution loop (consumer)
- event bus (lifecycle propagation)
- retry policy
- graceful shutdown (signals + drain)

Pipeline executed end-to-end on each enqueue() :
    receive → enqueue → dispatch → execute → log → persist memory → feedback
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

import structlog

from agicore.core.events import EventBus
from agicore.core.logging import configure_logging
from agicore.core.retry import RetryPolicy
from agicore.core.shutdown import ShutdownHandler
from agicore.core.task_queue import TaskQueue
from agicore.l2_memory.adapters.sqlalchemy_engine import SqlAlchemyEngine
from agicore.l2_memory.migrations.init_schema import init_schema
from agicore.l2_memory.schemas.task import TaskCreate, TaskRead
from agicore.l2_memory.services.memory_service import MemoryService

from .dispatcher import Dispatcher
from .execution_loop import ExecutionLoop
from .handlers import HandlerRegistry, TaskHandler
from .orchestrator import AgentOrchestrator

logger = structlog.get_logger(__name__)


class RuntimeEngine:
    """AGIcore Runtime Engine — Phase 3 v1."""

    def __init__(
        self,
        *,
        db_url: str = "sqlite:///:memory:",
        retry_policy: RetryPolicy | None = None,
        event_bus: EventBus | None = None,
        poll_interval: float = 0.5,
        batch_size: int = 10,
        configure_logging_now: bool = False,
        log_level: str = "INFO",
        log_json: bool = True,
        install_signal_handlers: bool = False,
    ) -> None:
        if configure_logging_now:
            configure_logging(level=log_level, json=log_json)

        # L2 memory
        self._engine = SqlAlchemyEngine(db_url)
        init_schema(self._engine)
        self._memory = MemoryService(self._engine)

        # L4 wiring
        self._registry = HandlerRegistry()
        self._event_bus = event_bus or EventBus()
        self._dispatcher = Dispatcher(self._registry, self._event_bus)
        self._orchestrator = AgentOrchestrator(
            memory=self._memory,
            engine=self._engine,
            dispatcher=self._dispatcher,
            event_bus=self._event_bus,
            retry_policy=retry_policy or RetryPolicy(max_attempts=3, initial_delay=0.1),
        )

        # Shutdown coordinator (stop_event shared with the loop)
        self._shutdown = ShutdownHandler()

        # Loop + queue share a wakeup event
        self._loop = ExecutionLoop(
            self._orchestrator,
            poll_interval=poll_interval,
            batch_size=batch_size,
            stop_event=self._shutdown.stop_event,
        )
        self._queue = TaskQueue(
            self._orchestrator,
            wakeup=self._loop.wakeup_event,
        )

        if install_signal_handlers:
            self._shutdown.install_signal_handlers()

        logger.info(
            "runtime.initialized",
            db_url=db_url,
            poll_interval=poll_interval,
            batch_size=batch_size,
        )

    # ------------------------------------------------------------------ Public surface
    @property
    def memory(self) -> MemoryService:
        return self._memory

    @property
    def event_bus(self) -> EventBus:
        return self._event_bus

    @property
    def queue(self) -> TaskQueue:
        return self._queue

    @property
    def loop(self) -> ExecutionLoop:
        return self._loop

    @property
    def orchestrator(self) -> AgentOrchestrator:
        return self._orchestrator

    @property
    def registry(self) -> HandlerRegistry:
        return self._registry

    @property
    def shutdown_handler(self) -> ShutdownHandler:
        return self._shutdown

    # ------------------------------------------------------------------ Operations
    def register_handler(
        self,
        task_type: str,
        handler: TaskHandler,
        *,
        replace: bool = False,
    ) -> None:
        """Register a handler for a task type."""
        self._registry.register(task_type, handler, replace=replace)

    def submit(self, task: TaskCreate) -> TaskRead:
        """Submit a task : persist + wake the loop."""
        return self._queue.enqueue(task)

    def subscribe(
        self, event_type: str, handler: Callable[[Any], None]
    ) -> Callable[[], None]:
        """Subscribe to a lifecycle event. Returns an unsubscribe callable."""
        return self._event_bus.subscribe(event_type, handler)

    def run_once(self) -> int:
        """Single drain cycle. Returns number of tasks finished."""
        return self._loop.run_once()

    def run_forever(self, *, max_iterations: int | None = None) -> int:
        """Block until shutdown is triggered. Returns total executed."""
        return self._loop.run_forever(max_iterations=max_iterations)

    def stop(self) -> None:
        """Signal a graceful stop. Loop will exit at the next safe point."""
        self._shutdown.trigger()
        self._loop.stop()

    def shutdown(self) -> None:
        """Full graceful teardown : stop loop, dispose engine, uninstall signals."""
        self.stop()
        self._shutdown.uninstall_signal_handlers()
        self._engine.dispose()
        logger.info("runtime.shutdown_complete")

    # ------------------------------------------------------------------ Context manager
    def __enter__(self) -> "RuntimeEngine":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.shutdown()


__all__ = ["RuntimeEngine"]
