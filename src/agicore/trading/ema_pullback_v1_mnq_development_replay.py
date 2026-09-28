"""Single deterministic EXPOSED_DEVELOPMENT replay for EMA pullback V1.

The public entry point accepts only the preserved clean-lineage RAW and verifies its
bytes before parsing.  It performs no network, broker, account, Risk Engine, or OOS
operation.  Returned evidence contains PnL metrics and timestamps, never market prices
or raw OHLCV rows.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path

from .ema_pullback_v1_mnq import (
    COST_MODEL_ID,
    EMA_PERIOD,
    MACD_FAST_PERIOD,
    MACD_REQUIRED_CLOSED_BARS,
    MACD_SIGNAL_PERIOD,
    MACD_SLOW_PERIOD,
    MNQ_POINT_VALUE_USD,
    MNQ_TICK_SIZE_POINTS,
    SOURCE_TRADING_HOURS_TEMPLATE,
    USD_CENT,
    ClosedBarEMA20,
    CostApplicationStatus,
    EMA20SlopeResult,
    EMAPullbackEntrySignalResult,
    EntrySignal,
    InitialStopFillSource,
    InitialStopTriggerStatus,
    MACDCrossResult,
    MACDStatus,
    NextBarOpen,
    ProtectedEntryExecutionResult,
    PullbackSide,
    StopEvaluationBar,
    V1CostedFillResult,
    apply_v1_execution_costs,
    arbitrate_exit_at_open,
    assemble_ema_pullback_entry_signal,
    calculate_ema,
    calculate_v1_realized_trade_pnl,
    evaluate_disabled_session_filter,
    evaluate_ema20_position_exit,
    evaluate_ema20_slope,
    evaluate_initial_stop_on_bar,
    evaluate_pullback_confirmation,
    simulate_entry_with_initial_structural_stop,
)
from .ema_pullback_v1_mnq_development import (
    DATASET_ID,
    PROTOCOL_ID,
    PROTOCOL_SHA256,
    REQUIRED_DATASET_ROLE,
    SOURCE_RAW_SHA256,
    DevelopmentClosedTrade,
    DevelopmentScreeningResult,
    DevelopmentVerdict,
    MarkedEquitySample,
    evaluate_development_screening,
)

RUNNER_ID = "EMA_PULLBACK_V1_MNQ_DEVELOPMENT_REPLAY_V1"
RUNNER_VERSION = "1.0"
EXPECTED_RAW_SIZE_BYTES = 2_791_485
EXPECTED_RAW_ROW_COUNT = 52_431
EXPECTED_FIRST_TIMESTAMP_UTC = datetime(2026, 3, 31, 22, 1, tzinfo=UTC)
EXPECTED_LAST_TIMESTAMP_UTC = datetime(2026, 6, 11, 21, 0, tzinfo=UTC)
RAW_TIMESTAMP_FORMAT = "%Y%m%d %H%M%S"
BAR_INTERVAL = timedelta(minutes=1)
NORMAL_INTRABAR_STOP_TIMESTAMP_POLICY = "SOURCE_BAR_CLOSE_TIMESTAMP"
OPEN_FILL_TIMESTAMP_POLICY = "SOURCE_BAR_CLOSE_MINUS_ONE_MINUTE"


class DevelopmentReplayError(ValueError):
    """Raised when the exact RAW or deterministic replay contract fails closed."""


@dataclass(frozen=True)
class DevelopmentReplayBar:
    """One verified NinjaTrader one-minute Last bar."""

    sequence: int
    timestamp_utc: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int

    def __post_init__(self) -> None:
        if type(self.sequence) is not int or self.sequence < 0:
            raise DevelopmentReplayError("bar sequence must be a non-negative integer")
        if self.timestamp_utc.tzinfo is None or self.timestamp_utc.utcoffset() != timedelta(0):
            raise DevelopmentReplayError("bar timestamp must be aware UTC")
        for field_name in ("open", "high", "low", "close"):
            value = getattr(self, field_name)
            if (
                not isinstance(value, Decimal)
                or not value.is_finite()
                or value <= 0
                or value % MNQ_TICK_SIZE_POINTS
            ):
                raise DevelopmentReplayError(
                    f"{field_name} must be positive on the exact MNQ tick grid"
                )
        if self.high < max(self.open, self.low, self.close) or self.low > min(
            self.open, self.high, self.close
        ):
            raise DevelopmentReplayError("bar OHLC range is inconsistent")
        if type(self.volume) is not int or self.volume < 0:
            raise DevelopmentReplayError("bar volume must be a non-negative integer")


@dataclass(frozen=True)
class VerifiedDevelopmentDataset:
    """Bytes-verified private dataset held only in memory."""

    bars: tuple[DevelopmentReplayBar, ...]
    source_raw_sha256: str
    source_size_bytes: int
    source_row_count: int
    dataset_id: str = DATASET_ID
    dataset_role: str = REQUIRED_DATASET_ROLE
    oos_accessed: bool = False

    def __post_init__(self) -> None:
        if (
            self.source_raw_sha256 != SOURCE_RAW_SHA256
            or self.source_size_bytes != EXPECTED_RAW_SIZE_BYTES
            or self.source_row_count != EXPECTED_RAW_ROW_COUNT
            or self.dataset_id != DATASET_ID
            or self.dataset_role != REQUIRED_DATASET_ROLE
            or self.oos_accessed is not False
        ):
            raise DevelopmentReplayError("dataset identity or DEVELOPMENT boundary mismatch")
        if len(self.bars) != EXPECTED_RAW_ROW_COUNT:
            raise DevelopmentReplayError("verified dataset row count mismatch")
        if (
            self.bars[0].timestamp_utc != EXPECTED_FIRST_TIMESTAMP_UTC
            or self.bars[-1].timestamp_utc != EXPECTED_LAST_TIMESTAMP_UTC
        ):
            raise DevelopmentReplayError("verified dataset temporal bounds mismatch")


@dataclass(frozen=True)
class DevelopmentReplayCounters:
    """Sanitized lifecycle counts; no market price is retained."""

    qualified_entry_signals: int
    ignored_signals_while_open: int
    filled_entries: int
    rejected_entries: int
    expired_entries: int
    structural_stop_exits: int
    ema20_exits: int
    expired_ema20_exits: int
    total_actual_fills: int
    rejected_by_session_filter: int = 0


@dataclass(frozen=True)
class DevelopmentReplayResult:
    """Sanitized evidence from the one allowed DEVELOPMENT baseline replay."""

    run_id: str
    runner_id: str
    runner_version: str
    protocol_id: str
    protocol_sha256: str
    dataset_id: str
    dataset_role: str
    source_raw_sha256: str
    source_size_bytes: int
    source_row_count: int
    first_timestamp_utc: datetime
    last_timestamp_utc: datetime
    counters: DevelopmentReplayCounters
    closed_trades: tuple[DevelopmentClosedTrade, ...]
    marked_equity_samples: tuple[MarkedEquitySample, ...]
    screening: DevelopmentScreeningResult
    open_position_at_end: bool
    unrealized_pnl_at_end_usd: Decimal
    variant_id: str | None = None
    variant_protocol_sha256: str | None = None
    replay_count: int = 1
    deterministic: bool = True
    oos_accessed: bool = False
    raw_rows_exposed: int = 0
    prices_exposed: int = 0


@dataclass(frozen=True)
class _PendingEntry:
    decision: EMAPullbackEntrySignalResult
    decision_bar: ClosedBarEMA20
    required_touch_bar: ClosedBarEMA20


@dataclass(frozen=True)
class _OpenPosition:
    execution: ProtectedEntryExecutionResult
    costed_entry: V1CostedFillResult
    entry_timestamp_utc: datetime


def _round_usd(value: Decimal) -> Decimal:
    return value.quantize(USD_CENT, rounding=ROUND_HALF_UP)


def parse_ninjatrader_last_rows(text: str) -> tuple[DevelopmentReplayBar, ...]:
    """Parse sanitized NinjaTrader text without logging or returning source rows."""
    if not isinstance(text, str) or not text:
        raise DevelopmentReplayError("NinjaTrader Last text is required")
    raw_lines = text.splitlines()
    if not raw_lines or any(not line for line in raw_lines):
        raise DevelopmentReplayError("NinjaTrader Last text contains an empty row")

    bars: list[DevelopmentReplayBar] = []
    previous_timestamp: datetime | None = None
    for sequence, line in enumerate(raw_lines):
        fields = line.split(";")
        if len(fields) != 6:
            raise DevelopmentReplayError("every NinjaTrader Last row must contain six fields")
        try:
            timestamp = datetime.strptime(fields[0], RAW_TIMESTAMP_FORMAT).replace(tzinfo=UTC)
            open_price, high, low, close = (Decimal(value) for value in fields[1:5])
            volume_decimal = Decimal(fields[5])
        except (ValueError, InvalidOperation) as exc:
            raise DevelopmentReplayError("NinjaTrader Last row has an invalid field") from exc
        if volume_decimal != volume_decimal.to_integral_value():
            raise DevelopmentReplayError("NinjaTrader Last volume must be integral")
        if previous_timestamp is not None and timestamp <= previous_timestamp:
            raise DevelopmentReplayError("NinjaTrader Last timestamps must strictly increase")
        previous_timestamp = timestamp
        bars.append(
            DevelopmentReplayBar(
                sequence=sequence,
                timestamp_utc=timestamp,
                open=open_price,
                high=high,
                low=low,
                close=close,
                volume=int(volume_decimal),
            )
        )
    return tuple(bars)


def load_preserved_development_raw(path: str | Path) -> VerifiedDevelopmentDataset:
    """Verify exact private bytes first, then parse the clean DEVELOPMENT root."""
    raw_path = Path(path)
    try:
        raw = raw_path.read_bytes()
    except OSError as exc:
        raise DevelopmentReplayError("preserved DEVELOPMENT RAW is unavailable") from exc
    digest = hashlib.sha256(raw).hexdigest()
    if digest != SOURCE_RAW_SHA256:
        raise DevelopmentReplayError("preserved DEVELOPMENT RAW SHA-256 mismatch")
    if len(raw) != EXPECTED_RAW_SIZE_BYTES:
        raise DevelopmentReplayError("preserved DEVELOPMENT RAW size mismatch")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise DevelopmentReplayError("preserved DEVELOPMENT RAW encoding is invalid") from exc
    bars = parse_ninjatrader_last_rows(text)
    return VerifiedDevelopmentDataset(
        bars=bars,
        source_raw_sha256=digest,
        source_size_bytes=len(raw),
        source_row_count=len(bars),
    )


def _prepare_closed_bars(
    bars: tuple[DevelopmentReplayBar, ...],
) -> tuple[ClosedBarEMA20, ...]:
    if not bars:
        raise DevelopmentReplayError("DEVELOPMENT replay requires bars")
    if tuple(bar.sequence for bar in bars) != tuple(range(len(bars))):
        raise DevelopmentReplayError("DEVELOPMENT bars must retain contiguous source order")
    timestamps = tuple(bar.timestamp_utc for bar in bars)
    if timestamps != tuple(sorted(timestamps)) or len(timestamps) != len(set(timestamps)):
        raise DevelopmentReplayError("DEVELOPMENT bars must have unique chronological timestamps")
    closes = [float(bar.close) for bar in bars]
    ema20 = calculate_ema(closes, EMA_PERIOD)
    return tuple(
        ClosedBarEMA20(
            sequence=bar.sequence,
            low=bar.low,
            high=bar.high,
            close=bar.close,
            ema20=Decimal(str(ema20[bar.sequence])),
        )
        for bar in bars
    )


def _prepare_macd(
    bars: tuple[DevelopmentReplayBar, ...],
) -> tuple[tuple[Decimal | None, ...], tuple[Decimal | None, ...]]:
    closes = [float(bar.close) for bar in bars]
    fast = calculate_ema(closes, MACD_FAST_PERIOD)
    slow = calculate_ema(closes, MACD_SLOW_PERIOD)
    first_warmed_index = MACD_SLOW_PERIOD - 1
    macd_values = [fast[index] - slow[index] for index in range(first_warmed_index, len(bars))]
    signal_values = calculate_ema(macd_values, MACD_SIGNAL_PERIOD)
    macd: list[Decimal | None] = [None] * len(bars)
    signal: list[Decimal | None] = [None] * len(bars)
    for offset, value in enumerate(macd_values):
        source_index = first_warmed_index + offset
        macd[source_index] = Decimal(str(value))
        signal[source_index] = Decimal(str(signal_values[offset]))
    return tuple(macd), tuple(signal)


def _macd_cross_result(
    *,
    side: PullbackSide,
    sequence: int,
    macd: tuple[Decimal | None, ...],
    signal: tuple[Decimal | None, ...],
) -> MACDCrossResult:
    if sequence + 1 < MACD_REQUIRED_CLOSED_BARS:
        return MACDCrossResult(
            side=side,
            status=MACDStatus.INSUFFICIENT_WARMUP,
            signal=EntrySignal.NONE,
            macd_cross_qualifies=False,
            previous_macd_line=None,
            previous_signal_line=None,
            current_macd_line=None,
            current_signal_line=None,
            previous_bar_sequence=None,
            confirmation_bar_sequence=sequence,
            observed_closed_bars=sequence + 1,
        )
    previous_macd = macd[sequence - 1]
    previous_signal = signal[sequence - 1]
    current_macd = macd[sequence]
    current_signal = signal[sequence]
    if not all(
        isinstance(value, Decimal)
        for value in (previous_macd, previous_signal, current_macd, current_signal)
    ):
        raise DevelopmentReplayError("precomputed MACD warmup is inconsistent")
    bullish = previous_macd <= previous_signal and current_macd > current_signal
    bearish = previous_macd >= previous_signal and current_macd < current_signal
    qualifies = bullish if side is PullbackSide.LONG else bearish
    return MACDCrossResult(
        side=side,
        status=MACDStatus.READY,
        signal=EntrySignal(side.value) if qualifies else EntrySignal.NONE,
        macd_cross_qualifies=qualifies,
        previous_macd_line=previous_macd,
        previous_signal_line=previous_signal,
        current_macd_line=current_macd,
        current_signal_line=current_signal,
        previous_bar_sequence=sequence - 1,
        confirmation_bar_sequence=sequence,
        observed_closed_bars=sequence + 1,
    )


def _candidate_entry_signal(
    *,
    sequence: int,
    closed_bars: tuple[ClosedBarEMA20, ...],
    macd: tuple[Decimal | None, ...],
    signal: tuple[Decimal | None, ...],
    slope_evaluator: Callable[..., EMA20SlopeResult] = evaluate_ema20_slope,
) -> EMAPullbackEntrySignalResult | None:
    if sequence + 1 < MACD_REQUIRED_CLOSED_BARS:
        return None
    long_macd = _macd_cross_result(
        side=PullbackSide.LONG,
        sequence=sequence,
        macd=macd,
        signal=signal,
    )
    short_macd = _macd_cross_result(
        side=PullbackSide.SHORT,
        sequence=sequence,
        macd=macd,
        signal=signal,
    )
    qualifying_sides = [
        side
        for side, result in (
            (PullbackSide.LONG, long_macd),
            (PullbackSide.SHORT, short_macd),
        )
        if result.macd_cross_qualifies
    ]
    if not qualifying_sides:
        return None
    if len(qualifying_sides) != 1:
        raise DevelopmentReplayError("one closed bar cannot contain two MACD cross directions")
    side = qualifying_sides[0]
    confirmation = closed_bars[sequence]
    preceding = closed_bars[sequence - 3 : sequence]
    pullback = evaluate_pullback_confirmation(
        side=side,
        preceding_bars=preceding,
        confirmation_bar=confirmation,
    )
    slope = slope_evaluator(
        side=side,
        lookback_bar=preceding[0],
        confirmation_bar=confirmation,
    )
    result = assemble_ema_pullback_entry_signal(
        side=side,
        pullback=pullback,
        slope=slope,
        macd=long_macd if side is PullbackSide.LONG else short_macd,
    )
    return result if result.entry_signal_qualifies else None


def _open_timestamp(bar: DevelopmentReplayBar) -> datetime:
    return bar.timestamp_utc - BAR_INTERVAL


def _unrealized_pnl(position: _OpenPosition | None, close: Decimal) -> Decimal:
    if position is None:
        return Decimal("0.00")
    entry = position.costed_entry.execution_price
    if entry is None:
        raise DevelopmentReplayError("open position lacks its costed entry price")
    signed = Decimal(1) if position.execution.side is PullbackSide.LONG else Decimal(-1)
    return _round_usd((close - entry) * signed * MNQ_POINT_VALUE_USD)


def _run_bars(
    bars: tuple[DevelopmentReplayBar, ...],
    *,
    source_raw_sha256: str,
    source_size_bytes: int,
    slope_evaluator: Callable[..., EMA20SlopeResult] = evaluate_ema20_slope,
    runner_id: str = RUNNER_ID,
    runner_version: str = RUNNER_VERSION,
    variant_id: str | None = None,
    variant_protocol_sha256: str | None = None,
    no_go_verdict: DevelopmentVerdict = DevelopmentVerdict.NO_GO_BASELINE,
    entry_eligibility_evaluator: Callable[[datetime], bool] | None = None,
) -> DevelopmentReplayResult:
    """Run already-verified bars; public callers must use the hash-verifying wrapper."""
    if (variant_id is None) is not (variant_protocol_sha256 is None):
        raise DevelopmentReplayError("variant id and protocol hash must be supplied together")
    if entry_eligibility_evaluator is not None and variant_id is None:
        raise DevelopmentReplayError("an entry filter requires an explicit variant contract")
    closed_bars = _prepare_closed_bars(bars)
    macd, signal = _prepare_macd(bars)
    evaluate_disabled_session_filter(
        source_bar_sequence=0,
        source_bar_closed=True,
        source_bar_valid=True,
        source_trading_hours_template=SOURCE_TRADING_HOURS_TEMPLATE,
    )

    position: _OpenPosition | None = None
    pending_entry: _PendingEntry | None = None
    pending_ema20_exit = None
    closed_trades: list[DevelopmentClosedTrade] = []
    marked_equity: list[MarkedEquitySample] = []
    realized_equity = Decimal("0.00")
    qualified_signals = 0
    rejected_by_session_filter = 0
    ignored_signals = 0
    filled_entries = 0
    rejected_entries = 0
    expired_entries = 0
    structural_exits = 0
    ema20_exits = 0
    expired_ema20_exits = 0
    total_fills = 0

    def close_position(exit_fill: V1CostedFillResult, timestamp: datetime) -> None:
        nonlocal position, realized_equity, total_fills, structural_exits, ema20_exits
        if position is None:
            raise DevelopmentReplayError("exit fill requires one open position")
        trade_pnl = calculate_v1_realized_trade_pnl(
            entry_fill=position.costed_entry,
            exit_fill=exit_fill,
        )
        entry_execution_price = position.costed_entry.execution_price
        if exit_fill.execution_price is None or entry_execution_price is None:
            raise DevelopmentReplayError("costed trade lacks an execution price")
        signed = Decimal(1) if position.execution.side is PullbackSide.LONG else Decimal(-1)
        gross_exit_delta = (
            (exit_fill.execution_price - entry_execution_price) * signed * MNQ_POINT_VALUE_USD
        )
        realized_equity = _round_usd(realized_equity + gross_exit_delta - exit_fill.commission_usd)
        closed_trades.append(
            DevelopmentClosedTrade(
                trade_index=len(closed_trades) + 1,
                entry_timestamp_utc=position.entry_timestamp_utc,
                exit_timestamp_utc=timestamp,
                net_realized_pnl_usd=trade_pnl.net_realized_pnl_usd,
            )
        )
        if exit_fill.event_kind.value == "STRUCTURAL_STOP":
            structural_exits += 1
        else:
            ema20_exits += 1
        total_fills += 1
        position = None

    for index, (bar, closed_bar) in enumerate(zip(bars, closed_bars, strict=True)):
        if position is not None and pending_ema20_exit is not None:
            priority = arbitrate_exit_at_open(
                position=position.execution,
                pending_ema20_exit=pending_ema20_exit,
                execution_bar=NextBarOpen(sequence=index, open=bar.open),
            )
            exit_fill = apply_v1_execution_costs(priority)
            close_position(exit_fill, _open_timestamp(bar))
            pending_ema20_exit = None

        if pending_entry is not None:
            if position is not None:
                raise DevelopmentReplayError("pending entry cannot coexist with an open position")
            execution = simulate_entry_with_initial_structural_stop(
                decision=pending_entry.decision,
                decision_bar=pending_entry.decision_bar,
                required_touch_bar=pending_entry.required_touch_bar,
                available_bar_opens=(NextBarOpen(sequence=index, open=bar.open),),
            )
            costed_entry = apply_v1_execution_costs(execution)
            if costed_entry.status is CostApplicationStatus.FILLED:
                position = _OpenPosition(
                    execution=execution,
                    costed_entry=costed_entry,
                    entry_timestamp_utc=_open_timestamp(bar),
                )
                realized_equity = _round_usd(realized_equity - costed_entry.commission_usd)
                filled_entries += 1
                total_fills += 1
            else:
                rejected_entries += 1
            pending_entry = None

        if position is not None:
            stop_result = evaluate_initial_stop_on_bar(
                position=position.execution,
                bar=StopEvaluationBar(
                    sequence=index,
                    open=bar.open,
                    low=bar.low,
                    high=bar.high,
                ),
            )
            if stop_result.status is InitialStopTriggerStatus.STOP_TRIGGERED:
                stop_fill = apply_v1_execution_costs(stop_result)
                stop_timestamp = (
                    _open_timestamp(bar)
                    if stop_result.fill_source is InitialStopFillSource.BAR_OPEN_GAP
                    else bar.timestamp_utc
                )
                close_position(stop_fill, stop_timestamp)

        candidate = _candidate_entry_signal(
            sequence=index,
            closed_bars=closed_bars,
            macd=macd,
            signal=signal,
            slope_evaluator=slope_evaluator,
        )
        if candidate is not None:
            entry_allowed = (
                True
                if entry_eligibility_evaluator is None
                else entry_eligibility_evaluator(bar.timestamp_utc)
            )
            if type(entry_allowed) is not bool:
                raise DevelopmentReplayError("entry eligibility evaluator must return bool")
            if entry_allowed:
                qualified_signals += 1
            else:
                rejected_by_session_filter += 1
                candidate = None

        if position is not None:
            if candidate is not None:
                ignored_signals += 1
            exit_decision = evaluate_ema20_position_exit(
                position_side=position.execution.side,
                closed_bars=(closed_bar,),
                decision_bar_sequence=index,
            )
            pending_ema20_exit = exit_decision if exit_decision.exit_qualifies else None
        elif candidate is not None:
            pending_entry = _PendingEntry(
                decision=candidate,
                decision_bar=closed_bar,
                required_touch_bar=closed_bars[index - 2],
            )

        unrealized = _unrealized_pnl(position, bar.close)
        marked_equity.append(
            MarkedEquitySample(
                timestamp_utc=bar.timestamp_utc,
                realized_equity_usd=realized_equity,
                unrealized_pnl_usd=unrealized,
                marked_equity_usd=_round_usd(realized_equity + unrealized),
            )
        )

    if pending_entry is not None:
        expired_entries += 1
    if pending_ema20_exit is not None:
        expired_ema20_exits += 1

    screening = evaluate_development_screening(
        dataset_start_utc=bars[0].timestamp_utc,
        dataset_end_utc=bars[-1].timestamp_utc,
        closed_trades=closed_trades,
        marked_equity_samples=marked_equity,
        dataset_role=REQUIRED_DATASET_ROLE,
        protocol_sha256=PROTOCOL_SHA256,
        oos_accessed=False,
        no_go_verdict=no_go_verdict,
    )
    run_payload = {
        "cost_model_id": COST_MODEL_ID,
        "dataset_id": DATASET_ID,
        "protocol_sha256": PROTOCOL_SHA256,
        "runner_id": runner_id,
        "runner_version": runner_version,
        "source_raw_sha256": source_raw_sha256,
    }
    if variant_id is not None and variant_protocol_sha256 is not None:
        run_payload["variant_id"] = variant_id
        run_payload["variant_protocol_sha256"] = variant_protocol_sha256
    run_hash = hashlib.sha256(
        json.dumps(run_payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    counters = DevelopmentReplayCounters(
        qualified_entry_signals=qualified_signals,
        ignored_signals_while_open=ignored_signals,
        filled_entries=filled_entries,
        rejected_entries=rejected_entries,
        expired_entries=expired_entries,
        structural_stop_exits=structural_exits,
        ema20_exits=ema20_exits,
        expired_ema20_exits=expired_ema20_exits,
        total_actual_fills=total_fills,
        rejected_by_session_filter=rejected_by_session_filter,
    )
    return DevelopmentReplayResult(
        run_id=f"ema-pullback-development-{run_hash[:16]}",
        runner_id=runner_id,
        runner_version=runner_version,
        protocol_id=PROTOCOL_ID,
        protocol_sha256=PROTOCOL_SHA256,
        dataset_id=DATASET_ID,
        dataset_role=REQUIRED_DATASET_ROLE,
        source_raw_sha256=source_raw_sha256,
        source_size_bytes=source_size_bytes,
        source_row_count=len(bars),
        first_timestamp_utc=bars[0].timestamp_utc,
        last_timestamp_utc=bars[-1].timestamp_utc,
        counters=counters,
        closed_trades=tuple(closed_trades),
        marked_equity_samples=tuple(marked_equity),
        screening=screening,
        open_position_at_end=position is not None,
        unrealized_pnl_at_end_usd=(
            marked_equity[-1].unrealized_pnl_usd if position is not None else Decimal("0.00")
        ),
        variant_id=variant_id,
        variant_protocol_sha256=variant_protocol_sha256,
    )


def run_preserved_development_replay(path: str | Path) -> DevelopmentReplayResult:
    """Verify and run the one private EXPOSED_DEVELOPMENT baseline replay."""
    dataset = load_preserved_development_raw(path)
    return _run_bars(
        dataset.bars,
        source_raw_sha256=dataset.source_raw_sha256,
        source_size_bytes=dataset.source_size_bytes,
    )


__all__ = [
    "BAR_INTERVAL",
    "EXPECTED_FIRST_TIMESTAMP_UTC",
    "EXPECTED_LAST_TIMESTAMP_UTC",
    "EXPECTED_RAW_ROW_COUNT",
    "EXPECTED_RAW_SIZE_BYTES",
    "NORMAL_INTRABAR_STOP_TIMESTAMP_POLICY",
    "OPEN_FILL_TIMESTAMP_POLICY",
    "RAW_TIMESTAMP_FORMAT",
    "RUNNER_ID",
    "RUNNER_VERSION",
    "DevelopmentReplayBar",
    "DevelopmentReplayCounters",
    "DevelopmentReplayError",
    "DevelopmentReplayResult",
    "VerifiedDevelopmentDataset",
    "load_preserved_development_raw",
    "parse_ninjatrader_last_rows",
    "run_preserved_development_replay",
]
