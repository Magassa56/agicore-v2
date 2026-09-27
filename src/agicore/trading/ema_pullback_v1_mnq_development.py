"""Precommitted DEVELOPMENT screening for ``EMA_PULLBACK_V1_MNQ``.

This module evaluates already-produced deterministic replay evidence.  It never reads a
dataset, emits an order, accesses OOS data, or changes the frozen strategy.  The exact
protocol bytes are committed separately and bound here by SHA-256 before any historical
DEVELOPMENT replay is allowed.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import StrEnum

PROTOCOL_ID = "EMA_PULLBACK_V1_MNQ_DEVELOPMENT_SCREENING_2026_09_27"
PROTOCOL_SHA256 = "13f3e1b71ce27a848a16a9598c37d76e9298a49331531fc7602118ec788c864f"
STRATEGY_ID = "EMA_PULLBACK_V1_MNQ"
COST_MODEL_ID = "EMA_PULLBACK_V1_MNQ_COSTS_2026_09_27"
DATASET_ID = "mnq-06-26-minute-last-development-3bd8c078-v1"
SOURCE_RAW_SHA256 = "3bd8c078d40143ccb1977562e47afadfd173f9c123e3a062ba28dbcb7721ba1a"
REQUIRED_DATASET_ROLE = "EXPOSED_DEVELOPMENT"
MINIMUM_CLOSED_TRADES = 100
MINIMUM_NET_PNL_USD = Decimal("200.00")
MINIMUM_PROFIT_FACTOR = Decimal("1.15")
MAXIMUM_DRAWDOWN_USD = Decimal("750.00")
MAXIMUM_CONSECUTIVE_LOSSES = 8
MINIMUM_SEGMENT_CLOSED_TRADES = 15
MINIMUM_PROFITABLE_SEGMENTS = 2
MINIMUM_SEGMENT_PROFIT_FACTOR = Decimal("0.80")
MINIMUM_SEGMENT_NET_PNL_USD = Decimal("-200.00")
USD_CENT = Decimal("0.01")
SEGMENT_LABELS = ("DEVELOPMENT_S1", "DEVELOPMENT_S2", "DEVELOPMENT_S3")


class DevelopmentProtocolError(ValueError):
    """Raised when evidence violates the frozen DEVELOPMENT protocol."""


class SegmentStability(StrEnum):
    """Mechanical segment-stability outcome."""

    PASS = "PASS"
    FAIL = "FAIL"
    INSUFFICIENT_SAMPLE = "INSUFFICIENT_SAMPLE"


class DevelopmentVerdict(StrEnum):
    """Mechanical, non-performance-claim verdict."""

    INSUFFICIENT_SAMPLE = "INSUFFICIENT_SAMPLE"
    GO_TO_INDEPENDENT_VALIDATION = "GO_TO_INDEPENDENT_VALIDATION"
    NO_GO_BASELINE = "NO_GO_BASELINE"
    NO_GO_VARIANT = "NO_GO_VARIANT"


def _require_utc(value: datetime, field_name: str) -> None:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise DevelopmentProtocolError(f"{field_name} must be an aware UTC datetime")


def _require_usd(value: Decimal, field_name: str) -> None:
    if not isinstance(value, Decimal) or not value.is_finite():
        raise DevelopmentProtocolError(f"{field_name} must be a finite Decimal")
    if value != value.quantize(USD_CENT):
        raise DevelopmentProtocolError(f"{field_name} must use exact USD cents")


@dataclass(frozen=True)
class DevelopmentClosedTrade:
    """One actually closed trade, already net of the frozen V1 costs."""

    trade_index: int
    entry_timestamp_utc: datetime
    exit_timestamp_utc: datetime
    net_realized_pnl_usd: Decimal

    def __post_init__(self) -> None:
        if type(self.trade_index) is not int or self.trade_index < 1:
            raise DevelopmentProtocolError("trade_index must be a positive integer")
        _require_utc(self.entry_timestamp_utc, "entry_timestamp_utc")
        _require_utc(self.exit_timestamp_utc, "exit_timestamp_utc")
        if self.exit_timestamp_utc < self.entry_timestamp_utc:
            raise DevelopmentProtocolError("a closed trade cannot exit before entry")
        _require_usd(self.net_realized_pnl_usd, "net_realized_pnl_usd")


@dataclass(frozen=True)
class MarkedEquitySample:
    """Chronological close mark without converting latent PnL to realized PnL."""

    timestamp_utc: datetime
    realized_equity_usd: Decimal
    unrealized_pnl_usd: Decimal
    marked_equity_usd: Decimal

    def __post_init__(self) -> None:
        _require_utc(self.timestamp_utc, "timestamp_utc")
        for field_name in (
            "realized_equity_usd",
            "unrealized_pnl_usd",
            "marked_equity_usd",
        ):
            _require_usd(getattr(self, field_name), field_name)
        if self.marked_equity_usd != self.realized_equity_usd + self.unrealized_pnl_usd:
            raise DevelopmentProtocolError(
                "marked equity must equal realized equity plus unrealized PnL"
            )


@dataclass(frozen=True)
class DevelopmentSegmentMetrics:
    """Closed-trade metrics for one pre-split elapsed-time third."""

    label: str
    closed_trades: int
    net_realized_pnl_usd: Decimal
    profit_factor: Decimal
    net_profitable: bool


@dataclass(frozen=True)
class DevelopmentScreeningMetrics:
    """Metrics governed by the frozen exploratory screening protocol."""

    closed_trades: int
    net_realized_pnl_usd: Decimal
    profit_factor: Decimal
    maximum_drawdown_usd: Decimal
    maximum_consecutive_losses: int
    segments: tuple[DevelopmentSegmentMetrics, DevelopmentSegmentMetrics, DevelopmentSegmentMetrics]


@dataclass(frozen=True)
class DevelopmentScreeningResult:
    """Fail-closed protocol result; never a validation or profitability claim."""

    protocol_id: str
    protocol_sha256: str
    dataset_id: str
    source_raw_sha256: str
    dataset_role: str
    segment_stability: SegmentStability
    verdict: DevelopmentVerdict
    metrics: DevelopmentScreeningMetrics
    failed_criteria: tuple[str, ...]
    oos_accessed: bool = False
    performance_independence_claimed: bool = False
    strategy_validated: bool = False
    apex_readiness_claimed: bool = False


def compute_profit_factor(net_trade_pnls: Iterable[Decimal]) -> Decimal:
    """Return the project convention for net-after-cost closed-trade profit factor."""
    pnls = tuple(net_trade_pnls)
    if any(not isinstance(pnl, Decimal) or not pnl.is_finite() for pnl in pnls):
        raise DevelopmentProtocolError("profit factor requires finite Decimal trade PnL")
    gross_positive = sum((pnl for pnl in pnls if pnl > 0), Decimal(0))
    gross_negative = abs(sum((pnl for pnl in pnls if pnl < 0), Decimal(0)))
    if gross_negative == 0:
        return Decimal("Infinity") if gross_positive > 0 else Decimal(0)
    return gross_positive / gross_negative


def compute_maximum_consecutive_losses(net_trade_pnls: Iterable[Decimal]) -> int:
    """Count losses with zero and positive outcomes both resetting the streak."""
    current = 0
    maximum = 0
    for pnl in net_trade_pnls:
        if not isinstance(pnl, Decimal) or not pnl.is_finite():
            raise DevelopmentProtocolError("loss streak requires finite Decimal trade PnL")
        if pnl < 0:
            current += 1
            maximum = max(maximum, current)
        else:
            current = 0
    return maximum


def compute_maximum_marked_equity_drawdown(
    samples: Iterable[MarkedEquitySample],
) -> Decimal:
    """Compute absolute USD drawdown from chronological close-to-close marked equity."""
    points = tuple(samples)
    if not points:
        raise DevelopmentProtocolError("marked-equity samples are required")
    timestamps = tuple(point.timestamp_utc for point in points)
    if timestamps != tuple(sorted(timestamps)) or len(set(timestamps)) != len(timestamps):
        raise DevelopmentProtocolError("marked-equity samples must be strictly chronological")
    peak = Decimal("0.00")
    maximum = Decimal("0.00")
    for point in points:
        peak = max(peak, point.marked_equity_usd)
        maximum = max(maximum, peak - point.marked_equity_usd)
    return maximum.quantize(USD_CENT)


def _segment_index(timestamp: datetime, start: datetime, end: datetime) -> int:
    """Assign an instant to exact elapsed-time thirds without rounded boundaries."""
    if timestamp < start or timestamp > end:
        raise DevelopmentProtocolError("trade exit lies outside the DEVELOPMENT interval")
    span = end - start
    if span <= timedelta(0):
        raise DevelopmentProtocolError("DEVELOPMENT interval must have positive duration")
    offset = timestamp - start
    if offset * 3 < span:
        return 0
    if offset * 3 < span * 2:
        return 1
    return 2


def _segment_metrics(
    trades: tuple[DevelopmentClosedTrade, ...],
    start: datetime,
    end: datetime,
) -> tuple[DevelopmentSegmentMetrics, DevelopmentSegmentMetrics, DevelopmentSegmentMetrics]:
    buckets: tuple[
        list[DevelopmentClosedTrade], list[DevelopmentClosedTrade], list[DevelopmentClosedTrade]
    ] = (
        [],
        [],
        [],
    )
    for trade in trades:
        buckets[_segment_index(trade.exit_timestamp_utc, start, end)].append(trade)
    metrics = []
    for label, bucket in zip(SEGMENT_LABELS, buckets, strict=True):
        pnls = tuple(trade.net_realized_pnl_usd for trade in bucket)
        net_pnl = sum(pnls, Decimal(0)).quantize(USD_CENT)
        metrics.append(
            DevelopmentSegmentMetrics(
                label=label,
                closed_trades=len(bucket),
                net_realized_pnl_usd=net_pnl,
                profit_factor=compute_profit_factor(pnls),
                net_profitable=net_pnl > 0,
            )
        )
    return tuple(metrics)  # type: ignore[return-value]


def _validate_replay_evidence(
    *,
    dataset_start_utc: datetime,
    dataset_end_utc: datetime,
    trades: tuple[DevelopmentClosedTrade, ...],
    marked_equity: tuple[MarkedEquitySample, ...],
    dataset_role: str,
    protocol_sha256: str,
    oos_accessed: bool,
) -> None:
    _require_utc(dataset_start_utc, "dataset_start_utc")
    _require_utc(dataset_end_utc, "dataset_end_utc")
    if dataset_end_utc <= dataset_start_utc:
        raise DevelopmentProtocolError("DEVELOPMENT interval must have positive duration")
    if dataset_role != REQUIRED_DATASET_ROLE:
        raise DevelopmentProtocolError("only EXPOSED_DEVELOPMENT is allowed")
    if protocol_sha256 != PROTOCOL_SHA256:
        raise DevelopmentProtocolError("replay evidence is not bound to the frozen protocol hash")
    if type(oos_accessed) is not bool or oos_accessed:
        raise DevelopmentProtocolError("OOS access is forbidden by this protocol")
    if any(not isinstance(trade, DevelopmentClosedTrade) for trade in trades):
        raise DevelopmentProtocolError("all trade evidence must be actually closed trades")
    if tuple(trade.trade_index for trade in trades) != tuple(range(1, len(trades) + 1)):
        raise DevelopmentProtocolError("closed trades must retain consecutive replay order")
    trade_order = tuple((trade.exit_timestamp_utc, trade.trade_index) for trade in trades)
    if trade_order != tuple(sorted(trade_order)):
        raise DevelopmentProtocolError("closed trades must be chronological by exit fill")
    for trade in trades:
        if trade.entry_timestamp_utc < dataset_start_utc:
            raise DevelopmentProtocolError("trade entry lies before DEVELOPMENT")
        _segment_index(trade.exit_timestamp_utc, dataset_start_utc, dataset_end_utc)
    if not marked_equity:
        raise DevelopmentProtocolError("every replay requires marked-equity close samples")
    if marked_equity[0].timestamp_utc != dataset_start_utc:
        raise DevelopmentProtocolError("marked equity must start on the first DEVELOPMENT close")
    if marked_equity[-1].timestamp_utc != dataset_end_utc:
        raise DevelopmentProtocolError("marked equity must end on the final DEVELOPMENT close")


def evaluate_development_screening(
    *,
    dataset_start_utc: datetime,
    dataset_end_utc: datetime,
    closed_trades: Iterable[DevelopmentClosedTrade],
    marked_equity_samples: Iterable[MarkedEquitySample],
    dataset_role: str,
    protocol_sha256: str,
    oos_accessed: bool,
    no_go_verdict: DevelopmentVerdict = DevelopmentVerdict.NO_GO_BASELINE,
) -> DevelopmentScreeningResult:
    """Apply the frozen thresholds mechanically to one DEVELOPMENT replay."""
    if no_go_verdict not in (
        DevelopmentVerdict.NO_GO_BASELINE,
        DevelopmentVerdict.NO_GO_VARIANT,
    ):
        raise DevelopmentProtocolError(
            "no_go_verdict must explicitly distinguish baseline from variant"
        )
    trades = tuple(closed_trades)
    marked_equity = tuple(marked_equity_samples)
    _validate_replay_evidence(
        dataset_start_utc=dataset_start_utc,
        dataset_end_utc=dataset_end_utc,
        trades=trades,
        marked_equity=marked_equity,
        dataset_role=dataset_role,
        protocol_sha256=protocol_sha256,
        oos_accessed=oos_accessed,
    )

    pnls = tuple(trade.net_realized_pnl_usd for trade in trades)
    segments = _segment_metrics(trades, dataset_start_utc, dataset_end_utc)
    metrics = DevelopmentScreeningMetrics(
        closed_trades=len(trades),
        net_realized_pnl_usd=sum(pnls, Decimal(0)).quantize(USD_CENT),
        profit_factor=compute_profit_factor(pnls),
        maximum_drawdown_usd=compute_maximum_marked_equity_drawdown(marked_equity),
        maximum_consecutive_losses=compute_maximum_consecutive_losses(pnls),
        segments=segments,
    )

    if any(segment.closed_trades < MINIMUM_SEGMENT_CLOSED_TRADES for segment in segments):
        segment_stability = SegmentStability.INSUFFICIENT_SAMPLE
    else:
        stable = (
            sum(segment.net_profitable for segment in segments) >= MINIMUM_PROFITABLE_SEGMENTS
            and all(segment.profit_factor >= MINIMUM_SEGMENT_PROFIT_FACTOR for segment in segments)
            and all(
                segment.net_realized_pnl_usd >= MINIMUM_SEGMENT_NET_PNL_USD for segment in segments
            )
        )
        segment_stability = SegmentStability.PASS if stable else SegmentStability.FAIL

    failed: list[str] = []
    if metrics.closed_trades < MINIMUM_CLOSED_TRADES:
        failed.append("minimum_closed_trades")
    if any(segment.closed_trades < MINIMUM_SEGMENT_CLOSED_TRADES for segment in segments):
        failed.append("minimum_segment_closed_trades")
    if metrics.net_realized_pnl_usd < MINIMUM_NET_PNL_USD:
        failed.append("minimum_net_pnl_usd")
    if metrics.profit_factor < MINIMUM_PROFIT_FACTOR:
        failed.append("minimum_profit_factor")
    if metrics.maximum_drawdown_usd > MAXIMUM_DRAWDOWN_USD:
        failed.append("maximum_drawdown_usd")
    if metrics.maximum_consecutive_losses > MAXIMUM_CONSECUTIVE_LOSSES:
        failed.append("maximum_consecutive_losses")
    if segment_stability is SegmentStability.FAIL:
        failed.append("segment_stability")

    if (
        metrics.closed_trades < MINIMUM_CLOSED_TRADES
        or segment_stability is SegmentStability.INSUFFICIENT_SAMPLE
    ):
        verdict = DevelopmentVerdict.INSUFFICIENT_SAMPLE
    elif not failed:
        verdict = DevelopmentVerdict.GO_TO_INDEPENDENT_VALIDATION
    else:
        verdict = no_go_verdict

    return DevelopmentScreeningResult(
        protocol_id=PROTOCOL_ID,
        protocol_sha256=PROTOCOL_SHA256,
        dataset_id=DATASET_ID,
        source_raw_sha256=SOURCE_RAW_SHA256,
        dataset_role=REQUIRED_DATASET_ROLE,
        segment_stability=segment_stability,
        verdict=verdict,
        metrics=metrics,
        failed_criteria=tuple(failed),
        oos_accessed=False,
    )


__all__ = [
    "COST_MODEL_ID",
    "DATASET_ID",
    "MAXIMUM_CONSECUTIVE_LOSSES",
    "MAXIMUM_DRAWDOWN_USD",
    "MINIMUM_CLOSED_TRADES",
    "MINIMUM_NET_PNL_USD",
    "MINIMUM_PROFIT_FACTOR",
    "MINIMUM_SEGMENT_CLOSED_TRADES",
    "MINIMUM_SEGMENT_NET_PNL_USD",
    "MINIMUM_SEGMENT_PROFIT_FACTOR",
    "PROTOCOL_ID",
    "PROTOCOL_SHA256",
    "REQUIRED_DATASET_ROLE",
    "SEGMENT_LABELS",
    "SOURCE_RAW_SHA256",
    "DevelopmentClosedTrade",
    "DevelopmentProtocolError",
    "DevelopmentScreeningMetrics",
    "DevelopmentScreeningResult",
    "DevelopmentSegmentMetrics",
    "DevelopmentVerdict",
    "MarkedEquitySample",
    "SegmentStability",
    "compute_maximum_consecutive_losses",
    "compute_maximum_marked_equity_drawdown",
    "compute_profit_factor",
    "evaluate_development_screening",
]
