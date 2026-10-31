"""Supervised bounded proof workers. This command has no real-data execution mode."""

from __future__ import annotations

import argparse
import copy
import os
import resource
import signal
import subprocess
import sys
import time
import traceback
import zlib
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path

from agicore.trading.ema_pullback_v2_recovery_storage import (
    encode_stream,
    produce_synthetic_bundle,
)
from agicore.trading.ema_pullback_v2_recovery_storage_verifier import (
    decode_stream,
    verify_synthetic_bundle,
)
from agicore.trading.ema_pullback_v2_storage_audit import (
    audit_native,
    native,
    screening_verdict,
    trade_statistics,
)
from agicore.trading.ema_pullback_v2_storage_format import (
    ROOT,
    StorageProofError,
    canonical,
    codec_profile,
    contracts,
    immutable_write,
    parse_canonical,
    require,
    sha,
)
from tests.unit.trading.v2_recovery_storage_fixtures import (
    BYTE_IDS,
    NATIVE_IDS,
    STATISTICS_CASES,
    TAMPER_IDS,
    synthetic_byte_stream,
    synthetic_raw,
)

FIXTURE_REGISTRATION = (
    ROOT / "docs/evidence/EMA_PULLBACK_V2_RECOVERY_STORAGE_FIXTURE_REGISTRATION_V1.json"
)
FIXTURE_SHA = "60038227f5b57bf777149fad00e37ce764fc77169c5d26443aeeda664b98a714"


def utc():
    """Operational receipt timestamp, never part of native result identity."""
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def footprint(directory):
    """All retained files and directory metadata; count logical or allocated max."""
    paths = [directory, *directory.rglob("*")]
    return sum(max(p.stat().st_size, p.stat().st_blocks * 512) for p in paths)


def verify_registration(path, *, formal):
    """Reject source drift before starting any proof worker."""
    source = parse_canonical([path.read_bytes()])
    require(sha(FIXTURE_REGISTRATION.read_bytes()) == FIXTURE_SHA, "fixture precommit changed")
    fixtures = parse_canonical([FIXTURE_REGISTRATION.read_bytes()])
    for entry in [
        fixtures["generator"],
        *fixtures["generator_dependencies"],
        *fixtures["reference_sources"],
        *source["complete_source_closure"]["files"],
    ]:
        require(
            sha((ROOT / entry["path"]).read_bytes()) == entry["sha256"],
            "registered executable source changed",
        )
    require(
        sha(canonical(source["complete_source_closure"]))
        == source["complete_source_closure_sha256"],
        "complete source closure",
    )
    require(
        sha(canonical(source["verifier_source_closure"]))
        == source["verifier_source_closure_sha256"],
        "verifier source closure",
    )
    if formal:
        require(codec_profile() == fixtures["codec_profile"], "formal codec host differs")
    return source, fixtures


def _reference(raw):
    from agicore.trading.ema_pullback_v2_development_replay import (
        evaluate_synthetic_development_replay_v2,
        read_frozen_replay_bindings_v2,
    )

    return evaluate_synthetic_development_replay_v2(
        raw, bindings=read_frozen_replay_bindings_v2()
    ).canonical_utf8


