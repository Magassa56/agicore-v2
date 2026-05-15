"""SnapshotStore — JSON-backed snapshot persistence layer (Phase 8E).

Each SnapshotRecord is stored as an individual JSON file named by its
sequence number, making point-in-time retrieval O(n) and load-latest O(1).

Thread-safety: all operations are protected by a single RLock.
"""
from __future__ import annotations

import dataclasses
import json
import threading
from pathlib import Path

from .models import SnapshotRecord


class SnapshotStore:
    """Persist and retrieve SnapshotRecord objects to/from a directory.

    Parameters
    ----------
    directory:
        Path to the directory where snapshot JSON files are stored.
        Created automatically if it does not exist.
    """

    _FILE_PREFIX = "snapshot_"
    _FILE_SUFFIX = ".json"

    def __init__(self, directory: Path) -> None:
        self._dir = Path(directory)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

    # ---------------------------------------------------------------- write

    def save(self, record: SnapshotRecord) -> None:
        """Persist *record* to disk.

        Overwrites any existing file with the same sequence number.
        """
        path = self._path_for(record.sequence)
        payload = json.dumps(dataclasses.asdict(record), indent=2)
        with self._lock:
            path.write_text(payload, encoding="utf-8")

    # ---------------------------------------------------------------- read

    def load_latest(self) -> SnapshotRecord | None:
        """Return the record with the highest sequence, or *None* if empty."""
        with self._lock:
            files = self._sorted_files()
            if not files:
                return None
            return self._load_file(files[-1])

    def load_at_or_before(self, sequence: int) -> SnapshotRecord | None:
        """Return the record with the highest sequence ≤ *sequence*, or *None*."""
        with self._lock:
            candidates = [
                f for f in self._sorted_files()
                if self._seq_from_path(f) <= sequence
            ]
            if not candidates:
                return None
            return self._load_file(candidates[-1])

    def list_all(self) -> list[SnapshotRecord]:
        """Return all stored records sorted by ascending sequence."""
        with self._lock:
            return [self._load_file(f) for f in self._sorted_files()]

    # ---------------------------------------------------------------- internals

    def _path_for(self, sequence: int) -> Path:
        name = f"{self._FILE_PREFIX}{sequence:010d}{self._FILE_SUFFIX}"
        return self._dir / name

    def _sorted_files(self) -> list[Path]:
        """Return snapshot files sorted by sequence (ascending)."""
        files = list(self._dir.glob(f"{self._FILE_PREFIX}*{self._FILE_SUFFIX}"))
        return sorted(files, key=lambda p: self._seq_from_path(p))

    @staticmethod
    def _seq_from_path(path: Path) -> int:
        stem = path.stem  # e.g. "snapshot_0000000100"
        return int(stem.split("_", 1)[1])

    @staticmethod
    def _load_file(path: Path) -> SnapshotRecord:
        data = json.loads(path.read_text(encoding="utf-8"))
        return SnapshotRecord(**data)


__all__ = ["SnapshotStore"]
