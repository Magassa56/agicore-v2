"""Deterministic offline OHLCV replay for a next-bar EMA crossover strategy."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from .local_bundle import LocalBundleError, deterministic_json, publish_local_bundle, sha256_file

_WARNINGS = [
    "retrospective historical simulation",
    "no proof of future profitability",
    "no commissions or slippage",
    "results expressed in points, not currency",
]


class MarketReplayError(ValueError):
    """Raised for an invalid local market replay request."""


@dataclass(frozen=True)
class OHLCVBar:
    """One validated market bar in chronological replay order."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class MarketReplayConfig:
    """Configuration for the fixed-size EMA crossover strategy."""

    fast_ema: int = 19
    slow_ema: int = 50

    def __post_init__(self) -> None:
        if self.fast_ema < 1:
            raise ValueError("fast_ema must be at least 1")
        if self.slow_ema < 2:
            raise ValueError("slow_ema must be at least 2")
        if self.fast_ema >= self.slow_ema:
            raise ValueError("fast_ema must be less than slow_ema")


@dataclass(frozen=True)
class ReplayTrade:
    """A closed one-unit simulated position, expressed only in points."""

    side: str
    entry_timestamp: datetime
    entry_price: float
    exit_timestamp: datetime
    exit_price: float
    entry_bar_index: int
    exit_bar_index: int
    exit_reason: str

    @property
    def pnl_points(self) -> float:
        return self.exit_price - self.entry_price if self.side == "LONG" else self.entry_price - self.exit_price


@dataclass(frozen=True)
class MarketReplayResult:
    """Completed historical replay including its closed trade ledger."""

    bars: tuple[OHLCVBar, ...]
    config: MarketReplayConfig
    trades: tuple[ReplayTrade, ...]


def load_ohlcv_csv(path: str | Path) -> list[OHLCVBar]:
    """Read, validate, de-duplicate and chronologically sort an explicit OHLCV CSV."""
    csv_path = Path(path)
    try:
        with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            sample = handle.read(4096)
            handle.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=",;\t") if sample else csv.excel
            except csv.Error:
                dialect = csv.excel
            reader = csv.DictReader(handle, dialect=dialect)
            if not reader.fieldnames:
                raise MarketReplayError("OHLCV CSV is missing a header row")
            columns = _columns(reader.fieldnames)
            missing = [name for name in ("timestamp", "open", "high", "low", "close", "volume") if name not in columns]
            if missing:
                raise MarketReplayError(f"OHLCV CSV missing required column(s): {', '.join(missing)}")
            bars = [_parse_row(row, columns, number) for number, row in enumerate(reader, start=2)]
    except MarketReplayError:
        raise
    except (OSError, csv.Error) as exc:
        raise MarketReplayError(f"Unable to read OHLCV CSV: {exc}") from exc
    if not bars:
        raise MarketReplayError("OHLCV CSV contains no bars")
    bars.sort(key=lambda bar: bar.timestamp)
    if any(first.timestamp == second.timestamp for first, second in zip(bars, bars[1:])):
        raise MarketReplayError("OHLCV CSV contains duplicate timestamps")
    return bars


def calculate_ema(closes: list[float], window: int) -> list[float]:
    """Calculate EMA seeded with the first close, using alpha=2/(window+1)."""
    if window < 1:
        raise ValueError("EMA window must be at least 1")
    if not closes:
        return []
    alpha = 2.0 / (window + 1)
    values = [closes[0]]
    for close in closes[1:]:
        values.append(alpha * close + (1.0 - alpha) * values[-1])
    return values


def replay_ema_crossover(bars: list[OHLCVBar], config: MarketReplayConfig) -> MarketReplayResult:
    """Replay EMA decisions at each close and execute them only at next opens."""
    if len(bars) < config.slow_ema + 1:
        raise MarketReplayError(f"At least {config.slow_ema + 1} OHLCV bars are required")
    ordered = tuple(sorted(bars, key=lambda bar: bar.timestamp))
    closes = [bar.close for bar in ordered]
    fast_values = calculate_ema(closes, config.fast_ema)
    slow_values = calculate_ema(closes, config.slow_ema)
    position: tuple[str, datetime, float, int] | None = None
    pending_side: str | None = None
    trades: list[ReplayTrade] = []

    for index, bar in enumerate(ordered):
        if pending_side is not None:
            if position is not None:
                trades.append(_close_trade(position, bar, index, "SIGNAL_REVERSAL"))
            position = (pending_side, bar.timestamp, bar.open, index)
            pending_side = None

        if index == len(ordered) - 1 or index < config.slow_ema - 1:
            continue
        desired = _desired_side(fast_values[index], slow_values[index], position[0] if position else "FLAT")
        current_side = position[0] if position else "FLAT"
        if desired != current_side:
            pending_side = desired

    if position is not None:
        last_index = len(ordered) - 1
        trades.append(_close_trade(position, ordered[-1], last_index, "END_OF_DATA", price=ordered[-1].close))
    return MarketReplayResult(ordered, config, tuple(trades))