def native_case(directory, fixture, registration, profile):
    """Complete frozen native equality, source-derived audit and immutable sealing."""
    raw = synthetic_raw(fixture)
    immutable_write(directory / "synthetic-source.Last.txt", raw)
    start = time.perf_counter_ns()
    reference = _reference(raw)
    immutable_write(directory / "reference-native.json", reference)
    immutable_write(
        directory / "progress-01-reference.json",
        canonical({"utc": utc(), "phase": "REFERENCE_COMPLETE", "sha256": sha(reference)}),
    )
    reference_ns = time.perf_counter_ns() - start
    start = time.perf_counter_ns()
    receipt = produce_synthetic_bundle(
        native_bytes=reference,
        synthetic_raw=raw,
        directory=directory / "bundle",
        profile=profile,
        complete_source_sha=registration["complete_source_closure_sha256"],
        verifier_source_sha=registration["verifier_source_closure_sha256"],
    )
    producer_ns = time.perf_counter_ns() - start
    arguments = {
        "expected_manifest_sha": receipt["bundle_manifest_sha256"],
        "expected_bindings": receipt["bindings"],
        "expected_profile": profile,
        "expected_native_sha": sha(reference),
        "synthetic_raw": raw,
    }
    start = time.perf_counter_ns()
    decoded, audit = verify_synthetic_bundle(directory / "bundle", **arguments, seal=True)
    verification_ns = time.perf_counter_ns() - start
    require(decoded == reference and sha(decoded) == sha(reference), "exact native roundtrip")
    # Re-read the completed immutable artifact, including both receipts and its seal.
    again, _ = verify_synthetic_bundle(directory / "bundle", **arguments)
    require(again == reference, "completed-bundle independent retrieval")
    manifest = parse_canonical([(directory / "bundle/bundle-manifest.json").read_bytes()])
    start = time.perf_counter_ns()
    require(
        b"".join(decode_stream(manifest["streams"][0], directory / "bundle", profile)) == reference,
        "decoder exact bytes",
    )
    decoder_ns = time.perf_counter_ns() - start
    stored = sum(p.stat().st_size for p in (directory / "bundle/objects").rglob("*.blob"))
    return {
        "case_id": fixture,
        "kind": "NATIVE",
        "status": "PASS",
        "reference_native_sha256": sha(reference),
        "reconstructed_native_sha256": sha(decoded),
        "native_output_sha256": audit["native_output_sha256"],
        "bundle_manifest_sha256": receipt["bundle_manifest_sha256"],
        "exact_bytes": True,
        "logical_native_bytes": len(reference),
        "compressed_shard_bytes": stored,
        "manifest_bytes": (directory / "bundle/bundle-manifest.json").stat().st_size,
        "summary_bytes": (directory / "bundle/decision-summary.json").stat().st_size,
        "witness_logical_bytes": manifest["streams"][1]["uncompressed_size_bytes"],
        "temporary_bytes": 0,
        "reference_ns": reference_ns,
        "producer_ns": producer_ns,
        "decoder_ns": decoder_ns,
        "independent_verification_ns": verification_ns,
        "compression_ratio": native(
            Fraction(len(reference) + manifest["streams"][1]["uncompressed_size_bytes"], stored)
        ),
        "input_sha256": sha(raw),
        "observations": audit["audit"]["observation_count"],
    }


def byte_case(directory, fixture, profile):
    """Opaque boundary/entropy cases do not claim to be native trading results."""
    raw = synthetic_byte_stream(fixture)
    immutable_write(directory / "source-bytes.bin", raw)
    start = time.perf_counter_ns()
    stream = encode_stream(raw, "codec_only", directory, profile)
    producer_ns = time.perf_counter_ns() - start
    immutable_write(directory / "codec-stream.json", canonical(stream))
    start = time.perf_counter_ns()
    chunks = tuple(decode_stream(stream, directory, profile))
    decoded = b"".join(chunks)
    decoder_ns = time.perf_counter_ns() - start
    require(raw == decoded, "codec byte equality")
    if fixture in ("utf8_crossing", "integer_crossing"):
        parsed = parse_canonical(chunks)
        require(canonical(parsed) == raw, "split token parsing equality")
    if fixture == "incompressible":
        require(all(c["codec"] == "IDENTITY" for c in stream["chunks"]), "incompressible fallback")
    if fixture == "repeated_chunks":
        require(
            stream["chunks"][0]["object_identity"] == stream["chunks"][1]["object_identity"],
            "physical dedup retains ordinal multiplicity",
        )
    stored = sum(p.stat().st_size for p in (directory / "objects").rglob("*.blob"))
    return {
        "case_id": fixture,
        "kind": "CODEC_ONLY",
        "status": "PASS",
        "logical_bytes": len(raw),
        "source_sha256": sha(raw),
        "decoded_sha256": sha(decoded),
        "exact_bytes": True,
        "stored_bytes": stored,
        "producer_ns": producer_ns,
        "decoder_ns": decoder_ns,
        "compression_ratio": native(Fraction(len(raw), stored)),
        "temporary_bytes": 0,
        "native_result_claimed": False,
    }


