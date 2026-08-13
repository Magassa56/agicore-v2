from datetime import datetime, timedelta
import json
import pytest
from agicore.cli.main import main

COMMANDS=("study-breakout-timeframes","study-breakout-stability","study-breakout-temporal-oos","study-breakout-walk-forward")
def _csv(path):
    start=datetime(2026,1,1); rows=["timestamp,open,high,low,close,volume"]
    for i in range(600):
        value=100 if i<240 else 102 if i%4<2 else 98
        rows.append(f"{start+timedelta(minutes=i)},{value},{value+1},{value-1},{value},1")
    path.write_text("\n".join(rows),encoding="utf-8")
def _base(command,source,out):
    args=["trading",command,str(source),"--output-dir",str(out)]
    if command=="study-breakout-stability": args += ["--window-bars","300"]
    if command=="study-breakout-temporal-oos": args += ["--lookback-bars","2"]
    if command=="study-breakout-walk-forward": args += ["--initial-train-bars","300","--validation-bars","100","--oos-bars","100","--lookback-bars","2"]
    return args
def _detailed(entry="0.125",exit="0.125"):
    return ["--cost-scenario","nominal","--cost-instrument","MNQ","--cost-currency","USD","--point-value","2","--commission-per-side","0.5","--spread-points","0.25","--entry-slippage-points",entry,"--exit-slippage-points",exit]
def _artifacts(out): return [json.loads((out/name).read_text()) for name in ("results.json","summary.json","manifest.json")]
def _rows(results): return results if isinstance(results,list) else results["segments"]
def _trades(results): return [t for row in _rows(results) for t in row.get("trades",[])]

@pytest.mark.parametrize("command",COMMANDS)
def test_detailed_cost_cli_succeeds_and_publishes_auditable_artifacts(tmp_path,command):
    source=tmp_path/"bars.csv"; out=tmp_path/command; _csv(source)
    assert main(_base(command,source,out)+["--round-trip-cost-points","0"]+_detailed())==0
    results,summary,manifest=_artifacts(out); trades=_trades(results)
    assert summary["configuration"]["cost_mode"]=="detailed" and summary["configuration"]["effective_round_trip_cost_points"]==1
    assert summary["configuration"]["execution_cost_model"]["instrument"]=="MNQ" and manifest["run_id"]
    assert trades and any(t["exit_reason"]=="END_OF_DATA" for t in trades)
    assert all(t["cost_breakdown"]["cost_mode"]=="detailed" and t["gross_pnl_points"]-t["cost_points"]==t["net_pnl_points"] for t in trades)

@pytest.mark.parametrize("command",COMMANDS)
def test_legacy_cli_remains_supported(tmp_path,command):
    source=tmp_path/"bars.csv"; out=tmp_path/command; _csv(source)
    assert main(_base(command,source,out)+["--round-trip-cost-points","0.5"])==0
    _,summary,_=_artifacts(out); assert summary["configuration"]["cost_mode"]=="legacy_all_in" and summary["configuration"]["effective_round_trip_cost_points"]==.5

@pytest.mark.parametrize("command",COMMANDS)
def test_partial_detailed_cost_cli_is_rejected_atomically(tmp_path,command,capsys):
    source=tmp_path/"bars.csv"; out=tmp_path/command; _csv(source)
    assert main(_base(command,source,out)+["--cost-scenario","nominal"])==2
    assert capsys.readouterr().err.startswith("error:") and not out.exists()

@pytest.mark.parametrize("command",COMMANDS)
def test_detailed_cost_and_nonzero_legacy_cost_are_rejected(tmp_path,command,capsys):
    source=tmp_path/"bars.csv"; out=tmp_path/command; _csv(source)
    assert main(_base(command,source,out)+["--round-trip-cost-points","1"]+_detailed())==2
    assert capsys.readouterr().err.startswith("error:") and not out.exists()

@pytest.mark.parametrize("bad",[("--point-value","0"),("--commission-per-side","-1"),("--spread-points","nan"),("--entry-slippage-points","inf"),("--cost-instrument"," ")])
def test_invalid_detailed_cost_cli_values_are_rejected(tmp_path,bad,capsys):
    source=tmp_path/"bars.csv"; out=tmp_path/"out"; _csv(source); args=_detailed(); args[args.index(bad[0])+1]=bad[1]
    assert main(_base("study-breakout-timeframes",source,out)+["--round-trip-cost-points","0"]+args)==2
    assert capsys.readouterr().err.startswith("error:") and not out.exists()

def test_existing_output_directory_is_preserved_on_cli_error(tmp_path,capsys):
    source=tmp_path/"bars.csv"; out=tmp_path/"out"; _csv(source); out.mkdir(); sentinel=out/"sentinel.txt"; sentinel.write_text("keep")
    assert main(_base("study-breakout-timeframes",source,out)+["--round-trip-cost-points","0"]+_detailed())==2
    assert capsys.readouterr().err.startswith("error:") and sentinel.read_text()=="keep" and list(out.iterdir())==[sentinel]

def test_equal_total_cost_allocations_keep_economics_but_change_identity(tmp_path):
    source=tmp_path/"bars.csv"; _csv(source); left,right=tmp_path/"left",tmp_path/"right"
    assert main(_base("study-breakout-temporal-oos",source,left)+["--round-trip-cost-points","0"]+_detailed("0.1","0.15"))==0
    assert main(_base("study-breakout-temporal-oos",source,right)+["--round-trip-cost-points","0"]+_detailed("0.15","0.1"))==0
    lr,ls,lm=_artifacts(left); rr,rs,rm=_artifacts(right); lt,rt=_trades(lr),_trades(rr)
    assert lt and rt and lm["run_id"]!=rm["run_id"] and ls["configuration"]!=rs["configuration"]
    assert [row["decisions"] for row in _rows(lr)]==[row["decisions"] for row in _rows(rr)]
    fields=("side","entry_timestamp","entry_bar_index","entry_price","exit_timestamp","exit_bar_index","exit_price","exit_reason","gross_pnl_points","cost_points","net_pnl_points")
    assert [tuple(t[x] for x in fields) for t in lt]==[tuple(t[x] for x in fields) for t in rt]
