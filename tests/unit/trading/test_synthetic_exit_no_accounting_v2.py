"""Synthetic exits must never call the frozen accounting/PnL layer."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta
from fractions import Fraction

import pytest

from agicore.trading import ema_pullback_fees_and_slippage_v2 as accounting
from agicore.trading import ema_pullback_open_position_signal_policy_v2 as positions
from agicore.trading import synthetic_mission_verify_v2 as verifier
from agicore.trading import synthetic_risk_handoff_v2 as risk_handoff
from agicore.trading.ema_pullback_entry_execution_v2 import (
    EntryExecutionStateV2,
    EntryExecutionStatusV2,
)
from agicore.trading.ema_pullback_exit_policy_v2 import EMA20ExitExecutionStateV2
from agicore.trading.synthetic_confirmation_fixture_v2 import (
    PROFILES,
    generate_confirmation_fixture,
)
from agicore.trading.synthetic_entry_replay_v2 import replay_entry_native
from agicore.trading.synthetic_exit_handoff_v2 import capture_synthetic_exit_v2
from agicore.trading.synthetic_exit_replay_v2 import replay_exit_native
from agicore.trading.synthetic_mission_verify_v2 import reconstruct_exit_native
from agicore.trading.synthetic_risk_replay_v2 import replay_risk_native
from tests.unit.trading.test_synthetic_exit_handoff_v2 import _setup_handoff


@pytest.fixture(autouse=True)
def no_accounting(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("synthetic exit called accounting, fees, slippage or PnL")

    for name in (
        "calculate_fill_cost_v2",
        "account_entry_fill_v2",
        "account_structural_stop_fill_v2",
        "account_ema20_exit_fill_v2",
        "report_usd_cents_v2",
    ):
        monkeypatch.setattr(accounting, name, forbidden)
    monkeypatch.setattr(accounting.FillCostRecordV2, "__post_init__", forbidden)
    monkeypatch.setattr(accounting.TradeCostRecordV2, "__post_init__", forbidden)
    monkeypatch.setattr(accounting.FeesAndSlippageBookV2, "__post_init__", forbidden)
    for name in (
        "total_fees_usd",
        "diagnostic_total_slippage_cost_usd",
        "gross_price_pnl_usd",
        "net_realized_pnl_usd",
    ):
        monkeypatch.setattr(accounting.TradeCostRecordV2, name, property(forbidden))


@pytest.mark.parametrize("profile", PROFILES)
def test_worker_and_independent_reconstruction_never_account(profile):
    raw = generate_confirmation_fixture(profile, 39)
    worker = replay_exit_native(raw)
    verification = reconstruct_exit_native(raw)
    assert worker == verification
    if "rejected" in profile:
        assert worker["risk"]["decision"] == "REJECT"
        assert worker["entry"] is None and worker["sized_entry"] is None and worker["exit"] is None
    else:
        assert worker["risk"]["decision"] == "APPROVE"
        assert worker["entry"]["execution"]["execution_bar_index"] == 36
        assert (
            worker["sized_entry"]["risk_decision"]["approved_quantity"]
            == worker["risk"]["approved_quantity"]
        )


@pytest.mark.parametrize(
    "replay",
    [
        replay_risk_native,
        replay_entry_native,
        replay_exit_native,
        verifier.reconstruct_risk_native,
        verifier.reconstruct_entry_native,
        verifier.reconstruct_exit_native,
    ],
)
@pytest.mark.parametrize("corruption", ["missing", "forged"])
def test_missing_or_forged_admission_fails_before_risk(monkeypatch, replay, corruption):
    raw = generate_confirmation_fixture("confirmation-long-v1", 39)
    original = positions.advance_open_position_signal_policy_v2

    def corrupt_admission(**kwargs):
        clock = original(**kwargs)
        decisions = []
        for decision in clock.signal_decisions:
            candidate = decision.pullback
            if (
                candidate is None
                or candidate.pullback is None
                or not candidate.pullback.pullback_qualified
            ):
                decisions.append(decision)
                continue
            if corruption == "missing":
                continue
            context = candidate.lifetime.context
            forged = replace(context, ema_reference=context.ema_reference + Fraction(1, 4))
            lifetime = replace(candidate.lifetime, context=forged)
            decisions.append(replace(decision, pullback=replace(candidate, lifetime=lifetime)))
        return replace(clock, signal_decisions=tuple(decisions))

    def forbidden_risk(*args, **kwargs):
        pytest.fail("risk calculation ran before verifying admission")

    monkeypatch.setattr(positions, "advance_open_position_signal_policy_v2", corrupt_admission)
    monkeypatch.setattr(risk_handoff, "evaluate_risk_position_sizing_v2", forbidden_risk)
    monkeypatch.setattr(verifier, "evaluate_risk_position_sizing_v2", forbidden_risk)
    with pytest.raises(positions.OpenPositionSignalPolicyV2Error, match="fresh admitted"):
        replay(raw)


@pytest.mark.parametrize("direction", ["long", "short"])
def test_opening_gap_wins_over_pending_ema(direction):
    raw = generate_confirmation_fixture(f"confirmation-{direction}-exit-ema-v1", 39)
    rows = raw.decode("ascii").splitlines()
    fields = rows[37].split(";")
    if direction == "long":
        fields[1:5] = ["19999", "20002", "19998", "20000"]
    else:
        fields[1:5] = ["20001", "20002", "19998", "20000"]
    rows[37] = ";".join(fields)
    changed = ("\n".join(rows) + "\n").encode("ascii")
    worker = replay_exit_native(changed)
    assert worker == reconstruct_exit_native(changed)
    assert worker["stop_reason"] == "EXIT_STRUCTURAL_STOP_FILLED"
    assert worker["exit"]["trigger_phase"] == "BAR_OPEN_GAP"
    assert worker["exit"]["trigger_bar_index"] == 37


@pytest.mark.parametrize("direction", ["long", "short"])
def test_later_valid_row_cannot_change_an_already_filled_stop(direction):
    raw = generate_confirmation_fixture(f"confirmation-{direction}-exit-stop-v1", 39)
    rows = raw.decode("ascii").splitlines()
    fields = rows[38].split(";")
    fields[-1] = "999"
    rows[38] = ";".join(fields)
    changed = ("\n".join(rows) + "\n").encode("ascii")
    before, after = replay_exit_native(raw), replay_exit_native(changed)
    assert before["input_sha256"] != after["input_sha256"]
    for key in (
        "confirmation",
        "window",
        "stop",
        "risk",
        "entry",
        "sized_entry",
        "exit",
        "end_state",
        "stop_reason",
    ):
        assert before[key] == after[key]
    assert after == reconstruct_exit_native(changed)


@pytest.mark.parametrize("direction", ["long", "short"])
def test_ema_next_open_exit_does_not_read_later_intrabar_or_future_prices(direction):
    signal, entry, risk, bars = _setup_handoff(f"confirmation-{direction}-exit-ema-v1")
    opening = bars[37]

    class OpenOnly:
        bar_index = opening.bar_index
        timestamp_utc = opening.timestamp_utc
        open = opening.open

        def __getattr__(self, name):
            raise AssertionError(f"exit read unavailable Open-phase field {name}")

    class FutureUnavailable:
        def __getattribute__(self, name):
            raise AssertionError(f"exit read future bar field {name}")

    bars[37] = OpenOnly()
    bars[38] = FutureUnavailable()
    result = capture_synthetic_exit_v2(
        confirmation=signal,
        initial_stop=entry.bound_initial_stop,
        risk_decision=risk,
        entry_execution=entry.execution_evaluation,
        sized_entry=entry.sized_entry,
        bars_by_index=bars,
    )
    assert result.stop_reason == "EXIT_EMA20_FILLED"
    assert result.terminal_exit.exit_execution_bar_index == 37


def test_elapsed_gap_expires_one_ema_signal_without_future_leak():
    raw = generate_confirmation_fixture("confirmation-long-exit-ema-v1", 39)
    rows = raw.decode("ascii").splitlines()
    for index in (37, 38):
        fields = rows[index].split(";")
        fields[0] = (datetime.strptime(fields[0], "%Y%m%d %H%M%S") + timedelta(minutes=1)).strftime(
            "%Y%m%d %H%M%S"
        )
        rows[index] = ";".join(fields)
    changed = ("\n".join(rows) + "\n").encode("ascii")
    worker = replay_exit_native(changed)
    assert worker == reconstruct_exit_native(changed)
    assert worker["stop_reason"] == "OPEN_UNREALIZED_END_OF_DATA"
    assert worker["exit"] is None
    signal, entry, risk, bars = _setup_handoff("confirmation-long-exit-ema-v1")
    for index in (37, 38):
        bars[index] = replace(
            bars[index], timestamp_utc=bars[index].timestamp_utc + timedelta(minutes=1)
        )
    outcome = capture_synthetic_exit_v2(
        confirmation=signal,
        initial_stop=entry.bound_initial_stop,
        risk_decision=risk,
        entry_execution=entry.execution_evaluation,
        sized_entry=entry.sized_entry,
        bars_by_index=bars,
    )
    assert outcome.exit_book.ema_executions[0].state is EMA20ExitExecutionStateV2.EXPIRED_EXIT_GAP


@pytest.mark.parametrize("direction", ["long", "short"])
@pytest.mark.parametrize(
    ("case", "expected_state"),
    [("missing", "EXPIRED_NO_EXECUTION"), ("late", "EXPIRED_EXECUTION_GAP")],
)
def test_unfilled_entry_has_same_safe_result_in_both_replays(direction, case, expected_state):
    rows = (
        generate_confirmation_fixture(f"confirmation-{direction}-v1", 39)
        .decode("ascii")
        .splitlines()
    )
    if case == "missing":
        rows = rows[:36]
    else:
        for index in (36, 37, 38):
            fields = rows[index].split(";")
            stamp = datetime.strptime(fields[0], "%Y%m%d %H%M%S") + timedelta(minutes=1)
            fields[0] = stamp.strftime("%Y%m%d %H%M%S")
            rows[index] = ";".join(fields)
    raw = ("\n".join(rows) + "\n").encode("ascii")
    worker = replay_exit_native(raw)
    assert worker == reconstruct_exit_native(raw)
    assert worker["risk"]["decision"] == "APPROVE"
    assert worker["entry"]["execution_state"] == expected_state
    assert worker["entry"]["execution"] is None
    assert worker["sized_entry"] is None
    assert worker["stop"]["at_entry"] is None
    assert worker["exit"] is None and worker["end_state"] is None
    assert worker["stop_reason"] == f"ENTRY_{expected_state}"


@pytest.mark.parametrize("kind", ["execution", "sizing", "bound_stop", "status", "source"])
def test_unfilled_entry_rejects_contradictory_state(kind):
    signal, filled, risk, bars = _setup_handoff("confirmation-long-v1")
    unbound_stop = replace(filled.bound_initial_stop, at_entry=None)
    expired = replace(
        filled.execution_evaluation,
        execution_state=EntryExecutionStateV2.EXPIRED_NO_EXECUTION,
        status=EntryExecutionStatusV2.EVALUATED,
        execution=None,
    )
    args = {
        "confirmation": signal,
        "initial_stop": unbound_stop,
        "risk_decision": risk,
        "entry_execution": expired,
        "sized_entry": None,
        "bars_by_index": bars,
    }
    if kind == "execution":
        args["entry_execution"] = replace(expired, execution=filled.execution_evaluation.execution)
    elif kind == "sizing":
        args["sized_entry"] = filled.sized_entry
    elif kind == "bound_stop":
        args["initial_stop"] = filled.bound_initial_stop
    elif kind == "status":
        args["entry_execution"] = replace(expired, status=EntryExecutionStatusV2.NOT_EVALUATED)
    else:
        different = replace(expired.confirmation, confirmation_bar_index=99)
        args["entry_execution"] = replace(expired, confirmation=different)
    with pytest.raises(ValueError):
        capture_synthetic_exit_v2(**args)


def test_filled_entry_requires_sizing_record():
    signal, filled, risk, bars = _setup_handoff("confirmation-long-v1")
    with pytest.raises(ValueError, match="filled execution requires"):
        capture_synthetic_exit_v2(
            confirmation=signal,
            initial_stop=filled.bound_initial_stop,
            risk_decision=risk,
            entry_execution=filled.execution_evaluation,
            sized_entry=None,
            bars_by_index=bars,
        )