def tamper_case(directory, fixture, valid_case, profile):
    """Preserve a new corrupted copy and require rejection without modifying originals."""
    base = valid_case / "bundle"
    raw = (valid_case / "synthetic-source.Last.txt").read_bytes()
    reference = (valid_case / "reference-native.json").read_bytes()
    files = {str(p.relative_to(base)): p.read_bytes() for p in base.rglob("*") if p.is_file()}
    manifest = parse_canonical([files["bundle-manifest.json"]])
    expected_manifest = sha(files["bundle-manifest.json"])
    bindings = copy.deepcopy(manifest["bindings"])
    first = manifest["streams"][0]["chunks"][0]
    old_path = first["object_identity"]
    direct_audit = False
    if fixture == "MISSING_SHARD":
        del files[old_path]
    elif fixture == "REORDERED_SHARDS":
        manifest["streams"].reverse()
    elif fixture == "DUPLICATE_ORDINAL":
        first["ordinal"] = 1
    elif fixture == "OVERLAPPING_OFFSET":
        first["uncompressed_offset"] = 1
    elif fixture == "TRUNCATED_COMPRESSED_OBJECT":
        files[old_path] = files[old_path][:-1]
    elif fixture == "WRONG_STORED_HASH":
        files[old_path] = bytes([files[old_path][0] ^ 1]) + files[old_path][1:]
    elif fixture == "WRONG_DECODED_HASH":
        first["uncompressed_sha256"] = "0" * 64
    elif fixture == "WRONG_DECODED_SIZE":
        first["uncompressed_size_bytes"] += 1
    elif fixture == "WRONG_CODEC_VERSION":
        manifest["codec_profile"]["zlib_runtime_version"] = "0.0.invalid"
    elif fixture in ("DECOMPRESSION_OVER_LIMIT", "TRAILING_COMPRESSED_BYTES"):
        if fixture == "DECOMPRESSION_OVER_LIMIT":
            c = zlib.compressobj(9, zlib.DEFLATED, -15, 8, zlib.Z_DEFAULT_STRATEGY)
            changed = c.compress(b"z" * (first["uncompressed_size_bytes"] + 1)) + c.flush()
        else:
            changed = files[old_path] + b"trailing"
        digest = sha(changed)
        path = f"objects/{digest[:2]}/{digest}.blob"
        del files[old_path]
        files[path] = changed
        first.update(stored_sha256=digest, stored_size_bytes=len(changed), object_identity=path)
    elif fixture in ("SUMMARY_METRIC_MISMATCH", "SUMMARY_VERDICT_MISMATCH"):
        summary = parse_canonical([files["decision-summary.json"]])
        if fixture == "SUMMARY_METRIC_MISMATCH":
            summary["metrics"]["entry_fills"] += 1
        else:
            summary["verdict"] = "NO_GO_BASELINE"
        files["decision-summary.json"] = canonical(summary)
    elif fixture == "WRONG_RUN_IDENTITY":
        manifest["bindings"]["run_identity"]["dataset_raw_sha256"] = "0" * 64
    elif fixture == "WRONG_SOURCE_CLOSURE":
        manifest["bindings"]["complete_source_closure_sha256"] = "0" * 64
    elif fixture == "MISSING_COMPLETION_SEAL":
        del files["completion-seal.json"]
    elif fixture == "PARTIAL_JOURNAL_LABELED_COMPLETE":
        journal = parse_canonical([files["production-receipt.json"]])
        journal["status"] = "COMPLETE"
        files["production-receipt.json"] = canonical(journal)
    else:
        direct_audit = True
    # Commit the corrupted manifest externally too, so deeper descriptor checks run.
    # For native mutations below, the separately rehashed audit bypasses transport.
    files["bundle-manifest.json"] = canonical(manifest)
    expected_manifest = sha(files["bundle-manifest.json"])
    corrupt = directory / "corrupt-bundle"
    for name, value in files.items():
        immutable_write(corrupt / name, value)
    document = parse_canonical([reference])
    witness_raw = b"".join(
        decode_stream(
            parse_canonical([(base / "bundle-manifest.json").read_bytes()])["streams"][1],
            base,
            profile,
        )
    )
    witnesses = [parse_canonical([row]) for row in witness_raw.splitlines(keepends=True)]
    if direct_audit:
        changed = reference
        if fixture == "TRUNCATED_FINAL_RECORD":
            changed = reference[:-3]
        elif fixture == "DUPLICATE_JSON_KEYS":
            changed = b'{"a":1,"a":2}\n'
        elif fixture == "NONCANONICAL_JSON":
            changed = b" " + reference
        elif fixture == "MISSING_FINAL_LF":
            changed = reference[:-1]
        elif fixture == "OMITTED_LIFECYCLE_RECORD":
            document["immutable_lifecycle_records"]["entries"].pop()
        elif fixture == "CHANGED_RATIONAL_DIGIT":
            document["closed_trade_records"][0]["net_realized_pnl_usd"]["numerator"] += 1
        elif fixture == "SWAPPED_TRADE_PROVENANCE":
            # Two distinct closed trades are required; fixture choice is predeclared.
            require(len(document["closed_trade_records"]) >= 2, "two-trade tamper fixture required")
            a, b = document["closed_trade_records"][:2]
            a["immutable_provenance"], b["immutable_provenance"] = (
                b["immutable_provenance"],
                a["immutable_provenance"],
            )
        elif fixture == "SOURCE_CLOSE_WITNESS_MISMATCH":
            witnesses[0]["raw_close_text"] = "1"
        else:
            raise AssertionError("undeclared tamper test")
        if changed is reference:
            document["output_sha256"] = sha(
                canonical({k: v for k, v in document.items() if k != "output_sha256"})
            )
            changed = canonical(document)
        immutable_write(directory / "corrupt-native.json", changed)
        immutable_write(
            directory / "corrupt-witnesses.jsonl", b"".join(canonical(w) for w in witnesses)
        )
    try:
        if direct_audit:
            audit_native(parse_canonical([changed]), witnesses, raw)
        else:
            verify_synthetic_bundle(
                corrupt,
                expected_manifest_sha=expected_manifest,
                expected_bindings=bindings,
                expected_profile=profile,
                expected_native_sha=sha(reference),
                synthetic_raw=raw,
            )
    except StorageProofError as exc:
        return {
            "case_id": fixture,
            "kind": "TAMPER",
            "status": "PASS",
            "outcome": "REJECT",
            "rejection": str(exc),
            "native_hash_recomputed_for_invariant_test": direct_audit,
            "corruption_preserved": True,
        }
    raise AssertionError("corrupted evidence was accepted")


