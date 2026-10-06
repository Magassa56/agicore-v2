"""Precommitted V2 DEVELOPMENT screening; no prices, strategy runner or data loader.

Inputs to these pure functions are metadata and accounting records. This tool
does not authorize replay: protocol merge and a separate lineage gate come first.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable
from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime, timedelta
from enum import Enum
from fractions import Fraction

STRATEGY_MANIFEST_SHA256 = "965b44c837477bac8a81bbcde5df354997fcd84a0afd4f66f76a30e0a654240a"
DEVELOPMENT_PROTOCOL_SHA256 = "68dc6e6409aea4efb88e4a19e09a7ba17a68043a79f14ec23e569d3353267402"


class ProtocolError(ValueError):
    """Fail-closed protocol, provenance or evidence error; never a performance verdict."""


class InfiniteProfitFactor(str, Enum):
    POSITIVE_INFINITY = "POSITIVE_INFINITY"


class Verdict(str, Enum):
    INSUFFICIENT_SAMPLE = "INSUFFICIENT_SAMPLE"
    GO_TO_INDEPENDENT_VALIDATION = "GO_TO_INDEPENDENT_VALIDATION"
    NO_GO_BASELINE = "NO_GO_BASELINE"


def _json_default(value: object) -> object:
    if isinstance(value, Fraction):
        return {"numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, datetime):
        return value.isoformat()
    if is_dataclass(value) and not isinstance(value, type):
        return asdict(value)
    raise TypeError(f"unsupported canonical type: {type(value).__name__}")


def canonical_bytes(value: object) -> bytes:
    """Serialize exact records deterministically as sorted compact UTF-8 JSON + LF."""
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
            default=_json_default,
        )
        + "\n"
    ).encode("utf-8")


@dataclass(frozen=True)
class VerifiedProtocol:
    """Immutable exact documents; mutable caller dictionaries are never retained."""

    protocol_bytes: bytes
    strategy_manifest_bytes: bytes

    def __post_init__(self) -> None:
        for raw, expected in (
            (self.protocol_bytes, DEVELOPMENT_PROTOCOL_SHA256),
            (self.strategy_manifest_bytes, STRATEGY_MANIFEST_SHA256),
        ):
            if type(raw) is not bytes or hashlib.sha256(raw).hexdigest() != expected:
                raise ProtocolError("document SHA-256 mismatch: FAIL_CLOSED")
        document = json.loads(self.protocol_bytes)
        if canonical_bytes(document) != self.protocol_bytes:
            raise ProtocolError("protocol serialization is not canonical")
        if document["strategy"]["strategy_manifest_sha256"] != STRATEGY_MANIFEST_SHA256:
            raise ProtocolError("protocol strategy binding mismatch")

    @property
    def document(self) -> dict:
        """Return a fresh parsed copy, leaving the verified bytes immutable."""
        return json.loads(self.protocol_bytes)


def verify_protocol(
    protocol_bytes: bytes,
    strategy_manifest_bytes: bytes,
    *,
    claimed_protocol_sha256: str,
    claimed_strategy_manifest_sha256: str,
) -> VerifiedProtocol:
    """Reject wrong claimed hashes as well as modified actual document bytes."""
    if (
        claimed_protocol_sha256 != DEVELOPMENT_PROTOCOL_SHA256
        or claimed_strategy_manifest_sha256 != STRATEGY_MANIFEST_SHA256
    ):
        raise ProtocolError("claimed protocol/strategy hash mismatch: FAIL_CLOSED")
    return VerifiedProtocol(protocol_bytes, strategy_manifest_bytes)


def _utc(value: datetime) -> None:
    if not isinstance(value, datetime) or value.utcoffset() != timedelta(0):
        raise ProtocolError("timestamp must be timezone-aware UTC")


def _exact(value: Fraction) -> None:
    if type(value) is not Fraction:
        raise ProtocolError("accounting values must be exact Fraction; no float/rounding")


@dataclass(frozen=True)
class RunIdentity:
    """Four immutable hashes, independent of output; this is not replay authorization."""

    strategy_manifest_sha256: str
    development_protocol_sha256: str
    dataset_raw_sha256: str
    runner_source_sha256: str

    def __post_init__(self) -> None:
        if (
            self.strategy_manifest_sha256 != STRATEGY_MANIFEST_SHA256
            or self.development_protocol_sha256 != DEVELOPMENT_PROTOCOL_SHA256
        ):
            raise ProtocolError("run strategy/protocol binding mismatch: FAIL_CLOSED")
        for value in asdict(self).values():
            if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
                raise ProtocolError("run identity requires four SHA-256 hex digests")

    @property
    def sha256(self) -> str:
        """Hash the canonical identity; reruns must retain this exact identity."""
        return hashlib.sha256(canonical_bytes(self)).hexdigest()


def verify_determinism_rerun(
    original: RunIdentity,
    repeated: RunIdentity,
    *,
    original_output_sha256: str,
    repeated_output_sha256: str,
) -> None:
    """Accept only the same inputs/code/output; never rewrite the original verdict."""
    if type(original) is not RunIdentity or type(repeated) is not RunIdentity:
        raise ProtocolError("immutable run identities required")
    if original != repeated:
        raise ProtocolError("rerun inputs or code differ from the original run")
    for value in (original_output_sha256, repeated_output_sha256):
        if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
            raise ProtocolError("output SHA-256 required")
    if original_output_sha256 != repeated_output_sha256:
        raise ProtocolError("rerun output differs; original verdict remains unchanged")


@dataclass(frozen=True)
class ContractCandidate:
    """Declared metadata only; eligibility facts need evidence in the future lineage gate."""

    contract_id: str
    expiration_utc: datetime
    instrument: str
    contract_type: str
    interval: str
    data_type: str
    merge_policy: str
    trading_hours_template: str
    completed: bool | None
    used_for_v1_performance: bool | None
    used_for_v2_performance: bool | None
    v2_performance_inspected: bool | None
    clean_lineage_establishable: bool | None

    def __post_init__(self) -> None:
        _utc(self.expiration_utc)
        if not isinstance(self.contract_id, str) or not self.contract_id:
            raise ProtocolError("candidate contract id is required")
        for name in (
            "completed",
            "used_for_v1_performance",
            "used_for_v2_performance",
            "v2_performance_inspected",
            "clean_lineage_establishable",
        ):
            if getattr(self, name) is not None and type(getattr(self, name)) is not bool:
                raise ProtocolError("eligibility facts must be explicit bool or unknown None")


@dataclass(frozen=True)
class DatasetSelection:
    candidate_contract_id: str | None
    status: str
    rejected_candidates: tuple[tuple[str, str], ...]


def select_development_candidate(
    protocol: VerifiedProtocol, candidates: Iterable[ContractCandidate]
) -> DatasetSelection:
    """Sort metadata by expiration, reject contamination, and leave lineage pending."""
    if type(protocol) is not VerifiedProtocol:
        raise ProtocolError("verified protocol required")
    rule = protocol.document["dataset_selection_rule"]
    records = tuple(candidates)
    if any(type(item) is not ContractCandidate for item in records):
        raise ProtocolError("candidate metadata record required")
    if len({item.contract_id for item in records}) != len(records):
        raise ProtocolError("duplicate contract identity")
    if len({item.expiration_utc for item in records}) != len(records):
        raise ProtocolError("ambiguous equal-expiration candidates; no arbitrary priority")
    rejected = []
    for item in sorted(records, key=lambda value: value.expiration_utc, reverse=True):
        if item.v2_performance_inspected is True:
            reason = "REJECT_DATASET_CONTAMINATED"
        elif item.contract_id in rule["explicitly_excluded_contracts"]:
            reason = "REJECT_DATASET_PREVIOUSLY_USED"
        elif any(getattr(item, name) != value for name, value in rule["required_metadata"].items()):
            reason = "REJECT_DATASET_METADATA"
        elif (
            item.completed is not True
            or item.used_for_v1_performance is not False
            or item.used_for_v2_performance is not False
            or item.v2_performance_inspected is not False
            or item.clean_lineage_establishable is not True
        ):
            reason = "REJECT_DATASET_INELIGIBLE_OR_UNPROVEN"
        else:
            return DatasetSelection(item.contract_id, "CANDIDATE_PENDING_LINEAGE", tuple(rejected))
        rejected.append((item.contract_id, reason))
    return DatasetSelection(None, "NO_ELIGIBLE_DEVELOPMENT_CANDIDATE", tuple(rejected))


@dataclass(frozen=True)
class ClosedTrade:
    trade_index: int
    entry_timestamp_utc: datetime
    exit_timestamp_utc: datetime
    net_realized_pnl_usd: Fraction

    def __post_init__(self) -> None:
        _utc(self.entry_timestamp_utc)
        _utc(self.exit_timestamp_utc)
        _exact(self.net_realized_pnl_usd)
        if type(self.trade_index) is not int or self.trade_index < 1:
            raise ProtocolError("trade indices start at one")
        if self.exit_timestamp_utc < self.entry_timestamp_utc:
            raise ProtocolError("exit precedes entry")


@dataclass(frozen=True)
class MarkedEquityPoint:
    bar_index: int
    timestamp_utc: datetime
    realized_equity_usd: Fraction
    unrealized_pnl_usd: Fraction

    def __post_init__(self) -> None:
        _utc(self.timestamp_utc)
        _exact(self.realized_equity_usd)
        _exact(self.unrealized_pnl_usd)
        if type(self.bar_index) is not int or self.bar_index < 0:
            raise ProtocolError("closed bar index must be nonnegative")

    @property
    def marked_equity_usd(self) -> Fraction:
        """Realized plus still-unrealized equity; never a synthetic exit."""
        return self.realized_equity_usd + self.unrealized_pnl_usd


def profit_factor(values: Iterable[Fraction]) -> Fraction | InfiniteProfitFactor:
    """Exact net profit factor; no losses gives +infinity only with positive profit."""
    pnls = tuple(values)
    for value in pnls:
        _exact(value)
    gains = sum((value for value in pnls if value > 0), Fraction())
    losses = -sum((value for value in pnls if value < 0), Fraction())
    if losses:
        return gains / losses
    return InfiniteProfitFactor.POSITIVE_INFINITY if gains else Fraction()


def maximum_consecutive_losses(values: Iterable[Fraction]) -> int:
    """Zero-net trades reset a loss streak, as do positive-net trades."""
    maximum = current = 0
    for value in values:
        _exact(value)
        current = current + 1 if value < 0 else 0
        maximum = max(maximum, current)
    return maximum


def maximum_marked_drawdown(points: Iterable[MarkedEquityPoint]) -> Fraction:
    """Exact running-peak drawdown including the zero starting equity baseline."""
    peak = maximum = Fraction()
    previous = None
    for point in points:
        if type(point) is not MarkedEquityPoint:
            raise ProtocolError("marked equity record required")
        if previous is not None and point.timestamp_utc <= previous:
            raise ProtocolError("marks must be strictly chronological")
        previous = point.timestamp_utc
        peak = max(peak, point.marked_equity_usd)
        maximum = max(maximum, peak - point.marked_equity_usd)
    return maximum


def _microseconds(span: timedelta) -> int:
    return (span.days * 86400 + span.seconds) * 1_000_000 + span.microseconds


@dataclass(frozen=True)
class TradeMetrics:
    closed_trades: int
    net_realized_pnl_usd: Fraction
    profit_factor: Fraction | InfiniteProfitFactor
    wins: int
    losses: int
    breakeven_trades: int
    average_trade_usd: Fraction | None
    median_trade_usd: Fraction | None
    win_rate: Fraction | None
    maximum_consecutive_losses: int


def _trade_metrics(trades: tuple[ClosedTrade, ...]) -> TradeMetrics:
    pnls = tuple(trade.net_realized_pnl_usd for trade in trades)
    count = len(pnls)
    total = sum(pnls, Fraction())
    ordered = sorted(pnls)
    median = None
    if count:
        median = (ordered[(count - 1) // 2] + ordered[count // 2]) / 2
    wins = sum(value > 0 for value in pnls)
    return TradeMetrics(
        count,
        total,
        profit_factor(pnls),
        wins,
        sum(value < 0 for value in pnls),
        sum(value == 0 for value in pnls),
        total / count if count else None,
        median,
        Fraction(wins, count) if count else None,
        maximum_consecutive_losses(pnls),
    )


@dataclass(frozen=True)
class SegmentMetrics:
    label: str
    start_offset_microseconds: Fraction
    end_offset_microseconds: Fraction
    metrics: TradeMetrics

    @property
    def profitable(self) -> bool:
        """Strictly positive net realized PnL; zero is not profitable."""
        return self.metrics.net_realized_pnl_usd > 0


@dataclass(frozen=True)
class ScreeningResult:
    """Screening evidence summary, not the complete future replay RESULT_SCHEMA."""

    run_identity: RunIdentity
    dataset_role: str
    first_timestamp_utc: datetime
    last_timestamp_utc: datetime
    metrics: TradeMetrics
    maximum_marked_equity_drawdown_usd: Fraction
    segments: tuple[SegmentMetrics, ...]
    open_trades_at_end: int
    unrealized_pnl_at_end_usd: Fraction
    verdict: Verdict
    failed_criteria: tuple[str, ...]
    next_gate: str


def _validate_evidence(
    trades: tuple[ClosedTrade, ...],
    marks: tuple[MarkedEquityPoint, ...],
    timestamps: tuple[datetime, ...],
    open_count: int,
) -> None:
    if type(open_count) is not int or open_count not in (0, 1):
        raise ProtocolError("one-position policy requires zero or one open trade")
    if len(timestamps) < 2:
        raise ProtocolError("positive elapsed-time source interval required")
    for index, timestamp in enumerate(timestamps):
        _utc(timestamp)
        if index and timestamp <= timestamps[index - 1]:
            raise ProtocolError("source closed-bar timestamps must strictly increase")
    if len(marks) != len(timestamps):
        raise ProtocolError("one mark per actual closed bar required")
    for index, trade in enumerate(trades, 1):
        if type(trade) is not ClosedTrade or trade.trade_index != index:
            raise ProtocolError("closed trades must have consecutive unique indices")
        if index > 1 and trade.exit_timestamp_utc < trades[index - 2].exit_timestamp_utc:
            raise ProtocolError("closed trades must be in causal exit order")
        if (
            not timestamps[0]
            <= trade.entry_timestamp_utc
            <= trade.exit_timestamp_utc
            <= timestamps[-1]
        ):
            raise ProtocolError("trade is outside source timestamps")
    realized = Fraction()
    cursor = 0
    for index, (point, timestamp) in enumerate(zip(marks, timestamps)):
        if type(point) is not MarkedEquityPoint or point.bar_index != index:
            raise ProtocolError("marked bar coverage is incomplete/duplicated")
        if point.timestamp_utc != timestamp:
            raise ProtocolError("marked timestamp does not match closed bar")
        while cursor < len(trades) and trades[cursor].exit_timestamp_utc <= timestamp:
            realized += trades[cursor].net_realized_pnl_usd
            cursor += 1
        if point.realized_equity_usd != realized:
            raise ProtocolError("realized equity does not reconcile with net closed trades")
    if not open_count and marks[-1].unrealized_pnl_usd != 0:
        raise ProtocolError("final unrealized equity without an open position")


def _pf_at_least(value: Fraction | InfiniteProfitFactor, minimum: str) -> bool:
    return value is InfiniteProfitFactor.POSITIVE_INFINITY or value >= Fraction(minimum)


def evaluate_screening(
    protocol: VerifiedProtocol,
    *,
    run_identity: RunIdentity,
    dataset_role: str,
    closed_trades: Iterable[ClosedTrade],
    marked_equity: Iterable[MarkedEquityPoint],
    closed_bar_timestamps: Iterable[datetime],
    open_trades_at_end: int = 0,
) -> ScreeningResult:
    """Compute a mechanical net-only verdict, with sample insufficiency checked first.

    No raw prices or strategy components are read. The current PR exercises this
    function exclusively with invented accounting evidence and metadata.
    """
    if type(protocol) is not VerifiedProtocol or type(run_identity) is not RunIdentity:
        raise ProtocolError("verified protocol and immutable run identity required")
    document = protocol.document
    if dataset_role != document["dataset_selection_rule"]["dataset_role"]:
        raise ProtocolError("only EXPOSED_DEVELOPMENT is admitted; OOS remains sealed")
    trades, marks, timestamps = (
        tuple(closed_trades),
        tuple(marked_equity),
        tuple(closed_bar_timestamps),
    )
    _validate_evidence(trades, marks, timestamps, open_trades_at_end)
    span = _microseconds(timestamps[-1] - timestamps[0])
    groups = [[], [], []]
    for trade in trades:
        offset = _microseconds(trade.exit_timestamp_utc - timestamps[0])
        group = 0 if offset * 3 < span else 1 if offset * 3 < 2 * span else 2
        groups[group].append(trade)
    contract = document["segment_contract"]
    segments = tuple(
        SegmentMetrics(
            label,
            Fraction(index * span, 3),
            Fraction((index + 1) * span, 3),
            _trade_metrics(tuple(group)),
        )
        for index, (label, group) in enumerate(zip(contract["labels"], groups))
    )
    metrics = _trade_metrics(trades)
    drawdown = maximum_marked_drawdown(marks)
    thresholds = document["screening_thresholds"]
    insufficient = []
    if metrics.closed_trades < thresholds["minimum_closed_trades"]:
        insufficient.append("minimum_closed_trades")
    for segment in segments:
        if segment.metrics.closed_trades < contract["minimum_closed_trades_per_segment"]:
            insufficient.append(f"{segment.label}.minimum_closed_trades")
    failures = []
    for name, passed in (
        (
            "minimum_net_pnl_usd",
            metrics.net_realized_pnl_usd >= Fraction(thresholds["minimum_net_pnl_usd"]),
        ),
        (
            "minimum_profit_factor",
            _pf_at_least(metrics.profit_factor, thresholds["minimum_profit_factor"]),
        ),
        (
            "maximum_marked_equity_drawdown_usd",
            drawdown <= Fraction(thresholds["maximum_marked_equity_drawdown_usd"]),
        ),
        (
            "maximum_consecutive_losses",
            metrics.maximum_consecutive_losses <= thresholds["maximum_consecutive_losses"],
        ),
        (
            "minimum_profitable_segments",
            sum(segment.profitable for segment in segments)
            >= contract["minimum_profitable_segments"],
        ),
    ):
        if not passed:
            failures.append(name)
    for segment in segments:
        if not _pf_at_least(
            segment.metrics.profit_factor, contract["minimum_segment_profit_factor"]
        ):
            failures.append(f"{segment.label}.minimum_profit_factor")
        if segment.metrics.net_realized_pnl_usd < Fraction(contract["minimum_segment_net_pnl_usd"]):
            failures.append(f"{segment.label}.minimum_net_pnl_usd")
    if insufficient:
        verdict = Verdict.INSUFFICIENT_SAMPLE
        failed = tuple(insufficient)
        next_gate = "EMA_PULLBACK_V2_DEVELOPMENT_SAMPLE_EXTENSION_REQUIRED"
    elif failures:
        verdict = Verdict.NO_GO_BASELINE
        failed = tuple(failures)
        next_gate = "EMA_PULLBACK_V2_NEW_HYPOTHESIS_PROTOCOL_REQUIRED"
    else:
        verdict = Verdict.GO_TO_INDEPENDENT_VALIDATION
        failed = ()
        next_gate = "EMA_PULLBACK_V2_INDEPENDENT_VALIDATION_PROTOCOL_REQUIRED"
    return ScreeningResult(
        run_identity,
        dataset_role,
        timestamps[0],
        timestamps[-1],
        metrics,
        drawdown,
        segments,
        open_trades_at_end,
        marks[-1].unrealized_pnl_usd,
        verdict,
        failed,
        next_gate,
    )
