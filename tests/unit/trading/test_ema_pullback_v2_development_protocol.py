"""Invented accounting/metadata only: never run V2 or open any historical dataset."""

import hashlib
import importlib.util
import json
import sys
from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta
from fractions import Fraction as F
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "ema_pullback_v2_development_protocol",
    ROOT / "tools/ema_pullback_v2_development_protocol.py",
)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)
START = datetime(2099, 1, 1, tzinfo=UTC)  # Entirely fictional accounting timeline.
EPSILON = F(1, 1_000_000_000)


@pytest.fixture
def protocol():
    return m.verify_protocol(
        (ROOT / "docs/evidence/EMA_PULLBACK_V2_DEVELOPMENT_PROTOCOL.json").read_bytes(),
        (ROOT / "docs/evidence/EMA_PULLBACK_V2_REGIME_GATED_BASELINE_MANIFEST.json").read_bytes(),
        claimed_protocol_sha256=m.DEVELOPMENT_PROTOCOL_SHA256,
        claimed_strategy_manifest_sha256=m.STRATEGY_MANIFEST_SHA256,
    )


def identity():
    # Invented digest labels; not the hash of any real price dataset or replay runner.
    return m.RunIdentity(
        m.STRATEGY_MANIFEST_SHA256, m.DEVELOPMENT_PROTOCOL_SHA256, "a" * 64, "b" * 64
    )


def groups():
    return [
        [F(200), F(-100)] + [F()] * 32,
        [F(200), F(-100)] + [F()] * 31,
        [F(100), F(-100)] + [F()] * 31,
    ]


def evidence(values=None, *, marked_overrides=None, final_unrealized=F()):
    """Build fictional already-accounted trades and one equity point per fictional close."""
    values = groups() if values is None else values
    trades = []
    for segment, pnls in enumerate(values):
        for offset, pnl in enumerate(pnls):
            exit_at = START + timedelta(minutes=segment * 100 + offset + 10)
            trades.append(
                m.ClosedTrade(len(trades) + 1, exit_at - timedelta(minutes=1), exit_at, pnl)
            )
    timestamps = tuple(START + timedelta(minutes=index) for index in range(301))
    marks = []
    realized = F()
    cursor = 0
    for index, timestamp in enumerate(timestamps):
        while cursor < len(trades) and trades[cursor].exit_timestamp_utc <= timestamp:
            realized += trades[cursor].net_realized_pnl_usd
            cursor += 1
        unrealized = (marked_overrides or {}).get(index, realized) - realized
        if index == 300:
            unrealized = final_unrealized
        marks.append(m.MarkedEquityPoint(index, timestamp, realized, unrealized))
    return tuple(trades), tuple(marks), timestamps


def screen(
    protocol, values=None, *, marked_overrides=None, final_unrealized=F(), open_count=0, **kwargs
):
    trades, marks, timestamps = evidence(
        values, marked_overrides=marked_overrides, final_unrealized=final_unrealized
    )
    arguments = {
        "run_identity": identity(),
        "dataset_role": "EXPOSED_DEVELOPMENT",
        "closed_trades": trades,
        "marked_equity": marks,
        "closed_bar_timestamps": timestamps,
        "open_trades_at_end": open_count,
    }
    arguments.update(kwargs)
    return m.evaluate_screening(protocol, **arguments)


def test_canonical_documents_bound_to_exact_user_strategy_hash(protocol):
    assert (
        m.STRATEGY_MANIFEST_SHA256
        == "965b44c837477bac8a81bbcde5df354997fcd84a0afd4f66f76a30e0a654240a"
    )
    assert hashlib.sha256(protocol.protocol_bytes).hexdigest() == m.DEVELOPMENT_PROTOCOL_SHA256
    assert m.canonical_bytes(protocol.document) == protocol.protocol_bytes
    assert (
        m.DEVELOPMENT_PROTOCOL_SHA256
        in (ROOT / "docs/evidence/EMA_PULLBACK_V2_DEVELOPMENT_PROTOCOL.md").read_text()
    )
    parsed = protocol.document
    parsed["screening_thresholds"]["minimum_closed_trades"] = 0
    assert protocol.document["screening_thresholds"]["minimum_closed_trades"] == 100
    with pytest.raises(FrozenInstanceError):
        protocol.protocol_bytes = b"altered"


