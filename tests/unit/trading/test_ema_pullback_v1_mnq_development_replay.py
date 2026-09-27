from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

import agicore.trading.ema_pullback_v1_mnq_development_replay as replay
from agicore.trading.ema_pullback_v1_mnq import (
    EntrySignal,
    PullbackSide,
    evaluate_ema_pullback_entry_signal,
)
from agicore.trading.ema_pullback_v1_mnq_development import (
    PROTOCOL_SHA256,
    SOURCE_RAW_SHA256,
    DevelopmentVerdict,
)
from agicore.trading.ema_pullback_v1_mnq_development_replay import (
    EXPECTED_FIRST_TIMESTAMP_UTC,
    EXPECTED_LAST_TIMESTAMP_UTC,
    EXPECTED_RAW_ROW_COUNT,
    EXPECTED_RAW_SIZE_BYTES,
    NORMAL_INTRABAR_STOP_TIMESTAMP_POLICY,
    OPEN_FILL_TIMESTAMP_POLICY,
    DevelopmentReplayBar,
    DevelopmentReplayError,
    load_preserved_development_raw,
    parse_ninjatrader_last_rows,
)

START = datetime(2026, 1, 1, tzinfo=UTC)


def _bar(
    sequence: int,
    *,
    close: str = "100.00",
    open_price: str | None = None,
    high: str | None = None,
    low: str | None = None,
) -> DevelopmentReplayBar:
    close_decimal = Decimal(close)
    open_decimal = Decimal(open_price or close)
    return DevelopmentReplayBar(
        sequence=sequence,
        timestamp_utc=START + timedelta(minutes=sequence + 1),
        open=open_decimal,
        high=Decimal(high)
        if high is not None
        else max(open_decimal, close_decimal) + Decimal("0.50"),
        low=Decimal(low) if low is not None else min(open_decimal, close_decimal) - Decimal("0.50"),
        close=close_decimal,
        volume=100,
    )


def _long_entry_history() -> list[DevelopmentReplayBar]:
    bars = [_bar(index) for index in range(34)]
    bars.append(
        _bar(
            34,
            close="101.00",
            open_price="100.00",
            high="101.00",
            low="99.75",
        )
    )
    return bars


def _ema_exit_history() -> tuple[DevelopmentReplayBar, ...]:
    bars = _long_entry_history()
    bars.extend(
        (
            _bar(
                35,
                close="101.50",
                open_price="101.25",
                high="102.00",
                low="100.50",
            ),
            _bar(
                36,
                close="100.00",
                open_price="101.50",
                high="101.75",
                low="99.50",
            ),
            _bar(
                37,
                close="100.00",
                open_price="100.00",
                high="100.25",
                low="99.75",
            ),
        )
    )
    return tuple(bars)


def _run_synthetic(bars: tuple[DevelopmentReplayBar, ...]):
    return replay._run_bars(
        bars,
        source_raw_sha256=SOURCE_RAW_SHA256,
        source_size_bytes=0,
    )


def test_preserved_raw_identity_constants_are_exact() -> None:
    assert EXPECTED_RAW_SIZE_BYTES == 2_791_485
    assert EXPECTED_RAW_ROW_COUNT == 52_431
    assert EXPECTED_FIRST_TIMESTAMP_UTC.isoformat() == "2026-03-31T22:01:00+00:00"
    assert EXPECTED_LAST_TIMESTAMP_UTC.isoformat() == "2026-06-11T21:00:00+00:00"
    assert OPEN_FILL_TIMESTAMP_POLICY == "SOURCE_BAR_CLOSE_MINUS_ONE_MINUTE"
    assert NORMAL_INTRABAR_STOP_TIMESTAMP_POLICY == "SOURCE_BAR_CLOSE_TIMESTAMP"


def test_parser_accepts_semicolon_ninjatrader_rows_without_header() -> None:
    text = (
        "20260101 000100;100.00;100.50;99.50;100.25;12\n"
        "20260101 000200;100.25;101.00;100.00;100.75;15"
    )
    bars = parse_ninjatrader_last_rows(text)

    assert len(bars) == 2
    assert bars[0].sequence == 0
    assert bars[-1].timestamp_utc == datetime(2026, 1, 1, 0, 2, tzinfo=UTC)
    assert bars[-1].volume == 15


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("20260101 000100;100;101;99;100", "six fields"),
        ("20260101 000100;100.10;101;99;100;1", "tick grid"),
        (
            "20260101 000100;100;101;99;100;1\n20260101 000100;100;101;99;100;1",
            "strictly increase",
        ),
        ("20260101 000100;100;99;101;100;1", "OHLC range"),
    ],
)
def test_parser_fails_closed_on_malformed_or_noncausal_rows(text: str, message: str) -> None:
    with pytest.raises(DevelopmentReplayError, match=message):
        parse_ninjatrader_last_rows(text)


