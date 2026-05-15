"""Integration test — StrategyAgent through the full Runtime Engine pipeline.

Validates that AGIcore can orchestrate a complete trading-analysis workflow
through the Runtime Engine, fully offline and deterministically.
"""
from __future__ import annotations

from agicore.agents.strategy_agent import (
    AGENT_ID,
    EVT_STRATEGY_BACKTEST_COMPLETED,
    TASK_TYPE_BACKTEST,
    StrategyAgent,
)
from agicore.core.events import (
    EVT_TASK_COMPLETED,
    EVT_TASK_CREATED,
    EVT_TASK_STARTED,
)
from agicore.core.retry import RetryPolicy
from agicore.l2_memory.repositories.task_repository import TaskRepository
from agicore.l2_memory.schemas.task import TaskCreate
from agicore.l4_planning.runtime import RuntimeEngine


def test_strategy_agent_full_runtime_pipeline() -> None:
    """receive → enqueue → dispatch → execute → log → persist → feedback."""
    rt = RuntimeEngine(
        retry_policy=RetryPolicy(max_attempts=1, initial_delay=0, jitter=False),
        poll_interval=0.0,
    )
    try:
        agent = StrategyAgent(rt.memory, rt.event_bus)
        rt.register_handler(TASK_TYPE_BACKTEST, agent)

        seen: list[str] = []
        rt.subscribe("*", lambda ev: seen.append(ev.event_type))

        # Submit
        submitted = rt.submit(
            TaskCreate(
                id="bt-1",
                task_type=TASK_TYPE_BACKTEST,
                payload={
                    "fast_period": 5,
                    "slow_period": 15,
                    "dataset_pattern": "oscillating",
                    "dataset_size": 100,
                    "initial_capital": 5_000.0,
                },
            )
        )
        assert submitted.status == "pending"

        # Drain
        executed = rt.run_once()
        assert executed == 1

        # 1. Task complétée + result structuré
        with rt.orchestrator._engine.session() as s:  # type: ignore[attr-defined]
            final = TaskRepository(s).get("bt-1")
        assert final is not None
        assert final.status == "completed"
        assert final.error is None
        assert final.result is not None
        for required in (
            "strategy_name", "total_trades", "win_rate", "total_pnl",
            "max_drawdown", "final_equity", "runtime_duration_ms",
        ):
            assert required in final.result, f"missing: {required}"
        assert final.result["agent_id"] == AGENT_ID
        assert final.result["task_id"] == "bt-1"
        assert "(5,15)" in final.result["strategy_name"]
        assert final.result["initial_equity"] == 5_000.0

        # 2. Lifecycle events propagés
        assert EVT_TASK_CREATED in seen
        assert EVT_TASK_STARTED in seen
        assert EVT_TASK_COMPLETED in seen
        assert EVT_STRATEGY_BACKTEST_COMPLETED in seen

        # 3. LTM contient l'event domaine
        events = rt.memory.get_recent_events(
            event_type=EVT_STRATEGY_BACKTEST_COMPLETED, limit=5
        )
        assert len(events) == 1
        assert events[0].task_id == "bt-1"
        assert events[0].agent_id == AGENT_ID

        # 4. Compteur agent
        assert agent.completed_count == 1
    finally:
        rt.shutdown()


def test_strategy_agent_failure_path_is_marked_failed() -> None:
    """Un payload invalide se traduit en task failed proprement."""
    rt = RuntimeEngine(
        retry_policy=RetryPolicy(max_attempts=1, initial_delay=0, jitter=False),
        poll_interval=0.0,
    )
    try:
        agent = StrategyAgent(rt.memory, rt.event_bus)
        rt.register_handler(TASK_TYPE_BACKTEST, agent)

        rt.submit(
            TaskCreate(
                id="bt-bad",
                task_type=TASK_TYPE_BACKTEST,
                payload={"dataset_pattern": "absurd"},
            )
        )
        rt.run_once()

        with rt.orchestrator._engine.session() as s:  # type: ignore[attr-defined]
            final = TaskRepository(s).get("bt-bad")
        assert final is not None
        assert final.status == "failed"
        assert final.error is not None
        assert "absurd" in final.error.lower() or "pattern" in final.error.lower()
    finally:
        rt.shutdown()
