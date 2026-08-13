"""Offline expanding-window walk-forward breakout evaluation."""
from __future__ import annotations
import hashlib
from pathlib import Path
from .breakout_replay import BreakoutReplayConfig, BreakoutReplayError, calculate_breakout_metrics, replay_breakout
from .breakout_execution_costs import BreakoutExecutionCostModel
from .local_bundle import LocalBundleError, deterministic_json, publish_local_bundle, sha256_file
from .market_replay import load_ohlcv_csv

class WalkForwardBreakoutError(ValueError): pass

def create_walk_forward_breakout_study(csv_path, output_dir, *, initial_train_bars, validation_bars, oos_bars, lookback_bars=240, round_trip_cost_points=1.0, side_policy="BOTH", execution_cost_model: BreakoutExecutionCostModel | None = None):
    try:
        if any(not isinstance(x,int) or x<=0 for x in (initial_train_bars,validation_bars,oos_bars)): raise WalkForwardBreakoutError("initial_train_bars, validation_bars, and oos_bars must be positive integers")
        config=BreakoutReplayConfig(lookback_bars,round_trip_cost_points,side_policy=side_policy,execution_cost_model=execution_cost_model); source,final=Path(csv_path).resolve(),Path(output_dir).resolve()
        if not source.is_file(): raise WalkForwardBreakoutError(f"OHLCV CSV file not found: {source}")
        if final.exists(): raise WalkForwardBreakoutError(f"Output directory already exists: {final}")
        bars=tuple(load_ohlcv_csv(source)); size=validation_bars+oos_bars
        if initial_train_bars+size>len(bars): raise WalkForwardBreakoutError("Source has no complete walk-forward fold")
        input_hash=sha256_file(source); rows=[]; fold=0
        while initial_train_bars+(fold+1)*size<=len(bars):
            train_end=initial_train_bars+fold*size; blocks=(("train",0,train_end),("validation",train_end,train_end+validation_bars),("oos",train_end+validation_bars,train_end+size))
            for role,start,end in blocks:
                segment=bars[start:end]
                if len(segment)<lookback_bars+1: raise WalkForwardBreakoutError(f"Fold {fold} {role} requires at least {lookback_bars+1} bars")
                replay=replay_breakout(segment,config); trades=replay["trades"]
                rows.append({"fold_index":fold,"role":role,"source_sha256":input_hash,"segment_sha256":hashlib.sha256(deterministic_json([_bar(x) for x in segment]).encode()).hexdigest(),"source_start_index":start,"source_end_index":end-1,"start_timestamp":segment[0].timestamp.isoformat(),"end_timestamp":segment[-1].timestamp.isoformat(),"bar_count":len(segment),"starts_flat":True,"local_lookback_warmup_bar_count":lookback_bars,"cross_boundary_warmup_bar_count":0,"boundary_forced_close_count":sum(x.exit_reason=="END_OF_DATA" for x in trades),"metrics":calculate_breakout_metrics(trades),"cost_mode":"detailed" if execution_cost_model else "legacy_all_in","effective_round_trip_cost_points":config.effective_round_trip_cost_points,"cost_breakdown":config.execution_cost_model.serialize() if config.execution_cost_model else {"cost_mode":"legacy_all_in","legacy_round_trip_cost_points":config.round_trip_cost_points,"total_round_trip_cost_points":config.round_trip_cost_points},"trades":[_trade(x,config) for x in trades],"decisions":replay["decisions"]})
            fold+=1
        excluded=len(bars)-(initial_train_bars+fold*size); cfg={"initial_train_bars":initial_train_bars,"validation_bars":validation_bars,"oos_bars":oos_bars,"lookback_bars":lookback_bars,"round_trip_cost_points":round_trip_cost_points,"effective_round_trip_cost_points":config.effective_round_trip_cost_points,"cost_mode":"detailed" if execution_cost_model else "legacy_all_in","side_policy":side_policy,"mode":"expanding","execution":"next_bar_open","fixed_configuration":True};
        if execution_cost_model: cfg["execution_cost_model"]=execution_cost_model.serialize()
        rh=hashlib.sha256(deterministic_json({"input_sha256":input_hash,"configuration":cfg}).encode()).hexdigest()
        summary={"schema_version":"1.1","configuration":cfg,"complete_fold_count":fold,"excluded_final_bar_count":excluded,"by_role":{role:_aggregate([x for x in rows if x["role"]==role]) for role in ("train","validation","oos")},"temporal_contract":{"train_expands_from_source_index":0,"validation_oos_blocks_do_not_overlap":True,"segment_boundary_index_basis":"source_global","trade_and_decision_index_basis":"segment_local","oos_used_for_selection":False}}
        manifest={"schema_version":"1.1","run_id":f"breakout-walk-forward-{rh[:16]}","input_filename":source.name,"input_sha256":input_hash,"configuration":cfg,"configuration_sha256":hashlib.sha256(deterministic_json(cfg).encode()).hexdigest(),"excluded_final_bar_count":excluded,"status":"completed","generated_files":["manifest.json","results.json","summary.json"],"warnings":["expanding windows reuse completed historical validation and OOS periods only as later train history","each segment starts FLAT and closes open positions with END_OF_DATA","no automatic parameter changes are performed","the nine existing contracts are development data and are not an independent holdout"]}
        return publish_local_bundle(final,{"results.json":deterministic_json(rows),"summary.json":deterministic_json(summary),"manifest.json":deterministic_json(manifest)})
    except (BreakoutReplayError,LocalBundleError,OSError,ValueError) as exc:
        if isinstance(exc,WalkForwardBreakoutError): raise
        raise WalkForwardBreakoutError(str(exc)) from exc
def _bar(x): return {"timestamp":x.timestamp.isoformat(),"open":x.open,"high":x.high,"low":x.low,"close":x.close,"volume":x.volume}
def _trade(x,config): return {"side":x.side,"entry_timestamp":x.entry_timestamp.isoformat(),"entry_price":x.entry_price,"exit_timestamp":x.exit_timestamp.isoformat(),"exit_price":x.exit_price,"entry_bar_index":x.entry_bar_index,"exit_bar_index":x.exit_bar_index,"exit_reason":x.exit_reason,"cost_points":x.cost_points,"gross_pnl_points":x.gross_pnl_points,"net_pnl_points":x.net_pnl_points,"cost_breakdown":config.execution_cost_model.serialize() if config.execution_cost_model else {"cost_mode":"legacy_all_in","legacy_round_trip_cost_points":config.round_trip_cost_points,"total_round_trip_cost_points":config.round_trip_cost_points}}
def _aggregate(rows): return {"segment_count":len(rows),"total_trades":sum(x["metrics"]["total_trades"] for x in rows),"gross_total_pnl_points":sum(x["metrics"]["gross_total_pnl_points"] for x in rows),"net_total_pnl_points":sum(x["metrics"]["net_total_pnl_points"] for x in rows),"boundary_forced_close_count":sum(x["boundary_forced_close_count"] for x in rows)}
__all__=["WalkForwardBreakoutError","create_walk_forward_breakout_study"]
