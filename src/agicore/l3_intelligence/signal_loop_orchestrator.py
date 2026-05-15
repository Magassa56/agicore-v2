"""SignalLoopOrchestrator — Phase 8B + Phase 8D risk gate.

Passive event-driven coordinator that wires :

    MarketFeed (L1) ─► Strategy ─► [optional Risk gate (8D)] ─► TaskQueue ─► Execution

Backward-compatible : when no ``risk_manager`` is configured, behavior is
identical to Phase 8B. When a ``risk_manager`` (and a paired
``snapshot_provider``) is configured, every non-HOLD signal is converted
to an ``ExecutionIntent`` and validated BEFORE submission. Blocked
intents NEVER reach the TaskQueue.

Bus events emitted
------------------
- ``agent.signal_loop.signal``  : every non-HOLD signal (when ``emit_signals``)
- ``agent.signal_loop.blocked`` : every signal blocked by the risk gate
                                  (subscribers can react to risk decisions)

Plus the underlying ``RiskManager`` emits ``risk.check.passed`` /
``risk.check.blocked`` on the same bus when configured with one — those
are NOT duplicated by the orchestrator.
"""
from __future__ import annotations

import threading
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any, Protocol
from uuid import uuid4

import structlog

from agicore.agents.execution_agent import TASK_TYPE_ORDER
from agicore.core.events import Event, EventBus
from agicore.core.task_queue import TaskQueue
from agicore.l1_perception.market_models import EVT_MARKET_TICK
from agicore.l2_memory.schemas.task import TaskCreate
from agicore.risk.exposure_models import (
    ExecutionIntent,
    ExposureSnapshot,
    IntentSide,
)
from agicore.risk.risk_manager import RiskManager
from agicore.strategy.signal_models import Action, OHLCV

logger = structlog.get_logger(__name__)


# Canonical identifiers
ORCHESTRATOR_ID: str = "signal_loop_orchestrator"
EVT_SIGNAL_GENERATED: str = "agent.signal_loop.signal"
EVT_SIGNAL_BLOCKED: str = "agent.signal_loop.blocked"


class _StrategyProtocol(Protocol):
    name: str
    def on_bar(self, bar: OHLCV) -> Any: ...


SnapshotProvider = Callable[[], ExposureSnapshot]


