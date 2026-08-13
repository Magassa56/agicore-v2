"""Auditable detailed execution costs for breakout replay."""
from __future__ import annotations
import math
from dataclasses import dataclass

@dataclass(frozen=True)
class BreakoutExecutionCostModel:
    scenario_name: str; instrument: str; currency: str; point_value_currency_per_point: float; commission_currency_per_side: float; round_trip_spread_points: float; entry_slippage_points: float; exit_slippage_points: float
    def __post_init__(self):
        if any(not isinstance(value,str) or not value.strip() for value in (self.scenario_name,self.instrument,self.currency)): raise ValueError("scenario_name, instrument, and currency must be non-empty strings")
        for name,value,positive in (("point_value_currency_per_point",self.point_value_currency_per_point,True),("commission_currency_per_side",self.commission_currency_per_side,False),("round_trip_spread_points",self.round_trip_spread_points,False),("entry_slippage_points",self.entry_slippage_points,False),("exit_slippage_points",self.exit_slippage_points,False)):
            if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or (value<=0 if positive else value<0): raise ValueError(f"{name} must be a finite {'positive' if positive else 'non-negative'} number")
    @property
    def commission_round_trip_currency(self): return 2*self.commission_currency_per_side
    @property
    def commission_round_trip_points(self): return self.commission_round_trip_currency/self.point_value_currency_per_point
    @property
    def total_round_trip_cost_points(self): return self.commission_round_trip_points+self.round_trip_spread_points+self.entry_slippage_points+self.exit_slippage_points
    def serialize(self): return {"cost_mode":"detailed","scenario_name":self.scenario_name,"instrument":self.instrument,"currency":self.currency,"point_value_currency_per_point":self.point_value_currency_per_point,"commission_currency_per_side":self.commission_currency_per_side,"commission_round_trip_currency":self.commission_round_trip_currency,"commission_round_trip_points":self.commission_round_trip_points,"round_trip_spread_points":self.round_trip_spread_points,"entry_slippage_points":self.entry_slippage_points,"exit_slippage_points":self.exit_slippage_points,"total_round_trip_cost_points":self.total_round_trip_cost_points}
