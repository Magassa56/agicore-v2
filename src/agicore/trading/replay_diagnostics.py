"""Deterministic, descriptive offline diagnostics for market replay results."""
from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from .local_bundle import LocalBundleError, deterministic_json, publish_local_bundle, sha256_file
from .market_replay import MarketReplayConfig, MarketReplayError, OHLCVBar, ReplayTrade, load_ohlcv_csv, replay_ema_crossover

_CLOCK_BLOCKS = (("00-05", range(0, 6)), ("06-11", range(6, 12)), ("12-17", range(12, 18)), ("18-23", range(18, 24)))
_WARNINGS = [
    "input timestamps are interpreted exactly as supplied",
    "timezone is unknown unless established outside this diagnostic",
    "volatility regime thresholds are calculated retrospectively on the complete sample and are not a directly deployable rule",
    "retrospective historical diagnostic; no proof of future profitability",
]


class ReplayDiagnosticsError(ValueError):
    """Raised for an invalid replay diagnostics request."""


@dataclass(frozen=True)
class ReplayDiagnosticsConfig:
    """Fixed descriptive settings layered on top of a market replay config."""

    rolling_window_trades: int = 100
    atr_window_bars: int = 20

    def __post_init__(self) -> None:
        if self.rolling_window_trades < 2:
            raise ValueError("rolling_window_trades must be at least 2")


def create_replay_diagnostics(
    csv_path: str | Path,
    output_dir: str | Path,
    strategy_config: MarketReplayConfig,
    diagnostics_config: ReplayDiagnosticsConfig,
) -> Path:
    """Replay explicit OHLCV data and atomically publish a diagnostic bundle."""
    input_path = Path(csv_path).resolve()
    if not input_path.exists():
        raise ReplayDiagnosticsError(f"OHLCV CSV file not found: {input_path}")
    if not input_path.is_file():
        raise ReplayDiagnosticsError(f"OHLCV CSV path is not a file: {input_path}")
    final_dir = Path(output_dir).resolve()
    if final_dir.exists():
        raise ReplayDiagnosticsError(f"Output directory already exists: {final_dir}")
    try:
        bars = load_ohlcv_csv(input_path)
        replay = replay_ema_crossover(bars, strategy_config)
        if diagnostics_config.rolling_window_trades > len(replay.trades):
            raise ReplayDiagnosticsError("rolling_window_trades must not exceed the number of closed trades")
        payload = diagnose_replay(replay.bars, replay.trades, strategy_config, diagnostics_config)
        return publish_local_bundle(final_dir, _bundle_files(input_path.name, sha256_file(input_path), payload))
    except ReplayDiagnosticsError:
        raise
    except (MarketReplayError, LocalBundleError, OSError, ValueError) as exc:
        raise ReplayDiagnosticsError(str(exc)) from exc


