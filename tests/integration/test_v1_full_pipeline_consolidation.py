"""Consolidated integration tests verifying the full V1/V2 offline synthetic chain.

EMA20 CONFIRMATION -> STRUCTURAL STOP -> RISK DECISION -> SYNTHETIC ENTRY -> SYNTHETIC EXIT.
Verifies causality, quantity preservation, price propagation, stop invariants,
producer/verifier independent reconstruction, and tampering rejection.
"""

from __future__ import annotations

import copy
import hashlib
import pytest

from agicore.manager import mission_cycle_v2 as manager
from agicore.trading import synthetic_confirmation_replay_v2 as confirmation_replay
from agicore.trading import synthetic_entry_handoff_v2 as entry_handoff
from agicore.trading import synthetic_exit_handoff_v2 as exit_handoff
from agicore.trading import synthetic_exit_replay_v2 as exit_replay
from agicore.trading import synthetic_mission_storage_v2 as producer
from agicore.trading import synthetic_mission_verify_v2 as verifier
from agicore.trading import synthetic_risk_handoff_v2 as risk_handoff
from agicore.trading import synthetic_stop_handoff_v2 as stop_handoff
from agicore.trading.ema20_pullback_v2 import EMA20PullbackBarV2
from agicore.trading.ema_pullback_entry_execution_v2 import EntryExecutionOpenV2
from agicore.trading.ema_pullback_v2_development_replay import parse_ninjatrader_last_rows_v2
from agicore.trading.synthetic_confirmation_fixture_v2 import generate_confirmation_fixture


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


@pytest.mark.parametrize(
    "profile,expected_stop_reason,expected_end_state,expected_order_semantics",
    [
        ("confirmation-long-v1", "OPEN_UNREALIZED_END_OF_DATA", "OPEN_UNREALIZED", None),
        ("confirmation-short-v1", "OPEN_UNREALIZED_END_OF_DATA", "OPEN_UNREALIZED", None),
        ("confirmation-long-exit-stop-v1", "EXIT_STRUCTURAL_STOP_FILLED", "FLAT", "STOP_MARKET"),
        ("confirmation-short-exit-stop-v1", "EXIT_STRUCTURAL_STOP_FILLED", "FLAT", "STOP_MARKET"),
        ("confirmation-long-exit-ema-v1", "EXIT_EMA20_FILLED", "FLAT", "MARKET"),
        ("confirmation-short-exit-ema-v1", "EXIT_EMA20_FILLED", "FLAT", "MARKET"),
        ("confirmation-long-rejected-v1", "ENTRY_REJECTED_BY_RISK", None, None),
        ("confirmation-short-rejected-v1", "ENTRY_REJECTED_BY_RISK", None, None),
    ],
)
def test_full_pipeline_causality_and_invariants(
    profile: str,
    expected_stop_reason: str,
    expected_end_state: str | None,
    expected_order_semantics: str | None,
):
    """Verify causality and invariant guarantees across all five pipeline stages."""
    raw = generate_confirmation_fixture(profile, observations=39)
    bars = parse_ninjatrader_last_rows_v2(raw)

    # 1. Confirmation Stage
    conf_handoff = confirmation_replay.replay_confirmation_native(raw)
    assert conf_handoff.summary["stop_reason"] == "CONFIRMED_BEFORE_RISK"
    assert conf_handoff.native_confirmation is not None
    eval_conf = conf_handoff.native_confirmation
    native_conf = eval_conf.confirmation
    assert native_conf is not None
    k = native_conf.pullback_bar_index
    q = native_conf.confirmation_bar_index
    assert 0 <= k < q
    assert q - k in (1, 2)
    assert conf_handoff.summary["processed_observations"] == q + 1

    # 2. Structural Stop Stage
    selected = tuple(
        EMA20PullbackBarV2(
            bar.bar_index, bar.timestamp_utc, bar.open, bar.high, bar.low, bar.close, True
        )
        for bar in bars[k : q + 1]
    )
    stop_res = stop_handoff.capture_synthetic_stop_v2(
        confirmation=eval_conf,
        closed_window=selected,
    )
    stop_eval = stop_res.evaluation
    assert stop_eval.status.value == "EVALUATED"
    assert stop_eval.initial_stop_record is not None
    assert stop_eval.initial_stop_record.structural_window_first_bar == k
    assert stop_eval.initial_stop_record.structural_window_last_bar == q
    assert stop_eval.initial_stop_record.stop_known_at_bar_index == q

    # 3. Risk Allocation Stage
    candidate_bar = selected[-1]
    risk_res = risk_handoff.capture_synthetic_risk_v2(
        confirmation=eval_conf,
        initial_stop=stop_eval,
        closed_candidate=candidate_bar,
    )
    risk_record = risk_res.decision
    assert risk_record.confirmation_bar_index == q
    assert risk_record.sizing_decision_known_at_bar == q

    # 4. Entry Execution Stage
    opening_bar = None
    if q + 1 < len(bars):
        next_bar = bars[q + 1]
        opening_bar = EntryExecutionOpenV2(
            bar_index=next_bar.bar_index,
            timestamp_utc=next_bar.timestamp_utc,
            open=next_bar.open,
        )
    entry_res = entry_handoff.capture_synthetic_entry_v2(
        confirmation=eval_conf,
        initial_stop=stop_eval,
        risk_decision=risk_record,
        opening_bar=opening_bar,
    )

    # 5. Exit Policy Stage
    bars_by_index = {
        bar.bar_index: EMA20PullbackBarV2(
            bar.bar_index, bar.timestamp_utc, bar.open, bar.high, bar.low, bar.close, True
        )
        for bar in bars
    }
    exit_res = exit_handoff.capture_synthetic_exit_v2(
        confirmation=eval_conf,
        initial_stop=entry_res.bound_initial_stop,
        risk_decision=risk_record,
        entry_execution=entry_res.execution_evaluation,
        sized_entry=entry_res.sized_entry,
        bars_by_index=bars_by_index,
    )

    assert exit_res.stop_reason == expected_stop_reason
    assert (exit_res.end_state.value if exit_res.end_state is not None else None) == expected_end_state

    # Also verify the canonical native replay gives the exact same result
    replay_env = exit_replay.replay_exit_native(raw)
    assert replay_env["stop_reason"] == expected_stop_reason
    assert replay_env["end_state"] == expected_end_state
    if expected_order_semantics is not None:
        assert replay_env["exit"]["order_semantics"] == expected_order_semantics
    else:
        assert replay_env["exit"] is None

    if expected_stop_reason == "ENTRY_REJECTED_BY_RISK":
        assert risk_record.decision.value == "REJECT"
        assert risk_record.approved_quantity == 0
        assert entry_res.execution_evaluation is None
        assert entry_res.sized_entry is None
        assert exit_res.terminal_exit is None
        assert replay_env["entry"] is None
        assert replay_env["exit"] is None
    else:
        assert risk_record.decision.value == "APPROVE"
        assert risk_record.approved_quantity > 0
        assert entry_res.execution_evaluation is not None
        assert entry_res.execution_evaluation.status.value == "EVALUATED"
        assert entry_res.sized_entry is not None
        assert entry_res.execution_evaluation.execution.execution_bar_index == q + 1
        assert entry_res.sized_entry.quantity == risk_record.approved_quantity

        if expected_end_state == "FLAT":
            assert exit_res.terminal_exit is not None
            if expected_order_semantics == "STOP_MARKET":
                assert replay_env["exit"]["trigger_bar_index"] >= q + 1
                assert "base_stop_fill_price" in replay_env["exit"]
            elif expected_order_semantics == "MARKET":
                assert replay_env["exit"]["exit_execution_bar_index"] >= q + 1
                assert "base_exit_fill_price" in replay_env["exit"]
        elif expected_end_state == "OPEN_UNREALIZED":
            assert exit_res.terminal_exit is None
            assert replay_env["exit"] is None


