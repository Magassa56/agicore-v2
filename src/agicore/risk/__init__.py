"""AGIcore-v2 — Risk & Exposure layer (Phase 8C).

Stateless pre-execution risk gatekeeper. Validates ``ExecutionIntent``
against an ``ExposureSnapshot`` using ``RiskLimits`` and returns a
``RiskCheckResult`` listing all violations.
"""
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
    SymbolExposure,
    empty_snapshot,
)
from .risk_manager import RiskManager

__all__ = [
    "RiskManager",
    "RiskLimits",
    "RiskLevel",
    "RiskCheckCode",
    "RiskViolation",
    "RiskCheckResult",
    "ExecutionIntent",
    "ExposureSnapshot",
    "SymbolExposure",
    "IntentSide",
    "empty_snapshot",
    "EVT_RISK_PASSED",
    "EVT_RISK_BLOCKED",
]
