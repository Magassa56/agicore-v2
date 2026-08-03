"""Deterministic offline resampling of explicit one-minute OHLCV CSV data."""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path

from .local_bundle import sha256_file


class OHLCVResamplerError(ValueError):
    """Raised for invalid input or unsafe local output."""


def resample_ohlcv(input_path: str | Path, output_path: str | Path, minutes: int) -> Path:
    """Write complete, aligned OHLCV buckets and a deterministic manifest."""
    if minutes not in (5, 15, 30):
        raise OHLCVResamplerError("minutes must be one of: 5, 15, 30")
    source, output = Path(input_path).resolve(), Path(output_path).resolve()
    manifest = output.with_name(f"{output.name}.manifest.json")
    if not source.is_file():
        raise OHLCVResamplerError(f"OHLCV CSV file not found: {source}")
    if output.exists() or manifest.exists():
        raise OHLCVResamplerError(f"Output already exists: {output}")
    bars = _read(source)
    groups: dict[datetime, list[tuple[datetime, float, float, float, float, float]]] = {}
    for bar in bars:
        stamp = bar[0].replace(minute=bar[0].minute - bar[0].minute % minutes, second=0, microsecond=0)
        groups.setdefault(stamp, []).append(bar)
    complete, dropped = [], 0
    for stamp, group in sorted(groups.items()):
        if len(group) == minutes and all(bar[0] == stamp.replace(minute=stamp.minute + index) for index, bar in enumerate(group)):
            complete.append((stamp, group[0][1], max(x[2] for x in group), min(x[3] for x in group), group[-1][4], sum(x[5] for x in group)))
        else:
            dropped += 1
    if not complete:
        raise OHLCVResamplerError("No complete OHLCV bucket could be produced")
    csv_text = "timestamp;open;high;low;close;volume\n" + "\n".join(f"{b[0].isoformat(sep=' ')};{b[1]};{b[2]};{b[3]};{b[4]};{b[5]}" for b in complete) + "\n"
    digest = sha256_file(source)
    run = hashlib.sha256(f"{digest}:{minutes}".encode()).hexdigest()
    data = {"schema_version":"1.0","input_filename":source.name,"input_sha256":digest,"output_filename":output.name,"timeframe_minutes":minutes,"input_bar_count":len(bars),"output_bar_count":len(complete),"dropped_incomplete_bucket_count":dropped,"first_output_timestamp":complete[0][0].isoformat(),"last_output_timestamp":complete[-1][0].isoformat(),"run_id":f"ohlcv-resample-{digest[:12]}-{run[:8]}","warnings":["input timestamps are interpreted exactly as supplied","incomplete buckets are dropped without interpolation"]}
    output.parent.mkdir(parents=True, exist_ok=True)
    temp_output, temp_manifest = output.with_name(f".{output.name}.tmp"), manifest.with_name(f".{manifest.name}.tmp")
    try:
        temp_output.write_text(csv_text, encoding="utf-8", newline="\n")
        temp_manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)+"\n", encoding="utf-8", newline="\n")
        if output.exists() or manifest.exists():
            raise OHLCVResamplerError(f"Output already exists: {output}")
        temp_output.rename(output); temp_manifest.rename(manifest)
    except Exception:
        for path in (temp_output, temp_manifest):
            if path.exists(): path.unlink()
        if output.exists() and not manifest.exists(): output.unlink()
        raise
    return output


def _read(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        sample = handle.read(4096)
        handle.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t") if sample else csv.excel
        except csv.Error:
            dialect = csv.excel
        reader = csv.DictReader(handle, dialect=dialect)
        fields = {name.strip().lower(): name for name in reader.fieldnames or []}
        required = ("timestamp", "open", "high", "low", "close", "volume")
        if any(name not in fields for name in required): raise OHLCVResamplerError("OHLCV CSV missing required columns")
        bars=[]
        for number,row in enumerate(reader,2):
            try: bars.append((datetime.fromisoformat(row[fields['timestamp']].replace('Z','+00:00')),*[float(row[fields[name]]) for name in required[1:]]))
            except (ValueError,TypeError): raise OHLCVResamplerError(f"Invalid OHLCV value on CSV row {number}")
    if not bars: raise OHLCVResamplerError("OHLCV CSV contains no bars")
    for first, second in zip(bars,bars[1:]):
        if second[0] == first[0]: raise OHLCVResamplerError("OHLCV CSV contains duplicate timestamps")
        if second[0] < first[0]: raise OHLCVResamplerError("OHLCV timestamps must be strictly increasing")
    return bars


__all__ = ["OHLCVResamplerError", "resample_ohlcv"]
