from __future__ import annotations
import json
from datetime import datetime, timedelta
import pytest
from agicore.trading.multitimeframe_breakout_study import TIMEFRAMES, MultiTimeframeStudyError, create_multitimeframe_breakout_study

def _csv(path, offset=0, count=270, missing_minutes=(), delimiter=","):
    start=datetime(2026,8,1,0,0); rows=[delimiter.join(("timestamp","open","high","low","close","volume"))]
    for i in range(count):
        if i in missing_minutes: continue
        value=100+offset+(i%20)
        rows.append(delimiter.join((f"{(start+timedelta(minutes=i)).isoformat(sep=' ')}",str(value),str(value+1),str(value-1),str(value),"1")))
    path.write_text("\n".join(rows),encoding="utf-8")

def _breakout_csv(path, mode):
    start=datetime(2026,8,1); rows=["timestamp,open,high,low,close,volume"]
    for i in range(270):
        if mode=="LONG": value=100 if i<240 else 102
        elif mode=="SHORT": value=100 if i<240 else 98
        else: value=100 if i<240 else 102 if i<242 else 98
        rows.append(f"{(start+timedelta(minutes=i)).isoformat(sep=' ')},{value},{value+1},{value-1},{value},1")
    path.write_text("\n".join(rows),encoding="utf-8")

def test_study_has_all_pre_registered_timeframes_and_is_deterministic(tmp_path):
    a,b=tmp_path/"a.csv",tmp_path/"b.csv"; _csv(a); _csv(b,10)
    one=create_multitimeframe_breakout_study([b,a],tmp_path/"one",1.0); two=create_multitimeframe_breakout_study([a,b],tmp_path/"two",1.0)
    results=json.loads((one/"results.json").read_text()); summary=json.loads((one/"summary.json").read_text())
    assert TIMEFRAMES=={1:240,5:48,15:16,30:8}; assert {x["timeframe_minutes"] for x in results}==set(TIMEFRAMES)
    assert "best_timeframe" not in summary and "winner" not in summary
    assert (one/"results.json").read_text()==(two/"results.json").read_text()

def test_study_rejects_duplicate_basename_and_negative_cost(tmp_path):
    a=tmp_path/"a.csv"; _csv(a)
    with pytest.raises(MultiTimeframeStudyError): create_multitimeframe_breakout_study([a],tmp_path/"x",-1)
    with pytest.raises(MultiTimeframeStudyError): create_multitimeframe_breakout_study([],tmp_path/"y",1)

def test_study_accepts_semicolon_ohlcv_input(tmp_path):
    source=tmp_path/"semicolon.csv"; _csv(source,delimiter=";")
    bundle=create_multitimeframe_breakout_study([source],tmp_path/"bundle",1.0)
    assert json.loads((bundle/"results.json").read_text())

def test_study_reports_resampler_manifest_metrics_and_real_drawdown(tmp_path):
    source=tmp_path/"gapped.csv"
    start=datetime(2026,8,1); rows=["timestamp,open,high,low,close,volume"]
    for i in range(300):
        if i == 2: continue
        value=100 if i<240 else 102 if i<242 else 98 if i<244 else 104 if i<246 else 106
        rows.append(f"{(start+timedelta(minutes=i)).isoformat(sep=' ')},{value},{value+1},{value-1},{value},1")
    source.write_text("\n".join(rows),encoding="utf-8")
    bundle=create_multitimeframe_breakout_study([source],tmp_path/"bundle",0.0)
    results=json.loads((bundle/"results.json").read_text())
    by_timeframe={row["timeframe_minutes"]:row for row in results}
    assert by_timeframe[1]["dropped_incomplete_bucket_count"]==0
    assert by_timeframe[1]["resampled_bar_count"]==299
    for timeframe, expected_bars in ((5,59),(15,19),(30,9)):
        assert by_timeframe[timeframe]["dropped_incomplete_bucket_count"]==1
        assert by_timeframe[timeframe]["resampled_bar_count"]==expected_bars
    assert by_timeframe[1]["net_closed_equity_drawdown_points"]==6
    assert by_timeframe[1]["net_closed_equity_drawdown_points"]>0

