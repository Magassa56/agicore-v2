"""V3 exact serialization, small supervised comparisons and provenance tests."""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace
import pytest

from agicore.trading import ema_pullback_v2_development_replay as reference
from agicore.trading import ema_pullback_v2_g2c_scaling as scaling
from agicore.trading.ema_pullback_v2_storage_format import StorageProofError, canonical, sha
from tests.integration import test_ema_pullback_v2_g2c_parity_v2 as v2_tests
from tests.unit.trading.v2_recovery_synthetic_fixtures import lifecycle_fixture
from tools import ema_pullback_v2_g2c_parity_v2 as v2
from tools import ema_pullback_v2_g2c_parity_v3 as v3
from tools import ema_pullback_v2_g2c_supervised_v51 as v51
from tools import ema_pullback_v2_g2c_supervisor as supervisor

REGISTRATION = "cff5ae162ec68b03904b0f8fb18e8fb68c456ecc97214da500d41206fd195424"
miniature = v2_tests.miniature

# The subprocess substitutes only a small test fixture at the contract boundary.
# The production command has no fixture override or synthetic input path argument.
_BOOT = r"""
import copy, os, sys
for dependency in reversed(os.environ.get('G2C_TEST_DEPS', '').split(os.pathsep)):
    if dependency:
        sys.path.insert(0, dependency)
from tools import ema_pullback_v2_g2c_parity_v3 as p
from agicore.trading.ema_pullback_v2_storage_format import require, sha
count, registration, expected = sys.argv[1:4]
count = int(count)
name = 'test-dense-' + str(count)
contract = copy.deepcopy(p.load_registration(registration))
contract['fixtures'][name] = {'observations': count, 'input_sha256': expected}
contract['tiers'][str(count)] = contract['tiers']['5000']
def load(producer):
    require(producer == p.v2.V4, 'test producer identity')
    return contract
def fixture(received, selected):
    require(received is contract and selected == name, 'test fixture identity')
    from tests.unit.trading.v2_recovery_synthetic_fixtures import dense_lifecycle_resource_bars_v2
    raw = b''.join(p.scaling._bar_row(bar) for bar in dense_lifecycle_resource_bars_v2(count))
    require(len(raw.splitlines()) == count and sha(raw) == expected, 'test fixture bytes')
    return raw
p.scaling.load_contract = load
p.scaling.invented_fixture = fixture
sys.argv = [p.ENTRY, 'worker', '--fixture', name, '--registration-sha256', registration]
raise SystemExit(p.main())
"""

