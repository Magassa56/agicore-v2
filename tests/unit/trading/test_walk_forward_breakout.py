from __future__ import annotations
import json
from datetime import datetime,timedelta
import pytest
from agicore.cli.main import main
from agicore.trading.walk_forward_breakout import WalkForwardBreakoutError,create_walk_forward_breakout_study
def _csv(path,count=100,offset=0,mutation_start=60):
 rows=["timestamp,open,high,low,close,volume"]; start=datetime(2026,1,1)
 for i in range(count):
  v=100 if i%3<2 else 102
  if i>=mutation_start:v+=offset
  rows.append(f"{(start+timedelta(minutes=i)).isoformat(sep=' ')},{v},{v+1},{v-1},{v},1")
 path.write_text("\n".join(rows),encoding="utf-8")
def test_expanding_folds_and_artifacts_are_exact(tmp_path):
 p=tmp_path/'a.csv'; _csv(p); out=create_walk_forward_breakout_study(p,tmp_path/'one',initial_train_bars=40,validation_bars=10,oos_bars=10,lookback_bars=2,round_trip_cost_points=.5)
 rows=json.loads((out/'results.json').read_text()); summary=json.loads((out/'summary.json').read_text()); manifest=json.loads((out/'manifest.json').read_text())
 assert [(x['fold_index'],x['role'],x['source_start_index'],x['source_end_index']) for x in rows]==[(0,'train',0,39),(0,'validation',40,49),(0,'oos',50,59),(1,'train',0,59),(1,'validation',60,69),(1,'oos',70,79),(2,'train',0,79),(2,'validation',80,89),(2,'oos',90,99)]
 assert summary['complete_fold_count']==3 and summary['excluded_final_bar_count']==0 and set(manifest['generated_files'])=={'manifest.json','results.json','summary.json'}
 assert all(x['starts_flat'] and x['local_lookback_warmup_bar_count']==2 and x['cross_boundary_warmup_bar_count']==0 and x['source_sha256']==manifest['input_sha256'] for x in rows)
 forbidden={'winner','best','ranking','rank','score','selection','selected','recommended','recommendation','optimized','optimization'}
 def keys(value):
  if isinstance(value,dict):
   for key,item in value.items(): yield key; yield from keys(item)
  elif isinstance(value,list):
   for item in value: yield from keys(item)
 assert not (set(keys({'r':rows,'s':summary,'m':manifest})) & forbidden)
def test_future_extension_preserves_completed_folds_and_adds_fold_three(tmp_path):
 a,b=tmp_path/'a.csv',tmp_path/'b.csv'; _csv(a,100); _csv(b,120)
 one=create_walk_forward_breakout_study(a,tmp_path/'one',initial_train_bars=40,validation_bars=10,oos_bars=10,lookback_bars=2); two=create_walk_forward_breakout_study(b,tmp_path/'two',initial_train_bars=40,validation_bars=10,oos_bars=10,lookback_bars=2)
 left=json.loads((one/'results.json').read_text()); right=json.loads((two/'results.json').read_text()); assert [{k:v for k,v in x.items() if k!='source_sha256'} for x in left]==[{k:v for k,v in x.items() if k!='source_sha256'} for x in right[:9]] and [(x['role'],x['source_start_index'],x['source_end_index']) for x in right[9:]]==[('train',0,99),('validation',100,109),('oos',110,119)]
 with pytest.raises(WalkForwardBreakoutError): create_walk_forward_breakout_study(a,tmp_path/'bad',initial_train_bars=0,validation_bars=10,oos_bars=10,lookback_bars=2)
 with pytest.raises(WalkForwardBreakoutError): create_walk_forward_breakout_study(a,tmp_path/'bad-validation',initial_train_bars=40,validation_bars=2,oos_bars=10,lookback_bars=2)
 assert main(['trading','study-breakout-walk-forward',str(a),'--output-dir',str(tmp_path/'cli'),'--initial-train-bars','40','--validation-bars','10','--oos-bars','10','--lookback-bars','2'])==0
 assert all((tmp_path/'cli'/name).is_file() for name in ('manifest.json','results.json','summary.json'))
 assert main(['trading','study-breakout-walk-forward',str(a),'--output-dir',str(tmp_path/'cli-bad'),'--initial-train-bars','0','--validation-bars','10','--oos-bars','10','--lookback-bars','2'])==2