def test_precommitment_contains_no_selected_or_exposed_dataset(protocol):
    document = protocol.document
    rule = document["dataset_selection_rule"]
    assert rule["expected_first_candidate"] == "MNQ 09-26"
    assert rule["canonical_development_dataset_id"] is None
    assert rule["canonical_development_raw_sha256"] is None
    assert document["current_phase"]["development_replay_status"] == "NOT_EXECUTED"
    assert document["current_phase"]["dataset_lineage_status"] == "NOT_EVALUATED"
    assert document["future_independent_validation"]["access"] == "SEALED"
    assert document["future_independent_validation"]["selected_contract_now"] is None
    assert document["after_merge"]["NEXT"] == "EMA_PULLBACK_V2_DEVELOPMENT_DATASET_LINEAGE_REQUIRED"


@pytest.mark.parametrize(
    "change", ["claimed_strategy", "claimed_protocol", "strategy_bytes", "protocol_bytes"]
)
def test_any_wrong_hash_or_modified_document_fails_closed(protocol, change):
    arguments = {
        "protocol_bytes": protocol.protocol_bytes,
        "strategy_manifest_bytes": protocol.strategy_manifest_bytes,
        "claimed_protocol_sha256": m.DEVELOPMENT_PROTOCOL_SHA256,
        "claimed_strategy_manifest_sha256": m.STRATEGY_MANIFEST_SHA256,
    }
    if change == "claimed_strategy":
        arguments["claimed_strategy_manifest_sha256"] = "c" * 64
    elif change == "claimed_protocol":
        arguments["claimed_protocol_sha256"] = "c" * 64
    else:
        key = "strategy_manifest_bytes" if change == "strategy_bytes" else "protocol_bytes"
        arguments[key] += b" "
    with pytest.raises(m.ProtocolError, match="mismatch"):
        m.verify_protocol(**arguments)


@pytest.mark.parametrize(
    "role",
    [
        "OOS",
        "OOS_TEST",
        "VALIDATION",
        "HOLDOUT",
        "PRODUCTION_PROOF",
        "EXPOSED_DEVELOPMENT_REPLICATION",
    ],
)
def test_wrong_dataset_role_is_rejected(protocol, role):
    with pytest.raises(m.ProtocolError, match="EXPOSED_DEVELOPMENT"):
        screen(protocol, dataset_role=role)


@pytest.mark.parametrize(
    "field",
    [
        "strategy_manifest_sha256",
        "development_protocol_sha256",
        "dataset_raw_sha256",
        "runner_source_sha256",
    ],
)
def test_run_identity_binding_and_sha_validation(field):
    changed = (
        "c" * 64
        if field in ("strategy_manifest_sha256", "development_protocol_sha256")
        else "not-a-digest"
    )
    with pytest.raises(m.ProtocolError):
        replace(identity(), **{field: changed})


@pytest.mark.parametrize("change", ["none", "dataset", "runner", "output", "invalid_output"])
def test_rerun_only_verifies_determinism_and_never_selects_another_result(change):
    original = identity()
    repeated = identity()
    output = repeated_output = "c" * 64
    if change == "dataset":
        repeated = replace(repeated, dataset_raw_sha256="d" * 64)
    elif change == "runner":
        repeated = replace(repeated, runner_source_sha256="d" * 64)
    elif change == "output":
        repeated_output = "d" * 64
    elif change == "invalid_output":
        repeated_output = "invalid"
    arguments = {
        "original_output_sha256": output,
        "repeated_output_sha256": repeated_output,
    }
    if change == "none":
        assert m.verify_determinism_rerun(original, repeated, **arguments) is None
    else:
        with pytest.raises(m.ProtocolError):
            m.verify_determinism_rerun(original, repeated, **arguments)
    assert original == identity()


