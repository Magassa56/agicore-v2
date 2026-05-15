"""Unit tests for risk exposure models."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from agicore.risk.exposure_models import (
    EVT_RISK_BLOCKED,
    EVT_RISK_PASSED,
    ExecutionIntent,
    ExposureSnapshot,
    IntentSide,
    RiskCheckCode,
    RiskCheckResult,
    RiskLevel,
    RiskLimits,
    RiskViolation,
    SymbolExposure,
    empty_snapshot,
)


def test_canonical_event_constants() -> None:
    assert EVT_RISK_PASSED == "risk.check.passed"
    assert EVT_RISK_BLOCKED == "risk.check.blocked"


def test_enum_values() -> None:
    assert RiskLevel.BLOCK.value == "BLOCK"
    assert RiskLevel.WARN.value == "WARN"
    assert RiskLevel.INFO.value == "INFO"
    assert RiskCheckCode.POSITION_SIZE_EXCEEDED.value == "POSITION_SIZE_EXCEEDED"
    assert IntentSide.BUY.value == "BUY"
    assert IntentSide.SELL.value == "SELL"


def test_risk_limits_all_optional() -> None:
    limits = RiskLimits()
    assert limits.max_position_size is None
    assert limits.max_exposure_value is None
    assert limits.max_drawdown_pct is None
    assert limits.daily_loss_limit is None


def test_risk_limits_validation_drawdown_range() -> None:
    with pytest.raises(ValidationError):
        RiskLimits(max_drawdown_pct=1.5)
    with pytest.raises(ValidationError):
        RiskLimits(max_drawdown_pct=-0.1)


def test_risk_limits_validation_negatives() -> None:
    with pytest.raises(ValidationError):
        RiskLimits(max_position_size=-1)
    with pytest.raises(ValidationError):
        RiskLimits(max_exposure_value=-1)
    with pytest.raises(ValidationError):
        RiskLimits(daily_loss_limit=-1)


def test_symbol_exposure_value_property() -> None:
    se = SymbolExposure(symbol="ES", quantity=4.0,
                        avg_entry_price=100.0, mark_price=110.0)
    assert se.exposure_value == pytest.approx(440.0)


def test_symbol_exposure_long_only() -> None:
    with pytest.raises(ValidationError):
        SymbolExposure(symbol="ES", quantity=-1.0,
                       avg_entry_price=100, mark_price=100)


def test_exposure_snapshot_computed_fields() -> None:
    snap = ExposureSnapshot(
        positions={
            "ES": SymbolExposure(symbol="ES", quantity=4.0,
                                  avg_entry_price=100.0, mark_price=110.0),
            "NQ": SymbolExposure(symbol="NQ", quantity=2.0,
                                  avg_entry_price=200.0, mark_price=210.0),
        },
        realized_pnl_total=80.0,
        daily_pnl=-20.0,
        initial_equity=10_000.0,
        peak_equity=10_100.0,
    )
    assert snap.current_equity == pytest.approx(10_080.0)
    assert snap.total_gross_exposure == pytest.approx(440.0 + 420.0)
    # peak 10100, current 10080 → dd = 20/10100
    assert snap.drawdown_pct == pytest.approx(20.0 / 10_100.0)


def test_exposure_snapshot_no_drawdown_when_above_peak() -> None:
    snap = ExposureSnapshot(
        positions={},
        realized_pnl_total=200.0,
        initial_equity=10_000.0,
        peak_equity=10_000.0,
    )
    # current 10200 > peak 10000 → drawdown clamped to 0
    assert snap.drawdown_pct == 0.0


def test_empty_snapshot_helper() -> None:
    snap = empty_snapshot(initial_equity=5_000.0)
    assert snap.positions == {}
    assert snap.initial_equity == 5_000.0
    assert snap.peak_equity == 5_000.0
    assert snap.current_equity == 5_000.0


def test_execution_intent_validation() -> None:
    with pytest.raises(ValidationError):
        ExecutionIntent(intent_id="", symbol="ES", side=IntentSide.BUY,
                        quantity=1.0, estimated_price=100.0,
                        timestamp=datetime.now(timezone.utc))
    with pytest.raises(ValidationError):
        ExecutionIntent(intent_id="i", symbol="ES", side=IntentSide.BUY,
                        quantity=0, estimated_price=100.0,
                        timestamp=datetime.now(timezone.utc))
    with pytest.raises(ValidationError):
        ExecutionIntent(intent_id="i", symbol="ES", side=IntentSide.BUY,
                        quantity=1.0, estimated_price=0,
                        timestamp=datetime.now(timezone.utc))


def test_risk_check_result_is_blocked_property() -> None:
    blocked = RiskCheckResult(
        passed=False,
        violations=[RiskViolation(code=RiskCheckCode.POSITION_SIZE_EXCEEDED,
                                   level=RiskLevel.BLOCK, message="x")],
        timestamp=datetime.now(timezone.utc),
    )
    assert blocked.is_blocked is True

    warn_only = RiskCheckResult(
        passed=True,
        violations=[RiskViolation(code=RiskCheckCode.OK,
                                   level=RiskLevel.INFO, message="ok")],
        timestamp=datetime.now(timezone.utc),
    )
    assert warn_only.is_blocked is False


def test_models_are_frozen() -> None:
    limits = RiskLimits(max_position_size=10)
    with pytest.raises(Exception):
        limits.max_position_size = 99  # type: ignore[misc]