def statistics_cases():
    """Compare independent statistics with the frozen pure screening authority."""
    from dataclasses import fields
    from datetime import timedelta

    from tools import ema_pullback_v2_development_protocol as frozen

    origin = datetime(2099, 1, 1, tzinfo=UTC)
    for values in STATISTICS_CASES:
        pnls = tuple(Fraction(v) for v in values)
        records = tuple(
            frozen.ClosedTrade(i + 1, origin, origin + timedelta(minutes=i + 1), v)
            for i, v in enumerate(pnls)
        )
        expected = frozen._trade_metrics(records)
        actual = trade_statistics(pnls)
        require(
            actual == {field.name: getattr(expected, field.name) for field in fields(expected)},
            "independent statistics equality",
        )
    _, protocol = contracts()
    template = {
        "closed_trades": 100,
        "net_realized_pnl_usd": Fraction(200),
        "profit_factor": Fraction(115, 100),
        "maximum_marked_equity_drawdown_usd": Fraction(750),
        "maximum_consecutive_losses": 8,
    }
    segments = [
        {
            "label": f"DEVELOPMENT_S{i}",
            "closed_trades": 15,
            "net_realized_pnl_usd": Fraction(1 if i < 3 else -200),
            "profit_factor": Fraction(80, 100),
        }
        for i in (1, 2, 3)
    ]
    rows = []
    names = parse_canonical([FIXTURE_REGISTRATION.read_bytes()])["screening_cases"]
    for name in names:
        m, s = copy.deepcopy(template), copy.deepcopy(segments)
        expected = "NO_GO_BASELINE"
        if name == "EXACT_GO_THRESHOLDS":
            expected = "GO_TO_INDEPENDENT_VALIDATION"
        elif name == "INSUFFICIENT_TOTAL":
            m["closed_trades"] = 99
            expected = "INSUFFICIENT_SAMPLE"
        elif name == "INSUFFICIENT_SEGMENT":
            s[1]["closed_trades"] = 14
            expected = "INSUFFICIENT_SAMPLE"
        elif name == "NET_BELOW":
            m["net_realized_pnl_usd"] -= Fraction(1, 100)
        elif name == "PF_BELOW":
            m["profit_factor"] -= Fraction(1, 1000000)
        elif name == "DD_ABOVE":
            m["maximum_marked_equity_drawdown_usd"] += Fraction(1, 100)
        elif name == "LOSS_STREAK_ABOVE":
            m["maximum_consecutive_losses"] += 1
        elif name == "ONE_PROFITABLE_SEGMENT":
            s[1]["net_realized_pnl_usd"] = Fraction()
        elif name == "PF_POSITIVE_INFINITY":
            m["profit_factor"] = "POSITIVE_INFINITY"
            expected = "GO_TO_INDEPENDENT_VALIDATION"
        else:
            raise AssertionError("unknown screening precommit")
        verdict, failures, _ = screening_verdict(m, s, protocol)
        require(verdict == expected, "synthetic screening edge")
        rows.append({"id": name, "status": "PASS", "failed_criteria": failures})
    return {
        "kind": "STATISTICS_AND_SCREENING",
        "status": "PASS",
        "statistics_case_count": len(STATISTICS_CASES),
        "screening_cases": rows,
    }


