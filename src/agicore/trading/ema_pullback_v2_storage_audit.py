"""Independent bounded native-evidence audit; no strategy imports or execution.

This verifier derives accounting from immutable fills and source Close witnesses.
It checks provenance, not whether a trading signal should have been generated.
The exact frozen-reference byte commitment separately protects all signal records.
"""

from __future__ import annotations

import re
from collections import Counter
from datetime import UTC, datetime, time, timedelta
from decimal import Decimal
from fractions import Fraction
from itertools import pairwise
from zoneinfo import ZoneInfo

from .ema_pullback_v2_storage_format import (
    MAX_OBSERVATIONS,
    REAL_RAW_SHA,
    ROOT,
    StorageProofError,
    canonical,
    contracts,
    parse_canonical,
    require,
    sha,
)


def rational(value):
    """Decode canonical native rationals without accepting coercion or floats."""
    require(type(value) is dict and set(value) == {"numerator", "denominator"}, "rational shape")
    n, d = value["numerator"], value["denominator"]
    require(type(n) is type(d) is int and d > 0, "rational integers")
    result = Fraction(n, d)
    require(result.numerator == n and result.denominator == d, "rational spelling")
    return result


def native(value):
    """Encode independently calculated exact audit quantities."""
    if isinstance(value, Fraction):
        return {"numerator": value.numerator, "denominator": value.denominator}
    if type(value) is dict:
        return {k: native(v) for k, v in value.items()}
    if type(value) in (list, tuple):
        return [native(v) for v in value]
    require(value is None or type(value) in (str, int, bool), "unsupported audit value")
    return value


def timestamp(value):
    """Require the frozen UTC spelling; preserve the supplied timestamp."""
    require(type(value) is str and value.endswith("Z"), "UTC timestamp required")
    parsed = datetime.fromisoformat(value)
    require(
        parsed.utcoffset() == timedelta() and parsed.isoformat().replace("+00:00", "Z") == value,
        "noncanonical UTC timestamp",
    )
    return parsed


def schema_check(value, schema, root):
    """Apply all keywords present in the frozen native schema, without execution."""
    if "$ref" in schema:
        target = root
        for part in schema["$ref"].removeprefix("#/").split("/"):
            target = target[part]
        return schema_check(value, target, root)
    if "anyOf" in schema:
        for option in schema["anyOf"]:
            try:
                schema_check(value, option, root)
                return
            except StorageProofError:
                pass
        raise StorageProofError("native schema anyOf: FAIL_CLOSED")
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
        require(type(value) is types[kind], "native schema type")
    if "const" in schema:
        require(type(value) is type(schema["const"]) and value == schema["const"], "native const")
    if "enum" in schema:
        require(value in schema["enum"], "native enum")
    if kind == "object":
        require(set(schema.get("required", ())) <= value.keys(), "native missing field")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            require(value.keys() <= properties.keys(), "native extra field")
        for key in value.keys() & properties.keys():
            schema_check(value[key], properties[key], root)
    elif kind == "array":
        require(
            schema.get("minItems", 0) <= len(value) <= schema.get("maxItems", len(value)),
            "native array length",
        )
        for child in value:
            schema_check(child, schema.get("items", {}), root)
    elif kind == "string":
        require(len(value) >= schema.get("minLength", 0), "native string length")
        if "pattern" in schema:
            require(re.search(schema["pattern"], value) is not None, "native string pattern")
        if schema.get("format") == "date-time":
            timestamp(value)
    elif kind == "integer" and "minimum" in schema:
        require(value >= schema["minimum"], "native integer minimum")


