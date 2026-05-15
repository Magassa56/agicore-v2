"""AGIcore-v2 — concrete agent implementations.

Each agent is a callable conforming to the ``TaskHandler`` protocol from
``agicore.l4_planning.handlers``. Instances are registered on a
RuntimeEngine via ``register_handler(task_type, agent)``.

Phase 4  : EchoAgent (reference handler).
Phase 5  : HeartbeatAgent + HeartbeatScheduler (runtime stability).
Phase 7B : StrategyAgent (offline backtest handler).
Phase 7D : ExecutionAgent (mock-broker execution handler).
"""
from .echo_agent import (
    AGENT_ID as ECHO_AGENT_ID,
    EVT_ECHO_PROCESSED,
    TASK_TYPE_ECHO,
    EchoAgent,
)
from .execution_agent import (
    AGENT_ID as EXECUTION_AGENT_ID,
    EVT_ORDER_PROCESSED,
    TASK_TYPE_ORDER,
    ExecutionAgent,
)
from .heartbeat_agent import (
    AGENT_ID as HEARTBEAT_AGENT_ID,
    EVT_HEARTBEAT_TICK,
    RUNTIME_STATE_ACTIVE,
    RUNTIME_STATE_DEGRADED,
    RUNTIME_STATE_STOPPING,
    TASK_TYPE_HEARTBEAT,
    HeartbeatAgent,
    HeartbeatScheduler,
)
from .strategy_agent import (
    AGENT_ID as STRATEGY_AGENT_ID,
    DATASET_PATTERNS,
    DEFAULT_BASE_PRICE,
    DEFAULT_DATASET_PATTERN,
    DEFAULT_DATASET_SIZE,
    DEFAULT_FAST_PERIOD,
    DEFAULT_INITIAL_CAPITAL,
    DEFAULT_SLOW_PERIOD,
    EVT_STRATEGY_BACKTEST_COMPLETED,
    TASK_TYPE_BACKTEST,
    StrategyAgent,
)

__all__ = [
    # Echo (Phase 4)
    "EchoAgent",
    "TASK_TYPE_ECHO",
    "EVT_ECHO_PROCESSED",
    "ECHO_AGENT_ID",
    # Heartbeat (Phase 5)
    "HeartbeatAgent",
    "HeartbeatScheduler",
    "TASK_TYPE_HEARTBEAT",
    "EVT_HEARTBEAT_TICK",
    "HEARTBEAT_AGENT_ID",
    "RUNTIME_STATE_ACTIVE",
    "RUNTIME_STATE_DEGRADED",
    "RUNTIME_STATE_STOPPING",
    # Strategy (Phase 7B)
    "StrategyAgent",
    "TASK_TYPE_BACKTEST",
    "EVT_STRATEGY_BACKTEST_COMPLETED",
    "STRATEGY_AGENT_ID",
    "DATASET_PATTERNS",
    "DEFAULT_FAST_PERIOD",
    "DEFAULT_SLOW_PERIOD",
    "DEFAULT_INITIAL_CAPITAL",
    "DEFAULT_DATASET_SIZE",
    "DEFAULT_DATASET_PATTERN",
    "DEFAULT_BASE_PRICE",
    # Execution (Phase 7D)
    "ExecutionAgent",
    "TASK_TYPE_ORDER",
    "EVT_ORDER_PROCESSED",
    "EXECUTION_AGENT_ID",
]
