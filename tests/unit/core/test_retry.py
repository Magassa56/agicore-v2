"""Tests for RetryPolicy and @retry decorator."""
from __future__ import annotations

import pytest

from agicore.core.retry import RetryError, RetryPolicy, retry


def test_retry_policy_succeeds_first_try() -> None:
    p = RetryPolicy(max_attempts=3, initial_delay=0.0, jitter=False)
    calls = {"n": 0}

    def f() -> str:
        calls["n"] += 1
        return "ok"

    assert p.execute(f) == "ok"
    assert calls["n"] == 1


def test_retry_policy_retries_until_success() -> None:
    p = RetryPolicy(max_attempts=4, initial_delay=0.0, jitter=False)
    calls = {"n": 0}

    def flaky() -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            raise ValueError("transient")
        return "ok"

    assert p.execute(flaky) == "ok"
    assert calls["n"] == 3


def test_retry_policy_exhausts_and_raises() -> None:
    p = RetryPolicy(max_attempts=2, initial_delay=0.0, jitter=False)
    calls = {"n": 0}

    def always_fail() -> None:
        calls["n"] += 1
        raise RuntimeError("nope")

    with pytest.raises(RetryError) as exc_info:
        p.execute(always_fail)

    assert calls["n"] == 2
    assert exc_info.value.attempts == 2
    assert isinstance(exc_info.value.__cause__, RuntimeError)


def test_retry_policy_only_retries_listed_exceptions() -> None:
    p = RetryPolicy(
        max_attempts=5,
        initial_delay=0.0,
        jitter=False,
        retryable_exceptions=(ValueError,),
    )
    calls = {"n": 0}

    def raises_unrelated() -> None:
        calls["n"] += 1
        raise TypeError("fatal")

    with pytest.raises(TypeError):
        p.execute(raises_unrelated)
    assert calls["n"] == 1  # pas de retry sur TypeError


def test_retry_compute_delay_caps_at_max() -> None:
    p = RetryPolicy(
        max_attempts=10,
        initial_delay=10.0,
        backoff_factor=10.0,
        max_delay=5.0,
        jitter=False,
    )
    # attempt 3 → 10 * 10^2 = 1000, capé à 5
    assert p.compute_delay(3) == 5.0


def test_retry_decorator_works() -> None:
    calls = {"n": 0}

    @retry(max_attempts=3, initial_delay=0.0, jitter=False)
    def flaky(x: int) -> int:
        calls["n"] += 1
        if calls["n"] < 2:
            raise ValueError("retry me")
        return x * 2

    assert flaky(21) == 42
    assert calls["n"] == 2


def test_retry_policy_invalid_args() -> None:
    with pytest.raises(ValueError):
        RetryPolicy(max_attempts=0)
    with pytest.raises(ValueError):
        RetryPolicy(initial_delay=-1)
