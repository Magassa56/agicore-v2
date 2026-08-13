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

def _run_trading_breakout(args: argparse.Namespace) -> int:
    try:
        from agicore.trading.breakout_replay import BreakoutReplayConfig, BreakoutReplayError, create_breakout_replay
        bundle=create_breakout_replay(args.csv,args.output_dir,BreakoutReplayConfig(args.lookback_bars,args.round_trip_cost_points))
    except (BreakoutReplayError,ValueError) as exc: sys.stderr.write(f"error: {exc}\n"); return 2
    sys.stdout.write(f"Causal breakout replay bundle written to: {bundle}\n"); return 0


def _run_trading_resample_ohlcv(args: argparse.Namespace) -> int:
    try:
        from agicore.trading.ohlcv_resampler import OHLCVResamplerError, resample_ohlcv
        output = resample_ohlcv(args.csv, args.output, args.minutes)
    except OHLCVResamplerError as exc:
        sys.stderr.write(f"error: {exc}\n"); return 2
    sys.stdout.write(f"Resampled OHLCV written to: {output}\n"); return 0

def _run_trading_study_breakout(args: argparse.Namespace) -> int:
    try:
        from agicore.trading.multitimeframe_breakout_study import MultiTimeframeStudyError, create_multitimeframe_breakout_study
        output=create_multitimeframe_breakout_study(args.csv,args.output_dir,args.round_trip_cost_points,args.side_policy,_breakout_cost_model(args))
    except (MultiTimeframeStudyError,ValueError) as exc: sys.stderr.write(f"error: {exc}\n"); return 2
    sys.stdout.write(f"Multi-timeframe breakout study written to: {output}\n"); return 0

def _run_trading_study_breakout_stability(args: argparse.Namespace) -> int:
    try:
        from agicore.trading.multitimeframe_breakout_stability import MultiTimeframeStabilityError, create_multitimeframe_breakout_stability_study
        output=create_multitimeframe_breakout_stability_study(args.csv,args.output_dir,round_trip_cost_points=args.round_trip_cost_points,window_bars=args.window_bars,execution_cost_model=_breakout_cost_model(args))
    except (MultiTimeframeStabilityError,ValueError) as exc: sys.stderr.write(f"error: {exc}\n"); return 2
    sys.stdout.write(f"Multi-timeframe breakout stability study written to: {output}\n"); return 0

def _run_trading_study_breakout_walk_forward(args: argparse.Namespace) -> int:
    try:
        from agicore.trading.walk_forward_breakout import WalkForwardBreakoutError, create_walk_forward_breakout_study
        output=create_walk_forward_breakout_study(args.csv,args.output_dir,initial_train_bars=args.initial_train_bars,validation_bars=args.validation_bars,oos_bars=args.oos_bars,lookback_bars=args.lookback_bars,round_trip_cost_points=args.round_trip_cost_points,side_policy=args.side_policy,execution_cost_model=_breakout_cost_model(args))
    except (WalkForwardBreakoutError,ValueError) as exc: sys.stderr.write(f"error: {exc}\n"); return 2
    sys.stdout.write(f"Breakout walk-forward study written to: {output}\n"); return 0

def _run_trading_study_breakout_temporal_oos(args: argparse.Namespace) -> int:
    try:
        from agicore.trading.temporal_breakout_oos import TemporalBreakoutOOSError, create_temporal_breakout_oos_study
        output=create_temporal_breakout_oos_study(args.csv,args.output_dir,lookback_bars=args.lookback_bars,round_trip_cost_points=args.round_trip_cost_points,side_policy=args.side_policy,train_ratio=args.train_ratio,validation_ratio=args.validation_ratio,oos_ratio=args.oos_ratio,execution_cost_model=_breakout_cost_model(args))
    except (TemporalBreakoutOOSError,ValueError) as exc: sys.stderr.write(f"error: {exc}\n"); return 2
    sys.stdout.write(f"Temporal breakout train/validation/OOS study written to: {output}\n"); return 0

