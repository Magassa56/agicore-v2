"""Deterministic chronological stability study for the causal breakout replay."""
from __future__ import annotations

import hashlib
import json
import math
import shutil
import tempfile
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from .breakout_replay import BreakoutReplayConfig, BreakoutReplayError, calculate_breakout_metrics, replay_breakout
from .breakout_execution_costs import BreakoutExecutionCostModel
from .local_bundle import LocalBundleError, deterministic_json, publish_local_bundle, sha256_file
from .market_replay import OHLCVBar, load_ohlcv_csv
from .multitimeframe_breakout_study import TIMEFRAMES
from .ohlcv_resampler import OHLCVResamplerError, resample_ohlcv


class MultiTimeframeStabilityError(ValueError):
    """Raised for an invalid chronological breakout stability study."""


def create_multitimeframe_breakout_stability_study(csv_paths, output_dir, *, round_trip_cost_points=1.0, window_bars: int, execution_cost_model: BreakoutExecutionCostModel | None = None) -> Path:
    """Evaluate independent, complete source-bar windows in canonical order."""
    if window_bars <= 0:
        raise MultiTimeframeStabilityError("window_bars must be strictly positive")
    if round_trip_cost_points < 0:
        raise MultiTimeframeStabilityError("round_trip_cost_points must be greater than or equal to 0")
    paths = sorted((Path(path).resolve() for path in csv_paths), key=lambda path: path.name)
    if not paths:
        raise MultiTimeframeStabilityError("At least one CSV is required")
    if len({path.name for path in paths}) != len(paths):
        raise MultiTimeframeStabilityError("Input CSV basenames must be unique")
    if any(not path.is_file() for path in paths):
        raise MultiTimeframeStabilityError("Input CSV file not found")
    final_dir = Path(output_dir).resolve()
    if final_dir.exists():
        raise MultiTimeframeStabilityError(f"Output directory already exists: {final_dir}")

    scratch = Path(tempfile.mkdtemp(prefix="agicore-breakout-stability-"))
    try:
        rows = []
        input_hashes = {}
        dropped_windows = {}
        for source in paths:
            source_bars = tuple(load_ohlcv_csv(source))
            complete_count, remainder = divmod(len(source_bars), window_bars)
            if complete_count < 2:
                raise MultiTimeframeStabilityError("At least two complete chronological windows are required")
            input_hashes[source] = sha256_file(source)
            dropped_windows[source.name] = remainder
            for window_index in range(complete_count):
                window = source_bars[window_index * window_bars:(window_index + 1) * window_bars]
                window_path = scratch / f"{source.stem}-window-{window_index:06d}.csv"
                _write_window_csv(window_path, window)
                window_hash = sha256_file(window_path)
                for timeframe, lookback in TIMEFRAMES.items():
                    bars, dropped_buckets, manifest_hash = _window_bars(window_path, window, timeframe, scratch)
                    if len(bars) < lookback + 1:
                        raise MultiTimeframeStabilityError(
                            f"Window {window_index} timeframe {timeframe} has insufficient bars: "
                            f"requires at least {lookback + 1}, got {len(bars)}"
                        )
                    replay_config = BreakoutReplayConfig(lookback, round_trip_cost_points, execution_cost_model=execution_cost_model)
                    trades = replay_breakout(bars, replay_config)["trades"]
                    metrics = calculate_breakout_metrics(trades)
                    boundary_forced_close_count = sum(trade.exit_reason == "END_OF_DATA" for trade in trades)
                    by_side = {
                        side: {
                            **calculate_breakout_metrics(tuple(trade for trade in trades if trade.side == side)),
                            "boundary_forced_close_count": sum(trade.side == side and trade.exit_reason == "END_OF_DATA" for trade in trades),
                        }
                        for side in ("LONG", "SHORT")
                    }
                    _verify_side_reconciliation(metrics, by_side, boundary_forced_close_count)
                    rows.append({
                        "input_filename": source.name,
                        "input_sha256": input_hashes[source],
                        "window_input_sha256": window_hash,
                        "window_index": window_index,
                        "source_start_timestamp": window[0].timestamp.isoformat(),
                        "source_end_timestamp": window[-1].timestamp.isoformat(),
                        "source_bar_count": len(window),
                        "timeframe_minutes": timeframe,
                        "lookback_bars": lookback,
                        "output_bar_count": len(bars),
                        "dropped_incomplete_bucket_count": dropped_buckets,
                        "resampler_manifest_sha256": manifest_hash,
                        "boundary_forced_close_count": boundary_forced_close_count,
                        "cost_mode": "detailed" if execution_cost_model else "legacy_all_in",
                        "effective_round_trip_cost_points": replay_config.effective_round_trip_cost_points,
                        "cost_breakdown": replay_config.execution_cost_model.serialize() if replay_config.execution_cost_model else {"cost_mode":"legacy_all_in","legacy_round_trip_cost_points":replay_config.round_trip_cost_points,"total_round_trip_cost_points":replay_config.round_trip_cost_points},
                        "trades": [_trade(trade, replay_config) for trade in trades],
                        "by_side": by_side,
                        **metrics,
                    })
        top_config = BreakoutReplayConfig(round_trip_cost_points=round_trip_cost_points, execution_cost_model=execution_cost_model)
        config = {"timeframes": TIMEFRAMES, "window_bars": window_bars, **_cost_config(top_config)}
        run_hash = hashlib.sha256(deterministic_json({"input_sha256": [input_hashes[path] for path in paths], "configuration": config}).encode("utf-8")).hexdigest()
        summary = {
            "schema_version": "1.2",
            "configuration": config,
            "dropped_incomplete_window_bar_count": dropped_windows,
            "by_timeframe": {
                str(timeframe): _timeframe_aggregate(row for row in rows if row["timeframe_minutes"] == timeframe)
                for timeframe in TIMEFRAMES
            },
        }
        manifest = {
            "schema_version": "1.2",
            "run_id": f"breakout-stability-{run_hash[:16]}",
            "input_filenames": [path.name for path in paths],
            "input_sha256": [input_hashes[path] for path in paths],
            "configuration_sha256": hashlib.sha256(deterministic_json(config).encode("utf-8")).hexdigest(),
            "configuration": config,
            "agicore_version": _version(),
            "status": "completed",
            "generated_files": ["manifest.json", "report.md", "results.json", "summary.json"],
            "warnings": [
                "chronological windows are disjoint and the final partial source window is excluded",
                "each window starts flat and uses no warm-up data from a previous window",
                "open positions are closed at the end of each window using END_OF_DATA behavior",
                "descriptive historical study; no timeframe is selected automatically",
            ],
        }
        report = _report(paths, summary, round_trip_cost_points, window_bars)
        return publish_local_bundle(final_dir, {"report.md": report, "summary.json": deterministic_json(summary), "results.json": deterministic_json(rows), "manifest.json": deterministic_json(manifest)})
    except (BreakoutReplayError, LocalBundleError, OHLCVResamplerError, OSError, ValueError) as exc:
        raise MultiTimeframeStabilityError(str(exc)) from exc
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def _window_bars(window_path: Path, source_window: tuple[OHLCVBar, ...], timeframe: int, scratch: Path):
    if timeframe == 1:
        return source_window, 0, None
    output = scratch / f"{window_path.stem}-{timeframe}.csv"
    resample_ohlcv(window_path, output, timeframe)
    bars = tuple(load_ohlcv_csv(output))
    manifest_path = output.with_name(f"{output.name}.manifest.json")
    manifest_text = manifest_path.read_text(encoding="utf-8")
    manifest = json.loads(manifest_text)
    if manifest["output_bar_count"] != len(bars):
        raise MultiTimeframeStabilityError("Resampler manifest output_bar_count does not match loaded bars")
    return bars, manifest["dropped_incomplete_bucket_count"], hashlib.sha256(manifest_text.encode("utf-8")).hexdigest()


