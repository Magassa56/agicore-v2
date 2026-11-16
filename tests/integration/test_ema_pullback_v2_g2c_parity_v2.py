"""Small invented parity V2 trials, provenance and fail-closed supervision."""

from __future__ import annotations

import cProfile
import json
import os
import pstats
import signal
import subprocess
import sys
import time
from dataclasses import replace
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace

import pytest

from agicore.trading import ema_pullback_v2_development_replay as reference
from agicore.trading import ema_pullback_v2_g2c_scaling as scaling
from agicore.trading.ema_pullback_v2_storage_format import StorageProofError, canonical, sha
from tests.integration import test_ema_pullback_v2_g2c_supervised_v51 as v51_tests
from tests.unit.trading.v2_recovery_synthetic_fixtures import dense_lifecycle_resource_bars_v2
from tools import ema_pullback_v2_g2c_parity_v2 as parity
from tools import ema_pullback_v2_g2c_supervised_v51 as v51
from tools import ema_pullback_v2_g2c_supervisor as supervisor

miniature = v51_tests.miniature
REGISTRATION = "a7debadeec3b5038699216b3abb6142086617296677dcb37b9fd01f6010c9699"
FIXTURES = {
    201: ("3d7c927e929737bf5fcde6351d41e16ce538be4c988c3e8e89b99df43250e274",
          "0b9f34a0bed7ac6bb663348d888dfd3d8fb52b65f5867e7eeaefa0e097158f26", 3),
    401: ("3ff0172bb1cbfdd73da1253792a98c2724d7adb31a16e01746901b1422c3dff9",
          "027314e29b9ae6d17e7d2c3ea9b68a2b0f3f41369c42390587949064c9c07d04", 7),
    601: ("2a01c33f65dd0ebf3efa42f38302d45daba6f115bf34352cbb371419a1706d88",
          "ba4db224998e792ea64b5c6726b9c2232211847fcd530cdf66b36c441348af9b", 10),
}

# Only the test process substitutes a distinct small fixture registration. The production
# command has no fixture override and accepts only fixtures in the authenticated V4 contract.
_BOOT = r"""
import copy, json, os, sys
from pathlib import Path
for dependency in reversed(os.environ.get('G2C_TEST_DEPS', '').split(os.pathsep)):
    if dependency:
        sys.path.insert(0, dependency)
from tools import ema_pullback_v2_g2c_parity_v2 as p
from agicore.trading.ema_pullback_v2_storage_format import require, sha
count, digest, expected, marker = sys.argv[1:5]
count = int(count)
name = 'test-dense-' + str(count)
contract = copy.deepcopy(p.load_registration(digest))
contract['fixtures'][name] = {'observations': count, 'input_sha256': expected}
contract['tiers'][str(count)] = contract['tiers']['5000']
def load(producer):
    require(producer == p.V4, 'test producer identity')
    return contract
def fixture(received, selected):
    require(received is contract and selected == name, 'test fixture identity')
    from tests.unit.trading.v2_recovery_synthetic_fixtures import dense_lifecycle_resource_bars_v2
    raw = b''.join(p.scaling._bar_row(bar) for bar in dense_lifecycle_resource_bars_v2(count))
    require(len(raw.splitlines()) == count and sha(raw) == expected, 'test fixture bytes')
    return raw
p.scaling.load_contract = load
p.scaling.invented_fixture = fixture
if marker != '-':
    Path(marker).write_text('ready', encoding='ascii')
sys.argv = [p.ENTRY, 'worker', '--fixture', name, '--registration-sha256', digest]
raise SystemExit(p.main())
"""