def diagnose_replay(
    bars: tuple[OHLCVBar, ...],
    trades: tuple[ReplayTrade, ...],
    strategy_config: MarketReplayConfig,
    diagnostics_config: ReplayDiagnosticsConfig,
) -> dict[str, object]:
    """Build descriptive breakdowns, concentration and rolling diagnostics."""
    ordered = tuple(sorted(trades, key=lambda trade: (trade.exit_timestamp, trade.entry_timestamp)))
    if diagnostics_config.rolling_window_trades > len(ordered):
        raise ReplayDiagnosticsError("rolling_window_trades must not exceed the number of closed trades")
    atrs = _pre_entry_atrs(bars, ordered, diagnostics_config.atr_window_bars)
    thresholds = (_percentile(atrs, 1 / 3), _percentile(atrs, 2 / 3))
    enriched = list(zip(ordered, atrs, strict=True))
    breakdowns = {
        "by_side": _group_metrics({side: [item for item in enriched if item[0].side == side] for side in ("LONG", "SHORT")}),
        "by_entry_month": _group_metrics(_group(enriched, lambda item: item[0].entry_timestamp.strftime("%Y-%m"))),
        "by_entry_iso_week": _group_metrics(_group(enriched, lambda item: f"{item[0].entry_timestamp.isocalendar().year}-W{item[0].entry_timestamp.isocalendar().week:02d}")),
        "by_entry_hour": _group_metrics({f"{hour:02d}": [item for item in enriched if item[0].entry_timestamp.hour == hour] for hour in range(24)}),
        "by_clock_block": _group_metrics({name: [item for item in enriched if item[0].entry_timestamp.hour in hours] for name, hours in _CLOCK_BLOCKS}),
        "by_volatility_regime": _group_metrics({name: [item for item in enriched if _regime(item[1], thresholds) == name] for name in ("LOW", "MEDIUM", "HIGH")}),
    }
    rolling = _rolling(ordered, diagnostics_config.rolling_window_trades)
    performance = _metrics(ordered)
    return {
        "summary": {
            "schema_version": "1.0",
            "strategy": _strategy_data(strategy_config),
            "market_data": {"bar_count": len(bars), "first_timestamp": bars[0].timestamp.isoformat(), "last_timestamp": bars[-1].timestamp.isoformat()},
            "performance": performance,
            "atr_window_bars": diagnostics_config.atr_window_bars,
            "low_medium_threshold": thresholds[0],
            "medium_high_threshold": thresholds[1],
            "regime_method": "pre-entry true-range mean over up to the prior 20 bars; retrospective 33.333% and 66.667% thresholds",
            "volatility": {"atr_window_bars": diagnostics_config.atr_window_bars, "low_medium_threshold": thresholds[0], "medium_high_threshold": thresholds[1], "regime_method": "pre-entry true-range mean over up to the prior 20 bars; retrospective 33.333% and 66.667% thresholds"},
            "concentration": _concentration(ordered),
            "rolling_stability": _rolling_summary(rolling, diagnostics_config.rolling_window_trades),
        },
        "breakdowns": breakdowns,
        "rolling": rolling,
    }


def _pre_entry_atrs(bars: tuple[OHLCVBar, ...], trades: tuple[ReplayTrade, ...], window: int) -> list[float]:
    index_by_timestamp = {bar.timestamp: index for index, bar in enumerate(bars)}
    trs = [bar.high - bar.low for bar in bars]
    for index in range(1, len(bars)):
        previous = bars[index - 1].close
        bar = bars[index]
        trs[index] = max(bar.high - bar.low, abs(bar.high - previous), abs(bar.low - previous))
    values: list[float] = []
    for trade in trades:
        entry = index_by_timestamp[trade.entry_timestamp]
        available = trs[max(0, entry - window):entry]
        values.append(sum(available) / len(available) if available else 0.0)
    return values


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    position = (len(ordered) - 1) * fraction
    lower, upper = math.floor(position), math.ceil(position)
    return ordered[lower] if lower == upper else ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def _regime(value: float, thresholds: tuple[float, float]) -> str:
    return "LOW" if value <= thresholds[0] else "MEDIUM" if value <= thresholds[1] else "HIGH"


def _group(items, key):
    groups = defaultdict(list)
    for item in items:
        groups[key(item)].append(item)
    return {name: groups[name] for name in sorted(groups)}


def _group_metrics(groups) -> dict[str, dict[str, object]]:
    return {name: _metrics([item[0] for item in items]) for name, items in groups.items()}


def _metrics(trades: list[ReplayTrade] | tuple[ReplayTrade, ...]) -> dict[str, object]:
    gross = [trade.gross_pnl_points for trade in trades]
    net = [trade.net_pnl_points for trade in trades]
    positives = [pnl for pnl in gross if pnl > 0]
    losses = [pnl for pnl in gross if pnl < 0]
    net_positive = [pnl for pnl in net if pnl > 0]
    net_loss = [pnl for pnl in net if pnl < 0]
    return {"total_trades": len(trades), "winning_trades": sum(pnl > 0 for pnl in net), "losing_trades": sum(pnl < 0 for pnl in net), "breakeven_trades": sum(pnl == 0 for pnl in net), "win_rate": sum(pnl > 0 for pnl in net) / len(net) if net else 0.0, "gross_total_pnl_points": sum(gross), "net_total_pnl_points": sum(net), "gross_average_trade_points": sum(gross) / len(gross) if gross else 0.0, "net_average_trade_points": sum(net) / len(net) if net else 0.0, "gross_profit_factor": sum(positives) / abs(sum(losses)) if losses else None, "net_profit_factor": sum(net_positive) / abs(sum(net_loss)) if net_loss else None, "net_closed_equity_drawdown_points": _drawdown(net), "largest_net_gain_points": max(net, default=0.0), "largest_net_loss_points": min(net, default=0.0)}