def _worker(args):
    registration, fixtures = verify_registration(args.registration, formal=args.formal)
    limits = fixtures["limits"]
    resource.setrlimit(resource.RLIMIT_AS, (limits["synthetic_process_address_space_bytes"],) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (limits["synthetic_case_output_bytes"],) * 2)
    args.destination.mkdir(parents=True, exist_ok=False)
    start, cpu = time.perf_counter_ns(), time.process_time_ns()
    immutable_write(
        args.destination / "START.json",
        canonical(
            {
                "utc": utc(),
                "pid": os.getpid(),
                "kind": args.worker,
                "fixture": args.fixture,
                "source_registration_sha256": sha(args.registration.read_bytes()),
            }
        ),
    )
    status = "FAIL"
    try:
        if args.worker == "native":
            result = native_case(args.destination, args.fixture, registration, codec_profile())
        elif args.worker == "bytes":
            result = byte_case(args.destination, args.fixture, codec_profile())
        elif args.worker == "tamper":
            result = tamper_case(args.destination, args.fixture, args.valid_case, codec_profile())
        else:
            result = statistics_cases()
        status = "PASS"
    except Exception:
        immutable_write(args.destination / "failure-traceback.txt", traceback.format_exc().encode())
        result = {"status": "FAIL", "case_id": args.fixture, "kind": args.worker}
        raise
    finally:
        result.update(
            utc=utc(),
            wall_ns=time.perf_counter_ns() - start,
            cpu_ns=time.process_time_ns() - cpu,
            peak_worker_memory_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            memory_method="getrusage(RUSAGE_SELF).ru_maxrss_linux_KiB",
            physical_bytes_before_END=footprint(args.destination),
            completion=status,
        )
        immutable_write(args.destination / "END.json", canonical(result))
    return result


