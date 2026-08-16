"""Deterministic signal-to-TaskQueue proposal orchestrator.

Risk is evaluated only by the canonical L5 ExecutionService.  This loop
keeps signal/HOLD accounting and emits explicit execution proposals; it never
calls RiskManager itself.
"""
from __future__ import annotations

import hashlib
import json
import threading
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any, Protocol

import structlog

from agicore.agents.execution_agent import EVT_ORDER_PROCESSED, TASK_TYPE_ORDER
from agicore.core.events import Event, EventBus
from agicore.core.task_queue import TaskQueue
from agicore.l1_perception.market_models import EVT_MARKET_TICK
from agicore.l2_memory.schemas.task import TaskCreate
from agicore.strategy.signal_models import Action, OHLCV

logger = structlog.get_logger(__name__)

ORCHESTRATOR_ID = "signal_loop_orchestrator"
EVT_SIGNAL_GENERATED = "agent.signal_loop.signal"
EVT_SIGNAL_BLOCKED = "agent.signal_loop.blocked"
RISK_RESULT_CONTRACT_VERSION = "canonical-l5-risk-result/1.0"


class _StrategyProtocol(Protocol):
    name: str

    def on_bar(self, bar: OHLCV) -> Any: ...


# Import compatibility only. Supplying it to the orchestrator is fail-closed;
# risk snapshots are owned by the canonical ExecutionService boundary.
SnapshotProvider = Callable[[], object]