def test_net_pnl_and_total_sample_exact_minimum_are_inclusive(protocol):
    result = screen(protocol)
    assert result.metrics.closed_trades == 100
    assert result.metrics.net_realized_pnl_usd == 200
    assert result.verdict is m.Verdict.GO_TO_INDEPENDENT_VALIDATION
    assert sum(segment.profitable for segment in result.segments) == 2
    assert result.segments[2].metrics.net_realized_pnl_usd == 0
    assert result.segments[2].profitable is False


@pytest.mark.parametrize(
    "delta,expected",
    [(F(), m.Verdict.GO_TO_INDEPENDENT_VALIDATION), (-EPSILON, m.Verdict.NO_GO_BASELINE)],
)
def test_profit_factor_exact_boundary_without_rounding(protocol, delta, expected):
    values = [[F(1840, 3), F(-1600, 3)] + [F()] * count for count in (32, 31, 31)]
    values[0][0] += delta
    result = screen(protocol, values)
    assert result.verdict is expected
    if not delta:
        assert result.metrics.profit_factor == F(115, 100)
    else:
        assert result.failed_criteria == ("minimum_profit_factor",)


@pytest.mark.parametrize(
    "extra,expected",
    [(F(), m.Verdict.GO_TO_INDEPENDENT_VALIDATION), (EPSILON, m.Verdict.NO_GO_BASELINE)],
)
def test_marked_drawdown_exact_maximum_boundary(protocol, extra, expected):
    result = screen(protocol, marked_overrides={299: F(950) + extra})
    assert result.maximum_marked_equity_drawdown_usd == F(750) + extra
    assert result.verdict is expected
    if extra:
        assert result.failed_criteria == ("maximum_marked_equity_drawdown_usd",)


@pytest.mark.parametrize(
    "loss_count,expected",
    [(8, m.Verdict.GO_TO_INDEPENDENT_VALIDATION), (9, m.Verdict.NO_GO_BASELINE)],
)
def test_consecutive_losses_maximum_boundary(protocol, loss_count, expected):
    values = groups()
    values[0] = [F(200)] + [F(-10)] * loss_count + [F()] * (33 - loss_count)
    result = screen(protocol, values)
    assert result.metrics.maximum_consecutive_losses == loss_count
    assert result.verdict is expected
    if loss_count > 8:
        assert result.failed_criteria == ("maximum_consecutive_losses",)


def test_one_net_criterion_below_boundary_is_no_go(protocol):
    values = groups()
    values[0][0] -= EPSILON
    result = screen(protocol, values)
    assert result.verdict is m.Verdict.NO_GO_BASELINE
    assert result.failed_criteria == ("minimum_net_pnl_usd",)
    assert result.next_gate == "EMA_PULLBACK_V2_NEW_HYPOTHESIS_PROTOCOL_REQUIRED"


def test_segment_exact_pf_and_pnl_boundaries_are_inclusive(protocol):
    values = [
        [F(90), F(-40)] * 10 + [F()] * 14,
        [F(90), F(-40)] * 10 + [F()] * 13,
        [F(80), F(-100)] * 10 + [F()] * 13,
    ]
    result = screen(protocol, values)
    assert result.segments[2].metrics.profit_factor == F(4, 5)
    assert result.segments[2].metrics.net_realized_pnl_usd == -200
    assert result.verdict is m.Verdict.GO_TO_INDEPENDENT_VALIDATION
    values[2][0] -= EPSILON
    assert screen(protocol, values).verdict is m.Verdict.NO_GO_BASELINE


def test_segment_pf_below_boundary_is_no_go(protocol):
    values = groups()
    values[1][0] = F(300)
    values[2][0] = F(79)
    result = screen(protocol, values)
    assert result.failed_criteria == ("DEVELOPMENT_S3.minimum_profit_factor",)
    assert result.verdict is m.Verdict.NO_GO_BASELINE


