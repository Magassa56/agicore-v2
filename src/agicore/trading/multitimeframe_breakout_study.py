"""Deterministic offline multi-timeframe causal breakout study."""
from __future__ import annotations
import hashlib, json, math, shutil, tempfile
from pathlib import Path
from .breakout_replay import BreakoutReplayConfig, BreakoutReplayError, calculate_breakout_metrics, replay_breakout
from .local_bundle import LocalBundleError, deterministic_json, publish_local_bundle, sha256_file
from .market_replay import load_ohlcv_csv
from .ohlcv_resampler import OHLCVResamplerError, resample_ohlcv

TIMEFRAMES={1:240,5:48,15:16,30:8}
class MultiTimeframeStudyError(ValueError): pass
def create_multitimeframe_breakout_study(csv_paths, output_dir, round_trip_cost_points=1.0):
    if round_trip_cost_points < 0: raise MultiTimeframeStudyError("round_trip_cost_points must be greater than or equal to 0")
    paths=sorted((Path(p).resolve() for p in csv_paths),key=lambda p:p.name)
    if not paths: raise MultiTimeframeStudyError("At least one CSV is required")
    if len({p.name for p in paths}) != len(paths): raise MultiTimeframeStudyError("Input CSV basenames must be unique")
    if any(not p.is_file() for p in paths): raise MultiTimeframeStudyError("Input CSV file not found")
    final=Path(output_dir).resolve()
    if final.exists(): raise MultiTimeframeStudyError(f"Output directory already exists: {final}")
    scratch=Path(tempfile.mkdtemp(prefix="agicore-study-"))
    try:
        rows=[]; source_hashes={}; trades_by_timeframe={timeframe:[] for timeframe in TIMEFRAMES}
        for source in paths:
            source_bars=tuple(load_ohlcv_csv(source))
            source_hash=sha256_file(source)
            source_hashes[source]=source_hash
            for timeframe,lookback in TIMEFRAMES.items():
                target=source if timeframe==1 else scratch/f"{source.stem}-{timeframe}.csv"
                if timeframe!=1: resample_ohlcv(source,target,timeframe)
                bars=source_bars if timeframe==1 else tuple(load_ohlcv_csv(target)); replay=replay_breakout(bars,BreakoutReplayConfig(lookback,round_trip_cost_points)); trades=replay["trades"]
                metrics=calculate_breakout_metrics(trades); boundary_forced_close_count=sum(t.exit_reason=="END_OF_DATA" for t in trades)
                by_side={side:{**calculate_breakout_metrics(tuple(t for t in trades if t.side==side)),"boundary_forced_close_count":sum(t.side==side and t.exit_reason=="END_OF_DATA" for t in trades)} for side in ("LONG","SHORT")}
                _verify_side_reconciliation(metrics,by_side,boundary_forced_close_count); longs=[t for t in trades if t.side=="LONG"]; shorts=[t for t in trades if t.side=="SHORT"]; trades_by_timeframe[timeframe].extend(trades)
                if timeframe==1: dropped=0
                else:
                    resample_manifest=json.loads(target.with_name(target.name+".manifest.json").read_text(encoding="utf-8"))
                    if resample_manifest["output_bar_count"] != len(bars): raise MultiTimeframeStudyError("Resampler manifest output_bar_count does not match loaded bars")
                    dropped=resample_manifest["dropped_incomplete_bucket_count"]
                rows.append({"input_filename":source.name,"input_sha256":source_hash,"timeframe_minutes":timeframe,"lookback_bars":lookback,"input_bar_count":len(source_bars),"resampled_bar_count":len(bars),"dropped_incomplete_bucket_count":dropped,"boundary_forced_close_count":boundary_forced_close_count,"by_side":by_side,"total_trades":metrics["total_trades"],"gross_total_pnl_points":metrics["gross_total_pnl_points"],"net_total_pnl_points":metrics["net_total_pnl_points"],"net_profit_factor":metrics["net_profit_factor"],"net_average_trade_points":metrics["net_average_trade_points"],"net_closed_equity_drawdown_points":metrics["net_closed_equity_drawdown_points"],"long_trades":len(longs),"long_net_pnl_points":sum(t.net_pnl_points for t in longs),"short_trades":len(shorts),"short_net_pnl_points":sum(t.net_pnl_points for t in shorts),"first_market_timestamp":bars[0].timestamp.isoformat(),"last_market_timestamp":bars[-1].timestamp.isoformat(),"run_id":hashlib.sha256(f"{source_hash}:{timeframe}:{lookback}:{round_trip_cost_points}".encode()).hexdigest()[:20]})
        config={"timeframes":TIMEFRAMES,"round_trip_cost_points":round_trip_cost_points}; run=hashlib.sha256(json.dumps({"inputs":[source_hashes[p] for p in paths],**config},sort_keys=True).encode()).hexdigest()
        aggregation_policy={"input_order":"canonical input_filename ascending","path_dependent_metrics_are_descriptive":True,"not_a_rollover_adjusted_continuous_equity_curve":True}
        summary={"schema_version":"1.1","configuration":config,"multi_source_aggregation":aggregation_policy,"by_timeframe":{str(tf):_timeframe_aggregate((r for r in rows if r["timeframe_minutes"]==tf),tuple(trades_by_timeframe[tf])) for tf in TIMEFRAMES}}
        manifest={"schema_version":"1.1","run_id":f"multitimeframe-{run[:16]}","input_filenames":[p.name for p in paths],"multi_source_aggregation":aggregation_policy,"status":"completed","generated_files":["manifest.json","report.md","results.json","summary.json"],"warnings":["descriptive multi-timeframe study; no automatic selection or optimization","multi-source metrics are path-dependent descriptive aggregates, not a rollover-adjusted continuous equity curve"]}
        report="# Multi-Timeframe Breakout Study\n\n"+"\n".join(["- Offline descriptive study; no timeframe is selected automatically.",f"- Inputs: {', '.join(p.name for p in paths)}",f"- Cost: {round_trip_cost_points:.2f}"])+"\n"
        return publish_local_bundle(final,{"report.md":report,"summary.json":deterministic_json(summary),"results.json":deterministic_json(rows),"manifest.json":deterministic_json(manifest)})
    except (BreakoutReplayError,OHLCVResamplerError,LocalBundleError,ValueError) as exc: raise MultiTimeframeStudyError(str(exc)) from exc
    finally: shutil.rmtree(scratch,ignore_errors=True)

