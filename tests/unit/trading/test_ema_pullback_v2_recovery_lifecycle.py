"""Per-phase exact state comparisons, before any resource or real execution gate."""

import hashlib
import os
from copy import deepcopy
from dataclasses import fields
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from agicore.trading import ema_pullback_regime_gated_baseline_v2 as reference
from agicore.trading import ema_pullback_v2_development_replay as replay
from agicore.trading.ema_pullback_v2_recovery_lifecycle import RecoveryLifecycleV1
from agicore.trading.regime_context_v2 import RegimeDirection
from tests.unit.trading.v2_recovery_synthetic_fixtures import SCENARIOS, lifecycle_fixture

COUNTEREXAMPLES = Path(os.environ.get(
    "V2_RECOVERY_COUNTEREXAMPLES", "/tmp/v2-recovery-semantic-repair-counterexamples"))


def _equal(candidate, expected, fixture, name, index, phase):
    if candidate != expected:
        stem = COUNTEREXAMPLES / ("counterexample-" + name + "-" + str(index) + "-" + phase)
        stem.with_suffix(".Last.txt").write_bytes(fixture)
        for label, value in (("reference", expected), ("candidate", candidate)):
            raw = reference.deterministic_baseline_snapshot_v2(value)
            Path(str(stem) + "." + label + ".json").write_bytes(raw)
        pytest.fail("BLOCKED_SEMANTIC_EQUIVALENCE: counterexample preserved at " + str(stem))


@pytest.mark.parametrize("name", SCENARIOS)
@pytest.mark.parametrize("direction", tuple(RegimeDirection))
def test_every_open_close_and_end_state_exact_twice(name, direction):
    fixture = lifecycle_fixture(name, direction)
    outputs = []
    for _ in range(2):
        dataset_id = "synthetic-" + hashlib.sha256(fixture).hexdigest()[:16] + "-v1"
        engine = RecoveryLifecycleV1(strategy_instance_id=reference.STRATEGY_ID,
                                     series_id=dataset_id)
        expected = reference.begin_regime_gated_baseline_v2(
            strategy_instance_id=reference.STRATEGY_ID, series_id=dataset_id)
        for bar in replay.parse_ninjatrader_last_rows_v2(fixture):
            opening = reference.execution.EntryExecutionOpenV2(
                bar.bar_index, bar.timestamp_utc, bar.open)
            expected = reference.process_baseline_open_v2(previous=expected, opening_bar=opening)
            engine.process_open(opening)
            _equal(engine.snapshot(), expected, fixture, name + direction, bar.bar_index, "OPEN")
            expected = reference.process_baseline_close_v2(previous=expected,
                                                           closed_bar=bar.closed_view())
            engine.process_close(bar.closed_view())
            _equal(engine.snapshot(), expected, fixture, name + direction, bar.bar_index, "CLOSE")
            assert len(engine.live.closed_bars) <= 21
            assert len(engine.live.policy.opportunities) <= 1
            assert len(engine.live.policy.positions.signal_decisions) <= 2
        expected = reference.finish_regime_gated_baseline_v2(previous=expected)
        engine.finish()
        final = engine.snapshot()
        _equal(final, expected, fixture, name + direction, bar.bar_index, "END")
        outputs.append(reference.deterministic_baseline_snapshot_v2(final))
    assert outputs[0] == outputs[1]


