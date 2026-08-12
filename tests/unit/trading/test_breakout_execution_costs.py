from datetime import datetime,timedelta
import json
import math
import pytest
from agicore.trading.breakout_execution_costs import BreakoutExecutionCostModel
from agicore.trading.breakout_replay import BreakoutReplayConfig,create_breakout_replay,replay_breakout
from agicore.trading.market_replay import OHLCVBar

def model(**changes):
 data=dict(scenario_name='nominal',instrument='MNQ',currency='USD',point_value_currency_per_point=2.0,commission_currency_per_side=.5,round_trip_spread_points=.25,entry_slippage_points=.125,exit_slippage_points=.125); data.update(changes); return BreakoutExecutionCostModel(**data)
def bars():
 values=(10,10,10,12,13,9,8,14,15); start=datetime(2026,8,1); return tuple(OHLCVBar(start+timedelta(minutes=i),v,v+1,v-1,v,1) for i,v in enumerate(values))
def test_detailed_cost_formula_is_exact():
 value=model(); assert value.commission_round_trip_currency==1 and value.commission_round_trip_points==.5 and value.total_round_trip_cost_points==1 and value.serialize()['total_round_trip_cost_points']==1
@pytest.mark.parametrize(
 'changes',
 [
  {'scenario_name': value} for value in ('', ' ')
 ] + [
  {'instrument': value} for value in ('', ' ')
 ] + [
  {'currency': value} for value in ('', ' ')
 ] + [
  {'point_value_currency_per_point': value} for value in (True, 0, -1, math.nan, math.inf)
 ] + [
  {field: value}
  for field in ('commission_currency_per_side', 'round_trip_spread_points', 'entry_slippage_points', 'exit_slippage_points')
  for value in (True, -1, math.nan, math.inf)
 ],
)
def test_detailed_cost_model_rejects_invalid_values(changes):
 with pytest.raises(ValueError): model(**changes)
def test_detailed_and_nonzero_legacy_cost_are_mutually_exclusive():
 with pytest.raises(ValueError): BreakoutReplayConfig(2,1.0,execution_cost_model=model())
 with pytest.raises(ValueError,match='execution_cost_model'): BreakoutReplayConfig(2,0,execution_cost_model='invalid')
def test_legacy_and_equivalent_detailed_cost_preserve_replay():
 legacy=replay_breakout(bars(),BreakoutReplayConfig(2,1)); detailed=replay_breakout(bars(),BreakoutReplayConfig(2,0,execution_cost_model=model()))
 assert legacy['decisions']==detailed['decisions'] and len(legacy['trades'])==len(detailed['trades'])>0
 for left,right in zip(legacy['trades'],detailed['trades']): assert (left.side,left.entry_timestamp,left.exit_timestamp,left.entry_bar_index,left.exit_bar_index,left.entry_price,left.exit_price,left.gross_pnl_points,left.cost_points,left.net_pnl_points)==(right.side,right.entry_timestamp,right.exit_timestamp,right.entry_bar_index,right.exit_bar_index,right.entry_price,right.exit_price,right.gross_pnl_points,right.cost_points,right.net_pnl_points)
def test_detailed_cost_applies_to_reversal_and_end_of_data():
 result=replay_breakout(bars(),BreakoutReplayConfig(2,0,execution_cost_model=model())); assert any(t.exit_reason=='SIGNAL_REVERSAL' for t in result['trades']) and any(t.exit_reason=='END_OF_DATA' for t in result['trades']) and all(t.cost_points==1 and t.gross_pnl_points-t.net_pnl_points==1 for t in result['trades'])