def _drawdown(pnls: list[float]) -> float:
    equity = peak = drawdown = 0.0
    for pnl in pnls:
        equity += pnl
        peak = max(peak, equity)
        drawdown = max(drawdown, peak - equity)
    return drawdown


def _concentration(trades: tuple[ReplayTrade, ...]) -> dict[str, object]:
    net = sorted((trade.net_pnl_points for trade in trades), reverse=True)
    ascending = list(reversed(net))
    total = sum(net)
    positive = sum(pnl for pnl in net if pnl > 0)
    result = {"best_trade_net_pnl_points": net[0] if net else 0.0, "worst_trade_net_pnl_points": ascending[0] if ascending else 0.0}
    for count in (5, 10):
        result[f"best_{count}_trades_net_pnl_points"] = sum(net[:count])
        result[f"worst_{count}_trades_net_pnl_points"] = sum(ascending[:count])
    for count in (1, 5, 10):
        result[f"net_pnl_without_best_{count}"] = total - sum(net[:count])
        result[f"net_pnl_without_worst_{count}"] = total - sum(ascending[:count])
    for percent in (1, 5):
        count = max(1, math.ceil(len(net) * percent / 100))
        result[f"top_{percent}_percent_share_of_gross_positive_net_pnl"] = sum(pnl for pnl in net[:count] if pnl > 0) / positive if positive else None
    return result


def _rolling(trades: tuple[ReplayTrade, ...], window: int) -> list[dict[str, object]]:
    entries = []
    for start in range(len(trades) - window + 1):
        subset = trades[start:start + window]
        metrics = _metrics(subset)
        entries.append({"window_index": start + 1, "first_trade_index": start + 1, "last_trade_index": start + window, "first_entry_timestamp": subset[0].entry_timestamp.isoformat(), "last_exit_timestamp": subset[-1].exit_timestamp.isoformat(), **{key: metrics[key] for key in ("total_trades", "winning_trades", "losing_trades", "breakeven_trades", "win_rate", "gross_total_pnl_points", "net_total_pnl_points", "gross_profit_factor", "net_profit_factor", "net_closed_equity_drawdown_points")}})
    return entries


def _rolling_summary(rolling: list[dict[str, object]], window: int) -> dict[str, object]:
    net = [float(item["net_total_pnl_points"]) for item in rolling]
    factors = [
        float(item["net_profit_factor"])
        for item in rolling
        if item["net_profit_factor"] is not None
        and math.isfinite(float(item["net_profit_factor"]))
    ]
    return {"window_trades": window, "window_count": len(rolling), "profitable_window_count": sum(value > 0 for value in net), "losing_window_count": sum(value < 0 for value in net), "breakeven_window_count": sum(value == 0 for value in net), "profitable_window_rate": sum(value > 0 for value in net) / len(net) if net else 0.0, "best_window_net_pnl_points": max(net, default=0.0), "worst_window_net_pnl_points": min(net, default=0.0), "median_window_net_pnl_points": _percentile(net, 0.5), "best_window_net_profit_factor": max(factors) if factors else None, "worst_window_net_profit_factor": min(factors) if factors else None, "maximum_window_drawdown_points": max((float(item["net_closed_equity_drawdown_points"]) for item in rolling), default=0.0)}


def _strategy_data(config: MarketReplayConfig) -> dict[str, object]:
    return {"name": "EMA_CROSSOVER", "fast_ema": config.fast_ema, "slow_ema": config.slow_ema, "execution": "next_bar_open", "position_size": 1, "round_trip_cost_points": config.round_trip_cost_points}


