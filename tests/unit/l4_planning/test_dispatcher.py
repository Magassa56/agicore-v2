"""Tests for HandlerRegistry + Dispatcher."""
from __future__ import annotations

import pytest

from agicore.l2_memory.schemas.task import TaskRead
from agicore.l4_planning.dispatcher import Dispatcher
from agicore.l4_planning.handlers import (
    HandlerAlreadyRegisteredError,
    HandlerNotFoundError,
    HandlerRegistry,
)


def _make_task(task_type: str = "tx.echo", task_id: str = "t-1") -> TaskRead:
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    return TaskRead(
        id=task_id,
        task_type=task_type,
        status="pending",
        assigned_to=None,
        payload={"x": 1},
        result=None,
        error=None,
        created_at=now,
        updated_at=now,
    )


def test_registry_register_and_get() -> None:
    reg = HandlerRegistry()
    reg.register("tx.echo", lambda t: {"echoed": t.payload})
    assert reg.has("tx.echo")
    handler = reg.get("tx.echo")
    out = handler(_make_task())
    assert out == {"echoed": {"x": 1}}


def test_registry_double_register_raises() -> None:
    reg = HandlerRegistry()
    reg.register("tx.echo", lambda t: {})
    with pytest.raises(HandlerAlreadyRegisteredError):
        reg.register("tx.echo", lambda t: {})


def test_registry_replace_allowed_with_flag() -> None:
    reg = HandlerRegistry()
    reg.register("tx.echo", lambda t: {"v": 1})
    reg.register("tx.echo", lambda t: {"v": 2}, replace=True)
    assert reg.get("tx.echo")(_make_task()) == {"v": 2}


def test_registry_unregister() -> None:
    reg = HandlerRegistry()
    reg.register("tx.echo", lambda t: {})
    reg.unregister("tx.echo")
    assert not reg.has("tx.echo")


def test_dispatcher_routes_to_handler() -> None:
    reg = HandlerRegistry()
    reg.register("tx.add", lambda t: {"sum": t.payload["a"] + t.payload["b"]})
    disp = Dispatcher(reg)
    result = disp.dispatch(
        TaskRead(
            id="t",
            task_type="tx.add",
            status="running",
            assigned_to=None,
            payload={"a": 2, "b": 3},
            result=None,
            error=None,
            created_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
            updated_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
        )
    )
    assert result == {"sum": 5}


def test_dispatcher_unknown_type_raises() -> None:
    disp = Dispatcher(HandlerRegistry())
    with pytest.raises(HandlerNotFoundError):
        disp.dispatch(_make_task("tx.unknown"))


def test_dispatcher_handler_must_return_dict() -> None:
    reg = HandlerRegistry()
    reg.register("bad", lambda t: "not a dict")  # type: ignore[arg-type,return-value]
    disp = Dispatcher(reg)
    with pytest.raises(TypeError):
        disp.dispatch(_make_task("bad"))
