"""Unit tests for NinjaTrader CSV import."""
from __future__ import annotations

from datetime import datetime

import pytest

from agicore.trading.import_nt8_csv import import_nt8_csv


def test_import_nt8_csv_normalizes_common_columns(tmp_path) -> None:
    path = tmp_path / "nt8.csv"
    path.write_text(
        "\n".join(
            [
                "Entry time,Exit time,Instrument,Qty,Entry price,Exit price,Profit,MAE,MFE",
                "2026-05-01 09:30:00,2026-05-01 09:35:00,NQ 06-26,2,18000,18020,100,-40,160",
                "2026-05-01 10:00:00,2026-05-01 10:02:00,NQ 06-26,1,18010,18000,(50),-60,20",
            ]
        ),
        encoding="utf-8",
    )

    trades = import_nt8_csv(path)

    assert len(trades) == 2
    assert trades[0].entry_time == datetime(2026, 5, 1, 9, 30)
    assert trades[0].exit_time == datetime(2026, 5, 1, 9, 35)
    assert trades[0].instrument == "NQ 06-26"
    assert trades[0].quantity == 2.0
    assert trades[0].pnl == 100.0
    assert trades[0].mae == -40.0
    assert trades[0].mfe == 160.0
    assert trades[1].pnl == -50.0


def test_import_nt8_csv_accepts_semicolon_and_aliases(tmp_path) -> None:
    path = tmp_path / "nt8_aliases.csv"
    path.write_text(
        "Time;Symbol;Contracts;P&L\n"
        "05/01/2026 09:30;MNQ 06-26;1;$25.50\n",
        encoding="utf-8",
    )

    trades = import_nt8_csv(path)

    assert len(trades) == 1
    assert trades[0].exit_time == trades[0].entry_time
    assert trades[0].pnl == 25.50
    assert trades[0].quantity == 1.0


def test_import_nt8_csv_requires_datetime_and_pnl(tmp_path) -> None:
    path = tmp_path / "invalid.csv"
    path.write_text("Instrument,Qty\nNQ,1\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Missing required"):
        import_nt8_csv(path)