class SignalLoopOrchestrator:
    """Turn non-HOLD strategy signals into complete canonical L5 proposals."""

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
        risk_manager: object | None = None,
        snapshot_provider: object | None = None,
    ) -> None:
        if not isinstance(symbol, str) or not symbol:
            raise ValueError("symbol must be non-empty")
        if order_quantity <= 0:
            raise ValueError("order_quantity must be > 0")
        if risk_manager is not None or snapshot_provider is not None:
            raise ValueError("risk evaluation belongs to canonical ExecutionService")
        self._bus = event_bus
        self._queue = task_queue
        self._strategy = strategy
        self._symbol = symbol
        self._qty = float(order_quantity)
        self._emit = bool(emit_signals)
        self._prefix = str(order_id_prefix)
        self._lock = threading.RLock()
        self._unsubs: list[Callable[[], None]] = []
        self._is_attached = False
        self._tick_count = 0
        self._signal_count = 0
        self._submitted_count = 0
        self._blocked_count = 0
        self._last_signal_action: str | None = None
        self._last_block_codes: list[str] = []
        self._pending_intents: dict[str, dict[str, object]] = {}
        self._completed_intents: set[str] = set()

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
    def risk_result_contract_version(self) -> str:
        return RISK_RESULT_CONTRACT_VERSION

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

    def attach(self) -> None:
        if self._is_attached:
            return
        self._unsubs = [
            self._bus.subscribe(EVT_MARKET_TICK, self._on_tick),
            self._bus.subscribe(EVT_ORDER_PROCESSED, self._on_execution_result),
        ]
        self._is_attached = True

    def detach(self) -> None:
        if not self._is_attached:
            return
        for unsubscribe in self._unsubs:
            try:
                unsubscribe()
            except Exception as exc:  # pragma: no cover
                logger.warning("signal_loop.unsub_failed", error=str(exc))
        self._unsubs.clear()
        self._is_attached = False

    def __enter__(self) -> "SignalLoopOrchestrator":
        self.attach()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.detach()

    def _on_tick(self, event: Event) -> None:
        payload = event.payload
        if payload.get("symbol") != self._symbol:
            return
        bar = self._tick_to_ohlcv(payload)
        if bar is None:
            return
        try:
            signal = self._strategy.on_bar(bar)
        except Exception as exc:
            logger.error("signal_loop.strategy_failed", symbol=self._symbol, error=str(exc))
            return
        with self._lock:
            self._tick_count += 1
            action = getattr(signal, "action", None)
            if action is not None:
                self._last_signal_action = action.value if hasattr(action, "value") else str(action)
            if action != Action.HOLD:
                self._signal_count += 1
                sequence = self._signal_count
            else:
                sequence = self._signal_count
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
        self._submit_order(action, bar, sequence)

    def _submit_order(self, action: Action, bar: OHLCV, sequence: int) -> None:
        side = "BUY" if action == Action.BUY else "SELL"
        identity = {
            "prefix": self._prefix,
            "sequence": sequence,
            "symbol": self._symbol,
            "side": side,
            "quantity": self._qty,
            "estimated_price": bar.close,
            "timestamp": bar.timestamp.isoformat(),
        }
        digest = hashlib.sha256(
            json.dumps(identity, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
        ).hexdigest()
        intent_id = f"{self._prefix}-intent-{digest[:32]}"
        task_id = f"sigtask-{digest[:32]}"
        payload = {
            "intent_id": intent_id,
            "symbol": self._symbol,
            "side": side,
            "quantity": self._qty,
            "estimated_price": bar.close,
            "timestamp": bar.timestamp.isoformat(),
            "order_type": "MARKET",
            "operation_id": f"operation-{digest}",
            "order_id": f"order-{digest}",
            "fill_id": f"fill-{digest}",
            "report_id": f"report-{digest}",
            "submitted_at": bar.timestamp.isoformat(),
            "filled_at": bar.timestamp.isoformat(),
        }
        with self._lock:
            self._pending_intents[intent_id] = {
                "symbol": self._symbol,
                "action": side,
                "price": bar.close,
                "strategy": getattr(self._strategy, "name", "?"),
            }
        try:
            self._queue.enqueue(
                TaskCreate(
                    id=task_id,
                    task_type=TASK_TYPE_ORDER,
                    assigned_to=ORCHESTRATOR_ID,
                    payload=payload,
                )
            )
        except Exception as exc:
            with self._lock:
                self._pending_intents.pop(intent_id, None)
            logger.error("signal_loop.enqueue_failed", task_id=task_id, error=str(exc))
            return
        with self._lock:
            self._submitted_count += 1

    def _on_execution_result(self, event: Event) -> None:
        payload = event.payload
        intent_id = payload.get("intent_id")
        if not isinstance(intent_id, str):
            return
        with self._lock:
            proposal = self._pending_intents.pop(intent_id, None)
            if proposal is None or intent_id in self._completed_intents:
                return
            self._completed_intents.add(intent_id)
            is_blocked = (
                payload.get("committed") is False
                and str(payload.get("order_status", "")).upper() == "REJECTED"
            )
            if not is_blocked:
                return
            codes = [str(code) for code in payload.get("violation_codes") or ()]
            self._blocked_count += 1
            self._last_block_codes = codes
        if self._emit:
            self._bus.emit(
                EVT_SIGNAL_BLOCKED,
                intent_id=intent_id,
                symbol=proposal["symbol"],
                action=proposal["action"],
                price=proposal["price"],
                strategy=proposal["strategy"],
                violation_codes=codes,
                authorization_id=payload.get("authorization_id"),
                decision_hash=payload.get("decision_hash"),
            )
        logger.warning(
            "signal_loop.signal_blocked",
            intent_id=intent_id,
            symbol=proposal["symbol"],
            codes=codes,
        )

    @staticmethod
    def _tick_to_ohlcv(payload: dict[str, Any]) -> OHLCV | None:
        try:
            raw = payload["timestamp"]
            if isinstance(raw, datetime):
                timestamp = raw
            else:
                timestamp = datetime.fromisoformat(str(raw))
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            price = float(payload["price"])
            if price <= 0:
                return None
            return OHLCV(
                timestamp=timestamp,
                open=price,
                high=price,
                low=price,
                close=price,
                volume=float(payload.get("volume", 0.0)),
            )
        except (KeyError, TypeError, ValueError):
            return None


__all__ = [
    "SignalLoopOrchestrator",
    "SnapshotProvider",
    "ORCHESTRATOR_ID",
    "EVT_SIGNAL_GENERATED",
    "EVT_SIGNAL_BLOCKED",
    "RISK_RESULT_CONTRACT_VERSION",
]
