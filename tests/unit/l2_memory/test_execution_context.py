"""Tests ExecutionContext — création, lecture, mise à jour de status."""
from __future__ import annotations

from agicore.l2_memory.adapters.sqlalchemy_engine import SqlAlchemyEngine
from agicore.l2_memory.models.execution_context import (
    EXEC_STATUS_COMPLETED,
    EXEC_STATUS_RUNNING,
    MEMORY_SCOPE_TASK,
)
from agicore.l2_memory.repositories.state_repository import StateRepository
from agicore.l2_memory.schemas.execution_context import ExecutionContextCreate


def test_execution_context_create_and_load(ltm_engine: SqlAlchemyEngine) -> None:
    with ltm_engine.session() as s:
        repo = StateRepository(s)
        created = repo.create_execution_context(
            ExecutionContextCreate(
                task_id="task-x",
                session_id="sess-99",
                planner_state="dispatched",
                memory_scope=MEMORY_SCOPE_TASK,
            )
        )
        assert created.task_id == "task-x"
        assert created.session_id == "sess-99"
        assert created.status == "pending"
        assert created.timestamp is not None

    with ltm_engine.session() as s:
        repo = StateRepository(s)
        loaded = repo.get_execution_context("task-x")
        assert loaded is not None
        assert loaded.planner_state == "dispatched"


def test_execution_context_status_transitions(ltm_engine: SqlAlchemyEngine) -> None:
    with ltm_engine.session() as s:
        repo = StateRepository(s)
        repo.create_execution_context(
            ExecutionContextCreate(
                task_id="task-y",
                session_id="sess-1",
                planner_state="dispatched",
            )
        )

    for new_status in (EXEC_STATUS_RUNNING, EXEC_STATUS_COMPLETED):
        with ltm_engine.session() as s:
            repo = StateRepository(s)
            updated = repo.update_execution_status("task-y", new_status)
            assert updated is not None
            assert updated.status == new_status


def test_execution_context_update_unknown_returns_none(
    ltm_engine: SqlAlchemyEngine,
) -> None:
    with ltm_engine.session() as s:
        repo = StateRepository(s)
        result = repo.update_execution_status("does-not-exist", "running")
        assert result is None
