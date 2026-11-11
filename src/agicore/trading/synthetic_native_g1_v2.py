"""Versioned, invented-only adapter for the existing full native V2 assembly.

Accounting is performed inside the frozen native engine. Only the explicitly
selected, nonfinancial fields below may leave this adapter.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from . import ema_pullback_regime_gated_baseline_v2 as baseline
from . import ema_pullback_v2_development_replay as parser
from .ema_pullback_exit_policy_v2 import EMA20ExitFillRecordV2
from .ema_pullback_structural_stop_trigger_fill_v2 import StructuralStopFillRecordV2
from .synthetic_confirmation_fixture_v2 import generate_confirmation_fixture

PROFILES = ("native-g1-long-v1", "native-g1-short-v1")
OBSERVATIONS = 64
STAGE = "native_g1"
MISSION_SCHEMA = "agicore:mission:native-g1:v1"
BUNDLE_SCHEMA = "agicore:invented-native-g1-bundle:v1"
WORKER_SCHEMA = "agicore:invented-native-g1-worker:v1"
VERIFICATION_SCHEMA = "agicore:invented-native-g1-verification:v1"
REPORT_SCHEMA = "agicore:mission-report:native-g1:v1"
REPLAY_SCHEMA = "agicore:synthetic-native-g1-projection:v1"
STRATEGY_MANIFEST_SHA256 = parser.STRATEGY_MANIFEST_SHA256


def generate_fixture(profile: str, observations: int) -> bytes:
    """Generate the bounded invented V2 session without accepting external bytes."""
    if profile not in PROFILES or type(observations) is not int or observations != OBSERVATIONS:
        raise ValueError("unsupported native G1 fixture")
    rows = [
        line.split(";")
        for line in generate_confirmation_fixture("confirmation-long-v1", 39)
        .decode("ascii")
        .splitlines()
    ]
    origin = datetime(2099, 1, 4, 8, tzinfo=UTC)
    for index in range(37, 55):
        close = Decimal(20006 + 2 * (index - 36))
        opening = Decimal(rows[index - 1][4])
        stamp = (origin + timedelta(minutes=index)).strftime("%Y%m%d %H%M%S")
        row = [
            stamp,
            str(opening),
            str(close + Decimal(".25")),
            str(opening - Decimal(".25")),
            str(close),
            "150" if index == 40 else "100",
        ]
        if index < len(rows):
            rows[index] = row
        else:
            rows.append(row)
    tail = (
        ("20042", "20042.25", "20019.75", "20020", "100"),
        ("20020.25", "20020.5", "20019.75", "20020.25", "100"),
        ("20020.25", "20023.5", "20020.25", "20023.25", "100"),
        ("20023.25", "20026.5", "20020.5", "20026.25", "100"),
        ("20021", "20031.25", "20020.75", "20031", "150"),
        ("20031", "20031.25", "20015", "20030", "100"),
        ("20030", "20060.25", "20029.75", "20060", "100"),
        ("20060.25", "20060.5", "20059.75", "20060.25", "100"),
        ("20060.25", "20061", "20014.5", "20016", "100"),
    )
    for index, values in enumerate(tail, 55):
        stamp = (origin + timedelta(minutes=index)).strftime("%Y%m%d %H%M%S")
        rows.append([stamp, *values])
    if profile == "native-g1-short-v1":
        for row in rows:
            opening, high, low, close = map(Decimal, row[1:5])
            row[1:5] = map(
                str,
                (
                    Decimal(40000) - opening,
                    Decimal(40000) - low,
                    Decimal(40000) - high,
                    Decimal(40000) - close,
                ),
            )
    return ("\n".join(";".join(row) for row in rows) + "\n").encode("ascii")


def _evaluate_invented(raw: bytes):
    """Run the frozen native engine; callers must establish invented provenance."""
    bars = parser.parse_ninjatrader_last_rows_v2(raw)
    if not 1 <= len(bars) <= OBSERVATIONS:
        raise ValueError("native G1 observation limit exceeded")
    try:
        book = baseline.evaluate_synthetic_scenario_v2(
            strategy_instance_id="native-g1-strategy",
            series_id="INVENTED_MNQ_1_MINUTE",
            closed_bars=(bar.closed_view() for bar in bars),
        )
    except Exception:  # noqa: BLE001 - never serialize native accounting exceptions
        # Native objects contain internal accounting; do not publish exception
        # details that could accidentally serialize those objects.
        raise ValueError("native synthetic evaluation failed") from None
    if book.manifest.sha256 != parser.STRATEGY_MANIFEST_SHA256:
        raise ValueError("frozen native strategy source identity changed")
    return book


def evaluate_profile(profile: str):
    """Evaluate a named built-in invented fixture through the unchanged V2 loop."""
    return _evaluate_invented(generate_fixture(profile, OBSERVATIONS))


def _time(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def project_worker(book, raw: bytes) -> dict:
    """Project only nonfinancial native decisions and position provenance."""
    positions = []
    for position in book.policy.positions.positions:
        entry, exit_fill = position.entry, position.exit
        sized = next(item for item in book.policy.risks.filled_entries if item.execution == entry)
        exit_record = None
        if isinstance(exit_fill, EMA20ExitFillRecordV2):
            exit_record = {
                "kind": "EMA20",
                "bar_index": exit_fill.exit_execution_bar_index,
                "timestamp": _time(exit_fill.exit_execution_timestamp),
                "signal_bar_index": exit_fill.signal.exit_signal_bar_index,
                "phase": "OPEN",
            }
        elif isinstance(exit_fill, StructuralStopFillRecordV2):
            exit_record = {
                "kind": "STRUCTURAL_STOP",
                "bar_index": exit_fill.trigger_bar_index,
                "timestamp": _time(exit_fill.trigger_bar_timestamp),
                "signal_bar_index": None,
                "phase": exit_fill.trigger_phase.value,
            }
        elif exit_fill is not None:
            raise ValueError("unsupported native exit type")
        positions.append(
            {
                "source_bar_index": entry.source_regime_event_bar_index,
                "pullback_bar_index": entry.pullback_bar_index,
                "confirmation_bar_index": entry.confirmation_bar_index,
                "entry_bar_index": entry.execution_bar_index,
                "entry_timestamp": _time(entry.execution_bar_timestamp),
                "direction": entry.execution_side.value,
                "approved_quantity": sized.quantity,
                "exit": exit_record,
            }
        )
    admissions = [
        {
            "bar_index": decision.composition.closed_bar_index,
            "status": decision.status.value,
            "state": decision.state_at_signal_decision.value,
            "events": [
                {"kind": event.event_type.value, "direction": event.event_direction.value}
                for event in decision.composition.events
            ],
        }
        for decision in book.policy.signal_decisions
    ]
    return {
        "schema": REPLAY_SCHEMA,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "strategy_manifest_sha256": book.manifest.sha256,
        "observations": len(book.closed_bars),
        "positions": positions,
        "admissions": admissions,
        "end_state": book.exits.end_state.value,
    }