def test_public_loader_rejects_any_noncanonical_bytes_before_replay(tmp_path) -> None:
    candidate = tmp_path / "MNQ 06-26.Last.txt"
    candidate.write_text("not the preserved raw", encoding="utf-8")

    with pytest.raises(DevelopmentReplayError, match="SHA-256 mismatch"):
        load_preserved_development_raw(candidate)


def test_precomputed_causal_signal_matches_the_frozen_contract() -> None:
    bars = tuple(_long_entry_history())
    closed_bars = replay._prepare_closed_bars(bars)
    macd, signal = replay._prepare_macd(bars)

    optimized = replay._candidate_entry_signal(
        sequence=34,
        closed_bars=closed_bars,
        macd=macd,
        signal=signal,
    )
    canonical = evaluate_ema_pullback_entry_signal(
        side=PullbackSide.LONG,
        closed_bars=closed_bars,
        confirmation_bar_sequence=34,
    )

    assert optimized == canonical
    assert optimized is not None
    assert optimized.signal is EntrySignal.LONG


def test_full_lifecycle_fills_next_open_and_exits_once_on_ema20() -> None:
    result = _run_synthetic(_ema_exit_history())

    assert result.protocol_sha256 == PROTOCOL_SHA256
    assert result.source_raw_sha256 == SOURCE_RAW_SHA256
    assert result.counters.qualified_entry_signals >= 1
    assert result.counters.filled_entries == 1
    assert result.counters.ema20_exits == 1
    assert result.counters.structural_stop_exits == 0
    assert result.counters.total_actual_fills == 2
    assert len(result.closed_trades) == 1
    assert result.closed_trades[0].entry_timestamp_utc == bars_open_timestamp(35)
    assert result.closed_trades[0].exit_timestamp_utc == bars_open_timestamp(37)
    assert result.closed_trades[0].net_realized_pnl_usd == Decimal("-4.52")
    assert result.open_position_at_end is False
    assert result.screening.verdict is DevelopmentVerdict.INSUFFICIENT_SAMPLE
    assert len(result.marked_equity_samples) == 38


def bars_open_timestamp(sequence: int) -> datetime:
    return START + timedelta(minutes=sequence)


def test_structural_stop_preempts_pending_ema_exit_at_same_open() -> None:
    bars = list(_ema_exit_history())
    bars[37] = _bar(
        37,
        close="99.00",
        open_price="99.00",
        high="99.50",
        low="98.50",
    )

    result = _run_synthetic(tuple(bars))

    assert result.counters.structural_stop_exits == 1
    assert result.counters.ema20_exits == 0
    assert result.counters.total_actual_fills == 2
    assert len(result.closed_trades) == 1


def test_normal_intrabar_stop_uses_closed_bar_timestamp_and_one_exit() -> None:
    bars = _long_entry_history()
    bars.append(
        _bar(
            35,
            close="99.50",
            open_price="101.25",
            high="101.50",
            low="99.25",
        )
    )

    result = _run_synthetic(tuple(bars))

    assert result.counters.structural_stop_exits == 1
    assert result.counters.ema20_exits == 0
    assert result.closed_trades[0].exit_timestamp_utc == bars[-1].timestamp_utc


def test_end_of_data_keeps_entry_open_without_synthetic_exit() -> None:
    bars = _long_entry_history()
    bars.append(
        _bar(
            35,
            close="101.50",
            open_price="101.25",
            high="102.00",
            low="100.50",
        )
    )

    result = _run_synthetic(tuple(bars))

    assert result.counters.filled_entries == 1
    assert result.counters.total_actual_fills == 1
    assert result.closed_trades == ()
    assert result.open_position_at_end is True
    assert result.screening.metrics.net_realized_pnl_usd == Decimal("0.00")
    assert result.unrealized_pnl_at_end_usd == Decimal("0.00")


def test_repeated_replay_is_deterministic_and_result_is_immutable() -> None:
    bars = _ema_exit_history()
    first = _run_synthetic(bars)
    second = _run_synthetic(bars)

    assert first == second
    with pytest.raises(FrozenInstanceError):
        first.replay_count = 2  # type: ignore[misc]


def test_bar_mutation_after_construction_cannot_change_frozen_instance() -> None:
    bar = _bar(0)
    with pytest.raises(FrozenInstanceError):
        bar.close = Decimal("200.00")  # type: ignore[misc]
    assert replace(bar, close=Decimal("100.25"), high=Decimal("100.50")).sequence == 0
