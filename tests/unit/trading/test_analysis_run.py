"""Tests for the explicit local NinjaTrader analysis bundle."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from agicore.trading.analysis_run import AnalysisRunError, create_analysis_run


def _write_csv(path: Path) -> str:
    content = "\n".join(
        [
            "Entry time,Exit time,Profit,MAE,MFE",
            "2026-07-01 09:30:00,2026-07-01 09:31:00,100,-20,120",
            "2026-07-01 10:00:00,2026-07-01 10:01:00,(50),-80,10",
            "2026-07-02 10:00:00,2026-07-02 10:01:00,(25),-40,5",
        ]
    )
    path.write_text(content, encoding="utf-8")
    return content


def test_create_analysis_run_writes_complete_deterministic_bundle(tmp_path) -> None:
    csv_path = tmp_path / "trades.csv"
    content = _write_csv(csv_path)
    first_dir = create_analysis_run(csv_path, tmp_path / "first")
    second_dir = create_analysis_run(csv_path, tmp_path / "second")

    assert {path.name for path in first_dir.iterdir()} == {
        "manifest.json",
        "report.md",
        "summary.json",
    }
    summary = json.loads((first_dir / "summary.json").read_text(encoding="utf-8"))
    manifest = json.loads((first_dir / "manifest.json").read_text(encoding="utf-8"))
    expected_hash = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    assert summary["total_trades"] == 3
    assert summary["total_pnl"] == 25.0
    assert summary["win_rate"] == pytest.approx(1 / 3)
    assert summary["average_trade"] == pytest.approx(25 / 3)
    assert summary["largest_gain"] == 100.0
    assert summary["largest_loss"] == -50.0
    assert summary["max_consecutive_losses"] == 2
    assert summary["average_mae"] == pytest.approx(-140 / 3)
    assert summary["average_mfe"] == pytest.approx(135 / 3)
    assert manifest["input_sha256"] == expected_hash
    assert manifest["run_id"] == f"analysis-{expected_hash[:12]}"
    assert manifest["generated_files"] == ["manifest.json", "report.md", "summary.json"]
    for filename in ("report.md", "summary.json", "manifest.json"):
        first = (first_dir / filename).read_text(encoding="utf-8")
        second = (second_dir / filename).read_text(encoding="utf-8")
        assert first == second
        assert str(csv_path.resolve()) not in first
        assert "\\Users\\" not in first
    assert content not in (first_dir / "manifest.json").read_text(encoding="utf-8")


def test_create_analysis_run_refuses_existing_directory_without_changing_it(tmp_path) -> None:
    csv_path = tmp_path / "trades.csv"
    _write_csv(csv_path)
    output_dir = tmp_path / "bundle"
    output_dir.mkdir()
    marker = output_dir / "keep.txt"
    marker.write_text("unchanged", encoding="utf-8")

    with pytest.raises(AnalysisRunError, match="already exists"):
        create_analysis_run(csv_path, output_dir)

    assert marker.read_text(encoding="utf-8") == "unchanged"


def test_create_analysis_run_invalid_csv_leaves_no_final_or_temporary_directory(tmp_path) -> None:
    csv_path = tmp_path / "invalid.csv"
    csv_path.write_text("Instrument,Qty\nNQ,1\n", encoding="utf-8")
    output_dir = tmp_path / "bundle"

    with pytest.raises(AnalysisRunError, match="Missing required"):
        create_analysis_run(csv_path, output_dir)

    assert not output_dir.exists()
    assert not list(tmp_path.glob(".bundle.tmp-*"))
