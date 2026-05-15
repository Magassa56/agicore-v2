"""Dispatcher — routes a task to its registered handler. Stateless."""
from __future__ import annotations

from typing import Any

import structlog

from agicore.core.events import EVT_TASK_DISPATCHED, EventBus
from agicore.l2_memory.schemas.task import TaskRead

from .handlers import HandlerNotFoundError, HandlerRegistry

logger = structlog.get_logger(__name__)


class Dispatcher:
    """Stateless task router.

    Looks up the handler for `task.task_type` and invokes it. Emits
    `task.dispatched` on the EventBus before invoking, so observers can
    react before the handler runs.
    """

    def __init__(self, registry: HandlerRegistry, event_bus: EventBus | None = None) -> None:
        self._registry = registry
        self._bus = event_bus

    def dispatch(self, task: TaskRead) -> dict[str, Any]:
        """Route a task to its handler. Raises HandlerNotFoundError if absent."""
        try:
            handler = self._registry.get(task.task_type)
        except HandlerNotFoundError:
            logger.error(
                "dispatcher.handler_not_found",
                task_id=task.id,
                task_type=task.task_type,
                known_types=self._registry.list_types(),
            )
            raise

        if self._bus is not None:
            self._bus.emit(
                EVT_TASK_DISPATCHED,
                task_id=task.id,
                task_type=task.task_type,
                assigned_to=task.assigned_to,
            )

        logger.info(
            "dispatcher.dispatching",
            task_id=task.id,
            task_type=task.task_type,
            assigned_to=task.assigned_to,
        )
        result = handler(task)
        if not isinstance(result, dict):
            raise TypeError(
                f"handler for task_type={task.task_type!r} must return dict, "
                f"got {type(result).__name__}"
            )
        return result


__all__ = ["Dispatcher"]