_LEGACY_BOOT = r"""
import copy, os, sys
for dependency in reversed(os.environ.get('G2C_TEST_DEPS', '').split(os.pathsep)):
    if dependency:
        sys.path.insert(0, dependency)
from agicore.trading import ema_pullback_v2_g2c_scaling as g
from agicore.trading.ema_pullback_v2_storage_format import require, sha
from tools import ema_pullback_v2_g2c_supervisor as supervisor
count, producer, expected = sys.argv[1:4]
count = int(count)
name = 'test-dense-' + str(count)
contract = copy.deepcopy(g.load_contract(producer))
contract['fixtures'][name] = {'observations': count, 'input_sha256': expected}
contract['tiers'][str(count)] = contract['tiers']['5000']
def load(supplied):
    require(supplied == producer, 'test producer identity')
    return contract
def fixture(received, selected):
    require(received is contract and selected == name, 'test fixture identity')
    from tests.unit.trading.v2_recovery_synthetic_fixtures import dense_lifecycle_resource_bars_v2
    raw = b''.join(g._bar_row(bar) for bar in dense_lifecycle_resource_bars_v2(count))
    require(len(raw.splitlines()) == count and sha(raw) == expected, 'test fixture bytes')
    return raw
g.load_contract = load
g.invented_fixture = fixture
supervisor.load_contract = load
sys.argv = [g.SUPERVISOR_PATH, '--worker', 'parity', '--fixture', name,
            '--contract-sha256', producer]
raise SystemExit(supervisor.main())
"""

_MINI_BOOT = r"""
import json, sys
from pathlib import Path
from tools import ema_pullback_v2_g2c_parity_v2 as p
from agicore.trading.ema_pullback_v2_storage_format import require, sha
spec_path, registration = sys.argv[1:3]
spec = json.loads(Path(spec_path).read_bytes())
contract, raw = spec['contract'], bytes.fromhex(spec['raw_hex'])
name = 'mini-invented-only'
p.V4 = spec['producer']
def registered(supplied):
    require(supplied == registration, 'test parity registration')
    return contract
def fixture(received, selected):
    require(received is contract and selected == name and len(raw.splitlines()) == 57
            and sha(raw) == contract['fixtures'][name]['input_sha256'], 'test fixture')
    return raw
p.load_registration = registered
p.scaling.invented_fixture = fixture
sys.argv = [p.ENTRY, 'worker', '--fixture', name, '--registration-sha256', registration]
raise SystemExit(p.main())
"""


def _raw(count):
    return b"".join(scaling._bar_row(bar) for bar in dense_lifecycle_resource_bars_v2(count))


def _command(count, marker="-"):
    return [sys.executable, "-B", "-c", _BOOT, str(count), REGISTRATION, FIXTURES[count][0], marker]


@pytest.fixture(scope="module")
def contract():
    return parity.load_registration(REGISTRATION)


def test_registration_plan_and_frozen_limits(contract, monkeypatch):
    assert sha(parity.REGISTRATION.read_bytes()) == REGISTRATION
    monkeypatch.setattr(supervisor, "run_worker", lambda *a, **k: pytest.fail("no worker in plan"))
    selected = parity.plan(REGISTRATION, 5000)
    assert selected["v51_plan"]["limits"] == contract["tiers"]["5000"]
    assert selected["v51_plan"]["limits"]["cpu_seconds"] == 150
    assert selected["v51_plan"]["limits"]["wall_seconds"] == 240
    assert selected["v51_plan"]["binding_sha256"] == parity.V51_BINDING


def test_tampered_registration_rejected_even_if_rehashed(tmp_path, monkeypatch):
    with pytest.raises(StorageProofError, match="external parity registration"):
        parity.load_registration("0" * 64)
    doc = json.loads(parity.REGISTRATION.read_bytes())
    doc["worker"]["sha256"] = "0" * 64
    path = tmp_path / "forged.json"
    path.write_bytes(canonical(doc))
    monkeypatch.setattr(parity, "REGISTRATION", path)
    with pytest.raises(StorageProofError, match="registration or source mismatch"):
        parity.load_registration(sha(path.read_bytes()))


