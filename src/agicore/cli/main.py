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
        print("agicore-v2 0.1.0-phase9c")
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
            print(
                f"AGIcore runtime started (mode={cfg.runtime_mode}, "
                f"dryrun={settings.dryrun}). Press Ctrl+C to stop."
            )
            import signal
            signal.pause()
        except KeyboardInterrupt:
            pass
        finally:
            mgr.stop()
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
