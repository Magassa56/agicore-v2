from __future__ import annotations

import hashlib
import json
from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from agicore.trading.ema_pullback_v1_mnq_development import (
    DATASET_ID,
    MAXIMUM_DRAWDOWN_USD,
    MINIMUM_NET_PNL_USD,
    MINIMUM_PROFIT_FACTOR,
    PROTOCOL_ID,
    PROTOCOL_SHA256,
    REQUIRED_DATASET_ROLE,
    SOURCE_RAW_SHA256,
    DevelopmentClosedTrade,
    DevelopmentProtocolError,
    DevelopmentVerdict,
    MarkedEquitySample,
    SegmentStability,
    compute_maximum_consecutive_losses,
    compute_maximum_marked_equity_drawdown,
    compute_profit_factor,
    evaluate_development_screening,
)

ROOT = Path(__file__).resolve().parents[3]
PROTOCOL = ROOT / "docs/evidence/EMA_PULLBACK_V1_MNQ_DEVELOPMENT_PROTOCOL.json"
START = datetime(2026, 1, 1, tzinfo=UTC)
END = START + timedelta(minutes=300)


def _trade(index: int, minute: int, pnl: str) -> DevelopmentClosedTrade:
    exit_timestamp = START + timedelta(minutes=minute)
    return DevelopmentClosedTrade(
        trade_index=index,
        entry_timestamp_utc=max(START, exit_timestamp - timedelta(minutes=1)),
        exit_timestamp_utc=exit_timestamp,
        net_realized_pnl_usd=Decimal(pnl),
    )


def _distributed_trades(pnls: list[str]) -> tuple[DevelopmentClosedTrade, ...]:
    counts = (34, 33, 33)
    starts = (1, 101, 201)
    trades: list[DevelopmentClosedTrade] = []
    cursor = 0
    for count, first_minute in zip(counts, starts, strict=True):
        for offset in range(count):
            if cursor >= len(pnls):
                return tuple(trades)
            trades.append(_trade(cursor + 1, first_minute + offset, pnls[cursor]))
            cursor += 1
    return tuple(trades)


def _equity(*values: tuple[int, str, str]) -> tuple[MarkedEquitySample, ...]:
    return tuple(
        MarkedEquitySample(
            timestamp_utc=START + timedelta(minutes=minute),
            realized_equity_usd=Decimal(realized),
            unrealized_pnl_usd=Decimal(unrealized),
            marked_equity_usd=Decimal(realized) + Decimal(unrealized),
        )
        for minute, realized, unrealized in values
    )


def _evaluate(
    trades: tuple[DevelopmentClosedTrade, ...],
    equity: tuple[MarkedEquitySample, ...] | None = None,
    **overrides: object,
):
    arguments: dict[str, object] = {
        "dataset_start_utc": START,
        "dataset_end_utc": END,
        "closed_trades": trades,
        "marked_equity_samples": equity or _equity((0, "0.00", "0.00"), (300, "0.00", "0.00")),
        "dataset_role": REQUIRED_DATASET_ROLE,
        "protocol_sha256": PROTOCOL_SHA256,
        "oos_accessed": False,
    }
    arguments.update(overrides)
    return evaluate_development_screening(**arguments)  # type: ignore[arg-type]


def test_protocol_bytes_hash_and_precommitted_contract_are_exact() -> None:
    raw = PROTOCOL.read_bytes()
    payload = json.loads(raw)

    assert hashlib.sha256(raw).hexdigest() == PROTOCOL_SHA256
    assert payload["protocol_id"] == PROTOCOL_ID
    assert payload["source_dataset"] == {
        "dataset_id": DATASET_ID,
        "source_raw_sha256": SOURCE_RAW_SHA256,
        "role": "DEVELOPMENT",
        "exposure_state": "EXPOSED_DEVELOPMENT",
        "oos_access_permitted": False,
    }
    assert payload["total_screening_thresholds"] == {
        "minimum_closed_trades": 100,
        "minimum_net_pnl_usd": "200.00",
        "minimum_profit_factor": "1.15",
        "maximum_drawdown_usd": "750.00",
        "maximum_consecutive_losses": 8,
        "comparators_at_boundary": "INCLUSIVE",
    }
    assert payload["execution"]["maximum_replay_count_for_this_protocol"] == 1
    assert payload["execution"]["threshold_changes_after_first_replay"] == "FORBIDDEN"
    assert payload["verdict_contract"]["go_is_strategy_validation"] is False


def test_all_total_boundaries_are_inclusive_and_exactly_100_trades_can_go() -> None:
    pnls = ["92.00" if index % 2 == 0 else "-80.00" for index in range(100)]
    trades = _distributed_trades(pnls)
    equity = _equity(
        (0, "0.00", "0.00"),
        (150, "100.00", "850.00"),
        (300, "600.00", "-400.00"),
    )

    result = _evaluate(trades, equity)

    assert result.metrics.closed_trades == 100
    assert result.metrics.net_realized_pnl_usd == Decimal("600.00")
    assert result.metrics.profit_factor == MINIMUM_PROFIT_FACTOR
    assert result.metrics.maximum_drawdown_usd == MAXIMUM_DRAWDOWN_USD
    assert result.metrics.maximum_consecutive_losses == 1
    assert result.segment_stability is SegmentStability.PASS
    assert result.verdict is DevelopmentVerdict.GO_TO_INDEPENDENT_VALIDATION
    assert result.performance_independence_claimed is False
    assert result.strategy_validated is False
    assert result.apex_readiness_claimed is False