def create_market_replay(
    csv_path: str | Path, output_dir: str | Path, config: MarketReplayConfig
) -> Path:
    """Create an atomic deterministic four-file bundle for an explicit OHLCV CSV."""
    input_path = Path(csv_path).resolve()
    if not input_path.exists():
        raise MarketReplayError(f"OHLCV CSV file not found: {input_path}")
    if not input_path.is_file():
        raise MarketReplayError(f"OHLCV CSV path is not a file: {input_path}")
    final_dir = Path(output_dir).resolve()
    if final_dir.exists():
        raise MarketReplayError(f"Output directory already exists: {final_dir}")
    try:
        input_sha256 = sha256_file(input_path)
        result = replay_ema_crossover(load_ohlcv_csv(input_path), config)
        return publish_local_bundle(final_dir, _bundle_files(input_path.name, input_sha256, result))
    except MarketReplayError:
        raise
    except (LocalBundleError, OSError, ValueError) as exc:
        raise MarketReplayError(str(exc)) from exc


def _columns(headers: list[str]) -> dict[str, str]:
    return {header.strip().lower(): header for header in headers}


def _parse_row(row: dict[str, str | None], columns: dict[str, str], number: int) -> OHLCVBar:
    try:
        timestamp = datetime.fromisoformat(_value(row, columns["timestamp"]).replace("Z", "+00:00"))
        values = {name: float(_value(row, columns[name])) for name in ("open", "high", "low", "close", "volume")}
    except (TypeError, ValueError) as exc:
        raise MarketReplayError(f"Invalid OHLCV value on CSV row {number}") from exc
    if not all(math.isfinite(value) for value in values.values()):
        raise MarketReplayError(f"Non-finite OHLCV value on CSV row {number}")
    if any(values[name] <= 0 for name in ("open", "high", "low", "close")) or values["volume"] < 0:
        raise MarketReplayError(f"Invalid OHLCV range on CSV row {number}")
    if values["high"] < max(values["open"], values["close"], values["low"]) or values["low"] > min(values["open"], values["close"], values["high"]):
        raise MarketReplayError(f"Inconsistent OHLC values on CSV row {number}")
    return OHLCVBar(timestamp=timestamp, **values)


def _value(row: dict[str, str | None], column: str) -> str:
    value = row.get(column)
    if value is None or not value.strip():
        raise ValueError("missing value")
    return value.strip()


def _desired_side(fast: float, slow: float, current: str) -> str:
    if fast > slow:
        return "LONG"
    if fast < slow:
        return "SHORT"
    return current


def _close_trade(
    position: tuple[str, datetime, float, int],
    bar: OHLCVBar,
    index: int,
    reason: str,
    *,
    price: float | None = None,
) -> ReplayTrade:
    side, entry_timestamp, entry_price, entry_index = position
    return ReplayTrade(side, entry_timestamp, entry_price, bar.timestamp, bar.open if price is None else price, entry_index, index, reason)


