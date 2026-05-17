"""Offline playbook helpers for declared trader behavior."""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .analyze_trades import TradeStats
from .playbook_models import PlaybookCheck, PlaybookComparison, RiskRules, TraderProfile


def create_trader_profile(
    *,
    name: str,
    style_detected: str,
    entry_conditions: list[str] | tuple[str, ...] = (),
    exit_conditions: list[str] | tuple[str, ...] = (),
    forbidden_conditions: list[str] | tuple[str, ...] = (),
    risk_rules: RiskRules | None = None,
    notes: str | None = None,
) -> TraderProfile:
    """Create a normalized trader profile dataclass."""
    if not name.strip():
        raise ValueError("Trader profile name is required")
    if not style_detected.strip():
        raise ValueError("Trader profile style_detected is required")
    return TraderProfile(
        name=name.strip(),
        style_detected=style_detected.strip(),
        entry_conditions=_clean_conditions(entry_conditions),
        exit_conditions=_clean_conditions(exit_conditions),
        forbidden_conditions=_clean_conditions(forbidden_conditions),
        risk_rules=risk_rules or RiskRules(),
        notes=notes.strip() if notes else None,
    )


def save_playbook(profile: TraderProfile, path: str | Path) -> None:
    """Save a trader playbook as simple JSON."""
    payload = asdict(profile)
    json_path = Path(path)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def load_playbook(path: str | Path) -> TraderProfile:
    """Load a trader playbook from simple JSON."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    risk_payload = payload.get("risk_rules") or {}
    return create_trader_profile(
        name=payload["name"],
        style_detected=payload["style_detected"],
        entry_conditions=payload.get("entry_conditions", ()),
        exit_conditions=payload.get("exit_conditions", ()),
        forbidden_conditions=payload.get("forbidden_conditions", ()),
        risk_rules=RiskRules(
            max_daily_loss=risk_payload.get("max_daily_loss"),
            max_trades_per_day=risk_payload.get("max_trades_per_day"),
            max_consecutive_losses=risk_payload.get("max_consecutive_losses"),
            forbidden_hours=tuple(risk_payload.get("forbidden_hours") or ()),
            minimum_win_rate=risk_payload.get("minimum_win_rate"),
            minimum_average_trade=risk_payload.get("minimum_average_trade"),
        ),
        notes=payload.get("notes"),
    )


def compare_playbook_to_stats(
    profile: TraderProfile,
    stats: TradeStats,
) -> PlaybookComparison:
    """Compare declared playbook risk rules to aggregate trading statistics."""
    checks: list[PlaybookCheck] = []
    rules = profile.risk_rules

    if rules.max_daily_loss is not None:
        worst_day = min(stats.pnl_by_day.values(), default=0.0)
        checks.append(
            _check(
                rule="max_daily_loss",
                passed=worst_day >= -abs(rules.max_daily_loss),
                expected=f">= {-abs(rules.max_daily_loss):.2f}",
                actual=f"{worst_day:.2f}",
                fail_message="Worst realized day breached the declared loss limit",
            )
        )

    if rules.max_trades_per_day is not None:
        busiest_day = max(stats.trades_by_day.values(), default=0)
        checks.append(
            _check(
                rule="max_trades_per_day",
                passed=busiest_day <= rules.max_trades_per_day,
                expected=f"<= {rules.max_trades_per_day}",
                actual=str(busiest_day),
                fail_message="Realized trade count exceeded the declared daily limit",
            )
        )

    if rules.max_consecutive_losses is not None:
        checks.append(
            _check(
                rule="max_consecutive_losses",
                passed=stats.max_consecutive_losses <= rules.max_consecutive_losses,
                expected=f"<= {rules.max_consecutive_losses}",
                actual=str(stats.max_consecutive_losses),
                fail_message="Loss streak exceeded the declared playbook limit",
            )
        )

    if rules.forbidden_hours:
        traded_forbidden_hours = tuple(
            hour for hour in sorted(rules.forbidden_hours) if hour in stats.pnl_by_hour
        )
        checks.append(
            _check(
                rule="forbidden_hours",
                passed=not traded_forbidden_hours,
                expected=", ".join(f"{hour:02d}:00" for hour in rules.forbidden_hours),
                actual=_format_hours(traded_forbidden_hours),
                fail_message="Trades were detected during forbidden hours",
            )
        )

    if rules.minimum_win_rate is not None:
        checks.append(
            _check(
                rule="minimum_win_rate",
                passed=stats.win_rate >= rules.minimum_win_rate,
                expected=f">= {rules.minimum_win_rate:.2%}",
                actual=f"{stats.win_rate:.2%}",
                fail_message="Realized win rate is below the declared minimum",
            )
        )

    if rules.minimum_average_trade is not None:
        checks.append(
            _check(
                rule="minimum_average_trade",
                passed=stats.average_trade >= rules.minimum_average_trade,
                expected=f">= {rules.minimum_average_trade:.2f}",
                actual=f"{stats.average_trade:.2f}",
                fail_message="Realized average trade is below the declared minimum",
            )
        )

    failed_checks = sum(1 for check in checks if check.status == "fail")
    return PlaybookComparison(
        profile_name=profile.name,
        style_detected=profile.style_detected,
        total_checks=len(checks),
        passed_checks=len(checks) - failed_checks,
        failed_checks=failed_checks,
        checks=tuple(checks),
    )


def _check(
    *,
    rule: str,
    passed: bool,
    expected: str,
    actual: str,
    fail_message: str,
) -> PlaybookCheck:
    return PlaybookCheck(
        rule=rule,
        expected=expected,
        actual=actual,
        status="pass" if passed else "fail",
        message="Rule respected" if passed else fail_message,
    )


def _clean_conditions(values: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    return tuple(value.strip() for value in values if value.strip())


def _format_hours(hours: tuple[int, ...]) -> str:
    if not hours:
        return "none"
    return ", ".join(f"{hour:02d}:00" for hour in hours)


__all__ = [
    "compare_playbook_to_stats",
    "create_trader_profile",
    "load_playbook",
    "save_playbook",
]
