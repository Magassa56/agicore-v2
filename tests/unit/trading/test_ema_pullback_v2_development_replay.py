"""Invented OHLCV/accounting only; canonical DEVELOPMENT bytes stay unopened."""

from __future__ import annotations

import ast
import hashlib
import json
import sys
from dataclasses import FrozenInstanceError, asdict, replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal as D
from fractions import Fraction as F
from pathlib import Path

import pytest

from agicore.trading import ema_pullback_v2_development_replay as replay
from agicore.trading.regime_context_v2 import RegimeDirection
from tests.unit.trading.test_ema_pullback_regime_gated_baseline_v2 import SCENARIOS, _scenario

START = datetime(2099, 1, 1, tzinfo=UTC)
SIMPLE = (
    b"20990101 000000;20000;20000.25;19999.75;20000;100\n"
    b"20990101 000100;20000;20000.25;19999.75;20000;0\n"
)


@pytest.fixture(scope="module")
def bindings():
    return replay.read_frozen_replay_bindings_v2()


def _raw(bars):
    """Serialize already invented test bars; retain insertion order and real gaps."""
    return (
        "\n".join(
            ";".join(
                (
                    bar.timestamp_utc.strftime("%Y%m%d %H%M%S"),
                    *(str(getattr(bar, name)) for name in ("open", "high", "low", "close")),
                    str(bar.volume),
                )
            )
            for bar in bars.values()
        )
        + "\n"
    ).encode("ascii")


def _exact(value):
    return F(value["numerator"], value["denominator"])


def _evaluate(name, bindings, direction=RegimeDirection.LONG):
    return replay.evaluate_synthetic_development_replay_v2(
        _raw(_scenario(name, direction)), bindings=bindings
    )


def _registration(bindings):
    identity = replay.build_replay_run_identity_v2()
    return replay.canonical_replay_bytes_v2(
        {
            "status": "PASS",
            "dataset_lineage_manifest_sha256": replay.DATASET_LINEAGE_MANIFEST_SHA256,
            "run_identity": asdict(identity),
            "runner_source_sha256": identity.runner_source_sha256,
            "original_development_run_id_sha256": identity.sha256,
        }
    )


def _rehash(document):
    document["output_sha256"] = hashlib.sha256(
        replay.canonical_replay_bytes_v2(
            {key: value for key, value in document.items() if key != "output_sha256"}
        )
    ).hexdigest()


def test_exact_native_parser_and_decimal_fraction_values():
    bars = replay.parse_ninjatrader_last_rows_v2(SIMPLE.replace(b"\n", b"\r\n"))
    assert [bar.bar_index for bar in bars] == [0, 1]
    assert bars[0].timestamp_utc == START
    assert bars[1].timestamp_utc == START + timedelta(minutes=1)
    assert type(bars[0].open) is D and F(bars[0].high) == F(80001, 4)
    assert bars[0].volume == 100 and bars[1].volume == 0
    assert bars[0].closed_view().data_type == "Last"
    assert bars[0].closed_view().volume_measure == "BAR_TRADE_VOLUME"
    assert replay.parse_ninjatrader_last_rows_v2(SIMPLE.rstrip(b"\n")) == bars


@pytest.mark.parametrize(
    "raw",
    [
        b"",
        SIMPLE + b"\n",
        SIMPLE.replace(b";100", b";-1"),
        SIMPLE.replace(b";100", b";1.0"),
        SIMPLE.replace(b";100", b";NaN"),
        SIMPLE.replace(b";20000;", b";NaN;", 1),
        SIMPLE.replace(b";20000;", b";Infinity;", 1),
        SIMPLE.replace(b";20000;", b";20000.01;", 1),
        SIMPLE.replace(b";20000.25;", b";19999.75;", 1),
        SIMPLE.replace(b"20990101", b"20990230", 1),
        SIMPLE.replace(b"000000", b"000030", 1),
        SIMPLE.replace(b";100", b";100;extra"),
        SIMPLE.replace(b"\n", b"\v"),
        SIMPLE.replace(b"\n", b"\r"),
        b"\xef\xbb\xbf" + SIMPLE,
    ],
)
def test_malformed_input_fails_without_repairs(raw):
    with pytest.raises(replay.DevelopmentReplayV2Error):
        replay.parse_ninjatrader_last_rows_v2(raw)


@pytest.mark.parametrize(
    "raw",
    [
        SIMPLE.replace(b"000100", b"000000"),
        b"\n".join(reversed(SIMPLE.rstrip(b"\n").split(b"\n"))) + b"\n",
    ],
)
def test_duplicate_and_nonchronological_rows_rejected(raw):
    with pytest.raises(replay.DevelopmentReplayV2Error, match="duplicate/nonchronological"):
        replay.parse_ninjatrader_last_rows_v2(raw)


