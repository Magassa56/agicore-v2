"""Offline retrospective simulation of explicit trading risk rules."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from datetime import date
from enum import Enum
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from .analyze_trades import TradeStats, analyze_trades
from .import_nt8_csv import NormalizedTrade, import_nt8_csv
from .local_bundle import LocalBundleError, deterministic_json, publish_local_bundle, sha256_file

_WARNING = "Retrospective in-sample simulation; not proof of future profitability."


class BlockReason(str, Enum):
    """The deterministic primary reason for a blocked historical trade."""

    DAILY_LOSS_STOP = "DAILY_LOSS_STOP"
    CONSECUTIVE_LOSS_STOP = "CONSECUTIVE_LOSS_STOP"
    MAX_TRADES_REACHED = "MAX_TRADES_REACHED"
    FORBIDDEN_HOUR = "FORBIDDEN_HOUR"


@dataclass(frozen=True)
class RiskRuleConfig:
    """Explicit rules applied independently to each historical exit day."""

    daily_loss_limit: float = 300.0
    max_consecutive_losses: int = 3
    max_trades_per_day: int = 10
    forbidden_hours: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if self.daily_loss_limit <= 0:
            raise ValueError("daily_loss_limit must be greater than 0")
        if self.max_consecutive_losses < 1:
            raise ValueError("max_consecutive_losses must be at least 1")
        if self.max_trades_per_day < 1:
            raise ValueError("max_trades_per_day must be at least 1")
        hours = tuple(sorted(set(self.forbidden_hours)))
        if any(hour < 0 or hour > 23 for hour in hours):
            raise ValueError("forbidden hours must be between 0 and 23")
        object.__setattr__(self, "forbidden_hours", hours)


@dataclass(frozen=True)
class BlockedTradeDecision:
    """A blocked trade and its one deterministic primary blocking reason."""

    trade: NormalizedTrade
    reason: BlockReason
    exit_day: date


@dataclass(frozen=True)
class RiskSimulationResult:
    """The baseline, protected scenario, and reproducible simulation metadata."""

    config: RiskRuleConfig
    input_sha256: str
    rules_sha256: str
    baseline: TradeStats
    protected: TradeStats
    blocked: tuple[BlockedTradeDecision, ...]
    stopped_days: tuple[str, ...]


class RiskSimulationError(ValueError):
    """Raised when a risk simulation cannot safely produce a complete bundle."""


def create_risk_rule_simulation(
    csv_path: str | Path, output_dir: str | Path, config: RiskRuleConfig
) -> Path:
    """Simulate explicit historical rules and atomically publish its local bundle."""
    input_path = Path(csv_path).resolve()
    _validate_input_file(input_path)
    final_dir = Path(output_dir).resolve()
    if final_dir.exists():
        raise RiskSimulationError(f"Output directory already exists: {final_dir}")
    try:
        input_sha256 = sha256_file(input_path)
        trades = import_nt8_csv(input_path)
        if not trades:
            raise RiskSimulationError("CSV contains no usable trades")
        result = simulate_risk_rules(trades, config, input_sha256=input_sha256)
        files = _bundle_files(input_path.name, result)
        return publish_local_bundle(final_dir, files)
    except RiskSimulationError:
        raise
    except (LocalBundleError, OSError, ValueError) as exc:
        raise RiskSimulationError(str(exc)) from exc


def simulate_risk_rules(
    trades: list[NormalizedTrade], config: RiskRuleConfig, *, input_sha256: str = ""
) -> RiskSimulationResult:
    """Apply rules retrospectively without mutating the supplied trades."""
    baseline = analyze_trades(trades)
    executable: list[NormalizedTrade] = []
    blocked: list[BlockedTradeDecision] = []
    stopped_days: set[str] = set()
    grouped: dict[date, list[tuple[int, NormalizedTrade]]] = {}
    for index, trade in enumerate(trades):
        grouped.setdefault(trade.exit_time.date(), []).append((index, trade))

    for exit_day in sorted(grouped):
        daily_pnl = 0.0
        loss_streak = 0
        executed_today = 0
        for _, trade in sorted(
            grouped[exit_day], key=lambda item: (item[1].entry_time, item[1].exit_time, item[0])
        ):
            reason = _block_reason(config, daily_pnl, loss_streak, executed_today, trade)
            if reason is not None:
                blocked.append(BlockedTradeDecision(trade, reason, exit_day))
                stopped_days.add(exit_day.isoformat())
                continue
            executable.append(trade)
            executed_today += 1
            daily_pnl += trade.pnl
            loss_streak = loss_streak + 1 if trade.pnl <= 0 else 0

    canonical_rules = _rules_data(config)
    rules_sha256 = hashlib.sha256(
        json.dumps(canonical_rules, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return RiskSimulationResult(
        config=config,
        input_sha256=input_sha256,
        rules_sha256=rules_sha256,
        baseline=baseline,
        protected=analyze_trades(executable),
        blocked=tuple(blocked),
        stopped_days=tuple(sorted(stopped_days)),
    )


def _block_reason(
    config: RiskRuleConfig,
    daily_pnl: float,
    loss_streak: int,
    executed_today: int,
    trade: NormalizedTrade,
) -> BlockReason | None:
    if daily_pnl <= -config.daily_loss_limit:
        return BlockReason.DAILY_LOSS_STOP
    if loss_streak >= config.max_consecutive_losses:
        return BlockReason.CONSECUTIVE_LOSS_STOP
    if executed_today >= config.max_trades_per_day:
        return BlockReason.MAX_TRADES_REACHED
    if trade.entry_time.hour in config.forbidden_hours:
        return BlockReason.FORBIDDEN_HOUR
    return None


def _bundle_files(input_filename: str, result: RiskSimulationResult) -> dict[str, str]:
    summary = _summary(result)
    run_id = f"risk-sim-{result.input_sha256[:12]}-{result.rules_sha256[:8]}"
    return {
        "report.md": _report(summary),
        "summary.json": deterministic_json(summary),
        "manifest.json": deterministic_json(
            {
                "schema_version": "1.0",
                "run_id": run_id,
                "input_filename": input_filename,
                "input_sha256": result.input_sha256,
                "rules_sha256": result.rules_sha256,
                "agicore_version": _agicore_version(),
                "status": "completed",
                "generated_files": ["manifest.json", "report.md", "summary.json"],
                "warnings": [_WARNING],
            }
        ),
    }


def _summary(result: RiskSimulationResult) -> dict[str, object]:
    blocked_by_reason = Counter(decision.reason.value for decision in result.blocked)
    baseline = _stats_data(result.baseline)
    protected = _stats_data(result.protected)
    protected["executed_trades"] = result.protected.total_trades
    protected["blocked_trades"] = len(result.blocked)
    pnl_delta = result.protected.total_pnl - result.baseline.total_pnl
    return {
        "schema_version": "1.0",
        "rules": _rules_data(result.config),
        "baseline": baseline,
        "protected": protected,
        "comparison": {
            "pnl_delta": pnl_delta,
            "executed_trade_delta": result.protected.total_trades - result.baseline.total_trades,
            "blocked_historical_pnl": sum(item.trade.pnl for item in result.blocked),
            "blocked_by_reason": {
                reason.value: blocked_by_reason[reason.value] for reason in BlockReason
            },
            "stopped_days": list(result.stopped_days),
            "outcome": "improved" if pnl_delta > 0 else "worsened" if pnl_delta < 0 else "unchanged",
        },
    }


def _rules_data(config: RiskRuleConfig) -> dict[str, object]:
    return {
        "daily_loss_limit": float(config.daily_loss_limit),
        "max_consecutive_losses": config.max_consecutive_losses,
        "max_trades_per_day": config.max_trades_per_day,
        "forbidden_hours": list(config.forbidden_hours),
    }


def _stats_data(stats: TradeStats) -> dict[str, object]:
    return {
        "total_trades": stats.total_trades,
        "total_pnl": stats.total_pnl,
        "win_rate": stats.win_rate,
        "average_trade": stats.average_trade,
        "largest_gain": stats.largest_gain,
        "largest_loss": stats.largest_loss,
        "max_consecutive_losses": stats.max_consecutive_losses,
        "worst_day_pnl": min(stats.pnl_by_day.values(), default=0.0),
    }


def _report(summary: dict[str, object]) -> str:
    rules = summary["rules"]
    baseline = summary["baseline"]
    protected = summary["protected"]
    comparison = summary["comparison"]
    assert isinstance(rules, dict) and isinstance(baseline, dict)
    assert isinstance(protected, dict) and isinstance(comparison, dict)
    reasons = comparison["blocked_by_reason"]
    assert isinstance(reasons, dict)
    lines = [
        "# Historical Risk Rule Simulation",
        "",
        f"> Warning: {_WARNING}",
        "",
        "## Rules Tested",
        "",
        f"- Daily loss limit: {rules['daily_loss_limit']:.2f}",
        f"- Max consecutive losses: {rules['max_consecutive_losses']}",
        f"- Max trades per day: {rules['max_trades_per_day']}",
        f"- Forbidden hours: {', '.join(map(str, rules['forbidden_hours'])) or 'none'}",
        "",
        "## Baseline vs Protected Scenario",
        "",
        "| Metric | Baseline | Protected |",
        "| --- | ---: | ---: |",
        f"| Total PnL | {baseline['total_pnl']:.2f} | {protected['total_pnl']:.2f} |",
        f"| Total trades | {baseline['total_trades']} | {protected['executed_trades']} |",
        f"| Win rate | {baseline['win_rate']:.2%} | {protected['win_rate']:.2%} |",
        f"| Worst day PnL | {baseline['worst_day_pnl']:.2f} | {protected['worst_day_pnl']:.2f} |",
        "",
        "## Comparison",
        "",
        f"- PnL delta: {comparison['pnl_delta']:.2f}",
        f"- Executed trades: {protected['executed_trades']}",
        f"- Blocked trades: {protected['blocked_trades']}",
        f"- Blocked historical PnL: {comparison['blocked_historical_pnl']:.2f}",
        f"- Stopped days: {', '.join(comparison['stopped_days']) or 'none'}",
        "",
        "## Block Reasons",
        "",
        *[f"- {reason}: {count}" for reason, count in reasons.items()],
        "",
        f"## Neutral Outcome: {comparison['outcome']}",
        "",
    ]
    return "\n".join(lines)


def _validate_input_file(path: Path) -> None:
    if not path.exists():
        raise RiskSimulationError(f"CSV file not found: {path}")
    if not path.is_file():
        raise RiskSimulationError(f"CSV path is not a file: {path}")


def _agicore_version() -> str:
    try:
        return version("agicore")
    except PackageNotFoundError:
        return "unknown"


__all__ = [
    "BlockReason",
    "BlockedTradeDecision",
    "RiskRuleConfig",
    "RiskSimulationError",
    "RiskSimulationResult",
    "create_risk_rule_simulation",
    "simulate_risk_rules",
]