def test_changed_worker_bytes_rejected(contract, monkeypatch):
    read = parity.regular_read

    def forged(path, **kwargs):
        raw = read(path, **kwargs)
        return raw + b" " if path == parity.ROOT / parity.ENTRY else raw

    monkeypatch.setattr(parity, "regular_read", forged)
    with pytest.raises(StorageProofError, match="registration or source mismatch"):
        parity.load_registration(REGISTRATION)


def test_rehashed_accounting_forgery_fails_exact_comparison(contract, monkeypatch):
    raw = _raw(201)
    real = parity.optimized.run_synthetic_native_v1

    def forged(*args, **kwargs):
        document, identity = real(*args, **kwargs)
        document["metrics"]["total_fees_usd"]["numerator"] += 1
        return document, identity

    monkeypatch.setattr(parity, "load_registration", lambda _: contract)
    monkeypatch.setattr(parity.scaling, "invented_fixture", lambda *_: raw)
    monkeypatch.setattr(parity.optimized, "run_synthetic_native_v1", forged)
    with pytest.raises(StorageProofError, match="G2C reference parity"):
        parity.compare_reference("test-dense-201", registration_sha256=REGISTRATION)


def test_cache_rebuilds_replaced_bars_and_isolates_prefix():
    bars = reference.parse_ninjatrader_last_rows_v2(_raw(201))
    first, second = (bar.closed_view() for bar in bars[:2])
    cache = parity._PriceViews(reference.assembly._price_views)
    earlier = cache({0: first})
    current = cache({0: first, 1: second})
    assert list(earlier) == [0]
    assert current[0] is earlier[0]
    assert current == reference.assembly._price_views({0: first, 1: second})
    changed = replace(first, close=first.high if first.close != first.high else first.low)
    assert cache({0: changed}) == reference.assembly._price_views({0: changed})
    assert cache({0: changed})[0].close != earlier[0].close
    invalid = SimpleNamespace(
        timestamp_utc=first.timestamp_utc.replace(tzinfo=None),
        open=first.open, high=first.high, low=first.low, close=first.close,
        is_closed=first.is_closed,
    )
    with pytest.raises(reference.assembly.pullback.EMA20PullbackV2Error):
        cache({0: invalid})


@pytest.mark.parametrize("count", [201, 401, 601])
def test_future_mutation_preserves_previous_close_and_cache(count, monkeypatch):
    raw = _raw(count)
    rows = raw.splitlines(keepends=True)
    changed_index = count - 21
    observed_index = count - 61
    fields = rows[changed_index].decode("ascii").strip().split(";")
    fields[4] = fields[2] if fields[4] != fields[2] else fields[3]
    rows[changed_index] = (";".join(fields) + "\n").encode("ascii")
    changed = b"".join(rows)
    assert changed != raw
    snapshots, seen = [], []
    original_rebind = parity._rebind
    original_cache = parity._PriceViews

    class AuditedViews(original_cache):
        def __call__(self, raw_bars):
            result = super().__call__(raw_bars)
            assert set(result) == set(raw_bars) == set(range(len(raw_bars)))
            seen.append(len(result))
            return result

    def rebind(function, namespace):
        bound = original_rebind(function, namespace)
        if function is reference.assembly.process_baseline_close_v2:
            def close(**kwargs):
                book = bound(**kwargs)
                if book.closed_bars[-1].bar_index == observed_index:
                    snapshots.append(book)
                return book
            return close
        return bound

    monkeypatch.setattr(parity, "_PriceViews", AuditedViews)
    monkeypatch.setattr(parity, "_rebind", rebind)
    bindings = reference.read_frozen_replay_bindings_v2()
    for source in (raw, changed):
        parity._cached_reference()(source, bindings=bindings)
    # The dataset identifier binds the entire input, including the changed future row.
    # Project that identifier in memory while comparing the earlier strategy state.
    assert len(snapshots) == 2
    states = [repr(book).replace(f"synthetic-{sha(source)[:16]}-v1", "synthetic-test-v1")
              for book, source in zip(snapshots, (raw, changed), strict=True)]
    assert states[0] == states[1]
    assert seen.count(observed_index + 1) == 2 and max(seen) == count


