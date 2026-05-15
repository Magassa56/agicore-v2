"""EchoAgent — minimal reference handler for AGIcore-v2 Runtime.

Purpose
-------
Prove the Runtime Engine can execute a real task end-to-end. This is the
canonical reference implementation of a `TaskHandler` and serves as a
permanent smoke-test handler.

Logic
-----
For each incoming task :
1. Hash the input payload (idempotency tracking).
2. Persist a domain-specific `agent.echo.processed` event in LTM.
3. Optionally emit the same event on the EventBus.
4. Return structured feedback containing the echoed payload, latency,
   timestamps, and execution metadata.

Task type
---------
Registered under the canonical task_type `agent.echo`.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

import structlog

from agicore.core.events import EventBus
from agicore.l2_memory.schemas.task import TaskRead
from agicore.l2_memory.services.memory_service import MemoryService

logger = structlog.get_logger(__name__)


# Canonical task type for this handler
TASK_TYPE_ECHO: str = "agent.echo"

# Domain event emitted by this agent (in addition to lifecycle events)
EVT_ECHO_PROCESSED: str = "agent.echo.processed"

# Stable agent identifier — used in logs, events, and feedback
AGENT_ID: str = "echo_agent"


class EchoAgent:
    """Minimal callable handler conforming to `TaskHandler` protocol.

    Instances are stateful only for a process-local processed counter (used
    in feedback and tests). All persistent state goes through `MemoryService`.

    Parameters
    ----------
    memory : MemoryService
        Required. Used to persist the domain-specific event.
    event_bus : EventBus | None
        Optional. If provided, also publishes `agent.echo.processed`.

    Examples
    --------
    >>> rt = RuntimeEngine(...)
    >>> rt.register_handler(TASK_TYPE_ECHO, EchoAgent(rt.memory, rt.event_bus))
    >>> rt.submit(TaskCreate(id="t-1", task_type=TASK_TYPE_ECHO, payload={"x": 1}))
    """

    def __init__(
        self,
        memory: MemoryService,
        event_bus: EventBus | None = None,
    ) -> None:
        self._memory = memory
        self._bus = event_bus
        self._processed_count = 0

    @property
    def processed_count(self) -> int:
        """Number of tasks this instance has handled. Process-local."""
        return self._processed_count

    @property
    def agent_id(self) -> str:
        return AGENT_ID

    def __call__(self, task: TaskRead) -> dict[str, Any]:
        """TaskHandler protocol — synchronous, returns structured feedback dict."""
        started_at = datetime.now(timezone.utc)

        payload_hash = self._hash_payload(task.payload)

        logger.info(
            "echo_agent.received",
            task_id=task.id,
            payload_keys=sorted(task.payload.keys()),
            payload_hash=payload_hash,
        )

        # Persist a domain-specific event in LTM (in addition to lifecycle
        # events emitted by the orchestrator).
        self._memory.create_event(
            EVT_ECHO_PROCESSED,
            task_id=task.id,
            agent_id=AGENT_ID,
            payload={
                "input_keys": sorted(task.payload.keys()),
                "input_hash": payload_hash,
            },
        )

        # Optional — propagate on the in-process event bus
        if self._bus is not None:
            self._bus.emit(
                EVT_ECHO_PROCESSED,
                task_id=task.id,
                payload_hash=payload_hash,
            )

        self._processed_count += 1
        finished_at = datetime.now(timezone.utc)
        latency_ms = (finished_at - started_at).total_seconds() * 1000.0

        feedback: dict[str, Any] = {
            "echoed": dict(task.payload),
            "task_id": task.id,
            "agent_id": AGENT_ID,
            "started_at": started_at.isoformat(),
            "finished_at": finished_at.isoformat(),
            "latency_ms": round(latency_ms, 3),
            "payload_hash": payload_hash,
            "processed_count": self._processed_count,
        }

        logger.info(
            "echo_agent.completed",
            task_id=task.id,
            latency_ms=feedback["latency_ms"],
            processed_count=self._processed_count,
        )
        return feedback

    @staticmethod
    def _hash_payload(payload: dict[str, Any]) -> str:
        """SHA-256 truncated to 16 hex chars — deterministic for equal payloads."""
        encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()[:16]


__all__ = [
    "EchoAgent",
    "TASK_TYPE_ECHO",
    "EVT_ECHO_PROCESSED",
    "AGENT_ID",
]
