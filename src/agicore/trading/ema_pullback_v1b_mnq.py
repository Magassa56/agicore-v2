"""Single precommitted US-RTH entry-window child variant of EMA pullback V1A.

V1B changes exactly one rule: otherwise-qualified V1A entry signals are eligible only
from 08:30 inclusive to 15:00 exclusive, Monday through Friday, in America/Chicago.
The conversion uses IANA rules for the date of the closed decision bar.  Exit handling
is intentionally absent from this filter and remains delegated unchanged to V1A/V1.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from .ema_pullback_v1_mnq import PullbackContractError
from .ema_pullback_v1_mnq_development import DevelopmentVerdict
from .ema_pullback_v1_mnq_development_replay import (
    DevelopmentReplayResult,
    _run_bars,
    load_preserved_development_raw,
)
from .ema_pullback_v1a_mnq import (
    VARIANT_ID as PARENT_VARIANT_ID,
)
from .ema_pullback_v1a_mnq import (
    evaluate_v1a_ema20_slope,
)

VARIANT_ID = "EMA_PULLBACK_V1B_MNQ_V1A_US_RTH_ENTRY_ONLY"
VARIANT_HYPOTHESIS = (
    "Restrict new entries to the main US cash/RTH window to reduce low-liquidity/choppy "
    "entries, clustered losses and drawdown while preserving the existing exit logic."
)
EXPECTED_PARENT_VARIANT_ID = "EMA_PULLBACK_V1A_MNQ_EMA20_MIN_SLOPE_1_TICK"
PARENT_RESULT_SHA256 = "29eef4a574fc46aab07a5ab60fc0c09fe111c3e72acc6d91ae3e5f04450582de"
VARIANT_PROTOCOL_SHA256 = "c034db1ab2592f0ba4455c0aa0bd5c1c7bc2193f944d9f297819e38c35452f0e"

ENTRY_SESSION_FILTER_ENABLED = True
ENTRY_SESSION_TIMEZONE = "America/Chicago"
ENTRY_SESSION_START = time(8, 30, 0)
ENTRY_SESSION_END = time(15, 0, 0)
ENTRY_SESSION_WEEKDAYS = (0, 1, 2, 3, 4)
DST_POLICY = "IANA_TIMEZONE_RULES"
RUNNER_ID = "EMA_PULLBACK_V1B_MNQ_DEVELOPMENT_REPLAY_V1"
RUNNER_VERSION = "1.0"

_ENTRY_TIMEZONE = ZoneInfo(ENTRY_SESSION_TIMEZONE)

if PARENT_VARIANT_ID != EXPECTED_PARENT_VARIANT_ID:
    raise RuntimeError("V1B parent variant identity changed")


@dataclass(frozen=True)
class V1BEntrySessionEvaluation:
    """Fail-closed session eligibility for one already-closed UTC decision bar."""

    source_timestamp_utc: datetime
    local_timestamp: datetime
    weekday_allowed: bool
    time_allowed: bool
    entry_allowed: bool
    structural_stop_active: bool = True
    ema20_exit_active: bool = True
    entry_session_filter_enabled: bool = ENTRY_SESSION_FILTER_ENABLED
    timezone_name: str = ENTRY_SESSION_TIMEZONE
    session_start: time = ENTRY_SESSION_START
    session_end: time = ENTRY_SESSION_END
    session_weekdays: tuple[int, ...] = ENTRY_SESSION_WEEKDAYS
    dst_policy: str = DST_POLICY

    def __post_init__(self) -> None:
        if (
            not isinstance(self.source_timestamp_utc, datetime)
            or self.source_timestamp_utc.tzinfo is None
            or self.source_timestamp_utc.utcoffset() != timedelta(0)
        ):
            raise PullbackContractError("V1B source timestamp must be aware UTC")
        expected_local = self.source_timestamp_utc.astimezone(_ENTRY_TIMEZONE)
        if self.local_timestamp != expected_local:
            raise PullbackContractError("V1B local timestamp must use America/Chicago IANA rules")
        if (
            self.entry_session_filter_enabled is not True
            or self.timezone_name != ENTRY_SESSION_TIMEZONE
            or self.session_start != ENTRY_SESSION_START
            or self.session_end != ENTRY_SESSION_END
            or self.session_weekdays != ENTRY_SESSION_WEEKDAYS
            or self.dst_policy != DST_POLICY
        ):
            raise PullbackContractError("V1B entry session contract must remain exact")
        expected_weekday = expected_local.weekday() in ENTRY_SESSION_WEEKDAYS
        local_clock = expected_local.timetz().replace(tzinfo=None)
        expected_time = ENTRY_SESSION_START <= local_clock < ENTRY_SESSION_END
        if self.weekday_allowed is not expected_weekday or self.time_allowed is not expected_time:
            raise PullbackContractError("V1B session eligibility components are inconsistent")
        if self.entry_allowed is not (expected_weekday and expected_time):
            raise PullbackContractError("V1B entry eligibility is inconsistent")
        if self.structural_stop_active is not True or self.ema20_exit_active is not True:
            raise PullbackContractError("V1B entry filter cannot disable position exits")


def evaluate_v1b_entry_session(timestamp_utc: datetime) -> V1BEntrySessionEvaluation:
    """Evaluate the closed bar timestamp using date-specific America/Chicago DST rules."""
    if (
        not isinstance(timestamp_utc, datetime)
        or timestamp_utc.tzinfo is None
        or timestamp_utc.utcoffset() != timedelta(0)
    ):
        raise PullbackContractError("V1B source timestamp must be aware UTC")
    local_timestamp = timestamp_utc.astimezone(_ENTRY_TIMEZONE)
    local_clock = local_timestamp.timetz().replace(tzinfo=None)
    weekday_allowed = local_timestamp.weekday() in ENTRY_SESSION_WEEKDAYS
    time_allowed = ENTRY_SESSION_START <= local_clock < ENTRY_SESSION_END
    return V1BEntrySessionEvaluation(
        source_timestamp_utc=timestamp_utc,
        local_timestamp=local_timestamp,
        weekday_allowed=weekday_allowed,
        time_allowed=time_allowed,
        entry_allowed=weekday_allowed and time_allowed,
    )


def v1b_entry_session_allows(timestamp_utc: datetime) -> bool:
    """Return only the deterministic new-entry eligibility consumed by the replay."""
    return evaluate_v1b_entry_session(timestamp_utc).entry_allowed


def run_preserved_v1b_development_replay(path: str | Path) -> DevelopmentReplayResult:
    """Verify and run the sole authorized V1B EXPOSED_DEVELOPMENT replay."""
    dataset = load_preserved_development_raw(path)
    return _run_bars(
        dataset.bars,
        source_raw_sha256=dataset.source_raw_sha256,
        source_size_bytes=dataset.source_size_bytes,
        slope_evaluator=evaluate_v1a_ema20_slope,
        runner_id=RUNNER_ID,
        runner_version=RUNNER_VERSION,
        variant_id=VARIANT_ID,
        variant_protocol_sha256=VARIANT_PROTOCOL_SHA256,
        no_go_verdict=DevelopmentVerdict.NO_GO_VARIANT,
        entry_eligibility_evaluator=v1b_entry_session_allows,
    )


__all__ = [
    "DST_POLICY",
    "ENTRY_SESSION_END",
    "ENTRY_SESSION_FILTER_ENABLED",
    "ENTRY_SESSION_START",
    "ENTRY_SESSION_TIMEZONE",
    "ENTRY_SESSION_WEEKDAYS",
    "PARENT_RESULT_SHA256",
    "RUNNER_ID",
    "RUNNER_VERSION",
    "VARIANT_HYPOTHESIS",
    "VARIANT_ID",
    "VARIANT_PROTOCOL_SHA256",
    "V1BEntrySessionEvaluation",
    "evaluate_v1b_entry_session",
    "run_preserved_v1b_development_replay",
    "v1b_entry_session_allows",
]
