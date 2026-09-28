from __future__ import annotations

import hashlib
import json
from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal
from inspect import signature
from pathlib import Path

import pytest

import agicore.trading.ema_pullback_v1_mnq_development_replay as replay
import agicore.trading.ema_pullback_v1b_mnq as variant
from agicore.trading.ema_pullback_v1_mnq import PullbackContractError
from agicore.trading.ema_pullback_v1_mnq_development import (
    PROTOCOL_SHA256,
    SOURCE_RAW_SHA256,
    DevelopmentVerdict,
)
from agicore.trading.ema_pullback_v1_mnq_development_replay import (
    DevelopmentReplayBar,
    DevelopmentReplayError,
)
from agicore.trading.ema_pullback_v1a_mnq import (
    VARIANT_ID as PARENT_VARIANT_ID,
)
from agicore.trading.ema_pullback_v1a_mnq import (
    evaluate_v1a_ema20_slope,
)
from agicore.trading.ema_pullback_v1b_mnq import (
    DST_POLICY,
    ENTRY_SESSION_END,
    ENTRY_SESSION_FILTER_ENABLED,
    ENTRY_SESSION_START,
    ENTRY_SESSION_TIMEZONE,
    ENTRY_SESSION_WEEKDAYS,
    PARENT_RESULT_SHA256,
    RUNNER_ID,
    VARIANT_ID,
    VARIANT_PROTOCOL_SHA256,
    evaluate_v1b_entry_session,
    v1b_entry_session_allows,
)

ROOT = Path(__file__).resolve().parents[3]
VARIANT_PROTOCOL = ROOT / "docs/evidence/EMA_PULLBACK_V1B_MNQ_VARIANT_PROTOCOL.json"
V1_MODULE = ROOT / "src/agicore/trading/ema_pullback_v1_mnq.py"
V1A_MODULE = ROOT / "src/agicore/trading/ema_pullback_v1a_mnq.py"
V1_RESULT = ROOT / "docs/evidence/EMA_PULLBACK_V1_MNQ_DEVELOPMENT_REPLAY_RESULT.json"
V1A_RESULT = ROOT / "docs/evidence/EMA_PULLBACK_V1A_MNQ_DEVELOPMENT_REPLAY_RESULT.json"
V1B_RESULT = ROOT / "docs/evidence/EMA_PULLBACK_V1B_MNQ_DEVELOPMENT_REPLAY_RESULT.json"


@pytest.mark.parametrize(
    ("timestamp_utc", "expected_local", "allowed"),
    [
        ("2026-01-05T14:29:59+00:00", "2026-01-05T08:29:59-06:00", False),
        ("2026-01-05T14:30:00+00:00", "2026-01-05T08:30:00-06:00", True),
        ("2026-01-05T20:59:59+00:00", "2026-01-05T14:59:59-06:00", True),
        ("2026-01-05T21:00:00+00:00", "2026-01-05T15:00:00-06:00", False),
        ("2026-06-01T13:29:59+00:00", "2026-06-01T08:29:59-05:00", False),
        ("2026-06-01T13:30:00+00:00", "2026-06-01T08:30:00-05:00", True),
        ("2026-06-01T19:59:59+00:00", "2026-06-01T14:59:59-05:00", True),
        ("2026-06-01T20:00:00+00:00", "2026-06-01T15:00:00-05:00", False),
    ],
)
def test_v1b_boundaries_are_half_open_under_winter_and_summer_dst(
    timestamp_utc: str,
    expected_local: str,
    allowed: bool,
) -> None:
    result = evaluate_v1b_entry_session(datetime.fromisoformat(timestamp_utc))

    assert result.local_timestamp.isoformat() == expected_local
    assert result.entry_allowed is allowed
    assert v1b_entry_session_allows(datetime.fromisoformat(timestamp_utc)) is allowed


def test_v1b_one_minute_contract_last_eligible_close_and_excluded_end() -> None:
    last_minute_close = evaluate_v1b_entry_session(
        datetime.fromisoformat("2026-06-01T19:59:00+00:00")
    )
    excluded_end = evaluate_v1b_entry_session(datetime.fromisoformat("2026-06-01T20:00:00+00:00"))

    assert last_minute_close.local_timestamp.strftime("%H:%M:%S") == "14:59:00"
    assert last_minute_close.entry_allowed is True
    assert excluded_end.local_timestamp.strftime("%H:%M:%S") == "15:00:00"
    assert excluded_end.entry_allowed is False