def _write_window_csv(path: Path, bars: tuple[OHLCVBar, ...]) -> None:
    rows = ["timestamp,open,high,low,close,volume"]
    rows.extend(f"{bar.timestamp.isoformat(sep=' ')},{bar.open},{bar.high},{bar.low},{bar.close},{bar.volume}" for bar in bars)
    path.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")


def _aggregate(rows):
    values = tuple(rows)
    pnl = [row["net_total_pnl_points"] for row in values]
    return {
        "evaluated_window_count": len(values),
        "positive_window_count": sum(value > 0 for value in pnl),
        "negative_window_count": sum(value < 0 for value in pnl),
        "flat_window_count": sum(value == 0 for value in pnl),
        "worst_window_net_pnl_points": min(pnl) if pnl else None,
        "maximum_window_drawdown_points": max((row["net_closed_equity_drawdown_points"] for row in values), default=None),
        "total_trades": sum(row["total_trades"] for row in values),
        "net_total_pnl_points": sum(pnl),
    }


def _timeframe_aggregate(rows):
    values = tuple(rows)
    aggregate = _aggregate(values)
    aggregate["by_side"] = {
        side: _aggregate(row["by_side"][side] for row in values)
        for side in ("LONG", "SHORT")
    }
    return aggregate


def _verify_side_reconciliation(metrics, by_side, global_boundary_forced_close_count) -> None:
    if metrics["total_trades"] != by_side["LONG"]["total_trades"] + by_side["SHORT"]["total_trades"]:
        raise MultiTimeframeStabilityError("Directional trade counts do not reconcile")
    if not math.isclose(
        metrics["net_total_pnl_points"],
        by_side["LONG"]["net_total_pnl_points"] + by_side["SHORT"]["net_total_pnl_points"],
        rel_tol=1e-12,
        abs_tol=1e-9,
    ):
        raise MultiTimeframeStabilityError("Directional net PnL does not reconcile")
    if global_boundary_forced_close_count != (
        by_side["LONG"]["boundary_forced_close_count"] + by_side["SHORT"]["boundary_forced_close_count"]
    ):
        raise MultiTimeframeStabilityError("Directional boundary forced-close counts do not reconcile")


