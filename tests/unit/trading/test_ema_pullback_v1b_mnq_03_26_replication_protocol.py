"""Fail-closed checks for the precommitted MNQ 03-26 V1B replication."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "docs" / "evidence"
PROTOCOL = EVIDENCE / "EMA_PULLBACK_V1B_MNQ_03_26_REPLICATION_PROTOCOL.json"
EXPECTED_PROTOCOL_SHA256 = "c431c991c290f000bfdd9f39f01372ccfc05c963911e11534184d1ab95b07d37"
EXPECTED_IMMUTABLE_HASHES = {
    ROOT / "src/agicore/trading/ema_pullback_v1_mnq.py": (
        "af9d9159262e6c027afada5d4faf1aa6374cf696c234ed1de554801d477dcac9"
    ),
    ROOT / "src/agicore/trading/ema_pullback_v1a_mnq.py": (
        "9f8b88f5b5f476b9f00a7f096e5b74d4eda79771fbce03e166cea699d0305f59"
    ),
    ROOT / "src/agicore/trading/ema_pullback_v1b_mnq.py": (
        "c61703033504539cda5067798c5b38832f406484e069228c9b6e3eb0533ee717"
    ),
    EVIDENCE / "EMA_PULLBACK_V1_MNQ_DEVELOPMENT_REPLAY_RESULT.json": (
        "4351d82e2b965b75843b0e24545358c80e2dc544a0549d085ceb8e93f4ceb3f6"
    ),
    EVIDENCE / "EMA_PULLBACK_V1A_MNQ_DEVELOPMENT_REPLAY_RESULT.json": (
        "29eef4a574fc46aab07a5ab60fc0c09fe111c3e72acc6d91ae3e5f04450582de"
    ),
    EVIDENCE / "EMA_PULLBACK_V1B_MNQ_DEVELOPMENT_REPLAY_RESULT.json": (
        "d3b188c8efed50fc418dab25941b9237261bf39cb88a259c371d7e65e4a0e41b"
    ),
}


def _payload() -> dict[str, object]:
    return json.loads(PROTOCOL.read_text(encoding="utf-8"))


def test_replication_protocol_hash_and_frozen_parents_are_exact() -> None:
    assert hashlib.sha256(PROTOCOL.read_bytes()).hexdigest() == EXPECTED_PROTOCOL_SHA256
    for path, expected_hash in EXPECTED_IMMUTABLE_HASHES.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected_hash

    payload = _payload()
    assert payload["experiment_id"] == "EMA_PULLBACK_V1B_MNQ_CROSS_CONTRACT_REPLICATION_03_26"
    strategy = payload["strategy_under_test"]
    assert isinstance(strategy, dict)
    assert strategy["variant_id"] == "EMA_PULLBACK_V1B_MNQ_V1A_US_RTH_ENTRY_ONLY"
    assert strategy["strategy_change"] == "NONE"
    assert strategy["immutability"] == "BIT_FOR_BIT_REQUIRED"

    parents = payload["frozen_parent_results"]
    assert isinstance(parents, dict)
    assert parents["v1"]["verdict"] == "NO_GO_BASELINE"
    assert parents["v1a"]["verdict"] == "NO_GO_VARIANT"
    assert parents["v1b_mnq_06_26"]["verdict"] == "NO_GO_VARIANT"


def test_replication_source_and_window_are_precommitted_fail_closed() -> None:
    payload = _payload()
    source = payload["required_source_contract"]
    assert source == {
        "instrument": "MNQ",
        "contract_id": "MNQ 03-26",
        "bar_interval": "1 minute",
        "data_type": "Last",
        "merge_policy": "DoNotMerge",
        "continuous_contract": False,
        "trading_hours_template": "CME US Index Futures ETH",
        "account_provider": "Apex Trader Funding",
        "market_data_provider_or_routing": "Rithmic",
        "platform": "NinjaTrader",
        "source_raw_filename": "MNQ 03-26.Last.txt",
        "dataset_role": "EXPOSED_DEVELOPMENT_REPLICATION",
    }

    lineage = payload["clean_lineage_gate"]
    assert isinstance(lineage, dict)
    assert lineage["required_status_before_replay"] == "PASS"
    assert lineage["current_status"] == "BLOCKED_MISSING_NEW_EXPORT_AND_EVIDENCE"
    assert lineage["source_raw_sha256"] == "REQUIRED_BEFORE_REPLAY"
    assert lineage["source_size_bytes"] == "REQUIRED_BEFORE_REPLAY"
    assert lineage["source_row_count"] == "REQUIRED_BEFORE_REPLAY"
    assert lineage["export_receipt_sha256"] == "REQUIRED_BEFORE_REPLAY"
    assert lineage["prohibited_source"] == ("MNQ_OHLCV_2024_2025_03-26_SANS_09-26(1).zip")

    window = payload["precommitted_contract_window"]
    assert isinstance(window, dict)
    assert window["ninjatrader_export_from_local_date_inclusive"] == "2026-01-01"
    assert window["ninjatrader_export_to_local_date_inclusive"] == "2026-03-31"
    assert window["interpretation_timezone"] == "America/Chicago"
    assert window["source_timestamp_timezone"] == "UTC"
    assert window["timestamp_semantics"] == "BAR_CLOSE"
    assert window["dst_policy"] == "IANA_TIMEZONE_RULES"
    assert window["pnl_based_date_selection"] == "FORBIDDEN"
    assert window["post_result_window_change"] == "FORBIDDEN"


def test_v1b_and_original_screening_are_unchanged() -> None:
    payload = _payload()
    unchanged = payload["unchanged_v1b_contract"]
    assert isinstance(unchanged, dict)
    assert unchanged["ema20_minimum_absolute_slope_points_per_bar"] == "0.25"
    assert unchanged["us_rth_entry_filter"] == (
        "08:30:00_INCLUSIVE_TO_15:00:00_EXCLUSIVE_AMERICA_CHICAGO_MONDAY_FRIDAY"
    )
    assert unchanged["take_profit"] == "NONE"
    assert unchanged["breakeven"] == "NONE"
    assert unchanged["trailing_stop"] == "NONE"
    assert unchanged["position_size_mnq"] == 1

    screening = payload["screening"]
    assert isinstance(screening, dict)
    assert screening == {
        "protocol_id": "EMA_PULLBACK_V1_MNQ_DEVELOPMENT_SCREENING_2026_09_27",
        "protocol_sha256": "13f3e1b71ce27a848a16a9598c37d76e9298a49331531fc7602118ec788c864f",
        "minimum_closed_trades": 100,
        "minimum_net_pnl_usd": "200.00",
        "minimum_profit_factor": "1.15",
        "maximum_drawdown_usd": "750.00",
        "maximum_consecutive_losses": 8,
        "segment_stability_rule": "UNCHANGED",
        "comparators_at_boundary": "INCLUSIVE",
        "threshold_changes": "FORBIDDEN",
    }


def test_replication_outcomes_and_execution_gate_are_not_optimizable() -> None:
    payload = _payload()
    assessment = payload["replication_assessment"]
    assert isinstance(assessment, dict)
    assert assessment["material_edge_failure_action"] == ("STOP_INCREMENTAL_EMA_PULLBACK_V1_PATH")
    assert assessment["mixed_development_evidence_action"] == "RETURN_TO_HUMAN_GATE"
    assert assessment["favorable_replication_action"] == (
        "RETURN_TO_HUMAN_GATE_WITHOUT_OPENING_OOS"
    )
    assert assessment["oos_auto_open"] is False
    assert assessment["v1c_auto_creation"] is False

    execution = payload["execution_gate"]
    assert isinstance(execution, dict)
    assert execution["maximum_effective_replay_count"] == 1
    assert execution["current_replay_count"] == 0
    assert execution["replay_authorized_now"] is False
    assert all(
        execution[key] is True
        for key in (
            "deterministic_replay_required",
            "clean_lineage_pass_required",
            "protocol_hash_freeze_required",
            "implementation_hash_freeze_required",
            "tests_pass_required",
            "ci_green_required",
        )
    )


def test_protocol_contains_no_market_rows_prices_oos_or_hidden_v1c() -> None:
    payload = _payload()
    privacy = payload["privacy"]
    assert isinstance(privacy, dict)
    assert privacy == {
        "raw_files_committed": False,
        "market_rows_committed": 0,
        "prices_committed": 0,
        "account_identifiers_committed": False,
        "credentials_committed": False,
        "oos_accessed": False,
    }
    assert "V1C_ON_MNQ_06_26" in payload["prohibitions"]

    public_text = PROTOCOL.read_text(encoding="utf-8")
    assert re.search(r"(?m)^\d{8} \d{6};", public_text) is None
    assert re.search(r"(?m)^\d{8};", public_text) is None
