"""AGIcore-v2 CLI — Phase 9B.

Entry point for the agicore command-line interface.

Commands
--------
version   Print the current AGIcore-v2 version.
run       Initialise and start the AGIcore runtime (blocking).

Usage
-----
$ agicore version
$ agicore run --db-url sqlite:///agicore.db --log-level DEBUG
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _default_analysis_output(csv_path: Path) -> Path:
    return Path("reports") / "local" / f"{csv_path.stem}-analysis.md"


def _write_text_atomically(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.tmp")
    try:
        tmp_path.write_text(content, encoding="utf-8")
        tmp_path.replace(path)
    except OSError:
        try:
            if tmp_path.exists():
                tmp_path.unlink()
        finally:
            raise


def _run_trading_analyze(
    csv_arg: str, output_arg: str | None, output_dir_arg: str | None
) -> int:
    if output_dir_arg:
        try:
            from agicore.trading.analysis_run import AnalysisRunError, create_analysis_run

            bundle_dir = create_analysis_run(csv_arg, output_dir_arg)
        except AnalysisRunError as exc:
            sys.stderr.write(f"error: {exc}\n")
            return 2
        sys.stdout.write(f"Trading analysis bundle written to: {bundle_dir}\n")
        return 0

    csv_path = Path(csv_arg).resolve()
    if not csv_path.exists():
        sys.stderr.write(f"error: CSV file not found: {csv_path}\n")
        return 2
    if not csv_path.is_file():
        sys.stderr.write(f"error: CSV path is not a file: {csv_path}\n")
        return 2

    try:
        from agicore.trading.analyze_trades import analyze_trades
        from agicore.trading.import_nt8_csv import import_nt8_csv
        from agicore.trading.report import generate_markdown_report
        from agicore.trading.risk_guard import evaluate_risk

        trades = import_nt8_csv(csv_path)
        if not trades:
            sys.stderr.write(f"error: CSV contains no usable trades: {csv_path}\n")
            return 2
        stats = analyze_trades(trades)
        risk = evaluate_risk(stats)
        report = generate_markdown_report(stats, risk)
    except (OSError, ValueError) as exc:
        sys.stderr.write(f"error: unable to analyze CSV: {exc}\n")
        return 2

    output_path = Path(output_arg).resolve() if output_arg else _default_analysis_output(csv_path)
    try:
        _write_text_atomically(output_path, report)
    except OSError as exc:
        sys.stderr.write(f"error: unable to write report: {exc}\n")
        return 2

    sys.stdout.write(f"Trading analysis report written to: {output_path}\n")
    return 0


def _run_trading_simulate_risk(args: argparse.Namespace) -> int:
    try:
        from agicore.trading.risk_rule_simulator import (
            RiskRuleConfig,
            RiskSimulationError,
            create_risk_rule_simulation,
        )

        config = RiskRuleConfig(
            daily_loss_limit=args.daily_loss_limit,
            max_consecutive_losses=args.max_consecutive_losses,
            max_trades_per_day=args.max_trades_per_day,
            forbidden_hours=tuple(args.forbid_hour or []),
        )
        bundle_dir = create_risk_rule_simulation(args.csv, args.output_dir, config)
    except (RiskSimulationError, ValueError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2
    sys.stdout.write(f"Historical risk simulation bundle written to: {bundle_dir}\n")
    return 0


def _run_trading_replay_market(args: argparse.Namespace) -> int:
    try:
        from agicore.trading.market_replay import (
            MarketReplayConfig,
            MarketReplayError,
            create_market_replay,
        )

        bundle_dir = create_market_replay(
            args.csv,
            args.output_dir,
            MarketReplayConfig(
                fast_ema=args.fast_ema,
                slow_ema=args.slow_ema,
                round_trip_cost_points=args.round_trip_cost_points,
            ),
        )
    except (MarketReplayError, ValueError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2
    sys.stdout.write(f"Historical market replay bundle written to: {bundle_dir}\n")
    return 0


def _run_trading_diagnose_replay(args: argparse.Namespace) -> int:
    try:
        from agicore.trading.market_replay import MarketReplayConfig
        from agicore.trading.replay_diagnostics import ReplayDiagnosticsConfig, ReplayDiagnosticsError, create_replay_diagnostics

        bundle_dir = create_replay_diagnostics(args.csv, args.output_dir, MarketReplayConfig(args.fast_ema, args.slow_ema, args.round_trip_cost_points), ReplayDiagnosticsConfig(args.rolling_window_trades))
    except (ReplayDiagnosticsError, ValueError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2
    sys.stdout.write(f"Replay diagnostics bundle written to: {bundle_dir}\n")
    return 0


def _run_trading_performance_gate(args: argparse.Namespace) -> int:
    try:
        from agicore.trading.market_replay import MarketReplayConfig
        from agicore.trading.performance_gate import PerformanceGateConfig, PerformanceGateError, create_performance_gate
        bundle_dir = create_performance_gate(args.csv, args.output_dir, MarketReplayConfig(args.fast_ema, args.slow_ema, args.round_trip_cost_points), PerformanceGateConfig(args.gate_window_trades))
    except (PerformanceGateError, ValueError) as exc:
        sys.stderr.write(f"error: {exc}\n"); return 2
    sys.stdout.write(f"Causal performance gate bundle written to: {bundle_dir}\n"); return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agicore",
        description="AGIcore-v2 — multi-agent World Model orchestrator CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ── version ──────────────────────────────────────────────────────────────
    sub.add_parser("version", help="Print AGIcore-v2 version and exit.")

    # ── run ──────────────────────────────────────────────────────────────────
    run_p = sub.add_parser("run", help="Start the AGIcore runtime.")
    run_p.add_argument(
        "--db-url",
        default="sqlite:///:memory:",
        help="SQLAlchemy database URL (default: sqlite:///:memory:).",
    )
    run_p.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO).",
    )
    run_p.add_argument(
        "--dryrun",
        action="store_true",
        help="Start in dry-run mode (no side effects).",
    )

    trading_p = sub.add_parser("trading", help="Offline trading utilities.")
    trading_sub = trading_p.add_subparsers(dest="trading_command", required=True)
    analyze_p = trading_sub.add_parser(
        "analyze",
        help="Analyze an explicit local NinjaTrader CSV export offline.",
    )
    analyze_p.add_argument("csv", help="Path to the local NinjaTrader CSV export.")
    output_group = analyze_p.add_mutually_exclusive_group()
    output_group.add_argument(
        "--output",
        help=(
            "Markdown report path. Defaults to "
            "reports/local/<csv-name>-analysis.md."
        ),
    )

    simulate_p = trading_sub.add_parser(
        "simulate-risk", help="Simulate explicit offline risk rules on a local CSV export."
    )
    simulate_p.add_argument("csv", help="Path to the local NinjaTrader CSV export.")
    simulate_p.add_argument("--output-dir", required=True, help="New directory for the simulation bundle.")
    simulate_p.add_argument("--daily-loss-limit", type=float, default=300.0)
    simulate_p.add_argument("--max-consecutive-losses", type=int, default=3)
    simulate_p.add_argument("--max-trades-per-day", type=int, default=10)
    simulate_p.add_argument("--forbid-hour", type=int, action="append", default=[])
    replay_p = trading_sub.add_parser(
        "replay-market", help="Replay an explicit local OHLCV CSV with EMA crossover."
    )
    replay_p.add_argument("csv", help="Path to the local OHLCV CSV file.")
    replay_p.add_argument("--output-dir", required=True, help="New directory for the replay bundle.")
    replay_p.add_argument("--fast-ema", type=int, default=19)
    replay_p.add_argument("--slow-ema", type=int, default=50)
    replay_p.add_argument("--round-trip-cost-points", type=float, default=0.0)
    diagnose_p = trading_sub.add_parser("diagnose-replay", help="Describe an explicit local EMA replay by regime and period.")
    diagnose_p.add_argument("csv", help="Path to the local OHLCV CSV file.")
    diagnose_p.add_argument("--output-dir", required=True)
    diagnose_p.add_argument("--fast-ema", type=int, default=19)
    diagnose_p.add_argument("--slow-ema", type=int, default=50)
    diagnose_p.add_argument("--round-trip-cost-points", type=float, default=0.0)
    diagnose_p.add_argument("--rolling-window-trades", type=int, default=100)
    gate_p = trading_sub.add_parser("replay-performance-gate", help="Replay EMA with a causal trailing shadow-performance gate.")
    gate_p.add_argument("csv"); gate_p.add_argument("--output-dir", required=True)
    gate_p.add_argument("--fast-ema", type=int, default=19); gate_p.add_argument("--slow-ema", type=int, default=50)
    gate_p.add_argument("--round-trip-cost-points", type=float, default=0.0); gate_p.add_argument("--gate-window-trades", type=int, default=100)
    output_group.add_argument(
        "--output-dir",
        help="Directory in which to create the complete local analysis bundle.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.

    Returns
    -------
    int
        Exit code (0 = success, non-zero = error).
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "version":
        sys.stdout.write("agicore-v2 0.1.0-phase9c\n")
        return 0

    if args.command == "run":
        from agicore.config.settings import AppSettings
        from agicore.manager.manager_models import ManagerConfig
        from agicore.manager.agicore_manager import AGIcoreManager

        settings = AppSettings(
            db_url=args.db_url,
            log_level=args.log_level,
            dryrun=args.dryrun,
        )
        cfg = ManagerConfig(
            manager_id="cli-runtime",
            runtime_mode="SANDBOX",
        )
        mgr = AGIcoreManager(config=cfg)
        try:
            mgr.start()
            sys.stdout.write(
                f"AGIcore runtime started (mode={cfg.runtime_mode}, "
                f"dryrun={settings.dryrun}). Press Ctrl+C to stop.\n"
            )
            import signal
            signal.pause()
        except KeyboardInterrupt:
            pass
        finally:
            mgr.stop()
        return 0

    if args.command == "trading" and args.trading_command == "analyze":
        return _run_trading_analyze(args.csv, args.output, args.output_dir)

    if args.command == "trading" and args.trading_command == "simulate-risk":
        return _run_trading_simulate_risk(args)

    if args.command == "trading" and args.trading_command == "replay-market":
        return _run_trading_replay_market(args)

    if args.command == "trading" and args.trading_command == "diagnose-replay":
        return _run_trading_diagnose_replay(args)
    if args.command == "trading" and args.trading_command == "replay-performance-gate":
        return _run_trading_performance_gate(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
