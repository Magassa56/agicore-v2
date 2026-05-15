"""AGIcore-v2 — Replay subsystem (Phase 7E + 7F).

State_t = f(Events_0..t). Events are the only source of truth ; state is
always recomputed from the immutable event log.

Public API :
- EventStore             : append-only immutable log
- ReplayEvent            : immutable event record (Pydantic frozen)
- ReplayEventType        : enum of supported event types
- StateBuilder           : pure stateless reconstructor
- ReplayState            : output state snapshot
- ReplayPosition         : per-symbol position
- ReplayClosedOrder      : closed order record
- ReplayEngine           : orchestrator EventStore + StateBuilder
- RuntimeEventBridge     : passive bridge Runtime EventBus → EventStore
- DEFAULT_TRANSLATORS    : default runtime → replay event translators
- RuntimeToReplayTranslator : translator type alias
- RUNTIME_EXECUTION_EVENT   : canonical runtime event constant
"""
from .event_store import EventStore, ReplayEvent, ReplayEventType
from .replay_engine import ReplayEngine
from .runtime_event_bridge import (
    DEFAULT_TRANSLATORS,
    RUNTIME_EXECUTION_EVENT,
    RuntimeEventBridge,
    RuntimeToReplayTranslator,
)
from .state_builder import (
    ReplayClosedOrder,
    ReplayPosition,
    ReplayState,
    StateBuilder,
)

__all__ = [
    "EventStore",
    "ReplayEvent",
    "ReplayEventType",
    "StateBuilder",
    "ReplayState",
    "ReplayPosition",
    "ReplayClosedOrder",
    "ReplayEngine",
    "RuntimeEventBridge",
    "RuntimeToReplayTranslator",
    "RUNTIME_EXECUTION_EVENT",
    "DEFAULT_TRANSLATORS",
]