def test_long_trade_is_attributed_with_full_empty_short_schema(tmp_path):
    source=tmp_path/"long.csv"; _breakout_csv(source,"LONG")
    bundle=create_multitimeframe_breakout_study([source],tmp_path/"bundle",0.5)
    row=next(item for item in json.loads((bundle/"results.json").read_text()) if item["timeframe_minutes"]==1)
    long,short=row["by_side"]["LONG"],row["by_side"]["SHORT"]
    assert row["total_trades"]==long["total_trades"]==1 and short["total_trades"]==0
    assert row["boundary_forced_close_count"]==long["boundary_forced_close_count"]==1 and short["boundary_forced_close_count"]==0
    assert long["gross_total_pnl_points"]-long["net_total_pnl_points"]==0.5
    assert long["gross_total_pnl_points"]==row["gross_total_pnl_points"] and long["net_total_pnl_points"]==row["net_total_pnl_points"]
    assert short["net_profit_factor"] is None and short["largest_net_gain_points"]==short["largest_net_loss_points"]==0.0

def test_short_trade_is_attributed_with_empty_long_schema(tmp_path):
    source=tmp_path/"short.csv"; _breakout_csv(source,"SHORT")
    bundle=create_multitimeframe_breakout_study([source],tmp_path/"bundle",0.5)
    row=next(item for item in json.loads((bundle/"results.json").read_text()) if item["timeframe_minutes"]==1)
    long,short=row["by_side"]["LONG"],row["by_side"]["SHORT"]
    assert row["total_trades"]==short["total_trades"]==1 and long["total_trades"]==0
    assert row["boundary_forced_close_count"]==short["boundary_forced_close_count"]==1 and long["boundary_forced_close_count"]==0
    assert short["gross_total_pnl_points"]-short["net_total_pnl_points"]==0.5
    assert short["net_total_pnl_points"]==row["net_total_pnl_points"]

def test_mixed_sides_reconcile_rows_and_timeframe_aggregate(tmp_path):
    source=tmp_path/"mixed.csv"; _breakout_csv(source,"MIXED")
    bundle=create_multitimeframe_breakout_study([source],tmp_path/"bundle",0.5)
    results=json.loads((bundle/"results.json").read_text()); summary=json.loads((bundle/"summary.json").read_text()); manifest=json.loads((bundle/"manifest.json").read_text())
    row=next(item for item in results if item["timeframe_minutes"]==1); long,short=row["by_side"]["LONG"],row["by_side"]["SHORT"]
    assert row["total_trades"]==long["total_trades"]+short["total_trades"]==2
    assert row["gross_total_pnl_points"]==long["gross_total_pnl_points"]+short["gross_total_pnl_points"]
    assert row["net_total_pnl_points"]==long["net_total_pnl_points"]+short["net_total_pnl_points"]
    assert row["boundary_forced_close_count"]==long["boundary_forced_close_count"]+short["boundary_forced_close_count"]==1
    aggregate=summary["by_timeframe"]["1"]
    assert aggregate["total_trades"]==aggregate["by_side"]["LONG"]["total_trades"]+aggregate["by_side"]["SHORT"]["total_trades"]
    assert aggregate["gross_total_pnl_points"]==aggregate["by_side"]["LONG"]["gross_total_pnl_points"]+aggregate["by_side"]["SHORT"]["gross_total_pnl_points"]
    assert aggregate["net_total_pnl_points"]==aggregate["by_side"]["LONG"]["net_total_pnl_points"]+aggregate["by_side"]["SHORT"]["net_total_pnl_points"]
    assert aggregate["boundary_forced_close_count"]==aggregate["by_side"]["LONG"]["boundary_forced_close_count"]+aggregate["by_side"]["SHORT"]["boundary_forced_close_count"]
    assert summary["schema_version"]==manifest["schema_version"]=="1.1"
    expected_policy={"input_order":"canonical input_filename ascending","path_dependent_metrics_are_descriptive":True,"not_a_rollover_adjusted_continuous_equity_curve":True}
    assert summary["multi_source_aggregation"]==manifest["multi_source_aggregation"]==expected_policy
    assert any("rollover-adjusted continuous equity curve" in warning for warning in manifest["warnings"])
    assert "best" not in json.dumps({"summary":summary,"results":results}).lower()
