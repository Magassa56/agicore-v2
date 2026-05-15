"""RiskManager — pre-execution gatekeeper.

Stateless validation pipeline that takes an ``ExecutionIntent`` plus a
caller-supplied ``ExposureSnapshot`` and returns a ``RiskCheckResult``
listing all violations. The manager does NOT mutate state, fetch market
data, or place orders ; it only validates and emits events.

Bus events
----------
- ``risk.check.passed``  : emitted when no BLOCK-level violation
- ``risk.check.blocked`` : emitted when at least one BLOCK violation

Both payloads carry ``intent_id``, ``symbol``, ``side``, ``quantity``,
plus a list of violation codes.

Thread-safety
-------------
The manager is stateless apart from ``RiskLimits`` (frozen) and an
optional EventBus reference. All operations are safe to call from
multiple threads concurrently.
"""
from __future__ import annotations

from datetime import datetime, timezone

import structlog

from agicore.core.events import EventBus

from .exposure_models import (
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
)

logger = structlog.get_logger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RiskManager:
    """Pre-execution risk gatekeeper.

    Parameters
    ----------
    limits : RiskLimits
        Required. Each ``None`` field disables the corresponding check.
    event_bus : EventBus | None
        Optional. When provided, emits ``risk.check.passed`` /
        ``risk.check.blocked`` events for every validation.
    """

    def __init__(
        self,
        limits: RiskLimits,
        *,
        event_bus: EventBus | None = None,
    ) -> None:
        self._limits = limits
        self._bus = event_bus

    # ------------------------------------------------------------------ Inspection
    @property
    def limits(self) -> RiskLimits:
        return self._limits

    # ------------------------------------------------------------------ Validation
    def validate(
        self,
        intent: ExecutionIntent,
        snapshot: ExposureSnapshot,
    ) -> RiskCheckResult:
        """Run all configured checks and return a RiskCheckResult."""
        violations: list[RiskViolation] = []

        delta_qty = (
            intent.quantity if intent.side == IntentSide.BUY else -intent.quantity
        )
        current_pos = snapshot.positions.get(intent.symbol)
        current_qty = current_pos.quantity if current_pos else 0.0
        proposed_qty = current_qty + delta_qty

        # Check 0 — long-only safeguard (no shorts allowed in Phase 8C)
        if proposed_qty < 0:
            violations.append(RiskViolation(
                code=RiskCheckCode.INSUFFICIENT_POSITION,
                level=RiskLevel.BLOCK,
                message=(
                    f"insufficient position : have={current_qty}, "
                    f"want_to_sell={intent.quantity}"
                ),
                limit_value=current_qty,
                actual_value=proposed_qty,
            ))

        # Check 1 — max position size per symbol
        if self._limits.max_position_size is not None:
            if abs(proposed_qty) > self._limits.max_position_size:
                violations.append(RiskViolation(
                    code=RiskCheckCode.POSITION_SIZE_EXCEEDED,
                    level=RiskLevel.BLOCK,
                    message=(
                        f"position size limit breached on {intent.symbol}"
                    ),
                    limit_value=self._limits.max_position_size,
                    actual_value=abs(proposed_qty),
                ))

        # Check 2 — max gross exposure value
        if self._limits.max_exposure_value is not None:
            current_exposure_for_symbol = (
                current_pos.exposure_value if current_pos else 0.0
            )
            other_exposure = (
                snapshot.total_gross_exposure - current_exposure_for_symbol
            )
            new_symbol_exposure = abs(proposed_qty) * intent.estimated_price
            proposed_total = max(0.0, other_exposure) + new_symbol_exposure
            if proposed_total > self._limits.max_exposure_value:
                violations.append(RiskViolation(
                    code=RiskCheckCode.EXPOSURE_EXCEEDED,
                    level=RiskLevel.BLOCK,
                    message="gross exposure limit breached",
                    limit_value=self._limits.max_exposure_value,
                    actual_value=proposed_total,
                ))

        # Check 3 — max drawdown
        if self._limits.max_drawdown_pct is not None:
            if snapshot.drawdown_pct > self._limits.max_drawdown_pct:
                violations.append(RiskViolation(
                    code=RiskCheckCode.DRAWDOWN_EXCEEDED,
                    level=RiskLevel.BLOCK,
                    message="max drawdown exceeded",
                    limit_value=self._limits.max_drawdown_pct,
                    actual_value=snapshot.drawdown_pct,
                ))

        # Check 4 — daily loss limit
        if self._limits.daily_loss_limit is not None:
            # daily_pnl is negative when losing money ; compare absolute loss
            if snapshot.daily_pnl < -self._limits.daily_loss_limit:
                violations.append(RiskViolation(
                    code=RiskCheckCode.DAILY_LOSS_EXCEEDED,
                    level=RiskLevel.BLOCK,
                    message="daily loss limit exceeded",
                    limit_value=-self._limits.daily_loss_limit,
                    actual_value=snapshot.daily_pnl,
                ))

        passed = not any(v.level == RiskLevel.BLOCK for v in violations)
        result = RiskCheckResult(
            passed=passed,
            violations=violations,
            intent_id=intent.intent_id,
            timestamp=_utcnow(),
        )

        self._emit(intent, result)
        self._log(intent, result)
        return result

    # ------------------------------------------------------------------ Helpers
    def _emit(self, intent: ExecutionIntent, result: RiskCheckResult) -> None:
        if self._bus is None:
            return
        event_type = EVT_RISK_PASSED if result.passed else EVT_RISK_BLOCKED
        try:
            self._bus.emit(
                event_type,
                intent_id=intent.intent_id,
                symbol=intent.symbol,
                side=intent.side.value,
                quantity=intent.quantity,
                estimated_price=intent.estimated_price,
                violation_codes=[v.code.value for v in result.violations],
                violations=[
                    {
                        "code": v.code.value,
                        "level": v.level.value,
                        "message": v.message,
                        "limit_value": v.limit_value,
                        "actual_value": v.actual_value,
                    }
                    for v in result.violations
                ],
            )
        except Exception as exc:
            logger.error(
                "risk_manager.emit_failed",
                intent_id=intent.intent_id,
                error=str(exc),
            )

    def _log(self, intent: ExecutionIntent, result: RiskCheckResult) -> None:
        if result.passed:
            logger.info(
                "risk_manager.passed",
                intent_id=intent.intent_id,
                symbol=intent.symbol,
                side=intent.side.value,
                quantity=intent.quantity,
            )
        else:
            logger.warning(
                "risk_manager.blocked",
                intent_id=intent.intent_id,
                symbol=intent.symbol,
                side=intent.side.value,
                quantity=intent.quantity,
                codes=[v.code.value for v in result.violations],
            )


__all__ = ["RiskManager"]