def _bundle_files(input_filename: str, input_sha256: str, payload: dict[str, object]) -> dict[str, str]:
    summary = payload["summary"]
    assert isinstance(summary, dict)
    strategy_sha = _hash(summary["strategy"])
    diagnostics = {"rolling_window_trades": summary["rolling_stability"]["window_trades"], "atr_window_bars": summary["atr_window_bars"], "clock_blocks": [name for name, _ in _CLOCK_BLOCKS], "percentiles": [33.333, 66.667], "attribution_timestamp": "entry_timestamp"}
    diagnostics_sha = _hash(diagnostics)
    manifest = {"schema_version": "1.0", "run_id": f"replay-diagnostics-{input_sha256[:12]}-{strategy_sha[:8]}-{diagnostics_sha[:8]}", "input_filename": input_filename, "input_sha256": input_sha256, "strategy_sha256": strategy_sha, "diagnostics_sha256": diagnostics_sha, "agicore_version": _agicore_version(), "status": "completed", "generated_files": ["breakdowns.json", "manifest.json", "report.md", "rolling.json", "summary.json"], "warnings": _WARNINGS}
    return {"report.md": _report(input_filename, summary, payload["breakdowns"], payload["rolling"]), "summary.json": deterministic_json(summary), "breakdowns.json": deterministic_json(payload["breakdowns"]), "rolling.json": deterministic_json(payload["rolling"]), "manifest.json": deterministic_json(manifest)}


def _hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _report(input_filename, summary, breakdowns, rolling) -> str:
    performance, market, strategy = summary["performance"], summary["market_data"], summary["strategy"]
    def extremes(name):
        values = breakdowns[name]
        return (
            max(values, key=lambda key: values[key]["net_total_pnl_points"], default="n/a"),
            min(values, key=lambda key: values[key]["net_total_pnl_points"], default="n/a"),
        )

    best_month, worst_month = extremes("by_entry_month")
    best_week, worst_week = extremes("by_entry_iso_week")
    best_hour, worst_hour = extremes("by_entry_hour")
    best_block, worst_block = extremes("by_clock_block")
    rolling_summary = summary["rolling_stability"]
    concentration = summary["concentration"]
    lines = ["# Replay Diagnostics", "", *[f"> Warning: {warning}" for warning in _WARNINGS], "", f"- File: {input_filename}", f"- Period: {market['first_timestamp']} to {market['last_timestamp']}", f"- Bars: {market['bar_count']}", f"- EMA: {strategy['fast_ema']} / {strategy['slow_ema']}", f"- Cost per trade: {strategy['round_trip_cost_points']:.2f}", f"- Trades: {performance['total_trades']}", f"- Gross PnL: {performance['gross_total_pnl_points']:.2f}", f"- Net PnL: {performance['net_total_pnl_points']:.2f}", f"- Gross PF: {performance['gross_profit_factor']}", f"- Net PF: {performance['net_profit_factor']}", f"- Net drawdown: {performance['net_closed_equity_drawdown_points']:.2f}", "", "## Descriptive Highlights", "", f"- LONG net PnL: {breakdowns['by_side']['LONG']['net_total_pnl_points']:.2f}", f"- SHORT net PnL: {breakdowns['by_side']['SHORT']['net_total_pnl_points']:.2f}", f"- Best/worst month: {best_month} / {worst_month}", f"- Best/worst week: {best_week} / {worst_week}", f"- Best/worst hour: {best_hour} / {worst_hour}", f"- Best/worst clock block: {best_block} / {worst_block}", f"- Volatility LOW/MEDIUM/HIGH net PnL: {breakdowns['by_volatility_regime']['LOW']['net_total_pnl_points']:.2f} / {breakdowns['by_volatility_regime']['MEDIUM']['net_total_pnl_points']:.2f} / {breakdowns['by_volatility_regime']['HIGH']['net_total_pnl_points']:.2f}", f"- Best/worst rolling window net PnL: {rolling_summary['best_window_net_pnl_points']:.2f} / {rolling_summary['worst_window_net_pnl_points']:.2f}", f"- Profitable rolling window rate: {rolling_summary['profitable_window_rate']:.2%}", f"- Net PnL without best 1/5/10: {concentration['net_pnl_without_best_1']:.2f} / {concentration['net_pnl_without_best_5']:.2f} / {concentration['net_pnl_without_best_10']:.2f}", f"- This report is descriptive and does not predict future performance.", ""]
    return "\n".join(lines)


def _agicore_version() -> str:
    try:
        return version("agicore")
    except PackageNotFoundError:
        return "unknown"


__all__ = ["ReplayDiagnosticsConfig", "ReplayDiagnosticsError", "create_replay_diagnostics", "diagnose_replay"]
