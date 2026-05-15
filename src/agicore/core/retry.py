"""Retry policy with exponential backoff + jitter.

Use as a decorator::

    @retry(max_attempts=5, initial_delay=0.1)
    def fetch():
        ...

Or programmatically::

    policy = RetryPolicy(max_attempts=3)
    result = policy.execute(lambda: fetch())
"""
from __future__ import annotations

import functools
import random
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

import structlog

logger = structlog.get_logger(__name__)

T = TypeVar("T")


class RetryError(Exception):
    """Raised when all retry attempts have been exhausted.

    The last underlying exception is available as `.__cause__`.
    """

    def __init__(self, message: str, attempts: int) -> None:
        super().__init__(message)
        self.attempts = attempts


@dataclass(frozen=True)
class RetryPolicy:
    """Configurable retry policy.

    Attributes
    ----------
    max_attempts : int
        Total attempts (including the first try). Must be >= 1.
    initial_delay : float
        Delay (s) before the second attempt.
    backoff_factor : float
        Multiplied at each subsequent delay.
    max_delay : float
        Hard ceiling on any single delay.
    jitter : bool
        If True, multiplies the delay by a random factor in [0.5, 1.5].
    retryable_exceptions : tuple
        Only these exception types trigger a retry. Default: Exception.
    """

    max_attempts: int = 3
    initial_delay: float = 0.1
    backoff_factor: float = 2.0
    max_delay: float = 30.0
    jitter: bool = True
    retryable_exceptions: tuple[type[BaseException], ...] = field(
        default_factory=lambda: (Exception,)
    )

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        if self.initial_delay < 0 or self.max_delay < 0:
            raise ValueError("delays must be >= 0")

    def compute_delay(self, attempt: int) -> float:
        """Delay (s) to wait *after* a failed attempt N before attempt N+1."""
        base = self.initial_delay * (self.backoff_factor ** (attempt - 1))
        capped = min(base, self.max_delay)
        if self.jitter:
            capped *= random.uniform(0.5, 1.5)
        return max(capped, 0.0)

    def execute(self, func: Callable[[], T]) -> T:
        """Execute func with retry. Raises RetryError on exhaustion."""
        last_exc: BaseException | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                result = func()
                if attempt > 1:
                    logger.info("retry.succeeded_after_failures", attempt=attempt)
                return result
            except self.retryable_exceptions as exc:
                last_exc = exc
                if attempt == self.max_attempts:
                    logger.error(
                        "retry.exhausted",
                        attempt=attempt,
                        max_attempts=self.max_attempts,
                        error=str(exc),
                        error_type=type(exc).__name__,
                    )
                    raise RetryError(
                        f"all {self.max_attempts} attempts failed",
                        attempts=attempt,
                    ) from exc
                delay = self.compute_delay(attempt)
                logger.warning(
                    "retry.attempt_failed",
                    attempt=attempt,
                    max_attempts=self.max_attempts,
                    next_delay_s=round(delay, 4),
                    error=str(exc),
                    error_type=type(exc).__name__,
                )
                time.sleep(delay)
        # Unreachable; appease type checker
        raise RetryError("unreachable", attempts=self.max_attempts) from last_exc


def retry(
    policy: RetryPolicy | None = None,
    **kwargs: Any,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator factory. Either pass a `policy=...` or keyword args for a fresh one.

    Examples
    --------
    >>> @retry(max_attempts=5, initial_delay=0.05)
    ... def call_external():
    ...     ...
    """
    if policy is not None and kwargs:
        raise ValueError("pass either `policy` or kwargs, not both")
    p = policy or RetryPolicy(**kwargs)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kw: Any) -> T:
            return p.execute(lambda: func(*args, **kw))

        return wrapper

    return decorator


__all__ = ["RetryPolicy", "RetryError", "retry"]
