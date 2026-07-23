"""Deterministic local bundle generation for explicit NinjaTrader CSV analysis."""
from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from .analyze_trades import TradeStats, analyze_trades
from .import_nt8_csv import import_nt8_csv
from .local_bundle import LocalBundleError, deterministic_json, publish_local_bundle, sha256_file
from .report import generate_markdown_report
from .risk_guard import RiskGuardResult, evaluate_risk


class AnalysisRunError(ValueError):
    """Raised when an analysis run cannot safely produce a complete bundle."""


def create_analysis_run(csv_path: str | Path, output_dir: str | Path) -> Path:
    """Create a complete, deterministic analysis bundle from an explicit CSV file.

    The final directory is created only after the CSV was successfully analyzed
    and all bundle files have been written to a neighboring temporary directory.
    """
    input_path = Path(csv_path).resolve()
    final_dir = Path(output_dir).resolve()
    _validate_input_file(input_path)
    if final_dir.exists():
        raise AnalysisRunError(f"Output directory already exists: {final_dir}")

    try:
        input_sha256 = sha256_file(input_path)
        trades = import_nt8_csv(input_path)
        if not trades:
            raise AnalysisRunError("CSV contains no usable trades")
        stats = analyze_trades(trades)
        risk = evaluate_risk(stats)
        files = _bundle_files(input_path.name, input_sha256, stats, risk)
    except AnalysisRunError:
        raise
    except (OSError, ValueError) as exc:
        raise AnalysisRunError(f"Unable to analyze CSV: {exc}") from exc

    try:
        return publish_local_bundle(final_dir, files)
    except LocalBundleError as exc:
        raise AnalysisRunError(str(exc)) from exc


def _validate_input_file(path: Path) -> None:
    if not path.exists():
        raise AnalysisRunError(f"CSV file not found: {path}")
    if not path.is_file():
        raise AnalysisRunError(f"CSV path is not a file: {path}")


def _bundle_files(
    input_filename: str,
    input_sha256: str,
    stats: TradeStats,
    risk: RiskGuardResult,
) -> dict[str, str]:
    return {
        "report.md": generate_markdown_report(stats, risk),
        "summary.json": deterministic_json(_summary(stats, risk)),
        "manifest.json": deterministic_json(
            {
                "schema_version": "1.0",
                "run_id": f"analysis-{input_sha256[:12]}",
                "input_filename": input_filename,
                "input_sha256": input_sha256,
                "agicore_version": _agicore_version(),
                "status": "completed",
                "generated_files": ["manifest.json", "report.md", "summary.json"],
                "warnings": [],
            }
        ),
    }


def _summary(stats: TradeStats, risk: RiskGuardResult) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "total_trades": stats.total_trades,
        "total_pnl": stats.total_pnl,
        "win_rate": stats.win_rate,
        "average_trade": stats.average_trade,
        "largest_gain": stats.largest_gain,
        "largest_loss": stats.largest_loss,
        "max_consecutive_losses": stats.max_consecutive_losses,
        "average_mae": stats.average_mae,
        "average_mfe": stats.average_mfe,
        "risk_alerts": [
            {"kind": alert.kind, "severity": alert.severity, "message": alert.message}
            for alert in risk.alerts
        ],
        "apex_rules": risk.apex_rules,
        "worst_days": risk.worst_days,
        "worst_hours": risk.worst_hours,
    }


def _agicore_version() -> str:
    try:
        return version("agicore")
    except PackageNotFoundError:
        return "unknown"


__all__ = ["AnalysisRunError", "create_analysis_run"]
