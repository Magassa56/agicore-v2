"""The archive limit applies to ZIP bytes including names, headers and the omission index."""

import hashlib
import json
import random
import zipfile

import pytest

from tools import ema_pullback_v2_g2c_archive as archive


def test_actual_over_32_mib_retains_reports_and_hashes_the_omitted_body(tmp_path):
    root = tmp_path / "run"
    root.mkdir()
    report = b'{"status":"FAIL","reason":"CPU_LIMIT"}\n'
    (root / "tier_report.json").write_bytes(report)
    # An early-sorting non-blob must not starve the report. The large body is
    # independently hashed as incompressible invented bytes are generated.
    (root / "a.txt").write_bytes(b"z" * archive.MEMBERS_BYTES)
    random_bytes = random.Random(328)
    expected = hashlib.sha256()
    with (root / "dense.blob").open("xb") as f:
        for _ in range(33):
            block = random_bytes.randbytes(archive.MiB)
            expected.update(block)
            f.write(block)
    path = tmp_path / "out.zip"
    result = archive.retain(root, path)
    assert result["status"] == "PARTIAL" and result["omitted_count"] == 2
    assert path.stat().st_size == result["bytes"] <= archive.LOG_BYTES < 32 * archive.MiB
    with zipfile.ZipFile(path) as z:
        assert z.read("tier_report.json") == report
        assert "dense.blob" not in z.namelist()
        index = json.loads(z.read(archive.INDEX))
    assert index["omitted_index_complete"] is True
    assert index["omitted"][-1] == {
        "path": "dense.blob",
        "bytes": 33 * archive.MiB,
        "sha256": expected.hexdigest(),
        "reason": "retention_budget",
    }
    assert result["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    with pytest.raises(FileExistsError):
        archive.retain(root, path)


def test_excluded_duplicates_and_truncated_index_cannot_claim_complete(tmp_path, monkeypatch):
    monkeypatch.setattr(archive, "INDEX_BYTES", 780)
    root = tmp_path / "run"
    duplicate = root / "dense-2" / "bundle"
    duplicate.mkdir(parents=True)
    for i in range(10):
        (duplicate / str(i)).write_bytes(bytes([i]))
    for name in ("one.zip", "two.zip"):
        path = tmp_path / name
        result = archive.retain(root, path)
        with zipfile.ZipFile(path) as z:
            index = json.loads(z.read(archive.INDEX))
        assert result["status"] == "PARTIAL"
        assert index["omitted_count"] == 10 > len(index["omitted"])
        assert index["omitted_index_complete"] is False
    assert (tmp_path / "one.zip").read_bytes() == (tmp_path / "two.zip").read_bytes()


def test_archive_never_follows_alias_or_emits_success(tmp_path):
    root = tmp_path / "run"
    root.mkdir()
    (root / "link").symlink_to(tmp_path / "unread")
    with pytest.raises(ValueError, match="path"):
        archive.retain(root, tmp_path / "out.zip")