@pytest.mark.parametrize("count", [201, 401, 601])
def test_full_worker_cpu_and_exact_reference_bytes(count, contract, tmp_path):
    raw = _raw(count)
    expected_input, expected_reference, expected_trades = FIXTURES[count]
    assert sha(raw) == expected_input
    bindings = reference.read_frozen_replay_bindings_v2()
    frozen = reference.evaluate_synthetic_development_replay_v2(raw, bindings=bindings)
    cached = parity._cached_reference()(raw, bindings=bindings)
    assert cached.canonical_utf8 == frozen.canonical_utf8
    assert sha(frozen.canonical_utf8) == expected_reference
    document = frozen.document
    trades = document["closed_trade_records"]
    assert len(trades) == expected_trades
    for trade in trades:
        assert Fraction(**trade["gross_price_pnl_usd"]) - Fraction(**trade["total_fees_usd"]) == (
            Fraction(**trade["net_realized_pnl_usd"])
        )
        assert Fraction(**trade["diagnostic_slippage_cost_usd"]) > 0
    for trade_field, metric_field in (
        ("total_fees_usd", "closed_trade_fees_usd"),
        ("net_realized_pnl_usd", "net_realized_pnl_usd"),
    ):
        assert sum((Fraction(**trade[trade_field]) for trade in trades), Fraction()) == (
            Fraction(**document["metrics"][metric_field])
        )
    if count == 601:
        assert {trade["direction"] for trade in trades} == {"LONG", "SHORT"}
    folder = tmp_path / f"worker-{count}"
    metrics, receipt = supervisor.run_worker(
        _command(count), folder, contract["tiers"]["5000"], root=parity.ROOT
    )
    assert metrics["status"] == "PASS", (metrics, (folder / "stderr.log").read_text())
    assert receipt["schema"] == "agicore:g2c-parity:v2"
    assert receipt["parity_registration_sha256"] == REGISTRATION
    assert receipt["reference_native_sha256"] == expected_reference
    assert receipt["input_sha256"] == expected_input
    assert (folder / "stdout.log").read_bytes() == canonical(receipt)
    old_folder = tmp_path / f"legacy-worker-{count}"
    old_command = [sys.executable, "-B", "-c", _LEGACY_BOOT, str(count), parity.V4, expected_input]
    old_metrics, old_receipt = supervisor.run_worker(
        old_command, old_folder, contract["tiers"]["5000"], root=parity.ROOT
    )
    assert old_metrics["status"] == "PASS", (old_metrics, (old_folder / "stderr.log").read_text())
    assert old_receipt["schema"] == "agicore:g2c-parity:v1"
    for key in ("input_sha256", "reference_native_sha256", "optimized_native_sha256"):
        assert old_receipt[key] == receipt[key]
    print("G2C_PARITY_V2_FULL_WORKER=" + json.dumps(
        {"observations": count, "v2": metrics, "v1": old_metrics}, sort_keys=True
    ))


def test_reference_profile_measures_raw_reconstruction():
    raw = _raw(601)
    bindings = reference.read_frozen_replay_bindings_v2()
    profile = cProfile.Profile(timer=time.process_time)
    profile.runcall(parity._cached_reference(), raw, bindings=bindings)
    wanted = {"_raw_regime_decision", "_price_views", "evaluate_ema20_v2", "evaluate_macd_v2",
              "_integer_text", "<dictcomp>"}
    rows = []
    for (filename, line, name), (_, calls, own, cumulative, _) in pstats.Stats(profile).stats.items():
        if name in wanted and "/agicore/trading/" in filename:
            rows.append({"file": Path(filename).name, "line": line, "function": name,
                         "calls": calls, "own_cpu_s": own, "cumulative_cpu_s": cumulative})
    raw_row = next(r for r in rows if r["function"] == "_raw_regime_decision")
    assert raw_row["calls"] == 602
    print("G2C_PARITY_V2_CPROFILE=" + json.dumps(rows, sort_keys=True))