def _bundle_files(input_filename: str, input_sha256: str, result: MarketReplayResult) -> dict[str, str]:
    summary = _summary(result)
    strategy = summary["strategy"]
    strategy_sha256 = hashlib.sha256(json.dumps(strategy, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    trades = [_trade_data(index + 1, trade) for index, trade in enumerate(result.trades)]
    return {
        "report.md": _report(input_filename, summary, trades),
        "summary.json": deterministic_json(summary),
        "trades.json": deterministic_json(trades),
        "manifest.json": deterministic_json({
            "schema_version": "1.0",
            "run_id": f"market-replay-{input_sha256[:12]}-{strategy_sha256[:8]}",
            "input_filename": input_filename,
            "input_sha256": input_sha256,
            "strategy_sha256": strategy_sha256,
            "agicore_version": _agicore_version(),
            "status": "completed",
            "generated_files": ["manifest.json", "report.md", "summary.json", "trades.json"],
            "warnings": _WARNINGS,
        }),
    }


def _summary(result: MarketReplayResult) -> dict[str, object]:
    pnls = [trade.pnl_points for trade in result.trades]
    wins = [pnl for pnl in pnls if pnl > 0]
    losses = [pnl for pnl in pnls if pnl < 0]
    gross_profit = sum(wins)
    gross_loss = sum(losses)
    equity = 0.0
    peak = 0.0
    drawdown = 0.0
    for pnl in pnls:
        equity += pnl
        peak = max(peak, equity)
        drawdown = max(drawdown, peak - equity)
    return {
        "schema_version": "1.0",
        "strategy": {"name": "EMA_CROSSOVER", "fast_ema": result.config.fast_ema, "slow_ema": result.config.slow_ema, "execution": "next_bar_open", "position_size": 1},
        "market_data": {"bar_count": len(result.bars), "first_timestamp": result.bars[0].timestamp.isoformat(), "last_timestamp": result.bars[-1].timestamp.isoformat()},
        "performance": {"total_trades": len(pnls), "winning_trades": len(wins), "losing_trades": len(losses), "win_rate": len(wins) / len(pnls) if pnls else 0.0, "total_pnl_points": sum(pnls), "average_trade_points": sum(pnls) / len(pnls) if pnls else 0.0, "largest_gain_points": max(pnls, default=0.0), "largest_loss_points": min(pnls, default=0.0), "gross_profit_points": gross_profit, "gross_loss_points": gross_loss, "profit_factor": gross_profit / abs(gross_loss) if gross_loss else None, "max_closed_equity_drawdown_points": drawdown},
    }


def _trade_data(index: int, trade: ReplayTrade) -> dict[str, object]:
    return {"trade_index": index, "side": trade.side, "entry_timestamp": trade.entry_timestamp.isoformat(), "entry_price": trade.entry_price, "exit_timestamp": trade.exit_timestamp.isoformat(), "exit_price": trade.exit_price, "pnl_points": trade.pnl_points, "entry_bar_index": trade.entry_bar_index, "exit_bar_index": trade.exit_bar_index, "exit_reason": trade.exit_reason}


def _report(input_filename: str, summary: dict[str, object], trades: list[dict[str, object]]) -> str:
    strategy = summary["strategy"]
    market = summary["market_data"]
    performance = summary["performance"]
    assert isinstance(strategy, dict) and isinstance(market, dict) and isinstance(performance, dict)
    best = sorted(trades, key=lambda trade: float(trade["pnl_points"]), reverse=True)[:5]
    worst = sorted(trades, key=lambda trade: float(trade["pnl_points"]))[:5]
    profit_factor = performance["profit_factor"]
    profit_factor_text = "n/a" if profit_factor is None else f"{profit_factor:.2f}"
    best_lines = [_trade_line(trade) for trade in best] or ["- No trades"]
    worst_lines = [_trade_line(trade) for trade in worst] or ["- No trades"]
    lines = [
        "# Historical Market Replay",
        "",
        *[f"> Warning: {warning}" for warning in _WARNINGS],
        "",
        "## Input",
        "",
        f"- File: {input_filename}",
        f"- Period: {market['first_timestamp']} to {market['last_timestamp']}",
        f"- Bars: {market['bar_count']}",
        "",
        "## Strategy",
        "",
        f"- EMA crossover: {strategy['fast_ema']} / {strategy['slow_ema']}",
        "- Execution: next-bar-open",
        "- Position size: 1",
        "",
        "## Performance",
        "",
        f"- Total trades: {performance['total_trades']}",
        f"- Total PnL points: {performance['total_pnl_points']:.2f}",
        f"- Win rate: {performance['win_rate']:.2%}",
        f"- Profit factor: {profit_factor_text}",
        f"- Closed equity drawdown points: {performance['max_closed_equity_drawdown_points']:.2f}",
        "",
        "## Five Best Trades",
        "",
        *best_lines,
        "",
        "## Five Worst Trades",
        "",
        *worst_lines,
        "",
        "## Descriptive Conclusion",
        "",
        "This retrospective result describes this supplied historical dataset only.",
        "",
    ]
    return "\n".join(lines)


def _trade_line(trade: dict[str, object]) -> str:
    return f"- #{trade['trade_index']} {trade['side']}: {trade['pnl_points']:.2f} points"


def _agicore_version() -> str:
    try:
        return version("agicore")
    except PackageNotFoundError:
        return "unknown"


__all__ = ["MarketReplayConfig", "MarketReplayError", "MarketReplayResult", "OHLCVBar", "ReplayTrade", "calculate_ema", "create_market_replay", "load_ohlcv_csv", "replay_ema_crossover"]