def test_v1b_uses_date_specific_iana_dst_not_a_fixed_utc_offset() -> None:
    winter = evaluate_v1b_entry_session(datetime(2026, 1, 5, 13, 30, tzinfo=UTC))
    summer = evaluate_v1b_entry_session(datetime(2026, 6, 1, 13, 30, tzinfo=UTC))

    assert winter.local_timestamp.strftime("%H:%M") == "07:30"
    assert winter.local_timestamp.utcoffset() == timedelta(hours=-6)
    assert winter.entry_allowed is False
    assert summer.local_timestamp.strftime("%H:%M") == "08:30"
    assert summer.local_timestamp.utcoffset() == timedelta(hours=-5)
    assert summer.entry_allowed is True


@pytest.mark.parametrize(
    "timestamp_utc",
    [
        datetime(2026, 6, 6, 13, 30, tzinfo=UTC),
        datetime(2026, 6, 7, 13, 30, tzinfo=UTC),
    ],
)
def test_v1b_rejects_weekends_inside_the_clock_window(timestamp_utc: datetime) -> None:
    result = evaluate_v1b_entry_session(timestamp_utc)

    assert result.time_allowed is True
    assert result.weekday_allowed is False
    assert result.entry_allowed is False


@pytest.mark.parametrize(
    "invalid_timestamp",
    [
        datetime(2026, 6, 1, 13, 30, tzinfo=UTC).replace(tzinfo=None),
        datetime(2026, 6, 1, 14, 30, tzinfo=timezone(timedelta(hours=1))),
    ],
)
def test_v1b_rejects_non_utc_or_naive_source_timestamps(
    invalid_timestamp: datetime,
) -> None:
    with pytest.raises(PullbackContractError, match="aware UTC"):
        evaluate_v1b_entry_session(invalid_timestamp)


def test_v1b_filter_is_entry_only_and_never_disables_existing_exits() -> None:
    outside = evaluate_v1b_entry_session(datetime(2026, 6, 1, 20, 0, tzinfo=UTC))

    assert outside.entry_allowed is False
    assert outside.structural_stop_active is True
    assert outside.ema20_exit_active is True
    with pytest.raises(PullbackContractError, match="cannot disable position exits"):
        replace(outside, structural_stop_active=False)
    with pytest.raises(FrozenInstanceError):
        outside.entry_allowed = True  # type: ignore[misc]


def test_v1b_session_evaluator_is_causal_deterministic_and_has_no_machine_clock() -> None:
    timestamp = datetime(2026, 6, 1, 13, 30, tzinfo=UTC)
    first = evaluate_v1b_entry_session(timestamp)
    second = evaluate_v1b_entry_session(timestamp)

    assert first == second
    assert set(signature(evaluate_v1b_entry_session).parameters) == {"timestamp_utc"}
    assert first.source_timestamp_utc == timestamp


def _flat_bars_ending_at(end_timestamp: datetime) -> tuple[DevelopmentReplayBar, ...]:
    return tuple(
        DevelopmentReplayBar(
            sequence=sequence,
            timestamp_utc=end_timestamp - timedelta(minutes=3 - sequence),
            open=Decimal("100.00"),
            high=Decimal("100.50"),
            low=Decimal("99.50"),
            close=Decimal("100.00"),
            volume=100,
        )
        for sequence in range(4)
    )


def test_runner_counts_session_admission_and_rejection_separately(monkeypatch) -> None:
    def fake_candidate(*, sequence: int, **_: object) -> object | None:
        return object() if sequence == 3 else None

    monkeypatch.setattr(replay, "_candidate_entry_signal", fake_candidate)
    common = {
        "source_raw_sha256": SOURCE_RAW_SHA256,
        "source_size_bytes": 0,
        "variant_id": VARIANT_ID,
        "variant_protocol_sha256": VARIANT_PROTOCOL_SHA256,
        "no_go_verdict": DevelopmentVerdict.NO_GO_VARIANT,
        "entry_eligibility_evaluator": v1b_entry_session_allows,
    }

    admitted = replay._run_bars(
        _flat_bars_ending_at(datetime(2026, 6, 1, 13, 30, tzinfo=UTC)),
        **common,  # type: ignore[arg-type]
    )
    rejected = replay._run_bars(
        _flat_bars_ending_at(datetime(2026, 6, 1, 20, 0, tzinfo=UTC)),
        **common,  # type: ignore[arg-type]
    )

    assert admitted.counters.qualified_entry_signals == 1
    assert admitted.counters.rejected_by_session_filter == 0
    assert admitted.counters.expired_entries == 1
    assert rejected.counters.qualified_entry_signals == 0
    assert rejected.counters.rejected_by_session_filter == 1
    assert rejected.counters.expired_entries == 0