def test_independent_reconstruction_parity(tmp_path):
    """Verify bit-level parity between producer bundle verification and verifier reconstruction."""
    for idx, profile in enumerate((
        "confirmation-long-v1",
        "confirmation-short-exit-stop-v1",
        "confirmation-long-exit-ema-v1",
        "confirmation-short-rejected-v1",
    )):
        bundle = tmp_path / f"bundle_{idx}"
        worker = producer.produce(bundle, 39, stage="exit", profile=profile)
        verified = verifier.verify(bundle, 39, stage="exit", profile=profile)

        assert verified["status"] == "PASS"
        assert verified["stage"] == "exit"
        assert verified["input_sha256"] == worker["input_sha256"]
        assert verified["replay"] == worker["replay"]


def test_tampered_bundle_or_receipt_rejected(tmp_path):
    """Verify fail-closed rejection of tampered receipts or chunks."""
    profile = "confirmation-long-exit-stop-v1"
    bundle = tmp_path / "bundle_tamper"
    worker = producer.produce(bundle, 39, stage="exit", profile=profile)
    replay = worker["replay"]

    # Valid replay passes
    assert manager._valid_exit_replay(replay, worker) is True

    # Tampered exit semantics rejected
    tampered_replay = copy.deepcopy(replay)
    tampered_replay["exit"]["order_semantics"] = "FORGED_LIMIT"
    assert manager._valid_exit_replay(tampered_replay, worker) is False

    # Tampered end state rejected
    tampered_replay2 = copy.deepcopy(replay)
    tampered_replay2["end_state"] = "OPEN_UNREALIZED"
    assert manager._valid_exit_replay(tampered_replay2, worker) is False
