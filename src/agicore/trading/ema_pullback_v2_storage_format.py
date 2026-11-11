"""Exact bounded storage primitives, with incremental UTF-8/JSON token parsing.

The parsed object is deliberately bounded to small proof fixtures. No claim of
constant-memory native auditing or 89,841-observation feasibility is made.
"""

from __future__ import annotations

import codecs
import hashlib
import importlib.util
import json
import math
import os
import platform
import stat
import sys
import zlib
from pathlib import Path

CHUNK_SIZE = 1_048_576
MAX_NATIVE_BYTES = 16_777_216
MAX_OBSERVATIONS = 200
ROOT = Path(__file__).resolve().parents[3]
ADDENDUM_SHA = "9f0752d90f8cec746addcb97ded86664f9739e727951d47d9a04eeb29243b019"
PROTOCOL_SHA = "68dc6e6409aea4efb88e4a19e09a7ba17a68043a79f14ec23e569d3353267402"
REAL_RAW_SHA = "ee6eeed4871947b1fabe3c85bf4b5b319dc0d68e86edec7d2000815e22b2a126"


class StorageProofError(ValueError):
    """Incomplete, corrupted, out-of-scope or unbound evidence is never authoritative."""


def require(condition: bool, message: str) -> None:
    """Fail closed without repair, fallback or strategy execution."""
    if not condition:
        raise StorageProofError(message + ": FAIL_CLOSED")


def sha(raw: bytes) -> str:
    """SHA-256 of exactly the supplied bytes."""
    return hashlib.sha256(raw).hexdigest()


def integer_text(value: int) -> str:
    """Exact decimal spelling without changing Python's global digit limit."""
    tail = []
    rest = abs(value)
    while rest >= 1_000_000_000:
        rest, digit = divmod(rest, 1_000_000_000)
        tail.append(f"{digit:09d}")
    return ("-" if value < 0 else "") + str(rest) + "".join(reversed(tail))


def canonical_parts(value: object):
    """Emit sorted compact exact JSON tokens; never coerce or round numbers."""
    if type(value) is dict:
        require(all(type(k) is str for k in value), "string keys required")
        yield b"{"
        for index, key in enumerate(sorted(value)):
            if index:
                yield b","
            yield json.dumps(key, ensure_ascii=False).encode()
            yield b":"
            yield from canonical_parts(value[key])
        yield b"}"
    elif type(value) is list:
        yield b"["
        for index, child in enumerate(value):
            if index:
                yield b","
            yield from canonical_parts(child)
        yield b"]"
    elif type(value) is int:
        yield integer_text(value).encode()
    else:
        require(value is None or type(value) in (str, bool), "float/unsupported type")
        yield json.dumps(value, ensure_ascii=False, allow_nan=False).encode()


def canonical(value: object) -> bytes:
    """Bounded-fixture canonical bytes with exactly one final LF."""
    return b"".join(canonical_parts(value)) + b"\n"