def test_runner_default_keeps_v1_and_v1a_session_behavior_unchanged(monkeypatch) -> None:
    def fake_candidate(*, sequence: int, **_: object) -> object | None:
        return object() if sequence == 3 else None

    monkeypatch.setattr(replay, "_candidate_entry_signal", fake_candidate)
    result = replay._run_bars(
        _flat_bars_ending_at(datetime(2026, 6, 1, 20, 0, tzinfo=UTC)),
        source_raw_sha256=SOURCE_RAW_SHA256,
        source_size_bytes=0,
    )

    assert result.counters.qualified_entry_signals == 1
    assert result.counters.rejected_by_session_filter == 0
    assert result.counters.expired_entries == 1


def test_runner_fails_closed_on_hidden_or_non_boolean_entry_filter(monkeypatch) -> None:
    bars = _flat_bars_ending_at(datetime(2026, 6, 1, 20, 0, tzinfo=UTC))
    with pytest.raises(DevelopmentReplayError, match="explicit variant contract"):
        replay._run_bars(
            bars,
            source_raw_sha256=SOURCE_RAW_SHA256,
            source_size_bytes=0,
            entry_eligibility_evaluator=lambda _: True,
        )

    monkeypatch.setattr(replay, "_candidate_entry_signal", lambda **_: object())
    with pytest.raises(DevelopmentReplayError, match="must return bool"):
        replay._run_bars(
            bars,
            source_raw_sha256=SOURCE_RAW_SHA256,
            source_size_bytes=0,
            variant_id=VARIANT_ID,
            variant_protocol_sha256=VARIANT_PROTOCOL_SHA256,
            entry_eligibility_evaluator=lambda _: 1,  # type: ignore[return-value]
        )


def _history_bar(
    sequence: int,
    first_timestamp: datetime,
    *,
    close: str = "100.00",
    open_price: str | None = None,
    high: str | None = None,
    low: str | None = None,
) -> DevelopmentReplayBar:
    closing = Decimal(close)
    opening = Decimal(open_price or close)
    return DevelopmentReplayBar(
        sequence=sequence,
        timestamp_utc=first_timestamp + timedelta(minutes=sequence),
        open=opening,
        high=Decimal(high) if high is not None else max(opening, closing) + Decimal("0.50"),
        low=Decimal(low) if low is not None else min(opening, closing) - Decimal("0.50"),
        close=closing,
        volume=100,
    )


def _entry_history_ending_at_1458_chicago() -> list[DevelopmentReplayBar]:
    confirmation_timestamp = datetime(2026, 6, 1, 19, 58, tzinfo=UTC)
    first_timestamp = confirmation_timestamp - timedelta(minutes=34)
    bars = [_history_bar(sequence, first_timestamp) for sequence in range(34)]
    bars.append(
        _history_bar(
            34,
            first_timestamp,
            close="101.00",
            open_price="100.00",
            high="101.00",
            low="99.75",
        )
    )
    return bars


def _run_entry_only_session_integration(
    bars: tuple[DevelopmentReplayBar, ...],
):
    return replay._run_bars(
        bars,
        source_raw_sha256=SOURCE_RAW_SHA256,
        source_size_bytes=0,
        variant_id=VARIANT_ID,
        variant_protocol_sha256=VARIANT_PROTOCOL_SHA256,
        no_go_verdict=DevelopmentVerdict.NO_GO_VARIANT,
        entry_eligibility_evaluator=v1b_entry_session_allows,
    )


