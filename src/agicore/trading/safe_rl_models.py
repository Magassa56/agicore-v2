"""Models for the offline Safe RL experiment layer."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class SafeRLStatus(StrEnum):
    """Safety status emitted by the offline Safe RL layer."""

    SAFE = "SAFE"
    WARNING = "WARNING"
    BLOCKED = "BLOCKED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class SafeRLGuardrail(StrEnum):
    """Guardrails enforced before offline RL experiments are allowed."""

    DATASET_QUALITY_MINIMUM = "DATASET_QUALITY_MINIMUM"
    MINIMUM_TRANSITIONS_COUNT = "MINIMUM_TRANSITIONS_COUNT"
    POLICY_SCORE_MINIMUM = "POLICY_SCORE_MINIMUM"
    BLOCK_AGGRESSIVE_HIGH_RISK = "BLOCK_AGGRESSIVE_HIGH_RISK"
    BLOCK_DANGEROUS_MARKET = "BLOCK_DANGEROUS_MARKET"
    BLOCK_HIGH_EMOTIONAL_RISK = "BLOCK_HIGH_EMOTIONAL_RISK"
    BLOCK_NEGATIVE_REWARD = "BLOCK_NEGATIVE_REWARD"
    BLOCK_OVERTRADING = "BLOCK_OVERTRADING"
    BLOCK_REVENGE_TRADING = "BLOCK_REVENGE_TRADING"
    BLOCK_NO_TRADE_CONTEXT = "BLOCK_NO_TRADE_CONTEXT"
    REQUIRE_DRY_RUN = "REQUIRE_DRY_RUN"
    FORBID_LIVE_BROKER = "FORBID_LIVE_BROKER"
    FORBID_REAL_ORDER = "FORBID_REAL_ORDER"
    FORBID_NEURAL_TRAINING = "FORBID_NEURAL_TRAINING"
    FORBID_EXTERNAL_ML = "FORBID_EXTERNAL_ML"


@dataclass(frozen=True)
class SafeRLExperimentConfig:
    """Offline-only safety thresholds and hard gates."""

    min_dataset_quality_score: int = 70
    min_transitions_count: int = 10
    min_policy_score: int = 60
    max_dangerous_decision_rate: float = 0.10
    max_emotional_risk_score: int = 70
    min_normalized_reward: int = 35
    min_total_reward: int = -100
    dry_run_required: bool = True
    dry_run: bool = True
    allow_live_broker: bool = False
    allow_real_orders: bool = False
    allow_neural_training: bool = False
    allow_external_ml: bool = False


@dataclass(frozen=True)
class SafeRLValidationResult:
    """Single guardrail validation finding."""

    guardrail: SafeRLGuardrail
    status: SafeRLStatus
    message: str


@dataclass(frozen=True)
class SafeRLExperimentResult:
    """Aggregated Safe RL validation output."""

    status: SafeRLStatus
    validations: tuple[SafeRLValidationResult, ...]
    active_guardrails: tuple[SafeRLGuardrail, ...]
    risks_detected: tuple[str, ...]
    allowed_experiments: tuple[str, ...]
    blocked_experiments: tuple[str, ...]
    recommendations: tuple[str, ...]
    safety_summary: str


__all__ = [
    "SafeRLExperimentConfig",
    "SafeRLExperimentResult",
    "SafeRLGuardrail",
    "SafeRLStatus",
    "SafeRLValidationResult",
]
