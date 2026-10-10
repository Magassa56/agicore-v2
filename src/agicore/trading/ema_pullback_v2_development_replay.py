"""Repository DEVELOPMENT boundary for frozen V2; no automatic execution.

This implementation gate uses invented bytes only. The unchanged assembly keeps
its SYNTHETIC_ONLY declaration. A future explicit execution gate must authorize
feeding it canonical DEVELOPMENT observations through this separate adapter.
No strategy formula, session filter, synthetic minute or float belongs here.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from dataclasses import dataclass, fields, is_dataclass
from datetime import UTC, datetime, time, timedelta
from decimal import Decimal, InvalidOperation
from enum import Enum
from fractions import Fraction
from pathlib import Path
from zoneinfo import ZoneInfo

from tools import ema_pullback_v2_development_protocol as screening

from . import ema_pullback_regime_gated_baseline_v2 as assembly

STRATEGY_MANIFEST_SHA256 = screening.STRATEGY_MANIFEST_SHA256
DEVELOPMENT_PROTOCOL_SHA256 = screening.DEVELOPMENT_PROTOCOL_SHA256
DATASET_LINEAGE_MANIFEST_SHA256 = "d9a5d15a8746491391ba13417a099801ba6add44be1f275d2ca9e699adf56b89"
CANONICAL_DATASET_ID = "mnq-09-26-minute-last-development-ee6eeed4-v1"
CANONICAL_DATASET_RAW_SHA256 = "ee6eeed4871947b1fabe3c85bf4b5b319dc0d68e86edec7d2000815e22b2a126"
CANONICAL_DATASET_SIZE_BYTES = 4_785_270
CANONICAL_DATASET_ROWS = 89_841
FIRST_TIMESTAMP_UTC = datetime(2026, 6, 18, 22, 1, tzinfo=UTC)
LAST_TIMESTAMP_UTC = datetime(2026, 9, 18, 13, 30, tzinfo=UTC)
DATASET_ROLE = "EXPOSED_DEVELOPMENT"
EXECUTION_GATE = "EMA_PULLBACK_V2_DEVELOPMENT_REPLAY_EXECUTION"
PROTOCOL_IMPLEMENTATION_SHA256 = "55673813d9d716303aec2ad24fda425ca22d52a186e3b2e071653cfb81e4e1ec"
REPOSITORY = Path(__file__).resolve().parents[3]
_TIMESTAMP = re.compile(r"[0-9]{8} [0-9]{6}")
_PRICE = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)")
_VOLUME = re.compile(r"[0-9]+")


class DevelopmentReplayV2Error(ValueError):
    """Fail closed before strategy execution on any boundary or evidence error."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DevelopmentReplayV2Error(message + ": FAIL_CLOSED")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _utc(value: datetime) -> None:
    _require(
        isinstance(value, datetime) and value.utcoffset() == timedelta(0),
        "aware UTC timestamp required",
    )