def test_detailed_cost_bundle_is_auditable_and_run_id_sensitive(tmp_path):
 source=tmp_path/'bars.csv'; rows=['timestamp,open,high,low,close,volume']+[f'{x.timestamp},{x.open},{x.high},{x.low},{x.close},{x.volume}' for x in bars()]; source.write_text('\n'.join(rows),encoding='utf-8')
 one=create_breakout_replay(source,tmp_path/'one',BreakoutReplayConfig(2,0,execution_cost_model=model())); two=create_breakout_replay(source,tmp_path/'two',BreakoutReplayConfig(2,0,execution_cost_model=model())); changed=create_breakout_replay(source,tmp_path/'changed',BreakoutReplayConfig(2,0,execution_cost_model=model(exit_slippage_points=.25)))
 trades=json.loads((one/'trades.json').read_text()); manifest=json.loads((one/'manifest.json').read_text()); assert trades and all(t['cost_breakdown']['cost_mode']=='detailed' and t['gross_pnl_points']-t['net_pnl_points']==t['cost_breakdown']['total_round_trip_cost_points'] for t in trades)
 assert manifest['run_id']==json.loads((two/'manifest.json').read_text())['run_id']!=json.loads((changed/'manifest.json').read_text())['run_id']
 report=(one/'report.md').read_text()
 assert '- Cost mode: detailed' in report and '- Effective round-trip cost: 1.00' in report
 assert '- Scenario: nominal' in report and '- Instrument: MNQ' in report and '- Currency: USD' in report
def test_legacy_bundle_keeps_strategy_hash_and_ledger_contract(tmp_path):
 source=tmp_path/'bars.csv'; source.write_text('timestamp,open,high,low,close,volume\n'+'\n'.join(f'{x.timestamp},{x.open},{x.high},{x.low},{x.close},{x.volume}' for x in bars()),encoding='utf-8')
 bundle=create_breakout_replay(source,tmp_path/'legacy',BreakoutReplayConfig(2,1)); manifest=json.loads((bundle/'manifest.json').read_text()); trades=json.loads((bundle/'trades.json').read_text())
 strategy={"name":"CAUSAL_PRICE_CHANNEL_BREAKOUT","lookback_bars":2,"execution":"next_bar_open","position_size":1,"round_trip_cost_points":1,"side_policy":"BOTH","pyramiding":False,"channel_rule":"prior_completed_bars_only","exit_rule":"opposite_breakout_or_end_of_data"}
 assert manifest['strategy']==strategy and manifest['strategy_sha256']==__import__('hashlib').sha256(json.dumps(strategy,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 assert all(t['cost_breakdown']=={'cost_mode':'legacy_all_in','legacy_round_trip_cost_points':1,'total_round_trip_cost_points':1} and t['gross_pnl_points']-t['net_pnl_points']==t['cost_points']==t['cost_breakdown']['total_round_trip_cost_points'] for t in trades)
def test_same_total_detailed_components_change_identity_not_replay(tmp_path):
 source=tmp_path/'bars.csv'; source.write_text('timestamp,open,high,low,close,volume\n'+'\n'.join(f'{x.timestamp},{x.open},{x.high},{x.low},{x.close},{x.volume}' for x in bars()),encoding='utf-8')
 a=model(entry_slippage_points=.1,exit_slippage_points=.15); b=model(entry_slippage_points=.15,exit_slippage_points=.1)
 assert a.total_round_trip_cost_points==b.total_round_trip_cost_points>0
 one=create_breakout_replay(source,tmp_path/'one',BreakoutReplayConfig(2,0,execution_cost_model=a)); two=create_breakout_replay(source,tmp_path/'two',BreakoutReplayConfig(2,0,execution_cost_model=b))
 m1=json.loads((one/'manifest.json').read_text()); m2=json.loads((two/'manifest.json').read_text())
 t1=json.loads((one/'trades.json').read_text()); t2=json.loads((two/'trades.json').read_text())
 d1=json.loads((one/'decisions.json').read_text()); d2=json.loads((two/'decisions.json').read_text())
 assert d1 and d1==d2 and t1 and t2 and len(t1)==len(t2)
 assert [trade['cost_breakdown'] for trade in t1] != [trade['cost_breakdown'] for trade in t2]
 fields=('side','entry_timestamp','entry_bar_index','entry_price','exit_timestamp','exit_bar_index','exit_price','exit_reason','gross_pnl_points','cost_points','net_pnl_points')
 for left,right in zip(t1,t2): assert tuple(left[field] for field in fields)==tuple(right[field] for field in fields)
 assert m1['strategy_sha256']!=m2['strategy_sha256'] and m1['run_id']!=m2['run_id']
