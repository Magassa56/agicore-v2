"""Retain bounded synthetic evidence; never replay, repair or infer missing bundles."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import stat
import zipfile
from pathlib import Path

MiB = 1 << 20
MEMBERS_BYTES = 8 * MiB
INDEX_BYTES = MiB
LOG_BYTES = 10 * MiB
INDEX = "RETENTION_INDEX.json"
REPORTS = ("preflight.json", "tier_report.json")


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def retain(root: Path, archive: Path) -> dict:
    """Bound payload, member headers and omission index *before* writing a fresh ZIP."""
    root, archive = root.absolute(), archive.absolute()
    if (
        "data" in root.parts
        or archive.parent != root.parent
        or archive == root
        or any(p.is_symlink() for p in (root, *root.parents))
        or not root.is_dir()
    ):
        raise ValueError("invalid synthetic retention path")
    paths = []
    for directory, dirs, files in os.walk(root, followlinks=False, onerror=_raise):
        for name in (*dirs, *files):
            path = Path(directory) / name
            if name == "data" or path.is_symlink():
                raise ValueError("invalid evidence path")
        paths.extend(Path(directory) / name for name in files)
    paths.sort(
        key=lambda p: (
            p.relative_to(root).as_posix() not in REPORTS,
            p.suffix == ".blob",
            p.as_posix(),
        )
    )
    remaining, index_room = MEMBERS_BYTES, INDEX_BYTES - 512
    omitted, count, commitment = [], 0, hashlib.sha256()
    physical = 0
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_STORED, allowZip64=False) as out:
        for path in paths:
            relative = path.relative_to(root)
            name = relative.as_posix()
            if name == INDEX:
                raise ValueError("reserved retention index name")
            with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), "rb") as f:
                info = os.fstat(f.fileno())
                if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                    raise ValueError("nonregular or aliased evidence")
                size = info.st_size
                physical += info.st_blocks * 512
                # ZIP_STORED + seekable output: local header 30, central header 46,
                # name twice. With a bounded selection there is no ZIP64 or descriptor.
                cost = size + 76 + 2 * len(name.encode("utf-8"))
                duplicate = "bundle" in relative.parts and relative.parts[0].endswith("-2")
                if not duplicate and cost <= remaining and len(out.filelist) < 16000:
                    content = f.read(size + 1)
                    if len(content) != size:
                        raise ValueError("evidence changed")
                    out.writestr(zipfile.ZipInfo(name), content)
                    remaining -= cost
                    if name in REPORTS and size <= 2 * MiB:
                        print(
                            "G2C_FILE_"
                            + name.replace(".", "_").upper()
                            + "="
                            + content.decode("utf-8").strip()
                        )
                    continue
                digest = hashlib.file_digest(f, "sha256").hexdigest()
                entry = {
                    "path": name,
                    "bytes": size,
                    "sha256": digest,
                    "reason": "duplicate_bundle_policy" if duplicate else "retention_budget",
                }
                line = _json(entry) + b"\n"
                commitment.update(line)
                count += 1
                if len(line) <= index_room:
                    omitted.append(entry)
                    index_room -= len(line)
        index = {
            "status": "PARTIAL" if count else "COMPLETE_SELECTED",
            "omitted": omitted,
            "omitted_count": count,
            "omitted_index_complete": count == len(omitted),
            "omitted_records_sha256": commitment.hexdigest(),
        }
        raw = _json(index)
        if len(raw) > INDEX_BYTES:
            raise ValueError("retention index exceeds reserved space")
        out.writestr(zipfile.ZipInfo(INDEX), raw)
    size = archive.stat().st_size
    if size > LOG_BYTES or physical + archive.stat().st_blocks * 512 > 1024 * MiB:
        raise ValueError("retention size or aggregate physical limit exceeded")
    return {
        "status": index["status"],
        "bytes": size,
        "omitted_count": count,
        "aggregate_physical_bytes": physical + archive.stat().st_blocks * 512,
        "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
    }


def _raise(error):
    raise error


def main() -> None:
    """Export only the verified-size archive, using the historical GitHub log protocol."""
    root = Path(os.environ["G2C_OUTPUT"])
    if not root.exists() and not root.is_symlink():
        print("G2C_ARCHIVE_STATUS=NO_OUTPUT")
        return
    archive = root.parent / "agicore-g2c-5000-evidence.zip"
    result = retain(root, archive)
    print("G2C_ARCHIVE_INFO=" + _json(result).decode())
    encoded = base64.b64encode(archive.read_bytes()).decode("ascii")
    for i in range(0, len(encoded), 6000):
        print("G2C_ARCHIVE_PART=" + encoded[i : i + 6000])
    print("G2C_ARCHIVE_STATUS=" + result["status"] + "_EXPORTED_TO_LOG")


if __name__ == "__main__":
    main()
