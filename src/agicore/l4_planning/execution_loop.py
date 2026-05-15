"""ExecutionLoop — minimal polling driver around the orchestrator.

Single thread, no asyncio. Honours both:
- a `stop_event` (permanent exit)
- a `wakeup_event` (early polling, pulsed by TaskQueue.enqueue)

The two can be the same event (default) or supplied externally for
coordination with TaskQueue and ShutdownHandler.
"""
from __future__ import annotations

from threading import Event as ThreadEvent

import structlog

from .orchestrator import AgentOrchestrator

logger = structlog.get_logger(__name__)


class ExecutionLoop:
    """Polls pending tasks at a fixed interval and executes them."""

    def __init__(
        self,
        orchestrator: AgentOrchestrator,
        *,
        poll_interval: float = 1.0,
        batch_size: int = 10,
        stop_event: ThreadEvent | None = None,
        wakeup_event: ThreadEvent | None = None,
    ) -> None:
        if poll_interval < 0:
            raise ValueError("poll_interval must be >= 0")
        if batch_size < 1:
            raise ValueError("batch_size must be >= 1")
        self._orch = orchestrator
        self._poll = poll_interval
        self._batch = batch_size
        self._stop = stop_event or ThreadEvent()
        self._wake = wakeup_event or ThreadEvent()

    @property
    def stop_event(self) -> ThreadEvent:
        return self._stop

    @property
    def wakeup_event(self) -> ThreadEvent:
        return self._wake

    def run_once(self) -> int:
        finished = self._orch.execute_pending(limit=self._batch)
        if finished:
            logger.info("execution_loop.cycle", executed=len(finished))
        return len(finished)

    def run_forever(self, *, max_iterations: int | None = None) -> int:
        """Loop until stop or max_iterations. Returns total executed."""
        total = 0
        iteration = 0
        logger.info(
            "execution_loop.starting", poll_s=self._poll, batch=self._batch
        )
        while not self._stop.is_set():
            iteration += 1
            total += self.run_once()
            if max_iterations is not None and iteration >= max_iterations:
                logger.info(
                    "execution_loop.max_iterations_reached", iteration=iteration
                )
                break
            # Wake on either: stop signal OR wakeup pulse OR timeout
            self._wake.wait(self._poll)
            # Consume the pulse only if we weren't stopped
            if not self._stop.is_set():
                self._wake.clear()
        logger.info(
            "execution_loop.stopped", total_executed=total, iterations=iteration
        )
        return total

    def stop(self) -> None:
        """Signal exit. Also pulses wakeup so the loop unblocks immediately."""
        self._stop.set()
        self._wake.set()
        logger.info("execution_loop.stop_requested")

    def is_running(self) -> bool:
        return not self._stop.is_set()

    def wakeup(self) -> None:
        """Force an immediate poll (without exiting)."""
        self._wake.set()


__all__ = ["ExecutionLoop"]
