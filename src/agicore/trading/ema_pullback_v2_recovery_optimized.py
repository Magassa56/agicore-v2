"""EMA_PULLBACK_V2_RECOVERY_OPTIMIZED_ENGINE_V1: distinct, exact, synthetic only.

Architecture exception PR #313 permits explicit incremental computational
equivalents. The original frozen assembly is NOT executing this engine's Close
paths. A registered identity is evidence, never authorization to read real data.
This implementation exposes no real file loader or recovery-claim creator.
Close validation preserves the frozen duplicate/end-of-data/error precedence;
the source closure binds this entrypoint and its separately hashed reducer.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from . import ema_pullback_v2_development_replay as reference
from .ema_pullback_v2_recovery_accounting import RecoveryMarksV1, build_native_result_v1
from .ema_pullback_v2_recovery_evidence import CanonicalEncoderV1, validate_native_result_v1
from .ema_pullback_v2_recovery_lifecycle import RecoveryLifecycleV1

RUNTIME_ID = "EMA_PULLBACK_V2_RECOVERY_OPTIMIZED_ENGINE_V1"
INPUT_DOMAIN = "SYNTHETIC_ONLY"
REAL_EXECUTION_AUTHORIZED = False


def build_recovery_identity_v1(raw_sha256: str):
    """The unchanged four-field identity binds this distinct entrypoint's bytes."""
    return reference.screening.RunIdentity(
        reference.STRATEGY_MANIFEST_SHA256, reference.DEVELOPMENT_PROTOCOL_SHA256,
        raw_sha256, hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


def run_synthetic_native_v1(raw: bytes, *, bindings, progress=None):
    """Invented bytes only; produce the complete native document without a real claim."""
    reference._require(type(raw) is bytes, "synthetic bytes required")
    digest = hashlib.sha256(raw).hexdigest()
    reference._require(digest != reference.CANONICAL_DATASET_RAW_SHA256,
                       "canonical DEVELOPMENT cannot be synthetic")
    bars = reference.parse_ninjatrader_last_rows_v2(raw)
    reference._require(len(bars) >= 2, "positive source span required")
    identity = build_recovery_identity_v1(digest)
    engine = RecoveryLifecycleV1(strategy_instance_id=reference.assembly.STRATEGY_ID,
                                 series_id="synthetic-" + digest[:16] + "-v1")
    marks = RecoveryMarksV1()
    for bar in bars:
        opening = reference.assembly.execution.EntryExecutionOpenV2(
            bar.bar_index, bar.timestamp_utc, bar.open)
        engine.process_open(opening)
        if progress is not None:
            progress(bar.bar_index, "OPEN", engine)
        engine.process_close(bar.closed_view())
        marks.append(engine.live, bar)
        if progress is not None:
            progress(bar.bar_index, "CLOSE", engine)
    engine.finish()
    document = build_native_result_v1(engine, bars, marks, identity, bindings)
    return document, identity


def evaluate_synthetic_recovery_v1(raw: bytes, *, bindings, progress=None):
    """Validate and serialize complete synthetic native evidence exactly."""
    document, identity = run_synthetic_native_v1(raw, bindings=bindings, progress=progress)
    validate_native_result_v1(document, bindings, identity)
    return reference.DevelopmentReplayResultV2(CanonicalEncoderV1().bytes(document))


def execute_real_recovery_v1(*args, **kwargs):
    """Always DENY in this gate; a separate execution implementation/approval is required."""
    raise reference.DevelopmentReplayV2Error(
        "real recovery execution forbidden; separate future authorization artifact required")
