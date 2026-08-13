from __future__ import annotations
import json
from datetime import datetime, timedelta
import pytest
from agicore.cli.main import main
from agicore.trading.temporal_breakout_oos import TemporalBreakoutOOSError, create_temporal_breakout_oos_study

def _csv(path, count=60, future_offset=0):
    start=datetime(2026,8,1); rows=["timestamp,open,high,low,close,volume"]
    for index in range(count):
        value=100 if index%3<2 else 102
        if index>=48: value+=future_offset
        rows.append(f"{(start+timedelta(minutes=index)).isoformat(sep=' ')},{value},{value+1},{value-1},{value},1")
    path.write_text("\n".join(rows),encoding="utf-8")

def test_temporal_oos_bundle_is_chronological_deterministic_and_boundary_flat(tmp_path):
    source=tmp_path/"bars.csv"; _csv(source)
    one=create_temporal_breakout_oos_study(source,tmp_path/"one",lookback_bars=2,round_trip_cost_points=0.5,side_policy="LONG_ONLY")
    two=create_temporal_breakout_oos_study(source,tmp_path/"two",lookback_bars=2,round_trip_cost_points=0.5,side_policy="LONG_ONLY")
    changed_config=create_temporal_breakout_oos_study(source,tmp_path/"changed-config",lookback_bars=2,round_trip_cost_points=0.5,side_policy="BOTH")
    rows=json.loads((one/"results.json").read_text()); summary=json.loads((one/"summary.json").read_text()); manifest=json.loads((one/"manifest.json").read_text())
    assert (one/"results.json").read_text()==(two/"results.json").read_text() and manifest["run_id"]==json.loads((two/"manifest.json").read_text())["run_id"]
    assert manifest["run_id"]!=json.loads((changed_config/"manifest.json").read_text())["run_id"]
    assert [row["segment"] for row in rows]==["train","validation","oos"] and [row["bar_count"] for row in rows]==[36,12,12]
    assert [(row["source_start_index"],row["source_end_index"]) for row in rows]==[(0,35),(36,47),(48,59)]
    assert all(row["starts_flat"] and row["local_lookback_warmup_bar_count"]==2 and row["cross_boundary_warmup_bar_count"]==0 and row["boundary_forced_close_count"]>=1 for row in rows)
    assert rows[0]["source_end_index"]+1==rows[1]["source_start_index"] and rows[1]["source_end_index"]+1==rows[2]["source_start_index"]
    assert rows[0]["end_timestamp"]<rows[1]["start_timestamp"]<rows[2]["start_timestamp"]
    assert summary["temporal_contract"]=={"ordered":["train","validation","oos"],"disjoint":True,"each_starts_flat":True,"warmup_crosses_boundaries":False,"oos_used_for_selection":False,"segment_boundary_index_basis":"source_global","trade_and_decision_index_basis":"segment_local"}
    assert all(row["source_sha256"]==manifest["input_sha256"] for row in rows)
    assert summary["configuration"]=={"lookback_bars":2,"round_trip_cost_points":0.5,"effective_round_trip_cost_points":0.5,"cost_mode":"legacy_all_in","side_policy":"LONG_ONLY","ratios":{"train":0.6,"validation":0.2,"oos":0.2},"execution":"next_bar_open","fixed_configuration":True,"oos_used_for_selection":False}
    assert all(row["trades"] and all(trade["gross_pnl_points"]-trade["cost_points"]==trade["net_pnl_points"] for trade in row["trades"]) for row in rows)
    assert set(manifest["generated_files"])=={"manifest.json","results.json","summary.json"} and all((one/name).is_file() for name in manifest["generated_files"])
    assert not any(word in json.dumps({"summary":summary,"manifest":manifest}).lower() for word in ("winner","best","ranking","selected","recommended"))

def test_temporal_oos_prefix_is_unchanged_by_future_oos_mutation_and_errors_are_controlled(tmp_path):
    baseline,changed=tmp_path/"baseline.csv",tmp_path/"changed.csv"; _csv(baseline); _csv(changed,future_offset=500)
    left=create_temporal_breakout_oos_study(baseline,tmp_path/"left",lookback_bars=2)
    right=create_temporal_breakout_oos_study(changed,tmp_path/"right",lookback_bars=2)
    left_rows=json.loads((left/"results.json").read_text()); right_rows=json.loads((right/"results.json").read_text())
    assert json.loads((left/"manifest.json").read_text())["run_id"]!=json.loads((right/"manifest.json").read_text())["run_id"]
    assert [row["segment_sha256"] for row in left_rows[:2]]==[row["segment_sha256"] for row in right_rows[:2]] and left_rows[2]["segment_sha256"]!=right_rows[2]["segment_sha256"]
    fields=("segment_sha256","source_start_index","source_end_index","start_timestamp","end_timestamp","bar_count","boundary_forced_close_count","metrics","trades","decisions")
    for segment in (0,1): assert {key:left_rows[segment][key] for key in fields}=={key:right_rows[segment][key] for key in fields}
    short=tmp_path/"short.csv"; _csv(short,count=8)
    with pytest.raises(TemporalBreakoutOOSError): create_temporal_breakout_oos_study(short,tmp_path/"short",lookback_bars=2)
    with pytest.raises(TemporalBreakoutOOSError,match="ratios"): create_temporal_breakout_oos_study(baseline,tmp_path/"bad",lookback_bars=2,train_ratio=.7,validation_ratio=.2,oos_ratio=.2)
    assert main(["trading","study-breakout-temporal-oos",str(baseline),"--output-dir",str(tmp_path/"cli"),"--lookback-bars","2"])==0
