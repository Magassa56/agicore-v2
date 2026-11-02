"""Versioned, invented 39-bar confirmation fixtures for local missions.

No external bytes, paths, market data or current time are accepted.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

PROFILES = (
    "confirmation-long-v1",
    "confirmation-short-v1",
    "confirmation-long-rejected-v1",
    "confirmation-short-rejected-v1",
)
OBSERVATIONS = 39
SCHEMA = "agicore:invented-confirmation-fixture-bundle:v1"


def generate_confirmation_fixture(profile: str, observations: int) -> bytes:
    """Generate a fixed long or short confirmation with no external input."""
    if profile not in PROFILES or type(observations) is not int or observations != OBSERVATIONS:
        raise ValueError("unsupported invented confirmation fixture")
    baseline = ("20000", "20000.25", "19999.75", "20000")
    low_bar_34 = "19940" if "rejected" in profile else "20001.75"
    rows = [baseline] * 29 + [
        ("20000", "20000.25", "19999.25", "20000.25"),
        ("20000.25", "20000.50", "19999.50", "20000.50"),
        ("20000.50", "20000.75", "19999.75", "20000.75"),
        ("20000.25", "20002", "20000", "20001.75"),
        ("20004", "20004.25", "20000.25", "20002"),
        ("20002", "20003.25", low_bar_34, "20003"),
        ("20002.50", "20004.50", "20000.25", "20004.25"),
        ("20004.50", "20006.25", "20004", "20006"),
        ("20006", "20008.25", "20005.75", "20008"),
        ("20008.25", "20009", "20007.75", "20008.50"),
    ]
    origin = datetime(2099, 1, 4, 8, tzinfo=UTC)
    result = []
    is_short = "short" in profile
    for index, values in enumerate(rows):
        open_, high, low, close = (Decimal(value) for value in values)
        if is_short:
            open_, high, low, close = (
                Decimal(40000) - open_,
                Decimal(40000) - low,
                Decimal(40000) - high,
                Decimal(40000) - close,
            )
        volume = 150 if index in (32, 34) else 100
        timestamp = origin + timedelta(minutes=index)
        result.append(f"{timestamp:%Y%m%d %H%M%S};{open_};{high};{low};{close};{volume}\n")
    return "".join(result).encode("ascii")
