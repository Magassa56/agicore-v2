"""AppSettings — Phase 8E.

Centralized configuration loaded from environment variables with sane
defaults. All fields are plain Python types; no Pydantic required.

Usage
-----
>>> from agicore.config.settings import AppSettings
>>> cfg = AppSettings.from_env()
>>> cfg.db_url
'sqlite:///:memory:'
"""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class AppSettings:
    """Runtime settings for AGIcore-v2.

    Attributes
    ----------
    db_url : str
        SQLAlchemy database URL. Default: sqlite in-memory.
    log_level : str
        Logging level (DEBUG / INFO / WARNING / ERROR). Default: INFO.
    log_json : bool
        Emit JSON-structured logs when True. Default: True.
    poll_interval : float
        Execution loop poll interval in seconds. Default: 0.5.
    batch_size : int
        Tasks per execution-loop cycle. Default: 10.
    max_retry_attempts : int
        Maximum retry attempts per task. Default: 3.
    initial_retry_delay : float
        Initial backoff delay in seconds. Default: 0.1.
    dryrun : bool
        Enable dry-run mode (no side effects). Default: False.
    """

    db_url: str = "sqlite:///:memory:"
    log_level: str = "INFO"
    log_json: bool = True
    poll_interval: float = 0.5
    batch_size: int = 10
    max_retry_attempts: int = 3
    initial_retry_delay: float = 0.1
    dryrun: bool = False

    @classmethod
    def from_env(cls) -> "AppSettings":
        """Construct settings from environment variables.

        Each field maps to ``AGICORE_<UPPERCASE_FIELD_NAME>``.
        Missing variables fall back to the field defaults above.
        """
        return cls(
            db_url=os.getenv("AGICORE_DB_URL", "sqlite:///:memory:"),
            log_level=os.getenv("AGICORE_LOG_LEVEL", "INFO"),
            log_json=os.getenv("AGICORE_LOG_JSON", "true").lower() == "true",
            poll_interval=float(os.getenv("AGICORE_POLL_INTERVAL", "0.5")),
            batch_size=int(os.getenv("AGICORE_BATCH_SIZE", "10")),
            max_retry_attempts=int(os.getenv("AGICORE_MAX_RETRY", "3")),
            initial_retry_delay=float(os.getenv("AGICORE_RETRY_DELAY", "0.1")),
            dryrun=os.getenv("AGICORE_DRYRUN", "false").lower() == "true",
        )


__all__ = ["AppSettings"]