def _report(paths, summary, cost, window_bars) -> str:
    config=summary["configuration"]
    lines = ["# Multi-Timeframe Chronological Breakout Stability Study", "", "- Offline, descriptive historical study; no timeframe is selected automatically.", f"- Inputs: {', '.join(path.name for path in paths)}", f"- Source window bars: {window_bars}", *_cost_report_lines(config), "- Windows are complete, disjoint, chronological, and start FLAT.", "- No prior-window warm-up is used; open positions close with END_OF_DATA at each boundary.", ""]
    for timeframe, aggregate in summary["by_timeframe"].items():
        lines.append(f"- {timeframe}m: windows={aggregate['evaluated_window_count']}, positive={aggregate['positive_window_count']}, negative={aggregate['negative_window_count']}, flat={aggregate['flat_window_count']}, worst_net_pnl={aggregate['worst_window_net_pnl_points']}, max_drawdown={aggregate['maximum_window_drawdown_points']}")
    return "\n".join(lines) + "\n"


def _version() -> str:
    try:
        return version("agicore")
    except PackageNotFoundError:
        return "unknown"

def _cost_config(config):
    row={"round_trip_cost_points":config.round_trip_cost_points,"effective_round_trip_cost_points":config.effective_round_trip_cost_points,"cost_mode":"detailed" if config.execution_cost_model else "legacy_all_in"}
    if config.execution_cost_model: row["execution_cost_model"]=config.execution_cost_model.serialize()
    return row
def _trade(trade,config): return {"side":trade.side,"entry_timestamp":trade.entry_timestamp.isoformat(),"entry_price":trade.entry_price,"exit_timestamp":trade.exit_timestamp.isoformat(),"exit_price":trade.exit_price,"entry_bar_index":trade.entry_bar_index,"exit_bar_index":trade.exit_bar_index,"exit_reason":trade.exit_reason,"gross_pnl_points":trade.gross_pnl_points,"cost_points":trade.cost_points,"net_pnl_points":trade.net_pnl_points,"cost_breakdown":config.execution_cost_model.serialize() if config.execution_cost_model else {"cost_mode":"legacy_all_in","legacy_round_trip_cost_points":config.round_trip_cost_points,"total_round_trip_cost_points":config.round_trip_cost_points}}
def _cost_report_lines(config):
    detail=config.get("execution_cost_model")
    if not detail: return ["- Cost mode: legacy_all_in",f"- Legacy round-trip cost points: {config['round_trip_cost_points']}",f"- Total round-trip cost points: {config['effective_round_trip_cost_points']}"]
    return [f"- Cost mode: {config['cost_mode']}",*[f"- {name}: {detail[name]}" for name in ("scenario_name","instrument","currency","point_value_currency_per_point","commission_currency_per_side","commission_round_trip_currency","commission_round_trip_points","round_trip_spread_points","entry_slippage_points","exit_slippage_points","total_round_trip_cost_points")]]


__all__ = ["MultiTimeframeStabilityError", "create_multitimeframe_breakout_stability_study"]