def test_segment_net_pnl_below_boundary_with_pf_above_minimum(protocol):
    values = [
        [F(90), F(-40)] * 10 + [F()] * 14,
        [F(90), F(-40)] * 10 + [F()] * 13,
        [F(400), F(-501), F(400), F(-500)] + [F()] * 29,
    ]
    result = screen(protocol, values)
    assert result.segments[2].metrics.profit_factor < F(4, 5)
    # Lift both gains/losses equally: PF stays above .80 with the same failing net.
    values[2][0] += F(100)
    values[2][1] -= F(100)
    result = screen(protocol, values)
    assert result.segments[2].metrics.profit_factor > F(4, 5)
    assert result.segments[2].metrics.net_realized_pnl_usd == -201
    assert result.failed_criteria == ("DEVELOPMENT_S3.minimum_net_pnl_usd",)
    assert result.verdict is m.Verdict.NO_GO_BASELINE


def test_one_of_three_profitable_segments_is_no_go(protocol):
    values = groups()
    values[0][0] = F(300)
    values[1][0] = F(100)
    result = screen(protocol, values)
    assert sum(segment.profitable for segment in result.segments) == 1
    assert result.failed_criteria == ("minimum_profitable_segments",)
    assert result.verdict is m.Verdict.NO_GO_BASELINE


def test_insufficient_total_sample_has_priority_over_bad_performance(protocol):
    values = groups()
    values[0] = [F(-1)] * 33
    result = screen(protocol, values)
    assert result.metrics.closed_trades == 99
    assert result.verdict is m.Verdict.INSUFFICIENT_SAMPLE
    assert result.failed_criteria == ("minimum_closed_trades",)
    assert result.next_gate == "EMA_PULLBACK_V2_DEVELOPMENT_SAMPLE_EXTENSION_REQUIRED"


@pytest.mark.parametrize(
    "last_count,expected",
    [(15, m.Verdict.GO_TO_INDEPENDENT_VALIDATION), (14, m.Verdict.INSUFFICIENT_SAMPLE)],
)
def test_segment_sample_threshold_with_sufficient_total(protocol, last_count, expected):
    values = groups()
    values[1] = values[1][:2] + [F()] * (64 - last_count)
    values[2] = values[2][:2] + [F()] * (last_count - 2)
    result = screen(protocol, values)
    assert result.metrics.closed_trades == 100
    assert result.segments[2].metrics.closed_trades == last_count
    assert result.verdict is expected


@pytest.mark.parametrize(
    "values,expected",
    [
        ([F(1), F(2)], m.InfiniteProfitFactor.POSITIVE_INFINITY),
        ([F(), F()], F()),
        ([], F()),
        ([F(-3)], F()),
        ([F(23), F(-20)], F(23, 20)),
    ],
)
def test_profit_factor_infinity_zero_and_exact_finite(values, expected):
    assert m.profit_factor(values) == expected
    if expected is m.InfiniteProfitFactor.POSITIVE_INFINITY:
        assert b'"POSITIVE_INFINITY"' in m.canonical_bytes({"pf": expected})


def test_infinite_pf_is_eligible_with_sufficient_sample(protocol):
    result = screen(protocol, [[F(2)] * count for count in (34, 33, 33)])
    assert result.metrics.profit_factor is m.InfiniteProfitFactor.POSITIVE_INFINITY
    assert result.verdict is m.Verdict.GO_TO_INDEPENDENT_VALIDATION


def test_empty_sample_remains_insufficient_with_null_average_median_and_win_rate(protocol):
    result = screen(protocol, [[], [], []])
    assert result.verdict is m.Verdict.INSUFFICIENT_SAMPLE
    assert result.metrics.closed_trades == 0
    assert result.metrics.profit_factor == 0
    assert result.metrics.average_trade_usd is None
    assert result.metrics.median_trade_usd is None
    assert result.metrics.win_rate is None


def test_zero_trade_resets_loss_streak():
    assert m.maximum_consecutive_losses([F(-1)] * 8 + [F()] + [F(-1)] * 7) == 8


