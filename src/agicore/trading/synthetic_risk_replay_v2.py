"""Replay a fixed invented input through confirmation, structural stop and risk decision.

This module binds the decision to exact synthetic bytes supplied by the caller.
It performs no order, entry execution, fill, position or financial profit calculation.
"""

from __future__ import annotations

import hashlib
import json

from .ema20_pullback_v2 import EMA20PullbackBarV2
from .ema_pullback_initial_stop_v2 import InitialStopStatusV2
from .ema_pullback_v2_development_replay import (
    canonical_replay_bytes_v2,
    parse_ninjatrader_last_rows_v2,
)
from .synthetic_confirmation_replay_v2 import replay_confirmation_native
from .synthetic_risk_handoff_v2 import capture_admitted_synthetic_risk_v2
from .synthetic_stop_handoff_v2 import capture_synthetic_stop_v2

SCHEMA = "agicore:synthetic-confirmation-risk-replay:v1"


def replay_risk_native(raw: bytes) -> dict:
    """Bind confirmation, structural stop and risk decision to caller-supplied bytes.

    The caller must establish synthetic provenance. Both worker and verifier
    reconstruct each phase independently and check bit-for-bit equivalence.
    """
    outcome = replay_confirmation_native(raw)
    signal = outcome.native_confirmation
    if signal is None or outcome.summary["stop_reason"] != "CONFIRMED_BEFORE_RISK":
        raise ValueError("the fixed risk profile did not confirm")
    record = signal.confirmation
    k, q = record.pullback_bar_index, record.confirmation_bar_index
    if type(k) is not int or type(q) is not int or not 0 <= k < q or q - k not in (1, 2):
        raise ValueError("invalid confirmation window")
    bars = parse_ninjatrader_last_rows_v2(raw)
    if q >= len(bars) or outcome.summary["processed_observations"] != q + 1:
        raise ValueError("confirmation clock differs from input")
    selected = tuple(
        EMA20PullbackBarV2(
            bar.bar_index, bar.timestamp_utc, bar.open, bar.high, bar.low, bar.close, True
        )
        for bar in bars[k : q + 1]
    )
    if selected != outcome.stop_window:
        raise ValueError("confirmation window differs from input bytes")

    stop_eval = capture_synthetic_stop_v2(confirmation=signal, closed_window=selected).evaluation
    if (
        stop_eval.status is not InitialStopStatusV2.EVALUATED
        or stop_eval.initial_stop_record is None
        or stop_eval.at_entry is not None
    ):
        raise ValueError("stop not captured without entry")

    candidate_bar = selected[-1]
    risk_handoff = capture_admitted_synthetic_risk_v2(
        raw=raw, confirmation=signal, initial_stop=stop_eval, closed_candidate=candidate_bar
    )
    risk_record = risk_handoff.decision

    lines = raw.splitlines(keepends=True)
    if len(lines) != len(bars):
        raise ValueError("row boundaries differ from parsed input")

    return {
        "schema": SCHEMA,
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "confirmation_replay": outcome.summary,
        "confirmation": json.loads(canonical_replay_bytes_v2(record)),
        "window": {
            "first_bar_index": k,
            "last_bar_index": q,
            "raw_rows_sha256": hashlib.sha256(b"".join(lines[k : q + 1])).hexdigest(),
        },
        "stop": json.loads(canonical_replay_bytes_v2(stop_eval)),
        "risk": json.loads(canonical_replay_bytes_v2(risk_record)),
        "stop_reason": "RISK_DECIDED_BEFORE_ENTRY",
    }
