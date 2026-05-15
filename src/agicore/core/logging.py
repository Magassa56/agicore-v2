"""Structured logging — structlog + stdlib logging.

Single source of truth for logging configuration. Call `configure_logging()`
once at application boot. After that, `structlog.get_logger(__name__)` from
anywhere yields a configured BoundLogger emitting JSON (or pretty-printed
console output in dev).

NEVER use print() in AGIcore-v2. Always go through structlog.
"""
from __future__ import annotations

import logging
import sys
from typing import Any

import structlog


_DEFAULT_PROCESSORS_PRE: list[Any] = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.processors.TimeStamper(fmt="iso", utc=True),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
]


def configure_logging(
    *,
    level: str = "INFO",
    json: bool = True,
    stream: Any = None,
) -> None:
    """Configure structlog + stdlib logging. Idempotent.

    Parameters
    ----------
    level : str
        Log level name (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    json : bool
        If True, emits JSON lines (production). If False, ConsoleRenderer (dev).
    stream :
        Optional output stream. Defaults to sys.stdout.
    """
    out = stream if stream is not None else sys.stdout

    logging.basicConfig(
        format="%(message)s",
        stream=out,
        level=getattr(logging, level.upper()),
        force=True,  # idempotent reconfiguration
    )

    processors = list(_DEFAULT_PROCESSORS_PRE)
    if json:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=False))

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def bind_context(**kwargs: Any) -> None:
    """Bind context vars propagated to every log call in the current context."""
    structlog.contextvars.bind_contextvars(**kwargs)


def clear_context() -> None:
    """Clear all bound context vars."""
    structlog.contextvars.clear_contextvars()


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Convenience wrapper to keep a stable import path within agicore.core."""
    return structlog.get_logger(name)


__all__ = ["configure_logging", "bind_context", "clear_context", "get_logger"]