def test_isolated_rejection_view_reconstruction_cost():
    bars = [bar.closed_view() for bar in reference.parse_ninjatrader_last_rows_v2(_raw(601))]
    rejection = reference.assembly.reversal.RejectionBarV2
    elapsed, constructed = 0, 0
    for size in (*range(1, len(bars) + 1), len(bars)):
        raw = {bar.bar_index: bar for bar in bars[:size]}
        started = time.process_time_ns()
        views = {index: rejection(index, bar.timestamp_utc, bar.close, bar.is_closed,
                                  bar.open, bar.high, bar.low) for index, bar in raw.items()}
        elapsed += time.process_time_ns() - started
        constructed += len(views)
        assert len(views) == size
    assert constructed == 181502
    print("G2C_PARITY_V2_REJECTION_REBUILD=" + json.dumps(
        {"observations": len(bars), "constructions": constructed, "isolated_cpu_ns": elapsed}
    ))


@pytest.mark.parametrize("field", ["schema", "fixture", "contract_sha256", "input_sha256",
                                   "parity_registration_sha256", "reference_native_sha256"])
def test_parent_rejects_forged_receipt_even_when_canonical(field, contract, tmp_path):
    fixture = "constant-5000"
    receipt = {"schema": "agicore:g2c-parity:v2", "status": "PASS", "fixture": fixture,
               "contract_sha256": parity.V4, "parity_registration_sha256": REGISTRATION,
               "input_sha256": contract["fixtures"][fixture]["input_sha256"],
               "optimized_native_sha256": "1" * 64, "reference_native_sha256": "2" * 64,
               "comparison": "EXACT_AFTER_TEMPORARY_IDENTITY_PROJECTION",
               "projected_output_persisted": False}
    (tmp_path / "stdout.log").write_bytes(canonical(receipt))
    parity._check_receipt(receipt, tmp_path, fixture, contract, REGISTRATION)
    receipt[field] = "forged"
    (tmp_path / "stdout.log").write_bytes(canonical(receipt))
    with pytest.raises(StorageProofError, match="unbound or noncanonical"):
        parity._check_receipt(receipt, tmp_path, fixture, contract, REGISTRATION)


def test_unknown_fixture_refused_without_a_receipt(contract, tmp_path):
    caps = contract["tiers"]["5000"]
    command = [sys.executable, "-B", str(parity.ROOT / parity.ENTRY), "worker",
               "--fixture", "test-dense-201", "--registration-sha256", REGISTRATION]
    metrics, receipt = supervisor.run_worker(command, tmp_path / "foreign", caps, root=parity.ROOT)
    assert metrics["status"] == "FAIL" and receipt == {}
    assert (tmp_path / "foreign/stdout.log").read_bytes() == b""
    assert "unregistered parity fixture" in (tmp_path / "foreign/stderr.log").read_text()


def test_interruption_and_fresh_retry_cannot_reuse_output(contract, tmp_path):
    caps = contract["tiers"]["5000"]
    marker, partial = tmp_path / "ready", tmp_path / "partial.out"
    command = ["prlimit", f"--as={caps['address_space_bytes']}", f"--cpu={caps['cpu_seconds']}",
               f"--fsize={caps['file_bytes']}", "--", *_command(601, str(marker))]
    with partial.open("wb") as out, (tmp_path / "partial.err").open("wb") as err:
        process = subprocess.Popen(command, cwd=parity.ROOT, stdout=out, stderr=err,
                                   start_new_session=True)
        try:
            deadline = time.monotonic() + 15
            while not marker.exists() and process.poll() is None and time.monotonic() < deadline:
                time.sleep(0.02)
            assert marker.exists()
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=10)
    assert process.returncode == -signal.SIGKILL and partial.read_bytes() == b""
    destination = tmp_path / "fresh"
    metrics, receipt = supervisor.run_worker(_command(601), destination, caps, root=parity.ROOT)
    assert metrics["status"] == "PASS" and receipt["status"] == "PASS"
    with pytest.raises(FileExistsError):
        supervisor.run_worker(_command(601), destination, caps, root=parity.ROOT)