def _timeframe_aggregate(rows,trades):
    values=tuple(rows); metrics=calculate_breakout_metrics(trades); boundary_forced_close_count=sum(t.exit_reason=="END_OF_DATA" for t in trades)
    by_side={side:{**calculate_breakout_metrics(tuple(t for t in trades if t.side==side)),"boundary_forced_close_count":sum(t.side==side and t.exit_reason=="END_OF_DATA" for t in trades)} for side in ("LONG","SHORT")}
    _verify_side_reconciliation(metrics,by_side,boundary_forced_close_count)
    return {"contract_count":len(values),"total_trades":metrics["total_trades"],"gross_total_pnl_points":metrics["gross_total_pnl_points"],"net_total_pnl_points":metrics["net_total_pnl_points"],"boundary_forced_close_count":boundary_forced_close_count,"by_side":by_side}

def _verify_side_reconciliation(metrics,by_side,boundary_forced_close_count):
    if metrics["total_trades"] != by_side["LONG"]["total_trades"]+by_side["SHORT"]["total_trades"]: raise MultiTimeframeStudyError("Directional trade counts do not reconcile")
    if not math.isclose(metrics["gross_total_pnl_points"],by_side["LONG"]["gross_total_pnl_points"]+by_side["SHORT"]["gross_total_pnl_points"],rel_tol=1e-12,abs_tol=1e-9): raise MultiTimeframeStudyError("Directional gross PnL does not reconcile")
    if not math.isclose(metrics["net_total_pnl_points"],by_side["LONG"]["net_total_pnl_points"]+by_side["SHORT"]["net_total_pnl_points"],rel_tol=1e-12,abs_tol=1e-9): raise MultiTimeframeStudyError("Directional net PnL does not reconcile")
    if boundary_forced_close_count != by_side["LONG"]["boundary_forced_close_count"]+by_side["SHORT"]["boundary_forced_close_count"]: raise MultiTimeframeStudyError("Directional boundary forced-close counts do not reconcile")
__all__=["TIMEFRAMES","MultiTimeframeStudyError","create_multitimeframe_breakout_study"]
