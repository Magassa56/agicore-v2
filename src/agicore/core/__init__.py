"""AGIcore-v2 — core utilities (logging, retry, events, queue, shutdown,
runtime_monitor)."""
from .events import (
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
    Handler,
)
from .logging import bind_context, clear_context, configure_logging, get_logger
from .retry import RetryError, RetryPolicy, retry
from .runtime_monitor import HEARTBEAT_EVENT_TYPE, RuntimeMonitor
from .shutdown import DEFAULT_SIGNALS, ShutdownHandler
from .task_queue import TaskQueue

__all__ = [
    # logging
    "configure_logging",
    "bind_context",
    "clear_context",
    "get_logger",
    # retry
    "RetryPolicy",
    "RetryError",
    "retry",
    # events
    "Event",
    "EventBus",
    "Handler",
    "WILDCARD",
    "EVT_TASK_CREATED",
    "EVT_TASK_DISPATCHED",
    "EVT_TASK_STARTED",
    "EVT_TASK_COMPLETED",
    "EVT_TASK_FAILED",
    "EVT_TASK_RETRIED",
    "EVT_TASK_CANCELLED",
    # queue + shutdown
    "TaskQueue",
    "ShutdownHandler",
    "DEFAULT_SIGNALS",
    # observability
    "RuntimeMonitor",
    "HEARTBEAT_EVENT_TYPE",
]