def test_parent_rejects_wrong_parity_dispatch(contract, tmp_path, monkeypatch):
    selected = parity.plan(REGISTRATION, 1000)
    instance = v51._private_supervisor()
    parity._bind_parent(instance, selected, tmp_path, contract, REGISTRATION)
    monkeypatch.setattr(supervisor, "run_worker", lambda *a, **k: pytest.fail("no worker expected"))
    fixture = selected["v51_plan"]["fixtures"][0]
    command = [sys.executable, "-B", str(parity.ROOT / scaling.SUPERVISOR_PATH), "--worker",
               "parity", "--fixture", fixture, "--contract-sha256", "0" * 64]
    with pytest.raises(StorageProofError, match="unregistered parity dispatch"):
        instance.run_worker(command, tmp_path / f"{fixture}-parity",
                            selected["v51_plan"]["limits"], root=parity.ROOT)


def test_parent_routes_v2_and_rejects_a_substituted_receipt(contract, tmp_path, monkeypatch):
    selected = parity.plan(REGISTRATION, 1000)
    instance = v51._private_supervisor()
    parity._bind_parent(instance, selected, tmp_path, contract, REGISTRATION)
    fixture = selected["v51_plan"]["fixtures"][0]
    folder = tmp_path / f"{fixture}-parity"
    folder.mkdir()
    receipt = {"schema": "agicore:g2c-parity:v2", "status": "PASS", "fixture": fixture,
               "contract_sha256": parity.V4, "parity_registration_sha256": REGISTRATION,
               "input_sha256": contract["fixtures"][fixture]["input_sha256"],
               "optimized_native_sha256": "1" * 64, "reference_native_sha256": "2" * 64,
               "comparison": "EXACT_AFTER_TEMPORARY_IDENTITY_PROJECTION",
               "projected_output_persisted": False}
    calls = []

    def transport(command, destination, caps, *, root):
        calls.append(command)
        (destination / "stdout.log").write_bytes(canonical(receipt))
        return {"status": "PASS", "reason": None}, dict(receipt)

    monkeypatch.setattr(supervisor, "run_worker", transport)
    command = [sys.executable, "-B", str(parity.ROOT / scaling.SUPERVISOR_PATH), "--worker",
               "parity", "--fixture", fixture, "--contract-sha256", parity.V4]
    metrics, result = instance.run_worker(command, folder, selected["v51_plan"]["limits"],
                                          root=parity.ROOT)
    assert metrics["status"] == "PASS" and result == receipt
    assert calls[0] == [sys.executable, "-B", str(parity.ROOT / parity.ENTRY), "worker",
                        "--fixture", fixture, "--registration-sha256", REGISTRATION]
    receipt["parity_registration_sha256"] = "0" * 64
    metrics, result = instance.run_worker(command, folder, selected["v51_plan"]["limits"],
                                          root=parity.ROOT)
    assert metrics["status"] == "FAIL" and result == {}
    assert "unbound or noncanonical" in metrics["reason"]