@pytest.mark.parametrize("value", [1.0, {"nested": [0.0]}, float("nan")])
def test_float_rejected_before_calculation_or_serialization(value):
    with pytest.raises(replay.DevelopmentReplayV2Error, match="floats forbidden"):
        replay.canonical_replay_bytes_v2(value)
    with pytest.raises(replay.DevelopmentReplayV2Error):
        replay.DevelopmentReplayBarV2(0, START, 20000.0, D(20001), D(19999), D(20000), 1)


def test_source_has_no_float_calculation_or_strategy_formula_copy():
    source = Path(replay.__file__).read_text()
    tree = ast.parse(source)
    calls = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "float" not in calls
    assert not any(
        isinstance(node, ast.Constant) and type(node.value) is float for node in ast.walk(tree)
    )
    assert replay.assembly.MODE == "OFFLINE_DETERMINISTIC"
    assert replay.assembly.REAL_DATA_ACCESS == "FORBIDDEN"
    assert replay.assembly.REPLAY == "FORBIDDEN"
    for name in (
        "begin_regime_gated_baseline_v2",
        "process_baseline_open_v2",
        "process_baseline_close_v2",
        "finish_regime_gated_baseline_v2",
    ):
        assert "assembly." + name in source


def test_canonical_big_integer_rationals_without_global_digit_limit_mutation():
    before = sys.get_int_max_str_digits()
    number = 10**6000 + 51
    raw = replay.canonical_replay_bytes_v2({"exact": F(number, 3), "utf8": "é"})
    assert raw.endswith(b"\n") and b"\xc3\xa9" in raw
    assert _exact(replay.DevelopmentReplayResultV2(raw).document["exact"]) == F(number, 3)
    assert sys.get_int_max_str_digits() == before
    small = {"z": F(51, 100), "a": 3}
    assert replay.canonical_replay_bytes_v2(small) == replay.screening.canonical_bytes(small)


@pytest.mark.parametrize(
    "field", ["strategy_bytes", "protocol_bytes", "lineage_bytes", "session_calendar_bytes"]
)
def test_every_bound_document_is_immutable_and_hash_guarded(bindings, field):
    with pytest.raises(replay.DevelopmentReplayV2Error, match="changed|mismatch"):
        replace(bindings, **{field: getattr(bindings, field) + b" "})
    with pytest.raises(FrozenInstanceError):
        bindings.lineage_bytes = b"changed"
    lineage = bindings.lineage
    lineage["canonical_dataset_id"] = "wrong"
    assert bindings.lineage["canonical_dataset_id"] == replay.CANONICAL_DATASET_ID


@pytest.mark.parametrize(
    "changes",
    [
        {"sha256": "a" * 64},
        {"size_bytes": 1},
        {"rows": 3},
        {"first_timestamp": START + timedelta(minutes=1)},
        {"last_timestamp": START + timedelta(minutes=2)},
    ],
)
def test_sha_size_row_bound_mismatch_fails_on_invented_bytes(changes):
    identity = replay.RawIdentityV2(
        hashlib.sha256(SIMPLE).hexdigest(),
        len(SIMPLE),
        2,
        START,
        START + timedelta(minutes=1),
        "invented",
        "EXPOSED_DEVELOPMENT",
    )
    assert len(replay._verify_raw_bytes(SIMPLE, identity)) == 2
    with pytest.raises(replay.DevelopmentReplayV2Error, match="mismatch"):
        replay._verify_raw_bytes(SIMPLE, replace(identity, **changes))