def _native(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if type(value) is Fraction:
        return {"numerator": value.numerator, "denominator": value.denominator}
    if type(value) is Decimal:
        _require(value.is_finite(), "finite Decimal required")
        return _native(Fraction(value))
    if isinstance(value, datetime):
        _utc(value)
        return value.isoformat().replace("+00:00", "Z")
    if is_dataclass(value) and not isinstance(value, type):
        return {f.name: _native(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, dict):
        _require(all(type(key) is str for key in value), "string JSON keys required")
        return {key: _native(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_native(item) for item in value]
    if value is None or type(value) in (int, bool, str):
        return value
    raise DevelopmentReplayV2Error("unsupported numeric/canonical type; floats forbidden")


def _integer_text(value: int) -> str:
    # Exact rational histories can exceed Python's integer-string digit limit.
    # Chunking avoids changing a global interpreter security setting.
    sign = "-" if value < 0 else ""
    remaining = abs(value)
    chunks = []
    while remaining >= 1_000_000_000:
        remaining, tail = divmod(remaining, 1_000_000_000)
        chunks.append(f"{tail:09d}")
    return sign + str(remaining) + "".join(reversed(chunks))


def _json_text(value: object) -> str:
    if type(value) is int:
        return _integer_text(value)
    if isinstance(value, dict):
        return (
            "{"
            + ",".join(
                json.dumps(key, ensure_ascii=False) + ":" + _json_text(value[key])
                for key in sorted(value)
            )
            + "}"
        )
    if isinstance(value, list):
        return "[" + ",".join(_json_text(item) for item in value) + "]"
    return json.dumps(value, ensure_ascii=False, allow_nan=False)


def _decode_json(raw: bytes) -> dict:
    return json.loads(raw, parse_int=lambda text: int(Decimal(text)))


def canonical_replay_bytes_v2(value: object) -> bytes:
    """Sorted, compact UTF-8 JSON + LF, rejecting every float before serialization."""
    return (_json_text(_native(value)) + "\n").encode("utf-8")


@dataclass(frozen=True)
class VerifiedReplayBindingsV2:
    """Immutable metadata documents; constructing these never reads a RAW."""

    strategy_bytes: bytes
    protocol_bytes: bytes
    lineage_bytes: bytes
    session_calendar_bytes: bytes

    def __post_init__(self) -> None:
        for raw, expected in (
            (self.strategy_bytes, STRATEGY_MANIFEST_SHA256),
            (self.protocol_bytes, DEVELOPMENT_PROTOCOL_SHA256),
            (self.lineage_bytes, DATASET_LINEAGE_MANIFEST_SHA256),
        ):
            _require(type(raw) is bytes and _sha(raw) == expected, "frozen document hash mismatch")
        _require(
            _sha(Path(screening.__file__).read_bytes()) == PROTOCOL_IMPLEMENTATION_SHA256,
            "precommitted screening implementation changed",
        )
        _require(
            assembly.build_strategy_manifest_v2().canonical_utf8 == self.strategy_bytes,
            "frozen assembly/component source changed",
        )
        lineage = self.lineage
        _require(
            _sha(self.session_calendar_bytes)
            == lineage["gap_reconciliation"]["evidence"]["sha256"],
            "lineage calendar evidence changed",
        )
        derived = lineage["derived_raw"]
        _require(
            lineage["status"] == "PASS"
            and lineage["strategy_manifest_sha256"] == STRATEGY_MANIFEST_SHA256
            and lineage["development_protocol_sha256"] == DEVELOPMENT_PROTOCOL_SHA256
            and lineage["canonical_dataset_id"] == CANONICAL_DATASET_ID
            and lineage["dataset_role"] == DATASET_ROLE
            and lineage["source_raw_sha256"] == CANONICAL_DATASET_RAW_SHA256
            and derived["sha256"] == CANONICAL_DATASET_RAW_SHA256
            and derived["size_bytes"] == CANONICAL_DATASET_SIZE_BYTES
            and derived["data_rows"] == CANONICAL_DATASET_ROWS
            and derived["first_timestamp_utc"] == _native(FIRST_TIMESTAMP_UTC)
            and derived["last_timestamp_utc"] == _native(LAST_TIMESTAMP_UTC),
            "canonical lineage binding mismatch",
        )
        screening.VerifiedProtocol(self.protocol_bytes, self.strategy_bytes)

    @property
    def lineage(self) -> dict:
        """Fresh metadata copy; callers cannot mutate the frozen binding."""
        return json.loads(self.lineage_bytes)

    @property
    def protocol(self) -> screening.VerifiedProtocol:
        """Reuse the exact precommitted screening, including thresholds and segments."""
        return screening.VerifiedProtocol(self.protocol_bytes, self.strategy_bytes)

    @property
    def session_calendar(self) -> dict:
        """Metadata-only calendar/gap evidence already bound by frozen lineage."""
        return json.loads(self.session_calendar_bytes)


def read_frozen_replay_bindings_v2() -> VerifiedReplayBindingsV2:
    """Read bound evidence JSON/calendar metadata and source guards, never a RAW."""
    root = REPOSITORY / "docs/evidence"
    return VerifiedReplayBindingsV2(
        (root / "EMA_PULLBACK_V2_REGIME_GATED_BASELINE_MANIFEST.json").read_bytes(),
        (root / "EMA_PULLBACK_V2_DEVELOPMENT_PROTOCOL.json").read_bytes(),
        (root / "EMA_PULLBACK_V2_DEVELOPMENT_DATASET_LINEAGE.json").read_bytes(),
        (root / "EMA_PULLBACK_V2_DEVELOPMENT_DATASET_GAP_AUDIT.json").read_bytes(),
    )


def build_replay_run_identity_v2(
    dataset_raw_sha256: str = CANONICAL_DATASET_RAW_SHA256,
) -> screening.RunIdentity:
    """Four-hash identity; persistence/authorization is separate from calculation."""
    return screening.RunIdentity(
        STRATEGY_MANIFEST_SHA256,
        DEVELOPMENT_PROTOCOL_SHA256,
        dataset_raw_sha256,
        _sha(Path(__file__).read_bytes()),
    )


@dataclass(frozen=True)
class DevelopmentReplayBarV2:
    """One actual source observation; exact Decimal prices and integral trade volume."""

    bar_index: int
    timestamp_utc: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int

    def __post_init__(self) -> None:
        _utc(self.timestamp_utc)
        _require(
            type(self.bar_index) is int
            and self.bar_index >= 0
            and self.timestamp_utc.second == self.timestamp_utc.microsecond == 0,
            "one-minute observation/index required",
        )
        for price in (self.open, self.high, self.low, self.close):
            _require(type(price) is Decimal and price.is_finite(), "finite Decimal OHLC required")
            _require(
                (Fraction(price) / assembly.risk.TICK_SIZE).denominator == 1,
                "off MNQ tick grid",
            )
        _require(
            self.high >= max(self.open, self.close)
            and self.low <= min(self.open, self.close)
            and self.high >= self.low,
            "invalid OHLC",
        )
        _require(
            type(self.volume) is int and self.volume >= 0, "nonnegative integer volume required"
        )

    def closed_view(self) -> assembly.impulse.DirectionalImpulseBarV2:
        """Native closed observation; no local indicator or strategy calculation."""
        return assembly.impulse.DirectionalImpulseBarV2(
            self.bar_index,
            self.timestamp_utc,
            self.open,
            self.high,
            self.low,
            self.close,
            True,
            self.volume,
            assembly.impulse.IMPULSE_VOLUME_MEASURE,
            1,
            "Last",
        )


def parse_ninjatrader_last_rows_v2(raw: bytes) -> tuple[DevelopmentReplayBarV2, ...]:
    """Parse caller-supplied bytes exactly, without file access, repair or sorting."""
    _require(type(raw) is bytes and bool(raw), "nonempty RAW bytes required")
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise DevelopmentReplayV2Error("invalid native RAW encoding: FAIL_CLOSED") from exc
    _require("\r" not in text.replace("\r\n", ""), "invalid RAW line ending")
    text = text.replace("\r\n", "\n")
    lines = text.removesuffix("\n").split("\n")
    _require(bool(lines), "RAW rows required")
    bars = []
    for index, line in enumerate(lines):
        parts = line.split(";")
        _require(
            len(parts) == 6 and _TIMESTAMP.fullmatch(parts[0]) is not None,
            "malformed RAW row/timestamp",
        )
        _require(
            all(_PRICE.fullmatch(p) is not None for p in parts[1:5])
            and _VOLUME.fullmatch(parts[5]) is not None,
            "malformed price or integer volume",
        )
        try:
            timestamp = datetime.strptime(parts[0], "%Y%m%d %H%M%S").replace(tzinfo=UTC)
            bar = DevelopmentReplayBarV2(
                index, timestamp, *(Decimal(p) for p in parts[1:5]), int(parts[5])
            )
        except (ValueError, InvalidOperation) as exc:
            raise DevelopmentReplayV2Error("invalid native RAW observation: FAIL_CLOSED") from exc
        _require(
            not bars or timestamp > bars[-1].timestamp_utc, "duplicate/nonchronological timestamp"
        )
        bars.append(bar)
    return tuple(bars)


@dataclass(frozen=True)
class RawIdentityV2:
    """Dataset byte/row/bound identity; no strategy setting is present."""

    sha256: str
    size_bytes: int
    rows: int
    first_timestamp: datetime
    last_timestamp: datetime
    dataset_id: str
    dataset_role: str


CANONICAL_RAW_IDENTITY = RawIdentityV2(
    CANONICAL_DATASET_RAW_SHA256,
    CANONICAL_DATASET_SIZE_BYTES,
    CANONICAL_DATASET_ROWS,
    FIRST_TIMESTAMP_UTC,
    LAST_TIMESTAMP_UTC,
    CANONICAL_DATASET_ID,
    DATASET_ROLE,
)


def _verify_raw_bytes(raw: bytes, expected: RawIdentityV2) -> tuple[DevelopmentReplayBarV2, ...]:
    _require(type(raw) is bytes and _sha(raw) == expected.sha256, "RAW SHA-256 mismatch")
    _require(len(raw) == expected.size_bytes, "RAW size mismatch")
    bars = parse_ninjatrader_last_rows_v2(raw)
    _require(len(bars) == expected.rows, "RAW row count mismatch")
    _require(
        bars[0].timestamp_utc == expected.first_timestamp
        and bars[-1].timestamp_utc == expected.last_timestamp,
        "RAW timestamp bounds mismatch",
    )
    return bars


def _require_execution_gate(execution_gate: str | None) -> None:
    _require(
        execution_gate == EXECUTION_GATE, "real DEVELOPMENT access requires future execution gate"
    )


def _verify_registration(raw: bytes, bindings: VerifiedReplayBindingsV2) -> screening.RunIdentity:
    _require(type(bindings) is VerifiedReplayBindingsV2, "verified metadata required")
    try:
        registered = json.loads(raw)
        identity = build_replay_run_identity_v2()
        _require(
            canonical_replay_bytes_v2(registered) == raw, "noncanonical implementation evidence"
        )
        _require(
            registered["status"] == "PASS"
            and registered["dataset_lineage_manifest_sha256"] == DATASET_LINEAGE_MANIFEST_SHA256
            and registered["run_identity"] == _native(identity)
            and registered["runner_source_sha256"] == identity.runner_source_sha256
            and registered["original_development_run_id_sha256"] == identity.sha256,
            "pre-execution registered identity/source mismatch",
        )
        return identity
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise DevelopmentReplayV2Error(
            "invalid registered implementation evidence: FAIL_CLOSED"
        ) from exc


def load_canonical_development_raw_v2(
    path: str | Path,
    *,
    bindings: VerifiedReplayBindingsV2,
    registered_implementation_bytes: bytes,
    dataset_id: str = CANONICAL_DATASET_ID,
    dataset_role: str = DATASET_ROLE,
    execution_gate: str | None = None,
) -> tuple[DevelopmentReplayBarV2, ...]:
    """Future-only loader: deny by default before path access, then verify all bytes."""
    _require_execution_gate(execution_gate)
    _verify_registration(registered_implementation_bytes, bindings)
    _require(
        dataset_id == CANONICAL_DATASET_ID and dataset_role == DATASET_ROLE,
        "dataset ID/role mismatch; OOS forbidden",
    )
    source = Path(path).resolve()
    _require(not source.is_relative_to(REPOSITORY / "data"), "repo/data is forbidden")
    try:
        raw = source.read_bytes()
    except OSError as exc:
        raise DevelopmentReplayV2Error("canonical RAW unavailable: FAIL_CLOSED") from exc
    return _verify_raw_bytes(raw, CANONICAL_RAW_IDENTITY)


def _context_key(context) -> tuple:
    return (
        context.source_event_bar_index,
        context.source_event_direction,
        context.source_event_types,
    )


def _lifecycle(book: assembly.RegimeGatedBaselineBookV2, input_domain: str) -> dict:
    contexts = {}
    pullbacks = []
    for decision in book.policy.positions.signal_decisions:
        if decision.pullback is None:
            continue
        lifetime = decision.pullback.lifetime
        for context in (*lifetime.retired_contexts, lifetime.context):
            if context.source_event_bar_index is not None:
                contexts[_context_key(context)] = context
        if decision.pullback.pullback is not None and decision.pullback.pullback.pullback_qualified:
            pullbacks.append(decision.pullback.pullback)
    if book.policy.positions.lifetime is not None:
        lifetime = book.policy.positions.lifetime
        for context in (*lifetime.retired_contexts, lifetime.context):
            if context.source_event_bar_index is not None:
                contexts[_context_key(context)] = context
    events = [e for d in book.policy.signal_decisions for e in d.composition.events]
    confirmations = [
        o.confirmation.confirmation
        for o in book.policy.opportunities
        if o.confirmation.entry_confirmation
    ]
    entries = [e.execution for e in book.policy.risks.executions.entries if e.execution is not None]
    exits = [p.exit for p in book.policy.positions.positions if p.exit is not None]
    suppressions = [s for d in book.policy.signal_decisions for s in d.suppressions]
    suppressions += [s for d in book.policy.positions.signal_decisions for s in d.suppressions]
    terminals = [
        {"kind": "INPUT_DOMAIN", "state": input_domain},
        {"kind": "END_OF_DATA", "state": book.exits.end_state},
    ]
    terminals += [{"kind": "OPPORTUNITY", "record": o} for o in book.policy.opportunities]
    terminals += [
        {"kind": "ENTRY_EXECUTION", "record": e} for e in book.policy.risks.executions.entries
    ]
    terminals += [{"kind": "EMA_EXIT_EXECUTION", "record": e} for e in book.exits.ema_executions]
    terminals += [{"kind": "CONTEXT", "record": c} for c in contexts.values()]
    return {
        "events": events,
        "contexts": list(contexts.values()),
        "pullbacks": pullbacks,
        "confirmations": confirmations,
        "stops": list(book.policy.initial_stops.entries),
        "risk_decisions": list(book.policy.risks.decisions),
        "entries": entries,
        "exits": exits,
        "suppressions": suppressions,
        "terminal_states": terminals,
    }


def _trade_record(final, lifecycle: dict) -> dict:
    trade = final.accounting
    position = final.position
    decision = trade.sized_entry.risk_decision
    context = decision.consumed_context
    pullback = next(
        p for p in lifecycle["pullbacks"] if p.pullback_bar_index == context.pullback_bar_index
    )
    provenance = {
        "regime": {
            "consumed_context": context,
            "events": [
                e
                for e in lifecycle["events"]
                if e.event_bar_index == context.source_event_bar_index
                and e.event_direction == context.source_event_direction
            ],
        },
        "pullback": pullback,
        "confirmation": decision.confirmation,
        "initial_stop": decision.initial_stop_record,
        "risk_decision": decision,
        "entry": position.entry,
        "accounting": trade,
    }
    record = {
        "immutable_provenance": provenance,
        "approved_quantity": trade.quantity,
        "entry_base_fill_price": trade.entry.base_fill_price,
        "entry_effective_fill_price": trade.entry.effective_fill_price_after_slippage,
        "entry_fee_usd": trade.entry.fee_usd,
        "entry_timestamp": position.entry.execution_bar_timestamp,
        "direction": trade.direction,
        "net_realized_pnl_usd": trade.net_realized_pnl_usd,
    }
    if position.exit is None:
        record["state"] = "OPEN_UNREALIZED"
    else:
        provenance["exit"] = position.exit
        record.update(
            {
                "exit_base_fill_price": trade.exit.base_fill_price,
                "exit_effective_fill_price": trade.exit.effective_fill_price_after_slippage,
                "exit_fee_usd": trade.exit.fee_usd,
                "exit_timestamp": position.exit_timestamp,
                "exit_reason": trade.exit_type,
                "gross_price_pnl_usd": trade.gross_price_pnl_usd,
                "total_fees_usd": trade.total_fees_usd,
                "diagnostic_slippage_cost_usd": trade.diagnostic_total_slippage_cost_usd,
            }
        )
    return record


def _mark(book, bar: DevelopmentReplayBarV2) -> screening.MarkedEquityPoint:
    realized = sum(
        (
            t.net_realized_pnl_usd
            for t in book.exits.costs.trades
            if t.net_realized_pnl_usd is not None
        ),
        Fraction(),
    )
    unrealized = Fraction()
    for trade in book.exits.costs.trades:
        if trade.exit is None:
            sign = 1 if trade.direction is assembly.context.RegimeDirection.LONG else -1
            unrealized += (
                sign
                * (Fraction(bar.close) - trade.entry.effective_fill_price_after_slippage)
                * assembly.costs.POINT_VALUE_USD
                * trade.quantity
                - trade.entry.fee_usd
            )
    return screening.MarkedEquityPoint(bar.bar_index, bar.timestamp_utc, realized, unrealized)


def _aggregate_costs(records: list[dict]) -> dict:
    return {
        "long_closed_trades": sum(
            r["direction"] == assembly.context.RegimeDirection.LONG for r in records
        ),
        "short_closed_trades": sum(
            r["direction"] == assembly.context.RegimeDirection.SHORT for r in records
        ),
        "structural_stop_exits": sum(r["exit_reason"] == "STRUCTURAL_STOP" for r in records),
        "ema20_exits": sum(r["exit_reason"] == "EMA20_POSITION_EXIT" for r in records),
        **{
            key: sum((r[key] for r in records), Fraction())
            for key in ("gross_price_pnl_usd", "total_fees_usd", "diagnostic_slippage_cost_usd")
        },
    }


def _session_bucket(timestamp: datetime, timezone, closures, off_session) -> tuple[str, str]:
    # Regular ETH 17:00-16:00 CT comes from CME_REGULAR_EQUITY_HOURS in
    # the bound lineage calendar; scheduled exceptions come from its gap audit.
    # These labels never control whether an observation reaches the assembly.
    local = timestamp.astimezone(timezone)
    active = (
        local.weekday() < 5
        and local.time() <= time(16)
        or local.weekday() in (6, 0, 1, 2, 3)
        and local.time() > time(17)
    )
    active = (
        active
        and timestamp not in off_session
        and not any(first < timestamp < last for first, last in closures)
    )
    day = local.date() + (timedelta(days=1) if active and local.time() > time(17) else timedelta())
    session = "CME_US_INDEX_FUTURES_ETH" if active else "OFF_SESSION_STORED_OBSERVATION"
    return day.isoformat(), session


def _diagnostics(bars, closed, opened, bindings) -> list[dict]:
    calendar = bindings.session_calendar
    timezone = ZoneInfo(calendar["calendar_conversion"]["calendar_timezone"])
    closures = tuple(
        (_timestamp(gap["previous_timestamp_utc"]), _timestamp(gap["next_timestamp_utc"]))
        for gap in calendar["gaps"]
        if gap["classification"].startswith("SCHEDULED_")
    )
    off_session = frozenset(
        _timestamp(row["timestamp_utc"]) for row in calendar["off_session_observed_rows"]
    )
    counts = {
        _session_bucket(bar.timestamp_utc, timezone, closures, off_session): [0, 0] for bar in bars
    }
    for record in (*closed, *opened):
        counts[_session_bucket(record["entry_timestamp"], timezone, closures, off_session)][0] += 1
    for record in closed:
        counts[_session_bucket(record["exit_timestamp"], timezone, closures, off_session)][1] += 1
    return [
        {
            "trading_day": key[0],
            "session_id": key[1],
            "entry_fills": value[0],
            "closed_trades": value[1],
        }
        for key, value in sorted(counts.items())
    ]


def _assemble_result(bars, raw_sha: str, dataset_id: str, bindings, input_domain: str) -> dict:
    _require(
        type(bindings) is VerifiedReplayBindingsV2 and len(bars) >= 2,
        "verified bindings/positive source span required",
    )
    identity = build_replay_run_identity_v2(raw_sha)
    book = assembly.begin_regime_gated_baseline_v2(
        strategy_instance_id=assembly.STRATEGY_ID, series_id=dataset_id
    )
    _require(book.manifest.sha256 == STRATEGY_MANIFEST_SHA256, "assembly manifest mismatch")
    marks = []
    for bar in bars:
        opening = assembly.execution.EntryExecutionOpenV2(
            bar.bar_index, bar.timestamp_utc, bar.open
        )
        book = assembly.process_baseline_open_v2(previous=book, opening_bar=opening)
        book = assembly.process_baseline_close_v2(previous=book, closed_bar=bar.closed_view())
        marks.append(_mark(book, bar))
    book = assembly.finish_regime_gated_baseline_v2(previous=book)
    lifecycle = _lifecycle(book, input_domain)
    records = [_trade_record(p, lifecycle) for p in book.final_positions]
    closed = [r for r in records if r["net_realized_pnl_usd"] is not None]
    opened = [r for r in records if r["net_realized_pnl_usd"] is None]
    times = tuple(b.timestamp_utc for b in bars)
    screen = screening.evaluate_screening(
        bindings.protocol,
        run_identity=identity,
        dataset_role=DATASET_ROLE,
        closed_trades=tuple(
            screening.ClosedTrade(
                i, r["entry_timestamp"], r["exit_timestamp"], r["net_realized_pnl_usd"]
            )
            for i, r in enumerate(closed, 1)
        ),
        marked_equity=tuple(marks),
        closed_bar_timestamps=times,
        open_trades_at_end=len(opened),
    )
    costs = _aggregate_costs(closed)
    actual = book.exits.costs.trades
    metrics = {
        **{f.name: getattr(screen.metrics, f.name) for f in fields(screen.metrics)},
        **{k: v for k, v in costs.items() if k != "diagnostic_slippage_cost_usd"},
        "directional_impulses": sum(
            e.event_type is assembly.context.RegimeEventType.DIRECTIONAL_IMPULSE_EVENT
            for e in lifecycle["events"]
        ),
        "reversal_transitions": sum(
            e.event_type is assembly.context.RegimeEventType.REVERSAL_TRANSITION_EVENT
            for e in lifecycle["events"]
        ),
        "admitted_contexts": len(lifecycle["contexts"]),
        "ambiguous_contexts": sum(
            d.composition.status is assembly.context.RegimeContextStatus.AMBIGUOUS
            for d in book.policy.signal_decisions
        ),
        "expired_contexts": sum(
            c.state.value.startswith("EXPIRED_") for c in lifecycle["contexts"]
        ),
        "qualified_ema20_pullbacks": len(lifecycle["pullbacks"]),
        "suppressed_pending_opportunities": sum(
            s.suppression_reason == "PENDING_OPPORTUNITY_ALREADY_ACTIVE"
            for s in lifecycle["suppressions"]
        ),
        "suppressed_position_open_events": sum(
            s.suppression_reason == "POSITION_ALREADY_OPEN" for s in lifecycle["suppressions"]
        ),
        "confirmations": len(lifecycle["confirmations"]),
        "risk_approvals": sum(
            d.decision is assembly.risk.RiskSizingDecisionV2.APPROVE
            for d in lifecycle["risk_decisions"]
        ),
        "risk_rejections": sum(
            d.decision is assembly.risk.RiskSizingDecisionV2.REJECT
            for d in lifecycle["risk_decisions"]
        ),
        "quantity_1_count": sum(t.quantity == 1 for t in actual),
        "quantity_2_count": sum(t.quantity == 2 for t in actual),
        "entry_fills": len(lifecycle["entries"]),
        "open_trades_at_end": len(opened),
        "long_entry_fills": sum(
            t.direction is assembly.context.RegimeDirection.LONG for t in actual
        ),
        "short_entry_fills": sum(
            t.direction is assembly.context.RegimeDirection.SHORT for t in actual
        ),
        "total_fees_usd": sum((t.total_fees_usd for t in actual), Fraction()),
        "closed_trade_fees_usd": costs["total_fees_usd"],
        "open_entry_fees_usd": sum((r["entry_fee_usd"] for r in opened), Fraction()),
        "diagnostic_total_slippage_cost_usd": sum(
            (t.diagnostic_total_slippage_cost_usd for t in actual), Fraction()
        ),
        "maximum_marked_equity_drawdown_usd": screen.maximum_marked_equity_drawdown_usd,
        "unrealized_pnl_at_end_usd": marks[-1].unrealized_pnl_usd,
        "marked_equity_at_end_usd": marks[-1].marked_equity_usd,
    }
    segments = []
    span = times[-1] - times[0]
    duration = (span.days * 86400 + span.seconds) * 1_000_000 + span.microseconds
    for index, segment in enumerate(screen.segments):
        group = []
        for r in closed:
            elapsed = r["exit_timestamp"] - times[0]
            offset = (elapsed.days * 86400 + elapsed.seconds) * 1_000_000 + elapsed.microseconds
            target = min(2, offset * 3 // duration)
            if target == index:
                group.append(r)
        segment_costs = _aggregate_costs(group)
        segment_costs["diagnostic_total_slippage_cost_usd"] = segment_costs.pop(
            "diagnostic_slippage_cost_usd"
        )
        segments.append(
            {
                **{f.name: getattr(segment.metrics, f.name) for f in fields(segment.metrics)},
                **segment_costs,
                "label": segment.label,
                "profitable": segment.profitable,
                "start_offset_microseconds": segment.start_offset_microseconds,
                "end_offset_microseconds": segment.end_offset_microseconds,
            }
        )
    result = _native(
        {
            "strategy_id": assembly.STRATEGY_ID,
            "formalization_version": assembly.FORMALIZATION_VERSION,
            "dataset_role": DATASET_ROLE,
            "dataset_id": dataset_id,
            "run_identity": identity,
            "run_id_sha256": identity.sha256,
            "dataset_lineage_manifest_sha256": DATASET_LINEAGE_MANIFEST_SHA256,
            "dataset_first_timestamp_utc": times[0],
            "dataset_last_timestamp_utc": times[-1],
            "metrics": metrics,
            "segments": segments,
            "closed_trade_records": closed,
            "open_trade_records": opened,
            "marked_equity_samples": [
                {
                    **{f.name: getattr(p, f.name) for f in fields(p)},
                    "marked_equity_usd": p.marked_equity_usd,
                }
                for p in marks
            ],
            "immutable_lifecycle_records": lifecycle,
            "diagnostic_trades_per_trading_day_session": _diagnostics(
                bars, closed, opened, bindings
            ),
            "verdict": screen.verdict,
            "failed_criteria": screen.failed_criteria,
            "next_gate": screen.next_gate,
            "oos_accessed": False,
            "parameter_changes": False,
            "production_proof": False,
        }
    )
    result["output_sha256"] = _sha(canonical_replay_bytes_v2(result))
    return result


def _schema_check(value: object, schema: dict, root: dict) -> None:
    if "$ref" in schema:
        target = root
        for part in schema["$ref"].removeprefix("#/").split("/"):
            target = target[part]
        _schema_check(value, target, root)
        return
    if "anyOf" in schema:
        for option in schema["anyOf"]:
            try:
                _schema_check(value, option, root)
                return
            except DevelopmentReplayV2Error:
                pass
        raise DevelopmentReplayV2Error("result schema anyOf mismatch: FAIL_CLOSED")
    kind = schema.get("type")
    types = {
        "object": dict,
        "array": list,
        "integer": int,
        "string": str,
        "boolean": bool,
        "null": type(None),
    }
    if kind:
        _require(type(value) is types[kind], "result schema type mismatch")
    if "const" in schema:
        _require(
            type(value) is type(schema["const"]) and value == schema["const"],
            "result schema const mismatch",
        )
    if "enum" in schema:
        _require(value in schema["enum"], "result schema enum mismatch")
    if kind == "object":
        _require(set(schema.get("required", ())) <= value.keys(), "result schema missing field")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            _require(value.keys() <= properties.keys(), "result schema unexpected field")
        for key, child in value.items():
            if key in properties:
                _schema_check(child, properties[key], root)
    elif kind == "array":
        _require(len(value) >= schema.get("minItems", 0), "result schema array too short")
        if "maxItems" in schema:
            _require(len(value) <= schema["maxItems"], "result schema array too long")
        if "items" in schema:
            for child in value:
                _schema_check(child, schema["items"], root)
    elif kind == "string":
        _require(len(value) >= schema.get("minLength", 0), "result schema string too short")
        if "pattern" in schema:
            _require(
                re.fullmatch(schema["pattern"], value) is not None, "result schema pattern mismatch"
            )
        if schema.get("format") == "date-time":
            try:
                _utc(datetime.fromisoformat(value))
            except ValueError as exc:
                raise DevelopmentReplayV2Error("invalid result UTC timestamp: FAIL_CLOSED") from exc
    elif kind == "integer" and "minimum" in schema:
        _require(value >= schema["minimum"], "result schema integer below minimum")


def _fraction(value: dict) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _validate_result(document: dict, bindings: VerifiedReplayBindingsV2) -> None:
    _require(type(bindings) is VerifiedReplayBindingsV2, "verified result bindings required")
    canonical_replay_bytes_v2(document)
    schema = bindings.protocol.document["result_schema"]
    _schema_check(document, schema, schema)
    omitted = {k: v for k, v in document.items() if k != "output_sha256"}
    _require(
        _sha(canonical_replay_bytes_v2(omitted)) == document["output_sha256"],
        "result output digest mismatch",
    )
    identity = screening.RunIdentity(**document["run_identity"])
    _require(
        identity == build_replay_run_identity_v2(identity.dataset_raw_sha256)
        and identity.sha256 == document["run_id_sha256"]
        and document["dataset_lineage_manifest_sha256"] == DATASET_LINEAGE_MANIFEST_SHA256,
        "result identity/source binding mismatch",
    )
    closed, opened = document["closed_trade_records"], document["open_trade_records"]
    life, metrics = document["immutable_lifecycle_records"], document["metrics"]
    marks = tuple(
        screening.MarkedEquityPoint(
            p["bar_index"],
            _timestamp(p["timestamp_utc"]),
            _fraction(p["realized_equity_usd"]),
            _fraction(p["unrealized_pnl_usd"]),
        )
        for p in document["marked_equity_samples"]
    )
    for point, native in zip(marks, document["marked_equity_samples"], strict=True):
        _require(
            point.marked_equity_usd == _fraction(native["marked_equity_usd"]),
            "marked equity does not reconcile",
        )
    timestamps = tuple(p.timestamp_utc for p in marks)
    domain = life["terminal_states"][0]
    _require(domain["kind"] == "INPUT_DOMAIN", "result input domain evidence required")
    if domain["state"] == "SYNTHETIC_ONLY":
        _require(
            identity.dataset_raw_sha256 != CANONICAL_DATASET_RAW_SHA256
            and document["dataset_id"] == "synthetic-" + identity.dataset_raw_sha256[:16] + "-v1",
            "synthetic result must never claim canonical DEVELOPMENT",
        )
    else:
        _require(
            domain["state"] == "AUTHORIZED_EXPOSED_DEVELOPMENT"
            and identity.dataset_raw_sha256 == CANONICAL_DATASET_RAW_SHA256
            and document["dataset_id"] == CANONICAL_DATASET_ID
            and len(marks) == CANONICAL_DATASET_ROWS
            and timestamps[0] == FIRST_TIMESTAMP_UTC
            and timestamps[-1] == LAST_TIMESTAMP_UTC,
            "real result canonical observation coverage mismatch",
        )
    _require(
        _native(timestamps[0]) == document["dataset_first_timestamp_utc"]
        and _native(timestamps[-1]) == document["dataset_last_timestamp_utc"],
        "marked source bounds mismatch",
    )
    trades = tuple(
        screening.ClosedTrade(
            i,
            _timestamp(r["entry_timestamp"]),
            _timestamp(r["exit_timestamp"]),
            _fraction(r["net_realized_pnl_usd"]),
        )
        for i, r in enumerate(closed, 1)
    )
    screen = screening.evaluate_screening(
        bindings.protocol,
        run_identity=identity,
        dataset_role=document["dataset_role"],
        closed_trades=trades,
        marked_equity=marks,
        closed_bar_timestamps=timestamps,
        open_trades_at_end=len(opened),
    )
    for field in fields(screen.metrics):
        _require(
            metrics[field.name] == _native(getattr(screen.metrics, field.name)),
            "net metric mismatch",
        )
    _require(
        document["verdict"] == screen.verdict.value
        and document["failed_criteria"] == list(screen.failed_criteria)
        and document["next_gate"] == screen.next_gate,
        "mechanical screening mismatch",
    )
    for saved, segment in zip(document["segments"], screen.segments, strict=True):
        for field in fields(segment.metrics):
            _require(
                saved[field.name] == _native(getattr(segment.metrics, field.name)),
                "segment net metric mismatch",
            )
        _require(
            saved["label"] == segment.label
            and saved["profitable"] is segment.profitable
            and saved["start_offset_microseconds"] == _native(segment.start_offset_microseconds)
            and saved["end_offset_microseconds"] == _native(segment.end_offset_microseconds),
            "elapsed-time segment mismatch",
        )
    _require(
        len(life["entries"]) == metrics["entry_fills"] == len(closed) + len(opened)
        and len(life["exits"]) == metrics["closed_trades"]
        and len(opened) == metrics["open_trades_at_end"]
        and len(life["contexts"]) == metrics["admitted_contexts"]
        and len(life["pullbacks"]) == metrics["qualified_ema20_pullbacks"]
        and len(life["confirmations"]) == metrics["confirmations"],
        "lifecycle count mismatch",
    )
    events = Counter(event["event_type"] for event in life["events"])
    grouped = {}
    for event in life["events"]:
        grouped.setdefault(event["event_bar_index"], set()).add(event["event_direction"])
    risks = Counter(record["decision"] for record in life["risk_decisions"])
    suppressed = Counter(record["suppression_reason"] for record in life["suppressions"])
    _require(
        events["DIRECTIONAL_IMPULSE_EVENT"] == metrics["directional_impulses"]
        and events["REVERSAL_TRANSITION_EVENT"] == metrics["reversal_transitions"]
        and sum(len(directions) > 1 for directions in grouped.values())
        == metrics["ambiguous_contexts"]
        and sum(record["state"].startswith("EXPIRED_") for record in life["contexts"])
        == metrics["expired_contexts"]
        and risks["APPROVE"] == metrics["risk_approvals"]
        and risks["REJECT"] == metrics["risk_rejections"]
        and suppressed["PENDING_OPPORTUNITY_ALREADY_ACTIVE"]
        == metrics["suppressed_pending_opportunities"]
        and suppressed["POSITION_ALREADY_OPEN"] == metrics["suppressed_position_open_events"],
        "event/risk/suppression count mismatch",
    )
    quantities = Counter(r["approved_quantity"] for r in (*closed, *opened))
    directions = Counter(r["direction"] for r in (*closed, *opened))
    reasons = Counter(r["exit_reason"] for r in closed)
    _require(
        quantities[1] == metrics["quantity_1_count"]
        and quantities[2] == metrics["quantity_2_count"]
        and directions["LONG"] == metrics["long_entry_fills"]
        and directions["SHORT"] == metrics["short_entry_fills"]
        and reasons["STRUCTURAL_STOP"] == metrics["structural_stop_exits"]
        and reasons["EMA20_POSITION_EXIT"] == metrics["ema20_exits"],
        "fill/quantity/direction count mismatch",
    )
    _require(
        sum(quantities.values()) == quantities[1] + quantities[2]
        and directions["LONG"] + directions["SHORT"] == metrics["entry_fills"]
        and reasons["STRUCTURAL_STOP"] + reasons["EMA20_POSITION_EXIT"] == metrics["closed_trades"]
        and len({entry["execution_bar_index"] for entry in life["entries"]})
        == metrics["entry_fills"],
        "duplicate/unsupported fill or exit",
    )
    for record in closed:
        _require(
            _fraction(record["entry_fee_usd"]) + _fraction(record["exit_fee_usd"])
            == _fraction(record["total_fees_usd"])
            and _fraction(record["gross_price_pnl_usd"]) - _fraction(record["total_fees_usd"])
            == _fraction(record["net_realized_pnl_usd"]),
            "closed accounting mismatch",
        )
    for record in (*closed, *opened):
        provenance = record["immutable_provenance"]
        _require(
            provenance["entry"] in life["entries"]
            and provenance["risk_decision"] in life["risk_decisions"]
            and provenance["confirmation"] in life["confirmations"]
            and provenance["pullback"] in life["pullbacks"]
            and provenance["risk_decision"]["approved_quantity"] == record["approved_quantity"],
            "trade provenance does not reconcile with native histories",
        )
        accounting = provenance["accounting"]
        for name in ("entry", "exit"):
            cost = accounting[name]
            if cost is None:
                continue
            native_cost = assembly.costs.calculate_fill_cost_v2(
                base_fill_price=_fraction(cost["base_fill_price"]),
                action=assembly.costs.FillActionV2(cost["action"]),
                quantity=record["approved_quantity"],
            )
            _require(cost == _native(native_cost), "native frozen fill costs mismatch")
            _require(
                record[name + "_base_fill_price"] == cost["base_fill_price"]
                and record[name + "_effective_fill_price"]
                == cost["effective_fill_price_after_slippage"]
                and record[name + "_fee_usd"] == cost["fee_usd"],
                "actual fill cost provenance mismatch",
            )
    _require(
        all(record["immutable_provenance"]["exit"] in life["exits"] for record in closed),
        "exit provenance does not reconcile with native histories",
    )
    diagnostics = document["diagnostic_trades_per_trading_day_session"]
    _require(
        sum(row["entry_fills"] for row in diagnostics) == metrics["entry_fills"]
        and sum(row["closed_trades"] for row in diagnostics) == metrics["closed_trades"],
        "session diagnostics do not reconcile",
    )
    closed_fees = sum((_fraction(r["total_fees_usd"]) for r in closed), Fraction())
    open_fees = sum((_fraction(r["entry_fee_usd"]) for r in opened), Fraction())
    gross = sum((_fraction(r["gross_price_pnl_usd"]) for r in closed), Fraction())
    _require(
        closed_fees == _fraction(metrics["closed_trade_fees_usd"])
        and open_fees == _fraction(metrics["open_entry_fees_usd"])
        and closed_fees + open_fees == _fraction(metrics["total_fees_usd"])
        and gross == _fraction(metrics["gross_price_pnl_usd"])
        and gross - closed_fees == _fraction(metrics["net_realized_pnl_usd"])
        and screen.maximum_marked_equity_drawdown_usd
        == _fraction(metrics["maximum_marked_equity_drawdown_usd"])
        and marks[-1].unrealized_pnl_usd == _fraction(metrics["unrealized_pnl_at_end_usd"])
        and marks[-1].marked_equity_usd == _fraction(metrics["marked_equity_at_end_usd"]),
        "equity/actual fee reconciliation mismatch",
    )
    diagnostic_slippage = sum(
        (
            _fraction(cost["slippage_cost_usd"])
            for record in (*closed, *opened)
            for cost in (
                record["immutable_provenance"]["accounting"]["entry"],
                record["immutable_provenance"]["accounting"]["exit"],
            )
            if cost is not None
        ),
        Fraction(),
    )
    _require(
        diagnostic_slippage == _fraction(metrics["diagnostic_total_slippage_cost_usd"])
        and sum(r["direction"] == "LONG" for r in closed) == metrics["long_closed_trades"]
        and sum(r["direction"] == "SHORT" for r in closed) == metrics["short_closed_trades"],
        "closed direction/slippage diagnostic mismatch",
    )
    origin = timestamps[0]
    for segment in document["segments"]:
        group = []
        for record in closed:
            elapsed = _timestamp(record["exit_timestamp"]) - origin
            offset = (elapsed.days * 86400 + elapsed.seconds) * 1_000_000 + elapsed.microseconds
            first, last = (
                _fraction(segment["start_offset_microseconds"]),
                _fraction(segment["end_offset_microseconds"]),
            )
            if first <= offset < last or segment["label"] == "DEVELOPMENT_S3" and offset == last:
                group.append(record)
        for name in ("gross_price_pnl_usd", "total_fees_usd", "diagnostic_slippage_cost_usd"):
            target = (
                "diagnostic_total_slippage_cost_usd"
                if name == "diagnostic_slippage_cost_usd"
                else name
            )
            _require(
                sum((_fraction(r[name]) for r in group), Fraction()) == _fraction(segment[target]),
                "exit-timestamp segment cost attribution mismatch",
            )
        _require(
            sum(r["direction"] == "LONG" for r in group) == segment["long_closed_trades"]
            and sum(r["direction"] == "SHORT" for r in group) == segment["short_closed_trades"]
            and sum(r["exit_reason"] == "STRUCTURAL_STOP" for r in group)
            == segment["structural_stop_exits"]
            and sum(r["exit_reason"] == "EMA20_POSITION_EXIT" for r in group)
            == segment["ema20_exits"],
            "segment direction/exit count mismatch",
        )


def validate_development_result_v2(document: dict, bindings: VerifiedReplayBindingsV2) -> None:
    """Fail closed on the frozen schema, identity and cross-record accounting invariants."""
    try:
        _validate_result(document, bindings)
    except DevelopmentReplayV2Error:
        raise
    except (KeyError, IndexError, TypeError, ValueError, ZeroDivisionError) as exc:
        raise DevelopmentReplayV2Error("invalid result/provenance: FAIL_CLOSED") from exc


@dataclass(frozen=True)
class DevelopmentReplayResultV2:
    """Immutable canonical output bytes; reading document returns a fresh copy."""

    canonical_utf8: bytes

    @property
    def document(self) -> dict:
        """Fresh decoded result, including exact rational monetary values."""
        return _decode_json(self.canonical_utf8)

    @property
    def output_sha256(self) -> str:
        """Frozen schema digest: canonical payload with this digest field omitted."""
        return self.document["output_sha256"]


def evaluate_synthetic_development_replay_v2(
    raw: bytes,
    *,
    bindings: VerifiedReplayBindingsV2,
) -> DevelopmentReplayResultV2:
    """Exercise adapter/metrics on explicitly invented input, never the canonical RAW."""
    _require(type(raw) is bytes, "synthetic bytes required")
    digest = _sha(raw)
    _require(digest != CANONICAL_DATASET_RAW_SHA256, "canonical DEVELOPMENT cannot be synthetic")
    bars = parse_ninjatrader_last_rows_v2(raw)
    document = _assemble_result(
        bars, digest, "synthetic-" + digest[:16] + "-v1", bindings, "SYNTHETIC_ONLY"
    )
    validate_development_result_v2(document, bindings)
    return DevelopmentReplayResultV2(canonical_replay_bytes_v2(document))


def execute_registered_development_replay_v2(
    raw_path: str | Path,
    *,
    bindings: VerifiedReplayBindingsV2,
    registration_path: str | Path,
    output_path: str | Path,
    execution_gate: str | None = None,
) -> DevelopmentReplayResultV2:
    """Future gate only: claim the registered original once, then verify RAW before replay.

    A failed claim/load/execution is fail-closed and never silently retried. A
    separate future determinism-proof gate must preserve the original verdict.
    This function is not called on real data during the implementation gate.
    """
    _require_execution_gate(execution_gate)
    registration = Path(registration_path).resolve()
    _require(
        registration
        == REPOSITORY / "docs/evidence/EMA_PULLBACK_V2_DEVELOPMENT_REPLAY_IMPLEMENTATION.json",
        "only the canonical original run registration is executable",
    )
    registered_bytes = registration.read_bytes()
    identity = _verify_registration(registered_bytes, bindings)
    output = Path(output_path)
    _require(not output.exists(), "existing result cannot be overwritten")
    claim = registration.with_suffix(registration.suffix + ".original-execution-claim")
    try:
        with claim.open("xb") as stream:
            stream.write(canonical_replay_bytes_v2(identity))
    except FileExistsError as exc:
        raise DevelopmentReplayV2Error(
            "original DEVELOPMENT run already claimed: FAIL_CLOSED"
        ) from exc
    bars = load_canonical_development_raw_v2(
        raw_path,
        bindings=bindings,
        registered_implementation_bytes=registered_bytes,
        execution_gate=execution_gate,
    )
    document = _assemble_result(
        bars,
        CANONICAL_DATASET_RAW_SHA256,
        CANONICAL_DATASET_ID,
        bindings,
        "AUTHORIZED_EXPOSED_DEVELOPMENT",
    )
    validate_development_result_v2(document, bindings)
    result = DevelopmentReplayResultV2(canonical_replay_bytes_v2(document))
    with output.open("xb") as stream:
        stream.write(result.canonical_utf8)
    return result