def test_ema20_exit_executes_at_1500_even_though_new_entries_are_excluded() -> None:
    bars = _entry_history_ending_at_1458_chicago()
    first_timestamp = bars[0].timestamp_utc
    bars.extend(
        (
            _history_bar(
                35,
                first_timestamp,
                close="101.50",
                open_price="101.25",
                high="102.00",
                low="100.50",
            ),
            _history_bar(
                36,
                first_timestamp,
                close="100.00",
                open_price="101.50",
                high="101.75",
                low="99.50",
            ),
            _history_bar(37, first_timestamp),
        )
    )

    result = _run_entry_only_session_integration(tuple(bars))

    assert result.counters.filled_entries == 1
    assert result.counters.ema20_exits == 1
    assert result.counters.structural_stop_exits == 0
    assert result.closed_trades[0].exit_timestamp_utc == datetime(2026, 6, 1, 20, 0, tzinfo=UTC)


def test_structural_stop_remains_active_on_the_excluded_1500_close() -> None:
    bars = _entry_history_ending_at_1458_chicago()
    first_timestamp = bars[0].timestamp_utc
    bars.extend(
        (
            _history_bar(
                35,
                first_timestamp,
                close="101.50",
                open_price="101.25",
                high="102.00",
                low="100.50",
            ),
            _history_bar(
                36,
                first_timestamp,
                close="100.00",
                open_price="101.50",
                high="101.75",
                low="99.25",
            ),
        )
    )

    result = _run_entry_only_session_integration(tuple(bars))

    assert result.counters.filled_entries == 1
    assert result.counters.structural_stop_exits == 1
    assert result.counters.ema20_exits == 0
    assert result.closed_trades[0].exit_timestamp_utc == datetime(2026, 6, 1, 20, 0, tzinfo=UTC)


def test_v1b_protocol_hash_parent_and_single_delta_are_exact() -> None:
    raw = VARIANT_PROTOCOL.read_bytes()
    payload = json.loads(raw)

    assert hashlib.sha256(raw).hexdigest() == VARIANT_PROTOCOL_SHA256
    assert payload["variant_id"] == VARIANT_ID
    assert payload["parent_variant"] == PARENT_VARIANT_ID
    assert payload["parent_result"] == {
        "verdict": "NO_GO_VARIANT",
        "result_sha256": PARENT_RESULT_SHA256,
        "retention": "IMMUTABLE",
    }
    assert payload["single_strategy_delta"] == {
        "field": "new_entry_session_filter",
        "enabled": True,
        "timezone": "America/Chicago",
        "start_local": "08:30:00",
        "start_comparison": "INCLUSIVE",
        "end_local": "15:00:00",
        "end_comparison": "EXCLUSIVE",
        "weekdays": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "dst_policy": "IANA_TIMEZONE_RULES",
        "decision_timestamp": "CLOSED_BAR_TIMESTAMP_T",
        "fixed_utc_offset": "FORBIDDEN",
        "scope": "NEW_ENTRIES_ONLY",
        "force_exit_at_end": False,
    }
    assert payload["screening"]["protocol_sha256"] == PROTOCOL_SHA256
    assert payload["screening"]["maximum_replay_count"] == 1
    assert payload["source_dataset"]["oos_access_permitted"] is False


def test_v1_and_v1a_sources_and_results_remain_byte_for_byte_immutable() -> None:
    expected = {
        V1_MODULE: "af9d9159262e6c027afada5d4faf1aa6374cf696c234ed1de554801d477dcac9",
        V1A_MODULE: "9f8b88f5b5f476b9f00a7f096e5b74d4eda79771fbce03e166cea699d0305f59",
        V1_RESULT: "4351d82e2b965b75843b0e24545358c80e2dc544a0549d085ceb8e93f4ceb3f6",
        V1A_RESULT: "29eef4a574fc46aab07a5ab60fc0c09fe111c3e72acc6d91ae3e5f04450582de",
    }

    assert {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in expected} == expected


def test_v1b_constants_are_exact() -> None:
    assert ENTRY_SESSION_FILTER_ENABLED is True
    assert ENTRY_SESSION_TIMEZONE == "America/Chicago"
    assert ENTRY_SESSION_START.isoformat() == "08:30:00"
    assert ENTRY_SESSION_END.isoformat() == "15:00:00"
    assert ENTRY_SESSION_WEEKDAYS == (0, 1, 2, 3, 4)
    assert DST_POLICY == "IANA_TIMEZONE_RULES"


