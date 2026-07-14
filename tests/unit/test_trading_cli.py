"""Unit tests for the local trading CLI."""
from __future__ import annotations

import pytest

from agicore.cli.main import main


def test_trading_analyze_help_returns_zero(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["trading", "analyze", "--help"])

    assert exc.value.code == 0
    assert "usage: agicore trading analyze" in capsys.readouterr().out


def test_trading_analyze_valid_csv_writes_deterministic_report(
    tmp_path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)
    csv_path = tmp_path / "trades_juillet.csv"
    csv_path.write_text(
        "\n".join(
            [
                "Entry time,Exit time,Instrument,Qty,Entry price,Exit price,Profit,MAE,MFE",
                "2026-07-01 09:30:00,2026-07-01 09:35:00,NQ 09-26,2,18000,18020,100,-40,160",
                "2026-07-01 10:00:00,2026-07-01 10:02:00,NQ 09-26,1,18010,18000,(50),-60,20",
            ]
        ),
        encoding="utf-8",
    )

    code = main(["trading", "analyze", str(csv_path)])

    output_path = tmp_path / "reports" / "local" / "trades_juillet-analysis.md"
    assert code == 0
    assert output_path.exists()
    first_report = output_path.read_text(encoding="utf-8")
    assert "- Total trades: 2" in first_report
    assert "- Total PnL: 50.00" in first_report
    assert "- Win rate: 50.00%" in first_report
    assert "bama" not in first_report.lower()
    first_output = capsys.readouterr().out
    assert "reports" in first_output
    assert "trades_juillet-analysis.md" in first_output

    code = main(["trading", "analyze", str(csv_path)])

    assert code == 0
    assert output_path.read_text(encoding="utf-8") == first_report


def test_trading_analyze_missing_file_returns_two_without_report(
    tmp_path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)
    output_path = tmp_path / "report.md"

    code = main(
        ["trading", "analyze", str(tmp_path / "missing.csv"), "--output", str(output_path)]
    )

    captured = capsys.readouterr()
    assert code == 2
    assert "not found" in captured.err
    assert not output_path.exists()


def test_trading_analyze_invalid_csv_does_not_use_data_directory(
    tmp_path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "valid.csv").write_text(
        "Entry time,Exit time,Profit\n"
        "2026-07-01 09:30:00,2026-07-01 09:31:00,10\n",
        encoding="utf-8",
    )
    invalid_csv = tmp_path / "invalid.csv"
    invalid_csv.write_text("Instrument,Qty\nNQ,1\n", encoding="utf-8")
    output_path = tmp_path / "report.md"

    code = main(["trading", "analyze", str(invalid_csv), "--output", str(output_path)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Missing required" in captured.err
    assert not output_path.exists()
    assert not (tmp_path / "reports").exists()
