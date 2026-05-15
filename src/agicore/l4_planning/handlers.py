"""Task handler protocol and registry.

A `TaskHandler` is any callable taking a `TaskRead` and returning a result dict.
The registry maps `task_type` → handler. The Dispatcher consults it.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol

import structlog

from agicore.l2_memory.schemas.task import TaskRead

logger = structlog.get_logger(__name__)


class TaskHandler(Protocol):
    """Callable handling a single task."""

    def __call__(self, task: TaskRead) -> dict[str, Any]: ...


class HandlerNotFoundError(KeyError):
    """No handler registered for the given task_type."""


class HandlerAlreadyRegisteredError(ValueError):
    """A handler is already registered for the given task_type."""


class HandlerRegistry:
    """In-memory registry of `task_type` → `TaskHandler`."""

    def __init__(self) -> None:
        self._handlers: dict[str, TaskHandler] = {}

    def register(
        self,
        task_type: str,
        handler: TaskHandler,
        *,
        replace: bool = False,
    ) -> None:
        """Register a handler. Use `replace=True` to overwrite an existing one."""
        if not replace and task_type in self._handlers:
            raise HandlerAlreadyRegisteredError(
                f"handler already registered for task_type={task_type!r}"
            )
        self._handlers[task_type] = handler
        logger.info("handler.registered", task_type=task_type, replace=replace)

    def unregister(self, task_type: str) -> None:
        if task_type in self._handlers:
            del self._handlers[task_type]
            logger.info("handler.unregistered", task_type=task_type)

    def get(self, task_type: str) -> TaskHandler:
        try:
            return self._handlers[task_type]
        except KeyError as exc:
            raise HandlerNotFoundError(
                f"no handler for task_type={task_type!r}"
            ) from exc

    def has(self, task_type: str) -> bool:
        return task_type in self._handlers

    def list_types(self) -> list[str]:
        return sorted(self._handlers.keys())


def make_callable_handler(func: Callable[[TaskRead], dict[str, Any]]) -> TaskHandler:
    """Promote a plain callable to TaskHandler (no-op at runtime — Protocol is structural)."""
    return func


__all__ = [
    "TaskHandler",
    "HandlerRegistry",
    "HandlerNotFoundError",
    "HandlerAlreadyRegisteredError",
    "make_callable_handler",
]
