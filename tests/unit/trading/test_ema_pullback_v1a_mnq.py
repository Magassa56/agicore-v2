from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

import agicore.trading.ema_pullback_v1_mnq_development_replay as replay
from agicore.trading.ema_pullback_v1_mnq import (
    MACD_REQUIRED_CLOSED_BARS,
    ClosedBarEMA20,
    PullbackContractError,
    PullbackSide,
    evaluate_ema20_slope,
)
from agicore.trading.ema_pullback_v1_mnq_development import (
    PROTOCOL_SHA256,
    REQUIRED_DATASET_ROLE,
    DevelopmentClosedTrade,
    DevelopmentVerdict,
    MarkedEquitySample,
    evaluate_development_screening,
)
from agicore.trading.ema_pullback_v1a_mnq import (
    MINIMUM_ABSOLUTE_SLOPE_POINTS_PER_BAR,
    RUNNER_ID,
    VARIANT_ID,
    VARIANT_PROTOCOL_SHA256,
    evaluate_v1a_ema20_slope,
)

ROOT = Path(__file__).resolve().parents[3]
VARIANT_PROTOCOL = ROOT / "docs/evidence/EMA_PULLBACK_V1A_MNQ_VARIANT_PROTOCOL.json"
START = datetime(2026, 1, 1, tzinfo=UTC)


def _closed_bar(sequence: int, ema20: str, close: str | None = None) -> ClosedBarEMA20:
    ema = Decimal(ema20)
    closing = Decimal(close) if close is not None else ema
    return ClosedBarEMA20(
        sequence=sequence,
        low=min(ema, closing) - Decimal("0.25"),
        high=max(ema, closing) + Decimal("0.25"),
        close=closing,
        ema20=ema,
    )


@pytest.mark.parametrize(
    ("side", "lookback_ema", "confirmation_ema", "expected_slope"),
    [
        (PullbackSide.LONG, "100.00", "100.75", Decimal("0.25")),
        (PullbackSide.SHORT, "100.75", "100.00", Decimal("-0.25")),
    ],
)
def test_v1a_inclusive_one_tick_slope_boundary_qualifies(
    side: PullbackSide,
    lookback_ema: str,
    confirmation_ema: str,
    expected_slope: Decimal,
) -> None:
    result = evaluate_v1a_ema20_slope(
        side=side,
        lookback_bar=_closed_bar(10, lookback_ema),
        confirmation_bar=_closed_bar(13, confirmation_ema),
    )

    assert MINIMUM_ABSOLUTE_SLOPE_POINTS_PER_BAR == Decimal("0.25")
    assert result.slope_points_per_bar == expected_slope
    assert result.ema20_slope_qualifies is True


@pytest.mark.parametrize(
    ("side", "lookback_ema", "confirmation_ema", "expected_slope"),
    [
        (
            PullbackSide.LONG,
            "100",
            "100.749999999999999999999999",
            Decimal("0.2499999999999999999999996667"),
        ),
        (
            PullbackSide.SHORT,
            "100.75",
            "100.000000000000000000000001",
            Decimal("-0.2499999999999999999999996667"),
        ),
    ],
)
def test_v1a_near_boundary_is_rejected_without_rounding(
    side: PullbackSide,
    lookback_ema: str,
    confirmation_ema: str,
    expected_slope: Decimal,
) -> None:
    result = evaluate_v1a_ema20_slope(
        side=side,
        lookback_bar=_closed_bar(20, lookback_ema),
        confirmation_bar=_closed_bar(23, confirmation_ema),
    )

    assert result.slope_points_per_bar == expected_slope
    assert result.ema20_slope_qualifies is False


def test_v1_baseline_zero_threshold_remains_unchanged() -> None:
    lookback = _closed_bar(30, "100")
    confirmation = _closed_bar(33, "100.000000000000000000000003")

    baseline = evaluate_ema20_slope(
        side=PullbackSide.LONG,
        lookback_bar=lookback,
        confirmation_bar=confirmation,
    )
    variant = evaluate_v1a_ema20_slope(
        side=PullbackSide.LONG,
        lookback_bar=lookback,
        confirmation_bar=confirmation,
    )

    assert baseline.slope_points_per_bar == Decimal("0.000000000000000000000001")
    assert baseline.ema20_slope_qualifies is True
    assert variant.ema20_slope_qualifies is False


def test_v1a_slope_fails_closed_on_warmup_and_non_t_minus_three() -> None:
    with pytest.raises(PullbackContractError, match="warmup"):
        evaluate_v1a_ema20_slope(
            side=PullbackSide.LONG,
            lookback_bar=_closed_bar(0, "100"),
            confirmation_bar=_closed_bar(2, "101"),
        )
    with pytest.raises(PullbackContractError, match="exactly t-3"):
        evaluate_v1a_ema20_slope(
            side=PullbackSide.SHORT,
            lookback_bar=_closed_bar(8, "101"),
            confirmation_bar=_closed_bar(12, "100"),
        )