def supervise_one(command, destination, timeout, limit):
    """One identified process group, durable logs, explicit timeout, no retry."""
    log = destination.parent / (destination.name + ".log")
    progress = destination.parent / (destination.name + ".supervision.jsonl")
    start = time.perf_counter_ns()
    peak = 0
    failure = None
    with log.open("xb") as output, progress.open("xb") as samples:
        child = subprocess.Popen(
            command, stdout=output, stderr=subprocess.STDOUT, start_new_session=True
        )
        while child.poll() is None:
            try:
                status = Path(f"/proc/{child.pid}/status").read_text()
                rss = next(
                    int(line.split()[1]) * 1024
                    for line in status.splitlines()
                    if line.startswith("VmRSS:")
                )
            except (OSError, StopIteration):
                rss = 0
            parent_peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
            peak = max(peak, rss + parent_peak)
            elapsed = time.perf_counter_ns() - start
            physical = footprint(destination) if destination.exists() else 0
            samples.write(
                canonical(
                    {
                        "utc": utc(),
                        "pid": child.pid,
                        "elapsed_ns": elapsed,
                        "sampled_process_tree_rss_bytes": rss + parent_peak,
                        "physical_bytes": physical,
                    }
                )
            )
            samples.flush()
            if elapsed > timeout * 1_000_000_000 or physical > limit or peak > 4_294_967_296:
                failure = "TIMEOUT_OR_RESOURCE_LIMIT"
                os.killpg(child.pid, signal.SIGKILL)
                break
            time.sleep(1)
        return_code = child.wait()
    result = (
        parse_canonical([(destination / "END.json").read_bytes()])
        if (destination / "END.json").exists()
        else {}
    )
    peak = max(
        peak,
        result.get("peak_worker_memory_bytes", 0)
        + resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
    )
    receipt = {
        "command": command,
        "exit_code": return_code,
        "failure": failure,
        "peak_process_tree_memory_bytes": peak,
        "memory_method": "conservative_sum_of_worker_peak_and_supervisor_peak",
        "physical_bytes": footprint(destination)
        + max(log.stat().st_size, log.stat().st_blocks * 512)
        + max(progress.stat().st_size, progress.stat().st_blocks * 512),
        "result": result,
    }
    immutable_write(destination.parent / (destination.name + ".receipt.json"), canonical(receipt))
    require(
        return_code == 0 and result.get("completion") == "PASS" and failure is None,
        "mandatory bounded proof failed; no retry",
    )
    return receipt


def main():
    """Run only named invented proof cases; there is no arbitrary RAW argument."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--formal", action="store_true")
    parser.add_argument("--worker", choices=("native", "bytes", "tamper", "statistics"))
    parser.add_argument("--fixture")
    parser.add_argument("--valid-case", type=Path)
    args = parser.parse_args()
    if args.worker:
        _worker(args)
        return
    registration, fixtures = verify_registration(args.registration, formal=args.formal)
    args.destination.mkdir(parents=True, exist_ok=False)
    immutable_write(args.destination / "source-registration.json", canonical(registration))
    immutable_write(
        args.destination / "START.json",
        canonical({"utc": utc(), "status": "INCOMPLETE", "pid": os.getpid()}),
    )
    receipts = []
    inventory = [
        (kind, fixture, repeat)
        for kind, ids in (("native", NATIVE_IDS), ("bytes", BYTE_IDS))
        for fixture in ids
        for repeat in (1, 2)
    ]
    inventory += [("tamper", fixture, 1) for fixture in TAMPER_IDS]
    inventory += [("statistics", "precommitted", 1)]
    for kind, fixture, repeat in inventory:
        name = f"{kind}-{fixture}-{repeat}"
        destination = args.destination / name
        command = [
            sys.executable,
            "-B",
            "-m",
            "tools.ema_pullback_v2_storage_synthetic_proof",
            "--registration",
            str(args.registration),
            "--destination",
            str(destination),
            "--worker",
            kind,
            "--fixture",
            fixture,
        ]
        if args.formal:
            command.append("--formal")
        if kind == "tamper":
            source = (
                "dense_gapped_LONG"
                if fixture == "SWAPPED_TRADE_PROVENANCE"
                else "impulse_profit_LONG"
            )
            command += ["--valid-case", str(args.destination / f"native-{source}-1")]
        try:
            receipt = supervise_one(
                command,
                destination,
                60 if kind == "native" else 30,
                fixtures["limits"]["synthetic_case_output_bytes"],
            )
            receipts.append({"case": name, "receipt_sha256": sha(canonical(receipt))})
            print(name, "PASS", flush=True)
        except Exception:
            immutable_write(
                args.destination / "FAILED.json",
                canonical(
                    {
                        "utc": utc(),
                        "failed_case": name,
                        "completed": receipts,
                        "not_run": len(inventory) - len(receipts) - 1,
                        "status": "BLOCKED_STORAGE_CONTRACT_EQUIVALENCE",
                    }
                ),
            )
            raise
    immutable_write(
        args.destination / "END.json",
        canonical(
            {
                "utc": utc(),
                "status": "PASS",
                "cases": receipts,
                "physical_bytes_before_END": footprint(args.destination),
                "real_data_accessed": False,
            }
        ),
    )


if __name__ == "__main__":
    main()