def synthetic_source(raw: bytes, expected_sha: str) -> list[dict]:
    """Independently bind every witness to a registered invented source row."""
    require(type(raw) is bytes and sha(raw) == expected_sha != REAL_RAW_SHA, "synthetic source SHA")
    registration = parse_canonical(
        [
            (
                ROOT / "docs/evidence/EMA_PULLBACK_V2_RECOVERY_STORAGE_FIXTURE_REGISTRATION_V1.json"
            ).read_bytes()
        ]
    )
    require(
        any(f["raw_sha256"] == expected_sha for f in registration["native_fixtures"]),
        "source not in precommitted invented inventory",
    )
    rows, offset = [], 0
    for index, row in enumerate(raw.splitlines(keepends=True)):
        require(index < MAX_OBSERVATIONS and row.endswith(b"\n"), "bounded complete source rows")
        fields = row.rstrip(b"\r\n").decode("ascii").split(";")
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
                "source_row_size_bytes": len(row),
                "source_row_sha256": sha(row),
            }
        )
        offset += len(row)
    require(2 <= len(rows) <= MAX_OBSERVATIONS and offset == len(raw), "source coverage")
    return rows


def trade_statistics(pnls) -> dict:
    """Independent exact statistics, including zero-profit streak reset and infinity."""
    values = list(pnls)
    require(all(isinstance(v, Fraction) for v in values), "exact PnL values")
    count = len(values)
    gains = sum((v for v in values if v > 0), Fraction())
    losses = -sum((v for v in values if v < 0), Fraction())
    total = gains - losses
    streak = longest = 0
    for value in values:
        streak = streak + 1 if value < 0 else 0
        longest = max(longest, streak)
    ordered = sorted(values)
    median = (ordered[(count - 1) // 2] + ordered[count // 2]) / 2 if count else None
    wins = sum(v > 0 for v in values)
    return {
        "closed_trades": count,
        "wins": wins,
        "losses": sum(v < 0 for v in values),
        "breakeven_trades": sum(v == 0 for v in values),
        "net_realized_pnl_usd": total,
        "average_trade_usd": total / count if count else None,
        "median_trade_usd": median,
        "win_rate": Fraction(wins, count) if count else None,
        "profit_factor": gains / losses
        if losses
        else ("POSITIVE_INFINITY" if gains else Fraction()),
        "maximum_consecutive_losses": longest,
    }


def marked_drawdown(equities):
    """Running peak includes the zero starting equity."""
    peak = maximum = Fraction()
    for equity in equities:
        require(isinstance(equity, Fraction), "exact marked equity")
        peak = max(peak, equity)
        maximum = max(maximum, peak - equity)
    return maximum


def screening_verdict(metrics, segments, protocol):
    """Independently apply the immutable metadata thresholds, sample checks first."""
    thresholds, segment_rule = protocol["screening_thresholds"], protocol["segment_contract"]
    failures = []
    if metrics["closed_trades"] < thresholds["minimum_closed_trades"]:
        failures.append("minimum_closed_trades")
    for segment in segments:
        if segment["closed_trades"] < segment_rule["minimum_closed_trades_per_segment"]:
            failures.append(segment["label"] + ".minimum_closed_trades")
    if failures:
        return (
            "INSUFFICIENT_SAMPLE",
            failures,
            "EMA_PULLBACK_V2_DEVELOPMENT_SAMPLE_EXTENSION_REQUIRED",
        )

    def pf_pass(value, boundary):
        return value == "POSITIVE_INFINITY" or value >= Fraction(boundary)

    checks = [
        (
            "minimum_net_pnl_usd",
            metrics["net_realized_pnl_usd"] >= Fraction(thresholds["minimum_net_pnl_usd"]),
        ),
        (
            "minimum_profit_factor",
            pf_pass(metrics["profit_factor"], thresholds["minimum_profit_factor"]),
        ),
        (
            "maximum_marked_equity_drawdown_usd",
            metrics["maximum_marked_equity_drawdown_usd"]
            <= Fraction(thresholds["maximum_marked_equity_drawdown_usd"]),
        ),
        (
            "maximum_consecutive_losses",
            metrics["maximum_consecutive_losses"] <= thresholds["maximum_consecutive_losses"],
        ),
        (
            "minimum_profitable_segments",
            sum(s["net_realized_pnl_usd"] > 0 for s in segments)
            >= segment_rule["minimum_profitable_segments"],
        ),
    ]
    failures.extend(name for name, valid in checks if not valid)
    for segment in segments:
        if not pf_pass(segment["profit_factor"], segment_rule["minimum_segment_profit_factor"]):
            failures.append(segment["label"] + ".minimum_profit_factor")
        if segment["net_realized_pnl_usd"] < Fraction(segment_rule["minimum_segment_net_pnl_usd"]):
            failures.append(segment["label"] + ".minimum_net_pnl_usd")
    return (
        ("NO_GO_BASELINE", failures, "EMA_PULLBACK_V2_NEW_HYPOTHESIS_PROTOCOL_REQUIRED")
        if failures
        else (
            "GO_TO_INDEPENDENT_VALIDATION",
            [],
            "EMA_PULLBACK_V2_INDEPENDENT_VALIDATION_PROTOCOL_REQUIRED",
        )
    )


def _authority():
    addendum, protocol = contracts()
    for binding in (*addendum["parents"].values(), *addendum["reference_sources"]):
        require(
            sha((ROOT / binding["path"]).read_bytes()) == binding["sha256"], "frozen dependency"
        )
    strategy = parse_canonical(
        [(ROOT / addendum["parents"]["strategy_manifest"]["path"]).read_bytes()]
    )
    constants = {c["name"]: c["constants"] for c in strategy["components"]}
    return addendum, protocol, constants


def _clock(index, stamp, witnesses):
    require(type(index) is int and 0 <= index < len(witnesses), "provenance bar index")
    require(stamp == witnesses[index]["timestamp_utc"], "provenance clock")


def _lifecycle_audit(life, witnesses):
    for name, rows in life.items():
        require(
            type(rows) is list and len({sha(canonical(row)) for row in rows}) == len(rows),
            "duplicate lifecycle record: " + name,
        )
    events = life["events"]
    require(
        [e["event_bar_index"] for e in events] == sorted(e["event_bar_index"] for e in events),
        "event order",
    )
    for event in events:
        _clock(event["event_bar_index"], event["event_timestamp"], witnesses)
    for context in life["contexts"]:
        matching = [
            e
            for e in events
            if e["event_bar_index"] == context["source_event_bar_index"]
            and e["event_direction"] == context["source_event_direction"]
        ]
        require(
            {e["event_type"] for e in matching} == set(context["source_event_types"]),
            "context source events",
        )
        _clock(context["source_event_bar_index"], context["source_event_timestamp"], witnesses)
        require(context["state"] != "ACTIVE", "unfinished context")
    for pullback in life["pullbacks"]:
        require(pullback["pullback_qualified"] is True, "unqualified pullback")
        _clock(pullback["pullback_bar_index"], pullback["pullback_timestamp"], witnesses)
        require(
            any(
                c["state"] == "CONSUMED"
                and c["pullback_bar_index"] == pullback["pullback_bar_index"]
                and c["ema_reference"] == pullback["ema_reference"]
                and c["source_event_bar_index"] == pullback["context_event_bar_index"]
                and c["source_event_direction"] == pullback["context_direction"]
                for c in life["contexts"]
            ),
            "consumed pullback context",
        )
    for confirmation in life["confirmations"]:
        _clock(
            confirmation["confirmation_bar_index"],
            confirmation["confirmation_timestamp"],
            witnesses,
        )
        require(
            any(
                p["pullback_bar_index"] == confirmation["pullback_bar_index"]
                and p["ema_reference"] == confirmation["ema_reference"]
                for p in life["pullbacks"]
            ),
            "confirmation pullback",
        )
    for stop in life["stops"]:
        require(stop["confirmation"] in life["confirmations"], "stop confirmation")
        if stop["initial_stop_record"] is not None:
            require(
                stop["initial_stop_record"]["confirmation"] == stop["confirmation"],
                "initial stop source",
            )
    for risk in life["risk_decisions"]:
        require(
            risk["confirmation"] in life["confirmations"]
            and risk["consumed_context"] in life["contexts"],
            "risk provenance",
        )
        require(
            any(
                s["confirmation"] == risk["confirmation"]
                and s["initial_stop_record"] == risk["initial_stop_record"]
                for s in life["stops"]
            ),
            "risk stop source",
        )
    terminals = life["terminal_states"]
    require(terminals[0] == {"kind": "INPUT_DOMAIN", "state": "SYNTHETIC_ONLY"}, "synthetic only")
    require(terminals[1]["kind"] == "END_OF_DATA", "end-of-data evidence")
    grouped = {
        kind: [t["record"] for t in terminals if t["kind"] == kind]
        for kind in ("CONTEXT", "ENTRY_EXECUTION", "OPPORTUNITY", "EMA_EXIT_EXECUTION")
    }
    require(grouped["CONTEXT"] == life["contexts"], "terminal contexts")
    require(
        [e["execution"] for e in grouped["ENTRY_EXECUTION"] if e["execution"] is not None]
        == life["entries"],
        "terminal entry fills",
    )
    require(
        [
            o["confirmation"]["confirmation"]
            for o in grouped["OPPORTUNITY"]
            if o["confirmation"]["state"] == "CONFIRMED"
            and o["confirmation"]["confirmation"] is not None
        ]
        == life["confirmations"],
        "terminal confirmations",
    )
    require(
        [o["risk_decision"] for o in grouped["OPPORTUNITY"] if o["risk_decision"] is not None]
        == life["risk_decisions"],
        "terminal risk decisions",
    )
    for opportunity in grouped["OPPORTUNITY"]:
        require(
            opportunity["confirmation"]["opportunity"]["consumed_context"] in life["contexts"],
            "opportunity context",
        )
        require(
            opportunity["state"] not in ("AWAITING_CONFIRMATION", "PENDING_ENTRY_EXECUTION"),
            "unfinished opportunity",
        )
        if opportunity["execution"] is not None:
            require(opportunity["execution"] in grouped["ENTRY_EXECUTION"], "opportunity execution")
    require(
        [e["fill"] for e in grouped["EMA_EXIT_EXECUTION"] if e["fill"] is not None]
        == [e for e in life["exits"] if e.get("exit_reason") == "EMA20_POSITION_EXIT"],
        "terminal EMA fills",
    )


def _audit_trade(trade, life, witnesses, costs):
    p = trade["immutable_provenance"]
    quantity = trade["approved_quantity"]
    sign = 1 if trade["direction"] == "LONG" else -1
    entry, risk, confirmation, stop = (
        p[k] for k in ("entry", "risk_decision", "confirmation", "initial_stop")
    )
    for key, group in (
        ("entry", "entries"),
        ("risk_decision", "risk_decisions"),
        ("confirmation", "confirmations"),
        ("pullback", "pullbacks"),
    ):
        require(p[key] in life[group], "trade provenance membership: " + key)
    require(
        entry["confirmation"] == confirmation == risk["confirmation"] == stop["confirmation"],
        "confirmation join",
    )
    require(
        risk["initial_stop_record"] == stop
        and risk["decision"] == "APPROVE"
        and risk["approved_quantity"] == quantity
        and risk["direction"] == trade["direction"],
        "frozen sizing join",
    )
    context = p["regime"]["consumed_context"]
    require(context == risk["consumed_context"] and context in life["contexts"], "trade context")
    require(
        p["regime"]["events"]
        == [
            e
            for e in life["events"]
            if e["event_bar_index"] == context["source_event_bar_index"]
            and e["event_direction"] == context["source_event_direction"]
        ],
        "trade event provenance",
    )
    require(
        p["pullback"]["pullback_bar_index"]
        == context["pullback_bar_index"]
        == confirmation["pullback_bar_index"],
        "trade pullback join",
    )
    ei = entry["execution_bar_index"]
    _clock(ei, entry["execution_bar_timestamp"], witnesses)
    require(
        ei == confirmation["confirmation_bar_index"] + 1
        and trade["entry_timestamp"] == entry["execution_bar_timestamp"],
        "entry next observation/time",
    )
    require(
        trade["direction"] == entry["execution_side"]
        and trade["entry_base_fill_price"] == entry["execution_price_before_costs"],
        "entry price/direction join",
    )
    accounting = p["accounting"]
    require(
        accounting["sized_entry"]["execution"] == entry
        and accounting["sized_entry"]["risk_decision"] == risk,
        "accounting sized entry",
    )
    for side, action in (
        ("entry", "BUY" if sign > 0 else "SELL_SHORT"),
        ("exit", "SELL" if sign > 0 else "BUY_TO_COVER"),
    ):
        cost = accounting[side]
        if side == "exit" and trade["net_realized_pnl_usd"] is None:
            require(
                cost is None
                and accounting["stop_fill"] is None
                and accounting["ema_exit_fill"] is None
                and "exit" not in p,
                "open trade has no exit",
            )
            continue
        base = rational(trade[side + "_base_fill_price"])
        effective = base + (1 if action in ("BUY", "BUY_TO_COVER") else -1) * rational(
            costs["ADVERSE_SLIPPAGE_POINTS_PER_FILL"]
        )
        fee = quantity * rational(costs["FEE_PER_CONTRACT_PER_FILL_USD"])
        expected = {
            "quantity": quantity,
            "action": action,
            "base_fill_price": base,
            "effective_fill_price_after_slippage": effective,
            "fee_usd": fee,
            "slippage_cost_usd": quantity * rational(costs["TICK_VALUE_USD"]),
            "slippage_ticks": costs["ADVERSE_SLIPPAGE_TICKS_PER_FILL"],
        }
        require(cost == native(expected), "independent fill costs")
        require(
            trade[side + "_effective_fill_price"] == native(effective)
            and trade[side + "_fee_usd"] == native(fee),
            "trade effective price/fee",
        )
    if trade["net_realized_pnl_usd"] is None:
        require(trade["state"] == "OPEN_UNREALIZED", "open terminal state")
        return ei, None
    exit_record = p["exit"]
    require(exit_record in life["exits"], "exit lifecycle membership")
    if trade["exit_reason"] == "STRUCTURAL_STOP":
        xi = exit_record["trigger_bar_index"]
        xt = exit_record["trigger_bar_timestamp"]
        price = exit_record["base_stop_fill_price"]
        bound = exit_record["initial_stop_at_entry"]
        require(
            accounting["stop_fill"] == exit_record and accounting["ema_exit_fill"] is None,
            "stop accounting link",
        )
    else:
        xi, xt = exit_record["exit_execution_bar_index"], exit_record["exit_execution_timestamp"]
        price = exit_record["base_exit_fill_price"]
        bound = exit_record["signal"]["initial_stop_at_entry"]
        require(
            accounting["ema_exit_fill"] == exit_record and accounting["stop_fill"] is None,
            "EMA accounting link",
        )
    _clock(xi, xt, witnesses)
    require(
        xi >= ei and xt == trade["exit_timestamp"] and price == trade["exit_base_fill_price"],
        "exit clock/price",
    )
    require(
        bound["execution"] == entry and bound["initial_stop_record"] == stop,
        "immutable stop/entry join",
    )
    gross = (
        sign
        * (
            rational(trade["exit_effective_fill_price"])
            - rational(trade["entry_effective_fill_price"])
        )
        * rational(costs["POINT_VALUE_USD"])
        * quantity
    )
    fees = rational(trade["entry_fee_usd"]) + rational(trade["exit_fee_usd"])
    require(
        trade["gross_price_pnl_usd"] == native(gross)
        and trade["total_fees_usd"] == native(fees)
        and trade["net_realized_pnl_usd"] == native(gross - fees)
        and trade["diagnostic_slippage_cost_usd"]
        == native(2 * quantity * rational(costs["TICK_VALUE_USD"])),
        "independent net PnL / slippage once",
    )
    return ei, xi


def _aggregate(closed):
    return {
        "long_closed_trades": sum(r["direction"] == "LONG" for r in closed),
        "short_closed_trades": sum(r["direction"] == "SHORT" for r in closed),
        "structural_stop_exits": sum(r["exit_reason"] == "STRUCTURAL_STOP" for r in closed),
        "ema20_exits": sum(r["exit_reason"] == "EMA20_POSITION_EXIT" for r in closed),
        **{
            name: sum((rational(r[name]) for r in closed), Fraction())
            for name in ("gross_price_pnl_usd", "total_fees_usd")
        },
        "diagnostic_total_slippage_cost_usd": sum(
            (rational(r["diagnostic_slippage_cost_usd"]) for r in closed), Fraction()
        ),
    }


def _diagnostics(witnesses, closed, opened, addendum):
    lineage = parse_canonical(
        [(ROOT / addendum["parents"]["dataset_lineage"]["path"]).read_bytes()]
    )
    # Only the hash-bound calendar metadata is read, never its dataset paths.
    calendar_binding = lineage["gap_reconciliation"]["evidence"]
    raw = (ROOT / calendar_binding["path"]).read_bytes()
    require(sha(raw) == calendar_binding["sha256"], "calendar binding")
    calendar = parse_canonical([raw])
    zone = ZoneInfo(calendar["calendar_conversion"]["calendar_timezone"])
    closures = [
        (timestamp(g["previous_timestamp_utc"]), timestamp(g["next_timestamp_utc"]))
        for g in calendar["gaps"]
        if g["classification"].startswith("SCHEDULED_")
    ]
    off = {r["timestamp_utc"] for r in calendar["off_session_observed_rows"]}

    def bucket(text):
        ts = timestamp(text)
        local = ts.astimezone(zone)
        active = (local.weekday() < 5 and local.time() <= time(16)) or (
            local.weekday() in (6, 0, 1, 2, 3) and local.time() > time(17)
        )
        active = active and text not in off and not any(a < ts < b for a, b in closures)
        day = local.date() + (
            timedelta(days=1) if active and local.time() > time(17) else timedelta()
        )
        return (
            day.isoformat(),
            "CME_US_INDEX_FUTURES_ETH" if active else "OFF_SESSION_STORED_OBSERVATION",
        )

    counts = {bucket(w["timestamp_utc"]): [0, 0] for w in witnesses}
    for r in (*closed, *opened):
        counts[bucket(r["entry_timestamp"])][0] += 1
    for r in closed:
        counts[bucket(r["exit_timestamp"])][1] += 1
    return [
        {"trading_day": k[0], "session_id": k[1], "entry_fills": v[0], "closed_trades": v[1]}
        for k, v in sorted(counts.items())
    ]


def audit_native(document, witnesses, synthetic_raw: bytes):
    """Audit the entire bounded native result independently of producer aggregates."""
    try:
        return _audit_native(document, witnesses, synthetic_raw)
    except StorageProofError:
        raise
    except (KeyError, TypeError, ValueError, IndexError, ArithmeticError) as exc:
        raise StorageProofError("invalid native evidence: FAIL_CLOSED") from exc


def _audit_native(document, witnesses, synthetic_raw):
    addendum, protocol, constants = _authority()
    schema = protocol["result_schema"]
    schema_check(document, schema, schema)
    identity = document["run_identity"]
    require(
        identity["dataset_raw_sha256"] == sha(synthetic_raw) != REAL_RAW_SHA, "invented identity"
    )
    require(
        identity["strategy_manifest_sha256"] == addendum["parents"]["strategy_manifest"]["sha256"]
        and identity["development_protocol_sha256"]
        == addendum["parents"]["development_protocol"]["sha256"]
        and identity["runner_source_sha256"]
        == next(
            r["sha256"]
            for r in addendum["reference_sources"]
            if r["role"] == "FROZEN_REFERENCE_RUNNER"
        )
        and document["run_id_sha256"] == sha(canonical(identity)),
        "native reference run binding",
    )
    require(
        document["dataset_lineage_manifest_sha256"]
        == addendum["parents"]["dataset_lineage"]["sha256"]
        and document["dataset_id"] == "synthetic-" + sha(synthetic_raw)[:16] + "-v1",
        "native dataset binding",
    )
    require(
        document["output_sha256"]
        == sha(canonical({k: v for k, v in document.items() if k != "output_sha256"})),
        "native embedded output SHA",
    )
    require(
        witnesses == synthetic_source(synthetic_raw, identity["dataset_raw_sha256"]),
        "source Close witnesses",
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
