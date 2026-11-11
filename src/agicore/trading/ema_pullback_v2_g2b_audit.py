"""Independent, identity-aware audit for the versioned invented G2B contract.

The reconciliation below reuses the historical auditor's pure lifecycle, fill,
statistics and screening routines. Only its orchestration is repeated because
the historical entrypoint intentionally accepts the frozen reference runner only.
No identity is replaced or normalized here.
"""

from __future__ import annotations

import re
from collections import Counter
from datetime import UTC, datetime
from decimal import Decimal
from fractions import Fraction
from itertools import pairwise

from .ema_pullback_v2_storage_audit import (
    _aggregate,
    _audit_trade,
    _authority,
    _diagnostics,
    _lifecycle_audit,
    marked_drawdown,
    native,
    rational,
    schema_check,
    screening_verdict,
    timestamp,
    trade_statistics,
)
from .ema_pullback_v2_storage_format import (
    REAL_RAW_SHA,
    StorageProofError,
    canonical,
    require,
    sha,
)


def source_witnesses(raw: bytes, expected_sha: str, *, maximum: int) -> list[dict]:
    """Derive exact row provenance from already-registered invented bytes."""
    require(
        type(raw) is bytes and sha(raw) == expected_sha != REAL_RAW_SHA, "invented source identity"
    )
    rows, offset = [], 0
    for index, line in enumerate(raw.splitlines(keepends=True)):
        require(index < maximum and line.endswith(b"\n"), "G2B bounded source rows")
        fields = line.rstrip(b"\r\n").decode("ascii").split(";")
        require(len(fields) == 6 and re.fullmatch(r"\d{8} \d{6}", fields[0]), "source row shape")
        stamp = datetime.strptime(fields[0], "%Y%m%d %H%M%S").replace(tzinfo=UTC)
        require(
            stamp.second == 0 and (not rows or timestamp(rows[-1]["timestamp_utc"]) < stamp),
            "source observation ordering",
        )
        close = Decimal(fields[4])
        require(close.is_finite(), "source Close finite")
        rows.append(
            {
                "bar_index": index,
                "timestamp_utc": stamp.isoformat().replace("+00:00", "Z"),
                "raw_close_text": fields[4],
                "close_exact": native(Fraction(close)),
                "source_row_byte_offset": offset,
                "source_row_size_bytes": len(line),
                "source_row_sha256": sha(line),
            }
        )
        offset += len(line)
    require(2 <= len(rows) <= maximum and offset == len(raw), "source coverage")
    return rows


def audit_optimized_native(
    document: dict, witnesses: list, raw: bytes, *, runner_sha: str, input_sha: str, maximum: int
) -> dict:
    """Audit the genuine optimized identity, source, lifecycle and exact metrics."""
    try:
        return _audit_optimized_native(
            document, witnesses, raw, runner_sha=runner_sha, input_sha=input_sha, maximum=maximum
        )
    except StorageProofError:
        raise
    except (KeyError, TypeError, ValueError, IndexError, ArithmeticError) as exc:
        raise StorageProofError("invalid G2B native evidence: FAIL_CLOSED") from exc


