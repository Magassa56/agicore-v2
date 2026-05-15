"""DryRunModeController — Phase 8H / 9A.

State machine for a deterministic dry-run session.

State transitions
-----------------
IDLE  ──start()──►  RUNNING  ──pause()──►  PAUSED
                        ▲                      │
                        └──────resume()─────────┘
                        │
                    stop() / emergency_stop()
                        │
                        ▼
                    STOPPED  (terminal)

Invariants
----------
- No random() — tick generation is deterministic (SHA-256 of inputs).
- Thread-safe: all mutable state behind threading.RLock.
- No wall-clock in replay paths.
"""
from __future__ import annotations

import hashlib
import threading
from datetime import datetime, timezone
from typing import Any

import structlog

from agicore.broker.alpaca_paper_adapter import AlpacaPaperBrokerAdapter
from agicore.dryrun.models import DryRunConfig, DryRunSessionSnapshot, DryRunState
from agicore.dryrun.recorder import DryRunRecorder, ExecutionRecorder, TickEvent

logger = structlog.get_logger(__name__)


class UnsafeModeTransitionError(RuntimeError):
    """Raised when a requested state transition violates the allowed graph."""


class DryRunModeController:
    """Controls the full lifecycle of a deterministic dry-run session.

    Parameters
    ----------
    config : DryRunConfig
        Immutable session configuration (session_id, symbols, mode, …).
    """

    def __init__(self, config: DryRunConfig) -> None:
        self._config = config
        self._lock = threading.RLock()
        self._state: DryRunState = DryRunState.IDLE
        self._ticks_processed: int = 0
        self._last_sequence: int = 0
        self._orders_submitted: int = 0
        self._fills: int = 0
        self._rejects: int = 0
        self._risk_blocks: int = 0
        self._recorder = DryRunRecorder()
        self._execution_recorder = ExecutionRecorder()
        self._events: list[str] = []
        self._adapter = AlpacaPaperBrokerAdapter(runtime_mode=config.runtime_mode)
        logger.info(
            "dryrun_controller.initialized",
            session_id=config.session_id,
            runtime_mode=config.runtime_mode,
            symbols=config.symbols,
        )

    # ---------------------------------------------------------------------- props

    @property
    def state(self) -> DryRunState:
        """Current session state (thread-safe read)."""
        with self._lock:
            return self._state

    @property
    def recorder(self) -> DryRunRecorder:
        """Tick event recorder. Safe to read from any thread."""
        return self._recorder

    @property
    def execution_recorder(self) -> ExecutionRecorder:
        """Order execution statistics recorder."""
        return self._execution_recorder

    # ---------------------------------------------------------------------- lifecycle

    def start(self) -> None:
        """Transition IDLE → RUNNING.

        Raises
        ------
        UnsafeModeTransitionError
            If the session is not in the IDLE state.
        """
        with self._lock:
            if self._state != DryRunState.IDLE:
                raise UnsafeModeTransitionError(
                    f"Cannot start: session is already {self._state.value!r}. "
                    "Only IDLE sessions can be started."
                )
            self._state = DryRunState.RUNNING
            self._events.append("start")
        logger.info("dryrun_controller.started", session_id=self._config.session_id)

    def stop(self) -> None:
        """Transition any non-terminal state → STOPPED (graceful)."""
        with self._lock:
            if self._state == DryRunState.STOPPED:
                return  # idempotent
            self._state = DryRunState.STOPPED
            self._events.append("stop")
        logger.info("dryrun_controller.stopped", session_id=self._config.session_id)

    def pause(self) -> None:
        """Transition RUNNING → PAUSED.

        Raises
        ------
        UnsafeModeTransitionError
            If the session is not RUNNING.
        """
        with self._lock:
            if self._state != DryRunState.RUNNING:
                raise UnsafeModeTransitionError(
                    f"Cannot pause: session is {self._state.value!r}. "
                    "Only RUNNING sessions can be paused."
                )
            self._state = DryRunState.PAUSED
            self._events.append("pause")
        logger.info("dryrun_controller.paused", session_id=self._config.session_id)

    def resume(self) -> None:
        """Transition PAUSED → RUNNING.

        Raises
        ------
        UnsafeModeTransitionError
            If the session is not PAUSED.
        """
        with self._lock:
            if self._state != DryRunState.PAUSED:
                raise UnsafeModeTransitionError(
                    f"Cannot resume: session is {self._state.value!r}. "
                    "Only PAUSED sessions can be resumed."
                )
            self._state = DryRunState.RUNNING
            self._events.append("resume")
        logger.info("dryrun_controller.resumed", session_id=self._config.session_id)

    def emergency_stop(self, *, reason: str = "") -> None:
        """Immediately stop from any state. Recorder is preserved intact."""
        with self._lock:
            prev = self._state
            self._state = DryRunState.STOPPED
            self._events.append(f"emergency_stop:{reason}")
        logger.warning(
            "dryrun_controller.emergency_stop",
            session_id=self._config.session_id,
            reason=reason,
            previous_state=prev.value,
        )

    # ---------------------------------------------------------------------- operations

    def run_ticks(self, n: int) -> None:
        """Simulate *n* synthetic market ticks. Deterministic by SHA-256.

        Parameters
        ----------
        n : int
            Number of ticks to generate.

        Raises
        ------
        UnsafeModeTransitionError
            If the session is not in RUNNING state.
        """
        with self._lock:
            if self._state != DryRunState.RUNNING:
                raise UnsafeModeTransitionError(
                    f"Cannot run ticks: session is {self._state.value!r}. "
                    "Must be RUNNING."
                )

        symbols = self._config.symbols
        n_symbols = len(symbols)
        session_id = self._config.session_id

        for _ in range(n):
            with self._lock:
                if self._state != DryRunState.RUNNING:
                    # Abort mid-batch if state changed (e.g. emergency_stop from another thread)
                    break
                self._last_sequence += 1
                seq = self._last_sequence
                self._ticks_processed += 1

            # Symbol cycling is deterministic: round-robin by sequence number
            symbol = symbols[seq % n_symbols]

            # Deterministic tick payload — no random(), no wall-clock
            tick_data = hashlib.sha256(
                f"{session_id}:{symbol}:{seq}".encode()
            ).hexdigest()

            event = TickEvent(
                sequence=seq,
                session_id=session_id,
                symbol=symbol,
                tick_data=tick_data,
            )
            self._recorder.record(event)

    def submit_order(self, symbol: str, quantity: float, side: str) -> dict[str, Any]:
        """Submit a synthetic order through the paper broker.

        Parameters
        ----------
        symbol : str
            Trading symbol (e.g. "AAPL").
        quantity : float
            Order size.
        side : str
            "buy" or "sell".

        Returns
        -------
        dict
            Broker response (synthetic fill or reject).

        Raises
        ------
        UnsafeModeTransitionError
            If the session is not RUNNING.
        """
        with self._lock:
            if self._state != DryRunState.RUNNING:
                raise UnsafeModeTransitionError(
                    f"Cannot submit order: session is {self._state.value!r}. "
                    "Must be RUNNING."
                )

        # Simulate an insufficient-funds reject for unrealistically large orders
        if quantity >= 999_999.0:
            status = "REJECT"
            result: dict[str, Any] = {
                "status": "REJECT",
                "symbol": symbol,
                "reason": "insufficient_funds",
            }
        else:
            result = self._adapter.submit_order(symbol, quantity, side)
            status = "FILL"

        with self._lock:
            self._orders_submitted += 1
            if status == "FILL":
                self._fills += 1
            else:
                self._rejects += 1

        self._execution_recorder.record_order(
            symbol, quantity, side, status=status, latency_ms=0.0
        )
        logger.info(
            "dryrun_controller.order_submitted",
            session_id=self._config.session_id,
            symbol=symbol,
            quantity=quantity,
            side=side,
            status=status,
        )
        return result

    def snapshot(self) -> DryRunSessionSnapshot:
        """Return a thread-safe point-in-time view of the session state."""
        with self._lock:
            return DryRunSessionSnapshot(
                session_id=self._config.session_id,
                state=self._state,
                ticks_processed=self._ticks_processed,
                orders_submitted=self._orders_submitted,
                fills=self._fills,
                rejects=self._rejects,
                risk_blocks=self._risk_blocks,
                last_sequence=self._last_sequence,
                config_fingerprint=hashlib.sha256(
                    self._config.session_id.encode()
                ).hexdigest(),
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

    def replay_equivalence_fingerprint(self) -> str:
        """Return a SHA-256 fingerprint of the full event stream + tick count.

        Two controllers with identical config and identical ``run_ticks(n)``
        calls will produce the same fingerprint. Idempotent.

        Returns
        -------
        str
            64-character hex string.
        """
        recorder_fp = self._recorder.compute_fingerprint()
        with self._lock:
            ticks = self._ticks_processed
        return hashlib.sha256(
            f"{recorder_fp}:{ticks}".encode()
        ).hexdigest()


__all__ = ["DryRunModeController", "UnsafeModeTransitionError"]