def test_net_pnl_boundary_is_inclusive() -> None:
    result = _evaluate(
        _distributed_trades(["2.00"] * 100),
        _equity((0, "0.00", "0.00"), (300, "200.00", "0.00")),
    )

    assert result.metrics.net_realized_pnl_usd == MINIMUM_NET_PNL_USD
    assert result.metrics.profit_factor.is_infinite()
    assert result.verdict is DevelopmentVerdict.GO_TO_INDEPENDENT_VALIDATION


def test_profit_factor_uses_net_trade_pnl_and_zero_loss_project_convention() -> None:
    assert compute_profit_factor((Decimal("10.00"), Decimal("-5.00"))) == Decimal(2)
    assert compute_profit_factor((Decimal("0.00"), Decimal("3.00"))).is_infinite()
    assert compute_profit_factor((Decimal("0.00"), Decimal("0.00"))) == 0


def test_zero_and_wins_reset_the_loss_streak() -> None:
    pnls = [Decimal("-1.00")] * 8 + [Decimal("0.00")] + [Decimal("-1.00")] * 7
    pnls += [Decimal("1.00"), Decimal("-1.00")]
    assert compute_maximum_consecutive_losses(pnls) == 8


def test_drawdown_uses_chronological_marked_equity_not_realized_only() -> None:
    samples = _equity(
        (0, "0.00", "0.00"),
        (100, "100.00", "900.00"),
        (200, "100.00", "-650.00"),
        (300, "200.00", "0.00"),
    )
    assert compute_maximum_marked_equity_drawdown(samples) == Decimal("1550.00")


def test_total_sample_precedes_other_thresholds() -> None:
    result = _evaluate(_distributed_trades(["100.00"] * 99))

    assert result.metrics.closed_trades == 99
    assert result.verdict is DevelopmentVerdict.INSUFFICIENT_SAMPLE
    assert "minimum_closed_trades" in result.failed_criteria


def test_any_segment_below_15_is_insufficient_even_with_100_total_trades() -> None:
    trades = tuple(_trade(index + 1, index + 1, "2.00") for index in range(100))
    result = _evaluate(trades)

    assert [segment.closed_trades for segment in result.metrics.segments] == [99, 1, 0]
    assert result.segment_stability is SegmentStability.INSUFFICIENT_SAMPLE
    assert result.verdict is DevelopmentVerdict.INSUFFICIENT_SAMPLE


def test_failure_after_sufficient_samples_is_no_go_and_is_not_relabelled() -> None:
    result = _evaluate(
        _distributed_trades(["1.99"] * 100),
        _equity((0, "0.00", "0.00"), (300, "199.00", "0.00")),
    )

    assert result.metrics.net_realized_pnl_usd == Decimal("199.00")
    assert result.segment_stability is SegmentStability.PASS
    assert result.verdict is DevelopmentVerdict.NO_GO_BASELINE
    assert result.failed_criteria == ("minimum_net_pnl_usd",)


def test_exact_elapsed_time_boundaries_go_to_next_half_open_segment() -> None:
    trades = (
        _trade(1, 99, "1.00"),
        _trade(2, 100, "1.00"),
        _trade(3, 199, "1.00"),
        _trade(4, 200, "1.00"),
        _trade(5, 300, "1.00"),
    )
    result = _evaluate(trades)

    assert [segment.closed_trades for segment in result.metrics.segments] == [1, 2, 2]


@pytest.mark.parametrize(
    ("override", "message"),
    [
        ({"dataset_role": "OOS"}, "only EXPOSED_DEVELOPMENT"),
        ({"protocol_sha256": "0" * 64}, "frozen protocol hash"),
        ({"oos_accessed": True}, "OOS access is forbidden"),
    ],
)
def test_evidence_fails_closed_outside_precommitted_scope(
    override: dict[str, object], message: str
) -> None:
    with pytest.raises(DevelopmentProtocolError, match=message):
        _evaluate((), **override)


def test_marked_equity_identity_and_chronology_fail_closed() -> None:
    with pytest.raises(DevelopmentProtocolError, match="must equal"):
        MarkedEquitySample(
            timestamp_utc=START,
            realized_equity_usd=Decimal("1.00"),
            unrealized_pnl_usd=Decimal("2.00"),
            marked_equity_usd=Decimal("4.00"),
        )

    reversed_samples = tuple(reversed(_equity((0, "0.00", "0.00"), (300, "1.00", "0.00"))))
    with pytest.raises(DevelopmentProtocolError, match="strictly chronological"):
        compute_maximum_marked_equity_drawdown(reversed_samples)


def test_result_is_deterministic_and_immutable() -> None:
    trades = _distributed_trades(["2.00"] * 100)
    first = _evaluate(trades)
    assert first == _evaluate(trades)
    with pytest.raises(FrozenInstanceError):
        first.verdict = DevelopmentVerdict.NO_GO_BASELINE  # type: ignore[misc]
