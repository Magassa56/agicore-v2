"""Strict chronological train/validation/OOS breakout replay."""
from __future__ import annotations

import hashlib
import math
from pathlib import Path

from .breakout_replay import BreakoutReplayConfig, BreakoutReplayError, calculate_breakout_metrics, replay_breakout
from .breakout_execution_costs import BreakoutExecutionCostModel
from .local_bundle import LocalBundleError, deterministic_json, publish_local_bundle, sha256_file
from .market_replay import OHLCVBar, load_ohlcv_csv


class TemporalBreakoutOOSError(ValueError):
    """Raised when a strict temporal breakout study cannot be created."""


def create_temporal_breakout_oos_study(csv_path, output_dir, *, lookback_bars=240, round_trip_cost_points=1.0, side_policy="BOTH", train_ratio=0.6, validation_ratio=0.2, oos_ratio=0.2, execution_cost_model: BreakoutExecutionCostModel | None = None) -> Path:
    """Publish three independent, chronological breakout replays without selection."""
    try:
        config = BreakoutReplayConfig(lookback_bars, round_trip_cost_points, side_policy=side_policy, execution_cost_model=execution_cost_model)
        ratios = (train_ratio, validation_ratio, oos_ratio)
        if any(not math.isfinite(value) or value <= 0 for value in ratios) or not math.isclose(sum(ratios), 1.0, rel_tol=0.0, abs_tol=1e-12):
            raise TemporalBreakoutOOSError("train, validation, and oos ratios must be positive and sum to 1.0")
        source, final_dir = Path(csv_path).resolve(), Path(output_dir).resolve()
        if not source.is_file(): raise TemporalBreakoutOOSError(f"OHLCV CSV file not found: {source}")
        if final_dir.exists(): raise TemporalBreakoutOOSError(f"Output directory already exists: {final_dir}")
        bars = tuple(load_ohlcv_csv(source)); segments = _split(bars, ratios, config.lookback_bars)
        input_hash = sha256_file(source)
        configuration = _configuration(config, {"lookback_bars":config.lookback_bars,"side_policy":config.side_policy,"ratios":{"train":train_ratio,"validation":validation_ratio,"oos":oos_ratio},"execution":"next_bar_open","fixed_configuration":True,"oos_used_for_selection":False})
        rows = [_segment_row(name, start, segment, config, input_hash) for name, start, segment in segments]
        run_hash = hashlib.sha256(deterministic_json({"input_sha256":input_hash,"configuration":configuration}).encode("utf-8")).hexdigest()
        summary = {"schema_version":"1.1","configuration":configuration,"segments":rows,"temporal_contract":{"ordered":["train","validation","oos"],"disjoint":True,"each_starts_flat":True,"warmup_crosses_boundaries":False,"oos_used_for_selection":False,"segment_boundary_index_basis":"source_global","trade_and_decision_index_basis":"segment_local"}}
        manifest = {"schema_version":"1.1","run_id":f"breakout-temporal-oos-{run_hash[:16]}","input_filename":source.name,"input_sha256":input_hash,"configuration":configuration,"configuration_sha256":hashlib.sha256(deterministic_json(configuration).encode("utf-8")).hexdigest(),"status":"completed","generated_files":["manifest.json","results.json","summary.json"],"warnings":["segments are chronological, disjoint, and independently replayed from FLAT","open positions are closed with END_OF_DATA at each segment boundary","no automatic comparison or optimization is performed","the nine existing contracts are development data and are not an independent holdout"]}
        return publish_local_bundle(final_dir,{"summary.json":deterministic_json(summary),"results.json":deterministic_json(rows),"manifest.json":deterministic_json(manifest)})
    except (BreakoutReplayError, LocalBundleError, OSError, ValueError) as exc:
        if isinstance(exc, TemporalBreakoutOOSError): raise
        raise TemporalBreakoutOOSError(str(exc)) from exc


def _split(bars: tuple[OHLCVBar, ...], ratios, lookback):
    train_count, validation_count = int(len(bars)*ratios[0]), int(len(bars)*ratios[1])
    groups = (("train",0,bars[:train_count]),("validation",train_count,bars[train_count:train_count+validation_count]),("oos",train_count+validation_count,bars[train_count+validation_count:]))
    if any(not group[2] for group in groups): raise TemporalBreakoutOOSError("train, validation, and oos segments must all be non-empty")
    if any(len(group[2]) < lookback + 1 for group in groups): raise TemporalBreakoutOOSError(f"Each segment requires at least {lookback + 1} OHLCV bars")
    return groups


def _segment_row(name, start, bars, config, input_hash):
    replay = replay_breakout(bars, config); trades = replay["trades"]
    return {"segment":name,"source_sha256":input_hash,"segment_sha256":hashlib.sha256(deterministic_json([_bar(bar) for bar in bars]).encode("utf-8")).hexdigest(),"source_start_index":start,"source_end_index":start+len(bars)-1,"start_timestamp":bars[0].timestamp.isoformat(),"end_timestamp":bars[-1].timestamp.isoformat(),"bar_count":len(bars),"starts_flat":True,"local_lookback_warmup_bar_count":config.lookback_bars,"cross_boundary_warmup_bar_count":0,"boundary_forced_close_count":sum(trade.exit_reason=="END_OF_DATA" for trade in trades),"cost_mode":"detailed" if config.execution_cost_model else "legacy_all_in","effective_round_trip_cost_points":config.effective_round_trip_cost_points,"cost_breakdown":config.execution_cost_model.serialize() if config.execution_cost_model else {"cost_mode":"legacy_all_in","legacy_round_trip_cost_points":config.round_trip_cost_points,"total_round_trip_cost_points":config.round_trip_cost_points},"metrics":calculate_breakout_metrics(trades),"trades":[_trade(trade,config) for trade in trades],"decisions":replay["decisions"]}


def _bar(bar): return {"timestamp":bar.timestamp.isoformat(),"open":bar.open,"high":bar.high,"low":bar.low,"close":bar.close,"volume":bar.volume}
def _configuration(config, values):
    values.update({"round_trip_cost_points":config.round_trip_cost_points,"effective_round_trip_cost_points":config.effective_round_trip_cost_points,"cost_mode":"detailed" if config.execution_cost_model else "legacy_all_in"})
    if config.execution_cost_model: values["execution_cost_model"]=config.execution_cost_model.serialize()
    return values
def _trade(trade,config): return {"side":trade.side,"entry_timestamp":trade.entry_timestamp.isoformat(),"entry_price":trade.entry_price,"exit_timestamp":trade.exit_timestamp.isoformat(),"exit_price":trade.exit_price,"entry_bar_index":trade.entry_bar_index,"exit_bar_index":trade.exit_bar_index,"exit_reason":trade.exit_reason,"cost_points":trade.cost_points,"gross_pnl_points":trade.gross_pnl_points,"net_pnl_points":trade.net_pnl_points,"cost_breakdown":config.execution_cost_model.serialize() if config.execution_cost_model else {"cost_mode":"legacy_all_in","legacy_round_trip_cost_points":config.round_trip_cost_points,"total_round_trip_cost_points":config.round_trip_cost_points}}


__all__ = ["TemporalBreakoutOOSError", "create_temporal_breakout_oos_study"]