def test_drawdown_uses_unrealized_mark_at_every_close_without_rounding():
    marks = [
        m.MarkedEquityPoint(0, START, F(), F()),
        m.MarkedEquityPoint(1, START + timedelta(minutes=1), F(100), F(900)),
        m.MarkedEquityPoint(2, START + timedelta(minutes=2), F(100), F(-650) - EPSILON),
    ]
    assert m.maximum_marked_drawdown(marks) == F(1550) + EPSILON
    assert m.maximum_marked_drawdown([m.MarkedEquityPoint(0, START, F(), F(-50))]) == 50


def test_open_end_trade_is_never_force_closed_or_added_to_sample(protocol):
    closed = screen(protocol)
    result = screen(protocol, open_count=1, final_unrealized=F(-12345, 7))
    assert result.metrics == closed.metrics
    assert result.metrics.closed_trades == 100
    assert result.open_trades_at_end == 1
    assert result.unrealized_pnl_at_end_usd == F(-12345, 7)
    assert result.maximum_marked_equity_drawdown_usd > 750
    assert result.verdict is m.Verdict.NO_GO_BASELINE


@pytest.mark.parametrize(
    "damage",
    [
        "missing_mark",
        "duplicate_mark",
        "duplicate_timestamp",
        "wrong_bar",
        "wrong_realized",
        "final_unrealized_flat",
    ],
)
def test_incomplete_or_contradictory_equity_evidence_fails_closed(protocol, damage):
    trades, marks, timestamps = evidence()
    if damage == "missing_mark":
        marks = marks[:-1]
    elif damage == "duplicate_mark":
        marks = (marks[0],) + marks
    elif damage == "duplicate_timestamp":
        timestamps = (timestamps[0],) + timestamps[:-1]
    elif damage == "wrong_bar":
        marks = (replace(marks[0], bar_index=1),) + marks[1:]
    elif damage == "wrong_realized":
        marks = (replace(marks[0], realized_equity_usd=F(1)),) + marks[1:]
    else:
        marks = marks[:-1] + (replace(marks[-1], unrealized_pnl_usd=F(1)),)
    with pytest.raises(m.ProtocolError):
        screen(
            protocol, closed_trades=trades, marked_equity=marks, closed_bar_timestamps=timestamps
        )


@pytest.mark.parametrize("invalid", [1.0, float("nan"), float("inf"), "1.00"])
def test_no_float_or_nonfinite_accounting_inputs(invalid):
    with pytest.raises(m.ProtocolError, match="Fraction"):
        m.ClosedTrade(1, START, START, invalid)
    with pytest.raises(m.ProtocolError, match="Fraction"):
        m.profit_factor([invalid])


def test_exact_microsecond_thirds_and_exit_attribution(protocol):
    timestamps = tuple(START + timedelta(microseconds=i) for i in range(11))
    trades = tuple(
        m.ClosedTrade(index, timestamps[offset], timestamps[offset], F(1))
        for index, offset in enumerate((3, 4, 6, 7, 10), 1)
    )
    marks = tuple(
        m.MarkedEquityPoint(
            index, timestamp, F(sum(t.exit_timestamp_utc <= timestamp for t in trades)), F()
        )
        for index, timestamp in enumerate(timestamps)
    )
    result = screen(
        protocol, closed_trades=trades, marked_equity=marks, closed_bar_timestamps=timestamps
    )
    assert [s.metrics.closed_trades for s in result.segments] == [1, 2, 2]
    assert result.segments[0].end_offset_microseconds == F(10, 3)
    assert result.segments[1].end_offset_microseconds == F(20, 3)


def candidate(protocol, name, days, **changes):
    values = dict(
        contract_id=name,
        expiration_utc=START + timedelta(days=days),
        **protocol.document["dataset_selection_rule"]["required_metadata"],
        completed=True,
        used_for_v1_performance=False,
        used_for_v2_performance=False,
        v2_performance_inspected=False,
        clean_lineage_establishable=True,
    )
    values.update(changes)
    return m.ContractCandidate(**values)