class _Parser:
    def __init__(self, chunks, limit):
        self.digest = hashlib.sha256()
        self.size = 0
        self.limit = limit
        self.chunks = iter(codecs.iterdecode(self._bounded(chunks), "utf-8", errors="strict"))
        self.buffer = ""
        self.cursor = 0

    def _bounded(self, chunks):
        for chunk in chunks:
            require(type(chunk) is bytes, "byte stream required")
            self.size += len(chunk)
            require(self.size <= self.limit, "decoded stream over limit")
            self.digest.update(chunk)
            yield chunk

    def peek(self):
        while self.cursor == len(self.buffer):
            try:
                self.buffer = next(self.chunks)
            except StopIteration:
                return ""
            self.cursor = 0
        return self.buffer[self.cursor]

    def take(self):
        char = self.peek()
        require(bool(char), "truncated JSON token")
        self.cursor += 1
        return char

    def expect(self, char):
        require(self.take() == char, "noncanonical JSON delimiter")

    def string(self):
        self.expect('"')
        text = ['"']
        escaped = False
        while True:
            char = self.take()
            text.append(char)
            if char == '"' and not escaped:
                break
            escaped = char == "\\" and not escaped
        token = "".join(text)
        value = json.loads(token)
        require(json.dumps(value, ensure_ascii=False) == token, "noncanonical string spelling")
        return value

    def value(self, depth=0):
        require(depth < 128, "JSON nesting limit")
        char = self.peek()
        if char == '"':
            return self.string()
        if char == "{":
            self.take()
            value = {}
            previous = None
            if self.peek() != "}":
                while True:
                    key = self.string()
                    require(previous is None or key > previous, "duplicate/unsorted JSON key")
                    previous = key
                    self.expect(":")
                    value[key] = self.value(depth + 1)
                    if self.peek() != ",":
                        break
                    self.take()
            self.expect("}")
            return value
        if char == "[":
            self.take()
            value = []
            if self.peek() != "]":
                while True:
                    value.append(self.value(depth + 1))
                    if self.peek() != ",":
                        break
                    self.take()
            self.expect("]")
            return value
        for token, value in (("null", None), ("true", True), ("false", False)):
            if char == token[0]:
                for item in token:
                    self.expect(item)
                return value
        require(char in "-0123456789" and bool(char), "invalid/float JSON token")
        negative = char == "-"
        if negative:
            self.take()
        digits = []
        while self.peek() and self.peek() in "0123456789":
            digits.append(self.take())
        require(bool(digits) and (len(digits) == 1 or digits[0] != "0"), "integer spelling")
        require(not (negative and digits == ["0"]), "negative zero")
        number = 0
        for start in range(0, len(digits), 9):
            block = "".join(digits[start : start + 9])
            number = number * 10 ** len(block) + int(block)
        return -number if negative else number


def _resolve_schema(schema: dict, root: dict) -> dict:
    """Resolve bounded local JSON-schema references without guessing semantic types."""
    seen = set()
    while "$ref" in schema:
        reference = schema["$ref"]
        require(
            type(reference) is str and reference.startswith("#/") and reference not in seen,
            "schema reference",
        )
        seen.add(reference)
        target = root
        for token in reference[2:].split("/"):
            key = token.replace("~1", "/").replace("~0", "~")
            require(type(target) is dict and key in target, "schema reference target")
            target = target[key]
        require(type(target) is dict, "schema reference object")
        schema = target
    return schema


def _schema_type_matches(value: object, schema: dict, root: dict) -> bool:
    """Select an anyOf branch by exact JSON type before semantic validation."""
    schema = _resolve_schema(schema, root)
    kind = schema.get("type")
    if kind is None:
        return True
    expected = {
        "object": dict,
        "array": list,
        "integer": int,
        "string": str,
        "boolean": bool,
        "null": type(None),
    }.get(kind)
    require(expected is not None, "supported schema type")
    return type(value) is expected


def _validate_rational_contracts(value: object, schema: dict, root: dict, depth: int = 0) -> None:
    """Validate rationals only where the applicable frozen schema declares one."""
    require(depth < 128 and type(schema) is dict and type(root) is dict, "schema depth/type")
    resolved = _resolve_schema(schema, root)
    rational_schema = root.get("$defs", {}).get("rational")
    if type(rational_schema) is dict and resolved is rational_schema:
        require(
            type(value) is dict and set(value) == {"numerator", "denominator"},
            "rational shape",
        )
        numerator, denominator = value["numerator"], value["denominator"]
        require(
            type(numerator) is type(denominator) is int
            and denominator > 0
            and math.gcd(numerator, denominator) == 1,
            "noncanonical rational",
        )
        return
    if "anyOf" in resolved:
        branches = [
            option
            for option in resolved["anyOf"]
            if type(option) is dict and _schema_type_matches(value, option, root)
        ]
        require(bool(branches), "schema anyOf branch")
        failures = []
        for option in branches:
            try:
                _validate_rational_contracts(value, option, root, depth + 1)
                return
            except StorageProofError as exc:
                failures.append(exc)
        raise failures[0]
    if type(value) is dict and resolved.get("type") == "object":
        properties = resolved.get("properties", {})
        require(type(properties) is dict, "schema properties")
        for key in value.keys() & properties.keys():
            _validate_rational_contracts(value[key], properties[key], root, depth + 1)
    elif type(value) is list and resolved.get("type") == "array":
        item_schema = resolved.get("items")
        if item_schema is not None:
            require(type(item_schema) is dict, "schema items")
            for child in value:
                _validate_rational_contracts(child, item_schema, root, depth + 1)


