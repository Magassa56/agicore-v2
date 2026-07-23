"""Small deterministic helpers for publishing local analysis bundles."""
from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Mapping


class LocalBundleError(ValueError):
    """Raised when a local bundle cannot be safely published."""


def sha256_file(path: str | Path) -> str:
    """Return the SHA-256 hash of a file read in bounded blocks."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def deterministic_json(value: object) -> str:
    """Serialize JSON deterministically as UTF-8 compatible text."""
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def publish_local_bundle(output_dir: str | Path, files: Mapping[str, str]) -> Path:
    """Atomically publish named text files to a new local directory."""
    _validate_filenames(files)
    final_dir = Path(output_dir).resolve()
    if final_dir.exists():
        raise LocalBundleError(f"Output directory already exists: {final_dir}")

    temp_dir: Path | None = None
    try:
        final_dir.parent.mkdir(parents=True, exist_ok=True)
        if final_dir.exists():
            raise LocalBundleError(f"Output directory already exists: {final_dir}")
        temp_dir = Path(
            tempfile.mkdtemp(prefix=f".{final_dir.name}.tmp-", dir=final_dir.parent)
        )
        for name, content in files.items():
            (temp_dir / name).write_text(content, encoding="utf-8", newline="\n")
        if final_dir.exists():
            raise LocalBundleError(f"Output directory already exists: {final_dir}")
        temp_dir.rename(final_dir)
        return final_dir
    except LocalBundleError:
        raise
    except OSError as exc:
        raise LocalBundleError(f"Unable to publish local bundle: {exc}") from exc
    finally:
        if temp_dir is not None and temp_dir.exists():
            shutil.rmtree(temp_dir)


def _validate_filenames(files: Mapping[str, str]) -> None:
    for name in files:
        posix = PurePosixPath(name)
        windows = PureWindowsPath(name)
        if (
            not name
            or posix.is_absolute()
            or windows.is_absolute()
            or windows.drive
            or len(posix.parts) != 1
            or len(windows.parts) != 1
            or ".." in posix.parts
            or ".." in windows.parts
        ):
            raise LocalBundleError(f"Unsafe bundle filename: {name!r}")


__all__ = ["LocalBundleError", "deterministic_json", "publish_local_bundle", "sha256_file"]
