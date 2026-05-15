"""Unit tests for RiskManager."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from agicore.core.events import EventBus
from agicore.risk.exposure_models import (
    EVT_RISK_BLOCKED,
    EVT_RISK_PASSED,
    ExecutionIntent,
    ExposureSnapshot,
    IntentSide,
    RiskCheckCode,
    RiskLevel,
    RiskLimits,
    SymbolExposure,
    empty_snapshot,
)
from agicore.risk.risk_manager import RiskManager


def _intent(
    *,
    intent_id: str = "i-1",
    symbol: str = "ES",
    side: IntentSide = IntentSide.BUY,
    quantity: float = 1.0,
    estimated_price: float = 100.0,
) -> ExecutionIntent:
    return ExecutionIntent(
        intent_id=intent_id, symbol=symbol, side=side,
        quantity=quantity, estimated_price=estimated_price,
        timestamp=datetime.now(timezone.utc),
    )


def _snapshot_with_position(
    qty: float = 0.0,
    avg: float = 100.0,
    mark: float = 100.0,
    *,
    realized: float = 0.0,
    daily: float = 0.0,
    initial: float = 10_000.0,
    peak: float | None = None,
) -> ExposureSnapshot:
    positions = {}
    if qty > 0:
        positions["ES"] = SymbolExposure(
            symbol="ES", quantity=qty, avg_entry_price=avg, mark_price=mark,
        )
    return ExposureSnapshot(
        positions=positions,
        realized_pnl_total=realized,
        daily_pnl=daily,
        initial_equity=initial,
        peak_equity=peak if peak is not None else initial,
    )


# ---------------------------------------------------------------- No limits
class TestNoLimits:
    def test_passes_when_no_limits_configured(self) -> None:
        rm = RiskManager(RiskLimits())
        result = rm.validate(_intent(), empty_snapshot())
        assert result.passed
        assert result.violations == []

    def test_intent_id_propagated_in_result(self) -> None:
        rm = RiskManager(RiskLimits())
        result = rm.validate(_intent(intent_id="abc"), empty_snapshot())
        assert result.intent_id == "abc"


# ---------------------------------------------------------------- Long-only safeguard
class TestLongOnlySafeguard:
    def test_sell_without_position_blocked(self) -> None:
        rm = RiskManager(RiskLimits())
        result = rm.validate(
            _intent(side=IntentSide.SELL, quantity=2.0),
            empty_snapshot(),
        )
        assert not result.passed
        assert any(v.code == RiskCheckCode.INSUFFICIENT_POSITION
                   for v in result.violations)

    def test_sell_oversize_blocked(self) -> None:
        rm = RiskManager(RiskLimits())
        result = rm.validate(
            _intent(side=IntentSide.SELL, quantity=5.0),
            _snapshot_with_position(qty=2.0),
        )
        assert not result.passed
        assert any(v.code == RiskCheckCode.INSUFFICIENT_POSITION
                   for v in result.violations)

    def test_sell_within_position_passes(self) -> None:
        rm = RiskManager(RiskLimits())
        result = rm.validate(
            _intent(side=IntentSide.SELL, quantity=1.0),
            _snapshot_with_position(qty=2.0),
        )
        assert result.passed


# ---------------------------------------------------------------- Position size
class TestPositionSize:
    def test_buy_within_limit_passes(self) -> None:
        rm = RiskManager(RiskLimits(max_position_size=10.0))
        result = rm.validate(
            _intent(quantity=5.0),
            _snapshot_with_position(qty=3.0),
        )
        assert result.passed

    def test_buy_exceeds_limit_blocks(self) -> None:
        rm = RiskManager(RiskLimits(max_position_size=10.0))
        result = rm.validate(
            _intent(quantity=8.0),
            _snapshot_with_position(qty=5.0),
        )
        assert not result.passed
        v = next(v for v in result.violations
                 if v.code == RiskCheckCode.POSITION_SIZE_EXCEEDED)
        assert v.limit_value == 10.0
        assert v.actual_value == 13.0


# ---------------------------------------------------------------- Exposure
class TestExposure:
    def test_within_exposure_limit_passes(self) -> None:
        rm = RiskManager(RiskLimits(max_exposure_value=10_000.0))
        result = rm.validate(
            _intent(quantity=10.0, estimated_price=100.0),
            empty_snapshot(),
        )
        assert result.passed

    def test_exceeds_exposure_limit_blocks(self) -> None:
        rm = RiskManager(RiskLimits(max_exposure_value=500.0))
        result = rm.validate(
            _intent(quantity=10.0, estimated_price=100.0),
            empty_snapshot(),
        )
        assert not result.passed
        assert any(v.code == RiskCheckCode.EXPOSURE_EXCEEDED
                   for v in result.violations)

    def test_existing_other_symbol_counts_toward_total(self) -> None:
        rm = RiskManager(RiskLimits(max_exposure_value=600.0))
        snap = ExposureSnapshot(
            positions={
                "NQ": SymbolExposure(symbol="NQ", quantity=2.0,
                                      avg_entry_price=200.0, mark_price=200.0),
            },
            initial_equity=10_000.0, peak_equity=10_000.0,
        )
        # NQ exposure = 400. Buying ES with 3 @ 100 → +300 → total 700 > 600
        result = rm.validate(
            _intent(symbol="ES", quantity=3.0, estimated_price=100.0),
            snap,
        )
        assert not result.passed


# ---------------------------------------------------------------- Drawdown
class TestDrawdown:
    def test_drawdown_within_limit_passes(self) -> None:
        rm = RiskManager(RiskLimits(max_drawdown_pct=0.10))
        snap = ExposureSnapshot(
            positions={}, realized_pnl_total=-500.0,
            initial_equity=10_000.0, peak_equity=10_000.0,
        )  # dd = 5%
        result = rm.validate(_intent(), snap)
        assert result.passed

    def test_drawdown_exceeds_limit_blocks(self) -> None:
        rm = RiskManager(RiskLimits(max_drawdown_pct=0.05))
        snap = ExposureSnapshot(
            positions={}, realized_pnl_total=-1500.0,
            initial_equity=10_000.0, peak_equity=10_000.0,
        )  # dd = 15%
        result = rm.validate(_intent(), snap)
        assert not result.passed
        assert any(v.code == RiskCheckCode.DRAWDOWN_EXCEEDED
                   for v in result.violations)


# ---------------------------------------------------------------- Daily loss
class TestDailyLoss:
    def test_daily_loss_within_limit_passes(self) -> None:
        rm = RiskManager(RiskLimits(daily_loss_limit=500.0))
        snap = _snapshot_with_position(daily=-300.0)
        result = rm.validate(_intent(), snap)
        assert result.passed

    def test_daily_loss_exceeds_limit_blocks(self) -> None:
        rm = RiskManager(RiskLimits(daily_loss_limit=200.0))
        snap = _snapshot_with_position(daily=-500.0)
        result = rm.validate(_intent(), snap)
        assert not result.passed
        assert any(v.code == RiskCheckCode.DAILY_LOSS_EXCEEDED
                   for v in result.violations)

    def test_daily_profit_does_not_block(self) -> None:
        rm = RiskManager(RiskLimits(daily_loss_limit=200.0))
        snap = _snapshot_with_position(daily=300.0)  # gain
        result = rm.validate(_intent(), snap)
        assert result.passed


# ---------------------------------------------------------------- Combined
class TestCombined:
    def test_multiple_violations_recorded(self) -> None:
        rm = RiskManager(RiskLimits(
            max_position_size=2.0,
            max_exposure_value=100.0,
        ))
        result = rm.validate(
            _intent(quantity=10.0, estimated_price=100.0),
            empty_snapshot(),
        )
        # Both POSITION_SIZE and EXPOSURE breached
        codes = {v.code for v in result.violations}
        assert RiskCheckCode.POSITION_SIZE_EXCEEDED in codes
        assert RiskCheckCode.EXPOSURE_EXCEEDED in codes
        assert not result.passed
        assert result.is_blocked is True


# ---------------------------------------------------------------- Bus emission
class TestBusEmission:
    def test_emits_passed_event(self) -> None:
        bus = EventBus()
        captured: list = []
        bus.subscribe(EVT_RISK_PASSED, lambda ev: captured.append(ev))
        rm = RiskManager(RiskLimits(), event_bus=bus)
        rm.validate(_intent(), empty_snapshot())
        assert len(captured) == 1
        assert captured[0].payload["intent_id"] == "i-1"

    def test_emits_blocked_event(self) -> None:
        bus = EventBus()
        captured: list = []
        bus.subscribe(EVT_RISK_BLOCKED, lambda ev: captured.append(ev))
        rm = RiskManager(RiskLimits(max_position_size=1.0), event_bus=bus)
        rm.validate(_intent(quantity=5.0), empty_snapshot())
        assert len(captured) == 1
        assert "POSITION_SIZE_EXCEEDED" in captured[0].payload["violation_codes"]

    def test_works_without_bus(self) -> None:
        rm = RiskManager(RiskLimits())
        result = rm.validate(_intent(), empty_snapshot())
        assert result.passed


# ---------------------------------------------------------------- Determinism
class TestDeterminism:
    def test_same_inputs_yield_same_violations(self) -> None:
        rm = RiskManager(RiskLimits(
            max_position_size=5.0, max_exposure_value=1000.0,
            max_drawdown_pct=0.1, daily_loss_limit=100.0,
        ))
        intent = _intent(quantity=10.0, estimated_price=200.0)
        snap = ExposureSnapshot(
            positions={
                "ES": SymbolExposure(symbol="ES", quantity=4.0,
                                      avg_entry_price=100, mark_price=100)
            },
            realized_pnl_total=-1500.0, daily_pnl=-200.0,
            initial_equity=10_000.0, peak_equity=10_000.0,
        )
        r1 = rm.validate(intent, snap)
        r2 = rm.validate(intent, snap)
        assert {v.code for v in r1.violations} == {v.code for v in r2.violations}
