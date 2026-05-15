"""DryRunPolicyEnforcer — Phase 9A.

Validates a DryRunConfig against safety rules before a session can start.

Rules enforced
--------------
1. Adapter name must not contain any forbidden substring
   (live, prod, real, capital). Only paper/sandbox adapters are permitted.
2. tick_interval_ms must be >= 0.
"""
from __future__ import annotations

from typing import Any

from agicore.dryrun.models import DryRunConfig

# Substrings that must not appear in the adapter_name (case-insensitive).
_FORBIDDEN_ADAPTER_SUBSTRINGS: frozenset[str] = frozenset(
    {"live", "prod", "real", "capital"}
)


class DryRunPolicyError(ValueError):
    """Raised when a DryRunConfig violates one or more safety policies."""


class DryRunPolicyEnforcer:
    """Stateless validator for DryRunConfig objects.

    Usage
    -----
    >>> enforcer = DryRunPolicyEnforcer()
    >>> enforcer.enforce(config, context)   # raises DryRunPolicyError if unsafe
    """

    def enforce(self, config: DryRunConfig, context: Any) -> None:
        """Check *config* against all policy rules.

        Parameters
        ----------
        config : DryRunConfig
            The session configuration to validate.
        context : Any
            Caller context (e.g. current session, broker registry). May be
            *None*; reserved for future cross-component checks.

        Raises
        ------
        DryRunPolicyError
            On the first policy violation detected.
        """
        self._check_adapter_name(config)
        self._check_tick_interval(config)

    # ------------------------------------------------------------------ rules

    def _check_adapter_name(self, config: DryRunConfig) -> None:
        """Reject adapter names that contain forbidden substrings."""
        lower_name = config.adapter_name.lower()
        for forbidden in _FORBIDDEN_ADAPTER_SUBSTRINGS:
            if forbidden in lower_name:
                raise DryRunPolicyError(
                    f"Adapter name {config.adapter_name!r} contains the forbidden "
                    f"substring {forbidden!r}. Only paper/sandbox adapters are allowed "
                    f"in dry-run mode (forbidden: {sorted(_FORBIDDEN_ADAPTER_SUBSTRINGS)})."
                )

    def _check_tick_interval(self, config: DryRunConfig) -> None:
        """Reject negative tick intervals."""
        if config.tick_interval_ms < 0:
            raise DryRunPolicyError(
                f"tick_interval_ms must be >= 0, got {config.tick_interval_ms}. "
                "A value of 0 means as-fast-as-possible."
            )


__all__ = ["DryRunPolicyEnforcer", "DryRunPolicyError"]