def _breakout_cost_model(args: argparse.Namespace):
    names=("cost_scenario","cost_instrument","cost_currency","point_value","commission_per_side","spread_points","entry_slippage_points","exit_slippage_points")
    supplied=[name for name in names if getattr(args,name,None) is not None]
    if not supplied: return None
    missing=[name for name in names if getattr(args,name,None) is None]
    if missing: raise ValueError("Detailed execution cost requires all options: "+", ".join("--"+name.replace("_","-") for name in missing))
    from agicore.trading.breakout_execution_costs import BreakoutExecutionCostModel
    return BreakoutExecutionCostModel(args.cost_scenario,args.cost_instrument,args.cost_currency,args.point_value,args.commission_per_side,args.spread_points,args.entry_slippage_points,args.exit_slippage_points)


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
    breakout_p=trading_sub.add_parser("replay-breakout",help="Replay a causal prior-bar price-channel breakout.")
    breakout_p.add_argument("csv"); breakout_p.add_argument("--output-dir",required=True); breakout_p.add_argument("--lookback-bars",type=int,default=240); breakout_p.add_argument("--round-trip-cost-points",type=float,default=1.0)
    resample_p = trading_sub.add_parser("resample-ohlcv", help="Resample explicit one-minute OHLCV into complete buckets.")
    resample_p.add_argument("csv"); resample_p.add_argument("--output", required=True); resample_p.add_argument("--minutes", type=int, required=True)
    study_p=trading_sub.add_parser("study-breakout-timeframes",help="Study pre-registered breakout timeframes offline.")
    study_p.add_argument("csv",nargs="+"); study_p.add_argument("--output-dir",required=True); study_p.add_argument("--round-trip-cost-points",type=float,default=1.0); study_p.add_argument("--side-policy",choices=("BOTH","LONG_ONLY","SHORT_ONLY"),default="BOTH")
    stability_p=trading_sub.add_parser("study-breakout-stability",help="Study chronological breakout stability across pre-registered timeframes.")
    stability_p.add_argument("csv",nargs="+"); stability_p.add_argument("--output-dir",required=True); stability_p.add_argument("--round-trip-cost-points",type=float,default=1.0); stability_p.add_argument("--window-bars",type=int,required=True)
    walk_p=trading_sub.add_parser("study-breakout-walk-forward",help="Evaluate a fixed breakout in explicit expanding walk-forward folds.")
    walk_p.add_argument("csv"); walk_p.add_argument("--output-dir",required=True); walk_p.add_argument("--initial-train-bars",type=int,required=True); walk_p.add_argument("--validation-bars",type=int,required=True); walk_p.add_argument("--oos-bars",type=int,required=True); walk_p.add_argument("--lookback-bars",type=int,default=240); walk_p.add_argument("--round-trip-cost-points",type=float,default=1.0); walk_p.add_argument("--side-policy",choices=("BOTH","LONG_ONLY","SHORT_ONLY"),default="BOTH")
    temporal_p=trading_sub.add_parser("study-breakout-temporal-oos",help="Replay breakout in strict train, validation, and OOS segments.")
    temporal_p.add_argument("csv"); temporal_p.add_argument("--output-dir",required=True); temporal_p.add_argument("--lookback-bars",type=int,default=240); temporal_p.add_argument("--round-trip-cost-points",type=float,default=1.0); temporal_p.add_argument("--side-policy",choices=("BOTH","LONG_ONLY","SHORT_ONLY"),default="BOTH"); temporal_p.add_argument("--train-ratio",type=float,default=0.6); temporal_p.add_argument("--validation-ratio",type=float,default=0.2); temporal_p.add_argument("--oos-ratio",type=float,default=0.2)
    for cost_parser in (study_p,stability_p,walk_p,temporal_p):
        cost_parser.add_argument("--cost-scenario"); cost_parser.add_argument("--cost-instrument"); cost_parser.add_argument("--cost-currency")
        cost_parser.add_argument("--point-value",type=float); cost_parser.add_argument("--commission-per-side",type=float); cost_parser.add_argument("--spread-points",type=float); cost_parser.add_argument("--entry-slippage-points",type=float); cost_parser.add_argument("--exit-slippage-points",type=float)
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
    if args.command == "trading" and args.trading_command == "replay-breakout":
        return _run_trading_breakout(args)
    if args.command == "trading" and args.trading_command == "resample-ohlcv":
        return _run_trading_resample_ohlcv(args)
    if args.command == "trading" and args.trading_command == "study-breakout-timeframes":
        return _run_trading_study_breakout(args)
    if args.command == "trading" and args.trading_command == "study-breakout-stability":
        return _run_trading_study_breakout_stability(args)
    if args.command == "trading" and args.trading_command == "study-breakout-walk-forward":
        return _run_trading_study_breakout_walk_forward(args)
    if args.command == "trading" and args.trading_command == "study-breakout-temporal-oos":
        return _run_trading_study_breakout_temporal_oos(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