def parse_canonical(chunks, *, limit: int = MAX_NATIVE_BYTES, schema: dict | None = None):
    """Parse exact canonical JSON and optionally enforce schema-declared rationals."""
    try:
        parser = _Parser(chunks, limit)
        result = parser.value()
        parser.expect("\n")
        require(not parser.peek(), "trailing JSON bytes")
        if schema is not None:
            _validate_rational_contracts(result, schema, schema)
        digest = hashlib.sha256()
        for chunk in canonical_parts(result):
            digest.update(chunk)
        digest.update(b"\n")
        require(digest.digest() == parser.digest.digest(), "noncanonical JSON")
        return result
    except StorageProofError:
        raise
    except (UnicodeError, ValueError, TypeError, RecursionError) as exc:
        raise StorageProofError("invalid exact JSON: FAIL_CLOSED") from exc


def codec_profile() -> dict:
    """Bind the actual codec binary/runtime; this is not a cross-version guarantee."""
    executable = sha(Path(sys.executable).read_bytes())
    return {
        "profile_id": "EXACT_NATIVE_BYTE_SHARDS_DEFLATE_V1",
        "algorithm": "RAW_DEFLATE",
        "level": 9,
        "window_bits": -15,
        "memory_level": 8,
        "strategy": "Z_DEFAULT_STRATEGY",
        "fallback": "IDENTITY_IF_COMPRESSED_LENGTH_GREATER_THAN_OR_EQUAL_TO_UNCOMPRESSED_LENGTH",
        "chunk_size": CHUNK_SIZE,
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "python_executable_sha256": executable,
        "zlib_compile_version": zlib.ZLIB_VERSION,
        "zlib_runtime_version": zlib.ZLIB_RUNTIME_VERSION,
        "zlib_module_origin": importlib.util.find_spec("zlib").origin,
        "zlib_binary_sha256": sha(Path(zlib.__file__).read_bytes())
        if getattr(zlib, "__file__", None)
        else executable,
    }


def contracts() -> tuple[dict, dict]:
    """Read only frozen documentary metadata, never market data."""
    result = []
    for name, digest in (
        ("EMA_PULLBACK_V2_RECOVERY_EVIDENCE_STORAGE_ADDENDUM_V1", ADDENDUM_SHA),
        ("EMA_PULLBACK_V2_DEVELOPMENT_PROTOCOL", PROTOCOL_SHA),
    ):
        raw = (ROOT / "docs/evidence" / (name + ".json")).read_bytes()
        require(sha(raw) == digest, "frozen authority changed")
        result.append(parse_canonical([raw]))
    return tuple(result)


def regular_read(path: Path, limit=MAX_NATIVE_BYTES) -> bytes:
    """Reject aliases and nonregular objects before bounded reads."""
    for parent in (path, *path.parents):
        require(not parent.is_symlink(), "symlink evidence path")
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as handle:
        info = os.fstat(handle.fileno())
        require(
            stat.S_ISREG(info.st_mode) and info.st_nlink == 1, "regular nonaliased file required"
        )
        require(info.st_size <= limit, "evidence file over limit")
        raw = handle.read(limit + 1)
        require(len(raw) == info.st_size, "evidence changed during read")
        return raw


def immutable_write(path: Path, raw: bytes) -> None:
    """Exclusive durable write; existing bytes and incomplete evidence are preserved."""
    require(not path.exists() and not path.is_symlink(), "evidence overwrite forbidden")
    for parent in path.parents:
        require(not parent.is_symlink(), "symlink output parent")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def array_counts(value, path="") -> dict:
    """Count every ordered native array path, including repeated nested provenance."""
    result = {}
    if type(value) is list:
        result[path] = len(value)
        for index, child in enumerate(value):
            result.update(array_counts(child, path + "/" + str(index)))
    elif type(value) is dict:
        for key, child in value.items():
            key = key.replace("~", "~0").replace("/", "~1")
            result.update(array_counts(child, path + "/" + key))
    return result