def test_v1b_runner_identity_is_bound_to_v1a_and_the_new_protocol(monkeypatch) -> None:
    dataset = type(
        "Dataset",
        (),
        {"bars": (), "source_raw_sha256": "3" * 64, "source_size_bytes": 0},
    )()
    captured: dict[str, object] = {}

    def fake_run_bars(*args: object, **kwargs: object) -> object:
        captured.update(kwargs)
        return object()

    monkeypatch.setattr(variant, "load_preserved_development_raw", lambda path: dataset)
    monkeypatch.setattr(variant, "_run_bars", fake_run_bars)

    variant.run_preserved_v1b_development_replay("private-raw")

    assert captured["runner_id"] == RUNNER_ID
    assert captured["variant_id"] == VARIANT_ID
    assert captured["variant_protocol_sha256"] == VARIANT_PROTOCOL_SHA256
    assert captured["no_go_verdict"] is DevelopmentVerdict.NO_GO_VARIANT
    assert captured["slope_evaluator"] is evaluate_v1a_ema20_slope
    assert captured["entry_eligibility_evaluator"] is v1b_entry_session_allows


def test_recorded_v1b_result_is_aggregate_fail_closed_and_matches_parents() -> None:
    raw = V1B_RESULT.read_bytes()
    result = json.loads(raw)
    v1_raw = V1_RESULT.read_bytes()
    v1a_raw = V1A_RESULT.read_bytes()

    assert hashlib.sha256(raw).hexdigest() == (
        "d3b188c8efed50fc418dab25941b9237261bf39cb88a259c371d7e65e4a0e41b"
    )
    assert result["variant_id"] == VARIANT_ID
    assert result["parent_variant"] == PARENT_VARIANT_ID
    assert result["variant_protocol_sha256"] == VARIANT_PROTOCOL_SHA256
    assert result["screening_protocol_sha256"] == PROTOCOL_SHA256
    assert result["screening_thresholds_changed"] is False
    assert result["replay_count"] == 1
    assert result["verdict"] == "NO_GO_VARIANT"
    assert result["failed_criteria"] == [
        "maximum_drawdown_usd",
        "maximum_consecutive_losses",
        "segment_stability",
    ]

    counters = result["counters"]
    metrics = result["metrics"]
    segments = result["segments"]
    comparison = result["comparison_v1_v1a_v1b"]
    assert counters["qualified_signals"] == 339
    assert counters["rejected_by_session_filter"] == 780
    assert counters["qualified_signals"] + counters["rejected_by_session_filter"] == 1119
    assert (
        counters["structural_stop_exit_count"] + counters["ema20_exit_count"]
        == metrics["closed_trades"]
    )
    assert counters["total_actual_fills"] == metrics["closed_trades"] * 2
    assert sum(segment["closed_trades"] for segment in segments) == metrics["closed_trades"]
    assert sum(Decimal(segment["net_realized_pnl_usd"]) for segment in segments) == Decimal(
        metrics["net_realized_pnl_usd"]
    )

    assert comparison["v1"]["result_sha256"] == hashlib.sha256(v1_raw).hexdigest()
    assert comparison["v1"]["verdict"] == "NO_GO_BASELINE"
    assert comparison["v1a"]["result_sha256"] == hashlib.sha256(v1a_raw).hexdigest()
    assert comparison["v1a"]["verdict"] == "NO_GO_VARIANT"
    assert comparison["v1b"]["qualified_signals"] == counters["qualified_signals"]
    assert comparison["v1b"]["rejected_by_session_filter"] == counters["rejected_by_session_filter"]
    assert comparison["v1b"]["closed_trades"] == metrics["closed_trades"]

    assert result["entry_session"] == {
        "enabled": True,
        "timezone": "America/Chicago",
        "start_local_inclusive": "08:30:00",
        "end_local_exclusive": "15:00:00",
        "weekdays": "Monday-Friday",
        "dst_policy": "IANA_TIMEZONE_RULES",
        "fixed_utc_offset_used": False,
        "scope": "NEW_ENTRIES_ONLY",
        "force_exit_at_end": False,
    }
    observed_keys: set[str] = set()
    pending: list[object] = [result]
    while pending:
        current = pending.pop()
        if isinstance(current, dict):
            observed_keys.update(current)
            pending.extend(current.values())
        elif isinstance(current, list):
            pending.extend(current)
    assert observed_keys.isdisjoint(
        {"open", "high", "low", "close", "volume", "execution_price", "base_fill_price"}
    )
    assert result["oos_accessed"] is False
    assert result["raw_rows_exposed"] == 0
    assert result["prices_exposed"] == 0
    assert result["independent_validation_authorized"] is False
    assert result["alternate_session_test_authorized"] is False