def test_selection_sorts_expiration_without_actual_dataset_or_results(protocol):
    records = [candidate(protocol, "SYNTHETIC_OLDER", 1), candidate(protocol, "SYNTHETIC_NEWER", 2)]
    first = m.select_development_candidate(protocol, records)
    assert first == m.select_development_candidate(protocol, reversed(records))
    assert first.candidate_contract_id == "SYNTHETIC_NEWER"
    assert first.status == "CANDIDATE_PENDING_LINEAGE"


def test_contaminated_newest_is_rejected_and_same_rule_continues(protocol):
    result = m.select_development_candidate(
        protocol,
        [
            candidate(protocol, "SYNTHETIC_NEWEST", 2, v2_performance_inspected=True),
            candidate(protocol, "SYNTHETIC_OLDER", 1),
        ],
    )
    assert result.candidate_contract_id == "SYNTHETIC_OLDER"
    assert result.rejected_candidates == (("SYNTHETIC_NEWEST", "REJECT_DATASET_CONTAMINATED"),)


@pytest.mark.parametrize(
    "changes",
    [
        {"contract_id": "MNQ 06-26"},
        {"contract_id": "MNQ 03-26"},
        {"completed": False},
        {"instrument": "NQ"},
        {"merge_policy": "MergeBackAdjusted"},
        {"used_for_v1_performance": True},
        {"used_for_v2_performance": True},
        {"clean_lineage_establishable": None},
        {"v2_performance_inspected": None},
    ],
)
def test_ineligible_or_unknown_candidate_never_becomes_canonical(protocol, changes):
    result = m.select_development_candidate(
        protocol, [candidate(protocol, "SYNTHETIC", 1, **changes)]
    )
    assert result.candidate_contract_id is None
    assert result.status == "NO_ELIGIBLE_DEVELOPMENT_CANDIDATE"


def test_equal_expiration_has_no_arbitrary_priority(protocol):
    with pytest.raises(m.ProtocolError, match="ambiguous"):
        m.select_development_candidate(
            protocol, [candidate(protocol, "SYNTHETIC_A", 1), candidate(protocol, "SYNTHETIC_B", 1)]
        )


def test_fresh_screenings_identical_and_terminal_records_immutable(protocol, monkeypatch):
    # All inputs already in memory. The screening cannot open a file or load market prices.
    def forbidden(*args, **kwargs):
        raise AssertionError("screening attempted file I/O")

    monkeypatch.setattr("builtins.open", forbidden)
    first, second = screen(protocol), screen(protocol)
    assert first == second
    assert m.canonical_bytes(first) == m.canonical_bytes(second)
    assert first.run_identity.sha256 == second.run_identity.sha256
    with pytest.raises(FrozenInstanceError):
        first.verdict = m.Verdict.NO_GO_BASELINE


def test_schema_cost_diagnostics_and_open_trade_realized_pnl(protocol):
    schema = protocol.document["result_schema"]
    properties = schema["properties"]["metrics"]["properties"]
    assert all(
        name in properties
        for name in (
            "net_realized_pnl_usd",
            "gross_price_pnl_usd",
            "total_fees_usd",
            "closed_trade_fees_usd",
            "open_entry_fees_usd",
            "diagnostic_total_slippage_cost_usd",
            "suppressed_pending_opportunities",
        )
    )
    assert schema["properties"]["open_trade_records"]["items"]["properties"][
        "net_realized_pnl_usd"
    ] == {"type": "null"}
    assert "diagnostic_trades_per_trading_day_session" in schema["required"]
    assert protocol.document["metric_contract"]["trades_per_trading_day_session"].startswith(
        "DIAGNOSTIC_ONLY"
    )
    assert protocol.document["future_replay_contract"]["execution_count"] == "ONCE"
    assert (
        json.loads(m.canonical_bytes(screen(protocol)))["verdict"] == "GO_TO_INDEPENDENT_VALIDATION"
    )
