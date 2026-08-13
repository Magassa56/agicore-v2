from datetime import datetime, timedelta
import json
from pathlib import Path
from agicore.trading.breakout_execution_costs import BreakoutExecutionCostModel
from agicore.trading.multitimeframe_breakout_study import create_multitimeframe_breakout_study
from agicore.trading.multitimeframe_breakout_stability import create_multitimeframe_breakout_stability_study
from agicore.trading.temporal_breakout_oos import create_temporal_breakout_oos_study
from agicore.trading.walk_forward_breakout import create_walk_forward_breakout_study

def _model(entry=.125, exit=.125): return BreakoutExecutionCostModel("nominal","MNQ","USD",2,.5,.25,entry,exit)
def _csv(path, count=600):
    start=datetime(2024,1,1)
    path.write_text("timestamp,open,high,low,close,volume\n"+"\n".join(f"{start+timedelta(minutes=i)},{100 if i<240 else 102 if i%4<2 else 98},{101 if i<240 else 103 if i%4<2 else 99},{99 if i<240 else 101 if i%4<2 else 97},{100 if i<240 else 102 if i%4<2 else 98},1" for i in range(count)),encoding="utf-8")
def _assert_bundle(bundle):
    results=json.loads((bundle/"results.json").read_text()); summary=json.loads((bundle/"summary.json").read_text()); manifest=json.loads((bundle/"manifest.json").read_text())
    rows=results if isinstance(results,list) else results["segments"]
    assert summary["configuration"]["cost_mode"]=="detailed" and summary["configuration"]["effective_round_trip_cost_points"]==1
    assert summary["configuration"]["execution_cost_model"]["instrument"]=="MNQ"
    assert manifest["configuration"]==summary["configuration"] and manifest["configuration_sha256"]
    assert all(row["cost_mode"]=="detailed" and row["effective_round_trip_cost_points"]==1 and row["cost_breakdown"]["total_round_trip_cost_points"]==1 for row in rows)
    trades=[trade for row in rows for trade in row.get("trades",[])]
    assert trades and any(trade["exit_reason"]=="END_OF_DATA" for trade in trades)
    assert all(trade["cost_breakdown"]["cost_mode"]=="detailed" and trade["gross_pnl_points"]-trade["cost_points"]==trade["net_pnl_points"] for trade in trades)
    return manifest, rows
def test_detailed_cost_propagates_to_four_facades_and_identity_changes(tmp_path):
    source=tmp_path/"bars.csv"; _csv(source)
    calls=(
        lambda out, model: create_multitimeframe_breakout_study([source],out,0,execution_cost_model=model),
        lambda out, model: create_multitimeframe_breakout_stability_study([source],out,round_trip_cost_points=0,window_bars=300,execution_cost_model=model),
        lambda out, model: create_temporal_breakout_oos_study(source,out,lookback_bars=2,round_trip_cost_points=0,execution_cost_model=model),
        lambda out, model: create_walk_forward_breakout_study(source,out,initial_train_bars=40,validation_bars=20,oos_bars=20,lookback_bars=2,round_trip_cost_points=0,execution_cost_model=model),
    )
    for index, call in enumerate(calls):
        one=call(tmp_path/f"one-{index}",_model()); two=call(tmp_path/f"two-{index}",_model(.1,.15)); first, rows=_assert_bundle(one); second, other_rows=_assert_bundle(two)
        assert first["run_id"] != second["run_id"] and first["configuration_sha256"] != second["configuration_sha256"]
        assert sum(len(row.get("trades",[])) for row in rows)==sum(len(row.get("trades",[])) for row in other_rows)>0
        assert [row.get("decisions",[]) for row in rows]==[row.get("decisions",[]) for row in other_rows]

def test_reports_publish_complete_detailed_and_legacy_cost_contracts(tmp_path):
    source=tmp_path/"bars.csv"; _csv(source)
    detail=_model()
    for name,call in (("multi",lambda out,cost:create_multitimeframe_breakout_study([source],out,0,execution_cost_model=cost)),("stability",lambda out,cost:create_multitimeframe_breakout_stability_study([source],out,round_trip_cost_points=0,window_bars=300,execution_cost_model=cost))):
        detailed=call(tmp_path/(name+"-d"),detail); legacy=call(tmp_path/(name+"-l"),None)
        text=(detailed/"report.md").read_text(); legacy_text=(legacy/"report.md").read_text()
        assert all(str(detail.serialize()[key]) in text for key in ("scenario_name","instrument","currency","point_value_currency_per_point","commission_currency_per_side","commission_round_trip_currency","commission_round_trip_points","round_trip_spread_points","entry_slippage_points","exit_slippage_points","total_round_trip_cost_points"))
        assert "legacy_all_in" in legacy_text and "Total round-trip cost points" in legacy_text