_MINI_BOOT = r"""
import json, sys
from pathlib import Path
from agicore.trading.ema_pullback_v2_storage_format import require, sha
from tools import ema_pullback_v2_g2c_parity_v3 as p
spec_path, registration, predecessor = sys.argv[1:4]
spec = json.loads(Path(spec_path).read_bytes())
contract, raw = spec['contract'], bytes.fromhex(spec['raw_hex'])
name = 'mini-invented-only'
p.v2.V4, p.V2_SHA = spec['producer'], predecessor
def registered(supplied):
    require(supplied == registration, 'test parity V3 registration')
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


def _command(count):
    return [sys.executable, "-B", "-c", _BOOT, str(count), REGISTRATION,
            v2_tests.FIXTURES[count][0]]


@pytest.fixture(scope="module")
def contract():
    return v3.load_registration(REGISTRATION)


def test_registration_and_plan_preserve_predecessor_and_limits(contract, monkeypatch):
    assert sha(v3.REGISTRATION.read_bytes()) == REGISTRATION
    monkeypatch.setattr(supervisor, "run_worker", lambda *a, **k: pytest.fail("plan executed"))
    selected = v3.plan(REGISTRATION, 5000)
    previous = selected["v2_plan"]
    assert selected["v2_plan_sha256"] == sha(canonical(previous))
    assert previous["parity_registration_sha256"] == v3.V2_SHA
    assert previous["v51_plan"]["limits"] == contract["tiers"]["5000"]
    assert (previous["v51_plan"]["limits"]["cpu_seconds"],
            previous["v51_plan"]["limits"]["wall_seconds"]) == (150, 240)
    assert contract["tiers"]["5000"]["address_space_bytes"] == 2 << 30


def test_registration_source_and_predecessor_tampering_fails(contract, tmp_path, monkeypatch):
    with pytest.raises(StorageProofError, match="external parity V3 registration"):
        v3.load_registration("0" * 64)
    doc = json.loads(v3.REGISTRATION.read_bytes())
    doc["integer_encoder"]["sha256"] = "0" * 64
    forged = tmp_path / "registration.json"
    forged.write_bytes(canonical(doc))
    with monkeypatch.context() as patch:
        patch.setattr(v3, "REGISTRATION", forged)
        with pytest.raises(StorageProofError, match="V3 registration or source mismatch"):
            v3.load_registration(sha(forged.read_bytes()))
    source_read = v3.regular_read

    def changed_worker(path, **kwargs):
        raw = source_read(path, **kwargs)
        return raw + b" " if path == v3.ROOT / v3.ENTRY else raw

    with monkeypatch.context() as patch:
        patch.setattr(v3, "regular_read", changed_worker)
        with pytest.raises(StorageProofError, match="V3 registration or source mismatch"):
            v3.load_registration(REGISTRATION)
    forged.write_bytes(v2.REGISTRATION.read_bytes() + b" ")
    monkeypatch.setattr(v2, "REGISTRATION", forged)
    with pytest.raises(StorageProofError, match="external parity registration"):
        v3.load_registration(REGISTRATION)


def test_exact_integer_boundaries_cache_eviction_and_private_globals(monkeypatch):
    original_digits_limit = sys.get_int_max_str_digits()
    original_function = reference._integer_text
    encoders = []
    actual_encoder = v3.CanonicalEncoderV1

    def small_encoder(*, cache_cap_bytes):
        encoder = actual_encoder(cache_cap_bytes=cache_cap_bytes)
        encoders.append(encoder)
        return encoder

    monkeypatch.setattr(v3, "CACHE_CAP_BYTES", 1024)
    monkeypatch.setattr(v3, "CanonicalEncoderV1", small_encoder)
    first = v3._cached_reference()
    second = v3._cached_reference()
    convert = first.__globals__["_integer_text"]
    assert first.__globals__ is not second.__globals__
    values = [0, 1, -1, 10**9 - 1, 10**9, -(10**9), 10**307, -(10**308),
              10**4500 + 123, -(10**4500 + 456)]
    values.extend(10**420 + index for index in range(5))
    for value in values:
        assert convert(value) == reference._integer_text(value)
        assert encoders[0].cache_bytes <= 1024
    assert len(encoders[0].cache) < 5
    assert reference._integer_text is original_function
    assert sys.get_int_max_str_digits() == original_digits_limit
    serialize = first.__globals__["canonical_replay_bytes_v2"]
    for invalid in (float("nan"), 1.5, {"x": float("inf")}):
        with pytest.raises(reference.DevelopmentReplayV2Error):
            serialize(invalid)


@pytest.mark.parametrize("count", [201, 401, 601])
def test_reference_bytes_causality_financial_and_end_of_data(count):
    raw = v2_tests._raw(count)
    assert sha(raw) == v2_tests.FIXTURES[count][0]
    bindings = reference.read_frozen_replay_bindings_v2()
    before = v2._cached_reference()(raw, bindings=bindings)
    after = v3._cached_reference()(raw, bindings=bindings)
    assert before.canonical_utf8 == after.canonical_utf8
    assert sha(after.canonical_utf8) == v2_tests.FIXTURES[count][1]
    document = after.document
    trades = document["closed_trade_records"]
    assert len(trades) == v2_tests.FIXTURES[count][2]
    assert {trade["direction"] for trade in trades} == {"LONG", "SHORT"}
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
    assert document["marked_equity_samples"][-1]["bar_index"] == count - 1
    assert document["dataset_last_timestamp_utc"] == (
        reference.parse_ninjatrader_last_rows_v2(raw)[-1].timestamp_utc.isoformat().replace("+00:00", "Z")
    )


@pytest.mark.parametrize("count", [201, 401, 601])
def test_future_bar_mutation_keeps_earlier_state_and_views(count):
    raw = v2_tests._raw(count)
    rows = raw.splitlines(keepends=True)
    changed_index, observed_index = count - 21, count - 61
    fields = rows[changed_index].decode("ascii").strip().split(";")
    fields[4] = fields[2] if fields[4] != fields[2] else fields[3]
    rows[changed_index] = (";".join(fields) + "\n").encode("ascii")
    changed = b"".join(rows)
    assert changed != raw
    bindings = reference.read_frozen_replay_bindings_v2()
    states, prefix_counts = [], []
    for source in (raw, changed):
        evaluator = v3._cached_reference()
        assembly = evaluator.__globals__["assembly"]
        close, views = assembly.process_baseline_close_v2, assembly._price_views

        def checked_views(raw_bars):
            result = views(raw_bars)
            assert set(result) == set(raw_bars) == set(range(len(raw_bars)))
            prefix_counts.append(len(result))
            return result

        def checked_close(**kwargs):
            book = close(**kwargs)
            if book.closed_bars[-1].bar_index == observed_index:
                states.append(repr(book).replace(f"synthetic-{sha(source)[:16]}-v1", "synthetic-test-v1"))
            return book

        assembly._price_views = checked_views
        assembly.process_baseline_close_v2 = checked_close
        evaluator(source, bindings=bindings)
    assert len(states) == 2 and states[0] == states[1]
    assert prefix_counts.count(observed_index + 1) == 2 and max(prefix_counts) == count


@pytest.mark.parametrize("scenario", ["context_eof", "confirmation_eof", "entry_eof",
                                     "open_eof", "ema_eof", "rejection_eof"])
@pytest.mark.parametrize("direction", list(reference.assembly.context.RegimeDirection))
def test_end_of_data_scenarios_match_exactly(scenario, direction):
    raw = lifecycle_fixture(scenario, direction)
    bindings = reference.read_frozen_replay_bindings_v2()
    previous = v2._cached_reference()(raw, bindings=bindings)
    current = v3._cached_reference()(raw, bindings=bindings)
    assert current.canonical_utf8 == previous.canonical_utf8
    assert current.document["marked_equity_samples"][-1]["bar_index"] == len(raw.splitlines()) - 1


@pytest.mark.parametrize("count", [201, 401, 601])
def test_alternating_complete_workers(count, contract, tmp_path):
    caps = contract["tiers"]["5000"]
    samples = []
    orders = (("v2", "v3"), ("v3", "v2")) * 2
    for repeat, order in enumerate(orders, 1):
        receipts = {}
        for mode in order:
            command = v2_tests._command(count) if mode == "v2" else _command(count)
            folder = tmp_path / f"{count}-{repeat}-{mode}"
            metrics, receipt = supervisor.run_worker(command, folder, caps, root=v3.ROOT)
            assert metrics["status"] == "PASS", (metrics, (folder / "stderr.log").read_text())
            assert receipt["status"] == "PASS" and receipt["fixture"] == f"test-dense-{count}"
            assert (folder / "stdout.log").read_bytes() == canonical(receipt)
            samples.append({"repeat": repeat, "mode": mode, "receipt_sha256": sha(canonical(receipt)),
                            **metrics})
            receipts[mode] = receipt
        assert receipts["v2"]["schema"] == "agicore:g2c-parity:v2"
        assert receipts["v3"]["schema"] == "agicore:g2c-parity:v3"
        assert receipts["v3"]["parity_registration_sha256"] == REGISTRATION
        assert receipts["v3"]["predecessor_parity_registration_sha256"] == v3.V2_SHA
        for key in ("input_sha256", "reference_native_sha256", "optimized_native_sha256"):
            assert receipts["v2"][key] == receipts["v3"][key]
        assert receipts["v3"]["input_sha256"] == v2_tests.FIXTURES[count][0]
        assert receipts["v3"]["reference_native_sha256"] == v2_tests.FIXTURES[count][1]
    for mode in ("v2", "v3"):
        assert len({sample["receipt_sha256"] for sample in samples if sample["mode"] == mode}) == 1
    print("G2C_PARITY_V3_WORKERS=" + json.dumps(
        {"observations": count, "input_sha256": receipts["v3"]["input_sha256"],
         "reference_native_sha256": receipts["v3"]["reference_native_sha256"],
         "optimized_native_sha256": receipts["v3"]["optimized_native_sha256"],
         "samples": samples}, sort_keys=True
    ))


@pytest.mark.parametrize("field", ["schema", "fixture", "contract_sha256", "input_sha256",
                                   "parity_registration_sha256", "predecessor_parity_registration_sha256",
                                   "reference_native_sha256"])
def test_parent_rejects_canonical_forged_receipt(field, contract, tmp_path):
    fixture = "constant-5000"
    receipt = {"schema": "agicore:g2c-parity:v3", "status": "PASS", "fixture": fixture,
               "contract_sha256": v2.V4, "parity_registration_sha256": REGISTRATION,
               "predecessor_parity_registration_sha256": v3.V2_SHA,
               "input_sha256": contract["fixtures"][fixture]["input_sha256"],
               "optimized_native_sha256": "1" * 64, "reference_native_sha256": "2" * 64,
               "comparison": "EXACT_AFTER_TEMPORARY_IDENTITY_PROJECTION",
               "projected_output_persisted": False}
    (tmp_path / "stdout.log").write_bytes(canonical(receipt))
    v3._check_receipt(receipt, tmp_path, fixture, contract, REGISTRATION)
    receipt[field] = "forged"
    (tmp_path / "stdout.log").write_bytes(canonical(receipt))
    with pytest.raises(StorageProofError, match="unbound or noncanonical"):
        v3._check_receipt(receipt, tmp_path, fixture, contract, REGISTRATION)


def test_rehashed_accounting_forgery_fails_exact_comparison(contract, monkeypatch):
    raw = v2_tests._raw(201)
    real = v2.optimized.run_synthetic_native_v1

    def forged(*args, **kwargs):
        document, identity = real(*args, **kwargs)
        document["metrics"]["total_fees_usd"]["numerator"] += 1
        return document, identity

    monkeypatch.setattr(v3, "load_registration", lambda _: contract)
    monkeypatch.setattr(scaling, "invented_fixture", lambda *_: raw)
    monkeypatch.setattr(v2.optimized, "run_synthetic_native_v1", forged)
    with pytest.raises(StorageProofError, match="G2C reference parity"):
        v3.compare_reference("test-dense-201", registration_sha256=REGISTRATION)


def test_unknown_fixture_fails_before_receipt(contract, tmp_path):
    caps = contract["tiers"]["5000"]
    command = [sys.executable, "-B", str(v3.ROOT / v3.ENTRY), "worker",
               "--fixture", "test-dense-201", "--registration-sha256", REGISTRATION]
    metrics, receipt = supervisor.run_worker(command, tmp_path / "foreign", caps, root=v3.ROOT)
    assert metrics["status"] == "FAIL" and receipt == {}
    assert (tmp_path / "foreign/stdout.log").read_bytes() == b""
    assert "unregistered parity fixture" in (tmp_path / "foreign/stderr.log").read_text()


def test_parent_routes_v3_worker_to_existing_miniature_producer(miniature, tmp_path, monkeypatch):
    out, report, contract, _, name, producer, verifier = miniature
    registration, predecessor = sha(b"test-parity-v3"), sha(b"test-parity-v2")
    monkeypatch.setattr(v2, "V4", producer)
    monkeypatch.setattr(v51, "V4", producer)
    monkeypatch.setattr(v51, "V51", verifier)
    monkeypatch.setattr(v3, "V2_SHA", predecessor)
    previous = v51._plan(report["binding_sha256"], 57, contract)
    selected = {"v2_plan": {"v51_plan": previous}}
    instance = v51._private_supervisor()
    destination = tmp_path / "supervised"
    destination.mkdir()
    v3._bind_parent(instance, selected, destination, contract, registration)
    real = supervisor.run_worker

    def transport(command, folder, caps, *, root):
        assert command[2] == str(v3.ROOT / v3.ENTRY)
        return real([sys.executable, "-B", "-c", _MINI_BOOT, str(out.parent / "miniature.json"),
                     registration, predecessor], folder, caps, root=root)

    monkeypatch.setattr(supervisor, "run_worker", transport)
    command = [sys.executable, "-B", str(v3.ROOT / scaling.SUPERVISOR_PATH), "--worker",
               "parity", "--fixture", name, "--contract-sha256", producer]
    folder = destination / f"{name}-parity"
    metrics, receipt = instance.run_worker(command, folder, previous["limits"], root=v3.ROOT)
    assert metrics["status"] == "PASS", (metrics, (folder / "stderr.log").read_text())
    assert receipt["schema"] == "agicore:g2c-parity:v3"
    assert receipt["optimized_native_sha256"] == report["fixtures"][0]["production"]["native_sha256"]


def test_parent_refuses_wrong_parity_dispatch(contract, tmp_path, monkeypatch):
    selected = v3.plan(REGISTRATION, 1000)
    instance = v51._private_supervisor()
    v3._bind_parent(instance, selected, tmp_path, contract, REGISTRATION)
    monkeypatch.setattr(supervisor, "run_worker", lambda *a, **k: pytest.fail("unexpected worker"))
    previous = selected["v2_plan"]["v51_plan"]
    fixture = previous["fixtures"][0]
    command = [sys.executable, "-B", str(v3.ROOT / scaling.SUPERVISOR_PATH), "--worker",
               "parity", "--fixture", fixture, "--contract-sha256", "0" * 64]
    with pytest.raises(StorageProofError, match="unregistered parity V3 dispatch"):
        instance.run_worker(command, tmp_path / f"{fixture}-parity", previous["limits"], root=v3.ROOT)


def test_existing_output_cannot_be_resumed(contract, tmp_path, monkeypatch):
    selected = v3.plan(REGISTRATION, 1000)
    monkeypatch.setattr(supervisor, "run_worker", lambda *a, **k: pytest.fail("unexpected worker"))
    destination = tmp_path / "previous-attempt"
    destination.mkdir()
    with pytest.raises(RuntimeError, match="invalid or existing output path"):
        v3.run_tier(REGISTRATION, 1000, destination, plan_sha256=sha(canonical(selected)))


def test_tier_stops_at_first_parity_resource_failure(contract, tmp_path, monkeypatch):
    # The V5.1 seal is checked in its own regression tests; this isolates V3's stop path.
    selected = v3.plan(REGISTRATION, 1000)
    previous = selected["v2_plan"]["v51_plan"]
    previous.update(tier=201, fixtures=["mini-a", "mini-b"])
    contract = dict(contract)
    contract["tier_fixtures"] = {"201": ["mini-a", "mini-b"]}
    contract["tiers"] = {"201": previous["limits"]}
    instance = v51._private_supervisor()
    instance.load_contract = lambda supplied: contract
    instance.preflight = lambda *a, **k: {}
    instance.supervision_selfcheck = lambda *a, **k: {"worker_and_descendant_stopped": True}
    instance._storage_sizes = lambda *a, **k: {}
    monkeypatch.setattr(v51, "_check_verification", lambda *a, **k: None)
    calls = []

    def transport(command, folder, caps, *, root):
        folder.mkdir(parents=True)
        if command[2] == str(v3.ROOT / scaling.SUPERVISOR_PATH):
            fixture = command[6]
            calls.append("producer-" + fixture)
            bundle = Path(command[command.index("--bundle") + 1])
            bundle.mkdir()
            production = {"schema": "agicore:g2c-production:v1", "status": "PRODUCED_INCOMPLETE",
                          "contract_sha256": v2.V4, "runner_sha256": scaling.RUNNER_SHA256,
                          "fixture": fixture, "manifest_sha256": "1" * 64,
                          "native_sha256": "2" * 64}
            (bundle / "production.json").write_bytes(canonical(production))
            return {"status": "PASS", "reason": None}, production
        if command[2] == str(v3.ROOT / v51.verifier.WORKER):
            calls.append("verifier")
            return {"status": "PASS", "reason": None}, {"status": "PASS"}
        assert command[2] == str(v3.ROOT / v3.ENTRY)
        calls.append("parity")
        return {"status": "FAIL", "reason": "CPU_LIMIT"}, {}

    monkeypatch.setattr(supervisor, "run_worker", transport)
    destination = tmp_path / "tier"
    v3._bind_parent(instance, selected, destination, contract, REGISTRATION)
    args = SimpleNamespace(tier=201, output=destination, contract_sha256=v2.V4,
                           gate_report=None, gate_sha256=None)
    assert instance.run_tier(args) == 1
    report = json.loads((destination / "tier_report.json").read_bytes())
    assert report["schema"] == "agicore:g2c-supervised-tier:parity-v3"
    assert report["parity_v3_registration_sha256"] == REGISTRATION
    assert report["status"] == "BLOCKED" and "CPU_LIMIT" in report["failure"]
    assert calls == ["producer-mini-a", "verifier", "producer-mini-a", "verifier", "parity"]
