"""Tests insert/retrieve pour EventRepository, TaskRepository, StateRepository."""
from __future__ import annotations

from agicore.l2_memory.adapters.sqlalchemy_engine import SqlAlchemyEngine
from agicore.l2_memory.models.task import TASK_STATUS_RUNNING
from agicore.l2_memory.repositories.event_repository import EventRepository
from agicore.l2_memory.repositories.state_repository import StateRepository
from agicore.l2_memory.repositories.task_repository import TaskRepository
from agicore.l2_memory.schemas.event import EventCreate
from agicore.l2_memory.schemas.task import TaskCreate, TaskUpdate


def test_event_repository_insert_and_retrieve(ltm_engine: SqlAlchemyEngine) -> None:
    with ltm_engine.session() as s:
        repo = EventRepository(s)
        created = repo.create(
            EventCreate(
                event_type="signal_received",
                task_id="task-1",
                agent_id="trading_agent",
                payload={"price": 4500.25},
            )
        )
        assert created.id is not None
        assert created.event_type == "signal_received"

    with ltm_engine.session() as s:
        repo = EventRepository(s)
        found = repo.get(created.id)
        assert found is not None
        assert found.payload == {"price": 4500.25}


def test_event_repository_list_recent_filters(ltm_engine: SqlAlchemyEngine) -> None:
    with ltm_engine.session() as s:
        repo = EventRepository(s)
        repo.create(EventCreate(event_type="a", task_id="t-1"))
        repo.create(EventCreate(event_type="b", task_id="t-1"))
        repo.create(EventCreate(event_type="a", task_id="t-2"))

    with ltm_engine.session() as s:
        repo = EventRepository(s)
        all_a = repo.list_recent(event_type="a")
        assert len(all_a) == 2
        only_t1 = repo.list_recent(task_id="t-1")
        assert len(only_t1) == 2


def test_task_repository_full_lifecycle(ltm_engine: SqlAlchemyEngine) -> None:
    with ltm_engine.session() as s:
        repo = TaskRepository(s)
        repo.create(TaskCreate(id="task-42", task_type="trade.evaluate"))

    with ltm_engine.session() as s:
        repo = TaskRepository(s)
        t = repo.get("task-42")
        assert t is not None
        assert t.status == "pending"

        updated = repo.update(
            "task-42",
            TaskUpdate(status=TASK_STATUS_RUNNING, assigned_to="trading_agent"),
        )
        assert updated is not None
        assert updated.status == TASK_STATUS_RUNNING
        assert updated.assigned_to == "trading_agent"

    with ltm_engine.session() as s:
        repo = TaskRepository(s)
        running = repo.list_by_status(TASK_STATUS_RUNNING)
        assert len(running) == 1


def test_state_repository_agent_state_upsert(ltm_engine: SqlAlchemyEngine) -> None:
    with ltm_engine.session() as s:
        repo = StateRepository(s)
        from agicore.l2_memory.schemas.agent_state import AgentStateUpsert

        first = repo.upsert_agent_state(
            AgentStateUpsert(agent_id="orch-1", state="idle", context={"v": 1})
        )
        assert first.state == "idle"

        second = repo.upsert_agent_state(
            AgentStateUpsert(agent_id="orch-1", state="active", context={"v": 2})
        )
        assert second.state == "active"
        assert second.context == {"v": 2}

    with ltm_engine.session() as s:
        repo = StateRepository(s)
        loaded = repo.get_agent_state("orch-1")
        assert loaded is not None
        assert loaded.state == "active"
