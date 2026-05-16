"""Tests for structlog configuration."""
from __future__ import annotations

import ast
import io
import json
import pathlib

import pytest
import structlog

from agicore.core.logging import (
    bind_context,
    clear_context,
    configure_logging,
    get_logger,
)


@pytest.fixture(autouse=True)
def _reset_structlog() -> None:
    clear_context()
    yield
    clear_context()


def _capture_log_buf() -> io.StringIO:
    buf = io.StringIO()
    configure_logging(level="DEBUG", json=True, stream=buf)
    return buf


def test_configure_logging_emits_json() -> None:
    buf = _capture_log_buf()
    log = get_logger("test")
    log.info("hello", k=1)
    line = buf.getvalue().strip().splitlines()[-1]
    parsed = json.loads(line)
    assert parsed["event"] == "hello"
    assert parsed["k"] == 1
    assert parsed["level"] == "info"
    assert "timestamp" in parsed


def test_configure_logging_respects_level() -> None:
    buf = io.StringIO()
    configure_logging(level="WARNING", json=True, stream=buf)
    log = get_logger("test")
    log.info("low")
    log.warning("high")
    out = buf.getvalue()
    assert "high" in out
    assert "low" not in out


def test_bind_context_propagates_to_logs() -> None:
    buf = _capture_log_buf()
    log = get_logger("test")
    bind_context(task_id="t-42", agent_id="trader")
    log.info("scoped")
    line = buf.getvalue().strip().splitlines()[-1]
    parsed = json.loads(line)
    assert parsed["task_id"] == "t-42"
    assert parsed["agent_id"] == "trader"


def test_clear_context_removes_bound_vars() -> None:
    buf = _capture_log_buf()
    log = get_logger("test")
    bind_context(scope="x")
    clear_context()
    log.info("after_clear")
    line = buf.getvalue().strip().splitlines()[-1]
    parsed = json.loads(line)
    assert "scope" not in parsed


def test_no_print_in_source() -> None:
    """AST-strict scan: no real print() calls in logging-controlled scope."""
    project_root = pathlib.Path(__file__).resolve().parents[3]
    paths = [
        project_root / "src" / "agicore",
        project_root / "services" / "operator" / "app" / "main.py",
        project_root / "tools" / "utils.py",
    ]
    offending: list[str] = []
    files = []
    for path in paths:
        if path.is_dir():
            files.extend(path.rglob("*.py"))
        else:
            files.append(path)
    for py in files:
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "print"
            ):
                offending.append(f"{py}:{node.lineno}")
    assert not offending, f"print() found:\n  " + "\n  ".join(offending)