class SignalLoopOrchestrator:
    """Bridges market ticks to execution tasks via a strategy.

    Optional risk gate
    ------------------
    Pass ``risk_manager`` and ``snapshot_provider`` together to activate
    the Phase 8D risk gate. Each non-HOLD signal becomes an
    ``ExecutionIntent`` validated against a fresh snapshot ; only passed
    intents reach the TaskQueue.

    Parameters
    ----------
    event_bus : EventBus
    task_queue : TaskQueue
    strategy : object with ``on_bar(OHLCV) -> Signal``
    symbol : str
    order_quantity : float (> 0)
    emit_signals : bool, default True
    order_id_prefix : str, default "sig"
    risk_manager : RiskManager | None, default None
    snapshot_provider : Callable[[], ExposureSnapshot] | None, default None
        Required when ``risk_manager`` is given. Called fresh on each
        non-HOLD signal so the gate sees up-to-date state.
    """

    def __init__(
        self,
        event_bus: EventBus,
        task_queue: TaskQueue,
        strategy: _StrategyProtocol,
        *,
        symbol: str,
        order_quantity: float,
        emit_signals: bool = True,
        order_id_prefix: str = "sig",
        risk_manager: RiskManager | None = None,
        snapshot_provider: SnapshotProvider | None = None,
    ) -> None:
        if not symbol:
            raise ValueError("symbol must be non-empty")
        if order_quantity <= 0:
            raise ValueError("order_quantity must be > 0")
        if risk_manager is not None and snapshot_provider is None:
            raise ValueError("risk_manager requires snapshot_provider")
        if snapshot_provider is not None and risk_manager is None:
            raise ValueError("snapshot_provider requires risk_manager")

        self._bus = event_bus
        self._queue = task_queue
        self._strategy = strategy
        self._symbol = symbol
        self._qty = float(order_quantity)
        self._emit = bool(emit_signals)
        self._prefix = str(order_id_prefix)
        self._risk = risk_manager
        self._snapshot_provider = snapshot_provider

        self._lock = threading.RLock()
        self._unsub: Callable[[], None] | None = None
        self._is_attached = False
        self._tick_count = 0
        self._signal_count = 0
        self._submitted_count = 0
        self._blocked_count = 0
        self._last_signal_action: str | None = None
        self._last_block_codes: list[str] = []

    # ------------------------------------------------------------------ Inspection
    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def order_quantity(self) -> float:
        return self._qty

    @property
    def is_attached(self) -> bool:
        return self._is_attached

    @property
    def has_risk_gate(self) -> bool:
        return self._risk is not None

    @property
    def tick_count(self) -> int:
        with self._lock:
            return self._tick_count

    @property
    def signal_count(self) -> int:
        with self._lock:
            return self._signal_count

    @property
    def submitted_count(self) -> int:
        with self._lock:
            return self._submitted_count

    @property
    def blocked_count(self) -> int:
        with self._lock:
            return self._blocked_count

    @property
    def last_signal_action(self) -> str | None:
        with self._lock:
            return self._last_signal_action

    @property
    def last_block_codes(self) -> list[str]:
        with self._lock:
            return list(self._last_block_codes)

    # ------------------------------------------------------------------ Lifecycle
    def attach(self) -> None:
        if self._is_attached:
            return
        self._unsub = self._bus.subscribe(EVT_MARKET_TICK, self._on_tick)
        self._is_attached = True
        logger.info(
            "signal_loop.attached",
            symbol=self._symbol,
            order_quantity=self._qty,
            risk_gate=self.has_risk_gate,
            strategy=getattr(self._strategy, "name",
                             str(type(self._strategy).__name__)),
        )

    def detach(self) -> None:
        if not self._is_attached:
            return
        if self._unsub is not None:
            try:
                self._unsub()
            except Exception as exc:  # pragma: no cover
                logger.warning("signal_loop.unsub_failed", error=str(exc))
        self._unsub = None
        self._is_attached = False
        logger.info("signal_loop.detached", symbol=self._symbol)

    def __enter__(self) -> "SignalLoopOrchestrator":
        self.attach()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.detach()

    # ------------------------------------------------------------------ Tick handler
    def _on_tick(self, event: Event) -> None:
        payload = event.payload
        if payload.get("symbol") != self._symbol:
            return

        bar = self._tick_to_ohlcv(payload)
        if bar is None:
            logger.warning("signal_loop.malformed_tick",
                           symbol=payload.get("symbol"))
            return

        try:
            signal = self._strategy.on_bar(bar)
        except Exception as exc:
            logger.error("signal_loop.strategy_failed",
                         symbol=self._symbol, error=str(exc), exc_info=True)
            return

        with self._lock:
            self._tick_count += 1
            action = getattr(signal, "action", None)
            if action is not None:
                self._last_signal_action = (
                    action.value if hasattr(action, "value") else str(action)
                )
            if action != Action.HOLD:
                self._signal_count += 1

        if action == Action.HOLD or action is None:
            return

        if self._emit:
            self._bus.emit(
                EVT_SIGNAL_GENERATED,
                symbol=self._symbol,
                action=self._last_signal_action,
                price=bar.close,
                reason=getattr(signal, "reason", ""),
                strategy=getattr(self._strategy, "name", "?"),
            )

        # ============== Risk gate (Phase 8D) ==============
        if self._risk is not None:
            if not self._gate_passes(action, bar):
                return  # blocked — do NOT submit

        self._submit_order(action, bar)

    def _gate_passes(self, action: Action, bar: OHLCV) -> bool:
        """Build an ExecutionIntent, fetch snapshot, run RiskManager.
        Returns True if order should proceed, False if blocked."""
        assert self._risk is not None
        assert self._snapshot_provider is not None

        side = IntentSide.BUY if action == Action.BUY else IntentSide.SELL
        intent_id = f"{self._prefix}-intent-{uuid4()}"
        intent = ExecutionIntent(
            intent_id=intent_id,
            symbol=self._symbol,
            side=side,
            quantity=self._qty,
            estimated_price=bar.close,
            timestamp=bar.timestamp,
        )

        try:
            snapshot = self._snapshot_provider()
        except Exception as exc:
            logger.error(
                "signal_loop.snapshot_provider_failed",
                symbol=self._symbol, error=str(exc), exc_info=True,
            )
            # Fail closed — block on snapshot failure to be safe
            with self._lock:
                self._blocked_count += 1
                self._last_block_codes = ["SNAPSHOT_PROVIDER_FAILED"]
            return False

        try:
            result = self._risk.validate(intent, snapshot)
        except Exception as exc:
            logger.error(
                "signal_loop.risk_manager_failed",
                symbol=self._symbol, intent_id=intent_id,
                error=str(exc), exc_info=True,
            )
            with self._lock:
                self._blocked_count += 1
                self._last_block_codes = ["RISK_MANAGER_ERROR"]
            return False

        if result.passed:
            return True

        # Blocked — record + emit
        codes = [v.code.value for v in result.violations]
        with self._lock:
            self._blocked_count += 1
            self._last_block_codes = codes
        if self._emit:
            self._bus.emit(
                EVT_SIGNAL_BLOCKED,
                symbol=self._symbol,
                action=self._last_signal_action,
                price=bar.close,
                intent_id=intent_id,
                violation_codes=codes,
                strategy=getattr(self._strategy, "name", "?"),
            )
        logger.warning(
            "signal_loop.signal_blocked",
            symbol=self._symbol, intent_id=intent_id,
            action=self._last_signal_action, codes=codes,
        )
        return False

    def _submit_order(self, action: Action, bar: OHLCV) -> None:
        side = "BUY" if action == Action.BUY else "SELL"
        client_order_id = f"{self._prefix}-{uuid4()}"
        task_id = f"sigtask-{uuid4()}"
        try:
            self._queue.enqueue(
                TaskCreate(
                    id=task_id,
                    task_type=TASK_TYPE_ORDER,
                    assigned_to=ORCHESTRATOR_ID,
                    payload={
                        "symbol": self._symbol,
                        "side": side,
                        "quantity": self._qty,
                        "client_order_id": client_order_id,
                    },
                )
            )
        except Exception as exc:
            logger.error("signal_loop.enqueue_failed",
                         task_id=task_id, side=side, error=str(exc),
                         exc_info=True)
            return

        with self._lock:
            self._submitted_count += 1
        logger.info(
            "signal_loop.order_submitted",
            task_id=task_id, client_order_id=client_order_id,
            symbol=self._symbol, side=side, quantity=self._qty,
            tick_price=bar.close,
        )

    @staticmethod
    def _tick_to_ohlcv(payload: dict[str, Any]) -> OHLCV | None:
        try:
            ts_raw = payload["timestamp"]
            if isinstance(ts_raw, datetime):
                ts = ts_raw if ts_raw.tzinfo else ts_raw.replace(tzinfo=timezone.utc)
            else:
                ts = datetime.fromisoformat(str(ts_raw))
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
            price = float(payload["price"])
            if price <= 0:
                return None
            return OHLCV(
                timestamp=ts, open=price, high=price, low=price,
                close=price, volume=float(payload.get("volume", 0.0)),
            )
        except (KeyError, ValueError, TypeError):
            return None


__all__ = [
    "SignalLoopOrchestrator",
    "SnapshotProvider",
    "ORCHESTRATOR_ID",
    "EVT_SIGNAL_GENERATED",
    "EVT_SIGNAL_BLOCKED",
]
