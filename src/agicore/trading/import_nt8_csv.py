"""NinjaTrader 8 CSV import and normalization.

The importer is intentionally offline-only: it reads a local CSV export and
returns normalized trade records for later analysis.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class NormalizedTrade:
    """Canonical trade representation used by the trading analysis module."""

    entry_time: datetime
    exit_time: datetime
    pnl: float
    quantity: float | None = None
    instrument: str | None = None
    entry_price: float | None = None
    exit_price: float | None = None
    mae: float | None = None
    mfe: float | None = None


_COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "entry_time": (
        "entry time",
        "entrytime",
        "entry date",
        "entry datetime",
        "entry",
        "open time",
        "time",
    ),
    "exit_time": (
        "exit time",
        "exittime",
        "exit date",
        "exit datetime",
        "exit",
        "close time",
    ),
    "pnl": (
        "pnl",
        "p&l",
        "profit",
        "profit/loss",
        "realized pnl",
        "net profit",
        "pl",
    ),
    "quantity": ("quantity", "qty", "size", "contracts", "filled"),
    "instrument": ("instrument", "symbol", "market", "name"),
    "entry_price": ("entry price", "avg entry price", "entryprice", "open price"),
    "exit_price": ("exit price", "avg exit price", "exitprice", "close price"),
    "mae": ("mae", "max adverse excursion", "maximum adverse excursion"),
    "mfe": ("mfe", "max favorable excursion", "maximum favorable excursion"),
}


def import_nt8_csv(path: str | Path) -> list[NormalizedTrade]:
    """Read a NinjaTrader CSV export and return normalized trades.

    The CSV must contain at least a PnL column and one timestamp column. If an
    explicit exit timestamp is missing, the entry timestamp is reused.
    """
    csv_path = Path(path)
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        sample = handle.read(4096)
        handle.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t") if sample else csv.excel
        reader = csv.DictReader(handle, dialect=dialect)
        if not reader.fieldnames:
            return []

        column_map = _build_column_map(reader.fieldnames)
        _validate_required_columns(column_map)

        trades: list[NormalizedTrade] = []
        for row_number, row in enumerate(reader, start=2):
            if not any((value or "").strip() for value in row.values()):
                continue
            trades.append(_normalize_row(row, column_map, row_number=row_number))
        return trades


def _build_column_map(fieldnames: list[str]) -> dict[str, str]:
    normalized_to_original = {_normalize_column(name): name for name in fieldnames}
    column_map: dict[str, str] = {}
    for target, aliases in _COLUMN_ALIASES.items():
        for alias in aliases:
            found = normalized_to_original.get(_normalize_column(alias))
            if found is not None:
                column_map[target] = found
                break
    return column_map


def _validate_required_columns(column_map: dict[str, str]) -> None:
    missing = [name for name in ("entry_time", "pnl") if name not in column_map]
    if missing:
        raise ValueError(f"Missing required NT8 CSV column(s): {', '.join(missing)}")


def _normalize_row(
    row: dict[str, Any],
    column_map: dict[str, str],
    *,
    row_number: int,
) -> NormalizedTrade:
    entry_time = _parse_datetime(_get(row, column_map, "entry_time"), row_number=row_number)
    exit_value = _get(row, column_map, "exit_time")
    exit_time = _parse_datetime(exit_value, row_number=row_number) if exit_value else entry_time
    return NormalizedTrade(
        entry_time=entry_time,
        exit_time=exit_time,
        pnl=_parse_float(_get(row, column_map, "pnl"), "pnl", row_number=row_number),
        quantity=_parse_optional_float(_get(row, column_map, "quantity"), "quantity", row_number),
        instrument=_parse_optional_text(_get(row, column_map, "instrument")),
        entry_price=_parse_optional_float(
            _get(row, column_map, "entry_price"), "entry_price", row_number
        ),
        exit_price=_parse_optional_float(_get(row, column_map, "exit_price"), "exit_price", row_number),
        mae=_parse_optional_float(_get(row, column_map, "mae"), "mae", row_number),
        mfe=_parse_optional_float(_get(row, column_map, "mfe"), "mfe", row_number),
    )


def _get(row: dict[str, Any], column_map: dict[str, str], target: str) -> str | None:
    column = column_map.get(target)
    if column is None:
        return None
    value = row.get(column)
    return str(value).strip() if value is not None else None


def _parse_datetime(value: str | None, *, row_number: int) -> datetime:
    if not value:
        raise ValueError(f"Missing datetime on CSV row {row_number}")

    candidates = (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%Y-%m-%dT%H:%M:%S",
    )
    cleaned = value.strip()
    try:
        return datetime.fromisoformat(cleaned)
    except ValueError:
        pass

    for fmt in candidates:
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    raise ValueError(f"Invalid datetime {value!r} on CSV row {row_number}")


def _parse_float(value: str | None, field_name: str, *, row_number: int) -> float:
    if value is None or value == "":
        raise ValueError(f"Missing {field_name} on CSV row {row_number}")
    cleaned = value.strip().replace("$", "").replace(",", "").replace(" ", "")
    if cleaned.startswith("(") and cleaned.endswith(")"):
        cleaned = f"-{cleaned[1:-1]}"
    try:
        return float(cleaned)
    except ValueError as exc:
        raise ValueError(f"Invalid {field_name} {value!r} on CSV row {row_number}") from exc


def _parse_optional_float(value: str | None, field_name: str, row_number: int) -> float | None:
    if value is None or value == "":
        return None
    return _parse_float(value, field_name, row_number=row_number)


def _parse_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _normalize_column(name: str) -> str:
    return " ".join(name.strip().lower().replace("_", " ").split())


__all__ = ["NormalizedTrade", "import_nt8_csv"]