def _audit_optimized_native(document, witnesses, raw, *, runner_sha, input_sha, maximum):
    addendum, protocol, constants = _authority()
    schema = protocol["result_schema"]
    schema_check(document, schema, schema)
    identity = document["run_identity"]
    require(
        identity["dataset_raw_sha256"] == input_sha == sha(raw) != REAL_RAW_SHA, "invented identity"
    )
    require(
        identity["strategy_manifest_sha256"] == addendum["parents"]["strategy_manifest"]["sha256"]
        and identity["development_protocol_sha256"]
        == addendum["parents"]["development_protocol"]["sha256"]
        and identity["runner_source_sha256"] == runner_sha
        and document["run_id_sha256"] == sha(canonical(identity)),
        "optimized run binding",
    )
    require(
        document["dataset_lineage_manifest_sha256"]
        == addendum["parents"]["dataset_lineage"]["sha256"]
        and document["dataset_id"] == "synthetic-" + input_sha[:16] + "-v1",
        "native dataset binding",
    )
    require(
        document["output_sha256"]
        == sha(canonical({k: v for k, v in document.items() if k != "output_sha256"})),
        "native output SHA",
    )
    require(
        witnesses == source_witnesses(raw, input_sha, maximum=maximum), "source Close witnesses"
    )
    require(
        document["dataset_first_timestamp_utc"] == witnesses[0]["timestamp_utc"]
        and document["dataset_last_timestamp_utc"] == witnesses[-1]["timestamp_utc"],
        "source bounds",
    )
    closed, opened, life = (
        document[k]
        for k in ("closed_trade_records", "open_trade_records", "immutable_lifecycle_records")
    )
    _lifecycle_audit(life, witnesses)
    require(
        life["terminal_states"][1]["state"] == ("OPEN_UNREALIZED" if opened else "FLAT"),
        "final position state",
    )
    costs = constants["ema_pullback_fees_and_slippage_v2.py"]
    trades = sorted((*closed, *opened), key=lambda r: r["entry_timestamp"])
    spans = [_audit_trade(trade, life, witnesses, costs) for trade in trades]
    require(
        [t["immutable_provenance"]["entry"] for t in trades] == life["entries"],
        "entries exactly once/order",
    )
    require(
        [t["immutable_provenance"]["exit"] for t in closed] == life["exits"],
        "exits exactly once/order",
    )
    require(
        [r["exit_timestamp"] for r in closed] == sorted(r["exit_timestamp"] for r in closed),
        "closed order",
    )
    for (entry_a, exit_a), (entry_b, _) in pairwise(spans):
        require(exit_a is not None and entry_a <= exit_a < entry_b, "one open position")
    marks = []
    pv = rational(costs["POINT_VALUE_USD"])
    for witness in witnesses:
        i = witness["bar_index"]
        realized = unrealized = Fraction()
        for trade, (entry_i, exit_i) in zip(trades, spans, strict=True):
            if exit_i is not None and exit_i <= i:
                realized += rational(trade["net_realized_pnl_usd"])
            elif entry_i <= i:
                sign = 1 if trade["direction"] == "LONG" else -1
                unrealized += sign * (
                    rational(witness["close_exact"]) - rational(trade["entry_effective_fill_price"])
                ) * pv * trade["approved_quantity"] - rational(trade["entry_fee_usd"])
        marks.append(
            {
                "bar_index": i,
                "timestamp_utc": witness["timestamp_utc"],
                "realized_equity_usd": realized,
                "unrealized_pnl_usd": unrealized,
                "marked_equity_usd": realized + unrealized,
            }
        )
    require(
        native(marks) == document["marked_equity_samples"], "independent per-source Close equity"
    )
    metrics = trade_statistics(rational(r["net_realized_pnl_usd"]) for r in closed)
    metrics.update(_aggregate(closed))
    grouped = {}
    for event in life["events"]:
        grouped.setdefault(event["event_bar_index"], set()).add(event["event_direction"])
    events, risks, suppressions = (
        Counter(r[field] for r in life[key])
        for key, field in (
            ("events", "event_type"),
            ("risk_decisions", "decision"),
            ("suppressions", "suppression_reason"),
        )
    )
    open_fees = sum((rational(r["entry_fee_usd"]) for r in opened), Fraction())
    metrics.update(
        {
            "directional_impulses": events["DIRECTIONAL_IMPULSE_EVENT"],
            "reversal_transitions": events["REVERSAL_TRANSITION_EVENT"],
            "admitted_contexts": len(life["contexts"]),
            "ambiguous_contexts": sum(len(v) > 1 for v in grouped.values()),
            "expired_contexts": sum(c["state"].startswith("EXPIRED_") for c in life["contexts"]),
            "qualified_ema20_pullbacks": len(life["pullbacks"]),
            "confirmations": len(life["confirmations"]),
            "risk_approvals": risks["APPROVE"],
            "risk_rejections": risks["REJECT"],
            "suppressed_pending_opportunities": suppressions["PENDING_OPPORTUNITY_ALREADY_ACTIVE"],
            "suppressed_position_open_events": suppressions["POSITION_ALREADY_OPEN"],
            "quantity_1_count": sum(t["approved_quantity"] == 1 for t in trades),
            "quantity_2_count": sum(t["approved_quantity"] == 2 for t in trades),
            "entry_fills": len(trades),
            "open_trades_at_end": len(opened),
            "long_entry_fills": sum(t["direction"] == "LONG" for t in trades),
            "short_entry_fills": sum(t["direction"] == "SHORT" for t in trades),
            "closed_trade_fees_usd": metrics["total_fees_usd"],
            "open_entry_fees_usd": open_fees,
            "maximum_marked_equity_drawdown_usd": marked_drawdown(
                m["marked_equity_usd"] for m in marks
            ),
            "unrealized_pnl_at_end_usd": marks[-1]["unrealized_pnl_usd"],
            "marked_equity_at_end_usd": marks[-1]["marked_equity_usd"],
        }
    )
    metrics["total_fees_usd"] += open_fees
    metrics["diagnostic_total_slippage_cost_usd"] += sum(
        (r["approved_quantity"] * rational(costs["TICK_VALUE_USD"]) for r in opened), Fraction()
    )
    require(native(metrics) == document["metrics"], "independent complete metrics")
    first, last = (timestamp(witnesses[i]["timestamp_utc"]) for i in (0, -1))

    def microseconds(delta):
        return (delta.days * 86400 + delta.seconds) * 1_000_000 + delta.microseconds

    duration = microseconds(last - first)
    segments = []
    for i, label in enumerate(protocol["segment_contract"]["labels"]):
        group = [
            r
            for r in closed
            if min(2, 3 * microseconds(timestamp(r["exit_timestamp"]) - first) // duration) == i
        ]
        segment = trade_statistics(rational(r["net_realized_pnl_usd"]) for r in group)
        segment.update(_aggregate(group))
        segment.update(
            label=label,
            profitable=segment["net_realized_pnl_usd"] > 0,
            start_offset_microseconds=Fraction(i * duration, 3),
            end_offset_microseconds=Fraction((i + 1) * duration, 3),
        )
        segments.append(segment)
    require(native(segments) == document["segments"], "independent exact segmentation")
    verdict, failed, next_gate = screening_verdict(metrics, segments, protocol)
    require(
        (verdict, failed, next_gate)
        == (document["verdict"], document["failed_criteria"], document["next_gate"]),
        "independent screening",
    )
    require(
        _diagnostics(witnesses, closed, opened, addendum)
        == document["diagnostic_trades_per_trading_day_session"],
        "independent diagnostic buckets",
    )
    return {
        "status": "PASS",
        "observation_count": len(witnesses),
        "all_cross_field_invariants": "PASS",
        "native_output_sha256": document["output_sha256"],
        "strategy_recomputed": False,
    }
