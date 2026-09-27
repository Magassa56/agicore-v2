"""Single precommitted DEVELOPMENT variant of ``EMA_PULLBACK_V1_MNQ``.

V1A changes exactly one strategy predicate: the absolute EMA20 slope boundary is one
MNQ tick per bar and is inclusive.  Every other rule, dataset boundary, cost, execution,
accounting, and screening threshold is delegated unchanged to the frozen V1 code.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from .ema_pullback_v1_mnq import (
    EMA_SLOPE_LOOKBACK_BARS,
    MNQ_TICK_SIZE_POINTS,
    ClosedBarEMA20,
    EMA20SlopeResult,
    PullbackContractError,
    PullbackSide,
)
from .ema_pullback_v1_mnq_development import DevelopmentVerdict
from .ema_pullback_v1_mnq_development_replay import (
    DevelopmentReplayResult,
    _run_bars,
    load_preserved_development_raw,
)

VARIANT_ID = "EMA_PULLBACK_V1A_MNQ_EMA20_MIN_SLOPE_1_TICK"
VARIANT_HYPOTHESIS = (
    "Reject near-flat EMA20 conditions to reduce whipsaw trades, clustered losses and drawdown."
)
VARIANT_PROTOCOL_SHA256 = "1dc90028d9de807a28218075c09b7d9b32d2eb8cc86b41a84814107a898f77df"
MINIMUM_ABSOLUTE_SLOPE_POINTS_PER_BAR = Decimal("0.25")
RUNNER_ID = "EMA_PULLBACK_V1A_MNQ_DEVELOPMENT_REPLAY_V1"
RUNNER_VERSION = "1.0"

if MINIMUM_ABSOLUTE_SLOPE_POINTS_PER_BAR != MNQ_TICK_SIZE_POINTS:
    raise RuntimeError("V1A slope threshold must remain exactly one MNQ tick")


def evaluate_v1a_ema20_slope(
    *,
    side: PullbackSide,
    lookback_bar: ClosedBarEMA20,
    confirmation_bar: ClosedBarEMA20,
) -> EMA20SlopeResult:
    """Apply the exact causal V1 formula with the inclusive V1A one-tick boundary."""
    if not isinstance(side, PullbackSide):
        raise PullbackContractError("side must be explicitly LONG or SHORT")
    if confirmation_bar.sequence < EMA_SLOPE_LOOKBACK_BARS:
        raise PullbackContractError(
            f"at least {EMA_SLOPE_LOOKBACK_BARS} closed warmup bars are required"
        )
    expected_lookback_sequence = confirmation_bar.sequence - EMA_SLOPE_LOOKBACK_BARS
    if lookback_bar.sequence != expected_lookback_sequence:
        raise PullbackContractError("lookback bar must be the causal closed bar exactly t-3")

    slope = (confirmation_bar.ema20 - lookback_bar.ema20) / Decimal(EMA_SLOPE_LOOKBACK_BARS)
    qualifies = (
        slope >= MINIMUM_ABSOLUTE_SLOPE_POINTS_PER_BAR
        if side is PullbackSide.LONG
        else slope <= -MINIMUM_ABSOLUTE_SLOPE_POINTS_PER_BAR
    )
    return EMA20SlopeResult(
        side=side,
        ema20_slope_qualifies=qualifies,
        slope_points_per_bar=slope,
        lookback_bar_sequence=lookback_bar.sequence,
        confirmation_bar_sequence=confirmation_bar.sequence,
    )


def run_preserved_v1a_development_replay(path: str | Path) -> DevelopmentReplayResult:
    """Verify and run the sole authorized V1A EXPOSED_DEVELOPMENT replay."""
    dataset = load_preserved_development_raw(path)
    return _run_bars(
        dataset.bars,
        source_raw_sha256=dataset.source_raw_sha256,
        source_size_bytes=dataset.source_size_bytes,
        slope_evaluator=evaluate_v1a_ema20_slope,
        runner_id=RUNNER_ID,
        runner_version=RUNNER_VERSION,
        variant_id=VARIANT_ID,
        variant_protocol_sha256=VARIANT_PROTOCOL_SHA256,
        no_go_verdict=DevelopmentVerdict.NO_GO_VARIANT,
    )


__all__ = [
    "MINIMUM_ABSOLUTE_SLOPE_POINTS_PER_BAR",
    "RUNNER_ID",
    "RUNNER_VERSION",
    "VARIANT_HYPOTHESIS",
    "VARIANT_ID",
    "VARIANT_PROTOCOL_SHA256",
    "evaluate_v1a_ema20_slope",
    "run_preserved_v1a_development_replay",
]