def test_malformed_close_preserves_reference_error_contract_after_one_observation():
    import json

    fixture = lifecycle_fixture("impulse_profit", RegimeDirection.LONG)
    first = replay.parse_ninjatrader_last_rows_v2(fixture)[0]
    engine = RecoveryLifecycleV1(strategy_instance_id=reference.STRATEGY_ID,
                                 series_id="synthetic-malformed-close-v1")
    expected = reference.begin_regime_gated_baseline_v2(
        strategy_instance_id=reference.STRATEGY_ID, series_id="synthetic-malformed-close-v1")
    opening = reference.execution.EntryExecutionOpenV2(
        first.bar_index, first.timestamp_utc, first.open)
    expected = reference.process_baseline_open_v2(previous=expected, opening_bar=opening)
    engine.process_open(opening)
    expected = reference.process_baseline_close_v2(previous=expected, closed_bar=first.closed_view())
    engine.process_close(first.closed_view())
    assert engine.snapshot() == expected

    def outcome(callback):
        try:
            callback()
        except Exception as error:  # noqa: BLE001 -- compare exact rejected-input contract
            return {"exception_type": type(error).__name__, "message": str(error)}
        return {"exception_type": None, "message": None}

    original = outcome(lambda: reference.process_baseline_close_v2(
        previous=expected, closed_bar=None))
    optimized = outcome(lambda: engine.process_close(None))
    if original != optimized:
        COUNTEREXAMPLES.mkdir(parents=True, exist_ok=True)
        stem = COUNTEREXAMPLES / "counterexample-malformed-close-after-one-observation"
        inputs = {"source_fixture_sha256": hashlib.sha256(fixture).hexdigest(),
                  "processed_actual_observations": 1, "rejected_close_argument": None,
                  "input_domain": "INVENTED_SYNTHETIC_ONLY"}
        for label, value in (("inputs", inputs), ("reference-error", original),
                             ("candidate-error", optimized)):
            Path(str(stem) + "." + label + ".json").write_bytes(
                (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode())
        Path(str(stem) + ".source-fixture.Last.txt").write_bytes(fixture)
        Path(str(stem) + ".reference-state.json").write_bytes(
            reference.deterministic_baseline_snapshot_v2(expected))
        Path(str(stem) + ".candidate-state.json").write_bytes(
            reference.deterministic_baseline_snapshot_v2(engine.snapshot()))
        pytest.fail("BLOCKED_SEMANTIC_EQUIVALENCE: " + str(stem))
    assert optimized == original


class _WrongClose:
    def __init__(self, index, *, poison_index=False):
        self.index = index
        self.poison_index = poison_index
        self.reads = []

    @property
    def bar_index(self):
        self.reads.append("bar_index")
        if self.poison_index:
            raise RuntimeError("invented unavailable index")
        return self.index

    def __getattr__(self, name):
        self.reads.append(name)
        raise AssertionError("unavailable field read: " + name)


class _TracedClose(reference.impulse.DirectionalImpulseBarV2):
    def __post_init__(self):
        object.__setattr__(self, "reads", [])
        super().__post_init__()
        self.reads.clear()

    def __getattribute__(self, name):
        if name in {"bar_index", "timestamp_utc", "is_closed", "open", "high", "low",
                    "close", "volume"}:
            object.__getattribute__(self, "reads").append(name)
        return super().__getattribute__(name)


_GUARD_CASES = (
    ("INITIAL", "none"), ("INITIAL", "plain"), ("INITIAL", "next_without_open"),
    ("CLOSED", "none"), ("CLOSED", "plain"), ("CLOSED", "next_without_open"),
    ("OPEN_NEXT", "wrong_indexed"), ("OPEN_NEXT", "poison_index"),
    ("OPEN_NEXT", "unclosed"), ("OPEN_NEXT", "truthy_closed"),
    ("OPEN_NEXT", "index_mismatch"), ("OPEN_NEXT", "timestamp_past"),
    ("OPEN_NEXT", "timestamp_future"), ("OPEN_NEXT", "open_mismatch"),
    ("CLOSED", "duplicate"), ("CLOSED", "duplicate_wrong_type"),
    ("CLOSED", "duplicate_unclosed"), ("CLOSED", "duplicate_malformed"),
    ("EOD", "none"), ("EOD", "poison_index"), ("EOD", "next_without_open"),
)


def _guard_argument(case, first, following):
    if case == "none":
        return None
    if case == "plain":
        return object()
    if case in ("wrong_indexed", "duplicate_wrong_type", "poison_index"):
        return _WrongClose(0 if case == "duplicate_wrong_type" else 1,
                           poison_index=case == "poison_index")
    if case.startswith("duplicate"):
        base = first.closed_view()
        changes = {}
        if case == "duplicate_unclosed":
            changes = {"is_closed": False}
        elif case == "duplicate_malformed":
            changes = {"is_closed": False, "timestamp_utc": None, "open": None}
    else:
        base = following.closed_view()
        changes = {
            "unclosed": {"is_closed": False},
            "truthy_closed": {"is_closed": 1},
            "index_mismatch": {"bar_index": 2},
            "timestamp_past": {"timestamp_utc": following.timestamp_utc - timedelta(minutes=1)},
            "timestamp_future": {"timestamp_utc": following.timestamp_utc + timedelta(minutes=1)},
            "open_mismatch": {"open": following.open + Decimal("0.25")},
        }
        changes = changes.get(case, {})
    traced = _TracedClose(**{field.name: getattr(base, field.name) for field in fields(base)})
    # Deliberately malformed synthetic instances exercise the frozen reducer's
    # own precedence; no frozen constructor/source/global is altered.
    for name, value in changes.items():
        object.__setattr__(traced, name, value)
    traced.reads.clear()
    return traced


@pytest.mark.parametrize("stage,case", _GUARD_CASES)
def test_close_rejection_and_terminal_precedence_exact_without_mutation(stage, case):
    import json

    fixture = lifecycle_fixture("impulse_profit", RegimeDirection.LONG)
    first, following = replay.parse_ninjatrader_last_rows_v2(fixture)[:2]
    engine = RecoveryLifecycleV1(strategy_instance_id=reference.STRATEGY_ID,
                                 series_id="synthetic-close-guard-v1")
    expected = reference.begin_regime_gated_baseline_v2(
        strategy_instance_id=reference.STRATEGY_ID, series_id="synthetic-close-guard-v1")
    if stage != "INITIAL":
        opening = reference.execution.EntryExecutionOpenV2(
            first.bar_index, first.timestamp_utc, first.open)
        expected = reference.process_baseline_open_v2(previous=expected, opening_bar=opening)
        engine.process_open(opening)
        expected = reference.process_baseline_close_v2(previous=expected,
                                                       closed_bar=first.closed_view())
        engine.process_close(first.closed_view())
    if stage == "OPEN_NEXT":
        opening = reference.execution.EntryExecutionOpenV2(
            following.bar_index, following.timestamp_utc, following.open)
        expected = reference.process_baseline_open_v2(previous=expected, opening_bar=opening)
        engine.process_open(opening)
    if stage == "EOD":
        expected = reference.finish_regime_gated_baseline_v2(previous=expected)
        engine.finish()
    assert engine.snapshot() == expected
    live_before = engine.live
    indicators_before = deepcopy(engine.indicators.__dict__)
    ledgers_before = {path: (tuple(ledger.versions), dict(ledger.latest), tuple(ledger.order))
                      for path, ledger in engine.histories.items()}

    def outcome(callback):
        try:
            callback()
        except Exception as error:  # noqa: BLE001 -- exact reference exception identity
            return type(error), str(error)
        return None, None

    original_arg = _guard_argument(case, first, following)
    candidate_arg = _guard_argument(case, first, following)
    original = outcome(lambda: reference.process_baseline_close_v2(
        previous=expected, closed_bar=original_arg))
    optimized = outcome(lambda: engine.process_close(candidate_arg))
    original_reads = list(getattr(original_arg, "reads", []))
    candidate_reads = list(getattr(candidate_arg, "reads", []))
    indicator_equal = engine.indicators.__dict__ == indicators_before
    ledger_equal = ledgers_before == {
        path: (tuple(ledger.versions), dict(ledger.latest), tuple(ledger.order))
        for path, ledger in engine.histories.items()}
    state_equal = engine.live is live_before and engine.snapshot() == expected
    if (original != optimized or original_reads != candidate_reads
            or not indicator_equal or not ledger_equal or not state_equal):
        COUNTEREXAMPLES.mkdir(parents=True, exist_ok=True)
        stem = COUNTEREXAMPLES / ("close-guard-" + stage + "-" + case)
        document = {"stage": stage, "argument_factory": case,
                    "source_fixture_sha256": hashlib.sha256(fixture).hexdigest(),
                    "reference_exception": None if original[0] is None else original[0].__name__,
                    "candidate_exception": None if optimized[0] is None else optimized[0].__name__,
                    "reference_message": original[1], "candidate_message": optimized[1],
                    "reference_field_reads": original_reads, "candidate_field_reads": candidate_reads,
                    "state_unchanged": state_equal, "indicators_unchanged": indicator_equal,
                    "ledgers_unchanged": ledger_equal}
        with Path(str(stem) + ".json").open("xb") as stream:
            stream.write((json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n").encode())
        with Path(str(stem) + ".fixture.Last.txt").open("xb") as stream:
            stream.write(fixture)
        pytest.fail("BLOCKED_SEMANTIC_EQUIVALENCE: " + str(stem))
    assert original == optimized
    assert original_reads == candidate_reads
    assert indicator_equal and ledger_equal and state_equal
    receipt_path = os.environ.get("V2_RECOVERY_ERROR_CONTRACT_RECEIPTS")
    if receipt_path:
        receipt = {"stage": stage, "case": case,
                   "error_type": None if original[0] is None else original[0].__name__,
                   "error_message": original[1], "field_reads": original_reads,
                   "state_unchanged": True, "exact_exception_and_precedence": True}
        with Path(receipt_path).open("ab") as stream:
            stream.write((json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n").encode())
