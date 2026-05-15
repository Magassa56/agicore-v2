"""Pytest-wide test harness settings."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path


_PYTEST_TMP_ROOT = Path(__file__).resolve().parents[1] / "tmp" / "pytest"
_PYTEST_TMP_ROOT.mkdir(parents=True, exist_ok=True)

for _key in ("TMPDIR", "TEMP", "TMP"):
    os.environ[_key] = str(_PYTEST_TMP_ROOT)

tempfile.tempdir = str(_PYTEST_TMP_ROOT)
