"""Versioned segmentation around the unchanged historical shard codec."""

from __future__ import annotations

import hashlib
from pathlib import Path

from .ema_pullback_v2_g2b_contract import MAX_LOGICAL_BYTES
from .ema_pullback_v2_storage_format import MAX_NATIVE_BYTES, require, sha


def encode_segments(raw: bytes, stream_id: str, directory: Path, profile: dict) -> dict:
    """Store exact bytes using historical 16 MiB streams as ordered segments."""
    from .ema_pullback_v2_recovery_storage import encode_stream

    require(type(raw) is bytes and 0 < len(raw) <= MAX_LOGICAL_BYTES, "G2B logical size")
    segments = []
    for offset in range(0, len(raw), MAX_NATIVE_BYTES):
        part = raw[offset : offset + MAX_NATIVE_BYTES]
        segments.append(encode_stream(part, stream_id, directory, profile))
    return {
        "stream_id": stream_id,
        "logical_size_bytes": len(raw),
        "logical_sha256": sha(raw),
        "segments": segments,
    }


def decode_segments(stream: dict, directory: Path, profile: dict) -> bytes:
    """Verify every segment and return the exact bounded logical stream."""
    from .ema_pullback_v2_recovery_storage_verifier import decode_stream

    require(
        type(stream) is dict
        and set(stream) == {"stream_id", "logical_size_bytes", "logical_sha256", "segments"},
        "G2B stream descriptor",
    )
    total = stream["logical_size_bytes"]
    require(type(total) is int and 0 < total <= MAX_LOGICAL_BYTES, "G2B logical size")
    segments = stream["segments"]
    require(
        type(segments) is list
        and len(segments) == (total + MAX_NATIVE_BYTES - 1) // MAX_NATIVE_BYTES,
        "G2B segment count",
    )
    out = []
    digest = hashlib.sha256()
    for index, segment in enumerate(segments):
        expected = min(MAX_NATIVE_BYTES, total - index * MAX_NATIVE_BYTES)
        require(
            segment["stream_id"] == stream["stream_id"]
            and segment["uncompressed_size_bytes"] == expected,
            "G2B segment order/size",
        )
        for part in decode_stream(segment, directory, profile):
            out.append(part)
            digest.update(part)
    raw = b"".join(out)
    require(len(raw) == total and digest.hexdigest() == stream["logical_sha256"], "G2B stream SHA")
    return raw