def test_parent_routes_a_real_small_worker_to_existing_producer(miniature, tmp_path, monkeypatch):
    # The existing miniature uses distinct test identities for its actual V4/V5.1 workers.
    out, report, contract, _, name, producer, verifier = miniature
    registration = sha(b"independent-test-parity-registration")
    monkeypatch.setattr(parity, "V4", producer)
    monkeypatch.setattr(v51, "V4", producer)
    monkeypatch.setattr(v51, "V51", verifier)
    previous = v51._plan(report["binding_sha256"], 57, contract)
    selected = {"v51_plan": previous}
    instance = v51._private_supervisor()
    destination = tmp_path / "supervised"
    destination.mkdir()
    parity._bind_parent(instance, selected, destination, contract, registration)
    real = supervisor.run_worker

    def transport(command, folder, caps, *, root):
        assert command[2] == str(parity.ROOT / parity.ENTRY)
        return real([sys.executable, "-B", "-c", _MINI_BOOT, str(out.parent / "miniature.json"),
                     registration], folder, caps, root=root)

    monkeypatch.setattr(supervisor, "run_worker", transport)
    command = [sys.executable, "-B", str(parity.ROOT / scaling.SUPERVISOR_PATH), "--worker",
               "parity", "--fixture", name, "--contract-sha256", producer]
    folder = destination / f"{name}-parity"
    metrics, receipt = instance.run_worker(command, folder, previous["limits"], root=parity.ROOT)
    assert metrics["status"] == "PASS", (metrics, (folder / "stderr.log").read_text())
    assert receipt["schema"] == "agicore:g2c-parity:v2"
    assert receipt["optimized_native_sha256"] == report["fixtures"][0]["production"]["native_sha256"]


def test_original_tier_loop_stops_at_first_parity_failure(contract, tmp_path, monkeypatch):
    # Isolate the parity stop policy. Historical verifier sealing is covered by its own tests.
    selected = parity.plan(REGISTRATION, 1000)
    selected["v51_plan"].update(tier=201, fixtures=["mini-a", "mini-b"])
    contract = dict(contract)
    contract["tier_fixtures"] = {"201": ["mini-a", "mini-b"]}
    contract["tiers"] = {"201": selected["v51_plan"]["limits"]}
    instance = v51._private_supervisor()
    instance.load_contract = lambda supplied: contract
    instance.preflight = lambda *a, **k: {}
    instance.supervision_selfcheck = lambda *a, **k: {"worker_and_descendant_stopped": True}
    instance._storage_sizes = lambda *a, **k: {}
    monkeypatch.setattr(v51, "_check_verification", lambda *a, **k: None)
    calls = []

    def transport(command, folder, caps, *, root):
        folder.mkdir(parents=True)
        if command[2] == str(parity.ROOT / scaling.SUPERVISOR_PATH):
            fixture = command[6]
            calls.append("producer-" + fixture)
            bundle = Path(command[command.index("--bundle") + 1])
            bundle.mkdir()
            production = {"schema": "agicore:g2c-production:v1", "status": "PRODUCED_INCOMPLETE",
                          "contract_sha256": parity.V4, "runner_sha256": scaling.RUNNER_SHA256,
                          "fixture": fixture, "manifest_sha256": "1" * 64,
                          "native_sha256": "2" * 64}
            (bundle / "production.json").write_bytes(canonical(production))
            return {"status": "PASS", "reason": None}, production
        if command[2] == str(parity.ROOT / v51.verifier.WORKER):
            calls.append("verifier")
            return {"status": "PASS", "reason": None}, {"status": "PASS"}
        assert command[2] == str(parity.ROOT / parity.ENTRY)
        calls.append("parity")
        return {"status": "FAIL", "reason": "CPU_LIMIT"}, {}

    monkeypatch.setattr(supervisor, "run_worker", transport)
    destination = tmp_path / "tier"
    parity._bind_parent(instance, selected, destination, contract, REGISTRATION)
    args = SimpleNamespace(tier=201, output=destination, contract_sha256=parity.V4,
                           gate_report=None, gate_sha256=None)
    assert instance.run_tier(args) == 1
    report = json.loads((destination / "tier_report.json").read_bytes())
    assert report["schema"] == "agicore:g2c-supervised-tier:parity-v2"
    assert report["status"] == "BLOCKED" and "CPU_LIMIT" in report["failure"]
    assert calls == ["producer-mini-a", "verifier", "producer-mini-a", "verifier", "parity"]