def _entry_inputs(
    confirmation_ema: str,
) -> tuple[tuple[ClosedBarEMA20, ...], tuple[Decimal | None, ...], tuple[Decimal | None, ...]]:
    bars = [_closed_bar(index, "100") for index in range(MACD_REQUIRED_CLOSED_BARS)]
    confirmation_sequence = MACD_REQUIRED_CLOSED_BARS - 1
    bars[confirmation_sequence - 3] = _closed_bar(confirmation_sequence - 3, "100")
    bars[confirmation_sequence - 2] = _closed_bar(confirmation_sequence - 2, "100.25")
    bars[confirmation_sequence - 1] = _closed_bar(confirmation_sequence - 1, "100.50")
    bars[confirmation_sequence] = _closed_bar(
        confirmation_sequence,
        confirmation_ema,
        close="101.00",
    )
    macd: list[Decimal | None] = [None] * MACD_REQUIRED_CLOSED_BARS
    signal: list[Decimal | None] = [None] * MACD_REQUIRED_CLOSED_BARS
    macd[-2], signal[-2] = Decimal(0), Decimal(0)
    macd[-1], signal[-1] = Decimal(1), Decimal(0)
    return tuple(bars), tuple(macd), tuple(signal)


def test_v1a_candidate_uses_only_the_new_slope_predicate() -> None:
    exact_bars, exact_macd, exact_signal = _entry_inputs("100.75")
    near_bars, near_macd, near_signal = _entry_inputs("100.749999999999999999999999")

    exact = replay._candidate_entry_signal(
        sequence=MACD_REQUIRED_CLOSED_BARS - 1,
        closed_bars=exact_bars,
        macd=exact_macd,
        signal=exact_signal,
        slope_evaluator=evaluate_v1a_ema20_slope,
    )
    near_variant = replay._candidate_entry_signal(
        sequence=MACD_REQUIRED_CLOSED_BARS - 1,
        closed_bars=near_bars,
        macd=near_macd,
        signal=near_signal,
        slope_evaluator=evaluate_v1a_ema20_slope,
    )
    near_baseline = replay._candidate_entry_signal(
        sequence=MACD_REQUIRED_CLOSED_BARS - 1,
        closed_bars=near_bars,
        macd=near_macd,
        signal=near_signal,
    )

    assert exact is not None
    assert near_variant is None
    assert near_baseline is not None


def test_variant_protocol_hash_and_single_delta_are_exact() -> None:
    raw = VARIANT_PROTOCOL.read_bytes()
    payload = json.loads(raw)

    assert hashlib.sha256(raw).hexdigest() == VARIANT_PROTOCOL_SHA256
    assert payload["variant_id"] == VARIANT_ID
    assert payload["single_strategy_delta"] == {
        "field": "minimum_absolute_ema20_slope_points_per_bar",
        "lookback_bars": 3,
        "formula": "(EMA20[t] - EMA20[t-3]) / 3",
        "baseline_value": "0.0",
        "variant_value": "0.25",
        "long_comparison": "slope >= +0.25",
        "short_comparison": "slope <= -0.25",
        "comparators_at_boundary": "INCLUSIVE",
        "rounding_before_comparison": "FORBIDDEN",
    }
    assert payload["screening"]["protocol_sha256"] == PROTOCOL_SHA256
    assert payload["screening"]["maximum_replay_count"] == 1
    assert payload["source_dataset"]["oos_access_permitted"] is False


def test_same_screening_thresholds_emit_variant_no_go_label() -> None:
    trades = tuple(
        DevelopmentClosedTrade(
            trade_index=index + 1,
            entry_timestamp_utc=START + timedelta(minutes=index * 3),
            exit_timestamp_utc=START + timedelta(minutes=index * 3 + 1),
            net_realized_pnl_usd=Decimal("-1.00"),
        )
        for index in range(100)
    )
    end = START + timedelta(minutes=300)
    equity = (
        MarkedEquitySample(START, Decimal("0.00"), Decimal("0.00"), Decimal("0.00")),
        MarkedEquitySample(end, Decimal("-100.00"), Decimal("0.00"), Decimal("-100.00")),
    )

    result = evaluate_development_screening(
        dataset_start_utc=START,
        dataset_end_utc=end,
        closed_trades=trades,
        marked_equity_samples=equity,
        dataset_role=REQUIRED_DATASET_ROLE,
        protocol_sha256=PROTOCOL_SHA256,
        oos_accessed=False,
        no_go_verdict=DevelopmentVerdict.NO_GO_VARIANT,
    )

    assert result.verdict is DevelopmentVerdict.NO_GO_VARIANT
    assert result.metrics.closed_trades == 100
    assert result.oos_accessed is False


def test_variant_runner_identity_is_distinct_and_bound_to_protocol(monkeypatch) -> None:
    dataset = type(
        "Dataset",
        (),
        {
            "bars": (),
            "source_raw_sha256": "3" * 64,
            "source_size_bytes": 0,
        },
    )()
    captured: dict[str, object] = {}

    def fake_run_bars(*args: object, **kwargs: object) -> object:
        captured.update(kwargs)
        return object()

    import agicore.trading.ema_pullback_v1a_mnq as variant

    monkeypatch.setattr(variant, "load_preserved_development_raw", lambda path: dataset)
    monkeypatch.setattr(variant, "_run_bars", fake_run_bars)

    variant.run_preserved_v1a_development_replay("private-raw")

    assert captured["runner_id"] == RUNNER_ID
    assert captured["variant_id"] == VARIANT_ID
    assert captured["variant_protocol_sha256"] == VARIANT_PROTOCOL_SHA256
    assert captured["no_go_verdict"] is DevelopmentVerdict.NO_GO_VARIANT
    assert captured["slope_evaluator"] is evaluate_v1a_ema20_slope