def test_oos_mutation_changes_only_final_oos_replay(tmp_path):
 a,b=tmp_path/'a.csv',tmp_path/'b.csv'; _csv(a,100); _csv(b,100,offset=500,mutation_start=90)
 one=create_walk_forward_breakout_study(a,tmp_path/'one',initial_train_bars=40,validation_bars=10,oos_bars=10,lookback_bars=2,round_trip_cost_points=.5); two=create_walk_forward_breakout_study(b,tmp_path/'two',initial_train_bars=40,validation_bars=10,oos_bars=10,lookback_bars=2,round_trip_cost_points=.5)
 left=json.loads((one/'results.json').read_text()); right=json.loads((two/'results.json').read_text()); lm=json.loads((one/'manifest.json').read_text()); rm=json.loads((two/'manifest.json').read_text())
 assert [{k:v for k,v in left[i].items() if k!='source_sha256'} for i in range(8)]==[{k:v for k,v in right[i].items() if k!='source_sha256'} for i in range(8)]
 assert left[8]['segment_sha256']!=right[8]['segment_sha256'] and left[8]['decisions'] and left[8]['trades'] and lm['run_id']!=rm['run_id']
 assert left[8]['trades']!=right[8]['trades'] or left[8]['decisions']!=right[8]['decisions'] or left[8]['metrics']!=right[8]['metrics']
 assert all(x['boundary_forced_close_count']==sum(t['exit_reason']=='END_OF_DATA' for t in x['trades']) for x in left)
 assert all(x['metrics']['gross_total_pnl_points']-x['metrics']['net_total_pnl_points']==pytest.approx(.5*x['metrics']['total_trades']) for x in left)
 assert all({'entry_timestamp','entry_price','exit_timestamp','exit_price','entry_bar_index','exit_bar_index','exit_reason','cost_points','gross_pnl_points','net_pnl_points'} <= set(t) for x in left for t in x['trades'])
 partial=tmp_path/'partial.csv'; _csv(partial,105); out=create_walk_forward_breakout_study(partial,tmp_path/'partial',initial_train_bars=40,validation_bars=10,oos_bars=10,lookback_bars=2); s=json.loads((out/'summary.json').read_text()); m=json.loads((out/'manifest.json').read_text())
 assert s['complete_fold_count']==3 and s['excluded_final_bar_count']==m['excluded_final_bar_count']==5 and len(json.loads((out/'results.json').read_text()))==9
 for value in (0,-1):
  with pytest.raises(WalkForwardBreakoutError): create_walk_forward_breakout_study(a,tmp_path/f'bad-{value}',initial_train_bars=40,validation_bars=value,oos_bars=10,lookback_bars=2)
def test_partial_tail_and_role_aggregates_are_reconciled(tmp_path):
 p=tmp_path/'p.csv'; _csv(p,105); out=create_walk_forward_breakout_study(p,tmp_path/'out',initial_train_bars=40,validation_bars=10,oos_bars=10,lookback_bars=2); rows=json.loads((out/'results.json').read_text()); summary=json.loads((out/'summary.json').read_text())
 assert summary['excluded_final_bar_count']==5
 for role,aggregate in summary['by_role'].items():
  values=[x for x in rows if x['role']==role]; assert aggregate=={'segment_count':len(values),'total_trades':sum(x['metrics']['total_trades'] for x in values),'gross_total_pnl_points':sum(x['metrics']['gross_total_pnl_points'] for x in values),'net_total_pnl_points':sum(x['metrics']['net_total_pnl_points'] for x in values),'boundary_forced_close_count':sum(x['boundary_forced_close_count'] for x in values)}
