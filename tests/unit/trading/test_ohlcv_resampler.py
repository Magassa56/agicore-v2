from __future__ import annotations
import json
from datetime import datetime, timedelta
import pytest
from agicore.cli.main import main
from agicore.trading.breakout_replay import BreakoutReplayConfig, replay_breakout
from agicore.trading.market_replay import load_ohlcv_csv
from agicore.trading.ohlcv_resampler import OHLCVResamplerError, resample_ohlcv

def _csv(path, count=30, gap=None):
    rows=["timestamp,open,high,low,close,volume"]
    for i in range(count):
        if i != gap: rows.append(f"2026-08-01 00:{i:02d}:00,{10+i},{11+i},{9+i},{10.5+i},1")
    path.write_text("\n".join(rows),encoding="utf-8")

def test_aggregate_complete_buckets_and_manifest(tmp_path):
    source=tmp_path/"input.csv"; _csv(source); output=tmp_path/"five.csv"; resample_ohlcv(source,output,5)
    lines=output.read_text().splitlines(); assert len(lines)==7; assert lines[1].startswith("2026-08-01 00:00:00;10.0;15.0;9.0;14.5;5.0")
    manifest=json.loads((tmp_path/"five.csv.manifest.json").read_text()); assert manifest["output_bar_count"]==6
    assert resample_ohlcv(source,tmp_path/"fifteen.csv",15); assert resample_ohlcv(source,tmp_path/"thirty.csv",30)

def test_incomplete_gap_errors_and_cli(tmp_path,capsys):
    source=tmp_path/"input.csv"; _csv(source,10,2); output=tmp_path/"out.csv"; resample_ohlcv(source,output,5)
    assert json.loads((tmp_path/"out.csv.manifest.json").read_text())["dropped_incomplete_bucket_count"]==1
    with pytest.raises(OHLCVResamplerError): resample_ohlcv(source,output,5)
    assert main(["trading","resample-ohlcv",str(source),"--output",str(tmp_path/"bad.csv"),"--minutes","4"])==2
    assert "5, 15, 30" in capsys.readouterr().err

def test_partial_bucket_mutation_does_not_change_published_buckets_or_breakout_replay(tmp_path):
    start=datetime(2026,8,1)
    def source(path,partial_values):
        values=[10]*10+[12]*10+partial_values
        rows=["timestamp,open,high,low,close,volume"]+[f"{(start+timedelta(minutes=index)).isoformat(sep=' ')},{value},{value+1},{value-1},{value},1" for index,value in enumerate(values)]
        path.write_text("\n".join(rows),encoding="utf-8")
    left_source,right_source=tmp_path/"left.csv",tmp_path/"right.csv"; source(left_source,[20,21]); source(right_source,[900,1])
    left_output,right_output=tmp_path/"left-5.csv",tmp_path/"right-5.csv"; resample_ohlcv(left_source,left_output,5); resample_ohlcv(right_source,right_output,5)
    left_manifest=json.loads((tmp_path/"left-5.csv.manifest.json").read_text()); right_manifest=json.loads((tmp_path/"right-5.csv.manifest.json").read_text())
    assert left_source.read_text()!=right_source.read_text() and left_manifest["input_sha256"]!=right_manifest["input_sha256"]
    assert (left_manifest["output_bar_count"],left_manifest["dropped_incomplete_bucket_count"])==(4,1)
    assert (right_manifest["output_bar_count"],right_manifest["dropped_incomplete_bucket_count"])==(4,1)
    left_text,right_text=left_output.read_text(),right_output.read_text()
    assert left_text and left_text==right_text and "00:20:00" not in left_text
    left_replay=replay_breakout(tuple(load_ohlcv_csv(left_output)),BreakoutReplayConfig(2,0.0))
    right_replay=replay_breakout(tuple(load_ohlcv_csv(right_output)),BreakoutReplayConfig(2,0.0))
    assert left_replay["decisions"] and left_replay["trades"]
    assert any(d["action"]=="ENTER_LONG" for d in left_replay["decisions"])
    assert any(t.side=="LONG" and t.entry_bar_index==3 and t.exit_reason=="END_OF_DATA" for t in left_replay["trades"])
    assert left_replay["decisions"]==right_replay["decisions"] and left_replay["trades"]==right_replay["trades"]

def test_semicolon_and_quoted_headers_match_comma_input(tmp_path):
    comma=tmp_path/"comma.csv"; _csv(comma,5)
    semicolon=tmp_path/"semicolon.csv"
    semicolon.write_text("\ufeff\"timestamp\";\"open\";\"high\";\"low\";\"close\";\"volume\"\n" + "\n".join(f"2026-08-01 00:0{i}:00;{10+i};{11+i};{9+i};{10.5+i};1" for i in range(5)),encoding="utf-8")
    comma_output, semicolon_output=tmp_path/"comma-out.csv",tmp_path/"semicolon-out.csv"
    resample_ohlcv(comma,comma_output,5); resample_ohlcv(semicolon,semicolon_output,5)
    comma_manifest=json.loads((tmp_path/"comma-out.csv.manifest.json").read_text())
    semicolon_manifest=json.loads((tmp_path/"semicolon-out.csv.manifest.json").read_text())
    assert comma_output.read_text()==semicolon_output.read_text()
    assert (comma_manifest["output_bar_count"],comma_manifest["dropped_incomplete_bucket_count"]) == (1,0)
    assert (semicolon_manifest["output_bar_count"],semicolon_manifest["dropped_incomplete_bucket_count"]) == (1,0)

def test_missing_columns_remain_an_explicit_error(tmp_path):
    source=tmp_path/"missing.csv"; source.write_text("timestamp;open;high;low;close\n2026-08-01 00:00:00;10;11;9;10\n",encoding="utf-8")
    with pytest.raises(OHLCVResamplerError,match="missing required columns"):
        resample_ohlcv(source,tmp_path/"out.csv",5)
