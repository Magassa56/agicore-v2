"""Governance tests for the single sanitized MNQ 03-26 V1B replication result."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RESULT_PATH = ROOT / "docs/evidence/EMA_PULLBACK_V1B_MNQ_03_26_REPLICATION_RESULT.json"
CHECKPOINT_PATH = ROOT / "AGICORE_CURRENT_STATE.md"
EXPECTED_RESULT_SHA256 = "968f934c46969c3978575aa96b7e98f015958c731c6ed73a543ebe3a9b8372b6"


def _result() -> dict[str, object]:
    return json.loads(RESULT_PATH.read_text(encoding="utf-8"))


def _keys(value: object) -> set[str]:
    if isinstance(value, dict):
        return set(value) | {key for child in value.values() for key in _keys(child)}
    if isinstance(value, list):
        return {key for child in value for key in _keys(child)}
    return set()


def test_replication_result_is_frozen_and_bound_to_clean_lineage() -> None:
    result = _result()

    assert hashlib.sha256(RESULT_PATH.read_bytes()).hexdigest() == EXPECTED_RESULT_SHA256
    assert result["experiment_id"] == "EMA_PULLBACK_V1B_MNQ_CROSS_CONTRACT_REPLICATION_03_26"
    assert result["run_id"] == "ema-pullback-development-99c298476b51b73a"
    assert result["replay_count"] == 1
    assert result["deterministic"] is True
    assert result["strategy_change"] == "NONE"
    assert result["screening_thresholds_changed"] is False
    assert result["dataset_role"] == "EXPOSED_DEVELOPMENT_REPLICATION"
    assert result["source_raw_sha256"] == (
        "2122722f25dbc865dad154905309b5e76d2190561ffc64acdaa955365ccb9efc"
    )
    assert result["source_size_bytes"] == 3_946_060
    assert result["source_row_count"] == 74_308
    assert result["clean_lineage"] == {
        "status": "PASS",
        "manifest_sha256": "b22371ac3be30952ae58f4b5a8a5d6261b688583bce31ed2dd6c958f7c4b7c80",
        "contract_identity_evidence_sha256": (
            "081386347dcf52ba6eff9b66143b9e217881f11f2cd0a9ab0c4439c7df7c65d7"
        ),
    }


def test_replication_metrics_and_mechanical_outcome_are_exact() -> None:
    result = _result()
    counters = result["counters"]
    metrics = result["metrics"]

    assert counters == {
        "qualified_signals": 478,
        "rejected_by_session_filter": 1101,
        "ignored_signals_while_open": 21,
        "filled_entries": 457,
        "rejected_entries": 0,
        "expired_entries": 0,
        "structural_stop_exit_count": 87,
        "ema20_exit_count": 370,
        "expired_ema20_exits": 0,
        "total_actual_fills": 914,
    }
    assert metrics["closed_trades"] == 457
    assert Decimal(metrics["net_realized_pnl_usd"]) == Decimal("-4758.64")
    assert Decimal(metrics["net_realized_pnl_per_closed_trade_usd"]) == Decimal("-10.41")
    assert Decimal(metrics["profit_factor"]) == Decimal("0.6444307622415035014152113552")
    assert Decimal(metrics["maximum_drawdown_usd"]) == Decimal("4998.09")
    assert metrics["maximum_consecutive_losses"] == 14
    assert result["screening_verdict"] == "NO_GO_VARIANT"
    assert result["segment_stability"] == "FAIL"
    assert all(segment["net_profitable"] is False for segment in result["segments"])
    assert result["replication_assessment"] == {
        "v1b_edge_reproduced": False,
        "material_replication_failure": True,
        "experiment_outcome": "STOP_INCREMENTAL_EMA_PULLBACK_V1_PATH",
        "reason": (
            "The clean MNQ 03-26 replication is net negative, has profit factor below 1.0, "
            "fails all three segment profitability checks, and materially fails to reproduce "
            "the positive MNQ 06-26 V1B development result."
        ),
    }


def test_comparison_is_bound_to_the_three_frozen_predecessor_results() -> None:
    result = _result()
    comparison = result["comparison"]
    expected = {
        "v1_mnq_06_26": (
            "EMA_PULLBACK_V1_MNQ_DEVELOPMENT_REPLAY_RESULT.json",
            "4351d82e2b965b75843b0e24545358c80e2dc544a0549d085ceb8e93f4ceb3f6",
            "3.02",
        ),
        "v1a_mnq_06_26": (
            "EMA_PULLBACK_V1A_MNQ_DEVELOPMENT_REPLAY_RESULT.json",
            "29eef4a574fc46aab07a5ab60fc0c09fe111c3e72acc6d91ae3e5f04450582de",
            "3.74",
        ),
        "v1b_mnq_06_26": (
            "EMA_PULLBACK_V1B_MNQ_DEVELOPMENT_REPLAY_RESULT.json",
            "d3b188c8efed50fc418dab25941b9237261bf39cb88a259c371d7e65e4a0e41b",
            "10.75",
        ),
    }

    for key, (filename, digest, pnl_per_trade) in expected.items():
        predecessor = ROOT / "docs/evidence" / filename
        assert hashlib.sha256(predecessor.read_bytes()).hexdigest() == digest
        assert comparison[key]["result_sha256"] == digest
        assert comparison[key]["net_realized_pnl_per_closed_trade_usd"] == pnl_per_trade

    replication = comparison["v1b_mnq_03_26_replication"]
    assert replication["net_realized_pnl_per_closed_trade_usd"] == "-10.41"
    assert Decimal(replication["profit_factor"]) < Decimal(1)
    assert sum(segment["closed_trades"] for segment in replication["segments"]) == 457


def test_strategy_modules_remain_bit_for_bit_unchanged() -> None:
    expected = {
        "ema_pullback_v1_mnq.py": (
            "af9d9159262e6c027afada5d4faf1aa6374cf696c234ed1de554801d477dcac9"
        ),
        "ema_pullback_v1a_mnq.py": (
            "9f8b88f5b5f476b9f00a7f096e5b74d4eda79771fbce03e166cea699d0305f59"
        ),
        "ema_pullback_v1b_mnq.py": (
            "c61703033504539cda5067798c5b38832f406484e069228c9b6e3eb0533ee717"
        ),
    }
    source = ROOT / "src/agicore/trading"

    for filename, digest in expected.items():
        assert hashlib.sha256((source / filename).read_bytes()).hexdigest() == digest


def test_result_is_sanitized_and_keeps_oos_closed() -> None:
    result = _result()
    keys = _keys(result)

    assert result["oos_accessed"] is False
    assert result["oos_opening_authorized"] is False
    assert result["v1c_authorized"] is False
    assert result["strategy_or_threshold_changed"] is False
    assert result["raw_rows_exposed"] == 0
    assert result["prices_exposed"] == 0
    assert result["trade_detail_rows_exposed"] == 0
    assert {"open", "high", "low", "close", "entry_price", "exit_price"}.isdisjoint(keys)
    assert result["next_gate"] == (
        "BLOCKED_HUMAN_GATE — EMA_PULLBACK_V1_PATH_TERMINATION_DECISION_REQUIRED"
    )


def test_checkpoint_records_single_replay_and_terminal_human_gate() -> None:
    checkpoint = CHECKPOINT_PATH.read_text(encoding="utf-8")

    assert "EMA_PULLBACK_V1B_MNQ_03_26_REPLAY_EXECUTION = COMPLETED_ONCE" in checkpoint
    assert "EMA_PULLBACK_V1B_MNQ_03_26_SCREENING_VERDICT = NO_GO_VARIANT" in checkpoint
    assert "STOP_INCREMENTAL_EMA_PULLBACK_V1_PATH" in checkpoint
    assert "EMA_PULLBACK_V1_PATH_TERMINATION_DECISION_REQUIRED" in checkpoint
    assert EXPECTED_RESULT_SHA256 in checkpoint
    assert "Aucune V1C et aucune\nouverture OOS ne sont autorisées" in checkpoint