def test_boundary_forced_close_and_costs_are_non_vacuous(tmp_path):
 p=tmp_path/'p.csv'; _csv(p); rows=json.loads((create_walk_forward_breakout_study(p,tmp_path/'out',initial_train_bars=40,validation_bars=10,oos_bars=10,lookback_bars=2,round_trip_cost_points=.5)/'results.json').read_text()); trades=[t for x in rows for t in x['trades']]
 assert trades and any(t['exit_reason']=='END_OF_DATA' for t in trades) and sum(x['boundary_forced_close_count'] for x in rows)>0
 assert all(t['gross_pnl_points']-t['net_pnl_points']==pytest.approx(t['cost_points']) for t in trades)
def test_run_id_is_reproducible_and_configuration_sensitive(tmp_path):
 p=tmp_path/'p.csv'; _csv(p)
 def make(name,**kw):
  args={'initial_train_bars':40,'validation_bars':10,'oos_bars':10,'lookback_bars':2}; args.update(kw)
  return create_walk_forward_breakout_study(p,tmp_path/name,**args)
 assert json.loads((make('a')/'manifest.json').read_text())['run_id']==json.loads((make('b')/'manifest.json').read_text())['run_id']
 base_run=json.loads((make('d')/'manifest.json').read_text())['run_id']
 assert json.loads((make('c',side_policy='LONG_ONLY')/'manifest.json').read_text())['run_id']!=base_run
 assert json.loads((make('e',initial_train_bars=60)/'manifest.json').read_text())['run_id']!=base_run
def test_invalid_sizes_and_short_segments_publish_nothing(tmp_path):
 p=tmp_path/'p.csv'; _csv(p)
 for name,kw in enumerate(({'initial_train_bars':0},{'validation_bars':0},{'oos_bars':0},{'initial_train_bars':2},{'validation_bars':2},{'oos_bars':2})):
  out=tmp_path/f'bad{name}'; args={'initial_train_bars':40,'validation_bars':10,'oos_bars':10,'lookback_bars':2}; args.update(kw)
  with pytest.raises(WalkForwardBreakoutError): create_walk_forward_breakout_study(p,out,**args)
  assert not out.exists()
 for name,kw in enumerate(({'initial_train_bars':-1},{'validation_bars':-1},{'oos_bars':-1})):
  out=tmp_path/f'negative{name}'; args={'initial_train_bars':40,'validation_bars':10,'oos_bars':10,'lookback_bars':2}; args.update(kw)
  with pytest.raises(WalkForwardBreakoutError): create_walk_forward_breakout_study(p,out,**args)
  assert not out.exists()
 short=tmp_path/'short.csv'; _csv(short,59)
 with pytest.raises(WalkForwardBreakoutError): create_walk_forward_breakout_study(short,tmp_path/'short-out',initial_train_bars=40,validation_bars=10,oos_bars=10,lookback_bars=2)
 assert not (tmp_path/'short-out').exists()
def test_existing_output_directory_and_cli_errors_are_controlled(tmp_path):
 p=tmp_path/'p.csv'; _csv(p); out=tmp_path/'out'; out.mkdir(); sentinel=out/'sentinel.txt'; sentinel.write_text('unchanged',encoding='utf-8')
 with pytest.raises(WalkForwardBreakoutError): create_walk_forward_breakout_study(p,out,initial_train_bars=40,validation_bars=10,oos_bars=10,lookback_bars=2)
 assert sentinel.read_text(encoding='utf-8')=='unchanged'
 assert main(['trading','study-breakout-walk-forward',str(p),'--output-dir',str(out),'--initial-train-bars','40','--validation-bars','10','--oos-bars','10','--lookback-bars','2'])==2
 assert sentinel.read_text(encoding='utf-8')=='unchanged'
def test_all_published_json_keys_are_neutral(tmp_path):
 p=tmp_path/'p.csv'; _csv(p); out=create_walk_forward_breakout_study(p,tmp_path/'out',initial_train_bars=40,validation_bars=10,oos_bars=10,lookback_bars=2)
 def walk(v):
  if isinstance(v,dict):
   for k,x in v.items(): yield k; yield from walk(x)
  elif isinstance(v,list):
   for x in v: yield from walk(x)
 keys=set().union(*(set(walk(json.loads((out/n).read_text()))) for n in ('results.json','summary.json','manifest.json')))
 assert not keys & {'winner','best','ranking','rank','score','selection','selected','recommended','recommendation','optimized','optimization'}
