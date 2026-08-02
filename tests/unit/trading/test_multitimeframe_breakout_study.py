from __future__ import annotations
import json
from datetime import datetime, timedelta
import pytest
from agicore.trading.multitimeframe_breakout_study import TIMEFRAMES, MultiTimeframeStudyError, create_multitimeframe_breakout_study

def _csv(path, offset=0, count=270, missing_minutes=()):
    start=datetime(2026,8,1,0,0); rows=["timestamp,open,high,low,close,volume"]
    for i in range(count):
        if i in missing_minutes: continue
        value=100+offset+(i%20)
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
