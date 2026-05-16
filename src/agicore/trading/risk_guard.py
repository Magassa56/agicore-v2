"""Simple risk guardrails for offline trading analysis."""
from __future__ import annotations

from dataclasses import dataclass, field

from .analyze_trades import TradeStats


@dataclass(frozen=True)
class RiskGuardConfig:
    destructive_day_loss: float = -500.0
    daily_loss_limit: float = -300.0
    max_trades_per_day: int = 10
    dangerous_hour_loss: float = -150.0
    max_consecutive_losses: int = 3


@dataclass(frozen=True)
class RiskAlert:
    kind: str
    message: str
    severity: str = "warning"


@dataclass(frozen=True)
class RiskGuardResult:
    alerts: list[RiskAlert] = field(default_factory=list)
    apex_rules: list[str] = field(default_factory=list)
    worst_days: list[str] = field(default_factory=list)
    worst_hours: list[int] = field(default_factory=list)


def evaluate_risk(stats: TradeStats, config: RiskGuardConfig | None = None) -> RiskGuardResult:
    """Detect destructive patterns and propose simple Apex-compatible rules."""
    cfg = config or RiskGuardConfig()
    alerts: list[RiskAlert] = []

    destructive_days = [
        day for day, pnl in stats.pnl_by_day.items() if pnl <= cfg.destructive_day_loss
    ]
    excessive_loss_days = [
        day for day, pnl in stats.pnl_by_day.items() if pnl <= cfg.daily_loss_limit
    ]
    overtrading_days = [
        day for day, count in stats.trades_by_day.items() if count > cfg.max_trades_per_day
    ]
    dangerous_hours = [
        hour for hour, pnl in stats.pnl_by_hour.items() if pnl <= cfg.dangerous_hour_loss
    ]

    for day in sorted(destructive_days):
        alerts.append(
            RiskAlert(
                kind="destructive_day",
                message=f"Destructive day detected on {day.isoformat()}",
                severity="critical",
            )
        )
    for day in sorted(excessive_loss_days):
        alerts.append(
            RiskAlert(
                kind="daily_loss",
                message=f"Daily loss limit breached on {day.isoformat()}",
                severity="critical",
            )
        )
    for day in sorted(overtrading_days):
        alerts.append(
            RiskAlert(
                kind="overtrading",
                message=f"Overtrading detected on {day.isoformat()}",
            )
        )
    for hour in sorted(dangerous_hours):
        alerts.append(
            RiskAlert(
                kind="dangerous_hour",
                message=f"Dangerous trading hour detected at {hour:02d}:00",
            )
        )
    if stats.max_consecutive_losses >= cfg.max_consecutive_losses:
        alerts.append(
            RiskAlert(
                kind="loss_streak",
                message=(
                    "Dangerous consecutive loss streak detected: "
                    f"{stats.max_consecutive_losses}"
                ),
                severity="critical",
            )
        )

    apex_rules = [
        f"Stop trading after {abs(cfg.daily_loss_limit):.2f} daily loss",
        f"Stop trading after {cfg.max_consecutive_losses} consecutive losses",
        f"Max {cfg.max_trades_per_day} trades per day",
    ]
    if dangerous_hours:
        hours = ", ".join(f"{hour:02d}:00" for hour in sorted(dangerous_hours))
        apex_rules.append(f"Avoid worst trading hours: {hours}")

    return RiskGuardResult(
        alerts=alerts,
        apex_rules=apex_rules,
        worst_days=[day.isoformat() for day in sorted(excessive_loss_days)],
        worst_hours=sorted(dangerous_hours),
    )


__all__ = ["RiskAlert", "RiskGuardConfig", "RiskGuardResult", "evaluate_risk"]