def test_real_loader_and_executor_denied_before_any_path_access(bindings, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("a file was read before future authorization")

    monkeypatch.setattr(Path, "read_bytes", forbidden)
    with pytest.raises(replay.DevelopmentReplayV2Error, match="future execution gate"):
        replay.load_canonical_development_raw_v2(
            "DO_NOT_OPEN.Last.txt", bindings=bindings, registered_implementation_bytes=b""
        )
    with pytest.raises(replay.DevelopmentReplayV2Error, match="future execution gate"):
        replay.execute_registered_development_replay_v2(
            "DO_NOT_OPEN.Last.txt",
            bindings=bindings,
            registration_path="DO_NOT_OPEN.json",
            output_path="DO_NOT_CREATE.json",
        )


@pytest.mark.parametrize(
    "field",
    [
        "status",
        "dataset_lineage_manifest_sha256",
        "runner_source_sha256",
        "original_development_run_id_sha256",
        "run_identity",
    ],
)
def test_wrong_registration_fails_before_loader_access(bindings, field):
    document = json.loads(_registration(bindings))
    document[field] = "wrong"
    with pytest.raises(replay.DevelopmentReplayV2Error):
        replay._verify_registration(replay.canonical_replay_bytes_v2(document), bindings)


@pytest.mark.parametrize("role", ["OOS", "VALIDATION", "HOLDOUT", "PRODUCTION_PROOF"])
def test_wrong_role_and_id_are_rejected_before_raw_path_access(bindings, role):
    with pytest.raises(replay.DevelopmentReplayV2Error, match="ID/role"):
        replay.load_canonical_development_raw_v2(
            "DO_NOT_OPEN.Last.txt",
            bindings=bindings,
            execution_gate=replay.EXECUTION_GATE,
            registered_implementation_bytes=_registration(bindings),
            dataset_role=role,
        )
    with pytest.raises(replay.DevelopmentReplayV2Error, match="ID/role"):
        replay.load_canonical_development_raw_v2(
            "DO_NOT_OPEN.Last.txt",
            bindings=bindings,
            execution_gate=replay.EXECUTION_GATE,
            registered_implementation_bytes=_registration(bindings),
            dataset_id="another",
        )


def test_future_loader_refuses_synthetic_bytes_before_strategy(tmp_path, bindings, monkeypatch):
    raw = tmp_path / "invented.Last.txt"
    raw.write_bytes(SIMPLE)

    def forbidden(**kwargs):
        raise AssertionError("strategy executed before canonical RAW integrity passed")

    monkeypatch.setattr(replay.assembly, "begin_regime_gated_baseline_v2", forbidden)
    with pytest.raises(replay.DevelopmentReplayV2Error, match="SHA-256 mismatch"):
        replay.load_canonical_development_raw_v2(
            raw,
            bindings=bindings,
            execution_gate=replay.EXECUTION_GATE,
            registered_implementation_bytes=_registration(bindings),
        )


def test_canonical_registration_claim_is_single_use_even_after_failure(
    tmp_path, bindings, monkeypatch
):
    monkeypatch.setattr(replay, "REPOSITORY", tmp_path)
    registration = tmp_path / "docs/evidence/EMA_PULLBACK_V2_DEVELOPMENT_REPLAY_IMPLEMENTATION.json"
    registration.parent.mkdir(parents=True)
    registration.write_bytes(_registration(bindings))
    raw = tmp_path / "invented.Last.txt"
    raw.write_bytes(SIMPLE)
    output = tmp_path / "never-created.json"
    with pytest.raises(replay.DevelopmentReplayV2Error, match="SHA-256 mismatch"):
        replay.execute_registered_development_replay_v2(
            raw,
            bindings=bindings,
            registration_path=registration,
            output_path=output,
            execution_gate=replay.EXECUTION_GATE,
        )
    with pytest.raises(replay.DevelopmentReplayV2Error, match="already claimed"):
        replay.execute_registered_development_replay_v2(
            raw,
            bindings=bindings,
            registration_path=registration,
            output_path=output,
            execution_gate=replay.EXECUTION_GATE,
        )
    with pytest.raises(replay.DevelopmentReplayV2Error, match="canonical original"):
        replay.execute_registered_development_replay_v2(
            raw,
            bindings=bindings,
            registration_path=tmp_path / "copied-registration.json",
            output_path=output,
            execution_gate=replay.EXECUTION_GATE,
        )
    assert not output.exists() and raw.read_bytes() == SIMPLE
    claim = registration.with_suffix(".json.original-execution-claim")
    assert claim.read_bytes() == replay.canonical_replay_bytes_v2(
        replay.build_replay_run_identity_v2()
    )


@pytest.mark.parametrize("direction", [RegimeDirection.LONG, RegimeDirection.SHORT])
@pytest.mark.parametrize("name", SCENARIOS)
def test_every_synthetic_full_lifecycle_twice_from_fresh_state(bindings, name, direction):
    first, second = _evaluate(name, bindings, direction), _evaluate(name, bindings, direction)
    assert first.canonical_utf8 == second.canonical_utf8
    assert first.output_sha256 == second.output_sha256
    document = first.document
    bars = _scenario(name, direction)
    assert len(document["marked_equity_samples"]) == len(bars)
    assert document["metrics"]["entry_fills"] == (
        len(document["closed_trade_records"]) + len(document["open_trade_records"])
    )
    assert not document["oos_accessed"] and not document["parameter_changes"]
    assert document["dataset_id"].startswith("synthetic-")
    assert document["verdict"] == "INSUFFICIENT_SAMPLE"
    assert (
        document["immutable_lifecycle_records"]["terminal_states"][0]["state"] == "SYNTHETIC_ONLY"
    )
    replay.validate_development_result_v2(document, bindings)
    if name.endswith("profit") or name == "first_confirmation":
        trade = document["closed_trade_records"][0]
        assert trade["exit_reason"] == "EMA20_POSITION_EXIT"
        assert _exact(trade["net_realized_pnl_usd"]) > 0
        assert trade["approved_quantity"] == (1 if name == "qty1_profit" else 2)
    if name == "risk_reject":
        assert document["metrics"]["entry_fills"] == 0
        assert document["metrics"]["risk_rejections"] == 1
        assert document["immutable_lifecycle_records"]["risk_decisions"][0]["rejection_reason"] == (
            "RISK_PER_CONTRACT_EXCEEDS_BUDGET"
        )
    if name in ("context_age", "context_elapsed", "context_eof"):
        assert document["metrics"]["expired_contexts"] == 1
    if name in ("entry_gap", "entry_missing", "entry_eof"):
        assert document["metrics"]["entry_fills"] == 0
    if name in ("open_eof", "ema_eof", "ema_gap", "position_suppressed"):
        assert document["metrics"]["open_trades_at_end"] == 1
        assert document["open_trade_records"][0]["net_realized_pnl_usd"] is None
    if name == "position_suppressed":
        assert document["metrics"]["suppressed_position_open_events"] > 0
    if name == "exit_regime_admitted":
        assert document["metrics"]["admitted_contexts"] == 2


def test_only_open_fields_available_and_open_before_close(bindings, monkeypatch):
    calls = []
    original_open = replay.assembly.process_baseline_open_v2
    original_close = replay.assembly.process_baseline_close_v2

    def open_phase(*, previous, opening_bar):
        assert set(vars(opening_bar)) == {"bar_index", "timestamp_utc", "open"}
        for name in ("high", "low", "close", "volume"):
            with pytest.raises(AttributeError):
                getattr(opening_bar, name)
        calls.append(("OPEN", opening_bar.bar_index))
        return original_open(previous=previous, opening_bar=opening_bar)

    def close_phase(*, previous, closed_bar):
        calls.append(("CLOSE", closed_bar.bar_index))
        return original_close(previous=previous, closed_bar=closed_bar)

    monkeypatch.setattr(replay.assembly, "process_baseline_open_v2", open_phase)
    monkeypatch.setattr(replay.assembly, "process_baseline_close_v2", close_phase)
    _evaluate("impulse_profit", bindings)
    assert calls == [(phase, index) for index in range(57) for phase in ("OPEN", "CLOSE")]


def test_clock_gaps_and_off_session_observation_are_not_filtered(bindings, monkeypatch):
    bars = _scenario("impulse_profit", RegimeDirection.LONG)
    first = datetime(2026, 7, 4, 14, 4, tzinfo=UTC)
    bars = {i: replace(bar, timestamp_utc=first + timedelta(minutes=i)) for i, bar in bars.items()}
    document = replay.evaluate_synthetic_development_replay_v2(
        _raw(bars), bindings=bindings
    ).document
    assert document["metrics"]["entry_fills"] == 1
    assert document["closed_trade_records"][0]["entry_timestamp"] == "2026-07-04T14:40:00Z"
    assert len(document["marked_equity_samples"]) == 57
    assert all(
        row["session_id"] == "OFF_SESSION_STORED_OBSERVATION"
        for row in document["diagnostic_trades_per_trading_day_session"]
    )
    gapped = SIMPLE.replace(b"000100", b"020100")
    result = replay.evaluate_synthetic_development_replay_v2(gapped, bindings=bindings).document
    assert len(result["marked_equity_samples"]) == 2
    assert result["marked_equity_samples"][1]["bar_index"] == 1
    assert result["marked_equity_samples"][1]["timestamp_utc"] == "2099-01-01T02:01:00Z"
    # Diagnostic labels alone cannot change screening.
    monkeypatch.setattr(replay, "_session_bucket", lambda *args: ("2099-01-01", "INVENTED_LABEL"))
    relabeled = replay.evaluate_synthetic_development_replay_v2(
        _raw(bars), bindings=bindings
    ).document
    assert document["metrics"] == relabeled["metrics"]
    assert document["verdict"] == relabeled["verdict"]
    assert document["closed_trade_records"] == relabeled["closed_trade_records"]


@pytest.mark.parametrize("direction", [RegimeDirection.LONG, RegimeDirection.SHORT])
@pytest.mark.parametrize(
    "name,phase",
    [
        ("intrabar_stop", "INTRABAR"),
        ("gap_stop", "BAR_OPEN_GAP"),
        ("stop_wins", "BAR_OPEN_GAP"),
        ("breached_1", "ENTRY_OPEN"),
        ("breached_2", "ENTRY_OPEN"),
    ],
)
def test_structural_stop_phase_priority_and_base_fill(bindings, direction, name, phase):
    document = _evaluate(name, bindings, direction).document
    trade = document["closed_trade_records"][0]
    exit_record = trade["immutable_provenance"]["exit"]
    assert trade["exit_reason"] == "STRUCTURAL_STOP"
    assert exit_record["trigger_phase"] == phase
    if phase == "INTRABAR":
        assert trade["exit_base_fill_price"] == exit_record["initial_stop_price"]
    else:
        bar = _scenario(name, direction)[exit_record["trigger_bar_index"]]
        assert _exact(trade["exit_base_fill_price"]) == F(bar.open)
    if phase == "ENTRY_OPEN":
        assert trade["entry_base_fill_price"] == trade["exit_base_fill_price"]
        assert _exact(trade["net_realized_pnl_usd"]) == -F(202, 100) * trade["approved_quantity"]
    if name == "stop_wins":
        ema = [
            record["record"]
            for record in document["immutable_lifecycle_records"]["terminal_states"]
            if record["kind"] == "EMA_EXIT_EXECUTION"
        ]
        assert any(record["state"] == "CANCELLED_STRUCTURAL_STOP" for record in ema)


@pytest.mark.parametrize("direction", [RegimeDirection.LONG, RegimeDirection.SHORT])
@pytest.mark.parametrize("name,quantity", [("impulse_profit", 2), ("qty1_profit", 1)])
def test_native_accounting_next_open_and_exit_timestamp_attribution(
    bindings, direction, name, quantity
):
    document = _evaluate(name, bindings, direction).document
    trade = document["closed_trade_records"][0]
    provenance = trade["immutable_provenance"]
    entry = provenance["entry"]
    exit_record = provenance["exit"]
    assert trade["approved_quantity"] == quantity
    assert entry["execution_bar_index"] == provenance["confirmation"]["confirmation_bar_index"] + 1
    assert (
        exit_record["exit_execution_bar_index"]
        == exit_record["signal"]["exit_signal_bar_index"] + 1
    )
    sign = 1 if direction is RegimeDirection.LONG else -1
    assert _exact(trade["entry_effective_fill_price"]) == _exact(
        trade["entry_base_fill_price"]
    ) + sign * F(1, 4)
    assert _exact(trade["exit_effective_fill_price"]) == _exact(
        trade["exit_base_fill_price"]
    ) - sign * F(1, 4)
    assert _exact(trade["entry_fee_usd"]) == _exact(trade["exit_fee_usd"]) == quantity * F(51, 100)
    assert _exact(trade["total_fees_usd"]) == quantity * F(102, 100)
    assert _exact(trade["diagnostic_slippage_cost_usd"]) == quantity
    gross = (
        sign
        * (_exact(trade["exit_effective_fill_price"]) - _exact(trade["entry_effective_fill_price"]))
        * 2
        * quantity
    )
    assert _exact(trade["gross_price_pnl_usd"]) == gross
    assert _exact(trade["net_realized_pnl_usd"]) == gross - quantity * F(102, 100)
    assert document["segments"][0]["closed_trades"] == document["segments"][1]["closed_trades"] == 0
    assert document["segments"][2]["net_realized_pnl_usd"] == trade["net_realized_pnl_usd"]
    assert document["segments"][2]["total_fees_usd"] == trade["total_fees_usd"]


def test_open_end_mark_charges_only_actual_entry_costs(bindings):
    document = _evaluate("open_eof", bindings).document
    trade = document["open_trade_records"][0]
    close = _scenario("open_eof", RegimeDirection.LONG)[36].close
    expected = (F(close) - _exact(trade["entry_effective_fill_price"])) * 2 * trade[
        "approved_quantity"
    ] - _exact(trade["entry_fee_usd"])
    assert _exact(document["marked_equity_samples"][-1]["unrealized_pnl_usd"]) == expected
    assert _exact(document["metrics"]["unrealized_pnl_at_end_usd"]) == expected
    assert trade["state"] == "OPEN_UNREALIZED" and trade["net_realized_pnl_usd"] is None
    assert document["metrics"]["closed_trades"] == 0
    assert not document["immutable_lifecycle_records"]["exits"]
    assert _exact(document["metrics"]["total_fees_usd"]) == F(102, 100)
    assert _exact(document["metrics"]["diagnostic_total_slippage_cost_usd"]) == 1


def test_marked_drawdown_includes_unrealized_and_zero_start(bindings):
    document = _evaluate("impulse_profit", bindings).document
    peak, maximum = F(), F()
    for sample in document["marked_equity_samples"]:
        mark = _exact(sample["marked_equity_usd"])
        peak = max(peak, mark)
        maximum = max(maximum, peak - mark)
    assert maximum == _exact(document["metrics"]["maximum_marked_equity_drawdown_usd"])
    assert maximum > 0 and document["metrics"]["maximum_consecutive_losses"] == 0
    assert document["metrics"]["profit_factor"] == "POSITIVE_INFINITY"
    empty = replay.evaluate_synthetic_development_replay_v2(SIMPLE, bindings=bindings).document
    assert _exact(empty["metrics"]["profit_factor"]) == 0


@pytest.mark.parametrize(
    "name", ["impulse_profit", "reversal_profit", "intrabar_stop", "open_eof", "stop_wins"]
)
def test_long_short_exact_accounting_symmetry(bindings, name):
    long = _evaluate(name, bindings, RegimeDirection.LONG).document
    short = _evaluate(name, bindings, RegimeDirection.SHORT).document
    for key in (
        "net_realized_pnl_usd",
        "total_fees_usd",
        "gross_price_pnl_usd",
        "maximum_marked_equity_drawdown_usd",
        "unrealized_pnl_at_end_usd",
        "diagnostic_total_slippage_cost_usd",
        "entry_fills",
        "closed_trades",
    ):
        assert long["metrics"][key] == short["metrics"][key]


def test_future_mutation_cannot_change_prior_native_decisions(bindings):
    bars = _scenario("impulse_profit", RegimeDirection.LONG)
    changed = dict(bars)
    changed[56] = replace(bars[56], open=D(20100), high=D(20101), low=D(19999), close=D(20020))
    original = replay.evaluate_synthetic_development_replay_v2(
        _raw(bars), bindings=bindings
    ).document
    mutated = replay.evaluate_synthetic_development_replay_v2(
        _raw(changed), bindings=bindings
    ).document
    assert original["marked_equity_samples"][:56] == mutated["marked_equity_samples"][:56]
    for name in (
        "events",
        "contexts",
        "pullbacks",
        "confirmations",
        "stops",
        "risk_decisions",
        "entries",
    ):
        assert (
            original["immutable_lifecycle_records"][name]
            == mutated["immutable_lifecycle_records"][name]
        )
    assert (
        original["closed_trade_records"][0]["exit_base_fill_price"]
        != mutated["closed_trade_records"][0]["exit_base_fill_price"]
    )


def test_gaps_do_not_reset_native_ema_or_macd(bindings):
    bars = _scenario("impulse_profit", RegimeDirection.LONG)
    shifted = {
        i: replace(bar, timestamp_utc=bar.timestamp_utc + timedelta(days=3)) if i else bar
        for i, bar in bars.items()
    }
    original = replay.evaluate_synthetic_development_replay_v2(
        _raw(bars), bindings=bindings
    ).document
    gapped = replay.evaluate_synthetic_development_replay_v2(
        _raw(shifted), bindings=bindings
    ).document
    assert len(gapped["marked_equity_samples"]) == len(bars)
    assert [m["marked_equity_usd"] for m in original["marked_equity_samples"]] == [
        m["marked_equity_usd"] for m in gapped["marked_equity_samples"]
    ]
    before = original["closed_trade_records"][0]["immutable_provenance"]
    after = gapped["closed_trade_records"][0]["immutable_provenance"]
    for field in ("macd", "signal", "histogram", "previous_macd", "previous_histogram"):
        assert before["confirmation"][field] == after["confirmation"][field]
    assert before["exit"]["signal"]["ema20_at_signal"] == after["exit"]["signal"]["ema20_at_signal"]
    assert original["metrics"]["net_realized_pnl_usd"] == gapped["metrics"]["net_realized_pnl_usd"]


def test_duplicate_native_phase_processing_has_identical_output(bindings, monkeypatch):
    expected = _evaluate("impulse_profit", bindings).canonical_utf8
    original_open = replay.assembly.process_baseline_open_v2
    original_close = replay.assembly.process_baseline_close_v2
    original_finish = replay.assembly.finish_regime_gated_baseline_v2

    def duplicate_open(*, previous, opening_bar):
        next_state = original_open(previous=previous, opening_bar=opening_bar)
        assert original_open(previous=next_state, opening_bar=opening_bar) is next_state
        return next_state

    def duplicate_close(*, previous, closed_bar):
        next_state = original_close(previous=previous, closed_bar=closed_bar)
        assert original_close(previous=next_state, closed_bar=closed_bar) is next_state
        return next_state

    def duplicate_finish(*, previous):
        next_state = original_finish(previous=previous)
        assert original_finish(previous=next_state) is next_state
        return next_state

    monkeypatch.setattr(replay.assembly, "process_baseline_open_v2", duplicate_open)
    monkeypatch.setattr(replay.assembly, "process_baseline_close_v2", duplicate_close)
    monkeypatch.setattr(replay.assembly, "finish_regime_gated_baseline_v2", duplicate_finish)
    assert _evaluate("impulse_profit", bindings).canonical_utf8 == expected


def test_pending_opportunity_suppression_preserves_original_provenance(bindings):
    document = _evaluate("impulse_profit", bindings).document
    assert document["metrics"]["suppressed_pending_opportunities"] >= 1
    assert document["metrics"]["entry_fills"] == 1
    assert [
        context["source_event_bar_index"]
        for context in document["immutable_lifecycle_records"]["contexts"]
    ] == [32]
    provenance = document["closed_trade_records"][0]["immutable_provenance"]
    assert provenance["regime"]["consumed_context"]["source_event_bar_index"] == 32
    assert provenance["regime"]["events"][0]["event_bar_index"] == 32


@pytest.mark.parametrize(
    "name,kind,state",
    [
        ("context_age", "CONTEXT", "EXPIRED_MAX_AGE"),
        ("context_elapsed", "CONTEXT", "EXPIRED_ELAPSED_TIME"),
        ("context_eof", "CONTEXT", "EXPIRED_END_OF_DATA"),
        ("confirmation_no", "OPPORTUNITY", "TERMINAL_CONFIRMATION_EXPIRED"),
        ("confirmation_elapsed", "OPPORTUNITY", "TERMINAL_CONFIRMATION_EXPIRED"),
        ("confirmation_eof", "OPPORTUNITY", "TERMINAL_INCOMPLETE_CONFIRMATION"),
        ("entry_gap", "ENTRY_EXECUTION", "EXPIRED_EXECUTION_GAP"),
        ("entry_eof", "ENTRY_EXECUTION", "EXPIRED_NO_EXECUTION"),
        ("ema_gap", "EMA_EXIT_EXECUTION", "EXPIRED_EXIT_GAP"),
        ("ema_eof", "EMA_EXIT_EXECUTION", "EXPIRED_NO_EXIT_EXECUTION"),
    ],
)
def test_terminal_expiration_proofs_are_carried_from_assembly(bindings, name, kind, state):
    terminal = _evaluate(name, bindings).document["immutable_lifecycle_records"]["terminal_states"]
    records = [item["record"] for item in terminal if item["kind"] == kind]
    assert any(item.get("state", item.get("execution_state")) == state for item in records)


@pytest.mark.parametrize(
    "mutation",
    [
        "missing",
        "extra_metric",
        "float",
        "wrong_role",
        "wrong_hash",
        "count",
        "fees",
        "segment_fees",
        "false_real_domain",
        "incomplete_provenance",
        "digest",
    ],
)
def test_result_schema_and_cross_record_reconciliation_fail_closed(bindings, mutation):
    document = _evaluate("impulse_profit", bindings).document
    if mutation == "missing":
        del document["segments"]
    elif mutation == "extra_metric":
        document["metrics"]["new_threshold"] = 1
    elif mutation == "float":
        document["metrics"]["closed_trades"] = 1.0
    elif mutation == "wrong_role":
        document["dataset_role"] = "OOS"
    elif mutation == "wrong_hash":
        document["run_identity"]["development_protocol_sha256"] = "a" * 64
    elif mutation == "count":
        document["metrics"]["entry_fills"] += 1
    elif mutation == "fees":
        document["closed_trade_records"][0]["entry_fee_usd"]["numerator"] += 1
    elif mutation == "segment_fees":
        document["segments"][2]["total_fees_usd"]["numerator"] += 1
    elif mutation == "false_real_domain":
        document["immutable_lifecycle_records"]["terminal_states"][0]["state"] = (
            "AUTHORIZED_EXPOSED_DEVELOPMENT"
        )
    elif mutation == "incomplete_provenance":
        del document["closed_trade_records"][0]["immutable_provenance"]["accounting"]
    elif mutation == "digest":
        document["output_sha256"] = "a" * 64
    if mutation not in ("float", "digest"):
        _rehash(document)
    with pytest.raises((replay.DevelopmentReplayV2Error, replay.screening.ProtocolError)):
        replay.validate_development_result_v2(document, bindings)


def test_result_and_manifest_identity_are_immutable_deterministic(bindings):
    result = _evaluate("impulse_profit", bindings)
    document = result.document
    document["metrics"]["entry_fills"] = 999
    assert result.document["metrics"]["entry_fills"] == 1
    with pytest.raises(FrozenInstanceError):
        result.canonical_utf8 = b"altered"
    identity = replay.build_replay_run_identity_v2()
    payload = replay.canonical_replay_bytes_v2(identity)
    assert set(json.loads(payload)) == {
        "strategy_manifest_sha256",
        "development_protocol_sha256",
        "dataset_raw_sha256",
        "runner_source_sha256",
    }
    assert hashlib.sha256(payload).hexdigest() == identity.sha256
    assert payload == replay.screening.canonical_bytes(identity)


def _screen(bindings, values=None, *, dd_override=None):
    values = values or (
        [F(200), F(-100)] + [F()] * 32,
        [F(200), F(-100)] + [F()] * 31,
        [F(100), F(-100)] + [F()] * 31,
    )
    trades = []
    for segment, pnls in enumerate(values):
        for offset, pnl in enumerate(pnls):
            timestamp = START + timedelta(minutes=segment * 100 + offset + 10)
            trades.append(
                replay.screening.ClosedTrade(
                    len(trades) + 1,
                    timestamp - timedelta(minutes=1),
                    timestamp,
                    pnl,
                )
            )
    timestamps = tuple(START + timedelta(minutes=i) for i in range(301))
    realized, cursor, marks = F(), 0, []
    for index, timestamp in enumerate(timestamps):
        while cursor < len(trades) and trades[cursor].exit_timestamp_utc <= timestamp:
            realized += trades[cursor].net_realized_pnl_usd
            cursor += 1
        unrealized = dd_override - realized if index == 299 and dd_override is not None else F()
        marks.append(replay.screening.MarkedEquityPoint(index, timestamp, realized, unrealized))
    return replay.screening.evaluate_screening(
        bindings.protocol,
        run_identity=replay.build_replay_run_identity_v2("a" * 64),
        dataset_role=replay.DATASET_ROLE,
        closed_trades=tuple(trades),
        marked_equity=tuple(marks),
        closed_bar_timestamps=timestamps,
    )


def test_frozen_screening_order_and_nonnegative_reset_loss_streak(bindings):
    assert _screen(bindings).verdict.value == "GO_TO_INDEPENDENT_VALIDATION"
    assert _screen(bindings, dd_override=F(-1000)).verdict.value == "NO_GO_BASELINE"
    values = ([F(100)] * 14, [F(100)] * 43, [F(100)] * 43)
    assert _screen(bindings, values).verdict.value == "INSUFFICIENT_SAMPLE"
    assert _screen(bindings, ([F(100)] * 20,) * 3).verdict.value == "INSUFFICIENT_SAMPLE"
    trades = tuple(
        replay.screening.ClosedTrade(
            i + 1,
            START + timedelta(minutes=i),
            START + timedelta(minutes=i + 1),
            pnl,
        )
        for i, pnl in enumerate((F(-1), F(-1), F(), F(-1), F(-1), F(-1), F(1), F(-1)))
    )
    assert replay.screening.maximum_consecutive_losses(t.net_realized_pnl_usd for t in trades) == 3
    assert (
        replay.screening.profit_factor((F(1), F()))
        is replay.screening.InfiniteProfitFactor.POSITIVE_INFINITY
    )
    assert replay.screening.profit_factor((F(), F())) == 0


def test_exact_elapsed_time_segmentation_and_exit_boundary_attribution(bindings):
    times = tuple(START + timedelta(minutes=30 * i) for i in range(4))
    trades = tuple(
        replay.screening.ClosedTrade(
            i,
            times[i] - timedelta(minutes=1),
            times[i],
            F(i),
        )
        for i in range(1, 4)
    )
    marks = tuple(
        replay.screening.MarkedEquityPoint(
            i,
            timestamp,
            F(i * (i + 1), 2),
            F(),
        )
        for i, timestamp in enumerate(times)
    )
    result = replay.screening.evaluate_screening(
        bindings.protocol,
        run_identity=replay.build_replay_run_identity_v2("a" * 64),
        dataset_role=replay.DATASET_ROLE,
        closed_trades=trades,
        marked_equity=marks,
        closed_bar_timestamps=times,
    )
    assert [segment.metrics.closed_trades for segment in result.segments] == [0, 1, 2]
    assert result.segments[1].metrics.net_realized_pnl_usd == 1
    assert result.segments[2].metrics.net_realized_pnl_usd == 5
    assert result.segments[0].end_offset_microseconds == F(1_800_000_000)
    # A nondivisible duration remains rational; no rounded segment boundary.
    times = (START, START + timedelta(minutes=1), START + timedelta(minutes=2, microseconds=1))
    marks = tuple(replay.screening.MarkedEquityPoint(i, t, F(), F()) for i, t in enumerate(times))
    result = replay.screening.evaluate_screening(
        bindings.protocol,
        run_identity=replay.build_replay_run_identity_v2("a" * 64),
        dataset_role=replay.DATASET_ROLE,
        closed_trades=(),
        marked_equity=marks,
        closed_bar_timestamps=times,
    )
    assert result.segments[0].end_offset_microseconds == F(120_000_001, 3)


def test_registered_artifact_binds_final_source_without_any_real_result(bindings):
    root = replay.REPOSITORY / "docs/evidence"
    raw = (root / "EMA_PULLBACK_V2_DEVELOPMENT_REPLAY_IMPLEMENTATION.json").read_bytes()
    evidence = json.loads(raw)
    assert replay.canonical_replay_bytes_v2(evidence) == raw
    assert replay._verify_registration(raw, bindings) == replay.build_replay_run_identity_v2()
    assert evidence["real_development_data_accessed"] is False
    assert evidence["real_strategy_replay"] == "NOT_EXECUTED"
    assert evidence["real_trade_count"] == evidence["real_pnl"] == "NOT_COMPUTED"
    assert evidence["oos_accessed"] is False
    assert evidence["next_gate"] == "EMA_PULLBACK_V2_DEVELOPMENT_REPLAY_EXECUTION_REQUIRED"
    assert (
        evidence["runner_source_sha256"]
        == hashlib.sha256(Path(replay.__file__).read_bytes()).hexdigest()
    )
